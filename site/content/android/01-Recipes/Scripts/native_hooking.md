---
title: "Native 层 Hook 技巧 (Native Hooking Patterns)"
date: 2024-10-03
type: posts
tags: ["Native层", "Frida脚本", "Frida", "代理池", "DEX", "脱壳"]
weight: 10
---

# Native 层 Hook 技巧 (Native Hooking Patterns)

> **📚 前置知识**
>
> 本配方涉及以下核心技术，建议先阅读相关章节：
>
> - **[Frida Native Hook](../../02-Tools/Dynamic/frida_guide.md#native-hook)** - 掌握 Interceptor API
> - **[SO/ELF 格式](../../04-Reference/Foundations/so_elf_format.md)** - 理解 libc 函数与符号
> - **[ARM 汇编入门](../../04-Reference/Foundations/arm_assembly.md)** - 理解 Inline Hook 原理
> - **[二进制分析工具链](../../04-Reference/Foundations/binary_analysis_toolkit.md)** - Capstone 反汇编与指令分析

在 Android 逆向中，Native 层 (C/C++) 的分析往往比 Java 层更具挑战性。Hook 标准 C 库 (libc) 函数是理解 Native 层行为、脱壳和还原算法的重要手段。

---

## 1. 文件操作监控 (File I/O)

监控文件操作可以帮助我们发现 App 读取了哪些配置文件、加载了哪些 Dex/So 文件，或者将解密后的数据写入到了哪里。

### Hook `open` / `openat`

```javascript
// Hook open and openat to trace file access
function hookFileOpen() {
  // Intercept 'open'
  var openPtr = Module.findExportByName("libc.so", "open");
  if (openPtr) {
    Interceptor.attach(openPtr, {
      onEnter: function (args) {
        this.path = args[0].readCString();
        this.flags = args[1].toInt32();
      },
      onLeave: function (retval) {
        if (
          this.path &&
          (this.path.endsWith(".dex") || this.path.endsWith(".so"))
        ) {
          console.log("[open] FD: " + retval + " Path: " + this.path);
        }
      },
    });
  }

  // Intercept 'openat' (commonly used on newer android versions)
  var openatPtr = Module.findExportByName("libc.so", "openat");
  if (openatPtr) {
    Interceptor.attach(openatPtr, {
      onEnter: function (args) {
        // args[0] is dirfd, args[1] is path
        this.path = args[1].readCString();
        this.flags = args[2].toInt32();
      },
      onLeave: function (retval) {
        if (
          this.path &&
          (this.path.indexOf("base.apk") >= 0 || this.path.indexOf(".dex") >= 0)
        ) {
          console.log("[openat] FD: " + retval + " Path: " + this.path);
        }
      },
    });
  }
}

hookFileOpen();
```

---

## 2. 动态库加载监控 (dlopen)

监控 `dlopen` 可以帮助我们发现 App 动态加载了哪些 SO 文件，这对于分析加壳应用非常有用。

### Hook `dlopen` / `android_dlopen_ext`

```javascript
function hookDlopen() {
  var dlopen = Module.findExportByName(null, "dlopen");
  var android_dlopen_ext = Module.findExportByName(null, "android_dlopen_ext");

  if (dlopen) {
    Interceptor.attach(dlopen, {
      onEnter: function (args) {
        this.path = args[0].readCString();
      },
      onLeave: function (retval) {
        if (this.path) {
          console.log("[dlopen] " + this.path + " -> Handle: " + retval);
          if (this.path.indexOf("libnative-lib.so") >= 0) {
            // Library loaded, ready to hook functions inside it
            console.log("[+] Target library loaded!");
          }
        }
      },
    });
  }

  if (android_dlopen_ext) {
    Interceptor.attach(android_dlopen_ext, {
      onEnter: function (args) {
        this.path = args[0].readCString();
      },
      onLeave: function (retval) {
        if (this.path) {
          console.log(
            "[android_dlopen_ext] " + this.path + " -> Handle: " + retval
          );
        }
      },
    });
  }
}

hookDlopen();
```

---

## 3. 内存操作监控 (memcpy)

监控 `memcpy` 可以帮助我们发现内存中的数据拷贝，特别是在脱壳时可以捕获解密后的 DEX 文件。

### Hook `memcpy`

```javascript
function hookMemcpy() {
  var memcpy = Module.findExportByName("libc.so", "memcpy");

  Interceptor.attach(memcpy, {
    onEnter: function (args) {
      this.dest = args[0];
      this.src = args[1];
      this.n = args[2].toInt32();
    },
    onLeave: function (retval) {
      // Filter by size or content to reduce noise
      if (this.n > 100 && this.n < 200) {
        // Check if source contains specific magic bytes (e.g., ELF header)
        try {
          var magic = this.src.readU32();
          if (magic == 0x464c457f) {
            // .ELF
            console.log("[memcpy] ELF header detected! Size: " + this.n);
            console.log(hexdump(this.src, { length: 32 }));
          }
        } catch (e) {}
      }

      // Check for DEX magic (dex\n035)
      if (this.n > 1000) {
        try {
          var dexMagic = this.src.readUtf8String(4);
          if (dexMagic === "dex\n") {
            console.log("[memcpy] DEX file detected! Size: " + this.n);
            // Dump DEX file
            var dexData = this.src.readByteArray(this.n);
            var filename = "/data/local/tmp/dump_" + Date.now() + ".dex";
            var file = new File(filename, "wb");
            file.write(dexData);
            file.close();
            console.log("[+] DEX dumped to: " + filename);
          }
        } catch (e) {}
      }
    },
  });
}

hookMemcpy();
```

---

## 4. 符号解析监控 (dlsym)

监控 `dlsym` 可以帮助我们发现 App 动态查找了哪些函数，这对于分析混淆代码非常有用。

### Hook `dlsym`

```javascript
function hookDlsym() {
  var dlsym = Module.findExportByName(null, "dlsym");

  Interceptor.attach(dlsym, {
    onEnter: function (args) {
      this.handle = args[0];
      this.symbol = args[1].readCString();
    },
    onLeave: function (retval) {
      if (this.symbol) {
        console.log(
          "[dlsym] Symbol: " + this.symbol + " -> Address: " + retval
        );

        // Hook specific functions when resolved
        if (this.symbol === "encrypt" && !retval.isNull()) {
          console.log("[+] Found encrypt function, hooking...");
          hookNativeFunction(retval, "encrypt");
        }
      }
    },
  });
}

function hookNativeFunction(addr, name) {
  Interceptor.attach(addr, {
    onEnter: function (args) {
      console.log("[" + name + "] called");
      console.log("  arg0: " + args[0]);
      console.log("  arg1: " + args[1]);
    },
    onLeave: function (retval) {
      console.log("  retval: " + retval);
    },
  });
}

hookDlsym();
```

---

## 5. 字符串比较监控 (strcmp)

监控字符串比较函数可以帮助我们发现 App 的校验逻辑，如 Root 检测、调试检测等。

### Hook `strcmp` / `strstr`

```javascript
function hookStringFunctions() {
  // Hook strcmp
  var strcmp = Module.findExportByName("libc.so", "strcmp");
  if (strcmp) {
    Interceptor.attach(strcmp, {
      onEnter: function (args) {
        var s1 = args[0].readCString();
        var s2 = args[1].readCString();

        // Filter for interesting strings
        var keywords = ["root", "su", "magisk", "frida", "xposed", "debug"];
        for (var i = 0; i < keywords.length; i++) {
          if (
            (s1 && s1.toLowerCase().indexOf(keywords[i]) >= 0) ||
            (s2 && s2.toLowerCase().indexOf(keywords[i]) >= 0)
          ) {
            console.log("[strcmp] " + s1 + " VS " + s2);
            break;
          }
        }
      },
    });
  }

  // Hook strstr
  var strstr = Module.findExportByName("libc.so", "strstr");
  if (strstr) {
    Interceptor.attach(strstr, {
      onEnter: function (args) {
        this.haystack = args[0].readCString();
        this.needle = args[1].readCString();
      },
      onLeave: function (retval) {
        if (this.needle && this.needle.toLowerCase().indexOf("frida") >= 0) {
          console.log(
            "[strstr] Searching for: " +
              this.needle +
              " in: " +
              this.haystack.substring(0, 50)
          );
          // Return NULL to bypass detection
          retval.replace(ptr(0));
        }
      },
    });
  }
}

hookStringFunctions();
```

---

## 6. 系统调用监控

监控系统调用可以帮助我们发现 App 的底层行为。

### Hook `syscall`

```javascript
function hookSyscall() {
  var syscall = Module.findExportByName("libc.so", "syscall");

  if (syscall) {
    Interceptor.attach(syscall, {
      onEnter: function (args) {
        var syscallNumber = args[0].toInt32();

        // Common syscall numbers on ARM64
        var syscallNames = {
          56: "openat",
          57: "close",
          63: "read",
          64: "write",
          78: "readlinkat",
          79: "fstatat",
          101: "nanosleep",
          172: "getpid",
          174: "getuid",
        };

        if (syscallNames[syscallNumber]) {
          console.log("[syscall] " + syscallNames[syscallNumber]);
        }
      },
    });
  }
}

hookSyscall();
```

---

## 7. 综合示例：脱壳辅助

结合多个 Hook 点进行脱壳分析。

```javascript
// Comprehensive unpacking helper
function unpackHelper() {
  console.log("[+] Unpacking helper started");

  var dexCount = 0;

  // Hook mmap to catch memory mapping
  var mmap = Module.findExportByName("libc.so", "mmap");
  Interceptor.attach(mmap, {
    onEnter: function (args) {
      this.addr = args[0];
      this.length = args[1].toInt32();
      this.prot = args[2].toInt32();
    },
    onLeave: function (retval) {
      if (this.length > 100000 && this.prot == 5) {
        // PROT_READ | PROT_EXEC
        try {
          var magic = retval.readUtf8String(4);
          if (magic === "dex\n") {
            console.log(
              "[mmap] DEX detected! Size: " + this.length + " Address: " + retval
            );
            dexCount++;
            var filename =
              "/data/local/tmp/unpack_" + dexCount + "_" + Date.now() + ".dex";
            var file = new File(filename, "wb");
            file.write(retval.readByteArray(this.length));
            file.close();
            console.log("[+] Dumped to: " + filename);
          }
        } catch (e) {}
      }
    },
  });

  // Hook dvmDexFileOpenPartial (for Dalvik)
  // Hook art::DexFile::Open (for ART)
  var artDexOpen = Module.findExportByName(
    "libart.so",
    "_ZN3art7DexFile10OpenMemoryEPKhjRKNSt3__112basic_stringIcNS3_11char_traitsIcEENS3_9allocatorIcEEEEjPNS_6MemMapEPKNS_7OatFileEPS9_"
  );
  if (artDexOpen) {
    Interceptor.attach(artDexOpen, {
      onEnter: function (args) {
        console.log("[art::DexFile::OpenMemory] called");
        this.base = args[0];
        this.size = args[1].toInt32();
      },
      onLeave: function (retval) {
        if (this.size > 0) {
          console.log("[+] ART DEX loaded, size: " + this.size);
        }
      },
    });
  }
}

unpackHelper();
```

---

## 8. Inline Hook 技术详解

Inline Hook 是 Native 层 Hook 的核心技术，通过直接修改目标函数的机器指令来实现函数拦截。与 GOT/PLT Hook 不同，Inline Hook 可以 Hook 任意函数地址，包括内部函数。

### 8.1 Inline Hook 原理

Inline Hook 的基本原理是：

1. **备份原指令**：保存目标函数开头的若干字节指令
2. **写入跳转指令**：在原位置写入跳转到 Hook 函数的指令
3. **执行 Hook 函数**：Hook 函数执行自定义逻辑
4. **执行原函数**：通过 Trampoline 跳回执行原始指令

```text
原始函数:                      Hook 后:
+------------------+           +------------------+
| 原始指令 1       |  ───>     | JMP hook_func    |
| 原始指令 2       |           | (覆盖原指令)      |
| 原始指令 3       |           | 原始指令 3       |
| ...              |           | ...              |
+------------------+           +------------------+

Hook 函数:                     Trampoline:
+------------------+           +------------------+
| 自定义逻辑       |           | 原始指令 1       |
| call_original()  |  ───>     | 原始指令 2       |
| 返回             |           | JMP 原函数+偏移  |
+------------------+           +------------------+
```

### 8.2 ARM64 跳转指令

在 ARM64 架构上，常用的跳转方式：

```c
// 方式1: B 指令 (±128MB 范围)
// B <offset>
// 4 字节，范围有限

// 方式2: LDR + BR 组合 (任意地址)
// LDR X17, #8    ; 加载后面的地址到 X17
// BR X17         ; 跳转到 X17
// .quad <addr>   ; 64位目标地址
// 共 16 字节

// 方式3: ADRP + ADD + BR (±4GB 范围)
// ADRP X17, <page>
// ADD X17, X17, <offset>
// BR X17
// 12 字节
```

### 8.3 主流 Inline Hook 框架

#### Substrate (Cydia Substrate)

最早的 iOS/Android Hook 框架，业界标准。

```c
// Substrate API
#include <substrate.h>

// 原函数指针
static int (*orig_open)(const char *path, int flags, ...);

// Hook 函数
int hook_open(const char *path, int flags, ...) {
    // 自定义逻辑
    __android_log_print(ANDROID_LOG_DEBUG, "HOOK", "open: %s", path);

    // 调用原函数
    return orig_open(path, flags);
}

// 安装 Hook
MSHookFunction((void *)open, (void *)hook_open, (void **)&orig_open);
```

#### Dobby

跨平台的轻量级 Hook 框架，支持 ARM/ARM64/x86/x86_64。

```c
// Dobby API
#include "dobby.h"

// 原函数指针
static int (*orig_open)(const char *path, int flags, mode_t mode);

// Hook 函数
int hook_open(const char *path, int flags, mode_t mode) {
    LOG("open: %s", path);
    return orig_open(path, flags, mode);
}

// 安装 Hook
DobbyHook((void *)open, (void *)hook_open, (void **)&orig_open);

// 卸载 Hook
DobbyDestroy((void *)open);
```

#### xHook (爱奇艺开源)

基于 PLT/GOT 的 Hook 框架，稳定性好，但只能 Hook 外部函数调用。

```c
// xHook API
#include "xhook.h"

// Hook 函数
int my_open(const char *path, int flags, ...) {
    LOG("xhook open: %s", path);
    // 调用原函数需要使用 xhook 的方式
    return XHOOK_CALL_ORIG(open, path, flags);
}

// 注册 Hook
xhook_register(".*\\.so$", "open", my_open, NULL);

// 刷新 Hook
xhook_refresh(0);
```

#### bhook (字节跳动开源)

PLT Hook 框架，支持自动管理 Hook 代理。

```c
// bhook API
#include "bytehook.h"

// Hook 函数
int my_open(const char *path, int flags, mode_t mode) {
    LOG("bhook open: %s", path);

    // 调用原函数
    BYTEHOOK_CALL_PREV(my_open, path, flags, mode);
    return result;
}

// 注册 Hook
bytehook_hook_single(
    "libc.so",           // 目标库
    NULL,                // 调用者 (NULL = 所有)
    "open",              // 函数名
    (void *)my_open,     // Hook 函数
    NULL,                // 回调
    NULL                 // 用户数据
);
```

#### ShadowHook (字节跳动开源)

真正的 Inline Hook 框架，支持 Hook 任意函数。

```c
// ShadowHook API
#include "shadowhook.h"

// 原函数类型
typedef int (*open_t)(const char *, int, mode_t);
static open_t orig_open;

// Hook 函数
int hook_open(const char *path, int flags, mode_t mode) {
    LOG("shadowhook open: %s", path);
    return orig_open(path, flags, mode);
}

// 安装 Inline Hook
void *stub = shadowhook_hook_func_addr(
    (void *)open,           // 目标函数地址
    (void *)hook_open,      // Hook 函数
    (void **)&orig_open     // 原函数指针
);

// 卸载 Hook
shadowhook_unhook(stub);
```

#### And-Hook

轻量级 Android Inline Hook 库。

```c
// And-Hook API
#include "And64InlineHook.hpp"

// Hook
A64HookFunction((void *)target_func, (void *)hook_func, (void **)&orig_func);
```

#### Whale

支持多种 Hook 模式的框架。

```c
// Whale API - Inline Hook
WInlineHookFunction((void *)open, (void *)hook_open, (void **)&orig_open);

// Whale API - Import Hook (类似 PLT Hook)
WImportHookFunction("libnative.so", "open", (void *)hook_open, (void **)&orig_open);
```

### 8.4 框架选型对比

| 框架 | Hook 类型 | 架构支持 | 稳定性 | 性能 | 适用场景 |
|------|----------|---------|--------|------|---------|
| **Substrate** | Inline | ARM/ARM64/x86 | ★★★★★ | ★★★★ | 通用 Hook，Xposed/Cydia |
| **Dobby** | Inline | ARM/ARM64/x86/x64 | ★★★★ | ★★★★★ | 跨平台，轻量级 |
| **xHook** | PLT/GOT | ARM/ARM64/x86/x64 | ★★★★★ | ★★★★ | 外部函数 Hook |
| **bhook** | PLT/GOT | ARM/ARM64 | ★★★★★ | ★★★★★ | 外部函数 Hook，自动代理 |
| **ShadowHook** | Inline | ARM/ARM64 | ★★★★ | ★★★★★ | 任意函数 Hook |
| **And-Hook** | Inline | ARM/ARM64 | ★★★ | ★★★★ | 简单场景 |
| **Whale** | Inline/Import | ARM/ARM64 | ★★★ | ★★★ | 多模式需求 |

### 8.5 选型建议

1. **只需要 Hook 外部函数调用** → 优先选择 **bhook** 或 **xHook**
   - 稳定性高，兼容性好
   - 不需要处理指令重定位

2. **需要 Hook 任意函数地址** → 选择 **ShadowHook** 或 **Dobby**
   - ShadowHook 对 Android 优化更好
   - Dobby 跨平台能力强

3. **Xposed 模块开发** → 使用 **Substrate** 或 **Dobby**
   - Substrate 是 Xposed 默认使用的框架
   - Dobby 作为替代方案也很成熟

4. **性能敏感场景** → **bhook** > **ShadowHook** > **Dobby**
   - PLT Hook 性能开销最小
   - Inline Hook 需要更多处理

### 8.6 Frida 中的 Inline Hook

Frida 的 `Interceptor.attach` 内部也是使用 Inline Hook 实现的：

```javascript
// Frida 使用内置的 Inline Hook 引擎
Interceptor.attach(Module.findExportByName("libc.so", "open"), {
    onEnter: function(args) {
        console.log("open:", args[0].readCString());
    },
    onLeave: function(retval) {
        console.log("  -> fd:", retval);
    }
});

// Frida 也支持直接替换函数
Interceptor.replace(targetAddr, new NativeCallback(function(arg0, arg1) {
    console.log("Replaced function called");
    return 0;
}, 'int', ['pointer', 'int']));
```

### 8.7 实战示例：使用 Dobby Hook JNI 函数

```c
#include <jni.h>
#include <android/log.h>
#include "dobby.h"

#define LOG(...) __android_log_print(ANDROID_LOG_DEBUG, "DobbyHook", __VA_ARGS__)

// 原函数指针
static jstring (*orig_NewStringUTF)(JNIEnv *env, const char *bytes);

// Hook 函数
jstring hook_NewStringUTF(JNIEnv *env, const char *bytes) {
    LOG("NewStringUTF: %s", bytes);

    // 可以修改字符串
    if (strstr(bytes, "secret") != NULL) {
        return orig_NewStringUTF(env, "hooked!");
    }

    return orig_NewStringUTF(env, bytes);
}

// 获取 JNI 函数地址
void *get_jni_func(JNIEnv *env, const char *name) {
    // JNINativeInterface 结构体偏移
    // NewStringUTF 在 JNINativeInterface 中的偏移是 167
    void **jni_funcs = *(void ***)env;
    return jni_funcs[167];  // NewStringUTF offset
}

// 初始化 Hook
void init_hooks(JNIEnv *env) {
    void *NewStringUTF_addr = get_jni_func(env, "NewStringUTF");

    DobbyHook(
        NewStringUTF_addr,
        (void *)hook_NewStringUTF,
        (void **)&orig_NewStringUTF
    );

    LOG("Hook installed at %p", NewStringUTF_addr);
}

JNIEXPORT jint JNI_OnLoad(JavaVM *vm, void *reserved) {
    JNIEnv *env;
    vm->GetEnv((void **)&env, JNI_VERSION_1_6);

    init_hooks(env);

    return JNI_VERSION_1_6;
}
```

### 8.8 注意事项

1. **线程安全**：Hook 安装时需要考虑多线程并发执行
2. **指令对齐**：ARM 指令需要 4 字节对齐，Thumb 需要 2 字节对齐
3. **指令重定位**：被覆盖的指令如果包含 PC 相对寻址，需要重新计算
4. **缓存刷新**：修改代码后需要刷新 CPU 指令缓存
5. **权限检查**：需要确保内存页有可写权限 (mprotect)

---

## 总结

Native 层 Hook 是 Android 逆向的核心技能之一。通过 Hook libc 函数（如 open、dlopen、memcpy、strcmp 等），我们可以：

1. 监控文件操作，发现配置文件和动态加载的库
2. 跟踪内存操作，捕获解密后的数据
3. 分析字符串比较，绕过安全检测
4. 进行脱壳分析，提取被保护的 DEX 文件

在技术选型时：

- **PLT/GOT Hook** (xHook, bhook)：稳定性好，适合 Hook 外部函数调用
- **Inline Hook** (Dobby, ShadowHook)：灵活性强，可以 Hook 任意地址
- **Frida Interceptor**：开发效率高，适合快速分析和原型验证

在实践中，需要根据目标应用的具体行为和需求来选择合适的 Hook 技术和框架。
