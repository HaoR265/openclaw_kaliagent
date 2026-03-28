#!/usr/bin/env python3
"""
遗留脚本：旧 workspace 内本地消费者入口。

当前正式路径为 `events/agent_consumer.py --category internal`。
本脚本保留仅用于阻断误用。
"""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVENTS_DIR = Path(os.environ.get("KALICLAW_ROOT", str(ROOT))).expanduser() / "events"

def main():
    print("错误: workspaces/offense-internal/consume.py 已废弃。")
    print(f"请改用: python3 {EVENTS_DIR}/agent_consumer.py --category internal [--once]")
    sys.exit(1)

if __name__ == "__main__":
    main()
