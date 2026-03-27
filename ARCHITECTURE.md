# OpenClaw C方案 - 架构设计文档

**文档版本**: 1.0  
**最后更新**: 2026-03-28  
**相关文档**: 
- [OpenClaw-C方案-事件驱动任务队列-详细实施计划.md](OpenClaw-C方案-事件驱动任务队列-详细实施计划.md)
- [OpenClaw-C方案-事件驱动任务队列-总结报告.md](OpenClaw-C方案-事件驱动任务队列-总结报告.md)
- [OpenClaw-Kali工具目录系统-介绍文档.md](OpenClaw-Kali工具目录系统-介绍文档.md)

---

## 📋 文档说明

本文档是OpenClaw C方案魔改版的**核心架构设计文档**，整合了项目实施过程中的所有关键设计决策、技术实现和架构原理。

### 文档结构
1. **架构概览** - 整体设计理念和核心变革
2. **事件驱动系统** - 队列机制、协议设计、消费者流程
3. **专业化代理体系** - 角色分工、职责约束、工作流
4. **工具目录系统** - 工具管理、安全约束、集成方式
5. **运维监控体系** - 状态监控、存储管理、故障处理
6. **开发扩展指南** - 代码结构、修改流程、测试方法
7. **附录** - 相关文档索引和参考资料

---

## 🏗️ 第一部分：架构概览

### 1.1 设计哲学

**核心问题**: 原版OpenClaw采用同步直接调用模式，存在职责混合、扩展困难、错误传播等问题。

**解决方案**: 事件驱动异步架构，实现：
- ✅ **职责分离**: 指挥官只分析/决策/委托，不执行
- ✅ **专业化分工**: 6个严格专业化攻击者代理
- ✅ **异步解耦**: 事件队列协调，代理独立消费
- ✅ **可扩展性**: 水平扩展设计，支持分布式
- ✅ **可观测性**: 完整监控和日志体系

### 1.2 架构对比

#### 原版OpenClaw（同步调用）
```
用户/界面 → 指挥官(command) → 直接调用 → 攻击者(offense) → 执行 → 返回结果
                            ↳ 同步等待
                            ↳ 可能阻塞
                            ↳ 错误直接传播
```

#### C方案魔改版（事件驱动）
```
指挥官 → 发布事件 → 任务队列 → 多个专业化代理 → 并行执行 → 结果存储
        (立即返回)    (持久化)    (独立消费)          (异步)     (后续分析)
```

### 1.3 技术选型决策

| 决策点 | 选择方案 | 理由 |
|--------|----------|------|
| 队列存储 | JSONL分片文件 | 简单、无依赖、可追溯、易于调试 |
| 通信协议 | 自定义JSON事件 | 结构化、可扩展、易于解析 |
| 调度机制 | Cron + 文件锁 | 轻量级、避免进程堆积、容错性好 |
| 工具管理 | 分类目录+智能发现 | 组织化、AI友好、安全约束 |
| 监控体系 | 脚本化状态检查 | 轻量级、可定制、易于集成 |

### 1.4 系统状态

**当前版本**: C方案 v1.0（阶段一完成）
- ✅ 事件队列基础设施部署完成
- ✅ 8个正式代理注册和配置（其中 6 个为专业化攻击代理）
- ✅ 工具目录系统集成完成
- ✅ 监控运维体系配置完成
- ✅ 完整工作流验证通过（recon→web→exploit）

**性能指标**:
- 事件处理延迟: <60秒
- API成功率: 100%
- 存储使用率: 12.13MB / 100MB阈值
- 队列积压: 0个待处理事件

---

## 🔄 第二部分：事件驱动系统

### 2.1 核心组件

#### 事件发布 (`publish.py`)
```python
# 功能：创建和发布事件到队列
# 接口：命令行参数或Python API
# 输出：事件ID（UUID格式）
# 正式写入：tasks-YYYY-MM-DD.jsonl

# 示例发布
python3 publish.py --type scan --task port-scan --category recon \
  --params '{"target":"192.168.1.0/24","ports":"top-100"}'
```

