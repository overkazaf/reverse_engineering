---
title: "电商网站逆向案例"
weight: 10
---

# 电商网站逆向案例

## 概述

电商网站通常具有复杂的反爬虫机制，包括 API 签名、加密价格、滑块验证码等。本文通过实际案例介绍电商网站的逆向思路。

---

## 案例一：商品价格加密

### 背景

某电商网站的商品列表页，价格字段返回的是加密字符串：

```json
{
"product_id": 12345,
"name": "iPhone 15",
"price_enc": "U2FsdGVkX19Qx7..."
}
```

浏览器能正常显示价格，说明前端有解密逻辑。

---

### 逆向步骤

#### 1. 定位解密函数

**方法一：搜索关键词**

```javascript
// 在 Sources 面板搜索
"price_enc";
"decrypt";
"AES";
```

**方法二：DOM 断点**

1. 右键价格元素 -> Inspect
2. 右键 DOM 节点 -> Break on -> subtree modifications
3. 刷新页面，断点会停在修改价格的代码处

#### 2. 分析加密算法

断点停下后，观察 Call Stack：

```
updatePrice()
|- decryptPrice(encryptedPrice)
|- CryptoJS.AES.decrypt(enc, key, {iv: iv})
```

发现使用了 **AES-CBC** 加密，Key 和 IV 都在 JS 中硬编码：

```javascript
function decryptPrice(enc) {
var key = CryptoJS.enc.Utf8.parse("1234567890abcdef");
var iv = CryptoJS.enc.Utf8.parse("abcdefghijklmnop");
var decrypted = CryptoJS.AES.decrypt(enc, key, {
iv: iv,
mode: CryptoJS.mode.CBC,
padding: CryptoJS.pad.Pkcs7,
});
return decrypted.toString(CryptoJS.enc.Utf8);
}
```

#### 3. Python 实现

```python
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64

def decrypt_price(price_enc):
key = b'1234567890abcdef'
iv = b'abcdefghijklmnop'

cipher = AES.new(key, AES.MODE_CBC, iv)
encrypted_data = base64.b64decode(price_enc)
decrypted = unpad(cipher.decrypt(encrypted_data), AES.block_size)

return decrypted.decode('utf-8')

# 测试
price_enc = "U2FsdGVkX19Qx7..."
print(decrypt_price(price_enc)) # "￥5999"
```

---

## 案例二：API 签名逆向

### 背景

商品搜索接口需要签名参数：

```
GET /api/search?q=iPhone&page=1&sign=abc123&timestamp=1234567890
```

不带 `sign` 或签名错误都会返回 403。

---

### 逆向步骤

#### 1. 定位签名生成

**XHR 断点**:

1. Sources -> XHR/fetch breakpoints
2. 输入 `/api/search`
3. 刷新页面，断点会在请求发送前停下

#### 2. 分析签名逻辑

在 Call Stack 中追踪，发现签名生成函数：

```javascript
function generateSign(params) {
// 1. 参数排序
var keys = Object.keys(params).sort();

// 2. 拼接字符串
var str = keys.map((k) => k + "=" + params[k]).join("&");

// 3. 加盐
str += "&key=my_secret_key_2023";

// 4. MD5
return md5(str);
}
```

**验证**:

```javascript
generateSign({ q: "iPhone", page: 1, timestamp: 1234567890 });
// "e10adc3949ba59abbe56e057f20f883e"
```

#### 3. Python 实现

```python
import hashlib
import time

def generate_sign(params):
# 参数排序
sorted_params = sorted(params.items())

# 拼接
param_str = '&'.join([f"{k}={v}" for k, v in sorted_params])

# 加盐
sign_str = param_str + '&key=my_secret_key_2023'

# MD5
return hashlib.md5(sign_str.encode()).hexdigest()

# 使用
params = {
'q': 'iPhone',
'page': 1,
'timestamp': int(time.time())
}
params['sign'] = generate_sign(params)

# 发送请求
import requests
response = requests.get('https://example.com/api/search', params=params)
print(response.json())
```

---

## 案例三：滑块验证码

### 背景

登录时出现滑块验证码，需要拖动滑块到指定位置。

---

### 逆向思路

#### 1. 轨迹生成

真实用户拖动滑块时，轨迹是不规则的（有加速、减速、抖动）。

**简单的线性轨迹**:

```python
def generate_track(distance):
track = []
current = 0
while current < distance:
step = min(5, distance - current) # 每次移动 5px
track.append(step)
current += step
return track
```

**模拟真实轨迹** (更高级):

```python
import random

def generate_realistic_track(distance):
track = []
current = 0
mid = distance * 0.8 # 80% 处开始减速

while current < distance:
if current < mid:
# 加速阶段
step = random.randint(5, 10)
else:
# 减速阶段
step = random.randint(2, 5)

if current + step > distance:
step = distance - current

track.append(step)
current += step

# 随机抖动
if random.random() < 0.2:
track.append(-random.randint(1, 2))
current -= track[-1]

return track
```

#### 2. Selenium 模拟

```python
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import time

driver = webdriver.Chrome()
driver.get('https://example.com/login')

# 等待滑块加载
slider = driver.find_element(By.CLASS_NAME, 'slider-button')

# 生成轨迹
distance = 260 # 需要移动的距离（像素）
track = generate_realistic_track(distance)

# 执行拖动
ActionChains(driver).click_and_hold(slider).perform()
for step in track:
ActionChains(driver).move_by_offset(step, 0).perform()
time.sleep(random.uniform(0.001, 0.003)) # 模拟人类延迟

ActionChains(driver).release().perform()
```

---

## 案例四：限流与反爬

### 背景

频繁请求会触发限流：

- 单 IP 每分钟最多 60 次请求
- 超过后返回 429 Too Many Requests

---

### 绕过策略

#### 1. 降低请求频率

```python
import time

for page in range(1, 100):
response = requests.get(f'https://example.com/api/products?page={page}')
print(response.json())

# 休眠 1-3 秒
time.sleep(random.uniform(1, 3))
```

#### 2. 使用代理池

```python
proxies_list = [
{'http': 'http://proxy1:port'},
{'http': 'http://proxy2:port'},
# ...
]

for page in range(1, 100):
proxy = random.choice(proxies_list)
response = requests.get(
f'https://example.com/api/products?page={page}',
proxies=proxy
)
```

#### 3. 分布式爬取

使用 Scrapy + Redis 实现分布式：

- 多台服务器同时爬取
- Redis 存储任务队列和去重
- 每台服务器独立 IP

---

## 总结

电商网站逆向的核心挑战：

1. **加密算法**: 价格、库存等敏感数据加密
2. **API 签名**: 防止参数篡改
3. **验证码**: 滑块、点选、行为验证
4. **限流**: IP 封禁、频率限制

**应对策略**:

- 静态分析 + 动态调试定位加密逻辑
- Hook 关键函数验证算法
- 使用代理池、降低频率避免封禁
- Selenium/Puppeteer 应对复杂验证码

---

## 相关章节

- [API 接口逆向](../03-Basic-Recipes/api_reverse_engineering.md)
- [JavaScript 反混淆](../04-Advanced-Recipes/javascript_deobfuscation.md)
- [验证码识别与绕过](../04-Advanced-Recipes/captcha_bypass.md)
- [代理池管理](../06-Engineering/proxy_pool_management.md)
