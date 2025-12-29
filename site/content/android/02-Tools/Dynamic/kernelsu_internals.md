---
title: "KernelSU 内部原理"
date: 2025-12-26
type: posts
tags: ["KernelSU", "内核", "Root", "Android", "LKM", "高级"]
weight: 10
---

# KernelSU 内部原理

深入分析 KernelSU 的内核级 root 实现机制，包括内核模块架构、权限提升原理、检测规避技术等核心内容。

---

## 目录

1. [架构总览](#1-架构总览)
2. [内核模块实现](#2-内核模块实现)
3. [Root 授权机制](#3-root-授权机制)
4. [OverlayFS 模块系统](#4-overlayfs-模块系统)
5. [隐蔽性设计](#5-隐蔽性设计)
6. [与 Magisk 技术对比](#6-与-magisk-技术对比)
7. [安全性分析](#7-安全性分析)

---

## 1. 架构总览

### 1.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          KernelSU 技术架构                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        用户空间 (User Space)                          │   │
│  │                                                                       │   │
│  │   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐             │   │
│  │   │  KernelSU   │    │   Root      │    │   普通      │             │   │
│  │   │  Manager    │    │   应用      │    │   应用      │             │   │
│  │   │             │    │             │    │             │             │   │
│  │   └──────┬──────┘    └──────┬──────┘    └─────────────┘             │   │
│  │          │                  │                                        │   │
│  │          │ Binder/         │ prctl()                                │   │
│  │          │ ioctl           │ syscall                                │   │
│  │          ↓                  ↓                                        │   │
│  └──────────┼──────────────────┼────────────────────────────────────────┘   │
│             │                  │                                             │
│  ═══════════╪══════════════════╪═════════════════════════════════════════   │
│             │    System Call   │   Interface                                 │
│  ═══════════╪══════════════════╪═════════════════════════════════════════   │
│             │                  │                                             │
│  ┌──────────┼──────────────────┼────────────────────────────────────────┐   │
│  │          ↓                  ↓           内核空间 (Kernel Space)      │   │
│  │   ┌─────────────────────────────────────────────────────────────┐   │   │
│  │   │                    KernelSU 内核模块                          │   │
│  │   │                                                              │   │
│  │   │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │   │
│  │   │  │   ksu_hook   │  │  allowlist   │  │   sucompat   │       │   │
│  │   │  │              │  │              │  │              │       │   │
│  │   │  │ - syscall    │  │ - uid 管理   │  │ - su 二进制  │       │   │
│  │   │  │   hooking    │  │ - 授权检查   │  │   兼容层     │       │   │
│  │   │  │ - prctl      │  │ - profile    │  │ - Magisk     │       │   │
│  │   │  │   handler    │  │   管理       │  │   API 兼容   │       │   │
│  │   │  └──────────────┘  └──────────────┘  └──────────────┘       │   │
│  │   │                                                              │   │
│  │   │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │   │
│  │   │  │  module_fs   │  │   selinux    │  │   ksud       │       │   │
│  │   │  │              │  │   patch      │  │   daemon     │       │   │
│  │   │  │ - overlayfs  │  │              │  │              │       │   │
│  │   │  │ - mount      │  │ - 策略修改   │  │ - 模块管理   │       │   │
│  │   │  │   管理       │  │ - 权限控制   │  │ - 状态监控   │       │   │
│  │   │  └──────────────┘  └──────────────┘  └──────────────┘       │   │
│  │   │                                                              │   │
│  │   └──────────────────────────────────────────────────────────────┘   │
│  │                                                                       │   │
│  │   ┌───────────────────────────────────────────────────────────────┐   │   │
│  │   │                      Linux Kernel                              │   │
│  │   │   - task_struct 修改                                           │   │
│  │   │   - cred 结构体操作                                            │   │
│  │   │   - namespace 管理                                             │   │
│  │   └───────────────────────────────────────────────────────────────┘   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 核心组件

| 组件 | 功能 | 实现方式 |
|------|------|----------|
| **ksu_hook** | 系统调用拦截 | kprobe/ftrace |
| **allowlist** | 权限管理 | 内核数据结构 |
| **sucompat** | su 兼容层 | 进程伪装 |
| **module_fs** | 模块文件系统 | overlayfs |
| **ksud** | 用户空间守护进程 | native daemon |

---

## 2. 内核模块实现

### 2.1 模块加载机制

KernelSU 可以通过两种方式集成到内核：

#### 方式一：编译时集成

```c
// kernel/ksu/core.c
static int __init ksu_init(void)
{
    int ret;

    pr_info("KernelSU version %d\n", KSU_VERSION);

    // 初始化 allowlist
    ret = ksu_allowlist_init();
    if (ret)
        return ret;

    // 安装系统调用 hook
    ret = ksu_hook_init();
    if (ret)
        goto err_hook;

    // 初始化 SELinux 补丁
    ret = ksu_selinux_init();
    if (ret)
        goto err_selinux;

    // 启动 ksud 通信
    ret = ksu_ksud_init();
    if (ret)
        goto err_ksud;

    pr_info("KernelSU initialized successfully\n");
    return 0;

err_ksud:
    ksu_selinux_exit();
err_selinux:
    ksu_hook_exit();
err_hook:
    ksu_allowlist_exit();
    return ret;
}
core_initcall(ksu_init);
```

#### 方式二：LKM 动态加载 (GKI 2.0+)

```c
// 作为可加载内核模块
static int __init ksu_module_init(void)
{
    // 检查内核版本兼容性
    if (!ksu_check_kernel_compat())
        return -ENODEV;

    return ksu_init();
}

static void __exit ksu_module_exit(void)
{
    ksu_exit();
}

module_init(ksu_module_init);
module_exit(ksu_module_exit);
MODULE_LICENSE("GPL");
MODULE_AUTHOR("tiann");
MODULE_DESCRIPTION("KernelSU - Kernel-based root solution");
```

### 2.2 系统调用 Hook

KernelSU 使用 kprobe 或 ftrace 来 hook 关键系统调用：

```c
// hook prctl 系统调用处理 root 请求
static int ksu_handle_prctl(int option, unsigned long arg2,
                            unsigned long arg3, unsigned long arg4,
                            unsigned long arg5)
{
    // KernelSU 魔数检查
    if (option == KSU_PRCTL_MAGIC) {
        switch (arg2) {
        case CMD_GET_VERSION:
            return KSU_VERSION;

        case CMD_BECOME_ROOT:
            return ksu_become_root(current);

        case CMD_CHECK_ROOT:
            return ksu_is_allowed_uid(current_uid().val);

        case CMD_GET_ALLOW_LIST:
            return ksu_get_allowlist((void __user *)arg3, arg4);

        case CMD_SET_ALLOW_LIST:
            return ksu_set_allowlist((void __user *)arg3, arg4);
        }
    }

    return -ENOSYS;  // 传递给原始 handler
}

// 使用 kprobe 安装 hook
static struct kprobe kp_prctl = {
    .symbol_name = "__arm64_sys_prctl",
    .pre_handler = ksu_prctl_handler,
};
```

### 2.3 凭证修改 (Credential Modification)

KernelSU 通过直接修改进程的 `cred` 结构体来提升权限：

```c
// kernel/ksu/core.c
int ksu_become_root(struct task_struct *task)
{
    struct cred *new_cred;
    struct ksu_profile *profile;

    // 检查是否在允许列表
    if (!ksu_is_allowed(task))
        return -EPERM;

    // 获取应用 profile
    profile = ksu_get_profile(task);

    // 准备新的凭证
    new_cred = prepare_creds();
    if (!new_cred)
        return -ENOMEM;

    // 设置 UID/GID 为 root
    new_cred->uid = new_cred->euid = new_cred->suid = new_cred->fsuid = GLOBAL_ROOT_UID;
    new_cred->gid = new_cred->egid = new_cred->sgid = new_cred->fsgid = GLOBAL_ROOT_GID;

    // 设置 capabilities
    if (profile && profile->capabilities) {
        new_cred->cap_effective = profile->cap_effective;
        new_cred->cap_permitted = profile->cap_permitted;
        new_cred->cap_inheritable = profile->cap_inheritable;
    } else {
        // 默认给予所有 capabilities
        cap_set_full(new_cred->cap_effective);
        cap_set_full(new_cred->cap_permitted);
        cap_set_full(new_cred->cap_inheritable);
    }

    // 修改 SELinux 上下文 (如果配置了)
    if (profile && profile->selinux_context) {
        ksu_set_selinux_context(new_cred, profile->selinux_context);
    }

    // 提交凭证修改
    return commit_creds(new_cred);
}
```

### 2.4 内核数据结构

```c
// KernelSU 内部数据结构

// 允许列表条目
struct ksu_allow_entry {
    uid_t uid;                    // 应用 UID
    char package_name[256];       // 包名
    struct ksu_profile *profile;  // 应用配置
    struct list_head list;        // 链表节点
};

// 应用配置文件
struct ksu_profile {
    uid_t uid;
    gid_t gid;
    gid_t groups[32];
    int groups_count;

    kernel_cap_t cap_effective;
    kernel_cap_t cap_permitted;
    kernel_cap_t cap_inheritable;

    char selinux_context[128];

    struct {
        bool mount_namespace;
        bool pid_namespace;
        bool net_namespace;
    } namespace_flags;
};

// 全局状态
struct ksu_state {
    bool initialized;
    int version;

    spinlock_t allowlist_lock;
    struct list_head allowlist;

    struct proc_dir_entry *proc_entry;
    struct dentry *debug_root;
};
```

---

## 3. Root 授权机制

### 3.1 授权流程

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         KernelSU Root 授权流程                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   应用进程                    KernelSU 内核模块                         │
│      │                              │                                    │
│      │  1. prctl(KSU_MAGIC,        │                                    │
│      │          CMD_BECOME_ROOT)    │                                    │
│      │ ────────────────────────────>│                                    │
│      │                              │                                    │
│      │                              │  2. 获取 current task              │
│      │                              │     检查 uid/package               │
│      │                              │                                    │
│      │                              │  3. 查询 allowlist                 │
│      │                              │     ┌─────────────────────┐        │
│      │                              │     │  uid: 10086         │        │
│      │                              │     │  pkg: com.example   │        │
│      │                              │     │  profile: {...}     │        │
│      │                              │     └─────────────────────┘        │
│      │                              │                                    │
│      │                              │  4. 验证通过?                      │
│      │                              │     ├─ Yes: prepare_creds()        │
│      │                              │     │       commit_creds()         │
│      │                              │     │                              │
│      │                              │     └─ No: return -EPERM           │
│      │                              │                                    │
│      │  5. 返回结果                 │                                    │
│      │ <────────────────────────────│                                    │
│      │                              │                                    │
│      │  [成功后 uid=0, caps=full]   │                                    │
│      ▼                              ▼                                    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.2 su 兼容实现

KernelSU 提供了与传统 `su` 命令兼容的接口：

```c
// kernel/ksu/sucompat.c

// 当执行 /system/bin/su 时，内核会拦截并处理
static int ksu_su_handler(struct linux_binprm *bprm)
{
    const char *filename = bprm->filename;

    // 检查是否是 su 调用
    if (!ksu_is_su_path(filename))
        return 0;  // 不处理

    // 检查调用者权限
    if (!ksu_is_allowed(current)) {
        // 未授权，返回原始的 "su: not found" 行为
        return -ENOENT;
    }

    // 提升权限
    int ret = ksu_become_root(current);
    if (ret)
        return ret;

    // 执行请求的 shell
    const char *shell = ksu_get_shell(bprm);
    return ksu_exec_shell(shell, bprm);
}
```

### 3.3 用户空间 API

应用程序可以通过以下方式与 KernelSU 交互：

```c
// 用户空间代码示例
#include <sys/prctl.h>

#define KSU_PRCTL_MAGIC  0x4B535500  // "KSU\0"
#define CMD_GET_VERSION  0
#define CMD_BECOME_ROOT  1
#define CMD_CHECK_ROOT   2

// 检查 KernelSU 是否存在
int ksu_get_version(void) {
    return prctl(KSU_PRCTL_MAGIC, CMD_GET_VERSION, 0, 0, 0);
}

// 请求 root 权限
int ksu_become_root(void) {
    return prctl(KSU_PRCTL_MAGIC, CMD_BECOME_ROOT, 0, 0, 0);
}

// 检查是否有 root 权限
int ksu_check_root(void) {
    return prctl(KSU_PRCTL_MAGIC, CMD_CHECK_ROOT, 0, 0, 0);
}
```

---

## 4. OverlayFS 模块系统

### 4.1 模块存储结构

```
/data/adb/
├── ksu/
│   ├── bin/              # KernelSU 工具
│   │   └── ksud          # 守护进程
│   ├── profile/          # 应用配置文件
│   │   ├── com.example.json
│   │   └── ...
│   └── log/              # 日志文件
│       └── ksud.log
├── modules/              # 已安装模块
│   ├── module_id_1/
│   │   ├── module.prop
│   │   ├── system/       # 要覆盖的系统文件
│   │   └── ...
│   └── module_id_2/
└── modules_update/       # 待更新模块
```

### 4.2 OverlayFS 实现

```c
// kernel/ksu/module_fs.c

static int ksu_mount_overlayfs(const char *module_path)
{
    struct path lower, upper, work;
    struct ovl_fs_context ctx = {
        .redirect_mode = OVL_REDIRECT_ON,
        .index = true,
    };

    // 设置 lower (只读层): 原始系统分区
    kern_path("/system", LOOKUP_DIRECTORY, &lower);

    // 设置 upper (读写层): 模块修改
    char upper_path[PATH_MAX];
    snprintf(upper_path, sizeof(upper_path), "%s/system", module_path);
    kern_path(upper_path, LOOKUP_DIRECTORY, &upper);

    // 设置 work 目录
    char work_path[PATH_MAX];
    snprintf(work_path, sizeof(work_path), "%s/.work", module_path);
    kern_path(work_path, LOOKUP_DIRECTORY, &work);

    // 挂载 overlayfs
    return ovl_mount(&ctx, "/system", &lower, &upper, &work);
}

// 模块加载流程
int ksu_load_modules(void)
{
    struct dir_context ctx;
    struct file *modules_dir;

    modules_dir = filp_open("/data/adb/modules", O_RDONLY | O_DIRECTORY, 0);
    if (IS_ERR(modules_dir))
        return PTR_ERR(modules_dir);

    // 遍历模块目录
    iterate_dir(modules_dir, &ctx);

    // 对每个模块应用 overlayfs
    list_for_each_entry(module, &ksu_modules, list) {
        if (module->enabled) {
            ksu_mount_overlayfs(module->path);
        }
    }

    filp_close(modules_dir, NULL);
    return 0;
}
```

### 4.3 Magisk 模块兼容

KernelSU 实现了对 Magisk 模块格式的兼容：

```c
// 解析 module.prop
static int ksu_parse_module_prop(const char *path, struct ksu_module *module)
{
    char buf[4096];
    struct file *f;

    f = filp_open(path, O_RDONLY, 0);
    if (IS_ERR(f))
        return PTR_ERR(f);

    kernel_read(f, buf, sizeof(buf), &f->f_pos);
    filp_close(f, NULL);

    // 解析字段
    ksu_parse_prop_field(buf, "id", module->id, sizeof(module->id));
    ksu_parse_prop_field(buf, "name", module->name, sizeof(module->name));
    ksu_parse_prop_field(buf, "version", module->version, sizeof(module->version));
    ksu_parse_prop_field(buf, "author", module->author, sizeof(module->author));

    return 0;
}
```

---

## 5. 隐蔽性设计

### 5.1 内核级隐藏优势

KernelSU 相比 Magisk 具有天然的隐蔽性优势：

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            检测点对比                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   检测方法              Magisk              KernelSU                     │
│   ─────────────────────────────────────────────────────────────────     │
│                                                                          │
│   /system/bin/su        存在伪装文件        不存在 (内核直接处理)        │
│   magiskd 进程          存在                不存在                       │
│   /data/adb/magisk      存在                不存在                       │
│   boot.img 修改         ramdisk 修改        内核修改                     │
│   属性检测              ro.boot.vbmeta.*   无明显特征                    │
│   SELinux 上下文        需要额外处理        内核直接设置                  │
│   挂载点检测            存在 magisk 挂载    仅 overlayfs                  │
│   内存特征              用户空间可检测      难以从用户空间检测            │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.2 隐藏策略实现

```c
// kernel/ksu/hide.c

// 对未授权进程隐藏 KernelSU 存在
static bool ksu_should_hide(struct task_struct *task)
{
    // 1. 系统应用始终隐藏
    if (ksu_is_system_uid(task_uid(task).val))
        return true;

    // 2. 黑名单应用隐藏
    if (ksu_is_blacklisted(task))
        return true;

    // 3. 非授权应用隐藏
    if (!ksu_is_allowed(task))
        return true;

    return false;
}

// Hook open 系统调用，隐藏敏感文件
static int ksu_hide_open(struct file *file, const char __user *filename)
{
    char path[PATH_MAX];

    if (ksu_should_hide(current)) {
        if (strncpy_from_user(path, filename, PATH_MAX) > 0) {
            // 隐藏 /data/adb/ksu 目录
            if (strstr(path, "/data/adb/ksu"))
                return -ENOENT;

            // 隐藏 /proc/ksu 接口
            if (strstr(path, "/proc/ksu"))
                return -ENOENT;
        }
    }

    return 0;  // 允许正常访问
}

// Hook stat 系统调用
static int ksu_hide_stat(const char __user *filename, struct stat *statbuf)
{
    if (ksu_should_hide(current)) {
        // 对敏感路径返回 ENOENT
        if (ksu_is_sensitive_path(filename))
            return -ENOENT;
    }
    return 0;
}
```

### 5.3 进程隐藏

```c
// 从 /proc 隐藏 ksud 进程
static int ksu_hide_proc_pid(struct task_struct *task, struct task_struct *target)
{
    // 对黑名单应用隐藏 ksud
    if (ksu_should_hide(task)) {
        if (strcmp(target->comm, "ksud") == 0)
            return -ENOENT;
    }
    return 0;
}

// Hook proc_pid_readdir
static int ksu_proc_readdir_hook(struct file *file, struct dir_context *ctx)
{
    // 过滤掉 ksud 的 PID
    // ...
}
```

---

## 6. 与 Magisk 技术对比

### 6.1 Root 实现对比

| 方面 | KernelSU | Magisk |
|------|----------|--------|
| **su 实现位置** | 内核空间 | 用户空间 (magiskd) |
| **权限提升** | 直接修改 cred | IPC 请求 magiskd |
| **进程数量** | 无额外守护进程 | magiskd 常驻 |
| **系统调用** | hook prctl | 正常 execve su |

### 6.2 代码对比

**Magisk su 请求流程**:
```c
// 用户空间: su 进程
int main(int argc, char **argv) {
    // 连接到 magiskd
    int fd = connect_magiskd();

    // 发送 root 请求
    write(fd, &request, sizeof(request));

    // 等待授权结果
    read(fd, &response, sizeof(response));

    if (response.granted) {
        // magiskd 会 fork 一个 root shell
        // 通过 PTY 转发
    }
}
```

**KernelSU su 请求流程**:
```c
// 用户空间: 直接 syscall
int become_root(void) {
    // 一次 prctl 调用，内核直接处理
    return prctl(KSU_MAGIC, CMD_BECOME_ROOT, 0, 0, 0);
    // 返回后当前进程已经是 root
}
```

### 6.3 检测难度对比

```c
// Magisk 检测方法 (相对容易)
bool detect_magisk() {
    // 检查文件
    if (access("/data/adb/magisk", F_OK) == 0) return true;
    if (access("/sbin/su", F_OK) == 0) return true;

    // 检查进程
    if (find_process("magiskd")) return true;

    // 检查属性
    char value[PROP_VALUE_MAX];
    if (__system_property_get("ro.boot.vbmeta.device_state", value) > 0) {
        if (strcmp(value, "unlocked") == 0) return true;
    }

    return false;
}

// KernelSU 检测方法 (非常困难)
bool detect_kernelsu() {
    // 尝试 prctl 探测 (KernelSU 可以针对性隐藏)
    int ret = prctl(0x4B535500, 0, 0, 0, 0);
    if (ret > 0) return true;  // 但 KernelSU 可以对黑名单应用返回 -1

    // 检查内核模块 (需要 root 权限)
    // 用户空间几乎无法检测

    return false;
}
```

---

## 7. 安全性分析

### 7.1 攻击面

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        KernelSU 攻击面分析                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   攻击向量                 风险等级          缓解措施                    │
│   ─────────────────────────────────────────────────────────────────     │
│                                                                          │
│   prctl 接口滥用          中                仅授权应用可调用             │
│   allowlist 篡改          高                内核空间存储，SELinux 保护   │
│   内核模块漏洞            高                代码审计，安全开发           │
│   提权漏洞利用            中                capability 最小化            │
│   Profile 注入            中                签名验证                     │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 7.2 安全设计

```c
// 安全检查示例

// 1. 调用者验证
static bool ksu_verify_caller(struct task_struct *task)
{
    // 检查 UID 是否在允许列表
    if (!ksu_is_allowed_uid(task_uid(task).val))
        return false;

    // 检查包签名 (通过 ksud 验证)
    if (!ksu_verify_package_signature(task))
        return false;

    // 检查 SELinux 上下文
    if (!ksu_check_selinux_context(task))
        return false;

    return true;
}

// 2. Capability 限制
static int ksu_apply_profile_caps(struct cred *cred, struct ksu_profile *profile)
{
    // 只授予 profile 中声明的 capabilities
    // 而不是默认给全部
    if (profile->capabilities) {
        cred->cap_effective = profile->cap_effective;
        cred->cap_permitted = profile->cap_permitted;
    }
    return 0;
}

// 3. 命名空间隔离
static int ksu_setup_namespace(struct ksu_profile *profile)
{
    if (profile->namespace_flags.mount_namespace)
        unshare(CLONE_NEWNS);

    if (profile->namespace_flags.pid_namespace)
        unshare(CLONE_NEWPID);

    return 0;
}
```

### 7.3 与 SELinux 集成

```c
// SELinux 策略修改
static int ksu_patch_selinux_policy(void)
{
    // 添加 KernelSU 相关的 SELinux 规则
    // 允许授权进程执行特定操作

    const char *rules[] = {
        "allow ksu_client ksu_server:binder { call transfer }",
        "allow ksu_client shell_data_file:file { read write }",
        "allow ksu_client su:process { transition }",
        NULL
    };

    for (int i = 0; rules[i]; i++) {
        ksu_add_selinux_rule(rules[i]);
    }

    return 0;
}
```

---

## 相关章节

- [KernelSU 使用指南](./kernelsu_guide.md) - 安装配置和基本使用
- [Magisk 与 LSPosed 原理](../../04-Reference/Advanced/magisk_lsposed_internals.md) - 对比学习
- [eBPF 内部原理](./ebpf_internals.md) - 另一种内核技术
- [Android 沙箱实现](../../04-Reference/Advanced/android_sandbox_implementation.md) - Android 安全机制
