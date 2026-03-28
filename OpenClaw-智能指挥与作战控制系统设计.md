# OpenClaw - 智能指挥与作战控制系统设计

**版本**: 0.1  
**日期**: 2026-03-28  
**状态**: 草案，作为新的独立任务板块  
**定位**: 面向前端控制台、指挥角色拆分、目标驱动托管与未来知识协作的统一方案

---

## 1. 为什么要从上一份方案里拆出来

当前工作已经不再只是：

- 多 Agent 编排
- 任务内核重构
- Kali 工具目录升级

而是明显进入了另一个更大的板块：

- 指挥入口如何工作
- 前端控制台如何组织
- `commander` 和 `analyst` 如何拆分
- 用户如何通过自然语言输入情报、目标、阶段性任务
- 系统如何在有人盯盘和无人盯盘两种情况下切换
- 未来如何承接知识库、情报总结、经验复用

因此，从现在开始应把两条大任务正式分开：

1. **基础设施板块**
   - 任务内核
   - worker / executor
   - tool catalog / recipe / policy
   - 数据真源、状态机、artifact、观测

2. **指挥与作战板块**
   - 前端控制台
   - 自然语言入口
   - `commander` / `analyst`
   - 方案讨论、方案确认、方案发布
   - 自动化托管模式
   - 防御模式入口
   - 后续知识协作入口

本文件只负责第二块。

---

## 1.1 当前已确认的默认决策

以下内容作为当前板块的默认基线：

- 角色架构：`commander + analyst`
- 角色关系：`analyst` 后台持续运行，不阻塞 `commander`
- 方案模型：动态方案 + 版本迭代 + 分支能力
- 任务组织：先落地任务树，后续预留到 DAG
- 对话模式：多轮讨论 -> 多轮修订 -> 方案确认 -> 发布
- 托管模式：`steady / rush / managed-auto / campaign-auto`
- “全自动红队模式”正式口径：目标驱动的自动化托管模式，内部状态名 `campaign_auto`
- 自动化控制：`pause / resume / drain / stop / emergency kill`
- 高危工具授权：按具体工具逐项勾选，并保留关键工具二次确认
- 交互式工具：允许 AI 驱动，但必须完整 transcript、checkpoint、timeout 与审计
- 前端技术路线：现在走 `React + Vite`，后续视内部发布需求再包装为桌面端
- 前端实时更新：优先 `SSE`
- 主视图：`Mission / Execution / Catalog`，后续补 `Command Board / Campaign / Defense`
- `commander / analyst` 布局：支持并排与堆叠切换，默认并排
- 结果层：摘要 + 详情 + 时间线 + artifact 浏览
- 日志层：系统日志 + 任务日志 + 分析日志 + transcript + 操作审计
- 模型路由：`commander` 默认 `reasoner/chat` 混合，`analyst` 默认 `chat/reasoner` 混合并带缓存压缩
- Token 控制：长对话压缩 + 摘要缓存 + 知识引用去重

以上默认决策，后续若无明确推翻，均按已确认处理。

---

## 2. 当前任务边界

### 2.1 本文档负责

- Mission / Execution / Catalog 控制台的演进
- `command` 当前形态与未来拆分
- 自然语言输入到候选方案的交互链
- 用户确认与自动发布
- 自动化托管模式
- 防御模式入口
- 后续知识协作的前端承接方式

### 2.2 本文档不负责

- SQLite/WAL 任务内核本身
- worker/executor 底层重构
- tool catalog v2 schema 本身
- recipe/policy 内核字段
- artifact 存储实现细节

这些分别归：
- [OpenClaw-多Agent编排与Kali工具系统重构设计.md](/home/asus/.openclaw/OpenClaw-多Agent编排与Kali工具系统重构设计.md)
- [OpenClaw-情报、记忆与研究分析设计.md](/home/asus/.openclaw/OpenClaw-情报、记忆与研究分析设计.md)

---

## 3. 当前控制台定位

控制台不应只是“发布任务的表单”。

它的正式定位应是：

**授权团队的内部作战控制台**

要同时覆盖三种使用方式：

1. **快速操作**
   - 已知目标
   - 已知能力类别
   - 直接发布任务

2. **指挥讨论**
   - 用户给情报、方向、阶段目标
   - 系统先分析，再给方案
   - 用户选择方案后自动发布

3. **阶段性托管**
   - 用户无法持续盯盘
   - 只给阶段目标和授权边界
   - 系统持续尝试、持续记录、持续推进

---

## 4. 指挥体系设计

### 4.1 当前阶段

当前仍用单一 `command` 入口。

它现在应该承担两种工作：

1. 对话与理解
2. 候选方案分析

但这只是过渡形态。

### 4.2 未来拆分

建议拆成两个并排角色：

#### `commander`

职责：

- 面向用户输入
- 识别目标、情报、阶段目标
- 负责对话、确认、协同和任务编排
- 接收各模块输出并统一决策
- 负责最终方案确认与发布

特点：

- 必须保持高响应
- 不应被长时间分析阻塞
- 更像现场指挥官

#### `analyst`

职责：

- 长时间分析
- 检索情报、历史结果、未来知识库
- 总结作战路径
- 输出候选方案、技术说明、注意事项
- 给 `commander` 提供分析支撑

特点：

- 可以长期占用
- 可以慢、可以深
- 更像旁路分析台

### 4.3 为什么必须拆

核心原因不是好看，而是并发需求：

- 当用户在下达新命令时
- `analyst` 可能还在检索、归纳、查资料、对比打法
- 这时如果还共用同一个角色，现场响应会变慢

因此需要：

- `analyst` 持续跑分析
- `commander` 持续接收你的现场输入

这也是为什么未来前端上，两者应并排显示，而不是上下串联。

---

## 5. 前端工作台分层

### 5.1 第一层：Mission

用途：

- 输入自然语言情报、目标、方向、问题
- 获取候选方案
- 查看 `commander` / `analyst` 的输出
- 选择方案并下发