#### 事件消费 (`agent_consumer.py`)
```python
# 功能：消费指定类别的事件并执行
# 特性：--once参数防止进程堆积
# 流程：读取→加锁→处理→更新状态→写入结果
# 正式消费者：events/agent_consumer.py
# 旧版 shared offense/consume.py 属于遗留实现

# 示例消费
python3 agent_consumer.py --once --category recon
```

#### 状态监控 (`status.py`)
```python
# 功能：实时查看队列状态
# 输出：事件统计、分类分布、存储信息
# 频率：可随时运行，无副作用
```

#### 归档管理 (`archive.py`)
```python
# 功能：自动归档旧事件文件
# 调度：每日凌晨2点（cron作业）
# 策略：保留7天数据，压缩存储
```

### 2.2 事件协议

#### 事件结构
```json
{
  "id": "uuid-v4格式",
  "type": "scan|test|attack|exploit|campaign",
  "agent": "offense",
  "task": "port-scan|dir-brute|sql-injection|...",
  "params": {"key": "value"},  // 任务参数
  "status": "pending|processing|completed|failed",
  "createdAt": "ISO-8601时间戳",
  "retryCount": 0,
  "maxRetries": 3,
  "deadLetter": false,  // 是否进入死信队列
  "category": "wireless|recon|web|internal|exploit|social",
  "processedAt": "ISO-8601时间戳",
  "completedAt": "ISO-8601时间戳",
  "statusHistory": [  // 状态历史追踪
    {"status": "pending", "at": "ISO-8601"},
    {"status": "processing", "at": "ISO-8601"}
  ]
}
```

#### 结果结构
```json
{
  "eventId": "对应事件ID",
  "status": "completed|failed",
  "rawData": {
    "task": "任务类型",
    "params": {"key": "value"},
    "executionResult": {
      "success": true|false,
      "data": {},  // 原始执行结果
      "message": "执行说明",
      "executionSource": "agent-api|local"
    },
    "category": "事件类别",
    "apiUsed": true|false,
    "executionSource": "agent"
  },
  "metadata": {
    "duration": 执行时间(秒),
    "toolsUsed": ["工具列表"],
    "apiUsed": true|false,
    "executionSource": "agent",
    "agentCategory": "代理类别"
  },
  "createdAt": "ISO-8601时间戳"
}
```

### 2.3 消费者工作流程

```
1. 读取当天任务文件（tasks-YYYY-MM-DD.jsonl）
2. 查找指定类别的pending事件
3. 获取文件锁（避免并发冲突）
4. 更新事件状态为processing
5. 释放文件锁（允许其他消费者继续）
6. 调用对应API或本地执行
7. 重新获取文件锁
8. 更新事件状态为completed/failed
9. 写入结果文件（results.jsonl）
10. 如果失败且重试次数未超限，增加retryCount
11. 如果重试次数超限，标记deadLetter=true
```

### 2.4 错误处理机制

#### 多层容错设计
```python
# 1. 消费者进程级别
python3 agent_consumer.py --once  # 防止内存泄漏

# 2. 任务执行级别
max_retries = 3  # 最大重试次数
retry_delays = [30, 60, 90]  # 指数退避

# 3. API调用级别
if status_code == 401:  # API密钥无效
    stop_retry()
elif status_code == 429:  # 速率限制
    wait(retry_after)
elif 500 <= status_code < 600:  # 服务器错误
    retry_with_backoff()

# 4. 优雅降级
if api_failed:
    execute_locally()  # 本地模拟执行
```

#### 死信队列机制
```python
# 事件重试超限后处理
if event['retryCount'] >= event['maxRetries']:
    event['deadLetter'] = True
    event['status'] = 'failed'
    # 可额外记录到专门死信文件
    # 后续可手动分析或自动处理
```

### 2.5 存储策略

#### 分片存储
```
~/.openclaw/events/
├── tasks-2026-03-27.jsonl  # 按日期分片
├── tasks-2026-03-28.jsonl
├── results.jsonl           # 所有结果集中存储
└── archive/                # 归档目录
    ├── tasks-2026-03-20.jsonl.gz
    └── tasks-2026-03-21.jsonl.gz
```

