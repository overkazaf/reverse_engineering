---
title: "Unidbg 实现原理剖析"
date: 2024-07-11
type: posts
tags: ["Native层", "动态分析", "Frida", "加密分析", "Xposed", "Android"]
weight: 10
---

# Unidbg 实现原理剖析

Unidbg 是一个强大的 Android 原生库 (`.so`) 模拟执行框架。理解其内部工作原理——CPU 模拟、内存管理、ELF 加载、JNI 桥接和系统调用仿真——可以帮助我们更高效地解决复杂的加密算法逆向和协议分析问题。

## 架构概览

### 核心思想

Unidbg 的核心思想是：**用纯 Java 在 PC 上构建一个虚拟的 Android 用户态 (User-Mode) 环境**。它不是完整的操作系统模拟器，而是专注于模拟一个 Android _进程_ 所需的一切，让 `.so` 文件"感觉"自己正运行在真实的 Android 设备里。

### 整体架构

```text
+================================================================+
|                    用户代码 (Java)                               |
|    MyEmulator extends AbstractJni                               |
+================================================================+
          |                    ^                    |
          | 调用函数           | JNI 回调           | IO 请求
          v                    |                    v
+================================================================+
|                    Unidbg 核心层                                |
|  +------------------+  +-----------------+  +-----------------+ |
|  | DalvikVM / ART   |  | SyscallHandler  |  | IOResolver      | |
|  | (JNI 模拟层)     |  | (系统调用处理)  |  | (文件系统模拟)  | |
|  +------------------+  +-----------------+  +-----------------+ |
|  +------------------+  +-----------------+  +-----------------+ |
|  | ELF Loader       |  | Memory Manager  |  | Hook Engine     | |
|  | (动态链接器)     |  | (内存管理)      |  | (HookZz/xHook)  | |
|  +------------------+  +-----------------+  +-----------------+ |
+================================================================+
          |                    ^
          | 指令执行           | 中断/回调
          v                    |
+================================================================+
|                    CPU 后端 (Backend)                            |
|  +------------------+  +-----------------+  +-----------------+ |
|  | Unicorn Engine   |  | Dynarmic        |  | KVM             | |
|  | (解释执行)       |  | (JIT 编译)      |  | (硬件虚拟化)    | |
|  +------------------+  +-----------------+  +-----------------+ |
+================================================================+
```

### CPU 模拟后端

Unidbg 采用**后端抽象层**设计，将 CPU 模拟能力与上层逻辑解耦。

#### Unicorn Engine

默认后端，基于 QEMU 的 TCG (Tiny Code Generator) 模块：

```text
ARM 二进制指令
     |
     v
+-------------------+
| Unicorn Frontend  |  解码 ARM/ARM64 指令
+-------------------+
     |
     v
+-------------------+
| TCG (中间表示)    |  转换为平台无关的中间码 (IR)
+-------------------+
     |
     v
+-------------------+
| Host Code Gen     |  转换为宿主机 (x86/ARM64) 本地指令
+-------------------+
     |
     v
     执行
```

| 特性       | 说明                                          |
| :--------- | :-------------------------------------------- |
| 多架构支持 | ARM, ARM64, MIPS, x86, x86_64, SPARC, M68K   |
| 执行粒度   | 逐基本块 (Basic Block) 翻译执行              |
| 回调机制   | 支持代码执行、内存访问、中断等事件回调        |
| 线程安全   | 单个 `uc_engine` 实例不是线程安全的           |

#### Dynarmic

高性能 ARM JIT 编译器，原为 Nintendo 3DS/Switch 模拟器开发。直接生成宿主机原生代码，无解释开销。

| 操作             | Unicorn  | Dynarmic | 加速比 |
| :--------------- | :------- | :------- | :----- |
| AES-128 加密 1KB | ~0.8ms   | ~0.1ms   | ~8x    |
| 典型 sign() 调用 | ~15ms    | ~2ms     | ~7.5x  |
| 初始化加载       | ~400ms   | ~500ms   | 0.8x   |

#### Backend 接口设计

