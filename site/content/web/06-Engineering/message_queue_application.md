---
title: "消息队列应用"
date: 2025-04-27
type: posts
tags: ["Web", "Docker", "工程实践", "分布式", "DEX", "部署"]
weight: 10
---

# 消息队列应用

## 概述

消息队列是分布式爬虫系统的核心组件，用于解耦生产者和消费者、削峰填谷、异步处理。本章介绍常见消息队列的使用。

---

## 消息队列对比

| 特性 | RabbitMQ | Kafka | Redis | Celery |
| ------------ | ------------ | ---------------- | ---------- | ----------- |
| **性能** | 中等 | 极高 | 高 | 中等 |
| **可靠性** | 高 | 高 | 中 | 中 |
| **消息顺序** | 支持 | 强保证 | 不保证 | 不保证 |
| **持久化** | 支持 | 支持 | 可选 | 依赖 Broker |
| **适用场景** | 通用消息队列 | 日志收集、流处理 | 轻量级队列 | 异步任务 |

---

## RabbitMQ

### 基本概念

- **Producer**: 生产者，发送消息
- **Consumer**: 消费者，接收消息
- **Exchange**: 交换机，路由消息
- **Queue**: 队列，存储消息
- **Binding**: 绑定，Exchange 和 Queue 的关系

### 安装启动

```bash
# Docker 启动
docker run -d --name rabbitmq \
-p 5672:5672 \
-p 15672:15672 \
rabbitmq:3-management

# 访问管理界面
# http://localhost:15672
# 默认账号: guest/guest
```

### Python 客户端

```python
import pika
import json

class RabbitMQClient:
def __init__(self, host='localhost'):
self.connection = pika.BlockingConnection(
pika.ConnectionParameters(host=host)
)
self.channel = self.connection.channel()

def declare_queue(self, queue_name):
"""声明队列"""
self.channel.queue_declare(
queue=queue_name,
durable=True # 持久化
)

def publish(self, queue_name, message):
"""发布消息"""
self.channel.basic_publish(
exchange='',
routing_key=queue_name,
body=json.dumps(message),
properties=pika.BasicProperties(
delivery_mode=2, # 消息持久化
)
)

def consume(self, queue_name, callback):
"""消费消息"""
self.channel.basic_qos(prefetch_count=1)
self.channel.basic_consume(
queue=queue_name,
on_message_callback=callback
)
self.channel.start_consuming()

def close(self):
self.connection.close()

# 生产者
producer = RabbitMQClient()
producer.declare_queue('urls')
producer.publish('urls', {'url': 'https://example.com', 'depth': 0})

# 消费者
def process_url(ch, method, properties, body):
message = json.loads(body)
print(f"Processing: {message['url']}")
# 处理完成后确认
ch.basic_ack(delivery_tag=method.delivery_tag)

consumer = RabbitMQClient()
consumer.consume('urls', process_url)
```

### Topic Exchange 示例

```python
class TopicExchangeClient:
def __init__(self):
self.connection = pika.BlockingConnection(
pika.ConnectionParameters('localhost')
)
self.channel = self.connection.channel()

# 声明 Topic Exchange
self.channel.exchange_declare(
exchange='scraper_topics',
exchange_type='topic',
durable=True
)

def publish_with_routing(self, routing_key, message):
"""发布带路由的消息"""
self.channel.basic_publish(
exchange='scraper_topics',
routing_key=routing_key,
body=json.dumps(message)
)

def subscribe_pattern(self, pattern, callback):
"""订阅符合模式的消息"""
result = self.channel.queue_declare('', exclusive=True)
queue_name = result.method.queue

self.channel.queue_bind(
exchange='scraper_topics',
queue=queue_name,
routing_key=pattern
)

self.channel.basic_consume(
queue=queue_name,
on_message_callback=callback,
auto_ack=True
)
self.channel.start_consuming()

# 使用
client = TopicExchangeClient()

# 发布不同类型的消息
client.publish_with_routing('news.tech', {'title': 'Tech News'})
client.publish_with_routing('news.sports', {'title': 'Sports News'})
client.publish_with_routing('video.movie', {'title': 'Movie Title'})

# 订阅所有新闻
client.subscribe_pattern('news.*', callback)

# 订阅所有消息
client.subscribe_pattern('#', callback)
```

---

## Kafka

### 适用场景

- 大规模日志收集
- 实时数据流处理
- 高吞吐量消息传递

### 启动 Kafka

```bash
# Docker Compose
version: '3'
services:
zookeeper:
image: confluentinc/cp-zookeeper:latest
environment:
ZOOKEEPER_CLIENT_PORT: 2181

kafka:
image: confluentinc/cp-kafka:latest
depends_on:
- zookeeper
ports:
- "9092:9092"
environment:
KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
```

### Python 客户端

