# Docker 部署问题

Docker 容器化部署中的常见问题及解决方案。

---

## 容器启动失败

### 问题表现

```bash
Error response from daemon: Container xxx exited with code 1
```

### 解决方案

#### 1. 查看日志

```bash
# 查看容器日志
docker logs container_name

# 实时查看日志
docker logs -f container_name

# 查看最近的日志
docker logs --tail 100 container_name

# 查看带时间戳的日志
docker logs -t container_name
```

#### 2. 检查容器状态

```bash
# 查看所有容器 (包括停止的)
docker ps -a

# 查看容器详细信息
docker inspect container_name

# 查看容器资源使用
docker stats container_name
```

#### 3. 进入容器调试

```bash
# 进入运行中的容器
docker exec -it container_name bash

# 如果容器已停止,使用临时容器
docker run -it --rm image_name bash

# 使用 sh (如果 bash 不可用)
docker exec -it container_name sh
```

#### 4. 检查启动命令

```yaml
# docker-compose.yml
services:
  app:
    image: myapp:latest
    command: python app.py  # 确保命令正确
    # 或使用数组格式
    command: ["python", "app.py"]
```

---

## 网络连接问题

### 容器无法访问外网

**解决方案**:

```bash
# 1. 检查 DNS 配置
docker run --rm alpine ping google.com

# 2. 指定 DNS 服务器
docker run --dns 8.8.8.8 --dns 8.8.4.4 myimage

# 3. docker-compose.yml 中配置
services:
  app:
    dns:
      - 8.8.8.8
      - 8.8.4.4

# 4. 检查 Docker 网络设置
docker network ls
docker network inspect bridge
```

### 容器间无法通信

**解决方案**:

```bash
# 1. 确保在同一网络中
docker-compose.yml:
services:
  app:
    networks:
      - mynetwork
  db:
    networks:
      - mynetwork

networks:
  mynetwork:
    driver: bridge

# 2. 使用服务名访问
# 在 app 容器中访问 db 容器
ping db  # 而不是 localhost

# 3. 检查防火墙
sudo ufw status
sudo iptables -L

# 4. 检查端口映射
docker port container_name
```

### 端口冲突

**问题表现**:

```bash
Error: Bind for 0.0.0.0:8080 failed: port is already allocated
```

**解决方案**:

```bash
# 1. 查看端口占用
lsof -i :8080  # Linux/Mac
netstat -ano | findstr :8080  # Windows

# 2. 修改端口映射
docker run -p 8081:8080 myimage  # 使用其他主机端口

# 3. docker-compose.yml
services:
  app:
    ports:
      - "8081:8080"  # host:container

# 4. 停止占用端口的容器
docker ps | grep 8080
docker stop container_name
```

---

## 卷挂载问题

### 文件权限错误

**问题表现**:

```bash
PermissionError: [Errno 13] Permission denied: '/app/data/file.txt'
```

**解决方案**:

```dockerfile
# 1. Dockerfile 中设置正确的权限
FROM python:3.11

WORKDIR /app

# 创建非 root 用户
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# 切换用户
USER appuser

COPY --chown=appuser:appuser . .
```

```yaml
# 2. docker-compose.yml 中指定用户
services:
  app:
    user: "1000:1000" # UID:GID
    volumes:
      - ./data:/app/data
```

```bash
# 3. 修改主机文件权限
sudo chown -R 1000:1000 ./data

# 4. 在容器内修改权限
docker exec -u root container_name chown -R appuser:appuser /app/data
```

### 卷挂载失败

**问题表现**:

```bash
Error: invalid mount config: volume driver not found
```

**解决方案**:

```yaml
# 1. 使用绝对路径
services:
  app:
    volumes:
      - /absolute/path/to/data:/app/data  # Linux/Mac
      - C:/absolute/path/to/data:/app/data  # Windows

# 2. 使用相对路径
services:
  app:
    volumes:
      - ./data:/app/data  # 相对于 docker-compose.yml

# 3. 使用命名卷
services:
  app:
    volumes:
      - mydata:/app/data

volumes:
  mydata:
    driver: local

# 4. Windows 路径转换
# Windows 下需要共享驱动器
# Docker Desktop → Settings → Resources → File Sharing
```

---

## 镜像构建问题

### 构建速度慢

**解决方案**:

```dockerfile
# 1. 使用多阶段构建
FROM python:3.11 AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH

# 2. 优化层缓存
# 把不常变的指令放前面
FROM python:3.11
WORKDIR /app

# 先复制依赖文件
COPY requirements.txt .
RUN pip install -r requirements.txt

# 再复制代码
COPY . .

# 3. 使用 .dockerignore
.git/
__pycache__/
*.pyc
*.pyo
*.log
.env
node_modules/
```

```bash
# 4. 使用构建缓存
docker build --cache-from myimage:latest -t myimage:new .

# 5. 使用 BuildKit
export DOCKER_BUILDKIT=1
docker build -t myimage .
```

