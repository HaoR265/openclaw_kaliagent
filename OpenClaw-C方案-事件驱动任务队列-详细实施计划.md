# OpenClaw C方案 - 事件驱动任务队列详细实施计划

## 项目概述

### 背景
原始的OpenClaw架构包含三类代理：指挥官(command)、攻击者(offense)、防御者(defense)。攻击者作为单一通用代理，负责所有渗透测试任务的执行。随着任务类型的增加，通用代理的负担过重，且职责不够清晰。

### 目标
1. **职责分离**：将通用攻击者代理拆分为6个专业化攻击者
2. **异步执行**：通过事件队列实现任务发布与执行的解耦
3. **可扩展性**：支持未来新增更多专业化攻击者类别
4. **可靠性**：实现任务重试、死信队列、状态追踪
5. **可观测性**：提供完整的监控和日志系统

### 核心思想
- **指挥官(command)**：只负责分析、决策、委托，不执行具体操作
- **专业化攻击者**：6个独立代理，每个专注于特定渗透测试领域
- **事件驱动**：任务通过队列异步传递，消费者按类别处理
- **原始数据反馈**：攻击者返回原始执行数据，指挥官进行分析提炼

---

## 架构设计

### 三层架构
```
┌─────────────────┐    发布事件    ┌─────────────────┐
│    指挥官       │──────────────▶│   事件队列       │
│   (command)     │                │ (tasks-*.jsonl) │
└─────────────────┘                └────────┬────────┘
         │                                  │ 消费者拉取
         │                                  ▼
         │                        ┌─────────────────┐
         │                        │专业化攻击者代理 │
         │                        │   (6个类别)     │
         └────────────────────────┼─────────────────┤
           结果汇总               │  • wireless     │
                                  │  • recon        │
                                  │  • web          │
                                  │  • internal     │
                                  │  • exploit      │
                                  │  • social       │
                                  └────────┬────────┘
                                           │ 写入结果
                                           ▼
                                  ┌─────────────────┐
                                  │   结果存储      │
                                  │ (results.jsonl) │
                                  └─────────────────┘
```

### 6个专业化攻击者类别

| 类别 | 代号 | 职责范围 | 典型任务 |
|------|------|----------|----------|
| **无线渗透** | `wireless` | WiFi监控、抓包、破解、WPS攻击 | `scan-cmcc`, `capture-handshake`, `wps-attack` |
| **网络侦察** | `recon` | 端口扫描、服务识别、子网发现、OSINT | `nmap-scan`, `service-detection`, `subnet-discovery` |
| **Web应用攻击** | `web` | SQL注入、XSS、目录遍历、API测试 | `sql-injection`, `xss-scan`, `dir-brute` |
| **内网渗透** | `internal` | 横向移动、凭证窃取、权限提升 | `pass-the-hash`, `lateral-movement`, `privilege-escalation` |
| **漏洞利用** | `exploit` | 已知漏洞利用（Metasploit、PoC） | `msf-exploit`, `cve-poc`, `exploit-chain` |
| **社会工程** | `social` | 钓鱼、信息收集、诱饵部署 | `phishing-campaign`, `osint-gather`, `bait-deployment` |

### 技术栈
- **队列存储**：JSONL文件（按日期分片）
- **消费者**：Python脚本 + cron作业
- **API调用**：DeepSeek Beta (严格的函数调用和工具调用能力)
- **监控**：Python脚本 + 日志文件
- **配置管理**：OpenClaw JSON配置 + 独立API密钥

---

## 已完成的工作

### 1. 基础设施
| 组件 | 位置 | 状态 | 说明 |
|------|------|------|------|
| **事件目录** | `~/.openclaw/events/` | ✅ 完成 | 所有队列相关文件的根目录 |
| **分片存储** | `tasks-YYYY-MM-DD.jsonl` | ✅ 完成 | 按日期分片，避免单文件过大 |
| **结果存储** | `results.jsonl` | ✅ 完成 | 所有执行结果的统一存储 |
| **死信队列** | `dead-letter.jsonl` | ✅ 完成 | 重试耗尽事件的存储 |
| **归档目录** | `events/archive/` | ✅ 完成 | 旧事件文件的压缩存储 |

