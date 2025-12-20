#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

BASE_DIR = "/Users/nongjiawu/frida/reverse_engineering/web_reversing/docs/04-Engineering"

docs = {
    "data_storage_solutions.md": """# 数据存储方案

## 概述

爬虫系统需要高效的数据存储方案来处理海量数据。本章介绍常见的存储选型和最佳实践。

---

## 存储选型

### 关系型数据库 vs NoSQL

| 特性 | 关系型数据库 | NoSQL |
|------|------------|-------|
| **数据模型** | 表格、严格schema | 文档、键值、列族 |
| **扩展性** | 垂直扩展 | 水平扩展 |
| **事务支持** | ACID 完整支持 | 部分支持 |
| **查询能力** | 强大的 SQL | 受限的查询语言 |
| **适用场景** | 结构化数据、复杂关联 | 海量数据、高并发写入 |

---

## MySQL

### 适用场景

- 结构化数据存储
- 需要复杂关联查询
- 事务要求高
- 数据量在千万级以下

### 表设计示例

```sql
-- 用户表
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 文章表
CREATE TABLE articles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    view_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at),
    FULLTEXT INDEX idx_content (title, content)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### Python 操作示例

```python
import pymysql
from dbutils.pooled_db import PooledDB

class MySQLStorage:
    def __init__(self, host='localhost', port=3306, user='root',
                 password='', database='scraper'):
        self.pool = PooledDB(
            creator=pymysql,
            maxconnections=20,
            mincached=2,
            maxcached=5,
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

    def insert_article(self, article):
        """插入文章"""
        conn = self.pool.connection()
        try:
            with conn.cursor() as cursor:
                sql = """
                INSERT INTO articles (user_id, title, content, view_count)
                VALUES (%(user_id)s, %(title)s, %(content)s, %(view_count)s)
                """
                cursor.execute(sql, article)
                conn.commit()
                return cursor.lastrowid
        finally:
            conn.close()

    def batch_insert(self, articles):
        """批量插入"""
        conn = self.pool.connection()
        try:
            with conn.cursor() as cursor:
                sql = """
                INSERT INTO articles (user_id, title, content)
                VALUES (%(user_id)s, %(title)s, %(content)s)
                """
                cursor.executemany(sql, articles)
                conn.commit()
        finally:
            conn.close()

    def query_by_user(self, user_id, limit=10):
        """查询用户文章"""
        conn = self.pool.connection()
        try:
            with conn.cursor() as cursor:
                sql = """
                SELECT * FROM articles
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT %s
                """
                cursor.execute(sql, (user_id, limit))
                return cursor.fetchall()
        finally:
            conn.close()
```

---

## MongoDB

### 适用场景

- 半结构化数据
- Schema 经常变动
- 需要水平扩展
- 读写性能要求高

### 文档设计示例

```javascript
// 用户文档
{
  "_id": ObjectId("507f1f77bcf86cd799439011"),
  "username": "john_doe",
  "email": "john@example.com",
  "profile": {
    "age": 30,
    "location": "Beijing"
  },
  "tags": ["tech", "science"],
  "created_at": ISODate("2024-01-01T00:00:00Z")
}

// 文章文档
{
  "_id": ObjectId("507f191e810c19729de860ea"),
  "user_id": ObjectId("507f1f77bcf86cd799439011"),
  "title": "Web 逆向入门",
  "content": "...",
  "tags": ["逆向", "爬虫"],
  "stats": {
    "views": 1000,
    "likes": 50
  },
  "comments": [
    {
      "user": "alice",
      "text": "Great article!",
      "date": ISODate("2024-01-02T00:00:00Z")
    }
  ],
  "created_at": ISODate("2024-01-01T00:00:00Z")
}
```

### Python 操作示例

```python
from pymongo import MongoClient, ASCENDING, DESCENDING
from datetime import datetime

class MongoStorage:
    def __init__(self, uri='mongodb://localhost:27017/', db_name='scraper'):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.articles = self.db.articles

        # 创建索引
        self.articles.create_index([('user_id', ASCENDING)])
        self.articles.create_index([('created_at', DESCENDING)])
        self.articles.create_index([('title', 'text'), ('content', 'text')])

    def insert_article(self, article):
        """插入文章"""
        article['created_at'] = datetime.now()
        result = self.articles.insert_one(article)
        return result.inserted_id

    def batch_insert(self, articles):
        """批量插入"""
        for article in articles:
            article['created_at'] = datetime.now()
        result = self.articles.insert_many(articles)
        return result.inserted_ids

    def find_by_user(self, user_id, limit=10):
        """查询用户文章"""
        cursor = self.articles.find(
            {'user_id': user_id}
        ).sort('created_at', DESCENDING).limit(limit)
        return list(cursor)

    def update_views(self, article_id):
        """更新浏览量"""
        self.articles.update_one(
            {'_id': article_id},
            {'$inc': {'stats.views': 1}}
        )

    def text_search(self, keyword):
        """全文搜索"""
        cursor = self.articles.find(
            {'$text': {'$search': keyword}}
        ).limit(20)
        return list(cursor)

    def aggregate_stats(self):
        """聚合统计"""
        pipeline = [
            {'$group': {
                '_id': '$user_id',
                'total_articles': {'$sum': 1},
                'total_views': {'$sum': '$stats.views'}
            }},
            {'$sort': {'total_views': -1}},
            {'$limit': 10}
        ]
        return list(self.articles.aggregate(pipeline))
```

---

## Redis

### 适用场景

- 缓存热点数据
- 分布式锁
- 消息队列
- 计数器、排行榜
- Session 存储

### 使用示例

```python
import redis
import json
import pickle
from functools import wraps

class RedisStorage:
    def __init__(self, host='localhost', port=6379, db=0):
        self.r = redis.Redis(host=host, port=port, db=db, decode_responses=False)

    def cache_result(self, key, data, expire=3600):
        """缓存数据"""
        self.r.setex(key, expire, pickle.dumps(data))

    def get_cache(self, key):
        """获取缓存"""
        data = self.r.get(key)
        if data:
            return pickle.loads(data)
        return None

    def cache_decorator(self, expire=3600):
        """缓存装饰器"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cache_key = f"{func.__name__}:{args}:{kwargs}"
                result = self.get_cache(cache_key)
                if result is not None:
                    return result

                result = func(*args, **kwargs)
                self.cache_result(cache_key, result, expire)
                return result
            return wrapper
        return decorator

    def incr_counter(self, key):
        """计数器"""
        return self.r.incr(key)

    def add_to_set(self, key, *values):
        """添加到集合（去重）"""
        return self.r.sadd(key, *values)

    def is_crawled(self, url):
        """检查 URL 是否已爬取"""
        return self.r.sismember('crawled_urls', url)

    def mark_as_crawled(self, url):
        """标记 URL 已爬取"""
        self.r.sadd('crawled_urls', url)

    def add_to_queue(self, queue_name, item):
        """添加到队列"""
        self.r.lpush(queue_name, json.dumps(item))

    def get_from_queue(self, queue_name, timeout=0):
        """从队列获取"""
        result = self.r.brpop(queue_name, timeout=timeout)
        if result:
            return json.loads(result[1])
        return None

    def sorted_set_add(self, key, score, member):
        """添加到有序集合（排行榜）"""
        self.r.zadd(key, {member: score})

    def get_top_n(self, key, n=10):
        """获取排行榜前 N 名"""
        return self.r.zrevrange(key, 0, n-1, withscores=True)
```

---

## Elasticsearch

### 适用场景

- 全文搜索
- 日志分析
- 实时数据分析
- 大规模数据检索

### 索引设计示例

```python
from elasticsearch import Elasticsearch
from datetime import datetime

class ElasticsearchStorage:
    def __init__(self, hosts=['localhost:9200']):
        self.es = Elasticsearch(hosts)
        self.index_name = 'articles'
        self._create_index()

    def _create_index(self):
        """创建索引"""
        if not self.es.indices.exists(index=self.index_name):
            mapping = {
                'mappings': {
                    'properties': {
                        'title': {
                            'type': 'text',
                            'analyzer': 'ik_max_word',
                            'search_analyzer': 'ik_smart'
                        },
                        'content': {
                            'type': 'text',
                            'analyzer': 'ik_max_word'
                        },
                        'author': {
                            'type': 'keyword'
                        },
                        'tags': {
                            'type': 'keyword'
                        },
                        'created_at': {
                            'type': 'date'
                        },
                        'view_count': {
                            'type': 'integer'
                        }
                    }
                }
            }
            self.es.indices.create(index=self.index_name, body=mapping)

    def index_document(self, doc_id, document):
        """索引文档"""
        document['created_at'] = datetime.now()
        return self.es.index(
            index=self.index_name,
            id=doc_id,
            body=document
        )

    def bulk_index(self, documents):
        """批量索引"""
        from elasticsearch.helpers import bulk

        actions = [
            {
                '_index': self.index_name,
                '_id': doc['id'],
                '_source': doc
            }
            for doc in documents
        ]
        return bulk(self.es, actions)

    def search(self, query, size=10):
        """搜索"""
        body = {
            'query': {
                'multi_match': {
                    'query': query,
                    'fields': ['title^2', 'content']
                }
            },
            'highlight': {
                'fields': {
                    'title': {},
                    'content': {}
                }
            },
            'size': size
        }
        return self.es.search(index=self.index_name, body=body)

    def search_by_tags(self, tags, size=10):
        """按标签搜索"""
        body = {
            'query': {
                'terms': {
                    'tags': tags
                }
            },
            'size': size
        }
        return self.es.search(index=self.index_name, body=body)

    def aggregate_by_author(self):
        """按作者聚合"""
        body = {
            'size': 0,
            'aggs': {
                'authors': {
                    'terms': {
                        'field': 'author',
                        'size': 10
                    },
                    'aggs': {
                        'avg_views': {
                            'avg': {
                                'field': 'view_count'
                            }
                        }
                    }
                }
            }
        }
        return self.es.search(index=self.index_name, body=body)
```

---

## 混合存储方案

### 典型架构

```
┌─────────────────────────────────────┐
│          Application Layer          │
└─────────────┬───────────────────────┘
              │
    ┌─────────┴──────────┐
    │                    │
    ▼                    ▼
┌─────────┐        ┌──────────┐
│  Redis  │        │  MySQL   │
│ (Cache) │        │ (Master) │
└─────────┘        └────┬─────┘
                        │
              ┌─────────┴─────────┐
              │                   │
              ▼                   ▼
        ┌──────────┐        ┌──────────┐
        │ MongoDB  │        │    ES    │
        │(文档存储) │        │(全文搜索) │
        └──────────┘        └──────────┘
```

### 实现示例

```python
class HybridStorage:
    def __init__(self):
        self.redis = RedisStorage()
        self.mysql = MySQLStorage()
        self.mongo = MongoStorage()
        self.es = ElasticsearchStorage()

    def save_article(self, article):
        """保存文章（多存储）"""
        # 1. MySQL 存储基本信息
        article_id = self.mysql.insert_article({
            'user_id': article['user_id'],
            'title': article['title'],
            'created_at': article['created_at']
        })

        # 2. MongoDB 存储完整文档
        article['_id'] = article_id
        self.mongo.insert_article(article)

        # 3. Elasticsearch 索引（用于搜索）
        self.es.index_document(article_id, article)

        # 4. Redis 缓存热点数据
        cache_key = f"article:{article_id}"
        self.redis.cache_result(cache_key, article, expire=3600)

        return article_id

    def get_article(self, article_id):
        """获取文章（缓存优先）"""
        # 1. 先查 Redis 缓存
        cache_key = f"article:{article_id}"
        cached = self.redis.get_cache(cache_key)
        if cached:
            return cached

        # 2. 查 MongoDB
        article = self.mongo.articles.find_one({'_id': article_id})
        if article:
            # 回写缓存
            self.redis.cache_result(cache_key, article, expire=3600)
            return article

        return None

    def search_articles(self, keyword):
        """搜索文章（使用 ES）"""
        return self.es.search(keyword)
```

---

## 性能优化

### 1. 批量操作

```python
# 批量插入
def batch_insert_optimized(articles, batch_size=1000):
    for i in range(0, len(articles), batch_size):
        batch = articles[i:i+batch_size]
        storage.batch_insert(batch)
```

### 2. 连接池

```python
# 使用连接池避免频繁创建连接
from dbutils.pooled_db import PooledDB

pool = PooledDB(
    creator=pymysql,
    maxconnections=20,
    mincached=2,
    blocking=True
)
```

### 3. 索引优化

```sql
-- 创建合适的索引
CREATE INDEX idx_user_created ON articles(user_id, created_at);

-- 分析查询性能
EXPLAIN SELECT * FROM articles WHERE user_id = 123;
```

---

## 相关章节

- [分布式爬虫架构](./distributed_scraping.md)
- [监控与告警系统](./monitoring_and_alerting.md)
- [Docker 容器化部署](./docker_deployment.md)
""",

    "message_queue_application.md": """# 消息队列应用

## 概述

消息队列是分布式爬虫系统的核心组件，用于解耦生产者和消费者、削峰填谷、异步处理。本章介绍常见消息队列的使用。

---

## 消息队列对比

| 特性 | RabbitMQ | Kafka | Redis | Celery |
|------|----------|-------|-------|--------|
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
            durable=True  # 持久化
        )

    def publish(self, queue_name, message):
        """发布消息"""
        self.channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # 消息持久化
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
            acks='all',  # 等待所有副本确认
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
        'schedule': crontab(minute=0),  # 每小时执行
        'args': ('https://example.com',)
    },
    'cleanup-every-day': {
        'task': 'tasks.cleanup',
        'schedule': crontab(hour=0, minute=0),  # 每天凌晨
    },
}

# 启动 Beat
# celery -A tasks beat --loglevel=info
```

---

## 爬虫系统集成

### 完整示例

```python
# producer.py - 生产者
import pika
import json

class URLProducer:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost')
        )
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='urls', durable=True)

    def add_url(self, url, priority=0):
        """添加 URL 到队列"""
        message = {
            'url': url,
            'priority': priority,
            'retry_count': 0
        }
        self.channel.basic_publish(
            exchange='',
            routing_key='urls',
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,
                priority=priority
            )
        )

    def add_urls_batch(self, urls):
        """批量添加 URL"""
        for url in urls:
            self.add_url(url)

# consumer.py - 消费者
import pika
import json
import requests

class URLConsumer:
    def __init__(self, num_workers=4):
        self.num_workers = num_workers

    def callback(self, ch, method, properties, body):
        """处理消息"""
        message = json.loads(body)
        url = message['url']

        try:
            response = requests.get(url, timeout=10)
            print(f"✓ {url} - {response.status_code}")

            # 提取新的 URL
            # new_urls = extract_urls(response.text)
            # for new_url in new_urls:
            #     producer.add_url(new_url)

            # 确认消息
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            print(f"✗ {url} - {e}")

            # 重试逻辑
            if message['retry_count'] < 3:
                message['retry_count'] += 1
                ch.basic_publish(
                    exchange='',
                    routing_key='urls',
                    body=json.dumps(message)
                )

            ch.basic_ack(delivery_tag=method.delivery_tag)

    def start(self):
        """启动消费者"""
        connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost')
        )
        channel = connection.channel()
        channel.basic_qos(prefetch_count=self.num_workers)
        channel.basic_consume(
            queue='urls',
            on_message_callback=self.callback
        )
        print('Waiting for messages...')
        channel.start_consuming()

# main.py
if __name__ == '__main__':
    # 启动生产者
    producer = URLProducer()
    producer.add_urls_batch([
        'https://example.com/page/1',
        'https://example.com/page/2',
        'https://example.com/page/3',
    ])

    # 启动消费者
    consumer = URLConsumer(num_workers=4)
    consumer.start()
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
    auto_ack=False  # 禁用自动确认
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
        'x-message-ttl': 60000  # 60秒后过期
    }
)
```

---

## 相关章节

- [分布式爬虫架构](./distributed_scraping.md)
- [监控与告警系统](./monitoring_and_alerting.md)
- [Docker 容器化部署](./docker_deployment.md)
""",

    "monitoring_and_alerting.md": """# 监控与告警系统

## 概述

监控和告警是保障分布式爬虫系统稳定运行的关键。本章介绍如何构建完整的监控和告警体系。

---

## 监控体系架构

```
┌──────────────────────────────────────┐
│         Scraper Nodes                │
│  - Metrics Exporter (Prometheus)     │
│  - Logging (Fluentd/Filebeat)        │
└──────────┬───────────────────────────┘
           │
    ┌──────┴──────┐
    │             │
    ▼             ▼
┌─────────┐  ┌──────────┐
│Prometheus│  │    ELK   │
│(Metrics) │  │  (Logs)  │
└────┬────┘  └────┬─────┘
     │            │
     └──────┬─────┘
            ▼
     ┌─────────────┐
     │   Grafana   │
     │ (可视化)     │
     └─────────────┘
            │
            ▼
     ┌─────────────┐
     │ AlertManager│
     │   (告警)     │
     └─────────────┘
```

---

## Prometheus 监控

### 安装部署

```yaml
# docker-compose.yml
version: '3'
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'

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
  - job_name: 'scraper'
    static_configs:
      - targets: ['scraper:8000']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

  - job_name: 'mongodb'
    static_configs:
      - targets: ['mongodb-exporter:9216']

  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']
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

### 自定义指标

```python
from prometheus_client import Counter, Histogram, Summary, Gauge
import redis

class ScraperMetrics:
    def __init__(self):
        self.r = redis.Redis()

        # 成功率
        self.success_rate = Gauge(
            'scraper_success_rate',
            'Success rate of scraping'
        )

        # 数据量
        self.data_collected = Counter(
            'scraper_data_collected_total',
            'Total data items collected',
            ['type']
        )

        # 响应时间分位数
        self.response_time = Summary(
            'scraper_response_time_seconds',
            'Response time summary'
        )

        # 错误类型统计
        self.errors = Counter(
            'scraper_errors_total',
            'Total errors',
            ['error_type']
        )

    def calculate_success_rate(self):
        """计算成功率"""
        total = int(self.r.get('total_requests') or 0)
        success = int(self.r.get('success_requests') or 0)

        if total > 0:
            rate = success / total
            self.success_rate.set(rate)

    def record_data(self, data_type, count=1):
        """记录数据收集"""
        self.data_collected.labels(type=data_type).inc(count)

    def record_error(self, error_type):
        """记录错误"""
        self.errors.labels(error_type=error_type).inc()
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
version: '3'
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

### Logstash 配置

```ruby
# logstash.conf
input {
  beats {
    port => 5044
  }
}

filter {
  if [type] == "scraper" {
    grok {
      match => {
        "message" => "%{TIMESTAMP_ISO8601:timestamp} %{LOGLEVEL:level} %{GREEDYDATA:message}"
      }
    }

    date {
      match => [ "timestamp", "ISO8601" ]
      target => "@timestamp"
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "scraper-logs-%{+YYYY.MM.dd}"
  }
}
```

### Python 日志集成

```python
import logging
from pythonjsonlogger import jsonlogger

class ScraperLogger:
    def __init__(self):
        self.logger = logging.getLogger('scraper')
        self.logger.setLevel(logging.INFO)

        # JSON 格式输出
        handler = logging.FileHandler('/var/log/scraper/app.log')
        formatter = jsonlogger.JsonFormatter(
            '%(asctime)s %(name)s %(levelname)s %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def log_request(self, url, status_code, duration):
        """记录请求日志"""
        self.logger.info('Request completed', extra={
            'url': url,
            'status_code': status_code,
            'duration': duration,
            'type': 'scraper'
        })

    def log_error(self, url, error):
        """记录错误日志"""
        self.logger.error('Request failed', extra={
            'url': url,
            'error': str(error),
            'type': 'scraper'
        })
```

---

## 告警配置

### AlertManager 配置

```yaml
# alertmanager.yml
global:
  resolve_timeout: 5m

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'email'

receivers:
  - name: 'email'
    email_configs:
      - to: 'admin@example.com'
        from: 'alertmanager@example.com'
        smarthost: 'smtp.example.com:587'
        auth_username: 'alertmanager@example.com'
        auth_password: 'password'

  - name: 'slack'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/xxx'
        channel: '#alerts'
        title: 'Scraper Alert'

  - name: 'webhook'
    webhook_configs:
      - url: 'http://localhost:5000/webhook'
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

### Python 告警集成

```python
import requests

class AlertManager:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    def send_alert(self, title, message, level='warning'):
        """发送告警"""
        payload = {
            'title': title,
            'message': message,
            'level': level,
            'timestamp': time.time()
        }

        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=5
            )
            response.raise_for_status()
        except Exception as e:
            print(f"Failed to send alert: {e}")

    def send_slack_alert(self, channel, message):
        """发送 Slack 告警"""
        slack_webhook = 'https://hooks.slack.com/services/xxx'
        payload = {
            'channel': channel,
            'username': 'Scraper Bot',
            'text': message,
            'icon_emoji': ':warning:'
        }
        requests.post(slack_webhook, json=payload)

