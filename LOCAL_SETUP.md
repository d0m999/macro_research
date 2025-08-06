# 本地开发环境设置指南

## 环境要求

- Anaconda 或 Miniconda
- Python 3.9 或更高版本

## 安装步骤

### 1. 创建 conda 环境

#### 方法一：使用 environment.yml（推荐）

```bash
# 从 environment.yml 创建环境
conda env create -f environment.yml

# 激活环境
conda activate freqtrade
```

#### 方法二：手动创建环境

```bash
# 创建 conda 环境（指定 Python 版本）
conda create -n freqtrade python=3.11

# 激活环境
conda activate freqtrade

# 安装 TA-Lib（conda-forge 渠道）
conda install -c conda-forge ta-lib

# 使用 pip 安装其他依赖
pip install -r requirements.txt
```

### 2. 验证安装

```bash
# 确保环境已激活
conda activate freqtrade

# 检查 conda 环境
conda info --envs

# 检查已安装的包
conda list

# 检查 FreqTrade 安装
freqtrade --version

# 运行配置检查
freqtrade show-config --config user_data/config.json
```

## 常用命令

### 回测
```bash
freqtrade backtesting --config user_data/config.json --strategy SampleStrategy
```

### 超参数优化
```bash
freqtrade hyperopt --config user_data/config.json --hyperopt-loss SampleHyperOptLoss --strategy SampleStrategy --epochs 100
```

### 启动交易（模拟模式）
```bash
freqtrade trade --config user_data/config.json --strategy SampleStrategy
```

### 启动 Web UI
```bash
freqtrade webserver --config user_data/config.json
```

## 环境管理

### 常用 conda 命令

```bash
# 激活环境
conda activate freqtrade

# 停用环境
conda deactivate

# 查看所有环境
conda env list

# 更新环境（从 environment.yml）
conda env update -f environment.yml

# 导出当前环境
conda env export > environment_backup.yml

# 删除环境
conda env remove -n freqtrade
```

### 包管理

```bash
# 安装新包（优先使用 conda）
conda install -c conda-forge package_name

# 如果 conda 没有，使用 pip
pip install package_name

# 更新包
conda update package_name
pip install --upgrade package_name
```

## 故障排除

### 环境创建失败

如果 `conda env create -f environment.yml` 失败，尝试以下方法：

```bash
# 方法1：更新 conda
conda update conda

# 方法2：清理缓存
conda clean --all

# 方法3：手动创建环境
conda create -n freqtrade python=3.11
conda activate freqtrade
conda install -c conda-forge ta-lib numpy pandas scikit-learn scipy matplotlib requests jupyter
pip install -r requirements.txt
```

### TA-Lib 安装问题

如果 TA-Lib 安装失败：

```bash
# macOS 用户
brew install ta-lib
pip install TA-Lib

# 或者使用 conda
conda install -c conda-forge ta-lib
```

## 注意事项

1. 确保 `user_data/config.json` 中的 `dry_run` 设置为 `true` 进行模拟交易
2. 在实盘交易前，请充分测试策略
3. 定期更新依赖包以获得最新功能和安全修复
4. 使用 conda 时，优先从 conda-forge 渠道安装包，避免版本冲突
5. 每次使用前记得激活 conda 环境：`conda activate freqtrade`
6. 如果遇到包版本冲突，可以删除环境重新创建

## Docker 对比

本地环境与 Docker 环境使用相同的包版本，确保一致性：
- FreqTrade 基础镜像：`freqtradeorg/freqtrade:stable`
- Python 包版本与 requirements.txt 和 environment.yml 保持同步
- conda 环境提供更好的依赖管理和版本控制