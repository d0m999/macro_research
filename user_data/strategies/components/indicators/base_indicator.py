"""
基础指标类 - 为所有自定义指标提供统一接口
遵循加密算法交易开发指南的注释和日志标准
"""

import logging
import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple
import talib.abstract as ta

# 配置Winston风格的日志记录
logger = logging.getLogger(__name__)

class BaseIndicator(ABC):
    """
    自定义指标基类
    
    设计原则：
    1. 统一的接口设计
    2. 完整的错误处理
    3. 性能优化（向量化操作）
    4. 详细的日志记录
    """
    
    def __init__(self, name: str, params: Dict[str, Any] = None):
        """
        初始化指标
        
        Args:
            name: 指标名称
            params: 指标参数字典
        """
        self.name = name
        self.params = params or {}
        self.logger = logging.getLogger(f"{__name__}.{name}")
        
        # 性能缓存
        self._cache = {}
        self._last_update_bar = -1
        
        self.logger.info(f"初始化指标 {name}，参数: {self.params}")
    
    @abstractmethod
    def calculate(self, dataframe: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """
        计算指标值 - 子类必须实现
        
        Args:
            dataframe: OHLCV数据框
            **kwargs: 额外参数
            
        Returns:
            包含指标列的数据框
        """
        pass
    
    def validate_dataframe(self, dataframe: pd.DataFrame) -> bool:
        """
        验证输入数据框的完整性
        
        Args:
            dataframe: 输入数据框
            
        Returns:
            验证结果
        """
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        
        if dataframe.empty:
            self.logger.error("数据框为空")
            return False
            
        missing_columns = [col for col in required_columns if col not in dataframe.columns]
        if missing_columns:
            self.logger.error(f"缺少必要列: {missing_columns}")
            return False
            
        # 检查数据质量
        if dataframe[required_columns].isnull().any().any():
            self.logger.warning("数据中存在空值，将进行前向填充")
            
        return True
    
    def safe_calculate(self, dataframe: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """
        安全的指标计算包装器
        包含错误处理和性能优化
        
        Args:
            dataframe: OHLCV数据框
            **kwargs: 额外参数
            
        Returns:
            包含指标的数据框
        """
        try:
            # 数据验证
            if not self.validate_dataframe(dataframe):
                self.logger.error(f"指标 {self.name} 数据验证失败")
                return dataframe
            
            # 性能优化：检查是否需要重新计算
            current_bar = len(dataframe)
            if (current_bar == self._last_update_bar and 
                self.name in self._cache):
                self.logger.debug(f"使用缓存的 {self.name} 计算结果")
                return self._cache[self.name]
            
            # 执行计算
            self.logger.debug(f"开始计算指标 {self.name}")
            result = self.calculate(dataframe.copy(), **kwargs)
            
            # 缓存结果
            self._cache[self.name] = result
            self._last_update_bar = current_bar
            
            self.logger.debug(f"指标 {self.name} 计算完成")
            return result
            
        except Exception as e:
            self.logger.error(f"指标 {self.name} 计算失败: {str(e)}")
            # 返回原始数据框，避免策略崩溃
            return dataframe
    
    def get_signal_strength(self, value: float, thresholds: Dict[str, float]) -> str:
        """
        根据阈值判断信号强度
        
        Args:
            value: 指标值
            thresholds: 阈值字典 {'strong_bull': 80, 'bull': 60, 'bear': 40, 'strong_bear': 20}
            
        Returns:
            信号强度字符串
        """
        if value >= thresholds.get('strong_bull', 80):
            return 'strong_bullish'
        elif value >= thresholds.get('bull', 60):
            return 'bullish'
        elif value <= thresholds.get('strong_bear', 20):
            return 'strong_bearish'
        elif value <= thresholds.get('bear', 40):
            return 'bearish'
        else:
            return 'neutral'