#!/usr/bin/env python3
from __future__ import annotations

import shlex

from tool_registry import load_policy


def validate_local_tool_request(
    tool: str | None,
    command: str | None,
    allowed_tools: set[str],
    policy_refs: list[str] | None = None,
    execution_profile: str = "steady",
    secondary_confirmation: bool = False,
    interactive: bool = False,
) -> dict | None:
    if not tool or not command:
        return {"code": "policy_denied", "message": "local tool execution requires tool and command"}
    if tool not in allowed_tools:
        return {"code": "policy_denied", "message": f"tool '{tool}' is not in the local-tool allowlist"}
    argv = shlex.split(command)
    if not argv:
        return {"code": "policy_denied", "message": "empty local tool command"}
    if argv[0] != tool:
        return {"code": "policy_denied", "message": "command must start with the declared tool name"}
    for policy_ref in policy_refs or []:
        policy = load_policy(policy_ref)
        if not policy:
            continue
        allowed_profiles = set(policy.get("execution_profiles", []))
        if allowed_profiles and execution_profile not in allowed_profiles:
            return {"code": "policy_denied", "message": f"policy '{policy_ref}' does not allow execution profile '{execution_profile}'"}
        if policy.get("requires_usb_wifi"):
            if not policy.get("allow_external_wifi_operations"):
                return {"code": "policy_denied", "message": f"policy '{policy_ref}' forbids current wireless operation"}
        if tool in set(policy.get("forbidden_binaries", [])):
            return {"code": "policy_denied", "message": f"tool '{tool}' is forbidden by policy '{policy_ref}'"}
        allowed = policy.get("allowed_tools")
        if allowed and tool not in set(allowed):
            return {"code": "policy_denied", "message": f"tool '{tool}' is not allowed by policy '{policy_ref}'"}
        if policy.get("forbid_interactive") and interactive:
            if not (
                execution_profile == "rush"
                and policy.get("allow_interactive_in_rush")
                and secondary_confirmation
            ):
                return {"code": "policy_denied", "message": f"interactive tool '{tool}' requires rush mode and secondary confirmation under policy '{policy_ref}'"}
        if policy.get("require_secondary_confirmation") and not secondary_confirmation:
            return {"code": "policy_denied", "message": f"policy '{policy_ref}' requires explicit secondary confirmation"}
    return None
