---
title: "社交媒体 App 与风控案例"
date: 2025-02-13
type: posts
tags: ["Native层", "签名验证", "Frida", "案例分析", "代理池", "Ghidra"]
weight: 10
---

# 社交媒体 App 与风控案例

> **📚 前置知识**
>
> 本案例涉及以下核心技术，建议先阅读相关章节：
>
> - **[密码学分析](../01-Recipes/Network/crypto_analysis.md)** - 理解 API 签名算法的逆向方法
> - **[Frida 完整指南](../02-Tools/Dynamic/frida_guide.md)** - 使用 Hook 定位签名生成函数
> - **[反分析技术案例](case_anti_analysis_techniques.md)** - 理解 Root/Frida 检测原理与绕过

社交媒体 App（如 X、Instagram、TikTok）是爬虫和自动化工具最常光顾的地方。因此，这些 App 的开发者在客户端和服务器端都部署了极其复杂的安全与风控系统，以保护用户数据和平台生态。本案例将聚焦于这些 App 中常见的风控对抗技术。

---

## 1. 社交媒体 App 逆向概述

### 1.1 主流社交 App 的防护体系

不同社交平台的防护侧重点和技术栈差异明显，但核心目标一致：**阻止非官方客户端的自动化访问**。以下是主流平台的防护特征对比：

| 平台 | 签名机制 | 设备指纹 | 风控 SDK | Native 混淆 | 难度评级 |
|------|----------|----------|----------|-------------|---------|
| TikTok/抖音 | X-Gorgon / X-Argus / X-Ladon | 多维度设备指纹 + 行为指纹 | 自研风控引擎 | OLLVM + VMP | ★★★★★ |
| 微信 | MMTLS 自定义协议 | 设备+网络指纹 | 自研 | 定制加密协议 | ★★★★★ |
| Instagram | X-IG-Signature | 设备 ID + Android ID | Meta 风控 | 部分 SO 混淆 | ★★★★ |
| X (Twitter) | OAuth + 自定义签名 | 客户端指纹 | Arkose Labs | 中度混淆 | ★★★ |
| 小红书 | shield 签名 | 设备指纹 + 行为分析 | 自研 | OLLVM | ★★★★ |
| 快手 | sig / sig3 签名 | 多维度指纹 | 自研风控 | VMP 保护 | ★★★★ |

### 1.2 通用防护架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                    社交 App 安全防护架构                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  客户端层                                                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │
│  │  环境检测   │  │  设备指纹   │  │  请求签名   │                 │
│  │ Root/Frida  │  │  采集上报   │  │  算法生成   │                 │
│  │ 模拟器检测  │  │  唯一标识   │  │  参数加密   │                 │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                 │
│         │                │                │                         │
│  ┌──────┴────────────────┴────────────────┴──────┐                 │
│  │              Native SO 安全核心                │                 │
│  │     (OLLVM / VMP / 自定义虚拟机保护)           │                 │
│  └───────────────────────┬───────────────────────┘                 │
│                          │                                          │
│  ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┼ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─   │
│                          │                                          │
│  服务端层                │                                          │
│  ┌─────────────┐  ┌─────┴───────┐  ┌─────────────┐                │
│  │  签名验证   │  │  风控引擎   │  │  行为分析   │                │
│  │  时效校验   │  │  规则匹配   │  │  异常检测   │                │
│  │  防重放     │  │  设备画像   │  │  机器学习   │                │
│  └─────────────┘  └─────────────┘  └─────────────┘                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.3 逆向工作流总览

一个完整的社交 App 逆向项目通常遵循以下流程：

1. **抓包分析** - 使用 Charles / mitmproxy 截获流量，识别关键参数
2. **签名定位** - 通过 Frida Hook 网络库定位签名生成入口
3. **算法逆向** - 静态分析 SO 中的签名算法，结合动态调试验证
4. **设备指纹** - 分析并模拟设备指纹采集逻辑
5. **签名复现** - 用 Python/Go 复现签名算法
6. **风控对抗** - 设计反检测和反封禁策略
7. **工程化** - 构建稳定可扩展的数据采集系统

---

## 2. 设备指纹采集分析

### 2.1 设备指纹采集维度

社交 App 通常会采集数十甚至上百项设备信息，用于生成唯一的设备标识和风控画像。以下是常见的采集维度：

| 维度 | 采集内容 | 采集方式 | 风控用途 |
|------|----------|----------|----------|
| 硬件信息 | CPU 型号、核心数、频率 | `/proc/cpuinfo` 读取 | 设备真实性验证 |
| 屏幕信息 | 分辨率、DPI、刷新率 | `DisplayMetrics` API | 模拟器检测 |
| 内存信息 | 总内存、可用内存 | `/proc/meminfo` | 设备画像 |
| 存储信息 | 总存储、可用空间 | `StatFs` API | 设备画像 |
| 网络信息 | MAC 地址、IP、WiFi SSID | `NetworkInterface` / `WifiManager` | 网络环境识别 |
| SIM 卡 | IMSI、运营商、国家码 | `TelephonyManager` | 地理位置验证 |
| 传感器 | 加速度计、陀螺仪列表 | `SensorManager` | 模拟器检测 |
| 系统属性 | Android 版本、Build 信息 | `Build` 类 / `getprop` | 设备指纹生成 |
| 应用列表 | 已安装 App 列表 | `PackageManager` | 用户画像/风控 |
| 电池信息 | 电量、充电状态、温度 | `BatteryManager` | 模拟器检测 |

### 2.2 识别指纹采集代码

指纹采集通常发生在 App 启动的早期阶段。以下 Frida 脚本可以监控常见的指纹采集行为：

```javascript
// monitor_fingerprint.js - 监控设备指纹采集行为
Java.perform(function () {
    // 1. 监控 Build 类的字段访问（最常见的指纹来源）
    var Build = Java.use("android.os.Build");
    var fields = ["MODEL", "MANUFACTURER", "BRAND", "DEVICE",
                  "PRODUCT", "HARDWARE", "BOARD", "FINGERPRINT"];

    fields.forEach(function (field) {
        // Build 类的字段是 static final，无法直接 Hook
        // 但可以通过 Hook 使用它们的代码间接发现
        console.log("[Build] " + field + " = " + Build[field].value);
    });

    // 2. 监控 Settings.Secure（获取 Android ID 等）
    var Secure = Java.use("android.provider.Settings$Secure");
    Secure.getString.overload(
        "android.content.ContentResolver", "java.lang.String"
    ).implementation = function (resolver, name) {
        var result = this.getString(resolver, name);
        if (name === "android_id" || name === "bluetooth_address") {
            console.log("[Settings.Secure] " + name + " = " + result);
            printStack();
        }
        return result;
    };

    // 3. 监控 TelephonyManager（获取 IMEI、IMSI 等）
    var TelephonyManager = Java.use("android.telephony.TelephonyManager");
    TelephonyManager.getDeviceId.overload().implementation = function () {
        var result = this.getDeviceId();
        console.log("[TelephonyManager] getDeviceId = " + result);
        printStack();
        return result;
    };

    // 4. 监控 WifiManager（获取 MAC 地址）
    var WifiInfo = Java.use("android.net.wifi.WifiInfo");
    WifiInfo.getMacAddress.implementation = function () {
        var result = this.getMacAddress();
        console.log("[WifiInfo] getMacAddress = " + result);
        printStack();
        return result;
    };

    // 5. 监控 SensorManager（传感器列表常用于模拟器检测）
    var SensorManager = Java.use("android.hardware.SensorManager");
    SensorManager.getSensorList.implementation = function (type) {
        var result = this.getSensorList(type);
        console.log("[SensorManager] getSensorList type=" + type
                    + " count=" + result.size());
        return result;
    };

    // 6. 监控文件读取（/proc/cpuinfo, /sys/ 等）
    var FileInputStream = Java.use("java.io.FileInputStream");
    FileInputStream.$init.overload("java.lang.String").implementation =
        function (path) {
            if (path.indexOf("/proc/") !== -1 ||
                path.indexOf("/sys/") !== -1) {
                console.log("[FileRead] " + path);
            }
            return this.$init(path);
        };

    function printStack() {
        console.log(Java.use("android.util.Log").getStackTraceString(
            Java.use("java.lang.Exception").$new()
        ));
    }
});
```

