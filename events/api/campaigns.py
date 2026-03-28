#!/usr/bin/env python3
from __future__ import annotations

from services.control import (
    control_campaign,
    create_approval_scope,
    create_campaign,
    get_campaign_detail,
    get_campaign_events,
    list_campaigns,
)


def create_scope(mission_id: str, payload: dict) -> dict:
    return create_approval_scope(
        mission_session_id=mission_id,
        scope_name=payload.get("scope_name") or "default-scope",
        allowed_categories=payload.get("allowed_categories_json") or payload.get("allowed_categories") or [],
        allowed_tools=payload.get("allowed_tools_json") or payload.get("allowed_tools") or [],
        interactive_tools=payload.get("interactive_tools_json") or payload.get("interactive_tools") or [],
        high_risk_tools=payload.get("high_risk_tools_json") or payload.get("high_risk_tools") or [],
        denied_tools=payload.get("denied_tools_json") or payload.get("denied_tools") or [],
        network_scope=payload.get("network_scope_json") or payload.get("network_scope") or {},
        confirmed_by=payload.get("confirmed_by", "operator"),
    )


def create_item(payload: dict) -> dict:
    return create_campaign(
        mission_session_id=payload["mission_session_id"],
        plan_revision_id=payload["plan_revision_id"],
        approval_scope_id=payload["approval_scope_id"],
        execution_profile=payload.get("execution_profile", "steady"),
        max_parallelism=int(payload.get("max_parallelism", 1)),
        auto_replan_enabled=bool(payload.get("auto_replan_enabled", True)),
    )


def control_item(campaign_id: str, payload: dict) -> dict | None:
    return control_campaign(campaign_id, payload["action"])


def list_events(campaign_id: str, limit: int = 50) -> list[dict]:
    return get_campaign_events(campaign_id, limit=limit)


def list_items(limit: int = 20) -> list[dict]:
    return list_campaigns(limit=limit)


def get_item(campaign_id: str) -> dict | None:
    return get_campaign_detail(campaign_id)