# 使用
alert_manager = AlertManager('http://localhost:9093/webhook')

def check_health():
    """健康检查"""
    queue_size = redis_client.llen('urls')

    if queue_size > 10000:
        alert_manager.send_alert(
            title='Queue Backlog',
            message=f'Queue size: {queue_size}',
            level='warning'
        )
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
        return size < 50000  # 队列未过载
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

## 性能分析

### 使用 cProfile

```python
import cProfile
import pstats

def profile_scraper():
    """性能分析"""
    profiler = cProfile.Profile()
    profiler.enable()

    # 运行爬虫
    scraper.run()

    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)
```

### 使用 line_profiler

```python
# 安装: pip install line_profiler

from line_profiler import LineProfiler

@profile
def scrape_url(url):
    response = requests.get(url)
    data = parse_response(response)
    save_data(data)

# 运行
# kernprof -l -v script.py
```

---

## 相关章节

- [分布式爬虫架构](./distributed_scraping.md)
- [Docker 容器化部署](./docker_deployment.md)
- [代理池管理](./proxy_pool_management.md)
""",

    "anti_anti_scraping_framework.md": """# 反反爬虫框架设计

## 概述

反反爬虫框架是一个综合性的系统，集成了多种对抗技术，用于突破各类反爬虫防护。本章介绍如何设计一个通用的反反爬虫框架。

