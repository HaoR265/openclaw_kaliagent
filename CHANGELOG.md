# OpenClaw C方案 - 变更记录

**版本**: 1.0  
**维护者**: OpenClaw Command Agent  
**格式**: 基于时间的变更记录，每次Codex/AI修改后更新

---

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

**最后更新**: 2026-03-28 02:55  
**维护状态**: 🟢 活跃维护  
**下一版本**: 计划添加自动化变更跟踪功能
