---
title: "CI/CD 流水线模板"
date: 2025-01-30
weight: 10
---

# CI/CD 流水线模板

自动化构建、测试和部署配置，支持 GitHub Actions、GitLab CI 和 Jenkins。

---

## 项目结构

```
.
├── .github/
│ └── workflows/
│ ├── ci.yml # 持续集成
│ ├── cd.yml # 持续部署
│ └── docker-publish.yml # Docker 镜像发布
├── .gitlab-ci.yml # GitLab CI
├── Jenkinsfile # Jenkins Pipeline
├── scripts/
│ ├── run_tests.sh
│ ├── build.sh
│ └── deploy.sh
└── tests/
├── unit/
├── integration/
└── e2e/
```

---

## GitHub Actions

### 1. .github/workflows/ci.yml (持续集成)

```yaml
name: CI

on:
push:
branches: [main, develop]
pull_request:
branches: [main, develop]

env:
PYTHON_VERSION: "3.11"

jobs:
# 代码质量检查
lint:
name: Code Quality
runs-on: ubuntu-latest

steps:
- name: Checkout code
uses: actions/checkout@v4

- name: Set up Python
uses: actions/setup-python@v5
with:
python-version: ${{ env.PYTHON_VERSION }}
cache: "pip"

- name: Install dependencies
run: |
python -m pip install --upgrade pip
pip install flake8 black mypy pylint

- name: Run Black (格式检查)
run: black --check .

- name: Run Flake8 (代码规范)
run: flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

- name: Run MyPy (类型检查)
run: mypy . --ignore-missing-imports

- name: Run Pylint
run: pylint **/*.py --fail-under=8.0

# 单元测试
test:
name: Unit Tests
runs-on: ubuntu-latest
needs: lint

strategy:
matrix:
python-version: ["3.10", "3.11", "3.12"]

steps:
- uses: actions/checkout@v4

- name: Set up Python ${{ matrix.python-version }}
uses: actions/setup-python@v5
with:
python-version: ${{ matrix.python-version }}
cache: "pip"

- name: Install dependencies
run: |
pip install -r requirements.txt
pip install -r requirements-dev.txt

- name: Run tests with coverage
run: |
pytest tests/unit/ \
--cov=app \
--cov-report=xml \
--cov-report=html \
--junitxml=junit.xml

- name: Upload coverage to Codecov
uses: codecov/codecov-action@v4
with:
files: ./coverage.xml
flags: unittests
name: codecov-${{ matrix.python-version }}

- name: Upload test results
uses: actions/upload-artifact@v4
if: always()
with:
name: test-results-${{ matrix.python-version }}
path: |
junit.xml
htmlcov/

# 集成测试
integration-test:
name: Integration Tests
runs-on: ubuntu-latest
needs: test

services:
mongodb:
image: mongo:7.0
env:
MONGO_INITDB_ROOT_USERNAME: admin
MONGO_INITDB_ROOT_PASSWORD: admin123
ports:
- 27017:27017
options: >-
--health-cmd "echo 'db.runCommand(\"ping\").ok' | mongosh localhost:27017/test --quiet"
--health-interval 10s
--health-timeout 5s
--health-retries 5

redis:
image: redis:7-alpine
ports:
- 6379:6379
options: >-
--health-cmd "redis-cli ping"
--health-interval 10s
--health-timeout 5s
--health-retries 5

steps:
- uses: actions/checkout@v4

- name: Set up Python
uses: actions/setup-python@v5
with:
python-version: ${{ env.PYTHON_VERSION }}
cache: "pip"

- name: Install dependencies
run: |
pip install -r requirements.txt
pip install -r requirements-dev.txt

- name: Run integration tests
env:
MONGODB_URI: mongodb://admin:${MONGO_PASSWORD}@localhost:27017/
REDIS_HOST: localhost
REDIS_PORT: 6379
run: |
pytest tests/integration/ -v --tb=short

# 安全扫描
security:
name: Security Scan
runs-on: ubuntu-latest
needs: lint

steps:
- uses: actions/checkout@v4

- name: Set up Python
uses: actions/setup-python@v5
with:
python-version: ${{ env.PYTHON_VERSION }}

- name: Install dependencies
run: |
pip install safety bandit

- name: Check for security vulnerabilities (Safety)
run: safety check --json

- name: Run Bandit (代码安全扫描)
run: bandit -r app/ -f json -o bandit-report.json

- name: Upload security reports
uses: actions/upload-artifact@v4
if: always()
with:
name: security-reports
path: |
bandit-report.json

# Docker 构建测试
docker-build:
name: Docker Build Test
runs-on: ubuntu-latest
needs: test

steps:
- uses: actions/checkout@v4

- name: Set up Docker Buildx
uses: docker/setup-buildx-action@v3

- name: Build Docker image
uses: docker/build-push-action@v5
with:
context: .
file: ./docker/Dockerfile
push: false
tags: scraper:test
cache-from: type=gha
cache-to: type=gha,mode=max

- name: Test Docker image
run: |
docker run --rm scraper:test python -c "import app; print('✅ Import successful')"
```