### 2.3 设备指纹生成流程

典型的设备指纹生成流程如下：

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  采集原始数据 │───>│  数据规范化   │───>│  哈希计算     │
│  Build 信息   │    │  去除空值     │    │  MD5/SHA256  │
│  Android ID   │    │  统一编码     │    │  生成 device │
│  MAC/IMEI     │    │  排序拼接     │    │  _id         │
│  传感器列表   │    │              │    │              │
└──────────────┘    └──────────────┘    └──────┬───────┘
                                               │
                                        ┌──────┴───────┐
                                        │  加密上报     │
                                        │  存入本地     │
                                        │  SharedPrefs  │
                                        └──────────────┘
```

**关键点**: 许多 App 会在 Native 层（SO 文件）中完成指纹的最终计算，以避免 Java 层被轻松 Hook。定位这些 SO 中的指纹生成函数是逆向的重要一步。

### 2.4 伪造设备指纹

当需要模拟多台设备时，必须伪造一套一致的设备指纹：

```javascript
// fake_device.js - 伪造设备指纹
Java.perform(function () {
    // 修改 Build 类的静态字段
    var Build = Java.use("android.os.Build");
    Build.MODEL.value = "Pixel 7 Pro";
    Build.MANUFACTURER.value = "Google";
    Build.BRAND.value = "google";
    Build.PRODUCT.value = "cheetah";
    Build.DEVICE.value = "cheetah";
    Build.HARDWARE.value = "tensor";
    Build.FINGERPRINT.value =
        "google/cheetah/cheetah:14/AP2A.240305.019.A1/" +
        "11373996:user/release-keys";

    // 修改 Build.VERSION 相关
    var Version = Java.use("android.os.Build$VERSION");
    Version.SDK_INT.value = 34;
    Version.RELEASE.value = "14";

    // 伪造 Android ID
    var Secure = Java.use("android.provider.Settings$Secure");
    Secure.getString.overload(
        "android.content.ContentResolver", "java.lang.String"
    ).implementation = function (resolver, name) {
        if (name === "android_id") {
            return generateRandomHex(16);
        }
        return this.getString(resolver, name);
    };

    function generateRandomHex(length) {
        var chars = "0123456789abcdef";
        var result = "";
        for (var i = 0; i < length; i++) {
            result += chars.charAt(Math.floor(Math.random() * 16));
        }
        return result;
    }
});
```

> **注意**: 设备指纹的各项参数之间存在**关联性**。例如 `Build.MODEL` 为 `Pixel 7 Pro` 但 `Build.HARDWARE` 为 `exynos` 会立刻被风控系统识别为伪造。伪造指纹时必须保持各字段的逻辑一致性。

---

## 3. 请求签名算法逆向

### 3.1 核心分析目标

几乎所有社交 App 的核心 API 请求都包含一个或多个签名参数（如 `X-Signature`, `X-Gorgon`）。这些签名是请求合法性的证明，也是逆向的主要目标。

### 3.2 定位签名参数

**目标**: 识别出 API 请求中哪个参数是签名。

1. **网络抓包**: 使用 Charles 或 Mitmproxy 拦截 App 的网络流量。刷新首页动态（timeline）的请求是最好的分析对象，因为它通常包含了最复杂的签名。
2. **观察请求**: 查看一个典型的 API 请求，例如 `/api/v2/feed`。你会注意到其 URL 参数或请求头 (Headers) 中存在一些看起来像哈希值的、无明显语义的参数。

   - **URL 参数**: `...&mas=01&as=a1...&ts=166...&ssmix=a...`
   - **请求头**: `X-Gorgon: 0404...`, `X-Khronos: 166...`

3. **参数筛选**: 通过多次重复请求，比较参数的变化规律。
   - **不变的**: `device_id`, `os_version` 等，通常是设备指纹的一部分。
   - **随时间变化的**: `ts`, `X-Khronos` 等，通常是时间戳。
   - **每次请求都随机变化的**: `mas`, `as`, `X-Gorgon` 等，这些就是我们要找的核心签名。

### 3.3 X-Gorgon / X-Argus 风格签名分析

以某短视频 App 为例，其请求头中典型的签名参数结构如下：

```
X-Gorgon:  0404b0d20000e3c70e15e5b91a7c9f35c7828beb8bc99b056770
X-Khronos: 1709123456
X-Argus:   vFYJBRsBIgoIa0MVF18yKC8HAQovHgkhCgRgJxUu...（Base64 编码）
X-Ladon:   z/5OBQACDwIOCQ0LBw...（Base64 编码）
X-Tyhon:   （较新版本出现的参数）
```

**签名生成的一般流程**:

```
┌───────────────────────────────────────────────────┐
│                 签名生成流程                        │
│                                                    │
│  1. 收集输入                                       │
│  ┌──────────────────────────────────────────────┐  │
│  │  URL Path + Query String (排序后)             │  │
│  │  POST Body (如果有)                           │  │
│  │  Cookie 值                                    │  │
│  │  当前时间戳                                   │  │
│  └──────────────────┬───────────────────────────┘  │
│                     │                               │
│  2. 预处理          ▼                               │
│  ┌──────────────────────────────────────────────┐  │
│  │  对各输入分别计算 MD5                          │  │
│  │  url_md5  = MD5(sorted_query_string)          │  │
│  │  body_md5 = MD5(post_body)                    │  │
│  │  cookie_md5 = MD5(cookie_str)                 │  │
│  └──────────────────┬───────────────────────────┘  │
│                     │                               │
│  3. 组装输入        ▼                               │
│  ┌──────────────────────────────────────────────┐  │
│  │  合并为固定格式的字节数组:                      │  │
│  │  [magic_bytes][timestamp][url_md5]            │  │
│  │  [body_md5][cookie_md5][session_key]          │  │
│  └──────────────────┬───────────────────────────┘  │
│                     │                               │
│  4. Native 加密     ▼                               │
│  ┌──────────────────────────────────────────────┐  │
│  │  调用 SO 中的核心签名函数                      │  │
│  │  多轮异或 + 查表 + 自定义变换                  │  │
│  │  生成最终签名字节                              │  │
│  └──────────────────┬───────────────────────────┘  │
│                     │                               │
│  5. 输出            ▼                               │
│  ┌──────────────────────────────────────────────┐  │
│  │  X-Gorgon = hex(签名字节)                     │  │
│  │  X-Khronos = timestamp                        │  │
│  └──────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────┘
```

### 3.4 定位签名生成代码

**目标**: 找到在客户端生成这些签名的代码。这是整个流程中最关键、也最困难的一步。

1. **全局搜索**: 在 `jadx-gui` 中，全局搜索上一步识别出的参数名，如 `X-Gorgon`。如果运气好，你能直接定位到构建网络请求的地方。

2. **Hook 大法**: 如果搜索无果（通常是因为参数名在代码中被加密或混淆了），Frida Hook 将是你的主力武器。

   - **Hook 网络库**: 从网络请求的源头入手。Hook `OkHttp` 的 `Request.Builder.addHeader` 或 `url()` 方法，打印出调用栈。

   ```javascript
   // hook_sign_entry.js - 定位签名入口
   Java.perform(function () {
       var Builder = Java.use("okhttp3.Request$Builder");
       Builder.addHeader.implementation = function (name, value) {
           if (name === "X-Gorgon") {
               console.log("=== Found X-Gorgon being added ===");
               console.log("Value: " + value);
               console.log("Stack trace:");
               console.log(
                   Java.use("android.util.Log").getStackTraceString(
                       Java.use("java.lang.Exception").$new()
                   )
               );
           }
           return this.addHeader(name, value);
       };

       // 同时 Hook OkHttp 的 Interceptor
       var RealInterceptorChain = Java.use(
           "okhttp3.internal.http.RealInterceptorChain"
       );
       RealInterceptorChain.proceed.overload(
           "okhttp3.Request"
       ).implementation = function (request) {
           var headers = request.headers();
           for (var i = 0; i < headers.size(); i++) {
               var name = headers.name(i);
               if (name.indexOf("X-") === 0) {
                   console.log("[Header] " + name + ": "
                               + headers.value(i));
               }
           }
           return this.proceed(request);
       };
   });
   ```

3. **从调用栈追溯到 Native**: 调用栈通常会指向一个 Java 方法，该方法内部通过 JNI 调用了 SO 中的签名函数。典型的路径如下：

   ```
   OkHttp Interceptor
     └─> SignatureHelper.addSignature(Request)
           └─> NativeHelper.generateSign(byte[])    // Java 声明
                 └─> libsecurity.so::Java_com_xxx_NativeHelper_generateSign
                       └─> core_sign_function(...)   // 真正的签名逻辑
   ```

### 3.5 分析 SO 中的签名函数

当定位到关键的 SO 文件后，使用 Ghidra 或 IDA 进行分析：

```javascript
// hook_jni_sign.js - Hook JNI 签名函数，获取输入输出
Java.perform(function () {
    // 方法 1: 从 Java 层 Hook
    var NativeHelper = Java.use("com.example.app.NativeHelper");
    NativeHelper.generateSign.implementation = function (input) {
        console.log("=== generateSign called ===");
        console.log("Input (hex): " + bytesToHex(input));
        console.log("Input (utf8): " + bytesToString(input));

        var result = this.generateSign(input);

        console.log("Output (hex): " + bytesToHex(result));
        return result;
    };

    // 方法 2: 直接 Hook SO 中的函数地址
    var baseAddr = Module.findBaseAddress("libsecurity.so");
    if (baseAddr) {
        // 假设通过 IDA 分析已知偏移为 0x12340
        var signFunc = baseAddr.add(0x12340);
        Interceptor.attach(signFunc, {
            onEnter: function (args) {
                console.log("=== Native sign function ===");
                // arg0 通常是 JNIEnv*
                // arg1 通常是 jclass 或 jobject
                // arg2 开始是实际参数
                this.inputPtr = args[2];
                this.inputLen = args[3].toInt32();
                console.log("Input buffer: " +
                    hexdump(this.inputPtr, {
                        length: this.inputLen
                    }));
            },
            onLeave: function (retval) {
                console.log("Return value: " + retval);
            }
        });
    }

    function bytesToHex(bytes) {
        var hex = [];
        for (var i = 0; i < bytes.length; i++) {
            hex.push(("0" + (bytes[i] & 0xff).toString(16)).slice(-2));
        }
        return hex.join("");
    }

    function bytesToString(bytes) {
        var result = "";
        for (var i = 0; i < bytes.length; i++) {
            result += String.fromCharCode(bytes[i] & 0xff);
        }
        return result;
    }
});
```

### 3.6 签名算法的常见模式

通过大量分析，社交 App 的签名算法通常遵循以下模式：

| 模式 | 描述 | 常见于 |
|------|------|--------|
| HMAC-SHA256 + Salt | 标准 HMAC，密钥硬编码或动态获取 | 中小型 App |
| 多轮 MD5 + 异或 | 对参数分段 MD5，再异或混合 | 早期版本的大型 App |
| 自定义查表算法 | 使用预计算的 S-Box 进行字节替换 | 抖音 X-Gorgon |
| Protobuf + 加密 | 参数序列化为 Protobuf 后整体加密 | X-Argus 类型签名 |
| TEA/XTEA 系列 | 轻量级分组加密 | 微信系 |

---

## 4. 反爬虫机制分析

### 4.1 服务端风控维度

社交 App 的反爬虫机制是一个多层次的系统，涵盖以下维度：

```
┌────────────────────────────────────────────────────────────────┐
│                    服务端风控引擎                                │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  实时检测层                                                     │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐  │
│  │ 频率限制   │ │ 签名验证   │ │ 时效检查   │ │ 重放检测   │  │
│  │ Rate Limit │ │ Sign Check │ │ Timestamp  │ │ Nonce      │  │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘  │
│                                                                │
│  行为分析层                                                     │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐  │
│  │ 访问模式   │ │ 操作序列   │ │ 时间分布   │ │ 内容偏好   │  │
│  │ Pattern    │ │ Sequence   │ │ TimeGap    │ │ Interest   │  │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘  │
│                                                                │
│  设备画像层                                                     │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐  │
│  │ 设备信誉   │ │ IP 信誉    │ │ 账号画像   │ │ 关联分析   │  │
│  │ DeviceRisk │ │ IPRisk     │ │ AccountAge │ │ Graph      │  │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘  │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### 4.2 频率限制策略

