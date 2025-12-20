// 启用 GNU 扩展功能以确保 dladdr 可用
#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif

#include "art_method_hook.h"
#include "anti_reverse.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

// 平台兼容性处理
#include <dlfcn.h>  // 在大多数 Unix-like 系统上都可用

// 如果某些平台不支持 dlfcn.h，可以在这里添加替代实现
#ifndef RTLD_LAZY
#define RTLD_LAZY 1
#endif

// 平台兼容性处理
#ifdef __ANDROID__
#include <sys/system_properties.h>
#else
// 非 Android 平台的替代实现
#define PROP_VALUE_MAX 256
static int __system_property_get(const char* name, char* value) {
    // 桌面平台的模拟实现
    if (strcmp(name, "ro.build.version.sdk") == 0) {
        strcpy(value, "28"); // 模拟 Android API 28
        return strlen(value);
    }
    value[0] = '\0';
    return 0;
}
#endif

// 全局变量
art_version_t g_art_version = ART_VERSION_UNKNOWN;
int g_art_method_hook_initialized = 0;

// 内部函数声明
static void* find_libart_symbol(const char* symbol_name);
static int get_android_api_level(void);
static void* create_executable_memory(size_t size);

// ========== ART版本检测实现 ==========

art_version_t detect_art_version(void) {
    if (g_art_version != ART_VERSION_UNKNOWN) {
        return g_art_version;
    }
    
    // 通过Android API级别确定ART版本
    int api_level = get_android_api_level();
    
    switch (api_level) {
        case 21: g_art_version = ART_VERSION_5_0; break;
        case 22: g_art_version = ART_VERSION_5_1; break;
        case 23: g_art_version = ART_VERSION_6_0; break;
        case 24: g_art_version = ART_VERSION_7_0; break;
        case 25: g_art_version = ART_VERSION_7_1; break;
        case 26: g_art_version = ART_VERSION_8_0; break;
        case 27: g_art_version = ART_VERSION_8_1; break;
        case 28: g_art_version = ART_VERSION_9_0; break;
        case 29: g_art_version = ART_VERSION_10_0; break;
        case 30: g_art_version = ART_VERSION_11_0; break;
        case 31: g_art_version = ART_VERSION_12_0; break;
        case 33: g_art_version = ART_VERSION_13_0; break;
        case 34: g_art_version = ART_VERSION_14_0; break;
        default:
            if (api_level >= 34) {
                g_art_version = ART_VERSION_14_0;
            } else if (api_level >= 21) {
                g_art_version = ART_VERSION_5_0; // 默认到最早支持的版本
            } else {
                g_art_version = ART_VERSION_UNKNOWN;
            }
            break;
    }
    
    return g_art_version;
}

const char* get_art_version_string(art_version_t version) {
    switch (version) {
        case ART_VERSION_5_0: return "Android 5.0 (API 21)";
        case ART_VERSION_5_1: return "Android 5.1 (API 22)";
        case ART_VERSION_6_0: return "Android 6.0 (API 23)";
        case ART_VERSION_7_0: return "Android 7.0 (API 24)";
        case ART_VERSION_7_1: return "Android 7.1 (API 25)";
        case ART_VERSION_8_0: return "Android 8.0 (API 26)";
        case ART_VERSION_8_1: return "Android 8.1 (API 27)";
        case ART_VERSION_9_0: return "Android 9.0 (API 28)";
        case ART_VERSION_10_0: return "Android 10.0 (API 29)";
        case ART_VERSION_11_0: return "Android 11.0 (API 30)";
        case ART_VERSION_12_0: return "Android 12.0 (API 31)";
        case ART_VERSION_13_0: return "Android 13.0 (API 33)";
        case ART_VERSION_14_0: return "Android 14.0 (API 34)";
        default: return "Unknown";
    }
}

int is_art_version_supported(art_version_t version) {
    return version >= ART_VERSION_5_0 && version <= ART_VERSION_14_0;
}

// ========== ArtMethod查找和操作实现 ==========

