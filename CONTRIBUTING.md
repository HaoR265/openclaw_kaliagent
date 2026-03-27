# OpenClaw C方案 - 贡献指南

**版本**: 1.0  
**最后更新**: 2026-03-28  
**目标读者**: AI代码助手（Codex/Cursor等）、开发者、贡献者

---

## 📋 简介

本文档提供OpenClaw C方案魔改版的**代码修改和贡献指南**，专门为AI代码助手（如Codex、Cursor、Claude Code等）优化，帮助AI理解项目结构、修改流程和编码规范。

### 主要目标
1. **AI友好**: 提供结构化信息，便于AI理解和操作
2. **标准化**: 定义统一的修改流程和代码规范
3. **安全**: 确保修改不破坏现有架构和安全约束
4. **可维护**: 保持代码质量和项目一致性

### 适用场景
- AI助手自动修改代码
- 开发者手动修改和扩展
- 代码审查和质量检查
- 新功能开发和集成测试

---

## 🏗️ 项目结构理解

### 核心目录说明
```
~/.openclaw/
├── 📁 events/                    # 事件队列核心（主要修改区域）
│   ├── 📄 publish.py           # 事件发布 - 添加新事件类型
│   ├── 📄 agent_consumer.py    # 消费者逻辑 - 添加新任务处理
│   ├── 📄 status.py            # 状态监控 - 扩展监控功能
│   ├── 📄 archive.py           # 归档管理 - 修改存储策略
│   ├── 📄 storage_monitor.py   # 存储监控 - 调整阈值和告警
│   ├── 📄 summarize.py         # 结果汇总 - 添加新分析功能
│   └── 📄 EVENT_PROTOCOL.md    # 协议文档 - 更新协议定义
├── 📁 agent-kits/              # 工具目录系统
│   ├── 📁 common/bin/         # 核心脚本 - 扩展工具功能
│   ├── 📁 offense-kit/catalog/ # 攻击工具目录 - 添加新工具
│   ├── 📁 defense-kit/catalog/ # 防御工具目录 - 添加新工具
│   └── 📁 cmd-special/catalog/ # 特殊工具目录 - 添加高级工具
├── 📁 agents/                  # 代理配置（谨慎修改）
│   ├── 📁 command/           # 指挥官配置
│   ├── 📁 defense/           # 防御者配置
│   └── 📁 offense-*/         # 攻击者配置（6个专业化代理）
├── 📁 workspaces/             # 代理工作空间
│   └── 📁 */TOOLS.md         # 代理工具指南 - 更新约束和指南
├── 📄 openclaw.json           # 主配置文件（重要，修改需谨慎）
├── 📄 README.md               # 项目说明文档
├── 📄 ARCHITECTURE.md         # 架构设计文档
├── 📄 CONTRIBUTING.md         # 本文档
└── 📄 DOCUMENTATION.md        # 文档导航
```

### 当前正式基线
- 正式代理总数为 8 个：`command`、`defense` 与 6 个 `offense-*` 专业攻击代理
- 正式执行路径为：`events/publish.py` 发布到 `tasks-YYYY-MM-DD.jsonl`，由 `events/agent_consumer.py` 按类别消费
- `openclaw agent --agent offense-*` 仅作为调试或应急入口，不作为默认执行路径
- 历史共享 `offense` 路径已清理出正式结构；旧版 `events/consume.py` 与各 `workspaces/offense-*/consume.py` 已废弃

### 遗留项识别
- `events/consume.py`：历史消费者入口，已废弃
- `workspaces/offense-*/consume.py`：历史 workspace 内本地消费者入口，已废弃
- 如果在旧会话、旧备份或历史快照中看到共享 `offense` 路径，应视为历史记录而非现行架构

### 关键文件修改优先级
| 文件 | 修改频率 | 风险等级 | AI修改建议 |
|------|----------|----------|------------|
| `events/` 下Python脚本 | 高 | 中 | ✅ AI可安全修改，遵循现有模式 |
| `agent-kits/` catalog JSON | 高 | 低 | ✅ AI可安全添加/修改工具条目 |
| 代理 `TOOLS.md` 文件 | 中 | 低 | ✅ AI可更新文档和指南 |
| `openclaw.json` 配置 | 低 | 高 | ⚠️ AI需谨慎，建议人工验证 |
| 代理配置目录 | 低 | 高 | ⚠️ AI需遵循现有结构，避免破坏 |

