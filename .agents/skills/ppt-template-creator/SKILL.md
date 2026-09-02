---
name: ppt-template-creator
description: "把用户提供的 PowerPoint 模板蒸馏为可复用的演示文稿 skill，保留 master、layout、品牌资产与可验证生成规则；不直接制作成品 deck。"
---

# PPT Template Creator

把用户提供的 `.pptx` 模板转化为自包含的演示文稿 skill。该 skill 产出“生成规则 + 模板资产”，不是当前任务的成品 presentation。

## 必读契约

- 检查或复制 `.pptx` 前读取 [`../../CODEX-EXECUTION-POLICY.md`](../../CODEX-EXECUTION-POLICY.md)。
- 使用用户提供的 template、fonts、logos 和 brand guidance；不自行下载或补造品牌资产。
- 生成 skill 时遵循当前环境的 `skill-creator`，不要引用本项目已移除的通用 skill 副本。
- 盘点 master、layout 和 placeholders 时读取 [`references/inspection-schema.md`](references/inspection-schema.md)。

## 工作流

1. **保留原件**：复制模板到新 skill 的 `assets/template.pptx`；记录文件 hash、slide count 和 layouts。
2. **盘点设计系统**：识别 master/layout、page size、主题色、字体、标题/正文层级、页脚、logo safe area、占位符和常用组件。
3. **建立 layout catalog**：为每个可复用 layout 记录用途、必需/可选内容、shape/placeholder 定位和 overflow 处理。只写模板中实际存在的模式。
4. **编写入口**：`SKILL.md` 保留选择 layout、填充顺序、关键不变量和完成条件；细节按 layout 分支放入 `references/`，并在对应步骤给出读取条件。
5. **验证样例**：用非金融占位内容生成最小样例，检查 master 继承、字体、溢出、重叠、图片裁切和来源区。验证生成的 skill 和模板 artifact。

## 生成 skill 的必要内容

- `SKILL.md`：用途、输入、layout 路由、工作流、完成条件。
- `assets/template.pptx`：未经无关改动的模板副本。
- `references/`：仅包含确有分支价值的 layout/brand 细节。
- `agents/openai.yaml`：按当前 skill 规范生成，不绑定版本路径。

## 完成条件

- 生成的 skill 可从模板稳定选择并填充至少一个代表性 layout；没有引用不存在的工具或路径。
- 模板原件保留，资产来源清晰；缺失字体或品牌元素被列出。
- `.pptx` 未完整逐页渲染时披露 `FULL_RENDER_UNVERIFIED`，不把缩略图当作完整视觉验收。
