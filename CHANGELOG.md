# OpenClaw C方案 - 变更记录

**版本**: 1.0  
**维护者**: OpenClaw Command Agent  
**格式**: 基于时间的变更记录，每次Codex/AI修改后更新

---

## [2026-03-28 17:20] 收口阶段性半成品文档、修正前端服务默认入口并清理仓库运行时冗余

**执行者**: Codex
**变更类型**: 文档 / 架构 / 仓库治理
**影响范围**: `dashboard/server.py`, `.gitignore`, `README.md`, `DOCUMENTATION.md`, `docs/README.md`, `OpenClaw-阶段性实力评估与发展方向总结.md`, `CHANGELOG.md`
**风险等级**: 中
**验证状态**: 已验证

### 变更详情
- **变更目的**:
  - 将之前两轮和本轮评估合并成可作为“半成品阶段基线”的正式文档，同时解决当前已经明显影响协作和发布质量的仓库冗余
- **技术内容**:
  - `dashboard/server.py` 现在优先服务 `dashboard-ui/dist` 中的 React 控制台，旧 `dashboard/` 静态页面仅作为回退
  - 为 React 控制台增加最小 SPA fallback 路由，避免前端页面做了但默认入口仍落在旧页面
  - `.gitignore` 补充 `events/runtime/*.db`、SQLite 辅助文件和 runtime artifacts 规则，并修正原有多处无效的同行尾注释写法
  - 将已被误纳入版本控制的运行时数据库、日志、任务 JSONL、锁文件和 agent session 文件从 Git 索引中移除，保留本地文件本身
  - 新增 `docs/README.md`，为当前根目录文档提供正式分类入口和半成品推荐阅读集
  - `OpenClaw-阶段性实力评估与发展方向总结.md` 升级为阶段性半成品版本总结，补入对接专家研究系统、公开项目可采纳项和当前必须处理冗余项
  - `README.md` 与 `DOCUMENTATION.md` 更新为当前正式控制台结构：`dashboard/` 为后端与旧静态回退，`dashboard-ui/` 为正式 React 控制台
- **测试验证**:
  - `python3 -m py_compile dashboard/server.py`
  - `npm run build`
  - `python3` 导入 `dashboard/server.py` 验证 `_static_dir()` 已指向 `dashboard-ui/dist`
  - `git check-ignore -v events/runtime/openclaw.db events/results.jsonl agents/command/sessions/sessions.json`

---

## [2026-03-28 16:55] 新增阶段性实力评估与发展方向总结文档

**执行者**: Codex
**变更类型**: 文档 / 架构评估
**影响范围**: `OpenClaw-阶段性实力评估与发展方向总结.md`, `CHANGELOG.md`
**风险等级**: 低
**验证状态**: 已验证

### 变更详情
- **变更目的**:
  - 将本轮关于“整体架构实力、第三大板块完成度、与公开 GitHub 项目的相对位置、以及后续发展方向”的结论固化为阶段性文档，便于后续统一方向
- **技术内容**:
  - 新增 `OpenClaw-阶段性实力评估与发展方向总结.md`
  - 文档明确区分当前强项与短板，强调 OpenClaw 当前更像“安全作战控制系统”而非“成熟专家研究平台”
  - 对比 `OpenHands / PentestGPT / PentAGI / GPT Researcher / company-research-agent` 几类公开项目，收口 OpenClaw 当前的相对位置
  - 固化“未来应新增独立研究分析面，而不是把当前 worker 继续堆成超级专家”的方向判断
- **测试验证**:
  - 人工检查文档结构、引用对象与结论口径
  - 确认链接路径与本地文件名一致

---

## [2026-03-28 21:05] 补齐 campaign scope 校验、runtime writeback 与页面恢复能力

**执行者**: Codex
**变更类型**: 后端 / 前端 / 稳定性
**影响范围**: `events/services/control.py`, `events/db.py`, `events/knowledge/writeback.py`, `dashboard-ui/src/shared/api/stream.ts`, `dashboard-ui/src/pages/MissionPage.tsx`, `dashboard-ui/src/pages/CampaignPage.tsx`, `dashboard-ui/src/pages/ExecutionPage.tsx`, `dashboard-ui/src/pages/CommandBoardPage.tsx`, `dashboard-ui/src/pages/IntelKnowledgePage.tsx`, `dashboard-ui/src/styles.css`
**风险等级**: 中
**验证状态**: 已验证

### 变更详情
- **变更目的**:
  - 把当前最值钱的闭环补扎实：campaign 启动前先做 scope 校验，execution 结果可被后续检索，关键页面刷新后能恢复到原有上下文
- **技术内容**:
  - `create_campaign(...)` 现在会基于 revision `task_tree_json` 与 approval scope 做最小校验；命中受限类别、deny tool、高风险 tool 或未授权 interactive tool 时，campaign 会进入 `under_review`
  - `get_campaign_detail()` 增加 `scope_issues`，`control_campaign()` 阻止 `under_review` campaign 直接 `resume`，并新增最小 `approve` 放行闭环
  - 新增 `events/knowledge/writeback.py`，`upsert_result()` 写入 execution 结果后会同步 upsert 到 `knowledge.db`
  - `openStream()` 增加自动重连包装，`Mission / Campaign / Execution / Command Board / Intel` 进一步补齐 localStorage 与 URL query 恢复
  - `ExecutionPage` 与 `CampaignPage` 增加跨页面跳转入口，`CampaignPage / MissionPage` 增加 under-review campaign 的显式 Approve 操作，`styles.css` 统一按钮链接表现
  - `ExecutionPage` 进一步展示 task result 摘要与 artifact 创建时间，减少排障时来回切换数据源
  - `CampaignPage` 增加控制失败的页内反馈；`ExecutionPage` 为 timeline / artifact 增加 `Focus Task` 快捷定位，缩短排障路径
  - `MissionPage` 增加返回当前 workflow/campaign 的快捷入口；`CampaignPage` 增加最近控制动作摘要，便于判断当前控制链是否生效
  - `ExecutionPage -> MissionPage` 跳转现在会带上 `revision` 上下文，`MissionPage` 也会把当前选中 revision 写入 URL，方便从运行结果回看方案
  - `ExecutionPage` 与 `CampaignPage` 都补上直达具体 revision 的按钮，减少从运行态回到方案态时的二次查找
  - `Campaign` 增加最小 reject review 动作；`MissionPage` 增加 revision diff 摘要和 campaign 控制错误反馈，补齐 review 与 revision 回看闭环
  - `ExecutionPage` 增加 focused task 详情；`CommandBoardPage` 单独展示 runtime-derived 检索结果；`Campaign` 控制动作增加最小幂等保护，减少重复控制噪音
  - `Campaign` 明确暴露当前可执行动作；`Mission / Campaign / Execution / Command Board` 增加实时流连接/重连提示；`Command Board` 直接显示当前 workflow runtime cards，`Execution` 增加 focused artifact 详情
  - 新增 `/api/artifacts/:id` 与 artifact preview，`ExecutionPage` 可查看 focused artifact 详情；实时流增加退避重连和“已恢复”提示；补 `events/smoke_necessary.py` 作为统一 smoke 脚本，并验证主链通过
- **测试验证**:
  - `python3 -m py_compile events/db.py events/services/control.py events/knowledge/db.py events/knowledge/search.py events/knowledge/writeback.py dashboard/server.py`
  - `npm run build`
  - 本地冒烟验证 runtime writeback 检索成功
  - 本地冒烟验证受限 approval scope 下 campaign 进入 `under_review`

---

## [2026-03-28 20:28] 收尾统一搜索动词、局部回退词与标题口径

**执行者**: Codex
**变更类型**: 前端 / 共享展示
**影响范围**: `dashboard-ui/src/pages/CampaignPage.tsx`, `dashboard-ui/src/pages/ExecutionPage.tsx`, `dashboard-ui/src/pages/CommandBoardPage.tsx`, `dashboard-ui/src/pages/MissionPage.tsx`
**风险等级**: 低
**验证状态**: 已验证

### 变更详情
- **变更目的**:
  - 把最后几处还残留的搜索动词、回退词和局部标题口径统一掉，避免页面里继续出现零碎不一致
- **技术内容**:
  - `CampaignPage` 与 `ExecutionPage` 将筛选输入统一为 `Search ...` 口径
  - `CampaignPage` 的 active step `capability` 回退从 `unknown` 收口到 `none`
  - `CommandBoardPage` 的当前计划/工作流摘要改为复用统一回退规则
  - `MissionPage` 的标题输入和 `current main` 标记统一到当前英文口径
- **测试验证**:
  - `npm run build`

---

## [2026-03-28 20:20] 继续统一 Mission 与 Intel 页的 ID、回退词和搜索文案

**执行者**: Codex
**变更类型**: 前端 / 共享展示
**影响范围**: `dashboard-ui/src/pages/MissionPage.tsx`, `dashboard-ui/src/pages/IntelKnowledgePage.tsx`, `dashboard-ui/src/pages/CommandBoardPage.tsx`
**风险等级**: 低
**验证状态**: 已验证

### 变更详情
- **变更目的**:
  - 把剩余页面里还没完全接上共享规则的 ID 展示、回退文案和搜索 placeholder 收尾统一
- **技术内容**:
  - `MissionPage` 统一 revision / campaign / parent revision 的 ID 展示，补齐 `no summary` 回退，并整理局部 JSX 结构
  - `IntelKnowledgePage` 统一搜索 placeholder 与 `capability` 回退文案
  - `CommandBoardPage` 将 lookup placeholder 收口到统一英文搜索口径
- **测试验证**:
  - `npm run build`

---

## [2026-03-28 20:12] 统一时间、ID 与回退文案的共享展示规则

**执行者**: Codex
**变更类型**: 前端 / 共享展示
**影响范围**: `dashboard-ui/src/shared/ui/present.ts`, `dashboard-ui/src/pages/CampaignPage.tsx`, `dashboard-ui/src/pages/ExecutionPage.tsx`, `dashboard-ui/src/pages/CommandBoardPage.tsx`
**风险等级**: 低
**验证状态**: 已验证

### 变更详情
- **变更目的**:
  - 把几页里仍然分散手写的时间、ID 截断和空值回退规则收口到共享层，避免页面继续各写各的
- **技术内容**:
  - `present.ts` 新增 `formatFallback()`、`formatCompactId()`、`formatTimestamp()`
  - `CampaignPage` 统一 event feed 的时间位置、task id 展示和 revision id 截断
  - `ExecutionPage` 统一 workflow id、artifact task id、timeline 时间和 `none` 回退文案
  - `CommandBoardPage` 统一 workflow / campaign / revision id 展示，以及 campaign feed 时间前置
- **测试验证**:
  - `npm run build`

---

## [2026-03-28 20:02] 收尾统一 Mission 工作台与共享卡片规则

**执行者**: Codex
**变更类型**: 前端 / 共享展示
**影响范围**: `dashboard-ui/src/pages/MissionPage.tsx`, `dashboard-ui/src/components/RecordCard.tsx`, `dashboard-ui/src/components/SummaryGroup.tsx`, `dashboard-ui/src/shared/ui/present.ts`, `dashboard-ui/src/styles.css`
**风险等级**: 低
**验证状态**: 已验证

### 变更详情
- **变更目的**:
  - 继续把 Mission 页剩余空状态、按钮顺序、placeholder、params 顺序和卡片展示规则收口到统一基线