### 2. 核心脚本
| 脚本 | 功能 | 使用方式 |
|------|------|----------|
| **publish.py** | 发布新事件到队列 | `python3 publish.py --type <type> --task <task> --category <category> --params '{}'` |
| **agent_consumer.py** | 专业化攻击者消费者 | `python3 agent_consumer.py --category <category> [--once]` |
| **status.py** | 队列状态监控 | `python3 status.py` |
| **summarize.py** | 结果汇总分析 | `python3 summarize.py --last <N> --category <category>` |
| **archive.py** | 旧事件归档压缩 | `python3 archive.py --days 7 --keep` |

### 3. 代理配置
| 代理ID | 配置目录 | API密钥 | 状态 |
|--------|----------|---------|------|
| `offense-wireless` | `~/.openclaw/agents/offense-wireless/` | `sk-b5caaee6333247fbb3281cddf839ea5d` | ✅ 已配置 |
| `offense-recon` | `~/.openclaw/agents/offense-recon/` | `sk-1f37071b3d6a4dcb8f4c8230488fede9` | ✅ 已配置 |
| `offense-web` | `~/.openclaw/agents/offense-web/` | `sk-6e0260ca2e5646929e95e1f5f4907328` | ✅ 已配置 |
| `offense-internal` | `~/.openclaw/agents/offense-internal/` | `sk-52bcfb2cd5964eae98751e023d7d74bb` | ✅ 已配置 |
| `offense-exploit` | `~/.openclaw/agents/offense-exploit/` | `sk-f99582d889484114b6cb96a69d735884` | ✅ 已配置 |
| `offense-social` | `~/.openclaw/agents/offense-social/` | `sk-32a0a13256cb4d6780a41d9489a7de04` | ✅ 已配置 |

### 4. OpenClaw配置
**配置文件**: `~/.openclaw/openclaw.json`
```json
{
  "agents": {
    "list": [
      {
        "id": "offense-wireless",
        "workspace": "/home/asus/.openclaw/workspaces/offense",
        "agentDir": "/home/asus/.openclaw/agents/offense-wireless/agent",
        "model": { "primary": "deepseek/deepseek-chat" },
        // ... 其他配置
      },
      // ... 其他5个代理配置
    ]
  }
}
```

### 5. API配置
**配置文件**: `~/.openclaw/events/apis.json`
```json
{
  "wireless": {
    "api_key": "sk-b5caaee6333247fbb3281cddf839ea5d",
    "base_url": "https://api.deepseek.com/beta",
    "endpoint": "/chat/completions",
    "model": "deepseek-chat",
    "callback_url": "http://localhost:8000/results"
  },
  // ... 其他5个类别配置
}
```

### 6. 自动化部署
| 自动化项 | 配置 | 运行频率 |
|----------|------|----------|
| **消费者cron作业** | `* * * * * cd /home/asus/.openclaw/events && python3 agent_consumer.py --category wireless >> wireless.log 2>&1` | 每分钟 |
| **归档cron作业** | `0 2 * * * cd /home/asus/.openclaw/events && python3 archive.py --days 7 >> archive.log 2>&1` | 每日2:00 |

---

## 技术实现细节

### 1. 事件协议
**文件格式**: JSONL (每行一个完整的JSON对象)

**事件字段**:
```json
{
  "id": "uuid-v4",
  "type": "scan|attack|test|...",
  "agent": "offense",
  "category": "wireless|recon|web|internal|exploit|social",
  "task": "scan-cmcc|ping|...",
  "params": {},
  "status": "pending|processing|completed|failed",
  "createdAt": "ISO-8601",
  "processedAt": "ISO-8601",
  "completedAt": "ISO-8601",
  "retryCount": 0,
  "maxRetries": 3,
  "deadLetter": false,
  "statusHistory": []
}
```

### 2. 结果格式
**文件格式**: JSONL

**结果字段**:
```json
{
  "eventId": "uuid-v4",
  "status": "completed|failed",
  "rawData": {
    "task": "scan-cmcc",
    "params": {},
    "executionResult": {
      "success": true,
      "data": {},
      "message": "执行完成",
      "executionSource": "agent-api|agent-fallback"
    },
    "category": "wireless",
    "apiUsed": true,
    "executionSource": "agent-api"
  },
  "metadata": {
    "duration": 5,
    "toolsUsed": ["airodump-ng"],
    "apiUsed": true,
    "executionSource": "agent-api",
    "agentCategory": "wireless"
  },
  "createdAt": "ISO-8601"
}
```

### 3. 消费者工作流程
```
1. 读取当天任务文件
2. 查找指定类别的pending事件
3. 获取文件锁（避免并发）
4. 更新事件状态为processing
5. 释放文件锁
6. 调用对应API（或本地执行）
7. 重新获取文件锁
8. 更新事件状态为completed/failed
9. 写入结果文件
10. 如果失败且重试次数未超限，增加retryCount
11. 如果重试次数超限，移至死信队列
```

