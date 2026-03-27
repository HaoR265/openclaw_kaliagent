#!/usr/bin/env python3
"""
创建6个独立攻击者代理配置
"""

import json
import shutil
import sys
from pathlib import Path

# 基础配置
AGENTS_DIR = Path("/home/asus/.openclaw/agents")
SOURCE_AGENT = AGENTS_DIR / "offense-backup"  # 使用备份作为模板

# 类别与API密钥映射（从 apis.json 获取）
CATEGORIES = {
    "wireless": "sk-b5caaee6333247fbb3281cddf839ea5d",
    "recon": "sk-1f37071b3d6a4dcb8f4c8230488fede9",
    "web": "sk-6e0260ca2e5646929e95e1f5f4907328",
    "internal": "sk-52bcfb2cd5964eae98751e023d7d74bb",
    "exploit": "sk-f99582d889484114b6cb96a69d735884",
    "social": "sk-32a0a13256cb4d6780a41d9489a7de04"
}

def read_models_template():
    """读取原始 models.json 作为模板"""
    models_file = SOURCE_AGENT / "agent" / "models.json"
    if not models_file.exists():
        print(f"错误: 模板文件不存在: {models_file}")
        sys.exit(1)
    
    with open(models_file, "r", encoding="utf-8") as f:
        return json.load(f)

def update_models_for_category(models_data, api_key, category):
    """更新 models.json 中的 API 密钥和 baseUrl"""
    # 更新 deepseek 提供商的配置
    if "providers" in models_data and "deepseek" in models_data["providers"]:
        models_data["providers"]["deepseek"]["baseUrl"] = "https://api.deepseek.com/beta"
        models_data["providers"]["deepseek"]["apiKey"] = api_key
    else:
        # 如果结构不同，确保有正确的配置
        models_data["providers"] = {
            "deepseek": {
                "baseUrl": "https://api.deepseek.com/beta",
                "api": "openai-completions",
                "apiKey": api_key,
                "models": [
                    {
                        "id": "deepseek-chat",
                        "name": "DeepSeek Chat",
                        "api": "openai-completions",
                        "reasoning": False,
                        "input": ["text"],
                        "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0},
                        "contextWindow": 131072,
                        "maxTokens": 8192,
                        "compat": {"supportsUsageInStreaming": True}
                    },
                    {
                        "id": "deepseek-reasoner",
                        "name": "DeepSeek Reasoner",
                        "api": "openai-completions",
                        "reasoning": True,
                        "input": ["text"],
                        "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0},
                        "contextWindow": 131072,
                        "maxTokens": 65536,
                        "compat": {"supportsUsageInStreaming": True}
                    }
                ]
            }
        }
    return models_data

def create_agent_for_category(category, api_key):
    """为特定类别创建代理配置"""
    agent_name = f"offense-{category}"
    target_dir = AGENTS_DIR / agent_name
    
    print(f"创建代理: {agent_name}")
    
    # 1. 复制目录结构
    if target_dir.exists():
        print(f"  警告: {agent_name} 已存在，跳过创建")
        return False
    
    try:
        # 复制整个目录
        shutil.copytree(SOURCE_AGENT, target_dir)
        print(f"  目录结构已复制")
    except Exception as e:
        print(f"  复制失败: {e}")
        return False
    
    # 2. 更新 models.json
    models_file = target_dir / "agent" / "models.json"
    if models_file.exists():
        models_data = read_models_template()
        updated_models = update_models_for_category(models_data, api_key, category)
        
        with open(models_file, "w", encoding="utf-8") as f:
            json.dump(updated_models, f, indent=2, ensure_ascii=False)
        print(f"  models.json 已更新")
    
    # 3. 创建 AGENTS.md（可选，描述代理职责）
    agents_md = target_dir / "AGENTS.md"
    if not agents_md.exists():
        with open(agents_md, "w", encoding="utf-8") as f:
            f.write(f"""# {category.upper()} 攻击者代理

## 职责
专门负责 **{category}** 类别的渗透测试任务。

## 技能范围
{get_category_skills(category)}

## 配置
- API: DeepSeek Beta (专用密钥)
- 端点: https://api.deepseek.com/beta/chat/completions
- 模型: deepseek-chat / deepseek-reasoner

## 使用方式
1. 通过事件队列路由（category="{category}"）
2. 直接调用: `openclaw agent --agent offense-{category} --message "任务"`

---

**注意**: 此代理是 6 个专业化攻击者之一，取代了通用的 'offense' 代理。
""")
        print(f"  AGENTS.md 已创建")
    
    # 4. 清理 sessions 目录（避免会话冲突）
    sessions_dir = target_dir / "sessions"
    if sessions_dir.exists():
        for item in sessions_dir.iterdir():
            if item.is_file() and item.name != "sessions.json":
                item.unlink()
        # 重置 sessions.json
        sessions_file = sessions_dir / "sessions.json"
        if sessions_file.exists():
            with open(sessions_file, "w", encoding="utf-8") as f:
                json.dump({}, f)
        print(f"  sessions 目录已清理")
    
    return True

def get_category_skills(category):
    """返回类别对应的技能描述"""
    skills = {
        "wireless": """- WiFi 监控、抓包、破解
- WPS 攻击
- 热点扫描与识别
- 握手包捕获与分析""",
        "recon": """- 端口扫描与服务识别
- 子网发现与拓扑映射
- DNS 枚举与信息收集
- 公开情报收集 (OSINT)""",
        "web": """- SQL 注入检测与利用
- XSS 与 CSRF 漏洞测试
- 目录遍历与文件包含
- API 安全测试
- Web 服务器配置审计""",
        "internal": """- 横向移动技术
- 凭证窃取与哈希传递
- 权限提升
- 内网侦察与后渗透""",
        "exploit": """- 已知漏洞利用 (Metasploit, PoC)
- CVE 分析与验证
- 漏洞研究
- 利用链构建""",
        "social": """- 钓鱼活动设计与执行
- 社会工程学信息收集
- 诱饵部署
- 人为因素漏洞评估"""
    }
    return skills.get(category, "- 通用渗透测试任务")

def main():
    print("开始创建 6 个独立攻击者代理配置")
    print("=" * 60)
    
    if not SOURCE_AGENT.exists():
        print(f"错误: 源代理目录不存在: {SOURCE_AGENT}")
        print("请先运行: cp -r /home/asus/.openclaw/agents/offense /home/asus/.openclaw/agents/offense-backup")
        sys.exit(1)
    
    created_count = 0
    for category, api_key in CATEGORIES.items():
        success = create_agent_for_category(category, api_key)
        if success:
            created_count += 1
        print()
    
    print(f"创建完成: {created_count}/{len(CATEGORIES)} 个代理")
    
    # 列出创建的代理
    print("\n创建的代理列表:")
    for category in CATEGORIES.keys():
        agent_name = f"offense-{category}"
        agent_dir = AGENTS_DIR / agent_name
        if agent_dir.exists():
            print(f"  ✓ {agent_name}")
        else:
            print(f"  ✗ {agent_name} (失败)")
    
    # 下一步建议
    print("\n下一步:")
    print("1. 测试代理配置: openclaw agent --agent offense-wireless --message '测试'")
    print("2. 配置路由绑定: openclaw agents bind --agent offense-wireless --bind webchat:wireless")
    print("3. 更新 AGENTS.md 文档，引用新的专业化攻击者")
    print("4. 可选的: 删除旧的通用 'offense' 代理")

if __name__ == "__main__":
    main()