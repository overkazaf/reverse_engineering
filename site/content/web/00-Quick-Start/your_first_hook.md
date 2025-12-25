---
title: "配方：你的第一个 Hook"
date: 2024-04-24
weight: 10
---

# 配方：你的第一个 Hook

## 配方信息

| 项目 | 说明 |
| ------------ | ---------------------- |
| **难度** | ⭐ (入门级) |
| **预计时间** | 15 分钟 |
| **所需工具** | Chrome 浏览器 |
| **适用场景** | 监控网站的所有网络请求 |
| **前置知识** | 无需编程基础 |

---

## 📚 前置知识

本配方是**零基础入门**，无需任何编程经验即可开始学习。

| 知识领域 | 重要程度 | 说明 |
|----------|---------|------|
| 基础计算机操作 | 必需 | 能够使用浏览器和键盘快捷键 |
| 英语阅读能力 | 推荐 | 代码和控制台信息多为英文 |

> 💡 **新手提示**: 这是你进入 Web 逆向世界的第一步！完成本配方后，建议继续学习 [解密 API 参数](./decrypt_api_params.md) 和 [Hook 技术详解](../03-Basic-Recipes/hooking_techniques.md)。

---

## 你将学到

完成这个配方后，你将能够：

- ✅ 打开和使用浏览器开发者工具
- ✅ 在浏览器中注入 JavaScript 代码
- ✅ 拦截和查看所有 XHR/Fetch 请求
- ✅ 理解 Hook 技术的基本原理
- ✅ 导出和保存拦截到的数据

---

## 准备工作

### 检查清单

在开始之前，请确认：

- ☐ 已安装 Chrome 浏览器（或 Edge/Firefox）
- ☐ 能够访问互联网
- ☐ 准备一个目标网站（推荐用 <https://jsonplaceholder.typicode.com/> 作为练习）

### 背景知识

**什么是 Hook？**

Hook（钩子）就像在数据流动的管道上安装一个"监听器"，可以：

- 查看通过管道的所有数据
- 修改数据内容
- 记录数据用于分析

在 Web 逆向中，我们主要 Hook 网络请求函数，监控网站发送和接收的数据。

---

## 步骤详解

### Step 1: 打开开发者工具

1. **打开 Chrome 浏览器**

2. **访问测试网站**:

```
https://jsonplaceholder.typicode.com/
```

3. **打开开发者工具**（三种方式任选其一）:

- 按 `F12` 键
- 按 `Ctrl+Shift+I` (Windows) 或 `Cmd+Option+I` (Mac)
- 右键页面 → "检查"

4. **切换到 Console 标签**

