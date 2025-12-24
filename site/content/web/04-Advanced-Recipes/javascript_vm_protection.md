---
title: "JavaScript 虚拟机保护"
weight: 10
---

# JavaScript 虚拟机保护

## 概述

JavaScript 虚拟机保护（JSVMP, Virtual Machine based code Protection for JavaScript）是一种高级的前端代码保护技术，通过将 JavaScript 源代码转换为自定义字节码，并使用专门的解释器执行，从而有效隐藏原始业务逻辑，增加逆向分析难度。

JSVMP 概念最早由西北大学 2015 级硕士研究生匡凯元在其 2018 年的论文《基于 WebAssembly 的 JavaScript 代码虚拟化保护方法研究与实现》中提出。

---

## 📚 前置知识

在开始本配方之前，建议先掌握以下内容：

| 知识领域 | 重要程度 | 参考资料 |
|----------|---------|---------|
| JavaScript 反混淆 | 必需 | [JavaScript 反混淆](./javascript_deobfuscation.md) |
| JavaScript 执行机制 | 必需 | [JavaScript 执行机制](../01-Foundations/javascript_execution_mechanism.md) |
| V8 引擎工具 | 必需 | [V8 工具](../02-Tooling/v8_tools.md) |
| AST 工具 | 推荐 | [AST 工具](../02-Tooling/ast_tools.md) |
| 调试技巧 | 推荐 | [调试技巧与断点设置](../03-Basic-Recipes/debugging_techniques.md) |

> ⚠️ **难度警告**: JSVMP 是目前**最复杂**的 JavaScript 保护技术之一，逆向难度极高。建议在熟练掌握常规混淆还原技术后再挑战本配方。

---

## 基础概念

### 定义

JSVMP（JavaScript Virtual Machine Protection）是一种 JavaScript 代码虚拟化保护方案。其核心思想是将代码虚拟化引入 JavaScript 代码保护中，将目标 JS 代码转换为只有特殊解释器才能识别的自定义字节码，隐藏目标代码的关键逻辑。

与传统的混淆、加密等保护方式不同，JSVMP 通过虚拟化技术从根本上改变了代码的执行方式。

### 核心原理

JSVMP 的工作流程包括以下几个关键步骤：

1. **词法分析 → 语法分析 → AST 生成**：解析原始 JavaScript 代码生成抽象语法树
2. **私有指令生成**：基于 AST 实现不同的虚拟化策略，将高级语法拆分为具有原子操作特性的中间代码
3. **字节码编码**：将中间代码映射到虚拟指令并编码成字节码
4. **私有解释器生成**：生成能够执行自定义字节码的虚拟机解释器

整个过程将原始代码转换为失去文本语法属性的字节码，使得逆向分析变得极其困难。

---

## 详细内容

### 虚拟机架构

JSVMP 的保护结构主要由两部分组成：

```mermaid
graph TB
subgraph Source["原始 JavaScript 代码"]
JS[JavaScript 源代码<br/>━━━━━━━━<br/>function encrypt(data) {<br/> return hash(data);<br/>}]
end

subgraph Compiler["编译阶段（离线）"]
Lexer[词法分析器<br/>Tokenizer]
Parser[语法分析器<br/>Parser]
AST[抽象语法树<br/>AST]
IRGen[中间代码生成<br/>IR Generator]
BytecodeGen[字节码生成<br/>Bytecode Generator]

JS --> Lexer --> Parser --> AST
AST --> IRGen
IRGen --> BytecodeGen
end

subgraph Output["输出产物"]
Bytecode[自定义字节码<br/>━━━━━━━━<br/>0x01 0x42 0x3A ...<br/>操作码序列]

ConstPool[常量池<br/>━━━━━━━━<br/>• 数字常量<br/>• 字符串表<br/>• 函数引用]

VMCode[VM 解释器<br/>━━━━━━━━<br/>• WebAssembly<br/>• 混淆的 JS]
end

BytecodeGen --> Bytecode
BytecodeGen --> ConstPool
BytecodeGen --> VMCode

subgraph Runtime["运行时执行"]
VMInit[VM 初始化<br/>━━━━━━━━<br/>• 创建上下文<br/>• 加载字节码<br/>• 初始化常量池]

VMContext[VM 上下文<br/>━━━━━━━━<br/>• 虚拟栈<br/>• 局部变量表<br/>• PC 寄存器]

Dispatcher[指令分发器<br/>━━━━━━━━<br/>• 读取操作码<br/>• 路由到 Handler]

Handlers[指令处理器集合<br/>━━━━━━━━<br/>• Handler_PUSH<br/>• Handler_ADD<br/>• Handler_CALL<br/>• Handler_JMP<br/>• ...]

VMExit[VM 退出<br/>━━━━━━━━<br/>• 返回结果<br/>• 清理资源]

VMInit --> VMContext
VMContext --> Dispatcher
Dispatcher --> Handlers
Handlers --> Dispatcher
Dispatcher --> VMExit
end

Bytecode -.加载.-> VMInit
ConstPool -.加载.-> VMInit
VMCode -.执行.-> Runtime

style JS fill:#e1f5ff
style Bytecode fill:#f5a623
style VMCode fill:#bd10e0
style Dispatcher fill:#4a90e2
```

