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

> **💡 思路一句话**: 先用 IDA 判断混淆类型 → 再用 Frida Stalker 动态追踪真实执行路径（跳过所有虚假分支）→ 然后在 IDA 中标记真实块提取核心逻辑 → 最后用 Unicorn 模拟验证并编写等价 Python 代码。
>
> **核心原则**: 不要试图"读懂"混淆后的代码，而是让程序自己告诉你它真正执行了什么。

**目标**: `libnative.so` 中的 `encrypt` 函数，被 OLLVM `-fla -bcf -sub` 保护。

#### 环境准备

```bash
# 工具清单 (确保已安装)
# 1. IDA Pro 7.5+ (带 Hex-Rays ARM64 反编译器)
# 2. Frida 16.x
# 3. Python 3.8+ + frida-tools
# 4. 一台 root 过的 Android 设备 (推荐 Android 10-13)

# 检查 Frida 连接
adb devices                           # 确认设备连接
adb shell "su -c 'frida-server -D'"   # 后台启动 frida-server
frida-ps -U | head -20                # 验证 Frida 正常工作

# 从设备上拉取目标 SO
adb shell "pm path com.example.app"
adb pull /data/app/com.example.app-xxx/lib/arm64/libnative.so ./
```

#### Step 1: IDA 静态观察 — 判断混淆类型

```text
操作步骤:
1. 打开 IDA Pro，将 libnative.so 拖入
2. 等待自动分析完成 (进度条走完)
3. 在 Functions 窗口搜索 "encrypt" 或 "Java_com_example" 找到目标函数
4. 双击进入，按 F5 查看反编译结果
5. 按空格键切换到图形视图 (Graph View)
```

**你会看到什么 (判断依据):**

| 观察到的现象 | 含义 | 混淆类型 |
|-------------|------|---------|
| 巨大的 switch-case 循环，几十个 case | 所有基本块被打散重组 | 控制流平坦化 (FLA) |
| 图形视图中心有一个"太阳"节点，所有块指向它 | 这就是分发器 | FLA 分发器 |
| 大量的 `if` 判断但跟踪发现从不走某个分支 | 恒真/恒假条件 | 虚假控制流 (BCF) |
| `a + b` 写成 `(a ^ b) + 2 * (a & b)` | 等价但复杂的表达式 | 指令替换 (SUB) |

```python
# 在 IDA 中运行此脚本快速判断 (File → Script Command)
import idaapi
func = idaapi.get_func(idc.here())
blocks = list(idaapi.FlowChart(func))
print(f"[*] 基本块数量: {len(blocks)}")

# 计算入度
in_degree = {}
for b in blocks:
    for s in b.succs():
        in_degree[s.start_ea] = in_degree.get(s.start_ea, 0) + 1

if in_degree:
    disp_ea = max(in_degree, key=in_degree.get)
    disp_indeg = in_degree[disp_ea]
    print(f"[*] 入度最高的块: 0x{disp_ea:X} (入度={disp_indeg})")
    if disp_indeg > 5:
        print("[!] >>> 高度疑似控制流平坦化 <<<")
    if len(blocks) > 30:
        print("[!] >>> 基本块过多，疑似叠加虚假控制流 <<<")
```

**本例结果**: 函数有 47 个基本块，中心节点入度 38 → 判定为 **平坦化 + 虚假控制流 + 指令替换** 三件套。

#### Step 2: Frida Stalker 动态追踪 — 获取真实执行路径

> **为什么用动态追踪?** 静态分析 47 个块可能需要数小时，而动态追踪 1 秒钟就能告诉你程序真正执行了哪 10 个块。

```bash
# 保存以下脚本为 trace_encrypt.js
```

