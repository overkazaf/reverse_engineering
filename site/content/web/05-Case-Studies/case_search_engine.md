---
title: "搜索引擎对抗"
date: 2025-12-25
weight: 10
---

# 搜索引擎对抗

## 概述

搜索引擎拥有业界最强的反爬虫防护机制。本文通过 5 个真实案例，讲解搜索引擎的防护技术及其对抗策略。

---

## 案例 1: CAPTCHA 与频率限制绕过

### 背景

搜索引擎（Google、Bing、百度）使用 CAPTCHA（验证码）和 IP 频率限制来防止自动化爬取。

### 防护机制

#### 1. CAPTCHA 类型

**Google reCAPTCHA v3**:

```javascript
<script src="https://www.google.com/recaptcha/api.js?render=site_key"></script>
<script>
grecaptcha.ready(function() {
grecaptcha.execute('site_key', {action: 'search'}).then(function(token) {
// 将 token 发送到服务器验证
document.getElementById('recaptcha_token').value = token;
});
});
</script>
```

**hCaptcha**:

```html
<div class="h-captcha" data-sitekey="your_site_key"></div>
<script src="https://js.hcaptcha.com/1/api.js" async defer></script>
```

#### 2. 频率检测

基于以下指标:

- **IP 地址**: 单 IP 每分钟请求次数
- **User-Agent**: 识别爬虫特征
- **Cookie**: 追踪用户会话
- **行为模式**: 请求间隔、搜索模式

### 逆向步骤

#### 1. 分析 CAPTCHA 触发条件

```python
import requests
import time

def test_rate_limit():
"""测试搜索引擎的频率限制阈值"""
session = requests.Session()
headers = {
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

captcha_triggered = False
request_count = 0

while not captcha_triggered:
response = session.get(
'https://www.google.com/search',
params={'q': f'test query {request_count}'},
headers=headers
)

request_count += 1

# 检测是否触发 CAPTCHA
if 'captcha' in response.text.lower() or response.status_code == 429:
print(f"CAPTCHA triggered after {request_count} requests")
captcha_triggered = True
else:
print(f"Request {request_count}: OK")
time.sleep(1) # 每秒 1 次请求

test_rate_limit()
```

**结果**:

- Google: 约 20-30 次/分钟（IP）
- Bing: 约 50-60 次/分钟
- 百度: 约 100 次/分钟

#### 2. reCAPTCHA v3 绕过

reCAPTCHA v3 不显示验证码，而是评分（0.0-1.0）:

```python
from playwright.sync_api import sync_playwright
import time

class RecaptchaV3Bypass:
def __init__(self):
self.playwright = None
self.browser = None

def solve_recaptcha(self, url, site_key, action='search'):
"""
通过模拟真实用户行为来提高 reCAPTCHA 评分
"""
with sync_playwright() as p:
# 使用真实浏览器配置
browser = p.chromium.launch(
headless=False, # 非无头模式评分更高
args=[
'--disable-blink-features=AutomationControlled',
'--disable-dev-shm-usage'
]
)

context = browser.new_context(
viewport={'width': 1920, 'height': 1080},
user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
)

# 加载真实 Cookie（从浏览器导出）
context.add_cookies([
{
'name': 'NID',
'value': 'your_google_cookie',
'domain': '.google.com',
'path': '/'
}
])

page = context.new_page()

# 模拟真实用户行为
page.goto(url)

# 随机鼠标移动
for _ in range(10):
x = random.randint(100, 800)
y = random.randint(100, 600)
page.mouse.move(x, y)
time.sleep(random.uniform(0.1, 0.3))

# 触发 reCAPTCHA
token = page.evaluate(f"""
new Promise((resolve) => {{
grecaptcha.ready(() => {{
grecaptcha.execute('{site_key}', {{action: '{action}'}})
.then(token => resolve(token));
}});
}})
""")

browser.close()
return token

def search_with_recaptcha(self, query):
"""带 reCAPTCHA 的搜索"""
token = self.solve_recaptcha(
'https://www.google.com',
site_key='6LfxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxE'
)

# 使用 token 进行搜索
response = requests.get(
'https://www.google.com/search',
params={
'q': query,
'recaptcha_token': token
}
)

return response.text
```

