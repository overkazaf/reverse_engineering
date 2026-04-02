---
title: "Radare2 入门"
date: 2024-06-29
type: posts
tags: ["静态分析", "Ghidra", "IDA", "Android", "IDA Pro"]
weight: 10
---

# Radare2 入门

Radare2 (通常简称为 r2) 是一款开源、免费、命令行驱动的逆向工程框架。它不仅仅是一个反汇编器，更像是一个功能极其丰富的"瑞士军刀"，集成了十六进制编辑、反汇编、调试、代码分析、漏洞利用、数据可视化等多种功能。Radare2 以其高度的可脚本化和可扩展性而闻名，深受寻求自动化和深度定制的黑客、CTF 选手和安全研究员的喜爱。

## 核心理念与特性

### 命令行驱动

Radare2 的所有核心功能都通过命令行接口暴露。这使得它非常适合在终端、SSH 会话或脚本中运行，易于实现自动化。

### 模块化设计

其功能由一系列单字母命令和子命令构成，例如 `p` 用于打印 (print)，`a` 用于分析 (analyze)，`d` 用于调试 (debug)。这种设计遵循了 Unix 哲学。

### 海量架构支持

Radare2 支持数量惊人的处理器架构，包括许多非常小众和古老的嵌入式架构，这方面甚至超过了 IDA Pro。

### 高度可脚本化

你可以使用任何你喜欢的语言（Python, Go, JavaScript, Rust 等）通过 r2pipe 与 Radare2 实例进行交互，实现复杂的自动化分析流程。

### 内置调试器

集成了功能强大的多平台调试器，支持硬件断点、跟踪等高级功能。

### 强大的二进制文件解析

不仅支持 ELF, PE, Mach-O 等标准格式，还能解析文件系统、图片、文档等各种二进制 blob。

---

## Radare2 vs. IDA Pro vs. Ghidra

| 特性         | Radare2                    | IDA Pro                | Ghidra                         |
| ------------ | -------------------------- | ---------------------- | ------------------------------ |
| **价格**     | **完全免费**               | 非常昂贵               | 完全免费                       |
| **开源**     | **是 (C)**                 | 否                     | 是 (Java)                      |
| **核心优势** | **极致的脚本化和命令行**   | 最强的交互式反汇编     | 高质量的免费反编译器           |
| **UI**       | **命令行** (或 Cutter GUI) | Qt，业界标准，成熟稳定 | Java Swing，功能强大但略显笨重 |
| **学习曲线** | **非常陡峭**               | 中等                   | 中等                           |
| **自动化**   | **设计哲学核心，能力极强** | 主要通过 IDC/IDAPython | 强大的 Headless 模式           |
| **灵活性**   | **最高**，一切皆可定制     | 较低，依赖插件         | 较高，可通过插件扩展           |

---

## 安装与基础命令

### 安装方式

#### 从源码编译（推荐）

最推荐的安装方式是通过 `git` 克隆官方仓库并运行安装脚本：

```bash
git clone https://github.com/radareorg/radare2
cd radare2
sys/install.sh
```

#### 通过包管理器安装

```bash
# macOS (Homebrew)
brew install radare2

# Debian/Ubuntu
sudo apt install radare2

# Arch Linux
sudo pacman -S radare2

# Windows (scoop)
scoop install radare2
```

#### 验证安装

```bash
$ r2 -v
radare2 5.9.6 0 @ linux-x86-64
commit: HEAD build: 2024-06-15
```

### 启动与退出

```bash
# 以分析模式打开文件（-A 等同于启动后执行 aaa）
r2 -A /bin/ls

# 以调试模式打开文件
r2 -d /bin/ls

# 以只读模式打开（不会修改原文件）
r2 -n /path/to/binary

# 以写模式打开（允许 patch）
r2 -w /path/to/binary

# 退出 r2（在 r2 交互界面中）
[0x00000000]> q
```

### 命令结构

Radare2 的命令结构遵循 `[命令][子命令][参数]` 模式。例如 `pdf` 是 `p` (print) -> `d` (disassemble) -> `f` (function) 的组合，意为"打印函数反汇编"。

**核心概念：万物皆 `?`**

在任何命令后面加上 `?` 都可以查看该命令的帮助文档。这是学习 Radare2 最重要的方法。

```bash
[0x00000000]> ?          # 顶级帮助
[0x00000000]> a?         # 分析命令帮助
[0x00000000]> pdf?       # 打印函数反汇编命令帮助
[0x00000000]> s?         # 跳转命令帮助
```

