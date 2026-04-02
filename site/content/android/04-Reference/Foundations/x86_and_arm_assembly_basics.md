---
title: "x86 与 ARM 汇编基础指南"
date: 2024-05-21
type: posts
tags: ["基础知识", "Smali", "Android", "ARM汇编", "DEX"]
weight: 10
---

# x86 与 ARM 汇编基础指南

汇编语言是与计算机硬件直接对话的低级编程语言，是逆向工程、系统编程和性能优化的基石。在当今世界，x86 和 ARM 是两种最主流的指令集架构 (ISA)。理解它们的核心概念与差异对于逆向工程师至关重要。

- **x86**: 由 Intel 主导，采用**CISC (复杂指令集计算机)** 设计。指令长度可变，功能强大但复杂，主要用于桌面和服务器。

- **ARM**: 由 ARM Holdings 设计，采用**RISC (精简指令集计算机)** 设计。指令长度固定，设计简洁优雅，功耗低，主宰了移动和嵌入式设备领域。

---

## x86/x64 寄存器模型

x86 架构的寄存器有着复杂的历史演变。从 16 位到 32 位再到 64 位，每一代都是在前一代基础上扩展的，因此寄存器命名呈现出嵌套结构。

### 通用寄存器 (General Purpose Registers)

**32 位 (IA-32) 通用寄存器**

8 个 32 位通用寄存器，它们有历史上的主要用途，但在很多情况下可以通用。

| 寄存器  | 16 位 | 高 8 位 | 低 8 位 | 主要用途                                                     |
| :------ | :---- | :------ | :------ | :----------------------------------------------------------- |
| **EAX** | AX    | AH      | AL      | **累加器**：函数返回值、算术运算                             |
| **EBX** | BX    | BH      | BL      | **基址**：数据段基址指针                                     |
| **ECX** | CX    | CH      | CL      | **计数器**：循环计数、移位计数                               |
| **EDX** | DX    | DH      | DL      | **数据**：乘除法扩展、I/O 端口                               |
| **ESP** | SP    | —       | —       | **栈指针**：永远指向栈顶                                     |
| **EBP** | BP    | —       | —       | **基址指针**：指向当前栈帧底部                               |
| **ESI** | SI    | —       | —       | **源变址**：字符串操作源地址                                 |
| **EDI** | DI    | —       | —       | **目的变址**：字符串操作目的地址                             |
| **EIP** | IP    | —       | —       | **指令指针**：指向下一条将执行的指令 (不可直接修改)          |

**64 位 (x86-64/AMD64) 通用寄存器**

x86-64 将所有寄存器扩展为 64 位，并新增了 R8-R15。

| 64 位   | 32 位   | 16 位   | 8 位    | 说明                           |
| :------ | :------ | :------ | :------ | :----------------------------- |
| **RAX** | EAX     | AX      | AL      | 返回值                         |
| **RBX** | EBX     | BX      | BL      | 被调用者保存                   |
| **RCX** | ECX     | CX      | CL      | System V: 第 4 个参数; Win: 第 1 个参数 |
| **RDX** | EDX     | DX      | DL      | System V: 第 3 个参数; Win: 第 2 个参数 |
| **RSP** | ESP     | SP      | SPL     | 栈指针                         |
| **RBP** | EBP     | BP      | BPL     | 帧指针 (被调用者保存)          |
| **RSI** | ESI     | SI      | SIL     | System V: 第 2 个参数          |
| **RDI** | EDI     | DI      | DIL     | System V: 第 1 个参数          |
| **R8**  | R8D     | R8W     | R8B     | System V: 第 5 个参数          |
| **R9**  | R9D     | R9W     | R9B     | System V: 第 6 个参数          |
| **R10** | R10D    | R10W    | R10B    | 调用者保存                     |
| **R11** | R11D    | R11W    | R11B    | 调用者保存                     |
| **R12** | R12D    | R12W    | R12B    | 被调用者保存                   |
| **R13** | R13D    | R13W    | R13B    | 被调用者保存                   |
| **R14** | R14D    | R14W    | R14B    | 被调用者保存                   |
| **R15** | R15D    | R15W    | R15B    | 被调用者保存                   |
| **RIP** | EIP     | IP      | —       | 指令指针                       |

