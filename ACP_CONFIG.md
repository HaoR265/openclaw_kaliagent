# OpenClaw ACP配置 - Codex最大权限指南

**版本**: 1.0  
**最后更新**: 2026-03-28  
**用途**: 配置和使用Codex/AI代码助手进行OpenClaw开发

---

## 📋 概述

本文档提供OpenClaw C方案魔改版中**Codex/AI代码助手的完整配置和使用指南**，确保AI工具拥有最大权限访问Kali工具和硬件设备，并建立规范的变更记录系统。

### 核心目标
1. **🔓 最大权限**: Codex可以无限制访问系统工具和硬件
2. **🛠️ Kali工具集成**: 完整访问300+渗透测试工具
3. **📱 硬件设备访问**: USB WiFi适配器等硬件测试支持
4. **📝 变更记录**: 每次修改都有完整记录和追踪
5. **🔒 安全可控**: 在最大权限下保持安全约束

---

## 🛠️ 权限配置说明

### 1. exec工具权限配置 (`openclaw.json`)
```json
"exec": {
  "pathPrepend": [
    "/home/asus/.openclaw/agent-kits/common/bin",  # 自定义工具脚本
    "/usr/bin",      # 系统二进制文件
    "/usr/sbin",     # 系统管理工具
    "/bin",          # 基本二进制文件
    "/sbin",         # 系统管理二进制文件
    "/usr/local/bin", # 本地安装工具
    "/usr/local/sbin", # 本地管理工具
    "/opt/bin",      # 可选工具目录
    "/opt/sbin"      # 可选管理工具
  ],
  "security": "full",    // 允许所有命令（最大权限）
  "ask": "off",         // 不要求批准（自动执行）
  "elevated": true,     // 允许sudo权限
  "host": "gateway",    // 在网关上执行
  "pty": true,          // 使用伪终端（交互式命令）
  "timeout": 300        // 5分钟超时
}
```

### 2. 关键权限解释
| 配置项 | 值 | 说明 | 风险等级 |
|--------|-----|------|----------|
| **security** | `"full"` | 允许执行所有命令，无限制 | 🔴 高 |
| **ask** | `"off"` | 不要求用户批准，自动执行 | 🔴 高 |
| **elevated** | `true` | 允许sudo权限，可执行特权命令 | 🔴 高 |
| **pty** | `true` | 使用伪终端，支持交互式CLI | 🟡 中 |
| **timeout** | `300` | 5分钟超时，防止无限执行 | 🟢 低 |

### 3. 路径优先级说明
```
执行命令时按以下顺序查找:
1. pathPrepend列表（从上到下）
2. 系统PATH环境变量
3. 当前目录

这样确保Kali工具优先于系统工具
```

---

## 🚀 Codex调用方法

### 1. 通过OpenClaw会话调用
```bash
# 基本调用（一次性任务）
sessions_spawn runtime="acp" agentId="codex" task="修改任务描述"

# 持久会话（适合复杂修改）
sessions_spawn runtime="acp" agentId="codex" task="任务描述" mode="session" thread=true

# 带附件的调用
sessions_spawn runtime="acp" agentId="codex" task="任务描述" \
  attachments='[{"name": "code.py", "content": "代码内容", "encoding": "utf8"}]'
```

### 2. 常用agentId选项
| agentId | 用途 | 权限级别 |
|---------|------|----------|
| `"codex"` | OpenAI Codex（如果配置） | 配置决定 |
| `"claude-code"` | Anthropic Claude Code | 配置决定 |
| `"cursor"` | Cursor AI | 配置决定 |
| 其他自定义ID | 根据acp配置 | 配置决定 |

### 3. 完整调用示例
```bash
# 修改事件队列代码
sessions_spawn runtime="acp" agentId="codex" \
  task="修改events/agent_consumer.py，添加新的任务处理逻辑" \
  mode="session" \
  thread=true \
  timeoutSeconds=1800 \
  attachments='[
    {
      "name": "current_code.py", 
      "content": "当前文件内容...",
      "encoding": "utf8"
    },
    {
      "name": "requirements.txt",
      "content": "修改需求说明...",
      "encoding": "utf8"
    }
  ]'
```

