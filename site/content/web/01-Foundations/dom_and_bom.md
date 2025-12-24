---
title: "DOM 与 BOM"
date: 2025-12-25
weight: 10
---

# DOM 与 BOM

## 概述

DOM (文档对象模型) 和 BOM (浏览器对象模型) 是 JavaScript 与网页内容及浏览器窗口交互的接口。在 Web 逆向中，理解它们对于定位页面元素、分析事件触发逻辑以及应对反调试至关重要。

---

## DOM (Document Object Model)

DOM 将 HTML 文档解析为一个树状结构，JavaScript 通过 DOM API 来操作页面内容。

### 1. 核心概念

- **DOM Tree**: 整个文档的层级结构。
- **Node (节点)**: 树中的每个组成部分（元素、文本、注释等）。
- **Element (元素)**: HTML 标签对应的节点（如 `<div>`, `<body>`）。

### 2. 常用操作

#### 选择与遍历

```javascript
// 选择器
document.getElementById("app"); // 唯一 ID
document.querySelector(".class-name"); // 第一个匹配
document.querySelectorAll("div > span"); // 所有匹配

// 遍历
element.parentNode; // 父节点
element.children; // 子元素列表
element.nextElementSibling; // 下一个兄弟元素
```

#### 修改 DOM

```javascript
// 创建
let newDiv = document.createElement("div");
newDiv.innerText = "Injected Content";

// 插入
document.body.appendChild(newDiv);

// 删除
element.remove();

// 属性操作
input.value = "hacked";
img.getAttribute("src");
```

### 3. 事件系统 (Event System)

逆向中最重要的部分之一。按钮点击触发加密、表单提交触发验证，背后都是事件在驱动。

#### 事件流

1. **捕获阶段 (Capturing)**: 从 window 往下传导到目标元素。
2. **目标阶段 (Target)**: 到达实际触发事件的元素。
3. **冒泡阶段 (Bubbling)**: 从目标元素往上传导回 window。

```javascript
element.addEventListener("click", handler, false); // false 表示在冒泡阶段触发（默认）
```

#### [Reverse Engineering Context] 定位事件监听器

**问题**: 点击一个按钮触发了加密请求，代码在哪里？

**方法**:

1. **DevTools -> Elements 面板**: 选中元素，右侧 "Event Listeners" 标签。可以看到绑定的事件，点击链接跳转到 JS 代码。
- _注意_: 如果使用了 jQuery 或 Vue/React 框架，监听器可能绑定在 `document` 或父节点上（事件委托）。
2. **DevTools -> Sources -> Event Listener Breakpoints**: 勾选 `Mouse -> click`。点击按钮时断点会停在事件处理函数的第一行。
3. **DOM 断点**:
    - **Subtree modifications**: 监听子节点变化（如动态插入了加密后的 token）。
    - **Attribute modifications**: 监听属性变化（如 class 改变）。
    - **Node removal**: 监听节点被删除。

---

## BOM (Browser Object Model)

BOM 提供了与浏览器窗口交互的对象，核心是 `window`。

### 1. Window 对象

全局作用域对象，所有全局变量（`var`）和函数都是它的属性。

- **逆向技巧**: 在 Console 输入 `window` 或 `this` 查看挂载的全局对象，常能发现暴露出来的加密库（如 `window.encrypt_lib`）。

### 2. Location (地址栏)

管理 URL。

```javascript
location.href; // 当前完整 URL
location.search; // 查询参数 (?id=1&token=abc)
location.reload(); // 刷新页面
location.replace("https://google.com"); // 跳转且不留历史记录
```

### 3. History (历史记录)

单页应用 (SPA) 常利用 History API 实现前端路由。

```javascript
history.pushState({}, "", "/new-path"); // 修改 URL 但不刷新
```

### 4. Screen & Navigator (指纹与环境)

- `screen.width` / `screen.height`: 屏幕分辨率。
- `navigator.userAgent`: 用户代理字符串。

#### [Reverse Engineering Context] 反调试检测

很多站点会检测 BOM 属性来判断是否处于调试模式。

1. **检测窗口大小**: 开发者工具打开时，网页可视区域 (`window.innerWidth` / `innerHeight`) 会变小。

```javascript
setInterval(() => {
if (window.outerWidth - window.innerWidth > 160) {
console.log("DevTools opened!");
}
}, 1000);
```

2. **检测 Console**: 重写 `console.log` 或利用 `console.table` 等方法的特殊行为。

3. **debugger 语句**:

```javascript
setInterval(() => {
    debugger; // 如果开启了 DevTools，会无限断点卡住页面
}, 100);
```

**对抗**:
- "Never pause here" (DevTools 右键断点行)。
- Hook `Function.prototype.constructor` (如果是 `Function("debugger")()` 这种形式)。
- 本地替换 (Local Override) 删除 `debugger` 语句。

---

## 总结

- **DOM** 是内容的载体，**逆向核心**是利用 DOM 断点和事件监听器断点快速定位业务逻辑入口。
- **BOM** 是环境的接口，**逆向核心**是识别和绕过基于浏览器环境特征的反调试/反爬虫检测。
