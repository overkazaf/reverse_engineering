---
title: "Frida 常用脚本速查手册"
date: 2025-02-24
type: posts
tags: ["RSA", "Native层", "浏览器指纹", "Frida脚本", "Frida", "SSL Pinning"]
weight: 10
---

# Frida 常用脚本速查手册

> **📚 前置知识**
>
> 本配方涉及以下核心技术，建议先阅读相关章节：
>
> - **[Frida 完整指南](../../02-Tools/Dynamic/frida_guide.md)** - 掌握 Frida 基础语法与 API
> - **[ADB 速查手册](../../02-Tools/Cheatsheets/adb_cheatsheet.md)** - 设备连接与应用管理

## 问题场景

你在使用 Frida 进行 Android 逆向时,经常遇到以下情况:

- 💭 **"我需要绕过 SSL Pinning 抓包,但不想从零写脚本"**
- 💭 **"如何快速 Hook 所有 JNI 函数来分析 Native 层?"**
- 💭 **"想拦截并修改网络请求,有现成的模板吗?"**
- 💭 **"需要从 PC 端主动调用 App 的加密函数,怎么写 RPC?"**
- 💭 **"App 检测到 Frida 就闪退,有通用的绕过脚本吗?"**

本配方提供一套**经过实战验证**的 Frida 脚本模板库,按场景分类,可直接使用或快速修改。每个脚本都包含详细注释和使用说明。

---

## 工具清单

### 必需工具

- [x] **Frida** - 已安装并配置好 (参考 [Frida 使用指南](../../02-Tools/Dynamic/frida_guide.md))
- [x] **Root 设备/模拟器** - 运行 Frida Server
- [x] **目标应用已安装** - 需要分析的 App

### 可选工具

- ☐ **Python 3** - 用于 RPC 控制脚本
- ☐ **mitmproxy/Burp Suite** - 配合 SSL Pinning 绕过使用
- ☐ **IDA Pro/Ghidra** - 用于分析 Native 代码确定 Hook 点

---

## 前置条件

✅ **Frida 环境已配置**并能成功 attach 到目标应用
✅ **了解基本的 JavaScript 语法**
✅ **知道如何运行 Frida 脚本** (`frida -U -f com.app -l script.js`)
✅ **能识别需要 Hook 的类/函数名**(至少知道包名)

---

## 脚本索引

本手册包含以下 **8 类场景**的脚本:

| 场景                                  | 脚本数量 | 适用情况                      |
| ------------------------------------- | -------- | ----------------------------- |
| 🛡️ [绕过保护机制](#1-绕过保护机制)    | 3 个     | 反调试、反 Frida、SSL Pinning |
| [网络拦截与修改](#2-网络拦截与修改)   | 1 个     | 抓包、修改请求/响应           |
| [自动化 RPC 调用](#3-自动化-rpc-调用) | 1 套     | 主动调用加密函数、批量测试    |
| [JNI 函数分析](#4-jni-函数分析)       | 5 个     | Native 层逆向、参数追踪       |
| [通用 Hook 模板](#5-通用-hook-模板)   | 3 个     | 快速定位、批量 Hook           |
| [C 代码辅助工具](#6-c-代码辅助工具)   | 2 个     | 算法仿真、设备指纹生成        |

---

## 1. 绕过保护机制

### 脚本 1.1: 绕过 TracerPid 反调试检测

**何时使用**: App 通过读取 `/proc/self/status` 中的 `TracerPid` 来检测调试器。

**工作原理**: Hook `fgets` 函数,当检测到读取 `TracerPid` 时,将其值强制改为 0。

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
```

**使用方法**:

```bash
# Spawn mode (recommended)
frida -U -f com.target.app -l bypass_tracerpid.js --no-pause

# Attach mode
frida -U com.target.app -l bypass_tracerpid.js
```

### 脚本 1.2: 隐藏 Frida 特征字符串

**何时使用**: App 通过搜索进程内存中的 "frida" 字符串来检测 Frida。

**工作原理**: Hook 字符串比较函数,当发现比较内容包含 "frida" 时,返回不匹配。

```javascript
// hide_frida_strings.js - Hide Frida signature strings

// Hook strstr (most commonly used string search function)
var strstrPtr = Module.findExportByName("libc.so", "strstr");
if (strstrPtr) {
  Interceptor.attach(strstrPtr, {
    onEnter: function (args) {
      this.haystack = args[0].readCString();
      this.needle = args[1].readCString();
    },
    onLeave: function (retval) {
      if (this.haystack && this.needle) {
        var haystackLower = this.haystack.toLowerCase();
        var needleLower = this.needle.toLowerCase();

        if (haystackLower.includes("frida") || needleLower.includes("frida")) {
          console.log("✓ [strstr] Intercept Frida Detection:");
          console.log(
            '  Search: "' +
              this.needle +
              '" in "' +
              this.haystack.substring(0, 50) +
              '..."'
          );
          retval.replace(ptr(0)); // Return NULL (not found)
        }
      }
    },
  });
  console.log("[+] strstr hook configured");
}

// Hook strcmp
var strcmpPtr = Module.findExportByName("libc.so", "strcmp");
if (strcmpPtr) {
  Interceptor.attach(strcmpPtr, {
    onEnter: function (args) {
      this.str1 = args[0].readCString();
      this.str2 = args[1].readCString();
    },
    onLeave: function (retval) {
      if (this.str1 && this.str2) {
        var str1Lower = this.str1.toLowerCase();
        var str2Lower = this.str2.toLowerCase();

        if (str1Lower.includes("frida") || str2Lower.includes("frida")) {
          console.log("✓ [strcmp] Intercept Frida Detection:");
          console.log(
            '  Comparing: "' + this.str1 + '" vs "' + this.str2 + '"'
          );
          retval.replace(1); // Return non-zero (not equal)
        }
      }
    },
  });
  console.log("[+] strcmp hook configured");
}

console.log("[+] Frida string hiding activated");
```

**使用方法**:

```bash
frida -U -f com.target.app -l hide_frida_strings.js --no-pause
```

### 脚本 1.3: 通用 SSL Pinning 绕过

**何时使用**: 需要使用中间人代理 (如 Burp Suite) 抓取 HTTPS 流量,但 App 实现了证书校验。

**工作原理**: Hook 常见网络库(TrustManager、OkHttp3、HttpsURLConnection)的证书校验函数。

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

**使用方法**:

```bash
# 1. Start Burp Suite/mitmproxy on PC
# 2. Run script
frida -U -f com.target.app -l bypass_ssl_pinning.js --no-pause

# 3. View traffic in Burp/mitmproxy
```

---

## 2. 网络拦截与修改

### 脚本 2.1: OkHttp3 流量拦截与修改

**何时使用**: 需要在不使用代理的情况下,直接在 App 内部拦截和修改网络流量。

**工作原理**: Hook OkHttp3 的 `RealInterceptorChain.proceed` 方法,可以访问和修改请求/响应。

```javascript
// intercept_okhttp.js - Intercept and modify OkHttp3 network requests

Java.perform(function () {
  console.log("[+] Starting OkHttp3 hook...");

  try {
    var RealInterceptorChain = Java.use(
      "okhttp3.internal.http.RealInterceptorChain"
    );

    RealInterceptorChain.proceed.implementation = function (request) {
      // ========================================
      // Request Interception
      // ========================================
      console.log("\n[REQUEST] ========================================");
      console.log("  URL: " + request.url().toString());
      console.log("  Method: " + request.method());

      // Print request headers
      var headers = request.headers();
      var headerCount = headers.size();
      if (headerCount > 0) {
        console.log("  Headers:");
        for (var i = 0; i < headerCount; i++) {
          console.log("    " + headers.name(i) + ": " + headers.value(i));
        }
      }

      // Print request body
      var requestBody = request.body();
      if (requestBody) {
        try {
          var Buffer = Java.use("okio.Buffer");
          var buffer = Buffer.$new();
          requestBody.writeTo(buffer);
          var bodyString = buffer.readUtf8();
          console.log("  Body: " + bodyString);
        } catch (e) {
          console.log("  Body: [Cannot read]");
        }
      }

      // ========================================
      // Modify Request (Optional)
      // ========================================
      var modifiedRequest = request
        .newBuilder()
        .header("X-Custom-Header", "Injected-By-Frida") // Add custom header
        .header("User-Agent", "FridaBot/1.0") // Modify User-Agent
        .build();

      // Execute request
      var response = this.proceed(modifiedRequest);

      // ========================================
      // Response Interception
      // ========================================
      console.log("\n[RESPONSE] ========================================");
      console.log("  Code: " + response.code());
      console.log("  Message: " + response.message());

      // Print response headers
      var respHeaders = response.headers();
      var respHeaderCount = respHeaders.size();
      if (respHeaderCount > 0) {
        console.log("  Headers:");
        for (var i = 0; i < respHeaderCount; i++) {
          console.log(
            "    " + respHeaders.name(i) + ": " + respHeaders.value(i)
          );
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

          console.log("  Body: " + bodyString.substring(0, 500));

          // Example: Modify JSON response field
          if (bodyString.includes('"status"')) {
            var modifiedBody = bodyString.replace(
              /"status":"error"/g,
              '"status":"success"'
            );
            console.log("✓ [Modify] Status field: error -> success");

            // Rebuild response
            var MediaType = Java.use("okhttp3.MediaType");
            var ResponseBody = Java.use("okhttp3.ResponseBody");

            var newBody = ResponseBody.create(contentType, modifiedBody);

            return response.newBuilder().body(newBody).build();
          }

          // If not modified, need to recreate body (because it was already read)
          var ResponseBody = Java.use("okhttp3.ResponseBody");
          var newBody = ResponseBody.create(contentType, bodyString);

          return response.newBuilder().body(newBody).build();
        } catch (e) {
          console.log("  Body: [Read failed] " + e);
        }
      }

      return response;
    };

    console.log("[+] OkHttp3 Hook 成功");
  } catch (e) {
    console.log("[-] Hook Failed: " + e);
  }
});
```

**使用方法**:

```bash
frida -U -f com.target.app -l intercept_okhttp.js --no-pause
```

---

## 3. 自动化 RPC 调用

### 脚本 3.1: RPC 远程过程调用框架

**何时使用**: 需要从 PC 端批量调用 App 的加密函数、签名算法等,进行自动化测试。

**Frida 脚本** (`rpc_agent.js`):

```javascript
// rpc_agent.js - RPC export functions for Python calls

console.log("[+] RPC Agent loaded");

// Define exported RPC functions
rpc.exports = {
  // ========================================
  // Example 1: Call static encryption function
  // ========================================
  callEncrypt: function (plaintext) {
    var result = "";

    Java.perform(function () {
      try {
        // Modify to target app's actual class name and method name
        var CryptoUtil = Java.use("com.example.app.utils.CryptoUtil");

        // Call static method
        result = CryptoUtil.encrypt(plaintext);

        console.log('[RPC] encrypt("' + plaintext + '") = ' + result);
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
  callInstanceMethod: function (className, methodName, args) {
    var result = "";

    Java.perform(function () {
      try {
        var TargetClass = Java.use(className);

        // Enumerate all instances
        Java.choose(className, {
          onMatch: function (instance) {
            console.log("[RPC] Found instance: " + instance);

            // Call instance method
            result = instance[methodName].apply(instance, args);

            console.log("[RPC] " + methodName + "() = " + result);
          },
          onComplete: function () {},
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
  callNativeFunction: function (libraryName, functionName, args) {
    try {
      var funcAddr = Module.findExportByName(libraryName, functionName);

      if (!funcAddr) {
        return "ERROR: Function not found";
      }

      // Define function signature (modify based on actual situation)
      // Example: int encrypt(char* input, char* output, int length)
      var nativeFunc = new NativeFunction(funcAddr, "int", [
        "pointer",
        "pointer",
        "int",
      ]);

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
  getAppInfo: function () {
    var info = {};

    Java.perform(function () {
      var Context = Java.use("android.app.ActivityThread")
        .currentApplication()
        .getApplicationContext();
      var PackageManager = Context.getPackageManager();
      var PackageName = Context.getPackageName();
      var PackageInfo = PackageManager.getPackageInfo(PackageName, 0);

      info.packageName = PackageName;
      info.versionName = PackageInfo.versionName.value;
      info.versionCode = PackageInfo.versionCode.value;

      console.log("[RPC] App Info: " + JSON.stringify(info));
    });

    return info;
  },
};

console.log("[+] RPC functions exported:");
console.log("  - callEncrypt(plaintext)");
console.log("  - callInstanceMethod(className, methodName, args)");
console.log("  - callNativeFunction(libraryName, functionName, args)");
console.log("  - getAppInfo()");
```

**Python 控制脚本** (`rpc_controller.py`):

```python
# rpc_controller.py - Python RPC control script

import frida
import sys

def on_message(message, data):
    """Process messages from Frida script"""
    if message['type'] == 'send':
        print(f"[*] {message['payload']}")
    elif message['type'] == 'error':
        print(f"[!] Error: {message['stack']}")

def main():
    # ========================================
    # Connect to device and app
    # ========================================
    try:
        device = frida.get_usb_device(timeout=5)
        print(f"[+] Connected to device: {device}")
    except frida.TimedOutError:
        print("[-] Device connection timeout")
        sys.exit(1)

    # Attach to running app
    try:
        package_name = "com.example.app"  # Modify to target app package name
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
    print("=" * 60)
    print("Example 1: Call encryption function")
    print("=" * 60)

    test_data = "Hello, Frida RPC!"
    encrypted = api.call_encrypt(test_data)
    print(f"Plaintext: {test_data}")
    print(f"Ciphertext: {encrypted}\n")

    # ========================================
    # Example 2: Batch test
    # ========================================
    print("=" * 60)
    print("Example 2: Batch test")
    print("=" * 60)

    test_cases = [
        "test1",
        "test2",
        "test3",
        "a" * 100,  # Long string
        "",  # Empty string
    ]

    for i, test_input in enumerate(test_cases):
        result = api.call_encrypt(test_input)
        print(f"[{i+1}] {test_input[:20]:<20} -> {result}")

    print()

    # ========================================
    # Example 3: Get app info
    # ========================================
    print("=" * 60)
    print("Example 3: Get app info")
    print("=" * 60)

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

if __name__ == "__main__":
    main()
```

**使用方法**:

```bash
# 1. Start the app on device first
# 2. Run Python script
python3 rpc_controller.py

# Output example:
# [+] Connected to device: ...
# [+] Attached to: com.example.app
# [+] Frida script loaded
#
# Plaintext: Hello, Frida RPC!
# Ciphertext: SGVsbG8sIEZyaWRhIFJQQyE=
```

---

## 4. JNI 函数分析

### 脚本 4.1: 枚举 SO 文件中的所有 JNI 函数

**何时使用**: 需要找出某个 Native 库导出了哪些 JNI 函数。

**工作原理**: 扫描 SO 文件的导出表,过滤出所有以 `Java_` 开头的符号。

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
  console.log("  JNI Function Enumeration: " + libraryName);
  console.log("  Base address: " + module.base);
  console.log("  Size: " + (module.size / 1024).toFixed(2) + " KB");
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
    console.log("  Address: " + exp.address);
    console.log("  Offset: +" + ptr(exp.address).sub(module.base));

    // Parse JNI function name
    // Format: Java_PackageName_ClassName_MethodName
    var parts = exp.name.split("_");
    if (parts.length >= 4) {
      var packageAndClass = parts.slice(1, -1).join(".");
      var methodName = parts[parts.length - 1];
      console.log(
        "  Java Method: " + packageAndClass + "." + methodName + "()"
      );
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

**使用方法**:

```bash
frida -U -f com.target.app -l enumerate_jni.js --no-pause
```

### 脚本 4.2: Hook 单个 JNI 函数

**何时使用**: 已知具体的 JNI 函数名,需要追踪其参数和返回值。

**工作原理**: 通过函数名直接定位并 Hook,解析 JNIEnv 指针和参数。

```javascript
// hook_jni_function.js - Hook single JNI function

function hookJNIFunction(libraryName, functionName) {
  var funcAddr = Module.findExportByName(libraryName, functionName);

  if (!funcAddr) {
    console.log("[-] Function not found: " + functionName);
    return;
  }

  console.log("[+] Hooking: " + functionName);
  console.log("  Address: " + funcAddr);

  Interceptor.attach(funcAddr, {
    onEnter: function (args) {
      console.log("\n" + "=".repeat(60));
      console.log("[JNI CALL] " + functionName);
      console.log("=".repeat(60));
      console.log("  JNIEnv*: " + args[0]);
      console.log("  jobject/jclass: " + args[1]);

      // Try to parse parameters (starting from args[2])
      for (var i = 2; i < 8 && i < args.length; i++) {
        var arg = args[i];
        console.log("  arg[" + (i - 2) + "]: " + arg);

        if (arg.isNull()) {
          console.log("    -> null");
          continue;
        }

        // Try to parse as jstring
        try {
          var env = Java.vm.getEnv();
          var strPtr = env.getStringUtfChars(arg, null);
          var str = strPtr.readCString();

          if (str && str.length > 0 && str.length < 500) {
            console.log('    -> jstring: "' + str + '"');
          }

          env.releaseStringUtfChars(arg, strPtr);
          continue;
        } catch (e) {}

        // Try to parse as integer
        try {
          var intVal = arg.toInt32();
          console.log(
            "    -> jint: " + intVal + " (0x" + intVal.toString(16) + ")"
          );
          continue;
        } catch (e) {}

        // Try to parse as byte array
        try {
          var env = Java.vm.getEnv();
          var arrayLen = env.getArrayLength(arg);

          if (arrayLen > 0 && arrayLen < 1024) {
            console.log("    -> jbyteArray[" + arrayLen + "]");

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

        console.log("    -> Pointer: " + arg);
      }
    },

    onLeave: function (retval) {
      console.log("\n  [Return Value]: " + retval);

      if (retval.isNull()) {
        console.log("    -> null");
        return;
      }

      // Try to parse return value
      try {
        var env = Java.vm.getEnv();
        var strPtr = env.getStringUtfChars(retval, null);
        var str = strPtr.readCString();

        if (str && str.length > 0 && str.length < 500) {
          console.log('    -> jstring: "' + str + '"');
        }

        env.releaseStringUtfChars(retval, strPtr);
      } catch (e) {
        try {
          var intVal = retval.toInt32();
          console.log("    -> jint: " + intVal);
        } catch (e2) {
          console.log("    -> Pointer: " + retval);
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

**使用方法**:

```bash
frida -U -f com.target.app -l hook_jni_function.js --no-pause
```

### 脚本 4.3: 批量 Hook 所有 JNI 函数

**何时使用**: 不确定哪个 JNI 函数与目标功能相关,需要全部拦截观察。

**工作原理**: 枚举所有 JNI 函数,批量设置 Hook。

```javascript
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
              console.log("  JNIEnv*: " + arg);
            } else if (i === 1) {
              console.log("  jobject: " + arg);
            } else {
              console.log("  arg[" + (i - 2) + "]: " + arg);

              // Try to parse string
              if (!arg.isNull()) {
                try {
                  var env = Java.vm.getEnv();
                  var str = env.getStringUtfChars(arg, null).readCString();
                  if (str && str.length > 0 && str.length < 100) {
                    console.log('    -> "' + str + '"');
                  }
                  env.releaseStringUtfChars(arg, str);
                } catch (e) {}
              }
            }
          }
        },

        onLeave: function (retval) {
          console.log("  Return: " + retval);
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

**使用方法**:

```bash
frida -U -f com.target.app -l hook_all_jni.js --no-pause
```

### 脚本 4.4: Hook JNI_OnLoad 函数

**何时使用**: 需要在 Native 库加载时的初始化阶段进行分析。

**工作原理**: Hook `JNI_OnLoad`,这是 Native 库加载时系统调用的第一个函数。

```javascript
// hook_jni_onload.js - Hook JNI_OnLoad function

function hookJNIOnLoad(libraryName) {
  var onLoadAddr = Module.findExportByName(libraryName, "JNI_OnLoad");

  if (!onLoadAddr) {
    console.log("[-] JNI_OnLoad not found: " + libraryName);
    return;
  }

  console.log("[+] Hooking JNI_OnLoad");
  console.log("  Address: " + onLoadAddr);

  Interceptor.attach(onLoadAddr, {
    onEnter: function (args) {
      console.log("\n" + "=".repeat(60));
      console.log("[JNI_OnLoad] Called");
      console.log("=".repeat(60));
      console.log("  JavaVM*: " + args[0]);
      console.log("  reserved: " + args[1]);

      this.vm = args[0];
    },

    onLeave: function (retval) {
      var jniVersion = retval.toInt32();
      console.log("  Return JNI Version: " + jniVersion);

      // Parse version number
      var major = (jniVersion >> 16) & 0xffff;
      var minor = jniVersion & 0xffff;
      console.log("  -> JNI_VERSION_" + major + "_" + minor);

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
```

**使用方法**:

```bash
frida -U -f com.target.app -l hook_jni_onload.js --no-pause
```

---

## 5. 通用 Hook 模板

### 脚本 5.1: Hook Java 方法(支持重载)

**何时使用**: 需要拦截某个 Java 类的特定方法。

**工作原理**: 使用 `Java.use()` 加载类,然后替换方法实现。

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
            console.log("  arg[" + i + "]: " + arguments[i]);
          }

          // Call original method
          var result = this[methodName].apply(this, arguments);

          console.log("  Return: " + result);

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
```

**使用方法**:

```bash
frida -U -f com.target.app -l hook_java_method.js --no-pause
```

### 脚本 5.2: Hook 类的所有方法

**何时使用**: 需要观察某个类的所有方法调用情况。

**工作原理**: 使用反射获取类的所有方法,批量 Hook。

```javascript
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
                console.log("  Parameters:");
                for (var i = 0; i < arguments.length; i++) {
                  console.log("    [" + i + "] " + arguments[i]);
                }
              }

              var result = this[methodName].apply(this, arguments);

              console.log("  Return: " + result);

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

**使用方法**:

```bash
frida -U -f com.target.app -l hook_all_methods.js --no-pause
```

### 脚本 5.3: Hook 构造函数

**何时使用**: 需要监控对象创建时机和构造参数。

**工作原理**: Hook 类的 `$init` 方法(Frida 中构造函数的特殊名称)。

```javascript
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
            console.log("  Constructor parameters:");
            for (var i = 0; i < arguments.length; i++) {
              console.log("    [" + i + "] " + arguments[i]);
            }
          }

          // Call original constructor
          var result = this.$init.apply(this, arguments);

          console.log("  Instance: " + this);

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

**使用方法**:

```bash
frida -U -f com.target.app -l hook_constructor.js --no-pause
```

---

## 6. C 代码辅助工具

### 工具 6.1: 算法仿真工具

**何时使用**: 在 IDA/Ghidra 中看到加密/解密算法逻辑,需要提取出来独立验证。

**示例: XOR 加密算法仿真**

```c
// emulate_xor_encrypt.c - Emulate XOR encryption algorithm

#include <stdio.h>
#include <string.h>
#include <stdint.h>

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

**编译和运行**:

```bash
# Compile the program
gcc emulate_xor_encrypt.c -o emulate

# Run the program
./emulate

# Output:
# === XOR Encryption Algorithm Test ===
#
# Plaintext: Hello, Android Reverse Engineering!
# Plaintext HEX: 48 65 6c 6c 6f 2c 20 41 6e 64 72 6f 69 64 ...
#
# After encryption:
# Ciphertext HEX: 17 30 39 39 32 79 75 16 39 31 2d 32 36 31 ...
#
# After decryption: Hello, Android Reverse Engineering!
```

### 工具 6.2: 设备指纹生成工具

**何时使用**: 需要批量生成虚拟设备的指纹信息用于测试。

**示例: 设备指纹生成**

```c
// device_fingerprint.c - 设备指纹生成工具

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
    printf("  \"timestamp\": %ld,\n", time(NULL));
    printf("  \"device\": {\n");

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

            printf("    \"%s\": \"%s\"", key, value);

            if (i < num_props - 1) {
                printf(",");
            }
            printf("\n");

            free(value);
        }
    }

    printf("  }\n");
    printf("}\n");

    return 0;
}
```

**编译和使用**:

```bash
# Push to device and compile
adb push device_fingerprint.c /data/local/tmp/
adb shell
cd /data/local/tmp
gcc device_fingerprint.c -o fingerprint
chmod +x fingerprint

# Run the program
./fingerprint

# Output JSON format device fingerprint:
# {
#   "timestamp": 1734518400,
#   "device": {
#     "brand": "google",
#     "model": "Pixel 5",
#     "manufacturer": "Google",
#     ...
#   }
# }

# Save to file
./fingerprint > /sdcard/device_info.json
```

---

## 常见问题排查

### 问题 1: Hook 没有生效

**可能原因**:

1. Hook 时机太晚,目标函数已经执行完毕
2. 类名或方法名拼写错误
3. 使用了 Attach 模式,但 DEX 还未加载

**解决方案**:

```bash
# 1. Use Spawn mode (Recommended)
frida -U -f com.target.app -l script.js --no-pause

# 2. Check if class name is correct
```

```javascript
Java.perform(function () {
  Java.enumerateLoadedClasses({
    onMatch: function (className) {
      if (className.indexOf("Crypto") !== -1) {
        console.log("[+] Found class: " + className);
      }
    },
    onComplete: function () {},
  });
});
```

```bash
# 3. Delayed hook (if using Attach mode)
```

```javascript
setTimeout(function () {
  hookJavaMethod("com.example.app.Crypto", "encrypt");
}, 2000);
```

### 问题 2: Hook JNI 函数时 App 崩溃

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

### 问题 3: RPC 调用时提示类不存在

**可能原因**:

1. 类还未加载到内存
2. 类名错误或被混淆
3. 使用了动态加载的 DEX

**解决方案**:

```python
# On Python side, wait for class to load first
api.wait_for_class("com.example.app.Crypto")  # Custom wait function
```

```javascript
// Or check in Frida script
rpc.exports = {
  callEncrypt: function (input) {
    var result = "";

    Java.perform(function () {
      // Check if class exists first
      try {
        var Crypto = Java.use("com.example.app.Crypto");
        result = Crypto.encrypt(input);
      } catch (e) {
        // Try to enumerate and find
        Java.enumerateLoadedClasses({
          onMatch: function (className) {
            if (className.includes("Crypto")) {
              console.log("[+] Found: " + className);
            }
          },
          onComplete: function () {},
        });

        result = "ERROR: " + e;
      }
    });

    return result;
  },
};
```

### 问题 4: SSL Pinning 绕过失败

**可能原因**:

1. 应用使用了自定义的 SSL Pinning 实现
2. Native 层实现的 Pinning
3. 使用了第三方网络库(如 Cronet)

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

---

## 相关资源

### 场景延伸

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
| **绕过 TracerPid 检测** | `bypass_tracerpid.js`              | ⭐   |
| **隐藏 Frida 字符串**   | `hide_frida_strings.js`            | ⭐   |
| **绕过 SSL Pinning**    | `bypass_ssl_pinning.js`            | ⭐   |
| **拦截网络请求**        | `intercept_okhttp.js`              | ⭐⭐ |
| **RPC 调用加密函数**    | `rpc_agent.js + rpc_controller.py` | ⭐⭐ |
| **枚举 JNI 函数**       | `enumerate_jni.js`                 | ⭐   |
| **Hook JNI 函数**       | `hook_jni_function.js`             | ⭐⭐ |
| **批量 Hook JNI**       | `hook_all_jni.js`                  | ⭐⭐ |
| **Hook 构造函数**       | `hook_constructor.js`              | ⭐   |

### 常用命令

```bash
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
```

### 最佳实践

1. **优先使用 Spawn 模式** - 确保在应用启动前 Hook 就绪
2. **添加异常处理** - 防止脚本错误导致应用崩溃
3. **适度打印日志** - 过多日志会影响性能
4. **模块化组织** - 将常用函数封装为独立模块
5. **保存脚本库** - 建立自己的脚本模板库

---

**💡 提示**: 这些脚本都是**模板**,实际使用时需要根据目标 App 的具体情况进行调整。建议先理解脚本原理,再修改关键参数(如类名、方法名、SO 文件名等)。
