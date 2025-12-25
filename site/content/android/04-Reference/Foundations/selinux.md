---
title: "SELinux 安全机制"
date: 2024-07-22
tags: ["Native层", "签名验证", "Frida", "基础知识", "Hook", "Smali"]
weight: 10
---

# SELinux 安全机制

SELinux (Security-Enhanced Linux) 是 Android 安全模型的核心组件，从 Android 4.3 开始引入，Android 5.0 后全面强制执行。理解 SELinux 对于逆向工程、Root 检测绕过、应用沙箱分析至关重要。

---

## 目录

1. [SELinux 基础概念](#1-selinux-基础概念)
2. [Android SELinux 架构](#2-android-selinux-架构)
3. [安全上下文与标签](#3-安全上下文与标签)
4. [SELinux 策略分析](#4-selinux-策略分析)
5. [常用命令与工具](#5-常用命令与工具)
6. [逆向工程中的 SELinux](#6-逆向工程中的-selinux)
7. [SELinux 绕过技术](#7-selinux-绕过技术)
8. [实战案例](#8-实战案例)

---

## 1. SELinux 基础概念

### 1.1 什么是 SELinux

SELinux 是一种强制访问控制 (MAC, Mandatory Access Control) 安全机制，与传统的自主访问控制 (DAC, Discretionary Access Control) 不同：

| 特性 | DAC (传统 Linux) | MAC (SELinux) |
|------|------------------|---------------|
| **控制主体** | 文件所有者 | 系统策略 |
| **权限继承** | 子进程继承父进程权限 | 每个进程独立策略 |
| **Root 权限** | Root 可以做任何事 | Root 也受策略限制 |
| **灵活性** | 用户可修改权限 | 策略由管理员定义 |

### 1.2 SELinux 运行模式

```
┌─────────────────────────────────────────────────────────────┐
│                    SELinux 运行模式                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  Disabled   │  │  Permissive │  │  Enforcing  │         │
│  │  (禁用)     │  │  (宽容模式) │  │  (强制模式) │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│        ↓                ↓                ↓                  │
│   完全禁用         仅记录违规         记录+阻止违规          │
│   不检查策略       不阻止操作         阻止未授权操作          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**查看当前模式：**

```bash
# 查看 SELinux 状态
getenforce
# 返回: Enforcing / Permissive / Disabled

# 查看详细状态
sestatus
```

**切换模式（需要 Root）：**

```bash
# 临时切换到 Permissive 模式
setenforce 0

# 临时切换到 Enforcing 模式
setenforce 1
```

### 1.3 核心概念

| 概念 | 说明 | 示例 |
|------|------|------|
| **Subject (主体)** | 执行操作的进程 | `u:r:untrusted_app:s0` |
| **Object (客体)** | 被访问的资源 | 文件、Socket、设备 |
| **Context (上下文)** | 安全标签 | `u:object_r:app_data_file:s0` |
| **Policy (策略)** | 访问控制规则 | `allow untrusted_app app_data_file:file read;` |
| **Domain (域)** | 进程运行的安全上下文 | `untrusted_app`, `system_app` |
| **Type (类型)** | 资源的安全标签 | `app_data_file`, `system_file` |

---

## 2. Android SELinux 架构

### 2.1 架构概览

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Android SELinux 架构                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                     User Space (用户空间)                    │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │   │
│  │  │   App    │  │ System   │  │  Zygote  │  │   Init   │    │   │
│  │  │ Process  │  │ Server   │  │          │  │          │    │   │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘    │   │
│  │       │             │             │             │           │   │
│  │       ↓             ↓             ↓             ↓           │   │
│  │  ┌─────────────────────────────────────────────────────┐   │   │
│  │  │              libselinux.so (SELinux 库)              │   │   │
│  │  └─────────────────────────┬───────────────────────────┘   │   │
│  └────────────────────────────┼───────────────────────────────┘   │
│                               │                                    │
│  ┌────────────────────────────┼───────────────────────────────┐   │
│  │                     Kernel Space (内核空间)                 │   │
│  │                            ↓                                │   │
│  │  ┌─────────────────────────────────────────────────────┐   │   │
│  │  │              SELinux Security Server                 │   │   │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │   │   │
│  │  │  │   Policy    │  │   Access    │  │   Audit     │  │   │   │
│  │  │  │   Database  │  │   Vector    │  │   Log       │  │   │   │
│  │  │  │             │  │   Cache     │  │             │  │   │   │
│  │  │  └─────────────┘  └─────────────┘  └─────────────┘  │   │   │
│  │  └─────────────────────────────────────────────────────┘   │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    SELinux Policy Files                      │   │
│  │  /system/etc/selinux/    /vendor/etc/selinux/               │   │
│  │  - plat_sepolicy.cil     - vendor_sepolicy.cil              │   │
│  │  - plat_file_contexts    - vendor_file_contexts             │   │
│  │  - plat_property_contexts                                    │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 策略文件位置

```bash
# Android 8.0+ (Treble 架构)
/system/etc/selinux/          # 平台策略
/vendor/etc/selinux/          # 厂商策略
/odm/etc/selinux/             # ODM 策略

# 主要文件
plat_sepolicy.cil             # 编译后的策略
plat_file_contexts            # 文件上下文映射
plat_property_contexts        # 系统属性上下文
plat_service_contexts         # 服务上下文
plat_seapp_contexts           # 应用上下文规则
```

### 2.3 Android 进程域分类

| 域 (Domain) | 说明 | 典型进程 |
|-------------|------|----------|
| `init` | Init 进程 | `/init` |
| `kernel` | 内核线程 | `kthreadd` |
| `zygote` | Zygote 进程 | `zygote`, `zygote64` |
| `system_server` | 系统服务 | `system_server` |
| `system_app` | 系统应用 | 预装系统 App |
| `platform_app` | 平台签名应用 | 使用平台签名的 App |
| `priv_app` | 特权应用 | `/system/priv-app/` 下的 App |
| `untrusted_app` | 普通应用 | 第三方 App |
| `isolated_app` | 隔离进程 | `isolatedProcess=true` |
| `shell` | Shell 进程 | `adb shell` |
| `su` | Root 进程 | Magisk su |
| `magisk` | Magisk 域 | Magisk 守护进程 |

---

## 3. 安全上下文与标签

### 3.1 上下文格式

SELinux 安全上下文格式：

```
user:role:type:sensitivity[:categories]
```

**示例解析：**

```
u:r:untrusted_app:s0:c512,c768
│ │ │              │  └─────────── 类别 (MLS/MCS)
│ │ │              └───────────── 敏感度级别
│ │ └──────────────────────────── 类型/域
│ └────────────────────────────── 角色
└──────────────────────────────── 用户
```

### 3.2 查看上下文

```bash
# 查看进程上下文
ps -Z
# 输出示例:
# u:r:untrusted_app:s0:c512,c768  u0_a123  12345  com.example.app

# 查看文件上下文
ls -Z /data/data/com.example.app/
# 输出示例:
# u:object_r:app_data_file:s0:c512,c768  files

# 查看当前进程上下文
cat /proc/self/attr/current
# 或
id -Z

# 查看 Socket 上下文
ss -Z

# 查看系统属性上下文
getprop -Z
```

### 3.3 上下文转换

```
┌─────────────────────────────────────────────────────────────┐
│                    进程上下文转换流程                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Zygote (u:r:zygote:s0)                                   │
│         │                                                   │
│         │ fork()                                            │
│         ↓                                                   │
│   App Process (初始: u:r:zygote:s0)                        │
│         │                                                   │
│         │ setcon() 域转换                                   │
│         ↓                                                   │
│   App Process (最终: u:r:untrusted_app:s0:c512,c768)       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**seapp_contexts 规则示例：**

```
# /system/etc/selinux/plat_seapp_contexts
user=_app seinfo=platform domain=platform_app type=app_data_file
user=_app isPrivApp=true domain=priv_app type=privapp_data_file
user=_app domain=untrusted_app type=app_data_file
user=_isolated domain=isolated_app
```

---

## 4. SELinux 策略分析

### 4.1 策略规则语法

**allow 规则：**

```
allow source_type target_type:class permissions;
```

**示例：**

```
# 允许 untrusted_app 域读取 app_data_file 类型的文件
allow untrusted_app app_data_file:file { read open getattr };

# 允许 untrusted_app 连接到 app_api_service
allow untrusted_app app_api_service:service_manager find;

# 允许 untrusted_app 使用 Binder IPC
allow untrusted_app servicemanager:binder { call transfer };
```

### 4.2 其他规则类型

```
# neverallow - 禁止规则（编译时检查）
neverallow untrusted_app system_file:file write;

# dontaudit - 不记录拒绝日志
dontaudit untrusted_app self:capability sys_ptrace;

# auditallow - 允许但记录日志
auditallow untrusted_app app_data_file:file write;

# type_transition - 类型转换
type_transition untrusted_app app_data_file:file app_tmp_file;
```

### 4.3 提取和分析策略

```bash
# 从设备提取策略
adb pull /sys/fs/selinux/policy ./policy.bin

# 使用 seinfo 分析策略（需要 setools）
seinfo policy.bin

# 查看所有类型
seinfo -t policy.bin

# 查看所有域
seinfo -a domain -x policy.bin

# 使用 sesearch 搜索规则
# 搜索 untrusted_app 的所有 allow 规则
sesearch -A -s untrusted_app policy.bin

# 搜索对特定类型的访问规则
sesearch -A -t app_data_file policy.bin

# 搜索特定权限
sesearch -A -p write -t system_file policy.bin
```

### 4.4 分析 file_contexts

```bash
# 查看文件上下文映射
cat /system/etc/selinux/plat_file_contexts

# 常见映射示例
/data(/.*)?                 u:object_r:system_data_file:s0
/data/app(/.*)?             u:object_r:apk_data_file:s0
/data/data(/.*)?            u:object_r:app_data_file:s0
/data/local/tmp(/.*)?       u:object_r:shell_data_file:s0
/system(/.*)?               u:object_r:system_file:s0
/vendor(/.*)?               u:object_r:vendor_file:s0
```

---

## 5. 常用命令与工具

### 5.1 基础命令

```bash
# 查看 SELinux 状态
getenforce                    # 获取当前模式
sestatus                      # 详细状态信息

# 切换模式（需要 Root）
setenforce 0                  # Permissive
setenforce 1                  # Enforcing

# 上下文操作
id -Z                         # 当前进程上下文
ps -eZ                        # 所有进程上下文
ls -Z                         # 文件上下文

# 修改文件上下文（需要 Root）
chcon u:object_r:system_file:s0 /path/to/file
restorecon /path/to/file      # 恢复默认上下文

# 查看拒绝日志
dmesg | grep avc              # 内核日志中的 AVC 拒绝
logcat | grep avc             # logcat 中的 AVC 拒绝
```

### 5.2 分析工具

| 工具 | 用途 | 安装方式 |
|------|------|----------|
| `setools` | 策略分析工具集 | `apt install setools` |
| `seinfo` | 查看策略信息 | setools 包含 |
| `sesearch` | 搜索策略规则 | setools 包含 |
| `audit2allow` | 生成 allow 规则 | `apt install policycoreutils` |
| `sepolicy-analyze` | Android 策略分析 | AOSP 构建 |

### 5.3 AVC 拒绝日志分析

```bash
# AVC 拒绝日志格式
avc: denied { read } for pid=12345 comm="com.example.app" \
    name="secret.txt" dev="dm-0" ino=123456 \
    scontext=u:r:untrusted_app:s0:c512,c768 \
    tcontext=u:object_r:system_data_file:s0 \
    tclass=file permissive=0

# 字段说明
# denied { read }           - 被拒绝的操作
# pid=12345                 - 进程 ID
# comm="com.example.app"    - 进程名
# name="secret.txt"         - 目标文件名
# scontext=...              - 源上下文（进程）
# tcontext=...              - 目标上下文（文件）
# tclass=file               - 目标类别
# permissive=0              - 是否为 Permissive 模式
```

**使用 audit2allow 生成规则：**

```bash
# 从日志生成 allow 规则
adb shell dmesg | audit2allow -p policy.bin

# 输出示例
#============= untrusted_app ==============
allow untrusted_app system_data_file:file read;
```

---

## 6. 逆向工程中的 SELinux

### 6.1 SELinux 对逆向的影响

```
┌─────────────────────────────────────────────────────────────┐
│              SELinux 对逆向工程的限制                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐     SELinux      ┌─────────────┐          │
│  │   Frida     │ ───────────────→ │  App 进程   │          │
│  │   Server    │     ptrace       │             │          │
│  └─────────────┘     denied       └─────────────┘          │
│                                                             │
│  限制场景:                                                   │
│  1. ptrace 附加进程                                         │
│  2. 读写 /proc/pid/mem                                      │
│  3. 注入 .so 文件                                           │
│  4. 访问其他应用数据                                         │
│  5. 执行特权操作                                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 检测 SELinux 状态

**Java 层检测：**

```java
public class SELinuxChecker {

    // 方法1: 通过 System 属性
    public static String getSELinuxStatus() {
        try {
            Class<?> c = Class.forName("android.os.SystemProperties");
            Method get = c.getMethod("get", String.class, String.class);
            return (String) get.invoke(null, "ro.build.selinux", "unknown");
        } catch (Exception e) {
            return "unknown";
        }
    }

    // 方法2: 通过执行命令
    public static boolean isEnforcing() {
        try {
            Process process = Runtime.getRuntime().exec("getenforce");
            BufferedReader reader = new BufferedReader(
                new InputStreamReader(process.getInputStream()));
            String result = reader.readLine();
            return "Enforcing".equals(result);
        } catch (Exception e) {
            return true; // 默认假设是 Enforcing
        }
    }

    // 方法3: 读取 /sys/fs/selinux/enforce
    public static int getEnforceValue() {
        try {
            BufferedReader reader = new BufferedReader(
                new FileReader("/sys/fs/selinux/enforce"));
            String line = reader.readLine();
            reader.close();
            return Integer.parseInt(line.trim());
        } catch (Exception e) {
            return -1;
        }
    }
}
```

**Native 层检测：**

```c
#include <stdio.h>
#include <selinux/selinux.h>

// 获取 SELinux 模式
int get_selinux_mode() {
    // 返回值: 1 = Enforcing, 0 = Permissive, -1 = Error
    return security_getenforce();
}

// 获取当前进程上下文
char* get_current_context() {
    char *context = NULL;
    if (getcon(&context) == 0) {
        return context;
    }
    return NULL;
}

// 获取文件上下文
char* get_file_context(const char *path) {
    char *context = NULL;
    if (getfilecon(path, &context) == 0) {
        return context;
    }
    return NULL;
}

// 检查是否可以访问
int check_access(const char *scon, const char *tcon,
                 const char *tclass, const char *perm) {
    return selinux_check_access(scon, tcon, tclass, perm, NULL);
}
```

### 6.3 Frida 检测 SELinux

```javascript
// Frida 脚本: 检测 SELinux 状态
function checkSELinux() {
    console.log("[*] Checking SELinux status...");

    // 方法1: 读取 enforce 文件
    try {
        var enforce = File.readAllText("/sys/fs/selinux/enforce");
        console.log("[*] /sys/fs/selinux/enforce: " + enforce.trim());
    } catch (e) {
        console.log("[!] Cannot read enforce file: " + e);
    }

    // 方法2: 读取当前进程上下文
    try {
        var context = File.readAllText("/proc/self/attr/current");
        console.log("[*] Current context: " + context.trim());
    } catch (e) {
        console.log("[!] Cannot read context: " + e);
    }

    // 方法3: Hook getenforce
    var getenforce = Module.findExportByName("libc.so", "security_getenforce");
    if (getenforce) {
        Interceptor.attach(getenforce, {
            onLeave: function(retval) {
                console.log("[*] security_getenforce() = " + retval);
            }
        });
    }
}

// 检测 SELinux 上下文获取
function hookSELinuxContextAPIs() {
    // Hook getcon
    var getcon = Module.findExportByName("libselinux.so", "getcon");
    if (getcon) {
        Interceptor.attach(getcon, {
            onEnter: function(args) {
                this.contextPtr = args[0];
            },
            onLeave: function(retval) {
                if (retval.toInt32() === 0) {
                    var context = Memory.readPointer(this.contextPtr);
                    console.log("[*] getcon() = " + Memory.readCString(context));
                }
            }
        });
    }

    // Hook getfilecon
    var getfilecon = Module.findExportByName("libselinux.so", "getfilecon");
    if (getfilecon) {
        Interceptor.attach(getfilecon, {
            onEnter: function(args) {
                this.path = Memory.readCString(args[0]);
                this.contextPtr = args[1];
            },
            onLeave: function(retval) {
                if (retval.toInt32() >= 0) {
                    var context = Memory.readPointer(this.contextPtr);
                    console.log("[*] getfilecon(" + this.path + ") = " +
                                Memory.readCString(context));
                }
            }
        });
    }
}
```

---

## 7. SELinux 绕过技术

### 7.1 Magisk 的 SELinux 处理

Magisk 通过以下方式处理 SELinux：

```
┌─────────────────────────────────────────────────────────────┐
│                  Magisk SELinux 处理流程                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 注入自定义 SELinux 规则                                  │
│     ┌─────────────────────────────────────────────────┐    │
│     │  magiskpolicy --live                             │    │
│     │  "allow magisk * * *"                            │    │
│     │  "allow su * * *"                                │    │
│     └─────────────────────────────────────────────────┘    │
│                                                             │
│  2. 创建 magisk 和 su 域                                    │
│     ┌─────────────────────────────────────────────────┐    │
│     │  type magisk domain                              │    │
│     │  type su domain                                  │    │
│     │  permissive magisk                               │    │
│     │  permissive su                                   │    │
│     └─────────────────────────────────────────────────┘    │
│                                                             │
│  3. 上下文转换                                               │
│     App (untrusted_app) → su → magisk                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 7.2 动态修改 SELinux 策略

```bash
# 使用 magiskpolicy 修改策略
magiskpolicy --live "allow untrusted_app system_file file read"
magiskpolicy --live "allow untrusted_app app_data_file file *"

# 添加 permissive 域
magiskpolicy --live "permissive untrusted_app"

# 类型转换规则
magiskpolicy --live "type_transition untrusted_app system_file:process su"
```

### 7.3 Frida SELinux 绕过

```javascript
// 绕过 SELinux 上下文检查
function bypassSELinuxCheck() {
    // Hook security_getenforce 返回 0 (Permissive)
    var security_getenforce = Module.findExportByName("libselinux.so",
                                                       "security_getenforce");
    if (security_getenforce) {
        Interceptor.replace(security_getenforce, new NativeCallback(function() {
            return 0; // 返回 Permissive
        }, 'int', []));
        console.log("[*] Hooked security_getenforce -> always return 0");
    }

    // Hook selinux_check_access 总是返回成功
    var selinux_check_access = Module.findExportByName("libselinux.so",
                                                        "selinux_check_access");
    if (selinux_check_access) {
        Interceptor.replace(selinux_check_access, new NativeCallback(function(
            scon, tcon, tclass, perm, auditdata) {
            return 0; // 返回允许访问
        }, 'int', ['pointer', 'pointer', 'pointer', 'pointer', 'pointer']));
        console.log("[*] Hooked selinux_check_access -> always return 0");
    }
}

// 修改进程上下文检测结果
function spoofContext() {
    var getcon = Module.findExportByName("libselinux.so", "getcon");
    if (getcon) {
        Interceptor.attach(getcon, {
            onLeave: function(retval) {
                if (retval.toInt32() === 0) {
                    // 可以修改返回的上下文
                    // 注意: 这只影响检测，不影响实际权限
                }
            }
        });
    }
}
```

### 7.4 内核级绕过

```c
// 内核模块方式（需要内核源码编译）
// 修改 security/selinux/hooks.c 中的 selinux_enforcing 变量

// 或通过 /dev/kmem 直接修改内核内存（需要特殊权限）
// 这种方式在现代 Android 上通常不可行
```

---

## 8. 实战案例

### 8.1 案例: 分析应用的 SELinux 权限

```bash
# 1. 获取目标应用的进程 ID
adb shell pidof com.example.app
# 输出: 12345

# 2. 查看进程上下文
adb shell cat /proc/12345/attr/current
# 输出: u:r:untrusted_app:s0:c512,c768

# 3. 查看应用数据目录上下文
adb shell ls -Z /data/data/com.example.app/
# 输出: u:object_r:app_data_file:s0:c512,c768 files

# 4. 分析该域的权限
sesearch -A -s untrusted_app -t app_data_file policy.bin
# 输出: allow untrusted_app app_data_file:file { read write ... };

# 5. 检查是否有敏感权限
sesearch -A -s untrusted_app -t system_file policy.bin
# 输出: (通常为空或受限)
```

### 8.2 案例: Root 检测中的 SELinux 检查

```java
// 常见的 SELinux Root 检测
public class RootDetector {

    public boolean detectByContext() {
        try {
            // 检查是否存在 su 或 magisk 上下文
            Process process = Runtime.getRuntime().exec("cat /proc/self/attr/current");
            BufferedReader reader = new BufferedReader(
                new InputStreamReader(process.getInputStream()));
            String context = reader.readLine();

            // 正常应用: u:r:untrusted_app:s0
            // Root 后可能: u:r:su:s0 或 u:r:magisk:s0
            if (context.contains(":su:") || context.contains(":magisk:")) {
                return true; // 检测到 Root
            }
        } catch (Exception e) {}
        return false;
    }

    public boolean detectByEnforcing() {
        try {
            // 检查 SELinux 是否被禁用
            Process process = Runtime.getRuntime().exec("getenforce");
            BufferedReader reader = new BufferedReader(
                new InputStreamReader(process.getInputStream()));
            String status = reader.readLine();

            // Permissive 或 Disabled 通常意味着被修改
            if (!"Enforcing".equals(status)) {
                return true;
            }
        } catch (Exception e) {}
        return false;
    }
}
```

**绕过脚本：**

```javascript
// Frida 绕过 SELinux Root 检测
Java.perform(function() {
    // Hook Runtime.exec
    var Runtime = Java.use("java.lang.Runtime");
    Runtime.exec.overload('java.lang.String').implementation = function(cmd) {
        if (cmd.indexOf("getenforce") !== -1) {
            console.log("[*] Intercepted getenforce command");
            // 返回假的 Enforcing 结果
            return this.exec("echo Enforcing");
        }
        if (cmd.indexOf("/proc/self/attr/current") !== -1) {
            console.log("[*] Intercepted context read");
            // 返回正常应用上下文
            return this.exec("echo u:r:untrusted_app:s0");
        }
        return this.exec(cmd);
    };
});
```

### 8.3 案例: 调试 SELinux 拒绝问题

```bash
# 场景: Frida 注入失败，查看是否被 SELinux 阻止

# 1. 实时监控 AVC 拒绝日志
adb shell "dmesg -w | grep avc"

# 2. 尝试注入操作
frida -U com.example.app

# 3. 观察日志输出
# avc: denied { ptrace } for pid=1234 comm="frida-server" ...

# 4. 分析拒绝原因
# scontext=u:r:shell:s0 (Frida Server 运行在 shell 域)
# tcontext=u:r:untrusted_app:s0 (目标应用)
# tclass=process perm=ptrace

# 5. 解决方案
# 方案 A: 使用 Magisk 修改策略
magiskpolicy --live "allow shell untrusted_app process ptrace"

# 方案 B: 临时切换到 Permissive 模式
adb shell setenforce 0
```

---

## 总结

| 要点 | 说明 |
|------|------|
| **核心概念** | SELinux 是强制访问控制，即使 Root 也受策略限制 |
| **上下文格式** | `user:role:type:sensitivity` |
| **策略位置** | `/system/etc/selinux/`, `/vendor/etc/selinux/` |
| **分析工具** | `seinfo`, `sesearch`, `audit2allow` |
| **逆向影响** | 限制 ptrace、进程注入、文件访问等操作 |
| **绕过方式** | Magisk 策略注入、Hook SELinux API、切换 Permissive |

---

## 相关章节

- [F02: Android 四大组件](android_components.md)
- [A01: Android 沙箱实现](../Advanced/android_sandbox_implementation.md)
- [A07: Magisk 与 LSPosed 原理](../Advanced/magisk_lsposed_internals.md)
- [R15: Frida 反调试绕过](../../01-Recipes/Anti-Detection/frida_anti_debugging.md)