```javascript
// trace_encrypt.js — 追踪 encrypt 函数的真实执行路径
(function() {
    var soName = "libnative.so";
    var funcOffset = 0x12340;  // 从 IDA 中获取的函数偏移
    
    var mod = Process.findModuleByName(soName);
    if (!mod) {
        console.log("[-] 模块未加载，等待...");
        // 如果 SO 还没加载，等待加载
        Module.load(soName);
        mod = Process.findModuleByName(soName);
    }
    
    var base = mod.base;
    var target = base.add(funcOffset);
    var uniqueBlocks = {};
    var blockSequence = [];
    
    console.log("[*] SO base: " + base);
    console.log("[*] Target:  " + target);
    console.log("[*] 开始追踪...");
    
    Interceptor.attach(target, {
        onEnter: function(args) {
            console.log("[+] encrypt 被调用!");
            console.log("    参数0 (数据指针): " + args[0]);
            console.log("    参数1 (数据长度): " + args[1]);
            
            // 保存输入数据以便后续对比
            this.inputData = Memory.readByteArray(args[0], args[1].toInt32());
            
            this.tid = Process.getCurrentThreadId();
            Stalker.follow(this.tid, {
                transform: function(iterator) {
                    var inst = iterator.next();
                    do {
                        var addr = inst.address;
                        var off = addr.sub(base).toInt32();
                        
                        // 只记录目标函数范围内的指令
                        if (off >= funcOffset && off < funcOffset + 0x2000) {
                            iterator.putCallout(function(ctx) {
                                var pc = ctx.pc;
                                var offset = pc.sub(base).toInt32();
                                var hexOff = "0x" + offset.toString(16);
                                
                                if (!uniqueBlocks[hexOff]) {
                                    uniqueBlocks[hexOff] = 0;
                                }
                                uniqueBlocks[hexOff]++;
                                blockSequence.push(hexOff);
                            });
                        }
                        iterator.keep();
                    } while ((inst = iterator.next()) !== null);
                }
            });
        },
        onLeave: function(retval) {
            Stalker.unfollow(this.tid);
            Stalker.flush();
            
            // 打印结果
            console.log("\n========== 追踪结果 ==========");
            console.log("[+] 返回值: " + retval);
            console.log("[+] 唯一基本块数: " + Object.keys(uniqueBlocks).length);
            console.log("[+] 总指令数: " + blockSequence.length);
            
            console.log("\n[+] 真实执行的基本块 (按执行顺序):");
            var seen = {};
            blockSequence.forEach(function(off) {
                if (!seen[off]) {
                    seen[off] = true;
                    console.log("    " + off + " (执行 " + uniqueBlocks[off] + " 次)");
                }
            });
            
            // 输出为可直接粘贴到 IDAPython 的格式
            console.log("\n[+] IDAPython 标记代码:");
            console.log("REAL_BLOCKS = [" + 
                Object.keys(uniqueBlocks).join(", ") + "]");
        }
    });
})();
```

```bash
# 运行追踪
frida -U -f com.example.app -l trace_encrypt.js --no-pause

# 预期输出:
# [*] SO base: 0x70a0000000
# [*] Target:  0x70a0012340
# [+] encrypt 被调用!
#     参数0 (数据指针): 0x7ff0001000
#     参数1 (数据长度): 0x10
#
# ========== 追踪结果 ==========
# [+] 返回值: 0x7ff0001000
# [+] 唯一基本块数: 10
# [+] 总指令数: 847
#
# [+] 真实执行的基本块 (按执行顺序):
#     0x12340 (执行 1 次)    ← 函数入口
#     0x12358 (执行 1 次)    ← 初始化
#     0x1239C (执行 16 次)   ← 循环体 (处理 16 字节)
#     0x123E0 (执行 16 次)   ← XOR 操作
#     0x12428 (执行 4 次)    ← 字节翻转 (每4字节一组)
#     0x12460 (执行 4 次)    ← 翻转操作
#     0x124A8 (执行 16 次)   ← 循环判断
#     0x124F0 (执行 4 次)    ← 外层循环判断
#     0x12538 (执行 1 次)    ← 收尾
#     0x12580 (执行 1 次)    ← 返回
#
# 关键发现: 47 个块中只有 10 个被真正执行!
# 其余 37 个块都是 OLLVM 插入的垃圾!
```

