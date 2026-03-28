#!/usr/bin/env python3
"""
历史脚本：创建早期 offense-* 代理配置。

当前目录结构和正式配置已经稳定，本脚本保留为归档占位，
不再允许继续运行，也不再在仓库中保存任何明文 API 密钥。
"""

from __future__ import annotations

import sys


def main() -> None:
    print("该脚本已废弃，不再用于当前正式代理体系。", file=sys.stderr)
    print("原因：offense-* 代理、独立 workspace 和 worker 路径已完成收敛。", file=sys.stderr)
    print("请改用当前正式配置与文档，不要再通过该脚本生成代理。", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
