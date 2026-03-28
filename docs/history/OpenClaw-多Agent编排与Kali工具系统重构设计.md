# OpenClaw - 多Agent编排与Kali工具系统重构设计

**版本**: 0.1  
**日期**: 2026-03-28  
**状态**: 草案，可作为后续修改总蓝图  
**定位**: 面向未来阶段的统一方案，整合 C 方案队列内核升级与 Kali 工具目录系统升级  

> 边界说明：本文件后续主要负责“任务内核 / worker-executor / tool catalog-recipe-policy / 编排底座”。  
> 与前端控制台、`commander/analyst`、自动化托管模式相关的新板块，已单独拆到 [OpenClaw-智能指挥与作战控制系统设计.md](/home/asus/.openclaw/docs/history/OpenClaw-智能指挥与作战控制系统设计.md)。  
> 与知识库、经验记忆、情报整理、研究分析相关的新板块，已单独拆到 [OpenClaw-情报、记忆与研究分析设计.md](/home/asus/.openclaw/docs/history/OpenClaw-情报、记忆与研究分析设计.md)。

---

## 1. 文档目的

本文档用于替代“继续在当前 `JSONL + cron + 文件锁` 内核上叠加高级功能”的思路，给出一个更稳定、可演进的统一架构方案。

本文档的目标不是推翻当前 OpenClaw C 方案，而是明确：

1. 哪些现有设计应该保留
2. 哪些现有设计只适合阶段一，不适合继续作为长期底座
3. 后续所有阶段应围绕什么样的统一内核演进
4. 工具目录系统如何从“静态目录”升级为“能力注册表”
5. 后续代码修改应先改哪里、后改哪里

---

## 2. 核心结论

### 2.1 应保留的部分

以下结构应保留，不应回退：

- 8 个正式代理结构：`command`、`defense`、6 个 `offense-*`
- `command` 只分析、规划、委托，不直接执行
- `defense` 负责防御、证据、风险解释
- `offense-*` 负责专业化执行
- 异步任务模式
- Kali 工具目录系统
- 独立工作区结构

### 2.2 应替换的部分

以下结构不应继续作为长期内核：

- 以 `tasks-YYYY-MM-DD.jsonl` 为主真源的任务状态存储
- 通过整文件读取/整文件重写的状态更新方式
- 以 cron 轮询为主的正式 worker 生命周期管理
- 以 `agent="offense"` + `category=*` 为核心的事件寻址方式
- 只靠文档约束而不是机器可执行约束的工具执行模型
- 只靠 `results.jsonl` 追加的结果审计和检索方式

### 2.3 总体设计判断

当前实现适合：

- 阶段一验证
- 单机低并发
- 人工排障
- 简单任务链路验证

当前实现不适合继续直接承载：

- 优先级调度
- 工作流依赖
- 复杂重试/超时回收
- 可观测性增强
- 记忆切片/知识抽取
- 多 worker / 多节点扩展

---

## 3. 统一目标架构

### 3.1 分层结构

```
用户/会话
   ↓
command 编排层
   ↓
任务内核层（SQLite/WAL）
   ↓
worker 执行层（defense / offense-*）
   ↓
executor 适配层（API / 本地工具 / 混合执行）
   ↓
工具能力层（catalog + recipes + policies）
   ↓
结果与制品层（results + artifacts + summaries）
   ↓
观测层（logs + metrics + dashboard + webhook）
```

### 3.2 设计原则

1. `command` 仍然是编排者，不是执行者
2. 正式状态必须有事务性真源
3. 异步任务应具备可恢复、可重试、可追踪能力
4. 工具目录必须升级为可执行的能力目录
5. 约束必须机器可执行，而不是只写在文档里
6. 工作流、记忆、监控都应建立在统一任务内核之上

---

## 4. 保留层与替换层

### 4.1 保留层

| 层 | 保留内容 | 说明 |
|---|---|---|
| 代理层 | 8 个正式代理 | 保持当前角色边界 |
| 工作区层 | 独立 `workspaces/*` | 保持隔离 |
| 工具层 | `agent-kits/` 目录体系 | 保留 catalog 思路 |
| 异步层 | 发布任务 -> 消费任务 -> 回传结果 | 保留异步模型 |
| 约束层 | 无线保护、代理保护、工具限制 | 保留约束目标 |

### 4.2 替换层

| 现状 | 目标 |
|---|---|
| `JSONL` 任务主存储 | `SQLite + WAL` |
| cron 轮询 | 长驻 worker + supervisor/systemd |
| 文档式约束 | policy 驱动约束 |
| 静态工具清单 | 可执行能力注册表 |
| `results.jsonl` 单文件 | `results + artifacts + summaries` |
| `agent/category/task` 混合寻址 | `capability/operation/policy` 模型 |

