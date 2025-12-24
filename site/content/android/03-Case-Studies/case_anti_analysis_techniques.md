---
title: "反分析技术案例"
weight: 10
---

# 反分析技术案例

> **📚 前置知识**
>
> 本案例涉及以下核心技术，建议先阅读相关章节：
>
> - **[R15: Frida 反调试绕过](../01-Recipes/Anti-Detection/frida_anti_debugging.md)** - Frida 检测绕过技术
> - **[T01: Frida 使用指南](../02-Tools/Dynamic/frida_guide.md)** - 掌握 Hook 绕过反分析检测
> - **[F07: SO/ELF 文件格式](../04-Reference/Foundations/so_elf_format.md)** - 理解 Native 层检测原理

为了保护其核心代码和数据不被轻易分析，现代 App 普遍采用了一系列的反分析技术。这些技术旨在检测和阻止调试器、Hook 框架（如 Frida、Xposed）、模拟器和 Root 环境的运行。本案例将分类介绍这些技术的实现原理和对应的绕过策略。

---

## 技术概览

```
┌─────────────────────────────────────────────────────────────────┐
│                      反分析技术体系                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   反调试     │  │   反 Hook    │  │  反模拟器    │          │
│  │ Anti-Debug   │  │ Anti-Hook    │  │ Anti-Emulator│          │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤          │
│  │ TracerPid    │  │ Frida 端口   │  │ 系统属性     │          │
│  │ ptrace       │  │ 内存特征     │  │ 特有文件     │          │
│  │ 时间检测     │  │ Inline Hook  │  │ CPU 信息     │          │
│  │ 断点检测     │  │ Xposed 检测  │  │ 传感器数据   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Root 检测  │  │  完整性校验  │  │  SSL Pinning │          │
│  │ Root Detect  │  │  Integrity   │  │  证书绑定    │          │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤          │
│  │ su 文件      │  │ 签名校验     │  │ 证书指纹     │          │
│  │ Magisk 检测  │  │ DEX 校验     │  │ 公钥绑定     │          │
│  │ SELinux      │  │ SO 校验      │  │ 证书链验证   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1. 反调试 (Anti-Debugging)

**目标**: 检测 App 是否正被调试器附加。

### 1.1 基于 TracerPid 的检测

在 Linux 内核中，每个进程的 `/proc/<pid>/status` 文件都记录了其状态信息，其中 `TracerPid` 字段表示正在追踪（调试）该进程的进程 PID。如果进程没有被调试，该值为 0。

**实现原理**:

```c
// Native (C/C++) 实现 - TracerPid 检测
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <pthread.h>

int check_tracer_pid() {
    FILE *fp = fopen("/proc/self/status", "r");
    if (fp == NULL) {
        return 0;
    }

    char line[128];
    int tracer_pid = 0;

    while (fgets(line, sizeof(line), fp)) {
        if (strncmp(line, "TracerPid:", 10) == 0) {
            sscanf(line, "TracerPid:\t%d", &tracer_pid);
            break;
        }
    }

    fclose(fp);
    return tracer_pid;
}

// 后台线程持续检测
void* anti_debug_thread(void* arg) {
    while (1) {
        if (check_tracer_pid() != 0) {
            // 检测到调试器，执行保护逻辑
            kill(getpid(), SIGKILL);
        }
        usleep(100000);  // 100ms 间隔
    }
    return NULL;
}

// 在 JNI_OnLoad 或初始化函数中启动检测线程
void start_anti_debug() {
    pthread_t thread;
    pthread_create(&thread, NULL, anti_debug_thread, NULL);
    pthread_detach(thread);
}
```

**绕过策略 - Frida Hook**:

```javascript
// Frida 脚本 - 绕过 TracerPid 检测
Interceptor.attach(Module.findExportByName("libc.so", "fopen"), {
    onEnter: function(args) {
        this.path = args[0].readCString();
    },
    onLeave: function(retval) {
        if (this.path && this.path.indexOf("/proc/") !== -1 &&
            this.path.indexOf("/status") !== -1) {
            this.statusFile = retval;
        }
    }
});

Interceptor.attach(Module.findExportByName("libc.so", "fgets"), {
    onLeave: function(retval) {
        if (retval.isNull()) return;

        var line = retval.readCString();
        if (line && line.indexOf("TracerPid:") !== -1) {
            // 将 TracerPid 改为 0
            var newLine = "TracerPid:\t0\n";
            retval.writeUtf8String(newLine);
            console.log("[*] TracerPid spoofed to 0");
        }
    }
});
```

### 1.2 ptrace 自附加检测

一个进程同一时间只能被一个调试器附加。App 可以先 ptrace 自己，使得其他调试器无法再附加。

**实现原理**:

```c
// Native (C/C++) 实现 - ptrace 自附加
#include <sys/ptrace.h>
#include <sys/wait.h>
#include <unistd.h>
#include <stdlib.h>

void anti_debug_ptrace() {
    // 方法1: 直接 ptrace 自己
    if (ptrace(PTRACE_TRACEME, 0, NULL, NULL) == -1) {
        // 如果失败，说明已经被调试
        exit(0);
    }
}

void anti_debug_ptrace_fork() {
    // 方法2: fork 子进程来 ptrace 父进程
    pid_t child = fork();

    if (child == 0) {
        // 子进程
        pid_t parent = getppid();

        // 附加到父进程
        if (ptrace(PTRACE_ATTACH, parent, NULL, NULL) == -1) {
            // 父进程已被调试
            kill(parent, SIGKILL);
            exit(0);
        }

        // 等待父进程停止
        waitpid(parent, NULL, 0);

        // 继续父进程执行
        ptrace(PTRACE_CONT, parent, NULL, NULL);

        // 持续监控
        while (1) {
            int status;
            waitpid(parent, &status, 0);

            if (WIFEXITED(status) || WIFSIGNALED(status)) {
                exit(0);
            }

            ptrace(PTRACE_CONT, parent, NULL, NULL);
        }
    }
}
```

**绕过策略 - Frida Hook**:

```javascript
// Frida 脚本 - 绕过 ptrace 检测
var ptrace = Module.findExportByName(null, "ptrace");

Interceptor.attach(ptrace, {
    onEnter: function(args) {
        this.request = args[0].toInt32();
        console.log("[*] ptrace called with request: " + this.request);
    },
    onLeave: function(retval) {
        // PTRACE_TRACEME = 0
        if (this.request === 0) {
            retval.replace(0);  // 返回成功
            console.log("[*] ptrace(PTRACE_TRACEME) bypassed");
        }
    }
});

// 同时 Hook fork 防止子进程检测
Interceptor.attach(Module.findExportByName("libc.so", "fork"), {
    onLeave: function(retval) {
        var pid = retval.toInt32();
        if (pid === 0) {
            // 在子进程中，可以直接退出
            console.log("[*] fork() in child process, may be anti-debug");
        }
    }
});
```

### 1.3 时间检测 (Timing Attack)

调试时单步执行会导致代码运行时间显著增加。App 可以测量关键代码段的执行时间来判断是否被调试。

**实现原理**:

```c
// Native (C/C++) 实现 - 时间检测
#include <time.h>
#include <stdlib.h>

#define THRESHOLD_NS 100000000  // 100ms 阈值

void timing_check() {
    struct timespec start, end;

    clock_gettime(CLOCK_MONOTONIC, &start);

    // 执行一些简单操作
    volatile int sum = 0;
    for (int i = 0; i < 1000; i++) {
        sum += i;
    }

    clock_gettime(CLOCK_MONOTONIC, &end);

    long elapsed = (end.tv_sec - start.tv_sec) * 1000000000L +
                   (end.tv_nsec - start.tv_nsec);

    if (elapsed > THRESHOLD_NS) {
        // 执行时间异常，可能被调试
        exit(0);
    }
}
```

**Java 层实现**:

```java
// Java 实现 - 时间检测
public class TimingCheck {
    private static final long THRESHOLD_MS = 100;

    public static boolean isBeingDebugged() {
        long startTime = System.nanoTime();

        // 执行一些简单计算
        int sum = 0;
        for (int i = 0; i < 10000; i++) {
            sum += i;
        }

        long endTime = System.nanoTime();
        long elapsed = (endTime - startTime) / 1000000;  // 转换为毫秒

        return elapsed > THRESHOLD_MS;
    }
}
```

**绕过策略 - Frida Hook**:

```javascript
// Frida 脚本 - 绕过时间检测
var clock_gettime = Module.findExportByName("libc.so", "clock_gettime");
var baseTime = null;
var fakeElapsed = 1000000;  // 1ms

Interceptor.attach(clock_gettime, {
    onEnter: function(args) {
        this.timespec = args[1];
    },
    onLeave: function(retval) {
        if (baseTime === null) {
            baseTime = {
                tv_sec: this.timespec.readU32(),
                tv_nsec: this.timespec.add(4).readU32()
            };
        } else {
            // 返回假的时间差
            this.timespec.writeU32(baseTime.tv_sec);
            this.timespec.add(4).writeU32(baseTime.tv_nsec + fakeElapsed);
            fakeElapsed += 1000000;  // 每次增加 1ms
        }
    }
});

// Hook Java 层时间函数
Java.perform(function() {
    var System = Java.use("java.lang.System");

    var startNanoTime = null;

    System.nanoTime.implementation = function() {
        if (startNanoTime === null) {
            startNanoTime = this.nanoTime();
        }
        // 返回递增的假时间
        startNanoTime += 1000000;  // 1ms
        return startNanoTime;
    };
});
```

### 1.4 断点检测

检测代码段是否被设置了软件断点（通常是 0xCC 或 ARM 的断点指令）。

**实现原理**:

```c
// Native (C/C++) 实现 - 断点检测
#include <stdint.h>
#include <string.h>

