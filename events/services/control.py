#!/usr/bin/env python3
from __future__ import annotations

import json
import uuid
from pathlib import Path

from db import get_connection, now_iso
from publish import publish_event


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def _row_dict(row):
    return dict(row) if row is not None else None


def _json_load(value, default):
    if not value:
        return default
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return default


def _validate_scope_for_revision(task_tree: list[dict], scope: dict) -> list[str]:
    issues: list[str] = []
    allowed_categories = set(_json_load(scope.get("allowed_categories_json"), []))
    allowed_tools = set(_json_load(scope.get("allowed_tools_json"), []))
    denied_tools = set(_json_load(scope.get("denied_tools_json"), []))
    high_risk_tools = set(_json_load(scope.get("high_risk_tools_json"), []))
    interactive_tools = set(_json_load(scope.get("interactive_tools_json"), []))

    for index, task in enumerate(task_tree or []):
        capability = task.get("category") or task.get("capability")
        params = task.get("params") or {}
        tool_name = params.get("tool") or params.get("toolName")
        interactive = bool(params.get("interactive"))
        label = f"step {index + 1} ({task.get('task') or task.get('operation') or 'task'})"

        if allowed_categories and capability and capability not in allowed_categories:
            issues.append(f"{label}: category {capability} not in approval scope")
        if tool_name and denied_tools and tool_name in denied_tools:
            issues.append(f"{label}: tool {tool_name} is denied")
        if tool_name and allowed_tools and tool_name not in allowed_tools:
            issues.append(f"{label}: tool {tool_name} is outside allowed tools")
        if tool_name and tool_name in high_risk_tools:
            issues.append(f"{label}: tool {tool_name} requires high-risk review")
        if interactive and interactive_tools and tool_name and tool_name not in interactive_tools:
            issues.append(f"{label}: interactive tool {tool_name} is not approved")
    return issues


def _campaign_available_actions(status: str) -> list[str]:
    transition_map = {
        "under_review": ["approve", "reject", "stop", "kill"],
        "created": ["resume", "stop", "kill"],
        "running": ["pause", "drain", "stop", "kill"],
        "paused": ["resume", "stop", "kill"],
        "draining": ["stop", "kill"],
        "stopped": [],
        "killed": [],
    }
    return transition_map.get(status, [])


def list_missions(limit: int = 30) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, title, objective_text, status, priority, latest_plan_id,
                   latest_workflow_id, active_campaign_run_id, created_at, updated_at
            FROM mission_sessions
            ORDER BY updated_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


def create_mission(
    title: str,
    objective_text: str,
    context_text: str = "",
    priority: str = "medium",
    created_by: str = "operator",
) -> dict:
    mission_id = _new_id("mis")
    now = now_iso()
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO mission_sessions (
                id, title, objective_text, context_text, operator_notes,
                status, priority, created_by, created_at, updated_at
            ) VALUES (?, ?, ?, ?, '', 'draft', ?, ?, ?, ?)
            """,
            (mission_id, title, objective_text, context_text, priority, created_by, now, now),
        )
        row = conn.execute("SELECT * FROM mission_sessions WHERE id = ?", (mission_id,)).fetchone()
        conn.commit()
    return dict(row)


def get_mission(mission_id: str) -> dict | None:
    with get_connection() as conn:
        mission = conn.execute(
            "SELECT * FROM mission_sessions WHERE id = ?",
            (mission_id,),
        ).fetchone()
        if not mission:
            return None
        messages = conn.execute(
            """
            SELECT id, role, author_type, author_id, content_text, summary_text,
                   message_kind, token_in, token_out, created_at
            FROM discussion_messages
            WHERE mission_session_id = ?
            ORDER BY created_at ASC
            """,
            (mission_id,),
        ).fetchall()
        analysis_jobs = conn.execute(
            """
            SELECT id, status, job_kind, query_text, output_summary, evidence_refs_json,
                   warning_refs_json, error_text, started_at, finished_at, created_at
            FROM analysis_jobs
            WHERE mission_session_id = ?
            ORDER BY created_at DESC
            LIMIT 10
            """,
            (mission_id,),
        ).fetchall()
        plans = conn.execute(
            """
            SELECT id, status, title, goal_summary, discussion_summary, assumptions_json,
                   warnings_json, evidence_refs_json, preferred_branch_key, created_at, updated_at
            FROM plan_candidates
            WHERE mission_session_id = ?
            ORDER BY updated_at DESC
            """,
            (mission_id,),
        ).fetchall()
        plan_ids = [row["id"] for row in plans]
        revisions = []
        if plan_ids:
            placeholders = ",".join("?" for _ in plan_ids)
            revisions = conn.execute(
                f"""
                SELECT id, plan_candidate_id, revision_no, branch_key, parent_revision_id,
                       status, change_summary, plan_outline_json, task_tree_json,
                       launchable, created_by, created_at
                FROM plan_revisions
                WHERE plan_candidate_id IN ({placeholders})
                ORDER BY created_at DESC
                """,
                plan_ids,
            ).fetchall()
        approval_scopes = conn.execute(
            """
            SELECT id, scope_name, allowed_categories_json, allowed_tools_json,
                   interactive_tools_json, high_risk_tools_json, denied_tools_json,
                   network_scope_json, confirmed_by, confirmed_at, expires_at
            FROM approval_scopes
            WHERE mission_session_id = ?
            ORDER BY confirmed_at DESC
            """,
            (mission_id,),
        ).fetchall()
        campaigns = conn.execute(
            """
            SELECT id, plan_revision_id, approval_scope_id, status, objective_summary,
                   scope_summary, execution_profile, max_parallelism, auto_replan_enabled,
                   started_at, finished_at, created_at, updated_at
            FROM campaign_runs
            WHERE mission_session_id = ?
            ORDER BY updated_at DESC
            """,
            (mission_id,),
        ).fetchall()
    return {
        "mission": dict(mission),
        "messages": [dict(row) for row in messages],
        "analysis_jobs": [
            {
                **dict(row),
                "evidence_refs_json": _json_load(row["evidence_refs_json"], []),
                "warning_refs_json": _json_load(row["warning_refs_json"], []),
            }
            for row in analysis_jobs
        ],
        "plans": [
            {
                **dict(row),
                "assumptions_json": _json_load(row["assumptions_json"], []),
                "warnings_json": _json_load(row["warnings_json"], []),
                "evidence_refs_json": _json_load(row["evidence_refs_json"], []),
            }
            for row in plans
        ],
        "revisions": [
            {
                **dict(row),
                "plan_outline_json": _json_load(row["plan_outline_json"], {}),
                "task_tree_json": _json_load(row["task_tree_json"], []),
            }
            for row in revisions
        ],
        "approval_scopes": [
            {
                **dict(row),
                "allowed_categories_json": _json_load(row["allowed_categories_json"], []),
                "allowed_tools_json": _json_load(row["allowed_tools_json"], []),
                "interactive_tools_json": _json_load(row["interactive_tools_json"], []),
                "high_risk_tools_json": _json_load(row["high_risk_tools_json"], []),
                "denied_tools_json": _json_load(row["denied_tools_json"], []),
                "network_scope_json": _json_load(row["network_scope_json"], {}),
            }
            for row in approval_scopes
        ],
        "campaigns": [dict(row) for row in campaigns],
    }


def add_discussion_message(
    mission_id: str,
    content_text: str,
    role: str = "user",
    author_type: str = "operator",
    author_id: str = "local",
    message_kind: str = "input",
) -> dict:
    message_id = _new_id("msg")
    now = now_iso()
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO discussion_messages (
                id, mission_session_id, role, author_type, author_id,
                content_text, summary_text, message_kind, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, '', ?, ?)
            """,
            (message_id, mission_id, role, author_type, author_id, content_text, message_kind, now),
        )
        conn.execute(
            "UPDATE mission_sessions SET status = 'discussing', updated_at = ? WHERE id = ?",
            (now, mission_id),
        )
        row = conn.execute(
            "SELECT * FROM discussion_messages WHERE id = ?",
            (message_id,),
        ).fetchone()
        conn.commit()
    return dict(row)


