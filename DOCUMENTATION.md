# OpenClaw C方案 - 文档导航

**版本**: 1.0  
**最后更新**: 2026-03-28  
**用途**: 快速查找和访问所有项目文档

---

## 📋 文档分类索引

### 🏗️ 架构设计文档
| 文档 | 位置 | 用途 | 阅读顺序 |
|------|------|------|----------|
| **[README.md](README.md)** | 项目根目录 | 项目总览和快速开始 | 1 |
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | 项目根目录 | 完整架构设计和技术细节 | 2 |
| **[OpenClaw-多Agent编排与Kali工具系统重构设计.md](OpenClaw-多Agent编排与Kali工具系统重构设计.md)** | 项目根目录 | 后续阶段的统一架构蓝图和技术细化方案 | 3 |
| **[OpenClaw-C方案-事件驱动任务队列-详细实施计划.md](OpenClaw-C方案-事件驱动任务队列-详细实施计划.md)** | 项目根目录 | 原始设计和历史规划文档 | 4 |
| **[OpenClaw-C方案-事件驱动任务队列-总结报告.md](OpenClaw-C方案-事件驱动任务队列-总结报告.md)** | 项目根目录 | 实施成果总结和分析 | 5 |
| **[OpenClaw-Kali工具目录系统-介绍文档.md](OpenClaw-Kali工具目录系统-介绍文档.md)** | 项目根目录 | 工具系统详细说明 | 6 |

### 🔧 开发和运维文档
| 文档 | 位置 | 用途 | 目标读者 |
|------|------|------|----------|
| **[CONTRIBUTING.md](CONTRIBUTING.md)** | 项目根目录 | AI和开发者代码贡献指南 | AI助手、开发者 |
| **[events/EVENT_PROTOCOL.md](events/EVENT_PROTOCOL.md)** | `events/`目录 | 事件格式和协议规范 | 开发者、架构师 |
| **[ACP_CONFIG.md](ACP_CONFIG.md)** | 项目根目录 | Codex/AI最大权限配置指南 | AI助手、系统管理员 |
| **[CHANGELOG.md](CHANGELOG.md)** | 项目根目录 | 变更记录和追踪系统 | 所有贡献者 |
| **代理TOOLS.md文件** | `workspaces/*/TOOLS.md` | 各代理专用工具和约束指南 | 代理用户、AI |
| **配置文档** | 配置文件本身 | 配置说明和示例 | 系统管理员 |

### 📚 技术参考文档
| 文档 | 位置 | 内容 | 查询方式 |
|------|------|------|----------|
| **工具目录JSON** | `agent-kits/*/catalog/*.json` | 所有工具分类和说明 | `oc-toolfind`, `oc-toolcat` |
| **脚本帮助文档** | 脚本文件内部 | 命令行参数和使用说明 | `--help`参数 |
| **原版OpenClaw文档** | `/home/asus/.npm-global/lib/node_modules/openclaw/docs/` | 原版功能参考 | 按需查阅 |

---

## 🎯 按使用场景导航

### 场景1：新AI接手项目
**目标**: 快速理解项目架构和代码结构  
**推荐阅读顺序**:
1. **[README.md](README.md)** - 项目总览（5分钟）
2. **[ARCHITECTURE.md](ARCHITECTURE.md)** - 详细架构（15分钟）
3. **[OpenClaw-多Agent编排与Kali工具系统重构设计.md](OpenClaw-多Agent编排与Kali工具系统重构设计.md)** - 未来阶段统一蓝图（15分钟）
4. **[CONTRIBUTING.md](CONTRIBUTING.md)** - 代码修改指南（10分钟）
5. **[events/EVENT_PROTOCOL.md](events/EVENT_PROTOCOL.md)** - 事件协议（5分钟）

**快速测试**:
```bash
# 验证系统状态
openclaw gateway status
cd ~/.openclaw/events && python3 status.py

# 测试工具发现
oc-toolfind offense recon
oc-toolcat offense | head -20
```

### 场景2：添加新功能
**目标**: 了解如何扩展系统功能  
**关键文档**:
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - 第6-7节（开发扩展指南）
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - 第6节（开发扩展指南）
- **[events/EVENT_PROTOCOL.md](events/EVENT_PROTOCOL.md)** - 协议格式参考

**修改流程**:
1. 确定功能类型（事件类型/工具/代理）
2. 查找对应文档中的修改指南
3. 遵循测试和验证流程
4. 更新相关文档

