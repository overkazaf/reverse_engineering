---
title: "android 逆向工程 Cookbook"
date: 2025-07-29
tags: ["OLLVM", "加密分析", "Hook", "DEX", "IDA Pro", "反混淆"]
weight: 1
---

# android 逆向工程 Cookbook

欢迎来到 **Android RE Cookbook** —— 一本实战导向的 Android 逆向工程实用手册。

本 Cookbook 采用**场景驱动**的组织方式，帮助你快速找到解决特定问题的方法，而非传统的知识点罗列。
---
## 🚀 新手？从这里开始

**完全新手？** 先完成 10 分钟快速入门，体验第一次 Hook！

👉 **[10 分钟快速入门](./00-quick-start/)** - 安装 Frida 并完成第一次 Hook

**环境还没配置好？**
👉 **[环境配置指南](./00-quick-start/setup/)** - 从零搭建逆向分析环境
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

### 🌐 [Network - 网络与加密](./01-recipes/network/)
解决网络抓包、加密分析、TLS指纹等问题。

- [Network Sniffing](./01-recipes/network/network_sniffing/) - 网络协议分析与抓包
- [Crypto Analysis](./01-recipes/network/crypto_analysis/) - 密码学分析
- [TLS Fingerprinting](./01-recipes/network/tls_fingerprinting_guide/) - TLS指纹识别
- [JA3 Fingerprinting](./01-recipes/network/ja3_fingerprinting/) - JA3指纹分析
- [JA4 Fingerprinting](./01-recipes/network/ja4_fingerprinting/) - JA4指纹分析

### 🛡️ [Anti-Detection - 反检测与对抗](./01-recipes/anti-detection/)
绕过各类检测机制，包括反调试、反Hook、验证码等。

- [Frida Anti Debugging](./01-recipes/anti-detection/frida_anti_debugging/) - Frida反调试绕过
- [Xposed Anti Debugging](./01-recipes/anti-detection/xposed_anti_debugging/) - Xposed反调试绕过
- [Captcha Bypassing](./01-recipes/anti-detection/captcha_bypassing_techniques/) - 验证码绕过
- [App Hardening Identification](./01-recipes/anti-detection/app_hardening_identification/) - 加固识别
- [Device Fingerprinting & Bypass](./01-recipes/anti-detection/device_fingerprinting_and_bypass/) - 设备指纹绕过
- [Mobile App Security & Anti Bot](./01-recipes/anti-detection/mobile_app_sec_and_anti_bot/) - 移动端安全与反机器人

### 📦 [Unpacking - 脱壳与修复](./01-recipes/unpacking/)
处理加壳应用的脱壳和修复工作。

- [Unpacking](./01-recipes/unpacking/un-packing/) - 应用脱壳技术
- [Frida Unpacking & SO Fixing](./01-recipes/unpacking/frida_unpacking_and_so_fixing/) - Frida脱壳与SO修复
- [SO Obfuscation Deobfuscation](./01-recipes/unpacking/so_obfuscation_deobfuscation/) - SO混淆与反混淆
- [SO String Deobfuscation](./01-recipes/unpacking/so_string_deobfuscation/) - SO字符串反混淆

### 🔬 [Analysis - 分析与调试](./01-recipes/analysis/)
静态分析、动态分析和代码混淆分析。

- [RE Workflow](./01-recipes/analysis/re_workflow/) - 逆向工程工作流
- [Static Analysis Deep Dive](./01-recipes/analysis/static_analysis_deep_dive/) - 静态分析深入
- [Dynamic Analysis Deep Dive](./01-recipes/analysis/dynamic_analysis_deep_dive/) - 动态分析深入
- [eBPF Android Reversing](./01-recipes/analysis/ebpf_android_reversing/) - eBPF Android逆向实战
- [OLLVM Deobfuscation](./01-recipes/analysis/ollvm_deobfuscation/) - OLLVM反混淆
- [VMP Analysis](./01-recipes/analysis/vmp_analysis/) - VMP分析
- [JS Obfuscator](./01-recipes/analysis/js_obfuscator/) - JS混淆分析
- [JS VMP](./01-recipes/analysis/js_vmp/) - JS虚拟机保护
- [Native String Obfuscation](./01-recipes/analysis/native_string_obfuscation/) - Native字符串混淆

### 🤖 [Automation - 自动化与规模化](./01-recipes/automation/)
构建自动化分析系统和规模化解决方案。