后续增强：

- 支持继续追问
- 支持多轮对话上下文
- 支持锁定某一方案继续细化

### 5.2 第二层：Execution

用途：

- 看执行代理状态
- 看任务链进度
- 看最近结果
- 看日志和心跳

后续增强：

- worker/agent 详情
- attempt 级时间线
- artifact 浏览
- 失败原因筛选

### 5.3 第三层：Catalog

用途：

- 看工具
- 看 recipe
- 看 policy
- 看特殊/冷门工具

后续增强：

- 多维筛选
- 关联 capability
- 关联 recipe 覆盖率

### 5.4 第四层：Dual Command Board

这是未来新增视图，不是当前立刻实现。

内容应并排展示：

- 左侧 `commander`
- 右侧 `analyst`

典型布局：

- 左边负责实时沟通、确认、下达命令
- 右边负责分析摘要、情报检索、技术推理、候选方案

---

## 6. 任务意图链路

当前前端已经具备：

`自然语言输入 -> command -> 候选方案 -> 一键发布`

后续应演进为：

`情报/目标 -> commander -> analyst -> 候选方案 -> 用户确认 -> workflow 发布`

### 6.1 输入类型

前端应允许至少四类输入：

1. 一条情报
2. 一个技术问题
3. 一个攻击方向
4. 一个阶段性目标

### 6.2 输出类型

至少应统一为：

- `summary`
- `discussion`
- `assumptions`
- `options`
- `tasks`

其中：

- `discussion` 用于讨论原理、技术路线、风险点
- `options` 用于给用户选路径
- `tasks` 用于真正发布

---

## 7. 自动化托管模式

### 7.1 定义

这不是普通的 `rush`。

它的正式定位应是：

**目标驱动的自动化托管模式**

适用场景：

- 用户无法持续盯盘
- 用户只能间隔查看控制台
- 用户只给阶段目标
- 剩余推进交给系统持续规划和尝试

### 7.2 核心特征

该模式下系统应当：

- 根据阶段目标持续规划方案
- 自动选择下一步路径
- 在授权边界内持续尝试
- 持续记录日志与尝试历史
- 持续输出阶段总结

### 7.3 不能缺的约束

该模式必须保留：

- 严格日志
- 完整过程记录
- 关键步骤可追踪
- 高风险工具使用边界

### 7.4 高风险工具授权清单

进入该模式前，前端应弹出单独确认层：

- 列出正常情况下默认不放开的工具
- 分组展示：
  - 高风险工具
  - 特殊/冷门工具
  - 交互式工具
- 由用户逐项勾选允许

规则：

- 已勾选的，才允许进入自动化托管尝试范围
- 未勾选的，即使自动模式开启，也不得调用

### 7.5 与 `rush` 的关系

- `rush` 是执行档位
- 自动化托管模式是指挥与流程模式

两者可以叠加，但不能混为一谈。

---

## 8. Defense 模式入口

### 8.1 现阶段定位

先只作为路线图保留，不在当前轮次实现。

### 8.2 未来方向

`defense` 模式打开后，系统可以：

- 周期性扫描本地情况
- 周期性状态巡检
- 汇总风险变化
- 输出防御视角报告

更后面才考虑：

- 主动防御
- 策略联动
- 主动告警或阻断

---

## 9. 与未来知识协作的关系

知识库目前不在本轮正式实现，但本板块必须提前给它预留入口。

未来 `analyst` 可读取：

- 比赛中的经验总结
- 新场景打法
- 经典攻击链案例
- 最新公开情报
- 技术方案与原理说明

但这些都应作为后续独立阶段推进，不应现在把当前前端主线拖乱。

---

## 10. 后续执行顺序建议

建议这个新板块后续按以下顺序推进：

1. 前端第二阶段完善
   - 方案确认弹层
   - 结果详情
   - artifact 浏览
   - 更好的筛选和收纳

2. `commander` 多轮对话能力
   - 继续追问
   - 方案细化
   - 保留会话上下文

3. `commander + analyst` 角色拆分
   - 后端角色拆分
   - 前端并排工作台

4. 自动化托管模式
   - 目标输入
   - 授权清单
   - 严格日志
   - 持续推进

5. Defense 模式入口

6. 后续知识协作入口

---

## 11. 与旧方案的关系

从现在开始建议明确：

- [OpenClaw-多Agent编排与Kali工具系统重构设计.md](/home/asus/.openclaw/OpenClaw-多Agent编排与Kali工具系统重构设计.md)
  - 负责底层编排、任务内核、工具目录、worker/executor、policy/recipe

- [OpenClaw-智能指挥与作战控制系统设计.md](/home/asus/.openclaw/OpenClaw-智能指挥与作战控制系统设计.md)
  - 负责前端控制台、指挥角色、自然语言入口、自动化托管与控制面设计

- [OpenClaw-情报、记忆与研究分析设计.md](/home/asus/.openclaw/OpenClaw-情报、记忆与研究分析设计.md)
  - 负责知识库、经验沉淀、情报整理与未来研究分析能力

三者相关，但不再混写。

---

## 12. `commander + analyst` 技术边界与数据流

### 12.1 核心原则

两者不是“两个聊天窗口”，而是两个不同职责的系统角色：

- `commander` 负责面向用户、维持节奏、组织确认、触发发布
- `analyst` 负责持续分析、检索、归纳、比对、提供支撑

两者都不直接执行实际攻击任务。

### 12.2 职责边界

#### `commander` 负责

- 接收用户输入
- 识别当前输入属于：
  - 情报
  - 阶段目标
  - 技术问题
  - 明确任务
- 决定是否需要调用 `analyst`
- 汇总 `analyst` 输出
- 形成候选方案
- 请求用户确认
- 生成 workflow 并发布到任务内核

#### `analyst` 负责

- 长时间分析
- 检索结果、历史记录、知识引用
- 关联场景、工具链、失败案例
- 输出讨论结论和候选路径
- 向 `commander` 提供结构化分析结果