ArtMethod* get_art_method(JNIEnv* env, jclass clazz, const char* method_name, const char* signature) {
    if (!env || !clazz || !method_name || !signature) {
        return NULL;
    }
    
    // 获取jmethodID
    jmethodID method_id = (*env)->GetMethodID(env, clazz, method_name, signature);
    if (!method_id) {
        // 尝试静态方法
        (*env)->ExceptionClear(env);
        method_id = (*env)->GetStaticMethodID(env, clazz, method_name, signature);
    }
    
    if (!method_id) {
        (*env)->ExceptionClear(env);
        return NULL;
    }
    
    return jmethodid_to_art_method(method_id);
}

ArtMethod* jmethodid_to_art_method(jmethodID method_id) {
    if (!method_id) return NULL;
    
    // jmethodID在ART中就是ArtMethod指针
    // 但需要验证指针的有效性
    ArtMethod* art_method = (ArtMethod*)method_id;
    
    if (!validate_art_method(art_method)) {
        return NULL;
    }
    
    return art_method;
}

int validate_art_method(ArtMethod* art_method) {
    if (!art_method) return 0;
    
    // 基本指针检查
    if ((uintptr_t)art_method < 0x1000 || (uintptr_t)art_method > 0x7fffffff) {
        return 0;
    }
    
    // 尝试读取访问标志来验证
    art_version_t version = detect_art_version();
    if (version == ART_VERSION_UNKNOWN) return 0;
    
    uint32_t access_flags = get_art_method_access_flags(art_method, version);
    
    // 检查访问标志是否合理
    if (access_flags == 0 || access_flags > 0xFFFF) {
        return 0;
    }
    
    return 1;
}

uint32_t get_art_method_access_flags(ArtMethod* art_method, art_version_t version) {
    if (!art_method) return 0;
    
    // 所有版本的ArtMethod都有access_flags_字段在相同位置
    return art_method->v5_6.access_flags_;
}

art_method_result_t set_art_method_access_flags(ArtMethod* art_method, art_version_t version, uint32_t flags) {
    art_method_result_t result = {0};
    
    if (!art_method) {
        strcpy(result.error_msg, "Invalid ArtMethod pointer");
        return result;
    }
    
    // 修改内存保护
    if (change_memory_protection(art_method, sizeof(ArtMethod), PROT_READ | PROT_WRITE) != 0) {
        strcpy(result.error_msg, "Failed to change memory protection");
        return result;
    }
    
    // 保存原始值
    uint32_t original_flags = art_method->v5_6.access_flags_;
    
    // 设置新的访问标志
    art_method->v5_6.access_flags_ = flags;
    
    // 恢复内存保护
    change_memory_protection(art_method, sizeof(ArtMethod), PROT_READ);
    
    result.success = 1;
    result.original_entry_point = (void*)(uintptr_t)original_flags;
    return result;
}

// ========== JNI入口点操作实现 ==========

void* get_art_method_jni_entry_point(ArtMethod* art_method, art_version_t version) {
    if (!art_method) return NULL;
    
    switch (version) {
        case ART_VERSION_5_0:
        case ART_VERSION_5_1:
        case ART_VERSION_6_0:
            return art_method->v5_6.entry_point_from_jni_;
            
        case ART_VERSION_7_0:
        case ART_VERSION_7_1:
        case ART_VERSION_8_0:
        case ART_VERSION_8_1:
            return art_method->v7_8.ptr_sized_fields_.entry_point_from_jni_;
            
        case ART_VERSION_9_0:
        case ART_VERSION_10_0:
        case ART_VERSION_11_0:
        case ART_VERSION_12_0:
        case ART_VERSION_13_0:
        case ART_VERSION_14_0:
            // Android 9+使用不同的结构
            return art_method->v9_plus.ptr_sized_fields_.data_;
            
        default:
            return NULL;
    }
}

