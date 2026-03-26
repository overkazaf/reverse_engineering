---
title: "SO 文件反混淆：花指令识别与自动化去除"
date: 2025-02-13
type: posts
tags: ["Ghidra", "加固", "脱壳", "OLLVM", "Android", "反混淆", "VMP", "Unicorn", "angr"]
weight: 10
---

# SO 文件反混淆：花指令识别与自动化去除

> **📚 前置知识**
>
> 本配方涉及以下核心技术，建议先阅读相关章节：
>
> - **[SO/ELF 格式](../../04-Reference/Foundations/so_elf_format.md)** - 理解 ELF 段结构与指令布局
> - **[IDA Pro 指南](../../02-Tools/Static/ida_pro_guide.md)** - 使用 IDAPython 编写脚本
> - **[ARM 汇编基础](../../04-Reference/Foundations/arm_assembly.md)** - 阅读反汇编代码的能力

在 Android SO 文件逆向工程中，**代码混淆 (Code Obfuscation)**，俗称"花指令"，是开发者为了保护核心逻辑、增加逆向分析难度而采用的一种常用技术。其核心思想是在代码中插入大量对程序本身逻辑无用但能迷惑反汇编工具和分析人员的指令。

本指南将系统介绍 SO 混淆的完整技术分类、识别方法，并重点阐述如何利用 `IDAPython`、`Frida`、`Unicorn`、`angr` 等工具进行自动化反混淆。

---

## 目录

