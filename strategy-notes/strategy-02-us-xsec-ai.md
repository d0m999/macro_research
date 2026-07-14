# 策略 2：美股 AI 主题截面选股（US Cross-Sectional, AI Theme）

> 状态：草稿 v0.1（**数据源盘点阶段**——策略逻辑未立项，先回答"研究美股用什么公开数据"）
> 记录日期：2026-07-13
> 品种：US equities（美股现货，**long-only 起步**，不做空）
> 类型：**截面策略**（cross-sectional 选股），与策略 1（时序择时）互补
> 周期：月度调仓为主，主题持有期 3~5 年（对应本轮 AI 资本开支周期）
> 阶段定位：新手第一个截面项目——**数据基建的优先级高于信号研发**

---

## 0. 先说清楚我们在赚什么钱

做了三十年，第一课永远是先问收益来源。"吃 AI 红利"拆开是两笔钱：

- **主题 beta**（AI 板块整体上涨）——这部分**不需要选股**，买 SOXX / SMH / AIQ 这类 ETF 就能拿满，成本几个 bp。
- **截面 alpha**（板块内部谁强谁弱、产业链利润流向哪一环）——这才是截面选股要赚的钱，也是唯一值得你投入研究时间的部分。

新手最常见的自欺：回测赚的其实是 beta，却以为自己会选股。所以从第一天起立一条铁律：**所有回测结果必须对照两个基准做归因——(a) 等权股票池基准；(b) Ken French 因子回归后的残差收益**。跑赢不了等权池 = 你的"选股"没有信息量。

### 截面 vs 时序（与策略 1 的本质区别）

| | 策略 1（MTF Buff） | 本策略 |
|---|---|---|
| 预测对象 | 单一标的"涨不涨"（方向） | 股票池内"谁比谁强"（排序） |
| 每期样本量 | 1 个决策 | 几百个截面观测 |
| 收益来源 | 趋势延续 / 均值回复 | 打分与未来**相对收益**的秩相关（IC） |
| 对新手的友好度 | 低（样本少，运气成分大） | 高（**大数定律站在你这边**） |

截面策略的评价体系：每个调仓日对池内全部股票打分 → 排序 → 分层（quintile）→ 看 IC（信息系数）与分层单调性。IC 长期稳定在 0.03~0.05、且几个低相关信号能叠加，就是一门生意。不追求单次判断多准，追求**统计上的持续微弱优势**——这是 RenTech 的全部秘密，也没有别的秘密。

---

## 1. 美股公开数据全景地图

美股是全球**公开数据最丰富、监管披露最完整**的市场——这是选它做截面研究的根本理由。按研究用途分七层。

### 1.1 行情数据（价格 / 成交量）

| 来源 | 内容 | 成本 | 备注 |
|---|---|---|---|
| **yfinance**（Yahoo Finance 非官方库） | 日线 OHLCV、复权价、股息拆股 | 免费 | 起步首选；⚠️ 只有**存活标的**（幸存者偏差，见 §4.1）；非官方接口，只用于研究不可分发 |
| **Tiingo** | 日线 EOD、复权质量好、REST API | 免费额度充裕 | 免费层里数据质量最好的之一，适合做主力价格源 |
| **Polygon.io** | 日线免费（限速），分钟/tick 付费 | 免费层 5 req/min | 截面月频研究用不到 tick，免费层够 |
| **Alpha Vantage / Nasdaq Data Link** | 日线、部分基本面 | 免费层较紧 | 备胎 |
| **Stooq** | 日线历史（含部分退市） | 免费 | 冷门但历史长，可交叉校验 |
| CRSP（学术金标准） | 全历史含退市、退市收益 | 付费（WRDS 学术订阅） | 知道它存在即可；个人阶段不需要 |

> 结论：**Tiingo（主）+ yfinance（辅）**，全部落地为本地 parquet，永远不要在回测循环里现拉 API。

### 1.2 基本面数据 —— SEC EDGAR 是唯一的"源头活水"

所有商业数据商的基本面数据都是从 EDGAR 加工来的。直接喝源头的水：**免费、法定、含历史原文**。

