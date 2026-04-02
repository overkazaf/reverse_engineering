---
title: "OLLVM 反混淆"
date: 2024-11-05
type: posts
tags: ["Native层", "签名验证", "逆向分析", "Frida", "OLLVM", "加密分析"]
weight: 10
---

# OLLVM 反混淆

> **📚 前置知识**
>
> 本配方涉及以下核心技术，建议先阅读相关章节：
>
> - **[SO/ELF 格式](../../04-Reference/Foundations/so_elf_format.md)** - 理解 Native 库的结构
> - **[ARM 汇编基础](../../04-Reference/Foundations/arm_assembly.md)** - 阅读反汇编代码的能力

OLLVM (Obfuscator-LLVM) 是一个著名的开源代码混淆框架，它在 LLVM 编译器 IR (中间表示) 层面进行操作。这使其能够与具体语言无关，并对代码应用复杂的、难以逆向的转换。

> [!warning] 场景导入：当你遇到 OLLVM
> 打开 IDA，反编译一个函数，结果看到：
>
> - 一个巨大的 `switch-case` 循环，有几十甚至上百个 case 分支
> - 每个 case 里只有几行代码，然后又跳回 switch
> - 到处都是看起来有用实际无用的 `if` 判断
> - 简单的加法被替换成了 `a = b - (-c)` 这样的怪异表达式
>
> **你的第一反应可能是：这是什么鬼？**
>
> 恭喜，你遇到了 OLLVM 控制流平坦化 (FLA) + 虚假控制流 (BCF) + 指令替换 (SUB) 的"三件套"。
> 这是目前 Android Native 层最常见的商业级混淆方案。
>
> **关键问题**：面对这种混淆，是选择"硬看"代码，还是有更聪明的办法？
>
> 本文档涵盖了常见的 OLLVM 混淆通道 (pass) 及其分析和逆向策略。


---

## 核心混淆技术

OLLVM 的主要优势在于其三种核心混淆技术：

1. **控制流平坦化 (`-fla`)**: 该技术会彻底平坦化一个函数的控制流。它通过将所有基本块放入一个单一的、巨大的分发器循环（"主分发器"）中来隐藏原始的程序流程。一个状态变量用于控制下一个要执行的代码块。逆向此技术需要重建原始的控制流图 (CFG)。

2. **虚假控制流 (`-bcf`)**: 该技术在代码中插入无效的条件分支和不透明谓词。这些分支被设计为静态分析难以解析，但在运行时，它们总是会得出相同的结果。这会给控制流图增加大量的噪声。

3. **指令替换 (`-sub`)**: 这是最简单的混淆方式。它将标准的二进制运算符（如 `add`, `sub`, `and`, `or`）替换为功能上等价但更复杂的指令序列。例如，`a = b + c` 可能会变成 `a = b - (-c)`。

---

## OLLVM 扩展混淆技术

除了经典的三大混淆 Pass，许多 OLLVM 的分支和商业衍生版本引入了更为高级的混淆手段。了解这些扩展技术对于分析现代 Android Native 保护方案至关重要。

### 1. MBA (Mixed Boolean Arithmetic) 混合布尔算术表达式

MBA 是高级 OLLVM 变体用来替换简单算术运算的一种技术。其核心思想是将基本的算术操作（如加法、减法）替换为等价但结合了布尔运算（AND、OR、XOR、NOT）和算术运算的复杂表达式，使逆向分析者难以直接识别原始运算的含义。

**基本 MBA 等价关系：**

| 原始表达式 | MBA 等价形式 |
|-----------|-------------|
| `a + b` | `(a ^ b) + 2 * (a & b)` |
| `a + b` | `(a \| b) + (a & b)` |
| `a - b` | `(a ^ b) - 2 * (~a & b)` |
| `a ^ b` | `(a \| b) - (a & b)` |
| `a \| b` | `(a & b) + (a ^ b)` |

**ARM64 汇编中的 MBA 示例：**

```asm
// 原始操作: X0 = X1 + X2
// MBA 混淆后 (使用 (a | b) + (a & b) = a + b):
AND X3, X1, X2      // X3 = X1 & X2
ORR X4, X1, X2      // X4 = X1 | X2
ADD X0, X3, X4      // X0 = (X1 & X2) + (X1 | X2) = X1 + X2
```

**更复杂的嵌套 MBA 示例：**

```asm
// 原始操作: X0 = X1 + X2
// 深层嵌套 MBA 混淆 (使用 (a ^ b) + 2 * (a & b) = a + b):
EOR X3, X1, X2      // X3 = X1 ^ X2
AND X4, X1, X2      // X4 = X1 & X2
LSL X5, X4, #1      // X5 = (X1 & X2) << 1 = 2 * (X1 & X2)
// 进一步将 X3 + X5 再次 MBA 展开:
EOR X6, X3, X5      // X6 = X3 ^ X5
AND X7, X3, X5      // X7 = X3 & X5
LSL X8, X7, #1      // X8 = 2 * (X3 & X5)
ADD X0, X6, X8      // X0 = X6 + X8 = X3 + X5 = X1 + X2
```

> [!tip] MBA 混淆的特征识别
> 在 IDA 反编译结果中，如果你看到大量 `&`、`|`、`^` 与 `+`、`-` 混合运算，且最终结果仅完成简单的算术，这很可能是 MBA 混淆。特别注意形如 `(x & y) + (x | y)` 或 `(x ^ y) + 2 * (x & y)` 的模式。

**MBA 简化方法与工具：**

- **模式匹配**: 对照已知的 MBA 等价关系进行模板替换
- **SSPAM**: 基于代数简化的 MBA 表达式还原工具
- **MBA-Blast**: 使用位向量求解器批量简化 MBA 表达式
- **SiMBA**: 基于机器学习的 MBA 简化方法，能处理未知模式
- **d810 插件**: IDA Pro 的 Microcode API 插件，内置 MBA 简化规则

**Python MBA 简化示例 (使用 sympy)：**

```python
from sympy import symbols, simplify, And, Or, Xor
from sympy.core.numbers import Integer

def simplify_mba(expr_str):
    """
    简化 MBA 表达式到规范形式
    
    思路：将 MBA 表达式转化为 sympy 符号表达式，
    利用位运算的代数恒等式进行化简。
    """
    a, b = symbols('a b', integer=True)
    
    # 常见 MBA 恒等式验证
    identities = {
        "(a & b) + (a | b)":       a + b,
        "(a ^ b) + 2 * (a & b)":   a + b,
        "(a | b) - (a & b)":       a ^ b,  # XOR
        "(a ^ b) - 2 * (~a & b)":  a - b,
    }
    
    for pattern, simplified in identities.items():
        print(f"  {pattern:40s} => {simplified}")
    
    return identities.get(expr_str, None)

def verify_mba_equivalence():
    """使用穷举法验证 MBA 等价关系（适用于小位宽）"""
    import random
    
    test_cases = [(random.randint(0, 0xFFFFFFFF), random.randint(0, 0xFFFFFFFF)) 
                  for _ in range(10000)]
    
    for a, b in test_cases:
        mask = 0xFFFFFFFF  # 32-bit
        # 验证: (a & b) + (a | b) == a + b
        lhs = ((a & b) + (a | b)) & mask
        rhs = (a + b) & mask
        assert lhs == rhs, f"Failed: a={a:#x}, b={b:#x}"
    
    print("[+] MBA 等价验证通过 (10000 组随机数据)")

verify_mba_equivalence()
```

### 2. OLLVM 字符串加密 Pass (-sobf)

字符串加密是 OLLVM 扩展版本中非常常见的一个 Pass。它在编译时将源代码中的所有字符串常量进行加密，然后在运行时通过 `.init_array` 中注册的解密函数进行解密。这意味着你在 IDA 中直接打开 SO 文件时，`.rodata` 段中看到的都是乱码数据。

**工作原理：**

1. **编译时**: OLLVM 字符串加密 Pass 扫描所有全局字符串常量，用简单的 XOR 或更复杂的算法加密它们
2. **链接时**: 将解密函数注册到 `.init_array` 段（SO 加载时自动执行的函数数组）
3. **运行时**: 当 `dlopen` 加载 SO 时，linker 按顺序调用 `.init_array` 中的函数，字符串被解密回原始内容

**IDA 中的表现：**

```
.init_array:00001000  DCD decrypt_strings_0  ; 字符串解密函数 1
.init_array:00001004  DCD decrypt_strings_1  ; 字符串解密函数 2
.init_array:00001008  DCD real_init          ; 真正的初始化函数

.rodata:00002000  encrypted_str1  DCB 0x7A, 0x4F, 0x52, ...  ; 加密后的字符串
.rodata:00002020  encrypted_str2  DCB 0x1B, 0x33, 0x6E, ...  ; 加密后的字符串
```

**ARM64 字符串解密桩代码示例：**

