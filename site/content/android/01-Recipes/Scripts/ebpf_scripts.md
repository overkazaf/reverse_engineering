---
title: "eBPF 脚本集"
date: 2025-12-27
tags: ["eBPF", "bpftrace", "脚本", "追踪", "监控"]
weight: 7
type: posts
---

# eBPF 脚本集

本文提供可直接使用的 eBPF/bpftrace 脚本，覆盖 Android 逆向工程的常见场景。

---

## 系统调用追踪

### 追踪所有系统调用

```bash
#!/usr/bin/env bpftrace
// 文件: syscall_all.bt
// 用途: 统计目标应用的系统调用

tracepoint:raw_syscalls:sys_enter
/comm == "com.target.app"/
{
    @syscalls[args->id] = count();
}

END
{
    printf("\n=== 系统调用统计 ===\n");
    print(@syscalls);
}
```

### 追踪文件操作

```bash
#!/usr/bin/env bpftrace
// 文件: file_ops.bt
// 用途: 追踪文件打开、读写、关闭

tracepoint:syscalls:sys_enter_openat
/comm == "com.target.app"/
{
    @open_files[str(args->filename)] = count();
    printf("[OPEN] %s flags=%d\n", str(args->filename), args->flags);
}

tracepoint:syscalls:sys_enter_read
/comm == "com.target.app"/
{
    @read_count = count();
    @read_bytes = sum(args->count);
}

tracepoint:syscalls:sys_enter_write
/comm == "com.target.app"/
{
    @write_count = count();
    @write_bytes = sum(args->count);
}

tracepoint:syscalls:sys_enter_close
/comm == "com.target.app"/
{
    @close_count = count();
}

END
{
    printf("\n=== 文件操作统计 ===\n");
    printf("打开的文件:\n");
    print(@open_files);
    printf("\n读取: %d 次, %d 字节\n", @read_count, @read_bytes);
    printf("写入: %d 次, %d 字节\n", @write_count, @write_bytes);
    printf("关闭: %d 次\n", @close_count);
}
```

### 追踪敏感文件访问

```bash
#!/usr/bin/env bpftrace
// 文件: sensitive_files.bt
// 用途: 监控敏感文件的访问

tracepoint:syscalls:sys_enter_openat
{
    $filename = str(args->filename);

    // 检查敏感路径
    if (strcontains($filename, "/proc/") ||
        strcontains($filename, "/sys/") ||
        strcontains($filename, "/data/data/") ||
        strcontains($filename, "passwd") ||
        strcontains($filename, "shadow") ||
        strcontains($filename, ".key") ||
        strcontains($filename, ".pem")) {

        printf("[SENSITIVE] %s (PID:%d) opened: %s\n",
               comm, pid, $filename);
    }
}
```

---

## 网络追踪

### 追踪网络连接

```bash
#!/usr/bin/env bpftrace
// 文件: network_connect.bt
// 用途: 追踪 TCP/UDP 连接

#include <linux/socket.h>
#include <linux/in.h>

tracepoint:syscalls:sys_enter_connect
/comm == "com.target.app"/
{
    $sa = (struct sockaddr *)args->uservaddr;

    if ($sa->sa_family == AF_INET) {
        $sin = (struct sockaddr_in *)$sa;
        $port = ($sin->sin_port >> 8) | (($sin->sin_port & 0xff) << 8);
        $addr = $sin->sin_addr.s_addr;

        printf("[CONNECT] %d.%d.%d.%d:%d\n",
               $addr & 0xff,
               ($addr >> 8) & 0xff,
               ($addr >> 16) & 0xff,
               ($addr >> 24) & 0xff,
               $port);
    }
}

tracepoint:syscalls:sys_exit_connect
/comm == "com.target.app"/
{
    printf("  -> result: %d\n", args->ret);
}
```

### 追踪 DNS 查询

```bash
#!/usr/bin/env bpftrace
// 文件: dns_query.bt
// 用途: 追踪 DNS 解析

uprobe:/system/lib64/libc.so:getaddrinfo
/comm == "com.target.app"/
{
    printf("[DNS] Resolving: %s\n", str(arg0));
    @dns_queries[str(arg0)] = count();
}

uretprobe:/system/lib64/libc.so:getaddrinfo
/comm == "com.target.app"/
{
    printf("  -> result: %d\n", retval);
}
```

### 追踪 Socket 数据

