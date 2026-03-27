# OpenClaw 魔改版 - C方案事件驱动架构

> **⚠️ 注意：这是OpenClaw的深度魔改版本，与原版架构有重大差异**

## 📋 项目概述

**OpenClaw C方案**是对原版OpenClaw的重大架构改造，将系统从同步调用架构转型为**事件驱动的异步任务队列架构**，实现了专业化分工和可扩展协调。

### 核心变革
- 🔄 **同步→异步**：淘汰直接调用，引入事件队列
- 👥 **通用→专业**：6个专业化攻击者代理
- 🏗️ **耦合→解耦**：事件驱动，职责分离
- 🛡️ **简单→健壮**：多层次容错和监控

### 正式基线
- 正式代理总数为 8 个：`command`、`defense` 与 6 个 `offense-*` 专业攻击代理
- 正式执行路径为事件驱动队列：发布到 `tasks-YYYY-MM-DD.jsonl`，由 `events/agent_consumer.py` 按类别消费
- `openclaw agent --agent offense-*` 仅保留为调试或应急入口，不作为默认执行路径
- 旧共享 `offense` 路径与历史 `consume.py` 实现已退出正式结构，不再代表当前正式架构

### 项目状态
| 模块 | 状态 | 说明 |
|------|------|------|
| C方案事件队列 | ✅ 生产就绪 | 阶段一完成，已验证完整工作流 |
| 专业化代理体系 | ✅ 部署完成 | 8个代理（command+defense+6 offense-*） |
| 工具目录系统 | ✅ 集成完成 | 300+ Kali工具，智能发现 |
| 监控运维体系 | ✅ 配置完成 | 状态监控、存储管理、健康检查 |

## 🏗️ 架构设计

### 系统架构图
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   指挥官(command)   │    │   事件驱动队列   │    │  专业化代理执行  │
│  • 分析威胁       │───▶│  • 任务发布     │───▶│  • 工具调用     │
│  • 发现工具       │    │  • 结果收集     │    │  • 安全约束     │
│  • 制定策略       │    │  • 状态追踪     │    │  • 专业执行     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                        │                        │
         └────────────────────────┼────────────────────────┘
                                  │
                         ┌────────▼────────┐
                         │  工具目录系统   │
                         │  • 工具发现     │
                         │  • 分类管理     │
                         │  • 安全约束     │
                         │  • 使用指南     │
                         └─────────────────┘
```

### 代理体系
| 代理ID | 职责 | 状态 |
|--------|------|------|
| `command` | 指挥官（分析/决策/委托） | ✅ 已部署 |
| `defense` | 防御者（威胁分析） | ✅ 已部署 |
| `offense-wireless` | 无线渗透 | ✅ 已部署 |
| `offense-recon` | 网络侦察 | ✅ 已验证 |
| `offense-web` | Web攻击 | ✅ 已验证 |
| `offense-internal` | 内网渗透 | ✅ 已部署 |
| `offense-exploit` | 漏洞利用 | ✅ 已验证 |
| `offense-social` | 社会工程 | ✅ 已部署 |

说明：系统包含 8 个正式代理，其中 6 个为专业攻击代理。

### 技术栈
- **队列存储**: JSONL分片文件（按日期）
- **处理引擎**: Python消费者脚本 + Cron调度
- **通信协议**: 自定义事件协议（JSON格式）
- **监控系统**: 状态脚本 + 存储监控 + 健康检查
- **工具管理**: 智能工具发现 + 安全约束执行

## 🚀 快速开始

### 1. 环境检查
```bash
# 检查Gateway状态
openclaw gateway status

# 检查代理注册
openclaw agents list

# 检查队列状态
cd ~/.openclaw/events && python3 status.py
```

### 2. 发布测试任务
```bash
# 发布端口扫描任务
cd ~/.openclaw/events && python3 publish.py \
  --type scan \
  --task port-scan \
  --category recon \
  --params '{"target":"127.0.0.1","ports":"22,80,443"}'
```

### 3. 监控任务执行
```bash
# 查看队列状态
python3 status.py

# 查看消费者日志
tail -f recon.log

