---
title: "JavaScript 调试问题"
date: 2025-12-25
weight: 10
---

# JavaScript 调试问题

JavaScript 逆向和调试中的常见问题及解决方案。

---

## 断点不生效

### 问题表现

- 设置断点后代码不暂停
- 断点显示灰色
- 代码跳过断点继续执行

### 原因分析

1. 代码已被优化或内联
2. Source Map 不匹配
3. 异步代码执行时机问题
4. 代码被动态生成

### 解决方案

#### 1. 使用 debugger 语句

```javascript
// 在代码中直接插入
function suspiciousFunction(data) {
debugger; // 强制暂停
// ... 后续代码
}
```

**通过 Hook 注入**:

```javascript
// 在控制台执行
const original = window.someFunction;
window.someFunction = function (...args) {
debugger; // 在调用前暂停
return original.apply(this, args);
};
```

#### 2. 使用条件断点

在 DevTools 中右键断点 → Edit breakpoint:

```javascript
// 只有当条件满足时才暂停
userId === 12345;

// 或使用表达式
console.log("Value:", someVar) || false;
```

#### 3. DOM 断点

```javascript
// 监听 DOM 修改
const element = document.querySelector("#target");

// Break on: subtree modifications, attribute modifications, node removal
```

#### 4. Event Listener 断点

```javascript
// DevTools → Sources → Event Listener Breakpoints
// 勾选相关事件 (如 click, xhr, timeout)

// 或者代码中监听
monitorEvents(document.body, "click");
```

---

## 无法查看变量值

### 问题表现

- 变量显示 `undefined` 或 `<unavailable>`
- Scope 中看不到变量
- 闭包变量无法访问

### 解决方案

#### 1. 检查作用域

```javascript
// 在 Console 中，使用正确的作用域
// 如果在函数内部断点:

// ❌ 错误 - 全局作用域
console.log(localVar); // undefined

// ✅ 正确 - 当前作用域可见
// 直接在 Scope 面板查看，或在 Console 输入变量名
```

#### 2. 使用 Watch 表达式

```javascript
// Sources → Watch → Add expression

// 添加复杂表达式
this.userData.profile.name;
JSON.stringify(config, null, 2);
Object.keys(this);
```

#### 3. 使用 console.dir 查看对象

```javascript
// 查看对象完整结构
console.dir(complexObject);

// 查看原型链
console.log(Object.getPrototypeOf(obj));

// 查看所有属性
console.log(Object.getOwnPropertyNames(obj));
```

#### 4. 临时修改代码

```javascript
// 使用 Overrides 功能
// DevTools → Sources → Overrides → Enable Local Overrides

// 在代码中添加日志
function encrypt(data) {
console.log("encrypt input:", data); // 添加这行
const result = doEncrypt(data);
console.log("encrypt output:", result); // 添加这行
return result;
}
```

---

## Source Map 问题

### 问题表现

- 代码显示混淆后的版本
- 无法看到原始代码
- Source Map 加载失败

### 解决方案

#### 1. 手动加载 Source Map

```javascript
// 如果有 .map 文件
//# sourceMappingURL=app.js.map

// 在 DevTools → Sources 右键文件 → "Add source map"
// 输入 Source Map URL
```

#### 2. 使用在线工具

```bash
# 使用 source-map-cli 还原
npm install -g source-map-cli

# 查看原始位置
source-map resolve app.js.map 1 100
```

#### 3. 格式化代码

```javascript
// DevTools → Sources → 点击 {} 按钮 (Pretty print)
// 或快捷键: Ctrl + Shift + P → "Pretty print"
```

---

## 混淆代码调试

### 问题表现

- 变量名如 `_0x1a2b`, `a`, `b`
- 代码逻辑难以理解
- 大量无意义代码

### 解决方案

#### 1. 使用 AST 工具还原

