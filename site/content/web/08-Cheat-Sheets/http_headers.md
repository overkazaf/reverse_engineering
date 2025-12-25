---
title: "HTTP 头速查表"
date: 2025-05-14
tags: ["Web", "签名验证", "代理池", "速查表", "视频App", "参考"]
weight: 10
---

# HTTP 头速查表

## 常见请求头 (Request Headers)

| Header | 说明 | 示例 |
| --------------------- | ----------------- | ---------------------------------------------- |
| **User-Agent** | 客户端信息 | `Mozilla/5.0 (Windows NT 10.0; Win64; x64)...` |
| **Accept** | 可接受的内容类型 | `application/json, text/plain, */*` |
| **Accept-Language** | 可接受的语言 | `zh-CN,zh;q=0.9,en;q=0.8` |
| **Accept-Encoding** | 可接受的编码 | `gzip, deflate, br` |
| **Content-Type** | 请求体内容类型 | `application/json; charset=UTF-8` |
| **Content-Length** | 请求体长度 | `1234` |
| **Authorization** | 认证信息 | `Bearer eyJhbGciOiJIUzI1NiIs...` |
| **Cookie** | Cookie 数据 | `session_id=abc123; user=admin` |
| **Referer** | 来源页面 | `https://example.com/page1` |
| **Origin** | 请求来源 | `https://example.com` |
| **Host** | 目标主机 | `api.example.com` |
| **Connection** | 连接方式 | `keep-alive` |
| **Cache-Control** | 缓存控制 | `no-cache, no-store` |
| **Pragma** | HTTP/1.0 缓存控制 | `no-cache` |
| **If-Modified-Since** | 条件请求 | `Wed, 21 Oct 2025 07:28:00 GMT` |
| **If-None-Match** | ETag 条件请求 | `"686897696a7c876b7e"` |
| **Range** | 范围请求 | `bytes=0-1024` |
| **X-Requested-With** | 标识 AJAX 请求 | `XMLHttpRequest` |
| **X-CSRF-Token** | CSRF 令牌 | `abc123def456` |

## 常见响应头 (Response Headers)

| Header | 说明 | 示例 |
| -------------------------------- | ------------- | ------------------------------------- |
| **Content-Type** | 响应内容类型 | `application/json; charset=utf-8` |
| **Content-Length** | 响应体长度 | `1234` |
| **Content-Encoding** | 响应编码 | `gzip` |
| **Set-Cookie** | 设置 Cookie | `session_id=abc123; Path=/; HttpOnly` |
| **Cache-Control** | 缓存策略 | `max-age=3600, must-revalidate` |
| **Expires** | 过期时间 | `Wed, 21 Oct 2025 07:28:00 GMT` |
| **ETag** | 资源标识 | `"686897696a7c876b7e"` |
| **Last-Modified** | 最后修改时间 | `Wed, 21 Oct 2025 07:28:00 GMT` |
| **Location** | 重定向地址 | `https://example.com/new-page` |
| **Server** | 服务器信息 | `nginx/1.18.0` |
| **X-Powered-By** | 技术栈 | `PHP/7.4.0` |
| **Access-Control-Allow-Origin** | CORS 允许来源 | `*` 或 `https://example.com` |
| **Access-Control-Allow-Methods** | CORS 允许方法 | `GET, POST, PUT, DELETE` |
| **Access-Control-Allow-Headers** | CORS 允许头 | `Content-Type, Authorization` |
| **Access-Control-Max-Age** | CORS 预检缓存 | `3600` |
| **Strict-Transport-Security** | HSTS | `max-age=31536000; includeSubDomains` |
| **X-Frame-Options** | 防点击劫持 | `DENY` |
| **X-Content-Type-Options** | 防 MIME 嗅探 | `nosniff` |
| **X-XSS-Protection** | XSS 过滤器 | `1; mode=block` |

## 安全相关头

### 请求安全头

```http
# CSRF 防护
X-CSRF-Token: abc123def456
X-XSRF-TOKEN: abc123def456

# 自定义签名
X-Signature: md5_hash_value
X-Sign: sha256_hash_value
X-Timestamp: 1702887654321

# API密钥
X-API-Key: your_api_key_here
API-Key: your_api_key_here
```

### 响应安全头

```http
# 内容安全策略
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'

# XSS 防护
X-XSS-Protection: 1; mode=block

# 防点击劫持
X-Frame-Options: SAMEORIGIN

# MIME 类型嗅探防护
X-Content-Type-Options: nosniff

# Referer 策略
Referrer-Policy: no-referrer-when-downgrade

# 权限策略
Permissions-Policy: geolocation=(), camera=()
```

## Content-Type 常见值

### 请求/响应通用

| Content-Type | 说明 | 用途 |
| ----------------------------------- | ---------- | ----------------- |
| `application/json` | JSON 数据 | API 请求/响应 |
| `application/x-www-form-urlencoded` | 表单数据 | 传统表单提交 |
| `multipart/form-data` | 文件上传 | 含文件的表单 |
| `text/html` | HTML 文档 | 网页 |
| `text/plain` | 纯文本 | 文本文件 |
| `text/css` | CSS 样式 | 样式表 |
| `text/javascript` | JavaScript | JS 文件 |
| `application/javascript` | JavaScript | JS 文件（新标准） |
| `application/xml` | XML 数据 | XML 格式 |
| `text/xml` | XML 文本 | XML 文本 |
| `application/octet-stream` | 二进制流 | 文件下载 |
| `image/jpeg` | JPEG 图片 | 图片 |
| `image/png` | PNG 图片 | 图片 |
| `image/gif` | GIF 图片 | 动图 |
| `image/svg+xml` | SVG 图片 | 矢量图 |
| `video/mp4` | MP4 视频 | 视频 |
| `audio/mpeg` | MP3 音频 | 音频 |