> [!note] 32 位操作自动清零高 32 位
> 在 x86-64 中，对 32 位寄存器 (如 EAX) 的写操作会**自动将高 32 位清零**。但对 16 位或 8 位寄存器的写操作**不会**清零高位。这是一个重要细节：
> ```nasm
> MOV EAX, 0x1          ; RAX = 0x00000000_00000001 (高位自动清零)
> MOV  AX, 0x1          ; RAX 的高 48 位保持不变，只改低 16 位
> ```


### 段寄存器 (Segment Registers)

在现代系统中段寄存器作用已弱化，但 `FS`/`GS` 仍用于线程本地存储 (TLS)。在 Android 逆向中基本不会遇到。

### 标志寄存器 (EFLAGS/RFLAGS)

标志寄存器记录了上一条运算指令的结果状态，条件跳转指令据此决定是否跳转。

| 标志位 | 名称         | 含义                                      |
| :----- | :----------- | :---------------------------------------- |
| `ZF`   | Zero Flag    | 结果为零时置 1                            |
| `SF`   | Sign Flag    | 结果为负 (最高位为 1) 时置 1              |
| `CF`   | Carry Flag   | 无符号运算产生进位/借位时置 1             |
| `OF`   | Overflow Flag| 有符号运算溢出时置 1                      |
| `DF`   | Direction Flag | 字符串操作方向                          |
| `TF`   | Trap Flag    | 单步调试标志                              |

---

## x86 汇编 (IA-32)

以 32 位 x86 架构为例，其设计复杂而灵活。

### 常用指令

- **数据传送**:
- `MOV dest, src`: 将 `src` 的值赋给 `dest`。 (e.g., `MOV EAX, EBX`)

- `PUSH val`: 将 `val` 压入栈顶，`ESP` 减 4。

- `POP reg`: 从栈顶弹出一个值到 `reg`，`ESP` 加 4。

- `LEA reg, [mem]`: 将 `mem` 的**有效地址**加载到 `reg`，而不是其内容。

- `MOVZX reg, src`: 零扩展传送 (高位补零)。

- `MOVSX reg, src`: 符号扩展传送 (高位补符号位)。

- **算术运算**:
- `ADD dest, src`: `dest = dest + src`

- `SUB dest, src`: `dest = dest - src`

- `INC reg`: `reg = reg + 1`

- `DEC reg`: `reg = reg - 1`

- `IMUL`: 有符号乘法。单操作数: `EDX:EAX = EAX * 操作数`; 双操作数: `dest = dest * src`

- `IDIV divisor`: 有符号除法。`EDX:EAX / divisor`，商在 EAX，余数在 EDX。

- `NEG reg`: 取反 (`reg = -reg`)
- **逻辑运算**:
- `AND dest, src`: 按位与

- `OR dest, src`: 按位或

- `XOR dest, src`: 按位异或。`XOR EAX, EAX` 是清零 EAX 的惯用手法。

- `NOT reg`: 按位取反

- `SHL reg, count`: 逻辑左移

- `SHR reg, count`: 逻辑右移

- `SAR reg, count`: 算术右移 (保留符号位)

- `TEST reg1, reg2`: 按位与但不存储结果，只更新标志位。`TEST EAX, EAX` 用于检测 EAX 是否为 0。

- **比较与跳转**:
- `CMP reg1, reg2`: 比较 (实际是做减法)，并设置标志位。

- `JMP target`: 无条件跳转。

- `JE/JZ target`: 相等/零 (ZF=1) 则跳转。

- `JNE/JNZ target`: 不等/非零 (ZF=0) 则跳转。

- `JG/JNLE target`: 有符号大于。

- `JL/JNGE target`: 有符号小于。

- `JGE/JNL target`: 有符号大于等于。

- `JLE/JNG target`: 有符号小于等于。

- `JA/JB target`: 无符号大于/小于。
- **函数调用**:
- `CALL target`: 将 `EIP` 的下一条指令地址压栈，然后跳转到 `target`。

- `RET`: 从栈顶弹出地址，并跳转到该地址。

- `RET n`: 返回并从栈中弹出 n 字节 (被调用者清理栈，stdcall 使用)。

- `LEAVE`: 等价于 `MOV ESP, EBP; POP EBP`。用于函数结语中拆除栈帧。

---

## x86 调用约定详解

调用约定规定了函数如何传递参数、如何返回结果、谁负责清理栈。在逆向中正确识别调用约定是理解函数接口的关键。