```python
# 频率限制的典型表现和应对
"""
常见的频率限制策略：

1. 固定窗口限制:
   - 每个 device_id 每分钟最多 30 次请求
   - 超出后返回 429 或空数据

2. 滑动窗口限制:
   - 统计最近 60 秒内的请求数
   - 动态调整限制阈值

3. 令牌桶策略:
   - 每秒恢复 N 个令牌
   - 允许突发但限制持续高频

4. 渐进式惩罚:
   - 第 1 次超限: 降低数据质量（返回部分字段）
   - 第 2 次超限: 触发验证码
   - 第 3 次超限: 临时封禁 device_id
   - 持续违规:  永久封禁 + 关联封禁
"""
```

### 4.3 风控 SDK 识别

许多 App 集成了第三方风控 SDK，可以通过以下方法识别：

```javascript
// identify_risk_sdk.js - 识别风控 SDK
Java.perform(function () {
    // 列出加载的所有 SO 文件
    Process.enumerateModules({
        onMatch: function (module) {
            var name = module.name.toLowerCase();
            // 常见风控 SDK 的 SO 文件特征
            var riskSdks = {
                "libmsaoaidsec": "阿里系风控 (EMAS)",
                "libsecuritybodybridge": "字节系风控",
                "libtnet": "阿里网络安全库",
                "libsgmain": "阿里安全组件",
                "libBugly": "腾讯 Bugly",
                "libwbsafeedit": "微博安全",
                "libDexHelper": "风控辅助",
            };

            for (var key in riskSdks) {
                if (name.indexOf(key.toLowerCase()) !== -1) {
                    console.log("[Risk SDK] " + riskSdks[key]
                                + " -> " + module.name
                                + " @ " + module.base);
                }
            }
        },
        onComplete: function () {
            console.log("[*] Module scan complete.");
        }
    });

    // 列出与风控相关的 Java 类
    Java.enumerateLoadedClasses({
        onMatch: function (className) {
            var patterns = [
                "com.bytedance.frameworks.encryptor",
                "com.ss.android.deviceregister",
                "com.alibaba.wireless.security",
                "com.tencent.tp.",
                "com.netease.nis.sdkwrapper",
            ];
            for (var i = 0; i < patterns.length; i++) {
                if (className.indexOf(patterns[i]) === 0) {
                    console.log("[Risk Class] " + className);
                    break;
                }
            }
        },
        onComplete: function () {}
    });
});
```

### 4.4 验证码机制

当风控引擎判定请求可疑时，会触发验证码：

| 验证码类型 | 实现方式 | 破解难度 | 绕过策略 |
|-----------|---------|---------|---------|
| 滑块验证 | 前端 JS/WebView | 中 | 模拟轨迹 + 图像识别 |
| 点选文字 | 图片 OCR | 高 | OCR + 坐标计算 |
| 图片旋转 | 角度匹配 | 中 | 图像特征匹配 |
| 短信验证 | 手机接码 | 低 | 接码平台 |
| 行为验证 | 无感知分析 | 极高 | 需要完整模拟真实行为 |