```bash
#!/usr/bin/env bpftrace
// 文件: socket_data.bt
// 用途: 追踪 socket 发送接收的数据

tracepoint:syscalls:sys_enter_sendto
/comm == "com.target.app"/
{
    printf("[SEND] fd=%d len=%d\n", args->fd, args->len);
    @send_bytes = sum(args->len);
}

tracepoint:syscalls:sys_enter_recvfrom
/comm == "com.target.app"/
{
    @recv_pending[tid] = args->size;
}

tracepoint:syscalls:sys_exit_recvfrom
/comm == "com.target.app" && @recv_pending[tid]/
{
    $received = args->ret;
    if ($received > 0) {
        printf("[RECV] %d bytes\n", $received);
        @recv_bytes = sum($received);
    }
    delete(@recv_pending[tid]);
}

END
{
    printf("\n=== 网络统计 ===\n");
    printf("发送: %d 字节\n", @send_bytes);
    printf("接收: %d 字节\n", @recv_bytes);
}
```

---

## 加密函数追踪

### OpenSSL 追踪

```bash
#!/usr/bin/env bpftrace
// 文件: openssl_trace.bt
// 用途: 追踪 OpenSSL 加密操作

// EVP 加密初始化
uprobe:/system/lib64/libcrypto.so:EVP_EncryptInit_ex
/comm == "com.target.app"/
{
    printf("[CRYPTO] EVP_EncryptInit_ex\n");
    printf("  ctx: %p, cipher: %p\n", arg0, arg1);
    @encrypt_init = count();
}

// EVP 加密更新
uprobe:/system/lib64/libcrypto.so:EVP_EncryptUpdate
/comm == "com.target.app"/
{
    printf("[CRYPTO] EVP_EncryptUpdate len=%d\n", arg3);
    @encrypt_bytes = sum(arg3);
}

// EVP 解密初始化
uprobe:/system/lib64/libcrypto.so:EVP_DecryptInit_ex
/comm == "com.target.app"/
{
    printf("[CRYPTO] EVP_DecryptInit_ex\n");
    @decrypt_init = count();
}

// EVP 解密更新
uprobe:/system/lib64/libcrypto.so:EVP_DecryptUpdate
/comm == "com.target.app"/
{
    printf("[CRYPTO] EVP_DecryptUpdate len=%d\n", arg3);
    @decrypt_bytes = sum(arg3);
}

// HMAC
uprobe:/system/lib64/libcrypto.so:HMAC
/comm == "com.target.app"/
{
    printf("[CRYPTO] HMAC data_len=%d\n", arg3);
    @hmac_count = count();
}

// SHA256
uprobe:/system/lib64/libcrypto.so:SHA256
/comm == "com.target.app"/
{
    printf("[CRYPTO] SHA256 len=%d\n", arg1);
    @sha256_count = count();
}

END
{
    printf("\n=== 加密统计 ===\n");
    printf("加密初始化: %d 次, 处理: %d 字节\n", @encrypt_init, @encrypt_bytes);
    printf("解密初始化: %d 次, 处理: %d 字节\n", @decrypt_init, @decrypt_bytes);
    printf("HMAC: %d 次\n", @hmac_count);
    printf("SHA256: %d 次\n", @sha256_count);
}
```

### AES 密钥捕获

```bash
#!/usr/bin/env bpftrace
// 文件: aes_key_capture.bt
// 用途: 捕获 AES 密钥 (仅用于安全研究)

uprobe:/system/lib64/libcrypto.so:AES_set_encrypt_key
/comm == "com.target.app"/
{
    printf("[AES] Setting encrypt key, bits=%d\n", arg1);

    // 打印密钥的前几个字节 (仅示例)
    $key = (uint8 *)arg0;
    printf("  Key prefix: %02x %02x %02x %02x ...\n",
           $key[0], $key[1], $key[2], $key[3]);
}

uprobe:/system/lib64/libcrypto.so:AES_set_decrypt_key
/comm == "com.target.app"/
{
    printf("[AES] Setting decrypt key, bits=%d\n", arg1);
}
```

---

## 反调试检测

### 检测反调试行为

