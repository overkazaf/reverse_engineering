---
title: "JavaScript VMP 逆向工程"
date: 2025-05-07
type: posts
tags: ["Ghidra", "逆向分析", "Frida", "加密分析", "Hook", "脱壳"]
weight: 10
---

# JavaScript VMP 逆向工程

> **📚 前置知识**
>
> 本配方涉及以下核心技术，建议先阅读相关章节：
>
> - **[JS OB 混淆分析](./js_obfuscator.md)** - 理解 JavaScript 混淆的基本原理
> - **AST 与编译原理** - 理解抽象语法树和字节码执行

JavaScript VMP（虚拟机保护）是一种高级的代码保护技术，它将原始的 JavaScript 代码转换成一种自定义的、基于虚拟机的字节码。然后，在运行时，一个内置的解释器（或虚拟机）会执行这些字节码。这种方式极大地增加了逆向工程的难度，因为它隐藏了原始的代码逻辑和结构。

---

## JSVMP 原理

### 什么是 JavaScript 虚拟机保护

JSVMP 的核心思想是 **"把 JavaScript 当作汇编来写"**。传统的 JavaScript 混淆（如 OB 混淆）只是对源码做变形——变量重命名、控制流平坦化、字符串加密等，但代码结构仍然是标准 JavaScript，可以用 AST 工具还原。JSVMP 则彻底改变了执行模型：它将原始 JS 编译为一套 **私有字节码**，再用一个 JavaScript 编写的 **虚拟机解释器** 在运行时逐条解释执行。

```text
原始 JavaScript 代码
        |
        v
  +-----------+
  | JS 编译器  |   (离线阶段, 在构建/发布时执行)
  +-----------+
        |
        v
  +-------------------+
  | 私有字节码 (opcode)|   一个数字/字符串数组
  +-------------------+
        |
        v
  +-----------------+
  | JS 虚拟机解释器  |   (运行时, 在浏览器中执行)
  +-----------------+
        |
        v
     执行结果
```

### 与传统混淆的对比

| 特性 | OB 混淆 | JSVMP |
|---|---|---|
| 执行模型 | 标准 JS 引擎直接执行 | 自定义 VM 解释执行 |
| 代码结构 | 仍是合法 JS 语法 | 字节码 + 解释器 |
| AST 还原 | 可行（Babel 插件） | 几乎不可行 |
| 逆向难度 | 中等 | 非常高 |
| 性能影响 | 较小 | 较大（解释执行开销） |
| 代码体积 | 中等增长 | 较大增长 |
| 典型代表 | javascript-obfuscator | 某数、瑞数、Jsvmp.com |

### 编译流程详解

JSVMP 的编译过程模拟了真实编译器的工作方式：

```text
源码: function sign(data) { return md5(data + secret); }
         |
         v
    [1] 词法分析 (Lexer)
         |
         v
    Token 流: [FUNCTION, IDENT("sign"), LPAREN, ...]
         |
         v
    [2] 语法分析 (Parser)
         |
         v
    AST (抽象语法树)
         |
         v
    [3] 字节码生成 (Code Generator)
         |
         v
    字节码: [1, 0, 5, 2, 0, 1, 12, 3, 0, 7, 2, 1, 14, ...]
         |
         v
    [4] 打包 (Bundler)
         |
         v
    最终产物: VM 解释器代码 + 字节码数组
```

生成的字节码通常被编码为一个大型数组：

```javascript
// 编译后的字节码示例 (已简化)
var _bytecode = [1,0,5,2,0,1,12,3,0,7,2,1,14,0,3,6,15];
// 每个数字代表一条指令或操作数
// 1 = PUSH_LOCAL, 0 = 变量索引0
// 5 = PUSH_CONST, 2 = 常量索引2
// 12 = BINARY_ADD
// ...
```

---

## JSVMP 架构

JSVMP 虚拟机在架构上与真实 CPU 非常相似，包含以下核心组件：

### 整体架构图

```text
+------------------------------------------------------------------+
|                        JSVMP 虚拟机                               |
|                                                                  |
|  +------------------+    +-----------------------------+         |
|  |   字节码数组      |    |        调度器 (Dispatcher)   |         |
|  |  [1,0,5,2,12,..] |    |                             |         |
|  +--------+---------+    |   while (true) {            |         |
|           |              |     opcode = fetch(PC++);   |         |
|           v              |     switch (opcode) {       |         |
|  +------------------+    |       case 1: handler1();   |         |
|  |  程序计数器 (PC)  |--->|       case 2: handler2();   |         |
|  |     PC = 0       |    |       case 3: handler3();   |         |
|  +------------------+    |       ...                   |         |
|                          |     }                       |         |
|  +------------------+    |   }                         |         |
|  |   虚拟寄存器      |    +-----------------------------+         |
|  |  r0, r1, r2, ... |                                            |
|  +------------------+    +-----------------------------+         |
|                          |    Opcode Handlers           |         |
|  +------------------+    |                             |         |
|  |   虚拟栈 (Stack) |    |  handler1: PUSH(val)       |         |
|  |  [..., val, val] |    |  handler2: POP() -> reg    |         |
|  +------------------+    |  handler3: ADD(a, b)       |         |
|                          |  handler4: CALL(fn, args)  |         |
|  +------------------+    |  handler5: JMP(addr)       |         |
|  |   作用域链        |    |  ...                       |         |
|  |  [global, local] |    +-----------------------------+         |
|  +------------------+                                            |
+------------------------------------------------------------------+
```

