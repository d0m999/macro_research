#!/bin/bash

echo "🗑️  正在从Git仓库中删除被忽略的文件..."

# 删除主要的忽略文件夹
echo "删除 .kiro/ 文件夹..."
git rm -r --cached .kiro/ 2>/dev/null || echo "  .kiro/ 不存在或未被跟踪"

echo "删除 .vscode/ 文件夹..."
git rm -r --cached .vscode/ 2>/dev/null || echo "  .vscode/ 不存在或未被跟踪"

echo "删除 pine_indicator/ 文件夹..."
git rm -r --cached pine_indicator/ 2>/dev/null || echo "  pine_indicator/ 不存在或未被跟踪"

# 删除Python相关文件
echo "删除Python缓存文件..."
find . -name "__pycache__" -type d -exec git rm -r --cached {} \; 2>/dev/null || true
find . -name "*.pyc" -exec git rm --cached {} \; 2>/dev/null || true

# 删除日志文件
echo "删除日志文件..."
find . -name "*.log" -exec git rm --cached {} \; 2>/dev/null || true
git rm -r --cached logs/ 2>/dev/null || true
git rm -r --cached user_data/logs/ 2>/dev/null || true

# 删除配置和数据文件
echo "删除配置和数据文件..."
git rm --cached config.json 2>/dev/null || true
git rm --cached config_*.json 2>/dev/null || true
git rm --cached .env 2>/dev/null || true
git rm --cached *.db 2>/dev/null || true
git rm --cached *.sqlite 2>/dev/null || true

# 添加.gitignore并提交
echo "提交更改..."
git add .gitignore
git commit -m "Remove ignored files from repository and update .gitignore

- Removed .kiro/ directory and all contents
- Removed .vscode/ directory and all contents  
- Removed pine_indicator/ directory and all contents
- Removed Python cache files (__pycache__/, *.pyc)
- Removed log files (*.log, logs/)
- Removed config files (config*.json, .env)
- Removed database files (*.db, *.sqlite)
- Updated .gitignore to prevent future tracking"

echo "✅ 清理完成！"
echo ""
echo "📊 当前Git状态："
git status --short

echo ""
echo "🔍 验证：检查是否还有被忽略的文件在跟踪中..."
IGNORED_FILES=$(git ls-files | grep -E "(\.kiro|\.vscode|pine_indicator|__pycache__|\.pyc$|\.log$|config.*\.json$|\.env$|\.db$|\.sqlite$)" || true)

if [ -z "$IGNORED_FILES" ]; then
    echo "✅ 所有被忽略的文件都已从仓库中删除"
else
    echo "⚠️  以下文件仍在被跟踪，可能需要手动删除："
    echo "$IGNORED_FILES"
fi