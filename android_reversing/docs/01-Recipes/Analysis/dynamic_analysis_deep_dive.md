# 使用动态分析验证和探索 Android App 的运行时行为

## 问题场景

**你遇到了什么问题？**

- 你已经静态分析找到了目标函数，现在想验证它的实际输入输出
- 你想捕获运行时才生成的数据（如动态密钥、签名结果）
- 你想绕过 SSL Pinning / 反调试 / Root 检测
- 你想主动调用函数测试不同参数的效果
- 你想追踪代码执行路径，看看哪些函数被调用了

**本配方教你**：系统性地使用 Frida、调试器、追踪工具来验证静态分析结果、获取运行时数据、绕过保护机制。

**核心理念**：

> **动态分析：让代码说话**
>
> - 动态分析验证静态分析的假设
> - 获取只在运行时存在的数据
> - 主动探索程序的内部状态
> - Hook → Debug → Trace 三种武器各有用途

**预计用时**: 30-90 分钟

---

## 工具清单

### 必需工具

- **Frida** - 动态插桩框架
- **Android 设备**（已 Root）或模拟器
- **Python 3.7+** - 运行 Frida 脚本

### 可选工具

- **IDA Pro Remote Debugger** - Native 层调试
- **objection** - Frida 的交互式工具
- **Burp Suite** - 网络抓包
- **GDB** - GNU 调试器

---

## 前置条件

### 确认清单

```bash
# 1. Frida 正常运行
frida-ps -U

# 2. Python 环境
python3 --version

# 3. 目标 App 已安装
adb shell pm list packages | grep <app_name>
```

### Hook vs Debug vs Trace：何时用什么？

| 场景                             | 推荐工具               | 理由                            |
| -------------------------------- | ---------------------- | ------------------------------- |
| 想知道某个函数的输入输出         | **Frida Hook**         | 最快速，不中断程序流            |
| 想理解复杂算法的每一步细节       | **IDA/GDB 调试器**     | 可以单步执行，查看每个变量      |
| 想知道程序执行了哪些代码路径     | **Stalker/Trace**      | 全自动记录，无需设断点          |
| 想绕过某个检测（如 SSL Pinning） | **Frida Hook**         | 直接替换函数返回值              |
| 想找到某个字符串是在哪里生成的   | **内存断点 + 调试器**  | 在写入时中断                    |
| 想分析反调试机制                 | **Frida + 调试器组合** | 先用 Frida 禁用，再用调试器分析 |

**经验法则**：

- 能用 Hook 解决的，别用调试器（效率问题）
- 需要理解逻辑的，必须用调试器（深度问题）
- 需要全局视野的，用追踪（覆盖率问题）

---

## 解决方案

### 第 1 步：验证静态分析结果（15 分钟）

假设静态分析发现了签名函数：`SignUtils.generateSign()`

#### 1.1 Hook 函数查看输入输出

**基础 Hook 脚本** `verify_sign.js`：

```javascript
Java.perform(function () {
  console.log("[*] Start Hook SignUtils.generateSign");

  var SignUtils = Java.use("com.example.SignUtils");

  SignUtils.generateSign.implementation = function (params) {
    console.log("\n[*] generateSign is called!");
    console.log("    InputParameter:");

    // Print HashMap
    var iterator = params.entrySet().iterator();
    while (iterator.hasNext()) {
      var entry = iterator.next();
      console.log("      " + entry.getKey() + " = " + entry.getValue());
    }

    // Call original function
    var result = this.generateSign(params);

    console.log("    ReturnValue: " + result);
    console.log("");

    return result;
  };

  console.log("[*] Hook install completed");
});
```

**运行结果示例**：

```text
[*] generateSign is called!
    InputParameter:
      user = test123
      timestamp = 1701234567
      action = login
    ReturnValue: a1b2c3d4e5f6g7h8i9j0
```

---

### 第 2 步：处理重载方法（10 分钟）

#### 2.1 列出所有重载

```javascript
Java.perform(function () {
  var CryptoUtil = Java.use("com.example.CryptoUtil");

  // List all encryption methods
  console.log("[*] encrypt Method overloads:");
  CryptoUtil.encrypt.overloads.forEach(function (overload) {
    console.log("    " + overload);
  });
});
```

**输出示例**：

