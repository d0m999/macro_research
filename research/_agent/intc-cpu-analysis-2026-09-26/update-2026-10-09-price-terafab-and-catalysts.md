# 增量核验（2026-10-09）：价格锚失效、Terafab 事件、以及链条四的证伪条件首次被实时检验

**核验截点：2026-10-09（美股 10-08 收盘后）。** 上一版核验截点为 2026-10-05，四份稿件（主文档、链条二、链条三、链条四）的结论基准价格均为 **2026-09-25 收盘 $123.03**。本文只记录 10-05 → 10-09 之间发生的变化及其对既有结论的影响。

**按本仓惯例不改原稿**（`复核不改原稿，改动单列`）：链条二/三/四正文与 `fact-check-2026-10-05.md` 均未改动；本文是新增的结论单列件。基线 MD5 与行数见 §10。

**证据标记：** `[A]` 公司披露 `[B]` 第三方机构/媒体 `[C]` 渠道与行情报价 `[D]` KOL 个人判断 `[E]` 本文推算。

---

## 结论（先说会改变判断的五件事）

**1. 链条四唯一「能单独推翻本文结论」的事件（§5 证伪条件 1：14A 取得首个已承诺外部客户）在 10 月第一周被真实触发了一次，但触发方向是反的——客户没来，竞争对手进场了。** 10-05 Elon Musk 公开确认 TSMC 正参与 Terafab 洽谈，INTC 当日跌 4%；10-07 Musk 澄清「TSMC 最多只能转租 Terafab 的一部分场地，除此之外没有别的」；10-08 Intel CEO 陈立武在东京确认 Intel 仍是 Terafab 开发伙伴。**结论未变（已承诺客户仍为 0），但链条四原先把 Tesla 定位为「制程技术授权而非代工订单」，这次事件把这一点从推断变成了双方公开口径的既成事实**——见 §2。

**2. 「卖方目标价低于现价」这一结论已经反转，必须改写。** 10-08 收盘 **$107.08**，49 位分析师共识目标价 **$118.05**（评级 Buy），**现价低于目标价 10.25%**。链条四 §3.2 与结论 6 原写「上行空间已被定价」，此刻在数字上已不成立。同时 Mizuho 把 INTC 目标价从 $92 上调至 **$114**（维持 Neutral）。

**3. 价格锚整体失效：四份稿件共用的 $123.03 已低于市价 13.0%。** 按 10-08 收盘重算，市值约 **5,630 亿美元**、P/S 约 **9.9 倍**（原 12.3 倍）。

**4. ⚠️ 三份稿件（链条三 §3、链条四 §3、主文档）都把 Intel Q3 财报日写成 2026-10-22，这是错的。** 三个独立行情/日历源给的都是 **2026-10-29**（CNBC「EVENTS Earnings Date 10/29/2026」、stockanalysis「Earnings Date Oct 29, 2026」、IBTimes「Earnings are scheduled for Oct. 29」）。唯一给 10-22 的 theta.md 页面自己声明「last refreshed on August 7, 2026, beyond the 7-day freshness window」。**观察日历须整体后移一周。**

**5. 10-08 的 -5.34% 不是 Intel 的事，别记在代工头上。** 当日 FT 披露 OpenAI 年化收入接近 **500 亿美元**而非此前广为报道的 **680 亿**（净额 vs 含合作伙伴毛额的口径差），Nasdaq 跌 1.25%（8 月中以来最差单日）。INTC -5.3% / NVDA -2.9% / ORCL -5.5% / CRWV -8% / AMD -4% / AVGO -4% / SMCI ≈-5%，另有 Brent +4.2%、10Y ≈5.3%。**这是全板块 AI 折价 + 宏观，不是个股消息。**

> **一句话：链条四的结论方向全部未被推翻，但它的两条支撑腿（估值锚、Terafab 定位）都在这一周被改写了性质；链条三拿到了第一个「Intel 在新增蛋糕里有份」的量化答案；链条二的核心变量②（存储涨价拐点）仍等 Intel Q3 毛利率这一个数据点。**

---

## 1. 价格与估值锚：$123.03 已经不是基准

`[C]` stockanalysis.com（数据源 S&P Global Market Intelligence，逐日收盘）与 CNBC 交叉一致：

