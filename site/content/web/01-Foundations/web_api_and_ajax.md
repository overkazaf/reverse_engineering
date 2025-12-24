---
title: "Web API 与 Ajax"
date: 2025-12-25
weight: 10
---

# Web API 与 Ajax

## 概述

Web API 和 Ajax 是现代 Web 应用的核心。对于逆向工程师来说，理解这些技术是拦截网络请求、分析数据流向以及绕过某些安全检测的基础。

---

## Ajax 与网络请求

### 1. XMLHttpRequest (XHR)

XHR 是传统的 Ajax 实现方式，虽然 Fetch API 越来越流行，但许多老项目和混淆代码（如加密库）仍在使用 XHR。

#### XHR 生命周期与状态

XHR 对象通过 `readyState` 属性表示请求状态：

- `0 (UNSENT)`: 对象已创建，但未调用 `open()`。
- `1 (OPENED)`: `open()` 已调用。
- `2 (HEADERS_RECEIVED)`: `send()` 已调用，头部和状态可用。
- `3 (LOADING)`: 下载中，`responseText` 包含部分数据。
- `4 (DONE)`: 下载操作完成。

#### [Reverse Engineering Context] Hook XHR

在逆向中，我们经常 Hook `open` 和 `send` 方法来拦截请求参数和修改请求体。

```javascript
(function () {
let originalOpen = XMLHttpRequest.prototype.open;
let originalSend = XMLHttpRequest.prototype.send;

XMLHttpRequest.prototype.open = function (
method,
url,
async,
user,
password
) {
// 记录或修改 URL/Method
this._url = url; // 保存 URL 供 send 使用
console.log(`[XHR Open] ${method} ${url}`);

// 调用原始方法
return originalOpen.apply(this, arguments);
};

XMLHttpRequest.prototype.send = function (body) {
// 记录或修改请求体
console.log(`[XHR Send] to ${this._url}:`, body);

// 如果需要监听响应，可以绑定 onreadystatechange
this.addEventListener("readystatechange", function () {
if (this.readyState === 4) {
console.log(
`[XHR Response] from ${this.responseURL}:`,
this.responseText.slice(0, 100)
);
}
});

return originalSend.apply(this, arguments);
};
})();
```

### 2. Fetch API

Fetch 是基于 Promise 的新一代网络请求 API，语法更简洁，处理方式与 XHR 不同。

#### 基本用法

```javascript
fetch("https://api.example.com/data", {
method: "POST",
headers: { "Content-Type": "application/json" },
body: JSON.stringify({ id: 1 }),
})
.then((response) => response.json()) // 解析 JSON
.then((data) => console.log(data));
```

#### [Reverse Engineering Context] Hook Fetch

Fetch 是全局 `window` 对象的一个方法，Hook 起来相对简单。

```javascript
(function () {
let originalFetch = window.fetch;

window.fetch = async function (url, options) {
console.log(`[Fetch] ${url}`, options);

// 修改请求参数
if (url.includes("/api/sign")) {
// options.headers['X-Modified'] = 'true';
}

// 调用原始 fetch
let response = await originalFetch(url, options);

// 拦截响应（注意：response流只能读取一次，需要clone）
let clone = response.clone();
clone.text().then((body) => {
console.log(`[Fetch Response]`, body.slice(0, 100));
});

return response;
};
})();
```

### 3. WebSocket

WebSocket 提供全双工通信通道。逆向中常用于分析实时数据流（如直播弹幕、股票行情、游戏数据）。

#### [Reverse Engineering Context] Hook WebSocket

拦截 WebSocket 的 `send` (发包) 和 `onmessage` (收包)。

```javascript
(function () {
let OriginalWebSocket = window.WebSocket;

window.WebSocket = function (url, protocols) {
let ws = new OriginalWebSocket(url, protocols);
console.log(`[WebSocket] Connecting to ${url}`);

// Hook 发送
let originalSend = ws.send;
ws.send = function (data) {
console.log(`[WebSocket Send]`, data);
return originalSend.apply(this, arguments);
};

// Hook 接收
// WebSocket 的 onmessage 属性通常在实例创建后被赋值
// 使用 Object.defineProperty 拦截 setter 是一种更通用的方法
let onmessageVal;
Object.defineProperty(ws, "onmessage", {
configurable: true,
enumerable: true,
get() {
return onmessageVal;
},
set(fn) {
onmessageVal = function (event) {
console.log(`[WebSocket Recv]`, event.data);
return fn.apply(this, arguments);
};
},
});

return ws;
};

// 复制原型链，保持 instanceof 检查通过
window.WebSocket.prototype = OriginalWebSocket.prototype;
window.WebSocket.CONNECTING = OriginalWebSocket.CONNECTING;
// ... 其他静态属性
})();
```

---

## 常用 Web API

### 1. Storage API (存储)

Web 应用常用本地存储来保存 Session ID、Token 或加密密钥。

- **localStorage / sessionStorage**: 键值对存储。
- 逆向关注点：`localStorage.getItem('token')`。
- **Cookie**: 这个比较特殊，通常作为 HTTP 头发送。
- 逆向关注点：`document.cookie` 的读写。Hook `document.cookie` 的 setter 可以追踪 Cookie 的生成位置。

```javascript
// Hook Cookie Setter
Object.defineProperty(document, "cookie", {
set: function (val) {
console.log("[Cookie Set]", val);
debugger; // 在此处断点，查看调用栈
// 实际设置 cookie 的逻辑需要小心处理，防止无限递归或失效
// 通常在 hook 中不真正设置，或者通过 document->proto->cookie setter
},
});
```

### 2. Canvas API (指纹识别)

Canvas 除了绘图，常用于 **Canvas Fingerprinting**（帆布指纹）。网站在 hidden canvas 上绘制特定文本和图形，转换成 base64，不同浏览器/硬件渲染出的像素有微小差异，生成唯一 ID。

- **逆向特征**: 搜索 `toDataURL` 或 `getImageData`。
- **对抗**: 随机化 canvas 渲染结果，或固定返回特定指纹。

### 3. Navigator API (环境检测)

用于检测浏览器环境，反爬虫常检查以下属性：

- `navigator.userAgent`: 浏览器 UA。
- `navigator.webdriver`: **重点**，自动化工具（Selenium/Puppeteer）通常为 `true`。
- `navigator.plugins`: 插件列表。
- `navigator.languages`: 语言。

---

## 跨域通信 (postMessage)

`window.postMessage` 允许不同源的窗口（如 iframe 和父页面）通信。

```javascript
// 发送消息
otherWindow.postMessage(message, targetOrigin);

// 接收消息
window.addEventListener("message", (event) => {
if (event.origin !== "http://trusted.com") return;
console.log(event.data);
});
```

- **逆向场景**: 如果验证码或加密逻辑在 iframe 中，主页面通过 postMessage 获取 token，我们需要关注 message 事件的监听器。

---

## 总结

掌握 Web API 的 Hook 技术是 JS 逆向的“基本功”。无论是 XHR/Fetch 的网络层拦截，还是 Cookie/Storage 的数据层监控，亦或是 Canvas/Navigator 的环境层对抗，核心思路都是：**找到关键 API -> 替换实现 (Hook) -> 插入监控代码/修改逻辑 -> 调用原始实现**。
