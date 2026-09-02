---
name: deck-refresh
description: "在既有 presentation 中刷新季度数据、财报、comps 或市场数字，并核对跨页一致性。"
---

# Deck Refresh

更新既有 deck 中的数字并保持模板、叙事和格式。修改 `.pptx` 前读取 [`../../CODEX-EXECUTION-POLICY.md`](../../CODEX-EXECUTION-POLICY.md)，默认保留原 deck 并输出副本。

## 输入边界

只使用用户提供的 deck、mapping 和 source files。缺失 replacement value 时标 `SOURCE_UNAVAILABLE`，不主动从未授权来源补数。

## 工作流

1. **读取 mapping**：识别 old/new value、metric、period、unit、currency、source 和 derived-number rule。用户提供的 mapping 足够明确时直接继续；只有同一数字可能映射到不同 metric 或 derived values 是否重算会实质改变结果时才请求选择。
2. **扫描全 deck**：定位 text、tables、charts、chart source data、footnotes、sources 和 speaker notes 中的所有表示变体。记录 slide、shape、原文本、目标文本和 derivation。
3. **内部核验 change set**：检查每项映射的 metric、period、unit 和语境；识别受影响的 growth、margin、share、bridge、headline 和 narrative。用户授权完整刷新时连续执行。
4. **最小修改副本**：更新目标 text run、cell 或 chart series，保留 font、size、color、layout、master 和不相关内容。Derived values 只有在规则明确且输入完整时重算；否则保持不变并 flag。
5. **一致性与视觉 QC**：核对跨页重复数字、total、growth、margin、source、period 和 narrative；检查 overflow、overlap、cropping、axis 和 source lines。
6. **报告**：列出 changed、derived、flagged/unmodified 项和验证限制。

## 完成条件

- 原 deck 保留；输出副本和每个修改位置可追踪。
- 所有目标实例已处理，关键数字和叙事跨页一致；不确定的二阶影响没有被静默修改。
- Artifact 结构有效；未完整逐页渲染时披露 `FULL_RENDER_UNVERIFIED`。
