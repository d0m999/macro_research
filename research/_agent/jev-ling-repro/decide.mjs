#!/usr/bin/env node
// 判断腿：把「前一日投资简报 + 当前持仓」变成每个标的的 买/卖/不动 + 概率。
//
// 两种决策源：
//   jev  —— 真实调用 TypeSafe Jev 1.13（OpenRouter Decisions API）。
//            ★ 需要 OPENROUTER_API_KEY；无密钥直接报错退出，绝不静默回退。
//   rule —— 确定性规则替代。用于无密钥时验证**下游链路**（回测/仪表盘/出片）。
//            它不是模型，产物会被标注 decisionSource="rule"。
//
// Jev 的接口形状与 chat/completions 完全不同（chat SDK 调不通）：
//   POST https://openrouter.ai/api/alpha/decisions
//   { model, state, questions: { <name>: { type:"noul"|"choice"|"score",
//                                          instructions, criteria } } }
//   应答 { answers: { <name>: { type, choice|noul|score, probabilities, confidence } } }
//   一个请求内并行问多个问题（共享同一份 state）——这正是作者 1155 次决策只花 87s 的原因：
//   1155 = 77 天 × 3 策略 × 5 标的，但**调用只有 231 次** = 77 × 3，每次并行问 5 个标的。
import fs from 'node:fs';
import path from 'node:path';

const HERE = path.dirname(new URL(import.meta.url).pathname);
const DATA = path.join(HERE, 'data');
const OUT = path.join(HERE, 'out');

// ── 常量区（改参数只改这里）────────────────────────────────────
const JEV_MODEL = 'typesafe/jev-1.13';
const JEV_ENDPOINT = 'https://openrouter.ai/api/alpha/decisions';
const CHOICE_CRITERIA = {
  buy: '次日上涨概率明显占优，应当加仓或建立多头',
  hold: '信号不明确或风险收益比不足，维持当前仓位',
  sell: '次日下跌概率明显占优，应当减仓或清空多头',
};
const REPORT_MAX_HEADLINES = 40;

const W_NEWS = 0.55;      // 新闻倾向权重（仅 rule 源使用）
const W_MOM = 0.30;       // 24h 动量权重
const W_POS = 0.15;       // 7 日区间分位权重
const LOGIT_SCALE = 2.4;  // softmax 陡峭度

const BULL_WORDS = ['surge', 'soar', 'rally', 'record', 'gain', 'jump', 'bullish', 'approve',
  'approval', 'etf', 'inflow', 'adopt', 'upgrade', 'breakout', 'boost', 'rebound', 'climb', 'high'];
const BEAR_WORDS = ['plunge', 'crash', 'drop', 'fall', 'slump', 'bearish', 'hack', 'exploit',
  'lawsuit', 'ban', 'outflow', 'selloff', 'fear', 'liquidat', 'downgrade', 'fraud', 'halt', 'decline'];

// ── 简报文本（喂给模型的 state）────────────────────────────────
export function buildReport(entry) {
  const lines = [];
  lines.push(`# 投资日报（报告日 ${entry.reportDay} UTC）`);
  lines.push('');
  lines.push(`## 行情状态（截至 ${entry.reportDay} 23:00 UTC 收盘）`);
  for (const [sym, b] of Object.entries(entry.briefs)) {
    if (!b) { lines.push(`${sym}: 数据不足`); continue; }
    lines.push(`- ${sym}: 现价 ${b.px}｜近 24h ${(b.ret24h * 100).toFixed(2)}%`
      + `｜近 7 日 ${(b.ret7d * 100).toFixed(2)}%`
      + `｜24h 实现波动率 ${(b.vol24d * 100).toFixed(2)}%`
      + `｜7 日区间分位 ${(b.pos7d * 100).toFixed(0)}%（${b.lo7d}–${b.hi7d}）`);
  }
  lines.push('');
  lines.push(`## 当日新闻标题（${entry.headlines.length} 条，来自公开 RSS）`);
  if (!entry.headlines.length) lines.push('（当日无标题）');
  for (const h of entry.headlines.slice(0, REPORT_MAX_HEADLINES)) {
    lines.push(`- [${h.feed}] ${h.title}`);
  }
  return lines.join('\n');
}

