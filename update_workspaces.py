#!/usr/bin/env python3
import argparse
import json
import os
from pathlib import Path
from typing import Any

ROOT = Path(os.environ.get("KALICLAW_ROOT", str(Path(__file__).resolve().parent))).expanduser()
SOURCE_ROOT = Path(os.environ.get("KALICLAW_SOURCE_ROOT", str(ROOT))).expanduser()
CONFIG_BASENAME = os.environ.get("KALICLAW_CONFIG_BASENAME", "kaliclaw.json")
LEGACY_CONFIG_BASENAME = "openclaw.json"
CONFIG_PATH = ROOT / CONFIG_BASENAME
SOURCE_OVERRIDE = os.environ.get("KALICLAW_SOURCE_CONFIG_BASENAME")
AGENT_ROOT = ROOT / "agents"
WORKSPACE_ROOT = ROOT / "workspaces"
COMMON_BIN = str(ROOT / "agent-kits" / "common" / "bin")


def resolve_source_config_path() -> Path:
    if SOURCE_OVERRIDE:
        return SOURCE_ROOT / SOURCE_OVERRIDE
    if CONFIG_PATH.exists():
        return CONFIG_PATH
    legacy_config_path = SOURCE_ROOT / LEGACY_CONFIG_BASENAME
    if legacy_config_path.exists():
        return legacy_config_path
    return CONFIG_PATH


def workspace_for_agent(agent_id: str) -> str | None:
    if agent_id == "command":
        return str(WORKSPACE_ROOT / "command")
    if agent_id == "defense":
        return str(WORKSPACE_ROOT / "defense")
    if agent_id.startswith("offense-"):
        return str(WORKSPACE_ROOT / agent_id)
    return None


def agent_dir_for_agent(agent_id: str) -> str:
    return str(AGENT_ROOT / agent_id / "agent")


def load_config(source_config_path: Path) -> dict[str, Any]:
    if not source_config_path.exists():
        raise FileNotFoundError(f"配置文件不存在: {source_config_path}")
    with source_config_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def normalize_exec_paths(config: dict[str, Any], messages: list[str]) -> bool:
    exec_cfg = config.setdefault("tools", {}).setdefault("exec", {})
    paths = list(exec_cfg.get("pathPrepend", []))

    if not paths:
        exec_cfg["pathPrepend"] = [COMMON_BIN]
        messages.append(f"更新 tools.exec.pathPrepend: 初始化为 [{COMMON_BIN}]")
        return True

    normalized_paths: list[str] = []
    common_bin_seen = False
    for path in paths:
        normalized = COMMON_BIN if path.endswith("/agent-kits/common/bin") else path
        if normalized == COMMON_BIN:
            common_bin_seen = True
        normalized_paths.append(normalized)

    if common_bin_seen:
        normalized_paths = [path for path in normalized_paths if path != COMMON_BIN]
        normalized_paths.insert(0, COMMON_BIN)
    else:
        normalized_paths.insert(0, COMMON_BIN)

    if normalized_paths != paths:
        exec_cfg["pathPrepend"] = normalized_paths
        messages.append(f"更新 tools.exec.pathPrepend: 置顶 {COMMON_BIN}")
        return True
    return False


def transform_config(config: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    messages: list[str] = []

    for agent in config.get("agents", {}).get("list", []):
        agent_id = agent.get("id", "")
        new_workspace = workspace_for_agent(agent_id)
        if new_workspace:
            old_workspace = agent.get("workspace", "")
            if old_workspace != new_workspace:
                agent["workspace"] = new_workspace
                messages.append(f"更新 {agent_id} workspace: {old_workspace} -> {new_workspace}")
            else:
                messages.append(f"{agent_id} 已使用正确 workspace: {new_workspace}")

        new_agent_dir = agent_dir_for_agent(agent_id)
        old_agent_dir = agent.get("agentDir", "")
        if old_agent_dir != new_agent_dir:
            agent["agentDir"] = new_agent_dir
            messages.append(f"更新 {agent_id} agentDir: {old_agent_dir} -> {new_agent_dir}")
        else:
            messages.append(f"{agent_id} 已使用正确 agentDir: {new_agent_dir}")

    normalize_exec_paths(config, messages)
    return config, messages


def verify_paths(config: dict[str, Any]) -> list[str]:
    lines = ["", "验证 workspace 与 agentDir:"]
    for agent in config.get("agents", {}).get("list", []):
        agent_id = agent.get("id", "")
        workspace = agent.get("workspace", "")
        agent_dir = agent.get("agentDir", "")
        if workspace:
            marker = "✓" if os.path.exists(workspace) else "✗"
            status = workspace if os.path.exists(workspace) else f"目录不存在 {workspace}"
            lines.append(f"{marker} {agent_id} workspace: {status}")
        if agent_dir:
            marker = "✓" if os.path.exists(agent_dir) else "✗"
            status = agent_dir if os.path.exists(agent_dir) else f"目录不存在 {agent_dir}"
            lines.append(f"{marker} {agent_id} agentDir: {status}")
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize Kaliclaw/OpenClaw workspace config paths.")
    parser.add_argument("--dry-run", action="store_true", help="only print the planned changes")
    args = parser.parse_args()

    source_config_path = resolve_source_config_path()
    config = load_config(source_config_path)
    original_text = json.dumps(config, indent=2, ensure_ascii=False)
    config, messages = transform_config(config)
    updated_text = json.dumps(config, indent=2, ensure_ascii=False)
    target_changed = CONFIG_PATH != source_config_path
    content_changed = updated_text != original_text

    print(f"根目录: {ROOT}")
    print(f"源根目录: {SOURCE_ROOT}")
    print(f"源配置: {source_config_path}")
    print(f"目标配置: {CONFIG_PATH}")
    if target_changed:
        print("模式: source -> target 迁移")
    elif args.dry_run:
        print("模式: dry-run")

    if messages:
        print("\n计划变更:")
        for message in messages:
            print(f"- {message}")

    if not content_changed and not target_changed:
        print("\n无需更新")
        return 0

    if args.dry_run:
        if target_changed:
            print(f"\n[dry-run] 将写出新配置: {CONFIG_PATH}")
        else:
            print("\n[dry-run] 将原地更新配置")
        return 0

    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(updated_text + "\n", encoding="utf-8")
    if target_changed:
        print(f"\n配置已迁移: {source_config_path} -> {CONFIG_PATH}")
    else:
        print("\n配置已更新")

    for line in verify_paths(config):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