art_method_result_t set_art_method_jni_entry_point(ArtMethod* art_method, art_version_t version, void* entry_point) {
    art_method_result_t result = {0};
    
    if (!art_method || !entry_point) {
        strcpy(result.error_msg, "Invalid parameters");
        return result;
    }
    
    // 修改内存保护
    if (change_memory_protection(art_method, sizeof(ArtMethod), PROT_READ | PROT_WRITE) != 0) {
        strcpy(result.error_msg, "Failed to change memory protection");
        return result;
    }
    
    // 保存原始入口点
    void* original_entry_point = get_art_method_jni_entry_point(art_method, version);
    result.original_entry_point = original_entry_point;
    
    // 设置新的入口点
    switch (version) {
        case ART_VERSION_5_0:
        case ART_VERSION_5_1:
        case ART_VERSION_6_0:
            art_method->v5_6.entry_point_from_jni_ = entry_point;
            break;
            
        case ART_VERSION_7_0:
        case ART_VERSION_7_1:
        case ART_VERSION_8_0:
        case ART_VERSION_8_1:
            art_method->v7_8.ptr_sized_fields_.entry_point_from_jni_ = entry_point;
            break;
            
        case ART_VERSION_9_0:
        case ART_VERSION_10_0:
        case ART_VERSION_11_0:
        case ART_VERSION_12_0:
        case ART_VERSION_13_0:
        case ART_VERSION_14_0:
            art_method->v9_plus.ptr_sized_fields_.data_ = entry_point;
            break;
            
        default:
            strcpy(result.error_msg, "Unsupported ART version");
            change_memory_protection(art_method, sizeof(ArtMethod), PROT_READ);
            return result;
    }
    
    // 恢复内存保护
    change_memory_protection(art_method, sizeof(ArtMethod), PROT_READ);
    
    result.success = 1;
    return result;
}

void* get_art_method_quick_entry_point(ArtMethod* art_method, art_version_t version) {
    if (!art_method) return NULL;
    
    switch (version) {
        case ART_VERSION_5_0:
        case ART_VERSION_5_1:
        case ART_VERSION_6_0:
            return art_method->v5_6.entry_point_from_quick_compiled_code_;
            
        case ART_VERSION_7_0:
        case ART_VERSION_7_1:
        case ART_VERSION_8_0:
        case ART_VERSION_8_1:
            return art_method->v7_8.ptr_sized_fields_.entry_point_from_quick_compiled_code_;
            
        case ART_VERSION_9_0:
        case ART_VERSION_10_0:
        case ART_VERSION_11_0:
        case ART_VERSION_12_0:
        case ART_VERSION_13_0:
        case ART_VERSION_14_0:
            return art_method->v9_plus.ptr_sized_fields_.entry_point_from_quick_compiled_code_;
            
        default:
            return NULL;
    }
}

art_method_result_t set_art_method_quick_entry_point(ArtMethod* art_method, art_version_t version, void* entry_point) {
    art_method_result_t result = {0};
    
    if (!art_method || !entry_point) {
        strcpy(result.error_msg, "Invalid parameters");
        return result;
    }
    
    // 修改内存保护
    if (change_memory_protection(art_method, sizeof(ArtMethod), PROT_READ | PROT_WRITE) != 0) {
        strcpy(result.error_msg, "Failed to change memory protection");
        return result;
    }
    
    // 保存原始入口点
    void* original_entry_point = get_art_method_quick_entry_point(art_method, version);
    result.original_entry_point = original_entry_point;
    
    // 设置新的入口点
    switch (version) {
        case ART_VERSION_5_0:
        case ART_VERSION_5_1:
        case ART_VERSION_6_0:
            art_method->v5_6.entry_point_from_quick_compiled_code_ = entry_point;
            break;
            
        case ART_VERSION_7_0:
        case ART_VERSION_7_1:
        case ART_VERSION_8_0:
        case ART_VERSION_8_1:
            art_method->v7_8.ptr_sized_fields_.entry_point_from_quick_compiled_code_ = entry_point;
            break;
            
        case ART_VERSION_9_0:
        case ART_VERSION_10_0:
        case ART_VERSION_11_0:
        case ART_VERSION_12_0:
        case ART_VERSION_13_0:
        case ART_VERSION_14_0:
            art_method->v9_plus.ptr_sized_fields_.entry_point_from_quick_compiled_code_ = entry_point;
            break;
            
        default:
            strcpy(result.error_msg, "Unsupported ART version");
            change_memory_protection(art_method, sizeof(ArtMethod), PROT_READ);
            return result;
    }
    
    // 恢复内存保护
    change_memory_protection(art_method, sizeof(ArtMethod), PROT_READ);
    
    result.success = 1;
    return result;
}

