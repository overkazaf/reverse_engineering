# 🚀 部署指南 - Android Reverse Engineering Cookbook

## 📋 目录

- [快速开始](#快速开始)
- [同步脚本说明](#同步脚本说明)
- [部署方式](#部署方式)
- [服务器配置](#服务器配置)
- [常见问题](#常见问题)

---

## 🎯 快速开始

### 1. 初始化配置

首次使用需要创建配置文件：

```bash
./sync.sh
```

这将自动创建 `sync.conf` 配置文件。

### 2. 编辑配置

编辑 `sync.conf` 文件，填写你的服务器信息：

```bash
# 服务器地址
SERVER_HOST="your-server.com"

# SSH用户名
SERVER_USER="username"

# SSH端口
SERVER_PORT="22"

# 远程目录路径
REMOTE_PATH="/var/www/android_re_kb"

# SSH密钥路径（可选）
SSH_KEY="~/.ssh/id_rsa"
```

### 3. 选择部署方式

#### 方式A: 同步整个项目（推荐用于开发环境）
```bash
./sync.sh
```

#### 方式B: 构建后同步（推荐用于生产环境）
```bash
./sync-build.sh
```

#### 方式C: 完整部署（包含Nginx配置）
```bash
./sync-build.sh
./deploy-nginx.sh
```

---

## 📜 同步脚本说明

### sync.sh - 源码同步脚本

**功能**: 将整个项目源码同步到服务器

**适用场景**:
- 开发环境部署
- 需要在服务器上构建
- 快速测试

**使用方法**:
```bash
./sync.sh
```

**特点**:
- ✅ 自动排除不必要的文件（.git, node_modules等）
- ✅ 增量同步，只传输变更的文件
- ✅ 保持文件权限和时间戳
- ✅ SSH连接测试
- ✅ 安全确认机制

### sync-build.sh - 构建并同步脚本

**功能**: 本地构建MkDocs站点，然后同步到服务器

**适用场景**:
- 生产环境部署
- 只需要静态HTML文件
- 节省服务器资源

**使用方法**:
```bash
./sync-build.sh
```

**特点**:
- ✅ 本地构建MkDocs站点
- ✅ 只上传静态文件
- ✅ 自动设置文件权限
- ✅ 显示构建统计信息
- ✅ 提供后续配置建议

### deploy-nginx.sh - Nginx部署脚本

**功能**: 自动配置Nginx Web服务器

**适用场景**:
- 生产环境
- 需要域名访问
- 需要HTTPS

**使用方法**:
```bash
# 编辑 sync.conf，添加以下配置
SITE_NAME="android_re_kb"
DOMAIN="your-domain.com"
NGINX_PORT="80"

# 运行部署脚本
./deploy-nginx.sh
```

**特点**:
- ✅ 自动生成Nginx配置
- ✅ 启用Gzip压缩
- ✅ 配置静态资源缓存
- ✅ 添加安全头
- ✅ 自动测试和重载配置

---

## 🌐 部署方式

### 方式1: 开发环境部署（源码同步）

**步骤**:

1. **同步源码到服务器**
   ```bash
   ./sync.sh
   ```

2. **SSH登录服务器**
   ```bash
   ssh username@your-server.com
   ```

3. **在服务器上安装依赖**
   ```bash
   cd /var/www/android_re_kb
   pip install -r requirements.txt
   ```

4. **启动MkDocs开发服务器**
   ```bash
   mkdocs serve -a 0.0.0.0:8000
   ```

5. **访问**
   ```
   http://your-server.com:8000
   ```

### 方式2: 生产环境部署（静态文件）

**步骤**:

1. **本地构建并同步**
   ```bash
   ./sync-build.sh
   ```

2. **配置Nginx**
   ```bash
   ./deploy-nginx.sh
   ```

3. **访问**
   ```
   http://your-domain.com
   ```

### 方式3: Docker容器部署

创建 `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装MkDocs和主题
RUN pip install mkdocs mkdocs-material

# 复制项目文件
COPY . .

# 构建站点
RUN mkdocs build

# 使用简单的HTTP服务器
CMD ["python", "-m", "http.server", "8000", "--directory", "site"]
```

**使用Docker部署**:

```bash
# 构建镜像
docker build -t android-re-kb .

# 运行容器
docker run -d -p 8000:8000 android-re-kb

# 访问
# http://your-server.com:8000
```

---

## ⚙️ 服务器配置

### Nginx完整配置示例

编辑 `/etc/nginx/sites-available/android_re_kb`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 重定向到HTTPS（可选）
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL证书配置
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # 文档根目录
    root /var/www/android_re_kb;
    index index.html;

    # 日志
    access_log /var/log/nginx/android_re_kb_access.log;
    error_log /var/log/nginx/android_re_kb_error.log;

    # Gzip压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript
               application/x-javascript application/xml+rss
               application/json application/javascript;

    # 主路由
    location / {
        try_files $uri $uri/ =404;
    }

    # 静态资源缓存
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
}
```

### 获取SSL证书（Let's Encrypt）

```bash
# 安装certbot
sudo apt-get install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

### Apache配置示例

编辑 `/etc/apache2/sites-available/android_re_kb.conf`:

```apache
<VirtualHost *:80>
    ServerName your-domain.com
    DocumentRoot /var/www/android_re_kb

    <Directory /var/www/android_re_kb>
        Options Indexes FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>

    # 启用压缩
    <IfModule mod_deflate.c>
        AddOutputFilterByType DEFLATE text/html text/plain text/xml text/css text/javascript application/javascript
    </IfModule>

    # 缓存控制
    <IfModule mod_expires.c>
        ExpiresActive On
        ExpiresByType image/jpg "access plus 1 month"
        ExpiresByType image/jpeg "access plus 1 month"
        ExpiresByType image/png "access plus 1 month"
        ExpiresByType text/css "access plus 1 week"
        ExpiresByType application/javascript "access plus 1 week"
    </IfModule>

    ErrorLog ${APACHE_LOG_DIR}/android_re_kb_error.log
    CustomLog ${APACHE_LOG_DIR}/android_re_kb_access.log combined
</VirtualHost>
```

启用站点:
```bash
sudo a2ensite android_re_kb
sudo systemctl reload apache2
```

---

## 🔧 常见问题

### Q1: SSH连接失败

**解决方案**:

```bash
# 检查SSH配置
ssh -vvv username@your-server.com

# 使用SSH密钥
ssh-keygen -t rsa -b 4096
ssh-copy-id username@your-server.com

# 在sync.conf中配置密钥路径
SSH_KEY="~/.ssh/id_rsa"
```

### Q2: 权限问题

**解决方案**:

```bash
# 在服务器上设置正确的所有权
sudo chown -R www-data:www-data /var/www/android_re_kb

# 设置正确的权限
sudo chmod -R 755 /var/www/android_re_kb
```

### Q3: MkDocs构建失败

**解决方案**:

```bash
# 安装所需依赖
pip install -r requirements.txt

# 检查mkdocs.yml配置
mkdocs build --verbose

# 清理缓存
rm -rf site
mkdocs build --clean
```

### Q4: Nginx 403 Forbidden

**解决方案**:

```bash
# 检查目录权限
ls -la /var/www/android_re_kb

# 检查Nginx配置
sudo nginx -t

# 查看错误日志
sudo tail -f /var/log/nginx/error.log

# SELinux问题（CentOS/RHEL）
sudo setsebool -P httpd_read_user_content 1
```

### Q5: 端口被占用

**解决方案**:

```bash
# 查看端口占用
sudo netstat -tlnp | grep :80

# 或使用lsof
sudo lsof -i :80

# 修改端口
# 编辑 sync.conf
NGINX_PORT="8080"
```

---

## 📊 监控和维护

### 查看访问日志

```bash
# 实时查看访问日志
ssh username@server 'sudo tail -f /var/log/nginx/android_re_kb_access.log'

# 分析访问统计
ssh username@server 'sudo cat /var/log/nginx/android_re_kb_access.log | \
    awk "{print \$1}" | sort | uniq -c | sort -rn | head -10'
```

### 自动化部署

创建 `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Server

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Setup Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: pip install mkdocs mkdocs-material

    - name: Build MkDocs
      run: mkdocs build

    - name: Deploy to Server
      uses: easingthemes/ssh-deploy@main
      env:
        SSH_PRIVATE_KEY: ${{ secrets.SSH_PRIVATE_KEY }}
        REMOTE_HOST: ${{ secrets.REMOTE_HOST }}
        REMOTE_USER: ${{ secrets.REMOTE_USER }}
        TARGET: ${{ secrets.REMOTE_PATH }}
        SOURCE: "site/"
```

---

## 📝 总结

### 推荐部署流程

1. **开发阶段**: 使用 `./sync.sh` 快速同步测试
2. **测试阶段**: 使用 `./sync-build.sh` 构建并部署
3. **生产环境**: 使用 `./deploy-nginx.sh` 完整部署

### 安全建议

- ✅ 使用SSH密钥认证
- ✅ 修改SSH默认端口
- ✅ 配置防火墙
- ✅ 启用HTTPS
- ✅ 定期更新服务器
- ✅ 监控访问日志

---

**作者**: overkazaf@gmail.com
**微信**: _0xAF_
**更新**: 2025-08-01