### 2. .github/workflows/cd.yml (持续部署)

```yaml
name: CD

on:
push:
tags:
- "v*"
workflow_dispatch:

env:
PYTHON_VERSION: "3.11"
REGISTRY: ghcr.io
IMAGE_NAME: ${{ github.repository }}

jobs:
# 构建并发布 Docker 镜像
build-and-push:
name: Build and Push Docker Image
runs-on: ubuntu-latest
permissions:
contents: read
packages: write

steps:
- name: Checkout code
uses: actions/checkout@v4

- name: Log in to Container Registry
uses: docker/login-action@v3
with:
registry: ${{ env.REGISTRY }}
username: ${{ github.actor }}
password: ${{ secrets.GITHUB_TOKEN }}

- name: Extract metadata
id: meta
uses: docker/metadata-action@v5
with:
images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
tags: |
type=semver,pattern={{version}}
type=semver,pattern={{major}}.{{minor}}
type=sha,prefix={{branch}}-

- name: Set up Docker Buildx
uses: docker/setup-buildx-action@v3

- name: Build and push
uses: docker/build-push-action@v5
with:
context: .
file: ./docker/Dockerfile
push: true
tags: ${{ steps.meta.outputs.tags }}
labels: ${{ steps.meta.outputs.labels }}
cache-from: type=gha
cache-to: type=gha,mode=max

# 部署到生产环境
deploy:
name: Deploy to Production
runs-on: ubuntu-latest
needs: build-and-push
environment:
name: production
url: https://scraper.example.com

steps:
- name: Checkout code
uses: actions/checkout@v4

- name: Setup SSH
uses: webfactory/ssh-agent@v0.9.0
with:
ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}

- name: Deploy to server
run: |
ssh -o StrictHostKeyChecking=no ${{ secrets.SSH_USER }}@${{ secrets.SSH_HOST }} << 'EOF'
cd /opt/scraper
docker-compose pull
docker-compose up -d
docker-compose ps
EOF

- name: Health check
run: |
sleep 10
curl -f https://scraper.example.com/health || exit 1

- name: Notify deployment
if: always()
uses: 8398a7/action-slack@v3
with:
status: ${{ job.status }}
text: "Deployment ${{ job.status }}"
webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### 3. .github/workflows/docker-publish.yml

```yaml
name: Publish Docker Image

on:
release:
types: [published]

jobs:
push-to-registry:
name: Push to Docker Hub
runs-on: ubuntu-latest

steps:
- uses: actions/checkout@v4

- name: Log in to Docker Hub
uses: docker/login-action@v3
with:
username: ${{ secrets.DOCKER_USERNAME }}
password: ${{ secrets.DOCKER_PASSWORD }}

- name: Extract metadata
id: meta
uses: docker/metadata-action@v5
with:
images: ${{ secrets.DOCKER_USERNAME }}/scraper
tags: |
type=semver,pattern={{version}}
type=semver,pattern={{major}}.{{minor}}
type=raw,value=latest

- name: Build and push
uses: docker/build-push-action@v5
with:
context: .
push: true
tags: ${{ steps.meta.outputs.tags }}
labels: ${{ steps.meta.outputs.labels }}
```

---

## GitLab CI

### .gitlab-ci.yml

```yaml
# 定义阶段
stages:
- lint
- test
- build
- deploy

# 全局变量
variables:
PYTHON_VERSION: "3.11"
PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"
DOCKER_DRIVER: overlay2
DOCKER_TLS_CERTDIR: "/certs"

# 缓存配置
cache:
paths:
- .cache/pip
- venv/

# 代码质量检查
lint:flake8:
stage: lint
image: python:$PYTHON_VERSION
before_script:
- pip install flake8 black mypy
script:
- black --check .
- flake8 . --count --statistics
- mypy . --ignore-missing-imports
only:
- merge_requests
- main
- develop

# 单元测试
test:unit:
stage: test
image: python:$PYTHON_VERSION
services:
- mongo:7.0
- redis:7-alpine
variables:
MONGODB_URI: "mongodb://mongo:27017/"
REDIS_HOST: "redis"
before_script:
- python -m venv venv
- source venv/bin/activate
- pip install -r requirements.txt -r requirements-dev.txt
script:
- pytest tests/unit/ --cov=app --cov-report=xml --cov-report=term
coverage: '/^TOTAL.+?(\d+\%)$/'
artifacts:
reports:
coverage_report:
coverage_format: cobertura
path: coverage.xml
paths:
- htmlcov/
expire_in: 1 week