- **技术内容**:
  - `MissionPage` 统一 Mission List / Workbench / Revision Timeline 空状态，调整 revision 按钮顺序，并统一部分输入 placeholder
  - task tree 的 `params` 现在按 `executionMode / interactive / secondaryConfirmation / 其余字母序` 展示
  - `present.ts` 补充 `launchable / validated / pending` 状态文案和 tag tone 识别
  - `RecordCard` / `SummaryGroup` 改为过滤空标签，并为长 subtitle / line 加统一换行规则
  - 规范最近新增 `CHANGELOG` 条目的项目符号缩进
- **测试验证**:
  - `npm run build`

---

## [2026-03-28 19:36] 继续统一 Mission / Command Board / Catalog 的展示基线

**执行者**: Codex
**变更类型**: 前端 / 共享展示
**影响范围**: `dashboard-ui/src/pages/MissionPage.tsx`, `dashboard-ui/src/pages/CommandBoardPage.tsx`, `dashboard-ui/src/pages/CatalogPage.tsx`, `dashboard-ui/src/styles.css`
**风险等级**: 低
**验证状态**: 已验证

### 变更详情
- **变更目的**:
  - 将剩余主页面继续收口到统一状态文案、统计条语义、筛选条样式和空状态表现
- **技术内容**:
  - `MissionPage` 将 Mission、analysis、plan、campaign 的状态文本切到共享格式化逻辑，并增加统一空状态和统计条
  - `CommandBoardPage` 统一 Commander / Analyst 的状态、warning tag、feed 文案和筛选条布局
  - `CatalogPage` 改为复用共享 `RecordCard` 展示工具目录，并补上统计条与空状态
- **测试验证**:
  - `npm run build`

---

## [2026-03-28 19:49] 继续统一 Campaign / Execution / Intel 的筛选与空状态表现

**执行者**: Codex
**变更类型**: 前端 / 共享展示
**影响范围**: `dashboard-ui/src/pages/CampaignPage.tsx`, `dashboard-ui/src/pages/ExecutionPage.tsx`, `dashboard-ui/src/pages/IntelKnowledgePage.tsx`, `dashboard-ui/src/components/InsightSection.tsx`
**风险等级**: 低
**验证状态**: 已验证

### 变更详情
- **变更目的**:
  - 把剩余主页面的筛选条、状态文案、空状态、失败卡和 artifact 摘要继续收口到同一套表现层
- **技术内容**:
  - `CampaignPage` 统一 campaign 列表状态文案、筛选条布局、空状态和风险 tag 展示
  - `ExecutionPage` 统一 workflow 列表副标题、筛选文案、失败卡危险标识、artifact 摘要和空状态
  - `IntelKnowledgePage` 统一查询条布局、校验状态文案和空结果区块
  - `InsightSection` 增加统一空状态和嵌套卡片密度
- **测试验证**:
  - `npm run build`

---

## [2026-03-28 17:40] 补齐 Mission 动态方案的修订与分支闭环

**执行者**: Codex
**变更类型**: 代码 / 前端 / API
**影响范围**: `events/services/control.py`, `events/api/plans.py`, `dashboard/server.py`, `dashboard-ui/src/pages/MissionPage.tsx`, `dashboard-ui/src/shared/api/client.ts`
**风险等级**: 中
**验证状态**: 已验证

### 变更详情
- **变更目的**:
  - 将 Mission/Command Board 从“只能生成初始 revision”推进到“可继续修订、可从 revision 派生 branch”的最小闭环
- **技术内容**:
  - `create_plan_revision(...)` 增加 `parent_revision_id / created_by`，允许从父 revision 继承任务树与 outline
  - 新增 `create_branch_revision(...)`，支持从现有 revision 克隆出新 branch
  - 新增 `POST /api/missions/{id}/plans/{planId}/revise` 与 `POST /api/revisions/{id}/branches`
  - `MissionPage` 增加修订说明输入、基于现有 revision 继续修订、以及新 branch 创建入口
- **测试验证**:
  - `python3 -m py_compile events/*.py events/api/*.py events/executors/*.py events/knowledge/*.py events/services/*.py dashboard/server.py`
  - `npm run build`
  - `curl` 冒烟验证 Mission 创建、修订、分支接口成功返回

---

## [2026-03-28 17:52] 补齐 Mission 页的 revision 时间线与任务树预览

**执行者**: Codex
**变更类型**: 前端 / 交互
**影响范围**: `dashboard-ui/src/pages/MissionPage.tsx`, `dashboard-ui/src/styles.css`
**风险等级**: 低
**验证状态**: 已验证

### 变更详情
- **变更目的**:
  - 将 Mission 动态方案页从“能修订”推进到“能看清当前主 revision、revision 时间线和 task tree”
- **技术内容**:
  - 为 `MissionPage` 增加当前选中 revision 状态
  - 增加 `Current Main Revision` 摘要卡
  - 增加 revision timeline 列表与当前选中高亮
  - 增加 task tree preview 面板，显示 capability / task / notes / params
  - 为 revision 预览态补充样式
- **测试验证**:
  - `npm run build`

---

## [2026-03-28 18:03] 给 Mission 页补上 task tree 编辑并生成新 revision

**执行者**: Codex
**变更类型**: 前端 / 交互 / API 接线
**影响范围**: `dashboard-ui/src/pages/MissionPage.tsx`, `dashboard-ui/src/shared/api/client.ts`, `dashboard-ui/src/styles.css`
**风险等级**: 中
**验证状态**: 已验证

### 变更详情
- **变更目的**:
  - 让 Mission 工作台在发布前能直接调整 revision 的 task tree，而不是只能看预览
- **技术内容**:
  - 为选中 revision 增加本地 task tree draft
  - 支持修改 task 的 `category / task / notes`
  - 支持增删 task 节点
  - 支持将编辑结果通过 revise 接口保存为新的 revision
  - `reviseMissionPlan()` payload 扩展为可传 `task_tree / plan_outline`
- **测试验证**:
  - `npm run build`

---

## [2026-03-28 18:14] 为 Mission task tree 编辑器补上参数编辑与节点排序

**执行者**: Codex
**变更类型**: 前端 / 交互
**影响范围**: `dashboard-ui/src/pages/MissionPage.tsx`, `dashboard-ui/src/styles.css`
**风险等级**: 中
**验证状态**: 已验证

### 变更详情
- **变更目的**:
  - 让 task tree 编辑器真正能调整执行载荷，而不是只改节点标题和说明
- **技术内容**:
  - 支持 task `params` 的键值编辑、删除和新增
  - 支持 task 节点上移和下移
  - 为参数编辑区补充布局样式
- **测试验证**:
  - `npm run build`

---

## [2026-03-28 18:26] 补齐 Campaign 页的授权边界、主路线摘要与 kill 控制

**执行者**: Codex
**变更类型**: 前端 / API
**影响范围**: `events/services/control.py`, `dashboard-ui/src/pages/CampaignPage.tsx`
**风险等级**: 中
**验证状态**: 已验证

### 变更详情
- **变更目的**:
  - 让 Campaign 页从“只看状态”推进到“能看清 approval scope、当前 revision 主路线和控制上下文”
- **技术内容**:
  - `get_campaign_detail()` 增加 `branch_key / revision_no / revision_change_summary / denied_tools_json / network_scope_json`
  - `CampaignPage` 增加主路线摘要、事件快照、approval scope 详情、risk/interative 工具区、network scope 展示
  - 补上 `kill` 控制按钮
  - 事件流支持展示 `payload_json`，并从事件中提取最小 tool usage summary
- **测试验证**:
  - `python3 -m py_compile events/services/control.py`
  - `npm run build`

---

## [2026-03-28 18:38] 批量推进 Campaign 事件筛选与 Mission 节点级执行开关

**执行者**: Codex
**变更类型**: 前端 / API
**影响范围**: `events/services/control.py`, `dashboard-ui/src/pages/CampaignPage.tsx`, `dashboard-ui/src/pages/MissionPage.tsx`, `dashboard-ui/src/styles.css`
**风险等级**: 中
**验证状态**: 已验证

### 变更详情
- **变更目的**:
  - 一次性把 Campaign 和 Mission 两侧都推进到更接近真实发布/盯盘工作台的状态
- **技术内容**:
  - `get_campaign_detail()` 增加 `task_tree_json / plan_outline_json`
  - `CampaignPage` 增加事件 severity 过滤、关键词过滤、blocked reasons 摘要、active steps 区
  - `MissionPage` 为 task 节点增加 `executionMode / interactive / secondaryConfirmation` 开关
  - 补充对应布局样式
- **测试验证**:
  - `python3 -m py_compile events/services/control.py`
  - `npm run build`

---

## [2026-03-28 18:49] 再推进一批：Mission 节点克隆/批删与 Campaign 重规划会话摘要

**执行者**: Codex
**变更类型**: 前端
**影响范围**: `dashboard-ui/src/pages/MissionPage.tsx`, `dashboard-ui/src/pages/CampaignPage.tsx`, `dashboard-ui/src/styles.css`
**风险等级**: 中
**验证状态**: 已验证

### 变更详情
- **变更目的**:
  - 继续把 Mission 和 Campaign 两个工作台往“批量操作 + 状态摘要”方向推进
- **技术内容**:
  - `MissionPage` 增加 task 节点勾选、批量删除、单节点克隆
  - `CampaignPage` 增加统计条、最近重规划摘要、交互式会话摘要
  - 为新的批量选择和统计条补充样式
- **测试验证**:
  - `npm run build`

---

## [2026-03-28 19:01] 补齐 Execution 页的任务筛选、失败聚合与 artifact 摘要

**执行者**: Codex
**变更类型**: 前端
**影响范围**: `dashboard-ui/src/pages/ExecutionPage.tsx`
**风险等级**: 中
**验证状态**: 已验证

### 变更详情
- **变更目的**:
  - 让 Execution 从“查看列表”推进到“可用于排障和追踪 workflow 细节”的工作台
- **技术内容**:
  - 增加任务状态筛选和关键词过滤
  - 增加失败节点聚合区
  - 增加 artifact 摘要区和种类标签
  - 增加 timeline 类型过滤与统计条
  - 为 task / timeline 卡片增加 attempt/result 标签
- **测试验证**:
  - `npm run build`

---

## [2026-03-28 19:12] 推进 Command Board：双栏切换、卡片过滤与 analyst 摘要

**执行者**: Codex
**变更类型**: 前端
**影响范围**: `dashboard-ui/src/pages/CommandBoardPage.tsx`
**风险等级**: 中
**验证状态**: 已验证

### 变更详情
- **变更目的**:
  - 让 Command Board 更贴近文档里的 `commander / analyst` 双栏工作台，而不是固定摘要页
- **技术内容**:
  - 增加 `dual / stack` 视图切换
  - 增加 insight card 类型过滤
  - 增加 commander 统计条
  - 增加 analyst 状态摘要和卡片计数摘要
  - campaign feed 改为复用最近事件子集
- **测试验证**:
  - `npm run build`

---

## [2026-03-28 19:24] 开始统一 UI 基线：状态文案、tag 语义与统计条

**执行者**: Codex
**变更类型**: 前端 / 共享收口
**影响范围**: `dashboard-ui/src/shared/ui/present.ts`, `dashboard-ui/src/components/RecordCard.tsx`, `dashboard-ui/src/components/SummaryGroup.tsx`, `dashboard-ui/src/components/StatusBar.tsx`, `dashboard-ui/src/pages/CampaignPage.tsx`, `dashboard-ui/src/pages/ExecutionPage.tsx`, `dashboard-ui/src/pages/IntelKnowledgePage.tsx`, `dashboard-ui/src/styles.css`
**风险等级**: 中
**验证状态**: 已验证