### 核心组件说明

**1. 字节码数组（Bytecode Array）**

字节码数组是 VM 的 "程序"。它以紧凑的数字序列存储所有指令和操作数。

```javascript
// 典型的字节码数组结构
var G = [
    // 指令区
    1, 0,       // PUSH_LOCAL 0
    5, 3,       // PUSH_CONST 3
    12,         // ADD
    2, 1,       // STORE_LOCAL 1
    // 常量池 (有时混在一起, 有时独立存储)
    // ...
];
```

**2. 程序计数器（PC）**

PC 指向当前要执行的字节码位置。每执行一条指令后，PC 递增到下一条指令的起始位置。跳转指令会直接修改 PC。

**3. 虚拟栈（Virtual Stack）**

VM 使用栈来传递操作数和存储中间结果。这是一个典型的 **基于栈的虚拟机** 架构（类似 JVM、Python VM）。

```javascript
// 栈操作示例
// 计算 3 + 5:
// PUSH 3    -> stack: [3]
// PUSH 5    -> stack: [3, 5]
// ADD       -> pop 5, pop 3, push 8 -> stack: [8]
```

**4. 虚拟寄存器（Virtual Registers）**

部分 JSVMP 实现采用寄存器式或混合式架构，使用一组变量模拟寄存器来存储局部变量和临时值。

```javascript
// 寄存器式示例
var regs = new Array(16);  // 16 个虚拟寄存器
regs[0] = localVar0;
regs[1] = localVar1;
// ...
```

**5. 调度器（Dispatcher Loop）**

调度器是 VM 的心脏，负责取指令、解码、派发到对应的 handler。

```javascript
// 最典型的调度器结构
function vm_exec(bytecode) {
    var stack = [];
    var pc = 0;
    var regs = {};

    while (true) {
        var opcode = bytecode[pc++];
        switch (opcode) {
            case 0: // HALT
                return stack.pop();
            case 1: // PUSH_CONST
                var idx = bytecode[pc++];
                stack.push(constants[idx]);
                break;
            case 2: // PUSH_LOCAL
                var slot = bytecode[pc++];
                stack.push(regs[slot]);
                break;
            case 3: // STORE_LOCAL
                var slot = bytecode[pc++];
                regs[slot] = stack.pop();
                break;
            case 4: // ADD
                var b = stack.pop();
                var a = stack.pop();
                stack.push(a + b);
                break;
            // ... 更多 handler
        }
    }
}
```

---

## 识别 JSVMP

在分析一段混淆代码时，识别它是否使用了 JSVMP 是第一步。以下是典型的识别特征：

### 特征 1：巨大的 while-true + switch 结构

```javascript
// JSVMP 的标志性模式
while (true) {
    switch (_0x3a7b[_0x1c++]) {
        case 0:
            // ...
            break;
        case 1:
            // ...
            break;
        // 几十甚至上百个 case
        case 47:
            // ...
            break;
    }
}
```

> 注意：控制流平坦化（CFF）也有类似结构，但 CFF 的 case 数通常较少（与原始代码块数一致），且 case 内代码量较大。JSVMP 的 case 数非常多，每个 case 内代码非常短（通常只有 1-3 行），因为它们只执行一个原子操作。

### 特征 2：大型数字/字符串数组

```javascript
// 字节码数组 — 大量数字
var _0xab3f = [1,0,5,2,0,1,12,3,0,7,2,1,14,0,3,6,15,1,0,5,
    2,0,1,12,3,0,7,2,1,14,0,3,6,15,1,0,5,2,0,1,12,3,0,7,2,
    // ... 几千甚至上万个数字
];
```

### 特征 3：栈操作模式

代码中频繁出现 `push`、`pop` 操作或数组索引递增模式：

```javascript
// 常见的栈操作变体
_0x4f2a.push(_0x1b3c);          // 直接 push
_0x1b3c = _0x4f2a.pop();        // 直接 pop
_0x4f2a[++_0x5e7d] = _0x1b3c;  // 通过索引模拟 push
_0x1b3c = _0x4f2a[_0x5e7d--];  // 通过索引模拟 pop
```

### 特征 4：PC 递增模式

程序计数器变量不断递增来读取操作数：

```javascript
var _op = _0xab3f[_pc++];   // 取 opcode
var _arg = _0xab3f[_pc++];  // 取操作数
```

### 快速判别流程

```text
发现大型混淆 JS 文件
        |
        v
是否有大型数字数组 (>100 个元素)?  --否--> 可能是 OB 混淆或 CFF
        |
       是
        v
是否有 while(true) + switch?  --否--> 可能是其他保护
        |
       是
        v
switch 的 case 数量多且每个 case 很短?  --否--> 可能是 CFF
        |
       是
        v
是否有明显的栈操作 (push/pop)?  --否--> 可能是寄存器式 VMP
        |
       是
        v
    确认为 JSVMP (基于栈)
```

---

## 分析方法论

逆向 JSVMP 是一个系统性工程，需要结合静态分析和动态分析。以下是推荐的分步方法论：

### 总体流程

```text
[1] 定位 VM 入口
      |
      v
[2] 识别核心组件 (字节码数组, 调度器, 栈, PC)
      |
      v
[3] 标注所有 Opcode Handler
      |
      v
[4] 动态跟踪: 记录执行轨迹 (PC, opcode, stack)
      |
      v
[5] 逐个分析 Handler 功能
      |
      v
[6] 编写反汇编器 / 反编译器
      |
      v
[7] 还原关键逻辑
```

