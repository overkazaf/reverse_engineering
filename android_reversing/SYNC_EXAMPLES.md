# 📚 Sync脚本使用示例

## 🎯 多种使用方式

sync-build.sh 脚本现在支持3种方式指定服务器信息：

### 方式1: 使用配置文件（推荐）

**优点**: 一次配置，多次使用

```bash
# 1. 创建配置
cp sync.conf.example sync.conf
nano sync.conf

# 2. 部署
./sync-build.sh
```

### 方式2: 快捷格式（推荐）

**优点**: 一条命令搞定，适合临时部署

```bash
./sync-build.sh user@server:/path
```

**示例**:
```bash
# 部署到阿里云
./sync-build.sh root@123.45.67.89:/var/www/html

# 部署到腾讯云
./sync-build.sh ubuntu@your-domain.com:/home/ubuntu/kb

# 部署到本地测试服务器
./sync-build.sh admin@192.168.1.100:/opt/www
```

### 方式3: 命令行参数（最灵活）

**优点**: 完全控制所有参数

```bash
./sync-build.sh -h server -u user -d /path [其他选项]
```

**完整选项**:
```bash
-h, --host HOST      # 服务器地址
-u, --user USER      # SSH用户名  
-p, --port PORT      # SSH端口（默认22）
-d, --dir PATH       # 远程目录路径
-k, --key FILE       # SSH密钥文件
-c, --config FILE    # 使用指定配置文件
```

---

## 💡 实用示例

### 示例1: 部署到阿里云ECS

```bash
# 快捷方式
./sync-build.sh root@123.45.67.89:/var/www/android_re_kb

# 或完整参数
./sync-build.sh \
  --host 123.45.67.89 \
  --user root \
  --dir /var/www/android_re_kb
```

### 示例2: 使用非标准SSH端口

```bash
./sync-build.sh \
  --host example.com \
  --user admin \
  --port 2222 \
  --dir /home/admin/kb
```

### 示例3: 指定SSH密钥

```bash
./sync-build.sh \
  --host server.com \
  --user deploy \
  --dir /var/www/html \
  --key ~/.ssh/deploy_key
```

### 示例4: 使用自定义配置文件

```bash
# 创建多个配置文件
cp sync.conf.example sync-prod.conf
cp sync.conf.example sync-test.conf

# 部署到生产环境
./sync-build.sh --config sync-prod.conf

# 部署到测试环境
./sync-build.sh --config sync-test.conf
```

### 示例5: 部署到多个服务器

```bash
# 方法1: 依次部署
./sync-build.sh root@server1.com:/var/www/html
./sync-build.sh root@server2.com:/var/www/html
./sync-build.sh root@server3.com:/var/www/html

# 方法2: 使用循环
for server in server1.com server2.com server3.com; do
  ./sync-build.sh root@$server:/var/www/html
done

# 方法3: 并行部署
./sync-build.sh root@server1.com:/var/www/html &
./sync-build.sh root@server2.com:/var/www/html &
./sync-build.sh root@server3.com:/var/www/html &
wait
```

---

## 🚀 高级用法

### 一键部署脚本

创建 `deploy-all.sh`:

```bash
#!/bin/bash

# 部署到生产服务器
echo "部署到生产环境..."
./sync-build.sh root@prod.example.com:/var/www/kb

# 部署到备份服务器
echo "部署到备份服务器..."
./sync-build.sh root@backup.example.com:/var/www/kb

# 配置Nginx
./deploy-nginx.sh --config sync.conf

echo "✅ 全部部署完成！"
```

### 环境变量方式

```bash
# 设置环境变量
export SYNC_HOST="example.com"
export SYNC_USER="root"
export SYNC_PATH="/var/www/html"

# 修改脚本支持环境变量（需要在脚本中添加）
./sync-build.sh
```

### Git Hook自动部署

创建 `.git/hooks/post-commit`:

```bash
#!/bin/bash
# 每次提交后自动部署

echo "检测到新提交，开始自动部署..."
./sync-build.sh root@server.com:/var/www/kb
```

---

## 📋 常用组合

### 开发流程

```bash
# 本地开发和测试
mkdocs serve

# 测试通过后部署到测试服务器
./sync-build.sh root@test.example.com:/var/www/kb

# 确认无误后部署到生产环境
./sync-build.sh --config sync-prod.conf
```

### 备份流程

```bash
# 部署新版本前先备份
./sync-build.sh root@backup.example.com:/var/www/kb.backup

# 部署新版本
./sync-build.sh root@prod.example.com:/var/www/kb

# 如果有问题，从备份恢复
# ssh root@prod.example.com 'mv /var/www/kb.backup /var/www/kb'
```

---

## 🔍 参数优先级

当同时使用多种方式时，优先级从高到低:

1. **命令行参数** (`-h`, `-u`, `-d` 等)
2. **快捷格式** (`user@host:/path`)
3. **配置文件** (`sync.conf`)

示例:
```bash
# 配置文件中设置的是 server1.com
# 但命令行指定 server2.com，最终使用 server2.com
./sync-build.sh --host server2.com
```

---

## 💡 最佳实践

### 1. 开发环境使用快捷格式

```bash
./sync-build.sh root@dev.local:/var/www/kb
```

### 2. 生产环境使用配置文件

```bash
# sync-prod.conf
SERVER_HOST="prod.example.com"
SERVER_USER="deploy"
SERVER_PORT="22"
REMOTE_PATH="/var/www/kb"
SSH_KEY="~/.ssh/prod_key"

# 部署
./sync-build.sh --config sync-prod.conf
```

### 3. CI/CD使用环境变量

```yaml
# .github/workflows/deploy.yml
deploy:
  steps:
    - name: Deploy
      run: |
        ./sync-build.sh \
          --host ${{ secrets.SERVER_HOST }} \
          --user ${{ secrets.SERVER_USER }} \
          --dir ${{ secrets.REMOTE_PATH }} \
          --key ${{ secrets.SSH_KEY }}
```

---

## 🆘 故障排查

### 查看详细输出

```bash
# 添加-v参数查看详细过程（需要脚本支持）
bash -x ./sync-build.sh user@server:/path
```

### 测试连接

```bash
# 测试SSH连接
ssh user@server 'echo "连接成功"'

# 测试目录权限
ssh user@server 'ls -la /var/www'
```

### 查看帮助

```bash
./sync-build.sh --help
```

---

**作者**: overkazaf@gmail.com | **微信**: _0xAF_
