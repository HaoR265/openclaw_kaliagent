# OpenClaw - 情报、记忆与研究分析设计

**版本**: 0.1  
**日期**: 2026-03-28  
**状态**: 草案，作为第三个独立任务板块  
**定位**: 面向情报沉淀、经验记忆、知识库、研究分析与最新思路吸收的统一方案

---

## 1. 为什么需要第三个大板块

这部分如果继续塞进“控制台”或“多 Agent 编排”文档里，会迅速失控。

因为它关注的已经不是：

- 底层任务如何跑
- 前端如何展示
- 指挥官如何分派

而是：

- 如何沉淀经验
- 如何维护知识库
- 如何吸收最新公开思路和比赛打法
- 如何做研究、归纳、对比和复用
- 如何让 `analyst` 在未来具备更强的方案支持能力

因此这里应单独成板块。

---

## 1.1 当前已确认的默认决策

以下内容作为当前板块的默认基线：

- 知识底座：走 `C`，但按 `C1 / C2 / C3` 分阶段推进
- `C1`：结构化元数据 + 文件/制品层
- `C2`：语义召回 / 向量检索
- `C3`：图关系层，后置
- 知识来源：自动抓取进入 staging，再按可信度和流程进入正式知识层
- 高价值来源范围：内部记录 + 官方通告 + 高质量研究 + 比赛复盘 + 工具作者更新 + 技术报告
- 信任模型：`source_trust + content_confidence + validated_status`
- 知识分类：多维分类，不采用单一目录树
- 多维主轴：`capability + scene + target + evidence + confidence`
- 记忆粒度：成功经验 + 失败经验 + 分析判断 + 工具链 + 场景适配
- 研究分析使用方式：`analyst` 为主路径，知识层逐步参与自动化托管建议
- 知识层直接参与自动托管：可以参与候选路线生成，但不直接硬决定执行动作
- 知识条目格式：严格结构化 + artifact 引用 + 来源 + 时间戳
- 检索方式：关键词 + 过滤 + 语义召回 + 相似案例
- 前端展示：摘要 + 来源 + 时间 + 可信度 + 是否验证
- 失败案例：进入高优先级知识层，并优先用于风险提醒
- `analyst -> commander` 输出结构：`summary + discussion + assumptions + options + evidence_refs + warnings`
- `commander -> task kernel` 发布结构：方案确认后的任务树 + workflow + revision_id + evidence_refs
- 自动重规划：允许在授权范围内进行，并保留清晰审计记录
- `defense` 模式第一版：周期性巡检 + 风险摘要 + 后续主动防御预留

以上默认决策，后续若无明确推翻，均按已确认处理。

---

## 2. 本文档负责什么

### 2.1 负责

- 攻击经验与分析经验的沉淀结构
- 场景打法库
- 最新公开情报整理
- 经典攻击链样例与成功案例
- 失败案例与误判案例
- 研究分析流程
- `analyst` 的未来知识输入来源

### 2.2 不负责

- 任务内核
- worker / executor
- 前端控制台本身
- `commander` / `analyst` 的 UI 展示

这些分别归：

- [OpenClaw-多Agent编排与Kali工具系统重构设计.md](/home/asus/.openclaw/docs/history/OpenClaw-多Agent编排与Kali工具系统重构设计.md)
- [OpenClaw-智能指挥与作战控制系统设计.md](/home/asus/.openclaw/docs/history/OpenClaw-智能指挥与作战控制系统设计.md)

---

## 3. 总目标

目标不是做一个“大而全资料堆”。

目标是做一个：

**可被 `analyst` 检索、归纳、引用，并能反哺 `commander` 方案生成的研究与记忆系统。**

它至少应支持：

1. 记住做过什么
2. 记住为什么这样做
3. 记住什么场景下有效
4. 记住什么情况下会失败
5. 记住最新公开思路和可复用路线

---

## 4. 未来的知识输入来源

后续应允许 `analyst` 读取和整理以下内容：

1. 比赛中的攻击经验
2. 比赛中的分析经验
3. 新的公开漏洞思路
4. 新场景打法
5. 优秀攻击链路案例
6. 目标环境相关的历史经验
7. 失败案例和错误路线

这些都可以进入未来知识库，但要结构化，不要直接堆原文。

---

## 5. 记忆层建议

### 5.1 经验记忆

建议记录：

- 场景
- 目标类型
- 起始情报
- 最终路径
- 使用能力
- 使用工具链
- 为什么有效
- 哪一步最关键
- 哪些尝试无效

