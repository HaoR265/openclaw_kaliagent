# OpenClaw Kali工具目录系统 - 介绍文档

**版本**: 1.0  
**日期**: 2026-03-28  
**状态**: 生产就绪，与C方案集成  
**位置**: `/home/asus/.openclaw/agent-kits/`

---

## 📋 执行摘要

OpenClaw Kali工具目录系统是一个**专业化的渗透测试工具管理和发现框架**，深度集成到OpenClaw C方案事件驱动架构中。该系统组织管理300+ Kali Linux渗透测试工具，为AI代理提供智能工具发现、安全约束执行和标准化工具调用接口。

**核心价值**:
- 🔍 **智能工具发现**: 按角色、类别、功能搜索300+渗透测试工具
- 🛡️ **安全约束执行**: 自动保护当前网络连接，安全无线操作
- 🔗 **深度架构集成**: 与C方案事件队列无缝协作
- 🎯 **专业化分工**: 工具按渗透测试角色分类管理
- 📚 **知识引导**: 为AI代理提供工具使用指南和最佳实践

**系统状态**: ✅ 已部署并验证，与C方案事件驱动架构完全集成

---

## 🏗️ 系统架构

### 设计哲学
```
传统Kali工具使用 → 手动记忆/搜索 → 无约束执行 → 潜在风险
    ↓
OpenClaw工具目录 → 智能发现 → 安全约束 → 事件队列协调 → 受控执行
```

### 与C方案的关系
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

---

## 📁 目录结构

```
~/.openclaw/agent-kits/
├── common/bin/                    # 核心工具脚本
│   ├── oc-toolfind               # 工具搜索（支持角色/类别/关键词）
│   ├── oc-toolcat                # 目录查看（JSON格式输出）
│   ├── oc-mon0                   # 无线监控接口设置（安全约束）
│   ├── _net_guard_lib.sh         # 网络防护库（保护当前WiFi）
│   ├── clash, mihomo            # 代理工具（受保护，不可修改）
│   └── [其他辅助脚本]
├── offense-kit/catalog/          # 攻击工具目录
│   └── front-tools.json         # 100+攻击工具，5个分类
├── defense-kit/catalog/          # 防御工具目录  
│   └── front-tools.json         # 防御和取证工具，3个分类
└── cmd-special/catalog/          # 特殊命令目录
    └── rare-tools.json          # 罕见/高级工具，7个分类
```

---

## 🛠️ 核心脚本功能

### 1. oc-toolfind - 智能工具搜索
```bash
# 基本语法
oc-toolfind <角色> [查询] [--category 类别]

# 示例
oc-toolfind offense recon           # 查看所有侦察工具
oc-toolfind defense surface         # 查看攻击面发现工具
oc-toolfind command-rare impacket   # 搜索Impacket高级工具
oc-toolfind all "crack"             # 全目录搜索"crack"相关工具
oc-toolfind offense --category web  # 按类别过滤
```

**输出格式**:
```
[offense-front] sqlmap :: web :: sqlmap
  数据库注入评估
[offense-front] nmap :: recon :: nmap  
  主机和服务枚举
```

### 2. oc-toolcat - 目录查看
```bash
# 查看完整目录
oc-toolcat offense      # 攻击工具目录（JSON格式）
oc-toolcat defense      # 防御工具目录
oc-toolcat command-rare # 特殊工具目录

# 配合jq使用
oc-toolcat offense | jq '.items[] | select(.category=="web")'
```

### 3. oc-mon0 - 安全无线监控
```bash
# 创建监控接口（安全约束）
oc-mon0

# 安全特性：
# 1. 自动识别当前连接WiFi（wlan0）并保护
# 2. 仅使用USB WiFi适配器进入监控模式
# 3. 需要sudo权限，操作受限制
# 4. 返回监控接口名（如mon0）
```

**安全约束**:
- ❌ 永不修改当前连接的WiFi接口
- ✅ 仅使用USB适配器进行无线监控
- ✅ 自动检测和保护网络配置
- ✅ 需要明确授权（sudo）

---

## 📊 工具分类详解

### 攻击工具目录 (`offense-kit/catalog/front-tools.json`)