| 披露文件 | 内容 | 频率 / 时限 | 研究用途 |
|---|---|---|---|
| **10-K** | 年报（经审计财务报表、业务描述、风险因素） | 年度，财年结束后 60~90 天内 | 基本面因子的年度锚 |
| **10-Q** | 季报（未审计） | 季度，季末后 40~45 天内 | 季度基本面因子、capex 追踪 |
| **8-K** | 重大事项即时公告（含财报新闻稿附件） | 事件后 4 个工作日内 | 事件研究、财报日定位 |
| **13F** | 机构持仓（管理规模 ≥ $100M） | 季度，季末后 45 天内 | 机构持仓变动因子（⚠️ 45 天滞后） |
| **Form 4** | 内部人（高管/董事）买卖 | 交易后 2 个工作日内 | 内部人交易信号（不对称：买入信号 > 卖出） |
| **S-1 / 424B** | IPO / 增发 | 事件驱动 | 供给压力（AI 主题里增发很频繁） |

**程序化入口（全部免费）：**

- **XBRL Company Facts API**：`https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json` —— 单公司全部结构化财务数据，**带申报日期（filed date）**，这是自建 point-in-time 数据库的关键字段
- **Frames API**：`data.sec.gov/api/xbrl/frames/...` —— 按"某科目 × 某季度"横截面取全市场数据，天然适合截面研究
- **Financial Statement Data Sets**：每季度打包的全市场 XBRL 数值 ZIP，适合批量建库
- **EDGAR 全文检索**：`https://efts.sec.gov/LATEST/search-index?q=...`（UI：sec.gov/edgar/search/），覆盖 2001 年以来全部文件——可以统计"10-K 里提及 AI 相关关键词的次数/位置"来**规则化定义 AI 股票池**（学界已有同类做法）
- Python 库：**edgartools**（推荐）、sec-edgar-downloader
- ⚠️ 限速 10 req/s，必须带 `User-Agent`（邮箱），否则封 IP

### 1.3 分析师预期与盈利修正

诚实地说：**这是免费栈最大的缺口**。盈利修正（earnings revision）是截面研究最强的信号族之一，但 point-in-time 的历史预期数据（IBES）是付费的。

| 来源 | 内容 | 成本 | 局限 |
|---|---|---|---|
| yfinance analyst data | **当前**一致预期、目标价 | 免费 | 只有当前快照，**不能用于回测**，只能实盘筛选 |
| Zacks（网页） | 预期、盈利惊喜历史 | 部分免费 | 难以程序化 |
| IBES（WRDS） | PIT 历史一致预期 | 付费/学术 | 金标准，个人阶段不碰 |

**平替方案（重要）**：用 EDGAR 里的**实际财报数据**构造 **SUE（标准化盈利惊喜）与基本面动量**（营收加速度、毛利率环比变化），完全免费、完全 PIT。学术证据表明基本面动量与分析师修正因子高度同源——新手阶段用它替代，不丢多少信息。

### 1.4 持仓、内部人与空头数据

| 来源 | 内容 | 频率 | 成本 |
|---|---|---|---|
| EDGAR 13F | 机构持仓 | 季度（45 天滞后） | 免费 |
| EDGAR Form 4 | 内部人买卖 | 准实时（2 日内） | 免费 |
| **FINRA Short Interest** | 全市场空头持仓（short interest） | 每月两次（月中/月末结算日，数日后发布） | 免费 |
| ETF 发行商官网（iShares/SSGA/VanEck/Global X） | **ETF 每日全持仓 CSV** | 每日 | 免费 |

ETF 持仓 CSV 是被低估的宝藏：等于**指数公司免费替你做了主题分类和权重研究**，也是构建 AI 股票池的最快路径（见 §2.3）。

### 1.5 宏观与利率

| 来源 | 内容 | 备注 |
|---|---|---|
| **FRED**（圣路易斯联储） | 数万条宏观序列，API 免费 | 利率、通胀、金融条件，一站式 |
| **ALFRED** | FRED 的**vintage（原始发布值）**版本 | ⚠️ 宏观数据会修订——回测必须用"当时看到的值"，ALFRED 就是宏观界的 point-in-time |
| 美债收益率曲线 | Treasury 官网每日 | 折现率是长久期成长股（AI 股全是）的第一敏感项 |
| BLS / BEA / EIA | 就业、GDP、能源电力 | EIA 电力数据见 §2.2 |

3~5 年持有期意味着你必然穿越利率周期。AI 股是长久期资产，**真实利率上行 = 估值压缩**，这一层不用来择股，用来控制主题仓位与预期管理。

### 1.6 学术因子库（免费的"标准答案"）

