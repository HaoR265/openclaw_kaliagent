#!/usr/bin/env python3
from __future__ import annotations

import json
import mimetypes
import os
import shutil
import subprocess
import time
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

DEFAULT_ROOT = Path(__file__).resolve().parents[1]
ROOT = Path(os.environ.get("KALICLAW_ROOT", str(DEFAULT_ROOT))).expanduser()
COMMON_BIN_DIR = ROOT / "agent-kits" / "common" / "bin"


def _resolve_cli_bin() -> str:
    configured = os.environ.get("KALICLAW_CLI_BIN")
    candidates = [configured] if configured else [
        "kaliclaw",
        str(ROOT / "kaliclaw"),
        str(COMMON_BIN_DIR / "kaliclaw"),
        "openclaw",
    ]
    for candidate in candidates:
        if not candidate:
            continue
        if os.sep in candidate:
            expanded = Path(candidate).expanduser()
            if expanded.exists():
                return str(expanded)
            continue
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    return candidates[0]


CLI_BIN = _resolve_cli_bin()
EVENTS_DIR = ROOT / "events"
DASHBOARD_DIR = ROOT / "dashboard"
DASHBOARD_UI_DIST_DIR = ROOT / "dashboard-ui" / "dist"

import sys

sys.path.insert(0, str(EVENTS_DIR))

from db import get_connection, fetch_task_stats  # noqa: E402
from publish import publish_event  # noqa: E402
from api import campaigns as campaigns_api  # noqa: E402
from api import missions as missions_api  # noqa: E402
from api import plans as plans_api  # noqa: E402
from api import research as research_api  # noqa: E402
from knowledge.search import search_intel as knowledge_search_intel  # noqa: E402
from knowledge.search import search_knowledge as knowledge_search_knowledge  # noqa: E402
from services.control import get_artifact_detail, get_workflow_detail, list_workflows  # noqa: E402


def _static_dir() -> Path:
    return DASHBOARD_UI_DIST_DIR if DASHBOARD_UI_DIST_DIR.exists() else DASHBOARD_DIR


def _should_serve_spa_index(request_path: str) -> bool:
    static_dir = _static_dir()
    if static_dir != DASHBOARD_UI_DIST_DIR:
        return request_path == "/"
    if request_path == "/":
        return True
    relative = request_path.lstrip("/")
    if not relative or Path(relative).suffix:
        return False
    return not (static_dir / relative).exists()


