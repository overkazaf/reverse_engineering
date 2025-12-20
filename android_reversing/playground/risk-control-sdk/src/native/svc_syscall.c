/**
 * ======================================================================================
 * SVC (Supervisor Call) 系统调用实现 - 原理说明
 * ======================================================================================
 * 
 * SVC调用是ARM架构中直接执行系统调用的底层机制，绕过标准C库的包装函数。
 * 这在安全研究、反调试、性能优化等场景中具有重要意义。
 * 
 * 【SVC调用的基本原理】
 * 1. 用户态程序准备系统调用号和参数
 * 2. 执行SVC指令触发软件中断/异常
 * 3. CPU从用户态(EL0/User Mode)切换到内核态(EL1/Supervisor Mode)
 * 4. 处理器跳转到异常向量表中的相应处理程序
 * 5. 内核根据系统调用号查找系统调用表
 * 6. 执行对应的内核函数
 * 7. 返回结果，恢复用户态执行
 * 
 * 【ARM64 vs ARM32 的区别】
 * ARM64 (AArch64):
 *   - 系统调用号通过 x8 寄存器传递
 *   - 参数通过 x0-x7 寄存器传递（最多8个）
 *   - 返回值通过 x0 寄存器返回
 *   - 使用 svc #0 指令触发异常
 *   - 从 EL0 切换到 EL1
 * 
 * ARM32 (AArch32):
 *   - 系统调用号通过 r7 寄存器传递
 *   - 参数通过 r0-r6 寄存器传递（标准为r0-r3）
 *   - 返回值通过 r0 寄存器返回
 *   - 使用 svc #0 指令触发软件中断
 *   - 从 User Mode 切换到 Supervisor Mode
 * 
 * 【内联汇编约束说明】
 * - "=r": 输出约束，表示寄存器用于输出
 * - "+r": 输入输出约束，表示寄存器既是输入也是输出
 * - "r":  输入约束，表示寄存器用于输入
 * - "memory": 内存屏障，告诉编译器汇编可能修改内存
 * - "cc": 条件码约束，表示指令可能影响条件标志位
 * 
 * 【应用场景】
 * 1. 反调试：绕过被Hook的libc函数
 * 2. 性能优化：减少函数调用开销
 * 3. 沙箱逃逸：直接与内核交互
 * 4. 安全研究：理解系统调用机制
 * 5. 固件开发：底层系统编程
 * 
 * ======================================================================================
 */

#include "svc_syscall.h"
#include <sys/stat.h>
#include <sys/utsname.h>
#include <sys/mman.h>
#include <time.h>
#include <errno.h>
#include <string.h>
#include <stdio.h>

// 全局变量
static int g_svc_initialized = 0;
static int g_cpu_arch = -1;

// ========== ARM64 SVC调用实现 ==========

#ifdef __aarch64__

/**
 * ARM64 SVC调用执行原理:
 * 1. 将系统调用号加载到x8寄存器（ARM64 ABI约定）
 * 2. 执行svc #0指令触发系统调用异常
 * 3. CPU从EL0（用户态）切换到EL1（内核态）
 * 4. 内核根据x8寄存器中的系统调用号查找系统调用表
 * 5. 执行对应的内核函数，返回值通过x0寄存器传递
 */
long svc_call0(long syscall_num) {
    // 将系统调用号绑定到x8寄存器（ARM64系统调用约定）
    register long x8 asm("x8") = syscall_num;
    // 声明x0作为返回值寄存器
    register long x0 asm("x0");
    
    asm volatile(
        "svc #0"                // 触发Supervisor Call异常，进入内核态
        : "=r"(x0)              // 输出约束：x0寄存器包含系统调用返回值
        : "r"(x8)               // 输入约束：x8寄存器包含系统调用号
        : "memory", "cc"        // 破坏性约束：内存和条件码可能被修改
    );
    
    return x0;                   // 返回系统调用结果
}

/**
 * 带1个参数的ARM64 SVC调用
 * 参数传递约定：x0-x7寄存器依次传递前8个参数
 */
