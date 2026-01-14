---
title: "进阶主题"
date: 2025-06-24
tags: ["Android", "高级", "底层原理"]
weight: 30
---

进阶主题涵盖 Android Native 层的高级逆向技术，包括系统定制、混淆对抗、运行时分析等深入内容。

## 章节导航

### 混淆与反混淆
- [花指令与 OLLVM 混淆技术深度解析](junk_code_and_ollvm_obfuscation) - 花指令识别与去除、OLLVM 控制流平坦化/虚假控制流/指令替换的原理与去混淆实战
- [SO 文件反调试与字符串混淆技术](so_anti_debugging_and_obfuscation) - init_array、字符串混淆、反调试技术及绕过方法

### 系统定制与底层
- [AOSP 设备定制](aosp_device_modification) - Android 源码修改与定制
- [AOSP 与系统定制](aosp_and_system_customization) - 深度系统定制技术
- [Magisk 与 LSPosed 内部原理](magisk_lsposed_internals) - Root 框架实现机制
- [最小化 Android 根文件系统](minimal_android_rootfs) - 精简系统构建

### 分析与模拟
- [SO 运行时模拟](so_runtime_emulation) - 使用 Unicorn/Qemu 模拟 SO 执行
- [Android 沙箱实现](android_sandbox_implementation) - 应用隔离与沙箱技术
