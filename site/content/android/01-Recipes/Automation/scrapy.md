---
title: "Scrapy 快速入门备忘录"
date: 2024-09-20
type: posts
tags: ["自动化", "Android", "代理池"]
weight: 10
---

# Scrapy 快速入门备忘录

> **📚 前置知识**
>
> 本配方涉及以下核心技术，建议先阅读相关章节：
>
> - **Python 基础** - 掌握类、装饰器、生成器等概念
> - **HTTP 协议** - 理解请求响应、Headers、Cookies

Scrapy 是一个用于网络爬虫和数据抓取的、开源的、协作式的 Python 框架。它具有速度快、功能强大、可扩展性高的特点。本备忘录为 Scrapy 的核心概念和常用命令提供快速参考。

---

## Scrapy 框架概述

### 核心组件

| 组件 | 职责 | 关键接口 |
| :--- | :--- | :--- |
| **Engine (引擎)** | 控制所有组件之间的数据流，触发事件 | `ExecutionEngine` |
| **Scheduler (调度器)** | 接收 `Request` 并入队，按优先级提供给引擎 | `Scheduler` |
| **Downloader (下载器)** | 获取页面数据，将 `Response` 返回引擎 | `Downloader` |
| **Spiders (爬虫)** | 解析 `Response`，提取 `Item` 或额外 `Request` | `scrapy.Spider` |
| **Item Pipeline (管道)** | 清洗、验证和持久化 Spider 提取的 `Item` | `process_item()` |
| **Downloader Middlewares** | 引擎与下载器之间的请求/响应钩子 | `process_request()` / `process_response()` |
| **Spider Middlewares** | 引擎与 Spider 之间的输入/输出钩子 | `process_spider_input()` / `process_spider_output()` |

### 数据流

```text
┌────────┐ Request  ┌────────┐ Request ┌────────────┐ Request ┌────────────┐
│ Spider │────────►│ Engine │───────►│ Scheduler  │───────►│ Downloader │
│        │◄────────│        │◄───────│            │◄───────│            │
└────────┘Response └────────┘        └────────────┘Response└────────────┘
                       │                                    ▲     │
                       │ Items                    Downloader Middlewares
                       ▼
                 ┌──────────────┐
                 │ Item Pipeline│
                 └──────────────┘
```

1. Spider → `Request` → Engine → Scheduler 排队
2. Scheduler → `Request` → Downloader Middleware → Downloader
3. Downloader → `Response` → Engine → Spider Middleware → Spider
4. Spider → `Item` / 新 `Request` → Engine 分发到 Pipeline / Scheduler

---

## 项目搭建

```bash
pip install scrapy
scrapy startproject myproject && cd myproject
scrapy genspider example example.com
```

### 目录结构

```text
myproject/
├── scrapy.cfg               # 部署配置
└── myproject/
    ├── items.py             # Item 定义
    ├── middlewares.py       # 中间件
    ├── pipelines.py         # 数据管道
    ├── settings.py          # 项目设置
    └── spiders/
        └── example.py       # 爬虫文件
```

### 常用命令

| 命令 | 描述 |
| :--- | :--- |
| `scrapy startproject myproject` | 创建新项目 |
| `scrapy genspider example example.com` | 创建爬虫 |
| `scrapy crawl example` | 运行爬虫 |
| `scrapy crawl example -o output.json` | 运行并导出 JSON |
| `scrapy shell "http://example.com"` | 启动交互式 Shell |
| `scrapy list` | 列出所有爬虫 |
| `scrapy view http://example.com` | 在浏览器中打开下载的页面 |

### settings.py 关键配置

```python
BOT_NAME = "myproject"
ROBOTSTXT_OBEY = False
CONCURRENT_REQUESTS = 16          # 全局并发
CONCURRENT_REQUESTS_PER_DOMAIN = 8
DOWNLOAD_DELAY = 1                # 请求间隔（秒）
DOWNLOAD_TIMEOUT = 30
DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
    "User-Agent": "Mozilla/5.0 (Linux; Android 12) AppleWebKit/537.36",
}
LOG_LEVEL = "INFO"
HTTPCACHE_ENABLED = True
```