```java
public interface Backend {
    Number reg_read(int regId);
    void reg_write(int regId, Number value);
    void mem_map(long address, long size, int perms);
    void mem_write(long address, byte[] bytes);
    byte[] mem_read(long address, long size);
    void emu_start(long begin, long until, long timeout, long count);
    void emu_stop();
    void hook_add_new(CodeHook callback, long begin, long end, Object user);
    void hook_add_new(InterruptHook callback, Object user);
}
```

切换后端只需修改一行代码：

```java
AndroidEmulator emulator = AndroidEmulatorBuilder.for32Bit()
        .addBackendFactory(new DynarmicFactory(true))   // Dynarmic
        // .addBackendFactory(new Unicorn2Factory(true)) // Unicorn
        .build();
```

---

## 内存模型

### 虚拟地址空间布局 (32 位)

```text
0xFFFFFFFF  +---------------------------+
            |   Kernel Space (不可用)   |
0xC0000000  +---------------------------+
            |       Stack               |  <-- 向下增长 (默认 128KB)
            |           |               |
            |           v               |
0xBFF00000  +---------------------------+
            |       (未映射区域)        |
            +---------------------------+
            |       mmap 区域           |  <-- 动态库加载区
            |   (libc.so, libm.so等)    |
0x40000000  +---------------------------+
            |       目标 SO 加载区域    |  <-- libnative.so
            +---------------------------+
            |       Heap                |  <-- 向上增长 (malloc)
0x08000000  +---------------------------+
            |       低地址保留区域      |  <-- JNI 函数表、特殊映射
0x00000000  +---------------------------+
```

### mmap 实现

```java
// 简化的 mmap 流程
public long mmap2(long addr, int length, int prot, int flags, int fd, int offset) {
    // 1. 匿名映射：从 mmap 区域分配空闲地址
    if (addr == 0) addr = allocateMapAddress(length);

    // 2. 对齐到页边界 (4KB)
    long alignedAddr = addr & ~0xFFF;
    int alignedLength = (int)(((addr + length + 0xFFF) & ~0xFFF) - alignedAddr);

    // 3. 在 Backend 引擎中创建映射
    backend.mem_map(alignedAddr, alignedLength, prot);

    // 4. 文件映射：读取文件内容到映射区域
    if (fd > 0 && (flags & MAP_ANONYMOUS) == 0) {
        byte[] data = readFromFileDescriptor(fd, offset, length);
        backend.mem_write(addr, data);
    }

    // 5. 记录映射信息
    memoryMap.put(alignedAddr, new MemoryBlock(alignedAddr, alignedLength, prot));
    return addr;
}
```

### 栈与调用约定

ARM32 调用约定中，前 4 个参数通过 `r0-r3` 传递，多余参数通过栈传递。Unidbg 在调用函数时需要正确设置这些：

```java
// 函数调用的简化流程
public Number[] callFunction(long address, Object... args) {
    // 1. 保存 CPU 状态
    long savedSP = backend.reg_read(UC_ARM_REG_SP).longValue();

    // 2. 设置参数
    for (int i = 0; i < args.length; i++) {
        long value = resolveArg(args[i]);
        if (i < 4) {
            backend.reg_write(UC_ARM_REG_R0 + i, value);  // r0-r3
        } else {
            long sp = backend.reg_read(UC_ARM_REG_SP).longValue() - 4;
            backend.mem_write(sp, toBytes(value));          // 压栈
            backend.reg_write(UC_ARM_REG_SP, sp);
        }
    }

    // 3. 设置 LR 为哨兵地址，开始执行
    backend.reg_write(UC_ARM_REG_LR, LR_SENTINEL);
    backend.emu_start(address, LR_SENTINEL, 0, 0);

    // 4. 从 r0 读取返回值，恢复栈
    Number result = backend.reg_read(UC_ARM_REG_R0);
    backend.reg_write(UC_ARM_REG_SP, savedSP);
    return new Number[] { result };
}
```

### 堆管理

Unidbg 内置简单的堆分配器处理 `malloc` / `free`：

```text
+---------------------------+  堆起始地址
| Block Header (8B)         |
|   size=64, used=true      |
+---------------------------+
| 用户数据 (64B)            |  <-- malloc(64) 返回
+---------------------------+
| Block Header (8B)         |
|   size=128, used=false    |
+---------------------------+
| 空闲区域 (128B)           |  <-- 已 free
+---------------------------+
| Block Header (8B)         |
|   size=256, used=true     |
+---------------------------+
| 用户数据 (256B)           |  <-- malloc(256) 返回
+---------------------------+
```

