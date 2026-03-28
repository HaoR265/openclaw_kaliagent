# OpenClaw 务实推进路线图

## 原则

1. 必要优先，先补主链闭环和稳定性。
2. 不为了设计而设计，能从原始记录直接检索和归纳的，不额外造一层中间系统。
3. 不重复建模，Execution 的结果、Artifact、日志、Timeline 尽量直接复用。
4. 先把系统做成可用、可追踪、可恢复，再考虑产品化收尾。
5. 任何新结构都要回答一个问题：不做它，当前链路是不是跑不通。

---

## 已经完成的关键基础

1. `Mission -> Plan -> Revision -> Branch` 已经成最小闭环。
2. `Mission` 页已支持 task tree 编辑、参数编辑、排序、克隆和批量删除。
3. `Campaign` 页已有控制面、approval scope 摘要、事件流、blocked reasons、最近 replan 和交互摘要。
4. `Execution` 页已有 workflow、task、artifact、timeline、失败节点聚合和筛选。
5. `Command Board` 已有 commander / analyst 双工作区、knowledge/intel/risk/failure cards。
6. 前端共享展示基线已初步统一，包含状态文案、空状态、筛选条、统计条、ID/时间/回退文案。
7. `create_campaign(...)` 已增加最小 scope 校验，不满足授权范围时会进入 `under_review`。
8. execution 结果已经能最小写回 `knowledge.db`，后续可被检索。
9. 关键页面已补 localStorage 与 URL query 恢复。
10. 事件流已增加自动重连包装。

---

## 第一阶段：把主链真正做扎实

### 1. Campaign 状态流收口

1. 明确并固定 `created / under_review / running / paused / draining / stopped / killed` 的状态语义。
2. 让 `pause / resume / drain / stop / kill` 的成功与失败都回写结构化事件。
3. 把当前 `scope_validation` 事件继续收口成稳定的后端字段，而不只依赖前端拼装。
4. 给 `under_review` 增加最小人工处理闭环，而不是只有阻止继续执行。
5. 把 `auto_replan_enabled` 的触发点限制在真正必要的失败场景。
6. 避免同一 campaign 同时出现“已阻塞但还被当作 running”的状态漂移。
7. 给 campaign 控制动作补幂等保护，避免重复点击造成重复事件。
8. 给控制失败补用户可读错误，而不是只抛后端异常。
9. 在 mission、campaign、execution 三页统一展示当前 campaign 的主状态。
10. 把 `latest_workflow_id`、`active_campaign_run_id`、`plan_revision_id` 这组三角关系固定下来。

### 2. Execution 排障闭环

11. 给 workflow detail 增加 task 到 timeline 的更直接追踪入口。
12. 给 workflow detail 增加 artifact 原文或摘要查看。
13. 给失败 task 增加 result / error / last attempt 的结构化展示。
14. 让 task、artifact、timeline 三块使用同一套对象跳转口径。
15. 增加“从 task 反查 mission / revision / campaign”的稳定跳转。
16. 增加“只看失败 / 只看有 artifact / 只看 interactive”的快捷过滤。
17. 补 detail 页慢加载、空结果、接口失败时的可恢复提示。
18. 给 workflow 列表增加最近更新时间或最近事件时间，方便判断活跃度。
19. 把 artifact path、mime、size 之外真正有价值的字段补齐到 detail API。
20. 让 execution 页成为最小可用排障面，而不是只看卡片摘要。

### 3. Mission 与 Revision 主线收口

21. 给 revision 增加最小 diff/compare 能力。
22. 给 branch 增加更明确的“来自哪个 revision”的可视关系。
23. 让 `current main revision` 与 `selected revision` 的区别更加明确。
24. 让 launch 前 review 保持最小，只处理 scope、summary、task tree 三类信息。
25. 让 revision change summary 优先复用现有上下文自动生成，减少手工填空。
26. 给 mission detail 增加更稳定的 workflow / campaign 汇总。
27. 给 mission 页面增加“回到当前运行链路”的快捷跳转。
28. 补 `discussion -> analysis -> plan candidate -> revision` 的状态串联。
29. 让 mission 页能清楚显示“当前最新分析”和“当前可发布 revision”。
30. 避免 mission 页继续长成一个堆满次级卡片的大杂烩。

---

## 第二阶段：最小知识能力，不做重系统

### 4. 先把检索做实