---

## Spider 编写

### 基本 Spider

```python
import scrapy

class ExampleSpider(scrapy.Spider):
    name = "example"
    allowed_domains = ["example.com"]
    start_urls = ["http://example.com/"]

    def parse(self, response):
        # CSS 选择器
        title = response.css("h1::text").get()
        links = response.css("a::attr(href)").getall()
        # XPath 选择器
        paragraphs = response.xpath("//div[@class='content']/p/text()").getall()
        yield {"title": title, "links": links}
```

### CrawlSpider 与规则

```python
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class ProductSpider(CrawlSpider):
    name = "product_crawler"
    allowed_domains = ["shop.example.com"]
    start_urls = ["https://shop.example.com/"]

    rules = (
        # 跟进分类页链接（不解析）
        Rule(LinkExtractor(allow=r"/category/\w+"), follow=True),
        # 跟进详情页并解析
        Rule(LinkExtractor(allow=r"/product/\d+"), callback="parse_product"),
    )

    def parse_product(self, response):
        yield {
            "name": response.css("h1.product-title::text").get(),
            "price": response.css("span.price::text").get(),
            "url": response.url,
        }
```

### 处理分页

```python
def parse(self, response):
    for item in response.css("div.item"):
        yield {"title": item.css("h2::text").get()}
    # 方式一：跟进下一页
    next_page = response.css("a.next-page::attr(href)").get()
    if next_page:
        yield response.follow(next_page, callback=self.parse)

# 方式二：已知页数时直接生成所有请求
def start_requests(self):
    for page in range(1, 51):
        yield scrapy.Request(f"https://example.com/list?page={page}", self.parse)
```

---

## Item 与 Pipeline

### 定义 Item

```python
# myproject/items.py
import scrapy

class ProductItem(scrapy.Item):
    name = scrapy.Field()
    price = scrapy.Field()
    description = scrapy.Field()
    url = scrapy.Field()
    crawled_at = scrapy.Field()
```

### 数据清洗 Pipeline

```python
import re

class CleanDataPipeline:
    def process_item(self, item, spider):
        if item.get("name"):
            item["name"] = item["name"].strip()
        if item.get("price"):
            item["price"] = float(re.sub(r"[^\d.]", "", item["price"]) or 0)
        return item
```

### 导出为 JSON / CSV

```bash
scrapy crawl product -o products.json   # JSON
scrapy crawl product -o products.csv    # CSV
scrapy crawl product -o products.jl     # JSON Lines（适合大文件）
```

### 保存到 MongoDB

```python
import pymongo

class MongoPipeline:
    @classmethod
    def from_crawler(cls, crawler):
        uri = crawler.settings.get("MONGO_URI", "mongodb://localhost:27017")
        db = crawler.settings.get("MONGO_DATABASE", "scrapy_db")
        return cls(uri, db)

    def __init__(self, uri, db):
        self.uri, self.db_name = uri, db

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.uri)
        self.db = self.client[self.db_name]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db["products"].insert_one(dict(item))
        return item
```

在 `settings.py` 中激活管道（数字越小优先级越高）：

```python
ITEM_PIPELINES = {
    "myproject.pipelines.CleanDataPipeline": 100,   # 先清洗
    "myproject.pipelines.MongoPipeline": 300,        # 再存储
}
```

---

## Middleware 实战

> **💡 思路一句话**: Scrapy Middleware 是在请求/响应管道中插入自定义处理逻辑的地方 — 用它来自动添加签名参数、轮换代理 IP、处理反爬验证码。

### 随机 User-Agent

```python
import random

class RandomUserAgentMiddleware:
    USER_AGENTS = [
        "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 Chrome/101.0",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 15_5 like Mac OS X) AppleWebKit/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/102.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_4) AppleWebKit/537.36 Chrome/103.0",
    ]

    def process_request(self, request, spider):
        request.headers["User-Agent"] = random.choice(self.USER_AGENTS)
```

