# 分布式爬虫实战：Scrapy-Redis 详解

> **📚 前置知识**
>
> 本配方涉及以下核心技术，建议先阅读相关章节：
>
> - **[Scrapy 快速入门](./scrapy.md)** - 理解 Scrapy 调度器与去重机制
> - **Redis 基础** - 掌握 Redis 列表、集合操作

Scrapy 默认是单机架构，请求队列保存在内存中，重启即失，且无法多机共享。**Scrapy-Redis** 是一个强大的组件，它重写了 Scrapy 的调度器 (Scheduler) 和去重组件 (DupeFilter)，将请求队列和指纹集合存储在 Redis 中，从而实现：

1. **分布式爬取**: 多个爬虫节点共享同一个 Redis 队列，协同工作。
2. **断点续爬**: 请求持久化在 Redis 中，爬虫挂掉重启后可继续运行。

---

## 1. 核心架构原理

### 原生 Scrapy vs Scrapy-Redis

**原生 Scrapy**:

- **Scheduler**: 维护在内存中的 Python `deque` 或 `queue`。
- **DupeFilter**: 维护在内存中的 Python `set`。
- **缺点**: 无法跨进程/跨机器共享，内存受限。

**Scrapy-Redis**:

- **Scheduler**: 从 Redis 的 `List` (或 `PriorityQueue`) 中 `POP` 请求，向其 `PUSH` 新请求。
- **DupeFilter**: 利用 Redis 的 `Set` 数据结构存储 URL 指纹 (SHA1)，利用 Redis 的原子性进行去重。
- **Item Pipeline**: 可选将提取的数据直接推入 Redis，由独立的 Worker 消费存储。

---

## 2. 环境搭建与配置

### 安装

```bash
pip install scrapy-redis
```

### 配置 settings.py

```python
# settings.py

# 1. 启用 Scrapy-Redis 调度器
SCHEDULER = "scrapy_redis.scheduler.Scheduler"

# 2. 启用 Scrapy-Redis 去重过滤器
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"

# 3. 允许暂停 (断点续爬核心)
# 如果为真，当爬虫停止时，Redis 中的请求队列不会被清空
SCHEDULER_PERSIST = True

# 4. 设置 Redis 连接
# 方式一：单独设置
REDIS_HOST = '192.168.1.100'
REDIS_PORT = 6379
# REDIS_PARAMS = {'password': 'yourpassword'}

# 方式二：完整地址
# REDIS_URL = 'redis://user:pass@hostname:9001'

# 5. 配置请求队列模式（可选，默认为 PriorityQueue）
# SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.PriorityQueue'  # 有序集合，支持优先级
# SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.FifoQueue'      # 先进先出列表
# SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.LifoQueue'      # 后进先出列表（栈）

# 6. (可选) 将数据存入 Redis Pipeline
ITEM_PIPELINES = {
    'scrapy_redis.pipelines.RedisPipeline': 300,
}
```

---

## 3. 编写分布式 Spider

### 继承 RedisSpider

```python
from scrapy_redis.spiders import RedisSpider
import scrapy

class MyDistributedSpider(RedisSpider):
    name = 'myspider_distributed'

    # 核心差异：不再定义 start_urls
    # 定义 redis_key，爬虫启动后会阻塞等待该键中出现的 URL
    redis_key = 'myspider:start_urls'

    def parse(self, response):
        self.logger.info(f"Crawling {response.url}")

        # 提取数据逻辑与普通 Spider 一致
        yield {
            'url': response.url,
            'title': response.css('title::text').get()
        }

        # 生成新请求
        for href in response.css('a::attr(href)').getall():
            yield response.follow(href, self.parse)
```

### 启动流程

1. 启动爬虫（多个终端启动多个实例）：
    ```bash
    scrapy crawl myspider_distributed
    ```
2. 向 Redis 推送起始 URL：
    ```bash
    redis-cli lpush myspider:start_urls http://example.com
    ```

