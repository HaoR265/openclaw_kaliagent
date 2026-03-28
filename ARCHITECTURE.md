# Kaliclaw 架构基线

**文档版本**: 2.0  
**最后更新**: 2026-03-28  
**主设计文档**: 当前仍参考历史过渡稿 [docs/history/OpenClaw-多Agent编排与Kali工具系统重构设计.md](docs/history/OpenClaw-%E5%A4%9AAgent%E7%BC%96%E6%8E%92%E4%B8%8EKali%E5%B7%A5%E5%85%B7%E7%B3%BB%E7%BB%9F%E9%87%8D%E6%9E%84%E8%AE%BE%E8%AE%A1.md)

## 文档定位

本文档描述当前仓库已经落地的正式架构基线。

说明：

- 本文档是 Kaliclaw 当前正式架构入口之一
- 仍以 `OpenClaw-*.md` 命名的设计稿，现已归档到 `docs/history/`
- 更长周期的路线、阶段工作包和旧设计背景，请按需查阅那些历史材料

## 正式基线

### 代理分工

系统包含 8 个正式代理：

- `command`: 分析、规划、委派、汇总
- `defense`: 风险解释、证据整理、防御建议
- `offense-wireless`
- `offense-recon`
- `offense-web`
- `offense-internal`
- `offense-exploit`
- `offense-social`

其中 6 个 `offense-*` 是专业化执行代理，按任务类别分工。当前 v2 迁移阶段中，数据库里的 `capability` 与既有 `category` 一一对应：

- `wireless`
- `recon`
- `web`
- `internal`
- `exploit`
- `social`

### 核心边界

- `command` 不直接执行任务
- 正式异步执行路径为 `publish.py -> SQLite/WAL -> worker.py`
- `tasks-YYYY-MM-DD.jsonl` 和 `results.jsonl` 仅保留兼容镜像/导出职责
- 旧 `agent_consumer.py` 保留兼容入口，不再作为正式主执行链
- 工具目录、recipe、policy 已进入正式架构，但仍处于最小落地阶段

## 当前正式执行链

```text
command
  -> publish.py
  -> SQLite/WAL (tasks/results/artifacts/workers)
  -> worker.py --category <capability>
  -> executor (agent_api | local_tool)
  -> results/artifacts
  -> summarize.py / status.py / command 汇总
```

### 组件说明

| 组件 | 当前职责 | 状态 |
|------|----------|------|
| `events/publish.py` | 发布任务；SQLite 与 JSONL 兼容双写 | 正式 |
| `events/worker.py` | 按类别 claim 任务、执行、回写状态 | 正式 |
| `events/db.py` | SQLite/WAL 真源与任务状态机基础接口 | 正式 |
| `events/executors/agent_api.py` | 复用现有分类 API 执行链 | 正式 |
| `events/executors/local_tool.py` | 本地工具执行、白名单、recipe 驱动 | 正式 |
| `events/policies.py` | 最小策略检查 | 正式 |
| `events/tool_registry.py` | 读取 catalog/recipe/policy | 正式 |
| `events/status.py` | 优先读取数据库统计 | 正式 |
| `events/summarize.py` | 优先读取数据库结果，兼容 `results.jsonl` | 正式 |
| `events/agent_consumer.py` | 兼容期入口 | 遗留兼容 |

## 数据内核

### SQLite/WAL

当前正式真源默认位于 `events/runtime/kaliclaw.db`。  
如果新默认数据库不存在而旧兼容库 `openclaw.db` 仍在，当前运行时会自动回退到旧库，避免最终 cutover 时直接丢失历史数据。数据库路径仍支持通过 `KALICLAW_RUNTIME_DIR`、`KALICLAW_DB_PATH`、`KALICLAW_DB_BASENAME` 覆盖。核心表包括：

- `tasks`
- `task_attempts`
- `task_dependencies`
- `results`
- `artifacts`
- `workers`

### 任务状态机

当前正式状态机口径：

```text
queued -> leased -> running -> succeeded
queued -> leased -> running -> retry_wait
queued -> leased -> running -> failed
queued -> leased -> running -> dead_letter
queued -> canceled
```

兼容层仍会把旧 JSONL 状态映射为：

- `pending -> queued`
- `processing -> running`
- `completed -> succeeded`
- `failed -> failed`

### 兼容期说明

- 任务发布仍会写入 `tasks-YYYY-MM-DD.jsonl`
- worker 在处理任务时仍会同步旧 JSONL 事件状态
- 结果仍会镜像写入 `results.jsonl`
- 这些兼容层用于平滑迁移、回溯排障和旧工具兼容，不再作为长期主真源

## 执行层

### worker

`worker.py` 负责：

- 按 `capability` claim 任务
- 维护 `leased/running/succeeded/retry_wait/dead_letter` 等状态流转
- 记录 attempt、result、artifact
- 调用对应 executor

### executor

当前已落地两类 executor：

- `agent_api`: 沿用现有按类别配置的 API 调用链
- `local_tool`: 本地工具执行，支持白名单、recipe 和 policy

### recipe 与 policy

当前工具目录系统已具备三层结构：

- `catalog`: 工具元数据
- `recipes`: 某类任务的推荐工具/参数映射
- `policies`: 风险与约束检查

本地工具执行不再强依赖手工传完整 `command`，可以按 `capability + operation` 解析 recipe。

## 运维口径

### 调度

- 正式分钟级执行入口是 `worker.py --once --category <capability>`
- 当前 crontab 已切到 `worker.py`
- `archive.py` 仍负责归档与清理

### 观测

- `status.py` 读取数据库统计与最近日志
- `summarize.py` 汇总数据库结果并兼容旧结果文件
- 结果、artifact、attempt 已可独立追踪

## 安全与约束

当前继续沿用这些硬约束：

- `command` 只分析/委派，不直接执行
- 不修改当前连接的 Wi-Fi 接口
- 无线监控必须使用 USB 适配器
- 不修改 Clash / mihomo / 代理规则 / 订阅 / 节点相关配置
- 高风险或交互式本地工具默认不纳入首批白名单

## 已退役或降级的旧路径

以下内容不再属于正式架构：

- 共享 `offense` 目录与共享工作区
- `events/consume.py` 和各工作区旧 `consume.py`
- 旧 `tasks.jsonl` 单文件路径
- 以文件锁 + `agent_consumer.py` 为核心的主执行路径

## 后续路线

后续实现细节、工作包顺序和技术路线，如需追溯历史设计，请参考：

- [docs/history/OpenClaw-多Agent编排与Kali工具系统重构设计.md](docs/history/OpenClaw-%E5%A4%9AAgent%E7%BC%96%E6%8E%92%E4%B8%8EKali%E5%B7%A5%E5%85%B7%E7%B3%BB%E7%BB%9F%E9%87%8D%E6%9E%84%E8%AE%BE%E8%AE%A1.md)
