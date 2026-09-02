# PowerPoint Template Inspection Schema

只在盘点用户模板并编写 layout catalog 时读取。

对每个 master/layout 记录：

```text
layout_name
layout_id
intended_use
page_size
placeholders: name, type, position, size, required_or_optional
fixed_shapes: name, role, editable
title_style
body_style
table_style
chart_style
source_area
logo_safe_area
overflow_rule
example_slides
```

把 template 中实际复用的 shape 命名和约束写入 reference；不要把偶然的单页内容升格为全局规则。Fonts、colors、logos 和 images 只来自用户提供的模板/资产。

生成样例时覆盖至少一个主要 layout 和一个包含 table/chart/image 的复杂 layout（若模板存在），并记录不能完整渲染或缺失字体的限制。
