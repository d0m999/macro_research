#!/usr/bin/env python3
"""gate.py 与 attribute.py 共用的基础统计（纯标准库，无第三方依赖）。

口径约定：所有 Sharpe 一律先算**单期**值再做检验，避免年化因子
（252 / 365）影响结论。年化值只在报告里给人类阅读。
"""

import math
from statistics import NormalDist

NORM = NormalDist()
EULER_GAMMA = 0.5772156649015329


def mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def stdev(xs, ddof=1):
    n = len(xs)
    if n - ddof <= 0:
        return 0.0
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (n - ddof))


def sharpe(xs):
    """单期 Sharpe。"""
    s = stdev(xs)
    return mean(xs) / s if s > 0 else 0.0


def skewness(xs):
    n = len(xs)
    if n < 3:
        return 0.0
    m, s = mean(xs), stdev(xs)
    if s == 0:
        return 0.0
    g1 = sum(((x - m) / s) ** 3 for x in xs) / n
    return math.sqrt(n * (n - 1)) / (n - 2) * g1


def kurtosis_raw(xs):
    """raw kurtosis（正态 = 3）。PSR 分母要的是 raw，不是 excess。"""
    n = len(xs)
    if n < 4:
        return 3.0
    m, s = mean(xs), stdev(xs)
    if s == 0:
        return 3.0
    m4 = sum(((x - m) / s) ** 4 for x in xs) / n
    g2 = (n * (n + 1) * m4 - 3 * (n - 1) ** 2) / ((n - 2) * (n - 3))
    return g2 + 3.0


def deflated_sr_threshold(n, n_trials, sr_hat):
    """SR*：N 次试验下纯运气能达到的 Sharpe 期望最大值（Bailey & López de Prado）。

    N<=1 时 Φ⁻¹(0) = −∞，退化为无校正，按原作者处理取 0。
    """
    if n_trials <= 1:
        return 0.0
    var_sr = (1.0 + 0.5 * sr_hat ** 2) / n
    sd = math.sqrt(var_sr)
    z1 = NORM.inv_cdf(1.0 - 1.0 / n_trials)
    z2 = NORM.inv_cdf(1.0 - 1.0 / (n_trials * math.e))
    return sd * ((1 - EULER_GAMMA) * z1 + EULER_GAMMA * z2)


def psr(sr_hat, n, sr_star, skew, kurt):
    """概率夏普比率：SR̂ 真实值大于 SR* 的概率。"""
    denom = 1.0 - skew * sr_hat + ((kurt - 1.0) / 4.0) * sr_hat ** 2
    if denom <= 0:
        return 0.0
    z = (sr_hat - sr_star) * math.sqrt(n - 1) / math.sqrt(denom)
    return NORM.cdf(z)


def max_drawdown(returns):
    """按累计净值算最大回撤（返回负数）。"""
    equity, peak, mdd = 1.0, 1.0, 0.0
    for r in returns:
        equity *= (1.0 + r)
        peak = max(peak, equity)
        mdd = min(mdd, equity / peak - 1.0)
    return mdd


def win_rate(xs):
    if not xs:
        return 0.0
    return sum(1 for x in xs if x > 0) / len(xs)


def cumulative(xs):
    eq = 1.0
    for r in xs:
        eq *= (1.0 + r)
    return eq - 1.0
