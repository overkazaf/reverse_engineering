---
title: "监控与告警系统"
date: 2025-08-13
type: posts
tags: ["Web", "Docker", "代理池", "工程实践", "Hook", "分布式"]
weight: 10
---

# 监控与告警系统

## 概述

监控和告警是保障分布式爬虫系统稳定运行的关键。本章介绍如何构建完整的监控和告警体系。

---

## 监控体系架构

```
┌──────────────────────────────────────┐
│ Scraper Nodes │
│ - Metrics Exporter (Prometheus) │
│ - Logging (Fluentd/Filebeat) │
└──────────┬───────────────────────────┘
│
┌──────┴──────┐
│ │
▼ ▼
┌─────────┐ ┌──────────┐
│Prometheus│ │ ELK │
│(Metrics) │ │ (Logs) │
└────┬────┘ └────┬─────┘
│ │
└──────┬─────┘
▼
┌─────────────┐
│ Grafana │
│ (可视化) │
└─────────────┘
│
▼
┌─────────────┐
│ AlertManager│
│ (告警) │
└─────────────┘
```

---

## Prometheus 监控

### 安装部署

```yaml
# docker-compose.yml
version: "3"
services:
prometheus:
image: prom/prometheus:latest
ports:
- "9090:9090"
volumes:
- ./prometheus.yml:/etc/prometheus/prometheus.yml
- prometheus_data:/prometheus
command:
- "--config.file=/etc/prometheus/prometheus.yml"
- "--storage.tsdb.path=/prometheus"

grafana:
image: grafana/grafana:latest
ports:
- "3000:3000"
volumes:
- grafana_data:/var/lib/grafana
environment:
- GF_SECURITY_ADMIN_PASSWORD=admin

volumes:
prometheus_data:
grafana_data:
```

### Prometheus 配置

```yaml
# prometheus.yml
global:
scrape_interval: 15s
evaluation_interval: 15s

scrape_configs:
- job_name: "scraper"
static_configs:
- targets: ["scraper:8000"]

- job_name: "redis"
static_configs:
- targets: ["redis-exporter:9121"]

- job_name: "mongodb"
static_configs:
- targets: ["mongodb-exporter:9216"]

- job_name: "node"
static_configs:
- targets: ["node-exporter:9100"]
```

### Python 应用集成

```python
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time

# 定义指标
requests_total = Counter(
'scraper_requests_total',
'Total number of requests',
['status', 'domain']
)

request_duration = Histogram(
'scraper_request_duration_seconds',
'Request duration in seconds',
['domain']
)

active_scrapers = Gauge(
'scraper_active_workers',
'Number of active scrapers'
)

queue_size = Gauge(
'scraper_queue_size',
'Size of the URL queue'
)

class MonitoredScraper:
def __init__(self):
# 启动 Prometheus HTTP 服务器
start_http_server(8000)

def scrape(self, url):
"""爬取 URL 并记录指标"""
domain = self._extract_domain(url)

# 记录活跃爬虫数
active_scrapers.inc()

try:
# 记录请求时长
with request_duration.labels(domain=domain).time():
response = requests.get(url, timeout=10)

# 记录请求总数
requests_total.labels(
status=response.status_code,
domain=domain
).inc()

return response

except Exception as e:
requests_total.labels(status='error', domain=domain).inc()
raise
finally:
active_scrapers.dec()

def update_queue_size(self, size):
"""更新队列大小"""
queue_size.set(size)

def _extract_domain(self, url):
from urllib.parse import urlparse
return urlparse(url).netloc
```

---

## Grafana 可视化

### 仪表盘配置

```json
{
"dashboard": {
"title": "Scraper Monitoring",
"panels": [
{
"title": "Request Rate",
"targets": [
{
"expr": "rate(scraper_requests_total[5m])"
}
]
},
{
"title": "Success Rate",
"targets": [
{
"expr": "scraper_success_rate"
}
]
},
{
"title": "Queue Size",
"targets": [
{
"expr": "scraper_queue_size"
}
]
},
{
"title": "P95 Response Time",
"targets": [
{
"expr": "histogram_quantile(0.95, rate(scraper_request_duration_seconds_bucket[5m]))"
}
]
}
]
}
}
```