```bash
#!/usr/bin/env bpftrace
// 文件: anti_debug_detect.bt
// 用途: 检测应用的反调试行为

// ptrace 检测
tracepoint:syscalls:sys_enter_ptrace
{
    printf("[ANTI-DEBUG] ptrace by %s (PID:%d)\n", comm, pid);
    printf("  request: %d, pid: %d\n", args->request, args->pid);

    if (args->request == 0) {  // PTRACE_TRACEME
        printf("  !!! PTRACE_TRACEME detected !!!\n");
    }
}

// /proc/self/status 读取 (检测 TracerPid)
tracepoint:syscalls:sys_enter_openat
/strcontains(str(args->filename), "/proc/") &&
 strcontains(str(args->filename), "/status")/
{
    printf("[ANTI-DEBUG] %s reading %s\n", comm, str(args->filename));
}

// /proc/self/maps 读取 (检测 Frida)
tracepoint:syscalls:sys_enter_openat
/strcontains(str(args->filename), "/proc/") &&
 strcontains(str(args->filename), "/maps")/
{
    printf("[ANTI-DEBUG] %s reading %s\n", comm, str(args->filename));
}

// inotify 监控 (检测文件修改)
tracepoint:syscalls:sys_enter_inotify_add_watch
{
    printf("[ANTI-DEBUG] %s adding inotify watch: %s\n",
           comm, str(args->pathname));
}

// prctl 调用 (可能用于 PR_SET_DUMPABLE)
tracepoint:syscalls:sys_enter_prctl
{
    printf("[ANTI-DEBUG] prctl by %s option=%d\n", comm, args->option);
}
```

### Frida 检测监控

```bash
#!/usr/bin/env bpftrace
// 文件: frida_detect.bt
// 用途: 监控应用检测 Frida 的行为

// 检测 Frida 端口扫描
tracepoint:syscalls:sys_enter_connect
/comm == "com.target.app"/
{
    $sa = (struct sockaddr *)args->uservaddr;
    if ($sa->sa_family == 2) {
        $sin = (struct sockaddr_in *)$sa;
        $port = ($sin->sin_port >> 8) | (($sin->sin_port & 0xff) << 8);

        // Frida 默认端口
        if ($port == 27042 || $port == 27043) {
            printf("[FRIDA-DETECT] Connecting to Frida port %d\n", $port);
        }
    }
}

// 检测 Frida 相关文件访问
tracepoint:syscalls:sys_enter_openat
/comm == "com.target.app"/
{
    $f = str(args->filename);
    if (strcontains($f, "frida") ||
        strcontains($f, "gadget") ||
        strcontains($f, "agent")) {
        printf("[FRIDA-DETECT] Checking file: %s\n", $f);
    }
}

// 检测 /proc/self/maps 中的 Frida
kprobe:proc_pid_maps
{
    printf("[FRIDA-DETECT] %s reading /proc/maps\n", comm);
}
```

---

## 进程和线程

### 进程创建追踪

```bash
#!/usr/bin/env bpftrace
// 文件: process_trace.bt
// 用途: 追踪进程创建和执行

tracepoint:syscalls:sys_enter_clone
/comm == "com.target.app"/
{
    printf("[CLONE] %s creating child, flags=%x\n", comm, args->clone_flags);
}

tracepoint:syscalls:sys_enter_execve
{
    printf("[EXEC] %s -> %s\n", comm, str(args->filename));
}

tracepoint:sched:sched_process_fork
/comm == "com.target.app"/
{
    printf("[FORK] %s (PID:%d) forked child PID:%d\n",
           comm, args->parent_pid, args->child_pid);
}

tracepoint:sched:sched_process_exit
/comm == "com.target.app"/
{
    printf("[EXIT] %s (PID:%d)\n", comm, pid);
}
```

### 线程活动监控

```bash
#!/usr/bin/env bpftrace
// 文件: thread_trace.bt
// 用途: 追踪线程创建和调度

tracepoint:syscalls:sys_enter_clone
/comm == "com.target.app" && (args->clone_flags & 0x10000)/  // CLONE_THREAD
{
    printf("[THREAD] Creating new thread\n");
    @thread_create = count();
}

tracepoint:sched:sched_switch
/prev_comm == "com.target.app" || next_comm == "com.target.app"/
{
    printf("[SWITCH] %s -> %s\n", prev_comm, next_comm);
}

// 追踪互斥锁
uprobe:/apex/com.android.runtime/lib64/bionic/libc.so:pthread_mutex_lock
/comm == "com.target.app"/
{
    @mutex_lock[arg0] = nsecs;
}

uretprobe:/apex/com.android.runtime/lib64/bionic/libc.so:pthread_mutex_lock
/comm == "com.target.app" && @mutex_lock[arg0]/
{
    $wait = nsecs - @mutex_lock[arg0];
    @mutex_wait = hist($wait);
    delete(@mutex_lock[arg0]);
}

END
{
    printf("\n=== 线程统计 ===\n");
    printf("线程创建: %d\n", @thread_create);
    printf("互斥锁等待时间分布:\n");
    print(@mutex_wait);
}
```

---

## JNI 和 ART

