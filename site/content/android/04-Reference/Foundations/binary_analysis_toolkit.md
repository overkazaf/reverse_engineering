---
title: "二进制分析工具链"
date: 2024-07-06
tags: ["Frida", "脱壳", "基础知识", "Hook", "Smali", "Android"]
weight: 10
---

# 二进制分析工具链

Unicorn、Capstone、Keystone 是现代二进制分析的三大基础框架，它们共同构成了许多高级工具（如 Unidbg、Qiling、Frida）的底层支撑。理解这些基础技术对于深入逆向工程至关重要。

---

## 目录

1. [工具链概览](#1-工具链概览)
2. [Unicorn - CPU 仿真引擎](#2-unicorn---cpu-仿真引擎)
3. [Capstone - 反汇编框架](#3-capstone---反汇编框架)
4. [Keystone - 汇编框架](#4-keystone---汇编框架)
5. [三者协同使用](#5-三者协同使用)
6. [实战案例](#6-实战案例)

---

## 1. 工具链概览

### 1.1 技术关系

```
┌─────────────────────────────────────────────────────────────────┐
│                    二进制分析工具链关系图                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                    ┌─────────────┐                              │
│                    │   源代码     │                              │
│                    └──────┬──────┘                              │
│                           │ 编译                                 │
│                           ↓                                      │
│                    ┌─────────────┐                              │
│            ┌───────│  机器码     │───────┐                      │
│            │       └─────────────┘       │                      │
│            │                             │                      │
│            ↓                             ↓                      │
│   ┌─────────────────┐          ┌─────────────────┐             │
│   │    Capstone     │          │    Unicorn      │             │
│   │   (反汇编器)     │          │  (CPU 仿真器)   │             │
│   │                 │          │                 │             │
│   │ 机器码 → 汇编码  │          │  执行机器码     │             │
│   └────────┬────────┘          └────────┬────────┘             │
│            │                             │                      │
│            ↓                             ↓                      │
│   ┌─────────────────┐          ┌─────────────────┐             │
│   │   汇编代码       │          │   执行结果      │             │
│   │   (可读形式)     │          │ (寄存器/内存)   │             │
│   └────────┬────────┘          └─────────────────┘             │
│            │                                                    │
│            ↓                                                    │
│   ┌─────────────────┐                                          │
│   │    Keystone     │                                          │
│   │   (汇编器)       │                                          │
│   │                 │                                          │
│   │ 汇编码 → 机器码  │                                          │
│   └─────────────────┘                                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 工具对比

| 工具 | 功能 | 输入 | 输出 | 典型用途 |
|------|------|------|------|----------|
| **Unicorn** | CPU 仿真 | 机器码 | 执行结果 | 模拟执行、脱壳、算法还原 |
| **Capstone** | 反汇编 | 机器码 | 汇编指令 | 代码分析、指令识别 |
| **Keystone** | 汇编 | 汇编指令 | 机器码 | Patch 生成、Shellcode 编写 |

### 1.3 支持的架构

| 架构 | Unicorn | Capstone | Keystone |
|------|---------|----------|----------|
| ARM | ✅ | ✅ | ✅ |
| ARM64 (AArch64) | ✅ | ✅ | ✅ |
| x86 | ✅ | ✅ | ✅ |
| x86-64 | ✅ | ✅ | ✅ |
| MIPS | ✅ | ✅ | ✅ |
| SPARC | ✅ | ✅ | ✅ |
| PowerPC | ✅ | ✅ | ✅ |
| M68K | ✅ | ✅ | ✅ |

### 1.4 安装

```bash
# Python 安装
pip install unicorn capstone keystone-engine

# 验证安装
python -c "import unicorn; print('Unicorn:', unicorn.__version__)"
python -c "import capstone; print('Capstone:', capstone.__version__)"
python -c "import keystone; print('Keystone: OK')"
```

---

## 2. Unicorn - CPU 仿真引擎

### 2.1 Unicorn 简介

Unicorn 是一个轻量级的多平台、多架构 CPU 仿真框架，基于 QEMU 开发。它只模拟 CPU 指令执行，不模拟操作系统或硬件设备。

**核心特点：**

- 纯 CPU 仿真，无系统调用支持
- 支持多种 CPU 架构
- 提供多种语言绑定（Python、C、Java、Go 等）
- 可设置 Hook 监控执行过程
- 内存映射完全可控

### 2.2 基础使用

```python
from unicorn import *
from unicorn.arm_const import *

# ARM 机器码: mov r0, #0x37
ARM_CODE = b"\x37\x00\xa0\xe3"

# 初始化 ARM 模式的 Unicorn 实例
mu = Uc(UC_ARCH_ARM, UC_MODE_ARM)

# 映射 2MB 内存用于代码执行
ADDRESS = 0x10000
mu.mem_map(ADDRESS, 2 * 1024 * 1024)

# 写入代码
mu.mem_write(ADDRESS, ARM_CODE)

# 设置初始寄存器值
mu.reg_write(UC_ARM_REG_R0, 0x0)

# 开始仿真执行
mu.emu_start(ADDRESS, ADDRESS + len(ARM_CODE))

# 读取执行结果
r0 = mu.reg_read(UC_ARM_REG_R0)
print(f"R0 = 0x{r0:x}")  # 输出: R0 = 0x37
```

### 2.3 ARM64 仿真示例

```python
from unicorn import *
from unicorn.arm64_const import *

# ARM64 机器码
# mov x0, #0x1234
# mov x1, #0x5678
# add x2, x0, x1
ARM64_CODE = bytes([
    0x80, 0x46, 0x82, 0xd2,  # mov x0, #0x1234
    0x01, 0xcf, 0x8a, 0xd2,  # mov x1, #0x5678
    0x02, 0x00, 0x01, 0x8b,  # add x2, x0, x1
])

def emulate_arm64():
    # 创建 ARM64 仿真器
    mu = Uc(UC_ARCH_ARM64, UC_MODE_ARM)

    # 映射内存
    ADDRESS = 0x10000
    STACK_ADDR = 0x80000
    STACK_SIZE = 0x10000

    mu.mem_map(ADDRESS, 2 * 1024 * 1024)
    mu.mem_map(STACK_ADDR, STACK_SIZE)

    # 写入代码
    mu.mem_write(ADDRESS, ARM64_CODE)

    # 设置栈指针
    mu.reg_write(UC_ARM64_REG_SP, STACK_ADDR + STACK_SIZE - 8)

    # 执行
    mu.emu_start(ADDRESS, ADDRESS + len(ARM64_CODE))

    # 读取结果
    x0 = mu.reg_read(UC_ARM64_REG_X0)
    x1 = mu.reg_read(UC_ARM64_REG_X1)
    x2 = mu.reg_read(UC_ARM64_REG_X2)

    print(f"X0 = 0x{x0:x}")  # 0x1234
    print(f"X1 = 0x{x1:x}")  # 0x5678
    print(f"X2 = 0x{x2:x}")  # 0x68ac (0x1234 + 0x5678)

emulate_arm64()
```

### 2.4 Hook 机制

Unicorn 提供多种 Hook 类型用于监控和控制执行：

```python
from unicorn import *
from unicorn.arm_const import *

# Hook 类型说明
# UC_HOOK_CODE      - 每条指令执行前
# UC_HOOK_BLOCK     - 每个基本块执行前
# UC_HOOK_MEM_READ  - 内存读取时
# UC_HOOK_MEM_WRITE - 内存写入时
# UC_HOOK_INTR      - 中断发生时

def hook_code(uc, address, size, user_data):
    """每条指令执行前的回调"""
    code = uc.mem_read(address, size)
    print(f"执行地址: 0x{address:x}, 指令大小: {size}, 字节: {code.hex()}")

def hook_block(uc, address, size, user_data):
    """每个基本块执行前的回调"""
    print(f"进入基本块: 0x{address:x}, 大小: {size}")

def hook_mem_access(uc, access, address, size, value, user_data):
    """内存访问回调"""
    if access == UC_MEM_WRITE:
        print(f"内存写入: 0x{address:x} = 0x{value:x} (大小: {size})")
    else:
        print(f"内存读取: 0x{address:x} (大小: {size})")

def hook_mem_invalid(uc, access, address, size, value, user_data):
    """无效内存访问回调"""
    print(f"无效内存访问: 0x{address:x}")
    # 可以动态映射内存来处理
    uc.mem_map(address & ~0xfff, 0x1000)
    return True  # 返回 True 继续执行

# 使用示例
mu = Uc(UC_ARCH_ARM, UC_MODE_ARM)

# 添加 Hook
mu.hook_add(UC_HOOK_CODE, hook_code)
mu.hook_add(UC_HOOK_BLOCK, hook_block)
mu.hook_add(UC_HOOK_MEM_READ | UC_HOOK_MEM_WRITE, hook_mem_access)
mu.hook_add(UC_HOOK_MEM_INVALID, hook_mem_invalid)
```

### 2.5 处理系统调用

Unicorn 不模拟系统调用，需要手动处理：

```python
from unicorn import *
from unicorn.arm_const import *

# ARM Linux 系统调用号
SYS_WRITE = 4
SYS_EXIT = 1

def hook_intr(uc, intno, user_data):
    """处理软中断 (syscall)"""
    if intno == 2:  # ARM SWI 中断
        # 获取系统调用号 (R7)
        syscall_num = uc.reg_read(UC_ARM_REG_R7)

        if syscall_num == SYS_WRITE:
            # write(fd, buf, count)
            fd = uc.reg_read(UC_ARM_REG_R0)
            buf = uc.reg_read(UC_ARM_REG_R1)
            count = uc.reg_read(UC_ARM_REG_R2)

            data = uc.mem_read(buf, count)
            print(f"[syscall] write({fd}, {data}, {count})")

            # 返回值
            uc.reg_write(UC_ARM_REG_R0, count)

        elif syscall_num == SYS_EXIT:
            exit_code = uc.reg_read(UC_ARM_REG_R0)
            print(f"[syscall] exit({exit_code})")
            uc.emu_stop()

mu = Uc(UC_ARCH_ARM, UC_MODE_ARM)
mu.hook_add(UC_HOOK_INTR, hook_intr)
```

---

## 3. Capstone - 反汇编框架

### 3.1 Capstone 简介

Capstone 是一个轻量级的多平台、多架构反汇编框架。它将机器码转换为人类可读的汇编指令，并提供丰富的指令信息。

**核心特点：**

- 支持多种架构
- 提供详细的指令信息（操作数、寄存器、内存访问等）
- 线程安全
- 支持多种语法风格（Intel/AT&T）

### 3.2 基础使用

```python
from capstone import *

# ARM 机器码
ARM_CODE = b"\x00\x00\xa0\xe3\x01\x10\xa0\xe3\x02\x20\x81\xe0"

# 创建 ARM 反汇编器
md = Cs(CS_ARCH_ARM, CS_MODE_ARM)

# 反汇编
print("ARM 反汇编结果:")
for insn in md.disasm(ARM_CODE, 0x1000):
    print(f"0x{insn.address:x}:\t{insn.mnemonic}\t{insn.op_str}")

# 输出:
# 0x1000: mov  r0, #0
# 0x1004: mov  r1, #1
# 0x1008: add  r2, r1, r2
```

### 3.3 ARM64 反汇编

```python
from capstone import *

# ARM64 机器码
ARM64_CODE = bytes([
    0xe0, 0x03, 0x00, 0xaa,  # mov x0, x0
    0x21, 0x00, 0x80, 0xd2,  # mov x1, #1
    0x42, 0x00, 0x01, 0x8b,  # add x2, x2, x1
    0xc0, 0x03, 0x5f, 0xd6,  # ret
])

# 创建 ARM64 反汇编器
md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)

print("ARM64 反汇编结果:")
for insn in md.disasm(ARM64_CODE, 0x1000):
    print(f"0x{insn.address:x}:\t{insn.mnemonic}\t{insn.op_str}")
```

### 3.4 详细指令信息

```python
from capstone import *
from capstone.arm64 import *

ARM64_CODE = b"\x21\x00\x80\xd2"  # mov x1, #1

md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
md.detail = True  # 启用详细模式

for insn in md.disasm(ARM64_CODE, 0x1000):
    print(f"指令: {insn.mnemonic} {insn.op_str}")
    print(f"指令 ID: {insn.id}")
    print(f"指令大小: {insn.size} 字节")
    print(f"指令字节: {insn.bytes.hex()}")

    # 操作数信息
    print(f"操作数数量: {len(insn.operands)}")
    for i, op in enumerate(insn.operands):
        if op.type == ARM64_OP_REG:
            print(f"  操作数 {i}: 寄存器 {insn.reg_name(op.reg)}")
        elif op.type == ARM64_OP_IMM:
            print(f"  操作数 {i}: 立即数 0x{op.imm:x}")
        elif op.type == ARM64_OP_MEM:
            print(f"  操作数 {i}: 内存 [base={insn.reg_name(op.mem.base)}]")

    # 读写的寄存器
    if insn.regs_read:
        print(f"读取寄存器: {[insn.reg_name(r) for r in insn.regs_read]}")
    if insn.regs_write:
        print(f"写入寄存器: {[insn.reg_name(r) for r in insn.regs_write]}")

    # 指令分组
    if insn.groups:
        print(f"指令组: {[insn.group_name(g) for g in insn.groups]}")
```

### 3.5 识别特定指令

```python
from capstone import *
from capstone.arm64 import *

def analyze_function(code, base_addr):
    """分析函数中的特定指令模式"""
    md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
    md.detail = True

    branches = []
    calls = []
    returns = []

    for insn in md.disasm(code, base_addr):
        # 检查是否为分支指令
        if ARM64_GRP_JUMP in insn.groups:
            branches.append((insn.address, insn.mnemonic, insn.op_str))

        # 检查是否为调用指令
        if ARM64_GRP_CALL in insn.groups:
            calls.append((insn.address, insn.mnemonic, insn.op_str))

        # 检查是否为返回指令
        if ARM64_GRP_RET in insn.groups:
            returns.append((insn.address, insn.mnemonic))

    print("分支指令:", branches)
    print("调用指令:", calls)
    print("返回指令:", returns)
```

### 3.6 x86/x64 反汇编

```python
from capstone import *

# x86 代码
X86_CODE = b"\x55\x48\x89\xe5\x48\x83\xec\x10"

# x86-64 模式
md = Cs(CS_ARCH_X86, CS_MODE_64)
md.syntax = CS_OPT_SYNTAX_INTEL  # 使用 Intel 语法

print("x86-64 反汇编 (Intel 语法):")
for insn in md.disasm(X86_CODE, 0x1000):
    print(f"0x{insn.address:x}:\t{insn.mnemonic}\t{insn.op_str}")

# 切换到 AT&T 语法
md.syntax = CS_OPT_SYNTAX_ATT
print("\nx86-64 反汇编 (AT&T 语法):")
for insn in md.disasm(X86_CODE, 0x1000):
    print(f"0x{insn.address:x}:\t{insn.mnemonic}\t{insn.op_str}")
```

---

## 4. Keystone - 汇编框架

### 4.1 Keystone 简介

Keystone 是 Capstone 的姊妹项目，功能相反：将汇编代码转换为机器码。它是编写 Shellcode、生成 Patch 的利器。

### 4.2 基础使用

```python
from keystone import *

# 创建 ARM 汇编器
ks = Ks(KS_ARCH_ARM, KS_MODE_ARM)

# 汇编代码
code = "mov r0, #0x37; mov r1, #0x48; add r2, r0, r1"
encoding, count = ks.asm(code)

print(f"汇编指令数: {count}")
print(f"机器码: {bytes(encoding).hex()}")
print(f"字节列表: {encoding}")
```

### 4.3 ARM64 汇编

```python
from keystone import *

# 创建 ARM64 汇编器
ks = Ks(KS_ARCH_ARM64, KS_MODE_LITTLE_ENDIAN)

# 汇编多行代码
asm_code = """
    mov x0, #0x1234
    mov x1, #0x5678
    add x2, x0, x1
    ret
"""

try:
    encoding, count = ks.asm(asm_code)
    print(f"成功汇编 {count} 条指令")
    print(f"机器码: {bytes(encoding).hex()}")

    # 格式化输出
    for i in range(0, len(encoding), 4):
        chunk = encoding[i:i+4]
        print(f"0x{i:04x}: {bytes(chunk).hex()}")

except KsError as e:
    print(f"汇编错误: {e}")
```

### 4.4 生成 Shellcode

```python
from keystone import *

def generate_arm64_shellcode():
    """生成 ARM64 execve("/bin/sh") shellcode"""
    ks = Ks(KS_ARCH_ARM64, KS_MODE_LITTLE_ENDIAN)

    shellcode_asm = """
        // execve("/bin/sh", NULL, NULL)
        mov x0, #0x622f          // "/b"
        movk x0, #0x6e69, lsl #16  // "in"
        movk x0, #0x732f, lsl #32  // "/s"
        movk x0, #0x68, lsl #48    // "h\x00"

        str x0, [sp, #-16]!      // 保存字符串到栈
        mov x0, sp               // x0 = 字符串地址
        mov x1, xzr              // x1 = NULL
        mov x2, xzr              // x2 = NULL
        mov x8, #221             // execve syscall number
        svc #0                   // 系统调用
    """

    try:
        encoding, count = ks.asm(shellcode_asm)
        print(f"Shellcode 长度: {len(encoding)} 字节")
        print(f"Shellcode: {bytes(encoding).hex()}")
        return bytes(encoding)
    except KsError as e:
        print(f"错误: {e}")
        return None

shellcode = generate_arm64_shellcode()
```

### 4.5 生成函数 Patch

```python
from keystone import *

def create_patch(arch, mode, original_addr, patch_asm):
    """创建二进制 Patch"""
    ks = Ks(arch, mode)

    # 处理地址相关指令
    encoding, count = ks.asm(patch_asm, original_addr)

    return bytes(encoding)

# 示例: 创建 ARM64 Patch
# 原始: cmp x0, #0; b.eq skip
# Patch: nop; nop (跳过检查)
patch = create_patch(
    KS_ARCH_ARM64,
    KS_MODE_LITTLE_ENDIAN,
    0x1000,
    "nop; nop"
)
print(f"Patch 字节: {patch.hex()}")
```

---

## 5. 三者协同使用

### 5.1 反汇编 → 修改 → 重新汇编

```python
from capstone import *
from keystone import *

def patch_instruction(code, addr, old_mnemonic, new_asm):
    """
    查找并替换特定指令

    参数:
        code: 原始机器码
        addr: 基地址
        old_mnemonic: 要替换的指令助记符
        new_asm: 新的汇编代码
    """
    # 反汇编查找目标指令
    md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
    ks = Ks(KS_ARCH_ARM64, KS_MODE_LITTLE_ENDIAN)

    patched = bytearray(code)

    for insn in md.disasm(code, addr):
        if insn.mnemonic == old_mnemonic:
            print(f"找到目标指令: 0x{insn.address:x}: {insn.mnemonic} {insn.op_str}")

            # 生成新指令
            new_bytes, _ = ks.asm(new_asm)

            # 确保长度匹配
            if len(new_bytes) != insn.size:
                print(f"警告: 新指令长度 ({len(new_bytes)}) != 原指令长度 ({insn.size})")
                # 使用 NOP 填充
                while len(new_bytes) < insn.size:
                    nop_bytes, _ = ks.asm("nop")
                    new_bytes.extend(nop_bytes)

            # 应用 Patch
            offset = insn.address - addr
            for i, b in enumerate(new_bytes[:insn.size]):
                patched[offset + i] = b

            print(f"Patch 完成: {bytes(new_bytes[:insn.size]).hex()}")

    return bytes(patched)

# 使用示例
original = bytes([
    0x1f, 0x00, 0x00, 0xf1,  # cmp x0, #0
    0x40, 0x00, 0x00, 0x54,  # b.eq +8
    0xe0, 0x03, 0x00, 0xaa,  # mov x0, x0
    0xc0, 0x03, 0x5f, 0xd6,  # ret
])

# 将 b.eq 替换为 nop
patched = patch_instruction(original, 0x1000, "b.eq", "nop")
print(f"\n原始: {original.hex()}")
print(f"修改: {patched.hex()}")
```

### 5.2 动态指令插桩

```python
from unicorn import *
from unicorn.arm64_const import *
from capstone import *
from keystone import *

class ARM64Instrumenter:
    """ARM64 指令插桩器"""

    def __init__(self):
        self.md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
        self.md.detail = True
        self.ks = Ks(KS_ARCH_ARM64, KS_MODE_LITTLE_ENDIAN)

        self.mu = Uc(UC_ARCH_ARM64, UC_MODE_ARM)

        # 内存布局
        self.CODE_ADDR = 0x10000
        self.STACK_ADDR = 0x80000
        self.mu.mem_map(self.CODE_ADDR, 0x10000)
        self.mu.mem_map(self.STACK_ADDR, 0x10000)
        self.mu.reg_write(UC_ARM64_REG_SP, self.STACK_ADDR + 0x8000)

        # 指令统计
        self.insn_count = 0
        self.branch_count = 0
        self.mem_access_count = 0

    def hook_code(self, uc, address, size, user_data):
        """指令级 Hook，使用 Capstone 分析"""
        code = uc.mem_read(address, size)

        for insn in self.md.disasm(bytes(code), address):
            self.insn_count += 1

            # 检测分支指令
            if CS_GRP_JUMP in insn.groups or CS_GRP_CALL in insn.groups:
                self.branch_count += 1
                print(f"[BRANCH] 0x{address:x}: {insn.mnemonic} {insn.op_str}")

    def run(self, code):
        """执行代码"""
        self.mu.mem_write(self.CODE_ADDR, code)
        self.mu.hook_add(UC_HOOK_CODE, self.hook_code)

        try:
            self.mu.emu_start(self.CODE_ADDR, self.CODE_ADDR + len(code))
        except UcError as e:
            print(f"仿真错误: {e}")

        print(f"\n执行统计:")
        print(f"  总指令数: {self.insn_count}")
        print(f"  分支指令: {self.branch_count}")

# 使用示例
instrumenter = ARM64Instrumenter()
test_code = bytes([
    0x00, 0x00, 0x80, 0xd2,  # mov x0, #0
    0x21, 0x00, 0x80, 0xd2,  # mov x1, #1
    0x1f, 0x00, 0x01, 0xeb,  # cmp x0, x1
    0x40, 0x00, 0x00, 0x54,  # b.eq +8
    0x00, 0x04, 0x00, 0x91,  # add x0, x0, #1
    0xc0, 0x03, 0x5f, 0xd6,  # ret
])
instrumenter.run(test_code)
```

### 5.3 控制流分析器

```python
from capstone import *
from capstone.arm64 import *

class CFGAnalyzer:
    """控制流图分析器"""

    def __init__(self):
        self.md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
        self.md.detail = True

    def analyze(self, code, base_addr):
        """分析代码的控制流"""
        blocks = {}
        current_block = []
        current_addr = base_addr

        for insn in self.md.disasm(code, base_addr):
            current_block.append(insn)

            # 检查是否为基本块结束
            is_branch = (ARM64_GRP_JUMP in insn.groups or
                        ARM64_GRP_CALL in insn.groups or
                        ARM64_GRP_RET in insn.groups)

            if is_branch:
                blocks[current_addr] = {
                    'instructions': current_block,
                    'start': current_addr,
                    'end': insn.address,
                    'type': self._get_block_type(insn),
                    'targets': self._get_targets(insn)
                }
                current_block = []
                current_addr = insn.address + insn.size

        # 最后一个块
        if current_block:
            blocks[current_addr] = {
                'instructions': current_block,
                'start': current_addr,
                'end': current_block[-1].address,
                'type': 'fall-through',
                'targets': []
            }

        return blocks

    def _get_block_type(self, insn):
        if ARM64_GRP_RET in insn.groups:
            return 'return'
        elif ARM64_GRP_CALL in insn.groups:
            return 'call'
        elif ARM64_GRP_JUMP in insn.groups:
            if insn.mnemonic.startswith('b.'):
                return 'conditional'
            return 'unconditional'
        return 'unknown'

    def _get_targets(self, insn):
        targets = []
        for op in insn.operands:
            if op.type == ARM64_OP_IMM:
                targets.append(op.imm)
        return targets

    def print_cfg(self, blocks):
        """打印控制流图"""
        print("=" * 50)
        print("控制流图分析结果")
        print("=" * 50)

        for addr, block in blocks.items():
            print(f"\n基本块 0x{addr:x} ({block['type']}):")
            print(f"  范围: 0x{block['start']:x} - 0x{block['end']:x}")

            for insn in block['instructions']:
                print(f"    0x{insn.address:x}: {insn.mnemonic} {insn.op_str}")

            if block['targets']:
                print(f"  跳转目标: {[hex(t) for t in block['targets']]}")

# 使用示例
analyzer = CFGAnalyzer()
test_code = bytes([
    0x1f, 0x00, 0x00, 0xf1,  # cmp x0, #0
    0x40, 0x00, 0x00, 0x54,  # b.eq 0x1010
    0x00, 0x04, 0x00, 0x91,  # add x0, x0, #1
    0x01, 0x00, 0x00, 0x14,  # b 0x1014
    0x00, 0x00, 0x80, 0xd2,  # mov x0, #0
    0xc0, 0x03, 0x5f, 0xd6,  # ret
])

blocks = analyzer.analyze(test_code, 0x1000)
analyzer.print_cfg(blocks)
```

---

## 6. 实战案例

### 6.1 案例: SO 函数仿真

```python
from unicorn import *
from unicorn.arm64_const import *
from capstone import *

class SOEmulator:
    """简单的 SO 函数仿真器"""

    def __init__(self):
        self.mu = Uc(UC_ARCH_ARM64, UC_MODE_ARM)
        self.md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)

        # 内存布局
        self.CODE_BASE = 0x10000
        self.DATA_BASE = 0x20000
        self.STACK_BASE = 0x80000

        self.mu.mem_map(self.CODE_BASE, 0x10000)
        self.mu.mem_map(self.DATA_BASE, 0x10000)
        self.mu.mem_map(self.STACK_BASE, 0x10000)

        self.mu.reg_write(UC_ARM64_REG_SP, self.STACK_BASE + 0x8000)

    def load_function(self, code, offset=0):
        """加载函数代码"""
        self.mu.mem_write(self.CODE_BASE + offset, code)
        return self.CODE_BASE + offset

    def call_function(self, addr, args=None):
        """调用函数"""
        # 设置参数 (x0-x7)
        if args:
            regs = [UC_ARM64_REG_X0, UC_ARM64_REG_X1, UC_ARM64_REG_X2,
                   UC_ARM64_REG_X3, UC_ARM64_REG_X4, UC_ARM64_REG_X5,
                   UC_ARM64_REG_X6, UC_ARM64_REG_X7]
            for i, arg in enumerate(args[:8]):
                self.mu.reg_write(regs[i], arg)

        # 设置返回地址
        ret_addr = 0xDEAD0000
        self.mu.mem_map(ret_addr & ~0xfff, 0x1000)
        self.mu.reg_write(UC_ARM64_REG_LR, ret_addr)

        # 执行
        try:
            self.mu.emu_start(addr, ret_addr)
        except UcError as e:
            if self.mu.reg_read(UC_ARM64_REG_PC) != ret_addr:
                raise e

        # 返回值 (x0)
        return self.mu.reg_read(UC_ARM64_REG_X0)

# 使用示例
emu = SOEmulator()

# 简单的加法函数: add_func(a, b) = a + b
add_func_code = bytes([
    0x00, 0x00, 0x01, 0x8b,  # add x0, x0, x1
    0xc0, 0x03, 0x5f, 0xd6,  # ret
])

func_addr = emu.load_function(add_func_code)
result = emu.call_function(func_addr, args=[100, 200])
print(f"add_func(100, 200) = {result}")  # 输出: 300
```

### 6.2 案例: 指令 Patch 工具

```python
from capstone import *
from keystone import *

class BinaryPatcher:
    """二进制 Patch 工具"""

    def __init__(self, arch='arm64'):
        if arch == 'arm64':
            self.md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
            self.ks = Ks(KS_ARCH_ARM64, KS_MODE_LITTLE_ENDIAN)
        elif arch == 'arm':
            self.md = Cs(CS_ARCH_ARM, CS_MODE_ARM)
            self.ks = Ks(KS_ARCH_ARM, KS_MODE_ARM)

        self.md.detail = True
        self.patches = []

    def find_pattern(self, code, base_addr, pattern):
        """查找指令模式"""
        results = []
        for insn in self.md.disasm(code, base_addr):
            if pattern in f"{insn.mnemonic} {insn.op_str}":
                results.append({
                    'address': insn.address,
                    'offset': insn.address - base_addr,
                    'size': insn.size,
                    'instruction': f"{insn.mnemonic} {insn.op_str}",
                    'bytes': insn.bytes.hex()
                })
        return results

    def create_nop_patch(self, size, arch='arm64'):
        """创建 NOP 填充"""
        if arch == 'arm64':
            nop = bytes([0x1f, 0x20, 0x03, 0xd5])  # nop
        else:
            nop = bytes([0x00, 0xf0, 0x20, 0xe3])  # nop (ARM)

        return nop * (size // 4)

    def patch_function_call(self, code, base_addr, target_func, return_value):
        """Patch 函数调用，直接返回指定值"""
        # 生成: mov x0, #return_value; ret
        patch_asm = f"mov x0, #{return_value}; ret"
        patch_bytes, _ = self.ks.asm(patch_asm)

        # 查找目标函数
        matches = self.find_pattern(code, base_addr, target_func)
        return matches, bytes(patch_bytes)

    def apply_patches(self, code, patches):
        """应用所有 Patch"""
        patched = bytearray(code)
        for p in patches:
            offset = p['offset']
            new_bytes = p['bytes']
            for i, b in enumerate(new_bytes):
                if offset + i < len(patched):
                    patched[offset + i] = b
        return bytes(patched)

# 使用示例
patcher = BinaryPatcher('arm64')

# 模拟一段检测 Root 的代码
sample_code = bytes([
    0xfd, 0x7b, 0xbf, 0xa9,  # stp x29, x30, [sp, #-16]!
    0xfd, 0x03, 0x00, 0x91,  # mov x29, sp
    0x00, 0x00, 0x00, 0x94,  # bl check_root (占位)
    0x1f, 0x00, 0x00, 0xf1,  # cmp x0, #0
    0x40, 0x00, 0x00, 0x54,  # b.eq not_rooted
    0x20, 0x00, 0x80, 0xd2,  # mov x0, #1 (rooted)
    0x00, 0x00, 0x00, 0x14,  # b exit
    0x00, 0x00, 0x80, 0xd2,  # mov x0, #0 (not rooted)
    0xfd, 0x7b, 0xc1, 0xa8,  # ldp x29, x30, [sp], #16
    0xc0, 0x03, 0x5f, 0xd6,  # ret
])

# 查找 bl 指令
calls = patcher.find_pattern(sample_code, 0x1000, 'bl')
print("找到的函数调用:")
for c in calls:
    print(f"  0x{c['address']:x}: {c['instruction']}")
```

---

## 总结

| 工具 | 核心功能 | 典型应用场景 |
|------|----------|--------------|
| **Unicorn** | CPU 指令仿真 | SO 函数仿真、算法还原、脱壳 |
| **Capstone** | 反汇编 | 代码分析、指令识别、CFG 构建 |
| **Keystone** | 汇编 | Patch 生成、Shellcode 编写 |

**学习建议：**

1. 先掌握 Capstone 反汇编，理解指令结构
2. 学习 Keystone 生成机器码，理解汇编过程
3. 使用 Unicorn 进行动态仿真，结合前两者进行分析
4. 进阶学习 Qiling/Unidbg 等高级框架

---

## 相关章节

- [T05: Unidbg 使用指南](../../02-Tools/Dynamic/unidbg_guide.md)
- [T06: Unidbg 内部原理](../../02-Tools/Dynamic/unidbg_internals.md)
- [A06: SO 运行时仿真](../Advanced/so_runtime_emulation.md)
- [F09: ARM 汇编入门](arm_assembly.md)
- [F10: x86 与 ARM 汇编基础](x86_and_arm_assembly_basics.md)
