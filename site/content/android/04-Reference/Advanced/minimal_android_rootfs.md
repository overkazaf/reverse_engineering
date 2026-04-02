---
title: "构建最小化 Android 系统 (RootFS) 指南"
date: 2025-10-02
type: posts
tags: ["高级", "Android", "Root检测", "ARM汇编", "底层原理"]
weight: 10
---

# 构建最小化 Android 系统 (RootFS) 指南

构建一个完整的 AOSP (Android Open Source Project) 耗时巨大且对硬件要求苛刻。而构建一个最小化的 Android RootFS (Root File System) 是一个能让我们深刻理解 Android 启动流程和核心组件的绝佳实践。其目标是创建一个仅包含最基本组件、能够引导 Linux 内核并最终启动一个交互式 Shell 的系统。

## 本文将指导你完成这一过程，主要使用 QEMU 作为目标平台。

## 最小 Android 根文件系统概述

最小 Android 根文件系统（Minimal Android RootFS）是一个被精简到最低限度的 Android 用户空间环境，仅保留运行 Native 二进制文件所必需的核心组件。与完整的 Android 系统（通常包含数 GB 的框架、应用和服务）不同，一个最小 RootFS 通常只有几十 MB：

| 组件 | 大小（约） | 用途 |
|------|-----------|------|
| `linker64` | ~1 MB | 动态链接器 |
| `libc.so` | ~1 MB | C 标准库 |
| `libm.so` / `libdl.so` | ~200 KB | 数学库 / 动态加载接口 |
| `sh` / `toybox` | ~500 KB | Shell 和基础命令 |
| `init` | ~300 KB | 初始化进程 |

### 为什么逆向工程师需要它

1. **隔离的执行环境**：不启动完整 Android 框架即可运行目标 SO，排除框架层干扰
2. **可控的测试条件**：精确控制环境中存在哪些库和文件，方便绕过环境检测
3. **快速迭代**：无需刷机或重启设备，修改环境后立即测试
4. **反检测规避**：APP 的反调试逻辑依赖完整环境中的特定文件和进程，在最小 RootFS 中这些检查点天然缺失
5. **底层学习**：深入理解 linker 如何加载 SO、依赖如何解析、JNI 如何初始化

### 典型使用场景

```text
场景 1：分析某 APP 的加密 SO
  完整设备 → 反调试检测 → 被杀进程
  最小 RootFS → 无检测 → 自由调试

场景 2：批量调用签名函数
  Frida Hook → 依赖设备、慢
  最小 RootFS + dlopen → 脱离设备、快
```

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

## 构建方法

除了后续详细讲解的"从 AOSP 源码交叉编译"方式外，还有几种常见策略：

### 方法一：从 AOSP 编译产物中提取

从完整 AOSP 编译后的 `out/target/product/<device>/` 目录中提取所需文件：

```bash
PRODUCT_DIR=/aosp/out/target/product/generic_arm64
ROOTFS=./my_rootfs

mkdir -p $ROOTFS/{system/bin,system/lib64,dev,proc,sys,data}

# 提取核心二进制和库
cp $PRODUCT_DIR/system/bin/{linker64,toybox,sh} $ROOTFS/system/bin/
cp $PRODUCT_DIR/system/lib64/{libc.so,libm.so,libdl.so,liblog.so} $ROOTFS/system/lib64/
```

### 方法二：从现有设备提取

如果有已 Root 的设备，通过 `adb` 直接拉取：

```bash
ROOTFS=./my_rootfs
mkdir -p $ROOTFS/{system/bin,system/lib64}

adb pull /system/bin/linker64    $ROOTFS/system/bin/
adb pull /system/bin/toybox      $ROOTFS/system/bin/
adb pull /system/lib64/libc.so   $ROOTFS/system/lib64/
adb pull /system/lib64/libm.so   $ROOTFS/system/lib64/
adb pull /system/lib64/libdl.so  $ROOTFS/system/lib64/
```

### 方法三：从 Factory Image 解包