**架构组成部分**:

1. **虚拟指令集（Bytecode）**

- 自定义的操作码集合
- 编码后的指令序列
- 常量池和字符串表

2. **虚拟解释器（VM Interpreter）**
- **VMContext**：虚拟执行上下文，维护执行状态
- **VMInit**：初始化模块，设置虚拟机环境
- **Dispatcher**：调度器，负责指令分发
- **Handler**：字节码处理器，执行具体指令
- **VMExit**：退出模块，清理虚拟机状态

### 基于 WebAssembly 的实现

为了进一步增强保护强度，现代 JSVMP 解释器通常基于 WebAssembly 实现：

- 核心逻辑使用 C/C++ 编写
- 通过 Emscripten 框架编译为 WebAssembly 二进制格式
- 在浏览器中无法直接读取源代码
- 执行性能优于纯 JavaScript 实现

### 代码虚拟化策略

针对不同类型的目标代码，JSVMP 实现了不同的虚拟化策略：

1. **指令拆分**

- 将 JavaScript 代码转换为具有原子操作特性的中间代码
- 模拟本地执行环境

2. **自定义虚拟指令集**

- 将中间代码映射到虚拟指令
- 编码为自定义字节码格式

3. **字符串和属性替换**
- 将属性名和字符串替换为数组元素索引
- 进一步隐藏代码语义

### 相比传统保护的优势

| 保护方式 | 可绕过性 | 安全性 |
| --------- | -------------------------------- | ------ |
| 代码混淆 | 可通过 AST 还原 | 低 |
| 代码加密 | 可通过 Hook 获取解密后代码 | 中 |
| 反调试 | 可移除反调试代码 | 低 |
| **JSVMP** | **移除解释器会导致功能完全丧失** | **高** |

JSVMP 将目标代码转换为自定义字节码，破坏了文本语法属性，隐藏了关键逻辑。与反调试或加密等可以通过移除保护结构来绕过的方法不同，移除 JSVMP 解释器会导致原始功能完全失去恢复能力。

---

## JSVMP 逆向分析方法

### 三种主要逆向方法（2025）

目前针对 JSVMP 的逆向主要有三种方法：

1. **RPC 远程调用**

- 在真实浏览器环境中执行 JSVMP 保护的函数
- 通过网络接口暴露功能
- 优点：实现简单，稳定性高
- 缺点：需要维护浏览器环境，性能开销大

2. **环境补充（补环境）**

- 在 Node.js 中模拟浏览器环境
- 补充缺失的 DOM、BOM API
- 优点：执行效率高
- 缺点：需要大量环境适配工作

3. **插桩还原算法**
- 通过日志输出关键参数
- 从结果反推生成逻辑
- 实现纯算法还原
- 优点：不依赖原始代码，可移植性强
- 缺点：工作量大，需要深入理解算法

### 关键调试技巧

#### 1. AST 反混淆

使用工具对混淆代码进行还原：

```javascript
// 使用 v_jstools 插件进行 AST 反混淆
// 安装：npm install v_jstools

const parser = require("@babel/parser");
const traverse = require("@babel/traverse").default;
const generator = require("@babel/generator").default;
const fs = require("fs");

// 读取混淆代码
const code = fs.readFileSync("obfuscated.js", "utf-8");
const ast = parser.parse(code);

// 进行 AST 转换
traverse(ast, {
// 添加反混淆规则
});

// 生成还原后的代码
const output = generator(ast).code;
fs.writeFileSync("deobfuscated.js", output);
```

#### 2. 插桩/日志记录

在关键位置插入日志，输出关键参数信息：

```javascript
// 原始 JSVMP 解释器代码（示例）
function vmExecute(bytecode, context) {
// 插桩：记录字节码执行过程
console.log("Executing bytecode:", bytecode);
console.log("Context:", JSON.stringify(context));

let pc = 0;
while (pc < bytecode.length) {
const opcode = bytecode[pc];

// 插桩：记录每条指令
console.log(`PC: ${pc}, Opcode: ${opcode}`);

switch (opcode) {
case OP_LOAD:
// 插桩：记录加载操作
console.log("LOAD operation:", bytecode[pc + 1]);
break;
// ... 其他指令
}
pc++;
}
}
```

