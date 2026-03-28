# OpenClaw 文档分层

这份索引用来解决当前文档都堆在根目录、阅读路径不清的问题。

当前阶段不做大规模移动，原因是很多现有文档和 `CHANGELOG` 已经互相引用。  
现阶段先做两件更稳的事：

1. 明确文档分层
2. 明确“半成品版本”应该看哪几份

---

## 1. 当前正式入口

这些文件仍然是当前阶段的正式入口：

1. [README.md](/home/asus/.openclaw/README.md)
2. [ARCHITECTURE.md](/home/asus/.openclaw/ARCHITECTURE.md)
3. [DOCUMENTATION.md](/home/asus/.openclaw/DOCUMENTATION.md)
4. [CHANGELOG.md](/home/asus/.openclaw/CHANGELOG.md)

---

## 2. 四条主设计线

### 2.1 编排与执行底座

- [OpenClaw-多Agent编排与Kali工具系统重构设计.md](/home/asus/.openclaw/OpenClaw-%E5%A4%9AAgent%E7%BC%96%E6%8E%92%E4%B8%8EKali%E5%B7%A5%E5%85%B7%E7%B3%BB%E7%BB%9F%E9%87%8D%E6%9E%84%E8%AE%BE%E8%AE%A1.md)
- [OpenClaw-C方案-事件驱动任务队列-详细实施计划.md](/home/asus/.openclaw/OpenClaw-C%E6%96%B9%E6%A1%88-%E4%BA%8B%E4%BB%B6%E9%A9%B1%E5%8A%A8%E4%BB%BB%E5%8A%A1%E9%98%9F%E5%88%97-%E8%AF%A6%E7%BB%86%E5%AE%9E%E6%96%BD%E8%AE%A1%E5%88%92.md)
- [OpenClaw-C方案-事件驱动任务队列-总结报告.md](/home/asus/.openclaw/OpenClaw-C%E6%96%B9%E6%A1%88-%E4%BA%8B%E4%BB%B6%E9%A9%B1%E5%8A%A8%E4%BB%BB%E5%8A%A1%E9%98%9F%E5%88%97-%E6%80%BB%E7%BB%93%E6%8A%A5%E5%91%8A.md)

### 2.2 指挥与作战控制

- [OpenClaw-智能指挥与作战控制系统设计.md](/home/asus/.openclaw/OpenClaw-%E6%99%BA%E8%83%BD%E6%8C%87%E6%8C%A5%E4%B8%8E%E4%BD%9C%E6%88%98%E6%8E%A7%E5%88%B6%E7%B3%BB%E7%BB%9F%E8%AE%BE%E8%AE%A1.md)

### 2.3 情报、记忆与研究分析

- [OpenClaw-情报、记忆与研究分析设计.md](/home/asus/.openclaw/OpenClaw-%E6%83%85%E6%8A%A5%E3%80%81%E8%AE%B0%E5%BF%86%E4%B8%8E%E7%A0%94%E7%A9%B6%E5%88%86%E6%9E%90%E8%AE%BE%E8%AE%A1.md)

### 2.4 工具目录系统

- [OpenClaw-Kali工具目录系统-介绍文档.md](/home/asus/.openclaw/OpenClaw-Kali%E5%B7%A5%E5%85%B7%E7%9B%AE%E5%BD%95%E7%B3%BB%E7%BB%9F-%E4%BB%8B%E7%BB%8D%E6%96%87%E6%A1%A3.md)

---

## 3. 当前半成品版本建议阅读集

如果目的是对外有限范围展示当前半成品，建议优先放这几份：

1. [README.md](/home/asus/.openclaw/README.md)
2. [ARCHITECTURE.md](/home/asus/.openclaw/ARCHITECTURE.md)
3. [OpenClaw-阶段性实力评估与发展方向总结.md](/home/asus/.openclaw/OpenClaw-%E9%98%B6%E6%AE%B5%E6%80%A7%E5%AE%9E%E5%8A%9B%E8%AF%84%E4%BC%B0%E4%B8%8E%E5%8F%91%E5%B1%95%E6%96%B9%E5%90%91%E6%80%BB%E7%BB%93.md)
4. [OpenClaw-多Agent编排与Kali工具系统重构设计.md](/home/asus/.openclaw/OpenClaw-%E5%A4%9AAgent%E7%BC%96%E6%8E%92%E4%B8%8EKali%E5%B7%A5%E5%85%B7%E7%B3%BB%E7%BB%9F%E9%87%8D%E6%9E%84%E8%AE%BE%E8%AE%A1.md)
5. [OpenClaw-智能指挥与作战控制系统设计.md](/home/asus/.openclaw/OpenClaw-%E6%99%BA%E8%83%BD%E6%8C%87%E6%8C%A5%E4%B8%8E%E4%BD%9C%E6%88%98%E6%8E%A7%E5%88%B6%E7%B3%BB%E7%BB%9F%E8%AE%BE%E8%AE%A1.md)
6. [OpenClaw-情报、记忆与研究分析设计.md](/home/asus/.openclaw/OpenClaw-%E6%83%85%E6%8A%A5%E3%80%81%E8%AE%B0%E5%BF%86%E4%B8%8E%E7%A0%94%E7%A9%B6%E5%88%86%E6%9E%90%E8%AE%BE%E8%AE%A1.md)

---

## 4. 当前不急着做的整理

以下问题已经确认存在，但当前先不做大迁移：

1. 设计文档仍在根目录，没有全部移动到 `docs/design/`
2. 历史总结与现行设计文档混放
3. 旧兼容文档和新阶段文档并存

原因不是这些没问题，而是：

1. 当前更重要的是保持链接稳定
2. 当前更重要的是把系统做成可发布半成品
3. 等目录和公开边界稳定后，再做一次文档迁移更划算
