---
name: merger-model
description: "建立 M&A accretion/dilution、pro forma EPS、synergy sensitivity 和 purchase price allocation 模型。"
---

# Merger Model

创建或修改 `.xlsx` 时，先读取 [`../../CODEX-EXECUTION-POLICY.md`](../../CODEX-EXECUTION-POLICY.md)。

## Public-source gate

Read [`PUBLIC-SOURCE-POLICY.md`](../../PUBLIC-SOURCE-POLICY.md) before gathering inputs. Use opened company filings/IR materials, official transaction announcements or regulator records, validated public prices, and `USER_PROVIDED` deal terms. LTM actuals must be tied to cited filings; forward EPS requires dated issuer guidance, a user input, or `MODEL_DERIVED` assumptions. Synergies and financing terms must be sourced to an official deal document or labeled `USER_PROVIDED`/`MODEL_DERIVED`; otherwise mark them `SOURCE_UNAVAILABLE`.

## Workflow

### Step 1: Gather Inputs

**Acquirer:**
- Company name, current share price, shares outstanding
- LTM and NTM EPS (GAAP and adjusted)
- P/E multiple
- Pre-tax cost of debt, tax rate
- Cash on balance sheet, existing debt

**Target:**
- Company name, current share price, shares outstanding (if public)
- LTM and NTM EPS or net income
- Enterprise value or equity value

**Deal Terms:**
- Offer price per share (or premium to current)
- Consideration mix: % cash vs. % stock
- New debt raised to fund cash portion
- Expected synergies (revenue and cost) and phase-in timeline
- Transaction fees and financing costs
- Expected close date

### Step 2: Purchase Price Analysis

| Item | Value |
|------|-------|
| Offer price per share | |
| Premium to current | |
| Equity value | |
| Plus: net debt assumed | |
| Enterprise value | |
| EV / EBITDA implied | |
| P/E implied | |

### Step 3: Sources & Uses

| Sources | $ | Uses | $ |
|---------|---|------|---|
| New debt | | Equity purchase price | |
| Cash on hand | | Refinance target debt | |
| New equity issued | | Transaction fees | |
| | | Financing fees | |
| **Total** | | **Total** | |

### Step 4: Pro Forma EPS (Accretion / Dilution)

Calculate year-by-year (Year 1-3):

| | Standalone | Pro Forma | Accretion/(Dilution) |
|---|-----------|-----------|---------------------|
| Acquirer net income | | | |
| Target net income | | | |
| Synergies (after tax) | | | |
| Foregone interest on cash (after tax) | | | |
| New debt interest (after tax) | | | |
| Intangible amortization (after tax) | | | |
| Pro forma net income | | | |
| Pro forma shares | | | |
| **Pro forma EPS** | | | |
| **Accretion / (Dilution) %** | | | |

### Step 5: Sensitivity Analysis

**Accretion/Dilution vs. Synergies and Offer Premium:**

| | $0M syn | $25M syn | $50M syn | $75M syn | $100M syn |
|---|---------|----------|----------|----------|-----------|
| Lower purchase-price case | | | | | |
| Base purchase-price case | | | | | |
| Higher purchase-price case | | | | | |

**Accretion/Dilution vs. Cash/Stock Mix:**

| | Financing case 1 | Financing case 2 | Base financing | Financing case 4 | Financing case 5 |
|---|-----------|-------|-------|-------|------------|
| Year 1 | | | | | |
| Year 2 | | | | | |

### Step 6: Breakeven Synergies

Calculate the minimum synergies needed for the deal to be EPS-neutral in Year 1.

### Step 7: Output

- Excel workbook with:
  - Assumptions tab
  - Sources & uses
  - Pro forma income statement
  - Accretion/dilution summary
  - Sensitivity tables
  - Breakeven analysis
- One-page merger consequences summary for pitch book

## Important Notes

- Always show both GAAP and adjusted (cash) EPS where relevant
- Stock deals: use acquirer's current price for exchange ratio, note dilution from new shares
- Include purchase price allocation — goodwill and intangible amortization matter for GAAP EPS
- Synergy phase-in is critical; use official deal disclosure, `USER_PROVIDED` assumptions, or explicit `MODEL_DERIVED` cases rather than a default realization range
- Don't forget foregone interest income on cash used and new interest expense on debt raised
- Tax rate on synergies and interest adjustments should match the acquirer's marginal rate