// x86/x64 断点指令
#define BREAKPOINT_X86 0xCC

// ARM 断点指令
#define BREAKPOINT_ARM 0xE7F001F0
#define BREAKPOINT_THUMB 0xDE01

int check_breakpoints(void* func_addr, size_t func_size) {
    uint8_t* code = (uint8_t*)func_addr;

    for (size_t i = 0; i < func_size; i++) {
        // 检测 x86 软件断点
        if (code[i] == BREAKPOINT_X86) {
            return 1;  // 发现断点
        }

#ifdef __arm__
        // 检测 ARM/Thumb 断点
        if (i + 1 < func_size) {
            uint16_t thumb_inst = *(uint16_t*)(code + i);
            if (thumb_inst == BREAKPOINT_THUMB) {
                return 1;
            }
        }
#endif
    }

    return 0;
}

// 计算函数校验和，检测是否被修改
uint32_t calculate_checksum(void* start, size_t size) {
    uint32_t checksum = 0;
    uint8_t* data = (uint8_t*)start;

    for (size_t i = 0; i < size; i++) {
        checksum += data[i];
        checksum = (checksum << 1) | (checksum >> 31);  // 循环左移
    }

    return checksum;
}
```

**绕过策略**:

```javascript
// Frida 脚本 - 使用 Memory.protect 修改权限
// 在检测之前临时恢复原始代码

var targetFunction = Module.findExportByName("libtarget.so", "sensitive_function");

// 保存原始字节
var originalBytes = Memory.readByteArray(targetFunction, 16);

// 当检测函数被调用时，临时恢复
Interceptor.attach(Module.findExportByName("libtarget.so", "check_breakpoints"), {
    onEnter: function(args) {
        // 恢复原始代码
        Memory.writeByteArray(targetFunction, originalBytes);
    },
    onLeave: function(retval) {
        // 重新设置 Hook
        // ... 重新安装 Interceptor
    }
});
```

---

## 2. 反 Hook (Anti-Hooking)

**目标**: 检测和阻止 Frida、Xposed 等 Hook 框架的注入和功能。

### 2.1 Frida 端口检测

Frida Server 默认监听 27042 端口，App 可以扫描本地端口来检测 Frida。

**实现原理**:

```c
// Native (C/C++) 实现 - Frida 端口检测
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <errno.h>

// Frida 默认端口
#define FRIDA_DEFAULT_PORT 27042

int check_frida_port() {
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) {
        return 0;
    }

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(FRIDA_DEFAULT_PORT);
    addr.sin_addr.s_addr = inet_addr("127.0.0.1");

    // 设置非阻塞连接超时
    struct timeval timeout;
    timeout.tv_sec = 1;
    timeout.tv_usec = 0;
    setsockopt(sock, SOL_SOCKET, SO_SNDTIMEO, &timeout, sizeof(timeout));

    int result = connect(sock, (struct sockaddr*)&addr, sizeof(addr));
    close(sock);

    if (result == 0) {
        return 1;  // Frida 端口开放
    }

    return 0;
}

// 扫描多个可疑端口
int check_suspicious_ports() {
    int suspicious_ports[] = {27042, 27043, 27044, 27045, 4444};
    int num_ports = sizeof(suspicious_ports) / sizeof(suspicious_ports[0]);

    for (int i = 0; i < num_ports; i++) {
        int sock = socket(AF_INET, SOCK_STREAM, 0);
        if (sock < 0) continue;

        struct sockaddr_in addr;
        memset(&addr, 0, sizeof(addr));
        addr.sin_family = AF_INET;
        addr.sin_port = htons(suspicious_ports[i]);
        addr.sin_addr.s_addr = inet_addr("127.0.0.1");

        struct timeval timeout = {0, 100000};  // 100ms
        setsockopt(sock, SOL_SOCKET, SO_SNDTIMEO, &timeout, sizeof(timeout));

        if (connect(sock, (struct sockaddr*)&addr, sizeof(addr)) == 0) {
            close(sock);
            return 1;  // 发现可疑端口
        }
        close(sock);
    }

    return 0;
}
```

**Java 层实现**:

```java
// Java 实现 - Frida 端口检测
import java.net.Socket;
import java.net.InetSocketAddress;

public class FridaPortDetector {
    private static final int[] SUSPICIOUS_PORTS = {27042, 27043, 27044, 27045};

    public static boolean detectFridaPort() {
        for (int port : SUSPICIOUS_PORTS) {
            try {
                Socket socket = new Socket();
                socket.connect(new InetSocketAddress("127.0.0.1", port), 100);
                socket.close();
                return true;  // 端口开放，可能是 Frida
            } catch (Exception e) {
                // 连接失败，继续检测下一个端口
            }
        }
        return false;
    }
}
```

**绕过策略 - Frida Hook**:

```javascript
// Frida 脚本 - 绕过端口检测
// 方法1: Hook connect 函数
Interceptor.attach(Module.findExportByName("libc.so", "connect"), {
    onEnter: function(args) {
        var sockaddr = args[1];
        var family = sockaddr.readU16();

        if (family === 2) {  // AF_INET
            var port = (sockaddr.add(2).readU8() << 8) | sockaddr.add(3).readU8();

            // 检测 Frida 端口
            if (port === 27042 || port === 27043 || port === 27044) {
                console.log("[*] Blocking connect to Frida port: " + port);
                // 修改端口为不存在的端口
                sockaddr.add(2).writeU8(0xFF);
                sockaddr.add(3).writeU8(0xFF);
            }
        }
    }
});

// 方法2: 使用自定义端口启动 Frida
// frida-server -l 0.0.0.0:31337
```

### 2.2 内存映射检测

Frida 注入后会在进程内存中加载 `frida-agent.so` 等库，可以通过扫描 `/proc/self/maps` 检测。

**实现原理**:

```c
// Native (C/C++) 实现 - 内存映射检测
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

typedef struct {
    const char* pattern;
    int is_regex;
} DetectionPattern;

static DetectionPattern frida_patterns[] = {
    {"frida", 0},
    {"gadget", 0},
    {"gum-js-loop", 0},
    {"gmain", 0},
    {"linjector", 0},
    {"/data/local/tmp", 0},
    {"re.frida.server", 0},
    {"pool-frida", 0},
};

int check_frida_in_maps() {
    FILE *fp = fopen("/proc/self/maps", "r");
    if (fp == NULL) {
        return 0;
    }

    char line[512];
    int num_patterns = sizeof(frida_patterns) / sizeof(frida_patterns[0]);

    while (fgets(line, sizeof(line), fp)) {
        // 转换为小写进行匹配
        char lower_line[512];
        for (int i = 0; line[i]; i++) {
            lower_line[i] = tolower(line[i]);
        }
        lower_line[strlen(line)] = '\0';

        for (int i = 0; i < num_patterns; i++) {
            if (strstr(lower_line, frida_patterns[i].pattern)) {
                fclose(fp);
                return 1;  // 检测到 Frida
            }
        }
    }

    fclose(fp);
    return 0;
}

// 检测内存中的 Frida 特征字符串
int check_frida_strings_in_memory() {
    FILE *fp = fopen("/proc/self/maps", "r");
    if (fp == NULL) return 0;

    char line[512];
    while (fgets(line, sizeof(line), fp)) {
        // 解析内存区域
        unsigned long start, end;
        char perms[5];

        if (sscanf(line, "%lx-%lx %4s", &start, &end, perms) != 3) {
            continue;
        }

        // 只检查可读区域
        if (perms[0] != 'r') continue;

        // 搜索 Frida 特征
        char* region = (char*)start;
        size_t region_size = end - start;

        // 注意: 这种方法可能会崩溃，需要小心处理
        // 实际实现需要使用 process_vm_readv 或其他安全方式
    }

    fclose(fp);
    return 0;
}
```

**绕过策略 - Frida Hook**:

```javascript
// Frida 脚本 - 绕过 maps 检测
var keywords = ["frida", "gadget", "gum-js-loop", "gmain", "linjector"];

Interceptor.attach(Module.findExportByName("libc.so", "fopen"), {
    onEnter: function(args) {
        this.path = args[0].readCString();
    },
    onLeave: function(retval) {
        if (this.path && this.path.indexOf("maps") !== -1) {
            this.isMaps = true;
            this.fd = retval;
        }
    }
});

Interceptor.attach(Module.findExportByName("libc.so", "fgets"), {
    onLeave: function(retval) {
        if (!retval.isNull()) {
            var line = retval.readCString();
            if (line) {
                var shouldFilter = false;
                for (var i = 0; i < keywords.length; i++) {
                    if (line.toLowerCase().indexOf(keywords[i]) !== -1) {
                        shouldFilter = true;
                        break;
                    }
                }

                if (shouldFilter) {
                    // 用空行替换
                    retval.writeUtf8String("\n");
                    console.log("[*] Filtered maps line containing Frida");
                }
            }
        }
    }
});
```

### 2.3 Inline Hook 检测

检测关键函数的入口是否被修改（如插入跳转指令）。

**实现原理**:

```c
// Native (C/C++) 实现 - Inline Hook 检测
#include <dlfcn.h>
#include <string.h>
#include <stdint.h>

// ARM64 跳转指令特征
#define ARM64_BR_OPCODE    0xD61F0000
#define ARM64_BLR_OPCODE   0xD63F0000
#define ARM64_B_OPCODE     0x14000000
#define ARM64_B_MASK       0xFC000000

