---
title: "分布式爬虫架构模板"
date: 2025-12-25
weight: 10
---

# 分布式爬虫架构模板

基于 Scrapy + Redis 的分布式爬虫架构，支持多机协同、任务调度和数据去重。

---

## 项目结构

```
distributed_crawler/
├── scrapy_project/
│ ├── scrapy.cfg
│ ├── spiders/
│ │ ├── __init__.py
│ │ ├── base_spider.py
│ │ └── target_spider.py
│ ├── items.py
│ ├── pipelines.py
│ ├── middlewares.py
│ ├── settings.py
│ └── utils/
│ ├── __init__.py
│ ├── redis_client.py
│ └── bloomfilter.py
├── scheduler/
│ ├── __init__.py
│ ├── task_manager.py
│ └── url_scheduler.py
├── config/
│ ├── __init__.py
│ ├── settings.py
│ └── redis_config.py
├── docker/
│ ├── Dockerfile.spider
│ ├── Dockerfile.scheduler
│ └── docker-compose.yml
├── scripts/
│ ├── start_spider.sh
│ ├── add_tasks.py
│ └── monitor.py
├── tests/
│ └── test_spider.py
├── requirements.txt
└── README.md
```

---

## 核心文件

### 1. scrapy_project/settings.py

```python
"""
Scrapy 分布式配置
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Scrapy 基础配置
BOT_NAME = 'distributed_crawler'
SPIDER_MODULES = ['scrapy_project.spiders']
NEWSPIDER_MODULE = 'scrapy_project.spiders'

# 遵守 robots.txt
ROBOTSTXT_OBEY = False

# 并发配置
CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 8
CONCURRENT_REQUESTS_PER_IP = 8

# 下载延迟
DOWNLOAD_DELAY = 1
RANDOMIZE_DOWNLOAD_DELAY = True

# 超时设置
DOWNLOAD_TIMEOUT = 30
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

# User-Agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

# 请求头
DEFAULT_REQUEST_HEADERS = {
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
'Accept-Encoding': 'gzip, deflate',
}

# ==================== Redis 配置 ====================

# 使用 scrapy-redis
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
SCHEDULER_PERSIST = True # 保持调度队列

# Redis 连接
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')
REDIS_DB = int(os.getenv('REDIS_DB', 0))

# Redis 连接配置
REDIS_PARAMS = {
'password': REDIS_PASSWORD,
'db': REDIS_DB,
'decode_responses': False, # 关键：不自动解码
}

# 调度队列 key 前缀
SCHEDULER_QUEUE_KEY = '%(spider)s:requests'
SCHEDULER_DUPEFILTER_KEY = '%(spider)s:dupefilter'

# ==================== 中间件 ====================

DOWNLOADER_MIDDLEWARES = {
# 重试中间件
'scrapy.downloadermiddlewares.retry.RetryMiddleware': 90,

# Redis 统计中间件
'scrapy_redis.downloadermiddleware.RedisStatsMiddleware': 100,

# 随机 User-Agent
'scrapy_project.middlewares.RandomUserAgentMiddleware': 400,

# 代理中间件
'scrapy_project.middlewares.ProxyMiddleware': 410,

# 异常捕获
'scrapy_project.middlewares.ExceptionMiddleware': 500,
}

SPIDER_MIDDLEWARES = {
'scrapy_redis.spidermiddleware.RedisSrpiderMiddleware': 100,
}

# ==================== Pipeline ====================

ITEM_PIPELINES = {
# 数据清洗
'scrapy_project.pipelines.CleanPipeline': 100,

# 去重检查
'scrapy_project.pipelines.DuplicatesPipeline': 200,

# MongoDB 存储
'scrapy_project.pipelines.MongoPipeline': 300,

# Redis 缓存
'scrapy_project.pipelines.RedisPipeline': 400,
}

# ==================== MongoDB 配置 ====================

MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
MONGODB_DATABASE = os.getenv('MONGODB_DB', 'scraper_db')
MONGODB_COLLECTION = '%(spider)s_items'

# ==================== 日志配置 ====================

LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'
LOG_DATEFORMAT = '%Y-%m-%d %H:%M:%S'

# ==================== 其他配置 ====================

# 自动限速
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0

# Cookies
COOKIES_ENABLED = True
COOKIES_DEBUG = False

# Telnet 控制台
TELNETCONSOLE_ENABLED = True
TELNETCONSOLE_PORT = [6023, 6024, 6025]
```

