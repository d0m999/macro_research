#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
L∞p | detrend RSI  —— 数学复刻与验证
逐行复刻 PineScript/_L∞p/L∞p | RSI.pine 的计算链，产出可视化所需的数据 JSON。

用法:
    python3 tools/loops_rsi_math.py            # 生成 payload JSON
    python3 tools/loops_rsi_math.py --inject   # 生成 JSON 并注入 HTML 模板
"""
import csv
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(ROOT, "data", "BINANCE_BTCUSDT.P, 1D_a715e.csv")
HTML_TPL = os.path.join(ROOT, "strategy-notes", "design", "loops-rsi-math.html")
JSON_OUT = os.path.join(ROOT, "strategy-notes", "design", "loops-rsi-math.data.json")

NAN = float("nan")

# ----------------------------------------------------------------------------
# 基础算子（对齐 Pine 语义）
# ----------------------------------------------------------------------------


def sma(x, n):
    out, s = [], 0.0
    for i, v in enumerate(x):
        s += v
        if i >= n:
            s -= x[i - n]
        out.append(s / n if i >= n - 1 else NAN)
    return out


def ema_pine(x, n):
    """Pine ta.ema：以 SMA(n) 作种子"""
    out, alpha, seed = [], 2.0 / (n + 1), None
    for i, v in enumerate(x):
        if i == n - 1:
            seed = sum(x[:n]) / n
            out.append(seed)
            continue
        if i < n - 1:
            out.append(NAN)
            continue
        seed = alpha * v + (1 - alpha) * seed
        out.append(seed)
    return out


def rma(x, n):
    """Pine ta.rma / Wilder 平滑，alpha = 1/n，SMA 种子"""
    out, seed = [], None
    for i, v in enumerate(x):
        if i == n - 1:
            seed = sum(x[:n]) / n
            out.append(seed)
            continue
        if i < n - 1:
            out.append(NAN)
            continue
        seed = seed + (v - seed) / n
        out.append(seed)
    return out


def wma(x, n):
    wsum = n * (n + 1) / 2.0
    out = []
    for i in range(len(x)):
        if i < n - 1:
            out.append(NAN)
            continue
        s = 0.0
        for k in range(n):
            s += (n - k) * x[i - k]
        out.append(s / wsum)
    return out


def hma(x, n):
    """Pine: ta.wma(2*ta.wma(src, n/2) - ta.wma(src, n), int(sqrt(n)))"""
    half = n // 2
    a, b = wma(x, half), wma(x, n)
    raw = [(2 * a[i] - b[i]) if (a[i] == a[i] and b[i] == b[i]) else NAN for i in range(len(x))]
    return wma(raw, int(math.sqrt(n)))


def rolling_median(x, n):
    out = []
    for i in range(len(x)):
        if i < n - 1:
            out.append(NAN)
            continue
        w = sorted(x[i - n + 1: i + 1])
        m = len(w)
        out.append(w[m // 2] if m % 2 else 0.5 * (w[m // 2 - 1] + w[m // 2]))
    return out


def stdev_pop(x, n):
    out = []
    for i in range(len(x)):
        if i < n - 1:
            out.append(NAN)
            continue
        w = x[i - n + 1: i + 1]
        mu = sum(w) / n
        out.append(math.sqrt(sum((v - mu) ** 2 for v in w) / n))
    return out


def atr_pine(h, l, c, n):
    tr = [NAN]
    for i in range(1, len(c)):
        tr.append(max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1])))
    return rma(tr[1:], n) and [NAN] + rma(tr[1:], n)


# ----------------------------------------------------------------------------
# 模块 1-5：Hilbert 自适应周期链
# ----------------------------------------------------------------------------

DET_K = [0.0962, 0.0, 0.5769, 0.0, -0.5769, 0.0, -0.0962]  # lags 0..6


def fir(x, k):
    out = []
    for i in range(len(x)):
        if i < len(k) - 1:
            out.append(NAN)
            continue
        s = 0.0
        for j, c in enumerate(k):
            if c:
                s += c * x[i - j]
        out.append(s)
    return out


def shift(x, n):
    return [NAN] * n + x[: len(x) - n]


def f_atan2(y, x):
    if x > 0:
        return math.atan(y / x)
    if x < 0 and y >= 0:
        return math.atan(y / x) + math.pi
    if x < 0 and y < 0:
        return math.atan(y / x) - math.pi
    if y > 0:
        return math.pi / 2
    if y < 0:
        return -math.pi / 2
    return 0.0


def hilbert_chain(close, median_len=100):
    """返回 priceSmooth / detrender / I1 / Q1 / rawPeriod / medPeriod / rsiPeriod"""
    ps = sma(close, 4)
    det = fir(ps, DET_K)
    I1 = shift(det, 3)
    Q1 = fir(det, DET_K)
    jI, jQ = shift(I1, 3), shift(Q1, 3)
    I2 = [I1[i] - jQ[i] if (I1[i] == I1[i] and jQ[i] == jQ[i]) else NAN for i in range(len(close))]
    Q2 = [Q1[i] + jI[i] if (Q1[i] == Q1[i] and jI[i] == jI[i]) else NAN for i in range(len(close))]

    raw = [NAN] * len(close)
    for i in range(1, len(close)):
        a, b, c, d = I2[i], Q2[i], I2[i - 1], Q2[i - 1]
        if any(v != v for v in (a, b, c, d)):
            continue
        Re = a * c + b * d
        Im = a * d - b * c
        ang = math.degrees(f_atan2(Im, Re))
        if ang < 0:
            ang += 360
        ang = max(ang, 1.0)
        raw[i] = 360.0 / ang

    med = rolling_median(raw, median_len)
    per = [int(med[i] / 2) if med[i] == med[i] else NAN for i in range(len(med))]
    return dict(ps=ps, det=det, I1=I1, Q1=Q1, I2=I2, Q2=Q2, raw=raw, med=med, per=per)


# ----------------------------------------------------------------------------
# 模块 6-7：自适应 RSI + HMA
# ----------------------------------------------------------------------------


def pine_rsi(x, per_series):
    """复刻脚本内手写 RSI：alpha = 1/y，无种子（nz(sum[1]) = 0）"""
    out, su, sd = [], 0.0, 0.0
    prev = NAN
    for i, v in enumerate(x):
        p = per_series[i]
        if i == 0 or p != p or p <= 0 or prev != prev:
            out.append(NAN)
            prev = v
            continue
        u = max(v - prev, 0.0)
        d = max(prev - v, 0.0)
        a = 1.0 / float(p)
        su = a * u + (1 - a) * su
        sd = a * d + (1 - a) * sd
        out.append(100.0 - 100.0 / (1.0 + su / sd) if sd != 0 else 100.0)
        prev = v
    return out


def rsi_fixed(x, n):
    """标准 Wilder RSI（带 SMA 种子），用于对照"""
    up = [NAN] + [max(x[i] - x[i - 1], 0.0) for i in range(1, len(x))]
    dn = [NAN] + [max(x[i - 1] - x[i], 0.0) for i in range(1, len(x))]
    ru, rd = rma(up[1:], n), rma(dn[1:], n)
    out = [NAN]
    for i in range(len(ru)):
        out.append(100.0 - 100.0 / (1.0 + ru[i] / rd[i]) if rd[i] and rd[i] == rd[i] else NAN)
    return out


# ----------------------------------------------------------------------------
# 模块 8：Dual Channel Squeeze
# ----------------------------------------------------------------------------


def squeeze(h, l, c, bb_len=20, bb_mult=2.0, kc_len=20, kc_mult=1.2, kc_ema=True):
    basis = sma(c, bb_len)
    dev = bb_mult
    sd = stdev_pop(c, bb_len)
    bbU = [basis[i] + dev * sd[i] if sd[i] == sd[i] else NAN for i in range(len(c))]
    bbL = [basis[i] - dev * sd[i] if sd[i] == sd[i] else NAN for i in range(len(c))]
    kb = ema_pine(c, kc_len) if kc_ema else sma(c, kc_len)
    at = atr_pine(h, l, c, kc_len)
    kcU = [kb[i] + kc_mult * at[i] if at[i] == at[i] else NAN for i in range(len(c))]
    kcL = [kb[i] - kc_mult * at[i] if at[i] == at[i] else NAN for i in range(len(c))]
    sq = [(bbU[i] < kcU[i] and bbL[i] > kcL[i]) if bbU[i] == bbU[i] else False for i in range(len(c))]
    fired = [i > 0 and sq[i - 1] and not sq[i] for i in range(len(c))]
    return dict(bbU=bbU, bbL=bbL, kcU=kcU, kcL=kcL, sq=sq, fired=fired)


# ----------------------------------------------------------------------------
# 模块 9：Pivot 背离 + 强信号
# ----------------------------------------------------------------------------


def pivot_idx(x, left, right):
    out = []
    for i in range(left, len(x) - right):
        w = x[i - left: i + right + 1]
        if x[i] != x[i]:
            continue
        if any(v != v for v in w):
            continue
        if x[i] == min(w) and sum(1 for v in w if v == x[i]) == 1:
            out.append(("L", i))
        elif x[i] == max(w) and sum(1 for v in w if v == x[i]) == 1:
            out.append(("H", i))
    return out


def divergences(rsi_v, high, low, lbL=12, lbR=1, window=80):
    piv = pivot_idx(rsi_v, lbL, lbR)
    bull, bear = [], []
    prev = {"L": None, "H": None}
    for kind, i in piv:
        p = prev[kind]
        if p is not None:
            bars = i - p
            if bars <= window:
                if kind == "L":
                    if low[i - lbR] < low[p - lbR] and rsi_v[i - lbR] > rsi_v[p - lbR]:
                        bull.append(i - lbR)
                else:
                    if high[i - lbR] > high[p - lbR] and rsi_v[i - lbR] < rsi_v[p - lbR]:
                        bear.append(i - lbR)
        prev[kind] = i
    return bull, bear


def strong_signals(rsi_v):
    b, s = [], []
    for i in range(2, len(rsi_v)):
        a, c, d = rsi_v[i], rsi_v[i - 1], rsi_v[i - 2]
        if any(v != v for v in (a, c, d)):
            continue
        if a > c and c <= d and c < 20:
            b.append(i)
        if a < c and c >= d and c > 80:
            s.append(i)
    return b, s


# ----------------------------------------------------------------------------
# 频域分析
# ----------------------------------------------------------------------------


def resp(k, P):
    """FIR 频率响应 H(e^{jω}), ω = 2π/P"""
    w = 2 * math.pi / P
    re = sum(c * math.cos(w * j) for j, c in enumerate(k))
    im = -sum(c * math.sin(w * j) for j, c in enumerate(k))
    return complex(re, im)


def quad_validation(period):
    """对纯正弦验证 I1 / Q1 是否构成 90° 正交对"""
    n = 600
    x = [math.cos(2 * math.pi * t / period) for t in range(n)]
    ps = sma(x, 4)
    det = fir(ps, DET_K)
    I1, Q1 = shift(det, 3), fir(det, DET_K)
    s, e = 300, 500
    w = 2 * math.pi / period

    def proj(y):
        """y(t)=A cos(wt+phi) -> 返回 (phi, A)。Σ y cos = A cos(phi) N/2, Σ y sin = -A sin(phi) N/2"""
        cs = sum(y[i] * math.cos(w * i) for i in range(s, e))
        sn = sum(y[i] * math.sin(w * i) for i in range(s, e))
        amp = math.hypot(cs, sn) * 2.0 / (e - s)
        return math.atan2(-sn, cs), amp

    pI, aI = proj(I1)
    pQ, aQ = proj(Q1)
    diff = math.degrees(pQ - pI)
    while diff > 180:
        diff -= 360
    while diff < -180:
        diff += 360
    G = aQ / aI if aI else NAN
    return dict(P=period, phaseI=math.degrees(pI), phaseQ=math.degrees(pQ),
                diff=diff, ampI=aI, ampQ=aQ, ratio=G,
                ecc=(1 - G) / (1 + G) if G == G else NAN)


# ----------------------------------------------------------------------------
# 合成 chirp 验证
# ----------------------------------------------------------------------------


def make_chirp(seg, n=600, trend=0.0, noise=8.0, seed=7):
    """seg = ((t0,P0),(t1,P1),(t2,P2),(t3,P3)) 分段线性瞬时周期"""
    import random
    rnd = random.Random(seed)
    truth, phase, x = [], 0.0, []

    def P_of(t):
        for k in range(3):
            if seg[k][0] <= t < seg[k + 1][0]:
                a, b = seg[k], seg[k + 1]
                return a[1] + (b[1] - a[1]) * (t - a[0]) / (b[0] - a[0])
        return seg[-1][1]

    for t in range(n):
        p = P_of(t)
        truth.append(p)
        phase += 2 * math.pi / p
        x.append(4000 + trend * t + 260 * math.cos(phase) + rnd.gauss(0, noise))
    return x, truth


def ehlers_limiter(raw, lo=6.0, hi=50.0, rate_hi=1.5, rate_lo=0.67, sm=0.25):
    """Ehlers MESA 的标准限幅链：速率限制 -> 硬钳制 -> 指数平滑"""
    out, prev = [], None
    for v in raw:
        if v != v:
            out.append(NAN)
            continue
        if prev is None or prev != prev:
            prev = v
        else:
            v = min(max(v, rate_lo * prev), rate_hi * prev)
        v = min(max(v, lo), hi)
        prev = sm * v + (1 - sm) * prev if prev == prev else v
        out.append(prev)
    return out


# ----------------------------------------------------------------------------
# 主流程
# ----------------------------------------------------------------------------


def main():
    payload = {}

    # ---- 1. 滤波器频响 -----------------------------------------------------
    periods = [2 + i * 0.25 for i in range(233)]  # 2 ~ 60
    sma4_k = [0.25] * 4
    payload["freq"] = {
        "P": periods,
        "sma4": [abs(resp(sma4_k, p)) for p in periods],
        "det": [abs(resp(DET_K, p)) for p in periods],
        "total": [abs(resp(sma4_k, p)) * abs(resp(DET_K, p)) for p in periods],
        "det_phase": [math.degrees(math.atan2(resp(DET_K, p).imag, resp(DET_K, p).real))
                      for p in periods],
        "det_phase_unwrap": [90.0 - 3.0 * (360.0 / p) for p in periods],
    }
    payload["kernels"] = {
        "det": DET_K,
        "sma4": sma4_k,
    }

    # ---- 2. Hilbert 正交性验证 ---------------------------------------------
    payload["quad"] = [quad_validation(p) for p in (6, 8, 10, 14, 20, 30, 40, 60)]

    # ---- 3. HMA 权重与频响 --------------------------------------------------
    n = 21
    hw = [0.0] * n

    def wma_weights(m):
        ws = [m - k for k in range(m)]
        s = float(sum(ws))
        return [w / s for w in ws]

    w_half, w_full = wma_weights(n // 2), wma_weights(n)
    raw_k = [0.0] * n
    for i in range(n // 2):
        raw_k[i] += 2 * w_half[i]
    for i in range(n):
        raw_k[i] -= w_full[i]
    w_sqrt = wma_weights(int(math.sqrt(n)))
    hma_k = [0.0] * (n + int(math.sqrt(n)) - 1)
    for i, a in enumerate(raw_k):
        for j, b in enumerate(w_sqrt):
            hma_k[i + j] += a * b
    payload["hma"] = {
        "n": n,
        "raw_kernel": raw_k,
        "kernel": hma_k,
        "P": periods,
        "gain": [abs(resp(hma_k, p)) for p in periods],
        "gain_rma10": [abs(resp([1.0 / 10] * 10, p)) for p in periods],
    }

    # ---- 4. 合成 chirp（通带内 / 通带外）-----------------------------------
    def chirp_pack(seg, trend, noise, tag):
        x, truth = make_chirp(seg, trend=trend, noise=noise)
        ch = hilbert_chain(x, 100)
        raw = ch["raw"]
        el = ehlers_limiter(raw)
        def mae(y):
            e = [abs(y[i] - truth[i]) for i in range(150, 600) if y[i] == y[i]]
            b = [y[i] - truth[i] for i in range(150, 600) if y[i] == y[i]]
            return round(sum(e) / len(e), 2), round(sum(b) / len(b), 2)
        m1, b1 = mae(ch["med"])
        m2, b2 = mae(el)
        return dict(tag=tag, price=[round(v, 2) for v in x],
                    truth=[round(v, 2) for v in truth],
                    raw=[round(v, 2) if v == v else None for v in raw],
                    med=[round(v, 2) if v == v else None for v in ch["med"]],
                    ehlers=[round(v, 2) if v == v else None for v in el],
                    mae_med=m1, bias_med=b1, mae_ehlers=m2, bias_ehlers=b2)

    payload["chirp"] = {
        "inband": chirp_pack(((0, 8), (200, 8), (400, 20), (600, 8)), 0.0, 8.0, "通带内 8→20→8"),
        "outband": chirp_pack(((0, 30), (200, 30), (400, 60), (600, 40)), 0.0, 8.0, "通带外 30→60→40"),
    }

    # ---- 5. BTC 1D 实证 -----------------------------------------------------
    rows = list(csv.DictReader(open(CSV_PATH)))
    dates = [r["time"] for r in rows]
    o = [float(r["open"]) for r in rows]
    hi = [float(r["high"]) for r in rows]
    lo = [float(r["low"]) for r in rows]
    cl = [float(r["close"]) for r in rows]

    h = hilbert_chain(cl, 100)
    hper = [1 if p != p or p < 1 else p for p in h["per"]]
    base = pine_rsi(cl, hper)
    rv = hma(base, 21)
    r14 = rsi_fixed(cl, 14)
    sq = squeeze(hi, lo, cl)
    bull, bear = divergences(rv, hi, lo)
    sb, ss = strong_signals(rv)

    def clean(a, nd=3):
        return [round(v, nd) if v == v and abs(v) != float("inf") else None for v in a]

    # Ehlers 限幅对照
    el = ehlers_limiter(h["raw"])
    elper = [1 if p != p or p < 1 else int(p / 2) for p in el]
    el_rsi = pine_rsi(cl, elper)
    el_rv = hma(el_rsi, 21)

    payload["btc"] = {
        "dates": dates,
        "close": clean(cl, 2),
        "raw": clean(h["raw"], 2),
        "med": clean(h["med"], 2),
        "ehlers": clean(el, 2),
        "perEhlers": elper,
        "rsiEhlers": clean(el_rv, 3),
        "per": hper,
        "base": clean(base, 2),
        "rsi": clean(rv, 3),
        "rsi14": clean(r14, 2),
        "squeeze": [1 if v else 0 for v in sq["sq"]],
        "fired": [1 if v else 0 for v in sq["fired"]],
        "bullDiv": bull,
        "bearDiv": bear,
        "strongBull": sb,
        "strongBear": ss,
        "phasor": [[round(h["I1"][i] / max(abs(h["I1"][j]) for j in range(-160, 0) if h["I1"][j] == h["I1"][j]), 4),
                    round(h["Q1"][i] / max(abs(h["I1"][j]) for j in range(-160, 0) if h["I1"][j] == h["I1"][j]), 4)]
                   for i in range(len(cl) - 160, len(cl))],
    }

    vals = [v for v in rv if v == v]
    payload["stats"] = {
        "bars": len(cl),
        "span": dates[0] + " ~ " + dates[-1],
        "per_min": min(hper[100:]),
        "per_max": max(hper[100:]),
        "per_median": sorted(hper[100:])[len(hper[100:]) // 2],
        "rsi_min": round(min(vals), 2),
        "rsi_max": round(max(vals), 2),
        "overshoot_hi": sum(1 for v in vals if v > 100),
        "overshoot_lo": sum(1 for v in vals if v < 0),
        "squeeze_bars": sum(sq["sq"]),
        "squeeze_pct": round(100.0 * sum(sq["sq"]) / len(cl), 1),
        "fired": sum(sq["fired"]),
        "bullDiv": len(bull),
        "bearDiv": len(bear),
        "strongBull": len(sb),
        "strongBear": len(ss),
        "zero_period_guard": sum(1 for p in h["per"] if p == p and p < 1),
        "corr_adaptive_vs_fixed": None,
        "per_ehlers_min": min(elper[100:]),
        "per_ehlers_max": max(elper[100:]),
        "per_ehlers_median": sorted(elper[100:])[len(elper[100:]) // 2],
        "raw_negative_share": round(
            100.0 * sum(1 for v in h["raw"] if v == v and v < 2.0) / max(1, sum(1 for v in h["raw"] if v == v)), 1),
        "raw_hi_share": round(
            100.0 * sum(1 for v in h["raw"] if v == v and v > 40.0) / max(1, sum(1 for v in h["raw"] if v == v)), 1),
    }
    # 原始瞬时周期直方图（对数分箱）
    bins = [(0, 2), (2, 4), (4, 6), (6, 8), (8, 10), (10, 14), (14, 20), (20, 30), (30, 50), (50, 100), (100, 400)]
    valid = [v for v in h["raw"] if v == v]
    payload["stats"]["raw_hist"] = [
        dict(label="%g–%g" % (a, b), n=sum(1 for v in valid if a <= v < b), pct=round(100.0 * sum(1 for v in valid if a <= v < b) / len(valid), 1))
        for a, b in bins]
    # ---- 6. 钝化（饱和）分析 ------------------------------------------------
    def blunt(a, name):
        v = [x for x in a if x == x]
        n = max(1, len(v))
        run = mx = 0
        for x in a:
            if x == x and x >= 80:
                run += 1
                mx = max(mx, run)
            else:
                run = 0
        return dict(name=name, n=len(v),
                    hi=sum(1 for x in v if x >= 80), lo=sum(1 for x in v if x <= 20),
                    ex=sum(1 for x in v if x >= 90 or x <= 10),
                    pin=sum(1 for x in v if x >= 97 or x <= 3),
                    run=mx,
                    hi_pct=round(100.0 * sum(1 for x in v if x >= 80) / n, 1),
                    lo_pct=round(100.0 * sum(1 for x in v if x <= 20) / n, 1),
                    ex_pct=round(100.0 * sum(1 for x in v if x >= 90 or x <= 10) / n, 1),
                    pin_pct=round(100.0 * sum(1 for x in v if x >= 97 or x <= 3) / n, 1))

    payload["blunt"] = {
        "rows": [blunt(base, "base_rsi（N 自适应，实测 1–4）"),
                 blunt(rv, "rsi_v（+ HMA21）"),
                 blunt(r14, "RSI(14) 固定")] +
                [blunt(rsi_fixed(cl, k), "RSI(%d) 固定" % k) for k in (2, 3, 4, 7, 14, 21, 50)],
        "sens": [dict(r=r, s=round(r * (100 - r) / 100.0, 3),
                      L=round(math.log(r / (100.0 - r)), 3)) for r in
                 list(range(1, 100))],
        "curve": [dict(L=round(-5 + i * 0.25, 3),
                       rsi=round(100.0 / (1.0 + math.exp(5 - i * 0.25)), 3))
                  for i in range(41)],
    }

    # 自适应 vs 固定 RSI 相关性（重叠区间）
    pairs = [(rv[i], r14[i]) for i in range(len(rv)) if rv[i] == rv[i] and r14[i] == r14[i]]
    if len(pairs) > 10:
        ma = sum(p[0] for p in pairs) / len(pairs)
        mb = sum(p[1] for p in pairs) / len(pairs)
        cov = sum((p[0] - ma) * (p[1] - mb) for p in pairs)
        va = math.sqrt(sum((p[0] - ma) ** 2 for p in pairs))
        vb = math.sqrt(sum((p[1] - mb) ** 2 for p in pairs))
        payload["stats"]["corr_adaptive_vs_fixed"] = round(cov / (va * vb), 3)

    with open(JSON_OUT, "w") as f:
        json.dump(payload, f, separators=(",", ":"))
    print("wrote", JSON_OUT, os.path.getsize(JSON_OUT), "bytes")
    print("stats:", json.dumps(payload["stats"], ensure_ascii=False, indent=1))
    print("quad:", [(q["P"], round(q["diff"], 1), round(q["ratio"], 3)) for q in payload["quad"]])

    if "--inject" in sys.argv and os.path.exists(HTML_TPL):
        import re
        html = open(HTML_TPL).read()
        blob = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
        # 幂等：无论占位符是否已替换过，都整体重写这一行。
        # 用 lambda 作替换体，避免 blob 中的反斜杠被 re 当作转义处理。
        new, k = re.subn(r"^const DATA = .*;$", lambda _m: "const DATA = " + blob + ";",
                         html, count=1, flags=re.M)
        if k == 0:
            raise SystemExit("未找到 const DATA = ... 行，注入失败")
        open(HTML_TPL, "w").write(new)
        print("injected ->", HTML_TPL, len(blob), "bytes")


if __name__ == "__main__":
    main()
