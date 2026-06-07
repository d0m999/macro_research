# Environment Variables

> Source of truth: `.env.example` (template) → `.env` (real values, gitignored)
> Last updated: 2026-06-08

## Quick Start

```bash
# Copy template and fill in real values
cp .env.example .env
# Generate secrets (run each):
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_hex(32))"
python -c "import secrets; print('WS_TOKEN=' + secrets.token_hex(16))"
python -c "import secrets; from base64 import b64encode; print('API_PASSWORD=' + b64encode(secrets.token_bytes(24)).decode())"
# Edit .env, replace placeholders
chmod 600 .env
```

## Variable Reference

| Variable | Required | Used By | Description | Example |
|----------|----------|---------|-------------|---------|
| `EXCHANGE_API_KEY` | Yes* | Freqtrade | Binance API key (futures read+trade) | `vmPUlLvYQK...` |
| `EXCHANGE_API_SECRET` | Yes* | Freqtrade | Binance API secret | `N0TgI3wZ...` |
| `JWT_SECRET_KEY` | Yes | Freqtrade API | JWT signing key (HS256) | 64-char hex |
| `WS_TOKEN` | Yes | Freqtrade API | WebSocket auth token | 32-char hex |
| `API_USERNAME` | Yes | Freqtrade API | HTTP Basic Auth username | `freqtrader_secure` |
| `API_PASSWORD` | Yes | Freqtrade API | HTTP Basic Auth password | Base64 string |
| `TELEGRAM_TOKEN` | No | Freqtrade notify | Telegram bot token | `bot_id:auth_token` |
| `TELEGRAM_CHAT_ID` | No | Freqtrade notify | Target chat ID | `123456789` |
| `DB_URL` | Yes | Freqtrade | SQLite connection URI | `sqlite:///user_data/tradesv3.sqlite` |
| `OKX_API_KEY` | **Yes (new)** | Dashboard sync | OKX read-only API key (UUID) | `5f55d409-860a-4d88-...` |
| `OKX_SECRET` | **Yes (new)** | Dashboard sync | OKX API secret (hex) | `CBB53A75644B3F94...` |
| `OKX_PASSPHRASE` | **Yes (new)** | Dashboard sync | OKX API passphrase | user-defined |

`*` Only required for live trading. `dry_run: true` accepts placeholder values.

## Variable Grouping

### Group 1: Exchange (Binance) — Live trading
- `EXCHANGE_API_KEY` + `EXCHANGE_API_SECRET`
- Required permissions: **Read + Spot/Futures Trade**
- IP whitelist recommended

### Group 2: API Server Auth — Freqtrade webserver @ :8081
- `JWT_SECRET_KEY` (64 hex), `WS_TOKEN` (32 hex), `API_USERNAME`, `API_PASSWORD` (base64)
- All four required for the API to start
- Rotate `JWT_SECRET_KEY` triggers all users to re-login

### Group 3: Notifications — Optional
- `TELEGRAM_TOKEN` + `TELEGRAM_CHAT_ID`
- Both required together (token alone is useless)
- Test with: `freqtrade test-pairlist` (no, use Telegram test in config)

### Group 4: Database — Required
- `DB_URL` defaults to `sqlite:////freqtrade/user_data/tradesv3.sqlite` in Docker
- Local dev: `sqlite:///user_data/tradesv3.sqlite` (3 slashes = relative)
- Do NOT change DB type without migration plan (Freqtrade assumes SQLite)

### Group 5: OKX Dashboard (NEW) — Read-only
- `OKX_API_KEY` + `OKX_SECRET` + `OKX_PASSPHRASE`
- **MUST be Read-Only permission only** (no trade/withdraw)
- Used by `dashboard/fetch_trades.py` via ccxt
- Cron schedule: daily 02:00 (`dashboard/cron_fetch.sh`)

## Security Checklist

- [ ] `.env` is in `.gitignore` (verified: line 1-5 of `.gitignore`)
- [ ] `.env` file permissions are `600` (owner read/write only)
- [ ] OKX API key has **Read-Only** permission, no trade
- [ ] Exchange API key has IP whitelist
- [ ] Secrets are not in any committed file (`git grep -E "(KEY|SECRET|TOKEN)=" .`)
- [ ] No secrets in `user_data/config.json` (uses `${ENV_VAR}` placeholders)
- [ ] `JWT_SECRET_KEY` rotated on team member change

## Where Each Var Is Referenced

| Variable | Referenced In |
|----------|---------------|
| `EXCHANGE_API_KEY` | `user_data/config.json:35` (`"key": "${EXCHANGE_API_KEY}"`) |
| `EXCHANGE_API_SECRET` | `user_data/config.json:36` |
| `JWT_SECRET_KEY` | `user_data/config.json:61` |
| `WS_TOKEN` | `user_data/config.json:62` |
| `API_USERNAME` | `user_data/config.json:64` |
| `API_PASSWORD` | `user_data/config.json:65` |
| `TELEGRAM_TOKEN` | `user_data/config.json:52` |
| `TELEGRAM_CHAT_ID` | `user_data/config.json:53` |
| `OKX_API_KEY` | `dashboard/fetch_trades.py:28` (`os.getenv('OKX_API_KEY')`) |
| `OKX_SECRET` | `dashboard/fetch_trades.py:29` |
| `OKX_PASSPHRASE` | `dashboard/fetch_trades.py:30` |

## Rotation Policy

| Var | Rotation Frequency | Impact |
|-----|-------------------|--------|
| `EXCHANGE_API_KEY/SECRET` | 90 days | Need to update both `user_data/config.json` and `docker-compose.yml` secrets |
| `JWT_SECRET_KEY` | 180 days | All API/WS sessions invalidated |
| `WS_TOKEN` | 180 days | All WebSocket clients disconnected |
| `API_PASSWORD` | 90 days | All HTTP Basic sessions invalidated |
| `OKX_API_KEY/SECRET/PASSPHRASE` | 180 days | Dashboard sync breaks until updated |
| `TELEGRAM_TOKEN` | On compromise | Notifications stop |

## Related Files

- `.env.example` — Template (committed)
- `.env` — Real values (gitignored, mode 600)
- `.gitignore` — Excludes `.env`
- `SECURITY-GUIDE.md` — 65KB security manual
