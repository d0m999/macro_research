---
name: returns-analysis
description: "用用户或公开来源输入建立 PE IRR/MOIC 回报分析与 entry、leverage、exit、growth、hold period 敏感性。"
---

# Returns Analysis

生成或修改 `.xlsx`、`.pptx` 或 `.docx` 时，先读取 [`../../CODEX-EXECUTION-POLICY.md`](../../CODEX-EXECUTION-POLICY.md)。

## Public-source and user-input gate

Read [`../../PUBLIC-SOURCE-POLICY.md`](../../PUBLIC-SOURCE-POLICY.md). Entry financials, debt, fees, and deal terms must come from opened filings/official transaction documents or be labeled `USER_PROVIDED`; price and market inputs require a validated public page or user export. Growth, exit multiples, and leverage cases are assumptions and must be labeled `MODEL_DERIVED`. Missing inputs are `SOURCE_UNAVAILABLE`; do not fill them with private databases or unverified market estimates.

## Workflow

### Step 1: Gather Deal Inputs

Ask for (or extract from prior analysis):

**Entry:**
- Entry EBITDA (LTM or NTM)
- Entry multiple (EV / EBITDA)
- Enterprise value
- Net debt at close
- Equity check size
- Transaction fees & expenses

**Financing:**
- Senior debt (x EBITDA, rate, amortization)
- Subordinated debt / mezzanine (if any)
- Total leverage at entry (x EBITDA)
- Equity contribution

**Operating Assumptions:**
- Revenue growth rate (annual)
- EBITDA margin trajectory
- Capex as % of revenue
- Working capital changes
- Debt paydown schedule

**Exit:**
- Hold period (years)
- Exit multiple (EV / EBITDA)
- Exit EBITDA (calculated from growth assumptions)

### Step 2: Base Case Returns

Calculate:

| Metric | Value |
|--------|-------|
| Entry EV | |
| Equity invested | |
| Exit EBITDA | |
| Exit EV | |
| Net debt at exit | |
| Exit equity value | |
| **MOIC** | |
| **IRR** | |
| Cash-on-cash | |

Show the returns waterfall:
- EBITDA growth contribution
- Multiple expansion/contraction contribution
- Debt paydown contribution
- Fee/expense drag

### Step 3: Sensitivity Tables

Build 2-way sensitivity matrices:

**Entry Multiple vs. Exit Multiple**
| | Lower exit case | | Base exit case | | Higher exit case |
|---|---------|---------|---------|---------|----------|
| Lower entry case | | | | | |
| | | | | | |
| Base entry case | | | | | |
| Higher entry case | | | | | |

**EBITDA Growth vs. Exit Multiple** (at fixed entry)

**Leverage vs. Exit Multiple** (at fixed entry and growth)

**Hold Period vs. Exit Multiple**

Show both IRR and MOIC in each cell (IRR / MOIC format).

### Step 4: Scenario Analysis

Build 3 scenarios:

| | Bull | Base | Bear |
|---|------|------|------|
| Revenue CAGR | | | |
| Exit EBITDA margin | | | |
| Exit multiple | | | |
| Exit EBITDA | | | |
| MOIC | | | |
| IRR | | | |

### Step 5: Output

- Excel workbook with:
  - Assumptions tab
  - Returns calculation
  - Sensitivity tables (formatted with conditional coloring)
  - Scenario summary
- One-page returns summary suitable for IC deck

## Key Formulas

- **MOIC** = Exit Equity Value / Equity Invested
- **IRR** = solve for r: Equity Invested × (1 + r)^n = Exit Equity Value (adjust for interim cash flows)
- **Returns attribution**:
  - Growth: (Exit EBITDA - Entry EBITDA) × Exit Multiple / Equity
  - Multiple: (Exit Multiple - Entry Multiple) × Entry EBITDA / Equity
  - Leverage: Debt paydown over hold period / Equity

## Important Notes

- Always show returns both gross and net of fees/carry where applicable
- Management rollover and co-invest change the equity check — ask if relevant
- Dividend recaps or interim distributions affect IRR significantly — include if planned
- Include transaction costs only from official transaction materials, `USER_PROVIDED` inputs, or an explicit `MODEL_DERIVED` scenario; they reduce Day 1 equity value
- Tax considerations (asset vs. stock deal, 338(h)(10) election) can materially affect after-tax returns
