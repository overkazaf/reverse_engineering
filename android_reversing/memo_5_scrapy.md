# 🕷️ Scrapy 爬虫框架速记

## 🏗️ Scrapy 架构组件

### 📊 核心组件

| 组件 | 作用 | 重要性 |
|:---|:---|:---|
| **Engine (引擎)** | 控制数据流，协调各组件 | ⭐⭐⭐⭐⭐ |
| **Scheduler (调度器)** | 管理请求队列，去重调度 | ⭐⭐⭐⭐⭐ |
| **Spider (爬虫)** | 定义爬取逻辑和数据提取 | ⭐⭐⭐⭐⭐ |
| **Downloader (下载器)** | 发送HTTP请求，获取响应 | ⭐⭐⭐⭐ |
| **Item Pipeline** | 处理提取的数据项 | ⭐⭐⭐⭐ |
| **Middlewares** | 处理请求和响应的中间件 | ⭐⭐⭐ |

### 🔄 数据流向
```
Spider → Engine → Scheduler → Engine → Downloader → 
Downloader Middleware → Internet → Downloader Middleware →
Engine → Spider Middleware → Spider → Engine → Item Pipeline
```

---

## 🚀 基础使用

### 📋 项目创建
```bash
# 创建项目
scrapy startproject myproject

# 创建爬虫
cd myproject
scrapy genspider example example.com

# 运行爬虫
scrapy crawl example
```

### 🕷️ Spider 基础模板
```python
import scrapy

class ExampleSpider(scrapy.Spider):
    name = 'example'
    allowed_domains = ['example.com']
    start_urls = ['http://example.com']
    
    def parse(self, response):
        # 提取数据
        title = response.css('title::text').get()
        
        # 生成数据项
        yield {
            'title': title,
            'url': response.url,
        }
        
        # 跟进链接
        for link in response.css('a::attr(href)').getall():
            yield response.follow(link, self.parse)
```

---

## 🔧 选择器与数据提取

### 📋 选择器类型对比

| 选择器 | 语法 | 优点 | 缺点 |
|:---|:---|:---|:---|
| **CSS** | `response.css('div.class')` | 简洁直观 | 功能有限 |
| **XPath** | `response.xpath('//div[@class="class"]')` | 功能强大 | 语法复杂 |

### 🎯 常用选择器
```python
# CSS 选择器
response.css('title::text').get()           # 获取单个值
response.css('a::attr(href)').getall()      # 获取所有值
response.css('div.content p::text').getall() # 嵌套选择

# XPath 选择器
response.xpath('//title/text()').get()      # 基础路径
response.xpath('//a[@class="link"]/@href').getall()  # 属性选择
response.xpath('//text()[contains(., "关键词")]').getall()  # 文本包含

# 组合使用
for item in response.css('div.item'):
    yield {
        'title': item.css('h2::text').get(),
        'price': item.xpath('.//span[@class="price"]/text()').get(),
        'link': item.css('a::attr(href)').get(),
    }
```

---

## 📦 Item 和 Item Loader

### 🏗️ Item 定义
```python
import scrapy

class ProductItem(scrapy.Item):
    name = scrapy.Field()
    price = scrapy.Field()
    description = scrapy.Field()
    image_urls = scrapy.Field()
    images = scrapy.Field()
    
    # 添加序列化方法
    def __repr__(self):
        return f"ProductItem(name={self['name']!r})"
```

### 🔧 ItemLoader 使用
```python
from itemloaders import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose

class ProductLoader(ItemLoader):
    default_item_class = ProductItem
    default_output_processor = TakeFirst()
    
    # 字段处理器
    name_in = MapCompose(str.strip, str.title)
    price_in = MapCompose(lambda x: x.replace('$', ''), float)
    description_in = MapCompose(str.strip)

# 在Spider中使用
def parse_product(self, response):
    loader = ProductLoader(response=response)
    loader.add_css('name', 'h1::text')
    loader.add_css('price', '.price::text') 
    loader.add_css('description', '.description::text')
    return loader.load_item()
```

---

## 🔄 Pipeline 数据处理

### 📊 Pipeline 类型

| Pipeline类型 | 用途 | 示例 |
|:---|:---|:---|
| **验证Pipeline** | 数据验证和清洗 | 价格格式检查 |
| **去重Pipeline** | 去除重复数据 | URL去重 |
| **存储Pipeline** | 数据持久化 | 数据库存储 |
| **图片Pipeline** | 下载图片文件 | 商品图片下载 |