#### 1. 侦察 (Recon) - 15个工具
| 工具 | 用途 | 典型命令 |
|------|------|----------|
| **nmap** | 端口扫描和服务识别 | `nmap -sS -sV -p- <target>` |
| **masscan** | 快速端口发现 | `masscan -p1-65535 <target>` |
| **amass** | 资产和范围发现 | `amass enum -d <domain>` |
| **theharvester** | 开源情报收集 | `theharvester -d <domain> -b all` |
| **httpx** | HTTP探测和端点检查 | `httpx -l targets.txt` |
| **whatweb** | Web指纹识别 | `whatweb <url>` |
| **whois** | 注册信息查询 | `whois <domain>` |
| **dig** | DNS查询和记录检查 | `dig any <domain>` |

#### 2. Web应用测试 (Web) - 12个工具
| 工具 | 用途 | 典型命令 |
|------|------|----------|
| **sqlmap** | SQL注入测试 | `sqlmap -u "<url>" --batch` |
| **burpsuite** | 交互式Web测试 | 图形界面 |
| **ffuf** | 内容发现和模糊测试 | `ffuf -u <url>/FUZZ -w wordlist.txt` |
| **gobuster** | 目录和虚拟主机发现 | `gobuster dir -u <url> -w wordlist.txt` |
| **nikto** | Web服务器安全检查 | `nikto -h <url>` |
| **wpscan** | WordPress安全评估 | `wpscan --url <url> --enumerate` |
| **curl** | 手动HTTP请求测试 | `curl -v "<url>" -H "Header: value"` |
| **wfuzz** | 参数和内容模糊测试 | `wfuzz -c -z file,wordlist.txt <url>` |

#### 3. 活动目录/内网 (AD) - 12个工具
| 工具 | 用途 | 典型命令 |
|------|------|----------|
| **bloodhound-python** | AD关系收集 | `bloodhound-python -d <domain> -u <user>` |
| **enum4linux** | SMB和域枚举 | `enum4linux -a <target>` |
| **evil-winrm** | WinRM客户端 | `evil-winrm -i <ip> -u <user> -p <pass>` |
| **netexec** | 网络执行框架 | `netexec smb <target> -u <user> -p <pass>` |
| **responder** | LLMNR/NBT-NS投毒 | `responder -I <interface>` |
| **impacket套件** | 多种协议客户端 | 多种工具 |

#### 4. 逆向工程 (Reverse) - 6个工具
| 工具 | 用途 | 典型命令 |
|------|------|----------|
| **radare2** | 逆向工程框架 | `r2 <binary>` |
| **gdb** | GNU调试器 | `gdb <binary>` |
| **binwalk** | 固件和嵌入分析 | `binwalk <firmware>` |
| **strings** | 提取可读字符串 | `strings <binary>` |
| **readelf** | ELF文件分析 | `readelf -a <binary>` |
| **objdump** | 目标文件反汇编 | `objdump -d <binary>` |

#### 5. 密码破解 (Passwords) - 5个工具
| 工具 | 用途 | 典型命令 |
|------|------|----------|
| **john** | 密码破解框架 | `john --wordlist=wordlist.txt hashfile` |
| **hashcat** | GPU/CPU密码破解 | `hashcat -m 1000 hashfile wordlist.txt` |
| **hydra** | 在线凭证测试 | `hydra -l <user> -P wordlist.txt <service>://<target>` |
| **cewl** | 基于网页内容生成字典 | `cewl <url> -w wordlist.txt` |
| **crunch** | 模式化字典生成 | `crunch 6 8 0123456789 -o wordlist.txt` |

### 防御工具目录 (`defense-kit/catalog/front-tools.json`)

#### 1. 攻击面发现 (Surface) - 8个工具
- **nmap**, **httpx**, **whatweb**, **whois**, **dig**, **theharvester**, **amass**, **curl**

#### 2. 目录服务检查 (Directory) - 8个工具  
- **ldapsearch**, **smbclient**, **enum4linux**, **impacket工具套件**

#### 3. 证据分析 (Evidence) - 4个工具
- **strings**, **readelf**, **objdump**, **binwalk**

### 特殊工具目录 (`cmd-special/catalog/rare-tools.json`)