### 不建议直接修改的遗留项
- `events/consume.py`
- `workspaces/offense-*/consume.py`

这些文件已被降级为废弃或历史兼容入口。默认做法是保持阻断状态，不要在这些文件上继续开发新逻辑。

---

## 🔧 AI修改代码指南

### 1. 基本原则
```python
# ✅ 正确做法：遵循现有模式和结构
# 当添加新功能时，参考现有类似功能的实现

# ❌ 错误做法：引入全新的编程范式
# 不要完全重写现有模块，保持一致性

# ✅ 正确：增量修改，小步前进
# ❌ 错误：大规模重构，影响稳定性
```

### 2. 代码风格规范

#### Python代码规范
```python
# 1. 遵循PEP 8，使用4空格缩进
def function_name(parameter_name):
    """函数docstring，说明功能和参数"""
    # 实现逻辑
    return result

# 2. 使用明确的类型提示（Python 3.8+）
from typing import Dict, List, Optional, Any

def process_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """处理事件并返回结果"""
    # 实现逻辑
    return {"success": True, "data": {}}

# 3. 错误处理使用具体异常类型
try:
    result = api_call(data)
except requests.exceptions.Timeout:
    logger.error("请求超时")
    return {"success": False, "error": "timeout"}
except ValueError as e:
    logger.error(f"参数错误: {e}")
    return {"success": False, "error": "invalid_param"}

# 4. 日志记录使用统一格式
import logging
logger = logging.getLogger(__name__)

logger.debug("详细调试信息")  # 开发时使用
logger.info("正常操作信息")   # 常规操作记录
logger.warning("警告信息")    # 需要注意但不影响运行
logger.error("错误信息")      # 错误但可恢复
logger.critical("严重错误")   # 系统级错误
```

#### Shell脚本规范
```bash
#!/usr/bin/env bash
# 1. 使用set -euo pipefail保证健壮性
set -euo pipefail

# 2. 变量使用引号防止空值问题
name="value"
echo "$name"

# 3. 函数使用明确的前缀避免冲突
oc_helper_function() {
    local var_name="$1"  # 使用local变量
    # 函数逻辑
}

# 4. 错误信息输出到stderr
echo "错误信息" >&2
exit 1
```

#### JSON配置文件规范
```json
{
  // 1. 保持一致的缩进（2空格）
  "key": "value",
  
  // 2. 添加注释说明复杂字段
  "complex_field": {
    // 说明：这个字段用于XXX功能
    "subfield": "value"
  },
  
  // 3. 保持字段排序一致性
  "name": "工具名称",
  "category": "工具类别", 
  "bin": "可执行文件",
  "summary": "简要说明",
  "members": ["子工具列表"]  // 可选字段
}
```

### 3. 安全约束检查

#### 无线操作安全（必须检查）
```python
# 在修改任何无线相关代码时，必须包含：
def wireless_operation():
    # 1. 检查当前连接WiFi
    connected_wifi = get_connected_wifi()  # wlan0
    if not connected_wifi:
        raise SecurityError("无法检测当前WiFi连接")
    
    # 2. 确保只使用USB适配器
    usb_adapter = get_usb_wifi_iface()  # wlan1
    if not usb_adapter:
        raise SecurityError("未找到USB WiFi适配器")
    
    # 3. 禁止修改当前连接接口
    if "wlan0" in command or connected_wifi in command:
        raise SecurityError(f"禁止修改当前连接接口: {connected_wifi}")
    
    # 4. 使用oc-mon0辅助函数
    monitor_iface = run_command("oc-mon0")
    return monitor_iface
```

#### 代理权限约束
```python
# 各代理有严格的权限限制
def check_agent_permission(agent_id, action):
    permission_map = {
        "command": ["analyze", "decide", "delegate"],  # 只能分析/决策/委托
        "offense-wireless": ["wireless_scan", "monitor_mode"],  # 仅无线操作
        "offense-recon": ["port_scan", "host_discovery"],  # 仅侦察
        # ... 其他代理
    }
    
    if action not in permission_map.get(agent_id, []):
        raise PermissionError(f"代理 {agent_id} 无权执行 {action}")
```

