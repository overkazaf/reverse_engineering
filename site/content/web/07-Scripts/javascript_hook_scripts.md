---
title: "JavaScript Hook 脚本"
date: 2025-12-25
weight: 10
---

# JavaScript Hook 脚本

## 概述

Hook（钩子）是逆向工程中最核心的动态分析技术之一。通过运行时劫持(Runtime Interception)原生 API 或自定义函数，可以实现对目标代码的无侵入式监控、参数篡改和行为修改。Hook 技术基于 JavaScript 的动态特性和原型链机制，能够在不修改源代码的情况下改变程序执行流程。

### Hook 技术原理

Hook 的本质是**函数替换**（Function Replacement）和**代理模式**（Proxy Pattern）。通过以下几种方式实现：

1. **直接替换**：保存原函数引用，用新函数替换目标函数
2. **原型链劫持**：修改 `prototype` 上的方法，影响所有实例
3. **属性描述符劫持**：使用 `Object.defineProperty` 拦截属性访问
4. **Proxy 代理**：使用 ES6 Proxy 实现更精细的拦截控制

### 应用场景

- **API 监控**: 追踪 XHR/Fetch 请求、Cookie 操作、Storage 访问
- **加密分析**: 捕获加密函数的输入输出，定位密钥和算法
- **反调试绕过**: 屏蔽 `debugger` 语句和控制台检测
- **行为修改**: 修改函数返回值，绕过验证逻辑
- **性能分析**: 统计函数调用次数和执行时间

---

## 基础 Hook 模板

### 1. Hook 全局函数

```javascript
// 保存原始函数
const originalFunction = window.targetFunction;

// 替换为自定义函数
window.targetFunction = function (...args) {
console.log("[Hook] targetFunction called");
console.log("[Hook] Arguments:", args);

// 调用原始函数
const result = originalFunction.apply(this, args);

console.log("[Hook] Return value:", result);
return result;
};
```

---

## 网络请求 Hook

### Hook XMLHttpRequest

```javascript
(function () {
const originalOpen = XMLHttpRequest.prototype.open;
const originalSend = XMLHttpRequest.prototype.send;

// Hook open
XMLHttpRequest.prototype.open = function (method, url) {
this._method = method;
this._url = url;
console.log(`[XHR] ${method} ${url}`);
return originalOpen.apply(this, arguments);
};

// Hook send
XMLHttpRequest.prototype.send = function (body) {
console.log(`[XHR] Request body:`, body);

// Hook 响应
this.addEventListener("readystatechange", function () {
if (this.readyState === 4) {
console.log(`[XHR] Response:`, this.responseText);
}
});

return originalSend.apply(this, arguments);
};
})();
```

### Hook Fetch

```javascript
(function () {
const originalFetch = window.fetch;

window.fetch = function (...args) {
console.log("[Fetch] Request:", args);

return originalFetch.apply(this, args).then((response) => {
console.log("[Fetch] Response:", response);

// Clone response to avoid consuming it
return response
.clone()
.text()
.then((body) => {
console.log("[Fetch] Response body:", body);
return response;
});
});
};
})();
```

### 通用网络请求监控

```javascript
(function () {
// Hook XHR
const XHR_open = XMLHttpRequest.prototype.open;
const XHR_send = XMLHttpRequest.prototype.send;

XMLHttpRequest.prototype.open = function (method, url) {
this._requestInfo = { method, url, time: Date.now() };
console.log(` [XHR] ${method} ${url}`);
return XHR_open.apply(this, arguments);
};

XMLHttpRequest.prototype.send = function (body) {
if (body) {
console.log(` [XHR] Body:`, body);
}

this.addEventListener("load", function () {
const duration = Date.now() - this._requestInfo.time;
console.log(
` [XHR] ${this.status} ${this._requestInfo.url} (${duration}ms)`
);
console.log(` [XHR] Response:`, this.responseText.substring(0, 200));
});

return XHR_send.apply(this, arguments);
};

// Hook Fetch
const originalFetch = window.fetch;
window.fetch = async function (...args) {
const startTime = Date.now();
console.log(` [Fetch]`, args[0]);

if (args[1]?.body) {
console.log(` [Fetch] Body:`, args[1].body);
}

const response = await originalFetch.apply(this, args);
const duration = Date.now() - startTime;

console.log(` [Fetch] ${response.status} (${duration}ms)`);

// Clone to avoid consuming
const clonedResponse = response.clone();
const text = await clonedResponse.text();
console.log(` [Fetch] Response:`, text.substring(0, 200));

return response;
};
})();
```

---

## Cookie Hook

### 监控 Cookie 读写

