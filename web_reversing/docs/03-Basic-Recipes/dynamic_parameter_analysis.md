# 动态参数分析

## 概述

当静态代码混淆得像一团乱麻时，动态分析是我们唯一的出路。通过观察参数在运行时的变化，我们可以推导出生成逻辑。

动态分析的核心是**观察数据流** —— 不要试图理解每一行混淆代码的语义，而是关注数据从哪里来、经过了什么处理、最后变成了什么。

---

## 1. 堆栈跟踪 (Stack Trace) 分析

调用栈是程序执行的"案发现场"，是定位代码的第一手段。

### 1.1 查看调用栈的方法

#### 方法 1：断点自动停下

在 Sources 面板打断点后，右侧 Call Stack 面板会显示完整调用链：

```
generateSign (utils.js:1234)
  ↑ 调用者
sendRequest (api.js:567)
  ↑ 调用者
onClick (main.js:89)
  ↑ 调用者
(anonymous) (VM123:5)  ← 事件监听器
```

#### 方法 2：手动打印堆栈

在 Console 中任何位置执行：

```javascript
console.trace("当前调用栈");
```

输出类似：

```
console.trace
  at generateSign (utils.js:1234)
  at sendRequest (api.js:567)
  at onClick (main.js:89)
```

#### 方法 3：使用 Error 对象

```javascript
const stack = new Error().stack;
console.log(stack);
```

### 1.2 寻找"断层"技巧

**现象**: 调用栈中突然出现以下特征

- `VM123`, `eval` → 动态生成的代码
- `l`, `e`, `f`, `t` 等单字母函数名 → 混淆后的代码
- `<anonymous>` → 匿名函数（可能是立即执行函数 IIFE）

**含义**: 这通常意味着进入了混淆后的核心逻辑

**操作**: 在栈顶的第一个**可读函数**处打断点，然后 Step Into (F11) 进入内部

**示例**

```
Call Stack:
generateSign (utils.js:1234)  ← 可读，从这里开始调试
  ↑
t (VM123:5)                   ← 混淆代码
  ↑
e (VM123:2)                   ← 混淆代码
  ↑
onClick (main.js:89)          ← 可读
```

### 1.3 利用 Initiator (发起者)

Chrome 的 Network 面板有一列 `Initiator`，显示请求的来源。

**操作步骤**:

1. Network 面板找到目标请求
2. 查看 Initiator 列
3. 点击蓝色链接 → 直接跳转到发包代码

**Initiator 类型**:

| 类型         | 含义                   | 示例              |
| ------------ | ---------------------- | ----------------- |
| **Script**   | JS 代码发起            | `api.js:567`      |
| **Parser**   | HTML 解析器加载        | `<img src="...">` |
| **Redirect** | 重定向                 | `301/302`         |
| **Other**    | 其他（扩展、DevTools） | -                 |

**高级功能**: Request Call Stack

- 开启: DevTools Settings → Experiments → Enable async stack traces
- 效果: 可以看到异步回调前的调用栈（如 `setTimeout`, `Promise.then`）

---

## 2. 断点技术

### 2.1 断点类型

#### 普通断点 (Line Breakpoint)

点击行号即可，代码执行到此行时暂停。

#### 条件断点 (Conditional Breakpoint)

右键行号 → "Add conditional breakpoint"

**应用场景**: 只在特定条件下暂停

```javascript
// 只在 userId 等于 123 时暂停
userId === 123;

// 只在第 10 次循环时暂停
i === 10;

// 只在参数包含特定字符串时暂停
params.includes("target");
```

#### 日志断点 (Logpoint)

右键行号 → "Add logpoint"

**应用场景**: 不暂停，只打印日志（相当于 `console.log` 但不修改源码）

```javascript
// 语法（不需要写 console.log）
"userId:", userId, "timestamp:", timestamp;
```

#### DOM 断点 (DOM Breakpoint)

在 Elements 面板右键元素 → "Break on":

- **subtree modifications**: 子元素被修改
- **attribute modifications**: 属性被修改（如 `class`, `style`）
- **node removal**: 元素被删除

**应用场景**: 追踪是谁修改了某个 DOM 元素

#### XHR/Fetch 断点

Sources 面板 → XHR/fetch Breakpoints → 添加 URL 关键字

**应用场景**: 在发送包含 `/api/login` 的请求前自动断点

```
关键字: /api/login
```

#### 事件监听器断点 (Event Listener Breakpoint)

