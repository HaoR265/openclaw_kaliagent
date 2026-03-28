#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess

from services.control import (
    add_discussion_message,
    create_analysis_job,
    create_mission,
    create_plan_candidate,
    create_plan_revision,
    get_mission,
    list_missions,
    update_analysis_job,
)


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def _build_analysis_prompt(text: str) -> str:
    return f"""
你是 OpenClaw 的 analyst。目标是把输入的情报、方向或阶段目标，整理成候选方案和可执行任务。

输出必须是严格 JSON，不要输出 Markdown，不要输出额外解释。

JSON 结构：
{{
  "summary": "一句话总结",
  "discussion": ["技术判断、路径取舍、关键提醒"],
  "assumptions": ["..."],
  "warnings": ["..."],
  "options": [
    {{
      "title": "方案名称",
      "goal_summary": "方案目标",
      "discussion_summary": "方案讨论摘要",
      "assumptions": ["..."],
      "warnings": ["..."],
      "tasks": [
        {{
          "category": "wireless|recon|web|internal|exploit|social",
          "task": "kebab-case 任务名",
          "notes": "简短说明"
        }}
      ]
    }}
  ]
}}

要求：
1. 给 2 到 4 个候选方案。
2. 每个方案给 2 到 6 个可执行任务。
3. 不要给 steady/rush 建议。
4. 输入若偏讨论，也必须给出可执行路径。

输入：
{text}
""".strip()


def _parse_agent_response(output: str) -> dict:
    text = output.strip()
    if not text:
        raise ValueError("empty analyst response")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError("analyst response is not valid JSON")
        parsed = json.loads(text[start : end + 1])

    if isinstance(parsed, dict) and isinstance(parsed.get("payloads"), list):
        joined = "".join(block.get("text", "") for block in parsed["payloads"] if isinstance(block, dict))
        return _parse_agent_response(joined)
    if isinstance(parsed, dict) and isinstance(parsed.get("content"), list):
        joined = "".join(block.get("text", "") for block in parsed["content"] if isinstance(block, dict))
        return _parse_agent_response(joined)
    if isinstance(parsed, dict) and isinstance(parsed.get("assistant_response"), str):
        return _parse_agent_response(parsed["assistant_response"])
    if isinstance(parsed, dict) and isinstance(parsed.get("output_text"), str):
        return _parse_agent_response(parsed["output_text"])
    return parsed


def _run_analyst(text: str) -> dict:
    if not os.environ.get("DEEPSEEK_API_KEY_COMMAND"):
        raise RuntimeError("DEEPSEEK_API_KEY_COMMAND is not set")
    command = [
        "openclaw",
        "agent",
        "--local",
        "--agent",
        "command",
        "--json",
        "--message",
        _build_analysis_prompt(text),
    ]
    completed = subprocess.run(
        command,
        cwd=ROOT,
        env=os.environ.copy(),
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    output = completed.stdout or completed.stderr or ""
    if completed.returncode != 0:
        raise RuntimeError(output.strip() or "analyst execution failed")
    data = _parse_agent_response(output)
    if not isinstance(data, dict):
        raise ValueError("analyst did not return an object")
    data.setdefault("summary", "")
    data.setdefault("discussion", [])
    data.setdefault("assumptions", [])
    data.setdefault("warnings", [])
    data.setdefault("options", [])
    return data


def list_items(limit: int = 30) -> list[dict]:
    return list_missions(limit=limit)


def create_item(payload: dict) -> dict:
    return create_mission(
        title=payload.get("title") or "未命名 Mission",
        objective_text=payload.get("objective_text") or payload.get("text") or "",
        context_text=payload.get("context_text", ""),
        priority=payload.get("priority", "medium"),
        created_by=payload.get("created_by", "operator"),
    )


def get_item(mission_id: str) -> dict | None:
    return get_mission(mission_id)


def add_discussion(mission_id: str, payload: dict) -> dict:
    message = add_discussion_message(
        mission_id=mission_id,
        content_text=payload.get("content_text") or payload.get("text") or "",
        role=payload.get("role", "user"),
        author_type=payload.get("author_type", "operator"),
        author_id=payload.get("author_id", "local"),
        message_kind=payload.get("message_kind", "input"),
    )
    analysis_job = None
    if payload.get("run_analyst"):
        analysis_job = create_analysis_job(
            mission_id=mission_id,
            trigger_message_id=message["id"],
            query_text=message["content_text"],
        )
    return {"message": message, "analysis_job": analysis_job}


def analyze_item(mission_id: str, payload: dict) -> dict:
    text = payload.get("text") or payload.get("query_text") or ""
    if not text:
        mission = get_mission(mission_id)
        if not mission:
            raise ValueError("mission not found")
        text = mission["mission"]["objective_text"]

    analysis_job = create_analysis_job(
        mission_id=mission_id,
        query_text=text,
        trigger_message_id=payload.get("trigger_message_id"),
        status="queued",
    )
    update_analysis_job(analysis_job["id"], status="running")
    try:
        result = _run_analyst(text)
        completed_job = update_analysis_job(
            analysis_job["id"],
            status="completed",
            output_summary=result.get("summary", ""),
            evidence_refs=[],
            warning_refs=result.get("warnings", []),
        )
    except Exception as exc:
        failed_job = update_analysis_job(
            analysis_job["id"],
            status="failed",
            error_text=str(exc),
        )
        raise RuntimeError(failed_job["error_text"] if failed_job else str(exc))

    created_plans = []
    for option in result.get("options", []):
        plan = create_plan_candidate(
            mission_id=mission_id,
            title=option.get("title") or "候选方案",
            goal_summary=option.get("goal_summary") or option.get("goalSummary") or "",
            discussion_summary=option.get("discussion_summary") or option.get("discussionSummary") or "",
            assumptions=option.get("assumptions") or result.get("assumptions") or [],
            warnings=option.get("warnings") or result.get("warnings") or [],
            evidence_refs=[],
            source_message_id=payload.get("trigger_message_id"),
        )
        create_plan_revision(
            plan_id=plan["id"],
            change_summary="auto-generated initial revision",
            plan_outline={
                "summary": option.get("discussion_summary") or option.get("discussionSummary") or "",
                "discussion": option.get("discussion") or "",
            },
            task_tree=option.get("tasks") or [],
            branch_key="main",
            launchable=True,
        )
        created_plans.append(plan)

    return {
        "analysis_job": completed_job,
        "analysis_result": result,
        "created_plans": created_plans,
    }
