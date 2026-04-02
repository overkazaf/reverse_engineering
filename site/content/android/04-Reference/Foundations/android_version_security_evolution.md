---
title: "Android 版本安全特性演进与逆向影响"
date: 2025-04-02
type: posts
tags: ["Android", "安全", "逆向分析", "版本差异", "基础知识"]
weight: 5
---

# Android 版本安全特性演进与逆向影响

Android 系统从 5.0 到 15，每一个大版本都引入了大量安全特性。这些安全增强不仅影响了普通开发者的开发方式，更直接改变了逆向工程师的分析策略和工具选择。不了解目标设备的 Android 版本特性，往往是逆向分析受阻的首要原因。

---

## 1. 概述

对于逆向工程师来说，理解 Android 各版本安全特性的演进至关重要，原因如下：

1. **工具兼容性**：不同 Android 版本对 Frida、Xposed、Magisk 等工具的支持程度不同，选错工具版本会直接导致注入失败
2. **分析策略差异**：Android 7.0 之后的证书信任策略变化使得抓包方式截然不同；Android 9.0 的 Hidden API 限制改变了反射调用的方式
3. **绕过方法更新**：每个版本的安全增强都需要对应的绕过手段，旧方法可能在新版本上完全失效
4. **Native 层影响**：从 Linker namespace 到 XOM 再到 16KB 页面大小，底层变化影响 SO 分析的每一个环节
5. **加密与认证**：Hardware Keystore、BiometricPrompt、MTE 等特性不断提高数据保护强度

> [!tip] 实用建议
> 
> 在开始任何逆向分析任务之前，务必先确认目标设备的 Android 版本和安全补丁级别：
> ```bash
> adb shell getprop ro.build.version.release    # Android 版本号
> adb shell getprop ro.build.version.sdk         # API Level
> adb shell getprop ro.build.version.security_patch  # 安全补丁日期
> ```

---

## 2. 版本安全特性总览表

下表汇总了 Android 5.0 到 15 各版本的关键安全特性及其对逆向工程的影响：

| 版本号 (代号) | API Level | 关键安全特性 | 对逆向的影响 |
|:-------------|:---------:|:------------|:------------|
| **5.0-5.1** (Lollipop) | 21-22 | ART 默认运行时、SELinux enforcing、全盘加密 (FDE) | DEX 优化格式变化（OAT 文件），需新 dump 策略 |
| **6.0** (Marshmallow) | 23 | 运行时权限、验证启动、硬件 Keystore、指纹 API | 权限检查成为 hook 目标，Keystore 提取需新方法 |
| **7.0-7.1** (Nougat) | 24-25 | 网络安全配置、用户证书不信任、Linker namespace、APK Sig v2、FBE | 抓包需额外配置，注入需处理 namespace，v2 签名影响重打包 |
| **8.0-8.1** (Oreo) | 26-27 | Project Treble、Vendor/System 分离、HIDL、后台限制 | SO 分析需关注分区，后台限制影响持久化 hook |
| **9.0** (Pie) | 28 | Hidden API 限制、TLS 强制、BiometricPrompt、ASLR 改进 | 反射调用受限需绕过，ASLR 使内存分析更复杂 |
| **10** (Q) | 29 | Scoped Storage、XOM、TLS 1.3、MAC 随机化 | XOM 使 .text 不可读，Scoped Storage 影响 dump 路径 |
| **11** (R) | 30 | 包可见性限制、APK Sig v4、GWP-ASan | 应用枚举受限，需 QUERY_ALL_PACKAGES 权限 |
| **12-12L** (S) | 31-32 | 隐私面板、ART Mainline 模块化、ASLR 增强 | ART 可独立更新，调试限制增强 |
| **13** (T) | 33 | 通知权限、Intent filter 验证增强 | Intent filter 验证影响 deep link 测试 |
| **14** (U) | 34 | Credential Manager、16KB 页面大小支持、minSdkVersion 限制 | SO 段对齐变化，旧工具重打包受限 |
| **15** (V) | 35 | 16KB 页面全面支持、MTE 生产可用、Privacy Sandbox | MTE 影响内存分析和 exploit，16KB 页面成硬性要求 |

---

## 3. 详细版本分析

### 3.1 Android 5.0-5.1 (Lollipop, API 21-22)

Android 5.0 是 Android 安全架构的分水岭，三项核心变化奠定了现代 Android 安全的基础。

#### 3.1.1 ART 取代 Dalvik 成为默认运行时

Android 5.0 将 ART (Android Runtime) 确立为唯一的运行时环境，彻底取代了 Dalvik。ART 使用 AOT (Ahead-Of-Time) 编译，在应用安装时将 DEX 字节码编译为本地机器码。

**核心变化**：
- DEX 字节码不再直接解释执行，而是被编译为 OAT (Optimized Android runtime application) 格式
- 编译产物路径从 `/data/dalvik-cache/` 下的 `.dex` 文件变为 `.odex`（实际是 OAT 格式）
- 运行时方法调用方式发生根本改变

```bash
# 查看 OAT 文件
adb shell ls /data/dalvik-cache/arm64/
# 使用 oatdump 分析
oatdump --oat-file=/data/dalvik-cache/arm64/system@app@SomeApp@SomeApp.apk@classes.dex
```

#### 3.1.2 SELinux Enforcing Mode 全面启用

Android 5.0 将 SELinux 从 Permissive 模式切换到 Enforcing 模式，意味着所有违反安全策略的操作都会被阻止，而不仅仅是记录日志。

```bash
# 查看 SELinux 状态
adb shell getenforce
# 输出: Enforcing

# 查看 SELinux 策略
adb shell ls -la /sys/fs/selinux/
```

#### 3.1.3 全盘加密 (FDE)

Android 5.0 要求新出厂设备默认启用全盘加密 (Full Disk Encryption)，使用 `dm-crypt` 对 `/data` 分区进行加密。

#### 对逆向的影响

| 影响点 | 具体变化 | 应对策略 |
|:------|:--------|:--------|
| DEX dump | OAT 格式取代直接 DEX 执行 | 使用 `oatdump`、`baksmali` 适配 OAT 格式 |
| 方法 Hook | ART 方法结构与 Dalvik 不同 | 更新 Hook 框架至 ART 兼容版本 |
| SELinux 阻止 | 文件操作、ptrace 等被策略限制 | 需要修改 SELinux 策略或切换到 Permissive |
| 数据获取 | 全盘加密阻止离线数据读取 | 需要在设备解锁状态下操作 |

---

### 3.2 Android 6.0 (Marshmallow, API 23)

#### 3.2.1 运行时权限模型

Android 6.0 将敏感权限从安装时授予改为运行时动态申请。应用需要在代码中显式请求危险权限，用户可以拒绝或撤销。

```java
// 运行时权限检查代码（逆向分析中常见的 hook 目标）
if (ContextCompat.checkSelfPermission(this, Manifest.permission.READ_PHONE_STATE)
        != PackageManager.PERMISSION_GRANTED) {
    ActivityCompat.requestPermissions(this,
        new String[]{Manifest.permission.READ_PHONE_STATE}, REQUEST_CODE);
}
```

**逆向关注点**：`checkSelfPermission` 和 `requestPermissions` 是常见的 hook 目标，可以通过 Frida 直接返回 `PERMISSION_GRANTED` 绕过权限检查。