// x86_64 跳转指令特征
#define X86_JMP_REL32      0xE9
#define X86_JMP_ABS        0xFF

int check_function_hook(void* func_ptr) {
    uint8_t* code = (uint8_t*)func_ptr;

#if defined(__aarch64__)
    // ARM64 检测
    uint32_t instruction = *(uint32_t*)code;

    // 检测 BR/BLR 指令
    if ((instruction & 0xFFFFFC1F) == ARM64_BR_OPCODE ||
        (instruction & 0xFFFFFC1F) == ARM64_BLR_OPCODE) {
        return 1;  // 可能被 Hook
    }

    // 检测 B 指令
    if ((instruction & ARM64_B_MASK) == ARM64_B_OPCODE) {
        return 1;
    }

    // 检测 LDR + BR 组合 (常见 Hook 方式)
    // LDR X16, #offset; BR X16
    if ((instruction & 0xFF000000) == 0x58000000) {
        uint32_t next_inst = *(uint32_t*)(code + 4);
        if ((next_inst & 0xFFFFFFFF) == 0xD61F0200) {
            return 1;
        }
    }

#elif defined(__x86_64__) || defined(__i386__)
    // x86/x64 检测
    if (code[0] == X86_JMP_REL32) {  // E9 xx xx xx xx
        return 1;
    }

    if (code[0] == X86_JMP_ABS && code[1] == 0x25) {  // FF 25 xx xx xx xx
        return 1;
    }

    // 检测 push + ret (另一种 Hook 方式)
    if (code[0] == 0x68) {  // push imm32
        // 检查后面是否有 ret
        for (int i = 5; i < 10; i++) {
            if (code[i] == 0xC3) {  // ret
                return 1;
            }
        }
    }
#endif

    return 0;
}

// 检测常见被 Hook 的函数
void check_common_hooks() {
    const char* targets[] = {
        "open", "read", "write", "connect", "send", "recv",
        "ptrace", "kill", "exit", "fork", "execve"
    };

    void* libc = dlopen("libc.so", RTLD_NOW);
    if (!libc) return;

    for (int i = 0; i < sizeof(targets) / sizeof(targets[0]); i++) {
        void* func = dlsym(libc, targets[i]);
        if (func && check_function_hook(func)) {
            // 检测到 Hook
            exit(0);
        }
    }

    dlclose(libc);
}
```

**绕过策略**:

```javascript
// Frida 脚本 - 使用 Stalker 避免 Inline Hook 检测
// Stalker 使用代码追踪而非修改原始指令

var targetModule = Process.findModuleByName("libtarget.so");

Stalker.follow(Process.getCurrentThreadId(), {
    transform: function(iterator) {
        var instruction = iterator.next();

        do {
            if (instruction.address.compare(targetModule.base) >= 0 &&
                instruction.address.compare(targetModule.base.add(targetModule.size)) < 0) {
                // 在目标模块内，可以插入自定义代码
                iterator.putCallout(function(context) {
                    // 自定义逻辑
                });
            }
            iterator.keep();
        } while ((instruction = iterator.next()) !== null);
    }
});

// 或者使用 replace 替代 attach，更难被检测
var original = Module.findExportByName("libc.so", "open");
var originalFunc = new NativeFunction(original, 'int', ['pointer', 'int']);

Interceptor.replace(original, new NativeCallback(function(path, flags) {
    var pathStr = path.readCString();
    console.log("[*] open: " + pathStr);
    return originalFunc(path, flags);
}, 'int', ['pointer', 'int']));
```

### 2.4 Xposed 检测

检测 Xposed 框架是否安装和激活。

**实现原理**:

```java
// Java 实现 - Xposed 检测
import java.io.File;
import java.lang.reflect.Method;
import java.util.HashSet;
import java.util.Set;

public class XposedDetector {

    // 检测 Xposed 相关文件
    public static boolean checkXposedFiles() {
        String[] paths = {
            "/system/framework/XposedBridge.jar",
            "/system/lib/libxposed_art.so",
            "/system/lib64/libxposed_art.so",
            "/system/xposed.prop",
            "/data/data/de.robv.android.xposed.installer",
            "/data/data/org.lsposed.manager",
            "/data/adb/lspd"
        };

        for (String path : paths) {
            if (new File(path).exists()) {
                return true;
            }
        }
        return false;
    }

    // 检测 Xposed 类加载
    public static boolean checkXposedClass() {
        try {
            Class.forName("de.robv.android.xposed.XposedBridge");
            return true;
        } catch (ClassNotFoundException e) {
            // Xposed 未加载
        }

        try {
            Class.forName("de.robv.android.xposed.XposedHelpers");
            return true;
        } catch (ClassNotFoundException e) {
            // Xposed 未加载
        }

        return false;
    }

    // 通过堆栈检测 Xposed Hook
    public static boolean checkXposedInStack() {
        StackTraceElement[] stackTrace = Thread.currentThread().getStackTrace();

        for (StackTraceElement element : stackTrace) {
            String className = element.getClassName();
            if (className.contains("xposed") ||
                className.contains("lsposed") ||
                className.contains("EdXposed")) {
                return true;
            }
        }
        return false;
    }

    // 检测方法是否被 Hook (通过 Modifier)
    public static boolean isMethodHooked(Method method) {
        // Xposed Hook 后方法会变成 native
        if (method.getModifiers() != method.getModifiers()) {
            return true;
        }

        // 检查方法是否可访问性被修改
        try {
            // 某些 Hook 框架会修改这个值
        } catch (Exception e) {
            return true;
        }

        return false;
    }

    // 检测全局变量
    public static boolean checkXposedGlobals() {
        try {
            Class<?> xposedBridge = Class.forName("de.robv.android.xposed.XposedBridge");
            java.lang.reflect.Field disableHooks = xposedBridge.getDeclaredField("disableHooks");
            disableHooks.setAccessible(true);
            return true;
        } catch (Exception e) {
            return false;
        }
    }
}
```

**Native 层检测**:

```c
// Native (C/C++) 实现 - Xposed 检测
#include <dlfcn.h>
#include <link.h>

int check_xposed_in_loaded_libs() {
    // 遍历已加载的共享库
    FILE *fp = fopen("/proc/self/maps", "r");
    if (fp == NULL) return 0;

    char line[512];
    while (fgets(line, sizeof(line), fp)) {
        if (strstr(line, "XposedBridge") ||
            strstr(line, "libxposed") ||
            strstr(line, "lspd") ||
            strstr(line, "riru") ||
            strstr(line, "zygisk")) {
            fclose(fp);
            return 1;
        }
    }

    fclose(fp);
    return 0;
}

// 检测 ART 方法结构是否被修改
int check_art_method_hook(void* art_method) {
    // ART 方法被 Xposed Hook 后，entry_point 会被修改
    // 这需要了解 ART 内部结构，不同 Android 版本有差异

    // 简化示例: 检查 entry_point 是否指向已知区域
    // 实际实现需要根据具体 Android 版本调整

    return 0;
}
```

**绕过策略 - Frida Hook**:

```javascript
// Frida 脚本 - 绕过 Xposed 检测
Java.perform(function() {
    // Hook File.exists
    var File = Java.use("java.io.File");
    var xposedPaths = [
        "/system/framework/XposedBridge.jar",
        "/system/lib/libxposed_art.so",
        "/data/data/de.robv.android.xposed.installer",
        "/data/data/org.lsposed.manager"
    ];

    File.exists.implementation = function() {
        var path = this.getAbsolutePath();
        for (var i = 0; i < xposedPaths.length; i++) {
            if (path.indexOf(xposedPaths[i]) !== -1) {
                console.log("[*] Hiding Xposed file: " + path);
                return false;
            }
        }
        return this.exists();
    };

    // Hook Class.forName
    var JavaClass = Java.use("java.lang.Class");
    JavaClass.forName.overload("java.lang.String").implementation = function(name) {
        if (name.indexOf("xposed") !== -1 || name.indexOf("lsposed") !== -1) {
            console.log("[*] Blocking class load: " + name);
            throw Java.use("java.lang.ClassNotFoundException").$new(name);
        }
        return this.forName(name);
    };

    // Hook getStackTrace
    var Thread = Java.use("java.lang.Thread");
    Thread.getStackTrace.implementation = function() {
        var stack = this.getStackTrace();
        var filteredStack = [];

        for (var i = 0; i < stack.length; i++) {
            var className = stack[i].getClassName();
            if (className.indexOf("xposed") === -1 &&
                className.indexOf("lsposed") === -1) {
                filteredStack.push(stack[i]);
            }
        }

        return Java.array("java.lang.StackTraceElement", filteredStack);
    };
});
```

### 2.5 Magisk 检测

检测 Magisk Root 框架。

**实现原理**:

```java
// Java 实现 - Magisk 检测
import java.io.File;
import java.io.BufferedReader;
import java.io.InputStreamReader;

public class MagiskDetector {

    // 检测 Magisk 相关文件
    public static boolean checkMagiskFiles() {
        String[] paths = {
            "/sbin/.magisk",
            "/sbin/magisk",
            "/data/adb/magisk",
            "/data/adb/magisk.img",
            "/data/adb/magisk.db",
            "/data/data/com.topjohnwu.magisk",
            "/data/user_de/0/com.topjohnwu.magisk"
        };

        for (String path : paths) {
            if (new File(path).exists()) {
                return true;
            }
        }
        return false;
    }