### JNI 调用追踪

```bash
#!/usr/bin/env bpftrace
// 文件: jni_trace.bt
// 用途: 追踪 JNI 函数调用

// FindClass
uprobe:/apex/com.android.art/lib64/libart.so:*FindClass*
/comm == "com.target.app"/
{
    printf("[JNI] FindClass\n");
    @jni_findclass = count();
}

// GetMethodID
uprobe:/apex/com.android.art/lib64/libart.so:*GetMethodID*
/comm == "com.target.app"/
{
    printf("[JNI] GetMethodID\n");
    @jni_getmethod = count();
}

// CallObjectMethod
uprobe:/apex/com.android.art/lib64/libart.so:*CallObjectMethod*
/comm == "com.target.app"/
{
    printf("[JNI] CallObjectMethod\n");
    @jni_call = count();
}

// RegisterNatives
uprobe:/apex/com.android.art/lib64/libart.so:*RegisterNatives*
/comm == "com.target.app"/
{
    printf("[JNI] RegisterNatives\n");
    @jni_register = count();
}

END
{
    printf("\n=== JNI 统计 ===\n");
    printf("FindClass: %d\n", @jni_findclass);
    printf("GetMethodID: %d\n", @jni_getmethod);
    printf("CallObjectMethod: %d\n", @jni_call);
    printf("RegisterNatives: %d\n", @jni_register);
}
```

### ART 方法编译追踪

```bash
#!/usr/bin/env bpftrace
// 文件: art_compile.bt
// 用途: 追踪 ART JIT 编译

uprobe:/apex/com.android.art/lib64/libart.so:*JitCompile*
/comm == "com.target.app"/
{
    printf("[JIT] Method compiled\n");
    @jit_compile = count();
}

uprobe:/apex/com.android.art/lib64/libart.so:*CompileMethod*
/comm == "com.target.app"/
{
    @compile_method = count();
}

END
{
    printf("\n=== ART JIT 统计 ===\n");
    printf("JIT 编译: %d\n", @jit_compile);
    printf("方法编译: %d\n", @compile_method);
}
```

---

## 内存追踪

### 内存分配追踪

```bash
#!/usr/bin/env bpftrace
// 文件: memory_alloc.bt
// 用途: 追踪内存分配

uprobe:/apex/com.android.runtime/lib64/bionic/libc.so:malloc
/comm == "com.target.app"/
{
    @malloc_size = hist(arg0);
    @malloc_total = sum(arg0);
    @malloc_count = count();
}

uretprobe:/apex/com.android.runtime/lib64/bionic/libc.so:malloc
/comm == "com.target.app"/
{
    @malloc_ptrs[retval] = nsecs;
}

uprobe:/apex/com.android.runtime/lib64/bionic/libc.so:free
/comm == "com.target.app" && @malloc_ptrs[arg0]/
{
    $lifetime = nsecs - @malloc_ptrs[arg0];
    @mem_lifetime = hist($lifetime);
    delete(@malloc_ptrs[arg0]);
    @free_count = count();
}

uprobe:/apex/com.android.runtime/lib64/bionic/libc.so:realloc
/comm == "com.target.app"/
{
    printf("[REALLOC] ptr=%p new_size=%zu\n", arg0, arg1);
    @realloc_count = count();
}

END
{
    printf("\n=== 内存分配统计 ===\n");
    printf("malloc 次数: %d, 总量: %d 字节\n", @malloc_count, @malloc_total);
    printf("free 次数: %d\n", @free_count);
    printf("realloc 次数: %d\n", @realloc_count);
    printf("\nmalloc 大小分布:\n");
    print(@malloc_size);
    printf("\n内存生命周期分布 (ns):\n");
    print(@mem_lifetime);
}
```

### mmap 追踪

```bash
#!/usr/bin/env bpftrace
// 文件: mmap_trace.bt
// 用途: 追踪内存映射

tracepoint:syscalls:sys_enter_mmap
/comm == "com.target.app"/
{
    printf("[MMAP] addr=%p len=%zu prot=%x flags=%x fd=%d offset=%lu\n",
           args->addr, args->len, args->prot, args->flags,
           args->fd, args->off);

    @mmap_total = sum(args->len);
    @mmap_count = count();

    // 记录可执行映射
    if (args->prot & 4) {  // PROT_EXEC
        @exec_mmap = count();
        printf("  !!! EXECUTABLE MAPPING !!!\n");
    }
}

tracepoint:syscalls:sys_enter_munmap
/comm == "com.target.app"/
{
    printf("[MUNMAP] addr=%p len=%zu\n", args->addr, args->len);
    @munmap_count = count();
}

tracepoint:syscalls:sys_enter_mprotect
/comm == "com.target.app"/
{
    printf("[MPROTECT] addr=%p len=%zu prot=%x\n",
           args->start, args->len, args->prot);

    if (args->prot & 4) {  // PROT_EXEC
        printf("  !!! MAKING EXECUTABLE !!!\n");
    }
}

END
{
    printf("\n=== mmap 统计 ===\n");
    printf("mmap: %d 次, 总量: %d 字节\n", @mmap_count, @mmap_total);
    printf("munmap: %d 次\n", @munmap_count);
    printf("可执行映射: %d 次\n", @exec_mmap);
}
```