### 32 位调用约定

#### cdecl (C Declaration)

C 语言的默认调用约定，Linux/macOS 上最常见。

```nasm
; 调用 int add(int a, int b)  => add(1, 2)
PUSH  2              ; 第二个参数 (从右往左压栈)
PUSH  1              ; 第一个参数
CALL  add            ; 调用函数
ADD   ESP, 8         ; 调用者清理栈 (2 个参数 * 4 字节)
; 返回值在 EAX 中
```

| 特性 | 说明 |
| :--- | :--- |
| 参数传递 | 从右到左压栈 |
| 栈清理 | **调用者** (caller) |
| 返回值 | EAX (32位), EDX:EAX (64位) |
| 支持变参 | 是 (如 printf) |

#### stdcall (Standard Call)

Win32 API 的标准调用约定。

```nasm
; 调用 int __stdcall MessageBoxA(HWND, LPCSTR, LPCSTR, UINT)
PUSH  0              ; uType = MB_OK
PUSH  offset szTitle ; lpCaption
PUSH  offset szText  ; lpText
PUSH  0              ; hWnd = NULL
CALL  MessageBoxA    ; 调用函数
; 不需要 ADD ESP —— 被调用者已经清理了
; 函数内部以 RET 16 结尾
```

| 特性 | 说明 |
| :--- | :--- |
| 参数传递 | 从右到左压栈 |
| 栈清理 | **被调用者** (callee)，通过 `RET n` 实现 |
| 返回值 | EAX |
| 支持变参 | 否 |

#### fastcall

前两个参数通过寄存器传递，提高效率。

```nasm
; 调用 int __fastcall func(int a, int b, int c)  => func(1, 2, 3)
PUSH  3              ; 第三个参数通过栈
MOV   EDX, 2         ; 第二个参数 -> EDX
MOV   ECX, 1         ; 第一个参数 -> ECX
CALL  func
```

| 特性 | 说明 |
| :--- | :--- |
| 参数传递 | ECX=第1参数, EDX=第2参数, 剩余压栈 |
| 栈清理 | 被调用者 |
| 返回值 | EAX |

### 64 位调用约定

#### System V AMD64 ABI (Linux/macOS/Android x86-64)

这是 Android x86-64 模拟器中使用的调用约定，也是 Linux/macOS 的标准。

```nasm
; 调用 long func(long a, long b, long c, long d, long e, long f, long g)
; func(1, 2, 3, 4, 5, 6, 7)
PUSH  7              ; 第 7 个参数通过栈
MOV   R9, 6          ; 第 6 个参数
MOV   R8, 5          ; 第 5 个参数
MOV   RCX, 4         ; 第 4 个参数
MOV   RDX, 3         ; 第 3 个参数
MOV   RSI, 2         ; 第 2 个参数
MOV   RDI, 1         ; 第 1 个参数
CALL  func
ADD   RSP, 8         ; 调用者清理栈上的参数
```

| 特性 | 说明 |
| :--- | :--- |
| 整数参数 | RDI, RSI, RDX, RCX, R8, R9 (前 6 个) |
| 浮点参数 | XMM0-XMM7 (前 8 个) |
| 栈清理 | 调用者 |
| 返回值 | RAX (整数), XMM0 (浮点) |
| 被调用者保存 | RBX, RBP, R12-R15 |
| 调用者保存 | 其余所有 |
| Red Zone | RSP 下方 128 字节可用 (叶函数优化) |
| 栈对齐 | CALL 前 RSP 必须 16 字节对齐 |

#### Microsoft x64 (Windows x64)

| 特性 | 说明 |
| :--- | :--- |
| 整数参数 | RCX, RDX, R8, R9 (前 4 个) |
| 浮点参数 | XMM0-XMM3 (前 4 个) |
| Shadow Space | 调用者必须在栈上预留 32 字节 |
| 被调用者保存 | RBX, RBP, RDI, RSI, R12-R15 |

> [!tip] 快速判断调用约定
> - `PUSH` 参数 + `CALL` + `ADD ESP, N` -> **cdecl**
> - `PUSH` 参数 + `CALL`，无栈清理 -> **stdcall**
> - ECX/EDX 传参 -> **fastcall** 或 **thiscall**
> - 64 位 RDI/RSI 传参 -> **System V AMD64**
> - 64 位 RCX/RDX 传参 -> **Microsoft x64**


