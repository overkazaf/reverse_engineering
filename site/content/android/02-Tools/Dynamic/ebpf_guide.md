---
title: "eBPF 使用指南"
date: 2025-12-27
tags: ["eBPF", "内核追踪", "系统调用", "动态分析", "Android"]
weight: 7
type: posts
---

# eBPF 使用指南

eBPF (extended Berkeley Packet Filter) 是 Linux 内核中的一项革命性技术，允许在内核空间运行沙盒程序而无需修改内核代码。在 Android 逆向工程中，eBPF 提供了比 Frida 更底层、更隐蔽的追踪能力。

---

## 为什么选择 eBPF

### 与其他工具对比

| 特性 | eBPF | Frida | Xposed |
|------|------|-------|--------|
| 检测难度 | 极难 | 中等 | 容易 |
| 内核级追踪 | 原生支持 | 不支持 | 不支持 |
| 性能开销 | 极低 | 中等 | 中等 |
| 系统调用追踪 | 原生支持 | 需要额外实现 | 不支持 |
| 网络包捕获 | 原生支持 | 不支持 | 不支持 |
| Root 需求 | 是 | 是 | 是 |
| Android 支持 | 4.14+ 内核 | 广泛 | 广泛 |

### eBPF 的优势

1. **隐蔽性**: 运行在内核空间，应用层检测极其困难
2. **性能**: JIT 编译，接近原生性能
3. **安全性**: 内核验证器确保程序安全
4. **全面性**: 可追踪系统调用、网络、文件系统等各个层面

---

## 环境准备

### 检查内核支持

```bash
# 检查内核版本（需要 4.14+）
adb shell uname -r

# 检查 eBPF 支持
adb shell ls /sys/fs/bpf/

# 检查 CONFIG_BPF 相关配置
adb shell zcat /proc/config.gz | grep -i bpf
```

需要确认以下内核配置启用:
```
CONFIG_BPF=y
CONFIG_BPF_SYSCALL=y
CONFIG_BPF_JIT=y
CONFIG_HAVE_EBPF_JIT=y
CONFIG_BPF_EVENTS=y
```

### 安装 bpftrace (推荐)

bpftrace 是 eBPF 的高级追踪语言，类似于 awk 和 DTrace。

**在 Android 上安装:**

```bash
# 下载预编译的 bpftrace (需要 root)
# https://github.com/aspect-build/bpftrace-android

# 推送到设备
adb push bpftrace /data/local/tmp/
adb shell chmod +x /data/local/tmp/bpftrace

# 测试运行
adb shell /data/local/tmp/bpftrace -e 'BEGIN { printf("eBPF works!\n"); }'
```

### 安装 BCC 工具集

BCC (BPF Compiler Collection) 提供了丰富的预置追踪工具。

```bash
# 交叉编译 BCC for Android
# 或使用预编译版本

# 常用工具
# - opensnoop: 追踪文件打开
# - execsnoop: 追踪进程执行
# - tcpconnect: 追踪 TCP 连接
# - trace: 通用函数追踪
```

---

## 快速入门

### Hello World

```bash
# 最简单的 bpftrace 脚本
adb shell /data/local/tmp/bpftrace -e '
BEGIN {
    printf("开始追踪...\n");
}

END {
    printf("追踪结束\n");
}'
```

### 追踪系统调用

```bash
# 追踪特定应用的所有系统调用
adb shell /data/local/tmp/bpftrace -e '
tracepoint:raw_syscalls:sys_enter
/comm == "com.target.app"/
{
    @syscalls[args->id] = count();
}

END {
    print(@syscalls);
}'
```

### 追踪文件操作

```bash
# 追踪文件打开操作
adb shell /data/local/tmp/bpftrace -e '
tracepoint:syscalls:sys_enter_openat
/comm == "com.target.app"/
{
    printf("%s opened: %s\n", comm, str(args->filename));
}'
```

---

## 核心概念

### 程序类型

eBPF 支持多种程序类型:

| 类型 | 用途 | Android 逆向场景 |
|------|------|-----------------|
| kprobe/kretprobe | 内核函数追踪 | 追踪内核行为 |
| uprobe/uretprobe | 用户态函数追踪 | 追踪应用函数 |
| tracepoint | 内核静态追踪点 | 系统调用追踪 |
| socket_filter | 网络包过滤 | 网络流量分析 |
| xdp | 高性能网络处理 | 网络数据包分析 |

### Maps 数据结构

eBPF Maps 用于在内核和用户空间之间共享数据:

```c
// 常用 Map 类型
BPF_HASH(counts, u32);        // 哈希表
BPF_ARRAY(data, u64, 256);    // 数组
BPF_PERF_OUTPUT(events);      // 性能事件输出
BPF_STACK_TRACE(stacks, 128); // 调用栈追踪
```

### 辅助函数

```c
// 常用 eBPF 辅助函数
bpf_get_current_pid_tgid()    // 获取进程/线程 ID
bpf_get_current_comm()        // 获取进程名
bpf_probe_read()              // 安全读取内存
bpf_ktime_get_ns()           // 获取时间戳
bpf_trace_printk()           // 调试输出
```

---

## 实战场景

### 场景1: 追踪加密函数调用

追踪应用调用的 OpenSSL 加密函数:

```bash
adb shell /data/local/tmp/bpftrace -e '
uprobe:/system/lib64/libcrypto.so:EVP_EncryptInit_ex
/comm == "com.target.app"/
{
    printf("[%d] EVP_EncryptInit_ex called\n", pid);
    printf("  ctx: %p\n", arg0);
    printf("  type: %p\n", arg1);
}

uprobe:/system/lib64/libcrypto.so:EVP_EncryptUpdate
/comm == "com.target.app"/
{
    printf("[%d] EVP_EncryptUpdate\n", pid);
    printf("  input len: %d\n", arg3);
}
'
```

### 场景2: 监控网络连接

```bash
adb shell /data/local/tmp/bpftrace -e '
tracepoint:syscalls:sys_enter_connect
/comm == "com.target.app"/
{
    $sa = (struct sockaddr *)args->uservaddr;
    if ($sa->sa_family == 2) { // AF_INET
        $sin = (struct sockaddr_in *)$sa;
        printf("Connect to %s:%d\n",
            ntop(AF_INET, $sin->sin_addr.s_addr),
            ntohs($sin->sin_port));
    }
}'
```

### 场景3: 文件访问监控

```bash
adb shell /data/local/tmp/bpftrace -e '
tracepoint:syscalls:sys_enter_openat
/comm == "com.target.app"/
{
    @files[str(args->filename)] = count();
}

tracepoint:syscalls:sys_enter_read
/comm == "com.target.app"/
{
    @read_bytes = sum(args->count);
}

tracepoint:syscalls:sys_enter_write
/comm == "com.target.app"/
{
    @write_bytes = sum(args->count);
}

END {
    printf("\n=== 文件访问统计 ===\n");
    print(@files);
    printf("\n读取字节: %d\n", @read_bytes);
    printf("写入字节: %d\n", @write_bytes);
}'
```

### 场景4: JNI 调用追踪

```bash
# 追踪 JNI 函数调用
adb shell /data/local/tmp/bpftrace -e '
uprobe:/system/lib64/libart.so:*JNI*
/comm == "com.target.app"/
{
    printf("[JNI] %s\n", probe);
}'
```

### 场景5: 检测反调试行为

```bash
# 监控常见的反调试系统调用
adb shell /data/local/tmp/bpftrace -e '
tracepoint:syscalls:sys_enter_ptrace
{
    printf("[Anti-Debug] ptrace called by %s (PID: %d)\n", comm, pid);
    printf("  request: %d\n", args->request);
}

tracepoint:syscalls:sys_enter_prctl
{
    printf("[Anti-Debug] prctl called by %s\n", comm);
    printf("  option: %d\n", args->option);
}

kprobe:proc_pid_status
{
    printf("[Anti-Debug] /proc/pid/status read by %s\n", comm);
}'
```

---

## 高级技巧

### 1. 条件过滤

```bash
# 只追踪特定 UID 的进程
adb shell /data/local/tmp/bpftrace -e '
tracepoint:syscalls:sys_enter_*
/uid == 10123/  // 目标应用的 UID
{
    @syscalls[probe] = count();
}'
```

### 2. 调用栈追踪

```bash
# 获取完整调用栈
adb shell /data/local/tmp/bpftrace -e '
uprobe:/data/app/com.target.app-*/lib/arm64/libnative.so:suspicious_function
{
    printf("Function called!\n");
    printf("User stack:\n%s\n", ustack);
    printf("Kernel stack:\n%s\n", kstack);
}'
```

### 3. 时间统计

```bash
# 统计函数执行时间
adb shell /data/local/tmp/bpftrace -e '
uprobe:/data/app/com.target.app-*/lib/arm64/libnative.so:target_function
{
    @start[tid] = nsecs;
}

uretprobe:/data/app/com.target.app-*/lib/arm64/libnative.so:target_function
/@start[tid]/
{
    $duration = nsecs - @start[tid];
    @time = hist($duration);
    delete(@start[tid]);
}'
```