```javascript
(function () {
let cookieCache = document.cookie;

Object.defineProperty(document, "cookie", {
get: function () {
console.log(" [Cookie] Read:", cookieCache);
console.trace();
return cookieCache;
},
set: function (value) {
console.log(" [Cookie] Write:", value);
console.trace();

// 实际写入 Cookie
const cookieParts = value.split(";")[0];
const [key, val] = cookieParts.split("=");

// 更新缓存
const cookies = cookieCache.split("; ");
const index = cookies.findIndex((c) => c.startsWith(key + "="));
if (index !== -1) {
cookies[index] = cookieParts;
} else {
cookies.push(cookieParts);
}
cookieCache = cookies.join("; ");

return value;
},
});
})();
```

---

## Storage Hook

### Hook LocalStorage

```javascript
(function () {
const originalSetItem = localStorage.setItem;
const originalGetItem = localStorage.getItem;
const originalRemoveItem = localStorage.removeItem;

localStorage.setItem = function (key, value) {
console.log(` [LocalStorage] Set: ${key} = ${value}`);
console.trace();
return originalSetItem.apply(this, arguments);
};

localStorage.getItem = function (key) {
const value = originalGetItem.apply(this, arguments);
console.log(` [LocalStorage] Get: ${key} = ${value}`);
return value;
};

localStorage.removeItem = function (key) {
console.log(` [LocalStorage] Remove: ${key}`);
return originalRemoveItem.apply(this, arguments);
};
})();
```

### Hook SessionStorage

```javascript
// 同 LocalStorage，将 localStorage 替换为 sessionStorage
(function () {
const originalSetItem = sessionStorage.setItem;
const originalGetItem = sessionStorage.getItem;

sessionStorage.setItem = function (key, value) {
console.log(` [SessionStorage] Set: ${key} = ${value}`);
return originalSetItem.apply(this, arguments);
};

sessionStorage.getItem = function (key) {
const value = originalGetItem.apply(this, arguments);
console.log(` [SessionStorage] Get: ${key} = ${value}`);
return value;
};
})();
```

---

## 加密函数 Hook

### Hook CryptoJS

```javascript
(function () {
if (window.CryptoJS) {
// Hook MD5
const originalMD5 = CryptoJS.MD5;
CryptoJS.MD5 = function (...args) {
console.log(" [CryptoJS.MD5] Input:", args[0].toString());
const result = originalMD5.apply(this, args);
console.log(" [CryptoJS.MD5] Output:", result.toString());
debugger; // 自动断点
return result;
};

// Hook AES.encrypt
const originalAESEncrypt = CryptoJS.AES.encrypt;
CryptoJS.AES.encrypt = function (message, key, cfg) {
console.log(" [CryptoJS.AES.encrypt]");
console.log(" Message:", message.toString());
console.log(" Key:", key.toString());
console.log(" Config:", cfg);
const result = originalAESEncrypt.apply(this, arguments);
console.log(" Result:", result.toString());
debugger;
return result;
};

// Hook AES.decrypt
const originalAESDecrypt = CryptoJS.AES.decrypt;
CryptoJS.AES.decrypt = function (ciphertext, key, cfg) {
console.log(" [CryptoJS.AES.decrypt]");
console.log(" Ciphertext:", ciphertext.toString());
console.log(" Key:", key.toString());
const result = originalAESDecrypt.apply(this, arguments);
console.log(" Decrypted:", result.toString(CryptoJS.enc.Utf8));
debugger;
return result;
};
}
})();
```

### Hook Web Crypto API

```javascript
(function () {
const originalSubtle = window.crypto.subtle;

const hookCryptoMethod = (methodName) => {
const original = originalSubtle[methodName];
originalSubtle[methodName] = async function (...args) {
console.log(` [crypto.subtle.${methodName}]`, args);
const result = await original.apply(this, args);
console.log(` [crypto.subtle.${methodName}] Result:`, result);
return result;
};
};

hookCryptoMethod("encrypt");
hookCryptoMethod("decrypt");
hookCryptoMethod("sign");
hookCryptoMethod("verify");
hookCryptoMethod("digest");
})();
```

---

## JSON Hook

### Hook JSON.stringify

```javascript
(function () {
const originalStringify = JSON.stringify;

JSON.stringify = function (obj, replacer, space) {
console.log(" [JSON.stringify] Input:", obj);
console.trace();

const result = originalStringify.apply(this, arguments);
console.log(" [JSON.stringify] Output:", result);

return result;
};
})();
```

### Hook JSON.parse

```javascript
(function () {
const originalParse = JSON.parse;

JSON.parse = function (text, reviver) {
console.log(" [JSON.parse] Input:", text);

const result = originalParse.apply(this, arguments);
console.log(" [JSON.parse] Output:", result);

return result;
};
})();
```

---

## 定时器 Hook

### Hook setTimeout

```javascript
(function () {
const originalSetTimeout = window.setTimeout;

window.setTimeout = function (callback, delay, ...args) {
console.log(`⏰ [setTimeout] Delay: ${delay}ms`);
console.log(
`⏰ [setTimeout] Callback:`,
callback.toString().substring(0, 100)
);
console.trace();

return originalSetTimeout.apply(this, arguments);
};
})();
```

### Hook setInterval