```asm
; decrypt_strings_0 - 典型的 XOR 解密循环
decrypt_strings_0:
    ADRP    X0, #encrypted_str1@PAGE
    ADD     X0, X0, #encrypted_str1@PAGEOFF
    MOV     W1, #0x1A          ; 字符串长度
    MOV     W2, #0x5A          ; XOR 密钥
.loop:
    LDRB    W3, [X0]           ; 读取一个加密字节
    EOR     W3, W3, W2         ; XOR 解密
    STRB    W3, [X0], #1       ; 写回并递增指针
    SUBS    W1, W1, #1         ; 计数器减一
    B.NE    .loop              ; 循环直到所有字节解密
    RET
```

**使用 Frida 运行时提取解密后的字符串：**

```javascript
// 方法一: Hook .init_array 函数，在解密完成后 dump 字符串
function dumpDecryptedStrings(soName) {
    var mod = Process.findModuleByName(soName);
    if (!mod) {
        console.log("[-] Module not found: " + soName);
        return;
    }

    // 在 SO 加载完成后，.init_array 已经执行，字符串已解密
    // 直接扫描 .rodata 段寻找可读字符串
    var sections = Process.findModuleByName(soName).enumerateSections();
    sections.forEach(function(section) {
        if (section.name === ".rodata") {
            console.log("[*] Scanning .rodata at: " + section.address + 
                        " size: " + section.size);
            
            // 扫描 ASCII 字符串
            var base = section.address;
            var size = section.size;
            var data = Memory.readByteArray(base, size);
            var bytes = new Uint8Array(data);
            
            var currentStr = "";
            for (var i = 0; i < bytes.length; i++) {
                if (bytes[i] >= 0x20 && bytes[i] < 0x7F) {
                    currentStr += String.fromCharCode(bytes[i]);
                } else {
                    if (currentStr.length >= 4) {
                        console.log("[+] String @ offset 0x" + i.toString(16) + 
                                    ": " + currentStr);
                    }
                    currentStr = "";
                }
            }
        }
    });
}

// 方法二: Hook dlopen，在目标 SO 加载时自动提取
Interceptor.attach(Module.findExportByName(null, "dlopen"), {
    onEnter: function(args) {
        this.path = args[0].readCString();
    },
    onLeave: function(retval) {
        if (this.path && this.path.indexOf("libtarget.so") !== -1) {
            console.log("[*] Target SO loaded, dumping strings...");
            // dlopen 返回时 .init_array 已执行完毕
            setTimeout(function() {
                dumpDecryptedStrings("libtarget.so");
            }, 100);
        }
    }
});
```

> [!warning] 注意
> 某些高级字符串加密方案不使用 `.init_array`，而是在首次访问字符串时才解密（延迟解密）。对于这种情况，需要 Hook 字符串所在函数而非 `.init_array`。

### 3. 函数调用混淆 (Indirect Call Obfuscation)

函数调用混淆将直接的函数调用（`BL func`）替换为间接调用，通过函数指针完成跳转。这使得静态分析工具难以构建准确的调用图 (Call Graph)，因为在反汇编层面无法直接看出目标函数的地址。

**工作原理：**

- 原始代码中的 `BL target_func` 被替换为从全局表或加密指针中加载目标地址后的 `BLR Xn`
- 函数指针可能存储在加密的全局表中，运行时通过解密获取真实地址
- 某些变体还会在运行时动态计算目标地址

**ARM64 示例：**

```asm
// 原始代码 - 直接调用:
BL      target_func          // 直接调用 target_func

// 混淆后 - 间接调用:
ADRP    X8, #func_table@PAGE
ADD     X8, X8, #func_table@PAGEOFF
LDR     X8, [X8, #0x18]     // 从函数表加载目标地址
BLR     X8                   // 间接调用

// 更复杂的混淆 - 带解密的间接调用:
ADRP    X8, #encrypted_ptr@PAGE
LDR     X8, [X8, #encrypted_ptr@PAGEOFF]
MOV     X9, #0xDEAD          // 解密密钥的一部分
MOVK    X9, #0xBEEF, LSL #16
EOR     X8, X8, X9           // XOR 解密得到真实地址
BLR     X8                   // 调用解密后的地址
```

**对静态分析的影响：**

- IDA 无法自动识别 `BLR X8` 的目标，调用图中断
- 交叉引用 (xrefs) 缺失，无法追踪函数调用关系
- 需要结合动态分析确定运行时的实际目标地址

**Frida 动态恢复间接调用目标：**

```javascript
// Hook 间接调用指令，记录实际跳转目标
function resolveIndirectCalls(soName, funcOffset) {
    var mod = Process.findModuleByName(soName);
    var funcAddr = mod.base.add(funcOffset);
    
    Stalker.follow(Process.getCurrentThreadId(), {
        transform: function(iterator) {
            var inst = iterator.next();
            do {
                // 检测 BLR 指令
                if (inst.mnemonic === "blr") {
                    iterator.putCallout(function(ctx) {
                        // 读取寄存器中的实际目标地址
                        var target = ctx[inst.operands[0].value];
                        var targetMod = Process.findModuleByAddress(target);
                        var symbol = DebugSymbol.fromAddress(target);
                        console.log("[BLR] " + inst.address + " => " + 
                                    target + " (" + symbol.name + ")");
                    });
                }
                iterator.keep();
            } while ((inst = iterator.next()) !== null);
        }
    });
}
```

---

## OLLVM 变体与商业衍生

在 Android 生态中，原版 OLLVM 早已停止维护（最后版本基于 LLVM 4.0），但其设计理念被大量分支和商业产品继承和扩展。了解主流变体的差异有助于在逆向分析中快速识别目标所用的混淆方案，并选择对应的反混淆策略。

### 主流 OLLVM 变体对比

| 变体 | 基于 LLVM 版本 | 特色功能 | 常见于 |
|------|---------------|---------|--------|
| **原版 OLLVM** | LLVM 4.0 | FLA + BCF + SUB 三件套 | 早期项目、学术研究 |
| **Hikari (孤挺花)** | LLVM 8-15 | 嵌套分发器、反类 dump、函数包装 | 国内 App、游戏保护 |
| **Armariris (战斧)** | LLVM 12+ | MBA 表达式、增强字符串加密 | 安全 SDK、金融安全 |
| **Pluto-Obfuscator** | LLVM 12-16 | 全局变量混淆、Trap 混淆、间接跳转 | 开源项目、CTF |
| **Obfuscator-LLVM (goron)** | LLVM 10+ | 增强 FLA + 间接分支 | 金融 App、支付 SDK |

### Hikari (孤挺花)

Hikari 是目前国内 App 中使用最广泛的 OLLVM 变体之一，由 Zhang (Naville) 开发。它在原版 OLLVM 的基础上增加了多项高级混淆 Pass：

**核心特性：**

- **嵌套分发器 (Nested Dispatchers)**: 不同于原版 OLLVM 的单层 `switch`，Hikari 使用外层 switch + 内层 switch 的双层分发结构，极大增加了符号执行恢复控制流的难度
- **AntiClassDump**: 针对 Objective-C（iOS 端为主），通过修改运行时元数据来对抗 class-dump 类的工具
- **FunctionWrapper**: 将直接函数调用包装成通过跳板函数 (trampoline) 的间接调用，进一步切断调用图
- **IndirectBranch**: 将条件分支转为基于寄存器的间接跳转

**识别方法：**

```
// Hikari 嵌套分发器的反编译特征：
while (1) {
    switch (state_var_outer) {
        case 0x1A3B:
            switch (state_var_inner) {   // ← 嵌套 switch，这是 Hikari 的标志
                case 0x7F2C:
                    // 真实代码块
                    state_var_inner = 0x3D1E;
                    break;
                case 0x3D1E:
                    // 另一个真实代码块
                    break;
            }
            state_var_outer = 0x5C4D;
            break;
        case 0x5C4D:
            // ...
            break;
    }
}
```

**反混淆要点：**

- 符号执行需要同时追踪外层和内层状态变量
- 建议先使用 Frida Stalker 获取运行时 trace，再辅助静态分析
- deflat 工具默认不支持嵌套分发器，需要修改其分发器识别逻辑

### Armariris (战斧)

Armariris 是由国内安全团队维护的 OLLVM 分支，特别增强了数学运算混淆能力：

**核心特性：**

- **MBA 增强**: 不仅替换基本算术，还会对比较运算进行 MBA 化，如将 `a == b` 变为 `(a ^ b) == 0`
- **增强字符串加密**: 使用多轮加密而非简单 XOR，支持 AES/ChaCha20 等算法
- **控制流伪造**: 在 BCF 基础上增加更多数学恒等式类型的不透明谓词

**识别方法：**

- 大量 AND、OR、XOR 混合的算术表达式（MBA 特征）
- 字符串解密函数比标准 XOR 循环更复杂（多轮、多密钥）
- 不透明谓词使用高级数学恒等式而非简单的 `x*x % 2` 模式

### Pluto-Obfuscator

Pluto-Obfuscator 是一个功能丰富的开源 OLLVM 变体，专门设计了对抗自动化分析工具的功能：

**核心特性：**

