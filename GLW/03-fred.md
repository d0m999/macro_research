# GLW — FRED

状态：`PARTIAL`

FRED 的数据本身公开，但 FRED Web Services API 需要注册 API key。本次故意不提供 key，验证无凭证失败路径；随后用官方 `fredgraph.csv` 导出做窄范围 fallback。

## 来源登记

| 字段 | 值 |
|---|---|
| `official_domain` | `fred.stlouisfed.org` / `api.stlouisfed.org` |
| `series_id` | `DGS10` — 10-Year Treasury Constant Maturity Rate |
| `document_type` | FRED REST API JSON error、FRED CSV graph export、series page |
| `retrieved_at` | `2026-08-19T10:54:31Z` |
| `issuer` | Board of Governors of the Federal Reserve System (series source); Federal Reserve Bank of St. Louis (FRED distribution) |
| `费用/权限` | series/web/CSV 可公开访问；REST API 请求需要注册 key |
| `稳定 API` | REST endpoint 稳定但 key-gated；CSV export 可作为窄范围 fallback，不把它误称为无凭证 REST API |
| `自动化程度` | 有 key 时高；无 key 时只能使用受限公开导出并遵守 FRED 条款 |
| `缓存/再分发` | 不把无 key CSV fallback 自动扩展为全量镜像；按 FRED API/数据版权和引用要求处理 |

## 实际尝试

### 1. 无 key REST API

请求：

```text
https://api.stlouisfed.org/fred/series/observations?series_id=DGS10&file_type=json
```

结果：HTTP `400`，`Content-Type: application/json; charset=UTF-8`。

```json
{"error_code":400,"error_message":"Bad Request. Variable api_key is not set. Read https://fred.stlouisfed.org/docs/api/api_key.html for more information."}
```

这证明 FRED 不属于“无凭证 API 来源”。本次没有申请、猜测或写入 API key。

### 2. 官方 CSV fallback

请求：

```text
https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10
```

结果：HTTP `200`，`Content-Type: application/csv`。本次响应最后一行：

```text
2026-08-17,4.72
```

含义：2026-08-17 的 DGS10 观察值为 `4.72%`；没有把网页搜索摘要中的旧日期/数值覆盖到 CSV 结果上。

## 原始响应 hash

```text
无 key API error JSON: da3c632f9a98b4c8f641de2b0763d513b4642316fe56d52d883002e011a892ff
DGS10 CSV export:      5553781866aedbf1f9e70c1ff7e91539096504fa44de2823fcdd5baec5a442bc
```

## 适配器结论

```text
fred fetch DGS10 --from ... --to ...
=> with registered API key: expected PASS
=> without key: fail closed at AUTH_REQUIRED
=> narrow official CSV fallback: PARTIAL, retain source_url and retrieved_at
```

## 来源

- [FRED DGS10 series page](https://fred.stlouisfed.org/series/DGS10)
- [FRED API key requirements](https://fred.stlouisfed.org/docs/api/fred/v2/api_key.html)
- [FRED API errors](https://fred.stlouisfed.org/docs/api/fred/errors.html)
- [FRED CSV export used in this probe](https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10)