def create_analysis_job(
    mission_id: str,
    query_text: str,
    trigger_message_id: str | None = None,
    job_kind: str = "background_analysis",
    status: str = "queued",
    output_summary: str = "",
    evidence_refs: list | None = None,
    warning_refs: list | None = None,
) -> dict:
    analysis_id = _new_id("aj")
    now = now_iso()
    started_at = now if status in {"running", "completed"} else None
    finished_at = now if status == "completed" else None
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO analysis_jobs (
                id, mission_session_id, trigger_message_id, status, job_kind, query_text,
                input_snapshot_json, output_summary, evidence_refs_json, warning_refs_json,
                error_text, started_at, finished_at, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, '{}', ?, ?, ?, '', ?, ?, ?)
            """,
            (
                analysis_id,
                mission_id,
                trigger_message_id,
                status,
                job_kind,
                query_text,
                output_summary,
                json.dumps(evidence_refs or [], ensure_ascii=False),
                json.dumps(warning_refs or [], ensure_ascii=False),
                started_at,
                finished_at,
                now,
            ),
        )
        row = conn.execute("SELECT * FROM analysis_jobs WHERE id = ?", (analysis_id,)).fetchone()
        conn.commit()
    item = dict(row)
    item["evidence_refs_json"] = _json_load(item["evidence_refs_json"], [])
    item["warning_refs_json"] = _json_load(item["warning_refs_json"], [])
    return item


def update_analysis_job(
    analysis_job_id: str,
    *,
    status: str,
    output_summary: str = "",
    evidence_refs: list | None = None,
    warning_refs: list | None = None,
    error_text: str = "",
) -> dict | None:
    now = now_iso()
    started_at = now if status in {"running", "completed"} else None
    finished_at = now if status in {"completed", "failed"} else None
    with get_connection() as conn:
        existing = conn.execute(
            "SELECT id, started_at FROM analysis_jobs WHERE id = ?",
            (analysis_job_id,),
        ).fetchone()
        if not existing:
            return None
        conn.execute(
            """
            UPDATE analysis_jobs
            SET status = ?,
                output_summary = ?,
                evidence_refs_json = ?,
                warning_refs_json = ?,
                error_text = ?,
                started_at = COALESCE(started_at, ?),
                finished_at = COALESCE(?, finished_at)
            WHERE id = ?
            """,
            (
                status,
                output_summary,
                json.dumps(evidence_refs or [], ensure_ascii=False),
                json.dumps(warning_refs or [], ensure_ascii=False),
                error_text,
                started_at,
                finished_at,
                analysis_job_id,
            ),
        )
        row = conn.execute("SELECT * FROM analysis_jobs WHERE id = ?", (analysis_job_id,)).fetchone()
        conn.commit()
    item = dict(row)
    item["evidence_refs_json"] = _json_load(item["evidence_refs_json"], [])
    item["warning_refs_json"] = _json_load(item["warning_refs_json"], [])
    return item


def create_plan_candidate(
    mission_id: str,
    title: str,
    goal_summary: str = "",
    discussion_summary: str = "",
    assumptions: list | None = None,
    warnings: list | None = None,
    evidence_refs: list | None = None,
    source_message_id: str | None = None,
) -> dict:
    plan_id = _new_id("plan")
    now = now_iso()
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO plan_candidates (
                id, mission_session_id, source_message_id, status, title, goal_summary,
                discussion_summary, assumptions_json, warnings_json, evidence_refs_json,
                preferred_branch_key, created_at, updated_at
            ) VALUES (?, ?, ?, 'proposed', ?, ?, ?, ?, ?, ?, 'main', ?, ?)
            """,
            (
                plan_id,
                mission_id,
                source_message_id,
                title,
                goal_summary,
                discussion_summary,
                json.dumps(assumptions or [], ensure_ascii=False),
                json.dumps(warnings or [], ensure_ascii=False),
                json.dumps(evidence_refs or [], ensure_ascii=False),
                now,
                now,
            ),
        )
        conn.execute(
            "UPDATE mission_sessions SET latest_plan_id = ?, status = 'planned', updated_at = ? WHERE id = ?",
            (plan_id, now, mission_id),
        )
        row = conn.execute("SELECT * FROM plan_candidates WHERE id = ?", (plan_id,)).fetchone()
        conn.commit()
    item = dict(row)
    item["assumptions_json"] = _json_load(item["assumptions_json"], [])
    item["warnings_json"] = _json_load(item["warnings_json"], [])
    item["evidence_refs_json"] = _json_load(item["evidence_refs_json"], [])
    return item


def create_plan_revision(
    plan_id: str,
    change_summary: str,
    plan_outline: dict | None = None,
    task_tree: list | None = None,
    branch_key: str | None = "main",
    launchable: bool = False,
    parent_revision_id: str | None = None,
    created_by: str = "commander",
) -> dict:
    revision_id = _new_id("rev")
    now = now_iso()
    with get_connection() as conn:
        parent = None
        if parent_revision_id:
            parent = conn.execute(
                """
                SELECT id, plan_candidate_id, branch_key, plan_outline_json, task_tree_json, launchable
                FROM plan_revisions
                WHERE id = ? AND plan_candidate_id = ?
                """,
                (parent_revision_id, plan_id),
            ).fetchone()
            if not parent:
                raise ValueError("parent revision not found")
            if branch_key in {None, ""}:
                branch_key = parent["branch_key"]
            if plan_outline is None:
                plan_outline = _json_load(parent["plan_outline_json"], {})
            if task_tree is None:
                task_tree = _json_load(parent["task_tree_json"], [])
            if not launchable:
                launchable = bool(parent["launchable"])

        branch_key = branch_key or "main"
        current = conn.execute(
            """
            SELECT COALESCE(MAX(revision_no), 0) AS max_revision
            FROM plan_revisions
            WHERE plan_candidate_id = ? AND branch_key = ?
            """,
            (plan_id, branch_key),
        ).fetchone()
        revision_no = int(current["max_revision"]) + 1
        conn.execute(
            """
            INSERT INTO plan_revisions (
                id, plan_candidate_id, revision_no, branch_key, parent_revision_id,
                status, change_summary, plan_outline_json, task_tree_json, launchable,
                created_by, created_at
            ) VALUES (?, ?, ?, ?, ?, 'draft', ?, ?, ?, ?, ?, ?)
            """,
            (
                revision_id,
                plan_id,
                revision_no,
                branch_key,
                parent_revision_id,
                change_summary,
                json.dumps(plan_outline or {}, ensure_ascii=False),
                json.dumps(task_tree or [], ensure_ascii=False),
                1 if launchable else 0,
                created_by,
                now,
            ),
        )
        row = conn.execute("SELECT * FROM plan_revisions WHERE id = ?", (revision_id,)).fetchone()
        conn.commit()
    item = dict(row)
    item["plan_outline_json"] = _json_load(item["plan_outline_json"], {})
    item["task_tree_json"] = _json_load(item["task_tree_json"], [])
    return item


