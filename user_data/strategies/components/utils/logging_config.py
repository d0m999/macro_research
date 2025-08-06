"""
Winston风格的日志配置
为量化交易策略提供专业级日志管理

功能特性：
1. 多级别日志记录
2. 结构化日志格式
3. 性能监控
4. 交易操作审计
"""

import logging
import logging.handlers
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

class StructuredFormatter(logging.Formatter):
    """
    结构化日志格式器
    输出JSON格式的日志，便于分析和监控
    """
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # 添加额外的上下文信息
        if hasattr(record, 'pair'):
            log_entry['pair'] = record.pair
        if hasattr(record, 'trade_id'):
            log_entry['trade_id'] = record.trade_id
        if hasattr(record, 'strategy'):
            log_entry['strategy'] = record.strategy
        if hasattr(record, 'performance_data'):
            log_entry['performance'] = record.performance_data
        
        # 异常信息
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry, ensure_ascii=False)

class TradingLogger:
    """
    交易专用日志管理器
    提供不同类型的日志记录功能
    """
    
    def __init__(self, strategy_name: str, log_dir: str = "user_data/logs"):
        """
        初始化交易日志器
        
        Args:
            strategy_name: 策略名称
            log_dir: 日志目录
        """
        self.strategy_name = strategy_name
        self.log_dir = log_dir
        
        # 确保日志目录存在
        os.makedirs(log_dir, exist_ok=True)
        
        # 设置不同类型的日志器
        self._setup_loggers()
    
    def _setup_loggers(self):
        """设置各种日志器"""
        
        # 主策略日志器
        self.strategy_logger = self._create_logger(
            f"{self.strategy_name}.strategy",
            f"{self.log_dir}/{self.strategy_name}_strategy.log",
            logging.INFO
        )
        
        # 交易操作日志器
        self.trade_logger = self._create_logger(
            f"{self.strategy_name}.trades",
            f"{self.log_dir}/{self.strategy_name}_trades.log",
            logging.INFO
        )
        
        # 性能监控日志器
        self.performance_logger = self._create_logger(
            f"{self.strategy_name}.performance",
            f"{self.log_dir}/{self.strategy_name}_performance.log",
            logging.DEBUG
        )
        
        # 错误日志器
        self.error_logger = self._create_logger(
            f"{self.strategy_name}.errors",
            f"{self.log_dir}/{self.strategy_name}_errors.log",
            logging.ERROR
        )
        
        # 调试日志器
        self.debug_logger = self._create_logger(
            f"{self.strategy_name}.debug",
            f"{self.log_dir}/{self.strategy_name}_debug.log",
            logging.DEBUG
        )
    
    def _create_logger(self, name: str, filename: str, level: int) -> logging.Logger:
        """
        创建单个日志器
        
        Args:
            name: 日志器名称
            filename: 日志文件名
            level: 日志级别
            
        Returns:
            配置好的日志器
        """
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        # 避免重复添加处理器
        if logger.handlers:
            return logger
        
        # 文件处理器（带轮转）
        file_handler = logging.handlers.RotatingFileHandler(
            filename,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(StructuredFormatter())
        logger.addHandler(file_handler)
        
        # 控制台处理器（仅错误级别以上）
        if level >= logging.ERROR:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.ERROR)
            console_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)
        
        return logger
    
    def log_strategy_event(self, message: str, level: str = "INFO", **kwargs):
        """
        记录策略事件
        
        Args:
            message: 日志消息
            level: 日志级别
            **kwargs: 额外的上下文信息
        """
        logger_method = getattr(self.strategy_logger, level.lower())
        
        # 添加上下文信息到日志记录
        extra = {'strategy': self.strategy_name}
        extra.update(kwargs)
        
        logger_method(message, extra=extra)
    
    def log_trade_operation(self, operation: str, pair: str, 
                          trade_data: Dict[str, Any], **kwargs):
        """
        记录交易操作
        
        Args:
            operation: 操作类型 (entry, exit, adjustment)
            pair: 交易对
            trade_data: 交易数据
            **kwargs: 额外信息
        """
        message = f"交易操作: {operation} - {pair}"
        
        extra = {
            'strategy': self.strategy_name,
            'pair': pair,
            'operation': operation,
            'trade_data': trade_data
        }
        extra.update(kwargs)
        
        self.trade_logger.info(message, extra=extra)
    
    def log_performance_metric(self, metric_name: str, value: float, 
                             pair: Optional[str] = None, **kwargs):
        """
        记录性能指标
        
        Args:
            metric_name: 指标名称
            value: 指标值
            pair: 交易对（可选）
            **kwargs: 额外信息
        """
        message = f"性能指标: {metric_name} = {value}"
        
        extra = {
            'strategy': self.strategy_name,
            'metric_name': metric_name,
            'metric_value': value,
            'performance_data': {metric_name: value}
        }
        
        if pair:
            extra['pair'] = pair
        
        extra.update(kwargs)
        
        self.performance_logger.info(message, extra=extra)
    
    def log_error(self, error_message: str, exception: Optional[Exception] = None, 
                  **kwargs):
        """
        记录错误信息
        
        Args:
            error_message: 错误消息
            exception: 异常对象（可选）
            **kwargs: 额外信息
        """
        extra = {'strategy': self.strategy_name}
        extra.update(kwargs)
        
        if exception:
            self.error_logger.error(error_message, exc_info=exception, extra=extra)
        else:
            self.error_logger.error(error_message, extra=extra)
    
    def log_debug(self, debug_message: str, **kwargs):
        """
        记录调试信息
        
        Args:
            debug_message: 调试消息
            **kwargs: 额外信息
        """
        extra = {'strategy': self.strategy_name}
        extra.update(kwargs)
        
        self.debug_logger.debug(debug_message, extra=extra)

