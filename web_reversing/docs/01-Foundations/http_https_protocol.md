# HTTP/HTTPS 协议

## 概述

HTTP (HyperText Transfer Protocol) 和 HTTPS (HTTP Secure) 是 Web 通信的基础协议。理解这些协议对于 Web 逆向工程至关重要。

---

## HTTP 基础

### 请求方法

常见的 HTTP 方法：

- **GET**: 请求指定的资源，参数在 URL 中
- **POST**: 向服务器提交数据，参数在请求体中
- **PUT**: 更新资源
- **DELETE**: 删除资源
- **HEAD**: 类似 GET，但只返回头部
- **OPTIONS**: 获取服务器支持的方法
- **PATCH**: 部分更新资源

### 请求结构

```http
GET /api/users?id=123 HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0
Accept: application/json
Cookie: session_id=abc123
```

**组成部分**：

1. 请求行：方法 + 路径 + 协议版本
2. 请求头：Key-Value 键值对
3. 空行
4. 请求体（可选）

### 响应结构

```http
HTTP/1.1 200 OK
Content-Type: application/json
Set-Cookie: token=xyz789
Content-Length: 42

{"status":"success","data":{"id":123}}
```

**组成部分**：

1. 状态行：协议版本 + 状态码 + 状态描述
2. 响应头
3. 空行
4. 响应体

---

## 状态码

### 1xx 信息响应

- **100 Continue**: 继续请求
- **101 Switching Protocols**: 切换协议

### 2xx 成功

- **200 OK**: 请求成功
- **201 Created**: 资源已创建
- **204 No Content**: 无内容返回

### 3xx 重定向

- **301 Moved Permanently**: 永久重定向
- **302 Found**: 临时重定向
- **304 Not Modified**: 资源未修改

### 4xx 客户端错误

- **400 Bad Request**: 请求错误
- **401 Unauthorized**: 未授权
- **403 Forbidden**: 禁止访问
- **404 Not Found**: 资源不存在
- **429 Too Many Requests**: 请求过多

### 5xx 服务器错误

- **500 Internal Server Error**: 服务器内部错误
- **502 Bad Gateway**: 网关错误
- **503 Service Unavailable**: 服务不可用

---

## 重要的 HTTP 头部

### 请求头

| Header            | 说明             | 示例                                        |
| ----------------- | ---------------- | ------------------------------------------- |
| `User-Agent`      | 客户端标识       | `Mozilla/5.0 (Windows NT 10.0; Win64; x64)` |
| `Accept`          | 可接受的内容类型 | `application/json, text/html`               |
| `Accept-Encoding` | 可接受的编码     | `gzip, deflate, br`                         |
| `Accept-Language` | 可接受的语言     | `zh-CN,zh;q=0.9,en;q=0.8`                   |
| `Cookie`          | Cookie 信息      | `session_id=abc123; token=xyz`              |
| `Referer`         | 来源页面         | `https://example.com/page1`                 |
| `Origin`          | 请求来源         | `https://example.com`                       |
| `Authorization`   | 认证信息         | `Bearer eyJhbGciOiJIUzI1NiIs...`            |
| `Content-Type`    | 请求体类型       | `application/json`                          |
| `Content-Length`  | 请求体长度       | `256`                                       |

### 响应头

| Header                        | 说明          | 示例                                         |
| ----------------------------- | ------------- | -------------------------------------------- |
| `Content-Type`                | 响应内容类型  | `application/json; charset=utf-8`            |
| `Content-Length`              | 响应体长度    | `1024`                                       |
| `Set-Cookie`                  | 设置 Cookie   | `session_id=abc; Path=/; HttpOnly`           |
| `Cache-Control`               | 缓存控制      | `no-cache, no-store, must-revalidate`        |
| `Access-Control-Allow-Origin` | CORS 允许的源 | `*` 或 `https://example.com`                 |
| `Location`                    | 重定向地址    | `https://example.com/new-page`               |
| `Content-Encoding`            | 内容编码      | `gzip`                                       |
| `ETag`                        | 资源标识      | `"33a64df551425fcc55e4d42a148795d9f25f89d4"` |

---

## HTTPS 工作原理

### TLS/SSL 加密

HTTPS 在 HTTP 基础上增加了 TLS/SSL 加密层：

