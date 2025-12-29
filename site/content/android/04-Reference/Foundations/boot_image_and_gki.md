---
title: "Boot Image、Ramdisk 与 GKI 详解"
date: 2025-12-26
type: posts
tags: ["Boot", "Ramdisk", "GKI", "内核", "Android", "系统"]
weight: 10
---

# Boot Image、Ramdisk 与 GKI 详解

深入理解 Android 启动镜像的结构、ramdisk 的作用以及 GKI (Generic Kernel Image) 架构，这些知识是理解 Root 方案（如 Magisk、KernelSU）工作原理的基础。

---

## 目录

1. [Android 启动流程概述](#1-android-启动流程概述)
2. [Boot Image 结构](#2-boot-image-结构)
3. [Ramdisk 详解](#3-ramdisk-详解)
4. [GKI (Generic Kernel Image)](#4-gki-generic-kernel-image)
5. [分区与镜像类型](#5-分区与镜像类型)
6. [Root 方案与启动镜像](#6-root-方案与启动镜像)
7. [实用工具与操作](#7-实用工具与操作)

---

## 1. Android 启动流程概述

### 1.1 启动阶段

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Android 启动流程                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐            │
│   │   ROM    │    │  Boot-   │    │  Kernel  │    │   Init   │            │
│   │  (固件)  │───►│  loader  │───►│  启动    │───►│  进程    │            │
│   └──────────┘    └──────────┘    └──────────┘    └──────────┘            │
│        │              │               │               │                    │
│        │              │               │               │                    │
│        ▼              ▼               ▼               ▼                    │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐            │
│   │ 硬件初始 │    │ 加载     │    │ 挂载     │    │ 启动     │            │
│   │ 化       │    │ boot.img │    │ ramdisk  │    │ Zygote   │            │
│   └──────────┘    └──────────┘    └──────────┘    └──────────┘            │
│                                                         │                  │
│                                                         ▼                  │
│                                                    ┌──────────┐            │
│                                                    │ System   │            │
│                                                    │ Server   │            │
│                                                    └──────────┘            │
│                                                         │                  │
│                                                         ▼                  │
│                                                    ┌──────────┐            │
│                                                    │  Launcher│            │
│                                                    │  (桌面)  │            │
│                                                    └──────────┘            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 各阶段说明

| 阶段 | 说明 | 关键文件 |
|------|------|----------|
| **BootROM** | 固化在芯片中的代码，初始化硬件 | - |
| **Bootloader** | 引导加载程序，加载内核 | aboot, ABL |
| **Kernel** | Linux 内核启动 | zImage, Image |
| **Ramdisk** | 临时根文件系统 | ramdisk.cpio |
| **Init** | 第一个用户空间进程 | /init |
| **Zygote** | Android 进程孵化器 | app_process |

---

## 2. Boot Image 结构

### 2.1 Boot Image 组成

Boot Image (boot.img) 是 Android 设备启动的核心镜像：

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          boot.img 结构                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   偏移量        大小          内容                                           │
│   ─────────────────────────────────────────────────────────────────────     │
│   0x0000       2KB           Boot Header (启动头)                           │
│                              - magic: "ANDROID!"                            │
│                              - kernel_size                                  │
│                              - ramdisk_size                                 │
│                              - cmdline                                      │
│                              - ...                                          │
│   ─────────────────────────────────────────────────────────────────────     │
│   对齐后       kernel_size   Kernel (内核镜像)                              │
│                              - 压缩的 Linux 内核                            │
│                              - 通常为 gzip 压缩                             │
│   ─────────────────────────────────────────────────────────────────────     │
│   对齐后       ramdisk_size  Ramdisk (初始内存盘)                           │
│                              - CPIO 格式的文件系统                          │
│                              - gzip 压缩                                    │
│   ─────────────────────────────────────────────────────────────────────     │
│   对齐后       second_size   Second Stage (可选)                            │
│                              - 第二阶段引导程序                             │
│   ─────────────────────────────────────────────────────────────────────     │
│   对齐后       dtb_size      DTB (设备树, v2+)                              │
│                              - Device Tree Blob                             │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Boot Header 版本

Android 不同版本使用不同的 boot header 格式：

| 版本 | Android 版本 | 特点 |
|------|-------------|------|
| **v0-v2** | Android 9 及更早 | 传统格式 |
| **v3** | Android 11 | 引入 vendor_boot |
| **v4** | Android 12+ | 支持 vendor_ramdisk |

### 2.3 Boot Header v3/v4 结构

```c
// Android 12+ boot header v4
struct boot_img_hdr_v4 {
    uint8_t magic[BOOT_MAGIC_SIZE];      // "ANDROID!"
    uint32_t kernel_size;                 // 内核大小
    uint32_t ramdisk_size;               // ramdisk 大小
    uint32_t os_version;                 // 系统版本
    uint32_t header_size;                // header 大小
    uint32_t reserved[4];                // 保留字段
    uint32_t header_version;             // header 版本 (4)
    uint8_t cmdline[BOOT_ARGS_SIZE];     // 内核命令行
    uint32_t signature_size;             // 签名大小 (v4 新增)
};
```

---

## 3. Ramdisk 详解

### 3.1 什么是 Ramdisk

Ramdisk 是一个**临时的内存文件系统**，在内核启动早期加载到内存中：

- **格式**: CPIO 归档，通常使用 gzip 压缩
- **作用**: 提供启动初期所需的文件和程序
- **生命周期**: 系统启动后可能被卸载或保留

### 3.2 Ramdisk 内容

```
ramdisk/
├── init                          # 第一个用户空间进程
├── init.rc                       # init 配置脚本
├── init.*.rc                     # 设备特定配置
├── default.prop                  # 默认属性
├── fstab.*                       # 文件系统挂载表
├── ueventd.rc                    # 设备节点配置
├── sbin/                         # 系统二进制文件
│   ├── adbd                      # ADB 守护进程
│   └── ...
├── system/                       # 指向 /system 的挂载点
├── vendor/                       # 指向 /vendor 的挂载点
├── dev/                          # 设备文件
├── proc/                         # 进程文件系统
└── sys/                          # sysfs 文件系统
```

### 3.3 First Stage Init vs Second Stage Init

Android 使用两阶段 init：

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Init 两阶段启动                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌───────────────────────────────────────────────────────────────────┐    │
│   │                    First Stage Init                                │    │
│   │                                                                    │    │
│   │   来源: boot.img 中的 ramdisk                                      │    │
│   │   任务:                                                            │    │
│   │     1. 设置基本环境 (/dev, /proc, /sys)                           │    │
│   │     2. 加载 SELinux 策略                                          │    │
│   │     3. 挂载 /system, /vendor 等分区                               │    │
│   │     4. 切换到 Second Stage Init                                   │    │
│   │                                                                    │    │
│   └────────────────────────────┬──────────────────────────────────────┘    │
│                                │                                            │
│                                ▼                                            │
│   ┌───────────────────────────────────────────────────────────────────┐    │
│   │                   Second Stage Init                                │    │
│   │                                                                    │    │
│   │   来源: /system/bin/init                                           │    │
│   │   任务:                                                            │    │
│   │     1. 解析 init.rc 脚本                                          │    │
│   │     2. 启动各类服务 (servicemanager, surfaceflinger...)           │    │
│   │     3. 启动 Zygote                                                │    │
│   │     4. 属性服务                                                   │    │
│   │                                                                    │    │
│   └───────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.4 不同类型的 Ramdisk

Android 11+ 引入了多种 ramdisk：

| 类型 | 位置 | 内容 | 用途 |
|------|------|------|------|
| **Generic Ramdisk** | boot.img | 通用 init 文件 | First stage init |
| **Vendor Ramdisk** | vendor_boot.img | 厂商特定文件 | 硬件初始化 |
| **Recovery Ramdisk** | recovery.img | Recovery 环境 | 系统恢复 |

---

## 4. GKI (Generic Kernel Image)

### 4.1 GKI 概述

GKI 是 Google 在 Android 11 引入的**通用内核镜像**架构：

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      传统架构 vs GKI 架构                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   传统架构 (Android 10 及更早)                                               │
│   ─────────────────────────────────────────                                 │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                     boot.img (设备特定)                              │  │
│   │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │  │
│   │  │    Kernel        │  │    Ramdisk       │  │      DTB         │  │  │
│   │  │  (设备特定)      │  │   (设备特定)     │  │   (设备特定)     │  │  │
│   │  │                  │  │                  │  │                  │  │  │
│   │  │  - 厂商驱动      │  │  - init          │  │  - 设备树       │  │  │
│   │  │  - 定制修改      │  │  - 配置文件      │  │                  │  │  │
│   │  └──────────────────┘  └──────────────────┘  └──────────────────┘  │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│                                                                              │
│   GKI 架构 (Android 11+)                                                    │
│   ─────────────────────────────────────────                                 │
│                                                                              │
│   ┌──────────────────────────────────┐  ┌──────────────────────────────┐  │
│   │        boot.img (通用)           │  │     vendor_boot.img          │  │
│   │  ┌──────────────────────────┐   │  │  ┌──────────────────────┐   │  │
│   │  │    GKI Kernel            │   │  │  │  Vendor Ramdisk      │   │  │
│   │  │    (Google 提供)         │   │  │  │  (厂商提供)          │   │  │
│   │  │                          │   │  │  │                      │   │  │
│   │  │  - 标准化接口            │   │  │  │  - 硬件初始化        │   │  │
│   │  │  - 稳定 ABI              │   │  │  │  - 厂商配置          │   │  │
│   │  └──────────────────────────┘   │  │  └──────────────────────┘   │  │
│   │  ┌──────────────────────────┐   │  │  ┌──────────────────────┐   │  │
│   │  │    Generic Ramdisk       │   │  │  │        DTB           │   │  │
│   │  │    (Google 提供)         │   │  │  │   (厂商提供)         │   │  │
│   │  └──────────────────────────┘   │  │  └──────────────────────┘   │  │
│   └──────────────────────────────────┘  └──────────────────────────────┘  │
│                                                                              │
│   ┌──────────────────────────────────────────────────────────────────────┐ │
│   │                       vendor_dlkm (动态加载内核模块)                  │ │
│   │    厂商驱动以 LKM 形式加载，不修改 GKI 内核                          │ │
│   └──────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 GKI 版本

| GKI 版本 | Android 版本 | 内核版本 | 特点 |
|----------|-------------|----------|------|
| GKI 1.0 | Android 11 | 5.4 | 初始版本 |
| GKI 2.0 | Android 12 | 5.10 | 完整模块化 |
| GKI 2.0 | Android 13 | 5.15 | 增强稳定性 |
| GKI 2.0 | Android 14 | 6.1 | 最新内核支持 |

### 4.3 GKI 的优势

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           GKI 优势                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   1. 更快的安全更新                                                          │
│      - Google 可以直接推送内核安全补丁                                       │
│      - 无需等待厂商适配                                                      │
│                                                                              │
│   2. 标准化接口 (KMI - Kernel Module Interface)                             │
│      - 厂商驱动与内核解耦                                                    │
│      - 驱动以模块形式加载                                                    │
│                                                                              │
│   3. 更小的 boot.img                                                        │
│      - 厂商特定内容移至 vendor_boot                                          │
│      - 便于 OTA 更新                                                        │
│                                                                              │
│   4. 利于 Root 方案                                                         │
│      - KernelSU 可以作为 LKM 加载                                           │
│      - 无需编译完整内核                                                      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.4 检查设备是否使用 GKI

```bash
# 检查内核版本
adb shell uname -r
# GKI 内核通常显示: 5.10.x-android13-x-xxxxx

# 检查是否存在 vendor_boot 分区
adb shell ls -la /dev/block/by-name/ | grep vendor_boot

# 检查内核配置
adb shell zcat /proc/config.gz | grep CONFIG_GKI
```

---

## 5. 分区与镜像类型

### 5.1 启动相关分区

| 分区 | 用途 | 备注 |
|------|------|------|
| **boot** | 内核 + 通用 ramdisk | 必需 |
| **vendor_boot** | 厂商 ramdisk + DTB | GKI 设备 |
| **init_boot** | 通用 ramdisk | Android 13+ |
| **recovery** | Recovery 环境 | 部分设备 |
| **dtbo** | 设备树覆盖 | 独立分区 |

### 5.2 Android 13+ 分区变化

```
Android 12:
boot.img = kernel + generic_ramdisk

Android 13+:
boot.img = kernel only
init_boot.img = generic_ramdisk
```

### 5.3 A/B 分区

现代 Android 设备使用 A/B 分区方案：

```
boot_a    boot_b
vendor_boot_a    vendor_boot_b
system_a    system_b
...
```

查看当前槽位：
```bash
adb shell getprop ro.boot.slot_suffix
# 输出: _a 或 _b
```

---

## 6. Root 方案与启动镜像

### 6.1 Magisk 修改方式

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Magisk 修改 Boot Image                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   原始 boot.img                    修改后 boot.img                          │
│   ─────────────────               ─────────────────                         │
│                                                                              │
│   ┌─────────────────┐             ┌─────────────────┐                       │
│   │    Kernel       │             │    Kernel       │  (保持不变)           │
│   └─────────────────┘             └─────────────────┘                       │
│   ┌─────────────────┐             ┌─────────────────┐                       │
│   │    Ramdisk      │    ───►     │ Magisk Ramdisk  │                       │
│   │                 │             │                 │                       │
│   │  - init         │             │  - magiskinit   │  ← 替换 init          │
│   │  - init.rc      │             │  - init.rc      │                       │
│   │  - ...          │             │  - overlay.d/   │  ← Magisk 覆盖        │
│   │                 │             │  - ...          │                       │
│   └─────────────────┘             └─────────────────┘                       │
│                                                                              │
│   Magisk 注入流程:                                                          │
│   1. magiskinit 作为 init 启动                                              │
│   2. 执行 Magisk 初始化                                                     │
│   3. 挂载 Magisk 文件系统                                                   │
│   4. 启动 magiskd 守护进程                                                  │
│   5. 调用原始 init 继续启动                                                 │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 KernelSU 修改方式

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       KernelSU 修改 Boot Image                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   方式一: 修改内核 (编译时集成)                                              │
│   ─────────────────────────────────                                         │
│                                                                              │
│   ┌─────────────────┐             ┌─────────────────┐                       │
│   │  原始 Kernel    │    ───►     │ KernelSU Kernel │  ← 编译时集成         │
│   └─────────────────┘             └─────────────────┘                       │
│   ┌─────────────────┐             ┌─────────────────┐                       │
│   │    Ramdisk      │             │    Ramdisk      │  (保持不变)           │
│   └─────────────────┘             └─────────────────┘                       │
│                                                                              │
│                                                                              │
│   方式二: LKM 加载 (GKI 设备)                                               │
│   ─────────────────────────────────                                         │
│                                                                              │
│   ┌─────────────────┐             ┌─────────────────┐                       │
│   │  GKI Kernel     │             │  GKI Kernel     │  (保持不变)           │
│   └─────────────────┘             └─────────────────┘                       │
│   ┌─────────────────┐             ┌─────────────────┐                       │
│   │    Ramdisk      │    ───►     │    Ramdisk      │                       │
│   │                 │             │  + kernelsu.ko  │  ← 添加内核模块       │
│   │                 │             │  + 加载脚本     │                       │
│   └─────────────────┘             └─────────────────┘                       │
│                                                                              │
│   启动时加载 kernelsu.ko 模块，无需修改内核本身                             │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. 实用工具与操作

### 7.1 提取 Boot Image

```bash
# 方法一: 从设备提取
adb shell su -c "dd if=/dev/block/by-name/boot of=/sdcard/boot.img"
adb pull /sdcard/boot.img

# 方法二: 从 OTA 包提取
unzip ota.zip boot.img
# 或使用 payload-dumper
python payload_dumper.py payload.bin --out ./extracted/
```

### 7.2 解包 Boot Image

使用 **magiskboot** (推荐):

```bash
# 解包
./magiskboot unpack boot.img

# 生成的文件:
# - kernel          内核
# - ramdisk.cpio    ramdisk (压缩的)
# - dtb             设备树 (如果有)

# 解包 ramdisk
./magiskboot cpio ramdisk.cpio extract
```

使用 **AIK (Android Image Kitchen)**:

```bash
./unpackimg.sh boot.img
# 输出到 split_img/ 和 ramdisk/
```

使用 **mkbootimg 工具链**:

```bash
# 解包
unpack_bootimg --boot_img boot.img --out boot_unpacked/

# 查看 boot.img 信息
unpack_bootimg --boot_img boot.img --format mkbootimg
```

### 7.3 打包 Boot Image

```bash
# 使用 magiskboot
./magiskboot repack boot.img new_boot.img

# 使用 mkbootimg
mkbootimg \
    --kernel kernel \
    --ramdisk ramdisk.cpio.gz \
    --cmdline "..." \
    --os_version 13.0.0 \
    --os_patch_level 2024-01 \
    --header_version 4 \
    -o new_boot.img
```

### 7.4 刷入 Boot Image

```bash
# 进入 fastboot 模式
adb reboot bootloader

# 刷入 boot 分区
fastboot flash boot new_boot.img

# 对于 A/B 设备，可能需要指定槽位
fastboot flash boot_a new_boot.img

# 重启
fastboot reboot
```

### 7.5 修改 Ramdisk

```bash
# 1. 解包 ramdisk
mkdir ramdisk_dir
cd ramdisk_dir
gzip -dc ../ramdisk.cpio.gz | cpio -idmv

# 2. 修改文件
# 例如修改 init.rc, default.prop 等

# 3. 重新打包
find . | cpio -o -H newc | gzip > ../ramdisk.cpio.gz
```

### 7.6 验证 Boot Image

```bash
# 使用 avbtool 验证签名 (如果使用 AVB)
avbtool verify_image --image boot.img

# 查看 vbmeta 信息
avbtool info_image --image vbmeta.img
```

---

## 相关章节

- [KernelSU 使用指南](../../02-Tools/Dynamic/kernelsu_guide.md) - 基于内核的 Root 方案
- [KernelSU 内部原理](../../02-Tools/Dynamic/kernelsu_internals.md) - 内核模块实现
- [Magisk 与 LSPosed 原理](../Advanced/magisk_lsposed_internals.md) - 传统 Root 方案
- [AOSP 与系统定制](../Advanced/aosp_and_system_customization.md) - 系统级修改