| 日期 | 收盘 | 当日 | 备注 |
|---|---|---|---|
| 09-25 | **123.00** | -3.45% | 四份稿件的锚（README 记 $123.03，差 0.03，来源舍入） |
| 09-28 | 116.03 | -5.67% | |
| 09-30 | 120.23 | +3.71% | 美光 FY26Q4 公布日 |
| 10-02 | 119.33 | -0.56% | 链条四补注用过的时点 |
| 10-05 | 116.19 | -2.63% | **Terafab/TSMC 消息** |
| 10-06 | 112.50 | -3.18% | |
| 10-07 | 113.12 | +0.55% | Musk 澄清「仅转租」+ 陈立武表态前夕 |
| **10-08** | **107.08** | **-5.34%** | OpenAI 收入报告 + 宏观 |

**派生量重算 `[E]`（本文算术，未与同业横向比较）：**

| 量 | 10-25 锚 | 10-08 重算 | 变化 |
|---|---|---|---|
| 市值 | ~6,501 亿（52.85 亿股） | **约 5,630 亿**（stockanalysis 记 5,626.5 亿；CNBC 记 5,659.25 亿，用 52.9 亿股） | 股本口径 5.25–5.29 亿**十亿**股区间，见下 |
| P/S（TTM 收入 570.3 亿） | ~12.3x | **约 9.9x** | 收入分母已从 FY2025 的 528.5 亿升到 TTM 570.3 亿，是两件事同时发生 |
| 距 52 周高 $142.35（06-30-26） | — | **-24.8%** | |
| 距 52 周低 $32.89（11-21-25） | — | **+225.6%** | |
| YTD | 链条四记 +212% | **+190.19%**（Yahoo，截至 10-08） | 见下方 ❓ |

**⚠️ 三个口径坑（引用前必须声明）：**

1. **链条四的 P/S 12.3 倍用的是 FY2025 全年收入 528.5 亿，不是 TTM。** 现在的 TTM 收入是 **570.3 亿**（+7.9%）。所以 P/S 从 12.3 → 9.9 的下降里，**价格下跌贡献约 1.6 倍（-12.9%）、收入分母增长贡献约 0.8 倍（-7.3%）**——不是纯价格效应，两者比例约 2:1。
2. **股数口径仍然没闭合。** chain-4 用的是招股书「发行时预计 52.85 亿股」；stockanalysis 记 5.25B、CNBC 记 5.29B。**8 月增发的最终结算股数仍未回 8-K 原件核到**（链条四 §5 已列为待核项，本轮仍 ❓）。市值因此有约 40 亿美元的来源差。
3. **❓ YTD 基准无法自洽。** Yahoo 的 +190.19%（截至 10-08）隐含 2025 年末收盘 ≈ $36.90；链条四的 +212%（按 $123.03）隐含 ≈ $39.4。两个来源用了不同基准，**本轮未解**。凡涉及「年内涨幅」的表述一律改为直接引用价格水平，不要引用百分比。

---

## 2. Terafab 事件：链条四的支柱从「技术授权」推断变成双方公开口径的既成事实

这是 10-05 → 10-09 唯一实质性的产业事件。链条四 §1.1 原表把 Tesla/Terafab 放在「**已确认但非代工合约**——制程技术授权，对方自建自运营工厂」一行，当时只有 [B] 推断。**本轮事件把它变成了可引用的公开表述。**

**时间线（全部 `[B]`，媒体转述，未回 SEC 原件）：**

| 日期 | 事件 | INTC 反应 |
|---|---|---|
| 2026-04 | Intel 以**开发伙伴**身份加入 Terafab；项目预期以授权 **14A 节点**为制造基础 | — |
| 2026-10-05（周一） | Musk 确认 TSMC 可能在 Terafab 项目中参与 | **-2.63%**（收 $116.19） |
| 2026-10-06（周二） | 报道扩散；Musk 称 TSMC 将**自建并运营**一座专供 Tesla/SpaceX/xAI 的 fab | **-3.18%**（收 $112.50） |
| 2026-10-07（周三） | Musk 在 X 澄清原话：**"Maybe TSMC subleases part of the Terafab if they want, but nothing more than that."**（TSMC 最多只能转租一部分场地，除此之外没有别的）；同时称其公司将**自行建造并运营** Terafab。他还称与 TSMC 的讨论「just discussions, but something may come of it」 | **+0.55%**（收 $113.12） |
| 2026-10-08（周四） | 陈立武在 Intel 日本 50 周年活动（东京）表示 **Intel 仍是 Terafab 的开发伙伴**——这是 Intel 在 TSMC 消息后首次直接确认未被排除 | **-5.34%**（但当日主因是 OpenAI 报告，见 §3） |

