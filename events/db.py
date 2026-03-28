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
import os
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

EVENTS_DIR = Path(__file__).parent
DEFAULT_RUNTIME_DIR = EVENTS_DIR / "runtime"
RUNTIME_DIR = Path(os.environ.get("KALICLAW_RUNTIME_DIR", str(DEFAULT_RUNTIME_DIR))).expanduser()
DEFAULT_DB_BASENAME = "kaliclaw.db"
LEGACY_DB_BASENAME = "openclaw.db"


def _default_db_path() -> Path:
    explicit_path = os.environ.get("KALICLAW_DB_PATH")
    if explicit_path:
        return Path(explicit_path).expanduser()

    configured_basename = os.environ.get("KALICLAW_DB_BASENAME")
    if configured_basename:
        return (RUNTIME_DIR / configured_basename).expanduser()

    preferred = RUNTIME_DIR / DEFAULT_DB_BASENAME
    legacy = RUNTIME_DIR / LEGACY_DB_BASENAME
    if preferred.exists() or not legacy.exists():
        return preferred.expanduser()
    return legacy.expanduser()


DB_PATH = _default_db_path()
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


def update_task_state_from_legacy(
    task_id: str,
    legacy_status: str,
    error_message: str | None = None,
) -> None:
    """让旧 JSONL 消费者也能同步数据库状态，降低双轨期重复执行风险。"""
    state_map = {
        "pending": "queued",
        "processing": "running",
        "completed": "succeeded",
        "failed": "failed",
    }
    state = state_map.get(legacy_status, "queued")
    timestamp = now_iso()

    with transaction() as conn:
        if state == "running":
            conn.execute(
                """
                UPDATE tasks
                SET state = 'running',
                    started_at = COALESCE(started_at, ?)
                WHERE id = ?
                """,
                (timestamp, task_id),
            )
        elif state in {"succeeded", "failed"}:
            conn.execute(
                """
                UPDATE tasks
                SET state = ?,
                    completed_at = ?,
                    lease_owner = NULL,
                    lease_expires_at = NULL,
                    last_error_message = ?
                WHERE id = ?
                """,
                (state, timestamp, error_message, task_id),
            )
        else:
            conn.execute(
                "UPDATE tasks SET state = ? WHERE id = ?",
                (state, task_id),
            )


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _json_payload_to_legacy_event(row: sqlite3.Row) -> dict:
    payload = json.loads(row["payload_json"])
    return {
        "id": row["id"],
        "type": payload.get("type"),
        "agent": payload.get("agent"),
        "task": payload.get("task") or row["operation"],
        "params": payload.get("params", {}),
        "category": payload.get("legacyCategory", row["capability"]),
        "createdAt": row["created_at"],
        "processedAt": row["started_at"],
        "completedAt": row["completed_at"],
        "retryCount": row["attempt_count"],
        "maxRetries": row["max_attempts"],
    }


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


def register_worker(worker_id: str, agent_id: str, capabilities: list[str]) -> None:
    with transaction() as conn:
        conn.execute(
            """
            INSERT INTO workers (
                id, agent_id, capabilities_json, hostname, pid, last_heartbeat_at, status
            ) VALUES (?, ?, ?, '', NULL, ?, 'online')
            ON CONFLICT(id) DO UPDATE SET
                agent_id = excluded.agent_id,
                capabilities_json = excluded.capabilities_json,
                last_heartbeat_at = excluded.last_heartbeat_at,
                status = 'online'
            """,
            (worker_id, agent_id, json.dumps(capabilities, ensure_ascii=False), now_iso()),
        )


def heartbeat_worker(worker_id: str) -> None:
    with transaction() as conn:
        conn.execute(
            """
            UPDATE workers
            SET last_heartbeat_at = ?, status = 'online'
            WHERE id = ?
            """,
            (now_iso(), worker_id),
        )


def mark_worker_offline(worker_id: str) -> None:
    with transaction() as conn:
        conn.execute(
            """
            UPDATE workers
            SET last_heartbeat_at = ?, status = 'offline'
            WHERE id = ?
            """,
            (now_iso(), worker_id),
        )


def claim_next_task(capability: str, worker_id: str, lease_seconds: int = 120) -> dict | None:
    lease_expires_at = (
        datetime.now(timezone.utc) + timedelta(seconds=lease_seconds)
    ).isoformat()

    with get_connection() as conn:
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute(
            """
            SELECT *
            FROM tasks
            WHERE capability = ?
              AND (
                state = 'queued'
                OR (
                  state = 'retry_wait'
                  AND (schedule_at IS NULL OR schedule_at <= ?)
                )
              )
            ORDER BY priority DESC, created_at ASC
            LIMIT 1
            """,
            (capability, now_iso()),
        ).fetchone()

        if row is None:
            conn.commit()
            return None

        conn.execute(
            """
            UPDATE tasks
            SET state = 'leased',
                lease_owner = ?,
                lease_expires_at = ?,
                last_error_code = NULL,
                last_error_message = NULL
            WHERE id = ?
            """,
            (worker_id, lease_expires_at, row["id"]),
        )
        conn.commit()
        return dict(row)


