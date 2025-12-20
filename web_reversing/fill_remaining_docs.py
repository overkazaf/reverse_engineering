#!/usr/bin/env python3
"""
批量填充 Web 逆向工程所有剩余文档
"""

import os
from pathlib import Path

# 所有文档内容
ALL_DOCS = {}

# 03-Advanced-Topics 模块
ALL_DOCS["03-Advanced-Topics/canvas_fingerprinting.md"] = """# Canvas 指纹技术

## 概述

Canvas Fingerprinting 是一种通过 HTML5 Canvas API 生成浏览器指纹的技术。由于不同系统、浏览器、显卡渲染文本和图形时存在细微差异，这些差异可以用来唯一标识用户。

---

## 原理

### 1. 渲染差异来源

**硬件层面**:
- GPU 型号和驱动版本
- 操作系统（Windows/Mac/Linux）
- 字体渲染引擎（DirectWrite/CoreText/FreeType）

**软件层面**:
- 浏览器类型和版本
- 已安装的字体
- 图像压缩算法

### 2. 生成流程

```javascript
// 1. 创建 Canvas
const canvas = document.createElement('canvas');
const ctx = canvas.getContext('2d');

// 2. 绘制特定内容
ctx.textBaseline = 'top';
ctx.font = '14px Arial';
ctx.textBaseline = 'alphabetic';
ctx.fillStyle = '#f60';
ctx.fillRect(125, 1, 62, 20);
ctx.fillStyle = '#069';
ctx.fillText('Hello, world!', 2, 15);
ctx.fillStyle = 'rgba(102, 204, 0, 0.7)';
ctx.fillText('Hello, world!', 4, 17);

// 3. 导出为图像数据
const dataURL = canvas.toDataURL();

// 4. 计算哈希作为指纹
const fingerprint = md5(dataURL);
```

**关键点**: 即使绘制相同的内容，不同环境渲染出的像素值会有微小差异。

---

## 检测 Canvas 指纹

### 方法一：监控 API 调用

```javascript
// Hook toDataURL
const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
HTMLCanvasElement.prototype.toDataURL = function() {
    console.log('[Canvas] toDataURL called');
    console.trace();
    return originalToDataURL.apply(this, arguments);
};

// Hook getImageData
const originalGetImageData = CanvasRenderingContext2D.prototype.getImageData;
CanvasRenderingContext2D.prototype.getImageData = function() {
    console.log('[Canvas] getImageData called');
    console.trace();
    return originalGetImageData.apply(this, arguments);
};
```

### 方法二：在 DevTools 中查找

全局搜索关键词：
- `toDataURL`
- `getImageData`
- `canvas`
- `fingerprint`

---

## 对抗技术

### 1. 禁用 Canvas（极端方案）

某些隐私浏览器（如 Tor Browser）会禁用或限制 Canvas。

**问题**: 会导致网站功能异常。

### 2. Canvas Spoofing（伪造）

**原理**: 修改 Canvas API 返回值，给每个请求返回稍微不同的数据。

```javascript
// 简单的随机噪点注入
const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
HTMLCanvasElement.prototype.toDataURL = function(...args) {
    // 获取原始数据
    const dataURL = originalToDataURL.apply(this, arguments);

    // 注入噪点（修改少量像素）
    const canvas = this;
    const ctx = canvas.getContext('2d');
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const data = imageData.data;

    // 随机修改 0.01% 的像素
    for (let i = 0; i < data.length; i += 4) {
        if (Math.random() < 0.0001) {
            data[i] = Math.floor(Math.random() * 256);  // R
            data[i+1] = Math.floor(Math.random() * 256);  // G
            data[i+2] = Math.floor(Math.random() * 256);  // B
        }
    }

    ctx.putImageData(imageData, 0, 0);
    return canvas.toDataURL();
};
```

**浏览器插件**:
- **Canvas Fingerprint Defender**
- **Canvas Blocker**

### 3. 使用无头浏览器

Puppeteer/Selenium 可以通过注入脚本修改 Canvas 行为：

```javascript
// Puppeteer
await page.evaluateOnNewDocument(() => {
    const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
    HTMLCanvasElement.prototype.toDataURL = function(...args) {
        // 注入噪点逻辑
        // ...
        return originalToDataURL.apply(this, arguments);
    };
});
```

---

## 检测反爬虫中的 Canvas 指纹

### 案例：某电商网站

**现象**: 登录后立即被封号，提示"检测到异常行为"。

**分析**:
1. 在 Console Hook `toDataURL` 和 `getImageData`
2. 发现页面加载时调用了多次 Canvas API
3. 定位到 JS 文件，发现在生成设备指纹

**绕过**:
- 使用真实浏览器（Chrome）而非 Headless
- 安装 Canvas Defender 插件
- 或使用指纹伪造库（如 FingerprintJS Spoofing）

---

## Canvas vs WebGL 指纹

| 特性 | Canvas | WebGL |
|------|--------|-------|
| **原理** | 2D 图形渲染差异 | 3D 图形渲染差异 |
| **区分度** | 中 | 高 |
| **实现难度** | 低 | 中 |
| **常见场景** | 通用指纹 | 高级指纹 |

---

## 相关资源

- [BrowserLeaks - Canvas Test](https://browserleaks.com/canvas)
- [AmIUnique - 指纹测试](https://amiunique.org/)

---

## 相关章节

- [浏览器指纹识别](../02-Techniques/browser_fingerprinting.md)
- [WebRTC 指纹与隐私](./webrtc_fingerprinting.md)
- [反爬虫技术深度分析](./anti_scraping_deep_dive.md)
"""

