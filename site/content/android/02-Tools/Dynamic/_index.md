---
title: "动态分析工具"
date: 2024-08-02
tags: ["Android", "动态分析", "Frida", "Xposed"]
weight: 30
---

本节介绍 Android 逆向工程中主流的动态分析工具，包括 Hook 框架、模拟执行引擎、内核级工具等。每个工具都提供了使用指南和原理剖析，帮助你在实战中灵活选择和组合使用这些工具。

## 章节导航

### Frida
- [Frida 常用命令与脚本 API 大全](frida_guide) - Frida 命令行工具与 JavaScript API 的完整使用指南
- [Frida 核心模块与实现原理](frida_internals) - 深入分析 Frida 的架构设计与核心模块实现机制

### Unidbg
- [Unidbg 使用指南](unidbg_guide) - 基于 Unicorn 的 Android Native 模拟执行框架使用教程
- [Unidbg 内部原理](unidbg_internals) - Unidbg 的模拟执行引擎与系统调用实现原理

### Xposed
- [Xposed/LSPosed 使用指南](xposed_guide) - Xposed 框架及其现代替代方案 LSPosed 的安装与使用

### KernelSU
- [KernelSU 使用指南](kernelsu_guide) - 基于内核的 Root 方案 KernelSU 的安装配置与模块管理
- [KernelSU 内部原理](kernelsu_internals) - KernelSU 的内核实现机制与安全模型分析

### eBPF
- [eBPF 使用指南](ebpf_guide) - 利用 eBPF 进行 Android 内核级追踪与监控
- [eBPF 内部原理](ebpf_internals) - eBPF 虚拟机、验证器与 Map 机制的底层原理

### Magisk
- [Magisk 入门指南](magisk_guide) - Magisk 的安装、模块管理与 Root 隐藏配置
