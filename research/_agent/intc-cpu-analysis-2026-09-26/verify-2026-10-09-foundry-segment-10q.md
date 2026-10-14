# 一手来源核验：Foundry 分部收入与外部收入序列（10-Q 原件，2026-10-09）

> **为什么有这份文件：** 本轮（2026-10-09）在写 `update-2026-10-09-*.md` §6.3 时发现，主文档与链条四都写着
> 「Foundry 同季 **20.89 亿美元营业亏损**，外部收入仅 **2.93 亿美元**」——**把 20.89 亿同时当成了分部收入和营业亏损**。
> 这在算术上意味着 100% 亏损率。本文回 SEC 原件核清，并补上此前缺的 Q1 外部收入 `[A]` 级来源。
>
> **按本仓惯例不改原稿**（`复核不改原稿，改动单列`），本文是结论单列件；主文档与链条四的改正建议见 §5，待用户确认后执行。

**核验日：2026-10-09。** 证据全部来自 SEC EDGAR 原件（`PUBLIC_NO_AUTH`，SEC 官方归档，非发行人网站转发）。

---

## 0. 结论

**1. 那个 20.89 亿确实是串行错误，但它错的方向比预想的小——20.89 亿是「营业亏损」，不是「分部收入」。** Q2 2026 Intel Foundry 分部**收入为 57.65 亿美元**，营业亏损 20.89 亿，亏损率 **-36%**。原稿把亏损额错当成了收入额，导致「亏损率 100%」的荒谬读数，但**「营业亏损 20.89 亿」这个数字本身是对的**，且已由 MD&A 亏损率 -36% 独立印证。

**2. Q1 2026 Foundry 外部收入 = 1.74 亿美元，现已在 10-Q 原件中直接核到**（此前只有 Tom's Hardware 转述）。Q2 的 2.93 亿亦核到。**两季同口径，外部收入环比 +68.4% 成立。**

**3. 但链条四 §5 证伪条件 3 仍然不触发——Intel 自己说了原因：** 10-Q 明写外部收入增长「**primarily due to Altera's transition to an external customer following the deconsolidation of Altera in Q3 2025**」（主因是 Altera 在 2025Q3 出表后转为外部客户）。这与主文档的既有判断完全一致。**证伪条件 3 要求「剔除 Altera 重分类后仍显著增长」，而这个剔除值 Intel 未披露，仍未知。**

**4. 一个此前四份稿件都没记的数字：外部收入只占分部收入的 5.08%。** 分部收入 57.65 亿里 **55.47 亿是集团内部**（intersegment）。这个比例本身就是「代工商业兑现度」的最好单一指标。

---

## 1. 修正后的 Foundry 分部表（`[A]`，10-Q MD&A 与 Note 2 双处一致）

**来源：** [Q2 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/50863/000005086326000157/intc-20260627.htm)（filed 2026-07-24，期末 2026-06-27），MD&A「Intel Foundry Financial Performance」表 + Note 2 分部表。下载件 MD5 `22a065d2b0d362ad4f5bc0b7595b29ed`；SEC `last-modified: Fri, 24 Jul 2026 10:01:59 GMT`。

**来源：** [Q1 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/50863/000005086326000079/intc-20260328.htm)（filed 2026-04-24，期末 2026-03-28）。下载件 MD5 `91148affbad47cb322b3c7e8b93ec748`。

| 项目（百万美元） | Q2 2026 | Q1 2026 | 1H 2026 | Q2 2025 | 1H 2025 |
|---|---|---|---|---|---|
| **分部收入** | **5,765** | **5,421** | **11,186** | 4,417 | 9,084 |
| 销售成本与经营费用 | 7,854 | 7,858 | 15,712 | 7,585 | 14,572 |
| **营业亏损** | **(2,089)** | **(2,437)** | **(4,526)** | (3,168) | (5,488) |
| **亏损率** | **(36)%** | **(45)%** | **(40)%** | (72)% | (60)% |
| 其中：**外部收入** | **293** | **174** | **467** | **22** | **53** |
| 其中：**内部（intersegment）收入** | 5,472 | 5,247 | 10,719 | 4,395 | 9,031 |
| **外部占分部收入比** | **5.08%** | **3.21%** | **4.17%** | 0.50% | 0.58% |

**⚠️ 三个此前四份稿件都没有的读数（本文新增 `[E]`）：**