### 5.2 失败记忆

失败案例同样重要，建议记录：

- 失败原因
- 错误判断
- 被误导的情报
- 无效工具链
- 应避免的路径

### 5.3 研究记忆

适合记录：

- 原理解释
- 技术路线比较
- 某打法的适用前提
- 某类场景的最佳拆解方式

---

## 6. 知识库层建议

知识库建议按主题分层，而不是放成一锅粥。

至少可分为：

1. 漏洞与新思路
2. 场景打法
3. 工具链组合
4. 密码与凭据策略
5. 无线审计经验
6. Web 思路库
7. 内网路径库
8. 社工与暴露面研究
9. 防御视角知识

每条知识最好都带：

- 标题
- 来源
- 时间
- 适用范围
- 前置条件
- 风险点
- 推荐能力域
- 推荐工具链
- 是否已验证

---

## 7. `analyst` 如何使用这套系统

未来 `analyst` 不应只是搜索原始文本。

它应具备三种读取方式：

1. **检索**
   - 找相似场景
   - 找相关打法
   - 找近期公开思路

2. **归纳**
   - 总结当前目标最可能的路径
   - 汇总适用前提
   - 排除明显不适配的路线

3. **反哺**
   - 把结论交给 `commander`
   - 让 `commander` 再生成可执行方案

---

## 8. 研究分析流程建议

未来可分成四步：

1. 收集
   - 抓取外部思路
   - 记录内部经验

2. 整理
   - 结构化
   - 去重
   - 归类

3. 评估
   - 判断可行性
   - 判断适用场景
   - 判断风险

4. 投用
   - 交由 `analyst` 检索
   - 交由 `commander` 在讨论中引用

---

## 9. 与前端和指挥体系的关系

这部分后续不应直接裸露成一个复杂后台。

更合理的接入方式是：

- 由 `analyst` 读取
- 在控制台里展示“知识引用”“经验引用”“最近相关样例”
- 不要让最终用户先面对一个过重的知识系统

也就是说：

- 知识库是底层能力
- `analyst` 是主要使用者
- 控制台只展示与当前任务强相关的部分

---

## 10. 后续执行顺序建议

建议这个板块后续按以下顺序推进：

1. 经验记录格式
2. 情报条目格式
3. 知识条目分类
4. `analyst` 检索接口
5. `analyst` 归纳与引用
6. 控制台中的知识引用展示

不要一开始就做：

- 复杂知识图谱
- 过重的后台
- 过早的自动化学习

---

## 11. 三大板块的正式分工

从现在开始建议固定为：

1. 基础设施板块  
   [OpenClaw-多Agent编排与Kali工具系统重构设计.md](/home/asus/.openclaw/docs/history/OpenClaw-多Agent编排与Kali工具系统重构设计.md)

2. 智能指挥与控制板块  
   [OpenClaw-智能指挥与作战控制系统设计.md](/home/asus/.openclaw/docs/history/OpenClaw-智能指挥与作战控制系统设计.md)

3. 情报、记忆与研究分析板块  
   [OpenClaw-情报、记忆与研究分析设计.md](/home/asus/.openclaw/docs/history/OpenClaw-情报、记忆与研究分析设计.md)

这样后续再扩前端、角色、自动化托管、知识库和研究能力时，不会继续挤在一份文档里。

---

## 12. 知识底座与存储实现建议

### 12.1 分阶段实现

#### `C1` 结构化底座

目标：

- 先建立可审计、可检索、可引用的知识底座

建议形态：

- `SQLite/Postgres`：结构化元数据
- 本地文件或对象层：原始文档、摘要、附件、案例制品

#### `C2` 语义召回

目标：

- 在结构化检索之外补语义召回

建议形态：

- embedding 索引
- chunk 级向量召回
- 相似案例召回

#### `C3` 图关系层

目标：

- 处理实体关系和多跳关联

建议形态：

- 后置到真正有需求时再上
- 不在第一轮建设中引入复杂图系统

### 12.2 核心表建议

建议至少有：

#### `intel_items`

- 外部或内部情报条目

字段建议：

- `id`
- `title`
- `source_type`
- `source_ref`
- `source_trust`
- `content_confidence`
- `validated_status`
- `raw_ref`
- `normalized_ref`
- `published_at`
- `ingested_at`

#### `knowledge_entries`

- 正式知识条目

字段建议：

