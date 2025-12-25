---
title: "金融网站逆向案例"
date: 2025-10-13
tags: ["Web", "RSA", "浏览器指纹", "签名验证", "Canvas指纹", "案例分析"]
weight: 10
---

# 金融网站逆向案例

## 概述

金融网站通常具有极高的安全要求，包括多层加密、动态令牌、设备指纹、行为分析等。本文通过真实案例介绍金融网站的逆向分析方法和安全机制。

---

## 案例一：股票行情数据加密

### 背景

某股票交易平台的实时行情接口返回加密数据：

```json
{
"code": "600000",
"data": "eJyNVE1v2zAM/SuBzs4h...",
"timestamp": 1702800000
}
```

前端能实时显示股价、涨跌幅等信息，说明存在解密逻辑。

---

### 逆向步骤

#### 1. 抓包分析

使用 Chrome DevTools 观察 WebSocket 通信：

```javascript
// 打开控制台
const ws = new WebSocket("wss://stock.example.com/realtime");

ws.onmessage = function (event) {
console.log("Raw data:", event.data);
// {"code":"600000","data":"eJyNVE1v2zAM...","timestamp":1702800000}
};
```

#### 2. 定位解密函数

**方法：搜索关键词**

在 Sources 面板全局搜索：

- `"data"` 字段访问
- `decompress`
- `inflate`
- `pako` (常见压缩库)

找到解密代码：

```javascript
function decodeMarketData(encryptedData) {
// 1. Base64 解码
const compressed = atob(encryptedData);

// 2. 使用 pako 解压缩 (GZIP)
const binaryData = pako.inflate(compressed, { to: "string" });

// 3. JSON 解析
return JSON.parse(binaryData);
}
```

#### 3. Python 实现

```python
import base64
import gzip
import json

def decode_market_data(encrypted_data):
# Base64 解码
compressed = base64.b64decode(encrypted_data)

# GZIP 解压
decompressed = gzip.decompress(compressed)

# JSON 解析
return json.loads(decompressed.decode('utf-8'))

# 测试
encrypted = "eJyNVE1v2zAM/SuBzs4h..."
data = decode_market_data(encrypted)
print(data)
# {
# "price": 13.56,
# "change": 0.23,
# "volume": 1234567,
# ...
# }
```

---

## 案例二：登录加密与双因素认证

### 背景

某网银登录流程：

1. 输入用户名密码
2. 密码需要加密传输
3. 需要短信验证码（双因素认证）
4. 登录成功后获取 Token

---

### 逆向步骤

#### 1. 抓包分析登录请求

```http
POST /api/login HTTP/1.1
Content-Type: application/json

{
"username": "user123",
"password_enc": "MIGfMA0GCSqGSIb3DQEBA...",
"device_id": "uuid-1234-5678",
"timestamp": 1702800000,
"sign": "e10adc3949ba59abbe56e057f20f883e"
}
```

#### 2. 分析密码加密

在登录按钮点击事件上设置断点：

```javascript
// 找到加密函数
function encryptPassword(password, publicKey) {
// 使用 RSA 公钥加密
const encrypt = new JSEncrypt();
encrypt.setPublicKey(publicKey);
return encrypt.encrypt(password);
}

// 公钥从服务器获取
fetch("/api/public-key")
.then((res) => res.json())
.then((data) => {
const publicKey = data.public_key;
const encryptedPwd = encryptPassword(password, publicKey);
// 发送登录请求
});
```

**公钥示例**:

```
-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC...
-----END PUBLIC KEY-----
```

#### 3. 设备指纹生成

```javascript
function generateDeviceId() {
const fingerprint = {
userAgent: navigator.userAgent,
language: navigator.language,
platform: navigator.platform,
screen: `${screen.width}x${screen.height}`,
timezone: new Date().getTimezoneOffset(),
plugins: Array.from(navigator.plugins)
.map((p) => p.name)
.join(","),
canvas: getCanvasFingerprint(),
};

// 生成唯一 ID
const str = JSON.stringify(fingerprint);
return md5(str);
}

function getCanvasFingerprint() {
const canvas = document.createElement("canvas");
const ctx = canvas.getContext("2d");
ctx.textBaseline = "top";
ctx.font = "14px Arial";
ctx.fillText("Device Fingerprint", 2, 2);
return canvas.toDataURL();
}
```

#### 4. Python 完整实现