1. **外部收入占比从 0.50%（Q2 2025）升到 5.08%（Q2 2026）——翻了 10 倍，但绝对水平仍是 5%。** 用「外部收入增长 12.3 倍」（2.93 亿 vs 0.22 亿）描述会很惊人，用「占比 5.08%」才诚实。**引用时必须同时给两个数。**
2. **Q1 的亏损率（-45%）比 Q2（-36%）更差，即亏损率是在改善的**——这条支持链条四关于「亏损收窄」的方向，但须注意收窄的**主因是收入增长而非成本下降**（Q2 费用 78.54 亿 vs Q1 78.58 亿，基本持平；收入 57.65 亿 vs 54.21 亿）。
3. **内部收入增长的真实驱动被 Intel 明确归因于自有节点爬坡**：intersegment 收入增长「primarily driven by higher wafer volumes from **Intel 18A, Intel 3, and Intel 4** process nodes, which carry higher ASPs relative to predecessor process nodes」。**这是链条四 §1 关于 18A 执行的一个 `[A]` 级证据**——18A 的量确实在上来，且 ASP 高于前代节点。

---

## 2. 三处勾稽全部对上（内部一致性校验）

| 校验 | 算式 | 结果 | 10-Q 披露值 | 判定 |
|---|---|---|---|---|
| Q1 收入 = 1H − Q2 | 11,186 − 5,765 | 5,421 | Q1 10-Q 5,421 | ✅ |
| Q1 亏损 = 1H − Q2 | (4,526) − (2,089) | (2,437) | Q1 10-Q (2,437) | ✅ |
| **Q1 外部收入 = 1H − Q2** | 467 − 293 | **174** | **Q1 10-Q「$174 million in the first three months of 2026」** | ✅ |
| 外部 + 内部 = 分部收入 | 293 + 5,472 | 5,765 | 5,765 | ✅ |
| 亏损率 | (2,089) / 5,765 | (36.2)% | MD&A (36)% | ✅ |

**注意：Q1 外部收入有两条独立路径——① 直接从 Q1 10-Q 读到 1.74 亿；② 由 Q2 10-Q 的 1H 数减 Q2 数导出 1.74 亿。两者完全一致，且与 Tom's Hardware 转述的 1.74 亿亦一致。** 该数字已从 `[B]` 升级为 `[A]`。


---

## 3. Altera 重分类的确切措辞（链条四 §5 条件 3 的判据）

10-Q MD&A 原文（Note 2 与 MD&A 两处一致）：

> "External revenue was $293 million in Q2 2026, up $271 million from Q2 2025, and $467 million in YTD 2026, up $414 million from YTD 2025, **primarily due to Altera's transition to an external customer following the deconsolidation of Altera in Q3 2025**."

> "Intel Foundry revenue increased, and All Other revenue decreased, compared to Q2 2025 and YTD 2025, **primarily due to Altera's transition to an external customer following the deconsolidation of Altera in Q3 2025**."

**关键限定词是 "primarily"（主要），不是 "entirely"（全部）。** 因此：

- **不能说**「外部收入增长 100% 来自 Altera」——Intel 没这么说；
- **也不能说**「剔除 Altera 后仍在增长」——Intel 同样没给这个剔除值。
- **链条四 §5 证伪条件 3 的判定是：仍无法判定（缺 Intel 侧读数）。** 这与主文档和链条四的既有判断一致，本次核验**未推翻任何结论**。

**为什么这个区分重要 `[E]`：** 外部收入同比增加 2.71 亿美元（Q2）。若其中大部分是 Altera 重分类，则真实新客户贡献可能很小。但 Altera 重分类是**一次性基数效应**——它在 **2025Q3 出表后才开始计入外部**，所以 Q2 2026 vs Q2 2025 的同比差额里含首次纳入的基数跳跃；而 **Q2 2026 vs Q1 2026 的环比 +68% 里 Altera 应该已经稳定**（两个季度都已计入）。**这条环比才是更干净的信号，而 Intel 未解释环比增长的原因。这是 Q3 财报最该追问的一点。**

---

## 4. 顺带核到的服务器量价原文（链条二证伪条件的 `[A]` 门槛）

10-Q MD&A 原文（DCAI 部分）：

> "DCAI revenue increased $2.3 billion from Q2 2025 and $3.2 billion from YTD 2025, primarily driven by higher server revenue, which increased $2.0 billion in Q2 2026 and $2.7 billion in YTD 2026 due to **ASP increases of 48% and 38%**, respectively. The majority of the increase in server ASPs was driven by a **higher mix of premium products sold** in Q2 2026 and YTD 2026, with demand-based pricing actions contributing to a lesser extent, in part to offset higher input costs. **Server volume increased 9%** compared to Q2 2025 and **2%** compared to YTD 2025, primarily driven by higher hyperscaler demand."

