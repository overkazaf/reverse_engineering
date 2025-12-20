# 绕过 App 对 Frida 的检测

## 问题场景

**你遇到了什么问题？**

- 运行 Frida 后 App 立即崩溃或闪退
- App 显示"检测到调试工具"并拒绝运行
- Hook 脚本加载后 App 无响应或进入安全模式
- 某些功能在 Frida 环境下被禁用
- App 频繁弹窗提示"运行环境异常"

**本配方教你**：识别 Frida 检测技术、使用 Hook 绕过检测、定制 Frida 避免特征。

**核心理念**：

> **用 Frida 对抗检测 Frida** - 以子之矛攻子之盾
>
> - 在 App 检测之前就 Hook 检测函数
> - 修改检测结果让它"看不见" Frida
> - 或干脆隐藏 Frida 的所有特征

**预计用时**: 15-45 分钟（取决于检测复杂度）

## 工具清单

### 必需工具

- **Frida** - 动态插桩框架
- **Android 设备**（已 Root）
- **文本编辑器** - 编写绕过脚本

### 可选工具

- **jadx-gui** - 静态分析检测代码
- **IDA Pro / Ghidra** - Native 层检测分析
- **定制版 Frida** - 终极解决方案

---

## 前置条件

### 确认清单

```bash
# 1. Frida 正常运行
frida-ps -U

# 2. 能正常 attach（无检测时）
frida -U -f com.example.app

# 3. Root 权限可用
adb shell su
```

---

## 解决方案

### 第 1 步：识别检测类型（5 分钟）

#### 1.1 触发检测

**运行 Frida 并观察现象**：

```bash
# 使用 spawn 模式启动 App
frida -U -f com.example.app --no-pause

# 观察输出和 App 行为
```

**检测现象对照表**：

| 现象                   | 可能的检测方式         |
| ---------------------- | ---------------------- |
| 立即闪退               | 端口扫描、进程名检测   |
| 弹窗"检测到 Root/调试" | 模块名检测、线程名检测 |
| 特定功能被禁用         | Inline Hook 检测       |
| 随机崩溃/卡顿          | 多重检测组合           |

#### 1.2 静态分析检测代码（可选）

**用 jadx 搜索关键词**：

```text
# Frida 特征
frida
gum-js
27042

# 检测相关
/proc/self/maps
/proc/*/cmdline
pthread_create
connect
socket
```

**典型检测代码示例**：

```java
public static boolean isFridaDetected() {
    // 检查端口
    if (checkPort(27042)) return true;

    // 检查进程
    if (findProcess("frida-server")) return true;

    // 检查模块
    if (checkMaps("frida-agent")) return true;

    return false;
}
```

### 第 2 步：基础绕过（10 分钟）

**重命名 frida-server**：

```bash
# 下载 frida-server
# 重命名为无害名字
mv frida-server-16.1.4-android-arm64 system_daemon

# 推送到设备
adb push system_daemon /data/local/tmp/
adb shell "chmod 755 /data/local/tmp/system_daemon"

# 使用非标准端口启动
adb shell "/data/local/tmp/system_daemon -l 0.0.0.0:8888 &"
```

**使用 spawn 模式（重要）**：

```bash
# 推荐：Spawn 模式（最早注入）
frida -U -f com.example.app -l bypass.js --no-pause

# 不推荐：Attach 模式（检测代码可能已运行）
frida -U com.example.app -l bypass.js
```

### 第 3 步：通用绕过脚本

