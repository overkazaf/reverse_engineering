---
title: "反爬虫对抗框架"
date: 2025-05-07
tags: ["Web", "浏览器指纹", "代理池", "工程实践", "分布式", "Playwright"]
weight: 10
---

# 反爬虫对抗框架

## 概述

反爬虫对抗框架是一个综合性的系统，集成了多种对抗技术，用于突破各类反爬虫防护。本章介绍如何设计一个通用的反爬虫对抗框架。

---

## 框架架构

```
┌────────────────────────────────────────────┐
│ Scraper Application │
└──────────────┬─────────────────────────────┘
│
┌──────────────┴─────────────────────────────┐
│ Anti-Anti-Scraping Framework │
│ │
│ ┌──────────────────────────────────────┐ │
│ │ Request Middleware │ │
│ │ - User-Agent Rotation │ │
│ │ - Header Randomization │ │
│ │ - Cookie Management │ │
│ └──────────────────────────────────────┘ │
│ │
│ ┌──────────────────────────────────────┐ │
│ │ Proxy Manager │ │
│ │ - Proxy Pool │ │
│ │ - IP Rotation │ │
│ │ - Proxy Health Check │ │
│ └──────────────────────────────────────┘ │
│ │
│ ┌──────────────────────────────────────┐ │
│ │ Browser Simulator │ │
│ │ - Puppeteer/Playwright │ │
│ │ - Fingerprint Evasion │ │
│ │ - Human Behavior Simulation │ │
│ └──────────────────────────────────────┘ │
│ │
│ ┌──────────────────────────────────────┐ │
│ │ CAPTCHA Solver │ │
│ │ - 2Captcha Integration │ │
│ │ - OCR Recognition │ │
│ │ - AI Model Prediction │ │
│ └──────────────────────────────────────┘ │
│ │
│ ┌──────────────────────────────────────┐ │
│ │ Rate Limiter │ │
│ │ - Adaptive Delay │ │
│ │ - Token Bucket │ │
│ │ - Request Scheduling │ │
│ └──────────────────────────────────────┘ │
│ │
│ ┌──────────────────────────────────────┐ │
│ │ Retry & Fallback │ │
│ │ - Exponential Backoff │ │
│ │ - Fallback Strategies │ │
│ │ - Error Recovery │ │
│ └──────────────────────────────────────┘ │
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
self.r.zincrby('proxy_pool', -0.1, proxy) # 降低分数 = 提高优先级

def mark_failure(self, proxy: str):
"""标记代理失败"""
self.r.zincrby('proxy_pool', 1, proxy) # 提高分数 = 降低优先级

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

### 4. Rate Limiter

```python
import time
import random

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
```

---

## 完整框架集成

```python
class AntiAntiScrapingFramework:
def __init__(self, config):
self.middleware = RequestMiddleware()
self.proxy_manager = ProxyManager()
self.browser_simulator = BrowserSimulator()
self.rate_limiter = AdaptiveRateLimiter()

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

# 使用
config = {}
framework = AntiAntiScrapingFramework(config)
result = framework.fetch('https://example.com', use_browser=True)
```

---

## 相关章节

- [反爬虫技术深度分析](../04-Advanced-Recipes/anti_scraping_deep_dive.md)
- [浏览器指纹识别与对抗](../03-Advanced-Topics/browser_fingerprinting.md)
- [代理池管理](./proxy_pool_management.md)