> **小白提示**: 如果 `frida -U -f` 启动闪退，改用 `frida -U com.example.app -l trace_encrypt.js`（先手动打开App再附加）。如果报 `Module not found`，说明 SO 是延迟加载的，在 App 中触发对应功能后再运行。

#### Step 3: IDAPython 标记真实块

回到 IDA Pro，把追踪到的真实块标记出来：

```python
# 在 IDA 中运行 (File → Script Command → Python)

# 把 Frida 输出的偏移粘贴到这里
REAL_BLOCKS = [0x12340, 0x12358, 0x1239C, 0x123E0, 0x12428,
               0x12460, 0x124A8, 0x124F0, 0x12538, 0x12580]

# SO 在 IDA 中的基址 (看 IDA 左上角的地址)
SO_BASE = 0x0  # IDA 中 SO 通常从 0x0 开始加载

# 标记真实块为绿色，添加注释
for i, off in enumerate(REAL_BLOCKS):
    addr = SO_BASE + off
    # 设置背景色为绿色
    idc.set_color(addr, idc.CIC_ITEM, 0xC0FFC0)
    # 添加注释
    idc.set_cmt(addr, f"=== REAL_BLOCK_{i} ===", 0)
    print(f"[+] 标记 REAL_BLOCK_{i} @ 0x{addr:X}")

# 标记完成后，在图形视图中：
# - 绿色块 = 真实执行的代码
# - 白色块 = OLLVM 垃圾代码
print(f"\n[*] 标记完成! {len(REAL_BLOCKS)} 个真实块")
print("[*] 现在切换到 Graph View (空格键) 查看")
print("[*] 绿色 = 真实代码, 白色 = 垃圾代码")
```

**标记后你会看到**: 图形视图中绿色块清晰地串联成一条主线，白色块散落四周 — 这就是算法的真实骨架。

#### Step 4: 逐块分析核心逻辑

现在只需要阅读 10 个绿色块（而不是 47 个）：

```text
REAL_BLOCK_0 (0x12340): 函数序言，保存寄存器
REAL_BLOCK_1 (0x12358): 加载参数 (数据指针→X19, 长度→W20), 初始化循环计数器 i=0
REAL_BLOCK_2 (0x1239C): 循环开始, 加载 data[i], 加载 key[i%4]
REAL_BLOCK_3 (0x123E0): XOR 操作: data[i] ^= key[i % 4]  ← 关键!
REAL_BLOCK_4 (0x12428): 字节翻转开始, 加载 data[j] 和 data[j+3]
REAL_BLOCK_5 (0x12460): 交换: data[j]↔data[j+3], data[j+1]↔data[j+2]  ← 关键!
REAL_BLOCK_6 (0x124A8): 循环递增 i++, 判断 i < len
REAL_BLOCK_7 (0x124F0): 外层循环递增 j+=4, 判断 j < len-3
REAL_BLOCK_8 (0x12538): 收尾处理
REAL_BLOCK_9 (0x12580): 恢复寄存器, 返回
```

> **如何阅读混淆后的汇编**: 即使在真实块中，指令替换 (SUB) 也会让 `ADD` 变成 `(a^b)+2*(a&b)` 之类。不要被吓到，关注 **数据流**（哪个寄存器的值流向了哪里），而不是指令本身。

#### Step 5: Unicorn 模拟验证