def create_branch_revision(
    revision_id: str,
    branch_key: str,
    change_summary: str = "",
) -> dict:
    with get_connection() as conn:
        base = conn.execute(
            """
            SELECT id, plan_candidate_id, branch_key, plan_outline_json, task_tree_json, launchable
            FROM plan_revisions
            WHERE id = ?
            """,
            (revision_id,),
        ).fetchone()
    if not base:
        raise ValueError("base revision not found")
    next_branch = (branch_key or "").strip()
    if not next_branch:
        raise ValueError("branch_key is required")
    if next_branch == base["branch_key"]:
        raise ValueError("branch_key must differ from the current branch")
    return create_plan_revision(
        plan_id=base["plan_candidate_id"],
        change_summary=change_summary or f"branch from {base['id']}",
        plan_outline=_json_load(base["plan_outline_json"], {}),
        task_tree=_json_load(base["task_tree_json"], []),
        branch_key=next_branch,
        launchable=bool(base["launchable"]),
        parent_revision_id=base["id"],
        created_by="commander",
    )


def create_campaign(
    mission_session_id: str,
    plan_revision_id: str,
    approval_scope_id: str,
    execution_profile: str = "steady",
    max_parallelism: int = 1,
    auto_replan_enabled: bool = True,
) -> dict:
    campaign_id = _new_id("camp")
    now = now_iso()
    with get_connection() as conn:
        mission = conn.execute(
            "SELECT id FROM mission_sessions WHERE id = ?",
            (mission_session_id,),
        ).fetchone()
        if not mission:
            raise ValueError("mission not found")
        revision = conn.execute(
            """
            SELECT pr.id, pr.change_summary, pr.task_tree_json, pc.mission_session_id, ms.objective_text
            FROM plan_revisions pr
            JOIN plan_candidates pc ON pc.id = pr.plan_candidate_id
            JOIN mission_sessions ms ON ms.id = pc.mission_session_id
            WHERE pr.id = ? AND pc.mission_session_id = ?
            """,
            (plan_revision_id, mission_session_id),
        ).fetchone()
        if not revision:
            raise ValueError("revision does not belong to mission")
        scope = conn.execute(
            "SELECT * FROM approval_scopes WHERE id = ? AND mission_session_id = ?",
            (approval_scope_id, mission_session_id),
        ).fetchone()
        if not scope:
            raise ValueError("approval scope does not belong to mission")
        scope_issues = _validate_scope_for_revision(
            _json_load(revision["task_tree_json"], []),
            dict(scope),
        )
        status = "under_review" if scope_issues else "created"
        scope_summary = "; ".join(scope_issues[:6]) if scope_issues else "scope validated"
        conn.execute(
            """
            INSERT INTO campaign_runs (
                id, mission_session_id, plan_revision_id, approval_scope_id, status,
                objective_summary, scope_summary, execution_profile, max_parallelism,
                auto_replan_enabled, started_at, finished_at, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL, ?, ?)
            """,
            (
                campaign_id,
                mission_session_id,
                plan_revision_id,
                approval_scope_id,
                status,
                revision["objective_text"],
                scope_summary,
                execution_profile,
                max_parallelism,
                1 if auto_replan_enabled else 0,
                now,
                now,
            ),
        )
        conn.execute(
            "UPDATE mission_sessions SET active_campaign_run_id = ?, updated_at = ? WHERE id = ?",
            (campaign_id, now, mission_session_id),
        )
        conn.execute(
            """
            INSERT INTO campaign_events (
                id, campaign_run_id, event_type, severity, message, payload_json, created_at
            ) VALUES (?, ?, 'campaign_started', 'info', ?, '{}', ?)
            """,
            (_new_id("cevt"), campaign_id, "campaign created" if not scope_issues else "campaign created with scope issues", now),
        )
        for issue in scope_issues[:10]:
            conn.execute(
                """
                INSERT INTO campaign_events (
                    id, campaign_run_id, event_type, severity, message, payload_json, created_at
                ) VALUES (?, ?, 'scope_validation', 'warning', ?, '{}', ?)
                """,
                (_new_id("cevt"), campaign_id, issue, now),
            )
        row = conn.execute("SELECT * FROM campaign_runs WHERE id = ?", (campaign_id,)).fetchone()
        conn.commit()
    return dict(row)