#### 3. 使用第三方 CAPTCHA 求解服务

```python
import requests
from twocaptcha import TwoCaptcha

class CaptchaSolver:
def __init__(self, api_key):
self.solver = TwoCaptcha(api_key)

def solve_recaptcha_v2(self, site_key, page_url):
"""求解 reCAPTCHA v2"""
try:
result = self.solver.recaptcha(
sitekey=site_key,
url=page_url
)

return result['code']

except Exception as e:
print(f"Error: {e}")
return None

def solve_hcaptcha(self, site_key, page_url):
"""求解 hCaptcha"""
try:
result = self.solver.hcaptcha(
sitekey=site_key,
url=page_url
)

return result['code']

except Exception as e:
print(f"Error: {e}")
return None

# 使用示例
solver = CaptchaSolver(api_key='your_2captcha_api_key')
token = solver.solve_recaptcha_v2(
site_key='6LfxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxE',
page_url='https://www.google.com/search?q=test'
)

# 提交带 token 的请求
response = requests.post(
'https://www.google.com/search',
data={
'q': 'test',
'g-recaptcha-response': token
}
)
```

### 频率限制绕过

#### 1. IP 轮换

```python
import requests
from itertools import cycle

class ProxyRotator:
def __init__(self, proxy_list):
"""
proxy_list: ['http://1.2.3.4:8080', 'http://5.6.7.8:8080', ...]
"""
self.proxy_pool = cycle(proxy_list)
self.session = requests.Session()

def get_with_rotation(self, url, params=None):
"""使用代理轮换发送请求"""
max_retries = 5

for _ in range(max_retries):
proxy = next(self.proxy_pool)

try:
response = self.session.get(
url,
params=params,
proxies={'http': proxy, 'https': proxy},
timeout=10
)

if response.status_code == 200:
return response

except Exception as e:
print(f"Proxy {proxy} failed: {e}")
continue

raise Exception("All proxies failed")

# 使用代理池进行搜索
proxy_list = [
'http://proxy1.example.com:8080',
'http://proxy2.example.com:8080',
'http://proxy3.example.com:8080',
]

rotator = ProxyRotator(proxy_list)

for i in range(100):
response = rotator.get_with_rotation(
'https://www.google.com/search',
params={'q': f'query {i}'}
)
print(f"Search {i}: {response.status_code}")
```

#### 2. 请求间隔随机化

```python
import random
import time

class RateLimitEvader:
def __init__(self, min_delay=2.0, max_delay=5.0):
self.min_delay = min_delay
self.max_delay = max_delay
self.last_request_time = 0

def wait(self):
"""智能等待，避免被检测"""
current_time = time.time()
elapsed = current_time - self.last_request_time

# 使用正态分布生成延迟（更接近人类行为）
delay = random.gauss(
(self.min_delay + self.max_delay) / 2,
(self.max_delay - self.min_delay) / 4
)
delay = max(self.min_delay, min(self.max_delay, delay))

if elapsed < delay:
time.sleep(delay - elapsed)

self.last_request_time = time.time()

def search(self, query):
"""带智能延迟的搜索"""
self.wait()

response = requests.get(
'https://www.google.com/search',
params={'q': query}
)

return response.text

# 使用示例
evader = RateLimitEvader(min_delay=3.0, max_delay=7.0)

for i in range(100):
result = evader.search(f'query {i}')
print(f"Search {i} completed")
```

---

## 案例 2: 搜索结果 API 逆向

### 背景

搜索引擎通常有内部 API（用于自动补全、相关搜索等），这些 API 的防护相对较弱。

### 逆向步骤

#### 1. 发现隐藏 API

使用 Chrome DevTools 监控网络请求:

