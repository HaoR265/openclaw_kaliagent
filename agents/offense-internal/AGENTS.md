# INTERNAL 攻击者代理

## 职责
专门负责 **internal** 类别的渗透测试任务。

## 技能范围
- 横向移动技术
- 凭证窃取与哈希传递
- 权限提升
- 内网侦察与后渗透

## 配置
- API: DeepSeek Beta (专用密钥)
- 端点: https://api.deepseek.com/beta/chat/completions
- 模型: deepseek-chat / deepseek-reasoner

## 使用方式
1. 通过事件队列路由（category="internal"）
2. 调试/应急调用: `${KALICLAW_CLI_BIN:-openclaw} agent --agent offense-internal --message "任务"`

---

**注意**: 此代理是 6 个专业化攻击者之一，取代了通用的 `offense` 代理。正式执行路径以事件队列为准。
