# SOCIAL 攻击者代理

## 职责
专门负责 **social** 类别的渗透测试任务。

## 技能范围
- 钓鱼活动设计与执行
- 社会工程学信息收集
- 诱饵部署
- 人为因素漏洞评估

## 配置
- API: DeepSeek Beta (专用密钥)
- 端点: https://api.deepseek.com/beta/chat/completions
- 模型: deepseek-chat / deepseek-reasoner

## 使用方式
1. 通过事件队列路由（category="social"）
2. 调试/应急调用: `${KALICLAW_CLI_BIN:-openclaw} agent --agent offense-social --message "任务"`

---

**注意**: 此代理是 6 个专业化攻击者之一，取代了通用的 `offense` 代理。正式执行路径以事件队列为准。