---

## 日志收集 (ELK Stack)

### Docker Compose 配置

```yaml
version: "3"
services:
elasticsearch:
image: elasticsearch:8.11.0
environment:
- discovery.type=single-node
- xpack.security.enabled=false
ports:
- "9200:9200"
volumes:
- es_data:/usr/share/elasticsearch/data

logstash:
image: logstash:8.11.0
ports:
- "5044:5044"
volumes:
- ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf

kibana:
image: kibana:8.11.0
ports:
- "5601:5601"
environment:
- ELASTICSEARCH_HOSTS=http://elasticsearch:9200

filebeat:
image: elastic.co/beats/filebeat:8.11.0
volumes:
- ./filebeat.yml:/usr/share/filebeat/filebeat.yml
- /var/log:/var/log:ro
- /var/lib/docker/containers:/var/lib/docker/containers:ro

volumes:
es_data:
```

---

## 告警配置

### AlertManager 配置

```yaml
# alertmanager.yml
global:
resolve_timeout: 5m

route:
group_by: ["alertname"]
group_wait: 10s
group_interval: 10s
repeat_interval: 1h
receiver: "email"

receivers:
- name: "email"
email_configs:
- to: "admin@example.com"
from: "alertmanager@example.com"
smarthost: "smtp.example.com:587"
auth_username: "alertmanager@example.com"
auth_password: "password"

- name: "slack"
slack_configs:
- api_url: "https://hooks.slack.com/services/xxx"
channel: "#alerts"
title: "Scraper Alert"
```

### Prometheus 告警规则

```yaml
# alerts.yml
groups:
- name: scraper_alerts
interval: 30s
rules:
# 成功率告警
- alert: LowSuccessRate
expr: scraper_success_rate < 0.8
for: 5m
labels:
severity: warning
annotations:
summary: "Success rate is low"
description: "Success rate is {{ $value }}"

# 队列堆积告警
- alert: QueueBacklog
expr: scraper_queue_size > 10000
for: 10m
labels:
severity: warning
annotations:
summary: "Queue is backing up"
description: "Queue size: {{ $value }}"

# 高错误率告警
- alert: HighErrorRate
expr: rate(scraper_errors_total[5m]) > 10
for: 5m
labels:
severity: critical
annotations:
summary: "High error rate detected"
description: "Error rate: {{ $value }} errors/s"

# Worker 宕机告警
- alert: WorkerDown
expr: scraper_active_workers == 0
for: 1m
labels:
severity: critical
annotations:
summary: "No active workers"
```

---

## 健康检查

### HTTP 健康检查端点

```python
from flask import Flask, jsonify
import redis

app = Flask(__name__)
r = redis.Redis()

@app.route('/health')
def health():
"""健康检查"""
checks = {
'redis': check_redis(),
'queue': check_queue(),
'workers': check_workers()
}

all_healthy = all(checks.values())
status_code = 200 if all_healthy else 503

return jsonify({
'status': 'healthy' if all_healthy else 'unhealthy',
'checks': checks
}), status_code

def check_redis():
"""检查 Redis 连接"""
try:
r.ping()
return True
except:
return False

def check_queue():
"""检查队列状态"""
try:
size = r.llen('urls')
return size < 50000 # 队列未过载
except:
return False

def check_workers():
"""检查 Worker 状态"""
try:
active = int(r.get('active_workers') or 0)
return active > 0
except:
return False

if __name__ == '__main__':
app.run(host='0.0.0.0', port=8080)
```

---

## 相关章节

- [分布式爬虫架构](./distributed_scraping.md)
- [Docker 容器化部署](./docker_deployment.md)
- [代理池管理](./proxy_pool_management.md)