```javascript
(function () {
const originalSetInterval = window.setInterval;

window.setInterval = function (callback, delay, ...args) {
console.log(`⏰ [setInterval] Interval: ${delay}ms`);
console.log(
`⏰ [setInterval] Callback:`,
callback.toString().substring(0, 100)
);

return originalSetInterval.apply(this, arguments);
};
})();
```

---

## WebSocket Hook

```javascript
(function () {
const originalWebSocket = window.WebSocket;

window.WebSocket = function (url, protocols) {
console.log(` [WebSocket] Connecting to: ${url}`);

const ws = new originalWebSocket(url, protocols);

// Hook send
const originalSend = ws.send;
ws.send = function (data) {
console.log(" [WebSocket] Send:", data);
return originalSend.apply(this, arguments);
};

// Hook onmessage
ws.addEventListener("message", function (event) {
console.log(" [WebSocket] Message:", event.data);
});

// Hook onopen
ws.addEventListener("open", function () {
console.log("✅ [WebSocket] Connected");
});

// Hook onerror
ws.addEventListener("error", function (error) {
console.log("❌ [WebSocket] Error:", error);
});

// Hook onclose
ws.addEventListener("close", function () {
console.log(" [WebSocket] Closed");
});

return ws;
};
})();
```

---

## 反调试绕过

### 绕过 debugger

```javascript
// 方法一：重写 Function.prototype.constructor
(function () {
const originalConstructor = Function.prototype.constructor;

Function.prototype.constructor = function (...args) {
// 检查是否包含 'debugger'
const code = args[args.length - 1];
if (typeof code === "string" && code.includes("debugger")) {
console.log(" [Anti-Debug] Blocked debugger");
// 返回空函数
return function () {};
}

return originalConstructor.apply(this, args);
};
})();

// 方法二：使用 Chrome DevTools
// 右键 debugger 行 -> "Never pause here"
```

### Hook console 检测绕过

```javascript
(function () {
// 某些网站通过检测 console 被打开来反调试
// 重写 console 方法返回固定值

const noop = function () {};
const originalConsole = { ...console };

window.console = {
log: noop,
debug: noop,
info: noop,
warn: noop,
error: noop,
// 保留原始 console 供我们使用
_original: originalConsole,
};

// 使用：window.console._original.log('message');
})();
```

---

## 综合 Hook 脚本

### 一键监控所有关键 API

```javascript
(function () {
console.log(" Universal Hook Script Loaded");

// 1. Network
const originalFetch = window.fetch;
window.fetch = async function (...args) {
console.log(` [Fetch]`, args);
const response = await originalFetch.apply(this, args);
const clone = response.clone();
const text = await clone.text();
console.log(` [Fetch] Response:`, text.substring(0, 200));
return response;
};

// 2. Cookie
let cookieCache = document.cookie;
Object.defineProperty(document, "cookie", {
get: () => (console.log(" [Cookie] Read"), cookieCache),
set: (v) => (console.log(" [Cookie] Write:", v), (cookieCache = v), v),
});

// 3. LocalStorage
const originalSetItem = localStorage.setItem;
localStorage.setItem = function (k, v) {
console.log(` [LocalStorage] ${k} = ${v}`);
return originalSetItem.apply(this, arguments);
};

// 4. JSON
const originalStringify = JSON.stringify;
JSON.stringify = function (obj) {
console.log(" [JSON.stringify]", obj);
return originalStringify.apply(this, arguments);
};

// 5. CryptoJS (如果存在)
if (window.CryptoJS) {
const originalMD5 = CryptoJS.MD5;
CryptoJS.MD5 = function (...args) {
const result = originalMD5.apply(this, args);
console.log(` [MD5] ${args[0]} => ${result}`);
return result;
};
}

console.log("✅ All hooks installed!");
})();
```

---

## 使用建议

### 在 DevTools Console 中执行

1. 打开 DevTools
2. 切换到 Console 标签
3. 粘贴 Hook 脚本
4. 回车执行
5. 刷新页面或触发操作

### 保存为 Snippet

1. DevTools -> Sources -> Snippets
2. 新建 Snippet
3. 粘贴 Hook 脚本
4. `Ctrl+Enter` 执行

### 使用浏览器插件

可以将 Hook 脚本注入到 Tampermonkey 等插件中，实现自动加载。

---

## 高级 Hook 技术

### 使用 Proxy 实现深度拦截

ES6 Proxy 提供了更强大的拦截能力，可以拦截对象的所有操作：

```javascript
// Hook 整个对象的所有方法
function deepHookObject(obj, name = "Object") {
return new Proxy(obj, {
get(target, prop, receiver) {
const value = Reflect.get(target, prop, receiver);

// 如果是函数，则包装它
if (typeof value === "function") {
return new Proxy(value, {
apply(fn, thisArg, args) {
console.log(` [${name}.${String(prop)}] 调用`);
console.log(" 参数:", args);

const result = Reflect.apply(fn, thisArg, args);

console.log(" 返回:", result);
return result;
},
});
}

return value;
},

set(target, prop, value, receiver) {
console.log(` [${name}.${String(prop)}] 设置为:`, value);
return Reflect.set(target, prop, value, receiver);
},
});
}

// 使用示例：Hook 整个 localStorage
window.localStorage = deepHookObject(window.localStorage, "localStorage");
```