**Google 自动补全 API**:

```
GET /complete/search?q=python&client=chrome HTTP/1.1
Host: www.google.com
```

**响应**:

```json
[
"python",
["python tutorial", "python download", "python for beginners", "python snake"]
]
```

**Bing 搜索建议 API**:

```
GET /AS/Suggestions?pt=page.home&mkt=en-US&qry=javascript&cp=10&cvid=xxx
Host: www.bing.com
```

#### 2. 逆向签名算法

某些 API 需要签名参数:

```javascript
// 在 Bing 搜索页面的 JS 中找到
function generateSearchSignature(query, timestamp) {
const secret = "bing_api_secret_2024";
const str = `${query}|${timestamp}|${secret}`;
return CryptoJS.SHA256(str).toString();
}

function searchAPI(query) {
const timestamp = Date.now();
const sig = generateSearchSignature(query, timestamp);

return fetch(
`/api/search?q=${encodeURIComponent(query)}&t=${timestamp}&sig=${sig}`
).then((r) => r.json());
}
```

### Python 实现

```python
import requests
import hashlib
import time
import json

class SearchEngineAPI:
def __init__(self):
self.session = requests.Session()
self.session.headers.update({
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
'Accept': 'application/json',
'Referer': 'https://www.google.com/'
})

def google_autocomplete(self, query):
"""Google 自动补全 API"""
url = 'https://www.google.com/complete/search'
params = {
'q': query,
'client': 'chrome', # 或 'firefox', 'safari'
'hl': 'en'
}

response = self.session.get(url, params=params)

# 响应格式: [query, [suggestions], ...]
data = response.json()
return data[1] if len(data) > 1 else []

def bing_suggestions(self, query):
"""Bing 搜索建议 API"""
url = 'https://www.bing.com/AS/Suggestions'
params = {
'pt': 'page.home',
'mkt': 'en-US',
'qry': query,
'cp': len(query),
'cvid': self._generate_cvid()
}

response = self.session.get(url, params=params)
data = response.json()

# 提取建议
suggestions = []
for group in data.get('AS', {}).get('Results', []):
for item in group.get('Suggests', []):
suggestions.append(item.get('Txt'))

return suggestions

def _generate_cvid(self):
"""生成 Bing 的 CVID (Correlation Vector ID)"""
import uuid
return str(uuid.uuid4()).replace('-', '')

def baidu_suggestion(self, query):
"""百度搜索建议 API"""
url = 'https://www.baidu.com/sugrec'
params = {
'prod': 'pc',
'wd': query,
'cb': 'jQuery' # JSONP callback
}

response = self.session.get(url, params=params)

# 解析 JSONP 响应
text = response.text
json_str = text[text.index('(') + 1:text.rindex(')')]
data = json.loads(json_str)

suggestions = [item['q'] for item in data.get('g', [])]
return suggestions

def signed_search(self, query, secret_key="bing_api_secret_2024"):
"""带签名的搜索 API"""
timestamp = int(time.time())
sig = self._generate_signature(query, timestamp, secret_key)

url = 'https://api.search.example.com/search'
params = {
'q': query,
't': timestamp,
'sig': sig
}

response = self.session.get(url, params=params)
return response.json()

def _generate_signature(self, query, timestamp, secret):
"""生成搜索签名"""
str_to_sign = f"{query}|{timestamp}|{secret}"
return hashlib.sha256(str_to_sign.encode()).hexdigest()

# 使用示例
api = SearchEngineAPI()

# Google 自动补全
suggestions = api.google_autocomplete('python')
print("Google suggestions:", suggestions)

# Bing 建议
bing_suggestions = api.bing_suggestions('javascript')
print("Bing suggestions:", bing_suggestions)

# 百度建议
baidu_suggestions = api.baidu_suggestion('机器学习')
print("Baidu suggestions:", baidu_suggestions)
```

---

## 案例 3: JavaScript 渲染结果提取

### 背景