### 12.3 数据对象建议

建议新增以下对象：

#### `mission_sessions`

- 一次连续的指挥会话
- 承载目标、上下文、当前模式、当前阶段

建议字段：

- `id`
- `title`
- `user_goal`
- `current_status`
- `execution_profile_default`
- `automation_mode`
- `created_at`
- `updated_at`

#### `discussion_messages`

- 会话中的人机对话
- 可标记来源为 `user / commander / analyst / system`

建议字段：

- `id`
- `mission_session_id`
- `role`
- `content`
- `summary_ref`
- `created_at`

#### `analysis_jobs`

- `analyst` 的后台分析任务
- 用于表达“当前分析还在跑”

建议字段：

- `id`
- `mission_session_id`
- `job_type`
- `status`
- `input_ref`
- `output_ref`
- `started_at`
- `completed_at`

#### `analysis_outputs`

- `analyst` 的结构化输出

建议字段：

- `id`
- `analysis_job_id`
- `summary`
- `discussion_json`
- `assumptions_json`
- `evidence_refs_json`
- `warnings_json`
- `created_at`

### 12.4 数据流

建议主链如下：

1. 用户输入 -> `mission_session`
2. `commander` 判断输入类型
3. 需要分析时，创建 `analysis_job`
4. `analyst` 在后台运行
5. `analyst` 产出 `analysis_output`
6. `commander` 读取分析结果
7. `commander` 生成 `plan_candidate`
8. 用户确认某一方案
9. `commander` 生成 `workflow + task_tree`
10. 发布到任务内核

### 12.5 接口建议

建议新增或收敛成以下接口：

- `POST /api/missions`
- `POST /api/missions/{id}/discuss`
- `POST /api/missions/{id}/analyze`
- `GET /api/missions/{id}/analysis-jobs`
- `GET /api/missions/{id}/plans`
- `POST /api/missions/{id}/plans/{plan_id}/launch`
- `POST /api/missions/{id}/plans/{plan_id}/revise`

### 12.6 前端联动建议

Dual Command Board 下：

- 左栏显示 `commander`
  - 当前会话
  - 当前候选方案
  - 用户确认动作
- 右栏显示 `analyst`
  - 当前分析任务
  - 讨论摘要
  - 风险点
  - 相关知识引用

---

## 13. 动态方案系统与版本状态机

### 13.1 为什么必须动态化

方案不是“一次生成，一次执行”。

真实情况通常是：

- 新情报进入
- 某条路线失败
- 某个前提被推翻
- 某个能力结果和预期不一致
- 用户希望收窄或扩展范围

因此方案系统必须支持：

- 版本
- 修订
- 分支
- 回退
- 转发布

### 13.2 核心对象建议

#### `plan_candidates`

- 每个 mission 下的候选方案

建议字段：

- `id`
- `mission_session_id`
- `title`
- `intent`
- `fit`
- `risk_level`
- `status`
- `current_revision_id`
- `created_at`

#### `plan_revisions`

- 方案版本

建议字段：

- `id`
- `plan_candidate_id`
- `parent_revision_id`
- `revision_no`
- `summary`
- `discussion_json`
- `assumptions_json`
- `warnings_json`
- `created_at`

#### `plan_tasks`

- revision 下面的任务树节点

建议字段：

- `id`
- `plan_revision_id`
- `parent_task_node_id`
- `capability`
- `operation`
- `params_json`
- `notes`
- `order_index`

### 13.3 方案状态

建议 `plan_candidate.status`：

- `draft`
- `under_review`
- `approved`
- `launched`
- `superseded`
- `archived`

### 13.4 版本动作

建议支持以下动作：

- `create`
- `revise`
- `branch`
- `merge_note`
- `approve`
- `launch`
- `pause`
- `archive`

### 13.5 版本状态机

建议逻辑：

`draft`
  -> `under_review`
  -> `approved`
  -> `launched`

`under_review`
  -> `draft`
  -> `approved`
  -> `superseded`

`approved`
  -> `launched`
  -> `superseded`

`launched`
  -> `superseded`
  -> `archived`

### 13.6 分支模型

建议把分支设计为：

- 一个 `plan_candidate`
- 多个 `plan_revisions`
- revision 可从上一个 revision 继续
- 也可以从任意 revision 开出新 branch

这样可以表达：

- 主路线
- 备选路线
- 高风险路线
- 保守路线

### 13.7 发布模型

发布时不应只记“发了哪几个任务”，而应绑定：

- `mission_session_id`
- `plan_candidate_id`
- `plan_revision_id`
- `launch_batch_id`
- `workflow_id`

这样后面在执行页和回放页才能还原：

- 这批任务来自哪一轮讨论
- 是哪个版本的方案
- 为什么会这么发

### 13.8 前端展示建议

前端应支持：

- 当前主方案
- 方案版本历史
- 方案分支切换
- 某个 revision 的任务树预览
- 方案确认后的一键发布

---

## 14. `campaign_auto` 授权模型与运行状态机

### 14.1 定义

`campaign_auto` 是：

- 目标驱动
- 可持续推进
- 可自动重规划
- 保留严格审计

它不是简单的“自动勾选 rush”。

### 14.2 进入条件

进入前必须明确：

- 目标范围
- 当前 mission session
- 默认 execution profile
- 允许能力域
- 允许工具集
- 风险上限
- 超时策略
- 停止策略

### 14.3 授权对象建议

建议新增：

#### `approval_scopes`

- 一次托管运行的授权范围

字段建议：

- `id`
- `mission_session_id`
- `mode`
- `allowed_capabilities_json`
- `allowed_tools_json`
- `allowed_high_risk_tools_json`
- `interactive_tools_json`
- `approved_by`
- `approved_at`
- `expires_at`

#### `campaign_runs`

- 一次自动化托管运行实例

字段建议：