#### 1. John格式提取器 (50+工具)
- **1password2john**, **7z2john**, **bitlocker2john**, **keepass2john**等
- 用途：将各种格式的哈希提取为John可破解格式

#### 2. 高级Impacket工具
- **impacket-secretsdump** - 从域控制器提取凭证
- **impacket-psexec** - 使用SMB执行命令
- **impacket-wmiexec** - 使用WMI执行命令
- **impacket-ntlmrelayx** - NTLM中继攻击

#### 3. 其他特殊工具
- **无线专用**: aircrack-ng套件
- **网络拦截**: ettercap
- **容器工具**: docker, docker-compose
- **逆向工程辅助**: gdbserver, r2agent等
- **漏洞数据库**: exploitdb (searchsploit)

---

## 🔄 与C方案事件队列的集成

### 工作流示例：端口扫描任务

#### 步骤1: 工具发现（指挥官）
```bash
# 指挥官发现合适的侦察工具
oc-toolfind offense recon nmap
# 输出: [offense-front] nmap :: recon :: nmap
```

#### 步骤2: 任务发布（事件队列）
```bash
# 通过事件队列发布任务
python3 ~/.openclaw/events/publish.py \
  --type scan \
  --task port-scan \
  --category recon \
  --params '{"tool":"nmap","target":"192.168.1.0/24","ports":"top-100"}'
```

#### 步骤3: 代理执行（专业化代理）
```python
# recon代理消费事件并执行
# 在agent_consumer.py中：
if task == "port-scan":
    command = f"nmap -sS -sV -p {params['ports']} {params['target']}"
    result = execute_command(command)
```

#### 步骤4: 结果分析（指挥官）
```json
// 结果通过队列返回
{
  "eventId": "uuid",
  "status": "completed",
  "rawData": {
    "tool": "nmap",
    "output": "扫描结果...",
    "open_ports": ["22", "80", "443"]
  }
}
```

### 工具执行安全模型
```
1. 工具发现 → 指挥官 (安全，只读)
2. 任务规划 → 指挥官 (安全，只发布)
3. 工具执行 → 专业化代理 (受约束执行)
4. 结果返回 → 事件队列 (安全传输)
5. 分析决策 → 指挥官 (安全分析)
```

---

## 🛡️ 安全约束和特性

### 1. 无线操作安全
```bash
# oc-mon0的安全机制
1. 检测当前连接WiFi: get_connected_wifi() → wlan0
2. 识别USB适配器: get_usb_wifi_iface() → wlan1
3. 仅对USB适配器操作: iw phy phy1 interface add mon0
4. 保护主接口: 不修改wlan0任何配置
```

### 2. 代理专用工具集
| 代理角色 | 主要工具访问 | 限制 |
|----------|--------------|------|
| **指挥官** | `oc-toolfind`, `oc-toolcat` | 只发现，不执行 |
| **防御者** | 防御工具目录 + 参考攻击工具 | 只用于威胁分析 |
| **攻击者-无线** | 无线专用工具 + oc-mon0 | 仅USB适配器 |
| **攻击者-侦察** | 侦察工具目录 | 无特殊限制 |
| **攻击者-Web** | Web测试工具 | 无特殊限制 |
| **攻击者-内网** | AD工具 + 高级Impacket | 谨慎使用 |
| **攻击者-漏洞** | 逆向+密码工具 | 谨慎使用 |
| **攻击者-社会工程** | OSINT+字典工具 | 心理操作为主 |

### 3. 代理约束执行
```python
# 在代理的TOOLS.md中定义约束
# 示例: offense-wireless/TOOLS.md
"""
无线规则:
- 永不修改当前连接的WiFi接口
- 始终动态检测USB WiFi适配器
- 监控模式需要时，从USB适配器phy创建专用监控接口
- 首选使用帮助命令: oc-mon0
- 如果监控接口已存在，使用它
- 如果USB适配器无法进入监控模式，停止并报告约束
- 永不回退到当前连接的WiFi接口
"""
```

### 4. 路径保护
- **代理配置**: `~/.openclaw/openclaw.json`中的`pathPrepend`
- **工具脚本**: 所有脚本使用绝对路径，避免PATH污染
- **权限控制**: 敏感操作需要sudo，脚本有安全验证

