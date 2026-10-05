---
name: unit-economics
description: "分析用户或公开材料中的 ARR cohorts、LTV/CAC、retention、payback、revenue quality 和 margin waterfall。"
---

# Unit Economics Analysis

生成或修改 `.xlsx`、`.pptx` 或 `.docx` 时，先读取 [`../../CODEX-EXECUTION-POLICY.md`](../../CODEX-EXECUTION-POLICY.md)。

## User-material and public-source gate

Read [`PUBLIC-SOURCE-POLICY.md`](../../PUBLIC-SOURCE-POLICY.md). Customer-level data, ARR bridges, cohorts, contract terms, and retention metrics require a user-supplied file or an opened issuer filing/IR disclosure and must be labeled accordingly. Benchmark thresholds are heuristics unless backed by a fully accessible public source; otherwise label them `MODEL_DERIVED`. Do not infer customer economics from a private database or an inaccessible benchmark report.
Resolve every concrete source from [`../../data-sources.jsonl`](../../data-sources.jsonl) (single source of truth for skill data-source routing): filter by `data_types` × `markets`; honor `policy_status`/`auth`/`cost`; fail closed when nothing matches.

## Workflow

### Step 1: Identify Business Model

Determine the revenue model to tailor the analysis:
- **SaaS / Subscription**: ARR, net retention, cohorts
- **Recurring services**: Contract value, renewal rates, upsell
- **Transaction / usage-based**: Revenue per transaction, volume trends, take rate
- **Hybrid**: Break down by revenue stream

### Step 2: Core Metrics

#### ARR / Revenue Quality
- **ARR bridge**: Beginning ARR → New → Expansion → Contraction → Churn → Ending ARR
- **ARR by cohort**: Vintage analysis — how does each annual cohort retain and grow?
- **Revenue concentration**: Top 10/20/50 customers as % of total
- **Revenue by type**: Recurring vs. non-recurring vs. professional services
- **Contract structure**: ACV distribution, multi-year %, auto-renewal %

#### Customer Economics
- **CAC (Customer Acquisition Cost)**: Total S&M spend / new customers acquired
- **LTV (Lifetime Value)**: (ARPU × Gross Margin) / Churn Rate
- **LTV:CAC ratio**: Show the calculated ratio and compare only with a sourced peer set, user target, or labeled `MODEL_DERIVED` scenario
- **CAC payback period**: Months to recover acquisition cost
- **Blended vs. segmented**: Break down by customer segment (enterprise vs. SMB vs. mid-market)

#### Retention & Expansion
- **Gross retention**: % of beginning ARR retained (excludes expansion)
- **Net retention (NDR)**: % of beginning ARR retained including expansion
- **Logo churn**: % of customers lost
- **Dollar churn**: % of revenue lost (often different from logo churn)
- **Expansion rate**: Upsell + cross-sell as % of beginning ARR

#### Cohort Analysis
Build a cohort matrix showing:

| Cohort | Year 0 | Year 1 | Year 2 | Year 3 | Year 4 |
|--------|--------|--------|--------|--------|--------|
| 2020 | $1.0M | $1.1M | $1.2M | $1.1M | |
| 2021 | $1.5M | $1.7M | $1.8M | | |
| 2022 | $2.0M | $2.3M | | | |
| 2023 | $3.0M | | | | |

Show both absolute $ and indexed (Year 0 = 100%) views.

#### Margin Waterfall
- Revenue → Gross Profit → Contribution Margin → EBITDA
- Fully loaded unit economics: what does it cost to acquire, serve, and retain a customer?
- Gross margin by revenue stream (subscription vs. services vs. other)

### Step 3: Benchmarking

Compare unit economics only to relevant, opened public benchmarks or `USER_PROVIDED` benchmarks. When neither exists, use clearly labeled `MODEL_DERIVED` scenarios rather than presenting thresholds as facts:
- **SaaS Rule of 40**: Calculate only when the user requests this named framework; label it as an analytical framework, not a company fact
- **SaaS Magic Number**: Calculate `Net new ARR / prior period S&M spend`; any target requires a source, user input, or `MODEL_DERIVED` label
- **NDR**: Show the company's disclosed result and the sourced comparison set; do not apply fixed best/good/concerning bands without evidence
- **LTV:CAC and gross retention**: Present company history and the sourced comparison distribution; no fixed best/good/concerning bands
- **CAC payback**: Best-in-class <12mo, good <18mo, concerning >24mo

### Step 4: Revenue Quality Score

Synthesize into a revenue quality assessment:

| Factor | Score (1-5) | Notes |
|--------|-------------|-------|
| Recurring % | | |
| Net retention | | |
| Customer concentration | | |
| Cohort stability | | |
| Growth durability | | |
| Margin profile | | |
| **Overall** | | |

### Step 5: Output

- Excel workbook with ARR bridge, cohort matrix, unit economics dashboard
- Summary slide with key metrics and benchmarks
- Red flags and areas for further diligence

## Important Notes

- Always ask for raw customer-level data if available — aggregate metrics can hide problems
- NDR above 100% can mask high gross churn if expansion is strong enough — always show both
- Cohort analysis is the single most important view for revenue quality — push for this data
- Differentiate between contracted ARR and actual recognized revenue
- For usage-based models, focus on consumption trends and expansion patterns rather than traditional ARR metrics
- Professional services revenue should be evaluated separately from recurring revenue; any margin comparison requires company history, public peer evidence, user input, or a `MODEL_DERIVED` scenario
