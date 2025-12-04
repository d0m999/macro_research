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
)

# --------------------------------
# Add your lib to import here
import talib.abstract as ta
from technical import qtpylib
from freqtrade.exchange import timeframe_to_prev_date

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

    # 时间周期
    timeframe = '4h'

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
    stoploss_ema = CategoricalParameter(['ema21', 'ema55', 'ema100', 'ema200'], default='ema100', space="buy", optimize=True)

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
        计算希尔伯特变换周期

        使用希尔伯特变换从价格数据中提取主导周期。
        """
        close = dataframe['close'].values
        n = len(close)

        # 初始化数组
        price_smooth = np.zeros(n)
        detrender = np.zeros(n)
        I1 = np.zeros(n)
        Q1 = np.zeros(n)
        I2 = np.zeros(n)
        Q2 = np.zeros(n)
        Re = np.zeros(n)
        Im = np.zeros(n)
        phase_angle = np.zeros(n)
        hilbert_period = np.zeros(n)

        # 常量
        pi = np.pi

        for i in range(6, n):
            # 4 周期价格平滑
            price_smooth[i] = (close[i] + close[i-1] + close[i-2] + close[i-3]) / 4

            # 去趋势处理
            detrender[i] = (0.0962 * price_smooth[i]
                           + 0.5769 * price_smooth[i-2]
                           - 0.5769 * price_smooth[i-4]
                           - 0.0962 * price_smooth[i-6])

            # 希尔伯特变换 - I1
            I1[i] = detrender[i-3]

            # 希尔伯特变换 - Q1
            Q1[i] = (0.0962 * detrender[i]
                    + 0.5769 * detrender[i-2]
                    - 0.5769 * detrender[i-4]
                    - 0.0962 * detrender[i-6])

            # jI 和 jQ（延迟 3 周期）
            jI = I1[i-3] if i >= 9 else 0
            jQ = Q1[i-3] if i >= 9 else 0

            # 同相和正交分量
            I2[i] = I1[i] - jQ
            Q2[i] = Q1[i] + jI

            # Re 和 Im
            Re[i] = I2[i] * I2[i-1] + Q2[i] * Q2[i-1] if i > 0 else 0
            Im[i] = I2[i] * Q2[i-1] - Q2[i] * I2[i-1] if i > 0 else 0

            # 相位角计算
            if Re[i] != 0:
                phase_angle[i] = np.degrees(np.arctan2(Im[i], Re[i]))
            else:
                phase_angle[i] = 0

            # 确保相位角为正
            if phase_angle[i] < 0:
                phase_angle[i] += 360

            # 计算周期
            if phase_angle[i] > 1:
                hilbert_period[i] = 360 / phase_angle[i]
            else:
                hilbert_period[i] = hilbert_period[i-1] if i > 0 else 10

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
        # 5. EMA200 趋势过滤器（新增）
        # ======================================================================
        dataframe['ema_trend'] = ta.EMA(dataframe, timeperiod=self.trend_ema_period.value)
        dataframe['trend_bullish'] = dataframe['close'] > dataframe['ema_trend']
        dataframe['trend_bearish'] = dataframe['close'] < dataframe['ema_trend']

        # ======================================================================
        # 6. 动态止损 EMA（新增）
        # ======================================================================
        for period in [21, 55, 100, 200]:
            dataframe[f'ema{period}'] = ta.EMA(dataframe, timeperiod=period)

        return dataframe


    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        基于指标生成入场信号

        :param dataframe: 包含指标的 DataFrame
        :param metadata: 附加信息
        :return: 包含入场信号的 DataFrame
        """

        # ======================================================================
        # 做多入场条件
        # ======================================================================
        # 信号：RSI 从超卖区向上突破
        long_conditions = (
            # RSI 前一根蜡烛在超卖区
            (dataframe['adaptive_rsi'].shift(1) < self.rsi_oversold.value) &
            # RSI 当前向上突破超卖区
            (dataframe['adaptive_rsi'] > dataframe['adaptive_rsi'].shift(1)) &
            # 成交量存在
            (dataframe['volume_positive'])
        )

        # 可选：挤压过滤器
        if self.use_squeeze_filter.value:
            long_conditions = long_conditions & (
                dataframe['is_squeeze'] == 1
            )

        # 可选：EMA200 趋势过滤器（只在趋势向上时做多）
        if self.use_trend_filter.value:
            long_conditions = long_conditions & dataframe['trend_bullish']

        dataframe.loc[
            long_conditions,
            ['enter_long', 'enter_tag']
        ] = (1, 'rsi_oversold_bounce')

        # ======================================================================
        # 做空入场条件
        # ======================================================================
        # 信号：RSI 从超买区向下突破
        short_conditions = (
            # RSI 前一根蜡烛在超买区
            (dataframe['adaptive_rsi'].shift(1) > self.rsi_overbought.value) &
            # RSI 当前向下突破超买区
            (dataframe['adaptive_rsi'] < dataframe['adaptive_rsi'].shift(1)) &
            # 成交量存在
            (dataframe['volume_positive'])
        )

        # 可选：挤压过滤器
        if self.use_squeeze_filter.value:
            short_conditions = short_conditions & (
                dataframe['is_squeeze'] == 1
            )

        # 可选：EMA200 趋势过滤器（只在趋势向下时做空）
        if self.use_trend_filter.value:
            short_conditions = short_conditions & dataframe['trend_bearish']

        dataframe.loc[
            short_conditions,
            ['enter_short', 'enter_tag']
        ] = (1, 'rsi_overbought_drop')

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

    def custom_stake_amount(self, pair: str, current_time: datetime, current_rate: float,
                          proposed_stake: float, min_stake: float, max_stake: float,
                          leverage: float, entry_tag: Optional[str], side: str,
                          **kwargs) -> float:
        return proposed_stake
        
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        # ... (rest of the code is unreachable)

    def custom_stoploss(self, pair: str, trade: 'Trade', current_time: datetime,
                      current_rate: float, current_profit: float, **kwargs) -> float:
        return self.stoploss
        
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        # ... (rest of the code is unreachable)
        candle_date = timeframe_to_prev_date(self.timeframe, current_time)
        candle = dataframe.loc[dataframe['date'] == candle_date]
        
        if candle.empty:
            return proposed_stake
            
        candle = candle.iloc[0]
        ema_col = self.stoploss_ema.value
        ema_price = candle[ema_col]
        
        # 计算止损距离
        if side == "short":
             # 做空：止损在上方
             if ema_price < current_rate: # 均线在下方，无效
                 sl_dist = 0.10
             else:
                 sl_dist = (ema_price - current_rate) / current_rate
        else:
             # 做多：止损在下方
             if ema_price > current_rate: # 均线在上方，无效
                 sl_dist = 0.10
             else:
                 sl_dist = (current_rate - ema_price) / current_rate
                 
        # 加上 0.5% 缓冲
        sl_dist += 0.005
        
        # 风险资本
        total_capital = self.wallets.get_total_stake_amount()
        risk_capital = total_capital * self.risk_per_trade.value
        
        # 计算仓位
        # Stake = Risk / Stoploss%
        if sl_dist == 0:
            return proposed_stake
            
        stake = risk_capital / sl_dist
        
        return min(stake, max_stake, self.wallets.get_available_stake_amount())

    def custom_stoploss(self, pair: str, trade: 'Trade', current_time: datetime,
                      current_rate: float, current_profit: float, **kwargs) -> float:
        
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        candle_date = timeframe_to_prev_date(self.timeframe, trade.open_date_utc)
        candle = dataframe.loc[dataframe['date'] == candle_date]
        
        if candle.empty:
            return self.stoploss
            
        candle = candle.iloc[0]
        ema_col = self.stoploss_ema.value
        ema_price = candle[ema_col]
        open_rate = trade.open_rate
        
        if trade.is_short:
            if ema_price < open_rate:
                return -0.10 # 默认 10%
            sl_dist = (ema_price - open_rate) / open_rate
        else:
            if ema_price > open_rate:
                return -0.10
            sl_dist = (open_rate - ema_price) / open_rate
            
        # 返回负数表示亏损百分比
        return -(sl_dist + 0.005)