### 场景3：故障排查
**目标**: 快速定位和解决问题  
**关键文档**:
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - 第5节（运维监控体系）
- **[README.md](README.md)** - 运维管理部分
- 各代理的`TOOLS.md` - 约束和限制说明

**诊断命令**:
```bash
# 检查系统健康
cd ~/.openclaw/events && ./health_dashboard.sh

# 查看错误日志
tail -f events/*.log
tail -f /var/log/syslog | grep -i openclaw

# 验证配置
openclaw config validate --json
```

### 场景4：了解工具系统
**目标**: 理解和使用300+渗透测试工具  
**关键文档**:
- **[OpenClaw-Kali工具目录系统-介绍文档.md](OpenClaw-Kali工具目录系统-介绍文档.md)** - 完整工具系统说明
- 各代理的`TOOLS.md` - 代理专用工具指南

**工具操作**:
```bash
# 探索工具
oc-toolfind offense recon        # 侦察工具
oc-toolfind offense web          # Web测试工具
oc-toolfind offense ad           # AD工具
oc-toolfind command-rare         # 特殊工具

# 查看目录
oc-toolcat offense | jq '.'      # 完整攻击工具目录
oc-toolcat defense              # 防御工具目录

# 无线安全操作
oc-mon0                         # 安全监控接口
```

---

## 📁 详细文档说明

### 1. 架构设计文档

#### [ARCHITECTURE.md](ARCHITECTURE.md)
**文件大小**: 20.5KB  
**章节数**: 7个主要部分  
**核心内容**:
- 架构概览和设计哲学
- 事件驱动系统详细实现
- 专业化代理体系说明
- 工具目录系统架构
- 运维监控体系设计
- 开发扩展指南
- 附录和参考资料

**特色**: 整合了所有技术细节，是**最全面的技术参考文档**

#### [OpenClaw-C方案-事件驱动任务队列-详细实施计划.md](OpenClaw-C方案-事件驱动任务队列-详细实施计划.md)
**文件大小**: 20.6KB  
**性质**: 原始设计文档  
**内容**: 完整的四阶段实施计划，包括：
- 阶段一：清理与优化（已完成）
- 阶段二：高级特性（3-5周计划）
- 阶段三：记忆管理系统（6-8周计划）
- 阶段四：分布式扩展（9-12周计划）

**用途**: 了解项目背景和长期规划

#### [OpenClaw-多Agent编排与Kali工具系统重构设计.md](OpenClaw-多Agent编排与Kali工具系统重构设计.md)
**性质**: 未来阶段统一蓝图  
**内容**: 将 C 方案任务内核升级和 Kali 工具目录 schema 升级整合到一个统一方案中，包括：
- 保留层与替换层
- 任务内核 v2 设计
- catalog / recipe / policy 设计
- executor 与 worker 分层
- 全阶段迁移路线
- 对现有代码的修改映射

**用途**: 后续所有架构调整和代码改造的优先参考文档

#### [OpenClaw-C方案-事件驱动任务队列-总结报告.md](OpenClaw-C方案-事件驱动任务队列-总结报告.md)
**文件大小**: 19.7KB  
**性质**: 实施总结报告  
**内容**: 阶段一完成情况的详细总结，包括：
- 已完成工作清单
- 系统当前状态
- 技术决策记录
- 运维指南
- 与标准OpenClaw的对比分析

**用途**: 了解项目现状、成果以及已完成的结构清理背景

### 2. 工具系统文档

#### [OpenClaw-Kali工具目录系统-介绍文档.md](OpenClaw-Kali工具目录系统-介绍文档.md)
**文件大小**: 19.5KB  
**章节数**: 7个主要部分  
**核心内容**:
- 工具系统架构和设计
- 300+工具详细分类说明
- 核心脚本使用指南
- 安全约束机制
- 使用场景和示例
- 维护和扩展指南

**特色**: 专门针对工具系统的完整文档，包含具体工具命令示例

### 3. 开发运维文档

#### [CONTRIBUTING.md](CONTRIBUTING.md)
**文件大小**: 17.7KB  
**目标读者**: AI代码助手、开发者  
**核心内容**:
- AI修改代码的详细指南
- 代码风格和安全约束规范
- 常见修改场景步骤说明
- 测试要求和验证流程
- 文档更新要求
- 代码审查要点

**特色**: **专门为AI优化**，提供结构化修改指南

#### [events/EVENT_PROTOCOL.md](events/EVENT_PROTOCOL.md)
**位置**: `~/.openclaw/events/EVENT_PROTOCOL.md`  
**内容**: 事件格式的权威定义，包括：
- 事件JSON结构规范
- 各字段详细说明
- 示例事件格式
- 结果格式规范
- 错误处理约定