- `id`
- `title`
- `entry_type`
- `summary`
- `content_ref`
- `capabilities_json`
- `scenes_json`
- `targets_json`
- `evidence_json`
- `confidence_score`
- `validated_status`
- `created_at`
- `updated_at`

#### `experience_records`

- 成功/失败/分析经验

字段建议：

- `id`
- `record_type`
- `title`
- `scenario`
- `goal`
- `outcome`
- `summary`
- `workflow_ref`
- `artifact_refs_json`
- `created_at`

#### `case_links`

- 条目间关联

字段建议：

- `id`
- `from_type`
- `from_id`
- `to_type`
- `to_id`
- `link_type`
- `score`

#### `knowledge_chunks`

- 语义召回用切片

字段建议：

- `id`
- `entry_id`
- `chunk_index`
- `text`
- `embedding_ref`

### 12.3 artifact 建议

知识板块建议单独维护：

- `intel/`
- `knowledge/`
- `cases/`
- `experience/`

每个条目都引用 artifact，不直接把大段原文塞进数据库。

---

## 13. 入库流水线与信任模型

### 13.1 入库流水线

建议流程：

1. `collect`
2. `normalize`
3. `dedupe`
4. `classify`
5. `score`
6. `review_or_publish`

### 13.2 staging 层

自动抓取内容先进入 staging，不直接进入正式知识层。

建议对象：

#### `ingestion_jobs`

- 某次抓取任务

字段建议：

- `id`
- `source_type`
- `source_locator`
- `status`
- `started_at`
- `completed_at`
- `stats_json`

#### `staging_items`

- 待规范化、待审或待发布条目

字段建议：

- `id`
- `ingestion_job_id`
- `raw_ref`
- `normalized_ref`
- `dedupe_hash`
- `classifier_output_json`
- `score_output_json`
- `review_status`

### 13.3 信任模型

建议拆成 3 个维度：

1. `source_trust`
   - 来源可信度

2. `content_confidence`
   - 当前内容本身的可信度

3. `validated_status`
   - 是否被内部验证过

建议示意：

- `source_trust`: `low / medium / high`
- `content_confidence`: `0.0 - 1.0`
- `validated_status`: `unreviewed / staged / reviewed / field_validated / rejected`

### 13.4 自动发布边界

建议口径：

- staging 可以全自动入
- 正式知识层按策略发布
- 可允许高可信来源自动进入“轻量引用层”
- 不建议所有抓取内容直接进入“正式高可信知识层”

---

## 14. 检索、归纳与 analyst 接口

### 14.1 检索链路

建议按三层走：

1. 结构化过滤
2. 语义召回
3. analyst 归纳

### 14.2 analyst 查询接口建议

- `POST /api/intel/search`
- `POST /api/knowledge/search`
- `POST /api/experience/search`
- `POST /api/analyst/context-build`

#### `POST /api/knowledge/search`

输入：

```json
{
  "query": "边界 web 管理面 联动 内网",
  "capabilities": ["recon", "web", "internal"],
  "scenes": ["ctf", "enterprise-edge"],
  "limit": 10
}
```

输出：

```json
{
  "hits": [
    {
      "entryId": "ke_001",
      "title": "边界管理面到内网的常见联动路径",
      "score": 0.86,
      "sourceTrust": "high",
      "validatedStatus": "reviewed"
    }
  ]
}
```

### 14.3 analyst 上下文构建

`analyst` 不应直接把 10 条命中原封不动塞进 prompt。

建议先构建：

- `relevant_refs`
- `supporting_cases`
- `failure_warnings`
- `recommended_paths`
- `excluded_paths`

建议对象：

#### `analyst_contexts`

- `id`
- `mission_session_id`
- `query_summary`
- `relevant_refs_json`
- `supporting_cases_json`
- `warnings_json`
- `generated_at`

### 14.4 输出给 commander 的结构

建议固定为：

```json
{
  "summary": "...",
  "discussion": ["..."],
  "assumptions": ["..."],
  "options": [],
  "evidence_refs": [],
  "warnings": []
}
```

### 14.5 前端展示建议

控制台不直接展示大而全知识库。

更合理的是在 Mission / Command Board 中展示：

- 当前相关知识引用
- 相关案例
- 失败提醒
- 来源可信度
- 是否经过验证

---

## 15. 分类与条目模板建议

### 15.1 多维分类建议

建议固定 5 轴：

1. `capability`
2. `scene`
3. `target`
4. `evidence`
5. `confidence`

### 15.2 场景建议

建议至少支持：

