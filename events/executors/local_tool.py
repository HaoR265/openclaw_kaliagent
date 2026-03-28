#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from executors.base import ExecutionContext, ExecutionResult
from policies import validate_local_tool_request
from tool_registry import find_recipe, find_tool, resolve_recipe_command

SAFE_LOCAL_TOOLS = {
    "nmap",
    "httpx",
    "whatweb",
    "dig",
    "curl",
    "ffuf",
    "gobuster",
}

RUSH_LOCAL_TOOLS = SAFE_LOCAL_TOOLS | {
    "masscan",
    "nikto",
    "wfuzz",
    "wpscan",
    "john",
    "hashcat",
    "hydra",
    "sqlmap",
    "aircrack-ng",
    "ettercap",
    "burpsuite",
    "smbclient",
    "impacket-smbclient",
    "gdb",
    "radare2",
}


def resolve_allowed_tools(execution_profile: str) -> set[str]:
    return RUSH_LOCAL_TOOLS if execution_profile == "rush" else SAFE_LOCAL_TOOLS


def execute(event: dict, context: ExecutionContext, artifacts_dir: Path) -> ExecutionResult:
    params = event.get("params", {})
    tool = params.get("tool")
    command = params.get("command")
    execution_profile = params.get("executionProfile", "steady")
    secondary_confirmation = bool(params.get("secondaryConfirmation", False))
    interactive = bool(params.get("interactive", False))
    policy_refs = ["common-safe"]

    if not tool or not command:
        recipe = find_recipe(context.capability, context.operation)
        if recipe is None:
            return ExecutionResult(
                status="failed",
                summary={"message": f"no local-tool recipe for {context.capability}.{context.operation}", "success": False},
                structured_result={
                    "success": False,
                    "task": event["task"],
                    "params": params,
                    "category": context.capability,
                    "executionSource": "local-tool",
                },
                metrics={"duration": 0},
                error={"code": "recipe_not_found", "message": f"no local-tool recipe for {context.capability}.{context.operation}"},
                executor_type="local_tool",
            )
        tool, command = resolve_recipe_command(recipe, params)
        policy_refs = recipe.get("policy_refs", ["common-safe"])
    else:
        tool_entry = find_tool(tool)
        if tool_entry:
            policy_refs = tool_entry.get("policy_refs", ["common-safe"])
            interactive = bool(tool_entry.get("interactive", interactive))
            if tool_entry.get("risk_level") == "high" and execution_profile == "rush" and "rush-confirmed" not in policy_refs:
                policy_refs = list(policy_refs) + ["rush-confirmed"]

    validation = validate_local_tool_request(
        tool=tool,
        command=command,
        allowed_tools=resolve_allowed_tools(execution_profile),
        policy_refs=policy_refs,
        execution_profile=execution_profile,
        secondary_confirmation=secondary_confirmation,
        interactive=interactive,
    )
    if validation is not None:
        return ExecutionResult(
            status="failed",
            summary={"message": validation["message"], "success": False},
            structured_result={
                "success": False,
                "task": event["task"],
                "params": params,
                "category": context.capability,
                "executionSource": "local-tool",
            },
            metrics={"duration": 0},
            error=validation,
            executor_type="local_tool",
            tool_name=tool,
        )

    proc = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        timeout=int(params.get("timeoutSeconds", 300)),
    )

    artifacts_dir.mkdir(parents=True, exist_ok=True)
    stdout_path = artifacts_dir / f"{context.task_id}-stdout.log"
    stderr_path = artifacts_dir / f"{context.task_id}-stderr.log"
    stdout_path.write_text(proc.stdout, encoding="utf-8")
    stderr_path.write_text(proc.stderr, encoding="utf-8")

    success = proc.returncode == 0
    artifacts = [
        {"kind": "stdout-log", "path": str(stdout_path), "mime_type": "text/plain"},
        {"kind": "stderr-log", "path": str(stderr_path), "mime_type": "text/plain"},
    ]
    return ExecutionResult(
        status="succeeded" if success else "failed",
        summary={"message": f"local tool {tool} executed", "success": success},
        structured_result={
            "success": success,
            "task": event["task"],
            "params": params,
            "tool": tool,
            "executionProfile": execution_profile,
            "secondaryConfirmation": secondary_confirmation,
            "returncode": proc.returncode,
            "stdoutPreview": proc.stdout[:500],
            "stderrPreview": proc.stderr[:500],
            "executionSource": "local-tool",
        },
        artifacts=artifacts,
        metrics={"duration": 1, "exit_code": proc.returncode},
        error=None if success else {"code": "execution_failed", "message": f"{tool} exited with {proc.returncode}"},
        executor_type="local_tool",
        tool_name=tool,
    )