### 4. 测试要求

#### 修改前必须运行的测试
```bash
#!/bin/bash
# test_before_modify.sh

echo "=== 修改前验证测试 ==="

# 1. 基础功能测试
python3 events/status.py > /dev/null && echo "✅ 状态检查正常"
python3 -m json.tool events/EVENT_PROTOCOL.md > /dev/null 2>&1 && echo "✅ 协议文档正常"

# 2. 配置验证
openclaw config validate --json | grep -q '"valid":true' && echo "✅ 配置验证通过"

# 3. 关键脚本语法检查
python3 -m py_compile events/publish.py && echo "✅ publish.py语法正确"
python3 -m py_compile events/agent_consumer.py && echo "✅ agent_consumer.py语法正确"
python3 -m py_compile events/status.py && echo "✅ status.py语法正确"

# 4. 工具系统检查
./agent-kits/common/bin/oc-toolfind offense recon > /dev/null && echo "✅ 工具发现正常"
./agent-kits/common/bin/oc-toolcat offense | python3 -m json.tool > /dev/null && echo "✅ 工具目录正常"

echo "=== 预检查完成，可开始修改 ==="
```

#### 修改后必须运行的测试
```bash
#!/bin/bash
# test_after_modify.sh

echo "=== 修改后验证测试 ==="

# 1. 完整工作流测试
./test_full_workflow.sh

# 2. 新功能专项测试（如果有）
if [ -f "test_new_feature.sh" ]; then
    ./test_new_feature.sh
fi

# 3. 性能影响测试
START_EVENTS=$(python3 events/status.py | grep "总事件数" | awk '{print $2}')
./test_performance.sh
END_EVENTS=$(python3 events/status.py | grep "总事件数" | awk '{print $2}')

# 4. 验证事件处理完整性
if [ "$START_EVENTS" -eq "$END_EVENTS" ]; then
    echo "✅ 事件处理完整性验证通过"
else
    echo "⚠️  事件数量变化: $START_EVENTS -> $END_EVENTS"
    echo "   请检查是否有事件丢失或重复处理"
fi

echo "=== 修改验证完成 ==="
```

---

## 🚀 常见修改场景指南

### 场景1：添加新事件类型

#### 步骤指南
```python
# 1. 修改 events/publish.py
def publish_event(event_type, task, category, params):
    # 在事件类型验证中添加新类型
    valid_types = ['scan', 'test', 'attack', 'exploit', 'campaign', 'new_type']
    if event_type not in valid_types:
        raise ValueError(f"不支持的事件类型: {event_type}")
    
    # 2. 更新事件创建逻辑（如果需要特殊字段）
    event = {
        'id': str(uuid.uuid4()),
        'type': event_type,
        'task': task,
        'category': category,
        'params': params,
        'status': 'pending',
        # ... 其他标准字段
    }
    
    # 3. 添加对新类型的特殊处理（如果需要）
    if event_type == 'new_type':
        event['special_field'] = 'special_value'
    
    return event

# 4. 修改 events/agent_consumer.py
def process_event(event):
    if event['task'] == 'new_task':
        return execute_new_task(event['params'])
    
    # 或者按类型处理
    if event['type'] == 'new_type':
        return process_new_type_event(event)

# 5. 更新 events/EVENT_PROTOCOL.md
# 添加新类型的文档说明，包括：
# - 类型名称和用途
# - 必需和可选字段
# - 示例事件格式
# - 处理结果格式

# 6. 创建测试用例
# test_new_event_type.sh
```

注意：不要在 `events/consume.py` 或 `workspaces/offense-*/consume.py` 上添加新处理逻辑，这些文件不是正式执行链。

