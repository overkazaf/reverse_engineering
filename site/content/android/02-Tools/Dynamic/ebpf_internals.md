---
title: "eBPF 内部原理"
date: 2025-12-27
tags: ["eBPF", "内核", "虚拟机", "JIT", "验证器"]
weight: 8
type: posts
---

# eBPF 内部原理

本文深入剖析 eBPF 的内部工作机制，帮助你理解这项技术的底层原理，从而更好地应用于 Android 逆向工程。

---

## 架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                       用户空间                              │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐    │
│  │  bpftrace   │  │  BCC/Python  │  │   libbpf/C      │    │
│  └──────┬──────┘  └──────┬───────┘  └────────┬────────┘    │
│         │                │                    │             │
│         └────────────────┼────────────────────┘             │
│                          │ bpf() 系统调用                    │
├──────────────────────────┼──────────────────────────────────┤
│                       内核空间                              │
│                          ▼                                  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                    BPF 验证器                          │  │
│  │    - 安全检查        - 边界验证       - 死循环检测     │  │
│  └───────────────────────────────────────────────────────┘  │
│                          │                                  │
│                          ▼                                  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                    JIT 编译器                          │  │
│  │         将 BPF 字节码编译为原生机器码                   │  │
│  └───────────────────────────────────────────────────────┘  │
│                          │                                  │
│         ┌────────────────┼────────────────┐                 │
│         ▼                ▼                ▼                 │
│    ┌─────────┐     ┌─────────┐     ┌─────────────┐         │
│    │ kprobes │     │tracepoint│    │ socket/XDP  │         │
│    └─────────┘     └─────────┘     └─────────────┘         │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                    BPF Maps                            │  │
│  │    内核与用户空间共享的数据结构                          │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## BPF 虚拟机

### 寄存器模型

eBPF 使用 11 个 64 位寄存器:

| 寄存器 | 用途 |
|--------|------|
| R0 | 返回值，辅助函数返回值 |
| R1-R5 | 函数参数 |
| R6-R9 | 被调用者保存寄存器 |
| R10 | 只读栈帧指针 |

```c
// 寄存器使用示例
// R1 = ctx (上下文指针)
// R0 = 返回值

int bpf_prog(struct pt_regs *ctx) {
    // R1 = ctx
    u64 pid = bpf_get_current_pid_tgid();  // 结果在 R0
    return 0;  // R0 = 0
}
```

### 指令集

eBPF 指令格式 (64 位):

```
┌───────┬───────┬───────┬───────────────┬───────────────────┐
│ 8 bit │ 4 bit │ 4 bit │    16 bit     │      32 bit       │
│  op   │  dst  │  src  │    offset     │      imm          │
└───────┴───────┴───────┴───────────────┴───────────────────┘
```

**指令类别:**

```c
// 算术指令
BPF_ADD | BPF_X | BPF_ALU64   // dst += src (64位)
BPF_SUB | BPF_K | BPF_ALU     // dst -= imm (32位)

// 跳转指令
BPF_JEQ | BPF_K | BPF_JMP     // if dst == imm goto pc+off
BPF_JGT | BPF_X | BPF_JMP     // if dst > src goto pc+off

// 内存访问
BPF_LDX | BPF_MEM | BPF_DW    // dst = *(u64 *)(src + off)
BPF_STX | BPF_MEM | BPF_W     // *(u32 *)(dst + off) = src

// 函数调用
BPF_CALL                       // 调用辅助函数
BPF_EXIT                       // 退出程序
```

### 示例程序字节码

```c
// 简单的 eBPF 程序
int hello(void *ctx) {
    char msg[] = "Hello";
    bpf_trace_printk(msg, sizeof(msg));
    return 0;
}

// 编译后的字节码 (简化)
/*
0: r1 = 0x6f6c6c6548        // "Hello" 低位
1: *(u64 *)(r10 - 8) = r1   // 存储到栈
2: r1 = r10 - 8             // msg 地址
3: r2 = 6                   // sizeof(msg)
4: call bpf_trace_printk    // 调用辅助函数
5: r0 = 0                   // 返回值
6: exit                     // 退出
*/
```

---

## 验证器 (Verifier)

验证器是 eBPF 安全性的核心，确保程序不会破坏内核。

### 验证流程

