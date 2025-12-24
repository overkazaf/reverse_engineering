---
title: "风控 SDK 架构设计"
date: 2025-12-25
weight: 10
---

# 风控 SDK 架构设计

> **说明**: 本案例是笔者根据实际风控 SDK 逆向分析经验，构建的一个**精简版客户端风控 SDK Demo**。
> 旨在帮助读者理解风控 SDK 的核心架构和设计思路，而非生产级实现。

Risk Control SDK 是一个用于移动应用的设备指纹识别和安全评估系统，基于 JNI 架构实现。

---

## 核心架构

### 分层设计

```
┌─────────────────────────────────────────────────────────┐
│                    Application                           │
├─────────────────────────────────────────────────────────┤
│                    Java Layer                            │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │ RiskControl │  │   Device     │  │   Security     │  │
│  │    SDK      │  │ Fingerprint  │  │    Result      │  │
│  └──────┬──────┘  └──────┬───────┘  └───────┬────────┘  │
├─────────┴────────────────┴──────────────────┴───────────┤
│                    JNI Bridge                            │
│         native_init() / native_collect() / ...          │
├─────────────────────────────────────────────────────────┤
│                    Native Layer (C/C++)                  │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │ Fingerprint │  │   Security   │  │  Anti-Reverse  │  │
│  │  Collector  │  │   Detector   │  │   Protection   │  │
│  └─────────────┘  └──────────────┘  └────────────────┘  │
├─────────────────────────────────────────────────────────┤
│                    System Layer                          │
│     /proc  |  /sys  |  syscall  |  linker  |  ART      │
└─────────────────────────────────────────────────────────┘
```

### 设计原则

1. **敏感逻辑下沉 Native**: 核心检测算法放在 C/C++ 层，增加逆向难度
2. **JNI 动态注册**: 避免静态符号暴露，使用 `RegisterNatives` 动态绑定
3. **多维度采集**: 硬件、软件、网络、行为多个维度交叉验证
4. **分层防护**: 每层都有独立的安全检测机制

---

## 项目结构

```
risk-control-sdk/
├── src/
│   ├── java/com/riskcontrol/
│   │   ├── RiskControlSDK.java      # 对外 API 入口
│   │   ├── DeviceFingerprint.java   # 设备指纹数据结构
│   │   ├── SecurityResult.java      # 安全检测结果
│   │   └── RiskScore.java           # 风险评分
│   └── native/
│       ├── risk_control.c/.h        # 主控制逻辑
│       ├── fingerprint_collector.c  # 指纹采集
│       ├── security_detector.c      # 安全检测
│       ├── anti_reverse.c/.h        # 反逆向保护
│       ├── art_method_hook.c/.h     # ART Hook 检测
│       └── svc_syscall.c/.h         # 直接系统调用
└── CMakeLists.txt
```

---

## 核心模块设计

### 1. Java 层 API 设计

Java 层提供简洁的对外接口，隐藏底层复杂性：

```java
public class RiskControlSDK {
    private static volatile RiskControlSDK instance;

    static {
        System.loadLibrary("riskcontrol");
    }

    // 单例模式
    public static RiskControlSDK getInstance() {
        if (instance == null) {
            synchronized (RiskControlSDK.class) {
                if (instance == null) {
                    instance = new RiskControlSDK();
                }
            }
        }
        return instance;
    }

    // Native 方法声明
    private native int nativeInit();
    private native String nativeCollectFingerprint();
    private native int nativeSecurityCheck();
    private native void nativeCleanup();

    // 对外 API
    public DeviceFingerprint getDeviceFingerprint() {
        String rawData = nativeCollectFingerprint();
        return DeviceFingerprint.parse(rawData);
    }

    public SecurityResult performSecurityCheck() {
        int flags = nativeSecurityCheck();
        return new SecurityResult(flags);
    }

    public RiskScore calculateRiskScore(DeviceFingerprint fp, SecurityResult sr) {
        // 综合评分算法
        int score = 100;
        if (sr.isRooted()) score -= 30;
        if (sr.isEmulator()) score -= 40;
        if (sr.isHooked()) score -= 50;
        if (sr.isDebugged()) score -= 20;
        return new RiskScore(Math.max(0, score));
    }
}
```

### 2. JNI 动态注册

避免函数名暴露，使用动态注册方式：

