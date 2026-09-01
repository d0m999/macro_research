# Claude Financial Services 官方 Workflow 检索

检索日期：2026-08-31
上游仓库：<https://github.com/anthropics/financial-services>
检索范围：官方仓库 `main` 分支的根 README、vertical skills、commands 和 named agent prompts。

## 结论

官方包确实提供推荐的 workflow，但不是一条覆盖所有任务的单一总流程，而是三层结构：

1. 根 README 给出安装和组合方式：先安装 `financial-analysis` 核心，再按职能增加 vertical plugin 或 named agent。
2. Named agents 提供端到端 workflow，例如 `Market Researcher`、`Earnings Reviewer` 和 `Model Builder`。
3. 各个 skill/command 提供局部 workflow，例如 `sector-overview`、`initiating-coverage`、`earnings-analysis`、`3-statement-model`、`comps-analysis` 和 `dcf-model`。

因此，官方推荐的是“按问题选择 Agent/command，再由其调用相关 skills”，不是让用户把全部 skills 无条件串起来。

## 官方明确写出的层级关系

官方根 README 将组件分成：

- `Agents`：拥有端到端流程的自包含插件；
- `Skills`：领域知识、规范和逐步方法；
- `Commands`：用户显式触发的 slash actions；
- `Connectors`：连接机构数据和文档系统的 MCP。

官方根 README 同时写明，`financial-analysis` 是核心，包含共享建模 skills 和数据连接器，其他 vertical 按工作需要增加。Named agent 则是已经把相关 skills 组合好的起点。来源：

