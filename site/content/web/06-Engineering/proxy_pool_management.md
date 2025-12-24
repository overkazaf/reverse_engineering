---
title: "代理池管理"
weight: 10
---

# 代理池管理

## 概述

代理池是分布式爬虫的核心组件之一，用于突破 IP 限制和反爬虫检测。本章介绍代理池的构建、管理和优化策略。

---

## 代理类型

### 1. HTTP/HTTPS 代理

最常见的代理类型。

```python
proxies = {
'http': 'http://proxy_ip:port',
'https': 'https://proxy_ip:port'
}

response = requests.get(url, proxies=proxies)
```

### 2. SOCKS 代理

支持更多协议，性能更好。

```python
# 需要安装 requests[socks]
proxies = {
'http': 'socks5://proxy_ip:port',
'https': 'socks5://proxy_ip:port'
}
```

### 3. 代理分类

**按匿名性**:

- **透明代理**: 目标服务器能看到真实 IP
- **匿名代理**: 隐藏真实 IP，但暴露代理特征
- **高匿代理**: 完全隐藏，无代理特征

**按来源**:

- **免费代理**: 不稳定，速度慢
- **付费代理**: 稳定，速度快
- **住宅代理**: 真实家庭 IP，质量最高

---

## 代理池架构

```
┌──────────────────────────────────┐
│ Proxy Fetcher │
│ - 从多个源获取代理 │
│ - 免费代理网站 │
│ - 付费代理 API │
└──────────┬───────────────────────┘
│
▼
┌──────────────────────────────────┐
│ Proxy Validator │
│ - 验证代理有效性 │
│ - 测试响应时间 │
│ - 检查匿名性 │
└──────────┬───────────────────────┘
│
▼
┌──────────────────────────────────┐
│ Redis Storage │
│ - 可用代理池 │
│ - 代理评分 │
│ - 使用统计 │
└──────────┬───────────────────────┘
│
▼
┌──────────────────────────────────┐
│ Proxy Scheduler │
│ - 智能分配代理 │
│ - 失败重试 │
│ - 动态调整 │
└──────────────────────────────────┘
```

---

## 完整实现

### 代理池类

```python
import requests
import redis
import time
from typing import List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProxyPool:
def __init__(self):
self.r = redis.Redis(host='localhost', port=6379, decode_responses=True)
self.test_url = 'http://httpbin.org/ip'
self.timeout = 5

def fetch_proxies(self) -> List[str]:
"""从多个源获取代理"""
proxies = []
proxies.extend(self._fetch_from_free_proxy())
proxies.extend(self._fetch_from_paid_api())
return list(set(proxies))

def _fetch_from_free_proxy(self) -> List[str]:
"""从免费代理网站获取"""
proxies = []
try:
response = requests.get('https://www.kuaidaili.com/free/', timeout=10)
# 解析页面，提取代理
except Exception as e:
logger.error(f'Fetch free proxy failed: {e}')
return proxies

def _fetch_from_paid_api(self) -> List[str]:
"""从付费 API 获取"""
proxies = []
try:
response = requests.get('http://api.proxy.com/get?num=100', timeout=10)
data = response.json()
proxies = [f"{item['ip']}:{item['port']}" for item in data]
except Exception as e:
logger.error(f'Fetch paid proxy failed: {e}')
return proxies

def validate_proxy(self, proxy: str) -> bool:
"""验证代理可用性"""
proxies = {
'http': f'http://{proxy}',
'https': f'http://{proxy}'
}

try:
start_time = time.time()
response = requests.get(
self.test_url,
proxies=proxies,
timeout=self.timeout
)
response_time = time.time() - start_time

if response.status_code == 200:
self.r.zadd('proxy_pool', {proxy: response_time})
logger.info(f'Valid proxy: {proxy} ({response_time:.2f}s)')
return True
except:
pass
return False

def batch_validate(self, proxies: List[str]):
"""批量验证代理"""
from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=50) as executor:
executor.map(self.validate_proxy, proxies)

def get_proxy(self) -> str:
"""获取最快的代理"""
result = self.r.zrange('proxy_pool', 0, 0)
if result:
return result[0]
return None

def get_random_proxy(self) -> str:
"""随机获取代理"""
import random
proxies = self.r.zrange('proxy_pool', 0, -1)
if proxies:
return random.choice(proxies)
return None

def remove_proxy(self, proxy: str):
"""移除失效代理"""
self.r.zrem('proxy_pool', proxy)
logger.info(f'Removed proxy: {proxy}')

def get_pool_size(self) -> int:
"""获取代理池大小"""
return self.r.zcard('proxy_pool')

def run(self):
"""运行代理池"""
logger.info('Starting proxy pool...')
while True:
logger.info('Fetching proxies...')
proxies = self.fetch_proxies()
logger.info(f'Fetched {len(proxies)} proxies')

logger.info('Validating proxies...')
self.batch_validate(proxies)

self.cleanup_old_proxies()

pool_size = self.get_pool_size()
logger.info(f'Current pool size: {pool_size}')

time.sleep(300)

def cleanup_old_proxies(self):
"""清理响应时间过长的代理"""
self.r.zremrangebyscore('proxy_pool', 10, float('inf'))
```