### 4. API调用逻辑
```python
# 请求格式
{
  "model": "deepseek-chat",
  "messages": [
    {
      "role": "system", 
      "content": "你是 {category} 攻击者代理，执行渗透测试任务。请始终以JSON格式返回结果..."
    },
    {
      "role": "user",
      "content": f"任务: {task}\n参数: {json.dumps(params)}"
    }
  ],
  "max_tokens": 2000,
  "temperature": 0.1,
  "response_format": {"type": "json_object"}
}

# 重试机制
- 最大重试次数: 3次
- 超时递增: 30秒, 60秒, 90秒
- 错误处理: 401(停止), 429(等待Retry-After), 5xx(重试)
```

### 5. 文件锁机制
```python
import fcntl

# 获取排他锁
with open(lock_file, "w") as lock:
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    # 处理文件...
    fcntl.flock(lock, fcntl.LOCK_UN)  # 释放锁
```

---

## 操作指南

### 1. 环境检查
```bash
# 检查OpenClaw服务状态
openclaw gateway status
openclaw agents list

# 检查事件目录结构
ls -la ~/.openclaw/events/

# 检查代理配置
ls -la ~/.openclaw/agents/offense-*/
```

### 2. 发布任务
```bash
cd ~/.openclaw/events

# 无线扫描任务
python3 publish.py --type scan --task scan-cmcc --category wireless \
  --params '{"interface":"wlan1","duration":30,"channels":"1-13"}'

# 网络侦察任务
python3 publish.py --type scan --task port-scan --category recon \
  --params '{"target":"192.168.1.0/24","ports":"1-1000"}'

# Web测试任务
python3 publish.py --type test --task sql-injection --category web \
  --params '{"url":"http://example.com/login","method":"POST"}'

# 内网渗透任务
python3 publish.py --type attack --task lateral-movement --category internal \
  --params '{"target":"192.168.1.100","technique":"pth"}'

# 漏洞利用任务
python3 publish.py --type exploit --task cve-2024-1234 --category exploit \
  --params '{"target":"192.168.1.50","cve":"CVE-2024-1234"}'

# 社会工程任务
python3 publish.py --type campaign --task phishing --category social \
  --params '{"targets":["user@example.com"],"template":"login"}'
```

### 3. 监控状态
```bash
# 查看队列总体状态
python3 status.py

# 查看特定类别的事件
python3 status.py | grep -A5 "按类别分布"

# 查看最近结果
python3 summarize.py --last 10

# 查看特定类别的结果
python3 summarize.py --last 5 --category wireless

# 查看JSON格式的原始结果
python3 summarize.py --last 3 --json | jq .

# 查看消费者日志
tail -f ~/.openclaw/events/wireless.log
tail -f ~/.openclaw/events/recon.log
```

### 4. 手动操作
```bash
# 手动运行消费者（处理一个事件后退出）
python3 agent_consumer.py --category wireless --once

# 直接调用代理（绕过队列）
timeout 30 openclaw agent --agent offense-wireless --message "测试任务"

# 检查死信队列
cat ~/.openclaw/events/dead-letter.jsonl | wc -l

# 归档旧文件（模拟运行）
python3 archive.py --dry-run --days 7

# 实际归档
python3 archive.py --days 7 --keep
```

### 5. 故障排查
```bash
# 检查cron作业
crontab -l | grep agent_consumer

# 检查进程状态
pgrep -f "python3.*agent_consumer"

# 检查文件锁状态
ls -la ~/.openclaw/events/*.lock

# 检查API连通性
curl -X POST https://api.deepseek.com/beta/chat/completions \
  -H "Authorization: Bearer sk-b5caaee6333247fbb3281cddf839ea5d" \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-chat","messages":[{"role":"user","content":"test"}],"max_tokens":10}' \
  -v

# 检查OpenClaw网关
openclaw gateway restart
sleep 3
openclaw gateway status
```

---

## 配置说明

### 1. 事件协议文档
**位置**: `~/.openclaw/events/EVENT_PROTOCOL.md`
包含所有字段的详细定义、示例、版本历史。

### 2. 代理配置模板
每个代理目录包含:
```
offense-wireless/
├── agent/
│   ├── models.json          # 模型和API配置
│   ├── AGENTS.md            # 代理职责文档
│   └── ...其他OpenClaw配置
└── sessions/                # 会话存储
```