```python
# verify_encrypt.py — 验证还原的算法是否正确
from unicorn import *
from unicorn.arm64_const import *

# 1. 读取 SO 文件
with open("libnative.so", "rb") as f:
    so_data = f.read()

# 2. 模拟执行原始混淆函数
BASE = 0x10000
STACK = 0x80000
DATA_ADDR = 0x90000

mu = Uc(UC_ARCH_ARM64, UC_MODE_LITTLE_ENDIAN)
mu.mem_map(BASE, 0x100000)
mu.mem_write(BASE, so_data)
mu.mem_map(STACK, 0x10000)
mu.mem_map(DATA_ADDR, 0x1000)

# 准备测试数据
test_input = b"Hello World!1234"
mu.mem_write(DATA_ADDR, test_input)

# 设置寄存器
mu.reg_write(UC_ARM64_REG_SP, STACK + 0xF000)
mu.reg_write(UC_ARM64_REG_X0, DATA_ADDR)          # 参数1: 数据指针
mu.reg_write(UC_ARM64_REG_X1, len(test_input))     # 参数2: 长度
mu.reg_write(UC_ARM64_REG_LR, 0xDEAD0000)          # 返回地址

END_ADDR = 0xDEAD0000
mu.mem_map(END_ADDR & ~0xFFF, 0x1000)

try:
    mu.emu_start(BASE + 0x12340, END_ADDR, timeout=10_000_000)
except UcError as e:
    print(f"[!] 模拟异常: {e}")

original_result = bytes(mu.mem_read(DATA_ADDR, len(test_input)))
print(f"[+] 原始函数输出: {original_result.hex()}")

# 3. 用还原的 Python 算法计算
def recovered_encrypt(data: bytes, key=b"\x5A\xA5\x3C\xC3") -> bytes:
    """还原出的算法: 循环 XOR + 字节翻转"""
    r = bytearray(data)
    for i in range(len(r)):           # Round 1: XOR
        r[i] ^= key[i % len(key)]
    for i in range(0, len(r)-3, 4):   # Round 2: 字节翻转
        r[i], r[i+3] = r[i+3], r[i]
        r[i+1], r[i+2] = r[i+2], r[i+1]
    return bytes(r)

python_result = recovered_encrypt(test_input)
print(f"[+] Python 算法输出: {python_result.hex()}")

# 4. 对比验证
if original_result == python_result:
    print("\n[✓] 验证通过! 还原算法正确!")
else:
    print("\n[✗] 不匹配! 需要继续调试")
    # 逐字节对比找出差异
    for i in range(len(original_result)):
        if original_result[i] != python_result[i]:
            print(f"    字节 {i}: 原始={original_result[i]:02x} vs Python={python_result[i]:02x}")
```

```bash
# 运行验证
python3 verify_encrypt.py

# 预期输出:
# [+] 原始函数输出: c3a59b8e...
# [+] Python 算法输出: c3a59b8e...
# [✓] 验证通过! 还原算法正确!
```

#### 完整流程总结

```text
┌──────────────────────────────────────────────────────────────────┐
│  OLLVM 反混淆五步法 (从看不懂到完全还原)                          │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Step 1  IDA 观察           "这个函数被什么方式混淆了？"          │
│    │     打开SO → F5反编译 → 图形视图 → 判断混淆类型              │
│    ↓                                                             │
│  Step 2  Frida 动态追踪     "程序真正执行了哪些代码？"            │
│    │     Stalker追踪 → 记录执行的基本块 → 过滤掉垃圾块            │
│    ↓                                                             │
│  Step 3  IDAPython 标记     "把真实代码高亮出来"                  │
│    │     将追踪结果导入IDA → 绿色标记真实块 → 白色即垃圾           │
│    ↓                                                             │
│  Step 4  逐块分析           "这10个块在做什么运算？"              │
│    │     只读绿色块 → 关注数据流 → 提炼算法逻辑                   │
│    ↓                                                             │
│  Step 5  验证还原           "我的理解对不对？"                    │
│          Unicorn模拟 → 对比输出 → 编写等价Python代码              │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

> **常见踩坑**:
> - Stalker 在 Android 8 以下可能不稳定 → 升级 Frida 版本或换设备
> - Unicorn 模拟 SO 时缺少依赖函数 → 需要 hook 外部调用返回固定值
> - XOR 密钥可能是动态生成的 → 需要先 hook 密钥生成函数获取密钥
> - 函数有多个入口点 → 确认从 Java 层调用的具体路径

---

## deflat 自动化反平坦化工具

deflat 是目前最成熟的 OLLVM 控制流平坦化自动还原工具，基于 angr 符号执行引擎。

### 安装与配置

```bash
# 1. 安装 angr (建议使用虚拟环境)
python3 -m venv deflat_env
source deflat_env/bin/activate
pip install angr

