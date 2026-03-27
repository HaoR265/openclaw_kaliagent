#!/usr/bin/env python3
"""
归档旧事件文件
将超过指定天数的任务文件压缩为 .gz 格式，可配置是否删除原始文件。
"""

import json
import gzip
import shutil
import sys
from pathlib import Path
from datetime import datetime, timezone, date, timedelta
import argparse

EVENTS_DIR = Path(__file__).parent
ARCHIVE_DIR = EVENTS_DIR / "archive"

def ensure_archive_dir():
    """确保归档目录存在"""
    ARCHIVE_DIR.mkdir(exist_ok=True)
    return ARCHIVE_DIR

def get_task_files():
    """获取所有正式分片任务文件"""
    files = []
    for f in EVENTS_DIR.glob("tasks-*.jsonl"):
        files.append(f)
    return files

def compress_file(filepath, keep_original=True):
    """压缩文件为 .gz 格式"""
    archive_dir = ensure_archive_dir()
    compressed_path = archive_dir / f"{filepath.name}.gz"
    
    try:
        print(f"压缩: {filepath.name} → {compressed_path.name}")
        with open(filepath, 'rb') as f_in:
            with gzip.open(compressed_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # 验证压缩文件
        with gzip.open(compressed_path, 'rb') as f_check:
            # 尝试读取第一行以确保文件有效
            f_check.read(1)
        
        if not keep_original:
            # 验证压缩文件大小非零
            if compressed_path.stat().st_size > 0:
                filepath.unlink()
                print(f"删除原始文件: {filepath.name}")
            else:
                print(f"警告: 压缩文件为空，保留原始文件")
                return False
        
        return True
        
    except Exception as e:
        print(f"压缩失败 {filepath.name}: {e}")
        # 清理可能的部分压缩文件
        if compressed_path.exists():
            compressed_path.unlink()
        return False

def extract_date_from_filename(filename):
    """从文件名中提取日期"""
    # 格式: tasks-YYYY-MM-DD.jsonl (注意: .jsonl 是6个字符)
    if filename.startswith("tasks-") and filename.endswith(".jsonl"):
        date_str = filename[6:-6]  # 移除 "tasks-" 和 ".jsonl"
        try:
            return date.fromisoformat(date_str)
        except ValueError:
            pass
    return None

def main():
    parser = argparse.ArgumentParser(description="归档旧事件文件")
    parser.add_argument("--days", type=int, default=7, 
                       help="保留多少天的原始文件（默认：7）")
    parser.add_argument("--dry-run", action="store_true",
                       help="模拟运行，不实际压缩或删除")
    parser.add_argument("--keep", action="store_true",
                       help="保留原始文件（仅压缩，不删除）")
    parser.add_argument("--min-size", type=int, default=1024,
                       help="最小文件大小（字节），小于此值不压缩（默认：1024）")
    
    args = parser.parse_args()
    
    cutoff_date = date.today() - timedelta(days=args.days)
    task_files = get_task_files()
    
    print(f"归档配置:")
    print(f"  保留天数: {args.days} (早于 {cutoff_date.isoformat()})")
    print(f"  文件数: {len(task_files)}")
    print(f"  归档目录: {ARCHIVE_DIR}")
    print(f"  模式: {'模拟运行' if args.dry_run else '实际执行'}")
    print(f"  保留原始文件: {args.keep}")
    print()
    
    compressed_count = 0
    skipped_count = 0
    error_count = 0
    
    for filepath in task_files:
        file_date = extract_date_from_filename(filepath.name)
        
        if file_date is None:
            print(f"跳过无法解析日期的文件: {filepath.name}")
            skipped_count += 1
            continue
        
        # 检查是否早于截止日期
        if file_date >= cutoff_date:
            print(f"跳过未过期文件: {filepath.name} ({file_date.isoformat()})")
            skipped_count += 1
            continue
        
        # 检查文件大小
        file_size = filepath.stat().st_size
        if file_size < args.min_size:
            print(f"跳过小文件: {filepath.name} ({file_size} 字节)")
            skipped_count += 1
            continue
        
        # 检查是否已归档
        archive_path = ARCHIVE_DIR / f"{filepath.name}.gz"
        if archive_path.exists():
            print(f"跳过已归档文件: {filepath.name}")
            skipped_count += 1
            continue
        
        if args.dry_run:
            print(f"[模拟] 将归档: {filepath.name} ({file_date.isoformat()}, {file_size} 字节)")
            compressed_count += 1
            continue
        
        # 实际压缩
        success = compress_file(filepath, keep_original=args.keep)
        if success:
            compressed_count += 1
        else:
            error_count += 1
    
    print()
    print("归档完成:")
    print(f"  成功压缩: {compressed_count}")
    print(f"  跳过: {skipped_count}")
    print(f"  错误: {error_count}")
    
    # 显示归档目录内容
    if ARCHIVE_DIR.exists():
        gz_files = list(ARCHIVE_DIR.glob("*.gz"))
        if gz_files:
            print(f"\n归档目录中的文件 ({len(gz_files)} 个):")
            for f in sorted(gz_files)[-5:]:  # 显示最近5个
                size_mb = f.stat().st_size / 1024 / 1024
                print(f"  {f.name} ({size_mb:.2f} MB)")

if __name__ == "__main__":
    main()