### Seek（跳转）

`s` 命令用于在文件中移动当前位置：

```bash
[0x00000000]> s main          # 跳转到 main 函数
[0x00001080]> s 0x8048400     # 跳转到绝对地址
[0x08048400]> s+10            # 向前偏移 10 字节
[0x0804840a]> s-5             # 向后偏移 5 字节
[0x08048405]> s-              # 撤销上一次跳转（后退）
[0x0804840a]> s+              # 重做跳转（前进）
```

### 常用启动参数

| 参数   | 说明                                  |
| ------ | ------------------------------------- |
| `-A`   | 启动后自动运行 `aaa` 分析            |
| `-d`   | 以调试模式启动                        |
| `-w`   | 以读写模式打开（可 patch 二进制）     |
| `-n`   | 不加载任何二进制信息（纯裸模式）      |
| `-c`   | 启动后立即执行指定命令                |
| `-q`   | 安静模式（通常配合 `-c` 做批量处理）  |
| `-e`   | 设定配置变量，如 `-e asm.arch=arm`    |
| `-b`   | 设定位数，如 `-b 64` 表示 64 位模式   |

示例：批量执行命令后退出：

```bash
# 打开文件 -> 分析 -> 列出函数 -> 退出
r2 -q -c 'aaa; afl' /path/to/binary
```

---

## Android SO 分析实战

> **💡 思路一句话**: r2 的核心优势是「命令行+脚本化」— 适合在无 GUI 环境（服务器/CI）中自动化分析 SO 文件，用 r2pipe 将 r2 集成到 Python 分析流水线中。

在 Android 逆向中，原生层（Native）逻辑往往编译在 `.so` 共享库中。Radare2 对 ARM/AArch64 架构有良好的支持，非常适合分析这类文件。

### 打开 ARM .so 文件

```bash
# 直接打开（r2 会自动识别架构）
r2 -A libnative-lib.so

# 如果自动识别失败，手动指定架构
r2 -a arm -b 32 libnative-lib.so    # 32 位 ARM
r2 -a arm -b 64 libnative-lib.so    # 64 位 AArch64
```

### 查看文件基本信息

```bash
# 打开后先查看文件元信息
[0x00000000]> iI
arch     arm
baddr    0x0
binsz    125432
bintype  elf
bits     64
canary   true
class    ELF64
endian   little
machine  AArch64
os       linux
relro    full
stripped true

# 查看段（sections）
[0x00000000]> iS
[Sections]
nth paddr        size vaddr       vsize perm type        name
――――――――――――――――――――――――――――――――――――――――――――――――――――――――
0   0x00000000    0x0 0x00000000    0x0 ---- NULL
1   0x00000200   0x1c 0x00000200   0x1c -r-- NOTE        .note.gnu.build-id
2   0x00000220  0x130 0x00000220  0x130 -r-- DYNSYM      .dynsym
...

# 查看导入的外部函数
[0x00000000]> ii
[Imports]
nth vaddr      bind   type   lib name
――――――――――――――――――――――――――――――――――
1   0x00000680 GLOBAL FUNC       __cxa_atexit
2   0x00000690 GLOBAL FUNC       __android_log_print
3   0x000006a0 GLOBAL FUNC       strlen
...

# 查看导出函数（JNI 函数通常在这里）
[0x00000000]> iE
[Exports]
nth paddr      vaddr      bind   type size lib name
――――――――――――――――――――――――――――――――――――――――
0   0x00000abc 0x00000abc GLOBAL FUNC 128      Java_com_example_app_MainActivity_stringFromJNI
1   0x00000b3c 0x00000b3c GLOBAL FUNC 64       JNI_OnLoad
...
```

### 分析与函数导航

