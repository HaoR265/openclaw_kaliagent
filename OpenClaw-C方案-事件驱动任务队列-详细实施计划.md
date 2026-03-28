# OpenClaw C方案 - 事件驱动任务队列详细实施计划

## 文档状态

该文档保留为历史实施记录，不再作为当前正式路线图。

当前正式设计与后续实施计划请改看：

- [OpenClaw-多Agent编排与Kali工具系统重构设计.md](OpenClaw-多Agent编排与Kali工具系统重构设计.md)
- [ARCHITECTURE.md](ARCHITECTURE.md)
- [events/EVENT_PROTOCOL.md](events/EVENT_PROTOCOL.md)

## 历史说明

本文件原先记录的是早期 `JSONL + cron + agent_consumer.py` 方案，以及 6 个专业化 `offense-*` 代理的初始拆分过程。由于当前仓库已经完成以下收敛，这些内容不再适合作为后续修改依据：

- 正式真源已切换到 `SQLite/WAL`
- 正式执行入口已切换到 `worker.py`
- 旧共享 `offense` 目录和旧消费者路径已清理
- 工具目录已进入 `catalog + recipe + policy` 最小落地阶段

## 安全说明

历史版本中曾包含示例性敏感配置与明文 API 密钥。该类内容已从仓库文档中清除，后续若需记录配置示例，应统一使用占位符，例如：

```json
{
  "api_key": "${DEEPSEEK_API_KEY}",
  "base_url": "https://api.deepseek.com/beta",
  "model": "deepseek-chat"
}
```

## 历史方案摘要

早期 C 方案的主要目标有三点：

1. 将单一 `offense` 执行代理拆成 6 个专业化类别
2. 通过异步任务队列实现 `command` 与执行代理解耦
3. 建立基础状态监控、结果汇总和归档能力

这些目标已经在后续实现中被继承，但落地内核已经从早期文件队列演进到当前的数据库驱动架构。

## 归档原则

如果需要追溯早期设计决策，请将本文件视为“历史背景”，不要据此继续新增代码、脚本或配置。
