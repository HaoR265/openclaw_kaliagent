# Kaliclaw（爪龙）最后脱离 OpenClaw 的回滚说明

如果默认值翻转后需要回退到旧兼容运行方式，按下面步骤处理。

## 快速回滚

```bash
rm -f ~/.local/bin/kaliclaw
rm -rf ~/.kaliclaw
export KALICLAW_ROOT="$HOME/.openclaw"
export KALICLAW_CONFIG_PATH="$HOME/.openclaw/openclaw.json"
openclaw gateway status
```

## 保守回滚

如果你只是不想让新默认值生效，而不删除新目录：

```bash
export KALICLAW_ROOT="$HOME/.openclaw"
export KALICLAW_CONFIG_PATH="$HOME/.openclaw/openclaw.json"
export KALICLAW_CLI_BIN="openclaw"
```

然后继续使用旧兼容链路。

## 验证回滚

```bash
openclaw config file
python3 ~/.openclaw/dashboard/server.py --host 127.0.0.1 --port 8787
```

如果 `openclaw config file` 输出 `~/.openclaw/openclaw.json`，说明回滚已回到旧兼容入口。
