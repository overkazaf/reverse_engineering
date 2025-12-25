---
title: "容器化部署：Docker 与 Kubernetes 实战"
date: 2025-05-23
tags: ["Docker", "自动化", "Android", "Root检测", "Kubernetes"]
weight: 10
---

# 容器化部署：Docker 与 Kubernetes 实战

> **📚 前置知识**
>
> 本配方涉及以下核心技术，建议先阅读相关章节：
>
> - **[Scrapy 快速入门](./scrapy.md)** - 理解 Scrapy 项目结构
> - **Docker 基础** - 理解容器与镜像概念

将爬虫项目容器化是实现标准化部署、弹性伸缩和 CI/CD 的第一步。本指南将详细介绍如何编写 Dockerfile，使用 Docker Compose 编排服务，以及如何在 Kubernetes (K8s) 上运行爬虫任务。

---

## 1. Dockerfile 最佳实践

我们需要为 Scrapy 项目构建一个轻量、稳定的 Docker 镜像。

### 目录结构

```text
my_crawler/
├── scrapy.cfg
├── requirements.txt
├── Dockerfile
└── myproject/
    ├── __init__.py
    ├── items.py
    ├── settings.py
    └── spiders/
```

### Dockerfile

```dockerfile
FROM python:3.9-slim-buster

# 设置工作目录
WORKDIR /app

# 设置环境变量
# 防止 Python 生成 .pyc 文件
ENV PYTHONDONTWRITEBYTECODE 1
# 防止 Python 缓冲区 stdout/stderr，确保日志实时输出
ENV PYTHONUNBUFFERED 1
# 设置时区 (可选)
ENV TZ=Asia/Shanghai

# 安装系统依赖 (如果需要编译 lxml 或其它库)
# RUN apt-get update && apt-get install -y gcc libxml2-dev libxslt-dev && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

# 默认启动命令 (可被 docker run 覆盖)
# 这里我们默认启动 scrapyd (如果使用 scrapyd 部署) 或仅作为一个 shell
CMD ["scrapy", "list"]
```

### 构建与运行

```bash
# 构建镜像
docker build -t my-crawler:v1 .

# 运行爬虫
docker run --rm my-crawler:v1 scrapy crawl myspider
```

---

## 2. Docker Compose 编排

对于分布式 Scrapy-Redis 架构，我们需要同时运行 Redis、MongoDB 和多个爬虫节点。

### docker-compose.yml

```yaml
version: '3.8'

services:
  # 1. Redis 服务 (消息队列)
  redis:
    image: redis:6.2-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

  # 2. MongoDB 服务 (数据存储)
  mongo:
    image: mongo:5.0
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: password
    volumes:
      - mongo_data:/data/db

  # 3. 爬虫服务 (Master/Slave 模式中的 Slave)
  crawler:
    build: .
    image: my-crawler:latest
    # 覆盖默认命令，启动爬虫
    command: scrapy crawl myspider_distributed
    # 依赖服务就绪
    depends_on:
      - redis
      - mongo
    environment:
      - REDIS_HOST=redis
      - MONGO_URI=mongodb://admin:${MONGO_PASSWORD}@mongo:27017
    # 想要开启多个爬虫节点？直接 scale
    deploy:
      replicas: 3

volumes:
  redis_data:
  mongo_data:
```

### 启动与扩容

```bash
# 启动所有服务
docker-compose up -d

# 扩容爬虫节点到 5
docker-compose up -d --scale crawler=5

# 查看日志
docker-compose logs -f crawler

# 停止所有服务
docker-compose down
```

---

## 3. Kubernetes 部署

在 K8s 上运行爬虫，可以利用其强大的调度和自愈能力。

### Deployment（持续运行的爬虫 Worker）

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: scrapy-worker
  labels:
    app: scrapy-worker
