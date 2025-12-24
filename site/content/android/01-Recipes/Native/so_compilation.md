---
title: "SO 动态库编译与加载"
date: 2025-12-25
weight: 10
---

# SO 动态库编译与加载

> **📚 前置知识**
>
> 本配方涉及以下核心技术，建议先阅读相关章节：
>
> - **[SO/ELF 格式](../../04-Reference/Foundations/so_elf_format.md)** - 理解 ELF 文件的段与节
> - **[JNI 开发与调用原理](./jni_development.md)** - 理解 Java 与 Native 的交互

本章介绍如何从零开始编译 Android SO 动态库，以及 Android 系统加载 SO 的完整流程。理解这些原理对于逆向分析 Native 层代码至关重要。

## 目录

1. [SO 文件基础](#so-文件基础)
2. [编译环境准备](#编译环境准备)
3. [使用 NDK 编译 SO](#使用-ndk-编译-so)
4. [使用 CMake 构建](#使用-cmake-构建)
5. [SO 加载流程分析](#so-加载流程分析)
6. [手动加载 SO](#手动加载-so)
7. [调试与分析技巧](#调试与分析技巧)

---

## SO 文件基础

### 什么是 SO 文件

SO (Shared Object) 是 Linux/Android 系统的动态链接库格式，相当于 Windows 的 DLL。它采用 ELF (Executable and Linkable Format) 格式。

### SO 文件结构

```
┌─────────────────────┐
│     ELF Header      │  文件类型、架构、入口点
├─────────────────────┤
│   Program Headers   │  段加载信息
├─────────────────────┤
│      .text          │  可执行代码
├─────────────────────┤
│      .rodata        │  只读数据（字符串常量等）
├─────────────────────┤
│      .data          │  已初始化的全局变量
├─────────────────────┤
│      .bss           │  未初始化的全局变量
├─────────────────────┤
│      .dynamic       │  动态链接信息
├─────────────────────┤
│      .dynsym        │  动态符号表
├─────────────────────┤
│      .dynstr        │  动态字符串表
├─────────────────────┤
│   Section Headers   │  节信息
└─────────────────────┘
```

### Android 支持的 CPU 架构

| ABI           | 架构            | 说明                  |
| ------------- | --------------- | --------------------- |
| `arm64-v8a`   | ARMv8-A (64 位) | 现代 Android 设备主流 |
| `armeabi-v7a` | ARMv7-A (32 位) | 老旧设备兼容          |
| `x86_64`      | x86-64 (64 位)  | 模拟器、部分平板      |
| `x86`         | x86 (32 位)     | 老旧模拟器            |

---

## 编译环境准备

### 1. 安装 Android NDK

```bash
# 方式一：通过 Android Studio SDK Manager 安装

# 方式二：命令行下载
# 下载地址：https://developer.android.com/ndk/downloads
wget https://dl.google.com/android/repository/android-ndk-r25c-linux.zip
unzip android-ndk-r25c-linux.zip
export NDK_HOME=/path/to/android-ndk-r25c
export PATH=$PATH:$NDK_HOME
```

### 2. 验证安装

```bash
# 检查 NDK 版本
$NDK_HOME/ndk-build --version

# 检查可用的工具链
ls $NDK_HOME/toolchains/llvm/prebuilt/*/bin/
```

### 3. 独立工具链（可选）

```bash
# 创建独立工具链（适合命令行编译）
$NDK_HOME/build/tools/make_standalone_toolchain.py \
    --arch arm64 \
    --api 21 \
    --install-dir /path/to/toolchain
```

---

## 使用 NDK 编译 SO

### 方式一：ndk-build

#### 1. 项目结构

```
project/
├── jni/
│   ├── Android.mk
│   ├── Application.mk
│   └── native.c
└── libs/
    ├── arm64-v8a/
    │   └── libnative.so
    └── armeabi-v7a/
        └── libnative.so
```

#### 2. Android.mk

```makefile
LOCAL_PATH := $(call my-dir)

include $(CLEAR_VARS)

# 模块名称（生成 lib<名称>.so）
LOCAL_MODULE := native

# 源文件
LOCAL_SRC_FILES := native.c

# 依赖的系统库
LOCAL_LDLIBS := -llog -lz

# 编译选项
LOCAL_CFLAGS := -Wall -O2

# 构建动态库
include $(BUILD_SHARED_LIBRARY)
```

#### 3. Application.mk

```makefile
# 目标 ABI
APP_ABI := arm64-v8a armeabi-v7a

# 最低 API 级别
APP_PLATFORM := android-21

# C++ STL 库
APP_STL := c++_shared

# 优化级别
APP_OPTIM := release
```

#### 4. native.c

```c
#include <jni.h>
#include <string.h>
#include <android/log.h>

#define LOG_TAG "NativeLib"
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO, LOG_TAG, __VA_ARGS__)

// 导出函数
JNIEXPORT jstring JNICALL
Java_com_example_app_MainActivity_stringFromJNI(JNIEnv *env, jobject thiz) {
    LOGI("stringFromJNI called");
    return (*env)->NewStringUTF(env, "Hello from C!");
}

// 初始化函数（可选）
__attribute__((constructor))
void lib_init() {
    LOGI("Library loaded!");
}

// 卸载函数（可选）
__attribute__((destructor))
void lib_fini() {
    LOGI("Library unloaded!");
}
```

#### 5. 编译

```bash
cd project/
$NDK_HOME/ndk-build

# 清理
$NDK_HOME/ndk-build clean

# 指定 verbose 输出
$NDK_HOME/ndk-build V=1
```

### 方式二：命令行直接编译

```bash
# 设置编译器
export CC=$NDK_HOME/toolchains/llvm/prebuilt/linux-x86_64/bin/aarch64-linux-android21-clang

# 编译为目标文件
$CC -c -fPIC -o native.o native.c

# 链接为 SO
$CC -shared -o libnative.so native.o -llog

# 查看导出符号
$NDK_HOME/toolchains/llvm/prebuilt/linux-x86_64/bin/llvm-nm -D libnative.so
```

---

## 使用 CMake 构建

### 1. CMakeLists.txt

```cmake
cmake_minimum_required(VERSION 3.10.2)

project("nativelib")

# 设置 C++ 标准
set(CMAKE_CXX_STANDARD 17)

# 添加编译选项
add_compile_options(-Wall -O2)

# 定义库
add_library(
    native-lib
    SHARED
    src/native.cpp
    src/crypto.cpp
    src/utils.cpp
)

# 查找系统库
find_library(log-lib log)
find_library(z-lib z)

# 包含头文件目录
target_include_directories(native-lib PRIVATE
    ${CMAKE_SOURCE_DIR}/include
)

# 链接库
target_link_libraries(native-lib
    ${log-lib}
    ${z-lib}
)

# 添加预处理器定义
target_compile_definitions(native-lib PRIVATE
    DEBUG_MODE=1
)
```

### 2. 使用 CMake 编译

```bash
# 创建构建目录
mkdir build && cd build

# 配置（指定 NDK 工具链）
cmake \
    -DCMAKE_TOOLCHAIN_FILE=$NDK_HOME/build/cmake/android.toolchain.cmake \
    -DANDROID_ABI=arm64-v8a \
    -DANDROID_PLATFORM=android-21 \
    ..

# 编译
cmake --build .

# 或者使用 make
make -j4
```

### 3. Gradle 集成

```groovy
android {
    defaultConfig {
        externalNativeBuild {
            cmake {
                cppFlags "-std=c++17 -frtti -fexceptions"
                arguments "-DANDROID_STL=c++_shared"
            }
        }
        ndk {
            abiFilters 'arm64-v8a', 'armeabi-v7a'
        }
    }

    externalNativeBuild {
        cmake {
            path "src/main/cpp/CMakeLists.txt"
            version "3.10.2"
        }
    }
}
```

---

## SO 加载流程分析

### Android SO 加载流程

```
Java: System.loadLibrary("native")
         │
         ▼
Runtime.loadLibrary0()
         │
         ▼
ClassLoader.findLibrary()  ──→  查找 libnative.so 路径
         │
         ▼
Runtime.nativeLoad()
         │
         ▼
dlopen("libnative.so")  ──→  系统加载器
         │
         ├──→ 解析 ELF 头
         ├──→ 映射 PT_LOAD 段到内存
         ├──→ 处理依赖库（递归加载）
         ├──→ 执行重定位
         └──→ 调用 .init_array / constructor
         │
         ▼
JNI_OnLoad() ──→ 如果存在，执行初始化
```

### 关键函数

| 函数                   | 说明                |
| ---------------------- | ------------------- |
| `System.loadLibrary()` | Java 层加载库       |
| `dlopen()`             | Native 层打开动态库 |
| `dlsym()`              | 查找符号地址        |
| `dlclose()`            | 关闭动态库          |
| `JNI_OnLoad()`         | JNI 初始化回调      |
| `JNI_OnUnload()`       | JNI 卸载回调        |

### 库搜索路径

```java
// 应用私有库目录
/data/app/<package>/lib/<abi>/

// 系统库目录
/system/lib64/  (64位)
/system/lib/    (32位)
/vendor/lib64/
/vendor/lib/
```

---

## 手动加载 SO

### Java 层加载

```java
public class NativeLoader {

    // 方式一：从默认路径加载
    static {
        System.loadLibrary("native");  // 加载 libnative.so
    }

    // 方式二：从绝对路径加载
    public static void loadFromPath(String path) {
        System.load(path);  // 如: /data/local/tmp/libnative.so
    }

    // 方式三：自定义 ClassLoader
    public static void loadWithClassLoader(String libName) {
        try {
            // 获取应用的 ClassLoader
            ClassLoader loader = NativeLoader.class.getClassLoader();

            // 使用反射调用 findLibrary
            Method findLibrary = ClassLoader.class.getDeclaredMethod(
                "findLibrary", String.class);
            findLibrary.setAccessible(true);

            String libPath = (String) findLibrary.invoke(loader, libName);
            if (libPath != null) {
                System.load(libPath);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
```

### Native 层加载

```c
#include <dlfcn.h>
#include <android/log.h>

#define LOG_TAG "DynamicLoader"
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO, LOG_TAG, __VA_ARGS__)

// 动态加载 SO 并调用函数
void load_and_call(const char* lib_path, const char* func_name) {
    // 打开动态库
    void* handle = dlopen(lib_path, RTLD_NOW);
    if (!handle) {
        LOGI("dlopen failed: %s", dlerror());
        return;
    }

    // 查找函数符号
    typedef int (*func_ptr)(int, int);
    func_ptr func = (func_ptr)dlsym(handle, func_name);

    if (!func) {
        LOGI("dlsym failed: %s", dlerror());
        dlclose(handle);
        return;
    }

    // 调用函数
    int result = func(10, 20);
    LOGI("Function result: %d", result);

    // 关闭库
    dlclose(handle);
}

// 示例：加载加密库
void load_crypto_lib() {
    void* handle = dlopen("libcrypto.so", RTLD_LAZY);
    if (handle) {
        // 获取加密函数
        void* encrypt_func = dlsym(handle, "AES_encrypt");
        if (encrypt_func) {
            LOGI("Found AES_encrypt at %p", encrypt_func);
        }
    }
}
```

---

## 调试与分析技巧

### 1. 查看 SO 信息

```bash
# 查看 ELF 头信息
readelf -h libnative.so

# 查看程序头（加载段）
readelf -l libnative.so

# 查看节头
readelf -S libnative.so

# 查看动态符号表
readelf -s libnative.so

# 查看依赖库
readelf -d libnative.so | grep NEEDED

# 查看导出函数
nm -D libnative.so | grep " T "
```

### 2. Frida 动态分析

```javascript
// 监控 dlopen
Interceptor.attach(Module.findExportByName(null, "dlopen"), {
  onEnter: function (args) {
    this.path = args[0].readCString();
    console.log("[dlopen]", this.path);
  },
  onLeave: function (retval) {
    console.log("[dlopen] handle:", retval);
  },
});

// 监控 dlsym
Interceptor.attach(Module.findExportByName(null, "dlsym"), {
  onEnter: function (args) {
    this.symbol = args[1].readCString();
    console.log("[dlsym]", this.symbol);
  },
  onLeave: function (retval) {
    console.log("[dlsym] address:", retval);
  },
});

// 枚举已加载的模块
Process.enumerateModules().forEach(function (module) {
  if (module.name.indexOf("native") !== -1) {
    console.log(module.name, module.base, module.size);
  }
});

// 枚举模块导出函数
Module.enumerateExports("libnative.so").forEach(function (exp) {
  console.log(exp.type, exp.name, exp.address);
});
```

### 3. GDB 调试

```bash
# 连接到进程
adb forward tcp:1234 tcp:1234
gdbserver :1234 --attach <pid>

# 本地 GDB 连接
$NDK_HOME/prebuilt/linux-x86_64/bin/gdb
(gdb) target remote :1234
(gdb) set solib-search-path /path/to/symbols

# 在函数上设置断点
(gdb) break Java_com_example_app_MainActivity_stringFromJNI
(gdb) continue

# 查看内存
(gdb) x/20x $pc
```

### 4. 常见问题排查

| 问题                               | 原因           | 解决方法               |
| ---------------------------------- | -------------- | ---------------------- |
| `UnsatisfiedLinkError`             | 找不到库或符号 | 检查库路径和函数签名   |
| `dlopen failed: library not found` | 依赖库缺失     | 检查 `readelf -d` 输出 |
| `text relocations`                 | 代码段重定位   | 编译时添加 `-fPIC`     |
| `cannot locate symbol`             | 符号未导出     | 检查函数是否标记为导出 |