### 变更详情
- **变更目的**:
  - 按已确认统一项，开始把状态文案、tag 颜色语义和统计条样式收敛成共享规则
- **技术内容**:
  - 新增 `shared/ui/present.ts`，统一状态标签和 tag tone 规则
  - `RecordCard`、`SummaryGroup` 改为自动应用共享 tag 语义
  - `StatusBar` 改为按共享 tone 渲染 chip
  - `CampaignPage`、`ExecutionPage` 开始复用统一状态文案
  - `IntelKnowledgePage` 增加统一统计条
- **测试验证**:
  - `npm run build`

---

## [2026-03-28 16:52] 固化智能指挥与情报研究两大板块的默认决策集

**执行者**: Codex
**变更类型**: 文档 / 规划 / 决策固化
**影响范围**: `OpenClaw-智能指挥与作战控制系统设计.md`, `OpenClaw-情报、记忆与研究分析设计.md`
**风险等级**: 低
**验证状态**: 已验证

### 变更详情
- **变更目的**:
  - 将“默认按推荐”的大批选型一次性固化为决策基线，减少后续细化阶段反复回头确认
- **技术内容**:
  - 在智能指挥板块中补充默认决策集，固定角色拆分、动态方案、托管模式、前端路线、日志和模型路由
  - 在情报研究板块中补充默认决策集，固定知识底座、分阶段 `C1/C2/C3`、来源策略、分类方式、研究分析使用路径和自动重规划口径
- **测试验证**:
  - 两个板块文档均已写入默认决策集
  - 后续细化可直接以此为基线继续推进

## [2026-03-28 17:08] 细化智能指挥板块的角色边界、动态方案和 campaign_auto 状态机

**执行者**: Codex
**变更类型**: 文档 / 技术设计细化
**影响范围**: `OpenClaw-智能指挥与作战控制系统设计.md`
**风险等级**: 低
**验证状态**: 已验证

### 变更详情
- **变更目的**:
  - 将智能指挥板块从大纲推进到可指导后续实现的技术层，先细化最关键的 3 个核心块
- **技术内容**:
  - 补充 `commander + analyst` 的职责边界、核心对象、接口建议和前端数据流
  - 补充动态方案系统的对象设计、状态机、revision/branch 模型和发布绑定方式
  - 补充 `campaign_auto` 的进入条件、授权对象、运行状态、自动重规划规则、交互式工具接入和前端确认层
- **测试验证**:
  - 细化内容已写入智能指挥主文档

## [2026-03-28 17:18] 同步细化智能指挥前端/API 与情报研究底座实现建议

**执行者**: Codex
**变更类型**: 文档 / 技术设计细化
**影响范围**: `OpenClaw-智能指挥与作战控制系统设计.md`, `OpenClaw-情报、记忆与研究分析设计.md`
**风险等级**: 低
**验证状态**: 已验证

### 变更详情
- **变更目的**:
  - 将两个板块同时从“结构大纲”推进到更接近实现落地的技术层，便于后续直接按对象、接口和流水线展开
- **技术内容**:
  - 在智能指挥板块中补充前端模块拆分、路由建议、SSE 事件类型、Mission/Execution/Campaign 接口契约和前端优化路线
  - 在情报研究板块中补充知识底座分阶段实现、核心表建议、artifact 组织、staging 入库流水线、信任模型、检索接口、analyst 上下文构建和条目模板
- **测试验证**:
  - 两个板块文档均已补充实现级建议

## [2026-03-28 17:32] 为智能指挥与情报研究两大板块补充可直接执行的实施任务清单

**执行者**: Codex
**变更类型**: 文档 / 实施计划细化
**影响范围**: `OpenClaw-智能指挥与作战控制系统设计.md`, `OpenClaw-情报、记忆与研究分析设计.md`
**风险等级**: 低
**验证状态**: 已验证

### 变更详情
- **变更目的**:
  - 将两大板块进一步收敛为“后续可直接按文档持续实现”的实施任务表
- **技术内容**:
  - 在智能指挥板块中补充 24 项实施任务，覆盖前端工程化、Mission/Command Board、动态方案、Execution、Campaign Auto、Defense 入口与 UI 收敛
  - 在情报研究板块中补充 24 项实施任务，覆盖知识底座 C1、staging 流水线、知识/经验条目、检索与 analyst 接口、C2 语义召回、前端承接与知识回写
  - 两个板块均补充默认执行顺序和达到“可独立执行”的标准
- **测试验证**:
  - 两份主文档均已补充实施任务清单

## [2026-03-28 17:44] 将两大实施清单继续压到文件级映射、依赖和验收标准

**执行者**: Codex
**变更类型**: 文档 / 执行蓝图细化
**影响范围**: `OpenClaw-智能指挥与作战控制系统设计.md`, `OpenClaw-情报、记忆与研究分析设计.md`
**风险等级**: 低
**验证状态**: 已验证

### 变更详情
- **变更目的**:
  - 让两份文档更接近“按文档连续实现”的执行蓝图，而不只是任务列表
- **技术内容**:
  - 在智能指挥板块中为各组实施任务补充建议文件路径、依赖顺序、验收标准和默认执行口径
  - 在情报研究板块中为各组实施任务补充建议文件路径、依赖顺序、验收标准和默认执行口径
- **测试验证**:
  - 两份文档均已具备文件级修改映射与每组验收标准

## [2026-03-28 16:28] 将当前工作正式拆分为三大板块

**执行者**: Codex
**变更类型**: 文档 / 任务拆分
**影响范围**: `OpenClaw-多Agent编排与Kali工具系统重构设计.md`, `OpenClaw-智能指挥与作战控制系统设计.md`, `OpenClaw-情报、记忆与研究分析设计.md`, `DOCUMENTATION.md`
**风险等级**: 低
**验证状态**: 已验证

### 变更详情
- **变更目的**:
  - 当前工作已经明显超出“多 Agent 编排与 Kali 工具系统重构”的单一范围，需要正式拆成新的独立任务板块，避免后续设计混写
- **技术内容**:
  - 将控制台板块文档重命名为 [OpenClaw-智能指挥与作战控制系统设计.md](/home/asus/.openclaw/OpenClaw-智能指挥与作战控制系统设计.md)
  - 新建第三个大板块文档 [OpenClaw-情报、记忆与研究分析设计.md](/home/asus/.openclaw/OpenClaw-情报、记忆与研究分析设计.md)
  - 将三大板块正式固定为：基础设施、智能指挥与控制、情报记忆与研究分析
  - 在原 [OpenClaw-多Agent编排与Kali工具系统重构设计.md](/home/asus/.openclaw/OpenClaw-多Agent编排与Kali工具系统重构设计.md) 顶部补充新的边界说明
  - 更新 [DOCUMENTATION.md](/home/asus/.openclaw/DOCUMENTATION.md)，把三大文档加入正式索引与阅读顺序
- **测试验证**:
  - 三个方案文档都已落地到本地
  - 文档索引已可检索到三大板块

## [2026-03-28 14:58] 增加内部控制台第一版并接入真实队列数据

**执行者**: Codex
**变更类型**: 代码 / 文档 / 前端
**影响范围**: `dashboard/*`, `README.md`, `DOCUMENTATION.md`
**风险等级**: 中
**验证状态**: 已验证

### 变更详情
- **变更目的**:
  - 为当前多 agent 编排体系补一个实用优先的内部控制台，作为授权团队的比赛和运维操作面
- **技术内容**:
  - 新增 `dashboard/server.py`，提供本地静态页面与 HTTP JSON API
  - 新增 `dashboard/index.html`、`dashboard/styles.css`、`dashboard/app.js`
  - 控制台支持 Mission / Execution / Catalog 三个工作台视图与可折叠面板
  - 增加自然语言情报输入，由 `command` 生成候选执行方案，并可一键发布整条方案任务
  - 新增代理工作台，按 capability 和执行代理统一浏览 worker 心跳、状态计数和最近任务
  - 控制台支持总览、任务发布、工具目录、recipe、最近任务、结果、worker/log 面板
  - UI 采用深色主背景 + 暗紫色强调，并加入 Kali 风格的视觉符号
  - `POST /api/publish` 已接入现有 `publish.py` 发布链，支持 `steady / rush`
- **测试验证**:
  - `python3 -m py_compile dashboard/server.py`
  - `node --check dashboard/app.js`
  - `python3 dashboard/server.py --host 127.0.0.1 --port 8787`
  - `curl -s http://127.0.0.1:8787/api/overview`
  - `curl -s http://127.0.0.1:8787/api/agents`
  - `curl -s http://127.0.0.1:8787/`
  - `curl -s -X POST http://127.0.0.1:8787/api/publish ...`
  - 已清理该发布测试产生的临时任务

## [2026-03-28 16:05] 固化 Commander/Analyst、自动化冲刺与 Defense 模式的后续路线

**执行者**: Codex
**变更类型**: 文档 / 规划
**影响范围**: `OpenClaw-多Agent编排与Kali工具系统重构设计.md`
**风险等级**: 低
**验证状态**: 已验证

### 变更详情
- **变更目的**:
  - 把你刚提出的未来扩展方向固定到主方案文档，避免后续上下文重置或阶段推进时丢失
- **技术内容**:
  - 在主方案中补充 `command` 的未来拆分方向：`commander + analyst`
  - 明确 `commander` 负责自然语言识别、协调和任务编排，`analyst` 负责情报、分析和未来知识库检索
  - 明确角色拆分的一个关键动因是：`analyst` 可长期分析而不阻塞 `commander` 对现场指令的响应
  - 明确前端未来应将 `commander` 与 `analyst` 做成并排工作台
  - 将“自动化冲刺模式”重新收敛为“目标驱动的自动化托管模式”，并补充严格日志与工具授权清单要求
  - 在后续阶段路线中加入自动化托管模式与 `defense` 模式开关的规划口径
  - 明确知识库属于后续正式阶段内容，现已转交新的“情报、记忆与研究分析”板块继续承接
- **测试验证**:
  - 文档已更新到本地主方案文件

## [2026-03-28 11:28] 将双模式推进到真实操作面

**执行者**: Codex
**变更类型**: 代码 / 文档 / 工具
**影响范围**: `events/publish.py`, `events/worker.py`, `events/executors/local_tool.py`, `agent-kits/common/bin/oc-toolfind`, `README.md`, `OpenClaw-多Agent编排与Kali工具系统重构设计.md`
**风险等级**: 中
**验证状态**: 已验证

### 变更详情
- **变更目的**:
  - 把 steady/rush 从概念推进到真实操作面，让你可以直接发布 rush 任务、设置 worker 默认档位并检索特殊工具
- **技术内容**:
  - `publish.py` 支持 `--execution-profile`、`--secondary-confirmation`、`--interactive`
  - `worker.py` 支持 `--execution-profile-default`
  - `local_tool.py` 按 steady/rush 切换允许工具集，对 high-risk rush 工具自动补 `rush-confirmed`
  - `oc-toolfind` 支持 `--profile` 和 `--special-only`
  - `README.md` 与主设计文档补充了 rush 实际命令模板
- **测试验证**:
  - `python3 -m py_compile events/publish.py events/worker.py events/executors/local_tool.py`
  - `python3 agent-kits/common/bin/oc-toolfind all --profile rush --special-only`
  - `python3 - <<'PY' ... validate_local_tool_request(...) ... PY`

## [2026-03-28 11:40] 清理代理直连链明文 DeepSeek key 并完成本地直连验证