    // 检测 MagiskHide/DenyList
    public static boolean checkMagiskHide() {
        try {
            // 执行 magisk 命令
            Process process = Runtime.getRuntime().exec("magisk --hide status");
            BufferedReader reader = new BufferedReader(
                new InputStreamReader(process.getInputStream())
            );
            String line = reader.readLine();
            process.waitFor();
            return line != null;
        } catch (Exception e) {
            return false;
        }
    }

    // 通过挂载点检测
    public static boolean checkMagiskMount() {
        try {
            BufferedReader reader = new BufferedReader(
                new java.io.FileReader("/proc/self/mounts")
            );
            String line;
            while ((line = reader.readLine()) != null) {
                if (line.contains("magisk") || line.contains("/sbin/.")) {
                    reader.close();
                    return true;
                }
            }
            reader.close();
        } catch (Exception e) {
            // 忽略
        }
        return false;
    }

    // 检测 Zygisk
    public static boolean checkZygisk() {
        // Zygisk 会注入到 zygote 进程
        String[] zygiskIndicators = {
            "/data/adb/modules/zygisk",
            "/dev/zygisk"
        };

        for (String path : zygiskIndicators) {
            if (new File(path).exists()) {
                return true;
            }
        }
        return false;
    }
}
```

**绕过策略**:

```javascript
// Frida 脚本 - 绕过 Magisk 检测
Java.perform(function() {
    // 隐藏 Magisk 文件
    var magiskPaths = [
        "/sbin/.magisk", "/sbin/magisk", "/data/adb/magisk",
        "/data/data/com.topjohnwu.magisk"
    ];

    var File = Java.use("java.io.File");

    File.exists.implementation = function() {
        var path = this.getAbsolutePath();
        for (var i = 0; i < magiskPaths.length; i++) {
            if (path.indexOf(magiskPaths[i]) !== -1 ||
                path.indexOf("magisk") !== -1) {
                return false;
            }
        }
        return this.exists();
    };

    // Hook Runtime.exec 阻止 magisk 命令执行
    var Runtime = Java.use("java.lang.Runtime");

    Runtime.exec.overload("java.lang.String").implementation = function(cmd) {
        if (cmd.indexOf("magisk") !== -1 || cmd.indexOf("su") !== -1) {
            console.log("[*] Blocking command: " + cmd);
            throw Java.use("java.io.IOException").$new("Command not found");
        }
        return this.exec(cmd);
    };
});

// Native 层 Hook
Interceptor.attach(Module.findExportByName("libc.so", "fopen"), {
    onEnter: function(args) {
        var path = args[0].readCString();
        if (path && (path.indexOf("magisk") !== -1 ||
                     path.indexOf("/sbin/.") !== -1)) {
            console.log("[*] Blocking fopen: " + path);
            args[0].writeUtf8String("/nonexistent");
        }
    }
});
```

---

## 3. 反模拟器 (Anti-Emulator)

**目标**: 检测 App 是否运行在模拟器而非真实设备上。

### 3.1 系统属性检测

模拟器通常会留下特有的系统属性。

**实现原理**:

```java
// Java 实现 - 系统属性检测
import android.os.Build;
import android.os.SystemProperties;

public class EmulatorDetector {

    public static boolean checkBuildProperties() {
        // 检查 Build 属性
        String[] suspiciousProps = {
            Build.FINGERPRINT,
            Build.MODEL,
            Build.MANUFACTURER,
            Build.BRAND,
            Build.DEVICE,
            Build.PRODUCT,
            Build.HARDWARE
        };

        String[] emulatorKeywords = {
            "generic", "unknown", "emulator", "sdk", "google_sdk",
            "goldfish", "ranchu", "vbox", "genymotion", "andy",
            "nox", "bluestacks", "ttVM_Hdragon", "droid4x"
        };

        for (String prop : suspiciousProps) {
            if (prop == null) continue;
            String lowerProp = prop.toLowerCase();

            for (String keyword : emulatorKeywords) {
                if (lowerProp.contains(keyword)) {
                    return true;
                }
            }
        }

        return false;
    }

    // 检查特定系统属性
    public static boolean checkSystemProperties() {
        String[] emulatorProps = {
            "init.svc.qemud",
            "init.svc.qemu-props",
            "qemu.hw.mainkeys",
            "qemu.sf.fake_camera",
            "qemu.sf.lcd_density",
            "ro.kernel.android.qemud",
            "ro.kernel.qemu",
            "ro.kernel.qemu.gles",
            "ro.hardware.audio.primary",
            "ro.boot.qemu"
        };

        for (String prop : emulatorProps) {
            String value = getSystemProperty(prop);
            if (value != null && !value.isEmpty()) {
                return true;
            }
        }

        return false;
    }

    private static String getSystemProperty(String name) {
        try {
            Class<?> systemProperties = Class.forName("android.os.SystemProperties");
            java.lang.reflect.Method get = systemProperties.getMethod("get", String.class);
            return (String) get.invoke(null, name);
        } catch (Exception e) {
            return null;
        }
    }
}
```

**Native 层检测**:

```c
// Native (C/C++) 实现 - 系统属性检测
#include <sys/system_properties.h>
#include <string.h>

typedef struct {
    const char* name;
    const char* value;  // 如果为 NULL，表示检测属性是否存在
} PropCheck;

static PropCheck emulator_props[] = {
    {"ro.kernel.qemu", NULL},
    {"ro.hardware", "goldfish"},
    {"ro.hardware", "ranchu"},
    {"ro.product.model", "sdk"},
    {"ro.product.device", "generic"},
    {"ro.build.flavor", "sdk"},
    {"init.svc.qemud", NULL},
    {"qemu.hw.mainkeys", NULL},
};

int check_emulator_properties() {
    char value[PROP_VALUE_MAX];
    int num_checks = sizeof(emulator_props) / sizeof(emulator_props[0]);

    for (int i = 0; i < num_checks; i++) {
        if (__system_property_get(emulator_props[i].name, value) > 0) {
            if (emulator_props[i].value == NULL) {
                // 属性存在即为模拟器
                return 1;
            }
            if (strstr(value, emulator_props[i].value)) {
                return 1;
            }
        }
    }

    return 0;
}
```

### 3.2 文件系统检测

检测模拟器特有的文件。

**实现原理**:

```c
// Native (C/C++) 实现 - 文件系统检测
#include <stdio.h>
#include <unistd.h>
#include <sys/stat.h>

static const char* emulator_files[] = {
    // QEMU 相关
    "/system/lib/libc_malloc_debug_qemu.so",
    "/sys/qemu_trace",
    "/system/bin/qemu-props",
    "/dev/socket/qemud",
    "/dev/qemu_pipe",

    // Genymotion 相关
    "/dev/socket/genyd",
    "/dev/socket/baseband_genyd",

    // Nox 相关
    "/fstab.nox",
    "/system/bin/nox-prop",
    "/system/lib/libnoxd.so",

    // BlueStacks 相关
    "/system/bin/bstfolder",
    "/system/lib/libbluestacks.so",

    // 通用 x86 模拟器
    "/system/lib/libhoudini.so",  // ARM 转译库

    // VirtualBox 相关
    "/dev/vboxguest",
    "/dev/vboxuser",
};

int check_emulator_files() {
    int num_files = sizeof(emulator_files) / sizeof(emulator_files[0]);

    for (int i = 0; i < num_files; i++) {
        if (access(emulator_files[i], F_OK) == 0) {
            return 1;  // 文件存在
        }
    }

    return 0;
}

// 检查 /proc/cpuinfo
int check_cpuinfo() {
    FILE* fp = fopen("/proc/cpuinfo", "r");
    if (fp == NULL) return 0;

    char line[256];
    while (fgets(line, sizeof(line), fp)) {
        // 模拟器通常使用 Intel 或 AMD 处理器
        if (strstr(line, "GenuineIntel") || strstr(line, "AuthenticAMD")) {
            // 但某些真机也使用 x86，需要结合其他检测
        }

        // 检测 Goldfish (QEMU)
        if (strstr(line, "Goldfish") || strstr(line, "goldfish")) {
            fclose(fp);
            return 1;
        }

        // 检测 Ranchu (新版 QEMU)
        if (strstr(line, "ranchu")) {
            fclose(fp);
            return 1;
        }
    }

    fclose(fp);
    return 0;
}
```

### 3.3 传感器检测

真实设备有物理传感器，模拟器通常没有或返回固定值。

**实现原理**:

```java
// Java 实现 - 传感器检测
import android.content.Context;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;

public class SensorEmulatorDetector {
    private Context context;
    private SensorManager sensorManager;
    private boolean isEmulator = false;

    public SensorEmulatorDetector(Context context) {
        this.context = context;
        this.sensorManager = (SensorManager) context.getSystemService(Context.SENSOR_SERVICE);
    }

    // 检查传感器数量
    public boolean checkSensorCount() {
        java.util.List<Sensor> sensors = sensorManager.getSensorList(Sensor.TYPE_ALL);

        // 真机通常有多个传感器，模拟器可能很少或没有
        if (sensors.size() < 5) {
            return true;  // 可能是模拟器
        }

        // 检查关键传感器是否存在
        Sensor accelerometer = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER);
        Sensor gyroscope = sensorManager.getDefaultSensor(Sensor.TYPE_GYROSCOPE);
        Sensor magnetometer = sensorManager.getDefaultSensor(Sensor.TYPE_MAGNETIC_FIELD);

        if (accelerometer == null && gyroscope == null && magnetometer == null) {
            return true;
        }

