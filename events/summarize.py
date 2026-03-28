#!/usr/bin/env python3
"""
结果汇总脚本。

当前口径：
- 优先读取 SQLite/WAL 中的正式结果
- 如果数据库中没有结果，再回退到 results.jsonl
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

from db import get_connection

EVENTS_DIR = Path(__file__).parent
RESULTS_FILE = EVENTS_DIR / "results.jsonl"


def load_results_from_db(
    limit: int | None = None,
    task_filter: str | None = None,
    status_filter: str | None = None,
    category_filter: str | None = None,
) -> list[dict]:
    conn = get_connection()
    try:
        conditions = []
        params: list[str | int] = []

        if task_filter:
            conditions.append("t.operation = ?")
            params.append(task_filter)
        if status_filter:
            mapped_status = "succeeded" if status_filter == "completed" else status_filter
            conditions.append("r.status = ?")
            params.append(mapped_status)
        if category_filter:
            conditions.append("t.capability = ?")
            params.append(category_filter)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        limit_clause = "LIMIT ?" if limit else ""
        if limit:
            params.append(limit)

        rows = conn.execute(
            f"""
            SELECT
                r.task_id,
                r.status,
                r.summary_json,
                r.structured_json,
                r.created_at AS result_created_at,
                t.operation,
                t.capability,
                t.payload_json,
                t.attempt_count,
                t.max_attempts,
                t.created_at AS task_created_at,
                a.executor_type,
                a.tool_name
            FROM results r
            JOIN tasks t ON t.id = r.task_id
            LEFT JOIN task_attempts a
              ON a.task_id = t.id
             AND a.started_at = (
                 SELECT MAX(a2.started_at)
                 FROM task_attempts a2
                 WHERE a2.task_id = t.id
             )
            {where_clause}
            ORDER BY r.created_at DESC
            {limit_clause}
            """,
            params,
        ).fetchall()
    finally:
        conn.close()

    results = []
    for row in rows:
        try:
            summary = json.loads(row["summary_json"])
        except json.JSONDecodeError:
            summary = {}
        try:
            structured = json.loads(row["structured_json"])
        except json.JSONDecodeError:
            structured = {}
        try:
            payload = json.loads(row["payload_json"])
        except json.JSONDecodeError:
            payload = {}

        executor_type = row["executor_type"] or summary.get("executionSource", "unknown")
        raw_data = {
            "task": row["operation"],
            "params": payload.get("params", {}),
            "executionResult": {
                "success": row["status"] == "succeeded",
                "data": structured,
                "message": summary.get("message", ""),
                "executionSource": executor_type,
            },
            "category": row["capability"],
            "apiUsed": executor_type == "agent_api",
            "executionSource": executor_type,
        }
        metadata = {
            "duration": summary.get("duration"),
            "toolsUsed": [row["tool_name"]] if row["tool_name"] else [],
            "apiUsed": executor_type == "agent_api",
            "executionSource": executor_type,
            "agentCategory": row["capability"],
            "attemptCount": row["attempt_count"],
            "maxAttempts": row["max_attempts"],
        }
        results.append(
            {
                "eventId": row["task_id"],
                "status": "completed" if row["status"] == "succeeded" else row["status"],
                "rawData": raw_data,
                "metadata": metadata,
                "createdAt": row["result_created_at"],
                "_source": "sqlite",
            }
        )

    return results


def load_results_from_jsonl(
    limit: int | None = None,
    task_filter: str | None = None,
    status_filter: str | None = None,
    category_filter: str | None = None,
) -> list[dict]:
    if not RESULTS_FILE.exists():
        return []

    results = []
    with open(RESULTS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue

            raw_data = data.get("rawData", {})
            if task_filter and raw_data.get("task") != task_filter:
                continue
            if status_filter and data.get("status") != status_filter:
                continue
            if category_filter and raw_data.get("category") != category_filter:
                continue

            data["_source"] = "jsonl"
            results.append(data)

    results.sort(key=lambda x: x.get("createdAt", ""), reverse=True)
    if limit:
        results = results[:limit]
    return results


def load_results(
    limit: int | None = None,
    task_filter: str | None = None,
    status_filter: str | None = None,
    category_filter: str | None = None,
) -> list[dict]:
    db_results = load_results_from_db(
        limit=limit,
        task_filter=task_filter,
        status_filter=status_filter,
        category_filter=category_filter,
    )
    if db_results:
        return db_results
    return load_results_from_jsonl(
        limit=limit,
        task_filter=task_filter,
        status_filter=status_filter,
        category_filter=category_filter,
    )


def extract_execution_data(execution_result: dict) -> dict:
    if not isinstance(execution_result, dict):
        return {"output": str(execution_result)}
    if "data" in execution_result:
        data = execution_result.get("data", {})
        if isinstance(data, str):
            return {"output": data}
        return data
    if "output" in execution_result:
        return {"output": execution_result.get("output")}
    return execution_result


def summarize_cmcc_scan(results: list[dict]) -> dict:
    summary = {
        "total_aps": 0,
        "channels": defaultdict(int),
        "unique_ssids": set(),
        "rssi_range": {"min": 0, "max": -100},
        "events": [],
    }

    for res in results:
        raw = res.get("rawData", {})
        if raw.get("task") != "scan-cmcc":
            continue

        exec_result = raw.get("executionResult", {})
        data = extract_execution_data(exec_result)
        scan_results = data.get("scanResults", [])

        event_summary = {
            "eventId": res.get("eventId"),
            "timestamp": res.get("createdAt"),
            "ap_count": len(scan_results),
            "category": raw.get("category", "unknown"),
            "executionSource": exec_result.get("executionSource", "unknown"),
            "apiUsed": raw.get("apiUsed", False),
            "aps": [],
        }

        for ap in scan_results:
            if not isinstance(ap, dict):
                continue
            summary["total_aps"] += 1
            summary["unique_ssids"].add(ap.get("ssid", ""))
            channel = ap.get("channel", "")
            if channel:
                summary["channels"][channel] += 1
            rssi_str = ap.get("rssi", "")
            try:
                rssi = int(rssi_str) if str(rssi_str).lstrip("-").isdigit() else -100
            except ValueError:
                rssi = -100
            if rssi > summary["rssi_range"]["max"]:
                summary["rssi_range"]["max"] = rssi
            if rssi < summary["rssi_range"]["min"]:
                summary["rssi_range"]["min"] = rssi
            event_summary["aps"].append(
                {
                    "bssid": ap.get("bssid"),
                    "ssid": ap.get("ssid"),
                    "channel": channel,
                    "rssi": ap.get("rssi"),
                }
            )

        event_summary["aps"] = event_summary["aps"][:5]
        summary["events"].append(event_summary)

    summary["unique_ssid_count"] = len(summary["unique_ssids"])
    return summary


def print_summary(results: list[dict], task_filter: str | None = None, category_filter: str | None = None) -> None:
    if not results:
        print("暂无结果")
        return

    source = results[0].get("_source", "unknown")
    print(f"共 {len(results)} 个结果")
    print(f"结果源: {'SQLite/WAL' if source == 'sqlite' else 'results.jsonl'}")
    print("=" * 70)

    tasks = defaultdict(list)
    for res in results:
        raw = res.get("rawData", {})
        task = raw.get("task", "unknown")
        category = raw.get("category", "unknown")
        if task_filter and task != task_filter:
            continue
        if category_filter and category != category_filter:
            continue
        tasks[task].append((res, category))

    for task, task_items in tasks.items():
        task_results = [item[0] for item in task_items]
        categories = set(item[1] for item in task_items)

        print(f"\n任务类型: {task} ({len(task_results)} 个)")
        print(f"  涉及类别: {', '.join(sorted(categories))}")

        if task == "scan-cmcc":
            summary = summarize_cmcc_scan(task_results)
            print(f"  CMCC 热点总数: {summary['total_aps']}")
            print(f"  唯一 SSID 数量: {summary['unique_ssid_count']}")
            print(f"  频道分布: {dict(summary['channels'])}")
            print(f"  RSSI 范围: {summary['rssi_range']['min']} ~ {summary['rssi_range']['max']}")
            if summary["events"]:
                latest = summary["events"][0]
                source_name = "API" if latest["apiUsed"] else "本地"
                print(f"  最近扫描 ({latest['timestamp'][:19]}, {source_name}): {latest['ap_count']} 个热点")
                for ap in latest["aps"][:3]:
                    print(f"    - {ap['ssid']} ({ap['bssid']}) 频道{ap['channel']} 信号{ap['rssi']}")
            continue

        if task == "ping":
            for res in task_results[:3]:
                raw = res.get("rawData", {})
                exec_result = raw.get("executionResult", {})
                data = extract_execution_data(exec_result)
                event_id = res.get("eventId", "")[:8]
                category = raw.get("category", "unknown")
                api_used = raw.get("apiUsed", False)
                source_name = "API" if api_used else "本地"
                message = exec_result.get("message", "")
                if not message and "output" in data:
                    message = data.get("output", "")
                    if len(message) > 100:
                        message = message[:100] + "..."
                print(f"  {event_id} [{category}, {source_name}] - {message}")
            continue

        for res in task_results[:2]:
            raw = res.get("rawData", {})
            event_id = res.get("eventId", "")[:8]
            category = raw.get("category", "unknown")
            api_used = raw.get("apiUsed", False)
            source_name = "API" if api_used else "本地"
            status = res.get("status", "unknown")
            print(f"  {event_id} [{category}, {source_name}] - 状态: {status}")


def main() -> None:
    parser = argparse.ArgumentParser(description="汇总事件结果")
    parser.add_argument("--last", type=int, help="显示最近 N 个结果")
    parser.add_argument("--task", help="过滤特定任务")
    parser.add_argument("--status", help="过滤状态 (completed, failed, succeeded)")
    parser.add_argument("--category", help="过滤类别 (wireless, recon, web, ...)")
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式")
    args = parser.parse_args()

    results = load_results(
        limit=args.last,
        task_filter=args.task,
        status_filter=args.status,
        category_filter=args.category,
    )

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return
    print_summary(results, task_filter=args.task, category_filter=args.category)


if __name__ == "__main__":
    main()
