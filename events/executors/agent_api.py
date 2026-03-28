#!/usr/bin/env python3
from __future__ import annotations

from agent_consumer import call_category_api
from executors.base import ExecutionContext, ExecutionResult


def execute(event: dict, context: ExecutionContext) -> ExecutionResult:
    api_result = call_category_api(context.capability, event)
    if api_result is None:
        return ExecutionResult(
            status="failed",
            summary={"message": f"{context.capability} API call failed"},
            structured_result={
                "success": False,
                "task": event["task"],
                "params": event.get("params", {}),
                "category": context.capability,
                "executionSource": "agent-api",
            },
            metrics={"duration": 1},
            error={"code": "api_error", "message": f"{context.capability} API call failed"},
            executor_type="agent_api",
        )

    success = bool(api_result.get("success", True))
    return ExecutionResult(
        status="succeeded" if success else "failed",
        summary={
            "message": api_result.get("message", f"{context.capability} task executed"),
            "success": success,
        },
        structured_result={
            "success": success,
            "data": api_result.get("data", api_result),
            "message": api_result.get("message"),
            "executionSource": "agent-api",
            "category": context.capability,
            "task": event["task"],
            "params": event.get("params", {}),
        },
        metrics={"duration": 1},
        error=None if success else {"code": "execution_failed", "message": api_result.get("message", "Execution failed")},
        executor_type="agent_api",
    )