---

## 5. Frida 实战 Hook

### 5.1 Hook 签名生成全流程

以下是一个完整的签名 Hook 框架，可以捕获签名的输入和输出：

```javascript
// hook_full_sign.js - 完整的签名 Hook 框架
Java.perform(function () {
    console.log("[*] Starting full signature hook...");

    // ====== 第 1 层: Hook OkHttp 请求构建 ======
    try {
        var OkHttpClient = Java.use("okhttp3.OkHttpClient");
        var Request = Java.use("okhttp3.Request");
        var RequestBuilder = Java.use("okhttp3.Request$Builder");
        var RequestBody = Java.use("okhttp3.RequestBody");
        var Buffer = Java.use("okio.Buffer");

        // 拦截最终发出的请求
        RequestBuilder.build.implementation = function () {
            var request = this.build();
            var url = request.url().toString();
            var method = request.method();
            var headers = request.headers();

            console.log("\n========== Request ==========");
            console.log("[URL] " + method + " " + url);

            // 打印所有自定义头
            for (var i = 0; i < headers.size(); i++) {
                var name = headers.name(i);
                if (name.indexOf("X-") === 0 ||
                    name.indexOf("x-") === 0) {
                    console.log("[Header] " + name + ": "
                                + headers.value(i));
                }
            }

            // 打印请求体
            var body = request.body();
            if (body !== null) {
                var buffer = Buffer.$new();
                body.writeTo(buffer);
                var bodyStr = buffer.readUtf8();
                if (bodyStr.length < 2000) {
                    console.log("[Body] " + bodyStr);
                } else {
                    console.log("[Body] (length=" + bodyStr.length
                                + ") " + bodyStr.substring(0, 200)
                                + "...");
                }
            }
            console.log("==============================\n");
            return request;
        };
    } catch (e) {
        console.log("[-] OkHttp hook failed: " + e);
    }

    // ====== 第 2 层: Hook 签名生成函数 ======
    // 需要根据实际 App 调整类名和方法名
    try {
        var SignHelper = Java.use("com.example.app.security.SignHelper");

        // Hook 主签名方法
        SignHelper.getSign.overload(
            "java.util.Map", "java.lang.String"
        ).implementation = function (params, body) {
            console.log("\n===== SignHelper.getSign =====");

            // 打印参与签名的所有参数
            var iterator = params.entrySet().iterator();
            while (iterator.hasNext()) {
                var entry = iterator.next();
                console.log("  " + entry.getKey() + " = "
                            + entry.getValue());
            }

            if (body !== null) {
                console.log("[Body for sign] "
                            + body.substring(0, 200));
            }

            var result = this.getSign(params, body);
            console.log("[Sign Result] " + result);
            console.log("==============================\n");
            return result;
        };
    } catch (e) {
        console.log("[-] SignHelper hook failed: " + e);
    }

    // ====== 第 3 层: Hook Native 层 ======
    var soName = "libsecurity.so";
    var baseAddr = Module.findBaseAddress(soName);
    if (baseAddr) {
        console.log("[+] " + soName + " base: " + baseAddr);

        // Hook JNI_OnLoad 查看初始化逻辑
        var jniOnLoad = Module.findExportByName(
            soName, "JNI_OnLoad"
        );
        if (jniOnLoad) {
            Interceptor.attach(jniOnLoad, {
                onEnter: function (args) {
                    console.log("[+] JNI_OnLoad called");
                },
                onLeave: function (retval) {
                    console.log("[+] JNI_OnLoad returned: "
                                + retval);
                }
            });
        }

        // Hook 导出的签名函数
        var exports = Module.enumerateExports(soName);
        exports.forEach(function (exp) {
            if (exp.name.indexOf("sign") !== -1 ||
                exp.name.indexOf("Sign") !== -1 ||
                exp.name.indexOf("encrypt") !== -1) {
                console.log("[Export] " + exp.name
                            + " @ " + exp.address);
            }
        });
    }
});
```

### 5.2 Dump 签名参数并生成 Python 复现代码

```python
#!/usr/bin/env python3
"""
sign_replay.py - 配合 Frida Hook 数据复现签名算法

使用方式:
1. 先用 Frida Hook 脚本收集签名的输入输出样本
2. 根据收集到的数据分析签名逻辑
3. 用本脚本复现签名并验证
"""
import hashlib
import hmac
import struct
import time
import requests


class SignGenerator:
    """签名生成器 - 根据逆向结果实现"""

    def __init__(self, device_id, install_id, session_key=None):
        self.device_id = device_id
        self.install_id = install_id
        self.session_key = session_key or b""

    def generate_sign(self, url_path, query_params, body=None,
                      cookies=None):
        """
        生成 API 请求签名

        参数:
            url_path: 请求路径，如 "/api/v2/feed"
            query_params: dict, URL 查询参数
            body: bytes, POST 请求体（可选）
            cookies: str, Cookie 字符串（可选）

        返回:
            dict, 包含 X-Gorgon 和 X-Khronos
        """
        timestamp = int(time.time())

        # 第 1 步: 对查询参数排序并拼接
        sorted_params = sorted(query_params.items())
        query_string = "&".join(
            f"{k}={v}" for k, v in sorted_params
        )

        # 第 2 步: 分别计算 MD5
        url_md5 = hashlib.md5(
            query_string.encode()
        ).digest()

        body_md5 = hashlib.md5(
            body if body else b""
        ).digest()

        cookie_md5 = hashlib.md5(
            cookies.encode() if cookies else b""
        ).digest()

        # 第 3 步: 组装签名输入
        sign_input = bytearray()
        # magic header (4 bytes)
        sign_input.extend(b"\x04\x04")
        sign_input.extend(struct.pack("<H", 0))
        # timestamp (4 bytes, little-endian)
        sign_input.extend(struct.pack("<I", timestamp))
        # url md5, body md5, cookie md5 (各 16 bytes)
        sign_input.extend(url_md5)
        sign_input.extend(body_md5)
        sign_input.extend(cookie_md5)
        # session key
        sign_input.extend(self.session_key)

        # 第 4 步: 核心签名计算
        # （此处为简化示例，实际算法需根据逆向结果实现）
        signature = self._core_sign(bytes(sign_input))

        return {
            "X-Gorgon": signature.hex(),
            "X-Khronos": str(timestamp),
        }

    def _core_sign(self, data):
        """
        核心签名算法 - 需要根据 SO 逆向结果实现
        这里仅展示框架，实际算法会更复杂
        """
        # 示例: 多轮异或 + 查表
        # 实际需要从 SO 中提取 S-Box 和变换逻辑
        s_box = self._get_s_box()
        result = bytearray(20)
        for i in range(len(data)):
            result[i % 20] ^= s_box[data[i]]
        return bytes(result)

    @staticmethod
    def _get_s_box():
        """从 SO 中提取的 S-Box 查找表（256 字节）"""
        # 实际值需要从 Frida dump 或 IDA 分析中获取
        return bytes(range(256))


def make_api_request(sign_gen, endpoint, params, body=None):
    """发起带签名的 API 请求"""
    base_url = "https://api.example.com"

    # 添加设备参数
    params.update({
        "device_id": sign_gen.device_id,
        "iid": sign_gen.install_id,
        "os_version": "14",
        "device_type": "Pixel 7 Pro",
    })

    # 生成签名
    headers = sign_gen.generate_sign(
        endpoint, params, body
    )
    headers["User-Agent"] = (
        "com.example.app/30.0.0 "
        "(Linux; U; Android 14; zh_CN; Pixel 7 Pro; "
        "Build/AP2A.240305.019)"
    )

    # 发起请求
    url = f"{base_url}{endpoint}"
    if body:
        resp = requests.post(
            url, params=params, data=body, headers=headers
        )
    else:
        resp = requests.get(url, params=params, headers=headers)

    return resp.json()


# 使用示例
if __name__ == "__main__":
    signer = SignGenerator(
        device_id="7012345678901234567",
        install_id="7098765432109876543",
    )

    result = make_api_request(
        signer,
        "/api/v2/feed",
        {"count": "20", "cursor": "0"},
    )
    print(result)
```