        return false;
    }

    // 监听传感器数据，检测固定值
    public void startSensorMonitoring() {
        Sensor accelerometer = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER);
        if (accelerometer == null) {
            isEmulator = true;
            return;
        }

        SensorEventListener listener = new SensorEventListener() {
            private float[] lastValues = null;
            private int unchangedCount = 0;

            @Override
            public void onSensorChanged(SensorEvent event) {
                if (lastValues == null) {
                    lastValues = event.values.clone();
                    return;
                }

                // 检查值是否完全相同（模拟器常见）
                if (lastValues[0] == event.values[0] &&
                    lastValues[1] == event.values[1] &&
                    lastValues[2] == event.values[2]) {
                    unchangedCount++;

                    if (unchangedCount > 10) {
                        isEmulator = true;
                    }
                } else {
                    unchangedCount = 0;
                }

                lastValues = event.values.clone();
            }

            @Override
            public void onAccuracyChanged(Sensor sensor, int accuracy) {}
        };

        sensorManager.registerListener(listener, accelerometer,
            SensorManager.SENSOR_DELAY_NORMAL);
    }
}
```

### 3.4 电话功能检测

模拟器通常没有真实的电话功能。

**实现原理**:

```java
// Java 实现 - 电话功能检测
import android.content.Context;
import android.telephony.TelephonyManager;

public class TelephonyEmulatorDetector {

    public static boolean checkTelephony(Context context) {
        TelephonyManager tm = (TelephonyManager)
            context.getSystemService(Context.TELEPHONY_SERVICE);

        if (tm == null) {
            return true;
        }

        // 检查网络运营商
        String networkOperator = tm.getNetworkOperatorName();
        if (networkOperator != null) {
            String lower = networkOperator.toLowerCase();
            if (lower.equals("android") || lower.contains("emulator")) {
                return true;
            }
        }

        // 检查 IMEI (需要权限)
        try {
            String deviceId = tm.getDeviceId();
            if (deviceId != null) {
                // 模拟器常见的 IMEI
                if (deviceId.equals("000000000000000") ||
                    deviceId.equals("012345678912345") ||
                    deviceId.startsWith("00000")) {
                    return true;
                }
            }
        } catch (SecurityException e) {
            // 没有权限
        }

        // 检查电话号码
        try {
            String phoneNumber = tm.getLine1Number();
            if (phoneNumber != null) {
                if (phoneNumber.equals("15555215554") ||  // 默认模拟器号码
                    phoneNumber.startsWith("155552")) {
                    return true;
                }
            }
        } catch (SecurityException e) {
            // 没有权限
        }

        return false;
    }
}
```

**绕过策略 - Frida Hook**:

```javascript
// Frida 脚本 - 绕过模拟器检测
Java.perform(function() {
    // 1. Hook Build 属性
    var Build = Java.use("android.os.Build");

    // 设置为真机属性
    Build.FINGERPRINT.value = "samsung/dreamltexx/dreamlte:9/PPR1.180610.011/G950FXXS5DSL1:user/release-keys";
    Build.MODEL.value = "SM-G950F";
    Build.MANUFACTURER.value = "samsung";
    Build.BRAND.value = "samsung";
    Build.DEVICE.value = "dreamlte";
    Build.PRODUCT.value = "dreamltexx";
    Build.HARDWARE.value = "samsungexynos8895";

    console.log("[*] Build properties spoofed");

    // 2. Hook SystemProperties
    var SystemProperties = Java.use("android.os.SystemProperties");

    SystemProperties.get.overload("java.lang.String").implementation = function(key) {
        var emulatorKeys = ["ro.kernel.qemu", "qemu.hw.mainkeys", "ro.boot.qemu"];

        if (emulatorKeys.indexOf(key) !== -1) {
            console.log("[*] Hiding property: " + key);
            return "";
        }

        return this.get(key);
    };

    // 3. Hook 文件检测
    var File = Java.use("java.io.File");

    File.exists.implementation = function() {
        var path = this.getAbsolutePath();
        var emulatorFiles = [
            "qemu", "genymotion", "nox", "bluestacks",
            "vbox", "goldfish", "ranchu"
        ];

        for (var i = 0; i < emulatorFiles.length; i++) {
            if (path.toLowerCase().indexOf(emulatorFiles[i]) !== -1) {
                console.log("[*] Hiding emulator file: " + path);
                return false;
            }
        }

        return this.exists();
    };

    // 4. Hook TelephonyManager
    var TelephonyManager = Java.use("android.telephony.TelephonyManager");

    TelephonyManager.getDeviceId.overload().implementation = function() {
        var fakeImei = "358240051111110";
        console.log("[*] Returning fake IMEI: " + fakeImei);
        return fakeImei;
    };

    TelephonyManager.getNetworkOperatorName.implementation = function() {
        return "China Mobile";
    };

    // 5. Hook SensorManager
    var SensorManager = Java.use("android.hardware.SensorManager");

    SensorManager.getSensorList.implementation = function(type) {
        var result = this.getSensorList(type);
        console.log("[*] getSensorList called, returning " + result.size() + " sensors");
        return result;
    };
});
```

---

## 4. Root 检测 (Root Detection)

**目标**: 检测设备是否已被 Root。

### 4.1 常见 Root 文件检测

**实现原理**:

```java
// Java 实现 - Root 文件检测
import java.io.File;

public class RootDetector {

    // su 二进制文件路径
    private static final String[] SU_PATHS = {
        "/system/bin/su",
        "/system/xbin/su",
        "/sbin/su",
        "/system/su",
        "/system/bin/.ext/.su",
        "/system/usr/we-need-root/su-backup",
        "/system/xbin/mu",
        "/data/local/xbin/su",
        "/data/local/bin/su",
        "/data/local/su",
        "/su/bin/su",
        "/magisk/.core/bin/su"
    };

    // Root 管理应用
    private static final String[] ROOT_PACKAGES = {
        "com.topjohnwu.magisk",
        "com.koushikdutta.superuser",
        "eu.chainfire.supersu",
        "com.noshufou.android.su",
        "com.thirdparty.superuser",
        "com.yellowes.su"
    };

    // 危险应用
    private static final String[] DANGEROUS_PACKAGES = {
        "com.chelpus.lackypatch",
        "com.ramdroid.appquarantine",
        "com.devadvance.rootcloak",
        "com.devadvance.rootcloakplus",
        "de.robv.android.xposed.installer",
        "org.lsposed.manager"
    };

    public static boolean checkSuBinary() {
        for (String path : SU_PATHS) {
            if (new File(path).exists()) {
                return true;
            }
        }
        return false;
    }

    public static boolean checkSuCommand() {
        try {
            Process process = Runtime.getRuntime().exec(new String[]{"which", "su"});
            java.io.BufferedReader reader = new java.io.BufferedReader(
                new java.io.InputStreamReader(process.getInputStream())
            );
            String line = reader.readLine();
            return line != null && !line.isEmpty();
        } catch (Exception e) {
            return false;
        }
    }

    public static boolean checkRootPackages(android.content.pm.PackageManager pm) {
        for (String pkg : ROOT_PACKAGES) {
            try {
                pm.getPackageInfo(pkg, 0);
                return true;
            } catch (android.content.pm.PackageManager.NameNotFoundException e) {
                // 未安装
            }
        }
        return false;
    }

    public static boolean checkDangerousProps() {
        String[] dangerousProps = {
            "ro.debuggable",
            "ro.secure"
        };

        try {
            for (String prop : dangerousProps) {
                String value = getSystemProperty(prop);
                if ("ro.debuggable".equals(prop) && "1".equals(value)) {
                    return true;
                }
                if ("ro.secure".equals(prop) && "0".equals(value)) {
                    return true;
                }
            }
        } catch (Exception e) {
            // 忽略
        }

        return false;
    }

    private static String getSystemProperty(String name) throws Exception {
        Class<?> systemProperties = Class.forName("android.os.SystemProperties");
        java.lang.reflect.Method get = systemProperties.getMethod("get", String.class);
        return (String) get.invoke(null, name);
    }
}
```

### 4.2 执行权限检测

检测是否可以获取 root 权限执行命令。

**实现原理**:

```java
// Java 实现 - Root 执行检测
public class RootExecutionDetector {

    public static boolean canExecuteAsRoot() {
        Process process = null;
        java.io.DataOutputStream os = null;

        try {
            process = Runtime.getRuntime().exec("su");
            os = new java.io.DataOutputStream(process.getOutputStream());

            os.writeBytes("id\n");
            os.writeBytes("exit\n");
            os.flush();

            int exitValue = process.waitFor();

            // 如果成功执行，说明有 root 权限
            return exitValue == 0;

        } catch (Exception e) {
            return false;
        } finally {
            try {
                if (os != null) os.close();
                if (process != null) process.destroy();
            } catch (Exception e) {
                // 忽略
            }
        }
    }

    public static boolean checkRWSystem() {
        // 检查 /system 是否可写
        try {
            Process process = Runtime.getRuntime().exec("mount");
            java.io.BufferedReader reader = new java.io.BufferedReader(
                new java.io.InputStreamReader(process.getInputStream())
            );

            String line;
            while ((line = reader.readLine()) != null) {
                if (line.contains("/system") && line.contains("rw")) {
                    return true;  // /system 可写，可能被 Root
                }
            }
        } catch (Exception e) {
            // 忽略
        }

        return false;
    }
}
```

### 4.3 Native 层 Root 检测

**实现原理**:

```c
// Native (C/C++) 实现 - Root 检测
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/stat.h>
#include <dirent.h>