```python
import requests
import hashlib
import time
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import base64

class BankLogin:
def __init__(self):
self.session = requests.Session()
self.public_key = None

def get_public_key(self):
"""获取 RSA 公钥"""
response = self.session.get('https://bank.example.com/api/public-key')
self.public_key = response.json()['public_key']
return self.public_key

def encrypt_password(self, password):
"""RSA 加密密码"""
key = RSA.import_key(self.public_key)
cipher = PKCS1_v1_5.new(key)
encrypted = cipher.encrypt(password.encode())
return base64.b64encode(encrypted).decode()

def generate_device_id(self):
"""生成设备指纹"""
fingerprint = {
'userAgent': 'Mozilla/5.0...',
'language': 'zh-CN',
'platform': 'Linux x86_64',
'screen': '1920x1080',
'timezone': -480
}
fp_str = str(fingerprint)
return hashlib.md5(fp_str.encode()).hexdigest()

def generate_sign(self, params):
"""生成签名"""
sorted_params = sorted(params.items())
sign_str = '&'.join([f"{k}={v}" for k, v in sorted_params])
sign_str += '&key=SECRET_KEY_2023'
return hashlib.md5(sign_str.encode()).hexdigest()

def login(self, username, password):
"""登录流程"""
# 1. 获取公钥
self.get_public_key()

# 2. 加密密码
password_enc = self.encrypt_password(password)

# 3. 准备参数
timestamp = int(time.time())
params = {
'username': username,
'password_enc': password_enc,
'device_id': self.generate_device_id(),
'timestamp': timestamp
}

# 4. 生成签名
params['sign'] = self.generate_sign(params)

# 5. 发送登录请求
response = self.session.post(
'https://bank.example.com/api/login',
json=params
)

return response.json()

def verify_sms(self, code):
"""验证短信验证码"""
response = self.session.post(
'https://bank.example.com/api/verify-sms',
json={'code': code}
)
return response.json()

# 使用
bank = BankLogin()
result = bank.login('user123', 'password123')
print(result)

# 输入短信验证码
sms_code = input('请输入短信验证码: ')
verify_result = bank.verify_sms(sms_code)
print('Token:', verify_result['token'])
```

---

## 案例三：交易订单签名防篡改

### 背景

股票交易下单接口需要对订单参数进行签名，防止参数被篡改：

```http
POST /api/trade/order HTTP/1.1

{
"stock_code": "600000",
"action": "buy",
"price": 13.56,
"quantity": 1000,
"timestamp": 1702800000,
"nonce": "abc123",
"signature": "1a2b3c4d..."
}
```

---

### 逆向分析

#### 1. 定位签名生成函数

在下单按钮上设置断点，追踪调用栈：

```javascript
function generateOrderSignature(orderData) {
// 1. 参数排序
const keys = Object.keys(orderData).sort();

// 2. 拼接字符串
let signStr = "";
keys.forEach((key) => {
if (key !== "signature") {
signStr += `${key}=${orderData[key]}&`;
}
});

// 3. 添加私钥（从 localStorage 获取）
const privateKey = localStorage.getItem("user_private_key");
signStr += `key=${privateKey}`;

// 4. SHA256 签名
return CryptoJS.SHA256(signStr).toString();
}
```

#### 2. 私钥获取

私钥在登录成功后存储：

```javascript
// 登录响应
{
"token": "eyJhbGciOiJIUzI1NiIs...",
"private_key": "sk_live_1234567890abcdef" // 用户私钥
}

// 存储到 localStorage
localStorage.setItem('user_private_key', data.private_key);
```

#### 3. Python 实现

```python
import hashlib
import time
import uuid

def generate_order_signature(order_data, private_key):
# 移除 signature 字段
params = {k: v for k, v in order_data.items() if k != 'signature'}

# 参数排序
sorted_params = sorted(params.items())

# 拼接字符串
sign_str = '&'.join([f"{k}={v}" for k, v in sorted_params])
sign_str += f'&key={private_key}'

# SHA256
return hashlib.sha256(sign_str.encode()).hexdigest()

# 下单
order_data = {
'stock_code': '600000',
'action': 'buy',
'price': 13.56,
'quantity': 1000,
'timestamp': int(time.time()),
'nonce': str(uuid.uuid4())
}

# 生成签名
private_key = 'sk_live_1234567890abcdef' # 从登录响应获取
order_data['signature'] = generate_order_signature(order_data, private_key)

# 发送订单
response = requests.post(
'https://stock.example.com/api/trade/order',
json=order_data,
headers={'Authorization': f'Bearer {token}'}
)
```

---

## 案例四：反自动化交易检测

### 背景

金融平台会检测自动化交易行为：

- 鼠标轨迹分析
- 操作时间间隔
- 键盘输入模式
- WebGL 指纹
- 浏览器特征

---

### 检测机制分析

#### 1. 鼠标轨迹收集

```javascript
// 平台收集鼠标移动轨迹
let mouseTrack = [];
document.addEventListener("mousemove", function (e) {
mouseTrack.push({
x: e.clientX,
y: e.clientY,
timestamp: Date.now(),
});
});

// 提交订单时一起发送
function submitOrder(orderData) {
const payload = {
...orderData,
mouse_track: mouseTrack,
behavior_score: calculateBehaviorScore(mouseTrack),
};

return fetch("/api/trade/order", {
method: "POST",
body: JSON.stringify(payload),
});
}

function calculateBehaviorScore(track) {
// 分析鼠标轨迹是否自然
// 真人：曲线、有抖动、速度变化
// 机器：直线、匀速

let smoothness = 0;
for (let i = 1; i < track.length; i++) {
const dx = track[i].x - track[i - 1].x;
const dy = track[i].y - track[i - 1].y;
const distance = Math.sqrt(dx * dx + dy * dy);
const time = track[i].timestamp - track[i - 1].timestamp;
const speed = distance / time;

// 速度变化越大，越像真人
smoothness += Math.abs(speed - (previousSpeed || speed));
previousSpeed = speed;
}

return smoothness > 100 ? 1 : 0; // 1=真人，0=可疑
}
```