### 5.3 绕过设备检查

```javascript
// bypass_device_check.js - 绕过设备合法性检查
Java.perform(function () {
    // 1. 绕过 Google Play Services 检查
    try {
        var GoogleApiAvailability = Java.use(
            "com.google.android.gms.common.GoogleApiAvailability"
        );
        GoogleApiAvailability.isGooglePlayServicesAvailable
            .implementation = function (context) {
                console.log("[*] Bypassing Google Play check");
                return 0; // SUCCESS
            };
    } catch (e) {}

    // 2. 绕过 SafetyNet/Play Integrity 检测
    try {
        var SafetyNet = Java.use(
            "com.google.android.gms.safetynet.SafetyNetClient"
        );
        SafetyNet.attest.implementation = function (nonce, apiKey) {
            console.log("[*] SafetyNet attest intercepted");
            // 返回预先构造的合法 response
            return this.attest(nonce, apiKey);
        };
    } catch (e) {}

    // 3. 绕过设备注册校验
    //    许多 App 在首次启动时会向服务器注册设备
    //    返回一个 device_token，后续请求需要携带
    try {
        var DeviceRegister = Java.use(
            "com.example.app.device.DeviceRegister"
        );
        DeviceRegister.register.implementation = function () {
            console.log("[*] Device registration intercepted");
            var result = this.register();
            console.log("[*] device_token: " + result);
            return result;
        };
    } catch (e) {}

    // 4. 伪造设备注册响应
    //    如果服务器拒绝注册（检测到异常设备），可以直接
    //    Hook 返回值，注入一个预先获取的合法 token
    try {
        var SharedPrefs = Java.use(
            "android.app.SharedPreferencesImpl$EditorImpl"
        );
        SharedPrefs.putString.implementation = function (key, value) {
            if (key === "device_token" || key === "install_id") {
                console.log("[SharedPrefs] " + key + " = " + value);
            }
            return this.putString(key, value);
        };
    } catch (e) {}
});
```

---

## 6. 反检测绕过

### 6.1 Root 检测绕过

社交 App 通常会检测设备是否已 Root，并拒绝在 Root 设备上运行或降低信任等级。

```javascript
// bypass_root.js - Root 检测绕过
Java.perform(function () {
    // 方法 1: Hook 文件存在性检查
    var File = Java.use("java.io.File");
    File.exists.implementation = function () {
        var path = this.getAbsolutePath();
        var blacklist = [
            "/system/bin/su",
            "/system/xbin/su",
            "/sbin/su",
            "/su/bin/su",
            "/data/local/su",
            "/data/local/bin/su",
            "/system/app/Superuser.apk",
            "/system/app/SuperSU",
            "/system/app/Magisk",
            "/data/adb/magisk",
        ];
        for (var i = 0; i < blacklist.length; i++) {
            if (path === blacklist[i]) {
                console.log("[Root] Hiding: " + path);
                return false;
            }
        }
        return this.exists();
    };

    // 方法 2: Hook Runtime.exec（检测 su 命令是否可执行）
    var Runtime = Java.use("java.lang.Runtime");
    Runtime.exec.overload("java.lang.String").implementation =
        function (cmd) {
            if (cmd.indexOf("su") !== -1 ||
                cmd.indexOf("which") !== -1) {
                console.log("[Root] Blocking exec: " + cmd);
                throw Java.use("java.io.IOException")
                    .$new("Permission denied");
            }
            return this.exec(cmd);
        };

    // 方法 3: Hook System.getProperty
    var System = Java.use("java.lang.System");
    System.getProperty.overload("java.lang.String").implementation =
        function (key) {
            if (key === "ro.build.tags") {
                return "release-keys"; // 隐藏 test-keys 标志
            }
            return this.getProperty(key);
        };

    // 方法 4: Hook PackageManager（隐藏 Magisk 等 App）
    var PM = Java.use(
        "android.app.ApplicationPackageManager"
    );
    PM.getInstalledPackages.implementation = function (flags) {
        var packages = this.getInstalledPackages(flags);
        var hideList = [
            "com.topjohnwu.magisk",
            "eu.chainfire.supersu",
            "com.koushikdutta.superuser",
            "com.noshufou.android.su",
            "com.thirdparty.superuser",
        ];
        var iterator = packages.iterator();
        while (iterator.hasNext()) {
            var pkg = iterator.next();
            var pkgName = pkg.packageName.value;
            for (var i = 0; i < hideList.length; i++) {
                if (pkgName === hideList[i]) {
                    console.log("[Root] Hiding package: "
                                + pkgName);
                    iterator.remove();
                    break;
                }
            }
        }
        return packages;
    };

    console.log("[+] Root detection bypass loaded.");
});
```

### 6.2 Frida 检测绕过

现代 App 的 Frida 检测手段越来越丰富。以下是常见检测与绕过策略：

| 检测手段 | 检测原理 | 绕过策略 |
|---------|---------|---------|
| 端口扫描 | 扫描 27042 默认端口 | 使用非默认端口启动 Frida |
| `/proc/maps` 扫描 | 查找 frida-agent 内存映射 | Hook `fopen`/`open`，过滤 frida 字符串 |
| 线程名称检测 | 查找 `gum-js-loop` 等线程 | Hook `pthread_create`，修改线程名 |
| 内联 Hook 检测 | 检测函数 prologue 是否被修改 | 使用 Stalker 替代 Interceptor |
| D-Bus 协议检测 | 向本地发送 D-Bus AUTH 请求 | Hook `send`/`recv` 过滤 D-Bus 数据 |
| SO 文件名检测 | 搜索 `frida-agent.so` | 重命名 Frida SO 文件 |

```javascript
// bypass_frida_detect.js - Frida 反检测
// 注意: 需要在 App 的反检测代码执行之前加载

// 1. Hook libc 的 open 函数，过滤 /proc/self/maps 中的 frida 痕迹
Interceptor.attach(Module.findExportByName("libc.so", "open"), {
    onEnter: function (args) {
        var path = args[0].readUtf8String();
        this.isMaps = (path && path.indexOf("/proc/") !== -1 &&
                       path.indexOf("/maps") !== -1);
    },
    onLeave: function (retval) {
        if (this.isMaps) {
            // 这里不直接修改 open 的返回值
            // 而是后续 Hook read 来过滤内容
        }
    }
});

// 2. Hook strstr，防止检测 frida 关键字
Interceptor.attach(Module.findExportByName("libc.so", "strstr"), {
    onEnter: function (args) {
        this.haystack = args[0];
        this.needle = args[1].readUtf8String();
    },
    onLeave: function (retval) {
        if (this.needle !== null) {
            var keywords = [
                "frida", "FRIDA", "gum-js-loop",
                "gmain", "gdbus", "linjector"
            ];
            for (var i = 0; i < keywords.length; i++) {
                if (this.needle.indexOf(keywords[i]) !== -1) {
                    retval.replace(ptr(0));
                    break;
                }
            }
        }
    }
});

// 3. Hook pthread_create，过滤 frida 相关线程
Interceptor.attach(
    Module.findExportByName("libc.so", "pthread_create"),
    {
        onEnter: function (args) {
            // args[2] 是线程函数地址
            // 某些检测会创建专门的检测线程
        },
        onLeave: function (retval) {}
    }
);

// 4. 修改 Frida 默认端口
// 在启动时使用: frida -H 0.0.0.0:8888
// 或者: frida-server -l 0.0.0.0:12345

console.log("[+] Frida anti-detection bypass loaded.");
```