### 🔧 自定义Pipeline
```python
class ValidationPipeline:
    def process_item(self, item, spider):
        if not item.get('price'):
            raise DropItem(f"Missing price in {item}")
        return item

class DatabasePipeline:
    def open_spider(self, spider):
        # 连接数据库
        self.connection = sqlite3.connect('data.db')
        self.cursor = self.connection.cursor()
        
    def close_spider(self, spider):
        self.connection.close()
        
    def process_item(self, item, spider):
        # 插入数据
        self.cursor.execute("""
            INSERT INTO products (name, price, description) 
            VALUES (?, ?, ?)
        """, (item['name'], item['price'], item['description']))
        self.connection.commit()
        return item

class DuplicatesPipeline:
    def __init__(self):
        self.ids_seen = set()
        
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter['id'] in self.ids_seen:
            raise DropItem(f"Duplicate item found: {item!r}")
        else:
            self.ids_seen.add(adapter['id'])
            return item
```

---

## 🛠️ 中间件 (Middlewares)

### 🌐 Downloader 中间件
```python
class UserAgentMiddleware:
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
        ]
    
    def process_request(self, request, spider):
        ua = random.choice(self.user_agents)
        request.headers['User-Agent'] = ua
        return None

class ProxyMiddleware:
    def process_request(self, request, spider):
        proxy = self.get_proxy()  # 获取代理
        request.meta['proxy'] = proxy
        return None
        
    def process_response(self, request, response, spider):
        if response.status in [403, 429]:  # 被封IP
            new_proxy = self.get_new_proxy()
            request.meta['proxy'] = new_proxy
            return request  # 重新请求
        return response
```

### 🕷️ Spider 中间件
```python
class SpiderMiddleware:
    def process_spider_input(self, response, spider):
        # 处理Spider输入
        return None
        
    def process_spider_output(self, response, result, spider):
        # 处理Spider输出
        for item in result:
            yield item
            
    def process_spider_exception(self, response, exception, spider):
        # 处理Spider异常
        spider.logger.error(f"Spider exception: {exception}")
```

---

## ⚙️ 配置与优化

### 📋 常用配置
```python
# settings.py
# 机器人协议
ROBOTSTXT_OBEY = False

# 并发设置
CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 8
DOWNLOAD_DELAY = 1
RANDOMIZE_DOWNLOAD_DELAY = 0.5

# 重试设置
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

# 超时设置
DOWNLOAD_TIMEOUT = 180

# User-Agent
USER_AGENT = 'myproject (+http://www.yourdomain.com)'

# Pipeline激活
ITEM_PIPELINES = {
    'myproject.pipelines.ValidationPipeline': 300,
    'myproject.pipelines.DuplicatesPipeline': 400,
    'myproject.pipelines.DatabasePipeline': 500,
}

# 中间件激活
DOWNLOADER_MIDDLEWARES = {
    'myproject.middlewares.UserAgentMiddleware': 400,
    'myproject.middlewares.ProxyMiddleware': 500,
}
```

### 🚀 性能优化
```python
# 关闭不必要的中间件
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.robotstxt.RobotsTxtMiddleware': None,
}

# 启用HTTP缓存
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 3600

# 启用AutoThrottle
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 60
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0

# 内存使用优化
MEMUSAGE_ENABLED = True
MEMUSAGE_LIMIT_MB = 512
```

---

## 🔐 反爬虫对抗

### 🛡️ 常见反爬虫技术

| 反爬虫技术 | 检测方式 | 应对策略 |
|:---|:---|:---|
| **User-Agent检测** | 请求头检查 | 随机User-Agent池 |
| **IP频率限制** | 单IP请求频率 | 代理池轮换 |
| **验证码** | 图片/滑块验证 | OCR识别/人工处理 |
| **JavaScript渲染** | 动态内容加载 | Selenium/Splash |
| **请求签名** | 参数加密校验 | 逆向分析算法 |

### 🔧 对抗策略实现
```python
# 1. 随机延迟
import random
import time

class RandomDelayMiddleware:
    def process_request(self, request, spider):
        delay = random.uniform(1, 3)
        time.sleep(delay)

# 2. 请求头伪装
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# 3. Selenium集成
from scrapy_selenium import SeleniumRequest

def parse(self, response):
    yield SeleniumRequest(
        url=response.url,
        callback=self.parse_result,
        wait_time=3,
        screenshot=True
    )

# 4. 代理池管理
class ProxyPool:
    def __init__(self):
        self.proxies = [
            'http://proxy1:port',
            'http://proxy2:port',
            'socks5://proxy3:port',
        ]
        self.current = 0
    
    def get_proxy(self):
        proxy = self.proxies[self.current]
        self.current = (self.current + 1) % len(self.proxies)
        return proxy
```

---

## 📊 监控与调试

### 🔍 日志配置
```python
# 日志级别设置
LOG_LEVEL = 'INFO'
LOG_FILE = 'scrapy.log'

# 自定义日志格式
LOG_FORMAT = '%(levelname)s: %(message)s'

# 在Spider中使用日志
class MySpider(scrapy.Spider):
    def parse(self, response):
        self.logger.info(f'Parse function called on {response.url}')
        self.logger.warning(f'Low response time: {response.meta.get("download_latency")}')
```