```javascript
// Frida 绕过运行时权限检查
Java.perform(function() {
    var ContextCompat = Java.use('androidx.core.content.ContextCompat');
    ContextCompat.checkSelfPermission.implementation = function(context, permission) {
        console.log('[*] checkSelfPermission: ' + permission);
        return 0; // PERMISSION_GRANTED
    };
});
```

#### 3.2.2 验证启动 (Verified Boot)

Android 6.0 强化了验证启动机制，确保从引导加载程序到系统分区的完整信任链。修改 system 分区会触发验证失败。

#### 3.2.3 硬件级密钥库 (Hardware Keystore)

Android 6.0 引入了硬件级别的密钥库 API，密钥存储在 TEE (Trusted Execution Environment) 或专用安全芯片中。

**对逆向影响**：
- 存储在硬件 Keystore 中的密钥无法通过软件方式提取
- 加密操作在 TEE 内部完成，无法通过内存 dump 获取密钥材料
- 需要 hook `KeyStore` API 调用来拦截加密前/解密后的明文数据

```javascript
// Frida hook KeyStore 操作
Java.perform(function() {
    var Cipher = Java.use('javax.crypto.Cipher');
    Cipher.doFinal.overload('[B').implementation = function(input) {
        console.log('[*] Cipher.doFinal input: ' + bytesToHex(input));
        var result = this.doFinal(input);
        console.log('[*] Cipher.doFinal output: ' + bytesToHex(result));
        return result;
    };
});
```

#### 3.2.4 指纹认证 API

Android 6.0 引入 `FingerprintManager` API，允许应用使用设备指纹传感器进行身份验证。

---

### 3.3 Android 7.0-7.1 (Nougat, API 24-25)

Android 7.0 对逆向工程的影响极为深远，尤其是网络安全配置的引入，直接改变了流量拦截的方式。

#### 3.3.1 网络安全配置 (Network Security Config)

这是影响逆向分析最深远的变化之一。Android 7.0 引入了 `network_security_config.xml`，允许应用以声明式方式配置网络安全策略。

**最关键的变化**：默认情况下，应用不再信任用户安装的 CA 证书。这意味着在设备上安装 mitmproxy/Burp 等代理的证书后，targetSdkVersion >= 24 的应用会拒绝连接。

```xml
<!-- 应用的默认行为 (targetSdkVersion >= 24) -->
<network-security-config>
    <base-config>
        <trust-anchors>
            <certificates src="system"/>
            <!-- 注意：没有 user 证书源 -->
        </trust-anchors>
    </base-config>
</network-security-config>
```

#### 绕过证书信任限制

**方法一：修改 APK 中的网络安全配置**

反编译 APK 后，添加或修改 `network_security_config.xml`，使其信任用户证书：

```xml
<!-- network_security_config.xml -->
<network-security-config>
    <base-config>
        <trust-anchors>
            <certificates src="system"/>
            <certificates src="user"/>
        </trust-anchors>
    </base-config>
</network-security-config>
```

然后在 `AndroidManifest.xml` 中引用：

```xml
<application
    android:networkSecurityConfig="@xml/network_security_config"
    ...>
```

**方法二：Magisk + MoveCert 模块**

将用户证书移动到系统证书目录，使其被视为系统证书：

```bash
# 1. 安装 Magisk (确保版本 24+)
# 2. 安装 MagiskTrustUserCerts 模块
# 模块地址: https://github.com/NVISOsecurity/MagiskTrustUserCerts

# 安装用户证书后，模块会自动将其复制到 /system/etc/security/cacerts/
# 重启设备生效

# 验证证书是否在系统目录
adb shell ls /system/etc/security/cacerts/ | grep -i "hash"
```

**方法三：Frida SSL Pinning Bypass**

使用 Frida 在运行时绕过 SSL 证书验证：

```javascript
// Frida SSL Pinning Bypass (通用版)
Java.perform(function() {
    // 绕过 TrustManager
    var TrustManagerImpl = Java.use('com.android.org.conscrypt.TrustManagerImpl');
    TrustManagerImpl.verifyChain.implementation = function(untrustedChain,
        trustAnchorChain, host, clientAuth, ocspData, tlsSctData) {
        console.log('[*] SSL Pinning Bypass: ' + host);
        return untrustedChain;
    };

    // 绕过 OkHttp CertificatePinner
    try {
        var CertificatePinner = Java.use('okhttp3.CertificatePinner');
        CertificatePinner.check.overload('java.lang.String', 'java.util.List')
            .implementation = function(hostname, peerCertificates) {
            console.log('[*] OkHttp SSL Pinning Bypass: ' + hostname);
            return;
        };
    } catch (e) {
        console.log('[*] OkHttp not found, skipping...');
    }

    // 绕过 WebView SSL 错误
    var WebViewClient = Java.use('android.webkit.WebViewClient');
    WebViewClient.onReceivedSslError.implementation = function(view, handler, error) {
        console.log('[*] WebView SSL Error Bypass');
        handler.proceed();
    };
});
```

#### 3.3.2 Linker Namespace 隔离

Android 7.0 引入了 Linker namespace 机制，限制应用只能加载特定路径下的共享库，防止应用访问系统内部的私有 SO 库。

```
# namespace 隔离示意
┌──────────────────────────────────────────┐
│            Android 7.0+ Linker           │
├──────────────────────────────────────────┤
│                                          │
│  ┌────────────┐    ┌────────────┐        │
│  │  default    │    │  classloader│       │
│  │  namespace  │    │  namespace  │       │
│  ├────────────┤    ├────────────┤        │
│  │ /system/lib│    │ /data/app/ │        │
│  │ /vendor/lib│    │ app的SO    │        │
│  └────────────┘    └────────────┘        │
│       ↕ 受限访问                          │
└──────────────────────────────────────────┘
```

**对逆向影响**：Frida 和 Xposed 注入时需要处理 namespace 隔离，否则可能无法正确加载或 hook 目标 SO。

#### 3.3.3 APK Signature Scheme v2

APK Signature Scheme v2 对整个 APK 文件进行签名验证（而非仅 JAR 签名），修改 APK 任何部分都会导致签名失效。

**对逆向影响**：重打包后必须使用支持 v2 签名的工具重新签名：

```bash
# 使用 apksigner 进行 v2 签名
apksigner sign --ks my-key.jks --ks-key-alias mykey \
    --v1-signing-enabled true --v2-signing-enabled true \
    modified.apk

# 验证签名
apksigner verify --verbose modified.apk
```

#### 3.3.4 File-Based Encryption (FBE)

Android 7.0 引入基于文件的加密 (FBE) 取代全盘加密 (FDE)，允许不同文件使用不同密钥加密，支持 Direct Boot 模式。

#### 3.3.5 JIT 编译器回归 (Profile-Guided Compilation)

ART 重新引入 JIT 编译器，与 AOT 结合形成混合编译模式：

```
应用首次安装 → 全部解释执行/JIT
       ↓
   收集运行时 Profile
       ↓
   设备空闲时执行 AOT 编译（仅热点代码）
       ↓
   后续运行: 热点代码 AOT 执行 + 冷代码 JIT/解释执行
```

**对逆向影响**：方法可能处于不同的编译状态，hook 时需要考虑方法是 AOT 编译还是解释执行。

---

### 3.4 Android 8.0-8.1 (Oreo, API 26-27)

#### 3.4.1 Project Treble (HAL 接口标准化)

Project Treble 是 Android 架构的一次重大重构，将 vendor（硬件相关）实现与 Android 框架分离：