### 步骤 1：定位 VM 入口

VM 入口通常是一个接收字节码数组（或其索引）并启动解释循环的函数。搜索以下模式：

```javascript
// 模式 A: 直接传入字节码
function _0x2b3c(_bytecodes) {
    var _stack = [];
    var _pc = 0;
    while (true) { /* ... */ }
}

// 模式 B: 从全局数组中取字节码
function _0x2b3c(_startPC) {
    _pc = _startPC;
    while (true) {
        switch (_G[_pc++]) { /* ... */ }
    }
}
```

### 步骤 2：识别核心组件

定位到 VM 入口后，在闭包或函数作用域内寻找以下变量：

| 组件 | 识别特征 | 示例 |
|---|---|---|
| 字节码数组 | 大型数组，被 PC 索引访问 | `_G[_pc++]` |
| 程序计数器 | 不断递增的数值变量 | `_pc++`, `_idx++` |
| 虚拟栈 | 有 push/pop 操作的数组 | `_s.push(...)`, `_s.pop()` |
| 寄存器/局部变量 | 通过索引访问的数组或对象 | `_r[0]`, `_locals[n]` |
| 作用域 | 存储外部引用的对象 | `_scope`, `_env` |

### 步骤 3：标注 Opcode Handler

对调度器 switch 中的每个 case 添加注释，记录其功能。这是最耗时但也最关键的步骤。

```javascript
switch (opcode) {
    case 0:  // HALT - 终止执行, 返回栈顶
        return _stack[_sp];
    case 1:  // PUSH_CONST - 压入常量
        _stack[++_sp] = _G[_pc++];
        break;
    case 2:  // PUSH_LOCAL - 压入局部变量
        _stack[++_sp] = _regs[_G[_pc++]];
        break;
    case 3:  // STORE_LOCAL - 存储到局部变量
        _regs[_G[_pc++]] = _stack[_sp--];
        break;
    case 4:  // ADD - 加法
        _sp--;
        _stack[_sp] = _stack[_sp] + _stack[_sp + 1];
        break;
    // ... 逐个标注
}
```

### 步骤 4：动态跟踪

在调度器循环中插入日志代码，记录每条指令的执行情况：

```javascript
// 在 switch 之前插入
console.log(
    'PC:', _pc - 1,
    'OP:', opcode,
    'Stack:', JSON.stringify(_stack.slice(0, _sp + 1)),
    'Regs:', JSON.stringify(_regs)
);
```

---

## Opcode Handler 分析

以下是 JSVMP 中最常见的 Opcode 类型及其识别方法：

### 常见 Opcode 分类表

| 类别 | Opcode | 描述 | 典型实现 |
|---|---|---|---|
| 栈操作 | PUSH_CONST | 压入常量 | `s[++sp] = G[pc++]` |
| | PUSH_LOCAL | 压入局部变量 | `s[++sp] = r[G[pc++]]` |
| | POP | 弹出栈顶 | `sp--` |
| | DUP | 复制栈顶 | `s[sp+1] = s[sp]; sp++` |
| 存储 | STORE_LOCAL | 保存到局部变量 | `r[G[pc++]] = s[sp--]` |
| | STORE_GLOBAL | 保存到全局 | `global[k] = s[sp--]` |
| 算术 | ADD | 加法 | `s[sp-1] = s[sp-1] + s[sp]; sp--` |
| | SUB | 减法 | `s[sp-1] = s[sp-1] - s[sp]; sp--` |
| | MUL | 乘法 | `s[sp-1] = s[sp-1] * s[sp]; sp--` |
| | MOD | 取模 | `s[sp-1] = s[sp-1] % s[sp]; sp--` |
| | BITAND | 按位与 | `s[sp-1] = s[sp-1] & s[sp]; sp--` |
| | BITOR | 按位或 | `s[sp-1] = s[sp-1] \| s[sp]; sp--` |
| | BITXOR | 按位异或 | `s[sp-1] = s[sp-1] ^ s[sp]; sp--` |
| | SHL | 左移 | `s[sp-1] = s[sp-1] << s[sp]; sp--` |
| | SHR | 右移 | `s[sp-1] = s[sp-1] >> s[sp]; sp--` |
| | USHR | 无符号右移 | `s[sp-1] = s[sp-1] >>> s[sp]; sp--` |
| 比较 | EQ | 等于 | `s[sp-1] = s[sp-1] == s[sp]; sp--` |
| | SEQ | 严格等于 | `s[sp-1] = s[sp-1] === s[sp]; sp--` |
| | LT | 小于 | `s[sp-1] = s[sp-1] < s[sp]; sp--` |
| | GT | 大于 | `s[sp-1] = s[sp-1] > s[sp]; sp--` |
| 逻辑 | NOT | 逻辑非 | `s[sp] = !s[sp]` |
| | BITNOT | 按位取反 | `s[sp] = ~s[sp]` |
| 跳转 | JMP | 无条件跳转 | `pc = G[pc]` |
| | JMP_IF | 条件跳转 | `if(s[sp--]) pc=G[pc]; else pc++` |
| | JMP_IFNOT | 条件不跳 | `if(!s[sp--]) pc=G[pc]; else pc++` |
| 函数 | CALL | 函数调用 | `s[sp-n] = s[sp-n-1](...args)` |
| | NEW | 构造对象 | `s[sp-n] = new s[sp-n-1](...args)` |
| | RETURN | 返回 | `return s[sp]` |
| 对象 | GET_PROP | 获取属性 | `s[sp-1] = s[sp-1][s[sp]]; sp--` |
| | SET_PROP | 设置属性 | `s[sp-2][s[sp-1]] = s[sp]; sp-=3` |
| | TYPEOF | 类型判断 | `s[sp] = typeof s[sp]` |