Sources 面板 → Event Listener Breakpoints → 勾选事件类型

**常用事件**:

- Mouse → `click`, `mousedown`
- Keyboard → `keydown`, `keypress`
- Timer → `setTimeout`, `setInterval`

### 2.2 断点调试技巧

#### 单步调试快捷键

| 快捷键        | 功能                    | 说明                       |
| ------------- | ----------------------- | -------------------------- |
| **F8**        | Resume                  | 继续执行（到下一个断点）   |
| **F10**       | Step Over               | 单步跳过（不进入函数内部） |
| **F11**       | Step Into               | 单步进入（进入函数内部）   |
| **Shift+F11** | Step Out                | 跳出当前函数               |
| **Ctrl+F8**   | Disable All Breakpoints | 临时禁用所有断点           |

#### 黑盒脚本 (Blackbox Script)

右键文件 → "Blackbox script"

**作用**: 单步调试时自动跳过该文件（通常用于跳过第三方库）

**示例**: 跳过 jQuery, Lodash 等库文件

```
Settings → Blackboxing → Add pattern
Pattern: jquery.*\.js
Pattern: lodash.*\.js
```

#### Watch 表达式 (Watch Expressions)

在断点暂停时，右侧 Watch 面板可以监控表达式的值

**示例**:

```javascript
// 添加以下表达式
params.sign;
JSON.stringify(params);
btoa(params.user_id);
```

每次断点停下时，这些表达式都会自动求值并显示。

---

## 3. 内存漫游 (Scope Sniffing)

在断点停下后，Console 不仅仅是用来打印 log 的，它是一个全功能的 REPL (Read-Eval-Print Loop)。

### 3.1 检查作用域变量

**Scope 面板显示**:

- **Local**: 当前函数的局部变量
- **Closure**: 闭包变量（外层函数的变量）
- **Global**: 全局变量 (`window`)

**技巧**: 在 Console 中直接访问

```javascript
// 在断点暂停时，Console 的上下文就是当前函数
console.log(params); // 打印局部变量 params
console.log(this); // 打印 this 对象
```

### 3.2 检查闭包变量

**问题**: 某些加密函数使用了闭包变量，Local Scope 看不到

**示例**:

```javascript
function createEncryptor() {
  const secretKey = "hardcoded_key_2024"; // 闭包变量

  return function encrypt(data) {
    // 使用 secretKey，但 Local Scope 里看不到
    return AES.encrypt(data, secretKey);
  };
}

const encrypt = createEncryptor();
```

**解决方案**:

1. 查看 Scope 面板 → **Closure** 部分
2. 或在 Console 里直接输入变量名试试

### 3.3 导出大对象/数组

**场景**: 混淆代码预先生成了一个巨大的字符串数组（大表）

**方法 1: copy() 函数**

```javascript
// 在 Console 中执行
copy(bigArray); // 自动复制到剪贴板
```

**方法 2: 下载为文件**

```javascript
// 导出为 JSON 文件
const json = JSON.stringify(bigArray, null, 2);
const blob = new Blob([json], { type: "application/json" });
const url = URL.createObjectURL(blob);
const a = document.createElement("a");
a.href = url;
a.download = "bigArray.json";
a.click();
```

### 3.4 修改运行时变量

在断点暂停时，可以在 Console 中直接修改变量：

```javascript
// 修改参数测试不同情况
params.timestamp = 1234567890;
params.sign = "test_sign";

// 修改对象原型链
Object.prototype.myDebug = true;
```

---

## 4. 探针技术 (Probing)

如果找不到某个函数在哪被调用，可以"投石问路"。

### 4.1 污点追踪 (Property Access Interception)

**场景**: 怀疑某个对象的属性 `x` 会被加密函数读取

**方法**: 使用 `Object.defineProperty` 劫持属性访问

```javascript
const obj = { x: "original_value" };

Object.defineProperty(obj, "x", {
  get: function () {
    console.trace("读取了 obj.x"); // 打印调用栈
    debugger; // 自动断点
    return "original_value";
  },
  set: function (value) {
    console.trace("修改了 obj.x 为", value);
    debugger;
  },
});
```

**实战案例**: 追踪 Cookie 读取

```javascript
// 劫持 document.cookie
let _cookie = document.cookie;
Object.defineProperty(document, "cookie", {
  get: function () {
    console.trace("读取了 cookie");
    debugger;
    return _cookie;
  },
  set: function (value) {
    console.trace("设置了 cookie:", value);
    _cookie = value;
  },
});
```

