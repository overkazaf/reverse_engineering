---
title: "API 逆向与重放攻击"
date: 2024-08-25
type: posts
tags: ["Web", "RSA", "签名验证", "WebAssembly", "Canvas指纹", "代理池"]
weight: 10
---

# API 逆向与重放攻击

掌握 API 签名逆向，实现脱离浏览器的自动化请求。

---

## 配方信息

| 项目 | 说明 |
| ------------ | ------------------------------------ |
| **难度** | ⭐⭐⭐ (中级) |
| **预计时间** | 1-4 小时 |
| **所需工具** | Chrome DevTools, Python/Node.js |
| **适用场景** | API 签名破解、参数加密分析、请求伪造 |

---

## 📚 前置知识

在开始本配方之前，建议先掌握以下内容：

| 知识领域 | 重要程度 | 参考资料 |
|----------|---------|---------|
| HTTP/HTTPS 协议 | 必需 | [HTTP/HTTPS 协议](../01-Foundations/http_https_protocol.md) |
| Web API 与 Ajax | 必需 | [Web API 与 Ajax](../01-Foundations/web_api_and_ajax.md) |
| Hook 技术 | 必需 | [Hook 技术](./hooking_techniques.md) |
| 加密算法识别 | 推荐 | [加密算法识别](./crypto_identification.md) |
| Chrome DevTools | 推荐 | [浏览器开发者工具](../02-Tooling/browser_devtools.md) |

> 💡 **提示**: API 逆向是实现自动化爬取的关键步骤。掌握本配方后，你将能够脱离浏览器，用脚本直接调用目标网站的 API。

---

## 学习目标

完成本配方后，你将能够：

- ✅ 快速定位 API 签名算法
- ✅ 分析常见的签名结构 (MD5/SHA/HMAC)
- ✅ 处理时间戳、Nonce 等动态参数
- ✅ 实现完整的 API 重放攻击
- ✅ 编写自动化脚本调用 API

---

## 核心概念

逆向的最终目的通常不是为了看代码，而是为了**调用 API**。我们需要搞清楚客户端是如何构造请求的，以便我们在脚本中脱离浏览器伪造请求。

API 逆向的核心是**以假乱真** —— 让服务器无法区分请求来自浏览器还是自动化脚本。

---

## 1. 签名参数分析 (Signature Analysis)

大多数现代 API 都有签名机制，防止参数被篡改。

### 1.1 常见签名结构

#### 基础哈希签名

```python
# MD5 签名
sign = MD5(param1=a&param2=b&timestamp=123456&salt=xxxx)

# SHA256 签名
sign = SHA256(user_id + timestamp + secret_key)

# 多层签名
sign = MD5(SHA256(params) + salt)
```

#### HMAC 签名

```python
# HMAC-SHA256（更安全，防彩虹表）
import hmac
import hashlib

def generate_hmac_sign(params, secret_key):
message = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
return hmac.new(
secret_key.encode(),
message.encode(),
hashlib.sha256
).hexdigest()
```

#### 自定义签名算法

```javascript
// 某电商平台的魔改签名
function customSign(params) {
let str = Object.keys(params)
.sort()
.map((k) => params[k])
.join("");
// 魔改的 MD5：增加了位移和异或操作
let hash = md5(str);
return hash.split("").reverse().join("").substring(0, 16);
}
```

### 1.2 签名还原步骤

#### 第一步：观察变量规律

在 Network 面板发送 5-10 个请求，记录所有参数的变化：

| 请求序号 | timestamp | nonce | user_id | sign |
| -------- | ---------- | ------ | ------- | ----------- |
| 1 | 1638360000 | abc123 | 1001 | 5f8e9d2a... |
| 2 | 1638360003 | def456 | 1001 | 7a3b1c4e... |
| 3 | 1638360005 | ghi789 | 1001 | 2d6f8e1b... |

**分析规律**:

- `timestamp`: 每次递增，Unix 时间戳
- `nonce`: 随机字符串（6 位）
- `user_id`: 固定值
- `sign`: 每次都不同 → 依赖于其他参数

