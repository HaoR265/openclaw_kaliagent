#!/usr/bin/env python3
from __future__ import annotations

import json

from db import get_connection as get_events_connection
from knowledge.db import get_connection as get_knowledge_connection


def _row_dict(row):
    return dict(row) if row is not None else None


def write_result_to_knowledge(task_id: str, status: str, summary: dict, structured_result: dict) -> None:
    with get_events_connection() as conn:
        task = conn.execute(
            """
            SELECT
                id,
                workflow_id,
                capability,
                operation,
                completed_at,
                payload_json
            FROM tasks
            WHERE id = ?
            """,
            (task_id,),
        ).fetchone()
    if not task:
        return

    task_item = _row_dict(task)
    payload = json.loads(task_item.get("payload_json") or "{}")
    params = payload.get("params") or {}
    title = f"{task_item.get('operation') or 'task'} result"
    message = summary.get("message") or structured_result.get("message") or f"runtime result from {task_item.get('operation') or 'task'}"
    confidence = "medium" if status == "succeeded" else "low"
    validated_status = "runtime-derived"
    intel_id = f"intel_runtime_{task_id}"
    knowledge_id = f"knowledge_runtime_{task_id}"
    body = json.dumps(
        {
            "task_id": task_id,
            "workflow_id": task_item.get("workflow_id"),
            "status": status,
            "summary": summary,
            "structured_result": structured_result,
            "params": params,
        },
        ensure_ascii=False,
        indent=2,
    )

    with get_knowledge_connection() as conn:
        conn.execute(
            """
            INSERT INTO intel_items (
                id, title, summary, source_type, source_name, source_url,
                published_at, collected_at, capability, confidence_level,
                validated_status, status
            ) VALUES (?, ?, ?, 'runtime-result', ?, '', ?, ?, ?, ?, ?, 'published')
            ON CONFLICT(id) DO UPDATE SET
                title = excluded.title,
                summary = excluded.summary,
                published_at = excluded.published_at,
                collected_at = excluded.collected_at,
                capability = excluded.capability,
                confidence_level = excluded.confidence_level,
                validated_status = excluded.validated_status,
                status = excluded.status
            """,
            (
                intel_id,
                title,
                message,
                task_id,
                task_item.get("completed_at"),
                task_item.get("completed_at"),
                task_item.get("capability"),
                confidence,
                validated_status,
            ),
        )
        conn.execute(
            """
            INSERT INTO knowledge_entries (
                id, entry_type, title, summary, body_markdown,
                primary_capability, tool_name, confidence_level,
                validated_status, created_at, updated_at
            ) VALUES (?, 'runtime-result', ?, ?, ?, ?, ?, ?, ?, COALESCE(?, datetime('now')), COALESCE(?, datetime('now')))
            ON CONFLICT(id) DO UPDATE SET
                title = excluded.title,
                summary = excluded.summary,
                body_markdown = excluded.body_markdown,
                primary_capability = excluded.primary_capability,
                tool_name = excluded.tool_name,
                confidence_level = excluded.confidence_level,
                validated_status = excluded.validated_status,
                updated_at = excluded.updated_at
            """,
            (
                knowledge_id,
                title,
                message,
                body,
                task_item.get("capability"),
                params.get("tool") or params.get("toolName"),
                confidence,
                validated_status,
                task_item.get("completed_at"),
                task_item.get("completed_at"),
            ),
        )
        conn.commit()