---

## ARM 汇编 (ARMv7)

以 32 位 ARM 架构为例，其设计简洁而高效。

### 核心寄存器

共有 16 个 32 位通用寄存器 (R0-R15)。

| 寄存器       | 别名   | 主要用途                                                                |
| :----------- | :----- | :---------------------------------------------------------------------- |
| **R0 - R3**  |        | **参数/返回值**: 用于传递函数的前 4 个参数，`R0` 也用于存放函数返回值。 |
| **R4 - R11** |        | **被调用者保存**：函数使用前必须保存，返回前恢复。                      |
| **R12**      | **IP** | 过程内调用临时寄存器 (链接器使用)。                                     |
| **R13**      | **SP** | **栈指针 (Stack Pointer)**: 指向栈顶。                                  |
| **R14**      | **LR** | **链接寄存器 (Link Register)**: **存储函数的返回地址**。                |
| **R15**      | **PC** | **程序计数器 (Program Counter)**: **指向下一条将要执行的指令**。        |

### 加载/存储 (Load/Store) 架构

这是 RISC 的核心思想。**CPU 不能直接对内存中的数据进行运算**。

1. 必须先用 `LDR` (Load Register) 指令将内存中的数据加载到寄存器中。
2. 在寄存器之间完成所有算术和逻辑运算。
3. 再用 `STR` (Store Register) 指令将结果存回内存。

```armasm
; x86 可以直接对内存操作:
;   ADD [EBP-4], 10       ; 直接把内存中的值加 10

; ARM 必须三步走:
LDR  R0, [R11, #-4]      ; 1. 从内存加载到寄存器
ADD  R0, R0, #10          ; 2. 在寄存器中运算
STR  R0, [R11, #-4]      ; 3. 将结果存回内存
```

### 常用指令

- **数据传送**:
- `MOV Rd, Rn`: 将 `Rn` 的值赋给 `Rd`。 (e.g., `MOV R0, R1`)

- `MOV Rd, #imm`: 将立即数赋给 `Rd`。 (e.g., `MOV R0, #0xFF`)

- `MVN Rd, Rn`: 将 `Rn` 按位取反后赋给 `Rd`。
- **算术运算**:
- `ADD Rd, Rn, Rm`: `Rd = Rn + Rm`

- `SUB Rd, Rn, Rm`: `Rd = Rn - Rm`

- `MUL Rd, Rn, Rm`: `Rd = Rn * Rm`

- `RSB Rd, Rn, #0`: `Rd = 0 - Rn` (取负数的惯用手法)
- **内存操作**:
- `LDR Rd, [Rn, #offset]`: 从地址 `Rn + offset` 加载一个字到 `Rd`。

- `STR Rd, [Rn, #offset]`: 将 `Rd` 的值存储到地址 `Rn + offset`。

- `LDRB Rd, [Rn]`: 加载一个字节。

- `STRB Rd, [Rn]`: 存储一个字节。
- **栈操作**:
- `PUSH {reg_list}`: 将寄存器列表压入栈。

- `POP {reg_list}`: 将值从栈中弹出到寄存器列表。
- **跳转与比较**:
- `CMP Rn, Rm`: 比较 `Rn` 和 `Rm`，并设置标志位。

- `B target`: 无条件跳转到 `target`。

- `BEQ target`: 如果相等则跳转。

- `BNE target`: 如果不相等则跳转。

- `BL target`: **(Branch with Link)** "调用函数"。它会**自动将下一条指令的地址存入 LR 寄存器**，然后跳转到 `target`。

- 函数返回时，只需执行 `MOV PC, LR` 或 `BX LR` 即可。

### 调用约定 (AAPCS)

ARM Procedure Call Standard。

- **参数传递**:
- 前 4 个参数通过 **R0, R1, R2, R3** 传递。

- 剩余的参数通过栈传递。
- **返回值**:
- 返回值存储在 **R0** 中。
- **返回地址**:
- 通过 **LR** 寄存器管理。

---

## x86 vs ARM 指令对比

这一节将常见操作在两种架构上的实现并排对比，帮助你在两种架构之间快速切换思维。

### 基本操作对比

