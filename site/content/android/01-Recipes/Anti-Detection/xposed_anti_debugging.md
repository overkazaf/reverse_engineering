---
title: "绕过应用的 Xposed 检测"
date: 2025-02-23
tags: ["Native层", "签名验证", "SSL Pinning", "Frida", "DEX", "Hook"]
weight: 10
---

# 绕过应用的 Xposed 检测

> **📚 前置知识**
>
> 本配方涉及以下核心技术，建议先阅读相关章节：
>
> - **[Xposed 框架指南](../../02-Tools/Dynamic/xposed_guide.md)** - 理解 Xposed Hook 原理
> - **[Magisk 环境配置](../../02-Tools/Environment/magisk_guide.md)** - Root 环境与模块管理

## 问题场景

你可能遇到以下情况：

1. **App 启动即退出**：App 启动后弹出"检测到 Xposed 框架，禁止运行"，随即闪退
2. **功能受限**：金融/支付类 App 检测到 Xposed 后拒绝提供服务（无法转账、支付）
3. **账号封禁**：游戏检测到 Xposed 环境后触发风控，导致封号
4. **分析受阻**：需要在 Xposed 环境下分析 App 行为，但被反调试拦截
5. **通用方案失效**：已经使用 RootCloak Plus 等通用隐藏模块，但仍被检测到

## 工具清单

### 必需工具

- **Xposed 框架**：EdXposed 或 LSPosed（推荐 LSPosed，更稳定）
- **Root 设备**：已 Root 的 Android 设备或模拟器（如 Genymotion）
- **目标 APK**：需要绕过检测的应用安装包
- **Xposed 模块开发环境**：Android Studio（用于编写自定义绕过模块）

### 可选工具

- **JEB/Jadx**：反编译工具，用于分析 App 的检测代码
- **RootCloak Plus**：通用 Xposed/Root 隐藏模块（快速测试）
- **Hide My Applist**：高级应用列表和框架隐藏工具
- **MT Manager**：Android 文件管理器，查看系统文件
- **Xposed 源码**：EdXposed 源码（定制化框架需求）

## 前置条件

开始之前，请确认：

- **已安装 Xposed 框架**：设备上已刷入 EdXposed 或 LSPosed，并能正常使用
- **设备已 Root**：拥有 Root 权限，或使用虚拟化方案（如 VirtualXposed）
- **能反编译 APK**：会使用 Jadx/JEB 查看 Java 代码
- **了解 Xposed Hook 基础**：知道如何编写简单的 Xposed 模块（可参考 [Xposed Guide](../../02-Tools/Dynamic/xposed_guide.md)）
- **了解 Java 反射机制**：理解 `Class.forName()`, `ClassLoader` 等概念

## 解决方案

### 第 1 步：识别检测类型（15-30 分钟）

首先需要确定 App 使用了哪种检测方法，这决定了后续的绕过策略。

#### 方法 1：观察运行行为

运行目标 App，观察异常行为的时机和特征：

| 异常时机                       | 可能的检测类型                        |
| ------------------------------ | ------------------------------------- |
| **启动阶段立即崩溃/退出**      | 调用栈检测（Application.onCreate 中） |
| **特定功能（登录、支付）受限** | 关键方法处的定点检测                  |
| **延迟几秒后弹出警告**         | 定时器或异步线程中的检测              |
| **随机触发**                   | 多点分散检测或混淆后的检测            |

#### 方法 2：静态分析检测代码

使用 Jadx 反编译 APK，搜索 Xposed 检测的特征字符串：

```bash
# 反编译 APK
jadx -d ./decompiled target.apk

# 搜索 Xposed 相关特征
cd decompiled
grep -r "xposed" --include="*.java" .
grep -r "XposedBridge" --include="*.java" .
grep -r "de.robv.android" --include="*.java" .

# 搜索检测方法调用
grep -r "getStackTrace" --include="*.java" .
grep -r "Class.forName" --include="*.java" .
grep -r "/proc/self/maps" --include="*.java" .
```

**常见检测代码模式**：

**调用栈检测**：

```java
// 特征代码
try {
    throw new Exception("Xposed Detection");
} catch (Exception e) {
    for (StackTraceElement element : e.getStackTrace()) {
        if (element.getClassName().contains("de.robv.android.xposed")) {
            // Xposed 检测到!
            return true;
        }
    }
}
```

**类加载检测**：