```text
encrypt(java.lang.String)
encrypt(java.lang.String, java.lang.String)
encrypt([B)
```

#### 2.2 Hook 特定重载

```javascript
Java.perform(function () {
  var CryptoUtil = Java.use("com.example.CryptoUtil");

  // Hook the second overloaded version
  CryptoUtil.encrypt.overload(
    "java.lang.String",
    "java.lang.String"
  ).implementation = function (data, key) {
    console.log("[*] encrypt(String, String) is called");
    console.log("    Data:", data);
    console.log("    Key:", key);

    var result = this.encrypt(data, key);
    console.log("    Result:", result);

    return result;
  };

  // Hook the third overloaded version
  CryptoUtil.encrypt.overload("[B").implementation = function (bytes) {
    console.log("[*] encrypt(byte[]) is called");
    console.log("    BytesLength:", bytes.length);

    var result = this.encrypt(bytes);
    console.log("    ResultLength:", result.length);

    return result;
  };
});
```

---

### 第 3 步：主动调用函数（15 分钟）

#### 3.1 创建新实例

```javascript
Java.perform(function () {
  var CryptoUtil = Java.use("com.example.CryptoUtil");

  // Constructor accessible
  try {
    var instance = CryptoUtil.$new(); // Call no-arg constructor
    var result = instance.encrypt("Hello World", "mykey");
    console.log("[*] MainCallResult:", result);
  } catch (e) {
    console.log("[-] No way to create instance:", e);
  }
});
```

#### 3.2 使用已有实例

```javascript
Java.perform(function () {
  Java.choose("com.example.CryptoUtil", {
    onMatch: function (instance) {
      console.log("[+] Instance:", instance);

      // Actively call
      var encrypted = instance.encrypt("test data");
      console.log("[*] EncryptResult:", encrypted);

      var decrypted = instance.decrypt(encrypted);
      console.log("[*] DecryptResult:", decrypted);
    },
    onComplete: function () {
      console.log("[*] Search completed");
    },
  });
});
```

#### 3.3 调用静态方法

```javascript
Java.perform(function () {
  var SignUtils = Java.use("com.example.SignUtils");
  var HashMap = Java.use("java.util.HashMap");

  // Create Parameter
  var params = HashMap.$new();
  params.put("user", "testuser");
  params.put("timestamp", String(Date.now()));

  // Actively call static method
  var sign = SignUtils.generateSign(params);
  console.log("[*] GenerateSignature:", sign);
});
```

---

### 第 4 步：绕过安全检测（15 分钟）

#### 4.1 绕过 Root 检测

```javascript
Java.perform(function () {
  var RootDetector = Java.use("com.example.security.RootDetector");

  RootDetector.isRooted.implementation = function () {
    console.log("[*] Root Detection is Bypassed");
    return false; // Force return false (not rooted)
  };

  RootDetector.isXposedInstalled.implementation = function () {
    console.log("[*] Xposed Detection is Bypassed");
    return false;
  };
});
```

#### 4.2 绕过 SSL Pinning

```javascript
Java.perform(function () {
  // Hook OkHttp 3
  try {
    var CertificatePinner = Java.use("okhttp3.CertificatePinner");
    CertificatePinner.check.overload(
      "java.lang.String",
      "java.util.List"
    ).implementation = function (hostname, peerCertificates) {
      console.log("[*] Bypass OkHttp3 SSL Pinning:", hostname);
      return; // Return directly, skip validation
    };
    console.log("[+] OkHttp3 SSL Pinning Bypassed");
  } catch (e) {
    console.log("[-] OkHttp3 not found");
  }

  // Hook TrustManager
  try {
    var X509TrustManager = Java.use("javax.net.ssl.X509TrustManager");
    var SSLContext = Java.use("javax.net.ssl.SSLContext");

    var TrustManager = Java.registerClass({
      name: "com.example.TrustManager",
      implements: [X509TrustManager],
      methods: {
        checkClientTrusted: function (chain, authType) {},
        checkServerTrusted: function (chain, authType) {},
        getAcceptedIssuers: function () {
          return [];
        },
      },
    });

    var TrustManagers = [TrustManager.$new()];
    var SSLContext_init = SSLContext.init.overload(
      "[Ljavax.net.ssl.KeyManager;",
      "[Ljavax.net.ssl.TrustManager;",
      "java.security.SecureRandom"
    );
    SSLContext_init.implementation = function (
      keyManager,
      trustManager,
      secureRandom
    ) {
      console.log("[*] Replacing TrustManager");
      SSLContext_init.call(this, keyManager, TrustManagers, secureRandom);
    };
    console.log("[+] TrustManager Bypassed");
  } catch (e) {
    console.log("[-] TrustManager bypass failed:", e);
  }

  console.log("[*] SSL Pinning Bypass Config Completed");
});
```