| 操作 | x86 (AT&T 语法) | x86 (Intel 语法) | ARM (AArch64) |
| :--- | :--------------- | :---------------- | :------------- |
| 赋值 | `movl $1, %eax` | `MOV EAX, 1` | `MOV W0, #1` |
| 加法 | `addl %ebx, %eax` | `ADD EAX, EBX` | `ADD W0, W0, W1` |
| 减法 | `subl $5, %eax` | `SUB EAX, 5` | `SUB W0, W0, #5` |
| 比较 | `cmpl $10, %eax` | `CMP EAX, 10` | `CMP W0, #10` |
| 条件跳转 | `je label` | `JE label` | `B.EQ label` |
| 函数调用 | `call func` | `CALL func` | `BL func` |
| 函数返回 | `ret` | `RET` | `RET` |
| 清零 | `xorl %eax, %eax` | `XOR EAX, EAX` | `MOV W0, WZR` |

### 函数调用对比

```nasm
; === x86-64 (System V): 调用 func(1, 2, 3) ===
MOV   EDI, 1             ; 第 1 个参数 -> RDI
MOV   ESI, 2             ; 第 2 个参数 -> RSI
MOV   EDX, 3             ; 第 3 个参数 -> RDX
CALL  func               ; CALL 会把返回地址压栈
; 返回值在 RAX
```

```armasm
; === AArch64 (AAPCS64): 调用 func(1, 2, 3) ===
MOV   W0, #1             ; 第 1 个参数 -> X0
MOV   W1, #2             ; 第 2 个参数 -> X1
MOV   W2, #3             ; 第 3 个参数 -> X2
BL    func               ; BL 把返回地址存入 LR (X30)
; 返回值在 X0
```

### 栈帧建立对比

```nasm
; === x86 函数序言/结语 ===
; 序言 (Prologue)
PUSH  EBP                ; 保存旧的帧指针
MOV   EBP, ESP           ; 建立新的帧指针
SUB   ESP, 0x20          ; 分配 32 字节局部变量空间
PUSH  EBX                ; 保存被调用者保存寄存器

; 结语 (Epilogue)
POP   EBX                ; 恢复被调用者保存寄存器
LEAVE                    ; MOV ESP, EBP; POP EBP
RET                      ; 从栈弹出返回地址并跳转
```

```armasm
; === AArch64 函数序言/结语 ===
; 序言 (Prologue)
STP   X29, X30, [SP, #-32]!  ; 保存 FP 和 LR，分配栈空间
MOV   X29, SP                ; 建立帧指针
STP   X19, X20, [SP, #16]    ; 保存被调用者保存寄存器

; 结语 (Epilogue)
LDP   X19, X20, [SP, #16]    ; 恢复被调用者保存寄存器
LDP   X29, X30, [SP], #32    ; 恢复 FP 和 LR
RET                           ; 返回 (跳转到 LR)
```

### 核心差异总结

| 特性         | x86 (CISC)                                      | ARM (RISC)                                            |
| :----------- | :---------------------------------------------- | :---------------------------------------------------- |
| **指令集**   | 复杂，长度可变 (1-15 字节)                      | 精简，长度固定 (ARM: 4 字节, Thumb: 2/4 字节)        |
| **内存访问** | **可以直接对内存操作** (e.g., `ADD [mem], EAX`) | **加载/存储架构** (必须先 `LDR`，再 `STR`)            |
| **寄存器**   | 较少 (8/16 个)，且有特定用途                    | 较多 (16/31 个)，大多为通用寄存器                     |
| **函数调用** | `CALL` 指令压栈 `EIP`                           | `BL` 指令将返回地址存入 `LR` 寄存器                   |
| **参数传递** | 32位: 主要通过**栈**; 64位: 寄存器              | 主要通过**寄存器** (R0-R3 / X0-X7)                    |
| **条件执行** | 通过 `CMP` 和 `Jcc` 跳转指令                    | ARM32: 几乎所有指令可条件执行; A64: 条件分支 + CSEL   |
| **操作数格式** | 二操作数: `ADD EAX, EBX` (EAX += EBX)         | 三操作数: `ADD R0, R1, R2` (R0 = R1 + R2)            |
| **返回指令** | `RET` (从栈弹出地址)                            | `BX LR` / `RET` (从寄存器取地址)                     |

---

## 常见指令速查表

### x86/x64 指令速查