long svc_call1(long syscall_num, long arg1) {
    register long x8 asm("x8") = syscall_num;  // 系统调用号
    register long x0 asm("x0") = arg1;         // 第1个参数通过x0传递
    
    asm volatile(
        "svc #0"                // 执行系统调用
        : "+r"(x0)              // 输入输出约束：x0既是输入参数也是输出结果
        : "r"(x8)               // 输入约束：系统调用号
        : "memory", "cc"        // 破坏性约束
    );
    
    return x0;                   // 返回内核处理结果
}

/**
 * 带2个参数的ARM64 SVC调用
 * ARM64参数传递：x0=arg1, x1=arg2, x8=syscall_num
 */
long svc_call2(long syscall_num, long arg1, long arg2) {
    register long x8 asm("x8") = syscall_num;  // 系统调用号
    register long x0 asm("x0") = arg1;         // 第1个参数
    register long x1 asm("x1") = arg2;         // 第2个参数
    
    asm volatile(
        "svc #0"                // 执行系统调用
        : "+r"(x0)              // x0：输入第1个参数，输出返回值
        : "r"(x8), "r"(x1)      // x8：系统调用号，x1：第2个参数
        : "memory", "cc"        // 内存屏障和条件码破坏
    );
    
    return x0;
}

/**
 * 带3个参数的ARM64 SVC调用
 * 寄存器使用：x0-x2传递参数，x8传递系统调用号
 */
long svc_call3(long syscall_num, long arg1, long arg2, long arg3) {
    register long x8 asm("x8") = syscall_num;  // 系统调用号
    register long x0 asm("x0") = arg1;         // 第1个参数
    register long x1 asm("x1") = arg2;         // 第2个参数
    register long x2 asm("x2") = arg3;         // 第3个参数
    
    asm volatile(
        "svc #0"                     // 执行系统调用
        : "+r"(x0)                   // x0：输入输出寄存器
        : "r"(x8), "r"(x1), "r"(x2)  // 输入寄存器：系统调用号和参数
        : "memory", "cc"             // 破坏性约束
    );
    
    return x0;
}

/**
 * 带4个参数的ARM64 SVC调用
 * 参数分布：x0-x3依次传递4个参数
 */
long svc_call4(long syscall_num, long arg1, long arg2, long arg3, long arg4) {
    register long x8 asm("x8") = syscall_num;
    register long x0 asm("x0") = arg1;
    register long x1 asm("x1") = arg2;
    register long x2 asm("x2") = arg3;
    register long x3 asm("x3") = arg4;
    
    asm volatile(
        "svc #0"
        : "+r"(x0)
        : "r"(x8), "r"(x1), "r"(x2), "r"(x3)
        : "memory", "cc"
    );
    
    return x0;
}

/**
 * 带5个参数的ARM64 SVC调用
 * 参数分布：x0-x4依次传递5个参数
 */
long svc_call5(long syscall_num, long arg1, long arg2, long arg3, long arg4, long arg5) {
    register long x8 asm("x8") = syscall_num;
    register long x0 asm("x0") = arg1;
    register long x1 asm("x1") = arg2;
    register long x2 asm("x2") = arg3;
    register long x3 asm("x3") = arg4;
    register long x4 asm("x4") = arg5;
    
    asm volatile(
        "svc #0"
        : "+r"(x0)
        : "r"(x8), "r"(x1), "r"(x2), "r"(x3), "r"(x4)
        : "memory", "cc"
    );
    
    return x0;
}

/**
 * 带6个参数的ARM64 SVC调用（最大参数数量）
 * 参数分布：x0-x5依次传递6个参数，x8传递系统调用号
 * Linux ARM64最多支持6个寄存器参数，超出部分需通过栈传递
 */