def create_approval_scope(
    mission_session_id: str,
    scope_name: str,
    allowed_categories: list | None = None,
    allowed_tools: list | None = None,
    interactive_tools: list | None = None,
    high_risk_tools: list | None = None,
    denied_tools: list | None = None,
    network_scope: dict | None = None,
    confirmed_by: str = "operator",
) -> dict:
    scope_id = _new_id("scope")
    now = now_iso()
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO approval_scopes (
                id, mission_session_id, scope_name, allowed_categories_json, allowed_tools_json,
                interactive_tools_json, high_risk_tools_json, denied_tools_json, network_scope_json,
                confirmed_by, confirmed_at, expires_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)
            """,
            (
                scope_id,
                mission_session_id,
                scope_name,
                json.dumps(allowed_categories or [], ensure_ascii=False),
                json.dumps(allowed_tools or [], ensure_ascii=False),
                json.dumps(interactive_tools or [], ensure_ascii=False),
                json.dumps(high_risk_tools or [], ensure_ascii=False),
                json.dumps(denied_tools or [], ensure_ascii=False),
                json.dumps(network_scope or {}, ensure_ascii=False),
                confirmed_by,
                now,
            ),
        )
        row = conn.execute("SELECT * FROM approval_scopes WHERE id = ?", (scope_id,)).fetchone()
        conn.commit()
    item = dict(row)
    for key in [
        "allowed_categories_json",
        "allowed_tools_json",
        "interactive_tools_json",
        "high_risk_tools_json",
        "denied_tools_json",
        "network_scope_json",
    ]:
        item[key] = _json_load(item[key], [] if key.endswith("_json") and key != "network_scope_json" else {})
    return item


def get_campaign_events(campaign_id: str, limit: int = 50) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, event_type, severity, message, payload_json, related_task_id,
                   related_attempt_id, created_at
            FROM campaign_events
            WHERE campaign_run_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (campaign_id, limit),
        ).fetchall()
    items = []
    for row in rows:
        item = dict(row)
        item["payload_json"] = _json_load(item["payload_json"], {})
        items.append(item)
    return items


def list_campaigns(limit: int = 20) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                cr.id,
                cr.mission_session_id,
                cr.plan_revision_id,
                cr.approval_scope_id,
                cr.status,
                cr.objective_summary,
                cr.execution_profile,
                cr.max_parallelism,
                cr.auto_replan_enabled,
                cr.started_at,
                cr.finished_at,
                cr.created_at,
                cr.updated_at,
                ms.title AS mission_title
            FROM campaign_runs cr
            JOIN mission_sessions ms ON ms.id = cr.mission_session_id
            ORDER BY cr.updated_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    items = []
    for row in rows:
        item = dict(row)
        item["available_actions"] = _campaign_available_actions(item["status"])
        items.append(item)
    return items


def get_campaign_detail(campaign_id: str) -> dict | None:
    with get_connection() as conn:
        campaign = conn.execute(
            """
            SELECT
                cr.*,
                ms.title AS mission_title,
                ms.objective_text,
                pr.branch_key,
                pr.revision_no,
                pr.change_summary AS revision_change_summary,
                pr.task_tree_json,
                pr.plan_outline_json,
                aps.scope_name,
                aps.allowed_categories_json,
                aps.allowed_tools_json,
                aps.denied_tools_json,
                aps.network_scope_json,
                aps.high_risk_tools_json,
                aps.interactive_tools_json,
                ms.latest_workflow_id
            FROM campaign_runs cr
            JOIN mission_sessions ms ON ms.id = cr.mission_session_id
            JOIN plan_revisions pr ON pr.id = cr.plan_revision_id
            JOIN approval_scopes aps ON aps.id = cr.approval_scope_id
            WHERE cr.id = ?
            """,
            (campaign_id,),
        ).fetchone()
        if not campaign:
            return None
    item = dict(campaign)
    item["allowed_categories_json"] = _json_load(item["allowed_categories_json"], [])
    item["allowed_tools_json"] = _json_load(item["allowed_tools_json"], [])
    item["denied_tools_json"] = _json_load(item["denied_tools_json"], [])
    item["network_scope_json"] = _json_load(item["network_scope_json"], {})
    item["high_risk_tools_json"] = _json_load(item["high_risk_tools_json"], [])
    item["interactive_tools_json"] = _json_load(item["interactive_tools_json"], [])
    item["task_tree_json"] = _json_load(item["task_tree_json"], [])
    item["plan_outline_json"] = _json_load(item["plan_outline_json"], {})
    events = get_campaign_events(campaign_id, limit=50)
    item["scope_issues"] = [event["message"] for event in events if event["event_type"] == "scope_validation"]
    item["available_actions"] = _campaign_available_actions(item["status"])
    return {
        "campaign": item,
        "events": events,
    }


def _get_plan_revision(conn, revision_id: str):
    return conn.execute(
        """
        SELECT
            pr.id,
            pr.plan_candidate_id,
            pr.revision_no,
            pr.branch_key,
            pr.change_summary,
            pr.plan_outline_json,
            pr.task_tree_json,
            pr.launchable,
            pc.mission_session_id,
            pc.title AS plan_title,
            ms.title AS mission_title
        FROM plan_revisions pr
        JOIN plan_candidates pc ON pc.id = pr.plan_candidate_id
        JOIN mission_sessions ms ON ms.id = pc.mission_session_id
        WHERE pr.id = ?
        """,
        (revision_id,),
    ).fetchone()


def launch_plan_revision(
    revision_id: str,
    *,
    launch_mode: str = "assisted",
    execution_profile: str = "steady",
    selected_tools: list[str] | None = None,
) -> dict:
    workflow_id = _new_id("wf")
    launch_batch_id = _new_id("lb")
    now = now_iso()
    with get_connection() as conn:
        revision = _get_plan_revision(conn, revision_id)
        if not revision:
            raise ValueError("revision not found")
        task_tree = _json_load(revision["task_tree_json"], [])
        published_task_ids: list[str] = []
        for task in task_tree:
            task_params = dict(task.get("params") or {})
            if task.get("notes"):
                task_params.setdefault("notes", task["notes"])
            task_params.setdefault("workflowId", workflow_id)
            task_params.setdefault("planRevisionId", revision_id)
            task_id = publish_event(
                event_type=task.get("type", "task"),
                task=task.get("task") or task.get("operation") or "unknown-task",
                params=task_params,
                agent=task.get("agent", "offense"),
                category=task.get("category") or task.get("capability"),
                execution_profile=execution_profile,
                secondary_confirmation=bool(task_params.get("secondaryConfirmation", False)),
                interactive=bool(task_params.get("interactive", False)),
            )
            published_task_ids.append(task_id)
            conn.execute(
                """
                UPDATE tasks
                SET workflow_id = ?,
                    parent_task_id = NULL,
                    correlation_id = ?,
                    payload_json = payload_json
                WHERE id = ?
                """,
                (workflow_id, workflow_id, task_id),
            )

        conn.execute(
            """
            INSERT INTO launch_batches (
                id, mission_session_id, plan_revision_id, workflow_id, launch_mode,
                execution_profile, selected_tools_json, task_count, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'launched', ?)
            """,
            (
                launch_batch_id,
                revision["mission_session_id"],
                revision_id,
                workflow_id,
                launch_mode,
                execution_profile,
                json.dumps(selected_tools or [], ensure_ascii=False),
                len(published_task_ids),
                now,
            ),
        )
        conn.execute(
            """
            UPDATE mission_sessions
            SET latest_workflow_id = ?, status = 'running', updated_at = ?
            WHERE id = ?
            """,
            (workflow_id, now, revision["mission_session_id"]),
        )
        conn.commit()

    return {
        "launch_batch_id": launch_batch_id,
        "workflow_id": workflow_id,
        "task_ids": published_task_ids,
        "task_count": len(published_task_ids),
        "launch_mode": launch_mode,
        "execution_profile": execution_profile,
    }


def list_workflows(limit: int = 20) -> list[dict]:
    with get_connection() as conn:
        launch_rows = conn.execute(
            """
            SELECT
                lb.workflow_id,
                lb.id AS launch_batch_id,
                lb.launch_mode,
                lb.execution_profile,
                lb.task_count,
                lb.status AS launch_status,
                lb.created_at,
                ms.id AS mission_id,
                ms.title AS mission_title,
                ms.active_campaign_run_id,
                (
                  SELECT COUNT(*) FROM tasks t
                  WHERE t.workflow_id = lb.workflow_id
                ) AS total_tasks,
                (
                  SELECT COUNT(*) FROM tasks t
                  WHERE t.workflow_id = lb.workflow_id AND t.state = 'succeeded'
                ) AS succeeded_tasks,
                (
                  SELECT COUNT(*) FROM tasks t
                  WHERE t.workflow_id = lb.workflow_id AND t.state IN ('failed', 'dead_letter')
                ) AS failed_tasks
            FROM launch_batches lb
            JOIN mission_sessions ms ON ms.id = lb.mission_session_id
            ORDER BY lb.created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        experiment_rows = conn.execute(
            """
            SELECT
                er.workflow_id,
                er.id AS launch_batch_id,
                'research-experiment' AS launch_mode,
                COALESCE(
                    (
                        SELECT json_extract(t.payload_json, '$.params.executionProfile')
                        FROM tasks t
                        WHERE t.workflow_id = er.workflow_id
                        ORDER BY t.created_at ASC
                        LIMIT 1
                    ),
                    'steady'
                ) AS execution_profile,
                (
                  SELECT COUNT(*) FROM tasks t
                  WHERE t.workflow_id = er.workflow_id
                ) AS task_count,
                'launched' AS launch_status,
                er.created_at,
                ms.id AS mission_id,
                ms.title AS mission_title,
                ms.active_campaign_run_id,
                (
                  SELECT COUNT(*) FROM tasks t
                  WHERE t.workflow_id = er.workflow_id
                ) AS total_tasks,
                (
                  SELECT COUNT(*) FROM tasks t
                  WHERE t.workflow_id = er.workflow_id AND t.state = 'succeeded'
                ) AS succeeded_tasks,
                (
                  SELECT COUNT(*) FROM tasks t
                  WHERE t.workflow_id = er.workflow_id AND t.state IN ('failed', 'dead_letter')
                ) AS failed_tasks
            FROM experiment_requests er
            JOIN research_sessions rs ON rs.id = er.research_session_id
            JOIN mission_sessions ms ON ms.id = rs.mission_session_id
            WHERE er.workflow_id IS NOT NULL
            ORDER BY er.created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    items: list[dict] = []
    seen_workflows: set[str] = set()
    for row in list(launch_rows) + list(experiment_rows):
        item = dict(row)
        workflow_id = item.get("workflow_id")
        if not workflow_id or workflow_id in seen_workflows:
            continue
        seen_workflows.add(workflow_id)
        items.append(item)
    items.sort(key=lambda item: item.get("created_at") or "", reverse=True)
    return items[:limit]


def get_workflow_detail(workflow_id: str) -> dict | None:
    with get_connection() as conn:
        launch = conn.execute(
            """
            SELECT
                lb.workflow_id,
                lb.id AS launch_batch_id,
                lb.launch_mode,
                lb.execution_profile,
                lb.task_count,
                lb.status AS launch_status,
                lb.created_at,
                ms.id AS mission_id,
                ms.title AS mission_title,
                ms.active_campaign_run_id,
                pr.id AS plan_revision_id,
                pr.change_summary
            FROM launch_batches lb
            JOIN mission_sessions ms ON ms.id = lb.mission_session_id
            JOIN plan_revisions pr ON pr.id = lb.plan_revision_id
            WHERE lb.workflow_id = ?
            """,
            (workflow_id,),
        ).fetchone()
        if not launch:
            launch = conn.execute(
                """
                SELECT
                    er.workflow_id,
                    er.id AS launch_batch_id,
                    'research-experiment' AS launch_mode,
                    COALESCE(
                        (
                            SELECT json_extract(t.payload_json, '$.params.executionProfile')
                            FROM tasks t
                            WHERE t.workflow_id = er.workflow_id
                            ORDER BY t.created_at ASC
                            LIMIT 1
                        ),
                        'steady'
                    ) AS execution_profile,
                    (
                      SELECT COUNT(*) FROM tasks t
                      WHERE t.workflow_id = er.workflow_id
                    ) AS task_count,
                    'launched' AS launch_status,
                    er.created_at,
                    ms.id AS mission_id,
                    ms.title AS mission_title,
                    ms.active_campaign_run_id,
                    rs.plan_revision_id,
                    er.request_summary AS change_summary
                FROM experiment_requests er
                JOIN research_sessions rs ON rs.id = er.research_session_id
                JOIN mission_sessions ms ON ms.id = rs.mission_session_id
                WHERE er.workflow_id = ?
                """,
                (workflow_id,),
            ).fetchone()
        if not launch:
            return None
        tasks = conn.execute(
            """
            SELECT
                t.id, t.capability, t.operation, t.state, t.priority, t.created_at,
                t.started_at, t.completed_at, t.last_error_code, t.last_error_message,
                a.executor_type, a.tool_name, a.started_at AS attempt_started_at,
                a.ended_at AS attempt_ended_at, a.outcome AS attempt_outcome,
                r.status AS result_status, r.summary_json, r.structured_json
            FROM tasks t
            LEFT JOIN task_attempts a
              ON a.task_id = t.id
             AND a.started_at = (
               SELECT MAX(a2.started_at) FROM task_attempts a2 WHERE a2.task_id = t.id
             )
            LEFT JOIN results r ON r.task_id = t.id
            WHERE t.workflow_id = ?
            ORDER BY t.created_at ASC
            """,
            (workflow_id,),
        ).fetchall()
        artifacts = conn.execute(
            """
            SELECT id, task_id, kind, path, mime_type, size_bytes, created_at
            FROM artifacts
            WHERE task_id IN (SELECT id FROM tasks WHERE workflow_id = ?)
            ORDER BY created_at DESC
            """,
            (workflow_id,),
        ).fetchall()

    timeline = []
    task_items = []
    for row in tasks:
        item = dict(row)
        item["summary_json"] = _json_load(item["summary_json"], {})
        item["structured_json"] = _json_load(item["structured_json"], {})
        task_items.append(item)
        timeline.append(
            {
                "type": "task",
                "task_id": item["id"],
                "operation": item["operation"],
                "status": item["state"],
                "timestamp": item["completed_at"] or item["started_at"] or item["created_at"],
            }
        )
    for artifact in artifacts:
        timeline.append(
            {
                "type": "artifact",
                "task_id": artifact["task_id"],
                "kind": artifact["kind"],
                "timestamp": artifact["created_at"],
            }
        )
    timeline.sort(key=lambda item: item["timestamp"] or "")
    return {
        "workflow": dict(launch),
        "tasks": task_items,
        "artifacts": [dict(row) for row in artifacts],
        "timeline": timeline,
    }


def get_artifact_detail(artifact_id: str) -> dict | None:
    with get_connection() as conn:
        artifact = conn.execute(
            """
            SELECT
                a.id, a.task_id, a.kind, a.path, a.mime_type, a.size_bytes, a.created_at,
                t.workflow_id, t.capability, t.operation, t.state,
                r.status AS result_status, r.summary_json
            FROM artifacts a
            JOIN tasks t ON t.id = a.task_id
            LEFT JOIN results r ON r.task_id = t.id
            WHERE a.id = ?
            """,
            (artifact_id,),
        ).fetchone()
        if not artifact:
            return None
    item = dict(artifact)
    item["summary_json"] = _json_load(item["summary_json"], {})

    path = Path(item["path"])
    preview = None
    if path.exists() and path.is_file():
        is_text_like = (
            str(item.get("mime_type") or "").startswith("text/")
            or str(item.get("mime_type") or "").endswith("json")
            or path.suffix.lower() in {".txt", ".log", ".json", ".md", ".csv", ".xml", ".yaml", ".yml"}
        )
        if is_text_like:
            try:
                preview = path.read_text(encoding="utf-8", errors="replace")[:4000]
            except OSError:
                preview = None

    item["preview_text"] = preview
    return item


def control_campaign(campaign_id: str, action: str) -> dict | None:
    status_map = {
        "approve": "created",
        "reject": "stopped",
        "pause": "paused",
        "resume": "running",
        "drain": "draining",
        "stop": "stopped",
        "kill": "killed",
    }
    if action not in status_map:
        raise ValueError("unsupported action")
    now = now_iso()
    with get_connection() as conn:
        existing = conn.execute(
            "SELECT id, status FROM campaign_runs WHERE id = ?",
            (campaign_id,),
        ).fetchone()
        if not existing:
            return None
        if existing["status"] == status_map[action]:
            return dict(existing)
        if action not in _campaign_available_actions(existing["status"]):
            raise ValueError(f"action {action} is not allowed from status {existing['status']}")
        severity = "info"
        if action in {"pause", "drain", "stop", "reject"}:
            severity = "warning"
        if action == "kill":
            severity = "error"
        conn.execute(
            "UPDATE campaign_runs SET status = ?, updated_at = ? WHERE id = ?",
            (status_map[action], now, campaign_id),
        )
        conn.execute(
            """
            INSERT INTO campaign_events (
                id, campaign_run_id, event_type, severity, message, payload_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                _new_id("cevt"),
                campaign_id,
                f"{action}_requested",
                severity,
                f"campaign {action} requested",
                json.dumps(
                    {
                        "action": action,
                        "from_status": existing["status"],
                        "to_status": status_map[action],
                    },
                    ensure_ascii=False,
                ),
                now,
            ),
        )
        row = conn.execute("SELECT * FROM campaign_runs WHERE id = ?", (campaign_id,)).fetchone()
        conn.commit()
    return dict(row) if row else None