```
┌──────────────────────────────────────────────┐
│                Android 8.0+ 架构              │
├──────────────────────────────────────────────┤
│                                              │
│  ┌──────────┐  ┌──────────┐                  │
│  │ Framework │  │   Apps   │  ← system 分区   │
│  └────┬─────┘  └──────────┘                  │
│       │ HIDL                                 │
│  ┌────┴─────┐                                │
│  │  Vendor  │  ← vendor 分区                  │
│  │  HAL     │                                │
│  └──────────┘                                │
│                                              │
└──────────────────────────────────────────────┘
```

#### 3.4.2 Vendor/System 分区分离

SO 库被严格按照分区组织：

```bash
# System SO 路径
/system/lib64/     # 框架层 SO
/system/lib64/hw/  # System HAL 库

# Vendor SO 路径
/vendor/lib64/     # 厂商 SO
/vendor/lib64/hw/  # Vendor HAL 库

# 查看 SO 所在分区
adb shell ls -la /system/lib64/ | head -20
adb shell ls -la /vendor/lib64/ | head -20
```

#### 3.4.3 HIDL (HAL Interface Definition Language)

HIDL 定义了 Framework 与 Vendor HAL 之间的稳定接口，使用 Binder IPC 进行跨进程通信。

#### 3.4.4 更严格的后台限制

Android 8.0 对后台服务施加了严格限制：
- 后台服务在一定时间后被系统终止
- 隐式广播限制
- 后台定位更新频率降低

**对逆向影响**：
- 需要持久化运行的 hook 框架（如 Frida gadget）可能被后台限制影响
- 需要将服务声明为前台服务或使用 Work Manager

#### Treble 架构下的 SO 查找技巧

```bash
# 查找特定 SO 在哪个分区
adb shell find /system /vendor /product /apex -name "libtarget.so" 2>/dev/null

# 查看 SO 的链接依赖
adb shell readelf -d /vendor/lib64/libtarget.so | grep NEEDED

# 查看 vendor namespace 中可见的库
adb shell cat /system/etc/ld.config.txt | grep -A 10 "\[vendor\]"

# 列出 HIDL 服务
adb shell lshal
```

---

### 3.5 Android 9.0 (Pie, API 28)

Android 9.0 对逆向工程引入了几项影响深远的限制。

#### 3.5.1 非 SDK 接口限制 (Hidden API Restrictions)

这是对 Java 层逆向影响最大的变化之一。Android 9.0 开始限制应用通过反射、JNI 等方式访问 SDK 中未公开的内部 API（标记为 `@hide` 的 API）。

**限制分级**：

| 列表 | 说明 | 限制程度 |
|:-----|:-----|:--------|
| whitelist | 公开 SDK API | 无限制 |
| light-greylist | 宽松灰名单 | 可用但有警告 |
| dark-greylist | 严格灰名单 | targetSdk >= 28 被阻止 |
| blacklist | 黑名单 | 完全阻止 |

**绕过方法一：双重反射**

```java
// 通过双重反射绕过 Hidden API 限制
// 原理: 系统检查的是"调用者"的身份, 双重反射让"调用者"变成系统自己
Method forName = Class.class.getDeclaredMethod("forName", String.class);
Method getDeclaredMethod = Class.class.getDeclaredMethod(
    "getDeclaredMethod", String.class, Class[].class);

// 通过双重反射获取 VMRuntime
Class<?> vmRuntime = (Class<?>) forName.invoke(null, "dalvik.system.VMRuntime");
Method setHiddenApiExemptions = (Method) getDeclaredMethod.invoke(
    vmRuntime, "setHiddenApiExemptions", new Class[]{String[].class});

// 获取 VMRuntime 实例并设置豁免
Method getRuntime = (Method) getDeclaredMethod.invoke(
    vmRuntime, "getRuntime", new Class[0]);
Object runtime = getRuntime.invoke(null);

// 豁免所有隐藏 API（传入 "L" 表示所有以 L 开头的签名，即所有类）
setHiddenApiExemptions.invoke(runtime, new Object[]{new String[]{"L"}});
```

**绕过方法二：Frida 运行时绕过**

```javascript
// Frida 绕过 Hidden API 限制
Java.perform(function() {
    var VMRuntime = Java.use('dalvik.system.VMRuntime');
    var runtime = VMRuntime.getRuntime();
    runtime.setHiddenApiExemptions(['L']);
    console.log('[*] Hidden API restrictions bypassed');
});
```

**绕过方法三：通过 adb 设置**

```bash
# 开发/测试环境下可直接通过 adb 关闭限制
adb shell settings put global hidden_api_policy 1
# 0 = 不检测 (disable)
# 1 = 仅警告 (just warn)
# 2 = 不允许 dark greylist
# 3 = 不允许所有非 SDK API
```

#### 3.5.2 TLS 默认强制

Android 9.0 默认禁止明文 HTTP 流量 (cleartext traffic)。应用必须使用 HTTPS，除非在网络安全配置中显式允许明文。

```xml
<!-- 允许明文流量（逆向测试环境配置） -->
<network-security-config>
    <base-config cleartextTrafficPermitted="true">
        <trust-anchors>
            <certificates src="system"/>
            <certificates src="user"/>
        </trust-anchors>
    </base-config>
</network-security-config>
```

#### 3.5.3 BiometricPrompt API

Android 9.0 引入统一的生物识别认证 API `BiometricPrompt`，替代了 Android 6.0 的 `FingerprintManager`。

#### 3.5.4 DNS over TLS

系统级 DNS over TLS 支持（Private DNS），使得 DNS 查询也被加密，影响 DNS 层面的流量拦截。

#### 3.5.5 ASLR 改进

Android 9.0 改进了地址空间布局随机化 (ASLR)，增加了代码和数据段的随机化程度。

**对逆向影响**：
- 每次进程重启后，库的加载基址都会变化
- 不能依赖固定地址进行 hook，需要动态计算偏移
- 使用 Frida 的 `Module.findBaseAddress()` 获取实际加载地址

```javascript
// Frida 中动态获取 SO 基址
var base = Module.findBaseAddress('libtarget.so');
console.log('[*] libtarget.so base: ' + base);

// 基于偏移 hook
var targetFunc = base.add(0x1234);
Interceptor.attach(targetFunc, {
    onEnter: function(args) {
        console.log('[*] targetFunc called');
    }
});
```

---

### 3.6 Android 10 (Q, API 29)

Android 10 在原生安全层面引入了多项重要变化。

#### 3.6.1 Scoped Storage (分区存储)

应用只能访问自己的私有目录和特定的公共媒体文件，不再能自由访问外部存储。

**对逆向影响**：
- 文件 dump 路径受限，不能随意写入 `/sdcard/` 目录
- Frida 脚本中保存文件需要使用应用的私有目录

```javascript
// Frida 在 Scoped Storage 环境下保存文件
Java.perform(function() {
    var context = Java.use('android.app.ActivityThread')
        .currentApplication().getApplicationContext();
    var filesDir = context.getFilesDir().getAbsolutePath();
    console.log('[*] 可写目录: ' + filesDir);
    // 文件操作使用 filesDir 作为基础路径
});
```

#### 3.6.2 Execute-Only Memory (XOM)

Android 10 为 native 代码引入了仅执行内存 (XOM) 机制。`.text` 段被标记为仅执行，不可读取。

**核心影响**：传统的内存 dump 技术无法直接读取代码段。

