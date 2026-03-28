# 从 OpenClaw 兼容目录迁移到 Kaliclaw（爪龙）

这份文档描述最后一轮默认值翻转后的迁移方式。目标是把旧兼容目录 `~/.openclaw` 迁到新的默认目录 `~/.kaliclaw`，同时把默认配置名与数据库名切到 Kaliclaw。

## 迁移目标

- 默认根目录：`~/.kaliclaw`
- 默认 CLI：`kaliclaw`
- 默认配置名：`kaliclaw.json`
- 默认主数据库：`kaliclaw.db`

兼容层仍保留：`openclaw`、`~/.openclaw`、`openclaw.json`、`openclaw.db`。

## 一次性迁移

先做 dry-run：

```bash
cd ~/.openclaw && scripts/migrate_to_kaliclaw.sh --dry-run
```

确认输出无误后正式执行：

```bash
cd ~/.openclaw && scripts/migrate_to_kaliclaw.sh
```

迁移完成后检查新的运行根：

```bash
~/.kaliclaw/scripts/check_kaliclaw_runtime.sh ~/.kaliclaw
```

## 脚本做了什么

1. 把当前仓库复制到 `~/.kaliclaw`
2. 如存在 `events/runtime/openclaw.db`，复制为 `events/runtime/kaliclaw.db`
3. 调用 `update_workspaces.py` 生成 `kaliclaw.json`
4. 规范 `workspace / agentDir / tools.exec.pathPrepend`
5. 创建 `~/.local/bin/kaliclaw -> ~/.kaliclaw/kaliclaw` 软链接

## 仅迁移配置名

如果只想从旧 `openclaw.json` 生成新的 `kaliclaw.json`：

```bash
KALICLAW_SOURCE_ROOT="$HOME/.openclaw" \
KALICLAW_ROOT="$HOME/.kaliclaw" \
KALICLAW_SOURCE_CONFIG_BASENAME=openclaw.json \
KALICLAW_CONFIG_BASENAME=kaliclaw.json \
python3 update_workspaces.py
```

## 兼容回退

如果你还没准备好切换，可以继续使用兼容入口：

```bash
export KALICLAW_ROOT="$HOME/.openclaw"
export KALICLAW_CONFIG_PATH="$HOME/.openclaw/openclaw.json"
kaliclaw gateway status
```

Kaliclaw wrapper 会优先使用新默认值；如果未找到 `~/.kaliclaw`，会自动回退到旧兼容根目录并提示当前正在兼容模式运行。
