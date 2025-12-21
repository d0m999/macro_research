# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa: F401
# isort: skip_file
# --- Do not remove these libs ---
import numpy as np
import pandas as pd
from pandas import DataFrame
from datetime import datetime
from typing import Optional, Union
import logging

from freqtrade.strategy import (
    IStrategy,
    BooleanParameter,
    CategoricalParameter,
    DecimalParameter,
    IntParameter,
    merge_informative_pair,
)

# --------------------------------
# Add your lib to import here
import talib.abstract as ta
from technical import qtpylib
from freqtrade.exchange import timeframe_to_prev_date
from freqtrade.strategy import informative

logger = logging.getLogger(__name__)


class LoopRSIStrategy(IStrategy):
    """
    L∞p | RSI Strategy - 自适应共振振荡器 RSI 策略

    基于 PineScript 策略 "detrender RSI" 的 Freqtrade 实现。

    核心特性：
    1. 自适应周期检测（希尔伯特变换）
    2. 动态周期 RSI
    3. HMA 平滑处理
    4. Dual Channel Squeeze 检测
    5. 超买/超卖信号交易

    作者：d0m999
    版本：1.0
    """

    # 策略接口版本
    INTERFACE_VERSION = 3

    # 支持做空（期货）
    can_short: bool = True
    
    # Phase 2: 交易状态跟踪 (用于部分止盈)
    def __init__(self, config: dict) -> None:
        super().__init__(config)
        # 跟踪每个交易的部分止盈状态
        self.trade_partial_tp_status = {}  # {trade_id: {'tp1_done': bool, 'tp2_done': bool}}

    # 时间周期
    timeframe = '1h'

    # 最小 ROI 设置
    minimal_roi = {
        "0": 0.15,      # 开仓即可获利 15%
        "120": 0.10,    # 2 小时后 10%
        "360": 0.05,    # 6 小时后 5%
        "720": 0.02,    # 12 小时后 2%
    }

    # 止损设置（优化后）
    stoploss = -0.01  # 1% 止损（更紧）

    # 追踪止损（优化后）
    trailing_stop = True
    trailing_stop_positive = 0.05  # 5% 盈利后开始追踪
    trailing_stop_positive_offset = 0.06  # 6% 盈利后激活追踪
    trailing_only_offset_is_reached = True

    # 策略所需的启动蜡烛数量
    startup_candle_count: int = 200

    # 仅在新蜡烛时运行
    process_only_new_candles = True

    # 使用出场信号
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False

    # ==========================================================================
    # 策略参数（可用于 Hyperopt 优化）
    # ==========================================================================

    # 自适应振荡器参数
    enable_smoothing = BooleanParameter(default=True, space="buy", optimize=True)
    smoothing_length = IntParameter(10, 50, default=21, space="buy", optimize=True)
    median_length = IntParameter(50, 200, default=100, space="buy", optimize=False)

    # RSI 阈值参数
    rsi_oversold = IntParameter(10, 30, default=20, space="buy", optimize=True)
    rsi_overbought = IntParameter(70, 90, default=80, space="sell", optimize=True)

    # Dual Channel Squeeze 参数
    bb_length = IntParameter(10, 30, default=20, space="buy", optimize=False)
    bb_mult = DecimalParameter(1.5, 3.0, default=2.0, decimals=1, space="buy", optimize=False)
    kc_length = IntParameter(10, 30, default=20, space="buy", optimize=False)
    kc_mult = DecimalParameter(1.0, 2.0, default=1.2, decimals=1, space="buy", optimize=False)

    # 是否使用挤压过滤器（优化后默认启用）
    use_squeeze_filter = BooleanParameter(default=True, space="buy", optimize=True)

    # EMA200 趋势过滤器（新增）
    use_trend_filter = BooleanParameter(default=True, space="buy", optimize=True)
    trend_ema_period = IntParameter(100, 300, default=200, space="buy", optimize=True)

    # 动态仓位和止损参数
    risk_per_trade = DecimalParameter(0.01, 0.05, default=0.01, decimals=2, space="buy", optimize=True)
    # stoploss_ema 不再作为全局参数，而是由入场信号决定
    
    # 均线测试参数
    ema_test_tolerance = DecimalParameter(0.001, 0.01, default=0.005, decimals=3, space="buy", optimize=True)
    
    # 止损缓冲
    sl_buffer = DecimalParameter(0.005, 0.02, default=0.01, decimals=3, space="buy", optimize=True)

    # ==========================================================================
    # Phase 2: 价格位置过滤器参数
    # ==========================================================================
    
    # 启用价格位置过滤器
    use_price_position_filter = BooleanParameter(default=True, space="buy", optimize=True)
    
    # 价格位置范围设置（相对于近期高低点的百分比）
    price_position_low_threshold = DecimalParameter(0.1, 0.3, default=0.2, decimals=2, space="buy", optimize=True)
    price_position_high_threshold = DecimalParameter(0.7, 0.9, default=0.8, decimals=2, space="buy", optimize=True)
    
    # 价格位置计算周期
    price_position_period = IntParameter(20, 100, default=50, space="buy", optimize=True)
    
    # ==========================================================================
    # Phase 2: 多重止盈触发条件参数
    # ==========================================================================
    
    # 启用多重止盈
    use_multiple_take_profit = BooleanParameter(default=True, space="sell", optimize=True)
    
    # 第一重止盈目标 (快速止盈)
    tp1_percentage = DecimalParameter(0.5, 2.0, default=1.0, decimals=1, space="sell", optimize=True)
    tp1_size_ratio = DecimalParameter(0.2, 0.5, default=0.3, decimals=1, space="sell", optimize=True)
    
    # 第二重止盈目标 (中期止盈)
    tp2_percentage = DecimalParameter(1.0, 3.0, default=2.0, decimals=1, space="sell", optimize=True)
    tp2_size_ratio = DecimalParameter(0.3, 0.6, default=0.4, decimals=1, space="sell", optimize=True)
    
    # 第三重止盈目标 (长期止盈/移动止损)
    tp3_trailing_activation = DecimalParameter(1.5, 4.0, default=2.5, decimals=1, space="sell", optimize=True)
    tp3_trailing_distance = DecimalParameter(0.5, 2.0, default=1.0, decimals=1, space="sell", optimize=True)
    
    # ==========================================================================
    # Phase 2: 部分止盈机制参数
    # ==========================================================================
    
    # 启用部分止盈
    use_partial_take_profit = BooleanParameter(default=True, space="sell", optimize=True)
    
    # 部分止盈触发条件和比例
    partial_tp1_profit = DecimalParameter(0.5, 1.5, default=1.0, decimals=1, space="sell", optimize=True)
    partial_tp1_ratio = DecimalParameter(0.2, 0.4, default=0.3, decimals=1, space="sell", optimize=True)
    
    partial_tp2_profit = DecimalParameter(1.0, 2.5, default=2.0, decimals=1, space="sell", optimize=True)
    partial_tp2_ratio = DecimalParameter(0.3, 0.5, default=0.4, decimals=1, space="sell", optimize=True)
    
    # ==========================================================================
    # Phase 3: 市场波动性过滤器参数
    # ==========================================================================
    
    # 启用市场波动性过滤器
    use_volatility_filter = BooleanParameter(default=True, space="buy", optimize=True)
    
    # ATR周期和倍数
    volatility_atr_period = IntParameter(14, 50, default=20, space="buy", optimize=True)
    volatility_atr_multiplier = DecimalParameter(0.5, 3.0, default=1.5, decimals=1, space="buy", optimize=True)
    
    # 波动性阈值设置
    low_volatility_threshold = DecimalParameter(0.5, 1.5, default=1.0, decimals=1, space="buy", optimize=True)
    high_volatility_threshold = DecimalParameter(2.0, 5.0, default=3.0, decimals=1, space="buy", optimize=True)
    
    # ==========================================================================
    # Phase 3: 市场环境适应性止盈参数
    # ==========================================================================
    
    # 启用市场环境适应性止盈
    use_adaptive_take_profit = BooleanParameter(default=True, space="sell", optimize=True)
    
    # 趋势市场止盈调整
    trend_tp_multiplier = DecimalParameter(1.0, 2.0, default=1.5, decimals=1, space="sell", optimize=True)
    trend_trailing_activation = DecimalParameter(1.0, 3.0, default=2.0, decimals=1, space="sell", optimize=True)
    
    # 震荡市场止盈调整
    ranging_tp_multiplier = DecimalParameter(0.5, 1.5, default=1.0, decimals=1, space="sell", optimize=True)
    ranging_trailing_activation = DecimalParameter(1.5, 3.5, default=2.5, decimals=1, space="sell", optimize=True)
    
    # ==========================================================================
    # Phase 3: 相关性止盈参数
    # ==========================================================================
    
    # 启用相关性止盈
    use_correlation_exit = BooleanParameter(default=True, space="sell", optimize=True)
    
    # 相关性交易对列表 (主要加密货币对)
    correlation_pairs = ["BTC/USDT", "ETH/USDT"]
    
    # 相关性止盈阈值
    correlation_profit_threshold = DecimalParameter(1.0, 3.0, default=2.0, decimals=1, space="sell", optimize=True)
    correlation_avg_profit_threshold = DecimalParameter(0.5, 2.0, default=1.5, decimals=1, space="sell", optimize=True)
    
    # 订单类型
    order_types = {
        'entry': 'limit',
        'exit': 'limit',
        'stoploss': 'market',
        'stoploss_on_exchange': False
    }

    # 订单有效期
    order_time_in_force = {
        'entry': 'GTC',
        'exit': 'GTC'
    }

    # ==========================================================================
    # 绘图配置
    # ==========================================================================
    @property
    def plot_config(self):
        return {
            'main_plot': {
                'bb_upperband': {'color': 'rgba(150, 150, 150, 0.5)'},
                'bb_lowerband': {'color': 'rgba(150, 150, 150, 0.5)'},
                'kc_upperband': {'color': 'rgba(100, 100, 255, 0.5)'},
                'kc_lowerband': {'color': 'rgba(100, 100, 255, 0.5)'},
            },
            'subplots': {
                "Adaptive RSI": {
                    'adaptive_rsi': {'color': 'blue'},
                    'rsi_oversold_line': {'color': 'green'},
                    'rsi_overbought_line': {'color': 'red'},
                },
                "Market Period": {
                    'market_period': {'color': 'purple'},
                },
                "Squeeze": {
                    'is_squeeze': {'color': 'orange'},
                },
            }
        }

    # ==========================================================================
    # 辅助函数
    # ==========================================================================

    def _calculate_hilbert_period(self, dataframe: DataFrame) -> DataFrame:
        """
        计算希尔伯特变换周期（向量化优化版本）

        使用希尔伯特变换从价格数据中提取主导周期。
        向量化实现显著提高计算效率，避免循环操作。
        """
        close = dataframe['close'].values
        n = len(close)

        if n < 7:  # 确保有足够的数据进行计算
            dataframe['hilbert_period_raw'] = np.full(n, 10.0)
            return dataframe

        # 向量化价格平滑：使用卷积实现4周期移动平均
        # 语法解析：np.convolve(a, v, mode='valid') 计算卷积
        # 数学原理：(close[i] + close[i-1] + close[i-2] + close[i-3]) / 4
        kernel = np.array([0.25, 0.25, 0.25, 0.25])  # 4周期平均卷积核
        price_smooth = np.zeros(n)
        price_smooth[3:] = np.convolve(close, kernel, mode='valid')

        # 向量化去趋势处理：使用numpy切片和广播
        # 语法解析：数组切片 + 向量运算
        # 数学原理：detrender[i] = 0.0962*price_smooth[i] + 0.5769*price_smooth[i-2] - 0.5769*price_smooth[i-4] - 0.0962*price_smooth[i-6]
        detrender = np.zeros(n)
        valid_start = 6
        detrender[valid_start:] = (
            0.0962 * price_smooth[valid_start:] +
            0.5769 * price_smooth[valid_start-2:] -
            0.5769 * price_smooth[valid_start-4:] -
            0.0962 * price_smooth[valid_start-6:]
        )

        # 向量化希尔伯特变换分量
        # 语法解析：数组切片实现时间延迟
        # 数学原理：I1[i] = detrender[i-3], Q1[i] = 0.0962*detrender[i] + 0.5769*detrender[i-2] - 0.5769*detrender[i-4] - 0.0962*detrender[i-6]
        I1 = np.zeros(n)
        Q1 = np.zeros(n)
        
        I1[3:] = detrender[:-3]  # 延迟3周期
        Q1[valid_start:] = (
            0.0962 * detrender[valid_start:] +
            0.5769 * detrender[valid_start-2:] -
            0.5769 * detrender[valid_start-4:] -
            0.0962 * detrender[valid_start-6:]
        )

        # 向量化jI和jQ计算（延迟3周期）
        # 语法解析：数组切片实现多重延迟
        # 数学原理：jI[i] = I1[i-3], jQ[i] = Q1[i-3]
        jI = np.zeros(n)
        jQ = np.zeros(n)
        jI[6:] = I1[:-6]
        jQ[6:] = Q1[:-6]

        # 向量化同相和正交分量计算
        # 语法解析：数组逐元素运算
        # 数学原理：I2[i] = I1[i] - jQ[i], Q2[i] = Q1[i] + jI[i]
        I2 = I1 - jQ
        Q2 = Q1 + jI

        # 向量化Re和Im计算
        # 语法解析：数组移位 + 逐元素乘法
        # 数学原理：Re[i] = I2[i] * I2[i-1] + Q2[i] * Q2[i-1], Im[i] = I2[i] * Q2[i-1] - Q2[i] * I2[i-1]
        Re = np.zeros(n)
        Im = np.zeros(n)
        
        Re[1:] = I2[1:] * I2[:-1] + Q2[1:] * Q2[:-1]
        Im[1:] = I2[1:] * Q2[:-1] - Q2[1:] * I2[:-1]

        # 向量化相位角计算
        # 语法解析：np.arctan2(y, x) 计算反正切，np.degrees() 转换为角度
        # 数学原理：phase_angle = atan2(Im, Re) * (180/π)
        phase_angle = np.degrees(np.arctan2(Im, Re))

        # 确保相位角为正（向量化条件操作）
        # 语法解析：np.where(condition, x, y) 条件选择
        # 数学原理：phase_angle = phase_angle if phase_angle >= 0 else phase_angle + 360
        phase_angle = np.where(phase_angle < 0, phase_angle + 360, phase_angle)

        # 向量化周期计算
        # 语法解析：np.where() + 数组运算
        # 数学原理：period = 360 / phase_angle，但需要处理边界条件
        hilbert_period = np.where(
            phase_angle > 1,
            360 / phase_angle,
            10.0  # 默认周期
        )

        # 处理前几个无效值（向前填充）
        # 语法解析：np.maximum.accumulate() 累积最大值实现前向填充
        # 数学原理：用后续有效值填充前面的无效值
        valid_mask = phase_angle > 1
        if not valid_mask[0]:
            # 找到第一个有效值的位置
            first_valid_idx = np.argmax(valid_mask)
            if first_valid_idx > 0:
                hilbert_period[:first_valid_idx] = hilbert_period[first_valid_idx]

        dataframe['hilbert_period_raw'] = hilbert_period
        return dataframe

    def _calculate_adaptive_rsi(self, dataframe: DataFrame, period: pd.Series) -> pd.Series:
        """
        计算自适应周期 RSI

        使用动态周期计算 RSI，周期由希尔伯特变换确定。
        """
        close = dataframe['close'].values
        n = len(close)
        rsi_values = np.zeros(n)

        for i in range(1, n):
            # 获取当前周期（向下取整）
            current_period = max(2, int(period.iloc[i] / 2))

            # 计算变化
            changes = np.diff(close[max(0, i - current_period):i + 1])
            if len(changes) == 0:
                rsi_values[i] = 50
                continue

            gains = np.maximum(changes, 0)
            losses = np.maximum(-changes, 0)

            avg_gain = np.mean(gains) if len(gains) > 0 else 0
            avg_loss = np.mean(losses) if len(losses) > 0 else 0

            if avg_loss == 0:
                rsi_values[i] = 100
            elif avg_gain == 0:
                rsi_values[i] = 0
            else:
                rs = avg_gain / avg_loss
                rsi_values[i] = 100 - (100 / (1 + rs))

        return pd.Series(rsi_values, index=dataframe.index)

    def _hma(self, series: pd.Series, period: int) -> pd.Series:
        """
        计算 Hull Moving Average (HMA)

        HMA = WMA(2 * WMA(n/2) - WMA(n), sqrt(n))
        """
        half_period = int(period / 2)
        sqrt_period = int(np.sqrt(period))

        wma_half = series.rolling(window=half_period).apply(
            lambda x: np.sum(x * np.arange(1, len(x) + 1)) / np.sum(np.arange(1, len(x) + 1)),
            raw=True
        )
        wma_full = series.rolling(window=period).apply(
            lambda x: np.sum(x * np.arange(1, len(x) + 1)) / np.sum(np.arange(1, len(x) + 1)),
            raw=True
        )

        raw_hma = 2 * wma_half - wma_full

        hma = raw_hma.rolling(window=sqrt_period).apply(
            lambda x: np.sum(x * np.arange(1, len(x) + 1)) / np.sum(np.arange(1, len(x) + 1)),
            raw=True
        )

        return hma

    # ==========================================================================
    # 主要策略方法
    # ==========================================================================

    def informative_pairs(self):
        """定义额外的交易对/时间周期组合"""
        # 已经在装饰器中定义，这里可以返回空列表或根据需要补充
        return []

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        计算所有技术指标

        :param dataframe: 包含交易所数据的 DataFrame
        :param metadata: 附加信息，如当前交易对
        :return: 包含所有指标的 DataFrame
        """

        # ======================================================================
        # 1. 计算希尔伯特变换周期
        # ======================================================================
        dataframe = self._calculate_hilbert_period(dataframe)

        # 使用滚动中位数平滑周期
        dataframe['market_period'] = dataframe['hilbert_period_raw'].rolling(
            window=self.median_length.value
        ).median()

        # 填充 NaN 值
        dataframe['market_period'] = dataframe['market_period'].fillna(10)

        # ======================================================================
        # 2. 计算自适应 RSI
        # ======================================================================
        dataframe['adaptive_rsi_raw'] = self._calculate_adaptive_rsi(
            dataframe,
            dataframe['market_period']
        )

        # 可选 HMA 平滑
        if self.enable_smoothing.value:
            dataframe['adaptive_rsi'] = self._hma(
                dataframe['adaptive_rsi_raw'],
                self.smoothing_length.value
            )
        else:
            dataframe['adaptive_rsi'] = dataframe['adaptive_rsi_raw']

        # 填充 NaN 值
        dataframe['adaptive_rsi'] = dataframe['adaptive_rsi'].fillna(50)

        # RSI 阈值线（用于绘图）
        dataframe['rsi_oversold_line'] = self.rsi_oversold.value
        dataframe['rsi_overbought_line'] = self.rsi_overbought.value

        # ======================================================================
        # 3. 计算 Dual Channel Squeeze
        # ======================================================================

        # 布林带
        bb = qtpylib.bollinger_bands(
            qtpylib.typical_price(dataframe),
            window=self.bb_length.value,
            stds=self.bb_mult.value
        )
        dataframe['bb_upperband'] = bb['upper']
        dataframe['bb_lowerband'] = bb['lower']
        dataframe['bb_middleband'] = bb['mid']

        # 肯特纳通道
        dataframe['kc_basis'] = ta.EMA(dataframe, timeperiod=self.kc_length.value)
        dataframe['atr'] = ta.ATR(dataframe, timeperiod=self.kc_length.value)
        dataframe['kc_upperband'] = dataframe['kc_basis'] + self.kc_mult.value * dataframe['atr']
        dataframe['kc_lowerband'] = dataframe['kc_basis'] - self.kc_mult.value * dataframe['atr']

        # 挤压检测：BB 在 KC 内
        dataframe['is_squeeze'] = (
            (dataframe['bb_upperband'] < dataframe['kc_upperband']) &
            (dataframe['bb_lowerband'] > dataframe['kc_lowerband'])
        ).astype(int)

        # 挤压释放
        dataframe['squeeze_fired'] = (
            dataframe['is_squeeze'].shift(1) == 1
        ) & (dataframe['is_squeeze'] == 0)

        # ======================================================================
        # 4. 信号辅助指标
        # ======================================================================

        # RSI 方向
        dataframe['rsi_rising'] = dataframe['adaptive_rsi'] > dataframe['adaptive_rsi'].shift(1)
        dataframe['rsi_falling'] = dataframe['adaptive_rsi'] < dataframe['adaptive_rsi'].shift(1)

        # RSI 穿越超卖/超买
        dataframe['rsi_cross_above_oversold'] = qtpylib.crossed_above(
            dataframe['adaptive_rsi'],
            self.rsi_oversold.value
        )
        dataframe['rsi_cross_below_overbought'] = qtpylib.crossed_below(
            dataframe['adaptive_rsi'],
            self.rsi_overbought.value
        )

        # 超买超卖状态
        dataframe['in_oversold'] = dataframe['adaptive_rsi'] < self.rsi_oversold.value
        dataframe['in_overbought'] = dataframe['adaptive_rsi'] > self.rsi_overbought.value

        # 成交量过滤
        dataframe['volume_positive'] = dataframe['volume'] > 0

        # ======================================================================
        # 5. EMA200 趋势过滤器 (基于 4h Informative 数据)
        # ======================================================================
        # 获取 4h 数据
        informative_4h = self.dp.get_pair_dataframe(pair=metadata['pair'], timeframe='4h')
        
        # 计算 4h 趋势指标
        informative_4h['ema_trend'] = ta.EMA(informative_4h, timeperiod=self.trend_ema_period.value)
        
        # 合并 4h 数据到主数据框
        # merge_informative_pair 会自动添加 _4h 后缀 (例如 ema_trend_4h)
        dataframe = merge_informative_pair(dataframe, informative_4h, self.timeframe, '4h', ffill=True)
        
# 使用合并后的 4h EMA 进行趋势判断
        # 注意：合并列名为 'ema_trend_4h'
        if 'ema_trend_4h' in dataframe.columns:
            dataframe['trend_bullish'] = dataframe['close'] > dataframe['ema_trend_4h']
            dataframe['trend_bearish'] = dataframe['close'] < dataframe['ema_trend_4h']
        else:
            # 回退逻辑：如果合并失败（例如回测早期数据不足），使用本地计算作为临时替代
            # 但在生产环境应确保数据充足
            dataframe['ema_trend_local'] = ta.EMA(dataframe, timeperiod=self.trend_ema_period.value * 4) # 粗略模拟
            dataframe['trend_bullish'] = dataframe['close'] > dataframe['ema_trend_local']
            dataframe['trend_bearish'] = dataframe['close'] < dataframe['ema_trend_local']

        # ======================================================================
        # 6. Phase 2: 价格位置过滤器计算
        # ======================================================================
        if self.use_price_position_filter.value:
            # 计算指定周期内的最高价和最低价
            dataframe['price_position_high'] = dataframe['high'].rolling(
                window=self.price_position_period.value
            ).max()
            dataframe['price_position_low'] = dataframe['low'].rolling(
                window=self.price_position_period.value
            ).min()
            
            # 计算当前价格在高低点范围内的位置 (0-1之间)
            dataframe['price_position'] = (
                (dataframe['close'] - dataframe['price_position_low']) / 
                (dataframe['price_position_high'] - dataframe['price_position_low'])
            ).fillna(0.5)  # 如果无法计算，默认为中位数位置
            
            # 价格位置过滤器信号
            # 做多条件：价格处于相对低位 (低于阈值)
            dataframe['price_position_long_ok'] = (
                dataframe['price_position'] < self.price_position_low_threshold.value
            )
            
            # 做空条件：价格处于相对高位 (高于阈值)  
            dataframe['price_position_short_ok'] = (
                dataframe['price_position'] > self.price_position_high_threshold.value
            )
        else:
            # 如果未启用过滤器，默认允许所有交易
            dataframe['price_position_long_ok'] = True
            dataframe['price_position_short_ok'] = True
        
        # ======================================================================
        # 7. Phase 3: 市场波动性过滤器计算
        # ======================================================================
        if self.use_volatility_filter.value:
            # 计算ATR (Average True Range)
            dataframe['atr'] = ta.ATR(dataframe, timeperiod=self.volatility_atr_period.value)
            
            # 计算ATR百分比 (相对于收盘价的百分比)
            dataframe['atr_percent'] = (dataframe['atr'] / dataframe['close']) * 100
            
            # 波动性分类
            dataframe['volatility_regime'] = 'normal'
            dataframe.loc[dataframe['atr_percent'] < self.low_volatility_threshold.value, 'volatility_regime'] = 'low'
            dataframe.loc[dataframe['atr_percent'] > self.high_volatility_threshold.value, 'volatility_regime'] = 'high'
            
            # 市场环境判断 (基于价格和ATR的关系)
            # 使用ADX或类似指标判断趋势强度
            dataframe['adx'] = ta.ADX(dataframe, timeperiod=14)
            dataframe['trend_strength'] = 'weak'
            dataframe.loc[dataframe['adx'] > 25, 'trend_strength'] = 'strong'
            
            # 市场环境组合判断
            dataframe['market_environment'] = 'ranging'  # 默认震荡
            dataframe.loc[
                (dataframe['trend_strength'] == 'strong') & 
                (dataframe['volatility_regime'] != 'low'), 
                'market_environment'
            ] = 'trending'
            
            # 波动性过滤器信号
            # 低波动性：减少交易频率
            dataframe['volatility_filter_ok'] = (
                dataframe['volatility_regime'] != 'low'
            )
            
            # 高波动性：谨慎交易，需要更强的信号
            high_vol_extra_filter = (
                (dataframe['volatility_regime'] != 'high') |
                ((dataframe['rsi_cross_above_oversold'] | dataframe['rsi_cross_below_overbought']) &
                 (dataframe['volume'] > dataframe['volume'].rolling(20).mean() * 1.5))
            )
            dataframe['volatility_filter_ok'] = dataframe['volatility_filter_ok'] & high_vol_extra_filter
            
        else:
            # 如果未启用波动性过滤器，默认允许
            dataframe['volatility_filter_ok'] = True
            dataframe['market_environment'] = 'normal'
            dataframe['atr_percent'] = 1.0

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        基于指标生成入场信号 (v2: RSI + 均线测试)
        """
        
        # 基础条件：RSI 超卖/超买 + 成交量
        long_rsi_cond = (dataframe['adaptive_rsi'] < self.rsi_oversold.value) & dataframe['volume_positive']
        short_rsi_cond = (dataframe['adaptive_rsi'] > self.rsi_overbought.value) & dataframe['volume_positive']

        # 趋势过滤 (可选)
        if self.use_trend_filter.value:
            long_rsi_cond = long_rsi_cond & dataframe['trend_bullish']
            short_rsi_cond = short_rsi_cond & dataframe['trend_bearish']

        # 均线测试逻辑 (Confluence)
        # 定义测试范围：价格在均线 +/- tolerance 范围内，或者发生穿越
        tolerance = self.ema_test_tolerance.value

        for period in [21, 55, 100]:
            ema_col = f'ema{period}'
            
            # --- 做多入场 ---
            # 1. 价格触及均线 (Low <= EMA * (1+tol) AND Close >= EMA * (1-tol))
            #    这包含了回踩不破，或者短暂刺破后收回
            long_test = (
                (dataframe['low'] <= dataframe[ema_col] * (1 + tolerance)) &
                (dataframe['close'] >= dataframe[ema_col] * (1 - tolerance))
            )
            
            # 2. 或者发生向上穿越 (Crossover)
            long_cross = qtpylib.crossed_above(dataframe['close'], dataframe[ema_col])
            
            # 组合条件
            long_entry = long_rsi_cond & (long_test | long_cross)
            
            # Phase 2: 应用价格位置过滤器
            if self.use_price_position_filter.value:
                long_entry = long_entry & dataframe['price_position_long_ok']
            
            # Phase 3: 应用波动性过滤器
            if self.use_volatility_filter.value:
                long_entry = long_entry & dataframe['volatility_filter_ok']
            
            # 如果启用了挤压过滤器
            if self.use_squeeze_filter.value:
                long_entry = long_entry & (dataframe['is_squeeze'] == 1)

            dataframe.loc[long_entry, ['enter_long', 'enter_tag']] = (1, f'long_test_ema{period}')

            # --- 做空入场 ---
            # 1. 价格触及均线 (High >= EMA * (1-tol) AND Close <= EMA * (1+tol))
            short_test = (
                (dataframe['high'] >= dataframe[ema_col] * (1 - tolerance)) &
                (dataframe['close'] <= dataframe[ema_col] * (1 + tolerance))
            )
            
            # 2. 或者发生向下穿越 (Crossunder)
            short_cross = qtpylib.crossed_below(dataframe['close'], dataframe[ema_col])
            
            # 组合条件
            short_entry = short_rsi_cond & (short_test | short_cross)
            
            # Phase 2: 应用价格位置过滤器
            if self.use_price_position_filter.value:
                short_entry = short_entry & dataframe['price_position_short_ok']
            
            # Phase 3: 应用波动性过滤器
            if self.use_volatility_filter.value:
                short_entry = short_entry & dataframe['volatility_filter_ok']
            
            if self.use_squeeze_filter.value:
                short_entry = short_entry & (dataframe['is_squeeze'] == 1)

            dataframe.loc[short_entry, ['enter_short', 'enter_tag']] = (1, f'short_test_ema{period}')

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        基于指标生成出场信号

        :param dataframe: 包含指标的 DataFrame
        :param metadata: 附加信息
        :return: 包含出场信号的 DataFrame
        """

        # ======================================================================
        # 做多出场条件
        # ======================================================================
        # 信号：RSI 进入超买区或从超买区向下突破
        exit_long_conditions = (
            # RSI 从超买区向下突破
            (dataframe['adaptive_rsi'].shift(1) > self.rsi_overbought.value) &
            (dataframe['adaptive_rsi'] < dataframe['adaptive_rsi'].shift(1)) &
            (dataframe['volume_positive'])
        )

        dataframe.loc[
            exit_long_conditions,
            ['exit_long', 'exit_tag']
        ] = (1, 'rsi_overbought_exit')

        # ======================================================================
        # 做空出场条件
        # ======================================================================
        # 信号：RSI 进入超卖区或从超卖区向上突破
        exit_short_conditions = (
            # RSI 从超卖区向上突破
            (dataframe['adaptive_rsi'].shift(1) < self.rsi_oversold.value) &
            (dataframe['adaptive_rsi'] > dataframe['adaptive_rsi'].shift(1)) &
            (dataframe['volume_positive'])
        )

        dataframe.loc[
            exit_short_conditions,
            ['exit_short', 'exit_tag']
        ] = (1, 'rsi_oversold_exit')

        return dataframe

    def custom_exit(self, pair: str, trade: 'Trade', current_time: datetime, current_rate: float,
                    current_profit: float, **kwargs):
        """
        Phase 2: 自定义退出逻辑 (多重止盈 + 部分止盈机制)
        """
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        candle_date = timeframe_to_prev_date(self.timeframe, current_time)
        candle = dataframe.loc[dataframe['date'] == candle_date]
        
        if candle.empty:
            return None
            
        candle = candle.iloc[0]
        
        # Phase 2: 部分止盈状态管理
        trade_id = str(trade.id)
        
        # 初始化交易的部分止盈状态
        if trade_id not in self.trade_partial_tp_status:
            self.trade_partial_tp_status[trade_id] = {
                'tp1_done': False,
                'tp2_done': False
            }
        
        tp_status = self.trade_partial_tp_status[trade_id]
        
        # 如果未启用多重止盈，使用原有的EMA止盈逻辑
        if not self.use_multiple_take_profit.value:
            # 原有的EMA止盈逻辑
            if trade.is_short:
                ema55 = candle.get('ema55', 0)
                ema100 = candle.get('ema100', 0)
                if ema55 > 0 and current_rate <= ema55:
                    return 'ema55_tp'
                if ema100 > 0 and current_rate <= ema100:
                    return 'ema100_tp'
            else:
                ema55 = candle.get('ema55', 999999999)
                ema100 = candle.get('ema100', 999999999)
                if ema55 < 999999999 and current_rate >= ema55:
                    return 'ema55_tp'
                if ema100 < 999999999 and current_rate >= ema100:
                    return 'ema100_tp'
            return None
        
        # Phase 2: 部分止盈逻辑 (优先级高于完全止盈)
        if self.use_partial_take_profit.value:
            # 第一次部分止盈
            if not tp_status['tp1_done'] and current_profit >= self.partial_tp1_profit.value / 100:
                tp_status['tp1_done'] = True
                return f'partial_tp1_{self.partial_tp1_profit.value}%_{self.partial_tp1_ratio.value}'
            
            # 第二次部分止盈
            if not tp_status['tp2_done'] and current_profit >= self.partial_tp2_profit.value / 100:
                tp_status['tp2_done'] = True
                return f'partial_tp2_{self.partial_tp2_profit.value}%_{self.partial_tp2_ratio.value}'
        
        # Phase 2: 多重止盈逻辑 (在部分止盈完成后)
        # 获取交易已持续时间
        trade_duration = (current_time - trade.open_date_utc).total_seconds() / 3600  # 小时
        
        # Phase 3: 获取当前市场环境
        market_environment = candle.get('market_environment', 'normal')
        atr_percent = candle.get('atr_percent', 1.0)
        
        # Phase 3: 市场环境适应性止盈调整
        if self.use_adaptive_take_profit.value:
            if market_environment == 'trending':
                # 趋势市场：提高止盈目标，延长持仓时间
                tp1_adj = self.tp1_percentage.value * self.trend_tp_multiplier.value
                tp2_adj = self.tp2_percentage.value * self.trend_tp_multiplier.value
                tp3_activation_adj = self.tp3_trailing_activation.value * self.trend_tp_multiplier.value
                trailing_activation_adj = self.trend_trailing_activation.value
            elif market_environment == 'ranging':
                # 震荡市场：降低止盈目标，快速止盈
                tp1_adj = self.tp1_percentage.value * self.ranging_tp_multiplier.value
                tp2_adj = self.tp2_percentage.value * self.ranging_tp_multiplier.value
                tp3_activation_adj = self.tp3_trailing_activation.value * self.ranging_tp_multiplier.value
                trailing_activation_adj = self.ranging_trailing_activation.value
            else:
                # 正常市场：使用默认设置
                tp1_adj = self.tp1_percentage.value
                tp2_adj = self.tp2_percentage.value
                tp3_activation_adj = self.tp3_trailing_activation.value
                trailing_activation_adj = self.tp3_trailing_activation.value
        else:
            # 未启用适应性止盈，使用默认设置
            tp1_adj = self.tp1_percentage.value
            tp2_adj = self.tp2_percentage.value
            tp3_activation_adj = self.tp3_trailing_activation.value
            trailing_activation_adj = self.tp3_trailing_activation.value
        
        # 第一重止盈：快速止盈 (适用于短期获利)
        if current_profit >= tp1_adj / 100:
            # 如果交易时间很短(少于2小时)且达到第一重止盈目标，立即止盈
            if trade_duration < 2:
                return f'tp1_quick_{tp1_adj}%'
            
            # 如果价格出现快速反转迹象，也触发第一重止盈
            rsi_reversal = (
                (trade.is_short and candle.get('adaptive_rsi', 50) < 30) or
                (not trade.is_short and candle.get('adaptive_rsi', 50) > 70)
            )
            if rsi_reversal:
                return f'tp1_reversal_{tp1_adj}%'
        
        # 第二重止盈：中期止盈
        if current_profit >= tp2_adj / 100:
            # 结合EMA阻力/支撑位确认
            if trade.is_short:
                ema55 = candle.get('ema55', 0)
                ema100 = candle.get('ema100', 0)
                if (ema55 > 0 and current_rate <= ema55) or (ema100 > 0 and current_rate <= ema100):
                    return f'tp2_ema_support_{tp2_adj}%'
            else:
                ema55 = candle.get('ema55', 999999999)
                ema100 = candle.get('ema100', 999999999)
                if (ema55 < 999999999 and current_rate >= ema55) or (ema100 < 999999999 and current_rate >= ema100):
                    return f'tp2_ema_resistance_{tp2_adj}%'
        
        # 第三重止盈：移动止损 (长期持仓)
        if current_profit >= tp3_activation_adj / 100:
            # 检查是否触发移动止损条件
            if trade.is_short:
                # 做空移动止损：价格上涨超过追踪距离
                stop_loss_rate = trade.open_rate * (1 - current_profit + self.tp3_trailing_distance.value / 100)
                if current_rate >= stop_loss_rate:
                    return f'tp3_trailing_stop_{self.tp3_trailing_distance.value}%'
            else:
                # 做多移动止损：价格下跌超过追踪距离
                stop_loss_rate = trade.open_rate * (1 + current_profit - self.tp3_trailing_distance.value / 100)
                if current_rate <= stop_loss_rate:
                    return f'tp3_trailing_stop_{self.tp3_trailing_distance.value}%'
        
        # 额外的RSI反转止盈条件
        rsi_current = candle.get('adaptive_rsi', 50)
        
        if trade.is_short and current_profit > 0.005:  # 做空盈利超过0.5%
            # RSI进入超卖区，考虑止盈
            if rsi_current < 25:
                return 'rsi_oversold_exit'
                
        elif not trade.is_short and current_profit > 0.005:  # 做多盈利超过0.5%
            # RSI进入超买区，考虑止盈
            if rsi_current > 75:
                return 'rsi_overbought_exit'
        
        # Phase 3: 相关性止盈逻辑
        if self.use_correlation_exit.value and current_profit > self.correlation_profit_threshold.value / 100:
            # 获取当前所有开仓交易
            open_trades = self.wallets.get_open_trades()
            
            if len(open_trades) > 1:  # 有多个开仓交易时才考虑相关性
                # 计算相关交易对的盈利情况
                correlation_profits = []
                for other_trade in open_trades:
                    if other_trade.id != trade.id:  # 排除当前交易
                        # 检查是否为相关交易对
                        other_pair = other_trade.pair
                        if any(cor_pair in other_pair for cor_pair in self.correlation_pairs):
                            # 计算其他交易的当前盈利
                            other_profit = (other_trade.close_rate - other_trade.open_rate) / other_trade.open_rate
                            if not other_trade.is_short:
                                other_profit = -other_profit
                            correlation_profits.append(other_profit)
                
                # 相关性止盈条件
                if correlation_profits:
                    avg_correlation_profit = sum(correlation_profits) / len(correlation_profits)
                    
                    # 如果相关交易对平均盈利超过阈值，且当前交易也有不错盈利
                    if (avg_correlation_profit > self.correlation_avg_profit_threshold.value / 100 and 
                        current_profit > self.correlation_profit_threshold.value / 100):
                        return f'correlation_tp_avg_{avg_correlation_profit:.2%}'
                    
                    # 如果多个相关交易对都盈利，考虑部分止盈
                    profitable_correlations = sum(1 for p in correlation_profits if p > 0.01)
                    if profitable_correlations >= 2 and current_profit > 0.015:
                        return f'correlation_tp_multiple_{profitable_correlations}_pairs'
                
        return None
    
    def confirm_trade_entry(self, pair: str, order_type: str, amount: float,
                           rate: float, time_in_force: str, current_time: datetime,
                           entry_tag: Optional[str], side: str, **kwargs) -> bool:
        """
        Phase 2: 确认交易入场 (可用于部分止盈的仓位分配)
        """
        # 如果启用了部分止盈，这里可以调整初始仓位
        return True
    
    def trade_stopped(self, pair: str, trade: 'Trade'):
        """
        Phase 2: 交易停止时清理状态
        """
        # 清理交易的部分止盈状态
        trade_id = str(trade.id)
        if trade_id in self.trade_partial_tp_status:
            del self.trade_partial_tp_status[trade_id]

    def custom_stake_amount(self, pair: str, current_time: datetime, current_rate: float,
                          proposed_stake: float, min_stake: float, max_stake: float,
                          leverage: float, entry_tag: Optional[str], side: str,
                          **kwargs) -> float:
        
        # 如果没有 entry_tag，使用默认 stake
        if not entry_tag:
            return proposed_stake

        # 解析 entry_tag 获取测试的 EMA 周期
        # tag 格式: long_test_ema21
        try:
            ema_period = int(entry_tag.split('ema')[-1])
            ema_col = f'ema{ema_period}'
        except (ValueError, IndexError):
            return proposed_stake

        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        candle_date = timeframe_to_prev_date(self.timeframe, current_time)
        candle = dataframe.loc[dataframe['date'] == candle_date]
        
        if candle.empty:
            return proposed_stake
            
        candle = candle.iloc[0]
        ema_price = candle[ema_col]
        
        # 计算止损距离
        if side == "short":
             # 做空：止损在上方 (EMA)
             if ema_price < current_rate: 
                 sl_dist = 0.10 # 异常情况
             else:
                 sl_dist = (ema_price - current_rate) / current_rate
        else:
             # 做多：止损在下方 (EMA)
             if ema_price > current_rate:
                 sl_dist = 0.10
             else:
                 sl_dist = (current_rate - ema_price) / current_rate
                 
        # 加上缓冲
        sl_dist += self.sl_buffer.value
        
        # 风险资本
        total_capital = self.wallets.get_total_stake_amount()
        risk_capital = total_capital * self.risk_per_trade.value
        
        if sl_dist == 0:
            return proposed_stake
            
        stake = risk_capital / sl_dist
        
        return min(stake, max_stake, self.wallets.get_available_stake_amount())

    def custom_stoploss(self, pair: str, trade: 'Trade', current_time: datetime,
                      current_rate: float, current_profit: float, **kwargs) -> float:
        
        # 使用 entry_tag 确定止损基准
        if not trade.enter_tag:
            return self.stoploss
            
        try:
            ema_period = int(trade.enter_tag.split('ema')[-1])
            ema_col = f'ema{ema_period}'
        except (ValueError, IndexError):
            return self.stoploss

        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        candle_date = timeframe_to_prev_date(self.timeframe, trade.open_date_utc)
        candle = dataframe.loc[dataframe['date'] == candle_date]
        
        if candle.empty:
            return self.stoploss
            
        candle = candle.iloc[0]
        ema_price = candle[ema_col]
        open_rate = trade.open_rate
        
        if trade.is_short:
            if ema_price < open_rate:
                return -0.10 
            sl_dist = (ema_price - open_rate) / open_rate
        else:
            if ema_price > open_rate:
                return -0.10
            sl_dist = (open_rate - ema_price) / open_rate
            
        return -(sl_dist + self.sl_buffer.value)
