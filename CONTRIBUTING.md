# Kaliclaw 贡献与 AI 协作规范

**版本**: 1.0  
**最后更新**: 2026-03-28  
**目标读者**: AI 代码助手、开发者、维护者

---

## 1. 文档目的

这份文档定义 Kaliclaw 当前的协作规则、身份治理规则和最低修改要求。

它的重点不是解释所有历史实现，而是确保：

- 新改动不再继续把 OpenClaw 当作正式品牌
- 品牌层、归因层、兼容层、历史层分开处理
- AI 修改可回退、可验证、可追溯

---

## 2. 当前项目身份

Kaliclaw 是独立维护项目。  
OpenClaw 在当前仓库里只应出现在以下位置：

- 上游参考说明
- 兼容层默认值
- 历史文档或历史路径

禁止继续把仓库描述为：

- “OpenClaw 魔改版”
- “OpenClaw 的 C 方案”
- “本质上仍是 OpenClaw”

---

## 3. 修改前先分类

任何涉及 `OpenClaw / openclaw / ~/.openclaw / openclaw.json` 的改动，都必须先分类：

### 品牌层

例如：

- README 标题
- UI 品牌标题
- 服务启动输出
- 页面说明文案

处理方式：

- 直接改为 `Kaliclaw`
- 同时把语气改成独立项目叙事

### 归因层

例如：

- 项目来源说明
- 对上游的感谢或参考说明

处理方式：

- 保留事实
- 改写为“早期参考 / inspired by / upstream reference”
- 不允许继续使用“魔改版”叙述

### 兼容层

例如：

- `openclaw` CLI
- `~/.openclaw`
- `openclaw.json`
- 旧数据库名或旧路径默认值

处理方式：

- 优先参数化
- 保留 fallback
- 在注释里明确这是兼容层，不是正式品牌层

### 历史层

例如：

- `OpenClaw-*.md`
- 阶段计划
- 阶段总结
- 旧过渡期说明

处理方式：

- 迁移到 `docs/history/`
- 或在当前阶段至少降级为“历史材料”

---

## 4. 禁止事项

明确禁止：

1. 全仓粗暴替换 `OpenClaw -> Kaliclaw`
2. 在未分析语义前直接改 `openclaw` CLI 或根目录
3. 在新代码、新页面、新提示词里继续引入 OpenClaw 作为正式品牌
4. 不修链接就移动文档
5. 删除历史文档内容而不归档
6. 未核实事实就重写许可证说明

---

## 5. 当前仓库结构理解

当前应优先理解这些目录：

```text
.
├── events/            # 任务内核、worker、research、knowledge
├── dashboard/         # 控制台后端与旧静态回退
├── dashboard-ui/      # 正式 React 控制台
├── agent-kits/        # catalog / recipe / policy
├── agents/            # 代理配置
├── workspaces/        # 工作空间、工具指南、身份说明
├── README.md
├── ARCHITECTURE.md
├── DOCUMENTATION.md
├── CHANGELOG.md
└── docs/
```

当前正式默认值已经是：

- CLI：`kaliclaw`
- 根目录：`~/.kaliclaw`
- 配置文件：`kaliclaw.json`
- 主数据库：`kaliclaw.db`

以下内容只保留为兼容 fallback：

- `openclaw`
- `~/.openclaw`
- `openclaw.json`
- `openclaw.db`

---

## 6. 正式修改顺序

默认按这个顺序做：

1. 审计问题
2. 分类问题
3. 做最小必要改动
4. 跑验证
5. 更新文档
6. 更新 `CHANGELOG.md`
7. 再做残留扫描

---

## 7. 代码修改要求

### Python

- 保持现有模块边界
- 默认增量修改，不做无授权大重构
- 有风险的改动必须先做最小复验
- 不要为了“更优雅”破坏当前兼容链

### 前端

- 保持正式 React 控制台为主
- 旧 `dashboard/` 只作为回退页
- 新页面、新空状态、新品牌文案必须统一到 Kaliclaw

### 文档

- 正式入口文档使用相对路径
- 不要在正式索引里继续把历史稿放成主入口
- 历史文档内容保留，但要降级说明

---

## 8. 测试与验证

最低要求：

```bash
python3 -m py_compile <相关后端文件>
cd dashboard-ui && npm run build
```

涉及主链时，至少再做一条本地冒烟，例如：

- `Mission -> Revision -> Launch -> Workflow`
- `Campaign create / control`
- `Research session -> hypothesis -> experiment -> launch`

---

## 9. 文档同步要求

以下改动必须同步更新文档：

- 正式品牌变化
- 架构入口变化
- 新页面 / 新 API / 新工作流
- 历史文档归档
- 兼容层迁移策略

所有正式改动必须更新：

- [CHANGELOG.md](CHANGELOG.md)

必要时同步更新：

- [README.md](README.md)
- [DOCUMENTATION.md](DOCUMENTATION.md)
- [docs/README.md](docs/README.md)
- [ARCHITECTURE.md](ARCHITECTURE.md)

---

## 10. AI 协作要求

AI 修改每轮都应明确：

1. 本轮目标
2. 涉及文件
3. 修改属于哪一类
4. 风险
5. 回滚方式

修改后必须说明：

1. 实际修改文件
2. 验证结果
3. 仍未处理残留
4. 下一轮建议

---

## 11. 当前优先级

当前更值钱的方向：

1. Kaliclaw 独立化与正式入口重写
2. 历史文档归档
3. 兼容层参数化
4. research plane 与 knowledge plane 补完
5. 控制面和执行面继续加固

当前不值得优先做的方向：

1. 为了设计而设计的复杂抽象
2. 过早大规模目录迁移但不修链接
3. 不带回退的 CLI / 根路径硬切
4. 只改表面名字、不改身份叙述