---

## 5. 任务内核 v2 设计

### 5.1 存储选择

建议使用：

- 主存储：`SQLite`
- 模式：`WAL`
- 归档：保留 `JSONL` 导出/压缩，仅作为历史审计格式，不再作为主真源

原因：

- 单机足够稳定
- 有事务和锁语义
- 易调试
- 易做状态查询
- 比 Redis/RabbitMQ 更适合当前阶段的“可审计任务编排”

### 5.2 数据库文件位置

建议新增：

- `events/runtime/openclaw.db`
- `events/runtime/migrations/`

### 5.3 核心表设计

#### `tasks`

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | TEXT PK | 任务唯一 ID |
| `workflow_id` | TEXT | 所属工作流 |
| `parent_task_id` | TEXT NULL | 父任务 |
| `correlation_id` | TEXT | 同一轮分析或同一目标链路的追踪 ID |
| `capability` | TEXT | 能力域，如 `recon` / `web` / `defense.evidence` |
| `operation` | TEXT | 具体操作，如 `port_scan` / `dir_brute` |
| `requested_by` | TEXT | 谁发起：`command` / `defense` / user |
| `target_agent` | TEXT NULL | 可选的硬指定代理 |
| `state` | TEXT | `queued` / `leased` / `running` / `succeeded` / `retry_wait` / `dead_letter` / `canceled` |
| `priority` | INTEGER | 建议 0-100，数字越大优先级越高 |
| `payload_json` | TEXT | 请求载荷 |
| `policy_ref` | TEXT NULL | 约束策略引用 |
| `idempotency_key` | TEXT NULL | 幂等键 |
| `schedule_at` | TEXT NULL | 延迟执行时间 |
| `lease_owner` | TEXT NULL | 当前 lease 所属 worker |
| `lease_expires_at` | TEXT NULL | lease 到期时间 |
| `attempt_count` | INTEGER | 当前已尝试次数 |
| `max_attempts` | INTEGER | 最大尝试次数 |
| `timeout_seconds` | INTEGER | 单次执行超时 |
| `last_error_code` | TEXT NULL | 最近错误码 |
| `last_error_message` | TEXT NULL | 最近错误摘要 |
| `created_at` | TEXT | 创建时间 |
| `started_at` | TEXT NULL | 首次开始时间 |
| `completed_at` | TEXT NULL | 最终完成时间 |

#### `task_attempts`

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | TEXT PK | attempt ID |
| `task_id` | TEXT FK | 对应任务 |
| `worker_id` | TEXT | 执行 worker |
| `executor_type` | TEXT | `agent_api` / `local_tool` / `hybrid` |
| `tool_name` | TEXT NULL | 主要使用工具 |
| `started_at` | TEXT | 开始时间 |
| `ended_at` | TEXT NULL | 结束时间 |
| `outcome` | TEXT | `success` / `failed` / `timeout` / `canceled` |
| `exit_code` | INTEGER NULL | 本地工具退出码 |
| `error_code` | TEXT NULL | 错误码 |
| `error_message` | TEXT NULL | 错误详情 |
| `raw_output_ref` | TEXT NULL | 原始输出引用 |

#### `task_dependencies`

| 字段 | 类型 | 说明 |
|---|---|---|
| `task_id` | TEXT FK | 当前任务 |
| `depends_on_task_id` | TEXT FK | 依赖任务 |
| `dependency_type` | TEXT | `success_required` / `completion_required` |

#### `results`

| 字段 | 类型 | 说明 |
|---|---|---|
| `task_id` | TEXT PK/FK | 结果对应任务 |
| `status` | TEXT | `succeeded` / `failed` / `partial` |
| `summary_json` | TEXT | 面向 `command` 的结构化摘要 |
| `structured_json` | TEXT | 规范化结构化结果 |
| `created_at` | TEXT | 写入时间 |

#### `artifacts`

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | TEXT PK | artifact ID |
| `task_id` | TEXT FK | 所属任务 |
| `kind` | TEXT | `log` / `pcap` / `scan_xml` / `html` / `json` 等 |
| `path` | TEXT | 本地路径 |
| `mime_type` | TEXT | MIME |
| `size_bytes` | INTEGER | 文件大小 |
| `sha256` | TEXT NULL | 完整性校验 |
| `created_at` | TEXT | 创建时间 |

