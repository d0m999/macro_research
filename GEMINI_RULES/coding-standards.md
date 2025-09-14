---
inclusion: manual
---

# Coding Standards 💻

## Code Writing Principles
- Write concise, efficient code
- ALWAYS COMMENT YOUR CODE
- NEVER ERASE OLD COMMENTS IF THEY ARE STILL USEFUL

## Commenting Standards
- Use clear and concise language
- Avoid stating the obvious (e.g., don't just restate what the code does)
- Focus on the "why" and "how" rather than just the "what"
- Use single-line comments for brief explanations
- Use multi-line comments for longer explanations or function/class descriptions
- Ensure comments are JSDoc3 styled

## Trading Strategy Comments Requirements (MANDATORY)
- Entry/Exit conditions
- Risk management parameters
- Backtesting performance data
- Known limitations under specific market conditions

## Code Quality Requirements
- Prioritize vectorized operations over loops (applicable to Python/Pandas)
- Implement efficient data caching mechanisms
- Optimize strategy calculation processes to avoid redundant computations
- Pay attention to memory management, especially when handling large historical datasets

## Important Reminder
The user has to manually give you code base files to read! If you think you are missing important files ask the user to give you the info before continuing.

## 安全编码
* 输入验证: “永远不要相信外部输入”。
* 输出编码: 在将数据显示在UI或写入不同系统时进行编码。
* 参数化查询: 访问数据库时必须使用参数化查询或安全的 ORM。
* 最小权限原则: 代码执行时应使用尽可能低的权限。