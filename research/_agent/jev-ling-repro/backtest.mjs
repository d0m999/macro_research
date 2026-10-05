#!/usr/bin/env node
// 回测引擎（纯代码，无模型）：把概率变成仓位 → 用真实小时 K 线逐小时盯市 → 算净值。
// 未来函数纪律：
//   · 决策在持仓日 00:00 UTC 做出，只用**前一日**已完整发布的标题（见 fetch_data.mjs）
//   · 成交价取持仓日 00:00 那根小时 K 的 **开盘价**
//   · 当日净值用该日 00:00–23:00 的**收盘价**逐小时盯市
// 运行：node backtest.mjs
import fs from 'node:fs';
import path from 'node:path';

const HERE = path.dirname(new URL(import.meta.url).pathname);
const DATA = path.join(HERE, 'data');
const OUT = path.join(HERE, 'out');

// ── 常量区 ────────────────────────────────────────────────────
const INIT_EQUITY = 100000;   // 单账户本金（对齐作者口径：3 个账户各 $100,000）
const FEE_BPS = 10;           // 单边手续费，bp（Binance 现货 taker 量级）
const BENCH_WEIGHTS = null;   // null = 标的等权；否则给 { SYM: w }

const utcDay = (ts) => new Date(ts).toISOString().slice(0, 10);
const round = (x, n = 4) => +Number(x).toFixed(n);

function load() {
  const kl = JSON.parse(fs.readFileSync(path.join(DATA, 'klines.json'), 'utf8'));
  const briefs = JSON.parse(fs.readFileSync(path.join(DATA, 'briefs.json'), 'utf8'));
  const dec = JSON.parse(fs.readFileSync(path.join(OUT, 'decisions.json'), 'utf8'));
  return { kl, briefs, dec };
}

// 把概率折算成目标权重：w = clip(P(buy) − P(sell), 0, 1) ÷ N，其余留现金（现货多头，不做空）
function targetWeights(answer, nSym) {
  const w = {};
  let sum = 0;
  for (const [sym, a] of Object.entries(answer)) {
    const p = a.probabilities || {};
    const raw = Math.max(0, Math.min(1, (p.buy ?? 0) - (p.sell ?? 0)));
    w[sym] = raw / nSym;
    sum += w[sym];
  }
  return { w, gross: round(sum) };
}

