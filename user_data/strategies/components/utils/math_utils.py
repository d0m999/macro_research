"""
数学工具函数
为量化交易策略提供专业的数学计算功能

功能模块：
1. 统计分析函数
2. 技术指标计算
3. 风险度量
4. 性能评估
5. 信号处理
"""

import numpy as np
import pandas as pd
from typing import Union, Tuple, Optional, List
from scipy import stats
from scipy.signal import savgol_filter
import warnings

def safe_divide(numerator: Union[float, np.ndarray], 
               denominator: Union[float, np.ndarray], 
               default: float = 0.0) -> Union[float, np.ndarray]:
    """
    安全除法，避免除零错误
    
    Args:
        numerator: 分子
        denominator: 分母
        default: 除零时的默认值
        
    Returns:
        除法结果
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = np.divide(numerator, denominator, 
                          out=np.full_like(numerator, default, dtype=float), 
                          where=(denominator != 0))
    return result

def rolling_zscore(series: pd.Series, window: int = 20) -> pd.Series:
    """
    计算滚动Z分数
    
    Args:
        series: 输入序列
        window: 滚动窗口大小
        
    Returns:
        Z分数序列
    """
    rolling_mean = series.rolling(window=window).mean()
    rolling_std = series.rolling(window=window).std()
    
    return safe_divide(series - rolling_mean, rolling_std)

def rolling_percentile_rank(series: pd.Series, window: int = 20) -> pd.Series:
    """
    计算滚动百分位排名
    
    Args:
        series: 输入序列
        window: 滚动窗口大小
        
    Returns:
        百分位排名序列 (0-1)
    """
    return series.rolling(window=window).rank(pct=True)

def exponential_smoothing(series: pd.Series, alpha: float = 0.3) -> pd.Series:
    """
    指数平滑
    
    Args:
        series: 输入序列
        alpha: 平滑参数 (0-1)
        
    Returns:
        平滑后的序列
    """
    return series.ewm(alpha=alpha).mean()

def adaptive_ema(series: pd.Series, fast_period: int = 2, 
                slow_period: int = 30, volatility_period: int = 10) -> pd.Series:
    """
    自适应指数移动平均
    根据波动性调整平滑参数
    
    Args:
        series: 输入序列
        fast_period: 快速周期
        slow_period: 慢速周期
        volatility_period: 波动性计算周期
        
    Returns:
        自适应EMA序列
    """
    # 计算波动性（标准差）
    volatility = series.rolling(window=volatility_period).std()
    max_vol = volatility.rolling(window=50).max()
    min_vol = volatility.rolling(window=50).min()
    
    # 标准化波动性 (0-1)
    normalized_vol = safe_divide(volatility - min_vol, max_vol - min_vol)
    
    # 计算自适应平滑常数
    fast_sc = 2.0 / (fast_period + 1)
    slow_sc = 2.0 / (slow_period + 1)
    
    # 根据波动性调整平滑常数
    adaptive_sc = slow_sc + (fast_sc - slow_sc) * normalized_vol
    
    # 计算自适应EMA
    result = pd.Series(index=series.index, dtype=float)
    result.iloc[0] = series.iloc[0]
    
    for i in range(1, len(series)):
        if pd.notna(adaptive_sc.iloc[i]):
            result.iloc[i] = (adaptive_sc.iloc[i] * series.iloc[i] + 
                            (1 - adaptive_sc.iloc[i]) * result.iloc[i-1])
        else:
            result.iloc[i] = result.iloc[i-1]
    
    return result

def hilbert_transform_period(series: pd.Series) -> pd.Series:
    """
    希尔伯特变换周期检测
    用于自适应指标的周期计算
    
    Args:
        series: 输入价格序列
        
    Returns:
        检测到的周期序列
    """
    # 价格平滑
    smooth = (series + series.shift(1) + series.shift(2) + series.shift(3)) / 4
    
    # 去趋势
    detrender = (0.0962 * smooth + 0.5769 * smooth.shift(2) - 
                0.5769 * smooth.shift(4) - 0.0962 * smooth.shift(6))
    
    # 希尔伯特变换
    I1 = detrender.shift(3)
    Q1 = (0.0962 * detrender + 0.5769 * detrender.shift(2) - 
          0.5769 * detrender.shift(4) - 0.0962 * detrender.shift(6))
    
    # 正交分量
    jI = I1.shift(3)
    jQ = Q1.shift(3)
    
    I2 = I1 - jQ
    Q2 = Q1 + jI
    
    # 相位计算
    Re = I2 * I2.shift(1) + Q2 * Q2.shift(1)
    Im = I2 * Q2.shift(1) - Q2 * I2.shift(1)
    
    # 相位角
    phase = np.degrees(np.arctan2(Im, Re))
    phase = np.where(phase < 0, phase + 360, phase)
    phase = np.maximum(phase, 1.0)  # 避免除零
    
    # 计算周期
    period = 360 / phase
    
    # 平滑周期
    smoothed_period = period.rolling(window=50, center=True).median()
    
    return smoothed_period.fillna(14)  # 默认周期14

def calculate_fractal_dimension(series: pd.Series, window: int = 20) -> pd.Series:
    """
    计算分形维数
    用于衡量价格序列的复杂性和趋势强度
    
    Args:
        series: 输入序列
        window: 计算窗口
        
    Returns:
        分形维数序列
    """
    def _fractal_dim(data):
        """计算单个窗口的分形维数"""
        if len(data) < 4:
            return 1.5
        
        # 计算不同尺度下的变化
        scales = [1, 2, 4]
        fluctuations = []
        
        for scale in scales:
            if scale >= len(data):
                continue
            
            # 重新采样
            resampled = data[::scale]
            if len(resampled) < 2:
                continue
            
            # 计算累积偏差
            cumsum = np.cumsum(resampled - np.mean(resampled))
            
            # 计算波动
            fluctuation = np.std(cumsum)
            fluctuations.append(fluctuation)
        
        if len(fluctuations) < 2:
            return 1.5
        
        # 计算分形维数
        log_scales = np.log(scales[:len(fluctuations)])
        log_flucts = np.log(fluctuations)
        
        # 线性回归
        slope, _, _, _, _ = stats.linregress(log_scales, log_flucts)
        
        # 分形维数
        fractal_dim = 2 - slope
        
        return np.clip(fractal_dim, 1.0, 2.0)
    
    return series.rolling(window=window).apply(_fractal_dim, raw=True)

def calculate_hurst_exponent(series: pd.Series, window: int = 100) -> pd.Series:
    """
    计算Hurst指数
    用于判断时间序列的长期记忆性
    
    Args:
        series: 输入序列
        window: 计算窗口
        
    Returns:
        Hurst指数序列
    """
    def _hurst_exp(data):
        """计算单个窗口的Hurst指数"""
        if len(data) < 20:
            return 0.5
        
        # 计算对数收益率
        log_returns = np.log(data / data.shift(1)).dropna()
        
        if len(log_returns) < 10:
            return 0.5
        
        # 不同时间尺度
        lags = range(2, min(20, len(log_returns) // 2))
        tau = []
        
        for lag in lags:
            # 计算重标极差
            ts = log_returns.values
            n = len(ts)
            
            # 分段
            segments = n // lag
            if segments < 2:
                continue
            
            rs_values = []
            
            for i in range(segments):
                start = i * lag
                end = start + lag
                segment = ts[start:end]
                
                if len(segment) < 2:
                    continue
                
                # 累积偏差
                mean_segment = np.mean(segment)
                cumsum_segment = np.cumsum(segment - mean_segment)
                
                # 极差
                R = np.max(cumsum_segment) - np.min(cumsum_segment)
                
                # 标准差
                S = np.std(segment)
                
                if S > 0:
                    rs_values.append(R / S)
            
            if rs_values:
                tau.append(np.mean(rs_values))
        
        if len(tau) < 3:
            return 0.5
        
        # 线性回归计算Hurst指数
        log_lags = np.log(lags[:len(tau)])
        log_tau = np.log(tau)
        
        slope, _, _, _, _ = stats.linregress(log_lags, log_tau)
        
        return np.clip(slope, 0.0, 1.0)
    
    return series.rolling(window=window).apply(_hurst_exp, raw=False)

def smooth_noise_robust(series: pd.Series, window: int = 5, 
                       polyorder: int = 2) -> pd.Series:
    """
    抗噪声平滑
    使用Savitzky-Golay滤波器
    
    Args:
        series: 输入序列
        window: 滤波窗口（必须为奇数）
        polyorder: 多项式阶数
        
    Returns:
        平滑后的序列
    """
    if window % 2 == 0:
        window += 1  # 确保为奇数
    
    if len(series) < window:
        return series
    
    # 处理NaN值
    mask = ~series.isna()
    if mask.sum() < window:
        return series
    
    # 应用Savitzky-Golay滤波
    try:
        smoothed_values = savgol_filter(series[mask].values, window, polyorder)
        result = series.copy()
        result.loc[mask] = smoothed_values
        return result
    except:
        return series

def calculate_entropy(series: pd.Series, bins: int = 10, window: int = 50) -> pd.Series:
    """
    计算滚动熵
    用于衡量价格分布的随机性
    
    Args:
        series: 输入序列
        bins: 直方图分箱数
        window: 滚动窗口
        
    Returns:
        熵值序列
    """
    def _entropy(data):
        """计算单个窗口的熵"""
        if len(data) < 5:
            return 0
        
        # 创建直方图
        hist, _ = np.histogram(data, bins=bins)
        
        # 计算概率
        probs = hist / np.sum(hist)
        probs = probs[probs > 0]  # 移除零概率
        
        # 计算熵
        entropy = -np.sum(probs * np.log2(probs))
        
        return entropy
    
    return series.rolling(window=window).apply(_entropy, raw=True)

def detect_regime_change(series: pd.Series, window: int = 50, 
                        threshold: float = 2.0) -> pd.Series:
    """
    检测市场状态变化
    基于统计特性的变化
    
    Args:
        series: 输入序列
        window: 检测窗口
        threshold: 变化阈值
        
    Returns:
        状态变化信号 (1: 变化, 0: 无变化)
    """
    # 计算滚动统计量
    rolling_mean = series.rolling(window=window).mean()
    rolling_std = series.rolling(window=window).std()
    rolling_skew = series.rolling(window=window).skew()
    
    # 计算统计量的变化率
    mean_change = abs(rolling_mean.pct_change())
    std_change = abs(rolling_std.pct_change())
    skew_change = abs(rolling_skew.diff())
    
    # 综合变化指标
    change_score = (mean_change + std_change + skew_change) / 3
    
    # 检测显著变化
    change_threshold = change_score.rolling(window=window).quantile(0.95)
    regime_change = (change_score > change_threshold * threshold).astype(int)
    
    return regime_change

def calculate_drawdown_series(equity_curve: pd.Series) -> Tuple[pd.Series, pd.Series]:
    """
    计算回撤序列
    
    Args:
        equity_curve: 权益曲线
        
    Returns:
        (回撤序列, 回撤百分比序列)
    """
    # 计算累积最高点
    peak = equity_curve.expanding().max()
    
    # 计算回撤
    drawdown = equity_curve - peak
    drawdown_pct = drawdown / peak
    
    return drawdown, drawdown_pct

def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.0, 
                         periods: int = 252) -> float:
    """
    计算夏普比率
    
    Args:
        returns: 收益率序列
        risk_free_rate: 无风险利率
        periods: 年化周期数
        
    Returns:
        夏普比率
    """
    excess_returns = returns - risk_free_rate / periods
    
    if excess_returns.std() == 0:
        return 0.0
    
    sharpe = excess_returns.mean() / excess_returns.std() * np.sqrt(periods)
    
    return sharpe

def calculate_sortino_ratio(returns: pd.Series, target_return: float = 0.0, 
                          periods: int = 252) -> float:
    """
    计算索提诺比率
    
    Args:
        returns: 收益率序列
        target_return: 目标收益率
        periods: 年化周期数
        
    Returns:
        索提诺比率
    """
    excess_returns = returns - target_return / periods
    downside_returns = excess_returns[excess_returns < 0]
    
    if len(downside_returns) == 0 or downside_returns.std() == 0:
        return float('inf') if excess_returns.mean() > 0 else 0.0
    
    sortino = excess_returns.mean() / downside_returns.std() * np.sqrt(periods)
    
    return sortino

def calculate_calmar_ratio(returns: pd.Series, periods: int = 252) -> float:
    """
    计算卡玛比率
    
    Args:
        returns: 收益率序列
        periods: 年化周期数
        
    Returns:
        卡玛比率
    """
    # 计算年化收益率
    annual_return = returns.mean() * periods
    
    # 计算最大回撤
    equity_curve = (1 + returns).cumprod()
    _, drawdown_pct = calculate_drawdown_series(equity_curve)
    max_drawdown = abs(drawdown_pct.min())
    
    if max_drawdown == 0:
        return float('inf') if annual_return > 0 else 0.0
    
    calmar = annual_return / max_drawdown
    
    return calmar