spec:
  # 副本数，即并发爬虫节点数量
  replicas: 5
  selector:
    matchLabels:
      app: scrapy-worker
  template:
    metadata:
      labels:
        app: scrapy-worker
    spec:
      containers:
        - name: crawler
          image: registry.example.com/my-crawler:v1
          # 容器启动命令
          command: ["scrapy", "crawl", "myspider_distributed"]
          # 环境变量配置
          env:
            - name: REDIS_HOST
              value: "redis-service"  # K8s Service Name
            - name: MONGO_URI
              valueFrom:
                secretKeyRef:
                  name: db-secrets
                  key: mongo-uri
          resources:
            requests:
              memory: "256Mi"
              cpu: "250m"
            limits:
              memory: "512Mi"
              cpu: "500m"
```

### CronJob（定时任务）

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: daily-crawler
spec:
  # 每天凌晨 2 点运行
  schedule: "0 2 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
            - name: crawler
              image: registry.example.com/my-crawler:v1
              command: ["scrapy", "crawl", "daily_spider"]
              env:
                - name: REDIS_HOST
                  value: "redis-service"
          restartPolicy: OnFailure
```

### 常用 kubectl 命令

```bash
# 应用配置
kubectl apply -f crawler-deployment.yaml

# 查看 Pod 状态
kubectl get pods

# 动态扩缩容 (无需修改 yaml)
kubectl scale deployment scrapy-worker --replicas=10

# 查看日志
kubectl logs -f deployment/scrapy-worker

# 进入容器调试
kubectl exec -it <pod-name> -- /bin/bash
```

---

## 4. 集成 Scrapyd 管理平台

**Scrapyd**: Scrapy 官方的部署服务，提供 HTTP API 来部署、启动、停止爬虫。

**Gerapy**: 基于 Scrapyd 的分布式管理 GUI，支持节点管理、代码编辑、定时任务。

### Dockerfile (集成 Scrapyd)

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install scrapyd scrapy-redis
COPY scrapyd.conf /etc/scrapyd/
EXPOSE 6800
CMD ["scrapyd"]
```

### scrapyd.conf

```ini
[scrapyd]
eggs_dir    = eggs
logs_dir    = logs
items_dir   = items
jobs_to_keep = 5
dbs_dir     = dbs
max_proc    = 0
max_proc_per_cpu = 4
finished_to_keep = 100
poll_interval = 5.0
bind_address = 0.0.0.0
http_port   = 6800
debug       = off
runner      = scrapyd.runner
application = scrapyd.app.application
launcher    = scrapyd.launcher.Launcher
webroot     = scrapyd.website.Root
```

### 部署爬虫到 Scrapyd

```bash
# 打包项目
scrapyd-deploy -p myproject

# 启动爬虫
curl http://localhost:6800/schedule.json -d project=myproject -d spider=myspider

# 查看爬虫状态
curl http://localhost:6800/listjobs.json?project=myproject
```

---

## 5. CI/CD 集成

### GitHub Actions 示例

```yaml
name: Build and Deploy Crawler

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Build Docker image
        run: docker build -t my-crawler:${{ github.sha }} .

      - name: Push to Registry
        run: |
          docker login -u ${{ secrets.DOCKER_USER }} -p ${{ secrets.DOCKER_PASS }}
          docker tag my-crawler:${{ github.sha }} registry.example.com/my-crawler:${{ github.sha }}
          docker push registry.example.com/my-crawler:${{ github.sha }}

      - name: Deploy to K8s
        run: |
          kubectl set image deployment/scrapy-worker crawler=registry.example.com/my-crawler:${{ github.sha }}
```

---

## 总结

容器化部署是现代爬虫工程的标准实践。通过 Docker 实现环境一致性，通过 Docker Compose 简化本地开发，通过 Kubernetes 实现生产环境的弹性伸缩和自愈能力。结合 Scrapyd 和 CI/CD 流程，可以构建一个完整的爬虫 DevOps 体系。