# 2. 克隆 deflat
git clone https://github.com/cq674350529/deflat.git
cd deflat/flat_control_flow
```

### 基本用法

```bash
# 反平坦化指定函数
# -f: SO 文件路径
# --addr: 目标函数地址 (IDA 中看到的地址)
python deflat.py -f libtarget.so --addr 0x12340

# 指定架构 (默认自动检测)
python deflat.py -f libtarget.so --addr 0x12340 --arch aarch64
```

### 工作原理

```text
deflat 反平坦化流程:

1. 加载二进制 → angr.Project
2. 构建 CFG → 识别函数基本块
3. 识别分发器 → 入度最高的基本块
4. 识别序言块 → 函数入口到分发器之间的块
5. 识别真实块 → 非分发器、非序言的功能块
6. 符号执行每个真实块 → 确定后继状态值
7. 重建真实的控制流 → patch 二进制
```

### 实战示例：反平坦化加密函数

```python
# 手动使用 deflat 核心逻辑 (当自动模式失败时)
import angr
import struct

def manual_deflat(so_path, func_addr, state_var_offset):
    """
    手动反平坦化 - 当自动检测失败时使用
    
    Args:
        so_path: SO 文件路径
        func_addr: 函数起始地址
        state_var_offset: 状态变量在栈上的偏移
    """
    proj = angr.Project(so_path, auto_load_libs=False)
    cfg = proj.analyses.CFGFast(normalize=True)
    func = cfg.functions.get(func_addr)
    
    # 步骤 1: 识别分发器
    blocks = list(func.blocks)
    in_degrees = {}
    for node in func.graph.nodes():
        in_degrees[node] = func.graph.in_degree(node)
    
    dispatcher = max(in_degrees, key=in_degrees.get)
    print(f"[+] 分发器: 0x{dispatcher.addr:x} (入度: {in_degrees[dispatcher]})")
    
    # 步骤 2: 识别真实块 (后继包含分发器的块)
    real_blocks = []
    for node in func.graph.nodes():
        succs = list(func.graph.successors(node))
        if dispatcher in succs and node != dispatcher:
            real_blocks.append(node)
    
    print(f"[+] 真实块数量: {len(real_blocks)}")
    
    # 步骤 3: 对每个真实块符号执行，确定后继
    transitions = {}
    for block in real_blocks:
        state = proj.factory.blank_state(addr=block.addr)
        simgr = proj.factory.simulation_manager(state)
        
        # 执行到分发器
        simgr.explore(find=dispatcher.addr)
        
        if simgr.found:
            found_state = simgr.found[0]
            # 读取状态变量的值
            sp = found_state.regs.sp
            state_val = found_state.solver.eval(
                found_state.memory.load(sp + state_var_offset, 4, endness='Iend_LE')
            )
            transitions[block.addr] = state_val
            print(f"  0x{block.addr:x} → state=0x{state_val:x}")
    
    # 步骤 4: 建立状态值到块地址的映射
    state_to_block = {}
    for block in real_blocks:
        # 通过分发器的比较值确定映射
        pass  # 需要分析分发器的 CMP 指令
    
    # 步骤 5: 重建控制流
    print("\n[+] 恢复的控制流:")
    for src_addr, next_state in transitions.items():
        if next_state in state_to_block:
            dst_addr = state_to_block[next_state]
            print(f"  0x{src_addr:x} → 0x{dst_addr:x}")
    
    return transitions