```
┌─────────────────────────────────────────────────────────────┐
│                      BPF 验证器流程                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. CFG 检查 (Control Flow Graph)                           │
│     ├─ 检测不可达代码                                        │
│     ├─ 验证所有路径都有 exit                                 │
│     └─ 检测循环 (默认禁止无界循环)                           │
│                                                             │
│  2. 模拟执行                                                 │
│     ├─ 追踪每个寄存器状态                                    │
│     ├─ 验证内存访问边界                                      │
│     └─ 检查指针类型安全                                      │
│                                                             │
│  3. 辅助函数调用验证                                         │
│     ├─ 检查参数类型                                          │
│     ├─ 验证调用权限                                          │
│     └─ 追踪返回值类型                                        │
│                                                             │
│  4. Map 访问验证                                             │
│     ├─ 检查 Map 类型兼容性                                   │
│     ├─ 验证键/值大小                                         │
│     └─ 检查并发安全性                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 寄存器状态追踪

```c
// 验证器追踪的寄存器状态
enum bpf_reg_type {
    NOT_INIT,           // 未初始化
    SCALAR_VALUE,       // 标量值
    PTR_TO_CTX,         // 上下文指针
    PTR_TO_MAP_VALUE,   // Map 值指针
    PTR_TO_STACK,       // 栈指针
    PTR_TO_PACKET,      // 网络包指针
    // ...
};

// 验证示例
int bpf_prog(struct __sk_buff *skb) {
    // R1 = PTR_TO_CTX (skb)

    u8 *data = (void *)(long)skb->data;
    // data 类型: PTR_TO_PACKET

    u8 *end = (void *)(long)skb->data_end;
    // end 类型: PTR_TO_PACKET_END

    // 必须进行边界检查
    if (data + 14 > end) {
        return 0;  // 验证器要求的边界检查
    }

    // 现在可以安全访问 data[0..13]
    return data[0];
}
```

### 常见验证错误

```bash
# 错误1: 无界循环
"back-edge from insn X to Y"

# 错误2: 越界访问
"invalid access to map value, off=X size=Y"

# 错误3: 未初始化寄存器
"R3 !read_ok"

# 错误4: 指针泄露
"cannot write pointer to map value"

# 错误5: 无效的辅助函数调用
"unknown func bpf_xxx"
```

---

## JIT 编译器

### 编译流程

```
BPF 字节码 → JIT 编译器 → 原生机器码
     │              │            │
     │              │            ├─ x86_64
     │              │            ├─ ARM64
     │              │            ├─ ARM32
     │              │            └─ ...
```

### ARM64 JIT 示例

```c
// BPF 指令
BPF_ALU64 | BPF_ADD | BPF_X  // R0 += R1

// 编译为 ARM64
ADD X0, X0, X1

// BPF 指令
BPF_JEQ | BPF_K | BPF_JMP   // if R0 == 42 goto +5

// 编译为 ARM64
CMP X0, #42
B.EQ .+5*4
```

### JIT 优化

```c
// 常量折叠
r1 = 10
r2 = 20
r3 = r1 + r2  // 编译时计算为 30

// 死代码消除
if (false) {
    // 这段代码会被移除
}

// 寄存器分配
// BPF 寄存器直接映射到物理寄存器
// R0-R9 → X0-X9 (ARM64)
```

---

## BPF Maps

### Map 类型详解

```c
// 1. 哈希表 - 任意键值对
BPF_MAP_TYPE_HASH
// 用途: 存储 PID 到计数的映射
struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 10240);
    __type(key, u32);      // PID
    __type(value, u64);    // 计数
} pid_counts SEC(".maps");

// 2. 数组 - 快速索引访问
BPF_MAP_TYPE_ARRAY
// 用途: 预分配的固定大小数组
struct {
    __uint(type, BPF_MAP_TYPE_ARRAY);
    __uint(max_entries, 256);
    __type(key, u32);
    __type(value, struct stats);
} syscall_stats SEC(".maps");

// 3. 性能缓冲区 - 高效事件传输
BPF_MAP_TYPE_PERF_EVENT_ARRAY
// 用途: 向用户空间发送事件
struct {
    __uint(type, BPF_MAP_TYPE_PERF_EVENT_ARRAY);
    __uint(key_size, sizeof(int));
    __uint(value_size, sizeof(int));
} events SEC(".maps");

// 4. 栈追踪 - 存储调用栈
BPF_MAP_TYPE_STACK_TRACE
// 用途: 捕获内核/用户态调用栈

// 5. LRU 哈希表 - 自动淘汰
BPF_MAP_TYPE_LRU_HASH
// 用途: 有限空间下的缓存
```

### Map 操作

```c
// 内核态操作
void *bpf_map_lookup_elem(map, key);
long bpf_map_update_elem(map, key, value, flags);
long bpf_map_delete_elem(map, key);

// 用户态操作 (通过 bpf 系统调用)
int bpf_map_lookup_elem(int fd, const void *key, void *value);
int bpf_map_update_elem(int fd, const void *key, const void *value, __u64 flags);
int bpf_map_delete_elem(int fd, const void *key);
```

### Map 并发安全

```c
// 原子操作
__sync_fetch_and_add(&value, 1);