```bash
# 全量分析（建议对 so 文件始终使用 aaa）
[0x00000000]> aaa
[x] Analyze all flags starting with sym. and entry0 (aa)
[x] Analyze function calls (aac)
[x] Analyze len bytes of instructions for references (aar)
[x] Finding and parsing C++ vtables (avrr)
[x] Skipping type matching analysis in debugger mode (aaft)
[x] Propagate noreturn information (aanr)
[x] Use -AA or aaaa to perform additional experimental analysis.

# 列出所有识别到的函数
[0x00000000]> afl
0x00000abc    4 128          sym.Java_com_example_app_MainActivity_stringFromJNI
0x00000b3c    2  64          sym.JNI_OnLoad
0x00000b7c    8 256          fcn.00000b7c
0x00000c7c    3  96          fcn.00000c7c
...

# 按名称过滤函数
[0x00000000]> afl~JNI
0x00000abc    4 128          sym.Java_com_example_app_MainActivity_stringFromJNI
0x00000b3c    2  64          sym.JNI_OnLoad

# 跳转到目标函数并反汇编
[0x00000000]> s sym.Java_com_example_app_MainActivity_stringFromJNI
[0x00000abc]> pdf
            ; DATA XREF from entry0 @ 0x680
┌ 128: sym.Java_com_example_app_MainActivity_stringFromJNI (int64_t arg1, int64_t arg2);
│           ; arg int64_t arg1 @ x0
│           ; arg int64_t arg2 @ x1
│           0x00000abc      fd7bbfa9       stp x29, x30, [sp, -0x10]!
│           0x00000ac0      fd030091       mov x29, sp
│           0x00000ac4      e00300aa       mov x0, x0
│           0x00000ac8      01000090       adrp x1, 0x1000
│           0x00000acc      21c04091       add x1, x1, 0x130
│           ...
└           0x00000b38      c0035fd6       ret
```

### 分析 JNI_OnLoad

`JNI_OnLoad` 是分析 Android SO 的关键入口。许多加固方案和动态注册逻辑都在此函数中：

```bash
[0x00000000]> s sym.JNI_OnLoad
[0x00000b3c]> pdf

# 查看该函数调用了哪些其他函数
[0x00000b3c]> afcc
  sym.JNI_OnLoad calls:
    sym.imp.__android_log_print
    fcn.00000b7c
    sym.imp.RegisterNatives
```

### 查看字符串资源

Android SO 中的字符串往往包含关键信息（日志标签、URL、加密密钥等）：

```bash
# 列出所有字符串
[0x00000000]> iz
[Strings]
nth paddr      vaddr      len size section type  string
――――――――――――――――――――――――――――――――――――――――――――
0   0x00001000 0x00001000 13  14   .rodata ascii Hello from C++
1   0x00001010 0x00001010 11  12   .rodata ascii native-lib
2   0x00001020 0x00001020 28  29   .rodata ascii https://api.example.com/v2
...

# 仅列出 .rodata 段中的字符串
[0x00000000]> izz~.rodata
```

---

## Radare2 命令速查

以下是按类别整理的常用命令速查表。

### 信息与元数据

| 命令   | 说明                                  |
| ------ | ------------------------------------- |
| `iI`   | 文件基本信息（架构、位数、大小端等）  |
| `ie`   | 入口点 (entrypoints)                  |
| `iS`   | 段信息 (sections)                     |
| `iS.`  | 当前地址所在段                        |
| `is`   | 符号表 (symbols)                      |
| `ii`   | 导入表 (imports)                      |
| `iE`   | 导出表 (exports)                      |
| `il`   | 链接的动态库 (libraries)              |
| `iz`   | 数据段字符串                          |
| `izz`  | 整个文件中的字符串                    |
| `ic`   | 类信息（C++ / ObjC / Java）           |

### 分析

| 命令    | 说明                                      |
| ------- | ----------------------------------------- |
| `aa`    | 基础分析                                  |
| `aaa`   | 完整自动分析（推荐）                      |
| `aaaa`  | 实验性深度分析                            |
| `af`    | 分析当前位置的函数                        |
| `afl`   | 列出所有函数                              |
| `afll`  | 列出所有函数（详细模式，含大小、调用数）  |
| `aflj`  | 以 JSON 格式列出函数（方便脚本处理）      |
| `afi`   | 当前函数详细信息                          |
| `afcc`  | 当前函数的调用关系                        |
| `afvd`  | 显示函数的局部变量                        |
| `axt`   | 查找对当前地址的交叉引用 (xrefs to)       |
| `axf`   | 查找当前地址引用的目标 (xrefs from)       |
| `agc`   | 函数调用图（文本）                        |
| `agCd`  | 全局调用图（dot 格式，可导出）            |

### 打印与显示

| 命令       | 说明                             |
| ---------- | -------------------------------- |
| `pd N`     | 反汇编 N 条指令                  |
| `pdf`      | 反汇编当前函数                   |
| `pdc`      | 伪代码输出（内置反编译器）       |
| `pdg`      | Ghidra 反编译器输出（需插件）    |
| `px N`     | 十六进制转储 N 字节              |
| `pxw N`    | 以 word (4 字节) 格式显示        |
| `ps @ addr`| 打印指定地址的字符串             |
| `psz`      | 打印以零结尾的字符串             |
| `pf`       | 按格式化结构体打印               |