#### `workers`

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | TEXT PK | worker ID |
| `agent_id` | TEXT | 代理标识 |
| `capabilities_json` | TEXT | 可处理能力列表 |
| `hostname` | TEXT | 当前主机 |
| `pid` | INTEGER | 进程号 |
| `last_heartbeat_at` | TEXT | 最近心跳时间 |
| `status` | TEXT | `online` / `offline` / `draining` |

### 5.4 任务状态机

建议正式状态机如下：

```
queued
  -> leased
  -> running
  -> succeeded

running
  -> failed
  -> retry_wait
  -> dead_letter
  -> canceled

retry_wait
  -> queued

leased
  -> queued        (lease 过期回收)
  -> running
```

### 5.5 worker 抢占/执行流程

1. worker 注册自身能力并写心跳
2. worker 在事务中查询可执行任务
3. 按 `priority DESC, created_at ASC` 选任务
4. 成功 claim 后写入 `lease_owner` 和 `lease_expires_at`
5. 状态转为 `leased`
6. 真正开始执行时转为 `running`
7. 执行完成后落 attempt、result、artifact
8. 成功则 `succeeded`
9. 失败时根据策略进入 `retry_wait` 或 `dead_letter`
10. supervisor 负责常驻 worker 生命周期，cron 不再负责主执行

### 5.6 结果与制品

结果层必须拆开：

- `summary_json`: 给 `command` 读的摘要
- `structured_json`: 给程序、工作流、记忆层读的结构化结果
- `artifacts`: 原始文件、原始 stdout/stderr、抓包、报告等

不要继续把全部结果都塞在一个 `results.jsonl` 里。

---

## 6. 工具目录系统 v2 设计

### 6.1 设计目标

当前工具目录系统已经具备：

- 工具分类
- 工具搜索
- 基本说明
- 特殊工具分组
- 无线安全约束脚本

下一步目标不是继续堆工具名，而是把它升级成：

**工具注册表 + 能力配方层 + 约束策略层**

### 6.2 目录结构建议

建议在 `agent-kits/` 下新增：

```
agent-kits/
├── schema/
│   ├── tool-catalog.v2.schema.json
│   ├── recipe.v1.schema.json
│   └── policy.v1.schema.json
├── recipes/
│   ├── recon.port-scan.json
│   ├── web.dir-brute.json
│   ├── web.fingerprint.json
│   └── wireless.passive-scan.json
├── policies/
│   ├── common-safe.json
│   ├── wireless-usb-only.json
│   └── proxy-protected.json
└── validators/
    └── validate_catalog.py
```

### 6.3 catalog v2 字段建议

每个工具条目建议支持以下字段：

| 字段 | 必需 | 说明 |
|---|---|---|
| `id` | 是 | 稳定 ID，如 `tool.nmap` |
| `name` | 是 | 展示名 |
| `category` | 是 | 逻辑分类 |
| `bin` | 是 | 可执行文件 |
| `summary` | 是 | 简介 |
| `aliases` | 否 | 常见别名 |
| `tags` | 否 | 检索标签 |
| `protocols` | 否 | 如 `http`, `dns`, `smb` |
| `target_types` | 否 | 如 `host`, `cidr`, `url`, `domain`, `binary` |
| `requires_sudo` | 否 | 是否需要 sudo |
| `requires_network` | 否 | 是否需要主动网络访问 |
| `interactive` | 否 | 是否交互式 |
| `read_only` | 否 | 是否只读 |
| `destructive` | 否 | 是否可能破坏状态 |
| `risk_level` | 否 | `low` / `medium` / `high` |
| `stealth_level` | 否 | `low-noise` / `normal` / `loud` |
| `supports_json_output` | 否 | 是否支持结构化输出 |
| `default_timeout_seconds` | 否 | 默认超时 |
| `install_check` | 否 | 可用性检查命令 |
| `version_command` | 否 | 版本检测命令 |
| `wrapper` | 否 | 包装器脚本 |
| `parser` | 否 | 输出解析器 |
| `artifact_kinds` | 否 | 可能产出的制品 |
| `policy_refs` | 否 | 关联策略 |
| `example_args` | 否 | 示例参数 |
| `notes` | 否 | 运行提示 |

### 6.4 catalog v2 示例

