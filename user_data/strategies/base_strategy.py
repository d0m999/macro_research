"""
基础策略类 - 为所有策略提供统一的架构和最佳实践

遵循资深量化交易员的架构设计原则：
1. 模块化设计
2. 完整的风险管理
3. 详细的日志记录
4. 性能优化
5. 错误处理机制
"""

import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
from freqtrade.strategy import IStrategy, merge_informative_pair
from freqtrade.persistence import Trade
import freqtrade.vendor.qtpylib.indicators as qtpylib

# 导入自定义组件
from .components.indicators.adaptive_resonance import AdaptiveResonanceOscillator
from .components.indicators.atr_zigzag import ATRZigZag

class BaseStrategy(IStrategy):
    """
    基础策略类
    
    提供标准化的策略架构和最佳实践实现
    所有具体策略都应该继承此类
    """
    
    # 基础配置
    INTERFACE_VERSION = 3
    can_short = True
    
    # 时间框架设置
    timeframe = '5m'
    
    # 风险管理参数
    stoploss = -0.05  # 5%止损
    
    # ROI设置（可被子类覆盖）
    minimal_roi = {
        "0": 0.10,    # 10%立即退出
        "40": 0.05,   # 40分钟后5%
        "100": 0.02,  # 100分钟后2%
        "240": 0.01   # 240分钟后1%
    }
    
    # 启动蜡烛数量（确保指标有足够数据）
    startup_candle_count: int = 200
    
    # 自定义功能开关
    use_custom_stoploss = True
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False
    
    def __init__(self, config: dict):
        """
        初始化基础策略
        
        Args:
            config: Freqtrade配置字典
        """
        super().__init__(config)
        
        # 设置日志
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(f"初始化策略: {self.__class__.__name__}")
        
        # 初始化自定义指标
        self._init_indicators()
        
        # 策略状态跟踪
        self.strategy_state = {
            'last_analysis_time': None,
            'market_condition': 'unknown',
            'risk_level': 'normal'
        }
        
        # 性能统计
        self.performance_stats = {
            'total_signals': 0,
            'successful_trades': 0,
            'failed_trades': 0
        }
    
    def _init_indicators(self):
        """
        初始化自定义指标实例
        子类可以覆盖此方法来添加更多指标
        """
        # 初始化ARO指标
        self.aro = AdaptiveResonanceOscillator({
            'smooth': True,
            'smooth_length': 12,
            'use_volume': False
        })
        
        # 初始化ATR ZigZag指标
        self.atr_zigzag = ATRZigZag({
            'atr_length': 14,
            'pivot_length': 5,
            'atr_multiplier': 2.0
        })
        
        self.logger.info("自定义指标初始化完成")
    
    def informative_pairs(self):
        """
        定义信息对
        获取更高时间框架的数据用于确认信号
        """
        pairs = self.dp.current_whitelist()
        informative_pairs = []
        
        # 添加1小时时间框架的数据
        for pair in pairs:
            informative_pairs.append((pair, '1h'))
        
        # 添加BTC作为市场情绪指标
        informative_pairs.append(('BTC/USDT', '1h'))
        
        return informative_pairs
    
    def populate_indicators(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        """
        计算所有技术指标
        
        这是策略的核心方法，所有指标计算都在这里完成
        """
        try:
            self.logger.debug(f"开始计算指标，交易对: {metadata['pair']}")
            
            # 1. 基础技术指标
            dataframe = self._populate_basic_indicators(dataframe)
            
            # 2. 自定义指标
            dataframe = self._populate_custom_indicators(dataframe, metadata)
            
            # 3. 信息对数据
            dataframe = self._populate_informative_indicators(dataframe, metadata)
            
            # 4. 市场状态分析
            dataframe = self._analyze_market_condition(dataframe)
            
            self.logger.debug(f"指标计算完成，交易对: {metadata['pair']}")
            return dataframe
            
        except Exception as e:
            self.logger.error(f"指标计算失败: {str(e)}")
            return dataframe
    
    def _populate_basic_indicators(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        计算基础技术指标
        """
        # 移动平均线
        dataframe['ema_12'] = qtpylib.ema(dataframe['close'], 12)
        dataframe['ema_26'] = qtpylib.ema(dataframe['close'], 26)
        dataframe['sma_50'] = qtpylib.sma(dataframe['close'], 50)
        dataframe['sma_200'] = qtpylib.sma(dataframe['close'], 200)
        
        # MACD
        macd = qtpylib.macd(dataframe['close'])
        dataframe['macd'] = macd['macd']
        dataframe['macdsignal'] = macd['macdsignal']
        dataframe['macdhist'] = macd['macdhist']
        
        # RSI
        dataframe['rsi'] = qtpylib.rsi(dataframe['close'], 14)
        
        # 布林带
        bollinger = qtpylib.bollinger_bands(dataframe['close'], window=20, stds=2)
        dataframe['bb_lower'] = bollinger['lower']
        dataframe['bb_middle'] = bollinger['mid']
        dataframe['bb_upper'] = bollinger['upper']
        
        # ATR
        dataframe['atr'] = qtpylib.atr(dataframe, 14)
        
        # 成交量指标
        dataframe['volume_sma'] = qtpylib.sma(dataframe['volume'], 20)
        dataframe['volume_ratio'] = dataframe['volume'] / dataframe['volume_sma']
        
        return dataframe
    
    def _populate_custom_indicators(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        """
        计算自定义指标
        """
        # 计算ARO指标
        dataframe = self.aro.safe_calculate(dataframe)
        
        # 计算ATR ZigZag指标
        dataframe = self.atr_zigzag.safe_calculate(dataframe)
        
        return dataframe
    
    def _populate_informative_indicators(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        """
        处理信息对数据
        """
        if not self.dp:
            return dataframe
        
        # 获取1小时数据
        informative_1h = self.dp.get_pair_dataframe(pair=metadata['pair'], timeframe='1h')
        
        if not informative_1h.empty:
            # 计算1小时RSI
            informative_1h['rsi_1h'] = qtpylib.rsi(informative_1h['close'], 14)
            
            # 计算1小时趋势
            informative_1h['trend_1h'] = np.where(
                informative_1h['close'] > qtpylib.sma(informative_1h['close'], 50), 1, -1
            )
            
            # 合并信息对数据
            dataframe = merge_informative_pair(dataframe, informative_1h, self.timeframe, '1h', ffill=True)
        
        # 获取BTC数据作为市场情绪指标
        btc_informative = self.dp.get_pair_dataframe(pair='BTC/USDT', timeframe='1h')
        if not btc_informative.empty:
            btc_informative['btc_rsi_1h'] = qtpylib.rsi(btc_informative['close'], 14)
            btc_informative['btc_trend_1h'] = np.where(
                btc_informative['close'] > qtpylib.sma(btc_informative['close'], 50), 1, -1
            )
            
            # 重命名列以避免冲突
            btc_informative = btc_informative[['date', 'btc_rsi_1h', 'btc_trend_1h']].copy()
            btc_informative.columns = ['date_1h', 'btc_rsi_1h', 'btc_trend_1h']
            
            dataframe = pd.merge(dataframe, btc_informative, left_on='date', right_on='date_1h', how='left')
            dataframe = dataframe.ffill()
        
        return dataframe
    
    def _analyze_market_condition(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        分析市场状态
        """
        # 趋势强度
        dataframe['trend_strength'] = abs(dataframe['ema_12'] - dataframe['ema_26']) / dataframe['atr']
        
        # 波动性状态
        dataframe['volatility_state'] = np.where(
            dataframe['atr'] > dataframe['atr'].rolling(50).mean() * 1.5, 'high',
            np.where(dataframe['atr'] < dataframe['atr'].rolling(50).mean() * 0.5, 'low', 'normal')
        )
        
        # 市场情绪（基于多个指标）
        sentiment_score = 0
        
        # RSI贡献
        sentiment_score += np.where(dataframe['rsi'] > 70, -1, 
                                  np.where(dataframe['rsi'] < 30, 1, 0))
        
        # MACD贡献
        sentiment_score += np.where(dataframe['macd'] > dataframe['macdsignal'], 1, -1)
        
        # 价格相对于移动平均线的位置
        sentiment_score += np.where(dataframe['close'] > dataframe['sma_50'], 1, -1)
        
        dataframe['market_sentiment'] = sentiment_score
        
        return dataframe
    
    def populate_entry_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        """
        定义入场信号
        子类应该覆盖此方法来实现具体的入场逻辑
        """
        # 默认实现：基于ARO和ZigZag的简单策略
        
        # 多头入场条件
        long_conditions = [
            dataframe['aro_rsi'] < 30,  # ARO超卖
            dataframe['aro_strong_bullish'],  # ARO强烈看涨信号
            dataframe['close'] > dataframe['ema_12'],  # 价格在短期均线上方
            dataframe['volume_ratio'] > 1.2,  # 成交量放大
        ]
        
        # 空头入场条件
        short_conditions = [
            dataframe['aro_rsi'] > 70,  # ARO超买
            dataframe['aro_strong_bearish'],  # ARO强烈看跌信号
            dataframe['close'] < dataframe['ema_12'],  # 价格在短期均线下方
            dataframe['volume_ratio'] > 1.2,  # 成交量放大
        ]
        
        # 应用条件
        dataframe.loc[
            qtpylib.crossed_above(dataframe['aro_rsi'], 30) & 
            reduce(lambda x, y: x & y, long_conditions),
            ['enter_long', 'enter_tag']
        ] = (1, 'aro_long')
        
        dataframe.loc[
            qtpylib.crossed_below(dataframe['aro_rsi'], 70) & 
            reduce(lambda x, y: x & y, short_conditions),
            ['enter_short', 'enter_tag']
        ] = (1, 'aro_short')
        
        return dataframe
    
    def populate_exit_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        """
        定义出场信号
        """
        # 多头出场条件
        dataframe.loc[
            (dataframe['aro_rsi'] > 70) |  # ARO超买
            (dataframe['aro_strong_bearish']),  # ARO强烈看跌信号
            ['exit_long', 'exit_tag']
        ] = (1, 'aro_exit_long')
        
        # 空头出场条件
        dataframe.loc[
            (dataframe['aro_rsi'] < 30) |  # ARO超卖
            (dataframe['aro_strong_bullish']),  # ARO强烈看涨信号
            ['exit_short', 'exit_tag']
        ] = (1, 'aro_exit_short')
        
        return dataframe
    
    def custom_stoploss(self, pair: str, trade: Trade, current_time: datetime,
                       current_rate: float, current_profit: float, after_fill: bool,
                       **kwargs) -> float:
        """
        自定义止损逻辑
        基于ATR的动态止损
        """
        try:
            # 获取当前数据
            dataframe, _ = self.dp.get_analyzed_dataframe(pair=pair, timeframe=self.timeframe)
            if dataframe.empty:
                return self.stoploss
            
            current_candle = dataframe.iloc[-1]
            atr_value = current_candle['atr']
            
            if pd.isna(atr_value):
                return self.stoploss
            
            # 基于ATR的动态止损
            atr_multiplier = 2.0
            
            if trade.is_short:
                # 空头交易：止损在入场价格上方
                stop_distance = atr_value * atr_multiplier / current_rate
                return stop_distance
            else:
                # 多头交易：止损在入场价格下方
                stop_distance = -(atr_value * atr_multiplier / current_rate)
                return max(stop_distance, self.stoploss)  # 不能超过最大止损
                
        except Exception as e:
            self.logger.error(f"自定义止损计算失败: {str(e)}")
            return self.stoploss
    
    def custom_exit(self, pair: str, trade: Trade, current_time: datetime, 
                   current_rate: float, current_profit: float, **kwargs):
        """
        自定义出场逻辑
        """
        try:
            # 获取当前数据
            dataframe, _ = self.dp.get_analyzed_dataframe(pair=pair, timeframe=self.timeframe)
            if dataframe.empty:
                return False, None
            
            current_candle = dataframe.iloc[-1]
            
            # 基于ARO信号的出场
            if trade.is_short:
                if current_candle['aro_strong_bullish']:
                    return True, 'aro_reversal'
            else:
                if current_candle['aro_strong_bearish']:
                    return True, 'aro_reversal'
            
            # 基于时间的出场（防止长时间持仓）
            if current_time - trade.open_date_utc > timedelta(hours=24):
                return True, 'time_exit'
            
            return False, None
            
        except Exception as e:
            self.logger.error(f"自定义出场逻辑失败: {str(e)}")
            return False, None
    
    def leverage(self, pair: str, current_time: datetime, current_rate: float,
                proposed_leverage: float, max_leverage: float, entry_tag: str,
                side: str, **kwargs) -> float:
        """
        动态杠杆管理
        基于市场波动性调整杠杆
        """
        try:
            # 获取当前数据
            dataframe, _ = self.dp.get_analyzed_dataframe(pair=pair, timeframe=self.timeframe)
            if dataframe.empty:
                return 1.0
            
            current_candle = dataframe.iloc[-1]
            volatility_state = current_candle.get('volatility_state', 'normal')
            
            # 根据波动性调整杠杆
            if volatility_state == 'high':
                return min(2.0, max_leverage)  # 高波动时降低杠杆
            elif volatility_state == 'low':
                return min(5.0, max_leverage)  # 低波动时可以适当提高杠杆
            else:
                return min(3.0, max_leverage)  # 正常波动时使用中等杠杆
                
        except Exception as e:
            self.logger.error(f"杠杆计算失败: {str(e)}")
            return 1.0
    
    def confirm_trade_entry(self, pair: str, order_type: str, amount: float,
                           rate: float, time_in_force: str, current_time: datetime,
                           entry_tag: str, side: str, **kwargs) -> bool:
        """
        交易确认
        在实际下单前进行最后检查
        """
        try:
            # 检查市场状态
            dataframe, _ = self.dp.get_analyzed_dataframe(pair=pair, timeframe=self.timeframe)
            if dataframe.empty:
                return False
            
            current_candle = dataframe.iloc[-1]
            
            # 检查波动性是否过高
            if current_candle.get('volatility_state') == 'high':
                self.logger.warning(f"市场波动性过高，跳过交易: {pair}")
                return False
            
            # 检查成交量
            if current_candle['volume_ratio'] < 0.5:
                self.logger.warning(f"成交量过低，跳过交易: {pair}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"交易确认失败: {str(e)}")
            return False