static const char* su_paths[] = {
    "/system/bin/su",
    "/system/xbin/su",
    "/sbin/su",
    "/su/bin/su",
    "/magisk/.core/bin/su",
    "/data/local/bin/su",
    "/data/local/xbin/su"
};

int check_su_binary_native() {
    int num_paths = sizeof(su_paths) / sizeof(su_paths[0]);

    for (int i = 0; i < num_paths; i++) {
        struct stat st;
        if (stat(su_paths[i], &st) == 0) {
            return 1;  // su 存在
        }
    }

    return 0;
}

// 检测 PATH 环境变量中的 su
int check_su_in_path() {
    char* path = getenv("PATH");
    if (path == NULL) return 0;

    char* path_copy = strdup(path);
    char* token = strtok(path_copy, ":");

    while (token != NULL) {
        char su_path[256];
        snprintf(su_path, sizeof(su_path), "%s/su", token);

        if (access(su_path, F_OK) == 0) {
            free(path_copy);
            return 1;
        }

        token = strtok(NULL, ":");
    }

    free(path_copy);
    return 0;
}

// 检测 SELinux 状态
int check_selinux_enforcing() {
    FILE* fp = fopen("/sys/fs/selinux/enforce", "r");
    if (fp == NULL) {
        return -1;  // SELinux 不存在或无法访问
    }

    int enforcing = 0;
    fscanf(fp, "%d", &enforcing);
    fclose(fp);

    // 0 = Permissive (可能被 Root)
    // 1 = Enforcing (正常)
    return enforcing;
}

// 检测可疑进程
int check_suspicious_processes() {
    DIR* dir = opendir("/proc");
    if (dir == NULL) return 0;

    struct dirent* entry;
    while ((entry = readdir(dir)) != NULL) {
        if (entry->d_type != DT_DIR) continue;

        // 检查是否为数字目录 (进程目录)
        char* endptr;
        long pid = strtol(entry->d_name, &endptr, 10);
        if (*endptr != '\0') continue;

        // 读取进程名
        char cmdline_path[256];
        snprintf(cmdline_path, sizeof(cmdline_path), "/proc/%ld/cmdline", pid);

        FILE* fp = fopen(cmdline_path, "r");
        if (fp == NULL) continue;

        char cmdline[256];
        if (fgets(cmdline, sizeof(cmdline), fp) != NULL) {
            if (strstr(cmdline, "daemonsu") ||
                strstr(cmdline, "magiskd") ||
                strstr(cmdline, "supersu")) {
                fclose(fp);
                closedir(dir);
                return 1;
            }
        }
        fclose(fp);
    }

    closedir(dir);
    return 0;
}
```

**绕过策略 - Frida Hook**:

```javascript
// Frida 脚本 - 综合 Root 检测绕过
Java.perform(function() {
    // 1. 隐藏 su 文件
    var File = Java.use("java.io.File");
    var suPaths = [
        "/system/bin/su", "/system/xbin/su", "/sbin/su",
        "/su/bin/su", "/magisk"
    ];

    File.exists.implementation = function() {
        var path = this.getAbsolutePath();
        for (var i = 0; i < suPaths.length; i++) {
            if (path.indexOf(suPaths[i]) !== -1 ||
                path.indexOf("supersu") !== -1 ||
                path.indexOf("magisk") !== -1) {
                console.log("[*] Hiding root file: " + path);
                return false;
            }
        }
        return this.exists();
    };

    // 2. 阻止执行 su 命令
    var Runtime = Java.use("java.lang.Runtime");

    Runtime.exec.overload("[Ljava.lang.String;").implementation = function(cmdArray) {
        var cmd = cmdArray.join(" ");
        if (cmd.indexOf("su") !== -1 || cmd.indexOf("which") !== -1) {
            console.log("[*] Blocking command: " + cmd);
            throw Java.use("java.io.IOException").$new("Cannot run program");
        }
        return this.exec(cmdArray);
    };

    Runtime.exec.overload("java.lang.String").implementation = function(cmd) {
        if (cmd.indexOf("su") !== -1 || cmd.indexOf("which") !== -1) {
            console.log("[*] Blocking command: " + cmd);
            throw Java.use("java.io.IOException").$new("Cannot run program");
        }
        return this.exec(cmd);
    };

    // 3. 隐藏 Root 包
    var PackageManager = Java.use("android.app.ApplicationPackageManager");
    var rootPackages = [
        "com.topjohnwu.magisk", "eu.chainfire.supersu",
        "com.koushikdutta.superuser", "com.noshufou.android.su"
    ];

    PackageManager.getPackageInfo.overload("java.lang.String", "int").implementation = function(pkg, flags) {
        for (var i = 0; i < rootPackages.length; i++) {
            if (pkg === rootPackages[i]) {
                console.log("[*] Hiding root package: " + pkg);
                throw Java.use("android.content.pm.PackageManager$NameNotFoundException").$new(pkg);
            }
        }
        return this.getPackageInfo(pkg, flags);
    };
});

// Native 层绕过
Interceptor.attach(Module.findExportByName("libc.so", "access"), {
    onEnter: function(args) {
        var path = args[0].readCString();
        if (path && (path.indexOf("su") !== -1 || path.indexOf("magisk") !== -1)) {
            console.log("[*] Blocking access check: " + path);
            this.block = true;
        }
    },
    onLeave: function(retval) {
        if (this.block) {
            retval.replace(-1);  // 返回不存在
        }
    }
});

Interceptor.attach(Module.findExportByName("libc.so", "stat"), {
    onEnter: function(args) {
        var path = args[0].readCString();
        if (path && (path.indexOf("su") !== -1 || path.indexOf("magisk") !== -1)) {
            console.log("[*] Blocking stat: " + path);
            this.block = true;
        }
    },
    onLeave: function(retval) {
        if (this.block) {
            retval.replace(-1);
        }
    }
});
```

---

## 5. 完整性校验 (Integrity Checks)

**目标**: 检测 APK 或运行时代码是否被篡改。

### 5.1 签名校验

**实现原理**:

```java
// Java 实现 - APK 签名校验
import android.content.Context;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.content.pm.Signature;
import java.security.MessageDigest;

public class SignatureVerifier {

    // 原始签名的 SHA-256 哈希值 (需要预先计算)
    private static final String EXPECTED_SIGNATURE_HASH =
        "a1b2c3d4e5f6...";  // 替换为实际值

    public static boolean verifySignature(Context context) {
        try {
            PackageInfo packageInfo = context.getPackageManager()
                .getPackageInfo(context.getPackageName(), PackageManager.GET_SIGNATURES);

            Signature[] signatures = packageInfo.signatures;
            if (signatures == null || signatures.length == 0) {
                return false;
            }

            // 计算签名哈希
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            byte[] signatureBytes = signatures[0].toByteArray();
            byte[] hash = md.digest(signatureBytes);

            // 转换为十六进制字符串
            StringBuilder hexString = new StringBuilder();
            for (byte b : hash) {
                String hex = Integer.toHexString(0xff & b);
                if (hex.length() == 1) hexString.append('0');
                hexString.append(hex);
            }

            return EXPECTED_SIGNATURE_HASH.equals(hexString.toString());

        } catch (Exception e) {
            return false;
        }
    }

    // Android P+ 使用 GET_SIGNING_CERTIFICATES
    public static boolean verifySignatureV2(Context context) {
        try {
            if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.P) {
                PackageInfo packageInfo = context.getPackageManager()
                    .getPackageInfo(context.getPackageName(),
                        PackageManager.GET_SIGNING_CERTIFICATES);

                android.content.pm.SigningInfo signingInfo = packageInfo.signingInfo;
                Signature[] signatures = signingInfo.getApkContentsSigners();

                // 校验签名...
            }
        } catch (Exception e) {
            return false;
        }
        return true;
    }
}
```

### 5.2 DEX 文件校验

**实现原理**:

```java
// Java 实现 - DEX 文件校验
import java.io.File;
import java.io.FileInputStream;
import java.security.MessageDigest;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;

public class DexVerifier {

    // 预期的 classes.dex 哈希值
    private static final String EXPECTED_DEX_HASH = "...";

    public static boolean verifyDex(String apkPath) {
        try {
            ZipFile zipFile = new ZipFile(apkPath);
            ZipEntry dexEntry = zipFile.getEntry("classes.dex");

            if (dexEntry == null) {
                zipFile.close();
                return false;
            }

            // 计算 DEX 文件哈希
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            java.io.InputStream is = zipFile.getInputStream(dexEntry);

            byte[] buffer = new byte[8192];
            int bytesRead;
            while ((bytesRead = is.read(buffer)) != -1) {
                md.update(buffer, 0, bytesRead);
            }

            is.close();
            zipFile.close();

            byte[] hash = md.digest();

            // 转换并比较
            StringBuilder hexString = new StringBuilder();
            for (byte b : hash) {
                String hex = Integer.toHexString(0xff & b);
                if (hex.length() == 1) hexString.append('0');
                hexString.append(hex);
            }

            return EXPECTED_DEX_HASH.equals(hexString.toString());

        } catch (Exception e) {
            return false;
        }
    }
}
```

### 5.3 Native 代码校验

**实现原理**:

```c
// Native (C/C++) 实现 - SO 文件校验
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dlfcn.h>
#include <link.h>

// 预期的关键函数校验和
static uint32_t expected_checksums[] = {
    0x12345678,  // function1
    0x87654321,  // function2
    // ...
};