**对链条四 §1.1 的三条修正：**

1. **「自建自运营」现在是 Musk 亲口说的，不再是本文推断。** Quartz（2026-10-07）标题即「Elon Musk says his companies will build and run Terafab, ruling out TSMC」。TweakTown（10-08）同样记「its own team will build and operate the chip complex」。**这把链条四「Tesla 的 14A 关系不是 Intel 的晶圆代工订单」从推断升级为双方公开口径一致的事实**——链条四该结论因此更稳，而非更弱。
2. **⚠️ 但「转租」这个说法本身把 Intel 的暴露面弄模糊了，方向不利。** Tom's Hardware（Anton Shilov）指出概念问题：如果 TSMC 自装机台、自带工艺与生产管理，Terafab 只出土地/壳体/基础设施，那称其为「转租」是**低估**了这实际是「嵌在 Terafab 园区内的 TSMC 厂」；反之若 Terafab 提供机台与基础设施、TSMC 只负责运营，那就**更接近** Musk 表面上否认的那种 TSMC 运营介入。**两种解读都指向：Intel 14A 在 Terafab 的排他性下降了。** 这是本轮唯一实质性的负面。
3. **❓ 有一处本文未能核到原话。** Invezz（10-08）称「Musk 和 Intel 领导层都说了 Intel 会建造并运营这座 fab（"ZERO doubt"）」。**该 "ZERO doubt" 措辞未在任何可访问来源核到**（Benzinga/MarketWatch/Morningstar 均 401/403）。Quartz 与 TweakTown 的转述恰好相反——Musk 说的是**他的公司**建造运营。**该措辞不予采用**，引用时只用 Quartz/TweakTown 可核的版本。

**Terafab 的规模背景（`[B]`，供判断权重）：** 规划在 Tesla 德州园区建两座厂，一座供车用芯片与人形机器人，一座支持天基 AI 数据中心；公开表述的终极目标是**年产能一太瓦算力**，把逻辑制造、存储、封装、测试与掩模集中到一处。**这个体量意味着它不会是一个边缘客户，但也意味着它自建自运营，Intel 拿到的是授权费而非代工收入。**

---

## 3. 10-08 大跌的归因：全板块 AI 折价，不是 Intel 个股事件

**链条四 §3 若把 10-08 的 -5.34% 读成「市场在给代工叙事重新定价」，会犯归因错误。**

`[B]` SiliconANGLE（2026-10-08 20:44 EDT 更新）：FT 当日报道，OpenAI 在投资者演示中给出的**年化收入接近 500 亿美元**，远低于两个月前广为报道的 **680 亿**；差额源于口径——此前 680 亿**含合作伙伴的毛收入**（为与 Anthropic 可比），新数字基于**净收入**。OpenAI 同时给出 Q3 年化收入运行率 **+77%**、企业业务运行率 **+107%**。OpenAI 未回应 FT。

**同日板块反应（`[B]`）：** Nasdaq **-1.25%**（8 月中以来最差单日）、S&P 500 -0.5%；ORCL **-5.5%**、INTC **-5.3%**、CRWV **-8%**、AMD **-4%**、AVGO **-4%**、SMCI 约 -5%、NVDA -2.9%。宏观同时施压：Brent **+4.2%**、10Y 约 **5.3%**（Invezz 10-08）。

**读法 `[E]`：** INTC 当日跌幅（-5.34%）与 CRWV/ORCL 同级、大于 NVDA（-2.9%），与其 **beta 2.23**（stockanalysis）一致——**这是高 beta 在全板块冲击下的正常放大，不是代工叙事的独立重定价。** 链条四 §3 的「政策期权定价」结论因此不受本次跌幅影响。**10-06–10-07 的两次下跌（Terafab 消息）才是与 INTC 基本面相关的部分。**

---

## 4. 卖方共识：目标价已经高于现价，链条四结论 6 必须改写

`[C]`/`[B]` stockanalysis（49 位分析师，截至 10-09）、Yahoo Finance（36 位对本季、43 位对全年）、Mizuho 报告转述：

| 口径 | 数值 | 时点 |
|---|---|---|
| 共识评级 | **Buy**（49 位） | 10-09 |
| 共识目标价 | **$118.05** | 10-09 |
| 距 10-08 收盘 $107.08 | **+10.25%** | — |
| Mizuho | **$114**（自 $92 上调），维持 **Neutral** | 10-06 前后 |

