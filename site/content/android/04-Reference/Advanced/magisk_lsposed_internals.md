---
title: "Magisk 与 LSPosed 技术原理"
date: 2025-09-25
type: posts
tags: ["Native层", "代理池", "Frida", "SSL Pinning", "DEX", "高级"]
weight: 10
---

# Magisk 与 LSPosed 技术原理

Magisk 和 LSPosed 是 Android 平台上最流行的 Root 和 Hook 解决方案。本文深入分析其技术实现原理，帮助理解现代 Android 系统修改技术的核心机制。

---

## 目录

1. [技术架构总览](#1-技术架构总览)
2. [框架演进历史](#2-框架演进历史)
   - [Xposed 原版 (2012-2018)](#21-xposed-原版-2012-2018)
   - [EdXposed 过渡期 (2018-2020)](#22-edxposed-过渡期-2018-2020)
   - [Riru 注入框架](#23-riru-注入框架)
   - [Zygisk 注入框架](#24-zygisk-注入框架)
   - [LSPosed 现代标准 (2020-至今)](#25-lsposed-现代标准-2020-至今)
3. [Magisk 原理详解](#3-magisk-原理详解)
   - [Systemless Root 概念](#31-systemless-root-概念)
   - [Magisk 启动流程](#32-magisk-启动流程)
   - [MagiskSU 实现原理](#33-magisksu-实现原理)
   - [MagiskHide / DenyList 原理](#34-magiskhide--denylist-原理)
4. [LSPosed / Xposed 原理详解](#4-lsposed--xposed-原理详解)
   - [Xposed 框架架构](#41-xposed-框架架构)
   - [ART Hook 核心实现](#42-art-hook-核心实现)
   - [XposedBridge Java 层实现](#43-xposedbridge-java-层实现)
   - [Xposed 模块示例](#44-xposed-模块示例)
5. [LSPosed 与原版 Xposed 的区别](#5-lsposed-与原版-xposed-的区别)
   - [架构对比](#51-架构对比)
   - [LSPosed 作用域控制](#52-lsposed-作用域控制)
   - [按需注入机制](#53-按需注入机制)
   - [Binder 跨进程通信](#54-binder-跨进程通信)
6. [检测与对抗](#6-检测与对抗)
   - [常见检测方法](#61-常见检测方法)
   - [绕过检测](#62-绕过检测)
7. [总结](#7-总结)

---

## 1. 技术架构总览

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Android 系统修改技术栈                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌───────────────────────────────────────────────────────────────┐    │
│   │                     用户层 (User Space)                        │    │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │    │
│   │  │  LSPosed    │  │  模块 App   │  │  目标 App   │           │    │
│   │  │  Manager    │  │  (Xposed    │  │  (被 Hook)  │           │    │
│   │  │             │  │   Module)   │  │             │           │    │
│   │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘           │    │
│   │         │                │                │                   │    │
│   │         └────────────────┼────────────────┘                   │    │
│   │                          │                                    │    │
│   │              ┌───────────┴───────────┐                       │    │
│   │              │     LSPosed Core      │                       │    │
│   │              │   (libxposed_art.so)  │                       │    │
│   │              │   - ART Hook          │                       │    │
│   │              │   - 方法替换          │                       │    │
│   │              └───────────┬───────────┘                       │    │
│   │                          │                                    │    │
│   └──────────────────────────┼────────────────────────────────────┘    │
│                              │                                          │
│   ┌──────────────────────────┼────────────────────────────────────┐    │
│   │              ┌───────────┴───────────┐                        │    │
│   │              │       Zygisk          │                        │    │
│   │              │  (Magisk 注入机制)    │                        │    │
│   │              │  - 注入 Zygote        │                        │    │
│   │              │  - 加载模块           │                        │    │
│   │              └───────────┬───────────┘                        │    │
│   │                          │                                    │    │
│   │              ┌───────────┴───────────┐                        │    │
│   │              │       Magisk          │                        │    │
│   │              │   - Systemless Root   │                        │    │
│   │              │   - MagiskSU          │                        │    │
│   │              │   - MagiskHide/       │                        │    │
│   │              │     DenyList          │                        │    │
│   │              └───────────┬───────────┘                        │    │
│   │                          │                                    │    │
│   │                     内核层 (Kernel)                            │    │
│   └──────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│   ┌───────────────────────────────────────────────────────────────┐    │
│   │                      Boot 阶段                                 │    │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │    │
│   │  │  Boot.img   │  │ Magisk 补丁 │  │  ramdisk    │           │    │
│   │  │   (原始)    │──►│   处理     │──►│  (修改后)   │           │    │
│   │  └─────────────┘  └─────────────┘  └─────────────┘           │    │
│   └───────────────────────────────────────────────────────────────┘    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 框架演进历史

理解 LSPosed，需要先理清 Xposed 框架的演进历史：

```
Xposed (元祖) ──► EdXposed (过渡) ──► LSPosed (现代标准)
     │                  │                    │
     │                  │                    │
     ▼                  ▼                    ▼
替换 app_process   Riru 注入 Zygote    Zygisk/Riru 注入
  (修改 /system)      (Systemless)         (Magisk 生态)
```

### 2.1 Xposed 原版 (2012-2018)

Xposed 是由 rovo89 开发的 Android Hook 框架，开创了 Java 层方法 Hook 的先河。

**核心特点**：

| 特性 | 说明 |
|-----|------|
| 实现方式 | 替换 `/system/bin/app_process` |
| Root 方式 | 需要传统 Root (修改 /system) |
| 支持版本 | Android 4.0 - 8.x (Dalvik/ART) |
| 注入范围 | 全局注入所有进程 |
| 维护状态 | 2018 年停止更新 |

**技术原理**：

```c
/**
 * Xposed 原版通过替换 app_process 实现全局注入
 *
 * 原始启动流程:
 * init → zygote (app_process) → fork → App
 *
 * Xposed 修改后:
 * init → zygote (app_process_xposed) → XposedBridge 加载 → fork → App
 */

// app_process 被替换为 Xposed 修改版
// 在 ZygoteInit 阶段加载 XposedBridge.jar
// 所有 fork 出的 App 都继承了 Xposed 的 Hook 能力
```

**致命缺陷**：

1. 修改 `/system` 分区，无法通过 SafetyNet/Play Integrity
2. 全局注入导致系统卡顿、耗电
3. 兼容性差，不支持新版 Android

### 2.2 EdXposed 过渡期 (2018-2020)

EdXposed (Elder Xposed) 是 Xposed 的社区接力项目，解决了原版 Xposed 的一些问题。

**核心改进**：

| 特性 | Xposed 原版 | EdXposed |
|-----|------------|----------|
| Root 方式 | 修改 /system | 基于 Magisk |
| 注入方式 | 替换 app_process | Riru 注入 |
| 支持版本 | ≤ Android 8 | Android 8-11 |
| 作用域 | 全局 | 部分支持白名单 |

**EdXposed 架构**：

```
┌─────────────────────────────────────────────────────────────┐
│                      EdXposed 架构                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────────────┐                                       │
│   │ EdXposed Manager│ ←── 管理模块、配置                    │
│   └────────┬────────┘                                       │
│            │                                                │
│            ▼                                                │
│   ┌─────────────────┐                                       │
│   │   EdXposed Core │ ←── libxposed_art.so (ART Hook)       │
│   └────────┬────────┘                                       │
│            │                                                │
│            ▼                                                │
│   ┌─────────────────┐                                       │
│   │      Riru       │ ←── Zygote 注入框架                   │
│   └────────┬────────┘                                       │
│            │                                                │
│            ▼                                                │
│   ┌─────────────────┐                                       │
│   │     Magisk      │ ←── Systemless Root 基础              │
│   └─────────────────┘                                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 Riru 注入框架

Riru 是一个通用的 Zygote 注入框架，允许模块在 Zygote 进程中运行代码。

**核心原理**：利用 Android 的 `native bridge` 机制注入 Zygote。

```c
/**
 * Riru 注入原理
 *
 * Android 的 native bridge 用于运行非原生架构的代码
 * (例如在 ARM64 设备上运行 x86 应用)
 *
 * Riru 劫持了这个机制:
 */

// 1. Magisk 模块将 libriru.so 放入指定位置
// /system/lib64/libriruloader.so

// 2. 修改系统属性
// ro.dalvik.vm.native.bridge=libriruloader.so

// 3. Zygote 启动时加载 native bridge
// 实际上加载的是 Riru

// 4. Riru 加载所有 Riru 模块
void riru_init() {
    // 读取 /data/adb/riru/modules/ 目录
    // 加载每个模块的 .so 文件
    for (auto& module : riru_modules) {
        dlopen(module.path, RTLD_NOW);
    }
}

// 5. 模块可以 Hook Zygote 的关键函数
// 如 nativeForkAndSpecialize, nativeSpecializeAppProcess
```

**Riru 模块结构**：

```
/data/adb/riru/modules/
└── edxposed/
    ├── lib/
    │   ├── arm64-v8a/
    │   │   └── libriru_edxposed.so
    │   └── armeabi-v7a/
    │       └── libriru_edxposed.so
    └── module.prop
```

**Riru API (模块开发)**：

```c
// Riru 模块入口
extern "C" void* init(void* handle) {
    // 注册回调
    return riruInit(handle, riruApiVersion, &riruModuleInfo);
}

// nativeForkAndSpecialize 前回调
extern "C" void nativeForkAndSpecializePre(
    JNIEnv *env, jclass clazz, jint uid, jint gid,
    jintArray gids, jint runtimeFlags, ...
) {
    // 在 fork 前执行
    // 可以修改参数
}

// nativeForkAndSpecialize 后回调
extern "C" void nativeForkAndSpecializePost(
    JNIEnv *env, jclass clazz, jint result
) {
    if (result == 0) {
        // 子进程 (新 App)
        // 执行 Hook 逻辑
    }
}
```

### 2.4 Zygisk 注入框架

Zygisk 是 Magisk v24+ 引入的官方 Zygote 注入机制，作为 Riru 的替代方案。

**Zygisk vs Riru**：

| 特性 | Riru | Zygisk |
|-----|------|--------|
| 维护者 | 第三方 | Magisk 官方 |
| 注入方式 | Native Bridge 劫持 | 直接修补 app_process |
| 隐藏能力 | 依赖额外模块 | 内置 DenyList |
| 稳定性 | 良好 | 更好 |
| 模块兼容 | Riru 模块格式 | Zygisk 模块格式 |
| 当前状态 | 停止维护 | 活跃开发 |

**Zygisk 核心原理**：

```c
/**
 * Zygisk 直接修补 app_process (在内存中)
 * 比 Riru 的 native bridge 劫持更优雅
 */

// 1. Magisk 在 post-fs-data 阶段
//    将 app_process32/64 替换为修改版

// 2. 修改版 app_process 在 main() 开始时
//    加载 libzygisk.so

// 3. libzygisk.so Hook Zygote 的 fork 函数
void* zygisk_loader(void*) {
    // 加载 Zygisk 核心
    void* handle = dlopen("/data/adb/magisk/zygisk/libzygisk.so", RTLD_NOW);

    // 初始化
    auto entry = dlsym(handle, "zygisk_init");
    ((void(*)())entry)();

    return nullptr;
}

// 4. Zygisk 模块 API
struct ZygiskModule {
    // 在 App fork 前调用
    void (*preAppSpecialize)(void* args);

    // 在 App fork 后调用
    void (*postAppSpecialize)(const char* process_name);

    // 在系统服务 fork 前调用
    void (*preServerSpecialize)(void* args);

    // 在系统服务 fork 后调用
    void (*postServerSpecialize)();
};
```

**Zygisk 模块结构**：

```
/data/adb/modules/lsposed/
├── module.prop
├── post-fs-data.sh
├── service.sh
└── zygisk/
    ├── arm64-v8a.so    # 64位模块
    ├── armeabi-v7a.so  # 32位模块
    └── unloaded        # 控制卸载行为的标记
```

**Zygisk 模块开发**：

```cpp
// Zygisk 模块示例
#include <zygisk.hpp>

class MyModule : public zygisk::ModuleBase {
public:
    void onLoad(zygisk::Api* api, JNIEnv* env) override {
        this->api = api;
        this->env = env;
    }

    void preAppSpecialize(zygisk::AppSpecializeArgs* args) override {
        // 获取包名
        const char* process = env->GetStringUTFChars(args->nice_name, nullptr);

        // 判断是否需要 Hook
        if (strcmp(process, "com.target.app") == 0) {
            // 请求在 fork 后继续运行
            api->setOption(zygisk::DLCLOSE_MODULE_LIBRARY, false);
        }

        env->ReleaseStringUTFChars(args->nice_name, process);
    }

    void postAppSpecialize(const zygisk::AppSpecializeArgs* args) override {
        // fork 完成后，在目标 App 中执行 Hook
        initHooks();
    }

private:
    zygisk::Api* api;
    JNIEnv* env;
};

// 注册模块
REGISTER_ZYGISK_MODULE(MyModule)
```

### 2.5 LSPosed 现代标准 (2020-至今)

LSPosed 是目前最主流的 Xposed 实现，采用 Zygisk (或 Riru) 作为注入基础。

**核心定位**：

- **Magisk** 负责 Root 权限和文件系统修改
- **Zygisk/Riru** 负责 Zygote 注入
- **LSPosed** 负责 Java 方法 Hook

```
简单说：Magisk 帮你开了门，LSPosed 帮你进去改代码。
```

**LSPosed 关键创新**：

1. **按需注入 (Scope)**：只注入勾选的目标 App
2. **随机包名**：LSPosed Manager 使用随机包名避免检测
3. **寄生模式**：可将管理器寄生到其他 App 中
4. **Binder 通信**：Manager 与 Core 通过 Binder 通信

**LSPosed 启动流程**：

```
系统启动
    │
    ▼
Magisk 启动 ──► 加载 Zygisk/Riru
    │
    ▼
Zygisk 注入 Zygote ──► 加载 LSPosed Core
    │
    ▼
App 启动请求 (fork from Zygote)
    │
    ▼
LSPosed 检查: 这个 App 在哪些模块的作用域中?
    │
    ├── 在 "微信防撤回" 作用域中 ──► 加载该模块
    │
    ├── 不在任何作用域中 ──► 不加载任何模块
    │
    ▼
App 正常运行 (仅加载必要模块)
```

---

## 3. Magisk 原理详解

### 3.1 Systemless Root 概念

Magisk 的核心创新是 **Systemless Root** - 在不修改 `/system` 分区的情况下获取 Root 权限。

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     传统 Root vs Systemless Root                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  【传统 Root】                                                          │
│                                                                         │
│  /system/                                                               │
│  ├── bin/                                                               │
│  │   └── su          ◄── 直接修改 /system 分区                         │
│  ├── xbin/                                                              │
│  │   └── su                                                             │
│  └── app/                                                               │
│      └── Superuser/  ◄── Root 管理 App                                 │
│                                                                         │
│  问题:                                                                  │
│  - 无法通过 OTA 升级                                                    │
│  - 无法通过 SafetyNet                                                   │
│  - 修改系统分区可能变砖                                                  │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  【Systemless Root (Magisk)】                                           │
│                                                                         │
│  /system/  ◄── 完全不修改                                               │
│                                                                         │
│  /data/adb/magisk/                                                      │
│  ├── magisk           ◄── Magisk 二进制                                │
│  ├── magiskinit                                                         │
│  ├── magiskpolicy                                                       │
│  └── busybox                                                            │
│                                                                         │
│  Boot Image 修改:                                                       │
│  boot.img                                                               │
│  └── ramdisk/                                                           │
│      └── init  ──► magiskinit  ◄── 替换 init 进程                      │
│                                                                         │
│  优势:                                                                  │
│  - 系统分区完整，可正常 OTA                                              │
│  - 可绕过部分检测                                                        │
│  - 恢复简单，刷入原始 boot.img 即可                                      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Magisk 启动流程

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Magisk 启动流程                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. Bootloader 加载修补后的 boot.img                                    │
│     │                                                                   │
│     ▼                                                                   │
│  2. Kernel 启动，执行 ramdisk 中的 init                                 │
│     │   (实际是 magiskinit)                                             │
│     │                                                                   │
│     ▼                                                                   │
│  3. magiskinit 执行初始化                                               │
│     ├── 解析 /system, /vendor 等分区                                    │
│     ├── 注入 Magisk 到 /sbin                                            │
│     ├── 修补 sepolicy (SELinux 策略)                                    │
│     └── 启动原始 init                                                   │
│     │                                                                   │
│     ▼                                                                   │
│  4. 原始 init 执行系统初始化                                            │
│     │                                                                   │
│     ▼                                                                   │
│  5. post-fs-data 阶段                                                   │
│     ├── Magisk 挂载模块                                                 │
│     ├── 执行 post-fs-data.d 脚本                                        │
│     └── 设置 MagiskSU 守护进程                                          │
│     │                                                                   │
│     ▼                                                                   │
│  6. late_start 阶段                                                     │
│     ├── 执行 service.d 脚本                                             │
│     └── Zygisk 初始化 (如果启用)                                        │
│     │                                                                   │
│     ▼                                                                   │
│  7. 系统完全启动，Magisk 功能就绪                                       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.3 MagiskSU 实现原理

```c
/**
 * MagiskSU 核心实现原理 (简化版)
 *
 * Magisk 的 su 实现不是传统的 SUID 二进制，
 * 而是通过 Unix Domain Socket 与守护进程通信
 */

// ==================== su 客户端 ====================

/**
 * su_client.c - su 命令的客户端实现
 */

#include <sys/socket.h>
#include <sys/un.h>

#define MAGISK_SOCKET "/dev/socket/magisk"

// su 请求结构
struct su_request {
    int uid;           // 请求的 UID
    int login;         // 是否使用 login shell
    int keepenv;       // 是否保留环境变量
    char *shell;       // 指定 shell
    char *command;     // 要执行的命令
};

// su 响应
struct su_response {
    int allow;         // 是否允许
    int uid;           // 授权的 UID
    int gid;           // 授权的 GID
};

int su_client_main(int argc, char **argv) {
    // 1. 解析命令行参数
    struct su_request req = parse_args(argc, argv);

    // 2. 连接到 Magisk 守护进程
    int sockfd = socket(AF_UNIX, SOCK_STREAM, 0);

    struct sockaddr_un addr;
    addr.sun_family = AF_UNIX;
    strcpy(addr.sun_path, MAGISK_SOCKET);

    if (connect(sockfd, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
        fprintf(stderr, "Cannot connect to Magisk daemon\n");
        return 1;
    }

    // 3. 发送 su 请求
    //    包含调用者 PID、UID、请求的权限等
    send_su_request(sockfd, &req);

    // 4. 等待守护进程响应
    struct su_response resp;
    recv_su_response(sockfd, &resp);

    if (!resp.allow) {
        fprintf(stderr, "Permission denied\n");
        return 1;
    }

    // 5. 守护进程通过 socket 传递 pts (伪终端)
    int pts_fd = recv_fd(sockfd);

    // 6. 使用新的 pts 执行 shell
    //    此时已经在守护进程创建的 Root 环境中
    dup2(pts_fd, STDIN_FILENO);
    dup2(pts_fd, STDOUT_FILENO);
    dup2(pts_fd, STDERR_FILENO);

    execvp(req.shell ?: "/system/bin/sh", argv);

    return 0;
}

// ==================== su 守护进程 ====================

/**
 * su_daemon.c - Magisk 守护进程中处理 su 请求
 */

void handle_su_request(int client_fd) {
    // 1. 接收客户端信息
    struct su_request req;
    recv_su_request(client_fd, &req);

    // 2. 获取调用者信息
    struct ucred cred;
    socklen_t len = sizeof(cred);
    getsockopt(client_fd, SOL_SOCKET, SO_PEERCRED, &cred, &len);

    int caller_uid = cred.uid;
    int caller_pid = cred.pid;

    // 3. 查找调用者的应用信息
    char *pkg_name = get_package_name(caller_uid);
    char *app_name = get_app_name(caller_pid);

    // 4. 检查数据库中的授权状态
    int policy = check_su_policy(pkg_name);

    struct su_response resp;

    switch (policy) {
        case POLICY_ALLOW:
            // 已授权，直接允许
            resp.allow = 1;
            break;

        case POLICY_DENY:
            // 已拒绝
            resp.allow = 0;
            break;

        case POLICY_QUERY:
        default:
            // 需要询问用户
            resp.allow = prompt_user_for_su(pkg_name, app_name, caller_uid);

            // 记录用户选择
            save_su_policy(pkg_name, resp.allow);
            break;
    }

    // 5. 发送响应
    send_su_response(client_fd, &resp);

    if (!resp.allow) {
        close(client_fd);
        return;
    }

    // 6. 创建 Root 环境
    //    fork 一个子进程，设置其权限

    int pts_master, pts_slave;
    openpty(&pts_master, &pts_slave, NULL, NULL, NULL);

    pid_t pid = fork();

    if (pid == 0) {
        // 子进程 - 将成为 Root shell

        close(pts_master);
        setsid();

        // 设置 UID/GID 为 root
        setuid(0);
        setgid(0);

        // 设置 SELinux context
        setcon("u:r:su:s0");

        // 设置环境变量
        setenv("HOME", "/data", 1);
        setenv("SHELL", "/system/bin/sh", 1);
        setenv("PATH", "/sbin:/system/bin:/system/xbin", 1);

        // 重定向 stdio 到 pts
        dup2(pts_slave, STDIN_FILENO);
        dup2(pts_slave, STDOUT_FILENO);
        dup2(pts_slave, STDERR_FILENO);

        // 执行 shell
        execlp("/system/bin/sh", "sh", NULL);

    } else {
        // 父进程 - 守护进程

        close(pts_slave);

        // 将 pts_master fd 发送给客户端
        send_fd(client_fd, pts_master);

        // 等待子进程结束
        waitpid(pid, NULL, 0);
    }
}
```

### 2.4 MagiskHide / DenyList 原理

```c
/**
 * MagiskHide/DenyList 实现原理
 *
 * 目标: 对特定应用隐藏 Magisk 的存在
 */

// ==================== 进程隐藏 ====================

/**
 * hide_daemon.c - 隐藏守护进程
 */

#include <sys/ptrace.h>
#include <sys/mount.h>

// 需要隐藏的应用列表
struct hide_list {
    char *package_name;
    int uid;
};

// 监听 Zygote fork
void monitor_zygote() {
    // 使用 ptrace 或 inotify 监控 /proc/[zygote_pid]/task

    while (1) {
        // 检测新 fork 的进程
        pid_t new_pid = detect_new_fork();

        if (new_pid > 0) {
            // 获取进程信息
            char *cmdline = read_proc_cmdline(new_pid);
            int uid = get_process_uid(new_pid);

            // 检查是否在隐藏列表中
            if (should_hide(cmdline, uid)) {
                // 对该进程执行隐藏操作
                do_hide_process(new_pid);
            }
        }
    }
}

/**
 * 对目标进程执行隐藏
 */
void do_hide_process(pid_t pid) {
    // 1. 等待进程完成初始化
    //    使用 ptrace 或等待特定事件
    wait_for_process_init(pid);

    // 2. 卸载 Magisk 挂载的文件系统
    //    在目标进程的 mount namespace 中操作

    char ns_path[64];
    snprintf(ns_path, sizeof(ns_path), "/proc/%d/ns/mnt", pid);

    int ns_fd = open(ns_path, O_RDONLY);
    setns(ns_fd, CLONE_NEWNS);

    // 卸载 Magisk 模块挂载点
    unmount_magisk_mounts();

    // 3. 清理 /proc 中的痕迹
    //    (这部分比较复杂，需要内核支持)

    // 4. 恢复原始的系统属性
    //    某些属性会暴露 Root 状态

    // 5. 让进程继续执行
    ptrace(PTRACE_DETACH, pid, NULL, NULL);
}

/**
 * 卸载 Magisk 挂载点
 */
void unmount_magisk_mounts() {
    // 读取 /proc/self/mounts
    FILE *fp = fopen("/proc/self/mounts", "r");

    char line[1024];
    while (fgets(line, sizeof(line), fp)) {
        // 查找 Magisk 相关挂载
        if (strstr(line, "magisk") ||
            strstr(line, "/sbin/.magisk") ||
            strstr(line, "/data/adb")) {

            // 提取挂载点
            char *mountpoint = parse_mountpoint(line);

            // 卸载
            umount2(mountpoint, MNT_DETACH);
        }
    }

    fclose(fp);

    // 卸载模块的 overlay 挂载
    unmount_module_overlays();
}

// ==================== Zygisk 实现 ====================

/**
 * Zygisk - Magisk 在 Zygote 中的代码注入
 *
 * Zygisk 允许模块在 App 进程启动前注入代码，
 * 是 LSPosed 等框架的基础
 */

// zygisk_loader.cpp

#include <android/dlext.h>

/**
 * Zygote 进程启动时的钩子
 * 通过修改 LD_PRELOAD 实现
 */
__attribute__((constructor))
void zygisk_init() {
    // 检测当前是否是 Zygote 进程
    if (!is_zygote_process()) {
        return;
    }

    // Hook Zygote 的关键函数
    hook_zygote_functions();

    // 加载 Zygisk 模块
    load_zygisk_modules();
}

/**
 * Hook app_process 中的 fork 函数
 */
void hook_zygote_functions() {
    // 使用 PLT Hook 或 inline hook

    // Hook nativeForkAndSpecialize
    // 这是 Zygote fork 新应用进程的入口
    void *art_handle = dlopen("libart.so", RTLD_NOW);

    void *original_fork = dlsym(art_handle, "_ZN3art..."
        "nativeForkAndSpecializeEi...");

    // 替换为我们的函数
    hook_function(original_fork, my_fork_and_specialize);
}

/**
 * 我们的 fork 处理函数
 */
int my_fork_and_specialize(
    JNIEnv *env,
    jclass clazz,
    jint uid,
    jint gid,
    jintArray gids,
    jint runtime_flags,
    jobjectArray rlimits,
    jint mount_external,
    jstring se_info,
    jstring nice_name,  // 包名
    jintArray fds_to_close,
    jintArray fds_to_ignore,
    jboolean is_child_zygote,
    jstring instruction_set,
    jstring app_data_dir,
    jboolean is_top_app
) {
    // 获取包名
    const char *pkg_name = env->GetStringUTFChars(nice_name, NULL);

    // 检查是否需要对这个 App 执行操作
    bool should_hook = check_module_target(pkg_name);
    bool should_hide = check_hide_list(pkg_name);

    // 调用原始 fork
    int pid = original_fork_and_specialize(
        env, clazz, uid, gid, gids, runtime_flags,
        rlimits, mount_external, se_info, nice_name,
        fds_to_close, fds_to_ignore, is_child_zygote,
        instruction_set, app_data_dir, is_top_app
    );

    if (pid == 0) {
        // 子进程 (新 App)

        if (should_hide) {
            // 在子进程中执行隐藏
            do_unmount_in_child();
        }

        if (should_hook) {
            // 通知模块进行 Hook
            notify_modules_app_forked(pkg_name, uid);
        }
    }

    env->ReleaseStringUTFChars(nice_name, pkg_name);
    return pid;
}
```

---

## 3. LSPosed / Xposed 原理详解

### 3.1 Xposed 框架架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        LSPosed/Xposed 架构                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │                      Xposed Module (APK)                         │  │
│   │  ┌─────────────────┐  ┌─────────────────┐                       │  │
│   │  │  IXposedHookLoad │  │  XposedBridge   │                       │  │
│   │  │  InitPackageRes │  │  - findAndHook   │                       │  │
│   │  │  ZygoteInit     │  │    Method        │                       │  │
│   │  └────────┬────────┘  └────────┬────────┘                       │  │
│   │           │                    │                                 │  │
│   └───────────┼────────────────────┼─────────────────────────────────┘  │
│               │                    │                                    │
│               ▼                    ▼                                    │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │                    XposedBridge.jar                              │  │
│   │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │  │
│   │  │  XposedHelpers  │  │  XC_MethodHook  │  │  XC_MethodRepl  │ │  │
│   │  │  - findClass    │  │  - beforeHooked │  │  acement        │ │  │
│   │  │  - findMethod   │  │    Method       │  │                 │ │  │
│   │  │  - getField     │  │  - afterHooked  │  │                 │ │  │
│   │  │                 │  │    Method       │  │                 │ │  │
│   │  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘ │  │
│   │           │                    │                    │          │  │
│   └───────────┼────────────────────┼────────────────────┼──────────┘  │
│               │                    │                    │              │
│               ▼                    ▼                    ▼              │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │                   libxposed_art.so (Native)                      │  │
│   │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │  │
│   │  │   ART Hook      │  │  Method Entry   │  │  Backup/Restore │ │  │
│   │  │  - entry_point  │  │   Trampoline    │  │    Original     │ │  │
│   │  │    replacement  │  │                 │  │    Method       │ │  │
│   │  └─────────────────┘  └─────────────────┘  └─────────────────┘ │  │
│   └─────────────────────────────────────────────────────────────────┘  │
│                               │                                        │
│                               ▼                                        │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │                    ART Runtime (libart.so)                       │  │
│   │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │  │
│   │  │   ArtMethod     │  │   JIT Compiler  │  │  Class Linker  │ │  │
│   │  │  - entry_point_ │  │                 │  │                 │ │  │
│   │  │  - code_item_   │  │                 │  │                 │ │  │
│   │  └─────────────────┘  └─────────────────┘  └─────────────────┘ │  │
│   └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.2 ART Hook 核心实现

```cpp
/**
 * LSPosed ART Hook 实现原理
 *
 * 核心思想: 修改 ArtMethod 的 entry_point_from_quick_compiled_code_
 * 使方法调用跳转到我们的 trampoline 代码
 */

// ==================== ArtMethod 结构 ====================

/**
 * ART 虚拟机中的方法表示
 * (简化版，实际结构更复杂)
 */
struct ArtMethod {
    // GC 相关
    uint32_t gc_root_;

    // 声明此方法的类
    uint32_t declaring_class_;

    // 访问标志 (public, private, static 等)
    uint32_t access_flags_;

    // 方法在 DEX 文件中的索引
    uint32_t dex_method_index_;

    // 方法在 vtable 中的索引
    uint16_t method_index_;

    // 热度计数 (用于 JIT)
    uint16_t hotness_count_;

    // ========== 关键字段 ==========

    // 解释执行时使用的 DEX 字节码指针
    void *dex_code_item_offset_;

    // 快速编译代码的入口点
    // 这是 Hook 的核心目标!
    void *entry_point_from_quick_compiled_code_;

    // JNI 入口点 (native 方法)
    void *entry_point_from_jni_;
};

// ==================== Hook 实现 ====================

/**
 * art_hook.cpp - ART 方法 Hook
 */

#include <sys/mman.h>

// Trampoline 代码 (ARM64 示例)
// 这段代码会在被 Hook 的方法调用时执行
const uint8_t trampoline_template[] = {
    // 保存寄存器
    0xFD, 0x7B, 0xBF, 0xA9,  // stp x29, x30, [sp, #-16]!

    // 加载 hook_info 地址到 x16
    0x50, 0x00, 0x00, 0x58,  // ldr x16, #8

    // 跳转到 hook_handler
    0x00, 0x02, 0x1F, 0xD6,  // br x16

    // hook_info 地址 (占位符，运行时填充)
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
};

/**
 * Hook 信息结构
 */
struct HookInfo {
    void *original_entry;      // 原始入口点
    void *hook_handler;        // Hook 处理函数
    void *backup_method;       // 备份的原方法
    void *callback_before;     // before 回调
    void *callback_after;      // after 回调
    void *additional_info;     // 额外信息
};

/**
 * Hook 一个 Java 方法
 */
bool hook_method(
    JNIEnv *env,
    jclass clazz,
    const char *method_name,
    const char *method_sig,
    void *before_callback,
    void *after_callback
) {
    // 1. 获取 ArtMethod 指针
    jmethodID method_id = env->GetMethodID(clazz, method_name, method_sig);
    ArtMethod *art_method = (ArtMethod *)method_id;

    // 2. 备份原始方法
    //    创建一个新的 ArtMethod 作为备份
    ArtMethod *backup = create_backup_method(art_method);

    // 3. 分配 trampoline 代码内存
    //    需要可执行权限
    void *trampoline = mmap(
        NULL,
        PAGE_SIZE,
        PROT_READ | PROT_WRITE | PROT_EXEC,
        MAP_PRIVATE | MAP_ANONYMOUS,
        -1,
        0
    );

    // 4. 创建 HookInfo
    HookInfo *hook_info = new HookInfo();
    hook_info->original_entry = art_method->entry_point_from_quick_compiled_code_;
    hook_info->hook_handler = &hook_bridge;
    hook_info->backup_method = backup;
    hook_info->callback_before = before_callback;
    hook_info->callback_after = after_callback;

    // 5. 填充 trampoline 代码
    memcpy(trampoline, trampoline_template, sizeof(trampoline_template));

    // 将 hook_info 地址写入 trampoline
    *(void **)((uint8_t *)trampoline + 16) = hook_info;

    // 6. 修改原方法的入口点
    //    指向我们的 trampoline
    art_method->entry_point_from_quick_compiled_code_ = trampoline;

    // 7. 清除可能存在的 JIT 编译缓存
    invalidate_jit_code(art_method);

    return true;
}

/**
 * Hook 桥接函数
 * 当被 Hook 的方法被调用时，这个函数会被执行
 */
extern "C" void hook_bridge(HookInfo *info, ...) {
    // 1. 获取调用参数
    //    参数通过寄存器和栈传递
    va_list args;
    va_start(args, info);

    // 2. 调用 before 回调
    if (info->callback_before) {
        ((BeforeCallback)info->callback_before)(info, args);
    }

    // 3. 调用原始方法
    //    通过备份的 ArtMethod
    void *result = call_original_method(info->backup_method, args);

    // 4. 调用 after 回调
    if (info->callback_after) {
        result = ((AfterCallback)info->callback_after)(info, args, result);
    }

    va_end(args);

    // 5. 返回结果
    return result;
}

/**
 * 调用原始方法
 */
void *call_original_method(ArtMethod *backup, va_list args) {
    // 使用备份的 ArtMethod 调用原方法

    // 获取原始入口点
    void *entry = backup->entry_point_from_quick_compiled_code_;

    // 通过函数指针调用
    // 实际实现需要处理各种调用约定
    typedef void *(*MethodEntry)(ArtMethod *, ...);
    return ((MethodEntry)entry)(backup, args);
}
```

### 3.3 XposedBridge Java 层实现

```java
/**
 * XposedBridge.java - Xposed 框架的 Java 层核心
 */
public final class XposedBridge {

    private static final String TAG = "XposedBridge";

    // 存储所有已注册的 Hook
    private static final ConcurrentHashMap<Member, TreeSet<XC_MethodHook>>
            sHookedMethodCallbacks = new ConcurrentHashMap<>();

    /**
     * Hook 一个方法
     *
     * @param hookMethod 要 Hook 的方法
     * @param callback   Hook 回调
     * @return 用于取消 Hook 的 unhook 对象
     */
    public static XC_MethodHook.Unhook hookMethod(
            Member hookMethod,
            XC_MethodHook callback
    ) {
        if (!(hookMethod instanceof Method) && !(hookMethod instanceof Constructor)) {
            throw new IllegalArgumentException("Only methods and constructors can be hooked");
        }

        // 获取或创建该方法的回调集合
        TreeSet<XC_MethodHook> callbacks = sHookedMethodCallbacks.get(hookMethod);
        if (callbacks == null) {
            callbacks = new TreeSet<>();
            sHookedMethodCallbacks.put(hookMethod, callbacks);

            // 第一次 Hook 这个方法，进行 native Hook
            hookMethodNative(hookMethod);
        }

        // 添加回调
        callbacks.add(callback);

        return callback.new Unhook(hookMethod);
    }

    /**
     * Native Hook 方法
     * 由 libxposed_art.so 实现
     */
    private static native void hookMethodNative(Member method);

    /**
     * 当被 Hook 的方法被调用时，由 native 层调用此方法
     */
    private static Object handleHookedMethod(
            Member method,
            Object thisObject,
            Object[] args
    ) throws Throwable {

        // 获取该方法的所有回调
        TreeSet<XC_MethodHook> callbacks = sHookedMethodCallbacks.get(method);
        if (callbacks == null || callbacks.isEmpty()) {
            // 没有回调，直接调用原方法
            return invokeOriginalMethod(method, thisObject, args);
        }

        // 创建方法调用参数封装
        XC_MethodHook.MethodHookParam param = new XC_MethodHook.MethodHookParam();
        param.method = method;
        param.thisObject = thisObject;
        param.args = args;

        // ========== 调用 beforeHookedMethod ==========
        for (XC_MethodHook callback : callbacks) {
            try {
                callback.beforeHookedMethod(param);
            } catch (Throwable t) {
                XposedBridge.log(t);
            }

            // 如果回调设置了返回值，跳过后续处理
            if (param.returnEarly) {
                return param.getResult();
            }
        }

        // ========== 调用原始方法 ==========
        try {
            param.setResult(invokeOriginalMethod(method, param.thisObject, param.args));
        } catch (Throwable t) {
            param.setThrowable(t);
        }

        // ========== 调用 afterHookedMethod ==========
        // 注意: 逆序调用
        for (XC_MethodHook callback : callbacks.descendingSet()) {
            try {
                callback.afterHookedMethod(param);
            } catch (Throwable t) {
                XposedBridge.log(t);
            }
        }

        // 返回结果或抛出异常
        if (param.hasThrowable()) {
            throw param.getThrowable();
        }
        return param.getResult();
    }

    /**
     * 调用原始方法
     * 由 native 层实现
     */
    private static native Object invokeOriginalMethod(
            Member method,
            Object thisObject,
            Object[] args
    ) throws Throwable;
}

/**
 * XC_MethodHook.java - 方法 Hook 回调基类
 */
public abstract class XC_MethodHook implements Comparable<XC_MethodHook> {

    // Hook 优先级
    public final int priority;

    public XC_MethodHook() {
        this.priority = PRIORITY_DEFAULT;
    }

    public XC_MethodHook(int priority) {
        this.priority = priority;
    }

    /**
     * 方法调用前的回调
     */
    protected void beforeHookedMethod(MethodHookParam param) throws Throwable {
        // 默认空实现
    }

    /**
     * 方法调用后的回调
     */
    protected void afterHookedMethod(MethodHookParam param) throws Throwable {
        // 默认空实现
    }

    /**
     * 方法调用参数封装
     */
    public static class MethodHookParam {
        public Member method;
        public Object thisObject;
        public Object[] args;

        private Object result;
        private Throwable throwable;
        boolean returnEarly = false;

        public Object getResult() {
            return result;
        }

        public void setResult(Object result) {
            this.result = result;
            this.throwable = null;
            this.returnEarly = true;
        }

        public Throwable getThrowable() {
            return throwable;
        }

        public void setThrowable(Throwable throwable) {
            this.throwable = throwable;
            this.result = null;
            this.returnEarly = true;
        }

        public boolean hasThrowable() {
            return throwable != null;
        }

        public Object getResultOrThrowable() throws Throwable {
            if (throwable != null) throw throwable;
            return result;
        }
    }

    /**
     * 取消 Hook 的辅助类
     */
    public class Unhook {
        private final Member hookMethod;

        public Unhook(Member hookMethod) {
            this.hookMethod = hookMethod;
        }

        public void unhook() {
            TreeSet<XC_MethodHook> callbacks = sHookedMethodCallbacks.get(hookMethod);
            if (callbacks != null) {
                callbacks.remove(XC_MethodHook.this);
            }
        }
    }

    @Override
    public int compareTo(XC_MethodHook other) {
        // 按优先级排序
        return Integer.compare(this.priority, other.priority);
    }

    // 优先级常量
    public static final int PRIORITY_DEFAULT = 50;
    public static final int PRIORITY_LOWEST = -10000;
    public static final int PRIORITY_HIGHEST = 10000;
}

/**
 * XposedHelpers.java - 常用辅助方法
 */
public class XposedHelpers {

    /**
     * 查找并 Hook 方法
     */
    public static XC_MethodHook.Unhook findAndHookMethod(
            String className,
            ClassLoader classLoader,
            String methodName,
            Object... parameterTypesAndCallback
    ) {
        // 解析参数
        int paramCount = parameterTypesAndCallback.length - 1;
        Class<?>[] parameterTypes = new Class<?>[paramCount];
        for (int i = 0; i < paramCount; i++) {
            Object param = parameterTypesAndCallback[i];
            if (param instanceof Class) {
                parameterTypes[i] = (Class<?>) param;
            } else if (param instanceof String) {
                parameterTypes[i] = findClass((String) param, classLoader);
            }
        }

        XC_MethodHook callback = (XC_MethodHook) parameterTypesAndCallback[paramCount];

        // 查找类
        Class<?> clazz = findClass(className, classLoader);

        // 查找方法
        Method method = findMethodExact(clazz, methodName, parameterTypes);

        // Hook
        return XposedBridge.hookMethod(method, callback);
    }

    /**
     * 查找类
     */
    public static Class<?> findClass(String className, ClassLoader classLoader) {
        try {
            return classLoader.loadClass(className);
        } catch (ClassNotFoundException e) {
            throw new XposedHelpers.ClassNotFoundError(e);
        }
    }

    /**
     * 查找方法
     */
    public static Method findMethodExact(
            Class<?> clazz,
            String methodName,
            Class<?>... parameterTypes
    ) {
        try {
            Method method = clazz.getDeclaredMethod(methodName, parameterTypes);
            method.setAccessible(true);
            return method;
        } catch (NoSuchMethodException e) {
            throw new XposedHelpers.MethodNotFoundError(e);
        }
    }

    /**
     * 获取对象字段值
     */
    public static Object getObjectField(Object obj, String fieldName) {
        try {
            Field field = findField(obj.getClass(), fieldName);
            return field.get(obj);
        } catch (IllegalAccessException e) {
            throw new IllegalAccessError(e.getMessage());
        }
    }

    /**
     * 设置对象字段值
     */
    public static void setObjectField(Object obj, String fieldName, Object value) {
        try {
            Field field = findField(obj.getClass(), fieldName);
            field.set(obj, value);
        } catch (IllegalAccessException e) {
            throw new IllegalAccessError(e.getMessage());
        }
    }

    /**
     * 调用方法
     */
    public static Object callMethod(Object obj, String methodName, Object... args) {
        try {
            // 根据参数类型查找方法
            Class<?>[] paramTypes = new Class<?>[args.length];
            for (int i = 0; i < args.length; i++) {
                paramTypes[i] = args[i].getClass();
            }

            Method method = findMethodBestMatch(obj.getClass(), methodName, paramTypes);
            return method.invoke(obj, args);
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }
}
```

### 3.4 Xposed 模块示例

```java
/**
 * 一个完整的 Xposed 模块示例
 * 功能: Hook 微信发送消息，记录聊天内容
 */
package com.example.xposed.wechat;

import de.robv.android.xposed.IXposedHookLoadPackage;
import de.robv.android.xposed.XC_MethodHook;
import de.robv.android.xposed.XposedBridge;
import de.robv.android.xposed.XposedHelpers;
import de.robv.android.xposed.callbacks.XC_LoadPackage;

public class WeChatHook implements IXposedHookLoadPackage {

    private static final String TAG = "WeChatHook";
    private static final String WECHAT_PACKAGE = "com.tencent.mm";

    @Override
    public void handleLoadPackage(XC_LoadPackage.LoadPackageParam lpparam) throws Throwable {
        // 只处理微信
        if (!lpparam.packageName.equals(WECHAT_PACKAGE)) {
            return;
        }

        XposedBridge.log(TAG + ": Hooking WeChat");

        // Hook 发送消息的方法
        hookSendMessage(lpparam.classLoader);

        // Hook 接收消息的方法
        hookReceiveMessage(lpparam.classLoader);

        // Hook 登录流程
        hookLogin(lpparam.classLoader);
    }

    /**
     * Hook 发送消息
     */
    private void hookSendMessage(ClassLoader classLoader) {
        try {
            // 查找消息管理类
            // 注意: 实际类名可能被混淆，需要分析
            Class<?> msgManagerClass = XposedHelpers.findClass(
                    "com.tencent.mm.modelmulti.MMSessionProcessor",
                    classLoader
            );

            // Hook sendMessage 方法
            XposedHelpers.findAndHookMethod(
                    msgManagerClass,
                    "sendMessage",
                    String.class,  // 接收者
                    String.class,  // 消息内容
                    int.class,     // 消息类型
                    new XC_MethodHook() {
                        @Override
                        protected void beforeHookedMethod(MethodHookParam param) throws Throwable {
                            String receiver = (String) param.args[0];
                            String content = (String) param.args[1];
                            int msgType = (int) param.args[2];

                            XposedBridge.log(TAG + ": Sending message");
                            XposedBridge.log(TAG + ":   To: " + receiver);
                            XposedBridge.log(TAG + ":   Content: " + content);
                            XposedBridge.log(TAG + ":   Type: " + msgType);

                            // 可以在这里修改消息内容
                            // param.args[1] = content + " [Modified]";

                            // 或者阻止发送
                            // param.setResult(null);
                        }

                        @Override
                        protected void afterHookedMethod(MethodHookParam param) throws Throwable {
                            // 消息发送后的处理
                            Object result = param.getResult();
                            XposedBridge.log(TAG + ": Message sent, result: " + result);
                        }
                    }
            );

            XposedBridge.log(TAG + ": sendMessage hooked");

        } catch (Throwable t) {
            XposedBridge.log(TAG + ": Failed to hook sendMessage");
            XposedBridge.log(t);
        }
    }

    /**
     * Hook 接收消息
     */
    private void hookReceiveMessage(ClassLoader classLoader) {
        try {
            // Hook 消息数据库插入
            Class<?> sqliteClass = XposedHelpers.findClass(
                    "com.tencent.mm.storage.SqliteDB",
                    classLoader
            );

            XposedHelpers.findAndHookMethod(
                    sqliteClass,
                    "insert",
                    String.class,  // 表名
                    String.class,  // nullColumnHack
                    "android.content.ContentValues",
                    new XC_MethodHook() {
                        @Override
                        protected void beforeHookedMethod(MethodHookParam param) throws Throwable {
                            String tableName = (String) param.args[0];

                            // 只关心消息表
                            if (!"message".equals(tableName)) {
                                return;
                            }

                            Object contentValues = param.args[2];

                            // 提取消息内容
                            String content = (String) XposedHelpers.callMethod(
                                    contentValues, "getAsString", "content"
                            );
                            String talker = (String) XposedHelpers.callMethod(
                                    contentValues, "getAsString", "talker"
                            );

                            XposedBridge.log(TAG + ": Received message");
                            XposedBridge.log(TAG + ":   From: " + talker);
                            XposedBridge.log(TAG + ":   Content: " + content);
                        }
                    }
            );

            XposedBridge.log(TAG + ": receiveMessage hooked");

        } catch (Throwable t) {
            XposedBridge.log(TAG + ": Failed to hook receiveMessage");
            XposedBridge.log(t);
        }
    }

    /**
     * Hook 登录流程
     */
    private void hookLogin(ClassLoader classLoader) {
        try {
            // Hook 网络请求类
            Class<?> networkClass = XposedHelpers.findClass(
                    "com.tencent.mm.network.MMHttpClient",
                    classLoader
            );

            XposedHelpers.findAndHookMethod(
                    networkClass,
                    "execute",
                    "com.tencent.mm.network.MMHttpRequest",
                    new XC_MethodHook() {
                        @Override
                        protected void beforeHookedMethod(MethodHookParam param) throws Throwable {
                            Object request = param.args[0];

                            // 获取请求 URL
                            String url = (String) XposedHelpers.getObjectField(request, "url");

                            // 获取请求体
                            byte[] body = (byte[]) XposedHelpers.getObjectField(request, "body");

                            XposedBridge.log(TAG + ": HTTP Request");
                            XposedBridge.log(TAG + ":   URL: " + url);
                            if (body != null) {
                                XposedBridge.log(TAG + ":   Body length: " + body.length);
                            }
                        }

                        @Override
                        protected void afterHookedMethod(MethodHookParam param) throws Throwable {
                            Object response = param.getResult();

                            if (response != null) {
                                int statusCode = (int) XposedHelpers.getObjectField(
                                        response, "statusCode"
                                );
                                XposedBridge.log(TAG + ": HTTP Response: " + statusCode);
                            }
                        }
                    }
            );

            XposedBridge.log(TAG + ": network hooked");

        } catch (Throwable t) {
            XposedBridge.log(TAG + ": Failed to hook network");
            XposedBridge.log(t);
        }
    }
}
```

---

## 4. LSPosed 与原版 Xposed 的区别

### 4.1 架构对比

| 特性 | 原版 Xposed | LSPosed |
|-----|------------|---------|
| Root 方式 | 修改 /system | 基于 Magisk (Systemless) |
| 注入方式 | 替换 app_process | Zygisk 模块 |
| 作用范围 | 全局 | 可选择性启用 |
| 检测规避 | 无 | 支持白名单模式 |
| Android 支持 | 最高 8.x | 8.0 - 14+ |
| 维护状态 | 停止更新 | 活跃开发 |

### 4.2 LSPosed 作用域控制

```java
/**
 * LSPosed 允许为每个模块指定作用域
 * 只有在作用域内的 App 才会被 Hook
 */

// LSPosed Manager 中的配置存储
// /data/adb/lspd/config/<module_package>/scope.list

// 作用域列表格式:
// com.tencent.mm       # 微信
// com.tencent.mobileqq # QQ
// system               # 系统框架

/**
 * LSPosed 加载模块时会检查作用域
 */
public class ModuleLoader {

    public boolean shouldLoadModule(String modulePkg, String targetPkg) {
        // 读取作用域配置
        Set<String> scope = readModuleScope(modulePkg);

        // 检查目标 App 是否在作用域内
        return scope.contains(targetPkg) || scope.contains("*");
    }

    private Set<String> readModuleScope(String modulePkg) {
        File scopeFile = new File(
                "/data/adb/lspd/config/" + modulePkg + "/scope.list"
        );

        Set<String> scope = new HashSet<>();
        try (BufferedReader reader = new BufferedReader(new FileReader(scopeFile))) {
            String line;
            while ((line = reader.readLine()) != null) {
                line = line.trim();
                if (!line.isEmpty() && !line.startsWith("#")) {
                    scope.add(line);
                }
            }
        } catch (IOException e) {
            // 默认空作用域
        }

        return scope;
    }
}
```

### 5.3 按需注入机制

老版 Xposed 的致命缺点是**全局注入**：安装一个微信模块，Xposed 会把这个模块强行塞进系统里每一个进程（包括支付宝、系统设置、计算器）。

**问题后果**：
- 系统变慢、耗电
- 极易崩溃（不兼容就崩）
- 检测点多，容易被发现

**LSPosed 的革新 - 按需注入**：

```java
/**
 * LSPosed 按需注入实现
 *
 * 流程:
 * 1. 新 App 启动 (从 Zygote fork)
 * 2. LSPosed 桩代码检查: 这个 App 是谁?
 * 3. 查询配置: 哪些模块勾选了这个 App?
 * 4. 只加载相关模块
 */
public class LSPosedModuleManager {

    // 模块作用域配置
    // /data/adb/lspd/config/<module>/scope.list
    private Map<String, Set<String>> moduleScopes = new HashMap<>();

    /**
     * 当 App fork 后调用
     */
    public void onAppForked(String packageName, int uid) {
        // 遍历所有已启用的模块
        for (ModuleInfo module : getEnabledModules()) {
            // 检查该 App 是否在模块作用域中
            if (isInScope(module.packageName, packageName)) {
                // 加载该模块
                loadModule(module, packageName);
                Log.d("LSPosed", "Loaded " + module.name + " for " + packageName);
            }
        }
    }

    private boolean isInScope(String modulePkg, String targetPkg) {
        Set<String> scope = moduleScopes.get(modulePkg);
        if (scope == null) return false;

        // 检查是否在作用域中
        // 支持通配符 "*" 表示全局
        return scope.contains(targetPkg) ||
               scope.contains("*") ||
               (targetPkg.equals("system") && scope.contains("system"));
    }
}
```

**优势对比**：

| 特性 | 原版 Xposed | LSPosed |
|-----|------------|---------|
| 注入范围 | 所有进程 | 仅勾选的 App |
| 系统性能 | 明显下降 | 几乎无影响 |
| 稳定性 | 容易崩溃 | 稳定 |
| 检测难度 | 容易检测 | 更难检测 |

### 5.4 Binder 跨进程通信

LSPosed 分为两部分：
1. **LSPosed Manager**：用户看到的管理 App，负责配置模块
2. **LSPosed Core**：寄生在 Zygote 和各个 App 里的核心代码

由于它们在不同的进程，LSPosed 高度依赖 Android 的 **Binder 机制**进行通讯。

```java
/**
 * LSPosed Binder 通信架构
 */

// ==================== LSPosed Manager 侧 ====================

/**
 * Manager App 通过 Binder 与 Core 通信
 */
public class LSPosedManagerService extends ILSPosedManager.Stub {

    /**
     * 获取模块列表
     */
    @Override
    public List<ModuleInfo> getModuleList() {
        // 通过 Binder 调用 Core 的服务
        return getRemoteService().getModuleList();
    }

    /**
     * 更新模块作用域
     */
    @Override
    public void updateModuleScope(String modulePkg, List<String> scope) {
        // 写入配置
        writeScope(modulePkg, scope);

        // 通知 Core 重新加载配置
        getRemoteService().reloadConfig();
    }

    /**
     * 启用/禁用模块
     */
    @Override
    public void setModuleEnabled(String modulePkg, boolean enabled) {
        // 更新模块状态
        updateModuleStatus(modulePkg, enabled);

        // 重启相关 App 才能生效
        // (或等待下次 App 启动)
    }
}

// ==================== LSPosed Core 侧 ====================

/**
 * Core 运行在 system_server 中
 * 通过隐藏的 Binder 服务与 Manager 通信
 */
public class LSPosedService extends ILSPosedService.Stub {

    /**
     * 获取激活的模块列表
     */
    @Override
    public List<ModuleInfo> getActiveModules(String targetPackage) {
        List<ModuleInfo> result = new ArrayList<>();

        for (ModuleInfo module : allModules) {
            if (module.enabled && isInScope(module, targetPackage)) {
                result.add(module);
            }
        }

        return result;
    }

    /**
     * 重新加载配置
     * Manager 修改配置后调用
     */
    @Override
    public void reloadConfig() {
        // 重新读取配置文件
        loadModuleConfigs();

        // 通知正在运行的 Hook 更新
        notifyConfigChanged();
    }
}
```

**Binder 服务发现**：

```java
// LSPosed 使用隐藏的方式注册 Binder 服务
// 避免被其他 App 发现

// 1. Core 在 system_server 中注册服务
ServiceManager.addService("org.lsposed.daemon", mService, true, DUMP_FLAG_PRIORITY_NORMAL);

// 2. Manager 通过特殊方式获取服务
// 而不是普通的 ServiceManager.getService()
IBinder binder = new ShizukuBinderProxy().getService("org.lsposed.daemon");
```

---

## 6. Hook 技术选型对比

在 Android 逆向中，常用的 Hook 技术有三类：LSPosed (Xposed)、Frida、Inline Hook 框架。以下是详细对比和选型建议。

### 6.1 技术对比

| 维度 | LSPosed/Xposed | Frida | Inline Hook 框架 |
|-----|---------------|-------|-----------------|
| **Hook 层级** | Java 方法 | Java + Native | Native 函数 |
| **注入时机** | App 启动时 | 运行时动态注入 | 编译时 / 运行时 |
| **持久性** | 永久生效 | 临时 (进程重启失效) | 取决于实现 |
| **开发语言** | Java/Kotlin | JavaScript/Python | C/C++ |
| **上手难度** | 简单 | 中等 | 较难 |
| **Root 需求** | 需要 (Magisk) | 需要 | 取决于实现 |
| **检测难度** | 中等 | 较易检测 | 较难检测 |
| **适用场景** | 长期使用的功能模块 | 快速分析、动态调试 | 高性能、低侵入 Hook |

### 6.2 详细对比

#### LSPosed/Xposed 模块

**优势**：
- 开发简单，Java API 友好
- 持久生效，重启后仍有效
- 社区生态丰富，模块众多
- 与 Magisk 生态集成良好

**劣势**：
- 只能 Hook Java 层方法
- 需要编译 APK，迭代较慢
- 修改后需要重启 App

**适用场景**：
```
✅ 微信防撤回、去广告等长期使用的功能
✅ 系统级功能修改
✅ 发布给其他用户使用的模块
✅ 不需要频繁修改的稳定 Hook
```

#### Frida

**优势**：
- 动态注入，即时生效
- 支持 Java + Native 层
- 脚本语言开发，迭代极快
- 强大的内存操作能力
- 适合快速分析和调试

**劣势**：
- 进程重启后需要重新注入
- 容易被检测 (frida-server 特征明显)
- 性能开销较大
- 部署需要 frida-server

**适用场景**：
```
✅ 逆向分析、快速验证想法
✅ 动态调试、参数监控
✅ 加密算法分析、数据抓取
✅ 一次性的分析任务
```

#### Inline Hook 框架 (Dobby/ShadowHook/bhook)

**优势**：
- 高性能，开销极小
- 难以检测 (无明显特征)
- 支持 Hook 任意函数地址
- 可嵌入目标 App 中

**劣势**：
- 开发难度大，需要 C/C++
- 调试困难
- 需要处理 ABI、指令集等细节

**适用场景**：
```
✅ 风控 SDK 开发
✅ 高性能监控
✅ 需要隐蔽的 Hook
✅ 嵌入式 Hook (集成到 App 中)
```

### 6.3 选型决策流程

```
你的需求是什么?
    │
    ├── 快速分析 App 行为
    │   └── 选择 Frida ✅
    │
    ├── 开发给自己/他人长期使用的功能
    │   └── Java 层 Hook 够用吗?
    │       ├── 是 → 选择 LSPosed ✅
    │       └── 否 → 结合 LSPosed + Native Hook
    │
    ├── 开发风控/安全 SDK
    │   └── 选择 Inline Hook (Dobby/ShadowHook) ✅
    │
    └── 需要隐蔽的 Hook
        └── 选择 Inline Hook ✅
```

### 6.4 组合使用方案

实际项目中，往往需要组合使用多种技术：

**方案一：LSPosed + Frida**

```
开发流程:
1. 用 Frida 快速分析、定位关键函数
2. 确认 Hook 点后，用 LSPosed 模块实现持久化

适用: 大多数逆向项目
```

**方案二：LSPosed + Inline Hook**

```java
/**
 * LSPosed 模块中调用 Native Inline Hook
 */
public class MyXposedModule implements IXposedHookLoadPackage {

    @Override
    public void handleLoadPackage(XC_LoadPackage.LoadPackageParam lpparam) {
        // Java 层 Hook
        XposedHelpers.findAndHookMethod(...);

        // 加载 Native 库进行 Inline Hook
        System.loadLibrary("myhook");
        nativeInit();  // 执行 Dobby Hook
    }

    private native void nativeInit();
}
```

**方案三：Frida + Inline Hook 定位**

```javascript
// 用 Frida 定位函数后，获取地址
var targetFunc = Module.findExportByName("libtarget.so", "encrypt");
console.log("encrypt address: " + targetFunc);

// 然后用 Inline Hook 框架做持久化 Hook
// Frida 脚本输出:
// encrypt address: 0x7a3b4c5d00
// 将此地址用于 Dobby Hook
```

### 6.5 性能对比

| 技术 | Hook 安装开销 | 每次调用开销 | 内存占用 |
|-----|-------------|-------------|---------|
| LSPosed | 中 | 中 | 较大 |
| Frida | 高 | 高 | 很大 |
| PLT Hook | 低 | 极低 | 小 |
| Inline Hook | 中 | 低 | 小 |

**性能敏感场景推荐**：
- 高频函数 (如加密函数) → PLT Hook (bhook/xHook)
- 任意地址 Hook → Inline Hook (Dobby/ShadowHook)
- 分析调试阶段 → Frida (不在意性能)

---

## 7. 检测与对抗

### 7.1 常见检测方法

```java
/**
 * App 检测 Root/Xposed 的常用方法
 */
public class RootDetection {

    /**
     * 检测 su 二进制
     */
    public boolean checkSuBinary() {
        String[] paths = {
                "/system/bin/su",
                "/system/xbin/su",
                "/sbin/su",
                "/data/local/xbin/su",
                "/data/local/bin/su",
                "/data/local/su"
        };

        for (String path : paths) {
            if (new File(path).exists()) {
                return true;  // 检测到 Root
            }
        }
        return false;
    }

    /**
     * 检测 Magisk 特征
     */
    public boolean checkMagisk() {
        // 检查 Magisk 相关路径
        if (new File("/sbin/.magisk").exists()) return true;
        if (new File("/data/adb/magisk").exists()) return true;

        // 检查 Magisk 属性
        String magiskVersion = getSystemProperty("magisk.version");
        if (magiskVersion != null && !magiskVersion.isEmpty()) {
            return true;
        }

        return false;
    }

    /**
     * 检测 Xposed 框架
     */
    public boolean checkXposed() {
        // 方法1: 检查堆栈
        try {
            throw new Exception("detect");
        } catch (Exception e) {
            for (StackTraceElement element : e.getStackTrace()) {
                if (element.getClassName().contains("xposed")) {
                    return true;
                }
            }
        }

        // 方法2: 检查类加载器
        try {
            ClassLoader.getSystemClassLoader().loadClass(
                    "de.robv.android.xposed.XposedBridge"
            );
            return true;
        } catch (ClassNotFoundException e) {
            // 没有找到
        }

        // 方法3: 检查 native 方法特征
        // Xposed 会修改某些 native 方法的实现

        return false;
    }

    /**
     * 检测 Hook 框架 (通用)
     */
    public boolean checkHookFramework() {
        // 检查常见 Hook 框架的特征文件
        String[] hookIndicators = {
                "/data/data/de.robv.android.xposed.installer",
                "/data/data/org.lsposed.manager",
                "/data/data/com.saurik.substrate",
                "/data/local/tmp/frida-server"
        };

        for (String path : hookIndicators) {
            if (new File(path).exists()) {
                return true;
            }
        }

        // 检查内存中的 Hook 特征
        return checkNativeHooks();
    }

    /**
     * 检测 native 层 Hook
     */
    private native boolean checkNativeHooks();
}
```

### 7.2 绕过检测

```java
/**
 * LSPosed 模块: 绕过 Root 检测
 */
public class RootHider implements IXposedHookLoadPackage {

    @Override
    public void handleLoadPackage(XC_LoadPackage.LoadPackageParam lpparam) throws Throwable {
        // Hook File.exists()
        XposedHelpers.findAndHookMethod(
                File.class,
                "exists",
                new XC_MethodHook() {
                    @Override
                    protected void afterHookedMethod(MethodHookParam param) throws Throwable {
                        String path = ((File) param.thisObject).getAbsolutePath();

                        // 隐藏 Root 相关文件
                        if (isRootRelatedPath(path)) {
                            param.setResult(false);
                        }
                    }
                }
        );

        // Hook Runtime.exec()
        XposedHelpers.findAndHookMethod(
                Runtime.class,
                "exec",
                String.class,
                new XC_MethodHook() {
                    @Override
                    protected void beforeHookedMethod(MethodHookParam param) throws Throwable {
                        String cmd = (String) param.args[0];

                        // 阻止执行 which su, su 等命令
                        if (cmd.contains("su") || cmd.contains("magisk")) {
                            param.setThrowable(new IOException("Command not found"));
                        }
                    }
                }
        );

        // Hook System.getProperty() / Build 类
        // 修改设备指纹等

        // Hook PackageManager
        // 隐藏 Magisk/Xposed 应用
    }

    private boolean isRootRelatedPath(String path) {
        String[] patterns = {
                "su", "magisk", "supersu", "xposed", "lsposed",
                "/sbin/", "/data/adb/"
        };

        path = path.toLowerCase();
        for (String pattern : patterns) {
            if (path.contains(pattern)) {
                return true;
            }
        }
        return false;
    }
}
```

---

## 8. 总结

### 8.1 技术栈总览

| 技术 | 核心原理 | 主要用途 |
|-----|---------|---------|
| **Magisk** | 修补 boot.img, Systemless Root | Root 权限管理、模块加载 |
| **MagiskSU** | Unix Socket + 守护进程 | Root 权限请求处理 |
| **Riru** | Native Bridge 劫持注入 Zygote | 老版 Zygote 注入框架 |
| **Zygisk** | 修补 app_process 注入 Zygote | 官方 Zygote 注入框架 |
| **EdXposed** | Riru + ART Hook | 过渡期 Xposed 实现 |
| **LSPosed** | Zygisk/Riru + ART Method Hook | 现代 Xposed 实现 |
| **DenyList** | Mount namespace 隔离 | 对特定 App 隐藏 Root |

### 8.2 框架演进总结

```
时间线:
2012 ─── Xposed 诞生 (替换 app_process)
   │
2016 ─── Magisk 诞生 (Systemless Root)
   │
2018 ─── Xposed 停止更新
   │     EdXposed 接力 (基于 Riru)
   │
2020 ─── LSPosed 发布 (性能优化、按需注入)
   │
2021 ─── Magisk v24 引入 Zygisk
   │     Riru 逐渐被 Zygisk 取代
   │
2023 ─── Riru 官宣停止维护
        LSPosed Zygisk 版成为主流
```

### 8.3 最佳实践

1. **逆向分析阶段**：使用 Frida 快速分析、定位目标
2. **持久化 Hook**：使用 LSPosed 模块实现长期生效的功能
3. **高性能需求**：使用 Inline Hook 框架 (Dobby/ShadowHook)
4. **隐蔽性需求**：使用 Inline Hook + 代码混淆

这些技术共同构成了现代 Android 系统修改的核心基础设施，广泛应用于安全研究、应用开发调试和逆向工程领域。

**推荐下一步**：
- [SO 反调试与混淆](./so_anti_debugging_and_obfuscation.md)
- [Native Hook 技术](../../01-Recipes/Scripts/native_hooking.md)
