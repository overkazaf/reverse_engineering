---
title: "Unidbg 模拟执行框架指南"
date: 2024-06-09
type: posts
tags: ["Native层", "动态分析", "签名验证", "Frida", "代理池", "Ghidra"]
weight: 10
---

# Unidbg 模拟执行框架指南

Unidbg 是一个基于 Java 开发的 Android/iOS 原生库 (`.so`/`.dylib`) 模拟执行框架。它能够在 PC 上模拟完整的 ARM 执行环境，使你可以像调用本地 Java 方法一样直接调用和调试原生库中的函数。

---

## 核心思想与应用场景

Unidbg 的核心思想是**"欺骗"**——让 `.so` 文件认为自己正运行在一个真实的 Android 设备上：

- **模拟文件系统**: 创建虚拟文件系统，放入应用的数据和配置文件
- **模拟内存空间**: 加载 `.so` 及其依赖的系统库到模拟内存中
- **模拟 JNI 环境**: 实现大部分 JNI 函数，拦截 `.so` 对 Java 层的调用
- **Hook 系统调用 (SVC)**: 拦截底层系统调用，返回预设结果

### 主要应用场景

| 场景 | 说明 |
|:-----|:-----|
| 算法复现 | 直接调用加密/解密函数，无需逆向算法本身 |
| 绕过环境检测 | Hook Root、模拟器、设备 ID 等检测点 |
| 绕过反调试 | `ptrace` 等反调试手段在模拟环境中天然无效 |
| 批量计算 | 编写脚本批量调用目标函数，爆破参数或生成签名 |
| 调用非导出函数 | 只要知道偏移就可以直接调用任何函数 |

---

## Unidbg vs. Frida

| 特性         | Unidbg                                 | Frida                                        |
| :----------- | :------------------------------------- | :------------------------------------------- |
| **执行环境** | PC 端 (模拟执行)                       | 移动设备端 (真机/模拟器)                     |
| **工作模式** | 将 `.so` 当作黑盒库来调用              | 侵入正在运行的应用进程进行 Hook              |
| **依赖**     | 仅需要 `.so` 文件及其依赖库            | 需要一个完整的、能运行的 APK                 |
| **反调试**   | **天然免疫**                           | 需要编写脚本来对抗反调试                     |
| **性能**     | 较低 (全模拟)                          | 较高 (代码在设备上原生运行)                  |
| **适用性**   | 适合纯算法分析                         | 适合分析与系统、UI 强相关的逻辑             |

---

## 环境搭建

### Maven 项目配置

```xml
<project>
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>unidbg-demo</artifactId>
    <version>1.0-SNAPSHOT</version>

    <properties>
        <maven.compiler.source>8</maven.compiler.source>
        <maven.compiler.target>8</maven.compiler.target>
        <unidbg.version>0.9.7</unidbg.version>
    </properties>

    <repositories>
        <repository>
            <id>jitpack.io</id>
            <url>https://jitpack.io</url>
        </repository>
    </repositories>

    <dependencies>
        <dependency>
            <groupId>com.github.zhkl0228</groupId>
            <artifactId>unidbg-android</artifactId>
            <version>${unidbg.version}</version>
        </dependency>
        <dependency>
            <groupId>com.github.zhkl0228</groupId>
            <artifactId>unidbg-api</artifactId>
            <version>${unidbg.version}</version>
        </dependency>
        <dependency>
            <groupId>commons-logging</groupId>
            <artifactId>commons-logging</artifactId>
            <version>1.2</version>
        </dependency>
    </dependencies>
</project>
```

### Gradle 配置

```groovy
repositories {
    mavenCentral()
    maven { url 'https://jitpack.io' }
}
dependencies {
    implementation 'com.github.zhkl0228:unidbg-android:0.9.7'
    implementation 'com.github.zhkl0228:unidbg-api:0.9.7'
}
```

### 推荐项目结构

```text
unidbg-demo/
├── pom.xml
├── src/main/
│   ├── java/com/example/demo/
│   │   ├── SignEmulator.java        <-- 模拟器主类
│   │   └── AbstractApp.java        <-- 公共基类
│   └── resources/
│       ├── apk/target-app.apk      <-- 目标 APK
│       └── so/libnative-lib.so     <-- 目标 SO
└── target/rootfs/default/           <-- 虚拟文件系统
    └── proc/self/maps
```