### 跳转与导航

| 命令           | 说明                        |
| -------------- | --------------------------- |
| `s addr`       | 跳转到指定地址              |
| `s funcname`   | 跳转到函数名                |
| `s-`           | 后退                        |
| `s+`           | 前进                        |
| `s$$`          | 跳转到文件末尾              |
| `sr reg`       | 跳转到寄存器值对应地址      |

### 搜索

| 命令                 | 说明                          |
| -------------------- | ----------------------------- |
| `/ string`           | 搜索字符串                    |
| `/x 9090`            | 搜索十六进制模式              |
| `/r addr`            | 搜索对某地址的引用            |
| `/R pattern`         | 搜索 ROP gadgets              |
| `/a asm_instr`       | 搜索汇编指令                  |
| `/c jmp`             | 搜索含指定指令的位置          |

### 标记与注释

| 命令                | 说明                          |
| ------------------- | ----------------------------- |
| `f name @ addr`     | 在地址上添加标记 (flag)       |
| `f- name`           | 删除标记                      |
| `CC comment @ addr` | 在地址上添加注释              |
| `CC-`               | 删除注释                      |
| `afn newname`       | 重命名当前函数                |

### 调试

| 命令        | 说明                         |
| ----------- | ---------------------------- |
| `db addr`   | 设置断点                     |
| `db- addr`  | 删除断点                     |
| `dbl`       | 列出所有断点                 |
| `dc`        | 继续执行 (continue)          |
| `ds`        | 单步步入 (step into)         |
| `dso`       | 单步步过 (step over)         |
| `dr`        | 显示所有寄存器               |
| `dr rax`    | 显示指定寄存器               |
| `dm`        | 显示内存映射                 |
| `dbt`       | 显示调用栈 (backtrace)       |

---

## 脚本与自动化

Radare2 的精髓在于自动化。可以通过多种方式实现脚本化分析。

### r2pipe（Python）

`r2pipe` 是 Radare2 官方的脚本库，支持 Python、JavaScript、Go、Rust 等多种语言。

#### 安装

```bash
pip install r2pipe
```

#### 基础用法

```python
import r2pipe

# 打开文件
r2 = r2pipe.open("libnative-lib.so")

# 运行 'aaa' 命令进行分析
r2.cmd('aaa')

# 运行 'aflj' 命令获取 JSON 格式的函数列表并解析
functions = r2.cmdj('aflj')

# 打印每个函数名
if functions:
    for func in functions:
        print(f"Function: {func['name']} at {hex(func['offset'])} size={func['size']}")

r2.quit()
```

#### 批量提取 JNI 函数信息

```python
import r2pipe
import json

def analyze_jni_so(filepath):
    """分析 Android SO 文件中的 JNI 函数"""
    r2 = r2pipe.open(filepath)
    r2.cmd('aaa')

    # 获取所有导出函数
    exports = r2.cmdj('iEj')
    jni_funcs = [e for e in exports if e['name'].startswith('Java_')]

    print(f"[*] 找到 {len(jni_funcs)} 个 JNI 函数:")
    for func in jni_funcs:
        addr = func['vaddr']
        name = func['name']
        # 解析 JNI 命名规则：Java_包名_类名_方法名
        parts = name.split('_')
        if len(parts) >= 4:
            method = parts[-1]
            clazz = parts[-2]
            print(f"  {clazz}.{method}() @ {hex(addr)}")

        # 获取该函数的反汇编
        disasm = r2.cmd(f'pdf @ {addr}')

        # 检查该函数是否调用了加密相关函数
        if any(kw in disasm for kw in ['AES', 'encrypt', 'decrypt', 'cipher']):
            print(f"    [!] 该函数可能涉及加密操作")

    # 获取字符串列表
    strings = r2.cmdj('izj')
    suspicious = [s for s in strings if any(kw in s.get('string', '')
                  for kw in ['http', 'key', 'secret', 'password', 'token'])]
    if suspicious:
        print(f"\n[*] 发现 {len(suspicious)} 个可疑字符串:")
        for s in suspicious:
            print(f"  0x{s['vaddr']:08x}: {s['string']}")

    r2.quit()

# 使用
analyze_jni_so("libnative-lib.so")
```

### r2pipe（JavaScript / Node.js）

