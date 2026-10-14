# Model Update Playbook

只在刷新已有模型时读取。新建模型不要读本文件。

## 1. Identify the Trigger

确定更新来源：财报发布（新 actuals 要 plug）、guidance 变化、基于新引用公开数据或 `USER_PROVIDED` 数据的假设修订、宏观更新（利率/FX/商品）、事件驱动（M&A、重组、新产品、管理层变动）。

更新前先确认模型本身的口径：币种、单位、历史/预测分界、GAAP/adjusted。口径不同的数据在 plug 前先标准化，不直接覆盖。

## 2. Plug New Data

| Line Item | Prior Estimate | Actual | Delta | Notes |
|---|---|---|---|---|
| Revenue | | | | |
| Gross Margin | | | | |
| Operating Expenses | | | | |
| EBITDA | | | | |
| EPS | | | | |
| [Key metric] | | | | |

- **Segment detail**：逐段更新收入与 margin，标注 mix 变化。
- **Balance sheet / cash flow**：现金与债务余额、share count（回购/稀释）、CapEx 实际 vs 估计、营运资本变化。
- 先与公司已披露数字对平，再向前投影；非经常项目单独列一行，说明是否计入 adjusted 口径。

## 3. Revise Forward Estimates

| | Old FY Est | New FY Est | Change | Old Next FY | New Next FY | Change |
|---|---|---|---|---|---|---|
| Revenue | | | | | | |
| EBITDA | | | | | | |
| EPS | | | | | | |

**Key Assumption Changes**：逐项写「旧 → 新（理由）」。理由只能指向已打开的 filing/guidance、`USER_PROVIDED` 输入或标 `MODEL_DERIVED` 的推导；不得用「行业常见值」或模型记忆解释变动。

## 4. Valuation Impact

| Valuation Method | Prior | Updated | Change |
|---|---|---|---|
| DCF fair value | | | |
| P/E（NTM EPS × target multiple） | | | |
| EV/EBITDA（NTM EBITDA × target multiple） | | | |
| **Price Target** | | | |

重算必须沿用原模型的方法、倍数、share count 和估值日；改变方法等于另一次估值，不是 model update。价格或 shares 输入缺失时相关行写 `SOURCE_UNAVAILABLE`，不用模型内旧值冒充当前值。

## 5. Summary & Action

- 一段话说明改了什么、为什么、对股票意味着什么；区分 thesis 级变化与噪音。
- 评级/目标价是否调整、方法论和相对现价的空间。

## 6. Output

- 更新后的模型副本（不覆盖用户原文件）。
- Estimate change summary（Markdown 或 Word）。
- 目标价推导过程。

## 判据

- 估计修订历史要保留——它是分析演进过程的记录。
- 季度噪音大时，把信号与噪音在估计变动里分开。
- share count 要紧：股权激励、可转债、回购对 EPS 影响可能主导结果。
- 与 dated public guidance 或 dated `USER_PROVIDED` estimate 比较；两者都没有时写 `SOURCE_UNAVAILABLE`，不写 beat/miss。
