# 反混淆脚本

## 概述

JavaScript 混淆是保护代码逻辑的常用手段。本章提供常用的反混淆脚本和技术，帮助还原混淆后的代码。

---

## 混淆类型识别

### 1. 变量名混淆

**特征**:

```javascript
var _0x1a2b = "Hello";
var _0x3c4d = "World";
console.log(_0x1a2b, _0x3c4d);
```

**工具**: Prettier 格式化后手动重命名

### 2. 字符串数组混淆

**特征**:

```javascript
var _0x1234 = ["Hello", "World", "console", "log"];
var _0xa = _0x1234[0];
var _0xb = _0x1234[1];
window[_0x1234[2]][_0x1234[3]](_0xa, _0xb);
```

**脚本**: 见下方字符串数组还原脚本

### 3. 控制流平坦化

**特征**:

```javascript
var _0x1 = 0;
while (true) {
switch (_0x1) {
case 0:
console.log("A");
_0x1 = 1;
break;
case 1:
console.log("B");
_0x1 = 2;
break;
case 2:
return;
}
}
```

### 4. 死代码注入

**特征**:

```javascript
function real() {
var fake1 = 123;
if (false) {
/* 永远不会执行的代码 */
}
return "real";
}
```

---

## 在线工具

### 1. Prettier

**用途**: 格式化压缩的代码

```bash
# 安装
npm install -g prettier

# 格式化
prettier --write obfuscated.js
```

**在线版**: https://prettier.io/playground/

### 2. JS-Beautify

**用途**: 美化 JavaScript 代码

```bash
npm install -g js-beautify
js-beautify obfuscated.js > formatted.js
```

**在线版**: https://beautifier.io/

### 3. de4js

**用途**: 综合反混淆工具

**在线版**: https://lelinhtinh.github.io/de4js/

支持:

- JSFuck
- JJencode
- AAencode
- URLencode
- Packer
- JavaScript Obfuscator

---

## AST 反混淆脚本

### 基础框架

使用 Babel 解析和转换 AST：

```javascript
const parser = require("@babel/parser");
const traverse = require("@babel/traverse").default;
const generator = require("@babel/generator").default;
const t = require("@babel/types");
const fs = require("fs");

// 1. 读取混淆代码
const code = fs.readFileSync("obfuscated.js", "utf-8");

// 2. 解析为 AST
const ast = parser.parse(code);

// 3. 遍历和转换
traverse(ast, {
// 在这里添加转换规则
});

// 4. 生成代码
const output = generator(ast, {}, code);
fs.writeFileSync("deobfuscated.js", output.code);
```

### 脚本 1: 常量折叠

**目标**: 计算常量表达式

```javascript
traverse(ast, {
BinaryExpression(path) {
// 如果两个操作数都是字面量
if (t.isLiteral(path.node.left) && t.isLiteral(path.node.right)) {
// 计算结果
const result = eval(path.toString());
// 替换为结果
path.replaceWith(t.valueToNode(result));
}
},
});
```

**示例**:

```javascript
// Before
var a = 1 + 2;

// After
var a = 3;
```

### 脚本 2: 字符串数组还原

**目标**: 还原字符串数组引用

```javascript
let stringArray = [];

traverse(ast, {
// 第一步：找到字符串数组
VariableDeclarator(path) {
if (t.isArrayExpression(path.node.init)) {
const name = path.node.id.name;
stringArray = path.node.init.elements.map((e) => e.value);
}
},

// 第二步：替换数组访问
MemberExpression(path) {
// _0x1234[0] => stringArray[0]
if (
t.isIdentifier(path.node.object) &&
t.isNumericLiteral(path.node.property)
) {
const index = path.node.property.value;
const value = stringArray[index];
if (value !== undefined) {
path.replaceWith(t.stringLiteral(value));
}
}
},
});
```

**示例**:

```javascript
// Before
var _0x1234 = ["log", "Hello"];
console[_0x1234[0]](_0x1234[1]);

// After
console["log"]("Hello");
// 后续还可以继续优化为: console.log('Hello');
```

### 脚本 3: 计算成员表达式

**目标**: `obj['prop']` → `obj.prop`

