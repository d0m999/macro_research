---
name: buyer-list
description: "为卖方 M&A 建立潜在战略买家与财务买家 universe，评估匹配度并排序。"
---

# Buyer List

生成或修改 `.xlsx`、`.pptx` 或 `.docx` 时，先读取 [`../../CODEX-EXECUTION-POLICY.md`](../../CODEX-EXECUTION-POLICY.md)。

## Public-source gate

Read [`PUBLIC-SOURCE-POLICY.md`](../../PUBLIC-SOURCE-POLICY.md) before building the universe. Research buyer fit, revenue, capacity, public M&A history, and fund activity only from opened issuer/sponsor pages, filings, regulator or government records, official transaction announcements, or `USER_PROVIDED` materials. Do not use unprovided relationship data, paid databases, or unverified contact lists. If fund size, track record, likelihood, or a decision-maker cannot be verified publicly, record `SOURCE_UNAVAILABLE` rather than estimating it as fact.

## Workflow

### Step 1: Understand the Target

- Company description, sector, and business model
- Revenue, EBITDA, and growth profile
- Key assets and capabilities (IP, customer relationships, geographic footprint, team)
- Expected valuation range (`USER_PROVIDED` or `MODEL_DERIVED`)
- Seller preferences (strategic vs. financial, management continuity, timeline)

### Step 2: Strategic Buyers

Identify strategic acquirers across categories:

**Direct Competitors**
- Companies in the same space that would gain market share
- Rationale: Revenue synergies, eliminate competitor, scale

**Adjacent Players**
- Companies in adjacent markets that could expand into the target's space
- Rationale: Product extension, cross-sell, new market entry

**Vertical Integrators**
- Customers or suppliers that could integrate vertically
- Rationale: Supply chain control, margin capture, strategic lock-in

**Platform Builders**
- Large companies building a platform in the space through M&A
- Rationale: Tuck-in acquisition, fill capability gap

For each strategic buyer, assess:

| Buyer | Sector | Revenue | Strategic Fit | Financial Capacity | M&A Track Record | Likelihood | Priority |
|-------|--------|---------|--------------|-------------------|------------------|------------|----------|
| | | | High/Med/Low | | Active/Moderate/None | | A/B/C |

### Step 3: Financial Sponsors

Identify PE/financial buyers:

**Platform Investors**
- Sponsors looking for a new platform in this sector
- Criteria: Fund size, sector focus, deal size range

**Add-on Buyers**
- Sponsors with existing portfolio companies that could acquire the target as a bolt-on
- Identify the specific portfolio company and synergy rationale

**Growth Equity**
- For earlier-stage or high-growth targets
- Minority vs. majority preference

For each sponsor:

| Sponsor | Fund Size | Sector Focus | Portfolio Overlap | Recent Activity | Priority |
|---------|-----------|-------------|-------------------|-----------------|----------|
| | | | | | A/B/C |

### Step 4: Prioritization

Tier the buyer list:

- **Tier 1 (5-10)**: Highest strategic fit, proven acquirers, clear rationale — contact first
- **Tier 2 (10-15)**: Good fit but less obvious — contact in second wave
- **Tier 3 (10-20)**: Possible but lower probability — contact if process needs broadening

### Step 5: Contact Mapping

For each Tier 1 buyer:
- Key decision maker (CEO, Corp Dev head, Partner) only from an official public team page or filing
- Relationship status (existing relationship, cold outreach, need introduction)
- Known preferences or constraints (size, geography, structure)
- Best approach channel, without private contact details unless the user supplies them

### Step 6: Output

- Excel workbook with:
  - Strategic buyers tab (sorted by tier)
  - Financial sponsors tab (sorted by tier)
  - Contact mapping for Tier 1
  - Summary statistics (total buyers by tier, by type)
- One-page buyer universe summary for the engagement letter or pitch

## Important Notes

- Quality over quantity — a focused list of 30-40 well-researched buyers beats a list of 200 names
- Research recent M&A activity — buyers who just did a deal in the space are either hungry for more or tapped out
- Check for antitrust concerns with direct competitors — flag any that might face regulatory issues
- Financial sponsors: check fund vintage and deployment pace — a fund nearing end of investment period may be more motivated
- Always ask the seller if there are buyers they want included or excluded
- Update the list as the process progresses — move buyers between tiers based on feedback