### 4.2 函数劫持 (Function Hooking)

**场景**: 追踪某个函数的调用

**方法 1: 劫持全局函数**

```javascript
const _fetch = window.fetch;
window.fetch = function (...args) {
  console.log("[Fetch]", args[0]); // 打印 URL
  debugger; // 发起 fetch 请求前断点
  return _fetch.apply(this, args);
};
```

**方法 2: 劫持原型方法**

```javascript
const _stringify = JSON.stringify;
JSON.stringify = function (obj) {
  console.log("[JSON.stringify]", obj);
  debugger;
  return _stringify.apply(this, arguments);
};
```

**方法 3: Proxy 代理**

```javascript
const handler = {
  apply: function (target, thisArg, args) {
    console.log("[调用]", target.name, args);
    debugger;
    return target.apply(thisArg, args);
  },
};

// 劫持加密函数
const originalEncrypt = window.encrypt;
window.encrypt = new Proxy(originalEncrypt, handler);
```

### 4.3 异常断点 (Exception Breakpoint)

**方法**: Sources 面板 → 勾选 "Pause on exceptions"

**应用场景**:

- 代码抛出错误时自动暂停
- 追踪 `try-catch` 中捕获的异常

**示例**:

```javascript
try {
  // 某个会抛异常的加密函数
  const encrypted = riskyEncrypt(data);
} catch (e) {
  // 如果勾选了 "Pause on caught exceptions"，会在这里暂停
  console.error(e);
}
```

---

## 5. 异步调试 (Async Debugging)

### 5.1 Promise 调试

**问题**: Promise 链中某个步骤出错，难以定位

**解决方案 1**: 启用 Async Stack Traces

```
DevTools Settings → Enable async stack traces
```

**效果**: 调用栈会显示完整的 Promise 链

```
Call Stack:
then (api.js:123)  ← 当前 Promise
  ↑ (async)
fetchData (main.js:45)  ← 发起 Promise 的位置
```

**解决方案 2**: 在 Promise 中手动断点

```javascript
fetch("/api/data")
  .then((response) => {
    debugger; // 断点
    return response.json();
  })
  .then((data) => {
    debugger; // 断点
    console.log(data);
  });
```

### 5.2 async/await 调试

使用 `async/await` 比 Promise 链更容易调试：

```javascript
async function fetchData() {
  const response = await fetch("/api/data"); // 断点
  const json = await response.json(); // 断点
  console.log(json); // 断点
}
```

**优势**: 可以像同步代码一样单步调试 (F10)

### 5.3 setTimeout/setInterval 调试

**方法 1**: Event Listener Breakpoint

```
Sources → Event Listener Breakpoints → Timer → setInterval fired
```

**方法 2**: 劫持定时器\*\*

```javascript
const _setTimeout = window.setTimeout;
window.setTimeout = function (callback, delay) {
  console.log(`[setTimeout] ${delay}ms`, callback.toString());
  debugger;
  return _setTimeout.apply(this, arguments);
};
```

---

## 6. 性能分析 (Performance Profiling)

### 6.1 CPU 性能分析

**场景**: 代码运行很慢，怀疑有性能瓶颈或故意的延迟

**步骤**:

1. Performance 面板 → 点击 Record
2. 执行目标操作（如点击按钮）
3. 停止录制
4. 查看 **Flame Chart**（火焰图）

**分析技巧**:

- **宽度** = 执行时间（越宽越慢）
- **颜色**:
  - 黄色 = JavaScript 执行
  - 紫色 = 渲染/布局
  - 绿色 = 绘制

**示例**: 发现某个函数 `slowHash()` 占用了 90% 的 CPU 时间 → 这就是加密/混淆的核心逻辑

### 6.2 内存分析

**场景**: 怀疑代码中藏有解密后的 Key 或明文数据

**步骤**:

1. Memory 面板 → Take Heap Snapshot
2. 在搜索框输入关键字（如 `secret`, `key`, `password`）
3. 查找字符串对象

**技巧**: 对比两个快照

1. 拍第一个快照
2. 执行目标操作（如登录）
3. 拍第二个快照
4. 选择 Comparison 模式 → 查看新增的对象

---

## 7. 网络请求分析

### 7.1 XHR/Fetch 断点

在 Sources 面板设置 URL 过滤器：