function main() {
  const { kl, briefs, dec } = load();
  const symbols = Object.keys(briefs.find((b) => b.ok).briefs);
  const byKey = new Map(dec.entries.map((e) => [e.holdDay, e]));

  // BTC/ETH 等权基准的初始权重
  const bw = BENCH_WEIGHTS || Object.fromEntries(symbols.map((s) => [s, 1 / symbols.length]));

  const days = [];
  let equity = INIT_EQUITY;
  let bench = INIT_EQUITY;
  let weights = Object.fromEntries(symbols.map((s) => [s, 0]));   // 策略当前权重
  let benchUnits = null;
  let peak = equity, maxDD = 0;

  for (const entry of briefs.filter((b) => b.ok)) {
    const got = byKey.get(entry.holdDay);
    if (!got) continue;
    const dayBars = kl[symbols[0]].filter((b) => b.day === entry.holdDay);
    if (dayBars.length !== 24) { console.log(`跳过 ${entry.holdDay}：当日 ${dayBars.length} 根 K 线（需 24）`); continue; }

    const tw = targetWeights(got.answers, symbols.length);

    // 开盘价建仓
    const openPrice = {}, closePath = {};
    for (const s of symbols) {
      const bars = kl[s].filter((b) => b.day === entry.holdDay);
      openPrice[s] = bars[0].open;
      closePath[s] = bars.map((b) => b.close);
    }

    // 换手与手续费
    const turnover = symbols.reduce((a, s) => a + Math.abs((tw.w[s] ?? 0) - (weights[s] ?? 0)), 0);
    const fee = equity * turnover * (FEE_BPS / 10000);
    const equityAfterFee = equity - fee;

    // 建仓 → 记录每标的份额
    const units = {};
    for (const s of symbols) units[s] = (tw.w[s] ?? 0) * equityAfterFee / openPrice[s];
    const cash = equityAfterFee - symbols.reduce((a, s) => a + units[s] * openPrice[s], 0);

    // 逐小时盯市
    const path_ = [];
    for (let h = 0; h < 24; h++) {
      const v = cash + symbols.reduce((a, s) => a + units[s] * closePath[s][h], 0);
      path_.push({ h, t: dayBars[h].t, v: round(v, 2) });
    }
    const equityEnd = path_.at(-1).v;

    // 基准：首日按等权建仓，此后只盯市、不再平衡
    if (!benchUnits) {
      const feeB = bench * (1.0) * (FEE_BPS / 10000);
      const eB = bench - feeB;
      benchUnits = Object.fromEntries(symbols.map((s) => [s, bw[s] * eB / openPrice[s]]));
      bench = eB;
    }
    const benchPath = [];
    for (let h = 0; h < 24; h++) {
      const v = symbols.reduce((a, s) => a + benchUnits[s] * closePath[s][h], 0);
      benchPath.push({ h, t: dayBars[h].t, v: round(v, 2) });
    }
    const benchEnd = benchPath.at(-1).v;

    const ret = equityEnd / equity - 1;
    const retB = benchEnd / bench - 1;
    peak = Math.max(peak, equityEnd);
    maxDD = Math.min(maxDD, equityEnd / peak - 1);

    days.push({
      holdDay: entry.holdDay, reportDay: entry.reportDay,
      answers: got.answers,
      targetWeights: Object.fromEntries(Object.entries(tw.w).map(([k, v]) => [k, round(v, 4)])),
      grossExposure: tw.gross,
      prevWeights: Object.fromEntries(Object.entries(weights).map(([k, v]) => [k, round(v, 4)])),
      turnover: round(turnover), fee: round(fee, 2),
      equityStart: round(equity, 2), equityEnd,
      benchStart: round(bench, 2), benchEnd,
      ret: round(ret), retBench: round(retB),
      equityPath: path_.map((p) => round(p.v, 2)),
      benchPath: benchPath.map((p) => round(p.v, 2)),
      openPrice: Object.fromEntries(symbols.map((s) => [s, openPrice[s]])),
      headlines: entry.headlines.slice(0, 9).map((h) => ({ feed: h.feed, title: h.title, link: h.link })),
      nHeadlines: entry.headlines.length,
    });

    weights = { ...tw.w };
    equity = equityEnd;
    bench = benchEnd;
  }

  const total = equity / INIT_EQUITY - 1;
  const totalB = bench / INIT_EQUITY - 1;
  const res = {
    config: { INIT_EQUITY, FEE_BPS, symbols, days: days.length, decisionSource: dec.source, model: dec.model },
    days,
    summary: {
      finalEquity: round(equity, 2), totalReturn: round(total),
      benchFinal: round(bench, 2), benchReturn: round(totalB),
      excess: round(total - totalB),
      maxDrawdown: round(maxDD),
      totalFee: round(days.reduce((a, d) => a + d.fee, 0), 2),
      winDays: days.filter((d) => d.ret > 0).length,
    },
  };
  fs.mkdirSync(OUT, { recursive: true });
  fs.writeFileSync(path.join(OUT, 'backtest.json'), JSON.stringify(res, null, 1));

  // ── 自检 ───────────────────────────────────────────────────
  console.log('===== 回测结果 =====');
  console.log(`决策源 ${dec.source}${dec.model ? ' (' + dec.model + ')' : ''}｜标的 ${symbols.join('/')}｜${days.length} 个持仓日｜手续费 ${FEE_BPS}bp`);
  for (const d of days) {
    const px = symbols.map((s) => {
      const a = d.answers[s];
      return `${s.slice(0, 3)} ${a.choice}→${(d.targetWeights[s] * 100).toFixed(0)}%`;
    }).join('  ');
    console.log(`  ${d.holdDay}（报告日 ${d.reportDay}，${d.nHeadlines} 条标题）`);
    console.log(`     ${px}`);
    console.log(`     净值 ${d.equityStart.toLocaleString()} → ${d.equityEnd.toLocaleString()}（${(d.ret * 100).toFixed(2)}%）`
      + `｜基准 ${(d.retBench * 100).toFixed(2)}%｜换手 ${(d.turnover * 100).toFixed(0)}% 费 ${d.fee}`);
  }
  console.log(`\n策略期末 ${res.summary.finalEquity.toLocaleString()}（${(total * 100).toFixed(2)}%）`);
  console.log(`等权买入持有 ${res.summary.benchFinal.toLocaleString()}（${(totalB * 100).toFixed(2)}%）`);
  console.log(`超额 ${(res.summary.excess * 100).toFixed(2)}%｜最大回撤 ${(res.summary.maxDrawdown * 100).toFixed(2)}%｜盈利日 ${res.summary.winDays}/${days.length}`);
}
main();