现代搜索引擎大量使用 JavaScript 渲染结果（SPA），静态爬虫无法获取完整内容。

### 挑战

- **动态加载**: 滚动加载更多结果
- **延迟渲染**: 结果分批渲染
- **反调试**: 检测 DevTools、Selenium

### 解决方案

#### 1. 使用 Playwright（推荐）

```python
from playwright.sync_api import sync_playwright
import time

class JavaScriptSearchScraper:
def __init__(self):
self.playwright = None
self.browser = None
self.context = None

def setup(self):
"""初始化浏览器"""
self.playwright = sync_playwright().start()

# 使用隐身模式，避免检测
self.browser = self.playwright.chromium.launch(
headless=True,
args=[
'--disable-blink-features=AutomationControlled',
'--disable-dev-shm-usage',
'--no-sandbox'
]
)

# 修改 navigator.webdriver
self.context = self.browser.new_context(
viewport={'width': 1920, 'height': 1080},
user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
)

self.context.add_init_script("""
Object.defineProperty(navigator, 'webdriver', {
get: () => undefined
});
""")

def search_google(self, query, num_results=100):
"""搜索 Google 并提取结果"""
page = self.context.new_page()

# 访问搜索页面
page.goto(f'https://www.google.com/search?q={query}')

# 等待结果加载
page.wait_for_selector('#search', timeout=10000)

results = []
loaded_results = 0

# 滚动加载更多结果
while loaded_results < num_results:
# 提取当前可见结果
items = page.query_selector_all('.g')

for item in items[loaded_results:]:
try:
title_elem = item.query_selector('h3')
link_elem = item.query_selector('a')
snippet_elem = item.query_selector('.VwiC3b')

if title_elem and link_elem:
results.append({
'title': title_elem.inner_text(),
'url': link_elem.get_attribute('href'),
'snippet': snippet_elem.inner_text() if snippet_elem else ''
})

except Exception as e:
continue

loaded_results = len(results)

# 滚动到底部
page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
time.sleep(1)

# 检查是否有"更多结果"按钮
more_button = page.query_selector('a#pnnext')
if more_button and loaded_results < num_results:
more_button.click()
page.wait_for_load_state('networkidle')
else:
break

page.close()
return results

def search_bing(self, query):
"""搜索 Bing（处理无限滚动）"""
page = self.context.new_page()
page.goto(f'https://www.bing.com/search?q={query}')

# 等待结果
page.wait_for_selector('.b_algo')

results = []
last_height = 0

# 无限滚动
while True:
# 提取结果
items = page.query_selector_all('.b_algo')

for item in items[len(results):]:
try:
title = item.query_selector('h2').inner_text()
url = item.query_selector('a').get_attribute('href')
snippet = item.query_selector('.b_caption p').inner_text()

results.append({
'title': title,
'url': url,
'snippet': snippet
})

except:
continue

# 滚动
page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
time.sleep(2)

# 检查是否加载了新内容
new_height = page.evaluate('document.body.scrollHeight')
if new_height == last_height:
break

last_height = new_height

page.close()
return results

def cleanup(self):
"""清理资源"""
if self.context:
self.context.close()
if self.browser:
self.browser.close()
if self.playwright:
self.playwright.stop()

# 使用示例
scraper = JavaScriptSearchScraper()
scraper.setup()

try:
google_results = scraper.search_google('python tutorial', num_results=50)
print(f"Found {len(google_results)} Google results")

for result in google_results[:5]:
print(f"- {result['title']}: {result['url']}")

finally:
scraper.cleanup()
```

#### 2. 绕过反自动化检测