---

## 性能分析

### 函数耗时统计

```bash
#!/usr/bin/env bpftrace
// 文件: func_latency.bt
// 用途: 统计关键函数耗时
// 使用: 修改目标函数路径

uprobe:/data/app/com.target.app-*/lib/arm64/libnative.so:target_function
{
    @start[tid] = nsecs;
}

uretprobe:/data/app/com.target.app-*/lib/arm64/libnative.so:target_function
/@start[tid]/
{
    $latency = nsecs - @start[tid];
    @latency_ns = hist($latency);
    @total_time = sum($latency);
    @call_count = count();
    delete(@start[tid]);
}

END
{
    printf("\n=== 函数耗时统计 ===\n");
    printf("调用次数: %d\n", @call_count);
    printf("总耗时: %d ns\n", @total_time);
    printf("耗时分布:\n");
    print(@latency_ns);
}
```

### CPU 采样

```bash
#!/usr/bin/env bpftrace
// 文件: cpu_profile.bt
// 用途: CPU 热点采样

profile:hz:99
/comm == "com.target.app"/
{
    @cpu_samples[ustack] = count();
}

END
{
    printf("\n=== CPU 热点 (Top 10) ===\n");
    print(@cpu_samples, 10);
}
```

---

## 实用工具函数

### 进程过滤模板

```bash
#!/usr/bin/env bpftrace
// 文件: filter_template.bt
// 用途: 进程过滤模板

// 方法1: 按进程名过滤
/comm == "com.target.app"/

// 方法2: 按 PID 过滤
/pid == $1/  // bpftrace script.bt 12345

// 方法3: 按 UID 过滤
/uid == 10123/

// 方法4: 按 cgroup 过滤 (容器)
/cgroup == "docker/xxx"/

// 方法5: 排除特定进程
/comm != "logd" && comm != "servicemanager"/
```

### 输出格式化

```bash
#!/usr/bin/env bpftrace
// 文件: output_format.bt
// 用途: 输出格式化示例

BEGIN
{
    printf("%-20s %-10s %-10s %s\n",
           "TIME", "PID", "COMM", "ACTION");
    printf("%-20s %-10s %-10s %s\n",
           "----", "---", "----", "------");
}

tracepoint:syscalls:sys_enter_openat
/comm == "com.target.app"/
{
    $ts = nsecs / 1000000000;
    printf("%-20llu %-10d %-10s OPEN: %s\n",
           $ts, pid, comm, str(args->filename));
}
```

---

## 运行说明

### 基本用法

```bash
# 运行脚本
adb shell /data/local/tmp/bpftrace /path/to/script.bt

# 带参数运行
adb shell /data/local/tmp/bpftrace /path/to/script.bt 12345

# 单行命令
adb shell /data/local/tmp/bpftrace -e 'tracepoint:syscalls:sys_enter_* { @[probe] = count(); }'

# 输出到文件
adb shell /data/local/tmp/bpftrace /path/to/script.bt > output.txt 2>&1
```

### 权限设置

```bash
# 确保 root 权限
adb root

# 禁用 SELinux (临时)
adb shell setenforce 0

# 检查 bpf 文件系统
adb shell mount | grep bpf
```

### 常见问题

1. **"Failed to attach"**: 检查函数名是否正确，使用 `nm` 或 `readelf` 确认
2. **"Permission denied"**: 需要 root 权限和 SELinux 设置
3. **"不支持的内核版本"**: 需要 4.14+ 内核

---

## 参考资料

- [bpftrace Reference Guide](https://github.com/iovisor/bpftrace/blob/master/docs/reference_guide.md)
- [bpftrace One-Liners](https://github.com/iovisor/bpftrace/blob/master/docs/tutorial_one_liners.md)
- [eBPF 使用指南](../../02-Tools/Dynamic/ebpf_guide.md)