31. 保持 `intel / knowledge / runtime result` 三类最小检索，不立刻细分更多层。
32. 让 analyst 查询真正复用这三类数据，而不是前端只查空壳。
33. 优先做一个稳定的 `knowledge_search` API，而不是先建大量子表。
34. 让 capability 成为当前最重要的过滤维度。
35. 让搜索结果能回到相关 workflow/task，而不只是显示摘要。
36. 给 runtime writeback 增加最小来源信息：`task_id / workflow_id / capability / status`。
37. 对同一个 task 重复写回时保持 upsert，不生成噪音重复记录。
38. 对失败结果保留低置信度，对成功结果保留中等置信度，先不要假装“自动验证完成”。
39. 把 AI 归纳建立在真实结果上，不额外再造“失败经验专区”。
40. 让 Command Board 引用的是可检索数据，而不是硬编码 insight。

### 5. 最小写回闭环

41. 扩展 writeback，让关键 artifact 元信息可被检索。
42. 扩展 writeback，让关键错误信息可被后续 analyst 检索。
43. 扩展 writeback，让 mission/revision 引用链能带回结果来源。
44. 仅保留必要字段，不急着做 staging/review 流程。
45. 让 AI 可以直接基于 runtime result 归纳总结，而不是再存一份“总结对象”。
46. 如果后续确实出现噪音，再考虑增加 review，不要提前上复杂机制。
47. 把 writeback 接口设计成可扩展，但当前只落最小版本。
48. 给 writeback 增加失败保护，不能影响主执行链落库。
49. 给 writeback 增加可关闭开关，避免未来问题时拖慢主链。
50. 给 knowledge 搜索增加“只看 runtime result”能力，便于排障。

---

## 第三阶段：稳定性与恢复

### 6. 实时同步与恢复

51. 给 stream reconnect 增加退避策略，避免异常时打爆后端。
52. 给 reconnect 增加轻量状态提示，至少让用户知道实时流已断开或重连中。
53. 避免定时刷新和 stream 同时触发导致的闪动或覆盖。
54. 补页面首次加载失败后的重试入口。
55. 让页面恢复状态时优先尊重 URL query，其次才是 localStorage。
56. 对失效对象做降级处理，比如选中的 workflow 已不存在时自动回落。
57. 给关键页面保留筛选条件恢复，而不是每次刷新清空。
58. 补最小加载态，避免现在某些页面“空白一下再跳满”。
59. 让跨页面跳转保留必要上下文，而不是总回到第一页。
60. 把这些恢复逻辑压在最少代码里，避免到处复制。

### 7. 数据与接口稳定化

61. 把 `events/services/control.py` 继续拆出更稳定的 workflow/campaign 聚合函数。
62. 给前端 API 返回对象补更稳定的类型定义。
63. 降低页面内直接拼装业务字段的比例。
64. 把“页面自己猜字段意义”的逻辑逐步搬回后端或共享展示层。
65. 给关键对象定义最小一致字段：`id / state / summary / updated_at / refs`。
66. 收口异常字段命名，避免 `task / operation / tool_name / result_status` 到处变。
67. 补最小 smoke tests，覆盖 mission、campaign、execution、writeback 四条主链。
68. 补 sqlite 数据清理脚本或测试数据前缀约定，避免冒烟后残留脏数据。
69. 给 runtime 写回和 scope 校验补单独的最小测试脚本。
70. 保持所有新增能力都能通过 `py_compile + build + smoke` 三层检查。

---

## 第四阶段：最后再做的产品化项

### 8. 不影响主链，但后面可以补

71. 中英文切换。
72. 统计条点击筛选。
73. 不同对象使用不同的 ID 截断长度。
74. 更细的时间格式策略。
75. 更细的按钮、placeholder、标题文案统一。
76. 更细的移动端布局处理。
77. 更细的卡片密度和视觉层级。
78. 更细的筛选器组合。
79. 更细的导出和报告视图。
80. 更细的界面动效和视觉打磨。

---

## 明确不急着做的东西

1. 单独做一个“失败经验系统”。
2. 过早引入复杂 case link 图谱。
3. 过早引入多层 staging / review / publish 大流程。
4. 过早做很重的 Defense 子系统。
5. 过早把所有 insight 都做成正式产品模块。
6. 过早把知识层拆成很多理论上好看、实际上没人用的对象。

这些都不是永远不做，而是现在不该抢主链资源。

---

## 实施顺序建议

1. 先把 Campaign 状态流和 Execution 排障闭环做扎实。
2. 再把 Mission / Revision 主线的对比、跳转和最小 review 补齐。
3. 然后把 knowledge 检索和 runtime writeback 做到真正可用。
4. 接着补实时同步、恢复、接口稳定化和 smoke tests。
5. 最后再处理语言切换、筛选增强、视觉收尾。

---

## 每次新增功能前的检查问题

1. 这件事不做，主链会不会断。
2. 这件事能不能直接复用现有 execution/runtime 数据。
3. 这件事是不是只是把 AI 已经能自己归纳的东西再存一遍。
4. 这件事会不会让代码、数据模型或 UI 变重。
5. 这件事是不是应该放到最后收尾，而不是现在。
