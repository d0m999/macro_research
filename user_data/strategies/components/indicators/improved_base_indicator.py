"""
改进版基础指标类 - 为所有自定义指标提供统一接口
遵循加密算法交易开发指南的注释和日志标准
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple
from functools import wraps
import hashlib
import time

import numpy as np
import pandas as pd
import talib.abstract as ta


class CacheManager:
    """
    缓存管理器 - 处理指标计算结果的缓存
    
    @description 提供带有过期时间和大小限制的缓存机制
    """
    
    def __init__(self, max_size: int = 100, ttl_seconds: int = 300):
        """
        初始化缓存管理器
        
        @param {int} max_size - 最大缓存条目数
        @param {int} ttl_seconds - 缓存过期时间（秒）
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger(f"{__name__}.CacheManager")
    
    def get(self, key: str) -> Optional[pd.DataFrame]:
        """
        获取缓存值
        
        @param {str} key - 缓存键
        @returns {pd.DataFrame|None} 缓存的数据框或None
        """
        if key not in self._cache:
            return None
            
        cache_entry = self._cache[key]
        if time.time() - cache_entry['timestamp'] > self.ttl_seconds:
            del self._cache[key]
            self.logger.debug(f"缓存过期，删除键: {key}")
            return None
            
        self.logger.debug(f"缓存命中: {key}")
        return cache_entry['data']
    
    def set(self, key: str, data: pd.DataFrame) -> None:
        """
        设置缓存值
        
        @param {str} key - 缓存键
        @param {pd.DataFrame} data - 要缓存的数据
        """
        # 如果缓存已满，删除最旧的条目
        if len(self._cache) >= self.max_size:
            oldest_key = min(self._cache.keys(), 
                           key=lambda k: self._cache[k]['timestamp'])
            del self._cache[oldest_key]
            self.logger.debug(f"缓存已满，删除最旧条目: {oldest_key}")
        
        self._cache[key] = {
            'data': data,
            'timestamp': time.time()
        }
        self.logger.debug(f"缓存设置: {key}")


class SignalStrengthStrategy(ABC):
    """
    信号强度判断策略接口
    
    @description 使用策略模式支持不同的信号强度判断方法
    """
    
    @abstractmethod
    def get_strength(self, value: float) -> str:
        """
        获取信号强度
        
        @param {float} value - 指标值
        @returns {str} 信号强度字符串
        """
        pass


class DefaultSignalStrengthStrategy(SignalStrengthStrategy):
    """
    默认信号强度判断策略
    
    @description 基于阈值的传统信号强度判断
    """
    
    # 默认阈值常量
    DEFAULT_THRESHOLDS = {
        'strong_bull': 80,
        'bull': 60,
        'bear': 40,
        'strong_bear': 20
    }
    
    def __init__(self, thresholds: Dict[str, float] = None):
        """
        初始化策略
        
        @param {Dict[str, float]} thresholds - 自定义阈值字典
        """
        self.thresholds = thresholds or self.DEFAULT_THRESHOLDS
    
    def get_strength(self, value: float) -> str:
        """
        根据阈值判断信号强度
        
        @param {float} value - 指标值
        @returns {str} 信号强度字符串
        """
        if value >= self.thresholds['strong_bull']:
            return 'strong_bullish'
        elif value >= self.thresholds['bull']:
            return 'bullish'
        elif value <= self.thresholds['strong_bear']:
            return 'strong_bearish'
        elif value <= self.thresholds['bear']:
            return 'bearish'
        else:
            return 'neutral'


def cache_result(func):
    """
    缓存装饰器 - 自动缓存指标计算结果
    
    @description 装饰器模式实现缓存功能
    """
    @wraps(func)
    def wrapper(self, dataframe: pd.DataFrame, **kwargs):
        # 生成缓存键
        data_hash = hashlib.md5(
            pd.util.hash_pandas_object(dataframe).values
        ).hexdigest()
        cache_key = f"{self.name}_{data_hash}_{hash(frozenset(kwargs.items()))}"
        
        # 尝试从缓存获取
        cached_result = self.cache_manager.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # 执行计算并缓存结果
        result = func(self, dataframe, **kwargs)
        self.cache_manager.set(cache_key, result)
        return result
    
    return wrapper


