#!/usr/bin/env python3
"""
存储监控脚本
检查事件队列目录的大小，超过阈值时告警
"""

import os
import sys
import json
from pathlib import Path

# 配置
EVENTS_DIR = Path(__file__).parent
MAX_SIZE_MB = 100  # 最大100MB
LOG_FILE = EVENTS_DIR / "storage.log"

def get_directory_size(path):
    """计算目录大小（字节）"""
    total = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.isfile(fp):
                total += os.path.getsize(fp)
    return total

def bytes_to_mb(bytes_val):
    """字节转换为MB"""
    return bytes_val / (1024 * 1024)

def check_storage():
    """检查存储使用情况"""
    total_bytes = get_directory_size(EVENTS_DIR)
    total_mb = bytes_to_mb(total_bytes)
    
    # 检查各个子目录
    subdirs = {}
    for item in EVENTS_DIR.iterdir():
        if item.is_dir():
            size_bytes = get_directory_size(item)
            subdirs[item.name] = {
                "size_mb": bytes_to_mb(size_bytes),
                "size_bytes": size_bytes,
                "percent": (size_bytes / total_bytes * 100) if total_bytes > 0 else 0
            }
    
    # 检查大文件
    large_files = []
    for item in EVENTS_DIR.rglob("*"):
        if item.is_file():
            size = item.stat().st_size
            if size > 10 * 1024 * 1024:  # 10MB以上
                large_files.append({
                    "path": str(item.relative_to(EVENTS_DIR)),
                    "size_mb": bytes_to_mb(size)
                })
    
    result = {
        "timestamp": os.path.getmtime(__file__),  # 使用脚本修改时间作为时间戳
        "total_mb": total_mb,
        "total_bytes": total_bytes,
        "max_mb": MAX_SIZE_MB,
        "usage_percent": (total_mb / MAX_SIZE_MB * 100) if MAX_SIZE_MB > 0 else 0,
        "subdirectories": subdirs,
        "large_files": large_files[:10],  # 只显示前10个大文件
        "alerts": []
    }
    
    # 生成告警
    if total_mb > MAX_SIZE_MB:
        result["alerts"].append(f"存储超限: {total_mb:.1f}MB > {MAX_SIZE_MB}MB")
    
    if total_mb > MAX_SIZE_MB * 0.8:
        result["alerts"].append(f"存储使用率过高: {total_mb/MAX_SIZE_MB*100:.1f}%")
    
    if large_files:
        result["alerts"].append(f"发现大文件: {len(large_files)}个")
    
    # 写入日志
    log_entry = {
        "timestamp": result["timestamp"],
        "total_mb": total_mb,
        "alerts": result["alerts"]
    }
    
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    return result

def main():
    """主函数"""
    result = check_storage()
    
    # 控制台输出
    print(f"存储监控报告 ({EVENTS_DIR})")
    print(f"总大小: {result['total_mb']:.2f}MB / {result['max_mb']}MB ({result['usage_percent']:.1f}%)")
    print()
    
    if result["subdirectories"]:
        print("子目录大小:")
        for name, info in sorted(result["subdirectories"].items(), key=lambda x: x[1]["size_mb"], reverse=True):
            print(f"  {name}: {info['size_mb']:.2f}MB ({info['percent']:.1f}%)")
    
    if result["large_files"]:
        print("\n大文件 (>10MB):")
        for file_info in result["large_files"]:
            print(f"  {file_info['path']}: {file_info['size_mb']:.2f}MB")
    
    if result["alerts"]:
        print("\n⚠️  告警:")
        for alert in result["alerts"]:
            print(f"  {alert}")
        
        # 如果有告警，返回非零退出码
        sys.exit(1)
    else:
        print("\n✅ 存储状态正常")
        sys.exit(0)

if __name__ == "__main__":
    main()