### 代理轮换

```python
class ProxyRotationMiddleware:
    def __init__(self):
        self.proxies = [
            "http://proxy1.example.com:8080",
            "http://proxy2.example.com:8080",
            "http://proxy3.example.com:8080",
        ]

    def process_request(self, request, spider):
        request.meta["proxy"] = random.choice(self.proxies)

    def process_exception(self, request, exception, spider):
        # 移除失效代理，返回 request 触发重新调度
        failed = request.meta.get("proxy")
        if failed in self.proxies:
            self.proxies.remove(failed)
        return request
```

### 重试配置

```python
# settings.py
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]
```

### Selenium 集成

通过 `request.meta["use_selenium"] = True` 标记需要 JS 渲染的请求：

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scrapy.http import HtmlResponse

class SeleniumMiddleware:
    def __init__(self):
        opts = Options()
        opts.add_argument("--headless")
        self.driver = webdriver.Chrome(options=opts)

    def process_request(self, request, spider):
        if not request.meta.get("use_selenium"):
            return None
        self.driver.get(request.url)
        import time; time.sleep(3)
        return HtmlResponse(request.url, body=self.driver.page_source,
                            encoding="utf-8", request=request)

    def close_spider(self, spider):
        self.driver.quit()
```

注册中间件：

```python
DOWNLOADER_MIDDLEWARES = {
    "myproject.middlewares.RandomUserAgentMiddleware": 400,
    "myproject.middlewares.ProxyRotationMiddleware": 410,
    "myproject.middlewares.SeleniumMiddleware": 800,
}
```

---

## 反爬对抗

### Cookies 与 Session 管理

Scrapy 默认自动处理 Cookie（`COOKIES_ENABLED = True`）。登录场景：

```python
class LoginSpider(scrapy.Spider):
    name = "login_spider"

    def start_requests(self):
        yield scrapy.Request("https://example.com/login", self.login)

    def login(self, response):
        return scrapy.FormRequest.from_response(
            response, formdata={"username": "admin", "password": "123456"},
            callback=self.after_login)

    def after_login(self, response):
        if "欢迎" in response.text:
            yield scrapy.Request("https://example.com/dashboard", self.parse)
```

### 验证码方案对比

| 方案 | 优点 | 缺点 |
| :--- | :--- | :--- |
| 第三方打码平台 | 准确率高、接入简单 | 有成本、依赖外部 |
| OCR 本地识别 | 免费、离线 | 仅适用于简单验证码 |
| 机器学习模型 | 可定制 | 需训练数据 |
| 绕过策略 | 无额外成本 | 不一定可行 |

### Splash 渲染 JS

Splash 是轻量级 JS 渲染服务，比 Selenium 更适合大规模爬取：

```bash
docker run -d -p 8050:8050 scrapinghub/splash
pip install scrapy-splash
```

```python
# settings.py
SPLASH_URL = "http://localhost:8050"
DOWNLOADER_MIDDLEWARES = {
    "scrapy_splash.SplashCookiesMiddleware": 723,
    "scrapy_splash.SplashMiddleware": 725,
}
DUPEFILTER_CLASS = "scrapy_splash.SplashAwareDupeFilter"
```

```python
from scrapy_splash import SplashRequest

class SplashSpider(scrapy.Spider):
    name = "splash_spider"
    def start_requests(self):
        yield SplashRequest("https://spa.example.com/", self.parse,
                            args={"wait": 3, "images": 0})
    def parse(self, response):
        for item in response.css("div.dynamic-content"):
            yield {"text": item.css("::text").get()}
```

---

## Scrapy + 逆向工程

在移动端逆向场景中，我们通过 Frida、抓包等手段破解了 App 的 API 签名算法后，可以将签名逻辑集成到 Scrapy 中间件，实现大规模自动化采集。

### 自定义签名中间件

假设某 App 的 API 需要 `X-Sign` 头部，签名算法为 `MD5(path + timestamp + secret_key)`：

```python
import hashlib
import time
from urllib.parse import urlparse