---

## ELF 加载器

### ELF 文件结构

```text
+---------------------------+
| ELF Header                |  魔数、架构、入口点
+---------------------------+
| Program Headers           |
|   PT_LOAD (代码段)        |  .text, .rodata
|   PT_LOAD (数据段)        |  .data, .bss
|   PT_DYNAMIC              |  动态链接信息
+---------------------------+
| Section Headers           |
|   .dynsym                 |  动态符号表
|   .dynstr                 |  动态字符串表
|   .rel.plt / .rela.plt    |  PLT 重定位条目
|   .rel.dyn / .rela.dyn    |  数据重定位条目
|   .init_array             |  构造函数指针数组
+---------------------------+
```

### 加载流程

```text
vm.loadLibrary("libnative.so")
         |
         v
  1. 解析 ELF 头，验证架构匹配 (ARM/ARM64)
         |
         v
  2. 遍历 PT_LOAD 段，计算需要的虚拟地址范围
         |
         v
  3. 在 mmap 区域预留连续空间 (基址通常从 0x40000000 起)
         |
         v
  4. 将 PT_LOAD 段内容写入虚拟内存，设置权限 (R/W/X)
         |
         v
  5. 解析 PT_DYNAMIC 段，提取 DT_NEEDED 依赖库列表
         |
         v
  6. 递归加载依赖库 (Unidbg 自带常用系统库)
         |
         v
  7. 符号解析与重定位 (填充 GOT 表)
         |
         v
  8. 执行 .init 段和 .init_array 中的构造函数
         |
         v
  9. 返回 Module 对象 (包含基地址、符号表等)
```

### PLT/GOT 重定位

```asm
调用外部函数 (如 strlen) 的过程:

.text 段:
  BL strlen@PLT          ; 跳转到 PLT 桩代码

.plt 段:
  strlen@PLT:
    LDR PC, [PC, #offset] ; 从 GOT 表读取地址并跳转

.got 段:
  &strlen = 0x????????    ; 重定位前: 指向延迟绑定桩
         = 0x400023A0    ; 重定位后: 指向 strlen 真实地址
```

Unidbg 的重定位处理核心逻辑：

```java
private void processRelocation(ElfRelocation rel, Module module) {
    int type = rel.type();
    ElfSymbol symbol = rel.symbol();
    long targetAddr = module.base + rel.offset();

    switch (type) {
        case R_ARM_JUMP_SLOT:    // PLT 重定位
        case R_ARM_GLOB_DAT:     // 全局数据重定位
            long symbolAddr = resolveSymbol(symbol.getName());
            if (symbolAddr != 0) {
                backend.mem_write(targetAddr, toBytes((int) symbolAddr));
            }
            break;

        case R_ARM_RELATIVE:     // 相对重定位：加上基地址
            int origValue = readInt(targetAddr);
            backend.mem_write(targetAddr, toBytes(origValue + (int) module.base));
            break;
    }
}
```

### 自带的系统库

| 库名           | 用途         | 实现方式                  |
| :------------- | :----------- | :------------------------ |
| `libc.so`      | C 标准库     | 部分函数用 Java 实现      |
| `libdl.so`     | 动态链接     | Java 实现 dlopen/dlsym    |
| `libm.so`      | 数学库       | 直接使用 Java Math        |
| `libstdc++.so` | C++ 标准库   | 部分实现                  |
| `liblog.so`    | Android 日志 | 输出到 Java 控制台        |
| `libz.so`      | zlib 压缩    | 使用 Java 自带的 zlib     |

> 对于未内置的库 (如 `libcrypto.so`)，需要从真机 `/system/lib/` 提取并手动加载。

---

## JNI 桥接层

### JNI 函数表机制

在真实 Android 中，`JNIEnv*` 指向一个函数指针表。Unidbg 需要在模拟环境中实现等效机制：