---

## 框架架构

```
┌────────────────────────────────────────────┐
│           Scraper Application              │
└──────────────┬─────────────────────────────┘
               │
┌──────────────┴─────────────────────────────┐
│      Anti-Anti-Scraping Framework          │
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │      Request Middleware              │ │
│  │  - User-Agent Rotation               │ │
│  │  - Header Randomization              │ │
│  │  - Cookie Management                 │ │
│  └──────────────────────────────────────┘ │
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │      Proxy Manager                   │ │
│  │  - Proxy Pool                        │ │
│  │  - IP Rotation                       │ │
│  │  - Proxy Health Check                │ │
│  └──────────────────────────────────────┘ │
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │      Browser Simulator               │ │
│  │  - Puppeteer/Playwright              │ │
│  │  - Fingerprint Evasion               │ │
│  │  - Human Behavior Simulation         │ │
│  └──────────────────────────────────────┘ │
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │      CAPTCHA Solver                  │ │
│  │  - 2Captcha Integration              │ │
│  │  - OCR Recognition                   │ │
│  │  - AI Model Prediction               │ │
│  └──────────────────────────────────────┘ │
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │      Rate Limiter                    │ │
│  │  - Adaptive Delay                    │ │
│  │  - Token Bucket                      │ │
│  │  - Request Scheduling                │ │
│  └──────────────────────────────────────┘ │
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │      Retry & Fallback                │ │
│  │  - Exponential Backoff               │ │
│  │  - Fallback Strategies               │ │
│  │  - Error Recovery                    │ │
│  └──────────────────────────────────────┘ │
└────────────────────────────────────────────┘
```

