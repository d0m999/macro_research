# Serenity 观点、推理与方法：首轮蒸馏

日期：2026-09-26。研究对象：X 账号 **@aleabitoreddit**。这是公开表达的推理整理，不声称复原未公开的思考过程。

## 结论

本轮形成 **28 个可回溯案例、4 张样本内反复出现的方法卡、2 张候选方法卡**。覆盖 2025-09-14 至 2026-09-14；AI 资本开支 8 例、半导体供需 8 例、光通信 12 例。计数单位是判断事件，不把本地片段与在线补证重复计数。

最清楚的共同线索是：从大型客户的需求和支出出发，沿生产依赖关系寻找瓶颈；再问收入如何兑现、哪层掌握定价权、融资是否损害股东。**“发现瓶颈”还需要经过技术暴露、兑现阶段和资本结构的判断。** 这一归纳来自本轮具体案例，不是为他预设一套永远一致的理论。[SR-003](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:3)、[SR-005](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:5)、[SR-011](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:11)、[SR-020](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:20)、[SR-025](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:25)

另一个有用发现是，他表达过明确的条件与不确定性：IREN 的软件收购可以改善经营评价，同时融资条件仍阻止他参与；AXTI 能否通过涨价重估取决于是否实际提价；SIVE 的产能财务推算明确只是示意。[SR-008](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:8)、[SR-018](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:18)、[SR-028](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:28)

### 这次补全文字改变了什么

主流程在官方 X 页面补查 8 条高价值主帖，**8 条全部确认本地正文被截断**。截断不只影响细节：它切掉过成本模型假设、改口原因、未确认关系的限定，以及“不是公司指引”的重要说明。以下采用补回后的理解。现场读取摘要保存在 [online-evidence.jsonl](online-evidence.jsonl)，不覆盖清洗语料。

- GPU 云比较：恢复了同款 H100、4 年折旧、85% 利用率，以及毛利与融资后 IRR 的区别。[SR-003](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:3)
- IREN：恢复了原 colo 自由现金流支持 GPU 扩张的假设，以及资金路径改变的改口原因。[SR-006](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:6)
- 瓶颈映射：恢复了中游定价权的判断，限制了“越上游越好”的简单归纳。[SR-011](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:11)
- SIVE：恢复了示意模型、非公司指引及 2027 年第四季度目标的限定。[SR-028](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:28)

## 资料与抽取口径

全量扫描入口为 1,794 条主帖、5,061 条回复；按三个主题检索，再逐条阅读候选，优先选择论证自足、条件明确和能说明变化的材料。这是目的性抽样，不是随机样本或全量覆盖。对同一观点的反复庆祝、收益截图和无论证短评没有按独立方法证据计数。

- 20 例基于本地可自足理解的文本；8 例另经官方原帖展开补证。
- 本轮 28 例均为 `usable_reasoning`：**仅表示所抽取的命题有可理解的依据与推理**。不等于整帖、会话、附图或所引公司数据已核验。
- 回复的真实父帖 ID 不可得；只抽取该条自身明确命名的对象和理由，不把 `thread_id` 当作真实会话，也不补造对方问题。
- `explicit` 表示本人公开明说的内容；`inferred` 表示本轮归纳。方法卡整体是跨案例归纳，并非本人逐条发布过的操作规程。
- 第三方预测、财报数字和技术关系只按其引用方式记录。Counterpoint、Morgan Stanley、Trendforce 或公司高管的话保留原归属；它们的真实性未在本轮另做尽调。
- 日期按本地 `created_at` 的 UTC 日；AAOI 补证在 UTC+08 页面显示次日。Counterpoint 那条原帖显示最新编辑版本，不能保证全部措辞在最初发布日期就存在。

结构化台账：[serenity-cases.jsonl](serenity-cases.jsonl)。方法字段：[serenity-methods.jsonl](serenity-methods.jsonl)。共同规则：[PROTOCOL.md](PROTOCOL.md)。

## 案例索引

每行链接到完整案例字段；P 为主帖物理行号，R 为回复物理行号，W 为本轮官方页面补证记录。一个案例的多个引用仍是同一次判断。