```javascript
traverse(ast, {
MemberExpression(path) {
// 如果是 obj['prop'] 形式
if (path.node.computed && t.isStringLiteral(path.node.property)) {
const propName = path.node.property.value;
// 检查是否是合法标识符
if (/^[a-zA-Z_$][a-zA-Z0-9_$]*$/.test(propName)) {
path.node.computed = false;
path.node.property = t.identifier(propName);
}
}
},
});
```

**示例**:

```javascript
// Before
console["log"]("Hello");

// After
console.log("Hello");
```

### 脚本 4: 删除死代码

**目标**: 删除 `if (false)` 等死代码

```javascript
traverse(ast, {
IfStatement(path) {
// 如果条件是 false
if (t.isBooleanLiteral(path.node.test, { value: false })) {
// 删除整个 if 语句
path.remove();
}
// 如果条件是 true
else if (t.isBooleanLiteral(path.node.test, { value: true })) {
// 用 consequent 替换整个 if
path.replaceWithMultiple(path.node.consequent.body);
}
},
});
```

### 脚本 5: 函数内联

**目标**: 内联简单的包装函数

```javascript
const functionMap = {};

traverse(ast, {
// 收集函数定义
FunctionDeclaration(path) {
const name = path.node.id.name;
// 只处理简单的返回语句函数
if (
path.node.body.body.length === 1 &&
t.isReturnStatement(path.node.body.body[0])
) {
functionMap[name] = path.node.body.body[0].argument;
}
},

// 替换函数调用
CallExpression(path) {
if (t.isIdentifier(path.node.callee)) {
const name = path.node.callee.name;
if (functionMap[name]) {
// 替换为函数体
path.replaceWith(functionMap[name]);
}
}
},
});
```

---

## 完整反混淆流程

### 自动化脚本

```javascript
const fs = require("fs");
const parser = require("@babel/parser");
const traverse = require("@babel/traverse").default;
const generator = require("@babel/generator").default;
const t = require("@babel/types");

function deobfuscate(inputFile, outputFile) {
console.log(`[1/5] 读取文件: ${inputFile}`);
const code = fs.readFileSync(inputFile, "utf-8");

console.log("[2/5] 解析 AST");
const ast = parser.parse(code);

console.log("[3/5] 常量折叠");
constantFolding(ast);

console.log("[4/5] 字符串数组还原");
restoreStringArray(ast);

console.log("[5/5] 清理和格式化");
cleanup(ast);

const output = generator(ast, { comments: false }, code);
fs.writeFileSync(outputFile, output.code);
console.log(`✅ 完成! 输出到: ${outputFile}`);
}

function constantFolding(ast) {
traverse(ast, {
BinaryExpression(path) {
if (path.isConstantExpression()) {
const result = path.evaluate();
if (result.confident) {
path.replaceWith(t.valueToNode(result.value));
}
}
},
});
}

function restoreStringArray(ast) {
let stringArray = [];
let arrayName = "";

traverse(ast, {
VariableDeclarator(path) {
if (t.isArrayExpression(path.node.init)) {
arrayName = path.node.id.name;
stringArray = path.node.init.elements.map((e) => e.value);
}
},
});

if (stringArray.length === 0) return;

traverse(ast, {
MemberExpression(path) {
if (
t.isIdentifier(path.node.object, { name: arrayName }) &&
t.isNumericLiteral(path.node.property)
) {
const index = path.node.property.value;
const value = stringArray[index];
if (value !== undefined) {
path.replaceWith(t.stringLiteral(value));
}
}
},
});
}

function cleanup(ast) {
traverse(ast, {
// 删除空语句
EmptyStatement(path) {
path.remove();
},
// obj['prop'] -> obj.prop
MemberExpression(path) {
if (path.node.computed && t.isStringLiteral(path.node.property)) {
const prop = path.node.property.value;
if (/^[a-zA-Z_$][a-zA-Z0-9_$]*$/.test(prop)) {
path.node.computed = false;
path.node.property = t.identifier(prop);
}
}
},
});
}

// 使用示例
deobfuscate("obfuscated.js", "deobfuscated.js");
```

---

## 针对特定混淆器

