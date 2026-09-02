---
name: deal-tracker
description: "基于用户提供的状态跟踪多笔交易的里程碑、截止日、行动项和 pipeline 更新。"
---

# Deal Tracker

生成或修改 `.xlsx`、`.docx` 或 `.pptx` 时，先读取 [`../../CODEX-EXECUTION-POLICY.md`](../../CODEX-EXECUTION-POLICY.md)。

## Input boundary

Use only deal milestones, statuses, and dates supplied by the user or already present in the current workspace. Do not connect to private deal-management systems or infer unprovided status; mark missing fields `SOURCE_UNAVAILABLE`.

## Workflow

### Step 1: Deal Setup

For each deal, capture:
- **Deal name / code name**: Project [Name]
- **Client**: Seller or buyer name
- **Deal type**: Sell-side, buy-side, financing, restructuring
- **Role**: Lead advisor, co-advisor, fairness opinion
- **Deal size**: Expected enterprise value
- **Stage**: Pre-mandate → Engaged → Marketing → IOI → Diligence → Final bids → Signing → Close
- **Team**: MD, VP, Associate, Analyst assigned
- **Key dates**: Engagement date, CIM distribution, IOI deadline, management meetings, final bid deadline, target close

### Step 2: Milestone Tracking

Track key milestones per deal:

| Milestone | Target Date | Actual Date | Status | Notes |
|-----------|------------|-------------|--------|-------|
| Engagement letter signed | | | | |
| CIM / teaser drafted | | | | |
| Buyer list approved | | | | |
| Teaser distributed | | | | |
| NDA execution | | | | |
| CIM distributed | | | | |
| IOI deadline | | | | |
| IOIs received / reviewed | | | | |
| Shortlist selected | | | | |
| Management meetings | | | | |
| User-provided diligence materials received | | | | |
| Final bid deadline | | | | |
| Bids received / reviewed | | | | |
| Exclusivity granted | | | | |
| Confirmatory diligence | | | | |
| Purchase agreement signed | | | | |
| Regulatory approval | | | | |
| Close | | | | |

Status: On Track / At Risk / Delayed / Complete

### Step 3: Action Items

Maintain a running action item list across all deals:

| Action | Deal | Owner | Due Date | Priority | Status |
|--------|------|-------|----------|----------|--------|
| | | | | P0/P1/P2 | Open/Done/Blocked |

### Step 4: Weekly Deal Review

Generate a summary for weekly team meetings:

**For each active deal:**
1. One-line status update
2. Key developments this week
3. Upcoming milestones (next 2 weeks)
4. Blockers or risks
5. Action items for next week

**Pipeline summary:**
- Total active deals by stage
- Deals at risk (missed milestones, stalled processes)
- New mandates / pitches in pipeline
- Expected closings this quarter

### Step 5: Output

- Excel workbook with:
  - Pipeline overview (all deals, one row each)
  - Per-deal milestone tracker tabs
  - Action item master list
  - Weekly review summary
- Optional: Markdown summary for user/team distribution

## Important Notes

- Update the tracker weekly at minimum — stale trackers are worse than no tracker
- Flag deals where milestones are slipping — early warning prevents surprises
- Action items without owners and due dates don't get done — be specific
- The pipeline view should show deal stage, size, and likelihood — useful for revenue forecasting
- Keep notes on buyer/investor feedback — patterns in feedback inform strategy adjustments
- Archive closed/dead deals separately — keep the active view clean
