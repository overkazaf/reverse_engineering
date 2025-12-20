# SO 运行时仿真技术

在高级 Android 逆向工程中，我们经常需要自动化地调用 SO 文件中的加密、签名或校验函数。然而，在真实的设备上通过 Frida Hook 来做这件事，不仅效率低下，而且容易受到反调试和环境检测的阻碍。

**SO 运行时仿真**（有时被称为"符号执行"的工程化应用）是一种革命性的技术，它通过在 PC 上创建一个模拟的 Android Native 运行环境，直接加载并执行 SO 文件，从而摆脱对真实设备的依赖。

## 目录

1. [核心架构](#核心架构)
2. [推荐项目：unidbg](#推荐项目unidbg)
3. [Python + Unicorn 手动实现](#python--unicorn-手动实现)
4. [基于 chroot 与 linker 的高级仿真](#基于-chroot-与-linker-的高级仿真)
5. [方案对比与选型](#方案对比与选型)
6. [总结](#总结)

---

## 核心架构

一个典型的 SO 仿真框架主要由以下几个部分构成：

### 1. ELF 加载器 (ELF Loader)

这是仿真的基础。它负责像 Android 的 `linker` 一样工作：

| 功能 | 说明 |
|------|------|
| 解析 ELF | 读取 SO 文件的头部、程序头、段表等信息 |
| 内存映射 | 根据程序头（`PT_LOAD`）将 SO 的代码段（`.text`）和数据段（`.data`, `.bss`）加载到模拟的内存空间中 |
| 处理重定位 | 解析重定位表（`.rel.dyn`, `.rela.dyn`），修正所有对内部地址和外部符号的引用 |

### 2. CPU 模拟器 (CPU Emulator)

- **Unicorn Engine**: 这是目前最主流的选择。Unicorn 是一个基于 QEMU 的轻量级、多平台的 CPU 模拟器库
- **指令级控制**: Unicorn 允许我们精细地控制执行流程，包括设置寄存器、读写内存、以及通过 Hook 机制在执行到特定指令或地址时触发回调

### 3. 系统库与环境模拟 (Library & Environment Mocking)

SO 文件不会独立存在，它总是会调用外部函数。仿真框架必须能够"假装"自己是 Android 系统：

| Mock 目标 | 说明 |
|-----------|------|
| `libc.so` | 提供 `malloc`, `free`, `memcpy`, `strlen`, `printf` 等标准 C 库函数 |
| Android 框架库 | 提供 `liblog.so`、`libz.so`、`libcrypto.so` 等常用系统库函数 |
| JNI 环境 | 模拟 `JNIEnv` 指针和相关函数表（`NewStringUTF`, `GetFieldID` 等） |

---

## 推荐项目：unidbg

`unidbg` 是一个非常强大和成熟的、专门用于 Android SO 仿真和符号执行的 Java 开源项目。

### unidbg 的优点

| 特性 | 说明 |
|------|------|
| 高度自动化 | 内置了完善的 ELF 加载器和常用系统库的 Mock 实现 |
| 易于使用 | 提供了简洁的 API，用户只需几行代码就可以加载 SO、调用函数 |
| JNI 模拟 | 拥有强大的 JNI 模拟能力，甚至可以调用和 Mock Java 对象的方法 |
| 调试与跟踪 | 支持与 GDB 连接进行远程调试，也可以通过 Hook 机制打印详细的执行日志 |

### unidbg 使用范例

```java
// 使用 unidbg 调用 SO 中的签名函数
public class SignatureCalculator {
    public static void main(String[] args) {
        // 1. 创建 Android ARM64 模拟器实例
        Emulator<?> emulator = AndroidEmulatorBuilder.for64Bit().build();
        Memory memory = emulator.getMemory();

        // 2. 加载目标 SO 文件及其依赖
        // unidbg 会自动处理重定位和依赖加载
        Module module = emulator.loadLibrary(new File("libnative-lib.so"));

        // 3. 准备输入数据
        String input = "this is my data to sign";
        // 将输入字符串写入模拟器内存
        Pointer inputPtr = memory.allocateString(input);

        // 4. 调用目标函数
        // callFunction() 会自动处理寄存器和栈设置
        Number result = module.callFunction(emulator, 0x1234, inputPtr, input.length());

        // 5. 从模拟器内存中读取结果
        Pointer resultPtr = Pointer.pointer(emulator, result.intValue());
        String signature = resultPtr.getString(0);

        System.out.println("Input: " + input);
        System.out.println("Signature: " + signature);

        // 6. 关闭模拟器
        emulator.close();
    }
}
```

---

## Python + Unicorn 手动实现

如果需要更细粒度的控制，可以使用 Python + Unicorn 从头实现仿真。

### 依赖库

- **Unicorn Engine**: CPU 模拟引擎
- **pyelftools**: 用于解析 ELF 文件
- **Python**: 胶水语言，用于编写加载器和 Mock 函数

### 实现步骤

#### a. 初始化 Unicorn 环境

```python
from unicorn import *
from unicorn.arm64_const import *

# 初始化 ARM64 模拟器
mu = Uc(UC_ARCH_ARM64, UC_MODE_ARM)

# 定义内存区域
BASE_ADDRESS = 0x40000000
STACK_ADDRESS = 0x70000000
STACK_SIZE = 1024 * 1024  # 1MB 栈空间

# 映射内存
mu.mem_map(BASE_ADDRESS, 2 * 1024 * 1024)  # 2MB 用于 SO
mu.mem_map(STACK_ADDRESS, STACK_SIZE)

# 设置栈指针 (SP)
mu.reg_write(UC_ARM64_REG_SP, STACK_ADDRESS + STACK_SIZE)
```

#### b. 加载 ELF 文件

```python
from elftools.elf.elffile import ELFFile

def load_so(mu, so_path):
    """加载 SO 文件到模拟器内存"""
    with open(so_path, 'rb') as f:
        elffile = ELFFile(f)
        for segment in elffile.iter_segments():
            if segment.header.p_type == 'PT_LOAD':
                vaddr = segment.header.p_vaddr
                mem_size = segment.header.p_memsz
                file_size = segment.header.p_filesz
                data = segment.data()

                # 将段写入模拟器内存
                mu.mem_write(BASE_ADDRESS + vaddr, data)
                print(f"Loaded segment at {hex(BASE_ADDRESS + vaddr)} size {hex(mem_size)}")

    return BASE_ADDRESS

# 加载 SO
base = load_so(mu, 'libnative-lib.so')
```

#### c. 实现函数 Mock

```python
# 模拟外部函数地址
MOCK_PUTS_ADDR = 0xFFFFFFFF00001000

# 记录被 Hook 的指令
hooked_instructions = set()

def hook_code(mu, address, size, user_data):
    """代码执行 Hook 回调"""
    if address in hooked_instructions:
        return

    instruction = mu.mem_read(address, size)

    # 简化 BL 指令检查 (ARM64)
    if len(instruction) >= 4 and instruction[3] == 0x94:
        # 计算跳转目标地址 (需要完整解码指令)
        target_addr = calculate_branch_target(address, instruction)

        if target_addr == MOCK_PUTS_ADDR:
            # 1. 读取参数 (ARM64 第一个参数在 X0 寄存器)
            str_ptr = mu.reg_read(UC_ARM64_REG_X0)
            # 2. 从模拟器内存中读取字符串
            str_val = mu.mem_read(str_ptr, 256).split(b'\x00')[0]
            # 3. 执行 Mock 功能
            print(f"[+] puts called with: '{str_val.decode()}'")
            # 4. 模拟函数返回
            mu.reg_write(UC_ARM64_REG_PC, mu.reg_read(UC_ARM64_REG_LR))
        else:
            print(f"Warning: Unhandled call to {hex(target_addr)}")

        hooked_instructions.add(address)

# 在 SO 加载区域设置 Hook
mu.hook_add(UC_HOOK_CODE, hook_code, begin=BASE_ADDRESS, end=BASE_ADDRESS + 0x100000)
```

#### d. 文件系统 Mock

SO 文件可能会访问文件系统。通过 Mock `fopen`、`fread` 等函数，可以完全控制文件访问：

```python
class FileSystemMock:
    """文件系统模拟"""
    def __init__(self, rootfs_path):
        self.rootfs = rootfs_path
        self.file_handles = {}
        self.next_fd = 100

    def mock_fopen(self, mu, path_ptr, mode_ptr):
        """模拟 fopen"""
        # 读取路径参数
        path = mu.mem_read(path_ptr, 256).split(b'\x00')[0].decode()
        mode = mu.mem_read(mode_ptr, 8).split(b'\x00')[0].decode()

        # 映射到本地 rootfs
        local_path = os.path.join(self.rootfs, path.lstrip('/'))

        try:
            handle = open(local_path, mode)
            fd = self.next_fd
            self.file_handles[fd] = handle
            self.next_fd += 1
            print(f"[+] fopen('{path}', '{mode}') = {fd}")
            return fd
        except FileNotFoundError:
            print(f"[-] fopen('{path}') failed: file not found")
            return 0

    def mock_fread(self, mu, buf_ptr, size, count, fd):
        """模拟 fread"""
        if fd in self.file_handles:
            data = self.file_handles[fd].read(size * count)
            mu.mem_write(buf_ptr, data)
            return len(data)
        return 0
```

---

## 基于 chroot 与 linker 的高级仿真

这是最接近"真实"的仿真方式。直接利用从 Android 系统中提取出的 `linker64` 程序，在受控的 `chroot` 环境中加载目标 SO。

### 核心思路

1. **构建 Android Rootfs**: 在 Linux 主机上创建一个最小化的 Android 文件系统
2. **编写加载器 (Loader)**: 用 C 编写一个程序，`chroot` 到 Rootfs 中，然后启动 `linker64`
3. **编写测试桩 (Test Harness)**: 编写一个程序，加载目标 SO 并调用指定函数

### 实现步骤

#### a. 准备 Android Rootfs

```bash
# 在 PC 上创建目录结构
mkdir -p ~/android_rootfs/system/lib64
mkdir -p ~/android_rootfs/system/bin
mkdir -p ~/android_rootfs/data/local/tmp

# 从设备上拉取文件 (以 arm64 为例)
adb pull /system/bin/linker64 ~/android_rootfs/system/bin/
adb pull /system/lib64/libc.so ~/android_rootfs/system/lib64/
adb pull /system/lib64/libdl.so ~/android_rootfs/system/lib64/
adb pull /system/lib64/libm.so ~/android_rootfs/system/lib64/

# 将目标 SO 和测试桩程序放入
cp your_target.so ~/android_rootfs/data/local/tmp/
cp your_harness ~/android_rootfs/data/local/tmp/
```

#### b. 编写测试桩程序 (harness.c)

```c
#include <stdio.h>
#include <dlfcn.h>

// 假设目标 SO 导出函数: char* process_data(const char* input);
typedef const char* (*process_data_func)(const char*);

int main(int argc, char *argv[]) {
    // 在 chroot 环境中，路径是相对于新根目录的
    void* handle = dlopen("/data/local/tmp/your_target.so", RTLD_LAZY);
    if (!handle) {
        fprintf(stderr, "Cannot open library: %s\n", dlerror());
        return -1;
    }

    // 获取函数指针
    process_data_func func = (process_data_func)dlsym(handle, "process_data");
    if (!func) {
        fprintf(stderr, "Cannot find symbol: %s\n", dlerror());
        dlclose(handle);
        return -1;
    }

    // 调用函数并打印结果
    const char* input = "hello from harness";
    const char* result = func(input);
    printf("Result from SO: %s\n", result);

    dlclose(handle);
    return 0;
}
```

#### c. 编写加载器程序 (loader.c)

```c
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>

int main(int argc, char *argv[]) {
    const char* root_dir = "/home/user/android_rootfs";  // 修改为你的 rootfs 路径

    if (chroot(root_dir) != 0) {
        perror("chroot failed");
        return 1;
    }

    // 进入 chroot 后，'/' 就是之前的 root_dir
    chdir("/");

    // 准备 execve 参数
    char *new_argv[] = {
        "/data/local/tmp/harness",  // 要执行的程序
        NULL
    };
    char *new_envp[] = {
        "LD_LIBRARY_PATH=/system/lib64",  // 告诉 linker 在哪里找 .so
        NULL
    };

    // 使用 linker64 来执行测试桩程序
    execve("/system/bin/linker64", new_argv, new_envp);

    // 如果 execve 成功，这行代码永远不会被执行
    perror("execve failed");
    return 1;
}
```

### 注意事项

- **权限要求**: `chroot` 操作需要 root 权限
- **通信机制**: 主机与被仿真进程的通信需要借助文件、管道或 Socket 等 IPC 机制
- **架构匹配**: 需要在相同架构的 Linux 主机上运行（如 ARM64 主机运行 ARM64 SO）

---

## 方案对比与选型

| 方案 | 优点 | 复杂度 | 适用场景 |
|------|------|--------|----------|
| **unidbg (Java)** | 成熟稳定，JNI 模拟完善，API 简洁，社区活跃 | **低** | 快速分析、JNI 函数调用、通用 Android SO 仿真 |
| **Python + Unicorn** | 灵活可定制，完全控制执行流程，跨平台，帮助理解原理 | **中** | 纯 Native 算法逆向、安全研究、Fuzzing、学习目的 |
| **C + chroot + Harness** | 保真度最高，性能最好，直接利用系统原生 linker | **高** | 环境要求苛刻的 SO、需要 TLS 初始化、追求极致性能 |

---

## 总结

SO 运行时仿真是一项高级但回报巨大的技术。它将逆向分析从繁琐的手工调试和 Hook 中解放出来，带入了自动化、可大规模扩展的新阶段。

**关键要点**：

1. **核心组件**: ELF 加载器 + CPU 模拟器 + 系统库 Mock
2. **推荐工具**: unidbg 是最成熟的 Android SO 仿真框架
3. **进阶方案**: Python + Unicorn 提供更细粒度控制，chroot 方案提供最高保真度
4. **应用场景**: 加密算法分析、签名函数调用、自动化测试、Fuzzing

对于需要频繁调用 Native 函数、分析复杂算法的场景，掌握 SO 仿真技术是必不可少的技能。
