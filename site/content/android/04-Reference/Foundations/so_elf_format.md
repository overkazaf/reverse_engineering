---
title: "Android .so 文件详解 (ELF Format)"
weight: 10
---

# Android .so 文件详解 (ELF Format)

`.so` 文件（Shared Object）是 Android 平台上的原生共享库，等同于 Windows 上的 `.dll` 或 Linux 上的 `.so`。它们包含了由 C/C++ 等原生代码编译而成的机器码。在 Android 逆向工程中，分析 `.so` 文件是理解应用核心逻辑、破解加密算法和绕过安全机制的关键一步。

## 目录

1. [ELF 文件格式](#elf-文件格式)
   - [ELF Header](#elf-header)
   - [Program Header Table](#program-header-table)
   - [Section Header Table](#section-header-table)
   - [关键 Section](#关键-section)
2. [加载与链接](#加载与链接)
   - [System.loadLibrary()](#systemloadlibrary)
   - [JNI (Java Native Interface)](#jni-java-native-interface)
   - [动态链接器](#动态链接器)
3. [静态分析](#静态分析)
   - [识别关键函数](#识别关键函数)
   - [使用 IDA Pro / Ghidra](#使用-ida-pro--ghidra)
4. [动态分析](#动态分析)
   - [Frida Hook 原生函数](#frida-hook-原生函数)
   - [Unidbg 模拟执行](#unidbg-模拟执行)
5. [常见保护手段](#常见保护手段)
   - [字符串加密](#字符串加密)
   - [代码混淆](#代码混淆)
   - [反调试技术](#反调试技术)
6. [init_array 详解](#init_array-详解)
   - [调用时机](#调用时机)
   - [逆向分析对策](#逆向分析对策)

---

## ELF 文件格式

`.so` 文件遵循 **ELF (Executable and Linkable Format)** 格式，这是一种用于可执行文件、目标代码、共享库和核心转储的标准文件格式。

### ELF Header

位于文件开头，描述了整个文件的"档案"，包括：

| 字段 | 说明 |
|------|------|
| Magic Number | 文件的前 16 个字节，用于识别这是一个 ELF 文件 |
| Architecture | 标识文件是为哪种 CPU 架构编译的（如 ARM, ARM64, x86） |
| Type | 文件类型（可执行文件、共享库等） |
| Entry Point Address | 如果是可执行文件，这是程序启动的地址 |
| Program Header Table Offset | 指向程序头表的偏移 |
| Section Header Table Offset | 指向节头表的偏移 |

### Program Header Table

描述了系统如何将文件的各个部分（段，Segments）加载到内存中。每个条目都定义了一个段的类型（如 `LOAD`，表示需要加载到内存）、虚拟地址、物理地址、大小和权限（读、写、执行）。动态链接器 (`linker`) 依赖这个表来正确映射 `.so` 文件。

### Section Header Table

描述了文件中各个"节"（Sections）的信息。节是链接器用来组织和处理数据的单位。

### 关键 Section

| Section | 说明 |
|---------|------|
| `.text` | 包含已编译的程序机器码（汇编指令）。这是分析的核心区域 |
| `.rodata` | 只读数据区，通常存放字符串常量、const 变量等 |
| `.data` | 已初始化的可读可写数据区（全局变量和静态变量） |
| `.bss` | 未初始化的数据区。在文件中不占空间，但在加载到内存时会被分配并清零 |
| `.init_array` | 存放函数指针，这些函数会在库被加载 (`dlopen`) 时自动执行。**分析反调试的绝佳入口点** |
| `.fini_array` | 存放函数指针，这些函数会在库被卸载 (`dlclose`) 时自动执行 |
| `.dynsym` | 动态符号表，包含了库中导出和导入的函数和变量名 |
| `.dynstr` | 字符串表，`.dynsym` 中的符号名称就存储在这里 |

---

## 加载与链接

### System.loadLibrary()

在 Java/Kotlin 代码中，开发者通过 `System.loadLibrary("mylib")` 来加载一个名为 `libmylib.so` 的原生库。系统会在 `lib/` 目录下的相应 ABI 文件夹（如 `arm64-v8a`）中查找并加载该库。

### JNI (Java Native Interface)

JNI 是连接 Java 世界和 Native (C/C++) 世界的桥梁，是 Android 逆向分析中的核心知识点。

#### JNI 基础概念

**Java 侧声明**：

```java
public class NativeHelper {
    static {
        System.loadLibrary("native-lib"); // 加载 libnative-lib.so
    }

    // 静态 native 方法
    public static native String doEncrypt(String input);

    // 实例 native 方法
    public native byte[] processData(byte[] data, int flag);

    // 多参数 native 方法
    public native int complexOperation(String str, int[] array, boolean flag);
}
```

**Native 侧实现**：

```c
// 静态方法 JNI 函数签名：第二个参数是 jclass
JNIEXPORT jstring JNICALL
Java_com_example_app_NativeHelper_doEncrypt(JNIEnv *env, jclass clazz, jstring input) {
    const char *nativeString = (*env)->GetStringUTFChars(env, input, 0);
    // 执行加密逻辑...
    jstring result = (*env)->NewStringUTF(env, encrypted_result);
    (*env)->ReleaseStringUTFChars(env, input, nativeString);
    return result;
}

// 实例方法 JNI 函数签名：第二个参数是 jobject
JNIEXPORT jbyteArray JNICALL
Java_com_example_app_NativeHelper_processData(JNIEnv *env, jobject thiz, jbyteArray data, jint flag) {
    jsize len = (*env)->GetArrayLength(env, data);
    jbyte *body = (*env)->GetByteArrayElements(env, data, 0);

    // 处理数据...

    jbyteArray result = (*env)->NewByteArray(env, len);
    (*env)->SetByteArrayRegion(env, result, 0, len, processed_data);
    (*env)->ReleaseByteArrayElements(env, data, body, 0);
    return result;
}
```

#### JNI 数据类型映射

| Java 类型 | JNI 类型 | 签名字符 |
|-----------|----------|----------|
| boolean | jboolean | Z |
| byte | jbyte | B |
| char | jchar | C |
| short | jshort | S |
| int | jint | I |
| long | jlong | J |
| float | jfloat | F |
| double | jdouble | D |
| void | void | V |
| String | jstring | Ljava/lang/String; |
| Object | jobject | L完整类名; |
| int[] | jintArray | [I |
| byte[] | jbyteArray | [B |

#### JNI 常用函数

| 分类 | 函数 |
|------|------|
| 字符串操作 | `NewStringUTF()`, `GetStringUTFChars()`, `ReleaseStringUTFChars()` |
| 数组操作 | `NewByteArray()`, `GetByteArrayElements()`, `SetByteArrayRegion()` |
| 对象操作 | `NewObject()`, `GetObjectClass()`, `CallObjectMethod()` |
| 字段访问 | `GetFieldID()`, `GetIntField()`, `SetIntField()` |
| 方法调用 | `GetMethodID()`, `CallVoidMethod()`, `CallIntMethod()` |

#### JNI 方法注册

**静态注册**（编译时确定）：

函数名必须严格遵循命名规则：`Java_包名_类名_方法名`

```c
JNIEXPORT jstring JNICALL
Java_com_example_app_MainActivity_stringFromJNI(JNIEnv *env, jobject thiz) {
    return (*env)->NewStringUTF(env, "Hello from JNI!");
}
```

**动态注册**（运行时注册）：

```c
// 定义方法映射表
static JNINativeMethod gMethods[] = {
    {"encrypt", "(Ljava/lang/String;)Ljava/lang/String;", (void*)native_encrypt},
    {"decrypt", "([B)[B", (void*)native_decrypt},
    {"init", "(I)V", (void*)native_init}
};

// JNI_OnLoad 函数在库加载时自动调用
JNIEXPORT jint JNICALL JNI_OnLoad(JavaVM* vm, void* reserved) {
    JNIEnv* env;
    if ((*vm)->GetEnv(vm, (void**)&env, JNI_VERSION_1_6) != JNI_OK) {
        return JNI_ERR;
    }

    jclass clazz = (*env)->FindClass(env, "com/example/app/NativeHelper");
    if (clazz == NULL) {
        return JNI_ERR;
    }

    // 注册 native 方法
    if ((*env)->RegisterNatives(env, clazz, gMethods,
            sizeof(gMethods)/sizeof(gMethods[0])) < 0) {
        return JNI_ERR;
    }

    return JNI_VERSION_1_6;
}
```

### 动态链接器

动态链接器 (`/system/bin/linker` 或 `linker64`) 负责：

1. 将 `.so` 文件映射到进程的虚拟地址空间
2. 重定位符号（调整代码中的地址引用）
3. 解析该库的依赖项（即它需要从其他库，如 `libc.so`，导入的函数），并填充导入函数的地址
4. 执行 `.init_array` 中的初始化函数

---

## 静态分析

### 识别关键函数

| 目标 | 方法 |
|------|------|
| JNI 函数 | 在符号列表中搜索 `Java_` 前缀，可以快速定位所有 Java 和 Native 的交互点 |
| 导出函数 | 查看 `Exports` 列表，寻找有意义的函数名，如 `encrypt`, `decrypt`, `checkSignature` |
| `.init_array` 函数 | 查看 `.init_array` section，分析在库加载时自动执行的函数 |

**命令行工具**：

```bash
# 列出导出的 JNI 函数
nm -D libexample.so | grep Java_

# 使用 objdump
objdump -T libexample.so | grep Java_
```

### 使用 IDA Pro / Ghidra

1. **加载文件**: 将 `.so` 文件拖入 IDA 或 Ghidra
2. **查看伪代码**: 按 `F5` (IDA) 或等待 Ghidra 的自动分析，直接阅读反编译出的 C 伪代码
3. **交叉引用 (Cross-References)**: 对一个函数名或字符串常量按 `X` 键，可以查看所有引用了它的地方
4. **图形模式**: 使用图形视图来理解复杂的函数调用流程和条件分支

---

## 动态分析

### Frida Hook 原生函数

当静态分析困难（如代码被混淆或算法复杂）时，动态 Hook 是最有效的方法。

**基于偏移地址 Hook**：

```javascript
// Frida 脚本
const baseAddr = Module.findBaseAddress("libnative-lib.so");
const targetFuncPtr = baseAddr.add(0x1234); // 0x1234 是从 IDA/Ghidra 获取的函数偏移

Interceptor.attach(targetFuncPtr, {
    onEnter: function(args) {
        // args[0], args[1]... 是函数参数（指针）
        console.log("Hooked function called!");
        // 可以使用 Memory.readCString(args[0]) 等来读取参数内容
    },
    onLeave: function(retval) {
        // retval 是函数返回值
        // retval.replace(0x1); // 可以修改返回值
    }
});
```

**基于导出名称 Hook**：

```javascript
var encrypt_func = Module.findExportByName("libnative.so",
    "Java_com_example_app_NativeHelper_doEncrypt");

Interceptor.attach(encrypt_func, {
    onEnter: function(args) {
        // args[0] = JNIEnv*
        // args[1] = jclass/jobject
        // args[2] = 第一个参数 (jstring)
        var jstring_ptr = args[2];
        var str_content = Java.vm.getEnv().getStringUtfChars(jstring_ptr, null);
        console.log("Input: " + str_content.readCString());
    },
    onLeave: function(retval) {
        var result = Java.vm.getEnv().getStringUtfChars(retval, null);
        console.log("Output: " + result.readCString());
    }
});
```

**Java 层 Hook**：

```javascript
Java.perform(function() {
    var NativeHelper = Java.use("com.example.app.NativeHelper");

    NativeHelper.doEncrypt.implementation = function(input) {
        console.log("Java -> Native: " + input);
        var result = this.doEncrypt(input);
        console.log("Native -> Java: " + result);
        return result;
    };
});
```

### Unidbg 模拟执行

Unidbg 是一个基于 Unicorn 的 Android 原生库模拟执行框架，可以在 PC 上模拟执行 `.so` 文件。

```java
// Unidbg 基本用法
public class EmulatorDemo {
    public static void main(String[] args) {
        AndroidEmulator emulator = AndroidEmulatorBuilder.for64Bit().build();
        Memory memory = emulator.getMemory();
        memory.setLibraryResolver(new AndroidResolver(23));

        // 加载目标 so
        Module module = emulator.loadLibrary(new File("libtarget.so"));

        // 调用函数
        Number result = module.callFunction(emulator, "target_function", arg1, arg2);
        System.out.println("Result: " + result);
    }
}
```

---

## 常见保护手段

### 字符串加密

**保护机制**: `.so` 文件中的敏感字符串（如密钥、URL）被加密存放，在运行时动态解密使用。静态分析时无法直接看到。

**Native 实现示例**：

```c
// 加密的字符串
static char encrypted[] = "\x56\x2a\x3b\x4c\x5d";  // XOR 加密后的数据

const char* get_decrypted_string() {
    static char decrypted[256];
    int key = 0x42;
    for (int i = 0; encrypted[i]; i++) {
        decrypted[i] = encrypted[i] ^ key;
    }
    return decrypted;
}
```

**攻击方法**：

```javascript
// Frida Hook 解密函数
var decrypt_func = Module.findExportByName("libnative.so", "decrypt_string");
Interceptor.attach(decrypt_func, {
    onLeave: function(retval) {
        console.log("Decrypted string:", Memory.readCString(retval));
    }
});
```

### 代码混淆

**常见混淆技术**：

- 控制流平坦化 (Control Flow Flattening)
- 虚假控制流 (Bogus Control Flow)
- 指令替换 (Instruction Substitution)
- 符号剥离 (Symbol Stripping)

**攻击方法**：

```javascript
// 指令级 Hook 示例
var baseAddr = Module.findBaseAddress("libnative.so");
Interceptor.attach(baseAddr.add(0x1000), {
    onEnter: function(args) {
        console.log("Register state:", this.context);
    }
});
```

### 反调试技术

**常见检测方法**：

```c
// ptrace 反调试
JNIEXPORT void JNICALL
Java_com_example_app_Security_checkDebugger(JNIEnv *env, jclass clazz) {
    if (ptrace(PTRACE_TRACEME, 0, 1, 0) == -1) {
        // 检测到调试器，执行反制措施
        exit(1);
    }
}

// 模拟器检测
JNIEXPORT jboolean JNICALL
Java_com_example_app_Security_isEmulator(JNIEnv *env, jclass clazz) {
    char prop_value[256];
    __system_property_get("ro.kernel.qemu", prop_value);
    return strcmp(prop_value, "1") == 0;
}
```

**绕过方法**：

```javascript
// 绕过反调试示例
var anti_debug = Module.findExportByName("libnative.so", "check_debug");
Interceptor.attach(anti_debug, {
    onLeave: function(retval) {
        retval.replace(0);  // 返回 0 表示未检测到调试
    }
});

// Hook ptrace 系统调用
var ptrace = Module.findExportByName("libc.so", "ptrace");
Interceptor.attach(ptrace, {
    onEnter: function(args) {
        args[0] = ptr(0);  // 修改 ptrace 参数
    }
});
```

---

## init_array 详解

### 调用时机

`.init_array` 中的函数在 **ELF 库加载过程中的早期阶段** 被调用，这个时机非常关键，发生在 `JNI_OnLoad` 之前。

#### 完整的调用流程

```
System.loadLibrary("native")
         ↓
nativeLoad() [art/runtime/native/java_lang_Runtime.cc]
         ↓
android_dlopen_ext() [bionic/libdl/libdl.cpp]
         ↓
do_dlopen() [bionic/linker/linker.cpp]
         ↓
find_library() → load_library() → link_image()
         ↓
call_constructors() → init_array 函数执行
         ↓
JNI_OnLoad() 执行
```

#### Linker 源码分析

```cpp
// bionic/linker/linker.cpp
void soinfo::call_constructors() {
    // 1. 首先调用 DT_INIT 初始化函数
    if (init_func_ != nullptr) {
        init_func_();
    }

    // 2. 然后遍历 .init_array section 函数指针
    if (init_array_ != nullptr) {
        for (size_t i = 0; i < init_array_count_; ++i) {
            // 调用每个构造函数，包括 init_string_obfuscation
            ((void (*)())init_array_[i])();
        }
    }
}
```

#### C/C++ 声明方式

```cpp
// 字符串混淆初始化函数声明
__attribute__((constructor))
void init_string_obfuscation() {
    // 字符串解密和反调试逻辑
    decrypt_critical_strings();
    setup_anti_debug_measures();
}

// 可以指定优先级（数字越小，优先级越高）
__attribute__((constructor(101)))
void init_anti_debug_level1() {
    // 第一级反调试检测
    basic_environment_check();
}

__attribute__((constructor(102)))
void init_string_decryption() {
    // 字符串解密，依赖第一级检测通过
    if (environment_safe) {
        decrypt_strings();
    }
}
```

#### 实际应用示例

```cpp
// 实际字符串混淆初始化函数示例
__attribute__((constructor(100)))
void init_string_obfuscation() {
    // 1. 环境安全检查
    if (detect_debug_environment()) {
        // 检测到调试环境，执行反制措施
        execute_anti_debug_response();
        return;
    }

    // 2. 解密关键字符串
    decrypt_api_strings();
    decrypt_config_strings();
    decrypt_url_strings();

    // 3. 标记初始化完成
    string_obfuscation_initialized = true;
}

// 字符串解密函数
void decrypt_api_strings() {
    for (int i = 0; i < API_STRING_COUNT; i++) {
        decrypt_string_xor(encrypted_api_names[i],
                          decrypted_api_names[i],
                          API_XOR_KEY);
    }
}

// XOR 解密实现
void decrypt_string_xor(const char* encrypted, char* decrypted, uint8_t key) {
    int len = strlen(encrypted);
    for (int i = 0; i < len; i++) {
        decrypted[i] = encrypted[i] ^ key;
    }
    decrypted[len] = '\0';
}
```

### 逆向分析对策

#### 静态分析方法

```python
# Python 脚本分析 .init_array section
from elftools.elf.elffile import ELFFile

def analyze_init_array(so_path):
    with open(so_path, 'rb') as f:
        elf = ELFFile(f)

        # 查找 .init_array section
        init_array_section = elf.get_section_by_name('.init_array')
        if init_array_section:
            data = init_array_section.data()

            print(f"[+] Found .init_array section, size: {len(data)} bytes")

            # 解析函数指针（8 字节对齐，64 位系统）
            for i in range(0, len(data), 8):
                if i + 8 <= len(data):
                    func_addr = int.from_bytes(data[i:i+8], 'little')
                    print(f"[+] Init function {i//8}: 0x{func_addr:x}")

if __name__ == "__main__":
    analyze_init_array("libtarget.so")
```

#### 动态分析方法

```javascript
// Frida 脚本 Hook init_array 执行
function hookInitArray() {
    // Hook 构造函数调用函数
    var call_constructors = Module.findExportByName(
        "linker64",
        "_ZN6soinfo17call_constructorsEv"
    );

    if (call_constructors) {
        Interceptor.attach(call_constructors, {
            onEnter: function(args) {
                var soinfo = args[0];
                console.log("[+] Calling constructors for SO");
                this.start_time = Date.now();
            },
            onLeave: function(retval) {
                var duration = Date.now() - this.start_time;
                console.log("[+] Constructors completed in " + duration + "ms");
            }
        });
    }

    // 直接 hook 目标 SO 的 init_array 函数
    hook_target_init_functions();
}

function hook_target_init_functions() {
    var target_module = Process.findModuleByName("libtarget.so");
    if (target_module) {
        // 根据静态分析结果 hook 特定地址的函数
        var init_func_addr = target_module.base.add(0x2000);  // 示例地址

        Interceptor.attach(init_func_addr, {
            onEnter: function(args) {
                console.log("[!] init_string_obfuscation called");
                console.log("[+] Call stack:");
                console.log(Thread.backtrace(this.context, Backtracer.ACCURATE)
                    .map(DebugSymbol.fromAddress).join("\n"));
            },
            onLeave: function(retval) {
                console.log("[!] init_string_obfuscation completed");
            }
        });
    }
}

// 执行 hook
hookInitArray();
```

#### 分析要点总结

| 特性 | 说明 |
|------|------|
| 执行时机早 | 在 `JNI_OnLoad` 之前执行，难以常规方式 Hook |
| 优先级控制 | 可以通过参数控制多个初始化函数的执行顺序 |
| 静态分析困难 | 加密字符串在静态分析时不可见 |
| 调试时机窗口短 | 执行时间短，难以及时介入 |

---

## 总结

分析 Android `.so` 文件需要掌握以下核心技能：

1. **ELF 格式理解**: 熟悉 ELF 文件结构，特别是关键 section
2. **JNI 机制**: 理解 Java 和 Native 层的交互方式
3. **静态分析**: 使用 IDA Pro / Ghidra 进行反编译分析
4. **动态分析**: 使用 Frida 进行运行时 Hook 和调试
5. **保护绕过**: 了解常见保护手段并掌握绕过方法

通过综合运用这些技术，可以有效地分析和理解 Android 应用的原生代码逻辑。