def list_research_sessions(limit: int = 20) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                rs.id,
                rs.mission_session_id,
                rs.plan_revision_id,
                rs.workflow_id,
                rs.session_goal,
                rs.scope_summary,
                rs.status,
                rs.created_by,
                rs.created_at,
                rs.updated_at,
                ms.title AS mission_title,
                (
                  SELECT COUNT(*) FROM research_questions rq
                  WHERE rq.research_session_id = rs.id
                ) AS question_count,
                (
                  SELECT COUNT(*) FROM experiment_requests er
                  WHERE er.research_session_id = rs.id
                ) AS experiment_count
            FROM research_sessions rs
            JOIN mission_sessions ms ON ms.id = rs.mission_session_id
            ORDER BY rs.updated_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


def create_research_session(
    mission_session_id: str,
    plan_revision_id: str | None = None,
    workflow_id: str | None = None,
    session_goal: str = "",
    scope_summary: str = "",
    created_by: str = "operator",
) -> dict:
    session_id = _new_id("rs")
    now = now_iso()
    with get_connection() as conn:
        mission = conn.execute(
            "SELECT id, latest_workflow_id FROM mission_sessions WHERE id = ?",
            (mission_session_id,),
        ).fetchone()
        if not mission:
            raise ValueError("mission not found")
        if plan_revision_id:
            revision = conn.execute(
                """
                SELECT pr.id
                FROM plan_revisions pr
                JOIN plan_candidates pc ON pc.id = pr.plan_candidate_id
                WHERE pr.id = ? AND pc.mission_session_id = ?
                """,
                (plan_revision_id, mission_session_id),
            ).fetchone()
            if not revision:
                raise ValueError("revision does not belong to mission")
        if workflow_id:
            workflow = conn.execute(
                """
                SELECT workflow_id
                FROM launch_batches
                WHERE workflow_id = ? AND mission_session_id = ?
                UNION
                SELECT er.workflow_id
                FROM experiment_requests er
                JOIN research_sessions rs ON rs.id = er.research_session_id
                WHERE er.workflow_id = ? AND rs.mission_session_id = ?
                LIMIT 1
                """,
                (workflow_id, mission_session_id, workflow_id, mission_session_id),
            ).fetchone()
            if not workflow:
                raise ValueError("workflow does not belong to mission")
        conn.execute(
            """
            INSERT INTO research_sessions (
                id, mission_session_id, plan_revision_id, workflow_id, session_goal,
                scope_summary, status, created_by, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, 'active', ?, ?, ?)
            """,
            (
                session_id,
                mission_session_id,
                plan_revision_id,
                workflow_id or mission["latest_workflow_id"],
                session_goal,
                scope_summary,
                created_by,
                now,
                now,
            ),
        )
        conn.execute(
            "UPDATE mission_sessions SET updated_at = ? WHERE id = ?",
            (now, mission_session_id),
        )
        row = conn.execute("SELECT * FROM research_sessions WHERE id = ?", (session_id,)).fetchone()
        conn.commit()
    return dict(row)


