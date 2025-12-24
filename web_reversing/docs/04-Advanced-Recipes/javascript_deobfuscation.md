# JavaScript 反混淆 (Deobfuscation)

使用 AST 工具和手动技巧，还原混淆代码的可读性，快速定位核心加密逻辑。

---

## 配方信息

| 项目 | 说明 |
| ------------ | --------------------------------------------- |
| **难度** | ⭐⭐⭐⭐ (高级) |
| **预计时间** | 2-8 小时 (根据混淆复杂度) |
| **所需工具** | Chrome DevTools, Babel, AST Explorer, Node.js |
| **适用场景** | 混淆代码分析、加密算法提取、恶意代码分析 |

---

## 📚 前置知识

在开始本配方之前，建议先掌握以下内容：

| 知识领域 | 重要程度 | 参考资料 |
|----------|---------|---------|
| JavaScript 基础 | 必需 | [JavaScript 基础](../01-Foundations/javascript_basics.md) |
| JavaScript 执行机制 | 必需 | [JavaScript 执行机制](../01-Foundations/javascript_execution_mechanism.md) |
| AST 工具使用 | 必需 | [AST 工具](../02-Tooling/ast_tools.md) |
| Chrome DevTools | 必需 | [浏览器开发者工具](../02-Tooling/browser_devtools.md) |
| Node.js 调试 | 推荐 | [Node.js 调试](../02-Tooling/nodejs_debugging.md) |

> 💡 **提示**: JavaScript 反混淆是高级逆向的**核心技能**。建议深入理解 AST（抽象语法树）原理，这是自动化反混淆的基础。如果完全没有 AST 基础，建议先阅读 AST 工具指南。

---

## 学习目标

完成本配方后，你将能够：

- ✅ 识别常见的混淆技术类型
- ✅ 使用 AST 工具批量还原混淆代码
- ✅ 手动分析和还原关键逻辑
- ✅ 处理字符串数组、控制流平坦化等高级混淆
- ✅ 使用调试技巧绕过混淆代码

---

## 核心概念

混淆 (Obfuscation) 是 Web 逆向最大的拦路虎。代码混淆技术通过变换代码结构和语义，在不改变程序功能的前提下大幅增加逆向分析的难度。常见的混淆手段包括变量名压缩、字符串数组加密、大整数运算、控制流平坦化、死代码注入等。

**反混淆的本质**：通过自动化或手动手段还原代码的可读性，理解核心加密逻辑。

**重要提醒**：反混淆不是目的，**理解逻辑**才是。有时我们不需要还原全部代码，只要把关键的加密函数还原出来，或者直接找到调用入口即可。

**反混淆策略**:

```
1. 识别混淆类型 → 2. 选择工具/方法 → 3. 局部还原 → 4. 理解逻辑 → 5. 提取关键代码
```

---

## 1. 混淆技术分类

### 1.1 变量名混淆 (Identifier Mangling)

**特征**:

- 所有变量、函数名变成无意义的短字符: `a`, `b`, `_0x1234`
- 类似压缩器（Uglify、Terser）的输出

**示例**:

```javascript
// 原始代码
function calculatePrice(basePrice, discount) {
return basePrice * (1 - discount);
}

// 混淆后
function a(b, c) {
return b * (1 - c);
}
```

**对抗方法**:

- 使用 Chrome DevTools 的 "Rename Symbol" 功能手动重命名
- 使用 JSNice (http://jsnice.org/) 自动推测变量名
- 通过上下文理解变量含义

---

### 1.2 字符串数组混淆 (String Array Obfuscation)

**特征**:

- 代码顶部有一个巨大的字符串数组: `var _0x1234 = ['str1', 'str2', ...]`
- 字符串通过索引访问: `_0x1234[0]` 而不是直接写 `'str1'`
- 通常配合数组旋转（Shuffle）和解密函数

**示例**:

```javascript
// 混淆后的代码
var _0xabcd = ["aGVsbG8=", "d29ybGQ=", "Y29uc29sZQ==", "bG9n"];
(function (_0x4a5b3e, _0x2f8c1d) {
var _0x3e7a90 = function (_0x1c9f47) {
while (--_0x1c9f47) {
_0x4a5b3e["push"](_0x4a5b3e["shift"]());
}
};
_0x3e7a90(++_0x2f8c1d);
})(_0xabcd, 0x123);

var _0x5678 = function (_0x4a5b3e, _0x2f8c1d) {
_0x4a5b3e = _0x4a5b3e - 0x0;
var _0x3e7a90 = _0xabcd[_0x4a5b3e];
if (_0x5678["initialized"] === undefined) {
// Base64 解码逻辑
_0x5678["decoder"] = function (_0x1c9f47) {
// ...解码代码
};
_0x5678["initialized"] = ![];
}
var _0x1c9f47 = _0x5678["decoder"](_0x3e7a90);
return _0x1c9f47;
};

console[_0x5678("0x0")](_0x5678("0x1")); // 实际是 console.log('hello')
```

**对抗方法**:

1. 在 Console 中执行数组和旋转函数，使其初始化
2. 在 Console 中挂载解密函数 `_0x5678`
3. 使用正则替换：`_0x5678\('0x(\d+)'\)` → 执行并替换为真实字符串
4. 使用 AST 工具自动还原（详见后文）

---

### 1.3 控制流平坦化 (Control Flow Flattening)

**特征**:

- 整个函数变成一个 `while(true)` 循环
- 使用 `switch-case` 状态机控制执行流程
- 代码块被打乱，通过状态变量跳转

**示例**:

```javascript
// 原始代码
function add(a, b) {
var result = a + b;
console.log(result);
return result;
}

// 平坦化后
function add(a, b) {
var _0x1 = "3|1|0|4|2".split("|"),
_0x2 = 0;
while (!![]) {
switch (_0x1[_0x2++]) {
case "0":
console.log(result);
continue;
case "1":
result = a + b;
continue;
case "2":
return result;
case "3":
var result;
continue;
case "4":
// 可能插入的垃圾代码
continue;
}
break;
}
}
```

**对抗方法**:

- **手动分析**：记录状态转移路径，手动重组代码块
- **AST 还原**：解析状态机的跳转逻辑，自动重建代码顺序（需要高级 AST 技巧）
- **动态执行**：直接调用函数，通过输入输出推断逻辑

---

### 1.4 僵尸代码注入 (Dead Code Injection)

**特征**:

- 插入大量永远不会执行的代码块
- 使用 `if (false)` 或永远为假的复杂条件

**示例**:

```javascript
function encrypt(data) {
if (Math.random() < 0) {
// 这段代码永远不会执行
return decrypt(data);
}
var result = md5(data);
if (!![] && ![]) {
// 又是死代码
result = sha256(data);
}
return result;
}
```

**对抗方法**:

- 使用 Babel 的常量折叠 (Constant Folding) 优化
- 手动识别并删除明显的死代码分支

---

### 1.5 数字/字符串编码 (Encoding)

**特征**:

- 数字被编码为十六进制、八进制、或计算表达式
- 字符串被 Base64、Unicode 转义、或自定义编码

**示例**:

```javascript
// 原始
var port = 443;
var msg = "Hello";

// 混淆后
var port = 0x1bb; // 十六进制
var port = 0o673; // 八进制
var port = 500 - 57; // 计算表达式
var msg = atob("SGVsbG8="); // Base64
var msg = "\u0048\u0065\u006c\u006c\u006f"; // Unicode
```

**对抗方法**:

- AST 常量折叠自动计算
- 在 Console 手动执行编码字符串

---

### 1.6 特殊编码混淆 (JJEncode / AAEncode / JSFuck)

**特征**:

- **JJEncode**: 全是符号 `$ _ + " ☐ ( ) . !`
- **AAEncode**: 使用 颜文字 `(゚Д゚)` 等
- **JSFuck**: 仅使用 `[]()!+` 六个字符

**示例** (JSFuck):

```javascript
// alert(1) 的 JSFuck 版本
[][(![]+[])[+[]]+([![]]+[][[]])[+!+[]+[+[]]]+(![]+[])[!+[]+!+[]]+...
```

**对抗方法**:

- 直接在 Console 执行（去掉最后的 `()` 避免立即执行）
- 使用在线工具: https://enkhee-osiris.github.io/Decoder-JSFuck/
- 这些编码通常只是外层包装，解码后还需要进一步反混淆

---

## 2. 混淆器识别

### 2.1 javascript-obfuscator (最常见)

**官网**: https://obfuscator.io/

**特征**:

- 顶部有 `_0x????` 格式的字符串数组
- 自执行函数进行数组旋转
- 函数名、变量名全是 `_0x????` 格式
- 可能包含控制流平坦化

**配置等级**:
| 等级 | 特征 | 难度 |
|------|------|------|
| Low | 仅变量名混淆 | ⭐ |
| Medium | + 字符串数组 | ⭐⭐ |
| High | + 控制流平坦化 | ⭐⭐⭐⭐ |
| Extreme | + 死代码 + 自我防御 | ⭐⭐⭐⭐⭐ |

**对抗工具**:

- https://deobfuscate.io/ (针对 obfuscator.io)
- AST 自定义脚本（见 [反混淆脚本](../07-Scripts/deobfuscation_scripts.md)）

---

### 2.2 Webpack/Rollup 打包

**特征**:

- 立即执行函数 `(function(modules) { ... })([func1, func2, ...])`
- 模块通过索引访问: `__webpack_require__(0)`
- 有明显的模块加载器代码

**对抗工具**:

- **webcrack**: https://github.com/j4k0xb/webcrack
```bash
npm install -g webcrack
webcrack bundle.js -o output/
```
- **webpack-bundle-analyzer**: 分析打包结构

---

### 2.3 商业级混淆 (Jscrambler, 形状安全等)

**特征**:

- 多层嵌套混淆
- 虚拟机保护 (JSVMP)
- 反调试陷阱
- 域名绑定

**难度**: ⭐⭐⭐⭐⭐

**对抗方法**:

- 需要深入理解虚拟机原理（见 [JavaScript 虚拟机保护](./javascript_vm_protection.md)）
- 通常需要 RPC 调用或完整扣代码
- 商业混淆通常不建议完全还原，直接 Hook 或 RPC 更高效

---

## 3. 自动化反混淆工具

### 3.1 在线工具对比

| 工具 | 链接 | 支持混淆类型 | 优点 | 缺点 |
| ------------------ | ----------------------------------- | -------------------------- | ---------------------- | ---------------- |
| **deobfuscate.io** | https://deobfuscate.io/ | obfuscator.io | 专门针对 obfuscator.io | 仅支持特定混淆器 |
| **JSNice** | http://jsnice.org/ | 变量名恢复 | AI 推测变量名 | 不处理字符串数组 |
| **Prettier** | https://prettier.io/playground/ | 代码格式化 | 美化代码结构 | 不解密字符串 |
| **de4js** | https://lelinhtinh.github.io/de4js/ | JJEncode, AAEncode, JSFuck | 支持特殊编码 | 不支持通用混淆 |
| **Synchrony** | https://deobfuscate.relative.im/ | 通用混淆 | 自动识别混淆类型 | 准确率一般 |

---

### 3.2 本地工具

#### Babel + AST (推荐)

**安装**:

```bash
npm install @babel/core @babel/parser @babel/traverse @babel/generator @babel/types
```

**基础反混淆脚本**:

```javascript
const parser = require("@babel/parser");
const traverse = require("@babel/traverse").default;
const generator = require("@babel/generator").default;
const t = require("@babel/types");
const fs = require("fs");

// 读取混淆代码
const code = fs.readFileSync("obfuscated.js", "utf-8");
const ast = parser.parse(code);

// 1. 常量折叠
traverse(ast, {
BinaryExpression(path) {
const result = path.evaluate();
if (result.confident) {
path.replaceWith(t.valueToNode(result.value));
}
},
});

// 2. 字符串数组还原（需要先执行数组初始化代码）
// 具体实现见 07-Scripts/deobfuscation_scripts.md

// 3. 删除死代码
traverse(ast, {
IfStatement(path) {
const test = path.get("test").evaluate();
if (test.confident) {
if (test.value) {
path.replaceWithMultiple(path.node.consequent.body);
} else if (path.node.alternate) {
path.replaceWith(path.node.alternate);
} else {
path.remove();
}
}
},
});

// 输出结果
const output = generator(ast, {}, code);
fs.writeFileSync("deobfuscated.js", output.code);
```

详细的 AST 反混淆脚本见：[反混淆脚本](../07-Scripts/deobfuscation_scripts.md)

---

#### webcrack (Webpack 专用)

```bash
npm install -g webcrack
webcrack bundle.js -o output/
```

**功能**:

- 自动识别 Webpack 打包
- 提取模块代码
- 还原目录结构
- 重命名变量

---

## 4. 手动反混淆技巧

当自动化工具失效时，我们需要"手术刀"式精准操作。

### 4.1 Chrome DevTools 技巧

#### 重命名符号 (Rename Symbol)

1. 在 Sources 面板打开混淆代码
2. 右键变量名 → "Rename Symbol"
3. 输入有意义的名称（如 `token`, `timestamp`）
4. DevTools 会自动重命名该作用域内的所有引用

#### 格式化代码 (Pretty Print)

- 点击左下角 `{}` 按钮自动格式化
- 将单行代码展开为多行，便于阅读

#### 条件断点 (Conditional Breakpoint)

- 右键行号 → "Add conditional breakpoint"
- 输入条件：`userId === 12345`
- 只在特定条件下断点，避免频繁中断

---

### 4.2 Console REPL 技巧

#### 执行并替换

遇到复杂表达式，直接在 Console 计算结果：

```javascript
// 混淆代码
var a = 0x1bb * 0x2 - 0x64;

// Console 中执行
0x1bb * 0x2 - 0x64; // 输出: 790

// 手动替换为
var a = 790;
```

#### 导出大数组

```javascript
// 混淆代码中有巨大的数组
var _0xabcd = [
/* 几千个元素 */
];

// Console 中
copy(_0xabcd); // 自动复制到剪贴板
```

#### 提取解密函数

```javascript
// 混淆代码中的解密函数
var _0x5678 = function (index) {
return _0xabcd[index];
};

// 在 Console 中挂载为全局函数
window.decrypt = _0x5678;

// 然后可以批量解密
for (let i = 0; i < 10; i++) {
console.log(i, decrypt(i));
}
```

---

### 4.3 提取和重写

#### 三元表达式展开

```javascript
// 混淆代码
var result = a ? b : c ? d : e ? f : g;

// 改写为 if-else
var result;
if (a) {
result = b;
} else if (c) {
result = d;
} else if (e) {
result = f;
} else {
result = g;
}
```

#### 逗号表达式拆分

```javascript
// 混淆代码
var a = ((b = 1), (c = 2), (d = b + c), d * 2);

// 拆分为
var b = 1;
var c = 2;
var d = b + c;
var a = d * 2;
```

---

## 5. 反混淆实战案例

### 案例 1: obfuscator.io 字符串数组还原

**混淆代码**:

```javascript
var _0x4a5b = ["aGVsbG8=", "d29ybGQ="];
(function (_0x3e7a90, _0x1c9f47) {
var _0x5d8c12 = function (_0x2f8c1d) {
while (--_0x2f8c1d) {
_0x3e7a90["push"](_0x3e7a90["shift"]());
}
};
_0x5d8c12(++_0x1c9f47);
})(_0x4a5b, 0x123);
var _0x5678 = function (_0x3e7a90, _0x1c9f47) {
// ...解密逻辑
};

console[_0x5678("0x0")](_0x5678("0x1"));
```

**还原步骤**:

1. **执行初始化代码**（在 Console）:

```javascript
var _0x4a5b = ["aGVsbG8=", "d29ybGQ="];
(function (_0x3e7a90, _0x1c9f47) {
var _0x5d8c12 = function (_0x2f8c1d) {
while (--_0x2f8c1d) {
_0x3e7a90["push"](_0x3e7a90["shift"]());
}
};
_0x5d8c12(++_0x1c9f47);
})(_0x4a5b, 0x123);
```

2. **执行解密函数**:

```javascript
var _0x5678 = function (_0x3e7a90, _0x1c9f47) {
// 复制完整的解密函数代码
};

// 测试
_0x5678("0x0"); // 输出: "log"
_0x5678("0x1"); // 输出: "hello"
```

3. **批量替换**:
使用正则表达式或 AST 工具将所有 `_0x5678('0x...')` 替换为解密后的字符串

---

### 案例 2: 控制流平坦化还原

**混淆代码**:

```javascript
function checkPassword(pwd) {
var _0x1 = "2|0|3|1|4".split("|"),
_0x2 = 0;
while (true) {
switch (_0x1[_0x2++]) {
case "0":
if (pwd.length < 8) return false;
continue;
case "1":
if (!/[A-Z]/.test(pwd)) return false;
continue;
case "2":
var result = true;
continue;
case "3":
if (!/[0-9]/.test(pwd)) return false;
continue;
case "4":
return result;
}
break;
}
}
```

**还原步骤**:

1. **识别状态序列**: `'2|0|3|1|4'`
2. **按顺序重组代码**:

```javascript
function checkPassword(pwd) {
    var result = true; // case '2'
    if (pwd.length < 8) return false; // case '0'
    if (!/[0-9]/.test(pwd)) return false; // case '3'
    if (!/[A-Z]/.test(pwd)) return false; // case '1'
    return result; // case '4'
}
```

---

## 6. 反混淆最佳实践

### 6.1 渐进式反混淆

不要试图一次性还原所有代码，采用分层策略：

1. **第一层：格式化** - 使用 Prettier 美化代码
2. **第二层：字符串还原** - 还原字符串数组和编码
3. **第三层：常量折叠** - 计算所有常量表达式
4. **第四层：死代码删除** - 移除无效分支
5. **第五层：变量重命名** - 赋予变量有意义的名称
6. **第六层：控制流还原** - 处理控制流平坦化（可选）

### 6.2 保留中间结果

每一步都保存文件：

```
obfuscated.js // 原始
01_formatted.js // 格式化
02_strings_restored.js // 字符串还原
03_constants_folded.js // 常量折叠
04_dead_code_removed.js // 死代码删除
05_final.js // 最终版本
```

### 6.3 验证正确性

每次变换后都要验证：

```javascript
// 在 Console 中对比输出
eval(原始代码).someFunction(testInput);
eval(还原代码).someFunction(testInput);
// 两者应该返回相同结果
```

### 6.4 关注核心逻辑

不要浪费时间还原整个文件：

- **目标明确**: 只还原加密/签名相关函数
- **黑盒调用**: 对于复杂的辅助函数，直接调用而不是理解
- **RPC 策略**: 实在无法还原，考虑通过 RPC 调用浏览器执行

---

## 7. 常见问题与解决方案

### Q1: AST 工具报错 "Cannot read property 'type'"

**原因**: 某个节点被错误地删除或替换

**解决**: 在替换前检查节点是否存在

```javascript
if (path.node && t.isIdentifier(path.node)) {
// 安全操作
}
```

### Q2: 字符串数组还原后仍然是乱码

**原因**:

- 字符串经过多重编码（Base64 → XOR → ROT13）
- 解密函数依赖运行时动态生成的密钥

**解决**:

- 在浏览器环境中执行初始化代码
- 使用 Node.js 的 VM 模块模拟浏览器环境

### Q3: 控制流平坦化无法自动还原

**原因**: 状态跳转使用动态计算（非简单字符串）

**解决**:

- 手动跟踪状态转移
- 使用动态插桩记录实际执行路径
- 接受部分还原，关注关键代码块

### Q4: 反混淆后代码无法运行

**原因**:

- 丢失了必要的上下文（闭包变量）
- 自我防御代码检测到修改

**解决**:

- 保留完整的作用域链
- 禁用反调试代码（见 [调试技巧](../03-Basic-Recipes/debugging_techniques.md)）

---

## 8. 工具与资源

### 推荐工具

| 工具 | 用途 | 链接 |
| ---------------- | --------------- | ---------------------------------- |
| **AST Explorer** | 可视化 AST 结构 | https://astexplorer.net/ |
| **Babel REPL** | 测试 Babel 转换 | https://babeljs.io/repl |
| **webcrack** | Webpack 反混淆 | https://github.com/j4k0xb/webcrack |
| **synchrony** | 自动反混淆 | https://deobfuscate.relative.im/ |

### 学习资源

- [Babel Plugin Handbook](https://github.com/jamiebuilds/babel-handbook/blob/master/translations/en/plugin-handbook.md)
- [AST 解析工具](../02-Tooling/ast_tools.md)
- [反混淆脚本合集](../07-Scripts/deobfuscation_scripts.md)

---

## 9. 总结

JavaScript 反混淆是一门艺术，需要结合：

- **工具**: 自动化处理重复性工作
- **技巧**: 手动处理特殊情况
- **经验**: 快速识别混淆类型和核心逻辑
- **耐心**: 复杂混淆可能需要数小时乃至数天

**核心原则**:

1. 不要追求完美还原，理解核心逻辑即可
2. 善用动态分析，结合静态反混淆
3. 建立自己的工具库和脚本集
4. 保持学习，混淆技术在不断演进

---

## 相关章节

- [AST 解析工具](../02-Tooling/ast_tools.md)
- [反混淆脚本](../07-Scripts/deobfuscation_scripts.md)
- [调试技巧与断点设置](../03-Basic-Recipes/debugging_techniques.md)
- [JavaScript 虚拟机保护](./javascript_vm_protection.md)
- [动态参数分析](../03-Basic-Recipes/dynamic_parameter_analysis.md)