---

## 基本使用流程

### 完整代码模板

```java
import com.github.unidbg.AndroidEmulator;
import com.github.unidbg.Module;
import com.github.unidbg.linux.android.AndroidEmulatorBuilder;
import com.github.unidbg.linux.android.AndroidResolver;
import com.github.unidbg.linux.android.dvm.*;
import com.github.unidbg.memory.Memory;
import java.io.File;

public class MyEmulator extends AbstractJni {

    private final AndroidEmulator emulator;
    private final Module module;
    private final VM vm;

    public MyEmulator() {
        // 1. 创建模拟器 (for32Bit=armeabi-v7a, for64Bit=arm64-v8a)
        emulator = AndroidEmulatorBuilder
                .for32Bit()
                .setProcessName("com.example.target")
                .build();

        // 2. 初始化内存，设置 API 级别 (23=Android 6.0)
        final Memory memory = emulator.getMemory();
        memory.setLibraryResolver(new AndroidResolver(23));

        // 3. 创建 DVM，传入 APK 以自动解析 classes.dex
        vm = emulator.createDalvikVM(new File("src/main/resources/apk/target.apk"));
        vm.setJni(this);
        vm.setVerbose(true);

        // 4. 加载目标 SO (true = 执行 .init 和 .init_array)
        DalvikModule dm = vm.loadLibrary(
                new File("src/main/resources/so/libnative-lib.so"), true);
        module = dm.getModule();

        // 5. 调用 JNI_OnLoad (触发动态注册)
        dm.callJNI_OnLoad(emulator);
    }

    // 方式一：通过导出符号名调用
    public String callBySymbol(String input) {
        DvmObject<?> context = vm.resolveClass("android/content/Context").newObject(null);
        DvmObject<?> result = vm.callJniMethod(emulator,
                "Java_com_example_NativeLib_sign(Landroid/content/Context;Ljava/lang/String;)Ljava/lang/String;",
                context, new StringObject(vm, input));
        return result.getValue().toString();
    }

    // 方式二：通过偏移地址调用 (偏移从 IDA/Ghidra 获取)
    public int callByOffset(int arg1, int arg2) {
        // ARM 模式地址不变，Thumb 模式地址需要 +1
        Number[] result = module.callFunction(emulator, 0x1A3C, arg1, arg2);
        return result[0].intValue();
    }

    // 方式三：通过 DvmClass 调用 JNI 静态方法
    public String callByDvmClass(String input) {
        DvmClass dvmClass = vm.resolveClass("com/example/NativeLib");
        DvmObject<?> result = dvmClass.callStaticJniMethodObject(emulator,
                "getSign(Ljava/lang/String;)Ljava/lang/String;",
                new StringObject(vm, input));
        return result != null ? result.getValue().toString() : null;
    }

    public static void main(String[] args) {
        MyEmulator emu = new MyEmulator();
        System.out.println("Result: " + emu.callBySymbol("test_data"));
        emu.emulator.close();
    }
}
```

> **提示**: 如果目标 APK 同时包含 `armeabi-v7a` 和 `arm64-v8a`，优先尝试 32 位，模拟更成熟稳定。

---

## JNI 环境模拟

当 SO 通过 JNI 回调 Java 层代码时，需要在 `AbstractJni` 子类中手动实现这些回调。

### 方法重写示例