// ── 决策源 A：真实 Jev ────────────────────────────────────────
async function decideWithJev(entries) {
  const key = process.env.OPENROUTER_API_KEY;
  if (!key) {
    throw new Error(
      '缺少 OPENROUTER_API_KEY，无法调用 Jev。\n'
      + '  · Jev 1.13 在 OpenRouter 上的完整 ID 是 typesafe/jev-1.13（$0.042/M 入、$0 出）\n'
      + '  · 走的是 Decisions API（POST /api/alpha/decisions），不是 chat/completions\n'
      + '  · 拿到密钥后：export OPENROUTER_API_KEY=sk-or-v1-... 再跑 --source jev\n'
      + '  本次不会回退到规则源，请显式选择 --source rule 来验证下游链路。');
  }
  const out = [];
  for (const e of entries) {
    const state = buildReport(e);
    const questions = {};
    for (const sym of Object.keys(e.briefs)) {
      questions[sym] = { type: 'choice', instructions: `${sym} 在随后的 24 小时应当如何操作？`, criteria: CHOICE_CRITERIA };
    }
    const t0 = Date.now();
    const r = await fetch(JEV_ENDPOINT, {
      method: 'POST',
      headers: { Authorization: `Bearer ${key}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ model: JEV_MODEL, state, questions }),
      signal: AbortSignal.timeout(120000),
    });
    const txt = await r.text();
    if (!r.ok) throw new Error(`Jev HTTP ${r.status}: ${txt.slice(0, 400)}`);
    let j; try { j = JSON.parse(txt); } catch { throw new Error('Jev 返回非 JSON: ' + txt.slice(0, 300)); }
    out.push({ holdDay: e.holdDay, reportDay: e.reportDay, ms: Date.now() - t0, answers: j.answers, raw: j });
  }
  return { source: 'jev', model: JEV_MODEL, entries: out };
}

// ── 决策源 B：确定性规则（非模型，仅用于验证下游）──────────────
function sentiment(headlines) {
  let bull = 0, bear = 0;
  for (const h of headlines) {
    const t = h.title.toLowerCase();
    for (const w of BULL_WORDS) if (t.includes(w)) bull++;
    for (const w of BEAR_WORDS) if (t.includes(w)) bear++;
  }
  const n = bull + bear;
  return n === 0 ? 0 : (bull - bear) / n;
}

function softmax3(score) {
  // score > 0 → 倾向 buy；< 0 → 倾向 sell；≈0 → 倾向 hold
  const logits = [score * LOGIT_SCALE, 0, -score * LOGIT_SCALE];
  const mx = Math.max(...logits);
  const ex = logits.map((x) => Math.exp(x - mx));
  const s = ex.reduce((a, b) => a + b, 0);
  const p = ex.map((x) => x / s);
  return { buy: +p[0].toFixed(4), hold: +p[1].toFixed(4), sell: +p[2].toFixed(4) };
}

export function decideWithRule(entries) {
  const out = [];
  for (const e of entries) {
    const news = sentiment(e.headlines);
    const answers = {};
    for (const [sym, b] of Object.entries(e.briefs)) {
      const mom = b ? Math.tanh(b.ret24h / Math.max(b.vol24d, 0.01)) : 0;
      const pos = b ? 2 * (b.pos7d - 0.5) : 0;
      const score = W_NEWS * news + W_MOM * mom + W_POS * pos;
      const p = softmax3(score);
      const choice = p.buy >= p.hold && p.buy >= p.sell ? 'buy' : (p.sell >= p.hold ? 'sell' : 'hold');
      answers[sym] = {
        type: 'choice', choice, probabilities: p,
        confidence: +Math.max(p.buy, p.hold, p.sell).toFixed(4),
        debug: { news: +news.toFixed(3), mom: +mom.toFixed(3), pos: +pos.toFixed(3), score: +score.toFixed(3) },
      };
    }
    out.push({ holdDay: e.holdDay, reportDay: e.reportDay, ms: 0, answers });
  }
  return { source: 'rule', model: null, entries: out };
}

// ── CLI ───────────────────────────────────────────────────────
async function main() {
  const i = process.argv.indexOf('--source');
  const source = i >= 0 ? process.argv[i + 1] : 'rule';
  const entries = JSON.parse(fs.readFileSync(path.join(DATA, 'briefs.json'), 'utf8'));
  const usable = entries.filter((e) => e.ok);

  const res = source === 'jev' ? await decideWithJev(usable) : decideWithRule(usable);
  fs.mkdirSync(OUT, { recursive: true });
  fs.writeFileSync(path.join(OUT, 'decisions.json'), JSON.stringify({ ...res, entries: res.entries.map(({ raw, ...x }) => x) }, null, 1));

  console.log(`===== 决策源：${res.source}${res.model ? ' (' + res.model + ')' : '（确定性规则，非模型）'} =====`);
  for (const e of res.entries) {
    const parts = Object.entries(e.answers).map(([s, a]) => `${s} ${a.choice} p=[${a.probabilities.buy} ${a.probabilities.hold} ${a.probabilities.sell}]`);
    console.log(`  ${e.holdDay} ← 报告日 ${e.reportDay}: ${parts.join(' | ')}`);
  }
  console.log(`\n累计调用 ${res.entries.length} 次（每次并行问 ${Object.keys(res.entries[0].answers).length} 个标的）`);
}
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch((e) => { console.error('FAIL: ' + e.message); process.exit(1); });
}
