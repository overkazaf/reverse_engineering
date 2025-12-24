---
title: "android 逆向工程 Cookbook"
date: 2025-12-25
weight: 1
---

# android 逆向工程 Cookbook

欢迎来到 **Android RE Cookbook** —— 一本实战导向的 Android 逆向工程实用手册。

本 Cookbook 采用**场景驱动**的组织方式，帮助你快速找到解决特定问题的方法，而非传统的知识点罗列。
---
## 🚀 新手？从这里开始

**完全新手？** 先完成 10 分钟快速入门，体验第一次 Hook！

👉 **[10 分钟快速入门](./00-Quick-Start/index.md)** - 安装 Frida 并完成第一次 Hook

**环境还没配置好？**
👉 **[环境配置指南](./00-Quick-Start/setup.md)** - 从零搭建逆向分析环境
---
## 📖 如何使用本 Cookbook

### 🎯 按需查找
- **遇到问题？** 直接查看 [Recipes](#recipes) 章节，找到对应场景的解决方案
- **学习工具？** 查看 [Tools](#tools) 章节，了解各类工具的使用方法
- **参考案例？** 浏览 [Case Studies](#case-studies)，学习实战分析流程
- **查阅资料？** 访问 [Reference](#reference)，深入理解底层原理

### 📚 学习路径
1. **新手入门**: Reference → Tools → Recipes
2. **实战为主**: Recipes → Tools → Case Studies
3. **进阶提升**: Case Studies → Reference/Advanced
---
## 🎯 Recipes

按场景分类的实战菜谱，提供可直接使用的解决方案。

### 🌐 [Network - 网络与加密](./01-Recipes/Network/)
解决网络抓包、加密分析、TLS指纹等问题。

- [Network Sniffing](./01-Recipes/Network/network_sniffing.md) - 网络协议分析与抓包
- [Crypto Analysis](./01-Recipes/Network/crypto_analysis.md) - 密码学分析
- [TLS Fingerprinting](./01-Recipes/Network/tls_fingerprinting_guide.md) - TLS指纹识别
- [JA3 Fingerprinting](./01-Recipes/Network/ja3_fingerprinting.md) - JA3指纹分析
- [JA4 Fingerprinting](./01-Recipes/Network/ja4_fingerprinting.md) - JA4指纹分析

### 🛡️ [Anti-Detection - 反检测与对抗](./01-Recipes/Anti-Detection/)
绕过各类检测机制，包括反调试、反Hook、验证码等。

- [Frida Anti Debugging](./01-Recipes/Anti-Detection/frida_anti_debugging.md) - Frida反调试绕过
- [Xposed Anti Debugging](./01-Recipes/Anti-Detection/xposed_anti_debugging.md) - Xposed反调试绕过
- [Captcha Bypassing](./01-Recipes/Anti-Detection/captcha_bypassing_techniques.md) - 验证码绕过
- [App Hardening Identification](./01-Recipes/Anti-Detection/app_hardening_identification.md) - 加固识别
- [Device Fingerprinting & Bypass](./01-Recipes/Anti-Detection/device_fingerprinting_and_bypass.md) - 设备指纹绕过
- [Mobile App Security & Anti Bot](./01-Recipes/Anti-Detection/mobile_app_sec_and_anti_bot.md) - 移动端安全与反机器人

### 📦 [Unpacking - 脱壳与修复](./01-Recipes/Unpacking/)
处理加壳应用的脱壳和修复工作。

- [Unpacking](./01-Recipes/Unpacking/un-packing.md) - 应用脱壳技术
- [Frida Unpacking & SO Fixing](./01-Recipes/Unpacking/frida_unpacking_and_so_fixing.md) - Frida脱壳与SO修复
- [SO Obfuscation Deobfuscation](./01-Recipes/Unpacking/so_obfuscation_deobfuscation.md) - SO混淆与反混淆
- [SO String Deobfuscation](./01-Recipes/Unpacking/so_string_deobfuscation.md) - SO字符串反混淆

### 🔬 [Analysis - 分析与调试](./01-Recipes/Analysis/)
静态分析、动态分析和代码混淆分析。

- [RE Workflow](./01-Recipes/Analysis/re_workflow.md) - 逆向工程工作流
- [Static Analysis Deep Dive](./01-Recipes/Analysis/static_analysis_deep_dive.md) - 静态分析深入
- [Dynamic Analysis Deep Dive](./01-Recipes/Analysis/dynamic_analysis_deep_dive.md) - 动态分析深入
- [OLLVM Deobfuscation](./01-Recipes/Analysis/ollvm_deobfuscation.md) - OLLVM反混淆
- [VMP Analysis](./01-Recipes/Analysis/vmp_analysis.md) - VMP分析
- [JS Obfuscator](./01-Recipes/Analysis/js_obfuscator.md) - JS混淆分析
- [JS VMP](./01-Recipes/Analysis/js_vmp.md) - JS虚拟机保护
- [Native String Obfuscation](./01-Recipes/Analysis/native_string_obfuscation.md) - Native字符串混淆

### 🤖 [Automation - 自动化与规模化](./01-Recipes/Automation/)
构建自动化分析系统和规模化解决方案。

- [Automation & Device Farming](./01-Recipes/Automation/automation_and_device_farming.md) - 自动化与群控
- [Dial Up Proxy Pools](./01-Recipes/Automation/dial_up_proxy_pools.md) - 动态代理池
- [Proxy Pool Design](./01-Recipes/Automation/proxy_pool_design.md) - 代理池设计
- [Scrapy](./01-Recipes/Automation/scrapy.md) - Scrapy爬虫框架
- [Scrapy Redis Distributed](./01-Recipes/Automation/scrapy_redis_distributed.md) - 分布式Scrapy
- [Docker Deployment](./01-Recipes/Automation/docker_deployment.md) - Docker部署
- [Virtualization & Containers](./01-Recipes/Automation/virtualization_and_containers.md) - 虚拟化与容器
- [Web Anti Scraping](./01-Recipes/Automation/web_anti_scraping.md) - Web反爬虫

### 📝 [Scripts - 即用脚本](./01-Recipes/Scripts/)
可直接使用的脚本集合。

- [Frida Script Examples](./01-Recipes/Scripts/frida_script_examples.md) - Frida脚本示例
- [Frida Common Scripts](./01-Recipes/Scripts/frida_common_scripts.md) - Frida常用脚本
- [Automation Scripts](./01-Recipes/Scripts/automation_scripts.md) - 自动化脚本
- [Native Hooking](./01-Recipes/Scripts/native_hooking.md) - Native Hook模式
- [Objection Snippets](./01-Recipes/Scripts/objection_snippets.md) - Objection代码片段
- [C For Emulation](./01-Recipes/Scripts/c_for_emulation.md) - C语言仿真
---
## 🔨 Tools

工具使用指南和原理剖析。

### ⚡ [Dynamic - 动态分析工具](./02-Tools/Dynamic/)
- [Frida Guide](./02-Tools/Dynamic/frida_guide.md) - Frida使用指南
- [Frida Internals](./02-Tools/Dynamic/frida_internals.md) - Frida内部原理
- [Xposed Guide](./02-Tools/Dynamic/xposed_guide.md) - Xposed使用指南
- [Xposed Internals](./02-Tools/Dynamic/xposed_internals.md) - Xposed内部原理
- [Unidbg Guide](./02-Tools/Dynamic/unidbg_guide.md) - Unidbg使用指南
- [Unidbg Internals](./02-Tools/Dynamic/unidbg_internals.md) - Unidbg内部原理

### 🔍 [Static - 静态分析工具](./02-Tools/Static/)
- [Ghidra Guide](./02-Tools/Static/ghidra_guide.md) - Ghidra使用指南
- [IDA Pro Guide](./02-Tools/Static/ida_pro_guide.md) - IDA Pro使用指南
- [Radare2 Guide](./02-Tools/Static/radare2_guide.md) - Radare2使用指南

### 📋 [Cheatsheets - 速查表](./02-Tools/Cheatsheets/)
- [ADB Cheatsheet](./02-Tools/Cheatsheets/adb_cheatsheet.md) - ADB命令速查
---
## 📚 Case Studies

真实场景的案例分析，综合运用各类技术。

- [Anti Analysis Techniques](./03-Case-Studies/case_anti_analysis_techniques.md) - 反分析技术案例
- [Music Apps](./03-Case-Studies/case_music_apps.md) - 音乐App分析
- [Social Media & Anti Bot](./03-Case-Studies/case_social_media_and_anti_bot.md) - 社交媒体与风控
- [App Encryption](./03-Case-Studies/case_study_app_encryption.md) - 应用加密案例
- [Video Apps & DRM](./03-Case-Studies/case_video_apps_and_drm.md) - 视频App与DRM
- [Unity Games (Il2Cpp)](./03-Case-Studies/case_unity_games.md) - Unity游戏分析
- [Flutter Apps](./03-Case-Studies/case_flutter_apps.md) - Flutter应用分析
- [Malware Analysis](./03-Case-Studies/case_malware_analysis.md) - 恶意软件分析
---
## 📖 Reference

参考资料和理论知识，需要时查阅。

### 📱 [Foundations - 基础知识](./04-Reference/Foundations/)
Android应用和系统的核心基础。

- [APK Structure](./04-Reference/Foundations/apk_structure.md) - APK结构
- [Android Components](./04-Reference/Foundations/android_components.md) - 安卓四大组件
- [Android Manifest](./04-Reference/Foundations/android_manifest.md) - AndroidManifest.xml
- [Android Studio Debug Tools](./04-Reference/Foundations/android_studio_debug_tools.md) - Android Studio调试工具
- [DEX Format](./04-Reference/Foundations/dex_format.md) - DEX文件格式
- [Smali Syntax](./04-Reference/Foundations/smali_syntax.md) - Smali语法
- [SO ELF Format](./04-Reference/Foundations/so_elf_format.md) - SO文件(ELF)格式
- [ART Runtime](./04-Reference/Foundations/art_runtime.md) - ART运行时
- [ARM Assembly](./04-Reference/Foundations/arm_assembly.md) - ARM汇编
- [x86 & ARM Assembly Basics](./04-Reference/Foundations/x86_and_arm_assembly_basics.md) - x86与ARM汇编基础
- [TOTP](./04-Reference/Foundations/totp.md) - 时间动态密码原理

### 🚀 [Advanced - 高级主题](./04-Reference/Advanced/)
深入的系统级和高级技术。

- [Android Sandbox Implementation](./04-Reference/Advanced/android_sandbox_implementation.md) - Android沙箱实现
- [AOSP & System Customization](./04-Reference/Advanced/aosp_and_system_customization.md) - AOSP与系统定制
- [AOSP Device Modification](./04-Reference/Advanced/aosp_device_modification.md) - AOSP设备修改
- [Minimal Android Rootfs](./04-Reference/Advanced/minimal_android_rootfs.md) - 最小化Android根文件系统
- [SO Anti Debugging & Obfuscation](./04-Reference/Advanced/so_anti_debugging_and_obfuscation.md) - SO反调试与混淆
- [SO Runtime Emulation](./04-Reference/Advanced/so_runtime_emulation.md) - SO运行时仿真

### 🔩 [Engineering - 工程化](./04-Reference/Engineering/)
规模化和工程化相关技术。

- [Frameworks & Middleware](./04-Reference/Engineering/frameworks_and_middleware.md) - 框架与中间件
- [Message Queues](./04-Reference/Engineering/message_queues.md) - 消息队列
- [Redis](./04-Reference/Engineering/redis.md) - Redis数据库
- [Risk Control SDK Build Guide](./04-Reference/Engineering/risk_control_sdk_build_guide.md) - 风控SDK构建
- [Automation vs API Reverse](./04-Reference/Engineering/automation_vs_api_reverse.md) - 群控与API逆向对比

#### 📊 Data Analysis - 数据分析
- [Data Warehousing & Processing](./04-Reference/Engineering/Data-Analysis/data_warehousing_and_processing.md) - 数据仓库与处理
- [Flink](./04-Reference/Engineering/Data-Analysis/flink.md) - Flink流处理
- [HBase](./04-Reference/Engineering/Data-Analysis/hbase.md) - HBase分布式数据库
- [Hive](./04-Reference/Engineering/Data-Analysis/hive.md) - Hive数据仓库
- [Spark](./04-Reference/Engineering/Data-Analysis/spark.md) - Spark大数据处理
---
## 📎 Appendix

附录资源和社区资源。

- [Github Projects](./05-Appendix/github_projects.md) - 开源项目推荐
- [Learning Resources](./05-Appendix/learning_resources.md) - 学习资源
- [CTF Platforms](./05-Appendix/ctf_platforms.md) - CTF平台
- [Glossary](./05-Appendix/glossary.md) - 术语表
---
## 🎯 快速导航

### 我想...

- **抓包分析 HTTPS 流量** → [Network Sniffing](./01-Recipes/Network/network_sniffing.md)
- **绕过应用的反调试检测** → [Frida Anti Debugging](./01-Recipes/Anti-Detection/frida_anti_debugging.md)
- **脱壳加固应用** → [Unpacking](./01-Recipes/Unpacking/un-packing.md)
- **分析加密算法** → [Crypto Analysis](./01-Recipes/Network/crypto_analysis.md)
- **学习 Frida 使用** → [Frida Guide](./02-Tools/Dynamic/frida_guide.md)
- **查看 Frida 脚本示例** → [Frida Script Examples](./01-Recipes/Scripts/frida_script_examples.md)
- **了解 APK 文件结构** → [APK Structure](./04-Reference/Foundations/apk_structure.md)
- **看实战案例** → [Case Studies](./03-Case-Studies/)
---
## 📝 贡献

本 Cookbook 持续更新中。如有建议或发现错误，欢迎反馈！
---
**Happy Hacking! 🚀**