### 识别 Handler 的技巧

**技巧 1：观察栈指针变化**

```text
弹出 2 个, 压入 1 个 (sp--)  ->  二元运算 (ADD, SUB, EQ, ...)
弹出 0 个, 压入 1 个 (sp++)  ->  PUSH 类操作
弹出 1 个, 压入 0 个 (sp--)  ->  STORE 或 POP 操作
弹出 1 个, 压入 1 个 (sp不变) ->  一元运算 (NOT, TYPEOF, ...)
```

**技巧 2：观察 PC 变化**

```text
pc 正常递增 (+1 或 +2)  ->  普通指令
pc 被直接赋值          ->  跳转指令 (JMP, JMP_IF)
pc 不再使用            ->  RETURN 或 HALT
```

**技巧 3：观察外部调用**

```javascript
// 如果 handler 中出现 apply / call, 大概率是 CALL opcode
case 28:
    var args = _stack.splice(_sp - _argc, _argc);
    var fn = _stack[--_sp];
    var thisArg = _stack[--_sp];
    _stack[++_sp] = fn.apply(thisArg, args);
    break;
```

---

## 浏览器 Hook 辅助分析

### 使用 Chrome DevTools

**方法 1：条件断点记录**

在调度器的 `switch` 语句处设置条件断点，使其永远不暂停，但打印日志：

```javascript
// 在 switch(opcode) 行设置条件断点, 表达式为:
(console.log('PC:', _pc, 'OP:', opcode, 'ST:', JSON.stringify(_stack.slice(0, _sp+1))), false)
// 返回 false 使断点不暂停, 但 console.log 已经执行
```

**方法 2：Overrides 注入**

使用 Chrome DevTools 的 Local Overrides 功能，直接修改 JS 文件，在调度器中注入跟踪代码：

```javascript
// 在 fetch-decode 之后, execute 之前注入
var __opName = {0:'HALT',1:'PUSH_C',2:'PUSH_L',3:'STORE',4:'ADD',/*...*/};
console.log(
    '[VM]',
    'PC=' + (_pc-1).toString().padStart(5),
    'OP=' + opcode.toString().padStart(3),
    '(' + (__opName[opcode] || 'UNK') + ')',
    'SP=' + _sp,
    'TOP=' + JSON.stringify(_stack[_sp])
);
```

### 使用 Frida Hook

当 JSVMP 运行在 WebView 或 Node.js 环境中时，可以使用 Frida 进行 Hook：

```javascript
// Frida 脚本: Hook WebView 中的 evaluateJavascript
Java.perform(function() {
    var WebView = Java.use('android.webkit.WebView');

    // 注入跟踪脚本到 WebView
    WebView.evaluateJavascript.overload('java.lang.String', 'android.webkit.ValueCallback')
        .implementation = function(script, callback) {

        // 在目标脚本执行前注入 Hook
        var hookScript = `
            (function() {
                // 保存原始 Array.prototype.push
                var origPush = Array.prototype.push;
                var logBuffer = [];

                // Hook Array.push 来捕获栈操作
                // 注意: 需要精确定位 VM 的栈对象, 避免干扰其他数组
                // 这里仅作示意
            })();
        `;
        this.evaluateJavascript(hookScript, null);
        this.evaluateJavascript(script, callback);
    };
});
```

### 关键 API Hook 策略

通过 Hook 浏览器 API，可以捕获 VM 与外部环境的交互，从而快速定位关键逻辑：

```javascript
// Hook XMLHttpRequest 来捕获签名参数
(function() {
    var origOpen = XMLHttpRequest.prototype.open;
    var origSend = XMLHttpRequest.prototype.send;

    XMLHttpRequest.prototype.open = function(method, url) {
        this._url = url;
        console.log('[XHR] open:', method, url);
        return origOpen.apply(this, arguments);
    };

    XMLHttpRequest.prototype.send = function(data) {
        console.log('[XHR] send:', this._url, data);
        // 在这里下断点, 然后查看调用栈
        // 可以找到 VM 中哪个 CALL handler 发起了请求
        // debugger;
        return origSend.apply(this, arguments);
    };
})();

// Hook document.cookie 的读取
(function() {
    var cookieDesc = Object.getOwnPropertyDescriptor(Document.prototype, 'cookie')
        || Object.getOwnPropertyDescriptor(HTMLDocument.prototype, 'cookie');
    if (cookieDesc && cookieDesc.get) {
        Object.defineProperty(document, 'cookie', {
            get: function() {
                var val = cookieDesc.get.call(this);
                console.log('[Cookie] get:', val);
                console.trace();  // 打印调用栈, 定位 VM 中的读取位置
                return val;
            },
            set: function(val) {
                console.log('[Cookie] set:', val);
                console.trace();
                return cookieDesc.set.call(this, val);
            }
        });
    }
})();
```

---

## 补环境执行

"补环境" 是指在 Node.js 中模拟浏览器环境，使 JSVMP 代码能够在浏览器之外运行。这样做的目的是：