#### 测试脚本模板
```bash
#!/bin/bash
# test_new_event_type.sh

echo "=== 新事件类型测试 ==="

# 1. 发布新类型事件
EVENT_ID=$(python3 events/publish.py \
  --type new_type \
  --task new_task \
  --category recon \
  --params '{"test": "value"}' | grep "事件 ID:" | awk '{print $3}')

echo "发布新类型事件: $EVENT_ID"

# 2. 处理事件
python3 events/agent_consumer.py --once --category recon

# 3. 验证结果
if grep -q "$EVENT_ID" events/results.jsonl; then
    RESULT=$(grep "$EVENT_ID" events/results.jsonl | tail -1)
    STATUS=$(echo "$RESULT" | python3 -c "import json,sys; print(json.loads(sys.stdin.read())['status'])")
    
    if [ "$STATUS" = "completed" ]; then
        echo "✅ 新事件类型处理成功"
        echo "$RESULT" | python3 -m json.tool
    else
        echo "❌ 新事件类型处理失败: $STATUS"
        exit 1
    fi
else
    echo "❌ 未找到事件结果"
    exit 1
fi
```

### 场景2：添加新工具到目录

#### 步骤指南
```bash
# 1. 确定工具所属目录
# - 攻击工具: agent-kits/offense-kit/catalog/front-tools.json
# - 防御工具: agent-kits/defense-kit/catalog/front-tools.json  
# - 特殊工具: agent-kits/cmd-special/catalog/rare-tools.json

# 2. 编辑对应的JSON文件
# 添加新工具条目，格式如下：
{
  "name": "新工具名称",
  "category": "existing_or_new_category",
  "bin": "executable_name",
  "summary": "简要功能说明",
  "members": ["sub_tool1", "sub_tool2"]  # 可选，对于工具集
}

# 3. 验证JSON格式
python3 -m json.tool front-tools.json > /dev/null

# 4. 测试工具发现
./oc-toolfind offense "新工具名称"
./oc-toolfind offense --category "工具类别"

# 5. 更新相关代理的TOOLS.md
# 如果新工具针对特定代理，更新对应workspace的TOOLS.md
# 例如：workspaces/offense-recon/TOOLS.md
```

#### 验证脚本
```bash
#!/bin/bash
# test_new_tool.sh

echo "=== 新工具添加验证 ==="

TOOL_NAME="newtool"
TOOL_CATEGORY="newcategory"

# 1. 验证工具在目录中
if ./oc-toolfind offense "$TOOL_NAME" | grep -q "$TOOL_NAME"; then
    echo "✅ 工具发现功能正常"
else
    echo "❌ 工具未在目录中找到"
    exit 1
fi

# 2. 验证按类别查找
if ./oc-toolfind offense --category "$TOOL_CATEGORY" | grep -q "$TOOL_NAME"; then
    echo "✅ 类别分类正常"
else
    echo "❌ 工具未正确分类"
    exit 1
fi

# 3. 验证工具实际可用性（如果已安装）
if which "$TOOL_NAME" > /dev/null 2>&1; then
    echo "✅ 工具已安装"
    # 可选：测试基本功能
    # "$TOOL_NAME" --version || "$TOOL_NAME" --help
else
    echo "⚠️  工具未安装，仅目录添加完成"
fi

echo "=== 新工具验证完成 ==="
```

### 场景3：修改事件处理逻辑

#### 步骤指南
```python
# 1. 在 events/agent_consumer.py 中添加新处理函数
def process_new_task(params):
    """
    处理新任务类型。
    
    参数:
        params: 任务参数字典
        
    返回:
        dict: 处理结果，包含success、data、message等字段
    """
    try:
        # 实现具体逻辑
        result_data = execute_specific_operation(params)
        
        return {
            "success": True,
            "data": result_data,
            "message": "任务执行成功",
            "executionSource": "agent-api"
        }
    except Exception as e:
        logger.error(f"任务执行失败: {e}")
        return {
            "success": False,
            "data": {},
            "message": f"任务执行失败: {str(e)}",
            "executionSource": "agent"
        }

# 2. 在主处理逻辑中添加分支
def handle_event(event):
    task_handlers = {
        'port-scan': process_port_scan,
        'dir-brute': process_dir_brute,
        'sql-injection': process_sql_injection,
        'new-task': process_new_task,  # 新增
    }
    
    handler = task_handlers.get(event['task'])
    if handler:
        return handler(event['params'])
    else:
        return {"success": False, "message": f"未知任务类型: {event['task']}"}

# 3. 添加必要的工具调用
def execute_specific_operation(params):
    # 使用工具目录中的工具
    tool_info = find_tool("specific_tool")
    if not tool_info:
        raise ValueError("未找到所需工具")
    
    # 构建命令并执行
    command = build_command(tool_info['bin'], params)
    result = run_command(command)
    
    # 解析结果
    return parse_result(result)
```

