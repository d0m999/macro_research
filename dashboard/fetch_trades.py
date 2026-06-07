"""
OKX 交易数据采集模块
只读API，自动拉取交易历史并存入SQLite
"""

import ccxt
import sqlite3
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.path.join(os.path.dirname(__file__), 'trades.db')

# 要监控的交易对
SYMBOLS = [
    'BTC/USDT:USDT',
    'ETH/USDT:USDT',
    'SOL/USDT:USDT',
    'RENDER/USDT:USDT',
]


def get_exchange():
    """创建OKX交易所实例"""
    return ccxt.okx({
        'apiKey': os.getenv('OKX_API_KEY'),
        'secret': os.getenv('OKX_SECRET'),
        'password': os.getenv('OKX_PASSPHRASE'),
        'timeout': 30000,
        'enableRateLimit': True,
        'proxies': {
            'http': 'http://127.0.0.1:7897',
            'https': 'http://127.0.0.1:7897',
        },
    })


def init_db():
    """初始化数据库"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 交易记录表
    c.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id TEXT PRIMARY KEY,
            exchange TEXT DEFAULT 'okx',
            symbol TEXT,
            side TEXT,
            price REAL,
            amount REAL,
            cost REAL,
            fee REAL,
            fee_currency TEXT,
            timestamp INTEGER,
            datetime TEXT,
            order_id TEXT,
            pnl REAL,
            raw_json TEXT
        )
    ''')
    
    # 持仓快照表
    c.execute('''
        CREATE TABLE IF NOT EXISTS positions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exchange TEXT DEFAULT 'okx',
            symbol TEXT,
            side TEXT,
            contracts REAL,
            entry_price REAL,
            unrealized_pnl REAL,
            timestamp TEXT
        )
    ''')
    
    # 账户余额快照表
    c.execute('''
        CREATE TABLE IF NOT EXISTS balance_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exchange TEXT DEFAULT 'okx',
            currency TEXT,
            total REAL,
            free REAL,
            used REAL,
            timestamp TEXT
        )
    ''')
    
    conn.commit()
    conn.close()


def fetch_and_store_trades(exchange, symbol, limit=100):
    """拉取并存储交易记录"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    trades = exchange.fetch_my_trades(symbol, limit=limit)
    new_count = 0
    
    for t in trades:
        try:
            c.execute('''
                INSERT OR IGNORE INTO trades 
                (id, exchange, symbol, side, price, amount, cost, fee, fee_currency, 
                 timestamp, datetime, order_id, pnl, raw_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                t['id'],
                'okx',
                t['symbol'],
                t['side'],
                t['price'],
                t['amount'],
                t['cost'],
                t['fee']['cost'],
                t['fee']['currency'],
                t['timestamp'],
                t['datetime'],
                t['order'],
                float(t['info'].get('fillPnl', 0)),
                str(t),
            ))
            if c.rowcount > 0:
                new_count += 1
        except Exception as e:
            print(f"Error inserting trade {t['id']}: {e}")
    
    conn.commit()
    conn.close()
    return new_count, len(trades)


def fetch_and_store_positions(exchange):
    """拉取并存储当前持仓"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    positions = exchange.fetch_positions()
    timestamp = datetime.utcnow().isoformat()
    
    for p in positions:
        if float(p.get('contracts', 0)) > 0:
            c.execute('''
                INSERT INTO positions 
                (exchange, symbol, side, contracts, entry_price, unrealized_pnl, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                'okx',
                p['symbol'],
                p['side'],
                float(p['contracts']),
                float(p['entryPrice'] or 0),
                float(p.get('unrealizedPnl', 0)),
                timestamp,
            ))
    
    conn.commit()
    conn.close()


def fetch_and_store_balance(exchange):
    """拉取并存储账户余额"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    balance = exchange.fetch_balance()
    timestamp = datetime.utcnow().isoformat()
    
    for currency, data in balance['total'].items():
        if data > 0:
            c.execute('''
                INSERT INTO balance_snapshots 
                (exchange, currency, total, free, used, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                'okx',
                currency,
                data,
                balance['free'].get(currency, 0),
                balance['used'].get(currency, 0),
                timestamp,
            ))
    
    conn.commit()
    conn.close()


def run():
    """主采集流程"""
    print(f"[{datetime.now()}] 开始采集OKX数据...")
    
    exchange = get_exchange()
    init_db()
    
    # 1. 采集交易记录
    total_new = 0
    for symbol in SYMBOLS:
        try:
            new, total = fetch_and_store_trades(exchange, symbol)
            total_new += new
            print(f"  {symbol}: {total} 笔交易, 新增 {new} 笔")
        except Exception as e:
            print(f"  {symbol}: 采集失败 - {e}")
    
    # 2. 采集持仓
    fetch_and_store_positions(exchange)
    print("  持仓快照已保存")
    
    # 3. 采集余额
    fetch_and_store_balance(exchange)
    print("  余额快照已保存")
    
    print(f"[{datetime.now()}] 采集完成, 新增 {total_new} 笔交易")
    return total_new


if __name__ == '__main__':
    run()
