# 00-Foundations Summary

本章节介绍了 Android 逆向工程的基础知识。

## 主要内容

- **Android 系统架构**: Linux 内核、Runtime (ART/Dalvik)、Framework 层解析。
- **APK 文件结构**: `classes.dex`, `AndroidManifest.xml`, `resources.arsc` 及其作用。
- **ARM 汇编基础**: 寄存器、常见指令 (MOV, B/BL, CMP)、栈平衡、函数调用约定 (ATPCS)。
- **Smali 汇编**: 了解 Smali 语法，它是静态分析 DEX 文件最常用的中间语言。
- **JNI 与 NDK**: Java Native Interface 工作原理，`.so` 文件的加载与执行。