注意：当前唯一正式消费者是 `events/agent_consumer.py`。如果修改事件处理逻辑，不要把新逻辑写入遗留 `consume.py` 文件。

#### 测试修改
```bash
#!/bin/bash
# test_event_handler.sh

echo "=== 事件处理逻辑测试 ==="

# 1. 创建测试事件
TEST_PARAMS='{"param1": "value1", "param2": "value2"}'
EVENT_ID=$(python3 events/publish.py \
  --type test \
  --task new-task \
  --category recon \
  --params "$TEST_PARAMS" | grep "事件 ID:" | awk '{print $3}')

echo "测试事件ID: $EVENT_ID"

# 2. 运行消费者处理
python3 events/agent_consumer.py --once --category recon

# 3. 检查处理结果
RESULT_JSON=$(grep "$EVENT_ID" events/results.jsonl | tail -1)
if [ -n "$RESULT_JSON" ]; then
    echo "✅ 事件已处理"
    
    # 提取关键信息
    SUCCESS=$(echo "$RESULT_JSON" | python3 -c "import json,sys; print(json.loads(sys.stdin.read())['rawData']['executionResult']['success'])")
    MESSAGE=$(echo "$RESULT_JSON" | python3 -c "import json,sys; print(json.loads(sys.stdin.read())['rawData']['executionResult']['message'])")
    
    echo "处理结果: success=$SUCCESS, message=$MESSAGE"
    
    if [ "$SUCCESS" = "True" ]; then
        echo "✅ 任务执行成功"
    else
        echo "❌ 任务执行失败"
        exit 1
    fi
else
    echo "❌ 未找到处理结果"
    exit 1
fi
```

---

## 📝 文档更新要求

### 代码修改必须更新的文档

#### 1. 协议文档 (`EVENT_PROTOCOL.md`)
```markdown
## 新事件类型：new_type

### 用途说明
用于处理XXX类型的任务。

### 事件格式
```json
{
  "type": "new_type",
  "task": "new_task",
  "params": {
    "required_field": "类型说明",
    "optional_field": "类型说明（可选）"
  }
}
```

### 处理结果格式
```json
{
  "success": true/false,
  "data": {
    // 特定返回数据
  },
  "message": "处理结果说明"
}
```

### 示例
```bash
python3 publish.py --type new_type --task new_task \
  --category recon --params '{"field": "value"}'
```
```

#### 2. 代理工具指南 (`workspaces/*/TOOLS.md`)
```markdown
## 新工具/功能

### 新工具名称
- **用途**: 功能说明
- **命令**: `toolname --option value`
- **示例**: `toolname --target example.com`

### 相关任务
- 任务类型: `new-task`
- 参数格式: `{"param": "value"}`
- 使用场景: 说明何时使用此功能
```

#### 3. 架构文档 (`ARCHITECTURE.md`)
```markdown
### 新增功能：功能名称

#### 设计目的
说明为什么添加此功能。

#### 实现方式
描述技术实现细节。

#### 使用示例
提供具体使用示例。

#### 相关修改
- 修改文件: `events/agent_consumer.py` (添加处理逻辑)
- 新增文件: `events/new_module.py` (如果有)
- 配置更新: `openclaw.json` (如果有)
```

### 文档质量检查
```bash
#!/bin/bash
# check_documentation.sh

echo "=== 文档质量检查 ==="

# 1. 检查所有Markdown文件语法
for md_file in *.md events/*.md workspaces/*/*.md; do
    if [ -f "$md_file" ]; then
        python3 -m markdown -x extra "$md_file" > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            echo "✅ $md_file 语法正确"
        else
            echo "❌ $md_file 语法错误"
        fi
    fi
done

# 2. 检查链接有效性
echo "检查文档链接..."

# 3. 检查代码示例格式
echo "检查代码示例缩进和格式..."

echo "=== 文档检查完成 ==="
```

---

## 🔍 代码审查要点

