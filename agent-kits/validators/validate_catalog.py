#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path("/home/asus/.openclaw/agent-kits")
CATALOGS = sorted((ROOT / "offense-kit" / "catalog").glob("*.json")) + sorted((ROOT / "defense-kit" / "catalog").glob("*.json")) + sorted((ROOT / "cmd-special" / "catalog").glob("*.json"))
RECIPES = sorted((ROOT / "recipes").glob("*.json"))
POLICIES = sorted((ROOT / "policies").glob("*.json"))


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_catalog(path: Path) -> list[str]:
    data = load_json(path)
    errors = []
    for idx, item in enumerate(data.get("items", []), start=1):
        for key in [
            "id", "name", "category", "summary", "tags", "target_types",
            "requires_sudo", "interactive", "read_only", "destructive",
            "risk_level", "default_timeout_seconds", "policy_refs"
        ]:
            if key not in item:
                errors.append(f"{path.name} item #{idx} missing key: {key}")
        if "bin" not in item and "members" not in item:
            errors.append(f"{path.name} item #{idx} requires either 'bin' or 'members'")
    return errors


def validate_recipe(path: Path) -> list[str]:
    data = load_json(path)
    errors = []
    for key in [
        "id", "capability", "operation", "primary_tool", "tool_bin",
        "allowed_tools", "command_template", "input_schema", "policy_refs", "artifact_rules"
    ]:
        if key not in data:
            errors.append(f"{path.name} missing key: {key}")
    return errors


def validate_policy(path: Path) -> list[str]:
    data = load_json(path)
    errors = []
    for key in ["id", "description"]:
        if key not in data:
            errors.append(f"{path.name} missing key: {key}")
    return errors


def main() -> int:
    errors: list[str] = []
    for path in CATALOGS:
        errors.extend(validate_catalog(path))
    for path in RECIPES:
        errors.extend(validate_recipe(path))
    for path in POLICIES:
        errors.extend(validate_policy(path))

    if errors:
        print("validation failed:")
        for err in errors:
            print(f"- {err}")
        return 1

    print("catalog/recipe/policy validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