```javascript
Java.perform(function () {
  console.log("\n[Frida Anti-Detection] 已启动\n");

  // =====================================
  // 1. 绕过端口扫描检测
  // =====================================
  var connect = Module.findExportByName("libc.so", "connect");
  if (connect) {
    Interceptor.attach(connect, {
      onEnter: function (args) {
        var sockaddr = ptr(args[1]);
        var family = sockaddr.readU16();

        if (family === 2) {
          // AF_INET
          var port = (sockaddr.add(2).readU8() << 8) | sockaddr.add(3).readU8();
          var ip = sockaddr.add(4).readU32();

          // 检测是否在扫描 Frida 默认端口
          if (port === 27042 || port === 27043) {
            console.log("[Port] 拦截端口扫描: " + port);
            // 修改端口为无效端口
            sockaddr.add(2).writeU8(0xff);
            sockaddr.add(3).writeU8(0xff);
          }
        }
      },
    });
    console.log("[Port] Hook connect() 完成");
  }

  // =====================================
  // 2. 绕过 /proc/self/maps 检测
  // =====================================
  var fgets = Module.findExportByName("libc.so", "fgets");

  if (fgets) {
    Interceptor.attach(fgets, {
      onEnter: function (args) {
        this.buffer = args[0];
        this.fp = args[2];
      },
      onLeave: function (retval) {
        if (retval.isNull()) return;

        var line = this.buffer.readCString();
        if (line) {
          // 隐藏 Frida 相关模块
          if (
            line.includes("frida") ||
            line.includes("gum-js") ||
            line.includes("frida-agent")
          ) {
            console.log("[Maps] 隐藏模块: " + line.substring(0, 50) + "...");
            // 替换为空行
            this.buffer.writeUtf8String("\n");
          }
        }
      },
    });
    console.log("[Maps] Hook fgets() 完成");
  }

  // =====================================
  // 3. 绕过 strstr 字符串检测
  // =====================================
  var strstr = Module.findExportByName("libc.so", "strstr");
  if (strstr) {
    Interceptor.attach(strstr, {
      onEnter: function (args) {
        this.haystack = args[0].readCString();
        this.needle = args[1].readCString();

        if (
          this.needle &&
          (this.needle.includes("frida") ||
            this.needle.includes("gum-js") ||
            this.needle === "frida-agent" ||
            this.needle === "frida-server")
        ) {
          this.shouldBypass = true;
        }
      },
      onLeave: function (retval) {
        if (this.shouldBypass) {
          console.log("[Strstr] 隐藏字符串: " + this.needle);
          retval.replace(ptr(0)); // 返回 NULL（未找到）
        }
      },
    });
    console.log("[Strstr] Hook strstr() 完成");
  }

  // =====================================
  // 4. 绕过 Java 层检测函数
  // =====================================
  setTimeout(function () {
    // 搜索常见检测函数名
    var detectNames = [
      "isFridaDetected",
      "checkFrida",
      "detectDebugger",
      "isHooked",
      "checkRoot",
    ];

    Java.enumerateLoadedClasses({
      onMatch: function (className) {
        try {
          var clazz = Java.use(className);
          detectNames.forEach(function (methodName) {
            if (clazz[methodName]) {
              console.log(
                "[Java] 找到检测函数: " + className + "." + methodName
              );
              clazz[methodName].implementation = function () {
                console.log("[Java] 拦截调用: " + className + "." + methodName);
                return false; // 返回"未检测到"
              };
            }
          });
        } catch (e) {}
      },
      onComplete: function () {
        console.log("[Java] 类枚举完成");
      },
    });
  }, 500);

  // =====================================
  // 5. 绕过线程名检测
  // =====================================
  var pthread_setname_np = Module.findExportByName(
    "libc.so",
    "pthread_setname_np"
  );
  if (pthread_setname_np) {
    Interceptor.attach(pthread_setname_np, {
      onEnter: function (args) {
        var threadName = args[1].readCString();
        if (
          threadName &&
          (threadName.includes("gum-js") ||
            threadName.includes("gmain") ||
            threadName.includes("pool-"))
        ) {
          console.log("[Thread] 修改线程名: " + threadName + " → normal");
          args[1].writeUtf8String("normal");
        }
      },
    });
    console.log("[Thread] Hook pthread_setname_np() 完成");
  }

  console.log("\n[Frida Anti-Detection] 所有 Hook 已就绪\n");
});
```