---

## 🧪 Kali工具和硬件访问

### 1. 工具访问验证
```bash
# 测试工具发现功能
oc-toolfind offense recon
oc-toolfind offense web
oc-toolfind command-rare impacket

# 测试具体工具执行
nmap --version
sqlmap --version
john --help

# 测试路径配置
which nmap
which sqlmap
which aircrack-ng
```

### 2. 硬件设备访问
#### USB WiFi适配器访问
```bash
# 安全无线监控接口创建
sudo oc-mon0  # 需要elevated权限

# 验证USB适配器检测
iw dev | grep -A5 "wlan1"
lsusb | grep -i "wireless"
```

#### 其他硬件访问示例
```bash
# 网络接口操作
ip link show
iwconfig

# USB设备列表
lsusb

# PCI设备列表
lspci

# 磁盘设备
lsblk
```

### 3. 权限测试脚本
```bash
#!/bin/bash
# test_permissions.sh

echo "=== 权限测试 ==="

# 1. 基本命令测试
echo "1. 测试基本命令权限:"
whoami
id
pwd

# 2. 系统工具测试
echo -e "\n2. 测试系统工具:"
nmap --version 2>/dev/null && echo "✅ nmap可用"
sqlmap --version 2>/dev/null && echo "✅ sqlmap可用"

# 3. 特权命令测试（需要elevated权限）
echo -e "\n3. 测试特权命令:"
if sudo -n true 2>/dev/null; then
    echo "✅ sudo权限可用"
    sudo iw dev 2>/dev/null && echo "✅ 无线设备访问权限"
else
    echo "⚠️  sudo权限不可用"
fi

# 4. 硬件访问测试
echo -e "\n4. 测试硬件访问:"
lsusb 2>/dev/null | head -5 && echo "✅ USB设备可访问"
ip link show 2>/dev/null | head -10 && echo "✅ 网络接口可访问"

echo -e "\n=== 权限测试完成 ==="
```

---

## 📝 变更记录流程

### 1. 每次修改必须执行
```bash
# 1.1 备份当前状态
cp 要修改的文件 要修改的文件.backup.$(date +%Y%m%d_%H%M%S)

# 1.2 执行修改
# 通过Codex/AI进行修改

# 1.3 更新变更记录
# 编辑CHANGELOG.md，按照模板添加记录

# 1.4 验证修改
./test_相关功能.sh

# 1.5 提交到版本控制
git add 修改的文件 CHANGELOG.md
git commit -m "类型: 变更描述"
git push
```

### 2. 变更记录模板
```markdown
## [YYYY-MM-DD HH:MM] - 变更描述

**执行者**: Codex/AI工具名
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

### 验证结果
- ✅ 功能1验证通过
- ❌ 功能2发现问题
- ⚠️  注意事项

### 相关文档更新
- [ ] ARCHITECTURE.md
- [ ] CONTRIBUTING.md  
- [ ] 其他文档
```

### 3. 自动化变更记录脚本
```bash
#!/bin/bash
# record_change.sh

CHANGE_ID="change_$(date +%Y%m%d_%H%M%S)"
echo "记录变更ID: $CHANGE_ID"

# 创建变更记录目录
mkdir -p ~/.openclaw/changes/$CHANGE_ID

# 备份相关文件
cp 修改的文件 ~/.openclaw/changes/$CHANGE_ID/

# 生成变更摘要
echo "变更摘要:" > ~/.openclaw/changes/$CHANGE_ID/summary.txt
echo "时间: $(date)" >> ~/.openclaw/changes/$CHANGE_ID/summary.txt
echo "执行者: $1" >> ~/.openclaw/changes/$CHANGE_ID/summary.txt
echo "修改文件: $2" >> ~/.openclaw/changes/$CHANGE_ID/summary.txt

# 更新主变更记录
cat >> ~/.openclaw/CHANGELOG.md << EOF

## [$(date +%Y-%m-%d\ %H:%M)] - $3

**执行者**: $1
**变更类型**: 代码修改
**变更ID**: $CHANGE_ID

### 变更详情
- **修改文件**: $2
- **变更目的**: $3

[详细记录在changes/$CHANGE_ID/]
EOF

echo "变更记录完成: ~/.openclaw/changes/$CHANGE_ID/"
```