long svc_call6(long syscall_num, long arg1, long arg2, long arg3, long arg4, long arg5, long arg6) {
    register long x8 asm("x8") = syscall_num;  // 系统调用号寄存器
    register long x0 asm("x0") = arg1;         // 参数寄存器x0-x5
    register long x1 asm("x1") = arg2;
    register long x2 asm("x2") = arg3;
    register long x3 asm("x3") = arg4;
    register long x4 asm("x4") = arg5;
    register long x5 asm("x5") = arg6;
    
    asm volatile(
        "svc #0"                                      // 执行系统调用
        : "+r"(x0)                                    // x0既是输入参数也是返回值
        : "r"(x8), "r"(x1), "r"(x2), "r"(x3), "r"(x4), "r"(x5)  // 输入约束
        : "memory", "cc"                              // 破坏性约束
    );
    
    return x0;  // 返回内核执行结果
}

#elif defined(__arm__)

// ========== ARM32 SVC调用实现 ==========

/**
 * ARM32 SVC调用执行原理:
 * 1. 将系统调用号加载到r7寄存器（ARM32 EABI约定）
 * 2. 执行svc #0指令触发软中断异常
 * 3. CPU从用户态切换到管理态（Supervisor Mode）
 * 4. 处理器跳转到异常向量表中的SWI处理程序
 * 5. 内核根据r7中的系统调用号查找系统调用表
 * 6. 执行对应的内核函数，返回值通过r0寄存器传递
 */
long svc_call0(long syscall_num) {
    // ARM32系统调用号通过r7寄存器传递
    register long r7 asm("r7") = syscall_num;
    // r0寄存器用于接收返回值
    register long r0 asm("r0");
    
    asm volatile(
        "svc #0"                // 执行软件中断，触发系统调用
        : "=r"(r0)              // 输出约束：r0包含返回值
        : "r"(r7)               // 输入约束：r7包含系统调用号
        : "memory", "cc"        // 破坏性约束：内存和条件码可能变化
    );
    
    return r0;                   // 返回系统调用结果
}

/**
 * 带1个参数的ARM32 SVC调用
 * ARM32 AAPCS约定：r0-r3寄存器传递前4个参数
 */
long svc_call1(long syscall_num, long arg1) {
    register long r7 asm("r7") = syscall_num;  // 系统调用号
    register long r0 asm("r0") = arg1;         // 第1个参数通过r0传递
    
    asm volatile(
        "svc #0"                // 触发系统调用
        : "+r"(r0)              // r0既是输入参数也是输出结果
        : "r"(r7)               // r7传递系统调用号
        : "memory", "cc"        // 破坏性约束
    );
    
    return r0;
}

/**
 * 带2个参数的ARM32 SVC调用
 * 参数分布：r0=arg1, r1=arg2, r7=syscall_num
 */
long svc_call2(long syscall_num, long arg1, long arg2) {
    register long r7 asm("r7") = syscall_num;  // 系统调用号寄存器
    register long r0 asm("r0") = arg1;         // 第1个参数
    register long r1 asm("r1") = arg2;         // 第2个参数
    
    asm volatile(
        "svc #0"                // 执行系统调用
        : "+r"(r0)              // r0：输入参数并接收返回值
        : "r"(r7), "r"(r1)      // 输入约束：系统调用号和第2个参数
        : "memory", "cc"        // 内存屏障和条件码破坏约束
    );
    
    return r0;
}

/**
 * 带3个参数的ARM32 SVC调用
 * 寄存器使用：r0-r2传递参数，r7传递系统调用号
 */
long svc_call3(long syscall_num, long arg1, long arg2, long arg3) {
    register long r7 asm("r7") = syscall_num;  // 系统调用号
    register long r0 asm("r0") = arg1;         // 第1个参数
    register long r1 asm("r1") = arg2;         // 第2个参数
    register long r2 asm("r2") = arg3;         // 第3个参数
    
    asm volatile(
        "svc #0"                     // 执行系统调用
        : "+r"(r0)                   // r0：输入输出寄存器
        : "r"(r7), "r"(r1), "r"(r2)  // 输入寄存器：系统调用号和参数
        : "memory", "cc"             // 破坏性约束
    );
    
    return r0;
}

/**
 * 带4个参数的ARM32 SVC调用
 * ARM32最多可通过r0-r3四个寄存器传递参数
 */