| 指令 | 操作 | 示例 | 说明 |
| :--- | :--- | :--- | :--- |
| `MOV` | 赋值 | `MOV EAX, 1` | dest = src |
| `LEA` | 取地址 | `LEA EAX, [EBX+ECX*4]` | dest = 有效地址 (不访问内存) |
| `PUSH` | 压栈 | `PUSH EAX` | ESP -= 4; [ESP] = EAX |
| `POP` | 弹栈 | `POP EAX` | EAX = [ESP]; ESP += 4 |
| `ADD` | 加法 | `ADD EAX, EBX` | dest += src |
| `SUB` | 减法 | `SUB EAX, 5` | dest -= src |
| `IMUL` | 乘法 | `IMUL EAX, EBX` | dest *= src |
| `IDIV` | 除法 | `IDIV ECX` | EAX = EDX:EAX / ECX |
| `AND` | 按位与 | `AND EAX, 0xFF` | dest &= src |
| `OR` | 按位或 | `OR EAX, 1` | dest \|= src |
| `XOR` | 按位异或 | `XOR EAX, EAX` | dest ^= src (清零惯用法) |
| `SHL` | 左移 | `SHL EAX, 3` | dest <<= count |
| `SHR` | 逻辑右移 | `SHR EAX, 1` | dest >>= count (补0) |
| `SAR` | 算术右移 | `SAR EAX, 1` | dest >>= count (补符号) |
| `CMP` | 比较 | `CMP EAX, 10` | 设置标志位 (dest - src) |
| `TEST` | 测试 | `TEST EAX, EAX` | 设置标志位 (dest & src) |
| `JMP` | 跳转 | `JMP label` | 无条件跳转 |
| `JE/JZ` | 相等跳转 | `JE label` | ZF=1 则跳 |
| `JNE/JNZ` | 不等跳转 | `JNE label` | ZF=0 则跳 |
| `CALL` | 调用 | `CALL func` | 压栈返回地址并跳转 |
| `RET` | 返回 | `RET` | 弹出返回地址并跳转 |
| `NOP` | 空操作 | `NOP` | 什么也不做 (对齐/填充) |

### ARM/AArch64 指令速查

| 指令 | 操作 | 示例 | 说明 |
| :--- | :--- | :--- | :--- |
| `MOV` | 赋值 | `MOV X0, X1` | Xd = Xn |
| `MVN` | 取反赋值 | `MVN X0, X1` | Xd = ~Xn |
| `LDR` | 加载 | `LDR X0, [X1, #8]` | Xd = *(Xn + offset) |
| `STR` | 存储 | `STR X0, [X1]` | *Xn = Xd |
| `LDP` | 加载对 | `LDP X0, X1, [SP]` | 一次加载两个寄存器 (AArch64) |
| `STP` | 存储对 | `STP X0, X1, [SP, #-16]!` | 一次存储两个寄存器 (AArch64) |
| `ADD` | 加法 | `ADD X0, X1, X2` | Xd = Xn + Xm |
| `SUB` | 减法 | `SUB X0, X1, #10` | Xd = Xn - imm |
| `MUL` | 乘法 | `MUL X0, X1, X2` | Xd = Xn * Xm |
| `SDIV` | 有符号除法 | `SDIV X0, X1, X2` | Xd = Xn / Xm (AArch64) |
| `AND` | 按位与 | `AND X0, X1, #0xFF` | Xd = Xn & imm |
| `ORR` | 按位或 | `ORR X0, X1, X2` | Xd = Xn \| Xm |
| `EOR` | 按位异或 | `EOR X0, X1, X2` | Xd = Xn ^ Xm |
| `LSL` | 左移 | `LSL X0, X1, #3` | Xd = Xn << count |
| `LSR` | 逻辑右移 | `LSR X0, X1, #3` | Xd = Xn >> count |
| `CMP` | 比较 | `CMP X0, #10` | 更新 NZCV 标志 |
| `TST` | 测试位 | `TST X0, #0x1` | 更新标志 (Xn & imm) |
| `B` | 跳转 | `B label` | 无条件跳转 |
| `BL` | 调用 | `BL func` | LR = PC+4; 跳转到 func |
| `B.EQ` | 条件跳转 | `B.EQ label` | Z=1 则跳 |
| `CBZ` | 零则跳 | `CBZ X0, label` | X0 == 0 则跳 (AArch64) |
| `CBNZ` | 非零则跳 | `CBNZ X0, label` | X0 != 0 则跳 (AArch64) |
| `RET` | 返回 | `RET` | 跳转到 LR (AArch64) |
| `BX LR` | 返回 | `BX LR` | 跳转到 LR (ARM32) |
| `CSEL` | 条件选择 | `CSEL X0, X1, X2, EQ` | X0 = EQ ? X1 : X2 (AArch64) |
| `ADRP` | 取页地址 | `ADRP X0, label` | X0 = 4KB 页地址 (AArch64) |
| `SVC` | 系统调用 | `SVC #0` | 触发系统调用 |

