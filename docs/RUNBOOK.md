# Runbook

## Deployment

### Docker Deployment (Production)

```bash
# 1. Ensure .env is configured with real credentials
# 2. Verify config_runtime.json has correct settings

# Start
docker compose up -d

# Verify health
docker compose ps
docker compose logs --tail=50 freqtrade

# Health check endpoint
curl http://localhost:8081/api/v1/ping
```

### Docker Security Configuration

The `docker-compose.yml` includes hardened security:

| Setting | Value | Purpose |
|---------|-------|---------|
| `user` | 1000:1000 | Non-root execution |
| `read_only` | true | Read-only filesystem |
| `no-new-privileges` | true | Prevent privilege escalation |
| `cap_drop: ALL` | - | Remove all capabilities |
| Memory limit | 1G (512M reserved) | Prevent OOM |
| CPU limit | 0.5 (0.25 reserved) | Prevent runaway CPU |
| Network | internal bridge (172.20.0.0/16) | No external access |
| Port | expose 8081 (not published) | Internal only |

### Local Deployment

```bash
uv run freqtrade trade \
  --config user_data/config.json \
  --strategy LoopRSIStrategy \
  --logfile user_data/logs/freqtrade.log
```

### Updating

```bash
# Docker
docker compose pull
docker compose up -d

# Local
uv lock --upgrade
uv sync
```

## Monitoring

### Health Check

Docker health check runs automatically every 30s:
```
curl -f http://localhost:8081/api/v1/ping
```

Retries: 3, timeout: 10s, start period: 40s.

### Logs

```bash
# Docker logs
docker compose logs -f freqtrade

# Log file (Docker)
docker compose exec freqtrade cat /freqtrade/logs/freqtrade.log

# Log file (local)
tail -f user_data/logs/freqtrade.log
```

### Telegram Alerts

When configured (`TELEGRAM_TOKEN` + `TELEGRAM_CHAT_ID`), FreqTrade sends automatic notifications for:
- Trade entries/exits
- Daily profit summaries
- Error conditions

### Key Metrics to Watch

- Open trades count vs `max_open_trades` (3)
- Wallet balance and drawdown
- API connectivity to exchange
- Database file size (`tradesv3.sqlite`)

## Common Issues and Fixes

### 1. TA-Lib Import Error

**Symptom**: `ImportError: libta_lib.so.0: cannot open shared object file`

**Fix (macOS)**:
```bash
brew install ta-lib
uv sync --reinstall-package ta-lib
```

**Fix (Docker)**: TA-Lib is included in the base FreqTrade image.

### 2. Exchange API Rate Limiting

**Symptom**: `ccxt.RateLimitExceeded` errors in logs

**Fix**: Adjust `ccxt_config` in config.json:
```json
"ccxt_config": {
    "enableRateLimit": true,
    "rateLimit": 200
}
```

### 3. Database Locked

**Symptom**: `sqlite3.OperationalError: database is locked`

**Fix**: Ensure only one FreqTrade instance accesses `tradesv3.sqlite`. Stop any duplicate processes:
```bash
docker compose down
# or
pkill -f freqtrade
```

### 4. Memory Issues in Docker

**Symptom**: Container killed by OOM

**Fix**: Increase memory limit in `docker-compose.yml`:
```yaml
deploy:
  resources:
    limits:
      memory: 2G
```

### 5. Hyperopt Lock File

**Symptom**: `hyperopt.lock` prevents hyperopt from running

**Fix**:
```bash
rm user_data/hyperopt.lock
```
Only do this if no hyperopt process is actually running.

### 6. Stale Data Cache

**Symptom**: Backtests use outdated data

**Fix**:
```bash
freqtrade download-data --config user_data/config.json \
  --timerange 20240101- --erase
```

### 7. Container Health Check Failing

**Symptom**: `docker compose ps` shows unhealthy

**Fix**:
1. Check if API server is enabled in config
2. Verify port 8081 is correct
3. Check container logs: `docker compose logs freqtrade`

## Rollback Procedures

### Strategy Rollback

```bash
# List available strategies
ls user_data/strategies/*.py

# Change strategy in docker-compose.yml command section
# --strategy LoopRSIStrategy  →  --strategy SampleStrategy

# Restart
docker compose up -d
```

### Configuration Rollback

A config backup exists at `user_data/config.json.backup`:
```bash
cp user_data/config.json.backup user_data/config.json
docker compose restart freqtrade
```

### Docker Image Rollback

```bash
# Pin to specific version in docker-compose.yml
# image: freqtradeorg/freqtrade:stable  →  freqtradeorg/freqtrade:2024.10
docker compose up -d
```

### Database Rollback

SQLite database can be backed up/restored:
```bash
# Backup
cp user_data/tradesv3.sqlite user_data/tradesv3.sqlite.bak

# Restore
docker compose down
cp user_data/tradesv3.sqlite.bak user_data/tradesv3.sqlite
docker compose up -d
```

### Emergency Stop

```bash
# Stop all trading immediately
docker compose down

# or for local
pkill -f freqtrade
```

## Maintenance

### Regular Tasks

- **Weekly**: Download fresh market data for backtesting
- **Monthly**: Review and rotate API keys
- **Quarterly**: Update FreqTrade and dependencies
- **As needed**: Clean up `backtest_results/` and `hyperopt_results/`

### Backup Checklist

| Item | Location | Method |
|------|----------|--------|
| Strategies | `user_data/strategies/` | Git |
| Config | `user_data/config.json` | Manual copy (contains secrets) |
| Trade DB | `user_data/tradesv3.sqlite` | File copy |
| Environment | `.env` | Secure backup (not Git) |
| PineScript | `PineScript/` | Git |
