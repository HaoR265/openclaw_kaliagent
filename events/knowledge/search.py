#!/usr/bin/env python3
from __future__ import annotations

import json

from db import get_connection
from knowledge.db import get_connection as get_knowledge_connection, seed_if_empty


def search_intel(query: str = "", capability: str | None = None) -> dict:
    seed_if_empty()
    with get_knowledge_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, title, summary, capability, confidence_level, validated_status,
                   published_at, source_name
            FROM intel_items
            ORDER BY published_at DESC
            LIMIT 24
            """
        ).fetchall()

    items = []
    q = query.lower().strip()
    for row in rows:
        if capability and row["capability"] != capability:
            continue
        haystack = f"{row['title']} {row['summary']}".lower()
        if q and q not in haystack:
            continue
        items.append(
            {
                "id": row["id"],
                "kind": "intel-item",
                "title": row["title"],
                "summary": row["summary"],
                "confidence_level": row["confidence_level"],
                "validated_status": row["validated_status"],
                "time_range": {"effective_from": row["published_at"], "effective_to": None},
                "source_refs": [row["source_name"]],
                "why_relevant": "derived from knowledge intel seed/runtime data",
                "capability": row["capability"],
                "status": "published",
            }
        )

    if items:
        return {
            "items": items[:8],
            "total_estimate": len(items),
            "query_echo": query,
            "applied_filters": {"capability": capability} if capability else {},
            "warnings": [],
            "refs": [],
        }

    sql = """
        SELECT
            r.task_id,
            r.status,
            r.summary_json,
            r.created_at,
            t.capability,
            t.operation
        FROM results r
        JOIN tasks t ON t.id = r.task_id
        ORDER BY r.created_at DESC
        LIMIT 24
    """
    with get_connection() as conn:
        rows = conn.execute(sql).fetchall()

    items = []
    q = query.lower().strip()
    for row in rows:
        if capability and row["capability"] != capability:
            continue
        summary = json.loads(row["summary_json"] or "{}")
        haystack = f"{row['operation']} {summary.get('message', '')}".lower()
        if q and q not in haystack:
            continue
        items.append(
            {
                "id": row["task_id"],
                "kind": "result-intel",
                "title": row["operation"],
                "summary": summary.get("message") or "recent execution result",
                "confidence_level": "medium",
                "validated_status": "runtime-derived",
                "time_range": {"effective_from": row["created_at"], "effective_to": None},
                "source_refs": [row["task_id"]],
                "why_relevant": "derived from recent execution results",
                "capability": row["capability"],
                "status": row["status"],
            }
        )

    return {
        "items": items[:8],
        "total_estimate": len(items),
        "query_echo": query,
        "applied_filters": {"capability": capability} if capability else {},
        "warnings": [],
        "refs": [],
    }


def search_knowledge(recipes: list[dict], query: str = "", capability: str | None = None) -> dict:
    seed_if_empty()
    with get_knowledge_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, title, summary, primary_capability, tool_name, confidence_level, validated_status
            FROM knowledge_entries
            ORDER BY updated_at DESC
            LIMIT 24
            """
        ).fetchall()

    items = []
    q = query.lower().strip()
    for row in rows:
        if capability and row["primary_capability"] != capability:
            continue
        haystack = f"{row['title']} {row['summary']} {row['tool_name'] or ''}".lower()
        if q and q not in haystack:
            continue
        items.append(
            {
                "id": row["id"],
                "kind": "knowledge-entry",
                "title": row["title"],
                "summary": row["summary"],
                "confidence_level": row["confidence_level"],
                "validated_status": row["validated_status"],
                "time_range": {"effective_from": None, "effective_to": None},
                "source_refs": [row["tool_name"]] if row["tool_name"] else [],
                "why_relevant": "derived from knowledge seed/runtime data",
                "capability": row["primary_capability"],
            }
        )

    if items:
        return {
            "items": items[:8],
            "total_estimate": len(items),
            "query_echo": query,
            "applied_filters": {"capability": capability} if capability else {},
            "warnings": [],
            "refs": [],
        }

    items = []
    q = query.lower().strip()
    for recipe in recipes:
        if capability and recipe.get("capability") != capability:
            continue
        haystack = f"{recipe.get('operation', '')} {recipe.get('summary', '')} {recipe.get('tool_bin', '')}".lower()
        if q and q not in haystack:
            continue
        items.append(
            {
                "id": recipe.get("operation"),
                "kind": "recipe-knowledge",
                "title": recipe.get("operation"),
                "summary": recipe.get("summary") or recipe.get("tool_bin") or "",
                "confidence_level": "medium",
                "validated_status": "catalog-derived",
                "time_range": {"effective_from": None, "effective_to": None},
                "source_refs": [recipe.get("tool_bin")] if recipe.get("tool_bin") else [],
                "why_relevant": "derived from current recipe catalog",
                "capability": recipe.get("capability"),
            }
        )

    return {
        "items": items[:8],
        "total_estimate": len(items),
        "query_echo": query,
        "applied_filters": {"capability": capability} if capability else {},
        "warnings": [],
        "refs": [],
    }
