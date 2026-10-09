# tools/research — 假设注册 + 回测守门 + 失效归因

研究流水线的「判定层」。设计动机：用 LLM 批量产假设、快速迭代时，
收益 = 单次迭代改进 × 迭代次数 × (1 − 假阳率)。AI 只能拉动中间项，
本目录的职责是把第三项钉死。

## 边界（先读这条）

按 `CLAUDE.md` 与 `tools/factors/README.md`：本目录**不含回测撮合引擎**，
不接触订单、仓位、账户、私钥。三个脚本全部只读收益序列、只写报告。

回测本身由外部引擎完成（Pine / mjs / pandas 均可），导出收益序列后
接入本目录做判定 —— 「生成结果」与「判定结果」必须在两条独立路径上，
同一个模型既生成策略又评价策略是循环论证。

## 三件套

```
hypotheses.py   假设注册表 —— 回测前必须先落盘，缺「证伪条件」拒绝登记
gate.py         守门层 —— 登记校验 / future 静态扫描 / Bonferroni / PSR / 样本外
attribute.py    归因 —— 按时间与波动状态分段，找收益集中度
_stats.py       共享统计口径（单期 Sharpe 检验，年化仅展示）
```

标准流程：

```bash
# 1. 回测前：登记假设（四要素必填，缺证伪条件直接拒绝）
python3 tools/research/hypotheses.py register \
    --statement "..." --mechanism "..." \
    --data-source "..." --falsification "..." \
    --trials-planned 5

# 2. 回测后：导出 result.json（契约见下），过守门层
python3 tools/research/gate.py --result data/reports/<id>.json
# 退出码: 0=PASS 1=FAIL 2=INCONCLUSIVE 3=ERROR（与 tools/validation 一致）

# 3. 归因：收益高度依赖单一时段/波动档时告警
python3 tools/research/attribute.py --result data/reports/<id>.json
```

## result.json 契约（gate.py 输入）

```json
{
  "hyp_id":   "H-20261009-001",
  "returns":  [0.0012, -0.0008, "..."],   // 日收益序列（必填）
  "trials":   5,                          // 实际试验次数；缺省取注册表 trials_planned
  "code_paths": ["research/_agent/x/backtest.py"],  // future 静态扫描目标，建议给
  "is_split": 0.7,                        // 样本内比例，给了才做内外比对
  "cost_bps": 5.0,                        // 单边成本；给了就必须给 turnover
  "turnover": [1.0, 0.0, "..."],          // 与 returns 等长的换手率序列
  "annualization": 365                    // 仅展示用，默认 365
}
```

结果文件放 `data/reports/`（已在 `data/.gitignore` 内，不入库）。

## 统计口径与已知局限

- Sharpe 检验一律用**单期**值；年化值（×√365）只给人阅读。
- PSR / SR* 按 Bailey & López de Prado (2012/2014)，V[SR] 取 Lo (2002)
  IID 渐近方差 (1+SR̂²/2)/n。**收益自相关时会低估方差、高估 PSR** —— 未修正。
- future 扫描是正则启发式：**会漏报也会误报**，因此命中只给 WARN 不给 FAIL，
  也不会让整体变 PASS。命中的行必须人工确认，扫过不等于没有未来函数。
- PASS 的含义是「未被本层拦下」，不是「策略可用」。实盘才是唯一 ground truth。

## 端到端验证记录（2026-10-09）

用 `data/raw/binance-futures/BTCUSDT_perp_1d.csv`（2019-09-08 → 2026-09-20，
2570 根日线）跑了 20 日动量示例（信号 t 决定、t+1 持有，扣 5bps×换手）：

- 登记：`H-20261009-001`（trials=5）
- gate：**FAIL** —— t=2.41, p=0.0159 > Bonferroni α=0.01；PSR=0.891 < 0.95
  （峰度 12.78，厚尾进一步压低 PSR）
- attribute：**高波动档贡献 76.7%**（阈值 60%），触发集中度告警

示例本身是诚实信号（无未来函数），仍被拦下 —— 说明守门层有区分度。