### 性能优化：条件 Hook

避免过度日志输出影响性能：

```javascript
// 条件 Hook - 只记录特定条件
(function () {
const originalFetch = window.fetch;
const INTERESTING_URLS = ["/api/user", "/api/login", "/api/data"];

window.fetch = async function (...args) {
const url = args[0];
const shouldLog = INTERESTING_URLS.some((pattern) => url.includes(pattern));

if (shouldLog) {
console.log(" [Fetch]", url);
}

const response = await originalFetch.apply(this, args);

if (shouldLog) {
const clone = response.clone();
const text = await clone.text();
console.log(" [Response]", text.substring(0, 200));
}

return response;
};
})();
```

### 函数调用栈追踪

精确定位函数调用来源：

```javascript
function hookWithStackTrace(obj, methodName) {
const original = obj[methodName];

obj[methodName] = function (...args) {
console.log(` [${methodName}] 被调用`);
console.log("参数:", args);

// 获取调用栈
const stack = new Error().stack;
const callerLine = stack.split("\n")[2]; // 第三行是调用者
console.log("调用位置:", callerLine.trim());

// 只在特定位置触发断点
if (callerLine.includes("encrypt")) {
debugger; // 条件断点
}

return original.apply(this, args);
};
}

// 示例：追踪 MD5 调用来源
if (window.CryptoJS) {
hookWithStackTrace(CryptoJS, "MD5");
}
```

### Hook 计数器和性能分析

```javascript
class FunctionProfiler {
constructor() {
this.stats = new Map();
}

hook(obj, methodName, displayName) {
const original = obj[methodName];
const stats = {
callCount: 0,
totalTime: 0,
minTime: Infinity,
maxTime: 0,
};

this.stats.set(displayName, stats);

obj[methodName] = function (...args) {
stats.callCount++;
const startTime = performance.now();

const result = original.apply(this, args);

const duration = performance.now() - startTime;
stats.totalTime += duration;
stats.minTime = Math.min(stats.minTime, duration);
stats.maxTime = Math.max(stats.maxTime, duration);

return result;
};
}

report() {
console.log("\n=== 函数性能报告 ===");
for (const [name, stats] of this.stats.entries()) {
console.log(`\n${name}:`);
console.log(` 调用次数: ${stats.callCount}`);
console.log(` 总耗时: ${stats.totalTime.toFixed(2)}ms`);
console.log(
` 平均耗时: ${(stats.totalTime / stats.callCount).toFixed(2)}ms`
);
console.log(` 最小耗时: ${stats.minTime.toFixed(2)}ms`);
console.log(` 最大耗时: ${stats.maxTime.toFixed(2)}ms`);
}
}
}

// 使用示例
const profiler = new FunctionProfiler();
profiler.hook(XMLHttpRequest.prototype, "send", "XHR.send");
profiler.hook(window, "fetch", "Fetch");

// 稍后查看报告
setTimeout(() => profiler.report(), 10000);
```

### 防御性 Hook - 避免被检测

有些网站会检测 Hook 痕迹，需要更隐蔽的方式：

```javascript
// 方法1: 使用 Proxy 保持函数特性
function stealthHook(obj, prop, handler) {
const original = obj[prop];

// 创建 Proxy，保留原函数的所有属性
const proxy = new Proxy(original, {
apply(target, thisArg, args) {
handler.before && handler.before(args);
const result = Reflect.apply(target, thisArg, args);
handler.after && handler.after(result);
return result;
},
});

// 复制原函数的属性
Object.setPrototypeOf(proxy, Object.getPrototypeOf(original));
Object.defineProperty(obj, prop, {
value: proxy,
writable: true,
enumerable: false,
configurable: true,
});
}

// 方法2: 保持 toString() 一致
function invisibleHook(obj, methodName, callback) {
const original = obj[methodName];
const originalToString = original.toString();

obj[methodName] = function (...args) {
callback(args);
return original.apply(this, args);
};

// 伪造 toString
obj[methodName].toString = function () {
return originalToString;
};

// 隐藏 Proxy 特征
Object.defineProperty(obj[methodName], "name", {
value: original.name,
});
}
```

### 递归 Hook - 自动发现和 Hook 新方法

