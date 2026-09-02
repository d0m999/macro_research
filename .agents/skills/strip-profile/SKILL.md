---
name: strip-profile
description: "制作 1–4 页投资银行公司 strip profile，整合业务概览、关键财务、股东/交易信息、估值和来源。用于 company profile 或 strip。"
---

# Strip Profile

制作信息密集但可核验的公司 profile。用户指定单页或多页时遵循其要求；未指定时按可用数据和用途选择最小充分结构，不因版式选择强制暂停。

## 必读契约

- 研究前读取 [`../../PUBLIC-SOURCE-POLICY.md`](../../PUBLIC-SOURCE-POLICY.md)。
- 创建或修改 `.pptx` 前读取 [`../../CODEX-EXECUTION-POLICY.md`](../../CODEX-EXECUTION-POLICY.md)。
- 有用户模板时复制并保持 master/layout；没有模板时使用当前 Presentations capability 的合理默认版式。
- 用户没有模板或需要选择模块布局时读取 [`references/layouts.md`](references/layouts.md)。

## 工作流

1. **定义 profile**：确认公司、估值日期、受众、单页/多页、必须模块和币种/单位。
2. **收集公开事实**：使用 filing、IR、公司官网和官方公告；市场价格需当次验证。Forward、私营公司、所有权或交易事实不可获得时标 `SOURCE_UNAVAILABLE`。
3. **选择模块**：业务概览、产品/地区、关键 KPI、历史财务、资本结构、股东、交易、估值、管理层或时间线仅在数据和用途支持时加入。
4. **计算**：增长、margin、EV 和 multiples 由可追踪输入计算；预测或估值区间只来自用户输入、公开同业事实或 `MODEL_DERIVED` 情景。
5. **组版**：每页一条清晰 takeaway；图表、表格和文字保持层级与可读性，所有数字注明日期、单位和来源。
6. **QC**：核对跨模块数字、期间、舍入、source footnotes、裁切和重叠；运行统一 artifact 验证。

## 完成条件

- 事实、用户输入、派生值和缺失项状态清晰；不存在把经验区间写成公司事实的内容。
- 页面结构完整，关键数字一致，source footnotes 可定位。
- 未完整逐页渲染时披露 `FULL_RENDER_UNVERIFIED`。
