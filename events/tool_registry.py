#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path("/home/asus/.openclaw/agent-kits")
CATALOG_PATHS = [
    ROOT / "offense-kit" / "catalog" / "front-tools.json",
    ROOT / "defense-kit" / "catalog" / "front-tools.json",
    ROOT / "cmd-special" / "catalog" / "rare-tools.json",
]
RECIPES_DIR = ROOT / "recipes"
POLICIES_DIR = ROOT / "policies"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def find_tool(tool_name: str) -> dict | None:
    for path in CATALOG_PATHS:
        data = _load_json(path)
        for item in data.get("items", []):
            if item.get("name") == tool_name or item.get("bin") == tool_name:
                return item
    return None


def find_recipe(capability: str, operation: str) -> dict | None:
    if not RECIPES_DIR.exists():
        return None
    for path in RECIPES_DIR.glob("*.json"):
        recipe = _load_json(path)
        if recipe.get("capability") == capability and recipe.get("operation") == operation:
            return recipe
    return None


def load_policy(policy_id: str) -> dict | None:
    path = POLICIES_DIR / f"{policy_id}.json"
    if path.exists():
        return _load_json(path)
    for candidate in POLICIES_DIR.glob("*.json"):
        data = _load_json(candidate)
        if data.get("id") == policy_id:
            return data
    return None


def resolve_recipe_command(recipe: dict, params: dict) -> tuple[str, str]:
    resolved = {}
    for key, config in recipe.get("input_schema", {}).items():
        if key in params:
            resolved[key] = params[key]
        elif "default" in config:
            resolved[key] = config["default"]
        elif config.get("required"):
            raise ValueError(f"missing required recipe param: {key}")
    return recipe["tool_bin"], recipe["command_template"].format(**resolved)
