---
title: "反爬虫问题"
weight: 10
---

# 反爬虫问题

应对各种反爬虫机制的常见问题和解决方案。

---

## 403 Forbidden

### 问题表现

```
HTTP 403 Forbidden
Access Denied
```

### 原因分析

1. User-Agent 被检测
2. Referer 验证失败
3. IP 被封禁
4. 缺少必要的 Headers
5. JavaScript 挑战未通过

### 解决方案

#### 1. 完善 Headers

```python
import requests

headers = {
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
'Accept-Encoding': 'gzip, deflate, br',
'Connection': 'keep-alive',
'Upgrade-Insecure-Requests': '1',
'Sec-Fetch-Dest': 'document',
'Sec-Fetch-Mode': 'navigate',
'Sec-Fetch-Site': 'none',
'Sec-Fetch-User': '?1',
'Cache-Control': 'max-age=0',
}

# 如果是从其他页面跳转过来的，添加 Referer
headers['Referer'] = 'https://example.com/previous-page'

response = requests.get(url, headers=headers)
```

#### 2. 使用真实浏览器环境

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option('excludeSwitches', ['enable-automation'])
options.add_experimental_option('useAutomationExtension', False)

driver = webdriver.Chrome(options=options)

# 修改 webdriver 属性
driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
'source': '''
Object.defineProperty(navigator, 'webdriver', {
get: () => undefined
})
'''
})

driver.get(url)
```

#### 3. 使用无头浏览器

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
browser = p.chromium.launch(headless=True)
page = browser.new_page()

# 设置额外的 headers
page.set_extra_http_headers({
'Accept-Language': 'zh-CN,zh;q=0.9',
})

page.goto(url)
content = page.content()
browser.close()
```

---

## 429 Too Many Requests

### 问题表现

```
HTTP 429 Too Many Requests
Rate limit exceeded
```

### 原因分析

1. 请求频率过高
2. 同一 IP 请求过多
3. 超过 API 限额

### 解决方案

#### 1. 添加请求延迟

```python
import time
import random

def fetch_with_delay(url):
# 随机延迟 1-3 秒
delay = random.uniform(1, 3)
time.sleep(delay)

response = requests.get(url)
return response

# 批量请求
for url in urls:
response = fetch_with_delay(url)
# 处理响应...
```

#### 2. 实现退避算法

```python
import time

def fetch_with_backoff(url, max_retries=5):
"""指数退避重试"""
for attempt in range(max_retries):
try:
response = requests.get(url)

if response.status_code == 429:
# 获取 Retry-After 头
retry_after = int(response.headers.get('Retry-After', 60))
wait_time = min(retry_after, 2 ** attempt)

print(f"Rate limited. Waiting {wait_time}s...")
time.sleep(wait_time)
continue

return response

except Exception as e:
print(f"Attempt {attempt + 1} failed: {e}")
time.sleep(2 ** attempt)

raise Exception("Max retries exceeded")
```

#### 3. 使用代理池轮换

```python
import random

class ProxyPool:
def __init__(self, proxies):
self.proxies = proxies
self.failed_proxies = set()

def get_proxy(self):
"""获取可用代理"""
available = [p for p in self.proxies if p not in self.failed_proxies]
if not available:
# 重置失败列表
self.failed_proxies.clear()
available = self.proxies

return random.choice(available)

def mark_failed(self, proxy):
"""标记代理失败"""
self.failed_proxies.add(proxy)

# 使用示例
proxy_list = [
'http://proxy1.com:8080',
'http://proxy2.com:8080',
'http://proxy3.com:8080',
]

pool = ProxyPool(proxy_list)

def fetch_with_proxy_rotation(url):
for _ in range(3):
proxy = pool.get_proxy()
try:
response = requests.get(
url,
proxies={'http': proxy, 'https': proxy},
timeout=10
)
return response
except Exception as e:
print(f"Proxy {proxy} failed: {e}")
pool.mark_failed(proxy)

raise Exception("All proxies failed")
```

---

## IP 被封禁

### 问题表现

- 所有请求返回 403
- 长时间无响应
- 重定向到验证页面

### 解决方案

#### 1. 使用代理服务

```python
# 使用商业代理服务
PROXY_API_URL = "http://proxy-service.com/api/get"

def get_proxy():
"""从代理服务获取代理"""
response = requests.get(PROXY_API_URL)
proxy = response.text.strip()
return f"http://{proxy}"

def fetch_with_dynamic_proxy(url):
proxy = get_proxy()
proxies = {'http': proxy, 'https': proxy}

response = requests.get(url, proxies=proxies)
return response
```