- **GlobalEncryption**: 对全局变量进行加密，在 `__attribute__((constructor))` 标记的函数中解密，类似字符串加密但范围扩展到所有全局数据
- **TrapAngr**: 专门设计用于对抗 Angr 符号执行引擎的 Pass。插入特定的代码模式，使 Angr 在分析时陷入死循环或路径爆炸
- **IndirectBranch**: 将直接分支转换为基于寄存器的间接跳转，破坏静态 CFG 构建
- **Flattening 增强**: 在原版 FLA 基础上增加更多随机性和干扰块

**识别方法：**

```
// Pluto-Obfuscator 的 IndirectBranch 特征：
// 大量使用 BLR/BR 配合从内存加载的地址
ADRP    X16, #jump_table@PAGE
ADD     X16, X16, #jump_table@PAGEOFF
LDRSW   X17, [X16, X8, LSL #2]   // 从跳转表加载偏移
ADD     X16, X16, X17             // 计算目标地址
BR      X16                       // 间接跳转

// IDA 反编译中表现为大量的函数指针调用:
((void (*)(void))(base + offset_table[state]))();
```

**反混淆要点：**

- TrapAngr 会导致 Angr 超时或崩溃，需要在符号执行前识别并 patch 掉这些代码
- GlobalEncryption 可通过 Hook `constructor` 函数来获取解密后的全局变量值
- IndirectBranch 需要动态追踪获取实际跳转目标

### Obfuscator-LLVM (goron)

goron 是另一个活跃的 OLLVM 分支，侧重于增强控制流混淆的强度：

**核心特性：**

- **增强 FLA**: 使用更复杂的状态变量更新算法，包括哈希函数和多变量联合控制
- **间接分支增强**: 在 IndirectBranch 基础上加入运行时地址计算
- **代码布局随机化**: 每次编译生成不同的基本块布局

**识别方法：**

- 状态变量的更新使用乘法、异或等复杂运算（而非简单赋值）
- 同一函数多次编译产生不同的混淆结果
- 在金融类 App 的支付和验证模块中较常见

---

## Android 版本差异对 OLLVM 分析的影响

不同的 Android 版本、NDK 版本和系统安全特性会直接影响 OLLVM 混淆代码的分析方式。了解这些差异有助于选择正确的工具配置和绕过方案。

### NDK 与编译工具链演进

| NDK 版本 | 关键变化 | 对 OLLVM 的影响 |
|----------|---------|-----------------|
| **r17+** | 默认使用 Clang 编译器 | OLLVM 可直接作为 Clang 插件集成，混淆普及的起点 |
| **r21+** | 移除 GCC，全面转向 Clang；默认 ARM64 | 几乎所有新项目都使用 Clang，OLLVM 变体兼容性好 |
| **r23+** | LLD 成为默认链接器 | SO 段布局变化，影响节偏移计算和某些 patch 方案 |
| **r25+** | 基于 LLVM 15 | 新版 OLLVM 变体（如 Pluto-Obfuscator）与此版本对齐 |
| **r26+** | 基于 LLVM 17 | 部分旧版 OLLVM Pass 不再兼容，需要适配新的 LLVM API |

### Android 版本对分析的影响

| Android 版本 | 关键变化 | 对 OLLVM 分析的影响 |
|-------------|---------|-------------------|
| **7.0 (N)** | Linker namespace 隔离 | SO 加载顺序改变，Frida 注入需适配 namespace；`dlopen` 行为变化影响 Hook 时机 |
| **8.0 (O)** | Treble 架构引入 | vendor SO 与 system SO 严格分离，分析需注意 SO 来源和依赖 |
| **9.0 (P)** | 非 SDK API 限制 | 反射调用 hidden API 受限，影响部分 Frida/Xposed Hook 方案 |
| **10 (Q)** | Execute-Only Memory (XOM) | `.text` 段不可读，影响 dump 和内存扫描；Frida Stalker 不受影响 |
| **12 (S)** | ART 优化改进 | JNI 调用路径更复杂，追踪 Java → Native 调用链需更多 Hook 点 |
| **14 (U)** | 16KB 页面支持 | SO 段对齐从 4KB 变为 16KB，偏移计算和 patch 方案需适配 |
| **15 (V)** | MTE (Memory Tagging Extension) | 指针带标签，影响内存分析和指针追踪；需要清除标签才能使用裸指针 |

### XOM (Execute-Only Memory) 对 OLLVM 分析的实际影响

Android 10 引入的 XOM 使得 `.text` 段只可执行不可读。这直接影响了依赖内存读取的分析方案：

**受影响的操作：**

- 直接使用 `Memory.readByteArray` 读取 `.text` 段内容可能失败
- 内存扫描 (`Memory.scan`) 无法扫描代码段
- dump 整个 SO 文件到磁盘时代码段为空

**不受影响的操作：**

- Frida Stalker 正常工作（通过 ptrace 机制绕过）
- 断点和 Hook 正常工作
- 单步调试正常工作

```python
# Android 10+ XOM 环境下通过 Frida 读取代码段
# 标准 Memory.readByteArray 可能因 XOM 失败
# 使用以下策略绕过

def read_code_with_frida(base_offset, size):
    """
    通过 Frida 的 ptrace 能力绕过 XOM 读取代码
    XOM 仅阻止进程自身的 load 指令读取，
    但 Frida 通过 ptrace 附加的方式可以绕过此限制
    """
    script_code = """
    'use strict';
    
    var soName = 'libtarget.so';
    var mod = Process.findModuleByName(soName);
    
    if (mod === null) {
        send({error: 'Module not found'});
    } else {
        try {
            // 方法1: 直接读取（在部分设备上 Frida 可以绕过 XOM）
            var code = Memory.readByteArray(mod.base.add(%d), %d);
            send({type: 'code', data: code});
        } catch (e) {
            // 方法2: 如果直接读取失败，使用 mprotect 修改权限
            try {
                Memory.protect(mod.base.add(%d), %d, 'rwx');
                var code = Memory.readByteArray(mod.base.add(%d), %d);
                send({type: 'code', data: code});
            } catch (e2) {
                send({error: 'Cannot read code: ' + e2.message});
            }
        }
    }
    """ % (base_offset, size, base_offset, size, base_offset, size)
    
    return script_code
```

**Frida 脚本 - XOM 检测与自适应读取：**

```javascript
// 自动检测 XOM 并选择合适的读取策略
function adaptiveCodeRead(soName, offset, size) {
    var mod = Process.findModuleByName(soName);
    if (!mod) { return null; }
    
    var addr = mod.base.add(offset);
    
    // 尝试读取 - 检测是否有 XOM
    try {
        var data = Memory.readByteArray(addr, Math.min(size, 16));
        // 成功，没有 XOM 或 Frida 已绕过
        console.log("[*] Direct read succeeded (no XOM or bypassed)");
        return Memory.readByteArray(addr, size);
    } catch (e) {
        console.log("[!] XOM detected: " + e.message);
        
        // 方案 A: 尝试修改内存保护属性
        try {
            Memory.protect(addr, size, 'rwx');
            console.log("[*] Memory protection changed to rwx");
            return Memory.readByteArray(addr, size);
        } catch (e2) {
            console.log("[!] mprotect failed: " + e2.message);
        }
        
        // 方案 B: 从 /proc/self/mem 读取
        try {
            var fd = new File("/proc/self/mem", "rb");
            fd.seek(addr.toInt32());
            var data = fd.readBytes(size);
            fd.close();
            console.log("[*] Read via /proc/self/mem succeeded");
            return data;
        } catch (e3) {
            console.log("[!] /proc/self/mem read failed: " + e3.message);
        }
        
        // 方案 C: 从磁盘文件读取（不受 XOM 影响）
        console.log("[*] Falling back to disk read");
        return readFromDisk(mod.path, offset, size);
    }
}

function readFromDisk(path, offset, size) {
    var fd = new File(path, "rb");
    fd.seek(offset);
    var data = fd.readBytes(size);
    fd.close();
    return data;
}
```

### 16KB 页面对齐 (Android 15+)

Android 15 引入了对 16KB 内存页面的支持（传统 ARM64 使用 4KB 页面）。这一变化对 SO 文件的分析产生以下影响：

**段对齐变化：**

```
// 4KB 页面 (传统) - SO 文件段对齐
LOAD  offset=0x000000  vaddr=0x000000  align=0x1000  (4KB)
LOAD  offset=0x001000  vaddr=0x001000  align=0x1000  (4KB)

// 16KB 页面 (Android 15+) - SO 文件段对齐
LOAD  offset=0x000000  vaddr=0x000000  align=0x4000  (16KB)
LOAD  offset=0x004000  vaddr=0x004000  align=0x4000  (16KB)
```

**对分析的实际影响：**

- **偏移计算**: 从 ELF 文件偏移到内存地址的映射关系变化，使用 `readelf -l` 确认段布局
- **Patch 方案**: 修改 SO 文件后需要保持 16KB 对齐，否则在 Android 15+ 设备上加载失败
- **内存搜索**: 段之间的填充区域增大（从最多 4KB 到最多 16KB），内存扫描范围需要调整
- **工具兼容性**: 旧版分析工具可能假设 4KB 对齐，需要更新或配置

