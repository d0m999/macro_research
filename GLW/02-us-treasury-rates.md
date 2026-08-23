# GLW — 美国财政部利率

状态：`PASS`

这是宏观输入，不是 Corning 专属数据。本次用官方 Daily Treasury Par Yield Curve XML feed 验证了 2Y/5Y/10Y/30Y 的自动读取。

## 来源登记

| 字段 | 值 |
|---|---|
| `official_domain` | `home.treasury.gov` |
| `document_type` | OData-style XML feed / Daily Treasury Par Yield Curve Rates |
| `url` | `https://home.treasury.gov/resource-center/data-chart-center/interest-rates/pages/xml?data=daily_treasury_yield_curve&field_tdr_date_value=2026` |
| `published_at` | 最新记录 `2026-08-18`; feed entry `updated=2026-08-18T15:54:16Z` |
| `retrieved_at` | `2026-08-19T10:54:28Z` |
| `issuer` | U.S. Department of the Treasury |
| `reporting_period` | 2026 年；最新可见交易日 2026-08-18 |
| `费用/权限` | 免费公开 GET feed；不需要 API key |
| `稳定 API` | 年份参数化 XML endpoint；官方提供 all/year/month 结构和标准 HTTP 状态码 |
| `自动化程度` | 高；建议按年/月或指定日期读取，避免无界全量循环 |
| `缓存/再分发` | 本次只登记必要期限和源文件 hash；继续遵守 Treasury feed 使用边界及数据引用要求 |
| `Content-Type` | `text/xml; charset=UTF-8` |

## 实际取得的数据

2026-08-18：

| 期限 | XML 字段 | 收益率（%） |
|---:|---|---:|
| 2Y | `BC_2YEAR` | 4.19 |
| 5Y | `BC_5YEAR` | 4.37 |
| 10Y | `BC_10YEAR` | 4.71 |
| 30Y | `BC_30YEAR` | 5.28 |

这组值是名义 par yield curve，不是 FRED API 的另一份数据，也不应与实时交易行情混同。

## 原始响应 hash

```text
daily_treasury_yield_curve 2026 XML: 07b00736796f8dbc130ec883764e13a44f0e894489536c9f55dfe857ca984a55
```

## 适配器结论

```text
treasury-rate fetch --date 2026-08-18 --tenor 2Y,5Y,10Y,30Y
=> PASS
=> output should retain observation_date, tenor, value, unit, source_url, retrieved_at, sha256
```

## 来源

- [Treasury Daily Interest Rate XML Feed](https://home.treasury.gov/treasury-daily-interest-rate-xml-feed)
- [Treasury XML endpoint used in this probe](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/pages/xml?data=daily_treasury_yield_curve&field_tdr_date_value=2026)
- [Treasury Daily Rates text view](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?page=0)