---

## 核心组件实现

### 1. Request Middleware

```python
import random
from typing import Dict, List

class RequestMiddleware:
    def __init__(self):
        self.user_agents = self._load_user_agents()
        self.headers_pool = self._load_headers()

    def _load_user_agents(self) -> List[str]:
        """加载 User-Agent 池"""
        return [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
        ]

    def _load_headers(self) -> List[Dict]:
        """加载请求头池"""
        return [
            {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            },
            # 更多变体...
        ]

    def get_random_headers(self, referer=None) -> Dict:
        """获取随机请求头"""
        headers = random.choice(self.headers_pool).copy()
        headers['User-Agent'] = random.choice(self.user_agents)

        if referer:
            headers['Referer'] = referer

        return headers

    def randomize_headers(self, headers: Dict) -> Dict:
        """随机化请求头顺序"""
        items = list(headers.items())
        random.shuffle(items)
        return dict(items)
```

### 2. Proxy Manager

```python
import redis
import requests
from typing import Optional

class ProxyManager:
    def __init__(self, redis_url='redis://localhost:6379'):
        self.r = redis.from_url(redis_url, decode_responses=True)
        self.test_url = 'http://httpbin.org/ip'

    def get_proxy(self) -> Optional[str]:
        """获取可用代理"""
        # 从 Redis 有序集合获取评分最高的代理
        proxies = self.r.zrange('proxy_pool', 0, 0)
        if proxies:
            return proxies[0]
        return None

    def validate_proxy(self, proxy: str) -> bool:
        """验证代理"""
        proxies = {
            'http': f'http://{proxy}',
            'https': f'http://{proxy}'
        }
        try:
            response = requests.get(
                self.test_url,
                proxies=proxies,
                timeout=5
            )
            return response.status_code == 200
        except:
            return False

    def mark_success(self, proxy: str):
        """标记代理成功"""
        self.r.zincrby('proxy_pool', -0.1, proxy)  # 降低分数 = 提高优先级

    def mark_failure(self, proxy: str):
        """标记代理失败"""
        self.r.zincrby('proxy_pool', 1, proxy)  # 提高分数 = 降低优先级

        # 如果失败次数过多，移除代理
        score = self.r.zscore('proxy_pool', proxy)
        if score > 10:
            self.r.zrem('proxy_pool', proxy)
```