long svc_call4(long syscall_num, long arg1, long arg2, long arg3, long arg4) {
    register long r7 asm("r7") = syscall_num;  // 系统调用号
    register long r0 asm("r0") = arg1;         // 第1个参数
    register long r1 asm("r1") = arg2;         // 第2个参数
    register long r2 asm("r2") = arg3;         // 第3个参数
    register long r3 asm("r3") = arg4;         // 第4个参数
    
    asm volatile(
        "svc #0"                          // 执行系统调用
        : "+r"(r0)                        // r0既是输入也是输出
        : "r"(r7), "r"(r1), "r"(r2), "r"(r3)  // 输入寄存器约束
        : "memory", "cc"                  // 破坏性约束
    );
    
    return r0;
}

/**
 * 带5个参数的ARM32 SVC调用
 * 超过r0-r3的参数需使用r4等额外寄存器
 * 注意：r4可能被内核传参使用，但不是所有系统都支持
 */
long svc_call5(long syscall_num, long arg1, long arg2, long arg3, long arg4, long arg5) {
    register long r7 asm("r7") = syscall_num;
    register long r0 asm("r0") = arg1;
    register long r1 asm("r1") = arg2;
    register long r2 asm("r2") = arg3;
    register long r3 asm("r3") = arg4;
    register long r4 asm("r4") = arg5;         // 第5个参数（扩展寄存器）
    
    asm volatile(
        "svc #0"
        : "+r"(r0)
        : "r"(r7), "r"(r1), "r"(r2), "r"(r3), "r"(r4)
        : "memory", "cc"
    );
    
    return r0;
}

/**
 * 带6个参数的ARM32 SVC调用
 * 使用r0-r5六个寄存器传递参数，超出标准AAPCS约定
 * 注意：这可能不被所有ARM32 Linux系统支持
 */
long svc_call6(long syscall_num, long arg1, long arg2, long arg3, long arg4, long arg5, long arg6) {
    register long r7 asm("r7") = syscall_num;  // 系统调用号寄存器
    register long r0 asm("r0") = arg1;         // 参数寄存器r0-r5
    register long r1 asm("r1") = arg2;
    register long r2 asm("r2") = arg3;
    register long r3 asm("r3") = arg4;
    register long r4 asm("r4") = arg5;
    register long r5 asm("r5") = arg6;         // 第6个参数（扩展寄存器）
    
    asm volatile(
        "svc #0"                                          // 执行系统调用
        : "+r"(r0)                                        // r0既是参数也是返回值
        : "r"(r7), "r"(r1), "r"(r2), "r"(r3), "r"(r4), "r"(r5)  // 输入寄存器约束
        : "memory", "cc"                                  // 破坏性约束
    );
    
    return r0;  // 返回内核执行结果
}

#else
// 非 ARM 架构的模拟实现（用于桌面平台测试）
static inline long svc_call(long number, long arg1, long arg2, long arg3, long arg4, long arg5, long arg6) {
    // 在非 ARM 平台上，使用标准系统调用
    switch (number) {
        case __NR_getpid:
            return getpid();
        case __NR_getuid:
            return getuid();
        default:
            return -1; // 不支持的系统调用
    }
}
#endif

// ========== 文件系统操作实现 ==========

int svc_openat(const char* path, int flags) {
    long result = svc_call3(__NR_openat, AT_FDCWD, (long)path, flags);
    return (int)result;
}

ssize_t svc_read(int fd, void* buffer, size_t count) {
    long result = svc_call3(__NR_read, fd, (long)buffer, count);
    return (ssize_t)result;
}

int svc_close(int fd) {
    long result = svc_call1(__NR_close, fd);
    return (int)result;
}

int svc_stat(const char* path, struct stat* statbuf) {
    long result = svc_call2(__NR_stat, (long)path, (long)statbuf);
    return (int)result;
}

// ========== 进程信息获取实现 ==========

pid_t svc_getpid(void) {
    long result = svc_call0(__NR_getpid);
    return (pid_t)result;
}

uid_t svc_getuid(void) {
    long result = svc_call0(__NR_getuid);
    return (uid_t)result;
}

pid_t svc_gettid(void) {
    long result = svc_call0(__NR_gettid);
    return (pid_t)result;
}