```json
{
  "id": "tool.nmap",
  "name": "nmap",
  "category": "recon",
  "bin": "nmap",
  "summary": "host and service enumeration",
  "aliases": ["network mapper"],
  "tags": ["port-scan", "service-detect", "recon"],
  "protocols": ["tcp", "udp", "ip"],
  "target_types": ["host", "cidr"],
  "requires_sudo": false,
  "requires_network": true,
  "interactive": false,
  "read_only": true,
  "destructive": false,
  "risk_level": "low",
  "stealth_level": "normal",
  "supports_json_output": false,
  "default_timeout_seconds": 900,
  "install_check": "command -v nmap",
  "version_command": "nmap --version",
  "wrapper": "oc-run-nmap",
  "parser": "parsers.nmap_xml",
  "artifact_kinds": ["scan-xml", "stdout-log"],
  "policy_refs": ["common-safe"],
  "example_args": ["-sS", "-sV", "-Pn"],
  "notes": "Prefer XML output for structured parsing"
}
```

### 6.5 recipe 层

仅有工具目录还不够，需要配方层。

#### recipe 示例字段

| 字段 | 说明 |
|---|---|
| `id` | `recipe.recon.port-scan` |
| `capability` | `recon` |
| `operation` | `port_scan` |
| `primary_tool` | 主工具 |
| `fallback_tools` | 备选工具 |
| `allowed_tools` | 允许工具白名单 |
| `input_schema` | 输入参数定义 |
| `arg_mapping` | 参数到命令行映射 |
| `output_parser` | 结果解析器 |
| `artifact_rules` | 产生哪些制品 |
| `policy_refs` | 必须满足的策略 |

#### recipe 示例

```json
{
  "id": "recipe.recon.port-scan",
  "capability": "recon",
  "operation": "port_scan",
  "primary_tool": "tool.nmap",
  "fallback_tools": ["tool.masscan"],
  "allowed_tools": ["tool.nmap", "tool.masscan"],
  "input_schema": {
    "target": {"type": "string", "required": true},
    "ports": {"type": "string", "required": false},
    "speed": {"type": "string", "required": false}
  },
  "arg_mapping": {
    "target": {"position": 0},
    "ports": {"flag": "-p"},
    "speed": {"flag": "--min-rate"}
  },
  "output_parser": "parsers.nmap_xml",
  "artifact_rules": ["scan-xml", "stdout-log"],
  "policy_refs": ["common-safe"]
}
```

### 6.6 policy 层

policy 必须被独立出来，不能继续散落在多个文档里。

建议 policy 至少支持：

- 是否允许主动网络访问
- 是否允许修改本机网络状态
- 是否允许使用当前 Wi-Fi 接口
- 是否要求 USB Wi-Fi 适配器
- 是否要求 sudo
- 是否允许交互式工具
- 是否允许破坏性操作
- 是否允许访问代理/代理配置

### 6.7 双模式执行档位

系统应长期支持两种执行档位：

1. `steady`
   - 默认档位
   - 保留完整 policy、result、artifact、attempt 记录
   - 适合常规运行、长期维护、赛后复盘

2. `rush`
   - 冲刺档位
   - 只跳过非关键治理层，不改变总分 agent 结构和类别分工
   - 允许减少非必要整理、兼容写入和冗余日志
   - 对高风险或交互式工具，必须显式二次确认后才允许执行

建议任务参数统一支持：

- `executionProfile = steady | rush`
- `secondaryConfirmation = true | false`
- `interactive = true | false`

其中 `rush` 不是“无约束模式”，只是在关键时刻压缩流程。

#### 推荐切换方式

1. 默认保持 `steady`
2. 关键时刻只对单任务切到 `rush`
3. 高风险或交互式工具必须同时满足：
   - `executionProfile = rush`
   - `secondaryConfirmation = true`
   - 必要时显式标记 `interactive = true`

#### 冲刺任务示例

```bash
cd ~/.openclaw/events && python3 publish.py \
  --type assess \
  --task passive-scan \
  --category wireless \
  --execution-profile rush \
  --secondary-confirmation \
  --interactive \
  --params '{"executionMode":"local_tool","tool":"aircrack-ng","command":"aircrack-ng --help"}'
```

#### 工具检索示例

```bash
oc-toolfind all --profile steady recon
oc-toolfind all --profile rush --special-only
oc-toolfind all aircrack --profile rush
```

### 6.8 无线约束口径

无线能力域的正式约束收敛为：

- 严格不修改当前连接的内置 Wi-Fi 接口
- 允许对外置 USB 无线网卡执行监控、注入和相关审计动作
- 无线攻击与无线工具在授权内网环境中允许纳入正式能力范围
- 如果工具被标记为高风险或交互式，则在 `rush` 档位下仍需二次确认

#### `wireless-usb-only` 策略示意

```json
{
  "id": "wireless-usb-only",
  "requires_usb_wifi": true,
  "forbid_connected_wifi_modification": true,
  "allow_monitor_mode": true,
  "requires_wrapper": "oc-mon0"
}
```

---

## 7. agent 与工具目录的结合方式