#### 归档策略
```bash
# 每日凌晨2点自动运行
0 2 * * * cd ~/.openclaw/events && python3 archive.py --days 7 --keep

# 手动归档
python3 archive.py --days 3 --keep  # 保留3天，压缩归档
```

#### 存储监控
```python
# 存储监控脚本（storage_monitor.py）
# 功能：检查目录大小，超过阈值告警
# 阈值：100MB（可配置）
# 告警：控制台输出 + 日志记录
```

---

## 👥 第三部分：专业化代理体系

### 3.1 代理角色矩阵

| 代理ID | 核心职责 | 专用工具 | 安全约束 |
|--------|----------|----------|----------|
| **command** | 分析/决策/委托 | oc-toolfind, oc-toolcat | 不执行任何操作 |
| **defense** | 威胁分析/风险评估 | 防御工具目录 | 保护当前WiFi接口 |
| **offense-wireless** | 无线渗透测试 | 无线专用工具 | 仅使用USB适配器 |
| **offense-recon** | 网络侦察 | 侦察工具目录 | 通用约束 |
| **offense-web** | Web应用测试 | Web测试工具 | 通用约束 |
| **offense-internal** | 内网渗透 | AD/内网工具 | 谨慎使用高级功能 |
| **offense-exploit** | 漏洞利用 | 逆向/密码工具 | 谨慎使用 |
| **offense-social** | 社会工程 | OSINT/字典工具 | 心理操作为主 |

### 3.2 代理约束定义

#### 指挥官约束 (`command/TOOLS.md`)
```markdown
# 指挥官约束
- 只负责分析结果、制定策略、发布任务
- 不执行任何具体操作命令
- 通过事件队列委托任务给专业化代理
- 可发现工具但不直接调用
```

#### 无线代理约束 (`offense-wireless/TOOLS.md`)
```markdown
# 无线安全约束
- 永不修改当前连接的WiFi接口（wlan0）
- 始终动态检测USB WiFi适配器（wlan1）
- 监控模式需要时，从USB适配器phy创建专用监控接口
- 首选使用帮助命令：oc-mon0
- 如果USB适配器无法进入监控模式，停止并报告约束
- 永不回退到当前连接的WiFi接口
```

#### 通用攻击者约束
```markdown
# 通用约束（适用于所有offense-*代理）
- 执行前检查工具可用性
- 记录所有执行操作和结果
- 遵循最小权限原则
- 保护代理配置（特别是Clash/mihomo配置）
```

### 3.3 代理工作流

#### 标准工作流：recon → web → exploit
```
1. 指挥官发布侦察任务 → recon队列
2. recon代理执行端口扫描 → 返回开放端口
3. 指挥官分析结果，发现Web服务 → 发布Web测试任务
4. web代理执行目录扫描/SQL注入 → 返回漏洞信息
5. 指挥官分析漏洞，发布利用任务 → exploit队列
6. exploit代理执行漏洞利用 → 返回利用结果
7. 指挥官综合所有结果，制定进一步策略
```

#### 错误处理工作流
```
1. 代理执行失败 → 记录错误信息
2. 事件retryCount++ → 如果<maxRetries，重新进入队列
3. 达到最大重试次数 → 标记deadLetter=true
4. 指挥官收到失败通知 → 分析原因，决定下一步
5. 可选：手动干预或调整策略重新发布
```

### 3.4 代理配置管理

#### 主配置文件 (`openclaw.json`)
```json
{
  "agents": {
    "list": [
      {
        "id": "offense-recon",
        "workspace": "/home/asus/.openclaw/workspaces/offense-recon",
        "model": "deepseek/deepseek-chat",
        // ... 其他配置
      }
    ],
    "subagents": {
      "command": {
        "allowAgents": [
          "offense-wireless", "offense-recon", "offense-web",
          "offense-internal", "offense-exploit", "offense-social"
        ]
      }
    }
  }
}
```

