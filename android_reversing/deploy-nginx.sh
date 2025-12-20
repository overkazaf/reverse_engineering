#!/bin/bash
# Android RE Knowledge Base - Nginx部署脚本
# 自动配置Nginx服务器

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# 加载配置
CONFIG_FILE="sync.conf"

if [ ! -f "$CONFIG_FILE" ]; then
    print_error "配置文件不存在！请先运行 ./sync.sh"
    exit 1
fi

source "$CONFIG_FILE"

# SSH选项
SSH_OPTS="-p $SERVER_PORT"
if [ -n "$SSH_KEY" ] && [ -f "$SSH_KEY" ]; then
    SSH_OPTS="$SSH_OPTS -i $SSH_KEY"
fi

# Nginx配置
SITE_NAME="${SITE_NAME:-android_re_kb}"
DOMAIN="${DOMAIN:-localhost}"
PORT="${NGINX_PORT:-80}"

echo "========================================="
echo "🚀 Nginx 部署配置"
echo "========================================="
print_info "服务器: $SERVER_USER@$SERVER_HOST"
print_info "站点名称: $SITE_NAME"
print_info "域名: $DOMAIN"
print_info "端口: $PORT"
print_info "文档路径: $REMOTE_PATH"
echo "========================================="

# 生成Nginx配置
NGINX_CONFIG="
server {
    listen $PORT;
    server_name $DOMAIN;

    root $REMOTE_PATH;
    index index.html;

    # 日志
    access_log /var/log/nginx/${SITE_NAME}_access.log;
    error_log /var/log/nginx/${SITE_NAME}_error.log;

    # Gzip压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript
               application/x-javascript application/xml+rss
               application/json application/javascript;

    location / {
        try_files \$uri \$uri/ =404;
    }

    # 静态资源缓存
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf)$ {
        expires 30d;
        add_header Cache-Control \"public, immutable\";
    }

    # 安全头
    add_header X-Frame-Options \"SAMEORIGIN\" always;
    add_header X-Content-Type-Options \"nosniff\" always;
    add_header X-XSS-Protection \"1; mode=block\" always;
}
"

# 上传并配置Nginx
print_info "上传Nginx配置到服务器..."

ssh $SSH_OPTS "$SERVER_USER@$SERVER_HOST" "bash -s" << EOF
set -e

# 检查是否安装了Nginx
if ! command -v nginx &> /dev/null; then
    echo "❌ Nginx未安装！"
    echo "安装命令:"
    echo "  Ubuntu/Debian: sudo apt-get update && sudo apt-get install -y nginx"
    echo "  CentOS/RHEL:   sudo yum install -y nginx"
    exit 1
fi

# 创建配置文件
echo "创建Nginx配置..."
echo '$NGINX_CONFIG' | sudo tee /etc/nginx/sites-available/$SITE_NAME > /dev/null

# 启用站点（Debian/Ubuntu）
if [ -d /etc/nginx/sites-enabled ]; then
    sudo ln -sf /etc/nginx/sites-available/$SITE_NAME /etc/nginx/sites-enabled/
fi

# 测试配置
echo "测试Nginx配置..."
sudo nginx -t || {
    echo "❌ Nginx配置测试失败！"
    exit 1
}

# 重载Nginx
echo "重载Nginx..."
sudo systemctl reload nginx || sudo service nginx reload

# 确保Nginx正在运行
sudo systemctl enable nginx 2>/dev/null || true
sudo systemctl start nginx 2>/dev/null || sudo service nginx start

echo "✅ Nginx配置完成！"
EOF

if [ $? -eq 0 ]; then
    print_success "Nginx部署成功！"
    echo ""
    print_info "📝 访问信息:"
    echo "   URL: http://$DOMAIN:$PORT"
    echo ""
    print_info "🔧 常用命令:"
    echo "   查看状态: ssh $SERVER_USER@$SERVER_HOST 'sudo systemctl status nginx'"
    echo "   重启服务: ssh $SERVER_USER@$SERVER_HOST 'sudo systemctl restart nginx'"
    echo "   查看日志: ssh $SERVER_USER@$SERVER_HOST 'sudo tail -f /var/log/nginx/${SITE_NAME}_access.log'"
else
    print_error "Nginx部署失败！"
    exit 1
fi