#### 第二步：定位签名逻辑

**方法 1: 关键字搜索**

```javascript
// 在 Sources 面板搜索以下关键字
sign;
signature;
_sign;
generateSign;
md5;
sha;
encrypt;
```

**方法 2: XHR Breakpoint**
在 DevTools 中设置 URL 断点：

- Network → 右键请求 → "Replay XHR"
- Sources → XHR/fetch Breakpoints → 添加 URL 关键字（如 `/api/`）
- 刷新页面，自动断在发包前

**方法 3: Hook XMLHttpRequest/fetch**

```javascript
// 注入到页面最前面（Console 或 Tampermonkey）
(function () {
const _open = XMLHttpRequest.prototype.open;
XMLHttpRequest.prototype.open = function (method, url) {
console.log("[XHR]", method, url);
if (url.includes("/api/data")) {
debugger; // 发送 /api/data 请求前自动断点
}
return _open.apply(this, arguments);
};
})();
```

#### 第三步：算法识别

**标准算法识别**

| 特征 | 算法 | 输出长度 |
| ----------------------- | ----------- | --------------------- |
| 字符集 `[0-9a-f]` | MD5 | 32 字符 |
| 字符集 `[0-9a-f]` | SHA1 | 40 字符 |
| 字符集 `[0-9a-f]` | SHA256 | 64 字符 |
| 字符集 `[A-Za-z0-9+/=]` | Base64 编码 | 任意长度，能被 4 整除 |
| 字符集 `[A-Za-z0-9]` | 自定义编码 | 需要分析具体逻辑 |

**在代码中查找特征码**

```javascript
// MD5 特征：初始化向量
0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476

// AES 特征：S-Box 表
0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5...

// RSA 特征：大素数运算
modPow, BigInteger, 0x10001 (常见公钥指数)
```

#### 第四步：复现签名算法

**案例：某视频网站签名**

逆向发现签名逻辑：

```javascript
// 浏览器中的签名函数
function getSign(videoId, timestamp) {
const salt = "h5@video#2024";
const raw = `videoId=${videoId}&ts=${timestamp}&salt=${salt}`;
return md5(raw).toUpperCase();
}
```

Python 复现：

```python
import hashlib
import time

def get_sign(video_id, timestamp=None):
if timestamp is None:
timestamp = int(time.time())

salt = "h5@video#2024"
raw = f"videoId={video_id}&ts={timestamp}&salt={salt}"
return hashlib.md5(raw.encode()).hexdigest().upper()

# 测试
sign = get_sign("BV1xv4y1X7Yp")
print(sign) # 输出：E8A7F2D3C1B9...
```

---

## 2. 加密参数分析

除了签名，很多 API 会对**整个请求体**或**敏感参数**加密。

### 2.1 AES 加密

**特征识别**

```javascript
// 代码中可能出现的关键字
CryptoJS.AES.encrypt;
crypto.createCipheriv("aes-128-cbc");
Cipher.getInstance("AES/CBC/PKCS5Padding");
```

**案例：某登录接口**

浏览器代码：

```javascript
function encryptPassword(password) {
const key = CryptoJS.enc.Utf8.parse("1234567890abcdef");
const iv = CryptoJS.enc.Utf8.parse("abcdef1234567890");
const encrypted = CryptoJS.AES.encrypt(password, key, {
iv: iv,
mode: CryptoJS.mode.CBC,
padding: CryptoJS.pad.Pkcs7,
});
return encrypted.toString(); // Base64 格式
}
```

Python 复现：

```python
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64

def encrypt_password(password):
key = b'1234567890abcdef'
iv = b'abcdef1234567890'

cipher = AES.new(key, AES.MODE_CBC, iv)
encrypted = cipher.encrypt(pad(password.encode(), AES.block_size))
return base64.b64encode(encrypted).decode()

# 测试
print(encrypt_password("MyPassword123"))
```

### 2.2 RSA 加密

