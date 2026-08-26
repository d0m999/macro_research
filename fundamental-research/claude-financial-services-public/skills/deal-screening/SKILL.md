---
name: deal-screening
description: Quickly screen inbound deal flow — CIMs, teasers, and broker materials — against the fund's investment criteria. Extracts key deal metrics, runs a pass/fail framework, and outputs a one-page screening memo. Use when reviewing new deal flow, triaging inbound materials, or deciding whether to take a first call. Triggers on "screen this deal", "review this CIM", "should we look at this", "triage this teaser", or "deal screening".
---

# Deal Screening

## Public-source and user-material gate

Read [`PUBLIC-SOURCE-POLICY.md`](../../PUBLIC-SOURCE-POLICY.md). Treat the CIM, teaser, broker material, and any internal financials as `USER_PROVIDED` only when the user supplies them. Supplement with opened issuer, regulator, government, or official transaction sources. Do not fill gaps with private databases, analyst consensus, or unverified broker claims; label each missing fact `SOURCE_UNAVAILABLE` and keep the verdict conditional.

## Workflow

### Step 1: Extract Deal Facts

From the provided CIM, teaser, or description, extract:

- **Company**: Name, location, sector/subsector
- **Description**: What they do (1-2 sentences)
- **Financials**: Revenue, EBITDA, margins, growth rate
- **Deal type**: Platform, add-on, recap, minority, carve-out
- **Asking price / valuation**: Multiple, enterprise value if stated
- **Seller motivation**: Why selling now
- **Management**: Rolling or exiting
- **Key customers**: Concentration risk
- **Key risks**: Obvious red flags

### Step 2: Screen Against Criteria

Apply the fund's investment criteria (ask user if not known):

| Criterion | Target | Actual | Pass/Fail |
|-----------|--------|--------|-----------|
| Revenue range | | | |
| EBITDA range | | | |
| EBITDA margin | | | |
| Growth profile | | | |
| Sector fit | | | |
| Geography | | | |
| Deal size / EV | | | |
| Valuation (x EBITDA) | | | |
| Customer concentration | | | |
| Management continuity | | | |

### Step 3: Quick Assessment

Provide a 3-part assessment:

1. **Verdict**: Pass / Further Diligence / Hard Pass
2. **Bull case** (2-3 bullets): Why this could be a good deal
3. **Bear case** (2-3 bullets): Key risks and concerns
4. **Key questions**: What you'd need to answer on a first call

### Step 4: Output

One-page screening memo suitable for sharing with partners or an IC quick screen.

## Important Notes

- Speed matters — screening should take minutes, not hours
- Be direct about red flags. Don't bury concerns
- If financials seem inconsistent or incomplete, flag it explicitly
- Ask for the fund's criteria upfront if this is the first screening
- Save screening criteria in memory for future deals once confirmed