**检测设备页面大小：**

```bash
# 在 ADB shell 中检测页面大小
adb shell getconf PAGE_SIZE
# 输出 4096 (4KB) 或 16384 (16KB)
```

---

## 分析与反混淆策略

> [!question] 思考：静态分析 vs 动态分析，哪个更有效？
> 面对 OLLVM 混淆，有两种完全不同的思路：
>
> **静态分析**：
>
> - ✅ 优势：能看到所有可能的执行路径，包括错误处理分支
> - ❌ 劣势：需要对抗大量的虚假分支，分析工作量巨大
> - 适用场景：你需要理解完整的算法逻辑，或者寻找漏洞
>
> **动态分析**：
>
> - ✅ 优势：直接记录真实执行路径，绕过所有虚假分支
> - ❌ 劣势：只能看到当前输入下的执行路径，可能遗漏关键分支
> - 适用场景：你只想提取算法结果（如加密签名），不关心内部逻辑
>
> **实战建议**：
>
> 1. 先用动态分析（Frida Stalker / Unidbg trace）快速获取"真实"的执行流
> 2. 再用静态分析验证和补充动态分析遗漏的部分
> 3. 如果目标是自动化（如算法还原），考虑符号执行（Angr）


### 1. 静态分析

- **CFG 重建**: 对于控制流平坦化，关键是识别状态变量和分发器。通过符号执行或模式匹配分发器逻辑，可以确定每个真实基本块的后继，从而重建原始图。

- **不透明谓词求解**: Z3 或其他 SMT 求解器等工具可用于自动证明虚假控制流中的条件是不变的。这使得分析师能够识别并移除无效的代码路径。

- **模式匹配**: 对于指令替换，可以识别并替换简单的模式。例如，像 `x = rdtsc(); y = x & 1; if (y == 0) ...` 这样的序列是一个常见的虚假谓词。

### 2. 动态分析

- **使用 Frida/Unidbg 进行追踪**: 动态追踪非常有效。通过使用 Frida 的 `Stalker` 或 Unidbg 的追踪功能，可以记录运行时执行的基本块的确切顺序。这可以绕过所有的控制流混淆，为你提供"真实"的执行路径。

- **符号执行**: 像 Angr 这样的引擎可用于探索程序状态。符号执行可以自动求解路径约束，从而有效地反混淆控制流并简化不透明谓词。这个过程可能很慢，但功能非常强大。

### 3. 自动化工具

- **d-obfuscator**: 一个基于 Python 的工具，使用符号执行（通过 Angr）来反混淆 OLLVM。

- **QB-Di**: 一个基于 QBDI 动态插桩框架的交互式反混淆工具。

- **Triton**: 一个动态二进制分析框架，可以通过编写脚本来执行污点分析和符号执行。

---

## 实战：使用符号执行与约束求解

> **💡 思路一句话**: 不透明谓词用 Z3 证明恒真/恒假 → 控制流平坦化用 Angr 符号执行恢复真实 CFG → 两者结合实现自动化反混淆。这一节从工具安装到实际调用，手把手演示每个步骤。

> **环境准备** (5 分钟搞定):
> ```bash
> # 创建虚拟环境，避免依赖冲突
> python3 -m venv ollvm_env && source ollvm_env/bin/activate
> pip install z3-solver angr capstone keystone-engine
> # 验证安装
> python -c "from z3 import *; print('Z3 OK:', get_version_string())"
> python -c "import angr; print('angr OK:', angr.__version__)"
> ```

### Z3-Solver：不透明谓词求解

Z3 是微软开发的高性能 SMT (Satisfiability Modulo Theories) 求解器，非常适合用于分析 OLLVM 的虚假控制流。

#### 安装

```bash
pip install z3-solver
```

#### 示例 1：识别恒真/恒假条件

OLLVM 的虚假控制流 (BCF) 经常使用不透明谓词，例如：

```c
// 混淆后的代码
int x = get_input();
int y = x * x;
if ((y % 2) == 1) {  // 平方数永远不可能是奇数（对于整数）
    // 这个分支永远不会执行（死代码）
    fake_path();
} else {
    real_path();
}
```

使用 Z3 证明这个条件恒假：

```python
from z3 import *

def prove_opaque_predicate():
    """证明 x*x % 2 == 1 对于任意整数 x 都是假的"""
    x = BitVec('x', 32)  # 32位整数
    y = x * x            # y = x^2

    # 创建求解器
    solver = Solver()

    # 尝试找到使 y % 2 == 1 成立的 x
    solver.add(URem(y, 2) == 1)

    result = solver.check()
    if result == unsat:
        print("[+] 证明成功：条件 (x*x % 2 == 1) 恒假")
        print("    这是一个不透明谓词，对应的分支是死代码")
    elif result == sat:
        print("[-] 找到反例:", solver.model())
    else:
        print("[?] 无法确定")

prove_opaque_predicate()
```

#### 示例 2：求解复杂的不透明谓词

OLLVM 常用的另一种不透明谓词基于数学恒等式：

```python
from z3 import *

def analyze_complex_predicate():
    """
    分析复杂的不透明谓词：
    (x * (x + 1)) % 2 == 0  恒真（连续两个整数的乘积必为偶数）
    """
    x = BitVec('x', 32)

    # 表达式：x * (x + 1)
    expr = x * (x + 1)

    solver = Solver()
    # 尝试找到使 expr % 2 != 0 的情况
    solver.add(URem(expr, 2) != 0)

    if solver.check() == unsat:
        print("[+] 证明：(x * (x + 1)) % 2 == 0 恒真")
        print("    这个 if 分支总是会执行")
    else:
        print("[-] 找到反例:", solver.model())

def analyze_bcf_condition():
    """
    分析 OLLVM BCF 生成的典型条件：
    ((x & 0xFFFFFFFE) * (x | 1)) % 2 == 0
    """
    x = BitVec('x', 32)

    # OLLVM BCF 典型模式
    a = x & 0xFFFFFFFE  # 清除最低位，保证是偶数
    b = x | 1           # 设置最低位，保证是奇数
    product = a * b     # 偶数 * 奇数 = 偶数

    solver = Solver()
    solver.add(URem(product, 2) != 0)

    if solver.check() == unsat:
        print("[+] BCF 条件恒真：可以安全移除 else 分支")
    else:
        print("[-] 条件不恒定")

analyze_complex_predicate()
analyze_bcf_condition()
```

#### 示例 3：批量分析多个谓词

```python
from z3 import *

class OpaquePredicateAnalyzer:
    """批量分析 OLLVM 不透明谓词"""

    # 常见的 OLLVM 不透明谓词模式
    PATTERNS = {
        "square_mod_2": lambda x: URem(x * x, 2) == 1,           # 恒假
        "consecutive_product": lambda x: URem(x * (x + 1), 2) != 0,  # 恒假
        "cubic_identity": lambda x: URem(x * x * x - x, 6) != 0,     # 恒假 (n³-n 能被6整除)
    }

    def __init__(self, bits=32):
        self.bits = bits

    def analyze_all(self):
        """分析所有已知的不透明谓词模式"""
        x = BitVec('x', self.bits)

        print("=" * 60)
        print("OLLVM 不透明谓词分析报告")
        print("=" * 60)

        for name, predicate in self.PATTERNS.items():
            solver = Solver()
            solver.add(predicate(x))

            result = solver.check()
            status = "恒假 (死代码)" if result == unsat else "可能为真"
            print(f"\n[{name}]")
            print(f"  结果: {status}")

            if result == sat:
                print(f"  反例: x = {solver.model()[x]}")

    def analyze_custom(self, condition_func, name="custom"):
        """分析自定义条件"""
        x = BitVec('x', self.bits)
        solver = Solver()
        solver.add(condition_func(x))

        result = solver.check()
        if result == unsat:
            return f"{name}: 恒假"
        elif result == sat:
            return f"{name}: 可满足, 反例 x={solver.model()[x]}"
        else:
            return f"{name}: 未知"

# 使用示例
analyzer = OpaquePredicateAnalyzer()
analyzer.analyze_all()
```

---

### Angr：符号执行与控制流恢复

Angr 是一个强大的二进制分析框架，特别适合处理 OLLVM 的控制流平坦化。

#### 安装

```bash
pip install angr
```

#### 示例 1：基础符号执行 - 绕过简单混淆

```python
import angr
import claripy

def simple_symbolic_execution(binary_path, target_addr, avoid_addrs=None):
    """
    使用符号执行找到到达目标地址的输入

    Args:
        binary_path: SO 文件路径
        target_addr: 目标地址（如解密函数返回点）
        avoid_addrs: 需要避开的地址列表（如错误处理分支）
    """
    # 加载二进制文件
    proj = angr.Project(binary_path, auto_load_libs=False)

    # 创建符号化的输入（假设输入是一个 32 字节的 buffer）
    sym_input = claripy.BVS('input', 32 * 8)

    # 创建初始状态
    state = proj.factory.entry_state(
        args=[binary_path],
        stdin=angr.SimFile('/dev/stdin', content=sym_input)
    )

    # 创建模拟管理器
    simgr = proj.factory.simulation_manager(state)

    # 探索到目标地址
    simgr.explore(find=target_addr, avoid=avoid_addrs or [])

    if simgr.found:
        found_state = simgr.found[0]
        # 获取满足条件的具体输入
        solution = found_state.solver.eval(sym_input, cast_to=bytes)
        print(f"[+] 找到有效输入: {solution.hex()}")
        return solution
    else:
        print("[-] 未找到有效路径")
        return None
```

