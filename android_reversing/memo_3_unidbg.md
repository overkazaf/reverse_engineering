# 🖥️ Unidbg 模拟执行框架速记

## 🚀 基础使用

### 📋 环境搭建
```java
// 创建64位Android模拟器
emulator = AndroidEmulatorBuilder
    .for64Bit()  // 或 .for32Bit()
    .addBackendFactory(new Unicorn2Factory(true))
    .setProcessName("com.sina.oasis")
    .build();

// 初始化内存
Memory memory = emulator.getMemory();
memory.setLibraryResolver(new AndroidResolver(23)); // API Level 23

// 创建Dalvik虚拟机
vm = emulator.createDelvikVM(new File("path/to/apk"));
```

### 🔧 JNI配置
```java
// 设置JNI接口实现
vm.setJni(this);
vm.setVerbose(true); // 开启详细日志

// 加载SO库
DelvikModule dm = vm.loadLibrary("target.so", true);
dm.callJNI_OnLoad(emulator); // 调用JNI_OnLoad
```

---

## 🏗️ 核心架构

### 📊 架构组件

| 组件 | 作用 | 重要性 |
|:---|:---|:---|
| **Unicorn Engine** | CPU指令模拟执行 | ⭐⭐⭐⭐⭐ |
| **Android模拟器** | 系统环境模拟 | ⭐⭐⭐⭐⭐ |
| **Dalvik VM** | Java虚拟机模拟 | ⭐⭐⭐⭐ |
| **内存管理** | 虚拟内存分配 | ⭐⭐⭐⭐ |
| **系统调用** | Linux系统调用模拟 | ⭐⭐⭐ |

### 🔄 执行流程
```
Java调用 → JNI Bridge → Native函数 → 
Unicorn模拟 → 系统调用处理 → 返回结果
```

---

## 💻 常用代码模板

### 🎯 基本调用模板
```java
public class UnidbgTest extends AbstractJni {
    private final AndroidEmulator emulator;
    private final VM vm;
    private final DalvikModule dm;

    public UnidbgTest() {
        // 初始化模拟器
        emulator = AndroidEmulatorBuilder
            .for64Bit()
            .setProcessName("com.example.app")
            .build();

        // 内存设置
        Memory memory = emulator.getMemory();
        memory.setLibraryResolver(new AndroidResolver(23));

        // VM创建
        vm = emulator.createDalvikVM(null);
        vm.setJni(this);
        vm.setVerbose(true);

        // 加载SO
        dm = vm.loadLibrary("libtarget.so", true);
        dm.callJNI_OnLoad(emulator);
    }

    public void testFunction() {
        // 调用native函数
        Number result = dm.callFunction(emulator, "native_encrypt", 
            vm.getJNIEnv(), 0, "input_string");
        System.out.println("Result: " + result);
    }
}
```

### 🔧 JNI函数Hook
```java
@Override
public DvmObject<?> callObjectMethodV(BaseVM vm, DvmObject<?> dvmObject, 
    String signature, VaList vaList) {
    
    switch (signature) {
        case "android/content/Context->getPackageName()Ljava/lang/String;":
            return new StringObject(vm, "com.example.app");
    }
    
    return super.callObjectMethodV(vm, dvmObject, signature, vaList);
}
```

### 🛠️ 系统调用实现
```java
@Override
public FileResult resolve(Emulator emulator, String pathname, int oflags) {
    if ("/proc/version".equals(pathname)) {
        return FileResult.success(new ByteArrayFileIO(oflags, pathname, 
            "Linux version 4.14.81".getBytes()));
    }
    return null;
}
```

---

## 🔧 高级技巧

### 📝 内存操作
```java
// 分配内存
UnidbgPointer memory = emulator.getMemory().malloc(0x1000, true);

// 写入数据
memory.write(0, "test data".getBytes(), 0, 9);

// 读取数据
byte[] data = memory.getByteArray(0, 9);

// 释放内存
memory.free();
```

### 🎯 函数地址获取
```java
// 通过符号名获取
Symbol symbol = dm.findSymbolByName("target_function");
long address = symbol.getValue();

// 直接调用地址
Number result = emulator.eFunc(address, arg1, arg2, arg3);
```

### 🔍 调试与分析
```java
// 设置断点
emulator.attach().addBreakPoint(address);

// 内存Dump
Inspector.inspect(memory.pointer(address), "Memory dump");

// 寄存器状态
emulator.getBackend().reg_read(ArmConst.UC_ARM_REG_R0);
```

---

## 🚫 常见问题与解决

### ❗ 常见错误

