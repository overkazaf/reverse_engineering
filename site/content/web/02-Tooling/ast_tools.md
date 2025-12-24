---
title: "AST (抽象语法树) 工具"
date: 2025-12-25
weight: 10
---

# AST (抽象语法树) 工具

## 概述

在对抗混淆（Obfuscation）时，字符串替换和正则匹配往往力不从心。AST 为我们提供了操作代码结构的上帝视角。通过解析 AST，我们可以安全地删除死代码、还原控制流平坦化、计算常量表达式。

**Babel** 是目前 JS 逆向中最常用的 AST 库。它提供了完整的 JavaScript 解析、转换、生成能力。

---

## 1. 核心工作流

使用 `@babel` 系列包进行 AST 操作的标准流程：

```
源代码 (String)
↓ @babel/parser
AST (抽象语法树)
↓ @babel/traverse (遍历和修改)
修改后的 AST
↓ @babel/generator
新代码 (String)
```

### 1.1 四个核心包

| 包名 | 作用 | 主要 API |
| -------------------- | ------------- | ---------------------------------------- |
| **@babel/parser** | 代码 → AST | `parse(code)` |
| **@babel/traverse** | 遍历/修改 AST | `traverse(ast, visitor)` |
| **@babel/generator** | AST → 代码 | `generate(ast)` |
| **@babel/types** | 创建/判断节点 | `t.isIdentifier()`, `t.numericLiteral()` |

### 1.2 示例代码框架

```javascript
const parser = require("@babel/parser");
const traverse = require("@babel/traverse").default;
const generator = require("@babel/generator").default;
const t = require("@babel/types");
const fs = require("fs");

// 1. 读取并解析
const code = fs.readFileSync("obfuscated.js", "utf-8");
const ast = parser.parse(code);

// 2. 遍历并修改
traverse(ast, {
// 你的还原插件写在这里
StringLiteral(path) {
// 例如：将十六进制字符串 "\x61" 还原为 "a"
if (path.node.extra && path.node.extra.raw.startsWith('"\\x')) {
delete path.node.extra;
}
},
});

// 3. 生成新代码
const output = generator(ast, {
jsescOption: { minimal: true }, // 使用最少的转义
});

fs.writeFileSync("deobfuscated.js", output.code);
console.log("反混淆完成！");
```

---

## 2. 常见反混淆场景

### 2.1 常量折叠 (Constant Folding)

**问题**: 混淆器把 `3` 变成 `1 + 2`，或把字符串拆分为 `'H' + 'e' + 'l' + 'l' + 'o'`

**解决方案**: 计算并替换为结果

```javascript
traverse(ast, {
BinaryExpression(path) {
// 尝试求值
const result = path.evaluate();

// 如果可以计算出确定的值
if (result.confident) {
// 替换为字面量节点
path.replaceWith(t.valueToNode(result.value));
}
},
});
```

**示例**:

```javascript
// 混淆前
const x = 1 + 2 + 3;
const str = "H" + "e" + "l" + "l" + "o";

// 反混淆后
const x = 6;
const str = "Hello";
```

### 2.2 死代码消除 (Dead Code Elimination)

**问题**: 充斥着永远不会执行的代码

**解决方案 1**: 删除恒为 false 的条件分支

```javascript
traverse(ast, {
IfStatement(path) {
// 获取条件表达式的值
const test = path.get("test").evaluate();

if (test.confident) {
if (test.value) {
// 条件恒为 true，替换为 consequent（if 块）
path.replaceWithMultiple(path.node.consequent.body);
} else {
// 条件恒为 false
if (path.node.alternate) {
// 有 else 块，替换为 alternate
path.replaceWithMultiple(path.node.alternate.body);
} else {
// 没有 else，直接删除整个 if 语句
path.remove();
}
}
}
},
});
```

**示例**:

```javascript
// 混淆前
if (false) {
console.log("I am dead code");
}
if (true) {
console.log("I will always run");
}

// 反混淆后
console.log("I will always run");
```

