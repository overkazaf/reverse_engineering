# Android Reverse Engineering Cookbook

完整的 Android 逆向工程学习和实战指南

---

<!-- index.md -->

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

解决网络抓包、加密分析、TLS 指纹等问题。

- [Network Sniffing](./01-Recipes/Network/network_sniffing.md) - 网络协议分析与抓包
- [Crypto Analysis](./01-Recipes/Network/crypto_analysis.md) - 密码学分析
- [TLS Fingerprinting](./01-Recipes/Network/tls_fingerprinting_guide.md) - TLS 指纹识别
- [JA3 Fingerprinting](./01-Recipes/Network/ja3_fingerprinting.md) - JA3 指纹分析
- [JA4 Fingerprinting](./01-Recipes/Network/ja4_fingerprinting.md) - JA4 指纹分析

### 🛡️ [Anti-Detection - 反检测与对抗](./01-Recipes/Anti-Detection/)

绕过各类检测机制，包括反调试、反 Hook、验证码等。

- [Frida Anti Debugging](./01-Recipes/Anti-Detection/frida_anti_debugging.md) - Frida 反调试绕过
- [Xposed Anti Debugging](./01-Recipes/Anti-Detection/xposed_anti_debugging.md) - Xposed 反调试绕过
- [Captcha Bypassing](./01-Recipes/Anti-Detection/captcha_bypassing_techniques.md) - 验证码绕过
- [App Hardening Identification](./01-Recipes/Anti-Detection/app_hardening_identification.md) - 加固识别
- [Device Fingerprinting & Bypass](./01-Recipes/Anti-Detection/device_fingerprinting_and_bypass.md) - 设备指纹绕过
- [Mobile App Security & Anti Bot](./01-Recipes/Anti-Detection/mobile_app_sec_and_anti_bot.md) - 移动端安全与反机器人

### 📦 [Unpacking - 脱壳与修复](./01-Recipes/Unpacking/)

处理加壳应用的脱壳和修复工作。

- [Unpacking](./01-Recipes/Unpacking/un-packing.md) - 应用脱壳技术
- [Frida Unpacking & SO Fixing](./01-Recipes/Unpacking/frida_unpacking_and_so_fixing.md) - Frida 脱壳与 SO 修复
- [SO Obfuscation Deobfuscation](./01-Recipes/Unpacking/so_obfuscation_deobfuscation.md) - SO 混淆与反混淆
- [SO String Deobfuscation](./01-Recipes/Unpacking/so_string_deobfuscation.md) - SO 字符串反混淆

### 🔬 [Analysis - 分析与调试](./01-Recipes/Analysis/)

静态分析、动态分析和代码混淆分析。

- [RE Workflow](./01-Recipes/Analysis/re_workflow.md) - 逆向工程工作流
- [Static Analysis Deep Dive](./01-Recipes/Analysis/static_analysis_deep_dive.md) - 静态分析深入
- [Dynamic Analysis Deep Dive](./01-Recipes/Analysis/dynamic_analysis_deep_dive.md) - 动态分析深入
- [OLLVM Deobfuscation](./01-Recipes/Analysis/ollvm_deobfuscation.md) - OLLVM 反混淆
- [VMP Analysis](./01-Recipes/Analysis/vmp_analysis.md) - VMP 分析
- [JS Obfuscator](./01-Recipes/Analysis/js_obfuscator.md) - JS 混淆分析
- [JS VMP](./01-Recipes/Analysis/js_vmp.md) - JS 虚拟机保护
- [Native String Obfuscation](./01-Recipes/Analysis/native_string_obfuscation.md) - Native 字符串混淆

### 🤖 [Automation - 自动化与规模化](./01-Recipes/Automation/)

构建自动化分析系统和规模化解决方案。

- [Automation & Device Farming](./01-Recipes/Automation/automation_and_device_farming.md) - 自动化与群控
- [Dial Up Proxy Pools](./01-Recipes/Automation/dial_up_proxy_pools.md) - 动态代理池
- [Proxy Pool Design](./01-Recipes/Automation/proxy_pool_design.md) - 代理池设计
- [Scrapy](./01-Recipes/Automation/scrapy.md) - Scrapy 爬虫框架
- [Scrapy Redis Distributed](./01-Recipes/Automation/scrapy_redis_distributed.md) - 分布式 Scrapy
- [Docker Deployment](./01-Recipes/Automation/docker_deployment.md) - Docker 部署
- [Virtualization & Containers](./01-Recipes/Automation/virtualization_and_containers.md) - 虚拟化与容器
- [Web Anti Scraping](./01-Recipes/Automation/web_anti_scraping.md) - Web 反爬虫

### 📝 [Scripts - 即用脚本](./01-Recipes/Scripts/)

可直接使用的脚本集合。

- [Frida Script Examples](./01-Recipes/Scripts/frida_script_examples.md) - Frida 脚本示例
- [Frida Common Scripts](./01-Recipes/Scripts/frida_common_scripts.md) - Frida 常用脚本
- [Automation Scripts](./01-Recipes/Scripts/automation_scripts.md) - 自动化脚本
- [Native Hooking](./01-Recipes/Scripts/native_hooking.md) - Native Hook 模式
- [Objection Snippets](./01-Recipes/Scripts/objection_snippets.md) - Objection 代码片段
- [C For Emulation](./01-Recipes/Scripts/c_for_emulation.md) - C 语言仿真

---

## 🔨 Tools

工具使用指南和原理剖析。

### ⚡ [Dynamic - 动态分析工具](./02-Tools/Dynamic/)

- [Frida Guide](./02-Tools/Dynamic/frida_guide.md) - Frida 使用指南
- [Frida Internals](./02-Tools/Dynamic/frida_internals.md) - Frida 内部原理
- [Xposed Guide](./02-Tools/Dynamic/xposed_guide.md) - Xposed 使用指南
- [Xposed Internals](./02-Tools/Dynamic/xposed_internals.md) - Xposed 内部原理
- [Unidbg Guide](./02-Tools/Dynamic/unidbg_guide.md) - Unidbg 使用指南
- [Unidbg Internals](./02-Tools/Dynamic/unidbg_internals.md) - Unidbg 内部原理

### 🔍 [Static - 静态分析工具](./02-Tools/Static/)

- [Ghidra Guide](./02-Tools/Static/ghidra_guide.md) - Ghidra 使用指南
- [IDA Pro Guide](./02-Tools/Static/ida_pro_guide.md) - IDA Pro 使用指南
- [Radare2 Guide](./02-Tools/Static/radare2_guide.md) - Radare2 使用指南

### 📋 [Cheatsheets - 速查表](./02-Tools/Cheatsheets/)

- [ADB Cheatsheet](./02-Tools/Cheatsheets/adb_cheatsheet.md) - ADB 命令速查

---

## 📚 Case Studies

真实场景的案例分析，综合运用各类技术。

- [Anti Analysis Techniques](./03-Case-Studies/case_anti_analysis_techniques.md) - 反分析技术案例
- [Music Apps](./03-Case-Studies/case_music_apps.md) - 音乐 App 分析
- [Social Media & Anti Bot](./03-Case-Studies/case_social_media_and_anti_bot.md) - 社交媒体与风控
- [App Encryption](./03-Case-Studies/case_study_app_encryption.md) - 应用加密案例
- [Video Apps & DRM](./03-Case-Studies/case_video_apps_and_drm.md) - 视频 App 与 DRM
- [Unity Games (Il2Cpp)](./03-Case-Studies/case_unity_games.md) - Unity 游戏分析
- [Flutter Apps](./03-Case-Studies/case_flutter_apps.md) - Flutter 应用分析
- [Malware Analysis](./03-Case-Studies/case_malware_analysis.md) - 恶意软件分析

---

## 📖 Reference

参考资料和理论知识，需要时查阅。

### 📱 [Foundations - 基础知识](./04-Reference/Foundations/)

Android 应用和系统的核心基础。

- [APK Structure](./04-Reference/Foundations/apk_structure.md) - APK 结构
- [Android Components](./04-Reference/Foundations/android_components.md) - 安卓四大组件
- [Android Manifest](./04-Reference/Foundations/android_manifest.md) - AndroidManifest.xml
- [Android Studio Debug Tools](./04-Reference/Foundations/android_studio_debug_tools.md) - Android Studio 调试工具
- [DEX Format](./04-Reference/Foundations/dex_format.md) - DEX 文件格式
- [Smali Syntax](./04-Reference/Foundations/smali_syntax.md) - Smali 语法
- [SO ELF Format](./04-Reference/Foundations/so_elf_format.md) - SO 文件(ELF)格式
- [ART Runtime](./04-Reference/Foundations/art_runtime.md) - ART 运行时
- [ARM Assembly](./04-Reference/Foundations/arm_assembly.md) - ARM 汇编
- [x86 & ARM Assembly Basics](./04-Reference/Foundations/x86_and_arm_assembly_basics.md) - x86 与 ARM 汇编基础

### 🚀 [Advanced - 高级主题](./04-Reference/Advanced/)

深入的系统级和高级技术。

- [Android Sandbox Implementation](./04-Reference/Advanced/android_sandbox_implementation.md) - Android 沙箱实现
- [AOSP & System Customization](./04-Reference/Advanced/aosp_and_system_customization.md) - AOSP 与系统定制
- [AOSP Device Modification](./04-Reference/Advanced/aosp_device_modification.md) - AOSP 设备修改
- [Minimal Android Rootfs](./04-Reference/Advanced/minimal_android_rootfs.md) - 最小化 Android 根文件系统
- [SO Anti Debugging & Obfuscation](./04-Reference/Advanced/so_anti_debugging_and_obfuscation.md) - SO 反调试与混淆
- [SO Runtime Emulation](./04-Reference/Advanced/so_runtime_emulation.md) - SO 运行时仿真

### 🔩 [Engineering - 工程化](./04-Reference/Engineering/)

规模化和工程化相关技术。

- [Frameworks & Middleware](./04-Reference/Engineering/frameworks_and_middleware.md) - 框架与中间件
- [Message Queues](./04-Reference/Engineering/message_queues.md) - 消息队列
- [Redis](./04-Reference/Engineering/redis.md) - Redis 数据库
- [Risk Control SDK Build Guide](./04-Reference/Engineering/risk_control_sdk_build_guide.md) - 风控 SDK 构建

#### 📊 Data Analysis - 数据分析

- [Data Warehousing & Processing](./04-Reference/Engineering/Data-Analysis/data_warehousing_and_processing.md) - 数据仓库与处理
- [Flink](./04-Reference/Engineering/Data-Analysis/flink.md) - Flink 流处理
- [HBase](./04-Reference/Engineering/Data-Analysis/hbase.md) - HBase 分布式数据库
- [Hive](./04-Reference/Engineering/Data-Analysis/hive.md) - Hive 数据仓库
- [Spark](./04-Reference/Engineering/Data-Analysis/spark.md) - Spark 大数据处理

---

## 📎 Appendix

附录资源和社区资源。

- [Github Projects](./05-Appendix/github_projects.md) - 开源项目推荐
- [Learning Resources](./05-Appendix/learning_resources.md) - 学习资源
- [CTF Platforms](./05-Appendix/ctf_platforms.md) - CTF 平台
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

<!-- 00-Quick-Start/index.md -->

# 快速入门

欢迎！这个指南将帮助你在 **10 分钟内**完成第一次 Android 逆向分析。

---

## 你将学到什么

完成本指南后，你将能够：

- ✅ 在真机/模拟器上运行 Frida
- ✅ Hook 一个 Android 应用的 Java 方法
- ✅ 查看和修改方法的参数与返回值
- ✅ 理解基本的逆向分析流程

**预计用时**: 10-15 分钟

---

## 前置条件

### 必需工具

| 工具           | 说明                                                           |
| -------------- | -------------------------------------------------------------- |
| ☐ Android 设备 | 已 Root 的真机或模拟器（推荐 Genymotion / Android Studio AVD） |
| ☐ ADB          | Android Debug Bridge                                           |
| ☐ Python       | 版本 3.8+                                                      |
| ☐ 测试 App     | 本指南使用系统自带的设置应用                                   |

### 检查清单

```bash
# 1. Check if ADB is installed
adb version

# 2. Check if Python is installed
python3 --version

# 3. Check device connection
adb devices
# Should display your device

```

## 操作步骤

### 第 1 步：安装 Frida（2 分钟）

**在电脑上安装 Frida 工具**：

```bash
pip install frida-tools

```

```bash
# Visit https://github.com/frida/frida/releases
# Download frida-server matching your Python frida version

# View your frida version
frida --version

# View device architecture
adb shell getprop ro.product.cpu.abi
# Common output: arm64-v8a, armeabi-v7a, x86_64

# 2. Decompress and push to device
unzip frida-server-*.zip
adb push frida-server-*-android-* /data/local/tmp/frida-server

# 3. grant execute permission and run
adb shell "chmod 755 /data/local/tmp/frida-server"
adb shell "/data/local/tmp/frida-server &"

```

```bash
frida-ps -U
# Should see output like:
# PID Name
# ---- ---------------
# 1234 com.android.settings
# 5678 com.android.systemui
# ...

```

我们将 Hook Android 设置应用，监控其方法调用。

**创建 Hook 脚本** `first_hook.js`：

```javascript
// first_hook.js - your first Frida script

Java.perform(function () {
  console.log("\n[*] Frida hook started!");
  console.log("[*] Finding TargetClass...\n");

  // Hook Android system Log class
  var Log = Java.use("android.util.Log");

  // Hook Log.d method (debug log)
  Log.d.overload("java.lang.String", "java.lang.String").implementation =
    function (tag, msg) {
      console.log("\n[+] Captured LogCall:");
      console.log(" Tag: " + tag);
      console.log(" Message: " + msg);

      // Call original method
      return this.d(tag, msg);
    };

  console.log("[*] Hook setup completed! Now open Settings app...\n");
});
```

```bash
# Method 1: attach to running app
frida -U -n com.android.settings -l first_hook.js

# Method 2: inject at app startup
frida -U -f com.android.settings -l first_hook.js --no-pause

```

```

[+] Captured LogCall:
Tag: SettingsActivity
Message: onCreate called

[+] Captured LogCall:
Tag: SettingsFragment
Message: Loading preferences...

```

✅ **看到日志输出了吗？恭喜！你已经成功 Hook 了一个 Android 应用！**

---

### 第 3 步：修改应用行为（3 分钟）

现在让我们做点更有趣的 —— **修改应用的返回值**。

**创建脚本** `modify_behavior.js`：

```javascript
// modify_behavior.js - Modify App behavior

Java.perform(function () {
  console.log("\n[*] Start Hook...\n");

  // Hook String Class equals Method
  var String = Java.use("java.lang.String");

  String.equals.implementation = function (other) {
    // get original result
    var result = this.equals(other);

    // if string is "WiFi", modify result
    if (this.toString() === "WiFi" || other.toString() === "WiFi") {
      console.log("\n[!] detected WiFi String comparison");
      console.log(" Original: '" + this + "' == '" + other + "' => " + result);
      console.log(" Modified: true\n");
      return true; // return true
    }

    return result;
  };

  console.log(
    "[*] Hook completed! All 'WiFi' String comparison will return true\n"
  );
});
```

```bash
frida -U -f com.android.settings -l modify_behavior.js --no-pause

```

- 修改加密参数
- 绕过签名验证
- 篡改网络请求

---

## 恭喜！你已完成快速入门

### 你学会了什么

✅ 安装和运行 Frida
✅ 编写基本的 Hook 脚本
✅ 监控方法调用
✅ 修改方法返回值

### 下一步学习

根据你的兴趣选择：

#### **我想深入学习工具**

- [Frida 完整指南](../02-Tools/Dynamic/frida_guide.md) - 学习 Frida 的所有 API
- [Frida 内部原理](../02-Tools/Dynamic/frida_internals.md) - 理解 Frida 如何工作
- [ADB 命令速查](../02-Tools/Cheatsheets/adb_cheatsheet.md) - 掌握 ADB 常用命令

#### **我想解决具体问题**

**场景 1: 抓包分析**
→ [网络抓包 Recipe](../01-Recipes/Network/network_sniffing.md)

**场景 2: 绕过反调试**
→ [反调试绕过 Recipe](../01-Recipes/Anti-Detection/frida_anti_debugging.md)

**场景 3: 分析加密算法**
→ [密码学分析 Recipe](../01-Recipes/Network/crypto_analysis.md)

**场景 4: 脱壳加固 App**
→ [应用脱壳 Recipe](../01-Recipes/Unpacking/un-packing.md)

#### **我想看实战案例**

- [音乐 App 分析](../03-Case-Studies/case_music_apps.md) - VIP 破解、音频解密
- [社交 App 风控](../03-Case-Studies/case_social_media_and_anti_bot.md) - API 签名、设备指纹

#### **我想理解基础原理**

- [APK 文件结构](../04-Reference/Foundations/apk_structure.md)
- [Android 四大组件](../04-Reference/Foundations/android_components.md)
- [DEX 文件格式](../04-Reference/Foundations/dex_format.md)

---

## 💡 常见问题

### Q: Frida 连接不上设备？

```bash
# 1. Confirm frida-server is running
adb shell "ps | grep frida"

# 2. 重启 frida-server
adb shell "pkill frida-server"
adb shell "/data/local/tmp/frida-server &"

# 3. Check port forwarding (if needed)
adb forward tcp:27042 tcp:27042

```

**排查步骤**：

1. **确认应用正在运行**：

```bash
frida-ps -U | grep YourAppPackageName

```

- 使用 jadx-gui 反编译查看准确的类名
- 注意内部类的 `$` 符号（如 `OuterClass$InnerClass`）

3. **处理方法重载**：

```javascript
// If method has multiple overloads, need to specify parameter class type
YourClass.yourMethod.overload('java.lang.String').implementation = ...

```

→ 查看 [Frida 反调试绕过](../01-Recipes/Anti-Detection/frida_anti_debugging.md)

---

## 更多资源

| 项目                   | 说明                                                             |
| ---------------------- | ---------------------------------------------------------------- |
| **Frida 官方文档**     | https://frida.re/docs/                                           |
| **Frida CodeShare**    | https://codeshare.frida.re/ （社区脚本）                         |
| **本 Cookbook 脚本库** | [Frida 脚本示例](../01-Recipes/Scripts/frida_script_examples.md) |

---

**准备好了吗？开始你的逆向之旅吧！**

<!-- 00-Quick-Start/setup.md -->

# 环境配置指南

本指南帮助你从零开始搭建 Android 逆向分析环境。

---

## 所需工具概览

| 工具                | 用途                 | 必需程度 |
| ------------------- | -------------------- | -------- |
| ADB                 | 与 Android 设备通信  | 必需     |
| Python 3.8+         | 运行 Frida 工具      | 必需     |
| Frida               | 动态插桩框架         | 必需     |
| Android 设备/模拟器 | 运行目标应用         | 必需     |
| jadx-gui            | 反编译 APK           | 推荐     |
| Burp Suite          | 抓包分析             | 可选     |
| IDA Pro / Ghidra    | 静态分析 Native 代码 | 可选     |

---

## 选择你的系统

<details>
<summary><b>Windows 用户</b></summary>

### 1. 安装 Python

**下载安装包**：

- 访问 https://www.python.org/downloads/
- 下载 Python 3.8 或更高版本
- 安装时**勾选** "Add Python to PATH"

**验证安装**：

```cmd
python --version
pip --version

```

**方法 1: 通过 Android Studio**

- 下载 Android Studio: https://developer.android.com/studio
- 安装后，SDK Manager 会自动安装 ADB
- 路径通常在: `C:\Users\你的用户名\AppData\Local\Android\Sdk\platform-tools\`

**方法 2: 独立安装 platform-tools**

- 下载: https://developer.android.com/studio/releases/platform-tools
- 解压到 `C:\adb\`
- 添加到系统 PATH 环境变量

**验证安装**：

```cmd
adb version

```

```cmd
pip install frida-tools
frida --version

```

<details>
<summary><b>macOS 用户</b></summary>

### 1. 安装 Homebrew（如果没有）

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

```

```bash
brew install python3
brew install android-platform-tools
pip3 install frida-tools

```

```bash
python3 --version
adb version
frida --version

```

<details>
<summary><b>Linux 用户</b></summary>

### 1. 安装 Python

```bash
sudo apt update
sudo apt install python3 python3-pip

```

```bash
sudo apt install android-tools-adb
pip3 install frida-tools

```

```bash
python3 --version
adb version
frida --version

```

---

## 配置 Android 设备/模拟器

### 选项 1: 使用真机（推荐用于实战）

#### 步骤 1: 启用开发者选项

1. 打开 **设置** → **关于手机**
2. 连续点击 **"版本号"** 7 次
3. 返回设置，找到 **开发者选项**

#### 步骤 2: 启用 USB 调试

在开发者选项中：

- ✅ 启用 **USB 调试**
- ✅ 启用 **USB 安装**（允许通过 ADB 安装应用）

#### 步骤 3: 连接设备

```bash
# Connect device to PC via USB
# Device will pop up an authorization prompt, click "Allow"

# Verify connection
adb devices

# Should see:
# List of devices attached
# ABC123456789 device

```

**方法 1: 使用 Magisk**

1. 解锁 Bootloader（厂商特定）
2. 安装 Magisk: https://github.com/topjohnwu/Magisk
3. 参考官方文档

**方法 2: 使用已 Root 的测试机**

- Google Pixel 系列（容易解锁）
- 一加设备
- 或购买专门的测试机

**⚠️ 警告**: Root 会失去保修，仅在测试设备上操作！

---

### 选项 2: 使用 android 模拟器（推荐新手）

#### 方案 A: Genymotion（最稳定）

**优点**: 自带 Root，性能好
**缺点**: 个人版免费但功能受限

1. 下载 Genymotion: https://www.genymotion.com/download/
2. 安装并注册账号
3. 创建虚拟设备（推荐 Google Pixel 3, Android 9.0）
4. 启动虚拟设备

**验证**：

```bash
adb devices
# Should see Genymotion device

```

**步骤**：

1. 打开 Android Studio
2. Tools → Device Manager → Create Device
3. 选择设备（如 Pixel 5）
4. 选择系统镜像（⚠️ 必须选择 **不带 Google Play** 的镜像，如 "x86_64 API 30"）
5. 启动模拟器

**启用 Root**：

```bash
adb root
adb remount

```

**推荐**：

- 夜神: https://www.yeshen.com/
- 雷电: https://www.ldmnq.com/

**注意**: 部分模拟器可能不支持某些应用

---

## 安装 Frida Server 到设备

### 步骤 1: 确定设备架构

```bash
adb shell getprop ro.product.cpu.abi

```

- `arm64-v8a` → 下载 **frida-server-**-android-arm64\*\*（真机常用）
- `armeabi-v7a` → 下载 **frida-server-**-android-arm\*\*
- `x86_64` → 下载 **frida-server-**-android-x86_64\*\*（模拟器常用）
- `x86` → 下载 **frida-server-**-android-x86\*\*

### 步骤 2: 下载 Frida Server

1. 访问: https://github.com/frida/frida/releases
2. 找到与你电脑 Frida 版本一致的 release

**检查本地 Frida 版本**：

```bash
frida --version
# E.g.: 16.1.4

```

```bash
# Decompress
unxz frida-server-16.1.4-android-arm64.xz
# or Windows: Use 7-Zip Decompress

# Rename (optional, easier to manage)
mv frida-server-16.1.4-android-arm64 frida-server

# push to device
adb push frida-server /data/local/tmp/

# Grant Execute permission
adb shell "chmod 755 /data/local/tmp/frida-server"

```

```bash
adb shell "/data/local/tmp/frida-server &"

# Verify it is running
adb shell "ps | grep frida-server"

```

```bash
# Add to /data/adb/service.d/ (Need Root)

```

```bash
frida-ps -U

# Should see process list
# PID Name
# ---- ---------------
# 1234 com.android.settings
# ...

```

## 安装其他工具（可选）

### jadx-gui（强烈推荐）

用于反编译 APK 查看 Java 代码。

**安装**：

1. 下载: https://github.com/skylot/jadx/releases
2. 解压并运行 `jadx-gui`（或 Windows 上运行 `jadx-gui.bat`）

**使用**：

```bash
# command line
jadx -d output_dir app.apk

# or use GUI: Open APK File

```

**IDA Pro**:

- 商业软件，功能强大
- 官网: https://hex-rays.com/ida-pro/

**Ghidra**（免费开源）:

- NSA 开源工具
- 下载: https://github.com/NationalSecurityAgency/ghidra/releases
- 需要 JDK 11+

---

## ✅ 环境检查清单

完成配置后，运行以下命令验证：

```bash
# 1. Python
python3 --version # Should >= 3.8

# 2. Pip
pip3 --version

# 3. ADB
adb version

# 4. Verify device connection
adb devices # Should display device

# 5. Frida native tool
frida --version

# 6. Frida Server
frida-ps -U # Should list processes

# 7. jadx (Optional)
jadx --version

```

---

## ❓ 常见问题

### Q: `adb devices` 显示 "unauthorized"？

**解决**：

1. 设备上没有弹出授权提示？重新插拔 USB
2. 撤销授权并重试：

```bash
adb kill-server
adb start-server

```

### Q: `adb devices` 什么都不显示？

**Windows**:

1. 安装设备驱动（厂商网站下载）
2. 或安装 Universal ADB Driver

**Linux**:

1. 检查 udev 规则是否配置
2. 当前用户是否在 `plugdev` 组：

```bash
sudo usermod -aG plugdev $USER
# Need to re-login for changes to take effect

```

1. **确认设备已 Root**：

```bash
adb shell su
# If shows "not found", indicates no Root

```

```bash
adb shell "setenforce 0" # Temporarily disable SELinux

```

```bash
# Re-verify architecture
adb shell getprop ro.product.cpu.abi
# Download matching frida-server

```

```bash
# Native Frida Version
frida --version

# Make sure frida-server version matches
# Re-download corresponding version frida-server

```

**Android Studio AVD**:

- 使用 x86_64 镜像（而非 ARM）
- 启用硬件加速（Intel HAXM / AMD Hypervisor）

---

## 下一步

环境配置完成！接下来：

1. **完成快速入门** → [10 分钟第一次 Hook](./index.md)
2. **学习 Frida 工具** → [Frida 完整指南](../02-Tools/Dynamic/frida_guide.md)
3. **查看实战脚本** → [Frida 脚本示例](../01-Recipes/Scripts/frida_script_examples.md)

---

**祝配置顺利！**

<!-- 01-Recipes/Analysis/dynamic_analysis_deep_dive.md -->

# Recipe: 使用动态分析验证和探索 android App 的运行时行为

## 问题场景

**你遇到了什么问题？**

- ✅ 你已经静态分析找到了目标函数，现在想验证它的实际输入输出
- 你想捕获运行时才生成的数据（如动态密钥、签名结果）
- 你想绕过 SSL Pinning / 反调试 / Root 检测
- 🧪 你想主动调用函数测试不同参数的效果
- 🕵️ 你想追踪代码执行路径，看看哪些函数被调用了

**本配方教你**：系统性地使用 Frida、调试器、追踪工具来验证静态分析结果、获取运行时数据、绕过保护机制。

**核心理念**：

> 💡 **动态分析：让代码说话**
>
> - 动态分析验证静态分析的假设
> - 获取只在运行时存在的数据
> - 主动探索程序的内部状态
> - Hook → Debug → Trace 三种武器各有用途

**预计用时**: 30-90 分钟

---

## 工具清单

## # 必需工具

- - **Frida** - 动态插桩框架
- - **Android 设备**（已 Root）或模拟器
- - **Python 3.7+** - 运行 Frida 脚本

## # 可选工具

- - **IDA Pro Remote Debugger** - Native 层调试
- - **objection** - Frida 的交互式工具
- - **Burp Suite** - 网络抓包
- - **GDB** - GNU 调试器

---

## 前置条件

## # ✅ 确认清单

```bash
# 1. Frida 正常运行
frida-ps -U

# 2. Python 环境
python3 --version

# 3. 目标 App 已安装
adb shell pm list packages | grep <app_name>

```

## # 🤔 Hook vs Debug vs Trace：何时用什么？

| 场景                             | 推荐工具               | 理由                            |
| -------------------------------- | ---------------------- | ------------------------------- |
| 想知道某个函数的输入输出         | **Frida Hook**         | 最快速，不中断程序流            |
| 想理解复杂算法的每一步细节       | **IDA/GDB 调试器**     | 可以单步执行，查看每个变量      |
| 想知道程序执行了哪些代码路径     | **Stalker/Trace**      | 全自动记录，无需设断点          |
| 想绕过某个检测（如 SSL Pinning） | **Frida Hook**         | 直接替换函数返回值              |
| 想找到某个字符串是在哪里生成的   | **内存断点 + 调试器**  | 在写入时中断                    |
| 想分析反调试机制                 | **Frida + 调试器组合** | 先用 Frida 禁用，再用调试器分析 |

**经验法则**：

- 能用 Hook 解决的，别用调试器（效率问题）
- 需要理解逻辑的，必须用调试器（深度问题）
- 需要全局视野的，用追踪（覆盖率问题）

---

## 解决方案

## # 第 1 步：验证静态分析结果（15 分钟）

假设静态分析发现了签名函数：`SignUtils.generateSign()`

## # # 1.1 Hook 函数查看输入输出

**基础 Hook 脚本** `verify_sign.js`：

```javascript
Java.perform(function () {
  console.log("[*] Start Hook SignUtils.generateSign");

  var SignUtils = Java.use("com.example.SignUtils");

  SignUtils.generateSign.implementation = function (params) {
    console.log("\n[*] generateSign is called!");
    console.log(" InputParameter:");

    // Print HashMap
    var iterator = params.entrySet().iterator();
    while (iterator.hasNext()) {
      var entry = iterator.next();
      console.log(" " + entry.getKey() + " = " + entry.getValue());
    }

    // Call original function
    var result = this.generateSign(params);

    console.log(" ReturnValue: " + result);
    console.log("");

    return result;
  };

  console.log("[*] Hook install completed");
});
```

user = test123
timestamp = 1701234567
action = login
ReturnValue: a1b2c3d4e5f6g7h8i9j0

````

## # # 2.1 列出所有重载

```javascript
Java.perform(function () {
var CryptoUtil = Java.use("com.example.CryptoUtil");

// List all encryption methods
console.log("[*] encrypt Method overloads:");
CryptoUtil.encrypt.overloads.forEach(function (overload) {
console.log(" " + overload);
});
});

````

encrypt([B)

```

// This is the second overloaded version
CryptoUtil.encrypt.overload(
"java.lang.String",
"java.lang.String"
).implementation = function (data, key) {
console.log("[*] encrypt(String, String) is called");
console.log(" Data:", data);
console.log(" Key:", key);

var result = this.encrypt(data, key);
console.log(" Result:", result);

return result;
};

// This is the third overloaded version
CryptoUtil.encrypt.overload("[B").implementation = function (bytes) {
console.log("[*] encrypt(byte[]) is called");
console.log(" BytesLength:", bytes.length);

var result = this.encrypt(bytes);
console.log(" ResultLength:", result.length);

return result;
};
});

```

**方法 1：创建新实例**

```javascript
Java.perform(function () {
  var CryptoUtil = Java.use("com.example.CryptoUtil");

  // Constructor accessible
  try {
    var instance = CryptoUtil.$new(); // Call no-arg constructor
    var result = instance.encrypt("Hello World", "mykey");
    console.log("[*] MainCallResult:", result);
  } catch (e) {
    console.log("[-] No way to create instance:", e);
  }
});
```

Java.choose("com.example.CryptoUtil", {
onMatch: function (instance) {
console.log("[+] Instance:", instance);

// Actively call
var encrypted = instance.encrypt("test data");
console.log("[*] EncryptResult:", encrypted);

var decrypted = instance.decrypt(encrypted);
console.log("[*] DecryptResult:", decrypted);
},
onComplete: function () {
console.log("[*] Search completed");
},

});
});

```
var HashMap = Java.use("java.util.HashMap");

// CreateParameter
var params = HashMap.$new();
params.put("user", "testuser");
params.put("timestamp", String(Date.now()));

// Actively call static method
var sign = SignUtils.generateSign(params);
console.log("[*] GenerateSignature:", sign);
});

```

```javascript
Java.perform(function () {
  var RootDetector = Java.use("com.example.security.RootDetector");

  RootDetector.isRooted.implementation = function () {
    console.log("[*] Root Detection is Bypassed");
    return false; // Force return false (not rooted)
  };

  RootDetector.isXposedInstalled.implementation = function () {
    console.log("[*] Xposed Detection is Bypassed");
    return false;
  };
});
```

// Hook OkHttp 3
try {
var CertificatePinner = Java.use("okhttp3.CertificatePinner");
CertificatePinner.check.overload(
"java.lang.String",
"java.util.List"
).implementation = function (hostname, peerCertificates) {
console.log("[*] Bypass OkHttp3 SSL Pinning:", hostname);
return; // Return directly, skip validation
};
console.log("[+] OkHttp3 SSL Pinning 已 Bypass");
} catch (e) {}

// Hook TrustManager
try {
var X509TrustManager = Java.use("javax.net.ssl.X509TrustManager");
var SSLContext = Java.use("javax.net.ssl.SSLContext");

var TrustManager = Java.registerClass({
name: "com.example.TrustManager",
implements: [X509TrustManager],
methods: {
checkClientTrusted: function (chain, authType) {},
checkServerTrusted: function (chain, authType) {},
getAcceptedIssuers: function () {
return [];
},
},
});

var TrustManagers = [TrustManager.$new()];
var SSLContext_init = SSLContext.init.overload(
"[Ljavax.net.ssl.KeyManager;",
"[Ljavax.net.ssl.TrustManager;",
"java.security.SecureRandom"
);
SSLContext_init.implementation = function (
keyManager,
trustManager,
secureRandom
) {
console.log("[*] 替换 TrustManager");
SSLContext_init.call(this, keyManager, TrustManagers, secureRandom);
};
console.log("[+] TrustManager 已 Bypass");

} catch (e) {}

console.log("[*] SSL Pinning BypassConfig 完成");
});

````

## # # 5.1 定义 RPC 函数

* *rpc_example.js**：

```javascript
rpc.exports = {
// ExportFunction：GenerateSignature
generateSign: function (params) {
var result = null;

Java.perform(function () {
var SignUtils = Java.use("com.example.SignUtils");
var HashMap = Java.use("java.util.HashMap");

var map = HashMap.$new();
for (var key in params) {
map.put(key, params[key]);
}

result = SignUtils.generateSign(map);
});

return result;
},

// ExportFunction：EncryptData
encrypt: function (plaintext, key) {
var result = null;

Java.perform(function () {
var CryptoUtil = Java.use("com.example.CryptoUtil");
result = CryptoUtil.encrypt(plaintext, key);
});

return result;
},
};

````

import frida
import sys

def on_message(message, data):
print(f"[*] Message: {message}")

# Connect to to to to to to to device

device = frida.get_usb_device()

# Attach to process

pid = device.spawn(['com.example.app'])
session = device.attach(pid)

# LoadScript

with open('rpc_example.js', 'r') as f:
script = session.create_script(f.read())

script.on('message', on_message)
script.load()

device.resume(pid)

# Wait forScriptInitialize

import time
time.sleep(2)

# Call RPC Function

params = {
'user': 'testuser',
'timestamp': '1701234567',
'action': 'login'
}

sign = script.exports_sync.generate_sign(params)
print(f"[+] GenerateSignature: {sign}")

encrypted = script.exports_sync.encrypt('Hello World', 'mykey')
print(f"[+] EncryptResult: {encrypted}")

# 保持运行

sys.stdin.read()

````

## # # 6.1 IDA Pro 远程调试 Native 代码

**准备**：

```bash
# 1. 推送 android_server 到设备
adb push android_server64 /data/local/tmp/
adb shell chmod 755 /data/local/tmp/android_server64

# 2. 以 根 权限Run
adb shell su -c "/data/local/tmp/android_server64"

# 3. Port转发
adb forward tcp:23946 tcp:23946

````

- Port: 23946
- Hostname: localhost
- Port: 23946

3. **Debugger → Attach to Process** → 选择目标 App
4. 在目标函数处设置断点（F2）
5. 触发 App 中的操作，断点命中

## # # 6.2 使用 GDB 调试

```bash
# Attach to process
adb shell
su
ps | grep <app_name>
# 找到 PID，如 12345

gdbserver :5039 --attach 12345

```

arm-linux-androideabi-gdb

# gdb In

(gdb) target remote :5039
(gdb) continue

````
| --------- | --------------------------- |
| `F2` | 设置/取消断点 |
| `F9` | 运行/继续 |
| `F7` | 单步进入（Step Into） |
| `F8` | 单步跳过（Step Over） |
| `Ctrl+F7` | 执行到返回（Run to Return） |
___
## # 第 7 步：使用 Stalker 追踪代码覆盖率（15 分钟）

Frida Stalker 可以记录线程执行的所有指令。

## # # 7.1 基础 Stalker 示例

```javascript
// Stalker trace function execution
Interceptor.attach(
Module.findExportByName("libnative.so", "Java_com_example_Native_encrypt"),
{
onEnter: function (args) {
console.log("[*] Start追踪...");

Stalker.follow(Process.getCurrentThreadId(), {
events: {
call: true, // RecordFunctionCall
ret: false,
exec: false,
},
onReceive: function (events) {
console.log("[*] 捕获到", events.length, "事件");

// Parse events
var calls = Stalker.parse(events, {
annotate: true,
stringify: false,
});

calls.forEach(function (call) {
console.log(" Call:", call);
});
},
});
},
onLeave: function (retval) {
Stalker.unfollow(Process.getCurrentThreadId());
Stalker.flush();
console.log("[*] 追踪End");
},
}
);

````

var base = Module.findBaseAddress("libnative.so");
var size = Process.findModuleByName("libnative.so").size;

Stalker.follow(Process.getCurrentThreadId(), {
transform: function (iterator) {
var instruction = iterator.next();
do {
// Only record instructions within libnative.so
if (
instruction.address.compare(base) >= 0 &&
instruction.address.compare(base.add(size)) < 0
) {
iterator.keep();
}
instruction = iterator.next();
} while (instruction !== null);
},
});

```

│ Frida Hook │ 快速获取 I/O │ 不中断流程 │ 只看单点 │
│ │ 修改返回值 │ 易于 Auto 化 │ 不知道细节 │
├──────────────┼──────────────┼──────────────┼──────────────┤
│ Debug 器 │ 理解算法 Logic │ 完全 Control │ Speed 慢 │
│ (IDA/GDB) │ 单步跟踪 │ 看所有 Variable │ NeedManualOp │
├──────────────┼──────────────┼──────────────┼──────────────┤
│ Stalker │ Code 覆盖率 │ 全 Auto │ Performance 开销大 │
│ │ 追踪 ExecutePath │ No 需断点 │ Output 量巨大 │
└──────────────┴──────────────┴──────────────┴──────────────┘

```

↓ ↓
Send RPC Request Execute Java.perform()
↓ ↓
Etc 待 Result Call App Function
↓ ↓
ReceiveReturnValue ReturnResult
↓ ↓
ProcessData 完成

````

**检查清单**：

1. **确认类/方法名正确**

```javascript
// List all classes
Java.enumerateLoadedClasses({
onMatch: function (className) {
if (className.includes("SignUtils")) {
console.log(className);
}
},
onComplete: function () {},
});

````

- 在 App 中触发相关操作
- 检查是否有其他代码路径

- 在 App 中触发相关操作
- 检查是否有其他代码路径

3. **检查混淆**

```javascript
// If class name is obfuscated as a.b.c, use obfuscated name
var SignUtils = Java.use("a.b.c");
```

**症状**：`script.exports_sync.func()` 一直等待

**解决**：

```python
# UseAsyncCall
def on_rpc_message(result, error):
if error:
print(f"[-] Error: {error}")
else:
print(f"[+] Result: {result}")

script.exports.func(params, on_rpc_message)

# or增加超When
result = script.exports_sync.func(params, timeout=10)

```

// App Code
Socket socket = new Socket("127.0.0.1", 27042); // Frida default port

````

* *绕过**：修改 Frida Server 端口

```bash
frida-server -l 0.0.0.0:8888

````

2. **检查 maps 文件**

```java
BufferedReader reader = new BufferedReader(new FileReader("/proc/self/maps"));
if (line.contains("frida")) {
System.exit(0);
}

```

```bash
# strongR-frida
wget https://github.com/hluwa/strongR-frida-android/releases/download/xxx/frida-server

```

## # ❌ 问题 4: 调试器无法附加

**症状**：IDA Pro 显示 "Cannot attach to process"

**解决**：

1. **检查 SELinux**

```bash
adb shell getenforce
# IfIs Enforcing
adb shell setenforce 0

```

```bash
adb shell ps | grep <app_name>
# 确认 PID 正确

```

    ```bash

adb shell
su
echo 0 > /proc/sys/kernel/yama/ptrace_scope

````

**症状**：启用 Stalker 后 App 卡死

**优化**：

1. **只追踪关键模块**（见第 7.2 步）

2. **减少事件类型**

```javascript
events: {
call: true, // Only record function calls
ret: false, // Don't record returns
exec: false // Don't record every instruction
}

````

    ```javascript

transform: function(iterator) {
// Skip code we don't care about
}

````

## 延伸阅读

## # 相关配方

- **[静态分析深入](./static_analysis_deep_dive.md)** - 先静态找到目标
- **[Frida 常用脚本](../Scripts/frida_common_scripts.md)** - Hook 脚本模板
- **[Frida 反调试](../Anti-Detection/frida_anti_debugging.md)** - 绕过检测
- **[SSL Pinning 绕过](../Network/network_sniffing.md#绕过-ssl-pinning)** - 抓包必备

## # 工具深入

- **[Frida 完整指南](../../02-Tools/Dynamic/frida_guide.md)**
- **[IDA Pro 调试](../../02-Tools/Static/ida_pro_guide.md#远程调试)**
- **[objection 使用](../../02-Tools/Dynamic/)** - TODO

## # 在线资源

- **Frida 官方文档** - https://frida.re/docs/
- **Frida Codeshare** - https://codeshare.frida.re/ (脚本分享)
- **Frida Handbook** - https://learnfrida.info/

## # 理论基础

- **[ARM 汇编](../../04-Reference/Foundations/arm_assembly.md)** - 理解 Native 调试
- **[ART 运行时](../../04-Reference/Foundations/art_runtime.md)** - 理解 Java Hook
___
## 快速参考

## # Frida Hook 模板

**Hook Java 方法**：

```javascript
Java.perform(function () {
var ClassName = Java.use("com.example.ClassName");

ClassName.methodName.implementation = function (arg1, arg2) {
console.log("[*] methodName called");
console.log(" arg1:", arg1);
console.log(" arg2:", arg2);

var result = this.methodName(arg1, arg2);
console.log(" result:", result);

return result;
};
});

````

onEnter: function (args) {
console.log("[*] native_func called");
console.log(" arg0:", args[0]);
console.log(" arg1:", args[1]);
},
onLeave: function (retval) {
console.log(" retval:", retval);
},
});

```
var result = null;
Java.perform(function () {
var Class = Java.use(className);
result = Class[methodName].apply(Class, args);
});
return result;
},
};

```

F8 - 单步跳过
Ctrl+F7 - Execute 到 Return

```
next - 单步跳过
finish - Execute到Return
info registers - View寄存器
x/10x $sp - View栈内容

```

```

```

<!-- 01-Recipes/Analysis/js_obfuscator.md -->

# JavaScript Obfuscator (OB 混淆) 分析

`javascript-obfuscator` 是一个非常流行和强大的开源工具，用于混淆和保护 JavaScript 代码。它的混淆产物通常被称为"OB 混淆"。OB 混淆通过多种手段的组合，使得代码难以阅读、理解和调试。

## 核心混淆技术

OB 混淆主要依赖于以下几种关键技术：

### 1. 字符串混淆 (String Concealing)

- **字符串数组**：将代码中所有的字符串（特别是敏感信息）提取出来，放入一个或多个巨大的数组中。

- **编码与加密**：这些字符串通常会使用 Base64、RC4 或其他自定义算法进行编码或加密。

- **解码函数**：提供一个或多个解码函数。在代码执行时，通过调用 `decoder("0x1")` 这样的形式来获取原始字符串。

- **数组乱序与自愈**：为了防止静态分析，字符串数组的顺序会在脚本执行初期被动态打乱，解码函数也会随之调整，增加了静态还原的难度。

### 2. 控制流平坦化 (Control Flow Flattening)

这是 OB 混淆最核心、最复杂的特征之一。

- **状态机转换**：将原始代码块（如函数体内的语句）分割成多个小的代码片段，并放入一个巨大的 `while` 循环中的 `switch` 结构里。

- **状态变量**：用一个状态变量（程序计数器）来控制 `switch` 的执行顺序。每个 `case` 执行完毕后，会更新状态变量，决定下一个要执行的 `case`。

- **逻辑打断**：原始线性的代码逻辑被完全打乱，变成了在一个巨大的循环中无序跳转，使得人工跟踪变得极其困难。

### 3. 代码转换与编码 (Code Transformation)

- **变量名混淆 (Identifier Mangling)**：将有意义的变量名、函数名和属性名替换成无意义的短字符，如 `_0xabc123`。

- **数字常量替换**：将代码中的数字常量（如 `123`）替换成十六进制字符串表达式（如 `0x7b`），或者更复杂的表达式，增加阅读难度。

- **代理函数 (Proxy Functions)**：将简单的二元运算（如 `a + b`）或对象属性访问（`obj.prop`）替换成对一个代理函数的调用，例如 `add(a, b)`。这使得批量替换和模式识别变得更加困难。

- **死代码注入 (Dead Code Injection)**：在代码中插入一些永远不会被执行的、但看起来很复杂的逻辑分支（通常与不透明谓词结合），用来迷惑分析者。

### 4. 反调试与反格式化 (Anti-Debugging)

- **`debugger` 语句**：在代码中插入 `debugger;` 语句，并且通常会将其包裹在一个无限循环的函数中。当开发者工具打开时，程序会立即暂停并陷入这个循环，阻碍动态调试。

- **函数重绑定**：通过 `Function.prototype.constructor` 或 `eval` 来执行代码，使得常规的断点难以命中。

- **反格式化**：检测代码是否被美化或格式化，如果发现，则可能进入死循环或执行错误逻辑。

## 分析与反混淆策略

反混淆 OB 代码通常是一个系统性的工程，需要多种工具和技术结合。

### 1. 字符串解密与替换

- **定位解码函数**：找到负责从字符串数组中取值并解密的函数。

- **执行解码逻辑**：
- **动态执行**：在 Node.js 或浏览器环境中，直接调用解码函数，将所有加密的字符串预先解密出来。

- **静态分析**：如果解码算法（如 RC4）比较标准，可以编写脚本静态地解密所有字符串。
- **批量替换**：编写脚本（通常基于 AST），将代码中所有对解码函数的调用 `decoder("0x1")` 替换成其返回的原始字符串 `"original_string"`。

### 2. 控制流平坦化还原

这是最困难的一步，但也是最有价值的一步。

- **AST 分析**：使用 Babel 等工具将代码解析成 AST。

- **定位主循环**：找到包含 `while(true)` 和 `switch` 的巨大循环体。

- **识别状态变量**：找到控制 `switch` 跳转的状态变量和它的初始值。

- **重排代码块**：

1. 提取 `switch` 的 `case` 数组和状态变量的初始跳转顺序。
2. 根据这个顺序，将每个 `case` 块中的代码按正确的逻辑重新排列。
3. 移除 `while` 和 `switch` 结构，生成线性的、可读的代码。

- **自动化工具**：社区中有一些尝试自动化还原控制流的工具，但由于 OB 混淆变种繁多，通用性有限。

### 3. 其他净化操作

- **常量表达式计算**：将 `0x7b` 这样的表达式直接计算成 `123`。

- **代理函数内联**：将代理函数的逻辑直接替换回原来的位置，例如将 `add(a, b)` 还原成 `a + b`。

- **死代码移除**：通过分析控制流，识别并删除无法访问到的代码块。

## 常用工具

- **Babel (核心)**：用于解析（Parse）、转换（Transform）和生成（Generate）JavaScript 代码，是编写反混淆脚本的基础。

- **AST Explorer**：在线查看 AST 结构，便于编写转换逻辑。

- **Node.js / 浏览器控制台**：用于动态执行代码片段，特别是解密函数。

- **de4js**, **js-beautify**：用于基本的代码格式化和一些简单的反混淆。

- **AST-Deobfuscator**：一些开源的、基于 AST 的反混淆工具框架，可以作为参考。

<!-- 01-Recipes/Analysis/js_vmp.md -->

# JavaScript VMP 逆向工程

JavaScript VMP（虚拟机保护）是一种高级的代码保护技术，它将原始的 JavaScript 代码转换成一种自定义的、基于虚拟机的字节码。然后，在运行时，一个内置的解释器（或虚拟机）会执行这些字节码。这种方式极大地增加了逆向工程的难度，因为它隐藏了原始的代码逻辑和结构。

## 核心原理

JSVMP 的核心思想是创建一个自定义的指令集和一个对应的虚拟机来执行它。

1. **代码转换（编译）**：

- **词法分析与解析**：将原始 JavaScript 代码解析成抽象语法树（AST）。

- **指令生成**：遍历 AST，将代码逻辑转换成自定义的字节码序列。例如，`a + b` 可能会被转换成 `PUSH a; PUSH b; ADD`。

- **虚拟机注入**：将实现了解释器、指令调度循环和操作函数的虚拟机（通常用 JavaScript 编写）与生成的字节码打包在一起。

2. **运行时执行**：

- **虚拟机初始化**：设置虚拟机的执行环境，如堆栈（Stack）、程序计数器（PC）和上下文。

- **指令循环（Fetch-Decode-Execute）**：
- **Fetch**：从字节码数组中获取当前 PC 指向的指令。

- **Decode**：解析指令的操作码和操作数。

- **Execute**：执行指令对应的操作，例如进行数学运算、操作堆栈、调用函数等。
- **程序结束**：当执行完所有字节码后，虚拟机将结果返回或完成操作。

## 常见特征

- **巨大的代码体积**：代码中通常包含一个非常大的数组（字节码）和一个庞大的 `switch` 或 `while` 循环（虚拟机解释器）。

- **控制流平坦化**：原始的 `if/else`, `for`, `while` 结构被转换成由程序计数器（PC）控制的跳转指令，使得代码逻辑难以跟踪。

- **不透明谓词**：引入一些恒为真或恒为假的复杂条件判断，增加静态分析的难度。

- **自定义数据结构**：使用自定义的堆栈来存储变量和中间结果，而不是直接使用 JavaScript 的变量。

## 分析与脱壳策略

逆向 JSVMP 是一个复杂的过程，通常需要结合静态和动态分析。

### 1. 静态分析：理解虚拟机

- **定位核心组件**：
- **字节码数组**：通常是一个巨大的、包含数字或短字符串的数组。

- **虚拟机入口**：启动整个解释器循环的函数。

- **分发器（Dispatcher）**：通常是一个大的 `switch` 语句或 `while(true)` 循环，根据指令码调用不同的处理函数。

- **指令处理器（Handlers）**：`switch` 中的每个 `case` 或被调用的函数，实现了具体指令的功能。
- **指令集重建**：
- 通过分析每个 Handler 的功能，逐步还原出每个字节码对应的具体操作（如 `ADD`, `SUB`, `JMP` 等）。

- 为每个操作码（Opcode）添加注释，记录其功能。这是一个非常耗时但至关重要的步骤。

### 2. 动态分析：跟踪与调试

- **Hook 关键函数**：使用 Frida 或浏览器开发者工具在关键位置（如指令处理器）下断点或插入日志。
- **跟踪 PC 和操作数**：记录每次循环的程序计数器（PC）和当前指令的操作数，可以得到完整的执行轨迹（Trace）。

- **监控堆栈变化**：观察虚拟机自定义堆栈的压入（push）和弹出（pop）操作，以理解数据流。
- **AST 辅助分析**：使用工具（如 Babel）将 Handler 的代码解析成 AST，可以更快地理解其功能，甚至自动化地识别指令模式。

### 3. 代码还原与重构

- **编写反编译器**：基于已经重建的指令集，编写一个脚本，将字节码序列翻译回更高级、更易读的 JavaScript 代码。这是一个高级步骤，需要对虚拟机有完整的理解。

- **手动逻辑重构**：对于不是特别复杂的 VMP，可以通过跟踪执行流程，手动将关键逻辑（如加密算法）用等效的 JavaScript 代码重写出来。

## 常用工具

- **浏览器开发者工具**：用于下断点、单步调试和观察变量。

- **Frida**：用于 Hook 关键函数，实现动态跟踪。

- **Babel**：用于将 JavaScript 代码解析成 AST，辅助静态分析。

- **AST Explorer**：一个在线工具，可以方便地查看代码对应的 AST 结构。

- **IDA Pro / Ghidra**：虽然主要用于原生代码，但它们强大的反汇编和反编译功能可以为理解复杂的 JavaScript 虚拟机逻辑提供借鉴。

<!-- 01-Recipes/Analysis/native_string_obfuscation.md -->

# Native 层字符串混淆与逆向

在 Android Native 开发（C/C++）中，直接将明文字符串硬编码在代码中会带来安全风险。静态分析工具（如 IDA Pro、Ghidra）可以轻易地在二进制文件的 `.rodata`（只读数据）段中找到这些字符串，从而泄露 API 地址、加密密钥、敏感校验逻辑等信息。因此，开发者通常会采用各种字符串混淆技术来保护这些数据。

## 常见的 Native 字符串混淆技术

### 1. 栈上动态构造 (Stack-based Construction)

这是最简单的一种方法。它避免在数据段中留下完整的字符串，而是在函数运行时，逐个字符地将字符串构造在栈上。

**示例代码:**

```cpp
void get_secret_url() {
char url[19];
url[0] = 'h'; url[1] = 't'; url[2] = 't'; url[3] = 'p';
url[4] = 's'; url[5] = ':'; url[6] = '/'; url[7] = '/';
url[8] = 'a'; url[9] = 'p'; url[10] = 'i'; url[11] = '.';
url[12] = 'e'; url[13] = 'x'; url[14] = 'a'; url[15] = 'm';
url[16] = 'p'; url[17] = 'l'; url[18] = 'e';
url[19] = '\0'; // Null terminator
// ... use url
}

```

**示例代码:**

```cpp
char* decrypt_string(char* encrypted) {
char key = 0xAB;
int len = strlen(encrypted);
for (int i = 0; i < len; i++) {
encrypted[i] = encrypted[i] ^ key;
}
return encrypted;
}

void use_secret() {
// "secret_key" Xored with 0xAB
char encrypted_key[] = { 0xCF, 0xC4, 0xC2, 0xCD, 0xC4, 0xD1, 0xDF, 0xCB, 0xC4, 0xD8, 0x00 };
char* secret = decrypt_string(encrypted_key);
// ... use secret
}

```

**优点**: 自动化、全局覆盖、对开发者透明。
**缺点**: 通常需要定制的编译器或工具链。

## 逆向策略

逆向字符串混淆的目标是 **批量地、自动化地** 将混淆的字符串还原出来。

### 1. 静态分析 (IDA Pro / Ghidra)

静态分析是识别解密例程（Decryption Routine）和批量解密的关键。

- **识别解密模式**:
- 寻找特征性的循环结构。一个循环遍历内存、执行固定操作（如 `XOR`）然后写回，这通常就是解密函数。

- 在 IDA Pro 中，这种循环的图形视图非常具有辨识度。
- **定位解密函数**:
- 通过交叉引用（Xrefs）找到加密数据被哪些函数使用。这些函数很可能就是解密函数。

- 一旦找到一个解密函数，分析其逻辑（输入、输出、加密算法）。
- **自动化解密 (IDAPython / Ghidra Script)**:

1. **编写脚本**: 这是最高效的方法。编写一个脚本来模拟解密逻辑。
2. **寻找引用**: 脚本首先找到所有对解密函数的交叉引用。
3. **提取参数**: 在每个调用点，脚本向上回溯，解析传递给解密函数的参数（加密的数据、密钥等）。
4. **执行解密**: 脚本在内部执行解密算法。
5. **添加注释**: 最后，将解密后的字符串作为注释添加到 IDA Pro 或 Ghidra 的反汇编代码中。

### 2. 动态分析 (Frida)

当静态分析过于复杂或存在反调试时，动态分析是最佳选择。

- **Hook 解密函数**:

1. 通过初步的静态分析定位到疑似的解密函数。
2. 使用 Frida `Interceptor.attach` 来 Hook 这个函数的入口和出口。
3. 在 `onEnter` 中，打印函数的参数（通常是指向加密数据的指针）。
4. 在 `onLeave` 中，打印函数的返回值（通常是指向已解密的明文字符串的指针）。
5. 通过运行 App 并触发不同功能，就可以从日志中收集到大量的明文字符串。

- **内存扫描**:
- 另一种策略是让应用运行一段时间，然后使用 Frida 脚本或 GameGuardian 等工具扫描整个进程内存，寻找符合字符串特征（如 ASCII、UTF-8）的内存区域。

- **优点**: 无需关心解密逻辑。

- **缺点**: 信息非常嘈杂，包含大量无用数据；无法将被加密存储但在运行时未被使用的字符串解密出来。

### 3. 模拟执行 (Emulation)

对于一些独立的、没有太多外部依赖的解密函数，可以使用模拟执行框架（如 `Unicorn Engine`）来解密。

1. **提取代码和数据**: 从二进制文件中 dump 出解密函数的机器码和需要解密的字节数组。
2. **设置环境**: 在 Unicorn 中，映射所需的内存区域，将加密数据放入。
3. **模拟执行**: 设置好初始寄存器状态（如参数指针），然后开始模拟执行解密函数的机器码。
4. **获取结果**: 执行完毕后，从内存中读回解密后的字符串。

**优点**: 速度比动态分析快，无需运行完整的 App，可绕过反调试。
**缺点**: 环境设置复杂，不适用于有大量系统调用或复杂依赖的函数。

<!-- 01-Recipes/Analysis/ollvm_deobfuscation.md -->

# OLLVM 反混淆

OLLVM (Obfuscator-LLVM) 是一个著名的开源代码混淆框架，它在 LLVM 编译器 IR (中间表示) 层面进行操作。这使其能够与具体语言无关，并对代码应用复杂的、难以逆向的转换。

!!! warning "场景导入：当你遇到 OLLVM"
打开 IDA，反编译一个函数，结果看到：

- 一个巨大的 `switch-case` 循环，有几十甚至上百个 case 分支
- 每个 case 里只有几行代码，然后又跳回 switch
- 到处都是看起来有用实际无用的 `if` 判断
- 简单的加法被替换成了 `a = b - (-c)` 这样的怪异表达式

**你的第一反应可能是：这是什么鬼？**

恭喜，你遇到了 OLLVM 控制流平坦化 (FLA) + 虚假控制流 (BCF) + 指令替换 (SUB) 的"三件套"。
这是目前 Android Native 层最常见的商业级混淆方案。

**关键问题**：面对这种混淆，是选择"硬看"代码，还是有更聪明的办法？

本文档涵盖了常见的 OLLVM 混淆通道 (pass) 及其分析和逆向策略。

---

## 核心混淆技术

OLLVM 的主要优势在于其三种核心混淆技术：

1. **控制流平坦化 (`-fla`)**: 该技术会彻底平坦化一个函数的控制流。它通过将所有基本块放入一个单一的、巨大的分发器循环（"主分发器"）中来隐藏原始的程序流程。一个状态变量用于控制下一个要执行的代码块。逆向此技术需要重建原始的控制流图 (CFG)。

2. **虚假控制流 (`-bcf`)**: 该技术在代码中插入无效的条件分支和不透明谓词。这些分支被设计为静态分析难以解析，但在运行时，它们总是会得出相同的结果。这会给控制流图增加大量的噪声。

3. **指令替换 (`-sub`)**: 这是最简单的混淆方式。它将标准的二进制运算符（如 `add`, `sub`, `and`, `or`）替换为功能上等价但更复杂的指令序列。例如，`a = b + c` 可能会变成 `a = b - (-c)`。

---

## 分析与反混淆策略

!!! question "思考：静态分析 vs 动态分析，哪个更有效？"
面对 OLLVM 混淆，有两种完全不同的思路：

**静态分析**：

- ✅ 优势：能看到所有可能的执行路径，包括错误处理分支
- ❌ 劣势：需要对抗大量的虚假分支，分析工作量巨大
- 适用场景：你需要理解完整的算法逻辑，或者寻找漏洞

**动态分析**：

- ✅ 优势：直接记录真实执行路径，绕过所有虚假分支
- ❌ 劣势：只能看到当前输入下的执行路径，可能遗漏关键分支
- 适用场景：你只想提取算法结果（如加密签名），不关心内部逻辑

**实战建议**：

1. 先用动态分析（Frida Stalker / Unidbg trace）快速获取"真实"的执行流
2. 再用静态分析验证和补充动态分析遗漏的部分
3. 如果目标是自动化（如算法还原），考虑符号执行（Angr）

### 1. 静态分析

- **CFG 重建**: 对于控制流平坦化，关键是识别状态变量和分发器。通过符号执行或模式匹配分发器逻辑，可以确定每个真实基本块的后继，从而重建原始图。

- **不透明谓词求解**: Z3 或其他 SMT 求解器等工具可用于自动证明虚假控制流中的条件是不变的。这使得分析师能够识别并移除无效的代码路径。

- **模式匹配**: 对于指令替换，可以识别并替换简单的模式。例如，像 `x = rdtsc(); y = x & 1; if (y == 0) ...` 这样的序列是一个常见的虚假谓词。

### 2. 动态分析

- **使用 Frida/Unidbg 进行追踪**: 动态追踪非常有效。通过使用 Frida 的 `Stalker` 或 Unidbg 的追踪功能，可以记录运行时执行的基本块的确切顺序。这可以绕过所有的控制流混淆，为你提供"真实"的执行路径。

- **符号执行**: 像 Angr 这样的引擎可用于探索程序状态。符号执行可以自动求解路径约束，从而有效地反混淆控制流并简化不透明谓词。这个过程可能很慢，但功能非常强大。

### 3. 自动化工具

- **d-obfuscator**: 一个基于 Python 的工具，使用符号执行（通过 Angr）来反混淆 OLLVM。

- **QB-Di**: 一个基于 QBDI 动态插桩框架的交互式反混淆工具。

- **Triton**: 一个动态二进制分析框架，可以通过编写脚本来执行污点分析和符号执行。

<!-- 01-Recipes/Analysis/re_workflow.md -->

# Recipe: Android 应用逆向工程完整工作流程

## 问题场景

你刚拿到一个 Android 应用需要分析，但面临以下挑战：

- 🤔 **"拿到 APK 后应该先做什么？从哪里入手？"**
- 🤔 **"静态分析和动态分析应该如何配合？"**
- 🤔 **"如何系统化地分析，而不是盲目尝试？"**
- 🤔 **"遇到加固、混淆、反调试该怎么办？"**
- 🤔 **"分析完成后如何修改应用以达到目的？"**

本配方提供一个**经过实战验证的标准化工作流程**，帮助你系统化地完成从信息收集到代码修改的整个逆向工程过程。

---

## 工具清单

## # 必备工具

| 项目               | 说明                   |
| ------------------ | ---------------------- |
| [x] **APK 提取**   | ADB + Package Manager  |
| [x] **解包/回包**  | Apktool                |
| [x] **反编译工具** | Jadx-GUI（推荐）或 JEB |
| [x] **动态分析**   | Frida + Frida-tools    |

- [x] **Root 设备/模拟器** - Genymotion、夜神、雷电等

## # 可选工具

| 项目              | 说明                             |
| ----------------- | -------------------------------- |
| ☐ **Native 分析** | IDA Pro / Ghidra / Binary Ninja  |
| ☐ **网络抓包**    | mitmproxy / Burp Suite / Charles |
| ☐ **调试器**      | Android Studio / jdb             |
| ☐ **签名工具**    | apksigner（Android SDK 自带）    |
| ☐ **加壳检测**    | PKid / ApkTool-Plus              |

---

## 前置知识

✅ **了解 Android 基本架构**（四大组件、Manifest 文件）
✅ **掌握基本 Java/Smali 语法**
✅ **熟悉 ADB 命令**
✅ **拥有 Root 设备**（动态分析必需）

---

## 解决方案

## # 核心原则

> **由外到内、由浅入深、静动结合**
>
> 1. **信息侦察** → 了解应用基本信息和技术栈
> 2. **静态分析** → 理解代码逻辑和算法
> 3. **动态验证** → 观察实际行为、绕过保护
> 4. **代码修改** → 实现永久性改动

---

## 阶段一：信息收集与初步分析（ 15-30 分钟）

- **目标\*\***：在不运行应用的情况下，快速了解基本信息、功能和潜在入口点。

## # 步骤 1：获取 APK 文件

### 方法 A：从已安装应用提取

```bash
# 1. 列出所有包名
adb shell pm list packages | grep <关键词>

# 示例：查找音乐应用
adb shell pm list packages | grep music
# 输出：package:com.example.musicapp

# 2. 获取 APK 路径
adb shell pm path com.example.musicapp
# 输出：package:/data/app/~~ABC123/com.example.musicapp-XYZ456/base.apk

# 3. 拉取到本地
adb pull /data/app/~~ABC123/com.example.musicapp-XYZ456/base.apk ./target.apk

# 一键脚本（保存为 pull-apk.sh）
PACKAGE=$1
APK_PATH=$(adb shell pm path $PACKAGE | cut -d: -f2 | tr -d '\r')
adb pull $APK_PATH ./$PACKAGE.apk
echo "[+] APK 已保存: $PACKAGE.apk"

```

````

```bash
# 使用 Apktool（推荐 - 解码资源和 Smali）
apktool d target.apk -o target_unpacked

# 输出目录结构：
# target_unpacked/
# ├── androidManifest.xml (已解码)
# ├── apktool.yml
# ├── smali/ (Dalvik 字节码)
# ├── smali_classes2/ (多个 DEX)
# ├── res/ (资源文件)
# ├── lib/ (native 库)
# ├── assets/ (资产文件)
# └── original/

# 快速查看（不解码）
unzip -l target.apk
unzip target.apk -d target_quick

````

```bash
# 查看已解码的 manifest
cat target_unpacked/AndroidManifest.xml

# 或使用工具美化
xmllint --format target_unpacked/AndroidManifest.xml

```

| **包名** | `<manifest package="...">` | 应用唯一标识 |
| **入口 Activity** | `<activity>` 带 `LAUNCHER` intent | 应用启动入口 |
| **Application 类** | `<application android:name="...">` | 自定义 Application（可能有初始化逻辑）|
| **权限** | `<uses-permission>` | 推断功能（网络、存储、位置等）|
| **调试标志** | `android:debuggable="true"` | ⚠️ 可直接调试 |
| **备份标志** | `android:allowBackup="true"` | ⚠️ 数据可导出 |
| **导出组件** | `android:exported="true"` | ⚠️ 可被外部调用 |
| **URL Scheme** | `<intent-filter>` 带 `<data>` | Deep link 入口点 |
| **ContentProvider** | `<provider>` | 数据库接口 |
| **Service** | `<service>` | 后台服务 |

### 真实案例：分析腾讯乐固应用

```xml
<application
android:name="com.tencent.StubShell.TxAppEntry" <!-- ⚠️ 加壳特征 -->
android:debuggable="false"
android:allowBackup="false">

<activity android:name=".MainActivity"
android:exported="true"> <!-- ⚠️ 可外部启动 -->
<intent-filter>
<action android:name="android.intent.action.MAIN"/>
<category android:name="android.intent.category.LAUNCHER"/>
</intent-filter>

<!-- ⚠️ 自定义 URL Scheme -->
<intent-filter>
<data android:scheme="myapp" android:host="open"/>
<action android:name="android.intent.action.VIEW"/>
<category android:name="android.intent.category.BROWSABLE"/>
</intent-filter>
</activity>
</application>

```

- ⚠️ 可通过 `myapp://open` URL 启动
- ✅ 调试和备份已禁用（安全配置良好）

---

## # 步骤 4：快速目录结构审查

```bash
# 查看 native 库
ls -lh target_unpacked/lib/*/
# 输出示例：
# lib/arm64-v8a/libnative-lib.so (2.3 MB) ← Native 代码
# lib/arm64-v8a/libencrypt.so (450 KB) ← 可能是加密库
# lib/armeabi-v7a/libnative-lib.so

# 查看资产文件
ls -lh target_unpacked/assets/
# 输出示例：
# config.json ← 配置文件
# encrypted.dat ← 加密数据
# web/index.html ← H5 页面

# 统计 Smali 文件数量（估算代码规模）
find target_unpacked/smali* -name "*.smali" | wc -l
# 输出：8432 (约 8000+ 类)

# 搜索可疑关键词
grep -r "password" target_unpacked/smali/ | head -n 10
grep -r "encrypt" target_unpacked/smali/ | head -n 10

```

- ✅ 技术栈识别（是否加壳、是否使用 native 代码）
- ✅ 潜在攻击面（导出组件、URL Scheme）
- ✅ 初步分析方向（应该深入哪里）

---

## 阶段二：静态分析（ 1-3 小时）

- **目标\*\***：通过反编译理解应用如何工作、算法和业务逻辑。

## # 步骤 1：使用 Jadx 反编译

```bash
# 启动 Jadx GUI
jadx-gui target.apk

# 或命令行模式
jadx -d target_decompiled target.apk

```

- "encrypt"、"decrypt"、"AES"、"DES" → 加密算法
- "http"、"api"、"request" → 网络请求
- "premium"、"vip"、"paid" → 会员检查
- "signature"、"sign" → 签名算法
- "root"、"frida"、"xposed" → 反检测

  ```

  ```

* **📍 定位关键代码\*\***：

1. 从入口 Activity 开始（`MainActivity.onCreate()`）
2. 检查 Application 子类（`Application.onCreate()` - 初始化逻辑）
3. 搜索字符串常量（右键 → "查找用法"）
4. 分析网络请求（OkHttp、Retrofit、HttpURLConnection）
5. 追踪用户输入处理（`onClick` 回调）

- - 代码导航\*\*\*\*：

````
- Ctrl+H：查看类层次结构
- Ctrl+F12：查看当前类的所有方法
    ```

- --

## # 步骤 2：识别代码模式

### ✅ 正常代码

```java
// 可读的类名和方法名
public class LoginManager {
private static final String API_URL = "https://api.example.com/login";

public boolean login(String username, String password) {
String encryptedPassword = AESUtil.encrypt(password);
return ApiClient.post(API_URL, username, encryptedPassword);
}
}

````

// ProGuard/R8 混淆
public class a {
private static final String a = "https://api.example.com/login";

public boolean a(String str, String str2) {
String b = b.a(str2); // 字符串常量通常会保留
return c.a(a, str, b);
}
}

````


- --

## # 步骤 3：分析 Native 库

如果应用包含 `.so` 文件，核心算法通常在这里实现。

### 方法 A：使用 IDA Pro 分析

```bash
# 1. 打开 SO 文件
ida64 target_unpacked/lib/arm64-v8a/libnative-lib.so

# 2. 等待自动分析完成

# 3. 查看导出函数（Exports 窗口）
# 查找 JNI 函数命名模式：
# Java_com_example_app_NativeHelper_encrypt
# Java_<包名>_<类名>_<方法名>

# 4. 反编译关键函数（F5 反编译为伪代码）

````

# 2. 新建项目 → 导入文件 → 选择 .so 文件

# 3. 双击文件 → 自动分析

# 4. 窗口 → Symbol Tree → Exports

# 查看导出函数列表

# 5. 双击函数 → 反编译（右侧面板显示 C 伪代码）

```

# 输出示例：
# 00012340 T Java_com_example_app_Crypto_encrypt
# 00012680 T Java_com_example_app_Crypto_decrypt
# 00012a00 T Java_com_example_app_Sign_generate

# 搜索字符串（可能找到加密密钥）
strings libnative-lib.so | grep -i "key\|secret\|password"

```

````markdown
## 分析目标

- ☐ 提取登录 API 签名算法
- ☐ 绕过 VIP 会员检查
- ☐ 获取加密密钥

## 已定位的关键类/方法

1. `com.example.app.utils.SignUtil.generateSign(Map params)` - 签名生成
2. `com.example.app.user.UserManager.isPremium()` - 会员检查
3. Native: `Java_com_example_app_Crypto_encrypt` - 加密函数

## Hook 策略

- Hook `generateSign()` 查看参数和返回值
- Hook `isPremium()` 强制返回 true
- Hook native 函数获取加密密钥

## 预期挑战

- 签名算法可能在 native 层
- 可能有 Frida 检测
- 网络请求可能有 SSL pinning

  ```

  ```

### 阶段二产出

- ✅ 理解应用的核心功能和业务逻辑
- ✅ 定位关键类、方法和 native 函数
- ✅ 识别使用的加密/签名算法
- ✅ 确定动态分析的 hook 点清单
- ✅ 识别潜在的反调试/反 hook 机制

---

## 阶段三：动态分析（ 2-4 小时）

- **目标\*\***：在运行时观察实际行为，验证静态分析结论，绕过保护机制。

## # 步骤 1：设置 Frida 环境

```bash
# 1. 启动 Frida Server（在设备上）
adb push frida-server /data/local/tmp/
adb shell "chmod 755 /data/local/tmp/frida-server"
adb shell "/data/local/tmp/frida-server &"

# 2. 验证连接（在 PC 上）
frida-ps -U
# 应该看到设备上运行的进程列表

# 3. 测试 hook
frida -U -f com.example.app --no-pause
# 进入交互式控制台
```
````

基于静态分析结果，编写 Frida 脚本。

### 示例 1：Hook 会员检查

```javascript
// hook_premium.js - 绕过 VIP 检查

Java.perform(function () {
  console.log("[+] 开始 hook 会员检查...");

  var UserManager = Java.use("com.example.app.user.UserManager");

  // Hook isPremium 方法
  UserManager.isPremium.implementation = function () {
    console.log("[+] isPremium() 被调用");

    // 调用原始方法查看真实结果
    var realResult = this.isPremium();
    console.log(" 真实返回值: " + realResult);

    // 强制返回 true
    console.log(" 修改返回值: true");
    return true;
  };

  console.log("[+] Hook 完成");
});
```

// hook_sign.js - 提取签名算法

Java.perform(function() {
var SignUtil = Java.use("com.example.app.utils.SignUtil");

SignUtil.generateSign.implementation = function(params) {
console.log("\n[SIGN] generateSign() 被调用");
console.log(" 参数类型: " + params.$className);

// 如果是 Map，遍历打印
if (params.$className === "java.util.HashMap") {
var HashMap = Java.use("java.util.HashMap");
var entrySet = params.entrySet();
var iterator = entrySet.iterator();

console.log(" 参数内容:");
while (iterator.hasNext()) {
var entry = iterator.next();
var key = entry.getKey();
var value = entry.getValue();
console.log(" " + key + " = " + value);
}
}

// 调用原始方法
var result = this.generateSign(params);

console.log(" 签名结果: " + result);
console.log(" 签名长度: " + result.length);

// 打印调用栈
console.log(" 调用栈:");
console.log(Java.use("android.util.Log").getStackTraceString(
Java.use("java.lang.Exception").$new()
));

return result;
};

console.log("[+] 签名 hook 完成");
});

```

var encryptAddr = Module.findExportByName("libnative-lib.so",
"Java_com_example_app_Crypto_encrypt");

if (encryptAddr) {
console.log("[+] 找到 encrypt 函数: " + encryptAddr);

Interceptor.attach(encryptAddr, {
onEnter: function(args) {
console.log("\n[NATIVE] encrypt() 被调用");
console.log(" JNIEnv*: " + args[0]);
console.log(" jobject: " + args[1]);

// 第 3 个参数通常是 jstring（输入数据）
try {
var env = Java.vm.getEnv();
var inputStr = env.getStringUtfChars(args[2], null);
var input = inputStr.readCString();
console.log(" 输入: " + input);
env.releaseStringUtfChars(args[2], inputStr);
} catch (e) {
console.log(" 输入: [无法读取]");
}
},

onLeave: function(retval) {
// 返回值也是 jstring（密文）
try {
var env = Java.vm.getEnv();
var outputStr = env.getStringUtfChars(retval, null);
var output = outputStr.readCString();
console.log(" 输出: " + output);
env.releaseStringUtfChars(retval, outputStr);
} catch (e) {
console.log(" 输出: " + retval);
}
}
});

console.log("[+] Native hook 完成");
} else {
console.log("[-] 未找到 encrypt 函数");
}

```

// bypass_all.js - 综合绕过脚本

Java.perform(function() {
console.log("[+] 加载反检测模块...");

// 1. 绕过 Frida 端口检测
var connect = Module.findExportByName("libc.so", "connect");
Interceptor.attach(connect, {
onEnter: function(args) {
var sockaddr = ptr(args[1]);
var port = (sockaddr.add(2).readU8() << 8) | sockaddr.add(3).readU8();
if (port === 27042 || port === 27043) {
console.log("✓ [检测] 拦截了 Frida 端口扫描");
sockaddr.add(2).writeU8(0xFF);
}
}
});

// 2. 绕过 TracerPid 检测
var fgets = Module.findExportByName("libc.so", "fgets");
Interceptor.attach(fgets, {
onLeave: function(retval) {
if (retval && !retval.isNull()) {
var line = retval.readCString();
if (line && line.includes("TracerPid:")) {
retval.writeUtf8String("TracerPid:\t0\n");
console.log("✓ [检测] 修改 TracerPid 为 0");
}
}
}
});

// 3. 绕过字符串检测
var strstr = Module.findExportByName("libc.so", "strstr");
Interceptor.attach(strstr, {
onLeave: function(retval) {
if (this.needle && this.needle.toLowerCase().includes("frida")) {
retval.replace(ptr(0));
console.log("✓ [检测] 隐藏 Frida 字符串");
}
},
onEnter: function(args) {
this.needle = args[1].readCString();
}
});

console.log("[+] 反检测模块加载完成");
});

```
- l bypass_all.js \
- l hook_premium.js \
- -no-pause

```

# 1. 配置代理

adb shell settings put global http_proxy 192.168.1.100:8080

# 2. 启动应用并绕过 SSL pinning

frida -U -f com.example.app -l bypass_ssl_pinning.js --no-pause

# 3. 在 Burp Suite 中查看流量

```
var RealInterceptorChain = Java.use("okhttp3.internal.http.RealInterceptorChain");

RealInterceptorChain.proceed.implementation = function(request) {
console.log("\n[HTTP] " + request.method() + " " + request.url().toString());

// 打印请求头
var headers = request.headers();
for (var i = 0; i < headers.size(); i++) {
console.log(" " + headers.name(i) + ": " + headers.value(i));
}

var response = this.proceed(request);

console.log("[RESP] Code: " + response.code());

return response;
};
});

```

- ✅ 成功绕过会员检查、反调试等限制
- ✅ 完整的网络请求/响应日志
- ✅ 准备好重打包的修改点

---

## 阶段四：代码修改与重打包（ 30-60 分钟）

- **目标\*\***：对应用进行永久性修改，实现持久化的功能改变。

## # 步骤 1：修改 Smali 代码

基于动态分析结果，在 Smali 层面进行修改。

### 示例 1：绕过会员检查

- **原始 Java 代码\*\***（Jadx 反编译）：

```java
public boolean isPremium() {
return this.userInfo.vipStatus == 1;
}

```

# 读取 userInfo.vipStatus

iget-object v0, p0, Lcom/example/app/user/UserManager;->userInfo:Lcom/example/app/model/UserInfo;
iget v0, v0, Lcom/example/app/model/UserInfo;->vipStatus:I

# 比较是否等于 1

const/4 v1, 0x1
if-ne v0, v1, :cond_0

# 如果相等，返回 true

const/4 v0, 0x1
return v0

# 如果不相等，返回 false

:cond_0
const/4 v0, 0x0
return v0
.end method

```

# 直接返回 true，跳过所有检查
const/4 v0, 0x1
return v0
.end method

```

.method private showAd()V
.locals 1

# 检查是否不是 VIP

invoke-virtual {p0}, Lcom/example/app/MainActivity;->isPremium()Z
move-result v0

# 如果不是 VIP，显示广告

if-nez v0, :cond_0
invoke-direct {p0}, Lcom/example/app/MainActivity;->loadAdView()V

:cond_0
return-void
.end method

```

# 直接返回，不执行任何操作
return-void
.end method

```

```bash
# 1. 使用 Apktool 重打包
apktool b target_unpacked -o modified.apk

# 输出：
# I: Using Apktool 2.x.x
# I: Checking whether sources has changed...
# I: Smali folder: smali
# I: Smali folder: smali_classes2
# I: Copying raw resources...
# I: Copying libs... (/lib)
# I: Copying assets... (/assets)
# I: Building apk file...
# I: Copying unknown files/dir...
# I: Built apk into: modified.apk

# 2. 检查生成的 APK
ls -lh modified.apk
# -rw-r--r-- 1 user user 8.5M modified.apk

```

```bash
# 1. 生成签名密钥（只需执行一次）
keytool -genkey -v \
- keystore my-release-key.keystore \
- alias my-key-alias \
- keyalg RSA \
- keysize 2048 \
- validity 10000

# 提示输入密码和信息：
# Enter keystore password: [输入密码]
# Re-enter new password: [再次输入]
# What is your first and last name? [随意填写]
# ...

# 2. 签名 APK
apksigner sign \
- -ks my-release-key.keystore \
- -ks-key-alias my-key-alias \
- -out signed.apk \
modified.apk

# 提示输入 keystore 密码
# 输出：signed.apk

# 3. 验证签名
apksigner verify signed.apk
# 输出：Verifies
# 表示签名成功

```

java -jar uber-apk-signer.jar --apks modified.apk

# 输出：modified-aligned-debugSigned.apk

````

```bash
# 1. 卸载原应用（如果存在）
adb uninstall com.example.app

# 2. 安装修改后的 APK
adb install signed.apk

# 如果遇到签名冲突：
# adb install -r signed.apk (替换安装)

# 3. 启动应用
adb shell am start -n com.example.app/.MainActivity

# 4. 查看日志验证修改
adb logcat | grep "example.app"

````

- ☐ 修改的功能生效（例如 VIP 权限解锁）
- ☐ 没有崩溃或异常行为
- ☐ 网络功能正常（如果修改了签名相关代码）

### 常见问题排查

```bash
# 查看崩溃日志
adb logcat | grep "AndroidRuntime"

# 常见错误：
# 1. "INSTALL_PARSE_FAILED_NO_CERTIFICATES"
# → 签名失败，重新签名

# 2. "INSTALL_FAILED_UPDATE_INCOMPATIBLE"
# → 签名不匹配，先卸载原应用

# 3. 应用崩溃
# → 查看 logcat，可能是 Smali 语法错误

```

避免盲目分析浪费时间
↓
静态分析 (1-3 小时)
↓
理解代码逻辑和算法
定位关键函数和 hook 点
↓
动态分析 (2-4 小时)
↓
验证静态分析结论
绕过运行时保护
获取实际数据（密钥、API 参数）
↓
代码修改 (30-60 分钟)
↓
永久性修改
无需每次都使用 Frida

````
| **绕过混淆** | ❌ 困难 | ✅ 可行 | ✅ 高效 |
| **获取密钥** | ❌ 难（可能硬编码）| ✅ 易（运行时）| ✅ 最佳 |
| **修改代码** | ✅ 精确 | ❌ 不持久 | ✅ 灵活 |
| **时间成本** | 高（有混淆时）| 中等 | 低（互补）|

- --

## 常见问题

## # ❌ 问题 1：Apktool 解包失败

* *错误信息**：`brut.androlib.AndrolibException: Could not decode arsc file`

* *可能原因**：
1. APK 使用了资源混淆（AndResGuard）
2. APK 已损坏
3. Apktool 版本过旧


* *解决方案**：

```bash
# 1. 更新 Apktool 到最新版本
# 下载：https://ibotpeaches.github.io/Apktool/

# 2. 使用 -r 参数跳过资源解码
apktool d target.apk -r -o target_unpacked
# -r: 不解码资源文件 (resources.arsc)

# 3. 使用 --only-main-classes 仅解码主 DEX
apktool d target.apk --only-main-classes -o target_unpacked

# 4. 如果只需要 Smali，直接使用 dex2jar + jd-gui
d2j-dex2jar target.apk
# 生成 target-dex2jar.jar，用 JD-GUI 打开

````

- **解决方案\*\***：

```bash
# 1. 优先使用动态分析
# 混淆的代码在运行时行为不变
# 使用 Frida 直接 hook，观察参数和返回值

# 2. 利用字符串常量定位
# 字符串通常不会被混淆
# 在 Jadx 中搜索关键字符串，反向定位代码

# 3. 重命名类/方法（Jadx 支持）
# 右键类名 → Rename
# 根据功能手动重命名为有意义的名称

# 4. 使用符号还原工具
# 如果有 mapping.txt（混淆映射文件）
# 可以使用工具还原符号

```

1. 应用未运行
2. 包名错误
3. Frida Server 未启动

- **解决方案\*\***：

```bash
# 1. 检查 Frida Server 是否运行
adb shell ps | grep frida-server
# 如果没有输出，需要启动 Frida Server

# 2. 确认应用正在运行
adb shell ps | grep com.example.app
# 或
frida-ps -U | grep example

# 3. 使用正确的包名
# 查看已安装应用的包名
adb shell pm list packages | grep example

# 4. 使用 spawn 模式（自动启动应用）
frida -U -f com.example.app -l script.js --no-pause
# -f: spawn 模式，会自动启动应用

# 5. 检查设备连接
adb devices
# 应显示：device（不是 offline 或 unauthorized）

```

1. Smali 语法错误
2. 修改破坏了类结构
3. 缺少依赖

- **解决方案\*\***：

```bash
# 1. 查看详细崩溃日志
adb logcat -c # 清空日志
adb logcat | grep -E "AndroidRuntime|FATAL"

# 2. 验证 Smali 语法
# 用 Apktool 重新反编译修改后的 APK
apktool d signed.apk -o verify_unpacked
# 查看是否有错误提示

# 3. 回滚修改，逐步测试
# 先修改单个方法，通过后再修改其他

# 4. 使用 baksmali/smali 验证
baksmali d modified.apk -o smali_test
smali a smali_test -o test.dex
# 如果验证通过，说明 Smali 语法正确

# 5. 检查方法签名是否正确
# 确保修改的方法签名与接口/父类匹配

```

|------|------|
| [Recipe | Android 应用网络流量分析](../Network/network_sniffing.md) - 详细的网络流量分析步骤 |
| [Recipe | 绕过应用对 Frida 的检测](../Anti-Detection/frida_anti_debugging.md) - 反调试绕过 |
| [Recipe | 脱壳和分析加固的 Android 应用](../Unpacking/un-packing.md) - 处理加壳应用 |
| [Recipe | Frida 常用脚本速查](../Scripts/frida_common_scripts.md) - 现成的脚本模板 |

## # 工具深入

- [Frida 使用指南](../../02-Tools/Dynamic/frida_guide.md) - 完整的 Frida 使用手册
- [Ghidra 使用指南](../../02-Tools/Static/ghidra_guide.md) - Native 代码分析
- [IDA Pro 使用指南](../../02-Tools/Static/ida_pro_guide.md) - 专业逆向工程工具

## # 案例研究

- [案例：音乐应用分析](../../03-Case-Studies/case_music_apps.md) - 完整工作流程实践
- [案例：应用加密分析](../../03-Case-Studies/case_study_app_encryption.md)

## # 参考资料

- [APK 文件结构详解](../../04-Reference/Foundations/apk_structure.md)
- [Smali 语法参考](../../04-Reference/Foundations/smali_syntax.md)
- [Android 组件详解](../../04-Reference/Foundations/android_components.md)

---

## 速查手册

## # 工作流程快速地图

```
解包 APK 分析 Manifest 查看目录
│ │ │
└──────────────┼──────────────┘
↓
确定分析方向
↓
┌──────────────┼──────────────┐
↓ ↓
静态分析 动态分析
(Jadx/IDA) (Frida)
│ │
├─ 定位关键代码 │
├─ 理解算法逻辑 │
└─ 确定 hook 点 ──────────────┤
│
┌───────┼───────┐
↓ ↓
Hook 验证 绕过保护
│ │
└───────┬───────┘
↓
提取关键数据
(密钥/算法)
↓
修改 Smali
↓
重打包 & 签名
↓
测试 & 验证

```

| **解包** | Apktool | `apktool d app.apk -o unpacked` |
| **反编译** | Jadx | `jadx-gui app.apk` |
| **Native 分析** | IDA/Ghidra | 直接打开 `.so` 文件 |
| **动态分析** | Frida | `frida -U -f <pkg> -l script.js --no-pause` |
| **重打包** | Apktool | `apktool b unpacked -o modified.apk` |
| **签名** | apksigner | `apksigner sign --ks key.keystore --out signed.apk modified.apk` |
| **安装** | ADB | `adb install signed.apk` |

## # ⚡ 常用快捷操作

```bash
# 1. 一键提取 APK 脚本（保存为 get-apk.sh）
# !/bin/bash
PKG=$1
PATH=$(adb shell pm path $PKG | cut -d: -f2 | tr -d '\r')
adb pull $PATH ./$PKG.apk
echo "[+] 已保存: $PKG.apk"

# 使用：./get-apk.sh com.example.app

# 2. 一键解包 + 反编译
apktool d app.apk && jadx-gui app.apk &

# 3. 快速查看 Manifest
apktool d -s app.apk -o temp && cat temp/AndroidManifest.xml

# 4. 自动签名脚本（保存为 sign-apk.sh）
# !/bin/bash
APK=$1
java -jar uber-apk-signer.jar --apks $APK
echo "[+] 签名 APK 已创建"

# 5. Frida 快速 hook（交互模式）
frida -U com.example.app
# 进入后执行:
# Java.perform(function() {
# var cls = Java.use("com.example.Class");
# cls.method.implementation = function() { return true; };
# });

```

│ └─ 有 → 直接阅读代码 → 动态验证
│ └─ 无 → 继续
│
├─ 是否加壳?
│ └─ 是 → 先脱壳（参见脱壳 Recipe）
│ └─ 否 → 继续
│
├─ 是否混淆?
│ └─ 重度混淆 → 优先动态分析（Frida）
│ └─ 轻度/无 → 优先静态分析（Jadx）
│
├─ Native 代码多?
│ └─ 是 → 用 IDA/Ghidra 分析 .so
│ └─ 否 → 专注 Java 层
│
└─ 有反调试?
└─ 是 → 先绕过检测
└─ 否 → 直接 hook

```

```

<!-- 01-Recipes/Analysis/static_analysis_deep_dive.md -->

# Recipe: 使用静态分析定位 android App 的关键逻辑

## 问题场景

**你遇到了什么问题？**

- 你想找到 App 的加密/签名算法，但代码太多不知道从哪里开始
- 🧩 你想理解 App 的完整业务逻辑，包括所有分支和边界条件
- 🐛 你想寻找安全漏洞，比如硬编码密钥、逻辑缺陷
- 你想在没有运行环境的情况下分析 APK
- 你想进行批量自动化分析

**本配方教你**：系统性地使用静态分析工具（jadx, IDA Pro, Ghidra）快速定位关键代码、追踪数据流、识别加密算法。

**核心理念**：

> 💡 **静态分析：不运行代码，看清全局**
>
> - 静态分析能看到所有代码路径（包括未触发的分支）
> - 适合理解完整算法和寻找漏洞
> - 先动态获取线索，再静态深入分析
> - 交替迭代：动态发现 → 静态验证 → 动态测试

**预计用时**: 40-90 分钟

---

## 工具清单

## # 必需工具

- - **jadx-gui** - Java/Smali 反编译
- - **IDA Pro / Ghidra** - Native 层分析
- - **文本编辑器** - 记录分析笔记

## # 可选工具

- - **Binary Ninja** - 可视化 CFG
- - **FindCrypt** (IDA 插件) - 识别加密算法
- - **YARA** - 模式匹配
- - **angr** - 符号执行（高级）

---

## 前置条件

## # ✅ 确认清单

```bash
# 1. jadx-gui 已安装
jadx-gui --version

# 2. IDA Pro or Ghidra 可用
# IDA Pro: 商业软件
# Ghidra: 免费，下载自 https://ghidra-sre.org/

# 3. APK 文件已解压
unzip app.apk -d app_unzipped

```

## # 🤔 静态 vs 动态：何时选择什么？

| 你的目标                       | 推荐起点 | 理由                               |
| ------------------------------ | -------- | ---------------------------------- |
| **快速提取结果**（如加密参数） | 动态优先 | 直接 Hook 拿结果，不必理解全部逻辑 |
| **理解完整算法**（如协议逆向） | 静态优先 | 需要看清所有分支和边界条件         |
| **寻找漏洞**                   | 静态优先 | 需要覆盖所有代码路径，包括错误处理 |
| **对抗混淆/加壳**              | 动态优先 | 静态分析可能完全失效，先动态脱壳   |
| **批量自动化**                 | 静态优先 | 动态分析需要运行环境，静态可离线   |

**最佳实践**：

1. **先动态获取线索** - 用 Frida 快速定位关键函数
2. **再静态深入分析** - 有了"地图"后更有方向性
3. **交替迭代** - 动态发现的疑点用静态验证

---

## 解决方案

## # 第 1 步：确定分析目标（5 分钟）

**明确你想找什么**：

- - API 签名算法
- - 加密密钥位置
- - 网络协议逻辑
- - 特定功能实现（如登录、支付）
- - 安全漏洞

**示例**：假设目标是找到 API 请求的签名逻辑

---

## # 第 2 步：从字符串入手（10 分钟）

**最有效的起点**：搜索关键字符串

## # # 2.1 jadx-gui 字符串搜索

```
md5
sha
hmac
key
secret
encrypt

```

HashMap<String, String> params = new HashMap<>();
params.put("sign", generateSign(data));

```

```

1. 右键点击 `generateSign` 函数
2. 选择 **"Find Usage"** 或按 `X`
3. 查看所有调用点

**在 IDA Pro 中**：

1. 光标移到函数名
2. 按 `X` 键
3. 查看 **Xrefs to**（被谁调用）和 **Xrefs from**（调用了谁）

## # # 3.2 向上追溯调用链

```
RequestBuilder.buildParams()
↓
SignUtils.generateSign() ← 目标函数

```

// Step 1: Sort parameters
TreeMap<String, String> sortedParams = new TreeMap<>(params);

// Step 2: Concatenate string
StringBuilder sb = new StringBuilder();
for (Map.Entry<String, String> entry : sortedParams.entrySet()) {
sb.append(entry.getKey()).append("=").append(entry.getValue()).append("&");
}
sb.append("key=").append(SECRET_KEY);

// Step 3: Calculate MD5
return MD5.encode(sb.toString());

}

````
___
## # 第 4 步：数据流分析（15 分钟）

* *目标**：追踪 `SECRET_KEY` 的来源

## # # 4.1 查找变量定义

* *在 jadx 中**：

1. 点击 `SECRET_KEY`
2. Ctrl+Click 跳转到定义


* *可能的情况**：

<details>
<summary><b>情况 1: 硬编码（最简单）</b></summary>

```java
private static final String SECRET_KEY = "abc123def456";

````

<summary><b>情况 2: 从配置文件读取</b></summary>

```java
static {
try {
Properties props = new Properties();
props.load(context.getAssets().open("config.properties"));
SECRET_KEY = props.getProperty("api.secret");
} catch (IOException e) {
SECRET_KEY = null;
}
}

```

cat app_unzipped/assets/config.properties

````

```java
static {
System.loadLibrary("native-lib");
SECRET_KEY = getKeyFromNative();
}

private static native String getKeyFromNative();

````

在 Ghidra 反编译窗口：

1. 双击变量名
2. 所有使用该变量的地方会高亮显示
3. 追踪变量在函数内的流动

---

## # 第 5 步：Native 层分析（20 分钟）

如果关键逻辑在 SO 文件中。

## # # 5.1 定位 Native 函数

**在 jadx 中找到 JNI 声明**：

```java
public native String encrypt(String plaintext);

```

ls app_unzipped/lib/arm64-v8a/

# libnative-lib.so

# 用 IDA Pro 打开

````
3. 双击跳转到函数


* *或使用 Exports 窗口**：

1. **View → Open Subviews → Exports**
2. 搜索函数名
3. 双击跳转


## # # 5.3 分析函数逻辑

* *示例反编译代码**（IDA/Ghidra）：

```c
jstring Java_com_example_CryptoUtils_encrypt(JNIEnv *env, jobject obj, jstring plaintext) {
const char *plain = (*env)->GetStringUTFChars(env, plaintext, 0);

// AES encryption
unsigned char key[16] = {0x12, 0x34, 0x56, 0x78, ...};
unsigned char iv[16] = {0x00, 0x00, 0x00, 0x00, ...};

unsigned char *encrypted = aes_encrypt(plain, key, iv);

jstring result = (*env)->NewStringUTF(env, encrypted);
(*env)->ReleaseStringUTFChars(env, plaintext, plain);

return result;
}

````

- IV：`{0x00, 0x00, ...}`

---

## # 第 6 步：识别加密算法（10 分钟）

## # # 6.1 使用 FindCrypt 插件（IDA Pro）

**安装**：

```bash
# 下载
git clone https://github.com/polymorf/findcrypt-yara.git

# 复制到 IDA 插件目录
cp findcrypt3.py $IDA_PATH/plugins/

```

## # # 6.2 手动识别

**常见加密算法特征**：

| 算法    | 特征常量（十六进制）                   |
| ------- | -------------------------------------- |
| AES     | `63 7C 77 7B F2 6B 6F C5` (S-Box)      |
| MD5     | `67 45 23 01 EF CD AB 89` (初始化向量) |
| SHA-1   | `67 45 23 01 EF CD AB 89 98 BA DC FE`  |
| SHA-256 | `428A2F98 71374491 B5C0FBCF`           |
| DES     | 固定的 S-Box 和 P-Box 表               |

**在 IDA 中搜索**：

```

* *用途**：理解复杂函数的逻辑结构

## # 7.1 查看 CFG

* *IDA Pro**：

```

```
[检查密码长度] --No--> [返回错误 2]
↓ Yes
[加密密码]
↓
[发送网络请求]
↓
[解析响应] --Failed--> [返回错误 3]
↓ Success
[保存 Token]
↓
[返回成功]

```

**Xrefs to**（被谁调用）：

```

```

→ Base64.encode()

```
↓
params.put("user", username) ← 污点传播
↓
String signData = buildSignData(params)
↓
network.send(signData) ← 可能注入点

```

```
[A] [B][C][D] [E]
\ | | | /
\ | | | /
[Dispatcher]

```

---

## 常见问题

## # ❌ 问题 1: jadx 反编译失败

**症状**：打开 APK 后显示错误或代码不完整

**解决**：

1. **尝试不同版本的 jadx**

```bash
# 使用最新版
wget https://github.com/skylot/jadx/releases/download/v1.4.7/jadx-1.4.7.zip

```

````
- 禁用 "Deobfuscation"
- 禁用 "Inline methods"
    ```

3. **查看 Smali 代码**
    ```bash
# 使用 apktool
apktool d app.apk -o app_smali

````

**可能原因**：

1. **字符串被加密/混淆**

- 在运行时动态解密
- **解决**：用 Frida Hook 查看运行时字符串

- 在运行时动态解密
- **解决**：用 Frida Hook 查看运行时字符串

2. **字符串在 Native 层**

```bash
# 在 SO 文件中搜索
strings libnative-lib.so | grep "sign"

```

    ```java

// Code might be
String key = "sec" + "ret" + "key";

```

**症状**：打开 SO 文件后只看到数据，没有函数

**解决**：

1. **手动创建函数**

```

- 按 'P' 键创建函数
- 按 'C' 键转换为代码

  ```

  ```

2. **使用自动分析**

```
勾选 "Create Functions" "Analyze Code"

```

- OLLVM 控制流平坦化
- 参考：[OLLVM 反混淆](./ollvm_deobfuscation.md)

- OLLVM 控制流平坦化
- 参考：[OLLVM 反混淆](./ollvm_deobfuscation.md)

## # ❌ 问题 4: 代码太复杂看不懂

**策略**：

1. **重命名变量和函数**

```
Ghidra: 右键 → Rename

```

```java
// Original
String a = b(c, d);

// After renaming
String encryptedData = encrypt(plaintext, key);

```

```
Ghidra: 右键 → Set Comment

```

- 一次只分析一个功能
- 画流程图记录逻辑

- 一次只分析一个功能
- 画流程图记录逻辑

## # ❌ 问题 5: 如何验证静态分析结果？

**方法 1：使用 CyberChef**

访问 https://gchq.github.io/CyberChef/

```
def generate_sign(params, secret_key):
# 从静态分析复制的逻辑
sorted_params = sorted(params.items())
sign_str = '&'.join([f'{k}={v}' for k, v in sorted_params])
sign_str += f'&key={secret_key}'
return hashlib.md5(sign_str.encode()).hexdigest()

# 测试
params = {'user': 'test', 'timestamp': '1234567890'}
secret = 'abc123'
print(generate_sign(params, secret))

```

var SignUtils = Java.use('com.example.SignUtils');
var HashMap = Java.use('java.util.HashMap');

var params = HashMap.$new();
params.put('user', 'test');
params.put('timestamp', '1234567890');

var sign = SignUtils.generateSign(params);
console.log('[*] 签名结果:', sign);

});

```
- **[逆向工程工作流](./re_workflow.md)** - 完整的分析流程
- **[密码学分析](../Network/crypto_analysis.md)** - 加密算法识别
- **[OLLVM 反混淆](./ollvm_deobfuscation.md)** - 处理混淆代码


## # 工具深入

- **[IDA Pro 使用指南](../../02-Tools/Static/ida_pro_guide.md)**
- **[Ghidra 使用指南](../../02-Tools/Static/ghidra_guide.md)**
- **[jadx 使用技巧](../../02-Tools/Static/)** - TODO


## # 在线资源


| 项目 | 说明 |
|------|------|
| **IDA Pro 教程** - https | //www.hex-rays.com/products/ida/support/tutorials/ |
| **Ghidra 官方手册** - https | //ghidra-sre.org/docs/ |
| **FindCrypt 插件** - https | //github.com/polymorf/findcrypt-yara |


## # 理论基础

- **[ARM 汇编基础](../../04-Reference/Foundations/arm_assembly.md)**
- **[DEX 文件格式](../../04-Reference/Foundations/dex_format.md)**
- **[ELF 文件格式](../../04-Reference/Foundations/so_elf_format.md)**
___
## 快速参考

## # jadx 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+Shift+F` | 全局搜索 |
| `Ctrl+F` | 当前文件搜索 |
| `X` | 查找用法（Xrefs） |
| `Ctrl+Click` | 跳转到定义 |
| `Alt+←` | 后退 |
| `F5` | 重新反编译 |

## # IDA Pro 快捷键

| 快捷键 | 功能 |
|--------|------|
| `X` | 交叉引用 |
| `N` | 重命名 |
| `;` | 添加注释 |
| `Space` | 切换图形/文本视图 |
| `G` | 跳转到地址 |
| `P` | 创建函数 |
| `C` | 转换为代码 |
| `A` | 转换为字符串 |
| `Shift+F12` | 查看字符串 |
| `Alt+T` | 文本搜索 |
| `Alt+B` | 二进制搜索 |

## # 分析流程模板

```

---

↓

---

↓

---

---

↓

---

↓

---

5. 关键变量:

- 名称: **\*\*\*\***\_\_\_**\*\*\*\***
- 类型: **\*\*\*\***\_\_\_**\*\*\*\***
- 来源: **\*\*\*\***\_\_\_**\*\*\*\***
- 名称: **\*\*\*\***\_\_\_**\*\*\*\***
- 类型: **\*\*\*\***\_\_\_**\*\*\*\***
- 来源: **\*\*\*\***\_\_\_**\*\*\*\***

6. 算法识别: **\*\*\*\***\_\_\_**\*\*\*\***
7. 验证结果: **\*\*\*\***\_\_\_**\*\*\*\***
8. 下一步: **\*\*\*\***\_\_\_**\*\*\*\***

   ```

   ```

---

- 成功定位关键逻辑了吗？\*\* 现在你可以理解 App 的核心算法了！

下一步推荐：[动态分析深入](./dynamic_analysis_deep_dive.md)（验证和测试你的发现）

````



<!-- 01-Recipes/Analysis/vmp_analysis.md -->

# VMP 分析

VMP (VMProtect 的简称) 是一种非常强大的软件保护解决方案，它使用虚拟化（一个"虚拟机"）来保护代码。受保护的代码不再执行原生 CPU 指令，而是被转换成一种自定义的字节码，只有特定的、嵌入的虚拟机才能解释执行。

分析受 VMP 保护的代码是逆向工程中最具挑战性的任务之一。

___

## 核心概念

1. **虚拟机 (VM)**: VMP 的核心。它包括：
* **解释器循环**: 读取字节码并执行相应的处理程序 (handler)。
* **处理程序 (Handlers)**: 实现每个自定义字节码指令逻辑的小段原生代码（例如，虚拟加法、虚拟跳转）。
* **虚拟寄存器**: VM 使用自己的一套虚拟寄存器来存储数据，这些虚拟寄存器会映射到原生寄存器或内存位置。
* **VM 上下文**: 一个存储 VM 所有状态的结构，包括虚拟寄存器、标志位和虚拟指令指针 (VIP)。

2. **字节码**: 原始的原生代码被翻译成一个专为嵌入式 VM 设计的自定义、非标准的指令集。

3. **突变 (Mutation)**: 为了让分析更加困难，VMP 会为每个新版本的受保护软件突变 VM 的处理程序和字节码。这意味着一个"虚拟加法"指令的处理程序每次都会看起来不一样。

___

## 分析策略

直接对 VMP 进行去虚拟化极其困难，通常也不是主要目标。重点通常是理解某个特定受保护函数的逻辑。

### 1. 识别 VM 及其组件

* **入口点分析**: 第一步是定位"VM 入口"，即程序从执行原生代码切换到 VM 解释器循环的地方。其特征通常是一系列的 PUSH 指令，用以保存原生上下文，并最终通过一个 JMP/CALL 指令进入解释器。
* **处理程序追踪**: 一旦进入 VM，追踪执行流将揭示不同处理程序的地址。通过分析每个处理程序对 VM 上下文做了什么，就可以开始勾勒出虚拟指令集。例如，一个读取两个虚拟寄存器、将它们相加并存储结果的处理程序很可能就是"虚拟加法"。

### 2. 动态分析与追踪

* **指令追踪**: 这是最有效的方法。目标是构建一个正在执行的虚拟指令的追踪记录。这需要：
1. 在解释器循环的开始处（或每个处理程序上）设置断点。
2. 在每一步，转储虚拟机的状态（虚拟寄存器、VIP）。
3. 记录处理程序执行的原生操作。
* **Frida/DBI 工具**: 像 Frida、Pin 或 QBDI 这样的动态二进制插桩 (DBI) 框架至关重要。它们允许你编写追踪过程的脚本，在解释器的每一步自动记录 VM 状态。

### 3. 重建逻辑

* **语义重建**: 收集到虚拟指令的追踪记录后，就可以开始重建高层逻辑。例如，一个"加载"、"相加"、"存储"的虚拟指令序列可以被翻译回类似 C 的表达式 `var = a + b;`。
* **提升到更高级别的 IR**: 完整的去虚拟化工作的最终目标是将自定义字节码"提升"到一个标准的中间表示，如 LLVM IR 或 REIL。这让你能够使用标准的编译器。这是一个非常复杂的、研究级别的问题。

### 4. 关键要点

不要试图反编译 VM 本身。相反，**追踪 VM 的执行**来理解它在做什么。它所调用的处理程序的序列才是你需要分析的真正逻辑。



<!-- 01-Recipes/Anti-Detection/app_hardening_identification.md -->

# 主流应用加固厂商及其特征识别

Android 应用加固是一种保护 App 不被轻易逆向、篡改或攻击的技术手段。对于逆向工程师而言，在开始分析一个 App 之前，**首要任务就是识别出它所使用的加固厂商**，因为不同的加固方案需要不同的脱壳和分析策略。

本指南旨在系统性地总结中国市场主流加固厂商的静态特征"指纹"，帮助分析人员快速识别目标。

___

## 目录
1. [**通用识别思路**](#通用识别思路)
2. [**主流厂商特征详解**](#主流厂商特征详解)

* [梆梆安全 (Bangcle)](#梆梆安全-bangcle)

* [360 加固 (Qihoo 360)](#360-加固-qihoo-360)

* [腾讯乐固 (Tencent Legu)](#腾讯乐固-tencent-legu)

* [网易易盾 (Netease Yidun)](#网易易盾-netease-yidun)

* [爱加密 (Ijiami)](#爱加密-ijiami)
3. [**快速识别摘要表**](#快速识别摘要表)

___

## 通用识别思路

识别加固厂商通常遵循以下静态分析路径：
1. **检查 DEX 文件**：解压 APK，查看主 `classes.dex` 文件的大小。如果它非常小（通常小于 1MB），而 APK 本身体积很大，那么它很可能是一个"壳"，负责加载真正的、被加密隐藏起来的 DEX。
2. **检查 SO 库**：查看 `lib/[arch]/` 目录下的 `.so` 文件列表。加固厂商通常会放入带有自身品牌标识的 SO 库，这是最明显的特征。
3. **检查 `assets` 目录**：很多加固方案会将加密后的 DEX 文件、配置文件或其他组件放入 `assets` 目录。
4. **检查 `AndroidManifest.xml`**：加固方案通常会用自己的代理 `Application` 类替换掉原始的 `Application` 类。检查 `application` 标签下的 `android:name` 属性，可以找到代理类的名字，其包名往往暴露厂商信息。

## 主流厂商特征详解

### 梆梆安全 (Bangcle)
梆梆是最早期的加固厂商之一，特征相对明显。

* **SO 库特征**:
* `libSecShell.so`

* `libsecexe.so`

* `libsecmain.so`
* **Java 层特征**:
* 代理 Application 包名：`com.bangcle.protect` 或 `com.secshell.shell`。
* **`assets` 目录特征**:
* 可能会有 `bangcle_classes.jar` 或类似命名的加密 DEX 文件。
* **其他**:
* `AndroidManifest.xml` 的 `meta-data` 中可能会包含原始 Application 的信息。

### 360 加固 (Qihoo 360)
360 加固非常普遍，其特征也广为人知。

* **SO 库特征**:
* `libjiagu.so`

* `libprotectClass.so`

* `libjiagu_x86.so` / `libjiagu_art.so`
* **Java 层特征**:
* 代理 Application 包名：`com.qihoo.util`。

* 启动类中可能包含 `com.stub.StubApp`。
* **`assets` 目录特征**:
* `libjiagu.so` (是的，有时也会放在 assets 里)

* `.jiagu` 后缀的加密文件。

### 腾讯乐固 (Tencent Legu)
腾讯乐固通常与 Bugly SDK 一起出现，特征明显。

* **SO 库特征**:
* `liblegu.so`

* `libshella-xxxx.so` (xxxx 是版本号)
* **Java 层特征**:
* 代理 Application 包名：`com.tencent.bugly.legu`。
* **`assets` 目录特征**:
* `legu_data.so`

* `tosversion` 文件
* **其他**:
* DEX 文件头通常被修改为 `legu`。

### 网易易盾 (Netease Yidun)
网易易盾是近年来兴起的一款强大加固，特征也比较独特。

* **SO 库特征**:
* `libnesec.so` (最核心的特征)
* **Java 层特征**:
* 代理 Application 包名：`com.netease.nis.wrapper`。
* **`assets` 目录特征**:
* `nesec.dat`

* `classes.dex.ys` (加密的主 DEX)

* `xxx.dat` 格式的加密 DEX 文件。

### 爱加密 (Ijiami)
爱加密也是一款常见的加固产品。

* **SO 库特征**:
* `libexec.so`

* `libexecmain.so`

* `libijiami.so`
* **Java 层特征**:
* 代理 Application 包名：`com.ijiami.client.protect`。
* **`assets` 目录特征**:
* `ijiami.dat`

* `ijm_lib` 目录

___

## 快速识别摘要表

| 加固厂商 | 核心 SO 特征 | Java 包名/类名特征 | `assets` 目录特征 |
| :--- | :--- | :--- | :--- |
| **梆梆安全** | `libSecShell.so` | `com.bangcle.protect` | `bangcle_classes.jar` |
| **360 加固** | `libjiagu.so`, `libprotectClass.so` | `com.qihoo.util` | `.jiagu` 文件 |
| **腾讯乐固** | `liblegu.so` | `com.tencent.bugly.legu` | `legu_data.so` |
| **网易易盾** | `libnesec.so` | `com.netease.nis.wrapper`| `nesec.dat`, `classes.dex.ys`|
| **爱加密** | `libexec.so`, `libijiami.so` | `com.ijiami.client.protect` | `ijiami.dat` |


<!-- 01-Recipes/Anti-Detection/captcha_bypassing_techniques.md -->

# 验证码绕过技术：滑块与点选篇

滑块和点选（或称图标）验证码是现代 Web 应用中用于区分人类用户和自动化程序（机器人）的常见手段。与传统的字符输入验证码相比，它们更注重于分析用户的"行为特征"。本文旨在详细介绍绕过这两类验证码的主流技术和核心思想。

- --

## 目录
- [验证码绕过技术：滑块与点选篇](#验证码绕过技术滑块与点选篇)
- [目录](#目录)
- [验证码核心机制](#验证码核心机制)
- [滑块验证码](#滑块验证码)

- [点选验证码](#点选验证码)
- [绕过策略一：模拟人类行为](#绕过策略一模拟人类行为)
- [步骤 1: 目标识别 (计算机视觉)](#步骤-1-目标识别-计算机视觉)

- [步骤 2: 轨迹模拟 (核心关键)](#步骤-2-轨迹模拟-核心关键)
- [绕过策略二：机器学习与 AI](#绕过策略二机器学习与-ai)
- [目标检测模型 (YOLO/SSD)](#目标检测模型-yolossd)

- [第三方打码平台](#第三方打码平台)
- [绕过策略三：寻找逻辑漏洞](#绕过策略三寻找逻辑漏洞)

- [防御与对抗的演进](#防御与对抗的演进)

- --

### 验证码核心机制

#### 滑块验证码
* **目标**: 用户需要将滑块拖动到背景图的缺口位置。

* **验证重点**:
1. **结果准确性**: 滑块最终停留的位置是否在缺口的目标容差范围内。
2. **行为可信度**: **(更重要)** 用户的鼠标轨迹是否像人。一个由程序生成的、匀速的、完美的直线轨迹几乎肯定会被判定为机器人。

#### 点选验证码
* **目标**: 根据提示，按顺序点击图片中的一个或多个汉字、图标或物体。

* **验证重点**:
1. **识别准确性**: 是否能正确识别并点击目标。
2. **行为可信度**: 点击的坐标、间隔时间、鼠标移动轨迹是否自然。

- --

### 绕过策略一：模拟人类行为

这是最主流、最根本的绕过方法，其核心是尽可能地模仿人类操作的不完美性。

#### 步骤 1: 目标识别 (计算机视觉)

在模拟操作之前，程序需要先像人一样"看懂"验证码。

* **对于滑块验证码 (缺口识别)**:
* **常用库**: OpenCV (Python)。

* **方法一：边缘检测**:
1. 获取带缺口的背景图和不带缺口的完整背景图（通常可以从网络请求中找到）。
2. 使用 Canny 等边缘检测算法分别处理两张图片。
3. 对比两张图的边缘差异，差异最显著的区域就是缺口的位置。

* **方法二：模板匹配**:
1. 从网络请求或页面元素中获取到独立的"滑块"图片。
2. 将滑块图片作为"模板"，在带缺口的背景图上进行模板匹配 (`cv2.matchTemplate`)。匹配度最高的地方就是缺口的起始 X 坐标。

* **对于点选验证码 (目标识别)**:
* 如果目标是固定的文字或图标，可以采用与滑块类似的**模板匹配**方法。

* 如果目标是变化的、复杂的，例如"请点击图中所有的公交车"，则需要依赖更高级的机器学习模型（见策略二）。

#### 步骤 2: 轨迹模拟 (核心关键)

这是整个绕过过程的灵魂。一个好的轨迹模拟算法需要考虑以下几点，以欺骗服务器端的行为分析模型：

* **非线性移动**: 绝对不能是 `(x1, y1)` 到 `(x2, y2)` 的直线。路径需要是带有弧度的曲线。

* **变速移动**: 模拟人类操作的肌肉控制，轨迹应该是"慢-快-慢"的模式。
* **初段加速**: 初始移动速度较慢。

* **中段匀速/加速**: 中间过程速度加快。

* **末段减速**: 接近目标时，速度会显著减慢，进行微调。
* **随机抖动**: 在主轨迹的基础上，叠加微小的、随机的 Y 轴（有时也包括 X 轴）偏移，模拟手部自然的抖动。

* **超越与回退**: 有时可以模拟"拖过头了一点点，再往回拉"的行为，这会极大地增加轨迹的可信度。

* **停顿**: 在拖动过程中可以加入短暂的、随机时长的停顿。

* *实现示例 (伪代码)**:

```python
def generate_human_like_track(target_distance):
track = []
current_pos = 0
# Movement pattern: accelerate first, then decelerate
while current_pos < target_distance:
# 1. Calculate movement step size for current phase (non-uniform speed)
if current_pos < target_distance * 0.7:
step = random.uniform(2, 4) # Acceleration phase
else:
step = random.uniform(0.5, 2) # Deceleration and fine-tuning phase

# 2. Add random jitter
y_offset = random.uniform(-1, 1)

# 3. Record trajectory point
track.append((step, y_offset, random.uniform(10, 50))) # (x step, y offset, time interval ms)
current_pos += step

# (Optional) Add "overshoot and pull back" trajectory points
# ...
return track

````

- **适用场景**: 需要从一张大图中识别并定位多个不规则物体的点选验证码（例如，"选出所有的红绿灯"）。

- **方法**:

1. **数据标注**: 收集大量的验证码图片，并手动标注出需要识别的物体（如"红绿灯"、"公交车"）。
2. **模型训练**: 使用标注好的数据集训练一个目标检测模型，如 YOLOv5 或 SSD。
3. **推理**: 在实际绕过时，将验证码图片输入到训练好的模型中，模型会返回所有识别到的目标的位置坐标。
4. **后续操作**: 拿到坐标后，再结合上一节的"轨迹模拟"方法去点击。

#### 第三方打码平台

- **概念**: 将识别验证码这一专业任务外包给第三方服务。这些平台背后通常是大量的人工或者更强大的 AI 模型。

- **代表服务**: 2Captcha, Anti-Captcha 等。

- **工作流程**:

1. 注册并充值。
2. 通过 API 将验证码图片（或任务描述）发送给平台。
3. 平台返回结果（如滑块的 X 坐标，或点选目标的坐标序列）。
4. 你的程序拿到结果后，再执行后续的模拟操作。

- **优点**: 成功率极高，能解决几乎所有类型的验证码，无需自己维护复杂的识别模型。

- **缺点**: 需要付费，存在隐私和安全风险（将数据发给第三方），有网络延迟。

---

### 绕过策略三：寻找逻辑漏洞

在投入大量精力编写复杂的模拟和识别代码前，先尝试寻找"捷径"是一种高性价比的策略。

- **分析前端 JS**: 仔细审查页面的 JavaScript 文件，特别是与验证码相关的逻辑。有时可能会发现：
- **答案硬编码或弱加密**: 缺口位置、目标坐标等信息以明文或简单加密的方式存在于前端代码中。

- **可预测的随机数**: 用于生成验证码的随机种子或算法过于简单，可以被预测。
- **API 漏洞**:
- **验证绕过**: 尝试直接调用提交表单的 API，但不带验证码相关的参数，看后端是否强制校验。

- **Token 重放**: 成功通过一次验证后，获取到的 `session_token` 或 `captcha_id` 是否可以被多次重用。

---

### 防御与对抗的演进

验证码提供商也在不断进化，以对抗上述绕过技术：

- **环境检测**: 检测 WebDriver 特征（如 `navigator.webdriver` 标志）、浏览器指纹、字体、分辨率等。

- **更复杂的行为分析**: 不仅仅是轨迹，还会分析点击压力、滚轮行为、鼠标加速度等更深层次的生物特征。

- **图像干扰**: 在验证码图片上增加干扰线、噪点、形变、颜色抖动，增加 CV 识别难度。

- **无感验证 (reCAPTCHA v3)**: 完全在后台根据用户的综合行为评分，分数过低时才弹出挑战。

<!-- 01-Recipes/Anti-Detection/device_fingerprinting_and_bypass.md -->

# 设备指纹技术深度解析与绕过策略

- **设备指纹 (Device Fingerprinting)\*\*** 是指通过采集设备的软硬件特征，生成一个能够唯一标识该设备的、具有高熵值和稳定性的 ID 的过程。在当今的互联网服务中，它已成为反欺诈、反机器人、用户行为追踪和安全风控的基石技术。

绕过设备指纹并非简单地修改一两个参数，而是要创造一个完整的、逻辑自洽的、可信的虚拟设备"画像"。本指南将系统性地拆解主流的指纹采集维度，并探讨与之对应的核心绕过技术。

---

## 目录

- [设备指纹技术深度解析与绕过策略](#设备指纹技术深度解析与绕过策略)
- [目录](#目录)
- [设备指纹的工作原理](#设备指纹的工作原理)
- [指纹生成算法](#指纹生成算法)
- [熵值与稳定性](#熵值与稳定性)
- [指纹更新策略](#指纹更新策略)
- [主流设备指纹采集维度](#主流设备指纹采集维度)
- [硬件层标识符](#硬件层标识符)
- [系统与软件特征](#系统与软件特征)
- [硬件特性指纹](#硬件特性指纹)
- [通过 SVC (系统调用) 获取信息](#通过-svc-系统调用-获取信息)
- [网络环境指纹](#网络环境指纹)
- [行为特征指纹](#行为特征指纹)
- [核心绕过技术与策略](#核心绕过技术与策略)
- [Hook 技术 (Frida/Xposed)](#hook-技术-fridaxposed)
- [深度设备修改 ("改机")](#深度设备修改-改机)
- [环境虚拟化与容器技术](#环境虚拟化与容器技术)
- [云手机技术详解](#云手机技术详解)
- [构建一致性的"设备画像"](#构建一致性的设备画像)
- [商业化产品与服务](#商业化产品与服务)
- [国内主流设备指纹服务商](#国内主流设备指纹服务商)
- [国际知名产品](#国际知名产品)
- [开源工具与框架](#开源工具与框架)
- [设备指纹采集框架](#设备指纹采集框架)
- [反指纹工具](#反指纹工具)
- [对抗与挑战](#对抗与挑战)
- [Hook 框架检测](#hook-框架检测)
- [服务端交叉验证](#服务端交叉验证)
- [机器学习检测](#机器学习检测)
- [实战案例分析](#实战案例分析)
- [案例 1：某电商平台设备指纹分析](#案例1某电商平台设备指纹分析)
- [案例 2：金融 App 风控绕过](#案例2金融app风控绕过)

- [目录](#目录)
- [设备指纹的工作原理](#设备指纹的工作原理)
- [指纹生成算法](#指纹生成算法)
- [熵值与稳定性](#熵值与稳定性)
- [指纹更新策略](#指纹更新策略)
- [指纹生成算法](#指纹生成算法)
- [熵值与稳定性](#熵值与稳定性)
- [指纹更新策略](#指纹更新策略)
- [主流设备指纹采集维度](#主流设备指纹采集维度)
- [硬件层标识符](#硬件层标识符)
- [系统与软件特征](#系统与软件特征)
- [硬件特性指纹](#硬件特性指纹)
- [通过 SVC (系统调用) 获取信息](#通过-svc-系统调用-获取信息)
- [网络环境指纹](#网络环境指纹)
- [行为特征指纹](#行为特征指纹)
- [硬件层标识符](#硬件层标识符)
- [系统与软件特征](#系统与软件特征)
- [硬件特性指纹](#硬件特性指纹)
- [通过 SVC (系统调用) 获取信息](#通过-svc-系统调用-获取信息)
- [网络环境指纹](#网络环境指纹)
- [行为特征指纹](#行为特征指纹)
- [核心绕过技术与策略](#核心绕过技术与策略)
- [Hook 技术 (Frida/Xposed)](#hook-技术-fridaxposed)
- [深度设备修改 ("改机")](#深度设备修改-改机)
- [环境虚拟化与容器技术](#环境虚拟化与容器技术)
- [云手机技术详解](#云手机技术详解)
- [构建一致性的"设备画像"](#构建一致性的设备画像)
- [Hook 技术 (Frida/Xposed)](#hook-技术-fridaxposed)
- [深度设备修改 ("改机")](#深度设备修改-改机)
- [环境虚拟化与容器技术](#环境虚拟化与容器技术)
- [云手机技术详解](#云手机技术详解)
- [构建一致性的"设备画像"](#构建一致性的设备画像)
- [商业化产品与服务](#商业化产品与服务)
- [国内主流设备指纹服务商](#国内主流设备指纹服务商)
- [国际知名产品](#国际知名产品)
- [国内主流设备指纹服务商](#国内主流设备指纹服务商)
- [国际知名产品](#国际知名产品)
- [开源工具与框架](#开源工具与框架)
- [设备指纹采集框架](#设备指纹采集框架)
- [反指纹工具](#反指纹工具)
- [设备指纹采集框架](#设备指纹采集框架)
- [反指纹工具](#反指纹工具)
- [对抗与挑战](#对抗与挑战)
- [Hook 框架检测](#hook-框架检测)
- [服务端交叉验证](#服务端交叉验证)
- [机器学习检测](#机器学习检测)
- [Hook 框架检测](#hook-框架检测)
- [服务端交叉验证](#服务端交叉验证)
- [机器学习检测](#机器学习检测)
- [实战案例分析](#实战案例分析)
- [案例 1：某电商平台设备指纹分析](#案例1某电商平台设备指纹分析)
- [案例 2：金融 App 风控绕过](#案例2金融app风控绕过)

- [案例 1：某电商平台设备指纹分析](#案例1某电商平台设备指纹分析)
- [案例 2：金融 App 风控绕过](#案例2金融app风控绕过)

---

## 设备指纹的工作原理

### 指纹生成算法

设备指纹的生成并非简单地将所有采集到的信息拼接在一起，而是通过复杂的算法处理，确保生成的指纹具有唯一性、稳定性和不可逆性。

#### 基本流程

```
对采集到的原始数据进行预处理：
- **格式统一**: 将不同格式的数据转换为标准格式（如MAC地址统一为小写、去除分隔符）
- **缺失值处理**: 对无法获取的字段使用默认值或特殊标记
- **权重分配**: 根据稳定性和唯一性给不同维度分配权重


**3. 特征组合**
将处理后的数据按照预定规则组合：
```

```python
# 概念代码
fingerprint_input = {
'hardware': {
'android_id': 'abc123',
'imei': '867530900000000',
'mac': '00:11:22:33:44:55'
},
'software': {
'model': 'Pixel 6',
'sdk': 33,
'fingerprint': 'google/raven/raven:...'
},
'environment': {
'screen': '1080x2400',
'dpi': 420,
'timezone': 'Asia/Shanghai'
}
}

```

import hashlib
import json

def generate_fingerprint(data):

# WillData 转为 JSONString（确保顺序一致）

json_str = json.dumps(data, sort_keys=True)

# CalculateSHA256

fingerprint = hashlib.sha256(json_str.encode()).hexdigest()

return fingerprint

````

| 算法 | 输出长度 | 特点 | 适用场景 |
|------|----------|------|----------|
| MD5 | 128位 | 速度快，但安全性低 | 低安全要求场景 |
| SHA-256 | 256位 | 安全性高，计算稍慢 | 金融、高安全场景 |
| MurmurHash | 可变 | 速度极快，适合非加密 | 大规模数据处理 |
| xxHash | 可变 | 性能优异 | 实时计算场景 |

#### 高级技术

* *1. 模糊Hash (Fuzzy Hashing)**
允许设备指纹在细微变化时仍能匹配。使用 SimHash、MinHash 等算法：

```python
# SimHash 概念Implement
def simhash(features, hash_bits=64):
"""
将特征向量转换为 SimHash 值
相似特征会产生相似HashValue
"""
v = [0] * hash_bits

for feature, weight in features.items():
h = hash(feature)
for i in range(hash_bits):
if h & (1 << i):
v[i] += weight
else:
v[i] -= weight

fingerprint = 0
for i in range(hash_bits):
if v[i] >= 0:
fingerprint |= (1 << i)

return fingerprint

````

- **三级指纹（环境指纹）**: 基于网络、行为等临时特征

```python
def generate_tiered_fingerprint(data):
# 一级指纹：硬件ID
tier1 = hashlib.sha256(
f"{data['imei']}|{data['android_id']}".encode()
).hexdigest()

# 二级指纹：系统特征
tier2 = hashlib.sha256(
f"{tier1}|{data['model']}|{data['sdk']}".encode()
).hexdigest()

# 三级指纹：Complete特征
tier3 = hashlib.sha256(
json.dumps(data, sort_keys=True).encode()
).hexdigest()

return {
'strong': tier1,
'medium': tier2,
'weak': tier3
}

```

- 使用 PCA（主成分分析）提取关键特征
- 使用聚类算法识别异常设备
- 使用深度学习模型生成设备嵌入向量（Embedding）

### 熵值与稳定性

好的设备指纹需要在**唯一性（高熵值）**和**稳定性**之间找到平衡。

#### 熵值计算

熵值衡量一个特征的信息量和区分能力：

```python
import math
from collections import Counter

def calculate_entropy(values):
"""
Calculate一特征香农熵
熵值越高，说明该特征区分能力越强
"""
total = len(values)
counter = Counter(values)

entropy = 0
for count in counter.values():
p = count / total
entropy -= p * math.log2(p)

return entropy

# Example
android_ids = ['id1', 'id2', 'id3', ...] # 采集数据
entropy = calculate_entropy(android_ids)
print(f"Android ID熵Value: {entropy} bits")

```

| Android ID | 60+ bits | 高 | 中（恢复出厂会变） |
| MAC 地址 | 48 bits | 高 | 中（越来越难获取） |
| 设备型号 | 8-10 bits | 低 | 高 |
| 屏幕分辨率 | 6-8 bits | 低 | 高 |
| 传感器列表 | 15-20 bits | 中 | 高 |

#### 稳定性评估

稳定性指的是设备在不同时间点、不同环境下生成的指纹一致性：

```python
def stability_score(fingerprints):
"""
评估同一设备在不同时间生成的指纹Stable性
fingerprints: 同一设备多次生成的指纹列表
"""
if len(fingerprints) < 2:
return 1.0

# 计算指纹之间相似度
base = fingerprints[0]
similarities = []

for fp in fingerprints[1:]:
# Hamming 距离
diff = sum(c1 != c2 for c1, c2 in zip(base, fp))
similarity = 1 - (diff / len(base))
similarities.append(similarity)

return sum(similarities) / len(similarities)

```

"""
计算指纹方案质量分数
entropy: 熵 Value (0-100)
stability: Stable 性 (0-1)
coverage: 设备覆盖率 (0-1)
"""

# 加权计算

score = (
entropy _ 0.4 + # 唯一性权重 40%
stability _ 50 _ 0.4 + # 稳定性权重 40%
coverage _ 100 \*\* 0.2 # 覆盖率权重 20%
)
return score

````
- 设备硬件变更（换SIM卡、重置设备）
- App版本升级（指纹算法更新）
- 定期刷新（如每30天）


**2. 被动更新**
- 检测到指纹冲突（多个设备具有相同指纹）
- 检测到异常行为（疑似改机）
- 服务端要求强制更新


#### 更新策略

```python
class FingerprintManager:
def should_update(self, old_fp, new_data):
"""
CheckisNoNeedUpdate指纹
"""
# 计算新指纹
new_fp = self.generate_fingerprint(new_data)

# 1. 关KeyField变更
critical_changed = self._check_critical_fields(old_fp, new_data)
if critical_changed:
return True, "Critical field changed"

# 2. 相似度过低
similarity = self._calculate_similarity(old_fp, new_fp)
if similarity < 0.7:
return True, "Low similarity"

# 3. Time过期
if self._is_expired(old_fp):
return True, "Expired"

return False, "No update needed"

def update_fingerprint(self, device_id, new_fp, reason):
"""
更新指纹时保留历史记录
"""
history = {
'device_id': device_id,
'old_fingerprint': self.current_fp,
'new_fingerprint': new_fp,
'update_reason': reason,
'timestamp': time.time()
}
self._save_history(history)
self.current_fp = new_fp

````

```python
"""
Process指纹漂移
baseline_fp: 基线指纹
current_fp: Current指纹
threshold: 相似度阈Value
"""
similarity = calculate_similarity(baseline_fp, current_fp)

if similarity >= threshold:
# 可接受漂移，视为同一设备
return "same_device"
elif similarity >= 0.6:
# 异常漂移，需要二次验证
return "verification_needed"
else:
# 重大变化，疑似新设备or改机
return "new_device"

```

这些是传统的、权限较高的设备 ID。

| 标识符         | 获取方式 (Java API)                                 | 特点                                                                     |
| :------------- | :-------------------------------------------------- | :----------------------------------------------------------------------- |
| **Android ID** | `Settings.Secure.getString(resolver, "android_id")` | Android 8.0 以上，对每个 App 和用户都不同。恢复出厂设置会改变。          |
| **IMEI/MEID**  | `TelephonyManager.getImei()`                        | 手机的唯一身份码。需要 `READ_PHONE_STATE` 权限，且越来越难获取。         |
| **IMSI**       | `TelephonyManager.getSubscriberId()`                | SIM 卡的唯一身份码。同样需要高权限。                                     |
| **MAC 地址**   | `WifiInfo.getMacAddress()`                          | Android 6.0 以后，App 获取到的通常是一个固定的假值 `02:00:00:00:00:00`。 |

### 系统与软件特征

这是指纹库的主体，信息量大，获取成本低。

- **Build 属性**: 通过 `android.os.Build` 类或直接读取 `/system/build.prop` 文件获取。
- `Build.MODEL`: 设备型号 (e.g., "Pixel 6")

- `Build.BRAND`: 品牌 (e.g., "Google")

- `Build.MANUFACTURER`: 制造商 (e.g., "Google")

- `Build.VERSION.SDK_INT`: SDK 版本号 (e.g., 33)

- `Build.FINGERPRINT`: 系统构建指纹，信息量巨大。
- `Build.MODEL`: 设备型号 (e.g., "Pixel 6")

- `Build.BRAND`: 品牌 (e.g., "Google")

- `Build.MANUFACTURER`: 制造商 (e.g., "Google")

- `Build.VERSION.SDK_INT`: SDK 版本号 (e.g., 33)

- `Build.FINGERPRINT`: 系统构建指纹，信息量巨大。
- **系统设置**:
- 屏幕分辨率、DPI (`DisplayMetrics`)

- 系统语言、时区、默认字体列表。
- 屏幕分辨率、DPI (`DisplayMetrics`)

- 系统语言、时区、默认字体列表。
- **软件环境**:
- 已安装应用列表 (`PackageManager.getInstalledPackages`)。

- 特定 App (如输入法) 的版本。

- 已安装应用列表 (`PackageManager.getInstalledPackages`)。

- 特定 App (如输入法) 的版本。

### 硬件特性指纹

利用硬件的细微物理差异来创建指纹。

- **传感器数据**: 读取加速度计、陀螺仪等传感器的校准数据或在特定操作下的读数。不同批次的传感器存在物理差异。

- **CPU/GPU 信息**:
- 读取 `/proc/cpuinfo` 获取 CPU 型号、核心数、特性等。

- 通过 OpenGL/WebGL API 查询 GPU 供应商、渲染器信息，甚至可以执行一个标准渲染任务，将渲染结果的 Hash 作为指纹。
- 读取 `/proc/cpuinfo` 获取 CPU 型号、核心数、特性等。

- 通过 OpenGL/WebGL API 查询 GPU 供应商、渲染器信息，甚至可以执行一个标准渲染任务，将渲染结果的 Hash 作为指纹。
- **摄像头参数**: `CameraCharacteristics` 中包含的详细参数。

### 通过 SVC (系统调用) 获取信息

这是一种高级的反 Hook 技术，常见于加固方案中。其核心思想是**绕过所有上层 API 和 libc 函数**，通过 `SVC` 指令直接发起系统调用 (`syscall`) 来获取信息或执行操作。

- **原理**: `SVC` 是 ARM 处理器的一条指令，它会触发一个软件中断，使 CPU 从用户态（User Mode）切换到管理态（Supervisor Mode），从而执行内核代码。这是所有系统调用的基础。加固厂商在 SO 文件中直接嵌入 `SVC` 指令，可以不经过 `libc.so` 中的 `read`, `open`, `ioctl` 等函数，直接调用内核中对应的功能。

- **应用场景**:
- **绕过 API Hook**: 这是其最主要的目的。由于 Frida、Xposed 等框架主要 Hook 的是 App 进程空间中的函数（Java API 或 Native API），`SVC` 指令直接与内核交互，使得这些上层 Hook 完全失效。

- **读取敏感文件**: 直接使用 `open`/`read` 的系统调用号来读取 `/proc/self/maps`, `/proc/cpuinfo` 等文件，以检测环境或收集指纹。

- **执行反调试**: 使用 `ptrace` 的系统调用号来执行反调试检查。
- **绕过 API Hook**: 这是其最主要的目的。由于 Frida、Xposed 等框架主要 Hook 的是 App 进程空间中的函数（Java API 或 Native API），`SVC` 指令直接与内核交互，使得这些上层 Hook 完全失效。

- **读取敏感文件**: 直接使用 `open`/`read` 的系统调用号来读取 `/proc/self/maps`, `/proc/cpuinfo` 等文件，以检测环境或收集指纹。

- **执行反调试**: 使用 `ptrace` 的系统调用号来执行反调试检查。
- **分析与识别**:
- **静态分析**: 在 IDA 等反汇编工具中，直接搜索 `SVC` 指令。如果一个 SO 文件中含有大量 `SVC` 指令，且其上下文逻辑复杂，则极有可能使用了该技术。

- **动态分析**: Hook 系统调用需要更底层的工具。Frida 的 `Stalker` 可以用来跟踪指令级的执行流程，从而捕捉到 `SVC` 的调用。在某些情况下，也可以通过 Hook `libc.so` 中与 `syscall` 相关的底层函数来尝试捕获。

- **静态分析**: 在 IDA 等反汇编工具中，直接搜索 `SVC` 指令。如果一个 SO 文件中含有大量 `SVC` 指令，且其上下文逻辑复杂，则极有可能使用了该技术。

- **动态分析**: Hook 系统调用需要更底层的工具。Frida 的 `Stalker` 可以用来跟踪指令级的执行流程，从而捕捉到 `SVC` 的调用。在某些情况下，也可以通过 Hook `libc.so` 中与 `syscall` 相关的底层函数来尝试捕获。

### 网络环境指纹

- **IP 地址**: 最基础的维度，结合地理位置库可以判断用户位置。

- **网络信息**: 运营商名称 (`TelephonyManager.getNetworkOperatorName`)、Wi-Fi BSSID/SSID。

- **TLS/JA3 指纹**: 在建立 TLS 连接时，客户端 `Client Hello` 包的特征可以构成一个稳定的指纹，用于识别特定的网络库和版本。

### 行为特征指纹

行为特征是一种动态指纹，基于用户的操作模式和设备使用习惯。

#### 采集维度

- **1. 触摸行为\*\***
  ```java
  // 触摸事件采集
  view.setOnTouchListener(new View.OnTouchListener() {
  @Override
  public boolean onTouch(View v, MotionEvent event) {
  // 采集触摸压力
  float pressure = event.getPressure();
  // 采集触摸面积
  float size = event.getSize();
  // 采集触摸坐标 andTime 戳
  long timestamp = event.getEventTime();
  float x = event.getX();
  float y = event.getY();
  ```

// Build 触摸特征向量
TouchFeature feature = new TouchFeature(
pressure, size, timestamp, x, y
);
return false;
}
});

````
- 手指接触面积


* *2. 传感器行为**
    ```java
// 加速计/陀螺仪数据采集
SensorManager sensorManager = (SensorManager) getSystemService(SENSOR_SERVICE);
Sensor accelerometer = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER);

sensorManager.registerListener(new SensorEventListener() {
@Override
public void onSensorChanged(SensorEvent event) {
float x = event.values[0];
float y = event.values[1];
float z = event.values[2];

// Analysis持握姿态、步态特征etc.
analyzeMotionPattern(x, y, z);
}

@Override
public void onAccuracyChanged(Sensor sensor, int accuracy) {}
}, accelerometer, SensorManager.SENSOR_DELAY_NORMAL);

````

- **3. 应用使用模式\*\***

* App 启动时间分布
* 常用 App 列表及使用频率
* 前后台切换模式
* 应用安装/卸载习惯

- **4. 网络行为\*\***

* 访问时间模式（工作日 vs 周末，白天 vs 晚上）
* 请求频率和间隔
* 网络切换习惯（WiFi ↔ 4G/5G）
* 常用地理位置

#### 行为指纹生成

```python
class BehaviorFingerprint:
def __init__(self):
self.touch_features = []
self.sensor_features = []
self.app_usage = {}
self.network_pattern = {}

def extract_touch_signature(self, touch_events):
"""
从触摸事件提取用户Signature
"""
# CalculateStatistics特征
pressures = [e.pressure for e in touch_events]
velocities = self._calculate_velocities(touch_events)

signature = {
'avg_pressure': np.mean(pressures),
'std_pressure': np.std(pressures),
'avg_velocity': np.mean(velocities),
'touch_rhythm': self._analyze_rhythm(touch_events)
}
return signature

def generate_behavior_fingerprint(self):
"""
Generate综合行为指纹
"""
touch_sig = self.extract_touch_signature(self.touch_features)
motion_sig = self.extract_motion_signature(self.sensor_features)
usage_sig = self.extract_usage_signature(self.app_usage)

# 组合为行为特征向量
behavior_vector = {
'touch': touch_sig,
'motion': motion_sig,
'usage': usage_sig,
'network': self.network_pattern
}

return hashlib.sha256(
json.dumps(behavior_vector, sort_keys=True).encode()
).hexdigest()

```

import numpy as np

class BehaviorClassifier:
def **init**(self):
self.model = RandomForestClassifier(n_estimators=100)

def train(self, features, labels):
"""
训练行为识别模 Type
features: 行为特征向量 Array
labels: 设备/用户标识
"""
self.model.fit(features, labels)

def predict_device(self, behavior_features):
"""
根据行为特征预测设备身份
"""

# 特征向量化

feature_vector = self.\_vectorize(behavior_features)

# 预测

device_id = self.model.predict([feature_vector])[0]
confidence = self.model.predict_proba([feature_vector]).max()

return device_id, confidence

def detect_anomaly(self, behavior_features, known_device_id):
"""
检测异常行为（可能是账号被盗或设备被冒用）
"""
predicted_id, confidence = self.predict_device(behavior_features)

if predicted_id != known_device_id:
return True, f"Behavior mismatch (confidence: {confidence})"

if confidence < 0.7:
return True, "Low confidence in behavior match"

return False, "Normal behavior"

````

**核心思路**: 识别 -> Hook -> 伪造
1. **识别**: 定位 App 获取关键指纹信息的代码位置（Java API 或 JNI 函数）。
2. **Hook**: 使用 Frida 或 Xposed 拦截这些函数的调用。
3. **伪造**: 在函数返回前，用一套预设的、自洽的假数据替换真实返回值。


**Frida 概念脚本 (伪造 Build.MODEL):**

```javascript
Java.perform(function () {
var Build = Java.use("android.os.Build");
Build.MODEL.value = "Pixel 4"; // Modify MODEL Field

var String = Java.use("java.lang.String");
var TelephonyManager = Java.use("android.telephony.TelephonyManager");
TelephonyManager.getDeviceId.overload().implementation = function () {
console.log("Hooked getDeviceId(). Returning a fake IMEI.");
return String.$new("867530900000000"); // Return伪造 IMEI
};
});

````

- **优点**: 无法通过应用层的检测手段识破，因为 App 获取到的就是系统层返回的"真实"数据。

- **缺点**: 技术门槛高，工作量巨大。

### 环境虚拟化与容器技术

虚拟化和容器技术是规模化设备指纹绕过的核心基础设施，能够在单台物理机上运行数百个独立的 Android 实例。

#### android 虚拟化技术栈

**1. 基于 QEMU 的完整虚拟化**

Android 官方模拟器（AVD）基于 QEMU 实现：

```bash
# startupAVD模拟器
emulator -avd Pixel_6_API_33 \
- no-snapshot \
- wipe-data \
- gpu swiftshader_indirect

```

**主要问题**：

```bash
# 容易被检测的特征
getprop ro.hardware # Return "goldfish" or "ranchu"
getprop ro.product.model # Return "android SDK built for x86"
getprop ro.build.fingerprint # Contains "通用" 字样

# 缺失传感器
pm list features | grep sensor # 大量传感器缺失

```

wget https://osdn.net/projects/android-x86/releases/android-x86_64-9.0-r2.iso

# 在内 VirtualBox, Create 虚拟机

VBoxManage createvm --name "Android-x86" --ostype "Linux_64" --register
VBoxManage modifyvm "Android-x86" --memory 4096 --vram 128
VBoxManage storagectl "Android-x86" --name "SATA" --add sata
VBoxManage storageattach "Android-x86" --storagectl "SATA" \
--port 0 --device 0 --type dvddrive --medium android-x86.iso

````


* *缺点**：
- 仍有虚拟化特征
- GPU加速支持有限
- ARM应用兼容性差（需要ARM转译层）


* *3. 基于容器的方案 (Docker/LXC)**

容器技术提供更轻量的隔离：

```dockerfile
# Dockerfile for android container
FROM ubuntu:20.04

# 安装 android 环境
RUN apt-get update && apt-get install -y \
openjdk-11-jdk \
android-sdk \
adb \
fastboot

# 配置 android 环境
ENV ANDROID_HOME=/opt/android-sdk
ENV PATH=$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools

# RunADBService
CMD ["adb", "-a", "nodaemon", "server"]

````

| LXC/LXD | 系统级 | 高 | 多租户、云手机 |
| Kubernetes | 集群级 | 中 | 大规模部署 |

- **4. 专业容器方案：Redroid\*\***

Redroid 是一个基于 Docker 的 Android 容器方案：

```bash
# RunRedroid容器
docker run -d \
--name redroid \
--privileged \
-v ~/data:/data \
-p 5555:5555 \
redroid/redroid:11.0.0-latest

# Connect to to to to to to Redroid
adb connect localhost:5555
adb shell

```

- 支持 GPU 加速（通过 mesa/virgl）

#### 虚拟化检测对抗

- **检测点 1：Build 属性\*\***

```bash
# 容易暴露的属性
getprop ro.hardware # goldfish/ranchu
getprop ro.product.board # goldfish_x86
getprop ro.product.device # generic
getprop ro.build.product # sdk_gphone_x86
getprop ro.build.tags # test-keys

```

ro.hardware=qcom
ro.product.board=msmnile
ro.product.device=OnePlus7Pro
ro.build.product=OnePlus7Pro
ro.build.tags=release-keys
EOF

```
# 虚拟机可能显示: Intel Core i7 (主机 CPU)
# 真机应该显示: Qualcomm Snapdragon 888

# DetectionHypervisor
cat /proc/cpuinfo | grep hypervisor
# If exists at, indicatesRunAt虚拟机In

```

static int c_show(struct seq_file *m, void *v) {
// 伪造 CPUInfo
seq_printf(m, "model name\t: %s\n", fake_cpu_name);
// ...
}

```
List<Sensor> sensors = sm.getSensorList(Sensor.TYPE_ALL);

// 模拟器可能只有 3-5 个基本传感器
if (sensors.size() < 15) {
// 可能是模拟器
}

```

"android.hardware.SensorManager",
lpparam.classLoader,
"getSensorList",
int.class,
new XC_MethodHook() {
@Override
protected void afterHookedMethod(MethodHookParam param) {
List<Sensor> original = (List<Sensor>) param.getResult();
// Add 伪造传感器
original.add(createFakeSensor(Sensor.TYPE_GYROSCOPE));
original.add(createFakeSensor(Sensor.TYPE_MAGNETIC_FIELD));
// ...
param.setResult(original);
}
}
);

```
ls -la /dev/ | grep -E "qemu|vbox|vmware"

# 检测特定设备节点
if [ -e "/dev/socket/qemud" ]; then
echo "Emulator detected"
fi

```

# !/system/bin/sh

# 删除或隐藏模拟器特征

rm -f /dev/socket/qemud
rm -f /dev/qemu_pipe
mount -o bind /dev/null /system/bin/qemu-props
EOF

```
# ConfigGPU直通（NeedIOMMUSupport）
# 编辑 /etc/默认/grub
GRUB_CMDLINE_LINUX="intel_iommu=on vfio-pci.ids=10de:1b80"

# 创建带 GPU 的虚拟机
virt-install \
- -name android-vm \
- -ram 8192 \
- -vcpus 4 \
- -disk path=/var/lib/libvirt/images/android.qcow2 \
- -hostdev 01:00.0 # GPU PCIAddress

```

snap install --devmode --beta anbox

# AnboxUseLXC 容器，几乎 NoPerformance 损失

lxc-info -n android

````


* *3. 嵌套虚拟化**

在云服务器上运行Android虚拟机：

```bash
# AWS EC2上Enabled嵌套虚拟化
aws ec2 modify-instance-attribute \
--instance-id i-1234567890abcdef0 \
--cpu-options "CoreCount=4,ThreadsPerCore=2"

# 检查 if KVM is 可用
lsmod | grep kvm

````

│ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│ │Android │ │Android │ │Android │ │
│ │Container │ │Container │ │Container │ ... │
│ │ #1 │ │ #2 │ │ #N │ │
│ └────┬─────┘ └────┬─────┘ └────┬─────┘ │
├───────┴──────────────┴─────────────┴─────────────┤
│ 容器编排 Layer (Orchestration) │
│ - 调度 (Scheduling) │
│ - 负载均衡 (Load Balancing) │
│ - Auto 扩缩容 (Auto Scaling) │
├─────────────────────────────────────────────────┤
│ 物理 Server / 云 Main 机 │
│ - 高 PerformanceCPU (多 Core) │
│ - 大 Memory (128GB+) │
│ - GPU (Optional，Used for 加速) │
└─────────────────────────────────────────────────┘

```
kind: Deployment
metadata:
name: android-farm
spec:
replicas: 50 # 50androidInstance
selector:
matchLabels:
app: android
template:
metadata:
labels:
app: android
spec:
containers:
- name: android
image: redroid/redroid:11.0.0
securityContext:
privileged: true
resources:
limits:
memory: "2Gi"
cpu: "2"
ports:
- containerPort: 5555
image: redroid/redroid:11.0.0
securityContext:
privileged: true
resources:
limits:
memory: "2Gi"
cpu: "2"
ports:
- containerPort: 5555
___
apiVersion: v1
kind: Service
metadata:
name: android-service
spec:
type: LoadBalancer
selector:
app: android
ports:
- port: 5555
targetPort: 5555

```

#### 云手机架构

**1. 技术栈分层**

```
│ - WebControl台 │
│ - APIService │
│ - Auto化Script │
├────────────────────────────────────────┤
│ 云手机InstanceLayer (Instance Layer) │
│ ┌──────────┐ ┌──────────┐ │
│ │ 云手机1 │ │ 云手机2 │ ... │
│ │ Android │ │ Android │ │
│ └──────────┘ └──────────┘ │
├────────────────────────────────────────┤
│ 虚拟化Layer (Virtualization Layer) │
│ - ARM虚拟化 (KVM/QEMU) │
│ - GPU虚拟化 (vGPU) │
│ - Network虚拟化 (VPC) │
├────────────────────────────────────────┤
│ 硬件Layer (Hardware Layer) │
│ - ARMServer (华为鲲鹏/飞腾) │
│ - 高PerformanceStorage (NVMe SSD) │
│ - 专用GPU (Mali/Adreno) │
└────────────────────────────────────────┘

```

- AWS Graviton2

优势：

- 原生 ARM 指令集，No 需转译
- 性能接近真实设备
- 兼容性极好

  ```

  ```

**实现方案**：

```bash
# UselibvirtManageKVM虚拟机
virsh define android-vm.xml

# android-vm.xml
<domain type='kvm'>
<name>android-1</name>
<memory unit='GiB'>4</memory>
<vcpu>4</vcpu>
<os>
<type arch='aarch64'>hvm</type>
<boot dev='hd'/>
</os>
<devices>
<disk type='file' device='disk'>
<source file='/var/lib/libvirt/images/android.img'/>
<target dev='vda' bus='virtio'/>
</disk>
<graphics type='vnc' port='5900'/>
</devices>
</domain>

```

- 自研容器 RunWhen

优势：

- 极高密度 (单台 ServerRun100+Instance)
- 快速 Start/Boot (<5Second)
- Resources 占用低

  ```

  ```

**实现示例**：

```bash
# Use to runandroid
lxc launch ubuntu:20.04 android-base
lxc exec android-base -- bash

# 在内 容器, Installandroid
apt-get install android-tools-adb android-tools-fastboot

# 配置 android 系统
lxc config set android-base raw.lxc "lxc.mount.auto = proc:rw sys:rw"
lxc config device add android-base kmsg unix-char path=/dev/kmsg

```

- 软件渲染 (SwiftShader, ANGLE)

App 场景：

- 游戏云手机
- 视频 Process
- 图形渲染

  ```

  ```

#### 云手机平台对比

| 平台            | 架构           | 密度 | 性能 | 成本 | 适用场景         |
| --------------- | -------------- | ---- | ---- | ---- | ---------------- |
| 华为云手机      | ARM 服务器+KVM | 中   | 高   | 高   | 企业级应用       |
| 红手指          | ARM 容器       | 高   | 中   | 中   | 自动化、挂机     |
| 多多云手机      | x86+容器       | 高   | 低   | 低   | 批量注册、养号   |
| AWS Device Farm | 真机           | 低   | 极高 | 极高 | 测试、兼容性验证 |

#### 云手机指纹特征

云手机虽然接近真机，但仍有可被检测的特征：

**检测点 1：性能特征异常**

```java
// 云手机CPUPerformance可能过于一致
long startTime = System.nanoTime();
for (int i = 0; i < 1000000; i++) {
Math.sqrt(i);
}
long duration = System.nanoTime() - startTime;

// True机会有波动，云手机可能过于Stable

```

# 云手机通常使用数据中心 IP

curl ifconfig.me

# 返回: 42.120.x.x (阿里云)

# 119.28.x.x (腾讯云)

# DetectionIPClassType

curl https://api.ipgeolocation.io/ipgeo?apiKey=xxx

# organization: "Alibaba Cloud"

# isp: "China Mobile" # 真机更常见

```

```

- SupportGPU 加速
- 提供原生 Android 体验

APIUse：

```python
from huaweicloudsdkcore.auth.credentials import BasicCredentials
from huaweicloudsdkcph.v1 import CphClient, RunCloudPhoneRequest

# 创建云手机实例
credentials = BasicCredentials(ak, sk)
client = CphClient.new_builder().with_credentials(credentials).build()

request = RunCloudPhoneRequest()
request.body = {
"server_id": "server-123",
"phone_model": "cloudphone.arm.d2.16_64",
"count": 10
}
response = client.run_cloud_phone(request)

```

- 7x24 小时在线
- 主要用于游戏挂机

特点：

- 价格便宜 (几元/月)
- 性能一般
- 有明显的虚拟化特征

  ```

  ```

**3. 多多云 (DuoduoCloud)**

````
- 提供HTTP API
- 支持批量控制
- 适合自动化业务


使用示例：

```bash
# APIControl云手机
curl -X POST https://api.duoduoyun.com/v1/device/control \
- H "Authorization: Bearer $TOKEN" \
- d '{
"device_id": "12345",
"action": "install_app",
"package": "com.example.app"
}'

````

- 定制设备配置参数

**策略 2：设备指纹随机化**

```python
# 为每个云手机实例生成唯一指纹
def customize_cloud_phone(device_id):
fingerprint = generate_realistic_fingerprint()

# 通过 ADB 修改设备属性
adb_connect(device_id)
adb_shell(f"setprop ro.product.model {fingerprint['model']}")
adb_shell(f"setprop ro.build.fingerprint {fingerprint['build_fp']}")

# 安装随机 App
install_random_apps(device_id, count=random.randint(20, 50))

```

# 随机浏览时长

browse_time = random.randint(300, 1800) # 5-30Minute

# 随机点击

for \_ in range(random.randint(5, 20)):
x = random.randint(0, device.width)
y = random.randint(0, device.height)
device.tap(x, y)
time.sleep(random.uniform(1, 5))

# 模拟传感器数据

inject_sensor_data(device)

```


- --

## 商业化产品与服务

### 国内主流设备指纹服务商

#### 1. 顶象科技 (DingXiang)

* *产品**: 顶象设备指纹 (Device Fingerprint)

* *技术特点**：
- 采集200+设备特征维度
- 支持Android、iOS、Web、小程序
- 99.9%+设备唯一性识别率
- 设备指纹有效期90天+
- 支持私有化部署


* *核心能力**：

```

- 黑名单管理

  ```

  ```

**定价**：按 API 调用次数计费，企业版约 0.005-0.01 元/次

#### 2. 同盾科技 (Tongdun)

**产品**: 同盾设备指纹

**技术特点**：

- 结合 AI 和大数据分析
- 设备行为画像
- 实时风险决策
- 覆盖金融、电商、O2O 等场景

**API 示例**：

```python
import requests
import json

def tongdun_device_risk(device_id, event_type):
"""
Call同盾设备风险评估API
"""
url = "https://api.tongdun.cn/riskService"

params = {
"partner_code": "your_partner_code",
"device_id": device_id,
"event_type": event_type, # 如: login, register, pay
"timestamp": int(time.time() * 1000)
}

# AddSignature
params["sign"] = generate_sign(params)

response = requests.post(url, json=params)
result = response.json()

return {
"risk_score": result["final_score"], # 风险分数 0-100
"risk_level": result["risk_level"], # high/medium/low
"device_labels": result["labels"] # 设备标签
}

```

- **技术特点\*\***：

* 专注于内容安全和业务安全
* 设备指纹+行为分析
* 实时黑产设备库
* 支持多场景风控

- **应用场景\*\***：

* 羊毛党识别
* 虚假注册拦截
* 刷单检测
* 恶意爬虫识别

#### 4. 网易易盾 (NetEase YiDun)

- **产品\*\***: 易盾设备指纹

- **技术特点\*\***：

* 网易内部风控技术外化
* 游戏、社交场景优化
* 设备唯一性识别
* 设备环境检测（Root、模拟器、Hook 框架）

- **SDK 集成示例**（Android）\*\*：

```java
// Initialize
NECaptcha.getInstance()
.init(context, "your_business_id", new NECaptchaListener() {
@Override
public void onReady() {
// 获取设备指纹
String deviceId = NEDeviceRisk.getDeviceId();
}
});

// 获取设备风险信息
NEDeviceRisk.check(context, new NEDeviceRiskCallback() {
@Override
public void onResult(NEDeviceRiskResult result) {
int riskLevel = result.getRiskLevel(); // 0-4级风险
boolean isEmulator = result.isEmulator();
boolean isRooted = result.isRoot();
boolean isHooked = result.isHook();
}
});

```

- 微信、QQ 生态数据支持
- 黑产设备库实时更新
- 设备风险评分

* **定价\*\***：

- 按 QPS 计费
- 企业版: 约 0.01-0.03 元/次
- 支持包年包月

### 国际知名产品

#### 1. FingerprintJS

- **类型\*\***: 开源 + 商业版

- **特点\*\***：

* 主要用于 Web 浏览器指纹
* 开源版本基础功能免费
* Pro 版提供 99.5%准确率

- **使用示例\*\***：

```javascript
import FingerprintJS from "@fingerprintjs/fingerprintjs";

// Initializeagent
const fpPromise = FingerprintJS.load();

// Get访客标识
fpPromise
  .then((fp) => fp.get())
  .then((result) => {
    // ThisIs访客标识
    const visitorId = result.visitorId;
    console.log(visitorId);

    // 所有Component（浏览器特征）
    console.log(result.components);
  });
```

- 包含数万种设备型号
- 主要用于移动广告和分析
- 支持云端 API 和本地部署

* **API 示例\*\***：

```python
from deviceatlas import DeviceApi

# Initialize
api = DeviceApi("/path/to/DeviceAtlas.json")

# 根据 User-Agent 识别设备
user_agent = "Mozilla/5.0 (Linux; Android 11; Pixel 5)..."
properties = api.get_properties(user_agent)

print(properties.get('displayWidth')) # 屏幕宽度
print(properties.get('model')) # 设备型号
print(properties.get('manufacturer')) # 制造商

```

- 广告归因追踪
- 防作弊机制
- 支持 IDFA、GAID、设备指纹

#### 4. AppsFlyer

- **产品\*\***: 移动归因和营销分析

- **特点\*\***：

* 设备指纹技术
* 防作弊（Protect360）
* 支持跨平台追踪
* 隐私保护模式

---

## 开源工具与框架

### 设备指纹采集框架

#### 1. fingerprintjs2 (已废弃，由 FingerprintJS 取代)

- **GitHub\*\***: https://github.com/fingerprintjs/fingerprintjs

- **特点\*\***：

* 轻量级浏览器指纹库
* 纯 JavaScript 实现
* 采集 Canvas、WebGL、Audio 等特征

- **使用示例\*\***：

```javascript
Fingerprint2.get(function (components) {
  // Component 是键值对数组
  var values = components.map(function (component) {
    return component.value;
  });

  // 计算指纹哈希
  var murmur = Fingerprint2.x64hash128(values.join(""), 31);
  console.log(murmur); // 设备指纹
});
```

- 支持 12000+设备型号
- 可以根据 Build.MODEL 获取市场化设备名称

* **使用示例\*\***：

```java
DeviceName.with(context).request(new DeviceName.Callback() {
@Override
public void onFinished(DeviceName.DeviceInfo info, Exception error) {
String manufacturer = info.manufacturer; // "Samsung"
String marketName = info.marketName; // "Galaxy S21"
String model = info.model; // "SM-G991B"
String codename = info.codename; // "o1s"
}
});

```

- 解析 User-Agent
- 识别设备类型、品牌、型号

* **Python 示例\*\***：

```python
from device_detector import DeviceDetector

user_agent = "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X)..."
device = DeviceDetector(user_agent).parse()

print(device.os_name()) # iOS
print(device.device_brand()) # Apple
print(device.device_model()) # iPhone
print(device.is_mobile()) # True

```

```bash
# 修改设备指纹
props ro.build.fingerprint "google/raven/raven:12/..."
props ro.product.model "Pixel 6"

# 应用修改
props ro.build.product "raven"

```

#### 2. Xposed 模块

- **a) XPrivacyLua\*\***

- **GitHub\*\***: https://github.com/M66B/XPrivacyLua

- **功能\*\***：

* 细粒度权限控制
* API 返回值 Hook
* 设备信息伪造

- **使用\*\***：

````
    ```

**b) VirtualXposed / Taichi**

**功能**：
- 免 Root 使用 Xposed
- 应用虚拟化
- 在虚拟环境中修改设备信息

#### 3. Frida 脚本库

**a) frida-scripts (设备指纹相关)**

常用的设备信息 Hook 脚本：

```javascript
// 通用设备信息 Hook 脚本
Java.perform(function() {
// 拦截 Build 类所有字段
var Build = Java.use("android.os.Build");
Build.BRAND.value = "google";
Build.MODEL.value = "Pixel 6";
Build.DEVICE.value = "raven";
Build.PRODUCT.value = "raven";
Build.MANUFACTURER.value = "Google";

// Hook settingsss.Secure
var Settings = Java.use("android.provider.Settings$Secure");
Settings.getString.overload(
"android.content.ContentResolver",
"java.lang.String"
).implementation = function(resolver, name) {
if (name == "android_id") {
return "fake_android_id_12345678";
}
return this.getString(resolver, name);
};

// Hook TelephonyManager
var TelephonyManager = Java.use("android.telephony.TelephonyManager");
TelephonyManager.getDeviceId.overload().implementation = function() {
return "fake_imei_123456789012345";
};
});

````

- **功能\*\***：

* 修改 Android ID
* 修改 IMEI/MEID
* 修改 MAC 地址
* 修改手机号码
* 修改设备序列号

- **b) Busybox 改机\*\***

使用 busybox 命令修改系统文件：

```bash
# Modifybuild.prop
busybox sed -i 's/ro.product.model=.*/ro.product.model=Pixel 6/' /system/build.prop

# ModifyMultipleProperty
cat >> /system/build.prop << EOF
ro.product.brand=google
ro.product.device=raven
ro.product.manufacturer=Google
EOF

```

|------|------|
| **GSMArena API** | 设备规格数据库 |
| **Device Atlas** | 商业设备属性 API |
| **WURFL** | 设备描述库 |

- **使用示例\*\***：

```python
import requests

def get_device_specs(model):
"""
从GSMArenaGet设备规格
"""
api_url = f"https://api.gsmarena.com/devices/{model}"
response = requests.get(api_url)

if response.status_code == 200:
data = response.json()
return {
'model': data['model'],
'display': data['display'],
'chipset': data['chipset'],
'memory': data['memory'],
'camera': data['camera'],
'battery': data['battery'],
'sensors': data['sensors']
}

```

def **init**(self, device_pool_db):
self.db = device_pool_db
self.used_fingerprints = set()

def get_unused_fingerprint(self):
"""
从设备池中获取未使用的指纹
"""
while True:
fp = self.db.get_random_fingerprint()
fp_hash = hashlib.md5(json.dumps(fp).encode()).hexdigest()

if fp_hash not in self.used_fingerprints:
self.used_fingerprints.add(fp_hash)
return fp

def apply_fingerprint(self, adb_device, fingerprint):
"""
将指纹应用到设备
"""

# 修改系统属性

for key, value in fingerprint['build_props'].items():
adb_device.shell(f"setprop {key} {value}")

# 安装预设 App

for apk in fingerprint['apps']:
adb_device.install(apk)

# settingssssss 位置

adb_device.shell(f"settings put secure location_mode 3")
adb_device.shell(
f"am startservice -a com.example.fakelocation "
f"--es lat {fingerprint['location']['lat']} "
f"--es lng {fingerprint['location']['lng']}"
)

def rotate_fingerprint(self, adb_device, interval_hours=24):
"""
定期轮换设备指纹
"""
while True:
new_fp = self.get_unused_fingerprint()
self.apply_fingerprint(adb_device, new_fp)

# 记录 usage 历史

self.db.log_usage(adb_device.serial, new_fp, timestamp=time.time())

time.sleep(interval_hours \*\* 3600)

````

* 检查 `/proc/self/maps` 中是否加载了 `frida-agent.so` 或 `XposedBridge.jar`。


* 检测 Frida 的默认端口 `27042`。


* 通过 `try-catch` 执行一个会因 Xposed 修改而改变行为的函数，判断是否抛出异常。


### 服务端交叉验证

这是设备指紋技术最强大的地方。
后端服务会将客户端上传的几百个维度的指纹数据进行交叉比对。一个 `IMEI` 显示是三星设备，但 `Build.FINGERPRINT` 却属于小米，这种矛盾会立刻导致该设备被标记为高风险。任何与"正常设备"行为模式不符的特征组合都会被识别出来。

**交叉验证规则示例**：

```python
class FingerprintValidator:
def __init__(self):
self.device_database = self.load_device_db()
self.inconsistency_rules = self.load_rules()

def validate_fingerprint(self, fingerprint):
"""
Validate设备指纹一致性
"""
issues = []

# 规则1：品牌与型号匹配
if not self.check_brand_model_match(
fingerprint['brand'],
fingerprint['model']
):
issues.append({
'type': 'brand_model_mismatch',
'severity': 'high',
'message': f"Brand {fingerprint['brand']} does not match model {fingerprint['model']}"
})

# 规则2：屏幕分辨率与型号匹配
expected_resolution = self.device_database.get_resolution(fingerprint['model'])
if fingerprint['screen_resolution'] != expected_resolution:
issues.append({
'type': 'resolution_mismatch',
'severity': 'medium',
'message': f"Unexpected resolution for {fingerprint['model']}"
})

# 规则3：传感器ListComplete性
expected_sensors = self.device_database.get_sensors(fingerprint['model'])
if len(fingerprint['sensors']) < len(expected_sensors) * 0.8:
issues.append({
'type': 'sensor_missing',
'severity': 'high',
'message': 'Too few sensors for this device model'
})

# 规则4：CPU型号与设备型号匹配
expected_cpu = self.device_database.get_cpu(fingerprint['model'])
if fingerprint['cpu'] != expected_cpu:
issues.append({
'type': 'cpu_mismatch',
'severity': 'high',
'message': f"CPU mismatch: expected {expected_cpu}, got {fingerprint['cpu']}"
})

# 规则5：BuildTime戳合理性
release_date = self.device_database.get_release_date(fingerprint['model'])
if fingerprint['build_time'] < release_date:
issues.append({
'type': 'build_time_invalid',
'severity': 'critical',
'message': 'Build date earlier than device release date'
})

return {
'is_valid': len(issues) == 0,
'risk_score': self.calculate_risk_score(issues),
'issues': issues
}

````

使用标注数据训练模型，识别真实设备 vs 伪造设备：

```python
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
import numpy as np

class DeviceAuthenticityClassifier:
def __init__(self):
# 集成多个模型
self.models = {
'random_forest': RandomForestClassifier(n_estimators=200, max_depth=15),
'gradient_boosting': GradientBoostingClassifier(n_estimators=100),
'neural_network': MLPClassifier(hidden_layers=(128, 64, 32))
}
self.feature_extractor = FeatureExtractor()

def train(self, X_train, y_train):
"""
训练分类器
X_train: 设备指纹特征
y_train: 标签 (0=伪造, 1=True实)
"""
for name, model in self.models.items():
print(f"Training {name}...")
model.fit(X_train, y_train)

def predict(self, fingerprint):
"""
预测设备真实性
"""
features = self.feature_extractor.extract(fingerprint)

# 集成投票
votes = []
probabilities = []

for name, model in self.models.items():
pred = model.predict([features])[0]
prob = model.predict_proba([features])[0]
votes.append(pred)
probabilities.append(prob[1]) # 真实设备概率

# 加权平均
avg_probability = np.mean(probabilities)

return {
'is_genuine': avg_probability > 0.5,
'confidence': avg_probability,
'votes': dict(zip(self.models.keys(), votes))
}

class FeatureExtractor:
def extract(self, fingerprint):
"""
从原始指纹提取机器学习特征
"""
features = []

# 1. 数值特征
features.extend([
fingerprint.get('screen_width', 0),
fingerprint.get('screen_height', 0),
fingerprint.get('dpi', 0),
fingerprint.get('memory_mb', 0),
fingerprint.get('cpu_cores', 0),
len(fingerprint.get('sensors', [])),
len(fingerprint.get('installed_apps', []))
])

# 2. 分Class特征（独热Encode）
features.extend(self.encode_categorical(fingerprint.get('brand', 'unknown')))
features.extend(self.encode_categorical(fingerprint.get('os_version', 'unknown')))

# 3. Statistics特征
app_list = fingerprint.get('installed_apps', [])
features.append(self.calculate_app_diversity(app_list))

# 4. 一致性特征
features.append(self.check_brand_model_consistency(fingerprint))
features.append(self.check_hardware_software_consistency(fingerprint))

return np.array(features)

def calculate_app_diversity(self, app_list):
"""
CalculateAppList多样性
伪造设备可能AppList过于SimpleOr过于Complex
"""
if not app_list:
return 0

# 使用香农熵衡量多样性
from collections import Counter
counts = Counter(app.split('.')[0] for app in app_list) # ByPackageNameBefore缀
total = len(app_list)
entropy = -sum((count/total) * np.log2(count/total) for count in counts.values())

return entropy

```

from sklearn.covariance import EllipticEnvelope

class AnomalyDetector:
def **init**(self):
self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)
self.elliptic_envelope = EllipticEnvelope(contamination=0.1)

def fit(self, normal_devices):
"""
使用正常设备数据训练
normal_devices: 已知真实设备特征向量
"""
self.isolation_forest.fit(normal_devices)
self.elliptic_envelope.fit(normal_devices)

def detect_anomaly(self, device_features):
"""
Detection 设备 IsNoException
Return: (is_anomaly, anomaly_score)
"""

# Isolation Forest Detection

if_score = self.isolation_forest.score_samples([device_features])[0]
if_pred = self.isolation_forest.predict([device_features])[0] # -1representsanomaly

# Elliptic Envelope Detection

ee_pred = self.elliptic_envelope.predict([device_features])[0]

# 综合检查

is_anomaly = (if_pred == -1) or (ee_pred == -1)
anomaly_score = abs(if_score) # 分数越低越 anomaly

return is_anomaly, anomaly_score

```
from tensorflow.keras import layers, models

class DeepFingerprintDetector:
def __init__(self, input_dim):
self.model = self.build_model(input_dim)

def build_model(self, input_dim):
"""
Build深度神经Network
"""
model = models.Sequential([
layers.Dense(256, activation='relu', input_shape=(input_dim,)),
layers.Dropout(0.3),
layers.Dense(128, activation='relu'),
layers.Dropout(0.3),
layers.Dense(64, activation='relu'),
layers.Dropout(0.2),
layers.Dense(32, activation='relu'),
layers.Dense(1, activation='sigmoid') # 输出: True实设备概率
])

model.compile(
optimizer='adam',
loss='binary_crossentropy',
metrics=['accuracy', tf.keras.metrics.AUC()]
)

return model

def train(self, X_train, y_train, epochs=50, batch_size=32):
"""
训练模Type
"""
self.model.fit(
X_train, y_train,
epochs=epochs,
batch_size=batch_size,
validation_split=0.2
)

def predict(self, device_features):
"""
预测设备真实性
"""
probability = self.model.predict([device_features])[0][0]

return {
'is_genuine': probability > 0.5,
'confidence': probability
}

```

from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.models import Sequential

class BehaviorSequenceDetector:
def **init**(self, sequence_length=100, feature_dim=20):
self.sequence_length = sequence_length
self.model = self.build_lstm_model(sequence_length, feature_dim)

def build_lstm_model(self, sequence_length, feature_dim):
"""
BuildLSTM 模 TypeAnalyze 行为序列
"""
model = Sequential([
LSTM(128, return_sequences=True, input_shape=(sequence_length, feature_dim)),
LSTM(64, return_sequences=False),
Dense(32, activation='relu'),
Dense(1, activation='sigmoid')
])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
return model

def detect_bot_behavior(self, action_sequence):
"""
Detection 机器人行为
action_sequence: 用户操作序列 (点击、滑动、输入等)
"""

# 提取特征

features = self.extract_sequence_features(action_sequence)

# 预测

is_bot_probability = self.model.predict([features])[0][0]

return {
'is_bot': is_bot_probability > 0.7,
'confidence': is_bot_probability,
'suspicious_patterns': self.identify_suspicious_patterns(action_sequence)
}

def identify_suspicious_patterns(self, action_sequence):
"""
识别可疑模式
"""
patterns = []

# 检测过于规律的操作

if self.is_too_regular(action_sequence):
patterns.append('regular_intervals')

# 检测不自然的速度

if self.is_speed_abnormal(action_sequence):
patterns.append('abnormal_speed')

# 检测缺少人类特征（如微小抖动）

if not self.has_human_jitter(action_sequence):
patterns.append('no_human_jitter')

return patterns

```

class DeviceGraphAnalyzer:
def __init__(self):
self.device_graph = nx.Graph()

def add_device_relationships(self, device_id, related_devices, relationship_type):
"""
Add设备关系到图In
relationship_type: 'same_ip', 'same_wifi', 'same_behavior', etc.
"""
self.device_graph.add_node(device_id)

for related_id in related_devices:
self.device_graph.add_edge(
device_id,
related_id,
relationship=relationship_type
)

def detect_device_farm(self, threshold=10):
"""
检测设备农场（大量关联设备）
"""
# 寻找连通分量
components = list(nx.connected_components(self.device_graph))

suspicious_clusters = []
for component in components:
if len(component) > threshold:
# AnalyzeThisCluster特征
cluster_info = {
'devices': list(component),
'size': len(component),
'density': nx.density(self.device_graph.subgraph(component)),
'risk_score': self.calculate_cluster_risk(component)
}
suspicious_clusters.append(cluster_info)

return suspicious_clusters

def calculate_cluster_risk(self, device_cluster):
"""
计算设备簇风险分数
"""
subgraph = self.device_graph.subgraph(device_cluster)

# 特征1：连接密度（密度越高，越可能是设备农场）
density = nx.density(subgraph)

# 特征2：共享关系类型
edge_types = [subgraph[u][v]['relationship'] for u, v in subgraph.edges()]
type_diversity = len(set(edge_types)) / len(edge_types) if edge_types else 0

# 特征3：簇大小
size_score = min(len(device_cluster) / 100, 1.0)

# 综合评分
risk_score = (density * 0.4 + (1 - type_diversity) * 0.3 + size_score * 0.3) * 100

return risk_score

```

class FeatureImportanceAnalyzer:
def **init**(self, model, X_train):
self.model = model
self.explainer = shap.TreeExplainer(model)
self.X_train = X_train

def analyze_feature_importance(self, feature_names):
"""
Analyze 哪些特征对识别伪造设备最重要
"""
shap_values = self.explainer.shap_values(self.X_train)

# 绘制特征重要性图

shap.summary_plot(shap_values, self.X_train, feature_names=feature_names)

# 获取特征重要性排名

feature_importance = np.abs(shap_values).mean(axis=0)
importance_df = pd.DataFrame({
'feature': feature_names,
'importance': feature_importance
}).sort_values('importance', ascending=False)

return importance_df

def explain_prediction(self, device_features, feature_names):
"""
解释单个设备预测结果
"""
shap_values = self.explainer.shap_values(device_features)

# 可视化

shap.force_plot(
self.explainer.expected_value,
shap_values,
device_features,
feature_names=feature_names
)

# ReturnContribution 最大特征

contributions = dict(zip(feature_names, shap_values.flatten()))
top_contributors = sorted(
contributions.items(),
key=lambda x: abs(x[1]),
reverse=True
)[:10]

return top_contributors

````
某大型电商平台面临大量刷单、虚假评论和薅羊毛行为，需要通过设备指纹识别恶意用户。

**技术方案**：

**1. 指纹采集**

```java
public class EcommerceFingerprintCollector {
public DeviceFingerprint collect(Context context) {
DeviceFingerprint fp = new DeviceFingerprint();

// Basic硬件Info
fp.setAndroidId(getAndroidId(context));
fp.setModel(Build.MODEL);
fp.setBrand(Build.BRAND);

// NetworkInfo
fp.setIpAddress(getIPAddress());
fp.setMacAddress(getMacAddress(context));

// AppInfo
fp.setInstalledApps(getInstalledApps(context));

// 行为特征
fp.setTouchPressure(collectTouchPressure());
fp.setTypingSpeed(collectTypingSpeed());

// 环境Detection
fp.setIsRooted(checkRootStatus());
fp.setIsEmulator(checkEmulatorStatus());
fp.setIsHooked(checkHookStatus());

return fp;
}

private boolean checkHookStatus() {
// DetectionFrida
if (checkFridaPort()) return true;
if (checkFridaLibraries()) return true;

// DetectionXposed
if (checkXposedEnvironment()) return true;

return false;
}
}

````

self.fingerprint_db = FingerprintDatabase()
self.ml_detector = DeviceAuthenticityClassifier()
self.behavior_analyzer = BehaviorSequenceDetector()

def check_order_risk(self, user_id, device_fp, order_info):
"""
订单风险评估
"""
risk_factors = []
risk_score = 0

# 1. 设备指纹 Check

device_risk = self.check_device_fingerprint(device_fp)
if device_risk['is_suspicious']:
risk_factors.append(device_risk)
risk_score += 30

# 2. 设备 AssociationAnalyze

related_devices = self.fingerprint_db.find_related_devices(device_fp)
if len(related_devices) > 10:
risk_factors.append({
'type': 'device_cluster',
'message': f'Device associated with {len(related_devices)} other devices'
})
risk_score += 25

# 3. 用户行为 Analyze

user_behavior = self.fingerprint_db.get_user_behavior(user_id)
if self.is_bot_behavior(user_behavior):
risk_factors.append({'type': 'bot_behavior'})
risk_score += 35

# 4. 订单特征 Analyze

if order_info['amount'] > 10000 and order_info['create_time'] - user_id.register_time < 3600:
risk_factors.append({'type': 'new_user_large_order'})
risk_score += 20

# 决策

if risk_score >= 60:
action = 'reject'
elif risk_score >= 40:
action = 'manual_review'
else:
action = 'approve'

return {
'action': action,
'risk_score': risk_score,
'risk_factors': risk_factors
}

def check_device_fingerprint(self, fp):
"""
设备指纹完整性检查
"""
issues = []

# 检测模拟器

if fp.get('is_emulator'):
issues.append('emulator_detected')

# 检测 Hook 框架

if fp.get('is_hooked'):
issues.append('hook_framework_detected')

# 检测设备参数一致性

validator = FingerprintValidator()
validation = validator.validate_fingerprint(fp)
if not validation['is_valid']:
issues.extend([issue['type'] for issue in validation['issues']])

# 机器学习检测

ml_result = self.ml_detector.predict(fp)
if not ml_result['is_genuine']:
issues.append('ml_fake_device_detected')

return {
'is_suspicious': len(issues) > 0,
'issues': issues,
'risk_level': 'high' if len(issues) >= 3 else 'medium' if len(issues) > 0 else 'low'
}

````
- Frida Hook设备信息API
- 随机化应用列表


* *检测对抗**：

```python
def advanced_detection(device_fp, user_behavior):
"""
AdvancedDetection技术
"""
# Detection1：云手机特征
if is_cloud_phone(device_fp):
return {'blocked': True, 'reason': 'cloud_phone_detected'}

# Detection2：代理/机房IP
ip_info = get_ip_info(device_fp['ip_address'])
if ip_info['isp'] in ['Alibaba Cloud', 'Tencent Cloud', 'AWS']:
if not is_corporate_user(user_id):
return {'blocked': True, 'reason': 'datacenter_ip'}

# 检测3：设备参数过于完美
if all_parameters_perfectly_match(device_fp):
return {'blocked': True, 'reason': 'too_perfect_fingerprint'}

# Detection4：行为模式机器化
if behavior_too_regular(user_behavior):
return {'blocked': True, 'reason': 'bot_behavior'}

return {'blocked': False}

````

### 案例 2：金融 App 风控绕过

- **背景\*\***：
  某金融 App 使用顶象设备指纹进行风控，攻击者尝试绕过进行批量注册和薅羊毛。

- **App 保护措施\*\***：

1. 集成顶象 SDK 采集设备指纹
2. SO 层加固（360 加固）
3. 检测 Root、模拟器、Hook 框架
4. 网络请求签名验证

- **分析过程\*\***：

- **Step 1: 设备指纹 SDK 定位\*\***

```bash
# 反编译 APK
apktool d app.apk

# 搜索设备指纹相关代码
grep -r "getDeviceId" .
grep -r "fingerprint" .

# 找到 SDK 包名
# com.dingxiang.sdk.fingerprint

```

// Hook 顶象 SDK
var DXFingerprint = Java.use("com.dingxiang.sdk.fingerprint.DXFingerprint");

DXFingerprint.getDeviceId.implementation = function() {
console.log("[*] getDeviceId() called");

// Return 伪造设备 ID
var fakeDeviceId = "fake*dx_device_id*" + Math.random().toString(36).substring(7);
console.log("[*] Returning fake device ID: " + fakeDeviceId);

return fakeDeviceId;
};

// Hook 采集 Method
DXFingerprint.collect.implementation = function(context) {
console.log("[*] collect() called");

// Modify 采集 Data
var result = this.collect(context);

// 篡改指纹 Data
modifyFingerprintData(result);

return result;
};
});

````

```python
CompleteBypassFlow
"""
# 1. 准备环境
device = setup_rooted_device()

# 2. InstallMagisk隐藏Root
install_magisk_modules([
'MagiskHide',
'Universal SafetyNet Fix',
'Device Faker'
])

# 3. 修改设备指纹
fake_fingerprint = generate_realistic_fingerprint()
apply_fingerprint(device, fake_fingerprint)

# 4. 隐藏 Frida
use_frida_server_rename()
use_frida_gadget_injection()

# 5. 启动 Frida 脚本
frida_script = load_script('dingxiang_bypass.js')
attach_to_app(device, 'com.financial.app', frida_script)

# 6. 代理设置（绕过 IP 风控）
setup_proxy(device, get_random_proxy())

# 7. 模拟真实行为
simulate_human_behavior(device, duration=300) # 5 分钟

# 8. 执行目标操作
register_account(device)

````

```javascript
Java.perform(function () {
  // 1. 拦截 Native 层设备指纹采集
  var libc = Process.getModuleByName("libc.so");

  // Hook系统Call（SVC指令）
  Interceptor.attach(Module.findExportByName("libc.so", "syscall"), {
    onEnter: function (args) {
      var syscall_num = args[0].toInt32();

      // InterceptSpecific系统Call
      if (syscall_num == 3) {
        // read
        // ModifyRead内容
      } else if (syscall_num == 5) {
        // open
        var path = Memory.readUtf8String(args[1]);
        console.log("[*] Opening file: " + path);

        // Intercept敏感FileRead
        if (path.includes("/proc/cpuinfo")) {
          // Return伪造cpuinfo
        }
      }
    },
  });

  // 2. Hook加固AfterSO
  var libjiagu = Process.getModuleByName("libjiagu.so");

  // 寻找关KeyFunction
  var init_array = libjiagu.enumerateSymbols();
  init_array.forEach(function (symbol) {
    if (symbol.name.includes("fingerprint")) {
      console.log("[*] Found fingerprint function: " + symbol.name);

      Interceptor.attach(symbol.address, {
        onEnter: function (args) {
          console.log("[*] Called: " + symbol.name);
        },
        onLeave: function (retval) {
          // 修改返回值
        },
      });
    }
  });
});
```

- 每个实例配置独立代理
- 实现完整的设备指纹模拟
- 模拟真实用户行为模式
- 成本：约 2 元/账号

* **教训\*\***：

1. **单纯的 Hook 不够**：需要完整的环境伪装
2. **设备一致性至关重要**：所有参数必须逻辑自洽
3. **行为模拟必不可少**：纯技术绕过容易被行为分析识破
4. **成本与收益平衡**：高质量绕过需要较高成本

因此，成功的绕过，本质上是一场关于"伪造一个天衣无缝的设备画像"的持久战。

<!-- 01-Recipes/Anti-Detection/frida_anti_debugging.md -->

# Recipe: 绕过 App 对 Frida 的检测

## 问题场景

**你遇到了什么问题？**

- ❌ 运行 Frida 后 App 立即崩溃或闪退
- ❌ App 显示"检测到调试工具"并拒绝运行
- ❌ Hook 脚本加载后 App 无响应或进入安全模式
- ❌ 某些功能在 Frida 环境下被禁用
- ❌ App 频繁弹窗提示"运行环境异常"

**本配方教你**：识别 Frida 检测技术、使用 Hook 绕过检测、定制 Frida 避免特征。

**核心理念**：

> 💡 **用 Frida 对抗检测 Frida** - 以子之矛攻子之盾
>
> - 在 App 检测之前就 Hook 检测函数
> - 修改检测结果让它"看不见" Frida
> - 或干脆隐藏 Frida 的所有特征

**预计用时**: 15-45 分钟（取决于检测复杂度）

---

## 工具清单

## # 必需工具

- - **Frida** - 动态插桩框架
- - **Android 设备**（已 Root）
- - **文本编辑器** - 编写绕过脚本

## # 可选工具

- - **jadx-gui** - 静态分析检测代码
- - **IDA Pro / Ghidra** - Native 层检测分析
- - **定制版 Frida** - 终极解决方案

---

## 前置条件

## # ✅ 确认清单

```bash
# 1. Frida 正常Run
frida-ps -U

# 2. 能正常 attach（NoDetectionWhen）
frida -U -f com.example.app

# 3. 根 权限可用
adb shell su

```

---

## 解决方案

## # 第 1 步：识别检测类型（5 分钟）

### 1.1 触发检测

**运行 Frida 并观察现象**：

```bash
# Use spawn 模式startup App
frida -U -f com.example.app --no-pause

# 观察输出和 App 行为

```

| 弹窗"检测到 Root/调试" | 模块名检测、线程名检测 | |
| 特定功能被禁用 | Inline Hook 检测 | |
| 随机崩溃/卡顿 | 多重检测组合 | |

### 1.2 静态分析检测代码（可选）

**用 jadx 搜索关键词**：

```
gum-js
27042

# 检测相关
/proc/self/maps
/proc/*/cmdline
pthread_create
connect
socket

```

```java
public static boolean isFridaDetected() {
// CheckPort
if (checkPort(27042)) return true;

// CheckProcess
if (findProcess("frida-server")) return true;

// CheckModule
if (checkMaps("frida-agent")) return true;

return false;
}

```

**重命名 frida-server**：

```bash
# Download frida-server
# 重命名为无害名字
mv frida-server-16.1.4-android-arm64 system_daemon

# push to device
adb push system_daemon /data/local/tmp/
adb shell "chmod 755 /data/local/tmp/system_daemon"

# UseNot标准Portstartup
adb shell "/data/local/tmp/system_daemon -l 0.0.0.0:8888 &"

```

frida -U -f com.example.app -l bypass.js --no-pause

# ❌ 不推荐：Attach 模式（检测代码可能已运行）

frida -U com.example.app -l bypass.js

````

```javascript
Java.perform(function () {
console.log("\n🛡️ [Frida Anti-Detection] 已启动\n");

// =====================================
// 1. 绕过端口扫描检测
// =====================================
var connect = Module.findExportByName("libc.so", "connect");
if (connect) {
Interceptor.attach(connect, {
onEnter: function (args) {
var sockaddr = ptr(args[1]);
var family = sockaddr.readU16();

if (family === 2) {
// AF_INET
var port = (sockaddr.add(2).readU8() << 8) | sockaddr.add(3).readU8();
var ip = sockaddr.add(4).readU32();

// 检测是否在扫描 Frida 默认端口
if (port === 27042 || port === 27043) {
console.log("✓ [Port] 拦截端口扫描: " + port);
// 修改端口为无效端口
sockaddr.add(2).writeU8(0xff);
sockaddr.add(3).writeU8(0xff);
}
}
},
});
console.log("✓ [Port] Hook connect() 完成");
}

// =====================================
// 2. Bypass /proc/self/maps Detection
// =====================================
var fopen = Module.findExportByName("libc.so", "fopen");
var fgets = Module.findExportByName("libc.so", "fgets");

if (fgets) {
Interceptor.attach(fgets, {
onEnter: function (args) {
this.buffer = args[0];
this.fp = args[2];
},
onLeave: function (retval) {
if (retval.isNull()) return;

var line = this.buffer.readCString();
if (line) {
// 隐藏 Frida 相关Module
if (
line.includes("frida") ||
line.includes("gum-js") ||
line.includes("frida-agent")
) {
console.log(
"✓ [Maps] 隐藏Module: " + line.substring(0, 50) + "..."
);
// 替换为False行
this.buffer.writeUtf8String("\n");
}
}
},
});
console.log("✓ [Maps] Hook fgets() 完成");
}

// =====================================
// 3. Bypass strstr StringDetection
// =====================================
var strstr = Module.findExportByName("libc.so", "strstr");
if (strstr) {
Interceptor.attach(strstr, {
onEnter: function (args) {
this.haystack = args[0].readCString();
this.needle = args[1].readCString();

if (
this.needle &&
(this.needle.includes("frida") ||
this.needle.includes("gum-js") ||
this.needle === "frida-agent" ||
this.needle === "frida-server")
) {
this.shouldBypass = true;
}
},
onLeave: function (retval) {
if (this.shouldBypass) {
console.log("✓ [Strstr] 隐藏String: " + this.needle);
retval.replace(ptr(0)); // 返回 空（未找到）
}
},
});
console.log("✓ [Strstr] Hook strstr() 完成");
}

// =====================================
// 4. Bypass Java LayerDetectionFunction
// =====================================
setTimeout(function () {
// Search常见DetectionFunctionName
var detectNames = [
"isFridaDetected",
"checkFrida",
"detectDebugger",
"isHooked",
"checkRoot",
];

Java.enumerateLoadedClasses({
onMatch: function (className) {
try {
var clazz = Java.use(className);
detectNames.forEach(function (methodName) {
if (clazz[methodName]) {
console.log(
"✓ [Java] 找到DetectionFunction: " +
className +
"." +
methodName
);
clazz[methodName].implementation = function () {
console.log(
"✓ [Java] InterceptCall: " + className + "." + methodName
);
return false; // 返回"未检测到"
};
}
});
} catch (e) {}
},
onComplete: function () {
console.log("✓ [Java] ClassEnumerate完成");
},
});
}, 500);

// =====================================
// 5. BypassThreadNameDetection
// =====================================
var pthread_setname_np = Module.findExportByName(
"libc.so",
"pthread_setname_np"
);
if (pthread_setname_np) {
Interceptor.attach(pthread_setname_np, {
onEnter: function (args) {
var threadName = args[1].readCString();
if (
threadName &&
(threadName.includes("gum-js") ||
threadName.includes("gmain") ||
threadName.includes("pool-"))
) {
console.log(
"✓ [Thread] ModifyThreadName: " + threadName + " → normal"
);
args[1].writeUtf8String("normal");
}
},
});
console.log("✓ [Thread] Hook pthread_setname_np() 完成");
}

console.log("\n🛡️ [Frida Anti-Detection] 所有 Hook 已就绪\n");
});

````

✓ [Maps] Hook fgets() 完成
✓ [Strstr] Hook strstr() 完成
✓ [Thread] Hook pthread_setname_np() 完成
✓ [Java] 类枚举完成
✓ [Java] 找到检测函数: com.example.SecurityCheck.isFridaDetected

🛡️ [Frida Anti-Detection] 所有 Hook 已就绪

✓ [Port] 拦截端口扫描: 27042
✓ [Strstr] 隐藏字符串: frida-agent
✓ [Java] 拦截调用: com.example.SecurityCheck.isFridaDetected

````

**如果你找到了检测函数**（从第 1 步）：

```javascript
Java.perform(function () {
var SecurityCheck = Java.use("com.example.app.SecurityCheck");

// Hook DetectionFunction
SecurityCheck.isFridaDetected.implementation = function () {
console.log("✓ Bypass isFridaDetected()");
return false; // 始终Return"未检测到"
};

// 拦截 其他Detection相关Function
SecurityCheck.checkPort.implementation = function (port) {
console.log("✓ Bypass checkPort(" + port + ")");
return false;
};
});

````

// RestoreFunctionoriginal 字节（Advanced）
var targetFunc = Module.findExportByName("libc.so", "strcmp");
if (targetFunc) {
// ReadoriginalBytecode（从磁盘上 libc.so）
var libcPath = "/system/lib64/libc.so";
var libcFile = new File(libcPath, "rb");
// ... ComplexRestoreLogic ...
}

````

### 5.1 修改源码

* *克隆 Frida**：

```bash
git clone --recurse-submodules https://github.com/frida/frida.git
cd frida

````

# 替换模块名

find . -type f -exec sed -i 's/frida-agent/system-agent/g' {} +
find . -type f -exec sed -i 's/frida-server/system-daemon/g' {} +

# 替换线程名

find . -type f -exec sed -i 's/gum-js-loop/normal-thread/g' {} +
find . -type f -exec sed -i 's/gmain/worker/g' {} +

```

# Compile
make

```

```
│ ├── ProcessName: frida-server
│ └── Command行ParameterContains "frida"
├── 3. MemoryLayer
│ ├── ModuleName: frida-agent.so, frida-gadget.so
│ ├── ThreadName: gum-js-loop, gmain, pool-*
│ └── Function Hook: Modify系统FunctionBytecode
└── 4. 行为Layer
└── D-Bus 消息、Exception系统Call序列

```

| 进程名检测 | 重命名 frida-server | |
| /proc/self/maps | Hook `fgets()` 过滤输出 | |
| 字符串检测 | Hook `strstr()` 返回 NULL | |
| 线程名检测 | Hook `pthread_setname_np()` | |
| Inline Hook 检测 | Hook 检测函数本身 | |
| 多重组合检测 | 定制 Frida 源码 | |

## # Hook 时机很重要

```
↓
[0.5s] App 静态初始化代码运行
↓
[1s] App onCreate() 开始
↓
[1.5s] ⚠️ 反调试检测通常在此运行
↓
[2s] ❌ Attach 模式：Frida 在此时才注入（太晚）

```

**症状**：Hook 脚本运行了，但 App 仍然检测到 Frida

**可能原因**：

1. **Hook 时机太晚**

```bash
# ✅ 正确：--no-pause 立即运行
frida -U -f com.example.app -l bypass.js --no-pause

# ❌ 错误：会暂停等待手动恢复
frida -U -f com.example.app -l bypass.js

```

→ 使用 `frida-gadget` 而非 `frida-server`（更早注入）

→ 使用 `frida-gadget` 而非 `frida-server`（更早注入）

3. **存在未覆盖的检测点**
   → 使用 jadx 分析完整的检测逻辑

→ 使用 jadx 分析完整的检测逻辑

## # ❌ 问题 2: Hook 后 App 崩溃

**症状**：加载 Hook 脚本后 App 立即崩溃

**检查**：

1. **Hook 的函数签名错误**

```javascript
// Check重载
Java.use("ClassName").methodName.overloads.forEach(function (o) {
  console.log(o);
});
```

```javascript
// ❌ Error
SomeClass.returnsInt.implementation = function () {
  return "string"; // ClassTypeError！
};

// ✅ 正确
SomeClass.returnsInt.implementation = function () {
  return 0;
};
```

→ 添加条件判断，只 Hook 特定情况

→ 添加条件判断，只 Hook 特定情况

## # ❌ 问题 3: 某些检测绕不过去

**症状**：尝试了所有方法，仍有检测未绕过

**高级对策**：

1. **使用 frida-gadget（嵌入式）**

```bash
# 解包 APK
apktool d app.apk

# Will frida-gadget.so Add to lib/
# Modify androidManifest.xml And smali CodeLoad gadget
# 参考：https://frida.re/docs/gadget/

# Re-打Package
apktool b app -o app_patched.apk

```

3. **逆向检测逻辑并 Patch APK**

   ```bash

   ```

# 直接修改检测函数返回值

# 用 jadx 找到 .smali 代码

# 修改返回指令为返回 0

# 重新打包

````

**症状**：按照教程编译 Frida 时出错

**解决**：

1. **使用预编译的定制版**

- 社区项目：https://github.com/hluwa/strongR-frida-android
- 已重命名所有特征字符串

- 社区项目：https://github.com/hluwa/strongR-frida-android
- 已重命名所有特征字符串

2. **使用 Docker 编译环境**

```bash
docker run --rm -v $(pwd):/work frida/ci

````

- 不要全局替换，容易破坏代码
- 只修改：端口号、模块名、线程名

- 不要全局替换，容易破坏代码
- 只修改：端口号、模块名、线程名

---

## 延伸阅读

## # 相关配方

- **[Root 检测绕过](./device_fingerprinting_and_bypass.md)** - 通常与 Frida 检测一起出现
- **[SSL Pinning 绕过](../Network/network_sniffing.md#第-5-步绕过-ssl-pinning如遇到)** - 可能也有反 Frida
- **[模拟器检测绕过](./device_fingerprinting_and_bypass.md)** - 多重检测组合

## # 工具深入

- **[Frida 完整指南](../../02-Tools/Dynamic/frida_guide.md)**
- **[Frida 内部原理](../../02-Tools/Dynamic/frida_internals.md)** - 理解检测原理

## # 案例分析

- **[反分析技术案例](../../03-Case-Studies/case_anti_analysis_techniques.md)**
- **[社交媒体风控](../../03-Case-Studies/case_social_media_and_anti_bot.md)** - 高级检测对抗

## # 进阶资源

- **strongR-frida**: https://github.com/hluwa/strongR-frida-android
- **frida-gadget 文档**: https://frida.re/docs/gadget/
- **编译 Frida**: https://frida.re/docs/building/

---

## 快速参考

## # 一键绕过脚本

**下载通用绕过脚本**：

```bash
# 使用社区维护的 BypassScript
curl -O https://raw.githubusercontent.com/0xdea/frida-scripts/master/raptor_frida_android_bypass.js

# Run the command
frida -U -f com.example.app -l raptor_frida_android_bypass.js --no-pause

```

| 进程名 | `/proc/*/cmdline` | 重命名 + Hook `fopen()` |
| 模块名 | `/proc/self/maps` | Hook `fgets()` 过滤 |
| 字符串 | `strstr()` | Hook `strstr()` |
| 线程名 | `/proc/self/task/*/comm` | Hook `pthread_setname_np()` |
| Java 检测 | `isFridaDetected()` | Hook 检测函数 |

## # 常用命令

```bash
# 非标准端口运行 frida-server
adb shell "/data/local/tmp/frida -l 0.0.0.0:8888 &"

# 连接 to to to to to to Not标准Port
frida -H 127.0.0.1:8888 -f com.example.app

# Spawn mode（重要）
frida -U -f com.example.app -l bypass.js --no-pause

# 列表 allModule（CheckIsNo有 frida-agent）
frida -U -f com.example.app -e 'Process.enumerateModules()'

# List allThread（CheckThreadName）
frida -U -f com.example.app -e 'Process.enumerateThreads()'

```

<!-- 01-Recipes/Anti-Detection/mobile_app_sec_and_anti_bot.md -->

# 移动端安全与风控技术

现代移动应用，特别是那些处理敏感用户数据或有价值业务逻辑的应用，通常会实现多层安全机制来防御逆向工程、篡改和自动化滥用（机器人）。这一领域通常被称为"RASP"（运行时应用自我保护）或"反机器人技术"。

本文档概述了常见的技术。

---

## 关键防御类型

### 1. 反调试与反分析

这些技术旨在检测并阻止像调试器和插桩框架这样的分析工具。

- **调试器检测**:
- 检查 `/proc/self/status` 中的 `TracerPid`。一个非零值表示有调试器附加。

- 使用 `ptrace(PTRACE_TRACEME, 0, NULL, NULL)` 并检查返回值是否小于 0。

- 时间检查：测量执行一段代码所需的时间。如果附加了调试器（带有断点），时间将会有显著不同。
- **Frida 检测**:
- 扫描内存中是否存在 `frida-agent` 或 `frida-gadget` 库。

- 通过尝试连接其默认端口（27042）来检测 Frida 的服务器。

- 检查 Frida 特有的痕迹，如命名管道（`frida-pipe`）或对 `REPL` 环境的修改。
- **模拟器/Root 检测**:
- 检查已知的模拟器特有文件、属性（`ro.kernel.qemu`）或设备驱动。

- 检查是否存在 root 管理应用（如 SuperSU）或 `su` 二进制文件。

### 2. 反篡改

这些技术确保应用的代码和数据未被修改。

- **代码完整性校验**: 在运行时计算 `classes.dex` 文件或原生库（`.so`）的校验和或哈希值（例如 SHA-256），并与安全存储的已知良好值进行比较。

- **签名验证**: 在运行时，获取应用自身的签名并验证其是否与官方开发者签名匹配。这可以防止重打包。

- **内存完整性校验**: 定期扫描应用自身的内存，以确保关键函数未被 Frida 等工具钩住或修补。

### 3. 反机器人与业务逻辑保护

这些技术旨在防止自动化脚本滥用应用的 API 或功能（例如，创建垃圾账户、抓取数据）。

- **设备证明**: 使用像 Android 的 `SafetyNet` / `Play Integrity` API 这样的服务，从谷歌服务器获取一个加密证明，证明设备是真实的、非 root 的，并且正在运行官方应用。这非常难以绕过。

- **请求签名**: 关键的 API 请求通常受"签名"保护。这个签名是根据请求参数、时间戳、随机数和一个密钥计算出的哈希值（例如 HMAC-SHA256）。密钥通常使用混淆等技术隐藏起来。逆向这个签名算法是分析师的一个常见目标。

- **行为分析**: 在服务器端，分析 API 调用的*时间*和*顺序*，以建立真实用户的行为画像。机器人通常具有非常僵硬、非人类的时间模式，可以用来检测它们。

---

## 绕过策略

绕过这些防御需要结合静态和动态分析。

- **钩子与补丁**: 使用 Frida 钩住负责这些检查的函数，并强制它们返回一个"安全"的值。例如，钩住读取 `TracerPid` 的函数，使其总是返回 0。

- **自定义 Frida 版本**: 为了对抗 Frida 检测，你可以编译一个自定义名称和不同默认端口的 `frida-server` 版本。

- **静态分析**: 反汇编应用以找到检查逻辑。一旦找到，你通常可以将其"nop"掉（用 `NOP` 指令替换），以永久禁用它。

<!-- 01-Recipes/Anti-Detection/xposed_anti_debugging.md -->

# Recipe: 绕过应用的 Xposed 检测

## 问题场景

你可能遇到以下情况：

1. **App 启动即退出**：App 启动后弹出"检测到 Xposed 框架，禁止运行"，随即闪退
2. **功能受限**：金融/支付类 App 检测到 Xposed 后拒绝提供服务（无法转账、支付）
3. **账号封禁**：游戏检测到 Xposed 环境后触发风控，导致封号
4. **分析受阻**：需要在 Xposed 环境下分析 App 行为，但被反调试拦截
5. **通用方案失效**：已经使用 RootCloak Plus 等通用隐藏模块，但仍被检测到

## 工具清单

## # 必需工具

- ☐ **Xposed 框架**：EdXposed 或 LSPosed（推荐 LSPosed，更稳定）
- ☐ **Root 设备**：已 Root 的 Android 设备或模拟器（如 Genymotion）
- ☐ **目标 APK**：需要绕过检测的应用安装包
- ☐ **Xposed 模块开发环境**：Android Studio（用于编写自定义绕过模块）

## # 可选工具

- ☐ **JEB/Jadx**：反编译工具，用于分析 App 的检测代码
- ☐ **RootCloak Plus**：通用 Xposed/Root 隐藏模块（快速测试）
- ☐ **Hide My Applist**：高级应用列表和框架隐藏工具
- ☐ **MT Manager**：Android 文件管理器，查看系统文件
- ☐ **Xposed 源码**：EdXposed 源码（定制化框架需求）

## 前置条件

开始之前，请确认：

- ✅ **已安装 Xposed 框架**：设备上已刷入 EdXposed 或 LSPosed，并能正常使用
- ✅ **设备已 Root**：拥有 Root 权限，或使用虚拟化方案（如 VirtualXposed）
- ✅ **能反编译 APK**：会使用 Jadx/JEB 查看 Java 代码
- ✅ **了解 Xposed Hook 基础**：知道如何编写简单的 Xposed 模块（可参考 [Xposed Guide](../../02-Tools/Dynamic/xposed_guide.md)）
- ✅ **了解 Java 反射机制**：理解 `Class.forName()`, `ClassLoader` 等概念

## 解决方案

## # 第 1 步：识别检测类型（15-30 分钟）

首先需要确定 App 使用了哪种检测方法，这决定了后续的绕过策略。

### 方法 1：观察运行行为

运行目标 App，观察异常行为的时机和特征：

| 异常时机                       | 可能的检测类型                        |
| ------------------------------ | ------------------------------------- |
| **启动阶段立即崩溃/退出**      | 调用栈检测（Application.onCreate 中） |
| **特定功能（登录、支付）受限** | 关键方法处的定点检测                  |
| **延迟几秒后弹出警告**         | 定时器或异步线程中的检测              |
| **随机触发**                   | 多点分散检测或混淆后的检测            |

### 方法 2：静态分析检测代码

使用 Jadx 反编译 APK，搜索 Xposed 检测的特征字符串：

```bash
# 反编译 APK
jadx -d ./decompiled target.apk

# 搜索 Xposed 相关特征
cd decompiled
grep -r "xposed" --include="*.java" .
grep -r "XposedBridge" --include="*.java" .
grep -r "de.robv.android" --include="*.java" .

# SearchDetectionMethodCall
grep -r "getStackTrace" --include="*.java" .
grep -r "Class.forName" --include="*.java" .
grep -r "/proc/self/maps" --include="*.java" .

```

// 特征 Code
try {
throw new Exception("Xposed Detection");
} catch (Exception e) {
for (StackTraceElement element : e.getStackTrace()) {
if (element.getClassName().contains("de.robv.android.xposed")) {
// Xposed Detected!
return true;
}
}
}

```
try {
Class.forName("de.robv.android.xposed.XposedBridge");
// If 没抛 anomaly，Desc Xposed exists at
return true;
} catch (ClassNotFoundException e) {
return false;
}

```

if (xposedJar.exists()) {
// Xposed Detected!
}

````
FILE* fp = fopen("/proc/self/maps", "r");
// Read内容并查找 "libxposed_art.so" or "XposedBridge"

```
void* handle = dlopen("libart.so", RTLD_NOW);
void* sym = dlsym(handle, "_ZN3art9ArtMethod6InvokeEPNS_6ThreadEPjjPNS_6JValueEPKc");
// 检查 if 地址 is 在非标准内存区域

````

|---------|---------|-------|------|
| Java 层调用栈检测 | Hook `StackTraceElement.getClassName()` | 90% | 30min |
| Java 层类加载检测 | Hook `Class.forName()` | 85% | 20min |
| 文件系统检测 | Hook `File.exists()` | 95% | 20min |
| Native 层 maps 检测 | Hook `fopen()` / 定制框架 | 60% | 2-4h |
| 综合检测（多种方法） | 定制化 Xposed 框架 | 80% | 4h+ |

**决策树**：

```

快速测试需求或不想写代码
└─→ Strategy B：Use现成隐藏Module（最快）

```

创建 `AntiXposedDetection.java`：

```java
package com.example.antidetect;

import android.os.Bundle;
import de.robv.android.xposed.*;
import de.robv.android.xposed.callbacks.XC_LoadPackage.LoadPackageParam;
import java.io.File;

public class AntiXposedDetection implements IXposedHookLoadPackage {

// Modify为你TargetAppPackageName
private static final String TARGET_PACKAGE = "com.target.app";

@Override
public void handleLoadPackage(LoadPackageParam lpparam) throws Throwable {
// Only Hook TargetApp
if (!lpparam.packageName.equals(TARGET_PACKAGE)) return;

XposedBridge.log("[AntiDetect] Start Hook " + TARGET_PACKAGE);

// BypassCall栈Detection
hookStackTrace();

// BypassClassLoadDetection
hookClassForName();

// BypassFile系统Detection
hookFileExists();

// Bypass系统PropertyDetection
hookSystemProperties();

XposedBridge.log("[AntiDetect] 所有 Hook 已激活");
}

/**
* BypassCall栈Detection
* 原理：Modify StackTraceElement.getClassName() ReturnValue
* /
private void hookStackTrace() {
XposedHelpers.findAndHookMethod(
StackTraceElement.class,
"getClassName",
new XC_MethodHook() {
@Override
protected void afterHookedMethod(MethodHookParam param) throws Throwable {
String originalClassName = (String) param.getResult();

// 如果类名包含 xposed 特征，替换为No害系统Class
if (originalClassName != null &&
originalClassName.toLowerCase().contains("xposed")) {
param.setResult("com.android.internal.os.ZygoteInit");
XposedBridge.log("[AntiDetect] 隐藏调用栈: " + originalClassName);
}
}
}
);
}

/**
* BypassClassLoadDetection
* 原理：Intercept Class.forName() Call，对 Xposed Class抛出 ClassNotFoundException
* /
private void hookClassForName() {
XposedHelpers.findAndHookMethod(
Class.class,
"forName",
String.class,
new XC_MethodHook() {
@Override
protected void beforeHookedMethod(MethodHookParam param) throws Throwable {
String className = (String) param.args[0];

// If尝试Load Xposed 相关Class，抛出 ClassNotFoundanomaly
if (className != null &&
(className.contains("xposed") ||
className.contains("Xposed") ||
className.contains("EdXposed") ||
className.contains("LSPosed"))) {
param.setThrowable(new ClassNotFoundException(className));
XposedBridge.log("[AntiDetect] 阻止LoadClass: " + className);
}
}
}
);

// 也 拦截 三ParameterVersion forName
XposedHelpers.findAndHookMethod(
Class.class,
"forName",
String.class,
boolean.class,
ClassLoader.class,
new XC_MethodHook() {
@Override
protected void beforeHookedMethod(MethodHookParam param) throws Throwable {
String className = (String) param.args[0];
if (className != null && className.toLowerCase().contains("xposed")) {
param.setThrowable(new ClassNotFoundException(className));
}
}
}
);
}

/**
* BypassFile系统Detection
* 原理：Modify File.exists() ReturnValue，隐藏 Xposed 特征File
* /
private void hookFileExists() {
XposedHelpers.findAndHookMethod(
File.class,
"exists",
new XC_MethodHook() {
@Override
protected void afterHookedMethod(MethodHookParam param) throws Throwable {
File file = (File) param.thisObject;
String path = file.getAbsolutePath();

// Xposed 特征FileList
String[] xposedPaths = {
"XposedBridge",
"xposed",
"de.robv.android.xposed",
"EdXposed",
"LSPosed",
"libxposed",
"libedxposed",
"liblspd"
};

// 检查 if 路径 is Contains特征
for (String keyword : xposedPaths) {
if (path.contains(keyword)) {
param.setResult(false); // 伪装文件不存在
XposedBridge.log("[AntiDetect] 隐藏File: " + path);
return;
}
}
}
}
);
}

/**
* Bypass系统PropertyDetection
* 原理：Intercept System.getProperty() Call
* /
private void hookSystemProperties() {
XposedHelpers.findAndHookMethod(
System.class,
"getProperty",
String.class,
new XC_MethodHook() {
@Override
protected void afterHookedMethod(MethodHookParam param) throws Throwable {
String key = (String) param.args[0];

// VirtualXposed Etc会settingss特殊Property
if (key != null &&
(key.contains("xposed") ||
key.contains("vxp") ||
key.equals("ro.build.version.xposed"))) {
param.setResult(null); // Return null
XposedBridge.log("[AntiDetect] 隐藏系统Property: " + key);
}
}
}
);
}
}

```

│ │ ├── AndroidManifest.xml
│ │ ├── assets/
│ │ │ └── xposed_init # 入口类声明
│ │ └── java/com/example/antidetect/
│ │ └── AntiXposedDetection.java
│ └── build.gradle
└── build.gradle

```
package="com.example.antidetect">

<application
android:allowBackup="true"
android:label="Anti Xposed Detection"
android:icon="@mipmap/ic_launcher">

<!-- Xposed Module声明 -->
<meta-data
android:name="xposedmodule"
android:value="true" />
<meta-data
android:name="xposeddescription"
android:value="Hide Xposed from target app" />
<meta-data
android:name="xposedminversion"
android:value="54" />
</application>
</manifest>

```

./gradlew assembleRelease

# 2. Install 到设备

adb install app/build/outputs/apk/release/app-release.apk

# 3. At LSPosed/EdXposed In 激活 Module

# - Open LSPosed Manager

# - Module → 找到 "Anti Xposed 检测"

# - 勾选 Enabled，并 AtScopeInAddTarget App

# - 重启 Target App

# 4. ViewLogValidate

adb logcat -s Xposed:V | grep AntiDetect

````

1. **Hide My Applist**（最强大，推荐）
- 下载：[GitHub](https://github.com/Dr-TSNG/Hide-My-Applist)
- 功能：隐藏应用列表、Xposed 框架、Root
- 支持黑白名单、模板系统

- 下载：[GitHub](https://github.com/Dr-TSNG/Hide-My-Applist)
- 功能：隐藏应用列表、Xposed 框架、Root
- 支持黑白名单、模板系统


2. **XposedChecker Bypass**
- 专门针对 XposedChecker 这类检测工具
- 覆盖常见检测点

- 专门针对 XposedChecker 这类检测工具
- 覆盖常见检测点


3. **RootCloak Plus**（老牌模块）
- 同时隐藏 Root 和 Xposed
- 配置简单，但对新型检测效果较差

- 同时隐藏 Root 和 Xposed
- 配置简单，但对新型检测效果较差


* *使用步骤（以 Hide My Applist 为例）**：

```bash
# 1. Download并Install
# 从 GitHub 发布 Download最新 APK
adb install HideMyApplist.apk

# 2. At LSPosed In激活
# LSPosed 管理器 → Module → Hide My Applist → 勾选Enabled

# 3. Config隐藏规则
# Open Hide My Applist App
# → 模板Manage → 新建模板
# → 选择隐藏内容：
# 黑名单模式（隐藏 Xposed 相关）
# 隐藏 Xposed Module
# 隐藏系统框架
# → AppManage → 选择Target App → App模板

# 4. 重启Target App
adb shell am force-stop com.target.app
adb shell am start -n com.target.app/.MainActivity

````

- 包名：`de.robv.android.xposed` → `com.myfw.custom`
- 类名：`XposedBridge` → `CustomBridge`
- 文件名：`libxposed_art.so` → `libcustom_art.so`
- 系统属性：`persist.xposed.*` → `persist.myfw.*`

* **详细步骤**：

* **1. 获取 Xposed 源码**：

```bash
# 克隆 EdXposed 源码（推荐，比原版 Xposed 更活跃）
git clone --recursive https://github.com/ElderDrivers/EdXposed
cd EdXposed

# 也可以克隆 LSPosed（更现代实现）
git clone --recursive https://github.com/LSPosed/LSPosed

```

# 全局替换 Xposed 特征为自 DefineName 称

OLD_PACKAGE="de.robv.android.xposed"
NEW_PACKAGE="com.myframework.custom"

OLD_CLASS="Xposed"
NEW_CLASS="Custom"

OLD_LIB="xposed"
NEW_LIB="myfw"

echo "Start 替换 Xposed 特征..."

# 1. 替换 PackageName

echo "替换 PackageName..."
find . -type f \( -name "_.java" -o -name "_.cpp" -o -name "\*\*.h" \) \

- exec sed -i "s/$OLD_PACKAGE/$NEW_PACKAGE/g" {} +

# 2. 替换 ClassName

echo "替换 ClassName..."
find . -type f -name "\_.java" \

- exec sed -i "s/${OLD_CLASS}Bridge/${NEW*CLASS}Bridge/g" {} +
  find . -type f -name "*.java" \
- exec sed -i "s/${OLD_CLASS}Helpers/${NEW_CLASS}Helpers/g" {} +

# 3. renameFile

echo "重命 NameFile..."
find . -name "_Xposed_" | while read file; do
newfile=$(echo "$file" | sed "s/Xposed/Custom/g")
mv "$file" "$newfile" 2>/dev/null
done

# 4. 替换 LibraryFileName

echo "替换 Native LibraryName..."
find . -type f \( -name "_.cpp" -o -name "_.mk" -o -name "CMakeLists.txt" \) \

- exec sed -i "s/lib${OLD_LIB}/lib${NEW_LIB}/g" {} +

# 5. 替换系统 PropertyName

echo "替换系统 Property..."
find . -type f \( -name "_.cpp" -o -name "_.java" \) \

- exec sed -i "s/persist.xposed/persist.myfw/g" {} + - exec sed -i "s/ro.xposed/ro.myfw/g" {} +

echo "✓ 特征替换完成！"
echo "请 ManualCheck 以下 FileIsNo 正确："
echo " - AndroidManifest.xml"
echo " - module.prop (Magisk ModuleConfig)"
echo " - build.gradle"

```
name=Custom Framework (Xposed)
version=v1.0.0
versionCode=1
author=YourName
description=Customized Xposed Framework with renamed signatures
minMagisk=21000

```

# 执行替换

./rename_xposed.sh

# 编译（以 EdXposed 为例）

cd EdXposed
./gradlew :edxp-core:buildAll

# 输出位于 在外/edxp-core/发布/

# 获取 a .zip 文件，CanAt Magisk In 刷入

```

# 方法 1：通过 Magisk 管理器 Install
# 打开 Magisk 管理器 → Module → 从NativeInstall → 选择 ZIP

# 方法 2：通过 TWRP Recovery 刷入（If有）
# adb reboot recovery
# 在内 TWRP, 选择 Install → 选择 ZIP → 滑动确认

# 重启设备
adb reboot

```

- ☐ **Xposed Hook 依然生效**：你的 Hook 模块能正常 Hook 目标方法
- ☐ **检测工具显示干净**：使用 XposedChecker 等工具测试，显示未检测到

* **验证方法**：

* **1. 编写测试 Xposed 模块**：

```java
// 验证 拦截 IsNo生效
XposedHelpers.findAndHookMethod(
"com.target.app.MainActivity",
lpparam.classLoader,
"onCreate",
Bundle.class,
new XC_MethodHook() {
@Override
protected void afterHookedMethod(MethodHookParam param) throws Throwable {
XposedBridge.log("✓ Hook 成功！App 未检测到 Xposed");
// 可选：弹出 Toast 提示
// Toast.makeText(context, "Xposed Hook Active", Toast.LENGTH_SHorT).show();
}
}
);

```

# 查看 App 是否有检测相关日志

adb logcat | grep -i "xposed\|detect\|security\|check"

# Should see：

# - Hook 成功 Log

# - 没有检测相关错误日志

```

# Run and view Result
# IfBypassSuccess，Should display "Xposed: Not Detected"

```

└─→ TestCoreBusiness（支付/游戏/View 敏感 Info）
└─→ 观察 IsNo 触发风控 OrException

```
当 Xposed Hook 一个方法时，实际的调用链是：

```

**3. 文件系统特征**：
Xposed 需要在系统中安装文件：

- `/system/framework/XposedBridge.jar`
- `/system/lib/libxposed_art.so` 或 `/system/lib64/libxposed_art.so`

**4. 内存映射特征**：
进程的内存映射（`/proc/self/maps`）中会出现 Xposed 相关的库：

```

关键技术点：

1. **拦截检测方法的执行**：在检测代码执行前 Hook，修改其行为
2. **修改返回值**：让检测方法总是返回"未检测到"的结果
3. **过滤特征字符串**：将包含 "xposed" 的字符串替换为无害字符串
4. **阻止异常抛出**：对于 `Class.forName()` 这类检测，主动抛出 `ClassNotFoundException`

**示例：调用栈检测的绕过原理**

```

Hook After（BypassDetection）：
App Call getStackTrace()
→ Return [MainActivity, XposedBridge, ZygoteInit, ...]
→ 我们 Hook Intercept getClassName()
→ Will "XposedBridge" 替换为 "ZygoteInit"
→ App Only 看到 [MainActivity, ZygoteInit, ZygoteInit, ...]
→ DetectionFailed（未发现 Xposed）

```
| 类加载检测 | `Class.forName("de.robv...XposedBridge")` | 包名改为 `com.myfw...CustomBridge` | ✅ 检测失败 |
| 文件检测 | `/system/framework/XposedBridge.jar` | 文件名改为 `CustomBridge.jar` | ✅ 检测失败 |
| maps 检测 | 搜索 `libxposed_art.so` | 库名改为 `libcustom_art.so` | ✅ 检测失败 |

**缺点**：

- 维护成本高，需要跟随官方 Xposed 更新
- 编译过程复杂，需要配置 Android NDK
- 部分依赖原版 Xposed API 的模块可能不兼容

## 常见问题

## # ❌ 问题 1：Hook 模块激活后，App 仍然检测到 Xposed

**症状**：

```

2. **Native 层检测**：App 使用 JNI 检测，Java Hook 无法拦截
3. **遗漏的检测点**：App 使用了你没有覆盖的检测方法
4. **Hook 作用域未配置**：LSPosed 中未将目标 App 加入作用域

- **解决方案\*\***：

- **方案 1：提前 Hook 时机\*\***

```java
// At Application.attachBaseContext() In提Before 拦截
XposedHelpers.findAndHookMethod(
"com.target.app.MyApplication",
lpparam.classLoader,
"attachBaseContext",
Context.class,
new XC_MethodHook() {
@Override
protected void beforeHookedMethod(MethodHookParam param) throws Throwable {
// At Application InitializeBefore就 拦截 所有DetectionMethod
hookAllDetectionMethods(lpparam);
XposedBridge.log("[AntiDetect] Early hooks installed");
}
}
);

```

// Frida Script：Hook fopen() Intercept maps FileRead
Interceptor.attach(Module.findExportByName("libc.so", "fopen"), {
onEnter: function(args) {
var path = Memory.readUtf8String(args[0]);
if (path === "/proc/self/maps") {
console.log("[*] fopen() called for /proc/self/maps");
// 重定向到一干净 maps 文件
args[0] = Memory.allocUtf8String("/data/local/tmp/fake_maps");
}
}
});

```
// Call native MethodDo inline hook
nativeHookFopen();

```

cd decompiled

# 搜索所有可能检测模式

grep -rn "getStackTrace\|forName\|/proc/self/maps\|XposedBridge\|exists()" . \

- -include="\*\*.java" > detection_points.txt

```
adb shell "su -c 'ls /data/adb/lspd/config/modules/'"
# Should see你Module ID

# CheckScopeConfig
# LSPosed 管理器 → Module → 你Module → AppScope
# 确保目标 App 已勾选

```

- META-INF 目录下的脚本缺失
- 编译过程中出错，生成的 ZIP 损坏

* **解决方案\*\***：

* **方案 1：检查 ZIP 结构\*\***

```bash
# DecompressView结构
unzip -l edxp-custom.zip

# 标准 Magisk Module结构：
# META-INF/
# com/google/android/
# update-binary # InstallScript
# updater-script # 空文件即可
# module.prop # ModuleConfig
# system/ # 系统文件
# framework/
# CustomBridge.jar
# lib64/
# libcustom_art.so
# riru/ # Riru 相关（IfUse Riru）

```

id=custom_xposed
name=Custom Xposed Framework
version=v1.0.0
versionCode=100
author=YourName
description=Customized Xposed with renamed signatures

# OptionalField

minMagisk=21000
maxMagisk=99999

```
mkdir -p magisk_module/system/framework
mkdir -p magisk_module/system/lib64

# ReplicationFile
cp update-binary magisk_module/META-INF/com/google/android/
touch magisk_module/META-INF/com/google/android/updater-script
cp module.prop magisk_module/
cp CustomBridge.jar magisk_module/system/framework/
cp libcustom_art.so magisk_module/system/lib64/

# Package（注意：MustAtModuleDirectory内打Package）
cd magisk_module
zip -r ../custom-xposed-magisk.zip .
cd ..

# 推送并安装
adb push custom-xposed-magisk.zip /sdcard/
# In Magisk Manager, Install

```

# 在内 TWRP, ：Install → 选择 ZIP → 滑动确认

```

```

- **解决方案**：

- **方案 1：精准 Hook，缩小作用范围**

❌ **错误示范：全局 Hook**

```java
// 这样会影响所有类加载，包括正常业务
XposedHelpers.findAndHookMethod(Class.class, "forName", String.class, ...);

```

"com.target.app.security.SecurityChecker",
lpparam.classLoader,
"checkXposed",
new XC_MethodReplacement() {
@Override
protected Object replaceHookedMethod(MethodHookParam param) {
XposedBridge.log("[AntiDetect] checkXposed() blocked");
return false; // 返回"未检测到"
}
}
);

```
String className = (String) param.getResult();

// OnlyFilter Xposed 相关，不影响其他Class
if (className != null && className.toLowerCase().contains("xposed")) {
param.setResult("android.app.Activity");
}
// 其他情况保持原样，不做Modify
}

```

// 一次 OnlyEnabled 一 拦截，TestIsNo 导致崩溃
hookStackTrace(); // Test：OK
// hookClassForName(); // 暂 WhenComment 掉
// hookFileExists(); // 暂 WhenComment 掉

// 逐个启用并测试，找出导致崩溃 拦截

}

```

// 确保ReturnValueClassType匹配
@Override
protected void afterHookedMethod(MethodHookParam param) {
// If原MethodReturn boolean，你也MustReturn boolean
param.setResult(false); // ✅ 正确
// param.setResult("假"); // ❌ 错误！ClassType不匹配
}

```

- `assets/xposed_init` 文件缺失或路径错误
- `AndroidManifest.xml` 中缺少 Xposed 元数据声明
- 模块入口类的包名/类名与 `xposed_init` 中不一致
- LSPosed 缓存未刷新

**解决方案**：

**方案 1：检查 `assets/xposed_init` 文件**

```bash
# 确认文件存在
unzip -l app-release.apk | grep xposed_init
# Should see: assets/xposed_init

# 检查内容（必须是完整类名，无文件扩展名）
unzip -p app-release.apk assets/xposed_init
# OutputShouldIs：com.example.antidetect.AntiXposedDetection

```

✅ assets/xposed_init # 正确

```
<!-- 必须有这三个 meta-data -->
<meta-data
android:name="xposedmodule"
android:value="true" />
<meta-data
android:name="xposeddescription"
android:value="Hide Xposed from detection" />
<meta-data
android:name="xposedminversion"
android:value="54" />
</application>

```

# 检查 if 入口 Class is exists at

ls -l ./decompiled/com/example/antidetect/AntiXposedDetection.java

# 确认类实现了 IXposedHookLoadPackage 接口

grep "implements IXposedHookLoadPackage" \
./decompiled/com/example/antidetect/AntiXposedDetection.java

```

# 清除 LSPosed 缓存
adb shell "su -c 'rm -rf /data/adb/lspd/cache/*'"

# Re-Install
adb install app-release.apk

# 重启 LSPosed（or重启设备）
adb shell "su -c 'killall -9 com.android.systemui'"
# or
adb reboot

# 打开 LSPosed 管理器，Should能看到Module

```

- [逆向工程工作流](../Analysis/re_workflow.md) - 完整的逆向分析流程

* **工具深入**：

- [Xposed 使用指南](../../02-Tools/Dynamic/xposed_guide.md) - Xposed 框架基础使用
- [Xposed 内部原理](../../02-Tools/Dynamic/xposed_internals.md) - Xposed 工作机制详解
- [Frida 使用指南](../../02-Tools/Dynamic/frida_guide.md) - Frida 与 Xposed 协同使用

* **参考资料**：

- [Android 沙箱实现](../../04-Reference/Advanced/android_sandbox_implementation.md) - 虚拟化环境中使用 Xposed
- [ART 运行时](../../04-Reference/Foundations/art_runtime.md) - 理解 Xposed 如何修改 ART

* **案例分析**：

- [Anti Analysis Techniques](../../03-Case-Studies/case_anti_analysis_techniques.md) - 综合反分析技术案例
- [Social Media & Anti Bot](../../03-Case-Studies/case_social_media_and_anti_bot.md) - 社交应用的 Xposed 检测

## 快速参考

## # Xposed 检测方法速查表

| 检测类型     | 检测层级    | 特征代码                                            | 绕过方法                    | Hook 目标                          |
| ------------ | ----------- | --------------------------------------------------- | --------------------------- | ---------------------------------- |
| 调用栈检测   | Java        | `getStackTrace()` + `contains("xposed")`            | Hook 返回值过滤             | `StackTraceElement.getClassName()` |
| 类加载检测   | Java        | `Class.forName("XposedBridge")`                     | 抛出 ClassNotFoundException | `Class.forName()`                  |
| 已加载类检测 | Java        | `ClassLoader.loadClass(...)`                        | 同上                        | `ClassLoader.loadClass()`          |
| 文件检测     | Java        | `new File("/system/.../XposedBridge.jar").exists()` | 返回 false                  | `File.exists()`                    |
| maps 检测    | Native      | `fopen("/proc/self/maps")` + `strstr("libxposed")`  | Hook fopen 或定制框架       | `libc.fopen()`                     |
| 系统属性检测 | Java/Native | `System.getProperty("vxp_...")`                     | 返回 null                   | `System.getProperty()`             |
| 符号地址检测 | Native      | `dlsym(...)` 检查地址异常                           | 定制框架                    | N/A（需源码修改）                  |

## # 完整绕过模块模板（一键使用）

保存为 `AntiXposedBypass.java`，修改包名和目标 App 即可使用：

```java
package com.example.antidetect;

import de.robv.android.xposed.*;
import de.robv.android.xposed.callbacks.XC_LoadPackage.LoadPackageParam;
import java.io.File;

public class AntiXposedBypass implements IXposedHookLoadPackage {

private static final String TARGET = "com.target.app"; // 改为你Target App

@Override
public void handleLoadPackage(LoadPackageParam lpparam) throws Throwable {
if (!lpparam.packageName.equals(TARGET)) return;

XposedBridge.log("[Bypass] Hooking " + TARGET);

// 1. BypassCall栈Detection
XposedHelpers.findAndHookMethod(StackTraceElement.class, "getClassName",
new XC_MethodHook() {
@Override
protected void afterHookedMethod(MethodHookParam param) throws Throwable {
String name = (String) param.getResult();
if (name != null && name.toLowerCase().contains("xposed")) {
param.setResult("com.android.internal.os.ZygoteInit");
}
}
});

// 2. BypassClassLoadDetection
XposedHelpers.findAndHookMethod(Class.class, "forName", String.class,
new XC_MethodHook() {
@Override
protected void beforeHookedMethod(MethodHookParam param) throws Throwable {
String cls = (String) param.args[0];
if (cls != null && cls.toLowerCase().contains("xposed")) {
param.setThrowable(new ClassNotFoundException(cls));
}
}
});

// 3. BypassFileDetection
XposedHelpers.findAndHookMethod(File.class, "exists",
new XC_MethodHook() {
@Override
protected void afterHookedMethod(MethodHookParam param) throws Throwable {
String path = ((File) param.thisObject).getAbsolutePath();
if (path.toLowerCase().contains("xposed") ||
path.toLowerCase().contains("edxposed") ||
path.toLowerCase().contains("lspd")) {
param.setResult(false);
}
}
});

XposedBridge.log("[Bypass] All hooks activated");
}
}

```

adb shell "su -c 'ls -l /system/framework/Xposed\*\*'"
adb shell "su -c 'ps -A | grep xposed'"

# 查看已安装的 Xposed 模块

adb shell "su -c 'ls /data/app/ | grep -i xposed'"

# Check LSPosed Status

adb shell "su -c 'ls -l /data/adb/lspd/'"

# ========== LogDebug ==========

# View Xposed 框架 Log

adb logcat -s Xposed:V

# 查看模块日志（假设模块标签为 AntiDetect）

adb logcat | grep AntiDetect

# View App Detection 相关 Log

adb logcat | grep -iE "detect|xposed|security|check"

# 清空日志并实时查看

adb logcat -c && adb logcat -v time

# ========== ModuleManage ==========

# Compile Xposed Module

./gradlew assembleDebug # Debug 版
./gradlew assembleRelease # Release 版

# InstallModule

adb install app/build/outputs/apk/debug/app-debug.apk

# 卸载模块

adb uninstall com.example.antidetect

# 重启目标 App（应用更改）

adb shell am force-stop com.target.app
adb shell am start -n com.target.app/.MainActivity

# ========== 定制框架 ==========

# 推送自定义框架到设备

adb push EdXposed-custom.zip /sdcard/

# 在内 Magisk, Install（command line 方式）

adb shell "su -c 'magisk --install-module /sdcard/EdXposed-custom.zip'"

# 重启设备

adb reboot

# ========== TestValidate ==========

# Install XposedChecker TestTool

adb install XposedChecker.apk

# RunTarget App 并观察行为

adb shell am start -n com.target.app/.MainActivity

# 抓取崩溃日志

adb logcat -b crash

# CheckProcessMemoryMapping（查找 Xposed 特征）

adb shell "su -c 'cat /proc/$(pidof com.target.app)/maps | grep -i xposed'"

```

// 模式 1：Call栈Detection
if (element.getClassName().contains("xposed")) { /* Detection到 */ }

// 模式 2：anomalyCall栈Detection
try { throw new Exception(); } catch (Exception e) {
for (StackTraceElement elem : e.getStackTrace()) { /* Check */ }
}

// 模式 3：ClassLoadDetection
Class.forName("de.robv.android.xposed.XposedBridge");

// 模式 4：ClassLoader 检测
ClassLoader.getSystemClassLoader().loadClass("de.robv.android.xposed.XposedHelpers");

// 模式 5：FileDetection
new File("/system/framework/XposedBridge.jar").exists()

// 模式 6：系统PropertyDetection
System.getProperty("vxp_forbid_status")
System.getProperty("ro.xposed.version")

// ========== Native LayerDetection模式 ==========

// 模式 7：maps FileDetection（C/C++）
FILE* fp = fopen("/proc/self/maps", "r");
// ThenSearch "xposed" or "libxposed"

// 模式 8：dlopen 检测
void* handle = dlopen("libxposed_art.so", RTLD_NOW);
if (handle != NULL) { /* Detection到 */ }

```

Class.forName
/proc/self/maps
libxposed
vxp_forbid
ro.xposed
EdXposed
LSPosed

| 普通应用（社交、工具） | Java 层调用栈检测 | 策略 A：通用 Hook 模块 | 95% |
| 金融 App（银行、支付） | Java + Native 综合检测 | 策略 C：定制框架 + Hook | 70% |
| 大型游戏 | Native 层 + 定时检测 | 策略 C：定制框架 | 60% |
| 安全类 App（VPN、杀毒） | 深度检测 + 完整性校验 | 策略 C + 虚拟化 | 50% |
| 小众 App | 简单检测或无检测 | 策略 B：现成模块 | 99% |

**成功率说明**：

- **95%+**：通用方法即可绕过
- **70-90%**：需要针对性编写 Hook
- **50-70%**：需要定制框架或多种技术组合
- **<50%**：可能需要虚拟化、系统级修改等高级技术

```

```

<!-- 01-Recipes/Automation/automation_and_device_farming.md -->

# 工程化：自动化与群控系统

在虚拟化和容器化解决了"环境"问题之后，自动化和群控系统则负责解决"执行"和"管理"的问题。它们是驱动整个规模化测试和分析流水线运转的核心引擎。

---

## 1. 自动化框架

自动化框架是模拟用户行为、与 App UI 进行交互的工具集。它的核心任务是代替人工，实现对 App 的程序化控制。

### a) 主流框架对比

| 框架                      | 驱动原理                                | 优点                                                                 | 缺点                                                                                | 适用场景                                      |
| ------------------------- | --------------------------------------- | -------------------------------------------------------------------- | ----------------------------------------------------------------------------------- | --------------------------------------------- |
| **Appium**                | WebDriver 协议 -> UIAutomator2/XCUITest | 跨平台（Android/iOS），多语言支持，生态成熟，功能强大。              | 环境配置复杂，执行速度相对较慢，对 App 有一定的侵入性（需要安装 WebDriver Agent）。 | 标准化的、跨平台的端到端（E2E）功能测试。     |
| **UIAutomator2 (Python)** | Google UIAutomator2                     | 直接与设备通信，速度快，稳定，API 简洁易用。                         | 仅支持 Android，功能相对 Appium 较少。                                              | 纯 Android 平台的快速自动化、爬虫和日常脚本。 |
| **Airtest / Poco**        | 图像识别 + UI 控件                      | 能够解决无法获取 UI 控件树的问题（如游戏），跨引擎（Unity, Cocos）。 | 图像识别不稳定，受分辨率和 UI 变化影响大，速度慢。                                  | 游戏自动化，黑盒测试。                        |

### c) Poco 自动化技术深度解析

Poco 是网易推出的 UI 自动化测试框架，专为游戏和复杂应用设计，是 Airtest 项目的核心组件之一。

#### 核心架构与原理

```
│ ┌──────────┐ │ │ │
│ │Poco SDK │ │ │ │
│ │插件 │ │ │ │
│ └──────────┘ │ │ │
│ ↓ │ │ │
│ UI控件树 │ │ │
│ 节点信息 │ │ │
└─────────────────┘ └─────────────────┘

```

4. **指令执行**: 接收控制端指令，操作对应 UI 控件
5. **结果回传**: 将操作结果和状态信息返回控制端

#### SDK 集成方式

- **Unity 引擎集成\*\***:

```csharp
// Unity 项目中集成 Poco SDK
using Poco;

public class PocoManager : MonoBehaviour {
void Start() {
// 启动 Poco 服务
var poco = new PocoServiceBuilder()
.SetPort(5001)
.SetDebugMode(true)
.Build();

poco.Start();
}
}

```

bool AppDelegate::applicationDidFinishLaunching() {
// 初始化 Poco 服务
poco::PocoManager::getInstance()->start();

return true;
}

```

public class MainActivity extends AppCompatActivity {
@Override
protected void onCreate(Bundle savedInstanceState) {
super.onCreate(savedInstanceState);

// 启动 Poco 服务
Poco.start("poco", 5001);
}
}

```

from poco.drivers.android.uiautomation import AndroidUiautomationPoco

# Unity 游戏连接

poco = UnityPoco(('192.168.1.100', 5001))

# Android 原生应用连接

poco = AndroidUiautomationPoco(use_airtest_input=True, screenshot_each_action=False)

# 基本操作

poco('Button').click() # 点击按钮
poco('InputField').set_text('test') # 输入文本
poco('ScrollView').swipe('up') # 滑动操作

# 等待元素出现

poco('LoadingPanel').wait_for_disappearance() # 等待加载完成

```

# 属性选择
poco(text='确定').click()
poco(name='startBtn', enabled=True).click()
poco(type='Button', visible=True).click()

# 相对位置选择
poco('username').sibling('password') # 兄弟节点
poco('title').parent() # 父节点

# 条件过滤
buttons = poco('Button').filter(lambda x: x.get_text().startswith('确定'))

```

# 拖拽操作

poco.drag_to([0.2, 0.2], [0.8, 0.8])

# 多点触控

poco.pinch(in_or_out='in', center=[0.5, 0.5], percent=0.6)

# 等待游戏状态

def wait_for_battle_end():
return poco('BattleResult').exists()

poco.wait_for_all(wait_for_battle_end, timeout=60)

```
class PocoEngine:
def __init__(self, addr):
self.client = PocoClient(addr)

def screenshot(self):
"""获取游戏截图"""
return self.client.call("Screenshot")

def get_screen_size(self):
"""获取屏幕尺寸"""
return self.client.call("GetScreenSize")

def click(self, pos):
"""点击操作"""
return self.client.call("Click", pos)

def dump_hierarchy(self):
"""获取 UI 控件树"""
return self.client.call("Dump")

```

if engine_type == 'unity':
return UnityPoco(device_info['addr'])
elif engine_type == 'cocos':
return CocosJSPoco(device_info['addr'])
elif engine_type == 'unreal':
return UE4Poco(device_info['addr'])
elif engine_type == 'android':
return AndroidUiautomationPoco()
else:
raise ValueError(f"Unsupported engine: {engine_type}")

```
def __init__(self, max_connections=10):
self.pool = queue.Queue(max_connections)
self.max_connections = max_connections

def get_connection(self, addr):
try:
return self.pool.get_nowait()
except queue.Empty:
return UnityPoco(addr)

def return_connection(self, conn):
try:
self.pool.put_nowait(conn)
except queue.Full:
pass # 丢弃多余连接

```

"""批量获取多个元素，减少 RPC 调用"""
elements = {}
for name, selector in selectors.items():
try:
elements[name] = poco(selector)
except:
elements[name] = None
return elements

# UseExample

ui_elements = batch_get_elements(poco, {
'start_btn': 'StartButton',
'settings_btn': 'SettingsButton',
'exit_btn': 'ExitButton'
})

```

def retry_on_failure(max_retries=3, delay=1):
def decorator(func):
@wraps(func)
def wrapper(*args, **kwargs):
for attempt in range(max_retries):
try:
return func(*args, **kwargs)
except Exception as e:
if attempt == max_retries - 1:
raise e
print(f"Attempt {attempt + 1} failed: {e}")
time.sleep(delay)
return None
return wrapper
return decorator

@retry_on_failure(max_retries=3, delay=2)
def stable_click(poco, selector):
"""稳定的点击操作，带重试机制"""
element = poco(selector)
if element.exists():
element.click()
return True
else:
raise Exception(f"Element {selector} not found")

```

# 设置 Poco 日志

setup_logger(level=logging.DEBUG)

# 自定义操作日志

class PocoLogger:
@staticmethod
def log_action(action, element, result=None):
timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
print(f"[{timestamp}] {action} on {element}, result: {result}")

@staticmethod
def log_screenshot(path):
print(f"Screenshot saved: {path}")

# 使用示例

def logged_click(poco, selector):
try:
poco(selector).click()
PocoLogger.log_action("CLICK", selector, "SUCCESS")
except Exception as e:
PocoLogger.log_action("CLICK", selector, f"FAILED: {e}")

# 保存错误时的截图

screenshot*path = f"error*{int(time.time())}.png"
poco.snapshot(screenshot_path)
PocoLogger.log_screenshot(screenshot_path)
raise

```
def __init__(self, device_id, poco_port=5001):
self.device_id = device_id
self.poco_port = poco_port
self.poco = None

def connect(self):
"""连接到设备上的 Poco 服务"""
device_ip = self.get_device_ip(self.device_id)
self.poco = UnityPoco((device_ip, self.poco_port))
return self.poco is not None

def execute_task(self, task_config):
"""执行自动化任务"""
try:
# 解析任务配置
actions = task_config['actions']

for action in actions:
self.execute_action(action)

return {"status": "success", "device_id": self.device_id}

except Exception as e:
return {"status": "failed", "error": str(e), "device_id": self.device_id}

def execute_action(self, action):
"""执行单个操作"""
action_type = action['type']

if action_type == 'click':
self.poco(action['selector']).click()
elif action_type == 'input':
self.poco(action['selector']).set_text(action['text'])
elif action_type == 'wait':
time.sleep(action['duration'])
# ... 其他操作类型

```

4. **异步操作**: 对于耗时操作使用异步模式提高效率
5. **错误处理**: 完善的异常捕获和恢复机制
6. **性能监控**: 监控 RPC 调用延迟和成功率

#### 与其他自动化框架对比

| 特性           | Poco               | Appium       | UIAutomator2       |
| :------------- | :----------------- | :----------- | :----------------- |
| **游戏支持**   | ✅ 优秀            | ❌ 不支持    | ❌ 不支持          |
| **跨引擎**     | ✅ Unity/Cocos/UE4 | ❌ 仅原生    | ❌ 仅 Android 原生 |
| **集成复杂度** | 中等(需 SDK)       | 低(无需修改) | 低(无需修改)       |
| **执行速度**   | 快                 | 中等         | 快                 |
| **稳定性**     | 高                 | 中等         | 高                 |
| **学习成本**   | 中等               | 高           | 低                 |

Poco 特别适合游戏自动化测试、游戏 AI 训练、游戏内容验证等场景，是移动游戏自动化的首选方案。

### b) 脚本编写的最佳实践

- **分离 UI 元素与业务逻辑 (Page Object Model)**: 不要将 UI 元素的定位符（如 `resource-id`）硬编码在业务代码中。应该为每个页面创建一个类（Page Object），封装该页面的所有元素和操作。当 UI 变化时，你只需要修改对应的 Page Object，而无需改动业务流程代码。

- **明确的断言**: 每个测试用例都应该有明确的成功或失败的判断标准（断言）。例如，点击登录后，断言"用户名"元素是否出现在下一个页面。

- **异常处理与重试**: 网络延迟、系统弹窗等都可能导致自动化失败。在关键步骤加入合理的等待、异常捕获和重试机制，可以大大提高脚本的稳定性。

- **日志与报告**: 在脚本的关键节点输出有意义的日志。测试结束后，生成图文并茂的测试报告（如 Allure Report），方便快速定位问题。

---

## 2. 群控系统 (Device Farming)

群控系统是一个将大量物理设备或虚拟设备（模拟器）汇集成一个统一的、可编程的资源池，并对其进行集中化管理、调度和监控的平台。

### a) 核心架构

一个工业级的群控系统通常是微服务架构，包含以下核心组件：

1. **API 网关 (API Gateway)**:

- 作为所有服务的统一入口，负责请求路由、身份认证和速率限制。

2. **设备管理服务 (Device Management Service)**:

- 维护一个包含所有设备（真机/模拟器）信息的数据库。

- 通过心跳机制实时监控每个设备的状态（空闲、占用、离线、健康状况）。

- 处理设备的接入和注销。

3. **任务调度服务 (Task Scheduling Service)**:

- 接收用户提交的任务（例如，"在 Android 12 上对 App X 执行 Y 测试"）。

- 根据任务要求（设备类型、系统版本等）和预设的调度策略（如优先级、FIFO）从设备管理服务中查询并锁定一个合适的设备。

4. **执行代理 (Agent)**:

- 在每个物理设备或模拟器上运行的一个轻量级代理程序。

- 负责接收并执行来自调度中心的具体指令，如：安装/卸载 APK、启动/停止 Appium、执行 shell 命令、上传/下载文件等。

5. **结果收集与报告服务**:

- 接收来自 Agent 的实时日志、截图、录屏和测试结果。

- 将结果存入数据库，并在任务结束后生成最终的测试报告。

6. **Web 管理前端**:

- 提供一个可视化的界面，让用户可以实时查看设备列表、远程控制设备（如 STF）、提交任务、查看任务队列和历史报告。

### b) 开源方案与自研

- **STF (Smartphone Test Farm)**: 提供了优秀的设备管理和远程控制功能，是许多自研群控系统的基础。但它本身不包含任务调度和报告等功能。

- **自研**: 许多大型公司会基于 STF、Appium、Docker、Kubernetes 等开源技术栈，结合自身的业务需求，搭建自研的群控平台，以实现更灵活的调度逻辑和更深入的业务集成。

---

## 总结

自动化与群控系统是移动端工程化能力的集中体现。它将底层的设备资源、中层的执行脚本和上层的业务需求有机地结合在一起，形成了一个强大的、可扩展的自动化解决方案，是现代 App 开发、测试和安全分析不可或缺的一环。

<!-- 01-Recipes/Automation/dial_up_proxy_pools.md -->

# 逆向技术：动态住宅 IP 代理池

在高强度的爬虫和逆向分析场景中，请求的 IP 地址是识别和封禁爬虫流量的第一道关卡。相比于易于被识别和屏蔽的数据中心 IP，动态变化的住宅 IP 地址具有极高的伪装度，是绕过反爬虫策略的关键技术。本节将详细介绍动态住宅 IP（拨号代理）的原理及其代理池的搭建方法。

---

## 1. 动态住宅 IP (拨号代理) 原理

### a) 什么是动态住宅 IP？

- **住宅 IP**: 指由互联网服务提供商（ISP），如电信、联通、移动，分配给普通家庭用户的 IP 地址。这些 IP 地址属于真实的住宅网络，信誉度最高。

- **动态 IP**: 与数据中心固定的静态 IP 不同，住宅宽带通常使用 **PPPoE (Point-to-Point Protocol over Ethernet)** 协议进行拨号上网。其核心特点是：**每断开一次连接再重新拨号，ISP 的 BRAS（宽带远程接入服务器）就会从其地址池中重新分配一个新的 IP 地址给用户**。

利用这一特性，我们可以通过程序自动化地控制 ADSL (或光猫) 进行"断线重拨"，从而在极短的时间内获取一个全新的、干净的、真实的住宅 IP。这就是拨号代理的核心原理。

### b) 优势

- **极高的真实性**: IP 来自真实的 ISP 住宅网络，无法被目标服务器通过 IP 库识别为数据中心流量。

- **海量 IP 资源**: 一个地区级的 ISP 运营商通常拥有数万到数百万的 IP 地址池。理论上，通过不断重拨，你可以使用该地区的所有 IP。

- **成本可控**: 相比于按流量计费的商业住宅代理服务，自建拨号代理池（尤其是在拥有物理设备的情况下）的长期成本更低。

---

## 2. 搭建拨号代理池

搭建一个稳定高效的拨号代理池，需要将物理层的拨号设备、网络层的代理服务和管理层的调度系统结合起来。

### a) 硬件与物理层

1. **ADSL/光猫 + 路由器**: 这是最基础的单元。你需要一个（或多个）办理了宽带业务的 ADSL 猫或光猫，并连接到一个可以被程序控制的路由器。
2. **树莓派/小型 PC**: 在每个拨号设备旁边，放置一个类似树莓派的廉价小型主机，用于执行拨号和代理服务的指令。
3. **4G/5G 模块 (可选)**: 除了固定宽带，还可以使用 4G/5G 工业模块。通过控制模块的飞行模式切换或重置，同样可以实现 IP 的更换。这种方式灵活性更高，但流量成本也更高。

### b) 软件与网络层

1. **拨号脚本**: 在树莓派上运行一个脚本，用于控制路由器执行 PPPoE 的断开和重连操作。这通常可以通过 `curl` 或 `ssh` 调用路由器的管理接口来实现。

- **示例 (控制 OpenWrt/LEDE 路由器的脚本)**:

  ```bash

  ```

# 断开 PPPoE 连接

ssh root@192.168.1.1 'ifdown wan'

# 重新连接

ssh root@192.168.1.1 'ifup wan'

# 获取新 IP

ssh root@192.168.1.1 'ifconfig pppoe-wan | grep "inet addr" | cut -d: -f2 | cut -d" " -f1'

````

* **Squid 配置示例 (`squid.conf`)**:
    ```

# 允许所有来源的所有请求
http_access allow all

# 监听端口
http_port 3128

# 禁止泄露原始 IP
forwarded_for off
request_header_access Via deny all
request_header_access X-Forwarded-For deny all

````

当你有大量的拨号节点时，一个中心化的管理系统是必不可少的。

1. **中心 API 服务器**:

- **IP 注册**: 每个拨号节点在成功获取新 IP 后，将 `(新IP:端口, 地理位置, ISP)` 等信息上报给中心服务器。

- **IP 获取**: 业务程序（如爬虫）通过调用 API，从中心服务器获取一个当前可用的代理 IP。可以根据需求指定地理位置等条件。

- **IP 续期与心跳**: 拨号节点需要定期向中心服务器发送心跳，证明自己仍然在线。如果心跳超时，服务器就将该 IP 从可用池中移除。

- **IP 注册**: 每个拨号节点在成功获取新 IP 后，将 `(新IP:端口, 地理位置, ISP)` 等信息上报给中心服务器。

- **IP 获取**: 业务程序（如爬虫）通过调用 API，从中心服务器获取一个当前可用的代理 IP。可以根据需求指定地理位置等条件。

- **IP 续期与心跳**: 拨号节点需要定期向中心服务器发送心跳，证明自己仍然在线。如果心跳超时，服务器就将该 IP 从可用池中移除。

2. **IP 池管理策略**:

- **可用性检测**: 中心服务器定期主动检测池中代理的连通性，剔除失效的 IP。

- **IP 轮换**: 当一个 IP 被封禁或使用次数过多时，业务程序可以调用 API 请求中心服务器通知对应的拨号节点执行"换 IP"操作。

- **并发控制**: 管理每个代理 IP 当前的并发请求数，避免因过度使用而被封禁。

- **可用性检测**: 中心服务器定期主动检测池中代理的连通性，剔除失效的 IP。

- **IP 轮换**: 当一个 IP 被封禁或使用次数过多时，业务程序可以调用 API 请求中心服务器通知对应的拨号节点执行"换 IP"操作。

- **并发控制**: 管理每个代理 IP 当前的并发请求数，避免因过度使用而被封禁。

### d) 整体架构图

```mermaid
graph TD
subgraph "业务服务器"
A[爬虫/业务应用] --> B{中心 API Server};
end

B -- 获取代理 --> A;
B -- 管理/调度 --> C1;
B -- 管理/调度 --> C2;
B -- 管理/调度 --> C3;

subgraph "拨号节点 1 (上海电信)"
C1[树莓派] --> D1[代理服务 (Squid)];
C1 -- 控制重拨 --> E1[路由器/光猫];
E1 -- PPPoE --> F1[(ISP 网络)];
end

subgraph "拨号节点 2 (北京联通)"
C2[树莓派] --> D2[代理服务 (Squid)];
C2 -- 控制重拨 --> E2[路由器/光猫];
E2 -- PPPoE --> F2[(ISP 网络)];
end

subgraph "拨号节点 N (深圳移动)"
C3[树莓派] --> D3[代理服务 (Squid)];
C3 -- 控制重拨 --> E3[路由器/光猫];
E3 -- PPPoE --> F3[(ISP 网络)];
end

C1 -- 上报 IP --> B;
C2 -- 上报 IP --> B;
C3 -- 上报 IP --> B;

```

<!-- 01-Recipes/Automation/docker_deployment.md -->

# 容器化部署：Docker 与 Kubernetes 实战

将爬虫项目容器化是实现标准化部署、弹性伸缩和 CI/CD 的第一步。本指南将详细介绍如何编写 Dockerfile，使用 Docker Compose 编排服务，以及如何在 Kubernetes (K8s) 上运行爬虫任务。

## 1. Dockerfile 最佳实践

我们需要为 Scrapy 项目构建一个轻量、稳定的 Docker 镜像。

### 目录结构

```text
my_crawler/
├── scrapy.cfg
├── requirements.txt
├── Dockerfile
└── myproject/
├── __init__.py
├── items.py
├── settings.py
└── spiders/

```

FROM python:3.9-slim-buster

# 设置工作目录

WORKDIR /app

# 设置环境变量

# 防止 Python 生成 .pyc 文件

ENV PYTHONDONTWRITEBYTECODE 1

# 防止 Python 缓冲区 stdout/stderr，确保日志实时输出

ENV PYTHONUNBUFFERED 1

# 设置时区 (可选)

ENV TZ=Asia/Shanghai

# 安装系统依赖 (如果需要编译 lxml 或其它库)

# RUN apt-get update && apt-get install -y gcc libxml2-dev libxslt-dev && rm -rf /var/lib/apt/lists/\*\*

# 复制依赖文件并安装

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码

COPY . .

# 默认启动命令 (可被 docker run 覆盖)

# 这里我们默认启动 scrapyd (如果使用 scrapyd 部署) 或仅作为一个 shell

CMD ["scrapy", "list"]

```

# 运行爬虫
docker run --rm my-crawler:v1 scrapy crawl myspider

```

version: '3.8'

services:

# 1. Redis 服务 (消息队列)

redis:
image: redis:6.2-alpine
ports:

- "6379:6379"
  volumes:
- redis_data:/data
  command: redis-server --appendonly yes

# 2. MongoDB 服务 (数据存储)

mongo:
image: mongo:5.0
ports:

- "27017:27017"
  environment:
  MONGO_INITDB_ROOT_USERNAME: admin
  MONGO_INITDB_ROOT_PASSWORD: password
  volumes:
- mongo_data:/data/db

# 3. 爬虫服务 (Master/Slave 模式中的 Slave)

crawler:
build: .
image: my-crawler:latest

# 覆盖默认命令，启动爬虫

command: scrapy crawl myspider_distributed

# 依赖服务就绪

depends_on:

- redis
- mongo
  environment:
- REDIS_HOST=redis
- MONGO_URI=mongodb://admin:password@mongo:27017

# 想要开启多个爬虫节点？直接 scale

deploy:
replicas: 3

volumes:
redis_data:
mongo_data:

```

# 扩容爬虫节点到 5
docker-compose up -d --scale crawler=5

# 查看日志
docker-compose logs -f crawler

```

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
name: scrapy-worker
labels:
app: scrapy-worker
spec:
# 副本数，即并发爬虫节点数量
replicas: 5
selector:
matchLabels:
app: scrapy-worker
template:
metadata:
labels:
app: scrapy-worker
spec:
containers:
- name: crawler
image: registry.example.com/my-crawler:v1
# 容器startupCommand
command: ["scrapy", "crawl", "myspider_distributed"]
# Env VarsConfig
env:
- name: REDIS_HOST
value: "redis-service" # K8s Service Name
- name: MONGO_URI
valueFrom:
secretKeyRef:
name: db-secrets
key: mongo-uri
resources:
requests:
memory: "256Mi"
cpu: "250m"
limits:
memory: "512Mi"
cpu: "500m"

```

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
name: daily-crawler
spec:
# Run daily
schedule: "0 2 * * *"
jobTemplate:
spec:
template:
spec:
containers:
- name: crawler
image: registry.example.com/my-crawler:v1
command: ["scrapy", "crawl", "daily_spider"]
env:
- name: REDIS_HOST
value: "redis-service"
restartPolicy: OnFailure

```

# AppConfig

kubectl apply -f crawler-deployment.yaml

# View Pod Status

kubectl get pods

# 动态扩缩容 (No 需 Modify yaml)

kubectl scale deployment scrapy-worker --replicas=10

````
* **Gerapy**: 基于 Scrapyd 的分布式管理 GUI，支持节点管理、代码编辑、定时任务。


**Dockerfile (集成 Scrapyd)**:

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install scrapyd
COPY scrapyd.conf /etc/scrapyd/
CMD ["scrapyd"]




<!-- 01-Recipes/Automation/proxy_pool_design.md -->

# 代理池设计与 Scrapy 集成

在面对反爬虫策略严厉的目标站（如电商、社交媒体）时，单一 IP 很容易被封禁。构建一个高可用、自动轮转的代理池 (Proxy Pool) 是大规模数据采集的基础设施。

## 1. 代理池架构设计

一个成熟的代理池系统通常包含四个独立模块，通过 Redis 进行解耦：

### 核心组件

1. **Fetcher (获取器)**:

- **职责**: 定时从各大免费代理网站（快代理、云代理等）或付费 API 接口拉取代理 IP。
- **策略**: 每隔 N 分钟运行一次，将获取到的新 IP 存入 Redis 的“待检测”队列。

2. **Checker (检测器)**:

- **职责**: 异步检测 Redis 中代理 IP 的可用性、匿名度和响应速度。
- **实现**: 使用 `aiohttp` 或 `requests` 对目标网站（如百度、谷歌或特定目标站）发起请求。
- **评分机制**:

| 项目 | 说明 |
|------|------|
| **可用** | 分数设为 100（或 +1）。 |
| **不可用** | 分数减 1，当分数低于阈值（如 0）时，从 Redis 移除。 |
| **复检** | 定时遍历 Redis 中现存的代理进行复检，确保库中 IP 始终有效。 |


3. **Storage (存储器)**:


| 项目 | 说明 |
|------|------|
| **数据库** | Redis 是最佳选择。 |
| **数据结构** | `Sorted Set` (有序集合)。 |
| **Key** | 代理 IP (`1.2.3.4:8080`) |
| **Score** | 代理分数 (0-100) |
| **优势** | 可以利用 `ZRANGEBYSCORE` 轻松获取高质量（满分）代理。 |


4. **API Server (接口服务)**:
- **职责**: 为爬虫提供简单的 HTTP 接口获取代理。
- **接口**:
- `/get`: 随机返回一个高分代理。
- `/count`: 查看当前可用代理数量。

### architecture 图

```mermaid
graph LR
ProxySources[免费/付费源] --> Fetcher
Fetcher -->|Raw Proxy| Redis[(Redis Sorted Set)]
Redis <-->|Validation| Checker
Crawler[Scrapy 爬虫] -->|Request| API[API Server]
API -->|Get High Score Proxy| Redis

````

1. **请求前 (`process_request`)**: 从代理池获取一个代理，赋值给 `request.meta['proxy']`。
2. **响应后 (`process_response`)**: 检查状态码。如果是 200，说明代理正常；如果是 403/429/超时，说明代理可能失效或被封。
3. **异常处理 (`process_exception`)**: 捕获连接超时、连接拒绝等网络错误，标记该代理失效，并对当前请求进行重试。

### 代码实现

```python
# middlewares.py
import requests
import logging
from scrapy.exceptions import IgnoreRequest

class ProxyMiddleware:
def __init__(self, proxy_pool_url):
self.proxy_pool_url = proxy_pool_url
self.logger = logging.getLogger(__name__)

@classmethod
def from_crawler(cls, crawler):
return cls(
proxy_pool_url=crawler.settings.get('PROXY_POOL_URL')
)

def _get_random_proxy(self):
try:
response = requests.get(self.proxy_pool_url)
if response.status_code == 200:
return response.text.strip()
except requests.ConnectionError:
return None
return None

def process_request(self, request, spider):
# IfRequest已经settingssssss代理（E.g.SpecificRequest），则跳过
if request.meta.get('proxy'):
return

proxy = self._get_random_proxy()
if proxy:
self.logger.debug(f"Using proxy: {proxy}")
# settingssssss代理，格式: http://user:pass@ip:端口 or http://ip:端口
request.meta['proxy'] = f"http://{proxy}"
else:
self.logger.warning("No proxy available from pool!")

def process_response(self, request, response, spider):
# 如果遇到验证码、封禁等状态码
if response.status_code in [403, 429]:
self.logger.warning(f"Proxy {request.meta.get('proxy')} banned (Status {response.status_code}), retrying...")
# 标记该代理失效（可选：调用 接口 报告该代理坏）
# self._report_bad_proxy(request.meta.get('proxy'))

# DeleteCurrent代理settingssssss，Re-调度Request（会再次经过 process_request 换新代理）
del request.meta['proxy']
return request.replace(dont_filter=True)

return response

def process_exception(self, request, exception, spider):
# process connection timeout、DNS ErrorEtc
self.logger.error(f"Proxy {request.meta.get('proxy')} failed: {exception}")

# 换代理重试
del request.meta['proxy']
return request.replace(dont_filter=True)

```

'myproject.middlewares.ProxyMiddleware': 543,

# 禁用 Scrapy 默认 UserAgent and 重试 In 间件（视情况而定）

# 'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,

}

PROXY_POOL_URL = 'http://localhost:5000/get'

````

- **GitHub**: `jhao104/proxy_pool`
- **特点**: 也是基于 Redis，架构清晰，支持 Docker 一键部署，内置了几十个免费源的抓取规则。

2. **Gerapy / Scylla**

- **GitHub**: `imWildCat/scylla`
- **特点**: 智能化代理池，自动学习代理的稳定性。

3. **GimmeProxy**
- **特点**: Go 语言编写，性能强劲。
___
## 4. 隧道代理 (Tunnel Proxy)

对于企业级应用，维护自建代理池成本较高（免费 IP 质量极差，可用率不足 5%）。此时通常使用厂商提供的**隧道代理**。

**特点**:

- 不需要在本地维护 IP 池。
- 只有一个固定的入口地址（如 `http://proxy.vendor.com:8000`）。
- **每一次请求，云端会自动转发给背后不同的动态 IP**。

**Scrapy 集成**:
只需要在 `process_request` 中将代理设置为该固定地址，并在 Header 中添加鉴权信息。

```python
# Tunnel Proxy Example
request.meta['proxy'] = "http://proxy.vendor.com:8000"
# 某些厂商要求在头部通过 Proxy-Authorization 认证
import base64
auth = base64.b64encode(b"user:pass").decode()
request.headers['Proxy-Authorization'] = f"Basic {auth}"




<!-- 01-Recipes/Automation/scrapy.md -->

# Scrapy 快速入门备忘录

Scrapy 是一个用于网络爬虫和数据抓取的、开源的、协作式的 Python 框架。它具有速度快、功能强大、可扩展性高的特点。本备忘录为 Scrapy 的核心概念和常用命令提供快速参考。

- --

## 目录
- [Scrapy 快速入门备忘录](#scrapy-快速入门备忘录)
- [目录](#目录)
- [核心组件](#核心组件)

- [项目命令](#项目命令)

- [Spider (爬虫)](#spider-爬虫)
- [基本结构](#基本结构)

- [提取数据 (Selectors)](#提取数据-selectors)

- [处理分页和链接](#处理分页和链接)
- [Item (数据容器)](#item-数据容器)

- [Pipeline (数据管道)](#pipeline-数据管道)

- [Settings (设置)](#settings-设置)

- --

### 核心组件

Scrapy 的数据流由以下核心组件协同完成：

1. **Engine (引擎)**: 负责控制所有组件之间的数据流，并在相应动作发生时触发事件。
2. **Scheduler (调度器)**: 接收来自引擎的请求 (`Request`)，并将其入队，以便后续引擎请求时提供。
3. **Downloader (下载器)**: 负责获取页面数据，并将其提供给引擎，而后由引擎将结果 (`Response`) 交给 Spider。
4. **Spiders (爬虫)**: 用户编写的用于解析 `Response` 并提取 `Item` 或额外 `Request` 的类。
5. **Item Pipeline (项目管道)**: 负责处理由 Spider 提取出来的 `Item`。典型的操作包括数据清洗、验证和持久化（如存入数据库）。
6. **Downloader Middlewares (下载器中间件)**: 位于引擎和下载器之间的钩子，用于在请求发送和响应返回时进行自定义处理（如设置 User-Agent、处理代理）。
7. **Spider Middlewares (爬虫中间件)**: 位于引擎和 Spider 之间的钩子，用于处理 Spider 的输入 (`Response`) 和输出 (`Item`, `Request`)。

![Scrapy Architecture](https://docs.scrapy.org/en/latest/_images/scrapy_architecture.png)

- --

### 项目命令

| 命令 | 描述 |
| :--- | :--- |
| `pip install scrapy` | 安装 Scrapy 框架 |
| `scrapy startproject myproject` | 创建一个名为 `myproject` 的新项目 |
| `cd myproject` | 进入项目目录 |
| `scrapy genspider example example.com`| 在 `spiders` 目录下创建一个名为 `example` 的爬虫，限定域名为 `example.com` |
| `scrapy crawl example` | 运行名为 `example` 的爬虫 |
| `scrapy crawl example -o output.json` | 运行爬虫并将提取的数据保存为 JSON 文件 |
| `scrapy shell "http://example.com"` | 启动一个交互式 Shell，用于测试 XPath/CSS 选择器 |
| `scrapy list` | 列出项目中的所有可用爬虫 |

- --

### Spider (爬虫)

Spider 是你定义如何爬取某个网站（或一组网站）的类，包括爬取动作和如何从页面内容中提取结构化数据。

#### 基本结构

```python
# myproject/spiders/example_spider.py
import scrapy

class ExampleSpider(scrapy.Spider):
# 爬虫的唯一标识名称
name = 'example'
# 允许爬取的域名列表（可选）
allowed_domains = ['example.com']
# 爬虫启动时请求的 URL 列表
start_urls = ['http://example.com/']

# 处理 start_urls 响应的默认回调方法
def parse(self, response):
# 在这里编写解析逻辑
pass

````

- `response.css('a::attr(href)').getall()`: 提取所有 `<a>` 标签的 `href` 属性。

- `response.css('div.product > p::text').get()`: 提取 `class="product"` 的 `div` 下的 `p` 标签文本。

- **XPath 表达式**:
- `response.xpath('//h1/text()').get()`: 提取第一个 `<h1>` 标签的文本。

- `response.xpath('//a/@href').getall()`: 提取所有 `<a>` 标签的 `href` 属性。

- `response.xpath('//div[@class="product"]/p/text()').get()`: 同上。

#### 处理分页和链接

在 `parse` 方法中，你可以 `yield` 新的 `Request` 对象来跟进链接。

```python
def parse(self, response):
# ... 提取当前页面数据 ...

# 提取下一页链接并生成新请求
next_page = response.css('a.next_page::attr(href)').get()
if next_page is not None:
# response.urljoin() 用于处理相对 URL
yield response.follow(next_page, callback=self.parse)

```

```python
# myproject/items.py
import scrapy

class ProductItem(scrapy.Item):
name = scrapy.Field()
price = scrapy.Field()
description = scrapy.Field()

```

item = ProductItem()
item['name'] = response.css('h1.product-name::text').get()
item['price'] = response.css('span.price::text').get()
yield item

````

```python
# myproject/pipelines.py
import sqlite3

class SQLitePipeline:
def open_spider(self, spider):
# 爬虫开启时调用
self.connection = sqlite3.connect('products.db')
self.cursor = self.connection.cursor()
self.cursor.execute('CREATE TABLE IF NOT EXISTS products (name TEXT, price TEXT)')

def close_spider(self, spider):
# 爬虫关闭时调用
self.connection.close()

def process_item(self, item, spider):
# 每个 item 都会调用
self.cursor.execute('INSERT INTO products (name, price) VALUES (?, ?)', (item['name'], item['price']))
self.connection.commit()
return item # 必须返回 item

````

'myproject.pipelines.SQLitePipeline': 300,
}

````

* `DEFAULT_REQUEST_HEADERS`: 设置默认的请求头，如 `User-Agent`。

* `DOWNLOAD_DELAY = 1`: 设置下载延迟（秒），以避免对服务器造成太大压力。

* `CONCURRENT_REQUESTS = 16`: 并发请求数。

* `ITEM_PIPELINES`: 激活和设置 Item Pipeline 的优先级。

* `DOWNLOADER_MIDDLEWARES`: 激活和设置下载器中间件的优先级。



<!-- 01-Recipes/Automation/scrapy_redis_distributed.md -->

# 分布式爬虫实战：Scrapy-Redis 详解

Scrapy 默认是单机架构，请求队列保存在内存中，重启即失，且无法多机共享。**Scrapy-Redis** 是一个强大的组件，它重写了 Scrapy 的调度器 (Scheduler) 和去重组件 (DupeFilter)，将请求队列和指纹集合存储在 Redis 中，从而实现：
1. **分布式爬取**: 多个爬虫节点共享同一个 Redis 队列，协同工作。
2. **断点续爬**: 请求持久化在 Redis 中，爬虫挂掉重启后可继续运行。
___
## 1. 核心architecture原理

## # 原生 Scrapy vs Scrapy-Redis

* **原生 Scrapy**:
* **Scheduler**: 维护在内存中的 Python `deque` 或 `queue`。
* **DupeFilter**: 维护在内存中的 Python `set`。
* **缺点**: 无法跨进程/跨机器共享，内存受限。

* **Scheduler**: 维护在内存中的 Python `deque` 或 `queue`。
* **DupeFilter**: 维护在内存中的 Python `set`。
* **缺点**: 无法跨进程/跨机器共享，内存受限。


* **Scrapy-Redis**:
* **Scheduler**: 从 Redis 的 `List` (或 `PriorityQueue`) 中 `POP` 请求，向其 `PUSH` 新请求。
* **DupeFilter**: 利用 Redis 的 `Set` 数据结构存储 URL 指纹 (SHA1)，利用 Redis 的原子性进行去重。
* **Item Pipeline**: 可选将提取的数据直接推入 Redis，由独立的 Worker 消费存储。

* **Scheduler**: 从 Redis 的 `List` (或 `PriorityQueue`) 中 `POP` 请求，向其 `PUSH` 新请求。
* **DupeFilter**: 利用 Redis 的 `Set` 数据结构存储 URL 指纹 (SHA1)，利用 Redis 的原子性进行去重。
* **Item Pipeline**: 可选将提取的数据直接推入 Redis，由独立的 Worker 消费存储。
___
## 2. 环境搭建与配置

## # 安装

```bash
pip install scrapy-redis

````

# 1. 启用 Scrapy-Redis 调度器

SCHEDULER = "scrapy_redis.scheduler.Scheduler"

# 2. 启用 Scrapy-Redis 去重 Filter 器

DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"

# 3. 允许暂停 (断点续爬 Core)

# 如果为真，当爬虫停止时，Redis 中的请求队列不会被清空

SCHEDULER_PERSIST = True

# 4. settingssssss Redis Connect

# 方式一：单独 Setting

REDIS_HOST = '192.168.1.100'
REDIS_PORT = 6379

# REDIS_PARAMS = {'password': 'yourpassword'}

# 方式二：完成 地址

# REDIS_URL = 'redis://user:pass@hostname:9001'

# 5. 配置请求队列模式（可选，默认为 PriorityQueue）

# SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.PriorityQueue' # 有序集合，支持优先级

# SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.FifoQueue' # 先进先出列表

# SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.LifoQueue' # 后进先出列表（栈）

# 6. (可选) 将数据存入 Redis Pipeline

ITEM_PIPELINES = {
'scrapy_redis.pipelines.RedisPipeline': 300,
}

````

```python
from scrapy_redis.spiders import RedisSpider
import scrapy

class MyDistributedSpider(RedisSpider):
name = 'myspider_distributed'

# 核心差异：不再定义 start_urls
# 定义 redis_key，爬虫启动后会阻塞等待该键中出现的 URL
redis_key = 'myspider:start_urls'

def parse(self, response):
self.logger.info(f"Crawling {response.url}")

# 提取数据逻辑与普通 Spider 一致
yield {
'url': response.url,
'title': response.css('title::text').get()
}

# 生成新请求
for href in response.css('a::attr(href)').getall():
yield response.follow(href, self.parse)

````

````

2. 向 Redis 推送起始 URL：
    ```bash
redis-cli lpush myspider:start_urls http://example.com

````

如果你需要利用 `Rule` 和 `LinkExtractor` 自动抓取全站，可以使用 `RedisCrawlSpider`。

---

## 4. 进阶优化策略

## # Bloom Filter 去重优化

Scrapy-Redis 默认使用 Redis `Set` 存储所有指纹。对于亿级 URL 的爬取，这会消耗数十 GB 内存。解决方案是集成 **Bloom Filter**。

- **实现思路\*\***:

1. 重写 `RFPDupeFilter`。
2. 使用 `redis-py` 的 `bf.add` 和 `bf.exists` 命令 (需要 RedisBloom 模块) 或 Python 端的 `pybloom_live` 映射到 Redis BitMap。

```python
# custom_dupefilter.py 简易示意
from scrapy_redis.dupefilter import RFPDupeFilter

class BloomFilterDupeFilter(RFPDupeFilter):
def request_seen(self, request):
fp = self.request_fingerprint(request)
# Assume self.服务器 Is Redis 连接，且supports s s s s s BF command
# If fingerprintexists at，Return True
if self.server.execute_command('BF.EXISTS', self.key, fp):
return True
# ElseAdd指纹
self.server.execute_command('BF.ADD', self.key, fp)
return False

```

```python
# When Generate Request Specify priority
yield scrapy.Request(url, priority=100) # 首页，优先
yield scrapy.Request(url, priority=10) # 详情页，次之

```

```python
# settings.py
# 指定空闲等待时间（秒），超时则关闭爬虫
SCHEDULER_IDLE_BEFORE_CLOSE = 10

```

subgraph "Master / Redis Server"
Redis[(Redis Queue & Set)]
end

subgraph "Slave 1"
Spider1[Scrapy Spider 1] -->|Pop Request| Redis
Spider1 -->|Push Request| Redis
Spider1 -->|Dupe Check| Redis
end

subgraph "Slave 2"
Spider2[Scrapy Spider 2] -->|Pop Request| Redis
Spider2 -->|Push Request| Redis
Spider2 -->|Dupe Check| Redis
end

subgraph "Data Storage"
Mongo[(MongoDB)]
end

Spider1 -->|Store Item| Mongo
Spider2 -->|Store Item| Mongo

````



<!-- 01-Recipes/Automation/virtualization_and_containers.md -->

# 工程化：虚拟化与容器技术

移动端虚拟化技术是在服务器端模拟出成百上千个 Android 设备环境的能力，它是所有大规模自动化测试、数据采集和安全分析任务的基石。这项技术的核心在于平衡性能、隔离性和真实性。

___

## 1. Android 模拟器 (Emulators)

Android 模拟器是在非 ARM 架构（通常是 x86_64）的服务器上，通过软件来模拟一个完整的 Android 操作系统环境的程序。

### a) 主流方案对比

| 方案 | 类型 | 优点 | 缺点 | 适用场景 |
| --- | --- | --- | --- | --- |
| **Android SDK Emulator** | 全系统模拟 (QEMU) | 功能最全，Google 官方支持，能模拟最新的 Android API 和 Google 服务。 | 性能开销极大，资源占用高，启动慢。 | 应用开发与调试，小规模测试。 |
| **Anbox / Waydroid** | 基于内核的容器 | 性能极高，接近原生，资源占用小。 | 隔离性较差，依赖宿主机内核，可能存在兼容性问题。 | 对性能要求极高的游戏测试，云游戏。 |
| **Redroid / anbox-cloud** | 基于 Docker 的容器化模拟器 | 部署、扩展和管理极为方便，易于集成到 CI/CD 流水线。 | 配置相对复杂，对 Docker 和网络知识有一定要求。 | 大规模、动态伸缩的云手机平台，自动化测试集群。 |
| **Genymotion** | 商业虚拟化方案 | 性能好，功能强大（GPS, 摄像头模拟），提供 PaaS/SaaS 服务。 | 收费，闭源。 | 企业级测试，需要专业技术支持的场景。 |

### b) 关键技术点

* **指令集翻译**: 在 x86 服务器上运行为 ARM 架构编译的 App，需要进行动态的指令集翻译。Intel 的 `libhoudini` 和 Google 的 `NdkVm` 是实现这一功能的关键组件，其效率直接决定了模拟器的性能。

* **GPU 硬件加速**: 为了渲染复杂的 UI 和游戏，模拟器需要将 Android 的图形渲染指令（OpenGL ES）桥接到宿主机的 GPU 上。`Virgil3D` 等项目实现了这种透传能力。

* **快照与状态管理**: 高效的快照功能允许我们快速地将模拟器恢复到一个干净、预设的状态，这对于保证每次自动化测试都在同样的环境中进行至关重要。

___

## 2. 容器技术 (Containerization)

容器技术（以 Docker 为代表）虽然不直接运行 Android 系统，但它在整个工程化体系中扮演着"胶水"和"标准交付"的关键角色。

### a) 隔离与打包依赖项

在复杂的自动化流程中，除了 Android 模拟器本身，我们还需要大量的周边服务。

* **任务队列**: 使用 `redis` 或 `rabbitmq` 容器来管理和分发成千上万的测试任务。

* **代理服务**: 部署 `mitmproxy` 或 `squid` 容器来集中拦截和分析所有模拟器的网络流量。

* **数据库**: 使用 `mongodb` 或 `postgresql` 容器来持久化存储测试结果、App 元数据和设备状态。

* **文件存储**: 使用 `minio` 容器来提供一个 S3 兼容的对象存储服务，用于存放 APK 文件、测试报告和截图。

将这些服务全部容器化，意味着我们可以通过一个 `docker-compose.yml` 文件，在任何环境中一键拉起整套后端基础设施，极大地简化了部署和运维。

### b) 构建标准化的执行环境

我们可以将 Appium、UIAutomator2 脚本、Frida 脚本以及所有 Python 依赖打包到一个 Docker 镜像中。

* **一致性**: 确保无论是在开发者的本地机器上，还是在 CI/CD 服务器上，脚本的运行环境都完全一致，避免了"在我这里能跑"的问题。

* **版本控制**: 可以为每个版本的 App 配套一个特定版本的测试镜像，方便地对历史版本进行回归测试。

* **可移植性**: 整个测试套件可以作为一个 Docker 镜像轻松地迁移到不同的云平台或物理服务器上。

___

## 总结

虚拟化和容器化是从"手工作坊"迈向"工业化生产"的第一步。

* **虚拟化** 解决了"设备从哪里来"的问题，提供了可大规模复制的、隔离的 Android 运行环境。

* **容器化** 解决了"依赖和脚本如何管理"的问题，提供了标准化的、可移植的交付物。

二者结合，为上层的自动化和群控系统提供了坚实、可靠、可扩展的基础设施。


<!-- 01-Recipes/Automation/web_anti_scraping.md -->

# Web 反爬虫技术

网络爬虫是自动从网站提取数据的过程。由于这可能被滥用，许多现代网站和服务实施了复杂的反爬虫（或"反机器人"）技术来保护其数据。这些技术可大致分为客户端（浏览器）和服务器端防御。

___

## 1. 客户端（浏览器）挑战

这些防御措施的重点是确保客户端是由人类操作的真实、标准的网络浏览器。

*   **JavaScript (JS) 挑战**: 服务器发送一段复杂的 JavaScript，客户端必须正确执行。该脚本可能执行计算、与浏览器 API 交互，并生成一个必须在后续请求中发回的令牌。需要使用像 Puppeteer 或 Selenium 这样的无头浏览器来通过这些挑战。
    *   **例子**: Akamai Bot Manager, Cloudflare Bot Management。

*   **浏览器指纹**: 服务器收集客户端浏览器环境的详细画像。这包括：
    *   `User-Agent`、屏幕分辨率、颜色深度、时区。
    *   安装的字体、浏览器插件。
    *   浏览器 JS 引擎或渲染引擎（Canvas）行为的细微差异。

*   **TLS 指纹**: 分析客户端 TLS 握手的参数（密码套件、扩展等）。
    *   与标准浏览器画像（例如，Windows 上的 Chrome）的偏差可用于将客户端标记为机器人。

*   **CAPTCHA**: "全自动区分计算机和人类的公开图灵测试"。这需要用户解决一个对机器人来说很困难的挑战（例如，在图像中识别物体）。
    *   **例子**: 谷歌的 reCAPTCHA (v2/v3), hCaptcha。绕过这些通常需要使用第三方破解服务。

## 2. 服务器端检测

这些防御措施通过分析服务器上的请求模式来识别非人类行为。

*   **IP 地址信誉**: 阻止或速率限制来自已知属于数据中心（如 AWS、谷歌云）或代理/VPN 服务的 IP 地址的请求。通常使用住宅代理来规避此问题。

*   **速率限制**: 限制单个 IP 地址或用户帐户在给定时间段内可以发出的请求数量。爬虫必须遵守这些限制以避免被阻止。

*   **行为分析**: 这是最先进的技术。服务器会长期跟踪用户行为，以建立"正常"人类交互的模型。
    *   **鼠标移动和按键**: 真实用户有混乱、非线性的鼠标移动和打字模式。机器人通常缺乏这一点。高级机器人必须模拟这种"人类"输入。
    *   **导航模式**: 人类通过网站的路径是可预测但非完全线性的。机器人通常直接或以僵硬的顺序访问页面。
    *   **请求时间**: 来自人类用户的请求之间的时间是可变的。机器人通常以固定的、最小的延迟运行。

___

## 规避策略

*   **使用功能齐全的浏览器**: 使用 **Selenium**、**Puppeteer** 或 **Playwright** 等工具来自动化一个真实的浏览器。这有助于解决 JS 挑战并提供更具说服力的浏览器指纹。使用"stealth"插件进一步隐藏自动化。

*   **轮换 IP**: 使用高质量的**住宅或移动代理**池来避免基于 IP 的封锁并模仿真实用户。

*   **模仿人类行为**: 引入随机延迟，模拟逼真的鼠标移动，并以更像人类的方式在网站上导航。

*   **逆向工程 JS**: 对于某些 JS 挑战，可以逆向工程混淆的 JavaScript 代码，以了解反机器人令牌是如何生成的。这使你可以在自己的脚本中复制逻辑，而无需完整的浏览器，这样会快得多。甚至可以使用 Frida 等工具来钩住浏览器进程以进行分析。

*   **IP 质量检测**: 服务器端会检查请求 IP 的类型（数据中心、住宅、移动），并对来自数据中心的 IP 施加更严格的限制。

*   **行为分析**: 服务器通过分析用户在一系列请求中的行为模式（如请求频率、访问路径、鼠标移动轨迹）来判断其是否为机器人。

___

## 专题：绕过 Cloudflare 五秒盾

Cloudflare 的"I'm Under Attack Mode"（我正遭受攻击模式）是一个非常常见的强力反机器人措施，用户会看到一个持续约五秒的"Checking your browser before accessing..."页面。这就是俗称的"五秒盾"。

### 1. 工作原理

五秒盾的核心是一个 **JavaScript 挑战 (JS Challenge)**。当用户首次访问受保护的页面时，服务器会返回一个包含复杂、高度混淆的 JavaScript 代码的 HTML 页面。这段 JS 的主要目的不是为了好看，而是为了：

1.  **环境检测**: 检查当前环境是否为一个真实的、标准的浏览器。它会检测 `window`, `document` 等对象，以及屏幕分辨率、时区、插件等浏览器指纹信息。
2.  **计算密集型任务**: 执行一系列复杂的数学运算。这些运算对于现代浏览器来说耗时很短（通常在 1-2 秒内），但对于不具备 JS 执行引擎的简单爬虫（如纯粹的 `requests` 库）来说是无法完成的。
3.  **生成验证 Token**: JS 计算的最终结果会作为一个 Token，通过表单提交或 Ajax 请求发送回 Cloudflare 的服务器进行验证。
4.  **设置身份 Cookie**: 验证通过后，Cloudflare 会在用户的浏览器中设置一个特殊的 Cookie（如 `__cf_bm` 或 `cf_clearance`），该 Cookie 在一定时间内有效。后续的请求只要携带这个有效的 Cookie，就可以直接访问网站，无需再次挑战。

### 2. 绕过方案

绕过五秒盾的核心思想是 **模拟一个能够成功执行其 JS 挑战的环境**。

#### a. 方案一：使用无头浏览器 (Headless Browser) - 推荐

这是最稳定、成功率最高的方案。使用 `Puppeteer` (Node.js), `Playwright` (Python/Node.js) 或 `Selenium` 等自动化浏览器框架。

*   **工作方式**: 这些工具会启动一个真实的、完整的浏览器内核（如 Chrome），只是没有图形界面。当它们访问目标页面时，浏览器会像正常用户访问一样，自动执行所有的 JavaScript，完成挑战，获取 Cookie，然后继续访问目标页面。
*   **优点**: 成功率极高，几乎能应对所有基于 JS 挑战的防护。
*   **缺点**: 资源消耗大（需要启动整个浏览器），速度相对较慢。

**Playwright (Python) 示例：**


<!-- 01-Recipes/Network/crypto_analysis.md -->

# Recipe: 分析并提取 android 应用的加密密钥

## 问题场景

_你遇到了什么问题？_

- ❓ App 的 API 请求参数被加密了，看不懂内容
- ❓ 想知道 App 使用了什么加密算法
- ❓ 需要提取加密密钥来解密数据
- ❓ 想重现 App 的加密/签名逻辑用于自动化
- ❓ 需要绕过加密验证或签名检查

_本配方教你_：识别加密算法、定位密钥位置、使用 Frida 动态提取密钥。

_核心理念_：

> 💡 **密码学逆向的关键不是破解算法，而是找到密钥**
>
> - ❌ 不要试图"破解" AES/RSA 等成熟算法（几乎不可能）
> - ✅ 用动态分析直接提取密钥
> - ✅ 或直接调用 App 自己的加密函数（利用已有密钥）

_预计用时_: 30-60 分钟

- --

## 工具清单

## # 必需工具

- ☐ **jadx-gui** - Java 层静态分析
- ☐ **Frida** - 动态 Hook 提取密钥
- ☐ **Android 设备**（已 Root）

## # 可选工具

- ☐ **IDA Pro / Ghidra** - Native 层分析
- ☐ **Burp Suite** - 抓包查看加密后的数据
- ☐ **CyberChef** - 在线加密/解密工具（https://gchq.github.io/CyberChef/）

- --

## 前置条件

## # ✅ 确认清单

```bash
# 1. Frida 正常运行
frida-ps -U

# 2. jadx-gui 已安装
jadx-gui --version

# 3. 抓包环境已配置（可选）
# 参考: network_sniffing.md

````

---

## 解决方案

## # 第 1 步：识别加密算法（5 分钟）

## # # 1.1 搜索特征字符串

- _用 jadx-gui 打开 APK_，全局搜索：

```

# 非对称加密
RSA
ECC

# 哈希算法
MD5
SHA
SHA256
HMAC

# 加密模式
ECB
CBC
CTR
GCM

# Padding
PKCS5Padding
PKCS7Padding

# Encode
Base64

```

```java
// Java LayerEncrypt API
javax.crypto.Cipher
javax.crypto.spec.SecretKeySpec
javax.crypto.spec.IvParameterSpec
javax.crypto.Mac
java.security.Signature
java.security.MessageDigest

// Base64 Encode
android.util.Base64
java.util.Base64

```

unzip app.apk -d app_unzipped

# Search .so FileInEncryptLibrary

strings app*unzipped/lib/*/lib\_.so | grep -i -E "openssl|crypto|encrypt|aes|rsa"

# or 用 ToolAnalyze

rabin2 -z app_unzipped/lib/arm64-v8a/libnative.so | grep -i encrypt

````

_示例_：假设你搜到了 `AES/CBC/PKCS5Padding`

1. 在 jadx 中点击这个字符串
2. 查看交叉引用（`X` 键或右键 → Find Usage）
3. 跳转到使用这个字符串的函数

_典型代码模式_：

```java
// 你可能会看到类似这样的代码
public static String encrypt(String plaintext) {
Cipher cipher = Cipher.getInstance("AES/CBC/PKCS5Padding");
SecretKeySpec key = new SecretKeySpec(KEY_BYTES, "AES");
IvParameterSpec iv = new IvParameterSpec(IV_BYTES);
cipher.init(Cipher.ENCRYPT_MODE, key, iv);
byte[] encrypted = cipher.doFinal(plaintext.getBytes());
return Base64.encodeToString(encrypted, Base64.DEFAULT);
}

````

密钥 Variable: KEY_BYTES
IV Variable: IV_BYTES
EncryptFunction: com.example.app.CryptoUtils.encrypt()

````

<details>
<summary><b>📍 位置 1: Java 代码硬编码（难度：）</b></summary>

* *查找方法**：

```java
// 搜索关键词
SecretKeySpec
byte[] key
private static final byte[]

````

private static final byte[] KEY = {
0x12, 0x34, 0x56, 0x78,
0x9a, 0xbc, 0xde, 0xf0,
// ... 16/24/32 字节
};

````
- AES-256: 32 字节


</details>

<details>
<summary><b>📍 位置 2: 资源文件（难度：）</b></summary>

* *查找路径**：

```bash
# Check assets Directory
ls app_unzipped/assets/

# Check res/raw
ls app_unzipped/res/raw/

# 搜索二进制文件
find app_unzipped -type f -exec file {} \; | grep data

````

- `secret.key`

</details>

<details>
<summary><b>📍 位置 3: Native (.so) 硬编码（难度：）</b></summary>

- _IDA Pro 分析_：

1. 打开 `.so` 文件
2. 跳转到 **Strings** 窗口 (`Shift+F12`)
3. 搜索关键字符串
4. 查看交叉引用找到使用密钥的函数

- _Ghidra 分析_：

1. 导入 `.so` 文件
2. 搜索 → For Strings
3. 筛选长度为 16/24/32 的可疑字符串

</details>

<details>
<summary><b>📍 位置 4: 动态生成（难度：）</b></summary>

_特征_：密钥通过算法计算，常见方式：

```java
// 基于设备信息生成
String deviceId = getDeviceId();
byte[] key = MD5(deviceId + SALT);

// 基于时间戳
long timestamp = System.currentTimeMillis();
byte[] key = HMACSHA256(timestamp, SECRET);

```

_特征_：

- 启动时从服务器获取密钥
- 可能经过 RSA 加密传输

_对策_：

1. 抓包查看密钥传输
2. Hook 网络请求获取密钥
3. 或直接 Hook 加密函数（密钥已在内存中）

</details>

---

## # 第 4 步：动态提取密钥（15 分钟）

_终级方法_：无论密钥藏在哪，只要加密函数被调用，Hook 就能抓到

## # # 4.1 Hook Java 层加密

_通用 AES Hook 脚本_ `dump_aes_key.js`：

```javascript
Java.perform(function () {
  console.log("\n [Crypto Hook] started\n");

  // Hook Cipher.init
  var Cipher = Java.use("javax.crypto.Cipher");
  Cipher.init.overload(
    "int",
    "java.security.Key",
    "java.security.spec.AlgorithmParameterSpec"
  ).implementation = function (opmode, key, spec) {
    console.log("\n🔐 [Cipher.init] captured!");

    // 模式
    var mode = opmode == 1 ? "ENCRYPT" : "DECRYPT";
    console.log(" mode: " + mode);

    // 算法
    console.log(" algo: " + this.getAlgorithm());

    // 提取密钥
    try {
      var secretKey = Java.cast(
        key,
        Java.use("javax.crypto.spec.SecretKeySpec")
      );
      var keyBytes = secretKey.getEncoded();
      var Base64 = Java.use("android.util.Base64");
      console.log(" key (Base64): " + Base64.encodeToString(keyBytes, 0));
      console.log(" key (Hex): " + bytesToHex(keyBytes));
    } catch (e) {
      console.log(" key classNames: " + key.$className);
    }

    // 提取 IV
    if (spec) {
      try {
        var ivSpec = Java.cast(
          spec,
          Java.use("javax.crypto.spec.IvParameterSpec")
        );
        var ivBytes = ivSpec.getIV();
        console.log(" IV (Hex): " + bytesToHex(ivBytes));
      } catch (e) {}
    }

    return this.init(opmode, key, spec);
  };

  // Hook Cipher.doFinal
  Cipher.doFinal.overload("[B").implementation = function (input) {
    var result = this.doFinal(input);

    console.log("\n📦 [Cipher.doFinal] captured!");
    console.log(" InputLength: " + input.length);
    console.log(" OutputLength: " + result.length);
    console.log(
      " InputData (first 32 bytes): " + bytesToHex(input.slice(0, 32))
    );
    console.log(
      " OutputData (first 32 bytes): " + bytesToHex(result.slice(0, 32))
    );

    return result;
  };

  function bytesToHex(bytes) {
    var hex = [];
    for (var i = 0; i < bytes.length && i < 32; i++) {
      hex.push(("0" + (bytes[i] & 0xff).toString(16)).slice(-2));
    }
    return hex.join(" ");
  }

  console.log("✅ [Crypto Hook] configured\n");
});
```

```
key (Base64): MTIzNDU2Nzg5MGFiY2RlZg==
密钥 (Hex): 31 32 33 34 35 36 37 38 39 30 61 62 63 64 65 66
IV (Hex): 66 65 64 63 62 61 30 39 38 37 36 35 34 33 32 31

📦 [Cipher.doFinal] captured!
InputLength: 128
OutputLength: 144
InputData (first 32 bytes): 7b 22 75 73 65 72 6e 61 6d 65 22 3a ...
OutputData (first 32 bytes): a3 b2 c1 d0 e4 f5 ...

```

# 使用 nm 查看函数

nm -D libnative.so | grep -i encrypt

# 使用 Frida

frida -U -f com.example.app

> Module.enumerateExports('libnative.so').filter(e => e.name.includes('encrypt'))

```

Interceptor.attach(Module.findExportByName('libnative.so', 'Java_com_example_Crypto_encrypt'), {
onEnter: function(args) {
console.log("\n [Native Encrypt] Call!");

// args[0] = JNIEnv*
// args[1] = jclass
// args[2] = 第一个参数（通常是明文）
// args[3] = 第二个参数（可能是密钥）

// 读取字符串参数
var plaintext = Java.vm.getEnv().getStringUtfChars(args[2], null).readCString();
console.log(" 明文: " + plaintext);

// 读取字节数组参数
this.keyPtr = args[3]; // 保存指针用于后续读取
},
onLeave: function(retval) {
// retval 是返回值（密文）
console.log(" 返回值: " + retval);
}

});

```

1. 选择操作：`AES Decrypt`
2. 输入：

| 项目          | 说明                  |
| ------------- | --------------------- |
| **Key** (Hex) | `31 32 33 34 ...`     |
| **IV** (Hex)  | `66 65 64 63 ...`     |
| **Mode**      | `CBC`                 |
| **Input**     | 密文（Base64 或 Hex） |
| **Key** (Hex) | `31 32 33 34 ...`     |
| **IV** (Hex)  | `66 65 64 63 ...`     |
| **Mode**      | `CBC`                 |
| **Input**     | 密文（Base64 或 Hex） |

3. 点击 **Bake!**

- **如果解密成功\*\***，说明密钥正确！

## # 5.2 Python 脚本验证

```python
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64

# 从 Frida 获取密钥和 IV（Hex 转 bytes）
key = bytes.fromhex('31 32 33 34 35 36 37 38 39 30 61 62 63 64 65 66')
iv = bytes.fromhex('66 65 64 63 62 61 30 39 38 37 36 35 34 33 32 31')

# 从抓包获取密文
ciphertext = base64.b64decode('YWJjZGVmZ2hpamtsbW5vcA==')

# 解密
cipher = AES.new(key, AES.MODE_CBC, iv)
plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)

print("解密结果:", plaintext.decode())

```

Java.perform(function() {
var CryptoUtils = Java.use('com.example.app.CryptoUtils');

// CallEncryptFunction
var encrypted = CryptoUtils.encrypt("Hello World");
console.log("EncryptResult: " + encrypted);

// CallDecryptFunction
var decrypted = CryptoUtils.decrypt(encrypted);
console.log("DecryptResult: " + decrypted);

});

```

| 算法类型 | 算法 | 密钥长度 | 用途 |
| -------------- | ------- | ------------------ | ---------------- |
| **对称加密** | AES | 128/192/256 bit | 加密数据 |
| | DES | 56 bit | 旧标准（不安全） |
| | 3DES | 168 bit | DES 增强版 |
| **非对称加密** | RSA | 1024/2048/4096 bit | 密钥交换、签名 |
| | ECC | 256/384/521 bit | RSA 的高效替代 |
| **哈希** | MD5 | 128 bit 输出 | 校验（不安全） |
| | SHA-256 | 256 bit 输出 | 安全哈希 |
| | HMAC | 可变 | 带密钥的哈希 |

## # AES 加密流程

```

[AES Encrypt] ← Use 密钥 + IV
↓
密文 Data
↓
[Base64 Encode] ← 便于传输
↓
最终密文

````

- --

## 常见问题

## # ❌ 问题 1: Hook 脚本不生效

_症状_：运行 Frida 脚本后没有任何输出

_检查_：

1. **确认加密函数被调用了吗？**

```javascript
Java.use("javax.crypto.Cipher").$init.overload().implementation = function () {
console.log("[TEST] Cipher 实例化");
return this.$init();
};

````

→ 改用 Native Hook

3. **类名可能被混淆**
   → 搜索所有包含 `Cipher` 的类：

```javascript
Java.enumerateLoadedClasses({
  onMatch: function (className) {
    if (className.toLowerCase().includes("cipher")) {
      console.log(className);
    }
  },
  onComplete: function () {},
});
```

_可能原因_：

1. **IV 不正确**

- 确认是否使用了 IV
- 某些实现会将 IV 附加在密文开头

2. **Padding 不匹配**

- 尝试不同的 Padding：`PKCS5Padding`, `PKCS7Padding`, `NoPadding`

3. **编码问题**

```python
# 尝试不同编码
ciphertext = base64.b64decode(data) # Base64
ciphertext = bytes.fromhex(data) # Hex
ciphertext = data.encode() # UTF-8

```

- 可能使用了 PBKDF2 等密钥派生函数
- Hook `SecretKeyFactory.generateSecret()` 查看

## # ❌ 问题 3: Native 函数找不到

_症状_：`Module.findExportByName()` 返回 `null`

_解决_：

1. **函数可能未导出**

```bash
# 查看所有符号（包括未导出）
readelf -s libnative.so | grep encrypt

```

```javascript
var baseAddr = Module.findBaseAddress('libnative.so');
var funcAddr = baseAddr.add(0x1234); // 从 IDA 获取偏移
Interceptor.attach(funcAddr, { ... });

```

```javascript
// Hook RegisterNatives
var RegisterNatives = Module.findExportByName(
  "libart.so",
  "_ZN3art3JNI15RegisterNativesEP7_JNIEnvP7_jclassPK15JNINativeMethodi"
);
Interceptor.attach(RegisterNatives, {
  onEnter: function (args) {
    var methods = ptr(args[2]);
    console.log("Register JNI Method:", methods.readCString());
  },
});
```

_症状_：

```java
// 看到类似这样的代码
SecretKeySpec key = new SecretKeySpec("MyPassword123".getBytes(), "AES");

```

_解决方案_：

- **1. 使用密钥派生函数（KDF）\*\***

```python
from Crypto.Protocol.KDF import PBKDF2
password = "MyPassword123"
salt = b"somesalt" # 需要从代码中找到
key = PBKDF2(password, salt, dkLen=16) # 16 字节 AES-128

```

- `PBKDF2` 会将任意长度的密码派生为固定长度的密钥
- `salt` 通常在代码中硬编码或从服务器获取
- `dkLen` 决定输出密钥长度：16 (AES-128) / 24 (AES-192) / 32 (AES-256)

* **2. Hook 密钥派生函数\*\***

```javascript
var SecretKeyFactory = Java.use("javax.crypto.SecretKeyFactory");
SecretKeyFactory.generateSecret.implementation = function (keySpec) {
  var key = this.generateSecret(keySpec);
  console.log("[密钥派生] 算法:", this.getAlgorithm());
  console.log("[密钥派生] 密钥 (Hex):", bytesToHex(key.getEncoded()));

  // 尝试获取 salt（如果是 PBEKeySpec）
  try {
    var PBEKeySpec = Java.use("javax.crypto.spec.PBEKeySpec");
    var pbeSpec = Java.cast(keySpec, PBEKeySpec);
    console.log("[密钥派生] Salt:", bytesToHex(pbeSpec.getSalt()));
    console.log("[密钥派生] 迭代次数:", pbeSpec.getIterationCount());
  } catch (e) {}

  return key;
};
```

```bash
# 在代码中搜索
jadx-gui app.apk
# 搜索: getBytes()、"password"、"secret"、"key"

# 在 Frida 中枚举所有字符串字段
Java.perform(function() {
Java.choose("com.example.CryptoUtils", {
onMatch: function(instance) {
console.log("Found instance:", instance);
// 打印所有字段
var fields = instance.class.getDeclaredFields();
fields.forEach(function(field) {
field.setAccessible(true);
console.log(field.getName() + ":", field.get(instance));
});
},
onComplete: function() {}
});
});

```

```python
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import hashlib

# 从代码中找到的字符串密码
password = "MyPassword123"

# 方法 1: 直接使用前 16 字节
key = password.encode()[:16].ljust(16, b'\0')

# 方法 2: MD5 哈希（常见做法，输出正好 16 字节）
key = hashlib.md5(password.encode()).digest()

# 方法 3: SHA256 前 16 字节
key = hashlib.sha256(password.encode()).digest()[:16]

# 然后用于解密
cipher = AES.new(key, AES.MODE_CBC, iv)
plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)

```

## 延伸阅读

## # 相关配方

- **[网络抓包](./network_sniffing.md)** - 获取加密后的数据样本
- **[Frida 反调试](../Anti-Detection/frida_anti_debugging.md)** - 如果 App 检测到 Hook
- **[Native Hook 模式](../../01-Recipes/Scripts/native_hooking.md)** - 深入 Native 层分析

## # 工具深入

- **[Frida 完整指南](../../02-Tools/Dynamic/frida_guide.md)**
- **[IDA Pro 使用](../../02-Tools/Static/ida_pro_guide.md)**

## # 案例分析

- **[音乐 App 分析](../../03-Case-Studies/case_music_apps.md)** - 加密音频格式分析
- **[社交媒体风控](../../03-Case-Studies/case_social_media_and_anti_bot.md)** - API 签名算法逆向

## # 理论基础

- **[密码学基础知识](../../04-Reference/Foundations/)** - TODO

---

## 快速参考

## # Hook 脚本模板库

_1. 通用 AES Hook_

```javascript
var Cipher = Java.use("javax.crypto.Cipher");
Cipher.init.overload("int", "java.security.Key").implementation = function (
  opmode,
  key
) {
  console.log("[RSA] 模式:", opmode == 1 ? "ENCRYPT" : "DECRYPT");
  console.log("[RSA] 密钥ClassType:", key.$className);

  // Get公钥/私钥
  if (key.$className.includes("PublicKey")) {
    console.log("[RSA] 公钥:", key.getEncoded());
  } else if (key.$className.includes("PrivateKey")) {
    console.log("[RSA] 私钥:", key.getEncoded());
  }

  return this.init(opmode, key);
};

var Mac = Java.use("javax.crypto.Mac");
Mac.init.implementation = function (key) {
  console.log("[HMAC] 算法:", this.getAlgorithm());

  var secretKey = Java.cast(key, Java.use("javax.crypto.spec.SecretKeySpec"));
  console.log("[HMAC] 密钥:", secretKey.getEncoded());

  return this.init(key);
};

Mac.doFinal.overload("[B").implementation = function (data) {
  var result = this.doFinal(data);
  console.log("[HMAC] Input:", data);
  console.log("[HMAC] Output:", result);
  return result;
};

var Base64 = Java.use("android.util.Base64");
Base64.decode.overload("java.lang.String", "int").implementation = function (
  str,
  flags
) {
  var result = this.decode(str, flags);
  console.log("[Base64] Decode:");
  console.log(" Input:", str.substring(0, 50) + "...");
  console.log(" Output (Hex):", bytesToHex(result));
  return result;
};
```

# AES Encrypt

echo "Hello" | openssl enc -aes-128-cbc -K 3132333435363738393061626364656666 -iv 6665646362613039383736353433323120 -base64

# AES Decrypt

echo "密文" | base64 -d | openssl enc -d -aes-128-cbc -K ... -iv ...

# Generate MD5

echo -n "text" | openssl md5

# Generate SHA256

echo -n "text" | openssl sha256

# RSA 密钥生成

openssl genrsa -out private.pem 2048
openssl rsa -in private.pem -pubout -out public.pem

```

```

<!-- 01-Recipes/Network/ja3_fingerprinting.md -->

# JA3 TLS 指纹识别技术详解

JA3 是一种创建 SSL/TLS 客户端指纹的方法，旨在轻松识别网络上的客户端应用程序。当客户端与服务器建立加密连接时，它首先会发送一个 `Client Hello` 包。这个包的格式和内容在很大程度上取决于用于创建连接的客户端应用程序（例如浏览器、恶意软件、移动 App）中的库和方法。JA3 通过收集 `Client Hello` 包中特定字段的值，并将它们组合成一个易于共享和比较的 MD5 哈希值，从而为客户端生成一个独特的"指纹"。

---

## 目录

- [工作原理](#工作原理)
- [指纹生成过程](#指纹生成过程)
- [JA3S - 服务器端指纹](#ja3s---服务器端指纹)
- [应用场景](#应用场景)
- [局限性](#局限性)
- [如何检测 JA3](#如何检测-ja3)

---

### 工作原理

JA3 指纹的核心思想是：**客户端的 `Client Hello` 包暴露了其身份**。

一个 `Client Hello` 包包含了客户端希望如何与服务器进行通信的各种细节。JA3 方法精确地选择了以下 5 个字段，并按照特定顺序将它们串联起来：

1. **SSL/TLS Version (版本号)**: 客户端支持的最高 TLS 版本。
2. **Accepted Ciphers (加密套件)**: 客户端愿意接受的加密套件列表，按其偏好顺序排列。
3. **List of Extensions (扩展列表)**: `Client Hello` 中包含的所有扩展，按其出现顺序排列。
4. **Elliptic Curves (椭圆曲线)**: 客户端支持的椭圆曲线列表。
5. **Elliptic Curve Point Formats (椭圆曲线点格式)**: 支持的点格式列表。

这些字段的组合对于特定的客户端应用程序（及其版本）来说通常是独一无二的。例如，Chrome 浏览器、Firefox 浏览器、Tor 浏览器和一个 Golang 编写的僵尸网络程序，它们生成的 `Client Hello` 在这些字段上会有明显的差异。

---

### 指纹生成过程

生成 JA3 指纹的步骤如下：

1. **收集字段值**: 从一个 TCP 会话的 `Client Hello` 包中，提取上述 5 个字段的十进制值。
2. **格式化和拼接**:
   - 每个字段内的值用 `-` 分隔。
   - 5 个主要字段之间用 `,` 分隔。
   - 例如，一个 JA3 字符串看起来像这样：`771,4865-4866-4867-49195-49199-...,23-65281-10-11-35-16-0-13-18,29-23-24,0`
3. **计算 MD5 哈希**: 对上述拼接好的字符串计算 MD5 哈希值。
4. **最终指纹**: 得到的 32 位十六进制字符串就是该客户端的 JA3 指纹。
   - 例如，上述字符串的 MD5 哈希可能是：`e7d705a3286e19ea42f587b344ee6865`。

这个最终的 MD5 哈希就是可用于识别、共享和查询的 JA3 指纹。

---

### JA3S - 服务器端指纹

与 JA3 对应，**JA3S** 是对服务器响应的指纹。它基于服务器在 `Server Hello` 包中选择的参数。JA3S 收集以下字段：

1. **SSL/TLS Version**
2. **Selected Cipher**
3. **List of Extensions**

将这些值拼接并进行 MD5 哈希，就得到了 JA3S 指纹。

**为什么 JA3S 很重要？**

将 JA3 和 JA3S 结合起来，可以提供对加密连接的更强洞察力。例如，一个恶意软件 (JA3) 可能会尝试连接多个不同的 C2 服务器 (不同的 JA3S)。反之，一个 C2 服务器 (JA3S) 可能会接受来自不同类型恶意软件 (不同的 JA3) 的连接。这种组合分析可以更精确地描绘出威胁活动的全貌。

---

### 应用场景

- **恶意软件家族识别**: 许多恶意软件家族（如 Trickbot, Emotet）使用特定的 SSL/TLS 库，导致它们具有独特且一致的 JA3 指纹。安全分析师可以创建规则来检测或阻止已知的恶意 JA3 哈希。
- **僵尸网络检测**: 僵尸网络中的客户端通常是相同的程序，因此它们的 JA3 指纹也是相同的。这使得大规模识别受感染主机成为可能。
- **威胁情报共享**: JA3 指纹是一个优秀的技术性"失陷指标"(IOC)。安全社区可以共享已知的恶意 JA3 列表，就像共享恶意 IP 地址或域名一样。
- **识别非标准应用**: 可以用于识别组织内部网络中不合规或非标准的应用程序。

---

### 局限性

尽管 JA3 非常有用，但它也有一些明显的缺点：

- **指纹冲突**: 不同的应用程序可能偶然会使用相同的加密库和配置，从而产生相同的 JA3 指纹。
- **容易被规避 (Spoofing)**: 只要攻击者有能力修改其客户端的 SSL/TLS 库，他们就可以刻意模仿一个常见、合法的应用程序（如 Chrome 浏览器）的 `Client Hello` 包，从而生成一个"合法"的 JA3 指纹来逃避检测。这种技术被称为"JA3 欺骗"。
- **指纹随版本变化**: 当一个合法应用（如 Chrome）更新时，它的 TLS 实现可能会改变，导致其 JA3 指纹也发生变化。这意味着维护一个准确的指纹数据库需要持续的努力。
- **信息有限**: 一个 MD5 哈希本身不包含任何信息。你无法从两个不同的哈希值看出它们对应的客户端有多相似。例如，Chrome 90 和 Chrome 91 的 JA3 哈希可能完全不同，即使它们的 `Client Hello` 包只有微小的差异。

---

### 如何检测 JA3

要实现 JA3 检测，你需要能够监控网络流量并解析 TLS 握手的工具。常见的实现方式包括：

- **网络安全监控 (NSM) 工具**: Zeek (原名 Bro) 是原生支持 JA3 和 JA3S 指纹生成的黄金标准。
- **Suricata**: 从 4.1 版本开始，Suricata 也内置了 JA3 指纹功能。
- **Wireshark**: 可以通过特定的插件或手动的 tshark 脚本来提取和计算 JA3。

<!-- 01-Recipes/Network/ja4_fingerprinting.md -->

# JA4+ TLS/QUIC 指纹识别技术详解

JA4+ 是由 FoxIO (原 Salesforce 的 JA3 团队) 开发的一套网络指纹识别方法的集合，旨在成为 JA3 的下一代演进版本。它不仅仅是对 JA3 的简单升级，而是一个更全面、更具结构化和可操作性的指纹套件，旨在解决 JA3 的核心痛点，并扩展到 QUIC 和 HTTP 等协议。

---

## 目录

1. [**为什么需要 JA4+ (JA3 的局限性)**](#为什么需要-ja4-ja3-的局限性)
2. [**JA4 的核心设计 - 不再是哈希**](#ja4-的核心设计---不再是哈希)
3. [**JA4+ 套件概览**](#ja4-套件概览)
   - [**JA4** (客户端 TLS)](#ja4-客户端-tls)
   - [**JA4S** (服务器端 TLS)](#ja4s-服务器端-tls)
   - [**JA4H** (HTTP 客户端)](#ja4h-http-客户端)
   - [**JA4X** (TLS 证书)](#ja4x-tls-证书)
   - [**JA4L** (实验性)](#ja4l-实验性)
4. [**JA4 vs JA3：核心优势**](#ja4-vs-ja3核心优势)
5. [**应用与实践**](#应用与实践)

---

## 为什么需要 JA4+ (JA3 的局限性)

JA3 是一个非常成功的技术，但其核心设计——一个单一的 MD5 哈希——带来了几个无法克服的挑战：

- **缺乏上下文**: 一个 MD5 哈希是不透明的。`e7d705a3...` 和 `a8d9b1c2...` 这两个哈希值，我们无法判断它们代表的客户端有多相似。可能只是 TLS 扩展顺序的一个微小变化，就导致了完全不同的哈希。
- **"雪崩效应"**: 客户端的任何微小更新（例如，Chrome 101 -> 102）都可能导致 JA3 哈希完全改变，使得基于精确匹配的规则变得非常脆弱。
- **难以进行模糊搜索**: 无法进行"搜索所有使用 TLS 1.3 但不包含某个特定加密套件的客户端"这样的灵活查询。
- **易于被模仿**: 攻击者只需要精确复现 `Client Hello` 的特定字段，就能完全复制一个合法应用的 JA3 哈希。

JA4+ 的诞生就是为了解决这些问题。

---

## JA4 的核心设计 - 不再是哈希

JA4 最大的革新是**放弃了单一、不透明的哈希值**，转而采用一种**结构化、人类可读的字符串格式**。这使得指纹本身就携带了丰富的上下文信息。

JA4 的指纹格式为：`Protocol_Version_Ciphers_Extensions_Signature`，每个部分都有特定的含义和构造方法。

一个典型的 JA4 指纹例子：`t13d1516h2_174735a34e8a_b2149a751699`

我们来分解它：

- **`t` (Protocol)**: 协议。`t` 代表 TLS, `q` 代表 QUIC。
- **`13` (TLS Version)**: `Client Hello` 中支持的最高 TLS 版本。`12` = TLS 1.2, `13` = TLS 1.3。
- **`d1516h2` (Ciphers & Extensions Count)**:
  - `d`: 客户端支持的加密套件是有序的 (sorted)。`i` 表示无序 (insipid)。
  - `15`: 客户端提供了 15 个加密套件。
  - `16`: 客户端提供了 16 个扩展。
  - `h2`: 客户端在 `Client Hello` 中使用了 2 个 GREASE (Generate Random Extensions And Sustain Extensibility) 值，这通常是现代浏览器的特征。
- **`_` (分隔符)**
- **`174735a34e8a` (Extensions)**: 这是对**有序的**扩展列表进行特定算法计算后得到的**部分哈希**。相似的扩展列表会产生相似的哈希前缀。
- **`_` (分隔符)**
- **`b2149a751699` (Signature Algorithms)**: 这是对签名算法和支持的组（椭圆曲线）进行部分哈希计算后得到的值。

这种结构使得指纹既能用于精确匹配，也能用于强大的模糊匹配。

---

## JA4+ 套件概览

JA4+ 不是单一的工具，而是一个方法论集合。

### JA4 (客户端 TLS)

- **目标**: 识别发起 TLS 连接的客户端应用。
- **格式**: 如上所述的 `p_v_c_e_s` 结构。

### JA4S (服务器端 TLS)

- **目标**: 识别响应 TLS 连接的服务器应用。
- **格式**: `p_v_c_e`，比客户端指纹稍简单。
  - 例如：`t13d03_a06f30d07525`
  - `t` = TLS, `13` = TLS 1.3, `d` = 有序, `03` = 3 个扩展, `a06...` = 扩展的部分哈希。
- **应用**: 将 JA4 和 JA4S 结合，可以进行更精准的匹配，例如"只告警这个特定 JA4 连接到这个特定 JA4S 的行为"。

### JA4H (HTTP 客户端)

- **目标**: 对 HTTP 请求进行指纹识别，作为对 JA4 的补充。
- **格式**: `p_m_v_h`
  - `p`: 协议 (`h`=HTTP/1, `h2`=HTTP/2)。
  - `m`: 请求方法 (`g`=GET, `p`=POST)。
  - `v`: HTTP 版本。
  - `h`: 对 HTTP Header 的特定组合进行哈希。
- **应用**: 可以用来检测 JA4 欺骗。例如，一个声称自己是 Chrome 的 JA4 指纹，却发送了不符合 Chrome 行为的 JA4H 指纹，这很可能是一个恶意客户端。

### JA4X (TLS 证书)

- **目标**: 对 TLS 证书链进行指纹识别。
- **应用**: 快速识别自签名证书、特定恶意软件使用的证书等。

### JA4L (实验性)

- **L** for **L**ightweight。这是一个更简单的版本，只包含数字和计数，不包含哈希。
- **应用**: 适用于性能极高或资源受限的环境，提供基本的模糊匹配能力。

---

## JA4 vs JA3：核心优势

| 特性         | JA4+                          | JA3                |
| :----------- | :---------------------------- | :----------------- |
| **格式**     | **结构化字符串**              | 单一 MD5 哈希      |
| **可读性**   | **高**，指纹本身包含信息      | **无**             |
| **模糊匹配** | **原生支持**，可按部分查询    | 否                 |
| **上下文**   | **丰富** (协议, 版本, 计数)   | 无                 |
| **欺骗难度** | **更高**，需匹配行为逻辑      | 较低，只需匹配字段 |
| **覆盖范围** | TLS, QUIC, HTTP, Certificates | 仅 TLS             |
| **健壮性**   | **高**，微小变化不影响大局    | 低，"雪崩效应"     |

---

## 应用与实践

JA4+ 的应用场景比 JA3 更广泛和深入：

- **高级威胁狩猎**:

<!-- 01-Recipes/Network/network_sniffing.md -->

# Recipe: 抓包分析 android 应用的网络流量

## 问题场景

- _你遇到了什么问题？_

* ❓ 想知道某个 App 调用了哪些 API 接口
* ❓ 需要分析 API 的请求参数和响应数据
* ❓ 想查看 App 发送了哪些敏感信息（设备信息、定位等）
* ❓ 需要找到加密签名的生成逻辑
* ❓ 想重放或修改 API 请求

- _本配方教你_：配置抓包环境，拦截并分析 HTTPS 流量，绕过 SSL Pinning 限制。

- _预计用时_: 15-30 分钟（首次配置）

---

## 工具清单

## # 必需工具

- ☐ _Android 设备/模拟器_（已 Root，或可安装证书）
- ☐ _抓包代理工具_（选择其一）：
  - Burp Suite（推荐，功能最强）
  - Charles（UI 友好）
  - mitmproxy（开源，可编程）
- ☐ _Frida_（用于绕过 SSL Pinning）

## # 可选工具

- ☐ _Wireshark_（分析底层 TCP/UDP 流量）
- ☐ _HttpCanary_（Android 上的抓包工具，无需 PC）

---

## 前置条件

## # ✅ 确认清单

```bash
# 1. Verify device connection
adb devices

# 2. Frida 可用
frida-ps -U

# 3. PC and phone on the same Wi-Fi network
# Record PC IP address（used below as YOUR_PC_IP）
# Windows: ipconfig
# macOS/Linux: ifconfig or ip addr

```

- _Android 7.0+_：需要 Root 权限安装系统证书
- _Android 6.0-_：可直接安装用户证书，无需 Root
- 或使用支持用户证书的 App（Target SDK < 24）

---

## 解决方案

## # 第 1 步：配置抓包工具（5 分钟）

<details>
<summary><b>使用 Burp Suite（推荐）</b></summary>

### 1.1 启动 Burp Suite

```bash
# Download Burp Suite Community Edition (free)
# https://portswigger.net/burp/communitydownload

# Run the command
java -jar burpsuite_community.jar

```

1. 打开 _Proxy_ → _Options_
2. 在 _Proxy Listeners_ 部分
3. 点击 _Add_，配置：

- _Bind to port_: `8888`
- _Bind to address_: `All interfaces`（或选择你的 Wi-Fi 网卡）

4. 点击 _OK_ 保存

![Burp Proxy配置](../../images/burp_proxy_config.png)

✅ _验证_：浏览器访问 `http://YOUR_PC_IP:8888`，应该看到 Burp 的错误页面（表示代理工作正常）

</details>

<details>
<summary><b>使用 Charles</b></summary>

### 1.1 启动 Charles

下载：https://www.charlesproxy.com/download/

### 1.2 配置代理

1. _Proxy_ → _Proxy Settings_
2. 设置 Port 为 `8888`
3. 勾选 _Enable transparent HTTP proxying_

</details>

<details>
<summary><b>使用 mitmproxy</b></summary>

```bash
# Install
pip install mitmproxy

# startup（监听 8888 端口）
mitmproxy -p 8888 --listen-host 0.0.0.0

# 或使用 Web 界面
mitmweb -p 8888 --listen-host 0.0.0.0
# 访问 http://127.0.0.1:8081 查看流量

```

---

## # 第 2 步：配置手机代理（2 分钟）

### 2.1 连接到同一 Wi-Fi

确保手机和 PC 在*同一局域网*。

### 2.2 设置手动代理

1. 打开手机 _设置_ → _Wi-Fi_
2. *长按*当前连接的 Wi-Fi → _修改网络_
3. 展开 _高级选项_
4. 代理设置改为 _手动_：

- _代理服务器主机名_: `YOUR_PC_IP`（如 `192.168.1.100`）
- _代理服务器端口_: `8888`

5. 保存

### 2.3 验证代理连接

```bash
# 手机浏览器访问任意 HTTP 网站（如 http://example.com）
# 此时 Burp/Charles 应该显示拦截到的请求

```

## # 第 3 步：安装 HTTPS 证书（5-10 分钟）

_为什么需要？_ HTTPS 流量经过加密，需要安装证书才能解密查看。

<details>
<summary><b>Burp Suite 证书安装</b></summary>

### 3.1 下载证书

1. 手机浏览器访问 `http://burp`
2. 点击 _CA Certificate_ 下载 `cacert.der`

### 3.2 安装证书

- _Android 7.0+ （需要 Root）_：

```bash
# 1. 转换证书格式
openssl x509 -inform DER -in cacert.der -out cacert.pem

# 2. 计算证书哈希
HASH=$(openssl x509 -inform PEM -subject_hash_old -in cacert.pem | head -1)

# 3. 重命名并推送到系统目录
cp cacert.pem $HASH.0
adb root
adb remount
adb push $HASH.0 /system/etc/security/cacerts/
adb shell chmod 644 /system/etc/security/cacerts/$HASH.0

# 4. 重启设备
adb reboot

```

<details>
<summary><b>Charles 证书安装</b></summary>

1. 手机浏览器访问 `http://chls.pro/ssl`
2. 下载并安装证书
3. Android 7.0+ 同样需要安装到系统目录（参考 Burp 步骤）

</details>

<details>
<summary><b>mitmproxy 证书安装</b></summary>

1. 手机浏览器访问 `http://mitm.it`
2. 点击 Android 图标下载证书
3. 安装步骤同上

</details>

---

## # 第 4 步：开始抓包（1 分钟）

### 4.1 清空旧记录

- _Burp_: Proxy → HTTP history → 右键 → _Clear history_
- _Charles_: Proxy → _Clear Session_

### 4.2 启动目标 App

在手机上打开要分析的应用，正常使用。

### 4.3 查看流量

在抓包工具中：

- 查看 HTTP history / Sequence
- 筛选目标 App 的域名
- 分析 Request/Response 内容

_示例分析点_：

- 请求 URL 和参数
- Request Headers（`User-Agent`, `Authorization`, 自定义签名头）
- Request Body（POST 数据）
- Response Body（API 返回的 JSON/XML）

---

## # 第 5 步：绕过 SSL Pinning（如遇到）

_症状_：

- 证书已安装，但 HTTPS 请求仍无法抓取
- App 显示"网络错误"或直接闪退
- 抓包工具显示 SSL 握手失败

* _原因_：App 启用了 SSL Pinning（证书锁定），拒绝信任系统证书。

### 方法 1: 使用 Frida 通用脚本（推荐）

_下载脚本_ `bypass_ssl_pinning.js`：

```javascript
// Universal android SSL Pinning Bypass
Java.perform(function () {
  console.log(" [SSL Pinning Bypass] 已Start/Boot");

  // 拦截 TrustManagerImpl (常用)
  try {
    var TrustManagerImpl = Java.use(
      "com.android.org.conscrypt.TrustManagerImpl"
    );
    TrustManagerImpl.verifyChain.implementation = function (
      untrustedChain,
      trustAnchorChain,
      host,
      clientAuth,
      ocspData,
      tlsSctData
    ) {
      console.log("✓ [TrustManagerImpl] BypassCertValidate: " + host);
      return untrustedChain;
    };
  } catch (e) {
    console.log("! TrustManagerImpl 不存At");
  }

  // Hook OkHttp3
  try {
    var CertificatePinner = Java.use("okhttp3.CertificatePinner");
    CertificatePinner.check.overload(
      "java.lang.String",
      "java.util.List"
    ).implementation = function (hostname, peerCertificates) {
      console.log("✓ [OkHttp3] Bypass SSL Pinning: " + hostname);
      return;
    };
  } catch (e) {
    console.log("! OkHttp3 不存At");
  }

  // Hook SSLContext
  try {
    var SSLContext = Java.use("javax.net.ssl.SSLContext");
    SSLContext.init.overload(
      "[Ljavax.net.ssl.KeyManager;",
      "[Ljavax.net.ssl.TrustManager;",
      "java.security.SecureRandom"
    ).implementation = function (keyManager, trustManager, secureRandom) {
      console.log("✓ [SSLContext] Use自Define TrustManager");
      this.init(keyManager, null, secureRandom);
    };
  } catch (e) {
    console.log("! SSLContext hook Failed");
  }

  console.log(" [SSL Pinning Bypass] Config完成\n");
});
```

```bash
# 方式1：附加到运行中的 App
frida -U com.example.app -l bypass_ssl_pinning.js

# 方式2：启动 App 并注入
frida -U -f com.example.app -l bypass_ssl_pinning.js --no-pause

```

```
[SSL Pinning Bypass] Config完成

```

### 方法 2: 使用 Xposed 模块

<details>
<summary><b>JustTrustMe 安装步骤</b></summary>

1. 确保设备已安装 Xposed Framework
2. 下载 JustTrustMe 模块：https://github.com/Fuzion24/JustTrustMe
3. 在 Xposed Installer 中激活
4. 重启设备

### 方法 3: 修改 APK（重打包）

<details>
<summary><b>APK 重打包步骤</b></summary>

如果 Frida 被检测，可以修改 APK 来信任用户证书：

1. 反编译 APK
2. 修改 `AndroidManifest.xml`，添加：

```xml
<application android:networkSecurityConfig="@xml/network_security_config">

```

```xml
<network-security-config>
<base-config cleartextTrafficPermitted="true">
<trust-anchors>
<certificates src="system" />
<certificates src="user" />
</trust-anchors>
</base-config>
</network-security-config>

```

</details>

---

## 工作原理

## # MITM（中间人攻击）流程

````
2. 代理解密请求（使用安装的证书）
3. 代理重新加密并转发到真实服务器
4. 服务器响应经过代理返回给 App
    ```

## # SSL Pinning 是什么？

App 内置了服务器证书的指纹（Hash），只信任特定证书：

```java
CertificatePinner pinner = new CertificatePinner.Builder()
.add("api.example.com", "sha256/AAAAAAAAAA...")
.build();

````

## # ❌ 问题 1: 手机无法连接代理

_症状_：浏览器显示"无法连接到代理服务器"

_检查_：

1. PC 和手机是否在同一 Wi-Fi？
2. PC 防火墙是否允许 8888 端口？

```bash
# Windows 防火墙规则（以管理员身份运行）
netsh advfirewall firewall add rule name="Burp Proxy" dir=in action=allow protocol=TCP localport=8888

# macOS
# 系统偏好设置 → 安全性与隐私 → 防火墙选项 → 允许 Java

```

```bash
# 检查端口
netstat -an | grep 8888 # macOS/Linux
netstat -an | findstr 8888 # Windows

```

_症状_：浏览器显示证书无效

_Android 7.0+ 限制_：

- 默认只信任系统证书
- 必须将证书安装到 `/system/etc/security/cacerts/`（需要 Root）

_无 Root 设备的解决方案_：

- 使用 Magisk + MagiskTrustUserCerts 模块
- 或修改 APK（参考方法 3）

## # ❌ 问题 3: Frida 脚本不生效

_可能原因_：

1. _App 使用了自定义网络库_
   → 需要定位具体的类名和方法，定制 Hook 脚本

2. _Frida 被检测_
   → 使用重命名的 frida-server：

```bash
adb push frida-server /data/local/tmp/random_name
adb shell "/data/local/tmp/random_name &"

```

→ Hook 所有进程：

```bash
frida-ps -U # 找到所有进程
frida -U -p PID1 -p PID2 -l script.js

```

_可能原因_：

1. _使用了 HTTP/2 或 QUIC_
   → Burp Suite → Proxy → Options → HTTP/2 → 勾选"Enable HTTP/2"

2. _直接使用 Socket 通信_
   → 需要使用 Wireshark 或 tcpdump 抓取原始 TCP 包

3. _加密的自定义协议_
   → 需要逆向分析加密算法并解密

---

## 延伸阅读

## # 相关配方

- _[密码学分析](./crypto_analysis.md)_ - 分析 API 签名和加密算法
- _[Frida 反调试绕过](../Anti-Detection/frida_anti_debugging.md)_ - 如果 App 检测到 Frida
- _[TLS 指纹分析](./tls_fingerprinting_guide.md)_ - 理解 TLS 指纹技术

## # 工具深入

- _[Frida 完整指南](../../02-Tools/Dynamic/frida_guide.md)_
- _[Burp Suite 使用技巧]_ - TODO，一个比较流氓的工具

## # 案例分析

- _[音乐 App 分析](../../03-Case-Studies/case_music_apps.md)_ - API 抓包实战
- _[社交媒体风控](../../03-Case-Studies/case_social_media_and_anti_bot.md)_ - 复杂签名分析

---

## 快速参考

## # 一键启动脚本

- _macOS/Linux_:

```bash
# !/bin/bash
# start_proxy.sh

# 获取本机 IP
IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -1)

echo "📡 代理地址: $IP:8888"
echo " 配置手机代理到: $IP:8888"
echo " 证书下载: http://burp (Burp) 或 http://mitm.it (mitmproxy)"
echo ""

# 启动 mitmproxy
mitmweb -p 8888 --listen-host 0.0.0.0

```

```batch
@echo off
REM start_proxy.bat

for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do set IP=%%a
echo 📡 代理地址: %IP%:8888
echo 配置手机代理到: %IP%:8888
pause

java -jar burpsuite_community.jar

```

```bash
# 下载通用 SSL Pinning 绕过脚本
curl -O https://codeshare.frida.re/@pcipolloni/universal-android-ssl-pinning-bypass-with-frida/

# 运行
frida -U -f com.target.app -l universal-ssl-pinning.js --no-pause

```

````



<!-- 01-Recipes/Network/tls_fingerprinting_guide.md -->

# Recipe: 使用 TLS 指纹识别检测和绕过应用指纹

## 问题场景

_你遇到了什么问题？_

- 你的自动化脚本被服务器识别并封禁了
- 你用 Python/curl 请求 API，但服务器返回 403/风控拦截
- 你想伪装成真实浏览器/官方 App 的 TLS 指纹
- 你想分析 App 使用的 TLS 库和配置
- 你想检测自己的请求是否暴露了异常的 TLS 特征

_本配方教你_：理解 TLS 指纹识别原理、如何检测自己的 TLS 指纹、以及如何伪造合法的 TLS 指纹。

_核心理念_：

> 💡 **TLS 指纹是应用的"DNA"**
>
> - TLS 握手阶段暴露了客户端使用的库和配置
> - 不同的 HTTP 客户端有不同的 TLS 指纹
> - 服务器可以通过 JA3/JA4 指纹识别你的真实身份
> - 即使使用 HTTPS，TLS 握手特征也是明文的

_预计用时_: 20-40 分钟

- --

## 工具清单

## # 必需工具

- ☐ **Wireshark** - 抓取 TLS 握手包
- ☐ **在线 JA3 检测工具** - https://ja3er.com 或 https://tls.peet.ws
- ☐ **Python 3.7+** - 用于脚本测试

## # 可选工具

- ☐ **curl-impersonate** - 伪装浏览器 TLS 指纹的 curl
- ☐ **tls-client** (Python) - 支持自定义 TLS 指纹的 HTTP 库
- ☐ **Burp Suite** - 抓包分析
- ☐ **ja3transport** (Go) - Go 语言的 TLS 伪装库

- --

## 前置条件

## # ✅ 确认清单

1. **Wireshark 已安装并可用**
2. **Python 3.7+ 环境配置完成**

```bash
# 验证 Wireshark 安装
wireshark --version

# 验证 Python 环境
python3 --version

# 安装必要的 Python 库
pip3 install requests pycurl tls-client

````

---

## 解决方案

## # 第 1 步：理解 TLS 指纹识别原理（5 分钟）

### 1.1 什么是 JA3 指纹？

_JA3_ 是一种通过分析 TLS `Client Hello` 包生成指纹的技术。

_提取的字段_：

1. TLS 版本（如 TLS 1.3 = 771）
2. 加密套件列表（Cipher Suites）
3. 扩展列表（Extensions）
4. 椭圆曲线列表（Elliptic Curves）
5. 椭圆曲线点格式（EC Point Formats）

_生成过程_：

```
拼接成String: "771,4865-4866-4867,0-23-65281,29-23-24,0"
↓
Calculate MD5 哈希
↓
JA3 指纹: e7d705a3286e19ea42f587b344ee6865

```

| **格式** | MD5 哈希 | 结构化字符串 |
| **可读性** | 无 | 高（包含版本、计数等） |
| **示例** | `e7d705a3286e19ea42f587b344ee6865` | `t13d1516h2_174735a34e8a_b2149a751699` |
| **优势** | 简单，广泛支持 | 可模糊匹配，抗干扰 |

✅ **关键点**：不同的 HTTP 库有不同的 JA3 指纹

| 客户端          | JA3 指纹                           |
| --------------- | ---------------------------------- |
| Chrome 120      | `579ccef312d18482fc42e2b822ca2430` |
| Firefox 121     | `3b5074b1b5d032e5620f69f9f700ff0e` |
| Python requests | `084c44f52a434da89e0b1bc98f8dd159` |
| curl 默认       | `51c64c77e60f3980eea90869b68c58a8` |

_问题_：如果你用 Python requests 访问服务器，即使设置了 User-Agent，服务器也能通过 JA3 识别出你不是真实浏览器

---

## # 第 2 步：检测你的 TLS 指纹（10 分钟）

### 2.1 在线检测

_方法 1：访问 JA3 检测网站_

```bash
# 用 curl 测试
curl https://ja3er.com/json

# 用 Python requests 测试
python3 << 'EOF'
import requests
r = requests.get('https://ja3er.com/json')
print(r.text)
EOF


{
"ja3": "084c44f52a434da89e0b1bc98f8dd159",
"ja3_text": "771,4865-4866-4867-49195-49199-49196-49200-52393-52392-49171-49172-156-157-47-53,0-23-65281-10-11-35-16-5-13-18-51-45-43-27-21,29-23-24,0",
"User-Agent": "python-requests/2.31.0"
}

```

curl -s https://tls.peet.ws/api/all | jq .

````
2. 过滤器输入：`tls.handshake.type == 1`（只显示 Client Hello）
3. 在终端执行请求：

```bash
curl https://example.com

````

5. 展开 **Transport Layer Security → Handshake Protocol: Client Hello**

_查看关键字段_：

````
- TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384 (0xc030)
- ...
Extension: supported_groups (len=10)
- secp256r1 (0x0017)
- x25519 (0x001d)
- ...
    ```

✅ **成功标志**：你已经看到了自己客户端的 TLS 握手特征

- --

## # 第 3 步：获取目标指纹（5 分钟）

* *目标**：获取真实浏览器或官方 App 的 JA3 指纹用于伪装

### 3.1 浏览器指纹

* *方法 1：直接查询**

Chrome 浏览器访问 https://ja3er.com/json

记录显示的 JA3 哈希值。

* *方法 2：从 GitHub 数据库查询**

访问 https://github.com/salesforce/ja3/blob/master/lists/osx-nix-ja3.csv

搜索 "Chrome"、"Safari"、"Firefox" 找到对应版本的 JA3。

### 3.2 android App 指纹

* *使用 Wireshark 抓取真实 App 的流量**：

1. 配置手机走电脑代理
2. Wireshark 监听对应网卡
3. 打开目标 App，触发网络请求
4. 过滤 `tls.handshake.type == 1` 找到 Client Hello 包
5. 记录或导出该包

* *提取 JA3**：

```bash
# Use ja3 Tool（NeedInstall）
pip3 install pyshark
python3 << 'EOF'
import pyshark
cap = pyshark.FileCapture('capture.pcap', display_filter='tls.handshake.type == 1')
for pkt in cap:
print(pkt.tls.handshake_ciphersuite)
EOF

```

## # 第 4 步：伪造 TLS 指纹（15 分钟）

### 4.1 使用 curl-impersonate（推荐）

* *curl-impersonate** 是一个修改版的 curl，能完美模拟浏览器的 TLS 指纹。

* *安装**（macOS）：

```bash
# Use Homebrew
brew install curl-impersonate

# or downloadpre-compiled version
# https://github.com/lwthiker/curl-impersonate/releases

````

curl_chrome120 https://ja3er.com/json

# 伪装成 Firefox 121

curl_ff121 https://ja3er.com/json

# 伪装成 Safari 17

curl_safari17 https://ja3er.com/json

````

### 4.2 使用 Python tls-client 库

* *安装**：

```bash
pip3 install tls-client

````

# 创建会话，伪装成 Chrome 120

session = tls_client.Session(
client_identifier="chrome_120",
random_tls_extension_order=True
)

# SendRequest

response = session.get("https://ja3er.com/json")
print(response.json())

```
"firefox_102", "firefox_104", "firefox_121"
"safari_15_3", "safari_16_0", "safari_17_0"

# 移动端
"okhttp4_android_7", "okhttp4_android_8", "okhttp4_android_13"

```

client_identifier="custom",
ja3_string="771,4865-4866-4867-49195-49199-49196-49200-52393-52392-49171-49172-156-157-47-53,0-23-65281-10-11-35-16-5-13-18-51-45-43-27-21,29-23-24,0"
)

```

```

"fmt"
"io"
"net/http"
"github.com/CUCyber/ja3transport"
)

func main() {
// Create 带 JA3 指纹 Transport
tr, \_ := ja3transport.NewTransport("771,4865-4866-4867-49195-49199-49196-49200-52393-52392-49171-49172-156-157-47-53,0-23-65281-10-11-35-16-5-13-18-51-45-43-27-21,29-23-24,0")

client := &http.Client{Transport: tr}

resp, \_ := client.Get("https://ja3er.com/json")
defer resp.Body.Close()

body, \_ := io.ReadAll(resp.Body)
fmt.Println(string(body))

}

````

* *创建对比脚本**：

```bash
# !/bin/bash

echo "=== 原生 curl ==="
curl -s https://ja3er.com/json | jq -r '.ja3'

echo ""
echo "=== curl-impersonate (Chrome) ==="
curl_chrome120 -s https://ja3er.com/json | jq -r '.ja3'

echo ""
echo "=== Python requests ==="
python3 -c "import requests; print(requests.get('https://ja3er.com/json').json()['ja3'])"

echo ""
echo "=== Python tls-client ==="
python3 << 'EOF'
import tls_client
session = tls_client.Session(client_identifier="chrome_120")
print(session.get("https://ja3er.com/json").json()['ja3'])
EOF

````

./compare_ja3.sh

```
579ccef312d18482fc42e2b822ca2430

=== Python requests ===
084c44f52a434da89e0b1bc98f8dd159

=== Python tls-client ===
579ccef312d18482fc42e2b822ca2430

```

import tls_client

# 使用伪装的 TLS 指纹

session = tls_client.Session(client_identifier="chrome_120")

headers = {
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

response = session.get('https://api.example.com/protected', headers=headers)
print(response.status_code)
print(response.text)

```
| tls-client | Chrome | Chrome | ✅ 200 OK |

- --

## 工作原理

## # TLS 握手过程

```

| |
|←-- Server Hello --------------|
| (Server JA3S 指纹) |
| |
|--- Key Exchange -------------→|
|←-- Finished ------------------|
| |
|←→ EncryptData 传输 ←→|

```

## # JA3 指纹生成细节

_原始字符串示例_：

```

29-23-24 → Supported Groups (椭圆曲线)
0 → EC Point Formats

```

```

16 → 16 Extensions
h2 → HTTP/2
\_174735... → Extensions 哈希（截断）
\_b2149a... → Signature Algorithms 哈希

````
- 可读性强（无需查表）


- --

## 常见问题

## # ❌ 问题 1: curl-impersonate 安装失败

* *症状**：Homebrew 找不到 curl-impersonate

* *解决**：

```bash
# macOS/Linux: ManualDownloadpre-compiled version
wget https://github.com/lwthiker/curl-impersonate/releases/download/v0.6.1/curl-impersonate-v0.6.1.x86_64-linux-gnu.tar.gz

tar -xzf curl-impersonate-*.tar.gz
cd curl-impersonate-*
sudo cp curl_* /usr/local/bin/

````

ValueError: Unknown client identifier: chrome_999

```
print(tls_client.settings.ClientIdentifiers)

```

- JA3 指纹是浏览器，但 HTTP 头顺序/值不对
- **解决**：使用完整的浏览器模拟（包括 HTTP/2 特征）

- JA3 指纹是浏览器，但 HTTP 头顺序/值不对
- **解决**：使用完整的浏览器模拟（包括 HTTP/2 特征）

2. **行为特征异常**

- 请求速度太快
- 缺少 Referer/Cookie
- **解决**：添加延迟、模拟真实用户行为

- 请求速度太快
- 缺少 Referer/Cookie
- **解决**：添加延迟、模拟真实用户行为

3. **IP 信誉问题**

- IP 被标记为数据中心/代理
- **解决**：使用住宅代理或轮换 IP

- IP 被标记为数据中心/代理
- **解决**：使用住宅代理或轮换 IP

4. **设备指纹**

- 服务器检测 Canvas 指纹、WebGL 指纹等
- **解决**：使用真实浏览器自动化（Selenium + undetected-chromedriver）

- 服务器检测 Canvas 指纹、WebGL 指纹等
- **解决**：使用真实浏览器自动化（Selenium + undetected-chromedriver）

## # ❌ 问题 4: 如何在 Frida 中修改 TLS 指纹？

- **场景\*\***：你想修改 Android App 的 TLS 指纹

- **方法 1：Hook Java 层 SSLSocket\*\***

```javascript
Java.perform(function () {
  var SSLSocket = Java.use("javax.net.ssl.SSLSocket");

  SSLSocket.setEnabledCipherSuites.implementation = function (suites) {
    console.log("[*] Original Cipher Suites:", suites);

    // 修改为目标指纹加密套件
    var customSuites = [
      "TLS_AES_128_GCM_SHA256",
      "TLS_AES_256_GCM_SHA384",
      "TLS_CHACHA20_POLY1305_SHA256",
    ];

    console.log("[*] ModifyAfter:", customSuites);
    return this.setEnabledCipherSuites(customSuites);
  };
});
```

## 延伸阅读

## # 相关配方

- **[网络抓包](./network_sniffing.md)** - 抓取 TLS 握手包
- **[密码学分析](./crypto_analysis.md)** - 分析加密实现
- **[JA3 指纹详解](./ja3_fingerprinting.md)** - JA3 技术深入
- **[JA4 指纹详解](./ja4_fingerprinting.md)** - JA4+ 套件详解

## # 工具深入

- **curl-impersonate 文档** - https://github.com/lwthiker/curl-impersonate
- **tls-client (Python)** - https://github.com/FlorianREGAZ/Python-Tls-Client
- **ja3transport (Go)** - https://github.com/CUCyber/ja3transport

## # 在线资源

- **JA3 检测** - https://ja3er.com
- **TLS 指纹检测** - https://tls.peet.ws
- **JA3 数据库** - https://github.com/salesforce/ja3

## # 理论基础

- **[TLS 协议详解](../../04-Reference/Advanced/)** - TODO
- **[HTTP/2 指纹](../../04-Reference/Advanced/)** - TODO

---

## 快速参考

## # 常用工具对比

| 工具                   | 语言   | 难度 | 特点                 |
| ---------------------- | ------ | ---- | -------------------- |
| **curl-impersonate**   | Bash   |      | 最简单，完美模拟     |
| **tls-client**         | Python |      | 易用，支持多种浏览器 |
| **ja3transport**       | Go     |      | 高性能，需要 Go 环境 |
| **requests + urllib3** | Python |      | 复杂，需深度定制     |

## # 快速检测脚本

- **detect_ja3.sh\*\***：

```bash
# !/bin/bash

echo " 正AtDetection TLS 指纹..."
echo ""

URL="https://ja3er.com/json"

# DetectionCurrentClient
JA3=$(curl -s "$URL" | jq -r '.ja3')
echo "你 JA3: $JA3"

# 查询已知指纹
echo ""
echo " 常见Client JA3:"
echo " Chrome 120: 579ccef312d18482fc42e2b822ca2430"
echo " Firefox 121: 3b5074b1b5d032e5620f69f9f700ff0e"
echo " Safari 17: 4e2d5f6c3e8f7a9b0c1d2e3f4a5b6c7d"
echo " Python req: 084c44f52a434da89e0b1bc98f8dd159"
echo " curl: 51c64c77e60f3980eea90869b68c58a8"

# 对比
if [ "$JA3" == "579ccef312d18482fc42e2b822ca2430" ]; then
echo ""
echo "✅ 匹配: Chrome 120"
elif [ "$JA3" == "084c44f52a434da89e0b1bc98f8dd159" ]; then
echo ""
echo "⚠️ 匹配: Python requests (容易被识别)"
else
echo ""
echo "❓ 未知指纹"
fi

```

"""
TLS 指纹伪装模板
"""
import tls_client

class BrowserSession:
"""模拟浏览器会话"""

PROFILES = {
'chrome': 'chrome_120',
'firefox': 'firefox_121',
'safari': 'safari_17_0',
'android': 'okhttp4_android_13'
}

def **init**(self, browser='chrome'):
"""Initialize 会话

Args:
browser: 浏览器 ClassType ('chrome', 'firefox', 'safari', 'android')
"""
identifier = self.PROFILES.get(browser, 'chrome_120')
self.session = tls_client.Session(
client_identifier=identifier,
random_tls_extension_order=True
)
self.\_set_headers(browser)

def \_set_headers(self, browser):
"""Setting 对应 HTTP 头"""
user_agents = {
'chrome': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
'firefox': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
'safari': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
'android': 'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.144 Mobile Safari/537.36'
}

self.session.headers.update({
'User-Agent': user*agents.get(browser, user_agents['chrome']),
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/\_;q=0.8',
'Accept-Language': 'en-US,en;q=0.5',
'Accept-Encoding': 'gzip, deflate, br',
'DNT': '1',
'Connection': 'keep-alive',
'Upgrade-Insecure-Requests': '1'
})

def get(self, url, **kwargs):
"""Send GET Request"""
return self.session.get(url, **kwargs)

def post(self, url, **kwargs):
"""Send POST Request"""
return self.session.post(url, **kwargs)

def verify_fingerprint(self):
"""Validate TLS 指纹"""
r = self.get('https://ja3er.com/json')
return r.json()

# 使用示例

if **name** == '**main**': # 创建 Chrome 会话
browser = BrowserSession('chrome')

# 验证指纹

print(" Validate TLS 指纹...")
result = browser.verify_fingerprint()
print(f"JA3: {result['ja3']}")
print(f"User-Agent: {result['User-Agent']}")

# 发送请求

response = browser.get('https://api.example.com/data')
print(f"\nStatus 码: {response.status_code}")

```

```

````



<!-- 01-Recipes/Scripts/automation_scripts.md -->

# 自动化脚本 (Automation Scripts)

在 Android 逆向工程中，自动化脚本可以极大地提高效率，例如自动安装 APK、重启应用、模拟点击以及批量处理设备。Python 是编写这些脚本的首选语言。

## 1. 基础 ADB 封装 (Python)

虽然可以直接在 shell 中运行 `adb` 命令，但在 Python 中封装一层可以更方便地进行逻辑控制。

```python
import subprocess
import time
import os

class AdbWrapper:
def __init__(self, device_id=None):
self.device_id = device_id

def run_cmd(self, cmd):
adb_cmd = ["adb"]
if self.device_id:
adb_cmd.extend(["-s", self.device_id])
adb_cmd.extend(cmd)

try:
result = subprocess.run(
adb_cmd,
capture_output=True,
text=True,
check=True
)
return result.stdout.strip()
except subprocess.CalledProcessError as e:
print(f"Error running command {' '.join(adb_cmd)}: {e.stderr}")
return None

def install(self, apk_path):
print(f"Installing {apk_path}...")
return self.run_cmd(["install", "-r", apk_path])

def uninstall(self, package_name):
print(f"Uninstalling {package_name}...")
return self.run_cmd(["uninstall", package_name])

def start_app(self, package_name, activity_name):
print(f"Starting {package_name}/{activity_name}...")
return self.run_cmd(["shell", "am", "start", "-n", f"{package_name}/{activity_name}"])

def stop_app(self, package_name):
print(f"Stopping {package_name}...")
return self.run_cmd(["shell", "am", "force-stop", package_name])

def clear_data(self, package_name):
print(f"Clearing data for {package_name}...")
return self.run_cmd(["shell", "pm", "clear", package_name])

def click(self, x, y):
return self.run_cmd(["shell", "input", "tap", str(x), str(y)])

def swipe(self, x1, y1, x2, y2, duration=500):
return self.run_cmd(["shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration)])

def input_text(self, text):
# Note: special characters might need escaping
return self.run_cmd(["shell", "input", "text", text])

def screenshot(self, remote_path="/sdcard/screenshot.png", local_path="screenshot.png"):
self.run_cmd(["shell", "screencap", "-p", remote_path])
self.run_cmd(["pull", remote_path, local_path])
print(f"Screenshot saved to {local_path}")

# UseExample
if __name__ == "__main__":
adb = AdbWrapper() # 默认连接第一个设备

# 打印 connected设备
print("Devices:", adb.run_cmd(["devices"]))

# adb.start_app("com.example.app", "com.example.app.MainActivity")
# time.sleep(5)
# adb.click(500, 1000)
# adb.screenshot()

````

pip install uiautomator2

```

import time

# Connect to to to to to to to device (USB)
d = u2.connect()
# or通过 WiFi: d = u2.连接('192.168.1.100')

print(f"Connected to device: {d.info}")

# startupApp
pkg_name = "com.example.android.apis"
d.app_start(pkg_name)

# Wait forAppstartup
d.wait_activity(".ApiDemos", timeout=10)

# 查找并点击元素 (Support多种选择器)
try:
# 通过文本查找并点击
if d(text="App").exists:
d(text="App").click()

# 通过 resourceId 查找
# d(resourceId="com.example:id/button").click()

# 滚动查找 (向下滑动直到找到文本为 '通知' 元素)
d(scrollable=True).scroll.to(text="Notification")
d(text="Notification").click()

# 输入文本
# d(resourceId="com.example:id/edit_text").set_text("Hello World")

# 截图
d.screenshot("uiauto_screenshot.jpg")

except Exception as e:
print(f"Error: {e}")

finally:
# 停止 App
# d.app_stoperation (pkg_name)
pass

```

import glob
from concurrent.futures import ThreadPoolExecutor

class BatchManager:
def **init**(self, adb_wrapper):
self.adb = adb_wrapper

def install_all(self, directory):
apk_files = glob.glob(os.path.join(directory, "\*\*.apk"))
print(f"Found {len(apk_files)} APKs.")

# UseThread 池 ConcurrentInstall (注意：ADB Concurrent 可能不 Stable，视情况调整)

with ThreadPoolExecutor(max_workers=3) as executor:
executor.map(self.adb.install, apk_files)

def setup_proxy(self, host, port):
print(f"Setting global http proxy to {host}:{port}...")
self.adb.run_cmd(["shell", "settings", "put", "global", "http_proxy", f"{host}:{port}"])

def clear_proxy(self):
print("Clearing global http proxy...")
self.adb.run_cmd(["shell", "settings", "put", "global", "http_proxy", ":0"])

# UseExample

if **name** == "**main**":
adb = AdbWrapper()
manager = BatchManager(adb)

# 批量安装当前目录下 apks 文件夹中所有 apk

# manager.install_all("./apks")

# settingssssss 代理以便抓 Package

# manager.setup_proxy("192.168.1.10", "8080")

<!-- 01-Recipes/Scripts/c_for_emulation.md -->

# C 代码：用于运行时仿真与设备指纹生成

在逆向工程中，直接使用 C/C++ 编写一些辅助工具或重现目标逻辑是一种非常高效的策略。这可以帮助我们脱离复杂的 App 环境，对核心算法进行独立的测试、Fuzzing 或仿真。

## 1. 运行时仿真 (Runtime Emulation)

当我们在 SO 文件中定位到一个关键的核心算法（如自定义加密、签名生成）后，如果该算法逻辑清晰且依赖较少，最好的方法就是将其逻辑用 C/C++ “翻译”一遍。

- **场景示例：重现一个简单的 XOR 加密算法\*\***

假设在 IDA Pro 中看到如下伪代码：

```cpp
// Decompiled pseudo-code from IDA
void encrypt_data(char* data, int len) {
for (int i = 0; i < len; ++i) {
data[i] = (data[i] ^ 0x5A) + 5;
}
}

```

// Re-implementation of the encryption algorithm
void simulate_encrypt(char\*\* data, size_t len) {
for (size_t i = 0; i < len; ++i) {
data[i] = (data[i] ^ 0x5A) + 5;
}
}

// Corresponding decryption for our own testing
void simulate_decrypt(char\*\* data, size_t len) {
for (size_t i = 0; i < len; ++i) {
data[i] = (data[i] - 5) ^ 0x5A;
}
}

int main() {
char my_data[] = "this_is_a_test_message";
size_t len = strlen(my_data);

printf("Original: %s\n", my_data);

// Encrypt it
simulate_encrypt(my_data, len);
printf("Encrypted (as hex): ");
for(size_t i = 0; i < len; ++i) {
printf("%02x ", (unsigned char)my_data[i]);
}
printf("\n");

// Decrypt it
simulate_decrypt(my_data, len);
printf("Decrypted: %s\n", my_data);

return 0;
}

````

## 2. 设备指纹生成 (Device Fingerprint Generation)

许多 App 会通过读取 Android 系统的 `build.prop` 或其他系统属性来生成设备指纹，用于识别和跟踪设备。在进行自动化操作时，我们需要能够模拟这些指纹。

`getprop` 是 Android shell 中的一个命令，可以读取系统属性。我们也可以用 C 代码在 Native 层实现类似的功能，从而生成可以乱真的指纹数据。

* *场景示例：用 C 读取关键设备属性并生成 JSON**

```c
# include <stdio.h>
# include <stdlib.h>
# include <string.h>

// A simple wrapper to execute a shell command and get its output
// In a real scenario, you might use direct system calls for better performance/stealth
char* get_prop(const char* key) {
char command[256];
snprintf(command, sizeof(command), "getprop %s", key);

FILE* fp = popen(command, "r");
if (fp == NULL) {
return NULL;
}

char* line = malloc(256);
if (fgets(line, 256, fp) == NULL) {
free(line);
pclose(fp);
return NULL;
}

// Remove trailing newline
line[strcspn(line, "\n")] = 0;
pclose(fp);
return line;
}

int main() {
// List of properties we want to fetch
const char* props_to_fetch[] = {
"ro.product.brand",
"ro.product.model",
"ro.product.manufacturer",
"ro.build.version.release",
"ro.build.version.sdk",
"ro.build.fingerprint"
};
int num_props = sizeof(props_to_fetch) / sizeof(props_to_fetch[0]);

printf("{\n");
for (int i = 0; i < num_props; ++i) {
char* value = get_prop(props_to_fetch[i]);
if (value) {
printf(" \"%s\": \"%s\"", props_to_fetch[i], value);
if (i < num_props - 1) {
printf(",");
}
printf("\n");
free(value);
}
}
printf("}\n");

return 0;
}

````

````
    ```bash
# (NDK_PATH is the path to your android NDK)
# This command is for arm64 architecture, adjust as needed
$NDK_PATH/toolchains/llvm/prebuilt/linux-x86_64/bin/aarch64-linux-android21-clang fingerprinter.c -o fingerprinter
# Then push to device and run
# adb push fingerprinter /data/local/tmp/
# adb shell 'cd /data/local/tmp/ && ./fingerprinter'

````

````



<!-- 01-Recipes/Scripts/frida_common_scripts.md -->

# Recipe: Frida 常用脚本速查手册

## 问题场景

你在使用 Frida 进行 Android 逆向时，经常遇到以下情况：

- 💭 **"我需要绕过 SSL Pinning 抓包，但不想从零写脚本"**
- 💭 **"如何快速 Hook 所有 JNI 函数来分析 Native 层？"**
- 💭 **"想拦截并修改网络请求，有现成的模板吗？"**
- 💭 **"需要从 PC 端主动调用 App 的加密函数，怎么写 RPC？"**
- 💭 **"App 检测到 Frida 就闪退，有通用的绕过脚本吗？"**

本配方提供一套**经过实战验证**的 Frida 脚本模板库，按场景分类，可直接使用或快速修改。每个脚本都包含详细注释和使用说明。

___

## 工具清单

### 必需工具

- [x] **Frida** - 已安装并配置好 (参考 [Frida 使用指南](../../02-Tools/Dynamic/frida_guide.md))
- [x] **Root 设备/模拟器** - 运行 Frida Server
- [x] **目标应用已安装** - 需要分析的 App

### 可选工具

- ☐ **Python 3** - 用于 RPC 控制脚本
- ☐ **mitmproxy/Burp Suite** - 配合 SSL Pinning 绕过使用
- ☐ **IDA Pro/Ghidra** - 用于分析 Native 代码确定 Hook 点

___

## 前置条件

✅ **Frida 环境已配置**并能成功 attach 到目标应用
✅ **了解基本的 JavaScript 语法**
✅ **知道如何运行 Frida 脚本** (`frida -U -f com.app -l script.js`)
✅ **能识别需要 Hook 的类/函数名**（至少知道包名）

___

## 脚本索引

本手册包含以下 **8 类场景**的脚本：

| 场景 | 脚本数量 | 适用情况 |
| ---------------------------------------- | -------- | ----------------------------- |
| 🛡️ [绕过保护机制](#1-绕过保护机制) | 3 个 | 反调试、反 Frida、SSL Pinning |
| [网络拦截与修改](#2-网络拦截与修改) | 1 个 | 抓包、修改请求/响应 |
| [自动化 RPC 调用](#3-自动化-rpc-调用) | 1 套 | 主动调用加密函数、批量测试 |
| [JNI 函数分析](#4-jni-函数分析) | 5 个 | Native 层逆向、参数追踪 |
| [通用 Hook 模板](#5-通用-hook-模板) | 3 个 | 快速定位、批量 Hook |
| [C 代码辅助工具](#6-c-代码辅助工具) | 2 个 | 算法仿真、设备指纹生成 |

___

## 1. 绕过保护机制

### 脚本 1.1: 绕过 TracerPid 反调试检测

**何时使用**: App 通过读取 `/proc/self/status` 中的 `TracerPid` 来检测调试器。

**工作原理**: Hook `fgets` 函数，当检测到读取 `TracerPid` 时，将其值强制改为 0。

```javascript
// bypass_tracerpid.js - Bypass TracerPid Anti-Debugging

// Step 1: Establish FILE* to path mapping
var fpMap = {};

// Hook fopen to record file paths
Interceptor.attach(Module.findExportByName(null, "fopen"), {
onEnter: function (args) {
this.path = args[0].readCString();
},
onLeave: function (retval) {
if (!retval.isNull() && this.path) {
fpMap[retval.toString()] = this.path;
if (this.path.includes("/status")) {
console.log("[+] fopen: " + this.path);
}
}
},
});

// Hook fgets to modify TracerPid value
Interceptor.attach(Module.findExportByName(null, "fgets"), {
onEnter: function (args) {
this.buf = args[0];
this.fp = args[2];
},
onLeave: function (retval) {
if (retval.isNull()) return;

var fp = this.fp.toString();
var path = fpMap[fp];

if (path && path.endsWith("/status")) {
var line = this.buf.readCString();

if (line && line.includes("TracerPid:")) {
var oldValue = line.match(/TracerPid:\s*(\d+)/);
this.buf.writeUtf8String("TracerPid:\t0\n");

if (oldValue && oldValue[1] !== "0") {
console.log("✓ [TracerPid] Modify: " + oldValue[1] + " -> 0");
}
}
}
},
});

console.log("[+] TracerPid Anti-Debugging Bypass activated");

````

# Attach mode

frida -U com.target.app -l bypass_tracerpid.js

````

**工作原理**: Hook 字符串比较函数，当发现比较内容包含 "frida" 时，返回不匹配。

```javascript
// hide_frida_strings.js - Hide Frida signature strings

// Hook strstr (most commonly used string search function)
var strstrPtr = Module.findExportByName('libc.so', 'strstr');
if (strstrPtr) {
Interceptor.attach(strstrPtr, {
onEnter: function(args) {
this.haystack = args[0].readCString();
this.needle = args[1].readCString();
},
onLeave: function(retval) {
if (this.haystack && this.needle) {
var haystackLower = this.haystack.toLowerCase();
var needleLower = this.needle.toLowerCase();

if (haystackLower.includes('frida') || needleLower.includes('frida')) {
console.log("✓ [strstr] Intercept Frida Detection:");
console.log(" Search: \"" + this.needle + "\" in \"" + this.haystack.substring(0, 50) + "...\"");
retval.replace(ptr(0)); // Return NULL (not found)
}
}
}
});
console.log("[+] strstr hook configured");
}

// Hook strcmp
var strcmpPtr = Module.findExportByName('libc.so', 'strcmp');
if (strcmpPtr) {
Interceptor.attach(strcmpPtr, {
onEnter: function(args) {
this.str1 = args[0].readCString();
this.str2 = args[1].readCString();
},
onLeave: function(retval) {
if (this.str1 && this.str2) {
var str1Lower = this.str1.toLowerCase();
var str2Lower = this.str2.toLowerCase();

if (str1Lower.includes('frida') || str2Lower.includes('frida')) {
console.log("✓ [strcmp] Intercept Frida Detection:");
console.log(" Comparing: \"" + this.str1 + "\" vs \"" + this.str2 + "\"");
retval.replace(1); // Return non-zero (not equal)
}
}
}
});
console.log("[+] strcmp hook configured");
}

console.log("[+] Frida string hiding activated");

````

**工作原理**: Hook 常见网络库（TrustManager、OkHttp3、HttpsURLConnection）的证书校验函数。

```javascript
// bypass_ssl_pinning.js - Universal SSL Pinning Bypass Script

Java.perform(function () {
  console.log("[+] Starting SSL Pinning bypass...");

  // ========================================
  // 1. TrustManagerImpl (system level)
  // ========================================
  try {
    var TrustManagerImpl = Java.use(
      "com.android.org.conscrypt.TrustManagerImpl"
    );

    // android 7.0+
    TrustManagerImpl.verifyChain.implementation = function (
      untrustedChain,
      trustAnchorChain,
      host,
      clientAuth,
      ocspData,
      tlsSctData
    ) {
      console.log("✓ [TrustManagerImpl] Bypass cert validation: " + host);
      return untrustedChain; // Trust directly
    };

    console.log("[+] TrustManagerImpl Hook 成功");
  } catch (e) {
    console.log("[-] TrustManagerImpl not found: " + e);
  }

  // ========================================
  // 2. OkHttp3 (most commonly used)
  // ========================================
  try {
    var CertificatePinner = Java.use("okhttp3.CertificatePinner");

    CertificatePinner.check.overload(
      "java.lang.String",
      "java.util.List"
    ).implementation = function (hostname, peerCertificates) {
      console.log("✓ [OkHttp3] Bypass cert pinning: " + hostname);
      return; // Skip all checks
    };

    console.log("[+] OkHttp3 CertificatePinner Hook 成功");
  } catch (e) {
    console.log("[-] OkHttp3 not found: " + e);
  }

  // ========================================
  // 3. OkHttp3 - Hostname Verifier
  // ========================================
  try {
    var OkHostnameVerifier = Java.use(
      "okhttp3.internal.tls.OkHostnameVerifier"
    );

    OkHostnameVerifier.verify.overload(
      "java.lang.String",
      "javax.net.ssl.SSLSession"
    ).implementation = function (host, session) {
      console.log("✓ [OkHttp3] Bypass hostname validation: " + host);
      return true; // Always return validation passed
    };

    console.log("[+] OkHostnameVerifier Hook 成功");
  } catch (e) {
    console.log("[-] OkHostnameVerifier not found: " + e);
  }

  // ========================================
  // 4. HttpsURLConnection
  // ========================================
  try {
    var HttpsURLConnection = Java.use("javax.net.ssl.HttpsURLConnection");

    HttpsURLConnection.setDefaultHostnameVerifier.implementation = function (
      hostnameVerifier
    ) {
      console.log(
        "✓ [HttpsURLConnection] Intercept setDefaultHostnameVerifier"
      );
      return; // Don't set verifier
    };

    HttpsURLConnection.setSSLSocketFactory.implementation = function (
      socketFactory
    ) {
      console.log("✓ [HttpsURLConnection] Intercept setSSLSocketFactory");
      return; // Don't set factory
    };

    HttpsURLConnection.setHostnameVerifier.implementation = function (
      hostnameVerifier
    ) {
      console.log("✓ [HttpsURLConnection] Intercept setHostnameVerifier");
      return;
    };

    console.log("[+] HttpsURLConnection Hook 成功");
  } catch (e) {
    console.log("[-] HttpsURLConnection Hook Failed: " + e);
  }

  // ========================================
  // 5. SSLContext
  // ========================================
  try {
    var SSLContext = Java.use("javax.net.ssl.SSLContext");

    SSLContext.init.overload(
      "[Ljavax.net.ssl.KeyManager;",
      "[Ljavax.net.ssl.TrustManager;",
      "java.security.SecureRandom"
    ).implementation = function (km, tm, random) {
      console.log("✓ [SSLContext] Use custom TrustManager");

      // Create a TrustManager that trusts all certificates
      var TrustManager = Java.use("javax.net.ssl.X509TrustManager");
      var EmptyTrustManager = Java.registerClass({
        name: "com.frida.EmptyTrustManager",
        implements: [TrustManager],
        methods: {
          checkClientTrusted: function (chain, authType) {},
          checkServerTrusted: function (chain, authType) {},
          getAcceptedIssuers: function () {
            return [];
          },
        },
      });

      var emptyTrustManager = EmptyTrustManager.$new();
      this.init(km, [emptyTrustManager], random);
    };

    console.log("[+] SSLContext Hook 成功");
  } catch (e) {
    console.log("[-] SSLContext Hook Failed: " + e);
  }

  console.log("[+] SSL Pinning bypass configuration complete");
});
```

# 2. Run script

frida -U -f com.target.app -l bypass_ssl_pinning.js --no-pause

# 3. View traffic in Burp/mitmproxy

````

* *何时使用**: 需要在不使用代理的情况下，直接在 App 内部拦截和修改网络流量。

* *工作原理**: Hook OkHttp3 的 `RealInterceptorChain.proceed` 方法，可以访问和修改请求/响应。

```javascript
// intercept_okhttp.js - Intercept and modify OkHttp3 network requests

Java.perform(function() {
console.log("[+] Starting OkHttp3 hook...");

try {
var RealInterceptorChain = Java.use('okhttp3.internal.http.RealInterceptorChain');

RealInterceptorChain.proceed.implementation = function(request) {
// ========================================
// Request Interception
// ========================================
console.log("\n[REQUEST] ========================================");
console.log(" URL: " + request.url().toString());
console.log(" Method: " + request.method());

// Print request headers
var headers = request.headers();
var headerCount = headers.size();
if (headerCount > 0) {
console.log(" Headers:");
for (var i = 0; i < headerCount; i++) {
console.log(" " + headers.name(i) + ": " + headers.value(i));
}
}

// Print request body
var requestBody = request.body();
if (requestBody) {
try {
var Buffer = Java.use('okio.Buffer');
var buffer = Buffer.$new();
requestBody.writeTo(buffer);
var bodyString = buffer.readUtf8();
console.log(" Body: " + bodyString);
} catch (e) {
console.log(" Body: [Cannot read]");
}
}

// ========================================
// Modify Request (Optional)
// ========================================
var modifiedRequest = request.newBuilder()
.header('X-Custom-Header', 'Injected-By-Frida') // Add custom header
.header('User-Agent', 'FridaBot/1.0') // Modify User-Agent
.build();

// Execute request
var response = this.proceed(modifiedRequest);

// ========================================
// Response Interception
// ========================================
console.log("\n[RESPONSE] ========================================");
console.log(" Code: " + response.code());
console.log(" Message: " + response.message());

// Print response headers
var respHeaders = response.headers();
var respHeaderCount = respHeaders.size();
if (respHeaderCount > 0) {
console.log(" Headers:");
for (var i = 0; i < respHeaderCount; i++) {
console.log(" " + respHeaders.name(i) + ": " + respHeaders.value(i));
}
}

// ========================================
// Modify Response (Optional)
// ========================================
var responseBody = response.body();
if (responseBody) {
try {
var contentType = responseBody.contentType();
var bodyString = responseBody.string();

console.log(" Body: " + bodyString.substring(0, 500));

// Example: Modify JSON response field
if (bodyString.includes('"status"')) {
var modifiedBody = bodyString.replace(/"status":"error"/g, '"status":"success"');
console.log("✓ [Modify] Status field: error -> success");

// Rebuild response
var MediaType = Java.use('okhttp3.MediaType');
var ResponseBody = Java.use('okhttp3.ResponseBody');

var newBody = ResponseBody.create(contentType, modifiedBody);

return response.newBuilder()
.body(newBody)
.build();
}

// If not modified, need to recreate body (because it was already read)
var ResponseBody = Java.use('okhttp3.ResponseBody');
var newBody = ResponseBody.create(contentType, bodyString);

return response.newBuilder()
.body(newBody)
.build();

} catch (e) {
console.log(" Body: [Read failed] " + e);
}
}

return response;
};

console.log("[+] OkHttp3 Hook 成功");

} catch (e) {
console.log("[-] Hook Failed: " + e);
}
});

````

````

**何时使用**: 需要从 PC 端批量调用 App 的加密函数、签名算法等，进行自动化测试。

**Frida 脚本** (`rpc_agent.js`):

```javascript
// rpc_agent.js - RPC export functions for Python calls

console.log("[+] RPC Agent loaded");

// Define exported RPC functions
rpc.exports = {
// ========================================
// Example 1: Call static encryption function
// ========================================
callEncrypt: function(plaintext) {
var result = "";

Java.perform(function() {
try {
// Modify to target app's actual class name and method name
var CryptoUtil = Java.use('com.example.app.utils.CryptoUtil');

// Call static method
result = CryptoUtil.encrypt(plaintext);

console.log("[RPC] encrypt(\"" + plaintext + "\") = " + result);

} catch (e) {
result = "ERROR: " + e;
console.log("[-] " + result);
}
});

return result;
},

// ========================================
// Example 2: Call instance method
// ========================================
callInstanceMethod: function(className, methodName, args) {
var result = "";

Java.perform(function() {
try {
var TargetClass = Java.use(className);

// Enumerate all instances
Java.choose(className, {
onMatch: function(instance) {
console.log("[RPC] Found instance: " + instance);

// Call instance method
result = instance[methodName].apply(instance, args);

console.log("[RPC] " + methodName + "() = " + result);
},
onComplete: function() {}
});

} catch (e) {
result = "ERROR: " + e;
console.log("[-] " + result);
}
});

return result;
},

// ========================================
// Example 3: Call Native Function
// ========================================
callNativeFunction: function(libraryName, functionName, args) {
try {
var funcAddr = Module.findExportByName(libraryName, functionName);

if (!funcAddr) {
return "ERROR: Function not found";
}

// Define function signature (modify based on actual situation)
// Example: int encrypt(char* input, char* output, int length)
var nativeFunc = new NativeFunction(funcAddr, 'int', ['pointer', 'pointer', 'int']);

// Prepare parameters
var input = Memory.allocUtf8String(args[0]);
var output = Memory.alloc(1024);

// Call function
var ret = nativeFunc(input, output, args[0].length);

var result = output.readCString();
console.log("[RPC] Native " + functionName + "() returned: " + ret);
console.log("[RPC] Output: " + result);

return result;

} catch (e) {
return "ERROR: " + e;
}
},

// ========================================
// Example 4: Get app info
// ========================================
getAppInfo: function() {
var info = {};

Java.perform(function() {
var Context = Java.use('android.app.ActivityThread').currentApplication().getApplicationContext();
var PackageManager = Context.getPackageManager();
var PackageName = Context.getPackageName();
var PackageInfo = PackageManager.getPackageInfo(PackageName, 0);

info.packageName = PackageName;
info.versionName = PackageInfo.versionName.value;
info.versionCode = PackageInfo.versionCode.value;

console.log("[RPC] App Info: " + JSON.stringify(info));
});

return info;
}
};

console.log("[+] RPC functions exported:");
console.log(" - callEncrypt(plaintext)");
console.log(" - callInstanceMethod(className, methodName, args)");
console.log(" - callNativeFunction(libraryName, functionName, args)");
console.log(" - getAppInfo()");

````

# rpc_controller.py - Python RPC control script

import frida
import sys

def on_message(message, data):
"""Process messages from Frida script"""
if message['type'] == 'send':
print(f"[*] {message['payload']}")
elif message['type'] == 'error':
print(f"[!] Error: {message['stack']}")

def main(): # ======================================== # Connect to device and app # ========================================
try:
device = frida.get_usb_device(timeout=5)
print(f"[+] Connected to device: {device}")
except frida.TimedOutError:
print("[-] Device connection timeout")
sys.exit(1)

# Attach to running app

try:
package_name = "com.example.app" # Modify to target app package name
session = device.attach(package_name)
print(f"[+] Attached to: {package_name}")
except frida.ProcessNotFoundError:
print(f"[-] Process not found: {package_name}")
print("[*] Please ensure app is running")
sys.exit(1)

# ========================================

# Load Frida Script

# ========================================

with open("rpc_agent.js", "r", encoding="utf-8") as f:
script_code = f.read()

script = session.create_script(script_code)
script.on('message', on_message)
script.load()
print("[+] Frida script loaded\n")

# ========================================

# Get RPC API

# ========================================

api = script.exports

# ========================================

# Example 1: Call encryption function

# ========================================

print("=" _ 60)
print("Example 1: Call encryption function")
print("=" _ 60)

test_data = "Hello, Frida RPC!"
encrypted = api.call_encrypt(test_data)
print(f"Plaintext: {test_data}")
print(f"Ciphertext: {encrypted}\n")

# ========================================

# Example 2: Batch test

# ========================================

print("=" _ 60)
print("Example 2: Batch test")
print("=" _ 60)

test_cases = [
"test1",
"test2",
"test3",
"a" * 100, # Long string
"", # Empty string
]

for i, test_input in enumerate(test_cases):
result = api.call_encrypt(test_input)
print(f"[{i+1}] {test_input[:20]:<20} -> {result}")

print()

# ========================================

# Example 3: Get app info

# ========================================

print("=" _ 60)
print("Example 3: Get app info")
print("=" _ 60)

app_info = api.get_app_info()
print(f"Package name: {app_info['packageName']}")
print(f"Version: {app_info['versionName']} ({app_info['versionCode']})")

# ========================================

# Keep session alive

# ========================================

print("\n[+] RPC session established, press Ctrl+C to exit")
try:
sys.stdin.read()
except KeyboardInterrupt:
print("\n[*] Disconnecting...")

session.detach()
print("[+] Disconnected")

if **name** == "**main**":
main()

```

# 2. Run Python script
python3 rpc_controller.py

# Output example:
# [+] Connected to device: ...
# [+] Attached to: com.example.app
# [+] Frida script loaded
## Plaintext: Hello, Frida RPC!
# Ciphertext: SGVsbG8sIEZyaWRhIFJQQyE=

```

```javascript
// enumerate_jni.js - Enumerate all JNI functions in specified SO file

function enumerateJNIFunctions(libraryName) {
  var module = Process.findModuleByName(libraryName);

  if (!module) {
    console.log("[-] Module not found: " + libraryName);
    console.log("[*] Trying to wait for module loading...");

    // Monitor dlopen
    Interceptor.attach(Module.findExportByName(null, "dlopen"), {
      onEnter: function (args) {
        var path = args[0].readCString();
        if (path && path.includes(libraryName)) {
          console.log("[+] Detected target library loading: " + path);
          this.target = true;
        }
      },
      onLeave: function (retval) {
        if (this.target && !retval.isNull()) {
          setTimeout(function () {
            enumerateJNIFunctions(libraryName);
          }, 500);
        }
      },
    });

    return;
  }

  console.log("\n" + "=".repeat(70));
  console.log(" JNI Function Enumeration: " + libraryName);
  console.log(" Base address: " + module.base);
  console.log(" Size: " + (module.size / 1024).toFixed(2) + " KB");
  console.log("=".repeat(70) + "\n");

  var exports = module.enumerateExports();
  var jniFunctions = [];

  // Filter JNI functions
  exports.forEach(function (exp) {
    if (exp.name.startsWith("Java_")) {
      jniFunctions.push(exp);
    }
  });

  if (jniFunctions.length === 0) {
    console.log("[-] No JNI functions found");
    return;
  }

  // Sort by name
  jniFunctions.sort(function (a, b) {
    return a.name.localeCompare(b.name);
  });

  // Print results
  jniFunctions.forEach(function (exp, index) {
    console.log("[" + index + "] " + exp.name);
    console.log(" Address: " + exp.address);
    console.log(" Offset: +" + ptr(exp.address).sub(module.base));

    // Parse JNI function name
    // Format: Java_PackageName_ClassName_MethodName
    var parts = exp.name.split("_");
    if (parts.length >= 4) {
      var packageAndClass = parts.slice(1, -1).join(".");
      var methodName = parts[parts.length - 1];
      console.log(" Java Method: " + packageAndClass + "." + methodName + "()");
    }
    console.log();
  });

  console.log("[+] Found " + jniFunctions.length + " JNI functions\n");
}

// ========================================
// Usage example
// ========================================
var TARGET_LIBRARY = "libnative-lib.so"; // Modify to target SO file name

// Method 1: If library is already loaded
enumerateJNIFunctions(TARGET_LIBRARY);

// Method 2: Wait for library to load then enumerate
// (If not found above, will automatically enable monitoring)
```

// hook_jni_function.js - Hook single JNI function

function hookJNIFunction(libraryName, functionName) {
var funcAddr = Module.findExportByName(libraryName, functionName);

if (!funcAddr) {
console.log("[-] Function not found: " + functionName);
return;
}

console.log("[+] Hooking: " + functionName);
console.log(" Address: " + funcAddr);

Interceptor.attach(funcAddr, {
onEnter: function (args) {
console.log("\n" + "=".repeat(60));
console.log("[JNI CALL] " + functionName);
console.log("=".repeat(60));
console.log(" JNIEnv\*\*: " + args[0]);
console.log(" jobject/jclass: " + args[1]);

// Try to parse parameters (starting from args[2])
for (var i = 2; i < 8 && i < args.length; i++) {
var arg = args[i];
console.log(" arg[" + (i - 2) + "]: " + arg);

if (arg.isNull()) {
console.log(" -> null");
continue;
}

// Try to parse as jstring
try {
var env = Java.vm.getEnv();
var strPtr = env.getStringUtfChars(arg, null);
var str = strPtr.readCString();

if (str && str.length > 0 && str.length < 500) {
console.log(' -> jstring: "' + str + '"');
}

env.releaseStringUtfChars(arg, strPtr);
continue;
} catch (e) {}

// Try to parse as integer
try {
var intVal = arg.toInt32();
console.log(
" -> jint: " + intVal + " (0x" + intVal.toString(16) + ")"
);
continue;
} catch (e) {}

// Try to parse as byte array
try {
var env = Java.vm.getEnv();
var arrayLen = env.getArrayLength(arg);

if (arrayLen > 0 && arrayLen < 1024) {
console.log(" -> jbyteArray[" + arrayLen + "]");

var bytePtr = env.getByteArrayElements(arg, null);
var bytes = bytePtr.readByteArray(Math.min(arrayLen, 64));
console.log(
hexdump(bytes, {
offset: 0,
length: Math.min(arrayLen, 64),
header: false,
ansi: false,
})
);
env.releaseByteArrayElements(arg, bytePtr, 0);
}
continue;
} catch (e) {}

console.log(" -> Pointer: " + arg);
}
},

onLeave: function (retval) {
console.log("\n [Return Value]: " + retval);

if (retval.isNull()) {
console.log(" -> null");
return;
}

// Try to parse return value
try {
var env = Java.vm.getEnv();
var strPtr = env.getStringUtfChars(retval, null);
var str = strPtr.readCString();

if (str && str.length > 0 && str.length < 500) {
console.log(' -> jstring: "' + str + '"');
}

env.releaseStringUtfChars(retval, strPtr);
} catch (e) {
try {
var intVal = retval.toInt32();
console.log(" -> jint: " + intVal);
} catch (e2) {
console.log(" -> Pointer: " + retval);
}
}

console.log("=".repeat(60) + "\n");
},
});

console.log("[+] Hook configured\n");
}

// ========================================
// Usage example
// ========================================
hookJNIFunction("libnative-lib.so", "Java_com_example_app_Crypto_encrypt");

```
// hook_all_jni.js - Batch hook all JNI functions

function hookAllJNI(libraryName) {
var module = Process.findModuleByName(libraryName);

if (!module) {
console.log("[-] Module not found, waiting for load: " + libraryName);

Interceptor.attach(Module.findExportByName(null, "dlopen"), {
onEnter: function (args) {
var path = args[0].readCString();
if (path && path.includes(libraryName)) {
this.target = true;
}
},
onLeave: function (retval) {
if (this.target && !retval.isNull()) {
setTimeout(function () {
hookAllJNI(libraryName);
}, 500);
}
},
});

return;
}

console.log("[+] Starting batch JNI function hook: " + libraryName);

var exports = module.enumerateExports();
var hookedCount = 0;

exports.forEach(function (exp) {
if (!exp.name.startsWith("Java_")) {
return;
}

try {
Interceptor.attach(exp.address, {
onEnter: function (args) {
console.log("\n[JNI] " + exp.name);

// Simplified output, only print first 3 parameters
for (var i = 0; i < 5 && i < args.length; i++) {
var arg = args[i];

if (i === 0) {
console.log(" JNIEnv*: " + arg);
} else if (i === 1) {
console.log(" jobject: " + arg);
} else {
console.log(" arg[" + (i - 2) + "]: " + arg);

// Try to parse string
if (!arg.isNull()) {
try {
var env = Java.vm.getEnv();
var str = env.getStringUtfChars(arg, null).readCString();
if (str && str.length > 0 && str.length < 100) {
console.log(' -> "' + str + '"');
}
env.releaseStringUtfChars(arg, str);
} catch (e) {}
}
}
}
},

onLeave: function (retval) {
console.log(" Return: " + retval);
},
});

hookedCount++;
} catch (e) {
console.log("[-] Hook failed: " + exp.name);
}
});

console.log("[+] Successfully hooked " + hookedCount + " JNI functions");
}

// ========================================
// Usage
// ========================================
hookAllJNI("libnative-lib.so");

```

// hook_jni_onload.js - Hook JNI_OnLoad function

function hookJNIOnLoad(libraryName) {
var onLoadAddr = Module.findExportByName(libraryName, "JNI_OnLoad");

if (!onLoadAddr) {
console.log("[-] JNI_OnLoad not found: " + libraryName);
return;
}

console.log("[+] Hooking JNI_OnLoad");
console.log(" Address: " + onLoadAddr);

Interceptor.attach(onLoadAddr, {
onEnter: function (args) {
console.log("\n" + "=".repeat(60));
console.log("[JNI_OnLoad] Called");
console.log("=".repeat(60));
console.log(" JavaVM\*\*: " + args[0]);
console.log(" reserved: " + args[1]);

this.vm = args[0];
},

onLeave: function (retval) {
var jniVersion = retval.toInt32();
console.log(" Return JNI Version: " + jniVersion);

// Parse version number
var major = (jniVersion >> 16) & 0xffff;
var minor = jniVersion & 0xffff;
console.log(" -> JNI*VERSION*" + major + "\_" + minor);

console.log("=".repeat(60));

// After JNI_OnLoad completes, can start hooking other JNI functions
setTimeout(function () {
console.log(
"\n[+] JNI_OnLoad completed, starting to hook JNI functions...\n"
);
// Can call other hook functions here
}, 100);
},
});
}

// Monitor library loading
Interceptor.attach(Module.findExportByName(null, "dlopen"), {
onEnter: function (args) {
var path = args[0].readCString();
console.log("[dlopen] " + path);

if (path && path.includes("libnative-lib.so")) {
console.log("[+] Detected target library loading");
this.target = true;
}
},

onLeave: function (retval) {
if (this.target && !retval.isNull()) {
setTimeout(function () {
hookJNIOnLoad("libnative-lib.so");
}, 100);
}
},
});

console.log("[+] Monitoring library loading...");

````

```javascript
// hook_java_method.js - Universal Java method hook template

function hookJavaMethod(className, methodName) {
Java.perform(function () {
try {
var targetClass = Java.use(className);

// Get all overloads
var overloads = targetClass[methodName].overloads;

console.log(
"[+] Found " +
overloads.length +
" overloads: " +
className +
"." +
methodName
);

// Hook all overloads
overloads.forEach(function (overload) {
overload.implementation = function () {
console.log("\n[CALL] " + className + "." + methodName);

// Print parameters
for (var i = 0; i < arguments.length; i++) {
console.log(" arg[" + i + "]: " + arguments[i]);
}

// Call original method
var result = this[methodName].apply(this, arguments);

console.log(" Return: " + result);

return result;
};
});

console.log("[+] Hook complete");
} catch (e) {
console.log("[-] Hook failed: " + e);
}
});
}

// Usage example
hookJavaMethod("android.util.Log", "d");
hookJavaMethod("com.example.app.Crypto", "encrypt");

````

// hook_all_methods.js - Hook all methods of a class

function hookAllMethods(className) {
Java.perform(function () {
try {
var targetClass = Java.use(className);
var methods = targetClass.class.getDeclaredMethods();

console.log("[+] Class: " + className);
console.log("[+] Found " + methods.length + " methods\n");

var hookedCount = 0;

methods.forEach(function (method) {
try {
var methodName = method.getName();

// Skip certain methods
if (methodName === "toString" || methodName === "hashCode") {
return;
}

var overloads = targetClass[methodName].overloads;

overloads.forEach(function (overload) {
overload.implementation = function () {
console.log("\n[" + className + "] " + methodName + "()");

if (arguments.length > 0) {
console.log(" Parameters:");
for (var i = 0; i < arguments.length; i++) {
console.log(" [" + i + "] " + arguments[i]);
}
}

var result = this[methodName].apply(this, arguments);

console.log(" Return: " + result);

return result;
};
});

hookedCount++;
} catch (e) {
// Some methods may not be hookable
}
});

console.log("[+] Successfully hooked " + hookedCount + " methods");
} catch (e) {
console.log("[-] Failed: " + e);
}
});
}

// Usage
hookAllMethods("com.example.app.utils.CryptoUtil");

```
// hook_constructor.js - Hook class constructor

function hookConstructor(className) {
Java.perform(function () {
try {
var targetClass = Java.use(className);

// $init is the special name for constructors
var overloads = targetClass.$init.overloads;

console.log(
"[+] Found " + overloads.length + " constructors: " + className
);

overloads.forEach(function (overload) {
overload.implementation = function () {
console.log("\n[NEW] " + className + "()");

if (arguments.length > 0) {
console.log(" Constructor parameters:");
for (var i = 0; i < arguments.length; i++) {
console.log(" [" + i + "] " + arguments[i]);
}
}

// Call original constructor
var result = this.$init.apply(this, arguments);

console.log(" Instance: " + this);

return result;
};
});

console.log("[+] Constructor hook complete");
} catch (e) {
console.log("[-] Failed: " + e);
}
});
}

// Usage
hookConstructor("javax.crypto.spec.SecretKeySpec");

```

**示例：XOR 加密算法仿真**

```c
// emulate_xor_encrypt.c - Emulate XOR encryption algorithm

# include <stdio.h>
# include <string.h>
# include <stdint.h>

// Algorithm extracted from IDA pseudocode
void encrypt_data(uint8_t* data, size_t len, uint8_t key) {
for (size_t i = 0; i < len; i++) {
data[i] = (data[i] ^ key) + 5;
}
}

// Corresponding decryption algorithm
void decrypt_data(uint8_t* data, size_t len, uint8_t key) {
for (size_t i = 0; i < len; i++) {
data[i] = (data[i] - 5) ^ key;
}
}

// Helper function: Print hexadecimal
void print_hex(const char* label, uint8_t* data, size_t len) {
printf("%s: ", label);
for (size_t i = 0; i < len; i++) {
printf("%02x ", data[i]);
}
printf("\n");
}

int main() {
// Test data
uint8_t plaintext[] = "Hello, Android Reverse Engineering!";
size_t len = strlen((char*)plaintext);
uint8_t key = 0x5A;

printf("=== XOR Encryption Algorithm Test ===\n\n");

// Plaintext
printf("Plaintext: %s\n", plaintext);
print_hex("Plaintext HEX", plaintext, len);
printf("\n");

// Encrypt
encrypt_data(plaintext, len, key);
printf("After encryption:\n");
print_hex("Ciphertext HEX", plaintext, len);
printf("\n");

// Decrypt
decrypt_data(plaintext, len, key);
printf("After decryption: %s\n", plaintext);
print_hex("Decrypted HEX", plaintext, len);

return 0;
}

```

# Run the program

./emulate

# Output:

# === XOR Encryption Algorithm Test ===

## Plaintext: Hello, Android Reverse Engineering!

# Plaintext HEX: 48 65 6c 6c 6f 2c 20 41 6e 64 72 6f 69 64 ...

## After encryption:

# Ciphertext HEX: 17 30 39 39 32 79 75 16 39 31 2d 32 36 31 ...

## After decryption: Hello, Android Reverse Engineering!

````

```c
// device_fingerprint.c - 设备指纹GenerateTool

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

// Execute shell command and get output
char* execute_command(const char* cmd) {
FILE* fp = popen(cmd, "r");
if (!fp) return NULL;

char* result = malloc(256);
if (fgets(result, 256, fp) == NULL) {
free(result);
pclose(fp);
return NULL;
}

// Remove newline character
result[strcspn(result, "\n")] = 0;
pclose(fp);

return result;
}

// Get system property
char* get_prop(const char* key) {
char command[256];
snprintf(command, sizeof(command), "getprop %s", key);
return execute_command(command);
}

int main() {
printf("{\n");
printf(" \"timestamp\": %ld,\n", time(NULL));
printf(" \"device\": {\n");

// Device info
const char* props[] = {
"ro.product.brand",
"ro.product.model",
"ro.product.manufacturer",
"ro.product.device",
"ro.build.version.release",
"ro.build.version.sdk",
"ro.build.fingerprint",
"ro.serialno",
"ro.boot.serialno"
};

int num_props = sizeof(props) / sizeof(props[0]);

for (int i = 0; i < num_props; i++) {
char* value = get_prop(props[i]);

if (value) {
// Extract last part of property name
const char* last_dot = strrchr(props[i], '.');
const char* key = last_dot ? last_dot + 1 : props[i];

printf(" \"%s\": \"%s\"", key, value);

if (i < num_props - 1) {
printf(",");
}
printf("\n");

free(value);
}
}

printf(" }\n");
printf("}\n");

return 0;
}

````

adb push device_fingerprint.c /data/local/tmp/
adb shell
cd /data/local/tmp
gcc device_fingerprint.c -o fingerprint
chmod +x fingerprint

# Run the program

./fingerprint

# Output JSON format device fingerprint:

# {

# "timestamp": 1734518400,

# "device": {

# "brand": "google",

# "model": "Pixel 5",

# "manufacturer": "Google",

# ...

# }

# }

# Save to file

./fingerprint > /sdcard/device_info.json

````

**可能原因**:
1. Hook 时机太晚，目标函数已经执行完毕
2. 类名或方法名拼写错误
3. 使用了 Attach 模式，但 DEX 还未加载

**解决方案**:

```bash
# 1. Use Spawn mode (Recommended)
frida -U -f com.target.app -l script.js --no-pause

# 2. Check if class name is correct
Java.perform(function() {
Java.enumerateLoadedClasses({
onMatch: function(className) {
if (className.indexOf("Crypto") !== -1) {
console.log("[+] Found class: " + className);
}
},
onComplete: function() {}
});
});

# 3. Delayed hook (if using Attach mode)
setTimeout(function() {
hookJavaMethod("com.example.app.Crypto", "encrypt");
}, 2000);

````

**可能原因**:

1. 读取了无效的指针
2. JNIEnv 使用不当
3. 字节数组释放问题

**解决方案**:

```javascript
// Add try-catch protection
Interceptor.attach(funcAddr, {
  onEnter: function (args) {
    try {
      // Check pointer validity first
      if (!args[2].isNull()) {
        var env = Java.vm.getEnv();
        // ... Process parameters
      }
    } catch (e) {
      console.log("[-] Caught exception: " + e);
      // Don't re-throw to avoid crash
    }
  },
});
```

1. 类还未加载到内存
2. 类名错误或被混淆
3. 使用了动态加载的 DEX

**解决方案**:

```python
# On Python side, wait for class to load first
api.wait_for_class("com.example.app.Crypto") # Custom wait function

# Or check in Frida script
rpc.exports = {
callEncrypt: function(input) {
var result = "";

Java.perform(function() {
// Check if class exists first
try {
var Crypto = Java.use("com.example.app.Crypto");
result = Crypto.encrypt(input);
} catch (e) {
// Try to enumerate and find
Java.enumerateLoadedClasses({
onMatch: function(className) {
if (className.includes("Crypto")) {
console.log("[+] Found: " + className);
}
},
onComplete: function() {}
});

result = "ERROR: " + e;
}
});

return result;
}
};

```

1. 应用使用了自定义的 SSL Pinning 实现
2. Native 层实现的 Pinning
3. 使用了第三方网络库 (如 Cronet)

**解决方案**:

```javascript
// 1. Add more hook points
Java.perform(function () {
  // Hook custom TrustManager
  Java.enumerateLoadedClasses({
    onMatch: function (className) {
      if (
        className.includes("TrustManager") ||
        className.includes("Certificate")
      ) {
        console.log("[+] Found suspicious class: " + className);

        try {
          var clazz = Java.use(className);
          var methods = clazz.class.getDeclaredMethods();

          methods.forEach(function (method) {
            var methodName = method.getName();
            if (methodName.includes("check") || methodName.includes("verify")) {
              console.log("[+] Hook: " + className + "." + methodName);
              // Batch hook
            }
          });
        } catch (e) {}
      }
    },
    onComplete: function () {},
  });
});

// 2. Hook native layer SSL_CTX_set_verify
var SSL_CTX_set_verify = Module.findExportByName(
  "libssl.so",
  "SSL_CTX_set_verify"
);
if (SSL_CTX_set_verify) {
  Interceptor.attach(SSL_CTX_set_verify, {
    onEnter: function (args) {
      console.log("✓ [SSL_CTX_set_verify] Bypass");
      args[1] = ptr(0); // SSL_VERIFY_NONE
    },
  });
}
```

- [Recipe: 抓包分析 Android 应用的网络流量](../Network/network_sniffing.md) - 配合 SSL Pinning 绕过使用
- [Recipe: 分析并提取 Android 应用的加密密钥](../Network/crypto_analysis.md) - 密码学分析的完整流程

### 工具深入

- [Frida 使用指南](../../02-Tools/Dynamic/frida_guide.md) - 完整的 Frida 使用手册
- [Frida 内部原理](../../02-Tools/Dynamic/frida_internals.md) - 深入理解 Frida 工作机制

### 案例分析

- [案例: 音乐 App 分析](../../03-Case-Studies/case_music_apps.md) - 综合运用多个脚本

### 参考资料

- [JNI 函数速查](../../04-Reference/Foundations/jni_reference.md)
- [常见加密算法识别](../../04-Reference/Foundations/crypto_algorithms.md)

---

## 快速参考

### 脚本速查表

| 需求                    | 使用脚本                           | 难度 |
| ----------------------- | ---------------------------------- | ---- |
| **绕过 TracerPid 检测** | `bypass_tracerpid.js`              |      |
| **隐藏 Frida 字符串**   | `hide_frida_strings.js`            |      |
| **绕过 SSL Pinning**    | `bypass_ssl_pinning.js`            |      |
| **拦截网络请求**        | `intercept_okhttp.js`              |      |
| **RPC 调用加密函数**    | `rpc_agent.js + rpc_controller.py` |      |
| **枚举 JNI 函数**       | `enumerate_jni.js`                 |      |
| **Hook JNI 函数**       | `hook_jni_function.js`             |      |
| **批量 Hook JNI**       | `hook_all_jni.js`                  |      |
| **Hook 构造函数**       | `hook_constructor.js`              |      |

### 常用命令

````bash
# 1. Spawn mode run script (recommended)
frida -U -f com.target.app -l script.js --no-pause

# 2. Attach mode
frida -U com.target.app -l script.js

# 3. List all processes
frida-ps -Ua

# 4. Interactive REPL
frida -U com.target.app

# 5. Load multiple scripts
frida -U -f com.target.app -l script1.js -l script2.js --no-pause

# 6. Export output to file
frida -U com.target.app -l script.js > output.log 2>&1

3. **适度打印日志** - 过多日志会影响性能
4. **模块化组织** - 将常用函数封装为独立模块
5. **保存脚本库** - 建立自己的脚本模板库

- --

* *💡 提示**: 这些脚本都是**模板**，实际使用时需要根据目标 App 的具体情况进行调整。建议先理解脚本原理，再修改关键参数 (如类名、方法名、SO 文件名等)。
    ```

````

<!-- 01-Recipes/Scripts/frida_script_examples.md -->

# Frida 实战脚本集

本文档收集了适用于各种常见场景的 Frida 脚本。这些脚本旨在作为即用型模板，您可以根据特定目标进行修改。

---

## 目录

1. [信息收集 (Information Gathering)](#信息收集)
2. [Hook 与修改 (Hooking & Modification)](#hook-与修改)
3. [网络监控与绕过 (Networking)](#网络监控与绕过)
4. [数据持久化与脱壳 (Storage & Dumping)](#数据持久化与脱壳)
5. [反调试与环境检测绕过 (Anti-Analysis)](#反调试与环境检测绕过)
6. [UI 与事件 (UI & Events)](#ui-与事件)

---

### 信息收集

#### 1. 枚举指定类的所有方法

```javascript
// Usage: frida -U -f com.example.app -l list_methods.js
// Replace 'com.example.target class' below
Java.perform(function () {
  var targetClass = "com.example.TargetClass";
  var wrapper = Java.use(targetClass);
  var ownMethods = wrapper.class.getDeclaredMethods();

  console.log("Methods of class " + targetClass + ":");
  ownMethods.forEach(function (method) {
    console.log(method.toString());
  });
});
```

console.log("Listing all loaded classes...");
Java.enumerateLoadedClasses({
onMatch: function(className) {
console.log(className);
},
onComplete: function() {
console.log("Class enumeration complete.");
}
});
});

```
Java.perform(function() {
var TargetClass = Java.use('com.example.app.CryptoUtils');
var methodName = 'encrypt'; // Method name to trace

// Handle method overloads
TargetClass[methodName].overloads.forEach(function(overload) {
overload.implementation = function() {
console.log('\n[+] Called ' + TargetClass.$className + '.' + methodName);

// Print arguments
for (var i = 0; i < arguments.length; i++) {
console.log(' - Argument ' + i + ': ' + arguments[i]);
}

// Call original method
var retval = this[methodName].apply(this, arguments);

// Print return value
console.log(' - Return value: ' + retval);

return retval;
};
});
});

```

Java.perform(function() {
var PremiumUtils = Java.use('com.example.app.PremiumUtils');

PremiumUtils.isUserPremium.implementation = function() {
console.log('[+] Bypassing Premium check...');
return true; // Return true directly
};
});

```

Java.choose('com.example.app.UserInfo', {
onMatch: function(instance) {
console.log('[+] Found UserInfo instance.');
// Directly modify field value
instance.userLevel.value = 99;
console.log(' - Patched userLevel to 99.');
},
onComplete: function() {}
});
});

```

```javascript
// Usage: frida -U --no-pause -f com.example.app -l universal_ssl_unpinning.js
// Source: https://codeshare.frida.re/@pcipolloni/universal-android-ssl-pinning-bypass-with-frida/
setTimeout(function () {
  Java.perform(function () {
    console.log("");
    console.log("[.] Android SSL Pinning Bypass");

    var CertificateFactory = Java.use("java.security.cert.CertificateFactory");
    var FileInputStream = Java.use("java.io.FileInputStream");
    var BufferedInputStream = Java.use("java.io.BufferedInputStream");
    var X509Certificate = Java.use("java.security.cert.X509Certificate");
    var KeyStore = Java.use("java.security.KeyStore");
    var TrustManagerFactory = Java.use("javax.net.ssl.TrustManagerFactory");
    var SSLContext = Java.use("javax.net.ssl.SSLContext");

    // TrustManagerImpl (android > 7)
    try {
      var TrustManagerImpl = Java.use(
        "com.android.org.conscrypt.TrustManagerImpl"
      );
      TrustManagerImpl.verifyChain.implementation = function (
        untrustedChain,
        trustAnchorChain,
        host,
        clientAuth,
        ocspData,
        tlsSctData
      ) {
        console.log(
          "[+] Bypassing TrustManagerImpl verifyChain() for host: " + host
        );
        return untrustedChain;
      };
    } catch (e) {
      console.log("[-] TrustManagerImpl not found. Skipping.");
    }

    // OkHttp3
    try {
      var OkHttpClient = Java.use("okhttp3.OkHttpClient");
      OkHttpClient.Builder.prototype.build.implementation = function () {
        var builder = this.build.call(this);
        console.log("[+] OkHttp3 CertificatePinner removed.");
        builder.certificatePinner.value = null;
        return builder;
      };
    } catch (e) {
      console.log("[-] OkHttp3 not found. Skipping.");
    }

    // TrustManager (universal)
    var TrustManager = Java.use("javax.net.ssl.X509TrustManager");
    var checkServerTrusted = TrustManager.checkServerTrusted;
    checkServerTrusted.overload(
      "java.security.cert.X509Certificate[]",
      "java.lang.String"
    ).implementation = function (chain, authType) {
      console.log(
        "[+] Bypassing TrustManager checkServerTrusted for authType: " +
          authType
      );
      return;
    };
  });
}, 0);
```

Java.perform(function() {
var sharedPrefsEditor = Java.use('android.app.SharedPreferencesImpl$EditorImpl');

sharedPrefsEditor.putString.implementation = function(key, value) {
console.log('[SP Write] key: ' + key + ', value: ' + value);
return this.putString(key, value);
};

var sharedPrefs = Java.use('android.app.SharedPreferencesImpl');
sharedPrefs.getString.implementation = function(key, defValue) {
var value = this.getString(key, defValue);
console.log('[SP Read] key: ' + key + ', value: ' + value);
return value;
};
});

```

SQLiteDatabase.query.overload('java.lang.String', '[Ljava.lang.String;', 'java.lang.String', '[Ljava.lang.String;', 'java.lang.String', 'java.lang.String', 'java.lang.String').implementation = function(table, columns, selection, selectionArgs, groupBy, having, orderBy) {
console.log("\n[SQL Query] Table: " + table);
console.log(" - Columns: " + columns);
console.log(" - Selection: " + selection);
console.log(" - Selection Args: " + selectionArgs);
return this.query(table, columns, selection, selectionArgs, groupBy, having, orderBy);
};

SQLiteDatabase.execSQL.overload('java.lang.String', '[Ljava.lang.Object;').implementation = function(sql, bindArgs) {
console.log("\n[SQL execSQL] SQL: " + sql);
console.log(" - Bind Args: " + bindArgs);
return this.execSQL(sql, bindArgs);
};
});

```

Java.perform(function () {
var RootCheckClass = Java.use('com.example.security.RootUtil'); // Replace with target class

RootCheckClass.isDeviceRooted.implementation = function() {
console.log('[+] Bypassing root check...');
return false;
};
});

```
Debug.isDebuggerConnected.implementation = function() {
console.log('[+] Bypassing isDebuggerConnected check...');
return false;
}
});

```

Java.perform(function() {
var View = Java.use('android.view.View');

View.setOnClickListener.implementation = function(listener) {
var originalListener = listener;
var view = this;

// Create a new listener to wrap the original listener
var newListener = Java.implement(Java.use('android.view.View$OnClickListener'), {
onClick: function(v) {
console.log('[+] View clicked! Class: ' + view.getClass().getName() + ', ID: ' + view.getId());
if (originalListener) {
originalListener.onClick(v); // Call the original click event
}
}
});

// Set the new listener
this.setOnClickListener(newListener);
};
});

<!-- 01-Recipes/Scripts/native_hooking.md -->

# Native 层 Hook 技巧 (Native Hooking Patterns)

在 Android 逆向中，Native 层 (C/C++) 的分析往往比 Java 层更具挑战性。Hook 标准 C 库 (libc) 函数是理解 Native 层行为、脱壳和还原算法的重要手段。

## 1. 文件操作监控 (File I/O)

监控文件操作可以帮助我们发现 App 读取了哪些配置文件、加载了哪些 Dex/So 文件，或者将解密后的数据写入到了哪里。

## # Hook `open` / `openat`

```javascript
// Hook open and openat to trace file access
function hookFileOpen() {
  // Intercept 'open'
  var openPtr = Module.findExportByName("libc.so", "open");
  if (openPtr) {
    Interceptor.attach(openPtr, {
      onEnter: function (args) {
        this.path = args[0].readCString();
        this.flags = args[1].toInt32();
        // console.log("[open] " + this.path);
      },
      onLeave: function (retval) {
        if (
          this.path &&
          (this.path.endsWith(".dex") || this.path.endsWith(".so"))
        ) {
          console.log("[open] FD: " + retval + " Path: " + this.path);
        }
      },
    });
  }

  // Intercept 'openat' (commonly used on newer android versions)
  var openatPtr = Module.findExportByName("libc.so", "openat");
  if (openatPtr) {
    Interceptor.attach(openatPtr, {
      onEnter: function (args) {
        // args[0] is dirfd, args[1] is path
        this.path = args[1].readCString();
        this.flags = args[2].toInt32();
      },
      onLeave: function (retval) {
        if (
          this.path &&
          (this.path.indexOf("base.apk") >= 0 || this.path.indexOf(".dex") >= 0)
        ) {
          console.log("[openat] FD: " + retval + " Path: " + this.path);
        }
      },
    });
  }
}
```

function hookDlopen() {
var dlopen = Module.findExportByName(null, "dlopen");
var android_dlopen_ext = Module.findExportByName(null, "android_dlopen_ext");

if (dlopen) {
Interceptor.attach(dlopen, {
onEnter: function(args) {
this.path = args[0].readCString();
},
onLeave: function(retval) {
if (this.path) {
console.log("[dlopen] " + this.path + " -> Handle: " + retval);
if (this.path.indexOf("libnative-lib.so") >= 0) {
// Library loaded, ready to hook functions inside it
}
}
}
});
}

if (android_dlopen_ext) {
Interceptor.attach(android_dlopen_ext, {
onEnter: function(args) {
this.path = args[0].readCString();
},
onLeave: function(retval) {
if (this.path) {
console.log("[android_dlopen_ext] " + this.path + " -> Handle: " + retval);
}
}
});
}
}

````

```javascript
function hookMemcpy() {
var memcpy = Module.findExportByName("libc.so", "memcpy");

Interceptor.attach(memcpy, {
onEnter: function(args) {
this.dest = args[0];
this.src = args[1];
this.n = args[2].toInt32();
},
onLeave: function(retval) {
// Filter by size or content to reduce noise
if (this.n > 100 && this.n < 200) {
// Check if source contains specific magic bytes (e.g., ELF header)
try {
var magic = this.src.readU32();
if (magic == 0x464c457f) { // .ELF
console.log("[memcpy] ELF header detected! Size: " + this.n);
console.log(hexdump(this.src, {length: 32}));
}
} catch(e) {}
}
}
});
}

````

function hookDlsym() {
var dlsym = Module.findExportByName(null, "dlsym");

Interceptor.attach(dlsym, {
onEnter: function(args) {
this.handle = args[0];
this.symbol = args[1].readCString();
},
onLeave: function(retval) {
if (this.symbol) {
console.log("[dlsym] Symbol: " + this.symbol + " -> Address: " + retval);
}
}
});
}

```
function hookStrcmp() {
var strcmp = Module.findExportByName("libc.so", "strcmp");

Interceptor.attach(strcmp, {
onEnter: function(args) {
var s1 = args[0].readCString();
var s2 = args[1].readCString();

// Filter for interesting strings
if ((s1 && s1.indexOf("secret") >= 0) || (s2 && s2.indexOf("secret") >= 0)) {
console.log("[strcmp] " + s1 + " VS " + s2);
}
}
});
}

```

````



<!-- 01-Recipes/Scripts/objection_snippets.md -->

# Objection 常用技巧 (Objection Snippets)

Objection 是一个基于 Frida 开发的运行时移动端探索工具包。它提供了类似于 shell 的交互式命令行，无需编写 JavaScript 代码即可完成大部分常见的逆向任务。

* *安装**: `pip install objection`
* *启动**: `objection -g com.example.app explore`

## 1. 内存漫游与类查找

在不知道从何入手时，首先浏览应用中加载了哪些类。

* **搜索类**:
    ```bash
# SearchContains "Crypto" Class
android hooking search classes Crypto

````

    ```bash

# SearchContains "encrypt" Method

android hooking search methods encrypt

````
    ```bash
# 列表 com.示例.app.MainActivity 所有Method
android hooking list class_methods com.example.app.MainActivity

````

Objection 的核心功能之一是快速 Hook 类或方法，打印调用的参数、返回值和调用栈。

- **Hook 整个类的所有方法**:
  ```bash
  android hooking watch class com.example.app.CryptoUtil
  ```

````
    ```bash
# 拦截 加密 方法，并PrintParameterandReturnValue (--导出-args --导出-返回)
android hooking watch class_method com.example.app.CryptoUtil.encrypt --dump-args --dump-return

````

    ```bash

# 强制 isRooted MethodReturn 假

android hooking set return_value com.example.app.Security.isRooted false

````

可以搜索内存中存在的对象实例，甚至调用这些实例的方法。

* **搜索堆中的实例**:
    ```bash
# 查找内存中现存的 User 实例
android heap search instances com.example.app.User

````

    ```bash

# 假设上一步搜索到实例 hashcode 为 123456

# 调用该实例的 getToken 方法

android heap execute 123456 getToken

````
    ```bash
# 查看该实例的 username 字段值
android heap evaluate 123456
# (进入编辑器AfterInput) console.日志(clazz.username.值)

````

- **查看当前 Activity**:
  ```bash
  android hooking get current_activity
  ```

````
    ```bash
android hooking list fragments

````

    ```bash

android intent launch_activity com.example.app.SecretActivity

````

* **列出加载的 SO 库**:
    ```bash
memory list modules

````

    ```bash

# Will libnative-lib.so Export 到 NativeFile (Used for 修复脱壳 After SO)

memory dump from_base 0x7b12345000 0x50000 output.so

# orAutoDownload

memory dump all libnative-lib.so

````
    ```bash
ls
cd cache
cat log.txt
file download /data/data/com.example.app/shared_prefs/config.xml

````

- **禁用 SSL Pinning**:
  ```bash
  android sslpinning disable
  ```

````
    ```bash
android root disable

````

    ```bash

import /path/to/my_script.js

````



<!-- 01-Recipes/Unpacking/frida_unpacking_and_so_fixing.md -->

# Recipe: 使用 Frida 脱壳加固 App 并修复 SO 文件

## 问题场景

**你遇到了什么问题？**

- 用 jadx 打开 APK，发现代码被混淆或看不到关键逻辑
- 🛡️ APK 使用了加固（加壳）保护，无法静态分析
- 📦 SO 文件被加密，IDA Pro 无法正确加载
- 你想获取 App 运行时真正的 DEX 文件
- 🧩 需要分析 Native 层代码，但 SO 文件已被加壳

**本配方教你**：使用 Frida 动态脱壳加固 App、Dump 内存中的 DEX 和 SO 文件、修复文件格式以供分析。

**核心理念**：

> 💡 **动态脱壳：在运行时获取已解密的代码**
>
> - 加壳只是静态保护，运行时必然会解密
> - Frida 可以在 DEX/SO 加载时 dump 内存
> - 修复文件格式后即可用传统工具分析
> - 绕过所有加固方案的通用方法

**预计用时**: 30-60 分钟

___

## 工具清单

### 必需工具

- ☐ **Frida** - 动态插桩框架
- ☐ **Android 设备**（已 Root）或模拟器
- ☐ **Python 3.7+** - 运行 Frida 脚本
- ☐ **jadx-gui** - 分析脱壳后的 DEX

### 可选工具

- ☐ **IDA Pro / Ghidra** - 分析 SO 文件
- ☐ **frida-dexdump** - 自动化 DEX 脱壳
- ☐ **FRIDA-DEXDump** - 另一个流行的脱壳工具
- ☐ **SoFixer** - 修复 dump 的 SO 文件

___

## 前置条件

### ✅ 确认清单

```bash
# 1. Frida 正常运行
frida-ps -U

# 2. Python 环境
python3 --version

# 3. jadx-gui 已安装
jadx-gui --version

# 4. 检查设备 root 状态
adb shell su -c 'id'
# 应该显示 uid=0(root)

````

### 识别 App 是否加固

**方法 1：jadx 查看**

打开 APK，如果看到：

- 只有几个类和方法
- 有 `StubApp`、`ProxyApplication` 等字样
- MainActivity 逻辑异常简单

* **方法 2：查看 SO 文件**

```bash
# 解压 APK
unzip app.apk -d app_unzipped

# 查看 lib 目录
ls app_unzipped/lib/arm64-v8a/

# 常见加固壳 SO 文件名
# libjiagu.so (360加固)
# libDexHelper.so (梆梆加固)
# libtup.so (腾讯加固)
# libexec.so (爱加密)

```

### 第 1 步：使用 frida-dexdump 脱壳（10 分钟）

#### 1.1 安装 frida-dexdump

```bash
# 克隆项目
git clone https://github.com/hluwa/frida-dexdump.git
cd frida-dexdump

# 安装依赖
pip3 install frida frida-tools

```

# -f: 启动应用

# --no-pause: 不暂停，立即运行

python3 main.py -U -f com.example.app

# 脚本会自动：

# 1. 启动应用

# 2. Hook DEX 加载函数

# 3. 导出所有已加载的 DEX 文件

# 4. 保存到当前目录

```
[DEXDump] Dumping DEX file: 0x7abc000000, size: 4562314
[DEXDump] Saved: com.example.app_classes.dex
[DEXDump] Found DEX: /data/app/.../base.apk!classes2.dex
[DEXDump] Dumping DEX file: 0x7abc500000, size: 2314567
[DEXDump] Saved: com.example.app_classes2.dex
[DEXDump] Total: 2 DEX files dumped

```

# 然后在应用内触发需要分析的功能

```

# 用 jadx 打开
jadx-gui com.example.app_classes.dex

```

### 第 2 步：使用 FRIDA-DEXDump（备选方案）（10 分钟）

如果 frida-dexdump 不工作，可以尝试 FRIDA-DEXDump：

```bash
# 安装
git clone https://github.com/lasting-yang/frida_dump.git
cd frida_dump

# 运行命令
python3 dump_dex.py -U -f com.example.app

```

---

### 第 3 步：手动脚本脱壳（高级）（15 分钟）

如果自动化工具失败，可以编写自定义 Frida 脚本。

#### 3.1 Hook OpenCommon（适用于 android 8.0+）

**dex_dump.js**：

```javascript
function dumpDex() {
  Java.perform(function () {
    console.log("[*] DEX Dumper started");

    // 查找 libart.so
    var libart = Process.findModuleByName("libart.so");
    if (!libart) {
      console.log("[-] libart.so not found");
      return;
    }

    // Hook OpenCommon (android 8.0+)
    // 符号名称因版本而异，需要用 nm 或 readelf 确认
    var OpenCommon = null;

    // 尝试常见符号
    var symbols = [
      "_ZN3art7DexFile10OpenCommonEPKhjS2_jRKNS_10OatDexFileEbbPS1_",
      "_ZN3art7DexFile10OpenCommonEPKhmS2_jRKNS_10OatDexFileEbbPS1_NS_6Handle",
    ];

    for (var i = 0; i < symbols.length; i++) {
      OpenCommon = Module.findExportByName("libart.so", symbols[i]);
      if (OpenCommon) {
        console.log("[+] Found OpenCommon:", OpenCommon);
        break;
      }
    }

    if (!OpenCommon) {
      console.log("[-] OpenCommon not found");
      return;
    }

    // Hook
    Interceptor.attach(OpenCommon, {
      onEnter: function (args) {
        // args[0] = base (DEX 内存地址)
        // args[1] = size (DEX 文件大小)

        var base = args[0];
        var size = args[1].toInt32();

        console.log("[*] 检测到 DEX!");
        console.log(" 基址: " + base);
        console.log(" 大小: " + size);

        // 读取 DEX 文件头，验证魔数
        var magic = base.readCString(4);
        if (magic === "dex\n") {
          console.log(" Magic: " + magic + " ✓");

          // Dump DEX
          var dexBytes = base.readByteArray(size);
          var fileName = "/sdcard/" + size + ".dex";

          var file = new File(fileName, "wb");
          file.write(dexBytes);
          file.close();

          console.log("[+] DEX dumped to: " + fileName);
        } else {
          console.log(" Invalid magic: " + magic);
        }
      },
    });

    console.log("[*] Hooks installed, waiting for DEX load...");
  });
}

setImmediate(dumpDex);
```

# 拉取到本地

adb pull /sdcard/\*\*.dex .

```
Module.enumerateExports("libart.so").forEach(function(exp) {
if (exp.name.includes("DexFile") && exp.name.includes("Open")) {
console.log(exp.name, exp.address);
}
});

```

# 查看进程加载的 SO 文件

frida -U -f com.example.app

> Process.enumerateModules().forEach(function(m) {
> if (m.name.includes("native") || m.name.includes("encrypt")) {
> console.log(m.name, m.base, m.size);
> }
> });

# 输出示例:

# libnative-lib.so 0x7abc000000 0x50000

```
var module = Process.findModuleByName(moduleName);
if (!module) {
console.log("[-] Module not found: " + moduleName);
return;
}

console.log("[+] 找到模块:", moduleName);
console.log(" 基址: " + module.base);
console.log(" 大小: " + module.size);

// 导出整个模块
var buffer = module.base.readByteArray(module.size);
var fileName = "/sdcard/" + moduleName;

var file = new File(fileName, "wb");
file.write(buffer);
file.close();

console.log("[+] 已导出到: " + fileName);

}

// 使用
dumpSo("libnative-lib.so");

```

adb pull /sdcard/libnative-lib.so .

```
cd frida-all-in-one

# 运行命令

python3 dump_so.py -U com.example.app libnative-lib.so

# 会自动导出并修复 SO 文件

```

#### 5.1 使用 SoFixer

```bash
# 下载
git clone https://github.com/F8LEFT/SoFixer.git
cd SoFixer

# 编译（需要 CMake）
mkdir build && cd build
cmake ..
make

# 使用
./SoFixer ../libnative-lib.so ../libnative-lib_fixed.so

```

[+] Detected architecture: ARM64
[+] Rebuilding ELF header...
[+] Fixing section table...
[+] Fixing dynamic symbols...
[+] Output file: libnative-lib_fixed.so
[+] Done!

```
# 应该显示: ELF 64-bit LSB shared object, ARM aarch64...

# 用 IDA Pro 打开
# 或用 readelf 查看
readelf -h libnative-lib_fixed.so

```

```
解密原始 DEX（在内存中）
↓
调用 DexFile::OpenCommon 加载 DEX ← Frida Hook 点
↓
Frida 读取内存中的 DEX 数据
↓
保存到文件

```

size_t size, // DEX 大小
...)

```
Only dump This些段OriginalData，缺少 ELF File结构

```

[.text 段]
[.data 段]
[.rodata 段]
...
[Symbol Table] ← 重建
[String Table] ← 重建

```
| 梆梆加固 | libDexHelper.so | |
| 腾讯加固 | libtup.so | |
| 爱加密 | libexec.so | |
| 网易易盾 | libnesec.so | |

* *通用策略**：所有加固都需要在运行时解密，Frida 脱壳都有效！

- --

## 常见问题

### ❌ 问题 1: frida-dexdump 报错 "Failed to spawn"

* *症状**：

```

adb shell pm list packages | grep example

# 2. 确认包名正确

# 从 AndroidManifest.xml 获取准确包名

# 3. 尝试 Attach 模式

# 先手动启动应用

adb shell am start -n com.example.app/.MainActivity

# 再附加

python3 main.py -U com.example.app

````

1. **DEX 头部损坏**
    ```bash
# 检查魔数
xxd dumped.dex | head -1
# 应该看到: 64 65 78 0a (dex\n)

```
    ```python
# 验证 DEX 大小
with open('dumped.dex', 'rb') as f:
f.seek(32) # 跳到 file_size 字段
size = int.from_bytes(f.read(4), 'little')
print(f"DEX 声明的大小: {size}")

import os
actual_size = os.path.getsize('dumped.dex')
print(f"实际文件大小: {actual_size}")

```
    ```bash
git clone https://github.com/anestisb/dexrepair.git
python3 dexrepair/dexrepair.py dumped.dex fixed.dex

```

* *检查步骤**：

1. **确认 libart.so 已加载**
    ```javascript
var libart = Process.findModuleByName("libart.so");
console.log("libart found:", libart !== null);

```
    ```javascript
Module.enumerateExports("libart.so").forEach(function(exp) {
if (exp.name.includes("OpenCommon")) {
console.log(exp.name);
}
});

```
    ```javascript
// android 7.0-
var OpenMemory = Module.findExportByName("libart.so",
"_ZN3art7DexFile10OpenMemoryEPKhjRKNSt3__112basic_stringIcNS3_11char_traitsIcEENS3_9allocatorIcEEEEjPNS_6MemMapEPKNS_10OatDexFileEPS9_");

```

* *症状**：IDA 打开后只显示数据，没有函数

* *解决**：

1. **手动定义函数**
    ```

IDA In：
- 光标移到疑似Function起始处
- By 'P' KeyCreateFunction
- By 'C' KeyConvert为Code
    ```

2. **使用符号恢复工具**
    ```bash
# If 原始 SO 有符号table
readelf -s original.so > symbols.txt

# 用 IDA ScriptImport符号

```
- 如果看到大量跳转和无意义的代码块
- 可能是 OLLVM 控制流平坦化
- 参考：[OLLVM 反混淆](../Analysis/ollvm_deobfuscation.md)

- 如果看到大量跳转和无意义的代码块
- 可能是 OLLVM 控制流平坦化
- 参考：[OLLVM 反混淆](../Analysis/ollvm_deobfuscation.md)


### ❌ 问题 5: App 检测到 Frida 并崩溃

* *症状**：启动后立即退出，logcat 显示反调试提示

* *解决**：

参考 [Frida 反调试绕过](../Anti-Detection/frida_anti_debugging.md)

快速方法：

```bash
# 使用 Magisk Hide
# 或使用修改版 Frida 服务器
wget https://github.com/hluwa/strongR-frida-android/releases/download/xxx/frida-server

````

- **[应用脱壳总览](./un-packing.md)** - 各种脱壳技术对比
- **[Frida 反调试绕过](../Anti-Detection/frida_anti_debugging.md)** - 处理反 Frida 检测
- **[SO 混淆分析](./so_obfuscation_deobfuscation.md)** - 分析混淆的 SO 文件
- **[OLLVM 反混淆](../Analysis/ollvm_deobfuscation.md)** - 处理控制流混淆

### 工具深入

- **[Frida 完整指南](../../02-Tools/Dynamic/frida_guide.md)**
- **[IDA Pro 使用](../../02-Tools/Static/ida_pro_guide.md)**

### 项目资源

| 项目                         | 说明                                     |
| ---------------------------- | ---------------------------------------- |
| **frida-dexdump** - https    | //github.com/hluwa/frida-dexdump         |
| **FRIDA-DEXDump** - https    | //github.com/lasting-yang/frida_dump     |
| **SoFixer** - https          | //github.com/F8LEFT/SoFixer              |
| **frida-all-in-one** - https | //github.com/hookmaster/frida-all-in-one |

### 理论基础

- **[DEX 文件格式](../../04-Reference/Foundations/dex_format.md)**
- **[SO/ELF 文件格式](../../04-Reference/Foundations/so_elf_format.md)**
- **[ART 运行时](../../04-Reference/Foundations/art_runtime.md)**

---

## 快速参考

### 脱壳工具对比

| 工具              | 类型   | 难度 | 特点               |
| ----------------- | ------ | ---- | ------------------ |
| **frida-dexdump** | 自动化 |      | 简单，支持多版本   |
| **FRIDA-DEXDump** | 自动化 |      | 深度搜索，更全面   |
| **手动脚本**      | 定制   |      | 灵活，适合特殊情况 |
| **objection**     | 交互式 |      | 多功能，含脱壳     |

### 一键脱壳脚本

**auto_unpack.sh**：

```bash
#!/bin/bash

PACKAGE=$1

if [ -z "$PACKAGE" ]; then
echo "用法: $0 <package_name>"
exit 1
fi

echo " 开始脱壳: $PACKAGE"

# 1. Dump DEX
echo ""
echo "📦 导出 DEX 文件..."
python3 ~/tools/frida-dexdump/main.py -U -f $PACKAGE

# 2. Dump SO
echo ""
echo " 导出 SO 文件..."
frida -U -f $PACKAGE -l dump_all_so.js --no-pause

sleep 5

# 3. 拉取文件
echo ""
echo "📥 拉取文件..."
adb pull /sdcard/*.dex .
adb pull /sdcard/*.so .

# 4. 清理
adb shell rm /sdcard/*.dex
adb shell rm /sdcard/*.so

echo ""
echo "✅ 完成! 文件已保存到当前目录"
ls -lh *.dex *.so

```

function dumpAllSo() {
var modules = Process.enumerateModules();
console.log("[*] 找到 " + modules.length + " 个模块");

modules.forEach(function(module) {
// 只导出 .so 文件
if (!module.name.endsWith('.so')) {
return;
}

// 排除系统库
if (module.path.startsWith('/system') ||
module.path.startsWith('/apex')) {
return;
}

console.log("[+] 导出: " + module.name);
console.log(" 路径: " + module.path);
console.log(" 基址: " + module.base);
console.log(" 大小: " + module.size);

try {
var buffer = module.base.readByteArray(module.size);
var fileName = "/sdcard/" + module.name;
var file = new File(fileName, "wb");
file.write(buffer);
file.close();
console.log(" 已保存: " + fileName);
} catch(e) {
console.log(" 错误: " + e);
}
});

console.log("[*] 完成!");

}

setImmediate(dumpAllSo);

<!-- 01-Recipes/Unpacking/so_obfuscation_deobfuscation.md -->

# SO 文件反混淆：花指令识别与自动化去除

在 Android SO 文件逆向工程中，**代码混淆 (Code Obfuscation)**，俗称"花指令"，是开发者为了保护核心逻辑、增加逆向分析难度而采用的一种常用技术。其核心思想是在代码中插入大量对程序本身逻辑无用但能迷惑反汇编工具和分析人员的指令。

本指南将系统介绍花指令的常见类型、识别方法，并重点阐述如何利用 `IDAPython` 编写脚本，实现自动化"去花"。

---

## 目录

- [SO 文件反混淆：花指令识别与自动化去除](#so-文件反混淆花指令识别与自动化去除)
- [目录](#目录)

- [花指令的核心类型](#花指令的核心类型)
- [垃圾指令 (Junk Code)](#垃圾指令-junk-code)

- [不透明谓词 (Opaque Predicates)](#不透明谓词-opaque-predicates)

- [指令替换 (Instruction Substitution)](#指令替换-instruction-substitution)

- [控制流平坦化 (Control Flow Flattening)](#控制流平坦化-control-flow-flattening)
- [如何识别花指令](#如何识别花指令)
- [静态分析特征](#静态分析特征)

- [动态调试验证](#动态调试验证)
- [自动化"去花"脚本 (IDAPython 实战)](#自动化去花脚本-idapython-实战)
- [场景一：NOP 掉无效跳转](#场景一nop-掉无效跳转)

- [场景二：修复不透明谓词](#场景二修复不透明谓词)
- [总结](#总结)

---

## 花指令的核心类型

## # 垃圾指令 (Junk Code)

最简单的混淆形式。在真实指令之间插入不会影响程序状态（寄存器、内存、标志位）的指令。

```assembly
; 真实代码
PUSH EAX

; --- 垃圾代码 ---
NOP
MOV EBX, EBX
XCHG ECX, ECX
ADD EAX, 0
; --- 垃圾代码结束 ---

; 真实代码
POP EAX

```

MOV EAX, EDX
XOR EAX, EDX ; 清零 EAX
TEST EAX, EAX ; 设置 Z 标志

; JZ (为零则跳转) 将始终跳转
; JNZ 分支下的代码是永远不会执行的死代码
JZ real_code_path
; --- 死代码 ---
ADD EAX, 1234
CALL some_fake_func
; --- 死代码结束 ---

real_code_path:
; ...

````

## # 控制流平坦化 (Control Flow Flattening)
这是一种高级且非常有效的混淆技术。它将一个函数的正常逻辑块打散，然后使用一个中央分发器（Dispatcher）和 `switch-case` 结构来控制执行流。原始的调用关系被隐藏在一个巨大的循环中，使得函数逻辑极难被理解。

- --

## 如何识别花指令

## # 静态分析特征
在 IDA Pro 或 Ghidra 中观察：

* **无效跳转**：`JMP loc_A` 的下一条指令就是 `loc_A`。

* **跳转到指令中间**：`JMP $+5` 跳转到一个正常指令的中间，破坏反汇编。

* **对称操作**：连续的 `PUSH`/`POP` 同一个寄存器。

* **恒成立/不成立的条件**：在 `Jcc` 指令前，`CMP` 的两个操作数明显相等或不等。

* **无意义的计算**：计算结果没有被后续代码使用。

* **IDA 图形视图**：控制流平坦化的函数会呈现出一个巨大的、节点众多的 `switch` 结构，所有逻辑块都指向一个中心分发块。

## # 动态调试验证
最可靠的方法。使用 `gdb` 或 IDA 的调试器：

* 在可疑分支下断点，如果断点从未命中，则说明该分支是死代码。

* 单步执行，观察寄存器和内存的变化。如果一段指令执行后，相关的状态没有变化，则很可能是垃圾代码。

- --

## 自动化"去花"脚本 (IDAPython 实战)

当花指令数量庞大时，手动修复是不现实的。编写脚本自动化处理是唯一高效的途径。以下以 IDAPython 为例。

## # 场景一：NOP 掉无效跳转
一个常见的花指令模式是 `JMP dest`，而 `dest` 紧接着 `JMP` 指令。

```assembly
.text:00001234 JMP short loc_1236 ; 跳转指令本身占 2 字节
.text:00001236 ; ... 真实代码

````

import idaapi

def patch_junk_jumps():
"""
查找并将形式为 `JMP next_instruction` 的跳转 NOP 掉。
"""
print("扫描垃圾跳转...")
count = 0

# 遍历代码段

for seg_ea in idc.get_segm_list():
if idc.get_segm_attr(seg_ea, idc.SEGATTR_TYPE) != idc.SEG_CODE:
continue

seg_start = idc.get_segm_start(seg_ea)
seg_end = idc.get_segm_end(seg_ea)

for head in idautils.Heads(seg_start, seg_end):

# 检查是否是 JMP 指令

if idaapi.is_jmp_insn(head):

# 获取跳转目标地址

target_ea = idc.get_operand_value(head, 0)

# 获取指令长度

insn_len = idc.get_item_size(head)

# 如果跳转目标是下一条指令的地址

if target_ea == (head + insn_len):
print(f"在 0x{head:X} 处找到垃圾 JMP，目标: 0x{target_ea:X}")

# 用 NOP 修补

for i in range(insn_len):
idc.patch_byte(head + i, 0x90)
count += 1

print(f"完成。修补了 {count} 个垃圾跳转。")

# --- 执行脚本 ---

# patch_junk_jumps()

```
# ... 遍历指令 ...
head = ...

# 检查是否是 JNE 指令 (例如，操作码 0x75)
if idc.get_byte(head) == 0x75:
# 检查 JNE 之前的指令是否是 CMP
prev_head = idc.prev_head(head)
if idc.print_insn_mnem(prev_head) == "cmp":
# 检查 CMP 的两个操作数是否相同
op1 = idc.get_operand_value(prev_head, 0)
op2 = idc.get_operand_value(prev_head, 1)

# 这是一个简化示例，实际的操作数类型检查会更复杂
# if idc.get_operand_type(prev_head, 0) == o_reg and ...
if op1 == op2: # 例如，CMP EAX, EAX
print(f"在 0x{head:X} 处找到不透明谓词")
# 将 JNE 指令 NOP 掉
insn_len = idc.get_item_size(head)
for i in range(insn_len):
idc.patch_byte(head + i, 0x90)

```

2. **识别**：找到该模式的通用机器码或指令特征。
3. **编码**：编写脚本，精确地定位这些特征并进行修复 (Patch)。

虽然花指令的变种层出不穷，但其本质是有限的。掌握了自动化的脚本去花能力，就能极大地提升 SO 文件逆向分析的效率。

````



<!-- 01-Recipes/Unpacking/so_string_deobfuscation.md -->

# SO 文件字符串混淆对抗指南

在 Android Native 层安全中，字符串混淆是一种用于隐藏敏感信息、增加逆向分析难度的常用技术。开发者通过对 SO 文件中的关键字符串（如 API URL、加密密钥、Shell 命令、功能开关等）进行编码或加密，可以有效防止静态分析工具（如 `strings` 命令或 IDA Pro 的字符串窗口）直接发现它们。

本文旨在系统性地介绍 SO 文件中常见的字符串混淆技术，并提供一套从静态分析到动态分析的完整对抗策略。

- --

## 目录
- [SO 文件字符串混淆对抗指南](#so-文件字符串混淆对抗指南)
- [目录](#目录)
- [字符串混淆的核心思想](#字符串混淆的核心思想)

- [常见的混淆技术](#常见的混淆技术)

- [对抗策略一：静态分析 (IDA Pro / Ghidra)](#对抗策略一静态分析-ida-pro--ghidra)
- [识别解密/解混淆函数](#识别解密解混淆函数)

- [定位交叉引用](#定位交叉引用)

- [自动化脚本解密](#自动化脚本解密)
- [对抗策略二：动态分析 (Frida)](#对抗策略二动态分析-frida)
- [Hook 解密函数（首选策略）](#hook-解密函数首选策略)

- [内存漫游与搜索](#内存漫游与搜索)
- [总结：最高效的分析流程](#总结最高效的分析流程)

- --

### 字符串混淆的核心思想

其本质是**避免将明文字符串直接存储在二进制文件的 `.rodata` 或 `.data` 段中**。取而代之的是，在程序运行时，通过特定的函数动态地在内存中（栈或堆）恢复出原始的字符串。

一个典型的流程如下：
`加密的字节数组` -> `解密/解混淆函数` -> `内存中的明文字符串`

我们的目标就是截获"内存中的明文字符串"。

- --

### 常见的混淆技术

1. **简单编码**:
* **Base64**: 将 Base64 编码后的字符串存储，使用时再解码。

* **ROT13/Caesar Cipher**: 简单的字符位移。
2. **按位运算**:
* **XOR (异或)**: 将原始字符串与一个固定的（或动态计算的）密钥进行按字节异或。这是最常见、最高效的一种方式。
3. **栈上构建**:
* 不在任何段中存储字符串，而是在函数开始时，通过一系列 `mov` 指令逐字节地将字符串 push 到栈上。
    ```c++
void get_secret_string() {
char secret[12];
secret[0] = 's';
secret[1] = 'e';
// ...
secret[10] = 't';
secret[11] = '\0';
// use secret
}

````

- 使用如 AES, RC4, DES 等标准对称加密算法。密钥本身可能被再次混淆或从其他地方动态获取。

---

### 对抗策略一：静态分析 (IDA Pro / Ghidra)

静态分析的目标是**理解解密逻辑并自动化地应用它**。

#### 识别解密/解混淆函数

- **特征**: 解密函数通常具有以下一个或多个特征：
- 接受一个指向字节数组的指针和一个长度作为参数。

- 函数内部包含一个循环结构（`for` / `while`）。

- 循环内部有按位操作，特别是 `XOR` (异或) 指令。

- 函数的交叉引用（Xrefs）非常多，且调用的地方都伴随着一个数据块的地址。
- **方法**: 在 IDA Pro 或 Ghidra 中，通过搜索这些代码模式，通常能很快定位到核心的解密函数。

#### 定位交叉引用

一旦你识别出了解密函数（例如 `decrypt_string`），立即查看它的所有交叉引用。每一个调用 `decrypt_string` 的地方，都是一个加密字符串被使用的地方。传递给该函数的参数，就是加密的数据。

#### 自动化脚本解密

这是静态分析的精髓所在。

1. **分析算法**: 仔细阅读解密函数的汇编或反编译代码，用一种高级语言（如 Python）重新实现其逻辑。

   ```python

   ```

# 示例: Python 实现的简单 XOR 解密算法

def decrypt_xor(data, key):
decrypted = bytearray()
for i in range(len(data)):
decrypted.append(data[i] ^ key[i % len(key)])
return decrypted.decode('utf-8')

````

* **脚本逻辑**:
1. 获取解密函数的地址。
2. 遍历该函数的所有交叉引用。
3. 在每个交叉引用的地方，解析其参数，提取出加密数据块的地址和长度。
4. 读取加密数据。
5. 调用步骤 1 中实现的 Python 解密函数。
6. **将解密后的明文字符串，作为注释，添加到交叉引用的代码行旁边**。

* **效果**: 运行脚本后，IDA/Ghidra 中的代码将变得非常易读，所有加密字符串都以注释的形式被"还原"了。

- --

### 对抗策略二：动态分析 (Frida)
动态分析的核心思想是**不关心解密过程，只关心解密结果**。它通常更快速、更直接。

#### Hook 解密函数（首选策略）
这是对抗字符串混淆**最简单、最高效**的方法。
1. **定位函数**: 使用静态分析工具（IDA/Ghidra）找到解密函数的地址。
2. **编写 Frida 脚本**:
* **Hook `onEnter`**: 在进入解密函数时，打印其输入参数（加密的字节数组）。

* **Hook `onLeave` (更常用)**: 在函数返回时，直接读取其返回值。因为返回值通常就是指向内存中明文字符串的指针。
    ```javascript
const decryptFuncPtr = Module.findExportByName("libnative-lib.so", "Java_com_example_MainActivity_decryptString");
// 或者直接使用地址: const decryptFuncPtr = Module.getBaseAddress("libnative-lib.so").add(0x1234);

Interceptor.attach(decryptFuncPtr, {
onEnter: function(args) {
console.log("进入 decryptString，数据: " + args[0].readCString());
},
onLeave: function(retval) {
// retval 是指向解密后字符串的指针
var decryptedString = retval.readCString();
console.log("解密后的字符串 -> " + decryptedString);
// 可以进一步将结果写入文件
// send({ decrypted: decryptedString });
}
});

````

#### 内存漫游与搜索

在某些情况下，App 可能会在启动时一次性解密大量字符串，并将它们存放在一个特定的内存区域。

- **方法**:

1. 让 App 运行一段时间。
2. 使用 Frida 的 `Memory.scan` API 在进程的整个内存空间中搜索你感兴趣的字符串模式（例如，`https://`）。
   ```javascript
   Memory.scan(
     Process.findModuleByName("libnative-lib.so").base,
     Process.findModuleByName("libnative-lib.so").size,
     "68 74 74 70 73 3a 2f 2f",
     {
       // 十六进制表示 "https://"
       onMatch: function (address, size) {
         console.log("在以下地址找到模式: " + address);
         // 可能需要回退一些字节来找到字符串的起始位置
         console.log(address.readCString());
       },
       onComplete: function () {
         console.log("内存扫描完成。");
       },
     }
   );
   ```

````

### 总结：最高效的分析流程
对于字符串混淆，最高效的工作流程是结合静态和动态分析：
1. **静态分析定位**: 使用 IDA Pro 或 Ghidra 快速浏览 SO 文件，识别出可能的解密/解混淆函数。
2. **动态分析验证/获取**: 使用 Frida 对上一步定位到的函数地址进行 Hook，运行 App 并观察 `onLeave` 的返回值，快速获取所有解密后的字符串。
3. **(可选) 静态分析脚本化**: 如果需要对大量字符串进行离线分析或希望得到一个带注释的、更易读的反汇编文件，再回到静态分析工具中，根据已知的算法编写自动化解密脚本。


<!-- 01-Recipes/Unpacking/un-packing.md -->

# Recipe: 脱壳分析加固的 android 应用

## 问题场景

你在逆向分析一个 App 时遇到了以下情况：

- ❌ **Jadx 打开 APK 后代码完全不可读**，全是混淆的类名或空方法
- ❌ **classes.dex 文件异常小** (几十 KB)，不符合应用实际规模
- ❌ **应用启动时检测到 Frida 并闪退**，常规 Hook 无法生效
- ❌ **AndroidManifest.xml 中的 Application 入口被替换**成可疑的壳类名
- ❌ **`assets` 或 `lib` 目录中存在加密文件**，如 `.dat`、`.bin` 或奇怪命名的 `.so` 文件

这些都是应用被**加固(加壳)**的典型特征。加固技术通过加密 DEX 文件、抽取方法体、虚拟化指令等手段，让静态分析工具无法直接读取原始代码。本配方将教你如何识别、脱壳并恢复被加固的应用。

- --

## 工具清单

## # 必需工具

- [x] **Frida** - 动态插桩框架
- [x] **frida-dexdump** - 自动化 DEX dumper ([GitHub](https://github.com/hluwa/frida-dexdump))
- [x] **ADB** - 设备通信工具
- [x] **Root 权限设备** 或模拟器 (必须)

## # 可选工具

- ☐ **FUPK3** - 针对特定壳的专用脱壳工具
- ☐ **Youpk** - 较新的脱壳工具
- ☐ **PKid/ApkTool-Plus** - 加固类型识别工具
- ☐ **MT 管理器** - Android 端 APK 分析工具
- ☐ **IDA Pro/Ghidra** - Native 层分析 (SO 加固时需要)

- --

## 前置条件

在开始前请确认：

✅ **设备已 Root** 并安装 Frida Server
✅ **了解 DEX 文件基本结构** (至少知道 magic number `0x6465780A`)
✅ **应用已安装**并能正常启动 (即使有反调试)
✅ **磁盘空间充足** (脱壳可能产生大量文件)

- --

## 解决方案

## # 核心原理

> **"代码运行必解密"**
>
> 无论加固技术多么复杂，加密后的代码最终都必须在内存中恢复成可执行的 DEX 格式，才能被 ART 执行。脱壳的核心思想是：**在代码被解密后、执行前的那一刻，从内存中将其 dump 出来。**

- --

## # 第 1 步: 识别加固类型 ( 5-10 分钟)

不同代际的加固技术需要不同的脱壳策略，先识别目标应用使用了什么加固技术。

### 方法 A: 使用工具快速识别

```bash
# 使用 PKid (ApkTool-Plus) 检测
# 下载: https://github.com/rover12421/ApkToolPlus
java -jar ApkToolPlus.jar -pkid target.apk

# 输出示例:
# [+] 检测到加固厂商: 腾讯乐固 (Tencent Legu)
# [+] 加固类型: 第二代壳 (方法抽取)

````

# 可疑类名:

# com.tencent.StubShell.TxAppEntry (腾讯乐固)

# com.secneo.apkwrapper.ApplicationWrapper (梆梆 Security)

# com.baidu.protect.StubApplication (百度加固)

# 2. 检查 DEX 文件大小

unzip -l target.apk | grep classes.dex

# 如果 classes.dex < 100KB 且 App 功能复杂，很可能加壳

# 3. 检查可疑文件

unzip -l target.apk | grep -E "\.dat|\.bin|ijm_lib|secdata"

# 这些文件通常包含加密的原始 DEX

# 4. 检查 lib 目录中的可疑 SO

unzip -l target.apk | grep "lib/.\*\*\.so" | grep -E "(exec|vmp|protect)"

````
| **第一代** | 2010-2015 | 整体 DEX 加密 | 早期爱加密、360 | Application 入口被替换 | (简单) |
| **第二代** | 2015-2018 | 方法抽取 (Stolen Code) | 腾讯乐固、阿里聚安全 | 大量空方法、libexec.so | (中等) |
| **第三代** | 2018-2021 | 指令虚拟化 (VMP) | 梆梆VMP、顶象科技 | 自定义VM引擎、私有指令 | (困难) |
| **第四代** | 2021-至今 | 云端+多重保护 | 腾讯御安全、阿里云 | 云端下发代码、多层加壳 | (极难) |

- --

## # 第 2 步: 选择脱壳策略 ( 5 分钟)

根据识别出的加固类型，选择合适的脱壳方法：

### 第一代壳 (整体加密)
* *策略**: Hook ClassLoader，在 DEX 加载时 dump
* *推荐工具**: 手写 Frida 脚本或 frida-dexdump
* *成功率**: 95%+

### 第二代壳 (方法抽取)
* *策略**: Hook ArtMethod 的 invoke，在方法首次调用时 dump CodeItem
* *推荐工具**: FART 技术 (Frida ART Hook) + frida-dexdump
* *成功率**: 80%+ (取决于代码覆盖率)

### 第三代壳 (虚拟化)
* *策略**: Hook 虚拟机引擎，获取指令流 + 映射表逆向
* *推荐工具**: IDA Pro + 自定义脚本
* *成功率**: 50% (需要深入分析虚拟机实现)

### 第四代壳 (云端)
* *策略**: 网络抓包 + 内存扫描 + 多层 dump
* *推荐工具**: mitmproxy + frida-dexdump + 自定义脚本
* *成功率**: 30% (部分逻辑可能无法获取)

- --

## # 第 3 步: 执行脱壳 ( 10-60 分钟)

以下提供针对不同代际的脱壳脚本。

### 方法 A: 使用 frida-dexdump (通用，推荐首选)

```bash
# 1. 启动 Frida Server
adb push frida-server /data/local/tmp/
adb shell "chmod 755 /data/local/tmp/frida-server"
adb shell "/data/local/tmp/frida-server &"

# 2. 安装 frida-dexdump
pip3 install frida-dexdump

# 3. 运行脱壳 (Spawn 模式，在 App 启动时拦截)
python3 -m frida_dexdump -U -f com.target.app -o ./output

# 输出示例:
# [+] Hooking ClassLoader...
# [+] Dumped DEX: /output/com.target.app_1234567890.dex (5.2 MB)
# [+] Dumped DEX: /output/com.target.app_0987654321.dex (1.8 MB)
# [+] Total: 2 DEX files dumped

# 4. 将 DEX 文件拉取到本地
adb pull /data/data/com.target.app/files/*.dex ./dumped_dex/

````

- `-o ./output`: 输出目录

---

### 方法 B: 手写 Hook 脚本 (第一代壳)

适用于简单的整体加密壳。

```javascript
// unpacker_gen1.js - 第一代壳通用脚本

Java.perform(function () {
  console.log("[+] 开始 Hook ClassLoader...");

  // 拦截 1: DexClassLoader (最常见)
  var DexClassLoader = Java.use("dalvik.system.DexClassLoader");
  DexClassLoader.$init.implementation = function (
    dexPath,
    optimizedDirectory,
    librarySearchPath,
    parent
  ) {
    console.log("[+] DexClassLoader 加载 DEX:");
    console.log(" 路径: " + dexPath);

    // 尝试复制 DEX 文件
    if (dexPath && dexPath.indexOf("/data/data/") !== -1) {
      try {
        var File = Java.use("java.io.File");
        var FileInputStream = Java.use("java.io.FileInputStream");
        var FileOutputStream = Java.use("java.io.FileOutputStream");

        var srcFile = File.$new(dexPath);
        if (srcFile.exists()) {
          var timestamp = Date.now();
          var dstPath =
            "/data/data/com.target.app/dumped_" + timestamp + ".dex";
          var dstFile = File.$new(dstPath);

          var fis = FileInputStream.$new(srcFile);
          var fos = FileOutputStream.$new(dstFile);

          var buffer = Java.array("byte", [1024]);
          var len;
          while ((len = fis.read(buffer)) > 0) {
            fos.write(buffer, 0, len);
          }

          fis.close();
          fos.close();

          console.log("✓ [已导出] " + dstPath);
        }
      } catch (e) {
        console.log("[-] 复制失败: " + e);
      }
    }

    return this.$init(dexPath, optimizedDirectory, librarySearchPath, parent);
  };

  // Hook 2: InMemoryDexClassLoader (内存加载)
  try {
    var InMemoryDexClassLoader = Java.use(
      "dalvik.system.InMemoryDexClassLoader"
    );
    InMemoryDexClassLoader.$init.overload(
      "java.nio.ByteBuffer",
      "java.lang.ClassLoader"
    ).implementation = function (byteBuffer, classLoader) {
      console.log("[+] InMemoryDexClassLoader 加载内存 DEX");

      // 从 ByteBuffer 提取 DEX
      try {
        var remaining = byteBuffer.remaining();
        console.log(" DEX 大小: " + remaining + " bytes");

        // 获取字节数组
        var bytes = Java.array("byte", [remaining]);
        byteBuffer.get(bytes);

        // 写入文件
        var timestamp = Date.now();
        var dstPath = "/data/data/com.target.app/memory_" + timestamp + ".dex";
        var File = Java.use("java.io.File");
        var FileOutputStream = Java.use("java.io.FileOutputStream");

        var dstFile = File.$new(dstPath);
        var fos = FileOutputStream.$new(dstFile);
        fos.write(bytes);
        fos.close();

        console.log("✓ [已导出] " + dstPath);

        // 重置 ByteBuffer 位置
        byteBuffer.position(0);
      } catch (e) {
        console.log("[-] 导出失败: " + e);
      }

      return this.$init(byteBuffer, classLoader);
    };
  } catch (e) {
    console.log("[-] InMemoryDexClassLoader 不存在 (Android < 8.0)");
  }

  console.log("[+] Hook 完成，等待 DEX 加载...");
});
```

# Attach 模式

frida -U com.target.app -l unpacker_gen1.js

````

```javascript
// unpacker_fart.js - FART (Frida-ART-Hook) 脚本

// 警告: 此脚本需要深入理解 ART 内部机制，不同 Android 版本可能需要调整偏移

var artMethodInvokeAddr = null;

// 根据 Android 版本查找 ArtMethod::Invoke 符号
var symbols = [
"_ZN3art9ArtMethod6InvokeEPNS_6ThreadEPjjPNS_6JValueEPKc", // Android 7.0+
"_ZN3art9ArtMethod6InvokeEPNS_6ThreadEPjmPNS_6JValueEPKc", // Android 8.0+
];

for (var i = 0; i < symbols.length; i++) {
artMethodInvokeAddr = Module.findExportByName("libart.so", symbols[i]);
if (artMethodInvokeAddr) {
console.log("[+] 找到 ArtMethod::Invoke: " + artMethodInvokeAddr);
break;
}
}

if (!artMethodInvokeAddr) {
console.log("[-] 未找到 ArtMethod::Invoke，无法继续");
} else {
Interceptor.attach(artMethodInvokeAddr, {
onEnter: function(args) {
var artMethod = args[0];

// 读取 ArtMethod 结构中的 CodeItem (偏移因版本而异)
// 这里以 Android 7.0 为例，实际使用需要根据版本调整
try {
// 获取方法名 (通过 PrettyMethod)
var prettyMethodAddr = Module.findExportByName("libart.so", "_ZN3art9ArtMethod12PrettyMethodEv");
if (prettyMethodAddr) {
var prettyMethod = new NativeFunction(prettyMethodAddr, 'pointer', ['pointer']);
var methodName = prettyMethod(artMethod).readCString();

// 只关注 App 自身方法，忽略系统方法
if (methodName && methodName.indexOf("com.target.app") !== -1) {
console.log("[+] 调用方法: " + methodName);

// 尝试获取 CodeItem
// 注意: CodeItem 偏移在不同版本中不同
// Android 7.0: offset 24
// Android 8.0+: offset 16
var codeItemOffset = 24; // 需要根据实际版本调整
var codeItemPtr = artMethod.add(codeItemOffset).readPointer();

if (codeItemPtr && !codeItemPtr.isNull()) {
// 读取 CodeItem 结构
var registersSize = codeItemPtr.readU16();
var insSize = codeItemPtr.add(2).readU16();
var outsSize = codeItemPtr.add(4).readU16();
var triesSize = codeItemPtr.add(6).readU16();
var insnsSize = codeItemPtr.add(12).readU32();

if (insnsSize > 0 && insnsSize < 100000) {
console.log(" 找到 CodeItem: insnsSize = " + insnsSize);

// 导出字节码
var insnsPtr = codeItemPtr.add(16);
var codeData = Memory.readByteArray(insnsPtr, insnsSize * 2);

// 保存到文件
var safeMethodName = methodName.replace(/[^a-zA-Z0-9]/g, "_");
var filename = "/data/data/com.target.app/code_" + safeMethodName + ".bin";
var file = new File(filename, "wb");
file.write(codeData);
file.close();

console.log("✓ [已导出 CodeItem] " + filename);
}
}
}
}
} catch (e) {
// 忽略读取错误
}
}
});

console.log("[+] FART Hook 已激活，开始监控方法调用...");
}

````

- 只能 dump **被调用过的方法**，未触发的方法无法恢复

---

### 方法 D: 内存扫描 (通用兜底方案)

当其他方法失效时，可以定期扫描内存中的 DEX magic number。

```javascript
// unpacker_memscan.js - 内存扫描脚本

function scanMemoryForDex() {
  console.log("[+] 开始扫描内存中的 DEX 文件...");

  var ranges = Process.enumerateRanges("r--"); // 仅扫描可读区域
  var found = 0;

  ranges.forEach(function (range) {
    try {
      // DEX magic: "dex\n" = 0x6465780A
      var pattern = "64 65 78 0a";

      Memory.scan(range.base, range.size, pattern, {
        onMatch: function (address, size) {
          console.log("[+] 发现潜在 DEX: " + address);

          try {
            // 读取 DEX 文件大小 (偏移 32 字节处)
            var dexSize = address.add(32).readU32();

            // 合理性检查
            if (dexSize > 0x1000 && dexSize < 50 * 1024 * 1024) {
              console.log(" DEX Size: " + (dexSize / 1024).toFixed(2) + " KB");

              // Dump DEX
              var dexData = Memory.readByteArray(address, dexSize);
              var filename =
                "/data/data/com.target.app/memdump_" +
                address.toString().replace("0x", "") +
                ".dex";
              var file = new File(filename, "wb");
              file.write(dexData);
              file.close();

              console.log("✓ [Dumped] " + filename);
              found++;
            }
          } catch (e) {
            // 读取失败，跳过
          }
        },
        onComplete: function () {},
      });
    } catch (e) {
      // 忽略无法访问的内存区域
    }
  });

  console.log("[+] 扫描完成，找到 " + found + " 个 DEX 文件");
}

// 每 5 秒扫描一次
setInterval(function () {
  scanMemoryForDex();
}, 5000);

console.log("[+] 内存扫描已启动");
```

adb pull /data/data/com.target.app/ ./dumped_files/

# 2. 查看提取到的 DEX 文件

ls -lh ./dumped_files/\*\*.dex

# 输出示例:

# -rw-r--r-- 1 user user 5.2M dumped_1234567890.dex

# -rw-r--r-- 1 user user 1.8M dumped_0987654321.dex

# 3. 验证 DEX 文件完整性

xxd ./dumped_files/dumped_1234567890.dex | head -n 2

# 应该看到 DEX magic: 64 65 78 0a (dex\n)

# 4. 使用 Jadx 打开验证

jadx ./dumped_files/dumped_1234567890.dex

# 如果能正常反编译，表示脱壳成功

````

### 常见需要修复的情况:

1. **方法体被 NOP 填充**:
- 症状: Jadx 反编译后看到大量空方法或只有 `return` 的方法
- 原因: 壳用占位符替换了真实代码
- 解决: 如果用 FART dump 了 CodeItem，需要手动替换回去

2. **字符串池损坏**:
- 症状: 反编译后字符串显示为乱码或缺失
- 解决: 使用 `dex-repair` 工具重建字符串池

3. **类/方法索引错乱**:
- 症状: 方法调用关系不正确
- 解决: 使用 `smali/baksmali` 重新组装

### 自动化修复工具

```bash
# 使用 dex-repair (开源工具)
git clone https://github.com/F8LEFT/dex-repair
cd dex-repair
python3 repair.py ./dumped_files/dumped_1234567890.dex -o ./fixed.dex

# 验证修复结果
jadx ./fixed.dex

````

# 这需要使用 DexPatcher 或自定义脚本

# 2. 反汇编 DEX

baksmali d dumped_1234567890.dex -o ./smali_output

# 3. 查找空方法并替换

# 在 smali_output 中，找到方法体为空的 .smali 文件

# 将导出的 CodeItem 反汇编后的内容复制进去

# 4. 重新组装

smali a ./smali_output -o ./repacked.dex

# 5. 验证

jadx ./repacked.dex

```

│ 1. DEX 加密 │ 将 classes.dex 加密为 encrypted.dat
└────────┬────────┘
↓
┌─────────────────┐
│ 2. 壳代替换 │ 用壳 DEX 替换 classes.dex
└────────┬────────┘
↓
┌─────────────────┐
│ 3. 重新打包签名 │ 生成加固后的 APK
└─────────────────┘

运行时解密流程:
Application.onCreate()
↓
壳代码执行
↓
解密 encrypted.dat
↓
DexClassLoader.load(解密后的 DEX)
↓
跳转到原始 Application 入口

```

↓
壳代码运行
↓
解密原始 DEX ← Hook 点 1: ClassLoader
↓
ART 加载 DEX 到内存 ← Hook 点 2: libart.so
↓
编译为 OAT 格式
↓
类初始化和方法调用 ← Hook 点 3: ArtMethod::Invoke
↓
原始代码执行

````

* *可能原因**:

1. 壳检测到 Frida 并提前退出
2. Hook 时机太晚，DEX 已经加载完毕
3. 使用了非标准的加载方式

* *解决方案**:

```bash
# 1. 先绕过 Frida 检测
frida -U -f com.target.app -l bypass_frida_detection.js --no-pause

# 等待应用启动后，再运行 dexdump (分两步)
frida -U com.target.app -l frida_dexdump_manual.js

# 2. 尝试更早的拦截点
# 修改 frida-dexdump 源码，在 libc.so fork() 之前就注入

# 3. 使用内存扫描作为兜底方案
frida -U com.target.app -l unpacker_memscan.js

````

1. Dump 的时机不对，DEX 还未完全解密
2. DEX 文件被截断
3. 内存中的 DEX 已被修改 (如方法抽取)

- **解决方案\*\***:

```bash
# 1. 检查 DEX 文件头
xxd dumped.dex | head -n 5
# 前 4 字节必须是: 64 65 78 0a (dex\n)
# 后 4 字节是版本号: 30 33 35 00 (035) 或 30 33 38 00 (038)

# 2. 验证文件大小
# 偏移 32 字节处记录文件大小
dd if=dumped.dex bs=1 skip=32 count=4 | xxd
# 与实际文件大小对比

# 3. 尝试修复工具
dex-repair dumped.dex -o fixed.dex

# 4. 如果是方法抽取壳，需要用 FART 补全方法体

```

1. ArtMethod 结构偏移错误 (Android 版本不匹配)
2. 读取了无效的内存地址
3. Hook 符号错误

- **解决方案\*\***:

```javascript
// 1. 添加异常保护
Interceptor.attach(artMethodInvokeAddr, {
  onEnter: function (args) {
    try {
      var artMethod = args[0];
      // ... 你的代码
    } catch (e) {
      console.log("[-] 捕获异常: " + e);
      // 不要重新抛出，避免崩溃
    }
  },
});

// 2. 根据 Android 版本动态调整偏移
var androidVersion = Java.androidVersion;
var codeItemOffset;
if (androidVersion >= 10) {
  codeItemOffset = 16; // Android 10+
} else if (androidVersion >= 8) {
  codeItemOffset = 20; // Android 8-9
} else {
  codeItemOffset = 24; // Android 7
}

// 3. 检查指针有效性
if (codeItemPtr && !codeItemPtr.isNull()) {
  // 尝试读取前先检查是否可读
  try {
    Process.findRangeByAddress(codeItemPtr); // 会抛出异常如果地址无效
    var insnsSize = codeItemPtr.add(12).readU32();
    // ...
  } catch (e) {
    console.log("[-] 无效地址: " + codeItemPtr);
  }
}
```

- **解决方案\*\***:

```bash
# 1. 使用 FART 技术 (见第 3 步方法 C)
# 必须触发所有关键方法调用才能完整导出

# 2. 手动触发方法调用
# 写一个测试脚本，遍历所有类的所有方法并调用

# 3. 使用专用工具
# FUPK3、Youpk 等工具已内置方法主动调用逻辑

```

Java.enumerateLoadedClasses({
onMatch: function(className) {
if (className.indexOf("com.target.app") !== -1) {
try {
var clazz = Java.use(className);
var methods = clazz.class.getDeclaredMethods();

methods.forEach(function(method) {
try {
// 尝试调用静态方法 (传空参数)
console.log("[+] 尝试调用: " + method.getName());
method.invoke(null, []);
} catch (e) {
// 忽略调用失败
}
});
} catch (e) {}
}
},
onComplete: function() {
console.log("[+] 方法触发完成");
}
});

});

````

| 项目 | 说明 |
|------|------|
| [Recipe | 绕过 App 对 Frida 的检测](../Anti-Detection/frida_anti_debugging.md) - 脱壳前通常需要先过反调试 |
| [Recipe | 抓包分析 Android 应用的网络流量](../Network/network_sniffing.md) - 脱壳后抓包分析加密逻辑 |
| [Recipe | SO 混淆与反混淆](./so_obfuscation_deobfuscation.md) - Native 层加固的处理 |


## # 工具深入
- [Frida 内部原理](../../02-Tools/Dynamic/frida_internals.md) - 理解 Frida Hook 机制
- [Unidbg 使用指南](../../02-Tools/Dynamic/unidbg_guide.md) - 仿真执行 Native 解密函数

## # 案例分析
- [案例: 某音乐 App 的加固分析](../../03-Case-Studies/case_music_apps.md)

## # 参考资料
- [DEX 文件格式详解](../../04-Reference/Foundations/dex_format.md)
- [ART 运行时机制](../../04-Reference/Foundations/art_runtime.md)

- --

## 快速参考

## # 加固检测速查表

| 检测项 | 命令 | 可疑特征 |
|--------|------|----------|
| **Application 入口** | `unzip -p app.apk AndroidManifest.xml \| grep android:name` | `StubShell`, `ApplicationWrapper`, `StubApplication` |
| **DEX 文件大小** | `unzip -l app.apk \| grep classes.dex` | < 100 KB (复杂应用) |
| **加密数据文件** | `unzip -l app.apk \| grep -E "\.dat\|\.bin"` | `assets/` 下的 .dat/.bin 文件 |
| **可疑 SO 库** | `unzip -l app.apk \| grep "lib/.*\.so"` | `libexec.so`, `libvmp.so`, `libprotect.so` |
| **使用 PKid** | `java -jar ApkToolPlus.jar -pkid app.apk` | 直接输出加固厂商 |

## # 常用脱壳命令

```bash
# 1. 使用 frida-dexdump (推荐)
python3 -m frida_dexdump -U -f com.target.app -o ./output

# 2. 手写脚本 (Spawn 模式)
frida -U -f com.target.app -l unpacker.js --no-pause

# 3. 内存扫描
frida -U com.target.app -l memscan.js

# 4. 拉取导出文件
adb pull /data/data/com.target.app/ ./dumped/

# 5. 验证 DEX 文件
xxd dumped.dex | head -n 2 # 检查 magic number
jadx dumped.dex # 尝试反编译

````

| **frida-dexdump** | 自动化 DEX dumper | [GitHub](https://github.com/hluwa/frida-dexdump) |
| **FUPK3** | 针对特定壳的脱壳机 | [GitHub](https://github.com/F8LEFT/FUPK3) |
| **Youpk** | 较新的脱壳工具 | [GitHub](https://github.com/Youlor/Youpk) |
| **PKid** | 加固识别工具 | [GitHub](https://github.com/rover12421/ApkToolPlus) |
| **dex-repair** | DEX 文件修复工具 | [GitHub](https://github.com/F8LEFT/dex-repair) |

---

**💡 提示**: 脱壳是一个需要耐心和经验的过程。如果一种方法不奏效，尝试组合多种技术。记住，**代码运行必解密** - 只要应用能正常运行,理论上就能脱壳。

````



<!-- 02-Tools/Cheatsheets/adb_cheatsheet.md -->

# 常用 ADB 命令大全

ADB (Android Debug Bridge) 是一个功能强大的命令行工具，可让您与模拟器实例或连接的 Android 设备进行通信。

- --

## 目录
- [常用 ADB 命令大全](#常用-adb-命令大全)
- [目录](#目录)
- [设备管理](#设备管理)

- [文件管理](#文件管理)

- [应用管理](#应用管理)

- [网络](#网络)

- [系统与调试](#系统与调试)

- [Logcat 日志查看](#logcat-日志查看)

- [高级 Shell 命令](#高级-shell-命令)

- --

### 设备管理

| 命令 | 描述 |
| --- | --- |
| `adb devices -l` | 列出所有连接的设备及其详细信息 |
| `adb reboot` | 重启设备 |
| `adb reboot bootloader` | 重启到引导加载程序 (Bootloader) |
| `adb reboot recovery` | 重启到恢复模式 (Recovery) |
| `adb root` | 以 root 权限重启 adbd 服务 |
| `adb shell getprop ro.product.model` | 获取设备型号 |
| `adb shell getprop ro.build.version.release` | 获取 Android 系统版本 |
| `adb shell wm size` | 获取屏幕分辨率 |
| `adb shell wm density` | 获取屏幕像素密度 (DPI) |

- --

### 文件管理

| 命令 | 描述 |
| --- | --- |
| `adb push <本地路径> <远程路径>` | 将文件或文件夹从电脑推送到设备 |
| `adb pull <远程路径> [本地路径]` | 将文件或文件夹从设备拉取到电脑 |
| `adb shell ls <路径>` | 列出设备指定路径下的文件和文件夹 |
| `adb shell cd <路径>` | 切换设备上的当前目录 |
| `adb shell pwd` | 显示设备上的当前工作目录 |
| `adb shell cp <源路径> <目标路径>` | 在设备上复制文件 |
| `adb shell mv <源路径> <目标路径>` | 在设备上移动或重命名文件 |
| `adb shell rm <文件路径>` | 在设备上删除文件 |
| `adb shell mkdir <路径>` | 在设备上创建新目录 |

- --

### 应用管理

| 命令 | 描述 |
| --- | --- |
| `adb install <apk路径>` | 安装应用 |
| `adb install -r <apk路径>` | 重新安装应用（保留数据） |
| `adb install -g <apk路径>` | 为应用授予所有运行时权限 |
| `adb uninstall <包名>` | 卸载应用 |
| `adb shell pm list packages` | 列出所有已安装的应用包名 |
| `adb shell pm list packages -f` | 列出所有已安装的应用包名及其 APK 路径 |
| `adb shell pm list packages -3` | 列出所有第三方应用包名 |
| `adb shell pm path <包名>` | 获取指定应用的 APK 路径 |
| `adb shell am start -n <包名>/<Activity名>` | 启动一个 Activity |
| `adb shell am force-stop <包名>` | 强制停止应用 |
| `adb shell pm clear <包名>` | 清除应用数据和缓存 |
| `adb shell dumpsys activity | grep mFocusedActivity` | 获取当前前台 Activity |

- --

### 网络

| 命令 | 描述 |
| --- | --- |
| `adb forward tcp:<PC端口> tcp:<设备端口>` | 将电脑端口的请求转发到设备端口 |
| `adb forward --list` | 列出所有端口转发规则 |
| `adb forward --remove-all` | 移除所有端口转发规则 |
| `adb shell netstat` | 查看网络状态（监听的端口、连接等） |
| `adb shell ifconfig` or `adb shell ip addr` | 查看网络接口信息和 IP 地址 |

- --

### 系统与调试

| 命令 | 描述 |
| --- | --- |
| `adb shell ps` | 查看设备上的进程列表 |
| `adb shell top` | 查看实时资源占用情况 |
| `adb shell dumpsys <服务名>` | Dump 指定系统服务的信息 (如 `activity`, `battery`, `wifi`) |
| `adb shell screencap /sdcard/screenshot.png` | 截屏并保存到设备 |
| `adb shell screenrecord /sdcard/demo.mp4` | 录制屏幕（Ctrl+C 停止） |
| `adb bugreport [路径]` | 生成并拉取完整的 bug 报告 |
| `adb jdwp` | 列出设备上可供调试的 Java 进程 ID (JDWP) |

- --

### Logcat 日志查看

| 命令 | 描述 |
| --- | --- |
| `adb logcat` | 实时打印设备日志 |
| `adb logcat -c` | 清除旧的日志缓存 |
| `adb logcat -d` | Dump 当前日志到屏幕并退出 |
| `adb logcat -f /sdcard/log.txt` | 将日志输出到设备上的文件 |
| `adb logcat *:S <标签>:<优先级>` | 按标签和优先级过滤日志 |
| `adb logcat | grep <关键词>` | 在日志中搜索关键词 (区分大小写) |

* *日志优先级:**

* `V` — Verbose (最低)

* `D` — Debug

* `I` — Info

* `W` — Warning

* `E` — Error

* `F` — Fatal

* `S` — Silent (最高)

* *示例:** `adb logcat *:S MyApp:D` 只显示标签为 "MyApp" 且优先级为 Debug 或更高的日志。

- --

### 高级 Shell 命令

| 命令 | 描述 |
| --- | --- |
| `adb shell input text '<文本>'` | 向当前输入框输入文本（不支持中文） |
| `adb shell input keyevent <按键码>` | 发送一个按键事件 (例如 `3`=HOME, `4`=BACK, `26`=POWER) |
| `adb shell input tap <x> <y>` | 模拟在屏幕指定坐标的单击事件 |
| `adb shell input swipe <x1> <y1> <x2> <y2> [时长ms]` | 模拟滑动事件 |
| `adb shell settings get <命名空间> <键>` | 获取系统设置项的值 |
| `adb shell settings put <命名空间> <键> <值>` | 修改系统设置项的值 |
| `adb shell content query --uri <URI>` | 查询 Content Provider 中的数据 |
| `adb shell ime list -s` | 列出可用的输入法 |
| `adb shell ime set <输入法ID>` | 设置默认输入法 |



<!-- 02-Tools/Dynamic/frida_guide.md -->

# Frida 常用命令与脚本 API 大全

Frida 是一个动态代码插桩工具包，它允许您将自己的脚本注入到黑盒进程中。它对于逆向工程、安全研究和应用调试非常有用。

- --

## 目录
- [Frida 常用命令与脚本 API 大全](#frida-常用命令与脚本-api-大全)
- [目录](#目录)
- [Frida 工具集](#frida-工具集)

- [连接与附加模式](#连接与附加模式)

- [JavaScript API (核心)](#javascript-api-核心)
- [Java (Android)](#java-android)

- [Objective-C (iOS)](#objective-c-ios)

- [通用/原生 (Native)](#通用原生-native)
- [常用脚本场景与示例](#常用脚本场景与示例)
- [1. Hook 一个简单方法并打印参数](#1-hook-一个简单方法并打印参数)

- [2. 修改方法返回值](#2-修改方法返回值)

- [3. 查找实例并调用其方法](#3-查找实例并调用其方法)

- [4. Hook 构造函数](#4-hook-构造函数)

- [5. 跟踪原生函数调用 (SSL Pinning 绕过常见目标)](#5-跟踪原生函数调用-ssl-pinning-绕过常见目标)
- [RPC (远程过程调用)](#rpc-远程过程调用)

- --

## # Frida 工具集

这些是在终端中使用的核心 Frida 命令行工具。

| 命令 | 描述 |
| --- | --- |
| `frida --version` | 查看 Frida 版本 |
| `frida-ps -U` | 列出 USB 连接设备上的所有进程 |
| `frida-ps -Ua` | 列出 USB 连接设备上所有正在运行的应用程序 |
| `frida-ps -Uai` | 列出 USB 连接设备上所有已安装的应用程序及其标识符 |
| `frida-trace -U -f <包名> -i "<方法>"` | 跟踪指定方法的调用（附加到新进程）|
| `frida-trace -U -p <PID> -i "<方法>"` | 跟踪指定方法的调用（附加到现有进程）|
| `frida -U -f <包名> -l <脚本.js>` | Spawn 一个新进程并注入脚本 |
| `frida -U -p <PID> -l <脚本.js>` | 附加到现有进程并注入脚本 |
| `frida -U --no-pause -f <包名> -l <脚本.js>` | Spawn 新进程并注入脚本，且不暂停主线程 |

- --

## # 连接与附加模式

Frida 有两种主要的方式来 hook 应用：

* **Spawn (Spawning)**: Frida 启动应用程序并立即暂停主线程，以便您在应用代码执行前注入脚本。这是最常用的模式，特别是对于需要在应用启动早期进行 Hook 的场景。使用 `-f <包名>` 参数。

* **Attach (Attaching)**: Frida 附加到已经在运行的进程上。这对于 hook 那些在应用运行中途才会触发的功能很有用。使用 `-p <PID>` 或应用名称。

- --

## # JavaScript API (核心)

这是 Frida 脚本的核心。所有逻辑都在 JavaScript 脚本中实现。

### Java (android)

这些 API 用于与 Android 的 Java 运行时进行交互。所有 Java 相关代码都必须包裹在 `Java.perform(function() { ... });` 中。

| API/代码片段 | 描述 |
| --- | --- |
| `Java.perform(function() { ... });` | Frida 中与 Java 交互的入口点和作用域 |
| `Java.available` | 检查 Java VM 是否可用 |
| `var MyClass = Java.use('com.example.MyClass');` | 获取一个类的包装器，用于方法 Hook 或创建实例 |
| `MyClass.myMethod.implementation = function(...) { ... }` | 替换（Hook）一个方法的实现 |
| `this.myMethod(...)` | 在 Hook 的实现中调用原始方法 |
| `MyClass.$new()` | 创建一个类的新实例 |
| `Java.choose('com.example.MyClass', { onMatch: ..., onComplete: ... })` | 查找堆上特定类的所有活动实例 |
| `Java.cast(obj, MyClass)` | 将一个对象转换为特定的类类型 |
| `Java.backtrace(this.context, true)` | 获取当前线程的 Java 调用堆栈 |
| `send(data)` | 从脚本向 Python/Node.js 工具发送消息 |
| `recv(callback)` | 从 Python/Node.js 工具接收消息 |

### Objective-C (iOS)

这些 API 用于与 iOS 的 Objective-C 运行时进行交互。

| API/代码片段 | 描述 |
| --- | --- |
| `ObjC.classes.MyClass` | 获取一个类的引用 |
| `Interceptor.attach(ObjC.classes.MyClass['- myMethod'], { ... })` | 附加到方法的实现 (Native Interceptor) |
| `ObjC.choose(ObjC.classes.MyClass, { ... })` | 查找特定类的所有活动实例 |
| `ObjC.available` | 检查 Objective-C 运行时是否可用 |

### 通用/原生 (Native)

这些 API 用于与原生代码（C/C++）进行交互，跨平台通用。

| API/代码片段 | 描述 |
| --- | --- |
| `Interceptor.attach(ptr("..."), { onEnter: ..., onLeave: ... })` | 拦截指定地址的原生函数调用 |
| `Module.findExportByName("libname.so", "function_name")` | 按名称查找模块（库）的导出函数地址 |
| `Module.findBaseAddress("libname.so")` | 获取模块加载的基地址 |
| `Memory.readByteArray(address, size)` | 从指定地址读取字节数组 |
| `Memory.writeByteArray(address, bytes)` | 向指定地址写入字节数组 |
| `NativeFunction(address, returnType, argTypes)` | 创建一个可调用的原生函数对象 |
| `ptr("0x...")` | 创建一个原生指针 |
| `Thread.backtrace(this.context, Backtracer.ACCURATE)` | 获取当前线程的原生调用堆栈 |

### JNI (Java Native Interface)

JNI 是 Android 逆向中的重要组成部分，Frida 提供了强大的 JNI Hook 能力。

| API/代码片段 | 描述 |
| --- | --- |
| `Module.findExportByName("lib.so", "Java_com_pkg_Class_method")` | 查找 JNI 函数地址 |
| `Java.vm.getEnv()` | 获取当前线程的 JNIEnv 指针 |
| `Java.vm.tryGetEnv()` | 尝试获取 JNIEnv（不会抛异常） |
| `Java.vm.perform(callback)` | 在 Java 虚拟机线程中执行回调 |

* *JNI Hook 示例**：

```javascript
// Hook JNI Function
var jni_func = Module.findExportByName("libnative.so",
"Java_com_example_app_Crypto_encrypt");

if (jni_func) {
Interceptor.attach(jni_func, {
onEnter: function(args) {
console.log("[JNI Hook] encrypt() called");

// args[0] = JNIEnv*
// args[1] = jclass/jobject
// args[2] = first Java parameter

// Read jstring parameter
if (args[2]) {
var env = Java.vm.getEnv();
var jstr = args[2];
var cstr = env.getStringUtfChars(jstr, null);
console.log("Input: " + cstr.readCString());
env.releaseStringUtfChars(jstr, cstr);
}
},
onLeave: function(retval) {
// Read returned jstring
if (retval && !retval.isNull()) {
var env = Java.vm.getEnv();
var cstr = env.getStringUtfChars(retval, null);
console.log("Output: " + cstr.readCString());
env.releaseStringUtfChars(retval, cstr);
}
}
});
}

// Also hook the native method call from Java layer
Java.perform(function() {
var Crypto = Java.use("com.example.app.Crypto");

Crypto.encrypt.implementation = function(input) {
console.log("[Java Hook] encrypt called with: " + input);
var result = this.encrypt(input);
console.log("[Java Hook] encrypt returned: " + result);
return result;
};
});

````

var module = Process.getModuleByName(moduleName);
var exports = module.enumerateExports();

console.log("[JNI Enumeration] " + moduleName);
exports.forEach(function(exp) {
if (exp.name.startsWith("Java\_")) {
console.log(" " + exp.name + " @ " + exp.address);
}
});
}

// Usage example
enumerateJNIFunctions("libnative.so");

```
Java.perform(function() {
var MyClass = Java.use('com.example.SecretClass');

MyClass.secretMethod.implementation = function(arg1, arg2) {
console.log('secretMethod called with:', arg1, arg2);

// Call original method and get return value
var retval = this.secretMethod(arg1, arg2);
console.log('Original return value:', retval);

return retval; // Return original value
};
});

```

PremiumUtils.isUserPremium.implementation = function() {
console.log('Bypassing isUserPremium check...');
return true; // Always return true to bypass VIP check
};
});

```
onMatch: function(instance) {
console.log('Found UserManager instance:', instance);
console.log('User ID:', instance.getUserId());
},
onComplete: function() {
console.log('Search complete.');
}
});
});

```

User.$init.implementation = function(name, age) {
console.log('User object created with name:', name, 'and age:', age);

// Call original constructor
this.$init(name, age);
};
});

```
// args[0] is the SSL context
// args[1] is the buffer
// args[2] is the size
console.log("Intercepted SSL_write, size:", args[2].toInt32());
// You can use hexdump(args[1]) to view the data
},
onLeave: function(retval) {
// retval is the original return value
console.log("SSL_write returned:", retval.toInt32());
}
});

```

```javascript
function getSecretValueFromApp() {
  var secret = "";
  Java.perform(function () {
    // Assume there's a method to get the secret value
    var Utils = Java.use("com.example.Utils");
    secret = Utils.getSecret();
  });
  return secret;
}

// Export function
rpc.exports.getsecret = getSecretValueFromApp;
```

# ... Connect to device and attach to process ...

# script = session.create_script(js_code)

# ...

# script.load()

# Call the exported function from the script

secret = script.exports.getsecret()
print("Secret from app:", secret)

```

```

<!-- 02-Tools/Dynamic/frida_internals.md -->

# Frida 核心模块与实现原理

Frida 是一个功能强大的动态插桩框架，但要充分利用它，理解其内部工作原理至关重要。本指南将深入探讨构成 Frida 的几个核心模块、它们的作用以及它们是如何协同工作的。

---

## 目录

- [Frida 核心模块与实现原理](#frida-核心模块与实现原理)
- [目录](#目录)
- [Frida 的架构概览](#frida-的架构概览)

- [核心组件详解](#核心组件详解)
- [**Frida-Server**: 设备端的守护进程](#frida-server-设备端的守护进程)

- [**Frida-Core**: 注入目标进程的核心引擎](#frida-core-注入目标进程的核心引擎)

- [**Frida-Gum**: 实现 Hook 的魔法棒](#frida-gum-实现-hook-的魔法棒)
- [`Interceptor`: 函数拦截器](#interceptor-函数拦截器)

- [`Stalker`: 指令级跟踪器](#stalker-指令级跟踪器)
- [**JavaScript (V8) 运行时**: 脚本的执行环境](#javascript-v8-运行时-脚本的执行环境)

- [**语言绑定 (Bindings)**: 你的控制台](#语言绑定-bindings-你的控制台)
- [工作流程串讲](#工作流程串讲)

---

### Frida 的 architecture 概览

Frida 采用的是一种**客户端-服务器 (Client-Server)** 架构。

!!! question "思考：为什么需要这样复杂的架构？"
Frida 为什么不设计成一个简单的工具，而要分成客户端、服务器、Agent 三层？

- **跨平台的必然选择\*\***：

* **隔离性**：你的分析脚本（Python）运行在 PC，不会影响目标设备的性能
* **安全性**：Server 只负责进程管理和注入，真正的"危险操作"在隔离的进程内
* **灵活性**：同一个 Server 可以同时为多个客户端服务，支持团队协作
* **跨语言**：PC 端用 Python/Node.js 编写自动化脚本，目标进程内用 JavaScript 操作内存，各取所长

这种架构的本质是：**把"控制"和"执行"分离**，就像遥控无人机——遥控器在你手上，但飞行逻辑在机上。

- **客户端 (Client)**: 运行在你 PC 上的部分。这包括你编写的 Python 或 Node.js 脚本，以及你使用的 Frida 命令行工具 (`frida`, `frida-trace` 等)。

- **服务器 (Server)**: 在目标设备（如 Android 手机）上以后台守护进程模式运行的 `frida-server`。

- **Agent**: 当你附加到一个目标进程时，Frida 会将一个动态库 (`frida-agent.so`) **注入**到该进程的内存空间中。这个 Agent 负责执行你在客户端脚本中定义的逻辑。

![Frida Architecture](https://frida.re/static/images/frida-architecture.png)

- 图片来源: frida.re\*\*

---

### 核心组件详解

#### **Frida-Server**: 设备端的守护进程

`frida-server` 是一个在目标设备上运行的二进制文件。它的主要职责是：

1. **监听连接**: 监听来自你 PC 上 Frida 客户端的 TCP 连接。
2. **进程管理**: 枚举目标设备上正在运行的进程，获取应用信息。
3. **注入 Agent**: 当客户端指定要附加 (attach) 或启动 (spawn) 一个应用时，`frida-server` 负责将 `frida-agent.so` 注入到目标进程中。在 Android 上，它通常通过 `ptrace` 来实现这一点。

#### **Frida-Core**: 注入目标进程的核心引擎

`frida-core` 是 Frida 的核心，它被编译成 `frida-agent.so` 并注入到目标进程。它是一个用 C 语言编写的多平台库，主要负责：

1. **进程内通信**: 建立一个与 `frida-server` 的通信渠道，从而间接地与你的 PC 客户端通信。
2. **加载 JavaScript 引擎**: 它内部嵌入了一个 Google V8 JavaScript 引擎。
3. **暴露原生 API**: 将底层的 `frida-gum` 功能通过 JavaScript API (如 `Interceptor`, `Memory`, `NativePointer`) 暴露给用户脚本。

#### **Frida-Gum**: 实现 Hook 的魔法棒

`frida-gum` 是 `frida-core` 中最具魔力的部分，它是一个跨平台的代码插桩工具包。所有 Hook 和代码跟踪功能都由它提供。

##### `Interceptor`: 函数拦截器

`Interceptor` 是你最常使用的功能，用于 Hook/Trace/替换任意函数。

!!! tip "深入理解：Hook 的本质是什么？"
很多人把 Hook 当成"黑魔法"，但其实原理很朴素：

- **Hook = 劫持程序的执行流\*\***

想象你在高速公路上设置了一个收费站：

1. **原始道路**：函数的正常执行流程
2. **收费站（Trampoline）**：你插入的代码
3. **改道标志（JMP）**：修改函数入口的跳转指令
4. **恢复通行**：执行原始指令后继续

理解了这个本质，你就能：

- 判断哪些 Hook 会相互冲突（都修改同一个函数入口）
- 理解为什么有些反 Hook 检测能发现你（检查函数头的修改）
- 知道如何写更隐蔽的 Hook（inline hook vs. PLT/GOT hook）

* **实现原理**:

1. **动态代码生成**: 当你 `Interceptor.attach` 一个函数时，Frida-Gum 会在内存中动态地生成一小段汇编代码，我们称之为**蹦床 (Trampoline)**。
2. **函数头重写 (Prologue Rewriting)**: Frida-Gum 会修改目标函数入口点（函数头）的几条指令，将其替换为一个**无条件跳转 (`JMP`) 指令**，该指令指向刚刚创建的蹦床。Frida 会非常小心地保存被它覆盖掉的原始指令。
3. **执行流程**:

- 当应用调用目标函数时，它会首先跳转到蹦床。

- 蹦床代码会保存当前的 CPU 上下文（寄存器状态），然后调用你在 JavaScript 中定义的 `onEnter` 回调。

- `onEnter` 执行完毕后，蹦床会执行被它覆盖掉的原始函数指令，然后跳转回原始函数的剩余部分继续执行。

- 当原始函数执行完毕后，控制权返回给蹦床，蹦床再调用你的 `onLeave` 回调。

- 最后，蹦床恢复之前保存的 CPU 上下文，并将返回值传递给原始的调用者。

##### `Stalker`: 指令级跟踪器

`Stalker` 是 Frida 的代码跟踪引擎，功能极其强大但使用也更复杂。它可以用来记录一个线程执行过的**每一条**汇编指令。

- **实现原理 (基于动态重新编译)**:

1. **基本块 (Basic Block)**: Stalker 将代码分解为“基本块”。一个基本块是一系列连续的指令，只有一个入口点和一个出口点（通常是跳转或返回指令）。
2. **代码拷贝与插桩**: 当一个线程将要执行某个基本块时，Stalker 会：
   a. 将这个基本块的所有指令**拷贝**到一块新的内存区域。
   b. 在这份拷贝中**插入**你的分析代码（例如，记录指令地址、寄存器值的代码）。
   c. 执行这份被插桩后的代码副本。
3. **代码缓存 (Code Cache)**: Stalker 会缓存这些被修改过的基本块。下次再执行到同一个基本块时，可以直接使用缓存中的版本，极大地提高了性能。
4. **链接 (Chaining)**: Stalker 会修改每个插桩后基本块的末尾，使其跳转到下一个即将执行的原始基本块对应的“插桩版本”，从而形成一个完整的跟踪链。

简而言之，`Stalker` 通过创建和执行原始代码的“带监控的副本”来实现无死角的指令级跟踪。

#### **JavaScript (V8) 运行时**: 脚本的执行环境

为什么我们用 JavaScript 写 Hook 逻辑？因为 `frida-agent.so` 在注入目标进程后，会初始化一个 V8 引擎实例。你的 JS 脚本被完整地加载到这个 V8 引擎中执行。

这带来了巨大的优势：

- **高级语言的便利性**: 你可以在目标进程的地址空间内，用 JavaScript 的便利性来操作内存、调用函数。

- **JIT 编译**: V8 的即时编译 (JIT) 特性使得你的 JS 脚本能以接近原生的速度运行，性能远超解释执行。

- **强大的生态**: 可以利用现有的 JS 库。

#### **语言绑定 (Bindings)**: 你的控制台

`frida-python`, `frida-node` 等库是你的“控制端”。它们负责：

- **连接 Server**: 与设备上的 `frida-server` 建立通信。

- **发送指令**: 将你的指令（如“附加到 PID 1234”）发送给 `frida-server`。

- **加载脚本**: 将你的 `.js` 脚本文件内容发送给 `frida-agent.so` 里的 V8 引擎去执行。

- **双向通信 (RPC)**: 建立一个双向的 RPC 通道。这使得你在 JS 中调用 `send()` 的数据能被 Python 的 `on_message` 回调接收，反之亦然。

---

### 工作流程串讲

当你执行 `frida -U -f com.example.app -l script.js` 时，发生了什么？

1. **[PC]** `frida` (Python 客户端) 解析命令。
2. **[PC -> Phone]** 客户端通过 USB 连接到手机上的 `frida-server`。
3. **[PC -> Phone]** 客户端向 `frida-server` 发送指令：“请以 `spawn` 模式启动 `com.example.app`”。
4. **[Phone]** `frida-server` 找到 `com.example.app` 并启动它，但使其处于**暂停**状态。
5. **[Phone]** `frida-server` 将 `frida-agent.so` 注入到这个新创建的应用进程中。
6. **[Phone]** `frida-agent.so` 在进程内初始化，启动 V8 引擎，并建立与 `frida-server` 的内部通信。
7. **[PC -> Phone]** 客户端读取 `script.js` 的内容，并通过 `frida-server` 将其发送给 `frida-agent.so`。
8. **[Phone]** `frida-agent.so` 中的 V8 引擎执行 `script.js` 的代码（例如，`Interceptor.attach(...)`）。
9. **[PC -> Phone]** 客户端发送“恢复进程”的指令。
10. **[Phone]** 应用进程从暂停状态中恢复，开始正常执行。当它调用被 Hook 的函数时，你在 `script.js` 中定义的逻辑就会被触发。
11. **[双向]** 脚本中的 `send()` 消息会通过 `agent -> server -> client` 的路径回到你的 PC 终端上显示。

<!-- 02-Tools/Dynamic/unidbg_guide.md -->

# Unidbg 模拟执行框架指南

Unidbg 是一个基于 Java 开发的、开源的、功能强大的 Android/iOS 原生库 (`.so`/`.dylib`) 模拟执行框架。它能够在 PC (Windows/Linux/macOS) 上模拟一个完整的 ARM 执行环境，使得你可以像调用本地 Java 方法一样直接调用和调试原生库中的函数。这对于分析高度混淆、包含大量环境依赖和反调试机制的原生算法来说，是一个革命性的工具。

---

## 目录

- [Unidbg 模拟执行框架指南](#unidbg-模拟执行框架指南)
- [目录](#目录)
- [核心思想与应用场景](#核心思想与应用场景)

- [Unidbg vs. Frida](#unidbg-vs-frida)

- [环境搭建](#环境搭建)

- [基本使用流程](#基本使用流程)

- [核心 API 与概念](#核心-api-与概念)

- [实战技巧](#实战技巧)

---

## # 核心思想与应用场景

Unidbg 的核心思想是**"欺骗"**。它通过以下方式让 `.so` 文件认为自己正运行在一个真实的 Android 设备上：

- **模拟文件系统**: 创建一个虚拟的文件系统，你可以将应用的数据、配置文件等放入其中。

- **模拟内存空间**: 加载 `.so` 文件及其依赖的系统库 (如 `libc.so`, `libdl.so`) 到模拟的内存空间中。

- **模拟 JNI 环境**: 实现了大部分 JNI 函数，当 `.so` 文件试图通过 JNI 调用 Java 层代码时，Unidbg 会拦截并可以返回你指定的值。

- **Hook 系统调用 (SVC)**: 拦截底层的系统调用，返回预设的结果。

- **主要应用场景\*\***:
- **算法复现 (一把梭)**: 直接调用目标加密/解密函数，输入参数并获取返回值，无需费力去逆向算法本身。

- **绕过环境检测**: 目标函数可能包含对 Root、模拟器、设备 ID 等的检测。Unidbg 可以轻松 Hook 这些检测点，让它们全部失效。

- **绕过反调试**: `ptrace` 等反调试手段在 Unidbg 的模拟环境中天然无效。

- **批量计算/爆破**: 编写脚本，批量调用目标函数，用于参数的爆破或生成大量签名。

- **主动调用非导出函数**: 与 Frida 不同，只要知道函数偏移，就可以直接调用任何函数，无论它是否被导出。

---

## # Unidbg vs. Frida

| 特性         | Unidbg                                 | Frida                                        |
| :----------- | :------------------------------------- | :------------------------------------------- |
| **执行环境** | **PC 端 (模拟执行)**                   | **移动设备端 (真机/模拟器)**                 |
| **工作模式** | 将 `.so` 当作一个"黑盒"库来调用        | 侵入正在运行的应用进程进行 Hook              |
| **依赖**     | 仅需要 `.so` 文件及其依赖的库          | 需要一个完整的、能运行的 APK                 |
| **反调试**   | **天然免疫**                           | 需要编写脚本来对抗反调试                     |
| **环境依赖** | 需要手动模拟或 Hook                    | 运行在真实环境中，无需模拟                   |
| **性能**     | 较低 (因为是全模拟)                    | 较高 (代码在设备上原生运行)                  |
| **适用性**   | 适合纯算法分析，不涉及 UI 和复杂业务流 | 适合分析与 Android 系统、UI 强相关的业务逻辑 |

---

## # 环境搭建

1. **JDK**: 确保已安装 JDK 8 或更高版本。
2. **Maven**: 用于项目构建和依赖管理。
3. **IDE**: 推荐使用 IntelliJ IDEA。
4. **下载 Unidbg**: 从其 GitHub Release 页面下载最新的发行版 `unidbg-dist.zip`，或直接使用 Maven 依赖。
5. **创建 Maven 项目**: 在 IDE 中创建一个新的 Maven 项目，并在 `pom.xml` 中添加 Unidbg 的依赖：
   ```xml
   <dependency>
   <groupId>com.github.unidbg</groupId>
   <artifactId>unidbg-android</artifactId>
   <version>0.9.7</version> <!-- Use latest version -->
   </dependency>
   ```

````

## # 基本使用流程

以下是一个调用 `.so` 中简单函数的典型代码结构：

```java
import com.github.unidbg.AndroidEmulator;
import com.github.unidbg.Module;
import com.github.unidbg.linux.android.AndroidEmulatorBuilder;
import com.github.unidbg.linux.android.AndroidResolver;
import com.github.unidbg.linux.android.dvm.*;
import com.github.unidbg.memory.Memory;

import java.io.File;

public class MyTest extends DvmObject<String> {

private final AndroidEmulator emulator;
private final Module module;
private final VM vm;

public MyTest() {
// 1. Create emulator instance
emulator = AndroidEmulatorBuilder.for32Bit().build();
final Memory memory = emulator.getMemory();
// 2. Set system library resolver
memory.setLibraryResolver(new AndroidResolver(23)); // API 23

// 3. Create virtual machine instance (DVM)
vm = emulator.createDalvikVM(new File("target/classes/apk/app-debug.apk")); // APK can be provided for automatic extraction
vm.setVerbose(true); // Print detailed logs

// 4. Load target .so
DalvikModule dm = vm.loadLibrary(new File("target/classes/so/libnative-lib.so"), true);
module = dm.getModule();

// 5. Call JNI_OnLoad (optional but recommended)
dm.callJNI_OnLoad(emulator);
}

public void callNativeFunc() {
// 6. Call target function
Number result = module.callFunction(emulator, 0x1234, "hello unidbg")[0]; // 0x1234 is the function offset
System.out.println("Result: " + result.intValue());
}

public static void main(String[] args) {
MyTest test = new MyTest();
test.callNativeFunc();
test.emulator.close();
}
}

````

- **`VM`**: 虚拟机，可以是 `DalvikVM` (DVM) 或 `ART`。负责管理 Java 对象 (`DvmObject`) 和 JNI 调用。

- **`Module`**: 代表一个已加载到内存中的 `.so` 模块。
- `callFunction(emulator, address, args...)`: **核心方法**，通过绝对地址或偏移调用函数。

- `findSymbolByName("...")`: 按名称查找导出函数。
- **`DvmObject`**: Java 对象的代理。Unidbg 使用它来向 native 函数传递字符串、字节数组等。

- **`AbstractJni`**: 如果 `.so` 中有复杂的 JNI 回调，你需要继承 `AbstractJni` 并重写对应的方法，以模拟 Java 层的行为。

- **Hooking**: Unidbg 使用 `com.github.unidbg.hook.Hooker` 接口和 `TraceHook` 等工具来提供类似 Frida 的 Hooking 能力，可以监控指令、内存读写等。

---

## # 实战技巧

- **补环境**: 如果 `.so` 依赖特定的设备信息或文件，你需要：
- 在虚拟文件系统中创建对应的文件和内容。

- Hook `open`, `read`, `access` 等 libc 函数，返回预期的结果。

- Hook JNI 调用，如 `getSystemService`，返回一个模拟的 `TelephonyManager` 对象。
- **定位函数地址**: 函数地址是 `基地址 (module.base) + 偏移`。偏移可以从 IDA/Ghidra 中获得。

- **设置断点**: 使用 `emulator.attach().addBreakPoint(address, ...)` 可以在指定地址设置断点，进行调试。

- **日志分析**: `vm.setVerbose(true)` 会打印非常详细的 JNI 调用和 SVC 日志，这是解决环境问题的关键。

- **参考官方测试用例**: Unidbg 项目的 `unidbg-android/src/test/java` 目录下有大量针对主流 App 的测试用例，是学习 Unidbg 的最佳资料。

````



<!-- 02-Tools/Dynamic/unidbg_internals.md -->

# Unidbg 实现原理剖析

Unidbg 是一个强大的 Android 原生库 (`.so`) 模拟执行框架。它允许你在没有 Android 真机或模拟器的情况下，直接在 PC (macOS, Windows, Linux) 上运行和调试 JNI 函数。理解其工作原理，可以帮助我们更高效地解决复杂的加密算法逆向、协议分析等问题。
___
## 目录
- [Unidbg 实现原理剖析](#unidbg-实现原理剖析)
- [目录](#目录)
- [核心思想：在 PC 上模拟一个 Android 执行环境](#核心思想在-pc-上模拟一个-android-执行环境)

- [关键组件详解](#关键组件详解)
- [**Unicorn Engine**: CPU 模拟器](#unicorn-engine-cpu-模拟器)

- [**内存管理与映射 (Memory Management)**](#内存管理与映射-memory-management)

- [**动态库加载器 (Dynamic Linker)**](#动态库加载器-dynamic-linker)

- [**系统调用处理 (Syscall Handler)**](#系统调用处理-syscall-handler)

- [**JNI 函数模拟 (JNI Emulation)**](#jni-函数模拟-jni-emulation)
- [工作流程：`unidbg` 是如何运行一个 `.so` 的？](#工作流程unidbg-是如何运行一个-so-的)

- [Unidbg 的优势与局限](#unidbg-的优势与局限)
___
### 核心思想：在 PC 上模拟一个 android 执行环境

`.so` 文件是为特定 CPU 架构（如 ARM）和操作系统（如 Android）编译的。它不能直接在你的 x86 架构的 PC 上运行。

Unidbg 的核心思想就是：**用纯 Java 在 PC 上构建一个虚拟的、高度仿真的 Android 用户态 (User-Mode) 环境**。它不是一个完整的操作系统模拟器，而是专注于模拟一个 Android *进程* 所需的一切，让 `.so` 文件“感觉”自己正运行在一个真实的 Android 设备里。
___
### 关键组件详解

#### **Unicorn Engine**: CPU 模拟器

Unicorn 是 Unidbg 的基石。它是一个基于 QEMU 的轻量级、多平台、多架构的 CPU 模拟器库。

* **作用**: 负责**逐条解释和执行** `.so` 文件中的 ARM 或 AArch64 (ARM64) 汇编指令。

* **原理**: 当 Unidbg 加载 `.so` 的代码段到虚拟内存后，它会设置一个程序计数器 (PC) 指向要执行的函数地址，然后命令 Unicorn 从该地址开始执行。Unicorn 会读取指令、解码、模拟寄存器和内存的读写，并更新 CPU 状态，就像一个真实的 ARM 芯片一样。

#### **内存管理与映射 (Memory Management)**

Unidbg 内部实现了一套完整的内存管理系统，用于模拟一个进程的虚拟地址空间。

* **作用**:
1. 为加载的 `.so` 文件分配虚拟内存（代码段、数据段、BSS段等）。
2. 管理函数的栈空间 (Stack)，用于存储局部变量和返回地址。
3. 处理 `malloc`, `free` 等内存分配请求。

* **原理**: 它通过 Java 的数据结构（如 `byte[]` 或 `ByteBuffer`）来表示内存块，并通过一个映射表（`Map<Long, MemoryBlock>`）来管理虚拟地址和这些实际内存块之间的关系。当 Unicorn 需要读写某个虚拟地址时，Unidbg 会查询这个表，找到对应的 Java 内存块并进行操作。

#### **动态库加载器 (Dynamic Linker)**

Android 应用的 `.so` 文件通常会依赖其他的系统库，如 `libc.so` (标准 C 库), `liblog.so` (日志库), `libz.so` (压缩库) 等。

* **作用**: Unidbg 内置了一个简易的 `linker`，负责解析 `.so` 文件的依赖项，并加载这些依赖库。

* **原理**:
1. **解析 ELF**: Unidbg 会读取 `.so` 文件的 ELF 头，找到其 `.dynamic` section，这里记录了所有依赖库的名称。
2. **加载依赖**: Unidbg 会在预设的路径中查找这些依赖库（它自带了一些核心的 Android 系统库），然后像加载主 `.so` 一样，将它们也加载到虚拟内存中。
3. **符号重定位 (Relocation)**: 加载器最重要的工作是处理**重定位**。如果 A.so 调用了 B.so 中的函数 `foo`，A.so 中只存了一个对 `foo` 的“符号引用”。加载器需要在 B.so 中找到 `foo` 的实际地址，然后将这个地址填回到 A.so 的调用指令中。这个过程是 `.so` 文件能够跨库调用的关键。

#### **系统调用处理 (Syscall Handler)**

当 `.so` 文件需要执行一些需要操作系统内核参与的操作时（如读写文件、网络通信），它会发起一个**系统调用 (syscall)**，这通过 `SVC` 或 `SWI` 指令实现。

* **作用**: 拦截并处理 `.so` 发出的所有系统调用。

* **原理**: Unicorn 引擎在执行 `SVC` 指令时会产生一个“中断”，并将控制权交还给 Unidbg。Unidbg 会检查特定的寄存器（如 `r7`）来获取系统调用的编号，然后在其 `SyscallHandler` 中找到对应的 Java 实现并执行。
* 例如，如果 `.so` 尝试打开一个文件，Unidbg 会拦截这个系统调用，并用 Java 的 `FileInputStream` 在 PC 上实际打开一个文件，然后将文件描述符返回给 `.so`。

#### **JNI 函数模拟 (JNI Emulation)**

这是 Unidbg 最核心的功能之一。JNI (Java Native Interface) 是 `.so` 文件与 Java 层代码交互的桥梁。

* **作用**: 模拟 Android ART/Dalvik 虚拟机提供的所有 JNI 函数，如 `FindClass`, `GetMethodID`, `CallObjectMethod` 等。

* **原理**: Unidbg 在其虚拟环境中预先注册了所有 JNI 函数的 Java 实现。
* 当 `.so` 调用 `FindClass("java/lang/String")` 时，Unidbg 的 JNI 模块会接管这个调用，并返回一个代表 `java.lang.String` 类的虚拟对象（一个 Java `DvmClass` 实例）。

* 当 `.so` 调用 `CallObjectMethod` 时，Unidbg 会根据传入的参数，实际地在 PC 端的 JVM 中执行对应 Java 对象的相应方法，然后将结果返回给 `.so`。

通过这种方式，Unidbg 巧妙地将 `.so` 对 Android 虚拟机的调用“嫁接”到了 PC 端的 JVM 上。
___
### 工作流程：`unidbg` 是如何运行一个 `.so` 的？

1. **创建模拟器实例**: `AndroidARMEmulator emulator = new AndroidARMEmulator("com.example.app");`
2. **内存初始化**: `Memory memory = emulator.getMemory();` Unidbg 初始化内存管理器和 Unicorn 引擎。
3. **加载动态库**: `Module module = emulator.loadLibrary(new File("libnative-lib.so"));`
a. Unidbg 的 `linker` 解析 `libnative-lib.so` 的 ELF 结构。
b. 根据 `PT_LOAD` 段，将 `.so` 的内容映射到虚拟内存。
c. 解析其依赖库（如 `libc.so`），递归加载它们。
d. 进行符号重定位，修复函数调用地址。
4. **调用 JNI 函数**: `module.callJNI_OnLoad(emulator);` 或 `DvmObject<?> obj = module.callJniMethod(...);`
a. Unidbg 找到目标 JNI 函数在虚拟内存中的地址。
b. 设置函数参数，主要是将 `JNIEnv` 和 `jobject` 等 JNI 对象作为指针（虚拟地址）传入。
c. 启动 Unicorn 引擎，从目标函数地址开始执行 ARM 汇编指令。
5. **执行与交互**:
* 汇编指令由 Unicorn 解释执行。

* 遇到系统调用，Unicorn 中断，由 Unidbg 的 `SyscallHandler` 处理。

* 遇到调用 JNI 函数，由 Unidbg 的 JNI 模拟层处理，可能会在 PC 的 JVM 上执行真实的 Java 代码。
6. **返回结果**: 函数执行完毕后，从模拟的寄存器（如 `r0`）或栈上获取返回值，并转换为 Java 对象。
___
### Unidbg 的优势与局限

* **优势**:
* **摆脱环境限制**: 无需真机或模拟器，无 root 权限要求。

* **高可控性**: 可以完全控制程序的执行流程，任意修改内存、寄存器。

* **自动化与集成**: 易于与 Java/Python 项目集成，进行大规模的自动化测试和分析。

* **反反调试**: 由于没有实际的调试器进程 (`ptrace`)，可以绕过大多数基于 `ptrace` 的反调试检测。

* **局限**:
* **环境不完整**: 并非 100% 完整的 Android 环境。对于强依赖特定系统行为、硬件特性或大量 UI 操作的 `.so` 文件，模拟可能会失败。

* **性能开销**: 毕竟是逐条指令模拟，性能远低于原生执行。

* **系统调用和 JNI 覆盖**: 如果 `.so` 用到了 Unidbg 尚未实现的系统调用或 JNI 函数，执行会中断，需要手动补充实现。



<!-- 02-Tools/Dynamic/xposed_guide.md -->

# Xposed 框架入门

Xposed 是一个在 Android 平台上广受欢迎的动态代码 Hook 框架。与 Frida 主要用于实时、临时的分析不同，Xposed 旨在对系统和应用进行**永久性**的修改。它通过替换一个核心系统进程 (`app_process`)，在应用启动时加载自定义模块，从而实现对任意方法的高效 Hook。
___
## 目录
- [Xposed 框架入门](#xposed-框架入门)
- [目录](#目录)
- [核心原理](#核心原理)

- [Xposed vs. Frida](#xposed-vs-frida)

- [环境搭建 (以 LSPosed 为例)](#环境搭建-以-lsposed-为例)

- [开发第一个 Xposed 模块](#开发第一个-xposed-模块)
- [1. 项目结构](#1-项目结构)

- [2. 实现 Hook 逻辑](#2-实现-hook-逻辑)

- [3. 声明模块入口](#3-声明模块入口)

- [4. 激活模块](#4-激活模块)
- [核心 API 详解](#核心-api-详解)
- [`IXposedHookLoadPackage`](#ixposedhookloadpackage)

- [`XposedHelpers`](#xposedhelpers)

- [`XC_MethodHook`](#xc_methodhook)
- [常见应用场景](#常见应用场景)
___
### 核心原理

Xposed 的工作基础是它能够在 Android 系统启动的核心阶段介入，并将自己的代码注入到每一个应用程序进程中。

1. **Zygote 注入**: Xposed 通过替换系统原生的 `/system/bin/app_process` 可执行文件，实现了对 Zygote 进程（所有 App 进程的父进程）的控制。当 Zygote 启动时，会加载 Xposed 的核心 Jar 包（Xposed Bridge）。
2. **方法 Hook**: 当模块需要 Hook 一个方法时，Xposed 会在运行时深入虚拟机（ART）内部，直接修改该方法在内存中的数据结构。它将目标方法"伪装"成一个 Native 方法，并将其执行入口指向 Xposed 的一个通用桥接函数。
3. **执行流重定向**: 当 App 调用被 Hook 的方法时，执行流会先进入 Xposed 的桥接函数，在这里 Xposed 依次调用所有模块的 `beforeHookedMethod`，然后调用原方法，最后再调用所有模块的 `afterHookedMethod`，从而实现对方法调用的完全控制。

> 想要更深入地了解其实现细节，请参考 [**Xposed Internals: A Deep Dive**](./xposed_internals.md)。
___
### Xposed vs. Frida

| 特性 | Xposed | Frida |
| :--- | :--- | :--- |
| **核心目标** | **永久性修改**: 对应用或系统功能进行长期、稳定的修改。 | **动态分析**: 用于实时、临时的分析、逆向和快速原型验证。 |
| **运行环境** | 需要 Root，通过刷入框架修改系统，**需要重启**。 | 通常需要 Root，但无需重启，通过 `frida-server` 动态附加。 |
| **开发语言** | **Java**: 模块是标准的 Android APK。 | **JavaScript**: 主要使用 JS 编写脚本，也支持其他语言绑定。 |
| **开发周期** | 较慢：编码 → 编译 APK → 安装 → 激活 → 重启 App/设备 → 测试。 | 极快：编写/修改脚本 → 附加进程 → 立即看到结果。 |
| **稳定性** | 极高。为长期运行设计，一旦激活，随 App 启动自动生效。 | 较低。依赖于 `frida-server` 和附加会话，App 重启后失效。 |
| **适用场景** | UI 定制、功能增强、去广告、隐私控制（如伪造数据）。 | SSL Pinning 绕过、算法逆向、协议分析、漏洞挖掘。 |

* *总结**: 如果你想写一个"插件"来永久性地改变一个 App 的功能，用 Xposed；如果你想分析一个 App 的内部行为，用 Frida。
___
### 环境搭建 (以 LSPosed 为例)

当前，LSPosed 是社区中最主流、兼容性最好的 Xposed 框架实现，它基于 Riru/Zygisk，以 Magisk 模块的形式工作。

1. **前提条件**:
* 一台已解锁并刷入 Magisk 的 Android 设备（Android 8.1+）。
2. **安装 Riru 或启用 Zygisk**:
* **Zygisk (推荐)**: 在 Magisk Manager 中，进入设置，开启 `Zygisk` 选项。

* **Riru (备选)**: 在 Magisk Manager 的"模块"部分，搜索并安装 `Riru` 模块。
3. **安装 LSPosed**:
* 从 [LSPosed 的 GitHub Releases](https://github.com/LSPosed/LSPosed/releases) 页面下载最新的 Zygisk 版本 ZIP 包。

* 在 Magisk Manager 的"模块"页，选择"从本地安装"，然后选中下载的 LSPosed ZIP 包。

* 安装完成后，点击右下角的"重启"按钮。
4. **验证安装**:
* 重启后，桌面上会出现 LSPosed 的管理程序图标。

* 打开 LSPosed，如果状态显示为"已激活"，则表示框架安装成功。
___
### 开发第一个 Xposed 模块

我们将创建一个简单的模块，来 Hook 系统的时钟，在后面加上一个小尾巴。

#### 1. 项目结构

* 在 Android Studio 中创建一个新的、空的 Android 项目。

* 在 app 的 `build.gradle` 文件中添加 Xposed API 依赖：
    ```groovy
dependencies {
// ... other dependencies
compileOnly 'de.robv.android.xposed:api:82'
// 'compileOnly' is used because the framework is already provided by the system, only needed at compile time
}

````

- 创建一个新的 Java 类，例如 `ClockHook`，并让它实现 `IXposedHookLoadPackage` 接口。

```java
package com.example.myxposedmodule;

import de.robv.android.xposed.IXposedHookLoadPackage;
import de.robv.android.xposed.XC_MethodHook;
import de.robv.android.xposed.XposedBridge;
import de.robv.android.xposed.XposedHelpers;
import de.robv.android.xposed.callbacks.XC_LoadPackage.LoadPackageParam;
import android.widget.TextView;

public class ClockHook implements IXposedHookLoadPackage {
@Override
public void handleLoadPackage(final LoadPackageParam lpparam) throws Throwable {
// We only care about system UI
if (!lpparam.packageName.equals("com.android.systemui")) {
return;
}

XposedBridge.log("Loaded app: " + lpparam.packageName);

// Find and Hook the clock update class and method
// (Note: class names and method names may differ across Android versions)
XposedHelpers.findAndHookMethod(
"com.android.systemui.statusbar.policy.Clock", // Class name
lpparam.classLoader, // ClassLoader
"updateClock", // Method name
new XC_MethodHook() { // Hook callback
@Override
protected void afterHookedMethod(MethodHookParam param) throws Throwable {
super.afterHookedMethod(param);
TextView clockView = (TextView) param.thisObject;
String originalTime = clockView.getText().toString();
String newTime = originalTime + " ";
clockView.setText(newTime);
XposedBridge.log("Clock hooked! New time: " + newTime);
}
}
);
}
}

```

- 在 `app/src/main/AndroidManifest.xml` 的 `<application>` 标签内，添加 meta-data 来声明这是一个 Xposed 模块。

```xml
<meta-data
android:name="xposedmodule"
android:value="true" />
<meta-data
android:name="xposeddescription"
android:value="This is an example module that adds a tail to system clock" />
<meta-data
android:name="xposedminversion"
android:value="52" />

```

- 在 `assets` 文件夹内，创建一个名为 `xposed_init` 的文本文件。

- 在 `xposed_init` 文件中，写入你的 Hook 类的完整路径：

  ```

  ```

com.example.myxposedmodule.ClockHook

```

1. **构建 APK**: 在 Android Studio 中构建你的项目，生成 APK。
2. **安装 APK**: 将 APK 安装到你的测试设备上。
3. **激活模块**:
* 打开 LSPosed Manager。

* 进入"模块"部分，找到你刚刚安装的模块。

* 点击它，然后**启用**模块。

* 在作用域列表中，勾选"**SystemUI**"。
4. **重启目标进程**:
* 在 LSPosed 的状态页右上角，点击三个点菜单，选择"软重启"或"重启 SystemUI"，或者直接重启手机。
5. **查看效果**: 查看你的状态栏时钟，它现在应该带有一个 小尾巴了！你也可以在 LSPosed 的日志中看到 `XposedBridge.log` 输出的信息。
___
### 核心 API 详解

#### `IXposedHookLoadPackage`
这是所有模块的入口点。它只有一个方法 `handleLoadPackage(LoadPackageParam lpparam)`。当任何一个 App 启动时，Xposed 都会调用这个方法，并传入 `lpparam` 对象，其中包含了非常有用的信息：

* `lpparam.packageName`: 当前加载的 App 的包名。

* `lpparam.processName`: 当前进程名。

* `lpparam.classLoader`: 当前 App 的 ClassLoader，这是 Hook App 内部类的**必需品**。

#### `XposedHelpers`
一个包含大量静态辅助方法的工具类，极大简化了反射操作。

* `findAndHookMethod(String className, ClassLoader classLoader, String methodName, Object... parameterTypesAndCallback)`: 最核心的 Hook 方法。最后一个参数必须是 `XC_MethodHook` 回调。

* `findClass(String className, ClassLoader classLoader)`: 查找一个类。

* `getObjectField(Object obj, String fieldName)` / `setObjectField(Object obj, String fieldName, Object value)`: 获取/设置对象的成员变量。

* `callMethod(Object obj, String methodName, Object... args)`: 调用一个对象的方法。

* `getStaticObjectField(...)` / `callStaticMethod(...)`: 用于操作静态变量和静态方法。

#### `XC_MethodHook`
这是一个抽象类，你需要继承它并重写它的两个核心方法。

* `beforeHookedMethod(MethodHookParam param)`: 在原方法执行**前**被调用。

* `afterHookedMethod(MethodHookParam param)`: 在原方法执行**后**被调用。

这两个方法都接收一个 `MethodHookParam` 对象，它包含了本次方法调用的所有上下文信息：

* `param.thisObject`: `this` 指针，即方法所属的对象实例。

* `param.args`: `Object[]` 数组，包含了方法被调用时的所有参数。你可以在 `beforeHookedMethod` 中修改它。

* `param.getResult()`: 获取原方法的返回值。只能在 `afterHookedMethod` 中调用。

* `param.setResult(Object result)`: 设置一个新的返回值。如果在 `beforeHookedMethod` 中调用，原方法将**不会被执行**。如果在 `afterHookedMethod` 中调用，它会覆盖原方法的返回值。

* `param.getThrowable()` / `param.setThrowable(Throwable t)`: 用于获取/设置方法抛出的异常。
___
### 常见应用场景

* **UI 定制**: 修改系统或应用的外观，如状态栏、通知、锁屏等（代表作：`GravityBox`）。

* **功能增强**: 为应用添加原生不支持的功能，如为微信添加防撤回、自动抢红包功能。

* **去除限制**: 破解应用的付费功能、去除截图限制、去除广告等。

* **隐私保护**: 拦截应用获取敏感信息的请求（如定位、联系人、设备ID），并返回虚假或空数据（代表作：`XPrivacyLua`）。

* **安全分析**:
* 绕过 SSL Pinning（尽管 Frida 更灵活）。

* 禁用 Root 检测或反调试机制。

* 日志记录：打印关键方法的参数和返回值，分析应用行为。





<!-- 02-Tools/Dynamic/xposed_internals.md -->

# Xposed 内部原理：深度剖析

Xposed 是一个强大的 Android 框架，允许用户在运行时修改系统和应用程序进程的行为，而无需修改任何 APK 文件。本文档深入探讨了 Xposed 工作的核心原理。
___
## 1. 入口点：Zygote 进程注入

Xposed 的基础在于它能够将自定义代码注入到每个 Android 应用程序进程中。它通过针对 **Zygote** 进程来实现这一点，Zygote 是 Android OS 中的原始进程，所有应用程序进程都从它 fork 而来。

### 工作原理：

1. **替换 `app_process`**：在安装期间，Xposed 用自己修改后的版本替换原始的 `/system/bin/app_process` 可执行文件。这个可执行文件是 Zygote 进程启动的第一个程序。

2. **加载桥接器**：当 Zygote 启动时，它运行 Xposed 版本的 `app_process`。这个自定义可执行文件的主要任务是将一个特殊的 JAR 文件（通常称为 **Xposed Bridge**，即 `XposedBridge.jar`）加载到 Zygote 的地址空间中。

3. **通过 Fork 继承**：由于每个 Android 应用程序都是 Zygote 进程的 fork，它们都继承了父进程的内存空间。这意味着 Xposed Bridge JAR 从创建时刻起就自动加载到每个应用程序进程中。

这种巧妙的方法确保 Xposed 的核心逻辑在任何应用程序中都存在并准备好执行，为方法 Hook 提供了一个通用平台。

## 2. 核心魔法：方法 Hook

Xposed 最著名的功能是其"Hook"Java 方法的能力。这不是简单的反射；它是对底层虚拟机数据结构的深度操纵。

### `Method` 结构转换：

核心思想是改变虚拟机中目标 Java 方法的类型签名，使虚拟机认为它是一个 `native` 方法。

1. **查找目标**：模块使用 `findAndHookMethod` 等辅助函数来指定它们希望 Hook 的类和方法。

2. **修改 `Method` 对象**：在内部，Xposed 使用反射和本地代码来获取与目标对应的 Java `java.lang.reflect.Method` 对象的句柄。

3. **"Native"伪装**：

- Xposed 修改 `Method` 对象的 `accessFlags`，添加 `ACC_NATIVE` 标志。

- 然后它覆盖方法的入口点指针。在 ART 运行时中，这意味着替换内部 `ArtMethod` 结构中的 `entry_point_from_quick_compiled_code_` 字段。

- 这个新的入口点现在指向 Xposed 提供的通用原生桥接函数。

4. **保存原始方法**：在覆盖之前，Xposed 仔细地将原始方法的信息（包括其原始入口点和访问标志）保存到单独的备份结构中。

### Hooked 方法的执行流程：

当应用程序调用被 Xposed Hook 的方法时，会发生以下序列：

1. **绕道到原生桥接器**：虚拟机现在认为该方法是原生方法，将调用定向到 Xposed 的通用原生桥接函数。

2. **回调到 Java 桥接器**：原生函数做的事情很少。它的主要目的是回调到 Java 世界，调用 Xposed Bridge 中的核心 Java 方法：`handleHookedMethod`。

3. **`handleHookedMethod` 协调**：这个强大的 Java 方法协调整个 Hook 生命周期：

a. 它将方法的参数和 `this` 引用准备到一个 `MethodHookParam` 对象中。

b. **`beforeHookedMethod`**：它遍历模块中所有注册的回调，并调用它们的 `beforeHookedMethod` 方法。这些回调可以检查或修改参数。关键的是，"before"回调可以选择通过直接在 `param` 对象上设置结果来完全跳过原始方法。

c. **调用原始方法**：如果方法没有被跳过，`handleHookedMethod` 使用保存的备份信息来调用原始方法，并传入（可能已修改的）参数。

d. **`afterHookedMethod`**：在原始方法完成后，它再次遍历回调，这次调用它们的 `afterHookedMethod` 方法。这些回调可以检查或修改方法的返回值。

4. **返回给调用者**：最后，`handleHookedMethod` 将最终结果（来自"before"回调或原始方法的（已修改的）结果）返回给应用程序的原始调用点。

整个过程对应用程序代码是透明的，应用程序只是看到一个返回值的方法调用，而不知道它经历了复杂的绕道。

## 3. 模块加载机制

Xposed 模块是标准的 Android APK，它们向框架表明自己的性质。

- **`AndroidManifest.xml`**：模块的清单文件必须包含一个 `<meta-data>` 标签，其中 `android:name="xposedmodule"` 设置为 `true`。

- **`assets/xposed_init`**：模块 assets 目录中的这个文件是一个简单的文本文件。每行指向一个完全限定的类名。

- **`IXposedHookLoadPackage`**：`xposed_init` 中列出的类必须实现这个接口。Xposed 框架将实例化这些类，并为每个加载的应用程序包调用它们的 `handleLoadPackage` 方法，允许模块决定是否应用其 Hook。
___
## 架构图解

### Xposed 工作流程图

```

▼
┌─────────────────────────┐
│ 启动 Zygote 进程 │
└────────────┬────────────┘
│
▼
┌─────────────────────────┐
│ 运行修改的 app_process │
└────────────┬────────────┘
│
▼
┌─────────────────────────┐
│ 加载 XposedBridge.jar │
└────────────┬────────────┘
│
▼
┌─────────────────────────┐
│ Fork 应用进程 │
│ (继承 Xposed Bridge) │
└────────────┬────────────┘
│
▼
┌─────────────────────────┐
│ 应用启动 │
└────────────┬────────────┘
│
▼
┌─────────────────────────┐
│ 加载 Xposed 模块 │
│ (调用 handleLoadPackage)│
└────────────┬────────────┘
│
▼
┌─────────────────────────┐
│ Hook 目标方法 │
└─────────────────────────┘

```
┌──────────────────┐
│ VM 查找方法入口 │
└────────┬─────────┘
│
▼
┌─────────────────────────────┐
│ 检测到 ACC_NATIVE 标志 │
│ (已被 Xposed 修改) │
└────────┬────────────────────┘
│
▼
┌─────────────────────────────┐
│ 跳转到 Xposed Native Bridge │
└────────┬────────────────────┘
│
▼
┌─────────────────────────────┐
│ 调用 handleHookedMethod │
└────────┬────────────────────┘
│
├──► 调用 beforeHookedMethod 回调
│ (可以修改参数或跳过原方法)
│
├──► 调用原始方法 (如果未跳过)
│ (使用备份的原始入口点)
│
├──► 调用 afterHookedMethod 回调
│ (可以修改返回值)
│
▼
返回给调用者

```

**关键字段修改：**

- `access_flags_`: 添加 `ACC_NATIVE` 标志
- `entry_point_from_quick_compiled_code_`: 替换为 Xposed 桥接函数地址
- 备份原始字段值以便后续恢复

**伪代码示例：**

```cpp
// Xposed 内部简化逻辑
void hookMethod(ArtMethod* method) {
// 保存原始信息
backup.original_flags = method->access_flags_;
backup.original_entry = method->entry_point_from_quick_compiled_code_;

// 修改为 native 方法
method->access_flags_ |= ACC_NATIVE;
method->entry_point_from_quick_compiled_code_ = xposed_bridge_entry;
}

```

模块 A - beforeHookedMethod
│
▼
模块 B - beforeHookedMethod
│
▼
原始方法执行
│
▼
模块 B - afterHookedMethod
│
▼
模块 A - afterHookedMethod
│
▼
返回结果

````

### 3. 性能优化机制

* *JIT/AOT 编译影响：**

- Hooked 方法被标记为 native，避免 JIT 编译
- 通过 native 桥接的额外开销（约 10-50μs 每次调用）
- 大量 Hook 可能影响应用启动时间

* *最佳实践：**

- 只 Hook 必要的方法
- 在回调中避免耗时操作
- 使用条件判断减少不必要的处理
___
## 与其他 Hook 框架对比

| 特性 | Xposed | Frida | VirtualXposed |
| ------------- | ------------ | --------------------- | ------------- |
| **需要 Root** | 是 | 否（Gadget 模式除外） | 否 |
| **注入方式** | Zygote 级别 | 进程级别 | 虚拟化容器 |
| **性能开销** | 低-中 | 中-高 | 中 |
| **开发语言** | Java | JavaScript/Python | Java |
| **动态性** | 重启应用生效 | 实时生效 | 重启应用生效 |
| **稳定性** | 高 | 中 | 中-低 |
| **适用场景** | 长期修改 | 动态分析/调试 | 无 Root 测试 |
___
## 安全影响与检测

### 应用层检测方法

* *1. 检查 Xposed 特征文件：**

```java
private boolean isXposedInstalled() {
try {
// 检查 XposedBridge 类
Class.forName("de.robv.android.xposed.XposedBridge");
return true;
} catch (ClassNotFoundException e) {
return false;
}
}

````

int modifiers = method.getModifiers();
return Modifier.isNative(modifiers) && !shouldBeNative(method);
}

```
for (StackTraceElement trace : traces) {
if (trace.getClassName().contains("XposedBridge")) {
return true;
}
}
return false;
}

```

3. 清理堆栈跟踪信息
4. 使用定制版 Xposed（修改特征字符串）

---

## 实际应用场景

### 1. 隐私保护

- 伪造设备信息（IMEI、MAC 地址等）
- 阻止权限请求
- 拦截敏感数据上传

### 2. 功能增强

- 移除广告
- 解锁 VIP 功能
- 修改应用行为

### 3. 逆向分析

- 监控方法调用
- 提取加密密钥
- 分析算法逻辑

### 4. 自动化测试

- 模拟用户行为
- 注入测试数据
- 绕过验证码

---

## 模块开发示例

### 基础 Hook 示例

```java
public class MyXposedModule implements IXposedHookLoadPackage {

@Override
public void handleLoadPackage(XC_LoadPackage.LoadPackageParam lpparam)
throws Throwable {

// 只 Hook 目标应用
if (!lpparam.packageName.equals("com.example.target"))
return;

// Hook 方法
findAndHookMethod(
"com.example.target.MainActivity",
lpparam.classLoader,
"getUserInfo", // 方法名
new XC_MethodHook() {
@Override
protected void beforeHookedMethod(MethodHookParam param)
throws Throwable {
// 在方法执行前
XposedBridge.log("getUserInfo 即将被调用");
}

@Override
protected void afterHookedMethod(MethodHookParam param)
throws Throwable {
// 在方法执行后
String result = (String) param.getResult();
XposedBridge.log("getUserInfo 返回: " + result);

// 修改返回值
param.setResult("Fake User Info");
}
}
);
}
}

```

lpparam.classLoader,
byte[].class, // 参数类型
String.class,
new XC_MethodHook() {
@Override
protected void afterHookedMethod(MethodHookParam param)
throws Throwable {
byte[] key = (byte[]) param.args[0];
String algorithm = (String) param.args[1];

XposedBridge.log("捕获密钥!");
XposedBridge.log("算法: " + algorithm);
XposedBridge.log("密钥: " + bytesToHex(key));
}
}
);

1. **依赖 Root 权限**：需要系统级访问
2. **稳定性问题**：不当使用可能导致系统崩溃
3. **版本兼容性**：需要针对不同 Android 版本适配
4. **检测与对抗**：越来越多应用实施反 Xposed 检测

### 未来趋势

1. **EdXposed/LSPosed**：基于 Riru/Zygisk 的新实现
2. **虚拟化方案**：VirtualXposed、太极等无需 Root 的方案
3. **对抗升级**：更复杂的检测与反检测技术

---

## 总结

Xposed 通过以下核心技术实现了强大的运行时修改能力：

1. **Zygote 注入**：确保每个应用都加载 Xposed Bridge
2. **方法伪装**：将 Java 方法转换为 native，重定向入口点
3. **回调机制**：在方法执行前后插入自定义逻辑
4. **模块化设计**：灵活的 APK 插件系统

这种设计使 Xposed 成为 Android 平台上最强大的运行时修改框架之一，但同时也带来了安全风险和检测对抗的挑战。

理解 Xposed 的内部原理不仅有助于开发更好的模块，也为逆向工程、安全研究和应用保护提供了重要的技术洞察。

<!-- 02-Tools/Static/ghidra_guide.md -->

# Ghidra 入门

Ghidra 是由美国国家安全局 (NSA) 开发并开源的一款软件逆向工程 (SRE) 套件。它以功能全面、免费开源、跨平台等特性，迅速成为 IDA Pro 之外逆向工程师们的另一个重要选择，尤其在学术界和独立研究者中广受欢迎。

---

## 目录

1. [**核心特性**](#核心特性)
2. [**Ghidra vs. IDA Pro vs. Radare2**](#ghidra-vs-ida-pro-vs-radare2)
3. [**安装与配置**](#安装与配置)
4. [**基本工作流程**](#基本工作流程)
5. [**关键窗口与概念**](#关键窗口与概念)

- [Code Browser (代码浏览器)](#code-browser-代码浏览器)

- [Decompiler (反编译器)](#decompiler-反编译器)

- [Symbol Tree (符号树)](#symbol-tree-符号树)

- [Data Type Manager (数据类型管理器)](#data-type-manager-数据类型管理器)

- [Code Browser (代码浏览器)](#code-browser-代码浏览器)

- [Decompiler (反编译器)](#decompiler-反编译器)

- [Symbol Tree (符号树)](#symbol-tree-符号树)

- [Data Type Manager (数据类型管理器)](#data-type-manager-数据类型管理器)

6. [**脚本化与自动化**](#脚本化与自动化)
7. [**优缺点分析**](#优缺点分析)

---

## # 核心特性

- **强大的反编译器 (Decompiler)**: 这是 Ghidra 的王牌功能。它内置了一个高质量的、支持多种处理器架构的免费反编译器，能够将汇编代码转换为类似 C/C++ 的高级语言伪代码，极大地提高了代码理解效率。

- **全面的分析能力**: 支持对多种平台的可执行文件进行反汇编、分析、反编译、图表绘制和脚本化，包括 Windows, macOS, Linux, Android, iOS 等。

- **强大的脚本引擎**: 内置对 Java 和 Python (通过 Jython) 的支持，允许用户编写复杂的脚本来自动化分析任务，从简单的重命名到复杂的漏洞模式匹配。

- **交互式与自动化操作**: 既支持像 IDA Pro 那样的交互式手动分析，也提供了强大的"无头分析器"(Headless Analyzer)，可以通过命令行进行批量、自动化的分析。

- **多用户协作**: Ghidra Server 组件支持多名分析师对同一个二进制文件进行协同逆向，并能方便地进行版本追踪和合并。

- **可扩展性**: 用户可以自定义和扩展 Ghidra 的功能，包括编写新的处理器模块、加载器和分析器插件。

---

## # Ghidra vs. IDA Pro vs. Radare2

| 特性         | Ghidra                         | IDA Pro                     | Radare2                        |
| :----------- | :----------------------------- | :-------------------------- | :----------------------------- |
| **价格**     | **完全免费**                   | 非常昂贵                    | 完全免费                       |
| **开源**     | **是** (Java)                  | 否                          | 是 (C)                         |
| **核心优势** | **高质量的免费反编译器**       | **最强的交互式反汇编**      | **极致的脚本化和命令行**       |
| **UI**       | Java Swing，功能强大但略显笨重 | Qt，业界标准，成熟稳定      | 命令行，或通过 Cutter 提供 GUI |
| **自动化**   | 强大的 Headless 模式和脚本     | 主要通过 IDC/IDAPython 脚本 | 设计哲学核心，自动化能力极强   |
| **协作**     | 内置 Ghidra Server 支持        | 第三方插件 (如 BinSync)     | 脚本化协作，或通过第三方工具   |
| **学习曲线** | 中等，UI 直观                  | 中等，功能繁多              | **非常陡峭**，命令繁杂         |

---

## # 安装与配置

1. **前提**: 确保已安装 Java Development Kit (JDK) 11 或更高版本。
2. **下载**: 从 [Ghidra 官方网站](https://ghidra-sre.org/) 下载最新的稳定版 ZIP 包。
3. **解压**: 将 ZIP 包解压到任意目录。
4. **运行**:

- **Windows**: 双击运行 `ghidraRun.bat`。

- **Linux / macOS**: 在终端中执行 `sh ghidraRun`。
- **Windows**: 双击运行 `ghidraRun.bat`。

- **Linux / macOS**: 在终端中执行 `sh ghidraRun`。

5. **(可选) Ghidra Dark Theme**: Ghidra 的默认主题比较刺眼，可以通过安装 `Ghidra-dark-theme` 插件来获得更好的视觉体验。

---

## # 基本工作流程

1. **创建项目**:

- `File -> New Project...`

- 选择 `Non-Shared Project` (单用户项目)。

- 指定项目路径和名称。
- `File -> New Project...`

- 选择 `Non-Shared Project` (单用户项目)。

- 指定项目路径和名称。

2. **导入文件**:

- `File -> Import File...`

- 选择你想要分析的二进制文件 (如 `.exe`, `.dll`, `.so`, `.apk`)。

- Ghidra 会自动识别文件格式、处理器架构等，直接点击 `OK`。
- `File -> Import File...`

- 选择你想要分析的二进制文件 (如 `.exe`, `.dll`, `.so`, `.apk`)。

- Ghidra 会自动识别文件格式、处理器架构等，直接点击 `OK`。

3. **分析文件**:

- 在弹出的分析选项框中，保留默认勾选的分析器即可，点击 `Analyze`。

- Ghidra 会开始对文件进行自动分析，这可能需要一些时间，取决于文件大小和复杂度。
- 在弹出的分析选项框中，保留默认勾选的分析器即可，点击 `Analyze`。

- Ghidra 会开始对文件进行自动分析，这可能需要一些时间，取决于文件大小和复杂度。

4. **开始探索**:

- 分析完成后，双击项目窗口中的文件名，打开 Ghidra 的核心工具 **Code Browser**。

- 现在你可以开始你的逆向之旅了！

- 分析完成后，双击项目窗口中的文件名，打开 Ghidra 的核心工具 **Code Browser**。

- 现在你可以开始你的逆向之旅了！

---

## # 关键窗口与概念

### Code Browser (代码浏览器)

这是 Ghidra 的主界面，通常包含以下几个核心子窗口：

- **Listing (清单/反汇编窗口)**: 左侧显示反汇编代码，是分析的主要区域。

- **Functions (函数窗口)**: 左下角，列出所有已识别的函数。点击函数名可以在反汇编窗口中跳转。

- **Program Trees (程序树)**: 左上角，以树状结构展示程序的段 (sections)。

### Decompiler (反编译器)

- 通常位于反汇编窗口的右侧。

- 它会自动显示当前光标所在函数的 C 伪代码。

- 这是 Ghidra 最有价值的窗口。你可以直接在伪代码中对变量、函数进行重命名、修改类型，这些改动会**双向同步**到反汇编窗口。

### Symbol Tree (符号树)

- 位于左侧，`Functions` 窗口旁边。

- 它以树状结构列出了程序中所有的符号，包括函数、标签、导入/导出函数等。你可以通过过滤器快速查找特定函数。

### Data Type Manager (数据类型管理器)

- 左下角，`Functions` 窗口下方。

- 这里管理着程序中所有的数据类型 (struct, union, enum 等)。你可以创建、修改、导入和导出数据类型定义。这对于分析复杂的数据结构至关重要。

---

## # 脚本化与自动化

Ghidra 强大的脚本能力是其核心优势之一。

1. **打开 Script Manager**: 在 Code Browser 中，点击顶部菜单栏的绿色播放按钮图标，打开 **Script Manager**。
2. **选择与运行脚本**: 这里有大量 NSA 官方和社区贡献的预置脚本，覆盖了从查找密码、解密数据到识别特定代码模式等各种任务。
3. **编写自己的脚本**:

- 你可以通过 `Create New Script` 按钮创建新的 Java 或 Python 脚本。

- Ghidra 提供了丰富的 API (称为 `FlatAPI`)，让你可以在脚本中访问和修改程序的几乎所有信息，例如：

  ```python

  ```

# A simple Python script example that prints all function names and addresses

from ghidra.program.model.symbol import SymbolType

print("--- All Functions ---")
func_manager = currentProgram.getFunctionManager()
funcs = func_manager.getFunctions(True) # True means iterate in address order
for func in funcs:
print("{} at {}".format(func.getName(), func.getEntryPoint()))

```

## # 优缺点分析

### 优点

* **免费与开源**: 无任何费用，社区可以审查和贡献代码。


* **强大的反编译器**: 内置的高质量反编译器是其最大的卖点，足以媲美甚至在某些方面超越昂贵的商业软件。


* **跨平台**: 基于 Java，可以在 Windows, macOS, Linux 上无差别运行。


* **优秀的协作功能**: Ghidra Server 的存在使得团队协作变得非常容易。


### 缺点

* **性能**: 基于 Java Swing 的 UI 在处理超大型二进制文件时，可能会感到卡顿，性能不如 IDA Pro。


* **生态系统**: 虽然正在快速发展，但插件和社区支持的成熟度仍然不及 IDA Pro 经营多年的生态。


* **原生调试器**: Ghidra 的调试器功能相对较弱，不如 IDA Pro 和 x64dbg 等专用调试器成熟。
```

<!-- 02-Tools/Static/ida_pro_guide.md -->

# IDA Pro 入门

IDA Pro (Interactive Disassembler Professional) 是由 Hex-Rays 公司开发的一款业界闻名的交互式反汇编器。在逆向工程领域，IDA Pro 被广泛认为是**黄金标准**，以其最强大的反汇编引擎、无与伦比的处理器支持和极其成熟的生态系统，成为专业人士进行软件分析、漏洞挖掘和恶意软件研究的首选工具。

---

## 目录

- [IDA Pro 入门](#ida-pro-入门)
- [目录](#目录)
- [核心特性](#核心特性)

- [IDA Pro vs. Ghidra vs. Radare2](#ida-pro-vs-ghidra-vs-radare2)

- [版本与安装](#版本与安装)

- [基本工作流程](#基本工作流程)

- [关键视图与快捷键](#关键视图与快捷键)
- [IDA View (反汇编视图)](#ida-view-反汇编视图)

- [Hex View (十六进制视图)](#hex-view-十六进制视图)

- [Structures (结构体视图)](#structures-结构体视图)

- [Enums (枚举视图)](#enums-枚举视图)

- [核心快捷键](#核心快捷键)
- [脚本与插件](#脚本与插件)

- [优缺点分析](#优缺点分析)
- [优点](#优点)

- [缺点](#缺点)

---

### 核心特性

- **顶级的反汇编引擎**: IDA Pro 的核心竞争力在于其无与伦比的静态反汇编能力。它能够智能地、递归地遍历代码，区分代码与数据，识别函数边界，其分析结果的准确性是业界公认的最高水准。

- **FLIRT 技术**: **F**ast **L**ibrary **I**dentification and **R**ecognition **T**echnology。这是 IDA 的标志性技术，通过对标准编译器库函数的签名进行模式匹配，能够自动识别并命名大量的库函数，极大地减少了逆向工程师的重复工作。

- **强大的交互性**: IDA 的设计哲学鼓励用户与反汇编结果进行交互。用户可以随时重命名变量、修改类型、添加注释、转换数据格式，这些交互操作会实时地影响整个分析数据库。

- **Hex-Rays 反编译器 (付费插件)**: IDA Pro 的杀手级应用是其配套的 Hex-Rays 反编译器。虽然需要额外付费，但它被公认为目前市面上最强大的 C/C++ 反编译器，生成的伪代码质量极高，可读性极强。

- **多平台调试器**: 内置了强大的跨平台调试器，支持本地和远程调试，允许动态分析和修改程序行为。

- **极其丰富的插件生态**: 经过数十年的发展，IDA Pro 积累了海量的第三方插件，覆盖了从漏洞扫描、代码着色、数据解密到与其他工具联动的方方面面，极大地扩展了其功能边界。

---

### IDA Pro vs. Ghidra vs. Radare2

| 特性           | IDA Pro                         | Ghidra                         | Radare2                           |
| :------------- | :------------------------------ | :----------------------------- | :-------------------------------- |
| **价格**       | **非常昂贵**                    | 完全免费                       | 完全免费                          |
| **开源**       | **否**                          | 是 (Java)                      | 是 (C)                            |
| **核心优势**   | **最强的交互式反汇编**          | 高质量的免费反编译器           | 极致的脚本化和命令行              |
| **UI**         | **Qt，业界标准，成熟稳定**      | Java Swing，功能强大但略显笨重 | 命令行，或通过 Cutter 提供 GUI    |
| **反编译器**   | **Hex-Rays (业界顶尖，需付费)** | 内置免费，质量非常高           | 内置免费 (ghidra-dec)，或支持其他 |
| **生态系统**   | **极其成熟，插件海量**          | 快速发展中                     | 高度可定制，但插件较少            |
| **处理器支持** | **最广泛**                      | 广泛，但略少于 IDA             | 极广，覆盖很多小众架构            |

---

### 版本与安装

- **版本**: IDA Pro 有多个版本，主要区别在于支持的处理器架构和是否包含反编译器。`IDA Pro` 版本通常包含所有处理器模块和调试器，而 `IDA Home` 是针对个人爱好者的廉价版，功能受限。

- **购买与安装**: 需要通过官方或授权经销商购买。安装过程是标准的下一步式安装。

- **免费版**: Hex-Rays 提供一个免费版本的 IDA，但功能严重受限，仅支持 x86/x64，且不能保存数据库，仅适合非常初级的学习。

---

### 基本工作流程

1. **启动 IDA**: 打开 IDA Pro。
2. **加载文件**: 在启动界面点击 `New`，或将二进制文件直接拖入主窗口。
3. **加载选项**: IDA 会弹出一个加载对话框，让你确认文件类型、处理器类型等。通常，IDA 的自动分析非常准确，直接点击 `OK` 即可。
4. **自动分析**: IDA 会进行长时间的自动分析。分析过程可以在底部的输出窗口看到。**耐心等待分析完成**是使用 IDA 的好习惯，否则很多功能无法正常使用。
5. **开始分析**: 分析完成后，即可开始交互式分析。

---

### 关键视图与快捷键

#### IDA View (反汇编视图)

- 这是 IDA 的主视图。按**空格键**可以在**图形视图**（流程图）和**文本视图**（线性反汇编）之间切换。

- **图形视图**非常适合理解函数内的逻辑分支和循环。

#### Hex View (十六进制视图)

- 以经典的十六进制编辑器形式展示文件内容，与反汇编视图同步高亮。

#### Structures (结构体视图)

- 快捷键 `Shift+F9`。

- 用于定义和管理 C 语言风格的结构体。你可以手动创建，也可以从 C 头文件导入。正确地定义数据结构是逆向工程的关键一步。

#### Enums (枚举视图)

- 快捷键 `Shift+F10`。

- 用于定义和管理枚举类型，可以极大地提高代码的可读性，例如将 `mov eax, 2` 变为 `mov eax, MODE_READ`。

#### 核心快捷键

- `G`: 跳转到指定地址。

- `N`: 重命名变量、函数、标签。

- `Y`: 修改变量类型。

- `X`: 查看交叉引用 (cross-references)，即哪些地方调用/引用了当前符号。

- `P`: 创建一个函数。

- `U`: 取消定义（如将代码变为未定义数据）。

- `;`: 添加行注释。

- `:`: 添加可重复注释。

- `F5`: (如果已购买) 启动 Hex-Rays 反编译器。

---

### 脚本与插件

IDA 的强大能力有一半来自于其脚本和插件系统。

- **IDAPython**: 这是目前最主流的脚本语言。IDA 内置了一个完整的 Python 解释器和丰富的 API，允许你用 Python 脚本与 IDA 数据库进行深度交互。几乎所有重复性工作都可以通过 IDAPython 自动化。

- **IDC**: IDA 自带的类 C 脚本语言。语法古老，功能不如 IDAPython 强大，但对于一些简单的任务仍然有用。

- **插件**: IDA 的插件机制允许开发者使用 C++ 编写高性能插件，并将其深度集成到 IDA 的 UI 和核心中。社区中有大量优秀的开源插件，如 `FindCrypt`, `Keypatch` 等。

---

### 优缺点分析

#### 优点

- **最强的反汇编质量**: 业界公认的、最可靠的静态分析结果。

- **FLIRT 和类型系统**: 极大地自动化了库函数和数据结构的识别过程。

- **成熟和稳定**: 经过数十年打磨，软件本身极为稳定，用户体验流畅。

- **强大的生态**: 海量的插件、教程和社区支持，遇到任何问题几乎都能找到解决方案。

- **顶级的反编译器**: Hex-Rays 反编译器是其最强大的护城河。

#### 缺点

- **价格昂贵**: 对于个人开发者或小型团队来说，价格是最大的门槛。

- **闭源**: 核心功能是黑盒，无法审查或修改。

- **协作不便**: 原生不支持多人协作，需要依赖第三方插件。

<!-- 02-Tools/Static/radare2_guide.md -->

# Radare2 入门

Radare2 (通常简称为 r2) 是一款开源、免费、命令行驱动的逆向工程框架。它不仅仅是一个反汇编器，更像是一个功能极其丰富的"瑞士军刀"，集成了十六进制编辑、反汇编、调试、代码分析、漏洞利用、数据可视化等多种功能。Radare2 以其高度的可脚本化和可扩展性而闻名，深受寻求自动化和深度定制的黑客、CTF 选手和安全研究员的喜爱。

---

## 目录

- [Radare2 入门](#radare2-入门)
- [目录](#目录)
- [核心理念与特性](#核心理念与特性)

- [Radare2 vs. IDA Pro vs. Ghidra](#radare2-vs-ida-pro-vs-ghidra)

- [安装与入门](#安装与入门)

- [基本命令与工作流程](#基本命令与工作流程)
- [核心概念：万物皆 `?`](#核心概念万物皆-)

- [分析 (`a`)](#分析-a)

- [打印 (`p`)](#打印-p)

- [信息 (`i`)](#信息-i)

- [Seek (`s`)](#seek-s)

- [可视化 (`V`)](#可视化-v)
- [Cutter - Radare2 的 GUI](#cutter---radare2-的-gui)

- [脚本化](#脚本化)

- [优缺点分析](#优缺点分析)
- [优点](#优点)

- [缺点](#缺点)

---

### 核心理念与特性

- **命令行驱动**: Radare2 的所有核心功能都通过命令行接口暴露。这使得它非常适合在终端、SSH 会话或脚本中运行，易于实现自动化。

- **模块化设计**: 其功能由一系列单字母命令和子命令构成，例如 `p` 用于打印 (print)，`a` 用于分析 (analyze)，`d` 用于调试 (debug)。这种设计遵循了 Unix 哲学。

- **海量架构支持**: Radare2 支持数量惊人的处理器架构，包括许多非常小众和古老的嵌入式架构，这方面甚至超过了 IDA Pro。

- **高度可脚本化**: 你可以使用任何你喜欢的语言（Python, Go, JavaScript, Rust 等）通过 r2pipe 与 Radare2 实例进行交互，实现复杂的自动化分析流程。

- **内置调试器**: 集成了功能强大的多平台调试器，支持硬件断点、跟踪等高级功能。

- **强大的二进制文件解析**: 不仅支持 ELF, PE, Mach-O 等标准格式，还能解析文件系统、图片、文档等各种二进制 blob。

---

### Radare2 vs. IDA Pro vs. Ghidra

| 特性         | Radare2                    | IDA Pro                | Ghidra                         |
| :----------- | :------------------------- | :--------------------- | :----------------------------- |
| **价格**     | **完全免费**               | 非常昂贵               | 完全免费                       |
| **开源**     | **是 (C)**                 | 否                     | 是 (Java)                      |
| **核心优势** | **极致的脚本化和命令行**   | 最强的交互式反汇编     | 高质量的免费反编译器           |
| **UI**       | **命令行** (或 Cutter GUI) | Qt，业界标准，成熟稳定 | Java Swing，功能强大但略显笨重 |
| **学习曲线** | **非常陡峭**               | 中等                   | 中等                           |
| **自动化**   | **设计哲学核心，能力极强** | 主要通过 IDC/IDAPython | 强大的 Headless 模式           |
| **灵活性**   | **最高**，一切皆可定制     | 较低，依赖插件         | 较高，可通过插件扩展           |

---

### 安装与入门

- **安装**: 最推荐的安装方式是通过 `git` 克隆官方仓库并运行安装脚本：
  ```bash
  git clone https://github.com/radareorg/radare2
  cd radare2
  sys/install.sh
  ```

````

* **启动**:
    ```bash
# Open file and perform analysis
r2 /bin/ls

# Open file and perform debug
r2 -d /bin/ls

````

---

### 基本命令与工作流程

Radare2 的命令结构是 `[命令][子命令][参数]`。例如 `pdf` 是 `p` (print) -> `d` (disassemble) -> `f` (function) 的组合，意为"打印函数反汇编"。

#### 核心概念：万物皆 `?`

在任何命令后面加上 `?` 都可以查看该命令的帮助文档。这是学习 Radare2 最重要的方法。

- `?`: 显示顶级帮助。

- `a?`: 显示分析 (analyze) 命令的帮助。

- `pdf?`: 显示打印函数反汇编命令的帮助。

#### 分析 (`a`)

在你对一个二进制文件做任何事情之前，通常需要先分析它。

- `aaa`: 自动分析所有（函数、符号等）。这是最常用的起手命令。

- `afl`: 列出所有已识别的函数 (Analyze Function List)。

- `af`: 分析函数。

#### 打印 (`p`)

用于以不同格式显示数据。

- `px`: 以十六进制格式打印 (Print heXadecimal)。

- `ps`: 打印字符串 (Print String)。

- `pd N`: 反汇编 N 条指令 (Print Disassembly)。

- `pdf`: 打印当前函数的反汇编 (Print Disassembly Function)。

#### 信息 (`i`)

用于显示文件的元信息。

- `iI`: 显示文件基本信息 (入口点、架构等)。

- `is`: 显示符号。

- `iS`: 显示段 (sections)。

#### Seek (`s`)

用于在文件中跳转。

- `s main`: 跳转到 `main` 函数的地址。

- `s 0x8048400`: 跳转到指定地址。

- `s-`: 撤销上一次跳转。

#### 可视化 (`V`)

Radare2 提供了强大的文本模式可视化功能。

- **进入/退出**: 按 `V` 进入可视化模式，按 `q` 退出。

- **切换视图**: 在可视化模式下，按 `p` 和 `P` 可以在不同视图（反汇编、十六进制、调试寄存器等）之间切换。

- **图形视图**: 可视化模式下的 `v` 键可以展示函数的 ASCII-art 流程图，非常酷。

---

### Cutter - Radare2 的 GUI

对于不习惯纯命令行的用户，社区开发了 **Cutter**。Cutter 是一个基于 Qt C++ 的图形用户界面，后端由 Radare2 驱动。

- 它提供了类似 IDA Pro 和 Ghidra 的图形化界面，包括反汇编窗口、反编译窗口（集成了 Ghidra Decompiler）、函数列表、Hexdump 等。

- 所有在 Cutter 中进行的操作，实际上都是在后台调用 Radare2 的命令完成的。

- 对于初学者来说，从 Cutter 入手可以极大地降低学习 Radare2 的门槛。

---

### 脚本化

Radare2 的精髓在于自动化。`r2pipe` 是其官方的脚本库，支持多种语言。
以下是一个 Python 脚本示例，用于打开一个文件，分析它，并打印所有函数的名称：

```python
import r2pipe

# Open file
r2 = r2pipe.open("/bin/ls")

# Run 'aaa' command to perform analysis
r2.cmd('aaa')

# Run 'aflj' command to get JSON format function list and parse
functions = r2.cmdj('aflj')

# Print each function name
if functions:
for func in functions:
print(f"Function found: {func['name']} at {hex(func['offset'])}")

```

- **无与伦比的脚本化能力**: 设计哲学使其成为自动化逆向分析的理想选择。

- **极高的灵活性和定制性**: 你可以按照自己的需求组合命令，构建工作流。

- **轻量与快速**: 核心程序非常小，运行速度快，资源占用少。

- **海量架构支持**: 对各种奇异架构的支持是其一大特色。

#### 缺点

- **陡峭的学习曲线**: 命令繁多，语法特殊，对新手非常不友好。

- **文档相对混乱**: 虽然有帮助系统，但官方文档的结构性和完整性不如商业软件。

- **默认反编译器**: 内置的反编译器质量不如 Ghidra 或 Hex-Rays，但可以通过插件集成 Ghidra Decompiler。

<!-- 03-Case-Studies/case_anti_analysis_techniques.md -->

# 案例研究：反分析技术

为了保护其核心代码和数据不被轻易分析，现代 App 普遍采用了一系列的反分析技术。这些技术旨在检测和阻止调试器、Hook 框架（如 Frida）和模拟器的运行。本案例将分类介绍这些技术的实现原理和常见的绕过策略。

---

## 1. 反调试 (Anti-Debugging)

- **目标\*\***: 检测 App 是否正被调试器附加。

### 案例：基于 `TracerPid` 的检测

这是最常见的一种反调试方法。在 Linux 内核中，每个进程的 `/proc/<pid>/status` 文件都记录了其状态信息，其中 `TracerPid` 字段表示正在追踪（调试）该进程的进程 PID。如果一个进程没有被调试，该值为 0。

- **实现原理\*\***:
  App 在运行时会启动一个独立的线程或子进程，周期性地读取自身的 `TracerPid`。

```c
// Native (C/C++) implementation
#include <stdio.h>
#include <string.h>

int check_tracer_pid() {
FILE *fp = fopen("/proc/self/status", "r");
if (fp == NULL) {
return 0;
}

char line[128];
while (fgets(line, sizeof(line), fp)) {
if (strncmp(line, "TracerPid:", 10) == 0) {
int tracer_pid = 0;
sscanf(line, "TracerPid:\t%d", &tracer_pid);
fclose(fp);
return tracer_pid;
}
}
fclose(fp);
return 0;
}

// Call this in a loop somewhere in the App
if (check_tracer_pid() != 0) {
// Debugger detected, execute exit or crash logic
exit(0);
}

```

---

## 2. 反 Hook (Anti-Hooking)

- **目标\*\***: 检测和阻止 Frida 等 Hook 框架的注入和功能。

### 案例：扫描内存中的 Frida 特征

Frida 在注入到目标进程后，会在内存中留下一些特征，如其核心库 `frida-agent.so`。

- **实现原理\*\***:
  App 会扫描自身的内存映射（`/proc/self/maps`），寻找是否存在包含 `frida` 或 `gumjs` 等关键词的库。

```c
// Native (C/C++) implementation
int check_for_frida_in_maps() {
FILE *fp = fopen("/proc/self/maps", "r");
if (fp == NULL) {
return 0;
}

char line[256];
while (fgets(line, sizeof(line), fp)) {
if (strstr(line, "frida-agent") || strstr(line, "gumjs")) {
fclose(fp);
return 1; // Frida detected
}
}
fclose(fp);
return 0;
}

```

---

## 3. 反模拟器 (Anti-Emulator)

- **目标\*\***: 检测 App 是否运行在模拟器（如 Genymotion, Android SDK Emulator）而非真实设备上。

### 案例：检测设备特有文件或属性

模拟器通常会留下一些区别于真机的特有文件、驱动或系统属性。

- **实现原理\*\***:
- **检查系统属性**: 通过 `getprop` 或直接读取 `build.prop` 文件，检查是否存在 `ro.kernel.qemu`, `ro.hardware.goldfish` 等模拟器特有的属性。

- **检查文件**: 检查是否存在 `/system/lib/libc_malloc_debug_qemu.so` 或 `/sys/qemu_trace` 等文件。

- **检查 CPU 信息**: 读取 `/proc/cpuinfo`，检查 `Hardware` 字段是否包含 `Goldfish` 或 `Intel` 等，而非 `Qualcomm`, `MediaTek` 等移动端处理器厂商。

- **绕过策略\*\***:
- **Hook `System.getProperty`**: 在 Java 层 Hook 该方法，当请求特定属性时返回一个伪造的、看起来像真机的值。

- **Hook 文件 API**: Hook `File.exists()` 或 Native 层的 `access()`, `stat()` 等函数，对特定的模拟器文件路径返回 `false`。

- **使用定制 ROM**: 在一个修改过的 Android ROM 中，可以从系统层面移除或伪造这些模拟器特征。

- **选择更逼真的模拟器**: 一些商业或开源的、高度定制化的模拟器在隐藏自身特征方面做得更好，更难被检测。

---

## 总结

反分析技术的攻防是一个不断升级的"猫鼠游戏"。

- **检测方**: 努力寻找分析工具（调试器、Frida）在目标系统中留下的任何蛛丝马迹。

- **绕过方**: 努力抹去或伪造这些痕迹，让 App 认为自己运行在一个"干净"的环境中。

成功的绕过往往需要多项技术的组合，从 Java 层的 Hook，到 Native 层的 Patching，再到对操作系统和工具链本身的定制。

<!-- 03-Case-Studies/case_flutter_apps.md -->

# 案例研究：Flutter 应用逆向

Flutter 是 Google 推出的跨平台 UI 框架，它使用 Dart 语言开发。与传统的 Android App (Java/Kotlin) 或 Unity (C#) 不同，Release 模式下的 Flutter 应用将 Dart 代码预编译 (AOT) 成了原生机器码，打包在 `libapp.so` 中，这使得逆向难度大大增加。

---

## 核心架构

1. **`lib/armeabi-v7a/libflutter.so`**: Flutter 引擎，负责渲染、通信和运行时支持。通常不需要逆向，但可以用它来定位关键的内部函数。
2. **`lib/armeabi-v7a/libapp.so`**: **逆向的核心目标**。包含了开发者的所有业务逻辑代码（Dart 代码编译后的产物）。
3. **Snapshot 格式**: `libapp.so` 实际上不仅仅是代码，还包含了一个 Dart VM Snapshot。它没有标准的 ELF 符号表，也没有类似 Java 的类结构元数据。

---

## 逆向流程

## # 第 1 步：识别 Flutter 应用

解压 APK，查看 `lib` 目录。如果看到 `libflutter.so` 和 `libapp.so`，那么这肯定是一个 Flutter 应用。

## # 第 2 步：使用 reFlutter 框架

由于 Dart AOT 的特殊性，直接用 IDA 分析 `libapp.so` 非常困难，因为所有函数名都被剥离了，且 Dart 的调用约定和寄存器使用方式与标准 C/C++ 不同。

- **reFlutter\*\*** 是目前最强大的 Flutter 逆向辅助工具。它通过修改 Flutter 引擎 (`libflutter.so`)，在应用运行时利用 Dart VM 的内部机制来 Dump 类、函数和偏移信息。

- **工具\*\***: [reFlutter](https://github.com/Impact-I/reFlutter)

- **操作步骤\*\***:

1. **重打包**: 使用 reFlutter 处理目标 APK。
   ```bash
   reflutter target.apk
   ```

````
2. **安装运行**: 安装生成的 `release.RE.apk` 到手机。
3. **获取偏移**: 应用启动后，reFlutter 会在 Logcat 中输出关键的 Dart 库函数的偏移地址，或者生成一个 `dump.dart` 文件。

## # 第 3 步：流量拦截 (SSL Pinning Bypass)

Flutter 应用不使用系统的代理设置，也不使用 Java 层的 HTTP 客户端 (OkHttp)，而是使用 Dart 自己的 `HttpClient`。因此，传统的抓包设置（Wi-Fi 代理）和 Frida SSL Pinning 脚本通常无效。

* *reFlutter 的方案**:
reFlutter 在重打包时，会自动 Patch `libflutter.so` 中的网络校验逻辑，并强制将流量转发到指定的代理 IP（需要在 reFlutter 配置阶段输入你的 Burp/Charles IP）。这是目前拦截 Flutter 流量最稳定的方法。

* *Frida 方案 (Hook 验证函数)**:
如果你不想重打包，可以使用 Frida Hook `libflutter.so` 中负责验证证书的函数。
* 函数名通常包含 `SessionVerifyCertificateChain`。
* 你需要下载对应 Flutter 版本的 `libflutter.so` 符号文件，或者通过特征码搜索该函数。
* Hook 该函数并使其直接返回验证成功。

## # 第 4 步：使用 Doldrums 还原代码

* *Doldrums** 是一个针对 Flutter Android 应用的静态分析工具，试图将 `libapp.so` 反编译回 Dart 伪代码。

* *工具**: [Doldrums](https://github.com/rscloura/Doldrums)

* 注意：由于 Flutter 版本更新极快，Snapshot 格式经常变动，Doldrums 可能不支持最新的 Flutter 版本。

## # 第 5 步：动态分析 (Dart VM Hook)

如果无法静态还原代码，我们需要在运行时进行 Hook。由于没有符号，我们需要结合 reFlutter 导出的偏移地址。

```javascript
// Frida Script Example: Hook Dart Function
// Assume reFlutter tells us the function offset to hook is 0x1a2b3c

var appBase = Module.findBaseAddress('libapp.so');
var targetOffset = 0x1a2b3c;
var targetFunc = appBase.add(targetOffset);

Interceptor.attach(targetFunc, {
onEnter: function(args) {
// Dart function parameter passing is special
// args[0] may not be the first parameter, but a Closure or other VM structure
// Parameters are usually stored in specific registers or stack locations, depending on Dart version and ABI
console.log("Dart function called!");

// Print parameters (try reading first 4 parameters)
console.log("Arg1: " + args[0]);
console.log("Arg2: " + args[1]);
console.log("Arg3: " + args[2]);
},
onLeave: function(retval) {
console.log("Dart function returned: " + retval);
}
});

````

2. **代码分析**: 静态分析工具（如 Doldrums）兼容性较差，主要依赖 **reFlutter** 提取偏移 + **Frida** 动态调试。
3. **核心**: 理解 Dart VM 的工作原理（Snapshot 结构、Object Pool、Dispatch Table）是深入逆向 Flutter 的基础。

````



<!-- 03-Case-Studies/case_malware_analysis.md -->

# 案例研究：安卓银行木马分析

恶意软件分析是逆向工程的一个重要应用领域。与常规 App 分析不同，分析恶意软件更关注其**隐藏行为**、**持久化机制**、**窃密手段**以及**C2 (Command & Control) 通信**。

本案例将模拟分析一个典型的 **Android 银行木马 (Banking Trojan)**。
___
## 样本概况

* **伪装**: 该木马伪装成 "Flash Player" 或 "系统更新" 应用。
* **行为**: 诱导用户开启“无障碍服务”，然后利用该权限进行点击劫持、覆盖攻击 (Overlay Attack)，窃取银行 App 的账号密码，并拦截短信验证码。
___
## 详细分析流程

## # 第 1 步：静态分析 (Manifest & 权限)

使用 `jadx` 打开 APK，首先查看 `AndroidManifest.xml`。

* *关键发现**:
1. **敏感权限**:
* `android.permission.BIND_ACCESSIBILITY_SERVICE` (无障碍服务 - 核心权限)
* `android.permission.RECEIVE_SMS` (接收短信)
* `android.permission.READ_SMS` (读取短信)
* `android.permission.SYSTEM_ALERT_WINDOW` (悬浮窗 - 用于覆盖攻击)
* `android.permission.REQUEST_IGNORE_BATTERY_OPTIMIZATIONS` (忽略电池优化 - 保活)

2. **入口点 (Entry Points)**:
* 发现一个 `MainActivity`，但代码很简单，只是请求权限。
* 发现一个 `MyAccessibilityService`，继承自 `AccessibilityService`，这是核心逻辑所在。

## # 第 2 步：分析无障碍服务 (Accessibility Service)

定位到 `MyAccessibilityService` 类，重点分析 `onAccessibilityEvent` 方法。

```java
public void onAccessibilityEvent(AccessibilityEvent event) {
String packageName = event.getPackageName().toString();

// 1. Auto grant permissions (Self-Protection & Persistence)
if (packageName.equals("com.android.settings")) {
// If user opens settings page to uninstall or disable permissions, malware will auto click "Back" or "Cancel"
performGlobalAction(GLOBAL_ACTION_BACK);
}

// 2. Monitor target banking apps
if (TARGET_BANK_APPS.contains(packageName)) {
// Detected victim opened banking app
showOverlay(packageName);
}

// 3. Keyboard recording (Keylogging)
if (event.getEventType() == AccessibilityEvent.TYPE_VIEW_TEXT_CHANGED) {
String text = event.getText().toString();
logKey(text);
}
}

````

- **窃取**: 用户以为自己在登录银行，实际上是在木马的 WebView 中输入了账号密码。木马通过 JavaScript Interface 将输入的数据传回 Java 层，然后上传服务器。

## # 第 4 步：短信拦截 (SMS Stealing)

分析 `SmsReceiver` 类。

```java
public class SmsReceiver extends BroadcastReceiver {
@Override
public void onReceive(Context context, Intent intent) {
Object[] pdus = (Object[]) intent.getExtras().get("pdus");
for (Object pdu : pdus) {
SmsMessage sms = SmsMessage.createFromPdu((byte[]) pdu);
String body = sms.getMessageBody();
String sender = sms.getOriginatingAddress();

// Upload SMS to C2 Server
uploadSmsToC2(sender, body);

// If SMS contains "verification code" or other key words, intercept the broadcast so user cannot see it
if (is2FACode(body)) {
abortBroadcast();
}
}
}
}

```

- **资源解密**: 有时 C2 地址被加密存储在 `assets` 下的图片或文本文件中，或者使用 DGA (域名生成算法) 动态生成。
- **Native 分析**: 越来越多的木马将 C2 地址和通信逻辑隐藏在 SO 库中。

2. **通信协议**:

- **HTTP/HTTPS**: 抓包分析 POST 请求。
- **WebSocket**: 用于实时控制。
- **Telegram Bot API**: 很多新型木马利用 Telegram Bot 作为 C2，因为 Telegram 的流量通常不会被防火墙拦截，且 HTTPS 难以解密。

- **Frida Hook 示例 (拦截 Telegram API)\*\***:
  ```javascript
  // Assume malware uses OkHttp
  var OkHttpClient = Java.use("okhttp3.OkHttpClient");
  OkHttpClient.newCall.implementation = function (request) {
    var url = request.url().toString();
    if (url.includes("api.telegram.org")) {
      console.log("[!] Detected Telegram C2 Communication: " + url);
    }
    return this.newCall(request);
  };
  ```

```

木马作者也会使用各种手段防止被逆向：
* **模拟器检测**: 检查 `Build.FINGERPRINT`, `Build.MODEL` 等。
* **加壳**: 使用免费或商业的加固服务。
* **动态加载**: 核心 `dex` 文件被加密存储，运行时动态解密加载 (DexClassLoader)。
___
## 总结

分析银行木马的关键在于理解其**攻击链 (Kill Chain)**：
1. **Infection**: 诱导安装。
2. **Persistence**: 获取无障碍权限、保活。
3. **Stealing**: 覆盖攻击窃取凭证、拦截短信。
4. **Exfiltration**: 将数据回传 C2。

逆向工程师的任务是阻断这一链条，提取 IOC (Indicators of Compromise，如 C2 域名、文件 Hash)，并协助开发查杀策略。
```

<!-- 03-Case-Studies/case_music_apps.md -->

# 案例研究：音乐 App

音乐类 App 是非常典型的逆向分析目标。其核心场景通常围绕着 VIP 会员特权、音频数据加密和客户端风控策略。本案例将模拟对一个典型音乐 App 的分析过程。

---

## 核心分析目标

1. **解锁 VIP 功能**: 免费收听付费歌曲、下载无损音质、去除广告、使用专属皮肤等。
2. **音频数据提取**: 分析加密的音频文件格式（如 `ncm`, `qmcflac`），提取出可播放的 `mp3` 或 `flac` 文件。
3. **API 分析**: 分析其歌曲搜索、歌单获取、评论区等 API，为第三方工具或爬虫提供支持。

---

## 案例：分析 VIP 歌曲的播放流程

### 第 1 步：定位切入点

- **目标\*\***: 找到判断用户是否为 VIP 以及歌曲是否为付费歌曲的关键代码。

1. **界面分析**: 在 App 中播放一首需要 VIP 的歌曲，通常会弹出一个"开通 VIP"的提示框。这个提示框是绝佳的切入点。
2. **寻找关键词**: 使用 `jadx-gui` 反编译 APK，搜索与弹窗内容相关的字符串，例如"仅限 VIP"、"开通会员"等。
3. **交叉引用**: 对找到的字符串进行交叉引用，定位到显示这个弹窗的代码。你很可能会找到一个类似 `showVipDialog()` 的方法。
4. **回溯调用栈**: 继续对 `showVipDialog()` 进行交叉引用，向上回溯。通常，你会找到一个包含了核心判断逻辑的函数，其伪代码可能如下：

```java
void onPlayButtonClick(Song song) {
// isVip() determines from user information
// song.isPaywalled() determines from song information
if (!isVip() && song.isPaywalled()) {
showVipDialog();
return;
}
// ...execute playback logic...
startPlayback(song);
}

```

- **目标\*\***: 绕过 VIP 判断，让 App 认为我们是 VIP 用户。

最直接的方法是 Hook 负责判断用户身份的函数。

```javascript
Java.perform(function () {
  // Assume UserInfo class manages user information
  var UserInfo = Java.use("com.example.music.model.UserInfo");

  // Directly hook isVip method to always return true
  UserInfo.isVip.implementation = function () {
    console.log("Bypassing VIP check, returning true.");
    return true;
  };

  // Some apps may also verify VIP expiration time
  UserInfo.getVipExpireTime.implementation = function () {
    // Return a timestamp far in the future
    return new Date(2099, 11, 31).getTime();
  };
});
```

- 请求的 URL 中带有 `quality=flac` 或 `hires` 等参数。

- 服务器返回的响应 `Content-Type` 可能不是 `audio/mpeg`，而是一些自定义的类型如 `application/octet-stream`。

- 下载下来的文件（例如，`song.ncm`）无法用标准播放器播放。

2. **定位解密代码**: 这是最关键的一步。数据解密逻辑通常在 Native 层（`.so` 文件）以提高性能和逆向难度。

- **关键词搜索**: 在 IDA Pro 或 Ghidra 中打开相关的 `.so` 文件，搜索 `aes`, `cbc`, `decrypt`, `RC4` 等加密算法相关的字符串。

- **JNI 入口**: 从 Java 层调用 Native 代码需要通过 JNI (Java Native Interface)。在 Java 代码中寻找 `native` 关键字声明的函数，例如 `private native byte[] decryptAudio(byte[] encryptedData, int core);`。这个函数名就是你在 `.so` 文件中要找的符号。

- **Hook Native 函数**: 一旦定位到 JNI 函数（如 `Java_com_example_music_player_NativeDecoder_decryptAudio`），就可以使用 Frida 进行 Hook，观察其输入和输出。

```javascript
Interceptor.attach(
  Module.findExportByName(
    "libaudiodecrypt.so",
    "Java_com_example_music_player_NativeDecoder_decryptAudio"
  ),
  {
    onEnter: function (args) {
      // args[0] is JNIEnv*, args[1] is jclass, args[2] is encrypted data jbyteArray
      console.log("Entering decryptAudio...");
      // Can save encrypted data for subsequent offline analysis
      this.encryptedBuffer = args[2];
    },
    onLeave: function (retval) {
      // retval is the decrypted jbyteArray
      console.log("Leaving decryptAudio. Decrypted data pointer: " + retval);
      // Here you can read the memory pointed to by retval to get the decrypted PCM or MP3 data
    },
  }
);
```

通过动态分析，你已经能够获取到解密后的音频数据。但如果想开发一个独立的、离线的格式转换工具，就需要彻底理解其加密方案。

- **静态分析 Native 代码**: 在 Ghidra/IDA 中仔细分析 `decryptAudio` 函数的逻辑。它可能包含：
- **元数据解析**: 从加密文件头部读取歌曲 ID、专辑封面、比特率等信息。

- **密钥派生**: 使用一个固定的 Core Key 和从文件元数据中提取的 Nonce 来派生出每个文件唯一的 AES Key。

- **解密循环**: 循环读取加密的音频帧，使用 AES 或其他算法进行解密。
- **代码实现**: 使用 Python 的 `cryptography` 等库，将你在 Native 代码中看到的逻辑重新实现一遍。最终，你就能开发出一个可以将 `.ncm` 批量转换为 `.flac` 的工具。

---

## 主流平台加密方案实例

虽然通用的分析思路是一致的，但不同平台的具体实现细节各不相同。了解这些特征有助于更快地定位问题。

### 网易云音乐 (`.ncm`)

- **文件格式**: `.ncm` (Netease Cloud Music)

- **加密细节**: 采用 **AES + RC4** 的混合加密方案。

1. **元数据 (Meta)**: 文件中包含一块加密的元数据区域，其中含有歌曲名、专辑封面、AES Key 等信息。这块区域本身使用一个固定的 Meta Key 进行 AES-ECB 解密。
2. **音频数据 (Audio)**: 音频帧数据使用 AES-ECB 加密。解密所需的 AES Key 就存在于上一步解密后的元数据中。然而，最终的解密密钥流是通过一个类似 RC4-KSA 的算法，基于这个 AES Key 生成的。

- **逆向切入点**:
- 在 SO 库中搜索字符串 `ncm`, `core`, `meta`, `AES`, `RC4`。

- 其解密逻辑通常被封装在一个或多个专门的 Native 函数中。

### QQ 音乐 (`.qmcflac`, `.mflac`, `.qmc0`)

- **文件格式**: `.qmcflac`, `.qmc0`, `.qmc3`, `.mflac` 等。

- **加密细节**: **未使用标准加密算法**，而是一套自定义的字节**置乱 (Scramble)** 方案。
- 其核心是依赖一个巨大的**静态映射表 (Seed Map)**，这个表硬编码在 SO 文件中。

- 解密时，根据当前字节在文件中的偏移量，通过一个复杂的公式计算出在映射表中的索引，然后取出表中的值与加密字节进行运算（通常是异或）。
- **逆向切入点**:
- 由于没有使用标准算法，搜索加密关键词是无效的。

- 逆向的关键是在 SO 文件中**找到那个巨大的静态数组（映射表）**。

- 定位一个紧凑的循环，该循环体内部包含了复杂的偏移量计算和查表操作。

### 酷狗音乐 (`.kgm`, `.vpr`)

- **文件格式**: `.kgm` (Kugou Music), `.vpr`。

- **加密细节**: 同样是**自定义的置乱算法**，与 QQ 音乐思路相似，但实现不同。
- 依赖多个静态表（通常在开源项目中被称为 `table1`, `table2`）。

- 文件头包含了解密所需的关键信息，如密钥长度等。解密密钥由文件头信息和静态表共同派生。
- **逆向切入点**:
- 分析文件头的解析逻辑。

- 定位多个静态表，并还原其查表和密钥生成的算法。

### 酷我音乐 (`.kwm`)

- **文件格式**: `.kwm` (Kuwo Music)。

- **加密细节**: 采用相对简单的 **XOR 异或加密**。
- 解密密钥由一个**硬编码在 SO 中的静态密钥 (Base Key)** 与该歌曲的**资源 ID (`rid`)** 进行运算后得出。`rid` 是一个 uin64_t 类型的数字。

- 得到最终密钥后，对加密的音频数据进行逐字节异或即可完成解密。
- **逆向切入点**:
- 搜索关键词 `rid`, `kwm`。

- 定位一个逻辑相对简单的函数，其包含了获取 `rid`、与静态密钥进行运算、然后循环异或的过程。

## 总结

这个案例展示了从客户端功能绕过，到网络协议分析，再到核心加密算法逆向的完整流程。它结合了 Java 层的 Hook 和 Native 层的分析，是移动端逆向中非常具有代表性的场景。

<!-- 03-Case-Studies/case_social_media_and_anti_bot.md -->

# 案例研究：社交媒体 App 与风控

社交媒体 App（如 X、Instagram、TikTok）是爬虫和自动化工具最常光顾的地方。因此，这些 App 的开发者在客户端和服务器端都部署了极其复杂的安全与风控系统，以保护用户数据和平台生态。本案例将聚焦于这些 App 中常见的风控对抗技术。

---

## 核心分析目标

1. **API 签名算法逆向**: 几乎所有社交 App 的核心 API 请求都包含一个或多个签名参数（如 `X-Signature`, `X-Gorgon`）。这些签名是请求合法性的证明，也是逆向的主要目标。
2. **设备指纹分析**: 理解 App 如何收集设备信息（硬件、软件、网络环境等）来生成唯一的设备 ID (`device_id`)，并用于风控决策。
3. **业务风控逻辑分析**: 分析 App 在关键业务点（如注册、登录、点赞、评论）的风控策略，例如人机验证（滑块验证码、点图验证等）。

---

## 案例：分析一个典型社交 App 的 API 签名流程

## # 第 1 步：定位签名参数

- **目标\*\***: 识别出 API 请求中哪个参数是签名。

1. **网络抓包**: 使用 Charles 或 Mitmproxy 拦截 App 的网络流量。刷新首页动态（timeline）的请求是最好的分析对象，因为它通常包含了最复杂的签名。
2. **观察请求**: 查看一个典型的 API 请求，例如 `/api/v2/feed`。你会注意到其 URL 参数或请求头 (Headers) 中存在一些看起来像哈希值的、无明显语义的参数。

- **URL 参数**: `...&mas=01&as=a1...&ts=166...&ssmix=a...`

- **请求头**: `X-Gorgon: 0404...`, `X-Khronos: 166...`

- **URL 参数**: `...&mas=01&as=a1...&ts=166...&ssmix=a...`

- **请求头**: `X-Gorgon: 0404...`, `X-Khronos: 166...`

3. **参数筛选**: 通过多次重复请求，比较参数的变化规律。

- **不变的**: `device_id`, `os_version` 等，通常是设备指纹的一部分。

- **随时间变化的**: `ts`, `X-Khronos` 等，通常是时间戳。

- **每次请求都随机变化的**: `mas`, `as`, `X-Gorgon` 等，这些就是我们要找的核心签名。

- **不变的**: `device_id`, `os_version` 等，通常是设备指纹的一部分。

- **随时间变化的**: `ts`, `X-Khronos` 等，通常是时间戳。

- **每次请求都随机变化的**: `mas`, `as`, `X-Gorgon` 等，这些就是我们要找的核心签名。

## # 第 2 步：定位签名生成代码

- **目标\*\***: 找到在客户端生成这些签名的代码。这是整个流程中最关键、也最困难的一步。

1. **全局搜索**: 在 `jadx-gui` 中，全局搜索上一步识别出的参数名，如 `X-Gorgon`。如果运气好，你能直接定位到构建网络请求的地方。
2. **Hook 大法**: 如果搜索无果（通常是因为参数名在代码中被加密或混淆了），Frida Hook 将是你的主力武器。

- **Hook 网络库**: 从网络请求的源头入手。Hook `OkHttp` 的 `Request.Builder.addHeader` 或 `url()` 方法，打印出调用栈。
  ```javascript
  Java.perform(function () {
    var Builder = Java.use("okhttp3.Request$Builder");
    Builder.addHeader.implementation = function (name, value) {
      if (name === "X-Gorgon") {
        // Found it! Print call stack
        console.log("Found X-Gorgon being added: " + value);
        console.log(
          Java.use("android.util.Log").getStackTraceString(
            Java.use("java.lang.Exception").$new()
          )
        );
      }
      return this.addHeader(name, value);
    };
  });
  ```

```
3. **静态分析签名函数**: 定位到具体的签名函数后（例如，`SignHelper.getSign(params)`），在 Ghidra 或 IDA 中仔细分析其逻辑。

* **输入**: 它的输入通常是一个 `Map` 或 `List`，包含了所有要参与签名的业务参数（如 `user_id`）和设备指纹参数。

* **逻辑**: 函数内部逻辑通常是：
1. 对所有参数按 key 进行字典序排序。
2. 将排序后的 key-value 对拼接成一个长的字符串。
3. 将固定的盐（salt，可能硬编码或从 Native 获取）拼接到字符串的头部或尾部。
4. 对最终的字符串进行 MD5 或 HMAC-SHA256 哈希。
5. 有时还会进行额外的变换，如 Base64 编码或自定义的字节操作。

* **Native 混淆**: 越来越多的 App 将核心的签名算法（特别是盐）放到 `.so` 文件中，并使用 OLLVM 或 VMP 等技术进行混淆，以对抗静态分析。这时，就需要结合动态调试来一步步跟踪其执行流程。


* **输入**: 它的输入通常是一个 `Map` 或 `List`，包含了所有要参与签名的业务参数（如 `user_id`）和设备指纹参数。


* **逻辑**: 函数内部逻辑通常是：
1. 对所有参数按 key 进行字典序排序。
2. 将排序后的 key-value 对拼接成一个长的字符串。
3. 将固定的盐（salt，可能硬编码或从 Native 获取）拼接到字符串的头部或尾部。
4. 对最终的字符串进行 MD5 或 HMAC-SHA256 哈希。
5. 有时还会进行额外的变换，如 Base64 编码或自定义的字节操作。

1. 对所有参数按 key 进行字典序排序。
2. 将排序后的 key-value 对拼接成一个长的字符串。
3. 将固定的盐（salt，可能硬编码或从 Native 获取）拼接到字符串的头部或尾部。
4. 对最终的字符串进行 MD5 或 HMAC-SHA256 哈希。
5. 有时还会进行额外的变换，如 Base64 编码或自定义的字节操作。


* **Native 混淆**: 越来越多的 App 将核心的签名算法（特别是盐）放到 `.so` 文件中，并使用 OLLVM 或 VMP 等技术进行混淆，以对抗静态分析。这时，就需要结合动态调试来一步步跟踪其执行流程。


## # 第 3 步：模拟签名与自动化

* *目标**: 在你自己的 Python 或其他语言脚本中，重新实现签名算法，从而可以脱离 App 独立发起合法的 API 请求。

1. **代码复现**: 根据静态分析的结果，用 Python 完整地复现整个签名流程。每一个细节都要精确匹配，包括参数的排序、拼接方式、哈希算法等。
2. **获取设备参数**: 签名依赖的设备指纹参数（`device_id`, `install_id` 等）通常在 App 首次启动时生成并存储在本地。你需要 Hook 相关的函数来获取一套合法的设备参数，并在你的脚本中使用它们。
3. **风控对抗**:
* **滑块验证码**: 当服务器检测到你的请求异常时（例如，IP 地址异常、请求频率过高），它可能会返回一个需要进行人机验证的响应。你需要分析验证码的逻辑，这通常涉及到对一个 `JavaScript` 文件的逆向，分析其滑块轨迹加密算法。

* **请求频率**: 模拟真实用户的行为，在请求之间加入随机的延迟。

* **代理 IP**: 使用高质量的代理 IP 池来避免单个 IP 被封禁。

* **滑块验证码**: 当服务器检测到你的请求异常时（例如，IP 地址异常、请求频率过高），它可能会返回一个需要进行人机验证的响应。你需要分析验证码的逻辑，这通常涉及到对一个 `JavaScript` 文件的逆向，分析其滑块轨迹加密算法。


* **请求频率**: 模拟真实用户的行为，在请求之间加入随机的延迟。


* **代理 IP**: 使用高质量的代理 IP 池来避免单个 IP 被封禁。
___
## 总结

社交媒体 App 的逆向是典型的"数据在客户端，但由服务器规则校验"的场景。其核心是对抗，而不只是解密。

* **签名是核心**: 逆向签名算法是所有工作的基础。


* **动静结合**: 需要反复在静态分析（Ghidra/IDA）和动态验证（Frida）之间切换。


* **风控是持续的斗争**: 即使你成功逆向了签名，服务器端的风控策略也在不断演进。这是一个长期的、动态的攻防过程。
```

<!-- 03-Case-Studies/case_study_app_encryption.md -->

# 案例研究：主流 App 的加密签名机制解析

对主流 App 的 API 加密机制进行逆向分析，是检验和应用逆向工程综合能力的最佳实战。本案例研究将以常见的电商和社交类 App 为例，剖析其网络请求中核心加密字段和签名的生成逻辑，展示理论知识在实战中的应用。

> **免责声明**: 本文内容基于公开技术和过往分析经验的总结，旨在技术交流与学习。具体的加密实现会频繁更新，本文不保证与线上最新版本完全一致。

---

## 目录

- [案例研究：主流 App 的加密签名机制解析](#案例研究主流-app-的加密签名机制解析)
- [目录](#目录)

- [通用加密与签名模式](#通用加密与签名模式)

- [案例分析 1：电商 App (类拼多多模式)](#案例分析-1电商-app-类拼多多模式)
- [核心风控字段 (`anti_content`)](#核心风控字段-anti_content)

- [API 认证签名 (`sign`)](#api-认证签名-sign)
- [案例分析 2：社交 App (类小红书模式)](#案例分析-2社交-app-类小红书模式)
- [复杂的请求头签名 (`X-Sign`)](#复杂的请求头签名-x-sign)

- [设备信息上报 (`X-DeviceInfo`)](#设备信息上报-x-deviceinfo)
- [案例分析 3：字节跳动系 (抖音/TikTok)](#案例分析-3字节跳动系-抖音tiktok)

- [案例分析 4：快手](#案例分析-4快手)

- [案例分析 5：美团](#案例分析-5美团)

- [案例分析 6：阿里系 (淘宝、支付宝)](#案例分析-6阿里系-淘宝支付宝)

- [逆向分析通用策略](#逆向分析通用策略)

- [高级策略：黑盒 RPC 调用详解](#高级策略黑盒-rpc-调用详解)
- [什么是黑盒 RPC 调用？](#什么是黑盒-rpc-调用)

- [实现黑盒 RPC 的核心步骤](#实现黑盒-rpc-的核心步骤)
- [第一步：定位目标函数地址 (Finding the Function Pointer)](#第一步定位目标函数地址-finding-the-function-pointer)

- [第二步：分析函数原型 (Analyzing the Prototype)](#第二步分析函数原型-analyzing-the-prototype)

- [第三步：构建 RPC 服务端 (Frida Agent)](#第三步构建-rpc-服务端-frida-agent)

- [第四步：编写 RPC 客户端 (Python)](#第四步编写-rpc-客户端-python)
- [挑战与总结](#挑战与总结)

---

## 通用加密与签名模式

在分析具体案例前，我们先了解几种行业内通用的 API 保护模式：

- **请求体加密**：对整个 POST Body 进行对称（AES）或非对称（RSA）加密，保护数据内容隐私。

- **参数级加密**：仅对请求中的个别敏感字段（如密码、手机号）进行加密。

- **`sign` 签名机制**：**最核心、最普遍的模式**。通过对请求参数、时间戳、随机数等进行组合和哈希，生成一个签名值。服务器端会以同样的方式计算签名并进行比对，用于：
- **防篡改**：确保传输过程中的数据未被修改。

- **防重放**：通过加入时间戳或 Nonce，让签名一次有效。

- **身份认证**：验证请求是否由合法的客户端发出。

## 案例分析 1：电商 App (类拼多多模式)

## # 核心风控字段 (`anti_content`)

- **现象**: 在其 API 请求中，经常能看到一个名为 `anti_content` 的、内容极长的加密字段。

- **本质**: 它并非简单的 API 参数签名，而是一个由客户端 SDK 生成的、高度复杂的**风控数据包**。它更侧重于**识别"人"与"机器"**，而非认证 API 调用本身。

- **可能包含的内容**:
- **设备指纹**: 包含之前文档中提到的几乎所有硬件、软件和系统特征。

- **环境检测**: 是否 Root、是否越狱、是否使用了 Hook 框架 (Frida/Xposed)、是否在模拟器中运行。

- **传感器数据**: 在特定时间段内采集的加速度计、陀螺仪数据，用于判断设备是否在正常物理状态下。

- **行为数据**：用户的点击坐标、滑动轨迹等。
- **逆向挑战**: `anti_content` 的生成逻辑通常被封装在高度混淆的原生 SO 库中，并可能包含 `SVC` 系统调用等反分析技术。完整复现其算法的难度极高。

## # API 认证签名 (`sign`)

- **现象**: 除了 `anti_content`，请求参数中还有一个相对独立的 `sign` 字段。

- **目的**: 这个字段才是真正用于 API 级别认证的签名。

- **典型生成逻辑**:

1. 收集所有请求参数（GET Query Params 和 POST Form Body Params）。
2. 剔除 `sign` 字段本身。
3. 按参数名的 ASCII 字母顺序进行排序。
4. 将排序后的参数拼接成 `key=value&...` 的字符串（空值参数可能不参与拼接）。
5. 在拼接好的字符串**前后**或**中间**插入一个固定的密钥（App Secret / Salt），这个密钥通常硬编码在 SO 文件中。
6. 对最终的字符串进行 MD5 或 HMAC-SHA256 哈希，得到签名值。

## 案例分析 2：社交 App (类小红书模式)

## # 复杂的请求头签名 (`X-Sign`)

- **现象**: 认证信息不放在 URL 参数中，而是位于 HTTP 请求头，如 `X-Sign`, `X-T` (时间戳), `X-B3-TraceId` 等。

- **`X-Sign` 的构成**:
- **格式**: 通常是 `MD5(some_string)` 的形式。

- **`some_string` 的拼接方式**: `URL Path + Sorted Query Params + (POST Body Hash) + Token/Salt`。
- 这意味着，不仅 URL 参数，连 POST 的内容也参与了签名计算。

- 有时还会包含其他请求头的值。
- **动态 Salt**: 其签名用的密钥可能不是固定的，而是部分由服务器下发，或与时间戳、设备信息动态生成，这使得暴力破解和简单模拟请求变得非常困难。

## # 设备信息上报 (`X-DeviceInfo`)

- **现象**: 有一个专门的请求头，如 `X-DeviceInfo`，其内容是加密或 Base64 编码后的 JSON 字符串，里面是详细的设备指纹信息。

- **关联性**: 服务端的风控系统会将 `X-Sign` 和 `X-DeviceInfo` 进行强关联校验。
- 首先验证 `X-Sign` 是否合法。

- 然后解码 `X-DeviceInfo`，分析设备是否可信。

- 最后，可能会交叉验证，例如，某个版本的 App 是否可能运行在某个特定的 Android SDK 版本上，如果不匹配，则判定为异常。

## 案例分析 3：字节跳动系 (抖音/TikTok)

- **现象**: 其 API 请求中包含多个复杂的自定义请求头，如 `X-Gorgon`, `X-Khronos`, `X-Argus`, `X-Ladon`。请求体通常是经过 Protobuf 序列化后再加密的二进制数据。

- **核心逻辑**:
- **设备注册**: App 首次启动时会进行设备注册 (`/service/2/device_register/`)，获取服务器下发的 `device_id` 和 `install_id`。这两个 ID 是后续所有业务请求的身份基础。

- **多重签名系统**: `X-Gorgon` 是最核心的 API 请求签名，它将 URL、Cookie、POST Body 的哈希、设备指纹信息等多种因素混合计算而成。`X-Khronos` 是加密过的时间戳。这套体系确保了请求的来源、时效和完整性都可被验证。

- **Protobuf 序列化**: 大量使用 Protobuf 进行数据交换，相比 JSON，它更高效，但也增加了逆向难度，因为分析者需要先找到或还原 `.proto` 文件才能理解数据结构。

- **Cronet 网络库**: 使用 Google 的 Cronet 网络库进行网络请求，这使得常规的 OkHttp Hook 方法失效，必须深入到更底层的 `cronet.so` 或系统网络调用层面去进行 Hook。
- **逆向挑战**:
- **虚拟机保护 (VMP)**: 其核心 SO 库（如 `libmetasec_ml.so`, `libmsaoaidsec.so`）使用了行业顶级的 VMP 或其自研的虚拟机保护技术。这会将原始的 ARM 指令转换成虚拟机自定义的字节码，导致 IDA 等工具无法进行静态分析。

- **算法快速迭代**: 签名算法几乎每个版本都在变化，增加了长期维护的难度。

- **分析策略**: 鉴于 VMP 的存在，完全还原签名算法几乎是不可能的。业界主流的策略是**放弃算法还原，转向 RPC 调用**。即通过 Frida 等工具找到 SO 中负责计算签名的函数（无论是导出还是非导出函数），模拟其运行环境和参数，直接调用它来获取签名结果。

## 案例分析 4：快手

- **现象**: API 请求参数中包含 `sig` 和 `__NS_sig` 字段。请求体同样可能使用 Protobuf 序列化并加密。

- **核心逻辑**:
- **双签名体系**:
- `sig`: 一个相对传统的 API 签名，通常是对所有请求参数进行排序、拼接、加盐后进行 MD5 或 HMAC 哈希。

- `__NS_sig` (New Signature): 这是一个更复杂的风控签名，其计算过程融入了大量的设备指纹信息，用于对抗模拟器和脚本。
- **动态 Salt**: 在加密和签名过程中会使用到一个 `client_salt`，这个盐值并非固定，而是可能从 Protobuf 数据中动态获取，或者通过 JNI 调用 SO 库动态生成，这增加了模拟请求的难度。
- **逆向挑战**:
- 其核心 SO 库（如 `libcore.so`）经过了深度混淆，虽然可能不是 VMP 级别，但静态分析依然困难重重。

- 同样大量使用了 Protobuf，需要投入精力去逆向其数据结构。

## 案例分析 5：美团

- **现象**: API 请求中包含大量自定义请求头，如 `M-TraceId`。请求体被加密，并且能看到 `rohr` 和 `mtgsig` 等新一代的风控及签名字段。

- **核心逻辑**:
- **中心化风控库**: 核心保护逻辑高度集中在 `libmtguard.so` 中，该库负责生成几乎所有的签名和风控数据。

- **请求压缩与加密**: 请求体可能会先用 `zlib` 或 `gzip` 进行压缩，然后再通过 AES 进行加密，服务器端需要先解密再解压。

- **`rohr` & `mtgsig`**: 这是其新一代的风控签名体系。`rohr` 是一个风控令牌，包含了加密的设备和环境信息；`mtgsig` 是 API 签名，它在计算时会依赖 `rohr` 的部分数据，两者强关联。

- **统一请求网关**: 有一个统一的 API 网关，加密和签名逻辑相对集中，便于统一管理和迭代。
- **逆向挑战**:
- `libmtguard.so` 是逆向的重中之重，其内部逻辑复杂且经过混淆。

- 风控维度极广，除了常规的设备指纹，还可能包括地理位置、历史行为、网络环境等，对伪造设备画像的一致性要求非常高。

## 案例分析 6：阿里系 (淘宝、支付宝)

- **现象**: API 请求中包含一个 `sign` 字段，并且还有一个名为 `wua` 的神秘参数。网络请求通过自有的 MTop 网关进行分发。

- **核心逻辑**:
- **统一网关 (MTop)**: 阿里系 App 使用自研的 MTop (Mobile Taobao Open Platform) 作为统一无线网关。所有的 API 请求都经过这个网关，便于统一进行签名校验、安全风控和流量调度。

- **安全核心 (`libsgmain.so`)**: 所有的安全逻辑都高度集成在 `libsgmain.so` 以及一系列 `libsgxxx.so` (如 `libsgsecuritybody.so`) 的安全组件中。这是阿里安全的核心技术结晶，负责签名 `sign` 和风控参数 `wua` 的生成。

- **`sign` 签名**: 签名算法极其复杂。它不仅包含 API 的业务参数，还会将时间戳、App 版本、Token 以及从安全 SDK 中获取的大量设备指纹信息一同参与计算。其拼接和加密方式非常规整。

- **`wua` 风控参数**: 这是一个类似于 `anti_content` 的黑盒风控参数。它由 `libsgmain.so` 采集海量的设备信息（包括硬件、系统、网络、传感器、环境检测等）后，经过高度混淆的算法加密生成。`wua` 的生成难度和重要性甚至高于 `sign`。服务端会将 `sign` 和 `wua` 进行强关联校验。

- **ACCS 通道**: 使用自研的 ACCS (Alibaba Cloud Channel Service) 长连接通道，基于 HTTP/2，进一步封装了网络请求，使得常规抓包和分析变得更加困难。
- **逆向挑战**:
- **顶级混淆**: `libsgmain.so` 及其依赖库使用了自研的、多层次的复杂混淆技术，静态分析几乎无法下手，是业界公认的最难逆向的 SO 库之一。

- **动态加载与反调试**: 安全组件的加载和初始化过程非常隐晦，并伴有大量的反调试和环境检测手段，给动态调试和分析设置了极高的门槛。

- **黑盒 RPC 调用**: 与字节系类似，业界的主流策略是放弃算法还原。逆向的终极目标是在 SO 文件中找到一个类似 `main` 的函数入口，通过 RPC 调用的方式，传入请求参数，获取计算好的 `sign` 和 `wua` 值。定位这个入口需要极其深厚的动态调试和二进制分析功底。

## 逆向分析通用策略

1. **静态分析 (Jadx/Ghidra)**:

- **全局搜索**：搜索关键词，如 `sign`, `encrypt`, 以及上述案例中的 `anti_content`, `X-Sign`, `X-Gorgon`, `mtgsig`, `wua` 等。

- **定位网络库**: 现代 App 大多使用 OkHttp。搜索 `okhttp3.Interceptor` 的实现类，因为加密和签名的逻辑常常在自定义拦截器中统一处理。

- **追踪 JNI 调用**: 找到 Java 层调用 Native 方法的地方，重点关注那些函数名可疑（如 `getSignFromC`）、参数多且包含字节数组的函数。

2. **动态分析 (Frida)**:

- **Hook 加密算法**: 这是最有效的方法。Hook `java.security.MessageDigest.digest` 和 `javax.crypto.Mac.doFinal`，打印它们的输入（即被签名的明文）和调用堆栈，可以瞬间定位到生成签名的代码位置。

- **Hook 网络请求**: Hook `okhttp3.Request.Builder` 的 `build()` 方法，或 `okhttp3.OkHttpClient` 的 `newCall` 方法，可以 dump 出所有即将发出的网络请求的完整信息（URL, Headers, Body），用于和抓包结果对比。

* **Hook SO 函数**: 定位到核心 SO 库后，用 Frida `Interceptor.attach` 直接 Hook 目标导出函数，观察其输入和输出。对于非导出函数，可以通过基地址加偏移的方式进行 Hook。

---

## 高级策略：黑盒 RPC 调用详解

在分析字节、阿里等顶级厂商的加固 SO 时，会发现其核心逻辑受 VMP (虚拟机保护) 或自研虚拟机保护。这意味着原始的 ARM 指令被转换成了一套自定义的、无法被常规反汇编工具解析的字节码。在这种情况下，试图完全理解并"白盒"地还原签名算法，几乎是不可能的。

因此，业界的分析思路从"算法还原"转向"算法利用"，这便是**黑盒 RPC (Remote Procedure Call) 调用**。

## # 什么是黑盒 RPC 调用？

核心思想是：**不再关心函数内部是如何实现的，而是将其作为一个整体，一个黑盒子。我们只关心它的输入和输出。**
我们将通过 Frida 等工具，在 App 的运行时环境中，强行调用这个黑盒函数，让它为我们计算出所需的结果（如 `sign`, `wua`），然后将结果返回给外部的自动化程序。

这就好比我们使用一个网站的 API，我们不需要它的源码，只需要知道它的 URL、参数和返回值格式就能使用它。在这里，SO 里的函数就是那个"API"。

## # 实现黑盒 RPC 的核心步骤

### 第一步：定位目标函数地址 (Finding the Function Pointer)

这是最困难、最耗时的一步，需要深厚的动态调试功底。

1. **从 JNI 入口开始**: 从 Java 层调用 Native 方法的地方（`JNI` 函数）作为起点。
2. **主动调用与插桩**: 使用 Frida 主动调用该 JNI 函数，并使用 `Stalker` 等指令级跟踪工具，记录下执行轨迹。
3. **执行流分析**: 分析 Stalker 产生的巨大日志，或使用 `Unicorn Engine` 等模拟执行工具进行分析，理清复杂的跳转和计算逻辑，最终找到一个"干净"的函数入口——它接收相对原始的业务参数，返回最终的签名结果。这个函数的地址（通常是 SO 基址 + 偏移量）就是我们的目标。

### 第二步：分析函数原型 (Analyzing the Prototype)

确定目标函数的输入和输出。

- **输入参数**: 在上一步找到的函数调用点下断点，观察调用前各寄存器（ARM32 下重点关注 R0-R3）和栈上的值，推断出函数的参数类型、数量和顺序。参数可能是字符串、字节数组、结构体指针等。

- **返回值**: 在函数返回点下断点，观察 R0 寄存器的值，确定函数的返回值是什么（通常是一个指向结果字符串的指针或一个状态码）。

### 第三步：构建 RPC 服务端 (Frida Agent)

编写一个 Frida 脚本，将定位到的原生函数封装成一个可供远程调用的服务。

```javascript
// agent.js
// 1. Get SO base address
const baseAddr = Module.findBaseAddress("libsgmain.so");
// 2. Calculate target function absolute address
// This 0x123456 is the function offset found through great effort in step one
const targetFuncPtr = baseAddr.add(0x123456);

// 3. Define function based on the prototype analyzed in step two
// Assume function prototype is: char* func(char* input1, int input2)
const nativeFunc = new NativeFunction(targetFuncPtr, "pointer", [
  "pointer",
  "int",
]);

// 4. Expose interface using rpc.exports
rpc.exports = {
  // Define a remote call interface named getSign
  getSign: function (param1, param2) {
    console.log("RPC call received, invoking native function...");
    // Prepare parameters for native function
    const input1Ptr = Memory.allocUtf8String(param1);

    // Call native function
    const resultPtr = nativeFunc(input1Ptr, param2);

    // Read and return result
    return resultPtr.readUtf8String();
  },
};
```

# client.py

import frida
import sys

def main():

# Connect to frida-server on device

device = frida.get_usb_device()

# Attach to target App process

pid = device.spawn(["com.example.app"])
session = device.attach(pid)

# Load Frida Agent script

with open("agent.js") as f:
script_code = f.read()
script = session.create_script(script_code)
script.load()

# Prepare parameters

api_params_str = "param1=value1&param2=value2"
some_int_value = 123

# Call RPC interface like calling a local function

print("Calling RPC function: getSign...")
result_sign = script.exports.get_sign(api_params_str, some_int_value)

print(f"Successfully got sign: {result_sign}")

# Can use the obtained sign to construct and send network requests here

# ...

session.detach()

if **name** == '**main**':
main()

```

通过黑盒 RPC，我们可以绕过对 VMP 等复杂技术的直接对抗，将逆向的重点放在寻找和调用关键函数上，这在当今的高级移动安全攻防中是一种务实且高效的策略。
```

<!-- 03-Case-Studies/case_unity_games.md -->

# 案例研究：Unity 游戏逆向 (Il2Cpp)

Unity 是目前最流行的移动游戏引擎之一。现代 Unity 游戏通常使用 Il2Cpp 脚本后端，将 C# 代码转换为 C++ 代码并编译为 Native 库 (`libil2cpp.so`)。这使得传统的 Java/Smali 逆向方法失效，需要全新的工具和思路。

---

## 核心架构与文件结构

一个典型的 Unity Il2Cpp 游戏包含以下关键文件：

1. **`lib/armeabi-v7a/libil2cpp.so`**: 这是游戏的核心逻辑库。所有的 C# 脚本（玩家控制、游戏逻辑、网络通信）都被编译到了这里。
2. **`assets/bin/Data/Managed/global-metadata.dat`**: 这是 Il2Cpp 的元数据文件。它包含了被转换前的 C# 类名、方法名、字段名以及它们在 `libil2cpp.so` 中的偏移地址。**这是逆向的关键钥匙**。
3. **`lib/armeabi-v7a/libmain.so`** (或 `libunity.so`): Unity 引擎的运行时库，通常不需要修改。

---

## 逆向流程

### 第 1 步：元数据提取 (Metadata Dumping)

由于 `libil2cpp.so` 是剥离了符号表 (stripped) 的二进制文件，直接用 IDA 打开只能看到成千上万个无名函数 (`sub_xxxx`)。我们需要结合 `global-metadata.dat` 来还原这些函数的真实名称。

- **工具\*\***: [Il2CppDumper](https://github.com/Perfare/Il2CppDumper)

1. 将 APK 解压，提取出 `libil2cpp.so` 和 `global-metadata.dat`。
2. 运行 `Il2CppDumper.exe <libil2cpp.so> <global-metadata.dat>`。
3. 工具会生成：

- **`dump.cs`**: 还原后的 C# 伪代码，展示了所有类、字段和方法结构。
- **`script.py`**: 用于 IDA Pro 的 Python 脚本，可以自动重命名 IDA 中的函数。
- **`ghidra.py`**: 用于 Ghidra 的脚本。
- **`DummyDll/`**: 生成的空 DLL 文件，可以用 dnSpy 打开查看类结构。

### 第 2 步：静态分析与定位

使用 `dnSpy` 打开生成的 Dummy DLL，或是直接阅读 `dump.cs`，我们可以像阅读源码一样浏览游戏的类结构。

- **寻找切入点\*\***:
- **货币修改**: 搜索 `Coin`, `Gem`, `Money`, `Currency` 等关键词。寻找 `AddCoin()`, `GetMoney()`, `UpdateCurrency()` 等方法。
- **无敌/高伤害**: 搜索 `PlayerController`, `BattleManager`, `Health`, `Damage`。寻找 `TakeDamage()`, `OnHit()` 等方法。
- **内购破解**: 搜索 `IAP`, `Purchase`, `Store`, `Payment`。寻找 `OnPurchaseSuccess()`, `VerifyReceipt()` 等方法。

- **示例\*\***:
  在 `dump.cs` 中找到如下类：

```csharp
public class PlayerData {
public int coin;
public int gem;
public void AddCoin(int amount); // Address: 0x123456
public void SubCoin(int amount); // Address: 0x123460
}

```

// Il2Cpp Hook Template

var soName = "libil2cpp.so";
var baseAddr = Module.findBaseAddress(soName);

if (baseAddr) {
// Target function offset: 0x123456 (AddCoin)
var addCoinFunc = baseAddr.add(0x123456);

Interceptor.attach(addCoinFunc, {
onEnter: function(args) {
// args[0] is 'this' pointer (PlayerData instance)
// args[1] is amount (coin count to add)

console.log("[*] AddCoin called");
console.log(" Amount: " + args[1].toInt32());

// Modify parameter: force add 99999 regardless of game logic
args[1] = ptr(99999);
},
onLeave: function(retval) {
console.log("[*] AddCoin finished");
}
});
} else {
console.log("[-] libil2cpp.so not found!");
}

```
// Use frida-il2cpp-bridge
Il2Cpp.perform(() => {
// 1. Find class
const PlayerData = Il2Cpp.domain.assembly("Assembly-CSharp").image.class("PlayerData");

// 2. Hook method (auto process offset, no need to calculate manually)
PlayerData.method("SubCoin").implementation = function (amount) {
console.log("[*] SubCoin called with amount: " + amount);
// Prevent coin deduction (do nothing)
return;
};

// 3. Manually call method
// Assume we want to call PlayerData.Instance.AddCoin(1000)
// Need to find static instance or current instance first

// Trace all PlayerData instance creation
Il2Cpp.traceClass(PlayerData);
});

```

- **对抗\*\***:
- **Hook 加载函数**: 游戏必须在运行时解密 metadata 才能正常运行。Hook `libil2cpp.so` 中加载 metadata 的函数（通常是 `il2cpp::vm::MetadataCache::Register` 或相关初始化函数），Dump 出解密后的内存内容。
- **分析解密逻辑**: 逆向 `libil2cpp.so` 的初始化流程，找到解密 metadata 的算法（通常是 XOR 或 AES），写脚本还原。

### 2. 函数地址混淆 / 动态计算

- **现象\*\***: Il2CppDumper 导出的地址与内存中的实际地址不符。
- **对抗\*\***:
- 这通常是因为游戏在运行时动态修改了函数指针。
- 使用 **Frida 的扫描功能**，根据机器码特征（Pattern Scanning）来定位函数，而不是依赖固定的偏移。

### 3. 反调试与完整性校验

- **现象\*\***: 附加 Frida 后游戏崩溃或闪退。
- **对抗\*\***:
- 参考 "Anti-Debugging" 章节，隐藏 Frida 特征，Bypass TracerPid 检测。
- 使用 Magisk + Riru + Il2CppDumper (Zygisk 版) 在系统层面进行 Dump，规避应用层检测。

---

## 总结

Unity Il2Cpp 逆向的核心在于**还原符号**。只要拿到了正确的 `global-metadata.dat` 和 `libil2cpp.so` 的映射关系，剩下的工作就变成了标准的逻辑分析和 Native Hook。熟练掌握 Il2CppDumper 和 Frida 是搞定这类游戏的关键。

<!-- 03-Case-Studies/case_video_apps_and_drm.md -->

# 案例研究：视频 App 与 DRM

视频类 App 的逆向分析是移动端安全领域最具挑战性的方向之一，其核心难点在于数字版权管理（DRM）技术的对抗。本案例将深入探讨视频 App，特别是涉及 DRM 的分析思路。

---

## 核心分析目标

1. **视频流分析**: 解析视频播放的网络协议，如 `HLS` (`.m3u8`) 和 `DASH` (`.mpd`)，并提取视频分片。
2. **解锁 VIP 功能**: 绕过付费墙，观看 VIP 专属影片或解锁更高清晰度（如 1080p, 4K）。
3. **DRM 对抗**: 理解 DRM 的工作原理，并尝试获取解密视频所需的密钥。**（注意：这通常是极其困难的，且可能涉及法律风险。）**

---

## 案例：分析一个使用 Widevine DRM 的视频播放流程

### 第 1 步：视频流协议分析

- **目标\*\***: 找到描述视频信息的清单文件 (`.m3u8` 或 `.mpd`)。

1. **网络抓包**: 打开 Charles 或 Mitmproxy，启动目标视频 App 并播放一个影片。
2. **过滤请求**: 在抓包结果中，使用关键词 `m3u8` 或 `mpd` 进行过滤。你很快就能定位到一个请求，其 URL 类似于 `https://.../video.mpd`。
3. **分析清单文件**:

- **DASH (`.mpd`)**: 这是一个 XML 文件，描述了视频的各种信息，包括不同的分辨率、音轨、字幕轨道以及加密信息。

- **HLS (`.m3u8`)**: 这是一个文本文件。主 `m3u8` 文件可能指向多个子 `m3u8` 文件，每个子文件代表一种特定的码率（清晰度），并包含了该码率下所有视频分片（`.ts` 文件）的 URL。

在清单文件中，你会找到一个关键的标签，表明内容是受保护的，例如：

```xml
<!-- DASH MPD inEncryptInformation -->
<ContentProtection schemeIdUri="urn:uuid:edef8ba9-79d6-4ace-a3c8-27dcd51d21ed" cenc:default_KID="...value...">
<cenc:pssh>...</cenc:pssh>
</ContentProtection>

```

### 第 2 步：理解 DRM 工作流程 (Widevine)

Google 的 Widevine 是 Android 平台上最主流的 DRM 方案。它分为三个安全级别 (L1, L2, L3)，其中 L1 安全性最高。

1. **App 请求播放**: App 从视频清单中解析出 `pssh` 数据。
2. **获取许可证 (License)**: App 将 `pssh` 数据发送给系统的 `MediaDrm` API，生成一个许可证请求（License Request）。然后，App 将这个请求发送到视频服务提供商的许可证服务器。
3. **服务器验证**: 许可证服务器验证请求的合法性（例如，验证用户的 VIP 身份），然后返回一个加密的许可证（Encrypted License）。
4. **解密密钥**: App 将加密的许可证提供给 `MediaDrm` API。这一步是关键：

- **L1 安全级别**: 许可证的处理和内容密钥的解密完全在处理器的可信执行环境（TEE）中进行。Android 操作系统和 App 本身都无法访问到解密后的密钥。视频帧的解密也在 TEE 中完成，然后直接输出到屏幕，不会在 App 的内存中暴露。

- **L3 安全级别**: 在没有 TEE 支持的设备上，这些操作都在软件层面完成。因此，L3 是理论上最容易被攻击的。

### 第 3 步：逆向分析与信息获取

由于 L1 的硬件级保护，直接获取内容密钥（Content Key）几乎是不可能的。因此，分析的重点转向了许可证的获取过程。

- **目标\*\***: 拦截 App 与许可证服务器之间的通信，获取许可证请求和响应。

1. **定位许可证请求代码**:

- 搜索 `MediaDrm`, `getKeyRequest`, `provideKeyResponse` 等 `android.media` 包中的 DRM 相关 API。

- 使用 Frida Hook 这些方法，可以打印出 `pssh`、许可证请求和加密的许可证响应。

```javascript
Java.perform(function () {
  var MediaDrm = Java.use("android.media.MediaDrm");

  // Hook getKeyRequest method to capture license requests
  MediaDrm.getKeyRequest.implementation = function (
    scope,
    initData,
    mimeType,
    keyType,
    optionalParameters
  ) {
    console.log("Intercepting getKeyRequest...");
    // initData is the pssh
    console.log("PSSH (initData):", bytesToHex(initData));

    var keyRequest = this.getKeyRequest(
      scope,
      initData,
      mimeType,
      keyType,
      optionalParameters
    );
    // keyRequest is a complex object, needs further parsing
    // ...
    return keyRequest;
  };

  // Hook provideKeyResponse method to capture encrypted license
  MediaDrm.provideKeyResponse.implementation = function (scope, response) {
    console.log("Intercepting provideKeyResponse...");
    // response is the encrypted license obtained from the server
    console.log("Encrypted License (response):", bytesToHex(response));

    return this.provideKeyResponse(scope, response);
  };
});
function bytesToHex(arr) {
  /* ... a function to convert byte array to hex string ... */
}
```

3. **CDM (内容解密模块) 分析**: Widevine 的 L3 级 CDM 是一个原生库（`.so` 文件），负责处理白盒加密的逻辑。对这个 `.so` 文件进行深入的静态和动态分析，是理论上还原出设备密钥（Device Key）的唯一途径，这也是 CDM Challenge 等比赛的核心。这是一个极其复杂和耗时的过程。

---

## 主流平台 DRM 与加密方案实例

### 国内平台 (优酷、爱奇艺、腾讯视频、芒果 TV)

国内主流视频平台在加密策略上通常采用**"自研加密方案 + 标准 DRM"**的混合模式。

- 对于拥有全球版权的影视剧（如好莱坞大片），它们会使用行业标准的 Widevine DRM。

- 对于大量的自制剧、综艺等内容，它们更倾向于使用自研的加密方案，其核心是对 HLS 协议进行改造。

- **通用模式：保护 HLS 密钥的获取过程\*\***

1. **视频流**: 普遍使用 HLS (`.m3u8`) 协议。
2. **加密算法**: `.m3u8` 文件中会声明视频分片（`.ts` 文件）使用 `AES-128-CBC` 加密。
3. **核心保护**: **视频数据本身的加密算法是标准的，但获取解密密钥（Key）的过程是高度定制和保护的。**

- `.m3u8` 文件本身不是静态的，而是通过一个需要复杂签名的 API 动态生成的。

- `#EXT-X-KEY` 标签中指向的密钥 URL (`key.key`) 也不是一个能直接访问的地址，访问它同样需要正确的 Cookie、Referer 和加密参数。

4. **逆向关键**:

- **定位播放 API**: 逆向的重点是找到 App 中负责请求视频播放信息的 API。这个 API 的请求参数通常包含视频 ID、清晰度、以及一个类似我们在上一章分析过的、包含设备指纹和时间戳的 `sign` 或 `token`。

- **模拟合法请求**: 只要能够成功模拟这个 API 的调用，就能获取到一个包含了有效密钥 URL 的 `.m3u8` 文件。拿到密钥后，就可以使用标准的 `AES-128` 算法解密 `.ts` 文件并合并成一个完整的视频。

- **腾讯视频的 `vkey`**: 一个典型的例子是腾讯视频，其播放 API 中需要一个至关重要的 `vkey` 参数，这个参数的生成算法就封装在客户端的 SO 库中。

### 国外平台 (Netflix, YouTube, Hulu, HBO Max)

国外主流视频平台，特别是内容提供商，严格且深度地依赖标准化的 DRM 体系。逆向的焦点**完全不在于分析视频文件格式或算法，而在于 DRM 许可证的获取流程**。

#### Netflix / Hulu / HBO Max

- **DRM 方案**: 在 Android 上无一例外地使用 Google Widevine，在苹果设备上使用 FairPlay。

- **安全级别**: 对于高清内容（HD, 4K），强制要求设备的 Widevine 安全级别为 L1。这意味着密钥交换和内容解密全程在硬件 TEE 中完成，App 和操作系统均无法触及明文密钥。

- **许可证请求保护**: 逆向的唯一着眼点是 App 发起许可证请求的过程。
- 这个请求被多种方式保护，例如 Netflix 使用自研的 **MSL (Message Security Layer)** 协议对许可证请求本身进行二次封装和加密。

- App 会采集大量设备指纹信息，连同用户的身份凭证一起，用于生成许可证请求。服务端的风控系统会严格校验这些信息，以确保请求来自于一个合法的、未被篡改的官方 App 客户端。
- **逆向结论**: 在 L1 保护下，通过逆向 App 来获取视频解密密钥以进行离线下载是**几乎不可能**的。分析的主要意义在于理解其架构和安全强度。

#### YouTube

YouTube 的情况比较特殊，它需要区分对待：

- **付费内容 (YouTube Premium / 电影)**: 与 Netflix 类似，使用标准的 Widevine DRM 进行保护。

- **普通 UGC 内容**: 大部分视频没有使用 DRM 加密，但使用了另一种巧妙的保护方式——**动态 URL 签名**。
- **现象**: 使用 `youtube-dl` 等工具下载视频时，会看到它有一个"deciphering signature"的过程。

- **原理**: 视频流的 URL 中包含一个 `s` 或 `sig` 参数，这个签名是由一段混淆过的 JavaScript 代码（在 Web 端）或 Native 代码（在 App 端）动态生成的。该算法将视频的 `cipher` (一段加密字符串) 和其他参数作为输入，输出一个解密的签名。

- **逆向关键**: 逆向的重点不再是 DRM，而是**找到并还原那段负责计算签名的 JavaScript/Native 函数**。由于代码经过了高度混淆，这依然是一项具有挑战性的工作。

## 总结

视频 App 的 DRM 逆向是一场与硬件和复杂密码学协议的艰苦斗争。与音乐 App 不同，其核心目标通常不是开发一个"下载器"，而是理解其安全体系的强度和弱点。

- 对于普通分析，重点是**拦截和理解信令**（清单文件、许可证请求/响应）。

- 对于高级研究，核心是**攻击 L3 的 CDM 实现**，但这需要极高的逆向工程和密码学知识。

这个领域的攻防水平代表了整个行业安全对抗的顶峰。

<!-- 04-Reference/Advanced/android_sandbox_implementation.md -->

# android 沙箱技术与实现指南

Android 沙箱技术，通常也被称为"虚拟化引擎"或"App 多开框架"，是一种在单个 Android 设备上创建隔离环境以运行其他应用程序的技术。它允许一个"宿主"应用程序在自己的进程空间内加载并运行一个"插件"应用程序，同时对插件应用的所有系统交互进行拦截和管理。

这项技术的核心应用包括：应用多开、无感知隐私保护、自动化测试、以及免安装运行 App。

---

## 目录

1. [**核心概念：沙箱 vs. 虚拟机**](#核心概念沙箱-vs-虚拟机)
2. [**沙箱实现原理详解**](#沙箱实现原理详解)

- [**1. 类加载 (Class Loading)**](#1-类加载-class-loading)

- [**2. 组件生命周期管理 (Component Lifecycle)**](#2-组件生命周期管理-component-lifecycle)

- [**3. 系统服务 Hook (API Hooking via Binder Proxy)**](#3-系统服务-hook-api-hooking-via-binder-proxy)

- [**4. 资源管理 (Resource Management)**](#4-资源管理-resource-management)

3. [**实现一个最小化沙箱的步骤**](#实现一个最小化沙箱的步骤)
4. [**知名开源项目参考**](#知名开源项目参考)
5. [**挑战与局限**](#挑战与局限)

---

### 核心概念：沙箱 vs. 虚拟机

- **虚拟机 (VM)**: 创建一个完整的、独立的操作系统，拥有自己的内核和系统服务，资源开销巨大。

- **Android 沙箱**: 不创建独立的操作系统。它运行在宿主 App 的进程中，与宿主共享同一个 Android 系统内核和运行时。它通过**API Hooking**的方式，为插件 App 创造了一个"虚拟的"运行环境，拦截和重定向其对系统服务的请求。本质上是一种**进程内虚拟化**。

---

### 沙箱实现原理详解

实现一个 Android 沙箱需要解决四大核心问题：

#### 1. 类加载 (Class Loading)

由于插件 App 并未被系统"安装"，其代码不能通过常规的 `PathClassLoader` 加载。

- **解决方案**: 使用 `DexClassLoader`。宿主 App 需要创建一个 `DexClassLoader` 实例，将插件 APK 的路径和宿主 App 的私有数据目录（用于存放优化后的 ODEX 文件）作为参数传入。这样，宿主 App 就能加载并实例化插件 App 中的任意类。

#### 2. 组件生命周期管理 (Component Lifecycle)

插件 App 的组件（Activity, Service 等）并没有在宿主 App 的 `AndroidManifest.xml` 中注册，因此无法被系统直接启动。

- **解决方案**: **占坑 (Stub/Proxy Component)**。

1. **在宿主中预注册**: 在宿主 App 的 `AndroidManifest.xml` 中预先注册一系列"占坑"的组件，例如 `StubActivity1`, `StubActivity2`, `StubService1`...
2. **请求拦截与替换**: 当插件 App 想要启动一个组件时（例如 `startActivity(intentToPluginActivity)`），这个请求会被我们下一步要讲的系统服务 Hook 拦截到。
3. **移花接木**: 拦截到请求后，沙箱框架会创建一个指向"占坑"Activity 的新 `Intent` (`intentToStubActivity`)，并将原始的 `Intent` 作为 extra 数据附加到新 `Intent` 上。然后，它会用这个新的 `Intent` 去调用原始的系统服务。
4. **生命周期委托**: 系统启动了 `StubActivity`。在 `StubActivity` 的 `onCreate` 方法中，它会从 extra 中恢复出原始 `Intent`，得知自己需要扮演哪个插件 Activity 的角色。然后，它使用第一步的 `DexClassLoader` 实例化真正的插件 Activity，并手动调用其 `onCreate`, `onStart`, `onResume` 等所有生命周期方法，将自己的生命周期"委托"给插件 Activity。

#### 3. 系统服务 Hook (API Hooking via Binder Proxy)

这是整个沙箱技术**最核心、最复杂**的部分。插件 App 的所有行为，如启动 Activity、发送广播、访问数据库，都是通过调用系统服务完成的。我们必须拦截这些调用。

- **目标**: Android 的各种 `XXXManager`（如 `ActivityManager`, `PackageManager`）实际上都是通过 Binder IPC 与系统服务 (`ActivityManagerService`, `PackageManagerService`) 通信的。我们需要 Hook 的就是这个通信的接口。

- **解决方案**: **动态代理 (Dynamic Proxy)**。

1. **定位 Binder 接口**: 使用 Java 反射找到 `ActivityManager` 等类中持有的 `IActivityManager` 类型的 Binder 代理对象。
2. **创建代理对象**: 使用 `java.lang.reflect.Proxy.newProxyInstance()` 方法，为原始的 `IActivityManager` Binder 代理对象创建一个动态代理。
3. **实现 `InvocationHandler`**: 在 `InvocationHandler` 的 `invoke` 方法中，我们可以拦截所有对 `IActivityManager` 接口的方法调用（如 `startActivity`, `getRunningAppProcesses` 等）。
4. **请求重定向**: 在 `invoke` 方法中，判断当前请求是否来自插件 App。如果是，就不执行原始的系统调用，而是将其重定向到我们自己的沙箱管理逻辑中（例如，执行上述的"占坑"流程）。如果不是，就调用原始的 Binder 方法，保证宿主 App 自身功能正常。

#### 4. 资源管理 (Resource Management)

插件 App 需要加载自己的布局、字符串、图片等资源。

- **解决方案**: 创建一个自定义的 `Resources` 对象。

1. 通过 `AssetManager` 的隐藏方法 `addAssetPath()`，将插件 APK 的路径添加到 `AssetManager` 中。
2. 基于这个 `AssetManager` 创建一个新的 `Resources` 对象。
3. 在创建插件 Activity 等组件时，将这个自定义的 `Resources` 对象注入到其 `Context` 中，从而让它可以访问到自己的资源。

---

### 实现一个最小化沙箱的步骤

以下是一个启动插件 Activity 的极简流程：

1. **准备**:

- 一个宿主 App。

- 一个插件 App 的 APK 文件。

- 在宿主 App 的 `AndroidManifest.xml` 中注册一个 `StubActivity`。

2. **Hook AMS**: 在宿主 App 启动时（如 `Application.onCreate`），通过反射和动态代理，Hook `IActivityManager`。
3. **加载插件**: 当用户触发"启动插件"操作时：

- 创建 `DexClassLoader` 和自定义 `Resources` 对象。

- 构造一个指向插件主 Activity 的 `Intent`。

- 调用 `startActivity(pluginIntent)`。

4. **拦截与替换**:

- `IActivityManager` 的动态代理 `invoke` 方法拦截到这个 `startActivity` 调用。

- `invoke` 方法发现这是一个插件 `Intent`，于是将其替换为一个指向 `StubActivity` 的 `Intent`，并将原 `Intent` 存入 extra。

5. **启动与还原**:

- 系统正常启动 `StubActivity`。

- `StubActivity` 在 `onCreate` 中，解析出插件 Activity 的类名。

- 使用 `DexClassLoader` 反射创建插件 Activity 实例。

- 将自定义 `Resources` 等注入插件 Activity 的 `Context`。

- 手动调用插件 Activity 的 `onCreate()` 等生命周期方法。

至此，插件 Activity 的界面就显示出来了，但它实际上是运行在 `StubActivity` 的"壳"里。

---

### 知名开源项目参考

从零开始构建一个完整的沙箱框架非常困难，以下项目是极佳的学习资源：

- **VirtualApp**: 最著名的 Android 沙箱项目之一，代码结构清晰，是学习原理的绝佳范例。

- **DroidPlugin**: 由 360 开发的早期沙箱项目，对四大组件的支持非常完整。

---

### 挑战与局限

- **兼容性**: Android 版本每次大更新，大量系统服务内部实现会改变，需要持续适配。

- **复杂性**: 需要处理四大组件、文件系统、Content Provider、系统广播等方方面面的虚拟化。

- **Native Code**: 对包含 JNI/Native 代码的 App 支持起来更复杂，可能需要对 so 文件的加载和符号解析进行 Hook。

- **厂商 ROM**: 不同手机厂商对 Android 系统的魔改，也可能导致沙箱在某些设备上失效。

<!-- 04-Reference/Advanced/aosp_and_system_customization.md -->

# AOSP 与 android 系统裁剪

Android 开源项目（AOSP）是 Android 操作系统的开源基础。能够编译和修改 AOSP 是进行深度系统级定制、安全研究和 ROM 开发的核心技能。本节将介绍 AOSP 的基本概念、编译流程以及常见的系统裁剪技术。

---

## 1. AOSP 基础与编译

### a) AOSP 源码同步

编译 AOSP 的第一步是获取其庞大的源代码树。

1. **环境准备**:

- 一个强大的 Linux 构建服务器（推荐 Ubuntu LTS），至少需要 16GB RAM 和 300GB 的可用磁盘空间。

- 安装必要的依赖包，如 `git`, `curl`, `python`, `Java SDK` 等。

2. **获取 Repo 工具**: `Repo` 是 Google 开发的、基于 Git 的代码库管理工具，用于管理 AOSP 中数百个不同的 Git 仓库。

   ```bash

   ```

# Download Repo Tool

mkdir -p ~/.bin
curl https://storage.googleapis.com/git-repo-downloads/repo > ~/.bin/repo
chmod a+x ~/.bin/repo
export PATH=~/.bin:$PATH

````
    ```bash
# 创建工作目录
mkdir aosp && cd aosp

# 初始化源码仓库，指定分支（For example，android-12.0.0_r1）
repo init -u https://android.googlesource.com/platform/manifest -b android-12.0.0_r1 --depth=1

# StartSynchronization源码（ThisWillis一Long process）
repo sync -c -j8

````

- `--depth=1`: 只同步最新的 commit，大幅减少下载量。

- `-c`: 只同步当前分支。

- `-j8`: 使用 8 个线程并行同步。

### b) 编译流程

1. **设置环境**:
   ```bash
   source build/envsetup.sh
   ```

````

2. **选择目标 (Lunch)**:
    ```bash
lunch

````

- `aosp_arm64`: 目标设备架构（64 位 ARM）。

- `eng`: 构建变体（Engineering），包含最多的调试工具，权限为 root，适合开发和逆向。其他还有 `user`（发布版）和 `userdebug`（带 root 和调试功能的用户版）。

3. **开始编译 (Make)**:
   ```bash
   m
   ```

````

4. **编译产物**:
编译完成后，所有的系统镜像文件都存放在 `out/target/product/<device_name>/` 目录下，主要包括：

* `system.img`: 系统分区镜像。

* `vendor.img`: 厂商分区镜像。

* `boot.img`: 启动分区镜像，包含内核和 ramdisk。

* `userdata.img`: 用户数据分区镜像。
___
## 2. 系统裁剪与定制技术

拥有了编译 AOSP 的能力后，你就可以对系统进行任意的修改。

### a) 预置与删除 App

* **路径**: App 通常定义在 `packages/apps/` 目录下。

* **修改 `PRODUCT_PACKAGES`**: 在特定设备的 `device.mk` 文件中（例如 `device/<vendor>/<device_name>/device.mk`），有一个名为 `PRODUCT_PACKAGES` 的变量。
* **增加 App**: 将你想要预置的 App 的模块名添加到这个列表中。

* **删除 App**: 从这个列表中移除你不想要的系统 App（如 `Calendar`, `Camera2`）的模块名。

### b) 修改 Framework 层

这是更深度的定制，可以改变 Android 系统的核心行为。

* **路径**: Framework 核心代码位于 `frameworks/base/`。

* **示例：修改状态栏逻辑**:
1. 找到负责状态栏管理的 `SystemUI` App (`frameworks/base/packages/SystemUI/`)。
2. 修改其中的 Java 或 XML 文件，例如，改变时钟的显示格式或电池图标。
3. 重新编译 `SystemUI` 模块：`m SystemUI`。
4. 只编译模块并生成新的 `system.img`：`m snod` (`make systemimage-nodeps`)。

### c) 定制内核 (Kernel)

AOSP 默认不包含内核源码。你需要从 Google 的内核源码仓库或设备厂商的开源站点单独下载内核源码，并进行编译。

1. **获取内核源码**: `git clone https://android.googlesource.com/kernel/common.git`
2. **配置与编译**:
    ```bash
# 使用与 AOSP 匹配的交叉编译工具链
export CROSS_COMPILE=.../aarch64-linux-android-4.9/bin/aarch64-linux-android-
# 配置内核
make defconfig
# 编译内核镜像
make

````

### d) 制作完整的自定义 ROM

一个完整的自定义 ROM（如 LineageOS）的制作过程，就是上述所有技术的综合应用：

1. 同步 AOSP 基础代码。
2. 集成特定设备的驱动和配置文件（Device Tree）。
3. 修改 Framework，添加自定义功能（如高级重启菜单）。
4. 移除或替换系统 App。
5. 集成定制的内核。
6. 编译并打包成一个可供用户刷写的 `zip` 文件。

---

## android Linker 与 SO 加载原理

### Linker architecture 与工作原理

Android 系统使用动态链接器 (`/system/bin/linker` 或 `/system/bin/linker64`) 来加载和链接共享库 (.so 文件)。

#### 系统架构

```
Runtime.loadLibrary()
↓
DexPathList.loadLibrary()
↓
nativeLoad() [JNI]
↓
android_dlopen_ext()
↓
do_dlopen() [linker]
↓
find_library_internal()
↓
load_library() → link_image()

```

static soinfo* find_library_internal(android_namespace_t* ns,
const char* name,
int rtld_flags,
const android_dlextinfo* extinfo,
soinfo* needed_by) {
// 1. CheckisNo 已 Load
soinfo* si = find_loaded_library_by_soname(ns, name);
if (si != nullptr) {
return si;
}

// 2. in/atNamespaceInSearch
std::string realpath;
if (!find_library_in_namespace(ns, name, &realpath)) {
return nullptr;
}

// 3. LoadLibraryFile
return load_library(ns, realpath.c_str(), rtld_flags, extinfo, needed_by);
}

```
const char* name,
int rtld_flags,
const android_dlextinfo* extinfo,
soinfo* needed_by) {
// 1. OpenELFFile
int fd = open(name, O_RDONLY | O_CLOEXEC);

// 2. ParseELF头
ElfReader elf_reader(name, fd, file_offset, file_size);
if (!elf_reader.Load(extinfo)) {
return nullptr;
}

// 3. Createsoinfo结构
soinfo* si = soinfo_alloc(ns, realpath, &file_stat, rtld_flags, extinfo);

// 4. MapMemory段
if (!si->prelink_image()) {
return nullptr;
}

return si;
}

```

const soinfo_list_t& local_group,
const android_dlextinfo\*\* extinfo) {
// 1. Parse 动态段
if (!phdr_table_get_dynamic_section(phdr, phnum, load_bias, &dynamic, &dynamic_flags)) {
return false;
}

// 2. Process 依赖 Library
for (ElfW(Dyn)_ d = dynamic; d->d_tag != DT_NULL; ++d) {
if (d->d_tag == DT_NEEDED) {
const char_ library_name = get_string(d->d_un.d_val);
soinfo\*\* lsi = find_library(library_name, ...);
}
}

// 3. 重定位 Process
if (!relocate(global_group, local_group)) {
return false;
}

// 4. Call 构造 Function
call_constructors();

return true;
}

```
0x7001000000 ├─────────────────┤
│ .rodata (R) │ Only读Data段
0x7002000000 ├─────────────────┤
│ .data (RW) │ 可读写Data段
0x7003000000 ├─────────────────┤
│ .bss (RW) │ 未InitializeData段
0x7004000000 └─────────────────┘

```

size_t phdr_count,
ElfW(Addr) load_bias) {
for (size_t i = 0; i < phdr_count; ++i) {
const ElfW(Phdr)\*\* phdr = &phdr_table[i];
if (phdr->p_type != PT_LOAD) continue;

int prot = PFLAGS_TO_PROT(phdr->p_flags);
if (mprotect(reinterpret_cast<void\*\*>(seg_page_start + load_bias),
seg_page_end - seg_page_start, prot) < 0) {
return -1;
}
}
return 0;
}

```
__attribute__((constructor))
void anti_debug_check() {
// DetectionFrida
if (access("/data/local/tmp/frida-server", F_OK) == 0) {
_exit(1);
}

// DetectionDebug器
if (ptrace(PTRACE_TRACEME, 0, 1, 0) == -1) {
_exit(1);
}

// Detection虚拟机环境
check_emulator_files();
}

```

void\*\* handle = dlopen(NULL, RTLD_NOW);

// DetectionFrida 符号
if (dlsym(handle, "frida_agent_main") != NULL) {
\_exit(1);
}

// DetectionXposed 符号
if (dlsym(handle, "xposed_bridge") != NULL) {
\_exit(1);
}
}

```
Dl_info info;
dladdr((void*)check_code_integrity, &info);

// CalculateCode段哈希
uint32_t current_hash = calculate_hash(info.dli_fbase, TEXT_SIZE);
if (current_hash != EXPECTED_HASH) {
_exit(1);
}
}

```

var ptrace = Module.findExportByName("libc.so", "ptrace");
if (ptrace) {
Interceptor.attach(ptrace, {
onEnter: function(args) {
var request = args[0].toInt32();
if (request === 0) { // PTRACE_TRACEME
console.log("[+] ptrace(PTRACE_TRACEME) blocked");
args[0] = ptr(-1); // Modify parameter to make it fail
}
},
onLeave: function(retval) {
retval.replace(ptr(0)); // Return success
}
});
}

```
Interceptor.attach(dlsym, {
onEnter: function(args) {
this.symbol_name = args[1].readCString();
},
onLeave: function(retval) {
var blocked_symbols = ["frida_agent_main", "xposed_bridge"];
if (blocked_symbols.includes(this.symbol_name)) {
console.log("[+] Hiding symbol: " + this.symbol_name);
retval.replace(ptr(0));
}
}
});

```

Interceptor.attach(mprotect, {
onEnter: function(args) {
var addr = args[0];
var size = args[1].toInt32();
var prot = args[2].toInt32();

console.log("[+] mprotect called: " + addr + ", size: " + size + ", prot: " + prot);

// Prevent removal of execute permission
if ((prot & 0x4) == 0) { // PROT_EXEC
args[2] = ptr(prot | 0x4);
}
}
});

```
Interceptor.attach(access, {
onEnter: function(args) {
var path = args[0].readCString();
var sensitive_paths = [
"/data/local/tmp/frida-server",
"/system/xbin/su",
"/system/app/Superuser.apk"
];

if (sensitive_paths.some(p => path.includes(p))) {
console.log("[+] Blocking access to: " + path);
args[0] = Memory.allocUtf8String("/non/existent/path");
}
}
});

```

from elftools.elf.elffile import ELFFile

def inject_init_array(elf_path, hook_function_addr):
with open(elf_path, 'r+b') as f:
elf = ELFFile(f)

# 查找.init_array 段

init_array = elf.get_section_by_name('.init_array')
if init_array:

# in/atExistingFunction 指针 AfterAddNewFunctionAddress

f.seek(init_array['sh_offset'] + init_array['sh_size'])
f.write(hook_function_addr.to_bytes(8, 'little'))

```
// 1. 找到TargetsoLoad基址
void* base_addr = dlopen("target.so", RTLD_NOLOAD);

// 2. ParseELF头找到.init_array段
ElfW(Ehdr)* ehdr = (ElfW(Ehdr)*)base_addr;
ElfW(Shdr)* shdr = (ElfW(Shdr)*)((char*)base_addr + ehdr->e_shoff);

// 3. ModifyMemoryProtected
mprotect(init_array_addr, init_array_size, PROT_READ | PROT_WRITE);

// 4. AddFunction指针
*(void**)(init_array_addr + init_array_size) = target_function;

// 5. RestoreProtected
mprotect(init_array_addr, init_array_size, PROT_READ);
}

```

class AntiDebugChecker {
private:
static bool check_debugger_presence() {
return ptrace(PTRACE_TRACEME, 0, 1, 0) == -1;
}

static bool check_frida_artifacts() {
const char\*\* frida_files[] = {
"/data/local/tmp/frida-server",
"/data/local/tmp/frida-agent-64.so"
};

for (auto file : frida_files) {
if (access(file, F_OK) == 0) return true;
}
return false;
}

static bool check_memory_maps() {
FILE\*\* fp = fopen("/proc/self/maps", "r");
char line[512];
while (fgets(line, sizeof(line), fp)) {
if (strstr(line, "frida") || strstr(line, "gum-js-loop")) {
fclose(fp);
return true;
}
}
fclose(fp);
return false;
}

public:
static void comprehensive_check() {
if (check_debugger_presence() ||
check_frida_artifacts() ||
check_memory_maps()) {

// Execute 对抗 Measure
execute_countermeasures();
}
}
};

```
std::thread([]{
while (true) {
std::this_thread::sleep_for(std::chrono::seconds(5));
AntiDebugChecker::comprehensive_check();
}
}).detach();
}

```

- 深入理解 Android Framework 的工作原理，为 Hook 和逆向提供更底层的视角。

- 通过修改系统来绕过应用层的反分析技术，实现"降维打击"。

<!-- 04-Reference/Advanced/aosp_device_modification.md -->

# 基于 AOSP 的深度改机技术指南

在 Android 安全和逆向工程领域，"改机"指的是修改设备的各种硬件和软件标识符，以绕过应用程序的安全检测或实现隐私保护。虽然使用 Xposed 或 Frida 等 Hook 框架可以在应用层实现改机，但这些方法容易被检测。**基于 AOSP (Android Open Source Project) 源码进行修改，是从系统层面伪造设备指纹的终极手段**，因为 App 获取到的信息是由系统本身"真实"地提供的。

本文旨在提供一个关于如何通过修改 AOSP 源码来实现深度改机的技术框架和思路。

---

## 目录

1. [**核心思想：应用层 Hook vs. 系统层修改**](#核心思想应用层-hook-vs-系统层修改)
2. [**准备工作**](#准备工作)
3. [**关键参数定位与修改**](#关键参数定位与修改)

- [**Build Info (build.prop)**](#build-info-buildprop)

- [**硬件参数 (IMEI, MAC, Android ID)**](#硬件参数-imei-mac-android-id)

- [**系统属性 (System Properties)**](#系统属性-system-properties)

- [**内核参数 (Serial Number)**](#内核参数-serial-number)

- [**Build Info (build.prop)**](#build-info-buildprop)

- [**硬件参数 (IMEI, MAC, Android ID)**](#硬件参数-imei-mac-android-id)

- [**系统属性 (System Properties)**](#系统属性-system-properties)

- [**内核参数 (Serial Number)**](#内核参数-serial-number)

4. [**编译与刷机**](#编译与刷机)
5. [**优势与挑战**](#优势与挑战)

---

## # 核心思想：应用层 Hook vs. 系统层修改

| 特性         | 应用层 Hook (Xposed/Frida)                   | AOSP 系统层修改                                              |
| :----------- | :------------------------------------------- | :----------------------------------------------------------- |
| **原理**     | 在 App 运行时，拦截 API 调用，返回伪造结果。 | 直接修改 Android 框架层源码，使 API **本身**就返回伪造的值。 |
| **效果**     | 较好，但可被检测。                           | **极好**，效果彻底。                                         |
| **检测难度** | 容易被反 Hook、反调试技术检测到。            | 极难被检测，因为对 App 来说系统行为是"原生"的。              |
| **实现难度** | 相对较低，只需编写 Hook 脚本。               | **非常高**，需要编译整个 Android 系统。                      |
| **适用性**   | 通用性强，适用于大多数设备。                 | 通常只适用于 AOSP 支持良好的设备（如 Google Pixel）。        |

- **结论**: AOSP 改机的本质是**构建一个"出厂设置"就是伪装状态的自定义操作系统\*\***。

---

## # 准备工作

1. **硬件要求**:

- 一台高性能的 PC（至少 16GB RAM，推荐 32GB 或更高）。

- 大容量高速硬盘（SSD，至少 500GB 可用空间）。

- 一台受 AOSP 官方支持的设备（如 Google Pixel 系列），用于刷机验证。
- 一台高性能的 PC（至少 16GB RAM，推荐 32GB 或更高）。

- 大容量高速硬盘（SSD，至少 500GB 可用空间）。

- 一台受 AOSP 官方支持的设备（如 Google Pixel 系列），用于刷机验证。

2. **软件环境**:

- Linux 操作系统（推荐 Ubuntu LTS 版本）。

- 熟悉 Android 编译环境，安装好 `repo` 和所有必需的依赖库。
- Linux 操作系统（推荐 Ubuntu LTS 版本）。

- 熟悉 Android 编译环境，安装好 `repo` 和所有必需的依赖库。

3. **AOSP 源码**:

- 根据你的目标设备和 Android 版本，初始化并同步对应的 AOSP 源码仓库。

- 根据你的目标设备和 Android 版本，初始化并同步对应的 AOSP 源码仓库。

---

## # 关键参数定位与修改

### Build Info (build.prop)

这些是描述设备型号、品牌、制造商等最基础的信息。

- **定位**: 这些值通常定义在 `device/` 目录下的特定于设备的 `*.mk` makefile 文件中，或者在 `build/make/target/product/` 下的通用产品定义文件中。

- **修改示例**:
- 打开 `device/<vendor>/<product_name>/device.mk` 或类似文件。

- 找到并修改以下变量：
  ```makefile
  PRODUCT_MODEL := Pixel 8 Pro
  PRODUCT_BRAND := Google
  PRODUCT_NAME := my_custom_device
  PRODUCT_DEVICE := generic
  PRODUCT_MANUFACTURER := MyCompany
  ```

```


### 硬件参数 (IMEI, MAC, android ID)
这些是更敏感、更核心的设备标识符。修改它们需要深入到 Framework 层的 Java 代码和 JNI。

* **IMEI (Telephony)**:
* **定位**: `frameworks/opt/telephony/src/java/com/android/internal/telephony/Phone.java` 或相关的 `*SubInfo.java` 文件。

* **修改思路**: 找到 `getImei()` 或类似方法，在其中硬编码或返回一个动态生成的伪造 IMEI。
* **定位**: `frameworks/opt/telephony/src/java/com/android/internal/telephony/Phone.java` 或相关的 `*SubInfo.java` 文件。


* **修改思路**: 找到 `getImei()` 或类似方法，在其中硬编码或返回一个动态生成的伪造 IMEI。
* **MAC Address (Wi-Fi)**:
* **定位**: `frameworks/base/wifi/java/android/net/wifi/WifiInfo.java`。

* **修改思路**: 找到 `getMacAddress()` 方法。注意，在高版本 Android 中，该方法可能返回一个固定的、非真实的 MAC 地址。需要找到其更底层的实现，可能在 `wpa_supplicant` 或 Wi-Fi 驱动的 JNI 接口中。
* **定位**: `frameworks/base/wifi/java/android/net/wifi/WifiInfo.java`。


* **修改思路**: 找到 `getMacAddress()` 方法。注意，在高版本 Android 中，该方法可能返回一个固定的、非真实的 MAC 地址。需要找到其更底层的实现，可能在 `wpa_supplicant` 或 Wi-Fi 驱动的 JNI 接口中。
* **Android ID**:
* **定位**: `frameworks/base/services/core/java/com/android/server/pm/Settings.java` 中的 `getStringForUser()` 方法，结合 `android.provider.Settings.Secure.ANDROID_ID` 的实现。

* **修改思路**: 找到生成和存储 Android ID 的逻辑，将其替换为返回一个固定的或每次启动都随机生成的值。

* **定位**: `frameworks/base/services/core/java/com/android/server/pm/Settings.java` 中的 `getStringForUser()` 方法，结合 `android.provider.Settings.Secure.ANDROID_ID` 的实现。


* **修改思路**: 找到生成和存储 Android ID 的逻辑，将其替换为返回一个固定的或每次启动都随机生成的值。


### 系统属性 (System Properties)
App 通过 `android.os.SystemProperties.get()` 获取各种系统属性。

* **定位**: `frameworks/base/core/java/android/os/SystemProperties.java` 及其对应的 JNI 实现 `frameworks/base/core/jni/android_os_SystemProperties.cpp`。


* **修改思路**: 直接在 `SystemProperties.cpp` 的 `native_get` 方法中进行拦截。判断传入的属性名，如果是目标属性（如 `ro.serialno`），则返回一个伪造的值，否则执行原始逻辑。


### 内核参数 (Serial Number)
一些底层信息（如 CPU 序列号）直接由 Linux 内核通过 `/proc` 文件系统暴露。

* **定位**: 内核源码中的 `arch/<arch>/kernel/setup.c` 或相关驱动文件。


* **修改思路**:
1. 下载与 AOSP 版本匹配的内核源码。
2. 找到向 `/proc/cpuinfo` 或 `/proc/serial` 等文件写入信息的代码。
3. 修改这部分逻辑，使其输出伪造的信息。
4. 重新编译内核 (`boot.img`)。

1. 下载与 AOSP 版本匹配的内核源码。
2. 找到向 `/proc/cpuinfo` 或 `/proc/serial` 等文件写入信息的代码。
3. 修改这部分逻辑，使其输出伪造的信息。
4. 重新编译内核 (`boot.img`)。
___
## # 编译与刷机

1. **设置环境**: `source build/envsetup.sh`
2. **选择目标**: `lunch aosp_<device_name>-userdebug` (例如 `lunch aosp_husky-userdebug` 对应 Pixel 8 Pro)
3. **开始编译**: `make -j$(nproc)` (这会花费数小时)
4. **刷机**:
* 将设备置于 `fastboot` 模式。

* 执行 `fastboot flashall -w`，这将刷写所有编译生成的镜像 (`system.img`, `boot.img`, `vendor.img` 等)。

* 将设备置于 `fastboot` 模式。


* 执行 `fastboot flashall -w`，这将刷写所有编译生成的镜像 (`system.img`, `boot.img`, `vendor.img` 等)。
___
## # 优势与挑战

### 优势
* **彻底性**: 从系统根源上改变设备指纹，几乎无法被应用层技术检测。


* **稳定性**: 不会像 Hook 框架那样因为应用更新或加固而失效。


* **性能好**: 没有额外的 Hook 开销，所有修改都是原生代码。


### 挑战
* **技术门槛极高**: 需要深入理解 AOSP 源码结构、编译系统和 Linux 内核。


* **时间成本高**: 全量编译一次 AOSP 通常需要数小时。


* **设备限制**: 强依赖于有良好 AOSP 支持和开放驱动的设备。


* **维护困难**: 每次 Android 版本更新，都需要重新进行源码适配和修改。
```

<!-- 04-Reference/Advanced/minimal_android_rootfs.md -->

# 构建最小化 android 系统 (RootFS) 指南

构建一个完整的 AOSP (Android Open Source Project) 耗时巨大且对硬件要求苛刻。而构建一个最小化的 Android RootFS (Root File System) 是一个能让我们深刻理解 Android 启动流程和核心组件的绝佳实践。其目标是创建一个仅包含最基本组件、能够引导 Linux 内核并最终启动一个交互式 Shell 的系统。

本文将指导你完成这一过程，主要使用 QEMU 作为目标平台。

---

## 目录

- [构建最小化 Android 系统 (RootFS) 指南](#构建最小化-android-系统-rootfs-指南)
- [目录](#目录)
- [核心概念与启动流程](#核心概念与启动流程)

- [最小系统的核心组件](#最小系统的核心组件)

- [构建步骤详解](#构建步骤详解)
- [Step 1: 准备环境与工具链](#step-1-准备环境与工具链)

- [Step 2: 获取并编译 Linux 内核](#step-2-获取并编译-linux-内核)

- [Step 3: 构建最小化 RootFS](#step-3-构建最小化-rootfs)

- [Step 4: 打包并运行](#step-4-打包并运行)
- [从 Shell 到 Zygote：下一步是什么？](#从-shell-到-zygote下一步是什么)

- [目录](#目录)
- [核心概念与启动流程](#核心概念与启动流程)

- [最小系统的核心组件](#最小系统的核心组件)

- [构建步骤详解](#构建步骤详解)
- [Step 1: 准备环境与工具链](#step-1-准备环境与工具链)

- [Step 2: 获取并编译 Linux 内核](#step-2-获取并编译-linux-内核)

- [Step 3: 构建最小化 RootFS](#step-3-构建最小化-rootfs)

- [Step 4: 打包并运行](#step-4-打包并运行)
- [从 Shell 到 Zygote：下一步是什么？](#从-shell-到-zygote下一步是什么)

- [核心概念与启动流程](#核心概念与启动流程)

- [最小系统的核心组件](#最小系统的核心组件)

- [构建步骤详解](#构建步骤详解)
- [Step 1: 准备环境与工具链](#step-1-准备环境与工具链)

- [Step 2: 获取并编译 Linux 内核](#step-2-获取并编译-linux-内核)

- [Step 3: 构建最小化 RootFS](#step-3-构建最小化-rootfs)

- [Step 4: 打包并运行](#step-4-打包并运行)
- [Step 1: 准备环境与工具链](#step-1-准备环境与工具链)

- [Step 2: 获取并编译 Linux 内核](#step-2-获取并编译-linux-内核)

- [Step 3: 构建最小化 RootFS](#step-3-构建最小化-rootfs)

- [Step 4: 打包并运行](#step-4-打包并运行)
- [从 Shell 到 Zygote：下一步是什么？](#从-shell-到-zygote下一步是什么)

---

## # 核心概念与启动流程

1. **Bootloader**: 设备上电后执行的第一段代码，负责初始化硬件并加载 Linux 内核到内存。
2. **Kernel**: 内核被加载后，开始初始化各种驱动、内存管理等，然后挂载一个临时的根文件系统 (ramdisk)。
3. **`init` 进程**: 内核在用户空间启动的第一个进程，其 PID 为 1。它是所有其他用户空间进程的祖先。
4. **`init.rc`**: `init` 进程会解析这个配置文件，根据其中的指令执行动作，如挂载文件系统、设置系统属性、启动服务等。

我们的目标就是创建一个极简的 RootFS，其中包含 `init` 程序和一个能被它启动的 Shell。

## # 最小系统的核心组件

一个能启动到 Shell 的最小 Android 系统，必须包含以下组件：

- **Linux Kernel**: 操作系统的核心。

- **`init`**: 用户空间的守护神，来自 AOSP 源码 `system/core/init`。

- **C 库**: `libc.so` (C 标准库), `libm.so` (数学库)。所有原生程序都依赖它。

- **动态链接器**: `linker` 或 `linker64`，用于加载 `.so` 动态库。

- **Shell**: `sh`，我们的交互界面，通常由 `toybox` 或 `toolbox` 提供。

- **`init.rc`**: 一个最简单的配置文件。

- **基本目录结构**: `/dev`, `/proc`, `/sys`, `/system/bin`。

---

## # 构建步骤详解

### Step 1: 准备环境与工具链

你需要一个 Linux 环境（如 Ubuntu）和用于交叉编译的工具链。最简单的方法是从 AOSP 预编译库中获取。

```bash
# Download AOSP prebuilt aarch64 (ARM64) Toolchain
git clone https://android.googlesource.com/platform/prebuilts/gcc/linux-x86/aarch64/aarch64-linux-android-4.9

# WillToolchainPathAdd toEnvironment variables
export PATH=$(pwd)/aarch64-linux-android-4.9/bin:$PATH
export CROSS_COMPILE=aarch64-linux-android-

```

git clone https://android.googlesource.com/kernel/common.git
cd common

# Switch to 一 Stable branch

git checkout android-4.14

# 配置内核

export ARCH=arm64
make defconfig

# 编译内核

make -j$(nproc)

# CompileSuccessAfter，会 in/at arch/arm64/boot/ Directory 下 Generate Image.gz 内核 File

```
mkdir -p my_rootfs/{dev,proc,sys,system/bin,system/lib64}
cd my_rootfs

```

这一步比较复杂，因为需要从完整的 AOSP 源码中单独编译。一个简化的方法是**直接从一个现有的 Android 系统或 AOSP 编译产物中提取这些预编译好的二进制文件**。

- 从 AOSP 编译产物 `out/target/product/<device>/system/` 中找到以下文件：
- `bin/linker64` -> 复制到 `my_rootfs/system/bin/`

- `bin/init` -> 复制到 `my_rootfs/`

- `bin/toybox` -> 复制到 `my_rootfs/system/bin/`

- `lib64/libc.so`, `lib64/libm.so` -> 复制到 `my_rootfs/system/lib64/`
- 为 `toybox` 创建各种命令的软链接：
  ```bash
  cd my_rootfs/system/bin
  for cmd in $(./toybox); do
  ln -s toybox $cmd
  done
  cd ../../
  ```

````
在 `my_rootfs/` 目录下创建一个 `init.rc` 文件，内容如下：

```rc
# init.rc for minimal android

on early-init
mount tmpfs tmpfs /dev
mkdir /dev/pts
mount devpts devpts /dev/pts
mount proc proc /proc
mount sysfs sysfs /sys

on init
export PATH /system/bin
export LD_LIBRARY_PATH /system/lib64

on post-fs
# In a real system, we would mount /data, /cache, etc.
# Here we just start the shell.

service shell /system/bin/sh
class core
console
disabled
user shell
group shell
seclabel u:r:shell:s0

on property:sys.boot_completed=1
start shell

````

1. **打包 RootFS**: 我们需要将 `my_rootfs` 目录打包成一个 `cpio` 归档，并用 `gzip` 压缩，作为内核的 `initramfs`。

```bash
cd my_rootfs
find . | cpio -o -H newc | gzip > ../rootfs.cpio.gz
cd ..

```

# 确保 common/arch/arm64/boot/Image.gz and rootfs.cpio.gz in/atCurrentDirectory

qemu-system-aarch64 \

- M virt \
- cpu cortex-a57 \
- m 2048 \
- kernel common/arch/arm64/boot/Image.gz \
- initrd rootfs.cpio.gz \
- nographic \
- append "console=ttyAMA0"

我们已经有了一个最小的 Linux 环境，但它还不是"Android"。要让它成为 Android，还需要以下关键步骤：

1. **启动 `servicemanager`**: 编译并运行它，它是 Android Binder IPC 机制的核心。
2. **启动 Zygote**: 编译 `app_process` 并通过 `init.rc` 启动它。Zygote 会预加载 Android 框架的核心类 (`framework.jar`) 并监听一个 socket，等待孵化新的 App 进程。
3. **启动 `system_server`**: Zygote 启动的第一个 Java 进程，它会创建所有的 Android 系统服务 (AMS, WMS, PMS 等)。

完成这些后，系统才能真正地运行 Android 应用。但这已经超出了"最小化 RootFS"的范畴，进入了完整的系统移植和开发领域。

```



<!-- 04-Reference/Advanced/so_anti_debugging_and_obfuscation.md -->

# SO文件反调试与字符串混淆技术

在Android Native层安全对抗中，SO文件是实现高强度保护的重要载体。通过init_array机制、字符串混淆和反调试技术的组合使用，可以显著提高逆向分析的难度。本文将深入分析这些技术的实现原理及对应的分析绕过方法。
___
## 1. init_array调用流程原理

## # 1.1 ELF加载与init_array执行时机

```

```
// 1. First call DT_INIT initialization function
if (init_func_ != nullptr) {
init_func_();
}

// 2. Then iterate through .init_array section function pointers
if (init_array_ != nullptr) {
for (size_t i = 0; i < init_array_count_; ++i) {
// Call each constructor function
((void (*)())init_array_[i])();
}
}
}

```

↓
nativeLoad() [art/runtime/native/java_lang_Runtime.cc]
↓
android_dlopen_ext() [bionic/libdl/libdl.cpp]
↓
do_dlopen() [bionic/linker/linker.cpp]
↓
find_library() → load_library() → link_image()
↓
call_constructors() → init_arrayFunctionExecute

```
readelf -d target.so | grep INIT

# Use objdump for analysis
objdump -s -j .init_array target.so

```

Elf64_Addr \*\*init_array; // Function pointer array
size_t init_array_count; // Array size
} init_array_info;

// Anti-debugging function declaration
**attribute**((constructor))
void anti_debug_init() {
// Anti-debugging logic
}

// After compilation, function pointers are generated in .init_array section

````

```cpp
// String encryption macro definition
# define ENCRYPT_STRING(str) encrypt_string_xor(str, sizeof(str)-1, 0xAA)

constexpr char* encrypt_string_xor(const char* str, size_t len, char key) {
static char encrypted[256];
for (size_t i = 0; i < len; i++) {
encrypted[i] = str[i] ^ key;
}
encrypted[len] = '\0';
return encrypted;
}

// Usage example
void check_frida() {
// Original string: "/data/local/tmp/frida-server"
const char* encrypted = ENCRYPT_STRING("\xc4\xae\xa8\xa8\xe4\xe6\xe8\xe0\xe4\xe6\xe4\xa8\xe3\xed\xe4\xa0\xd7\xd9\xd6\xae\xa4\xd7\xd9\xe5\xd9");

char decrypted[256];
decrypt_string(encrypted, decrypted, strlen(encrypted), 0xAA);

if (access(decrypted, F_OK) == 0) {
exit(1);
}
}

````

private:
static constexpr uint8_t AES_KEY[16] = {
0x2b, 0x7e, 0x15, 0x16, 0x28, 0xae, 0xd2, 0xa6,
0xab, 0xf7, 0x15, 0x88, 0x09, 0xcf, 0x4f, 0x3c
};

static void aes_decrypt(const uint8_t* encrypted, uint8_t* decrypted, size_t len) {
AES_KEY aes_key;
AES_set_decrypt_key(AES_KEY, 128, &aes_key);

for (size_t i = 0; i < len; i += 16) {
AES_decrypt(encrypted + i, decrypted + i, &aes_key);
}
}

public:
static std::string decrypt_string(const uint8_t\*\* encrypted_data, size_t len) {
std::vector<uint8_t> decrypted(len);
aes_decrypt(encrypted_data, decrypted.data(), len);

// 移除 padding
size_t actual_len = len;
while (actual_len > 0 && decrypted[actual_len - 1] == 0) {
actual_len--;
}

return std::string(reinterpret_cast<char\*\*>(decrypted.data()), actual_len);
}
};

// Use encrypted strings
void advanced_anti_debug() {
// Encrypted "/proc/self/status" string
const uint8_t encrypted_proc_status[] = {
0x8a, 0x2d, 0x5e, 0x1f, 0x9b, 0x7c, 0x85, 0xa3,
0x4e, 0x92, 0x67, 0xc1, 0x55, 0x98, 0x33, 0x2a
};

std::string proc_status = StringObfuscator::decrypt_string(
encrypted_proc_status, sizeof(encrypted_proc_status)
);

check_debugger_via_status(proc_status.c_str());
}

```
void construct_string_on_stack() {
char target_path[64];

// 分段构造String
strcpy(target_path, "/data/");
strcat(target_path, "local/");
strcat(target_path, "tmp/");
strcat(target_path, "frida-");
strcat(target_path, "server");

if (access(target_path, F_OK) == 0) {
exit(1);
}

// 清理栈上敏感String
memset(target_path, 0, sizeof(target_path));
}

```

std::vector<std::string> fragments;

public:
void add_fragment(const char\*\* encrypted, size_t len, uint8_t key) {
std::string decrypted;
for (size_t i = 0; i < len; i++) {
decrypted += static_cast<char>(encrypted[i] ^ key);
}
fragments.push_back(decrypted);
}

std::string build() {
std::string result;
for (const auto& fragment : fragments) {
result += fragment;
}

// 立即清理 fragments
fragments.clear();

return result;
}
};

void dynamic_string_detection() {
DynamicStringBuilder builder;

// 分段 EncryptString 片段
const char frag1[] = {0x8f, 0x9e, 0x9a, 0x9a, 0x8f}; // "/data"
const char frag2[] = {0x8f, 0x93, 0x91, 0x9d, 0x9e, 0x93}; // "/local"
const char frag3[] = {0x8f, 0x9a, 0x94, 0x92}; // "/tmp"

builder.add_fragment(frag1, 5, 0xEE);
builder.add_fragment(frag2, 6, 0xEE);
builder.add_fragment(frag3, 4, 0xEE);

std::string path = builder.build();

// Use 构造 PathPerformDetection
perform_detection(path.c_str());
}

```
import re
from elftools.elf.elffile import ELFFile

def detect_string_obfuscation(so_path):
with open(so_path, 'rb') as f:
elf = ELFFile(f)

# Check if .rodata section contains suspicious encrypted data
rodata_section = elf.get_section_by_name('.rodata')
if rodata_section:
data = rodata_section.data()

# Detect Xor pattern (high entropy)
entropy = calculate_entropy(data)
if entropy > 7.5:
print(f"[+] Possible XOR encrypted strings, entropy: {entropy}")

# Detect AES block pattern (16-byte aligned data blocks)
aes_patterns = find_aes_patterns(data)
if aes_patterns:
print(f"[+] Possible AES encrypted strings: {len(aes_patterns)} blocks")

def calculate_entropy(data):
import math
byte_counts = [0] * 256
for byte in data:
byte_counts[byte] += 1

entropy = 0
for count in byte_counts:
if count > 0:
freq = count / len(data)
entropy -= freq * math.log2(freq)

return entropy

```

// Hook common string decryption functions
var decrypt_func = Module.findExportByName("libtarget.so", "\_Z15decrypt_stringPKcS0_h");
if (decrypt_func) {
Interceptor.attach(decrypt_func, {
onEnter: function(args) {
this.encrypted = args[0];
this.output = args[1];
},
onLeave: function(retval) {
var decrypted = this.output.readCString();
console.log("[+] Decrypted string: " + decrypted);

// Save the decrypted string
send({
type: "decrypted_string",
data: decrypted
});
}
});
}

// Hook Xor decryption
var xor_decrypt = Module.findExportByName("libtarget.so", "decrypt_string");
if (xor_decrypt) {
Interceptor.attach(xor_decrypt, {
onLeave: function(retval) {
var result = retval.readCString();
console.log("[+] XOR decrypted: " + result);
}
});
}
}

// Hook dynamic string construction
function hook_string_construction() {
var strcat = Module.findExportByName("libc.so", "strcat");
var strcpy = Module.findExportByName("libc.so", "strcpy");

var string_tracker = new Map();

Interceptor.attach(strcpy, {
onEnter: function(args) {
this.dest = args[0];
this.src = args[1].readCString();
},
onLeave: function(retval) {
string_tracker.set(this.dest.toString(), this.src);
}
});

Interceptor.attach(strcat, {
onEnter: function(args) {
this.dest = args[0];
this.src = args[1].readCString();
},
onLeave: function(retval) {
var dest_key = this.dest.toString();
var current = string_tracker.get(dest_key) || "";
var new_string = current + this.src;
string_tracker.set(dest_key, new_string);

// Detect sensitive string construction
if (new_string.includes("frida") || new_string.includes("/proc/") || new_string.includes("gdb")) {
console.log("[!] Sensitive string constructed: " + new_string);
}
}
});
}

````

```cpp
// in/at.init_arrayInExecuteAnti-DebuggingFunction
__attribute__((constructor(101))) // Specified优先级
void init_anti_debug_level1() {
// 1. ptrace自身Protected
if (ptrace(PTRACE_TRACEME, 0, 1, 0) == -1) {
_exit(1);
}

// 2. DetectionDebug器Process
check_debugger_processes();

// 3. DetectionFridaFile
check_frida_artifacts();
}

__attribute__((constructor(102)))
void init_anti_debug_level2() {
// 4. DetectionMemoryMap
check_suspicious_mappings();

// 5. Detectionhook痕迹
check_hook_signatures();

// 6. TimeDetection
timing_attack_detection();
}

void check_debugger_processes() {
const char* debugger_names[] = {
"gdb", "lldb", "strace", "ida", "x64dbg"
};

for (const char* name : debugger_names) {
if (process_exists(name)) {
execute_anti_debug_response();
}
}
}

void check_frida_artifacts() {
const char* frida_indicators[] = {
"/data/local/tmp/frida-server",
"/data/local/tmp/frida-agent-64.so",
"/system/lib64/libfrida-gum.so"
};

for (const char* indicator : frida_indicators) {
if (file_exists(indicator)) {
execute_anti_debug_response();
}
}
}

````

// 检测代码段完整性
verify_code_integrity();

// Detectionanomaly 向量 table
check_exception_handlers();

// SetMemoryProtected
setup_memory_protection();
}

void check_suspicious_mappings() {
FILE\*\* maps = fopen("/proc/self/maps", "r");
char line[512];

while (fgets(line, sizeof(line), maps)) {
// Detection 可疑 LibraryMap
if (strstr(line, "frida") ||
strstr(line, "gum-js-loop") ||
strstr(line, "xposed")) {
fclose(maps);
execute_anti_debug_response();
}

// Detection 可疑权限组合
if (strstr(line, "rwxp")) { // 可读写执行页面
analyze_rwx_mapping(line);
}
}

fclose(maps);
}

void verify_code_integrity() {
// CalculateCode 段哈希 Value
Dl_info info;
dladdr((void\*\*)verify_code_integrity, &info);

const char* base = (const char*)info.dli_fbase;
size_t text_size = get_text_section_size(base);

uint32_t current_hash = calculate_crc32(base, text_size);
uint32_t expected_hash = get_expected_hash();

if (current_hash != expected_hash) {
// Code 被 Modify，Execute 对抗 Measure
code_tampering_detected();
}
}

```
void init_timing_checks() {
// 启动定时器检测
start_timing_monitor();

// Detection单步Execute
detect_single_stepping();
}

void detect_single_stepping() {
struct timespec start, end;
clock_gettime(CLOCK_MONOTONIC, &start);

// Execute一些SimpleOperation
volatile int dummy = 0;
for (int i = 0; i < 1000; i++) {
dummy += i;
}

clock_gettime(CLOCK_MONOTONIC, &end);

long duration = (end.tv_sec - start.tv_sec) * 1000000000 +
(end.tv_nsec - start.tv_nsec);

// IfExecuteTimeanomaly，可能in/at单步Debug
if (duration > NORMAL_EXECUTION_TIME * 10) {
single_step_detected();
}
}

void start_timing_monitor() {
std::thread([]() {
while (true) {
std::this_thread::sleep_for(std::chrono::seconds(5));

// 定期检测系统调用时间
struct timespec start, end;
clock_gettime(CLOCK_MONOTONIC, &start);
getpid(); // Simple系统Call
clock_gettime(CLOCK_MONOTONIC, &end);

long syscall_time = (end.tv_sec - start.tv_sec) * 1000000000 +
(end.tv_nsec - start.tv_nsec);

if (syscall_time > NORMAL_SYSCALL_TIME * 5) {
// 系统调用被拦截或调试
syscall_hooking_detected();
}
}
}).detach();
}

```

EXIT_SILENTLY,
CORRUPT_DATA,
FAKE_EXECUTION,
CRASH_GRACEFULLY,
REPORT_TO_SERVER
};

void execute_anti_debug_response() {
static int detection_count = 0;
detection_count++;

// 根据检测次数选择不同响应策略
AntiDebugResponse response = select_response_strategy(detection_count);

switch (response) {
case AntiDebugResponse::EXIT_SILENTLY:
\_exit(0);
break;

case AntiDebugResponse::CORRUPT_DATA:
corrupt_critical_data();
break;

case AntiDebugResponse::FAKE_EXECUTION:
enter_fake_execution_mode();
break;

case AntiDebugResponse::CRASH_GRACEFULLY:
trigger_controlled_crash();
break;

case AntiDebugResponse::REPORT_TO_SERVER:
report_debug_attempt();
\_exit(1);
break;
}
}

void corrupt_critical_data() {
// 破坏关 KeyData 结构，使 AnalysisResultNo 效
extern char critical_data_start[];
extern char critical_data_end[];

size_t size = critical_data_end - critical_data_start;
for (size_t i = 0; i < size; i++) {
critical_data_start[i] ^= 0xFF;
}
}

void enter_fake_execution_mode() {
// 进入虚 FalseExecute 模式，ReturnErrorAnalysisResult
global_fake_mode = true;

// ModifyFunction 指针，指向虚 FalseImplement
redirect_function_calls();
}

````

```python
# Tool to analyze init_array section
import subprocess
from elftools.elf.elffile import ELFFile

class InitArrayAnalyzer:
def __init__(self, so_path):
self.so_path = so_path
self.init_functions = []

def analyze_init_array(self):
# Use readelf to get init_array information
result = subprocess.run(['readelf', '-d', self.so_path],
capture_output=True, text=True)

for line in result.stdout.split('\n'):
if 'INIT_ARRAY' in line:
# Parse init_array address and size
self.parse_init_array_info(line)

def extract_function_addresses(self):
with open(self.so_path, 'rb') as f:
elf = ELFFile(f)

# Find .init_array section
init_array_section = elf.get_section_by_name('.init_array')
if init_array_section:
data = init_array_section.data()

# Parse function pointers (8-byte aligned)
for i in range(0, len(data), 8):
if i + 8 <= len(data):
func_addr = int.from_bytes(data[i:i+8], 'little')
self.init_functions.append(func_addr)
print(f"[+] Init function at: 0x{func_addr:x}")

def disassemble_functions(self):
# Use objdump to disassemble each initialization function
for addr in self.init_functions:
print(f"\n[+] Disassembling function at 0x{addr:x}")
subprocess.run(['objdump', '-d', '--start-address', hex(addr),
'--stop-address', hex(addr + 0x100), self.so_path])

# Usage example
analyzer = InitArrayAnalyzer('target.so')
analyzer.analyze_init_array()
analyzer.extract_function_addresses()
analyzer.disassemble_functions()

````

// Hook constructor function calls
var call_constructors = Module.findExportByName("linker64", "\_ZN6soinfo17call_constructorsEv");
if (call_constructors) {
Interceptor.attach(call_constructors, {
onEnter: function(args) {
var soinfo = args[0];
var soname = get_soname(soinfo);
console.log("[+] Calling constructors for: " + soname);

this.soname = soname;
this.start_time = Date.now();
},
onLeave: function(retval) {
var duration = Date.now() - this.start_time;
console.log("[+] Constructors completed for " + this.soname +
" in " + duration + "ms");
}
});
}

// Hook each function in init_array
var target_module = Process.findModuleByName("libtarget.so");
if (target_module) {
analyze_init_array_section(target_module);
}
}

function analyze_init_array_section(module) {
// ParseELFFile 找到 init_array 段
var elf_base = module.base;
var elf_header = elf_base.readByteArray(64); // ELF header

// GetProgram 头 table 偏移
var phoff = elf_base.add(0x20).readU64();
var phnum = elf_base.add(0x38).readU16();

// IterateProgram 头，查找 PT_DYNAMIC
for (var i = 0; i < phnum; i++) {
var ph_addr = elf_base.add(phoff).add(i \*\* 56);
var p_type = ph_addr.readU32();

if (p_type === 2) { // PT_DYNAMIC
var p_vaddr = ph_addr.add(16).readU64();
var dynamic_addr = elf_base.add(p_vaddr);

parse_dynamic_section(dynamic_addr, module);
break;
}
}
}

function parse_dynamic_section(dynamic_addr, module) {
var addr = dynamic_addr;

while (true) {
var tag = addr.readU64();
var val = addr.add(8).readU64();

if (tag === 0) break; // DT_NULL

if (tag === 25) { // DT_INIT_ARRAY
var init_array_addr = module.base.add(val);
console.log("[+] Found init_array at: " + init_array_addr);

// Hook init_arrayin 每 Function
hook_init_array_functions(init_array_addr, module);
} else if (tag === 27) { // DT_INIT_ARRAYSZ
var array_size = val;
console.log("[+] Init_array size: " + array_size);
}

addr = addr.add(16);
}
}

function hook_init_array_functions(init_array_addr, module) {
var num_functions = 10; // False 设最多 10Function

for (var i = 0; i < num_functions; i++) {
var func_ptr_addr = init_array_addr.add(i \*\* 8);
var func_addr = func_ptr_addr.readPointer();

if (func_addr.isNull()) break;

console.log("[+] Hooking init function " + i + " at: " + func_addr);

Interceptor.attach(func_addr, {
onEnter: function(args) {
console.log("[!] Init function " + this.func_index + " called");

// PrintCall 栈
console.log(Thread.backtrace(this.context, Backtracer.ACCURATE)
.map(DebugSymbol.fromAddress).join('\n'));
},
onLeave: function(retval) {
console.log("[!] Init function " + this.func_index + " completed");
}
});
}
}

```
function bypass_ptrace() {
var ptrace = Module.findExportByName("libc.so", "ptrace");
if (ptrace) {
Interceptor.attach(ptrace, {
onEnter: function(args) {
var request = args[0].toInt32();
if (request === 0) { // PTRACE_TRACEME
console.log("[+] Blocking PTRACE_TRACEME");
args[0] = ptr(-1);
}
},
onLeave: function(retval) {
// 始终ReturnSuccess
retval.replace(ptr(0));
}
});
}
}

// BypassFileDetection
function bypass_file_detection() {
var access = Module.findExportByName("libc.so", "access");
var openat = Module.findExportByName("libc.so", "openat");

var blocked_paths = [
"/data/local/tmp/frida-server",
"/proc/self/maps",
"/proc/self/status"
];

if (access) {
Interceptor.attach(access, {
onEnter: function(args) {
var path = args[0].readCString();
if (blocked_paths.some(p => path.includes(p))) {
console.log("[+] Blocking access to: " + path);
args[0] = Memory.allocUtf8String("/dev/null");
}
}
});
}

if (openat) {
Interceptor.attach(openat, {
onEnter: function(args) {
var path = args[1].readCString();
if (blocked_paths.some(p => path.includes(p))) {
console.log("[+] Blocking openat for: " + path);
args[1] = Memory.allocUtf8String("/dev/null");
}
}
});
}
}

// BypassTimeDetection
function bypass_timing_detection() {
var clock_gettime = Module.findExportByName("libc.so", "clock_gettime");
if (clock_gettime) {
var fake_time = {
sec: 1640995200, // 固定时间戳
nsec: 0
};

Interceptor.attach(clock_gettime, {
onLeave: function(retval) {
var timespec = this.context.x1; // SecondParameter
if (!timespec.isNull()) {
// Write固定TimeValue
timespec.writeU64(fake_time.sec);
timespec.add(8).writeU64(fake_time.nsec);

// 每次调用略微增加纳秒
fake_time.nsec += 1000;
}
}
});
}
}

```

var mprotect = Module.findExportByName("libc.so", "mprotect");
if (mprotect) {
Interceptor.attach(mprotect, {
onEnter: function(args) {
var addr = args[0];
var size = args[1].toInt32();
var prot = args[2].toInt32();

console.log("[+] mprotect: " + addr + ", size: " + size +
", prot: 0x" + prot.toString(16));

// 阻止移除 execute permission
if ((prot & 0x4) === 0) {
args[2] = ptr(prot | 0x4); // AddPROT_EXEC
}
}
});
}
}

// HookStringDecryptFunction
function hook_string_decryption() {
var module = Process.findModuleByName("libtarget.so");
if (!module) return;

// 扫描 DecryptFunction 模式
var pattern = "48 89 ?? 48 89 ?? 48 83 ?? ?? 8B ?? ??"; // x64DecryptFunction 模式

Memory.scan(module.base, module.size, pattern, {
onMatch: function(address, size) {
console.log("[+] Found potential decryption function at: " + address);

Interceptor.attach(address, {
onEnter: function(args) {
console.log("[+] Decryption function called");
this.args = Array.prototype.slice.call(args);
},
onLeave: function(retval) {
// 尝试 ReadDecryptResult
try {
var result = retval.readCString();
if (result && result.length > 0 && result.length < 256) {
console.log("[+] Decrypted string: " + result);
}
} catch (e) {
// 可能不 isString
}
}
});
},
onComplete: function() {
console.log("[+] Decryption function scan completed");
}
});
}

// 智能 Anti-DebuggingBypass
function intelligent_anti_debug_bypass() {
// 1. 自动检测并绕过常见反调试技术
bypass_ptrace();
bypass_file_detection();
bypass_timing_detection();
bypass_memory_protection();

// 2. Monitorinit_arrayExecute
monitor_init_array();

// 3. HookStringDecrypt
hook_string_decryption();

// 4. Set 定期 Check，ProcessNewAnti-Debugging 机制
setInterval(function() {
check_new_anti_debug_mechanisms();
}, 5000);
}

function check_new_anti_debug_mechanisms() {
// DetectionNewAnti-DebuggingThread
var threads = Process.enumerateThreads();
threads.forEach(function(thread) {
// Check if ThreadCall 栈 is ContainsAnti-DebuggingFunction
var backtrace = Thread.backtrace(thread.context, Backtracer.ACCURATE);
// Analysis 并 Process...
});
}

```
// 实现多层级保护机制
class ComprehensiveProtection {
private:
static bool stage1_passed;
static bool stage2_passed;
static bool stage3_passed;

public:
// 第一Stage：BasicDetection
__attribute__((constructor(101)))
static void protection_stage1() {
if (basic_anti_debug_check()) {
stage1_passed = true;
decrypt_stage2_key();
} else {
enter_decoy_mode();
}
}

// SecondStage：深度Detection
__attribute__((constructor(102)))
static void protection_stage2() {
if (!stage1_passed) return;

if (advanced_detection()) {
stage2_passed = true;
unlock_critical_functions();
} else {
corrupt_stage2_data();
}
}

// 第三Stage：RunWhenProtected
__attribute__((constructor(103)))
static void protection_stage3() {
if (!stage2_passed) return;

start_runtime_protection();
stage3_passed = true;
}

// 关键函数只有在所有检测通过后才能正常执行
static bool is_protection_active() {
return stage1_passed && stage2_passed && stage3_passed;
}
};

```

private:
enum ThreatLevel {
NO_THREAT = 0,
LOW_THREAT = 1,
MEDIUM_THREAT = 2,
HIGH_THREAT = 3,
CRITICAL_THREAT = 4
};

static ThreatLevel assess_threat_level() {
int threat_score = 0;

// 各种检测权重评分
if (detect_frida()) threat_score += 30;
if (detect_debugger()) threat_score += 25;
if (detect_hook()) threat_score += 20;
if (detect_emulator()) threat_score += 15;
if (detect_root()) threat_score += 10;

if (threat_score >= 80) return CRITICAL_THREAT;
if (threat_score >= 60) return HIGH_THREAT;
if (threat_score >= 40) return MEDIUM_THREAT;
if (threat_score >= 20) return LOW_THREAT;
return NO_THREAT;
}

public:
static void adaptive_response() {
ThreatLevel level = assess_threat_level();

switch (level) {
case CRITICAL_THREAT:
immediate_termination();
break;
case HIGH_THREAT:
data_corruption_and_exit();
break;
case MEDIUM_THREAT:
fake_execution_mode();
break;
case LOW_THREAT:
increased_monitoring();
break;
case NO_THREAT:
normal_execution();
break;
}
}
};

```
1. 多层级检测机制，分阶段验证
2. 字符串动态解密，避免静态分析
3. 时间和行为检测，识别调试环境
4. 自适应响应策略，根据威胁等级调整

* *分析方的应对策略**：
1. 静态分析结合动态Hook
2. 全面的API拦截和重定向
3. 时间和环境模拟
4. 自动化绕过脚本开发

这一技术对抗将持续演进，双方都需要不断提升技术水平以应对新的挑战。
```

<!-- 04-Reference/Advanced/so_runtime_emulation.md -->

# SO 运行时仿真：脱离设备的 Native 代码执行

在高级 Android 逆向工程中，我们经常需要自动化地调用 SO 文件中的加密、签名或校验函数。然而，在真实的设备上通过 Frida Hook 来做这件事，不仅效率低下，而且容易受到反调试和环境检测的阻碍。

- **SO 运行时仿真\*\***（有时被称为"符号执行"的工程化应用）是一种革命性的技术，它通过在 PC 上创建一个模拟的 Android Native 运行环境，直接加载并执行 SO 文件，从而摆脱对真实设备的依赖。

## 核心架构

一个典型的 SO 仿真框架主要由以下几个部分构成：

## # 1. ELF 加载器 (ELF Loader)

这是仿真的基础。它负责像 Android 的 `linker` 一样工作：

- **解析 ELF**: 读取 SO 文件的头部、程序头、段表等信息。

- **内存映射**: 根据程序头（`PT_LOAD`）将 SO 的代码段（`.text`）和数据段（`.data`, `.bss`）加载到模拟的内存空间中。

- **处理重定位**: 这是最关键的一步。SO 文件在编译时并不知道它会被加载到哪个基地址，也不知道外部函数（如 `memcpy`）的具体地址。加载器需要解析重定位表（`.rel.dyn`, `.rela.dyn`），并将代码中所有对内部地址和外部符号的引用进行修正，填写正确的运行时地址。

## # 2. CPU 模拟器 (CPU Emulator)

- **Unicorn Engine**: 这是目前最主流的选择。Unicorn 是一个基于 QEMU 的轻量级、多平台的 CPU 模拟器库。我们可以通过它来执行加载到内存中的 ARM 或 ARM64 机器码。

- **指令级控制**: Unicorn 允许我们精细地控制执行流程，包括设置寄存器、读写内存、以及通过 Hook 机制在执行到特定指令或地址时触发回调。

## # 3. 系统库与环境模拟 (Library & Environment Mocking)

SO 文件不会独立存在，它总是会调用外部函数。仿真框架必须能够"假装"自己是 Android 系统，提供这些函数。

- **Mock `libc.so`**: 提供 `malloc`, `free`, `memcpy`, `strlen`, `printf` 等标准 C 库函数的实现。当 SO 调用这些函数时，会被重定向到我们自己实现的版本。

- **Mock Android Framework Libraries**: 提供 `liblog.so` (`__android_log_print`)、`libz.so` (压缩库)、`libcrypto.so` (OpenSSL) 等常用系统库的函数实现。

- **Mock JNI 环境**: 如果要调用的函数是 JNI 函数，那么还需要模拟 `JNIEnv` 指针和相关的函数表（`NewStringUTF`, `GetFieldID` 等）。这是与 Java 世界交互的关键。

## 推荐项目：`unidbg`

`unidbg` 是一个非常强大和成熟的、专门用于 Android SO 仿真和符号执行的 Java 开源项目。它极大地简化了上述复杂的工作。

- **`unidbg` 的优点\*\***:
- **高度自动化**: 内置了完善的 ELF 加载器和常用系统库的 Mock 实现。

- **易于使用**: 提供了简洁的 API，用户只需几行代码就可以加载 SO、调用函数。

- **JNI 模拟**: 拥有强大的 JNI 模拟能力，甚至可以调用和 Mock Java 对象的方法。

- **调试与跟踪**: 支持与 GDB 连接进行远程调试，也可以通过 Hook 机制打印详细的执行日志。

## # `unidbg` 使用范例 (概念代码)

```java
// Use unidbg Call一 SO inSignatureFunction
public class SignatureCalculator {
public static void main(String[] args) {
// 1. Create一 android ARM64 模拟器Instance
Emulator<?> emulator = AndroidEmulatorBuilder.for64Bit().build();
Memory memory = emulator.getMemory();

// 2. LoadTarget SO File及其依赖
// unidbg 会AutoProcess重定位and依赖Load
Module module = emulator.loadLibrary(new File("libnative-lib.so"));

// 3. 准备InputData
String input = "this is my data to sign";
// WillInputStringWrite模拟器MemoryIn
Pointer inputPtr = memory.allocateString(input);

// 4. CallTargetFunction
// d.callFunction() 会AutoProcess寄储器andStackSet
Number result = module.callFunction(emulator, /* function offset */ 0x1234, inputPtr, input.length());

// 5. 从模拟器MemoryInReadResult
Pointer resultPtr = Pointer.pointer(emulator, result.intValue());
String signature = resultPtr.getString(0);

System.out.println("Input: " + input);
System.out.println("Signature: " + signature);

// 6. 关闭模拟器
emulator.close();
}
}

```

- **pyelftools**: 用于解析 ELF 文件，获取加载信息。

- **Python**: 胶水语言，用于编写加载器和 Mock 函数。

## # 2. 实现步骤

### a. 初始化 Unicorn 环境

首先，我们需要初始化一个指定架构的模拟器，并分配内存用于加载 SO 和堆栈。

```python
from unicorn import *
from unicorn.arm64_const import *

# Initialize ARM64 模拟器
mu = Uc(UC_ARCH_ARM64, UC_MODE_ARM)

# DefineMemory区域
BASE_ADDRESS = 0x40000000
STACK_ADDRESS = 0x70000000
STACK_SIZE = 1024 * 1024 # 1MB Stack

# MapMemory
mu.mem_map(BASE_ADDRESS, 2 * 1024 * 1024) # 2MB for SO
mu.mem_map(STACK_ADDRESS, STACK_SIZE)

# SetStack指针 (SP)
mu.reg_write(UC_ARM64_REG_SP, STACK_ADDRESS + STACK_SIZE)

```

def load_so(mu, so_path):
with open(so_path, 'rb') as f:
elffile = ELFFile(f)
for segment in elffile.iter_segments():
if segment.header.p_type == 'PT_LOAD':
vaddr = segment.header.p_vaddr
mem_size = segment.header.p_memsz
file_size = segment.header.p_filesz
data = segment.data()

# 将段写入模拟器内存

mu.mem_write(BASE_ADDRESS + vaddr, data)
print(f"Loaded segment at {hex(BASE_ADDRESS + vaddr)} size {hex(mem_size)}")
return BASE_ADDRESS

# ...

# load_so(mu, 'libnative-lib.so')

```
# 模拟外部函数地址
MOCK_PUTS_ADDR = 0xFFFFFFFF00001000

# 记录被 Hook 的指令，防止重复处理
hooked_instructions = set()

def hook_code(mu, address, size, user_data):
# OnlyProcess跳转指令
if address in hooked_instructions:
return

instruction = mu.mem_read(address, size)
# 简化 BL 指令Check
if instruction[3] == 0x94: # BL instruction in ARM64
# 计算跳转目标地址 (简化)
# 实际需要完整解码指令
target_addr = ...

if target_addr == MOCK_PUTS_ADDR:
# 1. ReadParameter (ARM64In第一Parameterin/at X0 寄存器)
str_ptr = mu.reg_read(UC_ARM64_REG_X0)
# 2. 从模拟器MemoryInReadString
str_val = mu.mem_read(str_ptr, 50).split(b'\x00')[0]
# 3. Execute Mock 功能
print(f"[+] puts called with: '{str_val.decode()}'")
# 4. 模拟FunctionReturn，SetReturnAddress (LR) 到 PC
mu.reg_write(UC_ARM64_REG_PC, mu.reg_read(UC_ARM64_REG_LR))
else:
print(f"Warning: Unhandled call to {hex(target_addr)}")

hooked_instructions.add(address)

# in/at整 SO Load区域Set Hook
mu.hook_add(UC_HOOK_CODE, hook_code, begin=BASE_ADDRESS, end=BASE_ADDRESS + 0x100000) # Adjust size

```

- **Mock `fopen`**: 在 Hook 中，当你识别出对 `fopen` 的调用时，你的 Python Mock 函数会接收到一个路径参数（如 `/data/local/tmp/config.txt`）。你的 Mock 函数逻辑就是将这个模拟器内的路径拼接上你的 PC Rootfs 路径 (`./my_rootfs` + `/data/local/tmp/config.txt`)，然后用 Python 的 `open()` 函数打开真实文件，并返回一个文件句柄的模拟值给 SO。

- **Mock `fread`/`fwrite`**: 后续对 `fread` 的调用，都会根据模拟的文件句柄，在你的 Python Mock 函数中操作对应的真实文件。

通过这种方式，你可以完全控制 SO 的文件访问，为其提供定制的输入或记录其输出。

## 基于 `chroot` 与 `linker` 的高级仿真 (C 语言)

这是最接近"真实"的仿真方式。我们不再用 `pyelftools` 去模拟 ELF 加载，而是直接利用从 Android 系统中提取出的 `linker64` 程序，让它在一个受控的 `chroot` 环境中为我们加载目标 SO。

## # 1. 核心思路

1. **构建 Android Rootfs**: 在 Linux 主机上创建一个最小化的 Android 文件系统。
2. **编写加载器 (Loader)**: 用 C 编写一个加载器程序，它的唯一使命就是 `chroot` 到我们构建的 Rootfs 中，然后通过 `execve` 启动 `linker64`。
3. **编写测试桩 (Test Harness)**: 由于 `linker64` 需要执行一个带有 `main` 函数的可执行文件，我们可以编写一个"测试桩"程序。它的唯一作用就是加载目标 SO，调用指定函数，并返回结果。

## # 2. 实现步骤

### a. 准备 android Rootfs

在你的 Linux 主机上创建一个目录，例如 `~/android_rootfs/`，并仿照真实设备创建目录结构。然后从一个真实的 Android 设备（或 AOSP 编译产物）中 `adb pull` 出必要的系统文件：

```bash
# in/at你 PC 上
mkdir -p ~/android_rootfs/system/lib64
mkdir -p ~/android_rootfs/system/bin
mkdir -p ~/android_rootfs/data/local/tmp

# 从设备上拉取文件 (以 arm64 为例)
adb pull /system/bin/linker64 ~/android_rootfs/system/bin/
adb pull /system/lib64/libc.so ~/android_rootfs/system/lib64/
adb pull /system/lib64/libdl.so ~/android_rootfs/system/lib64/
adb pull /system/lib64/libm.so ~/android_rootfs/system/lib64/

# ... 以及TargetSO可能依赖其他Library

# 将你的目标 SO 和测试桩程序也放进去
cp your_target.so ~/android_rootfs/data/local/tmp/
cp your_harness ~/android_rootfs/data/local/tmp/

```

# include <dlfcn.h>

// False 设 TargetSO 有一 ExportFunction: char* process_data(const char* input);
typedef const char* (*process_data_func)(const char\*\*);

int main(int argc, char \*\*_argv) {
// in/at chroot 环境 In，Pathis 相对于新根 Directory
void_ handle = dlopen("/data/local/tmp/your_target.so", RTLD_LAZY);
if (!handle) {
fprintf(stderr, "Cannot open library: %s\n", dlerror());
return -1;
}

// GetFunction 指针
process_data_func func = (process_data_func)dlsym(handle, "process_data");
if (!func) {
fprintf(stderr, "Cannot find symbol: %s\n", dlerror());
dlclose(handle);
return -1;
}

// CallFunction 并 PrintResult
const char* input = "hello from harness";
const char* result = func(input);
printf("Result from SO: %s\n", result);

dlclose(handle);
return 0;
}

```

```

# include <unistd.h>

# include <stdlib.h>

int main(int argc, char \*\*_argv) {
const char_ root_dir = "/home/user/android_rootfs"; // Modify 为你 rootfs Path

if (chroot(root_dir) != 0) {
perror("chroot failed");
return 1;
}

// 进入 chroot After，'/' 就 is 之 Before root_dir
chdir("/");

// 准备 execve Parameter
char *new_argv[] = {
"/data/local/tmp/harness", // 要 ExecuteProgram
NULL
};
char *new_envp[] = {
"LD_LIBRARY_PATH=/system/lib64", // 告诉 linker in/atWhere 找 .so
NULL
};

// 使用 linker64 来执行我们的测试桩程序
// linker64 会 Process harness AllLoadand 链接工作
execve("/system/bin/linker64", new_argv, new_envp);

// 如果 execve 成功，这行代码永远不会被执行
perror("execve failed");
return 1;
}

```
| **Python + Unicorn** | 灵活，可定制性强，可完全控制执行流程和内存布局，跨平台。帮助深入理解原理。 | **中** | 纯 Native 算法逆向、安全研究、Fuzzing、学习 ELF 加载和 CPU 仿真、无复杂系统或 JNI 依赖的函数。 |
| **C + chroot + Test Harness** | 保真度最高，性能最好，直接利用系统原生 `linker` 和库，环境与真机几乎一致。 | **高** | 对运行环境要求苛刻的 SO、需要 TLS 初始化或有复杂依赖的场景、追求极致的执行性能。 |

## 总结

SO 运行时仿真是一项高级但回报巨大的技术。它将逆向分析从繁琐的手工调试和 Hook 中解放出来，带入了自动化、可大规模扩展的新阶段。对于需要频繁调用 Native 函数、分析复杂算法的场景，掌握如 `unidbg` 这样的仿真框架是必不可少的技能。

* **通信困难**: 主机与被仿真进程的通信需要借助文件、管道或 Socket 等 IPC 机制，不如 `unidbg` 的 API 调用方便。

* **权限要求**: `chroot` 操作需要 root 权限。
```

<!-- 04-Reference/Engineering/frameworks_and_middleware.md -->

# 工程化：框架、工具与中间件

在复杂的逆向工程和数据采集中，单纯依靠基础工具往往效率低下。为了处理大规模的任务、管理复杂的依赖和保证流程的稳定性，我们需要引入“工程化”的思维，利用成熟的框架和中间件来构建健壮、可扩展的分析系统。

本节内容将聚焦于那些能将单个脚本提升为工业级解决方案的关键技术，例如：

- **消息队列 (Message Queues)**: 如 RabbitMQ，用于解耦任务的生产者和消费者，实现异步处理和削峰填谷。

- **数据存储 (Data Storage)**: 如 MongoDB 或 PostgreSQL，用于结构化地存储分析结果，方便后续的查询和二次开发。

- **缓存系统 (Caching Systems)**: 如 Redis，用于缓存常用数据，加速热点路径的访问。

- **爬虫框架 (Crawling Frameworks)**: 如 Scrapy，提供了一整套用于网络数据提取的架构，包括请求调度、中间件处理和数据管道。

通过组合这些工具，我们可以搭建起一个能够处理海量设备、执行复杂任务并高效存储结果的强大平台。

<!-- 04-Reference/Engineering/message_queues.md -->

---

# 工程化：消息队列 (Message Queue)

消息队列（MQ）是大型分布式系统中用于服务间异步通信的核心组件。在规模化的逆向分析和数据采集中，它扮演着"缓冲池"和"解耦器"的关键角色，确保数据流的稳定、高效和可靠。

---

## 1. 核心概念与作用

### a) 为什么需要消息队列？

想象一个场景：你有 100 台爬虫节点（生产者）在高速抓取数据，同时有 10 个数据处理节点（消费者）负责清洗和入库。如果让生产者直接调用消费者的 API，会产生几个问题：

- **性能耦合**: 消费者的处理速度会直接限制生产者的抓取速度。如果数据库写入缓慢，整个爬虫集群都得等。
- **峰值压力**: 如果短时间内抓取到大量数据（流量洪峰），可能会瞬间压垮消费者服务。
- **服务依赖**: 如果消费者服务宕机，所有生产者都会失败，数据会丢失。

### b) 消息队列的解决方案

MQ 在生产者和消费者之间增加了一个中间层，解决了以上所有问题：

- **异步解耦**: 生产者只需将消息（如"一个待处理的数据包"）扔进队列即可，无需关心谁在消费、何时消费。
- **削峰填谷**: 流量洪峰到来时，消息会先在队列中积压。消费者可以按照自己的节奏平稳地进行处理，避免了系统崩溃。
- **可靠性与冗余**: 即使消费者宕机，消息仍然安全地存储在队列中。当消费者恢复后，可以继续处理，保证了数据不丢失。

---

## 2. 主流消息队列方案

### a) Kafka

- **定位**: 一个分布式的、分区的、多副本的、基于 Zookeeper 的**日志提交系统 (Commit Log)**。
- **核心特点**:
  - **极致的吞吐量**: 设计目标就是为了处理海量日志数据，拥有无与伦比的写入和读取性能，是大数据领域的首选。
  - **发布-订阅模型**: 消息以"主题 (Topic)"进行分类。生产者向一个 Topic 发送消息，多个消费者组 (Consumer Group) 可以独立地订阅和消费同一个 Topic 的消息，互不干扰。
  - **持久化与回溯**: 消息在 Kafka 中是持久化存储的。消费者可以根据需要"回溯"到任意时间点（Offset）重新消费数据，这对于数据重处理和故障恢复非常有用。
- **适用场景**:
  - 需要处理海量数据流的日志收集（Log Ingestion）。
  - 作为 Spark Streaming 或 Flink 等实时计算框架的数据源。
  - 构建大规模数据管道的总线。

### b) RabbitMQ

- **定位**: 一个实现了 AMQP (高级消息队列协议) 的、功能丰富的**消息代理 (Message Broker)**。
- **核心特点**:
  - **灵活的路由**: 拥有强大的交换机 (Exchange) 和路由键 (Routing Key) 机制，可以实现非常复杂的路由逻辑（如 fanout, direct, topic, headers）。
  - **功能全面**: 支持消息确认、优先级队列、延迟队列、死信队列等企业级特性。
  - **可靠性**: 提供了强大的消息确认机制，能确保消息"至少被成功消费一次"。
- **适用场景**:
  - 业务逻辑复杂，需要精细化控制消息路由的场景。
  - 对消息投递的可靠性要求极高的金融或事务性系统。
  - 需要使用延迟队列等高级特性的业务。

### c) Redis

- **定位**: 一个高性能的内存数据库，但其 `List` 和 `Pub/Sub` 功能使其可以作为一个轻量级的消息队列使用。
- **核心特点**:
  - **简单快速**: 配置简单，读写性能极高（基于内存）。
  - **功能有限**: 不支持复杂路由，可靠性保证较弱（如 `Pub/Sub` 不保证消息必达），消息积压能力受内存限制。
- **适用场景**:
  - 系统规模不大，对可靠性要求不高，但对实时性要求很高的场景。
  - 作为任务队列（如 Celery 的 Broker）。
  - 实现简单的实时通知或聊天功能。

---

## 总结

在工程化体系中，选择哪种 MQ 取决于具体的业务需求：

- 追求**极致的吞吐量和大数据生态兼容性**，选择 `Kafka`。
- 追求**灵活的路由和业务功能的丰富性**，选择 `RabbitMQ`。
- 追求**简单、轻量和极致的低延迟**，`Redis` 是一个不错的备选项。

---

<!-- 04-Reference/Engineering/redis.md -->

# Redis 常用命令备忘录

Redis 是一个开源的、基于内存的、高性能的键值存储系统。它支持多种数据结构，如字符串、哈希、列表、集合和有序集合。本备忘录旨在提供常用命令的快速参考。

---

## 目录

- [Redis 常用命令备忘录](#redis-常用命令备忘录)
- [目录](#目录)
- [连接与服务器管理](#连接与服务器管理)

- [键 (Key) 操作](#键-key-操作)

- [字符串 (String)](#字符串-string)

- [哈希 (Hash)](#哈希-hash)

- [列表 (List)](#列表-list)

- [集合 (Set)](#集合-set)

- [有序集合 (Sorted Set / ZSet)](#有序集合-sorted-set--zset)

- [目录](#目录)
- [连接与服务器管理](#连接与服务器管理)

- [键 (Key) 操作](#键-key-操作)

- [字符串 (String)](#字符串-string)

- [哈希 (Hash)](#哈希-hash)

- [列表 (List)](#列表-list)

- [集合 (Set)](#集合-set)

- [有序集合 (Sorted Set / ZSet)](#有序集合-sorted-set--zset)

- [连接与服务器管理](#连接与服务器管理)

- [键 (Key) 操作](#键-key-操作)

- [字符串 (String)](#字符串-string)

- [哈希 (Hash)](#哈希-hash)

- [列表 (List)](#列表-list)

- [集合 (Set)](#集合-set)

- [有序集合 (Sorted Set / ZSet)](#有序集合-sorted-set--zset)

---

## # 连接与服务器管理

| 命令                                          | 描述                                |
| :-------------------------------------------- | :---------------------------------- |
| `redis-cli`                                   | 启动 Redis 命令行客户端             |
| `redis-cli -h <host> -p <port> -a <password>` | 连接到指定的 Redis 实例             |
| `PING`                                        | 测试服务器是否仍在运行，返回 `PONG` |
| `AUTH <password>`                             | 验证连接密码                        |
| `SELECT <index>`                              | 选择数据库 (默认 0-15)              |
| `FLUSHDB`                                     | 清空当前数据库的所有键              |
| `FLUSHALL`                                    | 清空所有数据库的所有键              |
| `INFO`                                        | 获取服务器的信息和统计数据          |

---

## # 键 (Key) 操作

| 命令                                          | 描述                                                                     |
| :-------------------------------------------- | :----------------------------------------------------------------------- |
| `KEYS <pattern>`                              | 查找所有符合给定模式的键 (如 `KEYS *`, `KEYS user:*`) **(慎用，会阻塞)** |
| `SCAN <cursor> [MATCH pattern] [COUNT count]` | 迭代数据库中的键，比 `KEYS` 更安全                                       |
| `EXISTS <key>`                                | 检查给定键是否存在                                                       |
| `DEL <key> [key ...]`                         | 删除一个或多个键                                                         |
| `TYPE <key>`                                  | 返回键所存储的值的类型 (string, hash, list, set, zset)                   |
| `TTL <key>`                                   | 以秒为单位，返回给定键的剩余生存时间 (Time To Live)                      |
| `EXPIRE <key> <seconds>`                      | 为给定键设置生存时间                                                     |
| `PERSIST <key>`                               | 移除给定键的生存时间，使其永久保存                                       |
| `RENAME <key> <newkey>`                       | 修改键的名称                                                             |

---

## # 字符串 (String)

字符串是 Redis 最基本的数据类型，可以存储任何类型的数据，如文本、序列化的 JSON 或二进制数据。

| 命令                                     | 描述                                             |
| :--------------------------------------- | :----------------------------------------------- |
| `SET <key> <value>`                      | 设置指定键的值                                   |
| `GET <key>`                              | 获取指定键的值                                   |
| `SETEX <key> <seconds> <value>`          | 设置键值对并指定过期时间                         |
| `SETNX <key> <value>`                    | 只有在键不存在时才设置键的值 (SET if Not eXists) |
| `MSET <key1> <value1> [key2 value2 ...]` | 同时设置一个或多个键值对                         |
| `MGET <key1> [key2 ...]`                 | 获取所有给定键的值                               |
| `INCR <key>`                             | 将键中储存的数字值增一 (原子操作)                |
| `DECR <key>`                             | 将键中储存的数字值减一 (原子操作)                |
| `INCRBY <key> <increment>`               | 将键所储存的值加上指定的增量值                   |

---

## # 哈希 (Hash)

哈希是一个键值对的集合，非常适合用于存储对象。

| 命令                                                | 描述                                             |
| :-------------------------------------------------- | :----------------------------------------------- |
| `HSET <key> <field> <value>`                        | 将哈希表 `key` 中的字段 `field` 的值设为 `value` |
| `HGET <key> <field>`                                | 获取存储在哈希表中指定字段的值                   |
| `HMSET <key> <field1> <value1> [field2 value2 ...]` | 同时将多个 `field-value` 对设置到哈希表中        |
| `HMGET <key> <field1> [field2 ...]`                 | 获取所有给定字段的值                             |
| `HGETALL <key>`                                     | 获取在哈希表中指定键的所有字段和值               |
| `HKEYS <key>`                                       | 获取哈希表中的所有字段                           |
| `HVALS <key>`                                       | 获取哈希表中的所有值                             |
| `HDEL <key> <field1> [field2 ...]`                  | 删除一个或多个哈希表字段                         |
| `HEXISTS <key> <field>`                             | 查看哈希表的指定字段是否存在                     |

---

## # 列表 (List)

列表是简单的字符串列表，按照插入顺序排序。你可以添加一个元素到列表的头部（左边）或者尾部（右边）。

| 命令                                | 描述                                           |
| :---------------------------------- | :--------------------------------------------- |
| `LPUSH <key> <value1> [value2 ...]` | 将一个或多个值插入到列表头部                   |
| `RPUSH <key> <value1> [value2 ...]` | 将一个或多个值插入到列表尾部                   |
| `LPOP <key>`                        | 移出并获取列表的第一个元素                     |
| `RPOP <key>`                        | 移出并获取列表的最后一个元素                   |
| `LLEN <key>`                        | 获取列表的长度                                 |
| `LRANGE <key> <start> <stop>`       | 获取列表指定范围内的元素 (-1 表示最后一个元素) |
| `LINDEX <key> <index>`              | 通过索引获取列表中的元素                       |
| `LSET <key> <index> <value>`        | 通过索引设置列表元素的值                       |
| `LTRIM <key> <start> <stop>`        | 对一个列表进行修剪，只保留指定区间内的元素     |

---

## # 集合 (Set)

集合是字符串类型的**无序**集合。集合成员是唯一的，这意味着集合中不能出现重复的数据。

| 命令                                 | 描述                               |
| :----------------------------------- | :--------------------------------- |
| `SADD <key> <member1> [member2 ...]` | 向集合添加一个或多个成员           |
| `SMEMBERS <key>`                     | 返回集合中的所有成员               |
| `SISMEMBER <key> <member>`           | 判断 `member` 元素是否是集合的成员 |
| `SCARD <key>`                        | 获取集合的成员数                   |
| `SREM <key> <member1> [member2 ...]` | 移除集合中一个或多个成员           |
| `SPOP <key> [count]`                 | 随机移除并返回集合中一个或多个成员 |
| `SUNION <key1> [key2 ...]`           | 返回所有给定集合的并集             |
| `SINTER <key1> [key2 ...]`           | 返回所有给定集合的交集             |
| `SDIFF <key1> [key2 ...]`            | 返回所有给定集合的差集             |

---

## # 有序集合 (Sorted Set / ZSet)

有序集合和集合一样也是字符串类型元素的集合，且不允许重复的成员。不同的是每个元素都会关联一个 `double` 类型的**分数 (score)**。Redis 正是通过分数来为集合中的成员进行从小到大的排序。

| 命令                                                 | 描述                                                      |
| :--------------------------------------------------- | :-------------------------------------------------------- |
| `ZADD <key> <score1> <member1> [score2 member2 ...]` | 向有序集合添加一个或多个成员，或者更新已存在成员的分数    |
| `ZRANGE <key> <start> <stop> [WITHSCORES]`           | 通过索引区间返回有序集合成指定区间内的成员 (按分数值递增) |
| `ZREVRANGE <key> <start> <stop> [WITHSCORES]`        | 返回有序集中指定区间内的成员 (按分数值递减)               |
| `ZRANGEBYSCORE <key> <min> <max> [WITHSCORES]`       | 通过分数返回有序集合指定区间内的成员                      |
| `ZCARD <key>`                                        | 获取有序集合的成员数                                      |
| `ZSCORE <key> <member>`                              | 返回有序集中，成员的 score 值                             |
| `ZREM <key> <member1> [member2 ...]`                 | 移除有序集合中的一个或多个成员                            |
| `ZCOUNT <key> <min> <max>`                           | 计算在有序集合中指定分数区间的成员数                      |

---

## Redis 发展历程与 architecture 演进

## # 版本发展

| 版本      | 发布时间 | 主要特性                                   |
| :-------- | :------- | :----------------------------------------- |
| Redis 1.0 | 2009 年  | 基础键值存储，5 种基本数据结构             |
| Redis 2.0 | 2010 年  | 引入虚拟内存、发布订阅                     |
| Redis 2.2 | 2010 年  | 持久化改进、主从复制                       |
| Redis 2.6 | 2012 年  | Lua 脚本支持、过期键处理优化               |
| Redis 2.8 | 2013 年  | 部分重同步、Sentinel 高可用                |
| Redis 3.0 | 2015 年  | **Redis Cluster 集群支持**                 |
| Redis 4.0 | 2017 年  | 模块系统、内存优化、混合持久化             |
| Redis 5.0 | 2018 年  | **Stream 数据结构**、动态 HZ               |
| Redis 6.0 | 2020 年  | 多线程 I/O、ACL 权限控制、SSL              |
| Redis 7.0 | 2022 年  | Redis Functions、多 ACL 用户、Cluster 分片 |

## # architecture 演进路径

### 1. 单机模式 (Single Instance)

```


### 2. 主从复制 (Master-Slave)

```

### 3. Sentinel 高可用 (Redis Sentinel)

```


### 脑裂问题 (Split-Brain)

* *定义**: 脑裂是指在分布式系统中，由于网络分区或节点故障，导致系统中出现多个"大脑"（多个节点都认为自己是主节点）的情况。

* *Redis中的脑裂场景**:

```

PartitionB: Sentinel2,3 ←→ Slave1 ←→ Slave2 (ElectNew master)

````


* *Redis脑裂预防机制**:

1. **Sentinel奇数部署**: 确保故障转移时有明确的多数派

```bash
# Recommended configuration：At least3Sentinel
Sentinel1, Sentinel2, Sentinel3

````

# At leastNeed2Slave Node，maximum delay10Second

min-slaves-to-write 2
min-slaves-max-lag 10

```

sentinel = Sentinel([('localhost', 26379), ('localhost', 26380), ('localhost', 26381)])
master = sentinel.master_for('mymaster', socket_timeout=0.1)

```

### 4. 集群模式 (Redis Cluster)

````
___
## Redis 集群详解

## # Sentinel 模式

### 核心功能
1. **监控 (Monitoring)**: 监控master和slave健康状态
2. **通知 (Notification)**: 故障时通知管理员
3. **自动故障转移 (Automatic Failover)**: 自动选举新master
4. **配置提供 (Configuration Provider)**: 为客户端提供当前master地址


### 工作原理

```bash
# SentinelConfigFile
sentinel monitor mymaster 127.0.0.1 6379 2
sentinel down-after-milliseconds mymaster 30000
sentinel parallel-syncs mymaster 1
sentinel failover-timeout mymaster 180000

````

4. **新主选择**: 选择最优 slave 提升为 master
5. **配置更新**: 更新所有节点配置

## # Cluster 集群模式

### 集群特性

- **去中心化**: 无单点故障

- **数据分片**: 自动数据分布

- **高可用**: master 故障自动切换

- **在线扩缩容**: 支持动态添加/删除节点

### 数据分片算法

```bash
# CalculateKey哈希Slot
HASH_SLOT = CRC16(key) % 16384

# SlotAllocationExample（3Master Node）
Master1: 0-5461 (5462Slot)
Master2: 5462-10923 (5462Slot)
Master3: 10924-16383 (5460Slot)

```

127. 0.0.1:7003 127.0.0.1:7004 127.0.0.1:7005 \

- -cluster-replicas 1

# ViewClusterInformation

CLUSTER INFO
CLUSTER NODES

# Re-Sharding

redis-cli --cluster reshard 127.0.0.1:7000

# AddNode

redis-cli --cluster add-node 127.0.0.1:7006 127.0.0.1:7000

````
布隆过滤器是一种概率性数据结构，用于高效判断一个元素是否在集合中。

### 核心特性
- **误报率**: 可能误判存在，但不会误判不存在


- **空间效率**: 使用位数组，空间复杂度低


- **时间复杂度**: O(k) 查询时间，k为哈希函数数量


### 实现原理

```python
# 基本流程
1. Initialize: Createm位位Array，k哈希Function
2. 添加元素: 对元素计算 k 个哈希值，设置对应位为1
3. Query元素: Calculatek哈希Value，Check对应位isNo都为1

````

# 最优位数组大小

m = -n \*\* ln(p) / (ln(2))^2

# 最优哈希函数数量

k = (m/n) \*\* ln(2)

# 其中：n=元素数量，p=误报率，m=位数组大小，k=哈希函数数量

````

```bash
# 加载 RedisBloom 模块
MODULE LOAD /path/to/redisbloom.so

````

# 添加元素

BF.ADD myfilter "user123"
BF.MADD myfilter "user1" "user2" "user3"

# 检查元素

BF.EXISTS myfilter "user123"
BF.MEXISTS myfilter "user1" "user2"

# GetInformation

BF.INFO myfilter

```
4. **推荐系统**: 已推荐内容过滤
___
## Stream 流数据结构

## # 基本概念

Stream是Redis 5.0引入的新数据结构，主要用于消息队列和事件流处理。

### 核心特性
- **持久化消息队列**: 消息持久化存储


- **消费者组**: 支持多消费者协作


- **消息确认**: 支持消息确认机制


- **历史消息**: 可以查询历史消息


### 消息ID结构

```

# 添加消息

XADD mystream \*\* field1 value1 field2 value2
XADD mystream 1609459200000-0 user "john" action "login"

# 读取消息

XREAD COUNT 2 STREAMS mystream 0
XREAD BLOCK 1000 STREAMS mystream $ # 阻塞读取新消息

# ViewStreamInformation

XINFO STREAM mystream
XLEN mystream

# 范围查询

XRANGE mystream - +
XRANGE mystream 1609459200000 1609459300000

```

# 消费者读取
XREADGROUP GROUP mygroup consumer1 COUNT 1 STREAMS mystream >

# 确认消息
XACK mystream mygroup 1609459200000-0

# 查看消费者组信息
XINFO GROUPS mystream
XINFO CONSUMERS mystream mygroup

# 处理 pending 消息
XPENDING mystream mygroup
XCLAIM mystream mygroup consumer2 1800000 1609459200000-0

```

# 修剪 Stream

XTRIM mystream MAXLEN 1000
XTRIM mystream MAXLEN ~ 1000 # 近似修剪，Performance 更好

````
| 多消费者 | ❌ | ✅ | ✅ |
| 消息确认 | ❌ | ❌ | ✅ |
| 历史消息 | ✅ | ❌ | ✅ |
| 消费者组 | ❌ | ❌ | ✅ |
___
## 面试高频考点

## # 持久化机制

### RDB (Redis Database)

```bash
# ConfigFileSet
save 900 1 # 900seconds with at least1key变化
save 300 10 # 300seconds with at least10key变化
save 60 10000 # 60seconds with at least10000key变化

# 手动触发
SAVE # SynchronizationSave（阻塞）
BGSAVE # AsyncSave（After台）

````

### AOF (Append Only File)

```bash
# ConfigOption
appendonly yes
appendfsync always # 每次写入立即同步
appendfsync everysec # 每秒同步一次（推荐）
appendfsync no # 由OS决定SynchronizationWhen机

```

### 混合持久化 (Redis 4.0+)

```bash
aof-use-rdb-preamble yes

```

```bash
# 配置最大内存
maxmemory 2gb

# 淘汰策略
maxmemory-policy allkeys-lru

```

| `allkeys-lfu` | 所有 key 中淘汰最少频率的 |
| `volatile-lru` | 有过期时间的 key 中淘汰最少使用的 |
| `volatile-lfu` | 有过期时间的 key 中淘汰最少频率的 |
| `volatile-random` | 有过期时间的 key 中随机淘汰 |
| `volatile-ttl` | 淘汰即将过期的 key |

## # 缓存问题解决方案

### 1. 缓存穿透

- **问题\*\***: 查询不存在的数据，绕过缓存直接查数据库

- **解决方案\*\***:

* 布隆过滤器预过滤

* 空值缓存（设置较短过期时间）

* 参数校验

### 2. 缓存雪崩

- **问题\*\***: 大量缓存同时失效，数据库压力激增

- **解决方案\*\***:

* 随机过期时间

* 缓存预热

* 多级缓存

* 限流降级

### 3. 缓存击穿

- **问题\*\***: 热点数据过期，大量请求直达数据库

- **解决方案\*\***:

* 互斥锁重建缓存

* 异步更新缓存

* 热点数据永不过期

## # 分布式锁实现

### 基于 SETNX 的简单锁

```bash
# 加锁
SET lock_key unique_value PX 30000 NX

# 释放锁（LuaScript保证原子性）
if redis.call("get", KEYS[1]) == ARGV[1] then
return redis.call("del", KEYS[1])
else
return 0
end

```

2. 超过 N/2+1 个实例加锁成功才算成功
3. 加锁总时间要小于锁过期时间
4. 释放所有实例上的锁

````
- 小数据量使用ziplist编码（节省内存）

- 大数据量使用hashtable编码（提高性能）

### 2. 批量操作

```bash
# 使用 pipeline 减少网络往返
PIPELINE
SET key1 value1
SET key2 value2
EXEC

# UseMGET/MSETBatchOperation
MSET key1 value1 key2 value2
MGET key1 key2

````

# ConfigOptimize

hash-max-ziplist-entries 512
hash-max-ziplist-value 64
list-max-ziplist-size -2
set-max-intset-entries 512

````
___
## 数据库技术选型对比

## # 关系型数据库 (RDBMS)

### MySQL
* *特点**: 开源、成熟、社区活跃

| 方面 | 描述 |
|:---|:---|
| **存储引擎** | InnoDB(事务)、MyISAM(性能) |
| **事务支持** | 完整ACID支持 |
| **复制** | 主从复制、主主复制 |
| **分片** | 应用层分片 |
| **适用场景** | Web应用、电商系统、金融系统 |

```sql
- - IndexOptimize
CREATE INDEX idx_user_email ON users(email);
EXPLAIN SELECT * FROM users WHERE email = 'test@example.com';

- - PartitionTable
CREATE TABLE orders (
id INT,
order_date DATE,
amount DECIMAL(10,2)
) PARTITION BY RANGE (YEAR(order_date)) (
PARTITION p2022 VALUES LESS THAN (2023),
PARTITION p2023 VALUES LESS THAN (2024)
);

````

| **数据类型** | 丰富的内置类型(JSON、数组、地理) |
| **索引类型** | B-tree、Hash、GiST、SP-GiST、GIN、BRIN |
| **并发控制** | MVCC 多版本并发控制 |
| **扩展性** | 丰富的插件生态 |
| **适用场景** | 复杂查询、数据分析、地理信息系统 |

```sql
- - JSONOperation
SELECT data->>'name' FROM users WHERE data @> '{"age": 25}';

- - ArrayClassType
CREATE TABLE posts (
id SERIAL,
tags TEXT[]
);
INSERT INTO posts (tags) VALUES (ARRAY['postgres', 'database']);

- - 窗口Function
SELECT name, salary,
RANK() OVER (ORDER BY salary DESC) as rank
FROM employees;

```

|:---|:---|
| **数据模型** | BSON 文档 |
| **查询语言** | MongoDB Query Language |
| **分片** | 自动分片(Auto-Sharding) |
| **复制** | 副本集(Replica Set) |
| **适用场景** | 内容管理、实时分析、物联网 |

```javascript
// DocumentationOperation
db.users.insertOne({
  name: "John",
  age: 30,
  address: {
    city: "New York",
    state: "NY",
  },
  hobbies: ["reading", "swimming"],
});

// Aggregate管道
db.orders.aggregate([
  { $match: { status: "completed" } },
  { $group: { _id: "$customer_id", total: { $sum: "$amount" } } },
  { $sort: { total: -1 } },
]);

// Index
db.users.createIndex({ email: 1 }, { unique: true });
db.posts.createIndex({ title: "text", content: "text" }); // 全文Index
```

| **数据模型** | 宽列存储 |
| **一致性** | 可调一致性 |
| **分区** | 一致性哈希 |
| **容错** | 无单点故障 |
| **适用场景** | 时序数据、日志系统、推荐系统 |

```sql
- - Table设计（ByQuery设计）
CREATE TABLE user_posts (
user_id UUID,
post_time TIMESTAMP,
post_id UUID,
content TEXT,
PRIMARY KEY (user_id, post_time, post_id)
) WITH CLUSTERING ORDER BY (post_time DESC);

- - Query
SELECT * FROM user_posts
WHERE user_id = 123e4567-e89b-12d3-a456-426614174000
AND post_time >= '2023-01-01';

```

| **PostgreSQL** | 关系型 | 强一致 | 垂直扩展 | ✅ 很强 | 中 | 复杂业务、分析 |
| **Redis** | 键值 | 最终一致 | 水平扩展 | ❌ 弱 | 低 | 缓存、会话 |
| **MongoDB** | 文档 | 强一致 | 水平扩展 | ✅ 中等 | 中 | 内容管理、快速开发 |
| **Cassandra** | 列族 | 可调一致 | 线性扩展 | ❌ 弱 | 高 | 大数据、高并发写入 |
| **HBase** | 列族 | 强一致 | 水平扩展 | ❌ 弱 | 高 | 大数据存储、实时读写 |

## # CAP 理论与选择

### CAP 理论

- **C (Consistency)**: 一致性

- **A (Availability)**: 可用性

- **P (Partition tolerance)**: 分区容错性

### 数据库在 CAP 中的定位

```

AP系统 (高可用性)
├── Cassandra
├── DynamoDB
└── CouchDB

CA系统 (NetworkPartition少见)
├── 传统RDBMS (单机)
└── Redis (单机模式)

```

│ │ ├── is → PostgreSQL
│ │ └── No → MySQL
│ └── 简单键值访问？ → Redis
├── 中型 (1TB - 10TB)
│ ├── 结构化数据？
│ │ ├── 关系型需求 → MySQL/PostgreSQL + 分库分表
│ │ └── 文档类型需求 → MongoDB
│ └── 缓存需求？ → Redis Cluster
└── 大型 (> 10TB)
├── 实时读写 → HBase
├── 高并发写 → Cassandra
└── 复杂分析 → Hadoop 生态 + Hive

```
↓
MySQL (TransactionLayer)
↓
MongoDB (DocumentationStorage)
↓
HBase (大Data storage)

```

def **init**(self):
self.redis = Redis()
self.mysql = MySQL()
self.mongodb = MongoDB()

def get_user_profile(self, user_id):

# 1. 先查 RedisCache

cached = self.redis.get(f"user:{user_id}")
if cached:
return json.loads(cached)

# 2. 查 MySQLGetBasic information

user_basic = self.mysql.query(
"SELECT \*\* FROM users WHERE id = %s", user_id
)

# 3. 查 MongoDBGetExtensionInformation

user_extended = self.mongodb.find_one(
{"user_id": user_id}, collection="user_profiles"
)

# 4. 合并数据并缓存

user_data = {**user_basic, **user_extended}
self.redis.setex(f"user:{user_id}", 3600, json.dumps(user_data))

return user_data

- **MySQL**: 10K+ (SSD + 索引)

- **MongoDB**: 20K+ (内存 + 索引)

- **PostgreSQL**: 15K+ (优化后)

- **Cassandra**: 50K+ (分布式)

### 写性能 (TPS)

- **Redis**: 80K+ (内存)

- **MySQL**: 5K+ (InnoDB)

- **MongoDB**: 15K+ (异步写入)

- **Cassandra**: 100K+ (LSM 树)

- **HBase**: 50K+ (WAL + MemStore)

### 存储成本

- **内存数据库**: $100/GB/月 (Redis)

- **SSD 存储**: $1/GB/月 (MySQL/PostgreSQL)

- **HDD 存储**: $0.1/GB/月 (MongoDB/Cassandra)

---

## 总结与建议

## # 选型原则

1. **业务需求优先**: 根据具体业务场景选择
2. **团队能力**: 考虑团队的技术栈和维护能力
3. **成本控制**: 综合考虑开发、运维、硬件成本
4. **未来扩展**: 预留技术演进空间

## # 最佳实践

- **读多写少**: MySQL/PostgreSQL + Redis

- **写多读少**: Cassandra/MongoDB + Redis

- **复杂查询**: PostgreSQL + 数据仓库

- **实时分析**: HBase + Spark/Flink

- **混合负载**: 多数据库架构 + 数据同步

```



<!-- 04-Reference/Engineering/risk_control_sdk_build_guide.md -->

# Risk Control SDK 编译指南

Risk Control SDK 是一个用于移动应用的设备指纹识别和安全评估系统，基于 JNI 架构实现。本指南将详细说明如何编译和构建该 SDK。
___
## 目录

1. [项目概述](#项目概述)
2. [环境准备](#环境准备)
3. [项目结构](#项目结构)
4. [编译步骤](#编译步骤)
5. [构建选项](#构建选项)
6. [多平台编译](#多平台编译)
7. [问题排查](#问题排查)
___
## 项目概述

Risk Control SDK 提供以下核心功能：

- **设备指纹识别**: 硬件、软件、网络、行为指纹采集


- **安全检测**: 模拟器、Root、调试器、Hook框架检测


- **反逆向工程**: 代码混淆、字符串加密、运行时完整性监控


- **风险评估**: 基于多维度数据的风险评分算法


### 技术架构

```

├─────────────────┤
│ Native Layer │ ← C/C++ CoreImplement
└─────────────────┘

````

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y build-essential cmake git

# macOS
brew install cmake
xcode-select --install

# Windows (Use MSYS2)
pacman -S base-devel cmake git

````

# VerifyInstall

java -version
javac -version

```
unzip android-ndk-r25c-linux.zip
export ANDROID_NDK=/path/to/android-ndk-r25c

# Download android SDK (optional, Used forTest)
wget https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip

```

# MemoryCheck (Only Linux)

sudo apt install -y valgrind

```
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH

```

├── docs/ # DocumentationDirectory
│ ├── ArtMethod_Direct_Registration.md
│ └── diagrams/ # Architecture Diagramtable
├── examples/ # Example code
│ ├── ArtMethodDemo.java
│ └── RiskControlDemo.java
├── include/ # Header file directory
├── scripts/ # Build scripts
│ ├── build.sh.in # Generic build script template
│ └── build-android.sh.in # Android build script template
└── src/ # Source code
├── java/ # Java layer implementation
│ └── com/riskcontrol/
│ ├── DeviceFingerprint.java
│ ├── RiskControlSDK.java
│ ├── RiskScore.java
│ └── SecurityResult.java
└── native/ # Native layer implementation
├── anti_reverse.c/.h # Anti-reverse engineering protection
├── art_method_hook.c/.h # ART method hooking
├── risk_control.c/.h # Main risk control logic
└── svc_syscall.c/.h # System call handling

````

```bash
cd /path/to/android_reversing/playground
git clone <repository-url> risk-control-sdk # orUseExistingCode
cd risk-control-sdk

````

```

# orSpecifiedDetailedOption
cmake -DCMAKE_BUILD_TYPE=Release \
- DENABLE_DEBUG=OFF \
- DENABLE_ANTI_REVERSE=ON \
- DENABLE_SVC_SYSCALLS=ON \
..

```

# orCompileSpecificTarget

make riskcontrol # Compile Native Library
make compile_java # Compile Java Code
make create_jar # Create JAR Package
make example # CompileExampleProgram

```

# Should see:

# - libriskcontrol.so (Linux) or libriskcontrol.jnilib (macOS)

# - RiskControlSDK.jar

# - examples/

# Run tests
./examples/RiskControlDemo

```

echo $ANDROID_NDK

# ShouldOutput: /path/to/android-ndk-r25c

# Verify NDK Toolchain

$ANDROID_NDK/ndk-build --version

```
cmake -P scripts/generate_build_scripts.cmake

# Execute android Build
chmod +x build-android.sh
./build-android.sh

```

cd build-android

# Config android Toolchain

cmake -DCMAKE_TOOLCHAIN_FILE=$ANDROID_NDK/build/cmake/android.toolchain.cmake \
-DANDROID_ABI=arm64-v8a \
-DANDROID_PLATFORM=android-21 \
-DANDROID_NDK=$ANDROID_NDK \
-DBUILD_ANDROID=ON \
-DCMAKE_BUILD_TYPE=Release \
..

# Compile

make -j$(nproc)

```

for ARCH in "${ARCHITECTURES[@]}"; do
echo "Building for $ARCH..."
mkdir -p build-android-$ARCH
cd build-android-$ARCH

cmake -DCMAKE_TOOLCHAIN_FILE=$ANDROID_NDK/build/cmake/android.toolchain.cmake \
- DANDROID_ABI=$ARCH \
- DANDROID_PLATFORM=android-21 \
- DANDROID_NDK=$ANDROID_NDK \
- DBUILD_ANDROID=ON \
- DCMAKE_BUILD_TYPE=Release \
..

make -j$(nproc)
cd ..
done

```

|---------|--------|------|
| `CMAKE_BUILD_TYPE` | `Release` | 构建类型: Debug/Release/RelWithDebInfo |
| `ENABLE_DEBUG` | `OFF` | 启用调试模式和日志输出 |
| `ENABLE_ANTI_REVERSE` | `ON` | 启用反逆向工程保护 |
| `ENABLE_SVC_SYSCALLS` | `ON` | 启用 SVC 系统调用支持 |
| `BUILD_ANDROID` | `OFF` | Android 平台构建模式 |
| `BUILD_EXAMPLES` | `ON` | 构建示例程序 |
| `BUILD_DOCS` | `OFF` | 生成 Doxygen 文档 |

### 使用示例

```bash
# DebugBuild
cmake -DCMAKE_BUILD_TYPE=Debug -DENABLE_DEBUG=ON ..

# 最小化构建 (禁用保护功能)
cmake -DENABLE_ANTI_REVERSE=OFF -DENABLE_SVC_SYSCALLS=OFF ..

# ReleaseBuild (全功能)
cmake -DCMAKE_BUILD_TYPE=Release \
- DENABLE_ANTI_REVERSE=ON \
- DENABLE_SVC_SYSCALLS=ON \
- DBUILD_EXAMPLES=OFF \
..

```

|------|------|--------|--------|
| Linux | x86_64 | GCC/Clang | `libriskcontrol.so` |
| macOS | x86_64/arm64 | Clang | `libriskcontrol.jnilib` |
| Windows | x86_64 | MinGW/MSVC | `riskcontrol.dll` |
| Android | arm64-v8a | Android NDK | `libriskcontrol.so` |
| Android | armeabi-v7a | Android NDK | `libriskcontrol.so` |
| Android | x86/x86_64 | Android NDK | `libriskcontrol.so` |

### 平台特定配置

#### Linux 编译

```bash
# Ubuntu/Debian 依赖
sudo apt install -y build-essential cmake openjdk-8-jdk

# Compile
mkdir build-linux && cd build-linux
cmake -DCMAKE_BUILD_TYPE=Release ..
make -j$(nproc)

```

# Compile (Support Universal Binary)

mkdir build-macos && cd build-macos
cmake -DCMAKE_BUILD_TYPE=Release \
-DCMAKE_OSX_ARCHITECTURES="x86_64;arm64" \
..
make -j$(sysctl -n hw.ncpu)

```

mkdir build-windows && cd build-windows
cmake -G "MinGW Makefiles" -DCMAKE_BUILD_TYPE=Release ..
mingw32-make -j$(nproc)

```

```
java -version
javac -version

2. 查找正确 JDK Path


# macOS Homebrew Install OpenJDK
ls /usr/local/Cellar/openjdk/

# Ubuntu/Debian
ls /usr/lib/jvm/

# 手动查找 JNI 头文件
find /usr -name "jni.h" 2>/dev/null

3. 设置正确的 JAVA_HOME


# macOS Homebrew OpenJDK Example
export JAVA_HOME=/usr/local/Cellar/openjdk/24.0.1/libexec/openjdk.jdk/Contents/Home

# Ubuntu/Debian Example
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

4. 验证 JNI 头文件存在
ls -la $JAVA_HOME/include/jni.h

5. Re-Run CMake
cmake .

```

解决: Add 平台兼容性 Process

in/at art_method_hook.c InModify:
// originalCode

# include <sys/system_properties.h>

// Modify 为平台兼容

# ifdef **andROID**

# include <sys/system_properties.h>

# else

// Not android 平台替代 Implement

# define PROP_VALUE_MAX 256

static int \_\_system_property_get(const char* name, char* value) {
if (strcmp(name, "ro.build.version.sdk") == 0) {
strcpy(value, "28"); // 模拟 Android API 28
return strlen(value);
}
value[0] = '\0';
return 0;
}

# endif

```
#include <stdint.h> // Add标准IntegerClassTypeSupport

```

// Add 结构体 Define
typedef struct {
const char* name;
const char* signature;
void\*\* fnPtr;
} native_method_t;

// UpdateFunction 声明
int register_native_methods_direct(JNIEnv* env, const char* class_name,
const native_method_t\*\* methods, int method_count);

```
// originalCode（Delete）
typedef struct {
const char* name;
const char* signature;
void* fnPtr;
} native_method_t;

// 修改为前向声明
typedef struct native_method_t native_method_t;

```

uint32_t calculate_string_hash(const char* str); // 原 calculate_hash
char* decrypt_raw_string(const unsigned char\*\* encrypted, size_t len); // 原 decrypt_string

// MeanwhileUpdate .c FileinFunctionImplementandCall

```
#else
// Not ARM architecture模拟Implement（Used for桌面平台Test）
static inline long svc_call(long number, long arg1, long arg2, long arg3, long arg4, long arg5, long arg6) {
switch (number) {
case __NR_getpid: return getpid();
case __NR_getuid: return getuid();
default: return -1;
}
}
#endif

```

if (!env->functions->FindClass ||

// Modify 为
if (!(\*\*env)->FindClass ||

```


- Check JDK InstallComplete性


- 对于 Android: 确认 NDK Version >= r20

```

最佳解决方案: CreatePublicClassTypeDefineFile

1. Create src/native/common_types.h:
   #ifndef COMMON_TYPES_H
   #define COMMON_TYPES_H
   typedef struct {
   const char* name;
   const char* signature;
   void\*\* fnPtr;
   } native_method_t;
   #endif

2. in/atAllNeed 此 ClassType 头 FileInContains:
   #include "common_types.h"

3. 删除其他文件中的重复定义

```

Error: implicit declaration of function 'dladdr'
解决: Enabled GNU Extension并Add dl Library链接

1. 在 art_method_hook.c 开头添加（必须在所有 #include 之Before）:
// Enabled GNU Extension功能以确保 dladdr 可用
#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif

#include "art_method_hook.h"
// ... 其他 includes ...
#include <dlfcn.h>

2. in/at CMakeLists.txt InAdd dl Library链接:


# 链接库
target_link_libraries(riskcontrol ${JNI_LIBRARIES})

# in/atNot android 平台上链接 dl Library
if(NOT BUILD_ANDROID)
target_link_libraries(riskcontrol dl)
endif()

3. Re-ConfigProject:
rm -f CMakeCache.txt
cmake .
make clean
make -j8

```

```
sudo chown -R $USER:$USER build/

```

make -j$(nproc) # Linux
make -j$(sysctl -n hw.ncpu) # macOS

```

# Use Ninja Build系统 (更快)
cmake -G Ninja ..
ninja

```

export CC="ccache gcc"
export CXX="ccache g++"

```
cmake --verbose ..

# Make DetailedOutput
make VERBOSE=1

```

otool -L libriskcontrol.jnilib # macOS

# 检查符号

nm -D libriskcontrol.so
objdump -T libriskcontrol.so

```

# Java JNI Debug
java -Djava.library.path=./build -verbose:jni RiskControlDemo

```

// Load SDK
System.loadLibrary("riskcontrol");

// Use SDK
RiskControlSDK sdk = RiskControlSDK.getInstance();
SecurityResult result = sdk.performSecurityCheck();
DeviceFingerprint fingerprint = sdk.getDeviceFingerprint();
RiskScore score = sdk.calculateRiskScore(fingerprint, result);

```
// ...
sourceSets {
main {
jniLibs.srcDirs = ['libs']
}
}
}

dependencies {
implementation files('libs/RiskControlSDK.jar')
}

```

cp build/RiskControlSDK.jar /target/project/libs/

```
2. **构建选项**: 根据需求选择合适的功能开关和优化级别
3. **多平台支持**: 使用统一的 CMake 配置支持多种目标平台
4. **问题排查**: 遇到问题时，检查环境变量、依赖库和权限设置


通过遵循本指南，你应该能够成功编译和集成 Risk Control SDK 到你的项目中。


<!-- 04-Reference/Engineering/Data-Analysis/data_warehousing_and_processing.md -->

___
# 数据分析：数据仓库与计算引擎

当通过逆向和爬虫采集到海量数据后（例如，数亿条用户行为日志、商品信息），如何存储、管理和分析这些数据，就成了大数据领域的核心问题。本节将介绍主流的数据仓库和分布式计算引擎技术。

___

## 1. 数据仓库 (Data Warehouse)

数据仓库是一个用于存储和分析海量结构化、半结构化数据的系统。它与业务数据库（OLTP）不同，其核心目标是支持复杂的分析查询（OLAP）。

### a) Hive

* **定位**: 基于 Hadoop 的一个**数据仓库基础架构**。

* **核心思想**: Hive 允许你使用标准的 **SQL 语言** 来查询存储在 Hadoop 分布式文件系统（HDFS）上的大规模数据集。它将 SQL 查询翻译成 MapReduce、Tez 或 Spark 任务来执行。

* **元数据 (Metastore)**: Hive 的核心是其元数据存储。它记录了"表"的结构（列名、数据类型）与 HDFS 上的文件（如 CSV, Parquet, ORC 文件）之间的映射关系。本质上，Hive 提供了一种"给文件系统套上一个结构化外壳"的能力。

* **适用场景**:
    * 对海量（TB/PB 级）的、非实时的数据进行离线分析和 ETL（提取、转换、加载）。
    * 构建企业级的数据仓库，为数据分析师和 BI 报表提供统一的 SQL 查询入口。

### b) HBase

* **定位**: 一个分布式的、可伸缩的、面向列的 **NoSQL 数据库**。它构建在 HDFS 之上，并模仿 Google Bigtable 的设计。

* **核心特点**:
    * **海量存储**: 专为存储数十亿行、数百万列的超大规模稀疏数据集而设计。
    * **实时读写**: 与 Hive 主要用于离线批量分析不同，HBase 的核心优势在于支持对海量数据的**低延迟随机读写**。
    * **面向列**: 数据按列族（Column Family）组织。一个列族中的所有列在物理上存储在一起，这使得对特定列的读取非常高效。
    * **无模式 (Schemaless)**: 你可以随时向一个列族中添加新的列，而无需预先定义表结构。
* **适用场景**:
    * 需要对海量数据进行实时、随机访问的场景，例如用户画像系统、实时推荐引擎的特征库、监控数据的存储。
    * 作为数据采集系统的"落地层"，接收实时写入的数据流，然后由 Hive 或 Spark 进行后续的批量分析。

### Hive vs. HBase

| 特性 | Hive | HBase |
| --- | --- | --- |
| **数据库类型** | 数据仓库 (SQL on Hadoop) | NoSQL 数据库 (面向列) |
| **核心用途** | 批量分析 (OLAP) | 实时随机读写 (OLTP) |
| **延迟** | 高（分钟级） | 低（毫秒级） |
| **数据模型** | 结构化 | 半结构化/无模式 (稀疏表) |
| **语言** | SQL (HiveQL) | Java API, Shell, Thrift/REST |

___

## 2. 分布式计算引擎

计算引擎负责实际执行数据处理任务。现代计算引擎通过在内存中进行计算，极大地提升了处理速度。

### a) Spark

* **定位**: 一个快速、通用、可扩展的**分布式计算引擎**。

* **核心概念: RDD (弹性分布式数据集)**: Spark 的基础数据结构。它是一个不可变的、被分区到集群中多个节点上的元素集合，支持丰富的转换（`map`, `filter`, `join`）和行动（`count`, `collect`, `save`）操作。RDD 的"弹性"体现在其血缘关系（Lineage），任何分区的丢失都可以根据其转换历史被重新计算出来。

* **DataFrame & Spark SQL**: 在 RDD 之上，Spark 提供了更高级的 DataFrame API，它将数据组织成带有命名列的二维表，类似于关系型数据库的表。这使得你可以使用 Spark SQL 来进行结构化数据处理，并且 Spark 的 Catalyst 优化器会自动对你的查询进行优化。

* **生态系统**:
    * **Spark Streaming**: 用于处理实时数据流（Micro-batching）。
    * **MLlib**: 提供了一套丰富的机器学习算法库。
    * **GraphX**: 用于图计算。
* **适用场景**:
    * 需要高性能的、迭代式的批量数据处理和机器学习任务。
    * 统一批处理和流处理。

### b) Flink

* **定位**: 一个以**真正的流处理 (True Streaming)**为核心的分布式计算引擎。

* **核心特点**:
    * **流为核心**: Flink 的设计哲学是"一切皆是流"，批量计算被看作是流计算的一个特例。它能够以事件驱动的方式，逐条处理数据，实现极低的延迟。
    * **状态管理与窗口**: Flink 提供了强大的状态管理能力，允许你在流处理中维护和更新状态（例如，一个用户的累计消费金额）。它还支持灵活的窗口操作（如滚动窗口、滑动窗口、会话窗口），用于对无界数据流进行聚合分析。
    * **高吞吐与低延迟**: 专为低延迟、高吞吐的实时计算场景设计。
* **适用场景**:
    * 对实时性要求极高的场景，如实时风控、实时推荐、实时监控大盘。
    * 需要进行复杂事件处理（CEP）的场景。

___

## Spark vs. Flink

| 特性 | Spark | Flink |
| --- | --- | --- |
| **核心模型** | 批处理 (Batch) | 流处理 (Streaming) |
| **流处理方式** | 微批次 (Micro-batch) | 逐条处理 (Per-event) |
| **延迟** | 秒级 | 毫秒级 |
| **窗口** | 基于时间的窗口 | 灵活的窗口（时间、计数、会话） |
| **生态** | 更成熟，社区更庞大 | 快速发展，在实时计算领域是事实标准 |

**总结**: 如果你的主要任务是离线分析和机器学习，`Spark` 是一个更通用、更成熟的选择。如果你的核心是需要亚秒级响应的实时计算，`Flink` 则是更专业的工具。在许多现代数据平台中，二者往往会共存，分别处理不同的任务。
___


<!-- 04-Reference/Engineering/Data-Analysis/flink.md -->

# Apache Flink 实时流处理

Apache Flink 是一个分布式流处理框架，专为低延迟、高吞吐量的实时数据处理而设计。
___
## 目录
1. [**Flink 架构**](#flink-架构)
2. [**核心概念**](#核心概念)
3. [**DataStream API**](#datastream-api)
4. [**状态管理**](#状态管理)
5. [**时间与窗口**](#时间与窗口)
6. [**容错机制**](#容错机制)
7. [**性能调优**](#性能调优)
8. [**知识要点**](#知识要点)
___
## Flink 架构

## # 集群架构

```

├── ResourceManager
└── JobMaster
↓
TaskManager1 TaskManager2 TaskManager3
├── Task Slot1 ├── Task Slot1 ├── Task Slot1
├── Task Slot2 ├── Task Slot2 ├── Task Slot2
└── Task Slot3 └── Task Slot3 └── Task Slot3

```
| **TaskManager** | 执行具体任务，管理内存和网络 |
| **Dispatcher** | 接收作业提交，启动JobMaster |
| **ResourceManager** | 管理TaskManager资源 |
| **JobMaster** | 管理单个作业的执行 |

## # 运行时架构

```

Operator1 → Operator2 → Operator3

````

```java
StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

DataStream<String> stream = env
.socketTextStream("localhost", 9999)
.flatMap(new Tokenizer())
.keyBy(value -> value.f0)
.window(TumblingProcessingTimeWindows.of(Time.seconds(5)))
.sum(1);

env.execute("Word Count");

````

```
DataStream<Integer> intStream;

// 2. 元组类型
DataStream<Tuple2<String, Integer>> tupleStream;

// 3. POJO 类型
public class WordCount {
public String word;
public int count;
// constructors, getters, setters
}
DataStream<WordCount> pojoStream;

// 4. Row 类型（动态）
DataStream<Row> rowStream;

```

StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

// 1. Create from collection
DataStream<String> fromCollection = env.fromCollection(Arrays.asList("a", "b", "c"));

// 2. 从文件系统
DataStream<String> fromFile = env.readTextFile("path/to/file");

// 3. 从 Kafka
Properties props = new Properties();
props.setProperty("bootstrap.servers", "localhost:9092");
props.setProperty("group.id", "test");

DataStream<String> fromKafka = env.addSource(
new FlinkKafkaConsumer<>("topic", new SimpleStringSchema(), props));

// 4. 自定义数据源
DataStream<String> customSource = env.addSource(new CustomSourceFunction());

public class CustomSourceFunction implements SourceFunction<String> {
private volatile boolean running = true;

@Override
public void run(SourceContext<String> ctx) throws Exception {
while (running) {
ctx.collect("data-" + System.currentTimeMillis());
Thread.sleep(1000);
}
}

@Override
public void cancel() {
running = false;
}
}

```
DataStream<String> mapped = input.map(String::toUpperCase);

// 2. FlatMap - 一对多Convert
DataStream<String> flatMapped = input.flatMap(
(String line, Collector<String> out) -> {
for (String word : line.split(" ")) {
out.collect(word);
}
});

// 3. Filter - Filter
DataStream<String> filtered = input.filter(s -> s.startsWith("error"));

// 4. KeyBy - Group
KeyedStream<Tuple2<String, Integer>, String> keyed =
tupleStream.keyBy(value -> value.f0);

// 5. Reduce - Aggregate
DataStream<Tuple2<String, Integer>> reduced =
keyed.reduce((a, b) -> new Tuple2<>(a.f0, a.f1 + b.f1));

// 6. Aggregate - 自定义聚合
DataStream<Double> aggregated = keyed
.aggregate(new AverageAggregate());

public class AverageAggregate implements AggregateFunction<Tuple2<String, Integer>, Tuple2<Long, Long>, Double> {
@Override
public Tuple2<Long, Long> createAccumulator() {
return new Tuple2<>(0L, 0L);
}

@Override
public Tuple2<Long, Long> add(Tuple2<String, Integer> value, Tuple2<Long, Long> accumulator) {
return new Tuple2<>(accumulator.f0 + value.f1, accumulator.f1 + 1L);
}

@Override
public Double getResult(Tuple2<Long, Long> accumulator) {
return ((double) accumulator.f0) / accumulator.f1;
}

@Override
public Tuple2<Long, Long> merge(Tuple2<Long, Long> a, Tuple2<Long, Long> b) {
return new Tuple2<>(a.f0 + b.f0, a.f1 + b.f1);
}
}

```

// 2. 写入文件
stream.writeAsText("path/to/output");

// 3. 写入 Kafka
Properties props = new Properties();
props.setProperty("bootstrap.servers", "localhost:9092");

stream.addSink(new FlinkKafkaProducer<>("output-topic", new SimpleStringSchema(), props));

// 4. 写入数据库
stream.addSink(new CustomSinkFunction());

public class CustomSinkFunction extends RichSinkFunction<String> {
private Connection connection;

@Override
public void open(Configuration parameters) throws Exception {
// 初始化数据库连接
connection = DriverManager.getConnection("jdbc:mysql://localhost:3306/test", "user", "password");
}

@Override
public void invoke(String value, Context context) throws Exception {
// 执行插入操作
PreparedStatement stmt = connection.prepareStatement("INSERT INTO table VALUES (?)");
stmt.setString(1, value);
stmt.executeUpdate();
}

@Override
public void close() throws Exception {
if (connection != null) {
connection.close();
}
}
}

````

```java
public class StatefulMap extends RichMapFunction<Tuple2<String, Integer>, Tuple2<String, Integer>> {
private ValueState<Integer> sumState;

@Override
public void open(Configuration config) {
ValueStateDescriptor<Integer> descriptor =
new ValueStateDescriptor<>("sum", Integer.class);
sumState = getRuntimeContext().getState(descriptor);
}

@Override
public Tuple2<String, Integer> map(Tuple2<String, Integer> input) throws Exception {
Integer currentSum = sumState.value();
if (currentSum == null) {
currentSum = 0;
}
currentSum += input.f1;
sumState.update(currentSum);

return new Tuple2<>(input.f0, currentSum);
}
}

````

private ListState<String> checkpointedState;

@Override
public void snapshotState(FunctionSnapshotContext context) throws Exception {
checkpointedState.clear();
for (String element : bufferedElements) {
checkpointedState.add(element);
}
}

@Override
public void initializeState(FunctionInitializationContext context) throws Exception {
ListStateDescriptor<String> descriptor =
new ListStateDescriptor<>("buffered-elements", String.class);

checkpointedState = context.getOperatorStateStore().getListState(descriptor);

if (context.isRestored()) {
for (String element : checkpointedState.get()) {
bufferedElements.add(element);
}
}
}
}

```

// 2. FsStateBackend (生产推荐)
env.setStateBackend(new FsStateBackend("hdfs://namenode:port/flink-checkpoints"));

// 3. RocksDBStateBackend (大状态)
env.setStateBackend(new RocksDBStateBackend("hdfs://namenode:port/flink-checkpoints"));

// 配置
env.enableCheckpointing(60000); // 60 秒 checkpoint 一次
env.getCheckpointConfig().setCheckpointingMode(CheckpointingMode.EXACTLY_ONCE);
env.getCheckpointConfig().setMinPauseBetweenCheckpoints(30000);
env.getCheckpointConfig().setCheckpointTimeout(600000);

```

// 1. Processing Time (处理时间)
env.setStreamTimeCharacteristic(TimeCharacteristic.ProcessingTime);

// 2. Event Time (事件时间)
env.setStreamTimeCharacteristic(TimeCharacteristic.EventTime);

// 3. Watermark (水位线)
stream.assignTimestampsAndWatermarks(
WatermarkStrategy.<Event>forBoundedOutOfOrderness(Duration.ofSeconds(10))
.withTimestampAssigner((event, timestamp) -> event.getTimestamp()));

```
stream.keyBy(...)
.window(TumblingEventTimeWindows.of(Time.minutes(5)))
.sum(1);

// 滑动窗口 (Sliding Window)
stream.keyBy(...)
.window(SlidingEventTimeWindows.of(Time.minutes(10), Time.minutes(2)))
.sum(1);

// 会话窗口 (Session Window)
stream.keyBy(...)
.window(EventTimeSessionWindows.withGap(Time.minutes(30)))
.sum(1);

```

.countWindow(100)
.sum(1);

// 滑动计数窗口
stream.keyBy(...)
.countWindow(100, 10)
.sum(1);

```
.window(TumblingEventTimeWindows.of(Time.minutes(5)))
.reduce(new SumReduceFunction());

// 2. AggregateFunction
stream.keyBy(...)
.window(TumblingEventTimeWindows.of(Time.minutes(5)))
.aggregate(new AverageAggregateFunction());

// 3. ProcessWindowFunction
stream.keyBy(...)
.window(TumblingEventTimeWindows.of(Time.minutes(5)))
.process(new MyProcessWindowFunction());

public class MyProcessWindowFunction extends ProcessWindowFunction<Tuple2<String, Integer>, String, String, TimeWindow> {
@Override
public void process(String key, Context context, Iterable<Tuple2<String, Integer>> elements, Collector<String> out) {
int count = 0;
for (Tuple2<String, Integer> element : elements) {
count++;
}
out.collect("Window: " + context.window() + " count: " + count);
}
}

```

// EnabledCheckpoint
env.enableCheckpointing(60000, CheckpointingMode.EXACTLY_ONCE);

// ConfigCheckpoint
CheckpointConfig config = env.getCheckpointConfig();
config.setMinPauseBetweenCheckpoints(30000);
config.setCheckpointTimeout(600000);
config.setMaxConcurrentCheckpoints(1);
config.enableExternalizedCheckpoints(ExternalizedCheckpointCleanup.RETAIN_ON_CANCELLATION);

// 重启 Strategy
env.setRestartStrategy(RestartStrategies.fixedDelayRestart(
3, // 重启次数
Time.of(10, TimeUnit.SECONDS) // 重启间隔
));

env.setRestartStrategy(RestartStrategies.exponentialDelayRestart(
Time.milliseconds(1),
Time.milliseconds(1000),

1. 2, // 指数基数
   Time.milliseconds(5000), // 最大 Latency
2. 1 // 抖动因子
   ));

```

# 从 Savepoint 恢复
bin/flink run -s <savepointPath> <jarFile>

# DeleteSavepoint
bin/flink savepoint -d <savepointPath>

```

// 1. 全局并行度
env.setParallelism(4);

// 2. 算子并行度
stream.map(...).setParallelism(2);

// 3. Slot 共享组
stream.map(...).slotSharingGroup("group1");

```
taskmanager.memory.flink.size: 3g
taskmanager.memory.network.fraction: 0.1
taskmanager.memory.managed.fraction: 0.4

```

// 批量传输
env.setBufferTimeout(100);

```
backend.setPredefinedOptions(PredefinedOptions.SPINNING_DISK_OPTIMIZED);
backend.setDbStoragePath("/tmp/rocksdb");
env.setStateBackend(backend);

```

|:---|:---|:---|
| **处理模型** | 真正的流处理 | 微批处理 |
| **延迟** | 毫秒级 | 秒级 |
| **吞吐量** | 高 | 很高 |
| **状态管理** | 原生支持 | 有限支持 |
| **容错** | Checkpoint | RDD lineage |
| **反压** | 原生支持 | 有限支持 |

## # 2. 反压 (Backpressure) 机制

- **问题\*\***: 下游处理速度跟不上上游产生速度

- **Flink 解决方案\*\***:

1. **信用机制**: 基于信用的流量控制
2. **缓冲池**: 动态调整缓冲池大小
3. **网络栈**: TCP 流量控制
4. **监控**: Web UI 显示反压情况

## # 3. Exactly-Once 语义保证

- **组件\*\***:

1. **Source**: 可重放（如 Kafka offset）
2. **内部处理**: Checkpoint 机制
3. **Sink**: 两阶段提交或幂等写入

```java
// 两阶段提交 Sink 示例
public class TwoPhaseCommitSink extends TwoPhaseCommitSinkFunction<String, Transaction, Void> {
@Override
protected Transaction beginTransaction() throws Exception {
return new Transaction();
}

@Override
protected void invoke(Transaction transaction, String value, Context context) throws Exception {
transaction.add(value);
}

@Override
protected void preCommit(Transaction transaction) throws Exception {
transaction.flush();
}

@Override
protected void commit(Transaction transaction) {
transaction.commit();
}

@Override
protected void abort(Transaction transaction) {
transaction.rollback();
}
}

```

1. **Watermark**: 事件时间窗口
2. **Processing Time**: 处理时间窗口
3. **元素计数**: 计数窗口
4. **自定义**: 用户定义的触发器

## # 5. 状态管理最佳实践

1. **选择合适的状态类型**: ValueState vs ListState vs MapState
2. **设置状态 TTL**: 避免状态无限增长
3. **选择合适的状态后端**: 内存 vs 文件系统 vs RocksDB
4. **状态大小监控**: 及时发现状态膨胀

````java
// SetStatusTTL
StateTtlConfig ttlConfig = StateTtlConfig
.newBuilder(Time.days(7))
.setUpdateType(StateTtlConfig.UpdateType.OnCreateAndWrite)
.setStateVisibility(StateTtlConfig.StateVisibility.NeverReturnExpired)
.build();

ValueStateDescriptor<String> descriptor = new ValueStateDescriptor<>("my-state", String.class);
descriptor.enableTimeToLive(ttlConfig);


1. **检测故障**: JobManager监控TaskManager心跳
2. **重启任务**: 根据重启策略重启失败任务
3. **恢复状态**: 从最近的 Checkpoint 恢复状态
4. **重放数据**: Source 重放 Checkpoint 之后的数据
5. **继续处理**: 恢复正常处理流程
    ```



<!-- 04-Reference/Engineering/Data-Analysis/hbase.md -->

# HBase 分布式NoSQL数据库

Apache HBase 是一个分布式、面向列的开源数据库，基于 Google Bigtable 论文实现，运行在 HDFS 之上。
___
## 目录
1. [**HBase 架构**](#hbase-架构)
2. [**数据模型**](#数据模型)
3. [**Shell 操作**](#shell-操作)
4. [**Java API**](#java-api)
5. [**性能优化**](#性能优化)
6. [**集群管理**](#集群管理)
7. [**知识要点**](#知识要点)
___
## HBase 架构

## # 核心组件

````

RegionServer1 RegionServer2 RegionServer3
↓ ↓ ↓
Region1,2 Region3,4 Region5,6
↓ ↓ ↓
HDFS DataNode HDFS DataNode HDFS DataNode

```
| **Region** | 表的水平分片，包含一定范围的行 |
| **ZooKeeper** | 协调服务，存储元数据，故障检测 |
| **HDFS** | 底层存储系统 |

## # Region 详细结构

```

│ ├── Index Block
│ └── Bloom Filter
└── WAL (Write-Ahead Log)

```
3. **MemStore**: 数据写入内存
4. **Flush**: MemStore达到阈值时刷写到HFile
5. **Compaction**: 定期合并HFile


### 读取流程
1. **Client** → **RegionServer**: 读请求
2. **MemStore**: 先查内存中的数据
3. **BlockCache**: 查询缓存的HFile块
4. **HFile**: 从磁盘读取数据
5. **Merge**: 合并多个来源的数据返回
___
## 数据模型

## # 逻辑视图

```

│ │ └── age:25 (timestamp:1234567891)
│ └── Column Family: contact_info
│ ├── email:zhang@example.com (timestamp:1234567892)
│ └── phone:13800138000 (timestamp:1234567893)
└── Row Key: user002
└── ...

```
user002:name:1234567900 → li_si

contact_info Store:
user001:email:1234567892 → zhang@example.com
user001:phone:1234567893 → 13800138000

```

| **Column Family** | 列族，列的逻辑分组 |
| **Column Qualifier** | 列限定符，列族下的具体列 |
| **Cell** | 单元格，由(row, column family, column qualifier, timestamp)确定 |
| **Timestamp** | 时间戳，同一 Cell 的多个版本 |

---

## Shell 操作

## # 连接与基本操作

```bash
# StartHBase Shell
hbase shell

# ViewStatus
status
version

# ViewClusterInformation
whoami

```

# ListNamespace

list_namespace

# DeleteNamespace

drop_namespace 'my_namespace'

```

# Createtable（带Config）
create 'user_info',
{NAME => 'basic_info', VERSIONS => 3, TTL => 2592000},
{NAME => 'contact_info', COMPRESSION => 'SNAPPY'}

# Listtable
list

# View table结构
describe 'user_info'

# 禁用table
disable 'user_info'

# Enabledtable
enable 'user_info'

# Deletetable
drop 'user_info'

# 修改表结构
alter 'user_info', {NAME => 'basic_info', VERSIONS => 5}

```

put 'user_info', 'user001', 'basic_info:age', '25'
put 'user_info', 'user001', 'contact_info:email', 'zhang@example.com'

# 查询单行

get 'user_info', 'user001'

# 查询指定列族

get 'user_info', 'user001', 'basic_info'

# 查询指定列

get 'user_info', 'user001', 'basic_info:name'

# 扫描表

scan 'user_info'

# 条件扫描

scan 'user_info', {STARTROW => 'user001', ENDROW => 'user999'}
scan 'user_info', {FILTER => "SingleColumnValueFilter('basic_info', 'age', >=, 'binary:18')"}

# 删除数据

delete 'user_info', 'user001', 'basic_info:age'

# 删除行

deleteall 'user_info', 'user001'

# 计数

count 'user_info'

```
// ConfigConnect
Configuration conf = HBaseConfiguration.create();
conf.set("hbase.zookeeper.quorum", "node1,node2,node3");
conf.set("hbase.zookeeper.property.clientPort", "2181");

// CreateConnect
Connection connection = ConnectionFactory.createConnection(conf);
Admin admin = connection.getAdmin();

```

HTableDescriptor tableDesc = new HTableDescriptor(tableName);

// Add 列族
HColumnDescriptor basicInfo = new HColumnDescriptor("basic*info");
basicInfo.setMaxVersions(3);
basicInfo.setTimeToLive(30 * 24 \_ 60 \*\* 60); // 30 天 TTL

HColumnDescriptor contactInfo = new HColumnDescriptor("contact_info");
contactInfo.setCompressionType(Compression.Algorithm.SNAPPY);

tableDesc.addFamily(basicInfo);
tableDesc.addFamily(contactInfo);

// Createtable
admin.createTable(tableDesc);

```
Put put = new Put(Bytes.toBytes("user001"));
put.addColumn(Bytes.toBytes("basic_info"), Bytes.toBytes("name"), Bytes.toBytes("zhang_san"));
put.addColumn(Bytes.toBytes("basic_info"), Bytes.toBytes("age"), Bytes.toBytes("25"));
table.put(put);

// 批量插入
List<Put> puts = new ArrayList<>();
for (int i = 0; i < 1000; i++) {
Put batchPut = new Put(Bytes.toBytes("user" + String.format("%03d", i)));
batchPut.addColumn(Bytes.toBytes("basic_info"), Bytes.toBytes("name"), Bytes.toBytes("user" + i));
puts.add(batchPut);
}
table.put(puts);

// 查询数据
Get get = new Get(Bytes.toBytes("user001"));
get.addFamily(Bytes.toBytes("basic_info"));
Result result = table.get(get);

// 解析结果
for (Cell cell : result.listCells()) {
String family = Bytes.toString(CellUtil.cloneFamily(cell));
String qualifier = Bytes.toString(CellUtil.cloneQualifier(cell));
String value = Bytes.toString(CellUtil.cloneValue(cell));
System.out.println(family + ":" + qualifier + " = " + value);
}

// 扫描数据
Scan scan = new Scan();
scan.setStartRow(Bytes.toBytes("user001"));
scan.setStopRow(Bytes.toBytes("user999"));
scan.addFamily(Bytes.toBytes("basic_info"));

ResultScanner scanner = table.getScanner(scan);
for (Result res : scanner) {
// ProcessResult
}
scanner.close();

```

Bytes.toBytes("basic_info"),
Bytes.toBytes("age"),
CompareFilter.CompareOp.GREATER_OR_EQUAL,
Bytes.toBytes("18")
);

// 前缀过滤器
PrefixFilter prefixFilter = new PrefixFilter(Bytes.toBytes("user00"));

// 组合过滤器
FilterList filterList = new FilterList(FilterList.Operator.MUST_PASS_ALL);
filterList.addFilter(filter);
filterList.addFilter(prefixFilter);

scan.setFilter(filterList);

```
// 1. 避免热点：使用散列前缀
String rowKey = MD5Hash.digest(userId).toString().substring(0, 2) + "_" + userId;

// 2. 时间倒序：便于查询最新数据
String rowKey = userId + "_" + (Long.MAX_VALUE - timestamp);

// 3. 组合Key：Support多维Query
String rowKey = region + "_" + userId + "_" + timestamp;

```

{NAME => 'profile', COMPRESSION => 'SNAPPY'}, // 用户 Basic information
{NAME => 'behavior', TTL => 604800} // 用户行为 Data(7 天 TTL)

// 避免：列族过多
// 避免：不同访问模式列放 in/at 同一列族

```
for (UserData user : userData) {
Put put = createPut(user);
puts.add(put);

// 批量提交
if (puts.size() >= 1000) {
table.put(puts);
puts.clear();
}
}
// 提交剩余数据
if (!puts.isEmpty()) {
table.put(puts);
}

```

family.setBlockCacheEnabled(true);
family.setCacheBloomsOnWrite(true);
family.setCacheDataOnWrite(true);
family.setCacheIndexesOnWrite(true);

```
# 手动分裂 Region
split 'user_info', 'user500'

# 合并 Region
merge_region 'region1_encoded_name', 'region2_encoded_name'

# ViewRegionInformation
list_regions 'user_info'

```

balancer

# 查看负载均衡状态

balancer_enabled

```

# 手动触发 Minor Compaction
compact 'user_info'

# ViewCompressStatus
compaction_state 'user_info'

```

# ViewRegionServerInformation

list_regionservers

# View tableStatisticsInformation

list_table_stats 'user_info'

````
|:---|:---|:---|
| **数据模型** | 列族模型 | 关系模型 |
| **ACID** | 行级原子性 | 完整ACID |
| **扩展性** | 水平扩展 | 垂直扩展 |
| **查询语言** | NoSQL API | SQL |
| **适用场景** | 大数据读写 | 复杂事务 |

## # 2. 数据倾斜问题

* *问题**: Region 热点，某些Region访问量过大

* *解决方案**:
1. **Row Key设计**: 避免单调递增，使用散列前缀
2. **预分区**: 创建表时预先分区
3. **负载均衡**: 定期执行balance操作

```java
// 预PartitionExample
byte[][] splits = new byte[10][];
for (int i = 0; i < 10; i++) {
splits[i] = Bytes.toBytes(String.format("%02d", i));
}
admin.createTable(tableDesc, splits);

````

2. **Block Cache**: 缓存热点数据
3. **压缩**: 减少存储空间和 IO
4. **预读**: 设置合理的扫描缓存

```java
// ConfigBloom Filter
HColumnDescriptor family = new HColumnDescriptor("data");
family.setBloomFilterType(BloomType.ROW);

```

2. **WAL**: 根据需要关闭 WAL
3. **MemStore**: 调整内存大小
4. **压缩**: 异步压缩

```java
// 关闭WAL（DataSecurity性降低）
put.setDurability(Durability.SKIP_WAL);

```

2. **Region 迁移**: 自动迁移故障节点的 Region
3. **ZooKeeper**: 监控集群状态，协调故障恢复
4. **数据副本**: 依赖 HDFS 的数据副本机制

## # 6. 热点问题诊断

```bash
# 1. ViewRegion分布
list_regions 'table_name'

# 2. ViewRegionServer负载
status 'detailed'

# 3. Analysis访问模式

# 通过日志分析热点 Row Key

# 4. Re-设计Row Key

# 添加散列前缀或使用反向时间戳

```

<!-- 04-Reference/Engineering/Data-Analysis/hive.md -->

# Hive 数据仓库

Apache Hive 是基于 Hadoop 的数据仓库工具，可以将结构化的数据文件映射为数据库表，并提供类 SQL 查询功能。

---

## 目录

1. [**Hive 架构**](#hive-架构)
2. [**数据类型与存储格式**](#数据类型与存储格式)
3. [**DDL 操作**](#ddl-操作)
4. [**DML 操作**](#dml-操作)
5. [**分区与分桶**](#分区与分桶)
6. [**函数与 UDF**](#函数与udf)
7. [**性能优化**](#性能优化)
8. [**知识要点**](#知识要点)

---

## Hive 架构

## # 核心组件

```
Metastore (Metadata storage)
↓
HDFS (Data storage) + MapReduce/Tez/Spark (Compute engine)

```

| **Driver** | 解析 SQL、生成执行计划、协调执行 |
| **Execution Engine** | 执行引擎（MapReduce/Tez/Spark） |

## # 工作流程

1. **SQL 解析**: 词法分析 → 语法分析 → 语义分析
2. **逻辑计划**: 生成逻辑执行计划
3. **物理计划**: 转换为 MapReduce/Tez/Spark 任务
4. **执行**: 提交到 Hadoop 集群执行

---

## 数据类型与存储格式

## # 基本数据类型

| 类型        | 描述         | 示例                                                    |
| :---------- | :----------- | :------------------------------------------------------ |
| `TINYINT`   | 1 字节整数   | -128 到 127                                             |
| `SMALLINT`  | 2 字节整数   | -32,768 到 32,767                                       |
| `INT`       | 4 字节整数   | -2,147,483,648 到 2,147,483,647                         |
| `BIGINT`    | 8 字节整数   | -9,223,372,036,854,775,808 到 9,223,372,036,854,775,807 |
| `FLOAT`     | 4 字节浮点数 | 3.14159                                                 |
| `DOUBLE`    | 8 字节浮点数 | 3.141592653589793                                       |
| `STRING`    | 字符串       | 'Hello World'                                           |
| `BOOLEAN`   | 布尔值       | TRUE/FALSE                                              |
| `TIMESTAMP` | 时间戳       | '2023-01-01 12:00:00'                                   |
| `DATE`      | 日期         | '2023-01-01'                                            |

## # 复杂数据类型

```sql
- - Array
ARRAY<data_type>
- - 示例：ARRAY<STRING>

- - Map
MAP<primitive_type, data_type>
- - 示例：MAP<STRING, INT>

- - 结构体
STRUCT<col_name:data_type [COMMENT col_comment], ...>
- - 示例：STRUCT<name:STRING, age:INT>

- - 联合体
UNIONTYPE<data_type, data_type, ...>

```

| **SequenceFile** | 中 | 中 | 中 | 中间数据 |
| **RCFile** | 高 | 中 | 低 | 列式分析 |
| **ORC** | 很高 | 很高 | 低 | OLAP 分析 |
| **Parquet** | 很高 | 很高 | 低 | 跨平台分析 |

---

## DDL 操作

## # 数据库操作

```sql
- - 创建数据库
CREATE DATABASE IF NOT EXISTS mydb
COMMENT 'My database'
LOCATION '/user/hive/warehouse/mydb.db';

- - 使用数据库
USE mydb;

- - 显示数据库
SHOW DATABASES;

- - 删除数据库
DROP DATABASE IF EXISTS mydb CASCADE;

```

id INT,
name STRING,
salary DOUBLE,
department STRING
)
STORED AS ORC
TBLPROPERTIES ('orc.compress'='SNAPPY');

```
name STRING,
salary DOUBLE,
department STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/data/employee/';

```

name STRING,
salary DOUBLE
)
PARTITIONED BY (department STRING, year INT)
STORED AS ORC;

```

- - 修改列
ALTER TABLE employee CHANGE salary salary DECIMAL(10,2);

- - 添加分区
ALTER TABLE partitioned_employee ADD PARTITION (department='IT', year=2023);

- - 删除分区
ALTER TABLE partitioned_employee DROP PARTITION (department='IT', year=2023);

- - 重命名表
ALTER TABLE employee RENAME TO emp;

```

- - 插入数据
    INSERT INTO employee VALUES (1, 'John', 5000.0, 'IT');

- - 从查询插入
    INSERT INTO employee
    SELECT id, name, salary, department
    FROM temp_employee;

- - 覆盖插入
    INSERT OVERWRITE TABLE employee
    SELECT \*\* FROM temp_employee;

- - 分区插入
    INSERT INTO partitioned_employee PARTITION(department='IT', year=2023)
    SELECT id, name, salary FROM temp_employee;

- - 动态分区插入
    SET hive.exec.dynamic.partition=true;
    SET hive.exec.dynamic.partition.mode=nonstrict;

INSERT INTO partitioned_employee PARTITION(department, year)
SELECT id, name, salary, department, year FROM temp_employee;

```

- - 聚合查询
SELECT department, AVG(salary) as avg_salary
FROM employee
GROUP BY department
HAVING AVG(salary) > 6000;

- - 连接查询
SELECT e.name, d.dept_name
FROM employee e
JOIN department d ON e.department = d.dept_id;

- - 窗口函数
SELECT name, salary,
ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) as rank
FROM employee;

```

```sql
- - 静态分区
INSERT INTO partitioned_employee PARTITION(department='IT', year=2023)
SELECT id, name, salary FROM source_table;

- - 动态分区
INSERT INTO partitioned_employee PARTITION(department, year)
SELECT id, name, salary, department, year FROM source_table;

- - 查询特定分区
SELECT * FROM partitioned_employee
WHERE department='IT' AND year=2023;

```

CREATE TABLE bucketed_employee (
id INT,
name STRING,
salary DOUBLE,
department STRING
)
CLUSTERED BY (id) INTO 4 BUCKETS
STORED AS ORC;

- - 启用分桶
    SET hive.enforce.bucketing=true;

- - 插入数据（自动分桶）
    INSERT INTO bucketed_employee
    SELECT \*\* FROM employee;

````

```sql
- - 字符串操作
SELECT
CONCAT(first_name, ' ', last_name) as full_name,
UPPER(name) as upper_name,
LENGTH(name) as name_length,
SUBSTR(name, 1, 3) as name_prefix
FROM employee;

````

FROM_UNIXTIME(UNIX_TIMESTAMP()) as current_time,
YEAR(hire_date) as hire_year,
DATEDIFF(CURRENT_DATE, hire_date) as days_since_hire
FROM employee;

```
COUNT(*) as total_count,
SUM(salary) as total_salary,
AVG(salary) as avg_salary,
MAX(salary) as max_salary,
MIN(salary) as min_salary,
STDDEV(salary) as salary_stddev
FROM employee;

```

public String evaluate(String input) {
if (input == null) return null;
return input.toUpperCase();
}
}

```

- - 使用 UDF
SELECT my_upper(name) FROM employee;

```

- - 选择合适的存储格式
    CREATE TABLE optimized_table (
    col1 STRING,
    col2 INT
    )
    STORED AS ORC
    TBLPROPERTIES (
    'orc.compress'='SNAPPY',
    'orc.create.index'='true'
    );

```
SELECT * FROM partitioned_table
WHERE partition_col = 'value';

- - 避免：全表扫描
SELECT * FROM partitioned_table
WHERE non_partition_col = 'value';

```

- - 避免：SELECT _
    SELECT _ FROM employee;

```
FROM employee e
JOIN department d ON e.dept_id = d.id
WHERE e.salary > 5000;

```

- - 启用代价优化器
    SET hive.cbo.enable=true;

- - 设置合理的 MapReduce 参数
    SET mapreduce.job.reduces=10;
    SET hive.exec.reducers.bytes.per.reducer=1000000000;

- - 启用并行执行
    SET hive.exec.parallel=true;
    SET hive.exec.parallel.thread.number=8;

````
|:---|:---|:---|
| **数据量** | PB级 | GB-TB级 |
| **延迟** | 高（秒-分钟） | 低（毫秒） |
| **ACID** | 有限支持 | 完全支持 |
| **索引** | 有限 | 丰富 |
| **扩展性** | 水平扩展 | 垂直扩展 |
| **适用场景** | 离线分析 | 在线事务 |

## # 2. 内部表 vs 外部表

| 特性 | 内部表 | 外部表 |
|:---|:---|:---|
| **数据管理** | Hive管理 | 用户管理 |
| **删除表** | 删除元数据和数据 | 只删除元数据 |
| **数据位置** | Hive仓库目录 | 用户指定位置 |
| **使用场景** | 临时数据、中间结果 | 共享数据、外部数据源 |

## # 3. 数据倾斜解决方案

```sql
- - 1. 增加 Reduce 任务数
SET mapreduce.job.reduces=100;

- - 2. 启用负载均衡
SET hive.groupby.skewindata=true;

- - 3. 使用随机前缀
SELECT /*+ MAPJOIN(b) */ *
FROM (
SELECT CONCAT(CAST(RAND() * 100 AS INT), '_', key) as new_key, value
FROM skewed_table
) a
JOIN small_table b ON a.key = b.key;

````

- - 1. 合并小文件
       SET hive.merge.mapfiles=true;
       SET hive.merge.mapredfiles=true;
       SET hive.merge.size.per.task=256000000;

- - 2. 使用 Concatenate
       ALTER TABLE table_name CONCATENATE;

- - 3. 重新组织数据
       INSERT OVERWRITE TABLE new_table
       SELECT \*\* FROM old_table;

```
4. **分桶**: 对大表使用分桶
5. **索引**: 创建适当的索引
6. **缓存**: 缓存热点数据
7. **并行度**: 调整Map/Reduce任务数
8. **资源**: 合理分配内存和CPU
```

<!-- 04-Reference/Engineering/Data-Analysis/spark.md -->

# Apache Spark 大数据处理

Apache Spark 是一个统一的大数据处理引擎，支持批处理、流处理、机器学习和图计算。

---

## 目录

1. [**Spark 架构**](#spark-架构)
2. [**RDD 编程**](#rdd-编程)
3. [**DataFrame & Dataset**](#dataframe--dataset)
4. [**Spark SQL**](#spark-sql)
5. [**Spark Streaming**](#spark-streaming)
6. [**性能优化**](#性能优化)
7. [**知识要点**](#知识要点)

---

## Spark 架构

## # 集群架构

```
Cluster Manager (YARN/Mesos/Standalone)
↓
Worker Node1 Worker Node2 Worker Node3
├── Executor1 ├── Executor1 ├── Executor1
│ ├── Task1 │ ├── Task1 │ ├── Task1
│ └── Task2 │ └── Task2 │ └── Task2
└── Cache └── Cache └── Cache

```

| **SparkContext** | Spark 程序入口，协调集群资源 |
| **Cluster Manager** | 集群资源管理器 |
| **Worker Node** | 集群中的工作节点 |
| **Executor** | 运行在 Worker 上的进程，执行 Task |
| **Task** | 最小的工作单元 |

## # 运行流程

1. **Driver 创建 SparkContext**
2. **资源申请**: 向 Cluster Manager 申请资源
3. **任务调度**: DAG Scheduler 将 Job 分解为 Stage 和 Task
4. **任务分发**: Task Scheduler 将 Task 分发到 Executor
5. **任务执行**: Executor 执行 Task 并返回结果

---

## RDD 编程

## # RDD 基本概念

- **RDD (Resilient Distributed Dataset)\*\***: 弹性分布式数据集

### 特性

- **不可变性**: RDD 一旦创建不可修改

- **分区性**: 数据分布在多个分区

- **容错性**: 通过血统(Lineage)恢复丢失数据

- **惰性求值**: 只有在 Action 操作时才会执行

## # RDD 创建

```scala
import org.apache.spark.{SparkConf, SparkContext}

val conf = new SparkConf().setAppName("SparkExample").setMaster("local[*]")
val sc = new SparkContext(conf)

// 1. 从集合创建
val rdd1 = sc.parallelize(List(1, 2, 3, 4, 5))
val rdd2 = sc.makeRDD(Array("a", "b", "c"))

// 2. 从外部存储创建
val rdd3 = sc.textFile("hdfs://path/to/file")
val rdd4 = sc.wholeTextFiles("hdfs://path/to/directory")

// 3. 从其他 RDD 创建
val rdd5 = rdd1.map(_ * 2)

```

val mapped = data.map(\_ \*\* 2)

// 2. filter - Filter
val filtered = data.filter(\_ % 2 == 0)

// 3. flatMap - 一对多转换
val words = sc.parallelize(List("hello world", "spark scala"))
val flatMapped = words.flatMap(\_.split(" "))

// 4. distinct - 去重
val distincted = data.distinct()

// 5. union - 合并
val rdd1 = sc.parallelize(List(1, 2, 3))
val rdd2 = sc.parallelize(List(4, 5, 6))
val unioned = rdd1.union(rdd2)

// 6. intersection - 交集
val intersected = rdd1.intersection(rdd2)

// 7. groupByKey - 按键分组
val pairs = sc.parallelize(List(("a", 1), ("b", 2), ("a", 3)))
val grouped = pairs.groupByKey()

// 8. reduceByKey - 按键聚合
val reduced = pairs.reduceByKey(_ + _)

// 9. sortByKey - 按键排序
val sorted = pairs.sortByKey()

// 10. join - 连接
val rdd3 = sc.parallelize(List(("a", "x"), ("b", "y")))
val joined = pairs.join(rdd3)

```
val collected = data.collect()

// 2. count - 计算元素数
val count = data.count()

// 3. first - 获取第一个元素
val first = data.first()

// 4. take - 获取前 n 个元素
val taken = data.take(3)

// 5. reduce - 聚合所有元素
val sum = data.reduce(_ + _)

// 6. fold - 带初始值的聚合
val folded = data.fold(0)(_ + _)

// 7. aggregate - 复杂聚合
val (sum, count) = data.aggregate((0, 0))(
(acc, value) => (acc._1 + value, acc._2 + 1),
(acc1, acc2) => (acc1._1 + acc2._1, acc1._2 + acc2._2)
)

// 8. foreach - 对每个元素执行操作
data.foreach(println)

// 9. saveAsTextFile - 保存为文本文件
data.saveAsTextFile("hdfs://path/to/output")

```

```scala
import org.apache.spark.sql.{SparkSession, DataFrame}

val spark = SparkSession.builder()
.appName("DataFrameExample")
.master("local[*]")
.getOrCreate()

import spark.implicits._

// 1. 从 RDD 创建 DataFrame
case class Person(name: String, age: Int, city: String)
val peopleRDD = spark.sparkContext.parallelize(List(
Person("Alice", 25, "NYC"),
Person("Bob", 30, "LA"),
Person("Charlie", 35, "Chicago")
))
val peopleDF = peopleRDD.toDF()

// 2. 从文件创建 DataFrame
val df = spark.read
.option("header", "true")
.option("inferSchema", "true")
.csv("path/to/file.csv")

// 3. 从 JSON 创建
val jsonDF = spark.read.json("path/to/file.json")

```

df.show()
df.describe().show()

// 2. 选择列
df.select("name", "age").show()
df.select($"name", $"age" + 1).show()

// 3. 过滤
df.filter($"age" > 25).show()
df.where("age > 25").show()

// 4. 分组聚合
df.groupBy("city").count().show()
df.groupBy("city").agg(avg("age"), max("age")).show()

// 5. 排序
df.orderBy($"age".desc).show()
df.sort("name").show()

// 6. Connect
val df2 = spark.createDataFrame(List(
("NYC", "NY"),
("LA", "CA"),
("Chicago", "IL")
)).toDF("city", "state")

df.join(df2, "city").show()

// 7. 窗口 Function
import org.apache.spark.sql.expressions.Window
import org.apache.spark.sql.functions.\_

val windowSpec = Window.partitionBy("city").orderBy($"age".desc)
df.withColumn("rank", row_number().over(windowSpec)).show()

```

val ds: Dataset[Person] = df.as[Person]

// 类型安全操作
val adults = ds.filter(_.age >= 18)
val names = ds.map(_.name)

// 编译时类型检查
// ds.filter(_.salary > 1000) // 编译错误，Person 没有 salary 字段

```

// 注册临时视图
df.createOrReplaceTempView("people")

// SQL 查询
val result = spark.sql("""
SELECT city, COUNT(\*\*) as count, AVG(age) as avg_age
FROM people
WHERE age > 20
GROUP BY city
ORDER BY count DESC
""")

result.show()

// 复杂查询
val complexQuery = spark.sql("""
SELECT name, age, city,
ROW_NUMBER() OVER (PARTITION BY city ORDER BY age DESC) as rank
FROM people
""")

```
spark.catalog.listTables().show()

// 缓存表
spark.catalog.cacheTable("people")
spark.catalog.uncacheTable("people")

// 删除临时视图
spark.catalog.dropTempView("people")

```

import org.apache.spark.streaming.{StreamingContext, Seconds}

val ssc = new StreamingContext(spark.sparkContext, Seconds(1))

// 1. 从 socket 创建流
val lines = ssc.socketTextStream("localhost", 9999)

// 2. 转换操作
val words = lines.flatMap(_.split(" "))
val pairs = words.map(word => (word, 1))
val wordCounts = pairs.reduceByKey(_ + \_)

// 3. 输出操作
wordCounts.print()

// 启动流处理
ssc.start()
ssc.awaitTermination()

```
(a: Int, b: Int) => a + b, // reduce 函数
(a: Int, b: Int) => a - b, // inverse reduce 函数
Seconds(30), // 窗口长度
Seconds(10) // 滑动间隔
)

// 状态更新
def updateFunction(newValues: Seq[Int], runningCount: Option[Int]): Option[Int] = {
val newCount = newValues.sum + runningCount.getOrElse(0)
Some(newCount)
}

val stateDstream = pairs.updateStateByKey[Int](updateFunction)

```

val df = spark
.readStream
.format("socket")
.option("host", "localhost")
.option("port", 9999)
.load()

// 处理流数据
val words = df.as[String].flatMap(\_.split(" "))
val wordCounts = words.groupBy("value").count()

// 输出结果
val query = wordCounts.writeStream
.outputMode("complete")
.format("console")
.trigger(Trigger.ProcessingTime("10 seconds"))
.start()

query.awaitTermination()

```
import org.apache.spark.storage.StorageLevel

// 1. 基本Cache
val cachedRDD = rdd.cache() // MEMORY_ONLY
val persistedRDD = rdd.persist(StorageLevel.MEMORY_AND_DISK)

// 2. DataFrame 缓存
df.cache()
df.persist(StorageLevel.MEMORY_AND_DISK_SER)

// 3. 不同存储级别
StorageLevel.MEMORY_ONLY // 仅内存
StorageLevel.MEMORY_AND_DISK // 内存+磁盘
StorageLevel.MEMORY_ONLY_SER // 内存序列化
StorageLevel.DISK_ONLY // 仅磁盘
StorageLevel.MEMORY_AND_DISK_2 // 内存+磁盘，2副本

```

val coalesced = rdd.coalesce(2) // 减少分区

// 2. 自定义分区器
class CustomPartitioner(numPartitions: Int) extends Partitioner {
override def numPartitions: Int = numPartitions

override def getPartition(key: Any): Int = {
key.hashCode() % numPartitions
}
}

val partitioned = pairs.partitionBy(new CustomPartitioner(4))

// 3. 数据本地性
val localData = sc.textFile("hdfs://path", minPartitions = 4)

```
val result = rdd.map(x => x * broadcastVar.value.sum)

// 2. 累加器
val accum = sc.longAccumulator("My Accumulator")
rdd.foreach(x => accum.add(x))
println(s"Accumulator value: ${accum.value}")

// 3. 自定义累加器
class VectorAccumulator extends AccumulatorV2[Vector, Vector] {
private var _sum = Vector.zeros(3)

override def isZero: Boolean = _sum == Vector.zeros(3)
override def copy(): VectorAccumulator = new VectorAccumulator
override def reset(): Unit = _sum = Vector.zeros(3)
override def add(v: Vector): Unit = _sum += v
override def merge(other: AccumulatorV2[Vector, Vector]): Unit = {
_sum += other.asInstanceOf[VectorAccumulator]._sum
}
override def value: Vector = _sum
}

```

// 2. 启用代码生成
spark.conf.set("spark.sql.codegen.wholeStage", "true")

// 3. 广播 Join 优化
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")

// 4. 谓词下推
val optimizedDF = df.filter($"age" > 18) // Filter 下推到数据源

```
|:---|:---|:---|:---|
| **类型安全** | 编译时 | 运行时 | 编译时 |
| **性能优化** | 无 | Catalyst优化器 | Catalyst优化器 |
| **API风格** | 函数式 | 关系型 | 类型安全的关系型 |
| **内存使用** | Java对象 | 二进制格式 | 二进制格式 |
| **序列化** | Java序列化 | 自定义编码器 | 自定义编码器 |

## # 2. Spark内存管理

### 内存分配

```

│ └── 执行内存 (Execution) × 0.5
└── 用户内存 (剩余部分)

```
- -executor-memory 4g

# 2. 内存分配比例
- -conf spark.sql.execution.memory.fraction=0.6
- -conf spark.sql.execution.memory.storageFraction=0.5

# 3. 序列化
- -conf spark.serializer=org.apache.spark.serializer.KryoSerializer

```

### Shuffle 优化

```scala
// 1. 预分区
val partitioned = rdd.partitionBy(new HashPartitioner(100))

// 2. 调整并行度
spark.conf.set("spark.sql.shuffle.partitions", "400")

// 3. 启用外部排序
spark.conf.set("spark.sql.execution.useObjectHashAggregateExec", "false")

```

val skewedRDD = sc.parallelize(List(("key1", 1), ("key1", 1), /_很多 key1_/, ("key2", 1)))

// 加盐处理
val saltedRDD = skewedRDD.map { case (key, value) =>
val salt = Random.nextInt(10)
(s"${key}_$salt", value)
}

val result = saltedRDD.reduceByKey(_ + _)
.map { case (saltedKey, value) =>
val originalKey = saltedKey.split("_")(0)
(originalKey, value)
}
.reduceByKey(_ + \_)

```
iter.toList.groupBy(_._1).map { case (key, values) =>
(key, values.map(_._2).sum)
}.toIterator
}

// 第二阶段：全局聚合
val globalAgg = localAgg.reduceByKey(_ + _)

```

- -num-executors 10 --executor-cores 5 --executor-memory 2g

# 内存密集型

- -num-executors 5 --executor-cores 2 --executor-memory 8g

# 平衡型

- -num-executors 15 --executor-cores 3 --executor-memory 4g

```

// 避免
rdd.map(...).filter(...) // 先转换再过滤

// 减少Shuffle
val broadcastVar = sc.broadcast(smallData)
largeRDD.map(x => x + broadcastVar.value) // 使用广播变量代替 join

```

.mode("overwrite")
.option("compression", "snappy")
.parquet("path/to/output") // Parquet 格式

// 分区存储
df.write
.partitionBy("year", "month")
.parquet("path/to/partitioned/output")

```

```

<!-- 04-Reference/Foundations/android_components.md -->

---

# android 四大组件

Android 的应用框架核心由四个基本组件构成。每个组件都是一个独立的实体，系统和应用可以通过它进入你的 App。理解这四个组件的职责和生命周期是进行任何 Android 开发或逆向分析的基础。

---

## 1. 活动 (Activity)

- **概念**: Activity 是用户界面的单一屏幕。它为用户提供了一个可以进行交互的操作界面。一个 App 通常由多个相互关联的 Activity 组成。

- **核心职责**:

  - **UI 承载**: 负责绘制用户界面、承载 `View` 和 `ViewGroup`。
  - **用户交互**: 响应用户的点击、滑动、输入等事件。
  - **生命周期管理**: 管理从创建到销毁的整个生命周期，以响应系统状态的变化（如来电、屏幕旋转）。

- **生命周期**:

  一个 Activity 具有清晰的生命周期回调方法，这对于逆向分析至关重要，因为核心逻辑（如数据加载、UI 更新）常常在这些方法中被触发。

  - `onCreate()`: **Activity 被创建**。这是最重要的回调，通常在这里进行布局加载 (`setContentView`)、数据初始化、事件绑定等。
  - `onStart()`: Activity 变得可见，但还不能与用户交互。
  - `onResume()`: **Activity 到达前台**，可以与用户进行交互。这是 Hook UI 相关逻辑的绝佳位置。
  - `onPause()`: Activity 即将进入后台，不再是焦点。通常在这里保存未提交的数据。
  - `onStop()`: Activity 完全不可见。
  - `onDestroy()`: Activity 即将被销毁。
  - `onRestart()`: Activity 从停止状态重新启动。

- **逆向切入点**:
  - Hook `onCreate()` 或 `onResume()` 是分析一个新页面的标准起点。
  - 通过 `adb shell dumpsys activity top` 可以查看当前位于前台的 Activity 的类名，这是快速定位目标页面的关键命令。

---

## 2. 服务 (Service)

- **概念**: Service 是一个在后台执行长时间运行操作而没有用户界面的组件。即使用户切换到其他应用，服务仍然可以继续工作。

- **核心职责**:

  - **后台任务**: 执行不需要 UI 的任务，如播放音乐、下载文件、同步数据。
  - **进程间通信 (IPC)**: 可以作为服务端，为其他 App 提供功能。

- **类型**:

  - **启动服务 (Started Service)**: 通过 `startService()` 启动，一旦启动，服务就可以无限期地在后台运行，直到它自己停止或被系统销毁。
  - **绑定服务 (Bound Service)**: 通过 `bindService()` 启动。它提供了一个客户端-服务器接口，允许组件（如 Activity）与服务进行交互、发送请求、获取结果。当所有绑定的组件都解绑后，服务就会被销毁。
  - **前台服务 (Foreground Service)**: 为了防止被系统轻易杀死，Service 可以通过 `startForeground()` 将自己提升为前台服务，此时必须在状态栏显示一个持续的通知（例如音乐播放通知）。

- **逆向切入点**:
  - 很多 App 的核心业务逻辑（如消息推送、位置上报、数据同步）都放在 Service 中。
  - Hook Service 的 `onStartCommand()` 或 `onBind()` 方法可以帮助理解其后台行为。

---

## 3. 广播接收器 (Broadcast Receiver)

- **概念**: 广播接收器是一个用于响应系统范围广播通知的组件。许多广播源自系统（例如，屏幕关闭、网络状态改变、电池电量低），但应用也可以发起自定义广播。

- **核心职责**:

  - **监听系统事件**: 让 App 能够对设备状态的变化做出反应。
  - **应用间通信**: 一个 App 可以向其他 App 发送广播，实现简单的消息通知。

- **类型**:

  - **静态注册**: 在 `AndroidManifest.xml` 中使用 `<receiver>` 标签声明。即使 App 没有运行，当广播事件发生时，系统也会唤醒 App 来处理它。
  - **动态注册**: 在代码中通过 `Context.registerReceiver()` 注册。它的生命周期与注册它的组件（如 Activity）相关联。

- **逆向切入点**:
  - 分析 `AndroidManifest.xml` 中的静态广播接收器，可以了解 App 关心哪些系统事件。
  - Hook `onReceive()` 方法是捕获和分析广播内容（Intent）的关键。

---

## 4. 内容提供器 (Content Provider)

- **概念**: 内容提供器用于管理一组共享的应用数据。它以一种标准化的接口，将数据暴露给其他应用。数据可以存储在文件系统、SQLite 数据库或任何其他持久化存储位置。

- **核心职责**:

  - **数据共享**: 提供一个安全、统一的接口，让其他应用可以查询或修改本应用的数据。
  - **数据抽象**: 隐藏了底层数据的存储细节。无论数据是存在数据库还是文件中，对外的接口都是一致的。
  - **权限控制**: 可以精细地控制其他应用对数据的读写权限。

- **工作方式**:

  - 通过一个唯一的 `URI` (Uniform Resource Identifier) 来标识数据。例如 `content://com.example.app.provider/users/10`。
  - 其他应用使用 `ContentResolver` 对象，通过 `query()`, `insert()`, `update()`, `delete()` 等方法与 Content Provider 进行交互。

- **逆向切入点**:
  - App 的联系人、短信、媒体库等都是通过 Content Provider 访问的。
  - 分析 `AndroidManifest.xml` 中声明的 `provider`，可以找到 App 对外暴露了哪些数据。
  - 逆向 App 时，可以自己编写一个 App 来调用目标 App 的 Content Provider，从而读取或操纵其内部数据。

---

<!-- 04-Reference/Foundations/android_manifest.md -->

# androidManifest.xml 深度解析

`AndroidManifest.xml` 是 Android 应用的"大脑"和"蓝图"。它是一个强制性的配置文件，位于每个 APK 的根目录中。该文件向 Android 构建工具、操作系统和 Google Play 描述了应用的基本信息、组件、权限和硬件要求。对于逆向工程师来说，这是了解应用功能、入口点和安全边界的首要切入点。

---

## # 核心作用与特性

- **唯一标识**: 定义了应用的 Java 包名，这是它在设备和 Google Play 上的唯一标识。

- **组件声明**: 声明应用的所有核心组件（四大组件）。任何未在此文件中声明的组件都对系统不可见，也无法运行。

- **权限请求**: 列出应用需要访问的受保护部分 API 或系统资源所需的权限。

- **硬件/软件要求**: 声明应用运行所需的硬件功能（如摄像头、蓝牙）和最低 Android API 级别。

- **入口点定义**: 通过 `intent-filter` 指定哪个 Activity 是应用的启动器。

- **重要提示\*\***: 原始的 `AndroidManifest.xml` 是二进制格式的。必须使用 `apktool`, `jadx`, `aapt` 等工具解码后才能阅读。

---

## # 关键标签 (Tags) 详解

### `<manifest>`

根元素。它必须包含 `package` 属性来定义应用的唯一包名。

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
package="com.example.myapp">
...
</manifest>

```

- `android:theme`: 应用的全局主题。

- `android:name`: 指定 `Application` 子类的名称，常用于应用初始化。这是 Hook 的绝佳目标。

- `android:debuggable`: **（安全关键）** `true` 表示应用是可调试的，允许 `adb` 连接和任意代码执行。发布的 Release 版本必须为 `false`。

- `android:allowBackup`: **（安全关键）** `true` 允许用户通过 `adb backup` 备份应用数据。如果应用数据敏感，应设为 `false`。

- `android:networkSecurityConfig`: **（安全关键）** 指向网络安全配置文件，用于定义 SSL Pinning、自定义 CA 等高级网络策略。

### `<activity>`

声明一个 Activity (UI 界面)。

- `android:name`: Activity 类的名称。`.MyActivity` 是 `package.MyActivity` 的简写。

- `android:exported`: **（安全关键）** `true` 表示该 Activity 可以被其他应用启动。如果该 Activity 处理敏感数据且无需外部调用，应设为 `false`，否则可能导致组件劫持和数据泄露。对于包含 `LAUNCHER` intent-filter 的 Activity，`exported` 默认为 `true`。

### `<service>`

声明一个 Service (后台服务)。

- `android:name`: Service 类的名称。

- `android:exported`: **（安全关键）** `true` 表示该 Service 可以被其他应用绑定或启动。规则同 Activity。

### `<receiver>`

声明一个 BroadcastReceiver (广播接收器)。

- `android:name`: Receiver 类的名称。

- `android:exported`: **（安全关键）** `true` 表示它可以接收来自系统或其他应用的广播。

### `<provider>`

声明一个 ContentProvider (内容提供者)，用于跨应用共享数据。

- `android:name`: Provider 类的名称。

- `android:authorities`: Provider 的唯一标识符，通常是包名加上描述性后缀。

- `android:exported`: **（安全关键）** `true` 表示其他应用可以访问其数据。如果 `minSdkVersion` 或 `targetSdkVersion` >= 17，默认值为 `false`。不正确的 `exported` 设置可能导致 SQL 注入或文件遍历漏洞。

### `<uses-permission>`

请求应用运行所需的权限。这是分析应用行为的关键。

```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
<uses-permission android:name="android.permission.CAMERA" />

```

<activity android:name=".MainActivity" android:exported="true">
<intent-filter>
<action android:name="android.intent.action.MAIN" />
<category android:name="android.intent.category.LAUNCHER" />
</intent-filter>
<intent-filter>
<action android:name="android.intent.action.VIEW" />
<category android:name="android.intent.category.DEFAULT" />
<data android:scheme="http" android:host="example.com" />
</intent-filter>
</activity>

```

1. **确定入口点**:

* 寻找 `MAIN/LAUNCHER` 的 Activity。

* 寻找 `android:name` 属性定义的 `Application` 子类，这是最早执行代码的地方。

2. **识别核心功能**:

* 阅读权限列表 (`<uses-permission>`)，快速了解应用能力。

* 查看声明的 Activities、Services，推测其功能模块。

3. **寻找攻击面**:

* 检查所有组件的 `android:exported="true"` 属性，这些是潜在的攻击入口。

* 分析 `intent-filter`，特别是自定义的 `scheme`，寻找 URL Scheme 漏洞。

* 检查 `android:debuggable="true"`，如果为 `true`，可以直接附加调试器。

* 检查 `android:allowBackup="true"`，尝试 `adb backup` 导出数据。
___
## # 安全风险与配置

* **组件导出风险**: 错误地将内部组件设置为 `exported="true"` 是最常见的 Android 漏洞之一。

* **Webview 风险**: 检查是否使用了 `WebView`，并确认是否开启了 `setJavaScriptEnabled(true)`，这可能导致远程代码执行。

* **File Provider 路径遍历**: 如果 `ContentProvider` 是 `FileProvider`，不正确的配置可能导致任意文件读取。

* **硬编码密钥**: 虽然不在 Manifest 中，但分析后应在 `res/values/strings.xml` 或代码中寻找硬编码的 API 密钥或 URL。
```

<!-- 04-Reference/Foundations/android_studio_debug_tools.md -->

---

# android Studio 调试工具集

Android Studio 不仅仅是一个代码编辑器，它还集成了一套强大、可视化的调试和分析工具，能够极大地提升开发和逆向分析的效率。熟悉这些工具是每个 Android 工程师的必备技能。

---

## 1. 日志猫 (Logcat)

- _概念_: Logcat 是一个命令行工具，用于查看 Android 系统的日志输出。Android Studio 将其封装在一个便捷的窗口中，可以实时查看来自系统和所有应用的日志信息。
- _核心功能_:
  - **实时日志流**: 显示来自设备或模拟器的连续日志。
  - **日志级别过滤**: 可以按 Verbose, Debug, Info, Warn, Error, Assert 等级别进行过滤。在调试时，通常关注 Error 和 Warn 级别。
  - **进程/应用过滤**: 可以只显示当前正在调试的应用，或特定进程的日志。
  - **关键词搜索**: 强大的搜索功能，支持正则表达式，可以快速找到你关心的日志条目。
  - **堆栈跟踪点击**: 当日志中包含异常堆栈时，可以直接点击类名和行号，跳转到源码的对应位置。
- _逆向应用_:
  - 很多 App 在开发阶段会留下大量的调试日志，其中可能包含敏感信息，如加密前的请求参数、服务器返回的明文等。
  - 通过观察 App 在特定操作下的日志输出，可以推断其内部的工作流程。

---

## 2. 布局检查器 (Layout Inspector)

- _概念_: 这是一个强大的可视化工具，允许你实时检查和调试正在运行的应用的视图层次结构。
- _核心功能_:
  - **3D 视图层次**: 以 3D 可旋转的视图展示当前 Activity 的所有 `View` 组件是如何嵌套的。
  - **属性查看**: 点击任何一个 `View`，都可以实时查看其所有的属性，如 `ID`, `text`, `width`, `height`, `padding`, `color` 等。
  - **实时更新**: 在设备上操作 UI，布局检查器中的视图会实时同步更新。
  - **定位重叠视图**: 可以轻松发现被其他视图遮挡或尺寸为 0 的不可见视图。
- _逆向应用_:
  - 快速定位一个按钮或文本框的 `resource-id`，这是编写 UIAutomator2 等自动化脚本的关键。
  - 分析自定义 `View` 的绘制方式和内部结构。
  - 理解一些反截图、反录屏技术是如何通过添加一个透明的 `FLAG_SECURE` 窗口来实现的。

---

## 3. 应用分析器 (Profiler)

- _概念_: Profiler 是一套用于实时分析应用性能的工具，主要关注 CPU、内存、网络和电量四个方面。
- _核心功能_:
  - **CPU Profiler**:
    - **方法追踪 (Method Tracing)**: 可以记录下在一个时间段内所有函数的调用栈和执行时间，生成火焰图。这对于寻找性能瓶颈至关重要。
    - **系统调用追踪**: 可以查看 App 与系统内核的交互情况。
  - **Memory Profiler**:
    - **实时内存占用**: 显示 App 的 Java 堆、Native 堆和图形内存的实时使用情况。
    - **堆转储 (Heap Dump)**: 可以捕获某一时刻的内存快照，并分析其中所有的对象实例、引用关系。
    - **内存泄漏检测**: 长期运行并观察内存曲线，可以帮助定位内存泄漏问题。
  - **Network Profiler**:
    - **网络请求时间线**: 以时间线的形式展示 App 发起的所有网络请求，包括请求的建立时间、发送时间和接收时间。
    - **请求详情**: 可以查看每个请求的 URL、请求头、响应头和 Payload。**（注意：对于 HTTPS 流量，默认只能看到加密后的内容，需要配合其他抓包工具使用）**。
- _逆向应用_:
  - **方法追踪**: 通过对一个加密函数进行追踪，可以完整地了解其内部都调用了哪些子函数，帮助理解复杂算法。
  - **堆转储**: 在 App 解密并加载了某些核心数据到内存后，通过 Heap Dump 可能会找到这些数据对象，甚至是密钥对象。
  - **网络分析**: 虽然不能解密 HTTPS，但可以快速了解 App 在何时、向哪些域名发起了网络请求，为网络抓包提供目标。

---

## 4. 数据库检查器 (Database Inspector)

- _概念_: 允许你实时检查、查询和修改正在运行的应用中的数据库（SQLite）。
- _核心功能_:
  - **实时数据查看**: 实时显示数据库中所有表的内容。
  - **自定义查询**: 可以直接运行 SQL 查询语句来检索或修改数据。
  - **数据修改**: 可以直接在图形界面中修改字段的值。
  - **保持连接**: 即使 App 进程被杀死后重启，检查器也能保持连接。
- _逆向应用_:
  - 很多 App 会将用户信息、配置、聊天记录等重要数据存储在 SQLite 数据库中。通过数据库检查器，可以一目了然地分析其数据结构和内容。
  - 通过修改数据库中的值（例如，将会员状态字段从 0 改为 1），可以测试和验证一些本地的 VIP 功能绕过。

---

<!-- 04-Reference/Foundations/apk_structure.md -->

# APK 文件结构详解

APK (Android Package) 是 Android 操作系统用于分发和安装移动应用的文件格式。它本质上是一个 ZIP 归档文件，包含了应用的所有代码、资源、证书等。理解其内部结构是逆向工程和安全分析的第一步。

---

## 目录

- [APK 文件结构详解](#apk-文件结构详解)
- [目录](#目录)
- [APK 概览](#apk-概览)

- [核心文件与目录详解](#核心文件与目录详解)
- [`AndroidManifest.xml`](#androidmanifestxml)

- [`classes.dex`](#classesdex)

- [`resources.arsc`](#resourcesarsc)

- [`res/`](#res)

- [`lib/`](#lib)

- [`assets/`](#assets)

- [`META-INF/`](#meta-inf)
- [APK 分析流程](#apk-分析流程)

---

### APK 概览

一个标准的 APK 文件，当用解压缩工具打开时，通常会看到以下目录结构：

```
├── resources.arsc # [Required] Pre-compiled resource file, index for strings, layouts, etc.
├── res/ # [Required] Uncompiled resource directory for icons, layout XMLs, etc.
├── lib/ # [Optional] Directory for native libraries (.so files)
├── assets/ # [Optional] Directory for raw app assets
└── META-INF/ # [Required] Directory for app signature and certificate information

```

- **包名 (Package Name)**: 应用在系统中的唯一标识符 (e.g., `com.example.app`)。

- **组件 (Components)**: 声明所有的四大组件：
- `Activity`: 用户界面。

- `Service`: 后台服务。

- `BroadcastReceiver`: 广播接收器。

- `ContentProvider`: 内容提供者。
- **权限 (Permissions)**: 声明应用需要向系统申请的权限 (e.g., `android.permission.INTERNET`)。

- **入口点 (Entry Point)**: 指定哪个 Activity 是应用的启动入口（`LAUNCHER` Activity）。

- **SDK 版本**: 指定最低支持的 SDK 版本和目标 SDK 版本。

- 分析提示\*\*: 必须使用 `apktool` 或 `jadx` 等工具将其解码为人类可读的 XML 格式。直接用文本编辑器打开是乱码。

#### `classes.dex`

我们已经在 `dex.md` 中详细讨论过。这是由 Java/Kotlin 代码编译、转换后生成的 Dalvik 虚拟机字节码。应用的所有逻辑都在这里。如果应用方法数超过 65536 个，就会有 `classes2.dex`, `classes3.dex` 等文件。

- 分析提示\*\*: 使用 `jadx` 可以将其反编译为 Java 代码，使用 `baksmali` 可以反汇编为 Smali 代码。

#### `resources.arsc`

这是一个二进制资源索引表。Android 系统使用它来快速查找和匹配资源。它包含了一个从资源 ID 到具体资源文件（或字符串值）的映射关系。

例如，当代码中调用 `R.string.app_name` 时，系统通过 `resources.arsc` 找到 `app_name` 对应的字符串值。

- 分析提示\*\*: `apktool` 可以解码此文件，将其中的字符串等资源还原到 `res/values/strings.xml` 等文件中。直接查看是二进制格式。

#### `res/`

存放**未编译**的资源文件，这些资源在打包时大多保持原样或只进行简单处理。目录结构与 Android Studio 项目中的 `res` 目录类似。

- `res/drawable/`: 图片资源。

- `res/layout/`: 布局 XML 文件。

- `res/xml/`: 任意 XML 文件。

- `res/raw/`: 任意原始二进制文件。

- 分析提示\*\*: 这里的布局 XML 文件虽然可读，但它们引用的字符串等资源是以 `@string/app_name` 的形式存在的，需要结合 `resources.arsc` 才能完全理解。

#### `lib/`

存放应用使用的 C/C++ 原生库（`.so` 文件）。为了适配不同的 CPU 架构，它通常包含多个子目录。

- `armeabi-v7a`: 适用于 32 位的 ARM 架构。

- `arm64-v8a`: 适用于 64 位的 ARM 架构 (目前主流)。

- `x86`: 适用于 32 位的 x86 架构（常见于模拟器）。

- `x86_64`: 适用于 64 位的 x86 架构（常见于模拟器）。

- 分析提示\*\*: 核心的加密、解密、核心算法或游戏引擎常常在这里实现。需要使用 `IDA Pro`, `Ghidra`, `Binary Ninja` 等工具进行逆向分析。

#### `assets/`

这是一个"原封不动"的资源目录。与 `res/raw` 类似，这里的任何文件在打包时都不会被系统处理。开发者通常用它来存放游戏资源、配置文件、字体、HTML/JS/CSS 等。

- 分析提示\*\*: 检查此目录是否有敏感的配置文件、密钥或 Web 资源。

#### `META-INF/`

存放应用的签名信息，用于验证 APK 的完整性和来源。

- `CERT.SF`: APK 中每个文件的摘要（哈希值）。

- `CERT.RSA`: 包含用于签署 `CERT.SF` 的公钥和证书。

- `MANIFESF.MF`: 包含 APK 中每个文件的名称及其 SHA-256 哈希值。

- **签名机制\*\***:

1. 计算 APK 中每个文件的哈希，并记录在 `MANIFESF.MF`。
2. 计算 `MANIFESF.MF` 整个文件的哈希，并记录在 `CERT.SF`。
3. 用开发者的私钥对 `CERT.SF` 进行签名，生成 `CERT.RSA`。

当系统安装 APK 时，会用 `CERT.RSA` 中的公钥来验证签名，确保文件自签名后未被篡改。

- 分析提示\*\*: 对 APK 进行任何修改（包括重打包）后，都必须用自己的密钥重新签名，否则安装会失败。

---

### APK 分析流程

1. **解包**: 使用 `apktool d myapp.apk` 或直接用 `unzip` 命令解压。`apktool` 是首选，因为它能正确解码 `AndroidManifest.xml` 和 `resources.arsc`。
2. **静态分析**:

- 用 `jadx-gui myapp.apk` 打开，直接浏览反编译的 Java 代码和资源。

- 阅读 `AndroidManifest.xml`，了解其主要组件、权限和入口点。

- 检查 `assets/` 和 `lib/` 目录，寻找关键配置文件或原生库。

3. **动态分析**: 使用 `adb` 安装应用，并用 `frida` 或 `Xposed` 进行 Hook，观察其运行时行为。

<!-- 04-Reference/Foundations/arm_assembly.md -->

# ARM 汇编入门 (android Native)

当应用的核心逻辑、加密算法或性能密集型任务用 C/C++ 编写时，它们会被编译成原生库 (`.so` 文件)。在 Android 上，这些库主要是 ARM 架构的。理解 ARM 汇编是分析 `.so` 文件的基础。本指南将介绍逆向工程师需要了解的 ARMv7 (32-bit) 和 ARMv8 (64-bit/A64) 的基础知识。

!!! question "思考：为什么必须学习汇编？"
当你遇到以下场景时，该如何应对？

- 用 Jadx 打开 APK，发现关键的加密逻辑都在 `native` 方法中
- Frida Hook 到了某个 JNI 函数，但参数是指针，不知道如何读取
- IDA 打开 `.so` 文件，满屏的汇编指令让你无从下手

这些场景的共同点是：**核心逻辑被编译成了机器码**。不理解汇编，就像试图在不懂外语的情况下阅读外文书籍——你只能靠猜。

---

## 目录

1. [**基本概念：ARM vs x86**](#基本概念arm-vs-x86)
2. [**寄存器 (Registers)**](#寄存器-registers)

- [ARM 32-bit (ARMv7)](#arm-32-bit-armv7)

- [ARM 64-bit (AArch64)](#arm-64-bit-aarch64)

3. [**核心指令集**](#核心指令集)

- [数据移动指令](#数据移动指令)

- [算术与逻辑指令](#算术与逻辑指令)

- [分支与条件执行指令](#分支与条件执行指令)

- [栈操作指令](#栈操作指令)

4. [**函数调用约定 (Procedure Call Standard)**](#函数调用约定)
5. [**从 C 代码到汇编**](#从-c-代码到汇编)
6. [**IDA Pro/Ghidra 中的视图**](#ida-proghidra-中的视图)

---

### 基本概念：ARM vs x86

- **RISC vs CISC**: ARM 是**精简指令集计算机 (RISC)**，指令长度固定，种类较少，操作简单。x86 是**复杂指令集计算机 (CISC)**。

- **Load/Store 架构**: ARM 是一种"加载/存储"架构。这意味着数据处理（如加法、减法）**只能在寄存器之间**进行。你必须先用加载指令 (`LDR`) 将内存中的数据加载到寄存器，计算完成后再用存储指令 (`STR`) 将结果存回内存。

- **指令模式**: ARMv7 (32-bit) 支持两种指令集：
- **ARM**: 32-bit 定长指令，功能强大。

- **Thumb**: 16-bit/32-bit 变长指令，代码密度更高，是移动设备上的主流。在 IDA 等工具中，你通常会分析 Thumb 模式下的代码。

---

### 寄存器 (Registers)

寄存器是 CPU 内的高速存储单元。

!!! tip "快速定位关键寄存器"
在分析一个陌生函数时，如何快速抓住重点？

- **函数入口**：先看 `R0-R3` (32 位) 或 `X0-X7` (64 位)，这些是参数
- **函数返回**：关注 `R0/X0`，这是返回值存放的地方
- **函数调用**：`BL` 指令前后，检查参数寄存器的变化
- **栈操作**：`SP` 的变化反映了局部变量的分配

这种"重点优先"的阅读策略，能让你快速理解函数的输入输出，而不必逐行分析每条指令。

#### ARM 32-bit (ARMv7)

共有 16 个通用寄存器 (`R0` - `R15`)。

| 寄存器       | 别名        | 用途                                                                                |
| :----------- | :---------- | :---------------------------------------------------------------------------------- |
| `R0` - `R3`  | `A1` - `A4` | **参数寄存器** (Argument)。用于传递函数的前 4 个参数。`R0` 也用作**返回值寄存器**。 |
| `R4` - `R11` | `V1` - `V8` | **变量寄存器** (Variable)。用于保存函数的局部变量。                                 |
| `R12`        | `IP`        | 过程调用间临时寄存器 (Intra-Procedure call scratch register)。                      |
| `R13`        | `SP`        | **栈指针** (Stack Pointer)。指向栈顶。                                              |
| `R14`        | `LR`        | **链接寄存器** (Link Register)。存储函数调用的返回地址。                            |
| `R15`        | `PC`        | **程序计数器** (Program Counter)。指向当前正在执行的指令。                          |

#### ARM 64-bit (AArch64)

寄存器数量更多，且功能更明确。

| 寄存器        | 用途                                                                       |
| :------------ | :------------------------------------------------------------------------- | -------------------------------- |
| `X0` - `X7`   | **参数寄存器**。用于传递函数的前 8 个参数。`X0` 同样用作**返回值寄存器**。 |
| `X8` - `X18`  | 调用者/被调用者保存的临时寄存器。                                          |
| `X19` - `X28` | 被调用者保存的寄存器 (Callee-saved)。                                      |
| `X29`         | `FP`                                                                       | **帧指针** (Frame Pointer)。     |
| `X30`         | `LR`                                                                       | **链接寄存器** (Link Register)。 |
| `SP`          | **栈指针** (Stack Pointer)。                                               |

- 注\*\*: `W` 寄存器 (`W0`, `W1`...) 是 `X` 寄存器的低 32 位。例如，对 `W0` 的操作就是对 `X0` 的低 32 位进行操作。

---

### 核心指令集

#### 数据移动指令

- `MOV R1, R2` (32-bit) / `MOV X1, X2` (64-bit): 将寄存器 `R2` 的值移动到 `R1`。

- `LDR R0, [SP, #4]` (32-bit) / `LDR X0, [SP, #8]` (64-bit): **加载**。从栈指针 `SP` 偏移 4 (或 8) 字节的位置读取数据，并存入 `R0` (或 `X0`)。

- `STR R0, [SP, #4]` (32-bit) / `STR X0, [SP, #8]` (64-bit): **存储**。将 `R0` (或 `X0`) 的值写入到 `SP` 偏移 4 (或 8) 字节的内存地址。

- `ADR X0, aHelloWorld` (64-bit, PC-relative): `ADR` (Address PC-Relative) 指令将一个相对于 PC 的地址（如字符串 "Hello World" 的地址）加载到 `X0`。

#### 算术与逻辑指令

- `ADD R0, R1, R2`: `R0 = R1 + R2`。

- `SUB R0, R1, #1`: `R0 = R1 - 1`。

- `and R0, R0, #0xFF`: 按位与。

- `CMP R0, #10`: **比较** `R0` 和 10。该指令会更新状态寄存器 (CPSR)，但不存储结果。它总是紧跟在条件分支指令之前。

#### 分支与条件执行指令

- `B label`: **分支** (Branch)。无条件跳转到 `label`。

- `BL label`: **带链接的分支** (Branch with Link)。跳转到 `label` 之前，将下一条指令的地址存入 `LR` (链接寄存器)。这是**函数调用**的核心指令。

- `BX LR` / `RET`: **带交换的分支** (Branch with Exchange) / **返回**。跳转到 `LR` 中的地址，实现函数返回。`RET` 是 `BX LR` 的别名。

- `B.EQ label`: **条件分支**。如果前一个 `CMP` 指令的结果是相等 (Equal)，则跳转。

- `B.NE label`: 不相等 (Not Equal)。

- `B.GT label`: 大于 (Greater Than)。

- `B.LT label`: 小于 (Less Than)。

- `B.GE label`: 大于或等于 (Greater or Equal)。

- `B.LE label`: 小于或等于 (Less or Equal)。

#### 栈操作指令

- `PUSH {R4, LR}`: 将 `R4` 和 `LR` 寄存器压入栈。通常在函数开头，用于保存需要使用的寄存器和返回地址。

- `POP {R4, PC}`: 将栈顶数据弹出到 `R4` 和 `PC`。`POP {..., PC}` 是一种常见的函数返回方式，它将保存在栈上的 `LR` 值直接弹出到 `PC`，实现了跳转返回。

- `STP X29, X30, [SP, #-16]!` (A64): `STP` (Store Pair) 指令，将一对寄存器 (`X29`/`FP`, `X30`/`LR`) 存入 `SP` 指向的地址，`!` 表示 `SP` 会预先减去 16。

- `LDP X29, X30, [SP], #16` (A64): `LDP` (Load Pair) 指令，从 `SP` 地址加载数据到 `X29` 和 `X30`，然后 `SP` 再增加 16。

---

### 函数调用约定 (Procedure Call Standard)

1. **参数传递**:

- **32-bit**: 前 4 个参数通过 `R0` - `R3` 传递。

- **64-bit**: 前 8 个参数通过 `X0` - `X7` 传递。

- 超出数量的参数通过**栈**传递。

2. **函数调用**: 调用者使用 `BL` 指令。
3. **函数序言 (Prologue)**:

- 被调用函数（子函数）首先要做的是保存现场。

- 使用 `PUSH` 或 `STP` 将需要在函数中使用的寄存器（如 `R4-R11`, `FP`, `LR`) 压入栈中。

- 分配栈空间给局部变量 (`SUB SP, SP, #...`)。

4. **函数结语 (Epilogue)**:

- 函数执行完毕，准备返回。

- 释放局部变量的栈空间 (`ADD SP, SP, #...`)。

- 使用 `POP` 或 `LDP` 从栈中恢复之前保存的寄存器。

- 使用 `BX LR` 或 `RET` 或 `POP {PC}` 返回。

5. **返回值**:

- 简单的返回值（整数、指针）存放在 `R0` (32-bit) 或 `X0` (64-bit) 中。

---

### 从 C 代码到汇编

- **C 代码:\*\***

```c
int add_one(int a) {
return a + 1;
}

```

BX LR ; return

```
RET ; return

```

- **伪代码视图 (Pseudocode View)**: IDA Pro (F5 键) 和 Ghidra 的反编译器可以直接将汇编代码转换成可读性很高的 C 伪代码，这是静态分析的利器。通常先看伪代码，遇到不理解的地方再回头看汇编。

<!-- 04-Reference/Foundations/art_runtime.md -->

# android 运行时 (ART) 深度解析

ART (Android Runtime) 是 Android 5.0 (Lollipop) 之后默认的应用程序运行时环境，取代了旧的 Dalvik 虚拟机 (DVM)。ART 的引入显著改变了 Android 应用的执行方式，旨在提高应用的性能、启动速度和电池续航。

---

## 目录

- [Android 运行时 (ART) 深度解析](#android-运行时-art-深度解析)
- [目录](#目录)
- [核心机制：AOT vs JIT](#核心机制aot-vs-jit)
- [Dalvik 的 JIT (Just-In-Time)](#dalvik-的-jit-just-in-time)

- [ART 的 AOT (Ahead-Of-Time)](#art-的-aot-ahead-of-time)

- [混合编译 (AOT + JIT)](#混合编译-aot--jit)
- [ART 生成的文件格式](#art-生成的文件格式)
- [OAT 文件 (`.oat`)](#oat-文件-oat)

- [VDEX 文件 (`.vdex`)](#vdex-文件-vdex)

- [ART 文件 (`.art`) (Image)](#art-文件-art-image)
- [ART vs. Dalvik](#art-vs-dalvik)

- [对逆向工程的影响](#对逆向工程的影响)

---

### 核心机制：AOT vs JIT

!!! question "思考：为什么逆向工程师必须理解 ART？"
你可能会想："我只关心应用的 Java 代码和加密算法，ART 的编译机制与我有什么关系？"

- **实际场景告诉你答案\*\***：

* **Frida Hook 失败**：你写的 Hook 脚本在 Android 4.x 上好用，在 8.0+ 上就不工作了——因为 ART 的 AOT 编译改变了方法的执行方式
* **脱壳困境**：你用传统方法 dump DEX，结果发现关键类根本不在 DEX 里——它们在运行时被解密后直接编译成了 OAT
* **性能分析**：为什么同样的代码在不同 Android 版本上性能差异巨大？混合编译模式是关键
* **反调试对抗**：某些 App 会检测 OAT 文件的完整性，或者利用 `dex2oat` 的时机来进行反调试

- **核心要点\*\***：

* Android 5.0+ 的应用不再是简单的"DEX 字节码"执行
* 真正执行的是 **本地机器码**（OAT 文件）
* 理解 DEX → VDEX → OAT 的转换流程，才能应对现代 Android 逆向

#### Dalvik 的 JIT (Just-In-Time)

在 Android 4.4 及更早版本中，Dalvik 虚拟机使用 JIT 编译。

- **工作方式**: 应用每次运行时，Dalvik 会解释执行 DEX 字节码。对于频繁执行的"热点代码" (hotspot)，JIT 编译器会将其动态地编译成本地机器码并缓存。

- **优点**: 安装速度快，不占用额外存储空间。

- **缺点**: 应用启动和运行期间需要持续进行解释和编译，导致启动慢、耗电多。

#### ART 的 AOT (Ahead-Of-Time)

ART 最初的设计是纯 AOT 编译。

- **工作方式**: 在应用**安装时**，系统会调用 `dex2oat` 工具，将 APK 中的 `classes.dex` 文件完整地编译成本地机器码，并以 OAT 文件的形式存储。

- **优点**:

- **运行速度快**: 应用直接执行本地机器码，无需实时编译，性能和启动速度都大大提升。

- **更省电**: CPU 在运行时负担更轻。

- **缺点**:

- **安装时间长**: 应用安装过程需要额外的编译时间。

- **占用空间大**: 预编译的 OAT 文件会占用更多的存储空间。

#### 混合编译 (AOT + JIT)

从 Android 7.0 (Nougat) 开始，ART 引入了结合 JIT 的混合编译模式，以平衡上述优缺点。

- **工作流程**:

1. **初次安装**: 应用安装速度很快，不进行 AOT 编译。

2. **首次运行**: 应用代码由解释器执行，同时 JIT 编译器会介入，编译热点代码。在此期间，ART 会生成一份**代码执行频率的分析文件 (Profile)**。

3. **设备空闲时**: 当设备处于空闲状态并正在充电时，Android 系统会启动一个后台优化任务。该任务会根据之前收集的 Profile 信息，**只对那些频繁执行的热点方法进行 AOT 编译**，并生成新的 OAT 文件。

- **优点**: 兼顾了安装速度、运行性能和存储占用，是目前 Android 的标准执行模式。

---

### ART 生成的文件格式

当 ART 处理一个 APK 时，会在 `/data/dalvik-cache/<arch>/` 目录下生成一些优化后的文件。

#### OAT 文件 (`.oat`)

OAT (Optimized Android file format) 文件是核心。它包含了由 `dex2oat` 从 DEX 字节码编译而来的**本地机器码** (ARM 汇编)。一个 OAT 文件通常包含：

- **oatdata**: 包含已编译的本地代码。

- **oatexec**: 包含可执行的本地代码。

- **oatlastword**: 标识 OAT 文件的结束。

#### VDEX 文件 (`.vdex`)

从 Android 8.0 (Oreo) 开始引入。为了进一步优化，系统会将原始的 `classes.dex` 文件进行"解压缩"和"验证"，生成一个 VDEX (`Verified DEX`) 文件。这样做的好处是：

- **快速验证**: 系统可以直接使用 VDEX 文件，跳过了对原始 DEX 的验证步骤，加快了加载速度。

- **内容**: VDEX 文件本质上是一个未压缩的、带有额外依赖和验证信息的 DEX 文件。`dex2oat` 会直接使用 VDEX 文件作为输入来生成 OAT 文件。

#### ART 文件 (`.art`) (Image)

这是一个预加载的镜像文件，包含了系统启动时需要预加载的一些核心类（如 `java.lang.Object`）。当 Zygote 进程启动时，会直接将这个镜像映射到内存，从而避免了对这些常用类进行重复的初始化，加快了所有应用的启动速度。

- **总结\*\***: 在现代 Android 系统中，执行流程是：`classes.dex` -> (安装时) `.vdex` -> (后台优化时) `.oat`。

---

### ART vs. Dalvik

| 特性              | ART                    | Dalvik     |
| :---------------- | :--------------------- | :--------- |
| **编译模式**      | AOT + JIT 混合编译     | JIT        |
| **执行单元**      | 本地机器码 (主要)      | DEX 字节码 |
| **性能**          | 更高                   | 较低       |
| **启动速度**      | 更快                   | 较慢       |
| **安装时间**      | 更快 (混合模式下)      | 快         |
| **存储占用**      | 更高 (因 OAT 文件)     | 较低       |
| **垃圾回收 (GC)** | 优化更好，暂停时间更短 | 效率较低   |

---

### 对逆向工程的影响

!!! tip "实战技巧：从 ART 机制找到突破口"
理解 ART 的工作原理，能让你找到很多"非常规"的逆向思路：

- **脱壳新思路\*\***：

1. **监控 `dex2oat` 调用**：某些壳会在运行时动态调用 `dex2oat`，监控其命令行参数能发现隐藏的 DEX
2. **从 VDEX 提取 DEX**：Android 8.0+ 的 VDEX 文件本质上就是 DEX，用 `vdexExtractor` 可以快速提取
3. **从 OAT 还原 DEX**：使用 `oat2dex` 等工具从编译后的 OAT 文件反推原始 DEX

- **Hook 优化策略\*\***：

* **Java 方法 Hook**：优先 Hook Java 层 API，更稳定通用
* **Native Hook**：当 Java Hook 失效时，找到 ART 编译后的机器码地址进行 inline hook
* **GOT/PLT Hook**：Hook 动态链接库的导入表，绕过代码完整性检查

- **Hook 点的变化**: 由于存在 AOT 编译，Frida/Xposed 等框架的 Hook 原理也需要适应。它们不仅仅是 Hook Java 方法，实际上是找到了该方法编译后的本地机器码地址，并对其进行修改（inline hook）。

- **脱壳的复杂性**: 许多加固厂商利用 ART 的 AOT 机制。他们可能会在运行时动态解密并加载 DEX，然后手动调用 `dex2oat` 生成 OAT 文件来执行。这使得传统的 DEX Dump 方法失效，需要对 OAT 文件格式和 `dex2oat` 的调用时机进行监控。

- **OAT 文件分析**: 高级逆向分析有时需要直接分析 OAT 文件。有一些工具（如 `oatdump`）可以从 OAT 文件中提取出原始的 DEX 数据或查看编译后的汇编代码。

- **寻找代码的源头**: 即使代码被 AOT 编译，其元数据依然与原始的 DEX 文件相关联。因此，我们的分析起点通常还是从 `classes.dex` 反编译出的 Java 代码开始，而不是直接一头扎进 OAT 文件的汇编代码中。

<!-- 04-Reference/Foundations/dex_format.md -->

# DEX 文件权威指南

DEX (Dalvik Executable) 文件是 Android 操作系统的核心组成部分之一。它们是专门为在内存和处理器速度受限的设备上高效运行而设计的。本指南将深入探讨 DEX 文件的定义、格式、运行原理以及相关工具。

!!! question "思考：理解 DEX 格式的实战价值"
很多初学者会问："DEX 格式这么复杂，我真的需要了解这些底层细节吗？"

考虑这些实际场景：

- **加固对抗**：当 App 使用了 DEX 加壳（如梆梆、360），你需要知道 DEX 的魔数、签名字段在哪，才能判断脱壳是否完整
- **动态加载分析**：很多 App 会在运行时解密并加载隐藏的 DEX，理解 `Class Defs` 结构能帮你快速定位被隐藏的恶意代码
- **Multi-DEX 定位**：当你想 Hook 某个类，但不知道它在哪个 `classes.dex` 中时，理解 String IDs 和 Type IDs 能帮你快速搜索
- **方法数优化**：理解 65536 方法数限制的根本原因（Method IDs 索引用 16 位），能帮你更好地进行模块化设计

DEX 格式不是学术知识，而是你破解加固、分析恶意代码的**手术刀**。

---

## 目录

1. [**定义与角色**：什么是 DEX 文件？](#定义与角色)
2. [**DEX vs. CLASS**：与 Java 字节码的对比](#dex-vs-class)
3. [**DEX 文件结构**：深入剖析格式](#dex-文件结构)
4. [**运行原理**：DEX 文件如何被执行？](#运行原理)
5. [**Multi-DEX**：应对方法数限制](#multi-dex)
6. [**DEX 分析与处理工具**](#dex-分析与处理工具)

---

### 定义与角色

- **DEX 文件**是包含了 Android 应用代码的单个可执行文件。在打包（Build）过程中，Java 编译器首先将 `.java` 源码文件编译成标准的 Java 字节码 `.class` 文件。然后，Android SDK 中的 `d8` 工具（旧版本为 `dx`）会将所有的 `.class` 文件（包括项目代码和依赖库）优化并合并成 **一个或多个\*\*** `classes.dex` 文件。

这个 `classes.dex` 文件最终被打包进 APK (Android Package) 中。当用户安装并运行应用时，Android 系统（特别是 ART）会直接执行 DEX 文件中的代码。

- **核心角色\*\***：

- **紧凑性**: 将所有类文件合并，并共享字符串和常量，大大减少了文件体积和 I/O 开销。

- **高效性**: 采用基于寄存器的指令集，更接近底层硬件，执行效率比基于栈的 JVM 更高。

- **移动优化**: 专为内存有限的移动设备设计。

本文档参考了 Android 官方关于 [DEX 文件格式](https://source.android.com/docs/core/dalvik/dex-format) 的说明。

---

### DEX vs. CLASS

| 特性           | `.class` 文件 (JVM)              | `.dex` 文件 (ART/Dalvik)                       |
| -------------- | -------------------------------- | ---------------------------------------------- |
| **文件数量**   | 每个源文件对应一个 `.class` 文件 | 所有 `.class` 文件合并成一个或多个 `.dex` 文件 |
| **指令集架构** | **基于栈 (Stack-based)**         | **基于寄存器 (Register-based)**                |
| **常量池**     | 每个文件都有自己独立的常量池     | 所有类共享一个全局的字符串和常量池             |
| **冗余信息**   | 大量冗余字符串（如类名、方法名） | 字符串和常量去重，通过索引引用，冗余少         |
| **平台**       | 任何有 JVM 的地方                | Android 平台                                   |
| **转换工具**   | `javac`                          | `javac` -> `d8`/`dx`                           |

---

### DEX 文件结构

DEX 文件格式非常紧凑和高效，其结构可以大致分为以下几个部分，并由一个 `header` 来描述整个文件的元数据和偏移量。

!!! tip "逆向技巧：从结构入手快速定位"
面对一个陌生的 DEX 文件，如何快速找到你感兴趣的代码？

- **自顶向下的分析策略\*\***：

1. **看 Header**：检查魔数确认文件完整性，查看 `class_defs_size` 了解有多少个类
2. **搜 String IDs**：用 `dexdump` 或 `strings` 搜索关键字符串（如 "encrypt", "http://"），定位可疑代码
3. **查 Method IDs**：通过方法名索引找到具体实现
4. **跳 Class Defs**：直接定位到目标类的完整定义
5. **读 Code Item**：最后才深入字节码细节

这种"线索驱动"的方法，比漫无目的地浏览代码高效得多。

<!-- ![DEX File Structure](../images/dex-format.png) -->

A DEX file consists of several main sections:

### 1. 头部 (Header)

- **Header**: 文件头，包含魔数（`dex\n035\0`）、校验和、签名，以及指向其他数据结构（如字符串、类定义等）的偏移量和大小。

- **String IDs**: 字符串标识符列表。包含 DEX 文件中用到的所有字符串（如类名、方法名、变量名、字符串常量），并为每个字符串分配一个唯一的 ID。

- **Type IDs**: 类型标识符列表。包含代码中用到的所有类型（类、接口、数组、基本类型），并指向 `String IDs` 中的相应字符串。

- **Proto IDs**: 方法原型标识符列表。定义了方法的返回类型和参数类型。

- **Field IDs**: 字段标识符列表。定义了类的成员变量，包括其所属类、类型和名称。

- **Method IDs**: 方法标识符列表。定义了方法，包括其所属类、原型 (Proto ID) 和名称。

- **Class Defs**: 类定义列表。这是核心部分，包含了每个类的详细信息：访问标志、父类、实现的接口、源码文件名、注解、以及指向其字段和方法的指针。

- **Data Section**: 数据区，包含了所有类的实际内容，例如：
- **Code Item**: 实际的方法字节码（Dalvik 指令）。

- **Class Data**: 类的字段和方法列表的具体数据。

- **Map List**: 描述整个 DEX 文件数据布局的映射表，`dexdump` 等工具使用它来解析文件。

---

### 运行原理

DEX 文件的执行由 Android 运行时 (ART) 负责，在 Android 5.0 之前由 Dalvik 虚拟机 (DVM) 负责。

#### 1. Dalvik 虚拟机 (DVM) - android 4.4 及更早版本

- **JIT (Just-In-Time) 编译**: 当应用运行时，DVM 会解释执行 DEX 字节码。对于频繁执行的"热点"代码路径，JIT 编译器会将其动态编译成本地机器码，以提高后续执行速度。

- **缺点**: 每次启动应用都需要进行解释和 JIT 编译，导致应用启动速度较慢，且运行时消耗更多计算资源。

#### 2. android 运行时 (ART) - Android 5.0 及更高版本

- **AOT (Ahead-Of-Time) 编译**: 在应用**安装时**，ART 会使用 `dex2oat` 工具将 DEX 文件中的字节码预编译成设备原生的机器码，并保存为 OAT (Optimized Android file format) 文件。

- **优点**:
- **启动速度快**: 应用直接执行预编译的本地代码，无需实时编译，大大加快了启动速度。

- **性能更高**: AOT 可以进行更深度的优化，性能通常优于 JIT。

- **更省电**: 减少了运行时的 CPU 计算负担。
- **AOT + JIT 混合模式 (Android 7.0+ )**:
- 为了平衡安装速度/空间占用和性能，ART 引入了混合模式。

- **安装时**: 不进行完全 AOT 编译，或只编译部分关键代码。

- **首次运行**: 解释执行，并使用 JIT 编译热点代码，同时收集分析信息 (Profile)。

- **设备空闲时**: 当设备充电且空闲时，系统会根据收集到的分析信息，对常用代码进行 AOT 编译，实现最佳性能。

---

### Multi-DEX

单个 DEX 文件有一个方法引用数上限（65,536 个），当应用（包括其依赖库）的方法总数超过这个限制时，编译会失败。

为了解决这个问题，Android 引入了 **Multi-DEX** 机制。打包工具会将应用代码分割到多个 DEX 文件中，例如 `classes.dex`, `classes2.dex`, `classes3.dex` 等。主 `classes.dex` 文件会优先加载，然后应用代码会负责加载其余的 DEX 文件。

从 Android 5.0 (API 21) 开始，ART 原生支持加载多个 DEX 文件，无需额外的库。对于更早的版本，则需要使用官方的 `multidex-support-library`。

---

### DEX 分析与处理工具

| 工具                 | 描述                                                                                           |
| -------------------- | ---------------------------------------------------------------------------------------------- |
| **d8 / dx**          | Google 官方工具，用于将 `.class` 文件转换为 `.dex` 文件。`d8` 是新一代的转换器。               |
| **dexdump**          | 位于 Android SDK `build-tools` 中，用于打印 DEX 文件的详细信息，包括头信息、类、方法和字节码。 |
| **baksmali**         | 将 `.dex` 文件反汇编成 `.smali` 文件。Smali 是一种人类可读的 Dalvik 字节码表示形式。           |
| **smali**            | 将 `.smali` 文件重新汇编成 `.dex` 文件。常用于修改应用逻辑后重新打包。                         |
| **Jadx**             | 非常强大的反编译工具，可以直接将 APK/DEX 文件反编译成可读的 Java 代码，并提供图形化界面。      |
| **Ghidra / IDA Pro** | 高级逆向工程工具，支持对 DEX 文件和原生库进行深度静态和动态分析。                              |

<!-- 04-Reference/Foundations/smali_syntax.md -->

# Smali 语法入门

Smali/Baksmali 是 Dalvik 虚拟机字节码的汇编器/反汇编器。Smali 是对 DEX 格式的一种人类可读的表示，允许我们精确地查看和修改应用的行为。理解 Smali 是进行 Android 应用静态 patching（修改后重打包）的关键。

---

## 目录

- [Smali 语法入门](#smali-语法入门)

- [目录](#目录)

- [基本概念](#基本概念)

- [数据类型与表示](#数据类型与表示)

- [文件与类结构](#文件与类结构)

- [字段 (Fields)](#字段-fields)

- [方法 (Methods)](#方法-methods)

- [核心指令](#核心指令)

- [变量操作指令](#变量操作指令)

- [对象操作指令](#对象操作指令)

- [方法调用指令](#方法调用指令)

- [跳转/条件指令](#跳转条件指令)

- [运算指令](#运算指令)

- [Smali 实战：修改方法](#smali-实战修改方法)

---

### 基本概念

- **寄存器 (Registers)**: Dalvik VM 是基于寄存器的。方法内的局部变量存储在寄存器中。

- `v` 开头的寄存器用于存放本地变量，如 `v0`, `v1`, `v2`...

- `p` 开头的寄存器用于存放方法参数，如 `p0`, `p1`, `p2`...

- 对于非静态方法，`p0` 总是指向 `this` (当前对象实例)。

- 参数从 `p1` 开始。例如，一个有两个参数的非静态方法，`p0` 是 `this`，`p1` 是第一个参数，`p2` 是第二个参数。对于静态方法，参数从 `p0` 开始。

- **`.locals`**: 声明一个方法使用了多少个本地变量寄存器。

- **`.prologue`**: 方法体的序言部分。

- **`.line`**: 对应原始 Java 代码的行号，用于调试。

---

### 数据类型与表示

Smali 使用特定的描述符来表示 Java 中的数据类型。

| Smali 类型        | Java 类型           | 描述                            |
| :---------------- | :------------------ | :------------------------------ |
| `V`               | `void`              | 空返回类型                      |
| `Z`               | `boolean`           | 布尔值                          |
| `B`               | `byte`              | 字节                            |
| `S`               | `short`             | 短整型                          |
| `C`               | `char`              | 字符                            |
| `I`               | `int`               | 整型                            |
| `J`               | `long`              | 长整型 (占用两个寄存器)         |
| `F`               | `float`             | 浮点型                          |
| `D`               | `double`            | 双精度浮点型 (占用两个寄存器)   |
| `L<包名>/<类名>;` | `package.ClassName` | 对象类型，以 `L` 开头，`;` 结尾 |
| `[<类型>`         | `type[]`            | 数组类型，`[I` 代表 `int[]`     |

- **示例\*\***:

* `Ljava/lang/String;` -> `java.lang.String`

* `[I` -> `int[]`

* `[[Ljava/lang/Object;` -> `java.lang.Object[][]`

---

### 文件与类结构

每个 `.smali` 文件对应一个 Java 类。

```smali
# Define class, access modifiers, and complete class path
.class public Lcom/example/app/MainActivity;

# Define superclass
.super Landroid/app/Activity;

# Define source file name, optional
.source "MainActivity.java"

# ... Field definitions ...

# ... Method definitions ...

```

# Format: .field <access_modifier> [static] [final] <field_name>:<field_type>

.field private TAG:Ljava/lang/String;
.field public static final MY_CONSTANT:I = 0x1

```
# Format: .method <access_modifier> [static] [final] <method_name>(<parameter_types>)<return_type>
.method public onCreate(Landroid/os/Bundle;)V
# Declare number of local variable registers
.locals 3

# Declare parameter registers
.param p1, "savedInstanceState" # p1 is savedInstanceState

# Method body begins
.prologue
.line 15

# ... Smali instructions ...

# Method return
return-void
.end method

```

- `const-string v1, "Hello"`: 将字符串 "Hello" 赋值给 `v1`。

- `move-result-object v0`: 将上一个 `invoke` 指令返回的对象结果移动到 `v0`。

- `move-result v0`: 将上一个 `invoke` 指令返回的非对象结果移动到 `v0`。

- `move-exception v0`: 在 `catch` 块中，将捕获的异常对象移动到 `v0`。

#### 对象操作指令

- `new-instance v0, Ljava/lang/StringBuilder;`: 创建一个 `StringBuilder` 的新实例，并将其引用存入 `v0`。

- `iget-object v0, p0, Lcom/example/app/MyClass;->myField:Ljava/lang/String;`: 获取实例字段 (iget) 的值。从 `p0` (this) 对象中读取 `myField` 字段，并存入 `v0`。

- `iput-object v1, p0, Lcom/example/app/MyClass;->myField:Ljava/lang/String;`: 设置实例字段 (iput) 的值。将 `v1` 的值赋给 `p0` (this) 对象的 `myField` 字段。

- `sget-object v0, Lcom/example/app/Constants;->SOME_STRING:Ljava/lang/String;`: 获取静态字段 (sget) 的值。

- `sput-object v0, Lcom/example/app/Constants;->SOME_STRING:Ljava/lang/String;`: 设置静态字段 (sput) 的值。

#### 方法调用指令

- `invoke-virtual {p0, p1}, Lcom/example/app/MyClass;->myMethod(I)V`: 调用一个 `virtual` 方法（最常见的公有/保护方法）。`{p0, p1}` 是参数列表，`p0` 是 `this`，`p1` 是第一个参数。

- `invoke-direct {p0}, Ljava/lang/Object;-><init>()V`: 调用一个 `direct` 方法（私有方法或构造函数）。这里是调用父类的构造函数。

- `invoke-static {v0}, Landroid/util/Log;->d(Ljava/lang/String;Ljava/lang/String;)I`: 调用一个 `static` 方法。

- `invoke-super {p0, p1}, Landroid/app/Activity;->onCreate(Landroid/os/Bundle;)V`: 调用父类的方法。

- `invoke-interface {p0, v0}, Ljava/util/List;->add(Ljava/lang/Object;)Z`: 调用接口方法。

#### 跳转/条件指令

- `goto :label_10`: 无条件跳转到 `:label_10` 标签。

- `if-eqz v0, :label_10`: 如果 `v0` 等于 0 (或 `false`/`null`)，则跳转到 `:label_10`。`eqz` (equal zero)。

- `if-nez v0, :label_10`: 如果 `v0` 不等于 0 (或 `true`/`not null`)，则跳转。`nez` (not equal zero)。

- `if-eq v0, v1, :label_10`: 如果 `v0` 等于 `v1`，则跳转。

#### 运算指令

- `add-int v0, v1, v2`: `v0 = v1 + v2` (整型加法)。

- `sub-int v0, v1, v2`: `v0 = v1 - v2` (整型减法)。

- `mul-int/2addr v0, v1`: `v0 = v0 * v1` (`/2addr` 表示结果存回第一个源寄存器)。

---

### Smali 实战：修改方法

假设我们要修改一个方法，让它总是返回 `true`。

- **原始 Java 代码:\*\***

```java
public class LicenseCheck {
public boolean isLicensed() {
// ...ComplexCheckLogic...
return false;
}
}

```

# Complex check logic corresponding smali instructions...

const/4 v0, 0x0 # v0 = 0 (false)
return v0
.end method

```

# Remove all complex check logic

const/4 v0, 0x1 # v0 = 1 (true)
return v0
.end method

```

- 使用 `apktool b myapp -o new_app.apk` 重新打包。
- 用 `jarsigner` 或 `apksigner` 对 `new_app.apk` 进行签名。

<!-- 04-Reference/Foundations/so_elf_format.md -->

# android .so 文件详解 (ELF Format)

`.so` 文件（Shared Object）是 Android 平台上的原生共享库，等同于 Windows 上的 `.dll` 或 Linux 上的 `.so`。它们包含了由 C/C++ 等原生代码编译而成的机器码。在 Android 逆向工程中，分析 `.so` 文件是理解应用核心逻辑、破解加密算法和绕过安全机制的关键一步。

---

## 目录

1. [**ELF 文件格式**](#elf-文件格式)

- [ELF Header](#elf-header)

- [Program Header Table](#program-header-table)

- [Section Header Table](#section-header-table)

- [关键 Section](#关键-section)

- [ELF Header](#elf-header)

- [Program Header Table](#program-header-table)

- [Section Header Table](#section-header-table)

- [关键 Section](#关键-section)

2. [**加载与链接**](#加载与链接)

- [`System.loadLibrary()`](#systemloadlibrary)

- [JNI (Java Native Interface)](#jni-java-native-interface)

- [动态链接器 (`/system/bin/linker`)](#动态链接器-systembinlinker)

- [`System.loadLibrary()`](#systemloadlibrary)

- [JNI (Java Native Interface)](#jni-java-native-interface)

- [动态链接器 (`/system/bin/linker`)](#动态链接器-systembinlinker)

3. [**静态分析**](#静态分析)

- [识别关键函数](#识别关键函数)

- [使用 IDA Pro / Ghidra](#使用-ida-pro--ghidra)

- [识别关键函数](#识别关键函数)

- [使用 IDA Pro / Ghidra](#使用-ida-pro--ghidra)

4. [**动态分析**](#动态分析)

- [Frida Hook 原生函数](#frida-hook-原生函数)

- [Unidbg 模拟执行](#unidbg-模拟执行)

- [Frida Hook 原生函数](#frida-hook-原生函数)

- [Unidbg 模拟执行](#unidbg-模拟执行)

5. [**常见保护手段**](#常见保护手段)

---

### ELF 文件格式

`.so` 文件遵循 **ELF (Executable and Linkable Format)** 格式，这是一种用于可执行文件、目标代码、共享库和核心转储的标准文件格式。

#### ELF Header

位于文件开头，描述了整个文件的"档案"，包括：

- **Magic Number**: 文件的前 16 个字节，用于识别这是一个 ELF 文件。

- **Architecture**: 标识文件是为哪种 CPU 架构编译的（如 ARM, ARM64, x86）。

- **Type**: 文件类型（可执行文件、共享库等）。

- **Entry Point Address**: 如果是可执行文件，这是程序启动的地址。

- **Program Header Table Offset**: 指向程序头表的偏移。

- **Section Header Table Offset**: 指向节头表的偏移。

#### Program Header table

描述了系统如何将文件的各个部分（段，Segments）加载到内存中。每个条目都定义了一个段的类型（如 `LOAD`，表示需要加载到内存）、虚拟地址、物理地址、大小和权限（读、写、执行）。动态链接器 (`linker`) 依赖这个表来正确映射 `.so` 文件。

#### Section Header table

描述了文件中各个"节"（Sections）的信息。节是链接器用来组织和处理数据的单位。

#### 关键 Section

- **.text**: 包含已编译的程序机器码（汇编指令）。这是分析的核心区域。

- **.rodata**: 只读数据区，通常存放字符串常量、const 变量等。

- **.data**: 已初始化的可读可写数据区（全局变量和静态变量）。

- **.bss**: 未初始化的数据区。在文件中不占空间，但在加载到内存时会被分配并清零。

- **.init_array** / **.fini_array**: 存放一系列函数指针，这些函数会在库被加载 (`dlopen`) 时（`.init_array`）或卸载 (`dlclose`) 时（`.fini_array`）自动执行。**这是分析 `.so` 文件自启动逻辑和反调试的绝佳入口点**。

- **.dynsym** (Dynamic Symbol Table): 动态符号表，包含了库中导出（提供给外部使用）和导入（需要从其他库引用）的函数和变量名。

- **.dynstr** (Dynamic String Table): 字符串表，`.dynsym` 中的符号名称就存储在这里。

---

### 加载与链接

#### `System.loadLibrary()`

在 Java/Kotlin 代码中，开发者通过 `System.loadLibrary("mylib")` 来加载一个名为 `libmylib.so` 的原生库。系统会在 `lib/` 目录下的相应 ABI 文件夹（如 `arm64-v8a`）中查找并加载该库。

#### JNI (Java Native Interface)

JNI 是连接 Java 世界和 Native (C/C++) 世界的桥梁，是 Android 逆向分析中的核心知识点。

##### JNI 基础概念

- **Java 侧声明\*\***:

```java
public class NativeHelper {
static {
System.loadLibrary("native-lib"); // Load libnative-lib.so
}

// Static native method
public static native String doEncrypt(String input);

// Instance native method
public native byte[] processData(byte[] data, int flag);

// Multiple parameter native method
public native int complexOperation(String str, int[] array, boolean flag);
}

```

// Static method JNI function signature: second parameter is jclass
JNIEXPORT jstring JNICALL
Java_com_example_app_NativeHelper_doEncrypt(JNIEnv *env, jclass clazz, jstring input) {
const char *nativeString = (*env)->GetStringUTFChars(env, input, 0);
// Execute encryption logic...
jstring result = (*env)->NewStringUTF(env, encrypted_result);
(\*\*env)->ReleaseStringUTFChars(env, input, nativeString);
return result;
}

// Instance method JNI function signature: second parameter is jobject
JNIEXPORT jbyteArray JNICALL
Java_com_example_app_NativeHelper_processData(JNIEnv *env, jobject thiz, jbyteArray data, jint flag) {
jsize len = (*env)->GetArrayLength(env, data);
jbyte *body = (*env)->GetByteArrayElements(env, data, 0);

// Process data...

jbyteArray result = (*env)->NewByteArray(env, len);
(*env)->SetByteArrayRegion(env, result, 0, len, processed_data);
(\*\*env)->ReleaseByteArrayElements(env, data, body, 0);
return result;
}

````


- 常用函数分类：

- **字符串操作**: `NewStringUTF()`, `GetStringUTFChars()`, `ReleaseStringUTFChars()`

- **数组操作**: `NewByteArray()`, `GetByteArrayElements()`, `SetByteArrayRegion()`

- **对象操作**: `NewObject()`, `GetObjectClass()`, `CallObjectMethod()`

- **字段访问**: `GetFieldID()`, `GetIntField()`, `SetIntField()`

- **方法调用**: `GetMethodID()`, `CallVoidMethod()`, `CallIntMethod()`


- **字符串操作**: `NewStringUTF()`, `GetStringUTFChars()`, `ReleaseStringUTFChars()`


- **数组操作**: `NewByteArray()`, `GetByteArrayElements()`, `SetByteArrayRegion()`


- **对象操作**: `NewObject()`, `GetObjectClass()`, `CallObjectMethod()`


- **字段访问**: `GetFieldID()`, `GetIntField()`, `SetIntField()`


- **方法调用**: `GetMethodID()`, `CallVoidMethod()`, `CallIntMethod()`


**2. 数据类型映射**

```c
// Java type -> JNI type
boolean -> jboolean
byte -> jbyte
char -> jchar
short -> jshort
int -> jint
long -> jlong
float -> jfloat
double -> jdouble
String -> jstring
Object -> jobject
Class -> jclass
Array -> jarray (jintArray, jbyteArray etc.)

````

- 示例：`Java_com_example_myapp_crypto_AESUtil_encrypt`

##### JNI 方法注册

**静态注册**（编译时确定）：

```c
// Function name must strictly follow naming rules
JNIEXPORT jstring JNICALL
Java_com_example_app_MainActivity_stringFromJNI(JNIEnv *env, jobject thiz) {
return (*env)->NewStringUTF(env, "Hello from JNI!");
}

```

{"encrypt", "(Ljava/lang/String;)Ljava/lang/String;", (void*)native_encrypt},
{"decrypt", "([B)[B", (void*)native_decrypt},
{"init", "(I)V", (void\*\*)native_init}
};

// JNI_OnLoad function will be automatically called when library is loaded
JNIEXPORT jint JNICALL JNI_OnLoad(JavaVM* vm, void* reserved) {
JNIEnv* env;
if ((*vm)->GetEnv(vm, (void\*\*\*\*)&env, JNI_VERSION_1_6) != JNI_OK) {
return JNI_ERR;
}

jclass clazz = (\*\*env)->FindClass(env, "com/example/app/NativeHelper");
if (clazz == NULL) {
return JNI_ERR;
}

// Register native methods
if ((\*\*env)->RegisterNatives(env, clazz, gMethods,
sizeof(gMethods)/sizeof(gMethods[0])) < 0) {
return JNI_ERR;
}

return JNI_VERSION_1_6;
}

```

S - short
I - int
J - long
F - float
D - double
V - void

```

[[Ljava/lang/String; - String[][]

```

// Java: public native void processArray(int[] data, boolean flag);
// JNI Signature: ([IZ)V

```

nm -D libexample.so | grep Java\_

# Or use objdump

objdump -T libexample.so | grep Java\_

```
"libnative.so",
"Java_com_example_app_NativeHelper_doEncrypt"
);

Interceptor.attach(encrypt_func, {
onEnter: function (args) {
// args[0] = JNIEnv*
// args[1] = jclass/jobject
// args[2] = first parameter (jstring)
var jstring_ptr = args[2];
var str_content = Java.vm.getEnv().getStringUtfChars(jstring_ptr, null);
console.log("Input: " + str_content.readCString());
},
onLeave: function (retval) {
var result = Java.vm.getEnv().getStringUtfChars(retval, null);
console.log("Output: " + result.readCString());
},
});

```

var NativeHelper = Java.use("com.example.app.NativeHelper");

NativeHelper.doEncrypt.implementation = function (input) {
console.log("Java -> Native: " + input);
var result = this.doEncrypt(input);
console.log("Native -> Java: " + result);
return result;
};
});

```
JNIEXPORT void JNICALL
Java_com_example_app_Security_checkDebugger(JNIEnv *env, jclass clazz) {
if (ptrace(PTRACE_TRACEME, 0, 1, 0) == -1) {
// Debugger detected, execute countermeasure
exit(1);
}
}

```

// XOR decryption example
static char decrypted[256];
int key = 0x42;
for (int i = 0; encrypted[i]; i++) {
decrypted[i] = encrypted[i] ^ key;
}
return decrypted;
}

```
Java_com_example_app_Security_isEmulator(JNIEnv *env, jclass clazz) {
// Check system property
char prop_value[256];
__system_property_get("ro.kernel.qemu", prop_value);
return strcmp(prop_value, "1") == 0;
}

```

3. 解析该库的依赖项（即它需要从其他库，如 `libc.so`，导入的函数），并填充导入函数的地址。
4. 执行 `.init_array` 中的初始化函数。

---

### 静态分析

#### 识别关键函数

- **JNI 函数**: 在 IDA/Ghidra 中，直接在符号列表中搜索 `Java_` 前缀，可以快速定位所有 Java 和 Native 的交互点。

- **导出函数**: 查看 `Exports` 列表，寻找有意义的函数名，如 `encrypt`, `decrypt`, `checkSignature` 等。

- **`.init_array` 函数**: 查看 `.init_array` section，分析在库加载时自动执行的函数，这些函数经常被用来实现反调试或初始化加密密钥。

#### 使用 IDA Pro / Ghidra

1. **加载文件**: 将 `.so` 文件拖入 IDA 或 Ghidra。
2. **查看伪代码**: 按 `F5` (IDA) 或等待 Ghidra 的自动分析，直接阅读反编译出的 C 伪代码。这是最高效的分析方式。
3. **交叉引用 (Cross-References)**: 对一个函数名或字符串常量按 `X` 键，可以查看所有引用了它的地方，从而追踪数据流和调用关系。
4. **图形模式**: 使用图形视图来理解复杂的函数调用流程和条件分支。

---

### 动态分析

#### Frida Hook 原生函数

当静态分析困难（如代码被混淆或算法复杂）时，动态 Hook 是最有效的方法。

```javascript
// frida script
const baseAddr = Module.findBaseAddress("libnative-lib.so");
const targetFuncPtr = baseAddr.add(0x1234); // 0x1234 is function offset from IDA/Ghidra

Interceptor.attach(targetFuncPtr, {
  onEnter: function (args) {
    // args[0], args[1]... are function parameters (pointers)
    console.log("Hooked function called!");
    // Can use Memory.readCString(args[0]) etc. to read parameter content
  },
  onLeave: function (retval) {
    // retval is function return value
    // retval.replace(0x1); // Can modify return value
  },
});
```

#### 字符串加密

- **保护机制\*\***: `.so` 文件中的敏感字符串（如密钥、URL）被加密存放，在运行时动态解密使用。静态分析时无法直接看到。

- **攻击方法\*\***:

* Hook 解密函数: 找到解密函数入口，打印解密后的字符串

* 内存 Dump: 在解密后 Hook 内存读取操作，获取明文字符串

* 交叉引用分析: 使用 `axt` 查看调用最多的函数，通常是解密函数

```javascript
// Frida Hook example
var decrypt_func = Module.findExportByName("libnative.so", "decrypt_string");
Interceptor.attach(decrypt_func, {
  onLeave: function (retval) {
    console.log("Decrypted string:", Memory.readCString(retval));
  },
});
```

- **攻击方法\*\***:

* 动态分析为主: 绕过静态分析困难，直接 Hook 关键函数

* 去混淆工具: 使用 d810 (IDA 插件) 等工具去除控制流平坦化

* 模拟执行: 使用 Unidbg 模拟执行，获取算法输入输出

* 指令级 Hook: Hook 汇编指令级别，观察寄存器变化

```javascript
// Hook instruction-level example
var baseAddr = Module.findBaseAddress("libnative.so");
Interceptor.attach(baseAddr.add(0x1000), {
  onEnter: function (args) {
    console.log("Register state:", this.context);
  },
});
```

- **攻击方法\*\***:

* Hook 反调试函数: 直接返回正常值，绕过检测

* 修改检测逻辑: 使用 Frida 修改内存中的反调试代码

* 环境伪装: 修改系统调用返回值，伪装正常环境

* Spawn 模式: 使用 Frida 的 spawn 模式，在应用启动前注入

```javascript
// Bypass anti-debugging example
var anti_debug = Module.findExportByName("libnative.so", "check_debug");
Interceptor.attach(anti_debug, {
  onLeave: function (retval) {
    retval.replace(0); // Return 0 to indicate no debugging detected
  },
});

// Hook ptrace system call
var ptrace = Module.findExportByName("libc.so", "ptrace");
Interceptor.attach(ptrace, {
  onEnter: function (args) {
    args[0] = ptr(0); // Modify ptrace arguments
  },
});
```

### 调用时机详解

`.init_array` 中的函数在 **ELF 库加载过程中的早期阶段** 被调用，这个时机非常关键，发生在 JNI_OnLoad 之前。

#### 完整的调用流程

```

```

↓
nativeLoad() [art/runtime/native/java_lang_Runtime.cc]
↓
android_dlopen_ext() [bionic/libdl/libdl.cpp]
↓
do_dlopen() [bionic/linker/linker.cpp]
↓
find_library() → load_library() → link_image()
↓
call_constructors() → init_arrayFunctionExecute

```
// 1. First call DT_INIT initialization function
if (init_func_ != nullptr) {
init_func_();
}

// 2. Then iterate through .init_array section function pointers
if (init_array_ != nullptr) {
for (size_t i = 0; i < init_array_count_; ++i) {
// Call each constructor function, including init_string_obfuscation
((void (*)())init_array_[i])();
}
}
}

```

// String obfuscation initialization function declaration
**attribute**((constructor))
void init_string_obfuscation() {
// String decryption and anti-debugging logic
decrypt_critical_strings();
setup_anti_debug_measures();
}

// Can also specify priority (lower number = higher priority)
**attribute**((constructor(101)))
void init_anti_debug_level1() {
// First level anti-debugging detection
basic_environment_check();
}

**attribute**((constructor(102)))
void init_string_decryption() {
// String decryption, depends on first level detection passing
if (environment_safe) {
decrypt_strings();
}
}

````
4. **运行时调用**: 动态链接器按顺序调用所有函数指针


#### 实际应用示例

```cpp
// Actual string obfuscation initialization function example
__attribute__((constructor(100)))
void init_string_obfuscation() {
// 1. Environment security check
if (detect_debug_environment()) {
// Debug environment detected, execute countermeasures
execute_anti_debug_response();
return;
}

// 2. Decrypt critical strings
decrypt_api_strings();
decrypt_config_strings();
decrypt_url_strings();

// 3. Mark initialization complete
string_obfuscation_initialized = true;
}

// String decryption function
void decrypt_api_strings() {
// Decrypt API name strings
for (int i = 0; i < API_STRING_COUNT; i++) {
decrypt_string_xor(encrypted_api_names[i],
decrypted_api_names[i],
API_XOR_KEY);
}
}

// XOR decryption implementation
void decrypt_string_xor(const char* encrypted, char* decrypted, uint8_t key) {
int len = strlen(encrypted);
for (int i = 0; i < len; i++) {
decrypted[i] = encrypted[i] ^ key;
}
decrypted[len] = '\0';
}

````

- **优先级控制**: 可以通过参数控制多个初始化函数的执行顺序

#### 2. 安全防护优势

- **静态分析困扰**: 加密字符串在静态分析时不可见

- **运行时解密**: 只在运行时临时解密，增加分析难度

- **反调试集成**: 可在初始化阶段进行环境检测

#### 3. 逆向分析挑战

- **时机把握困难**: Hook 需要在 init_array 执行前完成

- **函数定位复杂**: 需要分析 ELF 结构才能准确定位

- **调试时机窗口短**: 执行时间短，难以及时介入

### 逆向分析对策

#### 静态分析方法

```python
# Python script to analyze .init_array section
from elftools.elf.elffile import ELFFile

def analyze_init_array(so_path):
with open(so_path, 'rb') as f:
elf = ELFFile(f)

# Find .init_array section
init_array_section = elf.get_section_by_name('.init_array')
if init_array_section:
data = init_array_section.data()

print(f"[+] Found .init_array section, size: {len(data)} bytes")

# Parse function pointers (8-byte aligned, 64-bit system)
for i in range(0, len(data), 8):
if i + 8 <= len(data):
func_addr = int.from_bytes(data[i:i+8], 'little')
print(f"[+] Init function {i//8}: 0x{func_addr:x}")

```

// Hook constructor call function
var call_constructors = Module.findExportByName(
"linker64",
"\_ZN6soinfo17call_constructorsEv"
);
if (call_constructors) {
Interceptor.attach(call_constructors, {
onEnter: function (args) {
var soinfo = args[0];
console.log("[+] Calling constructors for SO");
this.start_time = Date.now();
},
onLeave: function (retval) {
var duration = Date.now() - this.start_time;
console.log("[+] Constructors completed in " + duration + "ms");
},
});
}

// Directly hook init_array functions of target SO
hook_target_init_functions();
}

function hook_target_init_functions() {
var target_module = Process.findModuleByName("libtarget.so");
if (target_module) {
// Hook function at specific address based on static analysis results
var init_func_addr = target_module.base.add(0x2000); // Example address

Interceptor.attach(init_func_addr, {
onEnter: function (args) {
console.log("[!] init_string_obfuscation called");
console.log("[+] Call stack:");
console.log(
Thread.backtrace(this.context, Backtracer.ACCURATE)
.map(DebugSymbol.fromAddress)
.join("\n")
);
},
onLeave: function (retval) {
console.log("[!] init_string_obfuscation completed");
},
});
}
}

<!-- 04-Reference/Foundations/x86_and_arm_assembly_basics.md -->

# x86 与 ARM 汇编基础指南

汇编语言是与计算机硬件直接对话的低级编程语言，是逆向工程、系统编程和性能优化的基石。在当今世界，x86 和 ARM 是两种最主流的指令集架构 (ISA)。理解它们的核心概念与差异对于逆向工程师至关重要。

- **x86**: 由 Intel 主导，采用**CISC (复杂指令集计算机)** 设计。指令长度可变，功能强大但复杂，主要用于桌面和服务器。

- **ARM**: 由 ARM Holdings 设计，采用**RISC (精简指令集计算机)** 设计。指令长度固定，设计简洁优雅，功耗低，主宰了移动和嵌入式设备领域。

---

## 目录

- [x86 与 ARM 汇编基础指南](#x86-与-arm-汇编基础指南)
- [目录](#目录)

- [x86 汇编 (IA-32)](#x86-汇编-ia-32)
- [核心寄存器](#核心寄存器)

- [常用指令](#常用指令)

- [调用约定 (Calling Convention)](#调用约定-calling-convention)
- [ARM 汇编 (ARMv7)](#arm-汇编-armv7)
- [核心寄存器](#核心寄存器-1)

- [加载/存储 (Load/Store) 架构](#加载存储-loadstore-架构)

- [常用指令](#常用指令-1)

- [调用约定 (AAPCS)](#调用约定-aapcs)
- [x86 vs. ARM 核心差异对比](#x86-vs-arm-核心差异对比)

---

## x86 汇编 (IA-32)

以 32 位 x86 架构为例，其设计复杂而灵活。

### 核心寄存器

8 个 32 位通用寄存器，它们有主要用途，但在很多情况下可以通用。

| 寄存器  | 主要用途                                                                     |
| :------ | :--------------------------------------------------------------------------- |
| **EAX** | **累加器 (Accumulator)**: 通常用于存放函数返回值和算术运算结果。             |
| **EBX** | **基址 (Base)**: 常作为数据段的基址指针。                                    |
| **ECX** | **计数器 (Counter)**: 常用于循环计数。                                       |
| **EDX** | **数据 (Data)**: 常用于存放数据，特别是在乘除法中与 EAX 配合。               |
| **ESP** | **栈指针 (Stack Pointer)**: **永远指向栈顶**。                               |
| **EBP** | **基址指针 (Base Pointer)**: **永远指向当前函数栈帧的底部**。                |
| **ESI** | **源变址 (Source Index)**: 字符串和内存操作中的源地址。                      |
| **EDI** | **目的变址 (Destination Index)**: 字符串和内存操作中的目的地址。             |
| **EIP** | **指令指针 (Instruction Pointer)**: **永远指向下一条将要执行的指令的地址**。 |

### 常用指令

- **数据传送**:
- `MOV dest, src`: 将 `src` 的值赋给 `dest`。 (e.g., `MOV EAX, EBX`)

- `PUSH val`: 将 `val` 压入栈顶，`ESP` 减 4。

- `POP reg`: 从栈顶弹出一个值到 `reg`，`ESP` 加 4。

- `LEA reg, [mem]`: 将 `mem` 的**有效地址**加载到 `reg`，而不是其内容。
- **算术运算**:
- `ADD dest, src`: `dest = dest + src`

- `SUB dest, src`: `dest = dest - src`

- `INC reg`: `reg = reg + 1`

- `DEC reg`: `reg = reg - 1`
- **逻辑与跳转**:
- `CMP reg1, reg2`: 比较 `reg1` 和 `reg2` (实际是做减法)，并根据结果设置标志位。

- `JMP target`: 无条件跳转到 `target` 地址。

- `JE target`: 如果相等 (Zero Flag=1) 则跳转。

- `JNE target`: 如果不相等 (Zero Flag=0) 则跳转。

- `JG/JL/JGE/JLE`: 大于/小于/大于等于/小于等于时跳转。
- **函数调用**:
- `CALL target`: 将 `EIP` 的下一条指令地址压栈，然后跳转到 `target`。

- `RET`: 从栈顶弹出地址，并跳转到该地址。

### 调用约定 (Calling Convention)

规定了函数如何传递参数和返回结果。常见于 32 位 Windows 的是 `stdcall`，而 Linux/macOS 上常见 `cdecl`。

- **`cdecl`**:
- 参数从右到左依次压入栈中。

- **调用者**负责在函数返回后清理栈。
- **`stdcall`**:
- 参数从右到左依次压入栈中。

- **被调用者**自己负责在返回前清理栈。

---

## ARM 汇编 (ARMv7)

以 32 位 ARM 架构为例，其设计简洁而高效。

### 核心寄存器

共有 16 个 32 位通用寄存器 (R0-R15)。

| 寄存器       | 别名   | 主要用途                                                                |
| :----------- | :----- | :---------------------------------------------------------------------- |
| **R0 - R3**  |        | **参数/返回值**: 用于传递函数的前 4 个参数，`R0` 也用于存放函数返回值。 |
| **R4 - R12** |        | 通用寄存器，用于保存局部变量。                                          |
| **R13**      | **SP** | **栈指针 (Stack Pointer)**: 指向栈顶。                                  |
| **R14**      | **LR** | **链接寄存器 (Link Register)**: **存储函数的返回地址**。                |
| **R15**      | **PC** | **程序计数器 (Program Counter)**: **指向下一条将要执行的指令**。        |

### 加载/存储 (Load/Store) 架构

这是 RISC 的核心思想。**CPU 不能直接对内存中的数据进行运算**。

1. 必须先用 `LDR` (Load Register) 指令将内存中的数据加载到寄存器中。
2. 在寄存器之间完成所有算术和逻辑运算。
3. 再用 `STR` (Store Register) 指令将结果存回内存。

### 常用指令

- **数据传送**:
- `MOV Rd, Rn`: 将 `Rn` 的值赋给 `Rd`。 (e.g., `MOV R0, R1`)
- **算术运算**:
- `ADD Rd, Rn, Rm`: `Rd = Rn + Rm`

- `SUB Rd, Rn, Rm`: `Rd = Rn - Rm`
- **内存操作**:
- `LDR Rd, [Rn, #offset]`: 从地址 `Rn + offset` 加载一个字到 `Rd`。

- `STR Rd, [Rn, #offset]`: 将 `Rd` 的值存储到一个字到地址 `Rn + offset`。
- **栈操作**:
- `PUSH {reg_list}`: 将寄存器列表压入栈。

- `POP {reg_list}`: 将值从栈中弹出到寄存器列表。
- **跳转与比较**:
- `CMP Rn, Rm`: 比较 `Rn` 和 `Rm`，并设置标志位。

- `B target`: 无条件跳转到 `target`。

- `BEQ target`: 如果相等则跳转。

- `BNE target`: 如果不相等则跳转。

- `BL target`: **(Branch with Link)** "调用函数"。它会**自动将下一条指令的地址存入 LR 寄存器**，然后跳转到 `target`。

- 函数返回时，只需执行 `MOV PC, LR` 或 `BX LR` 即可。

### 调用约定 (AAPCS)

ARM Procedure Call Standard。

- **参数传递**:
- 前 4 个参数通过 **R0, R1, R2, R3** 传递。

- 剩余的参数通过栈传递。
- **返回值**:
- 返回值存储在 **R0** 中。
- **返回地址**:
- 通过 **LR** 寄存器管理。

---

## x86 vs. ARM 核心差异对比

| 特性         | x86 (CISC)                                      | ARM (RISC)                                            |
| :----------- | :---------------------------------------------- | :---------------------------------------------------- |
| **指令集**   | 复杂，长度可变                                  | 精简，长度固定                                        |
| **内存访问** | **可以直接对内存操作** (e.g., `ADD [mem], EAX`) | **加载/存储架构** (必须先 `LDR`，再 `STR`)            |
| **寄存器**   | 较少，且有特定用途                              | 较多，大多为通用寄存器                                |
| **函数调用** | `CALL` 指令压栈 `EIP`                           | `BL` 指令将返回地址存入 `LR` 寄存器                   |
| **参数传递** | 主要通过**栈**                                  | 主要通过**寄存器** (R0-R3)                            |
| **条件执行** | 通过 `CMP` 和 `Jcc` 跳转指令                    | **所有指令都可以是条件执行的** (e.g., `MOVEQ R0, R1`) |

<!-- 05-Appendix/ctf_platforms.md -->

---

# CTF 与 练习平台 (CTF & Practice Platforms)

实践是掌握逆向工程技术的关键。本页面整理了提供 Android 逆向挑战的 CTF 平台和 CrackMe 网站。

---

## 移动安全专项挑战 (Mobile Specific Challenges)

### OWASP UnCrackable Apps

- **描述**: OWASP 官方提供的一系列 Android 和 iOS 逆向挑战应用，分为 Level 1 到 Level 4 不同难度。是学习移动安全测试标准 (MSTG) 的最佳配套练习。
- **链接**: [OWASP MSTG Repo](https://github.com/OWASP/owasp-mastg/tree/master/Crackmes)

### Google CTF (Mobile Category)

- **描述**: Google 每年举办的 CTF 比赛中的 Mobile 类目题目。这些题目通常质量很高，涉及各种 Android 特性和新颖的保护机制。
- **链接**: [Google CTF Archives](https://capturetheflag.withgoogle.com/) (查看历年题目)

### android App Reverse Engineering 101 Crackmes

- **描述**: Maddie Stone 在她的 Workshop 中使用的练习题目。
- **链接**: [GitHub Repo](https://github.com/maddiestone/AndroidAppRE)

---

## 综合 CTF 平台 (General CTF Platforms)

### Hack The Box (HTB)

- **描述**: 著名的渗透测试练习平台，其中也有不少 Android 逆向相关的 Challenge (通常在 Mobile 或 Reversing 分类下) 和 Machine。
- **链接**: [https://www.hackthebox.com/](https://www.hackthebox.com/)

### TryHackMe

- **描述**: 对初学者更友好的网络安全学习平台，提供有引导性的 Android 逆向房间 (Rooms)。
- **链接**: [https://tryhackme.com/](https://tryhackme.com/)

### CTFtime

- **描述**: 全球 CTF 赛事聚合平台。可以在这里关注即将开始的比赛，很多综合性比赛都会包含 Reverse 和 Mobile 方向的题目。
- **链接**: [https://ctftime.org/](https://ctftime.org/)

---

## CrackMe 网站

### Crackmes.one

- **描述**: 全球最大的 CrackMe 收集网站。你可以通过搜索 "Android" 或 "APK" 标签找到大量的 Android 逆向练习程序，难度从简单到极难都有。
- **链接**: [https://crackmes.one/](https://crackmes.one/)

### Root Me

- **描述**: 一个涵盖各种安全领域的练习平台，其 "Cracking" 和 "App - Script" 分类下有一些针对移动应用的挑战。
- **链接**: [https://www.root-me.org/](https://www.root-me.org/)

---

## 推荐练习路线

1. **入门**: 从 **OWASP UnCrackable Level 1** 开始，学习基本的反编译、代码分析和简单的逻辑绕过。
2. **进阶**: 尝试 **Crackmes.one** 上评分较高的 Android 题目，或者 **Hack The Box** 的简单 Mobile 挑战。
3. **高级**: 挑战 **Google CTF** 的历史题目，或者 **OWASP UnCrackable Level 3/4**，主要涉及各种反调试、Native 层混淆、壳分析等。

---

<!-- 05-Appendix/github_projects.md -->

# 逆向工程领域相关的 GitHub 开源项目

本列表旨在收集和分类逆向工程领域的优秀开源项目，方便查阅和学习。

---

## 目录

- [逆向工程领域相关的 GitHub 开源项目](#逆向工程领域相关的-github-开源项目)
- [目录](#目录)
- [1. 动态分析与插桩工具](#1-动态分析与插桩工具)

- [2. 反汇编器与反编译器](#2-反汇编器与反编译器)

- [3. 调试器](#3-调试器)

- [4. 静态分析与二进制分析](#4-静态分析与二进制分析)

- [5. Android 平台](#5-android-平台)

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
| [dsincl/procmon-parser](https://github.com/dsincl/procmon-parser)                                                           | 170       | Sysinternals Process Monitor (Procmon) 的日志解析器。                  |
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
| [NationalSecurityAgency/ghidra](https://github.com/NationalSecurityAgency/ghidra) | 47.9k     | NSA 出品的软件逆向工程框架，包含反编译器。               |
| [radareorg/radare2](https://github.com/radareorg/radare2)                         | 19.8k     | 开源的逆向工程框架和命令行工具集。                       |
| [rizin-re/rizin](https://github.com/rizin-re/rizin)                               | 2.5k      | radare2 的一个分支，专注于可用性和社区。                 |
| [avast/retdec](https://github.com/avast/retdec)                                   | 8.2k      | 基于 LLVM 的可重定向机器码反编译器。                     |
| [yegord/snowman](https://github.com/yegord/snowman)                               | 1.8k      | 支持 x86, ARM 和 x86-64 的反编译器。                     |
| [aquynh/capstone](https://github.com/aquynh/capstone)                             | 7.4k      | 强大的多架构反汇编框架。                                 |
| [keystone-engine/keystone](https://github.com/keystone-engine/keystone)           | 3.9k      | 轻量级多架构汇编器框架。                                 |
| [unicorn-engine/unicorn](https://github.com/unicorn-engine/unicorn)               | 7.5k      | 基于 QEMU 的多架构 CPU 模拟器框架。                      |
| [lifting-bits/mcsema](https://github.com/lifting-bits/mcsema)                     | 1.7k      | 将 x86/64, aarch64 二进制文件提升到 LLVM IR。            |
| [maji-cat/redress](https://github.com/maji-cat/redress)                           | 680       | 基于 Triton 的二进制反编译器。                           |
| [wtdcode/retdec-idaplugin](https://github.com/wtdcode/retdec-idaplugin)           | 500+      | RetDec 反编译器的 IDA 插件。                             |
| [airbus-seclab/bincat](https://github.com/airbus-seclab/bincat)                   | 1k        | 二进制代码静态分析工具，支持值分析、污点分析和类型推断。 |

### 3. 调试器

| 项目                                                                    | Star 数量 | 描述                                                      |
| ----------------------------------------------------------------------- | --------- | --------------------------------------------------------- |
| [x64dbg/x64dbg](https://github.com/x64dbg/x64dbg)                       | 45.3k     | Windows 平台开源的 x64/x32 调试器。                       |
| [gdb/gdb](https://www.gnu.org/software/gdb/)                            | N/A       | GNU 项目调试器。                                          |
| [radareorg/cutter](https://github.com/radareorg/cutter)                 | 15.6k     | radare2 的 GUI 界面。                                     |
| [hugsy/gef](https://github.com/hugsy/gef)                               | 6.4k      | GDB 的现代化插件，用于漏洞利用和逆向。                    |
| [pwndbg/pwndbg](https://github.com/pwndbg/pwndbg)                       | 6.7k      | GDB 的一个插件，辅助 pwn。                                |
| [longld/peda](https://github.com/longld/peda)                           | 5.7k      | GDB PEDA - Python Exploit Development Assistance for GDB. |
| [voltron/voltron](https://github.com/snare/voltron)                     | 5.3k      | 一个可扩展的、跨平台的调试器 UI 工具包。                  |
| [microsoft/WinDbg-Samples](https://github.com/microsoft/WinDbg-Samples) | 300+      | WinDbg 的示例扩展、脚本和 API 用法。                      |
| [moyix/pdbpp](https://github.com/moyix/pdbpp)                           | 1.4k      | Python 调试器 (pdb) 的一个增强版。                        |
| [deroko/x64dbg-python](https://github.com/deroko/x64dbg-python)         | 300+      | 用于 x64dbg 的 Python 脚本插件。                          |

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
| [s-c-repo/vtable-dumper](https://github.com/s-c-repo/vtable-dumper) | 250       | 用于从 PE/ELF 文件中 dump 虚函数表的工具。                |

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
| [wbenny/xorsearch](https://github.com/wbenny/xorsearch)                             | 450+      | 在文件中搜索经过 XOR, ROL, ROT 或 SHIFT 编码的字符串。 |
| [balena-io/etason](https://github.com/balena-io/etason)                             | 200+      | JSON 解析器，能容忍语法错误。                          |
| [google/santa](https://github.com/google/santa)                                     | 3.1k      | 用于 macOS 的二进制文件白名单/黑名单系统。             |
| [trailofbits/osquery-extensions](https://github.com/trailofbits/osquery-extensions) | 300+      | osquery 的扩展，用于增强安全分析。                     |
| [checkra1n/pongoOS](https://github.com/checkra1n/pongoOS)                           | 1.2k      | checkra1n 使用的 Pre-boot eXecution Environment。      |
| [mitmproxy/mitmproxy](https://github.com/mitmproxy/mitmproxy)                       | 33k+      | 交互式的 HTTPS 代理，用于调试、测试和渗透。            |

### 7. Hex 编辑器

| 项目                                                                  | Star 数量 | 描述                            |
| --------------------------------------------------------------------- | --------- | ------------------------------- |
| [codepainters/distorm](https://github.com/codepainters/distorm)       | 500+      | x86/AMD64 的快速反汇编库。      |
| [radareorg/hex-lib](https://github.com/radareorg/hex-lib)             | 100+      | Hex a go go.                    |
| [WerWolv/ImHex](https://github.com/WerWolv/ImHex)                     | 3k        | 一个功能丰富的现代 Hex 编辑器。 |
| [chrystianvieira/hexcute](https://github.com/chrystianvieira/hexcute) | 100+      | 一个简单的十六进制编辑器。      |

### 8. 脱壳与反混淆

| 项目                                                                  | Star 数量 | 描述                                       |
| --------------------------------------------------------------------- | --------- | ------------------------------------------ |
| [de4dot/de4dot](https://github.com/de4dot/de4dot)                     | 6.5k      | .NET 反混淆器和脱壳器。                    |
| [fireeye/flare-floss](https://github.com/fireeye/flare-floss)         | 1.5k      | 自动从恶意软件中提取混淆后的字符串。       |
| [ioncodes/dnpatch](https://github.com/ioncodes/dnpatch)               | 500+      | 用于修补 .NET 程序集的工具。               |
| [rolfrolles/deobfuscator](https://github.com/rolfrolles/deobfuscator) | 400+      | 基于 QEMU 的 x86 反混淆器。                |
| [hluwa/frida-dexdump](https://github.com/hluwa/frida-dexdump)         | 3k+       | 基于 Frida 的快速 Dex 内存导出工具。       |
| [Perfare/Il2CppDumper](https://github.com/Perfare/Il2CppDumper)       | 7k+       | Unity Il2Cpp 逆向工具，还原 DLL 和头文件。 |

### 9. 固件分析

| 项目                                                                                    | Star 数量 | 描述                                 |
| --------------------------------------------------------------------------------------- | --------- | ------------------------------------ |
| [ReFirmLabs/binwalk](https://github.com/ReFirmLabs/binwalk)                             | 10.1k     | 用于分析、逆向和提取固件镜像的工具。 |
| [craigz/firmwalker](https://github.com/craigz/firmwalker)                               | 1k        | 自动在固件中搜索敏感信息的脚本。     |
| [attify/firmware-analysis-toolkit](https://github.com/attify/firmware-analysis-toolkit) | 1k        | 用于固件安全测试的工具包。           |
| [scriptingx/IoTSecurity101](https://github.com/scriptingx/IoTSecurity101)               | 500+      | 物联网安全入门。                     |

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
| [endgameinc/RSOI](https://github.com/endgameinc/RSOI)                     | 200+      | 逆向工程领域的资源和信息。                 |
| [enaqx/awesome-pentest](https://github.com/enaqx/awesome-pentest)         | 18k+      | 精选的渗透测试资源、工具和其它很棒的东西。 |
| [carpedm20/awesome-hacking](https://github.com/carpedm20/awesome-hacking) | 9k+       | 精选的黑客资源、工具和教程。               |
| [onethawt/idaplugins-list](https://github.com/onethawt/idaplugins-list)   | 1.9k      | IDA Pro 插件列表。                         |
| [Siguza/ios-resources](https://github.com/Siguza/ios-resources)           | 700+      | iOS 黑客相关的有用资源。                   |
| [michalmalik/osx-re-101](https://github.com/michalmalik/osx-re-101)       | 1.4k      | OSX/iOS 逆向资源。                         |

<!-- 05-Appendix/glossary.md -->

# 术语表 (Glossary)

收集了 Android 逆向工程中常见的术语和缩写。

## A

- **ADB (Android Debug Bridge)**: Android 调试桥，一个通用的命令行工具，允许你与模拟器实例或连接的 Android 设备进行通信。
- **AOSP (Android Open Source Project)**: Android 开源项目，即 Android 系统的源代码。
- **APK (Android Package)**: Android 应用程序包，Android 操作系统使用的一种应用程序包文件格式。
- **ART (Android Runtime)**: Android 运行时，Android 5.0 引入的新的应用运行时环境，完全取代了 Dalvik。它使用 AOT (Ahead-Of-Time) 编译技术。
- **ARM**: 一种精简指令集 (RISC) 处理器架构，广泛用于移动设备。

## B

- **Bootloader**: 引导加载程序，在操作系统内核运行之前运行的一段小程序，负责加载操作系统。
- **Baksmali**: 一个将 dex 文件反汇编成 smali 文件的工具。

## D

- **Dalvik**: Google 早期为 Android 设计的虚拟机，使用 JIT (Just-In-Time) 编译。在 Android 5.0 后被 ART 取代。
- **DEX (Dalvik Executable)**: Android 平台的可执行文件格式，包含编译后的代码。
- **Dynamic Analysis (动态分析)**: 在程序运行时对其进行分析的技术，通常涉及调试、Hook 等。

## E

- **ELF (Executable and Linkable Format)**: 可执行与可链接格式，Linux 系统（包括 Android Native 层）使用的标准二进制文件格式。

## F

- **Frida**: 一个动态插桩工具包，允许开发者、逆向工程师和安全研究人员在运行时监视和修改应用程序的行为。

## G

- **Ghidra**: NSA 开源的软件逆向工程 (SRE) 框架。

## H

- **Hooking (挂钩)**: 一种拦截软件组件之间函数调用、消息或事件的技术，用于改变或监视系统的行为。

## I

- **IDA Pro (Interactive DisAssembler)**: 业界标准的交互式反汇编器和调试器。
- **IL2CPP**: Unity 游戏引擎的一种脚本后端，将 C# 代码转换为 C++ 代码，增加了逆向难度。

## J

- **JADX**: 一个将 DEX 文件反编译为 Java 代码的工具。
- **JNI (Java Native Interface)**: Java 本地接口，允许 Java 代码和其他语言（主要是 C/C++）写的代码进行交互。

## M

- **Magisk**: 一个开源的 Android Root 解决方案，以 "Systemless"（不修改系统分区）著称。
- **Manifest (AndroidManifest.xml)**: 每个 Android 应用都必须包含的文件，描述了应用的包名、组件、权限等基本信息。

## N

- **Native Code**: 通常指使用 C/C++ 编写的，直接编译为机器码的代码（相对于 Java/Kotlin 字节码）。
- **NDK (Native Development Kit)**: 一个工具集，允许开发者使用 C 和 C++ 实现应用的一部分。

## O

- **Obfuscation (混淆)**: 使代码难以理解但保持其功能不变的技术，用于保护知识产权或隐藏恶意行为。
- **OLLVM (Obfuscator-LLVM)**: 基于 LLVM 的代码混淆项目，常用于 Native 代码混淆。
- **OAT**: ART 运行时使用的私有 ELF 文件格式，包含 AOT 编译后的机器码。

## R

- **Recovery**: Android 设备的恢复模式，用于恢复出厂设置、刷入更新包等。
- **Rooting**: 获取 Android 设备超级用户 (Root) 权限的过程。
- **Riru**: 一个用于注入 Zygote 进程的模块，常作为其他模块（如 LSPosed）的基础。

## S

- **Smali**: Android 的 Dalvik 字节码的人类可读汇编语言。
- **Static Analysis (静态分析)**: 在不运行程序的情况下对其进行分析的技术。
- **So (Shared Object)**: Linux/Android 下的动态链接库文件，通常由 C/C++ 编写。

## V

- **VMP (Virtual Machine Protection)**: 虚拟机保护，一种高级混淆技术，将原始代码转换为自定义字节码并在自定义解释器中运行。

## X

- **Xposed**: 一个强大的 Android 框架，允许在不修改 APK 的情况下通过模块改变系统和应用的行为。

## Z

- **Zygote**: Android 系统中所有应用进程的父进程。

<!-- 05-Appendix/learning_resources.md -->

---

# 学习资源 (Learning Resources)

本页面收集了 Android 逆向工程领域的高质量学习资源，包括书籍、博客、论坛、社区和课程。

---

## 书籍 (Books)

### 入门与基础

- **《Android 软件安全与逆向分析》** (丰生强 / 非虫)
  经典的入门书籍，涵盖了 Android 系统架构、Smali 语法、静态分析、动态调试等基础知识。
- **《Android 安全攻防实战》** (EaaLaboratory)
  偏向实战，包含很多案例分析。

### 进阶与深入

- **《Android Internals: A Confectioner's Cookbook》** (Jonathan Levin)
  [链接](http://newandroidbook.com/)
  深入剖析 Android 系统内部原理，是理解 Android 底层机制的必读之作。
- **《Android Hacker's Handbook》** (Joshua J. Drake et al.)
  全面介绍 Android 安全架构、漏洞挖掘和利用技术。
- **《MASTG - Mobile App Security Testing Guide》** (OWASP)
  [链接](https://mas.owasp.org/MASTG/)
  OWASP 发布的移动应用安全测试指南，涵盖了 iOS 和 Android 平台的安全测试方法论和技术细节，是行业标准参考文档。

---

## 博客与网站 (Blogs & Websites)

### 个人博客

- **Maddie Stone** ([Project Zero](https://googleprojectzero.blogspot.com/))
  专注于 Android 恶意软件分析和漏洞挖掘，文章质量极高。
- **R0ysue (肉丝)**
  国内知名的 Android 逆向专家，Frida 领域的领军人物。
- **Wei (LSPosed Developer)**
  深入研究 Android Runtime (ART) 和 Hook 技术。
- **Orange Tsai**
  Web 和移动安全领域的知名研究员，常有精彩的利用思路。

### 技术团队与厂商

- **Google Project Zero**
  [链接](https://googleprojectzero.blogspot.com/)
  Google 的安全研究团队，发布了大量关于 Android 内核、驱动和框架层的高质量漏洞分析报告。
- **Quarkslab Blog**
  [链接](https://blog.quarkslab.com/)
  发布了许多关于混淆、反混淆和底层逆向工具（如 Triton）的研究文章。
- **Check Point Research**
  经常披露 Android 恶意软件和高危漏洞。

---

## 论坛与社区 (Forums & Communities)

- **52pojie (吾爱破解)**
  [链接](https://www.52pojie.cn/)
  国内最大的破解和逆向技术交流论坛，拥有丰富的教程、工具和活跃的社区氛围。
- **Kanxue (看雪论坛)**
  [链接](https://bbs.kanxue.com/)
  国内老牌的安全技术社区，专注于二进制安全、漏洞挖掘和内核安全，技术深度较高。
- **XDA Developers**
  [链接](https://forum.xda-developers.com/)
  全球最大的 Android 开发者社区，关于 ROM 定制、Root、Xposed/Magisk 模块的资源非常丰富。
- **Reddit r/ReverseEngineering**
  [链接](https://www.reddit.com/r/ReverseEngineering/)
  国际逆向工程技术讨论区，汇集了全球的逆向爱好者和专家。
- **Reddit r/androiddev**
  [链接](https://www.reddit.com/r/androiddev/)
  虽然侧重开发，但了解开发者的思维对于逆向工程也非常有帮助。

---

## 课程与教程 (Courses & Tutorials)

- **Frida 官方文档与教程**
  [链接](https://frida.re/docs/home/)
  学习 Frida 最权威的资料。
- **Android App Reverse Engineering 101** (Maddie Stone)
  [链接](https://www.r00t0k.com/course/android-app-reverse-engineering-101) (需查找有效链接或存档)
  Workshops 形式的入门教程，非常适合初学者。
- **OWASP Mobile Security Testing Guide (MSTG) Hacking Playground**
  配合 MSTG 书籍的练习环境。

---

## 其他资源

- **Android Open Source Project (AOSP)**
  [链接](https://source.android.com/)
  阅读源码是理解 Android 最根本的方法。使用 [cs.android.com](https://cs.android.com/) 进行在线源码搜索非常方便。
- **Android Developers Documentation**
  [链接](https://developer.android.com/docs)
  官方开发文档，逆向时遇到不懂的 API 首先应该查阅的地方。

---