- `id`
- `mission_session_id`
- `approval_scope_id`
- `status`
- `goal_summary`
- `created_at`
- `started_at`
- `stopped_at`

#### `campaign_events`

- 托管运行过程中的每一步事件

字段建议：

- `id`
- `campaign_run_id`
- `event_type`
- `payload_json`
- `created_at`

### 14.4 运行状态

建议 `campaign_run.status`：

- `draft`
- `awaiting_approval`
- `ready`
- `running`
- `paused`
- `draining`
- `stopped`
- `completed`
- `failed`
- `killed`

### 14.5 运行状态机

建议：

`draft`
  -> `awaiting_approval`
  -> `ready`
  -> `running`

`running`
  -> `paused`
  -> `draining`
  -> `completed`
  -> `failed`
  -> `killed`

`paused`
  -> `running`
  -> `stopped`
  -> `killed`

`draining`
  -> `completed`
  -> `stopped`

### 14.6 自动重规划规则

自动重规划允许，但必须受以下约束：

- 只能在已授权能力域内重规划
- 只能在已授权工具集内重规划
- 高风险工具仍受单独批准约束
- 每次重规划都必须写 `campaign_event`
- 每次重规划都应生成新的 `plan_revision_ref`

### 14.7 交互式工具接入

交互式工具若进入 `campaign_auto`，必须补全：

- `interactive_session_id`
- transcript
- checkpoint
- timeout
- tool exit condition
- AI decision trace

建议额外对象：

#### `interactive_sessions`

- `id`
- `campaign_run_id`
- `tool_name`
- `task_id`
- `status`
- `transcript_ref`
- `started_at`
- `ended_at`

### 14.8 前端确认层

进入 `campaign_auto` 前，前端应弹出授权确认层，至少包含：

- 当前目标摘要
- 自动托管模式说明
- 默认执行档位
- 允许能力域
- 高风险工具清单
- 特殊/冷门工具清单
- 交互式工具清单
- 超时/停止说明

并要求用户：

- 勾选允许工具
- 勾选高风险确认
- 勾选交互式确认
- 最终确认启动

### 14.9 前端运行面板

Campaign 视图建议至少展示：

- 当前状态
- 当前目标
- 当前主路线
- 最近重规划
- 最近 20 条 campaign events
- 已使用高风险工具
- 当前交互式工具会话
- `pause / resume / drain / stop / emergency kill`

---

## 15. 前端与 API 的实现级建议

### 15.1 前端模块拆分

建议 React 端至少拆成以下模块：

- `apps/console`
- `features/mission`
- `features/execution`
- `features/catalog`
- `features/command-board`
- `features/campaign`
- `features/defense`
- `features/shared-timeline`

### 15.2 页面与路由建议

建议路由：

- `/mission`
- `/mission/:id`
- `/execution`
- `/execution/workflow/:workflowId`
- `/catalog`
- `/command-board/:missionId`
- `/campaign/:campaignRunId`
- `/defense`

### 15.3 前端状态建议

建议前端状态分层：

1. 会话层
   - 当前 `mission_session`
   - 当前视图
   - 当前 profile

2. 实时层
   - worker 心跳
   - campaign events
   - workflow 进度

3. 文档层
   - 方案 revision
   - analysis output
   - knowledge refs

建议工具：

- 服务端状态：`SSE`
- 本地 UI 状态：轻量 store
- 表单：独立 form state

### 15.4 SSE 事件类型建议

建议至少定义：

- `mission.updated`
- `analysis.job.updated`
- `analysis.output.created`
- `plan.updated`
- `workflow.updated`
- `campaign.updated`
- `campaign.event.created`
- `worker.heartbeat`
- `task.updated`
- `result.created`

### 15.5 Mission 视图接口契约

#### `POST /api/missions`

输入：

```json
{
  "title": "边界管理面目标",
  "userGoal": "先讨论可行路径，再给可执行方案",
  "executionProfileDefault": "steady"
}
```

输出：

```json
{
  "missionSessionId": "ms_001",
  "status": "active"
}
```

#### `POST /api/missions/{id}/discuss`

输入：

```json
{
  "content": "怀疑边界 Web 管理后台和内网服务有联动",
  "inputType": "intel"
}
```

输出：

```json
{
  "messageId": "msg_001",
  "analysisRequested": true,
  "analysisJobId": "aj_001"
}
```

#### `GET /api/missions/{id}`

返回：

- 会话元数据
- 最近消息
- 当前分析任务
- 当前主方案
- 当前 revision

### 15.6 Command Board 接口契约

#### `GET /api/missions/{id}/analysis-jobs`

返回：

- 当前运行中的 `analysis_jobs`
- 最近 `analysis_outputs`

#### `GET /api/missions/{id}/plans`

返回：

- 候选方案列表
- 当前主方案
- revision 历史
- 分支信息

#### `POST /api/missions/{id}/plans/{planId}/revise`

输入：

```json
{
  "instruction": "收窄到 recon 和 web，先不要碰 exploit"
}
```

### 15.7 Execution 视图接口契约

建议聚合接口：

- `GET /api/execution/overview`
- `GET /api/workflows/{workflowId}`
- `GET /api/tasks/{taskId}`
- `GET /api/results/{taskId}`
- `GET /api/artifacts/{taskId}`

其中 `GET /api/workflows/{workflowId}` 应至少返回：

- workflow 基础信息
- plan 绑定关系
- task tree
- 当前进度
- 最近失败点

### 15.8 Campaign 视图接口契约

#### `POST /api/campaigns`

输入：

```json
{
  "missionSessionId": "ms_001",
  "goalSummary": "在授权范围内持续推进边界到内网的可行路径",
  "approvalScopeId": "ap_001",
  "executionProfileDefault": "rush"
}
```

#### `POST /api/campaigns/{id}/control`

输入：

```json
{
  "action": "pause"
}
```

允许：

- `pause`
- `resume`
- `drain`
- `stop`
- `kill`

### 15.9 前端优化建议