```java
public class MyEmulator extends AbstractJni {

    @Override
    public DvmObject<?> callObjectMethod(BaseVM vm, DvmObject<?> dvmObject,
                                          String signature, VarArg varArg) {
        switch (signature) {
            case "android/content/Context->getPackageName()Ljava/lang/String;":
                return new StringObject(vm, "com.example.target");

            case "android/content/Context->getSharedPreferences(Ljava/lang/String;I)Landroid/content/SharedPreferences;":
                return vm.resolveClass("android/content/SharedPreferences").newObject(null);

            case "android/content/SharedPreferences->getString(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;":
                String key = varArg.getObjectArg(0).getValue().toString();
                return new StringObject(vm, "device_id".equals(key) ? "abc123" : "");
        }
        return super.callObjectMethod(vm, dvmObject, signature, varArg);
    }

    @Override
    public DvmObject<?> callStaticObjectMethod(BaseVM vm, DvmClass dvmClass,
                                                String signature, VarArg varArg) {
        switch (signature) {
            case "android/util/Base64->encodeToString([BI)Ljava/lang/String;":
                byte[] data = (byte[]) varArg.getObjectArg(0).getValue();
                return new StringObject(vm,
                        java.util.Base64.getEncoder().encodeToString(data));
        }
        return super.callStaticObjectMethod(vm, dvmClass, signature, varArg);
    }

    @Override
    public int callIntMethod(BaseVM vm, DvmObject<?> dvmObject,
                             String signature, VarArg varArg) {
        if ("java/lang/String->length()I".equals(signature)) {
            return dvmObject.getValue().toString().length();
        }
        return super.callIntMethod(vm, dvmObject, signature, varArg);
    }

    @Override
    public DvmObject<?> getObjectField(BaseVM vm, DvmObject<?> dvmObject,
                                        String signature) {
        switch (signature) {
            case "android/content/pm/PackageInfo->signatures:[Landroid/content/pm/Signature;":
                DvmObject<?> sig = vm.resolveClass("android/content/pm/Signature")
                        .newObject("fake_signature_hex");
                return new ArrayObject(sig);
        }
        return super.getObjectField(vm, dvmObject, signature);
    }

    @Override
    public int getStaticIntField(BaseVM vm, DvmClass dvmClass, String signature) {
        if ("android/os/Build$VERSION->SDK_INT:I".equals(signature)) return 23;
        return super.getStaticIntField(vm, dvmClass, signature);
    }
}
```

### JNI 签名速查表

| Java 类型    | JNI 签名              | 示例                              |
| :----------- | :-------------------- | :-------------------------------- |
| `void`       | `V`                   | `doSomething()V`                  |
| `boolean`    | `Z`                   | `isValid()Z`                      |
| `int`        | `I`                   | `getCount()I`                     |
| `long`       | `J`                   | `getTimestamp()J`                 |
| `byte[]`     | `[B`                  | `getData()[B`                     |
| `String`     | `Ljava/lang/String;`  | `getName()Ljava/lang/String;`     |
| `int[]`      | `[I`                  | `getIds()[I`                      |

---

## 系统调用处理

### 虚拟文件系统

```java
public class MyEmulator extends AbstractJni implements IOResolver<AndroidFileIO> {

    public MyEmulator() {
        // ... 其他初始化 ...
        emulator.getSyscallHandler().addIOResolver(this);
    }

    @Override
    public FileResult<AndroidFileIO> resolve(Emulator<AndroidFileIO> emulator,
                                              String pathname, int oflags) {
        switch (pathname) {
            case "/proc/self/status":
                // TracerPid=0 表示未被调试（反调试关键）
                return FileResult.success(new ByteArrayFileIO(oflags, pathname,
                    ("Name:\ttarget\nTracerPid:\t0\nUid:\t10086\n").getBytes()));

            case "/system/build.prop":
                return FileResult.success(new ByteArrayFileIO(oflags, pathname,
                    ("ro.product.model=Pixel 2\nro.product.brand=google\n").getBytes()));

            case "/proc/cpuinfo":
                return FileResult.success(new ByteArrayFileIO(oflags, pathname,
                    ("processor\t: 0\nHardware\t: Qualcomm MSM8998\n").getBytes()));
        }
        return null;  // 使用默认处理
    }
}
```

### 系统调用处理流程

```text
+------------------+     +------------------+     +------------------+
| SO 执行代码      |     | Unicorn 引擎     |     | Unidbg Handler   |
|                  |     |                  |     |                  |
|  open("/proc/    | --> | 执行 SVC #0      | --> | SyscallHandler   |
|   self/maps")    |     | 产生中断         |     | .handle()        |
|                  |     |                  |     |                  |
|  <-- fd=3        | <-- | 写入 r0=3        | <-- | IOResolver       |
|                  |     |                  |     | .resolve()       |
+------------------+     +------------------+     +------------------+
```