### 6.3 模拟器检测绕过

```javascript
// bypass_emulator.js - 模拟器检测绕过
Java.perform(function () {
    // 1. 修改可疑的系统属性
    var SystemProperties = Java.use("android.os.SystemProperties");
    SystemProperties.get.overload(
        "java.lang.String", "java.lang.String"
    ).implementation = function (key, def) {
        var fakeProps = {
            "ro.hardware": "cheetah",
            "ro.product.model": "Pixel 7 Pro",
            "ro.kernel.qemu": "0",
            "ro.boot.qemu": "0",
            "ro.hardware.chipname": "tensor",
            "gsm.version.baseband": "g5300q-230913-231003-B-11397125",
            "init.svc.qemu-props": "",
            "init.svc.qemud": "",
        };
        if (key in fakeProps) {
            console.log("[Emu] Faking prop: " + key);
            return fakeProps[key];
        }
        return this.get(key, def);
    };

    // 2. 隐藏模拟器特征文件
    var File = Java.use("java.io.File");
    var origExists = File.exists;
    File.exists.implementation = function () {
        var path = this.getAbsolutePath();
        var emuFiles = [
            "/dev/socket/qemud",
            "/dev/qemu_pipe",
            "/system/bin/nox-prop",
            "/system/bin/microvirtd",
            "/system/bin/nox",
            "/system/lib/libc_malloc_debug_qemu.so",
            "/dev/goldfish_pipe",
        ];
        for (var i = 0; i < emuFiles.length; i++) {
            if (path === emuFiles[i]) {
                console.log("[Emu] Hiding file: " + path);
                return false;
            }
        }
        return origExists.call(this);
    };

    // 3. 伪造传感器数据（模拟器通常缺少真实传感器）
    var SensorManager = Java.use("android.hardware.SensorManager");
    SensorManager.getSensorList.implementation = function (type) {
        var list = this.getSensorList(type);
        // 模拟器通常传感器数量极少
        // 如果传感器数量不足，风控会标记为可疑
        console.log("[Emu] getSensorList type=" + type
                    + " count=" + list.size());
        return list;
    };

    // 4. 伪造电池信息（模拟器电池状态固定）
    var BatteryManager = Java.use("android.os.BatteryManager");
    BatteryManager.getIntProperty.implementation = function (id) {
        if (id === 4) { // BATTERY_PROPERTY_CAPACITY
            return 73; // 返回一个看起来真实的电量
        }
        return this.getIntProperty(id);
    };

    console.log("[+] Emulator detection bypass loaded.");
});
```

### 6.4 综合反检测框架

在实际项目中，建议将所有绕过脚本整合为一个统一的框架：

```javascript
// anti_detect_framework.js - 综合反检测框架
// 启动命令: frida -U -f com.target.app -l anti_detect_framework.js
//           --no-pause -o output.log

var config = {
    hideRoot: true,
    hideFrida: true,
    hideEmulator: true,
    fakeDevice: true,
    logLevel: "info",  // "debug" | "info" | "warn"
};

function log(level, tag, msg) {
    var levels = { debug: 0, info: 1, warn: 2 };
    if (levels[level] >= levels[config.logLevel]) {
        console.log("[" + level.toUpperCase() + "][" + tag + "] "
                    + msg);
    }
}

// 按顺序加载各模块
if (config.hideFrida) {
    // 最先加载 - 必须在 App 检测代码运行前
    log("info", "Init", "Loading Frida bypass...");
    // ... (加载 bypass_frida_detect.js 的内容)
}

if (config.hideRoot) {
    log("info", "Init", "Loading Root bypass...");
    // ... (加载 bypass_root.js 的内容)
}

if (config.hideEmulator) {
    log("info", "Init", "Loading Emulator bypass...");
    // ... (加载 bypass_emulator.js 的内容)
}

if (config.fakeDevice) {
    log("info", "Init", "Loading device spoofing...");
    // ... (加载 fake_device.js 的内容)
}

log("info", "Init", "Anti-detection framework loaded.");
```

---

## 7. 数据采集架构

### 7.1 系统架构设计

一个生产级的社交媒体数据采集系统需要考虑稳定性、可扩展性和反封禁能力：

```
┌────────────────────────────────────────────────────────────────────┐
│                    数据采集系统架构                                  │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  任务调度层                                                         │
│  ┌──────────────────────────────────────────────────────────┐      │
│  │  Redis / RabbitMQ 任务队列                                │      │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐               │      │
│  │  │ 用户列表  │  │ 帖子列表  │  │ 评论列表  │               │      │
│  │  │ 采集任务  │  │ 采集任务  │  │ 采集任务  │               │      │
│  │  └──────────┘  └──────────┘  └──────────┘               │      │
│  └──────────────────────┬──────────────────────────────────┘      │
│                         │                                          │
│  执行引擎层             ▼                                          │
│  ┌──────────────────────────────────────────────────────────┐      │
│  │  Worker 集群 (Python / Go)                                │      │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐               │      │
│  │  │ Worker 1 │  │ Worker 2 │  │ Worker N │               │      │
│  │  │ 签名模块 │  │ 签名模块 │  │ 签名模块 │               │      │
│  │  │ 账号池   │  │ 账号池   │  │ 账号池   │               │      │
│  │  └─────┬────┘  └─────┬────┘  └─────┬────┘               │      │
│  └────────┼─────────────┼─────────────┼────────────────────┘      │
│           │             │             │                            │
│  代理层   ▼             ▼             ▼                            │
│  ┌──────────────────────────────────────────────────────────┐      │
│  │  代理池管理器                                             │      │
│  │  住宅代理 / 机房代理 / 4G 代理                            │      │
│  │  自动轮换 / 健康检查 / 地域分配                            │      │
│  └──────────────────────┬──────────────────────────────────┘      │
│                         │                                          │
│  存储层                 ▼                                          │
│  ┌──────────────────────────────────────────────────────────┐      │
│  │  MongoDB / PostgreSQL + S3 / MinIO                        │      │
│  │  结构化数据 + 媒体文件存储                                 │      │
│  └──────────────────────────────────────────────────────────┘      │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### 7.2 签名服务封装

将逆向得到的签名算法封装为独立的微服务，供采集 Worker 调用：

```python
#!/usr/bin/env python3
"""
sign_server.py - 签名服务 (基于 Flask)

两种模式:
1. 纯 Python 复现模式 - 适用于已完全逆向的简单算法
2. RPC 桥接模式 - 通过 Frida RPC 调用真机上的签名函数
"""
from flask import Flask, request, jsonify
import frida
import json
import threading
import time

app = Flask(__name__)


class FridaSignBridge:
    """通过 Frida RPC 调用真机签名函数"""

    def __init__(self, device_id=None, package_name=None):
        self.package_name = package_name or "com.target.app"
        self.device = None
        self.session = None
        self.script = None
        self.rpc = None
        self.lock = threading.Lock()
        self._connect(device_id)

    def _connect(self, device_id):
        """连接到 Frida 设备"""
        if device_id:
            self.device = frida.get_device(device_id)
        else:
            self.device = frida.get_usb_device()

        self.session = self.device.attach(self.package_name)

        # 注入签名导出脚本
        js_code = """
        rpc.exports = {
            sign: function(url, params, body) {
                // 调用 App 内部的签名函数
                var result = {};
                Java.perform(function() {
                    var SignHelper = Java.use(
                        "com.target.app.security.SignHelper"
                    );
                    var HashMap = Java.use("java.util.HashMap");
                    var map = HashMap.$new();

                    var paramObj = JSON.parse(params);
                    for (var key in paramObj) {
                        map.put(key, paramObj[key]);
                    }

                    var signResult = SignHelper.getSign(map, body);
                    result = JSON.parse(signResult.toString());
                });
                return result;
            },

            getDeviceInfo: function() {
                var info = {};
                Java.perform(function() {
                    var Build = Java.use("android.os.Build");
                    info.model = Build.MODEL.value;
                    info.brand = Build.BRAND.value;
                    info.device = Build.DEVICE.value;
                });
                return info;
            }
        };
        """
        self.script = self.session.create_script(js_code)
        self.script.load()
        self.rpc = self.script.exports_sync

    def get_sign(self, url, params, body=""):
        """线程安全地获取签名"""
        with self.lock:
            return self.rpc.sign(
                url, json.dumps(params), body
            )