#### 独立Workspace策略
```
每个代理独立workspace，避免冲突：
~/.openclaw/workspaces/
├── command/          # 指挥官独立空间
├── defense/          # 防御者独立空间
├── offense-recon/    # 侦察代理独立空间
├── offense-web/      # Web代理独立空间
└── ...              # 其他代理独立空间
```

说明：旧共享 `offense` 路径已退出正式结构；当前正式工作区仅保留独立 `workspaces/offense-*`。

---

## 🛠️ 第四部分：工具目录系统

### 4.1 系统架构

#### 目录结构
```
~/.openclaw/agent-kits/
├── common/bin/                    # 核心脚本
│   ├── oc-toolfind              # 智能工具搜索
│   ├── oc-toolcat               # 目录查看
│   ├── oc-mon0                  # 无线监控接口
│   └── _net_guard_lib.sh        # 网络防护库
├── offense-kit/catalog/         # 攻击工具（5类）
│   └── front-tools.json        # 100+工具
├── defense-kit/catalog/         # 防御工具（3类）
│   └── front-tools.json        # 防御/取证工具
└── cmd-special/catalog/         # 特殊工具（7类）
    └── rare-tools.json         # 高级/罕见工具
```

#### 工具分类体系
1. **攻击工具**（offense-kit）
   - recon（侦察）：nmap, masscan, amass, theharvester
   - web（Web测试）：sqlmap, burpsuite, ffuf, wpscan
   - ad（活动目录）：bloodhound-python, enum4linux, netexec
   - reverse（逆向工程）：radare2, gdb, binwalk, strings
   - passwords（密码破解）：john, hashcat, hydra, cewl

2. **防御工具**（defense-kit）
   - surface（攻击面发现）：nmap, httpx, whatweb, whois
   - directory（目录服务检查）：ldapsearch, smbclient, enum4linux
   - evidence（证据分析）：strings, readelf, objdump, binwalk

3. **特殊工具**（cmd-special）
   - john-extractors（50+种格式提取器）
   - impacket-rare（高级Impacket命令）
   - wireless-special（无线专用工具）
   - 其他特殊类别

### 4.2 核心脚本功能

#### oc-toolfind - 智能工具搜索
```bash
# 基本语法
oc-toolfind <角色> [查询] [--category 类别]

# 示例
oc-toolfind offense recon           # 查看侦察工具
oc-toolfind defense --category surface  # 按类别过滤
oc-toolfind all "crack"             # 全目录搜索
oc-toolfind command-rare impacket   # 搜索高级工具
```

#### oc-toolcat - 目录查看
```bash
# 查看完整目录
oc-toolcat offense      # 攻击工具目录（JSON格式）
oc-toolcat defense      # 防御工具目录
oc-toolcat command-rare # 特殊工具目录

# 配合jq过滤
oc-toolcat offense | jq '.items[] | select(.category=="web")'
```

#### oc-mon0 - 安全无线监控
```bash
# 安全特性
1. 检测当前连接WiFi: get_connected_wifi() → wlan0
2. 识别USB适配器: get_usb_wifi_iface() → wlan1
3. 仅对USB适配器操作: iw phy phy1 interface add mon0
4. 保护主接口: 不修改wlan0任何配置
5. 返回监控接口名: mon0
```

### 4.3 安全约束机制

#### 网络防护库 (`_net_guard_lib.sh`)
```bash
#!/usr/bin/env bash
# 关键安全函数

get_connected_wifi() {
  # 检测当前连接的WiFi接口
  nmcli -t -f DEVICE,TYPE,STATE dev status | \
    awk -F: '$2=="wifi" && $3 ~ /connected|已连接/ {print $1; exit}'
}

is_usb_iface() {
  # 判断接口是否为USB设备
  local iface="$1"
  local devpath
  devpath="$(readlink -f "/sys/class/net/$iface/device" 2>/dev/null || true)"
  [[ -n "$devpath" && "$devpath" == *"/usb"* ]]
}

get_usb_wifi_iface() {
  # 获取USB WiFi适配器接口
  for i in /sys/class/net/*; do
    i="$(basename "$i")"
    [[ "$i" == "lo" ]] && continue
    iw dev "$i" info >/dev/null 2>&1 || continue
    if is_usb_iface "$i"; then
      echo "$i"
      return 0
    fi
  done
  return 1
}

deny() {
  # 拒绝不安全操作
  echo "[net-guard] DENY: $*" >&2
  exit 126
}
```

