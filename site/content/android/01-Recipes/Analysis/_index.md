---
title: "分析技术"
date: 2024-12-09
tags: ["Android", "逆向分析"]
weight: 30
---

本节聚焦 Android 逆向中的核心分析技术，涵盖动态分析、协议逆向、签名算法破解以及各类代码混淆的对抗方法。无论是 Java 层的 VMP 保护还是 Native 层的 OLLVM 混淆，都能在此找到对应的实战方案。

## 章节导航

### 动态分析与追踪
- [使用动态分析验证和探索 Android App 的运行时行为](dynamic_analysis_deep_dive) - 深入运行时动态分析的方法论与工具链
- [eBPF Android 逆向实战](ebpf_android_reversing) - 利用 eBPF 进行内核级追踪与逆向分析

### 混淆与反混淆
- [JavaScript Obfuscator (OB 混淆) 分析](js_obfuscator) - 针对 JS OB 混淆的识别与还原技术
- [JavaScript VMP 逆向工程](js_vmp) - JavaScript 虚拟机保护方案的逆向方法
- [Native 层字符串混淆与逆向](native_string_obfuscation) - Native 代码中字符串加密的识别与解密
- [OLLVM 反混淆实战](ollvm_deobfuscation) - 对抗 OLLVM 控制流平坦化、虚假控制流等混淆手段

### 协议与签名
- [协议分析实战](protocol_analysis) - 网络协议的抓取、解析与还原技术
- [签名算法逆向 (Sign Analysis)](sign_analysis) - 逆向分析 App 请求签名的生成算法
- [VMP 逆向工程实战](vmp_analysis) - 虚拟机保护方案的深度分析与还原
