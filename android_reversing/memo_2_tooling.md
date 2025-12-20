# 🛠️ 动态分析工具与技术速记

## 🚀 Frida 动态插桩框架

### 🎯 核心特性
- **跨平台**: Windows/macOS/Linux/Android/iOS
- **多语言**: JavaScript 脚本 + Python 绑定
- **实时注入**: 无需重启目标进程
- **代码注入**: 支持 Java 层和 Native 层 Hook

### 🔧 主要功能
- **函数Hook**: 拦截和修改函数调用
- **内存操作**: 读写进程内存
- **RPC调用**: 脚本与主机通信
- **SSL Unpinning**: 绕过证书锁定

---

## 📱 Xposed 框架

### 🏗️ 工作原理
- 劫持 Zygote 进程
- 替换 `app_process`
- ART Hook 机制
- 全局方法拦截

### ⚖️ 优缺点
- **优点**: 全局Hook、持久化、模块化
- **缺点**: 需要Root、检测容易、兼容性问题

---

## 🖥️ Unidbg 模拟执行框架

### 📋 基础使用
```java
// 创建模拟器
emulator = AndroidEmulatorBuilder
    .for64Bit()
    .addBackendFactory(new Unicorn2Factory(true))
    .setProcessName("com.example.app")
    .build();

// 初始化内存和VM
Memory memory = emulator.getMemory();
memory.setLibraryResolver(new AndroidResolver(23));
vm = emulator.createDelvikVM(new File("path/to/apk"));

// 配置JNI
vm.setJni(this);
vm.setVerbose();

// 加载SO库
DelvikModule dm = vm.loadLibrary("target.so", true);
dm.callJNI_OnLoad(emulator);
```

---

## 🔒 rootfs 系统级技术

### 🛡️ 核心机制详解

#### 📂 chroot (Change Root)
**原理**: 改变进程的根目录，创建文件系统隔离环境

```bash
# 创建隔离环境
mkdir /tmp/jail
# 复制必要的系统文件
cp -r /bin /lib /lib64 /tmp/jail/
# 进入chroot环境
chroot /tmp/jail /bin/bash
```

**应用场景**:
- **容器技术**: Docker底层使用chroot隔离文件系统
- **安全测试**: 在隔离环境中运行可疑程序
- **系统恢复**: 从外部系统修复损坏的根文件系统

#### ⚡ execve (Execute Program)
**原理**: 加载新程序替换当前进程映像，实现程序切换

```c
// execve系统调用
int execve(const char *pathname, char *const argv[], char *const envp[]);

// 示例：执行shell命令
char *args[] = {"/bin/ls", "-la", NULL};
char *env[] = {"PATH=/bin:/usr/bin", NULL};
execve("/bin/ls", args, env);
```

**关键特性**:
- **进程替换**: PID不变，程序内容完全替换
- **内存清理**: 原程序内存被新程序覆盖
- **继承关系**: 文件描述符、信号处理等被继承

#### 🛡️ SELinux (Security-Enhanced Linux)
**原理**: 强制访问控制(MAC)，基于策略的安全机制

```bash
# 查看SELinux状态
getenforce
sestatus

# 设置SELinux模式
setenforce 0  # Permissive
setenforce 1  # Enforcing

# 查看文件安全上下文
ls -Z /etc/passwd
# -rw-r--r--. root root system_u:object_r:passwd_file_t:s0 /etc/passwd

# 设置安全上下文
chcon -t httpd_exec_t /usr/sbin/httpd
```

**核心概念**:
- **Subject**: 进程或用户
- **Object**: 文件、设备、网络端口等资源
- **Type**: 安全类型标识
- **Policy**: 访问控制规则