### 3. Browser Simulator

```python
from playwright.sync_api import sync_playwright
import random
import time

class BrowserSimulator:
    def __init__(self):
        self.playwright = sync_playwright().start()
        self.browser = None

    def launch_browser(self, headless=True, proxy=None):
        """启动浏览器"""
        launch_options = {
            'headless': headless,
            'args': [
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
            ]
        }

        if proxy:
            launch_options['proxy'] = {'server': proxy}

        self.browser = self.playwright.chromium.launch(**launch_options)
        return self.browser

    def create_stealth_context(self):
        """创建隐身上下文"""
        context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            locale='zh-CN',
            timezone_id='Asia/Shanghai',
        )

        # 注入反检测脚本
        context.add_init_script("""
            // 覆盖 navigator.webdriver
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });

            // 覆盖 navigator.plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });

            // 覆盖 navigator.languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['zh-CN', 'zh', 'en']
            });

            // Chrome 检测绕过
            window.chrome = {
                runtime: {}
            };
        """)

        return context

    def simulate_human_behavior(self, page):
        """模拟人类行为"""
        # 随机滚动
        page.evaluate("""
            () => {
                window.scrollTo({
                    top: Math.random() * document.body.scrollHeight,
                    behavior: 'smooth'
                });
            }
        """)
        time.sleep(random.uniform(0.5, 2))

        # 随机鼠标移动
        page.mouse.move(
            random.randint(100, 500),
            random.randint(100, 500)
        )
        time.sleep(random.uniform(0.2, 0.5))

    def scrape_with_stealth(self, url):
        """隐身爬取"""
        context = self.create_stealth_context()
        page = context.new_page()

        try:
            page.goto(url, wait_until='networkidle')
            self.simulate_human_behavior(page)
            content = page.content()
            return content
        finally:
            page.close()
            context.close()
```