#### 示例 2：Hook 混淆函数，加速分析

```python
import angr
import claripy

class OLLVMDeobfuscator:
    """OLLVM 反混淆器 - 使用 Angr 符号执行"""

    def __init__(self, binary_path, base_addr=0x0):
        self.proj = angr.Project(
            binary_path,
            main_opts={'base_addr': base_addr},
            auto_load_libs=False
        )
        self.cfg = None

    def build_cfg(self):
        """构建控制流图（用于分析混淆结构）"""
        print("[*] 正在构建 CFG...")
        self.cfg = self.proj.analyses.CFGFast()
        print(f"[+] CFG 构建完成: {len(self.cfg.graph.nodes())} 个节点")
        return self.cfg

    def find_dispatcher(self, func_addr):
        """
        识别控制流平坦化的分发器
        特征：大量的 case 分支，状态变量比较
        """
        func = self.cfg.functions.get(func_addr)
        if not func:
            return None

        # 找到入度最高的基本块（通常是分发器）
        max_in_degree = 0
        dispatcher = None

        for block in func.blocks:
            in_degree = len(list(self.cfg.graph.predecessors(block)))
            if in_degree > max_in_degree:
                max_in_degree = in_degree
                dispatcher = block

        if dispatcher and max_in_degree > 5:
            print(f"[+] 疑似分发器: 0x{dispatcher.addr:x} (入度: {max_in_degree})")
            return dispatcher
        return None

    def trace_execution(self, start_addr, input_data, max_steps=10000):
        """
        符号执行追踪，记录真实执行的基本块
        """
        state = self.proj.factory.blank_state(addr=start_addr)

        # 设置符号化输入
        sym_input = claripy.BVS('input', len(input_data) * 8)
        state.memory.store(state.regs.rdi, sym_input)  # 假设第一个参数是输入

        # 记录执行的基本块
        executed_blocks = []

        def block_hook(state):
            executed_blocks.append(state.addr)

        # 设置 Hook
        self.proj.hook(start_addr, block_hook, length=0)

        simgr = self.proj.factory.simulation_manager(state)
        simgr.run(n=max_steps)

        return executed_blocks

    def symbolic_execution_with_constraints(self, func_addr, target_output):
        """
        通过约束求解，找到产生特定输出的输入
        适用于分析加密/签名算法
        """
        state = self.proj.factory.call_state(func_addr)

        # 创建符号化参数
        sym_arg1 = claripy.BVS('arg1', 64)
        sym_arg2 = claripy.BVS('arg2', 64)

        # 设置函数参数 (x86_64 调用约定)
        state.regs.rdi = sym_arg1
        state.regs.rsi = sym_arg2

        simgr = self.proj.factory.simulation_manager(state)

        # 探索所有路径
        simgr.run()

        # 在结束状态中查找满足输出约束的
        for deadended in simgr.deadended:
            # 假设返回值在 rax
            deadended.solver.add(deadended.regs.rax == target_output)

            if deadended.solver.satisfiable():
                arg1_val = deadended.solver.eval(sym_arg1)
                arg2_val = deadended.solver.eval(sym_arg2)
                print(f"[+] 找到输入: arg1=0x{arg1_val:x}, arg2=0x{arg2_val:x}")
                return (arg1_val, arg2_val)

        return None

# 使用示例
def example_usage():
    # 加载混淆的 SO 文件
    deobf = OLLVMDeobfuscator("libencrypt.so", base_addr=0x10000)

    # 构建 CFG
    deobf.build_cfg()

    # 查找分发器
    dispatcher = deobf.find_dispatcher(0x12340)

    # 符号执行找到产生特定签名的输入
    result = deobf.symbolic_execution_with_constraints(
        func_addr=0x12340,
        target_output=0xDEADBEEF
    )
```

#### 示例 3：控制流平坦化恢复

```python
import angr
from angr.analyses.decompiler.condition_processor import ConditionProcessor

class CFGRecovery:
    """恢复被 OLLVM 平坦化的控制流"""

    def __init__(self, proj, func_addr):
        self.proj = proj
        self.func_addr = func_addr
        self.state_var = None
        self.real_blocks = {}  # state_value -> block_addr
        self.transitions = {}  # (from_state, to_state)

    def identify_state_variable(self, dispatcher_addr):
        """
        识别控制流平坦化的状态变量
        状态变量特征：
        1. 在分发器开头被加载
        2. 用于 switch-case 比较
        3. 在每个真实块末尾被更新
        """
        block = self.proj.factory.block(dispatcher_addr)

        # 分析 VEX IR 找到状态变量
        for stmt in block.vex.statements:
            # 查找从内存加载的操作
            if hasattr(stmt, 'data') and hasattr(stmt.data, 'tag'):
                if stmt.data.tag == 'Iex_Load':
                    # 这可能是状态变量
                    print(f"[*] 疑似状态变量加载: {stmt}")

        return self.state_var

    def extract_real_blocks(self, cfg):
        """
        从平坦化的 CFG 中提取真实的基本块
        真实块特征：
        1. 不是分发器
        2. 会修改状态变量
        3. 跳转回分发器
        """
        func = cfg.functions.get(self.func_addr)
        real_blocks = []

        for block in func.blocks:
            # 检查是否跳回分发器（平坦化的特征）
            successors = list(cfg.graph.successors(block))

            # 分析块中的状态变量修改
            # 这里需要更详细的数据流分析

            real_blocks.append(block)

        return real_blocks

    def recover_transitions(self, blocks):
        """
        恢复真实块之间的转换关系
        通过符号执行确定每个块的后继
        """
        transitions = []

        for block in blocks:
            state = self.proj.factory.blank_state(addr=block.addr)

            # 符号执行这个块
            simgr = self.proj.factory.simulation_manager(state)
            simgr.step()

            # 分析状态变量的新值来确定后继
            for succ_state in simgr.active:
                # 读取状态变量的值
                # new_state = succ_state.memory.load(state_var_addr, 4)
                pass

        return transitions

    def rebuild_cfg(self):
        """
        重建原始的控制流图
        """
        # 1. 识别状态变量
        # 2. 提取真实块
        # 3. 恢复转换关系
        # 4. 构建新的 CFG
        pass

def deflat_function(binary_path, func_addr):
    """
    反平坦化函数的完整流程
    """
    proj = angr.Project(binary_path, auto_load_libs=False)

    print(f"[*] 分析函数 @ 0x{func_addr:x}")

    # 构建 CFG
    cfg = proj.analyses.CFGFast()

    # 创建恢复器
    recovery = CFGRecovery(proj, func_addr)

    # 提取真实块
    real_blocks = recovery.extract_real_blocks(cfg)
    print(f"[+] 识别到 {len(real_blocks)} 个真实基本块")

    # 恢复转换
    transitions = recovery.recover_transitions(real_blocks)

    # 重建 CFG
    recovery.rebuild_cfg()

    return recovery
```

---

### 实战案例：分析混淆的签名函数

> **💡 思路一句话**: 先用 Frida hook 收集多组「输入→输出」样本 → 用 Z3 约束求解猜测算法结构（是否为线性变换）→ 猜不出则用 Angr 符号执行完整追踪 → 最后生成等价 Python 代码并验证。

> **适用场景**: 你已经找到了签名函数的地址，但反编译结果被 OLLVM 混淆得面目全非，无法直接阅读。
>
> **前提条件**:
> - 已通过 Frida/Xposed 定位到 native 签名函数地址
> - 能够触发签名函数被调用（比如发送网络请求）
> - 有 root 设备或模拟器

**操作流程概览**:
```text
Step 1: Frida hook 签名函数 → 收集 3+ 组 (输入, 输出) 样本
Step 2: Z3 约束求解 → 假设算法结构，尝试推断密钥
Step 3: 如果 Z3 失败 → Angr 符号执行，追踪完整计算过程
Step 4: 根据追踪结果 → 生成等价 Python 代码
Step 5: 用收集的样本验证 → 确认还原正确性
```

**Step 1: 用 Frida 收集输入输出样本**