```c
// risk_control.c

// 方法映射表（隐藏真实函数名）
static JNINativeMethod g_methods[] = {
    {"nativeInit",               "()I",                   (void*)rc_init},
    {"nativeCollectFingerprint", "()Ljava/lang/String;",  (void*)rc_collect},
    {"nativeSecurityCheck",      "()I",                   (void*)rc_check},
    {"nativeCleanup",            "()V",                   (void*)rc_cleanup},
};

// JNI_OnLoad 动态注册
JNIEXPORT jint JNI_OnLoad(JavaVM* vm, void* reserved) {
    JNIEnv* env;
    if ((*vm)->GetEnv(vm, (void**)&env, JNI_VERSION_1_6) != JNI_OK) {
        return JNI_ERR;
    }

    // 自检：检测是否被调试或 Hook
    if (detect_debugger() || detect_frida()) {
        return JNI_ERR;  // 拒绝加载
    }

    jclass clazz = (*env)->FindClass(env, "com/riskcontrol/RiskControlSDK");
    if (clazz == NULL) {
        return JNI_ERR;
    }

    // 动态注册 Native 方法
    int method_count = sizeof(g_methods) / sizeof(g_methods[0]);
    if ((*env)->RegisterNatives(env, clazz, g_methods, method_count) < 0) {
        return JNI_ERR;
    }

    return JNI_VERSION_1_6;
}
```

### 3. 设备指纹采集

多维度采集设备唯一标识：

```c
// fingerprint_collector.c

typedef struct {
    char android_id[64];
    char build_fingerprint[256];
    char hardware_serial[64];
    char mac_address[32];
    char cpu_info[128];
    uint32_t screen_metrics;
    uint32_t sensor_list_hash;
} device_fingerprint_t;

// 采集硬件信息（直接读取 /proc 和 /sys）
static void collect_hardware_info(device_fingerprint_t* fp) {
    // 读取 CPU 信息
    FILE* f = fopen("/proc/cpuinfo", "r");
    if (f) {
        char line[256];
        while (fgets(line, sizeof(line), f)) {
            if (strstr(line, "Hardware") || strstr(line, "model name")) {
                strncpy(fp->cpu_info, line, sizeof(fp->cpu_info) - 1);
                break;
            }
        }
        fclose(f);
    }

    // 读取 MAC 地址
    f = fopen("/sys/class/net/wlan0/address", "r");
    if (f) {
        fgets(fp->mac_address, sizeof(fp->mac_address), f);
        fclose(f);
    }
}

// 使用直接系统调用读取（绕过 libc Hook）
static int read_file_svc(const char* path, char* buf, size_t size) {
    int fd = syscall_open(path, O_RDONLY);
    if (fd < 0) return -1;

    int ret = syscall_read(fd, buf, size);
    syscall_close(fd);
    return ret;
}
```

### 4. 安全检测模块

检测各类逆向分析环境：

```c
// security_detector.c

#define FLAG_ROOTED      (1 << 0)
#define FLAG_EMULATOR    (1 << 1)
#define FLAG_DEBUGGED    (1 << 2)
#define FLAG_HOOKED      (1 << 3)
#define FLAG_TAMPERED    (1 << 4)

// Root 检测
static int detect_root(void) {
    const char* su_paths[] = {
        "/system/bin/su",
        "/system/xbin/su",
        "/sbin/su",
        "/data/local/su",
        "/data/local/bin/su",
    };

    for (int i = 0; i < sizeof(su_paths)/sizeof(su_paths[0]); i++) {
        if (access(su_paths[i], F_OK) == 0) {
            return 1;
        }
    }

    // 检测 Magisk
    if (access("/sbin/.magisk", F_OK) == 0) {
        return 1;
    }

    return 0;
}

// 模拟器检测
static int detect_emulator(void) {
    char buf[256];

    // 检查 Build 属性
    __system_property_get("ro.product.model", buf);
    if (strstr(buf, "sdk") || strstr(buf, "Emulator")) {
        return 1;
    }

    // 检查 QEMU 特征文件
    if (access("/dev/qemu_pipe", F_OK) == 0 ||
        access("/dev/goldfish_pipe", F_OK) == 0) {
        return 1;
    }

    // 检查 CPU 特征
    read_file_svc("/proc/cpuinfo", buf, sizeof(buf));
    if (strstr(buf, "goldfish") || strstr(buf, "ranchu")) {
        return 1;
    }

    return 0;
}

// Frida 检测
static int detect_frida(void) {
    // 1. 检测默认端口
    struct sockaddr_in addr;
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    addr.sin_family = AF_INET;
    addr.sin_port = htons(27042);  // Frida 默认端口
    addr.sin_addr.s_addr = inet_addr("127.0.0.1");

    if (connect(sock, (struct sockaddr*)&addr, sizeof(addr)) == 0) {
        close(sock);
        return 1;  // 端口开放，可能有 Frida
    }
    close(sock);

    // 2. 扫描 /proc/self/maps 查找 Frida 模块
    FILE* f = fopen("/proc/self/maps", "r");
    if (f) {
        char line[512];
        while (fgets(line, sizeof(line), f)) {
            if (strstr(line, "frida") || strstr(line, "gadget")) {
                fclose(f);
                return 1;
            }
        }
        fclose(f);
    }

    // 3. 检测 Frida 特征字符串
    // （遍历内存查找 "LIBFRIDA" 等特征）

    return 0;
}

// 调试器检测
static int detect_debugger(void) {
    // 1. 检查 TracerPid
    char buf[256];
    read_file_svc("/proc/self/status", buf, sizeof(buf));
    char* tracer = strstr(buf, "TracerPid:");
    if (tracer) {
        int pid = atoi(tracer + 10);
        if (pid != 0) {
            return 1;
        }
    }

    // 2. ptrace 自检
    if (ptrace(PTRACE_TRACEME, 0, NULL, NULL) == -1) {
        return 1;  // 已被 ptrace
    }
    ptrace(PTRACE_DETACH, 0, NULL, NULL);

    return 0;
}

// 综合安全检测
jint rc_check(JNIEnv* env, jobject thiz) {
    int flags = 0;

    if (detect_root())      flags |= FLAG_ROOTED;
    if (detect_emulator())  flags |= FLAG_EMULATOR;
    if (detect_debugger())  flags |= FLAG_DEBUGGED;
    if (detect_frida())     flags |= FLAG_HOOKED;

    return flags;
}
```