#### 🔧 rootfs实现原理
```c
// 模拟linker64加载SO文件的过程
#include <sys/mman.h>
#include <fcntl.h>
#include <elf.h>

int load_shared_library(const char* so_path) {
    // 1. 打开SO文件
    int fd = open(so_path, O_RDONLY);
    if (fd < 0) return -1;
    
    // 2. 读取ELF头
    Elf64_Ehdr ehdr;
    read(fd, &ehdr, sizeof(ehdr));
    
    // 3. 验证ELF魔数
    if (memcmp(ehdr.e_ident, ELFMAG, SELFMAG) != 0) {
        close(fd);
        return -1;
    }
    
    // 4. 读取程序头表
    Elf64_Phdr *phdrs = malloc(ehdr.e_phnum * sizeof(Elf64_Phdr));
    lseek(fd, ehdr.e_phoff, SEEK_SET);
    read(fd, phdrs, ehdr.e_phnum * sizeof(Elf64_Phdr));
    
    // 5. 映射LOAD段到内存
    for (int i = 0; i < ehdr.e_phnum; i++) {
        if (phdrs[i].p_type == PT_LOAD) {
            void *addr = mmap(
                (void*)phdrs[i].p_vaddr,
                phdrs[i].p_memsz,
                PROT_READ | PROT_WRITE | PROT_EXEC,
                MAP_PRIVATE | MAP_FIXED,
                fd,
                phdrs[i].p_offset
            );
            
            if (addr == MAP_FAILED) {
                perror("mmap failed");
                return -1;
            }
        }
    }
    
    // 6. 调用构造函数 (.init_array)
    call_constructors(ehdr, phdrs);
    
    free(phdrs);
    close(fd);
    return 0;
}

// chroot + execve 组合示例
void create_isolated_environment() {
    // 1. 创建新的根文件系统
    if (chroot("/opt/isolated_env") != 0) {
        perror("chroot failed");
        return;
    }
    
    // 2. 切换工作目录
    chdir("/");
    
    // 3. 执行新程序
    char *args[] = {"/bin/bash", NULL};
    char *env[] = {"PATH=/bin:/usr/bin", "HOME=/", NULL};
    execve("/bin/bash", args, env);
}
```

#### 🏗️ Android中的应用
```bash
# Android init进程中的rootfs操作
# 1. 挂载根文件系统
mount("rootfs", "/", "rootfs", 0, NULL);

# 2. 创建基础目录结构  
mkdir("/dev", 0755);
mkdir("/proc", 0755);
mkdir("/sys", 0755);
mkdir("/system", 0755);

# 3. 挂载关键文件系统
mount("tmpfs", "/dev", "tmpfs", MS_NOSUID, "mode=0755");
mount("proc", "/proc", "proc", 0, NULL);
mount("sysfs", "/sys", "sysfs", 0, NULL);

# 4. SELinux初始化
selinux_initialize();
selinux_load_policy();

# 5. 执行init程序
execve("/init", argv, envp);
```

#### 🛠️ 实际应用示例
```python
# Python中模拟chroot环境
import os
import subprocess

def create_minimal_rootfs():
    """创建最小化的rootfs环境"""
    rootfs_path = "/tmp/mini_rootfs"
    
    # 创建目录结构
    dirs = ["bin", "lib", "lib64", "usr/bin", "etc", "dev", "proc", "sys"]
    for d in dirs:
        os.makedirs(f"{rootfs_path}/{d}", exist_ok=True)
    
    # 复制必要的二进制文件
    binaries = ["/bin/bash", "/bin/ls", "/bin/cat", "/usr/bin/id"]
    for binary in binaries:
        if os.path.exists(binary):
            subprocess.run(["cp", binary, f"{rootfs_path}{binary}"])
    
    # 复制共享库
    # 使用ldd命令查找依赖的共享库
    proc = subprocess.run(["ldd", "/bin/bash"], capture_output=True, text=True)
    for line in proc.stdout.split('\n'):
        if '=>' in line:
            lib_path = line.split('=>')[1].strip().split()[0]
            if lib_path.startswith('/'):
                subprocess.run(["cp", lib_path, f"{rootfs_path}{lib_path}"])
    
    return rootfs_path

def enter_chroot_environment(rootfs_path):
    """进入chroot环境"""
    try:
        # 挂载必要的文件系统
        subprocess.run(["mount", "-t", "proc", "proc", f"{rootfs_path}/proc"])
        subprocess.run(["mount", "-t", "sysfs", "sys", f"{rootfs_path}/sys"])
        
        # 进入chroot环境
        os.chroot(rootfs_path)
        os.chdir("/")
        
        # 执行shell
        os.execve("/bin/bash", ["/bin/bash"], {"PATH": "/bin:/usr/bin"})
        
    except OSError as e:
        print(f"Failed to enter chroot: {e}")
```

#### 🔍 安全研究应用
在Android逆向中，rootfs技术常用于：
- **沙箱环境**: 在隔离环境中分析恶意APP
- **系统仿真**: 创建特定Android版本的运行环境  
- **绕过检测**: 通过chroot隐藏分析工具
- **容器化分析**: 使用Docker容器进行大规模自动化分析

---

## ⚖️ Unidbg vs Frida 对比

