# INTC 与 CPU 行业：把需求、交付和股东收益接起来

研究日：2026-09-26。最近可用的 Intel、AMD 季报均截至 2026 年第二季度；股价采用 2026-09-25 收盘观察。本稿将前一轮 Herman Jin / Serenity 方法卡应用于 INTC，以 CPU 行业作竞争背景。它是当日条件分析，不是对他们本人最新持仓的推断。

## 结论

**CPU 需求增强已经进入公司财报，Intel 的服务器产品也确实受益；INTC 后续能获得多少收益，取决于新增需求能否化成可交付的高利润产品，以及仍亏损的代工业务能否获得真正的外部客户。** Intel 2026Q2 的 DCAI 收入同比增 59% 至 **62.62 亿美元**、营业利润为 **24.74 亿美元**；DCAI 同时包含 CPU、加速器、网络产品等，不能把分部收入全算成 CPU。Foundry 同季 **20.89 亿美元营业亏损**，外部收入仅 **2.93 亿美元**，且增加主要与 Altera 从集团内部变为外部客户的会计边界变化有关。[Intel 2026Q2 10-Q：分部表及外部收入](https://www.intc.com/filings-reports/all-sec-filings/content/0000050863-26-000157/intc-20260627.htm)

这一判断有三层，必须各自接受证据检查：

1. **行业需求：证据较强。** Intel 披露服务器供不应求、出货量增加；AMD 同时披露 EPYC 需求增强，但其数据中心分部也含 GPU，不能将整个分部增长记为 CPU；Arm 和 NVIDIA 则在扩展 Arm 架构服务器 CPU。[Intel 10-Q](https://www.intc.com/filings-reports/all-sec-filings/content/0000050863-26-000157/intc-20260627.htm)、[AMD 10-Q](https://ir.amd.com/financial-information/sec-filings/content/0000002488-26-000123/amd-20260627.htm)、[Arm 2026-07 6-K](https://investors.arm.com/node/8356/html)、[NVIDIA Vera 公告](https://nvidianews.nvidia.com/news/nvidia-unveils-vera-the-cpu-for-agents)
2. **Intel 产品利润：已经体现，但不能全归因于缺货涨价。** Intel 披露服务器出货量同比增 9%、平均售价增 48%；公司明确说均价增加**主要来自高端产品组合**，缺货环境下的定价动作贡献较小，而且部分用于抵消更高的投入成本。服务器收入与利润增加是真实披露，具体可持续的净定价权仍需下一季跟踪。[Intel 10-Q：DCAI 量价解释](https://www.intc.com/filings-reports/all-sec-filings/content/0000050863-26-000157/intc-20260627.htm)
3. **外部先进代工：工程进展与商业兑现相差几步。** Intel 18A 的首批自有产品已经进入大量生产，18A-P 于 2026 年 6 月进入风险生产；14A 的重大潜在外部客户仍处于评估技术和设计里程碑的阶段。现有 Foundry 收入大部分是集团内部交易，不能视为已取得大规模先进节点外部订单。Foundry 同比亏损收窄还主要受到上年一次性费用不再发生的影响，不能全归因于外部代工经济性改善。[Intel 10-Q：工艺、外部业务及分部损益解释](https://www.intc.com/filings-reports/all-sec-filings/content/0000050863-26-000157/intc-20260627.htm)

**利润口径：** 同季归属 Intel 的 GAAP 净亏损约 **110.33 亿美元**，其中包括与政府托管股份估值变动相关的约 **125 亿美元**当季损失；DCAI 的分部营业利润与合并净亏损处在不同报表层级，不能把净亏损读成“CPU 产品亏损”。这项估值变动也提醒政策资本安排会改变普通股股东的经济结果。[Intel 2026Q2 10-Q](https://www.intc.com/filings-reports/all-sec-filings/content/0000050863-26-000157/intc-20260627.htm)

**估值必须先更新分母。** 2026-09-25 INTC 收盘约 **123 美元**，来自已打开的非发行人[历史报价页](https://www.investing.com/equities/intel-corp-historical-data)，标为 `PUBLIC_PAGE_VALIDATE`。Intel [8 月招股书](https://www.sec.gov/Archives/edgar/data/50863/000119312526345221/d98483d424b5.htm)按承销商增购选择权全额行使，列出发行后即刻预计在外股数 **5,285,069,511 股**；[8-K](https://www.sec.gov/Archives/edgar/data/50863/000119312526346806/d117670d8k.htm)确认该选择权于 2026-08-11 全额行使。将该**发行时预计股数**机械地乘 123 美元，约为 **6,501 亿美元**，只是 `MODEL_DERIVED` 的规模校验，不是已核实的 9 月 25 日准确市值：此后其他股数变动和最终结算未在本轮复核。2026-06-27 的 **50.43 亿股**与 **875.42 亿美元**归属 Intel 股东权益都早于此次发行；发行同时增加现金与权益，不能把新价格直接除以旧账面权益称作“当前 P/B”。此前语料中的低 P/B 判断须取得发行后股本、现金和权益，再按当时价格重算。[Intel 10-Q：资产负债表](https://www.intc.com/filings-reports/all-sec-filings/content/0000050863-26-000157/intc-20260627.htm)

## 1. 先界定 CPU 行业

| 需求池 | 采购对象和主要用途 | 受益链条 | 对 INTC 的检查 |
|---|---|---|---|
| PC 客户端 | 笔记本、台式机的 CPU/SoC；换机、性能与能效 | Intel、AMD、Arm 生态及 OEM | 客户端单位量、产品组合、售价和 CCPG 利润分别看。Intel 2026Q2 客户端收入增加，主要来自较高端产品组合，出货量同比下降 8%。[Intel 10-Q](https://www.intc.com/filings-reports/all-sec-filings/content/0000050863-26-000157/intc-20260627.htm) |
| 通用服务器 | 云服务、企业计算、存储和网络控制 | Xeon、EPYC、Arm 自研/授权 CPU；晶圆与封装 | 重点看服务器出货、ASP 来源和 DCAI 产品利润；不能用 GPU 销售代替 CPU 市场规模。[Intel 10-Q](https://www.intc.com/filings-reports/all-sec-filings/content/0000050863-26-000157/intc-20260627.htm)、[AMD 10-Q](https://ir.amd.com/financial-information/sec-filings/content/0000002488-26-000123/amd-20260627.htm) |
| AI 系统的主机、编排及数据处理 | GPU/ASIC 之外的调度、工具调用、检索、存储与数据准备 | x86 服务器 CPU、Arm 的 Graviton/Axion/Cobalt、NVIDIA Grace/Vera、Arm AGI CPU，以及各自代工厂 | CPU 需求增长并不指定 Intel 赢得全部份额；系统配置和软件适配会影响最终采购。[Arm 6-K](https://investors.arm.com/node/8356/html)、[NVIDIA 公告](https://nvidianews.nvidia.com/news/nvidia-unveils-vera-the-cpu-for-agents)、[TSMC 2026Q2 管理层交流](https://investor.tsmc.com/english/encrypt/files/encrypt_file/reports/2026-08/3e494f0c14dd0890f897aa044415e21d93486cc4/TSMC%202Q26%20Transcript.pdf) |
| 先进代工与封装 | 为自有或第三方芯片提供制程、封装和测试 | Intel Foundry、TSMC 等制造商 | 这是与 CPU 产品竞争不同的业务。以外部订单、认证、量产、外部收入和亏损收窄验证，不能只看先进制程名称。[Intel 10-Q](https://www.intc.com/filings-reports/all-sec-filings/content/0000050863-26-000157/intc-20260627.htm) |

**口径边界：** 本轮没有找到可免费打开、方法清楚且覆盖同一 CPU 市场定义的当期市场份额序列，所以不填“Intel/AMD/Arm 最新份额”。AMD 的 Data Center 收入 **67 亿美元**，包含 EPYC 和 Instinct 等，不是“AMD CPU 收入”；Arm 的许可/权利金与新 AGI CPU 实物销售也不能同 Intel 芯片销售额直接比较。[AMD 2026Q2 10-Q](https://ir.amd.com/financial-information/sec-filings/content/0000002488-26-000123/amd-20260627.htm)、[Arm 2026-07 6-K](https://investors.arm.com/node/8356/html)

### 1.1 同期价格对照：CPU 是本轮缺货涨价的温和跟随者

同为“AI 缺货”链条，2025Q4–2026H1 内存/存储的价格弹性显著大于 CPU。下表为机构测算与公开报道口径，**非本稿独立复算**，访问日 2026-09-26。

| 品类 | 涨幅（约） | 口径 |
|---|---|---|
| 服务器 CPU | 官方 RCP 累计 **+10~25%**：Intel 2026-03 一轮 10~15%，2026-07 一轮高端 Xeon 7~12%（旗舰 6980P +$1,495/+12%）；AMD 2026-04 跟进 10~15% | 建议价，非成交价；实际成交价受采购规模与客户关系影响 |
| 常规 DRAM 合约价 | 2026Q1 **+90~95% QoQ**（自 +55~60% 上修）；2026-04 较 Q1 再 **+57%** | TrendForce 2026-02-02；Bernstein 2026-05-07 |
| 服务器 DRAM | 2026Q1 合约价 **约 +90% QoQ**（史上最大季度涨幅）；DDR5 模组 2025 初→2026Q1 **+100~116%** | TrendForce；datacenterdisk |
| NAND / SSD | 2026Q1 合约价 **+55~60% QoQ**、eSSD **+53~58%**、客户端 SSD ≥+40%；2026-04 较 Q1 **+65~70%**；128Gb MLC 月度价连涨 15 个月，2026-03 环比 **+39.95%** | TrendForce；DRAMeXchange via Chosun 2026-03-31 |

**分析者归纳（非公司披露）：**

1. **数量级差**：若按“缺货 → 涨价 → 利润弹性”给 CPU 定价，同期内存是单季 55~95%、CPU 是累计 10~25%。Intel 服务器 ASP +48% 主要来自产品组合（结论第 2 条），与内存的纯合约价上涨**不是同一性质**。
2. **内存对 CPU 是成本项而非仅对照项**：Intel 10-Q 称部分 ASP 上涨用于抵消投入成本上升；内存/存储涨价同时推高 Intel 自身 BOM 与下游 OEM/云厂商成本，故“缺货涨价”对 CPU 多头是双刃的。
3. **与两人观点的接口**：Herman 观点 3 已把“存储与 CPU”并列为串联瓶颈（2025-12-30），[HJ-012](../kol-distillation-2026-09-26/herman-jin-cases.jsonl#L12) 提醒“CPU 缺货不会立刻复制存储股盈利”；本表为该提醒补充数量级对照。涨幅终点受每 token 成本约束（HJ-017），不能线性外推为长期 ASP。
4. **口径警告**：合约价 QoQ、月度现货价、累计涨幅三者**不可相加**；DDR4/DDR5、晶圆/模组、消费级/服务器级不可混用。后续核价先确认口径再引用。

## 2. 将两人的方法用于 INTC

| 问题 | Herman Jin 的原话/已归纳方法 | Serenity 的原话/已归纳方法 | 本次检查所得 |
|---|---|---|---|
| 新 CPU 需求从哪来？ | [HJ-010](../kol-distillation-2026-09-26/herman-jin-cases.jsonl#L10)、[HJ-011](../kol-distillation-2026-09-26/herman-jin-cases.jsonl#L11)：从 Agent 使用与新数据量追到服务器 CPU 和存储；2026-09-25 帖仅在**“GPU:CPU 走到 1:1”**条件下推未来高增长，[原帖](https://x.com/ShanghaoJin/status/2103484885013086227)与[本地行](../../../Herman%20Jin/x-archive/x-2026-09-25/posts.jsonl#L1305)。 | 2026-04-21 本人看 Arm，是因为编排、RAG、轻量模型及本地推理可能增加 CPU 使用；有明显预测成分，[原帖](https://x.com/aleabitoreddit/status/2046419572203683922)、[本地截断行](../../../Serenity/data/clean/posts.jsonl#L820)。 | Intel 与 AMD 财报支持服务器需求增加；GPU:CPU 的 1:1 比值缺少系统口径，不能作本轮基准预测。Arm 竞争使“CPU 好”与“INTC 独享”分离。 |
| 缺货如何变利润？ | [HJ-012](../kol-distillation-2026-09-26/herman-jin-cases.jsonl#L12)把瓶颈放到节点、封装、产量与良率；[2026-01 帖](https://x.com/ShanghaoJin/status/2014000610723643578)提醒 CPU 缺货不会立刻复制存储股盈利。 | [SR-M03](../kol-distillation-2026-09-26/serenity-methods.jsonl#L3)要求检查所引用的指标是否真的对应公司的产品和收入；2026-04-23 帖援引 CPU 缺货/涨价叙述，但所引价格与交期未经本轮独立复核，[原帖](https://x.com/aleabitoreddit/status/2047182611160965383)。 | Intel DCAI 收入和利润已明显增长；ASP 上升多数来自组合，交付还受内部产能与材料限制。 |
| 美国第二供应源何时形成收入？ | 既有 [Herman 观点 4](../../Herman-Jin%20观点%20rollup.md)归纳政策与制造期权，原文入口见 HJ-010 的分拆资产判断及 [Herman 2026-08 帖](https://x.com/ShanghaoJin/status/2091198496384876568)。 | 2026-01-17 长帖以政策和国家安全看 INTC，并将外部客户采用视作将来事项，[原帖](https://x.com/aleabitoreddit/status/2012492311092244821)、[本地截断行](../../../Serenity/data/clean/posts.jsonl#L136)；2026-01-23 回复直称其为政策而非基本面押注，[原帖](https://x.com/aleabitoreddit/status/2014733903140159682)、[本地截断行](../../../Serenity/data/clean/replies.jsonl#L1749)。3 月另表达过对 Intel 商业代工执行力的怀疑，[原帖](https://x.com/aleabitoreddit/status/2036238974747025683)。 | 国家战略与政策支持确实存在于其两人的论点中，但投资条件是独立的外部客户承诺、实际量产、净现金回收；目前 14A 仍需潜在客户验证。 |
| 预期是否已反映在价格？ | [HJ-M04](../kol-distillation-2026-09-26/herman-jin-methods.jsonl#L4)要求区分资产性质、利润来源与市场计入程度；2026-08 表达过短期过热、长期业务有前景的区分，[原帖](https://x.com/ShanghaoJin/status/2091198496384876568)。 | 2026-04-24 本人提醒不要每出现一个新“瓶颈”就追逐新题材，提议对既有仓位保持耐心，[原帖](https://x.com/aleabitoreddit/status/2047426124586893566)、[本地截断行](../../../Serenity/data/clean/posts.jsonl#L847)。 | 9 月股价乘发行时预计股数的规模校验远高于 Serenity 1 月帖子援引的 2340 亿美元；不能把旧帖的倍数空间直接用在当日价格上。需要重新建立分部估值及风险情景。 |

**归属说明：** HJ/SR 方法卡来自 55 个案例的首轮样本归纳，不是两人共同署名的 INTC 研究。上表使用的 Serenity 5 条重点原帖和 1 条回复于 2026-09-26 在官方 X 页面重新展开阅读；`posts.jsonl` / `replies.jsonl` 的相应本地行有截断，故仅以展开正文复原当时的公开表达。未留存完整在线文字或附图；访问时可见版本不保证与发帖瞬间完全一致。政策“兜底”、Apple/NVIDIA 关系、二级市场回报和供应链报价，均不可仅凭 KOL 发言写成已核实公司事实。

**本次可复用的推理路径（分析者归纳）：**

1. **沿 Herman 的量化链条：** 先确定 Agent/云端到底增加哪些 CPU 工作负载，再估计服务器数量和可交付晶圆，随后拆分 Intel 的销量、组合、提价和投入成本；只有新增营业利润能持续，才进入估值。华强北现货报价或供给紧张本身不能代替产量乘单件利润的计算。对应 [2026-04-18 原帖](https://x.com/ShanghaoJin/status/2045391062412460423)及[本地行](../../../Herman%20Jin/x-archive/x-2026-09-25/posts.jsonl#L354)，但该帖当时对 Q1/Q2 利润的判断须用后来财报重新检查。
2. **沿 Serenity 的论点归类：** 先写清买入假设是美国本土制造的多年政策期权，还是当期 CPU 基本面；再分别找政府资本条款、外部客户订单、Arm 竞争和实际现金回收。她本人曾把 INTC 长期观点明确归为政策判断，同时也表达过对 Arm CPU 的兴趣和对追逐短期瓶颈题材的警惕。[政策回复](https://x.com/aleabitoreddit/status/2014733903140159682)、[Arm 帖](https://x.com/aleabitoreddit/status/2046419572203683922)、[追涨提醒](https://x.com/aleabitoreddit/status/2047426124586893566)
3. **在 INTC 上合并：** CPU 需求成立 → Intel 拿到并交付产品订单 → 产品利润增长；外部代工则单独走“客户承诺 → 量产 → 对外收入 → 扣除资本成本后回报”。最后用发行后的股数、现金和市场价格核对已计入多少预期。任一步缺证据，就保留为条件情景，而非把上游需求直接折成目标价。

## 3. 分层证据：什么成立，什么仍待证

| 命题 | 已见证据 | 尚需观察的决定性数据 |
|---|---|---|
| AI/云端增加 CPU 工作量 | Intel 服务器销量与收入增加；AMD 把 Data Center 增长同时归因于 EPYC 和 GPU；Arm 披露数据中心权利金同比超过翻倍，NVIDIA 的 Vera 已进入量产。[Intel 10-Q](https://www.intc.com/filings-reports/all-sec-filings/content/0000050863-26-000157/intc-20260627.htm)、[AMD 10-Q](https://ir.amd.com/financial-information/sec-filings/content/0000002488-26-000123/amd-20260627.htm)、[Arm 6-K](https://investors.arm.com/node/8356/html)、[NVIDIA 公告](https://nvidianews.nvidia.com/news/nvidia-unveils-vera-the-cpu-for-agents) | 相同工作负载的 CPU 数量、利用率和架构分配；“GPU:CPU 1:1”目前只是条件情景。 |
| Intel CPU 出货增长能延续并保持利润 | Intel 2026Q2 DCAI 收入 62.62 亿美元、营业利润 24.74 亿美元，服务器单位量同比 +9%，服务器 ASP +48% 多由产品组合推动。[Intel 10-Q](https://www.intc.com/filings-reports/all-sec-filings/content/0000050863-26-000157/intc-20260627.htm) | 下一季同口径单位量、产品组合、供给改善、投入成本、经营利润。供给放松后 ASP/利润可能重新分配。 |
| 外部代工成为独立高利润增长源 | 18A 自有产品量产，18A-P 风险生产；2026Q2 外部收入 2.93 亿美元、Foundry 亏损 20.89 亿美元，外部增量主要来自 Altera 重新分类。[Intel 10-Q](https://www.intc.com/filings-reports/all-sec-filings/content/0000050863-26-000157/intc-20260627.htm) | 已签署的重要外部 14A 设计单、认证和合格率、客户量产时点、剔除会计边界变化后的外部收入、Foundry 亏损与资本回报。 |
| 政策支持保护现有股东回报 | Intel 已披露政府投资及相关权证/股本安排；8 月又签署约 2.421 亿股新股的承销交易且增购选择权全额行使。政策扶持不直接给出股东回报率。[Intel 10-Q](https://www.intc.com/filings-reports/all-sec-filings/content/0000050863-26-000157/intc-20260627.htm)、[Intel 8-K](https://www.sec.gov/Archives/edgar/data/50863/000119312526346806/d117670d8k.htm) | 发行结算后的现金与股数、未来新增资本需要多少自筹或增发、资本支出后的现金；政府策略和现有股东经济性分别核算。 |

## 4. 可执行的情景更新表

以下是**本轮分析者提出的检查规则**，不是两位作者已共同采用的交易信号。所有“若”均为未来条件，不是已发生结果。

| 情景 | 触发证据 | 对 INTC 论点的影响 |
|---|---|---|
| 增强 | 下一季服务器单位量、产品利润继续上升；内部供给改善；出现经披露的重大外部代工客户承诺与明确量产路径；Foundry 亏损持续收窄且融资成本可控 | 同时支持产品增长和制造期权。要按新股本、现金流与价格重新估值。 |
| 维持观察 | CPU 总需求强，但 Intel 产品增长主要依靠组合/短期缺货，14A 仍在评估，Foundry 外部收入低 | 行业判断可以成立，INTC 的新增价值兑现速度仍不清楚。 |
| 转弱 | 缺货缓解后服务器出货与利润回落，Arm/AMD 竞争拿走增量；14A 无法取得大客户承诺或资本投入大幅高于现金回收 | 降低对供给紧张和外部代工期权的估计，分别重新估算产品与代工价值。 |

**最近应核的 5 个字段：** Intel 下一份正式季报中的服务器单位量、ASP 与组合解释、DCAI 营业利润、Foundry 外部收入的真实新客户来源、资本开支及经营现金流。Intel 已给出的 **2026Q3 合并收入 158–168 亿美元、GAAP 毛利率 41%** 是公司指引，不是 CPU 或外部代工的单独预测。[Intel Q2 财报新闻稿](https://www.intc.com/news-events/press-releases/detail/1776/intel-reports-second-quarter-2026-financial-results) 对手信息则核 AMD 的 EPYC 叙述是否能与 Instinct 分开，以及 Arm AGI CPU、Vera 从交付到可辨认收入的速度。

## 来源记录与边界

| ID | 来源、发表时间与期间 | 访问/状态 | 本稿用法 |
|---|---|---|---|
| INTC-Q2-10Q | [Intel 2026Q2 Form 10-Q](https://www.intc.com/filings-reports/all-sec-filings/content/0000050863-26-000157/intc-20260627.htm)，2026-07-24，期末 2026-06-27 | 2026-09-26，`PUBLIC_NO_AUTH` | 分部、量价、工艺阶段、外部收入、当时权益和股数；财报历史事实和公司前瞻分别标明。 |
| INTC-AUG-OFFERING | [Intel 2026-08-12 8-K](https://www.sec.gov/Archives/edgar/data/50863/000119312526346806/d117670d8k.htm)与[招股书补充文件](https://www.sec.gov/Archives/edgar/data/50863/000119312526345221/d98483d424b5.htm) | 2026-09-26，`PUBLIC_NO_AUTH` | 承销协议、增购选择权全额行使、发行时预计股数与预计净所得；未核最终结算和 9 月在外股数。 |
| INTC-Q2-RELEASE | [Intel 2026Q2 财报新闻稿](https://www.intc.com/news-events/press-releases/detail/1776/intel-reports-second-quarter-2026-financial-results)，2026-07-23 | 2026-09-26，`PUBLIC_NO_AUTH` | Q3 2026 合并指引，仅作为公司前瞻。 |
| AMD-Q2-10Q | [AMD 2026Q2 Form 10-Q](https://ir.amd.com/financial-information/sec-filings/content/0000002488-26-000123/amd-20260627.htm)，2026-08-05，期末 2026-06-27 | 2026-09-26，`PUBLIC_NO_AUTH` | EPYC 与 Instinct 同在 Data Center 分部；不代入 CPU 单独收入。 |
| ARM-Q1-6K | [Arm FYE27 Q1 Form 6-K 附股东信](https://investors.arm.com/node/8356/html)，2026-07-29，期末 2026-06-30 | 2026-09-26，`PUBLIC_NO_AUTH` | 权利金与 AGI CPU 交付/需求是不同口径，管理层预测不记作已确认收入。 |
| NV-VERA | [NVIDIA Vera 公告](https://nvidianews.nvidia.com/news/nvidia-unveils-vera-the-cpu-for-agents)，2026-05-31 | 2026-09-26，`PUBLIC_NO_AUTH` | Arm 架构替代供给及产品生产阶段；性能比较属于公司宣称，本稿不据此排名。 |
| TSMC-Q2-CALL | [TSMC 官网 2026Q2 电话会](https://investor.tsmc.com/english/encrypt/files/encrypt_file/reports/2026-08/3e494f0c14dd0890f897aa044415e21d93486cc4/TSMC%202Q26%20Transcript.pdf)，2026-07-16，官网后上架编辑版 | 2026-09-26，`PUBLIC_NO_AUTH` | 管理层称 x86/Arm/RISC-V CPU 客户多数由其承接；作为公司表述，非份额数据。 |
| INTC-PRICE | [Investing.com INTC 历史报价](https://www.investing.com/equities/intel-corp-historical-data)，2026-09-25 收盘 | 2026-09-26，`PUBLIC_PAGE_VALIDATE`；非交易所/发行人来源 | 仅用于股价乘发行时预计股数的规模校验，不能代替当日准确市值、可交易报价或企业价值。 |
| MEM-CPU-PRICE | §1.1 涨幅对照：TrendForce 新闻稿（2026-01-05、2026-02-02、2026-03-06、2026-07-09）、Bernstein via Investing.com 2026-05-07、DRAMeXchange via Chosun 2026-03-31、Tom's Hardware/TrendForce 2026-07-03/07（Intel RCP）、21 世纪经济报道 2026-07-09（IDC/Counterpoint 涨幅引述）、Wecent 2026-05-31（累计涨幅汇总表） | 2026-09-26，`PUBLIC_PAGE_VALIDATE`；多为二手报道或机构测算 | 仅作同期数量级对照与成本项提示；非本稿独立复算，合约价/现货/累计口径不可加总，不用于任何利润或目标价推导。 |
| KOL-CORPUS | [首轮方法卡](../kol-distillation-2026-09-26/README.md) 与本地 X 清洗语料；上表链接到原帖 | `USER_PROVIDED`；2026-09-26 官方 X 页面重看所选长帖 | 记录两人公开表达，不把他们援引的公司、价格或政策说法当作独立公司事实。 |

**未覆盖：** 没有同口径全行业 CPU 出货/份额统计、Intel 产品级订单与良率、各架构的客户单位成本、14A 尚未公开的合同、完整的前瞻盈利预测；因此本稿不设价格目标或"必须买/卖"的结论。下一季数据到来时，先更新上面的指标与日期，再决定是否重估情景。

**接续稿：**

- **链条一（需求是否增长）**——不单独成稿，见本文件 §1 需求池与 §3 分层证据。
- **链条二（缺货 → 价格 → 利润）**——[chain-2-price-margin.md](chain-2-price-margin.md)，核验截点 2026-09-27；[美光 FY26Q4 回填核验](chain-2-micron-fy26q4-verify-2026-10-04.md)，核验截点 2026-10-04。
- **链条三（架构与份额：新增蛋糕里 Intel 拿到多少）**——[chain-3-architecture-share.md](chain-3-architecture-share.md)，核验截点 2026-10-05。核心读数：Intel 服务器份额环比 -137bp，且份额流失被归因于**自身供给不足**。
- **链条四（代工 / 摊薄 / 估值）**——[chain-4-foundry-dilution-valuation.md](chain-4-foundry-dilution-valuation.md)，核验截点 2026-10-05。核心读数：14A **已承诺外部客户 0 家**；股本较 FY2022 +27.7%；卖方共识目标价 $115.03 低于 9-25 市价 $123.03。

⚠ **「四条检查链条」的编号并非本文件原有**（本文件只出现过「第二条检查链条」字样），它来自 2026-09-25 工作区交接文档的整理。链条三、链条四的开篇各自界定了本链条的边界，引用时以那两份文件的定义为准。
