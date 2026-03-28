# WIRELESS 攻击者代理

## 职责
专门负责 **wireless** 类别的渗透测试任务。

## 技能范围
- WiFi 监控、抓包、破解
- WPS 攻击
- 热点扫描与识别
- 握手包捕获与分析

## 配置
- API: DeepSeek Beta (专用密钥)
- 端点: https://api.deepseek.com/beta/chat/completions
- 模型: deepseek-chat / deepseek-reasoner

## 使用方式
1. 通过事件队列路由（category="wireless"）
2. 调试/应急调用: `${KALICLAW_CLI_BIN:-openclaw} agent --agent offense-wireless --message "任务"`

---

**注意**: 此代理是 6 个专业化攻击者之一，取代了通用的 `offense` 代理。正式执行路径以事件队列为准。
