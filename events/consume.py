#!/usr/bin/env python3
"""
遗留脚本：旧版消费者入口。

当前正式消费者为 `events/agent_consumer.py`。
本脚本保留仅用于显式阻断旧路径，避免继续执行历史逻辑。
"""

import sys


def main():
    print("错误: events/consume.py 已废弃。")
    print("请改用: python3 events/agent_consumer.py --category <category> [--once]")
    sys.exit(1)


if __name__ == "__main__":
    main()
