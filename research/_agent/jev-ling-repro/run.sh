#!/usr/bin/env bash
# 一键跑通「trade the news」最小闭环。
# 用法：bash run.sh [rule|jev]
#   rule（默认）—— 确定性规则替代源，无需密钥，用于验证下游链路
#   jev          —— 真实调用 TypeSafe Jev 1.13，需要 OPENROUTER_API_KEY
set -euo pipefail

SOURCE="${1:-rule}"
NODE="${NODE:-/Users/d0m999/.workbuddy/binaries/node/versions/22.22.2-3/bin/node}"
PY="${PY:-/Library/Frameworks/Python.framework/Versions/3.10/bin/python3}"

for bin in "$NODE" "$PY"; do
  [ -x "$bin" ] || { echo "找不到可执行文件：$bin（可用 NODE= / PY= 覆盖）" >&2; exit 1; }
done

cd "$(dirname "$0")"
echo "==================== 1/5 采集真实数据 ===================="
"$NODE" fetch_data.mjs

echo "==================== 2/5 决策（源：$SOURCE）===================="
"$NODE" decide.mjs --source "$SOURCE"

echo "==================== 3/5 回测 ===================="
"$NODE" backtest.mjs

echo "==================== 4/5 生成仪表盘 ===================="
"$NODE" make_dashboard.mjs

echo "==================== 5/5 逐帧录屏出片 ===================="
"$PY" record.py

echo
echo "产物："
ls -la out/backtest.json out/dashboard.html out/trade-the-news-repro.mp4 2>/dev/null || true
echo
if [ "$SOURCE" = "rule" ]; then
  echo "⚠️  本次决策源是**规则替代**，不是 Jev 1.13；仪表盘也由脚本生成，不是 Ling-3.0-flash-VL 产出。"
  echo "    要接真实模型：export OPENROUTER_API_KEY=sk-or-v1-... 后跑 bash run.sh jev"
fi