# 查看结果
grep "事件ID" results.jsonl
```

### 4. 工具发现和使用
```bash
# 发现工具
oc-toolfind offense recon
oc-toolfind offense web

# 查看工具目录
oc-toolcat offense

# 无线安全操作
oc-mon0  # 需要sudo
```

## 📁 项目结构

```
~/.openclaw/
├── 📄 README.md                          # 本项目说明文档
├── 📄 ARCHITECTURE.md                    # 详细架构文档
├── 📄 CONTRIBUTING.md                    # 贡献指南
├── 📄 DOCUMENTATION.md                   # 文档索引
├── 📄 ACP_CONFIG.md                      # Codex/AI最大权限配置
├── 📄 CHANGELOG.md                       # 变更记录系统
├── events/                              # 事件队列核心
│   ├── publish.py                      # 事件发布脚本
│   ├── agent_consumer.py               # 正式消费者处理脚本
│   ├── status.py                       # 队列状态监控
│   ├── archive.py                      # 归档脚本（每日2点运行）
│   ├── storage_monitor.py              # 存储监控（100MB阈值）
│   ├── EVENT_PROTOCOL.md               # 事件协议文档
│   ├── tasks-*.jsonl                   # 正式分片任务存储
│   ├── results.jsonl                   # 结果存储
│   └── archive/                        # 归档目录
├── agent-kits/                         # 工具目录系统
│   ├── common/bin/
│   │   ├── oc-toolfind                # 工具搜索
│   │   ├── oc-toolcat                 # 目录查看
│   │   ├── oc-mon0                    # 无线监控接口
│   │   └── _net_guard_lib.sh          # 网络防护库
│   ├── offense-kit/catalog/           # 攻击工具（100+工具）
│   ├── defense-kit/catalog/           # 防御工具
│   └── cmd-special/catalog/           # 特殊工具
├── agents/                             # 代理配置目录
│   ├── command/                       # 指挥官代理
│   ├── defense/                       # 防御者代理
│   └── offense-*/                     # 6个专业化攻击者代理
├── workspaces/                         # 代理工作空间
│   ├── command/                       # 指挥官工作空间
│   ├── defense/                       # 防御者工作空间
│   └── offense-*/                     # 专业化代理工作空间
├── 📄 openclaw.json                    # 主配置文件
└── 📄 .gitignore                       # Git忽略文件
```

备注：旧版共享 `offense` 路径与历史 `consume.py` 已退出正式结构；当前正式执行路径仅保留 `events/agent_consumer.py` 和独立 `workspaces/offense-*`。

## 📚 核心文档

### 主要设计文档
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - 详细架构设计和实现原理
- **[OpenClaw-C方案-事件驱动任务队列-详细实施计划.md](OpenClaw-C方案-事件驱动任务队列-详细实施计划.md)** - 原始实施计划
- **[OpenClaw-C方案-事件驱动任务队列-总结报告.md](OpenClaw-C方案-事件驱动任务队列-总结报告.md)** - 实施总结报告
- **[OpenClaw-Kali工具目录系统-介绍文档.md](OpenClaw-Kali工具目录系统-介绍文档.md)** - 工具系统文档

### 操作指南
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - 代码贡献和修改指南
- **[DOCUMENTATION.md](DOCUMENTATION.md)** - 文档导航和阅读指南

### 技术参考
- `events/EVENT_PROTOCOL.md` - 事件协议规范
- 各代理的`TOOLS.md` - 代理专用工具指南

### AI开发和变更管理
- **[ACP_CONFIG.md](ACP_CONFIG.md)** - Codex/AI代码助手最大权限配置指南
- **[CHANGELOG.md](CHANGELOG.md)** - 变更记录系统，跟踪所有修改历史
- **变更记录要求**: 所有Codex/AI修改必须更新CHANGELOG.md
- **权限配置**: 已配置最大权限访问Kali工具和硬件设备

## 🔧 运维管理

### 日常操作
```bash
# 健康检查
cd ~/.openclaw/events && ./health_dashboard.sh

# 存储监控
python3 storage_monitor.py

