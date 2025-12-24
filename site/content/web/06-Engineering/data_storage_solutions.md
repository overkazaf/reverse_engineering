---
title: "数据存储方案"
date: 2025-12-25
weight: 10
---

# 数据存储方案

## 概述

爬虫系统需要高效的数据存储方案来处理海量数据。本章介绍常见的存储选型和最佳实践。

---

## 存储选型

### 关系型数据库 vs NoSQL

| 特性 | 关系型数据库 | NoSQL |
| ------------ | -------------------- | -------------------- |
| **数据模型** | 表格、严格 schema | 文档、键值、列族 |
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
"""添加到集合"""
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
"""添加到有序集合"""
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
│ Application Layer │
└─────────────┬───────────────────────┘
│
┌─────────┴──────────┐
│ │
▼ ▼
┌─────────┐ ┌──────────┐
│ Redis │ │ MySQL │
│ (Cache) │ │ (Master) │
└─────────┘ └────┬─────┘
│
┌─────────┴─────────┐
│ │
▼ ▼
┌──────────┐ ┌──────────┐
│ MongoDB │ │ ES │
│(文档存储) │ │(全文搜索) │
└──────────┘ └──────────┘
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