```javascript
// collect_samples.js — 收集签名函数的输入输出
// 使用: frida -U -f com.example.app -l collect_samples.js --no-pause

Java.perform(function() {
    // 方法 1: Hook Java 层签名方法
    var SignHelper = Java.use("com.example.app.SignHelper");
    SignHelper.getSign.implementation = function(data) {
        var result = this.getSign(data);
        console.log(JSON.stringify({
            input: data,
            output: result,
            input_hex: stringToHex(data),
        }));
        return result;
    };
    
    // 方法 2: Hook Native 函数（如果已知偏移）
    var mod = Process.findModuleByName("libsign.so");
    if (mod) {
        // 假设函数接受 (char* data, int len) 返回 int
        Interceptor.attach(mod.base.add(0x1234), {
            onEnter: function(args) {
                this.input = args[0].readCString();
                this.len = args[1].toInt32();
            },
            onLeave: function(retval) {
                console.log("[SAMPLE] input=" + this.input + 
                           " len=" + this.len + 
                           " output=0x" + retval.toInt32().toString(16));
            }
        });
    }
});

function stringToHex(str) {
    var hex = '';
    for (var i = 0; i < str.length; i++) {
        hex += str.charCodeAt(i).toString(16).padStart(2, '0');
    }
    return hex;
}
```

```bash
# 运行收集脚本，然后在 App 中多次触发签名操作
frida -U -f com.example.app -l collect_samples.js --no-pause

# 预期输出 (收集至少 3 组):
# [SAMPLE] input=test1 len=5 output=0xAABBCCDD
# [SAMPLE] input=test2 len=5 output=0x11223344  
# [SAMPLE] input=a     len=1 output=0xDEADBEEF
```

> **小白提示**: 如何触发签名？大多数 App 在发送网络请求时会计算签名。打开 App → 刷新页面/搜索/登录 → 就会看到 Frida 打印的样本。多触发几次，尽量让输入不同。

以下是结合 Z3 和 Angr 分析的完整代码：

```python
import angr
import claripy
from z3 import *

class SignatureAnalyzer:
    """分析 OLLVM 混淆的签名算法"""

    def __init__(self, so_path, sign_func_offset):
        self.proj = angr.Project(so_path, auto_load_libs=False)
        self.sign_func = self.proj.loader.main_object.mapped_base + sign_func_offset

    def analyze_with_known_io(self, known_inputs, known_outputs):
        """
        使用已知的输入输出对来推断算法

        Args:
            known_inputs: 已知输入列表
            known_outputs: 对应的输出列表
        """
        # 使用 Z3 建立约束
        solver = Solver()

        # 假设签名算法是 output = (input * key1 + key2) ^ key3
        key1 = BitVec('key1', 32)
        key2 = BitVec('key2', 32)
        key3 = BitVec('key3', 32)

        for inp, out in zip(known_inputs, known_outputs):
            inp_bv = BitVecVal(inp, 32)
            out_bv = BitVecVal(out, 32)
            solver.add((inp_bv * key1 + key2) ^ key3 == out_bv)

        if solver.check() == sat:
            model = solver.model()
            print(f"[+] 推断出密钥:")
            print(f"    key1 = 0x{model[key1].as_long():08x}")
            print(f"    key2 = 0x{model[key2].as_long():08x}")
            print(f"    key3 = 0x{model[key3].as_long():08x}")
            return model
        else:
            print("[-] 无法推断算法")
            return None

    def symbolic_trace(self, input_value):
        """
        符号执行追踪签名函数
        """
        state = self.proj.factory.call_state(
            self.sign_func,
            input_value,  # 第一个参数
            0,            # 第二个参数（如长度）
        )

        # 记录所有的算术操作
        operations = []

        def track_operations(state):
            # 记录当前执行的指令
            block = state.block()
            for insn in block.capstone.insns:
                if insn.mnemonic in ['xor', 'add', 'sub', 'mul', 'shl', 'shr', 'and', 'or']:
                    operations.append({
                        'addr': insn.address,
                        'op': insn.mnemonic,
                        'operands': insn.op_str
                    })

        simgr = self.proj.factory.simulation_manager(state)

        # 逐步执行并记录
        while simgr.active:
            for s in simgr.active:
                track_operations(s)
            simgr.step()

        return operations

    def generate_equivalent_code(self, operations):
        """
        根据追踪结果生成等价的 Python 代码
        """
        code_lines = ["def sign(input_val):"]
        code_lines.append("    result = input_val")

        for op in operations:
            if op['op'] == 'xor':
                code_lines.append(f"    result ^= ...  # @ 0x{op['addr']:x}")
            elif op['op'] == 'add':
                code_lines.append(f"    result += ...  # @ 0x{op['addr']:x}")
            # ... 其他操作

        code_lines.append("    return result")
        return '\n'.join(code_lines)


# 实战使用示例
def real_world_example():
    """
    实战：分析某 App 的签名算法
    """
    # 1. 首先用 Frida 收集几组输入输出
    known_data = [
        (0x12345678, 0xAABBCCDD),
        (0x87654321, 0x11223344),
        (0x00000001, 0xDEADBEEF),
    ]

    # 2. 使用 Z3 推断可能的算法结构
    analyzer = SignatureAnalyzer("libsign.so", 0x1234)

    inputs = [d[0] for d in known_data]
    outputs = [d[1] for d in known_data]

    # 尝试推断密钥
    keys = analyzer.analyze_with_known_io(inputs, outputs)

    # 3. 如果简单推断失败，使用符号执行
    if not keys:
        print("[*] 切换到符号执行模式...")
        operations = analyzer.symbolic_trace(0x12345678)

        print("[+] 检测到的核心操作:")
        for op in operations:
            print(f"    0x{op['addr']:x}: {op['op']} {op['operands']}")

        # 生成等价代码
        code = analyzer.generate_equivalent_code(operations)
        print("\n[+] 等价 Python 代码:")
        print(code)

if __name__ == "__main__":
    real_world_example()
```

---

## 实战反混淆工具详解

本节详细介绍在 OLLVM 反混淆实战中最常用的工具及其使用方法，包括安装配置、核心原理和实际操作步骤。

### 1. d810 - IDA Pro OLLVM 反混淆插件

d810 是目前最成熟的 IDA Pro OLLVM 反混淆插件之一。它基于 IDA 的 Microcode API，在编译器中间表示 (microcode) 层面进行优化和简化，而非直接操作汇编代码。这使得它能够更准确地识别和消除混淆模式。

**安装步骤：**

```bash
# 克隆仓库
git clone https://github.com/joydo/d810

# 将 d810 目录复制到 IDA 插件目录
# macOS:  ~/Library/Application Support/Hex-Rays/IDA Pro/plugins/
# Linux:  ~/.idapro/plugins/
# Windows: %APPDATA%/Hex-Rays/IDA Pro/plugins/
cp -r d810 /path/to/ida/plugins/
```

**使用流程：**

1. 打开 IDA，加载目标 SO 文件
2. 在菜单中选择 `Edit → Plugins → D-810`
3. 在弹出的配置窗口中选择要启用的优化规则：
   - **MBA Simplification**: 简化混合布尔算术表达式
   - **Opaque Predicate Removal**: 移除不透明谓词（恒真/恒假条件）
   - **Dead Code Elimination**: 删除永远不会执行的代码路径
   - **Constant Folding**: 常量折叠优化
4. 选择目标函数，点击 `Start` 开始反混淆
5. 反混淆完成后重新查看反编译结果（按 `F5`）

**d810 架构原理：**

d810 工作在 IDA Microcode 的多个优化级别上。IDA 在反编译时会将汇编代码转换为一系列 microcode maturity level (从 MMAT_GENERATED 到 MMAT_LVARS)。d810 在适当的 maturity level 注册回调，在 microcode 被进一步优化前对其进行修改。

**编写自定义规则示例：**

```python
# d810 自定义规则: 简化 MBA 模式 (a & b) + (a | b) => a + b
# 文件位置: d810/optimizers/custom_mba.py

from d810.optimizers.flow import MicroCodeOptimizer
from d810.tracker import MicroCodeTracker
import ida_hexrays as hr

class CustomMBASimplifier(MicroCodeOptimizer):
    """
    自定义 MBA 简化规则
    匹配模式: (x & y) + (x | y)
    替换为:   x + y
    """
    
    OPTIMIZER_NAME = "Custom MBA: (x&y)+(x|y) => x+y"
    
    def check_candidate(self, blk, ins):
        """检查当前指令是否匹配 MBA 模式"""
        
        # 匹配 ADD 指令
        if ins.opcode != hr.m_add:
            return False
        
        left = ins.l   # 左操作数
        right = ins.r  # 右操作数
        
        # 检查左操作数是否为 AND 操作
        if not self._is_insn(left, hr.m_and):
            return False
        
        # 检查右操作数是否为 OR 操作
        if not self._is_insn(right, hr.m_or):
            return False
        
        # 获取 AND 和 OR 的操作数
        and_left, and_right = self._get_operands(left)
        or_left, or_right = self._get_operands(right)
        
        # 检查操作数是否相同 (x&y 和 x|y 中的 x,y 相同)
        if self._same_operands(and_left, or_left) and \
           self._same_operands(and_right, or_right):
            self.x = and_left
            self.y = and_right
            return True
        
        return False
    
    def apply_replacement(self, blk, ins):
        """将匹配的 MBA 模式替换为简化形式"""
        # 替换为 x + y
        ins.opcode = hr.m_add
        ins.l = self.x
        ins.r = self.y
        return True

# 更多自定义规则: (x ^ y) + 2*(x & y) => x + y
class CustomMBASimplifier2(MicroCodeOptimizer):
    OPTIMIZER_NAME = "Custom MBA: (x^y)+2*(x&y) => x+y"
    
    def check_candidate(self, blk, ins):
        if ins.opcode != hr.m_add:
            return False
        
        # 匹配 (x ^ y) + (x & y) << 1
        # 或 (x ^ y) + 2 * (x & y)
        # ... (匹配逻辑类似上述规则)
        return False
```

