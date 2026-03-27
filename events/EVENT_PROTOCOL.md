# 事件协议

## 事件字段
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | 是 | 唯一标识符（UUID v4） |
| `type` | string | 是 | 事件类型：`ping`、`scan-cmcc`、`wps-attack` 等 |
| `agent` | string | 是 | 目标代理：`offense`、`defense` |
| `category` | string | 否 | 攻击者类别：`wireless`、`recon`、`web`、`internal`、`exploit`、`social` |
| `task` | string | 是 | 任务标识符，对应具体脚本 |
| `params` | object | 否 | 任务参数（JSON 对象） |
| `status` | string | 是 | 状态：`pending`、`processing`、`completed`、`failed` |
| `createdAt` | string | 是 | ISO-8601 时间戳 |
| `processedAt` | string | 否 | 开始处理时间 |
| `completedAt` | string | 否 | 完成时间 |
| `retryCount` | number | 否 | 重试次数（默认 0） |
| `maxRetries` | number | 否 | 最大重试次数（默认 3） |
| `deadLetter` | boolean | 否 | 是否已进入死信队列 |
| `statusHistory` | array | 否 | 状态历史记录 `[{ status, at }]` |

## 结果字段
| 字段 | 类型 | 说明 |
|------|------|------|
| `eventId` | string | 对应事件 ID |
| `status` | string | `completed` 或 `failed` |
| `rawData` | object | 原始输出（JSON 对象） |
| `metadata` | object | 元数据：`duration`、`toolsUsed`、`outputSize` 等 |
| `createdAt` | string | 结果生成时间 |

## 示例
### 事件
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "scan",
  "agent": "offense",
  "task": "scan-cmcc",
  "params": { "interface": "wlan1", "duration": 30 },
  "status": "pending",
  "createdAt": "2026-03-27T08:30:00Z",
  "retryCount": 0,
  "maxRetries": 3,
  "deadLetter": false,
  "statusHistory": []
}
```

### 结果
```json
{
  "eventId": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "rawData": {
    "scanResults": [
      { "bssid": "aa:bb:cc:dd:ee:ff", "ssid": "CMCC", "channel": 6 }
    ],
    "captureFile": "/tmp/scan-01.cap",
    "logs": "airodump-ng output..."
  },
  "metadata": {
    "duration": 25,
    "toolsUsed": ["airodump-ng"],
    "outputSize": 1024
  },
  "createdAt": "2026-03-27T08:30:30Z"
}
```