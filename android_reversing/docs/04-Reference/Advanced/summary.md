# 03-Advanced-Topics Summary

本章节深入探讨 Android 逆向中的高难度话题。

## 主要内容

- **Native 层逆向**:
  - Hook SO 层导出/未导出函数 (Interceptor, Module.findBaseAddress)。
  - Inline Hook 原理与检测。
  - JNITrace 使用。
- **混淆与加固**:
  - OLLVM (控制流平坦化、指令替换) 识别与还原。
  - 壳的原理 (一代壳、二代壳、VMP) 与脱壳机 (BlackDex, FART) 的使用。
- **反调试与检测**:
  - TracerPid 检测、端口检测、时间检测。
  - Root 检测、Frida 检测、模拟器检测 Bypass。
