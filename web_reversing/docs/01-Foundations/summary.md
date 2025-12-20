# 00-Foundations Summary

本章节涵盖了 Web 逆向工程所需的基础知识。

---

## 💭 开始前的思考

在打基础之前，先想想这些问题：

1. **你真的了解 JavaScript 吗？** 为什么说"不懂闭包，就不算懂 JavaScript"？
2. **浏览器是如何执行代码的？** 为什么有时候 `console.log` 的顺序和你预期的不一样？
3. **同源策略是保护用户还是限制开发者？** 为什么说它是"Web 安全的基石"？
4. **加密传输就安全了吗？** HTTPS 能防止抓包吗？能防止中间人攻击吗？

基础不牢，地动山摇。这些问题的答案，决定了你能在逆向这条路上走多远。

---

## 主要内容

- **[JavaScript 基础](./javascript_basics.md)**: 核心语法、闭包、原型链、异步编程。
- **[JavaScript 执行机制](./javascript_execution_mechanism.md)**: 事件循环 (Event Loop)、宏任务与微任务、V8 引擎架构。
- **[Web API 与 Ajax](./web_api_and_ajax.md)**: XHR, Fetch, WebSocket, Canvas, Navigator 等关键 API 的 Hook 与拦截。
- **[DOM 与 BOM](./dom_and_bom.md)**: DOM 树操作、事件监听器定位、反调试检测 (Window/Console)。
- **[浏览器架构](./browser_architecture.md)**: 多进程模型、渲染流水线、无头浏览器检测。
- **[Cookie 与 Storage](./cookie_and_storage.md)**: Cookie 属性 (HttpOnly), LocalStorage, IndexedDB 的逆向分析。
- **[用于 HTTP/HTTPS](./http_https_protocol.md)**: 协议结构、状态码、抓包分析。
- **[TLS/SSL 握手](./tls_ssl_handshake.md)**: 握手流程、JA3 指纹、证书固定 (Pinning) 绕过。
- **[CORS 与同源策略](./cors_and_same_origin_policy.md)**: SOP 限制、CORS 绕过技巧。
- **[WebAssembly 基础](./webassembly_basics.md)**: Wasm 格式、静态分析与动态调试。