---

### 第 5 步：使用 RPC 远程调用（20 分钟）

#### 5.1 定义 RPC 函数

**rpc_example.js**：

```javascript
rpc.exports = {
  // Export Function: Generate Signature
  generateSign: function (params) {
    var result = null;

    Java.perform(function () {
      var SignUtils = Java.use("com.example.SignUtils");
      var HashMap = Java.use("java.util.HashMap");

      var map = HashMap.$new();
      for (var key in params) {
        map.put(key, params[key]);
      }

      result = SignUtils.generateSign(map);
    });

    return result;
  },

  // Export Function: Encrypt Data
  encrypt: function (plaintext, key) {
    var result = null;

    Java.perform(function () {
      var CryptoUtil = Java.use("com.example.CryptoUtil");
      result = CryptoUtil.encrypt(plaintext, key);
    });

    return result;
  },
};
```

#### 5.2 Python 调用 RPC

**rpc_caller.py**：

```python
import frida
import sys
import time

def on_message(message, data):
    print(f"[*] Message: {message}")

# Connect to device
device = frida.get_usb_device()

# Attach to process
pid = device.spawn(['com.example.app'])
session = device.attach(pid)

# Load Script
with open('rpc_example.js', 'r') as f:
    script = session.create_script(f.read())

script.on('message', on_message)
script.load()

device.resume(pid)

# Wait for Script Initialize
time.sleep(2)

# Call RPC Function
params = {
    'user': 'testuser',
    'timestamp': '1701234567',
    'action': 'login'
}

sign = script.exports_sync.generate_sign(params)
print(f"[+] Generated Signature: {sign}")

encrypted = script.exports_sync.encrypt('Hello World', 'mykey')
print(f"[+] Encrypt Result: {encrypted}")

# Keep running
sys.stdin.read()
```

---

### 第 6 步：使用调试器进行深度分析（20 分钟）

#### 6.1 IDA Pro 远程调试 Native 代码

**准备**：

```bash
# 1. Push android_server to device
adb push android_server64 /data/local/tmp/
adb shell chmod 755 /data/local/tmp/android_server64

# 2. Run with root permission
adb shell su -c "/data/local/tmp/android_server64"

# 3. Port forward
adb forward tcp:23946 tcp:23946
```

**连接步骤**：

1. IDA Pro 中选择 **Debugger → Remote ARM Linux/Android debugger**
2. 配置连接参数：
   - Hostname: localhost
   - Port: 23946
3. **Debugger → Attach to Process** → 选择目标 App
4. 在目标函数处设置断点（F2）
5. 触发 App 中的操作，断点命中

#### 6.2 使用 GDB 调试

```bash
# Attach to process
adb shell
su
ps | grep <app_name>
# 找到 PID，如 12345

gdbserver :5039 --attach 12345
```

**在主机上连接**：

```bash
arm-linux-androideabi-gdb

# In GDB
(gdb) target remote :5039
(gdb) continue
```

#### 6.3 调试器快捷键

**IDA Pro**：

| 快捷键    | 功能                        |
| --------- | --------------------------- |
| `F2`      | 设置/取消断点               |
| `F9`      | 运行/继续                   |
| `F7`      | 单步进入（Step Into）       |
| `F8`      | 单步跳过（Step Over）       |
| `Ctrl+F7` | 执行到返回（Run to Return） |

**GDB**：

| 命令             | 功能       |
| ---------------- | ---------- |
| `break <addr>`   | 设置断点   |
| `continue`       | 继续执行   |
| `step`           | 单步进入   |
| `next`           | 单步跳过   |
| `finish`         | 执行到返回 |
| `info registers` | 查看寄存器 |
| `x/10x $sp`      | 查看栈内容 |