```
# XOM 内存权限对比
传统 (Android 9 及更早):
  .text 段权限: r-x (可读可执行)
  可以直接通过 /proc/pid/mem 读取代码

Android 10+ (XOM 启用):
  .text 段权限: --x (仅执行)
  通过 /proc/pid/mem 读取 .text 段返回全零
```

**XOM 绕过技术**：

```python
# 绕过方法 1: 使用 ptrace (Frida 默认使用此方式)
# ptrace 系统调用不受 XOM 限制
# Frida 通过 ptrace attach 到目标进程后可以正常读取代码段

# 绕过方法 2: 通过 adb 禁用 XOM (需要 root)
# adb shell setprop debug.arm64.xom false
# 部分设备可能不支持此属性

# 绕过方法 3: 修改 ELF phdr 移除 XOM 标志
# 将 PF_X (仅执行) 改为 PF_R|PF_X (可读可执行)
# 需要修改 SO 文件的 Program Header

# 绕过方法 4: 利用 mmap 重新映射
# 在 Frida 脚本中重新映射代码段为可读
```

```javascript
// Frida 检查 XOM 状态
function checkXOM(moduleName) {
    var module = Process.findModuleByName(moduleName);
    if (module) {
        Process.enumerateRanges('--x').forEach(function(range) {
            if (range.base.compare(module.base) >= 0 &&
                range.base.compare(module.base.add(module.size)) < 0) {
                console.log('[*] XOM 区域: ' + range.base + ' - '
                    + range.base.add(range.size)
                    + ' 权限: ' + range.protection);
            }
        });
    }
}

// 通过 Frida 读取 XOM 保护的代码段
function readXOMCode(address, size) {
    // Frida 通过 ptrace 可以绕过 XOM 限制
    try {
        var buf = Memory.readByteArray(address, size);
        console.log('[*] 成功读取 ' + size + ' 字节');
        return buf;
    } catch (e) {
        console.log('[-] 读取失败: ' + e);
        return null;
    }
}
```

#### 3.6.3 TLS 1.3 默认启用

Android 10 默认启用 TLS 1.3，提供更快的握手速度和更强的安全性。

**对逆向影响**：TLS 1.3 加密了更多的握手信息（如证书），使被动嗅探更加困难。但使用中间人代理（如 mitmproxy）的主动拦截仍然有效。

#### 3.6.4 MAC 地址随机化

Android 10 对每个 Wi-Fi 网络使用随机 MAC 地址，防止跨网络跟踪设备。

**对逆向影响**：
- 基于 MAC 地址的设备指纹识别失效
- 分析设备指纹时需要关注应用是否使用了其他持久化标识符

---

### 3.7 Android 11 (R, API 30)

#### 3.7.1 包可见性限制 (Package Visibility)

Android 11 限制了应用查询其他已安装应用的能力。默认情况下，应用只能看到特定的系统应用和在 `<queries>` 标签中声明的应用。

```xml
<!-- AndroidManifest.xml 中声明需要查询的包 -->
<manifest>
    <queries>
        <package android:name="com.target.app"/>
    </queries>

    <!-- 或者请求完全的包可见性 -->
    <uses-permission android:name="android.permission.QUERY_ALL_PACKAGES"/>
</manifest>
```

**对逆向影响**：
- 编写分析工具时，枚举已安装应用需要 `QUERY_ALL_PACKAGES` 权限
- hook `PackageManager.getInstalledPackages()` 可能返回不完整的结果

```javascript
// Frida 绕过包可见性限制
Java.perform(function() {
    var PackageManager = Java.use('android.app.ApplicationPackageManager');
    PackageManager.getInstalledPackages.overload('int').implementation = function(flags) {
        // 通过调用系统服务直接获取完整列表
        console.log('[*] getInstalledPackages called with flags: ' + flags);
        var result = this.getInstalledPackages(flags);
        console.log('[*] Returned ' + result.size() + ' packages');
        return result;
    };
});
```

#### 3.7.2 APK Signature Scheme v4

APK Signature Scheme v4 主要服务于 ADB 增量安装 (`adb install --incremental`)，生成一个单独的 `.idsig` 文件。

**对逆向影响**：v4 签名不影响传统的 APK 重打包流程，因为 v4 签名是可选的，且仅用于优化安装速度。

#### 3.7.3 Scoped Storage 强制执行

Android 11 强制所有应用使用 Scoped Storage，移除了 `requestLegacyExternalStorage` 的豁免。

#### 3.7.4 GWP-ASan (内存安全检测)

GWP-ASan 是一个概率性的内存安全检测器，可以检测 use-after-free 和 heap-buffer-overflow。

**对逆向影响**：
- 利用内存安全漏洞的 exploit 可能被 GWP-ASan 检测到
- 分析 crash 时需要区分 GWP-ASan 报告和普通 crash

---

### 3.8 Android 12-12L (S, API 31-32)

#### 3.8.1 隐私面板 (Privacy Dashboard)

Android 12 引入隐私面板，显示过去 24 小时内应用对敏感权限（位置、摄像头、麦克风）的访问记录。

#### 3.8.2 ART 模块化 (Mainline)

这是一项对逆向工程有深远影响的变化。ART 运行时成为 Project Mainline 的一部分，可以通过 Google Play 系统更新独立于 Android 版本进行更新。

**对逆向影响**：
- 同一个 Android 12 设备，ART 运行时版本可能不同
- hook 框架（如 Frida）的兼容性可能在 ART 模块更新后出现问题
- 分析 ART 内部结构时需要确认具体的 ART 版本

```bash
# 查看 ART 模块版本
adb shell pm list packages | grep com.google.android.art
adb shell dumpsys package com.google.android.art | grep version

# 查看 ART apex 信息
adb shell ls -la /apex/com.android.art/
```

#### 3.8.3 ASLR 增强

Android 12 进一步增强了 ASLR，增大了地址空间随机化范围，特别是对 64 位进程。

#### 3.8.4 Restricted Debugging 增强

Android 12 增强了对非 debuggable 应用的调试限制。

**绕过 Restricted Debugging 的方法**：

```bash
# 方法 1: 使用 Magisk 修改 ro.debuggable 属性
# 在 Magisk 的 post-fs-data.sh 中添加:
resetprop ro.debuggable 1

# 方法 2: 重打包 APK 启用 debuggable
# 在 AndroidManifest.xml 中添加:
# android:debuggable="true"

# 方法 3: 使用 Frida 直接注入（不需要 debuggable）
frida -U -f com.target.app -l hook.js --no-pause
```

```javascript
// Frida 绕过 debuggable 检查
Java.perform(function() {
    var ApplicationInfo = Java.use('android.content.pm.ApplicationInfo');
    var GET_META_DATA = 128;

    // 一些应用会检查自身是否为 debuggable
    var PackageManager = Java.use('android.app.ApplicationPackageManager');
    PackageManager.getApplicationInfo.overload('java.lang.String', 'int')
        .implementation = function(packageName, flags) {
        var info = this.getApplicationInfo(packageName, flags);
        // 移除 FLAG_DEBUGGABLE 标志，防止反调试检测
        info.flags.value = info.flags.value & ~2; // FLAG_DEBUGGABLE = 0x2
        return info;
    };
});
```

---

### 3.9 Android 13 (T, API 33)

#### 3.9.1 通知权限 (POST_NOTIFICATIONS)

Android 13 将通知发送权限改为运行时权限，应用需要显式请求 `POST_NOTIFICATIONS` 权限。