| 来源 | 内容 | 用途 |
|---|---|---|
| **Ken French Data Library** | Mkt/SMB/HML/RMW/CMA/动量因子收益，1926 年至今，另有 49 个行业组合 | **一切回测的归因基准**；也是你学因子体系的教材数据 |
| **Open Source Asset Pricing**（Chen & Zimmermann, openassetpricing.com） | 200+ 篇已发表异象的复制收益序列，免费 CSV | 想验证某因子"学界成绩单"时直接查，不用自己重跑 |
| AQR Data Library | QMJ、BAB 等因子月度收益 | 补充 |

### 1.7 股票池与行业分类

| 需求 | 免费方案 | 陷阱 |
|---|---|---|
| 大盘股池 | iShares IWB（Russell 1000）每日持仓 CSV；Wikipedia S&P 500 成分表 + 历史变更表 | ⚠️ 用**今天的**成分做历史回测 = 前视偏差（§4.4） |
| 行业分类 | EDGAR 的 SIC code（免费）；GICS 是付费的 | SIC 粗糙但够用；行业中性化时用 |
| 主题分类 | AI 相关 ETF 持仓并集（§2.3）；EDGAR 全文检索关键词法 | 主题池必须留存**每日快照**，从今天开始存 |

---

## 2. AI 主题专属的公开数据抓手

### 2.1 先建产业链地图（截面研究的"行业中性化"骨架）

```
上游：芯片设计（NVDA/AMD/AVGO/MRVL）→ 制造（TSM）→ 设备（ASML/AMAT/LRCX/KLAC）→ 存储（MU/SK海力士）
中游：服务器/整机（SMCI/DELL）→ 网络（ANET/CRDO）→ 数据中心 REIT（DLR/EQIX）→ 电力设备（VRT/ETN）
下游：云 hyperscaler（MSFT/GOOGL/AMZN/META/ORCL）→ 模型/应用（软件 SaaS）→ 电力供给（公用事业）
```

截面打分应**在链条环节内部比较**（设备股跟设备股比），跨环节比较的是景气度传导，两者不要混在一个分数里。

### 2.2 高频公开信号（这些是真金白银，且全部免费）

| 信号 | 来源 | 频率 | 为什么有用 |
|---|---|---|---|
| **TSMC 月度营收** | 台湾上市公司法定月披露（每月 10 日前，TSMC IR 官网） | **月度** | 全球 AI 芯片产能的单一最高频基本面读数；台积电月营收加速/减速领先美股半导体财报一个季度 |
| 其他台链月营收（鸿海、广达、纬创、台达电） | 同上（台湾证交所 MOPS） | 月度 | AI 服务器组装环节的出货节奏 |
| **韩国半导体出口（10 日 / 20 日快报）** | Korea Customs Service | **旬度** | 全球芯片周期最快的宏观代理变量 |
| **WSTS/SIA 全球半导体销售额** | 免费月度新闻稿（3 个月移动平均） | 月度 | 行业景气锚 |
| **SEMI 北美设备商 billings** | SEMI 月度报告 | 月度 | 设备环节（AMAT/LRCX/KLAC）景气前瞻 |
| **Hyperscaler capex** | MSFT/GOOGL/AMZN/META 10-Q 现金流量表"购置 PP&E"科目 + 财报电话会指引 | 季度 | **本轮 AI 红利的总阀门**——四家 capex 合计增速是整条产业链的营收领先指标；自建一张季度追踪表，手工维护即可 |
| NVDA 数据中心分部营收 | 10-Q segment 披露 | 季度 | 需求端确认 |
| **数据中心电力需求** | EIA 州级/部门用电量（VA/TX/GA 等数据中心集群州） | 月度 | 物理世界不会撒谎——电表比 PPT 诚实 |
| AI 招聘强度 | Indeed Hiring Lab（免费聚合指数）；Google Trends | 周/月 | 公司层面的扩张意愿代理 |
| 开源生态热度 | Hugging Face 下载量、GitHub star/commit（公开 API） | 实时 | 对模型层/开发工具类公司的采用度代理 |
| 财报电话会文本 | Motley Fool 免费 transcript、公司 IR 官网 | 季度 | 管理层措辞变化（capex 指引、"digestion"之类的词）；可做文本因子 |

