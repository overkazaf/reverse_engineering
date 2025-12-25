---
title: "Frida 常用命令与脚本 API 大全"
date: 2024-10-14
tags: ["Native层", "动态分析", "Frida", "SSL Pinning", "DEX", "加密分析"]
weight: 10
---

# Frida 常用命令与脚本 API 大全

Frida 是一个动态代码插桩工具包，它允许您将自己的脚本注入到黑盒进程中。它对于逆向工程、安全研究和应用调试非常有用。

---

## 目录

- [Frida 工具集](#frida-工具集)
- [连接与附加模式](#连接与附加模式)
- [JavaScript API (核心)](#javascript-api-核心)
  - [Java (Android)](#java-android)
  - [Objective-C (iOS)](#objective-c-ios)
  - [通用/原生 (Native)](#通用原生-native)
  - [JNI (Java Native Interface)](#jni-java-native-interface)
- [常用脚本示例](#常用脚本示例)

---

## Frida 工具集

这些是在终端中使用的核心 Frida 命令行工具。

| 命令                                         | 描述                                              |
| -------------------------------------------- | ------------------------------------------------- |
| `frida --version`                            | 查看 Frida 版本                                   |
| `frida-ps -U`                                | 列出 USB 连接设备上的所有进程                     |
| `frida-ps -Ua`                               | 列出 USB 连接设备上所有正在运行的应用程序         |
| `frida-ps -Uai`                              | 列出 USB 连接设备上所有已安装的应用程序及其标识符 |
| `frida-trace -U -f <包名> -i "<方法>"`       | 跟踪指定方法的调用（附加到新进程）                |
| `frida-trace -U -p <PID> -i "<方法>"`        | 跟踪指定方法的调用（附加到现有进程）              |
| `frida -U -f <包名> -l <脚本.js>`            | Spawn 一个新进程并注入脚本                        |
| `frida -U -p <PID> -l <脚本.js>`             | 附加到现有进程并注入脚本                          |
| `frida -U --no-pause -f <包名> -l <脚本.js>` | Spawn 新进程并注入脚本，且不暂停主线程            |

---

## 连接与附加模式

Frida 有两种主要的方式来 hook 应用：

- **Spawn (Spawning)**: Frida 启动应用程序并立即暂停主线程，以便您在应用代码执行前注入脚本。这是最常用的模式，特别是对于需要在应用启动早期进行 Hook 的场景。使用 `-f <包名>` 参数。

- **Attach (Attaching)**: Frida 附加到已经在运行的进程上。这对于 hook 那些在应用运行中途才会触发的功能很有用。使用 `-p <PID>` 或应用名称。

---

## JavaScript API (核心)

这是 Frida 脚本的核心。所有逻辑都在 JavaScript 脚本中实现。

### Java (Android)

这些 API 用于与 Android 的 Java 运行时进行交互。所有 Java 相关代码都必须包裹在 `Java.perform(function() { ... });` 中。

| API/代码片段                                                            | 描述                                         |
| ----------------------------------------------------------------------- | -------------------------------------------- |
| `Java.perform(function() { ... });`                                     | Frida 中与 Java 交互的入口点和作用域         |
| `Java.available`                                                        | 检查 Java VM 是否可用                        |
| `var MyClass = Java.use('com.example.MyClass');`                        | 获取一个类的包装器，用于方法 Hook 或创建实例 |
| `MyClass.myMethod.implementation = function(...) { ... }`               | 替换（Hook）一个方法的实现                   |
| `this.myMethod(...)`                                                    | 在 Hook 的实现中调用原始方法                 |
| `MyClass.$new()`                                                        | 创建一个类的新实例                           |
| `Java.choose('com.example.MyClass', { onMatch: ..., onComplete: ... })` | 查找堆上特定类的所有活动实例                 |
| `Java.cast(obj, MyClass)`                                               | 将一个对象转换为特定的类类型                 |
| `Java.backtrace(this.context, true)`                                    | 获取当前线程的 Java 调用堆栈                 |
| `send(data)`                                                            | 从脚本向 Python/Node.js 工具发送消息         |
| `recv(callback)`                                                        | 从 Python/Node.js 工具接收消息               |

### Objective-C (iOS)

这些 API 用于与 iOS 的 Objective-C 运行时进行交互。

| API/代码片段                                                      | 描述                                  |
| ----------------------------------------------------------------- | ------------------------------------- |
| `ObjC.classes.MyClass`                                            | 获取一个类的引用                      |
| `Interceptor.attach(ObjC.classes.MyClass['- myMethod'], { ... })` | 附加到方法的实现 (Native Interceptor) |
| `ObjC.choose(ObjC.classes.MyClass, { ... })`                      | 查找特定类的所有活动实例              |
| `ObjC.available`                                                  | 检查 Objective-C 运行时是否可用       |

### 通用/原生 (Native)

这些 API 用于与原生代码（C/C++）进行交互，跨平台通用。

| API/代码片段                                                     | 描述                               |
| ---------------------------------------------------------------- | ---------------------------------- |
| `Interceptor.attach(ptr("..."), { onEnter: ..., onLeave: ... })` | 拦截指定地址的原生函数调用         |
| `Module.findExportByName("libname.so", "function_name")`         | 按名称查找模块（库）的导出函数地址 |
| `Module.findBaseAddress("libname.so")`                           | 获取模块加载的基地址               |
| `Memory.readByteArray(address, size)`                            | 从指定地址读取字节数组             |
| `Memory.writeByteArray(address, bytes)`                          | 向指定地址写入字节数组             |
| `NativeFunction(address, returnType, argTypes)`                  | 创建一个可调用的原生函数对象       |
| `ptr("0x...")`                                                   | 创建一个原生指针                   |
| `Thread.backtrace(this.context, Backtracer.ACCURATE)`            | 获取当前线程的原生调用堆栈         |

### JNI (Java Native Interface)

JNI 是 Android 逆向中的重要组成部分，Frida 提供了强大的 JNI Hook 能力。

| API/代码片段                                                     | 描述                          |
| ---------------------------------------------------------------- | ----------------------------- |
| `Module.findExportByName("lib.so", "Java_com_pkg_Class_method")` | 查找 JNI 函数地址             |
| `Java.vm.getEnv()`                                               | 获取当前线程的 JNIEnv 指针    |
| `Java.vm.tryGetEnv()`                                            | 尝试获取 JNIEnv（不会抛异常） |
| `Java.vm.perform(callback)`                                      | 在 Java 虚拟机线程中执行回调  |

---

## 常用脚本示例

### JNI Hook 示例

```javascript
// Hook JNI Function
var jni_func = Module.findExportByName(
  "libnative.so",
  "Java_com_example_app_Crypto_encrypt"
);

if (jni_func) {
  Interceptor.attach(jni_func, {
    onEnter: function (args) {
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
    onLeave: function (retval) {
      // Read returned jstring
      if (retval && !retval.isNull()) {
        var env = Java.vm.getEnv();
        var cstr = env.getStringUtfChars(retval, null);
        console.log("Output: " + cstr.readCString());
        env.releaseStringUtfChars(retval, cstr);
      }
    },
  });
}

// Also hook the native method call from Java layer
Java.perform(function () {
  var Crypto = Java.use("com.example.app.Crypto");

  Crypto.encrypt.implementation = function (input) {
    console.log("[Java Hook] encrypt called with: " + input);
    var result = this.encrypt(input);
    console.log("[Java Hook] encrypt returned: " + result);
    return result;
  };
});
```

### 枚举 JNI 函数

```javascript
function enumerateJNIFunctions(moduleName) {
  var module = Process.getModuleByName(moduleName);
  var exports = module.enumerateExports();

  console.log("[JNI Enumeration] " + moduleName);
  exports.forEach(function (exp) {
    if (exp.name.startsWith("Java_")) {
      console.log("  " + exp.name + " @ " + exp.address);
    }
  });
}

// Usage example
enumerateJNIFunctions("libnative.so");
```

### Hook Java 方法

```javascript
Java.perform(function () {
  var MyClass = Java.use("com.example.SecretClass");

  MyClass.secretMethod.implementation = function (arg1, arg2) {
    console.log("secretMethod called with:", arg1, arg2);

    // Call original method and get return value
    var retval = this.secretMethod(arg1, arg2);
    console.log("Original return value:", retval);

    return retval; // Return original value
  };
});
```

### 绕过 VIP 检查

```javascript
Java.perform(function () {
  var PremiumUtils = Java.use("com.example.PremiumUtils");

  PremiumUtils.isUserPremium.implementation = function () {
    console.log("Bypassing isUserPremium check...");
    return true; // Always return true to bypass VIP check
  };
});
```

### 查找堆上的实例

```javascript
Java.perform(function () {
  Java.choose("com.example.UserManager", {
    onMatch: function (instance) {
      console.log("Found UserManager instance:", instance);
      console.log("User ID:", instance.getUserId());
    },
    onComplete: function () {
      console.log("Search complete.");
    },
  });
});
```

### Hook 构造函数

```javascript
Java.perform(function () {
  var User = Java.use("com.example.User");

  User.$init.implementation = function (name, age) {
    console.log("User object created with name:", name, "and age:", age);

    // Call original constructor
    this.$init(name, age);
  };
});
```

### Hook Native 函数 (SSL_write)

```javascript
var ssl_write = Module.findExportByName("libssl.so", "SSL_write");

Interceptor.attach(ssl_write, {
  onEnter: function (args) {
    // args[0] is the SSL context
    // args[1] is the buffer
    // args[2] is the size
    console.log("Intercepted SSL_write, size:", args[2].toInt32());
    // You can use hexdump(args[1]) to view the data
  },
  onLeave: function (retval) {
    // retval is the original return value
    console.log("SSL_write returned:", retval.toInt32());
  },
});
```

### RPC 导出函数

**JavaScript 脚本 (script.js):**

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

**Python 调用:**

```python
import frida

# ... Connect to device and attach to process ...
# script = session.create_script(js_code)
# ...
# script.load()

# Call the exported function from the script
secret = script.exports.getsecret()
print("Secret from app:", secret)
```
