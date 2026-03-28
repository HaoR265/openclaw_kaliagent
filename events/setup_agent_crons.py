#!/usr/bin/env python3
"""
为6个专业化攻击者代理设置cron作业
每个代理每分钟检查一次事件队列
"""

import subprocess
import sys
from pathlib import Path

EVENTS_DIR = Path(__file__).parent
WORKER = EVENTS_DIR / "worker.py"

# 6个代理类别
CATEGORIES = [
    "wireless", "recon", "web", "internal", "exploit", "social"
]

def get_current_crontab():
    """获取当前crontab内容"""
    try:
        result = subprocess.run(
            ["crontab", "-l"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return result.stdout
        else:
            # 如果没有crontab，返回空字符串
            return ""
    except Exception as e:
        print(f"获取crontab失败: {e}")
        return ""

def set_crontab(content):
    """设置crontab内容"""
    try:
        proc = subprocess.Popen(
            ["crontab", "-"],
            stdin=subprocess.PIPE,
            text=True
        )
        proc.communicate(input=content)
        if proc.returncode == 0:
            return True
        else:
            print(f"设置crontab失败 (返回码: {proc.returncode})")
            return False
    except Exception as e:
        print(f"设置crontab异常: {e}")
        return False

def main():
    print("为专业化攻击者代理设置cron作业")
    print("=" * 50)
    
    if not WORKER.exists():
        print(f"错误: worker 脚本不存在: {WORKER}")
        sys.exit(1)
    
    # 获取当前crontab
    current_crontab = get_current_crontab()
    
    # 移除现有的代理消费者 cron 作业（包括历史 consume.py 入口和旧 agent_consumer.py 入口）
    lines = current_crontab.split('\n')
    new_lines = []
    
    for line in lines:
        # 保留不是代理消费者cron的行
        if "agent_consumer.py" not in line and "events/consume.py" not in line and "worker.py" not in line:
            new_lines.append(line)
    
    # 为每个代理添加 worker cron 作业
    print("添加cron作业:")
    for category in CATEGORIES:
        cron_line = f"* * * * * cd {EVENTS_DIR} && /usr/bin/python3 {WORKER} --category {category} --once >> {EVENTS_DIR}/{category}.log 2>&1\n"
        new_lines.append(cron_line)
        print(f"  {category}: 每分钟检查一次")
    
    # 添加一个注释行
    new_lines.append("# 专业化攻击者数据库 worker (6个类别)")
    
    # 构建新的crontab内容
    new_crontab = '\n'.join(new_lines).strip() + '\n'
    
    # 显示将要设置的内容
    print(f"\n新的crontab将有 {len(new_lines)} 行")
    
    # 自动确认（非交互模式）
    response = 'y'
    print("\n自动确认设置cron作业 (非交互模式)")
    
    # 设置新的crontab
    if set_crontab(new_crontab):
        print("\ncron作业设置成功!")
        print(f"日志文件将保存到: {EVENTS_DIR}/*.log")
        print("\nworker 启动后，将每分钟检查一次 SQLite/JSONL 双轨队列。")
        
        # 显示测试命令
        print("\n测试命令:")
        for category in CATEGORIES:
            print(f"  {category}: python3 {WORKER} --category {category} --once")
        
        # 显示监控命令
        print("\n监控命令:")
        print(f"  查看队列状态: python3 {EVENTS_DIR}/status.py")
        print(f"  查看日志: tail -f {EVENTS_DIR}/wireless.log")
    else:
        print("\ncron作业设置失败")
        sys.exit(1)

if __name__ == "__main__":
    main()
