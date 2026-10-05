---
name: earnings-analysis
description: "分析用户指定或最新季度财报，更新关键指标、估计、估值和 thesis。用于财报分析、季度复盘、业绩更新、earnings update；指定历史期间优先，只有“最新”才寻找最新季度。"
---

# Earnings Analysis

分析指定财报期间，并生成适合当前受众的 earnings update。公司尚未建立覆盖不是拒绝条件；缺少历史模型、consensus 或 prior thesis 时，明确列为缺失基线并继续完成可支持的分析。

## 必读契约

- 收集数据前读取 [`../../PUBLIC-SOURCE-POLICY.md`](../../PUBLIC-SOURCE-POLICY.md)。
- 具体数据源路由以 [`../../data-sources.jsonl`](../../data-sources.jsonl) 为准（本项目 skill 数据源路由的单一事实来源）：按 `data_types` × `markets` 过滤，经 `policy_status`/`auth`/`cost` 校验；无匹配时 fail-closed。
- 创建或修改 `.docx`/`.xlsx` 前读取 [`../../CODEX-EXECUTION-POLICY.md`](../../CODEX-EXECUTION-POLICY.md)。
- 执行期间定位、材料收集和分析时读取 [`references/workflow.md`](references/workflow.md)。
- 需要正式报告结构时读取 [`references/report-structure.md`](references/report-structure.md)。
- 最终 QC 时读取 [`references/best-practices.md`](references/best-practices.md)。

## 期间规则

- 用户指定 fiscal quarter、calendar quarter、FY、发布日期或历史期间时，以该期间为准；不得跳转到“最新”。
- 只有用户说“最新”“最近一期”或没有提供期间且任务明确需要当前结果时，才定位最新已发布季度。
- 无论新旧期间，都验证 earnings release、filing、transcript/webcast 和 supplement 属于同一 fiscal period；不以“距今天三个月”作为有效性门槛。

## 输入与比较基线

Actuals 来自 earnings release、10-Q/10-K/8-K 和发行人 supplement。Beat/miss 只相对 dated public guidance、明确的 `USER_PROVIDED` estimate 或本项目先前标记的 `MODEL_DERIVED` estimate；没有基线时写 `SOURCE_UNAVAILABLE`，改为 actual-vs-prior-period 与 guidance analysis。

Forward estimates 只使用 dated issuer guidance、用户输入或有推导说明的 `MODEL_DERIVED` 情景。公开 transcript 不可获得时不从付费/登录页面补齐。

## 工作流

1. **锁定期间**：记录 fiscal quarter/year、period end、release date、filing date、当前日期以及“指定/最新”的选择依据。
2. **建立材料清单**：打开 earnings release、filing、supplement、guidance 和可公开 transcript/webcast；记录 URL、日期和定位。
3. **标准化 actuals**：核对 revenue、EPS、margin、segments、KPIs、cash flow、balance sheet 和一次性项目的期间、单位与 GAAP/adjusted 口径。
4. **分析差异**：相对有效基线计算 variance；解释 driver 时区分公司陈述与分析推断。
5. **更新 outlook**：比较 current/prior guidance；如有模型，建立 old-to-new estimate bridge 和 valuation impact；无模型则列出缺失基线，不伪造精确变动。
6. **更新 thesis**：说明结果支持、削弱或未触及哪些 thesis 条件，并列出催化剂、风险和待验证问题。
7. **生成并验证产物**：报告长度、表格和图表数量由用户要求与证据决定；检查关键数字、链接、期间和 artifact 限制。

## 完成条件

- 分析期间与用户要求一致；材料日期和 fiscal period 匹配。
- 每个 beat/miss、guidance 和 estimate change 都有有效比较基线；缺失项没有被模型记忆补齐。
- 公司未覆盖时已披露缺少 historical model/estimate baseline，但仍完成 actuals、guidance、drivers、risks 和可支持结论。
- 交付路径、source list、验证状态及 `FULL_RENDER_UNVERIFIED`/`FORMULA_EVALUATION_UNVERIFIED`（如适用）已报告。
