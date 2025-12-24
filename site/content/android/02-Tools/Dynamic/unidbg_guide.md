---
title: "Unidbg 模拟执行框架指南"
weight: 10
---

# Unidbg 模拟执行框架指南

Unidbg 是一个基于 Java 开发的、开源的、功能强大的 Android/iOS 原生库 (`.so`/`.dylib`) 模拟执行框架。它能够在 PC (Windows/Linux/macOS) 上模拟一个完整的 ARM 执行环境，使得你可以像调用本地 Java 方法一样直接调用和调试原生库中的函数。这对于分析高度混淆、包含大量环境依赖和反调试机制的原生算法来说，是一个革命性的工具。

---

## 目录

- [核心思想与应用场景](#核心思想与应用场景)
- [Unidbg vs. Frida](#unidbg-vs-frida)
- [环境搭建](#环境搭建)
- [基本使用流程](#基本使用流程)
- [实战技巧](#实战技巧)

---

## 核心思想与应用场景

Unidbg 的核心思想是**"欺骗"**。它通过以下方式让 `.so` 文件认为自己正运行在一个真实的 Android 设备上：

- **模拟文件系统**: 创建一个虚拟的文件系统，你可以将应用的数据、配置文件等放入其中。

- **模拟内存空间**: 加载 `.so` 文件及其依赖的系统库 (如 `libc.so`, `libdl.so`) 到模拟的内存空间中。

- **模拟 JNI 环境**: 实现了大部分 JNI 函数，当 `.so` 文件试图通过 JNI 调用 Java 层代码时，Unidbg 会拦截并可以返回你指定的值。

- **Hook 系统调用 (SVC)**: 拦截底层的系统调用，返回预设的结果。

### 主要应用场景

- **算法复现 (一把梭)**: 直接调用目标加密/解密函数，输入参数并获取返回值，无需费力去逆向算法本身。

- **绕过环境检测**: 目标函数可能包含对 Root、模拟器、设备 ID 等的检测。Unidbg 可以轻松 Hook 这些检测点，让它们全部失效。

- **绕过反调试**: `ptrace` 等反调试手段在 Unidbg 的模拟环境中天然无效。

- **批量计算/爆破**: 编写脚本，批量调用目标函数，用于参数的爆破或生成大量签名。

- **主动调用非导出函数**: 与 Frida 不同，只要知道函数偏移，就可以直接调用任何函数，无论它是否被导出。

---

## Unidbg vs. Frida

| 特性         | Unidbg                                 | Frida                                        |
| :----------- | :------------------------------------- | :------------------------------------------- |
| **执行环境** | **PC 端 (模拟执行)**                   | **移动设备端 (真机/模拟器)**                 |
| **工作模式** | 将 `.so` 当作一个"黑盒"库来调用        | 侵入正在运行的应用进程进行 Hook              |
| **依赖**     | 仅需要 `.so` 文件及其依赖的库          | 需要一个完整的、能运行的 APK                 |
| **反调试**   | **天然免疫**                           | 需要编写脚本来对抗反调试                     |
| **环境依赖** | 需要手动模拟或 Hook                    | 运行在真实环境中，无需模拟                   |
| **性能**     | 较低 (因为是全模拟)                    | 较高 (代码在设备上原生运行)                  |
| **适用性**   | 适合纯算法分析，不涉及 UI 和复杂业务流 | 适合分析与 Android 系统、UI 强相关的业务逻辑 |

---

## 环境搭建

1. **JDK**: 确保已安装 JDK 8 或更高版本。
2. **Maven**: 用于项目构建和依赖管理。
3. **IDE**: 推荐使用 IntelliJ IDEA。
4. **下载 Unidbg**: 从其 GitHub Release 页面下载最新的发行版 `unidbg-dist.zip`，或直接使用 Maven 依赖。
5. **创建 Maven 项目**: 在 IDE 中创建一个新的 Maven 项目，并在 `pom.xml` 中添加 Unidbg 的依赖：

```xml
<dependency>
    <groupId>com.github.unidbg</groupId>
    <artifactId>unidbg-android</artifactId>
    <version>0.9.7</version> <!-- Use latest version -->
</dependency>
```

---

## 基本使用流程

以下是一个调用 `.so` 中简单函数的典型代码结构：

```java
import com.github.unidbg.AndroidEmulator;
import com.github.unidbg.Module;
import com.github.unidbg.linux.android.AndroidEmulatorBuilder;
import com.github.unidbg.linux.android.AndroidResolver;
import com.github.unidbg.linux.android.dvm.*;
import com.github.unidbg.memory.Memory;

import java.io.File;

public class MyTest extends DvmObject<String> {

    private final AndroidEmulator emulator;
    private final Module module;
    private final VM vm;

    public MyTest() {
        // 1. Create emulator instance
        emulator = AndroidEmulatorBuilder.for32Bit().build();
        final Memory memory = emulator.getMemory();
        // 2. Set system library resolver
        memory.setLibraryResolver(new AndroidResolver(23)); // API 23

        // 3. Create virtual machine instance (DVM)
        vm = emulator.createDalvikVM(new File("target/classes/apk/app-debug.apk"));
        vm.setVerbose(true); // Print detailed logs

        // 4. Load target .so
        DalvikModule dm = vm.loadLibrary(new File("target/classes/so/libnative-lib.so"), true);
        module = dm.getModule();

        // 5. Call JNI_OnLoad (optional but recommended)
        dm.callJNI_OnLoad(emulator);
    }

    public void callNativeFunc() {
        // 6. Call target function
        Number result = module.callFunction(emulator, 0x1234, "hello unidbg")[0];
        System.out.println("Result: " + result.intValue());
    }

    public static void main(String[] args) {
        MyTest test = new MyTest();
        test.callNativeFunc();
        test.emulator.close();
    }
}
```

### 核心概念

- **`VM`**: 虚拟机，可以是 `DalvikVM` (DVM) 或 `ART`。负责管理 Java 对象 (`DvmObject`) 和 JNI 调用。

- **`Module`**: 代表一个已加载到内存中的 `.so` 模块。
  - `callFunction(emulator, address, args...)`: **核心方法**，通过绝对地址或偏移调用函数。
  - `findSymbolByName("...")`: 按名称查找导出函数。

- **`DvmObject`**: Java 对象的代理。Unidbg 使用它来向 native 函数传递字符串、字节数组等。

- **`AbstractJni`**: 如果 `.so` 中有复杂的 JNI 回调，你需要继承 `AbstractJni` 并重写对应的方法，以模拟 Java 层的行为。

- **Hooking**: Unidbg 使用 `com.github.unidbg.hook.Hooker` 接口和 `TraceHook` 等工具来提供类似 Frida 的 Hooking 能力，可以监控指令、内存读写等。

---

## 实战技巧

### 补环境

如果 `.so` 依赖特定的设备信息或文件，你需要：

- 在虚拟文件系统中创建对应的文件和内容。
- Hook `open`, `read`, `access` 等 libc 函数，返回预期的结果。
- Hook JNI 调用，如 `getSystemService`，返回一个模拟的 `TelephonyManager` 对象。

### 定位函数地址

函数地址是 `基地址 (module.base) + 偏移`。偏移可以从 IDA/Ghidra 中获得。

### 设置断点

使用 `emulator.attach().addBreakPoint(address, ...)` 可以在指定地址设置断点，进行调试。

### 日志分析

`vm.setVerbose(true)` 会打印非常详细的 JNI 调用和 SVC 日志，这是解决环境问题的关键。

### 参考官方测试用例

Unidbg 项目的 `unidbg-android/src/test/java` 目录下有大量针对主流 App 的测试用例，是学习 Unidbg 的最佳资料。
