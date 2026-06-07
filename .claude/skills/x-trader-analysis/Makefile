# X Trader Analysis — 一键命令
#
# 用法示例（常态化主力，twscrape 账号池）:
#   make account-add ARGS="--username u1 --cookies 'auth_token=xxx; ct0=yyy'"
#   make account-health
#   make scrape USER=ShanghaoJin SINCE=2023-01-01 UNTIL=2026-05-17
#   make preprocess USER=ShanghaoJin
#   make analyze USER=ShanghaoJin
#   make clean USER=ShanghaoJin
#
# 备用方案（兜底）:
#   make scrape-apify USER=ShanghaoJin SINCE=2023-01-01 UNTIL=2026-05-17
#   make scrape-scweet USER=ShanghaoJin SINCE=2023-01-01 UNTIL=2026-05-17

USER ?= ShanghaoJin
SINCE ?= 2023-01-01
UNTIL ?= 2026-05-17

SCRIPTS_DIR := .claude/skills/x-trader-analysis/scripts
ACCOUNT_POOL_DIR := .claude/skills/x-trader-analysis/.account_pool

.PHONY: help scrape scrape-twscrape scrape-apify scrape-scweet \
        account-add account-health \
        preprocess analyze clean status

help:
	@echo "X Trader Analysis — 可用命令"
	@echo ""
	@echo "  [主力 / 常态化推荐] twscrape 账号池方案 (零边际成本)"
	@echo "  make account-add ARGS=\"--username u1 --cookies 'auth_token=xxx; ct0=yyy'\""
	@echo "    往账号池新增 X 小号 (推荐 cookies 模式)"
	@echo ""
	@echo "  make account-health"
	@echo "    查看账号池所有账号的健康度 (probe 每个号是否可用)"
	@echo ""
	@echo "  make scrape USER=<handle> SINCE=YYYY-MM-DD UNTIL=YYYY-MM-DD"
	@echo "    twscrape 抓取 (默认即 scrape-twscrape，主力命令)"
	@echo ""
	@echo "  [兜底方案]"
	@echo "  make scrape-apify USER=<handle> SINCE=... UNTIL=..."
	@echo "    Apify (一次性大批量, 付费 ~\$$1-2/博主)"
	@echo ""
	@echo "  make scrape-scweet USER=<handle> SINCE=... UNTIL=..."
	@echo "    Scweet 单号 (低频, 需 1 个小号 cookies.json)"
	@echo ""
	@echo "  [pipeline 通用]"
	@echo "  make preprocess USER=<handle>"
	@echo "    清洗 + 实体抽取 + 噪音过滤 + 统计聚合"
	@echo ""
	@echo "  make analyze USER=<handle>"
	@echo "    提示在 Claude Code 中触发 skill 分析 (无脚本入口)"
	@echo ""
	@echo "  make status USER=<handle>"
	@echo "    显示当前 user 的 pipeline 进度"
	@echo ""
	@echo "  make clean USER=<handle>"
	@echo "    清除某个 user 的所有中间产物 (raw + enriched, 保留 report)"
	@echo ""
	@echo "默认参数: USER=$(USER) SINCE=$(SINCE) UNTIL=$(UNTIL)"

# ---------------------------------------------------------------------------
# 主力命令（常态化使用）
# ---------------------------------------------------------------------------

# 默认 scrape 指向 twscrape
scrape: scrape-twscrape

scrape-twscrape:
	@mkdir -p data/raw $(ACCOUNT_POOL_DIR)
	uv run python $(SCRIPTS_DIR)/scrape_twscrape.py \
		--user $(USER) \
		--since $(SINCE) \
		--until $(UNTIL) \
		--max 5000 \
		--out data/raw/$(USER).jsonl

account-add:
	@mkdir -p $(ACCOUNT_POOL_DIR)
	uv run python $(SCRIPTS_DIR)/account_pool/add_account.py $(ARGS)

account-health:
	uv run python $(SCRIPTS_DIR)/account_pool/health_check.py

# ---------------------------------------------------------------------------
# 备用方案（兜底）
# ---------------------------------------------------------------------------

scrape-apify:
	@mkdir -p data/raw
	uv run python $(SCRIPTS_DIR)/scrape_apify.py \
		--user $(USER) \
		--since $(SINCE) \
		--until $(UNTIL) \
		--max 5000 \
		--out data/raw/$(USER).jsonl

scrape-scweet:
	@mkdir -p data/raw
	uv run python $(SCRIPTS_DIR)/scrape_scweet.py \
		--user $(USER) \
		--cookies cookies.json \
		--since $(SINCE) \
		--until $(UNTIL) \
		--max 5000 \
		--out data/raw/$(USER).jsonl

# ---------------------------------------------------------------------------
# pipeline 通用
# ---------------------------------------------------------------------------

preprocess:
	@mkdir -p data/enriched
	uv run python $(SCRIPTS_DIR)/preprocess.py \
		--in data/raw/$(USER).jsonl \
		--out-enriched data/enriched/$(USER).jsonl \
		--out-stats data/enriched/$(USER)_stats.json

analyze:
	@echo ""
	@echo "数据准备完毕, 现在在 Claude Code 中说:"
	@echo ""
	@echo "    用 x-trader-analysis skill 分析 $(USER) 的交易风格"
	@echo ""
	@echo "Claude Code 会按 .claude/skills/x-trader-analysis/SKILL.md 自动执行 4 阶段分析,"
	@echo "5-10 分钟后产出: data/reports/$(USER)_profile_<YYYYMMDD>.md"
	@echo ""

status:
	@echo "X Trader Analysis Pipeline Status — User: $(USER)"
	@echo ""
	@if [ -f data/raw/$(USER).jsonl ]; then \
		echo "  [OK] data/raw/$(USER).jsonl ($$(wc -l < data/raw/$(USER).jsonl) 行)"; \
	else \
		echo "  [MISSING] data/raw/$(USER).jsonl - 请先跑 make scrape (或 scrape-apify / scrape-scweet)"; \
	fi
	@if [ -f data/enriched/$(USER).jsonl ]; then \
		echo "  [OK] data/enriched/$(USER).jsonl ($$(wc -l < data/enriched/$(USER).jsonl) 行)"; \
	else \
		echo "  [MISSING] data/enriched/$(USER).jsonl - 请跑 make preprocess"; \
	fi
	@if [ -f data/enriched/$(USER)_stats.json ]; then \
		echo "  [OK] data/enriched/$(USER)_stats.json"; \
	else \
		echo "  [MISSING] data/enriched/$(USER)_stats.json - 请跑 make preprocess"; \
	fi
	@echo ""
	@echo "已有报告 (data/reports/$(USER)_profile_*.md):"
	@ls -1 data/reports/$(USER)_profile_*.md 2>/dev/null | sed 's/^/  /' || echo "  (无)"
	@echo ""

clean:
	rm -f data/raw/$(USER).jsonl
	rm -f data/enriched/$(USER).jsonl
	rm -f data/enriched/$(USER)_stats.json
	@echo "已清除 $(USER) 的 raw + enriched 中间产物 (报告保留)"
