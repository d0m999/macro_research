# Earnings Analysis Workflow

只在定位期间、收集材料和执行分析时读取。

## 1. Period resolution

1. 解析用户指定的 fiscal quarter/year、calendar period、period end 或 release date。
2. 从 issuer release/filing 确认 fiscal calendar；不要假设 fiscal Q1 等于 calendar Q1。
3. 用户指定期间时搜索该精确期间；只有用户请求 latest 时搜索 most recent reported quarter。
4. 记录 period end、release date、filing date 和 accessed date。历史 release 较旧是预期状态，不是切换季度的理由。

## 2. Material collection

按可用性打开并交叉核对：

- earnings release；
- 10-Q/10-K/8-K 或当地监管 filing；
- investor presentation/supplement；
- current 与 prior guidance 的发行人材料；
- 发行人公开 transcript 或 webcast；
- 用户提供的 prior model/estimates。

搜索只用于发现；最终数字引用实际材料。每份材料核对 company、fiscal period、date、currency 和 units。

## 3. Data normalization

建立 actuals 表，保留 reported label、GAAP/adjusted、quarter/YTD、currency/unit、source 和 locator。重述、acquisition/discontinued operations、FX 与 accounting change 单列 reconciliation。

## 4. Variance analysis

有效 comparison baseline 按优先顺序选择：

1. 同期间 dated issuer guidance；
2. `USER_PROVIDED` estimate；
3. 在事件前已有且标记清晰的 `MODEL_DERIVED` estimate。

没有基线时不写 beat/miss。可分析同比、环比、mix、volume/price、margin bridge、segment、KPI、cash flow 和 balance sheet change。

## 5. Guidance and estimates

把 current guidance 与 prior guidance 同口径比较；显示范围、midpoint（若计算则标 `MODEL_DERIVED`）、期间和发布日期。更新 estimates 时保留 old/new/variance、驱动和公式；材料不足时保持 `SOURCE_UNAVAILABLE`。

## 6. Thesis and valuation

把事实变化映射到原 thesis 或新建立的临时 baseline。估值只在价格、shares、net debt、forecast 和方法输入完整时更新；经验阈值、rating change 或 price-target change 不由固定百分比自动触发。

## 7. QC

- 指定期间未被最新季度替换；所有材料属于同一 fiscal period。
- Actual、guidance、estimate 和 prior-period 列没有混用。
- 每个 figure/table 有 source 和 date；所有链接可打开或标记限制。
- 报告、模型与图表的关键数字一致。
