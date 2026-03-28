# Kaliclaw

Kaliclaw 是一个独立维护的、面向 Kali 场景的多代理作战、研究与控制平台。  
项目早期参考了 OpenClaw 的部分代理交互理念，但当前仓库已经形成独立的事件驱动编排、专业能力代理、Mission/Campaign 工作流、Research Studio、Intel/Knowledge 检索与控制台体系。

## 项目定位

Kaliclaw 当前更准确的定位是：

- 事件驱动的任务执行底座
- 面向安全场景的指挥与控制平面
- 可逐步演进为专家研究平台的作战系统底座

它不是通用 coding agent 平台，也不再应被描述为 “OpenClaw 魔改版”。

## 核心能力

- 事件驱动执行：`publish.py -> SQLite/WAL -> worker.py -> results/artifacts`
- 专业能力代理：`command`、`defense` 与 6 个 `offense-*` 专业执行代理
- 控制工作台：`Mission / Campaign / Execution / Command Board / Research / Intel`
- 研究闭环：`research session -> question -> hypothesis -> experiment request -> approve -> launch`
- 工具目录：Kali 导向的 catalog / recipe / policy 结构
- 结果沉淀：execution result、artifact 与最小 knowledge writeback

## 项目来源与差异

Kaliclaw 的早期方向受 OpenClaw 启发，但当前系统已经在以下方面形成独立架构：

- 从同步调用思路转向事件驱动异步执行
- 从通用 agent 交互收束为专业能力代理分工
- 引入 `Mission / Revision / Workflow / Campaign` 这套作战对象模型
- 增加 `Research Studio`、`hypothesis`、`experiment request` 这类研究对象
- 增加 `Intel / Knowledge` 检索与最小 runtime writeback
- 增加前端控制台与审批、回看、排障、研究工作台

当前仓库现在采用 Kaliclaw（爪龙）默认运行身份，同时保留 OpenClaw 兼容层：

- 默认 CLI：`kaliclaw`
- 默认运行根目录：`~/.kaliclaw`
- 默认配置文件：`kaliclaw.json`
- 默认主数据库：`kaliclaw.db`
- `openclaw`、`~/.openclaw`、`openclaw.json`、`openclaw.db` 只保留为兼容 fallback
- 当前已支持通过 `KALICLAW_ROOT`、`KALICLAW_CLI_BIN`、`KALICLAW_CONFIG_BASENAME`、`KALICLAW_SOURCE_CONFIG_BASENAME` 覆盖这些默认值
- 运行时数据库路径也已支持通过 `KALICLAW_RUNTIME_DIR`、`KALICLAW_DB_PATH`、`KALICLAW_DB_BASENAME`、`KALICLAW_KNOWLEDGE_DB_PATH`、`KALICLAW_KNOWLEDGE_DB_BASENAME` 覆盖

兼容层仍保留，但不再代表正式品牌或默认真值。

## 当前系统架构

当前正式执行链：

```text
command
  -> publish.py
  -> SQLite/WAL (tasks/results/artifacts/workers)
  -> worker.py --category <capability>
  -> executor (agent_api | local_tool)
  -> results / artifacts / writeback
```

当前正式控制链：

```text
Mission
  -> Plan Candidate
  -> Revision
  -> Launch
  -> Workflow
  -> Campaign
  -> Execution / Command Board / Research
```

## 当前主要模块

| 模块 | 作用 | 当前状态 |
|------|------|----------|
| `events/` | 事件队列、worker、结果真源、最小研究对象 | 可用 |
| `dashboard-ui/` | 正式 React 控制台 | 可用 |
| `dashboard/` | 控制台后端与旧静态回退 | 可用 |
| `agent-kits/` | 工具目录、recipe、policy | 可用 |
| `events/knowledge/` | 最小知识检索与写回 | 骨架完成 |
| `Research Studio` | 研究会话、假设、实验请求 | v1 最小闭环 |

## 快速开始

下面这组命令按 Kaliclaw（爪龙）默认运行身份编写：默认 CLI 为 `kaliclaw`，默认根目录为 `~/.kaliclaw`。

如果你当前还在旧兼容目录运行，先参考 [docs/reference/migrate-from-openclaw.md](docs/reference/migrate-from-openclaw.md) 和 [kaliclaw.env.example](kaliclaw.env.example)。

### 1. 基础状态检查

```bash
kaliclaw gateway status
kaliclaw agents list
cd ~/.kaliclaw/events && python3 status.py
```

### 2. 启动正式控制台

