---
title: "eBPF Android 逆向实战"
date: 2025-12-27
tags: ["eBPF", "Android", "逆向工程", "实战", "隐蔽追踪"]
weight: 8
type: posts
---

# eBPF Android 逆向实战

本文通过实战案例展示如何使用 eBPF 进行 Android 应用逆向分析。eBPF 的优势在于运行在内核层，极难被应用检测到。

---

## 实战环境准备

### 设备要求

```bash
# 1. 检查内核版本 (需要 >= 4.14)
adb shell uname -r
# 期望输出: 4.14.x 或更高

# 2. 检查 eBPF 支持
adb shell ls /sys/fs/bpf/
# 应该存在此目录

# 3. 检查必要的内核配置
adb shell zcat /proc/config.gz | grep -E "CONFIG_BPF|CONFIG_KPROBE"
```

### 工具安装

```bash
# 下载 bpftrace for Android
# 选项1: 使用预编译版本
wget https://github.com/aspect-build/bpftrace-android/releases/latest/bpftrace-arm64

# 选项2: 自行编译 (需要 NDK)

# 推送到设备
adb push bpftrace-arm64 /data/local/tmp/bpftrace
adb shell chmod +x /data/local/tmp/bpftrace

# 验证安装
adb shell /data/local/tmp/bpftrace --version
```

### SELinux 配置

```bash
# 获取 root 权限
adb root

# 临时禁用 SELinux (必需)
adb shell setenforce 0

# 验证
adb shell getenforce
# 输出: Permissive
```

---

## 实战案例 1: 隐蔽追踪加密通信

### 背景

目标应用使用自定义加密，需要在不被检测的情况下捕获明文数据。

### 步骤 1: 识别加密库

```bash
# 列出应用加载的共享库
adb shell cat /proc/$(pidof com.target.app)/maps | grep "\.so"

# 常见加密库位置
# /system/lib64/libcrypto.so      (OpenSSL)
# /system/lib64/libssl.so         (SSL/TLS)
# /data/app/xxx/lib/arm64/lib*.so (应用私有库)
```

### 步骤 2: 追踪 OpenSSL 加密

```bash
#!/usr/bin/env bpftrace
// 文件: ssl_intercept.bt

// 追踪 SSL_write - 捕获发送的明文
uprobe:/system/lib64/libssl.so:SSL_write
/comm == "com.target.app"/
{
    @ssl_write_buf[tid] = arg1;
    @ssl_write_len[tid] = arg2;
    printf("\n[SSL_write] len=%d\n", arg2);
}

uretprobe:/system/lib64/libssl.so:SSL_write
/comm == "com.target.app" && @ssl_write_buf[tid]/
{
    $buf = @ssl_write_buf[tid];
    $len = @ssl_write_len[tid];

    // 打印前64字节
    $print_len = $len < 64 ? $len : 64;
    printf("Data (first %d bytes):\n", $print_len);

    // 使用循环打印数据
    $i = 0;
    while ($i < $print_len && $i < 64) {
        $byte = *(uint8 *)($buf + $i);
        printf("%02x ", $byte);
        if (($i + 1) % 16 == 0) {
            printf("\n");
        }
        $i++;
    }
    printf("\n");

    delete(@ssl_write_buf[tid]);
    delete(@ssl_write_len[tid]);
}

// 追踪 SSL_read - 捕获接收的明文
uprobe:/system/lib64/libssl.so:SSL_read
/comm == "com.target.app"/
{
    @ssl_read_buf[tid] = arg1;
}

uretprobe:/system/lib64/libssl.so:SSL_read
/comm == "com.target.app" && retval > 0/
{
    $buf = @ssl_read_buf[tid];
    $len = retval;

    printf("\n[SSL_read] len=%d\n", $len);

    $print_len = $len < 64 ? $len : 64;
    printf("Data (first %d bytes):\n", $print_len);

    $i = 0;
    while ($i < $print_len && $i < 64) {
        $byte = *(uint8 *)($buf + $i);
        printf("%02x ", $byte);
        if (($i + 1) % 16 == 0) {
            printf("\n");
        }
        $i++;
    }
    printf("\n");

    delete(@ssl_read_buf[tid]);
}
```

