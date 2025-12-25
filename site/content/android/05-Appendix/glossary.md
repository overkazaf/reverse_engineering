---
title: "术语表 (Glossary)"
date: 2025-08-25
tags: ["Native层", "Ghidra", "Frida", "DEX", "资源", "OLLVM"]
weight: 10
---

# 术语表 (Glossary)

收集了 Android 逆向工程中常见的术语和缩写。

## A

- **ADB (Android Debug Bridge)**: Android 调试桥，一个通用的命令行工具，允许你与模拟器实例或连接的 Android 设备进行通信。
- **AOSP (Android Open Source Project)**: Android 开源项目，即 Android 系统的源代码。
- **APK (Android Package)**: Android 应用程序包，Android 操作系统使用的一种应用程序包文件格式。
- **ART (Android Runtime)**: Android 运行时，Android 5.0 引入的新的应用运行时环境，完全取代了 Dalvik。它使用 AOT (Ahead-Of-Time) 编译技术。
- **ARM**: 一种精简指令集 (RISC) 处理器架构，广泛用于移动设备。

## B

- **Bootloader**: 引导加载程序，在操作系统内核运行之前运行的一段小程序，负责加载操作系统。
- **Baksmali**: 一个将 dex 文件反汇编成 smali 文件的工具。

## D

- **Dalvik**: Google 早期为 Android 设计的虚拟机，使用 JIT (Just-In-Time) 编译。在 Android 5.0 后被 ART 取代。
- **DEX (Dalvik Executable)**: Android 平台的可执行文件格式，包含编译后的代码。
- **Dynamic Analysis (动态分析)**: 在程序运行时对其进行分析的技术，通常涉及调试、Hook 等。

## E

- **ELF (Executable and Linkable Format)**: 可执行与可链接格式，Linux 系统（包括 Android Native 层）使用的标准二进制文件格式。

## F

- **Frida**: 一个动态插桩工具包，允许开发者、逆向工程师和安全研究人员在运行时监视和修改应用程序的行为。

## G

- **Ghidra**: NSA 开源的软件逆向工程 (SRE) 框架。

## H

- **Hooking (挂钩)**: 一种拦截软件组件之间函数调用、消息或事件的技术，用于改变或监视系统的行为。

## I

- **IDA Pro (Interactive DisAssembler)**: 业界标准的交互式反汇编器和调试器。
- **IL2CPP**: Unity 游戏引擎的一种脚本后端，将 C# 代码转换为 C++ 代码，增加了逆向难度。

## J

- **JADX**: 一个将 DEX 文件反编译为 Java 代码的工具。
- **JNI (Java Native Interface)**: Java 本地接口，允许 Java 代码和其他语言（主要是 C/C++）写的代码进行交互。

## M

- **Magisk**: 一个开源的 Android Root 解决方案，以 "Systemless"（不修改系统分区）著称。
- **Manifest (AndroidManifest.xml)**: 每个 Android 应用都必须包含的文件，描述了应用的包名、组件、权限等基本信息。

## N

- **Native Code**: 通常指使用 C/C++ 编写的，直接编译为机器码的代码（相对于 Java/Kotlin 字节码）。
- **NDK (Native Development Kit)**: 一个工具集，允许开发者使用 C 和 C++ 实现应用的一部分。

## O

- **Obfuscation (混淆)**: 使代码难以理解但保持其功能不变的技术，用于保护知识产权或隐藏恶意行为。
- **OLLVM (Obfuscator-LLVM)**: 基于 LLVM 的代码混淆项目，常用于 Native 代码混淆。
- **OAT**: ART 运行时使用的私有 ELF 文件格式，包含 AOT 编译后的机器码。

## R

- **Recovery**: Android 设备的恢复模式，用于恢复出厂设置、刷入更新包等。
- **Rooting**: 获取 Android 设备超级用户 (Root) 权限的过程。
- **Riru**: 一个用于注入 Zygote 进程的模块，常作为其他模块（如 LSPosed）的基础。

## S

- **Smali**: Android 的 Dalvik 字节码的人类可读汇编语言。
- **Static Analysis (静态分析)**: 在不运行程序的情况下对其进行分析的技术。
- **So (Shared Object)**: Linux/Android 下的动态链接库文件，通常由 C/C++ 编写。

## V

- **VMP (Virtual Machine Protection)**: 虚拟机保护，一种高级混淆技术，将原始代码转换为自定义字节码并在自定义解释器中运行。

## X

- **Xposed**: 一个强大的 Android 框架，允许在不修改 APK 的情况下通过模块改变系统和应用的行为。

## Z

- **Zygote**: Android 系统中所有应用进程的父进程。
