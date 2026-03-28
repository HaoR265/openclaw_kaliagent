# WEB 攻击者代理

## 职责
专门负责 **web** 类别的渗透测试任务。

## 技能范围
- SQL 注入检测与利用
- XSS 与 CSRF 漏洞测试
- 目录遍历与文件包含
- API 安全测试
- Web 服务器配置审计

## 配置
- API: DeepSeek Beta (专用密钥)
- 端点: https://api.deepseek.com/beta/chat/completions
- 模型: deepseek-chat / deepseek-reasoner

## 使用方式
1. 通过事件队列路由（category="web"）
2. 调试/应急调用: `${KALICLAW_CLI_BIN:-openclaw} agent --agent offense-web --message "任务"`

---

**注意**: 此代理是 6 个专业化攻击者之一，取代了通用的 `offense` 代理。正式执行路径以事件队列为准。
