#!/usr/bin/env python3
"""
事件发布脚本
用法：python3 publish.py --type <type> --task <task> [--params <json>] [--agent <agent>]
示例：python3 publish.py --type scan --task scan-cmcc --params '{"interface":"wlan1"}'
"""

import json
import sys
import uuid
import argparse
from datetime import datetime, timezone, date, timedelta
from pathlib import Path

from db import insert_task

EVENTS_DIR = Path(__file__).parent

def get_tasks_file(target_date=None):
    """返回指定日期的任务文件路径（默认今天）"""
    if target_date is None:
        target_date = date.today()
    elif isinstance(target_date, str):
        target_date = date.fromisoformat(target_date)
    filename = f"tasks-{target_date.isoformat()}.jsonl"
    return EVENTS_DIR / filename

def get_all_task_files(days_back=7):
    """返回最近几天的任务文件列表"""
    files = []
    for i in range(days_back):
        d = date.today() - timedelta(days=i)
        f = get_tasks_file(d)
        if f.exists():
            files.append(f)
    return files

def publish_event(
    event_type,
    task,
    params=None,
    agent="offense",
    category=None,
    execution_profile=None,
    secondary_confirmation=False,
    interactive=False,
):
    """发布新事件，优先写入数据库，同时保留 JSONL 兼容写入。"""
    params = dict(params or {})
    if execution_profile:
        params.setdefault("executionProfile", execution_profile)
    if secondary_confirmation:
        params.setdefault("secondaryConfirmation", True)
    if interactive:
        params.setdefault("interactive", True)

    event = {
        "id": str(uuid.uuid4()),
        "type": event_type,
        "agent": agent,
        "task": task,
        "params": params,
        "status": "pending",
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "retryCount": 0,
        "maxRetries": 3,
        "deadLetter": False,
        "statusHistory": []
    }
    if category:
        event["category"] = category

    insert_task(event)

    tasks_file = get_tasks_file()
    with open(tasks_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

    print(f"事件已发布: {event['id']} (db + jsonl)")
    return event['id']

def main():
    parser = argparse.ArgumentParser(description="发布事件到队列")
    parser.add_argument("--type", required=True, help="事件类型 (scan, ping, attack)")
    parser.add_argument("--task", required=True, help="任务标识符")
    parser.add_argument("--params", default="{}", help="JSON 格式的参数")
    parser.add_argument("--agent", default="offense", help="逻辑目标代理标识（保留兼容字段，建议结合 --category 使用）")
    parser.add_argument("--category", help="攻击者类别 (wireless, recon, web, internal, exploit, social)")
    parser.add_argument("--execution-profile", choices=["steady", "rush"], help="执行档位")
    parser.add_argument("--secondary-confirmation", action="store_true", help="为 rush/high-risk 任务附加显式二次确认")
    parser.add_argument("--interactive", action="store_true", help="标记该任务将调用交互式工具")
    
    args = parser.parse_args()
    
    try:
        params = json.loads(args.params)
    except json.JSONDecodeError as e:
        print(f"参数 JSON 解析失败: {e}")
        sys.exit(1)
    
    event_id = publish_event(
        args.type,
        args.task,
        params,
        args.agent,
        args.category,
        args.execution_profile,
        args.secondary_confirmation,
        args.interactive,
    )
    print(f"事件 ID: {event_id}")

if __name__ == "__main__":
    main()