```

### 常见问题与解决

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| `Symbolic execution timeout` | 函数过大或路径爆炸 | 增加超时: `state.options.add(angr.options.LAZY_SOLVES)` |
| `Cannot identify dispatcher` | 非标准平坦化实现 | 手动指定分发器地址 |
| `Wrong number of real blocks` | 嵌套分发器 (Hikari) | 分层处理，先反外层再反内层 |
| `Patch verification failed` | 跳转距离超过指令范围 | 使用 trampoline 跳板 |
| `ARM64 branch range exceeded` | B 指令范围 ±128MB | 改用 ADRP+ADD+BR 间接跳转 |

---

## IDA Microcode API 反混淆实战

IDA 7.1+ 引入了 Hex-Rays Microcode API，允许在反编译器的中间表示层面进行优化。这比在汇编层面操作更高效，因为 Microcode 已经进行了寄存器分配和基本优化。

### Microcode 层次结构

```text
IDA Microcode 处理流水线:
  
  汇编 → Microcode (初始) → 优化 Pass 1-7 → Microcode (优化后) → C 伪代码
                              ↑
                              在这里插入自定义优化
```

### MBA 表达式简化插件

```python
import ida_hexrays as hr
import ida_idaapi

class MBASimplifier(hr.optinsn_t):
    """IDA Microcode 优化器: 简化 MBA 表达式"""
    
    def func(self, blk, ins, optflags):
        """
        在每个 microcode 指令上调用
        返回非零值表示进行了修改
        """
        # 模式: (a & b) + (a | b) => a + b
        if ins.opcode == hr.m_add:
            if (ins.l.is_insn(hr.m_and) and ins.r.is_insn(hr.m_or)):
                and_ins = ins.l.d
                or_ins = ins.r.d
                
                # 检查操作数是否相同
                if (and_ins.l.equal_mops(or_ins.l, hr.EQ_IGNSIZE) and
                    and_ins.r.equal_mops(or_ins.r, hr.EQ_IGNSIZE)):
                    # 简化为 a + b
                    ins.l.swap(and_ins.l)
                    ins.r.swap(and_ins.r)
                    return 1  # 已修改
        
        # 模式: (a ^ b) + 2*(a & b) => a + b
        if ins.opcode == hr.m_add:
            if ins.l.is_insn(hr.m_xor) and ins.r.is_insn(hr.m_mul):
                xor_ins = ins.l.d
                mul_ins = ins.r.d
                
                # 检查乘数是否为 2
                if (mul_ins.l.is_insn(hr.m_and) and
                    mul_ins.r.is_number() and mul_ins.r.value(False) == 2):
                    and_ins = mul_ins.l.d
                    
                    if (xor_ins.l.equal_mops(and_ins.l, hr.EQ_IGNSIZE) and
                        xor_ins.r.equal_mops(and_ins.r, hr.EQ_IGNSIZE)):
                        ins.l.swap(xor_ins.l)
                        ins.r.swap(xor_ins.r)
                        return 1
        
        return 0  # 未修改

# 安装优化器
optimizer = MBASimplifier()
optimizer.install()
print("[+] MBA Simplifier installed")
```

### 不透明谓词消除插件

```python
class OpaquePredicateRemover(hr.optinsn_t):
    """消除 OLLVM 不透明谓词"""
    
    # 已知的恒真/恒假模式
    ALWAYS_TRUE = [
        # (x * (x+1)) % 2 == 0
        # (x | 1) != 0
    ]
    
    def func(self, blk, ins, optflags):
        # 检测 if (x*x % 2 == 1) 模式 (恒假)
        if ins.opcode == hr.m_jcnd:
            cond = ins.l
            if self.is_always_false(cond):
                # 将条件跳转改为 NOP
                ins.opcode = hr.m_nop
                return 1
            elif self.is_always_true(cond):
                # 将条件跳转改为无条件跳转
                ins.opcode = hr.m_goto
                return 1
        return 0
    
    def is_always_false(self, mop):
        """检测恒假条件"""
        # 实现具体的模式匹配逻辑
        return False
    
    def is_always_true(self, mop):
        """检测恒真条件"""
        return False