uint32_t calculate_function_checksum(void* func_start, size_t size) {
    uint32_t checksum = 0;
    uint8_t* data = (uint8_t*)func_start;

    for (size_t i = 0; i < size; i++) {
        checksum ^= data[i];
        checksum = (checksum << 1) | (checksum >> 31);
    }

    return checksum;
}

int verify_code_integrity() {
    // 获取当前 SO 的基地址
    Dl_info info;
    if (dladdr((void*)verify_code_integrity, &info) == 0) {
        return 0;
    }

    void* base = info.dli_fbase;

    // 验证关键函数
    // 这里需要知道函数的偏移和大小
    // 实际实现中这些值应该在编译时确定

    return 1;
}

// 运行时检测内存页是否被修改
int check_memory_pages() {
    FILE* fp = fopen("/proc/self/maps", "r");
    if (fp == NULL) return 0;

    char line[512];
    while (fgets(line, sizeof(line), fp)) {
        unsigned long start, end;
        char perms[5];

        if (sscanf(line, "%lx-%lx %4s", &start, &end, perms) != 3) {
            continue;
        }

        // 检查代码段是否有写权限 (正常应该是 r-x)
        if (perms[0] == 'r' && perms[2] == 'x' && perms[1] == 'w') {
            // 代码段可写，可能被修改
            fclose(fp);
            return 1;
        }
    }

    fclose(fp);
    return 0;
}
```

**绕过策略 - Frida Hook**:

```javascript
// Frida 脚本 - 绕过完整性校验
Java.perform(function() {
    // 1. 绕过签名校验
    var PackageManager = Java.use("android.app.ApplicationPackageManager");

    PackageManager.getPackageInfo.overload("java.lang.String", "int").implementation = function(pkg, flags) {
        var info = this.getPackageInfo(pkg, flags);

        // 如果请求签名信息，返回原始签名
        if ((flags & 0x40) !== 0) {  // GET_SIGNATURES = 0x40
            // 这里可以构造假的签名对象
            // 实际操作需要知道原始签名
            console.log("[*] Signature verification intercepted");
        }

        return info;
    };

    // 2. 绕过 DEX 校验
    var MessageDigest = Java.use("java.security.MessageDigest");

    MessageDigest.digest.overload("[B").implementation = function(input) {
        // 检查调用栈是否来自完整性检测
        var stack = Java.use("java.lang.Thread").currentThread().getStackTrace();
        for (var i = 0; i < stack.length; i++) {
            var className = stack[i].getClassName();
            if (className.indexOf("Verifier") !== -1 ||
                className.indexOf("Integrity") !== -1) {
                console.log("[*] Integrity check detected, returning expected hash");
                // 返回预期的哈希值
                var expectedHash = Java.array('byte', [/* 预期哈希字节 */]);
                return expectedHash;
            }
        }
        return this.digest(input);
    };
});
```

---

## 6. SSL Pinning (证书绑定)

**目标**: 防止中间人攻击，确保通信只与指定服务器建立。

### 6.1 证书固定实现

**实现原理**:

```java
// Java 实现 - SSL Pinning
import java.security.cert.CertificateException;
import java.security.cert.X509Certificate;
import javax.net.ssl.*;
import java.security.MessageDigest;

public class SSLPinning {

    // 预期的证书公钥 SHA-256 哈希
    private static final String[] EXPECTED_PINS = {
        "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=",
        "sha256/BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB="
    };

    public static SSLSocketFactory getPinnedSSLSocketFactory() throws Exception {
        TrustManager[] trustManagers = new TrustManager[]{
            new X509TrustManager() {
                @Override
                public void checkClientTrusted(X509Certificate[] chain, String authType)
                    throws CertificateException {
                    // 不检查客户端证书
                }

                @Override
                public void checkServerTrusted(X509Certificate[] chain, String authType)
                    throws CertificateException {
                    if (chain == null || chain.length == 0) {
                        throw new CertificateException("Empty certificate chain");
                    }

                    // 验证证书链中是否有匹配的 Pin
                    for (X509Certificate cert : chain) {
                        String pin = getPublicKeyPin(cert);
                        for (String expectedPin : EXPECTED_PINS) {
                            if (expectedPin.equals(pin)) {
                                return;  // 验证通过
                            }
                        }
                    }

                    throw new CertificateException("Certificate pinning failed");
                }

                @Override
                public X509Certificate[] getAcceptedIssuers() {
                    return new X509Certificate[0];
                }

                private String getPublicKeyPin(X509Certificate cert) {
                    try {
                        byte[] publicKeyBytes = cert.getPublicKey().getEncoded();
                        MessageDigest md = MessageDigest.getInstance("SHA-256");
                        byte[] hash = md.digest(publicKeyBytes);
                        return "sha256/" + android.util.Base64.encodeToString(hash,
                            android.util.Base64.NO_WRAP);
                    } catch (Exception e) {
                        return "";
                    }
                }
            }
        };

        SSLContext sslContext = SSLContext.getInstance("TLS");
        sslContext.init(null, trustManagers, new java.security.SecureRandom());
        return sslContext.getSocketFactory();
    }
}
```

### 6.2 OkHttp Certificate Pinning

**实现原理**:

```java
// Java 实现 - OkHttp SSL Pinning
import okhttp3.CertificatePinner;
import okhttp3.OkHttpClient;

public class OkHttpPinning {