```java
try {
    Class.forName("de.robv.android.xposed.XposedBridge");
    // 如果没抛异常，说明 Xposed 存在
    return true;
} catch (ClassNotFoundException e) {
    return false;
}
```

**文件系统检测**：

```java
File xposedJar = new File("/system/framework/XposedBridge.jar");
if (xposedJar.exists()) {
    // Xposed 检测到!
}
```

**Native 层检测**：

```c
// maps 文件检测
FILE* fp = fopen("/proc/self/maps", "r");
// 读取内容并查找 "libxposed_art.so" 或 "XposedBridge"

// 符号地址检测
void* handle = dlopen("libart.so", RTLD_NOW);
void* sym = dlsym(handle, "_ZN3art9ArtMethod6InvokeEPNS_6ThreadEPjjPNS_6JValueEPKc");
// 检查地址是否在非标准内存区域
```

#### 方法 3：选择绕过策略

根据检测类型选择合适的策略：

| 检测类型 | 推荐策略 | 成功率 | 耗时 |
|---------|---------|-------|------|
| Java 层调用栈检测 | Hook `StackTraceElement.getClassName()` | 90% | 30min |
| Java 层类加载检测 | Hook `Class.forName()` | 85% | 20min |
| 文件系统检测 | Hook `File.exists()` | 95% | 20min |
| Native 层 maps 检测 | Hook `fopen()` / 定制框架 | 60% | 2-4h |
| 综合检测（多种方法） | 定制化 Xposed 框架 | 80% | 4h+ |

**决策树**：

```text
检测类型已知？
├─ 是 → 策略 A：编写针对性 Hook 模块
└─ 否 → 快速测试需求或不想写代码
         └─→ 策略 B：使用现成隐藏模块（最快）
```

### 第 2 步：策略 A - 编写自定义绕过模块

创建 `AntiXposedDetection.java`：

```java
package com.example.antidetect;

import android.os.Bundle;
import de.robv.android.xposed.*;
import de.robv.android.xposed.callbacks.XC_LoadPackage.LoadPackageParam;
import java.io.File;

public class AntiXposedDetection implements IXposedHookLoadPackage {

    // 修改为你的目标 App 包名
    private static final String TARGET_PACKAGE = "com.target.app";

    @Override
    public void handleLoadPackage(LoadPackageParam lpparam) throws Throwable {
        // 只 Hook 目标 App
        if (!lpparam.packageName.equals(TARGET_PACKAGE)) return;

        XposedBridge.log("[AntiDetect] 开始 Hook " + TARGET_PACKAGE);

        // 绕过调用栈检测
        hookStackTrace();

        // 绕过类加载检测
        hookClassForName();

        // 绕过文件系统检测
        hookFileExists();

        // 绕过系统属性检测
        hookSystemProperties();

        XposedBridge.log("[AntiDetect] 所有 Hook 已激活");
    }

    /**
     * 绕过调用栈检测
     * 原理：修改 StackTraceElement.getClassName() 返回值
     */
    private void hookStackTrace() {
        XposedHelpers.findAndHookMethod(
            StackTraceElement.class,
            "getClassName",
            new XC_MethodHook() {
                @Override
                protected void afterHookedMethod(MethodHookParam param) throws Throwable {
                    String originalClassName = (String) param.getResult();

                    // 如果类名包含 xposed 特征，替换为无害系统类
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
     * 绕过类加载检测
     * 原理：拦截 Class.forName() 调用，对 Xposed 类抛出 ClassNotFoundException
     */
    private void hookClassForName() {
        XposedHelpers.findAndHookMethod(
            Class.class,
            "forName",
            String.class,
            new XC_MethodHook() {
                @Override
                protected void beforeHookedMethod(MethodHookParam param) throws Throwable {
                    String className = (String) param.args[0];

                    // 如果尝试加载 Xposed 相关类，抛出 ClassNotFoundException
                    if (className != null &&
                        (className.contains("xposed") ||
                         className.contains("Xposed") ||
                         className.contains("EdXposed") ||
                         className.contains("LSPosed"))) {
                        param.setThrowable(new ClassNotFoundException(className));
                        XposedBridge.log("[AntiDetect] 阻止加载类: " + className);
                    }
                }
            }
        );

        // 也拦截三参数版本 forName
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
     * 绕过文件系统检测
     * 原理：修改 File.exists() 返回值，隐藏 Xposed 特征文件
     */
    private void hookFileExists() {
        XposedHelpers.findAndHookMethod(
            File.class,
            "exists",
            new XC_MethodHook() {
                @Override
                protected void afterHookedMethod(MethodHookParam param) throws Throwable {
                    File file = (File) param.thisObject;
                    String path = file.getAbsolutePath();

                    // Xposed 特征文件列表
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

                    // 检查路径是否包含特征
                    for (String keyword : xposedPaths) {
                        if (path.contains(keyword)) {
                            param.setResult(false); // 伪装文件不存在
                            XposedBridge.log("[AntiDetect] 隐藏文件: " + path);
                            return;
                        }
                    }
                }
            }
        );
    }

    /**
     * 绕过系统属性检测
     * 原理：拦截 System.getProperty() 调用
     */
    private void hookSystemProperties() {
        XposedHelpers.findAndHookMethod(
            System.class,
            "getProperty",
            String.class,
            new XC_MethodHook() {
                @Override
                protected void afterHookedMethod(MethodHookParam param) throws Throwable {
                    String key = (String) param.args[0];

                    // VirtualXposed 等会设置特殊属性
                    if (key != null &&
                        (key.contains("xposed") ||
                         key.contains("vxp") ||
                         key.equals("ro.build.version.xposed"))) {
                        param.setResult(null); // 返回 null
                        XposedBridge.log("[AntiDetect] 隐藏系统属性: " + key);
                    }
                }
            }
        );
    }
}
```