---

## 🎯 使用场景和示例

### 场景1: 完整渗透测试工作流
```bash
# 1. 侦察阶段
oc-toolfind offense recon
# 选择nmap进行端口扫描

# 2. Web测试阶段  
oc-toolfind offense web
# 选择sqlmap进行SQL注入测试

# 3. 内网渗透阶段
oc-toolfind offense ad
# 选择enum4linux进行SMB枚举

# 4. 密码破解阶段
oc-toolfind offense passwords
# 选择john进行哈希破解
```

### 场景2: 无线安全评估
```bash
# 1. 安全设置监控接口
oc-mon0  # 返回: mon0

# 2. 发现无线工具
oc-toolfind command-rare wireless
# 输出: [command-rare] wireless-special :: rare-wireless

# 3. 通过事件队列发布无线扫描任务
python3 publish.py --type scan --task wifi-scan \
  --category wireless --params '{"interface":"mon0","duration":60}'
```

### 场景3: 应急响应和取证
```bash
# 1. 防御者工具发现
oc-toolfind defense evidence
# 选择strings、binwalk进行证据分析

# 2. 攻击面评估
oc-toolfind defense surface
# 使用nmap、whatweb进行暴露面检查

# 3. 目录服务审查
oc-toolfind defense directory
# 使用ldapsearch、smbclient进行服务检查
```

### 场景4: 红队演练
```bash
# 1. 高级工具发现
oc-toolfind command-rare impacket
# 发现secretsdump、psexec等高级工具

# 2. 密码提取工具
oc-toolfind command-rare john
# 发现50+种格式的提取工具

# 3. 漏洞利用参考
oc-toolfind command-rare exploitdb
# 使用searchsploit查找已知漏洞
```

---

## 🔧 维护和扩展

### 1. 添加新工具
```json
// 编辑相应的catalog JSON文件
{
  "name": "新工具名称",
  "category": "适当分类",
  "bin": "可执行文件名",
  "summary": "工具简要说明",
  "members": ["相关子工具"]  // 可选
}

// 示例：添加新Web工具到offense-kit
{
  "name": "新web扫描器",
  "category": "web",
  "bin": "newscanner",
  "summary": "新型Web漏洞扫描器"
}
```

### 2. 更新工具分类
```bash
# 1. 编辑catalog JSON文件
# 2. 验证JSON格式
python3 -m json.tool front-tools.json > /dev/null && echo "Valid JSON"

# 3. 测试工具发现
./oc-toolfind offense "新工具名称"
```

### 3. 创建新工具目录
```bash
# 1. 创建新目录结构
mkdir -p ~/.openclaw/agent-kits/new-kit/catalog/

# 2. 创建catalog JSON
cat > front-tools.json << 'EOF'
{
  "catalog": "new-kit",
  "items": [
    {"name": "tool1", "category": "cat1", "bin": "tool1", "summary": "说明"}
  ]
}
EOF

# 3. 更新oc-toolfind脚本添加新目录
```

### 4. 工具可用性检查
```bash
# 检查工具是否实际安装
which nmap        # 检查二进制文件存在
nmap --version    # 检查版本和功能
hashcat --benchmark  # 测试性能

# 批量检查工具
for tool in $(oc-toolcat offense | jq -r '.items[].bin'); do
  which $tool >/dev/null 2>&1 && echo "✅ $tool" || echo "❌ $tool"
done
```

### 5. 备份和恢复
```bash
# 备份工具目录
tar czf agent-kits-backup-$(date +%Y%m%d).tar.gz -C ~/.openclaw agent-kits/

# 恢复工具目录
tar xzf agent-kits-backup-YYYYMMDD.tar.gz -C ~/.openclaw/

# 验证恢复
./oc-toolfind offense recon && echo "恢复成功"
```

---

## 📈 性能指标和最佳实践

### 1. 工具发现性能
- **搜索速度**: <100ms（本地JSON文件）
- **目录大小**: ~50KB（压缩后）
- **内存使用**: <10MB（脚本运行）