- `ctf`
- `enterprise-edge`
- `internal-network`
- `wireless`
- `web-app`
- `ad`
- `credential`
- `defense`

### 15.3 条目模板

#### 知识条目模板

- 标题
- 一句话摘要
- 适用场景
- 前置条件
- 推荐能力域
- 推荐工具链
- 风险点
- 失败提醒
- 来源
- 时间
- 是否验证

#### 经验条目模板

- 标题
- 场景
- 起始情报
- 路线
- 结果
- 关键点
- 无效尝试
- 可复用建议

#### 失败条目模板

- 标题
- 场景
- 误判原因
- 错误路径
- 浪费点
- 以后如何避免

---

## 16. 具体实施任务清单

以下清单作为本板块的默认执行任务表。后续如果没有新变更要求，可直接按顺序持续实现。

### 16.1 第一组：知识底座 C1

1. 建立知识库目录与运行目录  
交付：
- `knowledge/runtime/`
- `knowledge/artifacts/intel/`
- `knowledge/artifacts/entries/`
- `knowledge/artifacts/experience/`

2. 建立知识库数据库 schema 第一版  
交付：
- `intel_items`
- `knowledge_entries`
- `experience_records`
- `case_links`
- `knowledge_chunks`
- `ingestion_jobs`
- `staging_items`
- `analyst_contexts`

3. 建立知识库迁移脚本  
交付：
- 初始 migration
- schema version 记录

4. 建立 artifact 引用规则  
交付：
- 原文存放规则
- 摘要存放规则
- 附件命名规则
- artifact path 约定

### 16.2 第二组：staging 与入库流水线

5. 建立采集作业接口  
交付：
- `collect -> normalize -> dedupe -> classify -> score -> review_or_publish`
- `ingestion_jobs` 状态流转

6. 建立 staging item 规范化流程  
交付：
- 原始条目
- 规范化摘要
- 去重 hash
- 分类输出
- 打分输出

7. 建立信任模型计算规则  
交付：
- `source_trust`
- `content_confidence`
- `validated_status`
- 评分计算约定

8. 建立自动发布边界  
交付：
- staging 自动入
- 轻量引用层发布规则
- 正式知识层发布规则

### 16.3 第三组：知识与经验条目

9. 落地知识条目模板  
交付：
- 知识条目 JSON 结构
- 最小字段校验
- artifact 绑定

10. 落地经验条目模板  
交付：
- 成功经验
- 分析经验
- 工具链经验

11. 落地失败条目模板  
交付：
- 失败原因
- 误判原因
- 避免建议

12. 建立 case link 规则  
交付：
- 成功案例关联
- 失败案例关联
- 知识条目与经验条目关联

### 16.4 第四组：检索与 analyst 接口

13. 实现结构化检索接口  
交付：
- `POST /api/intel/search`
- `POST /api/knowledge/search`
- `POST /api/experience/search`

14. 实现 analyst 上下文构建  
交付：
- `POST /api/analyst/context-build`
- `relevant_refs`
- `supporting_cases`
- `failure_warnings`
- `recommended_paths`

15. 实现 evidence 引用结构  
交付：
- `evidence_refs`
- 来源、时间、可信度、验证状态统一输出

16. 实现失败提醒优先级  
交付：
- 失败案例优先加入 warnings
- analyst 输出时自动带风险提醒

### 16.5 第五组：C2 语义召回

17. 建立 chunk 切分策略  
交付：
- intel chunk
- knowledge chunk
- experience chunk

18. 建立 embedding 生成流程  
交付：
- embedding job
- 向量索引更新
- 失败重试

19. 实现语义召回接口  
交付：
- query -> semantic hits
- 结构化过滤 + 语义召回混合排序

20. 实现相似案例召回  
交付：
- 相似经验
- 相似失败案例
- 相似场景打法

### 16.6 第六组：前端承接与 analyst 使用

21. 实现知识引用输出协议  
交付：
- Mission / Command Board 需要的最小知识卡片字段

22. 实现 analyst 引用链  
交付：
- analyst 搜索
- analyst 归纳
- analyst 输出给 commander

23. 实现控制台引用卡片  
交付：
- 来源
- 时间
- 可信度
- 是否验证
- 跳转原条目

24. 实现知识回写机制  
交付：
- 新的成功/失败/分析结果可回写为经验条目

### 16.7 默认执行顺序

建议默认按下面顺序推进：

1. 1-4
2. 5-8
3. 9-12
4. 13-16
5. 17-20
6. 21-24

### 16.8 达到“可独立执行”的标准