**用途**: 开发事件相关功能时必须参考

### 4. 代理专用文档

#### 代理TOOLS.md文件
**位置**: `~/.openclaw/workspaces/*/TOOLS.md`  
**数量**: 8个文件（8个正式代理）  
**内容**: 各代理的：
- 职责和约束定义
- 专用工具指南
- 安全限制说明
- 使用示例

**重要文件**:
- `command/TOOLS.md` - 指挥官约束和工具发现指南
- `offense-wireless/TOOLS.md` - 无线安全约束
- `offense-recon/TOOLS.md` - 侦察工具指南
- `offense-web/TOOLS.md` - Web测试工具指南

---

## 🔍 文档关联关系

### 文档依赖图
```
      README.md (入口点)
          ↓
   ARCHITECTURE.md (核心架构)
     ↗     ↖     ↖
    ↗        ↖      ↖
实施计划文档   总结报告   工具系统文档
    ↓           ↓         ↓
CONTRIBUTING.md (开发指南)
    ↓
EVENT_PROTOCOL.md (协议规范)
    ↓
代理TOOLS.md (具体实施)
```

### 文档更新连锁反应
当修改以下内容时，需要更新的文档：

| 修改内容 | 必须更新的文档 |
|----------|----------------|
| 事件协议 | EVENT_PROTOCOL.md, ARCHITECTURE.md, CONTRIBUTING.md |
| 工具目录 | 工具系统文档, 相关代理TOOLS.md, ARCHITECTURE.md |
| 代理配置 | 相关代理TOOLS.md, ARCHITECTURE.md, README.md |
| 核心代码 | CONTRIBUTING.md, ARCHITECTURE.md, 测试文档 |
| 架构设计 | ARCHITECTURE.md, README.md, 所有相关文档 |

---

## 💡 文档使用技巧

### 快速搜索技巧
```bash
# 在文档中搜索关键词
grep -r "事件协议" ~/.openclaw/*.md
grep -r "无线约束" ~/.openclaw/workspaces/*/TOOLS.md

# 搜索工具相关
grep -r "nmap" ~/.openclaw/*.md
grep -r "sqlmap" ~/.openclaw/agent-kits/*/catalog/*.json

# 查看文档大小
wc -l ~/.openclaw/*.md | sort -nr
```

### 文档验证
```bash
# 检查Markdown语法
python3 -m markdown -x extra README.md > /dev/null && echo "✅ README.md语法正确"

# 检查JSON格式
python3 -m json.tool agent-kits/offense-kit/catalog/front-tools.json > /dev/null

# 检查链接有效性
grep -o '\[.*\](.*)' README.md | sed 's/.*(//;s/).*//' | while read link; do
    if [ -f "$link" ] || [[ "$link" == http* ]]; then
        echo "✅ 链接有效: $link"
    else
        echo "❌ 链接无效: $link"
    fi
done
```

### 文档维护
```bash
# 更新文档时间戳
sed -i "s/最后更新:.*/最后更新: $(date +%Y-%m-%d)/" DOCUMENTATION.md

# 生成文档索引
ls -la ~/.openclaw/*.md | awk '{print $9, "(" $5 "字节)"}'

# 检查文档完整性
for doc in README.md ARCHITECTURE.md CONTRIBUTING.md; do
    if [ -f "$doc" ]; then
        echo "✅ $doc 存在"
    else
        echo "❌ $doc 缺失"
    fi
done
```

---

## 🚀 学习路径建议

### 路径A：快速上手（30分钟）
1. **5分钟**: 阅读 [README.md](README.md) 了解项目概览
2. **10分钟**: 浏览 [ARCHITECTURE.md](ARCHITECTURE.md) 第1-2节了解架构
3. **5分钟**: 运行快速测试验证系统状态
4. **10分钟**: 查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解修改流程

### 路径B：深入理解（2小时）
1. **30分钟**: 完整阅读 [ARCHITECTURE.md](ARCHITECTURE.md)
2. **30分钟**: 阅读 [OpenClaw-Kali工具目录系统-介绍文档.md](OpenClaw-Kali工具目录系统-介绍文档.md)
3. **30分钟**: 查看实施计划和总结报告了解背景
4. **30分钟**: 实践操作和测试

### 路径C：开发扩展（持续）
1. **准备阶段**: 阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 和架构文档相关章节
2. **实施阶段**: 参考具体场景指南和示例
3. **测试阶段**: 运行完整测试套件
4. **文档阶段**: 更新所有相关文档