| 案例 | 日期 | 主题 | 抽取命题 | 来源 |
|---|---|---|---|---|
| [SR-001](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:1) | 2025-09-14 | AI 资本开支 | 同样是大额云合同，先看付款方 | [R56](/Users/d0m999/Desktop/vibe-trading/Serenity/data/clean/replies.jsonl:56) |
| [SR-002](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:2) | 2025-09-27 | AI 资本开支 | 融资条款决定是否愿意参与扩张 | [R255](/Users/d0m999/Desktop/vibe-trading/Serenity/data/clean/replies.jsonl:255) |
| [SR-003](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:3) | 2025-11-30 | AI 资本开支 | 统一硬件与利用率后比较云业务经济性 | [P68](/Users/d0m999/Desktop/vibe-trading/Serenity/data/clean/posts.jsonl:68)；[W2](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/online-evidence.jsonl:2) |
| [SR-004](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:4) | 2026-01-29 | AI 资本开支 | 以收入增长回应 Meta 资本开支疑虑 | [P174](/Users/d0m999/Desktop/vibe-trading/Serenity/data/clean/posts.jsonl:174) |
| [SR-005](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:5) | 2026-02-15 | AI 资本开支 | 资本开支消耗谁的现金，增加谁的利润 | [P268](/Users/d0m999/Desktop/vibe-trading/Serenity/data/clean/posts.jsonl:268)；[W3](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/online-evidence.jsonl:3) |
| [SR-006](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:6) | 2026-03-05 | AI 资本开支 | IREN 资金路径变化触发判断修改 | [P397](/Users/d0m999/Desktop/vibe-trading/Serenity/data/clean/posts.jsonl:397)；[W5](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/online-evidence.jsonl:5) |
| [SR-007](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:7) | 2026-03-28 | AI 资本开支 | 现成电力提供窗口，但不能直接等同于护城河 | [R3248](/Users/d0m999/Desktop/vibe-trading/Serenity/data/clean/replies.jsonl:3248) |
| [SR-008](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:8) | 2026-07-17 | AI 资本开支 | 收购改善 IREN 能力，融资条件仍是参与门槛 | [R4782](/Users/d0m999/Desktop/vibe-trading/Serenity/data/clean/replies.jsonl:4782) |
| [SR-009](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:9) | 2025-10-16 | 半导体供需 | ASML 不能独自代表全部半导体增长 | [R613](/Users/d0m999/Desktop/vibe-trading/Serenity/data/clean/replies.jsonl:613) |
| [SR-010](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:10) | 2026-02-03 | 半导体供需 | 涨幅与便宜程度分开，重看前瞻盈利 | [P191](/Users/d0m999/Desktop/vibe-trading/Serenity/data/clean/posts.jsonl:191) |
| [SR-011](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:11) | 2026-02-07 | 半导体供需 | 从技术瓶颈清单映射公司，再判断定价权在哪层 | [P229](/Users/d0m999/Desktop/vibe-trading/Serenity/data/clean/posts.jsonl:229)；[W1](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/online-evidence.jsonl:1) |
| [SR-012](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:12) | 2026-02-11 | 半导体供需 | 先辨别 HBM 与 Sandisk 的技术暴露 | [P245](/Users/d0m999/Desktop/vibe-trading/Serenity/data/clean/posts.jsonl:245) |
| [SR-013](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:13) | 2026-02-16 | 半导体供需 | 有存储 IP 收入，不等于享受存储涨价 | [R2086](/Users/d0m999/Desktop/vibe-trading/Serenity/data/clean/replies.jsonl:2086) |
| [SR-014](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:14) | 2026-03-13 | 半导体供需 | 在采购意愿条件下把供需预测推到利润率 | [P459](/Users/d0m999/Desktop/vibe-trading/Serenity/data/clean/posts.jsonl:459)；[W6](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/online-evidence.jsonl:6) |
| [SR-015](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:15) | 2026-07-17 | 半导体供需 | 经历回撤后仍以经营利润评价存储仓位 | [R4780](/Users/d0m999/Desktop/vibe-trading/Serenity/data/clean/replies.jsonl:4780) |
| [SR-016](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:16) | 2026-09-14 | 半导体供需 | 用单月利润与提价预期解释 ESMT 看法 | [R5047](/Users/d0m999/Desktop/vibe-trading/Serenity/data/clean/replies.jsonl:5047) |
| [SR-017](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:17) | 2026-01-08 | 光通信 | 区分旧合同收入延后与前瞻瓶颈 | [P121](/Users/d0m999/Desktop/vibe-trading/Serenity/data/clean/posts.jsonl:121) |
| [SR-018](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:18) | 2026-02-09 | 光通信 | 瓶颈能否变成收益，取决于是否行使提价权 | [R2002](/Users/d0m999/Desktop/vibe-trading/Serenity/data/clean/replies.jsonl:2002) |
| [SR-019](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:19) | 2026-02-25 | 光通信 | 用多层供应关系推测保密物料清单 | [P334](/Users/d0m999/Desktop/vibe-trading/Serenity/data/clean/posts.jsonl:334)；[W4](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/online-evidence.jsonl:4) |
| [SR-020](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:20) | 2026-02-28 | 光通信 | 从光模块财报追到外延片和设备需求 | [P361](/Users/d0m999/Desktop/vibe-trading/Serenity/data/clean/posts.jsonl:361) |
| [SR-021](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:21) | 2026-04-14 | 光通信 | 在衬底瓶颈上游再找前驱材料 | [P760](/Users/d0m999/Desktop/vibe-trading/Serenity/data/clean/posts.jsonl:760) |
| [SR-022](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:22) | 2026-04-27 | 光通信 | 用产业资本锁供给的动作回看 IQE | [P871](/Users/d0m999/Desktop/vibe-trading/Serenity/data/clean/posts.jsonl:871) |
| [SR-023](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:23) | 2026-05-04 | 光通信 | 送样、客户认证与量产需要分开 | [R4017](/Users/d0m999/Desktop/vibe-trading/Serenity/data/clean/replies.jsonl:4017) |
| [SR-024](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:24) | 2026-05-11 | 光通信 | 按量产窗口区分技术前景和投资时点 | [P992](/Users/d0m999/Desktop/vibe-trading/Serenity/data/clean/posts.jsonl:992) |
| [SR-025](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:25) | 2026-05-13 | 光通信 | 客户预付款是供给紧张的观察信号 | [P1023](/Users/d0m999/Desktop/vibe-trading/Serenity/data/clean/posts.jsonl:1023) |
| [SR-026](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:26) | 2026-05-14 | 光通信 | 客户映射可以合理，但必须保留传闻属性 | [P1033](/Users/d0m999/Desktop/vibe-trading/Serenity/data/clean/posts.jsonl:1033) |
| [SR-027](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:27) | 2026-08-21 | 光通信 | 光通信经营乐观不能免除融资约束 | [P1650](/Users/d0m999/Desktop/vibe-trading/Serenity/data/clean/posts.jsonl:1650)；[W7](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/online-evidence.jsonl:7) |
| [SR-028](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:28) | 2026-09-03 | 光通信 | 产能乘历史售价只是收入量级示意 | [P1716](/Users/d0m999/Desktop/vibe-trading/Serenity/data/clean/posts.jsonl:1716)；[W8](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/online-evidence.jsonl:8) |