#### 3.9.2 按应用语言设置

允许用户为每个应用单独设置语言，应用可能根据语言配置加载不同的资源或执行不同的逻辑分支。

#### 3.9.3 Intent Filter 验证增强

Android 13 加强了 Intent Filter 的验证，自动验证的 App Link 域名需要通过更严格的 Digital Asset Links 验证。

**对逆向影响**：
- 测试 deep link 时需要确保域名验证通过，或使用 adb 命令手动触发
- 分析应用的路由逻辑时需要关注 Intent Filter 配置

```bash
# 测试 deep link（不受 Intent Filter 验证限制）
adb shell am start -a android.intent.action.VIEW \
    -d "https://example.com/deeplink?param=value" \
    com.target.app

# 查看应用的 Intent Filter 验证状态
adb shell pm get-app-links com.target.app

# 手动重置验证状态
adb shell pm set-app-links --package com.target.app 0 all
```

#### 3.9.4 更细粒度的媒体权限

`READ_EXTERNAL_STORAGE` 被拆分为 `READ_MEDIA_IMAGES`、`READ_MEDIA_VIDEO` 和 `READ_MEDIA_AUDIO`。

**对逆向影响**：权限模型继续复杂化，hook 权限检查时需要覆盖更多的权限类型。

---

### 3.10 Android 14 (U, API 34)

#### 3.10.1 Credential Manager API

Android 14 引入 Credential Manager 统一管理密码、通行密钥 (Passkeys) 和联合登录凭据。

#### 3.10.2 16KB 页面大小支持（部分设备）

这是对 Native 层逆向影响最大的变化之一。部分 Android 14 设备开始支持 16KB 内存页面大小（传统为 4KB）。

**核心影响**：

```bash
# 4KB 页面 (传统): .text 段对齐到 0x1000 (4096)
# 16KB 页面 (Android 14+): .text 段对齐到 0x4000 (16384)

# 分析工具需要适配新的对齐方式
# 使用 readelf 检查段对齐:
readelf -l libtarget.so | grep LOAD

# 4KB 页面设备的典型输出:
# LOAD  0x000000 0x00000000 0x00000000 0x01234 0x01234 R   0x1000
# LOAD  0x001000 0x00001000 0x00001000 0x05678 0x05678 R E 0x1000

# 16KB 页面设备的典型输出:
# LOAD  0x000000 0x00000000 0x00000000 0x01234 0x01234 R   0x4000
# LOAD  0x004000 0x00004000 0x00004000 0x05678 0x05678 R E 0x4000
```

**对逆向影响详解**：

| 影响方面 | 4KB 页面 | 16KB 页面 |
|:--------|:---------|:---------|
| 段对齐 | 0x1000 | 0x4000 |
| 内存映射粒度 | 4KB | 16KB |
| ELF 段间距 | 较小 | 较大（更多填充） |
| 偏移计算 | 基于 0x1000 | 基于 0x4000 |
| 工具兼容性 | 所有工具支持 | 需要工具更新 |

```bash
# 查看设备页面大小
adb shell getconf PAGE_SIZE
# 输出 4096 或 16384

# 检查 SO 是否兼容 16KB 页面
# 如果 LOAD 段的 p_align 小于 0x4000，可能不兼容
readelf -l libtarget.so | grep -E "LOAD|Align"
```

#### 3.10.3 更严格的隐式 Intent 限制

Android 14 要求隐式 Intent 必须指定目标组件的导出状态，未导出的组件不能通过隐式 Intent 启动。

#### 3.10.4 minSdkVersion 限制

Android 14 不允许安装 `minSdkVersion` 低于 23 (Android 6.0) 的 APK。

**对逆向影响**：
- 一些旧版逆向工具（如早期的 Xposed Installer）的 APK 无法安装
- 重打包时需要确保 `minSdkVersion >= 23`

```bash
# 查看 APK 的 minSdkVersion
aapt2 dump badging target.apk | grep sdkVersion
# 或
apktool d target.apk && grep minSdkVersion target/apktool.yml
```

---

### 3.11 Android 15 (V, API 35)

#### 3.11.1 16KB 页面大小全面支持

Android 15 将 16KB 页面大小从可选变为全面支持，所有新发布的设备和 SO 库都需要适配。

**必须适配的要点**：
- 所有 Native 库的 ELF 段必须按 16KB 对齐
- 使用 NDK r27+ 编译以确保兼容
- 旧的 SO 库可能无法在 16KB 页面设备上加载

```bash
# 检查 SO 是否兼容 16KB 页面
# 需要所有 LOAD 段的 p_align >= 0x4000
check_16kb_compat() {
    local so_file=$1
    readelf -l "$so_file" 2>/dev/null | grep "LOAD" | while read line; do
        align=$(echo "$line" | awk '{print $NF}')
        if [ "$align" != "0x4000" ] && [ "$align" != "0x10000" ]; then
            echo "[-] $so_file: 不兼容 16KB 页面 (align=$align)"
            return 1
        fi
    done
    echo "[+] $so_file: 兼容 16KB 页面"
}

# 批量检查应用中的所有 SO
for so in $(unzip -l target.apk | grep "\.so$" | awk '{print $4}'); do
    unzip -o target.apk "$so" -d /tmp/check_so/
    check_16kb_compat "/tmp/check_so/$so"
done
```

#### 3.11.2 MTE (Memory Tagging Extension) 生产可用

MTE 是 ARMv8.5-A 引入的硬件级内存安全特性，Android 15 将其推向生产可用状态。MTE 在指针的高位（Top Byte）存储一个 4-bit 的标签 (tag)，并在内存分配时为每个 16 字节的内存 granule 分配一个对应的标签。访问内存时，硬件自动检查指针标签与内存标签是否匹配。

```
# MTE 指针格式
指针值:    0x0B00007F12345678
              ^^
              ||-- 4-bit memory tag (值: 0x0B)
              |
           高位字节中的标签

# 内存布局:
地址:     0x7F12345670  0x7F12345680  0x7F12345690
标签:        [0B]           [0B]           [03]
             ↑ 匹配          ↑ 匹配         ↑ 不匹配 → 触发异常

# 影响所有基于指针的分析:
# 1. 读取指针值时需要 mask 掉 tag bits
# 2. 构造指针时需要设置正确的 tag
# 3. 内存扫描需要考虑 tagged pointer
```

**MTE 对逆向工程的影响**：

| 影响方面 | 详细说明 |
|:--------|:--------|
| 指针分析 | 所有指针高位包含 tag，直接使用会导致地址错误 |
| 内存 dump | dump 的指针值包含 tag，需要 mask 后才能使用 |
| Exploit 开发 | UAF 和堆溢出被硬件检测，利用难度大幅增加 |
| Hook 框架 | 需要正确处理 tagged pointer，否则 hook 可能失败 |
| 调试工具 | GDB/LLDB 需要支持 MTE 才能正确显示地址 |

```javascript
// Frida 中处理 MTE tagged pointer
function untagPointer(ptr) {
    // 移除高字节中的 MTE tag
    // ARM64 的 TBI (Top Byte Ignore) 允许高字节存储 tag
    var mask = ptr_size === 8
        ? ptr('0x00FFFFFFFFFFFFFF')
        : ptr('0xFFFFFFFF');
    return ptr.and(mask);
}

// 使用示例
Interceptor.attach(targetAddr, {
    onEnter: function(args) {
        var rawPtr = args[0];
        var cleanPtr = untagPointer(rawPtr);
        console.log('[*] Raw pointer: ' + rawPtr);
        console.log('[*] Clean pointer: ' + cleanPtr);
        console.log('[*] MTE tag: 0x' +
            rawPtr.shr(56).and(0xF).toString(16));
    }
});
```

