#!/bin/bash
# Android RE Knowledge Base - Build & Sync Script
# 先构建MkDocs站点，然后同步到远程服务器
#
# 用法:
#   ./sync-build.sh                                    # 使用配置文件
#   ./sync-build.sh user@server:/path                 # 指定服务器和路径
#   ./sync-build.sh -h server -u user -p /path        # 使用参数

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 显示帮助
show_help() {
    cat << EOF
🚀 Android Reverse Engineering Cookbook - 构建并同步脚本

用法:
  $0 [选项]

选项:
  -h, --host HOST          服务器地址
  -u, --user USER          SSH用户名
  -p, --port PORT          SSH端口（默认22）
  -d, --dir PATH           远程目录路径
  -k, --key KEY_FILE       SSH密钥文件路径
  -c, --config FILE        配置文件路径（默认sync.conf）
  --no-build               跳过构建，只同步site目录
  --help                   显示此帮助信息

快捷用法:
  $0 user@server:/path     # 指定用户@服务器:路径
  $0                       # 使用配置文件

示例:
  $0 -h example.com -u root -d /var/www/html
  $0 root@123.45.67.89:/var/www/kb
  $0 -c my-server.conf

配置文件示例 (sync.conf):
  SERVER_HOST="example.com"
  SERVER_USER="root"
  SERVER_PORT="22"
  REMOTE_PATH="/var/www/html"
  SSH_KEY="~/.ssh/id_rsa"

EOF
    exit 0
}

# 默认值
CONFIG_FILE="sync.conf"
SERVER_HOST=""
SERVER_USER=""
SERVER_PORT="22"
REMOTE_PATH=""
SSH_KEY=""
SKIP_BUILD=false

# 解析命令行参数
parse_args() {
    # 检查是否是快捷格式: user@host:/path
    if [[ $1 =~ ^([^@]+)@([^:]+):(.+)$ ]]; then
        SERVER_USER="${BASH_REMATCH[1]}"
        SERVER_HOST="${BASH_REMATCH[2]}"
        REMOTE_PATH="${BASH_REMATCH[3]}"
        print_info "使用快捷格式: $SERVER_USER@$SERVER_HOST:$REMOTE_PATH"
        return
    fi

    # 解析选项参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--host)
                SERVER_HOST="$2"
                shift 2
                ;;
            -u|--user)
                SERVER_USER="$2"
                shift 2
                ;;
            -p|--port)
                SERVER_PORT="$2"
                shift 2
                ;;
            -d|--dir)
                REMOTE_PATH="$2"
                shift 2
                ;;
            -k|--key)
                SSH_KEY="$2"
                shift 2
                ;;
            -c|--config)
                CONFIG_FILE="$2"
                shift 2
                ;;
            --no-build)
                SKIP_BUILD=true
                shift
                ;;
            --help)
                show_help
                ;;
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

# 如果没有通过命令行指定，则尝试从配置文件加载
if [ -z "$SERVER_HOST" ] || [ -z "$SERVER_USER" ] || [ -z "$REMOTE_PATH" ]; then
    if [ -f "$CONFIG_FILE" ]; then
        print_info "从配置文件加载: $CONFIG_FILE"
        source "$CONFIG_FILE"
    else
        if [ $# -eq 0 ]; then
            print_error "配置文件 $CONFIG_FILE 不存在！"
            print_info "请使用以下方式之一:"
            echo "  1. 创建配置文件: cp sync.conf.example sync.conf"
            echo "  2. 使用命令行参数: $0 user@server:/path"
            echo "  3. 查看帮助: $0 --help"
            exit 1
        fi
    fi
fi

# 验证必要配置
if [ -z "$SERVER_HOST" ] || [ -z "$SERVER_USER" ] || [ -z "$REMOTE_PATH" ]; then
    print_error "配置文件不完整！"
    exit 1
fi

# SSH选项
SSH_OPTS="-p $SERVER_PORT"
if [ -n "$SSH_KEY" ] && [ -f "$SSH_KEY" ]; then
    SSH_OPTS="$SSH_OPTS -i $SSH_KEY"
fi

echo "========================================="
echo "🚀 Android RE Knowledge Base - 构建并同步"
echo "========================================="
print_info "服务器: $SERVER_USER@$SERVER_HOST:$SERVER_PORT"
print_info "远程路径: $REMOTE_PATH"
echo "========================================="

# 检查mkdocs是否安装
if ! command -v mkdocs &> /dev/null; then
    print_error "MkDocs 未安装！"
    print_info "请运行: pip install mkdocs mkdocs-material"
    exit 1
fi

# 清理旧的构建
if [ -d "site" ]; then
    print_info "清理旧的构建文件..."
    rm -rf site
fi

# 构建MkDocs站点
print_info "构建MkDocs站点..."
mkdocs build || {
    print_error "MkDocs 构建失败！"
    exit 1
}
print_success "MkDocs 站点构建完成"

# 检查构建结果
if [ ! -d "site" ]; then
    print_error "构建目录 'site' 不存在！"
    exit 1
fi

# 显示构建统计
SITE_SIZE=$(du -sh site | cut -f1)
FILE_COUNT=$(find site -type f | wc -l | tr -d ' ')
print_info "站点大小: $SITE_SIZE"
print_info "文件数量: $FILE_COUNT"

# 确认同步
read -p "$(echo -e ${YELLOW}确认要同步到服务器吗? [y/N]: ${NC})" -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "已取消同步"
    exit 0
fi

# 测试SSH连接
print_info "测试SSH连接..."
if ! ssh $SSH_OPTS "$SERVER_USER@$SERVER_HOST" "echo 'SSH连接成功'" > /dev/null 2>&1; then
    print_error "SSH连接失败！"
    exit 1
fi
print_success "SSH连接测试通过"

# 确保远程目录存在
print_info "准备远程目录..."
ssh $SSH_OPTS "$SERVER_USER@$SERVER_HOST" "mkdir -p $REMOTE_PATH" || {
    print_error "无法创建远程目录"
    exit 1
}

# 同步站点文件
print_info "同步站点文件到服务器..."
echo "========================================="

rsync -avz --progress \
    -e "ssh $SSH_OPTS" \
    --delete \
    site/ "$SERVER_USER@$SERVER_HOST:$REMOTE_PATH/" || {
    print_error "同步失败！"
    exit 1
}

echo "========================================="
print_success "同步完成！"

# 设置正确的权限（可选）
print_info "设置文件权限..."
ssh $SSH_OPTS "$SERVER_USER@$SERVER_HOST" "
    cd $REMOTE_PATH && \
    find . -type f -exec chmod 644 {} \; && \
    find . -type d -exec chmod 755 {} \;
" || print_warning "权限设置可能失败（可能需要sudo权限）"

echo ""
print_success "✨ MkDocs站点已成功部署到服务器"
print_info "服务器路径: $SERVER_USER@$SERVER_HOST:$REMOTE_PATH"
print_info "站点大小: $SITE_SIZE | 文件数: $FILE_COUNT"

# 显示访问提示
echo ""
print_info "📝 后续步骤:"
echo "   1. 配置Nginx/Apache服务器指向: $REMOTE_PATH"
echo "   2. 或使用Python简单服务器测试:"
echo "      ssh $SERVER_USER@$SERVER_HOST 'cd $REMOTE_PATH && python3 -m http.server 8000'"
echo "   3. 访问: http://$SERVER_HOST:8000"