// Per-CPU Map - 无锁并发
BPF_MAP_TYPE_PERCPU_HASH
BPF_MAP_TYPE_PERCPU_ARRAY

// 自旋锁 (较新内核)
struct bpf_spin_lock lock;
bpf_spin_lock(&lock);
// 临界区
bpf_spin_unlock(&lock);
```

---

## 程序类型深入

### Kprobe/Kretprobe

```c
// 在内核函数入口处触发
SEC("kprobe/do_sys_openat2")
int kprobe_openat(struct pt_regs *ctx) {
    // ctx 包含寄存器状态
    // ARM64: x0-x7 = 参数
    char *filename = (char *)PT_REGS_PARM2(ctx);
    return 0;
}

// 在内核函数返回时触发
SEC("kretprobe/do_sys_openat2")
int kretprobe_openat(struct pt_regs *ctx) {
    // PT_REGS_RC(ctx) = 返回值
    int fd = PT_REGS_RC(ctx);
    return 0;
}
```

### Uprobe/Uretprobe

```c
// 在用户态函数入口处触发
SEC("uprobe/libc.so.6:malloc")
int uprobe_malloc(struct pt_regs *ctx) {
    size_t size = PT_REGS_PARM1(ctx);
    bpf_printk("malloc(%zu)\n", size);
    return 0;
}

// 在用户态函数返回时触发
SEC("uretprobe/libc.so.6:malloc")
int uretprobe_malloc(struct pt_regs *ctx) {
    void *ptr = (void *)PT_REGS_RC(ctx);
    bpf_printk("malloc returned %p\n", ptr);
    return 0;
}
```

### Tracepoint

```c
// 内核静态追踪点 - 稳定的 ABI
SEC("tracepoint/syscalls/sys_enter_openat")
int trace_openat(struct trace_event_raw_sys_enter *ctx) {
    // 参数通过 args 访问
    char *filename = (char *)ctx->args[1];
    int flags = ctx->args[2];
    return 0;
}
```

### Socket/XDP

```c
// Socket 过滤器
SEC("socket")
int socket_filter(struct __sk_buff *skb) {
    // 返回 0 = 丢弃, 返回正数 = 接受
    return skb->len;
}

// XDP - 高性能网络处理
SEC("xdp")
int xdp_filter(struct xdp_md *ctx) {
    void *data = (void *)(long)ctx->data;
    void *data_end = (void *)(long)ctx->data_end;

    struct ethhdr *eth = data;
    if ((void *)(eth + 1) > data_end)
        return XDP_DROP;

    return XDP_PASS;
}
```

---

## 辅助函数

### 内存访问

```c
// 安全读取内核内存
long bpf_probe_read(void *dst, u32 size, const void *src);

// 安全读取用户内存
long bpf_probe_read_user(void *dst, u32 size, const void *src);

// 安全读取字符串
long bpf_probe_read_str(void *dst, u32 size, const void *src);
long bpf_probe_read_user_str(void *dst, u32 size, const void *src);
```

### 进程信息

```c
// 获取 PID/TID
u64 bpf_get_current_pid_tgid(void);
// 返回: (PID << 32) | TID

// 获取 UID/GID
u64 bpf_get_current_uid_gid(void);
// 返回: (GID << 32) | UID

// 获取进程名
long bpf_get_current_comm(void *buf, u32 size);

// 获取 cgroup ID
u64 bpf_get_current_cgroup_id(void);
```

### 时间和随机

```c
// 获取纳秒级时间戳
u64 bpf_ktime_get_ns(void);

// 获取启动时间
u64 bpf_ktime_get_boot_ns(void);

// 获取随机数
u32 bpf_get_prandom_u32(void);
```

### Map 操作

```c
void *bpf_map_lookup_elem(struct bpf_map *map, const void *key);
long bpf_map_update_elem(struct bpf_map *map, const void *key,
                         const void *value, u64 flags);
long bpf_map_delete_elem(struct bpf_map *map, const void *key);
```

### 输出和调试

```c
// 性能事件输出
long bpf_perf_event_output(void *ctx, struct bpf_map *map,
                           u64 flags, void *data, u64 size);

// 环形缓冲区输出 (推荐)
void *bpf_ringbuf_reserve(struct bpf_map *ringbuf, u64 size, u64 flags);
void bpf_ringbuf_submit(void *data, u64 flags);
void bpf_ringbuf_discard(void *data, u64 flags);