### 7.1 统一寻址模型

未来发布任务时不再优先用：

- `agent = offense`
- `category = recon`
- `task = port-scan`

而是优先用：

- `capability = recon`
- `operation = port_scan`
- `policy_ref = common-safe`

`target_agent` 只保留为特殊场景可选字段。

### 7.2 `command` 的职责

`command` 应该：

1. 识别目标和任务意图
2. 选择能力域
3. 查询 catalog + recipe
4. 发布结构化任务
5. 汇总结构化结果

`command` 不应直接决定某个具体二进制命令行，除非处于调试模式。
在 `rush` 档位下，`command` 可以缩短推理链，但仍不应突破类别边界和最小状态记录。

#### 7.2.1 `command` 的未来拆分方向

当前阶段保持单一 `command` 足够，但后续如果自然语言讨论、方案分析、任务编排和跨模块协调持续变重，建议拆成两个并排协作角色：

1. `commander`
   - 面向用户自然语言输入
   - 负责识别意图、组织对话、协调模块输出
   - 负责最终拍板任务编排与发布
   - 负责协调 offense / defense / toolchain 的整体节奏

2. `analyst`
   - 偏研究与分析
   - 负责收集情报、读取结果、关联历史数据
   - 负责从未来知识库中检索经典打法、场景思路、技术方案
   - 负责给 `commander` 提供候选作战路径、前提条件和推理支撑

拆分后仍保持原则：

- `commander` 不直接执行
- `analyst` 不直接执行
- 最终仍由 `commander -> task kernel -> workers` 发布与驱动
- 前端上两者应当并排展示，便于一边讨论、一边看分析结论
- `analyst` 可以长时间占用在分析、检索、归纳上，而不阻塞 `commander` 对用户输入和现场指令的快速响应
- 角色拆分的一个核心动因，就是避免“用户正在下达新命令时，分析线程还卡在资料检索或长链推理中”

### 7.3 `offense-*` 的职责

每个 `offense-*` worker：

1. 只消费自己能力域内的任务
2. 根据 recipe 选择工具和包装器
3. 执行 policy 检查
4. 运行 executor
5. 写入 attempt / result / artifact

### 7.4 `defense` 的职责

`defense` 不应只是旁路说明代理，还应正式支持能力域，例如：

- `defense.surface_review`
- `defense.evidence_extract`
- `defense.risk_assess`
- `defense.mitigation_plan`

---

## 8. executor 适配层

### 8.1 executor 类型

建议统一成三类：

1. `agent_api`
   - 由模型或代理 API 直接返回结构化结果

2. `local_tool`
   - 由本地 Kali 工具实际执行

3. `hybrid`
   - 先本地执行，再由模型做结构化解释或总结

### 8.2 推荐模块布局

建议新增：

```
events/
├── db.py
├── migrations/
├── dispatcher.py
├── worker.py
├── retry.py
├── policies.py
├── executors/
│   ├── base.py
│   ├── agent_api.py
│   ├── local_tool.py
│   └── hybrid.py
├── parsers/
│   ├── nmap_xml.py
│   ├── ffuf_json.py
│   └── generic_stdout.py
└── artifacts.py
```

### 8.3 executor 输入输出契约

#### 输入

```json
{
  "task_id": "uuid",
  "capability": "recon",
  "operation": "port_scan",
  "payload": {},
  "recipe": {},
  "policy": {},
  "context": {
    "workflow_id": "uuid",
    "correlation_id": "uuid"
  }
}
```

#### 输出

```json
{
  "status": "success|failed|partial",
  "summary": {},
  "structured_result": {},
  "artifacts": [],
  "metrics": {
    "duration_ms": 1234
  },
  "error": null
}
```

---

## 9. 观测层设计

### 9.1 日志

日志应逐步从“类别纯文本日志”迁移到“结构化日志”：

- `worker_id`
- `task_id`
- `attempt_id`
- `capability`
- `operation`
- `executor_type`
- `status`
- `duration_ms`
- `error_code`

### 9.2 指标

至少需要：

- 队列深度
- 平均等待时长
- 平均执行时长
- 成功率
- 重试率
- dead letter 数
- 每类能力的吞吐量

### 9.3 通知和面板

Webhook 和 dashboard 不应该先做。

正确顺序是：

1. 先有事务性状态源
2. 再从状态源派生通知和面板

---

## 10. 记忆系统与知识层

### 10.1 不建议过早引入图数据库

在没有稳定结构化结果前：

- 知识图谱容易沦为概念堆叠
- 维护成本高
- 真实收益不确定

### 10.2 正确顺序