def _count_jsonl_lines(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def get_overview() -> dict:
    stats = fetch_task_stats()
    results_count = _count_jsonl_lines(EVENTS_DIR / "results.jsonl")
    dead_letter_count = _count_jsonl_lines(EVENTS_DIR / "dead-letter.jsonl")

    with get_connection() as conn:
        recent_tasks = [
            dict(row)
            for row in conn.execute(
                """
                SELECT id, capability, operation, state, priority, created_at, completed_at
                FROM tasks
                ORDER BY created_at DESC
                LIMIT 8
                """
            ).fetchall()
        ]
        workers = [
            dict(row)
            for row in conn.execute(
                """
                SELECT id, agent_id, capabilities_json, last_heartbeat_at, status
                FROM workers
                ORDER BY last_heartbeat_at DESC
                LIMIT 12
                """
            ).fetchall()
        ]

    category_logs = []
    for category in ["wireless", "recon", "web", "internal", "exploit", "social"]:
        log_file = EVENTS_DIR / f"{category}.log"
        category_logs.append(
            {
                "category": category,
                "updated_at": log_file.stat().st_mtime if log_file.exists() else None,
                "exists": log_file.exists(),
            }
        )

    return {
        "stats": stats,
        "results_count": results_count,
        "dead_letter_count": dead_letter_count,
        "recent_tasks": recent_tasks,
        "workers": workers,
        "logs": category_logs,
        "profiles": ["steady", "rush"],
        "capabilities": ["wireless", "recon", "web", "internal", "exploit", "social"],
    }


def get_capability_agent(capability: str) -> str:
    if capability in {"wireless", "recon", "web", "internal", "exploit", "social"}:
        return f"offense-{capability}"
    return "command"


def get_recent_tasks(limit: int = 20) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                t.id,
                t.capability,
                t.operation,
                t.state,
                t.priority,
                t.payload_json,
                t.created_at,
                t.completed_at,
                r.status AS result_status,
                r.summary_json,
                a.executor_type,
                a.tool_name
            FROM tasks t
            LEFT JOIN results r ON r.task_id = t.id
            LEFT JOIN task_attempts a
              ON a.task_id = t.id
             AND a.started_at = (
                 SELECT MAX(a2.started_at)
                 FROM task_attempts a2
                 WHERE a2.task_id = t.id
             )
            ORDER BY t.created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    results = []
    for row in rows:
        payload = json.loads(row["payload_json"])
        summary = json.loads(row["summary_json"]) if row["summary_json"] else {}
        results.append(
            {
                "id": row["id"],
                "capability": row["capability"],
                "agent_id": get_capability_agent(row["capability"]),
                "operation": row["operation"],
                "state": row["state"],
                "priority": row["priority"],
                "created_at": row["created_at"],
                "completed_at": row["completed_at"],
                "params": payload.get("params", {}),
                "execution_mode": payload.get("params", {}).get("executionMode", "agent_api"),
                "profile": payload.get("params", {}).get("executionProfile", "steady"),
                "interactive": bool(payload.get("params", {}).get("interactive", False)),
                "secondary_confirmation": bool(payload.get("params", {}).get("secondaryConfirmation", False)),
                "result_status": row["result_status"],
                "summary": summary,
                "executor_type": row["executor_type"],
                "tool_name": row["tool_name"],
            }
        )
    return results


def get_recent_results(limit: int = 20) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                r.task_id,
                r.status,
                r.summary_json,
                r.structured_json,
                r.created_at,
                t.capability,
                t.operation
            FROM results r
            JOIN tasks t ON t.id = r.task_id
            ORDER BY r.created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    items = []
    for row in rows:
        items.append(
            {
                "task_id": row["task_id"],
                "status": row["status"],
                "summary": json.loads(row["summary_json"]),
                "structured": json.loads(row["structured_json"]),
                "created_at": row["created_at"],
                "capability": row["capability"],
                "operation": row["operation"],
            }
        )
    return items


def get_catalog(profile: str = "steady") -> list[dict]:
    catalog_paths = [
        ROOT / "agent-kits" / "offense-kit" / "catalog" / "front-tools.json",
        ROOT / "agent-kits" / "defense-kit" / "catalog" / "front-tools.json",
        ROOT / "agent-kits" / "cmd-special" / "catalog" / "rare-tools.json",
    ]
    items = []
    for path in catalog_paths:
        data = _load_json(path)
        for item in data.get("items", []):
            if profile == "steady" and (item.get("interactive") or item.get("risk_level") == "high"):
                continue
            item = dict(item)
            item["catalog"] = data.get("catalog")
            items.append(item)
    return items


def get_recipes() -> list[dict]:
    recipes_dir = ROOT / "agent-kits" / "recipes"
    recipes = []
    for path in sorted(recipes_dir.glob("*.json")):
        recipes.append(_load_json(path))
    return recipes


def get_agent_workbench() -> list[dict]:
    capabilities = ["wireless", "recon", "web", "internal", "exploit", "social"]
    items = []
    with get_connection() as conn:
        for capability in capabilities:
            worker = conn.execute(
                """
                SELECT agent_id, id, last_heartbeat_at, status
                FROM workers
                WHERE agent_id = ?
                ORDER BY last_heartbeat_at DESC
                LIMIT 1
                """,
                (get_capability_agent(capability),),
            ).fetchone()
            rows = conn.execute(
                """
                SELECT id, operation, state, created_at, completed_at
                FROM tasks
                WHERE capability = ?
                ORDER BY created_at DESC
                LIMIT 5
                """,
                (capability,),
            ).fetchall()
            counts = conn.execute(
                """
                SELECT state, COUNT(*) AS count
                FROM tasks
                WHERE capability = ?
                GROUP BY state
                """,
                (capability,),
            ).fetchall()
            items.append(
                {
                    "capability": capability,
                    "agent_id": get_capability_agent(capability),
                    "worker": dict(worker) if worker else None,
                    "state_counts": {row["state"]: row["count"] for row in counts},
                    "recent_tasks": [dict(row) for row in rows],
                }
            )
    return items


def get_command_board_insights(mission_id: str) -> dict:
    mission = missions_api.get_item(mission_id)
    if not mission:
        raise ValueError("mission not found")

    capabilities = set()
    for revision in mission.get("revisions", []):
        for task in revision.get("task_tree_json", []):
            capability = task.get("category") or task.get("capability")
            if capability:
                capabilities.add(capability)

    recipes = [
        recipe
        for recipe in get_recipes()
        if not capabilities or recipe.get("capability") in capabilities
    ][:6]
    recent_results = [
        item
        for item in get_recent_results(limit=20)
        if not capabilities or item.get("capability") in capabilities
    ][:6]

    knowledge_cards = [
        {
            "kind": "recipe",
            "title": recipe.get("operation"),
            "summary": recipe.get("summary") or recipe.get("tool_bin") or "",
            "capability": recipe.get("capability"),
            "tool": recipe.get("tool_bin"),
        }
        for recipe in recipes
    ]
    intel_cards = [
        {
            "kind": "result",
            "title": item.get("operation"),
            "summary": (item.get("summary") or {}).get("message") or "recent execution result",
            "capability": item.get("capability"),
            "status": item.get("status"),
        }
        for item in recent_results
    ]
    risk_cards = []
    for job in mission.get("analysis_jobs", [])[:5]:
        for warning in job.get("warning_refs_json", []):
            risk_cards.append({"kind": "analysis-warning", "title": "Analyst Warning", "summary": warning})
    for campaign in mission.get("campaigns", [])[:3]:
        risk_cards.append(
            {
                "kind": "campaign-status",
                "title": campaign.get("id"),
                "summary": f"{campaign.get('status')} / {campaign.get('execution_profile')} / parallel {campaign.get('max_parallelism')}",
            }
        )

    current_plan = mission.get("plans", [None])[0]
    current_revision = mission.get("revisions", [None])[0]
    current_campaign = mission.get("campaigns", [None])[0]
    current_workflow = None
    if mission["mission"].get("latest_workflow_id"):
        current_workflow = get_workflow_detail(mission["mission"]["latest_workflow_id"])

    failure_cards = []
    if current_workflow:
        for task in current_workflow.get("tasks", []):
            if task.get("state") in {"failed", "dead_letter"} or task.get("last_error_message"):
                failure_cards.append(
                    {
                        "task_id": task.get("id"),
                        "title": task.get("operation"),
                        "capability": task.get("capability"),
                        "summary": task.get("last_error_message") or task.get("result_status") or task.get("state"),
                    }
                )
    runtime_cards = []
    if current_workflow:
        for task in current_workflow.get("tasks", [])[:8]:
            if not (task.get("result_status") or task.get("summary_json")):
                continue
            runtime_cards.append(
                {
                    "task_id": task.get("id"),
                    "title": task.get("operation"),
                    "capability": task.get("capability"),
                    "status": task.get("state"),
                    "summary": (task.get("summary_json") or {}).get("message")
                    or (task.get("summary_json") or {}).get("summary")
                    or task.get("result_status")
                    or "runtime result",
                }
            )

    return {
        "mission_id": mission_id,
        "capabilities": sorted(capabilities),
        "current_plan": {
            "title": current_plan.get("title"),
            "goal_summary": current_plan.get("goal_summary"),
            "discussion_summary": current_plan.get("discussion_summary"),
        } if current_plan else None,
        "current_revision": {
            "id": current_revision.get("id"),
            "revision_no": current_revision.get("revision_no"),
            "branch_key": current_revision.get("branch_key"),
            "change_summary": current_revision.get("change_summary"),
            "launchable": current_revision.get("launchable"),
            "task_count": len(current_revision.get("task_tree_json", [])),
        } if current_revision else None,
        "current_workflow": {
            "id": current_workflow["workflow"]["workflow_id"],
            "launch_mode": current_workflow["workflow"]["launch_mode"],
            "execution_profile": current_workflow["workflow"]["execution_profile"],
            "task_count": len(current_workflow.get("tasks", [])),
            "artifact_count": len(current_workflow.get("artifacts", [])),
        } if current_workflow else None,
        "current_campaign": {
            "id": current_campaign.get("id"),
            "status": current_campaign.get("status"),
            "execution_profile": current_campaign.get("execution_profile"),
            "max_parallelism": current_campaign.get("max_parallelism"),
        } if current_campaign else None,
        "knowledge_cards": knowledge_cards,
        "intel_cards": intel_cards,
        "risk_cards": risk_cards[:8],
        "failure_cards": failure_cards[:6],
        "runtime_cards": runtime_cards[:6],
    }


def build_command_analysis_prompt(text: str, profile: str) -> str:
    return f"""
你是 Kaliclaw 的 command 指挥官。目标是把输入的情报、方向或阶段目标，整理成可执行候选方案。

输出必须是严格 JSON，不要输出 Markdown，不要输出解释性前后文。

JSON 结构：
{{
  "summary": "一句话总结",
  "assumptions": ["..."],
  "discussion": [
    "可选的技术判断、原理说明、风险点、为什么这样拆"
  ],
  "options": [
    {{
      "id": "option-1",
      "title": "方案名称",
      "intent": "方案目的",
      "fit": "适用原因",
      "risk": "low|medium|high",
      "discussion": "该方案的技术思路或取舍",
      "tasks": [
        {{
          "category": "wireless|recon|web|internal|exploit|social",
          "task": "短任务名",
          "type": "task",
          "params": {{}},
          "notes": "简短说明"
        }}
      ]
    }}
  ]
}}

要求：
1. 给 2 到 4 个候选方案。
2. 每个方案给 2 到 6 个可执行任务。
3. task 必须尽量用简短英文 kebab-case，例如 port-scan、service-enum、dir-brute。
4. 如果输入更偏讨论、原理、技术方案，也要先给简短讨论结论，再给可执行路径。
5. 不要替用户决定 steady/rush，不要输出执行模式建议。
6. 如果输入只是情报，也要给出先验证、再扩展的可执行路径。
7. 不要虚构不存在的 capability。
8. 尽量简洁，控制 token，不要长篇解释。

输入情报：
{text}
""".strip()


def parse_command_response(output: str) -> dict:
    text = output.strip()
    if not text:
        raise ValueError("empty response from command agent")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError("command response is not valid JSON")
        parsed = json.loads(text[start : end + 1])

    if isinstance(parsed, dict) and isinstance(parsed.get("content"), list):
        joined = "".join(block.get("text", "") for block in parsed["content"] if isinstance(block, dict))
        return parse_command_response(joined)
    if isinstance(parsed, dict) and isinstance(parsed.get("payloads"), list):
        joined = "".join(block.get("text", "") for block in parsed["payloads"] if isinstance(block, dict))
        return parse_command_response(joined)
    if isinstance(parsed, dict) and isinstance(parsed.get("assistant_response"), str):
        return parse_command_response(parsed["assistant_response"])
    if isinstance(parsed, dict) and isinstance(parsed.get("output_text"), str):
        return parse_command_response(parsed["output_text"])
    return parsed


def analyze_mission(text: str, profile: str) -> dict:
    if not text.strip():
        raise ValueError("mission text is empty")
    if not os.environ.get("DEEPSEEK_API_KEY_COMMAND"):
        raise RuntimeError("DEEPSEEK_API_KEY_COMMAND is not set in dashboard server environment")

    command = [
        CLI_BIN,
        "agent",
        "--local",
        "--agent",
        "command",
        "--json",
        "--message",
        build_command_analysis_prompt(text, profile),
    ]
    env = os.environ.copy()
    completed = subprocess.run(
        command,
        cwd=str(ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    output = completed.stdout or completed.stderr or ""
    if completed.returncode != 0:
        stderr = output.strip()
        raise RuntimeError(stderr or "command agent execution failed")

    data = parse_command_response(output)
    if not isinstance(data, dict):
        raise ValueError("command analysis did not return an object")
    data.setdefault("summary", "未提供摘要")
    data.setdefault("assumptions", [])
    data.setdefault("discussion", [])
    data.setdefault("options", [])
    return data


class DashboardHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(_static_dir()), **kwargs)

    def log_message(self, fmt: str, *args) -> None:
        return

    def _send_json(self, payload: object, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _stream_payload(self, parsed) -> tuple[str, callable] | None:
        query = parse_qs(parsed.query)
        mission_id = query.get("mission_id", [None])[0]
        workflow_id = query.get("workflow_id", [None])[0]
        campaign_id = query.get("campaign_id", [None])[0]
        if mission_id:
            return ("mission.updated", lambda: missions_api.get_item(mission_id))
        if workflow_id:
            return ("workflow.updated", lambda: get_workflow_detail(workflow_id))
        if campaign_id:
            return ("campaign.updated", lambda: campaigns_api.get_item(campaign_id))
        return None

    def _send_sse_stream(self, event_name: str, getter) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()

        last_body = None
        try:
            for _ in range(30):
                payload = getter()
                body = json.dumps(payload, ensure_ascii=False, sort_keys=True)
                if body != last_body:
                    self.wfile.write(f"event: {event_name}\n".encode("utf-8"))
                    self.wfile.write(f"data: {body}\n\n".encode("utf-8"))
                    self.wfile.flush()
                    last_body = body
                else:
                    self.wfile.write(b": heartbeat\n\n")
                    self.wfile.flush()
                time.sleep(2)
        except (BrokenPipeError, ConnectionResetError):
            return

    def _apply_spa_fallback(self, request_path: str) -> None:
        if _should_serve_spa_index(request_path):
            self.path = "/index.html"

    def do_HEAD(self) -> None:
        parsed = urlparse(self.path)
        if not parsed.path.startswith("/api/"):
            self._apply_spa_fallback(parsed.path)
        return super().do_HEAD()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path_parts = [part for part in parsed.path.split("/") if part]
        if parsed.path == "/api/stream":
            stream = self._stream_payload(parsed)
            if not stream:
                self._send_json({"error": "missing stream target"}, status=400)
                return
            event_name, getter = stream
            self._send_sse_stream(event_name, getter)
            return
        if parsed.path == "/api/overview":
            self._send_json(get_overview())
            return
        if parsed.path == "/api/missions":
            limit = int(parse_qs(parsed.query).get("limit", ["30"])[0])
            self._send_json(missions_api.list_items(limit=limit))
            return
        if parsed.path == "/api/intel/search":
            query = parse_qs(parsed.query).get("q", [""])[0]
            capability = parse_qs(parsed.query).get("capability", [None])[0]
            self._send_json(knowledge_search_intel(query=query, capability=capability))
            return
        if parsed.path == "/api/knowledge/search":
            query = parse_qs(parsed.query).get("q", [""])[0]
            capability = parse_qs(parsed.query).get("capability", [None])[0]
            self._send_json(knowledge_search_knowledge(get_recipes(), query=query, capability=capability))
            return
        if len(path_parts) == 4 and path_parts[:2] == ["api", "command-board"] and path_parts[3] == "insights":
            try:
                self._send_json(get_command_board_insights(path_parts[2]))
            except ValueError as exc:
                self._send_json({"error": str(exc)}, status=404)
            return
        if parsed.path == "/api/research/sessions":
            limit = int(parse_qs(parsed.query).get("limit", ["20"])[0])
            self._send_json(research_api.list_items(limit=limit))
            return
        if len(path_parts) == 4 and path_parts[:3] == ["api", "research", "sessions"] and path_parts[3]:
            session = research_api.get_item(path_parts[3])
            if not session:
                self._send_json({"error": "research session not found"}, status=404)
                return
            self._send_json(session)
            return
        if len(path_parts) == 5 and path_parts[:3] == ["api", "research", "sessions"] and path_parts[4] == "context":
            session = research_api.get_context(path_parts[3])
            if not session:
                self._send_json({"error": "research session not found"}, status=404)
                return
            self._send_json(session)
            return
        if len(path_parts) == 4 and path_parts[:3] == ["api", "research", "experiments"] and path_parts[3]:
            item = research_api.get_experiment_item(path_parts[3])
            if not item:
                self._send_json({"error": "experiment request not found"}, status=404)
                return
            self._send_json(item)
            return
        if parsed.path == "/api/campaigns":
            limit = int(parse_qs(parsed.query).get("limit", ["20"])[0])
            self._send_json(campaigns_api.list_items(limit=limit))
            return
        if len(path_parts) == 3 and path_parts[:2] == ["api", "missions"]:
            mission = missions_api.get_item(path_parts[2])
            if not mission:
                self._send_json({"error": "mission not found"}, status=404)
                return
            self._send_json(mission)
            return
        if len(path_parts) == 3 and path_parts[:2] == ["api", "campaigns"]:
            campaign = campaigns_api.get_item(path_parts[2])
            if not campaign:
                self._send_json({"error": "campaign not found"}, status=404)
                return
            self._send_json(campaign)
            return
        if len(path_parts) == 4 and path_parts[:2] == ["api", "campaigns"] and path_parts[3] == "events":
            limit = int(parse_qs(parsed.query).get("limit", ["50"])[0])
            self._send_json(campaigns_api.list_events(path_parts[2], limit=limit))
            return
        if parsed.path == "/api/workflows":
            limit = int(parse_qs(parsed.query).get("limit", ["20"])[0])
            self._send_json(list_workflows(limit=limit))
            return
        if len(path_parts) == 3 and path_parts[:2] == ["api", "workflows"]:
            workflow = get_workflow_detail(path_parts[2])
            if not workflow:
                self._send_json({"error": "workflow not found"}, status=404)
                return
            self._send_json(workflow)
            return
        if len(path_parts) == 3 and path_parts[:2] == ["api", "artifacts"]:
            artifact = get_artifact_detail(path_parts[2])
            if not artifact:
                self._send_json({"error": "artifact not found"}, status=404)
                return
            self._send_json({"artifact": artifact})
            return
        if parsed.path == "/api/tasks":
            limit = int(parse_qs(parsed.query).get("limit", ["20"])[0])
            self._send_json(get_recent_tasks(limit=limit))
            return
        if parsed.path == "/api/results":
            limit = int(parse_qs(parsed.query).get("limit", ["20"])[0])
            self._send_json(get_recent_results(limit=limit))
            return
        if parsed.path == "/api/tools":
            profile = parse_qs(parsed.query).get("profile", ["steady"])[0]
            self._send_json(get_catalog(profile=profile))
            return
        if parsed.path == "/api/recipes":
            self._send_json(get_recipes())
            return
        if parsed.path == "/api/agents":
            self._send_json(get_agent_workbench())
            return
        self._apply_spa_fallback(parsed.path)
        return super().do_GET()

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path_parts = [part for part in parsed.path.split("/") if part]
        length = int(self.headers.get("Content-Length", "0"))
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            self._send_json({"error": "invalid json"}, status=400)
            return

        if parsed.path == "/api/missions":
            objective = payload.get("objective_text") or payload.get("text") or ""
            if not objective:
                self._send_json({"error": "objective_text is required"}, status=400)
                return
            mission = missions_api.create_item(payload)
            self._send_json({"mission": mission}, status=HTTPStatus.CREATED)
            return

        if parsed.path == "/api/research/sessions":
            if not payload.get("mission_session_id"):
                self._send_json({"error": "mission_session_id is required"}, status=400)
                return
            try:
                session = research_api.create_item(payload)
            except ValueError as exc:
                self._send_json({"error": str(exc)}, status=400)
                return
            self._send_json({"research_session": session}, status=HTTPStatus.CREATED)
            return

        if len(path_parts) == 5 and path_parts[:3] == ["api", "research", "sessions"] and path_parts[4] == "questions":
            try:
                question = research_api.create_question_item(path_parts[3], payload)
            except ValueError as exc:
                self._send_json({"error": str(exc)}, status=400)
                return
            self._send_json({"research_question": question}, status=HTTPStatus.CREATED)
            return

        if len(path_parts) == 5 and path_parts[:3] == ["api", "research", "questions"] and path_parts[4] == "hypotheses":
            try:
                hypothesis = research_api.create_hypothesis_item(path_parts[3], payload)
            except ValueError as exc:
                self._send_json({"error": str(exc)}, status=400)
                return
            self._send_json({"hypothesis": hypothesis}, status=HTTPStatus.CREATED)
            return

        if len(path_parts) == 5 and path_parts[:3] == ["api", "research", "hypotheses"] and path_parts[4] == "review":
            try:
                hypothesis = research_api.review_hypothesis_item(path_parts[3], payload)
            except ValueError as exc:
                self._send_json({"error": str(exc)}, status=400)
                return
            if not hypothesis:
                self._send_json({"error": "hypothesis not found"}, status=404)
                return
            self._send_json({"hypothesis": hypothesis})
            return

        if len(path_parts) == 5 and path_parts[:3] == ["api", "research", "hypotheses"] and path_parts[4] == "experiments":
            try:
                experiment = research_api.create_experiment_item(path_parts[3], payload)
            except ValueError as exc:
                self._send_json({"error": str(exc)}, status=400)
                return
            self._send_json({"experiment_request": experiment}, status=HTTPStatus.CREATED)
            return

        if len(path_parts) == 5 and path_parts[:3] == ["api", "research", "experiments"] and path_parts[4] == "approve":
            try:
                experiment = research_api.approve_experiment_item(path_parts[3], payload)
            except ValueError as exc:
                self._send_json({"error": str(exc)}, status=400)
                return
            if not experiment:
                self._send_json({"error": "experiment request not found"}, status=404)
                return
            self._send_json({"experiment_request": experiment})
            return

        if len(path_parts) == 5 and path_parts[:3] == ["api", "research", "experiments"] and path_parts[4] == "launch":
            try:
                experiment = research_api.launch_experiment_item(path_parts[3], payload)
            except ValueError as exc:
                self._send_json({"error": str(exc)}, status=400)
                return
            self._send_json(experiment, status=HTTPStatus.CREATED)
            return

        if len(path_parts) == 4 and path_parts[:2] == ["api", "missions"] and path_parts[3] == "discuss":
            content_text = payload.get("content_text") or payload.get("text") or ""
            if not content_text:
                self._send_json({"error": "content_text is required"}, status=400)
                return
            result = missions_api.add_discussion(path_parts[2], payload)
            self._send_json(result, status=HTTPStatus.CREATED)
            return

        if len(path_parts) == 4 and path_parts[:2] == ["api", "missions"] and path_parts[3] == "analyze":
            try:
                result = missions_api.analyze_item(path_parts[2], payload)
            except (ValueError, RuntimeError) as exc:
                self._send_json({"error": str(exc)}, status=400)
                return
            self._send_json(result, status=HTTPStatus.CREATED)
            return

        if len(path_parts) == 4 and path_parts[:2] == ["api", "missions"] and path_parts[3] == "plans":
            title = payload.get("title") or payload.get("goal_summary") or ""
            if not title:
                self._send_json({"error": "title is required"}, status=400)
                return
            plan_candidate = plans_api.create_candidate(path_parts[2], payload)
            self._send_json({"plan_candidate": plan_candidate}, status=HTTPStatus.CREATED)
            return

        if len(path_parts) == 5 and path_parts[:2] == ["api", "missions"] and path_parts[3] == "plans" and path_parts[4]:
            self._send_json({"error": "unsupported path"}, status=404)
            return

        if len(path_parts) == 6 and path_parts[:2] == ["api", "missions"] and path_parts[3] == "plans" and path_parts[5] == "revise":
            try:
                revision = plans_api.create_revision(path_parts[4], payload)
            except ValueError as exc:
                self._send_json({"error": str(exc)}, status=400)
                return
            self._send_json({"plan_revision": revision}, status=HTTPStatus.CREATED)
            return

        if len(path_parts) == 4 and path_parts[:2] == ["api", "plans"] and path_parts[3] == "revisions":
            try:
                revision = plans_api.create_revision(path_parts[2], payload)
            except ValueError as exc:
                self._send_json({"error": str(exc)}, status=400)
                return
            self._send_json({"plan_revision": revision}, status=HTTPStatus.CREATED)
            return

        if len(path_parts) == 4 and path_parts[:2] == ["api", "revisions"] and path_parts[3] == "branches":
            try:
                revision = plans_api.branch_revision(path_parts[2], payload)
            except ValueError as exc:
                self._send_json({"error": str(exc)}, status=400)
                return
            self._send_json({"plan_revision": revision}, status=HTTPStatus.CREATED)
            return

        if len(path_parts) == 4 and path_parts[:2] == ["api", "revisions"] and path_parts[3] == "launch":
            try:
                launch = plans_api.launch_revision(path_parts[2], payload)
            except ValueError as exc:
                self._send_json({"error": str(exc)}, status=400)
                return
            self._send_json({"launch": launch}, status=HTTPStatus.CREATED)
            return

        if len(path_parts) == 4 and path_parts[:2] == ["api", "missions"] and path_parts[3] == "approval-scopes":
            scope = campaigns_api.create_scope(path_parts[2], payload)
            self._send_json({"approval_scope": scope}, status=HTTPStatus.CREATED)
            return

        if parsed.path == "/api/campaigns":
            required = ["mission_session_id", "plan_revision_id", "approval_scope_id"]
            missing = [name for name in required if not payload.get(name)]
            if missing:
                self._send_json({"error": f"missing fields: {', '.join(missing)}"}, status=400)
                return
            campaign = campaigns_api.create_item(payload)
            self._send_json({"campaign": campaign}, status=HTTPStatus.CREATED)
            return

        if len(path_parts) == 4 and path_parts[:2] == ["api", "campaigns"] and path_parts[3] == "control":
            action = payload.get("action")
            if not action:
                self._send_json({"error": "action is required"}, status=400)
                return
            try:
                campaign = campaigns_api.control_item(path_parts[2], payload)
            except ValueError as exc:
                self._send_json({"error": str(exc)}, status=400)
                return
            if not campaign:
                self._send_json({"error": "campaign not found"}, status=404)
                return
            self._send_json({"campaign": campaign})
            return

        if parsed.path == "/api/mission-plan":
            try:
                self._send_json(
                    analyze_mission(
                        text=payload.get("text", ""),
                        profile=payload.get("executionProfile", "steady"),
                    )
                )
            except (ValueError, RuntimeError) as exc:
                self._send_json({"error": str(exc)}, status=400)
            return

        if parsed.path != "/api/publish":
            self._send_json({"error": "not found"}, status=404)
            return

        try:
            event_id = publish_event(
                event_type=payload.get("type", "task"),
                task=payload["task"],
                params=payload.get("params", {}),
                agent=payload.get("agent", "offense"),
                category=payload.get("category"),
                execution_profile=payload.get("executionProfile"),
                secondary_confirmation=bool(payload.get("secondaryConfirmation", False)),
                interactive=bool(payload.get("interactive", False)),
            )
        except KeyError as exc:
            self._send_json({"error": f"missing field: {exc.args[0]}"}, status=400)
            return

        self._send_json({"ok": True, "event_id": event_id}, status=HTTPStatus.CREATED)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Kaliclaw dashboard server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), DashboardHandler)
    print(f"Kaliclaw dashboard: http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
