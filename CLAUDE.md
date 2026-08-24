# Project Instructions

## Scope

本仓库当前以 TradingView PineScript 研究指标、OI 逻辑、策略研究笔记和可视化 artifact 为主。

Python/FreqTrade 程序化交易引擎、回测运行环境、交易数据库、Dashboard 和 Docker 部署已经移出当前工作区。未经明确授权，不要重新引入 Python 交易执行层。

## 主要目录

- `PineScript/`：Pine v6 研究指标。按 `_L∞p/`、`Open Interest/`、`Oscillator/`、`Price_Zones/`、`Vol/` 分类。
- `strategy-notes/`：策略假设、指标组合、OI 语义和待验证事项。
- `strategy-notes/design/`：OI 面板及相关视觉研究 artifact；当前同时保留已跟踪基线与本地未跟踪版本。
- `open-interest-logic.md`：OI 方向、门限、veto 和可视化语义的补充说明。
- `docs/`：与研究流程相关的文档；不要把已移除的 Python/FreqTrade 运行说明加回来。

## 研究约束

- 先确认 Pine 文件的输入源、时间周期、是否使用未收线数据和重绘边界，再修改信号逻辑。
- `ΔOI` 的符号语义、价格方向着色、幅度门限和 veto 状态必须分开，显示降噪不得改变裁决真值。
- 研究指标和设计 artifact 的状态要分开描述；打开 mockup 不代表 Pine 已实现同等功能。
- 不把 TradingView 价格/永续数据自动等同于原生交易所 OI；数据来源必须在注释或研究笔记中写清楚。

## 验证方式

- PineScript：优先做静态扫描、版本/语法检查和 TradingView 内的人工编译与图表验收。
- 研究 artifact：核对文件版本、Git 状态和数据来源，不覆盖用户的未跟踪文件。
- 当前没有 Python 测试或程序化交易运行命令。

## Git 约束

- 保留用户已有的未跟踪 artifact；不要使用 `git add -A`、强制重置或覆盖式清理。
- 修改、提交、推送和发布是分开的授权；本仓库默认只做本地修改。

## Agent skills

### Issue tracker

Issues and specs are tracked in this repository's GitHub Issues via `gh`. See `docs/agents/issue-tracker.md`.

### Triage labels

Use the five canonical triage labels defined for this repository. See `docs/agents/triage-labels.md`.

### Domain docs

This repository uses a single-context layout with root `CONTEXT.md` and `docs/adr/`. See `docs/agents/domain.md`.
