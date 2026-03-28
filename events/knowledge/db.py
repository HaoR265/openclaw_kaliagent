#!/usr/bin/env python3
from __future__ import annotations

import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNTIME_DIR = ROOT / "events" / "runtime"
DB_PATH = RUNTIME_DIR / "knowledge.db"
MIGRATIONS_DIR = Path(__file__).resolve().parent / "migrations"


def get_connection() -> sqlite3.Connection:
    RUNTIME_DIR.mkdir(exist_ok=True)
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
    applied = {row["version"] for row in conn.execute("SELECT version FROM schema_migrations").fetchall()}
    for migration in sorted(MIGRATIONS_DIR.glob("*.sql")):
      if migration.name in applied:
          continue
      conn.executescript(migration.read_text(encoding="utf-8"))
      conn.execute("INSERT INTO schema_migrations(version) VALUES (?)", (migration.name,))
    conn.commit()


def seed_if_empty() -> None:
    with get_connection() as conn:
        intel_count = conn.execute("SELECT COUNT(*) FROM intel_items").fetchone()[0]
        knowledge_count = conn.execute("SELECT COUNT(*) FROM knowledge_entries").fetchone()[0]
        if intel_count == 0:
            conn.execute(
                """
                INSERT INTO intel_items (
                    id, title, summary, source_type, source_name, source_url,
                    published_at, collected_at, capability, confidence_level,
                    validated_status, status
                ) VALUES (?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'), ?, ?, ?, ?)
                """,
                (
                    "intel_seed_web",
                    "Web 入口情报占位",
                    "用于验证 Intel 页面与搜索链路的最小种子数据。",
                    "seed",
                    "local-seed",
                    "",
                    "web",
                    "medium",
                    "seeded",
                    "published",
                ),
            )
        if knowledge_count == 0:
            conn.execute(
                """
                INSERT INTO knowledge_entries (
                    id, entry_type, title, summary, body_markdown,
                    primary_capability, tool_name, confidence_level,
                    validated_status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
                """,
                (
                    "knowledge_seed_recon",
                    "playbook",
                    "Recon 初始路线占位",
                    "用于验证 Knowledge 页面与搜索链路的最小种子数据。",
                    "先建立暴露面，再决定是否进入更深的路径。",
                    "recon",
                    "nmap",
                    "medium",
                    "seeded",
                ),
            )
        conn.commit()
