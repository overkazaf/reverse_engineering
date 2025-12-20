#!/bin/bash
# Android RE Knowledge Base - Sync Only Script
# 只同步文件，不构建
#
# 用法:
#   ./sync-only.sh                     # 使用配置文件
#   ./sync-only.sh user@server:/path   # 指定服务器和路径
#   ./sync-only.sh -h server -u user -d /path -s site  # 同步site目录

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

show_help() {
    cat << 'HELP'
🚀 Android RE Cookbook - 仅同步脚本（不构建）

用法:
  ./sync-only.sh [选项]

选项:
  -h, --host HOST          服务器地址
  -u, --user USER          SSH用户名
  -p, --port PORT          SSH端口（默认22）
  -d, --dir PATH           远程目录路径
  -s, --source DIR         本地源目录（默认: 当前目录）
  -k, --key FILE           SSH密钥文件
  -c, --config FILE        配置文件（默认sync.conf）
  --help                   显示帮助

快捷格式:
  ./sync-only.sh user@server:/path

同步选项:
  --site                   只同步site目录（已构建的静态文件）
  --docs                   只同步docs目录
  --all                    同步整个项目（默认）

示例:
  # 只同步site目录（已构建的静态站点）
  ./sync-only.sh --site user@server:/var/www/html

  # 同步整个项目源码
  ./sync-only.sh --all root@server:/var/www/kb

  # 只同步docs目录
  ./sync-only.sh --docs root@server:/path

  # 指定本地源目录
  ./sync-only.sh -s ./site root@server:/var/www/html

HELP
    exit 0
}

# 默认值
CONFIG_FILE="sync.conf"
SERVER_HOST=""
SERVER_USER=""
SERVER_PORT="22"
REMOTE_PATH=""
SSH_KEY=""
SOURCE_DIR="."
SYNC_MODE="all"

# 解析参数
parse_args() {
    if [[ $1 =~ ^([^@]+)@([^:]+):(.+)$ ]]; then
        SERVER_USER="${BASH_REMATCH[1]}"
        SERVER_HOST="${BASH_REMATCH[2]}"
        REMOTE_PATH="${BASH_REMATCH[3]}"
        print_info "使用快捷格式: $SERVER_USER@$SERVER_HOST:$REMOTE_PATH"
        return
    fi

    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--host) SERVER_HOST="$2"; shift 2 ;;
            -u|--user) SERVER_USER="$2"; shift 2 ;;
            -p|--port) SERVER_PORT="$2"; shift 2 ;;
            -d|--dir) REMOTE_PATH="$2"; shift 2 ;;
            -s|--source) SOURCE_DIR="$2"; shift 2 ;;
            -k|--key) SSH_KEY="$2"; shift 2 ;;
            -c|--config) CONFIG_FILE="$2"; shift 2 ;;
            --site) SYNC_MODE="site"; shift ;;
            --docs) SYNC_MODE="docs"; shift ;;
            --all) SYNC_MODE="all"; shift ;;
            --help) show_help ;;
            *)
                print_error "未知选项: $1"
                echo "使用 --help 查看帮助"
                exit 1
                ;;
        esac
    done
}

# 解析参数
if [ $# -gt 0 ]; then
    parse_args "$@"
fi

# 从配置文件加载
if [ -z "$SERVER_HOST" ] || [ -z "$SERVER_USER" ] || [ -z "$REMOTE_PATH" ]; then
    if [ -f "$CONFIG_FILE" ]; then
        print_info "从配置文件加载: $CONFIG_FILE"
        source "$CONFIG_FILE"
    else
        if [ $# -eq 0 ]; then
            print_error "配置文件不存在且未指定服务器信息"
            print_info "使用方式:"
            echo "  1. ./sync-only.sh user@server:/path"
            echo "  2. ./sync-only.sh --help"
            exit 1
        fi
    fi
fi

# 验证配置
if [ -z "$SERVER_HOST" ] || [ -z "$SERVER_USER" ] || [ -z "$REMOTE_PATH" ]; then
    print_error "服务器信息不完整！"
    exit 1
fi

# 确定同步源目录
case $SYNC_MODE in
    site)
        if [ ! -d "site" ]; then
            print_error "site目录不存在！请先运行: mkdocs build"
            exit 1
        fi
        SOURCE_DIR="site"
        print_info "同步模式: 只同步site目录（静态文件）"
        ;;
    docs)
        if [ ! -d "docs" ]; then
            print_error "docs目录不存在！"
            exit 1
        fi
        SOURCE_DIR="docs"
        print_info "同步模式: 只同步docs目录（源文件）"
        ;;
    all)
        SOURCE_DIR="."
        print_info "同步模式: 同步整个项目"
        ;;
esac

# SSH选项
SSH_OPTS="-p $SERVER_PORT"
if [ -n "$SSH_KEY" ] && [ -f "$SSH_KEY" ]; then
    SSH_OPTS="$SSH_OPTS -i $SSH_KEY"
fi

# 排除模式
EXCLUDE_ARGS="--exclude=.git --exclude=.DS_Store --exclude=__pycache__ --exclude=*.pyc --exclude=.vscode --exclude=.idea --exclude=*.log"

echo "========================================="
echo "🚀 仅同步模式 - 不构建"
echo "========================================="
print_info "服务器: $SERVER_USER@$SERVER_HOST:$SERVER_PORT"
print_info "远程路径: $REMOTE_PATH"
print_info "本地源: $SOURCE_DIR"
echo "========================================="

# 确认
read -p "$(echo -e ${YELLOW}确认同步? [y/N]: ${NC})" -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "已取消"
    exit 0
fi

# 测试SSH
print_info "测试SSH连接..."
if ! ssh $SSH_OPTS "$SERVER_USER@$SERVER_HOST" "echo 'OK'" > /dev/null 2>&1; then
    print_error "SSH连接失败"
    exit 1
fi
print_success "SSH连接成功"

# 确保远程目录存在
print_info "准备远程目录..."
ssh $SSH_OPTS "$SERVER_USER@$SERVER_HOST" "mkdir -p $REMOTE_PATH"

# 同步
print_info "开始同步..."
echo "========================================="

rsync -avz --progress \
    -e "ssh $SSH_OPTS" \
    $EXCLUDE_ARGS \
    --delete \
    "$SOURCE_DIR/" "$SERVER_USER@$SERVER_HOST:$REMOTE_PATH/" || {
    print_error "同步失败"
    exit 1
}

echo "========================================="
print_success "同步完成！"
print_info "服务器: $SERVER_USER@$SERVER_HOST:$REMOTE_PATH"

# 设置权限
if [ "$SYNC_MODE" = "site" ]; then
    print_info "设置文件权限..."
    ssh $SSH_OPTS "$SERVER_USER@$SERVER_HOST" "
        cd $REMOTE_PATH && \
        find . -type f -exec chmod 644 {} \; && \
        find . -type d -exec chmod 755 {} \;
    " 2>/dev/null || print_warning "权限设置可能需要sudo"
fi

print_success "✨ 同步任务完成"