```javascript
// 使用 Babel 还原
const parser = require("@babel/parser");
const traverse = require("@babel/traverse").default;
const generate = require("@babel/generator").default;

const code = `/* 混淆后的代码 */`;
const ast = parser.parse(code);

// 还原变量名
traverse(ast, {
Identifier(path) {
if (path.node.name.startsWith("_0x")) {
path.node.name = "var_" + Math.random().toString(36).substr(2, 9);
}
},
});

const output = generate(ast, {}, code);
console.log(output.code);
```

#### 2. 在线反混淆工具

- [https://deobfuscate.io/](https://deobfuscate.io/)
- [https://lelinhtinh.github.io/de4js/](https://lelinhtinh.github.io/de4js/)

#### 3. 动态调试追踪

```javascript
// Hook 所有函数调用
const originalFunction = window._0x1a2b;
window._0x1a2b = function (...args) {
console.log("Called with:", args);
const result = originalFunction.apply(this, args);
console.log("Returned:", result);
return result;
};
```

#### 4. 使用反混淆脚本

```javascript
// Tampermonkey 脚本
// 在页面加载前注入
(function () {
"use strict";

// Hook eval
const originalEval = window.eval;
window.eval = function (code) {
console.log("eval code:", code);
return originalEval.call(this, code);
};

// Hook Function 构造器
const OriginalFunction = window.Function;
window.Function = function (...args) {
console.log("Function args:", args);
return OriginalFunction.apply(this, args);
};
})();
```

---

## 异步代码跟踪

### 问题表现

- Promise/async 代码难以调试
- 回调地狱
- 执行顺序混乱

### 解决方案

#### 1. Async Stack Traces

```javascript
// Chrome DevTools 默认启用
// Settings → Enable async stack traces

// 现在可以看到完整的异步调用栈
async function fetchData() {
debugger; // 可以看到异步调用链
const data = await fetch("/api/data");
return data.json();
}
```

#### 2. 使用 console.trace

```javascript
async function complexAsync() {
console.trace("Start"); // 显示调用栈

await step1();
console.trace("After step1");

await step2();
console.trace("After step2");
}
```

#### 3. 添加异步日志

```javascript
// 包装 fetch
const originalFetch = window.fetch;
window.fetch = async function (...args) {
console.log("Fetch started:", args[0]);
try {
const response = await originalFetch.apply(this, args);
console.log("Fetch completed:", response.status);
return response;
} catch (error) {
console.error("Fetch failed:", error);
throw error;
}
};
```

---

## XHR/Fetch 请求拦截

### 问题表现

- 无法捕获 AJAX 请求
- 需要查看请求参数
- 需要修改请求

### 解决方案

#### 1. XHR 断点

```javascript
// DevTools → Sources → XHR/fetch Breakpoints
// 添加 URL 包含的关键字，如 "/api/"
```

#### 2. Hook XMLHttpRequest

```javascript
(function () {
const XHR = XMLHttpRequest.prototype;
const open = XHR.open;
const send = XHR.send;

XHR.open = function (method, url) {
this._method = method;
this._url = url;
return open.apply(this, arguments);
};

XHR.send = function (data) {
console.log("XHR Request:", {
method: this._method,
url: this._url,
data: data,
});

this.addEventListener("load", function () {
console.log("XHR Response:", {
status: this.status,
response: this.responseText,
});
});

return send.apply(this, arguments);
};
})();
```

#### 3. Hook Fetch

```javascript
(function () {
const originalFetch = window.fetch;

window.fetch = async function (...args) {
console.log("Fetch Request:", args);

const response = await originalFetch.apply(this, args);

// Clone 响应以避免消费
const clonedResponse = response.clone();
const text = await clonedResponse.text();

console.log("Fetch Response:", {
status: response.status,
body: text,
});

return response;
};
})();
```

---

## WebAssembly 调试

### 问题表现

- WASM 代码难以理解
- 无法设置断点
- 变量查看困难

### 解决方案

#### 1. 使用 WASM Debug Info

```javascript
// 如果 WASM 包含调试信息
// Chrome DevTools 可以显示源码

// 查看 WASM 模块
WebAssembly.instantiate(bytes, imports).then((result) => {
console.log(result.instance.exports);
});
```

#### 2. 使用 wasmtime/wasmer 调试

```bash
# 使用 wasmtime 运行并调试
wasmtime --invoke main module.wasm

# 使用 wasmer
wasmer run module.wasm
```

#### 3. Hook WASM 函数

```javascript
// 获取 WASM 实例
const instance = wasmInstance;

// Hook 导出函数
const originalFunc = instance.exports.encrypt;
instance.exports.encrypt = function (...args) {
console.log("WASM encrypt called:", args);
const result = originalFunc.apply(this, args);
console.log("WASM encrypt result:", result);
return result;
};
```

---

## 时间相关问题

### 问题表现

- 时间戳检测
- 超时失效
- 定时器问题

### 解决方案

#### 1. Hook Date

```javascript
// 固定时间
const fixedTime = new Date("2024-01-01 00:00:00").getTime();

const OriginalDate = Date;
window.Date = function (...args) {
if (args.length === 0) {
return new OriginalDate(fixedTime);
}
return new OriginalDate(...args);
};
Date.now = function () {
return fixedTime;
};
Date.prototype = OriginalDate.prototype;
```

#### 2. Hook setTimeout/setInterval

```javascript
const originalSetTimeout = window.setTimeout;
window.setTimeout = function (callback, delay, ...args) {
console.log(`setTimeout called: ${delay}ms`);
return originalSetTimeout(callback, delay, ...args);
};
```

---

## 无限 debugger

### 问题表现

```javascript
// 反调试代码
setInterval(function () {
debugger;
}, 100);
```

### 解决方案

#### 1. 禁用断点

```javascript
// Chrome DevTools:
// 点击 "Deactivate breakpoints" 按钮 (Ctrl + F8)
```

#### 2. 条件断点绕过

```javascript
// 在 debugger 语句上右键 → "Never pause here"

// 或添加条件断点
false; // 永远不暂停
```

#### 3. 替换 debugger

```javascript
// 使用 Overrides 或 Requestly
// 将代码中的 debugger 替换为空语句

// 或 Hook Function
const _constructor = Function.prototype.constructor;
Function.prototype.constructor = function (...args) {
if (args.length > 0 && /debugger/.test(args[args.length - 1])) {
return function () {};
}
return _constructor.apply(this, args);
};
```

---

## 调试技巧总结

### 1. 快捷键

| 操作 | Windows/Linux | Mac |
| ------------- | ---------------- | ------------- |
| 打开 DevTools | F12 | Cmd + Opt + I |
| 打开控制台 | Ctrl + Shift + J | Cmd + Opt + J |
| 下一步 | F10 | F10 |
| 进入函数 | F11 | F11 |
| 跳出函数 | Shift + F11 | Shift + F11 |
| 继续执行 | F8 | F8 |
| 禁用断点 | Ctrl + F8 | Cmd + F8 |

### 2. Console API

```javascript
// 分组日志
console.group("Group 1");
console.log("message 1");
console.log("message 2");
console.groupEnd();

// 表格显示
console.table([
{ name: "a", value: 1 },
{ name: "b", value: 2 },
]);

// 计时
console.time("operation");
// ... 操作
console.timeEnd("operation");

// 计数
console.count("counter"); // counter: 1
console.count("counter"); // counter: 2

// 断言
console.assert(1 === 2, "Should not happen");
```

### 3. Performance 调试

```javascript
// 性能标记
performance.mark("start");
// ... 操作
performance.mark("end");
performance.measure("operation", "start", "end");

console.log(performance.getEntriesByType("measure"));
```

---

## 相关章节

- [调试技巧](../03-Basic-Recipes/debugging_techniques.md)
- [Hook 技巧](../03-Basic-Recipes/hooking_techniques.md)
- [JavaScript 反混淆](../04-Advanced-Recipes/javascript_deobfuscation.md)
- [浏览器 DevTools](../02-Tooling/browser_devtools.md)