```python
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

class StealthScraper:
def __init__(self):
self.playwright = sync_playwright().start()

# 使用 playwright-stealth 插件
self.browser = self.playwright.chromium.launch(headless=True)
self.context = self.browser.new_context()

def scrape_with_stealth(self, url):
"""使用隐身模式爬取"""
page = self.context.new_page()

# 应用 stealth 模式
stealth_sync(page)

# 添加额外的反检测措施
page.add_init_script("""
// 覆盖 navigator.webdriver
Object.defineProperty(navigator, 'webdriver', {
get: () => undefined
});

// 覆盖 chrome 对象
window.chrome = {
runtime: {}
};

// 覆盖 permissions
const originalQuery = window.navigator.permissions.query;
window.navigator.permissions.query = (parameters) => (
parameters.name === 'notifications' ?
Promise.resolve({ state: Notification.permission }) :
originalQuery(parameters)
);

// 覆盖 plugins
Object.defineProperty(navigator, 'plugins', {
get: () => [1, 2, 3, 4, 5]
});

// 覆盖 languages
Object.defineProperty(navigator, 'languages', {
get: () => ['en-US', 'en']
});
""")

page.goto(url)
return page.content()
```

---

## 案例 4: 搜索排名监控

### 背景

SEO 工具需要监控关键词排名，但搜索引擎会返回个性化结果。

### 解决方案

#### 1. 禁用个性化

```python
class UnbiasedSearchMonitor:
def __init__(self):
self.session = requests.Session()

def google_unbiased_search(self, query):
"""获取非个性化的 Google 搜索结果"""
url = 'https://www.google.com/search'

# 使用特殊参数禁用个性化
params = {
'q': query,
'pws': '0', # Disable personalization
'gl': 'us', # Geo-location: US
'hl': 'en', # Language: English
'num': 100 # Results per page
}

headers = {
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
'Accept-Language': 'en-US,en;q=0.9',
'Accept': 'text/html,application/xhtml+xml',
# 不发送 Cookie（避免个性化）
}

response = self.session.get(url, params=params, headers=headers)
return self.parse_results(response.text)

def parse_results(self, html):
"""解析搜索结果"""
from bs4 import BeautifulSoup

soup = BeautifulSoup(html, 'html.parser')
results = []

# 查找所有搜索结果
for index, item in enumerate(soup.select('.g'), start=1):
title_elem = item.select_one('h3')
link_elem = item.select_one('a')

if title_elem and link_elem:
url = link_elem.get('href', '')

results.append({
'rank': index,
'title': title_elem.get_text(),
'url': url,
'domain': self.extract_domain(url)
})

return results

def extract_domain(self, url):
"""提取域名"""
from urllib.parse import urlparse
parsed = urlparse(url)
return parsed.netloc

def track_keyword_ranking(self, keyword, target_domain):
"""追踪关键词排名"""
results = self.google_unbiased_search(keyword)

for result in results:
if target_domain in result['domain']:
return result['rank']

return None # 未进入前 100

# 使用示例
monitor = UnbiasedSearchMonitor()

ranking = monitor.track_keyword_ranking(
keyword='web scraping tutorial',
target_domain='example.com'
)

print(f"Current ranking: {ranking if ranking else 'Not in top 100'}")
```

#### 2. 批量排名监控

```python
import asyncio
import aiohttp
from typing import List, Dict

class BatchRankingMonitor:
def __init__(self, keywords: List[str], target_domain: str):
self.keywords = keywords
self.target_domain = target_domain

async def check_ranking(self, session, keyword):
"""异步检查单个关键词排名"""
url = 'https://www.google.com/search'
params = {
'q': keyword,
'pws': '0',
'gl': 'us',
'num': 100
}

async with session.get(url, params=params) as response:
html = await response.text()

# 简单解析（实际应使用 BeautifulSoup）
if self.target_domain in html:
# 计算排名（简化版本）
rank = html.index(self.target_domain) // 1000 # 粗略估算
return {'keyword': keyword, 'rank': rank}
else:
return {'keyword': keyword, 'rank': None}

async def check_all(self):
"""批量检查所有关键词"""
async with aiohttp.ClientSession() as session:
tasks = [
self.check_ranking(session, kw)
for kw in self.keywords
]

results = await asyncio.gather(*tasks)
return results

# 使用示例
async def main():
keywords = [
'python tutorial',
'web scraping',
'data analysis',
'machine learning'
]

monitor = BatchRankingMonitor(keywords, 'example.com')
results = await monitor.check_all()

for result in results:
print(f"{result['keyword']}: Rank {result['rank']}")

asyncio.run(main())
```

