"""
自适应共振振荡器 (Adaptive Resonance Oscillator)
基于Pine Script转换的Python实现

功能特性：
1. 自适应RSI计算（基于市场频率）
2. 希尔伯特变换周期检测
3. 双通道挤压检测
4. 背离信号识别
5. 成交量加权选项
"""

import numpy as np
import pandas as pd
import talib.abstract as ta
from typing import Dict, Any, Tuple, Optional
from .base_indicator import BaseIndicator

class AdaptiveResonanceOscillator(BaseIndicator):
    """
    自适应共振振荡器
    
    将Pine Script的复杂逻辑转换为高效的Python实现
    """
    
    def __init__(self, params: Dict[str, Any] = None):
        """
        初始化ARO指标
        
        默认参数对应Pine Script设置：
        - smooth: True (启用平滑)
        - smooth_length: 12 (平滑长度)
        - median_length: 100 (频率检测长度)
        - use_volume: False (是否使用成交量调整)
        - bb_length: 20 (布林带长度)
        - kc_length: 20 (肯特纳通道长度)
        - momentum_length: 12 (动量长度)
        """
        default_params = {
            'smooth': True,
            'smooth_length': 12,
            'median_length': 100,
            'use_volume': False,
            'bb_length': 20,
            'bb_mult': 2.0,
            'kc_length': 20,
            'kc_mult': 1.5,
            'use_ema_for_kc': True,
            'momentum_length': 12,
            'divergence_lookback': 20
        }
        
        if params:
            default_params.update(params)
            
        super().__init__("AdaptiveResonanceOscillator", default_params)
    
    def calculate(self, dataframe: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """
        计算自适应共振振荡器的所有组件
        
        Args:
            dataframe: OHLCV数据框
            
        Returns:
            包含ARO指标的数据框
        """
        df = dataframe.copy()
        
        # 1. 计算自适应周期
        df = self._calculate_adaptive_period(df)
        
        # 2. 计算自适应RSI
        df = self._calculate_adaptive_rsi(df)
        
        # 3. 计算双通道挤压
        df = self._calculate_dual_squeeze(df)
        
        # 4. 计算背离信号
        df = self._calculate_divergences(df)
        
        # 5. 生成综合信号
        df = self._generate_signals(df)
        
        self.logger.info(f"ARO指标计算完成，数据点数: {len(df)}")
        return df
    
    def _calculate_adaptive_period(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        使用希尔伯特变换计算自适应周期
        这是Pine Script中最复杂的部分
        """
        try:
            # 价格平滑处理
            df['price_smooth'] = (df['close'] + df['close'].shift(1) + 
                                df['close'].shift(2) + df['close'].shift(3)) / 4
            
            # 去趋势处理 (Detrender)
            df['detrender'] = (0.0962 * df['price_smooth'] + 
                             0.5769 * df['price_smooth'].shift(2) - 
                             0.5769 * df['price_smooth'].shift(4) - 
                             0.0962 * df['price_smooth'].shift(6))
            
            # 希尔伯特变换
            df['I1'] = df['detrender'].shift(3)
            df['Q1'] = (0.0962 * df['detrender'] + 
                       0.5769 * df['detrender'].shift(2) - 
                       0.5769 * df['detrender'].shift(4) - 
                       0.0962 * df['detrender'].shift(6))
            
            # 正交分量
            df['jI'] = df['I1'].shift(3)
            df['jQ'] = df['Q1'].shift(3)
            
            df['I2'] = df['I1'] - df['jQ']
            df['Q2'] = df['Q1'] + df['jI']
            
            # 相位计算
            df['Re'] = df['I2'] * df['I2'].shift(1) + df['Q2'] * df['Q2'].shift(1)
            df['Im'] = df['I2'] * df['Q2'].shift(1) - df['Q2'] * df['I2'].shift(1)
            
            # 相位角度
            df['phase_angle'] = np.degrees(np.arctan2(df['Im'], df['Re']))
            df['phase_angle'] = np.where(df['phase_angle'] < 0, 
                                       df['phase_angle'] + 360, 
                                       df['phase_angle'])
            
            # 限制最小相位
            df['phase_angle_clamped'] = np.maximum(df['phase_angle'], 1.0)
            
            # 计算希尔伯特周期
            df['hilbert_period_raw'] = 360 / df['phase_angle_clamped']
            
            # 使用中位数平滑市场频率
            df['market_frequency'] = df['hilbert_period_raw'].rolling(
                window=self.params['median_length'], center=True).median()
            
            # 计算自适应周期
            df['adaptive_period'] = (df['market_frequency'] / 2).astype(int)
            df['adaptive_period'] = np.clip(df['adaptive_period'], 2, 50)  # 限制范围
            
            self.logger.debug("自适应周期计算完成")
            return df
            
        except Exception as e:
            self.logger.error(f"自适应周期计算失败: {str(e)}")
            # 使用固定周期作为后备
            df['adaptive_period'] = 14
            return df
    
    def _calculate_adaptive_rsi(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算自适应RSI
        支持成交量加权选项
        """
        try:
            # 为每行计算RSI（使用自适应周期）
            rsi_values = []
            
            for i in range(len(df)):
                if i < 50:  # 确保有足够的历史数据
                    rsi_values.append(np.nan)
                    continue
                
                period = int(df['adaptive_period'].iloc[i]) if not pd.isna(df['adaptive_period'].iloc[i]) else 14
                period = max(2, min(period, 50))  # 限制周期范围
                
                # 获取计算RSI所需的数据
                start_idx = max(0, i - period * 3)  # 确保有足够数据
                end_idx = i + 1
                
                close_data = df['close'].iloc[start_idx:end_idx]
                
                if self.params['use_volume']:
                    # 成交量加权RSI
                    volume_data = df['volume'].iloc[start_idx:end_idx]
                    rsi_val = self._calculate_volume_weighted_rsi(close_data, volume_data, period)
                else:
                    # 标准RSI
                    if len(close_data) >= period + 1:
                        rsi_val = ta.RSI(close_data, timeperiod=period).iloc[-1]
                    else:
                        rsi_val = np.nan
                
                rsi_values.append(rsi_val)
            
            df['aro_rsi_raw'] = rsi_values
            
            # 应用平滑处理
            if self.params['smooth']:
                df['aro_rsi'] = ta.HMA(df['aro_rsi_raw'], timeperiod=self.params['smooth_length'])
            else:
                df['aro_rsi'] = df['aro_rsi_raw']
            
            self.logger.debug("自适应RSI计算完成")
            return df
            
        except Exception as e:
            self.logger.error(f"自适应RSI计算失败: {str(e)}")
            # 使用标准RSI作为后备
            df['aro_rsi'] = ta.RSI(df['close'], timeperiod=14)
            return df
    
    def _calculate_volume_weighted_rsi(self, close_data: pd.Series, 
                                     volume_data: pd.Series, period: int) -> float:
        """
        计算成交量加权RSI
        """
        try:
            if len(close_data) < period + 1:
                return np.nan
            
            # 计算价格变化
            price_changes = close_data.diff()
            
            # 分离上涨和下跌
            gains = np.where(price_changes > 0, price_changes, 0)
            losses = np.where(price_changes < 0, -price_changes, 0)
            
            # 成交量加权
            gains_vol = gains * volume_data
            losses_vol = losses * volume_data
            
            # 计算加权平均
            alpha = 1.0 / period
            avg_gain = pd.Series(gains_vol).ewm(alpha=alpha).mean().iloc[-1]
            avg_loss = pd.Series(losses_vol).ewm(alpha=alpha).mean().iloc[-1]
            
            if avg_loss == 0:
                return 100.0
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            return rsi
            
        except Exception as e:
            self.logger.error(f"成交量加权RSI计算失败: {str(e)}")
            return np.nan
    
    def _calculate_dual_squeeze(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算双通道挤压指标
        """
        try:
            # 布林带计算
            bb_basis = ta.SMA(df['close'], timeperiod=self.params['bb_length'])
            bb_std = ta.STDDEV(df['close'], timeperiod=self.params['bb_length'])
            df['bb_upper'] = bb_basis + (self.params['bb_mult'] * bb_std)
            df['bb_lower'] = bb_basis - (self.params['bb_mult'] * bb_std)
            
            # 肯特纳通道计算
            if self.params['use_ema_for_kc']:
                kc_basis = ta.EMA(df['close'], timeperiod=self.params['kc_length'])
            else:
                kc_basis = ta.SMA(df['close'], timeperiod=self.params['kc_length'])
            
            kc_atr = ta.ATR(df, timeperiod=self.params['kc_length'])
            df['kc_upper'] = kc_basis + (self.params['kc_mult'] * kc_atr)
            df['kc_lower'] = kc_basis - (self.params['kc_mult'] * kc_atr)
            
            # 识别挤压状态
            df['is_squeeze'] = ((df['bb_upper'] < df['kc_upper']) & 
                              (df['bb_lower'] > df['kc_lower']))
            
            # 挤压释放信号
            df['squeeze_fired'] = (df['is_squeeze'].shift(1) & ~df['is_squeeze'])
            
            # 计算动量
            df['momentum'] = (ta.LINEARREG(df['close'], timeperiod=self.params['momentum_length']) - 
                            ta.LINEARREG(df['close'], timeperiod=self.params['momentum_length']).shift(1))
            
            self.logger.debug("双通道挤压计算完成")
            return df
            
        except Exception as e:
            self.logger.error(f"双通道挤压计算失败: {str(e)}")
            return df
    
    def _calculate_divergences(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算背离信号
        """
        try:
            lookback = self.params['divergence_lookback']
            
            # 寻找RSI的高点和低点
            df['rsi_high'] = df['aro_rsi'].rolling(window=lookback*2+1, center=True).max() == df['aro_rsi']
            df['rsi_low'] = df['aro_rsi'].rolling(window=lookback*2+1, center=True).min() == df['aro_rsi']
            
            # 寻找价格的高点和低点
            df['price_high'] = df['high'].rolling(window=lookback*2+1, center=True).max() == df['high']
            df['price_low'] = df['low'].rolling(window=lookback*2+1, center=True).min() == df['low']
            
            # 初始化背离信号
            df['bullish_divergence'] = False
            df['bearish_divergence'] = False
            
            # 计算背离（简化版本）
            for i in range(lookback*2, len(df)-lookback):
                # 看涨背离：价格创新低，RSI未创新低
                if df['price_low'].iloc[i]:
                    prev_low_idx = self._find_previous_pivot(df['price_low'], i, lookback*4)
                    if prev_low_idx is not None:
                        if (df['low'].iloc[i] < df['low'].iloc[prev_low_idx] and 
                            df['aro_rsi'].iloc[i] > df['aro_rsi'].iloc[prev_low_idx]):
                            df.loc[df.index[i], 'bullish_divergence'] = True
                
                # 看跌背离：价格创新高，RSI未创新高
                if df['price_high'].iloc[i]:
                    prev_high_idx = self._find_previous_pivot(df['price_high'], i, lookback*4)
                    if prev_high_idx is not None:
                        if (df['high'].iloc[i] > df['high'].iloc[prev_high_idx] and 
                            df['aro_rsi'].iloc[i] < df['aro_rsi'].iloc[prev_high_idx]):
                            df.loc[df.index[i], 'bearish_divergence'] = True
            
            self.logger.debug("背离信号计算完成")
            return df
            
        except Exception as e:
            self.logger.error(f"背离信号计算失败: {str(e)}")
            df['bullish_divergence'] = False
            df['bearish_divergence'] = False
            return df
    
    def _find_previous_pivot(self, pivot_series: pd.Series, current_idx: int, 
                           max_lookback: int) -> Optional[int]:
        """
        寻找前一个枢轴点
        """
        start_idx = max(0, current_idx - max_lookback)
        for i in range(current_idx - 1, start_idx, -1):
            if pivot_series.iloc[i]:
                return i
        return None
    
    def _generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        生成综合交易信号
        """
        try:
            # 强烈看涨信号：RSI从超卖区域向上突破
            df['aro_strong_bullish'] = (
                (df['aro_rsi'] > df['aro_rsi'].shift(1)) & 
                (df['aro_rsi'].shift(1) < 20)
            )
            
            # 强烈看跌信号：RSI从超买区域向下突破
            df['aro_strong_bearish'] = (
                (df['aro_rsi'] < df['aro_rsi'].shift(1)) & 
                (df['aro_rsi'].shift(1) > 80)
            )
            
            # 挤压突破信号
            df['squeeze_bullish'] = df['squeeze_fired'] & (df['momentum'] > 0)
            df['squeeze_bearish'] = df['squeeze_fired'] & (df['momentum'] < 0)
            
            # 综合信号强度评分 (0-100)
            df['aro_signal_strength'] = 50  # 中性基准
            
            # RSI位置调整
            df['aro_signal_strength'] += (df['aro_rsi'] - 50) * 0.5
            
            # 背离信号调整
            df['aro_signal_strength'] += np.where(df['bullish_divergence'], 15, 0)
            df['aro_signal_strength'] -= np.where(df['bearish_divergence'], 15, 0)
            
            # 挤压信号调整
            df['aro_signal_strength'] += np.where(df['squeeze_bullish'], 10, 0)
            df['aro_signal_strength'] -= np.where(df['squeeze_bearish'], 10, 0)
            
            # 限制范围
            df['aro_signal_strength'] = np.clip(df['aro_signal_strength'], 0, 100)
            
            self.logger.debug("综合信号生成完成")
            return df
            
        except Exception as e:
            self.logger.error(f"信号生成失败: {str(e)}")
            return df