#### 2. 使用 Tor 网络

```python
import requests

# Tor SOCKS5 代理 (需要运行 Tor 服务)
proxies = {
'http': 'socks5h://127.0.0.1:9050',
'https': 'socks5h://127.0.0.1:9050',
}

# 安装: pip install requests[socks]
response = requests.get(url, proxies=proxies)

# 验证 IP
ip_check = requests.get('http://httpbin.org/ip', proxies=proxies)
print(f"Current IP: {ip_check.json()}")
```

#### 3. 轮换用户身份

```python
import random

USER_AGENTS = [
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_1) ...',
'Mozilla/5.0 (X11; Linux x86_64) ...',
]

def get_random_headers():
return {
'User-Agent': random.choice(USER_AGENTS),
'Accept-Language': random.choice(['zh-CN,zh;q=0.9', 'en-US,en;q=0.9']),
}

response = requests.get(url, headers=get_random_headers())
```

---

## 验证码拦截

### 问题表现

- 登录或访问时出现验证码
- 图片验证码、滑块验证码、点选验证码

### 解决方案

#### 1. 图片验证码识别 (OCR)

```python
from PIL import Image
import pytesseract
import requests
from io import BytesIO

def recognize_captcha(captcha_url):
"""OCR 识别验证码"""
# 下载验证码
response = requests.get(captcha_url)
img = Image.open(BytesIO(response.content))

# 图片预处理
img = img.convert('L') # 转灰度
img = img.point(lambda x: 0 if x < 128 else 255) # 二值化

# OCR 识别
code = pytesseract.image_to_string(img, config='--psm 7')
return code.strip()

# 使用示例
captcha_code = recognize_captcha('https://example.com/captcha.jpg')
print(f"Recognized: {captcha_code}")
```

#### 2. 使用打码平台

```python
import requests
import time

class TwoCaptcha:
"""2Captcha 打码平台"""

def __init__(self, api_key):
self.api_key = api_key
self.base_url = "http://2captcha.com"

def solve_image_captcha(self, image_path):
"""解决图片验证码"""
# 1. 提交验证码
with open(image_path, 'rb') as f:
files = {'file': f}
data = {'key': self.api_key, 'method': 'post'}
response = requests.post(
f"{self.base_url}/in.php",
files=files,
data=data
)

if not response.text.startswith('OK|'):
raise Exception(f"Submit failed: {response.text}")

captcha_id = response.text.split('|')[1]

# 2. 轮询结果
for _ in range(20):
time.sleep(5)
result = requests.get(
f"{self.base_url}/res.php",
params={
'key': self.api_key,
'action': 'get',
'id': captcha_id
}
)

if result.text.startswith('OK|'):
return result.text.split('|')[1]

raise Exception("Timeout waiting for result")

# 使用示例
solver = TwoCaptcha(api_key='your_api_key')
code = solver.solve_image_captcha('captcha.jpg')
```

#### 3. 滑块验证码

```python
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time

def solve_slider_captcha(driver):
"""解决滑块验证码"""
# 找到滑块元素
slider = driver.find_element('css selector', '.slider-button')

# 模拟人类滑动轨迹
def get_track(distance):
"""生成移动轨迹"""
track = []
current = 0
mid = distance * 4 / 5

# 加速阶段
while current < mid:
move = 2
track.append(move)
current += move

# 减速阶段
while current < distance:
move = 1
track.append(move)
current += move

return track

# 获取需要滑动的距离
distance = 260 # 根据实际情况调整

# 执行滑动
action = ActionChains(driver)
action.click_and_hold(slider).perform()

for move in get_track(distance):
action.move_by_offset(move, 0).perform()
time.sleep(0.01)

action.release().perform()
time.sleep(1)
```

---

## JavaScript 挑战

### 问题表现

- 页面显示 "Checking your browser"
- Cloudflare、DataDome 等防护
- 需要执行 JavaScript 才能访问

### 解决方案

#### 1. 使用 cloudscraper

```python
import cloudscraper

# 自动绕过 Cloudflare
scraper = cloudscraper.create_scraper()
response = scraper.get(url)
print(response.text)
```

#### 2. 使用 Selenium + undetected-chromedriver

```python
import undetected_chromedriver as uc

driver = uc.Chrome()
driver.get(url)

# 等待页面加载
time.sleep(5)

# 获取内容
html = driver.page_source
driver.quit()
```

#### 3. 使用 Playwright (Stealth)

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
browser = p.chromium.launch(
headless=True,
args=['--disable-blink-features=AutomationControlled']
)