### 3. API密钥管理
- **存储**: `~/.openclaw/events/apis.json`
- **加密**: 当前为明文，建议未来添加加密
- **轮换**: 支持API密钥轮换，只需更新配置文件

### 4. 日志配置
每个代理的cron作业输出到独立日志文件:
- `wireless.log` - 无线渗透代理日志
- `recon.log` - 网络侦察代理日志
- `web.log` - Web攻击代理日志
- `internal.log` - 内网渗透代理日志
- `exploit.log` - 漏洞利用代理日志
- `social.log` - 社会工程代理日志
- `consumer.log` - 旧消费者日志（已弃用）
- `archive.log` - 归档作业日志

---

## 故障排除

### 常见问题及解决方案

| 问题 | 症状 | 解决方案 |
|------|------|----------|
| **事件未被处理** | 状态一直为pending | 1. 检查消费者进程 `pgrep -f agent_consumer`<br>2. 检查cron作业 `crontab -l`<br>3. 检查文件锁 `ls -la *.lock`<br>4. 手动运行消费者测试 |
| **API调用失败** | 消费者日志显示API错误 | 1. 检查API密钥有效性<br>2. 检查网络连接<br>3. 检查DeepSeek服务状态<br>4. 检查请求格式和参数 |
| **文件锁死锁** | 消费者卡住，lock文件存在 | 1. 删除lock文件 `rm -f *.lock`<br>2. 重启消费者进程<br>3. 检查文件权限 |
| **存储空间不足** | 写入失败，磁盘已满 | 1. 运行归档脚本 `python3 archive.py --days 3`<br>2. 清理旧日志文件<br>3. 检查磁盘使用率 `df -h` |
| **代理未识别** | `openclaw agents list`不显示新代理 | 1. 检查`openclaw.json`配置<br>2. 重启网关 `openclaw gateway restart`<br>3. 检查代理目录权限 |
| **结果解析失败** | `summarize.py`报JSON解析错误 | 1. 检查results.jsonl格式<br>2. 删除损坏的行<br>3. 修复消费者脚本的响应处理 |

### 调试步骤
```bash
# 1. 检查基础状态
python3 status.py

# 2. 检查日志
tail -50 ~/.openclaw/events/wireless.log

# 3. 手动测试发布
python3 publish.py --type test --task ping --category wireless --params '{"message":"debug"}'

# 4. 手动测试消费
python3 agent_consumer.py --category wireless --once

# 5. 检查结果
tail -5 ~/.openclaw/events/results.jsonl | python3 -m json.tool

# 6. 检查API连通性
curl -s https://api.deepseek.com/beta/chat/completions -X POST \
  -H "Authorization: Bearer $(grep -A1 '"wireless"' ~/.openclaw/events/apis.json | grep api_key | cut -d'"' -f4)" \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-chat","messages":[{"role":"user","content":"ping"}],"max_tokens":10}' \
  -w "\nHTTP %{http_code}\n"
```

---

## 未来路线图

### 阶段一：清理与优化（1-2周）
1. **删除旧配置**
   - 移除通用`offense`代理目录
   - 清理`openclaw.json`中的旧条目
   - 更新所有文档引用

2. **路由绑定配置**
   - 实验`openclaw agents bind`命令
   - 建立标签到代理的直接调用链路
   - 文档化直接调用流程

3. **错误处理增强**
   - 完善消费者脚本的重试逻辑
   - 添加更详细的错误日志
   - 实现优雅降级机制

4. **存储优化**
   - 实施归档策略（每日自动运行）
   - 添加存储使用监控
   - 实现自动清理策略

### 阶段二：高级特性（3-5周）
5. **优先级队列**
   - 为事件添加`priority`字段（高、中、低）
   - 修改消费者优先处理高优先级任务
   - 实现优先级抢占机制

6. **Webhook通知**
   - 任务完成时自动推送通知
   - 支持多种通知渠道（HTTP、邮件、消息应用）
   - 可配置的通知模板

7. **可视化监控**
   - 简单Web面板显示队列状态
   - 实时执行历史查看
   - API健康度监控

8. **工作流引擎**
   - 支持任务依赖关系
   - 条件分支执行
   - 并行任务处理

### 阶段三：记忆管理系统（6-8周）
9. **记忆切片设计**
   - 将重要结果切片存储
   - 支持语义搜索
   - 关联查询能力

