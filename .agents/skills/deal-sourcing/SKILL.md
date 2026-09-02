---
name: deal-sourcing
description: "从公开页面发现 PE 目标公司，结合用户提供的 prior-contact 记录并起草个性化 outreach。"
---

# Deal Sourcing

将 shortlist 或 outreach 输出为 `.docx`、`.xlsx` 或 `.pptx` 时，先读取 [`../../CODEX-EXECUTION-POLICY.md`](../../CODEX-EXECUTION-POLICY.md)。

**Public-source gate:** Read [`../../PUBLIC-SOURCE-POLICY.md`](../../PUBLIC-SOURCE-POLICY.md). Discovery is limited to publicly reachable company, regulator, government, exchange, organizer or trade-association pages; private relationship data is not part of this package.

## Workflow

This skill follows a 3-step sourcing pipeline:

### Step 1: Discover Companies

Research and identify potential target companies based on the user's criteria:

- **Sector/industry focus**: Ask the user what space they're looking in (e.g., "B2B SaaS in healthcare", "industrial services in the Southeast")
- **Deal parameters**: Revenue range, EBITDA range, growth profile, geography, ownership type (founder-owned, PE-backed, corporate carve-out)
- **Sources**: Use search only to discover official company pages, SEC/other regulator filings, government records, public conference-organizer lists and public trade-association pages
- **Output**: A shortlist of companies with: name, description, disclosed revenue/size (or `SOURCE_UNAVAILABLE`), location, publicly identified founder/CEO, official website, source records and why they fit the thesis

### Step 2: CRM Check

Before outreach, ask whether the user has supplied a prior-contact export or prior-contact context. Do not connect to private systems or infer unprovided relationship data:

- If an export or prior correspondence is supplied, label it `USER_PROVIDED` and summarize only the provided evidence
- If no such context is supplied, record exactly `Prior contact unknown`; do not infer `New`
- Ask for prior-contact context only when outreach personalization or deduplication actually depends on it
- Flag existing relationships, prior passes or known context only when supported by the user-provided record
- **Output**: For each company, note `Prior contact unknown` when no record was supplied; use "New", "Existing", or "Previously Passed" only when the user-provided evidence supports that status

### Step 3: Draft Founder Outreach

Draft personalized cold emails to founders/CEOs:

- **Tone**: Professional but warm. Not overly formal — founders respond better to genuine, concise outreach
- **Structure**:
  1. Brief intro — who you are and your firm (ask user for their firm intro if not known)
  2. Why this company caught your attention — reference something specific (product, market position, growth)
  3. What you're looking for — partnership, not just a transaction
  4. Soft ask — "Would you be open to a brief conversation?"
- **Personalization**: Reference the company's specific product, a dated issuer/regulator announcement, or a publicly cited market position. Never use generic templates
- **Length**: 4-6 sentences max. Founders are busy
- **Voice matching**: If the user supplies prior outreach emails, study them to match tone and style; otherwise use a neutral professional voice

### Email Draft Guidelines

- Subject line: Keep it short and specific. Reference the company or sector, not "Investment Opportunity"
- No attachments on first touch
- Include a clear but low-pressure CTA
- Output as text for the user to review and copy; sending is outside this skill

## Example Interaction

**User**: "Find me founder-owned industrial services companies in Texas doing $10-50M revenue"

**Assistant**:
1. Searches web for industrial services companies in Texas matching the criteria
2. Presents a shortlist of 5-8 companies with key details
3. For each, checks only the user-provided prior-contact context; unknown status remains `SOURCE_UNAVAILABLE`
4. Drafts personalized outreach emails when requested; shortlist review is not a mandatory pause if the user authorized the full sourcing-and-drafting task
5. Presents drafts for user review before sending

## Important Notes

- Present the shortlist and drafts as separate sections so the user can review them together
- Never send emails without explicit user approval
- If the user's firm intro or investment criteria aren't clear, ask before drafting
- Prioritize quality over quantity — 5 well-researched targets beat 20 generic ones