### 4. CAPTCHA Solver

```python
import requests
from PIL import Image
import io

class CaptchaSolver:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'http://2captcha.com'

    def solve_image_captcha(self, image_data):
        """解决图片验证码"""
        # 上传图片
        files = {'file': ('captcha.png', image_data, 'image/png')}
        data = {'key': self.api_key, 'method': 'post'}

        response = requests.post(
            f'{self.base_url}/in.php',
            files=files,
            data=data
        )

        if response.text.startswith('OK|'):
            captcha_id = response.text.split('|')[1]
            return self._get_result(captcha_id)

        raise Exception(f'Upload failed: {response.text}')

    def solve_recaptcha(self, site_key, page_url):
        """解决 reCAPTCHA"""
        data = {
            'key': self.api_key,
            'method': 'userrecaptcha',
            'googlekey': site_key,
            'pageurl': page_url
        }

        response = requests.post(f'{self.base_url}/in.php', data=data)

        if response.text.startswith('OK|'):
            captcha_id = response.text.split('|')[1]
            return self._get_result(captcha_id)

        raise Exception(f'Captcha submission failed: {response.text}')

    def _get_result(self, captcha_id, timeout=120):
        """获取验证码结果"""
        import time

        for _ in range(timeout // 5):
            time.sleep(5)

            response = requests.get(
                f'{self.base_url}/res.php',
                params={
                    'key': self.api_key,
                    'action': 'get',
                    'id': captcha_id
                }
            )

            if response.text == 'CAPCHA_NOT_READY':
                continue

            if response.text.startswith('OK|'):
                return response.text.split('|')[1]

        raise Exception('Captcha timeout')
```