### AI生成代码审查清单
```python
# 审查项清单
REVIEW_CHECKLIST = {
    "security": [
        "无线操作是否保护当前连接",
        "代理权限是否被正确检查", 
        "敏感配置是否被保护",
        "输入参数是否被验证",
    ],
    "architecture": [
        "是否遵循事件驱动模式",
        "是否保持职责分离原则",
        "是否通过队列协调而非直接调用",
        "是否保持代理专业化分工",
    ],
    "code_quality": [
        "代码风格是否符合PEP 8",
        "错误处理是否完备",
        "日志记录是否适当",
        "函数是否有docstring",
        "类型提示是否完整",
    ],
    "testing": [
        "是否有对应的测试用例",
        "是否包含边界情况测试",
        "是否验证错误处理路径",
        "性能影响是否评估",
    ],
    "documentation": [
        "协议文档是否更新",
        "工具指南是否更新",
        "架构文档是否更新",
        "示例是否完整准确",
    ]
}
```

### 常见问题及修复

#### 问题1：直接调用而非通过队列
```python
# ❌ 错误：指挥官直接调用工具
def command_direct_call():
    result = run_command("nmap 127.0.0.1")  # 直接执行
    
# ✅ 正确：通过事件队列委托
def command_correct_way():
    event_id = publish_event("scan", "port-scan", "recon", {"target": "127.0.0.1"})
    # 等待结果通过队列返回
```

#### 问题2：缺少安全约束检查
```python
# ❌ 错误：无线操作无保护
def unsafe_wireless():
    os.system("iwconfig wlan0 mode monitor")  # 修改当前连接
    
# ✅ 正确：使用安全机制
def safe_wireless():
    monitor_iface = run_command("oc-mon0")  # 使用安全脚本
    # monitor_iface 是mon0（基于USB适配器）
```

#### 问题3：破坏代理专业化
```python
# ❌ 错误：代理执行非专业任务
def offense_recon_doing_web():
    # recon代理执行SQL注入
    run_command("sqlmap -u 'http://example.com'")
    
# ✅ 正确：保持专业化分工  
def offense_recon_proper():
    # recon代理只执行侦察任务
    run_command("nmap -sS 192.168.1.0/24")
    
def offense_web_proper():
    # web代理执行Web测试
    run_command("sqlmap -u 'http://example.com'")
```

---

## 📤 提交和部署

### Git提交规范
```bash
# 提交消息格式
# type(scope): description
#
# type类型:
#   feat:     新功能
#   fix:      修复bug  
#   docs:     文档更新
#   style:    代码格式调整
#   refactor: 代码重构
#   test:     测试相关
#   chore:    构建或工具更新
#
# 示例:
#   feat(event): 添加新事件类型new_type
#   fix(consumer): 修复API调用重试逻辑
#   docs(architecture): 更新架构文档

# 提交示例
git add events/agent_consumer.py
git add events/EVENT_PROTOCOL.md
git commit -m "feat(event): 添加新任务类型new-task支持"
```

### 部署前检查清单
```bash
#!/bin/bash
# pre_deployment_checklist.sh

echo "=== 部署前检查清单 ==="

# 1. 所有测试通过
./test_before_modify.sh
./test_after_modify.sh

# 2. 文档更新完成
grep -q "new_type" events/EVENT_PROTOCOL.md && echo "✅ 协议文档已更新"
grep -q "new-task" ARCHITECTURE.md && echo "✅ 架构文档已更新"

# 3. 配置验证
openclaw config validate --json | grep -q '"valid":true' && echo "✅ 配置验证通过"

# 4. 安全约束检查
./check_security_constraints.sh && echo "✅ 安全约束检查通过"

# 5. 性能基准测试
./test_performance.sh | grep -q "正常范围" && echo "✅ 性能影响可接受"

echo "=== 检查完成，可部署 ==="
```

### 回滚计划
```bash
#!/bin/bash
# rollback_plan.sh

echo "=== 修改回滚计划 ==="

# 1. 备份当前状态
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

cp events/publish.py "$BACKUP_DIR/"
cp events/agent_consumer.py "$BACKUP_DIR/"
cp events/EVENT_PROTOCOL.md "$BACKUP_DIR/"
cp openclaw.json "$BACKUP_DIR/" 2>/dev/null || true

echo "备份到: $BACKUP_DIR"

# 2. 回滚命令示例
echo ""
echo "如果需要回滚，执行:"
echo "  cp $BACKUP_DIR/publish.py events/"
echo "  cp $BACKUP_DIR/agent_consumer.py events/"
echo "  cp $BACKUP_DIR/EVENT_PROTOCOL.md events/"
echo "  [有条件地] cp $BACKUP_DIR/openclaw.json ."
echo "  openclaw gateway restart"
```

