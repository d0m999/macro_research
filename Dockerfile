# 基于 FreqTrade 官方镜像
FROM freqtradeorg/freqtrade:stable

# 设置工作目录
WORKDIR /freqtrade

# 复制并安装额外的 Python 包
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制用户数据和策略文件
COPY user_data/ /freqtrade/user_data/

# 暴露 API 端口
EXPOSE 8080

# 默认命令 - 可以通过 docker-compose.yml 覆盖
CMD ["freqtrade", "trade", "--config", "/freqtrade/user_data/config.json"]