### 步骤 3: 捕获加密密钥

```bash
#!/usr/bin/env bpftrace
// 文件: crypto_key_capture.bt

// AES 密钥设置
uprobe:/system/lib64/libcrypto.so:AES_set_encrypt_key
/comm == "com.target.app"/
{
    $key = (uint8 *)arg0;
    $bits = arg1;

    printf("\n[AES_set_encrypt_key] bits=%d\n", $bits);
    printf("Key: ");

    $len = $bits / 8;
    $i = 0;
    while ($i < $len) {
        printf("%02x", $key[$i]);
        $i++;
    }
    printf("\n");
}

// EVP 加密初始化 - 获取 IV
uprobe:/system/lib64/libcrypto.so:EVP_EncryptInit_ex
/comm == "com.target.app"/
{
    printf("\n[EVP_EncryptInit_ex]\n");
    printf("  ctx=%p cipher=%p key=%p iv=%p\n", arg0, arg1, arg3, arg4);

    if (arg4 != 0) {
        $iv = (uint8 *)arg4;
        printf("  IV: ");
        $i = 0;
        while ($i < 16) {
            printf("%02x", $iv[$i]);
            $i++;
        }
        printf("\n");
    }
}
```

---

## 实战案例 2: 绕过反调试检测

### 背景

目标应用有多重反调试保护，需要在不触发检测的情况下分析。

### 检测点分析

```bash
#!/usr/bin/env bpftrace
// 文件: anti_debug_analysis.bt
// 首先运行此脚本，观察应用的反调试行为

// 1. ptrace 检测
tracepoint:syscalls:sys_enter_ptrace
{
    printf("[PTRACE] %s (PID:%d) request=%d target_pid=%d\n",
           comm, pid, args->request, args->pid);

    @ptrace_requests[args->request] = count();
}

// 2. /proc 文件系统访问
tracepoint:syscalls:sys_enter_openat
/strcontains(str(args->filename), "/proc/")/
{
    $f = str(args->filename);

    if (strcontains($f, "status") ||
        strcontains($f, "stat") ||
        strcontains($f, "maps") ||
        strcontains($f, "cmdline")) {
        printf("[PROC] %s opening %s\n", comm, $f);
        @proc_access[$f] = count();
    }
}

// 3. 时间检测 (调试会导致执行变慢)
tracepoint:syscalls:sys_enter_clock_gettime
/comm == "com.target.app"/
{
    @clock_gettime = count();
}

tracepoint:syscalls:sys_enter_gettimeofday
/comm == "com.target.app"/
{
    @gettimeofday = count();
}

// 4. 信号处理
tracepoint:signal:signal_deliver
/comm == "com.target.app"/
{
    printf("[SIGNAL] %s received signal %d\n", comm, args->sig);
}

END
{
    printf("\n=== 反调试行为统计 ===\n");
    printf("\nptrace 请求:\n");
    print(@ptrace_requests);
    printf("\n/proc 访问:\n");
    print(@proc_access);
    printf("\n时间获取: clock_gettime=%d, gettimeofday=%d\n",
           @clock_gettime, @gettimeofday);
}
```

### 隐蔽监控方案

使用 eBPF 监控而非 Frida，避免被检测:

```bash
#!/usr/bin/env bpftrace
// 文件: stealth_monitor.bt
// eBPF 运行在内核空间，应用层无法检测

// 追踪所有关键行为，但不干预
tracepoint:syscalls:sys_enter_openat
/comm == "com.target.app"/
{
    @files[str(args->filename)] = count();
}

tracepoint:syscalls:sys_enter_connect
/comm == "com.target.app"/
{
    @connects = count();
}

tracepoint:syscalls:sys_enter_sendto
/comm == "com.target.app"/
{
    @send_bytes = sum(args->len);
}

tracepoint:syscalls:sys_enter_recvfrom
/comm == "com.target.app"/
{
    @recv_attempts = count();
}

// JNI 调用追踪
uprobe:/apex/com.android.art/lib64/libart.so:*RegisterNatives*
/comm == "com.target.app"/
{
    printf("[JNI] RegisterNatives called\n");
    @jni_register = count();
}

interval:s:10
{
    printf("\n--- 10秒统计 ---\n");
    printf("文件访问: ");
    print(@files);
    printf("网络连接: %d, 发送: %d 字节\n", @connects, @send_bytes);
    clear(@files);
    clear(@connects);
    clear(@send_bytes);
    clear(@recv_attempts);
}
```

