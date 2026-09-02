# Datapack Schema

只在定义 data contract 或新建 workbook 时读取。

## Source manifest fields

```text
source_id
source_type
publisher
url_or_path
document_title
published_at
accessed_at
period_end
status
citation_locator
notes
```

## Data row fields

```text
entity
metric_id
reported_label
period_start
period_end
period_type
currency
unit
reported_value
normalized_value
adjustment_formula
source_id
fact_or_assumption
status
notes
```

`Raw` 层不覆盖原值；`Normalized` 层显示转换；`Calculations` 只引用前两层；`Summary` 不新增无法回溯的 hardcode。
