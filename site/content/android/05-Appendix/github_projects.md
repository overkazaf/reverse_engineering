---
title: "逆向工程 GitHub 开源项目"
date: 2024-12-31
tags: ["代理池", "Frida", "SSL Pinning", "Ghidra", "DEX", "资源"]
weight: 10
---

# 逆向工程 GitHub 开源项目

本列表旨在收集和分类逆向工程领域的优秀开源项目，方便查阅和学习。

## 目录

- [逆向工程领域相关的 GitHub 开源项目](#逆向工程领域相关的-github-开源项目)
  - [本列表旨在收集和分类逆向工程领域的优秀开源项目，方便查阅和学习。](#本列表旨在收集和分类逆向工程领域的优秀开源项目方便查阅和学习)
  - [目录](#目录)
    - [1. 动态分析与插桩工具](#1-动态分析与插桩工具)
    - [2. 反汇编器与反编译器](#2-反汇编器与反编译器)
    - [3. 调试器](#3-调试器)
    - [4. 静态分析与二进制分析](#4-静态分析与二进制分析)
    - [5. android 平台](#5-android-平台)
    - [6. 多平台与通用工具](#6-多平台与通用工具)
    - [7. Hex 编辑器](#7-hex-编辑器)
    - [8. 脱壳与反混淆](#8-脱壳与反混淆)
    - [9. 固件分析](#9-固件分析)
    - [10. Apple 平台 (iOS/macOS)](#10-apple-平台-iosmacos)
    - [11. 其他与资源](#11-其他与资源)

---

### 1. 动态分析与插桩工具

| 项目                                                                                                                        | Star 数量 | 描述                                                                   |
| --------------------------------------------------------------------------------------------------------------------------- | --------- | ---------------------------------------------------------------------- |
| [frida/frida](https://github.com/frida/frida)                                                                               | 14.5k     | 跨平台动态插桩框架，支持 Windows, macOS, Linux, iOS, Android, 和 QNX。 |
| [DynamoRIO/dynamorio](https://github.com/DynamoRIO/dynamorio)                                                               | 1.8k      | Google 出品的跨平台动态二进制插桩框架。                                |
| [intel/pin](https://www.intel.com/content/www/us/en/developer/articles/tool/pin-a-dynamic-binary-instrumentation-tool.html) | N/A       | Intel 出品的动态二进制插桩框架。                                       |
| [googleprojectzero/winafl](https://github.com/googleprojectzero/winafl)                                                     | 2.1k      | AFL 的一个分支，用于对 Windows 二进制文件进行模糊测试。                |
| [processhacker/processhacker](https://github.com/processhacker/processhacker)                                               | 3.2k      | 强大的多用途工具，用于监控系统资源、调试软件和检测恶意软件。           |
| [eronnen/procmon-parser](https://github.com/eronnen/procmon-parser)                                                           | 170       | Sysinternals Process Monitor (Procmon) 的日志解析器。                  |
| [microsoft/Detours](https://github.com/microsoft/detours)                                                                   | 1.9k      | 微软官方的 API Hooking 工具库。                                        |
| [easyhook/EasyHook](https://github.com/easyhook/EasyHook)                                                                   | 1.8k      | 强大的 Windows API Hooking 库。                                        |
| [tmate-io/tmate](https://github.com/tmate-io/tmate)                                                                         | 3.5k      | 即时终端共享工具。                                                     |
| [lief-project/LIEF](https://github.com/lief-project/LIEF)                                                                   | 4k        | 用于解析、修改和抽象 ELF, PE, MachO 格式的库。                         |
| [qbdi/QBDI](https://github.com/qbdi/QBDI)                                                                                   | 680       | 基于 LLVM 的动态二进制插桩框架。                                       |
| [jmpews/dobby](https://github.com/jmpews/dobby)                                                                             | 1.6k      | 轻量级、多平台、多架构的 Hook 框架。                                   |
| [aslody/whale](https://github.com/aslody/whale)                                                                             | 880       | 跨平台的 Hook 框架 (Android/iOS/Linux/macOS)。                         |
| [iqiyi/xHook](https://github.com/iqiyi/xHook)                                                                               | 1.6k      | 用于 Android aarch64/arm/x86 平台的 PLT hook 库。                      |
| [facebook/fishhook](https://github.com/facebook/fishhook)                                                                   | 3.8k      | 在 iOS/macOS 上动态重绑定 Mach-O 二进制文件中的符号。                  |

### 2. 反汇编器与反编译器

| 项目                                                                              | Star 数量 | 描述                                                     |
| --------------------------------------------------------------------------------- | --------- | -------------------------------------------------------- |
| [NationalSecurityAgency/ghidra](https://github.com/NationalSecurityAgency/ghidra) | 47.9k     | NSA 出品的软件逆向工程框架，包含反编译器。               |Inline Hook 原理| [avast/retdec](https://github.com/avast/retdec)                                   | 8.2k      | 基于 LLVM 的可重定向机器码反编译器。                     |
| [yegord/snowman](https://github.com/yegord/snowman)                               | 1.8k      | 支持 x86, ARM 和 x86-64 的反编译器。                     |
| [aquynh/capstone](https://github.com/aquynh/capstone)                             | 7.4k      | 强大的多架构反汇编框架。                                 |
| [keystone-engine/keystone](https://github.com/keystone-engine/keystone)           | 3.9k      | 轻量级多架构汇编器框架。                                 |
| [unicorn-engine/unicorn](https://github.com/unicorn-engine/unicorn)               | 7.5k      | 基于 QEMU 的多架构 CPU 模拟器框架。                      |
| [lifting-bits/mcsema](https://github.com/lifting-bits/mcsema)                     | 1.7k      | 将 x86/64, aarch64 二进制文件提升到 LLVM IR。            |
| [avast/retdec-idaplugin](https://github.com/avast/retdec-idaplugin)           | 500+      | RetDec 反编译器的 IDA 插件。                             |
| [airbus-seclab/bincat](https://github.com/airbus-seclab/bincat)                   | 1k        | 二进制代码静态分析工具，支持值分析、污点分析和类型推断。 |

### 3. 调试器

| 项目                                                                    | Star 数量 | 描述                                                      |
| ----------------------------------------------------------------------- | --------- | --------------------------------------------------------- |
| [x64dbg/x64dbg](https://github.com/x64dbg/x64dbg)                       | 45.3k     | Windows 平台开源的 x64/x32 调试器。                       |
| [gdb/gdb](https://www.gnu.org/software/gdb/)                            | N/A       | GNU 项目调试器。                                          |
| [rizinorg/cutter](https://github.com/rizinorg/cutter)                 | 15.6k     | radare2 的 GUI 界面。                                     |
| [hugsy/gef](https://github.com/hugsy/gef)                               | 6.4k      | GDB 的现代化插件，用于漏洞利用和逆向。                    |
| [pwndbg/pwndbg](https://github.com/pwndbg/pwndbg)                       | 6.7k      | GDB 的一个插件，辅助 pwn。                                |
| [longld/peda](https://github.com/longld/peda)                           | 5.7k      | GDB PEDA - Python Exploit Development Assistance for GDB. |
| [voltron/voltron](https://github.com/snare/voltron)                     | 5.3k      | 一个可扩展的、跨平台的调试器 UI 工具包。                  |
| [microsoft/WinDbg-Samples](https://github.com/microsoft/WinDbg-Samples) | 300+      | WinDbg 的示例扩展、脚本和 API 用法。                      |
| [pdbpp/pdbpp](https://github.com/pdbpp/pdbpp)                           | 1.4k      | Python 调试器 (pdb) 的一个增强版。                        |
| [x64dbg/x64dbgpy](https://github.com/x64dbg/x64dbgpy)         | 300+      | 用于 x64dbg 的 Python 脚本插件。                          |

### 4. 静态分析与二进制分析

| 项目                                                                | Star 数量 | 描述                                                      |
| ------------------------------------------------------------------- | --------- | --------------------------------------------------------- |
| [angr/angr](https://github.com/angr/angr)                           | 7.3k      | 强大的二进制分析平台，支持符号执行。                      |
| [trailofbits/manticore](https://github.com/trailofbits/manticore)   | 2k        | 动态二进制分析工具，支持符号执行、污点分析。              |
| [JonathanSalwan/triton](https://github.com/JonathanSalwan/triton)   | 2.7k      | 动态二进制分析 (DBA) 框架。                               |
| [google/binexport](https://github.com/google/binexport)             | 450+      | 将反汇编从 IDA Pro, Binary Ninja, Ghidra 导出到 BinNavi。 |
| [google/binnavi](https://github.com/google/binnavi)                 | 2.8k      | 二进制代码逆向工程和分析的图形化工具。                    |
| [Gallopsled/pwntools](https://github.com/Gallopsled/pwntools)       | 11.2k     | CTF 框架和漏洞利用开发库。                                |
| [erocarrera/pefile](https://github.com/erocarrera/pefile)           | 1.3k      | 用于解析和操作 PE 文件的 Python 模块。                    |
| [eliben/pyelftools](https://github.com/eliben/pyelftools)           | 1k        | 用于解析和分析 ELF 文件和 DWARF 调试信息的 Python 库。    |
| [lvc/vtable-dumper](https://github.com/lvc/vtable-dumper)           | 250       | 用于从 PE/ELF 文件中 dump 虚函数表的工具。                |

### 5. android 平台

| 项目                                                                                              | Star 数量 | 描述                                                                |
| ------------------------------------------------------------------------------------------------- | --------- | ------------------------------------------------------------------- |
| [iBotPeaches/Apktool](https://github.com/iBotPeaches/Apktool)                                     | 18.2k     | 用于逆向 Android apk 文件的工具。                                   |
| [pxb1988/dex2jar](https://github.com/pxb1988/dex2jar)                                             | 12k       | 用于处理 .dex 和 .class 文件的工具。                                |
| [skylot/jadx](https://github.com/skylot/jadx)                                                     | 38.6k     | Dex 到 Java 的反编译器。                                            |
| [JesusFreke/smali](https://github.com/JesusFreke/smali)                                           | 4.4k      | Android 的 smali/baksmali 汇编器/反汇编器。                         |
| [MobSF/Mobile-Security-Framework-MobSF](https://github.com/MobSF/Mobile-Security-Framework-MobSF) | 16.4k     | 自动化的移动应用 (Android/iOS/Windows) 安全测试和恶意软件分析框架。 |
| [sensepost/objection](https://github.com/sensepost/objection)                                     | 8.3k      | 运行时移动安全评估框架，基于 Frida。                                |
| [Fuzion24/JustTrustMe](https://github.com/Fuzion24/JustTrustMe)                                   | 2.2k      | 禁用 SSL 证书检查的 Xposed 模块。                                   |
| [ac-pm/Inspeckage](https://github.com/ac-pm/Inspeckage)                                           | 1.8k      | Android 包动态分析工具，带 API hook 功能。                          |
| [rednaga/APKiD](https://github.com/rednaga/APKiD)                                                 | 850       | 用于识别 Android 安装包中加壳、混淆和其它异常的工具。               |
| [CalebFenton/simplify](https://github.com/CalebFenton/simplify)                                   | 3.2k      | 通用 Android 反混淆工具。                                           |
| [strazzere/android-unpacker](https://github.com/strazzere/android-unpacker)                       | 900+      | Defcon 22 上演示的 Android 脱壳工具。                               |
| [asLody/AndHook](https://github.com/asLody/AndHook)                                               | 600+      | Android 动态插桩框架。                                              |
| [turing-technician/fasthook](https://github.com/turing-technician/fasthook)                       | 400+      | Android ART Hook 框架。                                             |
| [wrbug/dumpdex](https://github.com/wrbug/dumpdex)                                                 | 1.9k      | Android 脱壳工具。                                                  |
| [topjohnwu/Magisk](https://github.com/topjohnwu/Magisk)                                           | 35k+      | Android 系统无感知 Root 工具。                                      |
| [LSPosed/LSPosed](https://github.com/LSPosed/LSPosed)                                             | 15k+      | 基于 Riru/Zygisk 的 ART Hook 框架 (Xposed 替代品)。                 |
| [Genymobile/scrcpy](https://github.com/Genymobile/scrcpy)                                         | 90k+      | 高性能的 Android 投屏与控制工具。                                   |
| [shroudedcode/apk-mitm](https://github.com/shroudedcode/apk-mitm)                                 | 3k+       | 自动修改 APK 以便进行 HTTPS 抓包的工具。                            |
| [r0ysue/r0capture](https://github.com/r0ysue/r0capture)                                           | 4k+       | 基于 Frida 的安卓应用层抓包通杀脚本。                               |

### 6. 多平台与通用工具

| 项目                                                                                | Star 数量 | 描述                                                   |
| ----------------------------------------------------------------------------------- | --------- | ------------------------------------------------------ |
| [upx/upx](https://github.com/upx/upx)                                               | 4.9k      | 极致的可执行文件压缩器。                               |
| [horsicq/Detect-It-Easy](https://github.com/horsicq/Detect-It-Easy)                 | 5.8k      | 用于判断文件类型的程序，支持 Windows, Linux, macOS。   |
| [DidierStevens/DidierStevensSuite](https://github.com/DidierStevens/DidierStevensSuite)                             | 450+      | 在文件中搜索经过 XOR, ROL, ROT 或 SHIFT 编码的字符串。 |
| [google/santa](https://github.com/google/santa)                                     | 3.1k      | 用于 macOS 的二进制文件白名单/黑名单系统。             |
| [trailofbits/osquery-extensions](https://github.com/trailofbits/osquery-extensions) | 300+      | osquery 的扩展，用于增强安全分析。                     |
| [checkra1n/pongoOS](https://github.com/checkra1n/pongoOS)                           | 1.2k      | checkra1n 使用的 Pre-boot eXecution Environment。      |
| [mitmproxy/mitmproxy](https://github.com/mitmproxy/mitmproxy)                       | 33k+      | 交互式的 HTTPS 代理，用于调试、测试和渗透。            |

### 7. Hex 编辑器

| 项目                                                                  | Star 数量 | 描述                            |
| --------------------------------------------------------------------- | --------- | ------------------------------- |
| [gdabah/distorm](https://github.com/gdabah/distorm)       | 500+      | x86/AMD64 的快速反汇编库。      |
| [WerWolv/ImHex](https://github.com/WerWolv/ImHex)                     | 3k        | 一个功能丰富的现代 Hex 编辑器。 |

### 8. 脱壳与反混淆

| 项目                                                                  | Star 数量 | 描述                                       |
| --------------------------------------------------------------------- | --------- | ------------------------------------------ |
| [de4dot/de4dot](https://github.com/de4dot/de4dot)                     | 6.5k      | .NET 反混淆器和脱壳器。                    |
| [fireeye/flare-floss](https://github.com/fireeye/flare-floss)         | 1.5k      | 自动从恶意软件中提取混淆后的字符串。       |
| [ioncodes/dnpatch](https://github.com/ioncodes/dnpatch)               | 500+      | 用于修补 .NET 程序集的工具。               |
| [hluwa/frida-dexdump](https://github.com/hluwa/frida-dexdump)         | 3k+       | 基于 Frida 的快速 Dex 内存导出工具。       |
| [Perfare/Il2CppDumper](https://github.com/Perfare/Il2CppDumper)       | 7k+       | Unity Il2Cpp 逆向工具，还原 DLL 和头文件。 |

### 9. 固件分析

| 项目                                                                                    | Star 数量 | 描述                                 |
| --------------------------------------------------------------------------------------- | --------- | ------------------------------------ |
| [ReFirmLabs/binwalk](https://github.com/ReFirmLabs/binwalk)                             | 10.1k     | 用于分析、逆向和提取固件镜像的工具。 |
| [craigz28/firmwalker](https://github.com/craigz28/firmwalker)                               | 1k        | 自动在固件中搜索敏感信息的脚本。     |
| [attify/firmware-analysis-toolkit](https://github.com/attify/firmware-analysis-toolkit) | 1k        | 用于固件安全测试的工具包。           |
| [0xff7/IoTSecurity101](https://github.com/0xff7/IoTSecurity101)               | 500+      | 物联网安全入门。                     |

### 10. Apple 平台 (iOS/macOS)

| 项目                                                                          | Star 数量 | 描述                                                              |
| ----------------------------------------------------------------------------- | --------- | ----------------------------------------------------------------- |
| [nygard/class-dump](https://github.com/nygard/class-dump)                     | 2.6k      | 从 Mach-O 文件生成 Objective-C 头文件。                           |
| [KJCracks/Clutch](https://github.com/KJCracks/Clutch)                         | 2.8k      | 快速的 iOS 可执行文件 dumper。                                    |
| [alonemonkey/MonkeyDev](https://github.com/alonemonkey/MonkeyDev)             | 4.5k      | iOS Tweak 开发工具，无需越狱。                                    |
| [facebook/chisel](https://github.com/facebook/chisel)                         | 8.3k      | 辅助调试 iOS 应用的 LLDB 命令集合。                               |
| [nabla-c0d3/ssl-kill-switch2](https://github.com/nabla-c0d3/ssl-kill-switch2) | 1.6k      | 黑盒工具，用于在 iOS 和 macOS 应用中禁用 SSL 证书验证。           |
| [ptoomey3/Keychain-Dumper](https://github.com/ptoomey3/Keychain-Dumper)       | 1k        | 在越狱设备上检查哪些钥匙串项可被访问。                            |
| [limneos/classdump-dyld](https://github.com/limneos/classdump-dyld)           | 450+      | 无需从 dyld_shared_cache 中提取即可 class-dump 任何 Mach-O 文件。 |

### 11. 其他与资源

| 项目                                                                      | Star 数量 | 描述                                       |
| ------------------------------------------------------------------------- | --------- | ------------------------------------------ |
| [firmianay/security-paper](https://github.com/firmianay/security-paper)   | 1.7k      | 安全领域的一些经典论文。                   |
| [enaqx/awesome-pentest](https://github.com/enaqx/awesome-pentest)         | 18k+      | 精选的渗透测试资源、工具和其它很棒的东西。 |
| [carpedm20/awesome-hacking](https://github.com/carpedm20/awesome-hacking) | 9k+       | 精选的黑客资源、工具和教程。               |
| [onethawt/idaplugins-list](https://github.com/onethawt/idaplugins-list)   | 1.9k      | IDA Pro 插件列表。                         |
| [Siguza/ios-resources](https://github.com/Siguza/ios-resources)           | 700+      | iOS 黑客相关的有用资源。                   |
| [michalmalik/osx-re-101](https://github.com/michalmalik/osx-re-101)       | 1.4k      | OSX/iOS 逆向资源。                         |