**预期输出**：

```text
[Port] Hook connect() 完成
[Maps] Hook fgets() 完成
[Strstr] Hook strstr() 完成
[Thread] Hook pthread_setname_np() 完成
[Java] 类枚举完成
[Java] 找到检测函数: com.example.SecurityCheck.isFridaDetected

[Frida Anti-Detection] 所有 Hook 已就绪

[Port] 拦截端口扫描: 27042
[Strstr] 隐藏字符串: frida-agent
[Java] 拦截调用: com.example.SecurityCheck.isFridaDetected
```

### 第 4 步：针对性绕过

**如果你找到了检测函数**（从第 1 步）：

```javascript
Java.perform(function () {
  var SecurityCheck = Java.use("com.example.app.SecurityCheck");

  // Hook 检测函数
  SecurityCheck.isFridaDetected.implementation = function () {
    console.log("Bypass isFridaDetected()");
    return false; // 始终返回"未检测到"
  };

  // 拦截其他检测相关函数
  SecurityCheck.checkPort.implementation = function (port) {
    console.log("Bypass checkPort(" + port + ")");
    return false;
  };
});
```

### 第 5 步：定制 Frida（终极方案）

#### 5.1 修改源码

**克隆 Frida**：

```bash
git clone --recurse-submodules https://github.com/frida/frida.git
cd frida
```

**修改特征字符串**：

```bash
# 替换模块名
find . -type f -exec sed -i 's/frida-agent/system-agent/g' {} +
find . -type f -exec sed -i 's/frida-server/system-daemon/g' {} +

# 替换线程名
find . -type f -exec sed -i 's/gum-js-loop/normal-thread/g' {} +
find . -type f -exec sed -i 's/gmain/worker/g' {} +
```

**编译**：

```bash
make
```

---

## 原理解析

### Frida 检测点分布

```text
检测点分布：
├── 1. 网络层
│   ├── 默认端口: 27042, 27043
│   └── D-Bus 协议特征
├── 2. 进程层
│   ├── 进程名: frida-server
│   └── 命令行参数包含 "frida"
├── 3. 内存层
│   ├── 模块名: frida-agent.so, frida-gadget.so
│   ├── 线程名: gum-js-loop, gmain, pool-*
│   └── 函数 Hook: 修改系统函数字节码
└── 4. 行为层
    └── D-Bus 消息、异常系统调用序列
```

### 绕过策略对照表

| 检测方式         | 绕过策略                    |
| ---------------- | --------------------------- |
| 进程名检测       | 重命名 frida-server         |
| /proc/self/maps  | Hook `fgets()` 过滤输出     |
| 字符串检测       | Hook `strstr()` 返回 NULL   |
| 线程名检测       | Hook `pthread_setname_np()` |
| Inline Hook 检测 | Hook 检测函数本身           |
| 多重组合检测     | 定制 Frida 源码             |

### Hook 时机很重要

```text
App 启动时序：
        ↓
[0.5s] App 静态初始化代码运行
        ↓
[1s] App onCreate() 开始
        ↓
[1.5s] ⚠️ 反调试检测通常在此运行
        ↓
[2s] ❌ Attach 模式：Frida 在此时才注入（太晚）
```

---

## 常见问题

### 问题 1: 绕过脚本不生效

**症状**：Hook 脚本运行了，但 App 仍然检测到 Frida

**可能原因**：

1. **Hook 时机太晚**
    ```bash
    # 正确：--no-pause 立即运行
    frida -U -f com.example.app -l bypass.js --no-pause

    # 错误：会暂停等待手动恢复
    frida -U -f com.example.app -l bypass.js
    ```
2. **Native 层检测未覆盖**
    - 使用 `frida-gadget` 而非 `frida-server`（更早注入）
3. **存在未覆盖的检测点**
    - 使用 jadx 分析完整的检测逻辑

### 问题 2: Hook 后 App 崩溃

**症状**：加载 Hook 脚本后 App 立即崩溃