#### 3.11.3 Privacy Sandbox

Privacy Sandbox 旨在替代广告追踪标识符（如 GAID），引入 Topics API、Attribution Reporting 等新机制。

**对逆向影响**：分析广告 SDK 和用户追踪机制时需要了解新的 Privacy Sandbox API。

#### 3.11.4 截屏检测 API

Android 15 引入了 `Activity.ScreenCaptureCallback`，允许应用检测用户截屏行为。

---

## 4. 逆向工具兼容性矩阵

下表展示了主流逆向工具在不同 Android 版本范围内的兼容性情况：

| 工具 | Android 7-9 | Android 10-12 | Android 13-15 | 关键适配点 |
|:-----|:----------:|:------------:|:------------:|:----------|
| **Frida** | ✅ | ✅ | ✅ (需适配) | XOM 绕过、SELinux 策略、MTE 兼容 |
| **Xposed (原版)** | ✅ | ❌ | ❌ | 仅支持 ART 5.0-8.1，已停止维护 |
| **LSPosed** | ❌ | ✅ | ✅ | 基于 Riru/Zygisk，需要 Magisk |
| **Magisk** | ✅ | ✅ | ✅ (需最新版) | 版本 24+ 改用 Zygisk 架构 |
| **objection** | ✅ | ✅ | ✅ | 基于 Frida，兼容性取决于 Frida |
| **apktool** | ✅ | ✅ | ✅ (v2.9+) | 需适配新资源格式和签名方案 |
| **jadx** | ✅ | ✅ | ✅ | Java/Kotlin 反编译无版本差异 |
| **IDA Pro** | ✅ | ✅ | ✅ | Native 层静态分析无版本差异 |
| **Ghidra** | ✅ | ✅ | ✅ | 同上，但需关注 16KB 页面对齐 |
| **r2/radare2** | ✅ | ✅ | ✅ | 同上 |

**工具版本建议**：

```bash
# 推荐的工具最低版本（截至 2025 年）
Frida:      >= 16.x     # 支持 Android 14/15 新特性
Magisk:     >= 26.x     # Zygisk 架构稳定版
LSPosed:    >= 1.9.x    # 最新 Zygisk 模块版本
apktool:    >= 2.9.x    # 支持新资源格式
objection:  >= 1.11.x   # 基于最新 Frida
```

---

## 5. APK 签名方案演进

APK 签名方案从 v1 到 v4 经历了四代演进，每一代都增强了安全性。

### 5.1 签名方案对比

| 方案 | 引入版本 | 签名范围 | 防篡改能力 | 重打包难度 |
|:-----|:--------|:--------|:---------|:---------|
| **v1** (JAR Signing) | 所有版本 | 仅 ZIP 条目 | 弱：可修改未签名条目 | 低 |
| **v2** (APK Sig Scheme) | Android 7.0+ | 整个 APK 文件 | 强：文件级完整性 | 中 |
| **v3** (Key Rotation) | Android 9.0+ | 整个 APK + 密钥轮换 | 强：支持证书链 | 中 |
| **v4** (Incremental) | Android 11+ | 增量安装验证 | 补充：仅用于安装优化 | 不影响 |

### 5.2 各方案详解

#### v1: JAR Signing

```
APK (ZIP 格式)
├── classes.dex          ← 签名覆盖
├── resources.arsc       ← 签名覆盖
├── res/                 ← 签名覆盖
├── lib/                 ← 签名覆盖
├── META-INF/
│   ├── MANIFEST.MF      ← 各文件 SHA 摘要
│   ├── CERT.SF          ← MANIFEST.MF 的签名
│   └── CERT.RSA         ← 证书 + 签名
└── assets/              ← 签名覆盖
```

**弱点**：
- 仅对 ZIP 条目进行独立签名
- 可以在不破坏签名的情况下在 ZIP 文件的注释区域添加数据
- 可以利用 ZIP 格式的特性绕过部分检查

#### v2: APK Signature Scheme v2

```
APK 文件结构 (v2 签名):
┌──────────────────────┐
│   ZIP 内容区          │  ← 签名保护区域 1
├──────────────────────┤
│   APK Signing Block  │  ← 包含 v2 签名数据
├──────────────────────┤
│   中央目录            │  ← 签名保护区域 2
├──────────────────────┤
│   中央目录结尾        │  ← 签名保护区域 3
└──────────────────────┘
```

v2 对 APK Signing Block 以外的所有区域计算摘要并签名，任何修改都会导致验证失败。

#### v3: Key Rotation

v3 在 v2 的基础上增加了密钥轮换支持，允许使用新证书签名同时保持与旧证书的信任链：

```
Signing Block 中的证书链:
  旧证书 A → 新证书 B → 当前证书 C
```

#### v4: Incremental Install

v4 签名主要用于 ADB 增量安装，生成独立的 `.idsig` 文件。

### 5.3 重打包工具和方法

```bash
# 1. 反编译
apktool d -r target.apk -o target_dir/  # -r 不解码资源（加速）

# 2. 修改代码/资源
# ... 修改 smali 代码 ...

# 3. 重新打包
apktool b target_dir/ -o modified_unsigned.apk

# 4. 对齐
zipalign -v 4 modified_unsigned.apk modified_aligned.apk

# 5. 签名（支持 v1+v2+v3）
apksigner sign \
    --ks my-release-key.jks \
    --ks-key-alias my-alias \
    --v1-signing-enabled true \
    --v2-signing-enabled true \
    --v3-signing-enabled true \
    modified_aligned.apk

# 6. 验证签名
apksigner verify --verbose --print-certs modified_aligned.apk
```

**签名验证绕过注意事项**：

```javascript
// 部分应用会在运行时校验签名，需要 hook 绕过
Java.perform(function() {
    // 方法 1: Hook PackageManager.getPackageInfo 替换签名
    var PackageManager = Java.use('android.app.ApplicationPackageManager');
    PackageManager.getPackageInfo.overload('java.lang.String', 'int')
        .implementation = function(packageName, flags) {
        // GET_SIGNATURES = 64, GET_SIGNING_CERTIFICATES = 0x08000000
        if ((flags & 64) !== 0 || (flags & 0x08000000) !== 0) {
            console.log('[*] Signature check intercepted for: ' + packageName);
        }
        return this.getPackageInfo(packageName, flags);
    };

    // 方法 2: 直接修改签名数据
    // 在内存中替换为原始签名的 byte array
});
```

---

## 6. ART 运行时演进

ART 运行时的演进直接影响了 DEX dump、方法 Hook 和代码追踪的技术路径。

### 6.1 演进时间线

```
Android 4.4     Android 5.0     Android 7.0      Android 12    Android 14+
    │               │               │                │             │
    ▼               ▼               ▼                ▼             ▼
  Dalvik         ART (AOT)    ART (AOT+JIT)    ART Mainline   ART + 16KB
  JIT 编译       纯 AOT 编译   混合编译          模块化更新      页面适配
                 dex2oat       Profile-Guided    独立 APEX
                               Compilation
```

### 6.2 编译模式演进

#### Dalvik JIT (Android 4.4 及更早)