**对链条四 §3.2 与结论 6 的修正（本文主张的写法）：**

- **原写**：「不同数据商的目标价区间为 $110–$118.67，均不高于现价但差距在 0.6%–7.6% 之间，结论应表述为『上行空间已被定价』」。
- **现况**：$118.05（10-09 共识）对 $107.08（10-08 收盘）为 **+10.25%**。**「上行空间已被定价」在数字上不成立，应改为「现价已回落至卖方共识目标价下方约 10%」。**
- **注意这是价格下跌造成的，不是分析师变乐观**：`fact-check-2026-10-05.md` §七 关于「目标价低于现价」的降级结论在 10-09 已过时，但其方法论提醒（「不能写成卖方不认同这个价格」）依然有效，只是方向反了。
- **⚠️ 一致预期的隐含含义值得单独记**：Yahoo 显示本季（9/2026）一致收入 **164.3 亿**、EPS **$0.39**；公司 Q3 指引为收入 **158–168 亿**、GAAP EPS **$0.31** / non-GAAP **$0.38**。**一致收入预期 164.3 亿落在指引区间内偏上沿**，即市场按指引上沿定价。链条二的「量价拆分」证伪条件在 Q3 有明确的数值门槛了。

---

## 5. 链条三的新输入：Mizuho 首次给出 agentic CPU 的 TAM 拆分，Intel 被列为四家之一

这是链条三缺了很久的东西——**「新增蛋糕有多大」的量化拆分**，而不是只有份额此消彼长。

`[B]` Mizuho（Vijay Rakesh 团队，2026-10-06 前后投资者报告，经 Invezz/CNBC/TheFly 转述）：

| 细分 | 2030E TAM | 4 年 CAGR |
|---|---|---|
| **Agentic AI CPU** | **约 800 亿美元** | **约 +123%** |
| Head-node CPU | 约 680 亿美元 | 约 +61% |
| 传统 CPU | 约 600 亿美元 | 约 **+2%** |
| **服务器 CPU 合计** | **约 2,090 亿美元** | **约 +32%** |

- 该 2,090 亿**低于** AMD 自设的 >2,200 亿目标，Mizuho 称自己的口径更保守。
- **Agentic AI 驱动 CPU/DRAM/NAND 各自增长至占总市场的 22–30%（按出货 bit 计）。**
- **Agentic AI CPU 占总服务器 CPU 的比例：今天约 4% → 2030E 约 30%。**
- **四家被点名为 agentic AI 负载的前沿处理器：Arm 的 AGI CPU、AMD 的 Venice、NVIDIA 的 Vera、Intel 的 Diamond Rapids。**
- Mizuho 同步把 INTC 目标价从 $92 上调至 **$114**（维持 Neutral），AMD 从 $580 上调至 **$705**。

**对链条三的意义 `[E]`：**

1. **链条三 §1 的「需求池」表第一次有了量级。** 原表只有定性分类（PC 客户端／通用服务器／AI 主机与编排／先进代工），Mizuho 把「AI 系统的主机、编排及数据处理」这一池子单独量化为 **agentic CPU 800 亿 + head-node 680 亿**，并指出**传统 CPU 600 亿的 CAGR 只有 2%**——这正好量化了链条三 §2.3「客户端是现金流基本盘但不是增长源」的说法。
2. **Intel 被列入四家前沿方案之一，但这是「有份」不是「占优」。** 四家里 Intel 的 Diamond Rapids 与 Arm AGI CPU、AMD Venice、NVIDIA Vera 并列——**它既没被排除在新增蛋糕之外（利好链条三的悲观读法），也没拿到任何份额承诺（不支持链条四的乐观读法）。**
3. **⚠️ 这是单一投行测算（`[B]`），且 Intel 自身的 Diamond Rapids 未发布量产数据。** 不能据此推算 INTC 收入。它改变的是**链条三的框架完备度**，不是任何结论。

---

## 6. 代工侧的新证据：四条，方向不一致，但共同指向「封装先于晶圆」

### 6.1 Google 的 3M+ TPU 订单——是 EMIB 封装，不是 14A 晶圆

`[B]` Tom's Hardware（引 The Information 报道，2026-06-08；Reuters 同日另有报道，401 无法访问原文）：Google  reportedly 预订 Intel 的 **EMIB 先进封装**，为 **2028 年 300 万颗以上 TPU** 做封装；SK hynix 正在测试 Intel 的 EMIB 封装以整合 HBM。