### 4.4 与事件队列的集成

#### 工具发现 → 任务发布工作流
```
1. 指挥官使用 oc-toolfind 发现合适工具
   → oc-toolfind offense recon nmap
   
2. 通过事件队列发布工具执行任务
   → python3 publish.py --type scan --task port-scan --category recon

3. 专业化代理接收并执行任务
   → agent_consumer.py --once --category recon

4. 结果通过队列返回给指挥官
   → results.jsonl 中记录完整执行结果
```

#### 代理专用工具访问
```python
# 在代理执行脚本中
def execute_task(task, params):
    if task == "port-scan":
        # 从工具目录获取工具信息
        tool_info = find_tool("nmap")
        if tool_info:
            command = f"{tool_info['bin']} {construct_params(params)}"
            return execute_command(command)
```

---

## 📊 第五部分：运维监控体系

### 5.1 状态监控

#### 队列状态监控 (`status.py`)
```bash
# 运行状态检查
cd ~/.openclaw/events && python3 status.py

# 输出示例：
事件队列状态（分片存储）
==================================================
任务文件数: 3
总事件数: 27
  待处理: 0
  处理中: 0
  已完成: 25
  失败:   2
最新事件: 2026-03-27T16:12:42.387003+00:00

按类别分布:
  recon: 4, web: 4, exploit: 2, wireless: 9, ...
```

#### 存储监控 (`storage_monitor.py`)
```bash
# 存储使用检查
python3 storage_monitor.py

# 输出示例：
存储监控报告 (/home/asus/.openclaw/events)
总大小: 12.13MB / 100MB (12.1%)
子目录大小:
  archive: 0.00MB (0.0%)
✅ 存储状态正常
```

#### 健康检查脚本
```bash
#!/bin/bash
# health_dashboard.sh
echo "=== OpenClaw C方案健康检查 ==="
echo "1. Gateway状态:"
openclaw gateway status | grep -E "(running|ok)"
echo ""
echo "2. 代理注册状态:"
openclaw agents list | grep -c "offense-"
echo ""
echo "3. 事件队列状态:"
python3 status.py | head -15
echo ""
echo "4. 存储状态:"
python3 storage_monitor.py | grep -E "(总大小|告警)"
```

### 5.2 日志管理

#### 代理专用日志
```
~/.openclaw/events/
├── wireless.log    # 无线代理日志
├── recon.log      # 侦察代理日志
├── web.log        # Web代理日志
├── internal.log   # 内网代理日志
├── exploit.log    # 漏洞代理日志
├── social.log     # 社会工程代理日志
└── archive.log    # 归档作业日志（运行时生成）
```

#### 日志轮转策略
```bash
# 每日日志清理（可添加到cron）
find ~/.openclaw/events/*.log -mtime +7 -delete
```

### 5.3 故障处理

#### 常见问题及解决方案
| 问题 | 症状 | 解决方案 |
|------|------|----------|
| **事件未被处理** | 状态一直为pending | 1. 检查消费者进程<br>2. 检查cron作业<br>3. 检查文件锁<br>4. 手动运行消费者测试 |
| **API调用失败** | 消费者日志显示API错误 | 1. 检查API密钥有效性<br>2. 检查网络连接<br>3. 检查服务状态<br>4. 检查请求格式 |
| **文件锁死锁** | 消费者卡住，lock文件存在 | 1. 删除lock文件<br>2. 重启消费者进程<br>3. 检查文件权限 |
| **存储空间不足** | 写入失败，磁盘已满 | 1. 运行归档脚本<br>2. 清理旧日志文件<br>3. 检查磁盘使用率 |
| **代理未识别** | `agents list`不显示新代理 | 1. 检查配置<br>2. 重启Gateway<br>3. 检查代理目录权限 |