### 5. Rate Limiter

```python
import time
import random
from collections import deque

class AdaptiveRateLimiter:
    def __init__(self, base_delay=1.0, max_delay=10.0):
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.current_delay = base_delay
        self.success_count = 0
        self.failure_count = 0

    def wait(self):
        """等待适当的时间"""
        delay = self.current_delay + random.uniform(-0.5, 0.5)
        time.sleep(max(0, delay))

    def record_success(self):
        """记录成功请求"""
        self.success_count += 1

        # 连续成功，逐渐减少延迟
        if self.success_count > 10:
            self.current_delay = max(
                self.base_delay,
                self.current_delay * 0.9
            )
            self.success_count = 0

    def record_failure(self):
        """记录失败请求"""
        self.failure_count += 1

        # 失败则增加延迟
        self.current_delay = min(
            self.max_delay,
            self.current_delay * 1.5
        )

        if self.failure_count > 5:
            # 严重限流，长时间等待
            time.sleep(self.max_delay * 2)
            self.failure_count = 0

class TokenBucketRateLimiter:
    def __init__(self, rate, capacity):
        """
        rate: 每秒生成的令牌数
        capacity: 桶容量
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()

    def acquire(self):
        """获取令牌"""
        now = time.time()

        # 添加新令牌
        elapsed = now - self.last_update
        self.tokens = min(
            self.capacity,
            self.tokens + elapsed * self.rate
        )
        self.last_update = now

        # 如果有令牌，消耗一个
        if self.tokens >= 1:
            self.tokens -= 1
            return True

        # 等待令牌生成
        wait_time = (1 - self.tokens) / self.rate
        time.sleep(wait_time)
        self.tokens = 0
        self.last_update = time.time()
        return True
```