- [Automation & Device Farming](./01-recipes/automation/automation_and_device_farming/) - 自动化与群控
- [Dial Up Proxy Pools](./01-recipes/automation/dial_up_proxy_pools/) - 动态代理池
- [Proxy Pool Design](./01-recipes/automation/proxy_pool_design/) - 代理池设计
- [Scrapy](./01-recipes/automation/scrapy/) - Scrapy爬虫框架
- [Scrapy Redis Distributed](./01-recipes/automation/scrapy_redis_distributed/) - 分布式Scrapy
- [Docker Deployment](./01-recipes/automation/docker_deployment/) - Docker部署
- [Virtualization & Containers](./01-recipes/automation/virtualization_and_containers/) - 虚拟化与容器
- [Web Anti Scraping](./01-recipes/automation/web_anti_scraping/) - Web反爬虫

### 📝 [Scripts - 即用脚本](./01-recipes/scripts/)
可直接使用的脚本集合。

- [Frida Script Examples](./01-recipes/scripts/frida_script_examples/) - Frida脚本示例
- [Frida Common Scripts](./01-recipes/scripts/frida_common_scripts/) - Frida常用脚本
- [eBPF Scripts](./01-recipes/scripts/ebpf_scripts/) - eBPF脚本集
- [Automation Scripts](./01-recipes/scripts/automation_scripts/) - 自动化脚本
- [Native Hooking](./01-recipes/scripts/native_hooking/) - Native Hook模式
- [Objection Snippets](./01-recipes/scripts/objection_snippets/) - Objection代码片段
- [C For Emulation](./01-recipes/scripts/c_for_emulation/) - C语言仿真
---
## 🔨 Tools

工具使用指南和原理剖析。

### ⚡ [Dynamic - 动态分析工具](./02-tools/dynamic/)
- [Frida Guide](./02-tools/dynamic/frida_guide/) - Frida使用指南
- [Frida Internals](./02-tools/dynamic/frida_internals/) - Frida内部原理
- [Xposed Guide](./02-tools/dynamic/xposed_guide/) - Xposed使用指南
- [Xposed Internals](./02-tools/dynamic/xposed_internals/) - Xposed内部原理
- [KernelSU Guide](./02-tools/dynamic/kernelsu_guide/) - KernelSU使用指南
- [KernelSU Internals](./02-tools/dynamic/kernelsu_internals/) - KernelSU内部原理
- [Unidbg Guide](./02-tools/dynamic/unidbg_guide/) - Unidbg使用指南
- [Unidbg Internals](./02-tools/dynamic/unidbg_internals/) - Unidbg内部原理
- [eBPF Guide](./02-tools/dynamic/ebpf_guide/) - eBPF使用指南
- [eBPF Internals](./02-tools/dynamic/ebpf_internals/) - eBPF内部原理

### 🔍 [Static - 静态分析工具](./02-tools/static/)
- [Ghidra Guide](./02-tools/static/ghidra_guide/) - Ghidra使用指南
- [IDA Pro Guide](./02-tools/static/ida_pro_guide/) - IDA Pro使用指南
- [Radare2 Guide](./02-tools/static/radare2_guide/) - Radare2使用指南

### 📋 [Cheatsheets - 速查表](./02-tools/cheatsheets/)
- [ADB Cheatsheet](./02-tools/cheatsheets/adb_cheatsheet/) - ADB命令速查
---
## 📚 Case Studies

真实场景的案例分析，综合运用各类技术。

- [Anti Analysis Techniques](./03-case-studies/case_anti_analysis_techniques/) - 反分析技术案例
- [Music Apps](./03-case-studies/case_music_apps/) - 音乐App分析
- [Social Media & Anti Bot](./03-case-studies/case_social_media_and_anti_bot/) - 社交媒体与风控
- [App Encryption](./03-case-studies/case_study_app_encryption/) - 应用加密案例
- [Video Apps & DRM](./03-case-studies/case_video_apps_and_drm/) - 视频App与DRM
- [Unity Games (Il2Cpp)](./03-case-studies/case_unity_games/) - Unity游戏分析
- [Flutter Apps](./03-case-studies/case_flutter_apps/) - Flutter应用分析
- [Malware Analysis](./03-case-studies/case_malware_analysis/) - 恶意软件分析
---
## 📖 Reference

参考资料和理论知识，需要时查阅。

### 📱 [Foundations - 基础知识](./04-reference/foundations/)
Android应用和系统的核心基础。