### 2. deflat - 控制流平坦化自动还原

deflat 是基于 Angr 符号执行框架的控制流平坦化自动还原工具。它能够识别 OLLVM 平坦化的分发器结构，通过符号执行确定每个真实基本块的后继关系，并输出还原后的二进制。

**安装步骤：**

```bash
# 克隆仓库
git clone https://github.com/cq674350529/deflat
cd deflat

# 安装依赖 (推荐使用虚拟环境)
python -m venv venv
source venv/bin/activate
pip install angr
```

**基本使用方法：**

```bash
# 反平坦化指定函数
# -f: 目标文件
# --addr: 目标函数的起始地址
python deflat.py -f libtarget.so --addr 0x1234

# 指定架构 (默认自动检测)
python deflat.py -f libtarget.so --addr 0x1234 --arch arm64
```

**工作原理：**

1. **识别分发器**: 分析函数 CFG，找到入度最高的基本块（即所有真实块都会跳转回的分发器块）
2. **识别状态变量**: 在分发器块中找到用于 switch-case 比较的变量
3. **提取真实块**: 将所有非分发器、非序言的基本块识别为真实基本块
4. **符号执行恢复转换**: 对每个真实块进行符号执行，观察其执行后状态变量的值，从而确定后继块
5. **重建 CFG**: 根据恢复的转换关系 patch 二进制，将跳转目标从分发器改为直接的后继块

**常见问题与解决方案：**

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| `Symbolic execution timeout` | 函数过大或有复杂循环 | 增加超时时间 `--timeout 600`；减小分析范围 |
| `Cannot identify dispatcher` | 分发器结构非标准（如 Hikari 嵌套） | 使用 `--dispatcher` 手动指定分发器地址 |
| `Path explosion` | 存在大量分支或循环 | 对已知的子函数设置 Hook 返回固定值 |
| `Unsupported architecture` | Angr 对特定架构支持不完整 | 确认 Angr 版本支持目标架构；考虑使用 Unicorn 替代 |
| `State variable not found` | 状态变量被进一步混淆 | 使用 `--state-var` 手动指定状态变量的地址或寄存器 |

### 3. IDA Microcode API 反混淆

直接使用 IDA 的 Microcode API 可以实现高度定制化的反混淆逻辑。相比 d810 这样的插件，直接使用 API 可以更灵活地处理特定的混淆模式。

**IDA Microcode 简介：**

IDA 在反编译（Hex-Rays）过程中会将汇编代码转换为多层 microcode 中间表示。每一层的表示逐渐接近高级语言，同时 IDA 会在各层进行不同的优化。我们可以在这些层注册自定义的优化回调来消除混淆。

**完整反混淆示例：**

```python
import ida_hexrays as hr
import ida_funcs
import idautils

class OLLVMDeobfuscator(hr.optinsn_t):
    """
    使用 IDA Microcode API 在编译器中间表示层面去混淆
    
    工作原理：
    1. 注册为 Hex-Rays 的 microcode 优化回调
    2. 在反编译过程中，遍历所有 microcode 指令
    3. 识别混淆模式并替换为简化形式
    """
    
    def __init__(self):
        super().__init__()
        self.changes = 0
    
    def func(self, blk, ins, optflags):
        """
        每条 microcode 指令都会触发此回调
        返回值: 1 = 有修改, 0 = 无修改
        """
        result = 0
        
        # 规则 1: MBA 简化 - (a & b) + (a | b) => a + b
        if self._simplify_mba_add(blk, ins):
            result = 1
        
        # 规则 2: 不透明谓词消除
        elif self._remove_opaque_predicate(blk, ins):
            result = 1
        
        # 规则 3: 常量折叠
        elif self._fold_constants(blk, ins):
            result = 1
        
        if result:
            self.changes += 1
        
        return result
    
    def _simplify_mba_add(self, blk, ins):
        """简化 MBA 加法模式"""
        if ins.opcode != hr.m_add:
            return False
        
        # 检查是否是 (x & y) + (x | y) 模式
        if ins.l.t != hr.mop_d or ins.r.t != hr.mop_d:
            return False
        
        left_ins = ins.l.d
        right_ins = ins.r.d
        
        if left_ins.opcode == hr.m_and and right_ins.opcode == hr.m_or:
            # 验证操作数匹配
            if (left_ins.l.equal_mops(right_ins.l, hr.EQ_IGNSIZE) and
                left_ins.r.equal_mops(right_ins.r, hr.EQ_IGNSIZE)):
                # 替换为 x + y
                ins.l.swap(left_ins.l)
                ins.r.swap(left_ins.r)
                return True
        
        return False
    
    def _remove_opaque_predicate(self, blk, ins):
        """
        消除不透明谓词
        检测恒真/恒假的条件跳转并简化
        """
        if ins.opcode != hr.m_jcnd:
            return False
        
        # 检查条件是否是已知的不透明谓词模式
        cond = ins.l
        if cond.t == hr.mop_d:
            cond_ins = cond.d
            
            # 模式: (x*x) % 2 == 1 → 恒假
            # 如果能证明条件恒假，则移除跳转
            # 模式: x*(x+1) % 2 == 0 → 恒真
            # 如果能证明条件恒真，则转为无条件跳转
            pass
        
        return False
    
    def _fold_constants(self, blk, ins):
        """常量折叠 - 将可在编译时计算的表达式替换为结果"""
        if ins.opcode in [hr.m_add, hr.m_sub, hr.m_xor, hr.m_and, hr.m_or]:
            if ins.l.t == hr.mop_n and ins.r.t == hr.mop_n:
                # 两个操作数都是常量，直接计算
                left_val = ins.l.nnn.value
                right_val = ins.r.nnn.value
                
                if ins.opcode == hr.m_add:
                    result = left_val + right_val
                elif ins.opcode == hr.m_sub:
                    result = left_val - right_val
                elif ins.opcode == hr.m_xor:
                    result = left_val ^ right_val
                elif ins.opcode == hr.m_and:
                    result = left_val & right_val
                elif ins.opcode == hr.m_or:
                    result = left_val | right_val
                
                # 将指令替换为 MOV 常量
                ins.opcode = hr.m_mov
                ins.l.make_number(result, ins.d.size)
                return True
        
        return False


def deobfuscate_function(func_addr):
    """反混淆指定函数"""
    
    # 安装优化器
    optimizer = OLLVMDeobfuscator()
    optimizer.install()
    
    try:
        # 强制重新反编译函数
        cfunc = hr.decompile(func_addr)
        
        if cfunc:
            print(f"[+] 反混淆完成，共应用 {optimizer.changes} 处优化")
            print(f"[+] 请查看反编译窗口 (F5) 获取优化结果")
        else:
            print("[-] 反编译失败")
    finally:
        # 卸载优化器
        optimizer.remove()


def batch_deobfuscate():
    """批量反混淆所有函数"""
    optimizer = OLLVMDeobfuscator()
    optimizer.install()
    
    total_changes = 0
    func_count = 0
    
    try:
        for func_addr in idautils.Functions():
            func = ida_funcs.get_func(func_addr)
            if func and func.size() > 50:  # 跳过太小的函数
                try:
                    cfunc = hr.decompile(func_addr)
                    if optimizer.changes > 0:
                        total_changes += optimizer.changes
                        func_count += 1
                        optimizer.changes = 0
                except:
                    pass
    finally:
        optimizer.remove()
    
    print(f"[+] 批量反混淆完成: {func_count} 个函数, "
          f"共 {total_changes} 处优化")
```

### 4. Frida Stalker 增强追踪

Frida Stalker 是动态分析 OLLVM 混淆代码最有效的工具之一。它通过代码插桩 (code instrumentation) 在运行时追踪每一条执行的指令或基本块，从而直接获取真实的执行路径，绕过所有虚假控制流。

以下是一个增强版的 Stalker 脚本，适配 Android 7-15 的各种差异：

