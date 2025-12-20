#!/bin/bash

# ============================================
# 远程服务器同步预览脚本
# 仅显示将要同步的文件，不实际执行
# ============================================

# 配置
REMOTE_USER="root"
REMOTE_HOST="67.219.99.40"
REMOTE_PATH="/root/codes/android_reversing"
LOCAL_PATH="$(cd "$(dirname "$0")" && pwd)"

# 颜色输出
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${CYAN}================================${NC}"
echo -e "${CYAN}   同步预览（Dry Run）${NC}"
echo -e "${CYAN}================================${NC}"
echo ""
echo -e "${YELLOW}本地路径:${NC} $LOCAL_PATH"
echo -e "${YELLOW}远程地址:${NC} ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}"
echo ""
echo -e "${YELLOW}以下是将要同步的变更（不会实际执行）:${NC}"
echo ""

# 使用 --dry-run 选项预览
rsync -avzhn --delete \
    --exclude='.git/' \
    --exclude='.DS_Store' \
    --exclude='__pycache__/' \
    --exclude='*.pyc' \
    --exclude='*.pyo' \
    --exclude='*.pyd' \
    --exclude='.Python' \
    --exclude='pip-log.txt' \
    --exclude='pip-delete-this-directory.txt' \
    --exclude='.env' \
    --exclude='.venv' \
    --exclude='venv/' \
    --exclude='ENV/' \
    --exclude='env/' \
    --exclude='site/' \
    --exclude='node_modules/' \
    --exclude='*.egg-info/' \
    --exclude='dist/' \
    --exclude='build/' \
    --exclude='.pytest_cache/' \
    --exclude='.coverage' \
    --exclude='htmlcov/' \
    --exclude='.idea/' \
    --exclude='.vscode/' \
    --exclude='*.swp' \
    --exclude='*.swo' \
    --exclude='*~' \
    --exclude='.claude/' \
    --exclude='output/' \
    --exclude='interviews/' \
    --exclude='test/' \
    --exclude='playground/' \
    "${LOCAL_PATH}/" \
    "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}/"

echo ""
echo -e "${CYAN}提示: 这只是预览，没有实际同步文件${NC}"
echo -e "运行 ${YELLOW}./sync.sh${NC} 来执行实际同步"
echo ""
