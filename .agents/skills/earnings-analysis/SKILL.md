---
name: earnings-analysis
description: "分析指定财报期间的业绩与经营指标，并生成适合当前受众的 earnings update。actual 未发布时做前瞻（指标清单、公开 guidance 基线、bull/base/bear 情景）；已发布时做复盘（actuals 标准化、variance、guidance 桥、thesis 与估值影响）；涉及 ARR、cohort、retention、CAC/LTV、payback、revenue quality 时进入单位经济深挖。用于财报分析、季度复盘、业绩更新、earnings update、财报前瞻、earnings preview、SaaS/订阅指标或单位经济分析。指定历史期间优先，只有“最新”才寻找最新季度。"
---

# Earnings Analysis

覆盖单个财报期间的完整分析。公司尚未建立覆盖不是拒绝条件；缺少历史模型、consensus 或 prior thesis 时，明确列为缺失基线并继续完成可支持的分析。

## 必读契约

- 来源合规与数据源路由遵循 [`../../PUBLIC-SOURCE-POLICY.md`](../../PUBLIC-SOURCE-POLICY.md)（含路由登记表 [`../../data-sources.jsonl`](../../data-sources.jsonl)，无匹配时 fail-closed）。
- 创建或修改 Office 产物前读取 [`../../CODEX-EXECUTION-POLICY.md`](../../CODEX-EXECUTION-POLICY.md)；验证器状态与限制按其口径披露。
- 执行期间定位、材料收集和分析时读取 [`references/workflow.md`](references/workflow.md)。
- 需要正式报告结构时读取 [`references/report-structure.md`](references/report-structure.md)。
- 最终 QC 时读取 [`references/best-practices.md`](references/best-practices.md)。
- 期间未发布、需要前瞻时读取 [`references/pre-release.md`](references/pre-release.md)。
- 需要 ARR/cohort/retention/单位经济时读取 [`references/unit-economics.md`](references/unit-economics.md)。

## 模式判别

- **前瞻（pre-release）**：用户要求的期间尚未发布，或明确说「前瞻」「关注点」「preview」。产出指标清单、公开 guidance 基线、bull/base/bear 情景和催化剂清单。
- **复盘（post-release）**：用户要求的期间已发布。产出 actuals 标准化、variance、guidance 桥、thesis 影响和估值影响。
- **指标深挖（unit economics）**：业务为订阅/用量制，或用户点名 ARR、cohort、NRR、CAC/LTV、payback、revenue quality。可叠加在前述任一模式内。
- 三种模式共用同一套期间规则、来源规则和完成条件。前瞻里在事件前标注 `MODEL_DERIVED` 的 base 情景，到复盘时是有效的比较基线，不需要另造基线。

## 期间规则

- 用户指定 fiscal quarter、calendar quarter、FY、发布日期或历史期间时，以该期间为准；不得跳转到“最新”。
- 只有用户说“最新”“最近一期”或没有提供期间且任务明确需要当前结果时，才定位最新已发布季度。
- 无论新旧期间，都验证 earnings release、filing、transcript/webcast 和 supplement 属于同一 fiscal period；不以“距今天三个月”作为有效性门槛。

## 输入与比较基线

Actuals 来自 earnings release、10-Q/10-K/8-K 和发行人 supplement。Beat/miss 只相对 dated public guidance、明确的 `USER_PROVIDED` estimate 或本项目先前标记的 `MODEL_DERIVED` estimate；没有基线时写 `SOURCE_UNAVAILABLE`，改为 actual-vs-prior-period 与 guidance analysis。

Forward estimates 只使用 dated issuer guidance、用户输入或有推导说明的 `MODEL_DERIVED` 情景。公开 transcript 不可获得时不从付费/登录页面补齐。

## 工作流

复盘模式按依赖顺序执行，细节与判据见 [`references/workflow.md`](references/workflow.md)：

1. **锁定期间**：记录 fiscal quarter/year、period end、release date、filing date、当前日期以及“指定/最新”的选择依据。
2. **建立材料清单**：打开 earnings release、filing、supplement、guidance 和可公开 transcript/webcast；记录 URL、日期和定位。
3. **标准化 actuals**：核对 revenue、EPS、margin、segments、KPIs、cash flow、balance sheet 和一次性项目的期间、单位与 GAAP/adjusted 口径。
4. **分析差异**：相对有效基线计算 variance；解释 driver 时区分公司陈述与分析推断。
5. **更新 outlook**：比较 current/prior guidance；如有模型，建立 old-to-new estimate bridge 和 valuation impact；无模型则列出缺失基线，不伪造精确变动。
6. **更新 thesis**：说明结果支持、削弱或未触及哪些 thesis 条件，并列出催化剂、风险和待验证问题。
7. **生成并验证产物**：报告长度、表格和图表数量由用户要求与证据决定；检查关键数字、链接、期间和 artifact 限制。

前瞻模式改用 [`references/pre-release.md`](references/pre-release.md)：指标清单 → 公开 guidance 基线 → bull/base/bear 情景 → 催化剂清单 → 一页式预览；其中形成的 guidance 比较项在复盘时直接沿用。

指标深挖在任一模式内叠加，按 [`references/unit-economics.md`](references/unit-economics.md) 的五步执行，并单独输出 cohort 与 revenue quality 视图。

用户同时要前瞻与复盘时可分为两份产物交付，但不得把两套口径混在同一张表里。

## 完成条件

- 分析期间与用户要求一致；材料日期和 fiscal period 匹配；指定期间未被“最新”替换。
- 每个 beat/miss、guidance 和 estimate change 都有有效比较基线（含前瞻沿用的事件前 `MODEL_DERIVED` base）；缺失项没有被模型记忆补齐，也没有填入无来源 consensus、whisper number 或期权隐含波动。
- 前瞻产物含按重要性排序且与本公司口径匹配的指标清单、公开 guidance 基线、bull/base/bear 情景和催化剂清单；情景输入只来自公开 guidance、`USER_PROVIDED` 或带推导说明的 `MODEL_DERIVED`。
- 指标深挖中 ARR bridge、cohort、CAC/LTV、retention 和 margin waterfall 的输入来自用户文件或已打开的发行人披露；gross retention 与 NDR 同时呈现，recurring 与非 recurring 分开评估；基准阈值有来源、用户输入或 `MODEL_DERIVED` 标记，固定 best/good/concerning 档位不作为公司事实。
- 公司未覆盖时已披露缺少 historical model/estimate baseline，但仍完成 actuals、guidance、drivers、risks 和可支持结论。
- 事实、管理层陈述与分析推断分开标注；前瞻与复盘分产物交付。
- 交付路径、source list、验证状态及 `FULL_RENDER_UNVERIFIED`/`FORMULA_EVALUATION_UNVERIFIED`（如适用）已报告。