通常用于加密 AES 的密钥（混合加密）或登录密码。

**提取公钥**

```javascript
// 浏览器中查找
publicKey = "-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGS..."

// 或从接口返回
GET /api/getPublicKey
{
"key": "MIGfMA0GCSqGS..."
}
```

**Python 复现**

```python
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import base64

def rsa_encrypt(text, public_key_str):
public_key = RSA.import_key(public_key_str)
cipher = PKCS1_v1_5.new(public_key)
encrypted = cipher.encrypt(text.encode())
return base64.b64encode(encrypted).decode()

public_key = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC...
-----END PUBLIC KEY-----"""

password_encrypted = rsa_encrypt("MyPassword123", public_key)
```

### 2.3 自定义加密算法

**案例：某 App 的魔改 Base64**

逆向发现它把标准 Base64 字符表打乱了：

```javascript
// 标准 Base64 字符表
const stdTable =
"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

// 魔改后的字符表（故意打乱）
const customTable =
"LMNOPQRSTUVWXYZABCDEFGHIJKabcdefghijklmnopqrstuv0123456789wx+/yz";
```

**复现方法**: 把混淆后的 Base64 编码/解码函数扣下来，改成 Python。

---

## 3. 重放攻击 (Replay Attack)

重放是验证逆向成果最简单的方法。

### 3.1 简单重放（无时间戳校验）

1. 在 Network 面板右键请求 → "Copy as cURL"
2. 在终端粘贴运行

```bash
curl 'https://api.example.com/data?user_id=123&sign=abc123' \
-H 'User-Agent: Mozilla/5.0' \
-H 'Cookie: session=xyz'
```

**如果能拿到数据**，说明该接口：

- ✅ 没有时间戳校验
- ✅ 没有 Nonce 校验
- ✅ 签名有效期很长（或无限期）

### 3.2 高级重放（带时间戳）

```python
import requests
import time
import hashlib

def generate_sign(params, salt="my_secret_salt"):
"""生成签名"""
s = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
s += f"&salt={salt}"
return hashlib.md5(s.encode()).hexdigest()

def api_request(user_id):
"""API 请求"""
params = {
"user_id": user_id,
"timestamp": int(time.time()),
"nonce": hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
}
params["sign"] = generate_sign(params)

response = requests.get(
"https://api.example.com/data",
params=params,
headers={
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
"Referer": "https://www.example.com/"
}
)
return response.json()

# 测试
print(api_request(123))
```

### 3.3 Session/Cookie 管理

**案例：登录 + API 调用**

```python
import requests

class APIClient:
def __init__(self):
self.session = requests.Session()
self.session.headers.update({
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
})

def login(self, username, password):
"""登录获取 Session"""
response = self.session.post(
"https://www.example.com/login",
data={
"username": username,
"password": self.encrypt_password(password) # 使用前面的加密函数
}
)
if response.json()["code"] == 0:
print("登录成功，Session 已保存")
return True
return False

def get_user_data(self, user_id):
"""调用需要登录的 API"""
params = {"user_id": user_id}
params["sign"] = self.generate_sign(params)

response = self.session.get(
"https://api.example.com/user/data",
params=params
)
return response.json()

def encrypt_password(self, password):
# 这里调用前面写的加密函数
pass

def generate_sign(self, params):
# 这里调用前面写的签名函数
pass

# 使用
client = APIClient()
if client.login("myusername", "mypassword"):
data = client.get_user_data(123)
print(data)
```

---

## 4. 防重放机制绕过

### 4.1 时间戳校验

**特征**

- 服务器检查 `timestamp` 是否在当前时间的 ± 60 秒内
- 旧请求会返回 `{"error": "Request expired"}`

**绕过方法**

```python
import time
import ntplib # pip install ntplib

def get_server_timestamp():
"""获取标准时间（防止本地时钟不准）"""
try:
client = ntplib.NTPClient()
response = client.request('pool.ntp.org')
return int(response.tx_time)
except:
return int(time.time())

# 使用
params = {
"user_id": 123,
"timestamp": get_server_timestamp() # 使用标准时间
}
```