---

## 案例 5: 行为检测与规避

### 背景

搜索引擎使用机器学习分析用户行为，检测爬虫。

### 检测指标

1. **鼠标轨迹**: 真实用户有不规则的鼠标移动
2. **键盘输入**: 真实用户有输入延迟和错误
3. **滚动模式**: 真实用户滚动不均匀
4. **点击模式**: 真实用户有犹豫、回退
5. **浏览历史**: 真实用户有跨页面浏览

### 对抗策略

```python
from playwright.sync_api import sync_playwright
import random
import time
import numpy as np

class HumanBehaviorSimulator:
def __init__(self):
self.playwright = None
self.browser = None
self.page = None

def setup(self):
"""初始化"""
self.playwright = sync_playwright().start()
self.browser = self.playwright.chromium.launch(headless=False)
self.page = self.browser.new_page()

def human_mouse_move(self, from_x, from_y, to_x, to_y):
"""模拟人类鼠标轨迹（贝塞尔曲线）"""
steps = random.randint(20, 40)

# 控制点（随机偏移）
cp1_x = from_x + (to_x - from_x) * random.uniform(0.2, 0.4) + random.uniform(-50, 50)
cp1_y = from_y + (to_y - from_y) * random.uniform(0.2, 0.4) + random.uniform(-50, 50)
cp2_x = from_x + (to_x - from_x) * random.uniform(0.6, 0.8) + random.uniform(-50, 50)
cp2_y = from_y + (to_y - from_y) * random.uniform(0.6, 0.8) + random.uniform(-50, 50)

for i in range(steps + 1):
t = i / steps

# 三次贝塞尔曲线
x = (1-t)**3 * from_x + \
3*(1-t)**2*t * cp1_x + \
3*(1-t)*t**2 * cp2_x + \
t**3 * to_x

y = (1-t)**3 * from_y + \
3*(1-t)**2*t * cp1_y + \
3*(1-t)*t**2 * cp2_y + \
t**3 * to_y

self.page.mouse.move(x, y)
time.sleep(random.uniform(0.005, 0.02))

def human_typing(self, text, element_selector):
"""模拟人类打字（带延迟和错误）"""
element = self.page.query_selector(element_selector)

for char in text:
# 随机延迟
delay = random.gauss(0.15, 0.05) # 平均 150ms
time.sleep(max(0.05, delay))

# 偶尔打错字
if random.random() < 0.05:
wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz')
element.type(wrong_char)
time.sleep(random.uniform(0.1, 0.3))
# 删除错字
self.page.keyboard.press('Backspace')
time.sleep(random.uniform(0.05, 0.15))

element.type(char)

def human_scroll(self, target_y):
"""模拟人类滚动"""
current_y = self.page.evaluate('window.pageYOffset')

distance = target_y - current_y
steps = random.randint(10, 20)

for i in range(steps):
# 加速 -> 减速
if i < steps / 2:
# 加速阶段
scroll_amount = distance / steps * (i + 1) / (steps / 2)
else:
# 减速阶段
scroll_amount = distance / steps * (steps - i) / (steps / 2)

self.page.evaluate(f'window.scrollBy(0, {scroll_amount})')
time.sleep(random.uniform(0.02, 0.05))

# 偶尔向上微调
if random.random() < 0.3:
self.page.evaluate('window.scrollBy(0, -50)')
time.sleep(random.uniform(0.1, 0.3))

def human_search(self, query):
"""模拟人类搜索行为"""
# 访问首页
self.page.goto('https://www.google.com')
time.sleep(random.uniform(0.5, 1.5))

# 移动鼠标到搜索框
search_box = self.page.query_selector('input[name="q"]')
box_position = search_box.bounding_box()

# 从随机位置移动到搜索框
self.human_mouse_move(
random.randint(100, 500),
random.randint(100, 400),
box_position['x'] + box_position['width'] / 2,
box_position['y'] + box_position['height'] / 2
)

# 点击搜索框
search_box.click()
time.sleep(random.uniform(0.2, 0.5))

# 人类化打字
self.human_typing(query, 'input[name="q"]')

# 随机选择提交方式
if random.random() < 0.7:
# 70% 按回车
self.page.keyboard.press('Enter')
else:
# 30% 点击搜索按钮
search_button = self.page.query_selector('input[name="btnK"]')
if search_button:
search_button.click()

# 等待结果
self.page.wait_for_selector('#search')
time.sleep(random.uniform(1.0, 2.0))

# 模拟浏览结果（滚动、阅读）
self.human_scroll(random.randint(500, 1500))
time.sleep(random.uniform(2.0, 4.0))

# 提取结果
results = []
items = self.page.query_selector_all('.g')

for item in items:
try:
title = item.query_selector('h3').inner_text()
url = item.query_selector('a').get_attribute('href')
results.append({'title': title, 'url': url})
except:
continue

return results

def cleanup(self):
"""清理"""
if self.browser:
self.browser.close()
if self.playwright:
self.playwright.stop()

# 使用示例
simulator = HumanBehaviorSimulator()
simulator.setup()

try:
results = simulator.human_search('python web scraping')
print(f"Found {len(results)} results")

for result in results[:5]:
print(f"- {result['title']}")

finally:
simulator.cleanup()
```