ALL_DOCS["03-Advanced-Topics/tls_fingerprinting.md"] = """# TLS 指纹识别 (JA3/JA4)

## 概述

TLS 握手过程中，客户端会发送一系列参数（如支持的加密套件、扩展等），这些参数的组合可以作为指纹识别客户端类型。JA3/JA4 是目前最流行的 TLS 指纹技术。

---

## TLS 握手回顾

```
Client -----> ClientHello (包含加密套件、扩展等) -----> Server
Client <----- ServerHello (选择加密套件)        <----- Server
...
```

**ClientHello 包含的信息**:
- TLS 版本
- 支持的加密套件列表
- 支持的压缩方法
- 扩展（Extension）列表

---

## JA3 指纹

### 1. 原理

JA3 将 ClientHello 中的关键字段拼接成字符串，然后计算 MD5。

**字段**:
```
TLS版本, 加密套件列表, 扩展列表, 椭圆曲线列表, 椭圆曲线点格式
```

**示例**:
```
771,49195-49199-49196-49200-52393-52392-49171-49172-156-157-47-53,0-5-10-11-13-65281,23-24-25,0
```

计算 MD5:
```
JA3 = md5("771,49195-49199-...")
    = "3b5074b1b5d032e5620f69f9f700ff0e"
```

### 2. 用途

**服务器端**:
- 识别客户端类型（浏览器 vs 脚本）
- 封禁特定客户端（如 Python requests 的 JA3）

**攻击者**:
- 伪造浏览器的 TLS 指纹

---

## JA3 检测

### 在线工具

- [tls.peet.ws](https://tls.peet.ws/api/clean) - 查看自己的 JA3
- [JA3er](https://ja3er.com/) - JA3 数据库

### Wireshark 抓包

1. 捕获 HTTPS 流量
2. 过滤 `ssl.handshake.type == 1` (ClientHello)
3. 查看 `Cipher Suites` 和 `Extensions`

---

## JA3 伪造

### 方法一：使用支持 TLS 指纹的库

**Python - curl_cffi**:
```python
from curl_cffi import requests

# 模拟 Chrome
response = requests.get('https://tls.peet.ws/api/clean', impersonate='chrome110')
print(response.text)
```

**Go - utls**:
```go
import "github.com/refraction-networking/utls"

config := &utls.Config{
    ServerName: "example.com",
}
conn := utls.UClient(tcpConn, config, utls.HelloChrome_Auto)
```

### 方法二：使用真实浏览器（RPC）

通过 Puppeteer/Playwright 控制真实浏览器，天然具有正确的 TLS 指纹。

```javascript
const puppeteer = require('puppeteer');

(async () => {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    await page.goto('https://example.com');
    const content = await page.content();
    console.log(content);
    await browser.close();
})();
```

---

## JA4 - 下一代指纹

### 与 JA3 的区别

| 特性 | JA3 | JA4 |
|------|-----|-----|
| **格式** | MD5 哈希 | 人类可读字符串 |
| **协议支持** | TLS 1.0-1.3 | TLS 1.0-1.3, QUIC |
| **细粒度** | 中 | 高 |
| **可读性** | 低（哈希） | 高（分段字符串） |

**JA4 示例**:
```
t13d1516h2_8daaf6152771_e5627efa2ab1
```

- `t13`: TLS 1.3
- `d15`: 加密套件数量
- `16`: 扩展数量
- `h2`: ALPN (HTTP/2)

---

## 绕过 TLS 指纹检测

### 1. 使用模拟库

选择支持自定义 TLS 指纹的 HTTP 库：
- `curl_cffi` (Python)
- `utls` (Go)
- `tls-client` (Python wrapper for Go utls)

### 2. 频繁更换指纹

即使被识别，也可以轮换不同的浏览器指纹（Chrome/Firefox/Safari）。

### 3. 使用住宅代理

高质量住宅代理通常会保留真实用户的 TLS 特征。

---

## 检测网站是否使用 TLS 指纹

**方法**:
1. 用 `requests` 库和真实浏览器分别访问同一接口
2. 如果 `requests` 返回 403/401，浏览器正常，可能是 TLS 指纹检测

**验证**:
```python
import requests

# Python requests 的 TLS 指纹
response = requests.get('https://tls.peet.ws/api/clean')
print(response.json())  # 查看 JA3
```

对比浏览器访问 `https://tls.peet.ws/api/clean` 的结果。

---

## 实战案例

### 案例：某社交媒体 API

**现象**: Python requests 请求返回 403，浏览器正常。

**分析**:
1. 检查 User-Agent - 已伪造，仍然失败
2. 检查 Cookie - 已携带，仍然失败
3. 怀疑 TLS 指纹

**解决**:
```python
from curl_cffi import requests

# 使用 curl_cffi 模拟 Chrome 的 TLS 指纹
response = requests.get(
    'https://api.socialmedia.com/user/info',
    headers={'User-Agent': 'Mozilla/5.0 ...'},
    cookies={'session': 'xxx'},
    impersonate='chrome110'
)
print(response.text)  # 成功！
```

---

## 相关资源

- [JA3 - Salesforce](https://github.com/salesforce/ja3)
- [JA4+ Network Fingerprinting](https://github.com/FoxIO-LLC/ja4)
- [curl-impersonate](https://github.com/lwthiker/curl-impersonate)

---

## 相关章节

- [浏览器指纹识别](../02-Techniques/browser_fingerprinting.md)
- [HTTP/2 与 HTTP/3](./http2_http3.md)
- [反爬虫技术深度分析](./anti_scraping_deep_dive.md)
"""