### 4.2 Nonce（随机数）校验

**特征**

- 服务器会缓存最近 10 分钟的所有 `nonce`
- 重复的 `nonce` 会被拒绝：`{"error": "Duplicate request"}`

**绕过方法**

```python
import uuid

def generate_nonce():
"""每次生成唯一的 nonce"""
return uuid.uuid4().hex # 示例：'a8f5f167f44f4964e6c998dee827110c'

# 或使用时间戳 + 随机数
import random
def generate_nonce_v2():
return f"{int(time.time())}{random.randint(1000, 9999)}"
```

### 4.3 序列号（Sequence）校验

**特征**

- 常见于 WebSocket 或长连接协议
- 每个包必须有递增的序列号：1, 2, 3, 4...
- 乱序或重复的包会被丢弃

**绕过方法**

```python
class WebSocketClient:
def __init__(self):
self.seq = 0 # 初始序列号

def send_message(self, msg_type, data):
self.seq += 1 # 自增序列号
packet = {
"seq": self.seq,
"type": msg_type,
"data": data
}
self.ws.send(json.dumps(packet))
```

---

## 5. 认证系统分析

### 5.1 JWT (JSON Web Token)

**识别方法**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjEyMywiaWF0IjoxNjM4MzYwMDAwfQ.5f8e9d2a7b3c1e4f...
```

三段用 `.` 分隔：

1. Header (算法类型)
2. Payload (用户数据)
3. Signature (签名，防篡改)

**解码**

```python
import jwt

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjEyMywiaWF0IjoxNjM4MzYwMDAwfQ.5f8e9d2a..."

# 解码（不验证签名）
payload = jwt.decode(token, options={"verify_signature": False})
print(payload) # {'userId': 123, 'iat': 1638360000}
```

**注意**：JWT 的签名密钥（secret）在服务端，客户端无法伪造。逆向重点是**如何获取有效的 Token**（通常通过登录）。

### 5.2 自定义 Token

**案例：某平台的 Token 生成**

```javascript
// 浏览器逻辑
function generateToken(userId, deviceId) {
const timestamp = Date.now();
const raw = `${userId}|${deviceId}|${timestamp}`;
const encrypted = AES.encrypt(raw, SECRET_KEY);
return Base64.encode(encrypted);
}
```

**复现**

```python
from Crypto.Cipher import AES
import base64
import time

def generate_token(user_id, device_id):
timestamp = int(time.time() * 1000)
raw = f"{user_id}|{device_id}|{timestamp}"

# 假设逆向出的 SECRET_KEY
key = b'sixteen byte key'
cipher = AES.new(key, AES.MODE_ECB)
encrypted = cipher.encrypt(raw.ljust(16).encode())
return base64.b64encode(encrypted).decode()
```

---

## 6. 高级技巧：RPC 调用

当 JS 逻辑过于复杂（如 WebAssembly、VM 保护），直接复现算法成本太高，可以使用 **RPC（Remote Procedure Call）** 技术。

### 6.1 原理

在浏览器中注入一个 WebSocket 服务器，Python 客户端通过 WebSocket 调用浏览器中的 JS 函数。

### 6.2 实现

**浏览器端（通过 Tampermonkey 注入）**

```javascript
// ==UserScript==
// @name RPC Server
// @match https://www.example.com/*
// ==/UserScript==

const ws = new WebSocket("ws://127.0.0.1:8765");

ws.onmessage = function (event) {
const request = JSON.parse(event.data);
let result;

try {
// 调用页面中的签名函数
if (request.method === "getSign") {
result = window.getSign(request.params.videoId, request.params.timestamp);
}
ws.send(JSON.stringify({ id: request.id, result: result }));
} catch (e) {
ws.send(JSON.stringify({ id: request.id, error: e.message }));
}
};
```

**Python 客户端**

```python
import asyncio
import websockets
import json

class RPCClient:
def __init__(self):
self.request_id = 0