### 2. scrapy_project/items.py

```python
"""
数据模型定义
"""
import scrapy
from scrapy.loader.processors import TakeFirst, MapCompose, Join
from w3lib.html import remove_tags


def clean_text(text):
"""清理文本"""
return text.strip() if text else ''


class BaseItem(scrapy.Item):
"""基础 Item"""
# 通用字段
url = scrapy.Field(output_processor=TakeFirst())
spider_name = scrapy.Field(output_processor=TakeFirst())
crawl_time = scrapy.Field(output_processor=TakeFirst())


class ProductItem(BaseItem):
"""商品 Item"""
title = scrapy.Field(
input_processor=MapCompose(remove_tags, clean_text),
output_processor=TakeFirst()
)
price = scrapy.Field(output_processor=TakeFirst())
stock = scrapy.Field(output_processor=TakeFirst())
description = scrapy.Field(
input_processor=MapCompose(remove_tags, clean_text),
output_processor=Join('\n')
)
images = scrapy.Field()
tags = scrapy.Field()
rating = scrapy.Field(output_processor=TakeFirst())
reviews_count = scrapy.Field(output_processor=TakeFirst())


class ArticleItem(BaseItem):
"""文章 Item"""
title = scrapy.Field(
input_processor=MapCompose(remove_tags, clean_text),
output_processor=TakeFirst()
)
author = scrapy.Field(output_processor=TakeFirst())
publish_time = scrapy.Field(output_processor=TakeFirst())
content = scrapy.Field(
input_processor=MapCompose(remove_tags, clean_text),
output_processor=Join('\n')
)
category = scrapy.Field()
tags = scrapy.Field()
view_count = scrapy.Field(output_processor=TakeFirst())
```

### 3. scrapy_project/pipelines.py

```python
"""
数据处理 Pipeline
"""
import hashlib
import pymongo
import redis
from datetime import datetime
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem


class CleanPipeline:
"""数据清洗 Pipeline"""

def process_item(self, item, spider):
adapter = ItemAdapter(item)

# 添加爬取时间
adapter['crawl_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
adapter['spider_name'] = spider.name

# 清理空值
for field in adapter.field_names():
value = adapter.get(field)
if value is None or value == '':
adapter[field] = None

return item


class DuplicatesPipeline:
"""去重 Pipeline (基于 Redis)"""

def __init__(self, redis_host, redis_port, redis_password, redis_db):
self.redis_host = redis_host
self.redis_port = redis_port
self.redis_password = redis_password
self.redis_db = redis_db
self.redis_client = None

@classmethod
def from_crawler(cls, crawler):
return cls(
redis_host=crawler.settings.get('REDIS_HOST'),
redis_port=crawler.settings.get('REDIS_PORT'),
redis_password=crawler.settings.get('REDIS_PASSWORD'),
redis_db=crawler.settings.get('REDIS_DB'),
)

def open_spider(self, spider):
self.redis_client = redis.Redis(
host=self.redis_host,
port=self.redis_port,
password=self.redis_password,
db=self.redis_db,
decode_responses=True
)

def close_spider(self, spider):
if self.redis_client:
self.redis_client.close()

def process_item(self, item, spider):
adapter = ItemAdapter(item)

# 生成唯一标识
url = adapter.get('url', '')
item_hash = hashlib.md5(url.encode()).hexdigest()

# 检查是否已存在
key = f"{spider.name}:items:{item_hash}"
if self.redis_client.exists(key):
raise DropItem(f"Duplicate item found: {url}")

# 标记已处理
self.redis_client.setex(key, 86400 * 7, '1') # 保留7天

return item


class MongoPipeline:
"""MongoDB 存储 Pipeline"""

def __init__(self, mongo_uri, mongo_db):
self.mongo_uri = mongo_uri
self.mongo_db = mongo_db
self.client = None
self.db = None

@classmethod
def from_crawler(cls, crawler):
return cls(
mongo_uri=crawler.settings.get('MONGODB_URI'),
mongo_db=crawler.settings.get('MONGODB_DATABASE')
)

def open_spider(self, spider):
self.client = pymongo.MongoClient(self.mongo_uri)
self.db = self.client[self.mongo_db]

def close_spider(self, spider):
if self.client:
self.client.close()

def process_item(self, item, spider):
collection_name = f"{spider.name}_items"
collection = self.db[collection_name]

# 插入数据
item_dict = ItemAdapter(item).asdict()
collection.insert_one(item_dict)

spider.logger.info(f"Item saved to MongoDB: {item_dict.get('url')}")
return item


class RedisPipeline:
"""Redis 缓存 Pipeline"""

def __init__(self, redis_host, redis_port, redis_password, redis_db):
self.redis_host = redis_host
self.redis_port = redis_port
self.redis_password = redis_password
self.redis_db = redis_db
self.redis_client = None

@classmethod
def from_crawler(cls, crawler):
return cls(
redis_host=crawler.settings.get('REDIS_HOST'),
redis_port=crawler.settings.get('REDIS_PORT'),
redis_password=crawler.settings.get('REDIS_PASSWORD'),
redis_db=crawler.settings.get('REDIS_DB') + 1, # 使用不同的 DB
)

def open_spider(self, spider):
self.redis_client = redis.Redis(
host=self.redis_host,
port=self.redis_port,
password=self.redis_password,
db=self.redis_db,
decode_responses=True
)

def close_spider(self, spider):
if self.redis_client:
self.redis_client.close()

def process_item(self, item, spider):
import json

adapter = ItemAdapter(item)
url = adapter.get('url', '')
item_hash = hashlib.md5(url.encode()).hexdigest()

# 缓存到 Redis
key = f"{spider.name}:cache:{item_hash}"
value = json.dumps(adapter.asdict(), ensure_ascii=False)
self.redis_client.setex(key, 3600, value) # 缓存1小时

return item
```