```javascript
const r2pipe = require('r2pipe');

r2pipe.open('libnative-lib.so', (err, r2) => {
    r2.cmd('aaa', () => {
        r2.cmdj('aflj', (err, funcs) => {
            funcs.forEach(f => {
                console.log(`${f.name} @ 0x${f.offset.toString(16)}`);
            });
            r2.quit();
        });
    });
});
```

### r2 内置脚本

除了 r2pipe，你也可以直接在 r2 的交互 shell 中执行脚本：

```bash
# 在 r2 中执行外部脚本
[0x00000000]> . script.r2

# 使用内置宏
[0x00000000]> (analyze_func addr; s $0; af; pdf)
[0x00000000]> .(analyze_func 0x1234)
```

`script.r2` 文件内容示例：

```text
# script.r2 - 自动分析脚本
aaa
afl~JNI
s sym.JNI_OnLoad
pdf
```

### 批量处理多个 SO 文件

```bash
#!/bin/bash
# batch_analyze.sh - 批量分析 APK 解压后的所有 SO 文件

SO_DIR="./lib/arm64-v8a"

for so in "$SO_DIR"/*.so; do
    echo "========== 分析: $so =========="
    r2 -q -c '
        aaa;
        echo "--- 导出函数 ---";
        iE~FUNC;
        echo "--- 可疑字符串 ---";
        izz~http;
        izz~encrypt;
        izz~decrypt;
        izz~key
    ' "$so"
    echo ""
done
```

---

## 与 Frida 联动

### r2frida 简介

`r2frida` 是一个将 Radare2 和 Frida 结合的插件。它允许你用 Radare2 的命令行接口来操作一个正在运行的进程，底层通过 Frida 实现注入和内存访问。这意味着你可以在不 root 的设备上，使用 r2 的全部分析命令来探查运行时内存。

### 安装 r2frida

```bash
# 通过 r2pm（r2 包管理器）安装
r2pm -ci r2frida
```

### 基本用法

```bash
# 附加到正在运行的 Android 进程
r2 frida://attach/usb//com.example.app

# 启动并附加
r2 frida://spawn/usb//com.example.app

# 连接后，你就进入了 r2 的交互 shell，但后端是 Frida
```

### r2frida 常用命令

在 r2frida 会话中，所有以 `\` 或 `:` 开头的命令是 Frida 特有命令：

```bash
# 列出已加载的模块（SO 库）
[0x00000000]> \il
0x7a3b4c0000 128K libnative-lib.so
0x7a3b5e0000 2.1M libart.so
0x7a3b800000 1.5M libc.so
...

# 列出模块的导出函数
[0x00000000]> \iE libnative-lib.so

# 搜索内存中的字符串
[0x00000000]> \/ Hello from C++

# 读取运行时内存
[0x00000000]> s 0x7a3b4c0abc
[0x7a3b4c0abc]> px 64

# 在运行时给函数下钩子
[0x00000000]> \di0 sym.Java_com_example_app_MainActivity_stringFromJNI
```

### 静态 + 动态联合分析工作流

一个典型的结合 Radare2 静态分析和 Frida 动态分析的工作流如下：

1. **静态分析阶段**：用 r2 打开 SO 文件，完成 `aaa` 分析，定位关键函数和字符串
2. **确定 Hook 点**：通过 `axt`（交叉引用）和 `pdf`（反汇编）确认要监控的函数地址
3. **动态验证**：用 r2frida 附加到运行中的 App，在目标地址查看运行时数据
4. **编写 Frida 脚本**：基于静态分析获得的偏移量，编写 Frida hook 脚本

```python
# 示例：先用 r2 找到偏移量，再用 Frida hook
import r2pipe
import frida

# 第一步：静态分析获取偏移
r2 = r2pipe.open("libnative-lib.so")
r2.cmd('aaa')
target_func = r2.cmdj('aflj~{name:encrypt_data}')
if target_func:
    offset = target_func[0]['offset']
    print(f"[*] 目标函数偏移: {hex(offset)}")
r2.quit()