---

## 🔒 安全注意事项

### 1. 高风险权限警告
⚠️ **当前配置为最大权限模式**，存在以下风险：
- 任何命令都可以执行，包括破坏性命令
- 不需要用户批准，自动执行
- 有sudo权限，可以修改系统配置
- 无命令过滤，可能执行恶意代码

### 2. 安全缓解措施
```bash
# 监控命令执行
tail -f ~/.openclaw/logs/exec.log

# 定期审计变更记录
grep -r "高风险" ~/.openclaw/CHANGELOG.md

# 备份关键配置
cp ~/.openclaw/openclaw.json ~/.openclaw/backups/

# 设置命令执行超时
# 已在配置中设置timeout: 300
```

### 3. 临时降低权限
```json
// 如果需要临时降低权限，修改为：
"exec": {
  "security": "allowlist",  // 只允许白名单命令
  "ask": "on-miss",         // 未知命令需要批准
  "elevated": false,        // 禁用sudo权限
  "timeout": 60            // 1分钟超时
}
```

### 4. 紧急停止措施
```bash
# 立即停止所有exec命令
pkill -f "agent_consumer"
pkill -f "openclaw"

# 恢复安全配置
cp ~/.openclaw/openclaw.json.backup ~/.openclaw/openclaw.json

# 重启服务
openclaw gateway restart
```

---

## 🧪 测试和验证

### 1. 权限配置验证
```bash
#!/bin/bash
# validate_permissions.sh

echo "=== 权限配置验证 ==="

# 检查配置文件
if python3 -m json.tool ~/.openclaw/openclaw.json > /dev/null 2>&1; then
    echo "✅ openclaw.json配置有效"
else
    echo "❌ openclaw.json配置无效"
    exit 1
fi

# 检查关键配置
if grep -q '"security": "full"' ~/.openclaw/openclaw.json; then
    echo "✅ security模式为full（最大权限）"
else
    echo "❌ security模式不是full"
fi

if grep -q '"ask": "off"' ~/.openclaw/openclaw.json; then
    echo "✅ ask模式为off（无需批准）"
else
    echo "❌ ask模式不是off"
fi

if grep -q '"elevated": true' ~/.openclaw/openclaw.json; then
    echo "✅ elevated权限启用"
else
    echo "❌ elevated权限未启用"
fi

# 测试实际执行权限
echo -e "\n测试命令执行:"
if openclaw gateway status > /dev/null 2>&1; then
    echo "✅ OpenClaw命令执行正常"
else
    echo "❌ OpenClaw命令执行失败"
fi

echo -e "\n=== 验证完成 ==="
```

### 2. 工具访问测试
```bash
#!/bin/bash
# test_tool_access.sh

echo "=== 工具访问测试 ==="

TOOLS=("nmap" "sqlmap" "john" "hashcat" "aircrack-ng" "burpsuite")

for tool in "${TOOLS[@]}"; do
    if which "$tool" > /dev/null 2>&1; then
        echo "✅ $tool 可访问"
    else
        echo "❌ $tool 不可访问"
    fi
done

# 测试自定义工具脚本
echo -e "\n测试自定义工具:"
if [ -f ~/.openclaw/agent-kits/common/bin/oc-toolfind ]; then
    echo "✅ oc-toolfind 可访问"
    ~/.openclaw/agent-kits/common/bin/oc-toolfind offense recon | head -3
else
    echo "❌ oc-toolfind 不可访问"
fi

echo -e "\n=== 工具测试完成 ==="
```