成品构建版：

```bash
cd ~/.kaliclaw && python3 dashboard/server.py --host 127.0.0.1 --port 8787
```

然后打开：

```text
http://127.0.0.1:8787
```

开发模式：

```bash
cd ~/.kaliclaw && python3 dashboard/server.py --host 127.0.0.1 --port 8787
```

另开一个终端：

```bash
cd ~/.kaliclaw/dashboard-ui && npm run dev -- --host 127.0.0.1 --port 5173
```

然后打开：

```text
http://127.0.0.1:5173
```

### 3. 发布测试任务

```bash
cd ~/.kaliclaw/events && python3 publish.py \
  --type task \
  --task port-scan \
  --category recon \
  --params '{"target":"127.0.0.1","ports":"22,80,443"}'
```

### 4. 进入研究模式

打开 `Research Studio` 后，可以直接完成：

- 创建 research session
- 添加 research question
- 生成 hypothesis
- 保存 skeptic review
- 创建 experiment request
- approve / launch 到执行面

### 5. 从 OpenClaw 兼容版迁移

当你要把旧兼容目录迁到 Kaliclaw 默认目录时，先跑迁移脚本：

```bash
cd ~/.openclaw && scripts/migrate_to_kaliclaw.sh --dry-run
cd ~/.openclaw && scripts/migrate_to_kaliclaw.sh

# 迁移完成后检查新的默认运行根
~/.kaliclaw/scripts/check_kaliclaw_runtime.sh ~/.kaliclaw
```

如果你只需要把旧 `openclaw.json` 转成新的 `kaliclaw.json`，也可以直接运行：

```bash
KALICLAW_SOURCE_ROOT="$HOME/.openclaw" \
KALICLAW_ROOT="$HOME/.kaliclaw" \
KALICLAW_SOURCE_CONFIG_BASENAME=openclaw.json \
KALICLAW_CONFIG_BASENAME=kaliclaw.json \
python3 update_workspaces.py
```

迁移脚本和配置规范脚本现在都支持兼容 source -> Kaliclaw target 的写法。回滚说明见 [docs/reference/final-cutover-rollback.md](docs/reference/final-cutover-rollback.md)。

这些脚本会一起规范：

- agent `workspace`
- agent `agentDir`
- `tools.exec.pathPrepend`

## 文档入口

当前正式入口：

1. [ARCHITECTURE.md](ARCHITECTURE.md)
2. [DOCUMENTATION.md](DOCUMENTATION.md)
3. [docs/README.md](docs/README.md)
4. [CONTRIBUTING.md](CONTRIBUTING.md)
5. [CHANGELOG.md](CHANGELOG.md)

当前已归档一批以 `OpenClaw-*.md` 命名的历史或过渡期设计文档。  
它们现在已经归档到 [docs/history/README.md](docs/history/README.md)，只应被视为历史/参考材料，而不是当前正式品牌入口。

## 当前状态

当前仓库已经具备较强的控制面和执行面，但仍处于“独立化迁移 + 研究面补完”阶段。

已形成的正式基线：

- 事件驱动任务内核
- 专业能力代理分工
- Mission / Campaign / Execution / Command Board / Research 控制台
- 最小 research plane 和最小 knowledge writeback

仍在迁移或待补完：

- 兼容层与剩余旧说明清理
- 路径、CLI、配置名与数据库名参数化
- 更成熟的 knowledge / research plane
- 更系统的测试与对外发布整理

## 贡献方式

请先阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。

当前最重要的贡献规则：

- 不要粗暴全局替换 `OpenClaw/openclaw`
- 品牌层、归因层、兼容层、历史层必须分开处理
- 新代码不得再把 OpenClaw 当作正式品牌
- 涉及兼容项时优先参数化，而不是直接改炸运行环境
- 所有改动都要同步更新文档和 [CHANGELOG.md](CHANGELOG.md)

## 许可证与致谢

已核实的事实：

- 当前仓库根目录还没有正式 `LICENSE` 文件
- 本地已安装的 upstream `openclaw` 包声明为 `MIT`

因此当前 README 只保留事实性说明，不继续使用“遵循原项目许可证条款”这类模糊表述。  
正式许可证文件与上游关系说明会在后续独立化轮次里单独收口。

致谢与来源说明：

- Kaliclaw 的早期方向受 OpenClaw 启发
- 本项目在演化过程中参考了上游的一些代理交互理念
- 当前实现、控制台、研究闭环与文档体系由本仓库独立维护并持续演进
