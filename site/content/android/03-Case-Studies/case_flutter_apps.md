---
title: "Flutter 应用逆向案例"
date: 2025-02-27
type: posts
tags: ["Native层", "Flutter", "代理池", "Frida", "案例分析", "SSL Pinning"]
weight: 10
---

# Flutter 应用逆向案例

> **📚 前置知识**
>
> 本案例涉及以下核心技术，建议先阅读相关章节：
>
> - **[SO/ELF 格式](../04-Reference/Foundations/so_elf_format.md)** - 理解 libapp.so 的结构与 Snapshot 格式
> - **[Frida Native Hook](../02-Tools/Dynamic/frida_guide.md#native-hook)** - 对 Dart 编译后的函数进行运行时 Hook

Flutter 是 Google 推出的跨平台 UI 框架，它使用 Dart 语言开发。与传统的 Android App (Java/Kotlin) 或 Unity (C#) 不同，Release 模式下的 Flutter 应用将 Dart 代码预编译 (AOT) 成了原生机器码，打包在 `libapp.so` 中，这使得逆向难度大大增加。

---

## 目录

- [Flutter 架构与逆向挑战](#flutter-架构与逆向挑战)
- [Flutter App 识别](#flutter-app-识别)
- [Dart 快照格式分析](#dart-快照格式分析)
- [reFlutter 工具使用](#reflutter-工具使用)
- [Frida 拦截 Flutter 网络请求](#frida-拦截-flutter-网络请求)
- [Flutter 逆向工具链](#flutter-逆向工具链)
- [libapp.so 分析技巧](#libappso-分析技巧)
- [实战：Flutter App 抓包](#实战flutter-app-抓包)
- [实战：提取 Flutter App 业务逻辑](#实战提取-flutter-app-业务逻辑)
- [常见问题与解决方案](#常见问题与解决方案)

---

## Flutter 架构与逆向挑战

### 核心架构概览

Flutter 应用的运行架构与传统 Android 应用截然不同。理解其内部结构是逆向的第一步。

```
+---------------------------------------------------------------+
|                     Flutter Application                       |
+---------------------------------------------------------------+
|                                                               |
|  +---------------------------+  +---------------------------+ |
|  |      Dart Framework       |  |     Developer Code        | |
|  |  (Material, Cupertino,    |  |  (业务逻辑、UI、网络)       | |
|  |   Widgets, Rendering)     |  |                           | |
|  +---------------------------+  +---------------------------+ |
|              |                            |                   |
|              v                            v                   |
|  +-------------------------------------------------------+   |
|  |              Dart AOT Compiled Code                    |   |
|  |                  ( libapp.so )                         |   |
|  +-------------------------------------------------------+   |
|              |                                                |
|              v                                                |
|  +-------------------------------------------------------+   |
|  |              Flutter Engine (C/C++)                    |   |
|  |                ( libflutter.so )                       |   |
|  |  +----------+  +-----------+  +---------------------+ |   |
|  |  | Dart VM  |  |   Skia    |  |   Platform Channel  | |   |
|  |  | Runtime  |  | (渲染引擎) |  |   (与原生通信)       | |   |
|  |  +----------+  +-----------+  +---------------------+ |   |
|  +-------------------------------------------------------+   |
|              |                                                |
|              v                                                |
|  +-------------------------------------------------------+   |
|  |              Android Platform (Java/Kotlin)            |   |
|  |      FlutterActivity / FlutterFragment (薄壳层)         |   |
|  +-------------------------------------------------------+   |
+---------------------------------------------------------------+
```

### 关键文件

| 文件 | 说明 | 逆向价值 |
|------|------|----------|
| `lib/<abi>/libflutter.so` | Flutter 引擎，包含 Dart VM、Skia 渲染引擎、BoringSSL | 用于 Hook 网络层 / SSL 验证 |
| `lib/<abi>/libapp.so` | 开发者 Dart 代码的 AOT 编译产物 | **核心目标** — 所有业务逻辑在此 |
| `assets/flutter_assets/` | 字体、图片、Shader 等资源 | 辅助理解 UI |
| `assets/flutter_assets/kernel_blob.bin` | Debug 模式下的 Dart Kernel（Release 不存在） | 若存在则可直接反编译 |

### Dart AOT 编译流程

```
  Dart 源代码 (.dart)
        |
        v
  [ Dart Frontend (CFE) ]
        |
        v
  Kernel Binary (.dill)        <-- Debug 模式到此为止 (JIT)
        |
        v
  [ AOT Compiler (gen_snapshot) ]
        |
        v
  +-----+---------------------------+
  |     |                           |
  v     v                           v
 指令段 (Text)    数据段 (Data)     快照 (Snapshot)
  机器码           全局对象         类/函数元数据
        |                           |
        +---------------------------+
                    |
                    v
              libapp.so             <-- Release 模式最终产物
```

**关键点**：

1. **没有 Java 字节码**：Flutter 的 Dart 代码不经过 DEX 编译，Java 层只有一个薄壳 `FlutterActivity`，所有逻辑在 Native 层。
2. **自有网络栈**：Dart 自带 HTTP 客户端和 BoringSSL，不走 Android 系统的 `java.net` 或 OkHttp。
3. **无标准符号表**：`libapp.so` 虽然是 ELF 格式，但函数名被剥离，无法直接通过符号定位函数。
4. **自定义调用约定**：Dart AOT 代码使用自己的寄存器约定和调用规范，与标准 ARM ABI 不同。

### 为什么传统 Hook 方法失效

| 传统方法 | 对 Flutter 的效果 | 原因 |
|----------|------------------|------|
| Xposed Hook Java 方法 | 无效 | 业务逻辑不在 Java 层 |
| JADX 反编译 DEX | 仅能看到空壳 Activity | Dart 代码在 libapp.so 中 |
| Wi-Fi 代理 + Burp | 无效 | Dart HttpClient 不走系统代理 |
| 通用 SSL Pinning Bypass (OkHttp) | 无效 | Flutter 使用 BoringSSL，不走 Java TLS |
| Frida Hook `javax.net.ssl` | 无效 | 同上 |

---

## Flutter App 识别

在动手逆向之前，我们首先需要确认目标应用是否使用了 Flutter 框架。

### 方法一：检查 APK 内部文件结构

解压 APK，检查以下特征文件：

```bash
# 解压 APK 并检查关键文件
unzip -l target.apk | grep -E "(libflutter|libapp|flutter_assets)"
```

**典型 Flutter APK 文件结构**:

```
target.apk
├── AndroidManifest.xml
├── classes.dex                    # Java 薄壳层
├── lib/
│   ├── arm64-v8a/
│   │   ├── libflutter.so          # <-- Flutter 引擎
│   │   └── libapp.so              # <-- Dart AOT 代码
│   └── armeabi-v7a/
│       ├── libflutter.so
│       └── libapp.so
├── assets/
│   └── flutter_assets/            # <-- Flutter 资源目录
│       ├── AssetManifest.json
│       ├── FontManifest.json
│       ├── fonts/
│       ├── packages/
│       └── shaders/
└── res/
```

### 方法二：检查 AndroidManifest.xml

Flutter 应用的 `AndroidManifest.xml` 中通常有以下特征：

```xml
<!-- Flutter 应用的典型 Activity 声明 -->
<activity
    android:name="io.flutter.embedding.android.FlutterActivity"
    android:launchMode="singleTop"
    android:hardwareAccelerated="true"
    android:windowSoftInputMode="adjustResize">
</activity>

<!-- 或者自定义 Activity 继承 FlutterActivity -->
<activity android:name=".MainActivity" ... >
    <!-- 内部会引用 Flutter 引擎 -->
</activity>
```

可以搜索以下关键字：

```bash
# 在 Manifest 中搜索 Flutter 关键字
aapt dump xmltree target.apk AndroidManifest.xml | grep -i "flutter"
```

### 方法三：运行时检测 (adb)

```bash
# 方法 1: 检查已加载的 SO 库
adb shell "cat /proc/$(pidof com.target.app)/maps | grep flutter"

# 预期输出:
# 7a3c000000-7a3c200000 r-xp ... /data/app/.../lib/arm64/libflutter.so
# 7a3d000000-7a3d100000 r-xp ... /data/app/.../lib/arm64/libapp.so

# 方法 2: 检查包名目录下的 SO 文件
adb shell "ls -la /data/app/~~*/com.target.app-*/lib/arm64/"
```

### 方法四：自动化脚本识别

```python
#!/usr/bin/env python3
"""Flutter App 快速识别脚本"""
import zipfile
import sys

def is_flutter_app(apk_path):
    indicators = {
        "libflutter.so": False,
        "libapp.so": False,
        "flutter_assets": False,
    }

    with zipfile.ZipFile(apk_path, 'r') as z:
        for name in z.namelist():
            if "libflutter.so" in name:
                indicators["libflutter.so"] = True
            if "libapp.so" in name:
                indicators["libapp.so"] = True
            if "flutter_assets" in name:
                indicators["flutter_assets"] = True

    score = sum(indicators.values())
    print(f"[*] 检测结果: {apk_path}")
    for k, v in indicators.items():
        status = "Found" if v else "Missing"
        print(f"    {k}: {status}")

    if score >= 2:
        print(f"[+] 结论: 高度确认为 Flutter 应用 (命中 {score}/3)")
    elif score == 1:
        print(f"[?] 结论: 可能为 Flutter 应用 (命中 {score}/3)")
    else:
        print(f"[-] 结论: 非 Flutter 应用")

    return score >= 2

if __name__ == "__main__":
    is_flutter_app(sys.argv[1])
```

### Flutter 版本识别

确认应用是 Flutter 后，还需要识别其使用的 Flutter 版本，这对后续选择工具至关重要：

```bash
# 从 libflutter.so 中提取版本信息
strings libflutter.so | grep -E "Flutter [0-9]+\.[0-9]+"

# 或者搜索 Dart SDK 版本
strings libflutter.so | grep -E "Dart.*[0-9]+\.[0-9]+\.[0-9]+"

# 通过 snapshot hash 判断版本
strings libapp.so | head -20
```

---

## Dart 快照格式分析

理解 Dart Snapshot 格式是深入逆向 Flutter 的基础。`libapp.so` 的核心就是一个 Dart VM Snapshot。

### Snapshot 结构概览

```
libapp.so (ELF)
├── .text           # 机器码指令段
├── .rodata         # 只读数据
├── _kDartVmSnapshotData        # VM 级别快照数据 (类型系统等)
├── _kDartVmSnapshotInstructions    # VM 内部 Stub 代码
├── _kDartIsolateSnapshotData       # Isolate 快照数据 (对象、常量)
└── _kDartIsolateSnapshotInstructions   # Isolate 代码 (开发者代码)
```

这四个符号在 `libapp.so` 中是始终存在的（即使其他符号被剥离），它们分别代表：

| 符号 | 内容 | 逆向价值 |
|------|------|----------|
| `_kDartVmSnapshotData` | Dart 类型系统、核心类定义 | 还原类型信息 |
| `_kDartVmSnapshotInstructions` | VM 内部运行时 Stub | 一般不需要分析 |
| `_kDartIsolateSnapshotData` | 对象池、常量表、库列表 | **核心** — 类/函数元数据 |
| `_kDartIsolateSnapshotInstructions` | 所有 AOT 编译的函数代码 | **核心** — 可执行代码 |

### Snapshot 数据段内部结构

Isolate Snapshot Data 的内部布局（简化）：

```
+----------------------------------+
|         Snapshot Header          |
|  - Magic Number                  |
|  - Snapshot Kind                 |
|  - Version Hash                  |  <-- 与 Flutter/Dart 版本强绑定
+----------------------------------+
|        Object Store / Pool       |
|  +----------------------------+  |
|  | Object #0: Null            |  |
|  | Object #1: Bool (true)     |  |
|  | Object #2: Smi (42)        |  |
|  | Object #3: String "hello"  |  |
|  | Object #4: Array [...]     |  |
|  | ...                        |  |
|  +----------------------------+  |
+----------------------------------+
|         Class Table              |
|  - ClassId -> Class Descriptor   |
|  - 字段数量、类型、偏移            |
|  - 父类引用                      |
+----------------------------------+
|        Library Table             |
|  - Library URI (如 package:app/) |
|  - 导出的类和函数列表              |
+----------------------------------+
|       Code / Function Table      |
|  - FunctionName -> Code Offset   |  <-- 函数名到指令偏移的映射
|  - Entry Point Table             |
+----------------------------------+
|     Dispatch Table (新版本)       |
|  - Selector ID -> Code Offset    |
+----------------------------------+
```

### 版本兼容性问题

Dart Snapshot 格式 **没有向后兼容性保证**。每个 Dart SDK 版本都可能改变 Snapshot 的内部格式。这意味着：

```
Dart SDK 2.17 生成的 Snapshot  ≠  Dart SDK 2.18 的格式
Dart SDK 3.0  生成的 Snapshot  ≠  Dart SDK 3.1  的格式
```

> **关键影响**：所有解析 Snapshot 的逆向工具（Doldrums、Blutter、darter 等）都必须与目标 App 的 Dart SDK 版本匹配，否则无法正确解析。

### 手动定位 Snapshot 入口

使用 `readelf` 找到关键符号的地址：

```bash
# 列出 libapp.so 中的动态符号
readelf -s libapp.so | grep -i "snapshot"

# 预期输出:
# 1: 0000000000001000  5242880 OBJECT GLOBAL DEFAULT  _kDartVmSnapshotInstructions
# 2: 0000000000501000  2097152 OBJECT GLOBAL DEFAULT  _kDartIsolateSnapshotInstructions
# 3: 0000000000701000   524288 OBJECT GLOBAL DEFAULT  _kDartVmSnapshotData
# 4: 0000000000781000  1048576 OBJECT GLOBAL DEFAULT  _kDartIsolateSnapshotData
```

---

## reFlutter 工具使用

**reFlutter** 是目前最强大的 Flutter 逆向辅助工具。它通过修改 Flutter 引擎 (`libflutter.so`)，在应用运行时利用 Dart VM 的内部机制来 Dump 类、函数和偏移信息。

**工具地址**: [reFlutter](https://github.com/Impact-I/reFlutter)

### 安装

```bash
# 通过 pip 安装
pip3 install reflutter

# 验证安装
reflutter --help
```

### 基本使用流程

```
+------------------+       +------------------+       +------------------+
|  原始 APK        | ----> |   reFlutter      | ----> |  Patched APK     |
|  (target.apk)    |       |   (替换引擎)      |       | (release.RE.apk) |
+------------------+       +------------------+       +------------------+
                                                              |
                                                              v
                                                     +------------------+
                                                     |  安装到手机运行    |
                                                     +------------------+
                                                              |
                                          +-------------------+-------------------+
                                          |                                       |
                                          v                                       v
                                 +------------------+                    +------------------+
                                 |  dump.dart       |                    |  流量转发到代理    |
                                 |  (函数偏移表)     |                    |  (绕过SSL Pinning)|
                                 +------------------+                    +------------------+
```

### 操作步骤

```bash
# 第 1 步: 运行 reFlutter 处理 APK
reflutter target.apk

# 交互过程中选择:
# 1) Traffic monitoring and interception  <-- 流量拦截
# 2) Socket trace                         <-- Socket 追踪
#
# 选择 1 后输入代理 IP (如 Burp 监听的 IP):
# Enter your Burp Suite IP: 192.168.1.100
```

```bash
# 第 2 步: 签名 Patched APK
# reFlutter 输出的 APK 未签名，需要重新签名
apksigner sign --ks my-key.keystore \
    --ks-pass pass:password \
    release.RE.apk

# 或使用 uber-apk-signer
java -jar uber-apk-signer.jar -a release.RE.apk
```

```bash
# 第 3 步: 安装运行
adb install release.RE.apk

# 第 4 步: 启动应用并监控 Logcat
adb logcat -s flutter

# 第 5 步: 获取 dump.dart 文件
adb pull /data/data/com.target.app/dump.dart .
```

### dump.dart 解读

`dump.dart` 是 reFlutter 导出的函数偏移表，格式如下：

```dart
// dump.dart 示例内容
Library:'package:http/http.dart'
    Class: Client  extends Object {
        Function 'get':. String url  {
              Code Coverage: _kDartIsolateSnapshotInstructions + 0x29a4c0
        }
        Function 'post':. String url, Map<String, String> headers, Object body {
              Code Coverage: _kDartIsolateSnapshotInstructions + 0x29a690
        }
    }

Library:'package:target_app/services/api_service.dart'
    Class: ApiService  extends Object {
        Function 'login':. String username, String password {
              Code Coverage: _kDartIsolateSnapshotInstructions + 0x3a1200
        }
        Function 'fetchUserData':. int userId {
              Code Coverage: _kDartIsolateSnapshotInstructions + 0x3a1580
        }
        Function 'encryptPayload':. String plaintext {
              Code Coverage: _kDartIsolateSnapshotInstructions + 0x3a1920
        }
    }
```

**重点**：`Code Coverage` 后面的偏移地址就是函数在 `libapp.so` 中的实际位置，可以直接用于 Frida Hook 或 IDA 定位。

### reFlutter 的局限性

| 局限 | 说明 |
|------|------|
| Flutter 版本兼容性 | 新版 Flutter 可能尚未被 reFlutter 支持 |
| 需要重打包 | 某些 App 有完整性校验，重打包后无法运行 |
| Root 检测 | Patched App 可能触发 Root/完整性检测 |
| 仅提供偏移 | 不提供函数体的反编译，需要配合其他工具 |

---

## Frida 拦截 Flutter 网络请求

Flutter 应用不使用系统的代理设置，也不使用 Java 层的 HTTP 客户端 (OkHttp)，而是使用 Dart 自己的 `HttpClient`，底层依赖 BoringSSL。因此，传统的抓包设置（Wi-Fi 代理）和 Frida SSL Pinning 脚本通常无效。

### BoringSSL 证书验证 Hook

Flutter 内嵌的 BoringSSL 库在 `libflutter.so` 中。我们需要 Hook 其中的证书验证函数：

```javascript
/**
 * Flutter SSL Pinning Bypass (通用版)
 *
 * 目标: Hook libflutter.so 中 BoringSSL 的 ssl_crypto_x509_session_verify_cert_chain
 * 原理: 使该函数始终返回 1 (验证成功)
 */

function findVerifyCertFunction() {
    // 方法 1: 通过导出符号查找 (有符号版本)
    var addr = Module.findExportByName("libflutter.so",
        "ssl_crypto_x509_session_verify_cert_chain");
    if (addr) {
        console.log("[+] 通过符号名找到验证函数: " + addr);
        return addr;
    }

    // 方法 2: 通过特征码搜索 (无符号版本, ARM64)
    // 该特征码对应证书验证函数的序言部分
    var patterns = [
        // Flutter 3.x 系列特征码
        "FF 03 05 D1 FD 7B 0F A9 F4 4F 0E A9 F6 57 0D A9",
        // Flutter 2.x 系列特征码
        "FF 43 04 D1 FE 67 0E A9 FD 7B 0D A9 FC 6F 0C A9",
    ];

    var module = Process.findModuleByName("libflutter.so");
    for (var i = 0; i < patterns.length; i++) {
        var matches = Memory.scanSync(module.base, module.size, patterns[i]);
        if (matches.length > 0) {
            console.log("[+] 通过特征码找到验证函数: " + matches[0].address);
            return matches[0].address;
        }
    }

    console.log("[-] 未找到证书验证函数，请更新特征码");
    return null;
}

function bypassSSLVerification() {
    var verifyFunc = findVerifyCertFunction();
    if (!verifyFunc) return;

    Interceptor.replace(verifyFunc, new NativeCallback(function () {
        console.log("[*] SSL 验证被绕过");
        return 1;  // 返回验证成功
    }, 'int', []));

    console.log("[+] SSL Pinning Bypass 已激活");
}

// 等待 libflutter.so 加载完成后执行
function waitForFlutter() {
    var interval = setInterval(function () {
        var module = Process.findModuleByName("libflutter.so");
        if (module) {
            clearInterval(interval);
            console.log("[*] libflutter.so 已加载: " + module.base);
            bypassSSLVerification();
        }
    }, 500);
}

waitForFlutter();
```

### Hook Dart HttpClient (通过 libapp.so 偏移)

结合 reFlutter 导出的 `dump.dart`，可以 Hook 具体的 Dart 网络请求函数：

```javascript
/**
 * Hook Dart HttpClient 请求
 * 需要配合 reFlutter 的 dump.dart 获取偏移地址
 */

// 假设 dump.dart 中获取到以下偏移:
// HttpClient._openUrl: 0x29a4c0
// _HttpClientRequest.close: 0x29b100
// _HttpClientResponse._readBody: 0x29c200

var libapp = Module.findBaseAddress("libapp.so");
if (!libapp) {
    console.log("[-] libapp.so 未加载");
} else {
    console.log("[*] libapp.so base: " + libapp);

    // Hook HTTP 请求发送
    var openUrlOffset = 0x29a4c0;
    Interceptor.attach(libapp.add(openUrlOffset), {
        onEnter: function (args) {
            console.log("[*] HttpClient._openUrl 被调用");
            // 注意: Dart 的参数传递方式与 C 不同
            // 需要根据 ARM64 ABI 和 Dart 调用约定分析寄存器
            // x0 通常是 this 指针
            // x1, x2, x3... 是参数
            console.log("    this = " + args[0]);
            console.log("    arg1 = " + args[1]);

            // 尝试读取 Dart String 对象内容
            // Dart String 对象布局: [tag][hash][length][data...]
            try {
                var strObj = args[1];
                var length = strObj.add(Process.pointerSize * 2).readS32();
                if (length > 0 && length < 2048) {
                    var data = strObj.add(Process.pointerSize * 3).readUtf8String(length);
                    console.log("    URL = " + data);
                }
            } catch (e) {
                // 解析失败，Dart 对象布局可能不同
            }
        }
    });
}
```

### 强制 Dart HttpClient 使用代理

```javascript
/**
 * Hook Dart Socket.connect 使流量经过代理
 *
 * 原理: Dart 的 HTTP 请求最终会调用 Socket.connect
 *       我们将目标地址替换为代理服务器地址
 */

var PROXY_HOST = "192.168.1.100";
var PROXY_PORT = 8080;

// 需要先从 dump.dart 或 blutter 输出中获取 Socket._nativeConnect 的偏移
// 以下偏移仅为示例
var socketConnectOffset = 0x1234;  // 替换为实际偏移

var libapp = Module.findBaseAddress("libapp.so");

Interceptor.attach(libapp.add(socketConnectOffset), {
    onEnter: function (args) {
        // 修改连接目标为代理地址
        console.log("[*] Socket.connect intercepted");
        // 具体的参数修改取决于 Dart 版本和调用约定
    }
});
```

---

## Flutter 逆向工具链

### 工具对比总览

| 工具 | 类型 | 原理 | 优势 | 劣势 |
|------|------|------|------|------|
| **reFlutter** | 动态 | 替换 libflutter.so，运行时 Dump | 获取完整函数偏移表 | 需要重打包 |
| **Blutter** | 静态 | 解析 Snapshot 格式 | 支持新版 Dart，输出详细 | 编译依赖较多 |
| **Doldrums** | 静态 | 解析 Snapshot 格式 | 使用简单 | 支持的 Dart 版本有限 |
| **darter** | 静态 | 解析 Snapshot 格式 | Python 实现，易修改 | 维护不活跃 |
| **dart-ffi** | 动态 | 通过 Dart FFI 接口交互 | 灵活 | 需要深入理解 Dart FFI |
| **Flutter Analyzer** | 静态 | 综合分析框架 | 集成度高 | 学习曲线陡 |

### Blutter (推荐)

Blutter 是目前最活跃且支持新版 Dart 的静态分析工具。

**安装**：

```bash
# 克隆仓库
git clone https://github.com/aspect-build/blutter.git
cd blutter

# 安装依赖 (需要 CMake, Ninja, Python 3)
python3 scripts/init.py

# 编译
python3 scripts/build.py
```

**使用**：

```bash
# 从 APK 中提取 libapp.so 和 libflutter.so
mkdir extracted && cd extracted
unzip ../target.apk lib/arm64-v8a/libapp.so lib/arm64-v8a/libflutter.so

# 运行 Blutter 分析
python3 blutter.py lib/arm64-v8a/libapp.so lib/arm64-v8a/libflutter.so output/
```

**Blutter 输出结构**：

```
output/
├── asm/                    # 每个 Dart 函数的反汇编
│   ├── ApiService.login.asm
│   ├── ApiService.fetchUserData.asm
│   └── ...
├── blutter_frida.js        # 自动生成的 Frida 脚本模板
├── objs.txt                # 对象池信息
├── pp.txt                  # 对象池指针列表
└── ida_script/
    └── addNames.py         # IDA Pro 符号导入脚本
```

**Blutter 输出的反汇编示例**：

```
; ApiService.login (String username, String password)
; offset: 0x3a1200
; Object Pool:
;   pp+0x10: "https://api.target.com/v1/auth/login"
;   pp+0x18: "username"
;   pp+0x20: "password"
;   pp+0x28: "Content-Type"
;   pp+0x30: "application/json"

0x3a1200: stp  x29, x30, [sp, #-0x40]!
0x3a1204: mov  x29, sp
0x3a1208: ldr  x16, [PP, #0x10]    ; "https://api.target.com/v1/auth/login"
0x3a120c: str  x16, [sp, #0x08]
...
0x3a1260: bl   HttpClient.post     ; 调用 HTTP POST
...
```

### Doldrums

**安装与使用**：

```bash
# 克隆仓库
git clone https://github.com/nicolo-ribaudo/doldrums.git
cd doldrums

# 运行 (需要 Dart SDK)
dart run bin/doldrums.dart libapp.so output_dir/
```

**输出示例** (dump.dart 格式)：

```dart
library package:target_app/models/user.dart

class User extends Object {
  // Fields:
  String name;     // offset 0x08
  String email;    // offset 0x10
  int id;          // offset 0x18

  // Methods:
  String toString() { /* offset: 0x1a2000 */ }
  Map<String, dynamic> toJson() { /* offset: 0x1a2100 */ }
  factory User.fromJson(Map<String, dynamic> json) { /* offset: 0x1a2200 */ }
}
```

### darter

```bash
# 安装
pip3 install darter

# 使用
darter libapp.so --output dump.json

# 输出为 JSON 格式，方便程序化处理
python3 -c "
import json
with open('dump.json') as f:
    data = json.load(f)
for lib in data['libraries']:
    print(f\"Library: {lib['uri']}\")
    for cls in lib['classes']:
        print(f\"  Class: {cls['name']}\")
        for func in cls['functions']:
            print(f\"    {func['name']}: 0x{func['offset']:x}\")
"
```

---

## libapp.so 分析技巧

### IDA Pro 分析

直接用 IDA Pro 打开 `libapp.so` 会看到大量无名函数。需要配合工具恢复符号信息。

**步骤 1: 导入符号**

```python
# IDA Python 脚本: 从 Blutter 输出导入符号
# 文件: import_blutter_symbols.py

import idaapi
import idautils
import idc

def import_blutter_names(script_path):
    """导入 Blutter 生成的 addNames.py 符号"""
    with open(script_path, 'r') as f:
        for line in f:
            line = line.strip()
            # 格式: idc.set_name(0xADDRESS, "ClassName.methodName", SN_NOWARN)
            if line.startswith("idc.set_name"):
                try:
                    exec(line)
                except Exception as e:
                    print(f"Error: {line}: {e}")

    print("[+] 符号导入完成")
    idaapi.refresh_idaview_anyway()

# 执行
import_blutter_names("/path/to/output/ida_script/addNames.py")
```

**步骤 2: 识别 Dart 调用约定**

Dart AOT (ARM64) 使用如下寄存器约定：

| 寄存器 | Dart 用途 | 说明 |
|--------|----------|------|
| `x0` | 函数返回值 / 第一个参数 | 类似标准 ABI |
| `x1`-`x7` | 函数参数 | |
| `x15` | Shadow call stack (某些版本) | |
| `x26` | Dart Thread 指针 (`THR`) | 指向当前 Dart Thread 结构 |
| `x27` | Object Pool 指针 (`PP`) | **重要** — 字符串/常量通过此指针访问 |
| `x28` | Dart Heap 指针 (`HEAP`) | 新对象分配相关 |
| `x29` | Frame Pointer (`FP`) | 栈帧指针 |
| `x30` | Link Register (`LR`) | 返回地址 |
| `SP` | Stack Pointer | 栈指针 |

> **关键**: `x27` (PP - Pool Pointer) 是理解 Dart 代码的关键。所有字符串字面量、API URL、加密密钥等常量都通过 `PP + offset` 来访问。

**步骤 3: 解读 Object Pool 引用**

```
; IDA 中常见的 Dart 代码模式:
ldr  x16, [x27, #0x1a8]    ; 从 Object Pool 加载对象
                             ; x27 = PP (Pool Pointer)
                             ; 0x1a8 = 对象在 Pool 中的偏移

; 要知道 0x1a8 处是什么对象, 需要查看 Blutter 输出的 pp.txt:
; pp+0x1a8: String "api_key"
; pp+0x1b0: String "X-Auth-Token"
; pp+0x1b8: Function 'encrypt'
```

### Ghidra 分析

Ghidra 分析 `libapp.so` 的流程与 IDA 类似，但需要不同的脚本：

```python
# Ghidra Script: 从 Blutter 导入符号
# 文件: ImportBlutterSymbols.py (放入 Ghidra Scripts 目录)

import re

def run():
    f = askFile("Select Blutter output file", "Open")
    with open(str(f)) as fp:
        for line in fp:
            match = re.match(r'(\w+)\s+(\w+)\s+(.+)', line.strip())
            if match:
                addr_str, size_str, name = match.groups()
                addr = toAddr(int(addr_str, 16))
                # 创建函数并命名
                createFunction(addr, name)
                sym = getSymbolAt(addr)
                if sym:
                    sym.setName(name, ghidra.program.model.symbol.SourceType.USER_DEFINED)

    println("[+] 导入完成")
```

### 快速定位技巧

**技巧 1: 搜索字符串常量**

```bash
# 在 libapp.so 中搜索有意义的字符串
strings -n 8 libapp.so | grep -iE "(api|http|login|token|encrypt|password|secret)"

# 常见发现:
# https://api.target.com/v1/
# Authorization
# X-API-Key
# AES/CBC/PKCS5Padding
# SHA256
```

**技巧 2: 通过 URL 定位网络请求函数**

```
1. strings 找到 API URL (如 "https://api.target.com/v1/login")
2. 在 Blutter 的 pp.txt 中搜索该字符串
3. 找到对应的 Pool 偏移 (如 pp+0x1a8)
4. 在 asm/ 中搜索引用该偏移的函数
5. 定位到具体的业务逻辑函数
```

**技巧 3: 通过交叉引用追踪调用链**

```bash
# 在 Blutter 的反汇编输出中搜索函数调用
grep -r "bl.*ApiService.login" output/asm/

# 或搜索 Pool 偏移引用
grep -r "\[PP, #0x1a8\]" output/asm/
```

---

## 实战：Flutter App 抓包

这是一个完整的 Flutter App HTTPS 流量拦截实战流程。

### 环境准备

```
+------------------+                    +------------------+
|  Android 手机     |  <--- 同一网络 --->  |  PC (分析机)      |
|  - 已 Root        |                    |  - Burp Suite    |
|  - Frida Server   |                    |  - adb           |
|  - 目标 App       |                    |  - reflutter     |
+------------------+                    +------------------+
     192.168.1.101                          192.168.1.100
```

### 方案一：reFlutter 重打包方案（推荐）

```bash
# ============================================
# 第 1 步: reFlutter 处理 APK
# ============================================
reflutter target.apk
# 选择 1 (Traffic monitoring and interception)
# 输入代理 IP: 192.168.1.100

# ============================================
# 第 2 步: 签名
# ============================================
# 生成临时签名密钥 (如果没有)
keytool -genkey -v -keystore debug.keystore \
    -alias debug -keyalg RSA -keysize 2048 \
    -validity 10000 -storepass android -keypass android \
    -dname "CN=Debug"

# 对齐 + 签名
zipalign -v 4 release.RE.apk release.RE.aligned.apk
apksigner sign --ks debug.keystore \
    --ks-pass pass:android \
    release.RE.aligned.apk

# ============================================
# 第 3 步: 安装并运行
# ============================================
adb install release.RE.aligned.apk

# ============================================
# 第 4 步: 配置 Burp Suite
# ============================================
# Burp -> Proxy -> Options -> Proxy Listeners
# 绑定: 192.168.1.100:8083  (所有接口)
# 注意: reFlutter 默认转发到代理的 8083 端口

# ============================================
# 第 5 步: 开始抓包
# ============================================
# 启动 App，Burp 中即可看到 Flutter 的 HTTPS 请求
```

### 方案二：Frida Hook 方案（无需重打包）

```javascript
/**
 * Flutter SSL Pinning Bypass + Proxy Redirect
 *
 * 使用方法:
 *   frida -U -f com.target.app -l flutter_ssl_bypass.js --no-pause
 */

var PROXY_IP = "192.168.1.100";
var PROXY_PORT = 8080;

// ========================================
// Part 1: 绕过 SSL 证书验证
// ========================================

function hookSSLVerify() {
    var flutter = Process.findModuleByName("libflutter.so");
    if (!flutter) {
        console.log("[-] libflutter.so 未加载，等待中...");
        return false;
    }

    console.log("[*] libflutter.so: " + flutter.base + " - " +
                flutter.base.add(flutter.size));

    // 搜索 ssl_crypto_x509_session_verify_cert_chain 特征码
    // ARM64 特征码 (根据 Flutter 版本可能不同)
    var pattern = "FF 03 05 D1 FD 7B 0F A9 F4 4F 0E A9 F6 57 0D A9";
    var matches = Memory.scanSync(flutter.base, flutter.size, pattern);

    if (matches.length === 0) {
        // 尝试备用特征码
        pattern = "FF 43 04 D1 FE 67 0E A9 FD 7B 0D A9";
        matches = Memory.scanSync(flutter.base, flutter.size, pattern);
    }

    if (matches.length > 0) {
        var verifyFunc = matches[0].address;
        console.log("[+] 找到验证函数: " + verifyFunc);

        // 替换为直接返回 1 (成功)
        Interceptor.replace(verifyFunc, new NativeCallback(function () {
            return 1;
        }, 'int', []));

        console.log("[+] SSL 验证已绕过");
        return true;
    }

    console.log("[-] 未找到验证函数特征码");
    return false;
}

// ========================================
// Part 2: 拦截 DNS 解析，实现透明代理
// ========================================

function hookGetAddrInfo() {
    var getaddrinfo = Module.findExportByName(null, "getaddrinfo");
    if (getaddrinfo) {
        Interceptor.attach(getaddrinfo, {
            onEnter: function (args) {
                var host = args[0].readCString();
                this.host = host;
                console.log("[DNS] " + host);
            },
            onLeave: function (retval) {
                // 可选: 将特定域名解析到代理 IP
                // 通常配合 iptables 透明代理使用
            }
        });
    }
}

// ========================================
// 主逻辑
// ========================================

console.log("[*] Flutter SSL Bypass Script 启动");

// 等待 libflutter.so 加载
var checkInterval = setInterval(function () {
    if (hookSSLVerify()) {
        clearInterval(checkInterval);
        hookGetAddrInfo();
        console.log("[+] 所有 Hook 已就绪");
    }
}, 1000);
```

### 方案三：ProxyDroid + iptables 透明代理

当上述方案均失败时，可以使用系统级透明代理强制重定向所有 TCP 流量：

```bash
# 在 Root 手机上设置 iptables 透明代理
# 将所有 443 端口流量重定向到 Burp

adb shell su -c "iptables -t nat -A OUTPUT -p tcp --dport 443 \
    -j DNAT --to-destination 192.168.1.100:8083"

adb shell su -c "iptables -t nat -A OUTPUT -p tcp --dport 80 \
    -j DNAT --to-destination 192.168.1.100:8080"

# 清除规则 (分析完成后)
adb shell su -c "iptables -t nat -F"
```

> **注意**: 此方案仍需配合 SSL 证书验证绕过，否则 TLS 握手会失败。

### 抓包结果分析

成功抓包后，典型的 Flutter App API 请求如下：

```
POST /v1/api/getUserInfo HTTP/1.1
Host: api.target.com
Content-Type: application/json; charset=utf-8
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
X-Request-Id: 550e8400-e29b-41d4-a716-446655440000
X-Timestamp: 1711440000
X-Sign: a3f2b8c91d...

{"user_id": 12345, "fields": ["name", "avatar", "balance"]}
```

**分析要点**：

- `Authorization`: JWT Token，可以在 jwt.io 解码查看载荷
- `X-Sign`: API 签名，需要逆向 `libapp.so` 中的签名生成函数
- `X-Timestamp`: 防重放时间戳

---

## 实战：提取 Flutter App 业务逻辑

本节以一个虚构的 Flutter 电商 App 为例，展示如何从 `libapp.so` 中提取关键业务逻辑。

### 目标

提取以下信息：
1. API 接口地址和请求格式
2. 请求签名 (`X-Sign`) 的生成算法
3. 本地数据加解密逻辑

### 第 1 步：使用 Blutter 提取函数信息

```bash
# 提取 SO 文件
mkdir -p work && cd work
unzip ../target.apk lib/arm64-v8a/libapp.so lib/arm64-v8a/libflutter.so -d .

# 运行 Blutter
python3 /path/to/blutter/blutter.py \
    lib/arm64-v8a/libapp.so \
    lib/arm64-v8a/libflutter.so \
    output/
```

### 第 2 步：定位关键类和函数

```bash
# 搜索与签名相关的函数
grep -ri "sign\|signature\|hmac\|encrypt" output/asm/ | head -30

# 搜索 API 服务类
grep -ri "ApiService\|HttpService\|NetworkManager" output/objs.txt

# 搜索 URL 常量
grep -ri "https://\|http://" output/pp.txt
```

**假设我们找到了以下关键信息**：

```
output/pp.txt:
  pp+0x2a0: String "https://api.target.com"
  pp+0x2a8: String "X-Sign"
  pp+0x2b0: String "X-Timestamp"
  pp+0x2b8: String "your_app_secret_key_2024"   # <-- 签名密钥!
  pp+0x2c0: Function '_generateSign'

output/asm/ApiService._generateSign.asm:
  ; _generateSign(String method, String path, Map params, int timestamp)
  ; offset: 0x3b4500
```

### 第 3 步：分析签名算法

查看 Blutter 输出的反汇编：

```
; ApiService._generateSign
; offset: 0x3b4500
; Pool references:
;   pp+0x2b8: "your_app_secret_key_2024"
;   pp+0x2c8: Function 'utf8.encode'
;   pp+0x2d0: Function 'Hmac.new'
;   pp+0x2d8: Closure 'sha256'

0x3b4500: stp  x29, x30, [sp, #-0x30]!
0x3b4504: mov  x29, sp
...
; 从 Pool 引用可以推断算法为: HMAC-SHA256
; 签名密钥: "your_app_secret_key_2024"
```

### 第 4 步：Frida 动态验证

```javascript
/**
 * Hook _generateSign 函数，动态捕获签名过程
 */

var libapp = Module.findBaseAddress("libapp.so");
var generateSignOffset = 0x3b4500;

Interceptor.attach(libapp.add(generateSignOffset), {
    onEnter: function (args) {
        console.log("=== _generateSign 被调用 ===");

        // 尝试读取 Dart 对象参数
        // 注意: 这里的参数解析高度依赖 Dart 版本和对象布局
        this.startTime = Date.now();

        // 打印调用栈
        console.log("调用栈:\n" +
            Thread.backtrace(this.context, Backtracer.ACCURATE)
            .map(DebugSymbol.fromAddress).join("\n"));
    },
    onLeave: function (retval) {
        console.log("返回值指针: " + retval);
        var elapsed = Date.now() - this.startTime;
        console.log("耗时: " + elapsed + "ms");

        // 尝试读取返回的 Dart String (签名结果)
        try {
            var taggedPtr = retval;
            // Dart 对象头部有 tag word
            var length = taggedPtr.add(Process.pointerSize * 2).readS32();
            if (length > 0 && length < 256) {
                var signStr = taggedPtr.add(Process.pointerSize * 3)
                    .readUtf8String(length);
                console.log("签名结果: " + signStr);
            }
        } catch (e) {
            console.log("读取签名失败: " + e);
        }
        console.log("========================");
    }
});
```

### 第 5 步：还原签名算法

结合静态分析和动态验证，还原出签名算法（Python 复现）：

```python
#!/usr/bin/env python3
"""还原 Flutter App 的 API 签名算法"""

import hmac
import hashlib
import time
import json
import requests

APP_SECRET = "your_app_secret_key_2024"
BASE_URL = "https://api.target.com"

def generate_sign(method, path, params, timestamp):
    """
    签名算法还原:
    1. 拼接: METHOD + PATH + sorted_params + TIMESTAMP
    2. HMAC-SHA256(secret, message)
    3. 转小写 hex
    """
    # 参数排序并拼接
    sorted_params = "&".join(
        f"{k}={v}" for k, v in sorted(params.items())
    )

    # 构造签名原文
    message = f"{method.upper()}{path}{sorted_params}{timestamp}"
    print(f"[DEBUG] 签名原文: {message}")

    # HMAC-SHA256
    sign = hmac.new(
        APP_SECRET.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    print(f"[DEBUG] 签名结果: {sign}")
    return sign


def call_api(path, params):
    """模拟 Flutter App 发送 API 请求"""
    timestamp = int(time.time())
    method = "POST"

    sign = generate_sign(method, path, params, timestamp)

    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "X-Sign": sign,
        "X-Timestamp": str(timestamp),
    }

    resp = requests.post(
        f"{BASE_URL}{path}",
        headers=headers,
        json=params
    )

    return resp.json()


# 测试调用
if __name__ == "__main__":
    result = call_api("/v1/api/getUserInfo", {
        "user_id": 12345,
        "fields": "name,avatar,balance"
    })
    print(json.dumps(result, indent=2, ensure_ascii=False))
```

### 第 6 步：分析数据加密逻辑

如果 App 对请求/响应数据进行了额外加密：

```javascript
/**
 * Hook 加解密函数，提取明文数据
 */

var libapp = Module.findBaseAddress("libapp.so");

// 假设通过 Blutter 分析发现:
// CryptoService.encrypt: 0x3c8000
// CryptoService.decrypt: 0x3c8200
// AES Key 在 pp+0x350: "0123456789abcdef"

var encryptOffset = 0x3c8000;
var decryptOffset = 0x3c8200;

// Hook 加密函数
Interceptor.attach(libapp.add(encryptOffset), {
    onEnter: function (args) {
        console.log("[ENCRYPT] 明文输入:");
        // 打印输入参数 (Dart String)
        try {
            var strObj = args[1];  // 第一个参数 (跳过 this)
            var len = strObj.add(Process.pointerSize * 2).readS32();
            if (len > 0 && len < 4096) {
                console.log(strObj.add(Process.pointerSize * 3)
                    .readUtf8String(len));
            }
        } catch (e) {}
    },
    onLeave: function (retval) {
        console.log("[ENCRYPT] 密文输出:");
        try {
            var strObj = retval;
            var len = strObj.add(Process.pointerSize * 2).readS32();
            if (len > 0 && len < 4096) {
                console.log(strObj.add(Process.pointerSize * 3)
                    .readUtf8String(len));
            }
        } catch (e) {}
    }
});

// Hook 解密函数
Interceptor.attach(libapp.add(decryptOffset), {
    onEnter: function (args) {
        console.log("[DECRYPT] 密文输入:");
        try {
            var strObj = args[1];
            var len = strObj.add(Process.pointerSize * 2).readS32();
            if (len > 0 && len < 4096) {
                console.log(strObj.add(Process.pointerSize * 3)
                    .readUtf8String(len));
            }
        } catch (e) {}
    },
    onLeave: function (retval) {
        console.log("[DECRYPT] 明文输出:");
        try {
            var strObj = retval;
            var len = strObj.add(Process.pointerSize * 2).readS32();
            if (len > 0 && len < 4096) {
                console.log(strObj.add(Process.pointerSize * 3)
                    .readUtf8String(len));
            }
        } catch (e) {}
    }
});
```

---

## 常见问题与解决方案

### 问题 1：reFlutter 不支持当前 Flutter 版本

**症状**：运行 `reflutter target.apk` 报错，提示不支持的引擎版本。

**解决方案**：

```bash
# 1. 确认 Flutter 引擎版本
strings lib/arm64-v8a/libflutter.so | grep -E "[0-9a-f]{40}"
# 输出的 hash 是 Flutter Engine Commit

# 2. 升级 reFlutter
pip3 install --upgrade reflutter

# 3. 如果仍不支持，改用 Blutter + Frida 方案
# Blutter 通常支持更新的版本
python3 blutter.py libapp.so libflutter.so output/

# 4. 使用 Frida 直接 Hook BoringSSL (不依赖 reFlutter)
# 参考上文 "Frida 拦截 Flutter 网络请求" 章节
```

### 问题 2：Patched APK 安装后闪退

**可能原因与对策**：

| 原因 | 检测方法 | 解决方案 |
|------|----------|----------|
| 签名校验失败 | Logcat 中有 signature 相关错误 | 确认已正确签名 |
| 完整性校验 | App 内部校验 SO 文件 hash | Hook 校验函数或 Patch 校验逻辑 |
| Root 检测 | 仅在 Root 设备闪退 | 使用 Magisk Hide / Shamiko |
| 架构不匹配 | reFlutter 替换了错误架构的 SO | 确认设备架构 (arm64-v8a / armeabi-v7a) |
| Flutter 版本不兼容 | Logcat 中有 snapshot 版本错误 | 使用正确版本的 reFlutter |

```bash
# 诊断步骤
adb logcat -s flutter,AndroidRuntime | tee crash_log.txt

# 常见错误信息:
# E/flutter: Snapshot is not compatible with the current VM
# E/AndroidRuntime: FATAL EXCEPTION: main - UnsatisfiedLinkError
```

### 问题 3：Frida 特征码搜索找不到 SSL 验证函数

**解决方案**：

```javascript
/**
 * 通用方法: 枚举 libflutter.so 中所有可疑的证书验证函数
 */

var flutter = Process.findModuleByName("libflutter.so");
var exports = flutter.enumerateExports();

console.log("[*] 搜索证书相关导出函数:");
exports.forEach(function (exp) {
    if (exp.name.toLowerCase().indexOf("cert") !== -1 ||
        exp.name.toLowerCase().indexOf("verify") !== -1 ||
        exp.name.toLowerCase().indexOf("ssl") !== -1 ||
        exp.name.toLowerCase().indexOf("x509") !== -1) {
        console.log("  " + exp.name + " @ " + exp.address);
    }
});

// 如果没有导出符号，尝试通过字符串引用定位
console.log("\n[*] 搜索证书相关字符串:");
var ranges = flutter.enumerateRanges("r--");
ranges.forEach(function (range) {
    try {
        var matches = Memory.scanSync(range.base, range.size,
            // "CERTIFICATE" 的 hex
            "43 45 52 54 49 46 49 43 41 54 45");
        matches.forEach(function (m) {
            console.log("  'CERTIFICATE' found at: " + m.address);
        });
    } catch (e) {}
});
```

### 问题 4：无法读取 Dart 对象内容

**问题**：Hook 到函数后，无法正确读取 Dart 对象（String、List、Map）的内容。

**原因**：Dart 对象的内存布局随版本变化，且使用 Tagged Pointer 机制。

```javascript
/**
 * Dart 对象读取辅助函数 (ARM64)
 *
 * Dart 使用 Tagged Pointer:
 * - Smi (小整数): 值直接存在指针中, 最低位为 0
 * - HeapObject: 指针最低位为 1, 需要减 1 获取真实地址
 */

function isDartSmi(ptr) {
    return (ptr.toInt32() & 1) === 0;
}

function dartSmiValue(ptr) {
    // Smi 值 = 指针 >> 1 (去掉 tag bit)
    return ptr.toInt32() >> 1;
}

function dartHeapObjectAddr(ptr) {
    // 去掉 tag bit
    return ptr.sub(1);
}

function readDartString(taggedPtr) {
    try {
        var obj = dartHeapObjectAddr(taggedPtr);
        // Dart String (OneByteString) 布局:
        //   +0x00: Object Header (class id, etc.)
        //   +0x08: hash (Smi)
        //   +0x10: length (Smi)
        //   +0x18: data (char[])

        var lengthTagged = obj.add(0x10).readPointer();
        var length = dartSmiValue(lengthTagged);

        if (length <= 0 || length > 65536) {
            return "<invalid length: " + length + ">";
        }

        return obj.add(0x18).readUtf8String(length);
    } catch (e) {
        return "<read error: " + e + ">";
    }
}

function readDartList(taggedPtr) {
    try {
        var obj = dartHeapObjectAddr(taggedPtr);
        // GrowableObjectArray 布局:
        //   +0x00: Object Header
        //   +0x08: type_arguments
        //   +0x10: length (Smi)
        //   +0x18: data (Array)

        var lengthTagged = obj.add(0x10).readPointer();
        var length = dartSmiValue(lengthTagged);

        var dataArray = dartHeapObjectAddr(obj.add(0x18).readPointer());
        var items = [];

        for (var i = 0; i < Math.min(length, 20); i++) {
            var item = dataArray.add(0x18 + i * 8).readPointer();
            if (isDartSmi(item)) {
                items.push(dartSmiValue(item));
            } else {
                items.push(readDartString(item));
            }
        }
        return "[" + items.join(", ") + "]";
    } catch (e) {
        return "<list read error: " + e + ">";
    }
}

// 使用示例
// var str = readDartString(args[1]);
// console.log("参数值: " + str);
```

### 问题 5：Flutter App 使用了 Certificate Pinning 且特征码方案失败

**终极方案：直接 Patch libflutter.so 二进制**

```python
#!/usr/bin/env python3
"""
手动 Patch libflutter.so 中的 SSL 验证函数
当 reFlutter 和特征码搜索都失败时使用
"""

import lief
import struct

def patch_ssl_verify(so_path, output_path):
    binary = lief.parse(so_path)

    # 方法: 搜索 BoringSSL 的 handshake_client.cc 中的
    # ssl_verify_peer_cert 相关代码段

    # 查找包含 "CERTIFICATE_VERIFY_FAILED" 的字符串引用
    text_section = binary.get_section(".text")
    rodata_section = binary.get_section(".rodata")

    rodata_bytes = bytes(rodata_section.content)

    # 搜索关键字符串
    target_str = b"CERTIFICATE_VERIFY_FAILED"
    idx = rodata_bytes.find(target_str)

    if idx >= 0:
        str_addr = rodata_section.virtual_address + idx
        print(f"[+] 找到字符串 @ 0x{str_addr:x}")
        # 此处需要进一步追踪交叉引用来定位验证函数
        # 然后将其开头 Patch 为 MOV W0, #1; RET
        # ARM64: 0x52800020 (MOV W0, #1), 0xD65F03C0 (RET)

    binary.write(output_path)
    print(f"[+] Patched SO 已保存到 {output_path}")

# patch_ssl_verify("libflutter.so", "libflutter_patched.so")
```

### 问题 6：Blutter 编译失败

```bash
# 常见错误: CMake / Ninja / Dart SDK 版本不匹配

# 解决步骤:
# 1. 确认依赖版本
cmake --version   # >= 3.20
ninja --version   # >= 1.10
python3 --version # >= 3.8

# 2. 确认目标 Dart 版本
strings libflutter.so | grep "Dart"

# 3. 使用 Docker 环境 (最稳定)
docker pull aspect/blutter:latest
docker run -v $(pwd):/work aspect/blutter \
    /work/libapp.so /work/libflutter.so /work/output/

# 4. 如果 Blutter 不支持，退而求其次使用 Doldrums
dart run bin/doldrums.dart libapp.so output/
```

### 工具选择决策树

```
                 Flutter App 逆向
                       |
            需要抓包？ OR 需要分析代码？
                /                \
               v                  v
          需要抓包              需要分析代码
               |                     |
    reFlutter 是否支持？      Blutter 是否支持？
          /        \              /         \
         是         否           是           否
         |          |            |            |
    reFlutter    Frida +      Blutter      Doldrums
    重打包方案   特征码 Hook   静态分析       or darter
         |          |            |            |
         v          v            v            v
    Burp 抓包   iptables     IDA/Ghidra   reFlutter
                透明代理     + 符号导入    动态 Dump
                    |            |            |
                    v            v            v
               SSL Bypass    Frida 动态    Frida 动态
               (Patch SO)   验证 + Hook   验证 + Hook
```

---

## 总结

| 阶段 | 关键技术 | 推荐工具 |
|------|----------|----------|
| **识别** | 检查 libflutter.so / libapp.so | unzip + strings |
| **版本识别** | 提取 Dart SDK 版本 | strings libflutter.so |
| **流量拦截** | SSL Pinning Bypass + 代理重定向 | reFlutter / Frida |
| **函数偏移提取** | Snapshot 解析，获取类名/函数名/偏移 | Blutter / reFlutter |
| **静态分析** | 反汇编 + 符号恢复 + Object Pool 分析 | IDA Pro + Blutter 脚本 |
| **动态分析** | Hook Dart 函数，拦截参数和返回值 | Frida |
| **算法还原** | 结合静态和动态分析复现加密/签名算法 | Python |

**核心要点**：

1. **流量拦截**: 必须使用 **reFlutter** 对 APK 进行 Patch，或者 Hook `libflutter.so` 中的 BoringSSL 证书验证函数。传统的 Java 层 Hook 和系统代理对 Flutter 无效。
2. **代码分析**: **Blutter** 是目前最推荐的静态分析工具，配合 IDA/Ghidra 符号导入可以大幅提高分析效率。reFlutter 的 `dump.dart` 提供了快速定位函数的能力。
3. **动态调试**: 所有 Hook 都发生在 Native 层。理解 Dart 的调用约定（PP 寄存器、Tagged Pointer、对象布局）是成功 Hook 的关键。
4. **版本敏感**: Flutter 逆向工具与 Dart SDK 版本强绑定。分析前务必确认目标 App 的 Flutter/Dart 版本，选择匹配的工具版本。
5. **核心原理**: 理解 Dart VM 的工作原理（Snapshot 结构、Object Pool、Dispatch Table）是深入逆向 Flutter 的基础。
