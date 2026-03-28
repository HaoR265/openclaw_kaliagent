# Kaliclaw 文档导航

**版本**: 1.0  
**最后更新**: 2026-03-28  
**用途**: 当前正式文档入口、历史材料降级入口与参考资料导航

---

## 当前正式阅读路径

如果你只想理解当前正式基线，按这个顺序读：

1. [README.md](README.md)
2. [ARCHITECTURE.md](ARCHITECTURE.md)
3. [docs/README.md](docs/README.md)
4. [CONTRIBUTING.md](CONTRIBUTING.md)
5. [CHANGELOG.md](CHANGELOG.md)

---

## 当前正式文档

| 文档 | 作用 | 说明 |
|------|------|------|
| [README.md](README.md) | 项目定位与快速开始 | Kaliclaw 的正式入口 |
| [ARCHITECTURE.md](ARCHITECTURE.md) | 当前正式架构基线 | 以已落地结构为准 |
| [CONTRIBUTING.md](CONTRIBUTING.md) | 贡献与 AI 协作规范 | 当前修改规则与身份治理规则 |
| [docs/README.md](docs/README.md) | 文档分层入口 | 区分 current / history / reference |
| [CHANGELOG.md](CHANGELOG.md) | 变更记录 | 所有正式改动都要登记 |
| [events/EVENT_PROTOCOL.md](events/EVENT_PROTOCOL.md) | 事件协议 | 任务和结果对象的底层约定 |

---

## 当前产品面与控制台

| 路径 | 作用 | 说明 |
|------|------|------|
| `dashboard-ui/` | 正式 React 控制台 | Mission / Campaign / Execution / Command / Research / Intel |
| `dashboard/` | 控制台后端与旧静态回退 | Python HTTP/API 服务 + fallback 页面 |
| `events/` | 任务内核、worker、research、knowledge | 当前最关键的后端目录 |
| `agent-kits/` | 工具目录、recipe、policy | Kali 导向的工具注册表 |

---

## 当前技术参考

| 文档或目录 | 用途 |
|------------|------|
| `agent-kits/*/catalog/*.json` | 工具目录与风险/能力分类 |
| `agent-kits/recipes/*.json` | recipe 映射 |
| `events/knowledge/` | 最小知识层实现 |
| `workspaces/*/TOOLS.md` | 各代理的工具和约束说明 |

---

## 历史与过渡期材料

以下文件已经归档到 `docs/history/`，应视为历史设计稿、阶段总结或过渡期参考，不再属于当前正式品牌入口：

- [docs/history/OpenClaw-多Agent编排与Kali工具系统重构设计.md](docs/history/OpenClaw-%E5%A4%9AAgent%E7%BC%96%E6%8E%92%E4%B8%8EKali%E5%B7%A5%E5%85%B7%E7%B3%BB%E7%BB%9F%E9%87%8D%E6%9E%84%E8%AE%BE%E8%AE%A1.md)
- [docs/history/OpenClaw-智能指挥与作战控制系统设计.md](docs/history/OpenClaw-%E6%99%BA%E8%83%BD%E6%8C%87%E6%8C%A5%E4%B8%8E%E4%BD%9C%E6%88%98%E6%8E%A7%E5%88%B6%E7%B3%BB%E7%BB%9F%E8%AE%BE%E8%AE%A1.md)
- [docs/history/OpenClaw-情报、记忆与研究分析设计.md](docs/history/OpenClaw-%E6%83%85%E6%8A%A5%E3%80%81%E8%AE%B0%E5%BF%86%E4%B8%8E%E7%A0%94%E7%A9%B6%E5%88%86%E6%9E%90%E8%AE%BE%E8%AE%A1.md)
- [docs/history/OpenClaw-专家研究平台v1设计.md](docs/history/OpenClaw-%E4%B8%93%E5%AE%B6%E7%A0%94%E7%A9%B6%E5%B9%B3%E5%8F%B0v1%E8%AE%BE%E8%AE%A1.md)
- [docs/history/OpenClaw-阶段性实力评估与发展方向总结.md](docs/history/OpenClaw-%E9%98%B6%E6%AE%B5%E6%80%A7%E5%AE%9E%E5%8A%9B%E8%AF%84%E4%BC%B0%E4%B8%8E%E5%8F%91%E5%B1%95%E6%96%B9%E5%90%91%E6%80%BB%E7%BB%93.md)
- [docs/history/OpenClaw-务实推进路线图.md](docs/history/OpenClaw-%E5%8A%A1%E5%AE%9E%E6%8E%A8%E8%BF%9B%E8%B7%AF%E7%BA%BF%E5%9B%BE.md)
- [docs/history/OpenClaw-C方案-事件驱动任务队列-详细实施计划.md](docs/history/OpenClaw-C%E6%96%B9%E6%A1%88-%E4%BA%8B%E4%BB%B6%E9%A9%B1%E5%8A%A8%E4%BB%BB%E5%8A%A1%E9%98%9F%E5%88%97-%E8%AF%A6%E7%BB%86%E5%AE%9E%E6%96%BD%E8%AE%A1%E5%88%92.md)
- [docs/history/OpenClaw-C方案-事件驱动任务队列-总结报告.md](docs/history/OpenClaw-C%E6%96%B9%E6%A1%88-%E4%BA%8B%E4%BB%B6%E9%A9%B1%E5%8A%A8%E4%BB%BB%E5%8A%A1%E9%98%9F%E5%88%97-%E6%80%BB%E7%BB%93%E6%8A%A5%E5%91%8A.md)
- [docs/history/OpenClaw-Kali工具目录系统-介绍文档.md](docs/history/OpenClaw-Kali%E5%B7%A5%E5%85%B7%E7%9B%AE%E5%BD%95%E7%B3%BB%E7%BB%9F-%E4%BB%8B%E7%BB%8D%E6%96%87%E6%A1%A3.md)

