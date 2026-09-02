---
name: comps-analysis
description: "建立上市公司可比分析、经营指标与估值倍数表，并计算统计区间和隐含估值。用于 comps、可比公司分析、同业估值、trading comparables 等请求。"
---

# Comparable Company Analysis

输出可审计的上市公司 comps workbook：原始事实、派生 EV/倍数、统计摘要和目标公司隐含估值均保持可追踪。

## 必读契约

- 收集输入前读取 [`../../PUBLIC-SOURCE-POLICY.md`](../../PUBLIC-SOURCE-POLICY.md)。
- 创建或修改 `.xlsx` 前读取 [`../../CODEX-EXECUTION-POLICY.md`](../../CODEX-EXECUTION-POLICY.md)。
- 构建 peer set 和口径时读取 [`references/peer-selection.md`](references/peer-selection.md)。
- 编写 workbook 公式时读取 [`references/formulas.md`](references/formulas.md)。
- 用户未提供模板时读取 [`references/workbook-layout.md`](references/workbook-layout.md)。

## 工作流

1. **定义估值时点与口径**：确认目标、估值日期、币种、LTM/NTM、GAAP/adjusted、enterprise/equity metrics 和受众。
2. **选择 peers**：按商业模式、客户、地域、规模、增长、利润率和资本强度建立候选集合；记录每家公司纳入/排除理由。不要为了凑数量放宽核心可比性。
3. **收集事实**：财务 actuals 来自 filings/IR；价格来自当次实际验证的公开页面或 `USER_PROVIDED` 导出；share count、debt、cash 和其他 EV adjustments 回链官方披露。Forward 指标没有公开 guidance 或用户输入时保持 `SOURCE_UNAVAILABLE`。
4. **标准化**：统一币种、期间、单位和非经常项目；所有调整保留原值、调整值、公式和说明。
5. **计算**：用 workbook 公式计算 market cap、EV、经营指标、倍数、分位数和隐含估值。统计结果不替代可比性判断；异常值保留并说明是否排除。
6. **敏感性与结论**：倍数区间必须来自本次 peer 数据、用户输入或明确 `MODEL_DERIVED` 情景，不采用无来源经验区间。
7. **验证与交付**：检查期间、单位、公式、EV bridge、中心统计、异常值处理、目标公司映射和来源注释；运行统一 artifact 验证器。

## 完成条件

- 每个硬编码事实有 source record；每个派生值是可追踪公式；缺失 forward/市场输入未被猜测补齐。
- peer 选择、口径调整和异常值处理有明确理由；隐含估值可从源数据重算。
- 统一验证器返回 `pass` 或 `pass_with_limitations`，并按契约披露公式求值限制。