第一轮实现建议：

- 保留深色高密度作战风格
- 用可折叠区块和抽屉，不用长单页堆叠
- 结果、analysis、artifact 一律抽屉化
- 关键对象一律支持复制 ID、跳转详情、查看时间线

第二轮实现建议：

- 双栏 `commander / analyst`
- 方案分支图
- workflow 树
- campaign 控制条

第三轮实现建议：

- 知识引用卡片
- 失败路径警告
- 自动重规划可视化

---

## 16. 具体实施任务清单

以下清单作为本板块的默认执行任务表。后续如果没有新变更要求，可直接按顺序持续实现。

### 16.1 第一组：前端工程化与骨架切换

1. 建立 `React + Vite` 前端工程  
交付：
- `dashboard-ui/` 或等价前端目录
- 基础路由、构建脚本、开发脚本
- 深色作战风格主题变量

2. 建立控制台布局骨架  
交付：
- 顶层壳
- 侧导航或顶部导航
- Mission / Execution / Catalog 三大主视图
- 抽屉、面板、时间线等通用组件

3. 建立 API client 与 SSE client  
交付：
- REST 请求层
- SSE 订阅层
- 错误处理和重连策略

### 16.2 第二组：Mission 与 Command Board

4. 实现 Mission Session 基础页  
交付：
- 新建 mission
- 查看 mission
- 最近消息列表
- 输入类型标识：情报 / 目标 / 问题 / 明确任务

5. 实现 Discuss 流程  
交付：
- `POST /api/missions`
- `POST /api/missions/{id}/discuss`
- 消息展示与状态更新

6. 实现 Analysis Job 面板  
交付：
- `analysis_jobs` 列表
- 当前运行状态
- 最近完成输出
- analyst 工作中/空闲态

7. 实现 Dual Command Board 第一版  
交付：
- 左侧 `commander`
- 右侧 `analyst`
- 支持并排/堆叠切换
- 支持知识引用摘要卡片预留位

### 16.3 第三组：动态方案系统

8. 实现 Plan Candidate 列表与详情  
交付：
- 候选方案列表
- 风险等级
- 方案摘要
- 当前 revision 标识

9. 实现 Revision 历史与分支切换  
交付：
- revision 时间线
- 分支入口
- 当前主 revision 高亮

10. 实现 Plan Task Tree 预览  
交付：
- 任务树可视化
- capability / operation / notes 展示
- 发布前预览

11. 实现 Plan Revise 接口与 UI  
交付：
- `POST /api/missions/{id}/plans/{planId}/revise`
- 修订说明输入
- 新 revision 自动生成

12. 实现 Launch Batch 绑定  
交付：
- 方案确认后生成 workflow
- 记录 `mission_session_id / plan_candidate_id / plan_revision_id / workflow_id`

### 16.4 第四组：Execution 视图

13. 实现 Workflow 详情页  
交付：
- task tree
- 当前进度
- 失败节点
- 最近结果

14. 实现 Task / Result / Artifact 抽屉  
交付：
- `GET /api/tasks/{taskId}`
- `GET /api/results/{taskId}`
- `GET /api/artifacts/{taskId}`
- 摘要、详情、时间线和 artifact 列表

15. 实现 Worker 与 Agent 视图  
交付：
- worker 心跳
- capability 状态
- 最近执行任务
- agent 维度汇总

### 16.5 第五组：Campaign Auto

16. 实现 Approval Scope 建模  
交付：
- 高风险工具清单
- 特殊/冷门工具清单
- 交互式工具清单
- 用户勾选授权记录

17. 实现 Campaign 创建与控制  
交付：
- `POST /api/campaigns`
- `POST /api/campaigns/{id}/control`
- `pause / resume / drain / stop / kill`

18. 实现 Campaign 事件流  
交付：
- `campaign_events`
- 最近事件列表
- 当前状态条
- 最近重规划记录

19. 实现交互式工具会话面板  
交付：
- `interactive_sessions`
- transcript 摘要
- checkpoint 标记
- timeout/退出原因

20. 实现 Campaign Auto 审计链  
交付：
- 每次自动重规划有记录
- 每次高风险工具调用有记录
- 每次中断/暂停/恢复有记录

### 16.6 第六组：Defense 入口与收尾

21. 建立 Defense 视图占位  
交付：
- 周期巡检面板占位
- 风险摘要位
- 后续主动防御预留入口

22. 建立全局时间线  
交付：
- mission / plan / workflow / campaign 共用时间线
- 支持对象间跳转

23. 建立全局搜索与对象跳转  
交付：
- mission id / workflow id / task id / campaign id 快速定位

24. 完成 UI 收敛  
交付：
- 统一视觉
- 收起/展开规则
- 大量信息下的高密度布局优化

### 16.7 默认执行顺序

建议默认按下面顺序推进：

1. 1-3
2. 4-7
3. 8-12
4. 13-15
5. 16-20
6. 21-24

### 16.8 达到“可独立执行”的标准

当以下条件满足时，后续可基本按文档直接持续开发：

- 页面结构固定
- API 契约固定
- 动态方案模型固定
- campaign_auto 状态机固定
- 审计和日志边界固定

---

## 17. 文件级修改映射、依赖顺序与验收标准

### 17.1 第一组：前端工程化与骨架切换

建议修改路径：

- `dashboard-ui/package.json`
- `dashboard-ui/vite.config.ts`
- `dashboard-ui/src/main.tsx`
- `dashboard-ui/src/app/router.tsx`
- `dashboard-ui/src/app/layout/*`
- `dashboard-ui/src/shared/api/*`
- `dashboard-ui/src/shared/sse/*`

依赖顺序：

1. 先建工程
2. 再建布局
3. 再接 API/SSE

验收标准：

- 本地开发服务可启动
- 主路由可访问
- API client 与 SSE client 可单独测试

### 17.2 第二组：Mission 与 Command Board

建议修改路径：

