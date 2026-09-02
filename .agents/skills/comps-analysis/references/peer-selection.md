# Peer Selection

只在建立或修改 peer universe 时读取。

## 候选维度

按本案重要性排序，而不是固定加权：

- 收入模式与产品/服务构成
- 客户类型、渠道和地域
- 规模、增长、margin 和资本强度
- 会计口径、财政年度和生命周期
- 监管、周期性和资产负债表风险

为每个候选记录 `included`、`excluded` 或 `secondary`，以及一行可复核理由。直接可比公司不足时，分别展示不同 peer tier，不把邻近公司混进同一统计集合。

## 口径

- 估值日期一致；价格、shares、debt 和 cash 尽量同一时点。
- LTM 从已披露季度构建并显示 period end；NTM 只有在 dated guidance、`USER_PROVIDED` estimate 或明确 `MODEL_DERIVED` forecast 可用时计算。
- GAAP 与 adjusted 指标分列；调整项保留来源和 reconciliation。
- 非同币种公司显示原币和换算币种，记录 FX 日期与来源。

异常值不自动删除。先检查数据/口径，再基于可比性说明保留、单列或排除。