1. 更方便地添加日志和调试
2. 批量执行签名生成函数
3. 避免浏览器反调试检测

### 基本环境框架

```javascript
// env.js - 浏览器环境模拟框架

// 1. 基础对象
var window = global;
var document = {};
var navigator = {};
var location = {};
var screen = {};
var history = {};

// 2. Navigator 模拟
navigator.userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' +
    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36';
navigator.platform = 'Win32';
navigator.language = 'zh-CN';
navigator.languages = ['zh-CN', 'zh', 'en'];
navigator.cookieEnabled = true;
navigator.webdriver = false;  // 重要: 很多检测会查这个属性

// 3. Document 模拟
document.cookie = '';
document.referrer = 'https://www.example.com/';
document.title = 'Example Page';
document.createElement = function(tag) {
    var elem = {
        tagName: tag.toUpperCase(),
        style: {},
        setAttribute: function(k, v) { this[k] = v; },
        getAttribute: function(k) { return this[k]; },
        appendChild: function(child) { return child; },
        addEventListener: function() {},
    };
    if (tag === 'canvas') {
        elem.getContext = function(type) {
            return {
                fillText: function() {},
                measureText: function() { return { width: 10 }; },
                canvas: { toDataURL: function() { return 'data:image/png;base64,...'; } }
            };
        };
    }
    return elem;
};
document.getElementById = function() { return null; };
document.querySelector = function() { return null; };
document.querySelectorAll = function() { return []; };

// 4. Location 模拟
location.href = 'https://www.example.com/page';
location.protocol = 'https:';
location.host = 'www.example.com';
location.hostname = 'www.example.com';
location.pathname = '/page';
location.search = '';
location.hash = '';

// 5. Screen 模拟
screen.width = 1920;
screen.height = 1080;
screen.availWidth = 1920;
screen.availHeight = 1040;
screen.colorDepth = 24;

// 6. 常用 API
window.btoa = function(s) { return Buffer.from(s, 'binary').toString('base64'); };
window.atob = function(s) { return Buffer.from(s, 'base64').toString('binary'); };

window.setTimeout = setTimeout;
window.setInterval = setInterval;
window.clearTimeout = clearTimeout;
window.clearInterval = clearInterval;

// 7. XMLHttpRequest 简单模拟 (仅记录, 不真正发送)
function XMLHttpRequest() {
    this.readyState = 0;
    this.status = 200;
    this.responseText = '{}';
}
XMLHttpRequest.prototype.open = function(method, url) {
    console.log('[XHR Mock] open:', method, url);
};
XMLHttpRequest.prototype.send = function(data) {
    console.log('[XHR Mock] send:', data);
    if (this.onreadystatechange) {
        this.readyState = 4;
        this.onreadystatechange();
    }
};
XMLHttpRequest.prototype.setRequestHeader = function() {};
```

### 环境检测对抗

JSVMP 通常会检测运行环境是否是真实浏览器：

```javascript
// 常见检测点及对策

// 检测 1: window === this (全局上下文)
// 对策: 确保 window 指向 global
global.window = global;
global.self = global;
global.top = global;
global.parent = global;

// 检测 2: toString 检测 (检查原生函数)
// 很多 VMP 会检查 document.createElement.toString() 是否返回 "function createElement() { [native code] }"
// 对策: 修改 Function.prototype.toString
(function() {
    var _origToString = Function.prototype.toString;
    var _nativeMap = new Map();

    function patchNative(obj, prop) {
        if (obj[prop]) {
            _nativeMap.set(obj[prop], 'function ' + prop + '() { [native code] }');
        }
    }

    patchNative(document, 'createElement');
    patchNative(document, 'getElementById');
    // ... 其他需要伪装的函数

    Function.prototype.toString = function() {
        if (_nativeMap.has(this)) {
            return _nativeMap.get(this);
        }
        return _origToString.call(this);
    };
    // 也要伪装 toString 自身
    _nativeMap.set(Function.prototype.toString,
        'function toString() { [native code] }');
})();

// 检测 3: Proxy 检测
// 一些高级 VMP 会尝试检测对象是否被 Proxy 包装
// 对策: 尽量避免使用 Proxy, 直接定义属性
```

### 使用 Proxy 记录环境访问

在调试阶段，可以用 Proxy 来自动发现 VMP 需要哪些环境属性：

```javascript
// proxy_logger.js - 自动检测 VMP 需要的环境属性
function createLoggingProxy(name, target) {
    return new Proxy(target || {}, {
        get: function(obj, prop) {
            if (prop === Symbol.toPrimitive || prop === Symbol.toStringTag) {
                return undefined;
            }
            var val = obj[prop];
            console.log('[ENV GET] ' + name + '.' + prop + ' =', val);
            if (val === undefined) {
                console.log('[ENV MISS] ' + name + '.' + prop + ' 需要补充!');
            }
            return val;
        },
        set: function(obj, prop, val) {
            console.log('[ENV SET] ' + name + '.' + prop + ' =', val);
            obj[prop] = val;
            return true;
        }
    });
}

// 使用方式
var document = createLoggingProxy('document', { /* 已知属性 */ });
var navigator = createLoggingProxy('navigator', { /* 已知属性 */ });
// 运行 VMP 代码后, 查看日志中的 [ENV MISS], 逐个补充
```

---

## 实战案例

以下以一个典型的 JSVMP 签名生成函数为案例，演示完整的分析流程。