# 初始化签名桥接
bridge = None


@app.route("/sign", methods=["POST"])
def generate_sign():
    """
    签名接口

    请求体:
    {
        "url": "/api/v2/feed",
        "params": {"count": "20", "cursor": "0"},
        "body": ""
    }
    """
    data = request.json
    try:
        result = bridge.get_sign(
            data["url"],
            data["params"],
            data.get("body", ""),
        )
        return jsonify({"code": 0, "data": result})
    except Exception as e:
        return jsonify({"code": -1, "error": str(e)}), 500


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "timestamp": int(time.time())})


if __name__ == "__main__":
    bridge = FridaSignBridge(package_name="com.target.app")
    app.run(host="0.0.0.0", port=5000, threaded=True)
```

### 7.3 采集 Worker 实现

```python
#!/usr/bin/env python3
"""
worker.py - 数据采集 Worker
"""
import json
import random
import time
import logging
import requests
from redis import Redis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProxyManager:
    """代理池管理"""

    def __init__(self, redis_client, proxy_key="proxy:pool"):
        self.redis = redis_client
        self.proxy_key = proxy_key

    def get_proxy(self):
        """获取一个可用代理"""
        proxy = self.redis.srandmember(self.proxy_key)
        if proxy:
            return {"http": proxy.decode(), "https": proxy.decode()}
        return None

    def report_bad(self, proxy_url):
        """上报失效代理"""
        self.redis.srem(self.proxy_key, proxy_url)
        logger.warning(f"Removed bad proxy: {proxy_url}")


class AccountManager:
    """账号池管理"""

    def __init__(self, redis_client, account_key="account:pool"):
        self.redis = redis_client
        self.account_key = account_key

    def get_account(self):
        """获取一个可用账号（轮询方式）"""
        account_json = self.redis.lpop(self.account_key)
        if account_json:
            account = json.loads(account_json)
            # 放回队尾
            self.redis.rpush(self.account_key, account_json)
            return account
        return None

    def disable_account(self, account_id):
        """禁用被封禁的账号"""
        self.redis.sadd("account:disabled", account_id)
        logger.warning(f"Account disabled: {account_id}")


class CrawlWorker:
    """采集 Worker"""

    SIGN_SERVER = "http://localhost:5000"

    def __init__(self, redis_url="redis://localhost:6379"):
        self.redis = Redis.from_url(redis_url)
        self.proxy_mgr = ProxyManager(self.redis)
        self.account_mgr = AccountManager(self.redis)
        self.session = requests.Session()

    def get_sign(self, url, params, body=""):
        """调用签名服务"""
        resp = self.session.post(
            f"{self.SIGN_SERVER}/sign",
            json={"url": url, "params": params, "body": body},
            timeout=5,
        )
        return resp.json()["data"]

    def fetch_feed(self, cursor="0", count=20):
        """采集首页 Feed"""
        endpoint = "/api/v2/feed"
        account = self.account_mgr.get_account()
        if not account:
            raise RuntimeError("No available account")

        params = {
            "cursor": cursor,
            "count": str(count),
            "device_id": account["device_id"],
            "iid": account["install_id"],
        }

        # 获取签名
        sign_headers = self.get_sign(endpoint, params)

        # 构建请求
        headers = {
            "User-Agent": account["user_agent"],
            **sign_headers,
        }

        proxy = self.proxy_mgr.get_proxy()
        try:
            resp = self.session.get(
                f"https://api.example.com{endpoint}",
                params=params,
                headers=headers,
                proxies=proxy,
                timeout=10,
            )

            if resp.status_code == 429:
                logger.warning("Rate limited, backing off...")
                time.sleep(random.uniform(30, 60))
                return None

            data = resp.json()

            if data.get("status_code") == 2154:
                # 需要验证码
                logger.warning("Captcha required")
                return None

            return data

        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            if proxy:
                self.proxy_mgr.report_bad(
                    proxy.get("http", "")
                )
            return None

    def run(self, task_queue="task:feed"):
        """主循环"""
        logger.info("Worker started.")
        while True:
            task = self.redis.blpop(task_queue, timeout=30)
            if task is None:
                continue

            task_data = json.loads(task[1])
            cursor = task_data.get("cursor", "0")

            result = self.fetch_feed(cursor=cursor)
            if result and result.get("has_more"):
                # 生成下一页任务
                next_cursor = result["cursor"]
                self.redis.rpush(
                    task_queue,
                    json.dumps({"cursor": str(next_cursor)}),
                )

            # 存储结果
            if result and "data" in result:
                self.redis.rpush(
                    "result:feed",
                    json.dumps(result["data"]),
                )

            # 随机延迟，模拟人类行为
            delay = random.uniform(2.0, 8.0)
            time.sleep(delay)
```

---

## 8. 风控对抗策略

### 8.1 账号池管理

| 策略 | 说明 | 效果 |
|------|------|------|
| 账号预热 | 新注册账号先模拟正常使用 3-7 天 | 降低新号风控等级 |
| 轮换机制 | 每个账号每天限定请求量，轮换使用 | 避免单账号异常 |
| 信誉分级 | 高/中/低信誉账号分配不同任务 | 高价值任务用高信誉号 |
| 异常隔离 | 触发验证码的账号暂时隔离冷却 | 避免连续触发风控 |
| 信息完善 | 补充头像、昵称、简介等个人信息 | 提高账号可信度 |

### 8.2 IP 代理策略

```python
"""
proxy_strategy.py - 代理策略

不同类型代理的特点:
- 机房代理: 便宜但容易被识别，适合低风控接口
- 住宅代理: 价格中等，IP 信誉好，适合主力采集
- 4G 代理: 最贵但最真实，适合高风控场景（注册、登录）
- 隧道代理: 每次请求自动换 IP，适合高频场景
"""


class ProxyStrategy:
    """根据任务类型自动选择代理"""

    STRATEGY_MAP = {
        "register": "4g",       # 注册用 4G 代理
        "login": "4g",          # 登录用 4G 代理
        "feed": "residential",  # 刷 Feed 用住宅代理
        "search": "residential",
        "detail": "datacenter", # 详情页可以用机房代理
        "media": "datacenter",  # 下载媒体文件用机房代理
    }

    def __init__(self, proxy_pools):
        """
        proxy_pools: {
            "4g": ["socks5://..."],
            "residential": ["http://..."],
            "datacenter": ["http://..."],
        }
        """
        self.pools = proxy_pools

    def get_proxy(self, task_type):
        proxy_type = self.STRATEGY_MAP.get(task_type, "residential")
        pool = self.pools.get(proxy_type, [])
        if pool:
            return random.choice(pool)
        return None
```

### 8.3 行为模拟

风控引擎会分析用户的行为模式，纯粹的 API 调用很容易被识别为机器人。以下是关键的行为模拟策略：

```python
"""
behavior_simulator.py - 行为模拟器
"""
import random
import time
import numpy as np