---

### 第 7 步：使用 Stalker 追踪代码覆盖率（15 分钟）

Frida Stalker 可以记录线程执行的所有指令。

#### 7.1 基础 Stalker 示例

```javascript
// Stalker trace function execution
Interceptor.attach(
  Module.findExportByName("libnative.so", "Java_com_example_Native_encrypt"),
  {
    onEnter: function (args) {
      console.log("[*] Start Tracking...");

      Stalker.follow(Process.getCurrentThreadId(), {
        events: {
          call: true, // Record Function Calls
          ret: false,
          exec: false,
        },
        onReceive: function (events) {
          console.log("[*] Captured", events.length, "events");

          // Parse events
          var calls = Stalker.parse(events, {
            annotate: true,
            stringify: false,
          });

          calls.forEach(function (call) {
            console.log("    Call:", call);
          });
        },
      });
    },
    onLeave: function (retval) {
      Stalker.unfollow(Process.getCurrentThreadId());
      Stalker.flush();
      console.log("[*] Tracking Ended");
    },
  }
);
```

#### 7.2 只追踪特定模块

```javascript
var base = Module.findBaseAddress("libnative.so");
var size = Process.findModuleByName("libnative.so").size;

Stalker.follow(Process.getCurrentThreadId(), {
  transform: function (iterator) {
    var instruction = iterator.next();
    do {
      // Only record instructions within libnative.so
      if (
        instruction.address.compare(base) >= 0 &&
        instruction.address.compare(base.add(size)) < 0
      ) {
        iterator.keep();
      }
      instruction = iterator.next();
    } while (instruction !== null);
  },
});
```

---

### 工具对比总结

| 工具       | 最佳场景     | 优点       | 缺点         |
| ---------- | ------------ | ---------- | ------------ |
| Frida Hook | 快速获取 I/O | 不中断流程 | 只看单点     |
|            | 修改返回值   | 易于自动化 | 不知道细节   |
| 调试器     | 理解算法逻辑 | 完全控制   | 速度慢       |
| (IDA/GDB)  | 单步跟踪     | 看所有变量 | 需要手动操作 |
| Stalker    | 代码覆盖率   | 全自动     | 性能开销大   |
|            | 追踪执行路径 | 无需断点   | 输出量巨大   |

---

### RPC 调用流程

```text
Python 脚本                    Frida 脚本
     |                              |
     | Send RPC Request             |
     | ---------------------------> |
     |                              | Execute Java.perform()
     |                              |
     |                              | Call App Function
     |                              |
     | <--------------------------- |
     | Receive Return Value         | Return Result
     |                              |
     | Process Data                 | Completed
```

---

## 常见问题

### 问题 1: Hook 没有触发

**检查清单**：

1. **确认类/方法名正确**
    ```javascript
    // List all classes
    Java.enumerateLoadedClasses({
      onMatch: function (className) {
        if (className.includes("SignUtils")) {
          console.log(className);
        }
      },
      onComplete: function () {},
    });
    ```
2. **确认方法被调用**
    - 在 App 中触发相关操作
    - 检查是否有其他代码路径
3. **检查混淆**
    ```javascript
    // If class name is obfuscated as a.b.c, use obfuscated name
    var SignUtils = Java.use("a.b.c");
    ```

### 问题 2: RPC 调用超时

**症状**：`script.exports_sync.func()` 一直等待

**解决**：

```python
# Use async call
def on_rpc_message(result, error):
    if error:
        print(f"[-] Error: {error}")
    else:
        print(f"[+] Result: {result}")

script.exports.func(params, on_rpc_message)

# Or add timeout
result = script.exports_sync.func(params, timeout=10)
```

### 问题 3: Frida 被检测

**常见检测方式**：

1. **检查端口**

```java
// App Code
Socket socket = new Socket("127.0.0.1", 27042); // Frida default port
```

**绕过**：修改 Frida Server 端口

```bash
frida-server -l 0.0.0.0:8888
```

2. **检查 maps 文件**

```java
BufferedReader reader = new BufferedReader(new FileReader("/proc/self/maps"));
if (line.contains("frida")) {
    System.exit(0);
}
```

**绕过**：使用魔改版 Frida

```bash
# strongR-frida
wget https://github.com/hluwa/strongR-frida-android/releases/download/xxx/frida-server
```