```javascript
// 自动 Hook 所有被调用的加密方法
(function () {
if (!window.CryptoJS) return;

const hookedMethods = new Set();

function autoHook(obj, prefix = "CryptoJS") {
return new Proxy(obj, {
get(target, prop) {
const value = target[prop];
const fullName = `${prefix}.${String(prop)}`;

if (typeof value === "function" && !hookedMethods.has(fullName)) {
hookedMethods.add(fullName);
console.log(` 自动 Hook: ${fullName}`);

return new Proxy(value, {
apply(fn, thisArg, args) {
console.log(` [${fullName}]`, args);
return Reflect.apply(fn, thisArg, args);
},
});
}

if (typeof value === "object" && value !== null) {
return autoHook(value, fullName);
}

return value;
},
});
}

window.CryptoJS = autoHook(window.CryptoJS);
})();
```

---

## Hook 框架封装

### 通用 Hook 管理器

```javascript
class HookManager {
constructor() {
this.hooks = [];
this.enabled = true;
}

// 注册 Hook
register(config) {
const { target, method, before, after, condition } = config;
const original = target[method];

if (!original) {
console.warn(`⚠️ 方法 ${method} 不存在`);
return;
}

const hookId = this.hooks.length;

target[method] = (...args) => {
if (!this.enabled) {
return original.apply(target, args);
}

// 条件检查
if (condition && !condition(args)) {
return original.apply(target, args);
}

// 前置处理
if (before) {
const modifiedArgs = before(args);
if (modifiedArgs !== undefined) {
args = modifiedArgs;
}
}

// 调用原函数
const result = original.apply(target, args);

// 后置处理
if (after) {
const modifiedResult = after(result, args);
if (modifiedResult !== undefined) {
return modifiedResult;
}
}

return result;
};

this.hooks.push({
id: hookId,
target,
method,
original,
});

return hookId;
}

// 移除 Hook
remove(hookId) {
const hook = this.hooks[hookId];
if (hook) {
hook.target[hook.method] = hook.original;
console.log(`✅ Hook ${hookId} 已移除`);
}
}

// 全局启用/禁用
toggle(enabled) {
this.enabled = enabled;
console.log(` Hook ${enabled ? "启用" : "禁用"}`);
}
}

// 使用示例
const hookManager = new HookManager();

// Hook Fetch 请求
hookManager.register({
target: window,
method: "fetch",
before: (args) => {
console.log(" Fetch:", args[0]);
},
after: async (response) => {
const clone = response.clone();
const text = await clone.text();
console.log(" Response:", text.substring(0, 100));
},
condition: (args) => {
// 只 Hook API 请求
return args[0].includes("/api/");
},
});

// 临时禁用所有 Hook
hookManager.toggle(false);
```

---

## 实战进阶案例

### 案例 1: 破解动态密钥生成算法

**场景**: 每次请求的加密密钥都不同，需要追踪密钥生成逻辑

```javascript
// Step 1: Hook 所有可能的密钥来源
const keyTracker = {
sources: [],

trackRandom() {
const originalRandom = Math.random;
Math.random = function () {
const value = originalRandom();
keyTracker.sources.push({ type: "Math.random", value });
return value;
};
},

trackTimestamp() {
const originalNow = Date.now;
Date.now = function () {
const value = originalNow();
keyTracker.sources.push({ type: "Date.now", value });
return value;
};
},

trackCrypto() {
if (window.crypto && window.crypto.getRandomValues) {
const original = window.crypto.getRandomValues.bind(window.crypto);
window.crypto.getRandomValues = function (array) {
const result = original(array);
keyTracker.sources.push({
type: "crypto.getRandomValues",
value: Array.from(array),
});
return result;
};
}
},

init() {
this.trackRandom();
this.trackTimestamp();
this.trackCrypto();
console.log(" 密钥追踪器已启动");
},

analyze() {
console.log("=== 密钥来源分析 ===");
console.log(`总计 ${this.sources.length} 个随机源`);
this.sources.forEach((source, i) => {
console.log(`${i + 1}. ${source.type}:`, source.value);
});
},
};

keyTracker.init();

// 触发加密操作后
setTimeout(() => keyTracker.analyze(), 5000);
```

### 案例 2: 绕过虚拟机检测

某些网站使用虚拟机（VM）执行关键代码以防止分析：

```javascript
// 检测并 Hook VM 环境
(function () {
// 常见的 VM 特征
const vmPatterns = [
"eval",
"Function",
"with",
"Proxy",
"_0x", // 混淆特征
"constructor",
];

// Hook Function 构造函数
const OriginalFunction = Function;
window.Function = new Proxy(OriginalFunction, {
construct(target, args) {
const code = args[args.length - 1];

// 检查是否是 VM 代码
const isVM = vmPatterns.some((pattern) => code.includes(pattern));

if (isVM) {
console.log(" 检测到 VM 代码执行");
console.log("代码片段:", code.substring(0, 200));
debugger; // 断点
}

return Reflect.construct(target, args);
},
});

console.log("✅ VM 检测 Hook 已安装");
})();
```

### 案例 3: 参数污染检测

自动检测哪些参数对加密结果有影响：