class BehaviorSimulator:
    """模拟真实用户行为模式"""

    def __init__(self):
        # 真实用户的操作间隔通常符合对数正态分布
        self.mu = 1.5       # 对数均值
        self.sigma = 0.8    # 对数标准差

    def random_delay(self, min_sec=1.0, max_sec=15.0):
        """生成符合真实用户分布的随机延迟"""
        delay = np.random.lognormal(self.mu, self.sigma)
        return max(min_sec, min(delay, max_sec))

    def simulate_session(self):
        """
        模拟一次完整的用户会话

        真实用户的行为序列:
        1. 打开 App -> 刷 Feed (5-20 条)
        2. 偶尔点进详情页 (30% 概率)
        3. 极少数会评论/点赞 (5% 概率)
        4. 浏览一段时间后退出 (5-30 分钟)
        """
        actions = []

        # 刷 Feed
        feed_count = random.randint(5, 20)
        for i in range(feed_count):
            actions.append({
                "type": "scroll_feed",
                "delay": self.random_delay(1.0, 5.0),
            })

            # 30% 概率进入详情
            if random.random() < 0.3:
                view_time = self.random_delay(3.0, 30.0)
                actions.append({
                    "type": "view_detail",
                    "delay": view_time,
                })

                # 查看详情时 15% 概率点赞
                if random.random() < 0.15:
                    actions.append({
                        "type": "like",
                        "delay": self.random_delay(0.5, 2.0),
                    })

        return actions

    def get_active_hours(self):
        """
        返回当前时间是否在活跃时段

        真实用户活跃时段分布:
        - 早高峰: 07:00 - 09:00
        - 午间:   12:00 - 14:00
        - 晚高峰: 19:00 - 23:00
        - 深夜:   几乎无活动
        """
        hour = time.localtime().tm_hour
        active_periods = [
            (7, 9, 0.7),    # 早高峰，70% 活跃度
            (9, 12, 0.4),   # 上午，40% 活跃度
            (12, 14, 0.8),  # 午间，80% 活跃度
            (14, 19, 0.5),  # 下午，50% 活跃度
            (19, 23, 1.0),  # 晚高峰，100% 活跃度
            (23, 24, 0.3),  # 深夜，30% 活跃度
            (0, 7, 0.05),   # 凌晨，5% 活跃度
        ]
        for start, end, prob in active_periods:
            if start <= hour < end:
                return random.random() < prob
        return False
```

### 8.4 异常处理与熔断

```python
"""
circuit_breaker.py - 熔断器

当错误率超过阈值时自动暂停采集，避免进一步触发风控
"""
import time
from collections import deque


class CircuitBreaker:
    """采集熔断器"""

    # 状态定义
    CLOSED = "closed"      # 正常工作
    OPEN = "open"          # 熔断，停止请求
    HALF_OPEN = "half_open"  # 试探性恢复

    def __init__(self, failure_threshold=5,
                 recovery_timeout=300,
                 window_size=60):
        """
        failure_threshold: 窗口期内允许的最大失败次数
        recovery_timeout: 熔断后恢复等待时间（秒）
        window_size: 统计窗口大小（秒）
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.window_size = window_size
        self.state = self.CLOSED
        self.failures = deque()  # (timestamp, error_type)
        self.last_failure_time = 0

    def can_proceed(self):
        """检查是否可以继续请求"""
        if self.state == self.CLOSED:
            return True
        elif self.state == self.OPEN:
            if time.time() - self.last_failure_time \
                    > self.recovery_timeout:
                self.state = self.HALF_OPEN
                return True
            return False
        else:  # HALF_OPEN
            return True

    def record_success(self):
        """记录成功请求"""
        if self.state == self.HALF_OPEN:
            self.state = self.CLOSED
            self.failures.clear()

    def record_failure(self, error_type="unknown"):
        """记录失败请求"""
        now = time.time()
        self.failures.append((now, error_type))
        self.last_failure_time = now

        # 清除窗口外的旧记录
        while self.failures and \
                now - self.failures[0][0] > self.window_size:
            self.failures.popleft()

        # 检查是否需要熔断
        if len(self.failures) >= self.failure_threshold:
            self.state = self.OPEN
            print(f"[CircuitBreaker] OPEN - "
                  f"{len(self.failures)} failures in "
                  f"{self.window_size}s window. "
                  f"Cooling down for {self.recovery_timeout}s.")

        if self.state == self.HALF_OPEN:
            self.state = self.OPEN
```

---

## 9. 法律与伦理提醒

> **本节非常重要。在进行任何社交媒体 App 的逆向工程和数据采集之前，请务必了解相关的法律法规和平台政策。**

### 9.1 法律红线

| 法律法规 | 适用范围 | 关键条款 |
|---------|---------|---------|
| 《中华人民共和国网络安全法》 | 中国 | 禁止未经授权侵入他人网络或干扰网络正常功能 |
| 《中华人民共和国数据安全法》 | 中国 | 规范数据收集、存储、使用、传输等行为 |
| 《个人信息保护法》(PIPL) | 中国 | 保护个人信息，限制数据处理行为 |
| CFAA (计算机欺诈和滥用法) | 美国 | 未经授权访问计算机系统属于联邦犯罪 |
| GDPR (通用数据保护条例) | 欧盟 | 严格保护个人数据的收集和处理 |
| 《反不正当竞争法》 | 中国 | 爬取竞争对手数据可能构成不正当竞争 |

### 9.2 行为边界

```
┌─────────────────────────────────────────────────────────────────┐
│                       行为合法性评估                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ✅ 通常合法/低风险                                               │
│  ├── 安全研究与漏洞发现（遵循负责任披露原则）                       │
│  ├── 学术研究目的的小规模数据分析                                  │
│  ├── 对自己账号和数据的分析                                       │
│  └── 在授权范围内的渗透测试                                       │
│                                                                 │
│  ⚠️  灰色地带/需谨慎                                              │
│  ├── 大规模公开数据的自动化采集                                    │
│  ├── 绕过技术限制获取数据                                         │
│  └── 未经平台许可的第三方客户端开发                                │
│                                                                 │
│  ❌ 通常违法/高风险                                               │
│  ├── 采集和贩卖用户个人信息（隐私数据）                             │
│  ├── 破解付费功能或版权内容                                       │
│  ├── 利用逆向成果进行欺诈、刷量等黑产活动                          │
│  ├── 大规模账号注册和养号                                         │
│  └── 干扰平台正常运营（DDoS、资源耗尽等）                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 9.3 负责任的安全研究原则

1. **最小化原则**: 只采集研究所需的最少数据量，不过度获取
2. **不留痕迹**: 不修改、删除或损害目标系统的数据和功能
3. **负责任披露**: 发现安全漏洞后，通过正当渠道报告给平台安全团队
4. **数据保护**: 对研究过程中获取的用户数据进行严格保密，研究结束后及时销毁
5. **遵守条款**: 了解并尽量遵守平台的服务条款和 robots.txt 规则
6. **目的正当**: 确保研究目的是为了改善安全性，而非用于违法活动

### 9.4 漏洞报告渠道

发现安全问题后，应通过平台官方的安全漏洞报告渠道进行负责任的披露：

- **字节跳动**: https://security.bytedance.com
- **腾讯**: https://security.tencent.com
- **Meta**: https://www.facebook.com/whitehat
- **X (Twitter)**: https://hackerone.com/x
- **快手**: https://security.kuaishou.com

---

## 总结

社交媒体 App 的逆向是典型的"数据在客户端，但由服务器规则校验"的场景。其核心是对抗，而不只是解密。

- **签名是核心**: 逆向签名算法是所有工作的基础。大部分 App 将签名逻辑放在 Native SO 中并使用 OLLVM/VMP 保护，需要结合静态分析和动态调试。
- **设备指纹是基石**: 理解 App 如何采集设备信息，才能正确伪造身份，避免被关联封禁。
- **动静结合**: 需要反复在静态分析（Ghidra/IDA）和动态验证（Frida）之间切换。
- **风控是持续的斗争**: 即使你成功逆向了签名，服务器端的风控策略也在不断演进。这是一个长期的、动态的攻防过程。
- **工程化思维**: 从单次 Hook 到生产级采集系统，需要考虑代理管理、账号池、行为模拟、熔断机制等工程问题。
- **法律底线**: 始终确保你的行为在法律和伦理的框架之内。安全研究的目的是让系统更安全，而非造成破坏。
