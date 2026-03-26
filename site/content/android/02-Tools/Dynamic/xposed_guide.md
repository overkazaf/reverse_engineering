---
title: "Xposed 框架入门"
date: 2024-10-09
type: posts
tags: ["Native层", "动态分析", "Frida", "SSL Pinning", "Hook", "Xposed"]
weight: 10
---

# Xposed 框架入门

Xposed 是一个在 Android 平台上广受欢迎的动态代码 Hook 框架。与 Frida 主要用于实时、临时的分析不同，Xposed 旨在对系统和应用进行**永久性**的修改。它通过替换一个核心系统进程 (`app_process`)，在应用启动时加载自定义模块，从而实现对任意方法的高效 Hook。

## 目录

- [核心原理](#核心原理)
- [Xposed/LSPosed 安装配置](#xposedlsposed-安装配置)
- [模块开发基础](#模块开发基础)
- [Hook 方法详解](#hook-方法详解)
- [高级 Hook 技巧](#高级-hook-技巧)
- [常用 Hook 场景](#常用-hook-场景)
- [与 Frida 对比](#与-frida-对比)
- [调试与排错](#调试与排错)
- [实战案例](#实战案例)
- [LSPosed 特性](#lsposed-特性)

---

## 核心原理

Xposed 的工作基础是它能够在 Android 系统启动的核心阶段介入，并将自己的代码注入到每一个应用程序进程中。

```
┌──────────────────────────────────────────────────────┐
│                  Android 系统启动                      │
│                                                      │
│  init 进程 ──> Zygote (app_process) ──> App 进程      │
│                    │                      │           │
│              Xposed 替换              加载 XposedBridge │
│              app_process                  │           │
│                    v                      v           │
│           XposedBridge.jar ──> 执行模块 handleLoadPkg  │
└──────────────────────────────────────────────────────┘
```

1. **Zygote 注入**: Xposed 通过替换系统原生的 `/system/bin/app_process` 可执行文件，实现了对 Zygote 进程（所有 App 进程的父进程）的控制。当 Zygote 启动时，会加载 Xposed 的核心 Jar 包（Xposed Bridge）。
2. **方法 Hook**: 当模块需要 Hook 一个方法时，Xposed 会在运行时深入虚拟机（ART）内部，直接修改该方法在内存中的数据结构。它将目标方法"伪装"成一个 Native 方法，并将其执行入口指向 Xposed 的一个通用桥接函数。
3. **执行流重定向**: 当 App 调用被 Hook 的方法时，执行流会先进入 Xposed 的桥接函数，在这里 Xposed 依次调用所有模块的 `beforeHookedMethod`，然后调用原方法，最后再调用所有模块的 `afterHookedMethod`，从而实现对方法调用的完全控制。

```
App 调用 targetMethod()
    │
    v
Xposed 桥接函数拦截
    │
    v
beforeHookedMethod()   ← 可修改参数、可阻止原方法执行
    │
    v
原方法执行              ← 如未被 setResult() 拦截
    │
    v
afterHookedMethod()    ← 可修改返回值、可替换异常
```

> 想要更深入地了解其实现细节，请参考 [**Xposed Internals: A Deep Dive**](./xposed_internals.md)。

---

## Xposed/LSPosed 安装配置

### 框架演进历史

| 框架名称 | 支持 Android 版本 | 状态 | 说明 |
|:---------|:-----------------|:-----|:-----|
| Xposed (原版) | 4.0 - 8.1 | 停止维护 | rovo89 开发，Dalvik/ART 均支持 |
| EdXposed | 8.0 - 10 | 停止维护 | 基于 Riru，接力原版 Xposed |
| LSPosed | 8.1 - 14+ | **活跃维护** | 基于 Riru/Zygisk，当前首选 |
| LSPatch | 9.0 - 14+ | 活跃维护 | 无需 Root，直接修补 APK |

### 前提条件

- **解锁 Bootloader**: 每个厂商的解锁方式不同，请查阅对应机型的教程。
- **刷入 Magisk**: 当前推荐使用 Magisk 26.0+，支持 Zygisk。
- **Android 版本**: LSPosed 支持 Android 8.1 (API 27) 及以上。

### 安装步骤 (Magisk + Zygisk + LSPosed)

**第一步：启用 Zygisk** — 打开 Magisk Manager → 设置 → 开启 Zygisk → 重启设备。

**第二步：安装 LSPosed** — 从 [LSPosed GitHub Releases](https://github.com/LSPosed/LSPosed/releases) 下载 Zygisk 版 ZIP 包 → Magisk Manager → 模块 → 从本地安装 → 选择 ZIP → 重启。

**第三步：验证安装**

```bash
# 通过 ADB 检查
adb shell su -c 'ls /data/adb/lspd'
# 查看日志确认
adb logcat | grep -i "lsposed"
```

打开 LSPosed Manager，若状态页显示 **"已激活"**（绿色对勾），则安装成功。

### 备选方案：Riru

如果不能使用 Zygisk：在 Magisk 中安装 `Riru` 模块 → 重启 → 安装 LSPosed 的 Riru 版本 → 重启。

### 备选方案：LSPatch（无需 Root）

LSPatch 允许不 Root 直接修补目标 APK 来使用 Xposed 模块：

```bash
java -jar lspatch.jar target.apk -m module.apk -l 2
# target.apk  - 目标应用    -m module.apk - Xposed 模块    -l 2 - 本地注入模式
```

> **注意**：LSPatch 修补后 APK 签名会改变，可能导致签名验证失败。

---

## 模块开发基础

### 第一步：创建 Android 项目

在 Android Studio 中创建新项目，选择 Empty Activity 模板，Minimum SDK 选 API 27。

### 第二步：配置 build.gradle

```groovy
android {
    compileSdk 34
    defaultConfig {
        applicationId "com.example.myxposedmodule"
        minSdk 27
        targetSdk 34
    }
    buildTypes {
        release {
            minifyEnabled false  // Xposed 模块不建议混淆，会导致 xposed_init 中类名失效
        }
    }
}
dependencies {
    compileOnly 'de.robv.android.xposed:api:82'          // 运行时由框架提供，必须用 compileOnly
    compileOnly 'de.robv.android.xposed:api:82:sources'  // 可选：调试用源码
}
```

### 第三步：配置 AndroidManifest.xml

在 `<application>` 标签内添加：

```xml
<meta-data android:name="xposedmodule" android:value="true" />
<meta-data android:name="xposeddescription" android:value="我的第一个 Xposed 模块" />
<meta-data android:name="xposedminversion" android:value="93" />
```

### 第四步：创建 xposed_init

在 `app/src/main/assets/` 目录下创建纯文本文件 `xposed_init`（无扩展名），写入入口类全名：

```text
com.example.myxposedmodule.MainHook
```

### 第五步：编写入口类

```java
package com.example.myxposedmodule;

import de.robv.android.xposed.IXposedHookLoadPackage;
import de.robv.android.xposed.XC_MethodHook;
import de.robv.android.xposed.XposedBridge;
import de.robv.android.xposed.XposedHelpers;
import de.robv.android.xposed.callbacks.XC_LoadPackage.LoadPackageParam;

public class MainHook implements IXposedHookLoadPackage {
    @Override
    public void handleLoadPackage(final LoadPackageParam lpparam) throws Throwable {
        if (!lpparam.packageName.equals("com.target.app")) return;
        XposedBridge.log("[MyModule] 目标应用已加载: " + lpparam.packageName);

        XposedHelpers.findAndHookMethod(
            "com.target.app.LoginActivity", lpparam.classLoader,
            "checkPassword", String.class, String.class,
            new XC_MethodHook() {
                @Override
                protected void beforeHookedMethod(MethodHookParam param) throws Throwable {
                    XposedBridge.log("[MyModule] 用户名: " + param.args[0] + ", 密码: " + param.args[1]);
                }
                @Override
                protected void afterHookedMethod(MethodHookParam param) throws Throwable {
                    XposedBridge.log("[MyModule] 原始结果: " + param.getResult());
                    param.setResult(true);  // 强制登录成功
                }
            }
        );
    }
}
```

### 项目目录结构

```
MyXposedModule/
├── app/src/main/
│   ├── java/com/example/myxposedmodule/
│   │   └── MainHook.java           ← Hook 入口类
│   ├── assets/
│   │   └── xposed_init              ← 入口类声明
│   └── AndroidManifest.xml
└── app/build.gradle
```

### 构建与安装

```bash
./gradlew assembleDebug
adb install -r app/build/outputs/apk/debug/app-debug.apk
# LSPosed Manager → 模块 → 启用 → 设置作用域 → 强制停止目标应用
adb shell am force-stop com.target.app
```

---

## Hook 方法详解

### findAndHookMethod

```java
// 基本签名
XposedHelpers.findAndHookMethod(
    "完整类名", classLoader, "方法名",
    参数类型1.class, 参数类型2.class, ..., new XC_MethodHook() { ... }
);

// 示例：Hook 无参方法，篡改返回值
XposedHelpers.findAndHookMethod("com.target.app.Utils", classLoader, "getDeviceId",
    new XC_MethodHook() {
        @Override
        protected void afterHookedMethod(MethodHookParam param) throws Throwable {
            param.setResult("fake_device_id_12345");
        }
    }
);

// 示例：Hook 带参数的方法（注意基本类型用 int.class 而非 Integer.class）
XposedHelpers.findAndHookMethod("com.target.app.Utils", classLoader,
    "calculate", int.class, double.class,
    new XC_MethodHook() {
        @Override
        protected void beforeHookedMethod(MethodHookParam param) throws Throwable {
            XposedBridge.log("calculate(" + param.args[0] + ", " + param.args[1] + ")");
        }
    }
);

// 示例：参数类型来自目标 App 时，用 findClass 获取
Class<?> configClass = XposedHelpers.findClass("com.target.app.Config", classLoader);
XposedHelpers.findAndHookMethod("com.target.app.Manager", classLoader,
    "init", configClass, boolean.class, new XC_MethodHook() { /* ... */ });
```

### findAndHookConstructor

```java
XposedHelpers.findAndHookConstructor("com.target.app.UserInfo", classLoader,
    String.class, int.class,
    new XC_MethodHook() {
        @Override
        protected void afterHookedMethod(MethodHookParam param) throws Throwable {
            XposedBridge.log("新建 UserInfo: " + param.args[0]);
            XposedHelpers.setObjectField(param.thisObject, "isVip", true);
        }
    }
);
```

### XC_MethodHook 核心用法

`MethodHookParam` 对象包含调用的全部上下文：

| 成员/方法 | 说明 | 可用阶段 |
|:---------|:-----|:---------|
| `param.thisObject` | 方法所属对象实例（静态方法为 null） | before / after |
| `param.args` | `Object[]` 参数数组，可直接修改 | before / after |
| `param.getResult()` | 获取返回值 | after |
| `param.setResult(val)` | 设置返回值（before 中调用则跳过原方法） | before / after |
| `param.getThrowable()` | 获取原方法抛出的异常 | after |
| `param.setThrowable(t)` | 设置/替换异常 | before / after |

### XC_MethodReplacement

完全替换原方法，原方法不再执行：

```java
XposedHelpers.findAndHookMethod("com.target.app.Security", classLoader,
    "verifyLicense", String.class,
    new XC_MethodReplacement() {
        @Override
        protected Object replaceHookedMethod(MethodHookParam param) throws Throwable {
            return true;  // 完全替代原方法
        }
    }
);
```

### hookAllMethods / hookAllConstructors

不知道确切参数签名，或想批量 Hook 所有同名重载时：

```java
Class<?> cls = XposedHelpers.findClass("com.target.app.Network", classLoader);
XposedBridge.hookAllMethods(cls, "request", new XC_MethodHook() {
    @Override
    protected void beforeHookedMethod(MethodHookParam param) throws Throwable {
        XposedBridge.log("request() 参数数量: " + param.args.length);
    }
});
XposedBridge.hookAllConstructors(cls, new XC_MethodHook() { /* ... */ });
```

---

## 高级 Hook 技巧

### Hook 内部类

Java 内部类编译后类名格式为 `外部类$内部类`，匿名内部类为 `外部类$数字`：

```java
// 命名内部类: Outer.Inner → com.target.app.Outer$Inner
XposedHelpers.findAndHookMethod("com.target.app.Outer$Inner", classLoader,
    "doSomething", new XC_MethodHook() { /* ... */ });

// 匿名内部类: Outer$1, Outer$2 ...（需用 jadx 确认编号）
XposedHelpers.findAndHookMethod("com.target.app.Outer$1", classLoader,
    "onClick", android.view.View.class, new XC_MethodHook() { /* ... */ });
```

### Hook 抽象方法 / 接口方法

不能直接 Hook 抽象方法，需 Hook 具体实现类，或用 `hookAllMethods` 动态捕获：

```java
Class<?> base = XposedHelpers.findClass("com.target.app.Encryptor", classLoader);
XposedBridge.hookAllMethods(base, "encrypt", new XC_MethodHook() {
    @Override
    protected void beforeHookedMethod(MethodHookParam param) throws Throwable {
        XposedBridge.log("实际调用类: " + param.thisObject.getClass().getName());
    }
});
```

### 基于反射的动态 Hook

类名被混淆时，可通过方法特征在运行时定位：

```java
Class<?> obfClass = XposedHelpers.findClass("a.b.c", classLoader);
for (java.lang.reflect.Method m : obfClass.getDeclaredMethods()) {
    if (m.getReturnType() == String.class
            && m.getParameterTypes().length == 2
            && m.getParameterTypes()[0] == byte[].class) {
        XposedBridge.hookMethod(m, new XC_MethodHook() {
            @Override
            protected void afterHookedMethod(MethodHookParam param) throws Throwable {
                XposedBridge.log("疑似加密方法返回: " + param.getResult());
            }
        });
    }
}
```

### 读写对象字段

```java
// 读取字段
Object val  = XposedHelpers.getObjectField(param.thisObject, "mField");
int count   = XposedHelpers.getIntField(param.thisObject, "mCount");
boolean ok  = XposedHelpers.getBooleanField(param.thisObject, "isEnabled");

// 设置字段
XposedHelpers.setObjectField(param.thisObject, "mField", "newValue");
XposedHelpers.setIntField(param.thisObject, "mCount", 999);

// 静态字段 / 调用方法
XposedHelpers.setStaticBooleanField(targetClass, "DEBUG", true);
Object result = XposedHelpers.callMethod(param.thisObject, "getConfig");
Object inst   = XposedHelpers.callStaticMethod(targetClass, "getInstance");
```

---

## 常用 Hook 场景

### SSL Pinning 绕过

```java
// 方式一：替换 TrustManager
XposedHelpers.findAndHookMethod("javax.net.ssl.SSLContext", classLoader,
    "init",
    javax.net.ssl.KeyManager[].class,
    javax.net.ssl.TrustManager[].class,
    java.security.SecureRandom.class,
    new XC_MethodHook() {
        @Override
        protected void beforeHookedMethod(MethodHookParam param) throws Throwable {
            param.args[1] = new javax.net.ssl.TrustManager[]{
                new javax.net.ssl.X509TrustManager() {
                    public java.security.cert.X509Certificate[] getAcceptedIssuers() {
                        return new java.security.cert.X509Certificate[0];
                    }
                    public void checkClientTrusted(java.security.cert.X509Certificate[] c, String a) {}
                    public void checkServerTrusted(java.security.cert.X509Certificate[] c, String a) {}
                }
            };
        }
    }
);

// 方式二：绕过 OkHttp CertificatePinner
XposedHelpers.findAndHookMethod("okhttp3.CertificatePinner", classLoader,
    "check", String.class, java.util.List.class,
    new XC_MethodReplacement() {
        @Override
        protected Object replaceHookedMethod(MethodHookParam param) { return null; }
    }
);
```

### Root 检测绕过

```java
// 1. 隐藏 Root 相关文件
XposedHelpers.findAndHookMethod("java.io.File", classLoader, "exists",
    new XC_MethodHook() {
        @Override
        protected void afterHookedMethod(MethodHookParam param) throws Throwable {
            String path = ((java.io.File) param.thisObject).getAbsolutePath();
            if (path.contains("/su") || path.contains("/magisk")
                    || path.contains("Superuser") || path.contains("busybox")) {
                param.setResult(false);
            }
        }
    }
);

// 2. 拦截 Runtime.exec（阻止执行 which su 等命令）
XposedHelpers.findAndHookMethod("java.lang.Runtime", classLoader,
    "exec", String[].class, String[].class, java.io.File.class,
    new XC_MethodHook() {
        @Override
        protected void beforeHookedMethod(MethodHookParam param) throws Throwable {
            String[] cmds = (String[]) param.args[0];
            if (cmds != null && cmds.length > 0
                    && (cmds[0].contains("su") || cmds[0].contains("which"))) {
                param.setThrowable(new java.io.IOException("Permission denied"));
            }
        }
    }
);

// 3. 伪造 Build.TAGS
XposedHelpers.setStaticObjectField(android.os.Build.class, "TAGS", "release-keys");
```

### 签名验证绕过

```java
XposedHelpers.findAndHookMethod("android.app.ApplicationPackageManager", classLoader,
    "getPackageInfo", String.class, int.class,
    new XC_MethodHook() {
        @Override
        protected void afterHookedMethod(MethodHookParam param) throws Throwable {
            String pkg = (String) param.args[0];
            int flags = (int) param.args[1];
            if (pkg.equals(TARGET_PACKAGE) && (flags & 0x40) != 0) {  // GET_SIGNATURES
                Object pkgInfo = param.getResult();
                if (pkgInfo != null) {
                    android.content.pm.Signature origSig =
                        new android.content.pm.Signature(ORIGINAL_SIGNATURE_HEX);
                    XposedHelpers.setObjectField(pkgInfo, "signatures",
                        new android.content.pm.Signature[]{ origSig });
                }
            }
        }
    }
);
```

### 调试标志修改

```java
// 让目标应用变为可调试 (debuggable)
XposedHelpers.findAndHookMethod("android.app.ApplicationPackageManager", classLoader,
    "getApplicationInfo", String.class, int.class,
    new XC_MethodHook() {
        @Override
        protected void afterHookedMethod(MethodHookParam param) throws Throwable {
            android.content.pm.ApplicationInfo info =
                (android.content.pm.ApplicationInfo) param.getResult();
            if (info != null) {
                info.flags |= android.content.pm.ApplicationInfo.FLAG_DEBUGGABLE;
            }
        }
    }
);
```

---

## 与 Frida 对比

| 特性 | Xposed / LSPosed | Frida |
|:-----|:-----------------|:------|
| **核心目标** | 永久性修改：长期、稳定地改变应用行为 | 动态分析：实时、临时的逆向 |
| **运行环境** | Root + 刷入框架，需重启 | Root，无需重启，动态附加 |
| **开发语言** | Java（模块是标准 APK） | JavaScript（脚本即改即用） |
| **开发周期** | 慢：编码→编译→安装→激活→重启→测试 | 快：写脚本→附加→立即生效 |
| **持久性** | 极强：随应用启动自动生效 | 弱：依赖 frida-server 会话 |
| **Hook 层面** | 主要 Java 层 | Java 层 + Native 层均可 |
| **反检测** | 较难被检测（系统级注入） | 较容易被检测（ptrace 附加） |

**何时选择 Xposed**：永久改行为（去广告、防撤回）、Hook 应用启动最早期代码、需长期稳定运行、目标有 Frida 检测。

**何时选择 Frida**：逆向分析快速迭代、Hook Native 层、实时修改脚本、一次性分析任务。

**最佳实践：先 Frida 分析，再 Xposed 固化**

```
1. 静态分析 (jadx/JEB)  ──> 了解应用结构，定位关键类和方法
2. Frida 动态分析        ──> 快速验证 Hook 点，迭代调整
3. Xposed 模块固化       ──> 将方案写成持久化模块
```

---

## 调试与排错

### 日志调试

```java
// 推荐：XposedBridge.log —— 同时输出到 LSPosed 日志界面和 logcat
XposedBridge.log("[MyModule] 调试信息");
// 备选：标准 Android Log
android.util.Log.d("MyModule", "调试信息");
```

```bash
adb logcat -s "LSPosed" "XposedBridge" "MyModule"   # 过滤关键标签
adb logcat | grep "MyModule"                          # 快速查看模块日志
```

### 常见错误与解决

**模块未加载** — 检查：`xposed_init` 文件位置和类名拼写 → AndroidManifest.xml 三个 meta-data → LSPosed 作用域是否勾选目标应用 → 强制停止目标应用后重开。

**ClassNotFoundException** — 类名拼错或类尚未加载。用 jadx 确认正确类名（内部类用 `$`）。若类延迟加载，可 Hook `Application.onCreate` 后再执行：

```java
XposedHelpers.findAndHookMethod("android.app.Application", classLoader, "onCreate",
    new XC_MethodHook() {
        @Override
        protected void afterHookedMethod(MethodHookParam param) throws Throwable {
            ClassLoader cl = param.thisObject.getClass().getClassLoader();
            hookMyTarget(cl);  // Application 创建后大部分类已可访问
        }
    }
);
```

**NoSuchMethodError** — 方法名或参数类型不匹配（注意混淆后方法名可能是 a/b/c）。调试技巧：列出目标类所有方法：

```java
Class<?> clazz = XposedHelpers.findClass("com.target.app.Utils", classLoader);
for (java.lang.reflect.Method m : clazz.getDeclaredMethods()) {
    StringBuilder sb = new StringBuilder(m.getName()).append("(");
    for (Class<?> p : m.getParameterTypes()) sb.append(p.getName()).append(", ");
    sb.append(") -> ").append(m.getReturnType().getName());
    XposedBridge.log("[Debug] " + sb);
}
```

**Bootloop（启动循环）** — 紧急处理：长按关机 → Recovery → ADB 删除或禁用模块：

```bash
adb shell su -c 'touch /data/adb/modules/zygisk_lsposed/disable'
# 或直接删除: rm -rf /data/adb/modules/zygisk_lsposed
```

> **预防**：始终在 `handleLoadPackage` 中过滤包名，永远不要无条件执行 Hook。

---

## 实战案例

### Hook 目标应用的加密函数

假设通过 jadx 分析发现目标应用 `com.example.secureapp` 有加密工具类：

```java
// jadx 反编译输出
package com.example.secureapp.crypto;
public class AESHelper {
    public static String encrypt(String plaintext) { /* AES 加密 */ }
    public static String decrypt(String ciphertext) { /* AES 解密 */ }
    public static byte[] encryptBytes(byte[] data, byte[] key, byte[] iv) { /* ... */ }
}
```

**编写 Hook 模块**：

```java
package com.example.cryptohook;
import de.robv.android.xposed.*;
import de.robv.android.xposed.callbacks.XC_LoadPackage.LoadPackageParam;

public class CryptoHook implements IXposedHookLoadPackage {
    private static final String TAG = "[CryptoHook]";
    private static final String TARGET = "com.example.secureapp";
    private static final String CLS = "com.example.secureapp.crypto.AESHelper";

    @Override
    public void handleLoadPackage(LoadPackageParam lpparam) throws Throwable {
        if (!lpparam.packageName.equals(TARGET)) return;
        XposedBridge.log(TAG + " 开始 Hook...");
        ClassLoader cl = lpparam.classLoader;

        // Hook encrypt(String)
        XposedHelpers.findAndHookMethod(CLS, cl, "encrypt", String.class,
            new XC_MethodHook() {
                @Override
                protected void beforeHookedMethod(MethodHookParam param) throws Throwable {
                    XposedBridge.log(TAG + " encrypt 明文: " + param.args[0]);
                }
                @Override
                protected void afterHookedMethod(MethodHookParam param) throws Throwable {
                    XposedBridge.log(TAG + " encrypt 密文: " + param.getResult());
                    // 打印调用栈定位调用来源
                    XposedBridge.log(TAG + " 调用栈:\n" +
                        android.util.Log.getStackTraceString(new Throwable()));
                }
            }
        );

        // Hook decrypt(String)
        XposedHelpers.findAndHookMethod(CLS, cl, "decrypt", String.class,
            new XC_MethodHook() {
                @Override
                protected void beforeHookedMethod(MethodHookParam param) throws Throwable {
                    XposedBridge.log(TAG + " decrypt 密文: " + param.args[0]);
                }
                @Override
                protected void afterHookedMethod(MethodHookParam param) throws Throwable {
                    XposedBridge.log(TAG + " decrypt 明文: " + param.getResult());
                }
            }
        );

        // Hook encryptBytes(byte[], byte[], byte[]) —— 捕获 key 和 iv
        XposedHelpers.findAndHookMethod(CLS, cl, "encryptBytes",
            byte[].class, byte[].class, byte[].class,
            new XC_MethodHook() {
                @Override
                protected void beforeHookedMethod(MethodHookParam param) throws Throwable {
                    XposedBridge.log(TAG + " encryptBytes:");
                    XposedBridge.log(TAG + "   data: " + bytesToHex((byte[]) param.args[0]));
                    XposedBridge.log(TAG + "   key:  " + bytesToHex((byte[]) param.args[1]));
                    XposedBridge.log(TAG + "   iv:   " + bytesToHex((byte[]) param.args[2]));
                    XposedBridge.log(TAG + "   key(UTF-8): " + new String((byte[]) param.args[1], "UTF-8"));
                }
                @Override
                protected void afterHookedMethod(MethodHookParam param) throws Throwable {
                    XposedBridge.log(TAG + "   result: " + bytesToHex((byte[]) param.getResult()));
                }
            }
        );
    }

    private static String bytesToHex(byte[] bytes) {
        if (bytes == null) return "null";
        StringBuilder sb = new StringBuilder();
        for (byte b : bytes) sb.append(String.format("%02x", b));
        return sb.toString();
    }
}
```

**增强：自动保存数据到文件**

```java
private void saveToFile(String filename, String content) {
    try {
        java.io.File dir = new java.io.File("/sdcard/CryptoHook/");
        if (!dir.exists()) dir.mkdirs();
        java.io.FileWriter w = new java.io.FileWriter(new java.io.File(dir, filename), true);
        String ts = new java.text.SimpleDateFormat("HH:mm:ss").format(new java.util.Date());
        w.write("[" + ts + "] " + content + "\n");
        w.close();
    } catch (Exception e) {
        XposedBridge.log(TAG + " 写文件失败: " + e.getMessage());
    }
}
```

**构建、安装与验证**：

```bash
./gradlew assembleDebug
adb install -r app/build/outputs/apk/debug/app-debug.apk
# LSPosed 中启用并设置作用域为 com.example.secureapp
adb shell am force-stop com.example.secureapp
adb shell monkey -p com.example.secureapp -c android.intent.category.LAUNCHER 1
adb logcat | grep "CryptoHook"
```

**预期输出**：

```
[CryptoHook] 开始 Hook...
[CryptoHook] encrypt 明文: {"user":"admin","pass":"123456"}
[CryptoHook] encrypt 密文: a3f2b8c1d4e5...
[CryptoHook] encryptBytes:
[CryptoHook]   data: 7b22757365...
[CryptoHook]   key:  4d795365637265744b6579313233
[CryptoHook]   iv:   00112233445566778899aabbccddeeff
[CryptoHook]   key(UTF-8): MySecretKey123
[CryptoHook]   result: e8b2c1a4f3...
```

---

## LSPosed 特性

### 作用域管理

这是 LSPosed 最重要的改进。原版 Xposed 会将模块加载到**所有**进程中，而 LSPosed 可以精确指定作用域——只让模块加载到选定的应用中，未选中的应用完全不受影响。

```
LSPosed 作用域设置
┌──────────────────────────────────────────┐
│ 模块: CryptoHook                         │
│                                          │
│  [x] com.example.secureapp  (目标应用)    │
│  [ ] com.android.systemui                │
│  [ ] com.android.settings                │
│  [ ] 系统框架 (android)                   │
│                                          │
│  仅在勾选的应用进程中加载此模块             │
└──────────────────────────────────────────┘
```

### 无需重启激活模块

- **启用/更新模块**：LSPosed Manager 中操作后，只需**强制停止目标应用**再重新打开即可生效。
- **作用域包含系统框架/SystemUI 时**：仍需软重启或完整重启。

```bash
adb install -r new_module.apk             # 更新模块
adb shell am force-stop com.target.app     # 强制停止 → 重新打开即生效
```

### 与原版 Xposed 的差异

| 功能 | 原版 Xposed | LSPosed |
|:-----|:-----------|:--------|
| API 兼容 | API 82 | API 82-93 完全兼容 |
| 作用域管理 | 无（加载到所有进程） | 精确到单个应用 |
| Android 支持 | 最高 8.1 | 8.1 - 14+ |
| 注入方式 | 替换 app_process | 基于 Riru/Zygisk |
| 隐藏检测 | 无 | 寄生管理器 + 通知栏入口 |
| 日志 | 文件形式 | 内置查看器，支持过滤 |
| 多用户支持 | 不支持 | 支持（工作资料、分身） |

### 隐藏机制

1. **寄生管理器**：LSPosed Manager 以随机包名寄生，不暴露 `org.lsposed.manager`。
2. **通知入口**：可隐藏桌面图标，通过通知栏快捷方式进入。
3. **最小侵入**：得益于作用域，未选中的应用完全感知不到框架存在。

---

## 常见应用场景总结

| 场景 | 说明 | 典型代表 |
|:-----|:-----|:--------|
| UI 定制 | 修改系统或应用外观 | GravityBox |
| 功能增强 | 防撤回、自动抢红包等 | 微X模块 |
| 去除限制 | 去广告、去截图限制 | 大圣净化 |
| 隐私保护 | 拦截敏感信息，返回虚假数据 | XPrivacyLua |
| 安全分析 | 绕过 SSL Pinning、Root 检测 | TrustMeAlready |

---

## 参考资源

- [Xposed Framework Wiki](https://github.com/rovo89/XposedBridge/wiki)
- [LSPosed GitHub](https://github.com/LSPosed/LSPosed)
- [Xposed API Javadoc](https://api.xposed.info/reference/packages.html)
- [LSPatch GitHub](https://github.com/LSPosed/LSPatch)