```text
真实 Android:
  JNIEnv* --> | GetVersion       | --> 原生函数指针
              | FindClass        | --> 原生函数指针
              | GetMethodID      | --> 原生函数指针
              | CallObjectMethod | --> 原生函数指针
              | ...              |

Unidbg 模拟:
  JNIEnv* --> | GetVersion       | --> 跳板代码地址 (触发中断)
              | FindClass        | --> 跳板代码地址 (触发中断)
              | GetMethodID      | --> 跳板代码地址 (触发中断)
              | CallObjectMethod | --> 跳板代码地址 (触发中断)
              | ...              |
```

### 跳板机制 (Trampoline)

Unidbg 使用跳板代码将 SO 对 JNI 函数的调用重定向到 Java 实现：

```text
SO 代码: (*env)->FindClass(env, "java/lang/String")
     |
     v
1. 从 JNIEnv 函数表取出 FindClass 的地址
     |
     v
2. 跳转到跳板代码，执行 SVC #0 (软中断)
     |
     v  (中断被 Unidbg 拦截)
3. InterruptHook 识别出是 FindClass 调用
     |
     v
4. 从寄存器读取参数:
   r0=env, r1=className("java/lang/String")
     |
     v
5. 执行 Java 实现: DalvikVM.findClass()
   返回 DvmClass 对象
     |
     v
6. 将结果的 hash 值写入 r0 (作为 jclass)
     |
     v
7. 恢复模拟器继续执行后续指令
```

### DvmObject 体系

```text
DvmObject<T>                  (所有 Java 对象的基类)
    |
    +-- StringObject          (java.lang.String)
    +-- ByteArray             (byte[])
    +-- IntArray              (int[])
    +-- ArrayObject           (Object[])
    +-- DvmInteger            (java.lang.Integer)
    +-- DvmLong               (java.lang.Long)
    +-- DvmBoolean            (java.lang.Boolean)
```

每个 `DvmObject` 有唯一的 hash 值，在 SO 代码中作为 `jobject` 指针：

```java
public abstract class DvmObject<T> {
    private final int hashCode;        // 作为 jobject 传给 SO
    private final DvmClass objectType; // 对象的类型信息
    private T value;                   // 实际的 Java 值
}

// VM 内部维护对象映射表
// Map<Integer, DvmObject<?>> objectMap
//   hash=0x1001 -> StringObject("hello")
//   hash=0x1002 -> DvmClass(android/content/Context)
```

### CallObjectMethod 完整生命周期

```yaml
SO: jstring result = (*env)->CallObjectMethod(env, obj, methodId, arg1);
     |
     v
1. 从函数表取地址，跳转到跳板，触发 SVC 中断
     |
     v
2. InterruptHook 捕获，识别为 CallObjectMethod
     |
     v
3. 从寄存器读取参数:
   r1=obj -> 通过 hash 查表得到 DvmObject
   r2=methodId -> 查表得到方法签名
     |
     v
4. 构造签名: "android/content/Context->getPackageName()Ljava/lang/String;"
     |
     v
5. 调用 AbstractJni.callObjectMethod()，用户代码匹配并返回结果
     |
     v
6. 返回值注册到对象表，hash 写入 r0，继续执行
```

### RegisterNatives 动态注册

许多加固后的 SO 在 `JNI_OnLoad` 中使用 `RegisterNatives` 动态注册：

```text
SO 中的 JNI_OnLoad:
  env->RegisterNatives(clazz, methods, count)
       |
       v
  Unidbg 拦截，读取 JNINativeMethod 数组:
    name="sign",      sig="(Ljava/lang/String;)Ljava/lang/String;",  fn=0x40001A3C
    name="verify",    sig="(Ljava/lang/String;Z)Z",                  fn=0x400023F0
       |
       v
  保存到 DvmClass 的 nativeMethods 映射:
    签名 -> 函数地址
       |
       v
  后续调用 callJniMethodObject 时，
  根据签名查找函数地址，设置参数并跳转执行
```

---

## 系统调用仿真

### ARM 系统调用机制

ARM 架构通过 `SVC #0` 指令发起系统调用，调用号在 `r7` 中，参数在 `r0-r5` 中：

```asm
MOV  r7, #5          ; syscall number: open = 5
MOV  r0, pathname    ; arg1: 文件路径
MOV  r1, #0          ; arg2: O_RDONLY
SVC  #0              ; 触发系统调用
; 返回值在 r0 中
```