---

## ❓ 常见问题解答

### Q: AI如何确定应该修改哪个文件？
**A**: 根据修改类型：
- 事件相关：`events/` 目录下的Python脚本
- 工具相关：`agent-kits/` 目录下的JSON文件
- 配置相关：`openclaw.json` 和各代理配置目录
- 文档相关：`.md` 文件和各 `TOOLS.md`

优先顺序：
- 正式执行链优先看 `events/publish.py`、`events/agent_consumer.py`、`events/status.py`、`events/archive.py`
- 不要默认修改 `events/consume.py` 或各 `workspaces/offense-*/consume.py`

### Q: 修改后如何验证不影响现有功能？
**A**: 运行完整测试套件：
```bash
./test_full_workflow.sh  # 完整工作流测试
./test_regression.sh     # 回归测试（如果有）
python3 events/status.py # 检查系统状态
```

### Q: 遇到架构约束冲突怎么办？
**A**: 优先遵循架构原则：
1. 指挥官不执行具体操作
2. 专业化代理各司其职
3. 通过事件队列协调
4. 安全约束必须遵守
如果确实需要调整架构，先更新 `ARCHITECTURE.md` 文档。

### Q: 如何添加新的专业化代理？
**A**: 完整流程：
1. 设计代理职责和约束
2. 创建代理目录和配置
3. 更新 `openclaw.json`
4. 创建workspace和`TOOLS.md`
5. 测试代理功能
6. 更新所有相关文档

补充：
- 新代理应使用独立 workspace，例如 `workspaces/offense-new`
- 新代理必须使用独立 `workspaces/offense-*` 目录，不要重新引入共享 `offense` workspace

### Q: AI可以自动运行测试吗？
**A**: 是的，建议AI在修改后自动运行：
```bash
# 自动化测试流程
./test_before_modify.sh && \
  # 执行修改 && \
  ./test_after_modify.sh && \
  ./test_full_workflow.sh
```
如果测试失败，AI应尝试修复或回滚修改。

---

## 📝 变更记录要求

### 1. 必须遵循的变更记录流程
**所有AI/Codex修改必须**:
1. **记录变更**: 在`CHANGELOG.md`中添加完整记录
2. **遵循格式**: 使用标准变更记录模板
3. **验证后更新**: 测试通过后再更新变更记录
4. **关联文档**: 同步更新相关文档

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

### 3. Codex专用变更记录命令
```bash
# 自动记录变更的辅助脚本
./record_change.sh "Codex" "修改的文件" "变更描述"

# 或手动更新CHANGELOG.md
# 1. 打开CHANGELOG.md
# 2. 在"变更记录历史"部分添加新记录
# 3. 按照模板填写完整信息
# 4. 保存并提交到Git
```

### 4. 变更质量检查
| 检查项 | 要求 | 验证方法 |
|--------|------|----------|
| **记录完整性** | 所有必填字段完整 | 检查CHANGELOG.md格式 |
| **技术准确性** | 技术描述准确无误 | 代码审查和测试验证 |
| **文档同步** | 相关文档已更新 | 检查文档更新时间戳 |
| **回滚准备** | 回滚计划可行 | 验证备份文件存在 |

### 5. 变更记录验证脚本
```bash
#!/bin/bash
# validate_change_record.sh

echo "=== 变更记录验证 ==="

# 检查CHANGELOG.md格式
if tail -20 CHANGELOG.md | grep -q "## \[.*\] - .*"; then
    echo "✅ 变更记录格式正确"
else
    echo "❌ 变更记录格式错误"
    exit 1
fi

# 检查最近变更是否完整
RECENT_CHANGE=$(tail -50 CHANGELOG.md | grep -A20 "## \[.*\] -")
if echo "$RECENT_CHANGE" | grep -q "变更详情"; then
    echo "✅ 最近变更记录完整"
else
    echo "❌ 最近变更记录不完整"
    exit 1
fi

echo "=== 变更记录验证完成 ==="
```

---

## 🤝 AI协作核心规则

