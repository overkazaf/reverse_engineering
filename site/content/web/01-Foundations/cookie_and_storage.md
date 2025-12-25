---
title: "Cookie 与 Storage"
date: 2024-04-09
type: posts
tags: ["Web", "HTTP", "签名验证", "JavaScript", "基础知识", "Hook"]
weight: 10
---

# Cookie 与 Storage

## 概述

Web 应用需要在客户端存储数据，用于维持会话状态（Session）、保存用户偏好或缓存数据。在逆向工程中，这些存储位置往往是寻找 Token、密钥或敏感信息的首选之地。

---

## Cookie

Cookie 是最早的客户端存储机制，主要用于 HTTP 状态管理。

### 1. 结构与属性

一个 Cookie 包含以下关键属性：

- **Name/Value**: 键值对。
- **Domain/Path**: 作用域。
- **Expires/Max-Age**: 有效期。
- **HttpOnly**: **关键属性**。如果设置为 `true`，JS 无法读取（`document.cookie` 读不到），但这不影响抓包。这主要是为了防止 XSS 攻击窃取 Cookie。
- **Secure**: 仅通过 HTTPS 传输。
- **SameSite**: `Strict` / `Lax` / `None`，限制跨站请求携带 Cookie（防止 CSRF）。

### 2. [Reverse Engineering Context] Cookie 逆向

- **Hook Setter**: 如前文所述，Hook `document.cookie` 的 setter 可以定位 JS 是在哪里生成/设置 Cookie 的。
```javascript
var cookie_cache = document.cookie;
Object.defineProperty(document, "cookie", {
get: function () {
return cookie_cache;
},
set: function (val) {
console.log("Setting cookie", val);
cookie_cache = val;
return val;
},
});
```
- **HttpOnly Bypass?**: 如果 Cookie 是 HttpOnly 的，你无法通过 JS Hook 拿到（因为浏览器内核阻止了）。但你可以：
1. 抓包（Burp/Fiddler/Network Panel）。
2. 如果是 Electron 应用，可以尝试调试主进程或使用 Protocol Monitor。

---

## Web Storage (Local / Session)

HTML5 引入的键值对存储，比 Cookie 更大（~5MB），接口更简单。

### 1. LocalStorage vs SessionStorage

- **LocalStorage**: 持久化存储，除非主动删除，否则一直存在。
- **SessionStorage**: 会话级存储，关闭标签页后消失。

### 2. API

- `getItem(key)`
- `setItem(key, value)`
- `removeItem(key)`
- `clear()`

### 3. [Reverse Engineering Context] 监控存储

很多 JWT (JSON Web Token) 存储在 LocalStorage 中。

```javascript
// 简单的 Hook 监控 setItem
const originalSetItem = localStorage.setItem;
localStorage.setItem = function (key, value) {
if (key === "token") {
console.log("[LocalStorage] Token detected:", value);
debugger;
}
return originalSetItem.apply(this, arguments);
};
```

**实战技巧**: 在 DevTools 的 Application 面板可以直接查看和编辑 Storage 数据。

---

## IndexedDB

浏览器内置的非关系型数据库，用于存储大量结构化数据。

### 1. 特点

- 支持事务。
- 支持索引。
- 异步 API。

### 2. 逆向场景

较少用于存储简单的 Token，但在复杂的 Web App（如在线文档、即时通讯、离线应用）中，可能会缓存大量的业务数据甚至代码逻辑。如果发现应用在 Application 面板的 IndexedDB 里存了很多数据，值得看一眼。

---

## 总结

| 存储类型 | 容量 | 生命周期 | JS 可访问性 | 逆向关注点 |
| :----------------- | :--- | :---------- | :-------------- | :------------------- |
| **Cookie** | 4KB | 可设 / 会话 | 取决于 HttpOnly | Session ID, 签名参数 |
| **LocalStorage** | 5MB | 永久 | 是 | JWT Token, 用户配置 |
| **SessionStorage** | 5MB | Tab 关闭 | 是 | 临时状态 |
| **IndexedDB** | 无限 | 永久 | 是 | 大量业务数据 |

**逆向第一步**: F12 -> Application 面板，把这几个地方翻一遍，看看有没有名为 `token`, `auth`, `sign`, `key` 的可疑字段。