---

## 实战案例 3: 分析应用启动流程

### 追踪启动过程

```bash
#!/usr/bin/env bpftrace
// 文件: app_startup.bt
// 用途: 分析应用从启动到完成初始化的全过程

BEGIN
{
    printf("等待应用启动...\n");
    printf("请执行: adb shell am start com.target.app/.MainActivity\n\n");
}

// Zygote fork 新进程
tracepoint:sched:sched_process_fork
/comm == "zygote64" || comm == "zygote"/
{
    printf("[%llu] FORK: %s -> child_pid=%d\n",
           nsecs, comm, args->child_pid);
    @app_pid = args->child_pid;
}

// 进程执行
tracepoint:sched:sched_process_exec
/@app_pid == pid/
{
    printf("[%llu] EXEC: %s\n", nsecs, comm);
}

// 库加载追踪
tracepoint:syscalls:sys_enter_openat
/pid == @app_pid && strcontains(str(args->filename), ".so")/
{
    printf("[%llu] LOAD: %s\n", nsecs, str(args->filename));
    @loaded_libs[str(args->filename)] = 1;
}

// DEX 文件访问
tracepoint:syscalls:sys_enter_openat
/pid == @app_pid &&
 (strcontains(str(args->filename), ".dex") ||
  strcontains(str(args->filename), ".apk") ||
  strcontains(str(args->filename), ".vdex") ||
  strcontains(str(args->filename), ".odex"))/
{
    printf("[%llu] DEX: %s\n", nsecs, str(args->filename));
}

// mmap 可执行区域 (代码加载)
tracepoint:syscalls:sys_enter_mmap
/pid == @app_pid && (args->prot & 4)/  // PROT_EXEC
{
    printf("[%llu] MMAP_EXEC: addr=%p len=%zu\n",
           nsecs, args->addr, args->len);
    @exec_maps = count();
}

// 网络连接 (首次通信)
tracepoint:syscalls:sys_enter_connect
/pid == @app_pid/
{
    printf("[%llu] FIRST_CONNECT\n", nsecs);
}

// 10 秒后输出统计
interval:s:10
{
    printf("\n=== 启动分析完成 ===\n");
    printf("加载的库:\n");
    print(@loaded_libs);
    printf("可执行映射数: %d\n", @exec_maps);
    exit();
}
```

### 追踪 Native 库初始化

```bash
#!/usr/bin/env bpftrace
// 文件: native_init.bt
// 追踪 .so 库的 init 函数

// dlopen 调用
uprobe:/apex/com.android.runtime/lib64/bionic/libdl.so:dlopen
/comm == "com.target.app"/
{
    printf("[DLOPEN] Loading: %s\n", str(arg0));
    @dlopen_start[str(arg0)] = nsecs;
}

uretprobe:/apex/com.android.runtime/lib64/bionic/libdl.so:dlopen
/comm == "com.target.app"/
{
    printf("[DLOPEN] Returned: %p\n", retval);
}

// 追踪 JNI_OnLoad
uprobe:/data/app/com.target.app-*/lib/arm64/*.so:JNI_OnLoad
/comm == "com.target.app"/
{
    printf("[JNI_OnLoad] %s\n", probe);
    @jni_onload = count();
}

// 追踪 .init_array 执行 (constructor 函数)
// 这需要知道具体函数地址，或使用通配符
```

---

## 实战案例 4: 协议逆向分析

### 追踪自定义协议