---

## 📊 文档统计

### 文档数量统计
| 文档类型 | 数量 | 总大小 |
|----------|------|--------|
| 架构设计文档 | 5个 | 80.0KB |
| 开发运维文档 | 4个 | ~32.7KB |
| 代理专用文档 | 9个 | ~5.0KB |
| 协议和配置文档 | 若干 | ~10.0KB |
| **总计** | **18+个** | **~127.7KB** |

### 文档质量指标
| 指标 | 状态 | 说明 |
|------|------|------|
| 完整性 | ✅ 优秀 | 覆盖所有关键方面 |
| 一致性 | ✅ 良好 | 术语和格式统一 |
| 可读性 | ✅ 优秀 | 结构清晰，示例丰富 |
| 实用性 | ✅ 优秀 | 包含具体操作指南 |
| 可维护性 | ✅ 良好 | 有明确的更新流程 |

### 文档更新频率
| 文档 | 更新频率 | 最后更新 |
|------|----------|----------|
| README.md | 中 | 2026-03-28 |
| ARCHITECTURE.md | 中 | 2026-03-28 |
| CONTRIBUTING.md | 低 | 2026-03-28 |
| 代理TOOLS.md | 低 | 2026-03-28 |
| 实施计划/总结 | 很低 | 2026-03-28 |

---

## 🔄 文档更新流程

### 常规更新
```bash
# 1. 确定需要更新的文档
# 2. 编辑文档内容
# 3. 验证文档格式
python3 -m markdown -x extra 文档名.md > /dev/null

# 4. 更新文档索引（如果需要）
sed -i "s/最后更新:.*/最后更新: $(date +%Y-%m-%d)/" 文档名.md

# 5. 更新本导航文档（如果需要）
# 6. 提交Git变更
git add 文档名.md
git commit -m "docs: 更新文档名.md"
```

### 重大架构变更时的文档更新
1. **更新架构文档** (`ARCHITECTURE.md`)
2. **更新README** 反映变更
3. **更新贡献指南** (`CONTRIBUTING.md`)
4. **更新相关代理文档** (`TOOLS.md`)
5. **更新本导航文档** (`DOCUMENTATION.md`)
6. **验证所有文档一致性**

### 文档评审要点
- ✅ 术语一致性检查
- ✅ 链接有效性检查
- ✅ 示例正确性验证
- ✅ 格式规范检查
- ✅ 与其他文档的协调性

---

## ❓ 常见文档问题

### Q: 找不到某个功能的文档？
**A**: 尝试：
1. 在本导航文档中搜索关键词
2. 使用 `grep -r "关键词" ~/.openclaw/`
3. 检查相关文档的关联部分
4. 如果确实缺失，考虑添加新文档

### Q: 文档内容冲突怎么办？
**A**: 解决优先级：
1. `ARCHITECTURE.md` 是架构权威文档
2. `EVENT_PROTOCOL.md` 是协议权威文档
3. `CONTRIBUTING.md` 是开发权威文档
4. 其他文档如有冲突，以权威文档为准

### Q: 如何添加新文档？
**A**: 步骤：
1. 确定文档类型和位置
2. 创建文档文件
3. 编写内容，遵循现有格式
4. 在本导航文档中添加索引
5. 验证和提交

### Q: 文档太技术化，有更简单的说明吗？
**A**: 阅读优先级：
1. `README.md` - 最简明的概述
2. 相关章节摘要 - 只看关键部分
3. 示例和命令 - 跳过理论直接看实践
4. 寻求具体问题的帮助

---

## 📞 文档支持

### 文档问题反馈
- **内容错误**: 直接修改并提交PR
- **缺失内容**: 添加新文档或补充现有文档
- **格式问题**: 修复格式并更新
- **理解困难**: 简化内容或添加更多示例

### 快速帮助
```bash
# 查看文档简要帮助
head -20 README.md

# 搜索具体问题
grep -i "无线" ARCHITECTURE.md

# 查看最近更新
git log --oneline --name-only --since="1 week ago" -- "*.md"
```

### 进一步学习
- **OpenClaw原版文档**: `/home/asus/.npm-global/lib/node_modules/openclaw/docs/`
- **在线文档**: https://docs.openclaw.ai
- **社区支持**: https://discord.com/invite/clawd

---

**文档状态**: 🟢 完整且最新  
**维护承诺**: 随项目发展持续更新  
**目标**: 提供全面、准确、易用的文档支持