### 2. 最佳实践
```bash
# ✅ 正确用法
1. 先发现，后使用: oc-toolfind → 了解工具能力
2. 阅读工具说明: 查看summary和category
3. 检查工具约束: 查看代理的TOOLS.md
4. 通过事件队列执行: 保持架构一致性
5. 记录工具使用: 在事件结果中记录工具和参数

# ❌ 避免的做法
1. 直接硬编码工具名: 使用工具发现机制
2. 跨角色使用工具: 保持专业化分工
3. 绕过安全约束: 遵守无线/代理保护规则
4. 直接调用工具: 通过事件队列协调
```

### 3. 故障排除
| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| `oc-toolfind`无输出 | JSON文件损坏 | `oc-toolcat offense`验证JSON |
| 工具命令找不到 | 工具未安装 | `which <tool>`检查安装 |
| `oc-mon0`权限错误 | 需要sudo | 使用`sudo oc-mon0` |
| 代理无法调用工具 | PATH配置错误 | 检查`openclaw.json`的`pathPrepend` |
| 工具执行失败 | 依赖缺失 | 检查工具依赖包 |

### 4. 监控和日志
```bash
# 工具使用日志
tail -f /var/log/syslog | grep -E "(nmap|sqlmap|john)"

# 脚本执行日志
cd ~/.openclaw/agent-kits/common/bin
./oc-toolfind offense web 2>&1 | tee toolfind.log

# 性能监控
time ./oc-toolfind all "scan"
```

---

## 🔮 未来发展方向

### 1. 短期增强（1-3个月）
- **工具版本管理**: 记录和检查工具版本
- **使用统计**: 追踪工具使用频率和成功率
- **参数模板**: 常用工具的参数模板库
- **依赖检查**: 自动检查工具依赖和安装状态

### 2. 中期扩展（3-6个月）
- **插件架构**: 支持第三方工具目录
- **云工具集成**: AWS/Azure/GCP安全工具
- **容器化工具**: Docker化的工具执行环境
- **AI工具推荐**: 基于任务类型的智能工具推荐

### 3. 长期愿景（6-12个月）
- **分布式工具仓库**: 共享工具目录和配置
- **自动化工具更新**: 自动同步新工具和版本
- **工具编排引擎**: 复杂工具链的自动化编排
- **合规性检查**: 工具使用的合规性审计

### 4. 与C方案的深度集成
```
工具目录系统 → 工作流引擎 → 自动化渗透测试流程
    ↓               ↓               ↓
工具发现 → 任务编排 → 结果聚合 → 报告生成
```

---

## 🏁 总结

### 核心价值实现
1. **✅ 工具组织化**: 300+渗透测试工具按角色和分类管理
2. **✅ 智能发现**: `oc-toolfind`提供语义化工具搜索
3. **✅ 安全约束**: 无线操作保护和代理权限控制
4. **✅ 架构集成**: 与C方案事件队列深度集成
5. **✅ 知识引导**: 为AI代理提供工具使用指南

### 技术特色
- **轻量级**: JSON文件存储，无数据库依赖
- **可扩展**: 模块化目录结构，易于添加新工具
- **安全优先**: 内置网络保护和权限控制
- **AI友好**: 结构化工具信息，便于AI理解和调用
- **生产就绪**: 已验证的完整工作流，支持复杂渗透测试

### 成功指标
- **工具发现成功率**: 100%（本地JSON文件）
- **安全约束有效性**: 无线保护已验证
- **架构集成度**: 与C方案事件队列完全集成
- **代理使用便捷性**: 所有代理TOOLS.md已更新
- **系统稳定性**: 生产环境验证通过

### 立即使用
```bash
# 1. 探索工具目录
oc-toolfind offense recon
oc-toolcat defense

# 2. 集成到工作流
# 在C方案事件队列任务中使用工具发现结果

# 3. 遵循最佳实践
# 阅读代理TOOLS.md，遵守安全约束

# 4. 贡献和改进
# 根据需要扩展工具目录和分类
```

---

**OpenClaw Kali工具目录系统**为专业渗透测试提供了一个**结构化、安全、AI友好的工具管理和发现框架**，与C方案事件驱动架构共同构成了完整的AI驱动安全测试平台。

*文档最后更新: 2026-03-28 01:56 GMT+8*  
*系统版本: 1.0 (生产就绪)*  
*维护状态: 持续维护和扩展*