---

## Hook 功能

### HookZz (Inline Hook)

```java
import com.github.unidbg.hook.hookzz.*;

IHookZz hookZz = HookZz.getInstance(emulator);

hookZz.wrap(module.base + 0x1A3C, new WrapCallback<HookZzArm32RegisterContext>() {
    @Override
    public void preCall(Emulator<?> emulator,
                        HookZzArm32RegisterContext ctx, HookEntryInfo info) {
        int arg0 = ctx.getIntArg(0);
        String arg1 = ctx.getPointerArg(1).getString(0);
        System.out.println("[preCall] arg0=" + arg0 + ", arg1=" + arg1);
        ctx.push(arg1);  // 保存供 postCall 使用
    }

    @Override
    public void postCall(Emulator<?> emulator,
                         HookZzArm32RegisterContext ctx, HookEntryInfo info) {
        int retVal = ctx.getIntArg(0);
        String saved = ctx.pop();
        System.out.println("[postCall] input=" + saved + ", ret=" + retVal);
        ctx.setR0(0);  // 修改返回值
    }
});
```

### xHook (PLT Hook)

```java
import com.github.unidbg.hook.xhook.IxHook;

IxHook xHook = XHookImpl.getInstance(emulator);

// Hook libnative-lib.so 中对 strlen 的调用
xHook.register("libnative-lib.so", "strlen", new ReplaceCallback() {
    @Override
    public HookStatus onCall(Emulator<?> emulator, HookContext context, long originFunction) {
        String str = context.getPointerArg(0).getString(0);
        System.out.println("[xHook] strlen(\"" + str + "\")");
        return HookStatus.RET(emulator, originFunction);  // 调用原函数
    }
});
xHook.refresh();  // 必须调用 refresh 使 Hook 生效
```

### 指令级追踪

```java
// 追踪指定范围内的所有指令
emulator.traceCode(module.base + 0x1000, module.base + 0x2000);

// 监控内存读写
emulator.traceRead(0x40001000, 0x40001100);
emulator.traceWrite(0x40001000, 0x40001100);
```

### Hook 方式对比

| Hook 方式  | 原理         | 适用场景                     | 性能影响 |
| :--------- | :----------- | :--------------------------- | :------- |
| HookZz     | Inline Hook  | Hook 任意地址的函数          | 低       |
| xHook      | PLT/GOT Hook | Hook 导入的外部函数          | 极低     |
| traceCode  | 指令回调     | 追踪执行流、分析算法逻辑    | 高       |
| Breakpoint | 断点中断     | 调试特定位置、检查寄存器状态 | 高       |

---

## 调试与排错

### 常见错误及解决方案

**1. Invalid memory read/write**
```yaml
UnicornException: Invalid memory read (UC_ERR_READ_UNMAPPED) at 0x00000000
```
原因：空指针引用。检查传入参数和 JNI 回调返回值是否有效。

**2. UnsupportedOperationException**
```text
UnsupportedOperationException:
  android/telephony/TelephonyManager->getDeviceId()Ljava/lang/String;
```
原因：未处理的 JNI 回调。在 `callObjectMethod` 等方法中补充对应签名的处理。

**3. 缺少 SO 依赖**
```yaml
FileNotFoundException: resolve library: libcrypto.so failed
```
解决：手动预加载依赖库：
```java
vm.loadLibrary(new File("path/to/libcrypto.so"), false);  // 先加载依赖
vm.loadLibrary(new File("path/to/libtarget.so"), true);   // 再加载目标
```

**4. 系统调用未实现**
```text
Unsupported syscall: 0x14e (334)
```
解决：查找 syscall 编号对应的功能，在 `SyscallHandler` 中补充实现。

### 调试技巧