```
XHR/fetch Breakpoints:
- /api/login
- /api/data
```

当发送匹配的请求时自动断点，此时可以：

- 查看 Call Stack（谁发起的请求）
- 查看 Local 变量（请求参数）
- 修改参数后继续执行

### 7.2 修改请求参数

**方法 1: 在断点处修改**

```javascript
// 在 fetch() 断点处
url = "https://evil.com/api"; // 修改 URL
body = JSON.stringify({ hacked: true }); // 修改 Body
```

**方法 2: 使用 Local Overrides**

1. Network → 右键请求 → "Override content"
2. 修改响应内容
3. 刷新页面 → 使用修改后的响应

---

## 8. 实战案例

### 案例 1：追踪签名函数的 Salt

**目标**: 某 API 的签名包含一个未知的 Salt

**步骤**:

1. Network 面板找到请求，发现参数 `sign=e8f2d3c1...`
2. 搜索 `sign` 关键字，找到 `generateSign()` 函数
3. 在该函数入口打断点
4. 触发请求（如点击按钮）→ 断点暂停
5. 查看 Call Stack 和 Local Scope
6. 发现局部变量 `salt = "my_secret_2024"`
7. 在 Console 中验证：
   ```javascript
   md5("user_id=123&timestamp=1638360000&salt=my_secret_2024");
   // 结果与 sign 匹配 ✅
   ```

### 案例 2：定位 AES 密钥

**目标**: 某登录接口的密码是 AES 加密的，密钥未知

**步骤**:

1. 搜索 `AES.encrypt` 关键字
2. 找到加密函数：
   ```javascript
   function encryptPassword(password) {
     return CryptoJS.AES.encrypt(password, key, { iv: iv }).toString();
   }
   ```
3. 在该函数打断点
4. 触发登录操作 → 断点暂停
5. 查看 Scope 面板 → Closure 部分
6. 发现 `key = "1234567890abcdef"`, `iv = "abcdef1234567890"`
7. 在 Console 中验证：
   ```javascript
   CryptoJS.AES.encrypt("MyPassword", key, { iv: iv }).toString();
   // 结果与实际加密的密码匹配 ✅
   ```

### 案例 3：追踪动态生成的参数

**目标**: 某请求的 `device_id` 参数每次都不同，不知道如何生成

**方法 1: XHR 断点**

1. 设置 XHR 断点（URL: `/api/data`）
2. 触发请求 → 自动断点
3. 查看 Call Stack:
   ```
   send (XMLHttpRequest)
     ↑
   sendRequest (api.js:567)  ← 查看此处代码
     ↑
   onClick (main.js:89)
   ```
4. 跳转到 `api.js:567`，发现：
   ```javascript
   const device_id = getDeviceId(); // 调用了函数
   ```
5. 继续追踪 `getDeviceId()` 函数

**方法 2: 属性拦截**

```javascript
// 在 Console 中执行
const params = {};
Object.defineProperty(params, "device_id", {
  set: function (value) {
    console.trace("设置 device_id:", value);
    debugger;
    this._device_id = value;
  },
  get: function () {
    return this._device_id;
  },
});

// 当代码执行 params.device_id = xxx 时，自动断点
```

### 案例 4：反调试绕过

**现象**: 打开 DevTools 后页面一片空白或报错

**常见反调试手段**:

#### 检测 DevTools 打开

```javascript
// 检测 console
const devtools = /./;
devtools.toString = function () {
  this.opened = true;
};
console.log("%c", devtools);
if (devtools.opened) {
  alert("请关闭开发者工具");
  debugger; // 无限 debugger 循环
}
```

**绕过方法**:

1. 禁用所有断点（Ctrl+F8）
2. 或在 Console 中执行：
   ```javascript
   devtools.toString = function () {
     return "";
   };
   ```

#### 检测页面大小变化

```javascript
window.onresize = function () {
  if (window.outerWidth - window.innerWidth > 200) {
    alert("检测到开发者工具");
    location.href = "about:blank"; // 跳转空白页
  }
};
```

**绕过方法**: 在独立窗口打开 DevTools（Undock into separate window）

#### 无限 debugger

```javascript
setInterval(function () {
  debugger;
}, 100);
```

**绕过方法**:

1. 禁用所有断点（Ctrl+F8）
2. 或右键代码 → "Never pause here"

---

## 9. 调试技巧总结

### 9.1 快速定位技巧