```

### d810 插件使用指南

d810 是基于 IDA Microcode API 的成熟反混淆框架：

```bash
# 安装 d810
git clone https://github.com/joydo/d810.git
# 将 d810 目录复制到 IDA plugins 目录
# Windows: %APPDATA%/Hex-Rays/IDA Pro/plugins/
# macOS: ~/Library/Application Support/Hex-Rays/IDA Pro/plugins/
# Linux: ~/.idapro/plugins/
```

使用步骤:
1. IDA 中打开目标 SO → Edit → Plugins → D-810
2. 选择目标函数 → 右键 → "Deobfuscate with d810"
3. 选择规则集:
   - `default`: 通用 MBA 简化 + 不透明谓词消除
   - `ollvm`: 针对 OLLVM 优化的规则集
   - `custom`: 自定义规则

```python
# d810 自定义规则示例
# 文件: d810/rules/custom_ollvm.py

from d810.optimizers.instructions import GenericPatternRule

class SimplifyANDOR(GenericPatternRule):
    """
    Rule: (x & y) + (x | y) => x + y
    Targets MBA obfuscation in Hikari/Armariris
    """
    PATTERN = "m_add(m_and(x, y), m_or(x, y))"
    REPLACEMENT = "m_add(x, y)"
    DESCRIPTION = "Simplify MBA: (x&y)+(x|y) -> x+y"
```

---

## Frida 动态追踪进阶：算法还原完整流程

> **💡 思路一句话**: 不要试图硬读 OLLVM 代码 — 让 Frida Stalker 追踪真实执行路径，用多组不同输入对比找出数据依赖的关键指令，最后根据这些关键指令逆推算法逻辑。

当面对重度 OLLVM 混淆时，动态追踪是最高效的方法。以下是从追踪到算法还原的完整工作流。

**环境准备清单:**

```bash
# 必需工具
pip install frida-tools          # Frida Python 绑定
adb shell "su -c 'frida-server -D'"  # 确保 frida-server 运行

# 验证连接
frida-ps -U | grep -i target_app   # 确认目标进程存在
```

### 步骤 1: 确定目标函数

```javascript
// 通过 JNI 函数注册表找到 native 函数地址
Java.perform(function() {
    var targetClass = Java.use("com.example.app.SignHelper");
    // Hook Java 层调用，获取参数和返回值
    targetClass.getSign.implementation = function(data) {
        console.log("[+] Input: " + data);
        var result = this.getSign(data);
        console.log("[+] Output: " + result);
        
        // 获取 native 函数地址
        var symbols = Module.enumerateExportsSync("libnative.so");
        symbols.forEach(function(sym) {
            if (sym.name.indexOf("getSign") !== -1 || 
                sym.name.indexOf("Java_com_example") !== -1) {
                console.log("[+] Native func: " + sym.name + " @ " + sym.address);
            }
        });
        
        return result;
    };
});
```

### 步骤 2: Stalker 指令级追踪

```javascript
function traceNativeAlgorithm(soName, funcOffset) {
    var mod = Process.findModuleByName(soName);
    var funcAddr = mod.base.add(funcOffset);
    var trace = [];
    var regSnapshots = [];
    
    Interceptor.attach(funcAddr, {
        onEnter: function(args) {
            console.log("[+] Args: X0=" + args[0] + " X1=" + args[1] + " X2=" + args[2]);
            this.tid = Process.getCurrentThreadId();
            
            Stalker.follow(this.tid, {
                transform: function(iterator) {
                    var inst;
                    while ((inst = iterator.next()) !== null) {
                        var addr = inst.address;
                        var offset = addr.sub(mod.base).toInt32();
                        
                        // 只追踪目标函数范围内的指令
                        if (offset >= funcOffset && offset < funcOffset + 0x5000) {
                            // 在关键算术指令处记录寄存器状态
                            if (['add', 'sub', 'mul', 'eor', 'and', 'orr', 'lsl', 'lsr', 'ror'].indexOf(inst.mnemonic) !== -1) {
                                iterator.putCallout(function(ctx) {
                                    trace.push({
                                        offset: ctx.pc.sub(mod.base).toInt32(),
                                        mnemonic: Instruction.parse(ctx.pc).mnemonic,
                                        opStr: Instruction.parse(ctx.pc).opStr,
                                        x0: ctx.x0.toInt32(),
                                        x1: ctx.x1.toInt32(),
                                        x8: ctx.x8.toInt32(),
                                    });
                                });
                            }
                        }
                        iterator.keep();
                    }
                }
            });
        },
        onLeave: function(retval) {
            Stalker.unfollow(this.tid);
            Stalker.flush();
            
            console.log("[+] Trace length: " + trace.length);
            // 输出算术操作序列
            trace.forEach(function(t) {
                console.log("  0x" + t.offset.toString(16) + ": " + 
                           t.mnemonic + " " + t.opStr + 
                           "  // X0=" + t.x0 + " X1=" + t.x1);
            });
            
            send({type: "trace", data: trace});
        }
    });
}
```

### 步骤 3: 多输入对比分析

```python
# Python 端收集多组追踪数据，对比分析
import frida
import json