def create_research_question(
    research_session_id: str,
    question_text: str,
    priority: int = 50,
    assigned_experts: list[str] | None = None,
) -> dict:
    if not question_text.strip():
        raise ValueError("question_text is required")
    question_id = _new_id("rq")
    now = now_iso()
    with get_connection() as conn:
        session = conn.execute(
            "SELECT id FROM research_sessions WHERE id = ?",
            (research_session_id,),
        ).fetchone()
        if not session:
            raise ValueError("research session not found")
        conn.execute(
            """
            INSERT INTO research_questions (
                id, research_session_id, question_text, priority, assigned_experts_json, status, created_at
            ) VALUES (?, ?, ?, ?, ?, 'open', ?)
            """,
            (
                question_id,
                research_session_id,
                question_text,
                priority,
                json.dumps(assigned_experts or [], ensure_ascii=False),
                now,
            ),
        )
        conn.execute(
            "UPDATE research_sessions SET updated_at = ? WHERE id = ?",
            (now, research_session_id),
        )
        row = conn.execute("SELECT * FROM research_questions WHERE id = ?", (question_id,)).fetchone()
        conn.commit()
    item = dict(row)
    item["assigned_experts_json"] = _json_load(item["assigned_experts_json"], [])
    return item


def create_hypothesis(
    research_question_id: str,
    expert_role: str,
    title: str,
    summary: str = "",
    assumptions: list | None = None,
    applicability_conditions: list | None = None,
    confidence_before: float = 0.5,
) -> dict:
    if not title.strip():
        raise ValueError("title is required")
    hypothesis_id = _new_id("hyp")
    now = now_iso()
    with get_connection() as conn:
        question = conn.execute(
            "SELECT id, research_session_id FROM research_questions WHERE id = ?",
            (research_question_id,),
        ).fetchone()
        if not question:
            raise ValueError("research question not found")
        conn.execute(
            """
            INSERT INTO hypotheses (
                id, research_question_id, expert_role, title, summary, assumptions_json,
                applicability_conditions_json, confidence_before, skeptic_review_status,
                skeptic_notes_json, status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending', '[]', 'open', ?, ?)
            """,
            (
                hypothesis_id,
                research_question_id,
                expert_role,
                title,
                summary,
                json.dumps(assumptions or [], ensure_ascii=False),
                json.dumps(applicability_conditions or [], ensure_ascii=False),
                confidence_before,
                now,
                now,
            ),
        )
        conn.execute(
            "UPDATE research_sessions SET updated_at = ? WHERE id = ?",
            (now, question["research_session_id"]),
        )
        row = conn.execute("SELECT * FROM hypotheses WHERE id = ?", (hypothesis_id,)).fetchone()
        conn.commit()
    item = dict(row)
    item["assumptions_json"] = _json_load(item["assumptions_json"], [])
    item["applicability_conditions_json"] = _json_load(item["applicability_conditions_json"], [])
    item["skeptic_notes_json"] = _json_load(item["skeptic_notes_json"], [])
    return item


