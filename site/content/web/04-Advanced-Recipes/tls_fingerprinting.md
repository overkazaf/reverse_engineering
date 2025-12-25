---
title: "TLS 指纹识别 (JA3/JA4)"
date: 2025-07-08
type: posts
tags: ["Web", "浏览器指纹", "代理池", "WebAssembly", "SSL Pinning", "加密分析"]
weight: 10
---

# TLS 指纹识别 (JA3/JA4)

## 思考时刻

在学习 TLS 指纹之前，先挑战你的认知：

1. **HTTPS 就安全了吗？** 即使用了加密传输，网站还能识别出你是爬虫？
2. **握手的秘密：** 在 HTTPS 连接建立的一瞬间，浏览器暴露了哪些信息？
3. **指纹的不可见性：** 你用 Python requests 发请求，HTTP 头伪装得再像，为什么还是被识别出来？
4. **实战场景：** 某网站封禁了所有 Python requests 的访问（返回 403），但用浏览器访问正常。你连一个请求都没发，它是怎么知道的？

TLS 指纹，是应用层之下的"暗战"。

---

## 📚 前置知识

在开始本配方之前，建议先掌握以下内容：

| 知识领域 | 重要程度 | 参考资料 |
|----------|---------|---------|
| TLS/SSL 握手 | 必需 | [TLS/SSL 握手](../01-Foundations/tls_ssl_handshake.md) |
| HTTP/HTTPS 协议 | 必需 | [HTTP/HTTPS 协议](../01-Foundations/http_https_protocol.md) |
| Wireshark 使用 | 必需 | [Wireshark 指南](../02-Tooling/wireshark_guide.md) |
| 浏览器指纹识别 | 推荐 | [浏览器指纹识别](./browser_fingerprinting.md) |

> ⚠️ **重要提示**: TLS 指纹是**应用层之下**的检测手段，无法通过修改 HTTP 头来伪装。如果你的爬虫被 TLS 指纹识别封禁，需要使用特殊的网络库或浏览器自动化方案。

---

## 概述

TLS 握手过程中，客户端会发送一系列参数（如支持的加密套件、扩展等），这些参数的组合可以作为指纹识别客户端类型。JA3/JA4 是目前最流行的 TLS 指纹技术。

---

## TLS 握手回顾

```
Client -----> ClientHello (包含加密套件、扩展等) -----> Server
Client <----- ServerHello (选择加密套件) <----- Server
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
const puppeteer = require("puppeteer");

(async () => {
const browser = await puppeteer.launch();
const page = await browser.newPage();
await page.goto("https://example.com");
const content = await page.content();
console.log(content);
await browser.close();
})();
```

---

## JA4 - 下一代指纹

### 与 JA3 的区别

| 特性 | JA3 | JA4 |
| ------------ | ----------- | ----------------- |
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
print(response.json()) # 查看 JA3
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
print(response.text) # 成功！
```

---

## 相关资源

- [JA3 - Salesforce](https://github.com/salesforce/ja3)
- [JA4+ Network Fingerprinting](https://github.com/FoxIO-LLC/ja4)
- [curl-impersonate](https://github.com/lwthiker/curl-impersonate)

---

## 相关章节

- [浏览器指纹识别](../04-Advanced-Recipes/browser_fingerprinting.md)
- [HTTP/2 与 HTTP/3](./http2_http3.md)
- [反爬虫技术深度分析](./anti_scraping_deep_dive.md)
