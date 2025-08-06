"""
ATR ZigZag指标
基于Pine Script转换的Python实现

功能特性：
1. 基于ATR的动态阈值ZigZag
2. 枢轴点检测和确认
3. 趋势长度和平均长度计算
4. 支持和阻力位识别
"""

import numpy as np
import pandas as pd
import talib.abstract as ta
from typing import Dict, Any, List, Tuple, Optional
from .base_indicator import BaseIndicator

class ATRZigZag(BaseIndicator):
    """
    ATR ZigZag指标
    
    使用ATR作为动态阈值来识别重要的价格转折点
    """
    
    def __init__(self, params: Dict[str, Any] = None):
        """
        初始化ATR ZigZag指标
        
        默认参数：
        - atr_length: 10 (ATR计算周期)
        - pivot_length: 3 (枢轴点检测长度，必须为奇数)
        - atr_multiplier: 2.0 (ATR倍数阈值)
        - avg_length_period: 3 (平均长度计算周期)
        - max_lines: 100 (最大保留的ZigZag线数量)
        """
        default_params = {
            'atr_length': 10,
            'pivot_length': 3,
            'atr_multiplier': 2.0,
            'avg_length_period': 3,
            'max_lines': 100
        }
        
        if params:
            default_params.update(params)
            
        super().__init__("ATRZigZag", default_params)
        
        # 验证pivot_length必须为奇数
        if self.params['pivot_length'] % 2 == 0:
            self.logger.warning("pivot_length必须为奇数，自动调整为下一个奇数")
            self.params['pivot_length'] += 1
    
    def calculate(self, dataframe: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """
        计算ATR ZigZag指标
        
        Args:
            dataframe: OHLCV数据框
            
        Returns:
            包含ZigZag指标的数据框
        """
        df = dataframe.copy()
        
        # 1. 计算ATR
        df['atr'] = ta.ATR(df, timeperiod=self.params['atr_length'])
        
        # 2. 检测枢轴点
        df = self._detect_pivots(df)
        
        # 3. 应用ATR过滤
        df = self._apply_atr_filter(df)
        
        # 4. 计算ZigZag线和统计信息
        df = self._calculate_zigzag_stats(df)
        
        # 5. 识别支撑阻力位
        df = self._identify_support_resistance(df)
        
        self.logger.info(f"ATR ZigZag计算完成，数据点数: {len(df)}")
        return df
    
    def _detect_pivots(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        检测价格枢轴点（高点和低点）
        """
        try:
            pivot_length = self.params['pivot_length']
            half_length = pivot_length // 2
            
            df['pivot_high'] = False
            df['pivot_low'] = False
            df['pivot_high_value'] = np.nan
            df['pivot_low_value'] = np.nan
            
            # 检测枢轴点
            for i in range(half_length, len(df) - half_length):
                # 检查是否为高点枢轴
                is_high_pivot = True
                is_low_pivot = True
                
                current_high = df['high'].iloc[i]
                current_low = df['low'].iloc[i]
                
                # 检查前后的价格
                for j in range(1, half_length + 1):
                    # 高点检查：当前点应该高于前后的点
                    if (current_high <= df['high'].iloc[i - j] or 
                        current_high <= df['high'].iloc[i + j]):
                        is_high_pivot = False
                    
                    # 低点检查：当前点应该低于前后的点
                    if (current_low >= df['low'].iloc[i - j] or 
                        current_low >= df['low'].iloc[i + j]):
                        is_low_pivot = False
                
                # 记录枢轴点
                if is_high_pivot:
                    df.loc[df.index[i], 'pivot_high'] = True
                    df.loc[df.index[i], 'pivot_high_value'] = current_high
                
                if is_low_pivot:
                    df.loc[df.index[i], 'pivot_low'] = True
                    df.loc[df.index[i], 'pivot_low_value'] = current_low
            
            self.logger.debug("枢轴点检测完成")
            return df
            
        except Exception as e:
            self.logger.error(f"枢轴点检测失败: {str(e)}")
            return df
    
    def _apply_atr_filter(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        应用ATR过滤器，只保留满足ATR阈值的枢轴点
        """
        try:
            df['confirmed_pivot_high'] = False
            df['confirmed_pivot_low'] = False
            df['confirmed_pivot_high_value'] = np.nan
            df['confirmed_pivot_low_value'] = np.nan
            
            # 存储确认的枢轴点
            confirmed_pivots = []  # [(index, type, value), ...]
            
            for i in range(len(df)):
                if not (df['pivot_high'].iloc[i] or df['pivot_low'].iloc[i]):
                    continue
                
                current_atr = df['atr'].iloc[i]
                if pd.isna(current_atr):
                    continue
                
                threshold = current_atr * self.params['atr_multiplier']
                
                # 检查是否满足ATR阈值
                if len(confirmed_pivots) == 0:
                    # 第一个枢轴点，直接添加
                    if df['pivot_high'].iloc[i]:
                        confirmed_pivots.append((i, 'high', df['pivot_high_value'].iloc[i]))
                        df.loc[df.index[i], 'confirmed_pivot_high'] = True
                        df.loc[df.index[i], 'confirmed_pivot_high_value'] = df['pivot_high_value'].iloc[i]
                    elif df['pivot_low'].iloc[i]:
                        confirmed_pivots.append((i, 'low', df['pivot_low_value'].iloc[i]))
                        df.loc[df.index[i], 'confirmed_pivot_low'] = True
                        df.loc[df.index[i], 'confirmed_pivot_low_value'] = df['pivot_low_value'].iloc[i]
                else:
                    last_pivot = confirmed_pivots[-1]
                    last_value = last_pivot[2]
                    last_type = last_pivot[1]
                    
                    # 检查当前枢轴点类型和距离
                    if df['pivot_high'].iloc[i]:
                        current_value = df['pivot_high_value'].iloc[i]
                        
                        if last_type == 'high':
                            # 连续高点，更新为更高的点
                            if current_value > last_value:
                                # 移除上一个高点
                                last_idx = confirmed_pivots[-1][0]
                                df.loc[df.index[last_idx], 'confirmed_pivot_high'] = False
                                df.loc[df.index[last_idx], 'confirmed_pivot_high_value'] = np.nan
                                
                                # 添加新高点
                                confirmed_pivots[-1] = (i, 'high', current_value)
                                df.loc[df.index[i], 'confirmed_pivot_high'] = True
                                df.loc[df.index[i], 'confirmed_pivot_high_value'] = current_value
                        else:
                            # 从低点转为高点，检查ATR阈值
                            if abs(current_value - last_value) >= threshold:
                                confirmed_pivots.append((i, 'high', current_value))
                                df.loc[df.index[i], 'confirmed_pivot_high'] = True
                                df.loc[df.index[i], 'confirmed_pivot_high_value'] = current_value
                    
                    elif df['pivot_low'].iloc[i]:
                        current_value = df['pivot_low_value'].iloc[i]
                        
                        if last_type == 'low':
                            # 连续低点，更新为更低的点
                            if current_value < last_value:
                                # 移除上一个低点
                                last_idx = confirmed_pivots[-1][0]
                                df.loc[df.index[last_idx], 'confirmed_pivot_low'] = False
                                df.loc[df.index[last_idx], 'confirmed_pivot_low_value'] = np.nan
                                
                                # 添加新低点
                                confirmed_pivots[-1] = (i, 'low', current_value)
                                df.loc[df.index[i], 'confirmed_pivot_low'] = True
                                df.loc[df.index[i], 'confirmed_pivot_low_value'] = current_value
                        else:
                            # 从高点转为低点，检查ATR阈值
                            if abs(current_value - last_value) >= threshold:
                                confirmed_pivots.append((i, 'low', current_value))
                                df.loc[df.index[i], 'confirmed_pivot_low'] = True
                                df.loc[df.index[i], 'confirmed_pivot_low_value'] = current_value
                
                # 限制保存的枢轴点数量
                if len(confirmed_pivots) > self.params['max_lines']:
                    confirmed_pivots = confirmed_pivots[-self.params['max_lines']:]
            
            self.logger.debug(f"ATR过滤完成，确认枢轴点数量: {len(confirmed_pivots)}")
            return df
            
        except Exception as e:
            self.logger.error(f"ATR过滤失败: {str(e)}")
            return df
    
    def _calculate_zigzag_stats(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算ZigZag统计信息
        """
        try:
            df['zigzag_length'] = np.nan
            df['zigzag_size'] = np.nan
            df['zigzag_avg_length'] = np.nan
            df['zigzag_direction'] = 0  # 1为上涨，-1为下跌
            
            # 获取所有确认的枢轴点
            pivot_indices = []
            pivot_values = []
            pivot_types = []
            
            for i in range(len(df)):
                if df['confirmed_pivot_high'].iloc[i]:
                    pivot_indices.append(i)
                    pivot_values.append(df['confirmed_pivot_high_value'].iloc[i])
                    pivot_types.append('high')
                elif df['confirmed_pivot_low'].iloc[i]:
                    pivot_indices.append(i)
                    pivot_values.append(df['confirmed_pivot_low_value'].iloc[i])
                    pivot_types.append('low')
            
            # 计算ZigZag段的统计信息
            for i in range(1, len(pivot_indices)):
                current_idx = pivot_indices[i]
                prev_idx = pivot_indices[i-1]
                
                # 计算长度（K线数量）
                length = current_idx - prev_idx
                df.loc[df.index[current_idx], 'zigzag_length'] = length
                
                # 计算大小（价格变化）
                size = abs(pivot_values[i] - pivot_values[i-1])
                df.loc[df.index[current_idx], 'zigzag_size'] = size
                
                # 计算方向
                if pivot_types[i] == 'high' and pivot_types[i-1] == 'low':
                    df.loc[df.index[current_idx], 'zigzag_direction'] = 1
                elif pivot_types[i] == 'low' and pivot_types[i-1] == 'high':
                    df.loc[df.index[current_idx], 'zigzag_direction'] = -1
                
                # 计算平均长度
                if i >= self.params['avg_length_period']:
                    avg_period = self.params['avg_length_period']
                    start_idx = max(0, i - avg_period + 1)
                    lengths = []
                    
                    for j in range(start_idx, i + 1):
                        if j < len(pivot_indices) - 1:
                            seg_length = pivot_indices[j+1] - pivot_indices[j]
                            lengths.append(seg_length)
                    
                    if lengths:
                        avg_length = np.mean(lengths)
                        df.loc[df.index[current_idx], 'zigzag_avg_length'] = avg_length
            
            self.logger.debug("ZigZag统计信息计算完成")
            return df
            
        except Exception as e:
            self.logger.error(f"ZigZag统计信息计算失败: {str(e)}")
            return df
    
    def _identify_support_resistance(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        识别支撑和阻力位
        """
        try:
            df['support_level'] = np.nan
            df['resistance_level'] = np.nan
            df['support_strength'] = 0
            df['resistance_strength'] = 0
            
            # 收集所有确认的枢轴点
            highs = []
            lows = []
            
            for i in range(len(df)):
                if df['confirmed_pivot_high'].iloc[i]:
                    highs.append((i, df['confirmed_pivot_high_value'].iloc[i]))
                if df['confirmed_pivot_low'].iloc[i]:
                    lows.append((i, df['confirmed_pivot_low_value'].iloc[i]))
            
            # 识别支撑���（基于低点）
            for i, (idx, value) in enumerate(lows):
                # 计算该支撑位的强度（附近相似价位的数量）
                strength = 1
                tolerance = df['atr'].iloc[idx] * 0.5 if not pd.isna(df['atr'].iloc[idx]) else value * 0.01
                
                for j, (other_idx, other_value) in enumerate(lows):
                    if i != j and abs(value - other_value) <= tolerance:
                        strength += 1
                
                df.loc[df.index[idx], 'support_level'] = value
                df.loc[df.index[idx], 'support_strength'] = strength
            
            # 识别阻力位（基于高点）
            for i, (idx, value) in enumerate(highs):
                # 计算该阻力位的强度
                strength = 1
                tolerance = df['atr'].iloc[idx] * 0.5 if not pd.isna(df['atr'].iloc[idx]) else value * 0.01
                
                for j, (other_idx, other_value) in enumerate(highs):
                    if i != j and abs(value - other_value) <= tolerance:
                        strength += 1
                
                df.loc[df.index[idx], 'resistance_level'] = value
                df.loc[df.index[idx], 'resistance_strength'] = strength
            
            # 向前填充最近的支撑阻力位
            df['current_support'] = df['support_level'].fillna(method='ffill')
            df['current_resistance'] = df['resistance_level'].fillna(method='ffill')
            
            self.logger.debug("支撑阻力位识别完成")
            return df
            
        except Exception as e:
            self.logger.error(f"支撑阻力位识别失败: {str(e)}")
            return df
    
    def get_current_trend(self, df: pd.DataFrame) -> str:
        """
        获取当前趋势方向
        
        Returns:
            'uptrend', 'downtrend', 或 'sideways'
        """
        try:
            # 获取最近的几个ZigZag方向
            recent_directions = df['zigzag_direction'].dropna().tail(3)
            
            if len(recent_directions) == 0:
                return 'sideways'
            
            # 计算趋势
            if recent_directions.iloc[-1] == 1:
                return 'uptrend'
            elif recent_directions.iloc[-1] == -1:
                return 'downtrend'
            else:
                return 'sideways'
                
        except Exception as e:
            self.logger.error(f"趋势判断失败: {str(e)}")
            return 'sideways'
    
    def get_nearest_support_resistance(self, df: pd.DataFrame, 
                                     current_price: float) -> Tuple[Optional[float], Optional[float]]:
        """
        获取最近的支撑和阻力位
        
        Args:
            df: 数据框
            current_price: 当前价格
            
        Returns:
            (nearest_support, nearest_resistance)
        """
        try:
            # 获取所有支撑位和阻力位
            supports = df[df['support_level'].notna()]['support_level'].values
            resistances = df[df['resistance_level'].notna()]['resistance_level'].values
            
            # 找到最近的支撑位（低于当前价格）
            valid_supports = supports[supports < current_price]
            nearest_support = valid_supports.max() if len(valid_supports) > 0 else None
            
            # 找到最近的阻力位（高于当前价格）
            valid_resistances = resistances[resistances > current_price]
            nearest_resistance = valid_resistances.min() if len(valid_resistances) > 0 else None
            
            return nearest_support, nearest_resistance
            
        except Exception as e:
            self.logger.error(f"支撑阻力位查找失败: {str(e)}")
            return None, None