- `dashboard-ui/src/features/mission/*`
- `dashboard-ui/src/features/command-board/*`
- `events/api/missions.py`
- `events/api/analysis.py`
- `events/services/mission_service.py`
- `events/services/analysis_service.py`

依赖顺序：

1. 先 Mission session API
2. 再 discuss
3. 再 analysis job
4. 最后 Dual Command Board

验收标准：

- 可以创建 mission
- 可以提交 discuss
- analyst job 状态可见
- Dual Command Board 能显示 commander / analyst 分栏

### 17.3 第三组：动态方案系统

建议修改路径：

- `events/api/plans.py`
- `events/services/plan_service.py`
- `events/db.py`
- `events/migrations/*plan*.sql`
- `dashboard-ui/src/features/mission/plans/*`
- `dashboard-ui/src/features/execution/workflow-link/*`

依赖顺序：

1. 先表结构
2. 再 service
3. 再 API
4. 再前端 revision / branch
5. 最后 launch 绑定

验收标准：

- 可创建 plan candidate
- 可生成 revision
- 可从 revision 派生 branch
- 可绑定 workflow 发布

### 17.4 第四组：Execution 视图

建议修改路径：

- `events/api/execution.py`
- `events/services/execution_service.py`
- `events/services/workflow_service.py`
- `dashboard-ui/src/features/execution/*`
- `dashboard-ui/src/features/shared-timeline/*`

依赖顺序：

1. 先 workflow 聚合接口
2. 再 task/result/artifact 详情
3. 再 worker/agent 汇总

验收标准：

- workflow 详情可查看
- task/result/artifact 抽屉可打开
- worker 和 agent 状态可汇总展示

### 17.5 第五组：Campaign Auto

建议修改路径：

- `events/api/campaigns.py`
- `events/services/campaign_service.py`
- `events/services/approval_service.py`
- `events/migrations/*campaign*.sql`
- `events/migrations/*approval*.sql`
- `dashboard-ui/src/features/campaign/*`
- `dashboard-ui/src/features/campaign/components/approval-modal/*`

依赖顺序：

1. 先 approval scope
2. 再 campaign run
3. 再 control API
4. 再 event stream
5. 再 interactive session
6. 最后 campaign audit

验收标准：

- 可创建 approval scope
- 可启动 campaign
- `pause / resume / drain / stop / kill` 全可用
- 高风险授权和 campaign event 可审计

### 17.6 第六组：Defense 入口与收尾

建议修改路径：

- `dashboard-ui/src/features/defense/*`
- `events/api/defense.py`
- `events/services/defense_service.py`
- `dashboard-ui/src/features/global-search/*`
- `dashboard-ui/src/features/shared-timeline/*`

依赖顺序：

1. 先 Defense 占位与风险摘要位
2. 再全局时间线
3. 再全局搜索
4. 最后 UI 收敛

验收标准：

- Defense 视图可访问
- 全局时间线可串起 mission / plan / workflow / campaign
- 对象级搜索可跳转
- UI 密度与布局稳定

### 17.7 默认执行口径

若后续未出现新冲突，默认执行方式为：

- 先后端对象和接口
- 再前端页面与交互
- 每组完成后做一轮 smoke test
- 通过后再推进下一组

## 18. 对象字段与 API 落地清单

### 18.1 `mission_sessions`

建议字段：

- `id`
- `title`
- `objective_text`
- `context_text`
- `operator_notes`
- `status`
- `priority`
- `created_by`
- `latest_plan_id`
- `latest_workflow_id`
- `active_campaign_run_id`
- `created_at`
- `updated_at`

说明：

- `objective_text` 存原始目标或情报输入
- `context_text` 存附加限制、边界、已知资产
- `status` 建议固定为 `draft / discussing / planned / running / paused / completed / archived`

### 18.2 `discussion_messages`

建议字段：

- `id`
- `mission_session_id`
- `role`
- `author_type`
- `author_id`
- `content_text`
- `summary_text`
- `message_kind`
- `token_in`
- `token_out`
- `created_at`

说明：

- `role` 建议支持 `user / commander / analyst / system`
- `message_kind` 建议支持 `input / clarification / analysis / plan_hint / decision / review`

### 18.3 `analysis_jobs`

建议字段：

- `id`
- `mission_session_id`
- `trigger_message_id`
- `status`
- `job_kind`
- `query_text`
- `input_snapshot_json`
- `output_summary`
- `evidence_refs_json`
- `warning_refs_json`
- `error_text`
- `started_at`
- `finished_at`

说明：

- `job_kind` 建议至少支持 `background_analysis / intel_lookup / path_review / risk_review`
- `input_snapshot_json` 用于固定当次分析上下文，避免后续复算歧义

### 18.4 `plan_candidates`

建议字段：

- `id`
- `mission_session_id`
- `source_message_id`
- `status`
- `title`
- `goal_summary`
- `discussion_summary`
- `assumptions_json`
- `warnings_json`
- `evidence_refs_json`
- `preferred_branch_key`
- `created_at`
- `updated_at`

说明：

- `status` 建议支持 `draft / proposed / selected / superseded / archived`

### 18.5 `plan_revisions`

建议字段：

- `id`
- `plan_candidate_id`
- `revision_no`
- `branch_key`
- `parent_revision_id`
- `status`
- `change_summary`
- `plan_outline_json`
- `task_tree_json`
- `launchable`
- `created_by`
- `created_at`

说明：

- `branch_key` 用于保存并行路线，例如 `main / stealth / fallback`
- `launchable` 为布尔值，标记当前 revision 是否已满足发布条件

### 18.6 `launch_batches`

建议字段：

- `id`
- `mission_session_id`
- `plan_revision_id`
- `workflow_id`
- `launch_mode`
- `execution_profile`
- `selected_tools_json`
- `task_count`
- `status`
- `created_at`

说明：

- `launch_mode` 建议支持 `manual / assisted / managed_auto / campaign_auto`

### 18.7 `campaign_runs`

