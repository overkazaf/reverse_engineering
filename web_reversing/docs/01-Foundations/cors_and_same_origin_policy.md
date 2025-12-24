# CORS 与同源策略

## 概述

同源策略 (Same-Origin Policy, SOP) 是浏览器最核心的安全机制，而 CORS (Cross-Origin Resource Sharing) 是 SOP 的各种 "例外" 之一。理解它们对于调试 API 请求失败、跨域注入攻击以及本地搭建测试环境至关重要。

---

## 同源策略 (SOP)

### 1. 定义

两个 URL 说它们是“同源”的，必须满足三个条件完全相同：

1. **协议 (Protocol)**: 都是 `http` 或都是 `https`。
2. **域名 (Domain)**: 如 `www.example.com`。
3. **端口 (Port)**: 如 `80`, `443`。

如果不同源，浏览器会限制：

- **Cookie, LocalStorage, IndexedDB** 读取。
- **DOM** 访问 (如 iframe)。
- **AJAX** 请求发送 (实际上请求通常能发出，但响应会被浏览器拦截，除非服务器允许 CORS)。

### 2. [Reverse Engineering Context] 为什么我的本地测试失败了？

很多时候，你把别人的 JS 代码 down 下来，在本地开个 `file://` 或 `localhost:8000` 运行，结果发现 API 请求全都报红：
`Access to fetch at ... from origin ... has been blocked by CORS policy`。

**原因**: 目标服务器只允许特定的域名（它的官网）访问，你的 `localhost` 不是它允许的源。

---

## CORS (跨域资源共享)

CORS 是一种机制，它使用额外的 HTTP 头来告诉浏览器：让运行在一个 origin (domain) 上的 Web 应用被准许访问来自不同源服务器上的指定的资源。

### 1. 简单请求 vs 预检请求

- **简单请求**: (GET, POST, HEAD, 且 Content-Type 是 application/x-www-form-urlencoded, multipart/form-data, text/plain 之一)。

- 浏览器直接发请求。
- 看响应头有没有 `Access-Control-Allow-Origin`。

- **预检请求 (Preflight)**: (带自定义 Header, 或 Content-Type 是 application/json 等)。
- 浏览器先发一个 `OPTIONS` 方法的请求。
- 服务器同意了 (`Access-Control-Allow-Methods`, `Access-Control-Allow-Headers`)，浏览器才发真正的请求。

### 2. 关键响应头

- `Access-Control-Allow-Origin`: `*` 或 `https://your-site.com`。
- `Access-Control-Allow-Credentials`: `true` (允许带 Cookie)。

---

## 逆向中的 CORS 绕过技巧

当你需要本地调试目标网站的 API，或者在自己的网站上调用别人的 API 时，必须处理 CORS。

### 1. 浏览器插件 / 启动参数

最简单的方法是关掉浏览器的安全策略（仅限调试用！）。

- **Chrome 启动参数**: `--disable-web-security --user-data-dir="/tmp/xxxx"`。

### 2. 配置反向代理 (Reverse Proxy)

这是最稳健的方法。使用 Nginx 或 Node.js 中间件，把你的请求“伪装”成同源。

**场景**:

- 本地开发环境: `localhost:3000`
- 目标 API: `api.target.com`

**Node.js 代理 (http-proxy-middleware)**:

```javascript
// 你发给 localhost:3000/api/xxx
// 代理转发给 api.target.com/api/xxx
// 并在转发时修改 Origin 头，欺骗服务器
pathRewrite: {'^/api': ''},
changeOrigin: true, // 关键：把请求头中的 Host/Origin 修改为目标域名
```

### 3. JSONP (过时但仍存在)

老旧的跨域方案，利用 `<script>` 标签不受 SOP 限制的特性。

- **特征**: URL 里有个 `callback=xxx`。
- **逆向**: 直接把 URL 里的 callback 改成你自己的函数名，或者直接请求拿到 JS 代码里面就是数据。

---

## 总结

SOP 是浏览器的“围墙”，CORS 是墙上的“门”。

- **正向开发**: 配置服务器开门。
- **逆向分析**: 既然墙是浏览器建的，那不管是关掉浏览器的墙（启动参数），还是骗服务器我是自己人（代理修改 Origin），目标都是为了让数据流通。