```javascript
class ParameterAnalyzer {
constructor(targetFunction, referenceOutput) {
this.targetFunction = targetFunction;
this.referenceOutput = referenceOutput;
this.results = [];
}

// 测试单个参数的影响
testParameter(baseParams, paramIndex, testValue) {
const testParams = [...baseParams];
testParams[paramIndex] = testValue;

const output = this.targetFunction(...testParams);
const changed = output !== this.referenceOutput;

this.results.push({
paramIndex,
testValue,
output,
changed,
});

return changed;
}

// 自动化测试
analyze(baseParams) {
console.log(" 开始参数分析");

baseParams.forEach((param, index) => {
console.log(`\n测试参数 ${index}:`);

// 测试不同的值
const testValues = [
null,
undefined,
"",
0,
param + "_modified",
param.toUpperCase?.(),
].filter((v) => v !== undefined);

testValues.forEach((testValue) => {
const changed = this.testParameter(baseParams, index, testValue);
console.log(
` ${JSON.stringify(testValue)} => ${
changed ? "✅ 影响输出" : "❌ 无影响"
}`
);
});
});

this.report();
}

report() {
console.log("\n=== 分析报告 ===");
const criticalParams = this.results
.filter((r) => r.changed)
.map((r) => r.paramIndex);

console.log("关键参数索引:", [...new Set(criticalParams)]);
}
}

// 使用示例
// 假设发现了加密函数 encryptData(timestamp, userId, data)
const analyzer = new ParameterAnalyzer(
window.encryptData,
window.encryptData(1638360000, "123", "test")
);

analyzer.analyze([1638360000, "123", "test"]);
```

---

## 调试集成技巧

### 条件日志

只在满足条件时输出日志，减少噪音：

```javascript
class ConditionalLogger {
constructor(condition) {
this.condition = condition;
this.buffer = [];
}

log(...args) {
if (this.condition()) {
console.log(...args);
} else {
this.buffer.push(args);
}
}

flush() {
console.log("=== 缓冲日志 ===");
this.buffer.forEach((args) => console.log(...args));
this.buffer = [];
}
}

// 只在特定URL时记录
const logger = new ConditionalLogger(() => {
return window.location.href.includes("/login");
});

logger.log("这条日志只在 /login 页面显示");
```

### 自动化断点注入

```javascript
// 在加密函数的关键参数处自动断点
function autoBreakpoint(obj, method, paramChecker) {
const original = obj[method];

obj[method] = function (...args) {
if (paramChecker(args)) {
console.log(" 触发自动断点");
console.log("参数:", args);
debugger; // 自动断点
}

return original.apply(this, args);
};
}

// 示例：当密钥包含特定字符串时断点
autoBreakpoint(CryptoJS.AES, "encrypt", (args) => {
const key = args[1]?.toString();
return key && key.includes("secret");
});
```

---

## 最佳实践总结

### 1. Hook 时机

- **尽早注入**: 在页面脚本执行前注入 Hook（使用浏览器扩展或代理）
- **异步 Hook**: 对于动态加载的库，使用 MutationObserver 监听

```javascript
// 监听动态加载的 CryptoJS
const observer = new MutationObserver(() => {
if (window.CryptoJS && !window._cryptoHooked) {
window._cryptoHooked = true;
// 安装 Hook
console.log("✅ CryptoJS 已加载，安装 Hook");
}
});

observer.observe(document, { childList: true, subtree: true });
```

### 2. 性能考虑

- 避免在 Hook 中执行耗时操作
- 使用条件判断减少不必要的日志
- 考虑使用 `requestIdleCallback` 延迟非关键日志

### 3. 错误处理

```javascript
function safeHook(obj, method, callback) {
const original = obj[method];

obj[method] = function (...args) {
try {
callback(args);
} catch (error) {
console.error("Hook 错误:", error);
// 继续执行原函数
}

return original.apply(this, args);
};
}
```

### 4. 清理和恢复

始终保存原函数引用，便于恢复：

```javascript
window._originalFunctions = window._originalFunctions || {};

function installHook(obj, method, hook) {
const key = `${obj.constructor.name}.${method}`;
window._originalFunctions[key] = obj[method];
obj[method] = hook(obj[method]);
}

function uninstallAllHooks() {
for (const [key, original] of Object.entries(window._originalFunctions)) {
const [objName, method] = key.split(".");
window[objName][method] = original;
}
console.log("✅ 所有 Hook 已移除");
}
```

---

## 工具推荐

| 工具 | 用途 | 链接 |
| ---------------------- | ----------------------------- | ------------------------------------------ |
| **Tampermonkey** | 用户脚本管理，自动注入 Hook | https://www.tampermonkey.net/ |
| **Proxy SwitchyOmega** | 代理切换，配合 mitmproxy 注入 | https://github.com/FelisCatus/SwitchyOmega |
| **Chrome DevTools** | 原生断点和监控 | 内置 |
| **Frida** | 动态插桩框架（适用于 App） | https://frida.re/ |

---

## 商业化动态分析平台对比

对于企业级项目，商业化的动态分析和 Hook 平台可以显著提升效率和可靠性。以下是市场主流方案对比。

