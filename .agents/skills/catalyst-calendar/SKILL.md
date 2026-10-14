---
name: catalyst-calendar
description: "建立和维护覆盖公司的催化剂日历，并按时间窗产出前瞻预览或当日晨会笔记，全部事件核验后可追溯。用于催化剂日历、事件日历、财报日期、近期催化剂、晨会、早报、morning note、隔夜发生了什么或 daily note 请求。指定时间窗优先。"
---

# Catalyst Calendar & Morning Note

按时间窗供给事件信息：远期建日历与周度前瞻，当日汇总隔夜公开事件并给出观点。两者共用同一套事件核验规则——「今日关键事件」是日历在当前时间窗上的切片，同一事件的 source record 只建一次。

## 必读契约

- 来源合规与数据源路由遵循 [`../../PUBLIC-SOURCE-POLICY.md`](../../PUBLIC-SOURCE-POLICY.md)（含路由登记表 [`../../data-sources.jsonl`](../../data-sources.jsonl)，无匹配时 fail-closed）。
- 创建或修改 Office 产物前读取 [`../../CODEX-EXECUTION-POLICY.md`](../../CODEX-EXECUTION-POLICY.md)；验证器状态与限制按其口径披露。
- 需要晨会笔记格式、隔夜扫描口径与写作判据时读取 [`references/morning-note.md`](references/morning-note.md)。

## 模式判别

- **日历模式**：用户要未来一段时间的催化剂、事件日历、周度前瞻或财报日期。产出覆盖宇宙、事件表和周度前瞻。
- **晨会模式**：用户要隔夜或当日汇总、morning note、daily note。产出一页式晨会笔记，含覆盖公司的快速反应表。
- 可叠加：先刷新日历再取当日切片，两个模式共用 source manifest。

## 工作流

### 日历模式

1. **定义覆盖宇宙**：标的清单、行业焦点、是否纳入宏观事件、时间窗（两周/月/季度）。
2. **收集催化剂**：财报与财务事件（财报日期与时段、股东会、investor day、capital markets day、债务到期/再融资）；公司事件（产品发布、FDA/监管决定、合同续约、M&A 里程碑、管理层变动、锁定期到期）；行业事件（会议、展会、监管评论期、月度数据）；宏观事件（FOMC、就业/CPI/GDP、其他央行决议、有市场影响的地缘事件）。
3. **日历表**：`| 日期 | 事件 | 标的/行业 | 类型 | 影响 | 持仓含义 | 备注 |`，日期未定的标「预计」并注明以 IR/公告为准。
4. **周度前瞻**：本周关键事件（逐项给公开 guidance 基线或 `SOURCE_UNAVAILABLE`、我们的估计、关注指标）、下周预告、对持仓的影响与二元事件前的风控。
5. **输出**：可排序的 Excel 日历、周度预览笔记、可选的本地 Markdown/CSV 日历供用户导入。

### 晨会模式

读取 [`references/morning-note.md`](references/morning-note.md)，按四步执行：隔夜扫描 → 一页式笔记（Top Call / 隔夜进展 / 今日事件 / Trade Ideas）→ 覆盖公司快速反应表 → 输出。日历模式产出的基线在此直接引用，不重新取数。

## 完成条件

- 每条事件从本次实际打开的发行人、监管、政府或官方交易所页面核验；未核验或日期未定的标 `SOURCE_UNAVAILABLE`/「预计」，不用推测日期填充。
- 日历表字段完整、影响分级有依据；有改期历史的会议类事件注明「以 IR/公告为准」。
- 晨会笔记一页以内、有明确 Top Call 观点，区分可执行事件与噪音，写作时点已注明；隔夜无大事时明确说无事发生。
- 快速反应表的 actual/variance 相对 dated public guidance 或 `USER_PROVIDED` 基线；无基线时只做 actual-vs-prior 陈述。
- 过往催化剂归档时带实际结果，可跨期复用；周度前瞻只列已核验事件。
- `.xlsx`/`.docx`/`.pptx` 产物按契约运行统一验证器并披露限制。
