# 🚀 同步部署脚本使用指南

## 📋 可用脚本

已为你创建了以下部署脚本：

### 1. sync-build.sh - 构建并同步（推荐）
**功能**: 本地构建MkDocs站点，然后同步到服务器
**适用**: 生产环境部署

```bash
./sync-build.sh
```

### 2. deploy-nginx.sh - Nginx自动配置
**功能**: 自动配置Nginx Web服务器
**适用**: 生产环境，需要域名访问

```bash
./deploy-nginx.sh
```

### 3. sync.sh - 源码同步（已存在）
**功能**: 同步整个项目到服务器
**适用**: 开发环境

---

## 🎯 快速开始

### 第一步: 创建配置文件

运行任一脚本会自动创建 `sync.conf`:

```bash
./sync-build.sh
```

### 第二步: 编辑配置

编辑生成的 `sync.conf` 文件：

```bash
# 服务器配置
SERVER_HOST="your-server.com"       # 你的服务器地址
SERVER_USER="username"              # SSH用户名
SERVER_PORT="22"                    # SSH端口
REMOTE_PATH="/var/www/html"         # 远程部署路径

# SSH密钥（可选）
SSH_KEY="~/.ssh/id_rsa"

# Nginx配置（可选）
SITE_NAME="android_re_kb"
DOMAIN="your-domain.com"
NGINX_PORT="80"
```

### 第三步: 部署

#### 方案A: 快速部署（静态站点）

```bash
# 1. 构建并同步
./sync-build.sh

# 2. 配置Nginx
./deploy-nginx.sh

# 3. 访问
# http://your-domain.com
```

#### 方案B: 开发环境

```bash
# 使用现有的sync.sh同步源码
./sync.sh

# SSH到服务器启动开发服务器
ssh username@server
cd /var/www/html
mkdocs serve -a 0.0.0.0:8000
```

---

## 📖 详细说明

### sync-build.sh 工作流程

1. ✅ 检查MkDocs是否安装
2. ✅ 清理旧构建
3. ✅ 构建静态站点到 `site/` 目录
4. ✅ 测试SSH连接
5. ✅ 使用rsync同步到服务器
6. ✅ 设置正确的文件权限

### deploy-nginx.sh 工作流程

1. ✅ 生成优化的Nginx配置
2. ✅ 上传配置到服务器
3. ✅ 测试Nginx配置
4. ✅ 重载Nginx服务
5. ✅ 提供访问信息

---

## 🔧 配置示例

### 完整的 sync.conf 示例

```bash
# ===== 服务器配置 =====
SERVER_HOST="example.com"
SERVER_USER="root"
SERVER_PORT="22"
REMOTE_PATH="/var/www/android_re_kb"

# SSH密钥路径（推荐使用密钥认证）
SSH_KEY="~/.ssh/id_rsa"

# ===== Nginx配置 =====
SITE_NAME="android_re_kb"
DOMAIN="kb.example.com"
NGINX_PORT="80"

# ===== 排除文件 =====
EXCLUDE_PATTERNS=(
    ".git"
    ".gitignore"
    ".DS_Store"
    "__pycache__"
    "*.pyc"
    ".vscode"
    ".idea"
    "node_modules"
    ".venv"
    "venv"
    "*.log"
    "output"
)
```

---

## 🌐 部署后配置

### 使用简单HTTP服务器（测试）

```bash
ssh username@server
cd /var/www/android_re_kb
python3 -m http.server 8000
```

访问: `http://your-server:8000`

### 使用Nginx（生产）

```bash
# 自动配置
./deploy-nginx.sh

# 或手动配置
ssh username@server
sudo nano /etc/nginx/sites-available/android_re_kb
sudo ln -s /etc/nginx/sites-available/android_re_kb /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

访问: `http://your-domain.com`

### 配置HTTPS（可选）

```bash
ssh username@server

# 安装certbot
sudo apt-get install certbot python3-certbot-nginx

# 获取SSL证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

---

## 💡 常用命令

### 查看远程文件

```bash
ssh username@server 'ls -lh /var/www/android_re_kb'
```

### 查看Nginx日志

```bash
ssh username@server 'sudo tail -f /var/log/nginx/android_re_kb_access.log'
```

### 重启Nginx

```bash
ssh username@server 'sudo systemctl restart nginx'
```

### 测试站点

```bash
curl -I http://your-domain.com
```

---

## ❓ 常见问题

### Q1: SSH连接失败

```bash
# 生成SSH密钥
ssh-keygen -t rsa -b 4096

# 复制到服务器
ssh-copy-id username@server

# 配置密钥路径
echo 'SSH_KEY="~/.ssh/id_rsa"' >> sync.conf
```

### Q2: 权限问题

```bash
# 在服务器上设置权限
ssh username@server
sudo chown -R www-data:www-data /var/www/android_re_kb
sudo chmod -R 755 /var/www/android_re_kb
```

### Q3: 端口被占用

```bash
# 修改端口
echo 'NGINX_PORT="8080"' >> sync.conf
./deploy-nginx.sh
```

---

## 📊 推荐工作流

### 开发阶段
```bash
# 本地开发
mkdocs serve

# 测试通过后同步
./sync-build.sh
```

### 生产部署
```bash
# 1. 构建并同步
./sync-build.sh

# 2. 首次部署配置Nginx
./deploy-nginx.sh

# 3. 后续更新只需
./sync-build.sh
```

---

**需要完整的部署文档?** 查看 `DEPLOYMENT_GUIDE.md`

**作者**: overkazaf@gmail.com
**微信**: _0xAF_
