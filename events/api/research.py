#!/usr/bin/env python3
from __future__ import annotations

from services.control import (
    approve_experiment_request,
    build_research_context,
    create_experiment_request,
    create_hypothesis,
    create_research_question,
    create_research_session,
    get_experiment_request_detail,
    get_research_session_detail,
    launch_experiment_request,
    list_research_sessions,
    review_hypothesis,
)


def list_items(limit: int = 20) -> list[dict]:
    return list_research_sessions(limit=limit)


def create_item(payload: dict) -> dict:
    return create_research_session(
        mission_session_id=payload["mission_session_id"],
        plan_revision_id=payload.get("plan_revision_id"),
        workflow_id=payload.get("workflow_id"),
        session_goal=payload.get("session_goal") or payload.get("goal") or "",
        scope_summary=payload.get("scope_summary", ""),
        created_by=payload.get("created_by", "operator"),
    )


def get_item(session_id: str) -> dict | None:
    return get_research_session_detail(session_id)


def get_context(session_id: str) -> dict | None:
    return build_research_context(session_id)


def create_question_item(session_id: str, payload: dict) -> dict:
    return create_research_question(
        research_session_id=session_id,
        question_text=payload.get("question_text") or payload.get("text") or "",
        priority=int(payload.get("priority", 50)),
        assigned_experts=payload.get("assigned_experts_json") or payload.get("assigned_experts") or [],
    )


def create_hypothesis_item(question_id: str, payload: dict) -> dict:
    return create_hypothesis(
        research_question_id=question_id,
        expert_role=payload.get("expert_role") or "research-lead",
        title=payload.get("title") or "Untitled hypothesis",
        summary=payload.get("summary", ""),
        assumptions=payload.get("assumptions_json") or payload.get("assumptions") or [],
        applicability_conditions=payload.get("applicability_conditions_json") or payload.get("applicability_conditions") or [],
        confidence_before=float(payload.get("confidence_before", 0.5)),
    )


def review_hypothesis_item(hypothesis_id: str, payload: dict) -> dict | None:
    return review_hypothesis(
        hypothesis_id=hypothesis_id,
        skeptic_review_status=payload.get("skeptic_review_status") or payload.get("status") or "reviewed",
        skeptic_notes=payload.get("skeptic_notes_json") or payload.get("skeptic_notes") or [],
    )


def create_experiment_item(hypothesis_id: str, payload: dict) -> dict:
    return create_experiment_request(
        hypothesis_id=hypothesis_id,
        requested_by_role=payload.get("requested_by_role") or payload.get("expert_role") or "research-lead",
        request_summary=payload.get("request_summary") or payload.get("summary") or "",
        required_observations=payload.get("required_observations_json") or payload.get("required_observations") or [],
        suggested_tasks=payload.get("suggested_tasks_json") or payload.get("suggested_tasks") or [],
        expected_artifacts=payload.get("expected_artifacts_json") or payload.get("expected_artifacts") or [],
        risk_level=payload.get("risk_level", "medium"),
        approval_mode=payload.get("approval_mode", "commander_review"),
    )


def get_experiment_item(experiment_id: str) -> dict | None:
    return get_experiment_request_detail(experiment_id)


def approve_experiment_item(experiment_id: str, payload: dict) -> dict | None:
    return approve_experiment_request(
        experiment_request_id=experiment_id,
        approved_by=payload.get("approved_by", "commander"),
    )


def launch_experiment_item(experiment_id: str, payload: dict) -> dict:
    return launch_experiment_request(
        experiment_request_id=experiment_id,
        execution_profile=payload.get("execution_profile", "steady"),
    )