## 方法卡

`支持事件数`只统计各卡列出的独立判断事件。至少 3 个的门槛是本轮工作约定，不是统计验证或投资有效性证明。一例可支持不同方法，但本轮总样本仍只有 28 例。

| 方法 | 触发问题 | 样本状态 | 支持事件数 | 本轮保留的边界与核验要求 |
|---|---|---|---:|---|
| [SR-M01](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-methods.jsonl:1) 沿支出和生产依赖关系追到瓶颈 | 钱和订单最终落在哪里？ | `supported_in_sample` | 5 | 上游位置不自动等于最高定价权；供需窗口不自动变成护城河 |
| [SR-M02](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-methods.jsonl:2) 合同、业务经济性与股东融资 | 扩张的收益能否留给现有股东？ | `supported_in_sample` | 7 | 对手方、毛利、IRR、SBC、ATM 需要分开理解 |
| [SR-M03](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-methods.jsonl:3) 产品暴露、口径与商业化阶段 | 指标或技术消息真的对应这家公司吗？ | `supported_in_sample` | 8（分支支持） | 产品/指标、阶段、毛利比较是不同分支，非 8 例都执行全流程 |
| [SR-M04](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-methods.jsonl:4) 前瞻经营量级与价格 | 上涨或回撤后，价格是否反映经营预期？ | `supported_in_sample` | 5 | 统一口径、不年化等属于本轮核验建议；非指引限定仅 SR-028 明示 |
| [SR-M05](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-methods.jsonl:5) 公开关系推测隐藏客户 | 保密 BOM 下能形成什么待验证假说？ | `candidate` | 2 | 合理映射仍不是直接订单确认 |
| [SR-M06](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-methods.jsonl:6) 稀缺供应的控制价值 | 谁可以提价或影响下游选择？ | `candidate` | 2 | 潜在权力与实际使用不同；假设收购不是已发生控制 |