### 规则：提出更好的方案，但要先讨论
**最重要规则**：AI/Codex可以（也应该）提出更好的计划方案，但**必须**先与用户讨论并获得明确批准后才能实施。

### 1. 为什么需要这个规则？
- **用户是最终决策者**：用户最了解项目需求和约束
- **避免意外变更**：未经讨论的"改进"可能破坏现有工作流
- **确保方向一致**：保持项目架构和设计理念的一致性
- **控制风险**：有些改进可能有隐藏的风险或副作用

### 2. 什么情况下应该提出更好的方案？
- 发现当前实现有明显缺陷或瓶颈
- 有更高效、更安全、更可靠的技术方案
- 可以显著提升系统性能或用户体验
- 发现潜在的安全隐患需要改进
- 有新的架构模式更适合当前需求

### 3. 如何提出方案？（标准流程）
```markdown
## 改进方案提议：[简要标题]

### 1. 当前状况分析
- 现有实现的问题或限制
- 为什么需要改进

### 2. 建议的改进方案
- 具体的技术方案
- 如何实施（步骤）
- 技术选型和理由

### 3. 预期效益
- 性能提升（量化指标）
- 功能增强
- 安全性改进
- 可维护性提升

### 4. 风险评估
- 可能的风险和问题
- 兼容性影响
- 实施复杂度
- 回滚难度

### 5. 测试验证计划
- 如何测试改进效果
- 需要哪些测试用例
- 验证标准

### 6. 请求讨论
请审阅此方案并提出意见，是否批准实施？
```

### 4. 实施前必须满足的条件
- ✅ 方案已与用户详细讨论
- ✅ 用户明确批准实施（最好有文字确认）
- ✅ 完整的实施计划已制定
- ✅ 风险评估和缓解措施已准备
- ✅ 回滚计划已制定
- ✅ CHANGELOG.md更新计划已准备

### 5. 违规后果
如果AI未经讨论直接实施"改进"：
1. **紧急停止**：立即停止所有相关操作
2. **强制回滚**：按照回滚计划恢复到原始状态
3. **记录违规**：在CHANGELOG.md中记录违规行为
4. **重新评估**：重新从讨论阶段开始

### 6. 成功案例模板
```
AI: "我注意到事件队列的存储方式可能在大数据量时出现性能问题。
     我研究了一个更好的方案，使用SQLite代替JSONL文件，但需要先和您讨论。"

用户: "请详细说明你的方案，包括实施步骤和预期效果。"

AI: [提供详细的技术方案文档]

用户: "方案看起来不错，但我们需要先做小规模测试。请先实现原型验证。"

AI: "好的，我会先实现原型，测试通过后再申请全面实施。"
```

### 7. 特殊情况的处理
- **紧急安全修复**：可以先实施，但必须立即通知用户并补充讨论
- **微小改进**（如拼写错误、格式调整）：可以直接实施，但需要记录
- **实验性功能**：必须明确标记为实验性，并获得用户同意

### 8. 记住的原则
1. **用户是合作者，不是执行对象**
2. **讨论在前，实施在后**
3. **透明沟通所有技术决策**
4. **尊重用户的项目愿景和约束**
5. **即使是最优技术方案，也需要用户批准**

---

## 📞 技术支持

### 紧急问题处理
```bash
# 1. 立即停止修改
# 2. 运行诊断脚本
./diagnose_problem.sh

# 3. 查看错误日志
tail -f events/*.log

# 4. 回滚到稳定版本
git checkout main
openclaw gateway restart
```

### 获取更多帮助
- **架构文档**: `ARCHITECTURE.md` - 详细设计说明
- **协议文档**: `EVENT_PROTOCOL.md` - 事件格式规范
- **工具文档**: `OpenClaw-Kali工具目录系统-介绍文档.md` - 工具系统说明
- **原版文档**: `/home/asus/.npm-global/lib/node_modules/openclaw/docs/` - OpenClaw原版参考

### 反馈渠道
- 代码问题：通过Git提交和代码审查
- 架构问题：更新架构文档并讨论
- 安全问题：立即报告并修复

---

**文档状态**: 🟢 最新版本  
**维护承诺**: 随项目发展持续更新  
**目标**: 使AI能高效、安全地修改OpenClaw C方案代码