### 场景描述

某网站的请求中携带 `_signature` 参数，该参数由 JavaScript 动态生成。经初步分析，生成逻辑被 JSVMP 保护。

### 第一步：定位签名生成入口

```javascript
// 通过 Hook XMLHttpRequest 或 fetch, 找到 _signature 的生成位置
// 在 Network 面板中找到携带 _signature 的请求
// 搜索 "_signature" 关键字, 或在 Initiator 中追溯调用栈

// 假设定位到以下代码:
var _signature = _0x2f3a(_0x4b7c, _0x1d5e);
// _0x2f3a 就是 VM 入口函数
// _0x4b7c 是字节码起始位置或参数
// _0x1d5e 是待签名的数据
```

### 第二步：分析 VM 结构

```javascript
// 格式化代码后, 找到 VM 调度器
function _0x2f3a(_startIdx, _input) {
    var _G = [3,1,0,5,...];  // 字节码, 数千个数字
    var _s = [];             // 虚拟栈
    var _pc = _startIdx;     // 程序计数器
    var _r = [_input];       // 寄存器, _r[0] = 输入参数
    var _sp = -1;            // 栈指针

    while (true) {
        var _op = _G[_pc++];
        switch (_op) {
            case 0: return _s[_sp];                              // HALT
            case 1: _s[++_sp] = _G[_pc++]; break;               // PUSH_CONST
            case 2: _s[++_sp] = _r[_G[_pc++]]; break;           // PUSH_REG
            case 3: _r[_G[_pc++]] = _s[_sp--]; break;           // STORE_REG
            case 4: _sp--; _s[_sp] = _s[_sp] + _s[_sp+1]; break; // ADD
            case 5: _sp--; _s[_sp] = _s[_sp] - _s[_sp+1]; break; // SUB
            case 6: _sp--; _s[_sp] = _s[_sp] ^ _s[_sp+1]; break; // XOR
            case 7: _sp--; _s[_sp] = _s[_sp] & _s[_sp+1]; break; // AND
            case 8: _sp--; _s[_sp] = _s[_sp] | _s[_sp+1]; break; // OR
            case 9: _sp--; _s[_sp] = _s[_sp] << _s[_sp+1]; break;// SHL
            case 10: _sp--; _s[_sp] = _s[_sp] >>> _s[_sp+1]; break;// USHR
            case 11: _pc = _G[_pc]; break;                       // JMP
            case 12:                                              // JMP_IF
                if (_s[_sp--]) _pc = _G[_pc]; else _pc++;
                break;
            case 13:                                              // CALL
                var _n = _G[_pc++];  // 参数数量
                var _args = _s.splice(_sp - _n + 1, _n); _sp -= _n;
                var _fn = _s[_sp--];
                var _this = _s[_sp--];
                _s[++_sp] = _fn.apply(_this, _args);
                break;
            case 14:                                              // GET_PROP
                _sp--;
                _s[_sp] = _s[_sp][_s[_sp+1]];
                break;
            case 15:                                              // PUSH_THIS
                _s[++_sp] = this;
                break;
            // ... 更多 handler
        }
    }
}
```

### 第三步：编写反汇编器

```javascript
// disasm.js - 简易反汇编器
function disassemble(G, startPC, endPC) {
    var pc = startPC;
    var output = [];

    var opNames = {
        0: ['HALT', 0],
        1: ['PUSH_CONST', 1],
        2: ['PUSH_REG', 1],
        3: ['STORE_REG', 1],
        4: ['ADD', 0],
        5: ['SUB', 0],
        6: ['XOR', 0],
        7: ['AND', 0],
        8: ['OR', 0],
        9: ['SHL', 0],
        10: ['USHR', 0],
        11: ['JMP', 1],
        12: ['JMP_IF', 1],
        13: ['CALL', 1],
        14: ['GET_PROP', 0],
        15: ['PUSH_THIS', 0],
    };

    while (pc < endPC) {
        var addr = pc;
        var op = G[pc++];
        var info = opNames[op];

        if (!info) {
            output.push(addr + ': UNKNOWN_' + op);
            continue;
        }

        var line = addr.toString().padStart(6, '0') + ': ' + info[0].padEnd(12);

        // 读取操作数
        for (var i = 0; i < info[1]; i++) {
            line += ' ' + G[pc++];
        }

        output.push(line);
    }

    return output.join('\n');
}

// 使用示例
// console.log(disassemble(_G, 0, 100));
//
// 输出:
// 000000: PUSH_REG     0
// 000002: PUSH_CONST   10
// 000004: AND
// 000005: STORE_REG    1
// 000007: PUSH_REG     0
// 000009: PUSH_CONST   8
// 000011: USHR
// ...
```

### 第四步：分析执行轨迹

```text
PC     | OP          | Stack (top)          | 说明
-------|-------------|----------------------|------------------
000000 | PUSH_REG 0  | [input_data]         | 加载输入
000002 | PUSH_CONST  | [input_data, 0xFF]   | 加载掩码
000004 | AND         | [input_data & 0xFF]  | 取低8位
000005 | STORE_REG 1 | []                   | 存入 r1
000007 | PUSH_REG 0  | [input_data]         | 再次加载输入
000009 | PUSH_CONST  | [input_data, 8]      | 加载移位量
000011 | USHR        | [input_data >>> 8]   | 右移8位
000012 | STORE_REG 2 | []                   | 存入 r2
  ...  |    ...      |       ...            | ...

=> 还原逻辑: 这段代码在对输入做逐字节拆分, 类似:
   r1 = input & 0xFF;
   r2 = (input >>> 8) & 0xFF;
   r3 = (input >>> 16) & 0xFF;
   r4 = (input >>> 24) & 0xFF;
   => 这是一个常见的 32 位整数拆字节操作
```

