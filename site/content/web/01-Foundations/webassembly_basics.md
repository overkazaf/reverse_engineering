---
title: "WebAssembly 基础"
weight: 10
---

# WebAssembly 基础

## 概述

WebAssembly (Wasm) 是一种二进制指令格式，允许在 Web 上运行高性能代码（如 C/C++/Rust 编译而来）。随着越来越多的核心算法（加密、解码、复杂逻辑）被迁移到 Wasm，逆向 Wasm 已成为现代 Web 逆向的必备技能。

---

## Wasm 是什么？

### 1. 核心特性

- **二进制格式 (`.wasm`)**: 紧凑，加载快，但不可读。
- **文本格式 (`.wat`)**: Wasm 的汇编形式，S-expression 风格，可读性尚可。
- **线性内存 (Linear Memory)**: Wasm 只能访问一块连续的 ArrayBuffer，通过下标读写。
- **栈式虚拟机**: 指令基于操作数栈，例如 `i32.add` 会从栈顶弹出两个数，相加后结果压栈。

### 2. JS 与 Wasm 互操作

Wasm 模块需要 JS 来加载和实例化。

```javascript
// 这里可以 Hook !
WebAssembly.instantiate(buffer, imports).then((results) => {
// results.instance.exports 包含 Wasm 导出的函数
});
```

---

## Wasm 逆向流程

### 1. 获取 Wasm 文件

通常在 Network 面板可以看到 `.wasm` 文件的请求。

- _注意_: 有些站点会将 Wasm 二进制数据硬编码在 JS 字符串或 ArrayBuffer 中，然后动态加载。可以通过 Hook `WebAssembly.instantiate` 来捕获 buffer。

### 2. 静态分析 (Disassembly / Decompilation)

拿到 `.wasm` 文件后，需要将其还原为可读代码。

- **wasm2wat (WABT 工具包)**: 转换为 `.wat` 汇编。
```lisp
(func $add (param $p0 i32) (param $p1 i32) (result i32)
local.get $p0
local.get $p1
i32.add)
```
- **Decompilers (反编译器)**: 尝试还原为类 C 代码（伪代码）。
- **JEB Decompiler**: 商业软件，反编译效果较好。
- **Ghidra**: 需要安装 Wasm 插件。
- **wasm-decompile**: WABT 自带，输出类似 C 的伪代码。

### 3. 动态调试

Chrome DevTools 已经很好地支持 Wasm 调试。

1. Sources 面板 -> 找到 `wasm` 文件（通常在 `wasm://` 协议下）。
2. 点击代码行号下断点。
3. 单步调试，观察 Stack（栈）和 Memory（内存）的变化。

---

## 关键逆向技巧

### 1. 寻找导出函数 (Exports)

Wasm 模块通常会导出一个入口函数给 JS 调用（如 `encrypt`, `hash`）。这是我们分析的起点。

### 2. 分析导入函数 (Imports)

Wasm 经常需要调用 JS 函数（因为 Wasm 不能直接操作 DOM 或发送网络请求）。

- 查看 Imports 列表，如果发现导入了 `console.log` 或者网络相关的 JS 函数，可以在这些 JS 函数上 Hook，从而窥探 Wasm 内部状态。

### 3. 内存视图

Wasm 的内存是一个 `WebAssembly.Memory` 对象，本质上是 JS 的 `ArrayBuffer`。

- 任何时候，你都可以通过 JS 读取这块内存：
```javascript
let mem = instance.exports.memory;
let view = new Uint8Array(mem.buffer);
console.log(view.slice(0, 100)); // 查看前100字节
```
- 如果 Wasm 在进行加密操作，密钥往往就在这块内存里。

---

## 总结

Wasm 逆向 = **二进制分析** (IDA/Ghidra) + **Web 动态调试** (DevTools)。虽然门槛比纯 JS 逆向高，但核心逻辑依然是：输入 -> [黑盒处理] -> 输出。只要能控制输入输出，并有能力窥探黑盒内部（Hook Imports, Dump Memory），就能攻克。