ALL_DOCS["05-Case-Studies/case_ecommerce.md"] = """# 电商网站逆向案例

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
"price_enc"
"decrypt"
"AES"
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
        padding: CryptoJS.pad.Pkcs7
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
print(decrypt_price(price_enc))  # "￥5999"
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
    var str = keys.map(k => k + '=' + params[k]).join('&');

    // 3. 加盐
    str += '&key=my_secret_key_2023';

    // 4. MD5
    return md5(str);
}
```

**验证**:
```javascript
generateSign({q: 'iPhone', page: 1, timestamp: 1234567890})
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
        step = min(5, distance - current)  # 每次移动 5px
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
    mid = distance * 0.8  # 80% 处开始减速

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
distance = 260  # 需要移动的距离（像素）
track = generate_realistic_track(distance)

# 执行拖动
ActionChains(driver).click_and_hold(slider).perform()
for step in track:
    ActionChains(driver).move_by_offset(step, 0).perform()
    time.sleep(random.uniform(0.001, 0.003))  # 模拟人类延迟

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

- [API 接口逆向](../02-Techniques/api_reverse_engineering.md)
- [JavaScript 反混淆](../02-Techniques/javascript_deobfuscation.md)
- [验证码识别与绕过](../02-Techniques/captcha_bypass.md)
- [代理池管理](../04-Engineering/proxy_pool_management.md)
"""

# 批量写入所有文档
def fill_all_documents():
    base_dir = Path(__file__).parent / "docs"

    count = 0
    for file_path, content in ALL_DOCS.items():
        full_path = base_dir / file_path

        # 确保目录存在
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # 写入文件
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)

        count += 1
        print(f"✅ [{count}/{len(ALL_DOCS)}] 已填充: {file_path}")

    print(f"\n🎉 成功填充 {count} 个文档!")
    print("\n剩余需要手动填充的文档可以通过以下命令查看:")
    print("grep -l 'TODO: 添加' docs/*/*.md")

if __name__ == "__main__":
    fill_all_documents()