当以下条件满足时，后续可基本按文档直接持续开发：

- schema 固定
- staging 流程固定
- analyst 检索链固定
- knowledge 引用结构固定
- 前端引用卡片字段固定

---

## 17. 文件级修改映射、依赖顺序与验收标准

### 17.1 第一组：知识底座 C1

建议修改路径：

- `knowledge/runtime/`
- `knowledge/artifacts/*`
- `events/knowledge/db.py`
- `events/knowledge/models.py`
- `events/knowledge/migrations/001_init.sql`

依赖顺序：

1. 先目录
2. 再 schema
3. 再 migration
4. 再 artifact 规则

验收标准：

- 知识库数据库可初始化
- artifact 路径规范已固定
- 基础表可查询

### 17.2 第二组：staging 与入库流水线

建议修改路径：

- `events/knowledge/ingest.py`
- `events/knowledge/normalize.py`
- `events/knowledge/dedupe.py`
- `events/knowledge/classify.py`
- `events/knowledge/score.py`
- `events/api/knowledge_ingest.py`

依赖顺序：

1. 先 ingestion_jobs
2. 再 staging_items
3. 再 normalize/dedupe
4. 再 classify/score
5. 最后 review_or_publish

验收标准：

- 一条抓取内容可进入 staging
- 可完成规范化与去重
- 可打分并进入 review 状态

### 17.3 第三组：知识与经验条目

建议修改路径：

- `events/knowledge/entries.py`
- `events/knowledge/experience.py`
- `events/knowledge/case_links.py`
- `events/api/knowledge_entries.py`
- `events/api/experience.py`

依赖顺序：

1. 先知识条目
2. 再经验条目
3. 再失败条目
4. 再 case link

验收标准：

- 条目模板可落库
- artifact 可绑定
- 案例之间可建立关联

### 17.4 第四组：检索与 analyst 接口

建议修改路径：

- `events/knowledge/search.py`
- `events/knowledge/context_builder.py`
- `events/api/intel_search.py`
- `events/api/knowledge_search.py`
- `events/api/experience_search.py`
- `events/api/analyst_context.py`

依赖顺序：

1. 先结构化检索
2. 再 context build
3. 再 evidence output
4. 再 warnings 优先级

验收标准：

- analyst 可搜索三类条目
- context 可构建
- evidence_refs 与 warnings 输出稳定

### 17.5 第五组：C2 语义召回

建议修改路径：

- `events/knowledge/chunking.py`
- `events/knowledge/embeddings.py`
- `events/knowledge/vector_index.py`
- `events/api/semantic_search.py`

依赖顺序：

1. 先 chunk
2. 再 embedding job
3. 再 vector index
4. 再 semantic search
5. 最后 similar cases

验收标准：

- 条目可切 chunk
- embedding 可生成
- 语义召回可返回相似案例

### 17.6 第六组：前端承接与 analyst 使用

建议修改路径：

- `dashboard-ui/src/features/command-board/knowledge/*`
- `dashboard-ui/src/features/mission/knowledge/*`
- `events/knowledge/writeback.py`
- `events/api/knowledge_refs.py`

依赖顺序：

1. 先知识引用输出协议
2. 再 analyst 引用链
3. 再控制台知识卡片
4. 最后知识回写

验收标准：

- Mission / Command Board 可展示知识引用
- analyst 输出可带 evidence refs
- 新的经验结果可回写为条目

### 17.7 默认执行口径

若后续未出现新冲突，默认执行方式为：

- 先知识底座
- 再 staging 流程
- 再 analyst 检索链
- 再语义召回
- 最后接前端引用与回写

## 18. 核心表字段、入库流水线与检索契约

### 18.1 `intel_items`

建议字段：

- `id`
- `title`
- `summary`
- `content_hash`
- `source_type`
- `source_name`
- `source_url`
- `published_at`
- `collected_at`
- `language`
- `raw_artifact_path`
- `normalized_artifact_path`
- `trust_score`
- `confidence_score`
- `validated_status`
- `status`

说明：

- `validated_status` 建议支持 `unreviewed / partially_reviewed / validated / rejected`
- `status` 建议支持 `staged / reviewed / published / archived`

### 18.2 `ingestion_jobs`

建议字段：

- `id`
- `job_type`
- `source_config_json`
- `trigger_type`
- `status`
- `fetched_count`
- `normalized_count`
- `deduped_count`
- `published_count`
- `error_count`
- `started_at`
- `finished_at`