### 镜像过大

**解决方案**:

```dockerfile
# 1. 使用更小的基础镜像
# ❌ 大镜像 (900MB+)
FROM python:3.11

# ✅ 小镜像 (100MB+)
FROM python:3.11-slim

# ✅ 更小的镜像 (50MB+)
FROM python:3.11-alpine

# 2. 多阶段构建
FROM python:3.11 AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt

FROM python:3.11-slim
COPY --from=builder /install /usr/local
COPY app /app
WORKDIR /app

# 3. 清理缓存
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    pip install -r requirements.txt && \
    apt-get purge -y gcc && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# 4. 使用 .dockerignore
.git/
*.md
tests/
docs/
```

```bash
# 5. 查看镜像层
docker history myimage:latest

# 6. 压缩镜像
docker export container_name | docker import - myimage:compressed
```

---

## 资源限制问题

### 内存不足

**问题表现**:

```bash
Container killed due to memory limit
```

**解决方案**:

```yaml
# docker-compose.yml
services:
  app:
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M

# 或使用旧语法
services:
  app:
    mem_limit: 512m
    mem_reservation: 256m
```

```bash
# Docker run 命令
docker run -m 512m --memory-reservation 256m myimage

# 查看容器内存使用
docker stats container_name
```

### CPU 限制

```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '0.5'  # 限制使用 0.5 个 CPU
        reservations:
          cpus: '0.25'

# 或
services:
  app:
    cpus: 0.5
```

---

## 环境变量问题

### 环境变量未生效

**解决方案**:

```yaml
# 1. docker-compose.yml 中设置
services:
  app:
    environment:
      - DEBUG=true
      - DB_HOST=database

# 2. 从 .env 文件加载
services:
  app:
    env_file:
      - .env
      - .env.local

# 3. 从主机环境继承
services:
  app:
    environment:
      - HOME  # 从主机继承 HOME 变量
```

```bash
# 4. 运行时指定
docker run -e DEBUG=true -e DB_HOST=localhost myimage

# 5. 查看容器环境变量
docker exec container_name env
```

---

## Docker Compose 问题

### 服务启动顺序

**问题**: 服务间有依赖关系

**解决方案**:

```yaml
services:
  app:
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy

  db:
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5
```

### 配置文件重载

```bash
# 重新构建镜像
docker-compose build

# 重新创建容器
docker-compose up -d --force-recreate

# 只重启特定服务
docker-compose restart app

# 查看配置
docker-compose config
```

---

## 健康检查

### 配置健康检查

```dockerfile
# Dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
```

```yaml
# docker-compose.yml
services:
  app:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

```bash
# 查看健康状态
docker ps
docker inspect --format='{{.State.Health.Status}}' container_name
```

---

## 日志管理

### 日志过大

**问题**: 容器日志占用大量磁盘空间

**解决方案**:

```yaml
# docker-compose.yml
services:
  app:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

```bash
# 查看日志大小
du -sh /var/lib/docker/containers/*/*-json.log

# 清理日志
truncate -s 0 /var/lib/docker/containers/*/*-json.log

# 全局配置 /etc/docker/daemon.json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

---

## 性能优化

### 容器启动慢

```dockerfile
# 1. 减少层数
# ❌ 多层
RUN apt-get update
RUN apt-get install -y package1
RUN apt-get install -y package2

# ✅ 合并层
RUN apt-get update && \
    apt-get install -y package1 package2 && \
    rm -rf /var/lib/apt/lists/*

# 2. 使用缓存
FROM python:3.11
WORKDIR /app

# 先安装依赖 (变化少)
COPY requirements.txt .
RUN pip install -r requirements.txt

# 再复制代码 (变化多)
COPY . .

# 3. 预热镜像
docker pull myimage:latest
docker-compose pull
```

---

## 清理和维护

### 清理 Docker 资源

```bash
# 清理所有未使用的资源
docker system prune -a

# 清理容器
docker container prune

# 清理镜像
docker image prune -a

# 清理卷
docker volume prune

# 清理网络
docker network prune

# 查看磁盘使用
docker system df
```

---

## 调试技巧

### 1. 使用临时容器

```bash
# 运行临时容器调试
docker run -it --rm alpine sh

# 挂载卷调试
docker run -it --rm -v $(pwd):/data alpine sh
```

### 2. 覆盖入口点

```bash
# 覆盖 CMD
docker run -it myimage bash

# 覆盖 ENTRYPOINT
docker run -it --entrypoint bash myimage
```

### 3. 检查网络

```bash
# 进入容器检查
docker exec -it container_name bash

# 测试连接
ping other_container
curl http://other_container:8080
telnet other_container 3306
```

---

## 📚 相关章节

- [Docker 部署](../06-Engineering/docker_deployment.md)
- [Docker 配置模板](../09-Templates/docker_setup.md)
- [监控告警](../06-Engineering/monitoring_and_alerting.md)