#### 3. 浏览器替换函数

使用浏览器的资源覆盖功能调试：

```javascript
// 在 Chrome DevTools 中使用 Overrides 功能
// 1. 打开 DevTools → Sources → Overrides
// 2. 选择本地文件夹
// 3. 修改 JS 文件并保存
// 4. 刷新页面测试修改后的代码

// 示例：Hook JSVMP 解释器
(function () {
const originalVMExecute = window.vmExecute;
window.vmExecute = function (...args) {
console.log("VM Execute called with:", args);
const result = originalVMExecute.apply(this, args);
console.log("VM Execute result:", result);
return result;
};
})();
```

#### 4. 动态分析

使用调试器捕获运行时指令流：

```javascript
// 在关键位置设置断点
// 使用 Chrome DevTools 的条件断点功能

// 条件断点示例：
// 当某个变量等于特定值时暂停
if (context.register[0] === 0x1234) {
debugger;
}

// 记录执行路径
const executionTrace = [];
function traceExecution(pc, opcode) {
executionTrace.push({ pc, opcode, timestamp: Date.now() });
}
```

#### 5. Apply 方法追踪

针对使用 apply 的循环代码进行分析：

```javascript
// Hook Function.prototype.apply
const originalApply = Function.prototype.apply;
Function.prototype.apply = function (thisArg, args) {
// 记录 apply 调用
console.log("Apply called:");
console.log(" Function:", this.name || "anonymous");
console.log(" This:", thisArg);
console.log(" Args:", args);

// 调用原始方法
const result = originalApply.call(this, thisArg, args);

console.log(" Result:", result);
return result;
};

// 在日志中分析算法逻辑，避免大量动态调试
```

---

## 实战案例分析

### 案例：某音 X-Bogus 参数分析

某短视频平台使用 JSVMP 保护其 X-Bogus 参数生成算法，以下是逆向分析的步骤：

#### 步骤 1：定位 JSVMP 解释器

```javascript
// 搜索特征代码
// 1. 查找 WebAssembly 实例化代码
const wasmMatch = code.match(/WebAssembly\.instantiate/);

// 2. 查找大量的 switch-case 结构（Dispatcher 特征）
const switchMatch = code.match(/switch\s*\(\s*\w+\s*\)\s*\{/g);

// 3. 查找字节码数组（通常是大型 Uint8Array）
const bytecodeMatch = code.match(/new\s+Uint8Array\(\[[\d,\s]+\]\)/);
```

#### 步骤 2：插桩分析

```javascript
// 在 Dispatcher 中插入日志
function dispatcher(opcode, operand) {
console.log(`Opcode: 0x${opcode.toString(16)}, Operand: ${operand}`);

switch (opcode) {
case 0x01: // LOAD
console.log(" Action: LOAD from", operand);
break;
case 0x02: // STORE
console.log(" Action: STORE to", operand);
break;
case 0x10: // ADD
console.log(" Action: ADD");
break;
// ... 更多指令
}
}
```

#### 步骤 3：算法还原

基于日志分析，还原核心算法：

```javascript
// 从 JSVMP 字节码执行日志中还原的算法
function generateXBogus(params) {
// 步骤 1: 参数序列化
const serialized = serializeParams(params);

// 步骤 2: MD5 哈希
const hash = md5(serialized);

// 步骤 3: 时间戳处理
const timestamp = Math.floor(Date.now() / 1000);

// 步骤 4: 混合编码
const mixed = mixEncode(hash, timestamp);

// 步骤 5: Base64 变种编码
const encoded = customBase64(mixed);

return encoded;
}

// 辅助函数实现
function serializeParams(params) {
return Object.keys(params)
.sort()
.map((key) => `${key}=${params[key]}`)
.join("&");
}

function mixEncode(hash, timestamp) {
const result = [];
for (let i = 0; i < hash.length; i++) {
result.push(hash.charCodeAt(i) ^ (timestamp & 0xff));
}
return result;
}
```

---

## 最佳实践

### 对于开发者（实施保护）

1. **合理选择保护范围**

- 仅对核心算法和敏感逻辑使用 JSVMP
- 避免保护整个应用，影响性能和调试
- 考虑保护粒度与性能的平衡

2. **性能优化**

- 使用 WebAssembly 实现解释器以提升性能
- 对热点代码路径进行优化
- 实现指令缓存机制

3. **多层防护**
- JSVMP 结合代码混淆
- 添加反调试和环境检测
- 实施完整性校验

### 对于逆向分析者

1. **选择合适的逆向方法**

- 简单场景使用 RPC 调用
- 复杂场景考虑算法还原
- 根据具体需求权衡成本和收益

2. **工具化分析流程**