async def call(self, method, params):
async with websockets.connect('ws://127.0.0.1:8765') as ws:
self.request_id += 1
request = {
'id': self.request_id,
'method': method,
'params': params
}
await ws.send(json.dumps(request))
response = await ws.recv()
return json.loads(response)['result']

# 使用
async def main():
client = RPCClient()
sign = await client.call('getSign', {'videoId': 'BV1xv4y1X7Yp', 'timestamp': 1638360000})
print(f"签名结果: {sign}")

asyncio.run(main())
```

**优点**：

- ✅ 不需要复现复杂算法
- ✅ 自动跟随网站更新
- ✅ 可调用任何 JS 函数（包括 WebAssembly）

**缺点**：

- ❌ 需要浏览器一直运行
- ❌ 性能较低（网络通信开销）
- ❌ 不适合高并发场景

---

## 7. 常见陷阱与调试技巧

### 7.1 参数顺序问题

**错误示例**

```python
# Python 的字典是无序的（3.7+ 保持插入顺序）
params = {"c": 3, "a": 1, "b": 2}
sign = md5("&".join([f"{k}={v}" for k in params])) # ❌ 错误
```

**正确做法**

```python
# 必须按字典序或指定顺序排序
sign = md5("&".join([f"{k}={params[k]}" for k in sorted(params.keys())])) # ✅ 正确
```

### 7.2 字符编码问题

```python
# 浏览器中可能使用 UTF-8 编码
sign_js = md5("中文参数") # JavaScript 默认 UTF-8

# Python 必须显式指定编码
sign_py = hashlib.md5("中文参数".encode('utf-8')).hexdigest() # ✅
```

### 7.3 浮点数精度

```javascript
// JavaScript
timestamp = Date.now(); // 1638360000123（13位毫秒）

// Python
timestamp = int(time.time()); // 1638360000（10位秒）❌
timestamp = int(time.time() * 1000); // 1638360000123 ✅
```

### 7.4 调试技巧：Diff 对比

当签名始终不匹配时，对比浏览器和脚本的中间结果：

```python
# 在浏览器 Console 中打印
console.log("待签名字符串:", rawString);
console.log("签名结果:", sign);

# 在 Python 中打印
print("待签名字符串:", raw_string)
print("签名结果:", sign)

# 使用在线 Diff 工具对比
# https://www.diffchecker.com/
```

---

## 8. 实战案例

### 案例 1：某新闻网站评论接口

**目标**: 自动发表评论

**分析过程**:

1. 抓包发现 POST 请求参数包含 `content`, `article_id`, `timestamp`, `sign`
2. 搜索 `sign` 关键字，定位到 `utils.js:1234`
3. 发现签名逻辑：`MD5(article_id + content + timestamp + "news_secret_2024")`
4. 测试发现 `timestamp` 有 ± 5 分钟容错

**完整脚本**:

```python
import requests
import hashlib
import time

def post_comment(article_id, content):
timestamp = int(time.time())
sign = hashlib.md5(
f"{article_id}{content}{timestamp}news_secret_2024".encode()
).hexdigest()

data = {
"article_id": article_id,
"content": content,
"timestamp": timestamp,
"sign": sign
}

response = requests.post(
"https://news.example.com/api/comment/add",
data=data,
headers={
"User-Agent": "Mozilla/5.0",
"Cookie": "session=YOUR_SESSION_COOKIE"
}
)
return response.json()

# 测试
result = post_comment(12345, "这篇文章写得真好！")
print(result)
```

### 案例 2：某电商搜索接口（AES 加密）

**目标**: 批量搜索商品价格

**分析过程**:

1. 发现请求参数 `q` 是加密的：`q=U2FsdGVkX1+3g7h2k...`（Base64 格式）
2. 搜索 `encrypt` 关键字，找到 `CryptoJS.AES.encrypt`
3. 提取 AES 密钥和 IV（硬编码在 JS 中）
4. 发现加密模式为 AES-128-CBC

**完整脚本**:

```python
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64
import requests

