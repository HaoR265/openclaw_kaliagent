#!/usr/bin/env python3
"""
数据库驱动的最小 worker 实现。

WP-2 阶段目标：
- 从 SQLite 真源 claim 任务
- 形成 leased -> running -> succeeded/failed/retry_wait/dead_letter 状态流转
- 执行逻辑暂时复用 agent_consumer 中已有的代理 API 调用函数
"""

from __future__ import annotations

import argparse
import socket
import time
import uuid
from pathlib import Path

from agent_consumer import (
    get_tasks_file,
    load_events,
    save_events,
    update_event_status,
    write_result,
)
from db import (
    claim_next_task,
    complete_task,
    fetch_legacy_event,
    heartbeat_worker,
    insert_artifact,
    mark_task_running,
    mark_worker_offline,
    register_worker,
    schedule_retry,
    update_attempt_metadata,
    upsert_result,
)
from executors.base import ExecutionContext
from executors import agent_api as agent_api_executor
from executors import local_tool as local_tool_executor

ARTIFACTS_DIR = Path(__file__).parent / "runtime" / "artifacts"


def build_worker_id(capability: str) -> str:
    return f"{socket.gethostname()}:{capability}:{uuid.uuid4().hex[:8]}"


def sync_legacy_jsonl_status(task_id: str, new_status: str) -> None:
    tasks_file = get_tasks_file()
    if not tasks_file.exists():
        return
    events = load_events()
    if update_event_status(task_id, new_status, events):
        save_events(events)


def choose_executor(event: dict) -> str:
    params = event.get("params", {})
    execution_mode = params.get("executionMode")
    if execution_mode == "local_tool":
        return "local_tool"
    return "agent_api"


def process_one_task(capability: str, worker_id: str, execution_profile_default: str = "steady") -> bool:
    claimed = claim_next_task(capability=capability, worker_id=worker_id)
    if claimed is None:
        return False

    task_id = claimed["id"]
    event = fetch_legacy_event(task_id)
    if event is None:
        return False
    event.setdefault("params", {})
    event["params"].setdefault("executionProfile", execution_profile_default)

    executor_type = choose_executor(event)
    attempt_id = mark_task_running(task_id=task_id, worker_id=worker_id, executor_type=executor_type)
    sync_legacy_jsonl_status(task_id, "processing")
    heartbeat_worker(worker_id)
    context = ExecutionContext(
        task_id=task_id,
        capability=capability,
        operation=event["task"],
        worker_id=worker_id,
    )
    failure_message = None

    try:
        if executor_type == "local_tool":
            exec_result = local_tool_executor.execute(event, context, ARTIFACTS_DIR)
        else:
            exec_result = agent_api_executor.execute(event, context)

        update_attempt_metadata(
            attempt_id=attempt_id,
            executor_type=exec_result.executor_type,
            tool_name=exec_result.tool_name,
            exit_code=exec_result.metrics.get("exit_code"),
            error_code=exec_result.error["code"] if exec_result.error else None,
            error_message=exec_result.error["message"] if exec_result.error else None,
        )
        upsert_result(
            task_id=task_id,
            status=exec_result.status,
            summary=exec_result.summary,
            structured_result=exec_result.structured_result,
        )
        for artifact in exec_result.artifacts:
            insert_artifact(
                task_id=task_id,
                kind=artifact["kind"],
                path=artifact["path"],
                mime_type=artifact.get("mime_type"),
            )

        if exec_result.status == "succeeded":
            final_state = "succeeded"
            complete_task(task_id=task_id, attempt_id=attempt_id, status=final_state)
            sync_legacy_jsonl_status(task_id, "completed")
        else:
            final_state = "failed"
            schedule_retry(
                task_id=task_id,
                attempt_id=attempt_id,
                error_message=exec_result.error["message"] if exec_result.error else exec_result.summary.get("message", "worker execution failed"),
            )
            sync_legacy_jsonl_status(task_id, "failed")
    except Exception as exc:
        exec_result = None
        final_state = "failed"
        failure_message = str(exc)
        schedule_retry(
            task_id=task_id,
            attempt_id=attempt_id,
            error_message=str(exc),
        )
        sync_legacy_jsonl_status(task_id, "failed")

    raw_data = {
        "task": event["task"],
        "params": event.get("params", {}),
        "executionResult": {
            "success": exec_result is not None and exec_result.status == "succeeded",
            "data": exec_result.structured_result if exec_result is not None else {"error": "execution exception"},
            "message": exec_result.summary.get("message") if exec_result is not None else (failure_message or "execution exception"),
            "executionSource": executor_type,
        },
        "category": capability,
        "apiUsed": executor_type == "agent_api",
        "executionSource": executor_type,
    }
    metadata = {
        "duration": (exec_result.metrics.get("duration", 1) if exec_result is not None else 1),
        "toolsUsed": [exec_result.tool_name] if exec_result is not None and exec_result.tool_name else [],
        "apiUsed": executor_type == "agent_api",
        "executionSource": executor_type,
        "agentCategory": capability,
        "workerId": worker_id,
    }
    write_result(
        task_id,
        "completed" if exec_result is not None and exec_result.status == "succeeded" else "failed",
        raw_data,
        metadata,
    )
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="数据库驱动的专业化代理 worker")
    parser.add_argument(
        "--category",
        required=True,
        help="能力类别 (wireless, recon, web, internal, exploit, social)",
    )
    parser.add_argument("--once", action="store_true", help="只处理一次然后退出")
    parser.add_argument(
        "--poll-seconds",
        type=int,
        default=15,
        help="未拿到任务时的轮询等待秒数",
    )
    parser.add_argument(
        "--execution-profile-default",
        choices=["steady", "rush"],
        default="steady",
        help="任务未显式设置 executionProfile 时采用的默认档位",
    )
    args = parser.parse_args()

    worker_id = build_worker_id(args.category)
    register_worker(worker_id=worker_id, agent_id=f"offense-{args.category}", capabilities=[args.category])
    print(f"启动数据库 worker: {worker_id}")

    try:
        while True:
            heartbeat_worker(worker_id)
            handled = process_one_task(args.category, worker_id, args.execution_profile_default)
            if args.once:
                return
            if not handled:
                time.sleep(args.poll_seconds)
    finally:
        mark_worker_offline(worker_id)


if __name__ == "__main__":
    main()