建议字段：

- `id`
- `mission_session_id`
- `plan_revision_id`
- `approval_scope_id`
- `status`
- `objective_summary`
- `scope_summary`
- `execution_profile`
- `max_parallelism`
- `auto_replan_enabled`
- `started_at`
- `finished_at`

### 18.8 `approval_scopes`

建议字段：

- `id`
- `mission_session_id`
- `scope_name`
- `allowed_categories_json`
- `allowed_tools_json`
- `interactive_tools_json`
- `high_risk_tools_json`
- `denied_tools_json`
- `network_scope_json`
- `confirmed_by`
- `confirmed_at`
- `expires_at`

说明：

- `allowed_tools_json` 和 `high_risk_tools_json` 要分开，后续前端弹窗才能清楚展示

### 18.9 `campaign_events`

建议字段：

- `id`
- `campaign_run_id`
- `event_type`
- `severity`
- `message`
- `payload_json`
- `related_task_id`
- `related_attempt_id`
- `created_at`

建议事件：

- `campaign_started`
- `plan_selected`
- `task_launched`
- `task_succeeded`
- `task_failed`
- `replan_requested`
- `replan_applied`
- `pause_requested`
- `resume_requested`
- `kill_requested`

### 18.10 第一版 API 清单

建议新增或固定以下接口：

- `POST /api/missions`
- `GET /api/missions/:id`
- `POST /api/missions/:id/discuss`
- `POST /api/missions/:id/analyze`
- `GET /api/missions/:id/analysis-jobs`
- `POST /api/missions/:id/plans`
- `GET /api/missions/:id/plans`
- `POST /api/plans/:id/revisions`
- `POST /api/revisions/:id/branches`
- `POST /api/revisions/:id/launch`
- `GET /api/workflows/:id`
- `GET /api/workflows/:id/timeline`
- `POST /api/campaigns`
- `POST /api/campaigns/:id/control`
- `GET /api/campaigns/:id/events`
- `GET /api/agents/overview`

### 18.11 SSE 事件清单

建议至少固定这些事件名：

- `mission.updated`
- `discussion.appended`
- `analysis.started`
- `analysis.finished`
- `plan.updated`
- `workflow.updated`
- `task.updated`
- `campaign.updated`
- `campaign.event`
- `agent.status`

### 18.12 第一版前端页面清单

建议页面顺序：

1. `MissionListPage`
2. `MissionWorkbenchPage`
3. `ExecutionDetailPage`
4. `CommandBoardPage`
5. `CampaignPage`
6. `CatalogPage`
7. `DefensePage`

默认组件：

- `MissionHeader`
- `DiscussionPanel`
- `AnalystPanel`
- `PlanCandidatesPanel`
- `LaunchConfirmModal`
- `WorkflowTimeline`
- `TaskDetailDrawer`
- `CampaignApprovalModal`
- `CampaignControlBar`

## 19. 阶段门槛、回归检查与直接实施规则

### 19.1 第一阶段门槛：Mission 与讨论闭环

达到以下条件才算完成：

- 可以创建 mission
- 可以持续追加 discussion message
- analyst job 可后台运行
- commander 与 analyst 双栏可同时显示
- Mission 页面刷新后状态可恢复

### 19.2 第二阶段门槛：动态方案闭环

达到以下条件才算完成：

- 一个 mission 下可存在多个 plan candidate
- plan candidate 可派生 revision 和 branch
- revision 可被选中并进入 launch 准备态
- 方案差异可在前端直接比较

### 19.3 第三阶段门槛：Execution 视图闭环

达到以下条件才算完成：

- workflow 可聚合 task / result / artifact / agent 状态
- 时间线可以回放关键事件
- task 失败可看到 error、attempt、tool、executor
- 结果详情抽屉可稳定打开

### 19.4 第四阶段门槛：Campaign Auto 闭环

达到以下条件才算完成：

- 可创建 approval scope
- 可启动 `campaign_auto`
- 可执行 `pause / resume / drain / stop / kill`
- 高风险和交互式工具授权可审计
- 自动重规划会留下清晰 event 记录

### 19.5 前端回归检查清单

每完成一组必须至少检查：

- 主导航和深链接没有断
- 页面刷新后 query state 和关键对象仍可恢复
- SSE 断开后能自动恢复或给出提示
- 长文本和中文内容不会破版
- 夜间深色主题下可读性稳定
- 高密度数据视图在 1440px 和移动端都不崩

### 19.6 后端回归检查清单

每完成一组必须至少检查：

- 新对象有 migration
- API 字段和文档一致
- 状态机流转无死状态
- 审计事件完整
- 错误返回结构统一
- smoke data 可清理，不污染正式数据

### 19.7 直接实施规则

若后续开始正式实现，默认按以下规则直接推进：

- 优先新建 `dashboard-ui/`，旧 `dashboard/` 先保留兼容
- 先做 Mission / Execution / Catalog 三大主视图，再补 Command Board 和 Campaign
- 先保证 commander / analyst / plan / workflow 四条主链可贯通，再做 UI 精修
- 默认 SSE，不先上 WebSocket
- 默认所有列表接口都支持 `cursor / limit / status / updated_after`
- 默认所有详情接口返回 `summary + refs + related objects`，避免前端重复拼装

## 20. 页面字段表、接口示例与实现附录

### 20.1 `MissionListPage` 字段表

列表字段建议：

- `mission_id`
- `title`
- `objective_summary`
- `status`
- `priority`
- `latest_plan_status`
- `latest_workflow_status`
- `active_campaign_status`
- `updated_at`

筛选项建议：

- `status`
- `priority`
- `has_campaign`
- `updated_after`
- `q`

### 20.2 `MissionWorkbenchPage` 字段表

页面分区建议：

1. Header
   - `title`
   - `mission_status`
   - `priority`
   - `latest_plan_badge`
   - `execution_profile_hint`
2. Discussion
   - `messages[]`
   - `pending_input`
   - `message_kind`