### 1. 专业动态分析工具

#### Frida（开源，企业级可用）

**定位**: 最流行的动态插桩框架

**核心优势**:

- 支持 JavaScript/Python/Swift 等多语言
- 跨平台（iOS/Android/Windows/macOS/Linux）
- 活跃的社区和丰富的脚本库
- 企业可免费使用

**应用场景**:

- 移动应用逆向
- Web 应用动态分析
- 恶意软件分析
- 安全研究

**GitHub**: https://github.com/frida/frida

**学习成本**: 中等

**企业使用**:

- ✅ 完全免费
- ✅ 无使用限制
- ✅ 可商业化
- ❌ 需要技术团队维护

---

#### Charles Proxy（商业网络调试工具）

**定位**: HTTP/HTTPS 抓包和调试

**功能**:

- SSL 证书中间人拦截
- 请求/响应修改
- 断点和重放
- 流量限速模拟

**价格**:

- 个人许可: $50（一次性）
- 商业许可: $100+

**优势**:

- 图形化界面，易用性强
- 稳定可靠
- 跨平台支持

**劣势**:

- 仅限网络层 Hook
- 无法 Hook JavaScript 函数

**官网**: https://www.charlesproxy.com/

**适用**: 网络层分析、API 调试

---

#### Burp Suite Professional

**定位**: Web 安全测试专业工具

**核心功能**:

- HTTP/HTTPS 代理拦截
- 扫描器（主动/被动）
- Intruder（自动化攻击）
- Repeater（请求重放）
- **Burp 扩展**：支持 JavaScript Hook 插件

**价格**:

- Professional: $449/年
- Enterprise: $3,999/年+

**JavaScript Hook 集成**:

```javascript
// 使用 Burp Extension: JS Link
// 可在Burp中直接注入Hook脚本
```

**官网**: https://portswigger.net/burp

**企业优势**:

- 强大的漏洞扫描
- 完整的测试报告
- 团队协作功能
- 专业技术支持

---

### 2. 浏览器自动化 Hook 平台

#### Sauce Labs Real Device Cloud

**功能**:

- 真实设备和浏览器云测试
- 自动化 Hook 脚本注入
- 实时交互调试
- 视频录制和日志

**定价**:

- Live Testing: $39/月起
- Automated Testing: $199/月起
- Enterprise: 定制化

**适用**:

- 跨浏览器 Hook 测试
- 移动端 JavaScript 调试
- CI/CD 集成

**官网**: https://saucelabs.com/

---

#### LambdaTest

**功能**:

- 3000+浏览器和操作系统组合
- 自动化测试和手动调试
- 集成开发者工具

**定价**:

- Live: $15/月起
- Automation: $99/月起

**相比 Sauce Labs 更便宜**

**官网**: https://www.lambdatest.com/

---

### 3. 企业级应用监控（APM）集成 Hook

#### Datadog RUM（Real User Monitoring）

**功能**:

- 前端性能监控
- JavaScript 错误追踪
- 自定义 Hook 注入
- 用户行为分析

**技术实现**:

```javascript
// Datadog 自动注入 Hook
import { datadogRum } from "@datadog/browser-rum";

datadogRum.init({
applicationId: "<YOUR_APP_ID>",
clientToken: "<YOUR_CLIENT_TOKEN>",
// 自动Hook XHR/Fetch
trackInteractions: true,
trackFrustrations: true,
});
```

**价格**: $0.90/1000 sessions 起

**官网**: https://www.datadoghq.com/

**企业价值**: 生产环境 Hook + 监控一体化

---

#### New Relic Browser

**功能**:

- 浏览器性能监控
- JavaScript 错误 Hook
- AJAX 请求自动追踪
- Session Trace

**价格**: $75/月起

**官网**: https://newrelic.com/

---

### 4. 商业 Hook 脚本库和平台

#### GreaseSpot（Tampermonkey 商业版）

**类型**: 用户脚本管理器（免费+商业支持）

**企业功能**:

- 脚本签名和安全审计
- 企业脚本库管理
- 部署自动化

**价格**:

- 个人免费
- 企业支持: 定制化定价

**官网**: https://www.greasespot.net/

---

#### Requestly（企业级请求修改）

**功能**:

- HTTP 请求拦截和修改
- JavaScript 注入
- Header 修改
- Mock API

**定价**:

- Free: 基础功能
- Professional: $12/月
- Team: $25/月/用户
- Enterprise: 定制化

**独特优势**:

- 云端规则同步
- 团队协作
- 规则市场

**官网**: https://requestly.io/

---

### 5. 动态分析即服务（DaaS）

#### Zimperium zScan（移动应用安全）

**功能**:

- 自动化 JavaScript Hook
- 运行时威胁检测
- API 安全分析
- 行为分析

**适用**: iOS/Android 应用安全测试

**价格**: 企业定价（$10,000+/年）

**官网**: https://www.zimperium.com/

---

### 6. 成本效益对比

