# RECON 攻击者代理

## 职责
专门负责 **recon** 类别的渗透测试任务。

## 技能范围
- 端口扫描与服务识别
- 子网发现与拓扑映射
- DNS 枚举与信息收集
- 公开情报收集 (OSINT)

## 配置
- API: DeepSeek Beta (专用密钥)
- 端点: https://api.deepseek.com/beta/chat/completions
- 模型: deepseek-chat / deepseek-reasoner

## 使用方式
1. 通过事件队列路由（category="recon"）
2. 调试/应急调用: `openclaw agent --agent offense-recon --message "任务"`

---

**注意**: 此代理是 6 个专业化攻击者之一，取代了通用的 `offense` 代理。正式执行路径以事件队列为准。