### 使用 RedisCrawlSpider

如果你需要利用 `Rule` 和 `LinkExtractor` 自动抓取全站，可以使用 `RedisCrawlSpider`。

```python
from scrapy_redis.spiders import RedisCrawlSpider
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule

class MyCrawlSpider(RedisCrawlSpider):
    name = 'mycrawl_distributed'
    redis_key = 'mycrawl:start_urls'

    rules = (
        Rule(LinkExtractor(allow=r'/article/'), callback='parse_article'),
        Rule(LinkExtractor(allow=r'/page/'), follow=True),
    )

    def parse_article(self, response):
        yield {
            'title': response.css('h1::text').get(),
            'content': response.css('.content::text').getall(),
        }
```

---

## 4. 进阶优化策略

### Bloom Filter 去重优化

Scrapy-Redis 默认使用 Redis `Set` 存储所有指纹。对于亿级 URL 的爬取，这会消耗数十 GB 内存。解决方案是集成 **Bloom Filter**。

**实现思路**:

1. 重写 `RFPDupeFilter`。
2. 使用 `redis-py` 的 `bf.add` 和 `bf.exists` 命令 (需要 RedisBloom 模块) 或 Python 端的 `pybloom_live` 映射到 Redis BitMap。

```python
# custom_dupefilter.py 简易示意
from scrapy_redis.dupefilter import RFPDupeFilter

class BloomFilterDupeFilter(RFPDupeFilter):
    def request_seen(self, request):
        fp = self.request_fingerprint(request)
        # 假设 self.server 是 Redis 连接，且支持 BF 命令
        # 如果指纹已存在，返回 True
        if self.server.execute_command('BF.EXISTS', self.key, fp):
            return True
        # 否则添加指纹
        self.server.execute_command('BF.ADD', self.key, fp)
        return False
```

### 请求优先级

```python
# 生成请求时指定优先级
yield scrapy.Request(url, priority=100)  # 首页，优先
yield scrapy.Request(url, priority=10)   # 详情页，次之
```

### 空闲超时关闭

```python
# settings.py
# 指定空闲等待时间（秒），超时则关闭爬虫
SCHEDULER_IDLE_BEFORE_CLOSE = 10
```

---

## 5. 部署架构图

```mermaid
graph TB
    subgraph "Master / Redis Server"
        Redis[(Redis Queue & Set)]
    end

    subgraph "Slave 1"
        Spider1[Scrapy Spider 1] -->|Pop Request| Redis
        Spider1 -->|Push Request| Redis
        Spider1 -->|Dupe Check| Redis
    end

    subgraph "Slave 2"
        Spider2[Scrapy Spider 2] -->|Pop Request| Redis
        Spider2 -->|Push Request| Redis
        Spider2 -->|Dupe Check| Redis
    end

    subgraph "Data Storage"
        Mongo[(MongoDB)]
    end

    Spider1 -->|Store Item| Mongo
    Spider2 -->|Store Item| Mongo
```

---

## 6. 常见问题

### Q: 爬虫启动后一直等待，不抓取？

**A**: 确认已向 `redis_key` 推送了起始 URL：

```bash
redis-cli lpush myspider:start_urls http://example.com
```

### Q: 如何监控爬取进度？

**A**: 使用 Redis 命令查看队列长度：

```bash
# 查看待爬取请求数量
redis-cli llen myspider:requests

# 查看已爬取指纹数量
redis-cli scard myspider:dupefilter
```

### Q: 如何清空队列重新开始？

**A**: 删除 Redis 中的相关键：

```bash
redis-cli del myspider:requests myspider:dupefilter myspider:start_urls
```

---

## 总结

Scrapy-Redis 是构建分布式爬虫系统的核心组件。通过将调度器和去重组件迁移到 Redis，实现了多节点协同爬取和断点续爬能力，是大规模数据采集的必备工具。