```
DEX 字节码 → Dalvik VM 解释执行 → 热点代码 JIT 编译 → 缓存本地代码
```

- 每次启动重新解释
- JIT 编译结果不持久化

#### ART 纯 AOT (Android 5.0-6.0)

```
安装时: DEX → dex2oat → OAT 文件（完整 AOT 编译）
运行时: 直接执行 OAT 中的本地机器码
```

- 安装时间长（全量编译）
- 占用大量存储空间
- 运行性能好

#### ART 混合编译 (Android 7.0+)

```
安装时: DEX → 仅验证（不编译或仅编译关键路径）
首次运行: 解释执行 + JIT 编译热点代码
       → 生成 Profile 文件（.prof）
设备空闲: Profile-Guided AOT 编译
       → 仅编译 Profile 中标记的热点方法
后续运行: 热点代码 AOT 执行 + 冷代码解释/JIT
```

```bash
# 查看应用的 Profile 文件
adb shell ls -la /data/misc/profiles/cur/0/com.target.app/

# 查看编译状态
adb shell cmd package compile -m speed -f com.target.app  # 强制 AOT 编译
adb shell cmd package compile -m verify com.target.app     # 仅验证
adb shell cmd package compile --reset com.target.app       # 重置编译
```

#### Baseline Profiles (Android 12+)

开发者可以在 APK 中打包 Baseline Profile，指导 ART 在安装时预编译关键路径代码：

```
APK 中的 assets/dexopt/baseline.prof
  → 安装时 ART 读取 Profile
  → AOT 编译 Profile 中标记的方法
  → 首次启动即有优化代码可用
```

### 6.3 对逆向工程的影响

#### DEX Dump 策略

```javascript
// Frida DEX Dump (适用于所有 ART 版本)
// 原理: 从 ClassLoader 中获取 DexFile 对象，读取其内存中的 DEX 数据
Java.perform(function() {
    Java.enumerateClassLoaders({
        onMatch: function(loader) {
            try {
                var dexFiles = loader.findClass('java.lang.Object')
                    .getClassLoader().getClass()
                    .getSuperclass().getDeclaredField('pathList');
                dexFiles.setAccessible(true);
                // ... 遍历 DexPathList 获取 DEX 数据
            } catch(e) {}
        },
        onComplete: function() {}
    });
});
```

#### 方法 Hook 注意事项

```javascript
// Hook 时需要考虑方法的编译状态
// AOT 编译的方法: entry_point 指向 OAT 中的本地代码
// JIT 编译的方法: entry_point 指向 JIT 代码缓存
// 解释执行的方法: entry_point 指向解释器入口

// Frida 通过替换 ArtMethod 的 entry_point 实现 hook
// 这在所有编译状态下都有效
Java.perform(function() {
    var targetClass = Java.use('com.target.app.Crypto');
    targetClass.encrypt.implementation = function(data) {
        console.log('[*] encrypt called: ' + data);
        var result = this.encrypt(data);
        console.log('[*] encrypt result: ' + result);
        return result;
    };
});
```

### 6.4 ART 内部结构关键偏移

不同 Android 版本的 ART 内部结构（如 `ArtMethod`）偏移可能不同。编写底层 hook 工具时需要适配：

```c
// ArtMethod 结构 (简化版, 偏移因版本而异)
struct ArtMethod {
    uint32_t declaring_class_;      // GcRoot<Class>
    uint32_t access_flags_;
    uint32_t dex_code_item_offset_;
    uint32_t dex_method_index_;
    // ...
    void* entry_point_from_quick_compiled_code_;  // hook 目标
    void* data_;
};
```

```bash
# 使用 Frida 获取 ArtMethod 偏移信息
# 参考 frida-java-bridge 源码中的 art.js
```

---

## 7. Linker 演进与 SO 加载

Android 的动态链接器 (linker/linker64) 在各版本中经历了重大变化，直接影响 SO 注入和 hook 技术。

### 7.1 演进时间线

| 版本 | 变化 | 影响 |
|:-----|:-----|:-----|
| Android 6.0 及更早 | 全局 namespace，应用可加载任何 SO | 注入和 hook 无限制 |
| Android 7.0 | Linker namespace 引入 | 应用不能直接 `dlopen` 系统私有 SO |
| Android 8.0 | Treble vendor namespace | vendor SO 与 system SO 严格隔离 |
| Android 10 | BionicLinker 改进 | namespace 检查更严格 |
| Android 12 | Linkerconfig 动态生成 | namespace 配置从静态文件变为动态生成 |
| Android 14+ | 16KB 页面支持 | SO 加载需要适配新的页面对齐 |

### 7.2 Linker Namespace 详解

```
┌─────────────────────────────────────────────────────┐
│                 Linker Namespace 架构                │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌────────────────┐   ┌────────────────┐            │
│  │  default (系统)  │   │  classloader-  │           │
│  │  namespace      │   │  namespace     │           │
│  ├────────────────┤   ├────────────────┤            │
│  │ libandroid.so  │   │ app 的 JNI SO  │           │
│  │ libc.so        │   │ (lib/*.so)     │           │
│  │ libm.so        │   └───────┬────────┘           │
│  │ liblog.so      │           │                     │
│  │ ...            │←──── 只能 dlopen ────────       │
│  └────────────────┘     公开的 NDK 库               │
│                                                     │
│  ┌────────────────┐   ┌────────────────┐            │
│  │  vendor         │   │  vndk           │          │
│  │  namespace      │   │  namespace      │          │
│  ├────────────────┤   ├────────────────┤            │
│  │ vendor HAL SO  │   │ VNDK 共享库     │           │
│  │ /vendor/lib64/ │   │ /apex/vndk/    │           │
│  └────────────────┘   └────────────────┘            │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 7.3 查看 Namespace 配置

```bash
# Android 7.0-11: 静态配置文件
adb shell cat /system/etc/ld.config.txt

# Android 12+: 动态生成的配置
adb shell cat /linkerconfig/ld.config.txt

# 查看配置中的 namespace 定义
adb shell cat /linkerconfig/ld.config.txt | grep -E "^\[|^namespace\."

# 典型输出示例:
# [system]
# namespace.default.isolated = true
# namespace.default.search.paths = /system/lib64:/apex/com.android.art/lib64
# namespace.default.permitted.paths = /system/lib64:/apex/...
# namespace.default.asan.search.paths = ...
#
# [vendor]
# namespace.default.isolated = true
# namespace.default.search.paths = /vendor/lib64
```

### 7.4 绕过 Namespace 限制

```javascript
// Frida 中绕过 namespace 限制加载系统私有 SO
// 方法 1: 使用 Process.dlopen (Frida 内部实现绕过)
var handle = Module.load('/system/lib64/libinput.so');
console.log('[*] Loaded: ' + handle);

// 方法 2: 使用 android_dlopen_ext 指定 namespace
var android_dlopen_ext = new NativeFunction(
    Module.findExportByName('libdl.so', 'android_dlopen_ext'),
    'pointer', ['pointer', 'int', 'pointer']
);

// 方法 3: 通过 linker 内部函数直接操作 namespace
// 需要找到 linker 中的 do_dlopen 函数并 hook
```

### 7.5 Android 14+ 的 16KB 页面与 SO 加载

```bash
# 在 16KB 页面设备上，linker 对段对齐有严格要求
# SO 的 LOAD 段必须按 max(p_align, page_size) 对齐