pid_t svc_getppid(void) {
    long result = svc_call0(__NR_getppid);
    return (pid_t)result;
}

// ========== 系统信息获取实现 ==========

int svc_uname(struct utsname* buf) {
    long result = svc_call1(__NR_uname, (long)buf);
    return (int)result;
}

char* svc_getcwd(char* buf, size_t size) {
    long result = svc_call2(__NR_getcwd, (long)buf, size);
    if (result < 0) {
        return NULL;
    }
    return buf;
}

// ========== 高级设备指纹获取实现 ==========

int svc_get_cpu_info(char* cpu_info, size_t max_len) {
    int fd = svc_openat("/proc/cpuinfo", O_RDONLY);
    if (fd < 0) {
        return -1;
    }
    
    ssize_t bytes_read = svc_read(fd, cpu_info, max_len - 1);
    svc_close(fd);
    
    if (bytes_read < 0) {
        return -1;
    }
    
    cpu_info[bytes_read] = '\0';
    return 0;
}

int svc_get_memory_info(device_info_svc_t* device_info) {
    char meminfo[1024];
    int fd = svc_openat("/proc/meminfo", O_RDONLY);
    if (fd < 0) {
        return -1;
    }
    
    ssize_t bytes_read = svc_read(fd, meminfo, sizeof(meminfo) - 1);
    svc_close(fd);
    
    if (bytes_read < 0) {
        return -1;
    }
    
    meminfo[bytes_read] = '\0';
    
    // 解析内存信息
    char* line = meminfo;
    while (line && *line) {
        if (strncmp(line, "MemTotal:", 9) == 0) {
            sscanf(line + 9, "%zu", &device_info->memory_total);
        } else if (strncmp(line, "MemAvailable:", 13) == 0) {
            sscanf(line + 13, "%zu", &device_info->memory_available);
        }
        
        // 移动到下一行
        line = strchr(line, '\n');
        if (line) line++;
    }
    
    return 0;
}

int svc_get_build_info(char* build_info, size_t max_len) {
    // 尝试读取多个系统属性文件
    const char* prop_files[] = {
        "/system/build.prop",
        "/vendor/build.prop",
        "/system/etc/prop.default",
        NULL
    };
    
    for (int i = 0; prop_files[i]; i++) {
        int fd = svc_openat(prop_files[i], O_RDONLY);
        if (fd >= 0) {
            ssize_t bytes_read = svc_read(fd, build_info, max_len - 1);
            svc_close(fd);
            
            if (bytes_read > 0) {
                build_info[bytes_read] = '\0';
                return 0;
            }
        }
    }
    
    return -1;
}

int svc_collect_device_fingerprint(device_info_svc_t* device_info) {
    if (!device_info) return -1;
    
    // 清零结构体
    memset(device_info, 0, sizeof(device_info_svc_t));
    
    // 获取进程信息
    device_info->process_id = svc_getpid();
    device_info->parent_pid = svc_getppid();
    device_info->thread_id = svc_gettid();
    device_info->real_uid = svc_getuid();
    device_info->effective_uid = svc_getuid(); // 简化处理
    
    // 获取系统信息
    struct utsname sys_info;
    if (svc_uname(&sys_info) == 0) {
        strncpy(device_info->kernel_version, sys_info.release, sizeof(device_info->kernel_version) - 1);
        strncpy(device_info->cpu_abi, sys_info.machine, sizeof(device_info->cpu_abi) - 1);
    }
    
    // 获取内存信息
    svc_get_memory_info(device_info);
    
    // 获取构建信息（简化处理）
    char build_buffer[512];
    if (svc_get_build_info(build_buffer, sizeof(build_buffer)) == 0) {
        // 提取关键信息
        char* fingerprint_line = strstr(build_buffer, "ro.build.fingerprint=");
        if (fingerprint_line) {
            char* end = strchr(fingerprint_line, '\n');
            size_t len = end ? (end - fingerprint_line - 21) : strlen(fingerprint_line + 21);
            len = len < sizeof(device_info->build_fingerprint) - 1 ? len : sizeof(device_info->build_fingerprint) - 1;
            strncpy(device_info->build_fingerprint, fingerprint_line + 21, len);
        }
    }
    
    return 0;
}

