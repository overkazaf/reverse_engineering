---
title: "Docker 容器化部署"
date: 2025-08-07
weight: 10
---

# Docker 容器化部署

## 概述

Docker 容器化使爬虫项目具备可移植性、可扩展性和易维护性。本章介绍如何将爬虫项目容器化并进行生产部署。

---

## Docker 基础

### 核心概念

- **镜像 (Image)**: 只读模板，包含运行应用所需的一切
- **容器 (Container)**: 镜像的运行实例
- **Dockerfile**: 构建镜像的脚本
- **Docker Compose**: 多容器编排工具

---

## Dockerfile 编写

### 爬虫项目 Dockerfile

```dockerfile
# 使用官方 Python 镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
gcc \
g++ \
wget \
&& rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

# 暴露端口（如果有 API）
EXPOSE 8000

# 设置环境变量
ENV PYTHONUNBUFFERED=1

# 运行爬虫
CMD ["python", "main.py"]
```

### Puppeteer/Playwright Dockerfile

需要安装浏览器依赖：

```dockerfile
FROM node:18-slim

# 安装 Chromium 依赖
RUN apt-get update && apt-get install -y \
chromium \
fonts-liberation \
libappindicator3-1 \
libasound2 \
libatk-bridge2.0-0 \
libatk1.0-0 \
libcups2 \
libdbus-1-3 \
libgdk-pixbuf2.0-0 \
libnspr4 \
libnss3 \
libx11-xcb1 \
libxcomposite1 \
libxdamage1 \
libxrandr2 \
xdg-utils \
&& rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

CMD ["node", "index.js"]
```

---

## Docker Compose

### 完整爬虫系统编排

```yaml
version: "3.8"

services:
# Redis
redis:
image: redis:7-alpine
ports:
- "6379:6379"
volumes:
- redis_data:/data
restart: unless-stopped

# MongoDB
mongodb:
image: mongo:6
ports:
- "27017:27017"
environment:
MONGO_INITDB_ROOT_USERNAME: admin
MONGO_INITDB_ROOT_PASSWORD: password
volumes:
- mongo_data:/data/db
restart: unless-stopped

# 爬虫 Master
spider-master:
build: .
command: python master.py
depends_on:
- redis
- mongodb
environment:
- REDIS_URL=redis://redis:6379
- MONGO_URL=mongodb://admin:${MONGO_PASSWORD}@mongodb:27017
restart: unless-stopped

# 爬虫 Worker
spider-worker:
build: .
command: python worker.py
depends_on:
- redis
- mongodb
environment:
- REDIS_URL=redis://redis:6379
- MONGO_URL=mongodb://admin:${MONGO_PASSWORD}@mongodb:27017
restart: unless-stopped
deploy:
replicas: 3 # 启动3个Worker

volumes:
redis_data:
mongo_data:
```

### 启动和管理

```bash
# 构建镜像
docker-compose build

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f spider-worker

# 扩展 Worker 数量
docker-compose up -d --scale spider-worker=5

# 停止所有服务
docker-compose down

# 停止并删除卷
docker-compose down -v
```

---

## 最佳实践

### 1. 多阶段构建

减小镜像体积：

```dockerfile
# 构建阶段
FROM python:3.11 AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# 运行阶段
FROM python:3.11-slim

WORKDIR /app

# 从构建阶段复制依赖
COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH

CMD ["python", "main.py"]
```

### 2. 使用 .dockerignore

```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
.env
venv/
.git
.gitignore
*.md
.pytest_cache
.coverage
htmlcov/
```

### 3. 健康检查

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1
```

### 4. 环境变量管理

```yaml
# docker-compose.yml
services:
spider:
env_file:
- .env
```

```bash
# .env 文件
REDIS_URL=redis://redis:6379
API_KEY=your_api_key_here
PROXY_URL=http://proxy.example.com
```

---

## 生产部署

### 使用 Docker Swarm

```bash
# 初始化 Swarm
docker swarm init

# 部署服务栈
docker stack deploy -c docker-compose.yml spider

# 查看服务状态
docker service ls

# 扩展服务
docker service scale spider_spider-worker=10

# 删除服务栈
docker stack rm spider
```

### 使用 Kubernetes

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
name: spider-worker
spec:
replicas: 3
selector:
matchLabels:
app: spider-worker
template:
metadata:
labels:
app: spider-worker
spec:
containers:
- name: spider
image: myregistry/spider:latest
env:
- name: REDIS_URL
value: "redis://redis:6379"
resources:
requests:
memory: "512Mi"
cpu: "500m"
limits:
memory: "1Gi"
cpu: "1000m"
```

```bash
# 部署
kubectl apply -f deployment.yaml

# 扩展
kubectl scale deployment spider-worker --replicas=10

# 查看状态
kubectl get pods
```

---

## 监控与日志

### 日志管理

```yaml
services:
spider:
logging:
driver: "json-file"
options:
max-size: "10m"
max-file: "3"
```

### 集成 Prometheus

```yaml
services:
prometheus:
image: prom/prometheus
ports:
- "9090:9090"
volumes:
- ./prometheus.yml:/etc/prometheus/prometheus.yml
- prometheus_data:/prometheus

grafana:
image: grafana/grafana
ports:
- "3000:3000"
volumes:
- grafana_data:/var/lib/grafana
```

---

## 常见问题

### Q1: 容器内时区不正确？

```dockerfile
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN echo "Asia/Shanghai" > /etc/timezone
```

### Q2: 如何调试容器内的应用？

```bash
# 进入容器
docker exec -it container_id /bin/bash

# 查看日志
docker logs -f container_id

# 实时查看资源使用
docker stats container_id
```

### Q3: 如何持久化数据？

使用 Docker Volume：

```yaml
services:
spider:
volumes:
- spider_data:/app/data

volumes:
spider_data:
```

---

## 相关章节

- [分布式爬虫架构](./distributed_scraping.md)
- [监控与告警系统](./monitoring_and_alerting.md)
- [消息队列应用](./message_queue_application.md)