**执行者**: Codex
**变更类型**: 配置 / 安全 / 文档
**影响范围**: `agents/*/agent/models.json`, `README.md`, `.env.deepseek.example`
**风险等级**: 中
**验证状态**: 已验证

### 变更详情
- **变更目的**:
  - 退出各正式代理 `models.json` 中的明文 DeepSeek key，同时确认 `openclaw agent --local --agent ...` 仍可用
- **技术内容**:
  - 将 8 个正式代理的 `models.json` 中 `providers.deepseek.apiKey` 全部改为 `${DEEPSEEK_API_KEY_*}` 占位符
  - 新增 `.env.deepseek.example` 作为环境变量模板
  - 在 `README.md` 中补充 `command` 与 `defense` 的环境变量示例
- **测试验证**:
  - `openclaw agent --local --agent offense-recon --message '只返回 OK' --json`
  - 返回成功，provider=`deepseek`，model=`deepseek-chat`

## [2026-03-28 11:52] 对齐 auth-profiles 到分类 DeepSeek env，并确认 openai-codex 凭据会被 runtime 自动回写

**执行者**: Codex
**变更类型**: 配置 / 安全 / 验证
**影响范围**: `agents/command/agent/auth-profiles.json`, `agents/offense-*/agent/auth-profiles.json`
**风险等级**: 中
**验证状态**: 已验证

### 变更详情
- **变更目的**:
  - 让各代理的 auth store 与分类 DeepSeek 环境变量对齐，并检查 `auth-profiles.json` 中的高敏感 OAuth 明文是否还能彻底退出
- **技术内容**:
  - 将各 `offense-*` 代理的 `auth-profiles.json` 从统一 `DEEPSEEK_API_KEY_OFFENSE` 收敛到各自分类变量
  - 为 `command` 增加 `deepseek:command` 的 env keyRef
  - 删除了重新冒出的 `agents/main`
- **测试验证**:
  - `DEEPSEEK_API_KEY_COMMAND=... openclaw agent --local --agent command --message '只返回 OK' --json`
  - `DEEPSEEK_API_KEY_RECON=... openclaw agent --local --agent offense-recon --message '只返回 OK' --json`
  - 两条都成功，`command` 走 `deepseek-reasoner`，`offense-recon` 走 `deepseek-chat`
  - 但运行时日志显示 `synced openai-codex credentials from external cli`，说明 `openai-codex` 的 OAuth 凭据会被 OpenClaw runtime 从外部 CLI 自动重新写回 `auth-profiles.json`

## 📋 变更记录格式规范

