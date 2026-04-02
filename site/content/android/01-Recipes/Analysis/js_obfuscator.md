---
title: "JavaScript Obfuscator (OB 混淆) 分析"
date: 2025-04-20
type: posts
tags: ["代理池", "逆向分析", "加密分析", "Android", "反混淆"]
weight: 10
---

# JavaScript Obfuscator (OB 混淆) 分析

> **📚 前置知识**
>
> 本配方涉及以下核心技术，建议先阅读相关章节：
>
> - **JavaScript 基础** - 理解 AST、作用域、闭包等概念
> - **浏览器开发者工具** - 使用 Chrome DevTools 进行调试

`javascript-obfuscator` 是一个非常流行和强大的开源工具，用于混淆和保护 JavaScript 代码。它的混淆产物通常被称为"OB 混淆"。OB 混淆通过多种手段的组合，使得代码难以阅读、理解和调试。

---

## JavaScript 混淆技术概述

### 为什么 App 要对 JS 代码进行混淆？

在 Android 逆向工程中，JavaScript 代码出现的频率远超初学者的想象。与 Native 层的 C/C++ 代码不同，JS 本质上是**解释执行的脚本语言**，其源代码或经过简单打包的 bundle 文件通常以**明文形式**存在于 APK 内部。这意味着，如果不做任何保护，攻击者只需解压 APK，就能直接阅读核心业务逻辑。

混淆 JS 代码的主要动机包括：

| 动机 | 说明 |
|------|------|
| **知识产权保护** | 防止竞品抄袭核心算法（如加密签名、风控逻辑） |
| **反爬虫** | 隐藏请求参数的生成逻辑，增加自动化爬虫的成本 |
| **防篡改** | 增加攻击者修改代码并重新打包的难度 |
| **安全加固** | 隐藏 API 密钥、加密密钥等敏感信息 |
| **反调试** | 通过 `debugger` 陷阱和检测手段阻碍动态分析 |

### JS 代码在 Android 应用中的存在形式

Android 应用中 JavaScript 代码主要以以下形式出现：

**1. WebView 内嵌网页**

这是最常见的场景。许多 App 使用 `android.webkit.WebView` 来加载 H5 页面，这些页面的 JS 代码负责：

- 页面渲染与交互
- 调用 `JSBridge` 与 Native 层通信
- 生成请求签名参数

```java
// Android 端加载 WebView
WebView webView = new WebView(this);
webView.getSettings().setJavaScriptEnabled(true);
webView.addJavascriptInterface(new JsBridge(), "NativeBridge");
webView.loadUrl("https://app.example.com/hybrid/index.html");
```

**2. React Native 应用**

React Native 应用将业务逻辑写在 JavaScript 中，打包后生成 `index.android.bundle` 文件，通常位于 APK 的 `assets/` 目录下。这个 bundle 文件包含了应用的**全部 JS 业务代码**，是逆向的重点目标。

```text
assets/
├── index.android.bundle      # 核心 JS 代码（可能已混淆）
├── index.android.bundle.meta  # 元数据
└── ...
```

**3. 混合开发框架 (Cordova / Ionic / uni-app)**

使用 Cordova、Ionic、uni-app 等框架开发的应用，其核心逻辑几乎全部由 JS 实现。代码通常存放在 APK 的 `assets/www/` 目录中。

**4. 独立 JS 引擎**

部分应用会内嵌 V8、QuickJS 或 Hermes 等 JS 引擎，用于执行动态下发的 JS 脚本。这类场景常见于：

- 动态化配置（热更新）
- 反爬虫参数生成（如某些电商 App 的签名逻辑）
- 游戏内脚本引擎

---

## 核心混淆技术

OB 混淆主要依赖于以下几种关键技术：

### 1. 字符串混淆 (String Concealing)

- **字符串数组**：将代码中所有的字符串（特别是敏感信息）提取出来，放入一个或多个巨大的数组中。

- **编码与加密**：这些字符串通常会使用 Base64、RC4 或其他自定义算法进行编码或加密。

- **解码函数**：提供一个或多个解码函数。在代码执行时，通过调用 `decoder("0x1")` 这样的形式来获取原始字符串。

- **数组乱序与自愈**：为了防止静态分析，字符串数组的顺序会在脚本执行初期被动态打乱，解码函数也会随之调整，增加了静态还原的难度。

### 2. 控制流平坦化 (Control Flow Flattening)

这是 OB 混淆最核心、最复杂的特征之一。

- **状态机转换**：将原始代码块（如函数体内的语句）分割成多个小的代码片段，并放入一个巨大的 `while` 循环中的 `switch` 结构里。

- **状态变量**：用一个状态变量（程序计数器）来控制 `switch` 的执行顺序。每个 `case` 执行完毕后，会更新状态变量，决定下一个要执行的 `case`。

- **逻辑打断**：原始线性的代码逻辑被完全打乱，变成了在一个巨大的循环中无序跳转，使得人工跟踪变得极其困难。

### 3. 代码转换与编码 (Code Transformation)

- **变量名混淆 (Identifier Mangling)**：将有意义的变量名、函数名和属性名替换成无意义的短字符，如 `_0xabc123`。

- **数字常量替换**：将代码中的数字常量（如 `123`）替换成十六进制字符串表达式（如 `0x7b`），或者更复杂的表达式，增加阅读难度。

- **代理函数 (Proxy Functions)**：将简单的二元运算（如 `a + b`）或对象属性访问（`obj.prop`）替换成对一个代理函数的调用，例如 `add(a, b)`。这使得批量替换和模式识别变得更加困难。

