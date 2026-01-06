---
title: "快速入门"
date: 2024-03-06
tags: ["入门", "签名验证", "Frida", "DEX", "加密分析", "Hook"]
weight: 1
---

# 快速入门

欢迎！这个指南将帮助你在 **10 分钟内**完成第一次 Android 逆向分析。

---

## 你将学到什么

完成本指南后,你将能够:

- ✅ 在真机/模拟器上运行 Frida
- ✅ Hook 一个 Android 应用的 Java 方法
- ✅ 查看和修改方法的参数与返回值
- ✅ 理解基本的逆向分析流程

**预计用时**: 10-15 分钟

---

## 前置条件

### 必需工具

| 工具           | 说明                                                         |
| -------------- | ------------------------------------------------------------ |
| ☐ Android 设备 | 已 Root 的真机或模拟器(推荐 Genymotion / Android Studio AVD) |
| ☐ ADB          | Android Debug Bridge                                         |
| ☐ Python       | 版本 3.8+                                                    |
| ☐ 测试 App     | 本指南使用系统自带的设置应用                                 |

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

---

## 操作步骤

### 第 1 步: 安装 Frida (2 分钟)

**在电脑上安装 Frida 工具**:

```bash
pip install frida-tools
```

**在 Android 设备上安装 frida-server**:

```bash
# Visit https://github.com/frida/frida/releases
# Download frida-server matching your Python frida version

# View your frida version
frida --version

# View device architecture
adb shell getprop ro.product.cpu.abi
# Common output: arm64-v8a, armeabi-v7a, x86_64
```

```bash
# Decompress and push to device
unzip frida-server-*.zip
adb push frida-server-*-android-* /data/local/tmp/frida-server

# Grant execute permission and run
adb shell "chmod 755 /data/local/tmp/frida-server"
adb shell "/data/local/tmp/frida-server &"
```

**验证安装**:

```bash
frida-ps -U
# Should see output like:
# PID Name
# ---- ---------------
# 1234 com.android.settings
# 5678 com.android.systemui
# ...
```

---

### 第 2 步: 编写第一个 Hook 脚本 (3 分钟)

我们将 Hook Android 设置应用,监控其方法调用。

**创建 Hook 脚本** `first_hook.js`:

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
      console.log("    Tag: " + tag);
      console.log("    Message: " + msg);

      // Call original method
      return this.d(tag, msg);
    };

  console.log("[*] Hook setup completed! Now open Settings app...\n");
});
```

**运行 Hook 脚本**:

```bash
# Method 1: attach to running app
frida -U -n com.android.settings -l first_hook.js

# Method 2: inject at app startup
frida -U -f com.android.settings -l first_hook.js --no-pause
```

**预期输出**:

```text
[+] Captured LogCall:
    Tag: SettingsActivity
    Message: onCreate called

[+] Captured LogCall:
    Tag: SettingsFragment
    Message: Loading preferences...
```

✅ **如果看到类似上方的日志输出，恭喜你已经成功 Hook 了一个 Android 应用!**

---

### 第 3 步: 修改应用行为 (3 分钟)

现在让我们做点更有趣的 —— **修改应用的返回值**。

**创建脚本** `modify_behavior.js`:

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
      console.log(
        "    Original: '" + this + "' == '" + other + "' => " + result
      );
      console.log("    Modified: true\n");
      return true; // return true
    }

    return result;
  };

  console.log(
    "[*] Hook completed! All 'WiFi' String comparison will return true\n"
  );
});
```

**运行脚本**:

```bash
frida -U -f com.android.settings -l modify_behavior.js --no-pause
```

**你可以用同样的方法**:

- 修改加密参数
- 绕过签名验证
- 篡改网络请求

---

## 恭喜你，现在你已完成快速入门

### 学会了什么？

- ✅ 安装和运行 Frida
- ✅ 编写基本的 Hook 脚本
- ✅ 监控方法调用
- ✅ 修改方法返回值

### 下一步学习

根据你的兴趣选择:

#### **深入学习工具**

- [Frida 完整指南](../02-Tools/Dynamic/frida_guide/) - 学习 Frida 的所有 API
- [Frida 内部原理](../02-Tools/Dynamic/frida_internals/) - 理解 Frida 如何工作
- [ADB 命令速查](../02-Tools/Cheatsheets/adb_cheatsheet/) - 掌握 ADB 常用命令

#### **解决具体问题**

**场景 1: 抓包分析**
→ [网络抓包](../01-Recipes/Network/network_sniffing/)

**场景 2: 绕过反调试**
→ [反调试绕过](../01-Recipes/Anti-Detection/frida_anti_debugging/)

**场景 3: 分析加密算法**
→ [密码学分析](../01-Recipes/Network/crypto_analysis/)

**场景 4: 脱壳加固 App**
→ [应用脱壳](../01-Recipes/Unpacking/un-packing/)

#### **实战案例**

- [音乐 App 分析](../03-Case-Studies/case_music_apps/) - VIP 破解、音频解密
- [社交 App 风控](../03-Case-Studies/case_social_media_and_anti_bot/) - API 签名、设备指纹

#### **理解基础原理**

- [APK 文件结构](../04-Reference/Foundations/apk_structure/)
- [Android 四大组件](../04-Reference/Foundations/android_components/)
- [DEX 文件格式](../04-Reference/Foundations/dex_format/)

---

## 💡 常见问题

### Q: Frida 连接不上设备?

```bash
# 1. Confirm frida-server is running
adb shell "ps | grep frida"

# 2. Reboot frida-server
adb shell "pkill frida-server"
adb shell "/data/local/tmp/frida-server &"

# 3. Check port forwarding (if needed)
adb forward tcp:27042 tcp:27042
```

### Q: Hook 不生效?

**排查步骤**:

1. **确认应用正在运行**:
   ```bash
   frida-ps -U | grep YourAppPackageName
   ```
2. **检查类名是否正确**:
   - 使用 jadx-gui 反编译查看准确的类名
   - 注意内部类的 `$` 符号(如 `OuterClass$InnerClass`)
3. **处理方法重载**:
   ```javascript
   // If method has multiple overloads, need to specify parameter class type
   YourClass.yourMethod.overload("java.lang.String").implementation = function (
     arg
   ) {
     // your code here
   };
   ```

### Q: 应用检测到 Frida?

→ 查看 [Frida 反调试绕过](../01-Recipes/Anti-Detection/frida_anti_debugging/)

---

## 更多资源

| 项目                   | 说明                                                             |
| ---------------------- | ---------------------------------------------------------------- |
| **Frida 官方文档**     | https://frida.re/docs/                                           |
| **Frida CodeShare**    | https://codeshare.frida.re/ (社区脚本)                           |
| **本 Cookbook 脚本库** | [Frida 脚本示例](../01-Recipes/Scripts/frida_script_examples/) |

---

**准备好开始你的逆向之旅吧!**