// 调试输出
long bpf_trace_printk(const char *fmt, u32 fmt_size, ...);
// 输出到 /sys/kernel/debug/tracing/trace_pipe
```

---

## CO-RE (Compile Once – Run Everywhere)

### BTF (BPF Type Format)

BTF 提供了内核类型信息，使 eBPF 程序可以跨内核版本运行。

```c
// 传统方式 - 硬编码偏移
u32 pid = *(u32 *)(task + 0x4c0);  // 不同内核偏移不同

// CO-RE 方式 - 使用 BTF
u32 pid;
bpf_core_read(&pid, sizeof(pid), &task->pid);
// 或使用 BPF_CORE_READ 宏
u32 pid = BPF_CORE_READ(task, pid);
```

### 字段重定位

```c
// 自动处理结构体字段偏移变化
struct task_struct___old {
    int pid;
    // ... 旧版本布局
};

struct task_struct___new {
    int __pad;
    int pid;
    // ... 新版本布局
};

// CO-RE 会在加载时自动重定位
int pid = BPF_CORE_READ(task, pid);
```

### 内核版本检测

```c
// 检查字段是否存在
if (bpf_core_field_exists(task->loginuid)) {
    // 使用 loginuid
}

// 检查枚举值
if (bpf_core_enum_value_exists(enum bpf_func_id, BPF_FUNC_xyz)) {
    // 使用新功能
}
```

---

## Android 特定考虑

### Android eBPF 限制

1. **SELinux 限制**
```bash
# 检查 SELinux 域
adb shell cat /proc/self/attr/current

# 可能需要的 SELinux 策略
allow domain bpf:bpf { map_create prog_load };
```

2. **内核配置差异**
```bash
# 检查可用的 eBPF 特性
adb shell cat /proc/sys/kernel/unprivileged_bpf_disabled
```

3. **库路径差异**
```bash
# Android 系统库位置
/system/lib64/libc.so
/apex/com.android.runtime/lib64/bionic/libc.so
/system/lib64/libcrypto.so
```

### Android 专用追踪

```c
// 追踪 Binder 调用
SEC("tracepoint/binder/binder_transaction")
int trace_binder(struct trace_event_raw_binder_transaction *ctx) {
    // 追踪进程间通信
    return 0;
}

// 追踪 ART 虚拟机
SEC("uprobe/libart.so:_ZN3art...")
int trace_art(struct pt_regs *ctx) {
    // 追踪 Java 方法调用
    return 0;
}
```

---

## 性能优化

### 减少 Map 查找

```c
// 不好 - 多次查找
void *val1 = bpf_map_lookup_elem(&map, &key);
void *val2 = bpf_map_lookup_elem(&map, &key);

// 好 - 缓存结果
void *val = bpf_map_lookup_elem(&map, &key);
if (val) {
    // 使用 val 两次
}
```

### 使用 Per-CPU Map

```c
// 避免锁竞争
struct {
    __uint(type, BPF_MAP_TYPE_PERCPU_ARRAY);
    __uint(max_entries, 1);
    __type(key, u32);
    __type(value, struct stats);
} stats SEC(".maps");
```

### 减少栈使用

```c
// eBPF 栈大小限制为 512 字节

// 不好 - 大数组在栈上
char buf[256];

// 好 - 使用 Per-CPU 数组
struct {
    __uint(type, BPF_MAP_TYPE_PERCPU_ARRAY);
    __uint(max_entries, 1);
    __type(key, u32);
    __type(value, char[256]);
} heap SEC(".maps");
```

---

## 调试技巧

### 查看验证器日志

```bash
# 增加日志级别
echo 2 > /proc/sys/kernel/bpf_stats_enabled

# 查看加载失败的详细信息
bpftool prog load xxx.o /sys/fs/bpf/xxx verbose
```

### 追踪 BPF 事件

```bash
# 使用 bpftrace 追踪 bpf 系统调用
bpftrace -e 'tracepoint:syscalls:sys_enter_bpf {
    printf("bpf cmd=%d\n", args->cmd);
}'
```

### 检查已加载的程序

```bash
# 列出所有 BPF 程序
bpftool prog list

# 查看程序详情
bpftool prog show id 123

# 查看字节码
bpftool prog dump xlated id 123

# 查看 JIT 编译后的代码
bpftool prog dump jited id 123
```

---

## 参考资料

- [Linux Kernel BPF Documentation](https://www.kernel.org/doc/html/latest/bpf/)
- [BPF and XDP Reference Guide](https://docs.cilium.io/en/stable/bpf/)
- [eBPF Instruction Set](https://www.kernel.org/doc/html/latest/bpf/instruction-set.html)
- [BTF Type Information](https://www.kernel.org/doc/html/latest/bpf/btf.html)