# 第二步：用 Frida 在运行时 hook 该偏移
js_code = f"""
var base = Module.findBaseAddress("libnative-lib.so");
var target = base.add({hex(offset)});
Interceptor.attach(target, {{
    onEnter: function(args) {{
        console.log("[*] encrypt_data 被调用");
        console.log("[*] 参数1: " + args[0].readUtf8String());
    }},
    onLeave: function(retval) {{
        console.log("[*] 返回值: " + retval.readUtf8String());
    }}
}});
"""
```

---

## Visual 模式详解

Radare2 虽然是命令行工具，但提供了丰富的文本用户界面（TUI）模式。

### V 模式（基础可视化）

在命令行中输入 `V` 进入基础可视化模式：

```bash
[0x00000000]> V
```

在 V 模式中的常用按键：

| 按键       | 说明                                        |
| ---------- | ------------------------------------------- |
| `p` / `P`  | 向前/向后切换视图面板（反汇编、十六进制等） |
| `j` / `k`  | 向下/向上滚动                               |
| `J` / `K`  | 向下/向上翻页                               |
| `g`        | 跳转到指定地址或函数                        |
| `Enter`    | 跟随跳转（进入被调用函数）                  |
| `u`        | 撤销跳转（返回上一位置）                    |
| `x`        | 查看交叉引用                                |
| `:`        | 进入命令行模式（执行 r2 命令）              |
| `q`        | 退出可视化模式                              |

`V` 模式通过按 `p` 可以在以下视图之间循环切换：
- **反汇编视图**：显示当前地址的汇编代码
- **十六进制视图**：显示原始字节的 hex dump
- **调试视图**：显示寄存器、栈等调试信息
- **字符串/数据视图**：以数据方式解释当前区域

### VV 模式（控制流图）

`VV` 模式是 Radare2 的 ASCII-art 控制流图，类似于 IDA Pro 的图形视图：

```bash
# 先跳转到目标函数，再进入图模式
[0x00000000]> s main
[0x00001080]> VV
```

在 VV 模式中的按键：

| 按键          | 说明                              |
| ------------- | --------------------------------- |
| `hjkl`        | 移动图形视图（左/下/上/右）       |
| `+` / `-`     | 放大/缩小                         |
| `Tab`         | 在基本块之间跳转                  |
| `t` / `f`     | 跟随 true / false 分支            |
| `g`           | 跳转到指定基本块                  |
| `R`           | 随机更换颜色方案                  |
| `p`           | 切换迷你图/完整图                 |
| `q`           | 退出图模式                        |

### Vd 模式（十六进制编辑）

在 V 模式中按 `p` 切换到十六进制视图后，你可以直接编辑字节（需要以 `-w` 写模式打开文件）：

```bash
# 以写模式打开
r2 -w target.so

# 进入可视化模式 -> 按 p 切换到 hex 视图
[0x00000000]> V
# 按 p 直到看到十六进制视图
# 按 i 进入插入模式，可直接修改字节
# 按 q 退出
```

### Panel 模式

Panel 模式允许你在同一界面中同时显示多个窗口：

```bash
[0x00000000]> v
# 或
[0x00000000]> V!
```

| 按键         | 说明                           |
| ------------ | ------------------------------ |
| `Tab`        | 在面板之间切换焦点             |
| `w`          | 进入窗口管理模式               |
| `e`          | 更改当前面板显示内容           |
| `|` / `-`    | 水平/垂直分割面板              |
| `X`          | 关闭当前面板                   |

---

## 搜索与交叉引用

### 字符串搜索

```bash
# 在当前分析的二进制中搜索 ASCII 字符串
[0x00000000]> / encrypt
Searching 7 bytes in [0x0-0x1e000]
hits: 3
0x00012340 hit0_0 "encrypt_key"
0x00012380 hit0_1 "encrypt_data"
0x000123c0 hit0_2 "decrypted_result"

# 搜索宽字符（UTF-16）字符串
[0x00000000]> /w password

# 搜索并列出所有匹配结果
[0x00000000]> fs hits
[0x00000000]> f
```

### 十六进制模式搜索

```bash
# 搜索特定字节序列
[0x00000000]> /x 7f454c46         # 搜索 ELF 魔数
[0x00000000]> /x 504b0304         # 搜索 ZIP/APK 魔数
[0x00000000]> /x 00009090..00     # 使用 .. 作为通配符

# 搜索 ARM 指令模式（如 BL 指令）
[0x00000000]> /x ....0094         # AArch64 的 BL 指令编码
```

### 汇编指令搜索

```bash
# 搜索特定汇编指令
[0x00000000]> /a mov x0, x1
[0x00000000]> /a svc 0            # 搜索系统调用