### 怎样理解这几张卡

**需求传导。** 以大型云公司的支出为起点，可以先找到供应商，再向材料与设备延伸。AAOI → 外延片 → MBE/MOCVD，以及 TSEM 预付款 → SOI 衬底，展示了不同的生产环节。同一规则还要容纳中游拥有定价权、上游仅有重要性但尚未兑现利润的情形。[SR-005](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:5)、[SR-011](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:11)、[SR-020](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:20)、[SR-025](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:25)

**股东条件。** 他并非每次都反对融资：好的条款和已完成的融资可以被接受；反复 ATM、较差资本结构或 SBC 又可能阻止参与。GPU 成本模型中，他把云业务毛利和融资后 IRR 分开。因此不能只复制某时刻“看多/看空 IREN”的标签。[SR-002](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:2)、[SR-003](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:3)、[SR-006](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:6)、[SR-008](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:8)、[SR-027](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:27)

**技术与阶段。** ASML 的建厂周期、HBM4 与 SNDK 的关系、RMBS 的 IP 收入、ELS 送样与认证，都被用来限制过度外推。这里有不同分支的重复：产品/指标边界见 SR-009/012/013，阶段边界见 SR-017/023/024/028，完整的同条件毛利比较只见 SR-003。不能说 8 例都跑过同一套流程；具体技术判断仍需要独立事实核验。[SR-009](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:9)、[SR-012](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:12)、[SR-013](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:13)、[SR-023](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:23)、[SR-024](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:24)

**经营量级。** 他会以未来盈利或产能量级重新评价市场价格，而非仅以已涨多少作判断。但其示意数值有明确性质：ESMT 是单月利润，SIVE 是历史价格下的产能推算，韩国存储的低 P/E 是第三方未来盈利估计。这些数值需要分别核验。统一期间/口径、不机械年化、以及不用股价证明兑现，属于本轮提出的分析者检查建议，不声称本人所有帖子都已执行。明确“示意、非指引”的限定只在 SR-028 这一例得到直接支持。[SR-010](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:10)、[SR-016](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:16)、[SR-028](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:28)

**两个候选。** 隐藏客户映射和供应控制的假设，在本轮各只找到两个独立、明确的例子。它们适合继续收集反例，暂不能宣称是已验证的选股能力。IQE 获产业资本锁供给的案例可以加强对重要性的理解，却不能单独证明控制整个行业的战略推演。[SR-018](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:18)、[SR-019](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:19)、[SR-021](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:21)、[SR-022](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:22)、[SR-026](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:26)

## 三个主题的时间线

### AI 资本开支：合同确定性 → 比较经济性 → 改变资金路径时改判断

| 时间 | 当时表达的判断 | 变化与边界 |
|---|---|---|
| 2025-09 | 看重 Microsoft 付款方信用；接受部分条款合理的融资 | 开始就有合同与股东条件，不是只看名义订单规模。[SR-001](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:1)、[SR-002](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:2) |
| 2025-11 | 统一 GPU 成本模型比较三家新云 | 承认 IREN 的成本优势与软件层潜力，同时单独看资本结构。[SR-003](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:3) |
| 2026-01 至 02 | 将 hyperscaler 高开支与收入增长、现金承受力及供应商利润一起看 | 支出方和收款供应商的风险、兑现时点不同。[SR-004](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:4)、[SR-005](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:5) |
| 2026-03 | 批评 IREN ATM；回顾原 colo 自由现金流路径被改变 | 这是明示改口原因，但原多头论点在本条属于事后自述。[SR-006](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:6) |
| 2026-03 | 电力与土地带来短期窗口 | 本人明确这些资源本身不是可防守的长期护城河。[SR-007](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:7) |
| 2026-07 | Mirantis 改善软件与容量组合 | 经营评价改善，但高管 SBC 与融资机制仍是参与门槛。[SR-008](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:8) |

### 半导体供需：核对暴露 → 前瞻盈利 → 回撤时重述依据