10. **记忆压缩算法**
    - 定期压缩去重
    - 提炼关键信息
    - 知识蒸馏

11. **知识图谱构建**
    - 建立任务、结果、实体关联
    - 图数据库存储
    - 可视化关系网络

12. **长期记忆存储**
    - 分层存储设计（热、温、冷数据）
    - 自动数据迁移
    - 记忆生命周期管理

### 阶段四：分布式扩展（9-12周）
13. **分布式队列**
    - 迁移到Redis/RabbitMQ
    - 支持多节点消费者
    - 队列分区和分片

14. **负载均衡**
    - 同类别的多个消费者实例
    - 智能任务分配
    - 资源利用率优化

15. **故障转移**
    - 自动检测失败消费者
    - 任务重新分配
    - 状态恢复机制

16. **跨节点通信**
    - 代理间协作协议
    - 信息共享机制
    - 分布式锁服务

---

## 维护指南

### 日常维护
```bash
# 每日检查
1. 检查队列状态: python3 status.py
2. 检查磁盘空间: df -h ~/.openclaw/
3. 检查日志大小: ls -lh ~/.openclaw/events/*.log
4. 检查消费者进程: pgrep -f agent_consumer | wc -l

# 每周维护
1. 归档旧文件: python3 archive.py --days 7
2. 清理旧日志: find ~/.openclaw/events -name "*.log" -mtime +30 -delete
3. 验证API密钥: 测试每个类别的API连通性
4. 备份配置: cp -r ~/.openclaw/ ~/.openclaw-backup-$(date +%Y%m%d)
```

### 性能监控指标
| 指标 | 正常范围 | 检查命令 |
|------|----------|----------|
| 队列长度 | 0-100 | `python3 status.py | grep "待处理"` |
| 处理延迟 | <60秒 | 查看事件`createdAt`和`processedAt`时间差 |
| API成功率 | >95% | `grep -c "API调用成功" *.log` |
| 磁盘使用 | <80% | `df -h /home/asus | tail -1` |
| 内存使用 | <70% | `free -m | grep Mem` |

### 备份策略
```bash
# 配置文件备份
tar -czf ~/backups/openclaw-config-$(date +%Y%m%d).tar.gz \
  ~/.openclaw/openclaw.json \
  ~/.openclaw/events/apis.json \
  ~/.openclaw/events/EVENT_PROTOCOL.md

# 完整备份（每周）
tar -czf ~/backups/openclaw-full-$(date +%Y%m%d).tar.gz \
  ~/.openclaw/ \
  --exclude="*.log" \
  --exclude="*.gz" \
  --exclude="archive/*"
```

---

## 附录

### A. 文件位置汇总
| 文件/目录 | 路径 | 用途 |
|-----------|------|------|
| 事件目录 | `~/.openclaw/events/` | 所有队列相关文件 |
| 代理配置 | `~/.openclaw/agents/offense-*/` | 6个专业化攻击者配置 |
| OpenClaw配置 | `~/.openclaw/openclaw.json` | OpenClaw主配置文件 |
| 指挥官工作区 | `~/.openclaw/workspaces/command/` | 指挥官代理工作区 |
| 攻击者工作区 | `~/.openclaw/workspaces/offense/` | 攻击者代理工作区（共享） |
| 备份目录 | `~/backups/` | 配置文件备份 |

### B. 命令速查
```bash
# 发布任务
python3 publish.py --type <type> --task <task> --category <category> --params '{}'

# 监控状态
python3 status.py
python3 summarize.py --last <N> --category <category>

# 手动操作
python3 agent_consumer.py --category <category> --once
python3 archive.py --days <N> --keep

# OpenClaw命令
openclaw gateway status
openclaw agents list
openclaw agent --agent offense-wireless --message "任务"
```

### C. 联系方式
- **项目仓库**: https://github.com/openclaw/openclaw
- **文档地址**: https://docs.openclaw.ai
- **社区Discord**: https://discord.com/invite/clawd
- **问题报告**: GitHub Issues

### D. 版本历史
| 版本 | 日期 | 变更说明 |
|------|------|----------|
| v1.0 | 2026-03-27 | 初始版本，完成C方案基础架构 |
| v1.1 | 计划中 | 优先级队列、Webhook通知 |
| v2.0 | 计划中 | 记忆管理系统 |
| v3.0 | 计划中 | 分布式扩展 |

---

**文档最后更新**: 2026-03-27 20:05 GMT+8  
**维护者**: OpenClaw Command Agent  
**状态**: 生产就绪（基础功能）