# 搜索 ROP gadgets
[0x00000000]> /R ret
[0x00000000]> /R pop              # 搜索以 pop 开头的 gadget
```

### 交叉引用分析

交叉引用（Cross References, xrefs）是逆向分析的核心能力之一：

```bash
# 查找谁引用了当前地址（xrefs TO）
[0x00012340]> axt
sym.encrypt_data 0x00000bfc [CALL] bl sym.imp.strlen
sym.JNI_OnLoad 0x00000b58 [DATA] adrp x1, 0x12000

# 查找当前地址引用了哪些目标（xrefs FROM）
[0x00000bfc]> axf
0x00000c04 [CALL] sym.imp.memcpy
0x00000c18 [CALL] sym.imp.free

# 对某个字符串查找引用
[0x00000000]> axt @ 0x00012340
fcn.00000b7c 0x00000b90 [DATA] adr x0, str.encrypt_key

# 使用图形方式展示调用关系
[0x00000000]> agc @ sym.JNI_OnLoad
```

交叉引用在 Android 逆向中的典型应用场景：
- 定位某个加密字符串被哪些函数使用
- 追踪 `RegisterNatives` 的调用来找到动态注册的 JNI 函数
- 从一个 log 字符串反向追踪到使用它的函数逻辑

---

## 调试功能

Radare2 内置了功能完整的调试器，支持本地调试和远程调试。

### 启动调试会话

```bash
# 直接调试本地可执行文件
r2 -d /path/to/binary

# 附加到正在运行的进程
r2 -d pid

# 远程调试（通过 gdb 协议）
r2 -d gdb://192.168.1.100:1234

# Android 远程调试（需要在设备上运行 r2 agent）
r2 -d gdb://localhost:23456
```

### 断点管理

```bash
# 在地址上设置断点
[0x00000000]> db 0x00000abc

# 在函数名上设置断点
[0x00000000]> db sym.JNI_OnLoad

# 设置条件断点（当 x0 == 1 时触发）
[0x00000000]> dbc 0x00000abc x0==1

# 列出所有断点
[0x00000000]> dbl
0x00000abc - enabled
0x00000b3c - enabled

# 删除断点
[0x00000000]> db- 0x00000abc

# 启用/禁用断点
[0x00000000]> dbe 0x00000abc     # enable
[0x00000000]> dbd 0x00000abc     # disable

# 设置硬件断点（对特定平台有效）
[0x00000000]> dbH 0x00000abc
```

### 执行控制

```bash
# 继续执行
[0x00000000]> dc

# 单步步入（进入函数调用）
[0x00000abc]> ds

# 单步步过（跳过函数调用）
[0x00000abc]> dso

# 执行到返回（跳出当前函数）
[0x00000abc]> dcr

# 执行到指定地址
[0x00000abc]> dcu 0x00000b00
```

### 寄存器与内存检查

```bash
# 显示所有寄存器
[0x00000abc]> dr
x0  = 0x00007fff5a3b4c00
x1  = 0x0000000000000042
x2  = 0x00007fff5a3b5000
...
pc  = 0x0000000000000abc
sp  = 0x00007fff5a3b4bf0

# 修改寄存器值
[0x00000abc]> dr x0=0x1234

# 查看调用栈
[0x00000abc]> dbt
0  0x00000abc sp: 0x7fff5a3b4bf0  sym.encrypt_data
1  0x00000b60 sp: 0x7fff5a3b4c10  sym.JNI_OnLoad
2  0x7a3b610c sp: 0x7fff5a3b4c30  libart.so

# 查看内存映射
[0x00000abc]> dm
0x0000000000000000 - 0x000000000001e000 r-x libnative-lib.so
0x000000000001e000 - 0x0000000000020000 rw- libnative-lib.so
0x00007a3b5e0000   - 0x00007a3b7e0000   r-x libart.so
...

# 读取指定地址的内存
[0x00000abc]> px 32 @ x0        # 读取 x0 指向的 32 字节
[0x00000abc]> ps @ x0           # 将 x0 指向的地址作为字符串打印

# 向内存写入数据
[0x00000abc]> wx 90909090 @ 0x00000abc   # 写入字节
[0x00000abc]> w Hello @ 0x00001000       # 写入字符串
```

### 跟踪与记录

```bash
# 跟踪函数调用
[0x00000000]> e dbg.trace=true
[0x00000000]> dc

# 查看执行轨迹
[0x00000000]> dbt

# 跟踪指定范围的指令执行
[0x00000000]> dte
```

---

## Cutter GUI

对于不习惯纯命令行的用户，社区开发了 **Cutter**。Cutter 是一个基于 Qt/C++ 的图形用户界面，后端由 Radare2 驱动。

### 安装

```bash
# macOS
brew install --cask cutter

