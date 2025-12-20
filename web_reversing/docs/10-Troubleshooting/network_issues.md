# 网络和请求问题

常见的网络连接和 HTTP 请求问题及解决方案。

---

## 请求超时

### 问题表现

```python
requests.exceptions.Timeout: HTTPConnectionPool(host='example.com', port=80):
Read timed out. (read timeout=10)
```

### 原因分析

1. 网络延迟过高
2. 服务器响应慢
3. 超时设置过短
4. 代理连接问题

### 解决方案

#### 1. 增加超时时间

```python
import requests

# 设置更长的超时时间 (连接超时, 读取超时)
response = requests.get(url, timeout=(10, 30))

# 或者只设置总超时
response = requests.get(url, timeout=60)
```

#### 2. 配置重试机制

```python
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()

# 配置重试策略
retry_strategy = Retry(
    total=3,                    # 总重试次数
    backoff_factor=2,          # 重试间隔倍数
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
)

adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)

# 发送请求
response = session.get(url, timeout=30)
```

#### 3. 使用异步请求

```python
import asyncio
import aiohttp

async def fetch(session, url):
    try:
        async with session.get(url, timeout=30) as response:
            return await response.text()
    except asyncio.TimeoutError:
        print(f"Timeout: {url}")
        return None

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
        return results

results = asyncio.run(main())
```

---

## 连接被拒绝

### 问题表现

```python
requests.exceptions.ConnectionError: HTTPConnectionPool(host='example.com', port=80):
Max retries exceeded with url: / (Caused by NewConnectionError)
```

### 原因分析

1. 目标服务器不可用
2. 网络不通
3. 端口错误
4. 防火墙拦截

### 解决方案

#### 1. 检查网络连通性

```bash
# 测试连接
ping example.com

# 测试端口
telnet example.com 80
# 或使用 nc
nc -zv example.com 80

# 使用 curl 测试
curl -I https://example.com
```

#### 2. 检查 URL 格式

```python
from urllib.parse import urlparse

url = "https://example.com:443/path"
parsed = urlparse(url)

print(f"Scheme: {parsed.scheme}")    # https
print(f"Host: {parsed.netloc}")      # example.com:443
print(f"Port: {parsed.port}")        # 443
print(f"Path: {parsed.path}")        # /path

# 确保 URL 格式正确
if not url.startswith(('http://', 'https://')):
    url = 'https://' + url
```

#### 3. 配置代理

```python
proxies = {
    'http': 'http://proxy.com:8080',
    'https': 'http://proxy.com:8080',
}

response = requests.get(url, proxies=proxies)
```

---

## SSL 证书错误

### 问题表现

```python
requests.exceptions.SSLError: HTTPSConnectionPool(host='example.com', port=443):
SSL certificate verify failed
```

### 原因分析

1. 服务器证书过期
2. 证书不被信任
3. 自签名证书
4. 证书链不完整

### 解决方案

#### 1. 禁用 SSL 验证 (仅用于测试)

```python
import requests
import urllib3

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 禁用验证
response = requests.get(url, verify=False)
```

#### 2. 指定 CA 证书

```python
# 使用系统证书
import certifi

response = requests.get(url, verify=certifi.where())

# 或指定自定义证书
response = requests.get(url, verify='/path/to/ca-bundle.crt')
```

#### 3. 使用自定义 SSL 上下文

```python
import ssl
import urllib3

# 创建 SSL 上下文
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

# 使用 urllib3
http = urllib3.PoolManager(
    ssl_context=context,
    cert_reqs='CERT_NONE'
)

response = http.request('GET', url)
```

---

## 代理配置问题

### 问题表现

- 请求无法通过代理
- 代理认证失败
- HTTPS 代理不生效

### 解决方案

#### 1. HTTP 代理

```python
# 基础代理
proxies = {
    'http': 'http://proxy.com:8080',
    'https': 'http://proxy.com:8080',
}

response = requests.get(url, proxies=proxies)
```

#### 2. SOCKS 代理

```python
# 需要安装: pip install requests[socks]
proxies = {
    'http': 'socks5://127.0.0.1:1080',
    'https': 'socks5://127.0.0.1:1080',
}

response = requests.get(url, proxies=proxies)
```

#### 3. 代理认证

```python
# 带用户名密码的代理
proxies = {
    'http': 'http://username:password@proxy.com:8080',
    'https': 'http://username:password@proxy.com:8080',
}

response = requests.get(url, proxies=proxies)
```

#### 4. 环境变量配置

```bash
# Linux/Mac
export HTTP_PROXY="http://proxy.com:8080"
export HTTPS_PROXY="http://proxy.com:8080"

# Windows
set HTTP_PROXY=http://proxy.com:8080
set HTTPS_PROXY=http://proxy.com:8080
```

```python
# 自动使用环境变量中的代理
response = requests.get(url)  # 会自动读取 HTTP_PROXY
```