// ========== 高级方法注册实现 ==========

art_method_result_t register_native_method_direct(JNIEnv* env, jclass clazz, 
                                                 const char* method_name, 
                                                 const char* signature, 
                                                 void* native_func) {
    art_method_result_t result = {0};
    
    if (!env || !clazz || !method_name || !signature || !native_func) {
        strcpy(result.error_msg, "Invalid parameters");
        return result;
    }
    
    // 检测ART版本
    art_version_t version = detect_art_version();
    if (!is_art_version_supported(version)) {
        strcpy(result.error_msg, "Unsupported ART version");
        return result;
    }
    
    // 获取ArtMethod
    ArtMethod* art_method = get_art_method(env, clazz, method_name, signature);
    if (!art_method) {
        strcpy(result.error_msg, "Failed to get ArtMethod");
        return result;
    }
    
    // 验证方法是否为native方法
    uint32_t access_flags = get_art_method_access_flags(art_method, version);
    if (!(access_flags & kAccNative)) {
        // 如果不是native方法，将其标记为native
        access_flags |= kAccNative;
        art_method_result_t flag_result = set_art_method_access_flags(art_method, version, access_flags);
        if (!flag_result.success) {
            strcpy(result.error_msg, "Failed to set native flag");
            return result;
        }
    }
    
    // 创建JNI桥接函数
    void* bridge_func = create_jni_bridge(native_func, version);
    if (!bridge_func) {
        strcpy(result.error_msg, "Failed to create JNI bridge");
        return result;
    }
    
    // 直接设置ArtMethod的JNI入口点
    result = set_art_method_jni_entry_point(art_method, version, bridge_func);
    if (!result.success) {
        return result;
    }
    
    // 同时设置快速编译代码入口点
    art_method_result_t quick_result = set_art_method_quick_entry_point(art_method, version, bridge_func);
    if (!quick_result.success) {
        // 恢复JNI入口点
        set_art_method_jni_entry_point(art_method, version, result.original_entry_point);
        strcpy(result.error_msg, "Failed to set quick entry point");
        result.success = 0;
        return result;
    }
    
    result.success = 1;
    return result;
}

int register_native_methods_direct(JNIEnv* env, const char* class_name, 
                                  const native_method_t* methods, int method_count) {
    if (!env || !class_name || !methods || method_count <= 0) {
        return 0;
    }
    
    // 查找类
    jclass clazz = (*env)->FindClass(env, class_name);
    if (!clazz) {
        (*env)->ExceptionClear(env);
        return 0;
    }
    
    int registered_count = 0;
    
    // 逐个注册方法
    for (int i = 0; i < method_count; i++) {
        art_method_result_t result = register_native_method_direct(
            env, clazz, methods[i].name, methods[i].signature, methods[i].fnPtr);
        
        if (result.success) {
            registered_count++;
        }
    }
    
    return registered_count;
}

void* create_jni_bridge(void* target_func, art_version_t version) {
    if (!target_func) return NULL;
    
    // 分配可执行内存
    size_t code_size = 256; // 足够的空间存放桥接代码
    void* bridge_code = create_executable_memory(code_size);
    if (!bridge_code) return NULL;
    
    // 生成桥接代码
    if (generate_random_jni_bridge(target_func, bridge_code, code_size) != 0) {
        munmap(bridge_code, code_size);
        return NULL;
    }
    
    return bridge_code;
}

// ========== 内存保护操作实现 ==========

int change_memory_protection(void* addr, size_t size, int prot) {
    if (!addr || size == 0) return -1;
    
    // 对齐到页面边界
    void* aligned_addr = align_to_page(addr);
    size_t page_size = get_page_size();
    size_t aligned_size = ((size + page_size - 1) / page_size) * page_size;
    
    return mprotect(aligned_addr, aligned_size, prot);
}

