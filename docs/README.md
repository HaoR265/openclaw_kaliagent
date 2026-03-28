# Kaliclaw 文档分层

这份索引只做一件事：把当前仓库里的文档分成 `current / history / reference` 三层，避免旧材料继续和正式入口混在一起。

---

## 1. Current

这些文件代表当前正式入口：

1. [../README.md](../README.md)
2. [../ARCHITECTURE.md](../ARCHITECTURE.md)
3. [../DOCUMENTATION.md](../DOCUMENTATION.md)
4. [../CONTRIBUTING.md](../CONTRIBUTING.md)
5. [../CHANGELOG.md](../CHANGELOG.md)
6. [../events/EVENT_PROTOCOL.md](../events/EVENT_PROTOCOL.md)

---

## 2. History

以下文件已归档到 `docs/history/`：

- [history/OpenClaw-多Agent编排与Kali工具系统重构设计.md](history/OpenClaw-%E5%A4%9AAgent%E7%BC%96%E6%8E%92%E4%B8%8EKali%E5%B7%A5%E5%85%B7%E7%B3%BB%E7%BB%9F%E9%87%8D%E6%9E%84%E8%AE%BE%E8%AE%A1.md)
- [history/OpenClaw-智能指挥与作战控制系统设计.md](history/OpenClaw-%E6%99%BA%E8%83%BD%E6%8C%87%E6%8C%A5%E4%B8%8E%E4%BD%9C%E6%88%98%E6%8E%A7%E5%88%B6%E7%B3%BB%E7%BB%9F%E8%AE%BE%E8%AE%A1.md)
- [history/OpenClaw-情报、记忆与研究分析设计.md](history/OpenClaw-%E6%83%85%E6%8A%A5%E3%80%81%E8%AE%B0%E5%BF%86%E4%B8%8E%E7%A0%94%E7%A9%B6%E5%88%86%E6%9E%90%E8%AE%BE%E8%AE%A1.md)
- [history/OpenClaw-专家研究平台v1设计.md](history/OpenClaw-%E4%B8%93%E5%AE%B6%E7%A0%94%E7%A9%B6%E5%B9%B3%E5%8F%B0v1%E8%AE%BE%E8%AE%A1.md)
- [history/OpenClaw-阶段性实力评估与发展方向总结.md](history/OpenClaw-%E9%98%B6%E6%AE%B5%E6%80%A7%E5%AE%9E%E5%8A%9B%E8%AF%84%E4%BC%B0%E4%B8%8E%E5%8F%91%E5%B1%95%E6%96%B9%E5%90%91%E6%80%BB%E7%BB%93.md)
- [history/OpenClaw-务实推进路线图.md](history/OpenClaw-%E5%8A%A1%E5%AE%9E%E6%8E%A8%E8%BF%9B%E8%B7%AF%E7%BA%BF%E5%9B%BE.md)
- [history/OpenClaw-C方案-事件驱动任务队列-详细实施计划.md](history/OpenClaw-C%E6%96%B9%E6%A1%88-%E4%BA%8B%E4%BB%B6%E9%A9%B1%E5%8A%A8%E4%BB%BB%E5%8A%A1%E9%98%9F%E5%88%97-%E8%AF%A6%E7%BB%86%E5%AE%9E%E6%96%BD%E8%AE%A1%E5%88%92.md)
- [history/OpenClaw-C方案-事件驱动任务队列-总结报告.md](history/OpenClaw-C%E6%96%B9%E6%A1%88-%E4%BA%8B%E4%BB%B6%E9%A9%B1%E5%8A%A8%E4%BB%BB%E5%8A%A1%E9%98%9F%E5%88%97-%E6%80%BB%E7%BB%93%E6%8A%A5%E5%91%8A.md)
- [history/OpenClaw-Kali工具目录系统-介绍文档.md](history/OpenClaw-Kali%E5%B7%A5%E5%85%B7%E7%9B%AE%E5%BD%95%E7%B3%BB%E7%BB%9F-%E4%BB%8B%E7%BB%8D%E6%96%87%E6%A1%A3.md)

统一的历史归档说明见 [history/README.md](history/README.md)。

---

## 3. Reference

以下内容属于参考层，而不是正式入口：

- [reference/migrate-from-openclaw.md](reference/migrate-from-openclaw.md)
- [reference/final-cutover-rollback.md](reference/final-cutover-rollback.md)
- upstream `openclaw` 本地安装文档
- 工具目录 JSON 与 recipe/policy 文件
- workspaces 下的工具与身份文档

---

## 4. 当前推荐阅读路径

如果是第一次接手当前仓库，按这个顺序读：

1. [../README.md](../README.md)
2. [../ARCHITECTURE.md](../ARCHITECTURE.md)
3. [../DOCUMENTATION.md](../DOCUMENTATION.md)
4. [../CONTRIBUTING.md](../CONTRIBUTING.md)
5. 历史或过渡材料按需查阅

---

## 5. 当前不做的事

这轮不继续做更深的历史文档重命名，只维持“正式入口 + 历史归档 + 参考迁移文档”三层结构。原因很简单：

1. 历史文档已经归档完成
2. 继续大规模改名会放大引用修复成本
3. 当前更值得做的是默认值翻转后的迁移链、回滚链和兼容入口收口