**解决方案 2**: 删除未引用的变量/函数

```javascript
traverse(ast, {
VariableDeclarator(path) {
const binding = path.scope.getBinding(path.node.id.name);

// 如果变量从未被引用
if (binding && !binding.referenced) {
path.remove();
}
},
});
```

### 2.3 字符串数组还原

**问题**: 混淆器把所有字符串提取到一个大数组中

**混淆代码**:

```javascript
const _0x1234 = ["name", "age", "hello"];

function greet() {
console.log(_0x1234[2]); // 'hello'
}
```

**解决方案**:

```javascript
let stringArray = null;

traverse(ast, {
// 第一步：提取字符串数组
VariableDeclarator(path) {
if (
path.node.id.name === "_0x1234" &&
t.isArrayExpression(path.node.init)
) {
stringArray = path.node.init.elements.map((e) => e.value);
console.log("找到字符串数组:", stringArray);
}
},
});

traverse(ast, {
// 第二步：替换所有引用
MemberExpression(path) {
// _0x1234[2] 形式
if (
t.isIdentifier(path.node.object, { name: "_0x1234" }) &&
t.isNumericLiteral(path.node.property)
) {
const index = path.node.property.value;
const str = stringArray[index];
path.replaceWith(t.stringLiteral(str));
}
},
});
```

**反混淆后**:

```javascript
function greet() {
console.log("hello");
}
```

### 2.4 控制流平坦化还原

**问题**: 混淆器把代码变成一个大的 switch-case

**混淆代码**:

```javascript
let _state = 0;
while (true) {
switch (_state) {
case 0:
console.log("step 1");
_state = 1;
break;
case 1:
console.log("step 2");
_state = 2;
break;
case 2:
console.log("step 3");
return;
}
}
```

**解决方案**: (复杂，需要符号执行)

```javascript
// 简化版：提取顺序执行的 case
traverse(ast, {
WhileStatement(path) {
const body = path.node.body;

// 检查是否是 switch 语句
if (t.isSwitchStatement(body.body[0])) {
const switchNode = body.body[0];
const cases = switchNode.cases;

// 按 case 值排序
const sortedCases = cases.sort((a, b) => {
return a.test.value - b.test.value;
});

// 提取所有 case 的 body（去除 break）
const statements = sortedCases.flatMap((c) => {
return c.consequent.filter((s) => !t.isBreakStatement(s));
});

// 替换整个 while 语句
path.replaceWithMultiple(statements);
}
},
});
```

### 2.5 标识符重命名

**问题**: 混淆器把所有变量名改成 `_0x1a2b`, `a`, `b`, `c`

**解决方案**: 重命名为有意义的名字

```javascript
let counter = 0;

traverse(ast, {
Scope(path) {
// 遍历作用域中的所有绑定
Object.keys(path.scope.bindings).forEach((name) => {
// 如果是混淆的名字（短或十六进制）
if (name.match(/^[a-z]$|^_0x[0-9a-f]+$/i)) {
const newName = `var_${counter++}`;
path.scope.rename(name, newName);
}
});
},
});
```

**示例**:

```javascript
// 混淆前
function a(b, c) {
return b + c;
}

// 反混淆后
function var_0(var_1, var_2) {
return var_1 + var_2;
}
```

---

## 3. 进阶技巧

### 3.1 自定义 Visitor

**Visitor 模式**: Babel 使用访问者模式遍历 AST

```javascript
const visitor = {
// 进入节点时调用
enter(path) {
console.log("进入:", path.type);
},

// 离开节点时调用
exit(path) {
console.log("离开:", path.type);
},

// 针对特定节点类型
FunctionDeclaration(path) {
console.log("找到函数:", path.node.id.name);
},

// 简写形式（只有 enter）
CallExpression(path) {
console.log("函数调用:", path.node.callee.name);
},
};

traverse(ast, visitor);
```

