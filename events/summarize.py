#!/usr/bin/env python3
"""
结果汇总脚本（支持新版 API 响应格式）
从 results.jsonl 读取数据，生成摘要报告。
"""

import json
import sys
import argparse
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict

EVENTS_DIR = Path(__file__).parent
RESULTS_FILE = EVENTS_DIR / "results.jsonl"

def load_results(limit=None, task_filter=None, status_filter=None, category_filter=None):
    """读取结果文件，可选过滤和限制"""
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
                raw_data = data.get("rawData", {})
                
                if task_filter and raw_data.get("task") != task_filter:
                    continue
                if status_filter and data.get("status") != status_filter:
                    continue
                if category_filter and raw_data.get("category") != category_filter:
                    continue
                    
                results.append(data)
            except json.JSONDecodeError as e:
                print(f"解析行时出错: {e}", file=sys.stderr)
    
    # 按时间倒序排列
    results.sort(key=lambda x: x.get("createdAt", ""), reverse=True)
    
    if limit:
        results = results[:limit]
    return results

def extract_execution_data(execution_result):
    """从 executionResult 中提取数据（兼容新旧格式）"""
    if not isinstance(execution_result, dict):
        return {"output": str(execution_result)}
    
    # 新格式: {"success": ..., "data": ..., "message": ..., "executionSource": ...}
    if "data" in execution_result:
        data = execution_result.get("data", {})
        # 如果 data 是字符串，转换为输出
        if isinstance(data, str):
            return {"output": data}
        return data
    # 旧格式: {"output": ..., "success": ...}
    elif "output" in execution_result:
        return {"output": execution_result.get("output")}
    # 其他格式
    else:
        return execution_result

def summarize_cmcc_scan(results):
    """汇总 CMCC 扫描结果（兼容新旧格式）"""
    summary = {
        "total_aps": 0,
        "channels": defaultdict(int),
        "unique_ssids": set(),
        "rssi_range": {"min": 0, "max": -100},
        "events": []
    }
    
    for res in results:
        raw = res.get("rawData", {})
        if raw.get("task") != "scan-cmcc":
            continue
        
        exec_result = raw.get("executionResult", {})
        data = extract_execution_data(exec_result)
        
        # 尝试从不同字段获取扫描结果
        scan_results = data.get("scanResults", [])
        if not scan_results and "scanResults" in exec_result:
            scan_results = exec_result.get("scanResults", [])
        
        event_summary = {
            "eventId": res.get("eventId"),
            "timestamp": res.get("createdAt"),
            "ap_count": len(scan_results),
            "category": raw.get("category", "unknown"),
            "executionSource": exec_result.get("executionSource", "unknown"),
            "apiUsed": raw.get("apiUsed", False),
            "aps": []
        }
        
        for ap in scan_results:
            if not isinstance(ap, dict):
                continue
            summary["total_aps"] += 1
            summary["unique_ssids"].add(ap.get("ssid", ""))
            ch = ap.get("channel", "")
            if ch:
                summary["channels"][ch] += 1
            rssi_str = ap.get("rssi", "")
            try:
                rssi = int(rssi_str) if rssi_str.lstrip('-').isdigit() else -100
            except:
                rssi = -100
            if rssi > summary["rssi_range"]["max"]:
                summary["rssi_range"]["max"] = rssi
            if rssi < summary["rssi_range"]["min"]:
                summary["rssi_range"]["min"] = rssi
            
            event_summary["aps"].append({
                "bssid": ap.get("bssid"),
                "ssid": ap.get("ssid"),
                "channel": ch,
                "rssi": ap.get("rssi")
            })
        
        event_summary["aps"] = event_summary["aps"][:5]  # 每个事件最多显示5个AP
        summary["events"].append(event_summary)
    
    summary["unique_ssid_count"] = len(summary["unique_ssids"])
    return summary

def print_summary(results, task_filter=None, category_filter=None):
    """打印摘要报告"""
    if not results:
        print("暂无结果")
        return
    
    print(f"共 {len(results)} 个结果")
    print("=" * 70)
    
    # 按任务类型分组
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
            
            # 显示最近一次扫描的详情
            if summary["events"]:
                latest = summary["events"][0]
                source = "API" if latest["apiUsed"] else "本地"
                print(f"  最近扫描 ({latest['timestamp'][:19]}, {source}): {latest['ap_count']} 个热点")
                for ap in latest["aps"][:3]:
                    print(f"    - {ap['ssid']} ({ap['bssid']}) 频道{ap['channel']} 信号{ap['rssi']}")
        
        elif task == "ping":
            for res in task_results[:3]:
                raw = res.get("rawData", {})
                exec_result = raw.get("executionResult", {})
                data = extract_execution_data(exec_result)
                
                event_id = res.get("eventId", "")[:8]
                category = raw.get("category", "unknown")
                api_used = raw.get("apiUsed", False)
                source = "API" if api_used else "本地"
                
                # 提取消息
                message = ""
                if "message" in exec_result:
                    message = exec_result.get("message", "")
                elif "output" in data:
                    message = data.get("output", "")
                    if len(message) > 100:
                        message = message[:100] + "..."
                
                print(f"  {event_id} [{category}, {source}] - {message}")
        
        else:
            # 通用显示
            for res in task_results[:2]:
                raw = res.get("rawData", {})
                event_id = res.get("eventId", "")[:8]
                category = raw.get("category", "unknown")
                api_used = raw.get("apiUsed", False)
                source = "API" if api_used else "本地"
                status = res.get("status", "unknown")
                
                print(f"  {event_id} [{category}, {source}] - 状态: {status}")

def main():
    parser = argparse.ArgumentParser(description="汇总事件结果")
    parser.add_argument("--last", type=int, help="显示最近 N 个结果")
    parser.add_argument("--task", help="过滤特定任务 (scan-cmcc, ping)")
    parser.add_argument("--status", help="过滤状态 (completed, failed)")
    parser.add_argument("--category", help="过滤类别 (wireless, recon, web, ...)")
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式")
    
    args = parser.parse_args()
    
    results = load_results(limit=args.last, task_filter=args.task, 
                          status_filter=args.status, category_filter=args.category)
    
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print_summary(results, task_filter=args.task, category_filter=args.category)

if __name__ == "__main__":
    main()