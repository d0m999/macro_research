#!/usr/bin/env node
// 采集真实数据：Binance 小时级 K 线 + 日期化新闻标题
// 不做任何伪造：网络不可达的源会被记为 skipped，不补假数据。
// 运行：node fetch_data.mjs
import fs from 'node:fs';
import path from 'node:path';

const HERE = path.dirname(new URL(import.meta.url).pathname);
const DATA = path.join(HERE, 'data');
fs.mkdirSync(DATA, { recursive: true });

// ── 窗口（UTC）─────────────────────────────────────────────────
const KL_START = Date.parse('2026-09-01T00:00:00Z'); // 给动量回看留足历史
const KL_END   = Date.parse('2026-09-21T02:00:00Z');
const HOLD_START = '2026-09-17';                     // 首个持仓日
const HOLD_END   = '2026-09-20';                     // 末个持仓日

const SYMBOLS = ['BTCUSDT', 'ETHUSDT'];

const FEEDS = [
  ['cointelegraph',      'https://cointelegraph.com/rss'],
  ['decrypt',            'https://decrypt.co/feed'],
  ['bitcoinmagazine',    'https://bitcoinmagazine.com/feed'],
  ['yahoo-btc',          'https://feeds.finance.yahoo.com/rss/2.0/headline?s=BTC-USD&region=US&lang=en-US'],
  ['yahoo-eth',          'https://feeds.finance.yahoo.com/rss/2.0/headline?s=ETH-USD&region=US&lang=en-US'],
];

const utcDay = (ts) => new Date(ts).toISOString().slice(0, 10);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function getJSON(url, tries = 3) {
  for (let i = 1; i <= tries; i++) {
    try {
      const r = await fetch(url, { signal: AbortSignal.timeout(15000) });
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return await r.json();
    } catch (e) {
      if (i === tries) throw e;
      await sleep(1200 * i);
    }
  }
}
async function getText(url, tries = 3) {
  for (let i = 1; i <= tries; i++) {
    try {
      const r = await fetch(url, { signal: AbortSignal.timeout(15000) });
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return await r.text();
    } catch (e) {
      if (i === tries) throw e;
      await sleep(1200 * i);
    }
  }
}

// ── 1. K 线（data-api.binance.vision，免密钥）────────────────────
// 注意：api.binance.com 在本沙箱超时，data-api.binance.vision 通。这两个是不同的主机。
async function klines(symbol) {
  const url = `https://data-api.binance.vision/api/v3/klines?symbol=${symbol}`
    + `&interval=1h&startTime=${KL_START}&endTime=${KL_END}&limit=1000`;
  const raw = await getJSON(url);
  return raw.map((k) => ({
    t: k[0], open: +k[1], high: +k[2], low: +k[3], close: +k[4], vol: +k[5],
    day: utcDay(k[0]),
  }));
}

