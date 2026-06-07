# 本地开发环境设置指南

## 环境要求

- [uv](https://docs.astral.sh/uv/) (Python 包管理器)
- Python 3.11+（uv 自动安装）
- TA-Lib C 库（macOS 用 Homebrew）

## 安装步骤

### 1. 安装 uv

```bash
# macOS
brew install uv
# 或
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 安装 TA-Lib C 库

```bash
# macOS
brew install ta-lib
```

如果在 Apple Silicon Mac 上编译 ta-lib Python 包失败：
```bash
CFLAGS="-I$(brew --prefix ta-lib)/include" LDFLAGS="-L$(brew --prefix ta-lib)/lib" uv sync
```

### 3. 创建环境并安装依赖

```bash
# 一条命令搞定：创建 .venv、安装 Python 3.11、解析并安装所有依赖
uv sync
```

### 4. 验证安装

```bash
uv run freqtrade --version
uv run freqtrade show-config --config user_data/config.json
```

## 常用命令

所有命令用 `uv run` 前缀，或先激活虚拟环境：

```bash
# 方式一：uv run 前缀
uv run freqtrade backtesting --config user_data/config.json --strategy LoopRSIStrategy

# 方式二：激活虚拟环境后直接运行
source .venv/bin/activate
freqtrade backtesting --config user_data/config.json --strategy LoopRSIStrategy
```

### 回测

```bash
uv run freqtrade backtesting --config user_data/config.json --strategy LoopRSIStrategy
```

### 超参数优化

```bash
uv run freqtrade hyperopt --config user_data/config.json \
  --hyperopt-loss SampleHyperOptLoss \
  --strategy LoopRSIStrategy --epochs 100
```

### 启动交易（模拟模式）

```bash
uv run freqtrade trade --config user_data/config.json --strategy LoopRSIStrategy
```

### 启动 Web UI

```bash
uv run freqtrade webserver --config user_data/config.json
```

## 依赖管理

```bash
# 添加新依赖
uv add <package-name>

# 移除依赖
uv remove <package-name>

# 升级所有依赖
uv lock --upgrade
uv sync

# 升级单个包
uv lock --upgrade-package <package-name>
uv sync
```

依赖定义在 `pyproject.toml`，锁定版本在 `uv.lock`。

## 故障排除

### TA-Lib 安装失败

```bash
# 确保 C 库已安装
brew install ta-lib

# 指定编译路径
CFLAGS="-I$(brew --prefix ta-lib)/include" LDFLAGS="-L$(brew --prefix ta-lib)/lib" uv sync
```

### uv sync 解析失败

```bash
# 清理缓存重试
uv cache clean
uv sync
```

### 网络超时

```bash
UV_HTTP_TIMEOUT=120 uv sync
```

## Docker 对比

本地环境使用 `pyproject.toml` + `uv.lock` 管理依赖（包含 freqtrade 本身）。
Docker 使用 `freqtradeorg/freqtrade:stable` 基础镜像 + `requirements.txt` 安装额外包。

## 注意事项

1. 确保 `user_data/config.json` 中 `dry_run` 设为 `true` 进行模拟交易
2. 在实盘交易前，请充分测试策略
3. 每次使用前记得用 `uv run` 或激活虚拟环境 `source .venv/bin/activate`

<!-- AUTO-GENERATED:START (source: dashboard/README.md) — added 2026-06-08 -->
## Dashboard(可选,交易可视化面板)

仅当需要可视化 OKX 真实交易数据时安装:

```bash
# Dashboard 依赖已在 pyproject.toml 中,uv sync 时已自动安装:
#   streamlit>=1.58.0, plotly>=6.7.0, python-dotenv>=1.2.2

# 1. 配置 OKX 凭据(.env 中追加):
echo 'OKX_API_KEY=your_key' >> .env
echo 'OKX_SECRET=your_secret' >> .env
echo 'OKX_PASSPHRASE=your_pass' >> .env

# 2. 手动触发一次采集以初始化数据库
uv run python dashboard/fetch_trades.py

# 3. 启动 Streamlit 面板
uv run streamlit run dashboard/app.py
# 访问 http://localhost:8501

# 4. 设置每日 02:00 自动采集(可选)
crontab -e
# 追加: 0 2 * * * cd /Users/d0m999/Desktop/vibe-trading && bash dashboard/cron_fetch.sh
```

Dashboard 完全独立于 Freqtrade 交易循环,可随时启用/禁用而不影响策略运行。
详见 `docs/ENV.md` 了解 OKX 凭据配置,`docs/RUNBOOK.md` 了解 Dashboard 监控。
<!-- AUTO-GENERATED:END -->