### 每次变更记录包含：
```markdown
## [YYYY-MM-DD HH:MM] - 变更描述

**执行者**: AI名称/工具名 (如: Codex/Claude Code/Cursor)
**变更类型**: [配置/代码/文档/工具/测试]
**影响范围**: [事件队列/代理/工具目录/配置/文档]
**风险等级**: [低/中/高]
**验证状态**: [待验证/已验证/失败]

### 变更详情
- **修改文件**: 文件路径列表
- **变更目的**: 简要说明为什么进行此变更
- **技术内容**: 具体修改的技术细节
- **测试验证**: 如何验证变更的有效性
- **回滚计划**: 如果出现问题如何回滚

### 前后对比
```diff
// 代码示例
- 旧代码
+ 新代码
```

### 验证结果
- ✅ 功能1验证通过

## [2026-03-28 10:30] 收敛 v2 文档协议并清理明文密钥

**执行者**: Codex
**变更类型**: 代码 / 文档 / 安全
**影响范围**: `ARCHITECTURE.md`, `events/EVENT_PROTOCOL.md`, `events/summarize.py`, `events/create_agents.py`, `events/apis.json`, `events/agent_consumer.py`, `OpenClaw-C方案-事件驱动任务队列-详细实施计划.md`, `README.md`
**风险等级**: 中
**验证状态**: 已验证

### 变更详情
- **修改文件**:
  - `ARCHITECTURE.md`
  - `events/EVENT_PROTOCOL.md`
  - `events/summarize.py`
  - `events/create_agents.py`
  - `events/apis.json`
  - `events/agent_consumer.py`
  - `OpenClaw-C方案-事件驱动任务队列-详细实施计划.md`
  - `README.md`
- **变更目的**:
  - 将文档、协议、汇总脚本和配置口径统一到当前 `SQLite/WAL + worker.py + executor` 正式路径，同时移除仓库中的明文 API 密钥
- **技术内容**:
  - 重写 `ARCHITECTURE.md`，明确 v2 正式基线、状态机、worker/executor、兼容层与退役路径
  - 重写 `events/EVENT_PROTOCOL.md`，拆分正式数据库字段与 JSONL 兼容字段
  - 改造 `events/summarize.py` 为优先读取数据库结果，必要时回退到 `results.jsonl`
  - 将 `events/create_agents.py` 降级为废弃占位脚本
  - 将 `events/apis.json` 中的明文 key 改为环境变量占位符
  - 在 `events/agent_consumer.py` 中加入 `${ENV_VAR}` 解析，兼容当前 API 调用链
  - 将旧实施计划文档改写为历史归档说明并清除敏感信息
  - 在 `README.md` 中补充环境变量示例
- **测试验证**:
  - `python3 -m py_compile events/summarize.py events/create_agents.py events/worker.py events/db.py events/publish.py events/status.py`
  - `python3 events/summarize.py --last 3`
  - `rg -n "sk-[A-Za-z0-9]+" ARCHITECTURE.md events/EVENT_PROTOCOL.md events/create_agents.py 'OpenClaw-C方案-事件驱动任务队列-详细实施计划.md' README.md DOCUMENTATION.md events`

## [2026-03-28 11:05] 补充 steady/rush 双模式与冲刺策略骨架

**执行者**: Codex
**变更类型**: 代码 / 文档
**影响范围**: `OpenClaw-多Agent编排与Kali工具系统重构设计.md`, `agent-kits/schema/policy.v1.schema.json`, `agent-kits/policies/*.json`, `events/policies.py`, `events/executors/local_tool.py`
**风险等级**: 中
**验证状态**: 已验证

### 变更详情
- **修改文件**:
  - `OpenClaw-多Agent编排与Kali工具系统重构设计.md`
  - `agent-kits/schema/policy.v1.schema.json`
  - `agent-kits/policies/common-safe.json`
  - `agent-kits/policies/wireless-usb-only.json`
  - `agent-kits/policies/rush-confirmed.json`
  - `events/policies.py`
  - `events/executors/local_tool.py`
- **变更目的**:
  - 为稳态模式与冲刺模式建立统一口径，并让高风险/交互式工具在冲刺模式下具备“二次确认后放行”的最小机制
- **技术内容**:
  - 在主设计文档中新增 steady/rush 双模式、无线外置网卡口径和 `WP-8`
  - 扩展 policy schema，加入 `execution_profiles`、`allow_interactive_in_rush`、`require_secondary_confirmation` 等字段
  - 新增 `rush-confirmed` 策略
  - `local_tool` 执行链开始支持 `executionProfile`、`secondaryConfirmation`、`interactive`
  - policy 检查允许在 `rush` 下对高风险交互式工具做显式确认放行
- **测试验证**:
  - `python3 -m py_compile events/policies.py events/executors/local_tool.py`
  - `python3 agent-kits/validators/validate_catalog.py`

## [2026-03-28 04:55] 落地 WP-1 数据库真源骨架

**执行者**: Codex
**变更类型**: 代码 / 文档
**影响范围**: `events/db.py`, `events/migrations/001_init.sql`, `events/runtime/.gitkeep`, `events/publish.py`, `events/status.py`
**风险等级**: 中
**验证状态**: 已验证

### 变更详情
- **修改文件**:
  - `events/db.py`
  - `events/migrations/001_init.sql`
  - `events/runtime/.gitkeep`
  - `events/publish.py`
  - `events/status.py`
- **变更目的**:
  - 为 v2 方案建立最小可用的 SQLite/WAL 任务真源骨架，同时保留当前 JSONL 兼容链路
- **技术内容**:
  - 新增 `db.py`，提供 SQLite 连接、WAL 初始化、migration 应用、任务插入、基础统计和 JSONL 补录能力
  - 新增 `001_init.sql`，建立 `tasks`、`task_attempts`、`task_dependencies`、`results`、`artifacts`、`workers` 等初始表
  - `publish.py` 改为数据库与 JSONL 双写
  - `status.py` 改为优先读取 SQLite 状态，并在双轨期自动补录最近任务文件
- **测试验证**:
  - `python3 -m py_compile events/db.py events/publish.py events/status.py`
  - 实际运行 `publish.py` 初始化数据库
  - 实际运行 `status.py` 验证状态页已切换到 SQLite/WAL 视图
  - 使用 `sqlite3` 直接检查 `tasks` 表数量
- **回滚计划**:
  - 删除 `events/runtime/openclaw.db`
  - 恢复 `publish.py` 和 `status.py` 到仅使用 JSONL 的版本
  - 删除 `events/db.py` 与 `events/migrations/001_init.sql`

### 验证结果
- ✅ SQLite 运行时数据库已创建
- ✅ migration 已自动应用
- ✅ `publish.py` 可同时写入数据库与 JSONL
- ✅ `status.py` 已优先读取 SQLite/WAL 统计视图

## [2026-03-28 05:21] 落地 WP-2 最小 worker 与双轨状态同步

**执行者**: Codex
**变更类型**: 代码
**影响范围**: `events/db.py`, `events/worker.py`, `events/agent_consumer.py`
**风险等级**: 中
**验证状态**: 已验证

### 变更详情
- **修改文件**:
  - `events/db.py`
  - `events/worker.py`
  - `events/agent_consumer.py`
- **变更目的**:
  - 为 v2 路线建立最小可运行的数据库 worker，并解决双轨期数据库/JSONL 状态漂移导致的重复执行风险
- **技术内容**:
  - 在 `db.py` 中新增 worker 注册、心跳、claim、running、complete、retry_wait / dead_letter 调度、legacy 状态同步等接口
  - 新增 `worker.py`，从数据库 claim 任务并驱动 `leased -> running -> succeeded/failed/retry_wait` 流转
  - `worker.py` 在双轨期会同步更新 `JSONL` 任务状态，避免旧 cron 消费者再次拾取同一任务
  - `agent_consumer.py` 也新增数据库状态回写，确保旧链路执行时不会让数据库长期停留在旧状态
- **测试验证**:
  - `python3 -m py_compile events/db.py events/agent_consumer.py events/worker.py`
  - 使用 `publish.py` + `worker.py --once` 完成两轮烟雾测试
  - 验证数据库中 `tasks/task_attempts/workers` 数据已生成
  - 验证 `JSONL` 状态会随新 worker 同步为 `processing/completed`
- **回滚计划**:
  - 删除 `events/worker.py`
  - 回退 `db.py` 中的 worker/状态同步接口
  - 回退 `agent_consumer.py` 的数据库回写逻辑

### 验证结果
- ✅ 新 `worker.py` 已可从 SQLite 真源执行任务
- ✅ `task_attempts` 与 `workers` 表已有实际记录
- ✅ 双轨期数据库与 JSONL 状态已可同步，避免最直接的重复消费风险

## [2026-03-28 05:40] 落地 WP-3 最小 executor 分层与结果入库

**执行者**: Codex
**变更类型**: 代码
**影响范围**: `events/worker.py`, `events/db.py`, `events/executors/*`, `events/policies.py`
**风险等级**: 中
**验证状态**: 已验证

### 变更详情
- **修改文件**:
  - `events/worker.py`
  - `events/db.py`
  - `events/executors/base.py`
  - `events/executors/agent_api.py`
  - `events/executors/local_tool.py`
  - `events/policies.py`
- **变更目的**:
  - 将执行逻辑从旧消费者中拆出，建立最小 `executor` 分层，并让数据库 `results/artifacts` 表开始承载正式结果
- **技术内容**:
  - 新增 `executors/base.py`，定义统一执行上下文和返回结构
  - 新增 `executors/agent_api.py`，承接现有按类别 API 调用逻辑
  - 新增 `executors/local_tool.py`，提供低风险白名单本地工具执行能力，并落 stdout/stderr artifact
  - 新增 `policies.py`，提供最小本地工具策略检查
  - `worker.py` 改为按任务选择 executor，而不是直接调用旧消费者执行函数
  - `db.py` 增加 `results/artifacts` 写入和 attempt 元数据更新接口
- **测试验证**:
  - `python3 -m py_compile` 检查新旧相关文件
  - 通过 `agent_api` 路径完成一轮 smoke test
  - 通过 `local_tool` 路径完成一轮 smoke test（白名单工具 `curl --version`）
  - 验证数据库中的 `tasks/results/artifacts/task_attempts` 状态与内容
  - 清理 smoke test 残留，并清理一轮由 sqlite CLI 产生的孤立记录
- **回滚计划**:
  - 删除 `events/executors/*` 与 `events/policies.py`
  - 将 `worker.py` 回退为直接调用旧消费者执行逻辑
  - 回退 `db.py` 中的结果与 artifact 写入接口

### 验证结果
- ✅ `agent_api` 与 `local_tool` 两类 executor 均已跑通
- ✅ 数据库 `results` 与 `artifacts` 表已经可以承接执行结果
- ✅ 本地工具执行已受到最小白名单和命令一致性校验约束

## [2026-03-28 05:50] 落地 WP-4/5 最小 catalog schema、recipe 与 policy

**执行者**: Codex
**变更类型**: 代码 / 数据
**影响范围**: `agent-kits/schema/*`, `agent-kits/recipes/*`, `agent-kits/policies/*`, `agent-kits/validators/validate_catalog.py`, `agent-kits/*/catalog/*.json`, `agent-kits/common/bin/oc-toolfind`, `agent-kits/common/bin/oc-toolcat`, `events/tool_registry.py`, `events/policies.py`, `events/executors/local_tool.py`
**风险等级**: 中
**验证状态**: 已验证

### 变更详情
- **修改文件**:
  - `agent-kits/schema/tool-catalog.v2.schema.json`
  - `agent-kits/schema/recipe.v1.schema.json`
  - `agent-kits/schema/policy.v1.schema.json`
  - `agent-kits/recipes/recon.port-scan.json`
  - `agent-kits/recipes/web.dir-brute.json`
  - `agent-kits/recipes/wireless.passive-scan.json`
  - `agent-kits/policies/common-safe.json`
  - `agent-kits/policies/wireless-usb-only.json`
  - `agent-kits/policies/proxy-protected.json`
  - `agent-kits/validators/validate_catalog.py`
  - `agent-kits/offense-kit/catalog/front-tools.json`
  - `agent-kits/defense-kit/catalog/front-tools.json`
  - `agent-kits/cmd-special/catalog/rare-tools.json`
  - `agent-kits/common/bin/oc-toolfind`
  - `agent-kits/common/bin/oc-toolcat`
  - `events/tool_registry.py`
  - `events/policies.py`
  - `events/executors/local_tool.py`
- **变更目的**:
  - 将工具目录升级为可校验的 catalog v2，并让本地工具执行可以由 recipe 和 policy 驱动，而不是只靠手工传 `command`
- **技术内容**:
  - 新增 catalog / recipe / policy 的最小 schema 文件
  - 为 `recon.port-scan`、`web.dir-brute`、`wireless.passive-scan` 建立最小 recipe
  - 为 `common-safe`、`wireless-usb-only`、`proxy-protected` 建立最小 policy
  - 重写 offense / defense / rare catalog 条目，补充 `id/tags/target_types/requires_sudo/interactive/read_only/destructive/risk_level/default_timeout_seconds/policy_refs`
  - 新增 `validate_catalog.py` 用于基础校验
  - 新增 `tool_registry.py` 用于加载 catalog / recipe / policy，并支持 recipe 命令解析
  - `local_tool executor` 现在可以在不给 `command` 的情况下，按 recipe 自动选择工具和拼接命令
  - `oc-toolfind` 增加 `risk_level` / `target_type` 等字段搜索和过滤
  - `oc-toolcat` 增加 recipes / policies 视图
- **测试验证**:
  - `python3 -m py_compile` 检查新增 Python 文件
  - 运行 `python3 agent-kits/validators/validate_catalog.py`
  - 运行 `oc-toolfind offense nmap --risk-level low --target-type host`
  - 通过 `publish.py + worker.py` 执行一次 recipe 驱动的 `recon port-scan` 本地工具任务
  - 清理 recipe smoke test 在数据库、JSONL 和 artifact 目录中的残留
- **回滚计划**:
  - 删除新增 schema / recipe / policy / validator / registry 文件
  - 恢复 catalog JSON 到旧结构
  - 回退 `local_tool executor`、`oc-toolfind`、`oc-toolcat` 的 recipe / policy 相关逻辑

### 验证结果
- ✅ catalog / recipe / policy 基础校验已通过
- ✅ `local_tool executor` 已能按 recipe 自动选择 `nmap`
- ✅ 新 catalog 字段已经可以通过 `oc-toolfind` 查询和过滤

## [2026-03-28 06:01] 切换 cron 正式入口到数据库 worker

**执行者**: Codex
**变更类型**: 代码 / 运维
**影响范围**: `events/setup_agent_crons.py`, `README.md`, 当前用户 crontab
**风险等级**: 中
**验证状态**: 已验证

### 变更详情
- **修改文件**:
  - `events/setup_agent_crons.py`
  - `README.md`
- **变更目的**:
  - 将按类别的定时执行入口从旧 `agent_consumer.py` 切换到新 `worker.py`，使正式运行路径与当前 v2 实现一致
- **技术内容**:
  - `setup_agent_crons.py` 改为生成 `worker.py --once --category <category>` 的 cron 作业
  - `README.md` 中的正式执行路径、技术栈和目录结构已更新为 SQLite/WAL + `worker.py`
  - 实际重写当前 crontab，将 6 个类别的分钟任务全部切到 `worker.py`
- **测试验证**:
  - `python3 -m py_compile events/setup_agent_crons.py`
  - 运行 `python3 setup_agent_crons.py`
  - 使用 `crontab -l` 验证当前分钟级任务已指向 `worker.py`
  - 运行 `python3 status.py` 确认切换后状态页正常
- **回滚计划**:
  - 将 crontab 中的 `worker.py` 改回 `agent_consumer.py`
  - 恢复 `setup_agent_crons.py` 和 `README.md` 到旧入口说明

### 验证结果
- ✅ 当前 crontab 已按 6 类全部切换到 `worker.py`
- ✅ `README.md` 已反映新的正式执行主线
- ✅ 切换后状态页与日志仍正常

## [2026-03-28 04:40] 新增 v2 统一架构与工具目录升级蓝图

**执行者**: Codex
**变更类型**: 文档
**影响范围**: `OpenClaw-多Agent编排与Kali工具系统重构设计.md`, `DOCUMENTATION.md`
**风险等级**: 低
**验证状态**: 已验证

### 变更详情
- **修改文件**:
  - `OpenClaw-多Agent编排与Kali工具系统重构设计.md`
  - `DOCUMENTATION.md`
- **变更目的**:
  - 将后续所有阶段的统一架构演进方案落地到本地文档，避免上下文重置后丢失设计结论
- **技术内容**:
  - 新增 v2 统一方案文档，后续改名为 `OpenClaw-多Agent编排与Kali工具系统重构设计.md`
  - 整合任务内核升级、工具目录 schema 升级、worker/executor 分层、全阶段路线图和现有代码修改映射
  - 补充第一批实施任务清单（WP-1 ~ WP-7），便于后续按包推进
  - 在文档导航中加入该方案文档，并提升为后续阶段的优先参考资料
- **测试验证**:
  - 检查文档文件是否创建成功
  - 检查 `DOCUMENTATION.md` 是否能导航到新文档
- **回滚计划**:
  - 删除新增文档
  - 恢复 `DOCUMENTATION.md` 对应段落

### 验证结果
- ✅ v2 统一方案文档已写入本地
- ✅ 文档导航已加入新方案入口

## [2026-03-28] 基线路径与遗留实现口径收敛

**修改类型**: 文档修正 / 遗留脚本降级
**影响范围**: `README.md`, `ARCHITECTURE.md`, `workspaces/command/AGENTS.md`, `agents/offense-*/AGENTS.md`, `events/publish.py`, `events/update_openclaw_config.py`
**验证状态**: 已验证

### 修改内容
- 统一正式队列路径表述为 `tasks-YYYY-MM-DD.jsonl`
- 明确 `events/agent_consumer.py` 为正式消费者路径
- 将 `openclaw agent --agent offense-*` 降级为调试/应急入口说明
- 明确 `workspaces/offense` 与旧 `consume.py` 为遗留路径
- 将 `events/update_openclaw_config.py` 标记为废弃并默认禁止运行

### 测试验证
- 检查核心文档中的正式路径说明是否一致
- 检查专业攻击代理文档是否已降级直接调用说明
- 检查废弃脚本是否会直接退出并给出风险提示

### 验证结果
- ✅ 正式路径表述已统一到分片任务文件
- ✅ 直接调用说明已降级为调试/应急入口
- ✅ 高风险旧配置脚本已被阻断

## [2026-03-28] 遗留消费者路径清理

**修改类型**: 遗留实现下线 / 队列兼容收缩
**影响范围**: `events/status.py`, `events/archive.py`, `events/consume.py`, `workspaces/offense*/consume.py`
**验证状态**: 已验证

### 修改内容
- `status.py` 只统计正式分片任务文件，不再纳入 `tasks.jsonl` legacy 路径
- `archive.py` 只归档正式分片任务文件，不再处理旧 `tasks.jsonl`
- `events/consume.py` 改为废弃阻断入口，提示使用 `events/agent_consumer.py`
- `workspaces/offense` 及各 `workspaces/offense-*` 下的 `consume.py` 改为废弃阻断入口

### 测试验证
- 编译检查所有改动后的 Python 脚本
- 检查废弃入口是否输出明确错误信息并退出
- 检查 `status.py` / `archive.py` 中不再包含 `tasks.jsonl` 兼容逻辑

### 验证结果
- ✅ 旧消费者脚本不再执行历史逻辑
- ✅ 状态与归档逻辑已收敛到正式分片文件

## [2026-03-28] 贡献指南与遗留目录口径补充

**修改类型**: 文档修正
**影响范围**: `CONTRIBUTING.md`, `README.md`
**验证状态**: 已验证

### 修改内容
- 在 `CONTRIBUTING.md` 中补充当前正式基线说明
- 明确 `events/consume.py`、`workspaces/offense/consume.py` 和各 `workspaces/offense-*/consume.py` 不应继续承载新逻辑
- 补充历史遗留目录识别说明，包括 `workspaces/offense/` 和 `agents/offense-deprecated-*`
- 在 `README.md` 中补充 deprecated offense 目录不属于当前正式 8 代理体系

### 测试验证
- 检查贡献指南中的正式路径与当前仓库状态是否一致
- 检查 README 中的遗留目录说明是否可读且不与现有架构冲突

### 验证结果
- ✅ 贡献指南已与当前正式执行链保持一致
- ✅ 遗留目录与正式目录的边界已更明确

## [2026-03-28] 遗留目录标记补充

**修改类型**: 文档修正 / 历史目录标记
**影响范围**: `workspaces/offense/*`, `agents/offense-deprecated-*`
**验证状态**: 已验证

### 修改内容
- 将 `workspaces/offense/AGENTS.md` 明确改为历史工作区说明
- 在 `workspaces/offense/TOOLS.md` 和 `workspaces/offense/BOOTSTRAP.md` 中补充 deprecated 说明
- 为 `agents/offense-deprecated-*` 与 `agents/offense-backup-deprecated-*` 添加 `README.md`，明确其仅为历史保留目录

### 测试验证
- 检查遗留目录中的说明文件是否明确指出“不属于正式执行路径”
- 检查说明内容是否与当前 8 代理正式基线一致

### 验证结果
- ✅ 共享 offense workspace 已被明确标记为历史目录
- ✅ deprecated agent 目录已具备清晰的人类可读说明

## [2026-03-28] 删除未接入的遗留代理目录

**修改类型**: 目录清理
**影响范围**: `agents/codex`, `agents/main`
**验证状态**: 已验证

### 修改内容
- 删除 `agents/codex`
- 删除 `agents/main`

### 变更原因
- 两个目录都不在当前正式 `openclaw.json` 的 8 代理注册列表中
- `agents/codex` 仅包含空会话索引，没有有效代理配置
- `agents/main` 未发现实际会话记录，不属于当前正式架构的一部分

### 测试验证
- 确认目录已从文件系统删除
- 确认当前正式代理配置未包含 `codex` 或 `main`

### 验证结果
- ✅ `agents/codex` 已删除
- ✅ `agents/main` 已删除

## [2026-03-28] 删除共享 offense 与 deprecated offense 目录

**修改类型**: 目录清理
**影响范围**: `agents/offense-deprecated-20260327_235506`, `agents/offense-backup-deprecated-20260327_235514`, `workspaces/offense`
**验证状态**: 已验证

### 修改内容
- 删除 `agents/offense-deprecated-20260327_235506`
- 删除 `agents/offense-backup-deprecated-20260327_235514`
- 删除 `workspaces/offense`

### 变更原因
- 通用 `offense` 已被 6 个专业化 `offense-*` 代理取代
- 共享 `workspaces/offense` 已不再承担正式执行职责
- deprecated offense 目录仅为历史残留，继续保留会增加误用和维护噪音

### 测试验证
- 确认 3 个目录已从文件系统删除
- 确认顶层 `agents/` 和 `workspaces/` 仅保留正式体系目录

### 验证结果
- ✅ 顶层 `agents/` 已收敛到正式 8 代理体系
- ✅ 顶层 `workspaces/` 已收敛到正式工作区体系

## [2026-03-28] 清理过时说明与测试配置

**修改类型**: 文档修正 / 配置清理
**影响范围**: `README.md`, `CONTRIBUTING.md`, `DOCUMENTATION.md`, `OpenClaw-C方案-事件驱动任务队列-总结报告.md`, `openclaw.json.GOLDEN`, `openclaw-new.json`, `openclaw.test-offense-*.json`, `openclaw.test-wireless.json`
**验证状态**: 已验证

### 修改内容
- 修正文档中仍假定共享 `offense` 目录存在的说明
- 修正文档中关于遗留项数量和定位的表述
- 删除仍包含通用 `offense` 路径的过时测试配置与旧 Golden 配置

### 测试验证
- 检查主文档中的正式结构说明是否与当前目录一致
- 检查已删除的过时测试配置不再保留通用 `offense` 路径入口

### 验证结果
- ✅ 主文档与当前目录结构已进一步对齐
- ✅ 明显过时的测试配置已移除

## [2026-03-28] 删除废弃脚本与旧消费者日志

**修改类型**: 文件清理
**影响范围**: `events/update_openclaw_config.py`, `events/fix_status.py`, `events/consumer.log`
**验证状态**: 已验证

### 修改内容
- 删除 `events/update_openclaw_config.py`
- 删除 `events/fix_status.py`
- 删除历史 `events/consumer.log`

### 变更原因
- `update_openclaw_config.py` 会把配置回退到旧共享 `offense` workspace 路径
- `fix_status.py` 是一次性的历史修复脚本，不应继续进入正式维护范围
- `consumer.log` 对应旧消费者路径，保留会干扰当前排障

### 测试验证
- 确认 3 个文件已从文件系统删除
- 确认 cron 设置脚本仍明确以 `agent_consumer.py` 为正式入口

### 验证结果
- ✅ 废弃脚本已清理
- ✅ 旧消费者日志已移除

## [2026-03-28] 清理旧队列文件与状态页遗留引用

**修改类型**: 文件清理 / 监控修正
**影响范围**: `events/status.py`, `events/tasks.jsonl`, `events/archive.log`
**验证状态**: 已验证

### 修改内容
- 更新 `status.py`，不再检查已删除的 `consumer.log`
- 改为显示各类别代理日志的最近更新时间
- 删除旧 `events/tasks.jsonl`
- 删除历史 `events/archive.log`

### 测试验证
- 确认 `status.py` 不再依赖 `consumer.log`
- 确认旧 `tasks.jsonl` 与 `archive.log` 已删除

### 验证结果
- ✅ 状态页已不再引用旧消费者日志
- ✅ 旧队列文件与历史归档日志已移除
- ❌ 功能2发现问题
- ⚠️  注意事项

### 相关文档更新
- [ ] ARCHITECTURE.md
- [ ] CONTRIBUTING.md  
- [ ] 其他文档
```
---

## 🗓️ 变更记录历史

### 2026-03-28 02:55 - 创建变更记录系统和Codex权限配置

**执行者**: OpenClaw Command Agent  
**变更类型**: 配置/文档  
**影响范围**: 配置/工具权限/文档  
**风险等级**: 低  
**验证状态**: 已验证

#### 变更详情
- **修改文件**: 
  - `/home/asus/.openclaw/openclaw.json` - 更新exec权限配置
  - `/home/asus/.openclaw/CHANGELOG.md` - 创建本文件
  - `/home/asus/.openclaw/ACP_CONFIG.md` - 创建ACP配置指南
- **变更目的**: 
  1. 为Codex/AI代码助手提供最大权限
  2. 确保能使用Kali工具和硬件设备测试代码
  3. 建立规范的变更记录系统
- **技术内容**:
  1. 在openclaw.json中更新tools.exec配置:
     - `security: "full"` - 允许所有命令
     - `ask: "off"` - 不要求批准
     - `elevated: true` - 允许sudo权限
     - 添加Kali工具路径到pathPrepend
  2. 创建ACP_CONFIG.md提供Codex调用指南
  3. 创建CHANGELOG.md变更记录模板
- **测试验证**:
  - 验证配置语法: `openclaw config validate --json`
  - 测试工具路径: `oc-toolfind offense recon`
  - 验证exec权限: 执行简单命令测试
- **回滚计划**:
  1. 恢复openclaw.json备份
  2. 删除新创建的文档文件
  3. 重启Gateway服务

#### 前后对比
```diff
# openclaw.json - tools.exec部分
  "tools": {
    "profile": "coding",
    "exec": {
-     "pathPrepend": [
-       "/home/asus/.openclaw/agent-kits/common/bin"
-     ]
+     "pathPrepend": [
+       "/home/asus/.openclaw/agent-kits/common/bin",
+       "/usr/bin",
+       "/usr/sbin", 
+       "/bin",
+       "/sbin",
+       "/usr/local/bin",
+       "/usr/local/sbin"
+     ],
+     "security": "full",
+     "ask": "off",
+     "elevated": true,
+     "host": "gateway"
    }
  }
```

#### 验证结果
- ✅ openclaw.json配置验证通过
- ✅ 变更记录文件创建成功
- ✅ ACP配置指南创建完成
- ⚠️ 需要重启Gateway使配置生效

#### 相关文档更新
- [x] README.md - 添加变更记录说明
- [x] CONTRIBUTING.md - 添加变更记录要求
- [x] DOCUMENTATION.md - 添加变更记录索引

---

### 2026-03-28 03:20 - 添加Codex/AI协作规则：更好的方案需要先讨论

**执行者**: OpenClaw Command Agent  
**变更类型**: 文档/规范  
**影响范围**: 所有AI协作流程  
**风险等级**: 低  
**验证状态**: 已验证

#### 变更详情
- **修改文件**: 
  - `/home/asus/.openclaw/ACP_CONFIG.md` - 添加Codex/AI协作规则部分
  - `/home/asus/.openclaw/CONTRIBUTING.md` - 添加AI协作核心规则
  - `/home/asus/.openclaw/README.md` - 添加协作规则常见问题
- **变更目的**: 
  1. 明确告诉Codex/AI：可以用更好的计划方案，但必须先与用户讨论
  2. 建立规范的AI协作流程
  3. 防止未经讨论的"改进"破坏现有系统
- **技术内容**:
  1. 在ACP_CONFIG.md中添加"🤝 Codex/AI协作规则"部分：
     - 核心原则：提出更好的方案，但要先讨论
     - 方案提出流程和讨论要求
     - 实施前检查清单和违规处理
  2. 在CONTRIBUTING.md中添加"🤝 AI协作核心规则"部分：
     - 为什么需要讨论规则
     - 标准方案提出流程
     - 实施前条件和成功案例
  3. 在README.md常见问题中添加AI协作规则说明
- **测试验证**:
  - 验证文档格式：`python3 -m markdown -x extra ACP_CONFIG.md > /dev/null`
  - 检查关键词：`grep -r "必须先与用户讨论" *.md`
  - 验证文档链接有效性
- **回滚计划**:
  1. 恢复文档文件的备份版本
  2. 删除添加的协作规则部分
  3. 更新相关文档索引

#### 验证结果
- ✅ 所有文档格式验证通过
- ✅ 协作规则关键词检查通过
- ✅ 文档链接有效性检查通过
- ✅ 变更记录已按规范更新

#### 相关文档更新
- [x] ACP_CONFIG.md - 添加协作规则
- [x] CONTRIBUTING.md - 添加协作规则  
- [x] README.md - 添加常见问题
- [x] CHANGELOG.md - 记录本次变更
- [ ] DOCUMENTATION.md - 需要更新文档统计

---

## 📊 变更统计

### 按类型统计
| 变更类型 | 次数 | 最近变更 |
|----------|------|----------|
| 配置变更 | 1 | 2026-03-28 |
| 文档更新 | 2 | 2026-03-28 |
| 代码修改 | 0 | - |
| 工具添加 | 0 | - |
| 测试更新 | 0 | - |

### 按执行者统计
| 执行者 | 次数 | 最近活动 |
|--------|------|----------|
| Command Agent | 2 | 2026-03-28 |
| Codex | 0 | - |
| Claude Code | 0 | - |
| Cursor | 0 | - |

### 风险分布
| 风险等级 | 次数 | 比例 |
|----------|------|------|
| 低 | 2 | 100% |
| 中 | 0 | 0% |
| 高 | 0 | 0% |

---

## 🔧 变更流程规范

### 1. 变更前准备
```bash
# 1.1 检查当前状态
openclaw gateway status
cd ~/.openclaw/events && python3 status.py

# 1.2 备份当前配置
cp openclaw.json openclaw.json.backup.$(date +%Y%m%d_%H%M%S)

# 1.3 记录变更计划
echo "## [$(date +%Y-%m-%d\ %H:%M)] - 计划变更" >> CHANGELOG_PLAN.md
```

### 2. 执行变更
```bash
# 2.1 执行具体修改操作
# 2.2 验证修改语法
python3 -m py_compile 修改的文件.py  # 如果是Python

# 2.3 测试修改效果
./test_修改的功能.sh
```

### 3. 验证和记录
```bash
# 3.1 更新变更记录
# 按照模板格式更新CHANGELOG.md

# 3.2 验证系统完整性
./health_dashboard.sh

# 3.3 提交到版本控制
git add 修改的文件
git commit -m "类型: 变更描述"
git push
```

### 4. 监控和回滚
```bash
# 4.1 监控变更影响
tail -f events/*.log

# 4.2 准备回滚脚本
cp 修改的文件 修改的文件.backup

# 4.3 如果出现问题
# 执行回滚计划
```

---

## 📝 Codex/AI变更专用指南

### 每次修改必须:
1. **记录变更**: 在CHANGELOG.md中添加记录
2. **验证权限**: 确保有足够权限执行修改
3. **测试功能**: 运行相关测试验证修改
4. **更新文档**: 同步更新相关文档
5. **备份状态**: 备份修改前的状态

### Codex调用示例:
```bash
# 通过OpenClaw ACP调用Codex
sessions_spawn runtime="acp" agentId="codex" task="修改任务描述"

# 需要包含的上下文
- 本CHANGELOG.md文件
- 相关代码文件
- 测试脚本
- 回滚计划
```

### 硬件设备访问权限:
```bash
# USB WiFi适配器访问
oc-mon0  # 需要sudo权限

# 其他硬件设备
# 确保配置了相应的exec权限
```

---

## 🚨 紧急变更处理

### 发现问题时:
1. **立即停止**: 停止相关操作
2. **诊断问题**: 查看日志和错误信息
3. **评估影响**: 确定影响范围
4. **执行回滚**: 按照回滚计划操作
5. **记录问题**: 在变更记录中记录问题和解决方案

### 回滚命令示例:
```bash
# 回滚配置
cp openclaw.json.backup.20260328_025500 openclaw.json

# 重启服务
openclaw gateway restart

# 验证回滚
openclaw gateway status
```

---

## 📈 变更质量指标

### 成功变更标准:
- ✅ 所有测试通过
- ✅ 文档同步更新
- ✅ 变更记录完整
- ✅ 无回归问题
- ✅ 性能影响可接受

### 变更评审要点:
1. **技术正确性**: 修改是否解决了问题
2. **架构一致性**: 是否符合C方案架构原则
3. **安全合规**: 是否遵守安全约束
4. **可维护性**: 代码是否清晰易维护
5. **测试覆盖**: 是否有足够的测试验证

---

## 2026-03-28 17:58

### 文档执行蓝图继续压实

本轮继续把两大新板块方案从“实施清单”压到“可直接照着实现”的层级：

- 为 [OpenClaw-智能指挥与作战控制系统设计.md](/home/asus/.openclaw/OpenClaw-智能指挥与作战控制系统设计.md) 新增：
  - 核心对象字段清单
  - 第一版 API / SSE / 页面清单
  - Mission / Plan / Campaign 的阶段门槛
  - 前后端回归检查清单
  - 默认直接实施规则
- 为 [OpenClaw-情报、记忆与研究分析设计.md](/home/asus/.openclaw/OpenClaw-情报、记忆与研究分析设计.md) 新增：
  - 核心表字段与 staging 流水线阶段
  - 检索接口与统一返回结构
  - 高价值来源分级
  - C1/C2 与 analyst 检索闭环门槛
  - 数据质量与分类检查清单
  - 默认直接实施规则

本轮目标是让后续实现可以默认按文档顺序直接推进，尽量减少中途再次拆解方案的成本。

## 2026-03-28 18:07

### 两大板块补充实现附录

继续为两份主方案补足最后一层实现附录：

- 为 [OpenClaw-智能指挥与作战控制系统设计.md](/home/asus/.openclaw/OpenClaw-智能指挥与作战控制系统设计.md) 新增：
  - 页面字段表
  - Mission / Plan / Campaign 请求响应示例
  - Workflow 与 SSE 消息骨架
  - React 模块建议与默认编码顺序
- 为 [OpenClaw-情报、记忆与研究分析设计.md](/home/asus/.openclaw/OpenClaw-情报、记忆与研究分析设计.md) 新增：
  - SQL schema 草案
  - `ingestion_jobs` / `staging_items` 状态流转
  - `intel_item / knowledge_entry / experience_record / analyst_context` 示例 JSON
  - 检索响应骨架
  - 默认 analyst context 构建规则
  - 默认编码顺序

此轮完成后，两份文档已经基本进入“按文档顺序直接持续实现”的状态。

## 2026-03-28 18:32

### 智能指挥第一批代码骨架落地

开始按新板块文档实际落代码，第一批完成以下内容：

- 新增 `events/migrations/002_command_control.sql`
  - 建立 `mission_sessions`
  - `discussion_messages`
  - `analysis_jobs`
  - `plan_candidates`
  - `plan_revisions`
  - `launch_batches`
  - `approval_scopes`
  - `campaign_runs`
  - `campaign_events`
- 新增 `events/services/control.py`
  - Mission / Discussion / Analysis Job / Plan / Revision / Approval Scope / Campaign 的最小 service 层
- 新增 `events/api/missions.py`、`events/api/plans.py`、`events/api/campaigns.py`
  - 作为 dashboard 新阶段的最小 API 包装层
- 更新 [dashboard/server.py](/home/asus/.openclaw/dashboard/server.py)
  - 接入 `/api/missions`
  - `/api/missions/:id`
  - `/api/missions/:id/discuss`
  - `/api/missions/:id/plans`
  - `/api/plans/:id/revisions`
  - `/api/missions/:id/approval-scopes`
  - `/api/campaigns`
  - `/api/campaigns/:id/control`
  - `/api/campaigns/:id/events`
- 新增 `dashboard-ui/`
  - `React + Vite + TypeScript` 前端工程骨架
  - 基础路由：`Mission / Execution / Command Board / Catalog`
  - Mission 页面已能对接最小 Mission API
  - Execution 和 Catalog 已对接现有 overview/tasks/tools
- 实际验证：
  - Python 编译通过
  - migration 已生效
  - `dashboard-ui` 可 `npm install` 与 `npm run build`
  - Mission / Discuss / Plan / Revision / Approval Scope / Campaign / Campaign Control 最小链路已做烟雾测试
  - smoke 数据已清理

同时修复了一处边界问题：不存在的 campaign 控制请求现在会优雅返回，不再触发 SQLite 外键错误。

## 2026-03-28 18:46

### 第二批联动：Mission 分析、方案与双栏工作台

在第一批骨架基础上，继续把 Mission 工作台推进到可联动状态：

- 更新 [events/services/control.py](/home/asus/.openclaw/events/services/control.py)
  - `get_mission()` 现在会返回：
    - `revisions`
    - `approval_scopes`
    - `campaigns`
  - 新增 `update_analysis_job()`，用于让 analyst 任务走干净的 `queued -> running -> completed/failed` 更新链
- 更新 [events/api/missions.py](/home/asus/.openclaw/events/api/missions.py)
  - 新增实际分析入口 `analyze_item()`
  - 通过 `openclaw agent --agent command --json` 触发分析
  - 自动把分析结果落为 `analysis_job`
  - 自动生成 `plan_candidate + initial revision`
- 更新 [dashboard/server.py](/home/asus/.openclaw/dashboard/server.py)
  - 新增 `/api/missions/:id/analyze`
- 更新 `dashboard-ui`
  - [MissionPage.tsx](/home/asus/.openclaw/dashboard-ui/src/pages/MissionPage.tsx)
    - 新增“直接分析 Mission”
    - 展示 analysis summary
    - 展示 plan candidates
    - 展示 revisions 与 campaigns
  - [CommandBoardPage.tsx](/home/asus/.openclaw/dashboard-ui/src/pages/CommandBoardPage.tsx)
    - 改为真正读取 Mission 数据
    - 左右分栏展示 commander / analyst 当前视图
  - [client.ts](/home/asus/.openclaw/dashboard-ui/src/shared/api/client.ts)
    - 新增 `analyzeMission()`
  - [styles.css](/home/asus/.openclaw/dashboard-ui/src/styles.css)
    - 补充按钮行、tag、chip、详情文本等样式

本轮校验：

- Python 编译通过
- `dashboard-ui` 再次 `npm run build` 通过
- 命令控制相关数据表中当前无遗留 smoke 数据

此时前端不再只是“能创建 mission”，而是已经具备：

- 讨论
- 触发分析
- 生成候选方案
- 查看 revision
- 在 Command Board 中并排查看 commander / analyst 输出

## 2026-03-28 19:05

### 第三批联动：Revision Launch 与 Workflow 详情

继续把智能指挥链往执行侧推进：

- 更新 [events/services/control.py](/home/asus/.openclaw/events/services/control.py)
  - 新增 `launch_plan_revision()`
    - 从 `plan_revision.task_tree_json` 发布任务
    - 为任务补 `workflow_id`
    - 创建 `launch_batches`
    - 回写 `mission_sessions.latest_workflow_id`
  - 新增 `list_workflows()` 与 `get_workflow_detail()`
    - 聚合 `launch_batch`
    - `tasks`
    - `results`
    - `artifacts`
    - `timeline`
- 更新 [events/api/plans.py](/home/asus/.openclaw/events/api/plans.py)
  - 新增 `launch_revision()`
- 更新 [dashboard/server.py](/home/asus/.openclaw/dashboard/server.py)
  - 新增 `/api/revisions/:id/launch`
  - 新增 `/api/workflows`
  - 新增 `/api/workflows/:id`
- 更新 `dashboard-ui`
  - [MissionPage.tsx](/home/asus/.openclaw/dashboard-ui/src/pages/MissionPage.tsx)
    - revision 卡片新增 `Launch Revision`
  - [ExecutionPage.tsx](/home/asus/.openclaw/dashboard-ui/src/pages/ExecutionPage.tsx)
    - 从原来的概览页切到：
      - workflow 列表
      - workflow 详情
      - task 列表
      - timeline
  - [client.ts](/home/asus/.openclaw/dashboard-ui/src/shared/api/client.ts)
    - 新增 `launchRevision()`
    - `listWorkflows()`
    - `getWorkflow()`

本轮验证：

- Python 编译通过
- `dashboard-ui` 构建通过
- 实际 smoke 跑通：
  - mission
  - plan
  - revision
  - launch
  - workflow detail
- smoke 产生的数据库记录、artifact 和 JSONL 兼容记录均已清理

## 2026-03-28 19:16

### 第四批联动：Approval Scope、Campaign 与最小自动刷新

继续把 Mission 与 Campaign 侧的控制能力接起来：

- 更新 `dashboard-ui`
  - [MissionPage.tsx](/home/asus/.openclaw/dashboard-ui/src/pages/MissionPage.tsx)
    - 新增 revision 选择后直接启动 campaign
    - 启动时自动创建默认 approval scope
    - 新增 `pause / resume / stop` 控制按钮
  - [CommandBoardPage.tsx](/home/asus/.openclaw/dashboard-ui/src/pages/CommandBoardPage.tsx)
    - 新增 mission 当前状态摘要
    - 新增 campaign feed 片段
  - [ExecutionPage.tsx](/home/asus/.openclaw/dashboard-ui/src/pages/ExecutionPage.tsx)
    - 新增最小轮询刷新
  - [client.ts](/home/asus/.openclaw/dashboard-ui/src/shared/api/client.ts)
    - 新增 `createApprovalScope()`
    - `createCampaign()`
    - `controlCampaign()`
    - `getCampaignEvents()`
  - [styles.css](/home/asus/.openclaw/dashboard-ui/src/styles.css)
    - 新增 campaign 控制区所需的输入样式

当前自动刷新策略为前端 5 秒轮询，先不触碰执行内核与 SSE。

本轮校验：

- Python 编译通过
- `dashboard-ui` 构建通过
- 当前数据库中无残留 mission / campaign / launch smoke 数据

## 2026-03-28 19:28

### 第五批联动：SSE 最小接入与独立 Campaign 页面

继续把控制台从纯轮询推进到更接近实时的状态：

- 更新 [dashboard/server.py](/home/asus/.openclaw/dashboard/server.py)
  - 新增 `/api/stream`
  - 支持按 `mission_id / workflow_id / campaign_id` 输出最小 SSE 流
  - 新增 `/api/campaigns`
  - 新增 `/api/campaigns/:id`
- 更新 [events/services/control.py](/home/asus/.openclaw/events/services/control.py)
  - 新增 `list_campaigns()`
  - 新增 `get_campaign_detail()`
- 更新 [events/api/campaigns.py](/home/asus/.openclaw/events/api/campaigns.py)
  - 新增 campaign 列表与详情包装
- 新增 `dashboard-ui` 文件：
  - [stream.ts](/home/asus/.openclaw/dashboard-ui/src/shared/api/stream.ts)
  - [CampaignPage.tsx](/home/asus/.openclaw/dashboard-ui/src/pages/CampaignPage.tsx)
- 更新 [router.tsx](/home/asus/.openclaw/dashboard-ui/src/app/router.tsx)
  - 新增 `Campaigns` 页面路由
- 更新几个核心页面：
  - [MissionPage.tsx](/home/asus/.openclaw/dashboard-ui/src/pages/MissionPage.tsx)
    - 选中 mission 时接入 SSE
  - [CommandBoardPage.tsx](/home/asus/.openclaw/dashboard-ui/src/pages/CommandBoardPage.tsx)
    - 选中 mission 时接入 SSE
    - 同时展示 campaign feed
  - [ExecutionPage.tsx](/home/asus/.openclaw/dashboard-ui/src/pages/ExecutionPage.tsx)
    - 选中 workflow 时接入 SSE

当前 SSE 是最小实现：

- 单连接按 2 秒检查一次
- 数据变化时推送 `mission.updated / workflow.updated / campaign.updated`
- 无变化时发 heartbeat

本轮校验：

- Python 编译通过
- `dashboard-ui` 构建通过
- 当前数据库中仍无残留 mission / campaign / launch smoke 数据

## 2026-03-28 19:40

### 第六批联动：Command Board 占位知识卡片与状态摘要

在不正式引入知识库后端的前提下，先给 `Command Board` 接上占位型 insights：

- 更新 [dashboard/server.py](/home/asus/.openclaw/dashboard/server.py)
  - 新增 `/api/command-board/:mission_id/insights`
  - 从：
    - 当前 mission revision 能力分布
    - recipe
    - recent results
    - analysis warnings
    - campaign 状态
    组合生成：
    - `knowledge_cards`
    - `intel_cards`
    - `risk_cards`
- 更新 [dashboard-ui/src/shared/api/client.ts](/home/asus/.openclaw/dashboard-ui/src/shared/api/client.ts)
  - 新增 `getCommandBoardInsights()`
- 更新 [CommandBoardPage.tsx](/home/asus/.openclaw/dashboard-ui/src/pages/CommandBoardPage.tsx)
  - 新增知识卡片、情报卡片、风险卡片
  - 新增授权状态摘要
  - 轮询从 5 秒收缩到 15 秒，详情主路径仍由 SSE 驱动
- 更新 [MissionPage.tsx](/home/asus/.openclaw/dashboard-ui/src/pages/MissionPage.tsx)
  - 增加 mission 状态、workflow 绑定、campaign 激活状态标签
  - 增加 campaign 状态和自动重规划摘要
  - 列表轮询收缩到 15 秒
- 更新 [CampaignPage.tsx](/home/asus/.openclaw/dashboard-ui/src/pages/CampaignPage.tsx)
  - 增加 scope、status、auto-replan、高风险/交互式授权摘要
  - campaign 列表轮询收缩到 15 秒
- 更新 [ExecutionPage.tsx](/home/asus/.openclaw/dashboard-ui/src/pages/ExecutionPage.tsx)
  - workflow 列表轮询收缩到 15 秒

本轮本质上是为后续正式知识/情报板块预留 UI 位置，让控制台先有“看板感”，后面再把占位数据替换成真正的知识后端。

本轮校验：

- Python 编译通过
- `dashboard-ui` 构建通过
- 当前数据库中仍无残留 mission / campaign smoke 数据

## 2026-03-28 19:49

### 第七批联动：Command Board 组件化与稳定摘要区

继续把 `Command Board` 从“堆卡片”整理成更稳定的结构：

- 更新 [dashboard/server.py](/home/asus/.openclaw/dashboard/server.py)
  - 扩展 `/api/command-board/:mission_id/insights`
  - 新增：
    - `current_plan`
    - `current_revision`
    - `current_workflow`
    - `current_campaign`
    - `failure_cards`
- 新增前端组件：
  - [InsightSection.tsx](/home/asus/.openclaw/dashboard-ui/src/components/InsightSection.tsx)
  - [SummaryGroup.tsx](/home/asus/.openclaw/dashboard-ui/src/components/SummaryGroup.tsx)
- 更新 [CommandBoardPage.tsx](/home/asus/.openclaw/dashboard-ui/src/pages/CommandBoardPage.tsx)
  - 使用组件化方式承接：
    - 当前状态
    - 授权摘要
    - 当前计划
    - 当前 revision
    - 当前 workflow
    - Knowledge / Intel / Risk / Recent Failure Points
- 这一轮的重点不是新增功能，而是把后续真正接知识/情报板块时最容易反复推翻的页面结构先稳定住

本轮校验：

- Python 编译通过
- `dashboard-ui` 构建通过
- 当前数据库中仍无残留 mission / campaign / launch smoke 数据

## 2026-03-28 19:58

### 第八批联动：复用摘要组件与情报/知识搜索接线壳

继续为后续正式情报/记忆板块落地做前置准备：

- 更新 [dashboard/server.py](/home/asus/.openclaw/dashboard/server.py)
  - 新增 `/api/intel/search`
  - 新增 `/api/knowledge/search`
  - 目前先用：
    - recent results
    - recipe catalog
    生成占位搜索结果，字段形状已对齐后续正式知识接口思路
- 新增前端通用组件：
  - [RecordCard.tsx](/home/asus/.openclaw/dashboard-ui/src/components/RecordCard.tsx)
- 更新 [MissionPage.tsx](/home/asus/.openclaw/dashboard-ui/src/pages/MissionPage.tsx)
  - 使用 `SummaryGroup`
  - 使用 `RecordCard`
- 更新 [ExecutionPage.tsx](/home/asus/.openclaw/dashboard-ui/src/pages/ExecutionPage.tsx)
  - 使用 `SummaryGroup`
  - 使用 `RecordCard`
- 更新 [CommandBoardPage.tsx](/home/asus/.openclaw/dashboard-ui/src/pages/CommandBoardPage.tsx)
  - 新增 `Lookup` 输入
  - 接上 `searchIntel()` / `searchKnowledge()`
  - 现在可以直接验证未来正式情报/知识接口在前端的呈现形状
- 更新 [client.ts](/home/asus/.openclaw/dashboard-ui/src/shared/api/client.ts)
  - 新增 `searchIntel()`
  - 新增 `searchKnowledge()`

这一轮的重点不是把真正知识库做完，而是把：

- 前端复用组件
- 搜索接口形状
- `Command Board` 中的知识/情报展示位

先稳定下来，后面正式接知识底座时就不用再返工页面和 client。

本轮校验：

- Python 编译通过
- `dashboard-ui` 构建通过
- 当前数据库中仍无残留 mission / campaign / launch smoke 数据

## 2026-03-28 20:07

### 第九批联动：`events/knowledge` 最小骨架与全局状态栏

继续往正式情报/记忆板块的落地方向推进：

- 新增：
  - [events/knowledge/__init__.py](/home/asus/.openclaw/events/knowledge/__init__.py)
  - [events/knowledge/search.py](/home/asus/.openclaw/events/knowledge/search.py)
- 将占位搜索逻辑从 [dashboard/server.py](/home/asus/.openclaw/dashboard/server.py) 抽到 `events/knowledge/search.py`
  - 当前仍是最小实现
  - 但后续可以直接在这个模块上继续接正式知识表、ingestion 和 analyst context
- 新增前端全局状态栏：
  - [StatusBar.tsx](/home/asus/.openclaw/dashboard-ui/src/components/StatusBar.tsx)
  - 在 [router.tsx](/home/asus/.openclaw/dashboard-ui/src/app/router.tsx) 顶部统一展示：
    - tasks
    - queued
    - running
    - ok
    - dead
    - results
    - online workers
- 更新 [styles.css](/home/asus/.openclaw/dashboard-ui/src/styles.css)
  - 补充全局状态栏样式

这一轮的意义是：

- 知识搜索不再只是 dashboard 内部临时函数
- 前端进入更像正式控制台的布局，而不是只有左侧导航和页面内容

本轮校验：

- Python 编译通过
- `dashboard-ui` 构建通过
- 当前数据库中仍无残留 mission / campaign / launch smoke 数据

## 2026-03-28 20:18

### 第十批联动：知识库最小表结构与独立 Intel / Knowledge 页面

开始让 `events/knowledge` 从纯搜索壳变成真正的最小知识子系统：

- 新增：
  - [events/knowledge/migrations/001_init.sql](/home/asus/.openclaw/events/knowledge/migrations/001_init.sql)
  - [events/knowledge/db.py](/home/asus/.openclaw/events/knowledge/db.py)
- 新增最小知识库表：
  - `intel_items`
  - `knowledge_entries`
- 在 [events/knowledge/db.py](/home/asus/.openclaw/events/knowledge/db.py) 中加入：
  - 独立 `knowledge.db`
  - migration 应用
  - `seed_if_empty()` 最小种子数据
- 更新 [events/knowledge/search.py](/home/asus/.openclaw/events/knowledge/search.py)
  - 搜索优先走 `knowledge.db`
  - 没有更多正式数据时仍可回落到旧占位逻辑
- 新增前端页面：
  - [IntelKnowledgePage.tsx](/home/asus/.openclaw/dashboard-ui/src/pages/IntelKnowledgePage.tsx)
- 更新 [router.tsx](/home/asus/.openclaw/dashboard-ui/src/app/router.tsx)
  - 新增 `Intel / Knowledge` 入口

这一轮之后：

- `events/knowledge/` 已经不再只是目录占位
- 已经有独立库、最小表、最小数据、最小页面
- 后面可以直接在这个子系统上继续加 ingestion、review、analyst context

本轮校验：

- Python 编译通过
- `knowledge.db` 已创建
- `intel_items` 与 `knowledge_entries` 均已有最小 seed 数据
- `dashboard-ui` 构建通过
- 主执行数据库中仍无残留 mission / campaign / launch smoke 数据

---

**最后更新**: 2026-03-28 02:55  
**维护状态**: 🟢 活跃维护  
**下一版本**: 计划添加自动化变更跟踪功能