![开发者工具界面](https://via.placeholder.com/800x400?text=DevTools+Console)

✅ **验证**: 你应该看到一个可以输入代码的控制台界面

---

### Step 2: 注入 Hook 代码

1. **复制以下代码**:

```javascript
// Universal Network Monitor Hook
(function () {
console.log(" Network Hook已启动！");

// Hook XMLHttpRequest
const originalXHROpen = XMLHttpRequest.prototype.open;
const originalXHRSend = XMLHttpRequest.prototype.send;

XMLHttpRequest.prototype.open = function (method, url) {
this._method = method;
this._url = url;
return originalXHROpen.apply(this, arguments);
};

XMLHttpRequest.prototype.send = function (body) {
console.log(" [XHR 请求]", {
method: this._method,
url: this._url,
body: body,
});

// Hook 响应
this.addEventListener("load", function () {
console.log(" [XHR 响应]", {
url: this._url,
status: this.status,
response: this.responseText.substring(0, 200) + "...",
});
});

return originalXHRSend.apply(this, arguments);
};

// Hook Fetch API
const originalFetch = window.fetch;
window.fetch = function (...args) {
console.log(" [Fetch 请求]", {
url: args[0],
options: args[1],
});

return originalFetch.apply(this, args).then((response) => {
console.log(" [Fetch 响应]", {
url: response.url,
status: response.status,
});

// Clone response 避免消耗它
return response
.clone()
.text()
.then((body) => {
console.log(" [Fetch 内容]", body.substring(0, 200) + "...");
return response;
});
});
};

console.log("✅ Hook 安装成功！现在所有请求都会被记录。");
})();
```

2. **粘贴到 Console 中**

3. **按 Enter 键执行**

✅ **验证**: 你应该看到消息 "✅ Hook 安装成功！现在所有请求都会被记录。"

---

### Step 3: 触发请求并观察

1. **在测试网站中点击示例链接**:

- 点击 `/posts`
- 点击 `/comments`
- 点击 `/users`

2. **观察 Console 输出**:

你会看到类似这样的输出：

```
[Fetch 请求] {url: "https://jsonplaceholder.typicode.com/posts", options: undefined}
[Fetch 响应] {url: "https://jsonplaceholder.typicode.com/posts", status: 200}
[Fetch 内容] [{"userId":1,"id":1,"title":"sunt aut facere...
```

3. **分析输出信息**:
    - 表示发送的请求
    - 表示收到的响应
    - 可以看到 URL、HTTP 方法、状态码、响应内容

✅ **验证**: 每次点击链接都能在 Console 看到请求和响应记录

---

### Step 4: 保存和导出数据

1. **右键 Console 输出**
2. **选择 "Save as..."**
3. **保存为 `network_log.txt`**

现在你有了所有请求的完整记录！

---

## ✅ 验证清单

完成后，检查以下项目：

- ☐ Console 中看到 "✅ Hook 安装成功！"
- ☐ 点击链接后能看到 和 的日志
- ☐ 日志中包含 URL 和状态码
- ☐ 能看到响应内容的前 200 个字符
- ☐ 成功保存了日志文件

---

## 进阶练习

### 练习 1: Hook 其他网站

尝试在真实网站上使用这个 Hook：

1. 访问 <https://www.douban.com/>
2. 注入同样的 Hook 代码
3. 刷新页面，观察所有请求

**思考**: 你能看到哪些有趣的 API 请求？

### 练习 2: 修改 Hook 脚本

尝试修改代码，添加更多功能：

```javascript
// 只记录包含特定关键词的请求
if (this._url.includes("/api/")) {
console.log(" API 请求", this._url);
}
```

### 练习 3: 统计请求数量

添加计数器：

```javascript
let requestCount = 0;
// 在发送请求时
requestCount++;
console.log(` 总请求数: ${requestCount}`);
```

---

## 常见问题

### Q1: 刷新页面后 Hook 失效了？

**A**: 是的！Hook 是注入到当前页面的 JavaScript 环境中的，刷新页面会清空所有内容。

**解决方案**:

- 每次刷新后重新执行 Hook 代码
- 或者使用浏览器扩展（如 Tampermonkey）自动注入

### Q2: 看不到任何输出？

**A**: 检查以下几点：

1. Hook 代码是否成功执行（有没有报错）
2. 网站是否真的发送了请求（检查 Network 标签）
3. Console 的过滤器是否设置正确（确保显示所有日志）

### Q3: 为什么有些请求看不到？

**A**: 可能的原因：

- 使用了其他请求方式（如 WebSocket）
- 请求在 Hook 代码注入前就发送了
- 使用了原生的网络 API（需要更深层的 Hook）

### Q4: Hook 会影响网站正常运行吗？

**A**: 我们的 Hook 代码只是"监听"，不修改数据，所以**不会影响**网站功能。但如果 Hook 代码有 bug，可能导致页面错误。

### Q5: 如何 Hook 更多的 API？

**A**: 同样的原理可以应用到：

- `localStorage.setItem` / `getItem`
- `document.cookie`
- `WebSocket`
- `XMLHttpRequest.setRequestHeader`

查看 [JavaScript Hook 脚本](../../07-Scripts/javascript_hook_scripts.md) 获取更多示例。

---

## 原理解析

### Hook 是如何工作的？

```javascript
// 1. 保存原始函数
const original = XMLHttpRequest.prototype.send;

// 2. 用我们的函数替换
XMLHttpRequest.prototype.send = function (...args) {
console.log("拦截到了！"); // 我们的代码
return original.apply(this, args); // 调用原函数
};
```

**关键点**:

- JavaScript 允许在运行时修改函数
- 我们用"包装函数"替换原函数
- 包装函数先执行我们的代码，再调用原函数
- 这样既能监控，又不影响功能

---

## 相关配方

### 基础配方

- [Hook 技术](../../03-Basic-Recipes/hooking_techniques.md) - Hook 的深入讲解
- [调试技巧](../../03-Basic-Recipes/debugging_techniques.md) - 使用断点调试

### 高级配方

- [JavaScript Hook 脚本合集](../../07-Scripts/javascript_hook_scripts.md) - 更多即用型 Hook

### 下一步

- [解密 API 参数](./decrypt_api_params.md) - 学习如何分析加密算法

---

## 恭喜！

你已经完成了第一个 Web 逆向配方！

现在你已经掌握了：

- ✅ 基本的 Hook 技术
- ✅ 如何监控网络请求
- ✅ 如何使用浏览器开发者工具

**下一步**: 继续学习 [解密 API 参数](./decrypt_api_params.md)，掌握更高级的技能！

---

**小贴士**:

- 将这个 Hook 代码保存为书签或 Snippet，以便随时使用
- 尝试在不同网站使用，观察它们的请求模式
- 加入逆向工程社区，分享你的发现

Happy Hacking! 