# 全局日志管理器实例
_loggers: Dict[str, TradingLogger] = {}

def get_trading_logger(strategy_name: str) -> TradingLogger:
    """
    获取交易日志器实例（单例模式）
    
    Args:
        strategy_name: 策略名称
        
    Returns:
        交易日志器实例
    """
    if strategy_name not in _loggers:
        _loggers[strategy_name] = TradingLogger(strategy_name)
    
    return _loggers[strategy_name]

def log_trade_entry(strategy_name: str, pair: str, side: str, 
                   amount: float, rate: float, **kwargs):
    """
    便捷函数：记录交易入场
    """
    logger = get_trading_logger(strategy_name)
    trade_data = {
        'side': side,
        'amount': amount,
        'rate': rate,
        'timestamp': datetime.now().isoformat()
    }
    trade_data.update(kwargs)
    
    logger.log_trade_operation('entry', pair, trade_data)

def log_trade_exit(strategy_name: str, pair: str, side: str, 
                  amount: float, rate: float, profit: float, **kwargs):
    """
    便捷函数：记录交易出场
    """
    logger = get_trading_logger(strategy_name)
    trade_data = {
        'side': side,
        'amount': amount,
        'rate': rate,
        'profit': profit,
        'timestamp': datetime.now().isoformat()
    }
    trade_data.update(kwargs)
    
    logger.log_trade_operation('exit', pair, trade_data)

def log_signal_generation(strategy_name: str, pair: str, signal_type: str, 
                         signal_strength: float, **kwargs):
    """
    便捷函数：记录信号生成
    """
    logger = get_trading_logger(strategy_name)
    logger.log_strategy_event(
        f"信号生成: {signal_type} - 强度: {signal_strength}",
        pair=pair,
        signal_type=signal_type,
        signal_strength=signal_strength,
        **kwargs
    )

def log_risk_event(strategy_name: str, event_type: str, description: str, 
                  severity: str = "WARNING", **kwargs):
    """
    便捷函数：记录风险事件
    """
    logger = get_trading_logger(strategy_name)
    
    if severity.upper() == "ERROR":
        logger.log_error(f"风险事件: {event_type} - {description}", **kwargs)
    else:
        logger.log_strategy_event(
            f"风险事件: {event_type} - {description}",
            level=severity.upper(),
            event_type=event_type,
            **kwargs
        )