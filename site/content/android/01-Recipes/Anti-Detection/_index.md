---
title: "反检测对抗"
date: 2025-05-30
tags: ["反检测", "Android", "SSL Pinning", "Root检测"]
weight: 30
---

本节专注于 Android 应用中各类检测与防护机制的分析与绕过。内容涵盖调试器检测、设备指纹识别、验证码防护以及应用加固识别等攻防对抗技术，帮助安全研究人员理解和突破目标应用的安全防线。

## 章节导航

### 调试检测绕过
- [绕过 App 对 Frida 的检测](frida_anti_debugging) - 分析并绕过常见的 Frida 检测手段
- [绕过 App 对 Xposed 的检测](xposed_anti_debugging) - 分析并绕过 Xposed 框架的检测机制

### 设备与环境对抗
- [设备指纹技术深度解析与绕过策略](device_fingerprinting_and_bypass) - 深入理解设备指纹采集原理及对抗方法
- [主流应用加固厂商及其特征识别](app_hardening_identification) - 识别梆梆、爱加密、360 等加固方案的特征

### 风控与验证码
- [验证码绕过技术：滑块与点选篇](captcha_bypassing_techniques) - 滑块验证码与点选验证码的自动化绕过
- [移动端安全与风控技术](mobile_app_sec_and_anti_bot) - 移动端风控系统的技术体系与对抗策略