**⚠️ 三条口径警告（这条极易被误读成「Intel 拿到 14A 大客户」）：**

1. **这是封装（packaging），不是晶圆制造（wafer foundry）。** 链条四 §1.1 的「已承诺（committed）外部客户 = 0」指的是 **14A 晶圆代工**，本条**不构成对该结论的证伪**。
2. **双方均未确认。** Intel 与 Google 都未公开确认；Tom's Hardware 自己列出质疑：不确定是 2027 还是 2028 的产品、或仍停留在评估阶段。
3. **❓ Reuters 那篇（Google 与 NVIDIA 考虑 Intel 作为备选制造商）原文无法访问**（401），本轮仅据标题与二手转述，不参与计算。

**但它确实支持链条四 §5 证伪条件 6**（「EMIB-T 在 2027H2 如期放量并达约 40% 毛利率 → 封装先于晶圆兑现」）——**这是该条件的第一个独立外部佐证。**

### 6.2 CFO Zinsner：外部代工会议的性质变了

`[B]` Zinsner 在 Deutsche Bank 2026 技术大会炉边对话（2026-08-26）：14A 的缺陷密度下降速度**为 22nm 时代（2012）以来最快**；外部代工客户的会议已**从技术审阅转向问「我能预订多少产能」**。

`[B]` 同一场合：EMIB-T 相较晶圆制造有三个优势——**收入来得更快**（2027H2 开始爬坡，比 14A 晶圆规模收入早约一年）、**毛利更高**（约 **40%**）、**资本密集度更低**。

**⚠️ 缺陷密度 ≠ 良率**（Tech Times 明确提示）：缺陷密度是每单位晶圆面积的缺陷数，是早期开发健康度信号；芯片良率还受**芯片面积**非线性影响——面积翻倍，缺陷落在关键处的概率指数上升。且 22nm 时代的检测设备远不如现在，**Intel 今天定义的「缺陷」可能包含 2010 年根本检不出的物理特征**，跨期比较的可比性有限。

### 6.3 Foundry 外部收入序列：链条四 §5 证伪条件 3 有了环比对照

`[B]`/`[A]` 交叉：

| 季度 | Foundry 分部收入 | Foundry 营业亏损 | **外部收入** |
|---|---|---|---|
| FY2025 全年 | 178 亿美元 | **-103 亿美元** | — |
| Q1 2026 | 54 亿美元 | -24 亿美元 | **1.74 亿美元** |
| **Q2 2026** | 20.89 亿美元（主文档口径） | **-20.89 亿美元** | **2.93 亿美元** |

**⚠️ 上表有两处口径冲突，本文未能闭合：**

1. **Q2 2026 的分部收入与营业亏损被记为同一个数字（20.89 亿），这在算术上意味着 100% 亏损率，明显是转述串行**——主文档与链条四都沿用了这个写法。**引用 Q2 分部收入时应回 10-Q 分部表原件复核。**
2. **❓ Q1 的外部收入 1.74 亿来自 Tom's Hardware 转述（`[B]`），Q2 的 2.93 亿来自 10-Q（`[A]`）。** 若两者同口径，则外部收入**环比 +68%**——这会让链条四 §5 证伪条件 3（「剔除 Altera 会计重分类后仍实现环比显著增长」）**部分触发**。但主文档明确说 Q2 外部收入增长**主要来自 Altera 从内部转为外部客户的会计边界变化**，所以**是否「剔除后仍增长」仍然未知**。**这是 Q3 财报最值得看的一个数字。**

### 6.4 Applied Materials × Intel 合作（2026-10-07）

`[B]` Applied Materials 官方新闻稿 + GlobeNewswire + BusinessWire（后两者本轮 403，官方 press release 页亦 403，仅据标题与 DIGITIMES 转述）：双方合作加速 AI 芯片创新，方向是**互连扩展（interconnect scaling）与 Foveros 3D**，地点在 Applied 硅谷 EPIC Center 与 Intel 俄勒冈 R&D 园区，目标是下一代晶体管、互连与先进封装。

**读法 `[E]`：** 这是设备厂/代工厂的联合开发，**不是客户订单**，对链条四「已承诺客户 = 0」无影响。它的价值在于印证 6.2 的方向——**Intel 把代工突破口押在先进封装上**，而非 14A 晶圆。

---

## 7. ⚠️ 财报日期：三份稿件都写的 10-22 是错的，应为 10-29

