#!/usr/bin/env python3
from __future__ import annotations

from db import get_connection, insert_task, upsert_result
from knowledge.db import get_connection as get_knowledge_connection
from knowledge.search import search_intel, search_knowledge
from services.control import (
    control_campaign,
    create_approval_scope,
    create_campaign,
    create_mission,
    create_plan_candidate,
    create_plan_revision,
    get_artifact_detail,
    get_campaign_detail,
    get_workflow_detail,
    launch_plan_revision,
)


def main() -> None:
    created: dict[str, str] = {}
    try:
        mission = create_mission("Smoke Mission", "necessary smoke", created_by="codex")
        created["mission_id"] = mission["id"]

        plan = create_plan_candidate(mission["id"], "Smoke Plan", goal_summary="smoke", discussion_summary="main chain")
        created["plan_id"] = plan["id"]

        revision = create_plan_revision(
            plan["id"],
            "smoke revision",
            task_tree=[{"category": "recon", "task": "scan", "params": {"tool": "nmap"}}],
            launchable=True,
        )
        created["revision_id"] = revision["id"]

        scope = create_approval_scope(
            mission["id"],
            "open",
            allowed_categories=["recon"],
            allowed_tools=["nmap"],
            confirmed_by="codex",
        )
        created["scope_id"] = scope["id"]

        campaign = create_campaign(mission["id"], revision["id"], scope["id"])
        created["campaign_id"] = campaign["id"]
        detail = get_campaign_detail(campaign["id"])
        assert detail and detail["campaign"]["available_actions"] == ["resume", "stop", "kill"]

        launch = launch_plan_revision(revision["id"], launch_mode="assisted", execution_profile="steady")
        workflow_id = launch["workflow_id"]
        created["workflow_id"] = workflow_id
        workflow = get_workflow_detail(workflow_id)
        assert workflow and workflow["workflow"]["plan_revision_id"] == revision["id"]

        task_id = workflow["tasks"][0]["id"]
        upsert_result(task_id, "succeeded", {"message": "runtime smoke ok"}, {"service": "ssh"})
        intel_hits = search_intel("runtime smoke ok", capability="recon")
        knowledge_hits = search_knowledge([], "runtime smoke ok", capability="recon")
        assert intel_hits
        assert knowledge_hits

        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO artifacts(id, task_id, kind, path, mime_type, size_bytes, sha256, created_at)
                VALUES ('artifact_smoke', ?, 'report', ?, 'text/plain', 12, NULL, datetime('now'))
                """,
                (task_id, "/tmp/kaliclaw-smoke-report.txt"),
            )
            conn.commit()
        created["artifact_id"] = "artifact_smoke"
        with open("/tmp/kaliclaw-smoke-report.txt", "w", encoding="utf-8") as handle:
            handle.write("smoke artifact\nline2")
        artifact = get_artifact_detail("artifact_smoke")
        assert artifact and "smoke artifact" in (artifact.get("preview_text") or "")

        resumed = control_campaign(campaign["id"], "resume")
        assert resumed and resumed["status"] == "running"
        same = control_campaign(campaign["id"], "resume")
        assert same and same["status"] == "running"

        print(
            "SMOKE_NECESSARY_OK",
            {
                "campaign_actions": detail["campaign"]["available_actions"],
                "workflow_id": workflow_id,
                "artifact_preview": bool(artifact.get("preview_text")),
                "intel_hits": len(intel_hits),
                "knowledge_hits": len(knowledge_hits),
            },
        )
    finally:
        with get_connection() as conn:
            if created.get("artifact_id"):
                conn.execute("DELETE FROM artifacts WHERE id = ?", (created["artifact_id"],))
            if created.get("workflow_id"):
                conn.execute("DELETE FROM launch_batches WHERE workflow_id = ?", (created["workflow_id"],))
                conn.execute("DELETE FROM results WHERE task_id IN (SELECT id FROM tasks WHERE workflow_id = ?)", (created["workflow_id"],))
                conn.execute("DELETE FROM tasks WHERE workflow_id = ?", (created["workflow_id"],))
            if created.get("campaign_id"):
                conn.execute("DELETE FROM campaign_events WHERE campaign_run_id = ?", (created["campaign_id"],))
                conn.execute("DELETE FROM campaign_runs WHERE id = ?", (created["campaign_id"],))
            if created.get("scope_id"):
                conn.execute("DELETE FROM approval_scopes WHERE id = ?", (created["scope_id"],))
            if created.get("revision_id"):
                conn.execute("DELETE FROM plan_revisions WHERE id = ?", (created["revision_id"],))
            if created.get("plan_id"):
                conn.execute("DELETE FROM plan_candidates WHERE id = ?", (created["plan_id"],))
            if created.get("mission_id"):
                conn.execute("DELETE FROM mission_sessions WHERE id = ?", (created["mission_id"],))
            conn.commit()
        with get_knowledge_connection() as conn:
            conn.execute("DELETE FROM intel_items WHERE summary LIKE '%runtime smoke ok%'")
            conn.execute("DELETE FROM knowledge_entries WHERE summary LIKE '%runtime smoke ok%'")
            conn.commit()


if __name__ == "__main__":
    main()
