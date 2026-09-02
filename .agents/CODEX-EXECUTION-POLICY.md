# Codex Financial Artifact Execution Policy

本文件是项目内金融 skill 生成或修改 Office artifact 的单一执行契约。具体 skill 只定义业务内容、输入和完成条件，不重复工具实现。

## 能力路由

按产物格式选择当前会话可用的 Codex artifact capability，能力名称不绑定安装路径或版本：

- `.xlsx`：Spreadsheets
- `.pptx`：Presentations
- `.docx`：Documents

先读取对应 capability 的说明并按其工作流创建、编辑、渲染和验证 artifact。只有当前会话确实没有对应 capability 时，才使用本机回退：

- `.xlsx`：`python3` 与 `openpyxl`
- `.pptx`：`python3` 与 `python-pptx`
- `.docx`：`python3` 与 `python-docx`

回退依赖缺失时，报告缺失依赖和未完成产物，不把占位文件当成交付物。使用回退时不得假设存在未在仓库内提供的脚本、服务或运行时。

## 连续执行与暂停边界

用户已授权完整任务时，内部按依赖顺序执行并在各阶段自行校验，不要求用户逐段重复授权。只有下列情况暂停并请求输入：

- 缺少会实质改变结果的关键业务选择或必需输入；
- 需要原地覆盖、删除或不可逆修改用户文件，且用户未明确要求；
- 需要发送邮件、提交材料、发布、交易或其他外部状态变更；
- 用户明确要求在检查点停下。

默认将修改后的 artifact 写入新文件，保留用户原文件。路径、格式和文件名应与用户要求一致；没有要求时使用可辨识的副本名称。

## 回退验证边界

所有回退产物运行：

```bash
python3 .agents/scripts/validate_financial_artifact.py <file>
```

验证器检查 OOXML 包结构和可读取的公式文本，不计算 Excel 公式，也不证明业务数字正确。

- 本地 Excel 回退必须披露 `FORMULA_EVALUATION_UNVERIFIED`。公式存在但没有由原生 spreadsheet capability 或用户实际打开重算时，不得声称公式结果已验证。
- PPTX/DOCX 若未由原生 capability 完整逐页渲染，只做结构检查并尽可能生成 Quick Look 缩略图，披露 `FULL_RENDER_UNVERIFIED`。缩略图只覆盖有限视觉状态，不等于逐页审阅。
- `pass_with_limitations` 是受限成功，不得改写成无保留的“全部通过”。`fail` 必须修复结构错误或明确说明未交付。

## 业务与来源验证

Artifact 结构验证不能替代金融验证。交付前仍须：

1. 按 [`PUBLIC-SOURCE-POLICY.md`](PUBLIC-SOURCE-POLICY.md)核对事实、期间、单位、来源状态和 source record。
2. 检查公式依赖、勾稽、敏感性中心值和关键输出；无法求值的部分按上述限制披露。
3. 对演示文稿和文档检查页数、标题、表格/图表数量、引用链接和关键数字一致性；未完整渲染时保留限制。
4. 报告输出路径、验证器状态和全部 limitations。
