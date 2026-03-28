#!/usr/bin/env python3
from __future__ import annotations

from services.control import (
    create_branch_revision,
    create_plan_candidate,
    create_plan_revision,
    launch_plan_revision,
)


def create_candidate(mission_id: str, payload: dict) -> dict:
    return create_plan_candidate(
        mission_id=mission_id,
        title=payload.get("title") or "未命名方案",
        goal_summary=payload.get("goal_summary", ""),
        discussion_summary=payload.get("discussion_summary", ""),
        assumptions=payload.get("assumptions_json") or payload.get("assumptions") or [],
        warnings=payload.get("warnings_json") or payload.get("warnings") or [],
        evidence_refs=payload.get("evidence_refs_json") or payload.get("evidence_refs") or [],
        source_message_id=payload.get("source_message_id"),
    )


def create_revision(plan_id: str, payload: dict) -> dict:
    plan_outline = (
        payload["plan_outline_json"]
        if "plan_outline_json" in payload
        else payload["plan_outline"]
        if "plan_outline" in payload
        else None
    )
    task_tree = (
        payload["task_tree_json"]
        if "task_tree_json" in payload
        else payload["task_tree"]
        if "task_tree" in payload
        else None
    )
    branch_key = payload["branch_key"] if "branch_key" in payload else None
    launchable = payload["launchable"] if "launchable" in payload else False
    return create_plan_revision(
        plan_id=plan_id,
        change_summary=payload.get("change_summary", ""),
        plan_outline=plan_outline,
        task_tree=task_tree,
        branch_key=branch_key,
        launchable=bool(launchable),
        parent_revision_id=payload.get("parent_revision_id"),
        created_by=payload.get("created_by", "commander"),
    )


def launch_revision(revision_id: str, payload: dict) -> dict:
    return launch_plan_revision(
        revision_id,
        launch_mode=payload.get("launch_mode", "assisted"),
        execution_profile=payload.get("execution_profile", "steady"),
        selected_tools=payload.get("selected_tools_json") or payload.get("selected_tools") or [],
    )


def branch_revision(revision_id: str, payload: dict) -> dict:
    return create_branch_revision(
        revision_id=revision_id,
        branch_key=payload.get("branch_key", ""),
        change_summary=payload.get("change_summary", ""),
    )