> "Market demand exceeded our available product supply in Q2 2026 and YTD 2026 due to internal and industry-wide constraints... We **expect these constraints to ease over the second half of 2026**."

**⚠️ 最后一句是主文档和链条二都没有的 `[A]` 级前瞻：Intel 自己说供给约束将在 2026 下半年缓解。** 这直接关系到：

- **链条二**「缺货 → 价格 → 利润」的时序判断——若 2H26 缺货缓解，ASP 的组合红利（premium mix）能否持续就成了问题；
- **链条三**「Intel 因交不出货而丢份额」的持续性——**若 2H26 约束确实缓解，链条三 §5 的证伪条件 1（份额连续两季回升）就有了机制基础。**

**建议补入主文档观察字段。**

客户端对照（同源）：客户端收入 77 亿，**ASP +27%**（YTD +22%），**出货量 -8%**（YTD -10%），「majority of the increase in ASPs was driven by a higher mix of premium products sold」。



---

## 5. 建议的改稿（待用户确认后执行，本轮未动原稿）

| # | 文件 | 位置 | 现状 | 建议改为 |
|---|---|---|---|---|
| 1 | `README.md` | 结论段 | 「Foundry 同季 **20.89 亿美元营业亏损**，外部收入仅 2.93 亿美元」 | 数字本身正确，**但须补分部收入 57.65 亿与亏损率 -36%**，否则读者会误以为是收入额（正是本轮误读的来源） |
| 2 | `chain-4-*.md` | 结论 1 / §1.1 | 同上，且未列分部收入 | 同上，并补「外部收入占分部收入 **5.08%**，其余 95% 为集团内部」 |
| 3 | 三份稿件 | 观察字段 | 「Intel Q3 财报（**2026-10-22**）」 | **2026-10-29**（CNBC / stockanalysis / IBTimes 三源一致） |
| 4 | `chain-4-*.md` | 结论 6 / §3.2 | 「卖方共识目标价 $115.03 **低于** 9-25 市价 $123.03」 | 10-09 共识 **$118.05** vs 10-08 收盘 **$107.08** = **+10.25%**；改为「现价已回落至共识目标价下方约 10%」 |
| 5 | `chain-4-*.md` | §1.2 | 14A 时点仅一组（2027H2/2028） | 补列三套口径，含 **Tan 本人 2026-05 在 JPM 大会说过的 2028/2029** |
| 6 | `README.md` / `chain-2-*.md` | 观察字段 | 无 | 补入 §4 的 `[A]` 级前瞻「expect these constraints to ease over the second half of 2026」 |

**本文不构成投资建议。**

---

## 6. 来源与边界

| ID | 来源 | 访问状态 | 本稿用法 |
|---|---|---|---|
| INTC-Q2-10Q-SEC | [Q2 2026 10-Q（SEC EDGAR 原件）](https://www.sec.gov/Archives/edgar/data/50863/000005086326000157/intc-20260627.htm)，filed 2026-07-24 | `PUBLIC_NO_AUTH`，MD5 `22a065d2…` | 分部表、外部收入 2.93/4.67 亿、Altera 措辞、服务器与客户端量价、2H26 约束缓解前瞻 |
| INTC-Q1-10Q-SEC | [Q1 2026 10-Q（SEC EDGAR 原件）](https://www.sec.gov/Archives/edgar/data/50863/000005086326000079/intc-20260328.htm)，filed 2026-04-24 | `PUBLIC_NO_AUTH`，MD5 `91148aff…` | **Q1 外部收入 1.74 亿（`[A]` 级，此前缺）**、Q1 分部收入与亏损 |

**边界：**

- **本文只核了 Intel Foundry 分部的收入/亏损/外部收入三条线，以及服务器与客户端的量价原文。** 未核：14A 客户状态、PDK 时点、8 月增发最终结算股数、Q2 经营现金流与资本开支的报表原值（链条四 §5 已列为待核项，本轮仍未闭合）。
- **10-Q 是静态归档**（Q2 的 SEC `last-modified` 为 2026-07-24），不含 7 月之后任何变化，亦不含 Q3 数据。
- **「内部收入」= 分部收入 − 外部收入，是本文的减法 `[E]`**，Intel 未单独披露该行（仅披露 intersegment 增长的定性原因；勾稽：内部同比 +10.8 亿 + 外部同比 +2.71 亿 = 分部收入同比 +13.48 亿，一致）。
- 本地工作件：`/tmp/intc-q2-10q.htm`、`/tmp/intc-q1-10q.htm`（原件）与同名 `.txt`（剥标签全文）。**这些在 `/tmp`，不在库内，重启即失；如需长期保留应另行归档。**