### 4. scrapy_project/middlewares.py

```python
"""
中间件
"""
import random
from scrapy import signals
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from scrapy.exceptions import IgnoreRequest


class RandomUserAgentMiddleware(UserAgentMiddleware):
"""随机 User-Agent 中间件"""

USER_AGENTS = [
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]

def process_request(self, request, spider):
user_agent = random.choice(self.USER_AGENTS)
request.headers['User-Agent'] = user_agent


class ProxyMiddleware:
"""代理中间件"""

def __init__(self, proxy_list):
self.proxy_list = proxy_list

@classmethod
def from_crawler(cls, crawler):
# 从配置或 Redis 获取代理列表
proxy_list = crawler.settings.get('PROXY_LIST', [])
return cls(proxy_list)

def process_request(self, request, spider):
if self.proxy_list:
proxy = random.choice(self.proxy_list)
request.meta['proxy'] = proxy
spider.logger.debug(f"Using proxy: {proxy}")

def process_exception(self, request, exception, spider):
# 代理失败时，移除该代理
proxy = request.meta.get('proxy')
if proxy and proxy in self.proxy_list:
self.proxy_list.remove(proxy)
spider.logger.warning(f"Removed failed proxy: {proxy}")


class ExceptionMiddleware:
"""异常处理中间件"""

def process_response(self, request, response, spider):
# 检查响应状态码
if response.status in [403, 429]:
spider.logger.warning(f"Rate limited or blocked: {response.url}")
# 可以在这里实现延迟重试逻辑

return response

def process_exception(self, request, exception, spider):
spider.logger.error(f"Request failed: {request.url} - {exception}")
```

### 5. scrapy_project/spiders/base_spider.py

```python
"""
基础爬虫类
"""
from scrapy_redis.spiders import RedisSpider
from scrapy.loader import ItemLoader


class BaseRedisSpider(RedisSpider):
"""基础 Redis 爬虫"""

# Redis key (需要在子类中覆盖)
redis_key = None

# 批处理大小
redis_batch_size = 10

# 最大空闲时间 (秒)
max_idle_time = 60

def make_request_from_data(self, data):
"""
从 Redis 获取的数据创建请求

Args:
data: 从 Redis 获取的 URL 或数据

Returns:
Request 对象
"""
url = data.decode('utf-8') if isinstance(data, bytes) else data
return self.make_requests_from_url(url)

def parse(self, response):
"""需要在子类中实现"""
raise NotImplementedError

def get_item_loader(self, item_class, response):
"""创建 ItemLoader"""
loader = ItemLoader(item=item_class(), response=response)
loader.add_value('url', response.url)
return loader
```

### 6. scrapy_project/spiders/target_spider.py