1. 先把 `results.structured_json` 做稳定
2. 再做实体抽取
3. 再做检索索引
4. 只有在真实查询需求强烈时，再考虑图关系层

### 10.3 记忆层建议

可以先支持：

- 目标历史
- 服务历史
- 漏洞历史
- 凭据历史
- 操作证据历史

这些都应来源于结构化结果，不应直接来源于原始日志堆。

---

## 11. 分布式扩展判断

### 11.1 当前阶段不建议直接迁移到 Redis/RabbitMQ

当前最大问题是任务状态与执行内核不够扎实，不是消息吞吐不够。

### 11.2 推荐扩展路线

1. 先 `SQLite/WAL`
2. 再 `Postgres`
3. 只有在跨节点吞吐或异步广播需求很强时，再评估消息队列

如果未来进入多节点阶段，优先保持：

- 状态在数据库
- broker 只负责运输，不负责成为唯一真源

---

## 12. 迁移路线图

### 阶段 A：基线校正

目标：

- 清理明文密钥
- 让旧实施计划文档退居历史参考
- 明确 v2 是未来正式路线图

交付物：

- 新设计文档
- 文档导航更新
- 旧规划文档状态说明

### 阶段 B：任务内核重建

目标：

- 上线 SQLite 真源
- 建立 tasks/attempts/results/artifacts 模型
- 引入 lease 和 retry

交付物：

- `events/db.py`
- 初始化 migration
- 新 `worker.py`
- 新 `dispatcher.py`

### 阶段 C：工具目录 v2

目标：

- 引入 catalog v2 schema
- 新增 recipe/policy/validator
- 让 catalog 可驱动执行

交付物：

- `agent-kits/schema/*.json`
- `agent-kits/recipes/*.json`
- `agent-kits/policies/*.json`
- catalog validator

### 阶段 D：工作流编排

目标：

- 支持 `workflow_id`
- 支持 task dependency
- 支持 fan-out / fan-in

交付物：

- `task_dependencies`
- 调度器依赖检查
- `command` 汇总逻辑适配

### 阶段 E：观测与通知

目标：

- 结构化日志
- dashboard
- webhook

交付物：

- metrics 导出
- 统一状态页面
- 通知配置

### 阶段 F：记忆与扩展

目标：

- 结构化记忆
- 检索与实体关联
- 视需求进入多节点

阶段 F 当前只作为后续正式计划入口，不在本轮实现中提前落地知识库。

建议在该阶段内进一步拆出三个子方向：

1. `F-1` 经验与情报记忆
   - 记录比赛中的攻击经验、分析经验、场景拆解
   - 整理最新公开情报、常见进攻思路、优秀攻击链路样例
   - 供 `analyst` 检索与归纳，不直接替代当前任务内核

2. `F-2` 角色拆分
   - 将现有 `command` 拆成 `commander + analyst`
   - `commander` 主对话与任务编排
   - `analyst` 主情报检索、知识归纳、方案支撑
   - 前端将两者做成并排工作台

3. `F-3` 模式扩展
   - 在现有 `steady / rush` 之外，规划 `defense` 模式开关
   - `defense` 模式先从周期性本地扫描、状态巡检开始
   - 后续再视需要扩展到主动防御能力

其中：

- `rush` 的未来增强方向可以包括“目标驱动的自动化托管模式”
- 这种模式不等于普通 `rush`，也不等于简单放宽策略；它更接近“用户只给阶段性目标，系统持续自行规划、尝试和推进”
- 该模式必须保留严格日志、完整过程记录和清晰的高风险工具授权边界
- 进入该模式前，应弹出高风险/特殊/冷门工具授权清单，由用户勾选批准哪些工具可自动纳入尝试范围
- 未被勾选批准的高风险工具，即使在自动化托管模式下也不得使用
- `defense` 模式目前只进入路线图，不在本轮正式实现

---

## 13. 对现有代码的修改映射

### 13.1 优先替换/新增

| 类型 | 路径建议 | 说明 |
|---|---|---|
| 新增 | `events/db.py` | 统一数据库访问 |
| 新增 | `events/migrations/001_init.sql` | 初始 schema |
| 新增 | `events/worker.py` | 正式 worker 主入口 |
| 新增 | `events/dispatcher.py` | 任务发布与路由 |
| 新增 | `events/policies.py` | 策略检查 |
| 新增 | `events/executors/*` | executor 层 |
| 新增 | `events/parsers/*` | 工具输出解析器 |
| 新增 | `agent-kits/schema/*` | schema 定义 |
| 新增 | `agent-kits/recipes/*` | 能力配方 |
| 新增 | `agent-kits/policies/*` | 机器可执行约束 |