# 或从 GitHub Releases 下载预编译包
# https://github.com/rizinorg/cutter/releases
```

> **注意**：Cutter 目前已经迁移到 Rizin（Radare2 的一个分支）作为后端。但其核心概念和使用方式与 Radare2 高度一致。

### 主要特点

- 提供了类似 IDA Pro 和 Ghidra 的图形化界面
- 包括反汇编窗口、反编译窗口（集成了 Ghidra Decompiler）、函数列表、Hexdump 等
- 所有在 Cutter 中进行的操作，实际上都是在后台调用 Radare2/Rizin 的命令完成的
- 对于初学者来说，从 Cutter 入手可以极大地降低学习 Radare2 的门槛
- 内置终端面板可以直接输入 r2 命令，方便从 GUI 过渡到命令行

### 典型工作流

1. 用 Cutter 打开 APK 中提取的 `.so` 文件
2. 在左侧函数列表中查找 JNI 函数
3. 在反汇编视图中查看控制流图
4. 切换到反编译视图获得伪代码
5. 使用搜索功能查找感兴趣的字符串
6. 在内置终端中运行高级 r2 命令

### Cutter vs. 纯命令行 r2

| 场景                     | 推荐工具         |
| ------------------------ | ---------------- |
| 初次浏览未知二进制       | Cutter           |
| 需要查看控制流图         | Cutter           |
| 需要反编译伪代码         | Cutter           |
| 批量/自动化分析          | 命令行 r2        |
| 远程 SSH 环境            | 命令行 r2        |
| 与 Frida 联动            | 命令行 r2        |
| 需要精细的搜索与过滤     | 命令行 r2        |

---

## 优缺点分析

### 优点

| 优点                     | 说明                                                             |
| ------------------------ | ---------------------------------------------------------------- |
| **无与伦比的脚本化能力** | 设计哲学使其成为自动化逆向分析的理想选择                         |
| **极高的灵活性和定制性** | 你可以按照自己的需求组合命令，构建工作流                         |
| **轻量与快速**           | 核心程序非常小，运行速度快，资源占用少，适合嵌入式和服务器环境   |
| **海量架构支持**         | 对各种奇异架构的支持是其一大特色，覆盖几乎所有 CPU 架构         |
| **完全免费开源**         | 无任何费用，社区可以审查和贡献代码                               |
| **命令行原生**           | 在 SSH、Docker、CI/CD 环境中可以无障碍使用                       |
| **r2frida 生态**         | 与 Frida 的深度集成提供了独特的静态+动态分析能力                 |
| **活跃的社区**           | 开发活跃，经常更新，社区贡献丰富的插件和工具                     |

### 缺点

| 缺点                     | 说明                                                                             |
| ------------------------ | -------------------------------------------------------------------------------- |
| **陡峭的学习曲线**       | 命令繁多，语法特殊，对新手非常不友好，需要大量练习                               |
| **文档相对混乱**         | 虽然有帮助系统，但官方文档的结构性和完整性不如商业软件                           |
| **默认反编译器质量一般** | 内置的反编译器质量不如 Ghidra 或 Hex-Rays，但可以通过插件集成 Ghidra Decompiler  |
| **交互式分析体验**       | 纯命令行的交互式分析体验不如 IDA Pro 直观，复杂分析时效率可能较低               |
| **API 稳定性**           | 因为开发活跃，命令和 API 偶尔会有不兼容的变更                                    |
| **错误提示不够友好**     | 输入错误命令时，提示信息有时不够清晰，增加了排错成本                             |

### 适用场景总结

Radare2 最适合以下场景：

- **自动化批量分析**：需要脚本化处理大量二进制文件时，r2 + r2pipe 是最佳选择
- **嵌入式/IoT 逆向**：面对小众架构时，r2 的广泛架构支持无可替代
- **服务器端分析**：在无 GUI 的远程服务器上，r2 是唯一可用的全功能选择
- **CTF 竞赛**：快速的命令行操作和强大的搜索能力在 CTF 中极为实用
- **与 Frida 联动**：r2frida 提供了其他工具无法比拟的动静态联合分析体验
- **Android SO 分析**：结合脚本化能力，可以高效批量处理 APK 中的原生库

对于日常的交互式逆向分析，如果你更习惯图形界面，可以考虑将 Radare2/Cutter 与 Ghidra/IDA Pro 搭配使用，取长补短。