### 6. Retry & Fallback

```python
import functools
import time

def retry_with_backoff(max_retries=3, base_delay=1, max_delay=60):
    """指数退避重试装饰器"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise

                    # 指数退避
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    print(f"Retry {attempt + 1}/{max_retries} after {delay}s: {e}")
                    time.sleep(delay)

        return wrapper
    return decorator

class FallbackHandler:
    def __init__(self):
        self.strategies = []

    def add_strategy(self, strategy):
        """添加回退策略"""
        self.strategies.append(strategy)

    def execute(self, url):
        """执行回退策略"""
        for strategy in self.strategies:
            try:
                return strategy(url)
            except Exception as e:
                print(f"Strategy {strategy.__name__} failed: {e}")
                continue

        raise Exception("All strategies failed")

# 使用示例
@retry_with_backoff(max_retries=3)
def fetch_url(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.text
```

---

## 完整框架集成

```python
class AntiAntiScrapingFramework:
    def __init__(self, config):
        self.middleware = RequestMiddleware()
        self.proxy_manager = ProxyManager()
        self.browser_simulator = BrowserSimulator()
        self.captcha_solver = CaptchaSolver(config['captcha_api_key'])
        self.rate_limiter = AdaptiveRateLimiter()
        self.fallback = FallbackHandler()

    def fetch(self, url, use_browser=False):
        """智能爬取"""
        # 速率限制
        self.rate_limiter.wait()

        try:
            if use_browser:
                # 使用浏览器模拟
                result = self._fetch_with_browser(url)
            else:
                # 使用请求库
                result = self._fetch_with_requests(url)

            self.rate_limiter.record_success()
            return result

        except Exception as e:
            self.rate_limiter.record_failure()

            # 检测验证码
            if 'captcha' in str(e).lower():
                return self._handle_captcha(url)

            raise

    def _fetch_with_requests(self, url):
        """使用 requests 爬取"""
        proxy = self.proxy_manager.get_proxy()
        headers = self.middleware.get_random_headers()

        proxies = {'http': f'http://{proxy}', 'https': f'http://{proxy}'} if proxy else None

        response = requests.get(url, headers=headers, proxies=proxies, timeout=10)

        if proxy:
            self.proxy_manager.mark_success(proxy)

        return response.text

    def _fetch_with_browser(self, url):
        """使用浏览器爬取"""
        return self.browser_simulator.scrape_with_stealth(url)

    def _handle_captcha(self, url):
        """处理验证码"""
        # 使用浏览器打开页面
        context = self.browser_simulator.create_stealth_context()
        page = context.new_page()
        page.goto(url)

        # 检测验证码类型
        if page.query_selector('[data-sitekey]'):
            # reCAPTCHA
            site_key = page.get_attribute('[data-sitekey]', 'data-sitekey')
            solution = self.captcha_solver.solve_recaptcha(site_key, url)
            # 注入解决方案
            page.evaluate(f'document.getElementById("g-recaptcha-response").innerHTML="{solution}";')
            page.click('button[type="submit"]')

        return page.content()

# 使用
config = {'captcha_api_key': 'your_2captcha_key'}
framework = AntiAntiScrapingFramework(config)

result = framework.fetch('https://example.com', use_browser=True)
```

---

## 相关章节

- [反爬虫技术深度分析](../03-Advanced-Topics/anti_scraping_deep_dive.md)
- [浏览器指纹识别与对抗](../03-Advanced-Topics/browser_fingerprinting.md)
- [代理池管理](./proxy_pool_management.md)
"""
}

# 写入文件
for filename, content in docs.items():
    filepath = os.path.join(BASE_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Created: {filename}")

print(f"\n✅ Successfully created {len(docs)} Engineering documents!")