### 13.2 需要逐步改造

| 现有文件 | 改造方向 |
|---|---|
| `events/publish.py` | 从写 `JSONL` 改为写数据库任务 |
| `events/agent_consumer.py` | 逐步退役，逻辑拆到 `worker.py` / executors |
| `events/status.py` | 改为直接查询数据库和 metrics |
| `events/summarize.py` | 改为读取 `results` + `artifacts` |
| `events/EVENT_PROTOCOL.md` | 改写为 v2 任务协议 |
| `agent-kits/common/bin/oc-toolfind` | 支持 catalog v2 字段和 recipe 搜索 |
| `agent-kits/common/bin/oc-toolcat` | 支持 schema-aware 输出 |

### 13.3 需要废弃的定位

以下内容在 v2 下只保留迁移兼容意义：

- `tasks-YYYY-MM-DD.jsonl` 作为正式任务真源
- `results.jsonl` 作为唯一结果真源
- 以 cron 为正式主执行入口

---

## 14. 验收标准

当以下条件满足时，可认为 v2 基本可用：

1. 跨天未完成任务不会丢失
2. 一个任务的状态流转可以事务性追踪
3. retry / dead letter 行为可验证
4. worker 异常退出后任务可回收
5. `command` 可以按 `workflow_id` 汇总任务链路
6. tool catalog 可以通过 schema 校验
7. 常见工具任务可通过 recipe 自动选择工具并产出结构化结果
8. 关键约束可通过 policy 自动阻止违规执行

---

## 15. 实施建议

建议后续修改顺序严格按以下顺序进行：

1. 先落数据库真源与状态机
2. 再落 worker / executor
3. 再落 catalog v2 / recipe / policy
4. 再改 `command` 的发布和汇总逻辑
5. 再做 dashboard / webhook
6. 最后才做记忆与扩展

不要反过来做：

- 不要先做可视化
- 不要先做知识图谱
- 不要先做分布式消息队列
- 不要继续在 `JSONL` 主真源上叠加复杂调度

---

## 16. 结语

本方案的核心不是“更复杂”，而是“把未来所有阶段建立在一个可演进的统一内核上”。

未来应保留：

- 多 agent
- 总分工结构
- Kali 工具目录
- 异步任务模式

未来应升级：

- 任务内核
- 工具目录 schema
- 约束执行方式
- 结果与制品模型

本文件可作为后续所有修改任务的总蓝图使用。

---

## 17. 第一批实施任务清单

本节用于把蓝图直接拆成可执行的改造包。建议后续开发按以下 work package 推进。

### WP-1: 建立数据库真源骨架

**目标**:

- 建立 `SQLite/WAL` 运行时真源
- 不立即删除现有 `JSONL`，先允许双读阶段存在

**新增文件建议**:

- `events/db.py`
- `events/migrations/001_init.sql`
- `events/runtime/.gitkeep`

**修改文件建议**:

- `events/publish.py`
- `events/status.py`

**交付要求**:

- `db.py` 提供连接、事务、基础查询接口
- 初始 migration 建出 `tasks`、`task_attempts`、`results`、`artifacts`、`workers`
- `publish.py` 支持向数据库发布任务
- `status.py` 支持优先读取数据库状态

**验证标准**:

- 可发布新任务到数据库
- `status.py` 能显示数据库中的待处理任务数
- 数据库在 WAL 模式下可正常打开

### WP-2: 建立 worker/lease 状态机

**目标**:

- 用数据库 lease 取代文件锁抢占
- 形成正式状态机

**新增文件建议**:

- `events/worker.py`
- `events/dispatcher.py`
- `events/retry.py`

**修改文件建议**:

- `events/agent_consumer.py`
- `events/EVENT_PROTOCOL.md`

**交付要求**:

- `worker.py` 支持按能力域 claim 任务
- lease 过期可回收
- 失败任务可进入 `retry_wait`
- 超限任务进入 `dead_letter`

**验证标准**:

- 同类两个 worker 不会重复拿到同一个任务
- worker 异常退出后任务可重新被 claim
- retry / dead letter 可被测试脚本复现

### WP-3: executor 适配层落地

**目标**:

- 把任务执行从消费者脚本里拆出来
- 统一 API、本地工具、混合执行模型

**新增文件建议**:

- `events/executors/base.py`
- `events/executors/agent_api.py`
- `events/executors/local_tool.py`
- `events/executors/hybrid.py`

**交付要求**:

- executor 接口统一输入输出
- `worker.py` 不直接拼命令或直连模型 API
- 执行结果统一写入 `results` / `artifacts`

**验证标准**:

