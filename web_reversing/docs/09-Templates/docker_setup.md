# Docker 部署配置模板

容器化部署爬虫项目的完整配置，支持单机和分布式部署。

---

## 📁 项目结构

```
docker_scraper/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   └── scraper.py
├── docker/
│   ├── Dockerfile
│   ├── Dockerfile.dev
│   └── docker-compose.yml
├── scripts/
│   ├── entrypoint.sh
│   └── wait-for-it.sh
├── nginx/
│   └── nginx.conf
├── .env.example
├── .dockerignore
└── README.md
```

---

## 📄 配置文件

### 1. Dockerfile (生产环境)

```dockerfile
# 基础镜像
FROM python:3.11-slim

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建非 root 用户
RUN useradd -m -u 1000 scraper && \
    chown -R scraper:scraper /app

# 切换用户
USER scraper

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# 启动命令
CMD ["python", "app/main.py"]
```

### 2. Dockerfile.dev (开发环境)

```dockerfile
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# 安装开发工具
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    wget \
    vim \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements-dev.txt ./

RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-dev.txt

# 不复制代码，使用 volume 挂载
VOLUME /app

CMD ["python", "app/main.py"]
```

### 3. docker-compose.yml

```yaml
version: "3.8"

services:
  # 爬虫应用
  scraper:
    build:
      context: .
      dockerfile: docker/Dockerfile
    container_name: scraper_app
    restart: unless-stopped
    environment:
      - MONGODB_URI=mongodb://mongodb:27017/
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - LOG_LEVEL=INFO
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    depends_on:
      mongodb:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - scraper_network
    labels:
      - "com.scraper.description=Main scraper service"

  # MongoDB 数据库
  mongodb:
    image: mongo:7.0
    container_name: scraper_mongodb
    restart: unless-stopped
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_PASSWORD:-admin123}
      MONGO_INITDB_DATABASE: scraper_db
    volumes:
      - mongodb_data:/data/db
      - mongodb_config:/data/configdb
    ports:
      - "27017:27017"
    healthcheck:
      test: echo 'db.runCommand("ping").ok' | mongosh localhost:27017/test --quiet
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 20s
    networks:
      - scraper_network

  # Redis 缓存
  redis:
    image: redis:7-alpine
    container_name: scraper_redis
    restart: unless-stopped
    command: redis-server --requirepass ${REDIS_PASSWORD:-redis123} --maxmemory 256mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - scraper_network

  # Nginx (可选)
  nginx:
    image: nginx:alpine
    container_name: scraper_nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./data/static:/usr/share/nginx/html:ro
    depends_on:
      - scraper
    networks:
      - scraper_network

  # 监控 (可选)
  prometheus:
    image: prom/prometheus:latest
    container_name: scraper_prometheus
    restart: unless-stopped
    command:
      - "--config.file=/etc/prometheus/prometheus.yml"
      - "--storage.tsdb.path=/prometheus"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - scraper_network

  # 可视化监控
  grafana:
    image: grafana/grafana:latest
    container_name: scraper_grafana
    restart: unless-stopped
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD:-admin123}
    volumes:
      - grafana_data:/var/lib/grafana
    ports:
      - "3000:3000"
    depends_on:
      - prometheus
    networks:
      - scraper_network

networks:
  scraper_network:
    driver: bridge

volumes:
  mongodb_data:
  mongodb_config:
  redis_data:
  prometheus_data:
  grafana_data:
```

### 4. docker-compose.dev.yml (开发环境)

```yaml
version: "3.8"

services:
  scraper:
    build:
      context: .
      dockerfile: docker/Dockerfile.dev
    container_name: scraper_dev
    environment:
      - MONGODB_URI=mongodb://mongodb:27017/
      - REDIS_HOST=redis
      - LOG_LEVEL=DEBUG
    volumes:
      - .:/app # 挂载代码目录，支持热重载
      - /app/__pycache__ # 排除缓存
    ports:
      - "8000:8000"
      - "5678:5678" # 调试端口
    depends_on:
      - mongodb
      - redis
    networks:
      - scraper_network
    command: python -m debugpy --listen 0.0.0.0:5678 --wait-for-client app/main.py

  mongodb:
    image: mongo:7.0
    container_name: scraper_mongodb_dev
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: admin123
    ports:
      - "27017:27017"
    volumes:
      - mongodb_dev_data:/data/db
    networks:
      - scraper_network

  redis:
    image: redis:7-alpine
    container_name: scraper_redis_dev
    command: redis-server --requirepass redis123
    ports:
      - "6379:6379"
    networks:
      - scraper_network

networks:
  scraper_network:
    driver: bridge

volumes:
  mongodb_dev_data:
```

