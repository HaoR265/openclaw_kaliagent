#!/usr/bin/env python3
"""
遗留脚本：旧 workspace 内本地消费者入口。

当前正式路径为 `events/agent_consumer.py --category web`。
本脚本保留仅用于阻断误用。
"""

import sys

def main():
    print("错误: workspaces/offense-web/consume.py 已废弃。")
    print("请改用: python3 /home/asus/.openclaw/events/agent_consumer.py --category web [--once]")
    sys.exit(1)

if __name__ == "__main__":
    main()
