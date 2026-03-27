#!/usr/bin/env python3
"""
事件数据库基础层。

WP-1 阶段只提供最小能力：
- 初始化 SQLite/WAL 真源
- 应用 migrations
- 插入任务
- 读取基础统计
"""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import date, timedelta
from pathlib import Path

EVENTS_DIR = Path(__file__).parent
RUNTIME_DIR = EVENTS_DIR / "runtime"
DB_PATH = RUNTIME_DIR / "openclaw.db"
MIGRATIONS_DIR = EVENTS_DIR / "migrations"


def _ensure_runtime_dir() -> None:
    RUNTIME_DIR.mkdir(exist_ok=True)


def _migration_files() -> list[Path]:
    if not MIGRATIONS_DIR.exists():
        return []
    return sorted(MIGRATIONS_DIR.glob("*.sql"))


def get_connection() -> sqlite3.Connection:
    _ensure_runtime_dir()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.execute("PRAGMA busy_timeout=5000;")
    _apply_migrations(conn)
    return conn


def _apply_migrations(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY,
            applied_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
        )
        """
    )
    applied = {
        row["version"]
        for row in conn.execute("SELECT version FROM schema_migrations").fetchall()
    }

    for migration in _migration_files():
        if migration.name in applied:
            continue
        sql = migration.read_text(encoding="utf-8")
        conn.executescript(sql)
        conn.execute(
            "INSERT INTO schema_migrations(version) VALUES (?)",
            (migration.name,),
        )
    conn.commit()


@contextmanager
def transaction():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def insert_task(event: dict) -> None:
    """将当前兼容事件格式写入 tasks 表。"""
    payload = {
        "type": event.get("type"),
        "task": event.get("task"),
        "params": event.get("params", {}),
        "agent": event.get("agent"),
        "legacyCategory": event.get("category"),
    }

    state_map = {
        "pending": "queued",
        "processing": "running",
        "completed": "succeeded",
        "failed": "failed",
    }
    state = state_map.get(event.get("status"), "queued")
    category = event.get("category") or "unknown"

    with transaction() as conn:
        conn.execute(
            """
            INSERT INTO tasks (
                id, workflow_id, parent_task_id, correlation_id, capability, operation,
                requested_by, target_agent, state, priority, payload_json, policy_ref,
                idempotency_key, schedule_at, lease_owner, lease_expires_at,
                attempt_count, max_attempts, timeout_seconds, last_error_code,
                last_error_message, created_at, started_at, completed_at
            ) VALUES (
                :id, NULL, NULL, :correlation_id, :capability, :operation,
                :requested_by, :target_agent, :state, :priority, :payload_json, NULL,
                NULL, NULL, NULL, NULL,
                :attempt_count, :max_attempts, NULL, NULL,
                NULL, :created_at, :started_at, :completed_at
            )
            ON CONFLICT(id) DO NOTHING
            """,
            {
                "id": event["id"],
                "correlation_id": event["id"],
                "capability": category,
                "operation": event.get("task", event.get("type", "unknown")),
                "requested_by": "command",
                "target_agent": event.get("agent"),
                "state": state,
                "priority": 50,
                "payload_json": json.dumps(payload, ensure_ascii=False),
                "attempt_count": event.get("retryCount", 0),
                "max_attempts": event.get("maxRetries", 3),
                "created_at": event.get("createdAt"),
                "started_at": event.get("processedAt"),
                "completed_at": event.get("completedAt"),
            },
        )


def fetch_task_stats() -> dict:
    with get_connection() as conn:
        states = {
            "queued": 0,
            "leased": 0,
            "running": 0,
            "succeeded": 0,
            "failed": 0,
            "retry_wait": 0,
            "dead_letter": 0,
            "canceled": 0,
        }
        rows = conn.execute(
            "SELECT state, COUNT(*) AS count FROM tasks GROUP BY state"
        ).fetchall()
        for row in rows:
            if row["state"] in states:
                states[row["state"]] = row["count"]

        by_capability = {
            row["capability"]: row["count"]
            for row in conn.execute(
                "SELECT capability, COUNT(*) AS count FROM tasks GROUP BY capability"
            ).fetchall()
        }
        latest = conn.execute(
            "SELECT MAX(created_at) AS latest FROM tasks"
        ).fetchone()["latest"]
        total = conn.execute("SELECT COUNT(*) AS count FROM tasks").fetchone()["count"]
        return {
            "total": total,
            "states": states,
            "by_capability": by_capability,
            "latest": latest,
        }


def db_ready() -> bool:
    return DB_PATH.exists()


def _task_files(days_back: int = 7) -> list[Path]:
    files = []
    for i in range(days_back):
        d = date.today() - timedelta(days=i)
        candidate = EVENTS_DIR / f"tasks-{d.isoformat()}.jsonl"
        if candidate.exists():
            files.append(candidate)
    return files


def backfill_tasks_from_jsonl(days_back: int = 7) -> int:
    """将最近几天的 JSONL 任务补录到数据库，重复 ID 自动跳过。"""
    inserted = 0
    for task_file in _task_files(days_back=days_back):
        with task_file.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue

                before = fetch_task_count_by_id(event.get("id"))
                insert_task(event)
                after = fetch_task_count_by_id(event.get("id"))
                if before == 0 and after == 1:
                    inserted += 1
    return inserted


def fetch_task_count_by_id(task_id: str | None) -> int:
    if not task_id:
        return 0
    with get_connection() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS count FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()
        return row["count"]
