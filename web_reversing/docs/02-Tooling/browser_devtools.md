# 浏览器开发者工具 (DevTools)

## 思考时刻

在深入学习 DevTools 之前，先思考：

1. **你真的会用 F12 吗？** 除了看 HTML 和 Network，你还用过哪些功能？
2. **断点调试的本质是什么？** 为什么说"会打断点的人，才算会调试"？
3. **动态 vs 静态：** 为什么说"动态调试比静态分析更有效"？
4. **实战场景：** 一个按钮点击后，发送了加密请求，你无法从代码里搜到请求 URL（因为是动态生成的）。你会如何定位到生成加密参数的代码？

掌握 DevTools，就是掌握了逆向的主动权。

---

## 概述

DevTools 是逆向工程师最顺手的兵器。除了基础的查看元素和发包,通过掌握一些高级调试技巧（Conditional Breakpoints, Local Overrides, Custom Snippets），我们可以大幅提升逆向效率。

---

## 1. Elements 面板

除了查看 DOM 结构，逆向中常用：

### DOM 断点 (DOM Breakpoints)

当不知道是谁修改了某个 DOM 元素（例如生成了验证码图片，或者插入了加密的 Token 输入框）时，使用它。

- **Subtree modifications**: 监听子节点变化。
- **Attribute modifications**: 监听属性变化（如 `class`, `src`, `value`）。
- **Node removal**: 监听节点被删除。

> **技巧**: 断下后，查看 Call Stack (调用栈)，通常能直接定位到操作 DOM 的 JS 代码。

---

## 2. Console 面板

不仅仅是打印日志。

### 实用指令 (Console API)

- `debug(fn)`: 当指定函数 `fn` 被调用时，自动断点。
- `monitor(fn)`: 当 `fn` 被调用时，自动 Log 输出参数。
- `queryObjects(Constructor)`: **强力工具**。查找所有该构造函数的实例。
- 例如：`queryObjects(WebSocket)` 可以列出当前页面所有的 WebSocket 连接对象。
- `getEventListeners(node)`: 获取 DOM 节点绑定的所有事件监听器。

### 当前上下文 (Context)

Console 左上角可以选择 Execution Context。如果网页使用了 iframe 或者 Web Worker，记得切换上下文，否则访问不到里面的变量。

---

## 3. Sources 面板

调试的核心战场。

### XHR/Fetch Breakpoints

在右侧面板勾选 "XHR/fetch breakpoints"，输入 URL 关键词（如 `/login`, `sign`）。

- 当发生包含该关键词的网络请求时，会在 `send()` 或 `fetch()` 调用处断下。

### Event Listener Breakpoints

不想手动找 DOM 绑定事件？直接勾选 `Mouse -> click` 或 `Keyboard -> keydown`。

### Snippets (代码片段)

在 "Snippets" 标签页可以保存常用的 Hook 脚本。

- **优点**: 跨页面通用，通过 `Ctrl+Enter` 快速执行。
- **场景**: 注入通用的 Cookie Hook, Debugger Bypass 脚本。

### Local Overrides (本地替换)

**逆向神器**。允许你修改线上的 JS 文件并在本地保存，刷新页面后依然生效。

1. 除了 "Overrides" 标签页，选择一个本地文件夹。
2. 在 "Network" 或 "Sources" 面板找到 JS 文件，右键 -> "Save for overrides"。
3. 直接编辑代码，Ctrl+S 保存。
4. **用途**: 删除混淆代码中的反调试逻辑、注入 Log 代码、修改加密函数的返回值。

---

## 4. Network 面板

### Initiator (发起者)

在请求列表中，鼠标悬停在 "Initiator" 列。

- 它会显示这就请求的调用栈链。点击蓝色的文件名，直接跳转到发包的 JS 代码。

### Replay XHR (重放)

右键请求 -> "Replay XHR"。快速重发请求，用于测试签名的时效性。

### Block Request URL (屏蔽请求)

右键请求 -> "Block Request URL"。

- **用途**: 屏蔽某些第三方的监控脚本、广告脚本，或者屏蔽加载 Wasm 文件以强制降级到 JS 版本（如果网站有降级逻辑）。

---

## 5. Application 面板

### Storage

直接查看和修改 LocalStorage, SessionStorage, Cookies, IndexedDB。

### Service Workers

有些网站使用 SW 来拦截请求或做缓存。如果调试时发现 Network 面板行为怪异（如请求直接从 ServiceWorker 返回），可以在 "Service Workers" 标签页勾选 "Bypass for network" 或直接 "Unregister"。

---

## 总结

熟练使用 DevTools 的高级功能，可以让你在没有源码的情况下，快速切入业务逻辑的核心。

- 找不到入口？用 **Event Listener / XHR Breakpoints**。
- 找到了混淆代码想改？用 **Local Overrides**。
- 想找隐藏的对象？用 **Console `queryObjects`**。