// ── 2. 新闻（RSS，按 UTC 日分桶）────────────────────────────────
// RSS 里的标题带 HTML 实体（&amp; &#39; 等），必须解码后再存，否则页面上会出现 "Glassess&#39;"
function decodeEntities(s) {
  return s
    .replace(/&#x([0-9a-f]+);/gi, (_, h) => String.fromCharCode(parseInt(h, 16)))
    .replace(/&#(\d+);/g, (_, d) => String.fromCharCode(+d))
    .replace(/&quot;/g, '"').replace(/&apos;/g, "'")
    .replace(/&nbsp;/g, ' ').replace(/&lt;/g, '<').replace(/&gt;/g, '>')
    .replace(/&amp;/g, '&');
}

function parseRSS(xml) {
  const out = [];
  for (const m of xml.matchAll(/<item>([\s\S]*?)<\/item>/g)) {
    const blk = m[1];
    const pick = (tag) => {
      const r = blk.match(new RegExp(`<${tag}>([\\s\\S]*?)</${tag}>`));
      return r ? r[1].replace(/<!\[CDATA\[|\]\]>/g, '').trim() : '';
    };
    const title = decodeEntities(pick('title'));
    const link = decodeEntities(pick('link'));
    const pd = pick('pubDate');
    const ts = pd ? Date.parse(pd) : NaN;
    if (!title || !Number.isFinite(ts)) continue;
    out.push({ title, link, ts, day: utcDay(ts) });
  }
  return out;
}

async function news() {
  const all = [];
  const status = [];
  for (const [name, url] of FEEDS) {
    try {
      const xml = await getText(url);
      const items = parseRSS(xml).map((x) => ({ ...x, feed: name }));
      all.push(...items);
      const days = [...new Set(items.map((x) => x.day))].sort();
      status.push({ feed: name, ok: true, n: items.length, from: days[0], to: days.at(-1) });
    } catch (e) {
      // 不补假数据，只记录失败
      status.push({ feed: name, ok: false, err: e.message.slice(0, 60) });
    }
  }
  return { items: all, status };
}

// ── 3. 决策时刻的量化简报（只用决策时刻之前的数据，无未来函数）──
function briefFor(bar, history) {
  const idx = history.findIndex((b) => b.t === bar.t);
  const before = history.slice(0, idx); // 严格早于决策时刻
  if (before.length < 24 * 7) return null;
  const px = before.at(-1).close;
  const px24 = before.at(-25).close;
  const px7d = before.at(-1 - 24 * 7).close;
  const ret24h = px / px24 - 1;
  const ret7d = px / px7d - 1;
  const win7d = before.slice(-24 * 7);
  const rets = win7d.slice(1).map((b, i) => b.close / win7d[i].close - 1);
  const mean = rets.reduce((a, b) => a + b, 0) / rets.length;
  const vol = Math.sqrt(rets.reduce((a, b) => a + (b - mean) ** 2, 0) / rets.length) * Math.sqrt(24); // 日化
  const hi = Math.max(...win7d.map((b) => b.high));
  const lo = Math.min(...win7d.map((b) => b.low));
  return {
    t: bar.t, day: bar.day, px: +px.toFixed(2),
    ret24h: +ret24h.toFixed(4), ret7d: +ret7d.toFixed(4), vol24d: +vol.toFixed(4),
    pos7d: +((px - lo) / (hi - lo)).toFixed(3),       // 7 日区间分位
    hi7d: +hi.toFixed(2), lo7d: +lo.toFixed(2),
  };
}

// ── main ──────────────────────────────────────────────────────
const kl = {};
for (const s of SYMBOLS) { kl[s] = await klines(s); console.log(`klines ${s}: ${kl[s].length} bars`); }
const nw = await news();
console.log('news: ' + JSON.stringify(nw.status));

const days = [...new Set(nw.items.map((x) => x.day))].sort();
const byDay = {};
for (const d of days) byDay[d] = nw.items.filter((x) => x.day === d).sort((a, b) => a.ts - b.ts);

// 决策日 = 持仓日；用**前一日**（已完整发布）的报告
const holds = [];
for (let d = HOLD_START; d <= HOLD_END; d = utcDay(Date.parse(d + 'T00:00:00Z') + 864e5)) {
  const reportDay = utcDay(Date.parse(d + 'T00:00:00Z') - 864e5);
  const briefs = {};
  let ok = true;
  for (const s of SYMBOLS) {
    const bar = kl[s].find((b) => b.t === Date.parse(d + 'T00:00:00Z'));
    const b = bar ? briefFor(bar, kl[s]) : null;
    if (!b) ok = false;
    briefs[s] = b;
  }
  holds.push({ holdDay: d, reportDay, briefs, headlines: byDay[reportDay] || [], ok });
}

fs.writeFileSync(path.join(DATA, 'klines.json'), JSON.stringify(kl));
fs.writeFileSync(path.join(DATA, 'news.json'), JSON.stringify({ status: nw.status, byDay, total: nw.items.length }, null, 1));
fs.writeFileSync(path.join(DATA, 'briefs.json'), JSON.stringify(holds, null, 1));

// ── 自检 ──────────────────────────────────────────────────────
console.log('\n===== 自检 =====');
for (const s of SYMBOLS) {
  const b = kl[s];
  console.log(`${s}: ${b.length} 根小时K，${b[0].day} → ${b.at(-1).day}，末价 ${b.at(-1).close}`);
}
console.log(`新闻总计 ${nw.items.length} 条，覆盖 ${days[0]} → ${days.at(-1)}`);
for (const h of holds) {
  console.log(`  持仓 ${h.holdDay} ← 报告日 ${h.reportDay}，标题 ${h.headlines.length} 条`
    + `，BTC ${h.briefs.BTCUSDT ? h.briefs.BTCUSDT.ret24h : 'NA'} / ETH ${h.briefs.ETHUSDT ? h.briefs.ETHUSDT.ret24h : 'NA'}`);
}
const insufficient = holds.filter((h) => !h.ok).length;
console.log(`可完整构建简报的持仓日：${holds.length - insufficient}/${holds.length}`);
console.log(`决策窗口：${HOLD_START} → ${HOLD_END}（共 ${holds.length} 天）`);
