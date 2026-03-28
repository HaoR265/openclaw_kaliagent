#!/usr/bin/env python3
import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("KALICLAW_ROOT", str(Path(__file__).resolve().parent))).expanduser()
CONFIG_BASENAME = os.environ.get("KALICLAW_CONFIG_BASENAME", "openclaw.json")
SOURCE_CONFIG_BASENAME = os.environ.get("KALICLAW_SOURCE_CONFIG_BASENAME", CONFIG_BASENAME)
config_path = ROOT / CONFIG_BASENAME
source_config_path = ROOT / SOURCE_CONFIG_BASENAME
AGENT_ROOT = ROOT / "agents"
WORKSPACE_ROOT = ROOT / "workspaces"
COMMON_BIN = str(ROOT / "agent-kits" / "common" / "bin")


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


def normalize_exec_paths(config: dict) -> bool:
    exec_cfg = config.setdefault("tools", {}).setdefault("exec", {})
    paths = list(exec_cfg.get("pathPrepend", []))
    updated = False

    if not paths:
        exec_cfg["pathPrepend"] = [COMMON_BIN]
        return True

    normalized_paths: list[str] = []
    common_bin_seen = False
    for path in paths:
        if path.endswith("/agent-kits/common/bin"):
            normalized = COMMON_BIN
            common_bin_seen = True
        else:
            normalized = path
            if normalized == COMMON_BIN:
                common_bin_seen = True
        if normalized != path:
            updated = True
        normalized_paths.append(normalized)

    if common_bin_seen:
        normalized_paths = [path for path in normalized_paths if path != COMMON_BIN]
        normalized_paths.insert(0, COMMON_BIN)
    else:
        normalized_paths.insert(0, COMMON_BIN)
        updated = True

    if normalized_paths != paths:
        exec_cfg["pathPrepend"] = normalized_paths
        updated = True
    return updated

# 读取配置文件
with open(source_config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

# 更新代理的 workspace / agentDir / exec 路径
updated = False
for agent in config.get('agents', {}).get('list', []):
    agent_id = agent.get('id', '')
    new_workspace = workspace_for_agent(agent_id)
    if new_workspace:
        old_workspace = agent.get('workspace', '')
        if old_workspace != new_workspace:
            print(f'更新 {agent_id} workspace: {old_workspace} -> {new_workspace}')
            agent['workspace'] = new_workspace
            updated = True
        else:
            print(f'{agent_id} 已使用正确 workspace: {new_workspace}')

    new_agent_dir = agent_dir_for_agent(agent_id)
    old_agent_dir = agent.get('agentDir', '')
    if old_agent_dir != new_agent_dir:
        print(f'更新 {agent_id} agentDir: {old_agent_dir} -> {new_agent_dir}')
        agent['agentDir'] = new_agent_dir
        updated = True

if normalize_exec_paths(config):
    print(f'更新 tools.exec.pathPrepend: 置顶 {COMMON_BIN}')
    updated = True

target_changed = config_path != source_config_path

if updated or target_changed:
    # 写入更新后的配置
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    if target_changed:
        print(f'\n配置已迁移: {source_config_path} -> {config_path}')
    else:
        print('\n配置已更新')
    
    # 验证目录存在
    print('\n验证workspace目录:')
    for agent in config.get('agents', {}).get('list', []):
        agent_id = agent.get('id', '')
        workspace = agent.get('workspace', '')
        agent_dir = agent.get('agentDir', '')
        if workspace:
            if os.path.exists(workspace):
                print(f'✓ {agent_id} workspace: {workspace}')
            else:
                print(f'✗ {agent_id} workspace: 目录不存在 {workspace}')
        if agent_dir:
            if os.path.exists(agent_dir):
                print(f'✓ {agent_id} agentDir: {agent_dir}')
            else:
                print(f'✗ {agent_id} agentDir: 目录不存在 {agent_dir}')
else:
    print('无需更新')