适用于没有设备也没有编译环境的情况。从 [Google 官方](https://developers.google.com/android/images) 下载 Factory Image，解包 `system.img` 后提取：

```bash
unzip image-xxx.zip
simg2img system.img system.raw.img
mkdir /mnt/android_system
sudo mount -o ro system.raw.img /mnt/android_system
cp /mnt/android_system/bin/linker64 ./my_rootfs/system/bin/
# ... 提取其他所需文件
sudo umount /mnt/android_system
```

---

## 关键目录结构

```text
/ (根目录)
├── system/          # 系统分区（只读）
│   ├── bin/         # 系统二进制 (linker64, sh, toybox)
│   ├── lib64/       # 64位系统共享库
│   └── lib/         # 32位系统共享库
├── vendor/          # 厂商分区（硬件相关库）
│   ├── lib64/       # 厂商64位库
│   └── lib/         # 厂商32位库
├── data/            # 用户数据分区（可读写）
│   ├── app/         # 已安装应用
│   └── local/tmp/   # 临时文件（逆向常用）
├── proc/            # 进程信息（虚拟文件系统）
├── sys/             # 内核参数（虚拟文件系统）
├── dev/             # 设备节点 (null, zero, urandom, pts/)
└── init.rc          # 初始化配置
```

各目录在最小 RootFS 中的优先级：

| 目录 | 优先级 | 说明 |
|------|--------|------|
| `/system/bin/` | **必需** | 必须包含 `linker64` 和 `sh` |
| `/system/lib64/` | **必需** | 必须包含 `libc.so`、`libm.so`、`libdl.so` |
| `/proc/` | **必需** | 需挂载 procfs，很多程序读取 `/proc/self/maps` |
| `/dev/` | **必需** | 需挂载 tmpfs 并创建基础设备节点 |
| `/sys/` | 推荐 | 部分程序检测 sysfs |
| `/data/local/tmp/` | 推荐 | 常用的工作目录 |
| `/vendor/` | 可选 | 仅当目标 SO 依赖厂商库时需要 |

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

---

## Linker 与动态库

Android 的动态链接机制是理解和运用最小 RootFS 的核心。与标准 Linux 使用 `ld-linux.so` 不同，Android 使用自己的 `linker`（32位）或 `linker64`（64位）。

### linker 的工作流程

```text
Kernel 加载 ELF → 读取 PT_INTERP → 找到 /system/bin/linker64
  ↓
linker64: 解析 PT_LOAD 段 → 映射到内存
  ↓
解析 DT_NEEDED → 递归加载所有依赖库
  ↓
处理重定位（GOT/PLT 表） → 调用 .init_array → 跳转入口点
```

### LD_LIBRARY_PATH 与库搜索

```bash
# linker 搜索 SO 的顺序：
# 1. DT_RUNPATH (编译时嵌入 ELF)
# 2. LD_LIBRARY_PATH 环境变量
# 3. 默认路径 (/system/lib64 等)

export LD_LIBRARY_PATH=/system/lib64:/vendor/lib64:/data/local/tmp

# 查看 SO 的依赖
readelf -d target.so | grep NEEDED
```

### 在最小环境中手动加载 SO

```c
// loader.c - 通用 SO 加载器
#include <stdio.h>
#include <dlfcn.h>

int main(int argc, char *argv[]) {
    if (argc < 3) {
        printf("Usage: %s <so_path> <func_name>\n", argv[0]);
        return 1;
    }
    void *handle = dlopen(argv[1], RTLD_NOW);
    if (!handle) { printf("dlopen: %s\n", dlerror()); return 1; }

    void *func = dlsym(handle, argv[2]);
    if (!func) { printf("dlsym: %s\n", dlerror()); dlclose(handle); return 1; }

    printf("[+] %s @ %p\n", argv[2], func);
    int (*f)(void) = (int (*)(void))func;
    printf("[+] Result: %d\n", f());
    dlclose(handle);
    return 0;
}
```

```bash
# 使用 NDK 交叉编译
$NDK/toolchains/llvm/prebuilt/linux-x86_64/bin/aarch64-linux-android30-clang \
    -o loader loader.c -ldl
cp loader my_rootfs/system/bin/
```

### 常见 linker 错误

| 错误信息 | 原因 | 解决方法 |
|---------|------|---------|
| `CANNOT FIND library "libxxx.so"` | 依赖库不在搜索路径中 | 复制到 `/system/lib64/` 或设置 `LD_LIBRARY_PATH` |
| `has text relocations` | 文本重定位（6.0+ 禁止） | 用 `-fPIC` 重编译或用旧版 linker |
| `cannot locate symbol "xxx"` | 缺少符号定义 | 检查依赖库或提供 stub 实现 |

---

## 在 chroot 环境中运行

在已 Root 的 Android 设备上，`chroot` 是使用最小 RootFS 最直接的方式。

### 设置与进入

```bash
adb push my_rootfs /data/local/tmp/rootfs
adb shell
su

ROOTFS=/data/local/tmp/rootfs

# 挂载虚拟文件系统
mount -t proc proc $ROOTFS/proc
mount -t sysfs sysfs $ROOTFS/sys
mount -t tmpfs tmpfs $ROOTFS/dev
mknod $ROOTFS/dev/null c 1 3
mknod $ROOTFS/dev/zero c 1 5
mknod $ROOTFS/dev/urandom c 1 9
mkdir -p $ROOTFS/dev/pts
mount -o bind /dev/pts $ROOTFS/dev/pts

# 进入 chroot
chroot $ROOTFS /system/bin/sh
```

### Bind Mount 映射目标文件

通过 bind mount 将设备上的目录映射到 chroot 环境中，无需复制文件：

```bash
# 映射目标 APP 的库目录
mkdir -p $ROOTFS/data/app_libs
mount -o bind /data/app/com.target.app/lib/arm64 $ROOTFS/data/app_libs

# 映射 vendor 库（如果目标 SO 依赖厂商库）
mkdir -p $ROOTFS/vendor/lib64
mount -o bind /vendor/lib64 $ROOTFS/vendor/lib64

# 进入后设置路径
chroot $ROOTFS /system/bin/sh
export LD_LIBRARY_PATH=/system/lib64:/vendor/lib64:/data/app_libs
/system/bin/loader /data/app_libs/libtarget.so targetFunction
```

### 退出和清理

```bash
exit
# 按反序卸载
umount $ROOTFS/dev/pts
umount $ROOTFS/dev
umount $ROOTFS/proc
umount $ROOTFS/sys
umount $ROOTFS/vendor/lib64 2>/dev/null
umount $ROOTFS/data/app_libs 2>/dev/null
```

---

## Docker Android 环境

Docker 提供了在 PC 上运行最小 Android 环境的便捷方式，配合 QEMU 用户态模拟可在 x86 上运行 ARM 二进制。

### Dockerfile 示例

```dockerfile
FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    qemu-user-static binfmt-support \
    && rm -rf /var/lib/apt/lists/*

RUN update-binfmts --enable qemu-aarch64
RUN mkdir -p /android/{system/bin,system/lib64,data/local/tmp}

COPY rootfs/system/bin/   /android/system/bin/
COPY rootfs/system/lib64/ /android/system/lib64/

ENV LD_LIBRARY_PATH=/android/system/lib64
ENV PATH=/android/system/bin:$PATH
WORKDIR /android/data/local/tmp
```

### 构建和使用

```bash
docker build -t android-rootfs .

# 运行容器，挂载目标库目录
docker run -it --rm \
    -v $(pwd)/target_libs:/android/data/local/tmp/libs \
    android-rootfs \
    qemu-aarch64-static -L /android /android/system/bin/sh

# 在容器中加载目标 SO
export LD_LIBRARY_PATH=/android/system/lib64:/android/data/local/tmp/libs
qemu-aarch64-static -L /android /android/system/bin/loader \
    /android/data/local/tmp/libs/libtarget.so targetFunction
```

| 方面 | 说明 |
|------|------|
| 可复现性 | 环境封装在镜像中，团队共享一致的分析环境 |
| 无需设备 | 在 x86 PC 上即可运行 ARM64 二进制 |
| 性能 | QEMU 用户态模拟比硬件慢 5-10 倍 |
| JNI 限制 | 无法提供真实的 JNI 环境（没有 ART） |

---

## proot 方案

`proot` 是无需 root 权限的 `chroot` 替代方案，通过 `ptrace` 拦截和重写文件路径相关的系统调用来模拟根目录切换。

### 基本使用

```bash
# 推送 proot 和 RootFS 到设备（无需 root）
adb push proot-aarch64 /data/local/tmp/proot
adb push my_rootfs /data/local/tmp/rootfs
adb shell chmod +x /data/local/tmp/proot

adb shell
cd /data/local/tmp

# 进入环境（绑定必要的虚拟文件系统）
./proot -r ./rootfs -b /proc -b /dev -b /sys /system/bin/sh

# 绑定目标 APP 的 SO 目录
./proot -r ./rootfs \
    -b /proc -b /dev \
    -b /data/app/com.target.app/lib/arm64:/data/libs \
    /system/bin/sh
```

### proot 的局限性

| 限制 | 说明 |
|------|------|
| 性能开销 | `ptrace` 拦截每个系统调用，性能损失约 10-30% |
| 兼容性 | 部分系统调用无法完美拦截 |
| SELinux | 在 enforcing 模式下可能受限 |
| Android 限制 | Android 10+ 限制了 `ptrace` 的使用范围 |

> **提示**：设备已 Root 时优先使用 `chroot`；只在无法获得 Root 权限时使用 `proot`。

---

## 实战：在最小环境中运行 SO

> **💡 思路一句话**: 当你需要脱离 Android 设备运行 SO（如 CI/CD 中自动化调用签名函数）— 用 Docker 搭建最小 Android 根文件系统 + linker + libc，就能在服务器上直接执行 SO 中的函数。

以下是完整的端到端示例：在最小 RootFS 中加载并调用目标 SO 的 Native 函数。

### 提取目标 SO 及其依赖

```bash
# 获取目标 SO 并查看依赖
adb pull /data/app/com.example.target/lib/arm64/libtarget.so ./
readelf -d libtarget.so | grep NEEDED
# (NEEDED) Shared library: [libc.so]
# (NEEDED) Shared library: [libm.so]
# (NEEDED) Shared library: [liblog.so]
# (NEEDED) Shared library: [libz.so]

# 拉取所有依赖库
for lib in libc.so libm.so liblog.so libz.so libdl.so; do
    adb pull /system/lib64/$lib ./rootfs/system/lib64/
done
```

### 编写调用程序并部署

```c
// call_target.c
#include <stdio.h>
#include <string.h>
#include <dlfcn.h>

int main() {
    void *handle = dlopen("/data/local/tmp/libtarget.so", RTLD_NOW);
    if (!handle) { fprintf(stderr, "[-] %s\n", dlerror()); return 1; }

    typedef int (*sign_func_t)(const char *, int);
    sign_func_t do_sign = (sign_func_t)dlsym(handle, "do_sign");
    if (!do_sign) { fprintf(stderr, "[-] %s\n", dlerror()); return 1; }

    const char *input = "hello_reverse";
    int result = do_sign(input, strlen(input));
    printf("[+] do_sign(\"%s\") = 0x%x\n", input, result);

    dlclose(handle);
    return 0;
}
```

```bash
# 编译并部署
NDK_CC=$NDK/toolchains/llvm/prebuilt/linux-x86_64/bin/aarch64-linux-android30-clang
$NDK_CC -o call_target call_target.c -ldl -pie

adb push call_target /data/local/tmp/rootfs/system/bin/
adb push libtarget.so /data/local/tmp/rootfs/data/local/tmp/
```

### 在 chroot 中执行

```bash
adb shell
su
ROOTFS=/data/local/tmp/rootfs
mount -t proc proc $ROOTFS/proc
mount -t tmpfs tmpfs $ROOTFS/dev
mknod $ROOTFS/dev/null c 1 3
mknod $ROOTFS/dev/urandom c 1 9

chroot $ROOTFS /system/bin/sh -c '
    export LD_LIBRARY_PATH=/system/lib64
    /system/bin/call_target
'
# [+] do_sign("hello_reverse") = 0xa3f2b1c0
```

### 常见问题排查

```bash
# 缺少依赖库 → 从设备拉取
adb pull /system/lib64/libxxx.so $ROOTFS/system/lib64/

# .init_array 崩溃 → 开启调试日志
export LD_DEBUG=all
/system/bin/call_target 2>&1 | head -100

# JNI_OnLoad 需要 JNIEnv → 构造 fake JNIEnv 或 patch 掉 JNI_OnLoad
```

---

## 与 unidbg 对比

最小 RootFS 和 unidbg 都能脱离完整 Android 环境运行 SO 函数，但原理和适用场景有显著差异。

| 特性 | 最小 RootFS | unidbg |
|------|-----------|--------|
| 运行方式 | 真实 ARM 硬件 / QEMU 全系统模拟 | Unicorn 指令级模拟 |
| linker | Android 原生 linker | 自行实现的 ELF 加载器 |
| 系统调用 | 真实内核处理 | 手动 Mock |
| JNI 支持 | 需自行构造 | 内置完整 JNI 模拟 |
| 运行平台 | ARM 设备 / QEMU | 任意 PC（Java/Python） |
| 性能 | 接近原生（设备）/ 中等（QEMU） | 较慢（指令模拟） |
| 调试 | GDB、strace 等标准工具 | 内置 Trace、寄存器查看 |
| 环境复杂度 | 需要准备文件系统 | 开箱即用 |

### 选择建议

- **纯 Native 函数 + 有 ARM 设备** → 最小 RootFS + chroot（性能最优）
- **需要 JNI 环境或复杂 Java 回调** → unidbg（JNI Mock 更成熟）
- **批量自动化调用** → unidbg（Java/Python 集成方便）
- **无 ARM 设备** → unidbg 或 Docker + QEMU

### 互补使用策略

在实际逆向项目中，两者往往配合使用：

1. **初始分析**：unidbg 快速验证函数调用，确认入参和返回值格式
2. **深度调试**：最小 RootFS 中使用 GDB 调试崩溃和逻辑问题
3. **自动化**：将可用的调用封装到 unidbg，批量生成签名或解密数据
4. **对抗升级**：当 unidbg 的 Mock 无法满足需求时，切换到最小 RootFS 获得更真实的环境

---

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
