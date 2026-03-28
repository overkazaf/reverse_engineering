---
title: "脱壳技术"
date: 2024-11-04
tags: ["Android", "加固", "脱壳", "SO修复"]
weight: 30
---

本节专注于 Android 应用加固的脱壳与 SO 文件的反混淆技术。内容涵盖主流加固方案的脱壳方法、SO 文件修复、花指令去除以及字符串混淆对抗，帮助安全研究人员还原被保护的应用原始代码。

## 章节导航

- [脱壳分析加固的 Android 应用](un-packing) - 主流加固方案的脱壳原理与实战操作流程
- [使用 Frida 脱壳加固 App 并修复 SO 文件](frida_unpacking_and_so_fixing) - 基于 Frida 的内存 dump 脱壳与 SO 文件修复技术
- [SO 文件反混淆：花指令识别与自动化去除](so_obfuscation_deobfuscation) - 识别和清除 SO 文件中的花指令混淆
- [SO 文件字符串混淆对抗指南](so_string_deobfuscation) - SO 文件中加密字符串的定位、分析与解密方法