#### 紧急恢复流程
```bash
# 1. 停止服务
openclaw gateway stop

# 2. 备份当前状态
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.backup.$(date +%Y%m%d)
cd ~/.openclaw/events && tar czf ../events-backup-$(date +%Y%m%d).tar.gz ./

# 3. 清理问题
rm -f ~/.openclaw/events/*.lock
rm -f ~/.openclaw/events/tasks-*.jsonl  # 注意：这会删除未处理事件

# 4. 恢复服务
openclaw gateway start
sleep 3
openclaw gateway status

# 5. 验证恢复
cd ~/.openclaw/events && python3 status.py
```

### 5.4 性能监控指标

#### 关键性能指标
| 指标 | 目标值 | 监控方法 |
|------|--------|----------|
| 事件处理延迟 | <60秒 | 计算createdAt到completedAt时间差 |
| API成功率 | >95% | 统计API调用成功/失败比例 |
| 队列积压 | 0（理想） | status.py中的待处理事件数 |
| 存储使用率 | <80% | storage_monitor.py监控 |
| 消费者进程数 | 0-6个 | `pgrep -f agent_consumer`计数 |
| 内存占用 | <200MB | `ps aux | grep agent_consumer` |

#### 监控脚本示例
```bash
#!/bin/bash
# monitor_metrics.sh

# 事件处理延迟
LATENCY=$(python3 -c "
import json, datetime
with open('results.jsonl', 'r') as f:
    lines = f.readlines()[-10:]  # 最近10个事件
    total = 0
    count = 0
    for line in lines:
        if line.strip():
            data = json.loads(line)
            created = datetime.datetime.fromisoformat(data['rawData'].get('createdAt', '').replace('Z', '+00:00'))
            completed = datetime.datetime.fromisoformat(data.get('createdAt', '').replace('Z', '+00:00'))
            total += (completed - created).total_seconds()
            count += 1
    print(f'{total/count:.1f}' if count > 0 else 'N/A')
")

# API成功率
API_SUCCESS=$(grep -c "API 调用成功" *.log 2>/dev/null | awk -F: '{sum+=$2} END{print sum}')
API_TOTAL=$(grep -c "调用.*API" *.log 2>/dev/null | awk -F: '{sum+=$2} END{print sum}')
API_RATE=$(python3 -c "print(f'{($API_SUCCESS/$API_TOTAL*100):.1f}%' if $API_TOTAL > 0 else 'N/A')")

echo "性能指标:"
echo "- 平均处理延迟: ${LATENCY:-N/A}秒"
echo "- API成功率: ${API_RATE:-N/A}"
echo "- 存储使用: $(python3 storage_monitor.py | grep '总大小' | cut -d: -f2)"
```

---

## 🔧 第六部分：开发扩展指南

### 6.1 代码结构

#### 核心脚本位置
```
~/.openclaw/events/              # 事件队列核心代码
├── publish.py                   # 事件发布（入口点）
├── agent_consumer.py           # 消费者逻辑（核心）
├── status.py                   # 状态监控
├── archive.py                  # 归档管理
├── storage_monitor.py          # 存储监控
├── summarize.py                # 结果汇总（辅助）
└── EVENT_PROTOCOL.md          # 协议文档

~/.openclaw/agent-kits/common/bin/  # 工具系统代码
├── oc-toolfind                # 工具搜索逻辑
├── oc-toolcat                 # 目录查看
├── oc-mon0                    # 无线监控
└── _net_guard_lib.sh          # 安全库
```

#### 配置管理
```
~/.openclaw/
├── openclaw.json              # 主配置文件
├── agents/                    # 代理配置目录
│   ├── command/              # 指挥官配置
│   ├── defense/              # 防御者配置
│   └── offense-*/            # 攻击者配置
└── workspaces/               # 代理工作空间
    └── .../*/TOOLS.md        # 代理专用工具指南
```

### 6.2 修改流程