---

## 自动化工具

### 现有工具与项目

| 工具 | 说明 | 链接/备注 |
|---|---|---|
| AST Explorer | 在线查看 JS AST 结构 | astexplorer.net |
| Babel | JS 编译器框架，可用于 AST 分析和代码变换 | babeljs.io |
| estools/escodegen | AST 代码生成库 | npm: escodegen |
| de4js | 在线 JS 反混淆工具 | de4js.com |
| jsvmp-decompiler | 社区 JSVMP 反编译项目 | GitHub 搜索 |
| Chrome DevTools | 断点、条件日志、覆盖 | 内置 |
| Frida | 动态 Hook 框架 | frida.re |
| mitmproxy | 中间人代理，可修改 JS 响应 | mitmproxy.org |

### 自定义跟踪脚本模板

```javascript
// trace_template.js - 可复用的 VMP 跟踪模板
(function() {
    'use strict';

    // ========== 配置区 ==========
    var VM_DISPATCHER_FUNC = '_0x2f3a';   // VM 调度器函数名
    var BYTECODE_VAR = '_G';               // 字节码数组变量名
    var PC_VAR = '_pc';                    // PC 变量名
    var STACK_VAR = '_s';                  // 栈变量名
    var MAX_LOG_ENTRIES = 10000;            // 最大记录条数

    // ========== 跟踪逻辑 ==========
    var traceLog = [];
    var traceCount = 0;

    function logInstruction(pc, opcode, stack, sp) {
        if (traceCount >= MAX_LOG_ENTRIES) return;
        traceLog.push({
            pc: pc,
            op: opcode,
            stackTop: stack[sp],
            stackSize: sp + 1,
            timestamp: Date.now()
        });
        traceCount++;
    }

    // 导出分析结果
    function exportTrace() {
        var blob = new Blob(
            [JSON.stringify(traceLog, null, 2)],
            { type: 'application/json' }
        );
        var url = URL.createObjectURL(blob);
        var a = document.createElement('a');
        a.href = url;
        a.download = 'vm_trace_' + Date.now() + '.json';
        a.click();
        console.log('Trace exported:', traceLog.length, 'entries');
    }

    // 统计 opcode 使用频率
    function analyzeTrace() {
        var freq = {};
        traceLog.forEach(function(entry) {
            freq[entry.op] = (freq[entry.op] || 0) + 1;
        });
        console.table(
            Object.keys(freq)
                .sort(function(a, b) { return freq[b] - freq[a]; })
                .map(function(op) {
                    return { opcode: op, count: freq[op] };
                })
        );
    }

    // 挂载到 window 供手动调用
    window.__vmTrace = {
        log: traceLog,
        export: exportTrace,
        analyze: analyzeTrace
    };

    console.log('[VMP Tracer] Ready. Use __vmTrace.export() to save, __vmTrace.analyze() for stats.');
})();
```

### 使用 Babel 自动标注 Handler

```javascript
// label_handlers.js - 使用 Babel 自动分析 switch case
const parser = require('@babel/parser');
const traverse = require('@babel/traverse').default;
const generate = require('@babel/generator').default;
const t = require('@babel/types');
const fs = require('fs');

const code = fs.readFileSync('vm_code.js', 'utf8');
const ast = parser.parse(code);

traverse(ast, {
    SwitchCase(path) {
        const testVal = path.node.test;
        if (!testVal || !t.isNumericLiteral(testVal)) return;

        const caseNum = testVal.value;
        const body = path.node.consequent;

        // 分析 case body 中的操作
        var label = 'UNKNOWN';
        const bodyCode = body.map(n => generate(n).code).join('; ');

        // 简单的模式匹配来猜测 opcode 功能
        if (/\.push\(/.test(bodyCode)) label = 'PUSH_*';
        if (/\.pop\(/.test(bodyCode)) label = 'POP / STORE_*';
        if (/\+\s/.test(bodyCode) && /\[\w+\s*-/.test(bodyCode)) label = 'ADD';
        if (/\-\s/.test(bodyCode) && /\[\w+\s*-/.test(bodyCode)) label = 'SUB';
        if (/\^\s/.test(bodyCode)) label = 'XOR';
        if (/return/.test(bodyCode)) label = 'HALT / RETURN';
        if (/apply|call/.test(bodyCode)) label = 'CALL';
        if (/\=\s*\w+\[\w+\]/.test(bodyCode) && !/pc|PC/.test(bodyCode)) label = 'GET_PROP';

        // 添加注释
        path.node.leadingComments = path.node.leadingComments || [];
        path.node.leadingComments.push({
            type: 'CommentLine',
            value: ' OP ' + caseNum + ': ' + label
        });

        console.log('Case', caseNum, '->', label);
    }
});

const output = generate(ast, { comments: true }).code;
fs.writeFileSync('vm_code_annotated.js', output);
console.log('Done! Annotated code saved to vm_code_annotated.js');
```

---

## 防御与对抗

### VMP 作者常用的加强手段

**1. 多层嵌套 VM**

将 VM 解释器本身也用另一个 VM 保护，形成嵌套结构：