| 错误类型 | 原因 | 解决方案 |
|:---|:---|:---|
| **Library not found** | SO库路径错误 | 检查路径，使用绝对路径 |
| **JNI signature error** | JNI签名不匹配 | 核对函数签名格式 |
| **Memory access violation** | 内存访问越界 | 检查指针有效性 |
| **System call not implemented** | 系统调用未实现 | 实现对应的系统调用 |

### 🔧 调试技巧
```java
// 开启详细日志
vm.setVerbose(true);

// Hook所有JNI调用
vm.setJni(new AbstractJni() {
    @Override
    public boolean verbose() {
        return true;
    }
});

// 追踪执行过程
emulator.traceCode(begin, end);
```

---

## 📊 性能优化

### ⚡ 优化策略
- **预加载库**: 提前加载常用系统库
- **缓存结果**: 缓存重复计算的结果
- **减少日志**: 生产环境关闭详细日志
- **内存管理**: 及时释放不用的内存

### 🎯 批量处理
```java
public void batchProcess(List<String> inputs) {
    for (String input : inputs) {
        // 复用已初始化的环境
        Number result = dm.callFunction(emulator, "encrypt", input);
        results.add(result);
    }
}
```

---

## 🔒 安全注意事项

### 🛡️ 沙箱限制
- 网络访问受限
- 文件系统隔离
- 系统资源控制

### ⚠️ 风险控制
```java
// 限制执行时间
emulator.setTimeout(5000); // 5秒超时

// 限制内存使用
memory.setMaxMemory(100 * 1024 * 1024); // 100MB

// 禁用危险操作
emulator.getSyscallHandler().setVerbose(false);
```

---

## 🎯 常见面试题及答案

### Q1: Unidbg 的工作原理是什么？
**A**: Unidbg 基于 Unicorn Engine 模拟 CPU 指令执行，在 PC 端创建一个 Android 用户态执行环境，通过模拟 Dalvik VM、JNI 接口和 Linux 系统调用，实现对 Android SO 库的黑盒调用。

### Q2: Unidbg 相比真机调试有什么优势？
**A**: 
- **环境可控**: 不受反调试检测影响
- **调试便利**: 可设置断点、查看内存、单步执行
- **部署简单**: 无需真机设备，仅需 SO 文件
- **批量处理**: 适合大量样本的自动化分析

### Q3: 如何在 Unidbg 中处理复杂的 JNI 调用？
**A**: 
1. **继承 AbstractJni**: 实现所需的 JNI 接口
2. **重写关键方法**: callObjectMethodV、callStaticObjectMethodV 等
3. **模拟 Android API**: 返回合理的模拟数据
4. **处理回调**: 实现 native 到 Java 的回调

### Q4: Unidbg 如何处理系统调用？
**A**: 
1. **重写 SyscallHandler**: 实现未支持的系统调用
2. **文件系统模拟**: 通过 FileResult 模拟文件访问
3. **网络调用处理**: 模拟 socket 相关操作
4. **进程信息**: 模拟 /proc 文件系统

### Q5: 如何用 Unidbg 分析加密算法？
**A**: 
1. **黑盒调用**: 直接调用加密函数观察输入输出
2. **中间结果**: Hook 关键函数获取中间数据
3. **内存分析**: 查看加密过程中的内存变化
4. **算法逆向**: 结合静态分析确定算法类型

### Q6: Unidbg 的局限性有哪些？
**A**: 
- **模拟完整性**: 无法 100% 模拟真实环境
- **性能开销**: 模拟执行比原生执行慢
- **复杂依赖**: 处理复杂的系统依赖困难
- **动态特性**: 无法处理运行时动态加载的代码

### Q7: 如何调试 Unidbg 中的内存问题？
**A**: 
```java
// 内存状态检查
memory.dumpMemory();

// 指针有效性验证
if (pointer != null && !pointer.isNull()) {
    // 安全访问
}

// 内存泄漏检测
memory.getHeapDumper().dump();
```

### Q8: Unidbg 如何处理多线程 SO 库？
**A**: 
- **单线程模拟**: Unidbg 主要支持单线程执行
- **线程同步**: 模拟 pthread 相关函数
- **异步处理**: 通过回调机制处理异步操作
- **状态管理**: 维护线程本地存储 (TLS) 状态

### Q9: 如何提高 Unidbg 的执行效率？
**A**: 
1. **减少日志输出**: 关闭不必要的 verbose 模式
2. **优化内存分配**: 重复使用内存块
3. **缓存机制**: 缓存重复计算的结果
4. **精简环境**: 只加载必需的系统库

### Q10: Unidbg 在实际项目中的应用场景？
**A**: 
- **算法逆向**: 分析加密、签名算法
- **接口分析**: 理解 App 的网络请求逻辑
- **自动化测试**: 批量测试不同输入的结果
- **安全研究**: 漏洞分析和 Exploit 开发
- **合规检测**: 检查 SO 库是否包含敏感行为