#### 5. 验证代理配置

```python
import requests

def test_proxy(proxy_url):
    """测试代理是否可用"""
    proxies = {
        'http': proxy_url,
        'https': proxy_url,
    }

    try:
        response = requests.get(
            'http://httpbin.org/ip',
            proxies=proxies,
            timeout=10
        )
        print(f"✅ Proxy working: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Proxy failed: {e}")
        return False

test_proxy('http://127.0.0.1:7890')
```

---

## Cookie 失效

### 问题表现

- 登录状态丢失
- 请求被重定向到登录页
- 返回 401 Unauthorized

### 解决方案

#### 1. 使用 Session 保持 Cookie

```python
import requests

# 创建 Session
session = requests.Session()

# 登录 (Cookie 会自动保存)
session.post('https://example.com/login', data={
    'username': 'user',
    'password': 'pass'
})

# 后续请求会自动带上 Cookie
response = session.get('https://example.com/profile')
```

#### 2. 手动管理 Cookie

```python
# 获取 Cookie
response = requests.post(login_url, data=credentials)
cookies = response.cookies

# 使用 Cookie
response = requests.get(url, cookies=cookies)
```

#### 3. 从浏览器复制 Cookie

```python
# 浏览器中复制 Cookie 字符串
cookie_str = "session_id=abc123; user_id=456; token=xyz"

# 转换为字典
cookies = {}
for item in cookie_str.split('; '):
    key, value = item.split('=', 1)
    cookies[key] = value

response = requests.get(url, cookies=cookies)
```

#### 4. 持久化 Cookie

```python
import pickle

# 保存 Cookie
with open('cookies.pkl', 'wb') as f:
    pickle.dump(session.cookies, f)

# 加载 Cookie
with open('cookies.pkl', 'rb') as f:
    cookies = pickle.load(f)
    session.cookies.update(cookies)
```

#### 5. Cookie 调试

```python
import requests

session = requests.Session()

# 查看当前 Cookie
print("Current cookies:")
for cookie in session.cookies:
    print(f"  {cookie.name} = {cookie.value}")
    print(f"    Domain: {cookie.domain}")
    print(f"    Path: {cookie.path}")
    print(f"    Expires: {cookie.expires}")
```

---

## 响应编码问题

### 问题表现

```python
# 乱码输出
print(response.text)  # 输出: �����
```

### 解决方案

#### 1. 自动检测编码

```python
import requests
from chardet import detect

response = requests.get(url)

# 检测编码
encoding = detect(response.content)['encoding']
response.encoding = encoding

print(response.text)  # 正确显示中文
```

#### 2. 手动指定编码

```python
response = requests.get(url)

# 常见中文编码
response.encoding = 'utf-8'
# 或
response.encoding = 'gbk'
# 或
response.encoding = 'gb2312'

print(response.text)
```

#### 3. 直接使用 bytes

```python
response = requests.get(url)

# 使用 content (bytes) 而不是 text (str)
html = response.content.decode('utf-8', errors='ignore')
```

---

## 重定向问题

### 问题表现

- 无限重定向
- 重定向后丢失参数

### 解决方案

#### 1. 控制重定向

```python
# 禁止自动重定向
response = requests.get(url, allow_redirects=False)
print(f"Status: {response.status_code}")
print(f"Location: {response.headers.get('Location')}")

# 手动处理重定向
if response.status_code in [301, 302, 303, 307, 308]:
    redirect_url = response.headers['Location']
    response = requests.get(redirect_url)
```

#### 2. 查看重定向历史

```python
response = requests.get(url)

# 查看重定向链
for r in response.history:
    print(f"{r.status_code} -> {r.url}")

print(f"Final: {response.status_code} -> {response.url}")
```

---

## Headers 配置问题

### 问题表现

- 请求被拒绝
- 返回异常数据

### 解决方案

#### 1. 完整的 Headers

```python
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Referer': 'https://example.com/',
    'Origin': 'https://example.com',
}

response = requests.get(url, headers=headers)
```

#### 2. 从浏览器复制 Headers

```javascript
// 浏览器控制台执行
copy(
  JSON.stringify(
    Object.fromEntries(
      [
        ...document.querySelector(".request-headers").querySelectorAll("tr"),
      ].map((r) => [r.cells[0].textContent, r.cells[1].textContent])
    ),
    null,
    2
  )
);
```

#### 3. 调试 Headers

```python
# 查看请求头
response = requests.get('http://httpbin.org/headers', headers=headers)
print(response.json())

# 查看响应头
print(response.headers)
```

---

## 📚 相关章节

- [HTTP/HTTPS 协议](../01-Foundations/http_https_protocol.md)
- [HTTP Headers 速查](../08-Cheat-Sheets/http_headers.md)
- [调试技巧](../03-Basic-Recipes/debugging_techniques.md)