```python
"""
目标网站爬虫
"""
from scrapy import Request
from .base_spider import BaseRedisSpider
from scrapy_project.items import ProductItem


class TargetSpider(BaseRedisSpider):
"""目标网站爬虫"""

name = 'target_spider'
redis_key = 'target_spider:start_urls'

custom_settings = {
'CONCURRENT_REQUESTS': 8,
'DOWNLOAD_DELAY': 2,
}

def parse(self, response):
"""
解析列表页
"""
# 提取产品链接
for href in response.css('.product-item a::attr(href)').getall():
url = response.urljoin(href)
yield Request(url, callback=self.parse_detail)

# 翻页
next_page = response.css('.pagination .next::attr(href)').get()
if next_page:
yield Request(response.urljoin(next_page), callback=self.parse)

def parse_detail(self, response):
"""
解析详情页
"""
loader = self.get_item_loader(ProductItem, response)

# 提取字段
loader.add_css('title', 'h1.product-title::text')
loader.add_css('price', '.price::text')
loader.add_css('stock', '.stock::text')
loader.add_css('description', '.description *::text')
loader.add_css('images', '.product-images img::attr(src)')
loader.add_css('tags', '.tags a::text')
loader.add_css('rating', '.rating::attr(data-rating)')
loader.add_css('reviews_count', '.reviews-count::text')

yield loader.load_item()
```

### 7. scheduler/task_manager.py

```python
"""
任务管理器
"""
import redis
import logging


class TaskManager:
"""分布式任务管理器"""

def __init__(self, redis_host='localhost', redis_port=6379, redis_password='', redis_db=0):
self.redis_client = redis.Redis(
host=redis_host,
port=redis_port,
password=redis_password,
db=redis_db,
decode_responses=True
)
self.logger = logging.getLogger(__name__)

def add_start_urls(self, spider_name, urls):
"""
添加起始 URL 到 Redis

Args:
spider_name: 爬虫名称
urls: URL 列表
"""
key = f"{spider_name}:start_urls"

if isinstance(urls, str):
urls = [urls]

added = self.redis_client.lpush(key, *urls)
self.logger.info(f"Added {added} URLs to {key}")
return added

def get_queue_size(self, spider_name):
"""获取队列大小"""
key = f"{spider_name}:start_urls"
return self.redis_client.llen(key)

def clear_queue(self, spider_name):
"""清空队列"""
key = f"{spider_name}:start_urls"
deleted = self.redis_client.delete(key)
self.logger.info(f"Cleared queue: {key}")
return deleted

def get_stats(self, spider_name):
"""获取统计信息"""
stats = {
'queue_size': self.get_queue_size(spider_name),
'items_count': self.redis_client.scard(f"{spider_name}:dupefilter"),
}
return stats


if __name__ == '__main__':
# 使用示例
logging.basicConfig(level=logging.INFO)

manager = TaskManager(
redis_host='localhost',
redis_port=6379,
redis_password=os.environ.get('REDIS_PASSWORD', '')
)

# 添加起始 URL
urls = [
'https://example.com/page/1',
'https://example.com/page/2',
'https://example.com/page/3',
]

manager.add_start_urls('target_spider', urls)

# 查看统计
stats = manager.get_stats('target_spider')
print(f"Stats: {stats}")
```

### 8. scripts/add_tasks.py

```python
"""
批量添加任务脚本
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from scheduler.task_manager import TaskManager
import logging

logging.basicConfig(
level=logging.INFO,
format='%(asctime)s [%(levelname)s] %(message)s'
)


def generate_urls(base_url, start_page, end_page):
"""生成 URL 列表"""
return [f"{base_url}?page={i}" for i in range(start_page, end_page + 1)]


def main():
manager = TaskManager(
redis_host='localhost',
redis_port=6379,
redis_password=os.environ.get('REDIS_PASSWORD', '')
)

# 生成 URL
urls = generate_urls(
base_url='https://example.com/products',
start_page=1,
end_page=100
)

# 添加到队列
manager.add_start_urls('target_spider', urls)

# 查看统计
stats = manager.get_stats('target_spider')
print(f"\n✅ Tasks added successfully!")
print(f" Queue size: {stats['queue_size']}")


if __name__ == '__main__':
main()
```

### 9. scripts/monitor.py

