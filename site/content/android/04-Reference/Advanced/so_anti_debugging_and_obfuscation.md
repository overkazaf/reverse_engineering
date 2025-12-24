---
title: "SO 文件反调试与字符串混淆技术"
weight: 10
---

# SO 文件反调试与字符串混淆技术

在 Android Native 层安全对抗中，SO 文件是实现高强度保护的重要载体。通过 init_array 机制、字符串混淆和反调试技术的组合使用，可以显著提高逆向分析的难度。本文将深入分析这些技术的实现原理及对应的分析绕过方法。

## 目录

1. [init_array 调用流程原理](#init_array-调用流程原理)
2. [字符串混淆技术](#字符串混淆技术)
3. [反调试技术实现](#反调试技术实现)
4. [分析与绕过方法](#分析与绕过方法)
5. [高级防护策略](#高级防护策略)

---

## 1. init_array 调用流程原理

### 1.1 ELF 加载与 init_array 执行时机

```cpp
// linker 中 call_constructors 的简化实现
void soinfo::call_constructors() {
    // 1. 首先调用 DT_INIT 初始化函数
    if (init_func_ != nullptr) {
        init_func_();
    }

    // 2. 然后遍历 .init_array 段的函数指针
    if (init_array_ != nullptr) {
        for (size_t i = 0; i < init_array_count_; ++i) {
            // 调用每个构造函数
            ((void (*)())init_array_[i])();
        }
    }
}
```

### 1.2 完整调用链路

```
System.loadLibrary("target")
         ↓
nativeLoad() [art/runtime/native/java_lang_Runtime.cc]
         ↓
android_dlopen_ext() [bionic/libdl/libdl.cpp]
         ↓
do_dlopen() [bionic/linker/linker.cpp]
         ↓
find_library() → load_library() → link_image()
         ↓
call_constructors() → init_array 函数执行
```

### 1.3 查看 init_array 信息

```bash
# 使用 readelf 查看动态段
readelf -d target.so | grep INIT

# 使用 objdump 分析
objdump -s -j .init_array target.so
```

### 1.4 init_array 结构

```cpp
// init_array 结构信息
typedef struct {
    Elf64_Addr *init_array;    // 函数指针数组
    size_t init_array_count;   // 数组大小
} init_array_info;

// 反调试函数声明
__attribute__((constructor))
void anti_debug_init() {
    // 反调试逻辑
}

// 编译后会在 .init_array 段生成函数指针
```

---

## 2. 字符串混淆技术

### 2.1 XOR 加密字符串

```cpp
// 字符串加密宏定义
#define ENCRYPT_STRING(str) encrypt_string_xor(str, sizeof(str)-1, 0xAA)

constexpr char* encrypt_string_xor(const char* str, size_t len, char key) {
    static char encrypted[256];
    for (size_t i = 0; i < len; i++) {
        encrypted[i] = str[i] ^ key;
    }
    encrypted[len] = '\0';
    return encrypted;
}

// 使用示例
void check_frida() {
    // 原始字符串: "/data/local/tmp/frida-server"
    const char* encrypted = "\xc4\xae\xa8\xa8\xe4\xe6\xe8\xe0\xe4\xe6\xe4";

    char decrypted[256];
    decrypt_string(encrypted, decrypted, strlen(encrypted), 0xAA);

    if (access(decrypted, F_OK) == 0) {
        exit(1);
    }
}
```

### 2.2 AES 加密字符串

```cpp
class StringObfuscator {
private:
    static constexpr uint8_t AES_KEY[16] = {
        0x2b, 0x7e, 0x15, 0x16, 0x28, 0xae, 0xd2, 0xa6,
        0xab, 0xf7, 0x15, 0x88, 0x09, 0xcf, 0x4f, 0x3c
    };

    static void aes_decrypt(const uint8_t* encrypted, uint8_t* decrypted, size_t len) {
        AES_KEY aes_key;
        AES_set_decrypt_key(AES_KEY, 128, &aes_key);

        for (size_t i = 0; i < len; i += 16) {
            AES_decrypt(encrypted + i, decrypted + i, &aes_key);
        }
    }

public:
    static std::string decrypt_string(const uint8_t* encrypted_data, size_t len) {
        std::vector<uint8_t> decrypted(len);
        aes_decrypt(encrypted_data, decrypted.data(), len);

        // 移除 padding
        size_t actual_len = len;
        while (actual_len > 0 && decrypted[actual_len - 1] == 0) {
            actual_len--;
        }

        return std::string(reinterpret_cast<char*>(decrypted.data()), actual_len);
    }
};

// 使用加密字符串
void advanced_anti_debug() {
    // 加密的 "/proc/self/status" 字符串
    const uint8_t encrypted_proc_status[] = {
        0x8a, 0x2d, 0x5e, 0x1f, 0x9b, 0x7c, 0x85, 0xa3,
        0x4e, 0x92, 0x67, 0xc1, 0x55, 0x98, 0x33, 0x2a
    };

    std::string proc_status = StringObfuscator::decrypt_string(
        encrypted_proc_status, sizeof(encrypted_proc_status)
    );

    check_debugger_via_status(proc_status.c_str());
}
```

### 2.3 栈上动态构造字符串

```cpp
void construct_string_on_stack() {
    char target_path[64];

    // 分段构造字符串
    strcpy(target_path, "/data/");
    strcat(target_path, "local/");
    strcat(target_path, "tmp/");
    strcat(target_path, "frida-");
    strcat(target_path, "server");

    if (access(target_path, F_OK) == 0) {
        exit(1);
    }

    // 清理栈上敏感字符串
    memset(target_path, 0, sizeof(target_path));
}
```

### 2.4 动态字符串构建器

```cpp
class DynamicStringBuilder {
private:
    std::vector<std::string> fragments;

public:
    void add_fragment(const char* encrypted, size_t len, uint8_t key) {
        std::string decrypted;
        for (size_t i = 0; i < len; i++) {
            decrypted += static_cast<char>(encrypted[i] ^ key);
        }
        fragments.push_back(decrypted);
    }

    std::string build() {
        std::string result;
        for (const auto& fragment : fragments) {
            result += fragment;
        }

        // 立即清理 fragments
        fragments.clear();

        return result;
    }
};

void dynamic_string_detection() {
    DynamicStringBuilder builder;

    // 分段加密字符串片段
    const char frag1[] = {0x8f, 0x9e, 0x9a, 0x9a, 0x8f}; // "/data"
    const char frag2[] = {0x8f, 0x93, 0x91, 0x9d, 0x9e, 0x93}; // "/local"
    const char frag3[] = {0x8f, 0x9a, 0x94, 0x92}; // "/tmp"

    builder.add_fragment(frag1, 5, 0xEE);
    builder.add_fragment(frag2, 6, 0xEE);
    builder.add_fragment(frag3, 4, 0xEE);

    std::string path = builder.build();

    // 使用构造的路径进行检测
    perform_detection(path.c_str());
}
```

---

## 3. 反调试技术实现

### 3.1 init_array 中的反调试

```cpp
// 在 .init_array 中执行反调试函数
__attribute__((constructor(101))) // 指定优先级
void init_anti_debug_level1() {
    // 1. ptrace 自身保护
    if (ptrace(PTRACE_TRACEME, 0, 1, 0) == -1) {
        _exit(1);
    }

    // 2. 检测调试器进程
    check_debugger_processes();

    // 3. 检测 Frida 文件
    check_frida_artifacts();
}

__attribute__((constructor(102)))
void init_anti_debug_level2() {
    // 4. 检测内存映射
    check_suspicious_mappings();

    // 5. 检测 hook 痕迹
    check_hook_signatures();

    // 6. 时间检测
    timing_attack_detection();
}

void check_debugger_processes() {
    const char* debugger_names[] = {
        "gdb", "lldb", "strace", "ida", "x64dbg"
    };

    for (const char* name : debugger_names) {
        if (process_exists(name)) {
            execute_anti_debug_response();
        }
    }
}

void check_frida_artifacts() {
    const char* frida_indicators[] = {
        "/data/local/tmp/frida-server",
        "/data/local/tmp/frida-agent-64.so",
        "/system/lib64/libfrida-gum.so"
    };

    for (const char* indicator : frida_indicators) {
        if (file_exists(indicator)) {
            execute_anti_debug_response();
        }
    }
}
```

### 3.2 内存映射检测

```cpp
__attribute__((constructor(103)))
void init_memory_protection() {
    // 检测代码段完整性
    verify_code_integrity();

    // 检测异常向量表
    check_exception_handlers();

    // 设置内存保护
    setup_memory_protection();
}

void check_suspicious_mappings() {
    FILE* maps = fopen("/proc/self/maps", "r");
    char line[512];

    while (fgets(line, sizeof(line), maps)) {
        // 检测可疑库映射
        if (strstr(line, "frida") ||
            strstr(line, "gum-js-loop") ||
            strstr(line, "xposed")) {
            fclose(maps);
            execute_anti_debug_response();
        }

        // 检测可疑权限组合
        if (strstr(line, "rwxp")) { // 可读写执行页面
            analyze_rwx_mapping(line);
        }
    }

    fclose(maps);
}

void verify_code_integrity() {
    // 计算代码段哈希值
    Dl_info info;
    dladdr((void*)verify_code_integrity, &info);

    const char* base = (const char*)info.dli_fbase;
    size_t text_size = get_text_section_size(base);

    uint32_t current_hash = calculate_crc32(base, text_size);
    uint32_t expected_hash = get_expected_hash();

    if (current_hash != expected_hash) {
        // 代码被修改，执行对抗措施
        code_tampering_detected();
    }
}
```

### 3.3 时间检测

```cpp
void init_timing_checks() {
    // 启动定时器检测
    start_timing_monitor();

    // 检测单步执行
    detect_single_stepping();
}

void detect_single_stepping() {
    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC, &start);

    // 执行一些简单操作
    volatile int dummy = 0;
    for (int i = 0; i < 1000; i++) {
        dummy += i;
    }

    clock_gettime(CLOCK_MONOTONIC, &end);

    long duration = (end.tv_sec - start.tv_sec) * 1000000000 +
                   (end.tv_nsec - start.tv_nsec);

    // 如果执行时间异常，可能在单步调试
    if (duration > NORMAL_EXECUTION_TIME * 10) {
        single_step_detected();
    }
}

void start_timing_monitor() {
    std::thread([]() {
        while (true) {
            std::this_thread::sleep_for(std::chrono::seconds(5));

            // 定期检测系统调用时间
            struct timespec start, end;
            clock_gettime(CLOCK_MONOTONIC, &start);
            getpid(); // 简单系统调用
            clock_gettime(CLOCK_MONOTONIC, &end);

            long syscall_time = (end.tv_sec - start.tv_sec) * 1000000000 +
                               (end.tv_nsec - start.tv_nsec);

            if (syscall_time > NORMAL_SYSCALL_TIME * 5) {
                // 系统调用被拦截或调试
                syscall_hooking_detected();
            }
        }
    }).detach();
}
```

### 3.4 反调试响应策略

```cpp
enum class AntiDebugResponse {
    EXIT_SILENTLY,
    CORRUPT_DATA,
    FAKE_EXECUTION,
    CRASH_GRACEFULLY,
    REPORT_TO_SERVER
};

void execute_anti_debug_response() {
    static int detection_count = 0;
    detection_count++;

    // 根据检测次数选择不同响应策略
    AntiDebugResponse response = select_response_strategy(detection_count);

    switch (response) {
        case AntiDebugResponse::EXIT_SILENTLY:
            _exit(0);
            break;

        case AntiDebugResponse::CORRUPT_DATA:
            corrupt_critical_data();
            break;

        case AntiDebugResponse::FAKE_EXECUTION:
            enter_fake_execution_mode();
            break;

        case AntiDebugResponse::CRASH_GRACEFULLY:
            trigger_controlled_crash();
            break;

        case AntiDebugResponse::REPORT_TO_SERVER:
            report_debug_attempt();
            _exit(1);
            break;
    }
}

void corrupt_critical_data() {
    // 破坏关键数据结构，使分析结果无效
    extern char critical_data_start[];
    extern char critical_data_end[];

    size_t size = critical_data_end - critical_data_start;
    for (size_t i = 0; i < size; i++) {
        critical_data_start[i] ^= 0xFF;
    }
}

void enter_fake_execution_mode() {
    // 进入虚假执行模式，返回错误分析结果
    global_fake_mode = true;

    // 修改函数指针，指向虚假实现
    redirect_function_calls();
}
```

---

## 4. 分析与绕过方法

### 4.1 静态分析 init_array

```python
# 分析 init_array 段的工具
import subprocess
from elftools.elf.elffile import ELFFile

class InitArrayAnalyzer:
    def __init__(self, so_path):
        self.so_path = so_path
        self.init_functions = []

    def analyze_init_array(self):
        # 使用 readelf 获取 init_array 信息
        result = subprocess.run(['readelf', '-d', self.so_path],
                               capture_output=True, text=True)

        for line in result.stdout.split('\n'):
            if 'INIT_ARRAY' in line:
                # 解析 init_array 地址和大小
                self.parse_init_array_info(line)

    def extract_function_addresses(self):
        with open(self.so_path, 'rb') as f:
            elf = ELFFile(f)

            # 找到 .init_array 段
            init_array_section = elf.get_section_by_name('.init_array')
            if init_array_section:
                data = init_array_section.data()

                # 解析函数指针 (8 字节对齐)
                for i in range(0, len(data), 8):
                    if i + 8 <= len(data):
                        func_addr = int.from_bytes(data[i:i+8], 'little')
                        self.init_functions.append(func_addr)
                        print(f"[+] Init function at: 0x{func_addr:x}")

    def disassemble_functions(self):
        # 使用 objdump 反汇编每个初始化函数
        for addr in self.init_functions:
            print(f"\n[+] Disassembling function at 0x{addr:x}")
            subprocess.run(['objdump', '-d', '--start-address', hex(addr),
                          '--stop-address', hex(addr + 0x100), self.so_path])

# 使用示例
analyzer = InitArrayAnalyzer('target.so')
analyzer.analyze_init_array()
analyzer.extract_function_addresses()
analyzer.disassemble_functions()
```

### 4.2 Frida Hook init_array

```javascript
// Hook init_array 执行
function monitor_init_array() {
    // Hook constructor 函数调用
    var call_constructors = Module.findExportByName(
        "linker64", "_ZN6soinfo17call_constructorsEv"
    );
    if (call_constructors) {
        Interceptor.attach(call_constructors, {
            onEnter: function(args) {
                var soinfo = args[0];
                var soname = get_soname(soinfo);
                console.log("[+] Calling constructors for: " + soname);

                this.soname = soname;
                this.start_time = Date.now();
            },
            onLeave: function(retval) {
                var duration = Date.now() - this.start_time;
                console.log("[+] Constructors completed for " + this.soname +
                           " in " + duration + "ms");
            }
        });
    }

    // Hook 目标 SO 的每个 init_array 函数
    var target_module = Process.findModuleByName("libtarget.so");
    if (target_module) {
        analyze_init_array_section(target_module);
    }
}

function analyze_init_array_section(module) {
    // 解析 ELF 文件找到 init_array 段
    var elf_base = module.base;

    // 获取 Program 头表偏移
    var phoff = elf_base.add(0x20).readU64();
    var phnum = elf_base.add(0x38).readU16();

    // 遍历 Program 头，查找 PT_DYNAMIC
    for (var i = 0; i < phnum; i++) {
        var ph_addr = elf_base.add(phoff).add(i * 56);
        var p_type = ph_addr.readU32();

        if (p_type === 2) { // PT_DYNAMIC
            var p_vaddr = ph_addr.add(16).readU64();
            var dynamic_addr = elf_base.add(p_vaddr);

            parse_dynamic_section(dynamic_addr, module);
            break;
        }
    }
}

function parse_dynamic_section(dynamic_addr, module) {
    var addr = dynamic_addr;

    while (true) {
        var tag = addr.readU64();
        var val = addr.add(8).readU64();

        if (tag === 0) break; // DT_NULL

        if (tag === 25) { // DT_INIT_ARRAY
            var init_array_addr = module.base.add(val);
            console.log("[+] Found init_array at: " + init_array_addr);

            // Hook init_array 中每个函数
            hook_init_array_functions(init_array_addr, module);
        } else if (tag === 27) { // DT_INIT_ARRAYSZ
            var array_size = val;
            console.log("[+] Init_array size: " + array_size);
        }

        addr = addr.add(16);
    }
}

function hook_init_array_functions(init_array_addr, module) {
    var num_functions = 10; // 假设最多 10 个函数

    for (var i = 0; i < num_functions; i++) {
        var func_ptr_addr = init_array_addr.add(i * 8);
        var func_addr = func_ptr_addr.readPointer();

        if (func_addr.isNull()) break;

        console.log("[+] Hooking init function " + i + " at: " + func_addr);

        Interceptor.attach(func_addr, {
            onEnter: function(args) {
                console.log("[!] Init function called");

                // 打印调用栈
                console.log(Thread.backtrace(this.context, Backtracer.ACCURATE)
                    .map(DebugSymbol.fromAddress).join('\n'));
            },
            onLeave: function(retval) {
                console.log("[!] Init function completed");
            }
        });
    }
}
```

### 4.3 绕过反调试

```javascript
// 绕过 ptrace 检测
function bypass_ptrace() {
    var ptrace = Module.findExportByName("libc.so", "ptrace");
    if (ptrace) {
        Interceptor.attach(ptrace, {
            onEnter: function(args) {
                var request = args[0].toInt32();
                if (request === 0) { // PTRACE_TRACEME
                    console.log("[+] Blocking PTRACE_TRACEME");
                    args[0] = ptr(-1);
                }
            },
            onLeave: function(retval) {
                // 始终返回成功
                retval.replace(ptr(0));
            }
        });
    }
}

// 绕过文件检测
function bypass_file_detection() {
    var access = Module.findExportByName("libc.so", "access");
    var openat = Module.findExportByName("libc.so", "openat");

    var blocked_paths = [
        "/data/local/tmp/frida-server",
        "/proc/self/maps",
        "/proc/self/status"
    ];

    if (access) {
        Interceptor.attach(access, {
            onEnter: function(args) {
                var path = args[0].readCString();
                if (blocked_paths.some(p => path.includes(p))) {
                    console.log("[+] Blocking access to: " + path);
                    args[0] = Memory.allocUtf8String("/dev/null");
                }
            }
        });
    }

    if (openat) {
        Interceptor.attach(openat, {
            onEnter: function(args) {
                var path = args[1].readCString();
                if (blocked_paths.some(p => path.includes(p))) {
                    console.log("[+] Blocking openat for: " + path);
                    args[1] = Memory.allocUtf8String("/dev/null");
                }
            }
        });
    }
}

// 绕过时间检测
function bypass_timing_detection() {
    var clock_gettime = Module.findExportByName("libc.so", "clock_gettime");
    if (clock_gettime) {
        var fake_time = {
            sec: 1640995200, // 固定时间戳
            nsec: 0
        };

        Interceptor.attach(clock_gettime, {
            onLeave: function(retval) {
                var timespec = this.context.x1; // 第二个参数
                if (!timespec.isNull()) {
                    // 写入固定时间值
                    timespec.writeU64(fake_time.sec);
                    timespec.add(8).writeU64(fake_time.nsec);

                    // 每次调用略微增加纳秒
                    fake_time.nsec += 1000;
                }
            }
        });
    }
}
```

### 4.4 Hook 字符串解密

```javascript
// 字符串检测混淆检测
function detect_string_obfuscation(so_path) {
    var module = Process.findModuleByName(so_path);
    if (!module) return;

    // 扫描解密函数模式
    var pattern = "48 89 ?? 48 89 ?? 48 83 ?? ?? 8B ?? ??"; // x64 解密函数模式

    Memory.scan(module.base, module.size, pattern, {
        onMatch: function(address, size) {
            console.log("[+] Found potential decryption function at: " + address);

            Interceptor.attach(address, {
                onEnter: function(args) {
                    console.log("[+] Decryption function called");
                    this.args = Array.prototype.slice.call(args);
                },
                onLeave: function(retval) {
                    // 尝试读取解密结果
                    try {
                        var result = retval.readCString();
                        if (result && result.length > 0 && result.length < 256) {
                            console.log("[+] Decrypted string: " + result);
                        }
                    } catch (e) {
                        // 可能不是字符串
                    }
                }
            });
        },
        onComplete: function() {
            console.log("[+] Decryption function scan completed");
        }
    });
}

// 智能反调试绕过
function intelligent_anti_debug_bypass() {
    // 1. 自动检测并绕过常见反调试技术
    bypass_ptrace();
    bypass_file_detection();
    bypass_timing_detection();

    // 2. 监控 init_array 执行
    monitor_init_array();

    // 3. Hook 字符串解密
    detect_string_obfuscation("libtarget.so");

    // 4. 设置定期检查，处理新反调试机制
    setInterval(function() {
        check_new_anti_debug_mechanisms();
    }, 5000);
}

function check_new_anti_debug_mechanisms() {
    // 检测新反调试线程
    var threads = Process.enumerateThreads();
    threads.forEach(function(thread) {
        // 检查线程调用栈是否包含反调试函数
        var backtrace = Thread.backtrace(thread.context, Backtracer.ACCURATE);
        // 分析并处理...
    });
}
```

---

## 5. 高级防护策略

### 5.1 多层级保护机制

```cpp
// 实现多层级保护机制
class ComprehensiveProtection {
private:
    static bool stage1_passed;
    static bool stage2_passed;
    static bool stage3_passed;

public:
    // 第一阶段：基础检测
    __attribute__((constructor(101)))
    static void protection_stage1() {
        if (basic_anti_debug_check()) {
            stage1_passed = true;
            decrypt_stage2_key();
        } else {
            enter_decoy_mode();
        }
    }

    // 第二阶段：深度检测
    __attribute__((constructor(102)))
    static void protection_stage2() {
        if (!stage1_passed) return;

        if (advanced_detection()) {
            stage2_passed = true;
            unlock_critical_functions();
        } else {
            corrupt_stage2_data();
        }
    }

    // 第三阶段：运行时保护
    __attribute__((constructor(103)))
    static void protection_stage3() {
        if (!stage2_passed) return;

        start_runtime_protection();
        stage3_passed = true;
    }

    // 关键函数只有在所有检测通过后才能正常执行
    static bool is_protection_active() {
        return stage1_passed && stage2_passed && stage3_passed;
    }
};
```

### 5.2 自适应响应系统

```cpp
class AdaptiveResponseSystem {
private:
    enum ThreatLevel {
        NO_THREAT = 0,
        LOW_THREAT = 1,
        MEDIUM_THREAT = 2,
        HIGH_THREAT = 3,
        CRITICAL_THREAT = 4
    };

    static ThreatLevel assess_threat_level() {
        int threat_score = 0;

        // 各种检测权重评分
        if (detect_frida()) threat_score += 30;
        if (detect_debugger()) threat_score += 25;
        if (detect_hook()) threat_score += 20;
        if (detect_emulator()) threat_score += 15;
        if (detect_root()) threat_score += 10;

        if (threat_score >= 80) return CRITICAL_THREAT;
        if (threat_score >= 60) return HIGH_THREAT;
        if (threat_score >= 40) return MEDIUM_THREAT;
        if (threat_score >= 20) return LOW_THREAT;
        return NO_THREAT;
    }

public:
    static void adaptive_response() {
        ThreatLevel level = assess_threat_level();

        switch (level) {
            case CRITICAL_THREAT:
                immediate_termination();
                break;
            case HIGH_THREAT:
                data_corruption_and_exit();
                break;
            case MEDIUM_THREAT:
                fake_execution_mode();
                break;
            case LOW_THREAT:
                increased_monitoring();
                break;
            case NO_THREAT:
                normal_execution();
                break;
        }
    }
};
```

---

## 总结

**防护方的核心策略**：

1. 多层级检测机制，分阶段验证
2. 字符串动态解密，避免静态分析
3. 时间和行为检测，识别调试环境
4. 自适应响应策略，根据威胁等级调整

**分析方的应对策略**：

1. 静态分析结合动态 Hook
2. 全面的 API 拦截和重定向
3. 时间和环境模拟
4. 自动化绕过脚本开发

这一技术对抗将持续演进，双方都需要不断提升技术水平以应对新的挑战。