```text
外层 VM 执行 -> 内层 VM 字节码 -> 内层 VM 执行 -> 目标逻辑字节码
```

这使得分析者不仅要还原目标逻辑，还要先还原内层 VM 本身。

**2. 动态 Opcode 映射**

每次生成的字节码使用不同的 opcode 编号映射，使得固定的反汇编器失效：

```javascript
// 版本 A: case 1 = ADD, case 2 = SUB
// 版本 B: case 1 = JMP, case 2 = PUSH
// 每次构建都会随机打乱映射关系
```

**3. Opcode 融合**

将多个简单操作合并为一个复合 opcode，增加 handler 数量和分析难度：

```javascript
// 普通: PUSH_LOCAL 0; PUSH_CONST 5; ADD;  (3条指令)
// 融合: ADD_LOCAL_CONST 0, 5;              (1条指令)
case 47:  // ADD_LOCAL_CONST (融合指令)
    var slot = _G[_pc++];
    var constVal = _G[_pc++];
    _s[++_sp] = _r[slot] + constVal;
    break;
```

**4. 环境指纹绑定**

将字节码的解密密钥绑定到浏览器环境指纹（如 Canvas 指纹、WebGL 信息等），使得在非目标环境中无法正确解码字节码。

**5. 运行时完整性校验**

VM 在执行过程中定期校验自身代码的完整性（如计算 hash），检测是否被篡改或注入了跟踪代码：

```javascript
// 简化示例
case 99: // SELF_CHECK
    var vmCode = _0x2f3a.toString();
    var hash = crc32(vmCode);
    if (hash !== EXPECTED_HASH) {
        // 检测到篡改, 走错误逻辑或直接崩溃
        _pc = TRAP_ADDRESS;
    }
    break;
```

**6. 反调试指令**

在字节码中嵌入检测调试器的指令：

```javascript
case 98: // ANTI_DEBUG
    var start = performance.now();
    // 执行一些操作
    var elapsed = performance.now() - start;
    if (elapsed > 100) {
        // 时间异常, 可能在单步调试
        _pc = TRAP_ADDRESS;
    }
    break;
```

### 对抗策略总结

| 加强手段 | 对抗方法 |
|---|---|
| 多层嵌套 VM | 逐层分析，从外到内；优先用动态分析定位关键逻辑 |
| 动态 Opcode 映射 | 动态跟踪而非依赖静态 opcode 编号；按 handler 行为分类 |
| Opcode 融合 | 将融合指令拆解为基本操作序列来理解 |
| 环境指纹绑定 | 完善补环境，或直接在真实浏览器中分析 |
| 完整性校验 | Hook `Function.prototype.toString` 返回原始代码 |
| 反调试指令 | Hook `performance.now` / `Date.now` 返回稳定值 |
| `debugger` 陷阱 | Chrome DevTools 中禁用 "Pause on debugger statements" |
| 代码自修改 | 在修改点下断点，记录修改前后的差异 |

### 通用反反调试脚本

```javascript
// anti_anti_debug.js - 在目标页面加载前注入
(function() {
    'use strict';

    // 1. 禁用 debugger 语句
    // 通过 hook Function 构造器来拦截动态生成的 debugger
    var _origFunction = Function;
    Function = function() {
        var args = Array.from(arguments);
        var body = args[args.length - 1];
        if (typeof body === 'string' && body.indexOf('debugger') !== -1) {
            args[args.length - 1] = body.replace(/debugger/g, '');
        }
        return _origFunction.apply(this, args);
    };
    Function.prototype = _origFunction.prototype;
    Object.defineProperty(Function, 'name', { value: 'Function' });

    // 2. 稳定化时间函数 (防止时间检测)
    var _startTime = Date.now();
    var _fakeElapsed = 0;
    var _origDateNow = Date.now;
    var _origPerfNow = performance.now.bind(performance);

    Date.now = function() {
        _fakeElapsed += Math.random() * 2 + 0.5;  // 模拟正常耗时
        return _startTime + Math.floor(_fakeElapsed);
    };

    performance.now = function() {
        return _fakeElapsed;
    };

    // 3. 保护 console 对象
    // 有些 VMP 会重写 console 来阻止日志输出
    var _console = {};
    ['log', 'warn', 'error', 'info', 'debug', 'trace', 'table'].forEach(function(method) {
        _console[method] = console[method].bind(console);
    });
    Object.defineProperty(window, '__console', {
        value: _console,
        writable: false,
        configurable: false
    });

    console.log('[Anti-Anti-Debug] Protections active');
})();
```

---

## 常用工具

- **浏览器开发者工具**：用于下断点、单步调试和观察变量。

- **Frida**：用于 Hook 关键函数，实现动态跟踪。

- **Babel**：用于将 JavaScript 代码解析成 AST，辅助静态分析。

- **AST Explorer**：一个在线工具，可以方便地查看代码对应的 AST 结构。

- **IDA Pro / Ghidra**：虽然主要用于原生代码，但它们强大的反汇编和反编译功能可以为理解复杂的 JavaScript 虚拟机逻辑提供借鉴。

- **mitmproxy / Charles**：HTTP 代理工具，用于拦截和修改 JS 文件，注入跟踪代码。

- **Node.js**：用于在浏览器外执行 VMP 代码，配合补环境技术。

- **Overrides (Chrome)**：DevTools 本地覆盖功能，可持久化修改线上 JS 文件。