3. Analyst
   - `analysis_jobs[]`
   - `current_context_summary`
   - `warnings[]`
   - `evidence_refs[]`
4. Plans
   - `plan_candidates[]`
   - `selected_revision`
   - `branch_list`
   - `launch_ready`

### 20.3 `ExecutionDetailPage` 字段表

详情区建议：

- `workflow_id`
- `workflow_status`
- `launched_from_revision_id`
- `tasks[]`
- `results[]`
- `artifacts[]`
- `worker_overview[]`
- `timeline[]`

任务详情抽屉建议字段：

- `task_id`
- `capability`
- `operation`
- `executor_type`
- `tool_name`
- `attempt_count`
- `status`
- `started_at`
- `finished_at`
- `error`
- `structured_result`
- `artifact_refs`

### 20.4 `CommandBoardPage` 字段表

左栏 `commander`：

- `latest_operator_message`
- `discussion_summary`
- `selected_plan`
- `decision_queue`

右栏 `analyst`：

- `active_analysis_jobs`
- `knowledge_refs`
- `intel_refs`
- `experience_refs`
- `risk_notes`
- `alternative_paths`

中部联动区：

- `current_mission_focus`
- `current_assumptions`
- `current_warnings`

### 20.5 `CampaignPage` 字段表

顶部状态：

- `campaign_id`
- `status`
- `execution_profile`
- `approval_scope_name`
- `auto_replan_enabled`
- `max_parallelism`

主体区：

- `active_steps`
- `recent_events`
- `tool_usage_summary`
- `blocked_reasons`
- `pause_resume_state`

控制区：

- `pause`
- `resume`
- `drain`
- `stop`
- `kill`

### 20.6 `POST /api/missions` 请求示例

```json
{
  "title": "外网入口初始研判",
  "objective_text": "目前只有一段情报，怀疑目标有一个暴露的 Web 面和弱口令入口，先帮我整理可能路径。",
  "context_text": "只在授权内网范围内，先偏信息收集和路径研判。",
  "priority": "high"
}
```

响应示例：

```json
{
  "mission": {
    "id": "mis_01JZ...",
    "title": "外网入口初始研判",
    "status": "draft",
    "priority": "high",
    "created_at": "2026-03-28T18:05:00+08:00"
  }
}
```

### 20.7 `POST /api/missions/:id/discuss` 请求示例

```json
{
  "content_text": "目前只有目标域名和一段比赛情报，先分析可能的入口和信息收集路线。",
  "message_kind": "input",
  "run_analyst": true
}
```

响应示例：

```json
{
  "message": {
    "id": "msg_01JZ...",
    "mission_session_id": "mis_01JZ...",
    "role": "user",
    "message_kind": "input",
    "created_at": "2026-03-28T18:06:00+08:00"
  },
  "analysis_job": {
    "id": "aj_01JZ...",
    "status": "queued",
    "job_kind": "background_analysis"
  }
}
```

### 20.8 `POST /api/missions/:id/plans` 响应示例

```json
{
  "plan_candidate": {
    "id": "plan_01JZ...",
    "status": "proposed",
    "title": "先收集暴露面，再验证 Web 与凭据路径",
    "goal_summary": "以 recon 和 web 为主，保留 internal 作为后续分支。",
    "discussion_summary": "当前情报不足，先建立攻击面画像，再决定是否进入更高风险路径。",
    "assumptions_json": [
      "目标至少存在一个 HTTP 服务",
      "可能存在通用弱凭据"
    ],
    "warnings_json": [
      "当前情报不足，先不要直接进入高风险工具链"
    ],
    "evidence_refs_json": []
  }
}
```

### 20.9 `POST /api/revisions/:id/launch` 请求示例

```json
{
  "launch_mode": "assisted",
  "execution_profile": "steady",
  "selected_tools_json": [
    "nmap",
    "httpx",
    "whatweb"
  ]
}
```

### 20.10 `POST /api/campaigns` 请求示例

```json
{
  "mission_session_id": "mis_01JZ...",
  "plan_revision_id": "rev_01JZ...",
  "approval_scope_id": "scope_01JZ...",
  "execution_profile": "rush",
  "auto_replan_enabled": true,
  "max_parallelism": 3
}
```

### 20.11 `GET /api/workflows/:id` 响应骨架

```json
{
  "workflow": {
    "id": "wf_01JZ...",
    "status": "running",
    "mission_session_id": "mis_01JZ...",
    "plan_revision_id": "rev_01JZ..."
  },
  "tasks": [],
  "results": [],
  "artifacts": [],
  "workers": [],
  "timeline": []
}
```

### 20.12 SSE 消息示例

```json
{
  "event": "analysis.finished",
  "data": {
    "mission_session_id": "mis_01JZ...",
    "analysis_job_id": "aj_01JZ...",
    "summary": "已完成初步路径分析，建议优先走 recon + web。",
    "warnings": [
      "当前没有高置信凭据线索"
    ]
  }
}
```

### 20.13 React 模块建议

建议目录：

- `dashboard-ui/src/app/`
- `dashboard-ui/src/entities/mission/`
- `dashboard-ui/src/entities/plan/`
- `dashboard-ui/src/entities/workflow/`
- `dashboard-ui/src/entities/campaign/`
- `dashboard-ui/src/features/discussion/`
- `dashboard-ui/src/features/analyst/`
- `dashboard-ui/src/features/launch/`
- `dashboard-ui/src/widgets/mission-workbench/`
- `dashboard-ui/src/widgets/execution-detail/`
- `dashboard-ui/src/widgets/campaign-control/`

### 20.14 直接编码顺序

若后续直接开工，默认顺序为：

1. 先写 `events/api/*` 与 `events/services/*` 的最小骨架
2. 再写 migration 和对象 schema
3. 再写 `dashboard-ui` 的页面骨架
4. 再接 SSE
5. 最后补详情抽屉、对比视图和 Campaign 控制条
