"""
高级量化策略实现
基于ARO和ATR ZigZag指标的多时间框架策略

策略特点：
1. 多时间框架确认
2. 动态风险管理
3. 智能仓位管理
4. 完整的信号过滤系统
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from functools import reduce
import freqtrade.vendor.qtpylib.indicators as qtpylib

from .base_strategy import BaseStrategy

class MyAdvancedStrategy(BaseStrategy):
    """
    高级量化策略
    
    结合ARO自适应共振振荡器和ATR ZigZag的多维度分析策略
    """
    
    # 策略元信息
    INTERFACE_VERSION = 3
    
    # 基础参数
    timeframe = '5m'
    can_short = True
    
    # 风险管理参数
    stoploss = -0.03  # 3%基础止损
    
    # 动态ROI设置
    minimal_roi = {
        "0": 0.08,    # 8%立即获利
        "30": 0.04,   # 30分钟后4%
        "60": 0.02,   # 60分钟后2%
        "120": 0.01,  # 120分钟后1%
        "240": 0.005  # 240分钟后0.5%
    }
    
    # 启动蜡烛数量
    startup_candle_count: int = 300
    
    # 自定义功能
    use_custom_stoploss = True
    use_custom_roi = True
    use_exit_signal = True
    exit_profit_only = False
    
    # 策略特定参数
    strategy_params = {
        # ARO参数
        'aro_oversold': 25,
        'aro_overbought': 75,
        'aro_strong_threshold': 15,  # 强信号阈值
        
        # 趋势确认参数
        'trend_confirmation_period': 20,
        'volume_threshold': 1.5,
        
        # 风险管理参数
        'max_open_trades': 3,
        'risk_per_trade': 0.02,  # 每笔交易2%风险
        
        # 时间过滤
        'avoid_weekend_close': True,
        'max_trade_duration_hours': 48,
    }
    
    def __init__(self, config: dict):
        """初始化高级策略"""
        super().__init__(config)
        
        # 策略状态跟踪
        self.trade_history = []
        self.market_regime = 'unknown'  # trending, ranging, volatile
        
        self.logger.info("高级量化策略初始化完成")
    
    def _init_indicators(self):
        """初始化策略专用指标"""
        super()._init_indicators()
        
        # 优化ARO参数
        self.aro = self.aro.__class__({
            'smooth': True,
            'smooth_length': 10,
            'median_length': 80,
            'use_volume': True,  # 启用成交量加权
            'bb_length': 20,
            'kc_length': 20,
            'momentum_length': 10
        })
        
        # 优化ZigZag参数
        self.atr_zigzag = self.atr_zigzag.__class__({
            'atr_length': 10,
            'pivot_length': 3,
            'atr_multiplier': 1.8,
            'avg_length_period': 5
        })
        
        self.logger.info("策略专用指标初始化完成")
    
    def populate_indicators(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        """计算所有指标"""
        dataframe = super().populate_indicators(dataframe, metadata)
        
        # 添加策略特定指标
        dataframe = self._add_advanced_indicators(dataframe)
        
        # 市场状态识别
        dataframe = self._identify_market_regime(dataframe)
        
        # 信号强度计算
        dataframe = self._calculate_signal_strength(dataframe)
        
        return dataframe
    
    def _add_advanced_indicators(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """添加高级技术指标"""
        
        # 多时间框架RSI
        dataframe['rsi_fast'] = qtpylib.rsi(dataframe['close'], 7)
        dataframe['rsi_slow'] = qtpylib.rsi(dataframe['close'], 21)
        
        # 价格动量
        dataframe['momentum_5'] = (dataframe['close'] / dataframe['close'].shift(5) - 1) * 100
        dataframe['momentum_10'] = (dataframe['close'] / dataframe['close'].shift(10) - 1) * 100
        
        # 波动率指标
        dataframe['volatility_ratio'] = dataframe['atr'] / dataframe['atr'].rolling(50).mean()
        
        # 成交量分析
        dataframe['volume_profile'] = dataframe['volume'].rolling(20).rank(pct=True)
        dataframe['volume_momentum'] = dataframe['volume'] / dataframe['volume'].rolling(10).mean()
        
        # 价格位置指标
        dataframe['price_position'] = (dataframe['close'] - dataframe['low'].rolling(20).min()) / \
                                    (dataframe['high'].rolling(20).max() - dataframe['low'].rolling(20).min())
        
        # 趋势强度
        dataframe['trend_strength'] = abs(dataframe['ema_12'] - dataframe['ema_26']) / dataframe['atr']
        
        return dataframe
    
    def _identify_market_regime(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """识别市场状态"""
        
        # 趋势性市场识别
        trend_score = 0
        
        # EMA排列
        ema_alignment = np.where(
            (dataframe['ema_12'] > dataframe['ema_26']) & 
            (dataframe['ema_26'] > dataframe['sma_50']), 1,
            np.where(
                (dataframe['ema_12'] < dataframe['ema_26']) & 
                (dataframe['ema_26'] < dataframe['sma_50']), -1, 0
            )
        )
        trend_score += ema_alignment
        
        # ADX趋势强度（简化版本）
        adx_proxy = dataframe['trend_strength'].rolling(14).mean()
        trend_score += np.where(adx_proxy > adx_proxy.rolling(50).mean(), 1, -1)
        
        # ZigZag趋势确认
        zigzag_trend = np.where(dataframe['zigzag_direction'] == 1, 1,
                               np.where(dataframe['zigzag_direction'] == -1, -1, 0))
        trend_score += zigzag_trend
        
        # 市场状态分类
        dataframe['market_regime'] = np.where(
            trend_score >= 2, 'trending_up',
            np.where(trend_score <= -2, 'trending_down',
                    np.where(dataframe['volatility_ratio'] > 1.5, 'volatile', 'ranging'))
        )
        
        return dataframe
    
    def _calculate_signal_strength(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """计算综合信号强度"""
        
        # 初始化信号强度
        dataframe['long_signal_strength'] = 0
        dataframe['short_signal_strength'] = 0
        
        # ARO信号贡献
        dataframe['long_signal_strength'] += np.where(
            dataframe['aro_rsi'] < self.strategy_params['aro_oversold'], 2,
            np.where(dataframe['aro_strong_bullish'], 3, 0)
        )
        
        dataframe['short_signal_strength'] += np.where(
            dataframe['aro_rsi'] > self.strategy_params['aro_overbought'], 2,
            np.where(dataframe['aro_strong_bearish'], 3, 0)
        )
        
        # 背离信号贡献
        dataframe['long_signal_strength'] += np.where(dataframe['bullish_divergence'], 2, 0)
        dataframe['short_signal_strength'] += np.where(dataframe['bearish_divergence'], 2, 0)
        
        # 挤压突破贡献
        dataframe['long_signal_strength'] += np.where(dataframe['squeeze_bullish'], 1, 0)
        dataframe['short_signal_strength'] += np.where(dataframe['squeeze_bearish'], 1, 0)
        
        # 趋势确认贡献
        dataframe['long_signal_strength'] += np.where(
            (dataframe['market_regime'] == 'trending_up') & 
            (dataframe['close'] > dataframe['ema_12']), 1, 0
        )
        
        dataframe['short_signal_strength'] += np.where(
            (dataframe['market_regime'] == 'trending_down') & 
            (dataframe['close'] < dataframe['ema_12']), 1, 0
        )
        
        # 成交量确认
        volume_confirmation = dataframe['volume_momentum'] > self.strategy_params['volume_threshold']
        dataframe['long_signal_strength'] += np.where(volume_confirmation, 1, 0)
        dataframe['short_signal_strength'] += np.where(volume_confirmation, 1, 0)
        
        # 多时间框架确认
        if 'rsi_1h' in dataframe.columns:
            dataframe['long_signal_strength'] += np.where(
                (dataframe['rsi_1h'] < 60) & (dataframe['trend_1h'] == 1), 1, 0
            )
            dataframe['short_signal_strength'] += np.where(
                (dataframe['rsi_1h'] > 40) & (dataframe['trend_1h'] == -1), 1, 0
            )
        
        return dataframe
    
    def populate_entry_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        """定义入场信号"""
        
        # 多头入场条件
        long_conditions = [
            # 主要信号：ARO超卖反弹
            qtpylib.crossed_above(dataframe['aro_rsi'], self.strategy_params['aro_oversold']),
            
            # 信号强度确认
            dataframe['long_signal_strength'] >= 4,
            
            # 趋势过滤
            dataframe['market_regime'].isin(['trending_up', 'ranging']),
            
            # 价格位置过滤
            dataframe['price_position'] < 0.8,  # 不在高位买入
            
            # 成交量确认
            dataframe['volume_momentum'] > 1.2,
            
            # 波动率过滤
            dataframe['volatility_ratio'] < 2.0,  # 避免极端波动
        ]
        
        # 空头入场条件
        short_conditions = [
            # 主要信号：ARO超买回落
            qtpylib.crossed_below(dataframe['aro_rsi'], self.strategy_params['aro_overbought']),
            
            # 信号强度确认
            dataframe['short_signal_strength'] >= 4,
            
            # 趋势过滤
            dataframe['market_regime'].isin(['trending_down', 'ranging']),
            
            # 价格位置过滤
            dataframe['price_position'] > 0.2,  # 不在低位卖出
            
            # 成交量确认
            dataframe['volume_momentum'] > 1.2,
            
            # 波动率过滤
            dataframe['volatility_ratio'] < 2.0,
        ]
        
        # 应用入场条件
        dataframe.loc[
            reduce(lambda x, y: x & y, long_conditions),
            ['enter_long', 'enter_tag']
        ] = (1, 'advanced_long')
        
        dataframe.loc[
            reduce(lambda x, y: x & y, short_conditions),
            ['enter_short', 'enter_tag']
        ] = (1, 'advanced_short')
        
        return dataframe
    
    def populate_exit_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        """定义出场信号"""
        
        # 多头出场条件
        long_exit_conditions = [
            # ARO信号反转
            (dataframe['aro_rsi'] > self.strategy_params['aro_overbought']) |
            dataframe['aro_strong_bearish'] |
            
            # 背离信号
            dataframe['bearish_divergence'] |
            
            # 趋势反转
            (dataframe['market_regime'] == 'trending_down') |
            
            # 技术指标反转
            qtpylib.crossed_below(dataframe['ema_12'], dataframe['ema_26'])
        ]
        
        # 空头出场条件
        short_exit_conditions = [
            # ARO信号反转
            (dataframe['aro_rsi'] < self.strategy_params['aro_oversold']) |
            dataframe['aro_strong_bullish'] |
            
            # 背离信号
            dataframe['bullish_divergence'] |
            
            # 趋势反转
            (dataframe['market_regime'] == 'trending_up') |
            
            # 技术指标反转
            qtpylib.crossed_above(dataframe['ema_12'], dataframe['ema_26'])
        ]
        
        # 应用出场条件
        dataframe.loc[
            reduce(lambda x, y: x | y, long_exit_conditions),
            ['exit_long', 'exit_tag']
        ] = (1, 'advanced_exit_long')
        
        dataframe.loc[
            reduce(lambda x, y: x | y, short_exit_conditions),
            ['exit_short', 'exit_tag']
        ] = (1, 'advanced_exit_short')
        
        return dataframe
    
    def custom_roi(self, pair: str, trade: Trade, current_time: datetime, 
                   trade_duration: int, entry_tag: str, side: str, **kwargs) -> float:
        """
        动态ROI管理
        基于市场状态和信号强度调整获利目标
        """
        try:
            dataframe, _ = self.dp.get_analyzed_dataframe(pair=pair, timeframe=self.timeframe)
            if dataframe.empty:
                return 0.01
            
            current_candle = dataframe.iloc[-1]
            market_regime = current_candle.get('market_regime', 'ranging')
            
            # 基础ROI
            base_roi = 0.02
            
            # 根据市场状态调整
            if market_regime in ['trending_up', 'trending_down']:
                # 趋势市场：提高获利目标
                base_roi *= 1.5
            elif market_regime == 'volatile':
                # 波动市场：降低获利目标
                base_roi *= 0.7
            
            # 根据信号强度调整
            if side == 'long':
                signal_strength = current_candle.get('long_signal_strength', 0)
            else:
                signal_strength = current_candle.get('short_signal_strength', 0)
            
            if signal_strength >= 6:
                base_roi *= 1.3  # 强信号提高目标
            elif signal_strength <= 3:
                base_roi *= 0.8  # 弱信号降低目标
            
            return max(base_roi, 0.005)  # 最小0.5%
            
        except Exception as e:
            self.logger.error(f"动态ROI计算失败: {str(e)}")
            return 0.01
    
    def custom_stoploss(self, pair: str, trade: Trade, current_time: datetime,
                       current_rate: float, current_profit: float, after_fill: bool,
                       **kwargs) -> float:
        """
        智能止损管理
        结合ATR、ZigZag支撑阻力位和时间衰减
        """
        try:
            dataframe, _ = self.dp.get_analyzed_dataframe(pair=pair, timeframe=self.timeframe)
            if dataframe.empty:
                return self.stoploss
            
            current_candle = dataframe.iloc[-1]
            atr_value = current_candle['atr']
            
            if pd.isna(atr_value):
                return self.stoploss
            
            # 基于ATR的动态止损
            atr_multiplier = 2.5
            
            # 根据市场状态调整ATR倍数
            market_regime = current_candle.get('market_regime', 'ranging')
            if market_regime == 'volatile':
                atr_multiplier = 3.0  # 波动市场放宽止损
            elif market_regime in ['trending_up', 'trending_down']:
                atr_multiplier = 2.0  # 趋势市场收紧止损
            
            # 计算ATR止损
            if trade.is_short:
                atr_stop = atr_value * atr_multiplier / current_rate
            else:
                atr_stop = -(atr_value * atr_multiplier / current_rate)
            
            # 结合ZigZag支撑阻力位
            if not pd.isna(current_candle.get('current_support')) and not trade.is_short:
                support_level = current_candle['current_support']
                support_stop = -(current_rate - support_level) / current_rate
                atr_stop = max(atr_stop, support_stop)  # 使用更宽松的止损
            
            if not pd.isna(current_candle.get('current_resistance')) and trade.is_short:
                resistance_level = current_candle['current_resistance']
                resistance_stop = (resistance_level - current_rate) / current_rate
                atr_stop = max(atr_stop, resistance_stop)
            
            # 时间衰减止损（长时间持仓收紧止损）
            trade_duration_hours = (current_time - trade.open_date_utc).total_seconds() / 3600
            if trade_duration_hours > 24:
                time_factor = min(1.5, 1 + (trade_duration_hours - 24) / 48 * 0.5)
                atr_stop = atr_stop / time_factor
            
            # 盈利保护（移动止损）
            if current_profit > 0.02:  # 盈利超过2%时启用移动止损
                profit_protection = -current_profit * 0.3  # 保护30%利润
                if trade.is_short:
                    profit_protection = -profit_protection
                atr_stop = max(atr_stop, profit_protection)
            
            return max(atr_stop, self.stoploss)
            
        except Exception as e:
            self.logger.error(f"智能止损计算失败: {str(e)}")
            return self.stoploss
    
    def custom_exit(self, pair: str, trade: Trade, current_time: datetime, 
                   current_rate: float, current_profit: float, **kwargs):
        """
        智能出场管理
        """
        try:
            dataframe, _ = self.dp.get_analyzed_dataframe(pair=pair, timeframe=self.timeframe)
            if dataframe.empty:
                return False, None
            
            current_candle = dataframe.iloc[-1]
            
            # 强制出场条件
            
            # 1. 时间限制
            trade_duration = current_time - trade.open_date_utc
            if trade_duration > timedelta(hours=self.strategy_params['max_trade_duration_hours']):
                return True, 'time_limit'
            
            # 2. 市场状态剧变
            market_regime = current_candle.get('market_regime', 'ranging')
            if current_candle.get('volatility_ratio', 1) > 3.0:
                return True, 'extreme_volatility'
            
            # 3. 信号完全反转
            if trade.is_short:
                if (current_candle.get('long_signal_strength', 0) >= 5 and 
                    current_candle.get('short_signal_strength', 0) <= 2):
                    return True, 'signal_reversal'
            else:
                if (current_candle.get('short_signal_strength', 0) >= 5 and 
                    current_candle.get('long_signal_strength', 0) <= 2):
                    return True, 'signal_reversal'
            
            # 4. 周末平仓（如果启用）
            if (self.strategy_params['avoid_weekend_close'] and 
                current_time.weekday() >= 5):  # 周六或周日
                return True, 'weekend_close'
            
            return False, None
            
        except Exception as e:
            self.logger.error(f"智能出场管理失败: {str(e)}")
            return False, None
    
    def leverage(self, pair: str, current_time: datetime, current_rate: float,
                proposed_leverage: float, max_leverage: float, entry_tag: str,
                side: str, **kwargs) -> float:
        """
        智能杠杆管理
        基于信号强度、市场状态和风险控制
        """
        try:
            dataframe, _ = self.dp.get_analyzed_dataframe(pair=pair, timeframe=self.timeframe)
            if dataframe.empty:
                return 1.0
            
            current_candle = dataframe.iloc[-1]
            
            # 基础杠杆
            base_leverage = 2.0
            
            # 根据信号强度调整
            if side == 'long':
                signal_strength = current_candle.get('long_signal_strength', 0)
            else:
                signal_strength = current_candle.get('short_signal_strength', 0)
            
            if signal_strength >= 6:
                base_leverage = 3.0  # 强信号提高杠杆
            elif signal_strength <= 3:
                base_leverage = 1.5  # 弱信号降低杠杆
            
            # 根据市场状态调整
            market_regime = current_candle.get('market_regime', 'ranging')
            volatility_ratio = current_candle.get('volatility_ratio', 1)
            
            if market_regime == 'volatile' or volatility_ratio > 2.0:
                base_leverage *= 0.7  # 波动市场降低杠杆
            elif market_regime in ['trending_up', 'trending_down']:
                base_leverage *= 1.2  # 趋势市场适当提高杠杆
            
            # 限制最大杠杆
            final_leverage = min(base_leverage, max_leverage, 5.0)
            
            self.logger.info(f"杠杆计算: {pair}, 信号强度: {signal_strength}, "
                           f"市场状态: {market_regime}, 最终杠杆: {final_leverage}")
            
            return final_leverage
            
        except Exception as e:
            self.logger.error(f"杠杆计算失败: {str(e)}")
            return 1.0
    
    def confirm_trade_entry(self, pair: str, order_type: str, amount: float,
                           rate: float, time_in_force: str, current_time: datetime,
                           entry_tag: str, side: str, **kwargs) -> bool:
        """
        最终交易确认
        多重安全检查
        """
        try:
            # 基础检查
            if not super().confirm_trade_entry(pair, order_type, amount, rate, 
                                             time_in_force, current_time, 
                                             entry_tag, side, **kwargs):
                return False
            
            # 获取当前数据
            dataframe, _ = self.dp.get_analyzed_dataframe(pair=pair, timeframe=self.timeframe)
            if dataframe.empty:
                return False
            
            current_candle = dataframe.iloc[-1]
            
            # 信号强度最终检查
            if side == 'long':
                signal_strength = current_candle.get('long_signal_strength', 0)
                min_strength = 4
            else:
                signal_strength = current_candle.get('short_signal_strength', 0)
                min_strength = 4
            
            if signal_strength < min_strength:
                self.logger.warning(f"信号强度不足: {signal_strength} < {min_strength}")
                return False
            
            # 市场状态检查
            market_regime = current_candle.get('market_regime', 'ranging')
            if market_regime == 'volatile' and current_candle.get('volatility_ratio', 1) > 2.5:
                self.logger.warning(f"市场过于波动，跳过交易: {pair}")
                return False
            
            # 时间过滤（避免重要新闻时段等）
            current_hour = current_time.hour
            if current_hour in [0, 1, 22, 23]:  # 避免流动性较低的时段
                self.logger.info(f"避开低流动性时段: {current_hour}点")
                return False
            
            self.logger.info(f"交易确认通过: {pair} {side} 信号强度: {signal_strength}")
            return True
            
        except Exception as e:
            self.logger.error(f"交易确认失败: {str(e)}")
            return False