#### 添加新事件类型
```python
# 1. 修改 publish.py 支持新type
def publish_event(event_type, task, category, params):
    # 添加对新type的验证
    if event_type not in ['scan', 'test', 'attack', 'exploit', 'campaign', 'new_type']:
        raise ValueError(f"不支持的事件类型: {event_type}")

# 2. 更新 EVENT_PROTOCOL.md 文档
# 添加新type的说明和示例

# 3. 修改 agent_consumer.py 处理逻辑
def process_event(event):
    if event['task'] == 'new_task':
        return execute_new_task(event['params'])

# 4. 测试新功能
python3 publish.py --type new_type --task new_task --category recon
python3 agent_consumer.py --once --category recon
```

#### 添加新工具类别
```bash
# 1. 编辑 catalog JSON 文件
# offense-kit/catalog/front-tools.json
# 或 defense-kit/catalog/front-tools.json
# 或 cmd-special/catalog/rare-tools.json

# 2. 添加新工具条目
{
  "name": "新工具名称",
  "category": "新类别或现有类别",
  "bin": "可执行文件名",
  "summary": "工具简要说明",
  "members": ["相关子工具"]  # 可选
}

# 3. 验证JSON格式
python3 -m json.tool front-tools.json > /dev/null

# 4. 测试工具发现
./oc-toolfind offense "新工具名称"
./oc-toolfind offense --category "新类别"
```

#### 添加新专业化代理
```bash
# 1. 创建代理目录结构
mkdir -p ~/.openclaw/agents/offense-new
mkdir -p ~/.openclaw/workspaces/offense-new

# 2. 创建代理配置文件
# 参考现有代理配置，创建必要的文件

# 3. 更新 openclaw.json
# 在 agents.list 中添加新代理配置
# 在 command.subagents.allowAgents 中添加新代理

# 4. 创建代理专用TOOLS.md
# 定义代理职责、约束、工具指南

# 5. 重启Gateway验证
openclaw gateway restart
openclaw agents list  # 确认新代理出现
```

### 6.3 测试策略

#### 单元测试
```bash
# 测试事件发布
python3 -c "
import sys
sys.path.append('.')
from publish import publish_event
result = publish_event('scan', 'port-scan', 'recon', {'target':'127.0.0.1'})
print(f'发布成功: {result}')
"

# 测试工具发现
./oc-toolfind offense recon | grep -q nmap && echo "工具发现正常"

# 测试配置验证
openclaw config validate --json | grep -q '"valid":true' && echo "配置有效"
```

#### 集成测试
```bash
#!/bin/bash
# test_full_workflow.sh
echo "=== 完整工作流测试 ==="

# 1. 发布测试事件
EVENT_ID=$(python3 publish.py --type test --task ping --category recon \
  --params '{"message":"集成测试"}' | grep "事件 ID:" | cut -d: -f2 | tr -d ' ')

echo "发布事件: $EVENT_ID"

# 2. 手动运行消费者
python3 agent_consumer.py --once --category recon

# 3. 检查结果
if grep -q "$EVENT_ID" results.jsonl; then
    echo "✅ 事件处理成功"
    grep "$EVENT_ID" results.jsonl | tail -1 | python3 -m json.tool
else
    echo "❌ 事件处理失败"
    exit 1
fi
```

#### 性能测试
```bash
#!/bin/bash
# test_performance.sh
echo "=== 性能测试 ==="

# 发布多个事件
for i in {1..10}; do
    python3 publish.py --type test --task ping --category recon \
      --params "{\"message\":\"性能测试 $i\"}" > /dev/null
done

# 测量处理时间
START_TIME=$(date +%s)
python3 agent_consumer.py --once --category recon
END_TIME=$(date +%s)

DURATION=$((END_TIME - START_TIME))
echo "处理10个事件耗时: ${DURATION}秒"
echo "平均每个事件: $(echo "scale=2; $DURATION/10" | bc)秒"
```

### 6.4 代码质量规范

#### 代码风格
```python
# Python代码遵循PEP 8
# 使用4空格缩进，最大行宽79字符
# 函数和类有docstring说明

def process_event(event):
    """
    处理单个事件。
    
    参数:
        event: 事件字典，包含id、type、task等字段
        
    返回:
        dict: 处理结果，包含success、data等字段
        
    异常:
        ValueError: 事件格式错误时抛出
    """
    # 实现逻辑
    pass
```

