#!/usr/bin/env node
// 生成可回放的仪表盘 HTML（单文件，无外部依赖）。
// ⚠️ 这个仪表盘由本脚本生成，**不是** Ling-3.0-flash-VL 的产出；页面上有显式声明。
// 目标分辨率 1280×720，供 record.mjs 逐帧录屏。
import fs from 'node:fs';
import path from 'node:path';

const HERE = path.dirname(new URL(import.meta.url).pathname);
const OUT = path.join(HERE, 'out');

const CFG = { W: 1280, H: 720, FPS: 30, FRAMES_PER_HOUR: 3 };

const css = `
*{margin:0;padding:0;box-sizing:border-box}
body{width:${CFG.W}px;height:${CFG.H}px;overflow:hidden;background:#0B1220;color:#E6EAF2;
  font-family:-apple-system,"PingFang SC","Helvetica Neue",Arial,sans-serif}
header{height:54px;display:flex;align-items:center;justify-content:space-between;padding:0 20px;
  border-bottom:1px solid rgba(255,255,255,.09)}
h1{font-size:17px;font-weight:600;letter-spacing:.2px}
h1 span{font-weight:400;color:#8A93A6;font-size:12px;margin-left:10px}
.speed{font-size:12px;color:#8A93A6}
.speed b{color:#E6EAF2;font-weight:600}
#row1{display:flex;gap:12px;padding:12px 20px 0;height:322px}
#row2{display:flex;gap:12px;padding:12px 20px 0;height:266px}
.panel{background:#111A2B;border:1px solid rgba(255,255,255,.08);border-radius:10px;padding:12px 14px;overflow:hidden}
.ptitle{font-size:12px;color:#8A93A6;margin-bottom:8px;display:flex;justify-content:space-between}
.ptitle b{color:#C9D1E0;font-weight:500}
#curve{flex:1;display:flex;flex-direction:column}
#dec{width:376px}
#hold{width:596px}
#news{flex:1}
svg{display:block}
.legend{display:flex;gap:16px;font-size:11px;color:#8A93A6;margin-top:6px}
.legend i{display:inline-block;width:14px;height:3px;border-radius:2px;margin-right:5px;vertical-align:middle}
.dsym{font-size:13px;font-weight:600;margin-bottom:6px;display:flex;align-items:center;gap:8px}
.chip{font-size:11px;padding:1px 7px;border-radius:4px;font-weight:600}
.c-buy{background:rgba(226,75,74,.18);color:#F09B9A;border:1px solid rgba(226,75,74,.5)}
.c-sell{background:rgba(29,158,117,.18);color:#6FD3AE;border:1px solid rgba(29,158,117,.5)}
.c-hold{background:rgba(255,255,255,.07);color:#B4BAC8;border:1px solid rgba(255,255,255,.18)}
.prow{display:flex;align-items:center;gap:7px;font-size:11px;color:#8A93A6;margin-top:3px}
.prow span:first-child{width:30px}
.track{flex:1;height:7px;background:rgba(255,255,255,.07);border-radius:4px;overflow:hidden}
.fill{height:100%;border-radius:4px;transition:none}
.pv{width:38px;text-align:right;color:#C9D1E0;font-variant-numeric:tabular-nums}
.bar{height:16px;background:rgba(255,255,255,.07);border-radius:4px;position:relative;overflow:hidden;margin-top:3px}
.bar i{position:absolute;left:0;top:0;bottom:0;border-radius:4px}
.hrow{display:flex;align-items:center;gap:8px;font-size:11px;color:#8A93A6}
.hrow span:first-child{width:38px;color:#C9D1E0}
.hrow span:last-child{width:44px;text-align:right;color:#C9D1E0;font-variant-numeric:tabular-nums}
.news{font-size:11px;color:#98A2B6;line-height:1.55}
.news div{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;margin-bottom:2px}
.news em{color:#5B6478;font-style:normal}
.ntag{color:#5C6680;margin-right:5px}
footer{position:absolute;bottom:0;left:0;right:0;height:34px;display:flex;align-items:center;
  padding:0 20px;font-size:10.5px;color:#6B7488;border-top:1px solid rgba(255,255,255,.07)}
footer b{color:#C08A4A;font-weight:600}
`;