### JavaScript Obfuscator

特征识别：

```javascript
var _0x1234 = function () {
/* ... */
};
(function (_0xabc, _0xdef) {
/* ... */
})(_0x1234, 0x123);
```

工具: https://github.com/javascript-deobfuscator/webcrack

### Webpack Bundle

使用 `webcrack`:

```bash
npm install -g webcrack
webcrack bundle.js -o output/
```

### JJencode

```javascript
function decode_jjencode(encoded) {
// JJencode 使用颜文字编码
return eval(encoded);
}
```

在线: https://utf-8.jp/public/jjencode.html

---

## 实战案例

### 案例：某电商网站混淆分析

**原始代码**:

```javascript
var _0x1a2b = ["log", "价格"];
console[_0x1a2b[0]](_0x1a2b[1]);
```

**反混淆步骤**:

1. **字符串数组提取**:

```javascript
// _0x1a2b = ['log', '价格']
```

2. **替换引用**:

```javascript
console["log"]("价格");
```

3. **成员表达式优化**:

```javascript
console.log("价格");
```

---

## 工具集合

| 工具 | 用途 | 链接 |
| ---------------- | -------------- | ----------------------------------- |
| **Prettier** | 格式化 | https://prettier.io/ |
| **de4js** | 综合反混淆 | https://lelinhtinh.github.io/de4js/ |
| **webcrack** | Webpack 反打包 | https://github.com/j4k0xb/webcrack |
| **Babel** | AST 操作 | https://babeljs.io/ |
| **AST Explorer** | 可视化 AST | https://astexplorer.net/ |

---

## 最佳实践

1. **分步处理**: 不要一次性处理所有混淆，逐步还原
2. **保留原文件**: 始终保留原始混淆代码作为备份
3. **验证正确性**: 每一步都要验证代码功能未被破坏
4. **结合动态调试**: AST 反混淆 + DevTools 调试结合使用
5. **识别混淆器**: 不同混淆器用不同工具，事半功倍

---

## 商业化反混淆解决方案对比

JavaScript 反混淆既是技术活也是体力活，商业化工具可以大幅提升效率。以下是业界主流方案的专业对比。

### 1. 企业级反混淆工具

#### JScrambler Reverse Engineering Tool

**定位**: 商业 JavaScript 保护工具的配套分析工具

**功能**:

- 识别 JScrambler 保护的代码
- 自动化去除某些保护层
- 控制流分析
- 代码覆盖率追踪

**价格**: 包含在 JScrambler 企业订阅中（$1,000+/月）

**局限**: 主要针对自家混淆器

**官网**: https://jscrambler.com/

---

#### JSDetox（在线反混淆）

**类型**: 免费在线工具（社区维护）

**功能**:

- 自动检测混淆类型
- 支持多种常见混淆器
- 交互式分析环境
- DOM 模拟执行

**优势**:

- 完全免费
- 无需安装
- 社区活跃

**劣势**:

- 不支持高级混淆
- 处理大文件较慢
- 缺乏商业支持

**官网**: http://www.jsdetox.com/

---

#### Synchrony（代码分析平台）

**定位**: 企业级静态分析平台

**功能**:

- JavaScript/TypeScript 深度分析
- 自动化反混淆流水线
- 漏洞检测
- 代码质量评估

**价格**: 企业定价（$10,000+/年）

**适用**: 大型代码库安全审计

**官网**: https://www.synopsys.com/

---

### 2. 专业反混淆服务对比

#### De4js（功能最全面）

**类型**: 开源免费在线工具

**支持混淆类型**:

- ✅ **JavaScript Obfuscator** (obfuscator.io)
- ✅ **JSFuck** (jsfuck.com)
- ✅ **JJencode** (utf-8.jp)
- ✅ **AAencode** (utf-8.jp)
- ✅ **URLencode**
- ✅ **Packer** (Dean Edwards)
- ✅ **Eval Chain**

**在线地址**: https://lelinhtinh.github.io/de4js/

**使用示例**:

```javascript
// 输入混淆代码
var _0x1a2b = ["Hello", "World"];
console.log(_0x1a2b[0], _0x1a2b[1]);

// 自动检测并还原
// 输出: console.log('Hello', 'World');
```

