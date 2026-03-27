#!/usr/bin/env python3
import json
import sys
import os

config_path = os.path.expanduser('~/.openclaw/openclaw.json')

# 读取配置文件
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

# 更新代理的workspace
updated = False
for agent in config.get('agents', {}).get('list', []):
    agent_id = agent.get('id', '')
    if agent_id.startswith('offense-'):
        category = agent_id.split('-', 1)[1]  # 提取wireless, recon等
        new_workspace = f'/home/asus/.openclaw/workspaces/offense-{category}'
        old_workspace = agent.get('workspace', '')
        
        if old_workspace != new_workspace:
            print(f'更新 {agent_id}: {old_workspace} -> {new_workspace}')
            agent['workspace'] = new_workspace
            updated = True
        else:
            print(f'{agent_id} 已使用正确workspace: {new_workspace}')

if updated:
    # 写入更新后的配置
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    print('\n配置已更新')
    
    # 验证目录存在
    print('\n验证workspace目录:')
    for agent in config.get('agents', {}).get('list', []):
        agent_id = agent.get('id', '')
        if agent_id.startswith('offense-'):
            workspace = agent.get('workspace', '')
            if os.path.exists(workspace):
                print(f'✓ {agent_id}: {workspace}')
            else:
                print(f'✗ {agent_id}: 目录不存在 {workspace}')
else:
    print('无需更新')