def mark_task_running(task_id: str, worker_id: str, executor_type: str = "agent_api", tool_name: str | None = None) -> str:
    attempt_id = str(uuid.uuid4())
    started_at = now_iso()
    with transaction() as conn:
        conn.execute(
            """
            UPDATE tasks
            SET state = 'running',
                started_at = COALESCE(started_at, ?),
                lease_owner = ?
            WHERE id = ?
            """,
            (started_at, worker_id, task_id),
        )
        conn.execute(
            """
            INSERT INTO task_attempts (
                id, task_id, worker_id, executor_type, tool_name,
                started_at, ended_at, outcome, exit_code,
                error_code, error_message, raw_output_ref
            ) VALUES (?, ?, ?, ?, ?, ?, NULL, ?, NULL, NULL, NULL, NULL)
            """,
            (attempt_id, task_id, worker_id, executor_type, tool_name, started_at, "running"),
        )
    return attempt_id


def complete_task(task_id: str, attempt_id: str, status: str, error_message: str | None = None) -> None:
    completed_at = now_iso()
    outcome = "success" if status == "succeeded" else "failed"
    with transaction() as conn:
        conn.execute(
            """
            UPDATE tasks
            SET state = ?,
                completed_at = ?,
                lease_owner = NULL,
                lease_expires_at = NULL,
                last_error_message = ?
            WHERE id = ?
            """,
            (status, completed_at, error_message, task_id),
        )
        conn.execute(
            """
            UPDATE task_attempts
            SET ended_at = ?, outcome = ?, error_message = COALESCE(?, error_message)
            WHERE id = ?
            """,
            (completed_at, outcome, error_message, attempt_id),
        )


def update_attempt_metadata(
    attempt_id: str,
    executor_type: str,
    tool_name: str | None = None,
    exit_code: int | None = None,
    error_code: str | None = None,
    error_message: str | None = None,
) -> None:
    with transaction() as conn:
        conn.execute(
            """
            UPDATE task_attempts
            SET executor_type = ?,
                tool_name = COALESCE(?, tool_name),
                exit_code = COALESCE(?, exit_code),
                error_code = COALESCE(?, error_code),
                error_message = COALESCE(?, error_message)
            WHERE id = ?
            """,
            (executor_type, tool_name, exit_code, error_code, error_message, attempt_id),
        )


def schedule_retry(task_id: str, attempt_id: str, error_message: str | None = None, delay_seconds: int = 30) -> None:
    retry_at = (datetime.now(timezone.utc) + timedelta(seconds=delay_seconds)).isoformat()
    completed_at = now_iso()
    with transaction() as conn:
        row = conn.execute(
            "SELECT attempt_count, max_attempts FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()
        next_attempt_count = row["attempt_count"] + 1
        next_state = "retry_wait" if next_attempt_count < row["max_attempts"] else "dead_letter"
        conn.execute(
            """
            UPDATE tasks
            SET state = ?,
                attempt_count = ?,
                schedule_at = CASE WHEN ? = 'retry_wait' THEN ? ELSE NULL END,
                lease_owner = NULL,
                lease_expires_at = NULL,
                completed_at = CASE WHEN ? = 'dead_letter' THEN ? ELSE completed_at END,
                last_error_message = ?
            WHERE id = ?
            """,
            (
                next_state,
                next_attempt_count,
                next_state,
                retry_at,
                next_state,
                completed_at,
                error_message,
                task_id,
            ),
        )
        conn.execute(
            """
            UPDATE task_attempts
            SET ended_at = ?, outcome = 'failed', error_message = COALESCE(?, error_message)
            WHERE id = ?
            """,
            (completed_at, error_message, attempt_id),
        )


def fetch_legacy_event(task_id: str) -> dict | None:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if row is None:
            return None
        return _json_payload_to_legacy_event(row)


def upsert_result(task_id: str, status: str, summary: dict, structured_result: dict) -> None:
    with transaction() as conn:
        conn.execute(
            """
            INSERT INTO results(task_id, status, summary_json, structured_json, created_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(task_id) DO UPDATE SET
                status = excluded.status,
                summary_json = excluded.summary_json,
                structured_json = excluded.structured_json,
                created_at = excluded.created_at
            """,
            (
                task_id,
                status,
                json.dumps(summary, ensure_ascii=False),
                json.dumps(structured_result, ensure_ascii=False),
                now_iso(),
            ),
        )
    try:
        from knowledge.writeback import write_result_to_knowledge

        write_result_to_knowledge(
            task_id=task_id,
            status=status,
            summary=summary,
            structured_result=structured_result,
        )
    except Exception:
        pass


def insert_artifact(task_id: str, kind: str, path: str, mime_type: str | None = None) -> None:
    artifact_path = Path(path)
    with transaction() as conn:
        conn.execute(
            """
            INSERT INTO artifacts(id, task_id, kind, path, mime_type, size_bytes, sha256, created_at)
            VALUES (?, ?, ?, ?, ?, ?, NULL, ?)
            """,
            (
                str(uuid.uuid4()),
                task_id,
                kind,
                path,
                mime_type,
                artifact_path.stat().st_size if artifact_path.exists() else None,
                now_iso(),
            ),
        )


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
