# 01-Tooling Summary

本章节介绍了 Android 逆向工程生态中的核心工具。

## 主要内容

- **ADB (Android Debug Bridge)**: 常用命令 (shell, logcat, install/push/pull, port forwarding)。
- **Frida**: 动态插桩神器。介绍 frida-server 部署、JavaScript API (Java.use, Interceptor.attach)、frida-tools (trace, ps)。
- **IDA Pro**: 静态分析与反编译之王。快捷键、插件 (Keypatch)、远程调试设置。
- **JADX / GDA**: 优秀的 DEX 反编译器，用于快速查看 Java 源码。
- **Objection**: 基于 Frida 的运行时探索工具 (内存漫游、Class 搜索、Method Hook)。