---

## Android 中的 x86

虽然 Android 设备绝大多数使用 ARM 处理器，但 x86 在 Android 生态中仍有重要存在。

### 为什么 Android 逆向工程师需要了解 x86？

1. **Android 模拟器**：官方 Android Emulator 使用 x86/x86-64 系统镜像以获得硬件虚拟化加速 (Intel HAXM / KVM)。在模拟器中分析应用时，native 代码可能是 x86 的。

2. **NDK 交叉编译**：使用 NDK 构建 native 库时，可以为 x86/x86-64 架构编译，方便在模拟器上调试。

3. **Translation Layer**：即使是 ARM-only 的 `.so`，在 x86 模拟器上也能通过 `libhoudini` (Intel 的 ARM 翻译层) 或 `libndk_translation` 运行，但行为可能有差异。

### 模拟器中的 x86 分析

当你在 x86 模拟器中分析一个 APK 时：

```text
APK 中的 native 库选择顺序:
1. lib/x86_64/libfoo.so     (如果模拟器是 x86_64 且存在此目录)
2. lib/x86/libfoo.so        (如果模拟器是 x86 且存在此目录)
3. lib/arm64-v8a/libfoo.so  (通过 ARM 翻译层运行)
4. lib/armeabi-v7a/libfoo.so (通过 ARM 翻译层运行)
```

> [!warning] 模拟器分析的陷阱
> - APK 包含 x86 `.so` 时，模拟器中的反汇编是 x86 指令而非 ARM
> - 某些应用会检测模拟器环境并拒绝运行
> - ARM 翻译层可能引入兼容性问题


### 分析技巧

分析 APK 时，检查 `lib/` 下的子文件夹 (`armeabi-v7a/`, `arm64-v8a/`, `x86/`, `x86_64/`) 判断支持哪些架构。

> [!tip] 逆向技巧：优先分析 x86 版本
> 如果 APK 同时提供 ARM 和 x86 版本的 `.so`，**有时可以优先分析 x86 版本**：
> 1. IDA 对 x86 的反编译质量最好
> 2. 可以在 PC 上直接运行和调试
> 3. 某些逻辑在 x86 版本中更清晰
>
> 注意：不同架构的编译结果可能有差异，尤其是涉及内联汇编或条件编译的代码。


---

## 实战：读懂反汇编

> **💡 思路一句话**: 读汇编不需要记住所有指令 — 关注三类：数据移动（MOV/LDR/STR）、算术运算（ADD/SUB/MUL/EOR）、控制流（B/BL/CBZ/RET），就能理解 90% 的反汇编代码。

下面通过一个完整的实例，演示如何从反汇编代码中还原出原始的 C 逻辑。

### 示例：一个简单的密码校验函数

假设我们在 IDA 中看到以下 AArch64 反汇编代码（这是一个简化的示例）：

