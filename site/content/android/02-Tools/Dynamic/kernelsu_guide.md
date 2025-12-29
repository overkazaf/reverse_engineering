---
title: "KernelSU 使用指南"
date: 2025-12-26
type: posts
tags: ["KernelSU", "Root", "内核", "Android", "逆向分析", "动态分析"]
weight: 10
---

# KernelSU 使用指南

KernelSU 是一个基于内核的 Android Root 解决方案，通过修改内核来提供 root 权限，相比 Magisk 具有更强的隐蔽性和更底层的控制能力。

---

## 目录

1. [KernelSU 简介](#1-kernelsu-简介)
2. [KernelSU vs Magisk](#2-kernelsu-vs-magisk)
3. [安装 KernelSU](#3-安装-kernelsu)
4. [KernelSU Manager 使用](#4-kernelsu-manager-使用)
5. [模块系统](#5-模块系统)
6. [与逆向工具配合使用](#6-与逆向工具配合使用)
7. [常见问题与排查](#7-常见问题与排查)

---

## 1. KernelSU 简介

KernelSU 是一个运行在内核空间的 root 解决方案，它的核心理念是：

- **内核级 Root**: 直接在内核中实现 su，而非用户空间守护进程
- **按需授权**: 应用程序需要主动声明 root 需求，而非被动授予
- **高度隐蔽**: 对未授权应用完全透明，检测难度极大
- **GKI 兼容**: 支持 Android 12+ 的 Generic Kernel Image

### 核心特性

| 特性 | 说明 |
|------|------|
| **内核模块** | 以 LKM (Loadable Kernel Module) 形式加载 |
| **UID 0 授权** | 直接在内核层面提升进程权限 |
| **App Profile** | 细粒度的应用权限控制 |
| **模块系统** | 兼容 Magisk 模块 (systemless) |
| **OverlayFS** | 使用 overlayfs 实现系统文件修改 |

---

## 2. KernelSU vs Magisk

### 架构对比

```
┌─────────────────────────────────────────────────────────────────┐
│                         Magisk 架构                              │
├─────────────────────────────────────────────────────────────────┤
│   App 请求 root  →  magiskd (守护进程)  →  授权/拒绝            │
│                           ↓                                      │
│                    用户空间实现 su                               │
│                           ↓                                      │
│                   修改 boot.img/ramdisk                         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                       KernelSU 架构                              │
├─────────────────────────────────────────────────────────────────┤
│   App 请求 root  →  内核模块直接处理  →  授权/拒绝              │
│                           ↓                                      │
│                    内核空间实现 su                               │
│                           ↓                                      │
│               修改内核或加载内核模块                             │
└─────────────────────────────────────────────────────────────────┘
```

### 详细对比

| 特性 | KernelSU | Magisk |
|------|----------|--------|
| **实现层级** | 内核空间 | 用户空间 |
| **Root 机制** | 内核直接授权 | magiskd 守护进程 |
| **安装方式** | 刷入修改的内核 | 修改 boot.img |
| **隐蔽性** | 极高 (内核级隐藏) | 高 (DenyList) |
| **检测难度** | 非常难 | 较难 |
| **模块兼容** | 兼容大部分 Magisk 模块 | 原生支持 |
| **系统要求** | Android 12+ GKI | Android 5.0+ |
| **设备支持** | 需要对应内核 | 几乎所有设备 |

### 选择建议

- **选择 KernelSU**:
  - 需要更强的隐蔽性（银行/支付应用）
  - 设备支持 GKI 内核
  - 想要更底层的系统控制

- **选择 Magisk**:
  - 设备较旧，不支持 GKI
  - 需要更广泛的模块生态
  - 追求稳定和成熟的解决方案

---

## 3. 安装 KernelSU

### 3.1 检查设备兼容性

```bash
# 检查内核版本
adb shell uname -r
# 输出示例: 5.10.101-android13-4-00001-g123456

# 检查是否为 GKI 内核
adb shell cat /proc/version
# GKI 内核通常包含 "android" 字样

# 检查架构
adb shell getprop ro.product.cpu.abi
# 常见: arm64-v8a
```

### 3.2 安装方法

#### 方法一：官方支持的设备（推荐）

1. 访问 [KernelSU 官方发布页](https://github.com/tiann/KernelSU/releases)
2. 下载适合你设备的 boot.img
3. 使用 fastboot 刷入：

```bash
# 进入 fastboot 模式
adb reboot bootloader

# 刷入 KernelSU boot 镜像
fastboot flash boot kernelsu_boot.img

# 重启设备
fastboot reboot
```

#### 方法二：GKI 设备通用安装

```bash
# 1. 下载 AnyKernel3 格式的 KernelSU
# 从 GitHub Releases 下载 AnyKernel3-*.zip

# 2. 使用 TWRP 或其他 Recovery 刷入
adb reboot recovery
# 在 Recovery 中选择刷入 zip

# 或使用 fastboot boot 临时启动
fastboot boot twrp.img
```

#### 方法三：自行编译内核

对于没有官方支持的设备，需要自行编译带 KernelSU 补丁的内核：

```bash
# 1. 获取设备内核源码
git clone <your-device-kernel-source>

# 2. 集成 KernelSU
curl -LSs "https://raw.githubusercontent.com/tiann/KernelSU/main/kernel/setup.sh" | bash -

# 3. 编译内核
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- -j$(nproc)

# 4. 打包并刷入
```

### 3.3 安装 KernelSU Manager

```bash
# 从 GitHub 下载最新版 Manager APK
# https://github.com/tiann/KernelSU/releases

# 安装到设备
adb install KernelSU_*.apk
```

---

## 4. KernelSU Manager 使用

### 4.1 主界面

打开 KernelSU Manager 后，主界面显示：

- **状态**: 显示 KernelSU 是否正常工作
- **版本**: 内核模块版本和 Manager 版本
- **超级用户**: 管理 root 授权的应用

### 4.2 授权管理

KernelSU 采用**主动声明**模式，应用需要在 AndroidManifest.xml 中声明：

```xml
<!-- 应用声明需要 root 权限 -->
<uses-permission android:name="com.topjohnwu.magisk.permission.ROOT" />
```

或者使用 KernelSU 特有的声明方式：

```xml
<meta-data
    android:name="com.topjohnwu.superuser.REQUESTER"
    android:value="true" />
```

### 4.3 App Profile（应用配置文件）

KernelSU 的独特功能，允许为每个应用定义详细的权限：

```json
{
  "name": "frida-server",
  "uid": 0,
  "gid": 0,
  "groups": [0, 1000, 1001],
  "capabilities": ["CAP_SYS_PTRACE", "CAP_DAC_OVERRIDE"],
  "context": "u:r:su:s0",
  "namespace": {
    "mnt": true,
    "pid": false
  }
}
```

#### Profile 配置项说明

| 字段 | 说明 |
|------|------|
| `uid/gid` | 进程的用户/组 ID |
| `groups` | 附加组 ID 列表 |
| `capabilities` | Linux capabilities 列表 |
| `context` | SELinux 上下文 |
| `namespace` | 命名空间隔离设置 |

---

## 5. 模块系统

### 5.1 模块兼容性

KernelSU 兼容大部分 Magisk 模块，但有一些注意事项：

- ✅ 纯 systemless 修改模块
- ✅ 使用 OverlayFS 的模块
- ⚠️ 依赖 Magisk 特定 API 的模块可能不兼容
- ❌ 需要 Zygisk 的模块（需要额外配置）

### 5.2 安装模块

```bash
# 方法一：通过 Manager 安装
# 在 KernelSU Manager 中点击 "模块" → "从本地安装"

# 方法二：命令行安装
adb push module.zip /data/local/tmp/
adb shell su -c "ksud module install /data/local/tmp/module.zip"
```

### 5.3 Zygisk 支持

KernelSU 通过 ZygiskNext 提供 Zygisk 兼容：

```bash
# 1. 下载 ZygiskNext
# https://github.com/Dr-TSNG/ZygiskNext/releases

# 2. 作为 KernelSU 模块安装
adb push ZygiskNext-*.zip /data/local/tmp/
adb shell su -c "ksud module install /data/local/tmp/ZygiskNext-*.zip"

# 3. 重启设备
adb reboot
```

---

## 6. 与逆向工具配合使用

### 6.1 配合 Frida 使用

KernelSU 提供了优秀的 Frida 运行环境：

```bash
# 1. 下载 frida-server
# https://github.com/frida/frida/releases
# 选择 frida-server-*-android-arm64.xz

# 2. 推送到设备
adb push frida-server /data/local/tmp/
adb shell chmod 755 /data/local/tmp/frida-server

# 3. 使用 KernelSU 运行 (通过 su)
adb shell
su
/data/local/tmp/frida-server &

# 4. 验证运行
frida-ps -U
```

#### 使用 App Profile 优化 Frida

创建专门的 Frida Profile 以获得必要权限：

```bash
# 在 /data/adb/ksu/profile/ 创建配置
cat > /data/adb/ksu/profile/frida-server.json << 'EOF'
{
  "uid": 0,
  "gid": 0,
  "groups": [0, 1000, 1001, 1002, 3001, 3002, 3003],
  "capabilities": [
    "CAP_SYS_PTRACE",
    "CAP_DAC_OVERRIDE",
    "CAP_DAC_READ_SEARCH",
    "CAP_SYS_ADMIN"
  ],
  "context": "u:r:su:s0"
}
EOF
```

### 6.2 配合 LSPosed 使用

KernelSU 可以与 LSPosed 配合使用：

```bash
# 1. 安装 ZygiskNext (如果还没安装)
ksud module install ZygiskNext.zip

# 2. 安装 LSPosed Zygisk 版本
# 从 https://github.com/LSPosed/LSPosed/releases 下载
ksud module install LSPosed-*.zip

# 3. 重启设备
reboot
```

### 6.3 隐藏 Root 检测

KernelSU 天生具有很强的隐蔽性，但某些应用仍可能检测到。配合以下模块可以增强隐藏效果：

```bash
# Shamiko - 隐藏 root 和 Zygisk
ksud module install Shamiko-*.zip

# 在 KernelSU Manager 中配置:
# 1. 启用 "隐藏超级用户授权"
# 2. 将目标应用加入黑名单
```

### 6.4 配合 eBPF 使用

KernelSU 提供了良好的内核访问能力，适合 eBPF 逆向：

```bash
# 检查 eBPF 支持
adb shell su -c "ls /sys/fs/bpf"

# 运行 bpftrace (需要 root)
adb shell su -c "bpftrace -e 'tracepoint:syscalls:sys_enter_openat { printf(\"%s %s\\n\", comm, str(args->filename)); }'"
```

---

## 7. 常见问题与排查

### 7.1 安装后无法启动

```bash
# 进入 fastboot 模式
# 长按 电源 + 音量下

# 刷回原版 boot
fastboot flash boot stock_boot.img
fastboot reboot
```

### 7.2 KernelSU 状态显示异常

```bash
# 检查内核模块是否加载
adb shell su -c "lsmod | grep kernelsu"

# 检查 ksudb 进程
adb shell su -c "ps -A | grep ksu"

# 查看内核日志
adb shell su -c "dmesg | grep -i ksu"
```

### 7.3 应用无法获得 root

```bash
# 检查应用是否在授权列表
# KernelSU Manager → 超级用户 → 检查目标应用

# 检查 SELinux 状态
adb shell getenforce
# 如果是 Enforcing，某些操作可能被阻止

# 检查应用的 Profile 设置
cat /data/adb/ksu/profile/<package_name>.json
```

### 7.4 模块安装失败

```bash
# 查看模块安装日志
adb shell su -c "cat /data/adb/ksu/log/module_install.log"

# 手动安装模块进行调试
adb shell su -c "unzip -o /path/to/module.zip -d /data/adb/modules/<module_id>"
```

### 7.5 与其他 Root 方案冲突

```bash
# KernelSU 与 Magisk 不能同时使用
# 如果之前安装了 Magisk，需要先卸载

# 检查是否存在 Magisk
adb shell ls /data/adb/magisk

# 卸载 Magisk (如果存在)
# 在 Magisk Manager 中选择 "卸载" → "完全卸载"
```

---

## 相关章节

- [KernelSU 内部原理](./kernelsu_internals.md) - 深入理解 KernelSU 的技术实现
- [Magisk 与 LSPosed 原理](../../04-Reference/Advanced/magisk_lsposed_internals.md) - 对比学习 Magisk 方案
- [Frida 完整指南](./frida_guide.md) - 配合 Frida 进行动态分析
- [eBPF 使用指南](./ebpf_guide.md) - 使用 eBPF 进行内核级追踪
