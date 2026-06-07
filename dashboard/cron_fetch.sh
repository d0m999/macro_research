#!/bin/bash
# OKX 交易数据定时采集脚本
# 每天凌晨2点运行，采集最新交易数据

cd /Users/d0m999/Desktop/vibe-trading
export PATH="/Users/d0m999/.local/bin:$PATH"

echo "[$(date)] 开始采集OKX交易数据..."
uv run python dashboard/fetch_trades.py

echo "[$(date)] 采集完成"