### 5. 反逆向保护

保护 Native 代码不被轻易分析：

```c
// anti_reverse.c

// 字符串加密（编译时混淆）
#define ENCRYPTED_STR(s) decrypt_string(s, sizeof(s))

static char* decrypt_string(const char* enc, size_t len) {
    static char buf[256];
    for (size_t i = 0; i < len && i < sizeof(buf) - 1; i++) {
        buf[i] = enc[i] ^ 0x5A;  // 简单 XOR（实际应使用更复杂算法）
    }
    buf[len] = '\0';
    return buf;
}

// 控制流平坦化示例
static int obfuscated_check(int input) {
    int state = 0;
    int result = 0;

    while (1) {
        switch (state) {
            case 0:
                if (input > 10) state = 1;
                else state = 2;
                break;
            case 1:
                result = input * 2;
                state = 3;
                break;
            case 2:
                result = input + 5;
                state = 3;
                break;
            case 3:
                return result;
        }
    }
}

// 完整性校验（检测代码是否被篡改）
static int verify_integrity(void) {
    Dl_info info;
    if (dladdr((void*)verify_integrity, &info) == 0) {
        return -1;
    }

    // 读取 .text 段计算校验和
    // 与预置值比较，检测是否被 patch

    return 0;
}
```

### 6. 直接系统调用

绕过 libc 层的 Hook：

```c
// svc_syscall.c (ARM64)

// 直接 SVC 调用，绕过 libc
static inline long syscall_open(const char* path, int flags) {
    long ret;
    __asm__ volatile (
        "mov x0, %1\n"
        "mov x1, %2\n"
        "mov x8, #56\n"    // __NR_openat
        "mov x0, #-100\n"  // AT_FDCWD
        "svc #0\n"
        "mov %0, x0\n"
        : "=r"(ret)
        : "r"(path), "r"(flags)
        : "x0", "x1", "x8"
    );
    return ret;
}

static inline long syscall_read(int fd, void* buf, size_t count) {
    long ret;
    __asm__ volatile (
        "mov x0, %1\n"
        "mov x1, %2\n"
        "mov x2, %3\n"
        "mov x8, #63\n"    // __NR_read
        "svc #0\n"
        "mov %0, x0\n"
        : "=r"(ret)
        : "r"(fd), "r"(buf), "r"(count)
        : "x0", "x1", "x2", "x8"
    );
    return ret;
}
```

---

## 数据流设计

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  App 调用    │────▶│  Java API    │────▶│  JNI Bridge  │
│  SDK.init()  │     │  getInstance │     │  nativeInit  │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                  │
                                                  ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  返回结果    │◀────│  组装数据    │◀────│  Native 采集 │
│  RiskScore   │     │  Fingerprint │     │  /proc /sys  │
└──────────────┘     └──────────────┘     └──────────────┘
```

---

## 快速编译

如需编译测试，只需执行：

```bash
mkdir build && cd build
cmake ..
make -j$(nproc)
```

输出文件：
- `libriskcontrol.so` - Native 库
- `RiskControlSDK.jar` - Java 封装

---

## 总结

本 Demo 展示了客户端风控 SDK 的核心设计理念：

| 模块 | 核心思想 |
|------|----------|
| JNI 动态注册 | 隐藏函数符号，增加静态分析难度 |
| 设备指纹 | 多维度采集，交叉验证 |
| 安全检测 | 多层次检测 Root/模拟器/Hook/调试器 |
| 直接系统调用 | 绕过 libc Hook，获取真实数据 |
| 反逆向保护 | 字符串加密、控制流混淆、完整性校验 |

理解这些设计思路，有助于在逆向分析时快速定位关键逻辑。