**优势**: 一站式解决大部分简单混淆

---

#### Webcrack（Webpack 专用）

**类型**: 开源 CLI 工具

**专注领域**: Webpack 打包代码逆向

**功能**:

- 自动识别 Webpack 版本
- 提取独立模块
- 还原原始文件结构
- 重命名变量

**GitHub**: https://github.com/j4k0xb/webcrack

**安装使用**:

```bash
npm install -g webcrack
webcrack bundle.js -o output/

# 输出：
# output/
# ├── module_0.js
# ├── module_1.js
# └── ...
```

**适用场景**: 逆向 React/Vue 等现代前端项目

---

### 3. 代码美化与格式化工具

| 工具 | 类型 | 特点 | 价格 | 推荐指数 |
| ----------------- | -------- | ------------------ | ------- | ---------- |
| **Prettier** | 开源 | 业界标准代码格式化 | 免费 | ⭐⭐⭐⭐⭐ |
| **JS Beautifier** | 开源 | 老牌工具，功能稳定 | 免费 | ⭐⭐⭐⭐ |
| **WebStorm** | 商业 IDE | 内置强大格式化 | $149/年 | ⭐⭐⭐⭐ |
| **ReSharper** | 商业插件 | Visual Studio 集成 | $149/年 | ⭐⭐⭐ |

**推荐组合**: Prettier（格式化）+ webcrack（解包）+ Babel（AST 处理）

---

### 4. AST 处理框架对比

#### Babel 生态（开源首选）

**核心组件**:

- `@babel/parser` - 解析 JS 为 AST
- `@babel/traverse` - 遍历和修改 AST
- `@babel/generator` - AST 转换回代码
- `@babel/types` - AST 节点构建工具

**优势**:

- 完全免费
- 社区庞大
- 文档完善
- 插件丰富

**学习成本**: 中等（需要理解 AST 概念）

**官网**: https://babeljs.io/

---

#### SWC（Rust 实现，速度最快）

**特点**:

- 比 Babel 快 20-70 倍
- 用 Rust 编写
- 兼容 Babel 插件

**适用**: 大规模代码处理

**GitHub**: https://github.com/swc-project/swc

---

#### Esprima vs Acorn

| 特性 | Esprima | Acorn |
| ------------ | -------- | ------ |
| **速度** | 中等 | 快 |
| **标准兼容** | ES2021 | ES2023 |
| **插件系统** | 有限 | 丰富 |
| **维护状态** | 活跃度低 | 活跃 |

**推荐**: 新项目使用 Acorn 或 Babel

---

### 5. 商业咨询与定制服务

#### Recurity Labs（德国安全公司）

**服务内容**:

- JavaScript 混淆逆向
- 恶意代码分析
- 定制化反混淆工具开发

**典型项目**: €20,000 - €100,000

**官网**: https://www.recurity-labs.com/

---

#### Pen Test Partners

**服务内容**:

- 前端安全审计
- 混淆代码分析
- 漏洞挖掘

**价格**: £1,500/人日

**官网**: https://www.pentestpartners.com/

---

### 6. 成本效益分析

#### 场景 1: 分析单个混淆文件（< 1000 行）

**方案 A（手动 + 免费工具）**:

- 工具: de4js + Prettier
- 时间: 1-2 小时
- 成本: **$0**
- 技能要求: 基础

**方案 B（专业工具）**:

- 工具: WebStorm + 自定义 Babel 插件
- 时间: 30 分钟
- 成本: **$149/年**（IDE 许可）
- 技能要求: 中等

---

#### 场景 2: 批量处理混淆代码（>10,000 文件）

**方案 A（自建工具链）**:

- 工具: Babel + 自定义脚本 + CI/CD 集成
- 初始投入: 3-5 个工作日开发
- 运行成本: **$0**
- 维护成本: 每月 1-2 小时

**方案 B（商业服务）**:

- 工具: Synopsys Code Insight
- 成本: **$50,000/年**起
- 优势: 零维护，企业支持

**结论**: 批量处理场景自建 ROI 更高

---

#### 场景 3: 紧急项目（24 小时内需要结果）