# 集成测试
test:integration:
stage: test
image: python:$PYTHON_VERSION
services:
- mongo:7.0
- redis:7-alpine
before_script:
- python -m venv venv
- source venv/bin/activate
- pip install -r requirements.txt -r requirements-dev.txt
script:
- pytest tests/integration/ -v
only:
- merge_requests
- main

# 安全扫描
security:scan:
stage: test
image: python:$PYTHON_VERSION
before_script:
- pip install safety bandit
script:
- safety check
- bandit -r app/ -f json -o bandit-report.json
artifacts:
paths:
- bandit-report.json
expire_in: 1 week
allow_failure: true

# 构建 Docker 镜像
build:docker:
stage: build
image: docker:24-dind
services:
- docker:24-dind
before_script:
- docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
script:
- docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA -f docker/Dockerfile .
- docker tag $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA $CI_REGISTRY_IMAGE:latest
- docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
- docker push $CI_REGISTRY_IMAGE:latest
only:
- main
- tags

# 部署到测试环境
deploy:staging:
stage: deploy
image: alpine:latest
before_script:
- apk add --no-cache openssh-client
- eval $(ssh-agent -s)
- echo "$SSH_PRIVATE_KEY" | tr -d '\r' | ssh-add -
- mkdir -p ~/.ssh
- chmod 700 ~/.ssh
script:
- ssh -o StrictHostKeyChecking=no $SSH_USER@$STAGING_HOST "
cd /opt/scraper &&
docker-compose pull &&
docker-compose up -d
"
environment:
name: staging
url: https://staging.scraper.example.com
only:
- develop

# 部署到生产环境
deploy:production:
stage: deploy
image: alpine:latest
before_script:
- apk add --no-cache openssh-client
- eval $(ssh-agent -s)
- echo "$SSH_PRIVATE_KEY" | tr -d '\r' | ssh-add -
script:
- ssh -o StrictHostKeyChecking=no $SSH_USER@$PRODUCTION_HOST "
cd /opt/scraper &&
docker-compose pull &&
docker-compose up -d &&
docker-compose ps
"
environment:
name: production
url: https://scraper.example.com
when: manual
only:
- main
- tags
```

---

## Jenkins Pipeline

### Jenkinsfile

```groovy
pipeline {
agent any

environment {
PYTHON_VERSION = '3.11'
DOCKER_REGISTRY = 'docker.io'
DOCKER_IMAGE = 'myuser/scraper'
DOCKER_CREDENTIALS = credentials('docker-hub-credentials')
}

options {
buildDiscarder(logRotator(numToKeepStr: '10'))
timestamps()
timeout(time: 1, unit: 'HOURS')
}

stages {
stage('Checkout') {
steps {
checkout scm
sh 'git rev-parse --short HEAD > .git/commit-id'
script {
env.GIT_COMMIT_ID = readFile('.git/commit-id').trim()
}
}
}

stage('Setup Python') {
steps {
sh '''
python${PYTHON_VERSION} -m venv venv
. venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt -r requirements-dev.txt
'''
}
}

stage('Lint') {
parallel {
stage('Black') {
steps {
sh '''
. venv/bin/activate
black --check .
'''
}
}
stage('Flake8') {
steps {
sh '''
. venv/bin/activate
flake8 . --count --statistics
'''
}
}
stage('MyPy') {
steps {
sh '''
. venv/bin/activate
mypy . --ignore-missing-imports
'''
}
}
}
}

stage('Test') {
steps {
sh '''
. venv/bin/activate
pytest tests/ \
--cov=app \
--cov-report=xml \
--cov-report=html \
--junitxml=junit.xml
'''
}
post {
always {
junit 'junit.xml'
publishHTML(target: [
allowMissing: false,
alwaysLinkToLastBuild: true,
keepAll: true,
reportDir: 'htmlcov',
reportFiles: 'index.html',
reportName: 'Coverage Report'
])
}
}
}

stage('Security Scan') {
steps {
sh '''
. venv/bin/activate
safety check || true
bandit -r app/ -f json -o bandit-report.json || true
'''
}
post {
always {
archiveArtifacts artifacts: 'bandit-report.json', allowEmptyArchive: true
}
}
}

stage('Build Docker') {
steps {
script {
docker.build("${DOCKER_IMAGE}:${GIT_COMMIT_ID}", "-f docker/Dockerfile .")
docker.build("${DOCKER_IMAGE}:latest", "-f docker/Dockerfile .")
}
}
}

stage('Push Docker') {
when {
branch 'main'
}
steps {
script {
docker.withRegistry('', 'docker-hub-credentials') {
docker.image("${DOCKER_IMAGE}:${GIT_COMMIT_ID}").push()
docker.image("${DOCKER_IMAGE}:latest").push()
}
}
}
}

stage('Deploy to Staging') {
when {
branch 'develop'
}
steps {
sshagent(['ssh-credentials']) {
sh '''
ssh -o StrictHostKeyChecking=no user@staging-host "
cd /opt/scraper &&
docker-compose pull &&
docker-compose up -d
"
'''
}
}
}

stage('Deploy to Production') {
when {
branch 'main'
}
steps {
input message: 'Deploy to production?', ok: 'Deploy'
sshagent(['ssh-credentials']) {
sh '''
ssh -o StrictHostKeyChecking=no user@production-host "
cd /opt/scraper &&
docker-compose pull &&
docker-compose up -d &&
docker-compose ps
"
'''
}
}
}
}

post {
always {
cleanWs()
}
success {
slackSend(
color: 'good',
message: "✅ Build ${env.JOB_NAME} #${env.BUILD_NUMBER} succeeded"
)
}
failure {
slackSend(
color: 'danger',
message: "❌ Build ${env.JOB_NAME} #${env.BUILD_NUMBER} failed"
)
}
}
}
```

---

## 辅助脚本

### scripts/run_tests.sh

```bash
#!/bin/bash
set -e

