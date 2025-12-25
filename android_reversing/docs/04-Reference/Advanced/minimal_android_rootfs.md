# 构建最小化 Android 系统 (RootFS) 指南

构建一个完整的 AOSP (Android Open Source Project) 耗时巨大且对硬件要求苛刻。而构建一个最小化的 Android RootFS (Root File System) 是一个能让我们深刻理解 Android 启动流程和核心组件的绝佳实践。其目标是创建一个仅包含最基本组件、能够引导 Linux 内核并最终启动一个交互式 Shell 的系统。

## 本文将指导你完成这一过程，主要使用 QEMU 作为目标平台。

## 目录

- [构建最小化 android 系统 (RootFS) 指南](#构建最小化-android-系统-rootfs-指南)
  - [本文将指导你完成这一过程，主要使用 QEMU 作为目标平台。](#本文将指导你完成这一过程主要使用-qemu-作为目标平台)
  - [目录](#目录)
  - [核心概念与启动流程](#核心概念与启动流程)
  - [最小系统的核心组件](#最小系统的核心组件)
  - [构建步骤详解](#构建步骤详解)
    - [Step 1: 准备环境与工具链](#step-1-准备环境与工具链)
    - [Step 2: 获取并编译 Linux 内核](#step-2-获取并编译-linux-内核)
    - [Step 3: 构建最小化 RootFS](#step-3-构建最小化-rootfs)
    - [Step 4: 打包并运行](#step-4-打包并运行)
  - [从 Shell 到 Zygote：下一步是什么？](#从-shell-到-zygote下一步是什么)

---

## 核心概念与启动流程

1. **Bootloader**: 设备上电后执行的第一段代码，负责初始化硬件并加载 Linux 内核到内存。
2. **Kernel**: 内核被加载后，开始初始化各种驱动、内存管理等，然后挂载一个临时的根文件系统 (ramdisk)。
3. **`init` 进程**: 内核在用户空间启动的第一个进程，其 PID 为 1。它是所有其他用户空间进程的祖先。
4. **`init.rc`**: `init` 进程会解析这个配置文件，根据其中的指令执行动作，如挂载文件系统、设置系统属性、启动服务等。

我们的目标就是创建一个极简的 RootFS，其中包含 `init` 程序和一个能被它启动的 Shell。

## 最小系统的核心组件

一个能启动到 Shell 的最小 Android 系统，必须包含以下组件：

- **Linux Kernel**: 操作系统的核心。

- **`init`**: 用户空间的守护神，来自 AOSP 源码 `system/core/init`。

- **C 库**: `libc.so` (C 标准库), `libm.so` (数学库)。所有原生程序都依赖它。

- **动态链接器**: `linker` 或 `linker64`，用于加载 `.so` 动态库。

- **Shell**: `sh`，我们的交互界面，通常由 `toybox` 或 `toolbox` 提供。

- **`init.rc`**: 一个最简单的配置文件。

- **基本目录结构**: `/dev`, `/proc`, `/sys`, `/system/bin`。

---

## 构建步骤详解

### Step 1: 准备环境与工具链

你需要一个 Linux 环境（如 Ubuntu）和用于交叉编译的工具链。最简单的方法是从 AOSP 预编译库中获取。

```bash
# Download AOSP prebuilt aarch64 (ARM64) Toolchain
git clone https://android.googlesource.com/platform/prebuilts/gcc/linux-x86/aarch64/aarch64-linux-android-4.9

# Add Toolchain Path to Environment variables
export PATH=$(pwd)/aarch64-linux-android-4.9/bin:$PATH
export CROSS_COMPILE=aarch64-linux-android-
```

### Step 2: 获取并编译 Linux 内核

```bash
git clone https://android.googlesource.com/kernel/common.git
cd common

# Switch to a Stable branch
git checkout android-xxxx

# 配置内核
export ARCH=arm64
make defconfig

# 编译内核
make -j$(nproc)

# Compile Success. After this, Image.gz will be generated in arch/arm64/boot/ directory
```

### Step 3: 构建最小化 RootFS

```bash
mkdir -p my_rootfs/{dev,proc,sys,system/bin,system/lib64}
cd my_rootfs
```

这一步比较复杂，因为需要从完整的 AOSP 源码中单独编译。一个简化的方法是**直接从一个现有的 Android 系统或 AOSP 编译产物中提取这些预编译好的二进制文件**。

- 从 AOSP 编译产物 `out/target/product/<device>/system/` 中找到以下文件：

  - `bin/linker64` -> 复制到 `my_rootfs/system/bin/`
  - `bin/init` -> 复制到 `my_rootfs/`
  - `bin/toybox` -> 复制到 `my_rootfs/system/bin/`
  - `lib64/libc.so`, `lib64/libm.so` -> 复制到 `my_rootfs/system/lib64/`

- 为 `toybox` 创建各种命令的软链接：

```bash
cd my_rootfs/system/bin
for cmd in $(./toybox); do
  ln -s toybox $cmd
done
cd ../../
```

在 `my_rootfs/` 目录下创建一个 `init.rc` 文件，内容如下：

```rc
# init.rc for minimal android

on early-init
    mount tmpfs tmpfs /dev
    mkdir /dev/pts
    mount devpts devpts /dev/pts
    mount proc proc /proc
    mount sysfs sysfs /sys

on init
    export PATH /system/bin
    export LD_LIBRARY_PATH /system/lib64

on post-fs
    # In a real system, we would mount /data, /cache, etc.
    # Here we just start the shell.

service shell /system/bin/sh
    class core
    console
    disabled
    user shell
    group shell
    seclabel u:r:shell:s0

on property:sys.boot_completed=1
    start shell
```

### Step 4: 打包并运行

1. **打包 RootFS**: 我们需要将 `my_rootfs` 目录打包成一个 `cpio` 归档，并用 `gzip` 压缩，作为内核的 `initramfs`。
    ```bash
    cd my_rootfs
    find . | cpio -o -H newc | gzip > ../rootfs.cpio.gz
    cd ..
    ```
2. **运行 QEMU**: 确保 `common/arch/arm64/boot/Image.gz` 和 `rootfs.cpio.gz` 在当前目录下。
    ```bash
    qemu-system-aarch64   -M virt   -cpu cortex-a57   -m 2048   -kernel common/arch/arm64/boot/Image.gz   -initrd rootfs.cpio.gz   -nographic   -append "console=ttyAMA0"
    ```

## 从 Shell 到 Zygote：下一步是什么？

我们已经有了一个最小的 Linux 环境，但它还不是"Android"。要让它成为 Android，还需要以下关键步骤：

1. **启动 `servicemanager`**: 编译并运行它，它是 Android Binder IPC 机制的核心。
2. **启动 Zygote**: 编译 `app_process` 并通过 `init.rc` 启动它。Zygote 会预加载 Android 框架的核心类 (`framework.jar`) 并监听一个 socket，等待孵化新的 App 进程。
3. **启动 `system_server`**: Zygote 启动的第一个 Java 进程，它会创建所有的 Android 系统服务 (AMS, WMS, PMS 等)。

完成这些后，系统才能真正地运行 Android 应用。但这已经超出了"最小化 RootFS"的范畴，进入了完整的系统移植和开发领域。

---

## 开源实现：mini_rootfs

基于本文介绍的构建技术，我实现了一个精简的开源项目：[mini_rootfs](https://github.com/overkazaf/mini_rootfs)

该项目演示了最小化rootfs环境下的动态库加载机制，提供两种实现方式：
- **Android方式**: 使用系统内置 `dlopen/dlsym` API 进行动态库加载
- **Linux方式**: 从头实现自定义ELF加载器，模拟Android linker架构
- **ELF解析**: 包含完整的ELF文件解析、内存映射、符号解析、重定位处理
- **教育导向**: 深入理解操作系统如何加载和执行动态链接的二进制文件

如果你对最小化 RootFS 环境下的动态链接机制感兴趣，欢迎参考该项目的实现，也欢迎贡献代码。
