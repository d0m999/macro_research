---
name: earnings-preview
description: "在财报发布前建立指标清单、公开 guidance 基线和 bull/base/bear 情景。用于财报前瞻、业绩预览、earnings preview 或财报关注点请求。"
---

# Earnings Preview

生成或修改 `.docx`、`.xlsx` 或 `.pptx` 时，先读取 [`../../CODEX-EXECUTION-POLICY.md`](../../CODEX-EXECUTION-POLICY.md)。

**Public-source gate:** Read [`../../PUBLIC-SOURCE-POLICY.md`](../../PUBLIC-SOURCE-POLICY.md) first. Use the issuer's official calendar, prior earnings materials and dated guidance. Do not invent external estimates, survey figures or option inputs.
Resolve every concrete source from [`../../data-sources.jsonl`](../../data-sources.jsonl) (single source of truth for skill data-source routing): filter by `data_types` × `markets`; honor `policy_status`/`auth`/`cost`; fail closed when nothing matches.

## Workflow

### Step 1: Gather Context

- Identify the company and reporting quarter
- Collect the latest public company guidance and the prior version of the user's model, if supplied; label missing comparison inputs `SOURCE_UNAVAILABLE`
- Find the earnings date and time (pre-market vs. after-hours)
- Review the company's prior quarter earnings call for any guidance or commentary

### Step 2: Key Metrics Framework

Build a "what to watch" framework specific to the company:

**Financial Metrics:**
- Revenue vs. public company guidance or `USER_PROVIDED` estimate (total and by segment)
- EPS vs. public company guidance or `USER_PROVIDED` estimate
- Margins (gross, operating, net) — expanding or contracting?
- Free cash flow
- Forward guidance vs. the prior dated public guidance or our `MODEL_DERIVED` scenario

**Operational Metrics** (sector-specific):
- Tech/SaaS: ARR, net retention, RPO, customer count
- Retail: Same-store sales, traffic, basket size
- Industrials: Backlog, book-to-bill, price vs. volume
- Financials: NIM, credit quality, loan growth, fee income
- Healthcare: Scripts, patient volumes, pipeline updates

### Step 3: Scenario Analysis

Build 3 scenarios with stock price implications:

| Scenario | Revenue | EPS | Key Driver | Stock Reaction |
|----------|---------|-----|------------|----------------|
| Bull | | | | |
| Base | | | | |
| Bear | | | | |

For each scenario:
- What would need to happen operationally
- What management commentary would signal this
- Historical context — how has the stock moved on similar prints?

### Step 4: Catalyst Checklist

Identify the 3-5 things that will determine the stock's reaction:

1. [Metric] vs. [dated public guidance or prior model; otherwise `SOURCE_UNAVAILABLE`] — why it matters
2. [Guidance item] — what the buy-side expects to hear
3. [Narrative shift] — any strategic changes, M&A, restructuring

### Step 5: Output

One-page earnings preview with:
- Company, quarter, earnings date
- Public guidance and internal scenario table, with `SOURCE_UNAVAILABLE` for missing comparisons
- Key metrics to watch (ranked by importance)
- Bull/base/bear scenario table
- Catalyst checklist
- Trading setup: recent stock performance, implied move from options

## Important Notes

- Public guidance changes — always note the source and date
- Do not use survey figures without a user-provided, dated source
- Historical earnings reactions help calibrate expectations (search for "[company] earnings reaction history")
- Options-implied move is optional; use only a validated public quote/page or `USER_PROVIDED` option data, otherwise mark it `SOURCE_UNAVAILABLE`