| 时间 | 当时表达的判断 | 变化与边界 |
|---|---|---|
| 2025-10 | ASML 与 TSM 反映的产业活动不同 | 不接受单靠建厂指标外推全部增长。[SR-009](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:9) |
| 2026-02 | 援引韩国存储低前瞻 P/E；映射产业瓶颈 | 价格已经上涨仍可能有重估空间，但盈利估计不是事实。[SR-010](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:10)、[SR-011](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:11) |
| 2026-02 | 排除 HBM4 新闻对 SNDK 的简单归因，也排除 RMBS 自动享受器件涨价 | 都是在核对实际收入暴露。[SR-012](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:12)、[SR-013](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:13) |
| 2026-03 | 援引有需求前提的价格预测，再推利润率 | Counterpoint 的条件保留原归属；当前在线版本存在编辑时间限制。[SR-014](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:14) |
| 2026-07 | 承认 EWY 回撤但继续看经营利润 | 属于维持判断，不是新盈利预测或成功验证。[SR-015](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:15) |
| 2026-09 | ESMT 单月利润与 H2 提价预期 | 是另一公司与新信息事件；不能机械年化单月数。[SR-016](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:16) |

### 光通信：衬底 → 更上游 → 商业化窗口 → 股东约束与财务量级

| 时间 | 当时表达的判断 | 变化与边界 |
|---|---|---|
| 2026-01 至 02 | AXTI 旧收入与前瞻瓶颈分开；能否提价仍不确定 | 瓶颈潜力不是确定收益。[SR-017](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:17)、[SR-018](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:18) |
| 2026-02 | LITE/IQE/AXTI 隐含映射；AAOI 需求向设备延伸 | 前者是未确认关系，后者是生产依赖推演。[SR-019](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:19)、[SR-020](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:20) |
| 2026-04 | 从 InP 上溯高纯磷；产业资本为 IQE 锁供给 | NCI 控制情景仍是假设，拟投资也不是定价能力证明。[SR-021](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:21)、[SR-022](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:22) |
| 2026-05 | 对过早的 ELS、2029 年以后塑料光学保留时点限制 | 需要客户认证及量产路径；未确认订单仍标为媒体推测。[SR-023](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:23)、[SR-024](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:24)、[SR-026](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:26) |
| 2026-05 | TSEM 预付款被用作上游 SOI 需求线索 | 未量化预付款到底对应多少 SOI 收入。[SR-025](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:25) |
| 2026-08 | 对 AAOI 反复 ATM 更谨慎 | 经营乐观与股东融资批评可以同时成立，不能推定已交易。[SR-027](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:27) |
| 2026-09 | 把 SIVE 目标产能转换成收入量级 | 保留非指引、示意模型及 2027 年第四季度时间条件。[SR-028](/Users/d0m999/Desktop/vibe-trading/research/_agent/kol-distillation-2026-09-26/serenity-cases.jsonl:28) |

## 局限、反例与下一轮

1. **完整性仍是最大资料风险。** 这次成功补回 8 条，不能外推其余 1,786 条主帖都完整。缺图、缺引文出处、缺原始抓取包及真实回复父帖仍需逐案处理。
2. **未把外部事实核验和观点还原混为一层。** 本轮核对的是他表达过什么、如何连接依据与结论；未重算模型、核实所有合同或公司技术关系。案例中的高抽取置信度只针对文字还原。
3. **已找到了限制条件，但还没有系统的失败样本库。** IREN 的判断修改、AXTI 的不确定提价、ELS 认证风险属于边界证据；它们不证明其他案例有效。没有找到反例不等于没有反例。
4. **时序不完全。** 某次回顾旧观点可能是事后叙述；已编辑原帖可能不是当时版本。两者都不能直接用于严格历史预测检验。
5. **这不是盲测。** 全部材料都在归纳时可见，抽样也根据主题和完整性决定。下一轮要先冻结方法卡与信息截止日期，再用未参与归纳的新材料记录预期变量、判断条件及其后是否修改。
6. **不评价投资绩效。** 股价、回撤或作者自报收益仅作为话语背景；`outcome_evaluated` 全为 `false`。本轮未计算胜率、回报，也未用涨幅证明因果关系。

下一轮应优先补：失败或撤回的客户映射、没有成功提价的瓶颈案例、公司实际融资文件、送样未获认证的后续。把这些材料加入候选卡，比继续增加同一上涨主题的复述更能区分适用边界。

## 本地核验范围

完成 JSONL 解析、28 个案例 ID 与 6 个方法 ID 唯一性、必填字段、36 个引用的路径/物理行与短引文匹配、方法引用、独立事件计数及相互关联检查。Serenity 的 3 个源文件 SHA-256 与本轮快照一致。对在线部分核对现场读取记录，不把摘要检查说成重新浏览了全部原文。

未做交易回测或外部财务事实验收。源文件只读；所有新增产物位于本轮目录。
