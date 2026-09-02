---
name: pitch-deck
description: "把用户提供的 PowerPoint 模板与 Excel/CSV/文档数据填入投资银行 pitch deck；适用于填充或更新既有模板，不用于无模板的新建演示。"
---

# Pitch Deck Template Population

在用户提供的模板中填充内容，保留母版、布局、品牌和既有结构。没有模板的新建演示应使用通用 Presentations capability，而不是本 skill。

## 必读契约

- 处理用户资料和公开补充来源前读取 [`../../PUBLIC-SOURCE-POLICY.md`](../../PUBLIC-SOURCE-POLICY.md)。
- 创建或修改 `.pptx` 前读取 [`../../CODEX-EXECUTION-POLICY.md`](../../CODEX-EXECUTION-POLICY.md)。
- 需要文本、表格、图表和对齐规则时读取 [`reference/formatting-standards.md`](reference/formatting-standards.md)。
- 遇到特定 slide 类型时读取 [`reference/slide-templates.md`](reference/slide-templates.md) 的对应部分。
- 需要核验 CAGR、份额、倍数或桥接计算时读取 [`reference/calculation-standards.md`](reference/calculation-standards.md)。
- 只有原生 capability 无法保留模板元素且确需 OOXML 级修改时读取 [`reference/xml-reference.md`](reference/xml-reference.md)。

## 输入边界

模板、source files、slide mapping 和交易材料必须由用户提供；公开补充事实需已打开并记录来源。缺少的私有交易/客户/预测信息保持 `SOURCE_UNAVAILABLE`。所有经验参数必须有公开来源、用户输入或 `MODEL_DERIVED` 标记。

## 工作流

1. **复制模板并盘点**：识别 master、layouts、占位符、现有 shapes、页脚、来源区和受保护元素；输出副本。
2. **建立 mapping**：把每个 source range/字段映射到 slide 和 shape；确认期间、单位、舍入、币种和口径。可以合理推断时连续执行；仅关键映射歧义才暂停。
3. **填充内容**：遵循现有布局和品牌；优先更新占位符而非重建 slide。来源数字按提供口径使用，派生数字显示公式/说明。
4. **财务核验**：核对 CAGR、总分、bridge、倍数、时期和跨页重复数字；叙事不得超出源材料。
5. **视觉与结构 QC**：检查 overflow、重叠、裁切、字体替换、对齐、页码、来源和 master 继承。能完整渲染时逐页检查；否则按统一契约受限交付。

## 完成条件

- 用户模板及原文件保留；每个修改 slide 可追踪到 source mapping。
- 关键数字、单位和叙事跨页一致；没有空占位符或无来源财务事实。
- Artifact 结构有效；未完整逐页渲染时披露 `FULL_RENDER_UNVERIFIED`。
