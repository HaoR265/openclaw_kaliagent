# OpenClaw - 专家研究平台 v1 设计

**版本**: 0.1  
**日期**: 2026-03-28  
**状态**: 草案  
**定位**: 面向后续“深度分析研究模式”的第一版正式设计，强调理论分析与受控实验闭环

---

## 1. 设计目标

专家研究平台不是要替代现有 OpenClaw 的任务内核、Campaign 控制和 worker 执行层。

它的目标是补上当前系统最薄弱的一层：

**深度研究、专家讨论、证据组织、实验设计、结论回写。**

它应当解决的问题不是：

1. 如何直接执行更多任务
2. 如何再加更多普通 worker

而是：

1. 如何提出更高质量的技术假设
2. 如何识别当前缺失的关键证据
3. 如何设计受控实验去补证据
4. 如何让结论反哺 `commander / revision / campaign`

---

## 2. 与现有 OpenClaw 的关系

未来系统推荐保持四层结构：

1. **Execution Substrate**
   - 现有 `events/` 任务内核、worker、executor、artifact、result

2. **Command & Control Plane**
   - 现有 `Mission / Campaign / Execution / Command Board`
   - `commander` 负责最终决策和任务发布

3. **Knowledge & Memory Plane**
   - 现有 knowledge runtime
   - 后续扩展 `knowledge / experience / evidence / source`

4. **Expert Research Plane**
   - 本文档负责的新增层
   - 负责研究、比较、假设、实验请求、证据收口

专家研究平台不应绕过现有控制面。

它与现有 OpenClaw 的标准接口应是：

1. 读取 mission、revision、workflow、artifact、knowledge
2. 产出结构化分析包
3. 通过 `experiment_request` 触发执行面
4. 吃回实验结果继续研究

---

## 3. 核心原则

### 3.1 理论与实践闭环

专家系统不能只会说理论。

它必须支持：

1. 提出假设
2. 指出证据缺口
3. 设计实验
4. 获取反馈
5. 修正结论

### 3.2 专家不直接绕过控制层

专家可以提出实验请求，但不应直接裸调 worker。

更合理的路径是：

`expert -> experiment_request -> commander/campaign/control plane -> worker`

### 3.3 共享知识底座，不做完全割裂的专家孤岛

每个专家可以有自己的检索视图和偏好，但不建议每个专家维护一套完全独立的知识宇宙。

更合理的是：

1. 共享 canonical knowledge base
2. 专家私有 retrieval profile
3. 专家私有 working memory

### 3.4 先少数专家，后细分

第一版不追求几十个专家。

第一版应先让少量高价值专家形成可用闭环。

---

## 4. 角色设计

### 4.1 横向角色

#### `research-lead`

职责：

1. 拆分研究问题
2. 决定调用哪些专家
3. 汇总多专家输出
4. 形成最终研究包

#### `skeptic`

职责：

1. 拆假设
2. 找反例
3. 挑证据不足
4. 防止专家组集体乐观

#### `evidence-curator`

职责：

1. 管理 source refs
2. 管理 evidence refs
3. 管理时间、可信度、验证状态
4. 把中间研究过程收口成可追踪材料

### 4.2 领域专家

建议 v1 先做这 8 类：

1. `wireless-protocol expert`
2. `web-vuln expert`
3. `identity-auth expert`
4. `crypto expert`
5. `binary-exploit expert`
6. `internal-lateral expert`
7. `reverse-forensic expert`
8. `defense-aware expert`

说明：

1. 这些专家不是执行 worker
2. 这些专家主要负责技术推演、证据判断和实验建议
3. 这些专家的调用由 `research-lead` 负责编排

---

## 5. 知识与检索架构

### 5.1 共享知识底座

知识底座建议由这些对象组成：

1. `source_document`
2. `knowledge_entry`
3. `experience_record`
4. `runtime_result_entry`
5. `artifact_ref`
6. `evidence_ref`

### 5.2 专家私有视图

每个专家不必拥有完全独立的知识库，而应拥有：

1. 专属检索权重
2. 专属过滤器
3. 专属排序逻辑
4. 专属 working memory

例如：

1. `crypto expert` 更关注协议、证明、实现差异、参数与适用条件
2. `wireless-protocol expert` 更关注 beacon、association、vendor 行为、模式切换
3. `web-vuln expert` 更关注逻辑链、状态机、鉴权边界、输入约束

### 5.3 向量和图谱策略

v1 不建议先上图谱。

建议顺序：

1. 关键词 + filter + runtime result + knowledge refs
2. chunk + embedding + vector retrieval
3. 相似案例召回
4. 图关系层后置

---

## 6. 核心对象模型

### 6.1 `research_session`

表示一次完整研究模式会话。

建议字段：

1. `id`
2. `mission_id`
3. `revision_id`
4. `workflow_id`
5. `session_goal`
6. `status`
7. `scope_summary`
8. `created_by`
9. `created_at`
10. `updated_at`

### 6.2 `research_question`

表示由 `research-lead` 拆出的子问题。

建议字段：

1. `id`
2. `research_session_id`
3. `question_text`
4. `priority`
5. `assigned_experts_json`
6. `status`
7. `created_at`

### 6.3 `hypothesis`

表示专家提出的技术假设。

建议字段：