### 问题 4: 调试器无法附加

**症状**：IDA Pro 显示 "Cannot attach to process"

**解决**：

1. **检查 SELinux**
    ```bash
    adb shell getenforce
    # If is Enforcing
    adb shell setenforce 0
    ```
2. **确认进程存在**
    ```bash
    adb shell ps | grep <app_name>
    # 确认 PID 正确
    ```
3. **检查 ptrace 权限**
    ```bash
    adb shell
    su
    echo 0 > /proc/sys/kernel/yama/ptrace_scope
    ```

### 问题 5: Stalker 导致 App 卡死

**症状**：启用 Stalker 后 App 卡死

**优化**：

1. **只追踪关键模块**（见第 7.2 步）
2. **减少事件类型**
    ```javascript
    events: {
        call: true,   // Only record function calls
        ret: false,   // Don't record returns
        exec: false   // Don't record every instruction
    }
    ```
3. **使用 transform 过滤**
    ```javascript
    transform: function(iterator) {
        // Skip code we don't care about
    }
    ```

---

## 延伸阅读

### 相关配方

- **[静态分析深入](./static_analysis_deep_dive.md)** - 先静态找到目标
- **[Frida 常用脚本](../Scripts/frida_common_scripts.md)** - Hook 脚本模板
- **[Frida 反调试](../Anti-Detection/frida_anti_debugging.md)** - 绕过检测
- **[SSL Pinning 绕过](../Network/network_sniffing.md#绕过-ssl-pinning)** - 抓包必备

### 工具深入

- **[Frida 完整指南](../../02-Tools/Dynamic/frida_guide.md)**
- **[IDA Pro 调试](../../02-Tools/Static/ida_pro_guide.md#远程调试)**

### 在线资源

| 资源            | 链接                        |
| --------------- | --------------------------- |
| Frida 官方文档  | https://frida.re/docs/      |
| Frida Codeshare | https://codeshare.frida.re/ |
| Frida Handbook  | https://learnfrida.info/    |

### 理论基础

- **[ARM 汇编](../../04-Reference/Foundations/arm_assembly.md)** - 理解 Native 调试
- **[ART 运行时](../../04-Reference/Foundations/art_runtime.md)** - 理解 Java Hook

---

## 快速参考

### Frida Hook 模板

**Hook Java 方法**：

```javascript
Java.perform(function () {
  var ClassName = Java.use("com.example.ClassName");

  ClassName.methodName.implementation = function (arg1, arg2) {
    console.log("[*] methodName called");
    console.log("    arg1:", arg1);
    console.log("    arg2:", arg2);

    var result = this.methodName(arg1, arg2);
    console.log("    result:", result);

    return result;
  };
});
```

**Hook Native 方法**：

```javascript
Interceptor.attach(Module.findExportByName("libnative.so", "native_func"), {
  onEnter: function (args) {
    console.log("[*] native_func called");
    console.log("    arg0:", args[0]);
    console.log("    arg1:", args[1]);
  },
  onLeave: function (retval) {
    console.log("    retval:", retval);
  },
});
```

**RPC 导出模板**：

```javascript
rpc.exports = {
  callMethod: function (className, methodName, args) {
    var result = null;
    Java.perform(function () {
      var Class = Java.use(className);
      result = Class[methodName].apply(Class, args);
    });
    return result;
  },
};
```

### IDA Pro 调试快捷键

| 快捷键    | 功能       |
| --------- | ---------- |
| `F2`      | 设置断点   |
| `F9`      | 继续执行   |
| `F7`      | 单步进入   |
| `F8`      | 单步跳过   |
| `Ctrl+F7` | 执行到返回 |

### GDB 常用命令

| 命令             | 功能       |
| ---------------- | ---------- |
| `break <addr>`   | 设置断点   |
| `continue`       | 继续执行   |
| `step`           | 单步进入   |
| `next`           | 单步跳过   |
| `finish`         | 执行到返回 |
| `info registers` | 查看寄存器 |
| `x/10x $sp`      | 查看栈内容 |

---

**成功验证分析结果了吗？** 现在你可以获取运行时数据了！

下一步推荐：[Frida 常用脚本](../Scripts/frida_common_scripts.md)（更多实用脚本模板）