- [APK Structure](./04-reference/foundations/apk_structure/) - APK结构
- [Android Components](./04-reference/foundations/android_components/) - 安卓四大组件
- [Android Manifest](./04-reference/foundations/android_manifest/) - AndroidManifest.xml
- [Android Studio Debug Tools](./04-reference/foundations/android_studio_debug_tools/) - Android Studio调试工具
- [DEX Format](./04-reference/foundations/dex_format/) - DEX文件格式
- [Smali Syntax](./04-reference/foundations/smali_syntax/) - Smali语法
- [SO ELF Format](./04-reference/foundations/so_elf_format/) - SO文件(ELF)格式
- [ART Runtime](./04-reference/foundations/art_runtime/) - ART运行时
- [Boot Image & GKI](./04-reference/foundations/boot_image_and_gki/) - 启动镜像与GKI
- [ARM Assembly](./04-reference/foundations/arm_assembly/) - ARM汇编
- [x86 & ARM Assembly Basics](./04-reference/foundations/x86_and_arm_assembly_basics/) - x86与ARM汇编基础
- [TOTP](./04-reference/foundations/totp/) - 时间动态密码原理

### 🚀 [Advanced - 高级主题](./04-reference/advanced/)
深入的系统级和高级技术。

- [Android Sandbox Implementation](./04-reference/advanced/android_sandbox_implementation/) - Android沙箱实现
- [AOSP & System Customization](./04-reference/advanced/aosp_and_system_customization/) - AOSP与系统定制
- [AOSP Device Modification](./04-reference/advanced/aosp_device_modification/) - AOSP设备修改
- [Minimal Android Rootfs](./04-reference/advanced/minimal_android_rootfs/) - 最小化Android根文件系统
- [SO Anti Debugging & Obfuscation](./04-reference/advanced/so_anti_debugging_and_obfuscation/) - SO反调试与混淆
- [SO Runtime Emulation](./04-reference/advanced/so_runtime_emulation/) - SO运行时仿真

### 🔩 [Engineering - 工程化](./04-reference/engineering/)
规模化和工程化相关技术。

- [Frameworks & Middleware](./04-reference/engineering/frameworks_and_middleware/) - 框架与中间件
- [Message Queues](./04-reference/engineering/message_queues/) - 消息队列
- [Redis](./04-reference/engineering/redis/) - Redis数据库
- [Risk Control SDK Build Guide](./04-reference/engineering/risk_control_sdk_build_guide/) - 风控SDK构建
- [Automation vs API Reverse](./04-reference/engineering/automation_vs_api_reverse/) - 群控与API逆向对比

#### 📊 Data Analysis - 数据分析
- [Data Warehousing & Processing](./04-reference/engineering/data-analysis/data_warehousing_and_processing/) - 数据仓库与处理
- [Flink](./04-reference/engineering/data-analysis/flink/) - Flink流处理
- [HBase](./04-reference/engineering/data-analysis/hbase/) - HBase分布式数据库
- [Hive](./04-reference/engineering/data-analysis/hive/) - Hive数据仓库
- [Spark](./04-reference/engineering/data-analysis/spark/) - Spark大数据处理
---
## 📎 Appendix

附录资源和社区资源。

- [Github Projects](./05-appendix/github_projects/) - 开源项目推荐
- [Learning Resources](./05-appendix/learning_resources/) - 学习资源
- [CTF Platforms](./05-appendix/ctf_platforms/) - CTF平台
- [Glossary](./05-appendix/glossary/) - 术语表
---
## 🎯 快速导航

### 我想...

- **抓包分析 HTTPS 流量** → [Network Sniffing](./01-recipes/network/network_sniffing/)
- **绕过应用的反调试检测** → [Frida Anti Debugging](./01-recipes/anti-detection/frida_anti_debugging/)
- **脱壳加固应用** → [Unpacking](./01-recipes/unpacking/un-packing/)
- **分析加密算法** → [Crypto Analysis](./01-recipes/network/crypto_analysis/)
- **学习 Frida 使用** → [Frida Guide](./02-tools/dynamic/frida_guide/)
- **学习 KernelSU Root** → [KernelSU Guide](./02-tools/dynamic/kernelsu_guide/)
- **学习 eBPF 隐蔽追踪** → [eBPF Guide](./02-tools/dynamic/ebpf_guide/)
- **查看 Frida 脚本示例** → [Frida Script Examples](./01-recipes/scripts/frida_script_examples/)
- **查看 eBPF 脚本示例** → [eBPF Scripts](./01-recipes/scripts/ebpf_scripts/)
- **了解 APK 文件结构** → [APK Structure](./04-reference/foundations/apk_structure/)
- **看实战案例** → [Case Studies](./03-case-studies/)
---
## 📝 贡献

本 Cookbook 持续更新中。如有建议或发现错误，欢迎反馈！
---
**Happy Hacking! 🚀**
