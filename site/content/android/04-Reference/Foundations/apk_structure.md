---
title: "APK 文件结构详解"
date: 2025-12-25
weight: 10
---

# APK 文件结构详解

APK (Android Package) 是 Android 操作系统用于分发和安装移动应用的文件格式。它本质上是一个 ZIP 归档文件，包含了应用的所有代码、资源、证书等。理解其内部结构是逆向工程和安全分析的第一步。

## 目录

1. [APK 概览](#apk-概览)
2. [AndroidManifest.xml](#androidmanifestxml)
3. [classes.dex](#classesdex)
4. [resources.arsc](#resourcesarsc)
5. [res/ 目录](#res-目录)
6. [lib/ 目录](#lib-目录)
7. [assets/ 目录](#assets-目录)
8. [META-INF/ 目录](#meta-inf-目录)
9. [APK 分析流程](#apk-分析流程)

---

## APK 概览

一个标准的 APK 文件，当用解压缩工具打开时，通常会看到以下目录结构：

```
app.apk
├── AndroidManifest.xml   # [必需] 应用清单文件（二进制格式）
├── classes.dex           # [必需] Dalvik/ART 字节码
├── classes2.dex          # [可选] 多 DEX 文件
├── resources.arsc        # [必需] 预编译资源索引表
├── res/                  # [必需] 未编译的资源目录
│   ├── drawable/         # 图片资源
│   ├── layout/           # 布局 XML
│   ├── values/           # 字符串、颜色等值资源
│   └── ...
├── lib/                  # [可选] 原生库目录
│   ├── arm64-v8a/        # 64位 ARM
│   ├── armeabi-v7a/      # 32位 ARM
│   ├── x86/              # 32位 x86
│   └── x86_64/           # 64位 x86
├── assets/               # [可选] 原始资源文件
└── META-INF/             # [必需] 签名信息
    ├── MANIFEST.MF
    ├── CERT.SF
    └── CERT.RSA
```

---

## AndroidManifest.xml

这是 APK 中最重要的文件，它以二进制 XML 格式存储，包含了应用的所有元信息。

### 核心内容

| 元素 | 说明 |
|------|------|
| 包名 (Package Name) | 应用在系统中的唯一标识符，如 `com.example.app` |
| 组件 (Components) | 声明所有四大组件：Activity、Service、BroadcastReceiver、ContentProvider |
| 权限 (Permissions) | 声明应用需要申请的权限，如 `android.permission.INTERNET` |
| 入口点 (Entry Point) | 指定哪个 Activity 是应用的启动入口（LAUNCHER Activity） |
| SDK 版本 | 指定 minSdkVersion、targetSdkVersion |

### 四大组件

```xml
<!-- Activity: 用户界面 -->
<activity android:name=".MainActivity" android:exported="true">
    <intent-filter>
        <action android:name="android.intent.action.MAIN" />
        <category android:name="android.intent.category.LAUNCHER" />
    </intent-filter>
</activity>

<!-- Service: 后台服务 -->
<service android:name=".MyService" android:exported="false" />

<!-- BroadcastReceiver: 广播接收器 -->
<receiver android:name=".MyReceiver">
    <intent-filter>
        <action android:name="android.intent.action.BOOT_COMPLETED" />
    </intent-filter>
</receiver>

<!-- ContentProvider: 内容提供者 -->
<provider android:name=".MyProvider"
          android:authorities="com.example.app.provider"
          android:exported="false" />
```

**分析提示**: 必须使用 `apktool` 或 `jadx` 等工具将其解码为人类可读的 XML 格式。直接用文本编辑器打开是乱码。

---

## classes.dex

这是由 Java/Kotlin 代码编译、转换后生成的 Dalvik 虚拟机字节码。应用的所有业务逻辑都在这里。

### DEX 文件特点

| 特性 | 说明 |
|------|------|
| 格式 | Dalvik Executable，专为移动设备优化 |
| 方法数限制 | 单个 DEX 文件最多 65536 个方法 |
| 多 DEX | 超过限制时会有 `classes2.dex`, `classes3.dex` 等 |
| 字节码 | 基于寄存器的指令集，比 JVM 字节码更紧凑 |

### 分析工具

```bash
# 使用 jadx 反编译为 Java 代码
jadx -d output/ app.apk

# 使用 baksmali 反汇编为 Smali 代码
baksmali d classes.dex -o smali_output/

# 使用 dex2jar 转换为 JAR
d2j-dex2jar.sh classes.dex
```

**分析提示**: 使用 `jadx` 可以将其反编译为 Java 代码，使用 `baksmali` 可以反汇编为 Smali 代码。

---

## resources.arsc

这是一个二进制资源索引表。Android 系统使用它来快速查找和匹配资源。

### 功能说明

- 包含从资源 ID 到具体资源文件（或字符串值）的映射关系
- 支持多语言、多屏幕密度等资源适配
- 当代码中调用 `R.string.app_name` 时，系统通过此文件找到对应的字符串值

### 资源 ID 格式

```
0x7f010001
│  │  │
│  │  └── 资源项 ID (0001)
│  └──── 资源类型 (01 = attr, 02 = drawable, 03 = layout, 04 = string...)
└────── 包 ID (7f = 应用本身, 01 = 系统资源)
```

**分析提示**: `apktool` 可以解码此文件，将其中的字符串等资源还原到 `res/values/strings.xml` 等文件中。

---

## res/ 目录

存放**未编译**的资源文件，这些资源在打包时大多保持原样或只进行简单处理。

### 目录结构

| 目录 | 内容 |
|------|------|
| `res/drawable/` | 图片资源（PNG, JPG, WebP, XML drawable） |
| `res/layout/` | 布局 XML 文件 |
| `res/values/` | 字符串、颜色、尺寸等值资源 |
| `res/xml/` | 任意 XML 配置文件 |
| `res/raw/` | 任意原始二进制文件 |
| `res/mipmap/` | 应用图标资源 |
| `res/anim/` | 动画定义文件 |

### 资源限定符

```
res/
├── drawable/           # 默认资源
├── drawable-hdpi/      # 高密度屏幕
├── drawable-xhdpi/     # 超高密度屏幕
├── drawable-xxhdpi/    # 超超高密度屏幕
├── values/             # 默认语言
├── values-zh/          # 中文
└── values-ja/          # 日文
```

**分析提示**: 布局 XML 文件虽然可读，但它们引用的字符串等资源是以 `@string/app_name` 的形式存在的，需要结合 `resources.arsc` 才能完全理解。

---

## lib/ 目录

存放应用使用的 C/C++ 原生库（`.so` 文件）。为了适配不同的 CPU 架构，它通常包含多个子目录。

### 架构说明

| 目录 | 架构 | 说明 |
|------|------|------|
| `arm64-v8a/` | 64位 ARM | 目前主流 Android 设备 |
| `armeabi-v7a/` | 32位 ARM | 较老的 ARM 设备 |
| `x86_64/` | 64位 x86 | 模拟器、Intel 设备 |
| `x86/` | 32位 x86 | 模拟器、Intel 设备 |

### 常见原生库

```
lib/arm64-v8a/
├── libnative-lib.so      # 应用自定义原生库
├── libflutter.so         # Flutter 引擎
├── libil2cpp.so          # Unity IL2CPP
├── libcrypto.so          # OpenSSL 加密库
└── libsqlcipher.so       # SQLCipher 加密数据库
```

**分析提示**: 核心的加密、解密、核心算法或游戏引擎常常在这里实现。需要使用 IDA Pro、Ghidra、Binary Ninja 等工具进行逆向分析。

---

## assets/ 目录

这是一个"原封不动"的资源目录。与 `res/raw` 类似，这里的任何文件在打包时都不会被系统处理。

### 常见用途

| 类型 | 示例 |
|------|------|
| 配置文件 | `config.json`, `settings.xml` |
| Web 资源 | `index.html`, `app.js`, `style.css` |
| 游戏资源 | 地图数据、关卡配置、精灵图 |
| 字体文件 | `custom_font.ttf` |
| 数据库 | 预置的 SQLite 数据库 |
| 加密数据 | 加密的配置或密钥文件 |

**分析提示**: 检查此目录是否有敏感的配置文件、密钥或 Web 资源。

---

## META-INF/ 目录

存放应用的签名信息，用于验证 APK 的完整性和来源。

### 文件说明

| 文件 | 说明 |
|------|------|
| `MANIFEST.MF` | 包含 APK 中每个文件的名称及其 SHA-256 哈希值 |
| `CERT.SF` | APK 中每个文件的摘要（哈希值） |
| `CERT.RSA` | 包含用于签署 `CERT.SF` 的公钥和证书 |

### 签名机制

```
1. 计算 APK 中每个文件的哈希 → 记录在 MANIFEST.MF
                    │
                    ▼
2. 计算 MANIFEST.MF 整个文件的哈希 → 记录在 CERT.SF
                    │
                    ▼
3. 用开发者私钥对 CERT.SF 签名 → 生成 CERT.RSA
```

当系统安装 APK 时，会用 `CERT.RSA` 中的公钥来验证签名，确保文件自签名后未被篡改。

### APK 签名方案

| 版本 | 说明 |
|------|------|
| v1 (JAR 签名) | 传统签名方式，基于 META-INF 目录 |
| v2 (APK 签名块) | Android 7.0+，签名信息存储在 APK 签名块中 |
| v3 (APK 签名块 + 密钥轮换) | Android 9.0+，支持密钥轮换 |
| v4 (增量签名) | Android 11+，支持增量安装 |

**分析提示**: 对 APK 进行任何修改（包括重打包）后，都必须用自己的密钥重新签名，否则安装会失败。

---

## APK 分析流程

### 1. 解包

```bash
# 推荐：使用 apktool 解包（正确解码 XML 和资源）
apktool d app.apk -o app_decoded/

# 备选：直接解压（不解码二进制 XML）
unzip app.apk -d app_unzipped/
```

### 2. 静态分析

```bash
# 使用 jadx-gui 打开，直接浏览反编译的 Java 代码
jadx-gui app.apk

# 命令行批量反编译
jadx -d java_output/ app.apk
```

**检查清单**:
- 阅读 `AndroidManifest.xml`，了解主要组件、权限和入口点
- 检查 `assets/` 目录，寻找配置文件或敏感数据
- 检查 `lib/` 目录，识别使用的原生库
- 搜索硬编码的密钥、URL、API 端点

### 3. 动态分析

```bash
# 安装应用
adb install app.apk

# 使用 Frida 进行 Hook
frida -U -f com.example.app -l hook_script.js

# 使用 objection 快速分析
objection -g com.example.app explore
```

### 4. 重打包（修改后）

```bash
# 使用 apktool 重新打包
apktool b app_decoded/ -o app_modified.apk

# 签名
apksigner sign --ks my.keystore app_modified.apk

# 或使用 jarsigner
jarsigner -keystore my.keystore app_modified.apk alias_name

# 对齐优化
zipalign -v 4 app_modified.apk app_aligned.apk
```

---

## 总结

| 文件/目录 | 分析重点 |
|-----------|----------|
| AndroidManifest.xml | 组件、权限、入口点、导出状态 |
| classes.dex | 业务逻辑、加密算法、网络请求 |
| lib/*.so | 核心算法、加密实现、反调试 |
| assets/ | 配置文件、密钥、Web 资源 |
| META-INF/ | 签名信息、证书 |

掌握 APK 文件结构是 Android 逆向工程的基础。通过系统地分析每个组成部分，可以全面了解应用的功能和实现细节。
