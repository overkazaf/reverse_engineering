---
title: "Node.js 调试指南"
date: 2024-07-07
weight: 10
---

# Node.js 调试指南

## 概述

随着 Webpack、Vite 等构建工具的普及，前端代码的混淆和打包逻辑往往运行在 Node.js 环境中。逆向工程中，我们经常需要调试 Webpack 的 Loader/Plugin、分析服务端的 JS 逻辑、或者理解加密算法的实现。

Node.js 调试的核心是利用 Chrome DevTools Protocol (CDP) 提供的强大调试能力。

---

## 1. 基础调试 (--inspect-brk)

### 1.1 启动调试模式

**最通用的 Node.js 调试方法**：

```bash
# --inspect: 启动调试，但不暂停
node --inspect script.js

# --inspect-brk: 启动调试并在第一行暂停（推荐）
node --inspect-brk script.js

# 指定调试端口（默认 9229）
node --inspect-brk=5858 script.js

# 绑定到所有网络接口（允许远程调试）
node --inspect-brk=0.0.0.0:9229 script.js
```

### 1.2 连接 Chrome DevTools

**方法 1: chrome://inspect**

1. 启动调试模式后，终端显示：

```
Debugger listening on ws://127.0.0.1:9229/unique-id
```
2. 打开 Chrome 浏览器，访问 `chrome://inspect`
3. 在 "Remote Target" 下点击 "inspect" 按钮
4. 自动打开 DevTools，可以像调试网页一样调试 Node.js

**方法 2: DevTools URL**

```
chrome-devtools://devtools/bundled/js_app.html?ws=127.0.0.1:9229/unique-id
```

**方法 3: 自动发现**

- Settings → Discover network targets
- 添加 `localhost:9229`

### 1.3 调试示例

**脚本**: encrypt.js

```javascript
const crypto = require("crypto");

function encrypt(text, key) {
const cipher = crypto.createCipheriv("aes-128-cbc", key, Buffer.alloc(16));
let encrypted = cipher.update(text, "utf8", "hex");
encrypted += cipher.final("hex");
return encrypted;
}

const key = Buffer.from("1234567890abcdef");
const result = encrypt("Hello World", key);
console.log("加密结果:", result);
```

**调试**:

```bash
node --inspect-brk encrypt.js
```

在 DevTools 中：

1. 自动停在第一行
2. 在 `encrypt` 函数打断点
3. F8 继续执行 → 断在 `encrypt` 函数
4. 查看 Scope 面板中的 `text`, `key` 变量

---

## 2. 在 VSCode 中调试

### 2.1 JavaScript Debug Terminal

**最简单的方法**（无需配置）：

1. 打开 VSCode
2. 点击侧边栏 "Run and Debug" (Ctrl+Shift+D)
3. 点击 "JavaScript Debug Terminal"
4. 在终端中运行：

```bash
node script.js
```
5. VSCode 自动 Attach 并停在你打的断点上

### 2.2 launch.json 配置

**更灵活的配置方式**：

创建 `.vscode/launch.json`：

```json
{
"version": "0.2.0",
"configurations": [
{
"type": "node",
"request": "launch",
"name": "调试当前文件",
"skipFiles": ["<node_internals>/**"],
"program": "${file}",
"console": "integratedTerminal"
},
{
"type": "node",
"request": "launch",
"name": "调试 NPM Script",
"runtimeExecutable": "npm",
"runtimeArgs": ["run", "start"],
"console": "integratedTerminal"
},
{
"type": "node",
"request": "attach",
"name": "附加到进程",
"port": 9229,
"restart": true
}
]
}
```

**使用方法**:

1. F5 启动调试
2. 在代码中点击行号左侧打断点
3. 单步调试 (F10/F11)

### 2.3 调试 Webpack 打包过程

**场景**: 理解 Webpack 如何处理模块

**webpack.config.js**:

```javascript
module.exports = {
entry: "./src/index.js",
output: {
filename: "bundle.js",
path: __dirname + "/dist",
},
module: {
rules: [
{
test: /\.js$/,
use: "./my-custom-loader.js", // 自定义 Loader
},
],
},
};
```

**调试 Loader**:

`.vscode/launch.json`:

```json
{
"type": "node",
"request": "launch",
"name": "调试 Webpack",
"program": "${workspaceFolder}/node_modules/webpack/bin/webpack.js",
"args": ["--mode", "development"],
"console": "integratedTerminal"
}
```

在 `my-custom-loader.js` 中打断点：

```javascript
module.exports = function (source) {
debugger; // 自动断在这里
console.log("正在处理:", this.resourcePath);
// 你的 Loader 逻辑
return source;
};
```

---

## 3. 调试第三方包

### 3.1 调试 node_modules

**问题**: 第三方包代码在 `node_modules` 中，如何调试？