```bash
#!/usr/bin/env bpftrace
// 文件: protocol_analysis.bt
// 分析应用自定义协议

// Socket 创建
tracepoint:syscalls:sys_enter_socket
/comm == "com.target.app"/
{
    printf("[SOCKET] domain=%d type=%d protocol=%d\n",
           args->family, args->type, args->protocol);
}

// 数据发送
tracepoint:syscalls:sys_enter_sendto
/comm == "com.target.app"/
{
    $buf = (uint8 *)args->buff;
    $len = args->len;

    printf("\n[SEND] len=%d\n", $len);

    // 打印协议头 (假设前16字节是头部)
    printf("Header: ");
    $i = 0;
    while ($i < 16 && $i < $len) {
        printf("%02x ", $buf[$i]);
        $i++;
    }
    printf("\n");

    // 分析魔数
    $magic = ($buf[0] << 24) | ($buf[1] << 16) | ($buf[2] << 8) | $buf[3];
    printf("Magic: 0x%08x\n", $magic);

    @send_sizes = hist($len);
}

// 数据接收
tracepoint:syscalls:sys_exit_recvfrom
/comm == "com.target.app" && args->ret > 0/
{
    printf("\n[RECV] len=%d\n", args->ret);
    @recv_sizes = hist(args->ret);
}

END
{
    printf("\n=== 协议统计 ===\n");
    printf("发送包大小分布:\n");
    print(@send_sizes);
    printf("接收包大小分布:\n");
    print(@recv_sizes);
}
```

### 追踪 Protobuf 序列化

```bash
#!/usr/bin/env bpftrace
// 文件: protobuf_trace.bt
// 追踪 Protobuf 编解码

// Google Protobuf 库函数
uprobe:/data/app/com.target.app-*/lib/arm64/lib*.so:*SerializeToString*
/comm == "com.target.app"/
{
    printf("[PROTOBUF] SerializeToString\n");
    @serialize = count();
}

uprobe:/data/app/com.target.app-*/lib/arm64/lib*.so:*ParseFromString*
/comm == "com.target.app"/
{
    printf("[PROTOBUF] ParseFromString\n");
    @parse = count();
}

// 追踪更底层的编码函数
uprobe:/data/app/com.target.app-*/lib/arm64/lib*.so:*WriteVarint*
/comm == "com.target.app"/
{
    @varint_writes = count();
}
```

---

## 实战案例 5: Root 检测分析

### 监控 Root 检测行为

```bash
#!/usr/bin/env bpftrace
// 文件: root_detect.bt
// 分析应用的 Root 检测机制

// 检测 su 二进制文件
tracepoint:syscalls:sys_enter_openat
/comm == "com.target.app"/
{
    $f = str(args->filename);

    if (strcontains($f, "/su") ||
        strcontains($f, "supersu") ||
        strcontains($f, "superuser") ||
        strcontains($f, "magisk") ||
        strcontains($f, "busybox")) {
        printf("[ROOT-CHECK] Checking: %s\n", $f);
        @root_checks[$f] = count();
    }
}

// 检测 stat/access 调用
tracepoint:syscalls:sys_enter_faccessat
/comm == "com.target.app"/
{
    $f = str(args->filename);

    if (strcontains($f, "/su") ||
        strcontains($f, "/system/xbin/") ||
        strcontains($f, "/system/bin/")) {
        printf("[ROOT-CHECK] Access check: %s\n", $f);
    }
}

// 检测 which 命令
tracepoint:syscalls:sys_enter_execve
/strcontains(str(args->filename), "which")/
{
    printf("[ROOT-CHECK] Exec: %s\n", str(args->filename));
}

// 检测系统属性读取
uprobe:/system/lib64/libc.so:__system_property_get
/comm == "com.target.app"/
{
    $name = str(arg0);

    if (strcontains($name, "ro.build") ||
        strcontains($name, "ro.debuggable") ||
        strcontains($name, "ro.secure")) {
        printf("[ROOT-CHECK] Property: %s\n", $name);
        @prop_checks[$name] = count();
    }
}

END
{
    printf("\n=== Root 检测统计 ===\n");
    printf("文件检查:\n");
    print(@root_checks);
    printf("\n属性检查:\n");
    print(@prop_checks);
}
```