**检查**：

1. **Hook 的函数签名错误**
    ```javascript
    // 检查重载
    Java.use("ClassName").methodName.overloads.forEach(function (o) {
      console.log(o);
    });
    ```
2. **返回值类型不匹配**
    ```javascript
    // 错误
    SomeClass.returnsInt.implementation = function () {
      return "string"; // 类型错误！
    };

    // 正确
    SomeClass.returnsInt.implementation = function () {
      return 0;
    };
    ```
3. **Hook 影响了正常功能**
    - 添加条件判断，只 Hook 特定情况

### 问题 3: 某些检测绕不过去

**症状**：尝试了所有方法，仍有检测未绕过

**高级对策**：

1. **使用 frida-gadget（嵌入式）**
    ```bash
    # 解包 APK
    apktool d app.apk

    # 将 frida-gadget.so 添加到 lib/
    # 修改 AndroidManifest.xml 和 smali 代码加载 gadget
    # 参考：https://frida.re/docs/gadget/

    # 重新打包
    apktool b app -o app_patched.apk
    ```
2. **使用预编译的定制版**
    - 社区项目：https://github.com/hluwa/strongR-frida-android
    - 已重命名所有特征字符串
3. **使用 Docker 编译环境**

```bash
docker run --rm -v $(pwd):/work frida/ci
```

---

## 延伸阅读

### 相关配方

- **[Root 检测绕过](./device_fingerprinting_and_bypass.md)** - 通常与 Frida 检测一起出现
- **[SSL Pinning 绕过](../Network/network_sniffing.md#第-5-步绕过-ssl-pinning如遇到)** - 可能也有反 Frida
- **[模拟器检测绕过](./device_fingerprinting_and_bypass.md)** - 多重检测组合

### 工具深入

- **[Frida 完整指南](../../02-Tools/Dynamic/frida_guide.md)**
- **[Frida 内部原理](../../02-Tools/Dynamic/frida_internals.md)** - 理解检测原理

### 案例分析

- **[反分析技术案例](../../03-Case-Studies/case_anti_analysis_techniques.md)**
- **[社交媒体风控](../../03-Case-Studies/case_social_media_and_anti_bot.md)** - 高级检测对抗

### 进阶资源

- **strongR-frida**: https://github.com/hluwa/strongR-frida-android
- **frida-gadget 文档**: https://frida.re/docs/gadget/
- **编译 Frida**: https://frida.re/docs/building/

---

## 快速参考

### 一键绕过脚本

**下载通用绕过脚本**：

```bash
# 使用社区维护的绕过脚本
curl -O https://raw.githubusercontent.com/0xdea/frida-scripts/master/raptor_frida_android_bypass.js

# 运行
frida -U -f com.example.app -l raptor_frida_android_bypass.js --no-pause
```

### 检测点速查表

| 检测类型  | 检测位置                 | 绕过方法                    |
| --------- | ------------------------ | --------------------------- |
| 进程名    | `/proc/*/cmdline`        | 重命名 + Hook `fopen()`     |
| 模块名    | `/proc/self/maps`        | Hook `fgets()` 过滤         |
| 字符串    | `strstr()`               | Hook `strstr()`             |
| 线程名    | `/proc/self/task/*/comm` | Hook `pthread_setname_np()` |
| Java 检测 | `isFridaDetected()`      | Hook 检测函数               |

### 常用命令

```bash
# 非标准端口运行 frida-server
adb shell "/data/local/tmp/frida -l 0.0.0.0:8888 &"

# 连接到非标准端口
frida -H 127.0.0.1:8888 -f com.example.app

# Spawn 模式（重要）
frida -U -f com.example.app -l bypass.js --no-pause

# 列出所有模块（检查是否有 frida-agent）
frida -U -f com.example.app -e 'Process.enumerateModules()'

# 列出所有线程（检查线程名）
frida -U -f com.example.app -e 'Process.enumerateThreads()'
```