### 3.2 Path 对象常用方法

| 方法 | 作用 | 示例 |
| ------------------------- | ----------------- | ----------------------------------------------- |
| `path.node` | 获取当前 AST 节点 | `path.node.id.name` |
| `path.parent` | 获取父节点 | `path.parent` |
| `path.scope` | 获取作用域信息 | `path.scope.bindings` |
| `path.get('key')` | 获取子路径 | `path.get('params.0')` |
| `path.replaceWith(node)` | 替换节点 | `path.replaceWith(t.numericLiteral(123))` |
| `path.remove()` | 删除节点 | `path.remove()` |
| `path.insertBefore(node)` | 在前面插入节点 | `path.insertBefore(t.expressionStatement(...))` |
| `path.insertAfter(node)` | 在后面插入节点 | `path.insertAfter(t.expressionStatement(...))` |
| `path.evaluate()` | 尝试求值 | `const result = path.evaluate()` |

### 3.3 Scope 作用域分析

**查找变量绑定**:

```javascript
traverse(ast, {
FunctionDeclaration(path) {
const funcName = path.node.id.name;

// 获取函数作用域
const scope = path.scope;

// 查找变量绑定
const binding = scope.getBinding("someVariable");

if (binding) {
console.log("变量定义于:", binding.path.node.loc);
console.log("引用次数:", binding.references);
console.log("是否被引用:", binding.referenced);
}
},
});
```

**重命名变量（包括所有引用）**:

```javascript
traverse(ast, {
Identifier(path) {
if (path.node.name === "oldName") {
path.scope.rename("oldName", "newName");
}
},
});
```

### 3.4 类型检查与创建

**检查节点类型**:

```javascript
if (t.isIdentifier(node)) {
console.log("这是一个标识符");
}

if (t.isIdentifier(node, { name: "foo" })) {
console.log("这是名为 foo 的标识符");
}

if (t.isFunctionDeclaration(node)) {
console.log("这是一个函数声明");
}
```

**创建新节点**:

```javascript
// 创建数字字面量
const num = t.numericLiteral(123);

// 创建字符串字面量
const str = t.stringLiteral("hello");

// 创建标识符
const id = t.identifier("myVar");

// 创建函数调用
const call = t.callExpression(t.identifier("console.log"), [
t.stringLiteral("hello"),
]);

// 创建变量声明
const varDecl = t.variableDeclaration("const", [
t.variableDeclarator(t.identifier("x"), t.numericLiteral(10)),
]);
```

---

## 4. 完整反混淆脚本示例

### 4.1 针对 javascript-obfuscator