```javascript
// 增强版 Stalker - 适配 Android 7-15
// 功能: 追踪混淆函数的真实执行路径，恢复控制流图

function getAndroidVersion() {
    try {
        var version = parseInt(Java.androidVersion);
        return isNaN(version) ? 0 : version;
    } catch (e) {
        return 0;
    }
}

function enhancedTrace(soName, funcOffset, options) {
    options = options || {};
    var maxBlocks = options.maxBlocks || 10000;
    var verbose = options.verbose || false;
    var outputCFG = options.outputCFG !== false;
    
    var mod = Process.findModuleByName(soName);
    if (!mod) {
        console.log("[-] Module not found: " + soName);
        return;
    }
    
    var androidVersion = getAndroidVersion();
    console.log("[*] Android version: " + androidVersion);
    console.log("[*] Module base: " + mod.base);
    console.log("[*] Target function: " + mod.base.add(funcOffset));
    
    // Android 10+ XOM 检测
    if (androidVersion >= 10) {
        console.log("[*] Android 10+ detected, code memory may be execute-only");
        console.log("[*] Using Stalker (not direct memory read) for analysis");
    }
    
    // Android 14+ 16KB 页面检测
    if (androidVersion >= 14) {
        console.log("[*] Android 14+ detected, checking page size...");
        // 16KB 页面可能影响模块段布局
    }
    
    var target = mod.base.add(funcOffset);
    var modBase = mod.base;
    var modSize = mod.size;
    
    // 数据收集结构
    var blocks = {};
    var transitions = [];
    var lastBlockOffset = null;
    var callTargets = {};
    var blockSequence = [];
    
    Interceptor.attach(target, {
        onEnter: function(args) {
            this.tid = Process.getCurrentThreadId();
            this.startTime = Date.now();
            
            // 保存函数参数用于分析
            this.args = [];
            for (var i = 0; i < 4; i++) {
                this.args.push(args[i]);
            }
            console.log("[+] Function entered, args: " + 
                        this.args.map(function(a) { return a; }).join(", "));
            
            // 重置追踪数据
            blocks = {};
            transitions = [];
            lastBlockOffset = null;
            blockSequence = [];
            callTargets = {};
            
            Stalker.follow(this.tid, {
                events: { call: true, ret: false, exec: false, block: false },
                
                transform: function(iterator) {
                    var inst = iterator.next();
                    var blockStart = inst.address;
                    var blockStartOffset = blockStart.sub(modBase).toInt32();
                    
                    // 只追踪目标模块内的代码
                    if (blockStart.compare(modBase) >= 0 && 
                        blockStart.compare(modBase.add(modSize)) < 0) {
                        
                        // 在块入口插入 callout
                        iterator.putCallout(function(ctx) {
                            var pc = ctx.pc;
                            var offset = pc.sub(modBase).toInt32();
                            
                            if (!blocks[offset]) {
                                blocks[offset] = { 
                                    count: 0, 
                                    firstSeen: blockSequence.length
                                };
                            }
                            blocks[offset].count++;
                            blockSequence.push(offset);
                            
                            // 记录块间转换
                            if (lastBlockOffset !== null && 
                                lastBlockOffset !== offset) {
                                transitions.push({
                                    from: lastBlockOffset, 
                                    to: offset
                                });
                            }
                            lastBlockOffset = offset;
                        });
                    }
                    
                    // 遍历块中所有指令
                    var instCount = 1;
                    do {
                        // 记录间接调用目标 (BLR)
                        if (inst.mnemonic === "blr") {
                            iterator.putCallout(function(ctx) {
                                var targetAddr = ctx[inst.operands[0].value];
                                var targetSym = DebugSymbol.fromAddress(targetAddr);
                                callTargets[inst.address.sub(modBase).toInt32()] = {
                                    target: targetAddr,
                                    symbol: targetSym.name || "unknown"
                                };
                                if (verbose) {
                                    console.log("  [BLR] " + inst.address + 
                                                " => " + targetAddr + 
                                                " (" + targetSym.name + ")");
                                }
                            });
                        }
                        
                        iterator.keep();
                        instCount++;
                    } while ((inst = iterator.next()) !== null);
                    
                    // 更新块大小信息
                    if (blockStart.compare(modBase) >= 0 && 
                        blockStart.compare(modBase.add(modSize)) < 0) {
                        if (blocks[blockStartOffset]) {
                            blocks[blockStartOffset].instCount = instCount;
                        }
                    }
                }
            });
        },
        
        onLeave: function(retval) {
            Stalker.unfollow(this.tid);
            Stalker.flush();
            
            var elapsed = Date.now() - this.startTime;
            
            console.log("\n" + "=".repeat(60));
            console.log("[+] Trace completed in " + elapsed + "ms");
            console.log("[+] Return value: " + retval);
            console.log("[+] Unique blocks: " + Object.keys(blocks).length);
            console.log("[+] Total transitions: " + transitions.length);
            console.log("[+] Block sequence length: " + blockSequence.length);
            console.log("[+] Indirect calls: " + Object.keys(callTargets).length);
            
            // 识别热点块 (可能是分发器)
            var sortedBlocks = Object.keys(blocks).sort(function(a, b) {
                return blocks[b].count - blocks[a].count;
            });
            
            console.log("\n[*] Top 10 most visited blocks (likely dispatchers):");
            for (var i = 0; i < Math.min(10, sortedBlocks.length); i++) {
                var offset = sortedBlocks[i];
                var info = blocks[offset];
                console.log("    0x" + parseInt(offset).toString(16) + 
                            " - visited " + info.count + " times" +
                            " (" + (info.instCount || "?") + " instructions)");
            }
            
            // 输出间接调用目标
            if (Object.keys(callTargets).length > 0) {
                console.log("\n[*] Resolved indirect calls:");
                for (var callOffset in callTargets) {
                    var info = callTargets[callOffset];
                    console.log("    0x" + parseInt(callOffset).toString(16) + 
                                " => " + info.target + " (" + info.symbol + ")");
                }
            }
            
            // 生成恢复的 CFG
            if (outputCFG) {
                var cfgData = {
                    type: "cfg",
                    module: soName,
                    funcOffset: funcOffset,
                    blocks: blocks,
                    transitions: transitions,
                    sequence: blockSequence,
                    callTargets: callTargets,
                    metadata: {
                        androidVersion: androidVersion,
                        elapsed: elapsed,
                        returnValue: retval.toString()
                    }
                };
                send(cfgData);
                console.log("\n[+] CFG data sent via send()");
                console.log("[+] Use the Python side to reconstruct the control flow graph");
            }
        }
    });
}

// 使用示例
// enhancedTrace("libtarget.so", 0x1234);
// enhancedTrace("libtarget.so", 0x1234, { verbose: true, maxBlocks: 5000 });
```

**Python 端 CFG 重建脚本：**

```python
import json
import sys

def reconstruct_cfg(trace_data):
    """
    根据 Frida Stalker 追踪数据重建控制流图
    """
    blocks = trace_data["blocks"]
    transitions = trace_data["transitions"]
    sequence = trace_data["sequence"]
    
    # 构建邻接表
    cfg = {}
    for trans in transitions:
        src = trans["from"]
        dst = trans["to"]
        if src not in cfg:
            cfg[src] = set()
        cfg[src].add(dst)
    
    # 找到入口块 (序列中的第一个块)
    entry = sequence[0] if sequence else None
    
    # 识别分发器 (被访问次数最多的块)
    sorted_blocks = sorted(blocks.items(), 
                          key=lambda x: x[1]["count"], 
                          reverse=True)
    
    # 过滤分发器块，只保留真实块
    dispatcher_threshold = len(sequence) * 0.1  # 访问次数超过 10% 的认为是分发器
    real_blocks = {k: v for k, v in blocks.items() 
                   if v["count"] < dispatcher_threshold}
    
    # 输出还原后的 CFG
    print(f"Entry block: 0x{entry:x}" if entry else "No entry")
    print(f"Total blocks: {len(blocks)}")
    print(f"Dispatcher candidates: {len(blocks) - len(real_blocks)}")
    print(f"Real blocks: {len(real_blocks)}")
    
    # 生成 dot 格式用于可视化
    dot_output = "digraph CFG {\n"
    dot_output += '    node [shape=box, style=filled, fillcolor=lightblue];\n'
    
    for src, dsts in cfg.items():
        for dst in dsts:
            dot_output += f'    "0x{src:x}" -> "0x{dst:x}";\n'
    
    dot_output += "}\n"
    
    with open("recovered_cfg.dot", "w") as f:
        f.write(dot_output)
    
    print("[+] CFG saved to recovered_cfg.dot")
    print("[+] Visualize with: dot -Tpng recovered_cfg.dot -o cfg.png")
    
    return cfg, real_blocks
```

---

## 工具对比与选择建议

| 工具 | 适用场景 | 优势 | 劣势 |
|------|----------|------|------|
| **Z3** | 不透明谓词求解、简单约束 | 速度快、精确 | 不能直接分析二进制 |
| **Angr** | 完整的符号执行、路径探索 | 功能全面、支持多架构 | 路径爆炸问题、较慢 |
| **Triton** | 动态符号执行、污点分析 | 精确追踪、与调试器集成好 | 需要运行环境 |
| **Miasm** | IR 分析、CFG 重建 | 轻量级、易于定制 | 文档较少 |

**实战建议**：

1. **快速分析**：先用 Frida Stalker 获取执行 trace，确定真实执行路径
2. **深度分析**：使用 Angr 进行符号执行，恢复完整算法
3. **精确求解**：使用 Z3 求解具体的约束条件和密钥
4. **组合使用**：Frida 获取运行时数据 → Z3 推断算法结构 → Angr 验证和补全