- **死代码注入 (Dead Code Injection)**：在代码中插入一些永远不会被执行的、但看起来很复杂的逻辑分支（通常与不透明谓词结合），用来迷惑分析者。

### 4. 反调试与反格式化 (Anti-Debugging)

- **`debugger` 语句**：在代码中插入 `debugger;` 语句，并且通常会将其包裹在一个无限循环的函数中。当开发者工具打开时，程序会立即暂停并陷入这个循环，阻碍动态调试。

- **函数重绑定**：通过 `Function.prototype.constructor` 或 `eval` 来执行代码，使得常规的断点难以命中。

- **反格式化**：检测代码是否被美化或格式化，如果发现，则可能进入死循环或执行错误逻辑。

---

## 常见混淆手段分类

为了系统地理解和应对 JS 混淆，我们将常见手段分为以下几个大类：

### 分类总览

| 分类 | 手段 | 复杂度 | 可逆性 |
|------|------|--------|--------|
| **标识符混淆** | 变量/函数重命名为 `_0x` 前缀 | 低 | 不可逆（原名丢失） |
| **字符串混淆** | Base64/RC4 编码 + 字符串表 | 中 | 可逆 |
| **控制流混淆** | while-switch 状态机 | 高 | 可逆（需 AST） |
| **死代码注入** | 不透明谓词 + 无效分支 | 中 | 可逆 |
| **eval 打包** | 将代码包裹在 eval() 中 | 低 | 可逆 |
| **代理函数** | 运算符替换为函数调用 | 中 | 可逆 |
| **反调试** | debugger 陷阱、时间检测 | 低 | 可绕过 |

### 变量重命名 (Identifier Mangling)

变量重命名是最基础的混淆手段。它将所有局部变量、函数名和参数名替换为无意义的标识符。

**混淆前：**

```javascript
function calculateDiscount(price, discountRate) {
    let discountAmount = price * discountRate;
    let finalPrice = price - discountAmount;
    return finalPrice;
}
```

**混淆后：**

```javascript
function _0x3a1b(_0x4c2d, _0x5e3f) {
    let _0x6a4b = _0x4c2d * _0x5e3f;
    let _0x7b5c = _0x4c2d - _0x6a4b;
    return _0x7b5c;
}
```

> **注意**：变量重命名是**不可逆**的，因为原始名称在混淆过程中被永久丢弃。逆向时只能根据上下文语义手动重命名。

### 字符串编码与字符串表

将字符串提取到一个集中的数组中，并通过索引 + 解码函数访问：

```javascript
// 混淆后的字符串表
var _0xstr = ['Y29uc29sZQ==', 'bG9n', 'SGVsbG8gV29ybGQ='];

// 解码函数
function _0xdecode(_0xindex) {
    return atob(_0xstr[_0xindex]);
}

// 使用：_0xdecode(0x0) => "console"
//       _0xdecode(0x1) => "log"
//       _0xdecode(0x2) => "Hello World"
```

### eval 打包 (Eval Packing)

eval 打包将整段 JS 代码编码为字符串，然后通过 `eval()` 在运行时解码执行：

```javascript
// Dean Edwards Packer 典型输出
eval(function(p,a,c,k,e,r){e=String;if(!''.replace(/^/,String)){
while(c--)r[c]=k[c]||c;k=[function(e){return r[e]}];
e=function(){return'\\w+'};c=1};while(c--)if(k[c])
p=p.replace(new RegExp('\\b'+e(c)+'\\b','g'),k[c]);return p}
('0.1("2 3")',4,4,'console|log|Hello|World'.split('|'),0,{}))
```

**破解方法**：将 `eval` 替换为 `console.log`，即可打印出解码后的原始代码。

### 死代码注入 (Dead Code Injection)

通过不透明谓词（opaque predicates）注入永远不会执行的代码路径：

```javascript
// 混淆后 —— 死代码示例
if ('xKqRt' !== 'xKqRt') {
    // 这段代码永远不会执行
    var _0xfake = _0x3a1b(0x1a, 0x2b);
    _0x4c2d['push'](_0xfake['toString']());
    return _0x5e3f['apply'](this, arguments);
} else {
    // 真正的逻辑在这里
    result = input * 2 + 1;
}
```

识别死代码的关键：查找**字符串字面量的恒等比较**（`'abc' !== 'abc'` 或 `'abc' === 'def'`），这类条件永远为 `true` 或 `false`。

---

## 字符串加密与解密

字符串混淆是 OB 混淆中最常见也最容易突破的环节。理解各种编码方式及其解密方法，是反混淆的第一步。

### 常见编码方式

**1. Base64 编码**

最基本的字符串编码方式，在浏览器中可直接使用 `atob()` 解码：

```javascript
// 编码
btoa("Hello World")  // => "SGVsbG8gV29ybGQ="

// 解码
atob("SGVsbG8gV29ybGQ=")  // => "Hello World"
```

**识别特征**：字符串仅包含 `A-Z, a-z, 0-9, +, /, =`，长度为 4 的倍数（含末尾填充 `=`）。

**2. 十六进制编码 (Hex Encoding)**

将每个字符转换为 `\xNN` 形式的十六进制：

```javascript
// "Hello" 的十六进制编码
var s = "\x48\x65\x6c\x6c\x6f";
console.log(s);  // => "Hello"
```

**3. Unicode 转义**

使用 `\uNNNN` 或 `\u{NNNNN}` 格式编码字符：

```javascript
var s = "\u0048\u0065\u006c\u006c\u006f";
console.log(s);  // => "Hello"
```