### 5. .dockerignore

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
*.egg-info/
dist/
build/

# 数据和日志
data/
logs/
*.log

# Git
.git/
.gitignore

# IDE
.vscode/
.idea/
*.swp
*.swo

# 环境变量
.env
.env.local

# Docker
docker-compose.yml
Dockerfile*

# 测试
.pytest_cache/
.coverage
htmlcov/

# 文档
docs/
*.md
!README.md
```

### 6. scripts/entrypoint.sh

```bash
#!/bin/bash
set -e

echo "🚀 Starting scraper application..."

# 等待 MongoDB 就绪
echo "⏳ Waiting for MongoDB..."
until python -c "
import pymongo
import sys
try:
    client = pymongo.MongoClient('${MONGODB_URI}', serverSelectionTimeoutMS=2000)
    client.server_info()
    print('✅ MongoDB is ready!')
except Exception as e:
    print(f'❌ MongoDB not ready: {e}')
    sys.exit(1)
"; do
  echo "MongoDB is unavailable - sleeping"
  sleep 2
done

# 等待 Redis 就绪
echo "⏳ Waiting for Redis..."
until python -c "
import redis
import sys
try:
    r = redis.Redis(host='${REDIS_HOST}', port=${REDIS_PORT}, password='${REDIS_PASSWORD}', socket_connect_timeout=2)
    r.ping()
    print('✅ Redis is ready!')
except Exception as e:
    print(f'❌ Redis not ready: {e}')
    sys.exit(1)
"; do
  echo "Redis is unavailable - sleeping"
  sleep 2
done

# 初始化数据库 (可选)
echo "🔧 Initializing database..."
python -c "
from app.database import init_db
init_db()
print('✅ Database initialized!')
"

echo "✨ All services are ready!"
echo "🎯 Starting main application..."

# 执行主命令
exec "$@"
```

### 7. scripts/wait-for-it.sh

```bash
#!/bin/bash
# wait-for-it.sh - 等待服务可用

TIMEOUT=15
QUIET=0
HOST=""
PORT=""

while [ $# -gt 0 ]; do
  case "$1" in
    *:* )
      HOST=$(printf "%s\n" "$1"| cut -d : -f 1)
      PORT=$(printf "%s\n" "$1"| cut -d : -f 2)
      shift 1
      ;;
    -t)
      TIMEOUT="$2"
      shift 2
      ;;
    -q)
      QUIET=1
      shift 1
      ;;
    *)
      echo "Unknown argument: $1"
      exit 1
      ;;
  esac
done

if [ "$HOST" = "" ] || [ "$PORT" = "" ]; then
  echo "Error: you need to provide a host and port to test."
  exit 1
fi

TIMEOUT_END=$(($(date +%s) + TIMEOUT))

while :; do
  if [ $QUIET -ne 1 ]; then
    echo "Waiting for $HOST:$PORT..."
  fi

  nc -z "$HOST" "$PORT" > /dev/null 2>&1
  result=$?

  if [ $result -eq 0 ]; then
    if [ $QUIET -ne 1 ]; then
      echo "$HOST:$PORT is available!"
    fi
    exit 0
  fi

  if [ "$(date +%s)" -ge "$TIMEOUT_END" ]; then
    echo "Timeout waiting for $HOST:$PORT"
    exit 1
  fi

  sleep 1