---

## 性能分析工具

### 热点函数分析

```bash
#!/usr/bin/env bpftrace
// 文件: hotspot.bt
// CPU 热点分析

profile:hz:99
/comm == "com.target.app"/
{
    @user_stacks[ustack(10)] = count();
    @kernel_stacks[kstack(10)] = count();
}

END
{
    printf("\n=== 用户态热点 (Top 5) ===\n");
    print(@user_stacks, 5);
    printf("\n=== 内核态热点 (Top 5) ===\n");
    print(@kernel_stacks, 5);
}
```

### 锁竞争分析

```bash
#!/usr/bin/env bpftrace
// 文件: lock_contention.bt

uprobe:/apex/com.android.runtime/lib64/bionic/libc.so:pthread_mutex_lock
/comm == "com.target.app"/
{
    @lock_start[tid, arg0] = nsecs;
}

uretprobe:/apex/com.android.runtime/lib64/bionic/libc.so:pthread_mutex_lock
/comm == "com.target.app" && @lock_start[tid, arg0]/
{
    $wait = nsecs - @lock_start[tid, arg0];
    @lock_wait = hist($wait);

    if ($wait > 1000000) {  // > 1ms
        printf("[LOCK] tid=%d waited %d ns for mutex %p\n",
               tid, $wait, arg0);
    }

    delete(@lock_start[tid, arg0]);
}

END
{
    printf("\n=== 锁等待时间分布 (ns) ===\n");
    print(@lock_wait);
}
```

---

## 与 Frida 配合使用

### 场景: eBPF 监控 + Frida 修改

```bash
# 终端1: eBPF 监控 (不被检测)
adb shell /data/local/tmp/bpftrace -e '
tracepoint:syscalls:sys_enter_openat
/comm == "com.target.app"/
{
    printf("OPEN: %s\n", str(args->filename));
}'

# 终端2: 等待检测通过后，使用 Frida 注入
# 可以利用 eBPF 的信息决定 Hook 点
frida -U -f com.target.app -l script.js
```

### 使用 eBPF 辅助 Frida 分析

```javascript
// Frida 脚本: 基于 eBPF 发现的地址进行 Hook
// eBPF 可以发现动态加载的库地址

// 假设 eBPF 发现加密函数在 0x12345678
var encrypt_addr = ptr("0x12345678");

Interceptor.attach(encrypt_addr, {
    onEnter: function(args) {
        console.log("Encrypt called");
    }
});
```

---

## 常见问题解决

### Q: bpftrace 找不到符号

```bash
# 检查符号表
adb shell readelf -s /system/lib64/libcrypto.so | grep EVP

# 使用地址而非符号名
uprobe:/system/lib64/libcrypto.so:0x12345
```

### Q: 追踪导致应用崩溃

```bash
# 减少追踪频率
interval:ms:100  # 而不是每次调用

# 避免追踪高频函数
# 使用 profile 采样而非 uprobe
```

### Q: 内存限制

```bash
# 增加 map 大小
sudo sysctl kernel.perf_event_max_stack=127
sudo sysctl kernel.perf_event_max_contexts_per_stack=8
```

---

## 总结

eBPF 在 Android 逆向中的核心优势:

1. **隐蔽性**: 内核态运行，无法被应用检测
2. **全面性**: 可追踪系统调用、网络、文件、内存等所有层面
3. **高性能**: JIT 编译，开销极低
4. **安全性**: 不影响目标应用稳定性

建议工作流:
1. 先用 eBPF 隐蔽监控，了解应用行为
2. 分析反调试机制
3. 确定关键函数和地址
4. 必要时配合 Frida 进行深入分析

---

## 参考资料

- [eBPF 使用指南](../../02-Tools/Dynamic/ebpf_guide.md)
- [eBPF 内部原理](../../02-Tools/Dynamic/ebpf_internals.md)
- [eBPF 脚本集](../Scripts/ebpf_scripts.md)