**4. RC4 自定义加密**

`javascript-obfuscator` 的高级模式使用 RC4 加密字符串。解码函数通常包含以下特征：

```javascript
// 典型的 RC4 解码函数结构
function _0xrc4(_0xstr, _0xkey) {
    var _0xs = [], _0xj = 0, _0xres = '';
    // S-box 初始化
    for (var _0xi = 0; _0xi < 256; _0xi++) {
        _0xs[_0xi] = _0xi;
    }
    for (_0xi = 0; _0xi < 256; _0xi++) {
        _0xj = (_0xj + _0xs[_0xi] + _0xkey['charCodeAt'](_0xi % _0xkey['length'])) % 256;
        var _0xtmp = _0xs[_0xi];
        _0xs[_0xi] = _0xs[_0xj];
        _0xs[_0xj] = _0xtmp;
    }
    // PRGA
    _0xi = 0; _0xj = 0;
    for (var _0xk = 0; _0xk < _0xstr['length']; _0xk++) {
        _0xi = (_0xi + 1) % 256;
        _0xj = (_0xj + _0xs[_0xi]) % 256;
        var _0xtmp = _0xs[_0xi];
        _0xs[_0xi] = _0xs[_0xj];
        _0xs[_0xj] = _0xtmp;
        _0xres += String['fromCharCode'](_0xstr['charCodeAt'](_0xk) ^
                  _0xs[(_0xs[_0xi] + _0xs[_0xj]) % 256]);
    }
    return _0xres;
}
```

### 数组旋转 (Array Rotation)

OB 混淆的标志性特征之一是**字符串数组旋转函数**。在脚本执行之初，一个 IIFE（立即调用函数表达式）会将字符串数组进行若干次 `push/shift` 操作，打乱原始顺序：

```javascript
// 字符串数组
var _0xarr = ['bG9n', 'Y29uc29sZQ==', 'SGVsbG8=', ...];

// 旋转函数 —— 在脚本开头执行
(function(_0xdata, _0xcount) {
    var _0xrotate = function(_0xnum) {
        while (--_0xnum) {
            _0xdata['push'](_0xdata['shift']());
        }
    };
    _0xrotate(++_0xcount);
}(_0xarr, 0x1a3));
```

**解密策略**：

1. 将字符串数组和旋转函数提取出来
2. 在 Node.js 中执行旋转逻辑，得到最终顺序的数组
3. 再对数组中的每个元素调用解码函数（Base64 / RC4），得到明文

### 实用解密脚本

以下是一个在 Node.js 中批量解密 OB 混淆字符串的通用模板：

```javascript
// step1: 将混淆代码中的字符串数组和旋转函数复制到这里
var _0x1234 = ['encrypted_str_1', 'encrypted_str_2', ...];
// (粘贴旋转函数并执行)

// step2: 复制解码函数
function _0xdecode(index, key) {
    // ... 从混淆代码中复制
}

// step3: 遍历所有可能的索引，输出解密结果
for (var i = 0; i < 500; i++) {
    try {
        var result = _0xdecode(i);
        if (result) {
            console.log(`_0xdecode(0x${i.toString(16)}) => "${result}"`);
        }
    } catch(e) {}
}
```

---

## 控制流平坦化

控制流平坦化 (Control Flow Flattening, CFF) 是 OB 混淆中最复杂、还原难度最高的技术。理解其工作原理是成功反混淆的关键。

### 工作原理

原始代码是线性顺序执行的：

```javascript
// 原始代码
function process(input) {
    let a = input + 1;       // 步骤 1
    let b = a * 2;           // 步骤 2
    let c = b - 3;           // 步骤 3
    return c;                // 步骤 4
}
```

经过控制流平坦化后，代码变成了一个 `while-switch` 状态机：

```javascript
// 平坦化后
function process(input) {
    var _0xstate = '3|0|1|4|2'['split']('|');
    var _0xidx = 0;
    while (true) {
        switch (_0xstate[_0xidx++]) {
            case '0':
                var _0xa = input + 0x1;
                continue;
            case '1':
                var _0xb = _0xa * 0x2;
                continue;
            case '2':
                return _0xc;
            case '3':
                var _0xinit = undefined;
                continue;
            case '4':
                var _0xc = _0xb - 0x3;
                continue;
        }
        break;
    }
}
```

**执行流程**：状态字符串 `'3|0|1|4|2'` 决定了 case 的执行顺序为 3 -> 0 -> 1 -> 4 -> 2，即原始逻辑的正确顺序。

### 识别模式

控制流平坦化的代码具有以下显著特征：

| 特征 | 描述 |
|------|------|
| `while(true)` 或 `while(!![])` | 外层包裹无限循环 |
| `switch` 语句 | 内层包含多个 case 分支 |
| 状态字符串 `'N\|N\|N...'['split']('\|')` | 用管道符分割的数字序列 |
| 每个 case 以 `continue` 结尾 | 跳回循环头继续分发 |
| 最后一个有效 case 无 `continue` | 函数返回或循环 break |

### 手动还原步骤

1. **定位状态序列**：找到类似 `'3|0|1|4|2'['split']('|')` 的表达式
2. **解析执行顺序**：将字符串按 `|` 分割，得到 `[3, 0, 1, 4, 2]`
3. **按序提取代码块**：按顺序取出每个 case 中的代码
4. **移除控制结构**：删除 `while`、`switch`、`continue` 和状态变量
5. **组合为线性代码**：将提取的代码块顺序拼接

### AST 自动化还原

