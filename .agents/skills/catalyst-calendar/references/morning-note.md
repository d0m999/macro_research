# Morning Note (Same-Day Workflow)

只在用户要隔夜/当日汇总、晨会笔记或 daily note 时读取。日历模式不要读本文件。

## 1. Overnight Scan

按覆盖宇宙扫描三类事项，只收本次可核验的公开信息。

**Earnings & Guidance**

- 覆盖公司是否在隔夜或盘前发布财报。
- revenue、EPS 和关键指标的 beat/miss。
- guidance 的 raised / lowered / maintained，并记录发布日期。

**News & Events**

- 公开的 M&A 公告；未经核验的传闻省略或标 `SOURCE_UNAVAILABLE`。
- 管理层变动。
- 产品发布、监管决定、公司/监管机构/官方交易所公告。
- 影响板块的宏观数据或政策变化。

**Market Context**

- 隔夜期货/盘前、板块 ETF、相关商品或货币：只用已验证的公开页面或 `USER_PROVIDED` 导出。
- 今日将公布的关键经济数据。

不使用私有终端、付费新闻、analyst consensus 或 whisper data。

## 2. Note Format

保持能在两分钟内读完。`[Analyst Name]` 与 `[Sector Coverage]` 按用户覆盖范围填写。

```markdown
**[Date] Morning Note — [Analyst Name]**
**[Sector Coverage]**

**Top Call: [Headline — PM 唯一需要知道的事]**
- 2-3 句：关键进展与为什么重要
- 股价影响：目标价、评级维持/调整

**Overnight/Pre-Market Developments**
- [公司 A]: 一行摘要 + 我们的看法
- [公司 B]: 一行摘要 + 我们的看法
- [板块/宏观]: 板块级变化

**Key Events Today**
- [时间]: [公司] 财报电话会
- [时间]: [经济数据]（预期 vs 我们的看法）
- [时间]: 会议或 investor day

**Trade Ideas** (如有)
- [Long/Short] [公司]: 1-2 句 thesis + 催化剂
- Risk: 什么会证明这是错的
```

## 3. Quick Takes on Earnings

覆盖公司已发布财报时给快速反应：

| Metric | Public Guide / Our Est. | Actual | Variance |
|---|---|---|---|
| Revenue | | | |
| EPS | | | |
| [Key metric] | | | |
| Guidance | | | |

**Our Take**：2-3 句——对股价是好是坏？是否改变 thesis？
**Action**：维持/上调/下调评级？是否调整目标价？

基线不存在时不写 variance，改为 actual-vs-prior period 陈述；不得用未标注来源的「市场预期」充当基线。

## 4. Output

- 默认 Markdown 文本，供用户或团队分发。
- 需要正式分发时输出 Word 文档。
- 一页为上限；PM 和交易员不会读更长的东西。

## 写作判据

- 要有观点。只罗列新闻没有看法的晨会笔记没有价值。
- 把最重要的放最前，不要埋头条。
- 「隔夜无大事」是有效的晨会笔记——直接写无事发生、维持现有仓位。
- 区分可执行事件（财报、M&A）与噪音（次要公告、非事件）。
- 注明写作时点：6 点写的稿要说明盘前可能变化。
- 判断错了在下期晨会里认账——可信度比每次都对更重要。