---

## 使用代理池

### 基本使用

```python
def crawl_with_proxy(url):
"""使用代理爬取"""
pool = ProxyPool()
max_retries = 3

for i in range(max_retries):
proxy = pool.get_proxy()
if not proxy:
logger.error('No available proxy!')
break

proxies = {
'http': f'http://{proxy}',
'https': f'http://{proxy}'
}

try:
response = requests.get(url, proxies=proxies, timeout=10)
return response
except Exception as e:
logger.warning(f'Proxy {proxy} failed: {e}')
pool.remove_proxy(proxy)

return None
```

### 与 Scrapy 集成

```python
# middlewares.py
class ProxyMiddleware:
def __init__(self):
self.pool = ProxyPool()

def process_request(self, request, spider):
"""为请求设置代理"""
proxy = self.pool.get_proxy()
if proxy:
request.meta['proxy'] = f'http://{proxy}'
spider.logger.info(f'Using proxy: {proxy}')

def process_exception(self, request, exception, spider):
"""处理代理失败"""
proxy = request.meta.get('proxy', '').replace('http://', '')
if proxy:
self.pool.remove_proxy(proxy)
spider.logger.warning(f'Removed failed proxy: {proxy}')
```

---

## 付费代理服务

### 推荐服务商

| 服务商 | 类型 | 价格 | 特点 |
| -------------------------- | --------------- | -------- | ------------------- |
| **Luminati (Bright Data)** | 住宅代理 | $500+/月 | 质量最高，IP 池最大 |
| **Smartproxy** | 住宅代理 | $75+/月 | 性价比高 |
| **Oxylabs** | 数据中心 + 住宅 | $300+/月 | 稳定可靠 |
| **ProxyMesh** | 数据中心 | $10+/月 | 便宜入门 |
| **站大爷** | 数据中心 | ¥100+/月 | 国内服务 |

### API 集成示例

```python
class LuminatiProxy:
def __init__(self, username, password, port=22225):
self.username = username
self.password = password
self.host = 'zproxy.lum-superproxy.io'
self.port = port

def get_proxy(self, country='us', session_id=None):
"""获取代理"""
if session_id:
username = f'{self.username}-country-{country}-session-{session_id}'
else:
username = f'{self.username}-country-{country}'

proxy = f'http://{username}:{self.password}@{self.host}:{self.port}'
return {'http': proxy, 'https': proxy}

# 使用
proxy_provider = LuminatiProxy('your_username', 'your_password')
proxies = proxy_provider.get_proxy(country='us', session_id='12345')
response = requests.get(url, proxies=proxies)
```

---

## 监控与统计

### 代理质量评分

```python
class ProxyScorer:
def __init__(self):
self.r = redis.Redis(decode_responses=True)

def record_success(self, proxy):
"""记录成功"""
self.r.hincrby(f'proxy:{proxy}', 'success', 1)
self.update_score(proxy)

def record_failure(self, proxy):
"""记录失败"""
self.r.hincrby(f'proxy:{proxy}', 'failure', 1)
self.update_score(proxy)

def update_score(self, proxy):
"""更新评分"""
success = int(self.r.hget(f'proxy:{proxy}', 'success') or 0)
failure = int(self.r.hget(f'proxy:{proxy}', 'failure') or 0)

total = success + failure
if total > 0:
score = success / total
self.r.hset(f'proxy:{proxy}', 'score', score)

def get_best_proxies(self, count=10):
"""获取评分最高的代理"""
all_proxies = self.r.keys('proxy:*')
scored_proxies = []

for key in all_proxies:
proxy = key.replace('proxy:', '')
score = float(self.r.hget(key, 'score') or 0)
scored_proxies.append((proxy, score))

scored_proxies.sort(key=lambda x: x[1], reverse=True)
return scored_proxies[:count]
```

---

## 最佳实践

1. **定期验证**: 每 5-10 分钟验证一次代理池
2. **快速失败**: 设置合理的超时时间（3-5 秒）
3. **评分系统**: 根据成功率动态调整代理权重
4. **混合使用**: 免费代理 + 付费代理组合
5. **地域分配**: 根据目标网站选择对应地区代理

---

## 相关章节

- [分布式爬虫架构](./distributed_scraping.md)
- [反爬虫技术深度分析](../04-Advanced-Recipes/anti_scraping_deep_dive.md)
- [监控与告警系统](./monitoring_and_alerting.md)