手动还原效率低下且容易出错。以下是使用 Babel 自动还原控制流平坦化的核心逻辑：

```javascript
const parser = require('@babel/parser');
const traverse = require('@babel/traverse').default;
const generate = require('@babel/generator').default;
const t = require('@babel/types');

function deobfuscateCFF(code) {
    const ast = parser.parse(code);

    traverse(ast, {
        WhileStatement(path) {
            // 检查是否是 while(true) + switch 结构
            const body = path.get('body');
            if (!body.isSwitchStatement() &&
                !(body.isBlockStatement() &&
                  body.get('body.0').isSwitchStatement())) {
                return;
            }

            const switchNode = body.isSwitchStatement()
                ? body
                : body.get('body.0');

            // 查找状态序列
            // 通常在 while 之前的变量声明中
            const parentBlock = path.parentPath;
            const siblings = parentBlock.get('body') || [];
            const whileIdx = siblings.findIndex(s => s === path);

            // 寻找状态变量声明（形如 var xxx = 'N|N|N'.split('|') ）
            let orderArray = null;
            for (let i = whileIdx - 1; i >= 0; i--) {
                const sibling = siblings[i];
                if (sibling.isVariableDeclaration()) {
                    const init = sibling.get('declarations.0.init');
                    // 检查是否是 'N|N|N'.split('|') 调用
                    if (init.isCallExpression()) {
                        try {
                            const evaluated = init.evaluate();
                            if (evaluated.confident &&
                                Array.isArray(evaluated.value)) {
                                orderArray = evaluated.value;
                                sibling.remove();
                                break;
                            }
                        } catch(e) {}
                    }
                }
            }

            if (!orderArray) return;

            // 按照状态序列提取并排列 case 代码块
            const cases = switchNode.node
                          ? switchNode.node.cases
                          : switchNode.cases;
            const caseMap = {};
            cases.forEach(c => {
                caseMap[c.test.value] = c.consequent.filter(
                    s => !t.isContinueStatement(s) &&
                         !t.isBreakStatement(s)
                );
            });

            const newBody = [];
            for (const key of orderArray) {
                if (caseMap[key]) {
                    newBody.push(...caseMap[key]);
                }
            }

            // 替换 while 循环为线性代码
            path.replaceWithMultiple(newBody);
        }
    });

    return generate(ast).code;
}
```

---

## AST 反混淆

AST (Abstract Syntax Tree，抽象语法树) 是 JS 反混淆的核心武器。通过将代码解析为 AST，我们可以编写精确的转换规则，批量地还原混淆操作。

### Babel 工具链

反混淆工作主要使用以下 Babel 包：

| 包名 | 用途 |
|------|------|
| `@babel/parser` | 将 JS 代码解析为 AST |
| `@babel/traverse` | 遍历和修改 AST 节点 |
| `@babel/generator` | 将 AST 重新生成为 JS 代码 |
| `@babel/types` | AST 节点类型的工具函数 |

安装依赖：

```bash
npm install @babel/parser @babel/traverse @babel/generator @babel/types
```

### 反混淆脚本模板

以下是一个通用的 AST 反混淆脚本框架：

```javascript
const fs = require('fs');
const parser = require('@babel/parser');
const traverse = require('@babel/traverse').default;
const generate = require('@babel/generator').default;
const t = require('@babel/types');

// 读取混淆代码
const code = fs.readFileSync('obfuscated.js', 'utf-8');
const ast = parser.parse(code);

// ========== Pass 1: 常量折叠 ==========
// 将 0x1a + 0x2b 计算为 69
traverse(ast, {
    BinaryExpression(path) {
        const { confident, value } = path.evaluate();
        if (confident && typeof value === 'number') {
            path.replaceWith(t.numericLiteral(value));
        }
        if (confident && typeof value === 'string') {
            path.replaceWith(t.stringLiteral(value));
        }
    }
});

// ========== Pass 2: 十六进制数字还原 ==========
// 将 0x7b 还原为 123
traverse(ast, {
    NumericLiteral(path) {
        // Babel 默认会输出十进制，无需额外操作
        // 但如果有 extra.raw 保留了十六进制，需要清除
        if (path.node.extra) {
            delete path.node.extra;
        }
    }
});

// ========== Pass 3: 对象属性调用还原 ==========
// 将 obj['prop'] 还原为 obj.prop（当属性名是合法标识符时）
traverse(ast, {
    MemberExpression(path) {
        if (path.node.computed &&
            t.isStringLiteral(path.node.property)) {
            const propName = path.node.property.value;
            if (/^[a-zA-Z_$][a-zA-Z0-9_$]*$/.test(propName)) {
                path.node.property = t.identifier(propName);
                path.node.computed = false;
            }
        }
    }
});

// ========== Pass 4: 死代码移除 ==========
// 移除 if ('xxx' !== 'xxx') { ... } 类型的死代码
traverse(ast, {
    IfStatement(path) {
        const test = path.get('test');
        const { confident, value } = test.evaluate();
        if (confident) {
            if (value) {
                // 条件恒为 true，保留 consequent
                path.replaceWithMultiple(
                    path.node.consequent.type === 'BlockStatement'
                        ? path.node.consequent.body
                        : [path.node.consequent]
                );
            } else {
                // 条件恒为 false
                if (path.node.alternate) {
                    path.replaceWithMultiple(
                        path.node.alternate.type === 'BlockStatement'
                            ? path.node.alternate.body
                            : [path.node.alternate]
                    );
                } else {
                    path.remove();
                }
            }
        }
    }
});

// ========== Pass 5: 代理函数内联 ==========
// 将 function _0xadd(a, b) { return a + b; } 的调用还原为 a + b
traverse(ast, {
    FunctionDeclaration(path) {
        const body = path.get('body.body');
        if (body.length !== 1 || !body[0].isReturnStatement()) return;

        const returnArg = body[0].get('argument');
        if (!returnArg.isBinaryExpression() &&
            !returnArg.isLogicalExpression()) return;

        const funcName = path.node.id.name;
        const params = path.node.params.map(p => p.name);
        const binding = path.scope.getBinding(funcName);
        if (!binding) return;

        // 检查所有引用是否都是调用表达式
        const refs = binding.referencePaths;
        const allCalls = refs.every(ref =>
            ref.parentPath.isCallExpression() &&
            ref.parentPath.get('callee') === ref
        );

        if (allCalls && refs.length > 0) {
            for (const ref of refs) {
                const callPath = ref.parentPath;
                const args = callPath.get('arguments');

                // 构建替换表达式
                const cloned = t.cloneDeep(returnArg.node);
                // 替换参数
                traverse(t.file(t.program([t.expressionStatement(cloned)])), {
                    Identifier(innerPath) {
                        const idx = params.indexOf(innerPath.node.name);
                        if (idx !== -1 && args[idx]) {
                            innerPath.replaceWith(
                                t.cloneDeep(args[idx].node)
                            );
                        }
                    },
                    noScope: true
                });
                callPath.replaceWith(cloned);
            }
            path.remove();
        }
    }
});

// 输出还原后的代码
const output = generate(ast, { comments: false }).code;
fs.writeFileSync('deobfuscated.js', output);
console.log('反混淆完成！输出: deobfuscated.js');
```

