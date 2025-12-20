#!/bin/bash

# ============================================
# 远程服务器增量同步脚本
# 只上传新文件和修改的文件，不删除远程文件
# ============================================

# 配置
REMOTE_USER="root"
REMOTE_HOST="67.219.99.40"
REMOTE_PATH="/root/codes/android_reversing"
LOCAL_PATH="$(cd "$(dirname "$0")" && pwd)"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}================================${NC}"
echo -e "${CYAN}   增量同步模式${NC}"
echo -e "${CYAN}================================${NC}"
echo ""
echo -e "${YELLOW}本地路径:${NC} $LOCAL_PATH"
echo -e "${YELLOW}远程地址:${NC} ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}"
echo -e "${YELLOW}模式:${NC} 增量（不删除远程文件）"
echo ""

# 检查 rsync 是否安装
if ! command -v rsync &> /dev/null; then
    echo -e "${RED}错误: rsync 未安装${NC}"
    exit 1
fi

# 创建远程目录
echo -e "${CYAN}[1/2] 准备远程目录...${NC}"
ssh ${REMOTE_USER}@${REMOTE_HOST} "mkdir -p ${REMOTE_PATH}" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 远程目录准备完成${NC}"
else
    echo -e "${RED}✗ 远程目录创建失败${NC}"
    exit 1
fi

# 同步文件（不使用 --delete 选项）
echo -e "${CYAN}[2/2] 同步文件...${NC}"
echo ""

rsync -avzh --progress \
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

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}================================${NC}"
    echo -e "${GREEN}✓ 增量同步完成！${NC}"
    echo -e "${GREEN}================================${NC}"
    echo ""
else
    echo ""
    echo -e "${RED}✗ 同步失败${NC}"
    echo ""
    exit 1
fi
