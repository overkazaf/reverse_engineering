---
title: "Scrapy 快速入门备忘录"
date: 2024-09-20
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

## 目录

- [Scrapy 快速入门备忘录](#scrapy-快速入门备忘录)
  - [目录](#目录)
    - [核心组件](#核心组件)
    - [项目命令](#项目命令)
    - [Spider (爬虫)](#spider-爬虫)
      - [基本结构](#基本结构)
      - [处理分页和链接](#处理分页和链接)

---

### 核心组件

Scrapy 的数据流由以下核心组件协同完成：

1. **Engine (引擎)**: 负责控制所有组件之间的数据流，并在相应动作发生时触发事件。
2. **Scheduler (调度器)**: 接收来自引擎的请求 (`Request`)，并将其入队，以便后续引擎请求时提供。
3. **Downloader (下载器)**: 负责获取页面数据，并将其提供给引擎，而后由引擎将结果 (`Response`) 交给 Spider。
4. **Spiders (爬虫)**: 用户编写的用于解析 `Response` 并提取 `Item` 或额外 `Request` 的类。
5. **Item Pipeline (项目管道)**: 负责处理由 Spider 提取出来的 `Item`。典型的操作包括数据清洗、验证和持久化（如存入数据库）。
6. **Downloader Middlewares (下载器中间件)**: 位于引擎和下载器之间的钩子，用于在请求发送和响应返回时进行自定义处理（如设置 User-Agent、处理代理）。
7. **Spider Middlewares (爬虫中间件)**: 位于引擎和 Spider 之间的钩子，用于处理 Spider 的输入 (`Response`) 和输出 (`Item`, `Request`)。

![Scrapy Architecture](https://docs.scrapy.org/en/latest/_images/scrapy_architecture.png)

---

### 项目命令

| 命令                                   | 描述                                                                       |
| :------------------------------------- | :------------------------------------------------------------------------- |
| `pip install scrapy`                   | 安装 Scrapy 框架                                                           |
| `scrapy startproject myproject`        | 创建一个名为 `myproject` 的新项目                                          |
| `cd myproject`                         | 进入项目目录                                                               |
| `scrapy genspider example example.com` | 在 `spiders` 目录下创建一个名为 `example` 的爬虫，限定域名为 `example.com` |
| `scrapy crawl example`                 | 运行名为 `example` 的爬虫                                                  |
| `scrapy crawl example -o output.json`  | 运行爬虫并将提取的数据保存为 JSON 文件                                     |
| `scrapy shell "http://example.com"`    | 启动一个交互式 Shell，用于测试 XPath/CSS 选择器                            |
| `scrapy list`                          | 列出项目中的所有可用爬虫                                                   |

---

### Spider (爬虫)

Spider 是你定义如何爬取某个网站（或一组网站）的类，包括爬取动作和如何从页面内容中提取结构化数据。

#### 基本结构

```python
# myproject/spiders/example_spider.py
import scrapy

class ExampleSpider(scrapy.Spider):
# 爬虫的唯一标识名称
name = 'example'
# 允许爬取的域名列表（可选）
allowed_domains = ['example.com']
# 爬虫启动时请求的 URL 列表
start_urls = ['http://example.com/']

# 处理 start_urls 响应的默认回调方法
def parse(self, response):
# 在这里编写解析逻辑
pass

```

- `response.css('a::attr(href)').getall()`: 提取所有 `<a>` 标签的 `href` 属性。

- `response.css('div.product > p::text').get()`: 提取 `class="product"` 的 `div` 下的 `p` 标签文本。

- **XPath 表达式**:
- `response.xpath('//h1/text()').get()`: 提取第一个 `<h1>` 标签的文本。

- `response.xpath('//a/@href').getall()`: 提取所有 `<a>` 标签的 `href` 属性。

- `response.xpath('//div[@class="product"]/p/text()').get()`: 同上。

#### 处理分页和链接

在 `parse` 方法中，你可以 `yield` 新的 `Request` 对象来跟进链接。

```python
def parse(self, response):
# ... 提取当前页面数据 ...

# 提取下一页链接并生成新请求
next_page = response.css('a.next_page::attr(href)').get()
if next_page is not None:
# response.urljoin() 用于处理相对 URL
yield response.follow(next_page, callback=self.parse)

```

```python
# myproject/items.py
import scrapy

class ProductItem(scrapy.Item):
name = scrapy.Field()
price = scrapy.Field()
description = scrapy.Field()

```

item = ProductItem()
item['name'] = response.css('h1.product-name::text').get()
item['price'] = response.css('span.price::text').get()
yield item

````

```python
# myproject/pipelines.py
import sqlite3

class SQLitePipeline:
def open_spider(self, spider):
# 爬虫开启时调用
self.connection = sqlite3.connect('products.db')
self.cursor = self.connection.cursor()
self.cursor.execute('CREATE TABLE IF NOT EXISTS products (name TEXT, price TEXT)')

def close_spider(self, spider):
# 爬虫关闭时调用
self.connection.close()

def process_item(self, item, spider):
# 每个 item 都会调用
self.cursor.execute('INSERT INTO products (name, price) VALUES (?, ?)', (item['name'], item['price']))
self.connection.commit()
return item # 必须返回 item

````

'myproject.pipelines.SQLitePipeline': 300,
}

```

* `DEFAULT_REQUEST_HEADERS`: 设置默认的请求头，如 `User-Agent`。

* `DOWNLOAD_DELAY = 1`: 设置下载延迟（秒），以避免对服务器造成太大压力。

* `CONCURRENT_REQUESTS = 16`: 并发请求数。

* `ITEM_PIPELINES`: 激活和设置 Item Pipeline 的优先级。

* `DOWNLOADER_MIDDLEWARES`: 激活和设置下载器中间件的优先级。
```