### 使用 AST Explorer 辅助分析

[AST Explorer](https://astexplorer.net/) 是一个在线工具，能将 JS 代码实时转换为 AST 树形结构。在编写反混淆脚本前，建议先用它观察混淆代码的 AST 结构：

1. 打开 https://astexplorer.net/
2. 选择解析器为 `@babel/parser`
3. 粘贴混淆代码片段
4. 在右侧面板中观察 AST 节点类型和结构
5. 根据观察到的模式，编写对应的 Babel visitor

---

## WebView 中的 JS 逆向

Android 应用中大量使用 WebView 来加载 H5 页面。使用 Frida 可以在运行时拦截和分析 WebView 中的 JS 执行。

### 拦截 WebView.loadUrl

当 App 通过 `loadUrl("javascript:...")` 向 WebView 注入 JS 代码时，我们可以拦截并记录：

```javascript
// frida -U -f com.target.app -l webview_hook.js

Java.perform(function() {
    var WebView = Java.use('android.webkit.WebView');

    // Hook loadUrl - 拦截所有加载的 URL 和注入的 JS
    WebView.loadUrl.overload('java.lang.String').implementation = function(url) {
        if (url.startsWith('javascript:')) {
            console.log('[WebView.loadUrl] JS 注入:');
            console.log(url.substring(11));  // 去掉 "javascript:" 前缀
            console.log('---');
        } else {
            console.log('[WebView.loadUrl] URL: ' + url);
        }
        return this.loadUrl(url);
    };
});
```

### Hook evaluateJavascript

Android 4.4+ 推荐使用 `evaluateJavascript()` 来执行 JS 并获取返回值：

```javascript
Java.perform(function() {
    var WebView = Java.use('android.webkit.WebView');

    WebView.evaluateJavascript.implementation = function(script, callback) {
        console.log('[evaluateJavascript] 执行脚本:');
        console.log(script);
        console.log('---');

        // 如果有回调，包装它来记录返回值
        if (callback !== null) {
            var ValueCallback = Java.use('android.webkit.ValueCallback');
            var originalCallback = callback;

            var newCallback = Java.registerClass({
                name: 'com.hook.JsCallback',
                implements: [ValueCallback],
                methods: {
                    onReceiveValue: function(value) {
                        console.log('[evaluateJavascript] 返回值: ' + value);
                        originalCallback.onReceiveValue(value);
                    }
                }
            });

            return this.evaluateJavascript(script, newCallback.$new());
        }
        return this.evaluateJavascript(script, callback);
    };
});
```

### 拦截 JSBridge 通信

许多 App 使用 `addJavascriptInterface` 向 WebView 暴露 Java 方法。我们可以 hook 这些接口：

```javascript
Java.perform(function() {
    var WebView = Java.use('android.webkit.WebView');

    // 拦截 addJavascriptInterface，找出所有 Bridge 对象
    WebView.addJavascriptInterface.implementation = function(obj, name) {
        console.log('[JSBridge] 注册接口: ' + name);
        console.log('[JSBridge] 对象类型: ' + obj.getClass().getName());

        // 列出所有暴露的方法
        var methods = obj.getClass().getDeclaredMethods();
        for (var i = 0; i < methods.length; i++) {
            var annotations = methods[i].getAnnotations();
            for (var j = 0; j < annotations.length; j++) {
                if (annotations[j].toString().indexOf('JavascriptInterface') !== -1) {
                    console.log('  -> @JavascriptInterface: ' + methods[i].getName());
                }
            }
        }
        return this.addJavascriptInterface(obj, name);
    };
});
```

### 从 WebView 中导出 JS 源码

使用 Frida 将 WebView 中正在运行的 JS 代码和关键变量导出到文件：

```javascript
Java.perform(function() {
    var WebView = Java.use('android.webkit.WebView');

    // 在页面加载完成后，注入 JS 提取页面中的所有 script 内容
    WebView.loadUrl.overload('java.lang.String').implementation = function(url) {
        var result = this.loadUrl(url);

        if (!url.startsWith('javascript:')) {
            // 延迟执行，等待页面加载完成
            var webview = this;
            setTimeout(function() {
                var extractScript = "javascript:void(function(){" +
                    "var scripts = document.querySelectorAll('script');" +
                    "var result = [];" +
                    "scripts.forEach(function(s, i){" +
                    "  result.push('=== Script ' + i + ' ===');" +
                    "  result.push(s.src || s.textContent.substring(0, 500));" +
                    "});" +
                    "window._extracted = result.join('\\n');" +
                    "}())";
                webview.loadUrl(extractScript);
            }, 3000);
        }
        return result;
    };
});
```

---

## React Native 逆向

React Native (RN) 应用将 JS 代码打包为一个 bundle 文件。逆向 RN 应用的核心在于提取和分析这个 bundle。

### Bundle 文件提取

**步骤 1：解压 APK**

```bash
# 使用 apktool 或直接解压
unzip target.apk -d target_apk

# React Native bundle 文件通常位于 assets 目录
ls target_apk/assets/
# 典型文件：index.android.bundle
```

**步骤 2：判断 Bundle 类型**

React Native 的 bundle 文件有两种格式：

| 类型 | 特征 | 查看方式 |
|------|------|----------|
| **JSC (JavaScriptCore)** | 文件开头为明文 JS 代码 | 直接用文本编辑器打开 |
| **Hermes 字节码** | 文件开头为 `c6 1f bc 03` (魔数) | 需要反编译 |

```bash
# 检查文件类型
xxd target_apk/assets/index.android.bundle | head -1
# 如果看到 c61fbc03，说明是 Hermes 字节码
# 如果看到 var __BUNDLE 或类似 JS 代码，说明是明文 JS
```

### Hermes 字节码反编译

Facebook 的 Hermes 引擎将 JS 编译为字节码以提升启动速度。反编译 Hermes 字节码需要专用工具。

**使用 hermes-dec (hbctool 的继任者)**

```bash
# 安装 hermes-dec
pip install hermes-dec

# 反编译 Hermes 字节码
hermes-dec index.android.bundle -o decompiled_output/

# 输出为可读的 JS 代码
cat decompiled_output/index.js
```

**使用 hbctool**

```bash
# 安装 hbctool
pip install hbctool

# 反汇编为 Hermes Assembly
hbctool disasm index.android.bundle output_dir/

# 查看反汇编结果
ls output_dir/
# instruction.hasm  metadata.json  string.json
```

`string.json` 文件中包含了 bundle 中的所有字符串常量，这对于理解代码逻辑非常有帮助：

```bash
# 搜索关键字符串
python3 -c "
import json
strings = json.load(open('output_dir/string.json'))
for i, s in enumerate(strings):
    if 'api' in s.lower() or 'token' in s.lower() or 'secret' in s.lower():
        print(f'[{i}] {s}')
"
```

### React Native 调试技巧

**通过 Frida Hook RN Bridge**

```javascript
Java.perform(function() {
    // Hook CatalystInstance.jniCallJSFunction
    // 这是 Java 层调用 JS 函数的入口
    var CatalystInstance = Java.use(
        'com.facebook.react.bridge.CatalystInstanceImpl'
    );

    CatalystInstance.jniCallJSFunction.implementation = function(module, method, args) {
        console.log('[RN Bridge] ' + module + '.' + method);
        console.log('  args: ' + args);
        return this.jniCallJSFunction(module, method, args);
    };
});
```

**使用 React Native Debugger 远程调试**

部分 RN 应用在 debug 模式下支持 Chrome 远程调试。即使是 release 版本，也可以通过 Frida 强制开启调试模式：

```javascript
Java.perform(function() {
    // 尝试启用 RN 开发者菜单
    var DevSettingsModule = Java.use(
        'com.facebook.react.devsupport.DevInternalSettings'
    );
    DevSettingsModule.setIsDebuggingRemotely.implementation = function(enabled) {
        console.log('[RN] 强制启用远程调试');
        return this.setIsDebuggingRemotely(true);
    };
});
```

---

## 实用反混淆工具

在实际逆向工作中，通常会结合自动化工具和手动分析。以下是常用工具及其适用场景：

### 工具对比

| 工具 | 类型 | 适用场景 | 地址 |
|------|------|----------|------|
| **de4js** | 在线/离线 | eval 解包、通用反混淆 | https://lelinhtinh.github.io/de4js/ |
| **synchrony** | Node.js CLI | javascript-obfuscator 专用还原 | https://github.com/nicolo-ribaudo/synchrony |
| **js-deobfuscator** | Node.js CLI | OB 混淆通用还原 | https://github.com/nicolo-ribaudo/js-deobfuscator |
| **JStillery** | 在线 | 动态分析 + 代码简化 | https://mindedsecurity.github.io/jstillery/ |
| **AST Explorer** | 在线 | AST 结构查看与调试 | https://astexplorer.net/ |
| **Babel** | Node.js 库 | 自定义 AST 转换脚本 | https://babeljs.io/ |
| **hermes-dec** | Python CLI | Hermes 字节码反编译 | https://github.com/nicolo-ribaudo/hermes-dec |
| **Prettier** | Node.js CLI | 代码格式化美化 | https://prettier.io/ |

### de4js 使用

de4js 支持多种常见的打包方式自动解包：

- **Eval** - `eval(function(p,a,c,k,e,r){...})` 类型
- **Array** - 基于数组的字符串替换
- **_Number** - 数字编码的混淆
- **JSFuck** - 纯符号编码 (`[]()!+`)
- **Obfuscator.io** - obfuscator.io 的输出

使用方式：将混淆代码粘贴到输入框，勾选对应的混淆类型，点击解码即可。

### synchrony 使用

synchrony 是目前还原 `javascript-obfuscator` 输出最有效的自动化工具之一：

```bash
# 安装
npm install -g deobfuscator

# 基本使用
synchrony deobfuscate obfuscated.js -o clean.js

# 指定转换 pass
synchrony deobfuscate obfuscated.js \
  --transform string-decoder \
  --transform control-flow \
  --transform dead-code \
  -o clean.js
```

### 自定义 Babel 插件工作流

当自动化工具无法处理特殊变种时，需要编写自定义的 Babel 插件。推荐的工作流：

```text
混淆代码 ──→ AST Explorer 分析结构
                    │
                    ↓
            编写 Babel visitor
                    │
                    ↓
         ┌──→ Pass 1: 字符串解密
         │    Pass 2: 常量折叠
         │    Pass 3: 代理函数内联
         │    Pass 4: 控制流还原
         │    Pass 5: 死代码移除
         │    Pass 6: 属性访问还原
         │         │
         │         ↓
         │    检查输出结果
         │         │
         └── 不满意 ──┘
                    │
                  满意
                    ↓
              Prettier 格式化
                    ↓
                最终输出
```

---

## 实战案例

> **💡 思路一句话**: 先用 AST 解析器还原控制流（反平坦化）→ 再用字符串解密脚本批量还原常量 → 最后手动重命名变量恢复可读性。JS 混淆的还原比 native 混淆容易得多，因为有完善的 AST 工具链。

以下是一个完整的实战案例，演示从 Android 应用中提取混淆 JS 代码并进行反混淆的全过程。

### 场景描述

某电商 App 在发起网络请求时，会在 WebView 中执行一段混淆的 JS 代码来生成请求签名参数 `_sign`。我们需要还原这段 JS 代码，理解签名算法。

### 第一步：定位 JS 代码

使用 Frida 拦截 WebView 的 JS 执行：

```javascript
// locate_sign.js
Java.perform(function() {
    var WebView = Java.use('android.webkit.WebView');

    WebView.evaluateJavascript.implementation = function(script, cb) {
        if (script.indexOf('_sign') !== -1 || script.indexOf('sign') !== -1) {
            console.log('========== 发现签名相关 JS ==========');
            console.log('长度: ' + script.length);
            console.log('前 200 字符: ' + script.substring(0, 200));

            // 将完整脚本保存到文件
            var File = Java.use('java.io.File');
            var FileWriter = Java.use('java.io.FileWriter');
            var fw = FileWriter.$new(
                '/data/data/com.target.app/files/sign_script.js'
            );
            fw.write(script);
            fw.close();
            console.log('脚本已保存到 /data/data/com.target.app/files/sign_script.js');
        }
        return this.evaluateJavascript(script, cb);
    };
});
```

```bash
# 运行 Frida
frida -U -f com.target.app -l locate_sign.js

# 导出保存的脚本
adb pull /data/data/com.target.app/files/sign_script.js ./
```

### 第二步：初步分析混淆代码

提取出的代码通常类似这样（已简化）：

```javascript
var _0x5a2e = ['bGVuZ3Ro', 'Y2hhckNvZGVBdA==', 'c3Vic3RyaW5n',
    'am9pbg==', 'c2xpY2U=', 'cHVzaA==', 'AEsMGQ4=', 'EAQOBBk='];

(function(_0x4a2f, _0x3b1e) {
    var _0xrotate = function(_0xnum) {
        while (--_0xnum) {
            _0x4a2f['push'](_0x4a2f['shift']());
        }
    };
    _0xrotate(++_0x3b1e);
}(_0x5a2e, 0xb3));

var _0xdec = function(_0xidx, _0xkey) {
    _0xidx = _0xidx - 0x0;
    var _0xval = _0x5a2e[_0xidx];
    // ... Base64 + XOR 解码逻辑 ...
    return _0xval;
};

function _0x2a1b(_0x3c4d, _0x5e6f) { return _0x3c4d + _0x5e6f; }
function _0x7b8c(_0x9d0e, _0x1f2a) { return _0x9d0e ^ _0x1f2a; }
function _0x4e5f(_0x6a7b, _0x8c9d) { return _0x6a7b % _0x8c9d; }

function generateSign(_0xinput) {
    var _0xorder = '2|0|4|1|3'['split']('|'), _0xi = 0x0;
    while (!![]) {
        switch (_0xorder[_0xi++]) {
            case '0':
                var _0xkey = _0xdec('0x3');
                continue;
            case '1':
                for (var _0xj = 0x0;
                     _0xj < _0xinput[_0xdec('0x0')]; _0xj++) {
                    _0xresult[_0xdec('0x5')](
                        String['fromCharCode'](
                            _0x7b8c(
                                _0xinput[_0xdec('0x1')](_0xj),
                                _0xkey[_0xdec('0x1')](
                                    _0x4e5f(_0xj, _0xkey[_0xdec('0x0')])
                                )
                            )
                        )
                    );
                }
                continue;
            case '2':
                var _0xresult = [];
                continue;
            case '3':
                return _0xresult[_0xdec('0x4')]('');
            case '4':
                var _0xlen = _0xinput[_0xdec('0x0')];
                continue;
        }
        break;
    }
}
```

### 第三步：执行反混淆

**3a. 字符串解密**

首先在 Node.js 中执行字符串数组和解码函数，得到所有明文：

```javascript
// decode_strings.js
// 粘贴字符串数组、旋转函数和解码函数到这里
// ... (省略，从混淆代码中复制)

// 批量解密
for (var i = 0; i < 20; i++) {
    try {
        console.log(`_0xdec('0x${i.toString(16)}') => "${_0xdec('0x' + i.toString(16))}"`);
    } catch(e) {}
}

// 输出:
// _0xdec('0x0') => "length"
// _0xdec('0x1') => "charCodeAt"
// _0xdec('0x2') => "substring"
// _0xdec('0x3') => "secretKey123"
// _0xdec('0x4') => "join"
// _0xdec('0x5') => "push"
```

**3b. 应用 AST 反混淆脚本**

使用前面介绍的 Babel 脚本，依次执行：

1. 字符串解密替换
2. 代理函数内联
3. 常量折叠
4. 控制流平坦化还原
5. 死代码移除

### 第四步：还原后的代码

经过完整反混淆处理后，代码变为：

```javascript
function generateSign(input) {
    var result = [];
    var key = "secretKey123";
    var len = input.length;

    for (var j = 0; j < input.length; j++) {
        result.push(
            String.fromCharCode(
                input.charCodeAt(j) ^ key.charCodeAt(j % key.length)
            )
        );
    }

    return result.join('');
}
```

**分析结论**：签名算法实际上是一个简单的**XOR 加密**，使用固定密钥 `"secretKey123"` 对输入字符串逐字符异或。

### 第五步：用 Frida 验证

编写 Frida 脚本，在运行时验证我们还原的算法是否正确：

```javascript
// verify_sign.js
Java.perform(function() {
    var WebView = Java.use('android.webkit.WebView');

    WebView.evaluateJavascript.implementation = function(script, cb) {
        if (script.indexOf('_sign') !== -1) {
            // 提取传入的参数
            var match = script.match(/generateSign\("(.+?)"\)/);
            if (match) {
                var input = match[1];
                var key = "secretKey123";

                // 用还原后的算法计算签名
                var result = [];
                for (var j = 0; j < input.length; j++) {
                    result.push(String.fromCharCode(
                        input.charCodeAt(j) ^ key.charCodeAt(j % key.length)
                    ));
                }
                var ourSign = result.join('');
                console.log('[验证] 输入: ' + input);
                console.log('[验证] 我们的签名: ' + ourSign);
            }
        }

        // 包装回调来获取 App 计算的签名
        if (cb !== null) {
            var ValueCallback = Java.use('android.webkit.ValueCallback');
            var origCb = cb;
            var newCb = Java.registerClass({
                name: 'com.hook.VerifyCb',
                implements: [ValueCallback],
                methods: {
                    onReceiveValue: function(value) {
                        console.log('[验证] App 的签名:  ' + value);
                        origCb.onReceiveValue(value);
                    }
                }
            });
            return this.evaluateJavascript(script, newCb.$new());
        }
        return this.evaluateJavascript(script, cb);
    };
});
```

如果两个签名一致，说明我们的反混淆结果是正确的。

---

## 分析与反混淆策略

反混淆 OB 代码通常是一个系统性的工程，需要多种工具和技术结合。

### 1. 字符串解密与替换

- **定位解码函数**：找到负责从字符串数组中取值并解密的函数。

- **执行解码逻辑**：
- **动态执行**：在 Node.js 或浏览器环境中，直接调用解码函数，将所有加密的字符串预先解密出来。

- **静态分析**：如果解码算法（如 RC4）比较标准，可以编写脚本静态地解密所有字符串。
- **批量替换**：编写脚本（通常基于 AST），将代码中所有对解码函数的调用 `decoder("0x1")` 替换成其返回的原始字符串 `"original_string"`。

### 2. 控制流平坦化还原

这是最困难的一步，但也是最有价值的一步。

- **AST 分析**：使用 Babel 等工具将代码解析成 AST。

- **定位主循环**：找到包含 `while(true)` 和 `switch` 的巨大循环体。

- **识别状态变量**：找到控制 `switch` 跳转的状态变量和它的初始值。

- **重排代码块**：

1. 提取 `switch` 的 `case` 数组和状态变量的初始跳转顺序。
2. 根据这个顺序，将每个 `case` 块中的代码按正确的逻辑重新排列。
3. 移除 `while` 和 `switch` 结构，生成线性的、可读的代码。

- **自动化工具**：社区中有一些尝试自动化还原控制流的工具，但由于 OB 混淆变种繁多，通用性有限。

### 3. 其他净化操作

- **常量表达式计算**：将 `0x7b` 这样的表达式直接计算成 `123`。

- **代理函数内联**：将代理函数的逻辑直接替换回原来的位置，例如将 `add(a, b)` 还原成 `a + b`。

- **死代码移除**：通过分析控制流，识别并删除无法访问到的代码块。

## 常用工具

- **Babel (核心)**：用于解析（Parse）、转换（Transform）和生成（Generate）JavaScript 代码，是编写反混淆脚本的基础。

- **AST Explorer**：在线查看 AST 结构，便于编写转换逻辑。

- **Node.js / 浏览器控制台**：用于动态执行代码片段，特别是解密函数。

- **de4js**, **js-beautify**：用于基本的代码格式化和一些简单的反混淆。

- **AST-Deobfuscator**：一些开源的、基于 AST 的反混淆工具框架，可以作为参考。
