# GLW — SEC EDGAR

状态：`PASS`（确定性 JSON API）；`PARTIAL`（本地直接读取 archive HTML 的通道差异）

## 来源登记

| 字段 | 值 |
|---|---|
| `issuer` | `CORNING INC /NY` |
| `ticker` | `GLW` |
| `exchange` | `NYSE` |
| `CIK` | `0000024741` |
| `SIC` | `3357 — Drawing & Insulating of Nonferrous Wire` |
| `document_type` | SEC `submissions` JSON、XBRL `companyfacts` JSON、filing HTML |
| `retrieved_at` | `2026-08-19T10:54:28Z`（API probe） |
| `费用/权限` | 公开；本次 API 请求不需要 API key |
| `稳定 API` | `https://data.sec.gov/submissions/CIK0000024741.json`；`https://data.sec.gov/api/xbrl/companyfacts/CIK0000024741.json` |
| `自动化边界` | 可自动访问，但需遵守 SEC fair-access、合理限速、只下载必要内容；不做无界爬取 |
| `缓存/再分发` | 本次只保留提取结果和 hash，不把原始 SEC 大文件提交到仓库；后续按 SEC 政策和具体文件条款处理 |

SEC 官方说明 `data.sec.gov` 的 submissions 和 XBRL API 不要求认证或 API key；自动访问仍要遵守 fair-access 规则，官方当前页面给出的上限是每秒 10 次。

## 实际取得的数据

### 1. 公司身份

`submissions` API 返回：

```text
name: CORNING INC /NY
tickers: GLW
exchanges: NYSE
sic: 3357
fiscalYearEnd: 1231
```
### 2. 最近 filings

| 表单 | filing date | report date / period | accession | primary document |
|---|---:|---:|---|---|
| `10-Q` | 2026-07-29 | 2026-06-30 | `0000024741-26-000255` | `glw-20260630.htm` |
| `8-K` | 2026-07-28 | 2026-07-28 | `0000024741-26-000253` | `glw-20260728.htm` |
| `10-Q` | 2026-05-01 | 2026-03-31 | `0000024741-26-000205` | `glw-20260331.htm` |
| `10-K` | 2026-02-12 | 2025-12-31 | `0000024741-26-000124` | `glw-20251231.htm` |

### 3. XBRL company facts 探针

`companyfacts` 返回实体 `CORNING INC /NY`。本次响应中 `us-gaap:Revenues` 的最新可见值包括：

| 期间 | 值 | 表单 | filed | accession |
|---|---:|---|---:|---|
| 2026-01-01 至 2026-03-31 | `$4,144,000,000` | `10-Q` | 2026-05-01 | `0000024741-26-000205` |
| 2025-01-01 至 2025-12-31 | `$15,629,000,000` | `10-K` | 2026-02-12 | `0000024741-26-000124` |

本次 `companyfacts` 快照在所选 `Revenues` tag 中尚未显示 Q2 2026 的单季值；但 Q2 `10-Q` 已由 submissions API 登记，并可通过 Web 读取 filing。适配器不能因为一个 XBRL tag 暂时没有新值，就把 Q2 当作缺失 filing。

## 通道验证

| 尝试 | 结果 | 备注 |
|---|---|---|
| `data.sec.gov/submissions` | HTTP `200`, `application/json` | 成功；适合公司身份和 filing index |
| `data.sec.gov/api/xbrl/companyfacts` | HTTP `200`, `application/json` | 成功；适合结构化事实，但需处理 tag、期间和重复/重述 |
| `www.sec.gov/Archives/.../glw-20251231.htm` via local `curl` | HTTP `403`, `text/html` | 返回访问拒绝页；该错误页 hash 不可当作 filing hash |
| 同一 2025 10-K via Web | 成功读取 HTML | 读取通道不同；报告事实绑定到 SEC filing URL，不绑定被拦截的错误页 |
| Q2 2026 10-Q via Web | 成功读取 HTML | 期间结束 2026-06-30；可读到 Q2 分部、客户合同负债等披露 |

## 原始响应 hash

以下 hash 是实际通过 API 下载到临时探针目录的响应 bytes；临时目录不纳入仓库：

```text
submissions JSON: 52f611cf4305ea50f0343cb9ba503534bddbed394a5b91cfa8c86df5a50c7025
companyfacts JSON: 024d80faa83a89b7b73d16e3a0914f9f8a65eda0c90c7f93bd4974fa7d5e9411
```

## 来源

- [SEC EDGAR Application Programming Interfaces](https://www.sec.gov/search-filings/edgar-application-programming-interfaces)
- [SEC Accessing EDGAR Data / fair access](https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data)
- [GLW submissions JSON](https://data.sec.gov/submissions/CIK0000024741.json)
- [GLW companyfacts JSON](https://data.sec.gov/api/xbrl/companyfacts/CIK0000024741.json)
- [GLW 2025 Form 10-K](https://www.sec.gov/Archives/edgar/data/24741/000002474126000124/glw-20251231.htm)
- [GLW Q2 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/24741/000002474126000255/glw-20260630.htm)
- [GLW Q2 2026 Form 8-K](https://www.sec.gov/Archives/edgar/data/24741/000002474126000253/glw-20260728.htm)

## 适配器结论

```text
sec-edgar fetch GLW --forms 10-K,10-Q,8-K
=> PASS for identity, filing index and XBRL JSON
=> filing HTML retrieval must support Web/browser fallback and record channel status
=> no API key required; rate-limit and source metadata are mandatory
```