```javascript
const parser = require("@babel/parser");
const traverse = require("@babel/traverse").default;
const generator = require("@babel/generator").default;
const t = require("@babel/types");
const fs = require("fs");

// 读取混淆代码
const code = fs.readFileSync("obfuscated.js", "utf-8");
const ast = parser.parse(code);

// ========== 步骤 1: 常量折叠 ==========
traverse(ast, {
BinaryExpression(path) {
const result = path.evaluate();
if (result.confident) {
path.replaceWith(t.valueToNode(result.value));
}
},
});

// ========== 步骤 2: 字符串数组还原 ==========
let stringArray = null;

// 提取字符串数组
traverse(ast, {
VariableDeclarator(path) {
if (
t.isArrayExpression(path.node.init) &&
path.node.init.elements.every((e) => t.isStringLiteral(e))
) {
stringArray = path.node.init.elements.map((e) => e.value);
console.log(`[字符串数组] 找到 ${stringArray.length} 个字符串`);

// 记录数组名
const arrayName = path.node.id.name;

// 替换所有引用
path.scope.traverse(path.scope.block, {
MemberExpression(innerPath) {
if (
t.isIdentifier(innerPath.node.object, { name: arrayName }) &&
t.isNumericLiteral(innerPath.node.property)
) {
const index = innerPath.node.property.value;
if (index < stringArray.length) {
innerPath.replaceWith(t.stringLiteral(stringArray[index]));
}
}
},
});

// 删除数组定义
path.remove();
}
},
});

// ========== 步骤 3: 死代码消除 ==========
traverse(ast, {
IfStatement(path) {
const test = path.get("test").evaluate();
if (test.confident) {
if (test.value) {
path.replaceWithMultiple(path.node.consequent.body);
} else {
if (path.node.alternate) {
path.replaceWithMultiple(path.node.alternate.body);
} else {
path.remove();
}
}
}
},
});

// ========== 步骤 4: 删除未使用的变量 ==========
traverse(ast, {
VariableDeclarator(path) {
const binding = path.scope.getBinding(path.node.id.name);
if (binding && !binding.referenced) {
console.log(`[删除] 未使用的变量: ${path.node.id.name}`);
path.remove();
}
},
});

// ========== 步骤 5: 函数调用内联 (简单情况) ==========
traverse(ast, {
CallExpression(path) {
// 如果调用的是 IIFE（立即执行函数）
if (
t.isFunctionExpression(path.node.callee) &&
path.node.callee.params.length === 0
) {
// 替换为函数体
const body = path.node.callee.body.body;
if (body.length === 1 && t.isReturnStatement(body[0])) {
path.replaceWith(body[0].argument);
}
}
},
});

// 生成代码
const output = generator(ast, {
jsescOption: { minimal: true },
compact: false, // 不压缩
comments: false, // 去除注释
});

fs.writeFileSync("deobfuscated.js", output.code);
console.log("\n反混淆完成！输出文件: deobfuscated.js");
console.log(`源代码: ${code.length} 字符`);
console.log(`反混淆后: ${output.code.length} 字符`);
```

### 4.2 性能优化

**问题**: AST 遍历很慢，尤其是大文件

**解决方案 1: 单次遍历**

```javascript
// ❌ 慢（多次遍历）
traverse(ast, { BinaryExpression() {} });
traverse(ast, { IfStatement() {} });
traverse(ast, { CallExpression() {} });

// ✅ 快（单次遍历）
traverse(ast, {
BinaryExpression() {},
IfStatement() {},
CallExpression() {},
});
```

**解决方案 2: 提前退出**

```javascript
traverse(ast, {
FunctionDeclaration(path) {
if (path.node.id.name === "targetFunction") {
// 找到目标函数，停止遍历
path.stop();
}
},
});
```

**解决方案 3: 限制遍历深度**

```javascript
traverse(ast, {
enter(path) {
// 只遍历第一层
if (path.node.loc.start.line > 100) {
path.skip(); // 跳过子节点
}
},
});
```

---

## 5. AST Explorer (在线工具)