```java
// 开启详细日志
vm.setVerbose(true);

// 设置断点
Debugger debugger = emulator.attach();
debugger.addBreakPoint(module.base + 0x1A3C, (emu, addr) -> {
    Arm32RegisterContext ctx = emu.getContext();
    System.out.println("R0=0x" + Long.toHexString(ctx.getR0Int()));
    System.out.println("R1=0x" + Long.toHexString(ctx.getR1Int()));
    return true;  // true=继续执行
});

// 内存 Dump
byte[] data = emulator.getBackend().mem_read(address, size);
Inspector.inspect(data, "Memory dump");
```

### 排错流程

```text
SO 执行失败
  +-- JNI 调用未处理？     --> 在 AbstractJni 中补充实现
  +-- 系统调用未实现？     --> 在 SyscallHandler 中补充
  +-- 文件访问失败？       --> 在 IOResolver 中添加文件模拟
  +-- 内存访问错误？       --> 检查参数传递和返回值
  +-- 以上都不是？         --> 开启 traceCode，结合 IDA 定位
```

---

## 实战案例

> **💡 思路一句话**: Unidbg 的核心思路是「在 PC 上模拟 Android 环境调用 SO 函数」— 不需要真机、不需要 root，直接在 Java 代码中加载 SO → 补齐 JNI 环境 → 调用目标函数 → 获取返回值。适合需要大量调用签名函数的场景。

模拟执行某 App 的 `generateSign()` 签名函数的完整流程。

### 目标

```java
// com.example.security.SignUtil (从 Jadx 反编译获得)
public class SignUtil {
    static { System.loadLibrary("security"); }
    public static native String generateSign(Context ctx, String params, long timestamp);
}
```

### 完整实现

```java
public class SignEmulator extends AbstractJni implements IOResolver<AndroidFileIO> {

    private final AndroidEmulator emulator;
    private final VM vm;
    private final DvmClass signUtilClass;

    public SignEmulator() {
        emulator = AndroidEmulatorBuilder.for32Bit()
                .setProcessName("com.example.security")
                .build();
        Memory memory = emulator.getMemory();
        memory.setLibraryResolver(new AndroidResolver(23));
        emulator.getSyscallHandler().addIOResolver(this);

        vm = emulator.createDalvikVM(new File("src/main/resources/apk/target-app.apk"));
        vm.setJni(this);
        vm.setVerbose(true);

        DalvikModule dm = vm.loadLibrary("security", true);
        dm.callJNI_OnLoad(emulator);

        signUtilClass = vm.resolveClass("com/example/security/SignUtil");
    }

    public String generateSign(String params, long timestamp) {
        DvmObject<?> context = vm.resolveClass("android/content/Context").newObject(null);
        DvmObject<?> result = signUtilClass.callStaticJniMethodObject(emulator,
                "generateSign(Landroid/content/Context;Ljava/lang/String;J)Ljava/lang/String;",
                context, new StringObject(vm, params), timestamp);
        return result != null ? result.getValue().toString() : null;
    }

    // ---------- JNI 回调 ----------
    @Override
    public DvmObject<?> callObjectMethod(BaseVM vm, DvmObject<?> dvmObject,
                                          String signature, VarArg varArg) {
        switch (signature) {
            case "android/content/Context->getPackageName()Ljava/lang/String;":
                return new StringObject(vm, "com.example.security");
            case "android/content/Context->getPackageManager()Landroid/content/pm/PackageManager;":
                return vm.resolveClass("android/content/pm/PackageManager").newObject(null);
            case "android/content/pm/PackageManager->getPackageInfo(Ljava/lang/String;I)Landroid/content/pm/PackageInfo;":
                return vm.resolveClass("android/content/pm/PackageInfo").newObject(null);
        }
        return super.callObjectMethod(vm, dvmObject, signature, varArg);
    }

    @Override
    public DvmObject<?> callStaticObjectMethod(BaseVM vm, DvmClass dvmClass,
                                                String signature, VarArg varArg) {
        if (signature.equals("android/provider/Settings$Secure->getString(Landroid/content/ContentResolver;Ljava/lang/String;)Ljava/lang/String;")) {
            return new StringObject(vm, "a1b2c3d4e5f67890");
        }
        return super.callStaticObjectMethod(vm, dvmClass, signature, varArg);
    }

    @Override
    public int callIntMethod(BaseVM vm, DvmObject<?> dvmObject,
                             String signature, VarArg varArg) {
        if ("android/content/pm/Signature->hashCode()I".equals(signature))
            return 0x12345678;  // 从真机获取
        return super.callIntMethod(vm, dvmObject, signature, varArg);
    }

    @Override
    public DvmObject<?> getObjectField(BaseVM vm, DvmObject<?> dvmObject, String signature) {
        if ("android/content/pm/PackageInfo->signatures:[Landroid/content/pm/Signature;".equals(signature)) {
            return new ArrayObject(
                    vm.resolveClass("android/content/pm/Signature").newObject("308201..."));
        }
        return super.getObjectField(vm, dvmObject, signature);
    }

    // ---------- 文件系统 ----------
    @Override
    public FileResult<AndroidFileIO> resolve(Emulator<AndroidFileIO> emulator,
                                              String pathname, int oflags) {
        if ("/proc/self/status".equals(pathname))
            return FileResult.success(new ByteArrayFileIO(oflags, pathname,
                    "Name:\tcom.example.security\nTracerPid:\t0\n".getBytes()));
        return null;
    }

    // ---------- 主入口 ----------
    public static void main(String[] args) {
        SignEmulator emu = new SignEmulator();
        long ts = System.currentTimeMillis() / 1000;
        String params = "method=getUserInfo&uid=12345&token=abcdef";
        String sign = emu.generateSign(params, ts);
        System.out.println("Sign: " + sign);
        emu.emulator.close();
    }
}
```