**方法 1: 禁用 skipFiles**

`.vscode/launch.json`:

```json
{
"skipFiles": [
// "<node_internals>/**", // 注释掉这行
// "node_modules/**" // 注释掉这行
]
}
```

**方法 2: 只跳过特定包**

```json
{
"skipFiles": [
"<node_internals>/**",
"node_modules/express/**", // 跳过 express
"node_modules/lodash/**" // 跳过 lodash
]
}
```

**方法 3: 使用 npm link**

```bash
# 进入第三方包目录
cd ~/projects/suspicious-package

# 创建全局链接
npm link

# 回到项目目录
cd ~/my-project

# 链接到本地包（替代 node_modules 中的版本）
npm link suspicious-package
```

现在可以直接在 `~/projects/suspicious-package` 中打断点调试。

### 3.2 调试加密库

**案例**: 逆向某加密算法

```javascript
// 在你的代码中
const crypto = require("crypto-js"); // 第三方加密库

// 1. 找到库的源码位置
// node_modules/crypto-js/core.js

// 2. 在 VSCode 中打开该文件，打断点

// 3. 运行调试
const encrypted = crypto.AES.encrypt("data", "key");
// → 自动断在 crypto-js 内部
```

---

## 4. 内存与性能分析

### 4.1 Heap Snapshot (堆快照)

**场景**: 查找内存泄漏或提取加密密钥

**方法 1: 通过 Chrome DevTools**

1. 连接到 Node.js 进程
2. Memory 面板 → "Take snapshot"
3. 搜索关键字（如 `secret`, `key`, `password`）
4. 查看字符串对象的值

**方法 2: 通过代码生成**

```javascript
const v8 = require("v8");
const fs = require("fs");

// 生成堆快照
const snapshot = v8.writeHeapSnapshot();
console.log("快照已保存到:", snapshot);

// 使用 Chrome DevTools 加载 .heapsnapshot 文件
```

**提取密钥示例**:

```javascript
// 1. 生成快照
const snapshot = v8.writeHeapSnapshot();

// 2. 在 Chrome DevTools 中加载
// 3. 搜索 "1234567890abcdef" (怀疑的密钥)
// 4. 找到对象，查看引用链，定位到代码位置
```

### 4.2 CPU Profiling (CPU 性能分析)

**场景**: 找出耗时的加密/混淆函数

**方法 1: 通过 Chrome DevTools**

1. Profiler 面板 → Start
2. 执行目标操作
3. Stop → 查看 Flame Chart

**方法 2: 通过代码**

```javascript
const inspector = require("inspector");
const fs = require("fs");

const session = new inspector.Session();
session.connect();

// 开始性能分析
session.post("Profiler.enable");
session.post("Profiler.start");

// 执行目标代码
expensiveEncryptFunction();

// 停止并保存
session.post("Profiler.stop", (err, { profile }) => {
fs.writeFileSync("profile.cpuprofile", JSON.stringify(profile));
console.log("性能分析已保存");
session.disconnect();
});
```

**分析结果**:

- 在 Chrome DevTools → Profiler → Load profile
- 查看 "Self Time" 最长的函数 → 这就是性能瓶颈
- 通常是加密/混淆的核心逻辑

### 4.3 Timeline (时间线分析)

```javascript
const { performance } = require("perf_hooks");

// 标记开始
performance.mark("encrypt-start");

encrypt(largeData);

// 标记结束
performance.mark("encrypt-end");

// 测量耗时
performance.measure("encrypt", "encrypt-start", "encrypt-end");

const measure = performance.getEntriesByName("encrypt")[0];
console.log(`加密耗时: ${measure.duration}ms`);
```

---

## 5. 调试异步代码

### 5.1 Promise 调试

**问题**: Promise 链中的错误难以追踪

**解决方案 1: async/await**

```javascript
// ❌ 难以调试
fetch(url)
.then((res) => res.json())
.then((data) => process(data))
.catch((err) => console.error(err));

// ✅ 易于调试
async function fetchData() {
const res = await fetch(url); // 断点
const data = await res.json(); // 断点
return process(data); // 断点
}
```

**解决方案 2: 启用 async stack traces**

在 Chrome DevTools 中：

- Settings → Enable async stack traces

### 5.2 调试事件循环

**查看当前事件循环状态**:

```javascript
const async_hooks = require("async_hooks");

const hooks = async_hooks.createHook({
init(asyncId, type, triggerAsyncId) {
console.log(`[Init] ${type} (id=${asyncId}, trigger=${triggerAsyncId})`);
},
before(asyncId) {
console.log(`[Before] ${asyncId}`);
},
after(asyncId) {
console.log(`[After] ${asyncId}`);
},
});

hooks.enable();

// 运行你的异步代码
setTimeout(() => {
console.log("Timeout executed");
}, 1000);
```