```
应用层: HTTP
安全层: TLS/SSL
传输层: TCP
网络层: IP
```

### TLS 握手过程

1. **ClientHello**: 客户端发送支持的加密套件、TLS 版本等
2. **ServerHello**: 服务器选择加密套件，发送证书
3. **证书验证**: 客户端验证服务器证书
4. **密钥交换**: 使用 RSA 或 DH 算法交换密钥
5. **完成握手**: 双方确认，开始加密通信

### 证书验证

- **证书链**: 服务器证书 → 中间证书 → 根证书
- **信任锚点**: 操作系统/浏览器内置的根证书
- **证书吊销**: CRL 和 OCSP 检查

---

## 逆向分析中的应用

### 1. 流量分析

使用代理工具拦截和分析 HTTPS 流量：

```bash
# 使用 mitmproxy
mitmproxy --mode transparent --set console_mouse=false

# 使用 Burp Suite
# 配置浏览器代理到 127.0.0.1:8080
# 安装 Burp CA 证书
```

### 2. 证书绕过

某些应用会进行证书固定（Certificate Pinning），需要绕过：

```javascript
// Hook Java 的证书验证 (Android)
Java.perform(function () {
  var TrustManager = Java.use("javax.net.ssl.X509TrustManager");
  TrustManager.checkServerTrusted.implementation = function (chain, authType) {
    console.log("Certificate pinning bypassed");
  };
});
```

### 3. 请求重放

捕获请求后可以修改参数重放：

```python
import requests

headers = {
    'User-Agent': 'Mozilla/5.0',
    'Authorization': 'Bearer token123'
}

response = requests.post(
    'https://api.example.com/data',
    headers=headers,
    json={'key': 'value'}
)
```

### 4. 签名分析

很多 API 会对请求参数进行签名：

```javascript
// 常见的签名生成流程
function generateSignature(params) {
  // 1. 参数排序
  const sorted = Object.keys(params).sort();

  // 2. 拼接字符串
  let str = "";
  sorted.forEach((key) => {
    str += key + "=" + params[key] + "&";
  });

  // 3. 加上密钥
  str += "secret_key";

  // 4. MD5/SHA256 哈希
  return md5(str);
}
```

---

## HTTP/2 特性

### 多路复用

- 单个 TCP 连接可以并发多个请求
- 解决了 HTTP/1.1 的队头阻塞问题

### 二进制分帧

- 使用二进制格式而非文本
- 更高效的解析

### 服务器推送

- 服务器可以主动推送资源
- 减少请求次数

### 头部压缩

- 使用 HPACK 算法压缩头部
- 减少传输数据量

---

## 常见问题

### Q: 如何在逆向时识别 API 加密？

**A**:

1. 抓包观察请求参数是否有明显的加密特征（Base64、Hex 编码）
2. 在浏览器 DevTools 中搜索参数名，定位到生成代码
3. 设置断点，追踪参数生成流程
4. 识别使用的加密算法（常见的有 MD5、SHA256、AES 等）

### Q: HTTPS 一定安全吗？

**A**:
不一定。HTTPS 只保证传输层安全，但不能防止：

- XSS 攻击
- CSRF 攻击
- 中间人攻击（如果证书验证被绕过）
- 应用层的逻辑漏洞

### Q: 如何处理 HTTP/2 的流量分析？

**A**:

- 使用支持 HTTP/2 的代理工具（如最新版 Burp Suite、Charles）
- 浏览器 DevTools 可以查看 HTTP/2 流量
- Wireshark 可以解析 HTTP/2 协议（需要 SSL 密钥）

---

## 进阶阅读

- [RFC 7230 - HTTP/1.1 Message Syntax and Routing](https://tools.ietf.org/html/rfc7230)
- [RFC 7540 - HTTP/2](https://tools.ietf.org/html/rfc7540)
- [RFC 8446 - TLS 1.3](https://tools.ietf.org/html/rfc8446)
- [MDN Web Docs - HTTP](https://developer.mozilla.org/en-US/docs/Web/HTTP)

---

## 相关章节

- [TLS/SSL 握手过程](./tls_ssl_handshake.md)
- [CORS 与同源策略](./cors_and_same_origin_policy.md)
- [浏览器开发者工具](../02-Tooling/browser_devtools.md)
- [Burp Suite 指南](../02-Tooling/burp_suite_guide.md)