echo " Running tests..."

# 激活虚拟环境
source venv/bin/activate

# 运行测试
pytest tests/ \
--cov=app \
--cov-report=xml \
--cov-report=html \
--cov-report=term \
--junitxml=junit.xml \
-v

echo "✅ Tests completed!"
```

### scripts/build.sh

```bash
#!/bin/bash
set -e

echo " Building Docker image..."

# 获取 Git 信息
GIT_COMMIT=$(git rev-parse --short HEAD)
GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# 构建镜像
docker build \
--build-arg GIT_COMMIT=$GIT_COMMIT \
--build-arg GIT_BRANCH=$GIT_BRANCH \
--build-arg BUILD_DATE=$BUILD_DATE \
-t scraper:$GIT_COMMIT \
-t scraper:latest \
-f docker/Dockerfile \
.

echo "✅ Build completed!"
echo "Image tags: scraper:$GIT_COMMIT, scraper:latest"
```

### scripts/deploy.sh

```bash
#!/bin/bash
set -e

ENVIRONMENT=${1:-staging}

echo " Deploying to $ENVIRONMENT..."

case $ENVIRONMENT in
staging)
HOST=$STAGING_HOST
USER=$STAGING_USER
;;
production)
HOST=$PRODUCTION_HOST
USER=$PRODUCTION_USER
read -p "⚠️ Deploy to PRODUCTION? (yes/no) " -n 3 -r
echo
if [[ ! $REPLY =~ ^yes$ ]]; then
echo "Deployment cancelled"
exit 1
fi
;;
*)
echo "Unknown environment: $ENVIRONMENT"
exit 1
;;
esac

# 部署
ssh $USER@$HOST << 'EOF'
cd /opt/scraper
docker-compose pull
docker-compose up -d
docker-compose ps
echo "✅ Deployment completed!"
EOF

# 健康检查
echo " Running health check..."
sleep 10
if curl -f http://$HOST/health; then
echo "✅ Health check passed!"
else
echo "❌ Health check failed!"
exit 1
fi
```

---

## 配置说明

### GitHub Secrets 配置

需要在 GitHub 仓库设置以下 Secrets:

```
DOCKER_USERNAME # Docker Hub 用户名
DOCKER_PASSWORD # Docker Hub 密码
SSH_PRIVATE_KEY # SSH 私钥
SSH_USER # SSH 用户名
SSH_HOST # 服务器地址
SLACK_WEBHOOK # Slack 通知 Webhook
```

### GitLab CI/CD Variables

需要在 GitLab 项目设置以下变量:

```
SSH_PRIVATE_KEY # SSH 私钥
SSH_USER # SSH 用户名
STAGING_HOST # 测试环境地址
PRODUCTION_HOST # 生产环境地址
```

### Jenkins 凭据

需要在 Jenkins 配置以下凭据:

- `docker-hub-credentials`: Docker Hub 用户名和密码
- `ssh-credentials`: SSH 私钥

---

## 最佳实践

1. **分支策略**: 使用 GitFlow 或 GitHub Flow
2. **代码审查**: 所有 PR 必须通过 CI 检查
3. **自动化测试**: 保持测试覆盖率 > 80%
4. **安全扫描**: 定期检查依赖漏洞
5. **版本管理**: 使用语义化版本
6. **回滚机制**: 保留最近 5 个版本的镜像

---

## 相关资源

- [Docker 部署](./docker_setup.md)
- [监控告警](../06-Engineering/monitoring_and_alerting.md)
- [GitHub Actions 文档](https://docs.github.com/actions)
- [GitLab CI 文档](https://docs.gitlab.com/ee/ci/)
- [Jenkins 文档](https://www.jenkins.io/doc/)