## 自定义头示例

### 常见的自定义业务头

```http
# 版本控制
X-API-Version: 1.0
X-Client-Version: 2.3.1

# 设备信息
X-Device-ID: 1234567890abcdef
X-Device-Type: mobile
X-Platform: ios
X-OS-Version: 14.5

# 追踪和调试
X-Request-ID: uuid-1234-5678
X-Trace-ID: trace_abc123
X-Debug: true

# 地理位置
X-Geo-Country: CN
X-Geo-City: Beijing
X-Client-IP: 1.2.3.4

# A/B测试
X-Experiment: variant_b
X-Feature-Flag: new_ui_enabled
```

## User-Agent 示例

### 桌面浏览器

```http
# Chrome (Windows)
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36

# Firefox (Windows)
Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0

# Edge (Windows)
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0

# Safari (macOS)
Mozilla/5.0 (Macintosh; Intel Mac OS X 14_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15
```

### 移动浏览器

```http
# iPhone Safari
Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1

# Android Chrome
Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36

# iPad Safari
Mozilla/5.0 (iPad; CPU OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1
```

### 爬虫/工具

```http
# Python Requests
python-requests/2.31.0

# Postman
PostmanRuntime/7.36.0

# cURL
curl/7.68.0
```

## Authorization 方式

### Bearer Token

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Basic Auth

```http
Authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ=
# (username:password 的 Base64编码)
```

### Digest Auth

```http
Authorization: Digest username="user", realm="example.com", nonce="abc123", uri="/api", response="def456"
```

### API Key

```http
Authorization: ApiKey your_api_key_here
# 或
X-API-Key: your_api_key_here
```

## Cookie 属性

```http
Set-Cookie: session_id=abc123; Domain=example.com; Path=/; Expires=Wed, 21 Oct 2025 07:28:00 GMT; Max-Age=3600; Secure; HttpOnly; SameSite=Strict
```

**属性说明**:

| 属性 | 说明 |
| ---------- | ------------------------------ |
| `Domain` | Cookie 的作用域 |
| `Path` | Cookie 的作用路径 |
| `Expires` | 过期时间（绝对时间） |
| `Max-Age` | 存活时间（秒） |
| `Secure` | 仅 HTTPS 传输 |
| `HttpOnly` | 禁止 JavaScript 访问 |
| `SameSite` | 跨站请求策略 (Strict/Lax/None) |

## Cache-Control 指令

### 请求指令

```http
Cache-Control: no-cache # 不使用缓存
Cache-Control: no-store # 不存储缓存
Cache-Control: max-age=0 # 立即过期
Cache-Control: max-stale=3600 # 可接受过期的缓存
Cache-Control: min-fresh=600 # 必须新鲜的缓存
Cache-Control: only-if-cached # 只使用缓存
```

### 响应指令

```http
Cache-Control: public # 可被任何缓存存储
Cache-Control: private # 只能被浏览器缓存
Cache-Control: no-cache # 需要验证
Cache-Control: no-store # 不能缓存
Cache-Control: max-age=3600 # 缓存3600秒
Cache-Control: s-maxage=3600 # 共享缓存时间
Cache-Control: must-revalidate # 过期后必须验证
Cache-Control: proxy-revalidate # 代理缓存需验证
Cache-Control: immutable # 不会改变
```

## Python 设置 Headers

```python
import requests

headers = {
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
'Accept': 'application/json',
'Accept-Language': 'zh-CN,zh;q=0.9',
'Accept-Encoding': 'gzip, deflate',
'Content-Type': 'application/json',
'Authorization': 'Bearer your_token_here',
'X-Requested-With': 'XMLHttpRequest',
'Referer': 'https://example.com',
'Origin': 'https://example.com'
}

response = requests.get('https://api.example.com/data', headers=headers)
```

## JavaScript 设置 Headers

```javascript
// Fetch API
fetch("https://api.example.com/data", {
method: "POST",
headers: {
"Content-Type": "application/json",
Authorization: "Bearer your_token_here",
"X-Custom-Header": "custom_value",
},
body: JSON.stringify({ key: "value" }),
});

// XHR
const xhr = new XMLHttpRequest();
xhr.open("POST", "https://api.example.com/data");
xhr.setRequestHeader("Content-Type", "application/json");
xhr.setRequestHeader("Authorization", "Bearer your_token_here");
xhr.send(JSON.stringify({ key: "value" }));
```

## cURL 设置 Headers

```bash
curl https://api.example.com/data \
-H "User-Agent: Mozilla/5.0..." \
-H "Accept: application/json" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer your_token_here" \
-H "X-Custom-Header: custom_value" \
-d '{"key":"value"}'
```

## 常见状态码对照

| 状态码 | 说明 |
| ------ | ---------------------------------- |
| 200 | OK - 成功 |
| 201 | Created - 已创建 |
| 204 | No Content - 无内容 |
| 301 | Moved Permanently - 永久重定向 |
| 302 | Found - 临时重定向 |
| 304 | Not Modified - 未修改（缓存有效） |
| 400 | Bad Request - 请求错误 |
| 401 | Unauthorized - 未授权 |
| 403 | Forbidden - 禁止访问 |
| 404 | Not Found - 未找到 |
| 405 | Method Not Allowed - 方法不允许 |
| 429 | Too Many Requests - 请求过多 |
| 500 | Internal Server Error - 服务器错误 |
| 502 | Bad Gateway - 网关错误 |
| 503 | Service Unavailable - 服务不可用 |

## 相关章节

- [HTTP/HTTPS 协议](../01-Foundations/http_https_protocol.md)
- [API 逆向](../03-Basic-Recipes/api_reverse_engineering.md)
- [常用命令](./common_commands.md)