### 📈 统计信息
```python
# 启用统计
STATS_CLASS = 'scrapy.statscollectors.MemoryStatsCollector'

# 在Spider中访问统计
def closed(self, reason):
    stats = self.crawler.stats
    self.logger.info(f'Spider closed: {reason}')
    self.logger.info(f'Total requests: {stats.get_value("downloader/request_count")}')
    self.logger.info(f'Total items: {stats.get_value("item_scraped_count")}')
```

### 🛠️ 调试技巧
```python
# 1. Scrapy Shell调试
# scrapy shell "http://example.com"
# >>> response.css('title::text').get()

# 2. 设置断点
def parse(self, response):
    import pdb; pdb.set_trace()  # 调试断点
    
# 3. 保存响应内容
def parse(self, response):
    with open('debug.html', 'w') as f:
        f.write(response.text)
        
# 4. 检查请求和响应
def parse(self, response):
    self.logger.debug(f'Request headers: {response.request.headers}')
    self.logger.debug(f'Response headers: {response.headers}')
```

---

## 🎯 常见面试题及答案

### Q1: Scrapy的架构组件及其作用？
**A**: 
- **Engine**: 控制组件间数据流
- **Scheduler**: 管理请求队列和去重
- **Spider**: 定义爬取逻辑和数据提取规则
- **Downloader**: 发送HTTP请求获取响应
- **Pipeline**: 处理和存储提取的数据
- **Middlewares**: 处理请求和响应的中间件

### Q2: Scrapy相比其他爬虫框架的优势？
**A**: 
- **异步处理**: 基于Twisted的异步网络框架，高并发
- **可扩展性**: 丰富的中间件和Pipeline系统
- **内置功能**: 去重、重试、缓存等开箱即用
- **调试友好**: 内置Shell和详细日志
- **社区生态**: 丰富的第三方插件和扩展

### Q3: 如何处理JavaScript渲染的页面？
**A**: 
1. **Scrapy-Selenium**: 集成Selenium WebDriver
2. **Scrapy-Splash**: 使用Splash渲染引擎
3. **Scrapy-Playwright**: 使用Playwright无头浏览器
4. **API逆向**: 分析AJAX请求直接调用API

### Q4: Scrapy如何实现去重？
**A**: 
- **内置去重**: `DUPEFILTER_CLASS`使用请求指纹去重
- **自定义去重**: 继承`BaseDupeFilter`实现自定义逻辑
- **Pipeline去重**: 在Item Pipeline中实现业务去重
- **外部去重**: 使用Redis等外部存储实现分布式去重

### Q5: 如何优化Scrapy的性能？
**A**: 
1. **并发设置**: 调整`CONCURRENT_REQUESTS`参数
2. **下载延迟**: 合理设置`DOWNLOAD_DELAY`
3. **AutoThrottle**: 启用自动调速功能
4. **内存优化**: 限制内存使用，处理大文件
5. **缓存机制**: 启用HTTP缓存减少重复请求

### Q6: 如何处理反爬虫机制？
**A**: 
- **请求头伪装**: 模拟真实浏览器请求头
- **代理轮换**: 使用代理池避免IP封禁
- **延迟控制**: 随机延迟模拟人类行为
- **Session管理**: 维护登录状态和Cookie
- **验证码处理**: OCR识别或人工介入

### Q7: Scrapy中Item和ItemLoader的区别？
**A**: 
- **Item**: 定义数据结构，类似于Python字典
- **ItemLoader**: 提供数据加载和处理机制
- **处理器**: ItemLoader支持输入输出处理器
- **复用性**: ItemLoader可复用数据处理逻辑
- **验证**: ItemLoader提供数据验证功能

### Q8: 如何实现分布式爬虫？
**A**: 
1. **Scrapy-Redis**: 使用Redis作为调度器和去重器
2. **配置共享**: 多个Spider共享请求队列
3. **数据存储**: 统一的数据存储后端
4. **监控管理**: 使用Scrapyd部署和管理
5. **负载均衡**: 合理分配爬取任务

### Q9: Pipeline的执行顺序如何控制？
**A**: 
- **优先级数字**: `ITEM_PIPELINES`中的数字越小优先级越高
- **返回值**: Pipeline必须返回Item或抛出DropItem异常
- **处理链**: Item按优先级顺序通过所有Pipeline
- **异常处理**: 某个Pipeline异常不影响其他Pipeline

### Q10: 如何调试Scrapy爬虫？
**A**: 
1. **Scrapy Shell**: 交互式测试选择器和请求
2. **日志系统**: 设置合适的日志级别和格式
3. **统计信息**: 监控请求数量、错误率等指标
4. **断点调试**: 使用pdb在代码中设置断点
5. **响应保存**: 保存HTML内容进行离线分析