# 如果 SO 的 p_align = 0x1000 但设备 page_size = 0x4000:
# linker 会尝试 compat 模式加载（可能失败）
# 或者直接拒绝加载

# 使用 NDK r27+ 重新编译 SO 以确保兼容:
# CMakeLists.txt 中添加:
# set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -Wl,-z,max-page-size=16384")
```

---

## 8. 实战建议：根据目标 Android 版本制定分析策略

> **💡 思路一句话**: 拿到目标 App 后，第一步看 `minSdkVersion` 和 `targetSdkVersion` 确定版本范围 → 根据版本选择对应的工具链和绕过方案 → 版本越高限制越多，但核心逆向方法论不变。

### 8.1 版本识别与环境评估

在开始分析前，首先收集目标设备的完整信息：

```bash
# 1. 基础信息收集
echo "=== Android 版本 ==="
adb shell getprop ro.build.version.release
adb shell getprop ro.build.version.sdk

echo "=== 安全补丁 ==="
adb shell getprop ro.build.version.security_patch

echo "=== 设备架构 ==="
adb shell getprop ro.product.cpu.abi

echo "=== SELinux 状态 ==="
adb shell getenforce

echo "=== Root 状态 ==="
adb shell su -c "id" 2>/dev/null || echo "未 root"

echo "=== 页面大小 ==="
adb shell getconf PAGE_SIZE

echo "=== Magisk 版本 ==="
adb shell su -c "magisk -v" 2>/dev/null || echo "无 Magisk"

echo "=== Kernel 版本 ==="
adb shell uname -r
```

### 8.2 分析策略决策流程

```
                    ┌─────────────────┐
                    │  确认 Android 版本  │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        Android 5-6     Android 7-9    Android 10+
              │              │              │
              ▼              ▼              ▼
        传统方案即可     需要处理:        需要处理:
        ・直接抓包      ・证书信任       ・XOM 绕过
        ・原版 Xposed   ・namespace     ・Scoped Storage
        ・简单重打包    ・Hidden API     ・16KB 页面 (14+)
                        ・v2 签名        ・MTE (15)
                             │              │
                             ▼              ▼
                        工具选择:        工具选择:
                        ・Frida         ・Frida (最新版)
                        ・LSPosed       ・LSPosed + Zygisk
                        ・Magisk        ・Magisk 26+
                        ・apktool       ・apktool 2.9+
```

### 8.3 各版本范围的推荐方案

#### Android 5.0-6.0 (API 21-23)

```bash
# 抓包: 直接安装证书即可
# 安装代理证书
adb push burp-cert.pem /sdcard/
# 设备上: 设置 → 安全 → 从存储安装证书

# Hook: Xposed 或 Frida 均可
# 安装 Xposed Framework (5.0-6.0 最后的稳定版)
# 或使用 Frida
frida -U -f com.target.app -l hook.js
```

#### Android 7.0-9.0 (API 24-28)

```bash
# 抓包: 需要处理证书信任
# 方案 A: 重打包添加网络安全配置
apktool d target.apk -o target_dir/
# 编辑 network_security_config.xml (信任用户证书)
apktool b target_dir/ -o modified.apk
apksigner sign --ks key.jks modified.apk

# 方案 B: Magisk + MoveCert 模块 (推荐)
# 安装 Magisk → 安装 MagiskTrustUserCerts 模块 → 重启

# Hook: 使用 Frida + LSPosed
# Hidden API 绕过 (Android 9.0):
adb shell settings put global hidden_api_policy 1
```

#### Android 10-12 (API 29-32)

```bash
# 抓包: Magisk + MoveCert (必须)
# + Frida SSL Pinning Bypass (如果应用使用 Certificate Pinning)

# Hook: Frida (最新版) + Magisk (24+)
# 注意 XOM: Frida 默认通过 ptrace 绕过，通常无需额外处理
# 注意 Scoped Storage: dump 文件使用应用私有目录

# 调试: 使用 Frida 而非 JDWP
# Android 12 的调试限制使 JDWP 更难用
frida -U -f com.target.app -l hook.js --no-pause
```

#### Android 13-15 (API 33-35)

```bash
# 抓包: Magisk + MoveCert + Frida SSL Bypass (完整方案)

# Hook: Frida 16.x + Magisk 26.x + LSPosed (Zygisk)
# 确认设备页面大小
adb shell getconf PAGE_SIZE

# 如果是 16KB 页面设备，注意:
# - 自定义 SO 注入可能因对齐问题失败
# - 使用 NDK r27+ 编译注入用的 SO

# MTE 检查 (Android 15):
adb shell cat /proc/cpuinfo | grep -i mte
# 如果设备支持 MTE，分析内存时需要 mask 指针 tag
```

### 8.4 常见问题排查

| 问题现象 | 可能原因 | 解决方案 |
|:--------|:--------|:--------|
| Frida 注入后 app 闪退 | Frida 检测/SELinux | 使用 Frida 检测绕过脚本/关闭 SELinux |
| 抓不到 HTTPS 流量 | 证书不信任 (7.0+) | MoveCert 模块 + SSL Pinning Bypass |
| 反射调用抛异常 | Hidden API 限制 (9.0+) | 双重反射绕过或 adb 设置 |
| SO 无法 dlopen | Namespace 限制 (7.0+) | 使用 Frida 的 Module.load 或修改 namespace |
| 内存 dump 全零 | XOM 保护 (10+) | 使用 Frida (ptrace) 读取 |
| SO 加载崩溃 | 16KB 页面对齐 (14+) | 重新编译 SO 适配新对齐 |
| 指针地址异常 | MTE tagged pointer (15) | mask 掉高字节的 tag bits |
| app 检测到 root | SafetyNet/Play Integrity | MagiskHide/Shamiko 模块 |

---

## 9. 相关链接

本站相关文档：

- [Android 运行时 (ART) 深度解析]({{< ref "art_runtime.md" >}}) - ART 运行时内部机制详解
- [SELinux 安全机制]({{< ref "selinux.md" >}}) - SELinux 策略分析与绕过
- [Android .so 文件详解 (ELF Format)]({{< ref "so_elf_format.md" >}}) - ELF 格式与 SO 分析基础
- [DEX 文件格式]({{< ref "dex_format.md" >}}) - DEX 字节码格式详解
- [APK 结构详解]({{< ref "apk_structure.md" >}}) - APK 文件组成与解析
- [Smali 语法参考]({{< ref "smali_syntax.md" >}}) - Smali 汇编语法
- [Binder IPC 机制]({{< ref "binder_ipc.md" >}}) - Android 进程间通信机制
- [ARM 汇编基础]({{< ref "arm_assembly.md" >}}) - ARM/ARM64 汇编指令参考
- [Magisk 与 LSPosed 原理]({{< ref "../Advanced/magisk_lsposed_internals.md" >}}) - Root 框架内部实现
- [SO 反调试与混淆]({{< ref "../Advanced/so_anti_debugging_and_obfuscation.md" >}}) - Native 层保护机制分析

外部资源：

- [Android 安全公告](https://source.android.com/docs/security/bulletin) - 官方安全更新信息
- [Android 版本发行说明](https://developer.android.com/about/versions) - 各版本新特性官方文档
- [Frida 官方文档](https://frida.re/docs/) - Frida 使用和 API 参考
- [Magisk 官方仓库](https://github.com/topjohnwu/Magisk) - Magisk 源码与发布
- [LSPosed 官方仓库](https://github.com/LSPosed/LSPosed) - LSPosed 框架