- 开发自动化插桩工具
- 建立 JSVMP 特征库
- 积累常见指令集模式

3. **团队协作**
- 分享 JSVMP 解释器特征
- 共享逆向工具和脚本
- 建立案例知识库

---

## 常见问题

### Q: JSVMP 会显著影响网页性能吗？

**A**: 会有一定影响。JSVMP 将原生 JavaScript 执行转换为虚拟机解释执行，会带来性能开销。根据实现方式不同，性能损失通常在 2-10 倍之间。使用 WebAssembly 实现的解释器性能损失较小（2-3 倍），纯 JavaScript 实现可能达到 5-10 倍。因此建议仅对核心算法使用 JSVMP，而非整个应用。

### Q: JSVMP 保护是否绝对安全？

**A**: 没有绝对安全的保护。JSVMP 大幅增加了逆向分析的难度和成本，但仍然可以通过以下方式绕过：

- RPC 远程调用（黑盒使用）
- 深度插桩分析还原算法
- 内存分析和动态调试
- 机器学习辅助的模式识别

JSVMP 的目标是提高攻击成本，而非完全防止逆向。

### Q: 如何检测代码是否使用了 JSVMP？

**A**: 可以通过以下特征识别：

- 存在大量 switch-case 结构（Dispatcher）
- 包含 WebAssembly 模块实例化
- 存在大型的字节码数组（Uint8Array）
- 函数调用被替换为虚拟机执行调用
- 代码中存在明显的虚拟寄存器和虚拟栈操作

### Q: JSVMP 与代码混淆的区别？

**A**: 主要区别：

| 特性 | 代码混淆 | JSVMP |
| -------- | ---------------------- | ---------------- |
| 原理 | 重命名、控制流平坦化等 | 代码虚拟化 |
| 可读性 | 降低但仍可理解 | 完全失去语法属性 |
| 执行方式 | 直接执行 | 虚拟机解释执行 |
| 性能影响 | 较小（0-50%） | 较大（2-10 倍） |
| 逆向难度 | 中 | 高 |
| 可还原性 | AST 可部分还原 | 难以完全还原 |

### Q: 学习 JSVMP 逆向需要哪些基础？

**A**: 建议掌握以下知识：

- JavaScript 语言深入理解（作用域、闭包、原型链等）
- 编译原理基础（词法分析、语法分析、AST）
- 虚拟机原理（指令集、解释器、字节码）
- WebAssembly 基础
- 逆向工程思维和方法
- 熟练使用浏览器开发者工具

---

## 进阶阅读

### 学术论文

- 匡凯元. 《基于 WebAssembly 的 JavaScript 代码虚拟化保护方法研究与实现》. 西北大学硕士论文, 2018
- Stephen Fewer. 《Virtual Machine Based Obfuscation》. 2006

### 技术博客

- [深入了解 JS 加密技术及 JSVMP 保护原理分析](https://blog.jsvmp.com/jsjiamihejsvmpyuanlifenx/)
- [JS 虚拟化代码虚拟化保护原理分析](https://blog.jsvmp.com/jsxunihua/)
- [JSVMP 分析 - CSDN](https://blog.csdn.net/Awesome_py/article/details/136652368)
- [JavaScript VMP 分析与调试](https://blog.csdn.net/liu_yueyang/article/details/149280146)
- [VMP（虚拟机保护）原理、工程落地、性能权衡与玩具实现](https://blog.csdn.net/weixin_43114209/article/details/150575091)

### 实战案例

- [某音 X-Bogus 逆向分析，JSVMP 纯算法还原](https://www.cnblogs.com/ikdl/p/16807224.html)
- [JSVMP 逆向实战 x-s、x-t 算法还原](https://blog.csdn.net/jerry3747/article/details/130889462)
- [JSVMP 编译与反编译详解](https://www.resourch.com/archives/95.html)
- [JSVMP 逆向（补环境篇）](https://blog.csdn.net/qq_59848320/article/details/132722222)

### 开源项目

- [vm2](https://github.com/patriksimek/vm2) - Node.js 沙箱虚拟机
- [js-sandbox](https://github.com/gf3/sandbox) - JavaScript 沙箱
- [Emscripten](https://emscripten.org/) - C/C++ 到 WebAssembly 编译器

---

## 相关章节

- [WebAssembly 逆向](./webassembly_reversing.md) - WebAssembly 技术基础
- [JavaScript 反混淆](../02-Techniques/js_deobfuscation.md) - 代码反混淆技术
- [AST 解析和操作](../02-Tooling/ast_tools.md) - AST 工具使用
- [浏览器调试技巧](../03-Basic-Recipes/debugging_techniques.md) - 高级调试方法
- [前端加固技术](./frontend_hardening.md) - 其他前端保护技术
