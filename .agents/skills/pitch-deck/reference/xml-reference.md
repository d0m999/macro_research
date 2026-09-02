# PowerPoint OOXML Fallback

只在 Presentations capability 无法保留模板中的特定元素，且修改确实需要 OOXML 级处理时读取。

优先使用统一执行契约中的 Presentations capability。回退时使用 `python3` 与 `python-pptx` 完成其支持的操作；仅对库无法表达的现有 shape property 做最小 OOXML 修改。

## 不变量

- 先复制原件，并只修改目标 part。
- 保留 relationship IDs、master/layout links、theme、embedded media 和 content types。
- 不按数组下标假设 shape 顺序；使用 name、type、placeholder 或明确 ID 定位。
- 修改 XML 前后重新打开 package，检查 slide count 和 relationships。
- 运行统一 artifact 验证器；逐页完整渲染不可用时披露 `FULL_RENDER_UNVERIFIED`。

结构检查不能证明视觉正确。Quick Look 缩略图只用于发现明显损坏，不能替代逐页 review。
