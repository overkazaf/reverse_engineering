# JNI 开发与调用原理

JNI (Java Native Interface) 是 Java 与 C/C++ 代码交互的标准接口。在 Android 逆向工程中，理解 JNI 的工作原理对于分析 Native 层代码至关重要。本章将从开发者视角介绍 JNI 的原理与实践。

## 目录

1. [JNI 基础概念](#jni-基础概念)
2. [JNI 开发环境搭建](#jni-开发环境搭建)
3. [JNI 函数注册方式](#jni-函数注册方式)
4. [JNI 数据类型映射](#jni-数据类型映射)
5. [JNI 常用函数](#jni-常用函数)
6. [完整示例：实现加密函数](#完整示例实现加密函数)
7. [逆向分析要点](#逆向分析要点)

---

## JNI 基础概念

### 什么是 JNI

JNI 是一个编程框架，允许 Java 代码调用 Native 代码（C/C++），也允许 Native 代码调用 Java 代码。

```
┌─────────────────┐
│   Java 层       │
│  (Dalvik/ART)   │
└────────┬────────┘
         │ JNI 接口
         ▼
┌─────────────────┐
│   Native 层     │
│   (C/C++ SO)    │
└─────────────────┘
```

### 为什么使用 JNI

| 用途         | 说明                                              |
| ------------ | ------------------------------------------------- |
| **性能优化** | 计算密集型任务（加密、图像处理）使用 C/C++ 更高效 |
| **代码复用** | 复用现有的 C/C++ 库（OpenSSL、FFmpeg 等）         |
| **安全保护** | Native 代码比 Java 更难逆向，常用于核心算法保护   |
| **硬件访问** | 直接访问硬件或操作系统底层功能                    |

---

## JNI 开发环境搭建

### 1. 配置 NDK

在 `build.gradle` 中配置 NDK：

```groovy
android {
    defaultConfig {
        ndk {
            abiFilters 'arm64-v8a', 'armeabi-v7a'
        }
    }

    externalNativeBuild {
        cmake {
            path "src/main/cpp/CMakeLists.txt"
        }
    }
}
```

### 2. 创建 CMakeLists.txt

```cmake
cmake_minimum_required(VERSION 3.10.2)

project("nativelib")

add_library(
    native-lib
    SHARED
    native-lib.cpp
)

find_library(
    log-lib
    log
)

target_link_libraries(
    native-lib
    ${log-lib}
)
```

### 3. 目录结构

```
app/
├── src/main/
│   ├── java/com/example/app/
│   │   └── NativeHelper.java      # Java 层声明
│   └── cpp/
│       ├── CMakeLists.txt
│       └── native-lib.cpp         # C/C++ 实现
```

---

## JNI 函数注册方式

### 方式一：静态注册（自动关联）

Java 层声明 native 方法：

```java
public class NativeHelper {
    static {
        System.loadLibrary("native-lib");
    }

    // 声明 native 方法
    public native String encrypt(String input);
    public native byte[] decrypt(byte[] data);
}
```

C++ 层实现（函数名遵循特定规则）：

```cpp
#include <jni.h>
#include <string>

// 函数名格式：Java_包名_类名_方法名
// 包名中的 . 替换为 _
extern "C" JNIEXPORT jstring JNICALL
Java_com_example_app_NativeHelper_encrypt(
    JNIEnv *env,
    jobject thiz,      // 非静态方法：jobject 指向调用对象
    jstring input) {

    // 获取 Java 字符串
    const char *str = env->GetStringUTFChars(input, nullptr);

    // 处理逻辑...
    std::string result = "encrypted_" + std::string(str);

    // 释放资源
    env->ReleaseStringUTFChars(input, str);

    // 返回新的 Java 字符串
    return env->NewStringUTF(result.c_str());
}
```

**静态注册的函数命名规则**：

```
Java_<包名>_<类名>_<方法名>

示例：
- 包名：com.example.app
- 类名：NativeHelper
- 方法名：encrypt
- 函数名：Java_com_example_app_NativeHelper_encrypt
```

### 方式二：动态注册（JNI_OnLoad）

动态注册在 `JNI_OnLoad` 中手动绑定函数：

```cpp
#include <jni.h>
#include <string>

// Native 函数实现（函数名可以任意）
static jstring native_encrypt(JNIEnv *env, jobject thiz, jstring input) {
    const char *str = env->GetStringUTFChars(input, nullptr);
    std::string result = "encrypted_" + std::string(str);
    env->ReleaseStringUTFChars(input, str);
    return env->NewStringUTF(result.c_str());
}

static jbyteArray native_decrypt(JNIEnv *env, jobject thiz, jbyteArray data) {
    // 解密实现...
    return data;
}

// 方法映射表
static JNINativeMethod gMethods[] = {
    // {Java方法名, 方法签名, Native函数指针}
    {"encrypt", "(Ljava/lang/String;)Ljava/lang/String;", (void*)native_encrypt},
    {"decrypt", "([B)[B", (void*)native_decrypt},
};

// JNI_OnLoad：库加载时自动调用
JNIEXPORT jint JNI_OnLoad(JavaVM *vm, void *reserved) {
    JNIEnv *env = nullptr;

    if (vm->GetEnv((void**)&env, JNI_VERSION_1_6) != JNI_OK) {
        return JNI_ERR;
    }

    // 找到目标 Java 类
    jclass clazz = env->FindClass("com/example/app/NativeHelper");
    if (clazz == nullptr) {
        return JNI_ERR;
    }

    // 注册 Native 方法
    int methodCount = sizeof(gMethods) / sizeof(gMethods[0]);
    if (env->RegisterNatives(clazz, gMethods, methodCount) < 0) {
        return JNI_ERR;
    }

    return JNI_VERSION_1_6;
}
```

### 两种注册方式对比

| 特性         | 静态注册              | 动态注册                 |
| ------------ | --------------------- | ------------------------ |
| **函数名**   | 必须遵循命名规则      | 可以任意命名             |
| **查找时机** | 首次调用时查找        | 加载时一次性注册         |
| **性能**     | 略慢（需要查找）      | 较快（直接使用函数指针） |
| **安全性**   | 函数名暴露类/方法信息 | 函数名可混淆，更隐蔽     |
| **逆向难度** | 较容易定位            | 需要分析 JNI_OnLoad      |

---

## JNI 数据类型映射

### 基本类型

| Java 类型 | JNI 类型   | 签名 | C/C++ 类型 |
| --------- | ---------- | ---- | ---------- |
| `boolean` | `jboolean` | `Z`  | `uint8_t`  |
| `byte`    | `jbyte`    | `B`  | `int8_t`   |
| `char`    | `jchar`    | `C`  | `uint16_t` |
| `short`   | `jshort`   | `S`  | `int16_t`  |
| `int`     | `jint`     | `I`  | `int32_t`  |
| `long`    | `jlong`    | `J`  | `int64_t`  |
| `float`   | `jfloat`   | `F`  | `float`    |
| `double`  | `jdouble`  | `D`  | `double`   |
| `void`    | `void`     | `V`  | `void`     |

### 引用类型

| Java 类型  | JNI 类型       | 签名                  |
| ---------- | -------------- | --------------------- |
| `Object`   | `jobject`      | `Ljava/lang/Object;`  |
| `String`   | `jstring`      | `Ljava/lang/String;`  |
| `Class`    | `jclass`       | `Ljava/lang/Class;`   |
| `int[]`    | `jintArray`    | `[I`                  |
| `byte[]`   | `jbyteArray`   | `[B`                  |
| `Object[]` | `jobjectArray` | `[Ljava/lang/Object;` |

### 方法签名格式

```
(参数类型)返回类型

示例：
- void method()                    -> ()V
- int method(int a)                -> (I)I
- String method(String s, int i)   -> (Ljava/lang/String;I)Ljava/lang/String;
- byte[] method(byte[] data)       -> ([B)[B
- void method(int[] arr, Object o) -> ([ILjava/lang/Object;)V
```

---

## JNI 常用函数

### 字符串操作

```cpp
// Java String -> C 字符串
const char* str = env->GetStringUTFChars(javaString, nullptr);
// 使用完毕后释放
env->ReleaseStringUTFChars(javaString, str);

// C 字符串 -> Java String
jstring result = env->NewStringUTF("Hello from C++");

// 获取字符串长度
jsize len = env->GetStringUTFLength(javaString);
```

### 数组操作

```cpp
// 获取数组长度
jsize len = env->GetArrayLength(javaArray);

// byte[] 操作
jbyte* bytes = env->GetByteArrayElements(byteArray, nullptr);
// 使用完毕后释放
env->ReleaseByteArrayElements(byteArray, bytes, 0);

// 创建新的 byte[]
jbyteArray newArray = env->NewByteArray(length);
env->SetByteArrayRegion(newArray, 0, length, data);

// int[] 操作
jint* ints = env->GetIntArrayElements(intArray, nullptr);
env->ReleaseIntArrayElements(intArray, ints, 0);
```

### 调用 Java 方法

```cpp
// 1. 获取类引用
jclass clazz = env->FindClass("com/example/app/MyClass");

// 2. 获取方法 ID
jmethodID methodId = env->GetMethodID(clazz, "methodName", "(I)Ljava/lang/String;");
// 静态方法使用 GetStaticMethodID

// 3. 调用方法
jstring result = (jstring)env->CallObjectMethod(obj, methodId, 123);
// 静态方法使用 CallStaticObjectMethod
```

### 访问 Java 字段

```cpp
// 获取字段 ID
jfieldID fieldId = env->GetFieldID(clazz, "fieldName", "I");
// 静态字段使用 GetStaticFieldID

// 读取字段值
jint value = env->GetIntField(obj, fieldId);

// 设置字段值
env->SetIntField(obj, fieldId, 100);
```

---

## 完整示例：实现加密函数

### Java 层

```java
package com.example.crypto;

public class CryptoHelper {
    static {
        System.loadLibrary("crypto-lib");
    }

    // AES 加密
    public native byte[] aesEncrypt(byte[] data, byte[] key);

    // AES 解密
    public native byte[] aesDecrypt(byte[] data, byte[] key);

    // MD5 哈希
    public native String md5(String input);
}
```

### Native 层 (crypto-lib.cpp)

```cpp
#include <jni.h>
#include <string>
#include <cstring>
#include <android/log.h>

#define LOG_TAG "CryptoLib"
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO, LOG_TAG, __VA_ARGS__)

// 简化的 XOR 加密示例（实际应使用 OpenSSL 等库）
static jbyteArray xor_encrypt(JNIEnv *env, jbyteArray data, jbyteArray key) {
    jsize dataLen = env->GetArrayLength(data);
    jsize keyLen = env->GetArrayLength(key);

    jbyte* dataBytes = env->GetByteArrayElements(data, nullptr);
    jbyte* keyBytes = env->GetByteArrayElements(key, nullptr);

    // 创建结果数组
    jbyteArray result = env->NewByteArray(dataLen);
    jbyte* resultBytes = new jbyte[dataLen];

    // XOR 加密
    for (int i = 0; i < dataLen; i++) {
        resultBytes[i] = dataBytes[i] ^ keyBytes[i % keyLen];
    }

    env->SetByteArrayRegion(result, 0, dataLen, resultBytes);

    // 清理
    delete[] resultBytes;
    env->ReleaseByteArrayElements(data, dataBytes, 0);
    env->ReleaseByteArrayElements(key, keyBytes, 0);

    return result;
}

// 简化的 MD5 实现（示例）
static jstring calc_md5(JNIEnv *env, jstring input) {
    const char* str = env->GetStringUTFChars(input, nullptr);

    // 实际应使用 OpenSSL 的 MD5 函数
    // 这里仅作示例，返回模拟的 MD5
    char md5[33];
    snprintf(md5, sizeof(md5), "%032x", (unsigned int)strlen(str));

    env->ReleaseStringUTFChars(input, str);
    return env->NewStringUTF(md5);
}

// 方法映射表
static JNINativeMethod gMethods[] = {
    {"aesEncrypt", "([B[B)[B", (void*)xor_encrypt},
    {"aesDecrypt", "([B[B)[B", (void*)xor_encrypt},  // XOR 加解密相同
    {"md5", "(Ljava/lang/String;)Ljava/lang/String;", (void*)calc_md5},
};

JNIEXPORT jint JNI_OnLoad(JavaVM *vm, void *reserved) {
    JNIEnv *env = nullptr;

    if (vm->GetEnv((void**)&env, JNI_VERSION_1_6) != JNI_OK) {
        return JNI_ERR;
    }

    jclass clazz = env->FindClass("com/example/crypto/CryptoHelper");
    if (clazz == nullptr) {
        LOGI("Failed to find class");
        return JNI_ERR;
    }

    int methodCount = sizeof(gMethods) / sizeof(gMethods[0]);
    if (env->RegisterNatives(clazz, gMethods, methodCount) < 0) {
        LOGI("Failed to register natives");
        return JNI_ERR;
    }

    LOGI("JNI_OnLoad success, registered %d methods", methodCount);
    return JNI_VERSION_1_6;
}
```

---

## 逆向分析要点

### 1. 定位 JNI 函数

**静态注册**：

```bash
# 在 IDA/Ghidra 中搜索函数名
# 格式：Java_包名_类名_方法名
strings libnative.so | grep "Java_"
```

**动态注册**：

```bash
# 分析 JNI_OnLoad 函数
# 查找 RegisterNatives 调用
# 追踪 JNINativeMethod 数组
```

### 2. Frida Hook JNI 函数

```javascript
// Hook JNI_OnLoad
Interceptor.attach(Module.findExportByName("libnative.so", "JNI_OnLoad"), {
  onEnter: function (args) {
    console.log("JNI_OnLoad called");
  },
  onLeave: function (retval) {
    console.log("JNI_OnLoad returned:", retval);
  },
});

// Hook RegisterNatives 获取动态注册信息
var RegisterNatives = Module.findExportByName(
  "libart.so",
  "_ZN3art3JNI15RegisterNativesEP7_JNIEnvP7_jclassPK15JNINativeMethodi"
);
Interceptor.attach(RegisterNatives, {
  onEnter: function (args) {
    var className = Java.vm.getEnv().getClassName(args[1]);
    var methods = args[2];
    var methodCount = args[3].toInt32();

    console.log("RegisterNatives:", className, "count:", methodCount);

    for (var i = 0; i < methodCount; i++) {
      var methodName = methods
        .add(i * Process.pointerSize * 3)
        .readPointer()
        .readCString();
      var signature = methods
        .add(i * Process.pointerSize * 3 + Process.pointerSize)
        .readPointer()
        .readCString();
      var fnPtr = methods
        .add(i * Process.pointerSize * 3 + Process.pointerSize * 2)
        .readPointer();

      console.log("  Method:", methodName, signature, "->", fnPtr);
    }
  },
});
```

### 3. 常见保护手段

| 保护手段   | 说明                   | 应对方法               |
| ---------- | ---------------------- | ---------------------- |
| 函数名混淆 | 使用动态注册隐藏函数名 | 分析 JNI_OnLoad        |
| 字符串加密 | 加密关键字符串         | 动态调试获取解密后的值 |
| 反调试检测 | 检测调试器/Frida       | 绕过反调试             |
| 代码混淆   | OLLVM 等混淆           | 符号执行/模式识别      |
