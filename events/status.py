#!/usr/bin/env python3
"""
队列状态监控（分片任务文件）
"""

import json
from pathlib import Path
from datetime import datetime, timezone, date, timedelta

from db import backfill_tasks_from_jsonl, db_ready, fetch_task_stats

EVENTS_DIR = Path(__file__).parent
RESULTS_FILE = EVENTS_DIR / "results.jsonl"
DEAD_LETTER_FILE = EVENTS_DIR / "dead-letter.jsonl"
CATEGORY_LOGS = ["wireless", "recon", "web", "internal", "exploit", "social"]

def get_task_files(days_back=7):
    """获取最近几天的分片任务文件"""
    files = []
    for i in range(days_back):
        d = date.today() - timedelta(days=i)
        filename = f"tasks-{d.isoformat()}.jsonl"
        f = EVENTS_DIR / filename
        if f.exists():
            files.append(f)
    return files

def count_lines(filepath):
    if not filepath.exists():
        return 0
    with open(filepath, "r", encoding="utf-8") as f:
        return sum(1 for line in f if line.strip())

def analyze_tasks():
    """分析所有任务文件"""
    task_files = get_task_files()
    
    stats = {
        "total": 0, "pending": 0, "processing": 0, "completed": 0, "failed": 0,
        "by_date": {}, "by_category": {}
    }
    latest = None
    
    for task_file in task_files:
        date_str = task_file.stem.replace("tasks-", "")
        
        if not task_file.exists():
            continue
            
        date_stats = {"total": 0, "pending": 0, "processing": 0, "completed": 0, "failed": 0}
        
        with open(task_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    stats["total"] += 1
                    date_stats["total"] += 1
                    
                    status = data.get("status", "unknown")
                    if status in stats:
                        stats[status] += 1
                        date_stats[status] += 1
                    
                    # 按类别统计
                    category = data.get("category", "unknown")
                    if category not in stats["by_category"]:
                        stats["by_category"][category] = 0
                    stats["by_category"][category] += 1
                    
                    # 记录最新事件时间
                    created = data.get("createdAt")
                    if created:
                        dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                        if latest is None or dt > latest:
                            latest = dt
                            
                except json.JSONDecodeError:
                    pass
        
        stats["by_date"][date_str] = date_stats
    
    stats["latest"] = latest.isoformat() if latest else None
    return stats


def analyze_tasks_from_db():
    db_stats = fetch_task_stats()
    states = db_stats["states"]
    return {
        "total": db_stats["total"],
        "pending": states["queued"],
        "processing": states["running"] + states["leased"],
        "completed": states["succeeded"],
        "failed": states["failed"] + states["dead_letter"],
        "by_date": {},
        "by_category": db_stats["by_capability"],
        "latest": db_stats["latest"],
    }

def main():
    results = count_lines(RESULTS_FILE)
    dead = count_lines(DEAD_LETTER_FILE)
    task_files = get_task_files()

    use_db = db_ready()
    if use_db:
        try:
            backfill_tasks_from_jsonl()
            stats = analyze_tasks_from_db()
        except Exception:
            stats = analyze_tasks()
            use_db = False
    else:
        stats = analyze_tasks()
    
    print("事件队列状态")
    print("=" * 50)

    if use_db:
        print("状态源: SQLite/WAL (WP-1)")
    else:
        print("状态源: JSONL 兼容模式")

    if not task_files and stats["total"] == 0:
        print("未找到任务文件")
        return
    
    print(f"任务文件数: {len(task_files)}")
    print(f"总事件数: {stats['total']}")
    print(f"  待处理: {stats['pending']}")
    print(f"  处理中: {stats['processing']}")
    print(f"  已完成: {stats['completed']}")
    print(f"  失败:   {stats['failed']}")
    
    if stats['latest']:
        print(f"最新事件: {stats['latest']}")
    
    print()
    
    # 按日期显示分布
    if stats["by_date"]:
        print("按日期分布:")
        for date_str, date_stats in sorted(stats["by_date"].items()):
            if date_stats["total"] > 0:
                print(f"  {date_str}: {date_stats['total']} 事件 (待处理: {date_stats['pending']}, 处理中: {date_stats['processing']}, 已完成: {date_stats['completed']})")
    
    # 按类别显示分布
    if stats["by_category"]:
        print("\n按类别分布:")
        for category, count in sorted(stats["by_category"].items()):
            print(f"  {category}: {count}")
    
    print()
    print(f"结果数量: {results}")
    print(f"死信数量: {dead}")
    print()
    
    # 显示各类别日志的最近更新时间
    available_logs = []
    for category in CATEGORY_LOGS:
        log_file = EVENTS_DIR / f"{category}.log"
        if log_file.exists():
            available_logs.append((category, log_file.stat().st_mtime))

    if available_logs:
        print("代理日志:")
        for category, mtime in sorted(available_logs):
            updated = datetime.fromtimestamp(mtime).isoformat(timespec="seconds")
            print(f"  {category}: {updated}")
    else:
        print("未找到代理日志")
    
    # 显示当前待处理事件（如果有）
    if stats["pending"] > 0:
        print(f"\n当前有 {stats['pending']} 个待处理事件，下次 cron 将在下一分钟处理")

if __name__ == "__main__":
    main()