> 经验之谈：**主题投资死于"故事仍在、数字先变"**。上表前六行就是"数字"——每月例行看一遍，比读一百篇研报有用。2000 年的教训是网络流量增速先于纳指见顶回落；这一轮对应物就是 hyperscaler capex 增速与 TSMC 月营收增速。

### 2.3 AI 股票池的构建（point-in-time！）

1. **ETF 持仓并集法**（快）：SOXX + SMH + IGV + AIQ + BOTZ + CIBR 持仓并集，每日从发行商官网抓 CSV 存档。⚠️ 历史持仓难以免费回补——**从今天开始每天存**，一年后你就拥有别人没有的 PIT 主题池。
2. **EDGAR 全文检索法**（可回溯）：统计历年 10-K 中 AI 相关关键词的提及密度，规则化打标签。优点是可回溯到 2001 年、完全 PIT；缺点是要清洗蹭热点的公司（关键词密度突增但 R&D/capex 不动的，是嘴上 AI）。
3. 交集使用：ETF 法定宽度，文本法定纯度。

---

## 3. 新手最小可行数据栈（MVD Stack）

**全免费，含金量却覆盖研究所需的 90%：**

| 层 | 选型 | 落地格式 |
|---|---|---|
| 股票池 | Russell 1000（IWB CSV）+ AI ETF 并集（§2.3），每日快照 | `universe/YYYY-MM-DD.parquet` |
| 行情 | Tiingo API（主）+ yfinance（校验），日线复权 | `prices/` parquet，列含 raw 与 adj |
| 基本面 | edgartools → companyfacts → 自建 PIT 表（**以 filed date 为时间戳**） | `fundamentals/` parquet |
| 因子基准 | Ken French 月度因子 + Open Source Asset Pricing | `benchmarks/` |
| 宏观 | FRED/ALFRED API | `macro/` |
| 主题高频 | TSMC 月营收、WSTS、SEMI、capex 追踪表（手工季度维护） | `theme/` 一张 CSV 起步即可 |
| 因子分析 | **alphalens-reloaded**（IC、分层、换手率一条龙） | notebook |
| 回测 | 先用 pandas 手写月频框架（几百行足够，还能逼你理解每个环节）；进阶再看 vectorbt / zipline-reloaded / MS qlib | `factor_research/` |

**何时付费（明确的升级触发条件）：**

- 当你要做**认真的历史回测**（>3 年、含中小盘）→ 幸存者偏差不可接受 → **Sharadar**（Nasdaq Data Link 上的股票+基本面包，退市股全含，个人价位）或 **Norgate Data**（含历史指数成分归属标记，回测股票池神器）。
- 需要 PIT 分析师预期 → 只有机构级方案，个人阶段用 §1.3 的 SUE 平替。
- **永远不需要 Bloomberg** 来做这件事。

---

## 4. 数据陷阱：新手死亡名单（按杀伤力排序）

在 RenTech，数据清洗占研究工作量的八成。以下每一条都毁掉过真实的回测：

### 4.1 幸存者偏差（Survivorship Bias）——头号杀手
yfinance 只返回**今天还活着**的股票。用它回测"2021 年的 AI/成长股池"，你自动跳过了所有已退市、已崩盘的标的，年化收益凭空虚增数个百分点。**主题股池的死亡率远高于大盘**——2000 年那一轮，回头看只看得见 Amazon，看不见 Pets.com；这一轮 3~5 年内，今天的热门名单里**一定**有几家消失。对策：短期先只做大盘池（Russell 1000 死亡率低）+ 尽早换 Sharadar/Norgate。

### 4.2 前视偏差 / Point-in-Time——次号杀手
- 财报数据必须以 **filed date（申报日）** 而非 period end（报告期末）为可用时间戳：Q1 的数字要到 5 月才看得见。
- yfinance 的基本面字段是**当前快照**，会被追溯修改——**绝对不能进回测**，只能用于实盘当日筛选。
- 宏观数据用 ALFRED vintage，不用 FRED 修订后终值。
- 财报重述（restatement）会覆盖商业数据商的历史值；EDGAR 的 as-filed 原文永远保留第一版——这就是自建 PIT 库的意义。

### 4.3 复权与公司行动
拆股（NVDA 2024 年 1 拆 10）、分红再投资。回测收益一律用**复权价计算、原始价核对成交可行性**。两列都存。