- 至少一个 API 类任务和一个本地工具任务可通过统一 executor 跑通
- 结果对象结构一致

### WP-4: catalog v2 schema 与 validator

**目标**:

- 把工具目录从静态清单升级为可校验 schema

**新增文件建议**:

- `agent-kits/schema/tool-catalog.v2.schema.json`
- `agent-kits/schema/recipe.v1.schema.json`
- `agent-kits/schema/policy.v1.schema.json`
- `agent-kits/validators/validate_catalog.py`

**修改文件建议**:

- `agent-kits/offense-kit/catalog/front-tools.json`
- `agent-kits/defense-kit/catalog/front-tools.json`
- `agent-kits/cmd-special/catalog/rare-tools.json`

**交付要求**:

- catalog 条目新增 v2 必需字段
- validator 可检查字段完整性和枚举合法性
- 文档中列出的关键工具先完成升级

**验证标准**:

- 所有 catalog 文件通过 validator
- `oc-toolfind` 仍可正常返回结果

### WP-5: recipe / policy 层落地

**目标**:

- 让工具目录可以真正驱动执行

**新增文件建议**:

- `agent-kits/recipes/recon.port-scan.json`
- `agent-kits/recipes/web.dir-brute.json`
- `agent-kits/recipes/wireless.passive-scan.json`
- `agent-kits/policies/common-safe.json`
- `agent-kits/policies/wireless-usb-only.json`
- `agent-kits/policies/proxy-protected.json`

**交付要求**:

- 至少为 `recon`、`web`、`wireless` 各落一个 recipe
- `wireless-usb-only` 可在执行前自动检查
- worker 能按 recipe 选择 primary/fallback 工具

**验证标准**:

- `command` 发布能力任务后，worker 能基于 recipe 自动选工具
- 违规策略会被阻断而不是写在文档里等人自觉遵守

### WP-6: 命令行工具升级

**目标**:

- 让目录查询工具理解新版 schema

**修改文件建议**:

- `agent-kits/common/bin/oc-toolfind`
- `agent-kits/common/bin/oc-toolcat`

**交付要求**:

- `oc-toolfind` 支持按 `tags`、`protocols`、`target_types`、`risk_level` 搜索
- `oc-toolcat` 支持输出工具详情、recipe 关联、policy 关联
- `oc-toolfind` 支持按执行档位和风险级别筛选冷门/特殊工具

**验证标准**:

- 能查询“低风险 recon 工具”
- 能查询“需要 sudo 的工具”
- 能查询“支持 URL 目标类型的 web 工具”

### WP-7: 迁移与兼容收尾

**目标**:

- 逐步退出旧 JSONL 主路径

**修改文件建议**:

- `events/summarize.py`
- `events/archive.py`
- `README.md`
- `ARCHITECTURE.md`
- `events/EVENT_PROTOCOL.md`

**交付要求**:

- `summarize.py` 读取 `results` 与 `artifacts`
- `archive.py` 只负责导出与压缩历史数据
- 主文档口径全部转向 v2

**验证标准**:

- 仓库中不再把 `JSONL` 描述为未来正式主真源
- v2 路径与旧兼容路径边界清晰

### WP-8: 双模式与特殊工具接入

**目标**:

- 让系统在稳态模式和冲刺模式之间可控切换
- 将冷门但有特殊价值的工具纳入正式目录，但受模式与策略约束

**修改文件建议**:

- `events/policies.py`
- `events/executors/local_tool.py`
- `events/worker.py`
- `agent-kits/policies/*.json`
- `agent-kits/cmd-special/catalog/*.json`

**交付要求**:

- 默认执行档位为 `steady`
- `rush` 档位下允许特定高风险或交互式工具，但必须显式二次确认
- 无线域只保护内置网卡，允许外置 USB 网卡相关操作
- 稀有/特殊工具进入正式目录，并具备明确 `risk_level` 与 `policy_refs`

**验证标准**:

- 同一能力任务可在 `steady` 和 `rush` 下按不同策略执行
- 未带确认标记的高风险交互式工具在 `rush` 下仍会被阻断
- 冷门工具可被检索、分类和受策略控制地调用

### 推荐执行顺序

1. `WP-1`
2. `WP-2`
3. `WP-3`
4. `WP-4`
5. `WP-5`
6. `WP-6`
7. `WP-7`

### 不建议并行推进的部分

- `WP-1` 和 `WP-2` 不建议拆开太久
- `WP-4` 和 `WP-5` 可以部分并行，但先定 schema 再写 recipe
- dashboard、webhook、记忆系统、分布式扩展不应插队到这批任务前面