| 来源 | 给的日期 | 可靠性 |
|---|---|---|
| CNBC「EVENTS Earnings Date」 | **10/29/2026** | 行情终端日历 |
| stockanalysis.com「Earnings Date」 | **Oct 29, 2026** | 数据源 S&P Global |
| IBTimes（2026-10-09 文章） | **Oct. 29** | 明确写「The Oct. 29 report is the next number that is not a headline」 |
| theta.md | Oct 22, 2026 | ⚠️ **页面自述 last refreshed August 7, 2026，超出其 7 天新鲜度窗口** |

**受影响的三处：** 链条三 §7 结语与 §6 观察字段（写「Intel Q3 财报（2026-10-22）」）、链条四 §5 观察字段（同）、主文档（同）。

**这是本轮唯一一处三份稿件共有的实质错误。** 三个独立源一致指向 10-29，而唯一支持 10-22 的来源自认过期。**观察日历须整体后移 7 天**，链条二的美光→Intel 毛利率证伪条件也因此多出一周等待。

---

## 8. 14A 节点时点：三个来源三套说法，本轮无法闭合

| 来源 | 风险生产 | 量产（HVM） |
|---|---|---|
| Q2 2026 prepared remarks（经 Tech Times 引） | **2027H2**（内部产品） | **2028** |
| Piper Sandler 经 Wccftech 引（2026-09-18，称「本周向 Intel 重申」） | **2027Q2** | **2028Q1** |
| Lip-Bu Tan 在 J.P.Morgan 大会 + Cramer 采访（2026-05，经 Wccftech 引） | **2028** | **2029** |

**⚠️ 这是本轮发现的第二处实质性不一致，且比链条四原稿记的更乱。** 链条四 §1.2 用的是「风险生产 2027 H2 / HVM 2028」一组，与 Q2 prepared remarks 一致；但 **Tan 本人在 2026-05 公开说过 2028/2029 一套更晚的时点**（同时说与 TSMC A14 时间接近），而 9 月又经 Piper Sandler 给出 2027Q2/2028Q1 的更早时点。

**推论 `[E]`：** 三种可能——① Tan 5 月说法与 9 月说法是不同产品口径（外部 vs 内部客户）；② 时点确实提前了；③ 转述有误。**本轮无足够信息判定。** 但无论哪种，链条四 §1.2 的核心推论（「14A 规模化代工收入在 2028 年之前不会出现」）**在最新口径下反而更稳**——因为唯一支持「更早」的 Piper Sandler 口径也是 2028Q1 量产。

**PDK 0.9 时点（链条四 §5 待核项）：** Tan 在 2026-05 JPM 大会上称 14A 的 0.5 PDK 已于「今年早些时候」对外发布，**0.9 PDK 预计「around October 2026」对外发布**（内部客户更早），并称之为 14A 的「**Holy Grail**」（圣杯）。Tech Times（2026-08-28）同样记「expected in October 2026」。

**⚠️ 今天是 10-09，即 PDK 0.9 原定时点就在本月内，本轮尚未核到「已发布」的确认。这是 10 月内就该盯的一个硬事件。** 一旦发布，14A 的正式设计周期才真正开启（链条四 §1.2 的推论才落地）。

**同时出现的两个新节点名：** Tan 在 2026-05 首次点名 **10A（1.0nm）与 7A（0.7nm）** 已进入工作，但公司**尚未发布 roadmap 或时点**；对照 TSMC 估计 A10 约 2031、A7 约 2034。这补充了链条四 §1 关于「长期业务」的论述，但不改变任何结论。

---

## 9. 链条二的状态：仍只差一个数据点

`chain-2-micron-fy26q4-verify-2026-10-04.md` §2 条件 1 需要「美光毛利率创新高 + DRAM 合约价 1Q27 仍为正 + **Intel 毛利率环比下滑**」，前两项已满足（美光 Q4 GAAP 毛利率 86.8% 创新高；Q4 DRAM ASP 约 +7~9%，增速缩窄），**唯一缺的是 Intel Q3 毛利率**——现在要等 **10-29**（不是原记的 10-22）。

**本轮新出现的反向证据 `[E]`：** 10-08 大跌的直接触发是 OpenAI 年化收入被下修至约 500 亿（毛额/净额口径差）。链条二 §2 漏斗 5「$/token 天花板」的机制因此得到一次**市场层面的检验**：当终端付费能力被质疑时，**整条链的定价权假设同时被折价**（CPU/GPU/存储/云厂无差别下跌）。这不是证伪链条二，而是给它的第 5 道漏斗加了一个观察窗口——**若 Q3 财报显示云厂 capex 指引下修，链条二的「内存先兑现、CPU 后兑现」时序判断需要重估。**

