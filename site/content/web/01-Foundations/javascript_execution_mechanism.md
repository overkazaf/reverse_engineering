---
title: "JavaScript 执行机制"
date: 2024-04-25
weight: 10
---

# JavaScript 执行机制

## 概述

深入理解 JavaScript 的执行机制（事件循环、V8 引擎、编译原理）对于处理复杂的反调试脚本、分析异步加密逻辑以及理解混淆代码的控制流至关重要。

---

## 1. 单线程与事件循环 (Event Loop)

JavaScript 是单线程的（主线程），为了不阻塞 UI 渲染，它采用了**事件循环**机制来处理异步任务。

### 宏任务 (MacroTask) vs 微任务 (MicroTask)

这是面试题常客，也是逆向分析异步代码执行顺序的关键。

- **MacroTask (宏任务)**: `setTimeout`, `setInterval`, `setImmediate` (Node), I/O, UI Rendering.
- **MicroTask (微任务)**: `Promise.then`, `process.nextTick` (Node), `MutationObserver`.

### 执行顺序

1. 执行同步代码（Main Script）。
2. 执行所有 **MicroTasks**（清空微任务队列）。
3. 执行 **一个** MacroTask。
4. 执行所有 **MicroTasks**。
5. 更新 UI 渲染。
6. 回到步骤 3。

### [Reverse Engineering Context] 反调试陷阱

很多反调试代码利用 MicroTask 的高优先级来卡死浏览器或者检测调试器。

```javascript
// 示例：利用 Event Loop 差异检测环境或制造时序混淆
console.log("Start");

setTimeout(() => {
console.log("Timeout"); // 宏任务
}, 0);

Promise.resolve().then(() => {
console.log("Promise"); // 微任务
// 恶意代码可能插在这里，优先于 setTimeout 执行
});

console.log("End");

// 输出: Start -> End -> Promise -> Timeout
```

如果在 `setTimeout` 回调里下了断点，却发现在此之前某些变量已经被 `Promise` 改了，这就是原因。

---

## 2. V8 引擎架构

Chrome 和 Node.js 都使用 V8 引擎。

### 编译流水线

1. **Parse**: 源码 -> AST (抽象语法树)。
2. **Ignition (解释器)**: AST -> Bytecode (字节码) 并执行。
3. **TurboFan (优化编译器)**: 将热点 Bytecode 编译成高效的 Machine Code (机器码)。
4. **Deoptimization (去优化)**: 如果假设失败（例如变量类型变了），从机器码退回到字节码。

### [Reverse Engineering Context] JIT 带来的现象

- **热点函数**: 如果一个加密函数被频繁调用，它会被编译成极其高效的汇编。在 Profiler 中看到标红的可能是关键逻辑。
- **类型变换**: 混淆代码有时会故意频繁改变变量类型（Int -> String -> Object），强迫 V8 进行 Deoptimization，导致代码执行变慢，干扰性能分析，甚至利用 JIT Bug。

---

## 3. 作用域链与上下文

### 执行上下文 (Execution Context)

每当 JS 引擎执行代码时，都会创建上下文：

- **Global Context**: 全局。
- **Function Context**: 函数调用时创建。

### 变量对象 (VO) 与 活动对象 (AO)

- 存储函数内的 arguments, 变量, 内部函数。
- 逆向时，Scopes 面板看到的 Closure 就是保存了外部函数 AO 的引用。

---

## 4. 垃圾回收 (Garbage Collection)

V8 使用分代回收算法：

- **新生代 (New Space)**: 存活时间短的对象，使用 Scavenge 算法 (复制清除)。
- **老生代 (Old Space)**: 存活时间长的对象，使用 Mark-Sweep (标记清除) 和 Mark-Compact (标记整理)。

### [Reverse Engineering Context] 内存泄漏

如果发现网页内存持续飙升，可能是反爬虫脚本在故意制造内存压力，或者由于频繁创建未销毁的闭包导致。

---

## 5. Eval 与 Function 构造器

动态执行代码的两种方式，也是混淆的重灾区。

```javascript
eval("var a = 1;"); // 访问本地作用域
new Function("return 1")(); // 只能访问全局作用域
```

**对抗**: Hook `eval` 和 `Function` 是获取解密后代码的最快路径。

```javascript
// Hook eval
window._eval = window.eval;
window.eval = function (str) {
console.log("[eval]", str);
return window._eval(str);
};

// Hook Function
// 注意：Function 不仅仅是函数，它本身也是构造器
var _Function = window.Function;
window.Function = function (...args) {
let body = args[args.length - 1];
console.log("[Function]", body);
return _Function.apply(this, args);
};
// 保持原型链，防止检测
window.Function.prototype = _Function.prototype;
window.Function.prototype.constructor = window.Function;
```

---

## 总结

理解 JS 执行机制让我们不仅能看懂代码，还能看懂代码“背后”的行为——为什么这里的断点进不去？为什么这段代码执行顺序和想的不一样？为什么内存一直在涨？这些问题的答案都在 Event Loop 和 V8 引擎里。