# 手动归档
python3 archive.py --days 3 --keep
```

### 故障排除
| 问题 | 快速修复 |
|------|----------|
| 事件停滞 | 删除`*.lock`文件，手动运行消费者 |
| API调用失败 | 检查`apis.json`，测试网络连通性 |
| 存储空间不足 | 运行归档脚本，检查`storage_monitor.py` |
| 代理未识别 | 重启Gateway，检查`openclaw.json`配置 |

### 备份恢复
```bash
# 配置备份
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.backup.$(date +%Y%m%d)

# 事件数据备份
cd ~/.openclaw/events && tar czf ../events-backup-$(date +%Y%m%d).tar.gz ./

# 恢复步骤
1. 停止Gateway: openclaw gateway stop
2. 恢复配置文件
3. 恢复事件数据
4. 启动Gateway: openclaw gateway start
5. 验证系统: python3 status.py
```

## 🎯 开发指南

### 代码修改流程
1. **理解架构**: 阅读`ARCHITECTURE.md`理解设计理念
2. **查看协议**: 参考`EVENT_PROTOCOL.md`了解事件格式
3. **测试修改**: 使用提供的测试工作流验证
4. **提交变更**: 遵循Git提交规范

### 添加新功能
```bash
# 1. 添加新事件类型
# 修改 publish.py 支持新type
# 更新 EVENT_PROTOCOL.md 文档

# 2. 添加新工具类别
# 编辑 agent-kits/*/catalog/*.json
# 测试 oc-toolfind 功能

# 3. 添加新代理
# 创建 agents/ 目录和配置
# 更新 openclaw.json 注册代理
# 创建对应workspace和TOOLS.md
```

### 测试验证
```bash
# 单元测试
python3 -m pytest tests/ -v

# 集成测试（完整工作流）
./test_full_workflow.sh

# 性能测试
./test_performance.sh
```

## 🔄 版本管理

### 当前版本
- **架构版本**: C方案 v1.0（阶段一完成）
- **工具系统**: v1.0（生产就绪）
- **代理体系**: v1.0（8个代理部署完成）

### 版本历史
| 版本 | 日期 | 主要变更 |
|------|------|----------|
| v0.1 | 2026-03-26 | 初始魔改，建立事件队列基础 |
| v0.5 | 2026-03-27 | 专业化代理拆分和注册 |
| v1.0 | 2026-03-28 | 阶段一完成，生产就绪 |

### 未来路线
- **阶段二**（3-5周）：优先级队列、Webhook通知、可视化监控
- **阶段三**（6-8周）：记忆管理系统、知识图谱
- **阶段四**（9-12周）：分布式扩展、多节点部署

## 👥 贡献者

- **项目发起**: 用户（魔改需求提出和实施）
- **架构设计**: OpenClaw Command Agent
- **实现开发**: 通过AI辅助完成
- **文档编写**: 本README及相关文档

## 📄 许可证

本项目基于OpenClaw原版项目魔改，遵循原项目的许可证条款。

## ❓ 常见问题

### Q: 与原版OpenClaw的主要区别？
**A**: 主要区别在于架构模式：原版是同步直接调用，本魔改版是事件驱动异步队列。具体差异见`ARCHITECTURE.md`。

### Q: 如何验证系统是否正常工作？
**A**: 运行完整工作流测试：`recon → web → exploit`，查看事件是否正常处理，结果是否正确返回。

### Q: 工具系统如何扩展？
**A**: 通过编辑相应的catalog JSON文件添加新工具，然后测试`oc-toolfind`功能。

### Q: 如何添加新的专业化代理？
**A**: 参考现有代理结构，创建agents目录、workspace，更新`openclaw.json`配置，然后重启Gateway。

### Q: AI/Codex如何提出改进方案？
**A**: AI可以（也应该）提出更好的计划方案，但**必须遵循协作规则**：
1. **先讨论，后实施**：所有改进方案必须先与用户详细讨论
2. **完整方案文档**：提供详细的技术方案、风险评估和实施计划
3. **明确批准**：获得用户明确批准后才能实施
4. **完整记录**：所有讨论和实施都记录在`CHANGELOG.md`
详细规则见`ACP_CONFIG.md`和`CONTRIBUTING.md`中的协作规则部分。

---

**项目维护状态**: 🟢 活跃维护  
**最后更新**: 2026-03-28  
**文档版本**: 1.0