### 5.3 调试 setInterval 泄漏

**问题**: setInterval 没有正确清理，导致内存泄漏

**检测方法**:

```javascript
const timers = new Set();

const originalSetInterval = global.setInterval;
global.setInterval = function (...args) {
const timer = originalSetInterval(...args);
timers.add(timer);
console.log("[setInterval]", args[1], "已创建", timers.size, "个定时器");
return timer;
};

const originalClearInterval = global.clearInterval;
global.clearInterval = function (timer) {
timers.delete(timer);
console.log("[clearInterval] 已清理", timers.size, "个定时器剩余");
return originalClearInterval(timer);
};
```

---

## 6. 调试 ES6+ 特性

### 6.1 调试 ES Modules

**问题**: 使用 `import`/`export` 的模块无法直接调试

**方法 1: 原生支持 (Node.js 14+)**

```json
// package.json
{
"type": "module"
}
```

```bash
node --inspect-brk --experimental-modules script.mjs
```

**方法 2: 使用 babel-node**

```bash
npm install -D @babel/node @babel/core @babel/preset-env

# 调试
node --inspect-brk node_modules/@babel/node/bin/babel-node.js script.js
```

### 6.2 调试 TypeScript

**方法 1: ts-node**

```bash
npm install -D ts-node

# 调试
node --inspect-brk -r ts-node/register script.ts
```

**方法 2: Source Maps**

`tsconfig.json`:

```json
{
"compilerOptions": {
"sourceMap": true,
"outDir": "./dist"
}
}
```

`.vscode/launch.json`:

```json
{
"type": "node",
"request": "launch",
"name": "调试 TypeScript",
"program": "${workspaceFolder}/src/index.ts",
"preLaunchTask": "tsc: build - tsconfig.json",
"outFiles": ["${workspaceFolder}/dist/**/*.js"],
"sourceMaps": true
}
```

---

## 7. 远程调试

### 7.1 调试生产环境

**警告**: 生产环境调试需谨慎，可能影响性能

**启动服务器**:

```bash
# 服务器端（允许所有 IP 连接）
node --inspect=0.0.0.0:9229 server.js
```

**本地连接**:

```bash
# SSH 隧道转发
ssh -L 9229:localhost:9229 user@remote-server

# 现在访问 chrome://inspect 即可调试远程服务器
```

**安全建议**:

- 仅在开发/测试环境使用
- 使用 SSH 隧道，不要直接暴露调试端口
- 调试后立即关闭

### 7.2 Docker 容器调试

**Dockerfile**:

```dockerfile
FROM node:18
WORKDIR /app
COPY . .
RUN npm install

# 暴露调试端口
EXPOSE 9229

CMD ["node", "--inspect=0.0.0.0:9229", "server.js"]
```

**运行**:

```bash
# 映射调试端口
docker run -p 9229:9229 -p 3000:3000 my-app

# 访问 chrome://inspect
```

**docker-compose.yml**:

```yaml
version: "3"
services:
app:
build: .
ports:
- "3000:3000"
- "9229:9229"
command: node --inspect=0.0.0.0:9229 server.js
volumes:
- .:/app
- /app/node_modules # 避免覆盖
```

---

## 8. 调试技巧与最佳实践

### 8.1 条件断点

在 Chrome DevTools 或 VSCode 中：

```javascript
// 右键断点 → Edit breakpoint → Condition
user_id === 123;

// 或在代码中
if (user_id === 123) {
debugger;
}
```

### 8.2 Logpoints (日志点)

**不修改源码的情况下打印日志**:

VSCode: 右键行号 → "Add Logpoint"

```javascript
// 语法（不需要 console.log）
"user_id:", user_id, "key:", key;
```

### 8.3 Watch 表达式

在 Watch 面板添加表达式：

```javascript
JSON.stringify(params);
Buffer.from(key).toString("hex");
new Date(timestamp);
```

### 8.4 环境变量调试

```bash
# 设置环境变量
export DEBUG=* # 启用所有 debug 日志
export NODE_ENV=development

# 在代码中读取
console.log(process.env.DEBUG);
```

**使用 debug 模块**:

```javascript
const debug = require("debug")("app:encrypt");

function encrypt(data, key) {
debug("加密开始, data=%s, key=%s", data, key.toString("hex"));
// ...
debug("加密完成, result=%s", result);
return result;
}
```

运行:

```bash
DEBUG=app:* node script.js
```

### 8.5 REPL 调试

**在运行时进入 REPL**:

```javascript
const repl = require("repl");

function complexFunction(data) {
const step1 = process1(data);

// 进入 REPL 检查中间结果
if (process.env.DEBUG) {
console.log("进入 REPL 调试...");
const r = repl.start("> ");
r.context.step1 = step1; // 导出变量到 REPL
r.context.data = data;
}

const step2 = process2(step1);
return step2;
}
```

