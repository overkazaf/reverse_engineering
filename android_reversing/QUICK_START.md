# 🚀 快速开始 - 部署到服务器

## 3分钟快速部署

### 步骤1: 准备配置文件 (30秒)

```bash
# 复制配置示例
cp sync.conf.example sync.conf

# 编辑配置
nano sync.conf
```

**最少只需要修改这4项**:
```bash
SERVER_HOST="your-server.com"      # 改成你的服务器地址
SERVER_USER="username"             # 改成你的用户名
SERVER_PORT="22"                   # SSH端口（通常是22）
REMOTE_PATH="/var/www/html"        # 部署到服务器的哪个目录
```

### 步骤2: 部署 (2分钟)

```bash
# 一键部署（推荐）
./sync-build.sh
```

就这么简单！✨

---

## 📖 详细说明

### 你刚才做了什么？

1. **sync-build.sh** 会:
   - 在本地构建MkDocs静态站点
   - 通过SSH将文件同步到服务器
   - 自动设置正确的权限

2. 构建的站点会被上传到服务器的 `REMOTE_PATH` 目录

### 下一步: 配置Web服务器

#### 方案A: 快速测试（使用Python）

```bash
# SSH登录服务器
ssh username@your-server.com

# 进入部署目录
cd /var/www/html

# 启动简单HTTP服务器
python3 -m http.server 8000
```

访问: `http://your-server.com:8000`

#### 方案B: 生产环境（使用Nginx）

```bash
# 自动配置Nginx
./deploy-nginx.sh
```

访问: `http://your-domain.com`

---

## 🔑 SSH密钥配置（推荐）

为了避免每次输入密码，建议配置SSH密钥:

```bash
# 1. 生成密钥（如果还没有）
ssh-keygen -t rsa -b 4096

# 2. 复制到服务器
ssh-copy-id username@your-server.com

# 3. 测试
ssh username@your-server.com
```

---

## 💡 常用场景

### 场景1: 内容更新后重新部署

```bash
# 只需要一条命令
./sync-build.sh
```

### 场景2: 更换服务器

```bash
# 1. 修改 sync.conf 中的服务器信息
# 2. 重新部署
./sync-build.sh
./deploy-nginx.sh
```

### 场景3: 同时部署到多个服务器

```bash
# 创建多个配置文件
cp sync.conf sync.conf.server1
cp sync.conf sync.conf.server2

# 分别部署
CONFIG_FILE=sync.conf.server1 ./sync-build.sh
CONFIG_FILE=sync.conf.server2 ./sync-build.sh
```

---

## ❓ 遇到问题？

### SSH连接失败

```bash
# 测试连接
ssh username@your-server.com

# 如果提示输入密码，说明密钥没配置好
# 重新执行密钥配置步骤
```

### 权限问题

```bash
# 在服务器上执行
sudo chown -R www-data:www-data /var/www/html
sudo chmod -R 755 /var/www/html
```

### 端口被占用

```bash
# 修改sync.conf
NGINX_PORT="8080"

# 重新部署
./deploy-nginx.sh
```

---

## 📚 更多文档

- **SYNC_README.md** - 脚本使用说明
- **DEPLOYMENT_GUIDE.md** - 完整部署指南

---

**作者**: overkazaf@gmail.com | **微信**: _0xAF_
