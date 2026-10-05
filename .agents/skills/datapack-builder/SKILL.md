---
name: datapack-builder
description: "把公开 filing、发行人材料和用户提供的文件抽取、标准化为带来源审计的金融 data pack workbook。用于尽调、IC 或组合报告数据包。"
---

# Datapack Builder

建立可复核的金融 data pack；它是标准化事实和计算的工作底稿，不是缺失数据的推测补全器。

## 必读契约

- 收集或映射数据前读取 [`../../PUBLIC-SOURCE-POLICY.md`](../../PUBLIC-SOURCE-POLICY.md)。
- 具体数据源路由以 [`../../data-sources.jsonl`](../../data-sources.jsonl) 为准（本项目 skill 数据源路由的单一事实来源）：按 `data_types` × `markets` 过滤，经 `policy_status`/`auth`/`cost` 校验；无匹配时 fail-closed。
- 创建或修改 `.xlsx` 前读取 [`../../CODEX-EXECUTION-POLICY.md`](../../CODEX-EXECUTION-POLICY.md)。
- 设计字段和审计表时读取 [`references/datapack-schema.md`](references/datapack-schema.md)。
- 发生期间、币种、会计口径或 entity 映射时读取 [`references/normalization.md`](references/normalization.md)。

## 工作流

1. **定义 data contract**：列出实体、期间、币种、单位、指标、来源状态、输出 tabs 和更新时点。只有关键字段无法推断时请求用户选择。
2. **建立 source manifest**：公开事实使用已打开的 filing/发行人/政府/监管页面；用户文件标 `USER_PROVIDED`。为每个来源记录标题、URL/路径、发布日期、访问日期、期间和定位。
3. **抽取原始数据**：保留 reported label、原值、单位、期间和来源定位；不直接覆盖原始层。
4. **标准化**：在独立层映射统一科目、币种、符号和期间；每项 adjustment 记录方法。无法可靠映射时使用 `SOURCE_UNAVAILABLE`。
5. **计算与呈现**：派生 KPI、bridge、同比/环比和摘要使用公式；需要的假设必须来自用户或标为 `MODEL_DERIVED`。
6. **质量控制**：检查重复、缺口、单位、期间、总分关系、资产负债或现金勾稽、跨 tab 链接和来源覆盖。
7. **受限交付**：默认输出副本；运行统一 artifact 验证器并报告限制。

## 完成条件

- Raw、Normalized、Calculations、Summary 和 Sources 的职责分开，或用户模板中有等价可追踪结构。
- 每个数据点保留事实/用户输入/模型推导/缺失状态；没有隐含私有来源。
- 所有金融经验参数带来源、用户输入或 `MODEL_DERIVED` 标记；未求值公式按契约披露。