**方案 A（加急咨询）**:

- 服务: Pen Test Partners 加急服务
- 成本: **£5,000-15,000**
- 保障: 专业团队，保证质量

**方案 B（远程外包）**:

- 平台: Upwork/Fiverr 逆向工程师
- 成本: **$500-2,000**
- 风险: 质量参差不齐

---

### 7. 开源 vs 商业方案决策矩阵

| 因素 | 推荐开源 | 推荐商业 |
| ------------ | ------------- | -------------- |
| **项目规模** | < 10,000 文件 | > 50,000 文件 |
| **团队规模** | < 5 人 | > 10 人 |
| **预算** | < $10,000/年 | > $50,000/年 |
| **技术能力** | 有 AST 经验 | 无专业逆向团队 |
| **合规要求** | 无特殊要求 | 需审计报告 |
| **时间压力** | 可灵活安排 | 紧急交付 |

---

### 8. AI 辅助反混淆（新兴趋势）

#### ChatGPT/Claude Code Analysis

**应用场景**:

- 解释混淆代码逻辑
- 生成反混淆脚本
- 识别混淆模式

**示例 Prompt**:

```
分析以下混淆JavaScript代码，解释其逻辑：
var _0x1a2b=['log','Hello'];
console[_0x1a2b[0]](_0x1a2b[1]);
```

**局限性**:

- 无法处理大文件（Token 限制）
- 可能误判复杂混淆
- 不适合批量处理

**成本**: $0.01-0.06/1K tokens（API 调用）

---

#### GitHub Copilot 辅助编写反混淆脚本

**优势**:

- 加速 Babel 插件开发
- 提供 AST 操作示例
- 代码补全

**成本**: $10/月或$100/年

---

### 9. 实战工具链推荐

#### 初学者配置（$0 成本）

```bash
# 安装工具
npm install -g prettier webcrack
npm install @babel/parser @babel/traverse @babel/generator

# 工作流程
1. 使用 de4js 在线初步分析
2. prettier格式化代码
3. webcrack解包Webpack（如适用）
4. 自写Babel脚本深度处理
```

---

#### 专业团队配置（< $1,000/年）

```bash
# 商业工具
- WebStorm IDE: $149/年
- GitHub Copilot: $100/年
- Better Comments（VS Code插件）: 免费

# 开源工具
- Babel完整工具链
- AST Explorer（在线）
- Source Map Visualization

总成本: $249/年 + 学习时间投入
```

---

#### 企业级配置（$10,000+/年）

- **Synopsys Code Insight**: 自动化代码分析
- **Fortify SCA**: 静态代码扫描
- **专业咨询**: 按需购买逆向服务
- **内部培训**: 团队技能提升

**ROI 分析**: 适合有合规要求或大规模项目的企业

---

### 10. 避坑指南

**常见错误**:

1. ❌ 过度依赖自动化工具（复杂混淆仍需手动分析）
2. ❌ 忽视代码版权（逆向后的代码使用需遵守法律）
3. ❌ 不备份原始文件（反混淆可能破坏代码）
4. ❌ 盲目追求完美还原（有时部分还原即可满足需求）

**最佳实践**:

1. ✅ 分层处理，逐步还原
2. ✅ 结合动态调试验证
3. ✅ 建立混淆特征库
4. ✅ 自动化重复性工作

---

### 11. 法律与合规考量

**警告**: 反混淆他人代码可能涉及法律风险

**合法场景**:

- ✅ 安全研究（合法授权）
- ✅ 恶意软件分析
- ✅ 自己的代码逆向
- ✅ 开源项目分析

**风险场景**:

- ❌ 商业软件逆向（未授权）
- ❌ 绕过 DRM 保护
- ❌ 窃取商业机密

**建议**: 进行商业逆向前咨询法律顾问

---

## 相关章节

- [JavaScript 反混淆](../04-Advanced-Recipes/javascript_deobfuscation.md)
- [AST 解析工具](../02-Tooling/ast_parsing_tools.md)
- [调试技巧与断点设置](../03-Basic-Recipes/debugging_techniques.md)
- [JavaScript Hook 脚本](javascript_hook_scripts.md)