class BaseIndicator(ABC):
    """
    改进版自定义指标基类
    
    @description 设计原则：
    1. 单一职责原则 - 每个方法只负责一个功能
    2. 开闭原则 - 通过策略模式支持扩展
    3. 依赖注入 - 支持自定义缓存和信号策略
    4. 完整的错误处理和日志记录
    5. 性能优化（向量化操作和智能缓存）
    """
    
    # 必需的数据列常量
    REQUIRED_COLUMNS = ['open', 'high', 'low', 'close', 'volume']
    
    def __init__(self, 
                 name: str, 
                 params: Dict[str, Any] = None,
                 cache_manager: CacheManager = None,
                 signal_strategy: SignalStrengthStrategy = None):
        """
        初始化指标
        
        @param {str} name - 指标名称
        @param {Dict[str, Any]} params - 指标参数字典
        @param {CacheManager} cache_manager - 缓存管理器实例
        @param {SignalStrengthStrategy} signal_strategy - 信号强度判断策略
        """
        self.name = name
        self.params = params or {}
        self.logger = logging.getLogger(f"{__name__}.{name}")
        
        # 依赖注入
        self.cache_manager = cache_manager or CacheManager()
        self.signal_strategy = signal_strategy or DefaultSignalStrengthStrategy()
        
        self.logger.info(f"初始化指标 {name}，参数: {self.params}")
    
    @abstractmethod
    def calculate(self, dataframe: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """
        计算指标值 - 子类必须实现
        
        @param {pd.DataFrame} dataframe - OHLCV数据框
        @param {**kwargs} kwargs - 额外参数
        @returns {pd.DataFrame} 包含指标列的数据框
        """
        pass    

    def _validate_dataframe(self, dataframe: pd.DataFrame) -> bool:
        """
        验证输入数据框的完整性
        
        @param {pd.DataFrame} dataframe - 输入数据框
        @returns {bool} 验证结果
        @private
        """
        if dataframe.empty:
            self.logger.error("数据框为空")
            return False
            
        missing_columns = [col for col in self.REQUIRED_COLUMNS 
                          if col not in dataframe.columns]
        if missing_columns:
            self.logger.error(f"缺少必要列: {missing_columns}")
            return False
            
        # 优化的空值检查 - 使用向量化操作
        null_counts = dataframe[self.REQUIRED_COLUMNS].isnull().sum()
        if null_counts.any():
            self.logger.warning(f"数据中存在空值: {null_counts.to_dict()}")
            
        return True
    
    def _handle_missing_data(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        处理缺失数据
        
        @param {pd.DataFrame} dataframe - 包含缺失数据的数据框
        @returns {pd.DataFrame} 处理后的数据框
        @private
        """
        # 前向填充缺失值
        filled_df = dataframe[self.REQUIRED_COLUMNS].fillna(method='ffill')
        
        # 如果仍有缺失值（开头的数据），使用后向填充
        filled_df = filled_df.fillna(method='bfill')
        
        # 更新原数据框
        result_df = dataframe.copy()
        result_df[self.REQUIRED_COLUMNS] = filled_df
        
        self.logger.debug("已处理缺失数据")
        return result_df
    
    @cache_result
    def safe_calculate(self, dataframe: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """
        安全的指标计算包装器
        包含错误处理和性能优化
        
        @param {pd.DataFrame} dataframe - OHLCV数据框
        @param {**kwargs} kwargs - 额外参数
        @returns {pd.DataFrame} 包含指标的数据框
        """
        try:
            # 数据验证
            if not self._validate_dataframe(dataframe):
                self.logger.error(f"指标 {self.name} 数据验证失败")
                return dataframe
            
            # 处理缺失数据
            clean_dataframe = self._handle_missing_data(dataframe)
            
            # 执行计算
            self.logger.debug(f"开始计算指标 {self.name}")
            result = self.calculate(clean_dataframe, **kwargs)
            
            self.logger.debug(f"指标 {self.name} 计算完成")
            return result
            
        except ValueError as e:
            self.logger.error(f"指标 {self.name} 数值错误: {str(e)}")
            return dataframe
        except KeyError as e:
            self.logger.error(f"指标 {self.name} 键错误: {str(e)}")
            return dataframe
        except Exception as e:
            self.logger.error(f"指标 {self.name} 未知错误: {str(e)}")
            # 在交易系统中，返回原始数据比抛出异常更安全
            return dataframe
    
    def get_signal_strength(self, value: float) -> str:
        """
        获取信号强度 - 使用策略模式
        
        @param {float} value - 指标值
        @returns {str} 信号强度字符串
        """
        return self.signal_strategy.get_strength(value)
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        获取指标性能指标
        
        @returns {Dict[str, Any]} 性能指标字典
        """
        cache_stats = {
            'cache_size': len(self.cache_manager._cache),
            'max_cache_size': self.cache_manager.max_size,
            'cache_ttl': self.cache_manager.ttl_seconds
        }
        
        return {
            'indicator_name': self.name,
            'parameters': self.params,
            'cache_statistics': cache_stats
        }
    
    def clear_cache(self) -> None:
        """
        清空缓存
        
        @description 在内存压力大或数据源变更时使用
        """
        self.cache_manager._cache.clear()
        self.logger.info(f"已清空指标 {self.name} 的缓存")


# 使用示例和测试辅助类
class ExampleRSIIndicator(BaseIndicator):
    """
    示例RSI指标实现
    
    @description 展示如何使用改进的基类
    """
    
    def __init__(self, period: int = 14, **kwargs):
        """
        初始化RSI指标
        
        @param {int} period - RSI计算周期
        """
        super().__init__(
            name=f"RSI_{period}",
            params={'period': period},
            **kwargs
        )
        self.period = period
    
    def calculate(self, dataframe: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """
        计算RSI指标
        
        @param {pd.DataFrame} dataframe - OHLCV数据
        @returns {pd.DataFrame} 包含RSI列的数据框
        """
        result_df = dataframe.copy()
        
        # 使用TA-Lib计算RSI
        result_df[f'rsi_{self.period}'] = ta.RSI(
            dataframe['close'], 
            timeperiod=self.period
        )
        
        self.logger.debug(f"RSI_{self.period} 计算完成")
        return result_df


# 工厂模式示例
class IndicatorFactory:
    """
    指标工厂类
    
    @description 使用工厂模式创建不同类型的指标
    """
    
    _indicators = {
        'rsi': ExampleRSIIndicator,
        # 可以添加更多指标类型
    }
    
    @classmethod
    def create_indicator(cls, 
                        indicator_type: str, 
                        **kwargs) -> BaseIndicator:
        """
        创建指标实例
        
        @param {str} indicator_type - 指标类型
        @param {**kwargs} kwargs - 指标参数
        @returns {BaseIndicator} 指标实例
        @throws {ValueError} 当指标类型不支持时
        """
        if indicator_type not in cls._indicators:
            raise ValueError(f"不支持的指标类型: {indicator_type}")
        
        indicator_class = cls._indicators[indicator_type]
        return indicator_class(**kwargs)
    
    @classmethod
    def get_supported_indicators(cls) -> list:
        """
        获取支持的指标类型列表
        
        @returns {list} 支持的指标类型
        """
        return list(cls._indicators.keys())