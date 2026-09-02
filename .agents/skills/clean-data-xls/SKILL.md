---
name: clean-data-xls
description: "清理用户提供的 spreadsheet 数据，标准化文本、数字、日期和重复项，并保留原文件与审计轨迹。"
---

# Clean Data XLS

清理用户提供的 workbook 或 range，不用外部数据填补缺失内容。先读取 [`../../CODEX-EXECUTION-POLICY.md`](../../CODEX-EXECUTION-POLICY.md)，默认输出副本并保留原文件。

## 工作流

1. **定义范围**：使用用户指定 range/sheet；未指定时处理 workbook 的 used ranges。记录输入路径、输出副本路径和 excluded sheets。
2. **Profile**：按 column 识别 dominant type、null、unique、mixed type 和异常值；先记录检测结果与拟采用的确定性转换。
3. **清理副本**：依次处理 whitespace/non-printing characters、casing、number-as-text、dates、duplicates、blanks 和 formula errors。保留原始列或建立可追踪 helper column；不改变金融口径。
4. **记录 audit trail**：列出 sheet/range、rule、affected rows、before/after samples、无法确定的 ambiguous cases 和跳过项。
5. **验证**：检查 row/column counts、keys、types、公式引用、dates、duplicates 和输出结构；运行统一 artifact 验证器。

## 安全边界

- 默认文件名使用可辨识的 cleaned copy；用户只要求“清理”不等于授权覆盖原文件。
- 只有用户明确要求原地覆盖时才执行破坏性写入；这是需要暂停确认的例外。
- 自动处理确定性修复；对会改变业务含义的日期、编码、分类、dedup key 或 blank fill 保持未修改并列入 ambiguity report，除非规则已由用户给出。
- 不要求每一类修复后逐轮确认；完整授权下连续执行并在最终报告中给出分项结果。
- 公式能透明表达的转换优先使用公式/helper column；静态清洗值必须保留 before/after 审计证据。

## 完成条件

- 原文件存在且未改变；清理副本路径明确。
- 所有修改由确定性规则或用户规则支持；ambiguous cases 没有被猜测处理。
- 结构检查通过；本地回退披露 `FORMULA_EVALUATION_UNVERIFIED`。
