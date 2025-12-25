---
title: "OLLVM 反混淆"
date: 2024-11-05
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

!!! warning "场景导入：当你遇到 OLLVM"
打开 IDA，反编译一个函数，结果看到：

- 一个巨大的 `switch-case` 循环，有几十甚至上百个 case 分支
- 每个 case 里只有几行代码，然后又跳回 switch
- 到处都是看起来有用实际无用的 `if` 判断
- 简单的加法被替换成了 `a = b - (-c)` 这样的怪异表达式

**你的第一反应可能是：这是什么鬼？**

恭喜，你遇到了 OLLVM 控制流平坦化 (FLA) + 虚假控制流 (BCF) + 指令替换 (SUB) 的"三件套"。
这是目前 Android Native 层最常见的商业级混淆方案。

**关键问题**：面对这种混淆，是选择"硬看"代码，还是有更聪明的办法？

本文档涵盖了常见的 OLLVM 混淆通道 (pass) 及其分析和逆向策略。

---

## 核心混淆技术

OLLVM 的主要优势在于其三种核心混淆技术：

1. **控制流平坦化 (`-fla`)**: 该技术会彻底平坦化一个函数的控制流。它通过将所有基本块放入一个单一的、巨大的分发器循环（"主分发器"）中来隐藏原始的程序流程。一个状态变量用于控制下一个要执行的代码块。逆向此技术需要重建原始的控制流图 (CFG)。

2. **虚假控制流 (`-bcf`)**: 该技术在代码中插入无效的条件分支和不透明谓词。这些分支被设计为静态分析难以解析，但在运行时，它们总是会得出相同的结果。这会给控制流图增加大量的噪声。

3. **指令替换 (`-sub`)**: 这是最简单的混淆方式。它将标准的二进制运算符（如 `add`, `sub`, `and`, `or`）替换为功能上等价但更复杂的指令序列。例如，`a = b + c` 可能会变成 `a = b - (-c)`。

---

## 分析与反混淆策略

!!! question "思考：静态分析 vs 动态分析，哪个更有效？"
面对 OLLVM 混淆，有两种完全不同的思路：

**静态分析**：

- ✅ 优势：能看到所有可能的执行路径，包括错误处理分支
- ❌ 劣势：需要对抗大量的虚假分支，分析工作量巨大
- 适用场景：你需要理解完整的算法逻辑，或者寻找漏洞

**动态分析**：

- ✅ 优势：直接记录真实执行路径，绕过所有虚假分支
- ❌ 劣势：只能看到当前输入下的执行路径，可能遗漏关键分支
- 适用场景：你只想提取算法结果（如加密签名），不关心内部逻辑

**实战建议**：

1. 先用动态分析（Frida Stalker / Unidbg trace）快速获取"真实"的执行流
2. 再用静态分析验证和补充动态分析遗漏的部分
3. 如果目标是自动化（如算法还原），考虑符号执行（Angr）

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

以下是一个完整的实战示例，展示如何结合 Z3 和 Angr 分析一个被 OLLVM 混淆的签名函数：

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