运行:

```bash
DEBUG=1 node script.js

# 在 REPL 中
> step1
> JSON.stringify(step1)
> .exit // 退出 REPL 继续执行
```

---

## 9. 实战案例

### 案例 1：逆向 Webpack 打包的加密逻辑

**目标**: 某网站的 JS 是 Webpack 打包的，找到加密函数

**步骤**:

1. **下载打包后的 JS**:

```bash
curl https://example.com/app.bundle.js > app.bundle.js
```

2. **使用 webcrack 反打包**:

```bash
npm install -g webcrack
webcrack app.bundle.js -o ./unpacked
```

3. **找到加密函数** (假设在 `./unpacked/module_123.js`):

```javascript
function encrypt(data) {
// 复杂的加密逻辑
}
```

4. **创建测试脚本** `test.js`:

```javascript
// 复制 module_123.js 的内容
const encrypt = require("./unpacked/module_123.js");

// 测试
const result = encrypt("Hello");
console.log(result);
```

5. **调试**:

```bash
node --inspect-brk test.js
```

6. **在 DevTools 中**:
    - 单步调试 `encrypt` 函数
    - 查看中间变量
    - 提取密钥/算法

### 案例 2：调试 Electron 应用

**目标**: 逆向某 Electron 桌面应用的加密通信

**步骤**:

1. **找到应用的 asar 文件**:

```bash
# macOS
cd /Applications/MyApp.app/Contents/Resources
ls app.asar

# Windows
cd C:\Program Files\MyApp\resources
dir app.asar
```

2. **解包 asar**:

```bash
npm install -g asar

asar extract app.asar app_unpacked
cd app_unpacked
```

3. **启动调试模式**:

```bash
# 设置环境变量
export ELECTRON_ENABLE_LOGGING=1
export ELECTRON_RUN_AS_NODE=1

# 启动 Electron 并附加调试器
electron --inspect-brk=5858 .
```

4. **连接 Chrome DevTools**:

```
chrome://inspect
```

5. **分析加密逻辑**:
    - 在 `main.js` 或 `renderer.js` 中搜索加密相关函数
    - 打断点调试

### 案例 3：Hook require() 追踪模块加载

**目标**: 查看脚本加载了哪些模块

```javascript
// hook-require.js
const Module = require("module");
const originalRequire = Module.prototype.require;

Module.prototype.require = function (id) {
console.log("[require]", id);

// 拦截特定模块
if (id === "crypto") {
console.log("[Hook] 拦截 crypto 模块");
debugger; // 断点
}

return originalRequire.apply(this, arguments);
};

// 加载目标脚本
require("./suspicious-script.js");
```

**运行**:

```bash
node --inspect-brk hook-require.js
```

---

## 10. 工具推荐

| 工具 | 用途 | 安装 |
| ----------------------- | ----------------------------- | --------------------------------- |
| **ndb** | Google 开发的增强版调试器 | `npm install -g ndb` |
| **node-inspector** | 旧版 Node.js 调试器（已废弃） | - |
| **nodemon** | 自动重启 + 调试 | `npm install -g nodemon` |
| **debug** | 条件日志输出 | `npm install debug` |
| **why-is-node-running** | 查找阻止退出的资源 | `npm install why-is-node-running` |

**ndb 使用**:

```bash
ndb script.js

# 或调试 npm script
ndb npm start
```

**nodemon + 调试**:

```bash
nodemon --inspect-brk script.js
```

**why-is-node-running 使用**:

```javascript
const why = require("why-is-node-running");

setTimeout(() => {
why(); // 打印所有未关闭的资源
}, 5000);
```

---

## 总结

Node.js 调试的关键技能：

1. ✅ **基础调试**: `--inspect-brk` + Chrome DevTools / VSCode
2. ✅ **内存分析**: Heap Snapshot 提取密钥和敏感数据
3. ✅ **性能分析**: CPU Profiler 定位耗时函数
4. ✅ **异步调试**: async/await + async stack traces
5. ✅ **第三方包调试**: npm link + 禁用 skipFiles
6. ✅ **远程调试**: SSH 隧道 + Docker 端口映射
7. ✅ **实战技巧**: Hook require、条件断点、REPL 调试

**记住**: Node.js 调试的本质是利用 Chrome DevTools Protocol，掌握了浏览器调试，就掌握了 Node.js 调试。

---

## 相关章节

- [浏览器开发者工具](./browser_devtools.md)
- [动态参数分析](../03-Basic-Recipes/dynamic_parameter_analysis.md)
- [AST 工具](./ast_tools.md)
- [Puppeteer 与 Playwright](./puppeteer_playwright.md)