| 场景                   | 方法                                         |
| ---------------------- | -------------------------------------------- |
| **找不到签名函数**     | 搜索 `sign`、`signature`、`md5`、`sha`       |
| **找不到加密函数**     | 搜索 `encrypt`、`AES`、`RSA`、`CryptoJS`     |
| **找不到请求发起点**   | Network → Initiator → 点击链接               |
| **找不到事件处理函数** | Elements → Event Listeners                   |
| **找不到定时器回调**   | Sources → Event Listener Breakpoints → Timer |

### 9.2 常见错误

| 错误                     | 原因                      | 解决方案                             |
| ------------------------ | ------------------------- | ------------------------------------ |
| **变量显示 `undefined`** | 作用域不对                | 检查 Scope 面板，可能在 Closure 中   |
| **断点不生效**           | 代码已优化/内联           | 使用 Logpoint 或禁用缓存             |
| **调用栈看不到源码**     | Source Map 缺失           | 寻找 `.map` 文件或分析编译后代码     |
| **异步代码断不住**       | Async Stack Traces 未开启 | Settings → Enable async stack traces |

### 9.3 效率提升技巧

```javascript
// 1. 快速打印调用栈
console.trace();

// 2. 快速打印对象（美化）
console.table(params);
console.dir(obj, { depth: null });

// 3. 性能测试
console.time("加密耗时");
encrypt(data);
console.timeEnd("加密耗时"); // 输出：加密耗时: 123.45ms

// 4. 分组日志
console.group("签名计算过程");
console.log("步骤 1: 参数排序", sorted);
console.log("步骤 2: 拼接字符串", joined);
console.log("步骤 3: MD5 加密", hashed);
console.groupEnd();

// 5. 断言
console.assert(params.sign === expected, "签名不匹配！");
```

---

## 10. 进阶工具

### 10.1 Chrome DevTools Protocol (CDP)

通过 CDP 可以编程控制 Chrome，实现自动化调试。

**示例**: 使用 Python 自动打断点

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

driver = webdriver.Chrome(options=options)
driver.execute_cdp_cmd("Debugger.enable", {})
driver.execute_cdp_cmd("Debugger.setBreakpointByUrl", {
    "lineNumber": 123,
    "url": "https://example.com/utils.js"
})
```

### 10.2 Puppeteer 调试模式

```javascript
const puppeteer = require("puppeteer");

(async () => {
  const browser = await puppeteer.launch({
    headless: false,
    devtools: true, // 自动打开 DevTools
  });

  const page = await browser.newPage();

  // 在控制台执行代码
  await page.evaluateOnNewDocument(() => {
    window.addEventListener("load", () => {
      debugger; // 页面加载完成后自动断点
    });
  });

  await page.goto("https://example.com");
})();
```

### 10.3 Frida Hook (移动端/桌面应用)

对于非浏览器环境（如 Electron、React Native），可以使用 Frida。

```javascript
// Frida 脚本
Interceptor.attach(Module.findExportByName(null, "encrypt"), {
  onEnter: function (args) {
    console.log("[encrypt] 参数:", Memory.readUtf8String(args[0]));
  },
  onLeave: function (retval) {
    console.log("[encrypt] 返回值:", Memory.readUtf8String(retval));
  },
});
```

---

## 总结

动态分析的精髓在于：

1. ✅ **调用栈追踪**: 从 Initiator 或 Call Stack 找到代码入口
2. ✅ **断点技巧**: 条件断点、Logpoint、XHR 断点、事件断点
3. ✅ **作用域检查**: Local、Closure、Global 三层作用域
4. ✅ **探针技术**: 属性拦截、函数劫持、Proxy 代理
5. ✅ **异步调试**: Async Stack Traces、Promise 链追踪
6. ✅ **性能分析**: CPU Profile、Memory Snapshot
7. ✅ **反调试绕过**: 禁用断点、修改检测代码

**记住**: 不要试图理解每一行混淆代码，而是**观察数据流** —— 数据从哪里来、经过了什么处理、最后变成了什么。

---

## 相关章节

- [JavaScript 反混淆](../04-Advanced-Recipes/javascript_deobfuscation.md)
- [浏览器开发者工具](../02-Tooling/browser_devtools.md)
- [Hooking 技术](./hooking_techniques.md)
- [API 逆向与重放攻击](./api_reverse_engineering.md)
- [Node.js 调试指南](../02-Tooling/nodejs_debugging.md)
