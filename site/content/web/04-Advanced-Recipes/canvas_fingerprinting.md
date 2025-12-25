---
title: "Canvas 指纹技术"
date: 2025-06-17
type: posts
tags: ["Web", "浏览器指纹", "Canvas指纹", "WebAssembly", "代理池", "电商"]
weight: 10
---

# Canvas 指纹技术

## 思考时刻

在学习 Canvas 指纹之前，先思考：

1. **为什么 Cookie 和 IP 地址不够用？** 为什么网站还需要指纹识别？
2. **你的浏览器是独一无二的吗？** 即使你换了 IP、清空了 Cookie，网站还能认出你吗？
3. **画布指纹的原理是什么？** 为什么在同一个 Canvas 上画同样的东西，不同电脑会产生不同的结果？
4. **实战场景：** 某电商网站限制每个用户只能抢购一件商品，你换了浏览器、清空了缓存、使用了代理，为什么还是被识别出来了？

这些问题的答案，藏在浏览器的渲染引擎里。

---

## 📚 前置知识

在开始本配方之前，建议先掌握以下内容：

| 知识领域 | 重要程度 | 参考资料 |
|----------|---------|---------|
| 浏览器架构 | 必需 | [浏览器架构](../01-Foundations/browser_architecture.md) |
| 浏览器指纹识别 | 必需 | [浏览器指纹识别](./browser_fingerprinting.md) |
| JavaScript 基础 | 必需 | [JavaScript 基础](../01-Foundations/javascript_basics.md) |
| DOM 与 BOM | 推荐 | [DOM 与 BOM](../01-Foundations/dom_and_bom.md) |
| Hook 技术 | 推荐 | [Hook 技术](../03-Basic-Recipes/hooking_techniques.md) |

> 💡 **提示**: Canvas 指纹是**最稳定**的指纹识别方式之一，因为它依赖于硬件和软件的渲染差异。了解其原理后，你可以通过 Hook Canvas API 来伪装指纹。

---

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
const canvas = document.createElement("canvas");
const ctx = canvas.getContext("2d");

// 2. 绘制特定内容
ctx.textBaseline = "top";
ctx.font = "14px Arial";
ctx.textBaseline = "alphabetic";
ctx.fillStyle = "#f60";
ctx.fillRect(125, 1, 62, 20);
ctx.fillStyle = "#069";
ctx.fillText("Hello, world!", 2, 15);
ctx.fillStyle = "rgba(102, 204, 0, 0.7)";
ctx.fillText("Hello, world!", 4, 17);

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
HTMLCanvasElement.prototype.toDataURL = function () {
console.log("[Canvas] toDataURL called");
console.trace();
return originalToDataURL.apply(this, arguments);
};

// Hook getImageData
const originalGetImageData = CanvasRenderingContext2D.prototype.getImageData;
CanvasRenderingContext2D.prototype.getImageData = function () {
console.log("[Canvas] getImageData called");
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
HTMLCanvasElement.prototype.toDataURL = function (...args) {
// 获取原始数据
const dataURL = originalToDataURL.apply(this, arguments);

// 注入噪点（修改少量像素）
const canvas = this;
const ctx = canvas.getContext("2d");
const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
const data = imageData.data;

// 随机修改 0.01% 的像素
for (let i = 0; i < data.length; i += 4) {
if (Math.random() < 0.0001) {
data[i] = Math.floor(Math.random() * 256); // R
data[i + 1] = Math.floor(Math.random() * 256); // G
data[i + 2] = Math.floor(Math.random() * 256); // B
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
HTMLCanvasElement.prototype.toDataURL = function (...args) {
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
| ------------ | --------------- | --------------- |
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

- [浏览器指纹识别](../04-Advanced-Recipes/browser_fingerprinting.md)
- [WebRTC 指纹与隐私](./webrtc_fingerprinting.md)
- [反爬虫技术深度分析](./anti_scraping_deep_dive.md)