class ApiSignMiddleware:
    SECRET_KEY = "a1b2c3d4e5f6"  # 通过逆向 App 获得

    def process_request(self, request, spider):
        if not request.meta.get("need_sign"):
            return None
        timestamp = str(int(time.time()))
        path = urlparse(request.url).path
        sign = hashlib.md5(f"{path}{timestamp}{self.SECRET_KEY}".encode()).hexdigest()
        request.headers["X-Sign"] = sign
        request.headers["X-Timestamp"] = timestamp
```

### 在 Spider 中调用逆向 API

```python
class AppApiSpider(scrapy.Spider):
    name = "app_api"
    custom_settings = {"DOWNLOADER_MIDDLEWARES": {"myproject.middlewares.ApiSignMiddleware": 543}}

    def start_requests(self):
        for uid in range(1, 1001):
            yield scrapy.Request(f"https://api.example.com/v2/user/{uid}/profile",
                                meta={"need_sign": True}, callback=self.parse_profile)

    def parse_profile(self, response):
        d = response.json()
        yield {"user_id": d.get("uid"), "nickname": d.get("nickname")}
```

---

## 性能调优

### 并发与延迟

| 配置项 | 默认值 | 说明 |
| :--- | :--- | :--- |
| `CONCURRENT_REQUESTS` | 16 | 全局最大并发 |
| `CONCURRENT_REQUESTS_PER_DOMAIN` | 8 | 同域名最大并发 |
| `CONCURRENT_REQUESTS_PER_IP` | 0 | 同 IP 最大并发 |
| `DOWNLOAD_DELAY` | 0 | 请求间隔（秒） |
| `RANDOMIZE_DOWNLOAD_DELAY` | True | 0.5x~1.5x 随机化延迟 |
| `DOWNLOAD_TIMEOUT` | 180 | 下载超时（秒） |

### AutoThrottle 自动限速

根据服务器响应时间自动调整爬取速度：

```python
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 2        # 初始延迟
AUTOTHROTTLE_MAX_DELAY = 30         # 最大延迟
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0
AUTOTHROTTLE_DEBUG = True           # 查看限速日志
```

### 其他优化

```python
DNSCACHE_ENABLED = True           # DNS 缓存
DNSCACHE_SIZE = 10000
TELNETCONSOLE_ENABLED = False     # 关闭不必要功能
COOKIES_ENABLED = False           # 不需要时关闭
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
```

---

## 部署方案

### Scrapyd 部署

```bash
pip install scrapyd scrapyd-client
scrapyd                      # 启动服务 http://localhost:6800
scrapyd-deploy default -p myproject   # 部署项目
```

| API 端点 | 方法 | 说明 |
| :--- | :--- | :--- |
| `/schedule.json` | POST | 调度运行爬虫 |
| `/cancel.json` | POST | 取消运行中的爬虫 |
| `/listprojects.json` | GET | 列出所有项目 |
| `/listjobs.json` | GET | 列出所有任务状态 |

```bash
# 调度爬虫
curl http://localhost:6800/schedule.json -d project=myproject -d spider=example
# 查看状态
curl http://localhost:6800/listjobs.json?project=myproject
```

### Docker 部署

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["scrapy", "crawl", "example", "-o", "/data/output.json"]
```

配合 `docker-compose.yml` 可同时启动 MongoDB、Splash、Scrapyd 等服务。

### 定时爬取

```bash
crontab -e
# 每天凌晨 2 点
0 2 * * * cd /path/to/myproject && scrapy crawl example -o /data/$(date +\%Y\%m\%d).json >> /var/log/scrapy.log 2>&1
# 每 6 小时
0 */6 * * * cd /path/to/myproject && scrapy crawl example
```

> **提示：** 生产环境推荐 Scrapyd + Docker + crontab 组合。更复杂的调度需求可使用 Airflow 或 Celery Beat。
