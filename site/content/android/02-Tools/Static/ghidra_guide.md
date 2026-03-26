---
title: "Ghidra 入门"
date: 2024-09-27
type: posts
tags: ["静态分析", "Ghidra", "IDA", "Android", "IDA Pro"]
weight: 10
---

# Ghidra 入门

Ghidra 是由美国国家安全局 (NSA) 开发并开源的一款软件逆向工程 (SRE) 套件。它以功能全面、免费开源、跨平台等特性，迅速成为 IDA Pro 之外逆向工程师们的另一个重要选择，尤其在学术界和独立研究者中广受欢迎。

---

## 目录

1. [核心特性](#核心特性)
2. [Ghidra vs. IDA Pro vs. Radare2](#ghidra-vs-ida-pro-vs-radare2)
3. [安装与配置](#安装与配置)
4. [基本工作流程](#基本工作流程)
5. [关键视图与操作](#关键视图与操作)
   - [Code Browser (代码浏览器)](#code-browser-代码浏览器)
   - [Decompiler (反编译器)](#decompiler-反编译器)
   - [Function Graph (函数图)](#function-graph-函数图)
   - [Symbol Tree (符号树)](#symbol-tree-符号树)
   - [Data Type Manager (数据类型管理器)](#data-type-manager-数据类型管理器)
6. [Android SO 分析实战](#android-so-分析实战)
7. [反编译器使用](#反编译器使用)
8. [Ghidra Script 实战](#ghidra-script-实战)
9. [Headless 模式](#headless-模式)
10. [常用插件与扩展](#常用插件与扩展)
11. [Ghidra vs IDA Pro 深度对比](#ghidra-vs-ida-pro-深度对比)
12. [高级技巧](#高级技巧)
13. [优缺点分析](#优缺点分析)

---

## 核心特性

- **强大的反编译器 (Decompiler)**: 这是 Ghidra 的王牌功能。它内置了一个高质量的、支持多种处理器架构的免费反编译器，能够将汇编代码转换为类似 C/C++ 的高级语言伪代码，极大地提高了代码理解效率。

- **全面的分析能力**: 支持对多种平台的可执行文件进行反汇编、分析、反编译、图表绘制和脚本化，包括 Windows, macOS, Linux, Android, iOS 等。

- **强大的脚本引擎**: 内置对 Java 和 Python (通过 Jython) 的支持，允许用户编写复杂的脚本来自动化分析任务，从简单的重命名到复杂的漏洞模式匹配。

- **交互式与自动化操作**: 既支持像 IDA Pro 那样的交互式手动分析，也提供了强大的"无头分析器"(Headless Analyzer)，可以通过命令行进行批量、自动化的分析。

- **多用户协作**: Ghidra Server 组件支持多名分析师对同一个二进制文件进行协同逆向，并能方便地进行版本追踪和合并。

- **可扩展性**: 用户可以自定义和扩展 Ghidra 的功能，包括编写新的处理器模块、加载器和分析器插件。

---

## Ghidra vs. IDA Pro vs. Radare2

| 特性         | Ghidra                         | IDA Pro                     | Radare2                        |
| :----------- | :----------------------------- | :-------------------------- | :----------------------------- |
| **价格**     | **完全免费**                   | 非常昂贵                    | 完全免费                       |
| **开源**     | **是** (Java)                  | 否                          | 是 (C)                         |
| **核心优势** | **高质量的免费反编译器**       | **最强的交互式反汇编**      | **极致的脚本化和命令行**       |
| **UI**       | Java Swing，功能强大但略显笨重 | Qt，业界标准，成熟稳定      | 命令行，或通过 Cutter 提供 GUI |
| **自动化**   | 强大的 Headless 模式和脚本     | 主要通过 IDC/IDAPython 脚本 | 设计哲学核心，自动化能力极强   |
| **协作**     | 内置 Ghidra Server 支持        | 第三方插件 (如 BinSync)     | 脚本化协作，或通过第三方工具   |
| **学习曲线** | 中等，UI 直观                  | 中等，功能繁多              | **非常陡峭**，命令繁杂         |

---

## 安装与配置

### JDK 版本要求

Ghidra 是基于 Java 开发的应用程序，运行前必须安装对应版本的 JDK。各版本对应关系如下：

| Ghidra 版本    | 最低 JDK 版本 | 推荐 JDK          |
| :------------- | :------------ | :----------------- |
| 10.x           | JDK 11        | Amazon Corretto 11 |
| 11.0 - 11.1    | JDK 17        | Amazon Corretto 17 |
| 11.2+          | JDK 21        | Amazon Corretto 21 |

> **提示**: 推荐使用 Amazon Corretto 或 Eclipse Adoptium (Temurin) 发行版，它们经过验证与 Ghidra 兼容良好。避免使用 Oracle JDK 的付费许可证，开源 JDK 完全够用。

### 安装步骤

1. **安装 JDK**: 下载并安装对应版本的 JDK，确保 `JAVA_HOME` 环境变量已正确设置。

   ```bash
   # macOS / Linux 验证 JDK 版本
   java -version
   # 应输出: openjdk version "21.x.x" 或类似

   # 设置 JAVA_HOME (以 zsh 为例)
   export JAVA_HOME=$(/usr/libexec/java_home -v 21)
   ```

2. **下载 Ghidra**: 从 [Ghidra 官方 GitHub](https://github.com/NationalSecurityAgency/ghidra/releases) 下载最新的稳定版 ZIP 包。

3. **解压运行**:

   ```bash
   # 解压
   unzip ghidra_11.2_PUBLIC_20241105.zip -d ~/tools/

   # 运行
   # Windows: 双击 ghidraRun.bat
   # Linux / macOS:
   cd ~/tools/ghidra_11.2_PUBLIC
   ./ghidraRun
   ```

### 内存配置优化

分析大型 Android SO 文件时，Ghidra 默认内存设置常常不够用。修改启动配置文件提升堆内存：

```bash
# 编辑 support/launch.properties
# 找到以下行并修改
MAXMEM=2G
# 改为 (根据你的机器内存调整)
MAXMEM=8G
```

对于更精细的控制，可以修改 `support/launch.properties` 中的 JVM 参数：

```properties
# 推荐的 JVM 配置 (16GB 物理内存的机器)
VMARGS=-XX:+UseG1GC -XX:MaxGCPauseMillis=200
MAXMEM=8G
```

> **项目组织建议**: 每个 APK 或目标应用创建一个独立的 Ghidra 项目，将相关的所有 SO 文件导入同一个项目中，方便交叉引用分析。共享的数据类型归档 (`.gdt` 文件) 可以在多个项目之间复用。

### 暗色主题配置

Ghidra 的默认亮色主题长时间使用比较刺眼。从 Ghidra 11.0 开始内置了主题支持：

- 进入 `Edit -> Theme -> Switch Theme...`
- 选择内置的暗色主题
- 对于旧版本，可以安装社区 [Ghidra-dark-theme](https://github.com/zackelia/ghidra-dark-theme) 插件

---

## 基本工作流程

### 1. 创建项目

- `File -> New Project...`
- 选择 `Non-Shared Project` (单用户项目)。
- 指定项目路径和名称。

### 2. 导入文件

- `File -> Import File...`
- 选择你想要分析的二进制文件 (如 `.exe`, `.dll`, `.so`, `.apk`)。
- Ghidra 会自动识别文件格式、处理器架构等，直接点击 `OK`。

### 3. 分析文件

- 在弹出的分析选项框中，保留默认勾选的分析器即可，点击 `Analyze`。
- Ghidra 会开始对文件进行自动分析，这可能需要一些时间，取决于文件大小和复杂度。

### 4. 开始探索

- 分析完成后，双击项目窗口中的文件名，打开 Ghidra 的核心工具 **Code Browser**。
- 现在你可以开始你的逆向之旅了！

---

## 关键视图与操作

### Code Browser (代码浏览器)

这是 Ghidra 的主界面，通常包含以下几个核心子窗口：

- **Listing (清单/反汇编窗口)**: 左侧显示反汇编代码，是分析的主要区域。
- **Functions (函数窗口)**: 左下角，列出所有已识别的函数。点击函数名可以在反汇编窗口中跳转。
- **Program Trees (程序树)**: 左上角，以树状结构展示程序的段 (sections)。

Code Browser 的整体布局：左侧面板包含 Program Trees、Symbol Tree 和 Data Type Manager；中间为 Listing (反汇编窗口)；右侧为 Decompiler (反编译器)；底部为 Console (控制台输出)。

### 常用快捷键速查

| 快捷键       | 功能                          | 说明                                 |
| :----------- | :---------------------------- | :----------------------------------- |
| `G`          | Go to Address                 | 跳转到指定地址                       |
| `L`          | Rename (Label)                | 重命名函数/变量/标签                 |
| `T`          | Set Data Type                 | 修改变量或参数的数据类型             |
| `Ctrl+E`     | Edit Function Signature       | 编辑函数签名 (返回值、参数)          |
| `Ctrl+L`     | Retype Variable               | 在反编译窗口中修改变量类型           |
| `;`          | Set Comment                   | 在当前行添加注释                     |
| `/`          | Set Comment (Decompiler)      | 在反编译窗口添加注释                 |
| `X`          | Show References (Xrefs)       | 查看对当前符号的所有交叉引用         |
| `Ctrl+Shift+F` | Search Memory              | 在整个程序内存中搜索字符串或字节     |
| `D`          | Disassemble                   | 将数据强制转换为代码                 |
| `P`          | Create Function               | 在当前地址创建函数                   |
| `Space`      | Toggle Listing/Graph          | 在反汇编列表和函数图之间切换         |
| `Ctrl+T`     | Show Data Type Chooser        | 快速选择数据类型                     |

### Decompiler (反编译器)

- 通常位于反汇编窗口的右侧。
- 它会自动显示当前光标所在函数的 C 伪代码。
- 这是 Ghidra 最有价值的窗口。你可以直接在伪代码中对变量、函数进行重命名、修改类型，这些改动会**双向同步**到反汇编窗口。

### Function Graph (函数图)

Function Graph 以控制流图 (CFG) 的方式展示函数结构，非常适合理解复杂的分支逻辑：

- 在 Listing 窗口中按 `Space` 键可以切换到函数图视图
- 也可以通过 `Window -> Function Graph` 打开独立窗口
- 支持缩放、拖动、折叠基本块
- 绿色边表示条件为真 (taken branch)，红色边表示条件为假 (fall-through)

### Symbol Tree (符号树)

- 位于左侧，`Functions` 窗口旁边。
- 它以树状结构列出了程序中所有的符号，包括函数、标签、导入/导出函数等。你可以通过过滤器快速查找特定函数。
- 在 Symbol Tree 的过滤框中输入关键词即可实时过滤，例如输入 `JNI` 即可快速定位所有 JNI 相关函数。

### Data Type Manager (数据类型管理器)

- 左下角，`Functions` 窗口下方。
- 这里管理着程序中所有的数据类型 (struct, union, enum 等)。你可以创建、修改、导入和导出数据类型定义。这对于分析复杂的数据结构至关重要。
- 右键可以创建新的结构体，也可以从 C 头文件 (`Parse C Source`) 批量导入类型定义。

---

## Android SO 分析实战

Android 应用中的 Native 层代码以 `.so` 共享库的形式存在，通常编译为 ARM 或 ARM64 架构。使用 Ghidra 分析这类文件是 Android 逆向中最常见的场景之一。

### 提取 SO 文件

首先需要从 APK 中提取目标 SO 文件：

```bash
# APK 本质是 ZIP 包，直接解压即可
unzip target_app.apk -d target_app_extracted/

# SO 文件通常位于 lib/ 目录下
ls target_app_extracted/lib/
# arm64-v8a/  armeabi-v7a/  x86/  x86_64/

# 优先分析 arm64-v8a (64位 ARM，现代设备主流)
ls target_app_extracted/lib/arm64-v8a/
# libnative-lib.so  libsecurity.so
```

### 导入 SO 文件与处理器选择

将 SO 文件导入 Ghidra 时，需要注意处理器选项：

1. `File -> Import File...` 选择目标 SO 文件
2. Ghidra 通常能自动识别 ELF 格式和 ARM 架构
3. 确认导入对话框中的设置：

| 字段               | arm64-v8a               | armeabi-v7a              |
| :----------------- | :---------------------- | :----------------------- |
| **Format**         | ELF (Executable and Linkable Format) | ELF                      |
| **Language**       | AARCH64:LE:64:v8A       | ARM:LE:32:v8             |
| **Compiler**       | default                 | default                  |

> **重要**: 如果 Ghidra 自动识别错误（偶尔发生在被加壳或修改的 SO 中），需要手动选择正确的处理器架构，否则反汇编结果会完全错误。

### 自动分析选项

导入后的自动分析对话框中，针对 Android SO 建议开启以下分析器：

- **Demangler GNU** - 还原 C++ 符号名称（必开）
- **Function Start Search** - 搜索未被识别的函数入口
- **Aggressive Instruction Finder** - 激进地查找代码区域
- **ELF Scalar Operand References** - 解析 ELF 中的标量引用
- **Non-Returning Functions** - 识别不返回的函数（如 `abort`, `exit`）
- **Stack** - 分析栈帧结构

### 定位 JNI 函数

Android SO 中最关键的是 JNI (Java Native Interface) 函数。有两种注册方式：

**静态注册** - 函数名遵循固定格式：

```
Java_com_example_app_MainActivity_stringFromJNI
```

在 Symbol Tree 中过滤 `Java_` 前缀即可快速找到所有静态注册的 JNI 函数。

**动态注册** - 通过 `JNI_OnLoad` 中调用 `RegisterNatives`。在 Ghidra 中定位步骤：

1. 在 Symbol Tree 中找到 `JNI_OnLoad`
2. 在反编译窗口中找到 `RegisterNatives` 调用
3. 追踪第三个参数 (methods 数组)，其中包含 `{Java方法名, 签名, Native函数指针}` 的映射
4. 函数指针即为实际的 Native 实现，可以跳转过去分析

### 应用 JNI 类型定义

为了让反编译结果更可读，建议导入 JNI 头文件的类型定义：

1. 打开 Data Type Manager
2. 右键 -> `Parse C Source...`
3. 添加 Android NDK 中的 `jni.h` 头文件路径
4. 解析完成后，`JNIEnv`, `JavaVM`, `jclass` 等类型就可以在反编译窗口中使用了

如果不想导入完整的 NDK 头文件，也可以在 `Parse C Source` 对话框中直接粘贴简化的 `typedef` 定义（如 `typedef void* JNIEnv;` 等）。

---

## 反编译器使用

Ghidra 的反编译器是其核心竞争力，也是大多数用户选择 Ghidra 的最主要原因。

### Ghidra 反编译器 vs Hex-Rays

| 对比维度         | Ghidra Decompiler          | Hex-Rays (IDA Pro)          |
| :--------------- | :------------------------- | :-------------------------- |
| **价格**         | 免费内置                   | 需额外付费，非常昂贵       |
| **架构支持**     | 几乎所有 Ghidra 支持的架构 | x86/x64/ARM/ARM64/MIPS/PPC |
| **输出质量**     | 良好，偶有冗余代码         | 优秀，更贴近原始代码        |
| **类型推断**     | 良好                       | 优秀                        |
| **交互修改**     | 支持双向同步               | 支持双向同步                |
| **Switch 识别**  | 较好                       | 极好                        |
| **C++ 虚函数**   | 部分支持                   | 支持较好                    |

总体而言，Hex-Rays 在输出质量上仍然领先，但 Ghidra 反编译器已经达到了非常实用的水平，对于大多数 Android 逆向场景完全够用。

### 阅读反编译输出

Ghidra 反编译器输出的伪代码有一些特点需要了解：

```c
// Ghidra 典型的反编译输出
undefined8 FUN_00012a4c(long param_1, long param_2, long param_3)
{
    int iVar1;
    long lVar2;
    undefined8 uVar3;
    char acStack_90 [128];

    lVar2 = *(long *)(param_1 + 0x18);
    iVar1 = (**(code **)(lVar2 + 0x538))(param_1, param_3, 0);
    if (iVar1 == 0) {
        uVar3 = 0;
    }
    else {
        __memcpy_chk(acStack_90, iVar1, 0x80, 0x80);
        uVar3 = FUN_00012b10(acStack_90);
    }
    return uVar3;
}
```

关键标识符含义：`undefined8` = 未推断出的 8 字节类型；`FUN_00012a4c` = 未命名函数 (地址)；`param_1` = 自动参数名；`acStack_90` = 栈偏移 0x90 的 char 数组；`*(long *)(param_1 + 0x18)` = 需要恢复的结构体成员访问。

### 修复类型和函数签名

分析 Android SO 时，第一步通常是修复 JNI 函数签名。以上面的例子为例：

1. **修改函数签名**: 右键函数名 -> `Edit Function Signature`，将 `undefined8 FUN_00012a4c(long, long, long)` 改为 `jboolean native_verify(JNIEnv *env, jobject thiz, jstring input)`
2. **修复结构体访问**: 修改参数类型后，`*(long *)(param_1 + 0x18)` 会自动解析为结构体成员
3. **重命名局部变量**: 右键变量 -> `Rename Variable`（或按 `L`），根据上下文取有意义的名称

修复后的反编译输出对比：

```c
// 修复前
undefined8 FUN_00012a4c(long param_1, long param_2, long param_3) { ... }

// 修复后
jboolean native_verify(JNIEnv *env, jobject thiz, jstring input) {
    const char *inputStr;
    char buffer[128];
    jboolean result;

    inputStr = (*env)->GetStringUTFChars(env, input, 0);
    if (inputStr == NULL) {
        result = JNI_FALSE;
    }
    else {
        __memcpy_chk(buffer, inputStr, 0x80, 0x80);
        result = do_verify(buffer);
    }
    return result;
}
```

可以看到，修复类型后代码的可读性有了质的飞跃。

---

## Ghidra Script 实战

Ghidra 强大的脚本能力是其核心优势之一。支持 Java 和 Python (Jython) 两种脚本语言。

### 打开 Script Manager

在 Code Browser 中，点击顶部菜单栏的绿色播放按钮图标（或 `Window -> Script Manager`），打开 **Script Manager**。这里有大量 NSA 官方和社区贡献的预置脚本。

### 脚本基础 - FlatAPI

Ghidra 脚本的核心是 `FlatAPI`，它提供了一系列简洁的接口来操作程序数据。以下是常用的 API 对象：

| API 对象                    | 用途                                 |
| :-------------------------- | :----------------------------------- |
| `currentProgram`            | 当前程序对象，获取所有程序信息的入口 |
| `currentAddress`            | 当前光标所在的地址                   |
| `currentSelection`          | 当前选中的地址范围                   |
| `getFunctionManager()`      | 函数管理器，增删改查函数             |
| `getMemory()`               | 内存管理器，读写程序内存             |
| `getSymbolTable()`          | 符号表，管理符号                     |
| `getDataTypeManager()`      | 数据类型管理器                       |
| `getDecompInterface()`      | 反编译器接口 (仅 Java)              |
| `toAddr(long)`              | 将整数转换为 Address 对象            |
| `getBytes(addr, length)`    | 从指定地址读取字节                   |
| `createFunction(addr, name)` | 在指定地址创建函数                  |

### 示例 1: 列出所有函数

```python
# list_functions.py - 列出所有函数名称和地址
from ghidra.program.model.symbol import SymbolType

print("--- All Functions ---")
func_manager = currentProgram.getFunctionManager()
funcs = func_manager.getFunctions(True)  # True means iterate in address order
count = 0
for func in funcs:
    print("{} at {}".format(func.getName(), func.getEntryPoint()))
    count += 1
print("Total functions: {}".format(count))
```

### 示例 2: 查找所有加密相关函数

在 Android 逆向中，经常需要快速定位加密相关的代码：

```python
# find_crypto.py - 查找潜在的加密/签名相关函数和字符串
import re

keywords = ["aes", "des", "rsa", "md5", "sha256", "encrypt", "decrypt",
            "cipher", "hmac", "base64", "key", "iv", "salt", "pbkdf"]
pattern = re.compile("|".join(keywords), re.IGNORECASE)

# 搜索函数名
for func in currentProgram.getFunctionManager().getFunctions(True):
    if pattern.search(func.getName()):
        print("[FUNC] {} @ {}".format(func.getName(), func.getEntryPoint()))

# 搜索字符串
from ghidra.program.util import DefinedDataIterator
for data in DefinedDataIterator.definedStrings(currentProgram):
    val = str(data.getValue())
    if pattern.search(val):
        print("[STR] '{}' @ {}".format(val[:60], data.getAddress()))
```

### 示例 3: 批量重命名 sub_ 函数

当分析动态注册的 JNI 函数时，经常需要根据 `RegisterNatives` 的 methods 数组批量重命名函数：

```python
# rename_jni_methods.py - 根据已知映射关系重命名 JNI 函数
# 在分析 RegisterNatives 后，手动整理出映射关系

jni_mappings = {
    0x12a4c: "native_verify",
    0x12b10: "native_encrypt",
    0x12c80: "native_getKey",
    0x12d44: "native_init",
}

func_manager = currentProgram.getFunctionManager()
for addr_int, new_name in jni_mappings.items():
    addr = toAddr(addr_int)
    func = func_manager.getFunctionAt(addr)
    if func is not None:
        old_name = func.getName()
        func.setName(new_name, ghidra.program.model.symbol.SourceType.USER_DEFINED)
        print("Renamed: {} -> {} @ {}".format(old_name, new_name, addr))
    else:
        print("No function at {}".format(addr))
```

### 示例 4: Java 脚本 - 使用反编译器 API

Java 脚本可以直接调用 `DecompInterface` 来获取反编译输出，功能比 Python 脚本更强大。核心模式如下：

```java
// FindSuspiciousCalls.java - 在反编译输出中搜索可疑调用
DecompInterface decomp = new DecompInterface();
decomp.openProgram(currentProgram);

FunctionIterator funcs = currentProgram.getFunctionManager().getFunctions(true);
while (funcs.hasNext()) {
    Function func = funcs.next();
    DecompileResults results = decomp.decompileFunction(func, 30, monitor);
    if (results.decompileCompleted()) {
        String code = results.getDecompiledFunction().getC();
        // 在反编译的 C 代码文本中搜索 "dlopen", "ptrace", "system" 等关键词
        if (code.contains("dlopen")) {
            printf("[!] %s @ %s\n", func.getName(), func.getEntryPoint());
        }
    }
}
decomp.dispose();
```

---

## Headless 模式

Ghidra 的 Headless Analyzer (无头分析器) 允许在不启动 GUI 的情况下进行分析，非常适合批量处理和 CI/CD 集成。

### 基本用法

```bash
# 基本语法
<ghidra_install>/support/analyzeHeadless \
    <project_dir> <project_name> \
    -import <target_file> \
    [options]

# 实际例子: 导入并分析一个 SO 文件
~/tools/ghidra_11.2_PUBLIC/support/analyzeHeadless \
    /tmp/ghidra_projects MyProject \
    -import libsecurity.so \
    -overwrite \
    -log /tmp/ghidra_analysis.log
```

### 常用参数

| 参数                    | 说明                                          |
| :---------------------- | :-------------------------------------------- |
| `-import <file>`        | 导入文件进行分析                              |
| `-process <file>`       | 处理已导入项目中的文件                        |
| `-overwrite`            | 如果文件已存在则覆盖                          |
| `-recursive`            | 递归导入目录中的所有文件                      |
| `-postScript <script>`  | 分析完成后运行指定脚本                        |
| `-preScript <script>`   | 分析开始前运行指定脚本                        |
| `-scriptPath <dir>`     | 添加额外的脚本搜索路径                        |
| `-deleteProject`        | 分析完成后删除项目                            |
| `-noanalysis`           | 只导入不分析                                  |
| `-processor <lang>`     | 手动指定处理器架构                            |
| `-log <logfile>`        | 指定日志输出文件                              |

### 批量分析 APK 中所有 SO 文件

```bash
#!/bin/bash
# batch_analyze.sh - 批量分析 APK 中的所有 SO 文件
APK_PATH="$1"
GHIDRA_HOME="$HOME/tools/ghidra_11.2_PUBLIC"
PROJECT_DIR="/tmp/ghidra_batch"

EXTRACT_DIR=$(mktemp -d)
unzip -q "$APK_PATH" -d "$EXTRACT_DIR"

find "$EXTRACT_DIR/lib" -name "*.so" | while read SO_FILE; do
    SO_NAME=$(basename "$SO_FILE")
    echo "[*] Analyzing: $SO_NAME"
    "$GHIDRA_HOME/support/analyzeHeadless" \
        "$PROJECT_DIR" BatchAnalysis \
        -import "$SO_FILE" -overwrite \
        -postScript "find_crypto.py" \
        -log "/tmp/${SO_NAME}.log" 2>&1 | tail -3
done
rm -rf "$EXTRACT_DIR"
```

> **提示**: Headless 模式非常适合集成到 CI/CD 流水线中，例如在 GitHub Actions 中安装 JDK + Ghidra，然后对提交的样本自动运行分析脚本并上传报告。

---

## 常用插件与扩展

Ghidra 的生态系统正在快速成长，以下是 Android 逆向中最有价值的插件和扩展。

### GhidraDev (官方 Eclipse 插件)

用于在 Eclipse IDE 中开发 Ghidra 脚本和模块：

1. 在 Eclipse 中安装：`Help -> Install New Software...`
2. 添加 `<ghidra_install>/Extensions/Eclipse/GhidraDev/` 目录
3. 安装完成后可以创建 Ghidra 脚本项目和模块项目
4. 支持代码补全、调试等 IDE 功能

### ghidra2ida / ida2ghidra

在 Ghidra 和 IDA Pro 之间迁移分析数据：

- **用途**: 将 IDA 中的函数名、注释、结构体定义导入 Ghidra，反之亦然
- **场景**: 团队中部分成员使用 IDA，部分使用 Ghidra
- **安装**: 从 GitHub 下载对应版本，放入 `<ghidra_install>/Extensions/Ghidra/` 目录

### SVD-Loader

为嵌入式设备逆向提供 SVD (System View Description) 文件支持：

- 自动将硬件寄存器地址映射为有意义的名称
- 对于分析 IoT 设备固件、Android 内核模块非常有用

### 其他推荐插件

| 插件名               | 用途                                     |
| :------------------- | :--------------------------------------- |
| **GhidraOllvm**      | 辅助分析 OLLVM 混淆的二进制文件          |
| **Ghidra Firmware Utils** | 固件分析工具包                      |
| **Ghidra Kotlin**    | Kotlin 脚本支持                          |
| **ret-sync**         | 与动态调试器 (GDB/LLDB/x64dbg) 同步     |
| **Ghidra Patch Diff** | 二进制差异对比 (类似 BinDiff)           |
| **Awesome Ghidra**   | GitHub 上的插件收集项目，持续更新        |

### 安装插件的通用方法

```
1. 下载插件 ZIP 包
2. Ghidra 主界面: File -> Install Extensions...
3. 点击 "+" 按钮，选择 ZIP 包
4. 重启 Ghidra
```

---

## Ghidra vs IDA Pro 深度对比

在 Android 逆向的实际工作中，Ghidra 和 IDA Pro 各有千秋。以下从多个实际场景出发进行深度对比。

### 反编译质量对比

以一个典型的 Android SO 中的 AES 加密函数为例，对比两者的反编译输出：

**Ghidra 输出**:
```c
void FUN_00013a00(byte *param_1, byte *param_2, int param_3,
                  byte *param_4, int param_5)
{
    AES_KEY local_108;
    byte local_e0 [16];

    __memcpy_chk(local_e0, param_4, 0x10, 0x10);
    AES_set_encrypt_key(param_2, param_3 << 3, &local_108);
    AES_cbc_encrypt(param_1, param_1, (long)param_5,
                    &local_108, local_e0, 1);
    return;
}
```

**IDA Pro (Hex-Rays) 输出**:
```c
void __fastcall aes_cbc_encrypt_wrapper(
    uint8_t *data, const uint8_t *key,
    int key_len, uint8_t *iv, int data_len)
{
    AES_KEY expanded;
    uint8_t iv_copy[16];

    memcpy(iv_copy, iv, 16);
    AES_set_encrypt_key(key, 8 * key_len, &expanded);
    AES_cbc_encrypt(data, data, data_len, &expanded, iv_copy, 1);
}
```

**分析**: IDA Pro 的输出更干净，FLIRT 技术更好地识别了库函数，类型推断也更准确。但 Ghidra 的输出完全可以理解，经过手动修复类型后差距会大幅缩小。

### 功能对比详表

| 功能             | Ghidra                                 | IDA Pro                               |
| :--------------- | :------------------------------------- | :------------------------------------ |
| **ARM Thumb 切换** | 自动处理，偶尔出错                   | 极其准确                              |
| **FLIRT 签名**   | 支持 (Function ID)，库较少             | 极其丰富，识别率高                    |
| **结构体恢复**   | 手动为主，支持从 C 头文件导入          | 自动推断较好，Local Types 功能强大    |
| **字符串识别**   | 良好，支持 UTF-8/UTF-16               | 优秀，支持更多编码                    |
| **调试器**       | 内置但不成熟                           | 成熟强大，支持远程调试 Android        |
| **Patch 能力**   | 支持直接修改字节                       | 支持 Keypatch 等插件，更方便          |
| **导出 C 代码**  | 支持批量导出所有函数反编译结果         | 需要脚本辅助                          |
| **版本控制**     | Ghidra Server 内置                     | 无内置方案                            |
| **Python 版本**  | Jython (Python 2.7)                    | Python 3.x (IDAPython)               |
| **启动速度**     | 较慢 (Java 冷启动)                     | 快                                    |
| **大文件分析**   | 内存消耗较大，需调优                   | 优化良好                              |

### 如何选择

- **预算有限 / 个人学习 / 团队协作** -> Ghidra（免费 + Ghidra Server）
- **预算充足 + 需要动态调试** -> IDA Pro + 远程调试器
- **实际建议**: 对于 Android 逆向入门者和独立研究者，Ghidra 是最佳选择。对于企业级漏洞挖掘团队，IDA Pro 仍然是首选。两者并不互斥，很多专业人员同时使用。

---

## 高级技巧

### 自定义数据类型

在分析 Android SO 时，经常遇到复杂的自定义数据结构。Ghidra 的 Data Type Manager 支持多种方式定义：

**方法 1: 图形界面创建**

1. Data Type Manager 右键 -> `New -> Structure`
2. 在弹出的结构体编辑器中添加成员
3. 设置每个成员的类型、大小和名称

**方法 2: 从 C 头文件导入**

```c
// 保存为 custom_types.h，通过 Parse C Source 导入
struct AppConfig {
    int version;
    int flags;
    char app_id[64];
    char secret_key[32];
    unsigned long timestamp;
    int (*callback)(void*, int);
};

struct EncryptContext {
    unsigned char key[32];
    unsigned char iv[16];
    int key_length;
    int mode;        // 0=ECB, 1=CBC, 2=CTR
    void *cipher_ctx;
};
```

**方法 3: 在反编译窗口中直接创建**

在反编译输出中看到类似 `*(int *)(param_1 + 0x44)` 的模式时：
1. 右键 `param_1` -> `Auto Create Structure`
2. Ghidra 会自动根据所有对该指针的偏移访问生成结构体
3. 然后手动完善各字段的名称和类型

### RTTI 信息恢复

对于 C++ 编写的 SO 文件，RTTI (Run-Time Type Information) 信息可以帮助恢复类层次结构：

1. Ghidra 内置了基本的 RTTI 分析支持
2. 在 Analysis Options 中确保 `GCC RTTI Analyzer` 已启用
3. 分析完成后，在 Symbol Tree 中搜索 `typeinfo` 或 `vtable` 前缀
4. 通过虚函数表 (vtable) 可以还原类的继承关系和虚函数列表

```
// 典型的 vtable 结构 (Ghidra 中查看)
//
// vtable for MyClass:
//   +0x00: offset_to_top (0)
//   +0x08: typeinfo pointer -> typeinfo for MyClass
//   +0x10: MyClass::method1()
//   +0x18: MyClass::method2()
//   +0x20: MyClass::~MyClass()
```

可以编写脚本遍历 vtable 中的每个指针，读取对应的函数地址并批量重命名为 `ClassName::vfunc_N` 的格式，快速恢复类的方法列表。

### PDB 与外部符号加载

虽然 Android SO 通常不带 PDB 文件，但在以下场景中外部符号加载很有用：

- **调试版本 SO**: 开发者可能保留了带符号的 SO 文件，从 `obj/` 目录中获取
- **系统库**: Android AOSP 提供了带符号的系统库，可以提升分析质量
- **DWARF 调试信息**: 某些 SO 保留了 DWARF 信息，Ghidra 会在导入时自动解析

可以用 `readelf -S libtarget.so | grep debug` 检查是否包含 DWARF 调试信息。如果有 `.debug_info` 等段，Ghidra 会在导入时自动解析。也可以通过 `File -> Load PDB File...` 手动加载外部符号文件。

### Ghidra Server 协作分析

Ghidra Server 提供版本控制和并发分析能力。服务端通过 `<ghidra_install>/server/` 目录下的脚本管理：`svrInstall` 初始化、`ghidraSvr start` 启动、`svrAdmin -add <user>` 添加用户。客户端通过 `File -> New Project... -> Shared Project` 连接服务器（默认端口 13100），使用 `Check Out / Check In` 管理文件，工作流类似 SVN。

### 实用小技巧汇总

1. **快速查看某地址被谁引用**: 选中地址后按 `X`，查看所有交叉引用 (Xrefs)
2. **搜索常量值**: `Search -> For Scalars...`，输入可疑的魔数 (如 AES 的 S-Box 值 `0x63`)
3. **对比两个函数**: `Window -> Function Comparison`，并排查看两个函数的汇编和反编译
4. **书签标记**: `Ctrl+D` 在当前地址创建书签，方便后续快速跳转
5. **导出反编译结果**: `File -> Export Program...`，选择 `C/C++` 格式，可以导出所有函数的反编译伪代码
6. **Undo/Redo**: `Ctrl+Z` / `Ctrl+Shift+Z`，Ghidra 支持几乎无限次撤销
7. **自动注释**: `Edit -> Tool Options -> Listing Fields -> Plate Comment`，设置自动显示函数的交叉引用摘要
8. **内存搜索**: `Search -> Memory...`，支持十六进制字节序列搜索，适合查找特征码

---

## 优缺点分析

### 优点

- **免费与开源**: 无任何费用，社区可以审查和贡献代码。
- **强大的反编译器**: 内置的高质量反编译器是其最大的卖点，足以媲美甚至在某些方面超越昂贵的商业软件。
- **跨平台**: 基于 Java，可以在 Windows, macOS, Linux 上无差别运行。
- **优秀的协作功能**: Ghidra Server 的存在使得团队协作变得非常容易。
- **Headless 模式**: 强大的命令行批处理能力，适合自动化流水线和 CI 集成。
- **完整的处理器支持**: 对 ARM/ARM64/MIPS 等 Android 相关架构支持完善。
- **活跃的社区**: NSA 持续维护，GitHub 上社区活跃，新功能和修复更新频繁。

### 缺点

- **性能**: 基于 Java Swing 的 UI 在处理超大型二进制文件时，可能会感到卡顿，性能不如 IDA Pro。
- **生态系统**: 虽然正在快速发展，但插件和社区支持的成熟度仍然不及 IDA Pro 经营多年的生态。
- **原生调试器**: Ghidra 的调试器功能相对较弱，不如 IDA Pro 和 x64dbg 等专用调试器成熟。
- **Python 版本**: 内置的 Jython 仅支持 Python 2.7，无法使用现代 Python 3 库（Ghidrathon 扩展可解决此问题）。
- **学习资源**: 相比 IDA Pro 数十年积累的书籍和教程，Ghidra 的高质量学习资源仍然偏少。