### 18.3 `staging_items`

建议字段：

- `id`
- `ingestion_job_id`
- `intel_item_id`
- `status`
- `dedupe_key`
- `dedupe_group`
- `classifier_output_json`
- `score_output_json`
- `review_notes`
- `reviewed_by`
- `reviewed_at`

说明：

- `status` 建议支持 `new / normalized / deduped / scored / review / published / rejected`

### 18.4 `knowledge_entries`

建议字段：

- `id`
- `entry_type`
- `title`
- `summary`
- `body_markdown_path`
- `source_item_id`
- `primary_capability`
- `scene_tags_json`
- `target_tags_json`
- `evidence_tags_json`
- `confidence_level`
- `validated_status`
- `effective_from`
- `effective_to`
- `created_at`
- `updated_at`

说明：

- `entry_type` 建议至少支持 `technique / playbook / note / pattern / warning`

### 18.5 `experience_records`

建议字段：

- `id`
- `record_type`
- `title`
- `summary`
- `outcome`
- `mission_session_id`
- `workflow_id`
- `related_capability`
- `tools_json`
- `conditions_json`
- `lessons_json`
- `artifact_refs_json`
- `created_at`

说明：

- `record_type` 建议支持 `success / failure / analysis / adaptation`

### 18.6 `case_links`

建议字段：

- `id`
- `source_kind`
- `source_id`
- `target_kind`
- `target_id`
- `link_type`
- `weight`
- `notes`
- `created_at`

建议 `link_type`：

- `similar_to`
- `depends_on`
- `invalidates`
- `supports`
- `derived_from`

### 18.7 `knowledge_chunks`

建议字段：

- `id`
- `entry_id`
- `chunk_index`
- `chunk_text`
- `token_count`
- `embedding_model`
- `embedding_status`
- `vector_ref`
- `created_at`

### 18.8 `analyst_contexts`

建议字段：

- `id`
- `analysis_job_id`
- `query_text`
- `context_summary`
- `knowledge_refs_json`
- `intel_refs_json`
- `experience_refs_json`
- `warnings_json`
- `created_at`

### 18.9 入库流水线标准阶段

默认阶段：

1. `collect`
2. `normalize`
3. `dedupe`
4. `classify`
5. `score`
6. `review`
7. `publish`
8. `chunk`
9. `embed`
10. `serve`

每个阶段都应记录：

- 输入数
- 输出数
- 错误数
- 耗时
- 当前版本号

### 18.10 检索接口建议

建议新增或固定以下接口：

- `GET /api/intel/search`
- `GET /api/knowledge/search`
- `GET /api/experience/search`
- `GET /api/knowledge/:id`
- `GET /api/experience/:id`
- `POST /api/analyst/context`
- `GET /api/analyst/context/:id`
- `POST /api/knowledge/writeback`
- `GET /api/semantic-search`

### 18.11 检索返回结构

建议统一返回：

- `items`
- `total_estimate`
- `query_echo`
- `applied_filters`
- `warnings`
- `refs`

每个条目建议至少包含：

- `id`
- `kind`
- `title`
- `summary`
- `confidence_level`
- `validated_status`
- `time_range`
- `source_refs`
- `why_relevant`

### 18.12 高价值来源分级

建议来源分层：

1. `tier_1`
   - 官方公告
   - 工具作者原始更新
   - 官方文档
2. `tier_2`
   - 高质量研究文章
   - 论文与技术报告
   - 比赛优秀复盘
3. `tier_3`
   - 社区讨论
   - 二次整理文章
   - 未核实线索

默认规则：

- `tier_1` 可自动进入 review 高优先级
- `tier_2` 自动进入 staging
- `tier_3` 默认不自动发布，只保留候选线索

## 19. 实施门槛、数据质量要求与直接实施规则

### 19.1 第一阶段门槛：知识底座 C1

达到以下条件才算完成：

- 知识库数据库可初始化
- `intel_items / knowledge_entries / experience_records / case_links` 可查询
- artifact 路径规则固定
- 至少一条样例条目可以完整落库

### 19.2 第二阶段门槛：staging 与 review 闭环

达到以下条件才算完成：

- 新来源可以进入 `ingestion_jobs`
- 抓取结果可进入 `staging_items`
- normalize / dedupe / score 流转稳定
- review 决策可改变发布状态

### 19.3 第三阶段门槛：analyst 检索闭环

达到以下条件才算完成：