当前权威入口请继续以本文件、`README.md`、`ARCHITECTURE.md` 和 `docs/README.md` 为准。

---

## 兼容层说明

当前仍存在这些兼容默认值：

- CLI 默认名：`openclaw`
- 默认根目录：`~/.openclaw`
- 默认配置名：`openclaw.json`

它们属于兼容层，不代表 Kaliclaw 的正式品牌命名。  
当前已经开始通过环境变量和 fallback 的方式逐步参数化：

- `KALICLAW_ROOT`
- `KALICLAW_CLI_BIN`
- `KALICLAW_CONFIG_BASENAME`
- `KALICLAW_SOURCE_CONFIG_BASENAME`
- `KALICLAW_RUNTIME_DIR`
- `KALICLAW_DB_PATH`
- `KALICLAW_DB_BASENAME`
- `KALICLAW_KNOWLEDGE_DB_PATH`
- `KALICLAW_KNOWLEDGE_DB_BASENAME`

推荐先参考：

- [kaliclaw.env.example](kaliclaw.env.example)

---

## 常用操作

### 状态检查

```bash
openclaw gateway status
cd ~/.openclaw/events && python3 status.py
```

### 启动控制台

```bash
cd ~/.openclaw && python3 dashboard/server.py --host 127.0.0.1 --port 8787
```

### 前端开发模式

```bash
cd ~/.openclaw/dashboard-ui && npm run dev -- --host 127.0.0.1 --port 5173
```

### 构建前端

```bash
cd ~/.openclaw/dashboard-ui && npm run build
```

### 规范化当前兼容配置

```bash
source ./kaliclaw.env.example
cd ~/.openclaw && python3 update_workspaces.py

# 从兼容配置名生成新的 Kaliclaw 配置文件
KALICLAW_SOURCE_CONFIG_BASENAME=openclaw.json \
KALICLAW_CONFIG_BASENAME=kaliclaw.json \
python3 update_workspaces.py
```

该脚本会基于当前 `KALICLAW_ROOT`、`KALICLAW_SOURCE_CONFIG_BASENAME` 与 `KALICLAW_CONFIG_BASENAME` 读取旧配置并写出目标配置，同时修正：

- agent `workspace`
- agent `agentDir`
- `tools.exec.pathPrepend`

---

## 外部参考

当前只保留事实性入口：

- 本地已安装 upstream `openclaw` 包文档目录：`/home/asus/.npm-global/lib/node_modules/openclaw/docs/`
- upstream 仓库：`https://github.com/openclaw/openclaw`

这些内容应被视为上游参考，而不是当前 Kaliclaw 的正式文档入口。
