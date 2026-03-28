---
title: "基础知识"
date: 2024-06-23
tags: ["Smali", "基础知识", "Android", "DEX"]
weight: 30
---

本章汇总了 Android 逆向工程所需的基础知识，包括系统组件、文件格式、汇编语言、运行时机制等核心概念。扎实的基础是进行高效逆向分析的前提，建议在实战之前系统性地掌握这些内容。

## 章节导航

### Android 基础
- [Android 四大组件](android_components) - Activity、Service、BroadcastReceiver、ContentProvider 详解
- [AndroidManifest.xml 深度解析](android_manifest) - 清单文件的结构、权限声明与组件注册
- [APK 文件结构详解](apk_structure) - APK 包的目录结构与各文件作用
- [DEX 文件格式](dex_format) - Dalvik Executable 文件的内部结构与解析方法

### 运行时与系统机制
- [Android Runtime (ART) 运行时机制](art_runtime) - ART 虚拟机的编译、执行与优化机制
- [Binder IPC 机制](binder_ipc) - Android 进程间通信的核心框架
- [SELinux 安全策略](selinux) - Android 强制访问控制的安全模型
- [Boot Image 与 GKI](boot_image_and_gki) - 启动镜像结构与通用内核映像

### 汇编与二进制分析
- [ARM 汇编入门 (Android Native)](arm_assembly) - ARM 架构汇编语言基础与常用指令
- [x86 与 ARM 汇编基础](x86_and_arm_assembly_basics) - 两大主流架构的汇编语法对比
- [Smali 语法速查](smali_syntax) - Dalvik 字节码的人类可读表示与常用语法
- [SO (ELF) 文件格式](so_elf_format) - 共享库文件的 ELF 格式结构解析
- [二进制分析工具链](binary_analysis_toolkit) - 常用二进制分析工具的功能与使用方法

### 其他工具与概念
- [Android Studio 调试工具集](android_studio_debug_tools) - Android Studio 内置调试与分析工具介绍
- [TOTP 时间同步动态验证码](totp) - 基于时间的一次性密码算法原理与实现
