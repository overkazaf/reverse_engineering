#ifndef SVC_SYSCALL_H
#define SVC_SYSCALL_H

#include <stdint.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>     // for struct stat
#include <sys/utsname.h>  // for struct utsname

// ARM64 系统调用号定义
#define __NR_openat     56
#define __NR_read       63
#define __NR_write      64
#define __NR_close      57
#define __NR_getpid     172
#define __NR_getuid     174
#define __NR_gettid     178
#define __NR_getppid    173
#define __NR_getcwd     17
#define __NR_uname      160
#define __NR_getdents64 61
#define __NR_stat       106
#define __NR_mmap       222
#define __NR_munmap     215
#define __NR_prctl      167
#define __NR_clock_gettime 113

// ARM32 系统调用号定义 (备用)
#define __NR32_openat   322
#define __NR32_read     3
#define __NR32_write    4
#define __NR32_close    6
#define __NR32_getpid   20

// AT_* 常量 (用于openat)
#define AT_FDCWD        -100
#define O_RDONLY        0
#define O_WRONLY        1
#define O_RDWR          2

// SVC调用结果结构体
typedef struct {
    long result;
    int error_code;
    char error_msg[128];
} svc_result_t;

// 设备信息结构体
typedef struct {
    char device_model[64];
    char cpu_abi[32];
    char kernel_version[128];
    char build_fingerprint[256];
    uint32_t cpu_features;
    size_t memory_total;
    size_t memory_available;
    uid_t real_uid;
    uid_t effective_uid;
    pid_t process_id;
    pid_t parent_pid;
    pid_t thread_id;
} device_info_svc_t;

#ifdef __cplusplus
extern "C" {
#endif

// ========== SVC系统调用封装函数 ==========

/**
 * 通用SVC系统调用接口
 * @param syscall_num 系统调用号
 * @param arg1-arg6 系统调用参数
 * @return 系统调用返回值
 */
long svc_call0(long syscall_num);
long svc_call1(long syscall_num, long arg1);
long svc_call2(long syscall_num, long arg1, long arg2);
long svc_call3(long syscall_num, long arg1, long arg2, long arg3);
long svc_call4(long syscall_num, long arg1, long arg2, long arg3, long arg4);
long svc_call5(long syscall_num, long arg1, long arg2, long arg3, long arg4, long arg5);
long svc_call6(long syscall_num, long arg1, long arg2, long arg3, long arg4, long arg5, long arg6);

// ========== 文件系统操作 (绕过libc) ==========

/**
 * 直接通过SVC打开文件
 * @param path 文件路径
 * @param flags 打开标志
 * @return 文件描述符或错误码
 */
int svc_openat(const char* path, int flags);

/**
 * 直接通过SVC读取文件
 * @param fd 文件描述符
 * @param buffer 缓冲区
 * @param count 读取字节数
 * @return 实际读取字节数或错误码
 */
ssize_t svc_read(int fd, void* buffer, size_t count);

/**
 * 直接通过SVC关闭文件
 * @param fd 文件描述符
 * @return 0成功，否则错误码
 */
int svc_close(int fd);

/**
 * 直接通过SVC获取文件状态
 * @param path 文件路径
 * @param statbuf 状态缓冲区
 * @return 0成功，否则错误码
 */
int svc_stat(const char* path, struct stat* statbuf);

// ========== 进程信息获取 (绕过libc) ==========

/**
 * 通过SVC获取进程ID
 * @return 进程ID
 */
pid_t svc_getpid(void);

/**
 * 通过SVC获取用户ID
 * @return 用户ID
 */
uid_t svc_getuid(void);

/**
 * 通过SVC获取线程ID
 * @return 线程ID
 */
pid_t svc_gettid(void);

/**
 * 通过SVC获取父进程ID
 * @return 父进程ID
 */
pid_t svc_getppid(void);

// ========== 系统信息获取 ==========

/**
 * 通过SVC获取系统信息
 * @param buf 系统信息缓冲区
 * @return 0成功，否则错误码
 */
int svc_uname(struct utsname* buf);

/**
 * 通过SVC获取当前工作目录
 * @param buf 缓冲区
 * @param size 缓冲区大小
 * @return 成功返回缓冲区指针，失败返回NULL
 */
char* svc_getcwd(char* buf, size_t size);

// ========== 高级设备指纹获取 ==========

/**
 * 通过SVC直接读取CPU信息
 * @param cpu_info 输出缓冲区
 * @param max_len 缓冲区最大长度
 * @return 0成功，否则错误码
 */
int svc_get_cpu_info(char* cpu_info, size_t max_len);

/**
 * 通过SVC直接读取内存信息
 * @param mem_info 内存信息结构体
 * @return 0成功，否则错误码
 */
int svc_get_memory_info(device_info_svc_t* mem_info);

/**
 * 通过SVC直接读取系统构建信息
 * @param build_info 输出缓冲区
 * @param max_len 缓冲区最大长度
 * @return 0成功，否则错误码
 */
int svc_get_build_info(char* build_info, size_t max_len);

/**
 * 通过SVC获取完整设备指纹
 * @param device_info 设备信息结构体
 * @return 0成功，否则错误码
 */
int svc_collect_device_fingerprint(device_info_svc_t* device_info);

// ========== 反Hook检测 ==========

/**
 * 检测系统调用是否被Hook
 * @return 1被Hook，0正常
 */
int svc_detect_syscall_hook(void);

/**
 * 比较SVC调用和libc调用的结果
 * @param syscall_num 系统调用号
 * @return 1不一致(可能被Hook)，0一致
 */
int svc_compare_with_libc(int syscall_num);

/**
 * 验证系统调用表完整性
 * @return 1完整，0被篡改
 */
int svc_verify_syscall_table(void);

// ========== 内存映射操作 ==========

/**
 * 通过SVC进行内存映射
 * @param addr 映射地址
 * @param length 映射长度
 * @param prot 保护属性
 * @param flags 映射标志
 * @param fd 文件描述符
 * @param offset 文件偏移
 * @return 映射地址或MAP_FAILED
 */
void* svc_mmap(void* addr, size_t length, int prot, int flags, int fd, off_t offset);

/**
 * 通过SVC取消内存映射
 * @param addr 映射地址
 * @param length 映射长度
 * @return 0成功，否则错误码
 */
int svc_munmap(void* addr, size_t length);

// ========== 时间相关 ==========

/**
 * 通过SVC获取系统时间
 * @param clk_id 时钟ID
 * @param tp 时间结构体
 * @return 0成功，否则错误码
 */
int svc_clock_gettime(clockid_t clk_id, struct timespec* tp);

// ========== 工具函数 ==========

/**
 * 获取当前CPU架构
 * @return 0=ARM32, 1=ARM64, -1=未知
 */
int get_cpu_arch(void);

/**
 * 检查SVC调用是否被拦截
 * @return 1被拦截，0正常
 */
int is_svc_intercepted(void);

/**
 * 初始化SVC模块
 * @return 0成功，否则错误码
 */
int svc_init(void);

/**
 * 清理SVC模块
 */
void svc_cleanup(void);

#ifdef __cplusplus
}
#endif

#endif // SVC_SYSCALL_H