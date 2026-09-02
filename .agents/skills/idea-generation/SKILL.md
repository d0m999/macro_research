---
name: idea-generation
description: "用可公开核验的筛选条件和主题研究生成多空候选，并区分筛选结果与投资结论。用于选股、股票筛选、投资想法、idea generation 或 thematic sweep。"
---

# Idea Generation

生成或修改 `.docx`、`.xlsx` 或 `.pptx` 时，先读取 [`../../CODEX-EXECUTION-POLICY.md`](../../CODEX-EXECUTION-POLICY.md)。

## Public-source gate

Read [`PUBLIC-SOURCE-POLICY.md`](../../PUBLIC-SOURCE-POLICY.md) before screening. Use only SEC EDGAR or other official regulator filings, issuer IR materials, government or official exchange pages, and validated public market-history pages or user-provided exports. Historical ratios may be calculated from cited inputs. Forward multiples or estimates require dated issuer guidance, a `USER_PROVIDED` estimate, or an explicitly labeled `MODEL_DERIVED` case; do not substitute analyst consensus or whisper data. If a required input cannot be opened and cited, record `SOURCE_UNAVAILABLE` and omit the ranking rather than filling it in.

## Workflow

### Step 1: Define Search Criteria

Ask the user for parameters:
- **Direction**: Long ideas, short ideas, or both
- **Market cap**: Large, mid, small, micro
- **Sector**: Specific sector or cross-sector
- **Style**: Value, growth, quality, special situation, event-driven
- **Geography**: US, international, global
- **Theme**: Any specific thematic angle (AI, reshoring, aging demographics, etc.)

### Step 2: Quantitative Screens

Build screens from cited, reproducible inputs. Market cap may be calculated as a cited public price multiplied by a cited share count. Insider activity may use public regulator filings such as SEC Forms 3/4/5. Short interest, ownership, and coverage counts are allowed only when an official or fully public source is opened and cited; otherwise mark them `SOURCE_UNAVAILABLE`.

Run screens based on the style. Every threshold must come from the user's criteria, the company's cited history, an opened public peer distribution, or an explicitly labeled `MODEL_DERIVED` screen; do not use the examples below as fixed cutoffs:

**Value Screen**
- P/E below sector median
- EV/EBITDA below historical average
- Free cash flow yield above the selected sourced comparison threshold
- Price/book below the selected sourced comparison threshold
- Insider buying over the user-selected, disclosed filing window
- Dividend yield above market average

**Growth Screen**
- Revenue growth above the selected historical/peer threshold
- Earnings growth above the selected historical/peer threshold
- Revenue acceleration (growth rate increasing)
- Expanding margins
- Return on invested capital above the selected sourced comparison
- Net retention above the selected company-history or public-peer comparison

**Quality Screen**
- Consistent revenue growth over the available comparable history
- Stable or expanding margins
- ROE above the selected sourced comparison
- Low debt/equity
- High free cash flow conversion
- Insider ownership relative to the selected public comparison set

**Short Screen**
- Declining revenue or decelerating growth
- Margin compression
- Rising receivables / inventory vs. sales
- Insider selling
- Valuation premium to peers without justification
- High short interest with deteriorating fundamentals
- Accounting red flags (auditor changes, restatements)

**Special Situation Screen**
- Recent IPOs / SPACs with lockup expirations
- Recent spin-offs within the user-selected event window
- Companies emerging from restructuring
- Activist involvement
- Management changes at underperforming companies

### Step 3: Thematic Sweep

For thematic ideas, research the theme and identify beneficiaries:

1. Define the thesis (e.g., "AI infrastructure spending accelerates through 2026")
2. Map the value chain — who benefits directly vs. indirectly?
3. Identify pure-play vs. diversified exposure
4. Assess which names are already "priced in" vs. under-appreciated
5. Look for second-order beneficiaries that the market hasn't connected to the theme

### Step 4: Idea Presentation

For each idea that passes the screen, present:

**[Company Name] — [Long/Short] — [One-Line Thesis]**

| Metric | Value | vs. Peers |
|--------|-------|-----------|
| Market cap | | |
| EV/EBITDA (forward, if public guidance/model-derived) | | |
| P/E (forward, if public guidance/model-derived) | | |
| Revenue growth | | |
| EBITDA margin | | |
| FCF yield | | |

**Thesis (3-5 bullets):**
- Why this is mispriced
- What the market is missing
- Catalyst to realize value

**Key Risks:**
- What would make this wrong

**Suggested Next Steps:**
- Build full model? Deep-dive diligence? Expert call?

### Step 5: Output

- Shortlist of 5-10 ideas with one-page summaries
- Screening criteria and methodology documented
- Comparison table across all ideas
- Prioritized list: which ideas to research first

## Important Notes

- Screens surface candidates, not conclusions — every screen output needs fundamental work
- The best ideas often come from intersections (e.g., quality company at value price due to temporary headwind)
- Avoid crowded trades — check ownership data or short interest only from opened public sources; analyst-coverage counts are optional and must be `SOURCE_UNAVAILABLE` when no public source is citable
- Contrarian ideas need a catalyst — being early without a catalyst is the same as being wrong
- Track idea hit rates over time — which screens and approaches produce the best ideas?
- Short ideas need higher conviction — timing is harder and risk is asymmetric
