---
title: "Hook (挂钩/劫持) 技术"
date: 2024-12-07
weight: 10
---

# Hook (挂钩/劫持) 技术

掌握 JavaScript Hook 技术，拦截和修改函数调用，无需破解即可获取关键数据。

---

## 配方信息

| 项目 | 说明 |
| ------------ | ------------------------------------------ |
| **难度** | ⭐⭐ (初级-中级) |
| **预计时间** | 30 分钟 - 2 小时 |
| **所需工具** | Chrome DevTools, Tampermonkey (可选) |
| **适用场景** | 函数拦截、参数监控、返回值修改、反调试绕过 |

---

## 📚 前置知识

在开始本配方之前，建议先掌握以下内容：

| 知识领域 | 重要程度 | 参考资料 |
|----------|---------|---------|
| JavaScript 基础 | 必需 | [JavaScript 基础](../01-Foundations/javascript_basics.md) |
| JavaScript 执行机制 | 推荐 | [JavaScript 执行机制](../01-Foundations/javascript_execution_mechanism.md) |
| DOM 与 BOM | 推荐 | [DOM 与 BOM](../01-Foundations/dom_and_bom.md) |
| Chrome DevTools | 推荐 | [浏览器开发者工具](../02-Tooling/browser_devtools.md) |

> 💡 **提示**: Hook 技术是 Web 逆向的**核心技能**，建议深入理解 JavaScript 的原型链和 `this` 绑定机制，这对编写高级 Hook 代码至关重要。

---

## 学习目标

完成本配方后，你将能够：

- ✅ 理解 Hook 技术的核心原理
- ✅ 使用覆盖法 Hook 全局函数
- ✅ 使用 Object.defineProperty Hook 属性
- ✅ 使用 Proxy 实现深度拦截
- ✅ Hook 常见 Web API (fetch, XHR, crypto)
- ✅ 编写防检测的 Hook 代码

---

## 思考时刻

在开始学习 Hook 技术之前，先思考几个问题：

1. **你打过电话窃听的比喻吗？** Hook 技术和电话窃听有什么相似之处？
2. **如果函数是一个黑盒**，你无法看到它的源码，怎么知道它在做什么？
3. **修改函数会破坏原有功能吗？** 如何在不影响业务的前提下"偷听"？
4. **实际场景：** 一个网站的登录接口发送了加密密码，你如何在不破解加密算法的情况下，拿到加密前的明文？

这些问题的答案，就是 Hook 技术的精髓。

---

## 核心概念

Hook（挂钩/劫持）技术是 JS 逆向的灵魂。核心思想是：**修改原函数的定义，插入我们的逻辑，再执行原函数**。这允许我们像中间人一样，在不破坏业务逻辑的前提下，查看和修改参数、返回值。

**Hook 的本质**:

```
原流程: 调用者 → 函数 → 返回值
Hook后: 调用者 → 我们的代码 → 原函数 → 我们的代码 → 返回值
```

---

## 1. 基础 Hook (覆盖法)

最简单粗暴的方法，直接把函数覆盖掉。

### 示例: Hook `alert`

```javascript
let _alert = window.alert; // 1. 保存原函数
window.alert = function (msg) {
// 2. 覆盖为新函数
console.log("[Hook] Alert called with:", msg); // 3. 插入逻辑
debugger; // 方便调试断下
return _alert.apply(this, arguments); // 4. 调用（劫持）原函数
};
// 5. 伪装 toString (可选，防止被检测)
window.alert.toString = function () {
return "function alert() { [native code] }";
};
```

---

## 2. Object.defineProperty (属性 Hook)

当某些变量是直接赋值而不是函数调用时（例如 `document.cookie = "xxx"`），我们需要 Hook 属性。

### 示例: Hook `cookie`

```javascript
(function () {
let cookieCache = document.cookie;
Object.defineProperty(document, "cookie", {
get: function () {
return cookieCache;
},
set: function (val) {
console.log("[Hook] Setting cookie:", val);
if (val.includes("token")) {
debugger;
}
cookieCache = val; // 实际上这里应该调用原生的 setter，比较复杂，通常用 Proxy 代替
return val;
},
});
})();
```

---

## 3. ES6 Proxy (代理 Hook)

Proxy 是最强大的 Hook 方式，它可以代理整个对象的所有操作（读、写、函数调用、遍历等）。

### 示例: 代理全局对象 window

```javascript
window = new Proxy(window, {
get: function (target, prop, receiver) {
if (prop === "v_account") {
console.log("[Hook] Reading v_account");
}
return Reflect.get(target, prop, receiver);
},
set: function (target, prop, value, receiver) {
if (prop === "v_account") {
console.log("[Hook] Setting v_account =", value);
debugger;
}
return Reflect.set(target, prop, value, receiver);
},
});
```

_注意：直接代理 window 可能会比较卡，且容易被检测。通常只代理特定的配置对象。_

---

## 4. 常见 Hook 点

记住这些“交通要道”，90% 的加密参数都会经过这里：

1. **JSON.stringify**: 无论什么加密参数，最后往往都要转成 JSON 发给服务器。
2. **JSON.parse**: 服务器返回的加密数据，解密后往往要转成 JSON 对象。
3. **String.prototype.split / slice**: 字符串操作函数。
4. **XMLHttpRequest.prototype.open / send**: 网络请求入口。
5. **Headers.prototype.append**: Fetch API 添加 Header 时。

---

## 总结

Hook 的本质是 **AOP (面向切面编程)**。在逆向中，它是我们切入黑盒系统的主要手段。时刻记得：Hook 代码要尽可能早地注入（注入时机在加载 DevTools 之前最佳，如使用油猴脚本或 Local Overrides）。