done
```

### 8. nginx/nginx.conf

```nginx
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # 日志格式
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    # 性能优化
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    # Gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1000;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;

    # 上游服务器
    upstream scraper_backend {
        server scraper:8000;
        keepalive 32;
    }

    # 主服务器配置
    server {
        listen 80;
        server_name localhost;

        # 静态文件
        location /static/ {
            alias /usr/share/nginx/html/;
            expires 30d;
            add_header Cache-Control "public, immutable";
        }

        # API 代理
        location /api/ {
            proxy_pass http://scraper_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # 超时设置
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # 健康检查
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }
}
```

### 9. .env.example

```bash
# MongoDB 配置
MONGODB_URI=mongodb://mongodb:27017/
MONGO_PASSWORD=admin123

# Redis 配置
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=redis123

# 应用配置
LOG_LEVEL=INFO
DEBUG=false

# Grafana 配置
GRAFANA_PASSWORD=admin123

# 代理配置 (可选)
USE_PROXY=false
PROXY_URL=http://proxy:7890
```

### 10. monitoring/prometheus.yml

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  # Prometheus 自身
  - job_name: "prometheus"
    static_configs:
      - targets: ["localhost:9090"]

  # 爬虫应用
  - job_name: "scraper"
    static_configs:
      - targets: ["scraper:8000"]
    metrics_path: "/metrics"

  # MongoDB Exporter (如果使用)
  - job_name: "mongodb"
    static_configs:
      - targets: ["mongodb-exporter:9216"]

  # Redis Exporter (如果使用)
  - job_name: "redis"
    static_configs:
      - targets: ["redis-exporter:9121"]
```

### 11. requirements-dev.txt

```txt
# 开发工具
debugpy>=1.8.0
ipython>=8.18.0
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-mock>=3.12.0
black>=23.12.0
flake8>=6.1.0
mypy>=1.7.0
```

---

## 🚀 使用指南

### 生产环境部署

```bash
# 1. 克隆项目
git clone <your-repo>
cd docker_scraper

# 2. 配置环境变量
cp .env.example .env
vim .env  # 修改密码等配置

# 3. 构建并启动
docker-compose up -d

# 4. 查看日志
docker-compose logs -f scraper

# 5. 查看状态
docker-compose ps

# 6. 停止服务
docker-compose down
```

### 开发环境

```bash
# 使用开发配置
docker-compose -f docker-compose.dev.yml up

# 进入容器
docker exec -it scraper_dev bash

# 运行测试
docker exec scraper_dev pytest

# 查看日志
docker-compose -f docker-compose.dev.yml logs -f
```

### 常用命令

```bash
# 重新构建镜像
docker-compose build --no-cache

# 只启动特定服务
docker-compose up -d mongodb redis

# 查看资源使用
docker stats

# 清理未使用的资源
docker system prune -a

# 导出数据
docker exec scraper_mongodb mongodump --out /tmp/backup
docker cp scraper_mongodb:/tmp/backup ./backup

# 导入数据
docker cp ./backup scraper_mongodb:/tmp/
docker exec scraper_mongodb mongorestore /tmp/backup
```

---

## 📊 监控和维护

### 访问 Grafana

```
URL: http://localhost:3000
用户名: admin
密码: (在 .env 中设置的 GRAFANA_PASSWORD)
```

### 查看 Prometheus 指标

```
URL: http://localhost:9090
```

### 健康检查

```bash
# 应用健康检查
curl http://localhost/health

# Docker 健康状态
docker inspect --format='{{.State.Health.Status}}' scraper_app
```

---

## 🔧 进阶配置

### 多副本部署

```yaml
# docker-compose.yml
services:
  scraper:
    # ... 其他配置
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: "0.5"
          memory: 512M
        reservations:
          cpus: "0.25"
          memory: 256M
```

### 使用 Docker Swarm

```bash
# 初始化 Swarm
docker swarm init

# 部署服务栈
docker stack deploy -c docker-compose.yml scraper_stack

# 查看服务
docker service ls

# 扩容
docker service scale scraper_stack_scraper=5
```

### 使用外部配置

```yaml
# docker-compose.yml
services:
  scraper:
    configs:
      - source: app_config
        target: /app/config.yaml

configs:
  app_config:
    file: ./config.yaml
```

---

## 📚 相关资源

- [Docker 部署](../06-Engineering/docker_deployment.md)
- [分布式爬虫](./distributed_crawler.md)
- [监控告警](../06-Engineering/monitoring_and_alerting.md)