### 处理流程

```text
Unicorn 执行 SVC #0
     |
     v
InterruptHook 回调
     |
     v
读取 r7 (syscall number) + r0-r5 (参数)
     |
     v
SyscallHandler.handle()
     |
     +-- 已实现 --> 执行 Java 实现，写返回值到 r0
     +-- 未实现 --> 抛异常或返回 -ENOSYS
```

### 已实现的关键系统调用

| 编号 | 名称            | 用途             | 实现方式                     |
| :--- | :-------------- | :--------------- | :--------------------------- |
| 3    | `read`          | 读取文件         | Java FileInputStream         |
| 4    | `write`         | 写入文件         | Java FileOutputStream        |
| 5    | `open`          | 打开文件         | IOResolver + 虚拟文件系统    |
| 6    | `close`         | 关闭文件         | 关闭 Java 流                 |
| 26   | `ptrace`        | 调试相关         | 返回 -EPERM (反调试免疫)     |
| 45   | `brk`           | 扩展堆           | 调整堆结束地址               |
| 125  | `mprotect`      | 修改内存权限     | 更新 Backend 内存权限        |
| 192  | `mmap2`         | 内存映射         | 分配虚拟地址+Backend映射     |
| 197  | `fstat64`       | 文件状态         | Java File 属性               |
| 240  | `futex`         | 互斥锁           | 简单实现 (单线程)            |
| 263  | `clock_gettime` | 获取时钟         | Java System.nanoTime         |
| 322  | `openat`        | 打开文件(相对路径)| 与 open 类似                 |

### Android Property 系统

`__system_property_get` 不是系统调用，而是通过共享内存实现。Unidbg 通过 Hook `libc.so` 中的该函数来处理：

```java
public int __system_property_get(Emulator<?> emulator) {
    Pointer namePtr = UnidbgPointer.register(emulator, UC_ARM_REG_R0);
    Pointer valuePtr = UnidbgPointer.register(emulator, UC_ARM_REG_R1);
    String name = namePtr.getString(0);

    String value;
    switch (name) {
        case "ro.build.version.sdk":  value = "23";       break;
        case "ro.product.model":      value = "Pixel 2";  break;
        case "ro.debuggable":         value = "0";         break;
        default:                      value = "";          break;
    }
    valuePtr.setString(0, value);
    return value.length();
}
```

### 文件描述符管理

```text
虚拟文件描述符表:
+------+---------------+-----------------------------------+
|  FD  | 类型          | 实际映射                          |
+------+---------------+-----------------------------------+
|  0   | STDIN         | Java System.in                    |
|  1   | STDOUT        | Java System.out                   |
|  2   | STDERR        | Java System.err                   |
|  3   | Regular File  | /proc/self/maps -> 虚拟内容       |
|  4   | Regular File  | /proc/self/status -> 虚拟内容     |
|  5   | Regular File  | /data/app/xxx/base.apk -> 真实文件|
+------+---------------+-----------------------------------+
```

---

## 与 Unicorn/Qiling 对比

### 三者定位

```text
  高层  +-- Unidbg ---+   专注 Android SO 模拟
        |             |   内置 JNI/DVM/Android 文件系统
        +-------------+

  中层  +-- Qiling ---+   通用 OS 模拟框架
        |             |   支持 Linux/Windows/macOS
        +-------------+

  底层  +-- Unicorn --+   纯 CPU 模拟引擎
        |             |   仅提供指令执行和内存管理
        +-------------+
```

### 详细对比

| 维度             | Unidbg               | Unicorn              | Qiling               |
| :--------------- | :-------------------- | :------------------- | :-------------------- |
| **开发语言**     | Java                  | C (多语言绑定)       | Python                |
| **定位**         | Android SO 模拟       | 通用 CPU 模拟引擎    | OS 级模拟框架         |
| **JNI 支持**     | 内置完整实现          | 无                   | 无                    |
| **DVM/ART**      | 内置                  | 无                   | 无                    |
| **Android 系统库** | 自带精简版          | 无                   | 部分支持              |
| **Linux syscall** | 针对 Android 优化    | 无                   | 通用 Linux 实现       |
| **Windows 支持** | 不支持                | 仅 CPU 层面          | 完整支持              |
| **ELF/PE 加载**  | ELF 内置              | 需自行实现           | 两者内置              |
| **Hook 框架**    | HookZz, xHook         | 需手动实现           | 内置                  |
| **多线程**       | 有限支持              | 不支持               | 有限支持              |
| **性能**         | 较高 (Dynarmic)       | 中等                 | 较低 (Python 开销)    |