#### 场景 1: 个人学习/研究

**推荐方案**:

- Chrome DevTools（免费）
- 手写 Hook 脚本
- Tampermonkey（免费）

**总成本**: **$0**

---

#### 场景 2: 小团队 Web 逆向项目

**推荐方案**:

- Burp Suite Professional（$449/年）
- Charles Proxy（$50 一次性）
- 自定义 Hook 脚本库

**总成本**: **~$500 第一年，$449 后续/年**

**ROI**: 专业工具节省时间，提高效率

---

#### 场景 3: 企业安全团队

**推荐方案**:

- Burp Suite Enterprise（$3,999/年）
- Datadog RUM（$1,000+/月，生产监控）
- 专业咨询服务（按需）

**总成本**: **$15,000-50,000/年**

**企业价值**:

- 合规审计报告
- 24/7 技术支持
- 团队协作功能
- 生产环境监控

---

### 7. 开源 vs 商业决策矩阵

| 因素 | 推荐开源 | 推荐商业 |
| ------------ | ------------------ | --------------------- |
| **预算** | < $1,000/年 | > $5,000/年 |
| **团队规模** | < 3 人 | > 5 人 |
| **项目类型** | 一次性逆向 | 持续安全测试 |
| **技术能力** | 高（能自己写脚本） | 中低（需要 GUI 工具） |
| **合规要求** | 无 | 需要审计报告 |
| **支持需求** | 社区就够 | 需要商业支持 |

---

### 8. 云端 Hook 服务（新兴）

#### Browserless.io Hook Support

**功能**:

- 云端浏览器 Hook 注入
- 无需本地环境
- API 调用方式

**示例**:

```javascript
const response = await fetch("https://chrome.browserless.io/function", {
method: "POST",
headers: { "Content-Type": "application/json" },
body: JSON.stringify({
code: `
// Hook代码
const original = XMLHttpRequest.prototype.send;
XMLHttpRequest.prototype.send = function(...args) {
console.log('Hooked:', args);
return original.apply(this, args);
};
`,
context: {
url: "https://example.com",
},
}),
});
```

**价格**: $29-299/月（见 automation_scripts.md）

---

### 9. AI 辅助 Hook 开发

#### GitHub Copilot for Security

**功能**:

- 自动生成 Hook 脚本
- 安全漏洞检测
- 代码补全

**价格**: $100/年（个人）

**示例 Prompt**:

```javascript
// Prompt: Write a hook for XMLHttpRequest that logs all requests
// Copilot 自动生成完整Hook代码
```

---

#### ChatGPT/Claude 辅助

**应用**:

- 解释复杂 Hook 逻辑
- 生成定制化 Hook 脚本
- 调试 Hook 代码

**成本**: $20/月（ChatGPT Plus）或按需 API 调用

---

### 10. 实战工具链推荐

#### 初学者（$0 成本）

**工具组合**:

1. Chrome DevTools（免费）
2. Tampermonkey（免费）
3. 本文档的 Hook 脚本库

**能力**:

- 基础 Hook
- 网络请求监控
- Cookie/Storage 操作

---

#### 专业人士（< $1,000/年）

**工具组合**:

1. Burp Suite Professional（$449/年）
2. Charles Proxy（$50 一次性）
3. GitHub Copilot（$100/年）
4. Requestly Pro（$144/年）

**总成本**: **~$750/年**

**能力提升**:

- 企业级拦截和修改
- 自动化 Hook 生成
- 团队协作

---

#### 企业团队（$10,000+/年）

**工具组合**:

1. Burp Suite Enterprise（$3,999/年）
2. Datadog RUM（$12,000/年）
3. 专业培训和咨询（按需）
4. 自建 Hook 平台（开发成本）

**ROI 分析**:

- 减少人工分析时间 60%+
- 提供审计报告
- 生产环境实时监控
- 降低安全风险

---

### 11. 行业案例参考

#### 金融行业（高合规要求）

**方案**:

- Burp Suite Enterprise
- Datadog APM
- 内部审计系统集成

**成本**: $50,000/年

**收益**: 满足 PCI DSS 合规要求

---

#### 安全公司（专业服务）

**方案**:

- Burp Suite + Frida
- 自研 Hook 框架
- 多语言支持

**成本**: $5,000/年（工具）+ 开发成本

**收益**: 可对外提供专业服务

---

#### 电商平台（业务监控）

**方案**:

- New Relic Browser
- 自定义 Hook 监控关键业务流程

**成本**: $15,000/年

**收益**: 提升用户体验，降低流失率

---

## 相关章节

- [调试技巧与断点设置](../03-Basic-Recipes/debugging_techniques.md)
- [JavaScript 反混淆](../04-Advanced-Recipes/javascript_deobfuscation.md)
- [浏览器开发者工具](../02-Tooling/browser_devtools.md)
- [加密算法识别脚本](crypto_detection_scripts.md)
- [浏览器自动化脚本](automation_scripts.md)