### 4. 内存访问追踪

```bash
# 追踪内存分配
adb shell /data/local/tmp/bpftrace -e '
uprobe:/apex/com.android.runtime/lib64/bionic/libc.so:malloc
/comm == "com.target.app"/
{
    @malloc_size = hist(arg0);
    @total_alloc = sum(arg0);
}

uretprobe:/apex/com.android.runtime/lib64/bionic/libc.so:malloc
/comm == "com.target.app"/
{
    printf("malloc returned: %p\n", retval);
}'
```

---

## BCC Python 脚本

对于更复杂的追踪需求，可以使用 BCC Python API:

```python
#!/usr/bin/env python3
from bcc import BPF

# eBPF 程序
prog = """
#include <uapi/linux/ptrace.h>
#include <linux/sched.h>

struct data_t {
    u32 pid;
    u64 ts;
    char comm[TASK_COMM_LEN];
    char filename[256];
};

BPF_PERF_OUTPUT(events);

int trace_openat(struct pt_regs *ctx, int dfd, const char __user *filename) {
    struct data_t data = {};

    data.pid = bpf_get_current_pid_tgid() >> 32;
    data.ts = bpf_ktime_get_ns();
    bpf_get_current_comm(&data.comm, sizeof(data.comm));
    bpf_probe_read_user_str(&data.filename, sizeof(data.filename), filename);

    events.perf_submit(ctx, &data, sizeof(data));
    return 0;
}
"""

# 加载 BPF 程序
b = BPF(text=prog)
b.attach_kprobe(event="do_sys_openat2", fn_name="trace_openat")

# 处理事件
def print_event(cpu, data, size):
    event = b["events"].event(data)
    print(f"[{event.pid}] {event.comm.decode()}: {event.filename.decode()}")

b["events"].open_perf_buffer(print_event)

print("Tracing file opens... Ctrl+C to exit")
while True:
    try:
        b.perf_buffer_poll()
    except KeyboardInterrupt:
        break
```

---

## 常见问题

### Q: Android 设备不支持 eBPF？

检查内核版本和配置:
```bash
# 内核版本需要 >= 4.14
adb shell uname -r

# 部分厂商可能禁用了 BPF
adb shell zcat /proc/config.gz | grep BPF
```

解决方案:
1. 使用自定义内核 (如 LineageOS)
2. 使用 Android 模拟器 (支持更好)
3. 使用特定的 Root 方案

### Q: bpftrace 报错 "Failed to attach"？

```bash
# 检查 SELinux 状态
adb shell getenforce

# 临时禁用 (需要 root)
adb shell setenforce 0

# 检查内核符号
adb shell cat /proc/kallsyms | head
```

### Q: 如何追踪特定应用？

```bash
# 方法1: 使用进程名
/comm == "com.target.app"/

# 方法2: 使用 PID
/pid == 12345/

# 方法3: 使用 UID
/uid == 10123/

# 获取应用 UID
adb shell dumpsys package com.target.app | grep userId
```

---

## 工具推荐

### 1. bpftrace
- 官网: https://github.com/iovisor/bpftrace
- Android 版: https://github.com/aspect-build/bpftrace-android

### 2. BCC
- 官网: https://github.com/iovisor/bcc
- 文档: https://github.com/iovisor/bcc/blob/master/docs/reference_guide.md

### 3. libbpf
- 官网: https://github.com/libbpf/libbpf
- CO-RE (一次编译，到处运行)

### 4. eCapture
- 官网: https://github.com/gojue/ecapture
- 无需 CA 证书的 HTTPS 抓包工具

### 5. Tracee
- 官网: https://github.com/aquasecurity/tracee
- 安全事件追踪工具

---

## 延伸阅读

- [eBPF 内部原理](./ebpf_internals.md) - 深入理解 eBPF 工作机制
- [eBPF Android 逆向实战](../../01-Recipes/Analysis/ebpf_android_reversing.md) - Android 逆向场景实战
- [eBPF 脚本集](../../01-Recipes/Scripts/ebpf_scripts.md) - 可直接使用的脚本

---

## 参考资料

- [eBPF.io](https://ebpf.io/) - eBPF 官方网站
- [Linux Kernel BPF Documentation](https://www.kernel.org/doc/html/latest/bpf/)
- [BPF Performance Tools](https://www.brendangregg.com/bpf-performance-tools-book.html) - Brendan Gregg 的经典书籍
- [Android eBPF](https://source.android.com/docs/core/architecture/kernel/bpf) - Android 官方 eBPF 文档
