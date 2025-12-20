#!/bin/bash

# ============================================
# 远程服务器同步脚本
# 将本地代码同步到远程服务器
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

# 显示标题
echo -e "${CYAN}================================${NC}"
echo -e "${CYAN}   远程服务器同步工具${NC}"
echo -e "${CYAN}================================${NC}"
echo ""
echo -e "${YELLOW}本地路径:${NC} $LOCAL_PATH"
echo -e "${YELLOW}远程地址:${NC} ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}"
echo ""

# 检查 rsync 是否安装
if ! command -v rsync &> /dev/null; then
    echo -e "${RED}错误: rsync 未安装${NC}"
    echo "请先安装 rsync:"
    echo "  macOS: brew install rsync"
    echo "  Ubuntu/Debian: sudo apt-get install rsync"
    echo "  CentOS/RHEL: sudo yum install rsync"
    exit 1
fi

# 测试远程连接
echo -e "${CYAN}[1/3] 测试远程连接...${NC}"
if ! ssh -o ConnectTimeout=5 -o BatchMode=yes ${REMOTE_USER}@${REMOTE_HOST} "echo 'Connection successful'" &> /dev/null; then
    echo -e "${YELLOW}警告: 无法使用 SSH 密钥连接${NC}"
    echo "将需要输入密码（建议配置 SSH 密钥以避免每次输入密码）"
    echo ""
    echo "配置 SSH 密钥的步骤："
    echo "  1. 生成密钥: ssh-keygen -t rsa -b 4096"
    echo "  2. 复制到服务器: ssh-copy-id ${REMOTE_USER}@${REMOTE_HOST}"
    echo ""
else
    echo -e "${GREEN}✓ SSH 连接正常${NC}"
fi

# 创建远程目录（如果不存在）
echo -e "${CYAN}[2/3] 准备远程目录...${NC}"
ssh ${REMOTE_USER}@${REMOTE_HOST} "mkdir -p ${REMOTE_PATH}" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 远程目录准备完成${NC}"
else
    echo -e "${RED}✗ 远程目录创建失败，请检查权限${NC}"
    exit 1
fi

# 同步文件
echo -e "${CYAN}[3/3] 同步文件...${NC}"
echo ""

# rsync 选项说明:
# -a: archive mode (保留权限、时间戳等)
# -v: verbose (显示详细信息)
# -z: compress (压缩传输)
# -h: human-readable (人类可读的格式)
# --progress: 显示进度
# --delete: 删除远程多余文件
# --exclude: 排除不需要同步的文件/目录

rsync -avzh --progress --delete \
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

# 检查同步结果
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}================================${NC}"
    echo -e "${GREEN}✓ 同步完成！${NC}"
    echo -e "${GREEN}================================${NC}"
    echo ""
    echo -e "远程路径: ${CYAN}${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}${NC}"
    echo ""
    echo "快速访问命令:"
    echo -e "  ${YELLOW}ssh ${REMOTE_USER}@${REMOTE_HOST}${NC}"
    echo -e "  ${YELLOW}cd ${REMOTE_PATH}${NC}"
    echo ""
else
    echo ""
    echo -e "${RED}================================${NC}"
    echo -e "${RED}✗ 同步失败${NC}"
    echo -e "${RED}================================${NC}"
    echo ""
    echo "可能的原因："
    echo "  1. 网络连接问题"
    echo "  2. SSH 认证失败"
    echo "  3. 远程服务器磁盘空间不足"
    echo "  4. 权限不足"
    echo ""
    exit 1
fi
