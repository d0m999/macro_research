# Three-Statement Formula Reference

只在补建公式或 schedule 时读取；模板已有可靠公式时保留其结构。

## Core linkages

```text
Assets = Liabilities + Equity
Change in Cash = CFO + CFI + CFF
Ending Cash (Cash Flow) = Cash (Balance Sheet)
Ending Retained Earnings = Beginning Retained Earnings + Net Income - Dividends
Ending PP&E = Beginning PP&E + CapEx - Depreciation - Disposals
Ending Debt = Beginning Debt + Borrowings + PIK - Repayments
```

## Operating metrics

```text
Gross Profit = Revenue - Cost of Revenue
EBITDA = EBIT + D&A
NOPAT = EBIT x (1 - Cash Tax Rate)
Net Debt = Debt - Cash
Change in NWC = NWC_current - NWC_prior
FCFF = NOPAT + D&A - CapEx - Change in NWC
```

每个 metric 的具体定义服从公司 disclosure 和用户模板。Revenue、EBITDA、debt、NWC、CapEx、tax 和 share count 的调整必须显示 reconciliation。

循环利息/现金模型若模板已有 circuit breaker 则保留；新建时把开关、iteration 假设和不收敛状态显式放在 checks。不要用固定 plug 隐藏循环错误。