---

## 防护与对抗总结

### 搜索引擎防护

1. **CAPTCHA**: reCAPTCHA v2/v3, hCaptcha
2. **频率限制**: IP、Cookie、User-Agent
3. **行为分析**: 鼠标轨迹、打字模式、浏览历史
4. **设备指纹**: Canvas、WebGL、Audio
5. **TLS 指纹**: JA3/JA3S 检测
6. **API 签名**: 时间戳 + 密钥验证

### 对抗策略

1. **CAPTCHA 求解**: 第三方服务、机器学习
2. **IP 轮换**: 代理池、住宅代理
3. **行为模拟**: 鼠标轨迹、人类化延迟
4. **浏览器指纹伪造**: Playwright Stealth
5. **API 逆向**: 发现隐藏接口
6. **分布式爬取**: 多账号、多地域

---

## 法律与道德声明

**本文仅用于技术研究和教育目的**。未经授权爬取搜索引擎可能违反:

- 服务条款 (ToS)
- 计算机欺诈和滥用法 (CFAA)
- 各国反爬虫法律

请仅在授权环境下进行测试，尊重搜索引擎的 robots.txt。

---

## 工具推荐

### 爬虫框架

- **Scrapy**: Python 爬虫框架
- **Playwright**: 现代浏览器自动化
- **Puppeteer**: Node.js 浏览器控制

### 代理服务

- **Bright Data**: 住宅代理池
- **Oxylabs**: 企业级代理
- **SmartProxy**: 低成本选择

### CAPTCHA 求解

- **2Captcha**: 人工求解服务
- **Anti-Captcha**: 自动识别
- **CapSolver**: AI 识别

### 反检测

- **undetected-chromedriver**: 反 Selenium 检测
- **playwright-stealth**: Playwright 隐身
- **puppeteer-extra-plugin-stealth**: Puppeteer 隐身

---

## 相关章节

- [浏览器 DevTools 使用](../01-Tools/browser_devtools.md)
- [JavaScript Hook 技术](../02-Techniques/js_hook.md)
- [浏览器指纹识别](../03-Advanced-Topics/browser_fingerprinting.md)
- [TLS 指纹识别](../04-Advanced-Recipes/tls_fingerprinting.md)
- [CAPTCHA 识别与绕过](../03-Advanced-Topics/captcha_bypass.md)