// ========== 反Hook检测实现 ==========

int svc_detect_syscall_hook(void) {
    // 简单的Hook检测：比较SVC调用和标准库调用的结果
    
    // 测试getpid系统调用
    pid_t svc_pid = svc_getpid();
    pid_t libc_pid = getpid();
    
    if (svc_pid != libc_pid) {
        return 1; // 检测到Hook
    }
    
    // 测试更多系统调用
    uid_t svc_uid = svc_getuid();
    uid_t libc_uid = getuid();
    
    if (svc_uid != libc_uid) {
        return 1; // 检测到Hook
    }
    
    return 0; // 未检测到Hook
}

int svc_compare_with_libc(int syscall_num) {
    switch (syscall_num) {
        case __NR_getpid: {
            pid_t svc_result = svc_getpid();
            pid_t libc_result = getpid();
            return svc_result != libc_result;
        }
        case __NR_getuid: {
            uid_t svc_result = svc_getuid();
            uid_t libc_result = getuid();
            return svc_result != libc_result;
        }
        default:
            return 0; // 未知系统调用，假定一致
    }
}

int svc_verify_syscall_table(void) {
    // 验证系统调用表的完整性（简化实现）
    
    // 检查关键系统调用的一致性
    int syscalls_to_check[] = {__NR_getpid, __NR_getuid, __NR_gettid, 0};
    
    for (int i = 0; syscalls_to_check[i] != 0; i++) {
        if (svc_compare_with_libc(syscalls_to_check[i])) {
            return 0; // 发现不一致，系统调用表可能被篡改
        }
    }
    
    return 1; // 系统调用表完整
}

// ========== 内存映射操作实现 ==========

void* svc_mmap(void* addr, size_t length, int prot, int flags, int fd, off_t offset) {
    long result = svc_call6(__NR_mmap, (long)addr, length, prot, flags, fd, offset);
    return (void*)result;
}

int svc_munmap(void* addr, size_t length) {
    long result = svc_call2(__NR_munmap, (long)addr, length);
    return (int)result;
}

// ========== 时间相关实现 ==========

int svc_clock_gettime(clockid_t clk_id, struct timespec* tp) {
    long result = svc_call2(__NR_clock_gettime, clk_id, (long)tp);
    return (int)result;
}

// ========== 工具函数实现 ==========

int get_cpu_arch(void) {
    if (g_cpu_arch != -1) {
        return g_cpu_arch;
    }
    
#ifdef __aarch64__
    g_cpu_arch = 1; // ARM64
#elif defined(__arm__)
    g_cpu_arch = 0; // ARM32
#else
    g_cpu_arch = -1; // 未知
#endif
    
    return g_cpu_arch;
}

int is_svc_intercepted(void) {
    // 通过时间差检测SVC是否被拦截
    struct timespec start, end;
    
    // 测量正常SVC调用时间
    svc_clock_gettime(CLOCK_MONOTONIC, &start);
    svc_getpid(); // 简单的系统调用
    svc_clock_gettime(CLOCK_MONOTONIC, &end);
    
    // 计算耗时（纳秒）
    long duration = (end.tv_sec - start.tv_sec) * 1000000000L + (end.tv_nsec - start.tv_nsec);
    
    // 如果耗时过长，可能被拦截了
    return duration > 1000000; // 1毫秒阈值
}

int svc_init(void) {
    if (g_svc_initialized) {
        return 0;
    }
    
    // 检测CPU架构
    get_cpu_arch();
    
    // 验证SVC调用是否正常工作
    pid_t test_pid = svc_getpid();
    if (test_pid <= 0) {
        return -1; // SVC调用失败
    }
    
    // 检测是否被拦截
    if (is_svc_intercepted()) {
        // 被拦截但不阻止初始化，只是记录状态
    }
    
    g_svc_initialized = 1;
    return 0;
}

void svc_cleanup(void) {
    g_svc_initialized = 0;
    g_cpu_arch = -1;
}