### 3. 硬件访问测试
```bash
#!/bin/bash
# test_hardware_access.sh

echo "=== 硬件访问测试 ==="

# 测试USB设备访问
if command -v lsusb > /dev/null 2>&1; then
    echo "✅ USB设备访问权限"
    lsusb | head -5
else
    echo "❌ 无法访问USB设备"
fi

# 测试网络设备访问
if command -v ip > /dev/null 2>&1; then
    echo -e "\n✅ 网络设备访问权限"
    ip link show | grep -E "wlan|eth" | head -5
else
    echo -e "\n❌ 无法访问网络设备"
fi

# 测试无线设备访问（需要sudo）
if sudo -n true 2>/dev/null; then
    echo -e "\n✅ sudo权限可用，测试无线设备:"
    sudo iw dev 2>/dev/null | head -10 && echo "✅ 无线设备访问正常"
else
    echo -e "\n⚠️  sudo权限不可用，跳过无线设备测试"
fi

echo -e "\n=== 硬件测试完成 ==="
```

---

## 🔄 配置管理和备份

### 1. 配置备份策略
```bash
#!/bin/bash
# backup_config.sh

BACKUP_DIR=~/.openclaw/backups/$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

echo "备份配置到: $BACKUP_DIR"

# 备份关键配置文件
cp ~/.openclaw/openclaw.json $BACKUP_DIR/
cp ~/.openclaw/CHANGELOG.md $BACKUP_DIR/
cp ~/.openclaw/ACP_CONFIG.md $BACKUP_DIR/

# 备份事件队列配置
cp -r ~/.openclaw/events/*.py $BACKUP_DIR/ 2>/dev/null || true

# 备份工具目录配置
cp -r ~/.openclaw/agent-kits/*/catalog/*.json $BACKUP_DIR/ 2>/dev/null || true

# 创建备份清单
find $BACKUP_DIR -type f > $BACKUP_DIR/backup_manifest.txt

echo "备份完成: $(ls -la $BACKUP_DIR | wc -l) 个文件"
```

### 2. 配置恢复流程
```bash
#!/bin/bash
# restore_config.sh

BACKUP_DIR=$1

if [ -z "$BACKUP_DIR" ] || [ ! -d "$BACKUP_DIR" ]; then
    echo "用法: restore_config.sh <备份目录>"
    echo "可用备份:"
    ls -d ~/.openclaw/backups/*/ 2>/dev/null | sort -r
    exit 1
fi

echo "从 $BACKUP_DIR 恢复配置"

# 停止服务
openclaw gateway stop

# 恢复配置文件
cp $BACKUP_DIR/openclaw.json ~/.openclaw/ 2>/dev/null || true
cp $BACKUP_DIR/CHANGELOG.md ~/.openclaw/ 2>/dev/null || true
cp $BACKUP_DIR/ACP_CONFIG.md ~/.openclaw/ 2>/dev/null || true

# 重启服务
openclaw gateway start

echo "配置恢复完成"
```

### 3. 定期备份计划
```bash
# 添加到cron，每日凌晨3点备份
0 3 * * * /home/asus/.openclaw/scripts/backup_config.sh
```

---

## 🆘 故障排除

### 常见问题及解决方案
| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| Codex无法执行命令 | exec权限配置错误 | 验证openclaw.json配置，重启Gateway |
| 工具命令找不到 | pathPrepend配置错误 | 检查pathPrepend路径，验证工具安装 |
| sudo权限被拒绝 | elevated配置无效 | 检查sudoers配置，验证用户权限 |
| 命令执行超时 | timeout设置太短 | 增加timeout值，优化命令执行 |
| 硬件访问失败 | 设备权限不足 | 检查udev规则，验证用户组权限 |

### 诊断命令
```bash
# 检查配置状态
openclaw config validate --json

# 检查服务状态
openclaw gateway status
systemctl status openclaw-gateway  # 如果使用systemd

# 检查日志
tail -f ~/.openclaw/logs/gateway.log
tail -f ~/.openclaw/events/*.log

# 测试权限
./validate_permissions.sh
./test_tool_access.sh
./test_hardware_access.sh
```

---

## 🤝 Codex/AI协作规则

### 核心原则：提出更好的方案，但要讨论
**重要规则**：Codex/AI可以提出更好的计划方案，但**必须**先与用户讨论，获得批准后才能实施。

### 1. 方案提出流程
```
Codex/AI发现改进机会 → 提出更好的方案 → 与用户讨论 → 获得批准 → 实施变更 → 记录到CHANGELOG.md
                              ↓
                      未经讨论和批准，不得直接实施
```