size_t get_page_size(void) {
    static size_t page_size = 0;
    if (page_size == 0) {
        page_size = sysconf(_SC_PAGESIZE);
    }
    return page_size;
}

void* align_to_page(void* addr) {
    size_t page_size = get_page_size();
    return (void*)((uintptr_t)addr & ~(page_size - 1));
}

// ========== Hook检测和对抗实现 ==========

int detect_art_method_hook(ArtMethod* art_method, art_version_t version) {
    if (!art_method) return 0;
    
    // 获取当前的入口点
    void* jni_entry = get_art_method_jni_entry_point(art_method, version);
    void* quick_entry = get_art_method_quick_entry_point(art_method, version);
    
    // 检查入口点是否指向可疑的内存区域
    if (jni_entry) {
        // 检查是否指向已加载的可疑库
        Dl_info dl_info;
        if (dladdr(jni_entry, &dl_info)) {
            if (dl_info.dli_fname) {
                // 检查库名是否包含Hook框架特征
                if (strstr(dl_info.dli_fname, "frida") ||
                    strstr(dl_info.dli_fname, "xposed") ||
                    strstr(dl_info.dli_fname, "substrate")) {
                    return 1;
                }
            }
        }
    }
    
    return 0;
}

int detect_jni_function_table_hook(JNIEnv* env) {
    if (!env) return 0;
    
    // 检查JNI函数表的完整性
    // 计算JNI函数表的校验和
    uint32_t current_checksum = calculate_function_checksum((void*)env);
    
    // 这里应该与已知的良好校验和进行比较
    // 为了演示，我们检查一些关键函数指针是否合理
    if (!(*env)->FindClass ||
        !(*env)->GetMethodID ||
        !(*env)->RegisterNatives) {
        return 1;
    }
    
    return 0;
}

art_method_result_t restore_art_method(ArtMethod* art_method, art_version_t version, void* original_entry_point) {
    return set_art_method_jni_entry_point(art_method, version, original_entry_point);
}

// ========== 内部辅助函数实现 ==========

static void* find_libart_symbol(const char* symbol_name) {
    // 尝试不同的libart.so路径
    const char* libart_paths[] = {
        "libart.so",
        "/system/lib/libart.so",
        "/system/lib64/libart.so",
        NULL
    };
    
    for (int i = 0; libart_paths[i]; i++) {
        void* handle = dlopen(libart_paths[i], RTLD_LAZY);
        if (handle) {
            void* symbol = dlsym(handle, symbol_name);
            if (symbol) {
                return symbol;
            }
        }
    }
    
    return NULL;
}

static int get_android_api_level(void) {
    char prop_value[256];
    int api_level = 0;
    
    if (__system_property_get("ro.build.version.sdk", prop_value) > 0) {
        api_level = atoi(prop_value);
    }
    
    if (api_level == 0) {
        // 备用方法：通过文件系统特征判断
        if (access("/system/framework/core-libart.jar", F_OK) == 0) {
            api_level = 28; // Android 9+
        } else if (access("/system/framework/core-oj.jar", F_OK) == 0) {
            api_level = 26; // Android 8+
        } else {
            api_level = 21; // 默认到Android 5.0
        }
    }
    
    return api_level;
}