const html = `<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8"><title>trade the news · 复刻最小闭环</title>
<style>${css}</style></head>
<body>
<header>
  <h1>trade the news<span>复刻最小闭环 · BTC / ETH · 小时级盯市</span></h1>
  <div class="speed">回放加速 <b id="spd">–</b> · 本片 <b id="dur">–</b></div>
</header>
<section id="row1">
  <div class="panel" id="curve">
    <div class="ptitle"><span>账户净值（起点 $100,000）</span><span id="eqline">–</span></div>
    <svg id="chart" width="820" height="246"></svg>
    <div class="legend">
      <span><i style="background:#E24B4A"></i>本策略（规则替代源）</span>
      <span><i style="background:#6B7488"></i>等权买入持有</span>
      <span id="replaydate" style="margin-left:auto;color:#C9D1E0"></span>
    </div>
  </div>
  <div class="panel" id="dec">
    <div class="ptitle"><span>当日决策</span><span id="decrep">–</span></div>
    <div id="declist"></div>
  </div>
</section>
<section id="row2">
  <div class="panel" id="hold">
    <div class="ptitle"><span>目标仓位（P(买) − P(卖)，按标的均分，其余现金）</span><span id="gross">–</span></div>
    <div id="holdlist"></div>
  </div>
  <div class="panel" id="news">
    <div class="ptitle"><span>当日投资简报（真实 RSS 标题）</span><span id="ncount">–</span></div>
    <div class="news" id="newslist"></div>
  </div>
</section>
<footer>
  决策源：<b id="srcnote">–</b>｜仪表盘由 research/_agent/jev-ling-repro/make_dashboard.mjs 生成，<b>非 Ling-3.0-flash-VL 产出</b>｜数据：Binance 小时 K 线 + 公开 RSS
</footer>
<script>
var D = __DATA__;
var CFG = __CFG__;
var INIT = D.config.INIT;
var days = D.days, NH = days.length * 24, FRAMES = NH * CFG.FRAMES_PER_HOUR;
var strat = [], bench = [];
for (var i = 0; i < days.length; i++) {
  for (var h = 0; h < 24; h++) { strat.push(days[i].equityPath[h]); bench.push(days[i].benchPath[h]); }
}
var pad = { l: 52, r: 62, t: 10, b: 18 };
var W = 820, Hh = 246;
function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
var lo = Math.min.apply(null, strat.concat(bench)), hi = Math.max.apply(null, strat.concat(bench));
// 规整刻度：先按目标 4 格求 nice step，再把上下界吸附到 step 的整数倍
function niceStep(range, target) {
  var raw = range / target;
  var p = Math.pow(10, Math.floor(Math.log10(raw)));
  var m = raw / p;
  var s = m <= 1 ? 1 : m <= 2 ? 2 : m <= 2.5 ? 2.5 : m <= 5 ? 5 : 10;
  return s * p;
}
var padFrac = (hi - lo) * 0.12; lo -= padFrac; hi += padFrac;
var step = niceStep(hi - lo, 4);
lo = Math.floor(lo / step) * step;
hi = Math.ceil(hi / step) * step;
function X(i) { return pad.l + (i / (NH - 1)) * (W - pad.l - pad.r); }
function Y(v) { return Hh - pad.b - ((v - lo) / (hi - lo)) * (Hh - pad.t - pad.b); }
function interp(a, x) { var i = Math.floor(x), j = Math.min(a.length - 1, i + 1), f = x - i; return a[i] * (1 - f) + a[j] * f; }
function cls(c) { return c === 'buy' ? 'c-buy' : c === 'sell' ? 'c-sell' : 'c-hold'; }
function label(c) { return c === 'buy' ? '买' : c === 'sell' ? '卖' : '不动'; }
function money(v) { return '$' + Math.round(v).toLocaleString('en-US'); }

// 网格与基准线（静态部分）
var g = '';
for (var v = lo; v <= hi + 1e-9; v += step) {
  var yy = Y(v);
  g += '<line x1="' + pad.l + '" y1="' + yy + '" x2="' + (W - pad.r) + '" y2="' + yy + '" stroke="rgba(255,255,255,.06)"/>';
  g += '<text x="' + (pad.l - 6) + '" y="' + (yy + 3) + '" fill="#5C6678" font-size="9" text-anchor="end">'
     + '$' + (v / 1000).toFixed(v % 1000 === 0 ? 0 : 1) + 'k</text>';
}
var zeroY = Y(INIT);
g += '<line x1="' + pad.l + '" y1="' + zeroY + '" x2="' + (W - pad.r) + '" y2="' + zeroY + '" stroke="rgba(255,255,255,.18)" stroke-dasharray="3 3"/>';

document.getElementById('spd').textContent = Math.round(NH / (FRAMES / CFG.FPS)) + 'x';
document.getElementById('dur').textContent = (FRAMES / CFG.FPS).toFixed(1) + 's';
document.getElementById('srcnote').textContent = D.config.decisionSource === 'jev'
  ? ('Jev 1.13（' + D.config.model + '）')
  : '规则替代（确定性规则，非 Jev 1.13）';
document.getElementById('ncount').textContent = '合计 ' + D.summaryTotalHeadlines + ' 条';

function seek(fr) {
  var hour = Math.min(NH - 0.0001, Math.max(0, fr / CFG.FRAMES_PER_HOUR));
  var di = Math.min(days.length - 1, Math.floor(hour / 24));
  var day = days[di];
  var cur = interp(strat, hour), curB = interp(bench, hour);

  var pts = '', ptsB = '';
  var upto = Math.floor(hour);
  for (var i = 0; i <= upto; i++) { pts += X(i) + ',' + Y(strat[i]) + ' '; ptsB += X(i) + ',' + Y(bench[i]) + ' '; }
  pts += X(hour) + ',' + Y(cur); ptsB += X(hour) + ',' + Y(curB);
  var svg = g
    + '<polyline points="' + ptsB + '" fill="none" stroke="#6B7488" stroke-width="1.3"/>'
    + '<polyline points="' + pts + '" fill="none" stroke="#E24B4A" stroke-width="2"/>'
    + '<circle cx="' + X(hour) + '" cy="' + Y(cur) + '" r="3.2" fill="#E24B4A"/>'
    + '<text x="' + (X(hour) + 7) + '" y="' + (Y(cur) - 5) + '" fill="#F09B9A" font-size="10">' + money(cur) + '</text>'
    + '<text x="' + (X(hour) + 7) + '" y="' + (Y(curB) + 11) + '" fill="#8A93A6" font-size="10">' + money(curB) + '</text>';
  document.getElementById('chart').innerHTML = svg;

  var ret = cur / INIT - 1, retB = curB / INIT - 1;
  document.getElementById('eqline').innerHTML =
    '<b style="color:' + (ret >= 0 ? '#F09B9A' : '#6FD3AE') + '">' + (ret * 100).toFixed(2) + '%</b>'
    + ' <span style="color:#8A93A6">vs 基准 ' + (retB * 100).toFixed(2) + '%</span>';
  document.getElementById('replaydate').textContent = day.holdDay + ' UTC · 第 ' + (Math.floor(hour) % 24) + ' 小时';

  // 决策矩阵
  document.getElementById('decrep').textContent = '报告日 ' + day.reportDay;
  var dl = '';
  for (var s in day.answers) {
    var a = day.answers[s], p = a.probabilities;
    dl += '<div class="dsym">' + s.replace('USDT', '') + '<span class="chip ' + cls(a.choice) + '">' + label(a.choice) + '</span>'
        + '<span style="font-size:10px;color:#6B7488;font-weight:400">置信 ' + a.confidence.toFixed(2) + '</span></div>';
    var rows = [['买', p.buy, '#E24B4A'], ['不动', p.hold, '#6B7488'], ['卖', p.sell, '#1D9E75']];
    for (var r = 0; r < rows.length; r++) {
      dl += '<div class="prow"><span>' + rows[r][0] + '</span><div class="track">'
          + '<i class="fill" style="width:' + (rows[r][1] * 100).toFixed(1) + '%;background:' + rows[r][2] + '"></i></div>'
          + '<span class="pv">' + (rows[r][1] * 100).toFixed(1) + '%</span></div>';
    }
  }
  document.getElementById('declist').innerHTML = dl;

  // 目标仓位
  var hl = '';
  for (var s2 in day.targetWeights) {
    var w = day.targetWeights[s2];
    hl += '<div class="hrow"><span>' + s2.replace('USDT', '') + '</span><div class="bar">'
        + '<i style="width:' + Math.min(100, w * 100).toFixed(1) + '%;background:' + (w > 0 ? '#E24B4A' : '#2A3446') + '"></i></div>'
        + '<span>' + (w * 100).toFixed(0) + '%</span></div>';
  }
  var cashW = 1 - Object.keys(day.targetWeights).reduce(function (x, k) { return x + day.targetWeights[k]; }, 0);
  hl += '<div class="hrow" style="margin-top:6px"><span>现金</span><div class="bar">'
      + '<i style="width:' + (cashW * 100).toFixed(1) + '%;background:#39445A"></i></div>'
      + '<span>' + (cashW * 100).toFixed(0) + '%</span></div>';
  hl += '<div style="font-size:10.5px;color:#6B7488;margin-top:9px">换手 ' + (day.turnover * 100).toFixed(0)
      + '%　手续费 ' + day.fee.toFixed(2) + '　当日 ' + (day.ret * 100).toFixed(2) + '%　基准 ' + (day.retBench * 100).toFixed(2) + '%</div>';
  document.getElementById('holdlist').innerHTML = hl;
  document.getElementById('gross').textContent = '总敞口 ' + (day.grossExposure * 100).toFixed(0) + '%';

  // 新闻
  var nl = '';
  for (var n = 0; n < day.headlines.length; n++) {
    nl += '<div><span class="ntag">' + esc(day.headlines[n].feed) + '</span>' + esc(day.headlines[n].title) + '</div>';
  }
  document.getElementById('newslist').innerHTML = nl || '<div style="color:#6B7488">当日无标题</div>';
}
window.__seek = seek;
window.__total = FRAMES;
window.__cfg = CFG;
seek(0);
</script>
</body></html>`;

const bt = JSON.parse(fs.readFileSync(path.join(OUT, 'backtest.json'), 'utf8'));
const payload = {
  config: { ...bt.config, INIT: bt.config.INIT_EQUITY },
  days: bt.days,
  summary: bt.summary,
  summaryTotalHeadlines: bt.days.reduce((a, d) => a + d.nHeadlines, 0),
};
const body = html
  .replace('__DATA__', JSON.stringify(payload))
  .replace('__CFG__', JSON.stringify(CFG));

fs.writeFileSync(path.join(OUT, 'dashboard.html'), body);
console.log('写出 ' + path.join(OUT, 'dashboard.html') + '（' + body.length + ' 字节）');
console.log(`帧数 ${payload.days.length * 24 * CFG.FRAMES_PER_HOUR}　${CFG.FPS}fps　≈ ${(payload.days.length * 24 * CFG.FRAMES_PER_HOUR / CFG.FPS).toFixed(1)}s`);
console.log('自检：', payload.days.length, '个持仓日；标题合计', payload.summaryTotalHeadlines, '条；决策源', payload.config.decisionSource);