```python
from kafka import KafkaProducer, KafkaConsumer
import json

class KafkaClient:
def __init__(self, bootstrap_servers='localhost:9092'):
self.bootstrap_servers = bootstrap_servers

def get_producer(self):
"""获取生产者"""
return KafkaProducer(
bootstrap_servers=self.bootstrap_servers,
value_serializer=lambda v: json.dumps(v).encode('utf-8'),
acks='all', # 等待所有副本确认
retries=3
)

def get_consumer(self, topic, group_id='scraper-group'):
"""获取消费者"""
return KafkaConsumer(
topic,
bootstrap_servers=self.bootstrap_servers,
group_id=group_id,
value_deserializer=lambda m: json.loads(m.decode('utf-8')),
auto_offset_reset='earliest',
enable_auto_commit=True
)

# 生产者
client = KafkaClient()
producer = client.get_producer()

# 发送消息
for i in range(100):
message = {'url': f'https://example.com/page/{i}', 'index': i}
producer.send('scraper-urls', value=message)

producer.flush()
producer.close()

# 消费者
consumer = client.get_consumer('scraper-urls')

for message in consumer:
data = message.value
print(f"Processing: {data['url']}")
```

---

## Celery

### 安装配置

```bash
pip install celery[redis]
```

### 定义任务

```python
# tasks.py
from celery import Celery
import requests

app = Celery(
'scraper',
broker='redis://localhost:6379/0',
backend='redis://localhost:6379/1'
)

app.conf.update(
task_serializer='json',
accept_content=['json'],
result_serializer='json',
timezone='Asia/Shanghai',
enable_utc=True,
)

@app.task(bind=True, max_retries=3)
def scrape_url(self, url):
"""爬取 URL 任务"""
try:
response = requests.get(url, timeout=10)
return {
'url': url,
'status_code': response.status_code,
'content_length': len(response.content)
}
except Exception as exc:
# 重试
raise self.retry(exc=exc, countdown=60)

@app.task
def process_data(data):
"""处理数据任务"""
print(f"Processing: {data}")
return {'status': 'processed'}

# 任务链
@app.task
def save_to_db(result):
"""保存到数据库"""
print(f"Saving: {result}")
return {'status': 'saved'}
```

### 启动 Worker

```bash
# 启动 Celery Worker
celery -A tasks worker --loglevel=info

# 启动多个 Worker
celery -A tasks worker --concurrency=10

# 启动 Flower (监控工具)
celery -A tasks flower
```

### 调用任务

```python
from tasks import scrape_url, process_data, save_to_db

# 异步调用
result = scrape_url.delay('https://example.com')

# 获取结果
print(result.get(timeout=10))

# 任务链
from celery import chain

workflow = chain(
scrape_url.s('https://example.com'),
process_data.s(),
save_to_db.s()
)
result = workflow.apply_async()

# 任务组（并行）
from celery import group

job = group([
scrape_url.s(f'https://example.com/page/{i}')
for i in range(10)
])
result = job.apply_async()
```

### 定时任务

```python
from celery.schedules import crontab

app.conf.beat_schedule = {
'scrape-every-hour': {
'task': 'tasks.scrape_url',
'schedule': crontab(minute=0), # 每小时执行
'args': ('https://example.com',)
},
'cleanup-every-day': {
'task': 'tasks.cleanup',
'schedule': crontab(hour=0, minute=0), # 每天凌晨
},
}

# 启动 Beat
# celery -A tasks beat --loglevel=info
```

---

## 最佳实践

### 1. 消息持久化

```python
# 队列持久化
channel.queue_declare(queue='urls', durable=True)

# 消息持久化
channel.basic_publish(
exchange='',
routing_key='urls',
body=message,
properties=pika.BasicProperties(delivery_mode=2)
)
```

### 2. 消息确认

```python
# 手动确认
channel.basic_consume(
queue='urls',
on_message_callback=callback,
auto_ack=False # 禁用自动确认
)

def callback(ch, method, properties, body):
# 处理消息
process(body)
# 确认
ch.basic_ack(delivery_tag=method.delivery_tag)
```

### 3. 限流控制

```python
# 预取数量限制
channel.basic_qos(prefetch_count=1)
```

### 4. 死信队列

```python
# 声明死信队列
channel.queue_declare(queue='dead_letter_queue', durable=True)

# 配置主队列
channel.queue_declare(
queue='urls',
durable=True,
arguments={
'x-dead-letter-exchange': '',
'x-dead-letter-routing-key': 'dead_letter_queue',
'x-message-ttl': 60000 # 60秒后过期
}
)
```

---

## 相关章节

- [分布式爬虫架构](./distributed_scraping.md)
- [监控与告警系统](./monitoring_and_alerting.md)
- [Docker 容器化部署](./docker_deployment.md)