static void* create_executable_memory(size_t size) {
    void* mem = mmap(NULL, size, PROT_READ | PROT_WRITE | PROT_EXEC, 
                     MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    
    if (mem == MAP_FAILED) {
        return NULL;
    }
    
    return mem;
}

// ========== 工具函数实现 ==========

uint32_t calculate_function_checksum(void* func_ptr) {
    if (!func_ptr) return 0;
    
    uint32_t checksum = 5381;
    uint8_t* bytes = (uint8_t*)func_ptr;
    
    // 计算函数前64字节的校验和
    for (int i = 0; i < 64; i++) {
        checksum = ((checksum << 5) + checksum) + bytes[i];
    }
    
    return checksum;
}

int generate_random_jni_bridge(void* target_func, void* bridge_code, size_t code_size) {
    if (!target_func || !bridge_code || code_size < 32) return -1;
    
    uint8_t* code = (uint8_t*)bridge_code;
    
#ifdef __aarch64__
    // ARM64 JNI桥接代码
    // 这是一个简化的桥接，实际实现会更复杂
    uint32_t arm64_code[] = {
        0xa9bf7bfd,  // stp x29, x30, [sp, #-16]!
        0x910003fd,  // mov x29, sp
        0x58000080,  // ldr x0, #16
        0xd63f0000,  // blr x0
        0xa8c17bfd,  // ldp x29, x30, [sp], #16
        0xd65f03c0,  // ret
        0x00000000,  // target function address (low)
        0x00000000   // target function address (high)
    };
    
    if (code_size < sizeof(arm64_code)) return -1;
    
    memcpy(code, arm64_code, sizeof(arm64_code));
    
    // 设置目标函数地址
    uint64_t target_addr = (uint64_t)target_func;
    *((uint32_t*)(code + 24)) = (uint32_t)(target_addr & 0xFFFFFFFF);
    *((uint32_t*)(code + 28)) = (uint32_t)(target_addr >> 32);
    
#elif defined(__arm__)
    // ARM32 JNI桥接代码
    uint32_t arm32_code[] = {
        0xe52de004,  // push {lr}
        0xe59f0004,  // ldr r0, [pc, #4]
        0xe12fff30,  // blx r0
        0xe49df004,  // pop {lr}
        0xe12fff1e,  // bx lr
        0x00000000   // target function address
    };
    
    if (code_size < sizeof(arm32_code)) return -1;
    
    memcpy(code, arm32_code, sizeof(arm32_code));
    
    // 设置目标函数地址
    *((uint32_t*)(code + 20)) = (uint32_t)target_func;
    
#else
    return -1; // 不支持的架构
#endif
    
    // 清空指令缓存
    __builtin___clear_cache(code, code + code_size);
    
    return 0;
}

void* obfuscate_function_pointer(void* func_ptr, uint32_t key) {
    if (!func_ptr) return NULL;
    return (void*)((uintptr_t)func_ptr ^ key);
}

void* deobfuscate_function_pointer(void* obfuscated_ptr, uint32_t key) {
    if (!obfuscated_ptr) return NULL;
    return (void*)((uintptr_t)obfuscated_ptr ^ key);
}

// ========== 调试和诊断实现 ==========

void dump_art_method_info(ArtMethod* art_method, art_version_t version) {
    if (!art_method) {
        printf("ArtMethod: NULL\n");
        return;
    }
    
    printf("ArtMethod Info:\n");
    printf("  Address: %p\n", art_method);
    printf("  ART Version: %s\n", get_art_version_string(version));
    printf("  Access Flags: 0x%08x\n", get_art_method_access_flags(art_method, version));
    printf("  JNI Entry Point: %p\n", get_art_method_jni_entry_point(art_method, version));
    printf("  Quick Entry Point: %p\n", get_art_method_quick_entry_point(art_method, version));
    
    // 检查是否被Hook
    if (detect_art_method_hook(art_method, version)) {
        printf("  Status: HOOKED\n");
    } else {
        printf("  Status: Normal\n");
    }
}

int verify_jni_env_integrity(JNIEnv* env) {
    return !detect_jni_function_table_hook(env);
}

int get_art_runtime_info(char* info_buffer, size_t buffer_size) {
    if (!info_buffer || buffer_size == 0) return -1;
    
    art_version_t version = detect_art_version();
    
    snprintf(info_buffer, buffer_size,
        "ART Runtime Info:\n"
        "  Version: %s\n"
        "  API Level: %d\n" 
        "  Supported: %s\n"
        "  Hook Detection: %s\n",
        get_art_version_string(version),
        (int)version,
        is_art_version_supported(version) ? "Yes" : "No",
        g_art_method_hook_initialized ? "Active" : "Inactive"
    );
    
    return 0;
}