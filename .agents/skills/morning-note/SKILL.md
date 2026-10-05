---
name: morning-note
description: "汇总隔夜公开事件、覆盖公司变化和可验证的交易观察，形成简洁晨会笔记。用于晨会、早报、morning note、隔夜发生了什么或 daily note。"
---

# Morning Note

生成或修改 `.docx`、`.xlsx` 或 `.pptx` 时，先读取 [`../../CODEX-EXECUTION-POLICY.md`](../../CODEX-EXECUTION-POLICY.md)。

## Public-source gate

Read [`PUBLIC-SOURCE-POLICY.md`](../../PUBLIC-SOURCE-POLICY.md) first. Use opened issuer releases and IR pages, SEC or other regulator filings, official government/exchange pages, and validated public market pages or user-provided exports. If an overnight item or price is not publicly accessible and citable, mark it `SOURCE_UNAVAILABLE` and do not infer it. Do not use private terminals, paid news, analyst consensus, or whisper data.
Resolve every concrete source from [`../../data-sources.jsonl`](../../data-sources.jsonl) (single source of truth for skill data-source routing): filter by `data_types` × `markets`; honor `policy_status`/`auth`/`cost`; fail closed when nothing matches.

## Workflow

### Step 1: Overnight Developments

Scan for relevant events across coverage universe:

**Earnings & Guidance**
- Any coverage companies reporting overnight or pre-market?
- Earnings surprises (beat/miss on revenue, EPS, key metrics)
- Guidance changes (raised, lowered, maintained)

**News & Events**
- Public M&A announcements; unverified rumors are omitted or labeled `SOURCE_UNAVAILABLE`
- Management changes
- Product launches or regulatory decisions
- Publicly accessible company, regulator, or official exchange announcements
- Macro data or policy changes affecting the sector

**Market Context**
- Overnight futures / pre-market moves from a validated public page or `USER_PROVIDED` export
- Sector ETF performance from a validated public page or `USER_PROVIDED` export
- Relevant commodity or currency moves from a validated public page or `USER_PROVIDED` export
- Key economic data releases today

### Step 2: Morning Note Format

Keep it tight — a morning note should be readable in 2 minutes:

---

**[Date] Morning Note — [Analyst Name]**
**[Sector Coverage]**

**Top Call: [Headline — the one thing PMs need to hear]**
- 2-3 sentences on the key development and why it matters
- Stock impact: price target, rating reiteration/change

**Overnight/Pre-Market Developments**
- [Company A]: One-line summary of earnings/news + our take
- [Company B]: One-line summary + our take
- [Sector/Macro]: Relevant sector-wide development

**Key Events Today**
- [Time]: [Company] earnings call
- [Time]: Economic data release (expectations vs. our view)
- [Time]: Conference or investor day

**Trade Ideas** (if any)
- [Long/Short] [Company]: 1-2 sentence thesis + catalyst
- Risk: What would make this wrong

---

### Step 3: Quick Takes on Earnings

If a coverage company reported, provide a quick reaction:

| Metric | Public Guide / Our Est. | Actual | Variance |
|--------|-----------|--------|-----------|
| Revenue | | | |
| EPS | | | |
| [Key metric] | | | |
| Guidance | | | |

**Our Take**: 2-3 sentences — is this good or bad for the stock? Does it change our thesis?

**Action**: Maintain / Upgrade / Downgrade rating? Adjust price target?

### Step 4: Output

- Markdown text for user/team distribution
- Word document if formal distribution is needed
- Keep to 1 page max — PMs and traders won't read more

## Important Notes

- Be opinionated — morning notes that just summarize news without a view are useless
- Lead with the most important thing — don't bury the headline
- "No news" is a valid morning note — say "nothing material overnight, maintaining positioning"
- Distinguish between actionable events (earnings, M&A) and noise (minor announcements, non-events)
- Time-stamp your takes — if you're writing at 6am, note that pre-market may change by open
- If you're wrong, own it in the next morning note — credibility matters more than being right every time