context = browser.new_context(
viewport={'width': 1920, 'height': 1080},
user_agent='Mozilla/5.0 ...'
)

page = context.new_page()

# 添加 stealth 脚本
page.add_init_script("""
Object.defineProperty(navigator, 'webdriver', {
get: () => undefined
});
Object.defineProperty(navigator, 'plugins', {
get: () => [1, 2, 3, 4, 5]
});
""")

page.goto(url)
page.wait_for_load_state('networkidle')

content = page.content()
browser.close()
```

---

## Cookie/Session 跟踪

### 问题表现

- 需要保持登录状态
- 跨页面请求失败
- Session 过期

### 解决方案

#### 1. 使用 Session 对象

```python
import requests

session = requests.Session()

# 登录
login_data = {
'username': 'user',
'password': 'pass'
}
session.post('https://example.com/login', data=login_data)

# 后续请求自动携带 Cookie
response = session.get('https://example.com/protected-page')

# 保存 Session
import pickle
with open('session.pkl', 'wb') as f:
pickle.dump(session.cookies, f)

# 加载 Session
with open('session.pkl', 'rb') as f:
session.cookies.update(pickle.load(f))
```

#### 2. 浏览器 Cookie 导入

```python
import browser_cookie3

# 从 Chrome 获取 Cookie
cookies = browser_cookie3.chrome(domain_name='example.com')

session = requests.Session()
session.cookies = cookies

response = session.get('https://example.com')
```

---

## TLS 指纹识别

### 问题表现

- 即使 Headers 完全相同仍被检测
- 基于 JA3 指纹识别

### 解决方案

#### 1. 使用 curl_cffi

```python
from curl_cffi import requests

# 模拟 Chrome 的 TLS 指纹
response = requests.get(
url,
impersonate="chrome110"
)
print(response.text)
```

#### 2. 使用真实浏览器

```python
# Playwright 和 Selenium 使用真实浏览器,
# 自然具有真实的 TLS 指纹

from playwright.sync_api import sync_playwright

with sync_playwright() as p:
browser = p.chromium.launch()
page = browser.new_page()
page.goto(url)
content = page.content()
browser.close()
```

---

## WebSocket 反爬

### 问题表现

- 实时数据通过 WebSocket 传输
- 需要维持长连接

### 解决方案

```python
import websocket
import json

def on_message(ws, message):
"""接收消息回调"""
data = json.loads(message)
print(f"Received: {data}")

def on_error(ws, error):
print(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
print("Connection closed")

def on_open(ws):
"""连接建立后发送订阅消息"""
subscribe_msg = json.dumps({
"action": "subscribe",
"channel": "data_feed"
})
ws.send(subscribe_msg)

# 创建 WebSocket 连接
ws = websocket.WebSocketApp(
"wss://example.com/ws",
on_open=on_open,
on_message=on_message,
on_error=on_error,
on_close=on_close,
header={
"User-Agent": "Mozilla/5.0 ...",
"Origin": "https://example.com"
}
)

ws.run_forever()
```

---

## 设备指纹识别

### 问题表现

- Canvas 指纹
- WebGL 指纹
- 浏览器特征识别

### 解决方案

#### 1. 使用指纹欺骗

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
browser = p.chromium.launch()
context = browser.new_context()

# 注入反指纹脚本
context.add_init_script("""
// 欺骗 Canvas 指纹
const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
HTMLCanvasElement.prototype.toDataURL = function() {
const context = this.getContext('2d');
const imageData = context.getImageData(0, 0, this.width, this.height);
// 添加噪点
for (let i = 0; i < imageData.data.length; i += 4) {
imageData.data[i] += Math.random() * 10 - 5;
}
context.putImageData(imageData, 0, 0);
return originalToDataURL.apply(this, arguments);
};

// 欺骗 WebGL 指纹
const getParameter = WebGLRenderingContext.prototype.getParameter;
WebGLRenderingContext.prototype.getParameter = function(parameter) {
if (parameter === 37445) {
return 'Intel Inc.';
}
if (parameter === 37446) {
return 'Intel Iris OpenGL Engine';
}
return getParameter.apply(this, arguments);
};
""")

page = context.new_page()
page.goto(url)
browser.close()
```

---

## 相关章节

- [浏览器指纹](../04-Advanced-Recipes/browser_fingerprinting.md)
- [CAPTCHA 绕过](../04-Advanced-Recipes/captcha_bypass.md)
- [反爬虫深度剖析](../04-Advanced-Recipes/anti_scraping_deep_dive.md)
- [TLS 指纹](../04-Advanced-Recipes/tls_fingerprinting.md)