class AlgorithmRecovery:
    def __init__(self, so_name, func_offset):
        self.so_name = so_name
        self.func_offset = func_offset
        self.traces = []
    
    def collect_traces(self, device, package, inputs):
        """收集多组输入对应的执行追踪"""
        session = device.attach(package)
        # ... 注入脚本，收集trace
        
    def diff_traces(self, trace_a, trace_b):
        """对比两条追踪，找到数据依赖的关键指令"""
        key_instructions = []
        for i in range(min(len(trace_a), len(trace_b))):
            a, b = trace_a[i], trace_b[i]
            if a['offset'] == b['offset']:
                # 同一条指令，但寄存器值不同 → 数据依赖
                if a['x0'] != b['x0'] or a['x1'] != b['x1']:
                    key_instructions.append({
                        'offset': a['offset'],
                        'mnemonic': a['mnemonic'],
                        'is_data_dependent': True
                    })
        return key_instructions
    
    def reconstruct_algorithm(self, key_instructions):
        """根据关键指令重建算法"""
        ops = []
        for inst in key_instructions:
            if inst['mnemonic'] == 'eor':
                ops.append('XOR')
            elif inst['mnemonic'] == 'add':
                ops.append('ADD')
            elif inst['mnemonic'] in ['lsl', 'lsr', 'ror']:
                ops.append(f'SHIFT({inst["mnemonic"]})')
            # ...
        
        print("[+] 算法操作序列:", " → ".join(ops))
        return ops
```

### 步骤 4: 生成等价 Python 实现

```python
def generate_python_equivalent(trace, known_io_pairs):
    """
    根据追踪结果和已知输入输出生成等价 Python 代码
    
    实战技巧：
    1. 先用简单输入 (如 0x00000001) 追踪，观察常量
    2. 再用全 FF 输入，观察位运算行为
    3. 用递增输入 (1,2,3...) 确认线性关系
    """
    # 从 trace 中提取核心操作
    core_ops = [t for t in trace if t.get('is_data_dependent')]
    
    code = "def sign(data: bytes) -> int:\n"
    code += "    # 从 OLLVM 混淆函数还原\n"
    code += "    result = int.from_bytes(data[:4], 'little')\n"
    
    for op in core_ops:
        if op['mnemonic'] == 'eor':
            code += f"    result ^= 0x{op.get('constant', 0):08X}\n"
        elif op['mnemonic'] == 'add':
            code += f"    result = (result + 0x{op.get('constant', 0):08X}) & 0xFFFFFFFF\n"
        elif op['mnemonic'] == 'ror':
            code += f"    result = ror32(result, {op.get('shift', 0)})\n"
    
    code += "    return result\n"
    
    # 用已知 IO 对验证
    for inp, expected_out in known_io_pairs:
        actual = eval(f"sign({inp})")
        status = "pass" if actual == expected_out else "FAIL"
        print(f"  {status} sign({inp}) = {actual:#x} (expected: {expected_out:#x})")
    
    return code
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