### 4.4 股票池漂移（Universe Look-ahead）
用今天的 S&P 500 名单回测 2020 年 = 你提前知道了谁会被纳入。指数成分必须用**当期名单**（Wikipedia 变更表可粗略重建；Norgate 有精确标记）。主题池同理——所以 §2.3 强调从今天开始存每日快照。

### 4.5 报告滞后
10-Q 滞后 40~45 天，13F 滞后 45 天。信号构建时一律按"该数据的公开可得日"再加一天保守偏移。

### 4.6 交易成本与流动性
月频、大盘股、long-only 的情况下成本温和，但仍要建模（单边 5~10 bp 起步假设）。小盘 AI 概念股点差与冲击成本会吃光纸面 alpha——这也是新手先做大盘池的第二个理由。

> **铁律**：任何回测结果，先问"这五条陷阱我踩了几条"，再问收益率。一个诚实的年化 8% 胜过一个虚假的 40%。

---

## 5. 信号 → 数据映射（预研清单，未立项）

| 候选信号族 | 需要的数据 | 免费可得？ |
|---|---|---|
| 价格动量（12-1 个月） | 复权日线 | ✅ |
| 基本面动量 / SUE | EDGAR PIT 财报 | ✅ |
| Capex + R&D 强度（AI 投入真实性） | 10-K/10-Q 现金流量表与费用科目 | ✅ |
| 盈利质量（应计项、FCF 转化率） | EDGAR | ✅ |
| 估值（EV/Sales、FCF yield，成长股慎用 PE） | EDGAR + 行情 | ✅ |
| 内部人净买入 | Form 4 | ✅ |
| 空头拥挤度 | FINRA short interest | ✅ |
| 分析师盈利修正 | IBES | ❌（用 SUE 平替） |
| 产业链景气传导（上游月度数据 → 下游个股） | §2.2 全表 | ✅ |

先跑通前两个（动量 + SUE）：文献最扎实、数据最干净、实现最简单。**一个新手能把这两个因子在无偏差数据上跑出与文献一致的结果，就已经超过 90% 的散户了。**

---

## 6. 工程落地与本仓库的关系

- **FreqTrade 不适用于截面策略**（它是单标的时序引擎）。本策略另起独立 pipeline，建议目录：`factor_research/`（data / factors / backtest / notebooks），与 `user_data/` 平行，不污染 FreqTrade 加载路径。
- 数据统一落 parquet（与现有 feather 习惯一致），列名规范先行。
- 回测框架决策（pandas 手写 vs vectorbt vs zipline-reloaded）**推迟到数据层跑通之后**——新手常犯的错误是先挑框架后建数据，顺序反了。

## 7. 下一步（可勾选）

- [ ] 注册 Tiingo / FRED API key，写 `data_ingest` 脚本（行情 + 宏观）
- [ ] edgartools 跑通一家公司（建议 NVDA）的 companyfacts → PIT 表 demo
- [ ] 开始每日存档 AI ETF 持仓 CSV（越早开始越值钱）
- [ ] 建 hyperscaler capex 季度追踪表（手工，4 家 × 8 个季度回填）
- [ ] 下载 Ken French 因子，写归因模板 notebook
- [ ] 用 alphalens 跑通第一个因子（12-1 动量）的 IC / 分层测试
- [ ] 读物配套：《Quantitative Momentum》（Gray）、AQR 与 French 库文档、Chen-Zimmermann 论文

## 8. 参考入口（URL 速查）

- SEC EDGAR 全文检索：https://www.sec.gov/edgar/search/ ｜ XBRL API：https://data.sec.gov
- Ken French Data Library：https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html
- Open Source Asset Pricing：https://www.openassetpricing.com
- FRED / ALFRED：https://fred.stlouisfed.org ｜ https://alfred.stlouisfed.org
- FINRA short interest：https://www.finra.org/finra-data
- Tiingo：https://www.tiingo.com ｜ Polygon：https://polygon.io
- Sharadar（Nasdaq Data Link）：https://data.nasdaq.com ｜ Norgate：https://norgatedata.com
- TSMC 月营收：https://pr.tsmc.com（IR → Monthly Revenue）
- WSTS：https://www.wsts.org ｜ SEMI：https://www.semi.org
- EIA 电力：https://www.eia.gov/electricity/ ｜ Indeed Hiring Lab：https://www.hiringlab.org
- 工具：edgartools（GitHub: dgunning/edgartools）、alphalens-reloaded、zipline-reloaded（stefan-jansen）、Microsoft qlib、OpenBB