- [官方根 README：Agents、How It Fits Together、Getting Started](https://github.com/anthropics/financial-services/blob/main/README.md)

## 与公司研究最相关的官方 workflow

### 1. 行业或主题研究：`Market Researcher`

这是官方最明确的“行业研究端到端 workflow”：

1. 明确 sector/theme、研究角度和 universe，确定 8–15 个代表性公司；
2. 调用 `sector-overview`，完成市场规模、增长、产业结构、驱动因素和 why-now；
3. 调用 `competitive-analysis`，梳理参与者、定位和近期变化；
4. 调用 `comps-analysis`，统一口径铺开 peer multiples；
5. 调用 `idea-generation`，从行业格局和 comps 中筛选主题表达标的；
6. 组装 research note，若需要再调用 `pptx-author`。

官方还明确说明该 Agent 适合 sector/theme primer，不适合单一公司的 coverage update。来源：

- [官方 Market Researcher agent prompt](https://github.com/anthropics/financial-services/blob/main/plugins/agent-plugins/market-researcher/agents/market-researcher.md)

### 2. 新公司首次覆盖：`initiating-coverage`

这是官方最完整、依赖关系最清楚的公司研究 workflow，共 5 个任务：

1. `Task 1 - Company Research`：公司、管理层、产品、行业、竞争和风险；
2. `Task 2 - Financial Modeling`：历史财务、预测、情景和模型；
3. `Task 3 - Valuation Analysis`：DCF、可比公司和估值结论；
4. `Task 4 - Chart Generation`：基于前面产物和外部市场数据生成图表；
5. `Task 5 - Report Assembly`：汇总成最终报告。

依赖关系是：Task 1 和 Task 2 可以按任意顺序先做；Task 3 依赖 Task 2；Task 4 依赖 Task 1、2、3；Task 5 依赖全部前置任务。

这个 workflow 有一个重要执行约束：每次只执行一个 task，完成并交付后等待用户明确请求下一个 task；不能自动把 5 个 task 串行跑完。来源：

- [官方 `initiating-coverage/SKILL.md`](https://github.com/anthropics/financial-services/blob/main/plugins/vertical-plugins/equity-research/skills/initiating-coverage/SKILL.md)
- [官方 `/initiate` command](https://github.com/anthropics/financial-services/blob/main/plugins/vertical-plugins/equity-research/commands/initiate.md)

### 3. 已覆盖公司、财报后更新：`Earnings Reviewer`

官方 `Earnings Reviewer` 的端到端顺序是：

1. 拉取本次业绩及历史/市场预期；
2. 调用 `earnings-analysis` 读取业绩、指引和管理层表述；
3. 调用 `model-update` 更新 coverage model；
4. 调用 `audit-xls` 做模型 QC；
5. 调用 `morning-note` 起草更新稿；
6. 以 draft 形式提交人工 review，不直接发布。

官方 `/earnings` command 也把财报发布、10-Q、电话会、投资者材料、共识预期和 beat/miss 分析列为输入。来源：

- [官方 Earnings Reviewer agent prompt](https://github.com/anthropics/financial-services/blob/main/plugins/agent-plugins/earnings-reviewer/agents/earnings-reviewer.md)
- [官方 `/earnings` command](https://github.com/anthropics/financial-services/blob/main/plugins/vertical-plugins/equity-research/commands/earnings.md)
- [官方 `earnings-analysis/SKILL.md`](https://github.com/anthropics/financial-services/blob/main/plugins/vertical-plugins/equity-research/skills/earnings-analysis/SKILL.md)

### 4. 只需要建模或估值：`Model Builder`

官方 `Model Builder` 的顺序是：

1. 获取历史数据、共识和 filings；
2. 按模型类型调用 `dcf-model`、`lbo-model`、`3-statement-model` 或 `comps-analysis`；
3. 调用 `audit-xls` 审计模型；
4. 生成敏感性分析；
5. 停下来交给用户 review。

该 Agent 特别适合从零建模，不适合更新已有 coverage model。来源：

- [官方 Model Builder agent prompt](https://github.com/anthropics/financial-services/blob/main/plugins/agent-plugins/model-builder/agents/model-builder.md)

## 官方 commands 提供的入口

官方 `equity-research` vertical 暴露的主要命令包括：

| Command | 官方用途 |
|---|---|
| `/sector` | 创建行业/sector overview |
| `/initiate` | 开始 5-task initiating coverage workflow |
| `/earnings` | 创建季度业绩更新 |
| `/model-update` | 用新业绩、指引或假设更新模型 |
| `/catalysts` | 查看或更新 catalyst calendar |
| `/thesis` | 创建或更新 investment thesis |
| `/morning-note` | 起草 morning meeting note |
| `/earnings-preview` | 业绩前预览 |
| `/screen` | 按条件筛选公司 |

官方 commands 目录可直接核对这些入口及其参数提示：

- [官方 equity-research commands 目录](https://github.com/anthropics/financial-services/tree/main/plugins/vertical-plugins/equity-research/commands)

## 对我们 public-only Codex 包的含义

当前项目级 Codex skills 只导入了 41 个 source `SKILL.md`，没有导入官方 named agents、commands、MCP 配置或 agent bundled 副本。因此，官方的 Agent 级编排目前不是本地可直接调用的命令，而是需要在 Codex 中按 skills 手动复现。

推荐的 public-only 映射如下：

| 官方层级 | Codex public-only 对应方式 |
|---|---|
| `Market Researcher` | `sector-overview` → `competitive-analysis` → `comps-analysis` → `idea-generation` |
| `initiating-coverage` | 先做公司研究和历史模型，再做估值；每个阶段单独确认 |
| `Earnings Reviewer` | `earnings-analysis` → `model-update` → `audit-xls` → `morning-note` |
| `Model Builder` | `3-statement-model` / `dcf-model` / `comps-analysis` → `audit-xls` → sensitivity |

在 public-only 版本中，官方 Agent prompt 中依赖的 CapIQ、FactSet、Daloopa、Bloomberg、电话会 transcript 数据和 analyst consensus 不能默认视为可用。应按 [`.agents/PUBLIC-SOURCE-POLICY.md`](../.agents/PUBLIC-SOURCE-POLICY.md) 执行：

- SEC EDGAR、`data.sec.gov`、公司 IR 和政府/监管机构页面可以作为公开来源；
- 用户提供的文件标记为 `USER_PROVIDED`，不能伪装成公共数据；
- 找不到公开且可核验的 consensus、whisper、历史估值倍数或 transcript 时，使用 `SOURCE_UNAVAILABLE`；
- 预测值只能来自公司公开 guidance、用户提供的估计或明确标记的 `MODEL_DERIVED` 情景；
- 不应写“beat/miss consensus”，除非有带日期的公开共识来源或用户提供的共识输入。

## 最终判断

答案是“有，但要区分两种官方 workflow”：

- 如果问“官方有没有一套完整的公司研究顺序”，有，最接近的是 `initiating-coverage` 的 5-task workflow；
- 如果问“行业研究、财报更新、建模分别怎么组合”，官方通过 `Market Researcher`、`Earnings Reviewer` 和 `Model Builder` 三个 named agents 给出了更实用的组合顺序；
- 如果问“我们的 public-only 项目级 skills 能否原样运行官方 workflow”，不能。官方组合关系可以保留，但所有付费/权限数据入口必须替换为公开来源或显式标记不可用。