#### 错误处理
```python
# 使用明确的异常类型
try:
    result = api_call(event)
except requests.exceptions.Timeout as e:
    logger.error(f"API调用超时: {e}")
    return {"success": False, "error": "timeout"}
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 401:
        logger.error("API密钥无效")
        return {"success": False, "error": "auth_failed"}
    else:
        logger.error(f"HTTP错误: {e}")
        return {"success": False, "error": "http_error"}
except Exception as e:
    logger.exception(f"未知错误: {e}")
    return {"success": False, "error": "unknown"}
```

#### 日志记录
```python
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('recon.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 使用不同级别记录
logger.debug("详细调试信息")
logger.info("正常操作信息")
logger.warning("警告信息")
logger.error("错误信息")
logger.critical("严重错误信息")
```

---

## 📚 第七部分：附录

### 7.1 相关文档索引

| 文档 | 位置 | 用途 |
|------|------|------|
| **详细实施计划** | `OpenClaw-C方案-事件驱动任务队列-详细实施计划.md` | 原始设计和规划文档 |
| **总结报告** | `OpenClaw-C方案-事件驱动任务队列-总结报告.md` | 实施成果总结报告 |
| **工具系统文档** | `OpenClaw-Kali工具目录系统-介绍文档.md` | 工具目录系统详细说明 |
| **事件协议** | `events/EVENT_PROTOCOL.md` | 事件格式和协议规范 |
| **代理工具指南** | `workspaces/*/TOOLS.md` | 各代理专用工具和约束 |

### 7.2 技术参考

#### OpenClaw原版文档
- **位置**: `/home/asus/.npm-global/lib/node_modules/openclaw/docs/`
- **用途**: 参考原版架构和功能设计

#### Kali工具手册
- **参考**: 各工具的man页面和官方文档
- **示例**: `man nmap`, `sqlmap --help`, `john --help`

#### 相关技术标准
- **JSON Schema**: 事件格式验证参考
- **ISO 8601**: 时间戳格式标准
- **UUID v4**: 事件ID生成标准

### 7.3 联系方式

#### 项目维护
- **当前维护者**: OpenClaw Command Agent
- **问题反馈**: 通过会话渠道报告

#### 技术支持
- **OpenClaw社区**: https://discord.com/invite/clawd
- **GitHub仓库**: https://github.com/openclaw/openclaw
- **文档地址**: https://docs.openclaw.ai

### 7.4 更新记录

| 版本 | 日期 | 主要更新 |
|------|------|----------|
| v1.0 | 2026-03-28 | 初始版本，整合所有架构文档 |
| v1.1 | 计划中 | 添加更多代码示例和测试用例 |
| v2.0 | 计划中 | 包含阶段二功能（优先级队列等） |

---

## 🏁 文档总结

本文档提供了OpenClaw C方案魔改版的**完整架构设计说明**，涵盖：

1. **架构理念** - 从同步到异步的事件驱动转型
2. **技术实现** - 队列机制、协议设计、消费者流程
3. **代理体系** - 专业化分工、职责约束、工作流
4. **工具系统** - 智能发现、安全约束、集成方式
5. **运维监控** - 状态检查、存储管理、故障处理
6. **开发指南** - 代码结构、修改流程、测试方法

**关键设计原则**:
- ✅ **职责分离**: 指挥官不执行，专业化代理各司其职
- ✅ **异步解耦**: 事件队列协调，避免直接依赖
- ✅ **安全约束**: 无线保护、代理权限、工具限制
- ✅ **可观测性**: 完整监控、日志记录、状态追踪
- ✅ **可扩展性**: 水平扩展设计，支持分布式演进

**下一步方向**:
- 阶段二：优先级队列、Webhook通知、可视化监控
- 阶段三：记忆管理系统、知识图谱构建
- 阶段四：分布式扩展、多节点部署

**文档状态**: 🟢 最新版本，与代码同步  
**维护承诺**: 持续更新，反映架构变更