**项目结构**：

```text
AntiXposedDetection/
├── app/
│   └── src/main/
│       ├── AndroidManifest.xml
│       ├── assets/
│       │   └── xposed_init  # 入口类声明
│       └── java/com/example/antidetect/
│           └── AntiXposedDetection.java
│   └── build.gradle
└── build.gradle
```

**AndroidManifest.xml**：

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.antidetect">

    <application
        android:allowBackup="true"
        android:label="Anti Xposed Detection"
        android:icon="@mipmap/ic_launcher">

        <!-- Xposed 模块声明 -->
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

**编译和安装**：

```bash
# 1. 编译模块
./gradlew assembleRelease

# 2. 安装到设备
adb install app/build/outputs/apk/release/app-release.apk

# 3. 在 LSPosed/EdXposed 中激活模块
# - 打开 LSPosed Manager
# - 模块 → 找到 "Anti Xposed 检测"
# - 勾选启用，并在作用域中添加目标 App
# - 重启目标 App

# 4. 查看日志验证
adb logcat -s Xposed:V | grep AntiDetect
```

### 第 3 步：策略 B - 使用现成隐藏模块

1. **Hide My Applist**（最强大，推荐）
   - 下载：[GitHub](https://github.com/Dr-TSNG/Hide-My-Applist)
   - 功能：隐藏应用列表、Xposed 框架、Root
   - 支持黑白名单、模板系统

2. **XposedChecker Bypass**
   - 专门针对 XposedChecker 这类检测工具
   - 覆盖常见检测点

3. **RootCloak Plus**（老牌模块）
   - 同时隐藏 Root 和 Xposed
   - 配置简单，但对新型检测效果较差

**使用步骤（以 Hide My Applist 为例）**：

```bash
# 1. 下载并安装
# 从 GitHub 发布页下载最新 APK
adb install HideMyApplist.apk

# 2. 在 LSPosed 中激活
# LSPosed 管理器 → 模块 → Hide My Applist → 勾选启用

# 3. 配置隐藏规则
# 打开 Hide My Applist App
# → 模板管理 → 新建模板
# → 选择隐藏内容：
#   黑名单模式（隐藏 Xposed 相关）
#   隐藏 Xposed 模块
#   隐藏系统框架
# → 应用管理 → 选择目标 App → 应用模板

# 4. 重启目标 App
adb shell am force-stop com.target.app
adb shell am start -n com.target.app/.MainActivity
```

### 第 4 步：策略 C - 定制 Xposed 框架

当 Hook 绕过无效时，可能需要从源码层面修改 Xposed 特征。

**修改目标**：

- 包名：`de.robv.android.xposed` → `com.myfw.custom`
- 类名：`XposedBridge` → `CustomBridge`
- 文件名：`libxposed_art.so` → `libcustom_art.so`
- 系统属性：`persist.xposed.*` → `persist.myfw.*`

**详细步骤**：

**1. 获取 Xposed 源码**：

```bash
# 克隆 EdXposed 源码（推荐，比原版 Xposed 更活跃）
git clone --recursive https://github.com/ElderDrivers/EdXposed
cd EdXposed

# 也可以克隆 LSPosed（更现代实现）
git clone --recursive https://github.com/LSPosed/LSPosed
```

**2. 修改特征字符串**（创建脚本 `rename_xposed.sh`）：

```bash
#!/bin/bash

# 全局替换 Xposed 特征为自定义名称
OLD_PACKAGE="de.robv.android.xposed"
NEW_PACKAGE="com.myframework.custom"

OLD_CLASS="Xposed"
NEW_CLASS="Custom"

OLD_LIB="xposed"
NEW_LIB="myfw"

echo "开始替换 Xposed 特征..."

# 1. 替换包名
echo "替换包名..."
find . -type f \( -name "*.java" -o -name "*.cpp" -o -name "*.h" \) \
    -exec sed -i "s/$OLD_PACKAGE/$NEW_PACKAGE/g" {} +

# 2. 替换类名
echo "替换类名..."
find . -type f -name "*.java" \
    -exec sed -i "s/${OLD_CLASS}Bridge/${NEW_CLASS}Bridge/g" {} +
find . -type f -name "*.java" \
    -exec sed -i "s/${OLD_CLASS}Helpers/${NEW_CLASS}Helpers/g" {} +

# 3. 重命名文件
echo "重命名文件..."
find . -name "*Xposed*" | while read file; do
    newfile=$(echo "$file" | sed "s/Xposed/Custom/g")
    mv "$file" "$newfile" 2>/dev/null
done

# 4. 替换库文件名
echo "替换 Native 库名..."
find . -type f \( -name "*.cpp" -o -name "*.mk" -o -name "CMakeLists.txt" \) \
    -exec sed -i "s/lib${OLD_LIB}/lib${NEW_LIB}/g" {} +

# 5. 替换系统属性名
echo "替换系统属性..."
find . -type f \( -name "*.cpp" -o -name "*.java" \) \
    -exec sed -i "s/persist.xposed/persist.myfw/g" {} + \
    -exec sed -i "s/ro.xposed/ro.myfw/g" {} +

echo "特征替换完成！"
echo "请手动检查以下文件是否正确："
echo "  - AndroidManifest.xml"
echo "  - module.prop (Magisk 模块配置)"
echo "  - build.gradle"
```

**3. 修改 module.prop**（Magisk 模块配置）：

```properties
id=custom_xposed
name=Custom Framework (Xposed)
version=v1.0.0
versionCode=1
author=YourName
description=Customized Xposed Framework with renamed signatures
minMagisk=21000
```

**4. 编译定制版框架**：

```bash
# 执行替换
./rename_xposed.sh

# 编译（以 EdXposed 为例）
cd EdXposed
./gradlew :edxp-core:buildAll

# 输出位于 out/edxp-core/release/
# 获取一个 .zip 文件，可在 Magisk 中刷入
```

**5. 安装定制版框架**：

```bash
# 方法 1：通过 Magisk 管理器安装
# 打开 Magisk 管理器 → 模块 → 从本地安装 → 选择 ZIP

# 方法 2：通过 TWRP Recovery 刷入（如有）
# adb reboot recovery
# 在 TWRP 中选择 Install → 选择 ZIP → 滑动确认

# 重启设备
adb reboot
```

### 第 5 步：验证绕过效果

**验证清单**：

- **目标 App 正常运行**：不再弹出检测警告，不闪退
- **Xposed Hook 依然生效**：你的 Hook 模块能正常 Hook 目标方法
- **检测工具显示干净**：使用 XposedChecker 等工具测试，显示未检测到

**验证方法**：

**1. 编写测试 Xposed 模块**：

```java
// 验证拦截是否生效
XposedHelpers.findAndHookMethod(
    "com.target.app.MainActivity",
    lpparam.classLoader,
    "onCreate",
    Bundle.class,
    new XC_MethodHook() {
        @Override
        protected void afterHookedMethod(MethodHookParam param) throws Throwable {
            XposedBridge.log("Hook 成功！App 未检测到 Xposed");
        }
    }
);
```

**2. 查看日志**：

```bash
# 查看 App 是否有检测相关日志
adb logcat | grep -i "xposed\|detect\|security\|check"

# 应该看到：
# - Hook 成功日志
# - 没有检测相关错误日志
```

**3. 使用 XposedChecker**：

```bash
# 安装 XposedChecker
adb install XposedChecker.apk

# 运行并查看结果
# 如果绕过成功，应该显示 "Xposed: Not Detected"
```

**4. 测试目标 App 功能**：

```text
完整功能测试流程：
├─→ 启动 App（观察是否崩溃）
├─→ 登录账号（观察是否被拒绝）
└─→ 测试核心业务（支付/游戏/查看敏感信息）
    └─→ 观察是否触发风控或异常
```

---

## 原理解析

### Xposed 检测原理

**1. 调用栈特征**：

当 Xposed Hook 一个方法时，实际的调用链是：

```text
App.targetMethod()
    ↓
XposedBridge.handleHookedMethod()
    ↓
原始方法/替换方法
```

App 可以通过 `Thread.currentThread().getStackTrace()` 获取调用栈，如果发现 `de.robv.android.xposed` 相关类，就说明 Xposed 存在。

**2. 类加载特征**：

Xposed 在 Zygote 进程中注入，会加载 `XposedBridge` 等类到每个 App 进程。App 可以尝试 `Class.forName("de.robv.android.xposed.XposedBridge")`，如果成功加载，就说明 Xposed 存在。

**3. 文件系统特征**：

Xposed 需要在系统中安装文件：

- `/system/framework/XposedBridge.jar`
- `/system/lib/libxposed_art.so` 或 `/system/lib64/libxposed_art.so`

**4. 内存映射特征**：

进程的内存映射（`/proc/self/maps`）中会出现 Xposed 相关的库。

### 绕过原理

关键技术点：

1. **拦截检测方法的执行**：在检测代码执行前 Hook，修改其行为
2. **修改返回值**：让检测方法总是返回"未检测到"的结果
3. **过滤特征字符串**：将包含 "xposed" 的字符串替换为无害字符串
4. **阻止异常抛出**：对于 `Class.forName()` 这类检测，主动抛出 `ClassNotFoundException`

**示例：调用栈检测的绕过原理**

```text
Hook 前（检测成功）：
App 调用 getStackTrace()
    → 返回 [MainActivity, XposedBridge, ZygoteInit, ...]
    → App 发现 "XposedBridge"
    → 检测成功（Xposed 存在）

Hook 后（绕过检测）：
App 调用 getStackTrace()
    → 返回 [MainActivity, XposedBridge, ZygoteInit, ...]
    → 我们 Hook 拦截 getClassName()
    → 将 "XposedBridge" 替换为 "ZygoteInit"
    → App 只看到 [MainActivity, ZygoteInit, ZygoteInit, ...]
    → 检测失败（未发现 Xposed）
```

### 定制框架效果

| 检测方式 | 检测代码 | 定制后 | 结果 |
|---------|---------|--------|------|
| 类加载检测 | `Class.forName("de.robv...XposedBridge")` | 包名改为 `com.myfw...CustomBridge` | 检测失败 |
| 文件检测 | `/system/framework/XposedBridge.jar` | 文件名改为 `CustomBridge.jar` | 检测失败 |
| maps 检测 | 搜索 `libxposed_art.so` | 库名改为 `libcustom_art.so` | 检测失败 |

**缺点**：

- 维护成本高，需要跟随官方 Xposed 更新
- 编译过程复杂，需要配置 Android NDK
- 部分依赖原版 Xposed API 的模块可能不兼容

---

## 常见问题

### 问题 1：Hook 模块激活后，App 仍然检测到 Xposed

**可能原因**：

1. **Hook 时机太晚**：App 在 `Application.onCreate()` 之前就检测了
2. **Native 层检测**：App 使用 JNI 检测，Java Hook 无法拦截
3. **遗漏的检测点**：App 使用了你没有覆盖的检测方法
4. **Hook 作用域未配置**：LSPosed 中未将目标 App 加入作用域

**解决方案**：

**方案 1：提前 Hook 时机**

```java
// 在 Application.attachBaseContext() 中提前拦截
XposedHelpers.findAndHookMethod(
    "com.target.app.MyApplication",
    lpparam.classLoader,
    "attachBaseContext",
    Context.class,
    new XC_MethodHook() {
        @Override
        protected void beforeHookedMethod(MethodHookParam param) throws Throwable {
            // 在 Application 初始化前就拦截所有检测方法
            hookAllDetectionMethods(lpparam);
            XposedBridge.log("[AntiDetect] Early hooks installed");
        }
    }
);
```

**方案 2：结合 Frida 处理 Native 层**

```javascript
// Frida Script：Hook fopen() 拦截 maps 文件读取
Interceptor.attach(Module.findExportByName("libc.so", "fopen"), {
    onEnter: function(args) {
        var path = Memory.readUtf8String(args[0]);
        if (path === "/proc/self/maps") {
            console.log("[*] fopen() called for /proc/self/maps");
            // 重定向到一个干净的 maps 文件
            args[0] = Memory.allocUtf8String("/data/local/tmp/fake_maps");
        }
    }
});
```

**方案 3：使用 Xposed 调用 Native Hook**

```java
// 调用 native 方法做 inline hook
nativeHookFopen();
```

**方案 4：全面分析检测代码**

```bash
cd decompiled

# 搜索所有可能检测模式
grep -rn "getStackTrace\|forName\|/proc/self/maps\|XposedBridge\|exists()" . \
    --include="*.java" > detection_points.txt
```

**方案 5：检查 LSPosed 作用域**

```bash
adb shell "su -c 'ls /data/adb/lspd/config/modules/'"
# 应该看到你的模块 ID

# 检查作用域配置
# LSPosed 管理器 → 模块 → 你的模块 → 应用作用域
# 确保目标 App 已勾选
```

### 问题 2：定制框架编译失败

**可能原因**：

- META-INF 目录下的脚本缺失
- 编译过程中出错，生成的 ZIP 损坏

**解决方案**：

**方案 1：检查 ZIP 结构**

```bash
# 解压查看结构
unzip -l edxp-custom.zip

# 标准 Magisk 模块结构：
# META-INF/
#   com/google/android/
#     update-binary      # 安装脚本
#     updater-script     # 空文件即可
# module.prop            # 模块配置
# system/                # 系统文件
#   framework/
#     CustomBridge.jar
#   lib64/
#     libcustom_art.so
# riru/                  # Riru 相关（如使用 Riru）
```

**方案 2：手动创建 module.prop**

```properties
id=custom_xposed
name=Custom Xposed Framework
version=v1.0.0
versionCode=100
author=YourName
description=Customized Xposed with renamed signatures

# 可选字段
minMagisk=21000
maxMagisk=99999
```

**方案 3：手动打包**

```bash
mkdir -p magisk_module/system/framework
mkdir -p magisk_module/system/lib64

# 复制文件
cp update-binary magisk_module/META-INF/com/google/android/
touch magisk_module/META-INF/com/google/android/updater-script
cp module.prop magisk_module/
cp CustomBridge.jar magisk_module/system/framework/
cp libcustom_art.so magisk_module/system/lib64/

# 打包（注意：必须在模块目录内打包）
cd magisk_module
zip -r ../custom-xposed-magisk.zip .
cd ..

# 推送并安装
adb push custom-xposed-magisk.zip /sdcard/
# 在 Magisk Manager 中安装
```

**方案 4：使用 TWRP 刷入**

```bash
adb reboot recovery
# 在 TWRP 中：Install → 选择 ZIP → 滑动确认
```

### 问题 3：Hook 后 App 功能异常或崩溃

**可能原因**：

- Hook 范围太广，影响了正常功能
- 返回值类型不匹配
- Hook 的方法签名不正确

**解决方案**：

**方案 1：精准 Hook，缩小作用范围**

错误示范：全局 Hook

```java
// 这样会影响所有类加载，包括正常业务
XposedHelpers.findAndHookMethod(Class.class, "forName", String.class, ...);
```

正确示范：针对性 Hook

```java
// 只 Hook 已知的检测类
XposedHelpers.findAndHookMethod(
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

**方案 2：添加条件判断**

```java
@Override
protected void afterHookedMethod(MethodHookParam param) throws Throwable {
    String className = (String) param.getResult();

    // 只过滤 Xposed 相关，不影响其他类
    if (className != null && className.toLowerCase().contains("xposed")) {
        param.setResult("android.app.Activity");
    }
    // 其他情况保持原样，不做修改
}
```

**方案 3：逐个启用 Hook 测试**

```java
@Override
public void handleLoadPackage(LoadPackageParam lpparam) throws Throwable {
    // 一次只启用一个拦截，测试是否导致崩溃
    hookStackTrace(); // 测试：OK
    // hookClassForName(); // 暂时注释掉
    // hookFileExists(); // 暂时注释掉

    // 逐个启用并测试，找出导致崩溃的拦截
}
```

**方案 4：确保返回值类型正确**

```java
// 确保返回值类型匹配
@Override
protected void afterHookedMethod(MethodHookParam param) {
    // 如果原方法返回 boolean，你也必须返回 boolean
    param.setResult(false); // 正确
    // param.setResult("false"); // 错误！类型不匹配
}
```

### 问题 4：模块在 LSPosed 中不显示

**可能原因**：

- `assets/xposed_init` 文件缺失或路径错误
- `AndroidManifest.xml` 中缺少 Xposed 元数据声明
- 模块入口类的包名/类名与 `xposed_init` 中不一致
- LSPosed 缓存未刷新

**解决方案**：

**方案 1：检查 `assets/xposed_init` 文件**

```bash
# 确认文件存在
unzip -l app-release.apk | grep xposed_init
# 应该看到: assets/xposed_init

# 检查内容（必须是完整类名，无文件扩展名）
unzip -p app-release.apk assets/xposed_init
# 输出应该是：com.example.antidetect.AntiXposedDetection
```

**方案 2：确认文件路径正确**

```text
正确路径：
app/src/main/assets/xposed_init  # 正确

错误路径：
app/assets/xposed_init           # 错误
```

**方案 3：检查 AndroidManifest.xml**

```xml
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

**方案 4：确认入口类存在**

```bash
# 检查入口类是否存在
ls -l ./decompiled/com/example/antidetect/AntiXposedDetection.java

# 确认类实现了 IXposedHookLoadPackage 接口
grep "implements IXposedHookLoadPackage" \
    ./decompiled/com/example/antidetect/AntiXposedDetection.java
```

**方案 5：刷新 LSPosed 缓存**

```bash
# 清除 LSPosed 缓存
adb shell "su -c 'rm -rf /data/adb/lspd/cache/*'"

# 重新安装
adb install app-release.apk

# 重启 LSPosed（或重启设备）
adb shell "su -c 'killall -9 com.android.systemui'"
# 或
adb reboot

# 打开 LSPosed 管理器，应该能看到模块
```

---

## 延伸阅读

### 相关配方

- [逆向工程工作流](../Analysis/re_workflow.md) - 完整的逆向分析流程

### 工具深入

- [Xposed 使用指南](../../02-Tools/Dynamic/xposed_guide.md) - Xposed 框架基础使用
- [Xposed 内部原理](../../02-Tools/Dynamic/xposed_internals.md) - Xposed 工作机制详解
- [Frida 使用指南](../../02-Tools/Dynamic/frida_guide.md) - Frida 与 Xposed 协同使用

### 参考资料

- [Android 沙箱实现](../../04-Reference/Advanced/android_sandbox_implementation.md) - 虚拟化环境中使用 Xposed
- [ART 运行时](../../04-Reference/Foundations/art_runtime.md) - 理解 Xposed 如何修改 ART

### 案例分析

- [反分析技术案例](../../03-Case-Studies/case_anti_analysis_techniques.md) - 综合反分析技术案例
- [社交媒体风控](../../03-Case-Studies/case_social_media_and_anti_bot.md) - 社交应用的 Xposed 检测

---

## 快速参考

### Xposed 检测方法速查表

| 检测类型     | 检测层级    | 特征代码                                            | 绕过方法                    | Hook 目标                          |
| ------------ | ----------- | --------------------------------------------------- | --------------------------- | ---------------------------------- |
| 调用栈检测   | Java        | `getStackTrace()` + `contains("xposed")`            | Hook 返回值过滤             | `StackTraceElement.getClassName()` |
| 类加载检测   | Java        | `Class.forName("XposedBridge")`                     | 抛出 ClassNotFoundException | `Class.forName()`                  |
| 已加载类检测 | Java        | `ClassLoader.loadClass(...)`                        | 同上                        | `ClassLoader.loadClass()`          |
| 文件检测     | Java        | `new File("/system/.../XposedBridge.jar").exists()` | 返回 false                  | `File.exists()`                    |
| maps 检测    | Native      | `fopen("/proc/self/maps")` + `strstr("libxposed")`  | Hook fopen 或定制框架       | `libc.fopen()`                     |
| 系统属性检测 | Java/Native | `System.getProperty("vxp_...")`                     | 返回 null                   | `System.getProperty()`             |
| 符号地址检测 | Native      | `dlsym(...)` 检查地址异常                           | 定制框架                    | N/A（需源码修改）                  |

### 完整绕过模块模板（一键使用）

保存为 `AntiXposedBypass.java`，修改包名和目标 App 即可使用：

```java
package com.example.antidetect;

import de.robv.android.xposed.*;
import de.robv.android.xposed.callbacks.XC_LoadPackage.LoadPackageParam;
import java.io.File;

public class AntiXposedBypass implements IXposedHookLoadPackage {

    private static final String TARGET = "com.target.app"; // 改为你的目标 App

    @Override
    public void handleLoadPackage(LoadPackageParam lpparam) throws Throwable {
        if (!lpparam.packageName.equals(TARGET)) return;

        XposedBridge.log("[Bypass] Hooking " + TARGET);

        // 1. 绕过调用栈检测
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

        // 2. 绕过类加载检测
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

        // 3. 绕过文件检测
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

### 常用命令速查

```bash
# ========== 环境检查 ==========

# 检查 Xposed 框架状态
adb shell "su -c 'ls -l /system/framework/Xposed'"
adb shell "su -c 'ps -A | grep xposed'"

# 查看已安装的 Xposed 模块
adb shell "su -c 'ls /data/app/ | grep -i xposed'"

# 检查 LSPosed 状态
adb shell "su -c 'ls -l /data/adb/lspd/'"

# ========== 日志调试 ==========

# 查看 Xposed 框架日志
adb logcat -s Xposed:V

# 查看模块日志（假设模块标签为 AntiDetect）
adb logcat | grep AntiDetect

# 查看 App 检测相关日志
adb logcat | grep -iE "detect|xposed|security|check"

# 清空日志并实时查看
adb logcat -c && adb logcat -v time

# ========== 模块管理 ==========

# 编译 Xposed 模块
./gradlew assembleDebug   # Debug 版
./gradlew assembleRelease # Release 版

# 安装模块
adb install app/build/outputs/apk/debug/app-debug.apk

# 卸载模块
adb uninstall com.example.antidetect

# 重启目标 App（应用更改）
adb shell am force-stop com.target.app
adb shell am start -n com.target.app/.MainActivity

# ========== 定制框架 ==========

# 推送自定义框架到设备
adb push EdXposed-custom.zip /sdcard/

# 在 Magisk 中安装（命令行方式）
adb shell "su -c 'magisk --install-module /sdcard/EdXposed-custom.zip'"

# 重启设备
adb reboot

# ========== 测试验证 ==========

# 安装 XposedChecker 测试工具
adb install XposedChecker.apk

# 运行目标 App 并观察行为
adb shell am start -n com.target.app/.MainActivity

# 抓取崩溃日志
adb logcat -b crash

# 检查进程内存映射（查找 Xposed 特征）
adb shell "su -c 'cat /proc/$(pidof com.target.app)/maps | grep -i xposed'"
```

### 常见检测代码模式

```java
// ========== Java 层检测模式 ==========

// 模式 1：调用栈检测
if (element.getClassName().contains("xposed")) { /* 检测到 */ }

// 模式 2：异常调用栈检测
try { throw new Exception(); } catch (Exception e) {
    for (StackTraceElement elem : e.getStackTrace()) { /* 检查 */ }
}

// 模式 3：类加载检测
Class.forName("de.robv.android.xposed.XposedBridge");

// 模式 4：ClassLoader 检测
ClassLoader.getSystemClassLoader().loadClass("de.robv.android.xposed.XposedHelpers");

// 模式 5：文件检测
new File("/system/framework/XposedBridge.jar").exists()

// 模式 6：系统属性检测
System.getProperty("vxp_forbid_status")
System.getProperty("ro.xposed.version")

// ========== Native 层检测模式 ==========

// 模式 7：maps 文件检测（C/C++）
FILE* fp = fopen("/proc/self/maps", "r");
// 然后搜索 "xposed" 或 "libxposed"

// 模式 8：dlopen 检测
void* handle = dlopen("libxposed_art.so", RTLD_NOW);
if (handle != NULL) { /* 检测到 */ }
```

### 搜索检测代码的关键词

```text
xposed
XposedBridge
de.robv.android.xposed
getStackTrace
Class.forName
/proc/self/maps
libxposed
vxp_forbid
ro.xposed
EdXposed
LSPosed
```

### App 类型与推荐策略

| App 类型 | 常见检测方式 | 推荐策略 | 成功率 |
|---------|-------------|---------|-------|
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