---

## 10. 来源记录与边界

### 本轮新增来源

| ID | 来源 | 时点 | 访问状态 | 本文用法 |
|---|---|---|---|---|
| PX-STOCKANALYSIS | [stockanalysis.com INTC history](https://stockanalysis.com/stocks/intc/history/)，数据源 S&P Global Market Intelligence | 截至 10-08 收盘 | `PUBLIC_PAGE_VALIDATE` | 逐日收盘价、市值、股数、beta、52 周区间、49 位共识 |
| PX-CNBC | CNBC INTC quote | 10-08/10-09 | `PUBLIC_PAGE_VALIDATE` | 股数 5.29B、市值、**财报日 10/29**、EPS/毛利/ROE TTM |
| PX-YAHOO | Yahoo Finance INTC analysis | 10-09 | `PUBLIC_PAGE_VALIDATE` | 一致预期收入/EPS（36 位）、YTD +190.19%、同业当日涨跌 |
| TERA-QZ | [Quartz 2026-10-07](https://qz.com/elon-musk-terafab-tsmc-build-run-100726) | 10-07 | `PUBLIC_PAGE_VALIDATE` | **Musk 原话「subleases part of the Terafab」**、自建自运营 |
| TERA-TWEAK | [TweakTown 2026-10-08](https://www.tweaktown.com/news/113960/intel-ceo-lip-bu-tan-confirms-role-in-elon-musks-terafab-despite-tsmc-talks/index.html) | 10-08 | `PUBLIC_PAGE_VALIDATE` | 陈立武东京表态、Terafab 两厂规划、14A 授权基础 |
| TERA-TH | [Tom's Hardware「Musk rejects rumors…」](https://www.tomshardware.com/tech-industry/semiconductors/musk-rejects-rumors-of-tsmc-takeover-of-terafab-intel-reaffirms-14a-node-deal-as-musk-floats-cleanroom-sublease) | 10-07/08 | `PUBLIC_PAGE_VALIDATE` | 「sublease」的概念问题分析（Anton Shilov） |
| TERA-DIGI | [DIGITIMES 2026-10-08](https://apps.digitimes.com/news/a20261007VL218.html) | 10-08 | `PUBLIC_PAGE_VALIDATE`（**付费墙，仅标题与导语**） | 标题「Musk keeps Terafab in-house, shifting execution risk onto his own companies」 |
| OAI-FT-SA | [SiliconANGLE 2026-10-08](https://siliconangle.com/2026/10/08/ai-stocks-crumble-on-report-that-openais-annualized-revenue-is-much-lower-than-previously-believed/) | 10-08 20:44 EDT | `PUBLIC_PAGE_VALIDATE` | FT 报道的 OpenAI 500 亿 vs 680 亿口径差、板块当日反应 |
| OAI-INVEZZ | [Invezz 2026-10-08](https://invezz.com/news/2026/10/08/why-are-intel-and-amd-stocks-plunging-on-thursday/) | 10-08 | `PUBLIC_PAGE_VALIDATE` | Brent +4.2%、10Y 5.3%、**Mizuho agentic CPU TAM 拆分**、Mizuho 目标价 |
| MIZ-AMAT | GlobeNewswire / BusinessWire / DIGITIMES 转述 | 10-07 | `PUBLIC_PAGE_VALIDATE`（**正文 403，仅标题+转述**） | Applied Materials × Intel：互连扩展 + Foveros 3D |
| PS-14A-WCCF | [Wccftech 2026-09-18](https://wccftech.com/intels-14a-process-is-currently-being-evaluated-by-amazon-apple-amd-google-tesla-microsoft-nvidia-and-qualcomm-according-to-piper-sandler/) | 09-18 | `PUBLIC_PAGE_VALIDATE`（二手转述 Piper 报告） | **8 家评估 14A**、14A 时点 2027Q2/2028Q1、TSMC 满载至 2028 |
| TAN-JPM-WCCF | [Wccftech 2026-05-20](https://wccftech.com/intel-ceo-lip-bu-tan-threatens-to-fire-anyone-whose-chip-exceeds-b0-stepping-14a-pdk-0-9-october-2026/) | 05-20 | `PUBLIC_PAGE_VALIDATE` | **PDK 0.9 = October 2026**、「Holy Grail」、14A 时点 2028/2029、10A/7A |
| GOOG-EMIB-TH | [Tom's Hardware「Google reportedly books Intel…」](https://www.tomshardware.com/tech-industry/google-reportedly-books-intel-for-more-than-3-million-tpus-in-2028) | 06-08 前后 | `PUBLIC_PAGE_VALIDATE`（引 The Information） | 3M+ TPU 的 **EMIB 封装**订单、SK hynix 测试、**Q1 外部收入 1.74 亿**、FY2025 分部亏损 103 亿 |
| ZINS-DB-TT | [Tech Times 2026-08-28](https://www.techtimes.com/articles/325890/20260828/intel-14a-defect-drop-rivals-22nm-era-customers-now-asking-capacity-not-data.htm) | 08-28 | `PUBLIC_PAGE_VALIDATE` | Zinsner 炉边对话、EMIB-T 2027H2/约 40% 毛利、Tesla 唯一确认、缺陷密度≠良率 |

### 本轮未能访问的来源（明确 ≠ 不存在）

| 来源 | 结果 |
|---|---|
| Benzinga「Lip-Bu Tan Says Company Will Keep Working on Terafab」 | 403（正文为空，仅拿到标题） |
| MarketWatch / Morningstar 同题 | 403 / 401 |
| Reuters（Terafab/TSMC；Google-Nvidia 考虑 Intel 备选） | 401 |
| Applied Materials 官方 press release / BusinessWire | 403 / 403 |
| TipRanks（全部文章） | 403 |
| Intel IR 页 / newsroom | 404 / 无可解析的季度日期 |
| The Information 原文（Google EMIB 订单） | 付费墙 |

### 基线 MD5（开工时记录，本轮未改原稿）

| 文件 | MD5 | 行数 |
|---|---|---|
| `chain-2-price-margin.md` | `eef2c67d7480d8384da9509e655de342` | 249 |
| `chain-2-micron-fy26q4-verify-2026-10-04.md` | `1ed01d56aa4e85068f0a3cb7845ea34a` | — |
| `chain-3-architecture-share.md` | `4276e5335ee1354e015d1f6f7a693e07` | 179 |
| `chain-4-foundry-dilution-valuation.md` | `ed043e7df5d0039ac23f106587203112` | 224 |
| `fact-check-2026-10-05.md` | `bb7349afaf614aa3f3cb1cedb8108ba7` | — |
| `README.md` | `fe4f4a7bf5c6dcc4166be6556ec912e9` | 110 |

改前备份：`/tmp/intc-backup-2026-10-09/`（全部 7 份 md）。

---

## 11. 对四条链条的影响汇总（本文归纳 `[E]`）

| 链条 | 结论方向 | 本轮变化 |
|---|---|---|
| 一（需求） | **不变** | Mizuho 给了 TAM 量级（§5），未改方向 |
| 二（缺货→价格→利润） | **不变，仍差一个点** | 唯一缺口仍是 Intel Q3 毛利率；日期 10-22 → **10-29** |
| 三（架构与份额） | **不变，框架补全** | 首次拿到 agentic CPU TAM 拆分；Intel 被列为四家前沿方案之一（§5） |
| 四（代工/摊薄/估值） | **方向不变，两条腿改写** | ① Terafab「自建自运营」从推断变公开事实，但「转租」使 14A 排他性下降（§2）；② 目标价已高于现价，结论 6 须改写（§4） |

**四条链条的核心判断在本轮均未被推翻。** 需要改写的具体语句有 3 处：财报日期（3 份稿件）、链条四结论 6 的估值表述、链条四 §1.2 的 14A 时点表述（补列 Tan 2026-05 的 2028/2029 口径）。

**10-29 财报前应盯的 5 个字段（按优先级）：**

1. **Foundry 外部收入**——Q1 1.74 亿 → Q2 2.93 亿，**剔除 Altera 重分类后是否仍增长**（链条四 §5 条件 3 的唯一判据）；
2. **服务器出货量 vs ASP 的拆分**——链条二「量价拆分」证伪条件的核心；一致预期收入 164.3 亿落在指引上沿，门槛明确；
3. **合并毛利率环比方向**——链条二 §7.6 条件 1 缺的那一半；
4. **PDK 0.9 是否已发布**（原定时点就在本月内）；
5. **资本开支与经营现金流**——Q2 调整后 FCF 为 **-84.19 亿美元**（含 122.16 亿 partner contributions, net），现金消耗速度是本轮未更新的缺口。

本文不构成投资建议。