### 迭代补环境过程

```text
第 1 次运行: UnsupportedOperation: Context->getPackageName()
  --> 补充 callObjectMethod 中的 getPackageName

第 2 次运行: UnsupportedOperation: Context->getPackageManager()
  --> 补充 PackageManager 相关处理

第 3 次运行: FileNotFoundException: /proc/self/status
  --> 补充 IOResolver 中的文件处理

第 4 次运行: UnsupportedOperation: Settings$Secure->getString()
  --> 补充 android_id 的返回值

第 5 次运行: 成功输出签名结果！
```

> **技巧**: 每次出错后，复制错误信息中的方法签名，在对应的 `callXxxMethod` 中添加 case 即可。这就是**"补环境"**。

---

## 性能优化

### 后端引擎选择

| 后端引擎   | 特点                            | 推荐场景           |
| :--------- | :------------------------------ | :----------------- |
| Unicorn    | 默认后端，兼容性最好            | 调试阶段           |
| Dynarmic   | JIT 编译，性能提升 5-10 倍      | 批量调用、生产环境 |
| KVM        | 硬件虚拟化 (仅 Linux ARM 主机)  | ARM 服务器部署     |

```java
// 使用 Dynarmic 后端
AndroidEmulator emulator = AndroidEmulatorBuilder.for32Bit()
        .addBackendFactory(new DynarmicFactory(true))
        .build();
```

### 复用与并发

```java
// Unidbg 不是线程安全的，需要使用对象池
public class SignServicePool {
    private final BlockingQueue<SignEmulator> pool;

    public SignServicePool(int poolSize) {
        pool = new LinkedBlockingQueue<>(poolSize);
        for (int i = 0; i < poolSize; i++) pool.offer(new SignEmulator());
    }

    public String sign(String params, long ts) throws InterruptedException {
        SignEmulator emu = pool.take();
        try { return emu.generateSign(params, ts); }
        finally { pool.offer(emu); }
    }
}
```

### 性能参考

```text
+--------------------------------------------------+
| 测试: MacBook Pro M1, JDK 11, sign() 函数       |
+--------------------------------------------------+
| 后端       | 单次调用 | 1000 次 | QPS            |
|------------|----------|---------|----------------|
| Unicorn    | ~15ms    | ~12s    | ~83            |
| Dynarmic   | ~2ms     | ~1.8s   | ~555           |
+--------------------------------------------------+
| 初始化时间: ~500ms  |  内存占用: ~80MB/实例     |
+--------------------------------------------------+
```

> 如果需要更高 QPS，可以封装为 HTTP 服务 (如 Spring Boot)，每个线程持有独立的 Emulator 实例。