    public static OkHttpClient createPinnedClient() {
        CertificatePinner certificatePinner = new CertificatePinner.Builder()
            .add("api.example.com",
                "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
            .add("api.example.com",
                "sha256/BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=")
            .add("*.example.com",
                "sha256/CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC=")
            .build();

        return new OkHttpClient.Builder()
            .certificatePinner(certificatePinner)
            .build();
    }
}
```

### 6.3 Native 层 SSL Pinning

**实现原理**:

```c
// Native (C/C++) 实现 - OpenSSL 证书验证
#include <openssl/ssl.h>
#include <openssl/x509.h>
#include <openssl/evp.h>

// 预期的公钥哈希
static const unsigned char expected_pin[] = {
    0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
    0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f, 0x10,
    0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18,
    0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f, 0x20
};

int verify_certificate_pin(X509* cert) {
    EVP_PKEY* pubkey = X509_get_pubkey(cert);
    if (pubkey == NULL) {
        return 0;
    }

    unsigned char* pubkey_der = NULL;
    int pubkey_len = i2d_PUBKEY(pubkey, &pubkey_der);

    if (pubkey_len <= 0) {
        EVP_PKEY_free(pubkey);
        return 0;
    }

    // 计算 SHA-256 哈希
    unsigned char hash[32];
    EVP_MD_CTX* ctx = EVP_MD_CTX_new();
    EVP_DigestInit_ex(ctx, EVP_sha256(), NULL);
    EVP_DigestUpdate(ctx, pubkey_der, pubkey_len);
    EVP_DigestFinal_ex(ctx, hash, NULL);
    EVP_MD_CTX_free(ctx);

    OPENSSL_free(pubkey_der);
    EVP_PKEY_free(pubkey);

    // 比较哈希
    return memcmp(hash, expected_pin, 32) == 0;
}

// 自定义 SSL 验证回调
int ssl_verify_callback(int preverify_ok, X509_STORE_CTX* ctx) {
    if (!preverify_ok) {
        return 0;  // 基本验证失败
    }

    // 获取证书
    X509* cert = X509_STORE_CTX_get_current_cert(ctx);
    if (cert == NULL) {
        return 0;
    }

    // 验证证书固定
    if (!verify_certificate_pin(cert)) {
        return 0;  // Pin 验证失败
    }

    return 1;
}
```

**绕过策略 - Frida Hook**:

```javascript
// Frida 脚本 - 综合 SSL Pinning 绕过
Java.perform(function() {
    console.log("[*] Starting SSL Pinning bypass...");

    // 1. 绕过 TrustManager
    var X509TrustManager = Java.use("javax.net.ssl.X509TrustManager");
    var SSLContext = Java.use("javax.net.ssl.SSLContext");

    var TrustManager = Java.registerClass({
        name: "com.custom.TrustManager",
        implements: [X509TrustManager],
        methods: {
            checkClientTrusted: function(chain, authType) {},
            checkServerTrusted: function(chain, authType) {},
            getAcceptedIssuers: function() {
                return [];
            }
        }
    });

    // Hook SSLContext.init
    SSLContext.init.overload(
        "[Ljavax.net.ssl.KeyManager;",
        "[Ljavax.net.ssl.TrustManager;",
        "java.security.SecureRandom"
    ).implementation = function(km, tm, sr) {
        console.log("[*] SSLContext.init intercepted");
        var trustManager = TrustManager.$new();
        var trustManagers = Java.array("javax.net.ssl.TrustManager", [trustManager]);
        this.init(km, trustManagers, sr);
    };

    // 2. 绕过 OkHttp CertificatePinner
    try {
        var CertificatePinner = Java.use("okhttp3.CertificatePinner");

        CertificatePinner.check.overload("java.lang.String", "java.util.List").implementation = function(hostname, peerCertificates) {
            console.log("[*] OkHttp CertificatePinner.check bypassed for: " + hostname);
            return;
        };

        CertificatePinner.check$okhttp.overload("java.lang.String", "kotlin.jvm.functions.Function0").implementation = function(hostname, peerCertificates) {
            console.log("[*] OkHttp CertificatePinner.check$okhttp bypassed for: " + hostname);
            return;
        };
    } catch (e) {
        console.log("[-] OkHttp not found or different version");
    }

    // 3. 绕过 Trustkit
    try {
        var TrustKit = Java.use("com.datatheorem.android.trustkit.pinning.OkHostnameVerifier");
        TrustKit.verify.overload("java.lang.String", "javax.net.ssl.SSLSession").implementation = function(hostname, session) {
            console.log("[*] TrustKit bypassed for: " + hostname);
            return true;
        };
    } catch (e) {
        console.log("[-] TrustKit not found");
    }

    // 4. 绕过 WebView SSL 错误
    try {
        var WebViewClient = Java.use("android.webkit.WebViewClient");

        WebViewClient.onReceivedSslError.implementation = function(view, handler, error) {
            console.log("[*] WebView SSL error bypassed");
            handler.proceed();
        };
    } catch (e) {
        console.log("[-] WebViewClient hook failed");
    }

    // 5. 绕过 HostnameVerifier
    var HostnameVerifier = Java.use("javax.net.ssl.HostnameVerifier");
    var HttpsURLConnection = Java.use("javax.net.ssl.HttpsURLConnection");

    var AllowAllHostnameVerifier = Java.registerClass({
        name: "com.custom.AllowAllHostnameVerifier",
        implements: [HostnameVerifier],
        methods: {
            verify: function(hostname, session) {
                return true;
            }
        }
    });

    HttpsURLConnection.setDefaultHostnameVerifier(AllowAllHostnameVerifier.$new());

    console.log("[+] SSL Pinning bypass complete");
});

// Native 层 SSL 绕过
Interceptor.attach(Module.findExportByName("libssl.so", "SSL_CTX_set_verify"), {
    onEnter: function(args) {
        console.log("[*] SSL_CTX_set_verify intercepted");
        // 设置为 SSL_VERIFY_NONE (0)
        args[1] = ptr(0);
    }
});
```

---

## 7. 综合绕过框架

将上述所有绕过技术整合为一个综合脚本：

```javascript
// Frida 脚本 - 综合反分析绕过框架
(function() {
    "use strict";

    console.log("===========================================");
    console.log("[*] Anti-Analysis Bypass Framework Started");
    console.log("===========================================");

    // 配置选项
    var config = {
        bypassRoot: true,
        bypassFrida: true,
        bypassEmulator: true,
        bypassDebug: true,
        bypassSSL: true,
        bypassIntegrity: true,
        verbose: true
    };

    function log(msg) {
        if (config.verbose) {
            console.log("[*] " + msg);
        }
    }

    // ========== Root 检测绕过 ==========
    if (config.bypassRoot) {
        Java.perform(function() {
            log("Applying Root detection bypass...");

            var File = Java.use("java.io.File");
            var rootIndicators = ["su", "magisk", "supersu", "busybox", "/sbin"];

            File.exists.implementation = function() {
                var path = this.getAbsolutePath().toLowerCase();
                for (var i = 0; i < rootIndicators.length; i++) {
                    if (path.indexOf(rootIndicators[i]) !== -1) {
                        log("Hiding root file: " + path);
                        return false;
                    }
                }
                return this.exists();
            };
        });
    }

    // ========== Frida 检测绕过 ==========
    if (config.bypassFrida) {
        // 端口绕过
        Interceptor.attach(Module.findExportByName("libc.so", "connect"), {
            onEnter: function(args) {
                var sockaddr = args[1];
                var family = sockaddr.readU16();
                if (family === 2) {
                    var port = (sockaddr.add(2).readU8() << 8) | sockaddr.add(3).readU8();
                    if (port >= 27042 && port <= 27045) {
                        log("Blocking Frida port: " + port);
                        sockaddr.add(2).writeU8(0xFF);
                        sockaddr.add(3).writeU8(0xFF);
                    }
                }
            }
        });

        // Maps 绕过
        var keywords = ["frida", "gadget", "gum-js", "linjector"];

        Interceptor.attach(Module.findExportByName("libc.so", "fgets"), {
            onLeave: function(retval) {
                if (!retval.isNull()) {
                    var line = retval.readCString();
                    if (line) {
                        for (var i = 0; i < keywords.length; i++) {
                            if (line.toLowerCase().indexOf(keywords[i]) !== -1) {
                                retval.writeUtf8String("\n");
                                log("Filtered maps line with: " + keywords[i]);
                                break;
                            }
                        }
                    }
                }
            }
        });
    }

    // ========== 调试检测绕过 ==========
    if (config.bypassDebug) {
        // TracerPid 绕过
        Interceptor.attach(Module.findExportByName("libc.so", "fgets"), {
            onLeave: function(retval) {
                if (!retval.isNull()) {
                    var line = retval.readCString();
                    if (line && line.indexOf("TracerPid:") !== -1) {
                        retval.writeUtf8String("TracerPid:\t0\n");
                        log("TracerPid spoofed to 0");
                    }
                }
            }
        });

        // ptrace 绕过
        var ptrace = Module.findExportByName(null, "ptrace");
        if (ptrace) {
            Interceptor.attach(ptrace, {
                onEnter: function(args) {
                    this.request = args[0].toInt32();
                },
                onLeave: function(retval) {
                    if (this.request === 0) {  // PTRACE_TRACEME
                        retval.replace(0);
                        log("ptrace(PTRACE_TRACEME) bypassed");
                    }
                }
            });
        }
    }

    // ========== 模拟器检测绕过 ==========
    if (config.bypassEmulator) {
        Java.perform(function() {
            log("Applying Emulator detection bypass...");

            var Build = Java.use("android.os.Build");
            Build.FINGERPRINT.value = "samsung/dreamltexx/dreamlte:9/PPR1.180610.011/G950FXXS5DSL1:user/release-keys";
            Build.MODEL.value = "SM-G950F";
            Build.MANUFACTURER.value = "samsung";
            Build.BRAND.value = "samsung";
            Build.DEVICE.value = "dreamlte";
            Build.PRODUCT.value = "dreamltexx";
            Build.HARDWARE.value = "samsungexynos8895";

            log("Build properties spoofed to Samsung S8");
        });
    }

    // ========== SSL Pinning 绕过 ==========
    if (config.bypassSSL) {
        Java.perform(function() {
            log("Applying SSL Pinning bypass...");

            var X509TrustManager = Java.use("javax.net.ssl.X509TrustManager");
            var SSLContext = Java.use("javax.net.ssl.SSLContext");

            var EmptyTrustManager = Java.registerClass({
                name: "com.bypass.EmptyTrustManager",
                implements: [X509TrustManager],
                methods: {
                    checkClientTrusted: function(chain, authType) {},
                    checkServerTrusted: function(chain, authType) {},
                    getAcceptedIssuers: function() { return []; }
                }
            });

            SSLContext.init.overload(
                "[Ljavax.net.ssl.KeyManager;",
                "[Ljavax.net.ssl.TrustManager;",
                "java.security.SecureRandom"
            ).implementation = function(km, tm, sr) {
                log("SSLContext.init intercepted");
                var emptyTm = Java.array("javax.net.ssl.TrustManager",
                    [EmptyTrustManager.$new()]);
                this.init(km, emptyTm, sr);
            };

            // OkHttp 绕过
            try {
                var CertificatePinner = Java.use("okhttp3.CertificatePinner");
                CertificatePinner.check.overload("java.lang.String", "java.util.List")
                    .implementation = function(hostname, certs) {
                    log("OkHttp pinning bypassed for: " + hostname);
                };
            } catch (e) {}
        });
    }

    console.log("===========================================");
    console.log("[+] All bypasses applied successfully!");
    console.log("===========================================");

})();
```

---

## 总结

### 反分析技术对照表

| 检测类型 | 检测方法 | 绕过策略 | 难度 |
|----------|----------|----------|------|
| **反调试** | TracerPid | Hook fgets | ⭐ |
| | ptrace | Hook ptrace | ⭐⭐ |
| | 时间检测 | Hook clock_gettime | ⭐⭐ |
| | 断点检测 | 临时恢复代码 | ⭐⭐⭐ |
| **反 Hook** | Frida 端口 | 自定义端口 | ⭐ |
| | 内存特征 | 过滤 maps | ⭐⭐ |
| | Inline Hook | Stalker | ⭐⭐⭐ |
| | Xposed 检测 | 隐藏特征 | ⭐⭐ |
| **反模拟器** | 系统属性 | 修改 Build | ⭐ |
| | 特有文件 | Hook exists | ⭐ |
| | 传感器 | 模拟数据 | ⭐⭐⭐ |
| **Root 检测** | su 文件 | Hook access/stat | ⭐ |
| | Root 包 | Hook PackageManager | ⭐ |
| | Magisk | MagiskHide | ⭐⭐ |
| **完整性** | 签名校验 | Hook getPackageInfo | ⭐⭐ |
| | DEX 校验 | Hook digest | ⭐⭐ |
| **SSL Pinning** | TrustManager | 自定义 TrustManager | ⭐⭐ |
| | OkHttp | Hook CertificatePinner | ⭐⭐ |

### 最佳实践

1. **分层防御**: 结合 Java 层和 Native 层检测
2. **多点检测**: 在多个位置进行检测，增加绕过难度
3. **动态检测**: 使用后台线程持续检测
4. **混淆代码**: 混淆检测代码本身，增加分析难度
5. **服务端验证**: 关键逻辑放在服务端，客户端仅做辅助检测

---

**相关章节**：
- [R15: Frida 反调试绕过](../01-Recipes/Anti-Detection/frida_anti_debugging.md)
- [R16: Xposed 反调试绕过](../01-Recipes/Anti-Detection/xposed_anti_debugging.md)
- [A07: Magisk 与 LSPosed 原理](../04-Reference/Advanced/magisk_lsposed_internals.md)