| 特性 | Unidbg | Frida |
|:---|:---|:---|
| **执行环境** | PC 端模拟执行 | 移动设备端真机 |
| **工作模式** | 黑盒库调用 | 进程注入Hook |
| **依赖要求** | 仅需SO文件 | 需要完整APK |
| **反调试** | 天然免疫 | 需要脚本对抗 |
| **环境依赖** | 手动模拟 | 真实运行环境 |
| **性能** | 较低(全模拟) | 较高(原生运行) |
| **适用场景** | 纯算法分析 | UI和业务逻辑分析 |

---

## 🛡️ 加固与脱壳技术

### 🔍 常见加固厂商
- `libnesec.so` (网易易盾)
- `libjiagu.so` (360加固)
- `libbaiduprotect.so` (百度加固)

### 🎯 脱壳原理
Frida 脱壳采用 **"以动制静"** 策略：不关心解密过程，在解密完成、即将执行时从内存 dump 原始代码。

### 📱 DEX 文件脱壳

#### 🎯 关键Hook点
- `DexFile::Open` / `DexFile::OpenFile` (低版本Android)
- `DexFile::DefineClass` (类定义时)
- `art::DexFile::OpenCommon` (新版Android核心函数)

#### 🔧 Hook 策略
```javascript
// Hook ART核心加载函数
var dexFileOpen = Module.findExportByName("libart.so", 
    "_ZN3art7DexFile10OpenCommonEPKh...");
Interceptor.attach(dexFileOpen, {
    onEnter: function(args) {
        var dex_start = args[0];
        var dex_size = args[1].toInt32();
        // Dump DEX文件
        this.dumpDex(dex_start, dex_size);
    }
});
```

### 💻 SO 文件修复

#### ❌ Dump 挑战
从 `/proc/<pid>/maps` 直接dump的数据缺少：
- ELF Header
- Section Headers  
- 正确的文件偏移

#### 🔧 修复流程
1. **基于内存布局**: 利用 maps 信息获取加载基址
2. **重建ELF Header**: 根据架构生成合法ELF头
3. **修复Section Table**: 从动态符号表恢复段信息
4. **对齐修正**: 调整偏移和地址

#### 🛠️ 推荐工具
- **SoFixer**: PC端SO修复工具
- **frida-so-dump**: 自动化dump+修复

---

## 🔐 加密算法逆向

### 🔄 对称加密
**特点**: 同一密钥加解密，速度快，适合大数据量

- **AES**: 模式(ECB/CBC/CTR)，填充(PKCS5/7)
- **DES/3DES**: 较老的算法，安全性较低

### 🔑 非对称加密
**特点**: 公私钥对，公钥加密私钥解密，速度慢

- **RSA**: 最常用的非对称算法
- **ECC**: 椭圆曲线加密，更高效

### 🧮 哈希算法
- **MD5**: 128位散列，已不安全
- **SHA**: SHA-1/SHA-256/SHA-512
- **HMAC**: 基于哈希的消息认证码

### 📝 编码算法
- **Base64**: 64个字符编码
- **Hex**: 十六进制编码

### 💻 实现方式对比

| 实现方式 | Java层 | Native层 |
|:---|:---|:---|
| **API** | javax.crypto | OpenSSL/mbedTLS |
| **优点** | 简单易懂 | 性能好，难分析 |
| **缺点** | 易反编译 | 实现复杂 |

---

## 🔍 逆向分析策略

### 🔎 静态分析
#### 特征字符串搜索
- **算法名**: AES/RSA/DES/MD5/SHA256
- **Java API**: javax.crypto.Cipher/SecretKeySpec
- **编码**: Base64
- **开源库**: OpenSSL/boringssl

#### 📊 代码交叉引用
- 定位加密API使用点
- 追踪上层业务调用
- 分析密钥生成逻辑

### 🎯 动态分析
#### Hook关键函数
```javascript
// Java层Cipher Hook
Java.perform(function() {
    var Cipher = Java.use("javax.crypto.Cipher");
    Cipher.doFinal.overload('[B').implementation = function(input) {
        console.log("[Cipher] Input: " + bytesToHex(input));
        var result = this.doFinal(input);
        console.log("[Cipher] Output: " + bytesToHex(result));
        return result;
    };
});

// Native层Hook
var encrypt_func = Module.findExportByName("libcrypto.so", "AES_encrypt");
Interceptor.attach(encrypt_func, {
    onEnter: function(args) {
        console.log("[AES] Key: " + hexdump(args[1], 16));
    }
});
```

---

## 🛡️ SO 反调试技术

### 🔄 init_array 调用流程
```
app_process → Zygote fork → dlopen(libxxx.so) → Linker加载
    ↓
ELF解析 → 段映射 → 重定位 → init_array执行 → JNI_OnLoad
```

