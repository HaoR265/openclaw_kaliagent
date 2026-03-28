# 事件协议

## 文档定位

当前仓库处于 v2 迁移期：

- 正式真源是 `SQLite/WAL`
- `tasks-YYYY-MM-DD.jsonl` 与 `results.jsonl` 仍保留兼容镜像格式

因此本协议分成两层：

1. 数据库正式字段口径
2. JSONL 兼容事件/结果格式

## 一、正式任务口径

正式任务存储在 `tasks` 表中。

### 核心字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | 是 | 任务 ID，当前默认复用事件 UUID |
| `workflow_id` | string | 否 | 工作流 ID |
| `parent_task_id` | string | 否 | 父任务 ID |
| `correlation_id` | string | 是 | 关联 ID，当前默认与 `id` 相同 |
| `capability` | string | 是 | 正式能力类别：`wireless`、`recon`、`web`、`internal`、`exploit`、`social` |
| `operation` | string | 是 | 任务操作名，例如 `port-scan` |
| `requested_by` | string | 是 | 任务发布方，当前默认 `command` |
| `target_agent` | string | 否 | 目标代理，例如 `offense-recon` |
| `state` | string | 是 | 正式状态机字段 |
| `priority` | number | 是 | 优先级，默认 `50` |
| `payload_json` | string | 是 | 任务原始 payload JSON |
| `policy_ref` | string | 否 | 任务级策略引用 |
| `idempotency_key` | string | 否 | 幂等键 |
| `schedule_at` | string | 否 | 可执行时间 |
| `lease_owner` | string | 否 | 当前租约持有 worker |
| `lease_expires_at` | string | 否 | 租约过期时间 |
| `attempt_count` | number | 是 | 已尝试次数 |
| `max_attempts` | number | 是 | 最大尝试次数 |
| `timeout_seconds` | number | 否 | 超时秒数 |
| `last_error_code` | string | 否 | 最近错误码 |
| `last_error_message` | string | 否 | 最近错误说明 |
| `created_at` | string | 是 | 创建时间 |
| `started_at` | string | 否 | 开始时间 |
| `completed_at` | string | 否 | 完成时间 |

### 正式状态机

| 状态 | 说明 |
|------|------|
| `queued` | 已入队，等待 worker claim |
| `leased` | 已被 worker claim，正在租约中 |
| `running` | 已进入执行阶段 |
| `succeeded` | 执行成功 |
| `failed` | 执行失败且不再重试 |
| `retry_wait` | 已失败，等待下次重试 |
| `dead_letter` | 达到重试上限，进入死信状态 |
| `canceled` | 已取消 |

## 二、JSONL 兼容事件格式

兼容文件：`tasks-YYYY-MM-DD.jsonl`

### 字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | 是 | 唯一标识符（UUID） |
| `type` | string | 是 | 事件类型 |
| `agent` | string | 是 | 目标代理，兼容字段 |
| `category` | string | 否 | 与当前 `capability` 一一对应 |
| `task` | string | 是 | 任务标识符 |
| `params` | object | 否 | 任务参数 |
| `status` | string | 是 | 兼容状态字段 |
| `createdAt` | string | 是 | 创建时间 |
| `processedAt` | string | 否 | 开始处理时间 |
| `completedAt` | string | 否 | 完成时间 |
| `retryCount` | number | 否 | 已重试次数 |
| `maxRetries` | number | 否 | 最大重试次数 |
| `deadLetter` | boolean | 否 | 兼容死信标记 |
| `statusHistory` | array | 否 | 兼容状态历史 |

### 兼容状态映射

| JSONL 状态 | 数据库状态 |
|-----------|------------|
| `pending` | `queued` |
| `processing` | `running` |
| `completed` | `succeeded` |
| `failed` | `failed` |

### 兼容事件示例

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "scan",
  "agent": "offense-recon",
  "category": "recon",
  "task": "port-scan",
  "params": {
    "target": "192.168.1.0/24",
    "topPorts": 100
  },
  "status": "pending",
  "createdAt": "2026-03-28T10:00:00Z",
  "retryCount": 0,
  "maxRetries": 3,
  "deadLetter": false,
  "statusHistory": []
}
```

## 三、正式结果口径

正式结果写入 `results` 与 `artifacts` 表。

### `results` 表

| 字段 | 类型 | 说明 |
|------|------|------|
| `task_id` | string | 对应任务 ID |
| `status` | string | `succeeded` 或 `failed` |
| `summary_json` | string | 高层摘要 |
| `structured_json` | string | 结构化结果 |
| `created_at` | string | 写入时间 |

### `artifacts` 表

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | artifact ID |
| `task_id` | string | 对应任务 ID |
| `kind` | string | `stdout`、`stderr`、`report` 等 |
| `path` | string | 文件路径 |
| `mime_type` | string | MIME 类型 |
| `size_bytes` | number | 文件大小 |
| `sha256` | string | 内容哈希 |
| `created_at` | string | 写入时间 |

## 四、JSONL 兼容结果格式

兼容文件：`results.jsonl`

```json
{
  "eventId": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "rawData": {
    "task": "port-scan",
    "params": {
      "target": "192.168.1.0/24",
      "topPorts": 100
    },
    "executionResult": {
      "success": true,
      "data": {
        "openPorts": [22, 80, 443]
      },
      "message": "扫描完成",
      "executionSource": "local_tool"
    },
    "category": "recon",
    "apiUsed": false,
    "executionSource": "local_tool"
  },
  "metadata": {
    "duration": 12,
    "toolsUsed": ["nmap"],
    "apiUsed": false,
    "executionSource": "local_tool",
    "agentCategory": "recon"
  },
  "createdAt": "2026-03-28T10:00:12Z"
}
```

## 五、兼容期说明

- `publish.py` 仍会双写 SQLite 与 JSONL
- `worker.py` 仍会同步兼容 JSONL 状态与结果
- `status.py` 和 `summarize.py` 已优先读取数据库
- 新增字段应优先加到数据库模型，再决定是否映射到兼容 JSONL