- analyst 可以同时搜索 `intel / knowledge / experience`
- 返回结果包含 `why_relevant`
- `analyst_context` 可复用和缓存
- evidence refs 与 warnings 可稳定输出

### 19.4 第四阶段门槛：C2 语义召回闭环

达到以下条件才算完成：

- published 条目可切 chunk
- embedding job 可稳定运行
- semantic search 可返回相似条目
- similar cases 可以被 analyst 直接引用

### 19.5 数据质量检查清单

每完成一组必须至少检查：

- 相同来源不会重复入库
- 时间字段和时区一致
- `validated_status` 不会缺失
- 条目有最小摘要
- artifact 路径可回溯
- 删除或归档不会留下悬空引用

### 19.6 分类与标签检查清单

每完成一组必须至少检查：

- `capability / scene / target / evidence / confidence` 五轴至少四轴可用
- 标签命名无重复别名
- 中文和英文标签能稳定共存
- 失败案例不会被错误归入成功经验

### 19.7 直接实施规则

若后续开始正式实现，默认按以下规则直接推进：

- 先做 `events/knowledge/` 子模块，不把知识逻辑混进现有 `events/worker.py`
- 先做结构化检索，再做向量召回
- 默认所有 ingestion source 先进入 staging，不允许绕过 review 直写正式知识层
- 默认所有 analyst 输出都附带 `source_refs`、`confidence_level`、`validated_status`
- 默认 writeback 先写 `experience_records`，再按规则提升为 `knowledge_entries`
- 默认知识库前端只显示当前任务强相关条目，不先做全量百科页

## 20. Schema 草案、状态流转与示例条目

### 20.1 `intel_items` schema 草案

```sql
CREATE TABLE intel_items (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  summary TEXT NOT NULL DEFAULT '',
  content_hash TEXT NOT NULL,
  source_type TEXT NOT NULL,
  source_name TEXT NOT NULL,
  source_url TEXT,
  published_at TEXT,
  collected_at TEXT NOT NULL,
  language TEXT NOT NULL DEFAULT 'zh',
  raw_artifact_path TEXT,
  normalized_artifact_path TEXT,
  trust_score REAL NOT NULL DEFAULT 0,
  confidence_score REAL NOT NULL DEFAULT 0,
  validated_status TEXT NOT NULL DEFAULT 'unreviewed',
  status TEXT NOT NULL DEFAULT 'staged'
);
```

### 20.2 `knowledge_entries` schema 草案

```sql
CREATE TABLE knowledge_entries (
  id TEXT PRIMARY KEY,
  entry_type TEXT NOT NULL,
  title TEXT NOT NULL,
  summary TEXT NOT NULL,
  body_markdown_path TEXT,
  source_item_id TEXT,
  primary_capability TEXT NOT NULL,
  scene_tags_json TEXT NOT NULL DEFAULT '[]',
  target_tags_json TEXT NOT NULL DEFAULT '[]',
  evidence_tags_json TEXT NOT NULL DEFAULT '[]',
  confidence_level TEXT NOT NULL DEFAULT 'medium',
  validated_status TEXT NOT NULL DEFAULT 'unreviewed',
  effective_from TEXT,
  effective_to TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
```

### 20.3 `experience_records` schema 草案

```sql
CREATE TABLE experience_records (
  id TEXT PRIMARY KEY,
  record_type TEXT NOT NULL,
  title TEXT NOT NULL,
  summary TEXT NOT NULL,
  outcome TEXT NOT NULL,
  mission_session_id TEXT,
  workflow_id TEXT,
  related_capability TEXT,
  tools_json TEXT NOT NULL DEFAULT '[]',
  conditions_json TEXT NOT NULL DEFAULT '[]',
  lessons_json TEXT NOT NULL DEFAULT '[]',
  artifact_refs_json TEXT NOT NULL DEFAULT '[]',
  created_at TEXT NOT NULL
);
```

### 20.4 `ingestion_jobs` 状态流转

建议状态：

- `queued`
- `collecting`
- `normalizing`
- `deduping`
- `classifying`
- `scoring`
- `reviewing`
- `publishing`
- `completed`
- `failed`
- `canceled`

流转建议：

`queued -> collecting -> normalizing -> deduping -> classifying -> scoring -> reviewing -> publishing -> completed`

异常流转：

- 任意阶段可进入 `failed`
- `queued / collecting / normalizing` 可进入 `canceled`

### 20.5 `staging_items` 状态流转

建议状态：

- `new`
- `normalized`
- `deduped`
- `scored`
- `review`
- `published`
- `rejected`

