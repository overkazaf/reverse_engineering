---
title: "ARM 汇编入门 (Android Native)"
date: 2024-07-22
type: posts
tags: ["Native层", "Ghidra", "Frida", "JNI", "加密分析", "基础知识"]
weight: 10
---

# ARM 汇编入门 (Android Native)

当应用的核心逻辑、加密算法或性能密集型任务用 C/C++ 编写时，它们会被编译成原生库 (`.so` 文件)。在 Android 上，这些库主要是 ARM 架构的。理解 ARM 汇编是分析 `.so` 文件的基础。本指南将介绍逆向工程师需要了解的 ARMv7 (32-bit) 和 ARMv8 (64-bit/A64) 的基础知识。

!!! question "思考：为什么必须学习汇编？"
当你遇到以下场景时，该如何应对？

- 用 Jadx 打开 APK，发现关键的加密逻辑都在 `native` 方法中
- Frida Hook 到了某个 JNI 函数，但参数是指针，不知道如何读取
- IDA 打开 `.so` 文件，满屏的汇编指令让你无从下手

## 这些场景的共同点是：**核心逻辑被编译成了机器码**。不理解汇编，就像试图在不懂外语的情况下阅读外文书籍——你只能靠猜。

## 目录

1. [**基本概念：ARM vs x86**](#基本概念arm-vs-x86)
2. [**ARM 与 ARM64 (AArch64) 架构**](#arm-与-arm64-aarch64-架构)
3. [**指令集详解**](#指令集详解)
4. [**函数调用约定 (AAPCS)**](#函数调用约定-aapcs)
5. [**常见模式识别**](#常见模式识别)
6. [**Thumb/Thumb-2 模式**](#thumbthumb-2-模式)
7. [**NEON/SIMD 基础**](#neonsimd-基础)
8. [**在 IDA/Ghidra 中阅读 ARM**](#在-idaghidra-中阅读-arm)

---

### 基本概念：ARM vs x86

- **RISC vs CISC**: ARM 是**精简指令集计算机 (RISC)**，指令长度固定，种类较少，操作简单。x86 是**复杂指令集计算机 (CISC)**。

- **Load/Store 架构**: ARM 是一种"加载/存储"架构。这意味着数据处理（如加法、减法）**只能在寄存器之间**进行。你必须先用加载指令 (`LDR`) 将内存中的数据加载到寄存器，计算完成后再用存储指令 (`STR`) 将结果存回内存。

- **指令模式**: ARMv7 (32-bit) 支持两种指令集：
- **ARM**: 32-bit 定长指令，功能强大。

- **Thumb**: 16-bit/32-bit 变长指令，代码密度更高，是移动设备上的主流。在 IDA 等工具中，你通常会分析 Thumb 模式下的代码。

---

### ARM 与 ARM64 (AArch64) 架构

在 Android 逆向中，你会同时遇到 32 位 (ARMv7/armeabi-v7a) 和 64 位 (ARMv8/arm64-v8a) 的 `.so` 文件。现代设备几乎都是 64 位，但很多应用为了兼容性仍然提供 32 位库。

#### ARM 32-bit (ARMv7) 寄存器模型

共有 16 个通用寄存器 (`R0` - `R15`)，加上一个当前程序状态寄存器 (CPSR)。

| 寄存器       | 别名        | 用途                                                                                |
| :----------- | :---------- | :---------------------------------------------------------------------------------- |
| `R0` - `R3`  | `A1` - `A4` | **参数寄存器** (Argument)。用于传递函数的前 4 个参数。`R0` 也用作**返回值寄存器**。 |
| `R4` - `R11` | `V1` - `V8` | **变量寄存器** (Variable)。被调用者保存，用于保存函数的局部变量。                   |
| `R12`        | `IP`        | 过程调用间临时寄存器 (Intra-Procedure call scratch register)。                      |
| `R13`        | `SP`        | **栈指针** (Stack Pointer)。指向栈顶，8 字节对齐。                                  |
| `R14`        | `LR`        | **链接寄存器** (Link Register)。存储函数调用的返回地址。                            |
| `R15`        | `PC`        | **程序计数器** (Program Counter)。指向当前正在执行的指令地址 +8 (ARM) 或 +4 (Thumb)。|

**CPSR (当前程序状态寄存器)**

CPSR 存储了条件标志位和处理器状态信息。条件分支指令正是根据 CPSR 中的标志位来决定是否跳转的。

| 标志位 | 名称     | 含义                                                          |
| :----- | :------- | :------------------------------------------------------------ |
| `N`    | Negative | 运算结果为负数时置 1                                          |
| `Z`    | Zero     | 运算结果为零时置 1                                            |
| `C`    | Carry    | 无符号运算产生进位/借位时置 1                                 |
| `V`    | Overflow | 有符号运算产生溢出时置 1                                      |
| `T`    | Thumb    | 处理器处于 Thumb 模式时置 1，ARM 模式时为 0                    |

!!! tip "快速定位关键寄存器"
在分析一个陌生函数时，如何快速抓住重点？

- **函数入口**：先看 `R0-R3` (32 位) 或 `X0-X7` (64 位)，这些是参数
- **函数返回**：关注 `R0/X0`，这是返回值存放的地方
- **函数调用**：`BL` 指令前后，检查参数寄存器的变化
- **栈操作**：`SP` 的变化反映了局部变量的分配

这种"重点优先"的阅读策略，能让你快速理解函数的输入输出，而不必逐行分析每条指令。

#### ARM 64-bit (AArch64) 寄存器模型

AArch64 有 31 个通用寄存器，设计比 ARM32 更加规整。

| 寄存器        | 64 位名 | 32 位名   | 用途                                                           |
| :------------ | :------ | :-------- | :------------------------------------------------------------- |
| 第 0-7 号     | `X0`-`X7`  | `W0`-`W7`  | **参数/返回值寄存器**。传递前 8 个参数，`X0` 也是返回值。      |
| 第 8 号       | `X8`    | `W8`      | 间接结果位置寄存器 (用于返回大结构体)。                        |
| 第 9-15 号    | `X9`-`X15` | `W9`-`W15` | **调用者保存的临时寄存器** (Caller-saved)。函数可自由修改。    |
| 第 16-17 号   | `X16`-`X17`| `W16`-`W17`| IP0/IP1，过程内调用临时寄存器（链接器使用）。                  |
| 第 18 号      | `X18`   | `W18`     | **平台寄存器**。Android 上被保留给 TLS (线程本地存储)。        |
| 第 19-28 号   | `X19`-`X28`| `W19`-`W28`| **被调用者保存的寄存器** (Callee-saved)。函数使用前必须保存。  |
| 第 29 号      | `X29`   | `W29`     | **帧指针 FP** (Frame Pointer)。                                |
| 第 30 号      | `X30`   | `W30`     | **链接寄存器 LR** (Link Register)。                            |
| —             | `SP`    | `WSP`     | **栈指针**。不是通用寄存器，有专门的编码。                     |
| —             | `XZR`   | `WZR`     | **零寄存器**。读取永远返回 0，写入被丢弃。                     |

**W 寄存器与 X 寄存器的关系**

`W` 寄存器是对应 `X` 寄存器的低 32 位视图。当你写入一个 `W` 寄存器时，高 32 位会被**自动清零**。

```armasm
; X0 = 0x00000001_FFFFFFFF
MOV W0, #0x42        ; X0 变为 0x00000000_00000042 (高32位被清零)
MOV X0, #0x42        ; X0 变为 0x00000000_00000042 (整个64位赋值)
```

**NZCV (AArch64 条件标志)**

AArch64 中条件标志存储在 NZCV 系统寄存器中，功能与 ARM32 的 CPSR 标志位相同：

```armasm
CMP X0, X1           ; 执行 X0 - X1，更新 NZCV 标志
B.EQ label           ; 如果 Z=1 (相等) 则跳转
B.NE label           ; 如果 Z=0 (不等) 则跳转
B.GT label           ; 如果有符号大于 则跳转
B.LT label           ; 如果有符号小于 则跳转
B.HI label           ; 如果无符号大于 则跳转
B.LO label           ; 如果无符号小于 则跳转 (等同于 B.CC)
```

**栈指针 (SP) 要求**

在 AArch64 中，栈指针必须**16 字节对齐**。这意味着 `SUB SP, SP, #N` 中的 N 必须是 16 的倍数，否则会触发对齐异常。这是初学者容易忽略的重要细节。

---

### 指令集详解

#### 数据处理指令

```armasm
; === 移动指令 ===
MOV  R1, R2           ; R1 = R2
MOV  X1, X2           ; X1 = X2 (AArch64)
MOV  R0, #0xFF        ; R0 = 255 (立即数)
MVN  R0, R1           ; R0 = ~R1 (按位取反)
MOVZ X0, #0x1234      ; X0 = 0x1234 (将16位立即数放入寄存器，其余位清零)
MOVK X0, #0x5678, LSL #16  ; 将 0x5678 放到 X0 的 [31:16] 位，保持其他位不变

; === 算术指令 ===
ADD  R0, R1, R2       ; R0 = R1 + R2
ADDS R0, R1, R2       ; R0 = R1 + R2，并更新 CPSR 标志位 (注意末尾的 S)
SUB  R0, R1, R2       ; R0 = R1 - R2
RSB  R0, R1, #0       ; R0 = 0 - R1 (反向减法，常用于取负数)
MUL  R0, R1, R2       ; R0 = R1 * R2
SDIV X0, X1, X2       ; X0 = X1 / X2 (有符号除法，AArch64)

; === 逻辑指令 ===
AND  R0, R1, #0xFF    ; R0 = R1 & 0xFF (按位与)
ORR  R0, R1, R2       ; R0 = R1 | R2  (按位或)
EOR  R0, R1, R2       ; R0 = R1 ^ R2  (按位异或)
BIC  R0, R1, R2       ; R0 = R1 & ~R2 (位清除)
TST  R0, #0x1         ; 测试 R0 的最低位 (AND 但不存储结果，只更新标志)

; === 移位指令 ===
LSL  R0, R1, #3       ; R0 = R1 << 3 (逻辑左移)
LSR  R0, R1, #3       ; R0 = R1 >> 3 (逻辑右移，高位补0)
ASR  R0, R1, #3       ; R0 = R1 >> 3 (算术右移，高位补符号位)
```

!!! note "ADDS vs ADD"
ARM 指令的一个重要特点：大多数数据处理指令默认**不更新**条件标志。只有在指令末尾加上 `S` 后缀（如 `ADDS`、`SUBS`），才会更新 CPSR/NZCV。而 `CMP` 和 `TST` 是特殊的——它们**总是**更新标志。在 AArch64 中这个规则同样适用。

#### 加载/存储指令

这是 ARM 的核心。所有内存访问都必须通过 LDR/STR 指令完成。

```armasm
; === 基本加载/存储 ===
LDR  R0, [R1]         ; R0 = *R1  (从 R1 指向的地址加载 4 字节)
STR  R0, [R1]         ; *R1 = R0  (将 R0 存储到 R1 指向的地址)

; === 不同大小的访问 ===
LDRB R0, [R1]         ; 加载 1 字节 (零扩展到 32 位)
LDRH R0, [R1]         ; 加载 2 字节 (半字, 零扩展)
LDRSB R0, [R1]        ; 加载 1 字节 (符号扩展到 32 位)
STRB R0, [R1]         ; 存储 R0 的最低 1 字节

; === 偏移寻址 ===
LDR  R0, [R1, #4]     ; R0 = *(R1 + 4)  (立即数偏移)
LDR  R0, [R1, R2]     ; R0 = *(R1 + R2)  (寄存器偏移)
LDR  R0, [R1, R2, LSL #2]  ; R0 = *(R1 + R2*4)  (带移位的寄存器偏移，常见于数组访问)

; === 前索引 (Pre-indexed) / 后索引 (Post-indexed) ===
LDR  R0, [R1, #4]!    ; R1 += 4; R0 = *R1  (先更新，再加载)
LDR  R0, [R1], #4     ; R0 = *R1; R1 += 4  (先加载，再更新)

; === AArch64 特有 ===
LDP  X0, X1, [SP]     ; 一次加载两个 64 位寄存器 (Load Pair)
STP  X0, X1, [SP, #-16]!  ; 一次存储两个寄存器，带前索引 (Store Pair)
LDUR X0, [X1, #-8]    ; 非对齐偏移加载 (Unscaled)
ADR  X0, label        ; 将 PC 相对地址加载到 X0
ADRP X0, page_label   ; 将 PC 相对页地址加载到 X0 (4KB 页粒度)
```

!!! tip "LDR 的 PC 相对寻址"
在反汇编中你会经常看到 `LDR R0, =0x12345678` 这种**伪指令**。汇编器实际上会将常量放在一个"文字池 (literal pool)"中，然后转换为 `LDR R0, [PC, #offset]`。在 IDA 中你可以看到这种转换后的形式。

#### 分支指令

```armasm
; === 无条件分支 ===
B    label            ; 跳转到 label
BL   label            ; 跳转到 label，同时 LR = 下一条指令地址 (函数调用)
BR   X8               ; 跳转到 X8 中的地址 (AArch64，寄存器间接跳转)
BLR  X8               ; 调用 X8 中的地址 (AArch64，间接函数调用)
RET                   ; 返回，等效于 BR X30 (AArch64)
BX   LR               ; 返回 (ARM32，同时可切换 ARM/Thumb 模式)

; === 条件分支 (ARM32) ===
CMP  R0, #10          ; 比较 R0 和 10
BEQ  label            ; Branch if Equal (Z=1)
BNE  label            ; Branch if Not Equal (Z=0)
BGT  label            ; Branch if Greater Than (有符号)
BLT  label            ; Branch if Less Than (有符号)
BHI  label            ; Branch if Higher (无符号大于)
BLO  label            ; Branch if Lower (无符号小于)

; === AArch64 条件分支 (使用点号语法) ===
CMP  X0, X1
B.EQ label            ; 相等
B.NE label            ; 不等

; === AArch64 特有的比较并分支 ===
CBZ  X0, label        ; X0 == 0 则跳转
CBNZ X0, label        ; X0 != 0 则跳转
TBZ  X0, #5, label    ; X0 的第 5 位为 0 则跳转
TBNZ X0, #5, label    ; X0 的第 5 位不为 0 则跳转
```

**常用条件码速查**

| 后缀   | 含义                      | 标志条件         |
| :----- | :------------------------ | :--------------- |
| `EQ`   | Equal (相等)              | Z=1              |
| `NE`   | Not Equal (不等)          | Z=0              |
| `GT`   | Greater Than (有符号大于) | Z=0, N=V         |
| `LT`   | Less Than (有符号小于)    | N!=V             |
| `GE`   | Greater or Equal          | N=V              |
| `LE`   | Less or Equal             | Z=1 或 N!=V      |
| `HI`   | Higher (无符号大于)       | C=1, Z=0         |
| `LO`   | Lower (无符号小于)        | C=0              |

#### 栈操作指令

```armasm
; === ARM32 栈操作 ===
PUSH {R4, R5, LR}     ; 将 R4, R5, LR 压入栈 (SP 向低地址增长)
POP  {R4, R5, PC}     ; 从栈弹出到 R4, R5, PC (将 LR 弹到 PC 实现返回)

; 等效展开：
; PUSH {R4, LR} 等同于:
;   STR  LR, [SP, #-4]!
;   STR  R4, [SP, #-4]!

; === AArch64 栈操作 ===
; AArch64 没有 PUSH/POP，使用 STP/LDP
STP  X29, X30, [SP, #-16]!  ; 保存 FP 和 LR，SP -= 16
MOV  X29, SP                ; 设置新的帧指针
; ... 函数体 ...
LDP  X29, X30, [SP], #16    ; 恢复 FP 和 LR，SP += 16
RET                          ; 返回

; 分配局部变量空间
SUB  SP, SP, #48             ; 分配 48 字节的栈空间 (必须是 16 的倍数)
; ... 使用 [SP, #0], [SP, #8] 等访问局部变量 ...
ADD  SP, SP, #48             ; 释放栈空间
```

---

### 函数调用约定 (AAPCS)

AAPCS (ARM Architecture Procedure Call Standard) 定义了函数之间如何交互。逆向工程师必须理解这些约定才能正确分析函数的输入输出。

#### 参数传递规则

**ARM32 (AAPCS)**

| 参数位置 | 寄存器 | 说明 |
| :------- | :----- | :--- |
| 第 1 个参数 | `R0` | 也用作返回值 |
| 第 2 个参数 | `R1` | 64 位参数可用 R0:R1 或 R2:R3 |
| 第 3 个参数 | `R2` | |
| 第 4 个参数 | `R3` | |
| 第 5+ 个参数 | 栈     | 按顺序压栈，第 5 个在 [SP]，第 6 个在 [SP, #4] |

**AArch64 (AAPCS64)**

| 参数位置 | 寄存器 | 说明 |
| :------- | :----- | :--- |
| 第 1 个参数 | `X0` | 也用作返回值 |
| 第 2 个参数 | `X1` | |
| 第 3-8 个参数 | `X2`-`X7` | |
| 第 9+ 个参数 | 栈 | |
| 浮点参数 | `D0`-`D7` | 使用 SIMD/浮点寄存器 |

#### 返回值

```armasm
; ARM32: 返回值在 R0 (32位) 或 R0:R1 (64位)
; 例: 返回 int
MOV  R0, #42
BX   LR

; AArch64: 返回值在 X0 (64位)
; 例: 返回 int
MOV  X0, #42
RET
```

#### 调用者保存 vs 被调用者保存

理解这个概念对识别函数边界非常重要：

| 类别 | ARM32 寄存器 | AArch64 寄存器 | 说明 |
| :--- | :----------- | :------------- | :--- |
| **调用者保存** (Caller-saved) | R0-R3, R12 | X0-X18 | 函数调用后可能被修改，调用者如需保留值必须自行保存 |
| **被调用者保存** (Callee-saved) | R4-R11 | X19-X28 | 被调用函数如果要使用，必须先保存、用完后恢复 |
| **特殊用途** | SP, LR, PC | SP, X29(FP), X30(LR) | 有特定约定 |

**实际例子：观察函数序言如何保存寄存器**

```armasm
; ARM32 函数序言 - 保存要使用的被调用者保存寄存器
my_function:
    PUSH {R4, R5, R6, LR}   ; 保存 R4-R6 (要使用) 和 LR (返回地址)
    SUB  SP, SP, #16         ; 分配 16 字节局部变量空间
    ; R0-R3 是参数，可以直接使用
    MOV  R4, R0              ; 将第一个参数保存到 R4 (调用其他函数后还需要用)
    BL   other_function      ; 调用其他函数 (R0-R3 可能被修改)
    ; R4 仍然保持之前的值，因为它是被调用者保存的
    MOV  R0, R4              ; 准备返回值
    ADD  SP, SP, #16         ; 释放局部变量空间
    POP  {R4, R5, R6, PC}   ; 恢复寄存器并返回

; AArch64 函数序言
my_function_a64:
    STP  X29, X30, [SP, #-32]!  ; 保存 FP, LR
    STP  X19, X20, [SP, #16]    ; 保存 callee-saved 寄存器
    MOV  X29, SP                ; 建立栈帧
    MOV  X19, X0                ; 保存第一个参数
    BL   other_function
    MOV  X0, X19                ; 使用保存的参数作为返回值
    LDP  X19, X20, [SP, #16]
    LDP  X29, X30, [SP], #32
    RET
```

---

### 常见模式识别

逆向工程最重要的技能之一是在汇编中识别高级语言的结构。以下是常见的代码模式。

#### if/else 结构

```c
// C 代码
if (a > 10) {
    result = 1;
} else {
    result = 0;
}
```

```armasm
; ARM32 汇编
    CMP   R0, #10         ; 比较 a 和 10
    BLE   .else_branch    ; 如果 a <= 10，跳到 else
    MOV   R0, #1          ; result = 1 (if 分支)
    B     .end_if         ; 跳过 else
.else_branch:
    MOV   R0, #0          ; result = 0 (else 分支)
.end_if:

; AArch64 可能使用条件选择指令代替分支
    CMP   W0, #10
    MOV   W1, #1          ; 准备 if 的值
    MOV   W2, #0          ; 准备 else 的值
    CSEL  W0, W1, W2, GT  ; W0 = (a > 10) ? W1 : W2
```

!!! tip "识别技巧"
看到 `CMP` 后紧跟条件跳转 `B.xx`，这几乎一定是 if/else 结构。跳转目标就是 else 分支或 if 块结束的位置。注意条件码是**反转**的：C 代码中是 `> 10`，汇编中跳转条件是 `<= 10` (BLE)，因为是"不满足条件就跳过"。

#### for 循环

```c
// C 代码
int sum = 0;
for (int i = 0; i < 10; i++) {
    sum += array[i];
}
```

```armasm
; AArch64 汇编
    MOV   W0, #0          ; sum = 0
    MOV   W1, #0          ; i = 0
    ADR   X2, array       ; X2 = 数组基地址
.loop_start:
    CMP   W1, #10         ; i < 10?
    B.GE  .loop_end       ; 如果 i >= 10，退出循环
    LDRSH W3, [X2, X1, LSL #2]  ; W3 = array[i] (假设 int 数组)
    ADD   W0, W0, W3      ; sum += array[i]
    ADD   W1, W1, #1      ; i++
    B     .loop_start     ; 跳回循环头部
.loop_end:
```

!!! tip "识别 for 循环的三要素"
1. **初始化**：循环变量设为初始值 (`MOV W1, #0`)
2. **条件检查**：`CMP` + 条件跳转到循环体外 (`CMP W1, #10; B.GE`)
3. **递增/递减**：循环变量更新 (`ADD W1, W1, #1`) 后跳回条件检查处

编译器可能将条件检查放在循环末尾（do-while 优化），这时结构变为：先跳到末尾检查，循环体在前，条件判断在后。

#### while 循环

```c
// C 代码
while (ptr != NULL) {
    process(ptr);
    ptr = ptr->next;
}
```

```armasm
; AArch64 汇编
    ; X19 = ptr (使用 callee-saved 寄存器保存)
.while_check:
    CBZ   X19, .while_end    ; if (ptr == NULL) 跳出
    MOV   X0, X19            ; 第一个参数 = ptr
    BL    process             ; 调用 process(ptr)
    LDR   X19, [X19, #8]    ; ptr = ptr->next (假设 next 在偏移 +8)
    B     .while_check       ; 回到条件检查
.while_end:
```

#### switch-case 结构

switch-case 有多种编译方式，最常见的是**跳转表 (jump table)**。

```c
// C 代码
switch (cmd) {
    case 0: action_a(); break;
    case 1: action_b(); break;
    case 2: action_c(); break;
    default: action_default(); break;
}
```

```armasm
; AArch64 汇编 (跳转表实现)
    CMP   W0, #2            ; cmd 和最大 case 值比较
    B.HI  .default_case     ; 无符号大于 2，跳到 default
    ADR   X1, .jump_table   ; 取跳转表基地址
    LDRSW X2, [X1, X0, LSL #2]  ; 从跳转表加载偏移
    ADD   X1, X1, X2        ; 计算目标地址
    BR    X1                ; 跳转到对应 case

.jump_table:
    .word .case_0 - .jump_table
    .word .case_1 - .jump_table
    .word .case_2 - .jump_table

.case_0:
    BL    action_a
    B     .switch_end
.case_1:
    BL    action_b
    B     .switch_end
.case_2:
    BL    action_c
    B     .switch_end
.default_case:
    BL    action_default
.switch_end:
```

!!! tip "在 IDA/Ghidra 中识别 switch"
当你看到一个 `CMP` 后跟范围检查 (`B.HI` 或 `B.HS`)，然后有一个 `ADR` + 表加载 + `BR` 的组合时，这就是一个跳转表实现的 switch。IDA 通常能自动识别并显示为 `switch jump` 注释。如果识别不了，可以手动指定跳转表。

#### 函数序言/结语 (Prologue/Epilogue)

这是最重要的模式之一，因为它标志着函数的边界。

```armasm
; === ARM32 典型函数序言/结语 ===
func_arm32:
    ; --- 序言 (Prologue) ---
    PUSH  {R4-R7, LR}       ; 保存被调用者保存寄存器和返回地址
    SUB   SP, SP, #20       ; 为局部变量分配栈空间
    ; --- 函数体 ---
    ; ...
    ; --- 结语 (Epilogue) ---
    ADD   SP, SP, #20       ; 释放局部变量空间
    POP   {R4-R7, PC}       ; 恢复寄存器，将 LR 弹到 PC 实现返回

; === AArch64 典型函数序言/结语 ===
func_aarch64:
    ; --- 序言 (Prologue) ---
    STP   X29, X30, [SP, #-32]!  ; 保存 FP 和 LR
    STP   X19, X20, [SP, #16]    ; 保存将要使用的 callee-saved 寄存器
    MOV   X29, SP                ; 建立帧指针
    ; --- 函数体 ---
    ; ...
    ; --- 结语 (Epilogue) ---
    LDP   X19, X20, [SP, #16]    ; 恢复 callee-saved 寄存器
    LDP   X29, X30, [SP], #32    ; 恢复 FP 和 LR
    RET                           ; 返回
```

---

### Thumb/Thumb-2 模式

在 Android 32 位 `.so` 文件中，你几乎总是在看 **Thumb-2** 代码，而不是纯 ARM 代码。理解 Thumb 模式对于正确分析至关重要。

#### 什么是 Thumb？

- **Thumb (T1)**：原始 Thumb 指令集，所有指令都是 16 位宽。代码密度高，但功能有限。
- **Thumb-2 (T2)**：ARMv6T2 及以上引入。混合使用 16 位和 32 位指令，既有高代码密度，又有完整功能。
- **ARM 模式**：所有指令 32 位宽。功能完整，但代码密度低。

#### ARM 与 Thumb 模式切换

处理器通过 CPSR 的 `T` 位判断当前模式。关键的切换机制是 **BX (Branch and Exchange)** 指令：

```armasm
; BX 指令通过目标地址的最低位判断切换到哪个模式：
; - 地址最低位 = 1 -> 切换到 Thumb 模式
; - 地址最低位 = 0 -> 切换到 ARM 模式
; (实际跳转时最低位会被忽略，只用于模式判断)

BX   R0          ; 跳转到 R0 中的地址，根据 R0[0] 切换模式
BLX  R0          ; 带链接的分支并交换模式
BLX  label       ; 跳转到 label 并切换 ARM/Thumb 模式
```

#### 在 IDA 中识别 Thumb 代码

- **函数地址**：如果函数地址是奇数（最低位为 1），说明是 Thumb 代码。例如地址 `0x1001` 实际是 `0x1000` 处的 Thumb 代码。
- **指令长度**：IDA 中 Thumb-2 代码的指令长度是 2 或 4 字节，ARM 模式总是 4 字节。
- **手动切换**：如果 IDA 错误地以 ARM 模式解析了 Thumb 代码（或反之），可以按 `Alt+G` 修改 `T` 寄存器的值（1 = Thumb，0 = ARM），然后按 `C` 重新分析。

#### Thumb-2 vs ARM 指令对比

| 操作 | ARM 模式 | Thumb-2 模式 |
| :--- | :------- | :----------- |
| 加法 | `ADD R0, R1, R2` (32-bit) | `ADD R0, R1, R2` (16-bit 或 32-bit) |
| 压栈 | `STMDB SP!, {R4-R6, LR}` | `PUSH {R4-R6, LR}` (16-bit) |
| 条件执行 | `ADDNE R0, R0, #1` | 需要 `IT NE` + `ADD R0, R0, #1` |
| 分支 | `B label` (32-bit) | `B label` (16-bit, 范围较小) |

**IT (If-Then) 指令块**：Thumb-2 用 IT 指令实现条件执行，这是逆向中常见的模式：

```armasm
; Thumb-2 条件执行
    CMP   R0, #0
    ITE   EQ         ; If-Then-Else: 如果 EQ，下一条执行；否则下下条执行
    MOVEQ R1, #1     ; if (R0 == 0) R1 = 1
    MOVNE R1, #0     ; else R1 = 0
```

!!! warning "AArch64 没有 Thumb"
ARM64 (AArch64) 架构不存在 Thumb 模式。AArch64 只使用固定 32 位宽的 A64 指令集。所以当你分析 `arm64-v8a` 的 `.so` 文件时，不需要担心 Thumb 模式的问题。

---

### NEON/SIMD 基础

在逆向分析加密算法（如 AES、SHA）的 native 实现时，你可能会遇到 NEON 指令。NEON 是 ARM 的 SIMD (单指令多数据) 扩展，能同时对多个数据元素执行相同操作。

#### NEON 寄存器

**ARM32 (VFPv3/NEON)**

| 寄存器 | 大小 | 说明 |
| :----- | :--- | :--- |
| `S0`-`S31` | 32-bit | 单精度浮点 |
| `D0`-`D31` | 64-bit | 双精度浮点 / NEON 向量 |
| `Q0`-`Q15` | 128-bit | NEON 四字向量 (Q0 = D0:D1) |

**AArch64 (ASIMD)**

| 寄存器 | 大小 | 说明 |
| :----- | :--- | :--- |
| `V0`-`V31` | 128-bit | 统一的向量/浮点寄存器 |
| 访问方式 | `Vn.16B` | 16 个字节 |
| | `Vn.8H` | 8 个半字 (16-bit) |
| | `Vn.4S` | 4 个单字 (32-bit) |
| | `Vn.2D` | 2 个双字 (64-bit) |

#### 逆向中常见的 NEON 指令

```armasm
; AArch64 NEON 示例 (AES 加密中常见)
LD1   {V0.16B}, [X0]          ; 从 X0 加载 16 字节到 V0
LD1   {V1.16B}, [X1]          ; 加载密钥
AESE  V0.16B, V1.16B          ; AES 单轮加密
AESMC V0.16B, V0.16B          ; AES MixColumns
EOR   V0.16B, V0.16B, V2.16B  ; 异或操作 (向量)
ST1   {V0.16B}, [X0]          ; 将结果存储回内存

; 常见的向量算术
ADD   V0.4S, V1.4S, V2.4S     ; 4 个 32 位整数同时加法
MUL   V0.4S, V1.4S, V2.4S     ; 4 个 32 位整数同时乘法
SHL   V0.4S, V1.4S, #8        ; 4 个 32 位元素同时左移 8 位
TBL   V0.16B, {V1.16B}, V2.16B ; 查表指令 (S-Box 实现常用)
```

!!! note "遇到 NEON 不要慌"
在逆向中遇到大量 NEON 指令，通常意味着以下几种情况之一：
1. **加密算法**：AES、SHA 等有硬件加速指令 (AESE、SHA256H 等)
2. **数据处理**：图片处理、音视频编解码
3. **校验和**：CRC32 等

通常你不需要逐条理解每个 NEON 指令，而是识别出**整体模式**（这是一个 AES 加密循环、这是一个 SHA-256 压缩函数等），然后查找对应的标准实现进行对比。

---

### 在 IDA/Ghidra 中阅读 ARM

掌握工具的使用技巧能极大提升逆向效率。

#### IDA Pro 实用技巧

**基本操作**

| 快捷键 | 功能 |
| :----- | :--- |
| `Space` | 在图形视图和文本视图之间切换 |
| `F5` | 反编译 (查看伪代码) |
| `G` | 跳转到指定地址 |
| `N` | 重命名函数/变量 |
| `X` | 查看交叉引用 (Xrefs) |
| `Y` | 修改函数签名/类型 |
| `H` | 切换数值显示格式 (十进制/十六进制) |
| `Alt+G` | 修改段寄存器值 (用于切换 ARM/Thumb) |
| `/` | 在反编译视图中添加注释 |

**ARM 特定技巧**

1. **检查 Thumb 模式**：如果反汇编看起来不对劲（大量无效指令），可能是 ARM/Thumb 模式判断错误。使用 `Alt+G` 设置 `T` 值。

2. **识别字符串引用**：在 ARM64 代码中，字符串加载通常是 `ADRP + ADD` 的组合：
```armasm
ADRP  X0, #aHelloWorld@PAGE      ; 加载页地址
ADD   X0, X0, #aHelloWorld@PAGEOFF ; 加上页内偏移
BL    puts                         ; 调用 puts
```

3. **结构体偏移**：看到连续的 `LDR Xn, [X0, #offset]` 时，这通常是在访问结构体成员。可以在 IDA 中创建结构体定义来改善可读性。

4. **函数签名恢复**：对于 JNI 函数，第一个参数是 `JNIEnv*`，第二个是 `jobject` (实例方法) 或 `jclass` (静态方法)。在 IDA 中设置正确的函数签名后，反编译结果会清晰得多。

#### Ghidra 实用技巧

1. **导入 `.so` 文件**：选择正确的处理器类型（ARM/AARCH64）和字节序（小端序 LE）。
2. **JNI 头文件**：通过 File -> Parse C Source 导入 `jni.h`，可以正确标注 JNI 函数。
3. **常用操作**：`L` 重命名、右键 "Retype Variable" 改类型、Window -> "Decompiler" 看反编译。
4. **注意事项**：Ghidra 可能在 Thumb/ARM 模式混淆、NEON 指令、尾调用优化等场景产生错误。

#### Frida 配合汇编分析

在静态分析后，可以用 Frida 动态验证你的理解：

```javascript
// 在特定地址读取寄存器值 (AArch64)
Interceptor.attach(ptr("0x12345678"), {
    onEnter: function(args) {
        // args[0] 对应 X0, args[1] 对应 X1, ...
        console.log("X0 =", args[0]);
        console.log("X1 =", args[1]);

        // 读取更多寄存器
        console.log("X8 =", this.context.x8);
        console.log("SP =", this.context.sp);
        console.log("LR =", this.context.lr);

        // 读取内存
        console.log("X0 指向的字符串:", args[0].readUtf8String());
        console.log("[SP+0x10]:", this.context.sp.add(0x10).readPointer());
    }
});
```

!!! tip "从汇编到 Frida hook 的工作流"
1. 在 IDA/Ghidra 中定位目标函数，分析函数签名
2. 找到关键比较/分支点 (如密码校验、License 检查)
3. 使用 Frida `Interceptor.attach` 在对应地址 hook，读取或修改寄存器值
4. 如果需要绕过检查，用 `Interceptor.replace` 替换函数或 `Memory.patchCode` 修改指令
