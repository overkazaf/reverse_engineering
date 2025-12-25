---
title: "Puppeteer & Playwright"
date: 2024-06-17
tags: ["Web", "签名验证", "Hook", "抓包", "Playwright", "DevTools"]
weight: 10
---

# Puppeteer & Playwright

## 概述

Puppeteer (基于 CDP) 和 Playwright (支持多浏览器) 是现代 Web 自动化的首选工具。在逆向中，我们需要利用它们来：

1. **动态渲染**: 抓取 SPA 页面数据。
2. **模拟用户**: 绕过复杂的行为验证码。
3. **Hook 注入**: 在页面加载前注入 JS 代码。

---

## 1. 基础启动 (Puppeteer)

```javascript
const puppeteer = require("puppeteer");

(async () => {
const browser = await puppeteer.launch({
headless: false, // 逆向调试务必开启有头模式
args: [
"--no-sandbox",
"--disable-setuid-sandbox",
"--ignore-certificate-errors", // 忽略证书错误（配合抓包）
"--window-size=1920,1080",
],
});
const page = await browser.newPage();
await page.goto("https://example.com");
// ...
})();
```

---

## 2. 关键逆向技巧

### 注入 Hook 代码 (evaluateOnNewDocument)

这是最重要的功能。在页面所有脚本执行**之前**执行你的代码。

```javascript
// 注入 navigator.webdriver = undefined 以绕过检测
await page.evaluateOnNewDocument(() => {
Object.defineProperty(navigator, "webdriver", {
get: () => undefined,
});
});
```

### 请求拦截 (Request Interception)

可以拦截、修改、中止请求。

```javascript
await page.setRequestInterception(true);
page.on("request", (request) => {
if (request.resourceType() === "image") {
request.abort(); // 加速抓取
} else if (request.url().includes("sign")) {
// 修改 Header
const headers = Object.assign({}, request.headers(), {
"X-Custom-Token": "hacked",
});
request.continue({ headers });
} else {
request.continue();
}
});
```

### CDP Session (直接调用 DevTools 协议)

Puppeteer 封装的功能有限，可以通过 CDP 甚至做更底层的操作。

```javascript
const client = await page.target().createCDPSession();
await client.send("Network.enable");
// 模拟弱网环境
await client.send("Network.emulateNetworkConditions", {
offline: false,
latency: 200,
downloadThroughput: (780 * 1024) / 8,
uploadThroughput: (330 * 1024) / 8,
});
```

---

## 3. Playwright 对比

Playwright API 设计更现代，且原生支持 WebKit (Safari)。

- **Context 隔离**: `browser.newContext()` 极其快速地创建隔离环境（Cookie 互不干扰），适合并发采集。
- **选择器引擎**: 支持 `text="Login"`, `css=.btn`, `xpath=//button` 混合搜索，更鲁棒。

---

## 4. 反爬虫对抗 (Anti-Detection)

直接使用 Puppeteer/Playwright 很容易被识别（因为有指纹）。

### 解决方案

1. **puppeteer-extra-plugin-stealth**: 必装插件。自动抹除几十种常见指纹（Chrome Runtime, Navigator Permissions, WebGL Vendor 等）。
```javascript
const puppeteer = require("puppeteer-extra");
const StealthPlugin = require("puppeteer-extra-plugin-stealth");
puppeteer.use(StealthPlugin());
```
2. **拟人化操作**: 不要 `page.click()` 瞬间点击，而是移动鼠标轨迹 -> 随机停顿 -> 按下 -> 抬起。可以使用 `ghost-cursor` 等库。

---

## 总结

对于逆向工程师，Puppeteer 不仅仅是爬虫工具，更是一个**可编程的浏览器**。利用 `evaluateOnNewDocument` 和 `setRequestInterception`，我们可以构建出强大的动态分析和解密环境。