说明：

- `published` 代表已进入正式知识层
- `rejected` 代表不再继续自动推进，但仍保留审计痕迹

### 20.6 示例 `intel_item` JSON

```json
{
  "id": "intel_01JZ...",
  "title": "某比赛场景中的边界入口打法复盘",
  "summary": "复盘指出目标常见暴露面为 HTTP 管理入口和弱凭据组合。",
  "source_type": "writeup",
  "source_name": "curated-source",
  "source_url": "https://example.invalid/writeup",
  "published_at": "2026-03-20T10:00:00+08:00",
  "collected_at": "2026-03-28T18:20:00+08:00",
  "trust_score": 0.82,
  "confidence_score": 0.74,
  "validated_status": "unreviewed",
  "status": "staged"
}
```

### 20.7 示例 `knowledge_entry` JSON

```json
{
  "id": "know_01JZ...",
  "entry_type": "playbook",
  "title": "Web 暴露面优先验证路线",
  "summary": "先用低风险工具建立服务画像，再进入目录、认证和凭据路径判断。",
  "primary_capability": "web",
  "scene_tags_json": [
    "ctf",
    "edge-service"
  ],
  "target_tags_json": [
    "http",
    "admin-panel"
  ],
  "evidence_tags_json": [
    "service-banner",
    "login-surface"
  ],
  "confidence_level": "high",
  "validated_status": "validated"
}
```

### 20.8 示例 `experience_record` JSON

```json
{
  "id": "exp_01JZ...",
  "record_type": "failure",
  "title": "弱口令路径误判",
  "summary": "仅凭登录框外观推断弱口令价值过高，导致浪费时间。",
  "outcome": "negative",
  "mission_session_id": "mis_01JZ...",
  "workflow_id": "wf_01JZ...",
  "related_capability": "web",
  "tools_json": [
    "httpx",
    "whatweb"
  ],
  "lessons_json": [
    "需要结合返回头和认证机制再判断",
    "不要过早切入高噪音凭据路径"
  ]
}
```

### 20.9 示例 `analyst_context` JSON

```json
{
  "id": "ctx_01JZ...",
  "analysis_job_id": "aj_01JZ...",
  "query_text": "当前这个目标更像先做 recon 还是先做 web 路线？",
  "context_summary": "历史案例显示，类似场景先建立暴露面画像成功率更高。",
  "knowledge_refs_json": [
    "know_01JZ_A",
    "know_01JZ_B"
  ],
  "intel_refs_json": [
    "intel_01JZ_A"
  ],
  "experience_refs_json": [
    "exp_01JZ_A"
  ],
  "warnings_json": [
    "当前没有可支撑凭据攻击的高置信情报"
  ]
}
```

### 20.10 检索请求示例

`GET /api/knowledge/search?q=web%20login&capability=web&validated_status=validated`

响应骨架：

```json
{
  "items": [
    {
      "id": "know_01JZ...",
      "kind": "knowledge_entry",
      "title": "Web 暴露面优先验证路线",
      "summary": "先用低风险工具建立服务画像，再进入目录、认证和凭据路径判断。",
      "confidence_level": "high",
      "validated_status": "validated",
      "time_range": {
        "effective_from": "2026-03-01T00:00:00+08:00",
        "effective_to": null
      },
      "source_refs": [
        "intel_01JZ..."
      ],
      "why_relevant": "与当前 web 登录面和暴露面优先判断直接相关"
    }
  ],
  "total_estimate": 1,
  "query_echo": "web login",
  "applied_filters": {
    "capability": "web",
    "validated_status": "validated"
  },
  "warnings": [],
  "refs": []
}
```

### 20.11 `analyst_context` 构建规则

默认构建顺序：

1. 先结构化检索 `knowledge_entries`
2. 再取 `experience_records`
3. 再补 `intel_items`
4. 最后再进 `semantic_search`

默认输出限制：

- `knowledge_refs` 最多 5 条
- `experience_refs` 最多 3 条
- `intel_refs` 最多 3 条
- `warnings` 最多 5 条

### 20.12 直接编码顺序

若后续直接开工，默认顺序为：

1. 先写 `events/knowledge/migrations/001_init.sql`
2. 再写 `events/knowledge/models.py`
3. 再写 `events/knowledge/ingest.py` 与 `normalize.py`
4. 再写 `dedupe.py / classify.py / score.py`
5. 再写 `search.py / context_builder.py`
6. 最后接 `vector_index.py` 与前端知识引用
