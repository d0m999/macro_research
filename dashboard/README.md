# 交易数据面板

## 快速开始

### 启动面板
```bash
cd /Users/d0m999/Desktop/vibe-trading
uv run streamlit run dashboard/app.py
```
访问: http://localhost:8501

### 手动采集数据
```bash
uv run python dashboard/fetch_trades.py
```

## 定时采集

已配置 cron 任务：**每天凌晨 2:00** 自动采集

查看采集日志：
```bash
tail -f dashboard/cron.log
```

查看定时任务：
```bash
crontab -l
```

## 文件说明

| 文件 | 说明 |
|------|------|
| `fetch_trades.py` | 数据采集脚本 |
| `app.py` | Streamlit 面板 |
| `cron_fetch.sh` | 定时采集脚本 |
| `trades.db` | SQLite 数据库 |
| `cron.log` | 采集日志 |

## 数据保留

- OKX API 最多返回 **3 个月**历史数据
- 本地数据库 **永久保存**
- 建议持续运行定时任务，积累历史数据