### 2. 可以提出的改进类型
| 改进类型 | 示例 | 讨论要求 |
|----------|------|----------|
| **架构优化** | 事件队列性能优化、代理分工调整 | 🟡 必须详细讨论 |
| **功能增强** | 新事件类型、新工具集成、新代理类型 | 🟡 必须详细讨论 |
| **安全改进** | 权限细化、约束加强、监控增强 | 🔴 必须详细讨论并测试 |
| **性能优化** | 存储优化、处理速度提升、资源管理 | 🟢 可简要讨论 |
| **用户体验** | 命令简化、文档改进、错误提示优化 | 🟢 可简要讨论 |

### 3. 讨论内容要求
当提出更好的方案时，必须包含：
1. **当前问题分析**：说明现有方案的不足
2. **改进方案描述**：详细说明更好的方案
3. **技术实现路径**：如何实施的步骤
4. **预期效果**：改进后的好处和影响
5. **风险评估**：可能的风险和应对措施
6. **测试计划**：如何验证改进效果

### 4. 讨论格式示例
```markdown
## 改进方案提议：事件队列优先级系统

### 当前问题
当前事件队列是先进先出，没有优先级区分，导致：
- 紧急任务可能被普通任务阻塞
- 高重要性任务无法优先处理

### 改进方案
添加优先级字段到事件协议，实现：
- 高/中/低三个优先级
- 消费者按优先级处理事件
- 可配置的优先级策略

### 技术实现
1. 修改EVENT_PROTOCOL.md添加priority字段
2. 更新publish.py支持优先级参数
3. 修改agent_consumer.py按优先级排序处理
4. 添加优先级监控到status.py

### 预期效果
- 紧急任务处理时间减少50%
- 系统响应性提升
- 更好的任务调度控制

### 风险评估
- 低：向后兼容，现有事件无priority字段使用默认优先级
- 测试计划：优先级测试套件

### 请求讨论
请讨论此改进方案是否可行，以及是否需要调整。
```

### 5. 实施前检查清单
- [ ] 方案已与用户详细讨论
- [ ] 用户明确批准实施
- [ ] 有完整的实施计划
- [ ] 风险评估已完成
- [ ] 回滚计划已准备
- [ ] CHANGELOG.md更新计划已准备

### 6. 违规处理
如果Codex/AI未经讨论直接实施改进：
1. **立即停止**：停止所有相关操作
2. **恢复原状**：按照回滚计划恢复
3. **记录问题**：在CHANGELOG.md中记录违规
4. **重新讨论**：重新与用户讨论方案

### 7. 成功协作示例
```bash
# Codex/AI提出方案
"我发现事件队列存储可以优化，当前JSONL文件可能在大数据量时性能下降。
我建议添加数据库后端支持，但需要先和您讨论这个方案。"

# 用户回应讨论
"好的，请详细说明你的方案，包括技术选型、实施步骤和预期效果。"

# Codex/AI提供详细方案
[提供完整的改进方案文档]

# 用户批准
"方案可行，可以实施。请先做原型测试。"

# Codex/AI实施并记录
[实施改进，更新CHANGELOG.md]
```

## 📞 支持和反馈

### 紧急支持
```bash
# 立即恢复安全配置
cp ~/.openclaw/openclaw.json.backup.20260328_025500 ~/.openclaw/openclaw.json
openclaw gateway restart

# 查看当前变更记录
tail -20 ~/.openclaw/CHANGELOG.md
```

### 获取帮助
- **架构文档**: `ARCHITECTURE.md` - 技术架构参考
- **贡献指南**: `CONTRIBUTING.md` - 开发规范
- **变更记录**: `CHANGELOG.md` - 历史变更
- **文档导航**: `DOCUMENTATION.md` - 所有文档索引

### 反馈渠道
- 代码问题：通过Git提交issue
- 配置问题：更新相关文档
- 安全问题：立即报告并修复

---

**配置状态**: 🟢 最大权限已启用  
**最后验证**: 2026-03-28  
**维护承诺**: 随使用情况更新优化