```python
"""
爬虫监控脚本
"""
import sys
import os
import time
import redis

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class CrawlerMonitor:
"""爬虫监控"""

def __init__(self, redis_host='localhost', redis_port=6379, redis_password='', redis_db=0):
self.redis_client = redis.Redis(
host=redis_host,
port=redis_port,
password=redis_password,
db=redis_db,
decode_responses=True
)

def get_spider_stats(self, spider_name):
"""获取爬虫统计信息"""
stats = {}

# 队列大小
queue_key = f"{spider_name}:requests"
stats['queue_size'] = self.redis_client.llen(queue_key)

# 去重集合大小
dupefilter_key = f"{spider_name}:dupefilter"
stats['processed_urls'] = self.redis_client.scard(dupefilter_key)

# 缓存数量
cache_pattern = f"{spider_name}:cache:*"
stats['cached_items'] = len(self.redis_client.keys(cache_pattern))

return stats

def monitor(self, spider_name, interval=5):
"""
持续监控

Args:
spider_name: 爬虫名称
interval: 刷新间隔（秒）
"""
print(f" Monitoring {spider_name}... (Press Ctrl+C to stop)\n")

try:
while True:
stats = self.get_spider_stats(spider_name)

print(f"\r Queue: {stats['queue_size']:>6} | "
f"Processed: {stats['processed_urls']:>8} | "
f"Cached: {stats['cached_items']:>6}",
end='', flush=True)

time.sleep(interval)

except KeyboardInterrupt:
print("\n\n✅ Monitoring stopped")


if __name__ == '__main__':
monitor = CrawlerMonitor(
redis_host='localhost',
redis_port=6379,
redis_password=os.environ.get('REDIS_PASSWORD', '')
)

monitor.monitor('target_spider', interval=2)
```

### 10. docker/docker-compose.yml

```yaml
version: "3.8"

services:
# Redis
redis:
image: redis:7-alpine
container_name: crawler_redis
command: redis-server --requirepass ${REDIS_PASSWORD} --maxmemory 512mb
ports:
- "6379:6379"
volumes:
- redis_data:/data
networks:
- crawler_network

# MongoDB
mongodb:
image: mongo:7.0
container_name: crawler_mongodb
environment:
MONGO_INITDB_ROOT_USERNAME: admin
MONGO_INITDB_ROOT_PASSWORD: admin123
ports:
- "27017:27017"
volumes:
- mongodb_data:/data/db
networks:
- crawler_network

# Scrapy Master (调度器)
master:
build:
context: ..
dockerfile: docker/Dockerfile.scheduler
container_name: crawler_master
environment:
REDIS_HOST: redis
REDIS_PORT: 6379
REDIS_PASSWORD: ${REDIS_PASSWORD}
MONGODB_URI: mongodb://admin:${MONGO_PASSWORD}@mongodb:27017/
depends_on:
- redis
- mongodb
networks:
- crawler_network
command: python scheduler/task_manager.py

# Scrapy Worker (爬虫节点)
spider:
build:
context: ..
dockerfile: docker/Dockerfile.spider
environment:
REDIS_HOST: redis
REDIS_PORT: 6379
REDIS_PASSWORD: ${REDIS_PASSWORD}
MONGODB_URI: mongodb://admin:${MONGO_PASSWORD}@mongodb:27017/
depends_on:
- redis
- mongodb
networks:
- crawler_network
deploy:
replicas: 3
command: scrapy crawl target_spider

networks:
crawler_network:
driver: bridge

volumes:
redis_data:
mongodb_data:
```

### 11. requirements.txt

```txt
Scrapy>=2.11.0
scrapy-redis>=0.7.3
redis>=5.0.0
pymongo>=4.6.0
python-dotenv>=1.0.0
w3lib>=2.1.0
itemadapter>=0.8.0
```

---

## 使用指南

### 单机测试

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动 Redis 和 MongoDB
docker-compose up -d redis mongodb

# 3. 添加任务
python scripts/add_tasks.py

# 4. 启动爬虫
scrapy crawl target_spider

# 5. 监控进度
python scripts/monitor.py
```

### 分布式部署

```bash
# 1. 构建并启动所有服务
docker-compose up -d

# 2. 扩容爬虫节点
docker-compose up -d --scale spider=5

# 3. 查看日志
docker-compose logs -f spider

# 4. 查看统计
docker exec crawler_master python scripts/monitor.py
```

---

## 相关资源

- [基础爬虫项目](./basic_scraper.md)
- [Docker 部署](./docker_setup.md)
- [分布式爬虫](../06-Engineering/distributed_scraping.md)
- [Scrapy 文档](https://docs.scrapy.org/)
- [scrapy-redis 文档](https://github.com/rmax/scrapy-redis)