### 🔤 SO 字符串混淆
- **编译时加密**: XOR、AES加密静态字符串
- **运行时解密**: 栈上构造、动态拼接
- **检测方法**: 熵值分析、内存Hook解密函数

### 🛡️ SO 反调试实现
- **ptrace检测**: `ptrace(PTRACE_TRACEME, 0, 1, 0) == -1`
- **文件检测**: 检查frida-server、调试器进程
- **内存检测**: 扫描/proc/self/maps中的可疑库
- **时间检测**: 检测单步执行、系统调用延迟
- **完整性检测**: 代码段哈希校验

### 🔓 绕过技术
- **Hook ptrace**: 修改参数和返回值
- **文件重定向**: access/openat重定向到/dev/null  
- **时间伪造**: clock_gettime返回固定值
- **内存保护**: mprotect保持执行权限
- **符号隐藏**: dlsym返回NULL隐藏敏感符号

### 🏗️ 多层级对抗
```cpp
__attribute__((constructor(101))) // 优先级101
void stage1_check() { /* 基础检测 */ }

__attribute__((constructor(102))) // 优先级102  
void stage2_check() { /* 深度检测 */ }
```

---

## 🚫 反调试技术详解

### 🔍 Frida 反调试
#### 常见检测技术
- **端口扫描**: 检测27042端口
- **特征文件**: 查找frida-server文件
- **内存模块**: 扫描/proc/self/maps中的frida相关模块
- **线程名**: 检测gum-js-loop、gmain等特征线程
- **D-Bus消息**: 检测D-Bus通信
- **Inline Hook**: 检测函数头部是否被修改

#### 🛡️ 检测方法
```cpp
// 地址校验
void* strcmp_addr = dlsym(RTLD_DEFAULT, "strcmp");
if (isAddressInFridaRange(strcmp_addr)) {
    // 检测到Frida
}

// 内容校验  
uint8_t* func_start = (uint8_t*)open;
if (func_start[0] != expected_prologue[0]) {
    // 函数被Hook
}
```

---

## 🎯 常见面试题及答案

### Q1: Frida 和 Xposed 的主要区别？
**A**: 
- **注入方式**: Frida运行时注入，Xposed启动时加载
- **Root要求**: Frida可免Root(某些场景)，Xposed必须Root
- **检测难度**: Frida检测较难，Xposed容易检测
- **适用场景**: Frida适合动态分析，Xposed适合系统级修改

### Q2: 如何使用Unidbg调用加密函数？
**A**: 
1. 创建Android模拟器环境
2. 加载目标SO库并调用JNI_OnLoad
3. 实现必要的JNI接口和系统调用
4. 直接调用目标函数获取结果

### Q3: DEX脱壳的核心原理是什么？
**A**: Hook ART运行时的DEX加载函数，在DEX被解密加载到内存后、执行前的时机点，将完整的DEX数据从内存中dump出来。

### Q4: 如何识别SO文件使用的加密算法？
**A**: 
1. **静态分析**: 搜索算法特征字符串、分析导入函数
2. **动态分析**: Hook加密库函数、观察数据流
3. **常量分析**: 查找算法特征常量(如AES的S-box)
4. **行为分析**: 分析加密流程和数据变换

### Q5: init_array在反调试中的作用？
**A**: init_array中的函数在SO加载时自动执行，常用于：
- 早期反调试检测(在JNI_OnLoad之前)
- 环境检测和初始化
- 关键数据解密
- 建立监控机制

### Q6: 如何绕过常见的反调试技术？
**A**: 
1. **ptrace检测**: Hook ptrace函数返回成功
2. **文件检测**: 重定向文件访问到空设备
3. **进程检测**: 隐藏或重命名调试进程
4. **时间检测**: 伪造系统时间函数
5. **内存检测**: 清理内存特征、使用隐蔽注入

### Q7: Frida脚本如何处理多进程应用？
**A**: 
```javascript
// 方法1: 使用spawn模式启动应用
frida -U -f com.example.app -l script.js --no-pause

// 方法2: Hook fork/clone系统调用跟踪子进程
// 方法3: 使用frida-tools的多进程管理功能
```

### Q8: 如何分析混淆严重的Native代码？
**A**: 
1. **动态追踪**: 使用Frida Stalker跟踪执行流
2. **符号恢复**: 分析字符串引用恢复函数名
3. **模拟执行**: 用Unidbg黑盒调用核心函数
4. **去混淆工具**: 使用d810、OLLVM去混淆插件
5. **分段分析**: 识别关键算法片段，逐个击破