- [SO 混淆技术分类](#so-混淆技术分类)
- [花指令的核心类型](#花指令的核心类型)
- [OLLVM 混淆详解](#ollvm-混淆详解)
- [反反汇编技巧](#反反汇编技巧)
- [代码虚拟化 (VMP)](#代码虚拟化-vmp)
- [如何识别花指令](#如何识别花指令)
- [静态去混淆](#静态去混淆)
- [动态去混淆](#动态去混淆)
- [自动化去花脚本 (IDAPython 实战)](#自动化去花脚本-idapython-实战)
- [Unicorn 辅助分析](#unicorn-辅助分析)
- [实战案例](#实战案例)

---

## SO 混淆技术分类

Android Native 层常见的混淆技术可归纳为以下几大类，往往组合使用以最大化保护效果：

| 分类 | 技术 | 难度 | 典型工具/来源 | 核心思路 |
|------|------|:----:|--------------|----------|
| **指令级** | 垃圾指令 (Junk Code) | 低 | 手写/脚本 | 插入不影响逻辑的无用指令 |
| **指令级** | 指令替换 (SUB) | 低 | OLLVM `-sub` | 等价但更复杂的指令序列 |
| **控制流** | 不透明谓词 (BCF) | 中 | OLLVM `-bcf` | 恒真/恒假分支迷惑分析器 |
| **控制流** | 控制流平坦化 (CFF) | 高 | OLLVM `-fla` | 分发器循环编排执行顺序 |
| **控制流** | 反反汇编 | 中 | 手写 | 利用反汇编器缺陷产生错误输出 |
| **语义级** | 代码虚拟化 (VMP) | 极高 | VMProtect/自研 | 原生指令转自定义字节码 |
| **链接级** | 符号剥离+字符串加密 | 低 | strip/自研 | 去除调试信息，加密常量 |

```text
混淆技术层次图:

┌─────────────────────────────────────────┐
│              语义级混淆                  │
│   ┌────────────────┐ ┌──────────────┐  │
│   │ 代码虚拟化(VMP) │ │ MBA混合表达式│  │
│   └────────────────┘ └──────────────┘  │
├─────────────────────────────────────────┤
│              控制流混淆                  │
│   ┌────────┐ ┌────────┐ ┌──────────┐  │
│   │ 平坦化 │ │不透明谓│ │ 反反汇编 │  │
│   └────────┘ └────────┘ └──────────┘  │
├─────────────────────────────────────────┤
│              指令级混淆                  │
│   ┌──────────┐  ┌──────────────────┐   │
│   │ 垃圾指令 │  │    指令替换      │   │
│   └──────────┘  └──────────────────┘   │
└─────────────────────────────────────────┘
         ↑ 复杂度递增 / 逆向难度递增 ↑
```

> **实战经验**: 商业级保护方案通常同时启用 OLLVM 三件套 (CFF + BCF + SUB) 并叠加字符串加密和符号剥离。

---

## 花指令的核心类型

### 垃圾指令 (Junk Code)

最简单的混淆形式。在真实指令之间插入不影响程序状态的指令。

```assembly
; 真实代码
PUSH EAX
; --- 垃圾代码 ---
NOP
MOV EBX, EBX
XCHG ECX, ECX
ADD EAX, 0
; --- 垃圾代码结束 ---
; 真实代码
POP EAX
```

### 不透明谓词 (Opaque Predicates)

构造**条件恒成立或恒不成立**的分支，使反汇编器误以为存在多个执行路径。

```assembly
MOV EAX, EDX
XOR EAX, EDX     ; 清零 EAX
TEST EAX, EAX    ; 设置 Z 标志
JZ real_code_path ; 始终跳转
; --- 死代码 (JNZ 分支) ---
ADD EAX, 1234
CALL some_fake_func
; --- 死代码结束 ---
real_code_path:
; ... 真实代码
```

### 控制流平坦化 (Control Flow Flattening)

将函数的正常逻辑块打散，使用中央分发器和 `switch-case` 结构控制执行流。

```text
原始代码:                平坦化后:
A → B → C → D                ┌──────────────┐
                              │  Dispatcher  │
                              └──────────────┘
                               ↓   ↓   ↓   ↓
                              [A] [B] [C] [D]
                               └───┴───┴───┘
                                   ↓
                              返回 Dispatcher
```

---

## OLLVM 混淆详解

OLLVM 在 LLVM IR 层面操作，提供三种核心混淆 pass。以下通过 before/after 对比展示效果。

### 控制流平坦化 (`-fla`)

**混淆前**：

```c
int check(int x) {
    int result = 0;
    if (x > 10) result = x * 2;
    else         result = x + 5;
    return result;
}
```

**混淆后** -- 所有块由 switch 分发器控制：

```c
int check(int x) {
    int state = 0xA3B1;
    int result;
    while (1) {
        switch (state) {
        case 0xA3B1: state = (x > 10) ? 0x7F02 : 0xD4E8; break;
        case 0x7F02: result = x * 2;  state = 0x91AC; break;
        case 0xD4E8: result = x + 5;  state = 0x91AC; break;
        case 0x91AC: return result;
        }
    }
}
```

### 虚假控制流 (`-bcf`)

插入基于不透明谓词的虚假分支，常见数学恒等式：

| 表达式 | 恒等结果 | 数学原理 |
|--------|----------|----------|
| `x*(x+1) % 2` | 恒为 0 | 连续整数之积必为偶数 |
| `x*x % 2 == 1` | 恒假 | 平方数模 2 只能是 0 |
| `(x^3 - x) % 6` | 恒为 0 | 费马小定理推论 |

### 指令替换 (`-sub`)

| 原始指令 | 替换后 | 等价原理 |
|----------|--------|----------|
| `a + b` | `a - (-b)` | 减负数等于加 |
| `a + b` | `(a ^ b) + 2*(a & b)` | 半加器公式 |
| `a - b` | `a + (~b) + 1` | 补码减法 |
| `a ^ b` | `(a \| b) & (~a \| ~b)` | 异或布尔展开 |

---

## 反反汇编技巧

利用反汇编器的解析缺陷，使其产生错误输出。

### 重叠指令 (Overlapping Instructions)

利用 x86 变长指令的特性，跳转到另一条指令的中间位置：

```assembly
; 线性扫描反汇编器看到的 (错误):
0x00: EB 01        JMP SHORT 0x03
0x02: E8 B8 01 00  CALL 0x1BE      ; 从 0x02 解析 -- 错!
; 真实执行路径 (JMP 跳到 0x03):
0x00: EB 01        JMP SHORT 0x03
0x03: B8 01 00 00  MOV EAX, ...    ; 从 0x03 才是正确指令
```

```text
字节流:  EB 01 E8 B8 01 00 00 C3
              ↑
              JMP 跳过 E8 (CALL 操作码)
              反汇编器被骗，从 E8 开始解析
```

### 基于异常的控制流

利用信号/异常处理隐藏真实执行路径：

```c
signal(SIGTRAP, real_handler);  // 注册处理函数
void obfuscated_func() {
    __asm__ __volatile__("int3"); // 触发 SIGTRAP -> real_handler
    fake_decrypt();               // 死代码，静态分析器不知道
}
void real_handler(int sig) {
    real_decrypt();               // 真实逻辑
}
```

### 滥用 CALL + 栈操作

```assembly
CALL next_insn        ; 压入返回地址
next_insn:
ADD  DWORD [ESP], 5   ; 修改返回地址 += 5
RET                   ; 跳到 next_insn + 5 (跳过垃圾字节)
DB 0xE8, 0xFF, 0xC0, 0x48, 0x83  ; 5 字节垃圾
real_code:            ; 真实代码从这里继续
```

---

## 代码虚拟化 (VMP)

代码虚拟化将原生指令翻译为自定义字节码，运行时通过嵌入的 VM 解释器执行。

```text
┌───────────────────────────────────────────┐
│  VM_Entry ──> Dispatcher (主循环)          │
│               opcode = fetch()            │
│               switch (opcode):            │
│                 0x01: vMOV  (虚拟传送)    │
│                 0x02: vADD  (虚拟加法)    │
│                 0x03: vXOR  (虚拟异或)    │
│                 0x04: vLOAD (虚拟内存读)  │
│                 0x05: vCMP  (虚拟比较)    │
│                 0xFF: VM_Exit             │
│                                           │
│  VM Context: VPC + VREG[0..15] + VSTACK   │
└───────────────────────────────────────────┘
```

**VMP 分析流程**: 定位 VM_Entry -> 识别 Dispatcher -> 分析每个 Handler 语义 -> dump 字节码 -> 编写反汇编器 -> 重建逻辑

```c
// 简化的 VMP Dispatcher
void vm_execute(uint8_t *bytecode, vm_context_t *ctx) {
    ctx->vpc = 0;
    while (1) {
        uint8_t op = bytecode[ctx->vpc++];
        switch (op) {
        case 0x01:  // vMOV reg, imm32
            ctx->regs[bytecode[ctx->vpc++]] = *(uint32_t*)&bytecode[ctx->vpc];
            ctx->vpc += 4; break;
        case 0x02:  // vADD reg1, reg2
            ctx->regs[bytecode[ctx->vpc]] += ctx->regs[bytecode[ctx->vpc+1]];
            ctx->vpc += 2; break;
        case 0xFF: return;  // vRET
        }
    }
}
```

---

## 如何识别花指令

### 静态分析特征

在 IDA Pro 或 Ghidra 中观察：

- **无效跳转**：`JMP loc_A` 的下一条指令就是 `loc_A`
- **跳转到指令中间**：`JMP $+5` 跳到正常指令中间
- **对称操作**：连续的 `PUSH`/`POP` 同一寄存器
- **恒成立条件**：`Jcc` 前 `CMP` 两个操作数明显相等
- **IDA 图形视图**：平坦化函数呈巨大 `switch` 结构，所有块指向中心分发块

### 动态调试验证

- 在可疑分支下断点，未命中则为死代码
- 单步观察寄存器变化，无变化则为垃圾代码

---

## 静态去混淆

### 符号执行 (angr)

```python
import angr

def deflat_with_angr(binary_path, func_addr):
    """使用 angr 识别平坦化结构"""
    proj = angr.Project(binary_path, auto_load_libs=False)
    cfg = proj.analyses.CFGFast(normalize=True)
    func = cfg.functions.get(func_addr)

    # 找分发器 -- 入度最高的基本块
    block_in_degrees = {n: func.graph.in_degree(n) for n in func.graph.nodes()}
    dispatcher = max(block_in_degrees, key=block_in_degrees.get)
    print(f"[+] 分发器: 0x{dispatcher.addr:x}, 入度: {block_in_degrees[dispatcher]}")

    # 真实块 = 跳回分发器的块
    real_blocks = [n for n in func.graph.nodes()
                   if dispatcher in func.graph.successors(n) and n != dispatcher]
    print(f"[+] 真实基本块: {len(real_blocks)}")
    return dispatcher, real_blocks
```

### 模式匹配 (Miasm)

```python
from miasm.analysis.machine import Machine
from miasm.expression.simplifications import expr_simp

def simplify_with_miasm(binary_path, func_addr):
    """使用 Miasm IR 简化混淆后的表达式"""
    machine = Machine("aarch64l")
    cont = machine.Container.from_stream(open(binary_path, "rb"), addr=func_addr)
    mdis = machine.dis_engine(cont.bin_stream, loc_db=cont.loc_db)
    asmcfg = mdis.dis_multiblock(func_addr)
    lifter = machine.lifter_model_call(mdis.loc_db)
    ircfg = lifter.new_ircfg_from_asmcfg(asmcfg)

    for lbl, irblock in ircfg.blocks.items():
        for assignblk in irblock:
            for dst, src in assignblk.items():
                simplified = expr_simp(src)
                if simplified != src:
                    print(f"  简化: {src} => {simplified}")
```

### Z3 求解不透明谓词

```python
from z3 import *

def batch_solve_predicates(predicates):
    """批量判断谓词是否为死代码。predicates: [(地址, lambda), ...]"""
    x = BitVec('x', 32)
    for addr, pred in predicates:
        s = Solver()
        s.set("timeout", 5000)
        s.add(pred(x))
        r = s.check()
        status = "恒假(死代码)" if r == unsat else f"可满足(x={s.model()[x]})" if r == sat else "未知"
        print(f"  0x{addr:04x}: {status}")

# 示例
batch_solve_predicates([
    (0x1000, lambda x: URem(x * x, 2) == 1),
    (0x1020, lambda x: URem(x * (x + 1), 2) != 0),
])
```

---

## 动态去混淆

### Frida Stalker 指令追踪

```javascript
// frida_trace_ollvm.js -- 追踪 OLLVM 函数的真实执行路径
function traceFunc(moduleName, funcOffset) {
    var base = Module.findBaseAddress(moduleName);
    var target = base.add(funcOffset);
    var realBlocks = [];

    Interceptor.attach(target, {
        onEnter: function(args) {
            this.tid = Process.getCurrentThreadId();
            Stalker.follow(this.tid, {
                transform: function(iterator) {
                    var inst = iterator.next();
                    var addr = inst.address;
                    var off = addr.sub(base).toInt32();
                    if (off >= funcOffset && off < funcOffset + 0x2000) {
                        iterator.putCallout(function(ctx) {
                            send({type: "block", offset: "0x" + off.toString(16)});
                        });
                    }
                    do { iterator.keep(); } while ((inst = iterator.next()) !== null);
                }
            });
        },
        onLeave: function(retval) {
            Stalker.unfollow(this.tid);
            Stalker.flush();
            send({type: "done", retval: retval.toString()});
        }
    });
}
traceFunc("libtarget.so", 0x1234);
```

### 执行路径对比

通过提供不同输入并对比路径差异，识别关键分支点：

```python
def diff_paths(trace_a, trace_b):
    """对比两条执行路径，找出分歧点"""
    for i in range(min(len(trace_a), len(trace_b))):
        if trace_a[i] != trace_b[i]:
            print(f"[+] 分歧点 #{i}: A=0x{trace_a[i]:x} vs B=0x{trace_b[i]:x}")
            print(f"    前一公共块: 0x{trace_a[i-1]:x}")
            return i
    return None
```

---

## 自动化去花脚本 (IDAPython 实战)

### 场景一：NOP 掉无效跳转

```python
import idaapi, idc, idautils

def patch_junk_jumps():
    """将 JMP next_instruction 形式的垃圾跳转 NOP 掉"""
    count = 0
    for seg_ea in idautils.Segments():
        if idc.get_segm_attr(seg_ea, idc.SEGATTR_TYPE) != idc.SEG_CODE:
            continue
        for head in idautils.Heads(idc.get_segm_start(seg_ea), idc.get_segm_end(seg_ea)):
            if idaapi.is_jmp_insn(head):
                target = idc.get_operand_value(head, 0)
                insn_len = idc.get_item_size(head)
                if target == head + insn_len:
                    for i in range(insn_len):
                        idc.patch_byte(head + i, 0x90)
                    count += 1
    print(f"修补了 {count} 个垃圾跳转")

patch_junk_jumps()
```

### 场景二：识别并去除不透明谓词

```python
import idc, idautils

def patch_opaque_predicates():
    """去除 CMP reg,reg + JNE 形式的不透明谓词"""
    count = 0
    for seg_ea in idautils.Segments():
        if idc.get_segm_attr(seg_ea, idc.SEGATTR_TYPE) != idc.SEG_CODE:
            continue
        for head in idautils.Heads(idc.get_segm_start(seg_ea), idc.get_segm_end(seg_ea)):
            if idc.get_byte(head) == 0x75:  # JNE
                prev = idc.prev_head(head)
                if idc.print_insn_mnem(prev) == "cmp":
                    if idc.get_operand_value(prev, 0) == idc.get_operand_value(prev, 1):
                        insn_len = idc.get_item_size(head)
                        for i in range(insn_len):
                            idc.patch_byte(head + i, 0x90)
                        count += 1
    print(f"修补了 {count} 个不透明谓词")

patch_opaque_predicates()
```

### 场景三：修复重叠指令

```python
import idc, idaapi

def fix_overlapping_instructions(start, end):
    """修复 JMP 到指令中间导致的反汇编错误"""
    count = 0
    cur = start
    while cur < end:
        insn = idaapi.insn_t()
        length = idaapi.decode_insn(insn, cur)
        if length == 0:
            cur += 1; continue
        if idc.get_byte(cur) == 0xEB:  # short JMP
            offset = idc.get_byte(cur + 1)
            if offset > 0x7F: offset -= 0x100
            target = cur + 2 + offset
            prev = idc.prev_head(target)
            if prev != idc.BADADDR and prev < target < prev + idc.get_item_size(prev):
                for i in range(cur, target):
                    idc.patch_byte(i, 0x90)
                idc.create_insn(target)
                count += 1
        cur += length
    print(f"修复了 {count} 处重叠指令")
    idaapi.plan_and_wait(start, end)
```

### 场景四：平坦化结构分析辅助

```python
import idaapi, idautils, idc

def analyze_flattened(func_addr):
    """分析疑似被平坦化的函数，输出结构信息"""
    func = idaapi.get_func(func_addr)
    blocks = list(idaapi.FlowChart(func))
    print(f"[*] 函数 @ 0x{func.start_ea:X}, 基本块: {len(blocks)}")

    in_degree = {}
    for b in blocks:
        for s in b.succs():
            in_degree[s.start_ea] = in_degree.get(s.start_ea, 0) + 1

    if in_degree:
        disp = max(in_degree, key=in_degree.get)
        print(f"    疑似分发器: 0x{disp:X} (入度={in_degree[disp]})")
        if in_degree[disp] > 5:
            print("    [!] 高度疑似控制流平坦化!")
        # 统计跳回分发器的块
        back_count = sum(1 for b in blocks if any(s.start_ea == disp for s in b.succs()))
        print(f"    跳回分发器的块: {back_count}")
```

---

## Unicorn 辅助分析

Unicorn 可脱离设备模拟执行函数片段，特别适合验证混淆算法逻辑。

```python
from unicorn import *
from unicorn.arm64_const import *

def emulate_func(so_bytes, func_offset, arg0, arg1):
    """用 Unicorn 模拟 ARM64 混淆函数，返回 (返回值, 执行轨迹)"""
    BASE, STACK = 0x10000, 0x80000
    mu = Uc(UC_ARCH_ARM64, UC_MODE_LITTLE_ENDIAN)
    code_size = (len(so_bytes) + 0xFFF) & ~0xFFF
    mu.mem_map(BASE, code_size)
    mu.mem_write(BASE, so_bytes)
    mu.mem_map(STACK, 0x10000)
    mu.reg_write(UC_ARM64_REG_SP, STACK + 0xF000)
    mu.reg_write(UC_ARM64_REG_X0, arg0)
    mu.reg_write(UC_ARM64_REG_X1, arg1)

    END = 0xDEAD0000
    mu.mem_map(END & ~0xFFF, 0x1000)
    mu.reg_write(UC_ARM64_REG_LR, END)

    trace = []
    mu.hook_add(UC_HOOK_CODE, lambda uc, addr, sz, _: trace.append(addr))

    try:
        mu.emu_start(BASE + func_offset, END, timeout=10_000_000)
    except UcError as e:
        print(f"[!] 异常: {e}, PC=0x{mu.reg_read(UC_ARM64_REG_PC):x}")

    ret = mu.reg_read(UC_ARM64_REG_X0)
    print(f"[+] f(0x{arg0:x}, 0x{arg1:x}) = 0x{ret:x}  ({len(trace)} 条指令)")
    return ret, trace
```

**批量测试输入输出** -- 辅助算法还原：

```python
def batch_test(so_bytes, func_offset, cases):
    """批量测试 [(arg0,arg1), ...], 打印 IO 关系表"""
    print(f"{'Input0':>12}  {'Input1':>12}  {'Output':>12}")
    print(f"{'─'*12}  {'─'*12}  {'─'*12}")
    for a0, a1 in cases:
        ret, _ = emulate_func(so_bytes, func_offset, a0, a1)
        print(f"{a0:>12x}  {a1:>12x}  {ret:>12x}")
```

---

## 实战案例

### 反混淆 OLLVM 保护的加密函数 (完整流程)

**目标**: `libnative.so` 中的 `encrypt` 函数，被 OLLVM `-fla -bcf -sub` 保护。

**Step 1 -- IDA 观察**: 函数有 47 个基本块，入度 38 的中心节点 -> 判定为平坦化 + 虚假控制流。

**Step 2 -- Frida 追踪真实路径** (见上方 Stalker 脚本)，得到真实执行的 10 个基本块偏移。

**Step 3 -- IDAPython 标记**:

```python
REAL_BLOCKS = [0x12340, 0x12358, 0x1239C, 0x123E0, 0x12428,
               0x12460, 0x124A8, 0x124F0, 0x12538, 0x12580]

for i, off in enumerate(REAL_BLOCKS):
    addr = 0x70000000 + off  # SO 基址
    idc.set_color(addr, idc.CIC_ITEM, 0xC0FFC0)  # 绿色标记
    idc.set_cmt(addr, f"REAL_BLOCK_{i}", 0)
```

**Step 4 -- Unicorn 验证**: 模拟执行并对比 Frida hook 获取的真实输出。

**Step 5 -- 算法还原**:

```python
def recovered_encrypt(data: bytes, key=b"\x5A\xA5\x3C\xC3") -> bytes:
    """还原出的算法: 循环 XOR + 字节翻转"""
    r = bytearray(data)
    for i in range(len(r)):           # Round 1: XOR
        r[i] ^= key[i % len(key)]
    for i in range(0, len(r)-3, 4):   # Round 2: 字节翻转
        r[i], r[i+3] = r[i+3], r[i]
        r[i+1], r[i+2] = r[i+2], r[i+1]
    return bytes(r)
```

**完整流程**:

```text
IDA 观察 ──> Frida Stalker 追踪 ──> IDAPython 标记
   判断混淆类型     获取真实路径          提取真实块
                                            │
验证还原算法 <── Unicorn 模拟 <─────────────┘
编写等价代码       确认算法逻辑
```

---

## 通用去花流程

1. **观察**：在 IDA Pro 中观察可疑代码的模式
2. **识别**：找到该模式的通用机器码或指令特征
3. **编码**：编写脚本，精确地定位这些特征并进行修复 (Patch)

虽然花指令的变种层出不穷，但其本质是有限的。掌握了自动化的脚本去花能力，就能极大地提升 SO 文件逆向分析的效率。

---

## 相关链接

### 相关配方

- [OLLVM 反混淆](../Analysis/ollvm_deobfuscation.md) - 处理控制流平坦化 (Z3/Angr 深入)
- [应用脱壳总览](./un-packing.md) - 脱壳后再去花

### 工具深入

- [IDA Pro 使用指南](../../02-Tools/Static/ida_pro_guide.md)
- [Ghidra 使用指南](../../02-Tools/Static/ghidra_guide.md)

---

**💡 提示**: 去花是一个需要耐心和经验的过程。建议先手动分析几个样本，理解混淆模式后再编写脚本自动化处理。面对高强度混淆 (如 VMP)，动态分析往往比纯静态分析更高效。