**网址**: [https://astexplorer.net/](https://astexplorer.net/)

**功能**:

- 实时查看代码的 AST 结构
- 支持多种语言（JavaScript, TypeScript, JSX, etc.）
- 支持多种解析器（Babel, Acorn, Esprima, etc.）
- 实时编写和测试转换插件

**使用步骤**:

1. 访问 astexplorer.net
2. 左侧输入 JavaScript 代码
3. 右侧自动显示 AST 结构
4. 点击节点查看详细信息
5. 在 Transform 标签页编写 Babel 插件测试

**示例**:

输入:

```javascript
const x = 1 + 2;
```

AST 输出（简化）:

```json
{
"type": "VariableDeclaration",
"declarations": [
{
"type": "VariableDeclarator",
"id": { "type": "Identifier", "name": "x" },
"init": {
"type": "BinaryExpression",
"operator": "+",
"left": { "type": "NumericLiteral", "value": 1 },
"right": { "type": "NumericLiteral", "value": 2 }
}
}
]
}
```

---

## 6. 实战案例

### 案例 1：某电商网站的签名算法

**目标**: 还原混淆的签名函数

**混淆代码** (简化版):

```javascript
const _0x1234 = ["sign", "md5", "timestamp"];

function _0xabcd(a, b) {
return _0x1234[0] + a + _0x1234[2] + b;
}
```

**反混淆脚本**:

```javascript
// (使用前面的完整脚本)
```

**反混淆后**:

```javascript
function _0xabcd(a, b) {
return "sign" + a + "timestamp" + b;
}
```

**手动简化**:

```javascript
function generateSignString(user_id, timestamp) {
return "sign" + user_id + "timestamp" + timestamp;
}
```

### 案例 2：控制流平坦化还原

**混淆代码**:

```javascript
let _state = "init";
while (_state !== "end") {
switch (_state) {
case "init":
console.log("Start");
_state = "middle";
break;
case "middle":
console.log("Process");
_state = "end";
break;
}
}
```

**反混淆脚本**: (使用前面的控制流平坦化还原代码)

**反混淆后**:

```javascript
console.log("Start");
console.log("Process");
```

---

## 7. 常见 AST 节点类型

| 类型 | 说明 | 示例代码 |
| ----------------------- | ------------ | -------------------- |
| **Program** | 整个程序 | `整个 JS 文件` |
| **FunctionDeclaration** | 函数声明 | `function foo() {}` |
| **VariableDeclaration** | 变量声明 | `const x = 1;` |
| **ExpressionStatement** | 表达式语句 | `console.log();` |
| **CallExpression** | 函数调用 | `foo()` |
| **BinaryExpression** | 二元表达式 | `1 + 2` |
| **Identifier** | 标识符 | `foo`, `x` |
| **NumericLiteral** | 数字字面量 | `123` |
| **StringLiteral** | 字符串字面量 | `'hello'` |
| **ArrayExpression** | 数组表达式 | `[1, 2, 3]` |
| **ObjectExpression** | 对象表达式 | `{a: 1, b: 2}` |
| **MemberExpression** | 成员访问 | `obj.prop`, `arr[0]` |
| **IfStatement** | if 语句 | `if (x) {...}` |
| **WhileStatement** | while 循环 | `while (true) {...}` |
| **ForStatement** | for 循环 | `for (;;) {...}` |
| **ReturnStatement** | return 语句 | `return x;` |

---

## 8. 工具与资源

| 资源 | 类型 | 链接 |
| ------------------ | -------------- | --------------------------------------------- |
| **AST Explorer** | 在线工具 | https://astexplorer.net/ |
| **Babel 文档** | 官方文档 | https://babeljs.io/docs/ |
| **Babel Handbook** | 深度教程 | https://github.com/jamiebuilds/babel-handbook |
| **jsjiami 还原** | 开源工具 | GitHub: javascript-obfuscator-deobfuscator |
| **webcrack** | Webpack 反打包 | https://github.com/j4k0xb/webcrack |
| **de4js** | 在线反混淆 | https://lelinhtinh.github.io/de4js/ |

---

## 总结

AST 是对抗高阶混淆的终极手段。掌握以下技能：

1. ✅ **Babel 工作流**: parse → traverse → generate
2. ✅ **常用转换**: 常量折叠、死代码消除、字符串数组还原
3. ✅ **Visitor 模式**: 理解如何遍历和修改 AST
4. ✅ **Path 和 Scope**: 掌握路径操作和作用域分析
5. ✅ **类型系统**: 使用 @babel/types 创建和检查节点
6. ✅ **性能优化**: 单次遍历、提前退出、限制深度

**记住**: AST 虽然学习曲线陡峭，但一旦掌握，你就能像外科手术一样精确地剔除代码中的"毒瘤"。

---

## 相关章节

- [JavaScript 反混淆](../04-Advanced-Recipes/javascript_deobfuscation.md)
- [动态参数分析](../03-Basic-Recipes/dynamic_parameter_analysis.md)
- [Node.js 调试指南](./nodejs_debugging.md)
- [浏览器开发者工具](./browser_devtools.md)