### 代码风格对比

同样的功能——加载 SO 并调用函数：

**Unicorn (Python) — 需要手动处理一切**:
```python
mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
mu.mem_map(0x10000, 0x10000)
mu.mem_write(0x10000, so_code_bytes)
mu.reg_write(UC_ARM_REG_SP, 0x20000)
mu.reg_write(UC_ARM_REG_R0, arg0)
mu.hook_add(UC_HOOK_INTR, hook_intr)
mu.emu_start(0x10000 + offset, 0x10000 + end)
# 需要自己实现 ELF 解析、重定位、JNI、syscall...
```

**Qiling (Python) — 有 OS 抽象，但没有 JNI**:
```python
ql = Qiling(["rootfs/lib/libnative.so"], rootfs="rootfs",
            ostype="linux", archtype="arm")
ql.run()
# 没有 JNI/DVM 支持，Android SO 需要大量额外工作
```

**Unidbg (Java) — Android 开箱即用**:
```java
AndroidEmulator emulator = AndroidEmulatorBuilder.for32Bit().build();
emulator.getMemory().setLibraryResolver(new AndroidResolver(23));
VM vm = emulator.createDalvikVM(new File("app.apk"));
vm.setJni(this);
DalvikModule dm = vm.loadLibrary("native", true);
dm.callJNI_OnLoad(emulator);
// JNI 调用一步到位
DvmObject<?> result = dvmClass.callStaticJniMethodObject(emulator,
    "sign(Ljava/lang/String;)Ljava/lang/String;",
    new StringObject(vm, input));
```

### 选择建议

| 目标场景                         | 推荐工具              |
| :------------------------------- | :-------------------- |
| Android SO 加密算法分析          | Unidbg                |
| Windows PE 算法分析              | Qiling                |
| 构建自定义模拟/分析工具          | Unicorn               |
| IoT 嵌入式固件模拟               | Qiling                |
| 高性能批量调用                   | Unidbg + Dynarmic     |

---

## 优势与局限

### 优势

| 优势           | 说明                                                    |
| :------------- | :------------------------------------------------------ |
| 摆脱环境限制   | 无需真机或模拟器，无 root 要求                          |
| 高可控性       | 完全控制执行流程，任意修改内存和寄存器                  |
| 自动化集成     | 易于与 Java/Python 项目集成，支持大规模自动化           |
| 反反调试       | 没有 `ptrace` 进程，绕过大多数反调试检测                |
| 可重复性       | 相同输入始终产生相同输出                                |

### 局限

| 局限           | 说明                                                    |
| :------------- | :------------------------------------------------------ |
| 环境不完整     | 非 100% Android 环境，强依赖系统/硬件特性的 SO 可能失败 |
| 性能开销       | 逐条指令模拟，性能低于原生 (Dynarmic 有显著改善)        |
| 覆盖度有限     | 未实现的 syscall/JNI 需要手动补充                       |
| 多线程局限     | 对 SO 内部创建线程的支持有限                            |
| 时间敏感       | 模拟速度不一致，依赖精确时间的代码可能产生不同结果      |

### 适用性判断

```text
+-----------------------------------+-----------------------------------+
|         适合使用 Unidbg           |        不适合使用 Unidbg          |
+-----------------------------------+-----------------------------------+
| 纯算法分析 (sign/encrypt/hash)   | 涉及 UI 渲染的功能               |
| 需要绕过强反调试                  | 重度依赖 Binder IPC              |
| 批量调用生成签名                  | 需要实时网络通信                  |
| 对抗混淆后的算法还原              | 多线程密集型 SO                   |
| 无真机环境的离线分析              | 依赖硬件特性 (GPU/传感器)        |
+-----------------------------------+-----------------------------------+
```