def review_hypothesis(
    hypothesis_id: str,
    skeptic_review_status: str,
    skeptic_notes: list | None = None,
) -> dict | None:
    now = now_iso()
    with get_connection() as conn:
        hypothesis = conn.execute(
            """
            SELECT h.id, rq.research_session_id
            FROM hypotheses h
            JOIN research_questions rq ON rq.id = h.research_question_id
            WHERE h.id = ?
            """,
            (hypothesis_id,),
        ).fetchone()
        if not hypothesis:
            return None
        conn.execute(
            """
            UPDATE hypotheses
            SET skeptic_review_status = ?,
                skeptic_notes_json = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                skeptic_review_status,
                json.dumps(skeptic_notes or [], ensure_ascii=False),
                now,
                hypothesis_id,
            ),
        )
        conn.execute(
            "UPDATE research_sessions SET updated_at = ? WHERE id = ?",
            (now, hypothesis["research_session_id"]),
        )
        row = conn.execute("SELECT * FROM hypotheses WHERE id = ?", (hypothesis_id,)).fetchone()
        conn.commit()
    item = dict(row)
    item["assumptions_json"] = _json_load(item["assumptions_json"], [])
    item["applicability_conditions_json"] = _json_load(item["applicability_conditions_json"], [])
    item["skeptic_notes_json"] = _json_load(item["skeptic_notes_json"], [])
    return item


def create_experiment_request(
    hypothesis_id: str,
    requested_by_role: str,
    request_summary: str,
    required_observations: list | None = None,
    suggested_tasks: list | None = None,
    expected_artifacts: list | None = None,
    risk_level: str = "medium",
    approval_mode: str = "commander_review",
) -> dict:
    if not request_summary.strip():
        raise ValueError("request_summary is required")
    experiment_id = _new_id("exp")
    now = now_iso()
    with get_connection() as conn:
        hypothesis = conn.execute(
            """
            SELECT
                h.id,
                h.expert_role,
                rq.research_session_id
            FROM hypotheses h
            JOIN research_questions rq ON rq.id = h.research_question_id
            WHERE h.id = ?
            """,
            (hypothesis_id,),
        ).fetchone()
        if not hypothesis:
            raise ValueError("hypothesis not found")
        conn.execute(
            """
            INSERT INTO experiment_requests (
                id, research_session_id, hypothesis_id, requested_by_role, request_summary,
                required_observations_json, suggested_tasks_json, expected_artifacts_json,
                risk_level, approval_mode, status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending_review', ?, ?)
            """,
            (
                experiment_id,
                hypothesis["research_session_id"],
                hypothesis_id,
                requested_by_role or hypothesis["expert_role"] or "research-lead",
                request_summary,
                json.dumps(required_observations or [], ensure_ascii=False),
                json.dumps(suggested_tasks or [], ensure_ascii=False),
                json.dumps(expected_artifacts or [], ensure_ascii=False),
                risk_level,
                approval_mode,
                now,
                now,
            ),
        )
        conn.execute(
            "UPDATE research_sessions SET updated_at = ? WHERE id = ?",
            (now, hypothesis["research_session_id"]),
        )
        row = conn.execute("SELECT * FROM experiment_requests WHERE id = ?", (experiment_id,)).fetchone()
        conn.commit()
    item = dict(row)
    item["required_observations_json"] = _json_load(item["required_observations_json"], [])
    item["suggested_tasks_json"] = _json_load(item["suggested_tasks_json"], [])
    item["expected_artifacts_json"] = _json_load(item["expected_artifacts_json"], [])
    return item


def approve_experiment_request(
    experiment_request_id: str,
    approved_by: str = "commander",
) -> dict | None:
    now = now_iso()
    with get_connection() as conn:
        existing = conn.execute(
            "SELECT id, research_session_id, status FROM experiment_requests WHERE id = ?",
            (experiment_request_id,),
        ).fetchone()
        if not existing:
            return None
        if existing["status"] not in {"pending_review", "approved"}:
            raise ValueError(f"cannot approve experiment from status {existing['status']}")
        conn.execute(
            """
            UPDATE experiment_requests
            SET status = 'approved',
                approved_by = ?,
                approved_at = COALESCE(approved_at, ?),
                updated_at = ?
            WHERE id = ?
            """,
            (approved_by, now, now, experiment_request_id),
        )
        conn.execute(
            "UPDATE research_sessions SET updated_at = ? WHERE id = ?",
            (now, existing["research_session_id"]),
        )
        row = conn.execute("SELECT * FROM experiment_requests WHERE id = ?", (experiment_request_id,)).fetchone()
        conn.commit()
    return _hydrate_experiment_request(row)


def launch_experiment_request(
    experiment_request_id: str,
    execution_profile: str = "steady",
) -> dict:
    now = now_iso()
    with get_connection() as conn:
        experiment = conn.execute(
            """
            SELECT
                er.*,
                rs.mission_session_id,
                rs.plan_revision_id
            FROM experiment_requests er
            JOIN research_sessions rs ON rs.id = er.research_session_id
            WHERE er.id = ?
            """,
            (experiment_request_id,),
        ).fetchone()
        if not experiment:
            raise ValueError("experiment request not found")
        if experiment["status"] == "launched" and experiment["workflow_id"]:
            existing_result = conn.execute(
                "SELECT * FROM experiment_results WHERE experiment_request_id = ?",
                (experiment_request_id,),
            ).fetchone()
            return {
                "experiment_request": _hydrate_experiment_request(experiment),
                "experiment_result": _hydrate_experiment_result(existing_result) if existing_result else None,
            }
        if experiment["status"] != "approved":
            raise ValueError("experiment request must be approved before launch")
        suggested_tasks = _json_load(experiment["suggested_tasks_json"], [])
        if not suggested_tasks:
            raise ValueError("experiment request has no suggested tasks")

        workflow_id = _new_id("wf")
        published_task_ids: list[str] = []
        for task in suggested_tasks:
            task_params = dict(task.get("params") or {})
            task_params.setdefault("workflowId", workflow_id)
            task_params.setdefault("researchSessionId", experiment["research_session_id"])
            task_params.setdefault("experimentRequestId", experiment_request_id)
            if experiment["plan_revision_id"]:
                task_params.setdefault("planRevisionId", experiment["plan_revision_id"])
            if task.get("notes"):
                task_params.setdefault("notes", task["notes"])
            task_id = publish_event(
                event_type=task.get("type", "task"),
                task=task.get("task") or task.get("operation") or "research-experiment",
                params=task_params,
                agent=task.get("agent", "offense"),
                category=task.get("category") or task.get("capability"),
                execution_profile=execution_profile,
                secondary_confirmation=bool(task_params.get("secondaryConfirmation", False)),
                interactive=bool(task_params.get("interactive", False)),
            )
            published_task_ids.append(task_id)
            conn.execute(
                """
                UPDATE tasks
                SET workflow_id = ?,
                    correlation_id = ?
                WHERE id = ?
                """,
                (workflow_id, workflow_id, task_id),
            )

        conn.execute(
            """
            UPDATE experiment_requests
            SET status = 'launched',
                workflow_id = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (workflow_id, now, experiment_request_id),
        )
        conn.execute(
            """
            INSERT INTO experiment_results (
                id, experiment_request_id, workflow_id, task_ids_json, result_summary,
                structured_observations_json, artifact_refs_json, confidence_delta, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, '{}', '[]', 0, ?, ?)
            ON CONFLICT(experiment_request_id) DO UPDATE SET
                workflow_id = excluded.workflow_id,
                task_ids_json = excluded.task_ids_json,
                result_summary = excluded.result_summary,
                updated_at = excluded.updated_at
            """,
            (
                _new_id("expr"),
                experiment_request_id,
                workflow_id,
                json.dumps(published_task_ids, ensure_ascii=False),
                f"launched {len(published_task_ids)} experiment tasks",
                now,
                now,
            ),
        )
        conn.execute(
            """
            UPDATE mission_sessions
            SET latest_workflow_id = ?, updated_at = ?
            WHERE id = ?
            """,
            (workflow_id, now, experiment["mission_session_id"]),
        )
        conn.execute(
            "UPDATE research_sessions SET updated_at = ? WHERE id = ?",
            (now, experiment["research_session_id"]),
        )
        experiment_row = conn.execute("SELECT * FROM experiment_requests WHERE id = ?", (experiment_request_id,)).fetchone()
        result_row = conn.execute("SELECT * FROM experiment_results WHERE experiment_request_id = ?", (experiment_request_id,)).fetchone()
        conn.commit()
    return {
        "experiment_request": _hydrate_experiment_request(experiment_row),
        "experiment_result": _hydrate_experiment_result(result_row) if result_row else None,
    }


def _hydrate_hypothesis(row) -> dict:
    item = dict(row)
    item["assumptions_json"] = _json_load(item["assumptions_json"], [])
    item["applicability_conditions_json"] = _json_load(item["applicability_conditions_json"], [])
    item["skeptic_notes_json"] = _json_load(item["skeptic_notes_json"], [])
    return item


def _hydrate_experiment_request(row) -> dict:
    item = dict(row)
    item["required_observations_json"] = _json_load(item["required_observations_json"], [])
    item["suggested_tasks_json"] = _json_load(item["suggested_tasks_json"], [])
    item["expected_artifacts_json"] = _json_load(item["expected_artifacts_json"], [])
    return item


def _hydrate_experiment_result(row) -> dict:
    item = dict(row)
    item["task_ids_json"] = _json_load(item["task_ids_json"], [])
    item["structured_observations_json"] = _json_load(item["structured_observations_json"], {})
    item["artifact_refs_json"] = _json_load(item["artifact_refs_json"], [])
    return item


def get_experiment_request_detail(experiment_request_id: str) -> dict | None:
    with get_connection() as conn:
        experiment = conn.execute(
            """
            SELECT
                er.*,
                h.title AS hypothesis_title,
                h.expert_role,
                rq.question_text
            FROM experiment_requests er
            JOIN hypotheses h ON h.id = er.hypothesis_id
            JOIN research_questions rq ON rq.id = h.research_question_id
            WHERE er.id = ?
            """,
            (experiment_request_id,),
        ).fetchone()
        if not experiment:
            return None
        result = conn.execute(
            "SELECT * FROM experiment_results WHERE experiment_request_id = ?",
            (experiment_request_id,),
        ).fetchone()
    return {
        "experiment_request": _hydrate_experiment_request(experiment),
        "experiment_result": _hydrate_experiment_result(result) if result else None,
    }


def get_research_session_detail(research_session_id: str) -> dict | None:
    with get_connection() as conn:
        session = conn.execute(
            """
            SELECT
                rs.*,
                ms.title AS mission_title,
                ms.objective_text
            FROM research_sessions rs
            JOIN mission_sessions ms ON ms.id = rs.mission_session_id
            WHERE rs.id = ?
            """,
            (research_session_id,),
        ).fetchone()
        if not session:
            return None
        questions = conn.execute(
            """
            SELECT *
            FROM research_questions
            WHERE research_session_id = ?
            ORDER BY priority DESC, created_at ASC
            """,
            (research_session_id,),
        ).fetchall()
        hypotheses = conn.execute(
            """
            SELECT
                h.*,
                rq.question_text,
                rq.research_session_id
            FROM hypotheses h
            JOIN research_questions rq ON rq.id = h.research_question_id
            WHERE rq.research_session_id = ?
            ORDER BY h.created_at DESC
            """,
            (research_session_id,),
        ).fetchall()
        experiments = conn.execute(
            """
            SELECT
                er.*,
                h.title AS hypothesis_title,
                h.expert_role,
                rq.question_text
            FROM experiment_requests er
            JOIN hypotheses h ON h.id = er.hypothesis_id
            JOIN research_questions rq ON rq.id = h.research_question_id
            WHERE er.research_session_id = ?
            ORDER BY er.created_at DESC
            """,
            (research_session_id,),
        ).fetchall()
        experiment_results = conn.execute(
            """
            SELECT
                xr.*,
                er.hypothesis_id,
                er.request_summary
            FROM experiment_results xr
            JOIN experiment_requests er ON er.id = xr.experiment_request_id
            WHERE er.research_session_id = ?
            ORDER BY xr.created_at DESC
            """,
            (research_session_id,),
        ).fetchall()
        packages = conn.execute(
            """
            SELECT *
            FROM analysis_packages
            WHERE research_session_id = ?
            ORDER BY updated_at DESC
            """,
            (research_session_id,),
        ).fetchall()

    question_items = []
    for row in questions:
        item = dict(row)
        item["assigned_experts_json"] = _json_load(item["assigned_experts_json"], [])
        question_items.append(item)

    package_items = []
    for row in packages:
        item = dict(row)
        item["hypotheses_json"] = _json_load(item["hypotheses_json"], [])
        item["options_json"] = _json_load(item["options_json"], [])
        item["warnings_json"] = _json_load(item["warnings_json"], [])
        item["evidence_refs_json"] = _json_load(item["evidence_refs_json"], [])
        item["proposed_revision_json"] = _json_load(item["proposed_revision_json"], {})
        item["proposed_experiments_json"] = _json_load(item["proposed_experiments_json"], [])
        package_items.append(item)

    return {
        "research_session": dict(session),
        "questions": question_items,
        "hypotheses": [_hydrate_hypothesis(row) for row in hypotheses],
        "experiments": [_hydrate_experiment_request(row) for row in experiments],
        "experiment_results": [_hydrate_experiment_result(row) for row in experiment_results],
        "analysis_packages": package_items,
    }


def build_research_context(research_session_id: str) -> dict | None:
    detail = get_research_session_detail(research_session_id)
    if not detail:
        return None
    session = detail["research_session"]
    mission_detail = get_mission(session["mission_session_id"])
    workflow_detail = get_workflow_detail(session["workflow_id"]) if session.get("workflow_id") else None
    revision = None
    capabilities: set[str] = set()
    if mission_detail and session.get("plan_revision_id"):
        for candidate in mission_detail.get("revisions", []):
            if candidate.get("id") == session["plan_revision_id"]:
                revision = candidate
                for task in candidate.get("task_tree_json", []):
                    capability = task.get("category") or task.get("capability")
                    if capability:
                        capabilities.add(capability)
                break
    if workflow_detail:
        for task in workflow_detail.get("tasks", []):
            capability = task.get("capability")
            if capability:
                capabilities.add(capability)
    return {
        "research_session": session,
        "mission": mission_detail["mission"] if mission_detail else None,
        "selected_revision": revision,
        "workflow": workflow_detail["workflow"] if workflow_detail else None,
        "capabilities": sorted(capabilities),
        "question_count": len(detail.get("questions", [])),
        "hypothesis_count": len(detail.get("hypotheses", [])),
        "experiment_count": len(detail.get("experiments", [])),
    }