1. `id`
2. `research_question_id`
3. `expert_role`
4. `title`
5. `summary`
6. `assumptions_json`
7. `applicability_conditions_json`
8. `confidence_before`
9. `status`
10. `created_at`

### 6.4 `finding`

表示当前已被确认或部分确认的研究发现。

建议字段：

1. `id`
2. `research_session_id`
3. `finding_type`
4. `summary`
5. `confidence_level`
6. `validated_status`
7. `evidence_refs_json`
8. `source_refs_json`
9. `created_at`

### 6.5 `experiment_request`

这是最关键的新对象。

它表示：

**专家提出的、用于验证假设的受控实验请求。**

建议字段：

1. `id`
2. `research_session_id`
3. `hypothesis_id`
4. `requested_by_role`
5. `request_summary`
6. `required_observations_json`
7. `suggested_tasks_json`
8. `expected_artifacts_json`
9. `risk_level`
10. `approval_mode`
11. `status`
12. `created_at`
13. `updated_at`

### 6.6 `experiment_result`

表示实验执行后的回流结果。

建议字段：

1. `id`
2. `experiment_request_id`
3. `workflow_id`
4. `task_ids_json`
5. `result_summary`
6. `structured_observations_json`
7. `artifact_refs_json`
8. `confidence_delta`
9. `created_at`

### 6.7 `analysis_package`

表示最终交回 `commander` 的结构化研究包。

建议字段：

1. `id`
2. `research_session_id`
3. `summary`
4. `hypotheses_json`
5. `options_json`
6. `warnings_json`
7. `evidence_refs_json`
8. `proposed_revision_json`
9. `proposed_experiments_json`
10. `created_at`

---

## 7. API 设计建议

### 7.1 Session API

1. `POST /api/research/sessions`
2. `GET /api/research/sessions/:id`
3. `GET /api/research/sessions/:id/context`

### 7.2 Question / Hypothesis API

1. `POST /api/research/sessions/:id/questions`
2. `POST /api/research/questions/:id/hypotheses`
3. `POST /api/research/hypotheses/:id/review`

### 7.3 Experiment API

1. `POST /api/research/hypotheses/:id/experiments`
2. `GET /api/research/experiments/:id`
3. `POST /api/research/experiments/:id/approve`
4. `POST /api/research/experiments/:id/launch`

### 7.4 Synthesis API

1. `POST /api/research/sessions/:id/synthesize`
2. `POST /api/research/sessions/:id/propose-revision`
3. `POST /api/research/sessions/:id/writeback`

---

## 8. 页面结构建议

建议新增一个正式页面：

`Research Studio`

### 8.1 左栏：问题树

展示：

1. session 目标
2. 当前研究问题树
3. 已分配专家
4. 当前状态

### 8.2 中栏：专家协作流

展示：

1. research lead 的拆题与收口
2. 各专家输出
3. skeptic 的反驳与修正
4. synthesis 结果

### 8.3 右栏：证据与知识

展示：

1. evidence refs
2. source refs
3. artifact refs
4. related knowledge
5. similar cases

### 8.4 底栏：实验桥

展示：

1. experiment request 列表
2. 审批状态
3. 执行结果
4. 结果对当前 hypothesis 的影响

---

## 9. 正式工作流

建议 v1 工作流如下：

1. 用户进入 `Research Mode`
2. 创建 `research_session`
3. `context_builder` 拉取 mission、revision、workflow、artifact、knowledge
4. `research-lead` 拆出 `research_question`
5. 领域专家提出 `hypothesis`
6. `skeptic` 做反驳和校验
7. `evidence-curator` 整理证据与来源
8. 专家组提交 `experiment_request`
9. `commander / control plane` 决定是否批准
10. 执行面返回 `experiment_result`
11. 专家组重新评估 hypothesis
12. `research-lead` 汇总成 `analysis_package`
13. 输出给 `commander`，决定是否转 revision 或 campaign
14. 高价值结论写回 knowledge / experience

---

## 10. 安全与边界

专家研究平台应默认遵守这些边界：

1. 不绕过 approval scope
2. 不直接替代 campaign controller
3. 不直接拥有原始工具执行权限
4. 高风险实验必须经过 control plane
5. 写回知识层时只保留高价值结构化结论，不堆全部推理过程

---

## 11. v1 实施顺序

### 第一阶段

1. 独立 `analyst`
2. `context_builder`
3. `research_session`
4. `analysis_package`

### 第二阶段

1. `hypothesis`
2. `finding`
3. `experiment_request`
4. `experiment_result`

### 第三阶段

1. shared knowledge base
2. expert retrieval profile
3. runtime result / experience 整合

### 第四阶段

1. chunk
2. embedding
3. vector retrieval
4. similar case retrieval

### 第五阶段

1. 更细分专家
2. 图关系层
3. 更复杂的专家协商和长期研究任务

---

## 12. 阶段结论

专家研究平台 v1 不应该追求“一开始就全专家、全图谱、全自动”。

v1 最重要的不是多，而是闭环：

1. 专家能提出高质量假设
2. 专家能指出证据缺口
3. 专家能发起受控实验请求
4. 系统能把实验结果回流给专家
5. 最终产出能反哺 `commander / revision / campaign`

如果这 5 件事做成，后续再继续细分专家、做更深检索、做图谱，才有意义。