def encrypt_query(keyword):
key = b'1234567890abcdef'
iv = b'abcdef1234567890'

cipher = AES.new(key, AES.MODE_CBC, iv)
encrypted = cipher.encrypt(pad(keyword.encode(), AES.block_size))
return base64.b64encode(encrypted).decode()

def search_product(keyword):
encrypted_q = encrypt_query(keyword)

response = requests.get(
"https://shop.example.com/api/search",
params={"q": encrypted_q}
)
return response.json()

# 批量搜索
keywords = ["iPhone 15", "MacBook Pro", "AirPods"]
for keyword in keywords:
results = search_product(keyword)
print(f"{keyword}: {results['total']} 个结果")
```

---

## 9. 防御与对抗

### 9.1 服务端防护手段

| 防护方法 | 原理 | 绕过难度 |
| ---------------- | ---------------------------- | --------------------------------- |
| **时间戳校验** | 拒绝过期请求（± 60s） | ⭐ 简单（同步时钟） |
| **Nonce 去重** | 缓存最近的随机数 | ⭐⭐ 中等（生成唯一值） |
| **请求频率限制** | 单 IP/用户限制 QPS | ⭐⭐⭐ 较难（IP 池 + 账号池） |
| **行为分析** | 检测自动化特征（速度、顺序） | ⭐⭐⭐⭐ 困难（模拟人类行为） |
| **设备指纹** | 绑定设备（Canvas、WebGL） | ⭐⭐⭐⭐ 困难（伪造指纹） |
| **验证码** | 人机识别（滑块、点选） | ⭐⭐⭐⭐⭐ 极难（OCR + 打码平台） |

### 9.2 逆向工程师对策

```python
# 1. 使用 IP 代理池
import requests

proxies = {
'http': 'http://proxy1.com:8080',
'https': 'http://proxy1.com:8080'
}
response = requests.get(url, proxies=proxies)

# 2. 随机化请求间隔
import random
import time

for i in range(100):
api_request()
time.sleep(random.uniform(2, 5)) # 2-5秒随机延迟

# 3. 模拟真实浏览器行为
headers = {
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
'Accept-Encoding': 'gzip, deflate, br',
'Referer': 'https://www.example.com/',
'DNT': '1',
'Connection': 'keep-alive',
'Upgrade-Insecure-Requests': '1'
}
```

---

## 10. 工具推荐

| 工具 | 用途 | 平台 |
| -------------- | ----------------------------- | ------- |
| **Postman** | API 调试、请求重放 | 全平台 |
| **mitmproxy** | 抓包、请求修改、Python 脚本 | 全平台 |
| **Burp Suite** | 高级抓包、参数 Fuzz、重放攻击 | 全平台 |
| **Fiddler** | Windows 抓包神器 | Windows |
| **Charles** | macOS 抓包工具 | macOS |
| **Insomnia** | API 调试（Postman 替代品） | 全平台 |

---

## 总结

API 逆向的本质是**理解通信协议**。掌握以下技能你将无往不利：

1. ✅ **签名算法识别**：MD5/SHA/HMAC/自定义算法
2. ✅ **加密参数分析**：AES/RSA/自定义加密
3. ✅ **防重放机制绕过**：时间戳/Nonce/序列号
4. ✅ **认证系统**：JWT/Session/自定义 Token
5. ✅ **RPC 调用**：处理复杂 JS/WASM 逻辑
6. ✅ **对抗检测**：IP 池、行为模拟、验证码处理

**记住**: 服务器看不出请求来自脚本还是浏览器，你就成功了。

---

## 相关章节

- [JavaScript 反混淆](../04-Advanced-Recipes/javascript_deobfuscation.md)
- [加密算法识别](../03-Basic-Recipes/crypto_identification.md)
- [动态参数分析](./dynamic_parameter_analysis.md)
- [Puppeteer 与 Playwright](../02-Tooling/puppeteer_playwright.md)
- [验证码绕过](../04-Advanced-Recipes/captcha_bypass.md)