#### 2. 绕过策略

**使用 Selenium 模拟真实行为**:

```python
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time
import random
import numpy as np

def generate_bezier_curve(start, end, control_points=2):
"""生成贝塞尔曲线路径（模拟真实鼠标移动）"""
# 随机生成控制点
points = [start]
for _ in range(control_points):
points.append((
random.randint(min(start[0], end[0]), max(start[0], end[0])),
random.randint(min(start[1], end[1]), max(start[1], end[1]))
))
points.append(end)

# 贝塞尔曲线插值
path = []
for t in np.linspace(0, 1, 50):
x = sum([(1-t)**(len(points)-1-i) * t**i * p[0] * np.math.comb(len(points)-1, i)
for i, p in enumerate(points)])
y = sum([(1-t)**(len(points)-1-i) * t**i * p[1] * np.math.comb(len(points)-1, i)
for i, p in enumerate(points)])
path.append((int(x), int(y)))

return path

def human_like_click(driver, element):
"""模拟真人点击"""
# 1. 移动到元素附近
location = element.location
size = element.size

# 随机偏移
target_x = location['x'] + random.randint(5, size['width'] - 5)
target_y = location['y'] + random.randint(5, size['height'] - 5)

# 生成曲线路径
current_pos = (random.randint(0, 800), random.randint(0, 600))
path = generate_bezier_curve(current_pos, (target_x, target_y))

# 2. 沿曲线移动
actions = ActionChains(driver)
for x, y in path:
actions.move_by_offset(x - current_pos[0], y - current_pos[1])
actions.pause(random.uniform(0.001, 0.005)) # 随机延迟
current_pos = (x, y)

# 3. 点击前停顿
actions.pause(random.uniform(0.1, 0.3))

# 4. 点击
actions.click()
actions.perform()

# 5. 点击后停顿
time.sleep(random.uniform(0.5, 1.5))

# 使用
driver = webdriver.Chrome()
driver.get('https://stock.example.com/trade')

buy_button = driver.find_element_by_id('buy-button')
human_like_click(driver, buy_button)
```

---

## 案例五：实时风控系统绕过

### 背景

平台有实时风控系统，监控异常行为：

- 同一 IP 短时间多次登录
- 异常交易模式
- 设备指纹变化
- 地理位置跳变

---

### 绕过策略

#### 1. 使用代理池

```python
import requests
from itertools import cycle

class ProxyRotator:
def __init__(self, proxy_list):
self.proxy_pool = cycle(proxy_list)

def get_session(self):
proxy = next(self.proxy_pool)
session = requests.Session()
session.proxies = {
'http': proxy,
'https': proxy
}
return session

# 使用
proxies = [
'http://proxy1.com:8080',
'http://proxy2.com:8080',
'http://proxy3.com:8080'
]

rotator = ProxyRotator(proxies)

for i in range(10):
session = rotator.get_session()
response = session.get('https://stock.example.com/api/market-data')
print(f'Request {i}: {response.status_code}')
time.sleep(random.uniform(2, 5)) # 随机延迟
```

#### 2. 保持设备指纹一致性

```python
class ConsistentBrowser:
def __init__(self):
self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)...'
self.headers = {
'User-Agent': self.user_agent,
'Accept-Language': 'zh-CN,zh;q=0.9',
'Accept-Encoding': 'gzip, deflate, br',
}
self.device_id = self.generate_device_id()

def generate_device_id(self):
# 生成一次后保持不变
fingerprint = {
'userAgent': self.user_agent,
'screen': '1920x1080',
'timezone': -480
}
return hashlib.md5(str(fingerprint).encode()).hexdigest()

def request(self, url):
headers = self.headers.copy()
headers['X-Device-Id'] = self.device_id

return requests.get(url, headers=headers)
```

---

## 安全建议

### 对于金融平台

1. **多层加密**

- 传输层: TLS 1.3
- 应用层: RSA + AES
- 数据库: 字段级加密

2. **动态防护**

- 每次登录更新公钥
- Token 短期有效（15 分钟）
- 签名盐值定期轮换

3. **行为分析**

- 机器学习检测异常
- 多维度指纹识别
- 实时风控规则引擎

4. **审计日志**
- 记录所有敏感操作
- 异常告警
- 可追溯性

### 对于研究人员

1. **合法合规**

- 仅在授权范围内研究
- 不进行实际交易测试
- 负责任披露漏洞

2. **测试环境**
- 使用演示账户
- 沙箱环境
- 不涉及真实资金

---

## 相关章节

- [加密算法逆向](../02-Techniques/crypto_reverse_engineering.md)
- [设备指纹识别](../03-Advanced-Topics/device_fingerprinting.md)
- [WebSocket 通信分析](../02-Techniques/websocket_analysis.md)
- [行为检测绕过](../02-Techniques/behavior_detection_bypass.md)