```armasm
; bool check_password(const char* input, int length)
; X0 = input (const char*), W1 = length (int)

check_password:
    STP   X29, X30, [SP, #-48]!   ; 保存 FP, LR
    MOV   X29, SP                  ; 建立栈帧
    STP   X19, X20, [SP, #16]     ; 保存 callee-saved 寄存器
    STR   X21, [SP, #32]          ; 保存 X21

    MOV   X19, X0                  ; X19 = input (保存参数)
    MOV   W20, W1                  ; W20 = length

    ; 第一步：检查长度
    CMP   W20, #8                  ; length == 8?
    B.NE  .fail                    ; 如果长度不是 8，直接失败

    ; 第二步：逐字符校验
    MOV   W21, #0                  ; W21 = i = 0 (循环计数器)
    ADRP  X8, .secret_key@PAGE
    ADD   X8, X8, .secret_key@PAGEOFF ; X8 = secret_key 数组地址

.loop:
    CMP   W21, W20                 ; i < length?
    B.GE  .success                 ; 如果 i >= length，循环结束，密码正确

    LDRB  W9, [X19, X21]          ; W9 = input[i]
    LDRB  W10, [X8, X21]          ; W10 = secret_key[i]
    EOR   W9, W9, #0x37           ; W9 = input[i] ^ 0x37
    CMP   W9, W10                  ; input[i] ^ 0x37 == secret_key[i]?
    B.NE  .fail                    ; 不相等则失败

    ADD   W21, W21, #1             ; i++
    B     .loop                    ; 继续循环

.success:
    MOV   W0, #1                   ; 返回 true
    B     .epilogue

.fail:
    MOV   W0, #0                   ; 返回 false

.epilogue:
    LDR   X21, [SP, #32]          ; 恢复 X21
    LDP   X19, X20, [SP, #16]     ; 恢复 X19, X20
    LDP   X29, X30, [SP], #48     ; 恢复 FP, LR
    RET
```

### 逐步分析过程

**第一步：识别函数边界**

看到 `STP X29, X30, [SP, ...]!` 开头，`LDP X29, X30, [SP], ... ; RET` 结尾——这是标准的 AArch64 函数序言/结语。

**第二步：确定参数**

- `X0` -> 保存到 `X19`，后面用 `LDRB W9, [X19, X21]` 按字节加载——说明这是一个字符串指针
- `W1` -> 保存到 `W20`，与 `#8` 比较、作为循环上界——说明这是长度参数

**第三步：理解控制流**

1. `CMP W20, #8; B.NE .fail` -> 长度必须是 8
2. `.loop` 是一个 for 循环 (W21 从 0 开始，每次 +1，到 W20 结束)
3. 循环体内：加载 `input[i]`，异或 `0x37`，与 `secret_key[i]` 比较
4. 不匹配就跳到 `.fail` 返回 0

**第四步：还原 C 代码**

```c
// 还原后的 C 代码
static const unsigned char secret_key[8] = { /* ... */ };

bool check_password(const char* input, int length) {
    // 长度必须为 8
    if (length != 8) {
        return false;
    }

    // 逐字符校验: input[i] ^ 0x37 == secret_key[i]
    for (int i = 0; i < length; i++) {
        if ((input[i] ^ 0x37) != secret_key[i]) {
            return false;
        }
    }

    return true;
}
```

**第五步：提取密钥并破解**

知道了校验逻辑是 `input[i] ^ 0x37 == secret_key[i]`，正确密码就是 `secret_key[i] ^ 0x37`。用 Frida 提取：

```javascript
var base = Module.findBaseAddress("libfoo.so");
var key = base.add(0x1234).readByteArray(8); // 替换为实际偏移
var keyBytes = new Uint8Array(key);
var password = "";
for (var i = 0; i < 8; i++) {
    password += String.fromCharCode(keyBytes[i] ^ 0x37);
}
console.log("password:", password);
```

### 分析方法论总结

当你面对一段陌生的反汇编代码时，建议按以下步骤进行：

| 步骤 | 行动 | 关注点 |
| :--- | :--- | :----- |
| 1. 识别边界 | 找到函数序言和结语 | STP/LDP (A64) 或 PUSH/POP (ARM32) |
| 2. 确定接口 | 分析参数和返回值 | X0-X7 (参数), X0 (返回值), callee-saved 的使用 |
| 3. 画控制流 | 标记所有分支目标 | CMP + B.xx 组合, CBZ/CBNZ |
| 4. 识别模式 | 对应高级语言结构 | 循环 (递增+条件跳转回), if/else, switch |
| 5. 理解数据 | 追踪数据流向 | LDR/STR 对应哪些变量, 字符串引用, 常量 |
| 6. 动态验证 | 用 Frida/调试器确认 | hook 函数，打印参数和返回值 |

> [!tip] 善用反编译器
> IDA Pro (F5) 和 Ghidra 的反编译器可以直接将汇编代码转换为可读性很高的 C 伪代码。通常的工作流是：**先看伪代码理解大致逻辑，遇到不确定的地方再回头看汇编确认细节**。反编译器不是万能的，它可能错误地识别变量类型、合并/拆分函数，但作为起点它是非常高效的。
