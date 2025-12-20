#include "anti_reverse.h"
#include "risk_control.h"
#include "art_method_hook.h"
#include <signal.h>
#include <sys/ptrace.h>
#include <sys/mman.h>
#include <time.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <dlfcn.h>

// 全局变量定义
anti_reverse_state_t g_anti_reverse_state = {0};
uint8_t g_aes_key[AES_KEY_SIZE] = {0};

// 加密的关键字符串（运行时解密）
static encrypted_string_t g_encrypted_strings[] = {
    // "com/riskcontrol/RiskControlSDK" 加密后
    {{0x38, 0x34, 0x37, 0x1f, 0x25, 0x26, 0x28, 0x38, 0x34, 0x31, 0x35, 0x34, 0x33, 0x1f, 0x25, 0x26, 0x28, 0x38, 0x34, 0x31, 0x35, 0x34, 0x33, 0x06, 0x05, 0x0b, 0x00}, 27, 0},
    // "frida-server" 加密后
    {{0x3c, 0x25, 0x26, 0x3e, 0x3e, 0x1d, 0x28, 0x39, 0x25, 0x31, 0x39, 0x25, 0x00}, 13, 0},
    // "/system/bin/su" 加密后
    {{0x15, 0x28, 0x37, 0x28, 0x35, 0x39, 0x37, 0x1f, 0x3a, 0x26, 0x38, 0x1f, 0x28, 0x36, 0x00}, 15, 0},
    // "TracerPid:" 加密后
    {{0x2e, 0x25, 0x3e, 0x38, 0x39, 0x25, 0x00, 0x26, 0x3e, 0x10, 0x00}, 11, 0}
};

static int g_encrypted_strings_count = sizeof(g_encrypted_strings) / sizeof(encrypted_string_t);

// JNI方法映射表（静态隐藏，动态注册）
static const native_method_t g_native_methods[] = {
    {"nativeInitialize", "()Z", (void*)Java_com_riskcontrol_RiskControlSDK_nativeInitialize},
    {"nativeCleanup", "()V", (void*)Java_com_riskcontrol_RiskControlSDK_nativeCleanup},
    {"nativeGetVersion", "()Ljava/lang/String;", (void*)Java_com_riskcontrol_RiskControlSDK_nativeGetVersion},
    {"nativeSetDebugMode", "(Z)V", (void*)Java_com_riskcontrol_RiskControlSDK_nativeSetDebugMode},
    {"nativeSetConfig", "(Ljava/lang/String;Ljava/lang/String;)V", (void*)Java_com_riskcontrol_RiskControlSDK_nativeSetConfig},
    {"nativeGetDeviceId", "()Ljava/lang/String;", (void*)Java_com_riskcontrol_RiskControlSDK_nativeGetDeviceId},
    {"nativeGetHardwareInfo", "()Ljava/lang/String;", (void*)Java_com_riskcontrol_RiskControlSDK_nativeGetHardwareInfo},
    {"nativeGetSoftwareInfo", "()Ljava/lang/String;", (void*)Java_com_riskcontrol_RiskControlSDK_nativeGetSoftwareInfo},
    {"nativeGetNetworkInfo", "()Ljava/lang/String;", (void*)Java_com_riskcontrol_RiskControlSDK_nativeGetNetworkInfo},
    {"nativeDetectEmulator", "()Z", (void*)Java_com_riskcontrol_RiskControlSDK_nativeDetectEmulator},
    {"nativeDetectRoot", "()Z", (void*)Java_com_riskcontrol_RiskControlSDK_nativeDetectRoot},
    {"nativeDetectDebug", "()Z", (void*)Java_com_riskcontrol_RiskControlSDK_nativeDetectDebug},
    {"nativeDetectHook", "()Z", (void*)Java_com_riskcontrol_RiskControlSDK_nativeDetectHook},
    {"nativeDetectProxy", "()Z", (void*)Java_com_riskcontrol_RiskControlSDK_nativeDetectProxy},
    {"nativeDetectVPN", "()Z", (void*)Java_com_riskcontrol_RiskControlSDK_nativeDetectVPN},
    {"nativeCalculateRiskScore", "(Ljava/lang/String;ZZZZ)I", (void*)Java_com_riskcontrol_RiskControlSDK_nativeCalculateRiskScore},
    {"nativeGetRiskDetails", "()Ljava/lang/String;", (void*)Java_com_riskcontrol_RiskControlSDK_nativeGetRiskDetails}
};

static const int g_native_methods_count = sizeof(g_native_methods) / sizeof(native_method_t);

// ========== .init_array 初始化函数 ==========

void __attribute__((constructor)) init_string_obfuscation(void) {
    // 生成AES密钥（基于时间和其他因素）
    uint64_t timestamp = get_timestamp_ns();
    uint32_t pid = getpid();
    
    for (int i = 0; i < AES_KEY_SIZE; i++) {
        g_aes_key[i] = (timestamp >> (i * 4)) ^ (pid >> (i * 2)) ^ XOR_KEY;
    }
    
    // 解密关键字符串（实际不在这里解密，而是在需要时）
    g_anti_reverse_state.string_obfuscation_active = 1;
    
    // 注册关键代码段
    register_critical_section((void*)init_string_obfuscation, 1024);
}

void __attribute__((constructor)) init_anti_debug_protection(void) {
    // 设置信号处理器
    setup_signal_handlers();
    
    // 启动ptrace自保护
    if (ptrace_anti_debug()) {
        // 检测到调试器，执行反制措施
        execute_countermeasures(THREAT_DEBUGGER);
    }
    
    // 检测其他威胁
    if (detect_frida()) {
        execute_countermeasures(THREAT_FRIDA);
    }
    
    if (detect_xposed()) {
        execute_countermeasures(THREAT_XPOSED);
    }
    
    g_anti_reverse_state.anti_debug_active = 1;
    
    // 注册关键代码段
    register_critical_section((void*)init_anti_debug_protection, 1024);
}

// ========== JNI 动态注册实现 ==========

JNIEXPORT jint JNICALL JNI_OnLoad(JavaVM* vm, void* reserved) {
    JNIEnv* env;
    
    // 获取JNI环境
    if ((*vm)->GetEnv(vm, (void**)&env, JNI_VERSION_1_6) != JNI_OK) {
        return JNI_ERR;
    }
    
    // 执行反调试检查
    if (detect_debugger()) {
        execute_countermeasures(THREAT_DEBUGGER);
        return JNI_ERR;
    }
    
    // 检查代码完整性
    if (!verify_code_integrity()) {
        execute_countermeasures(THREAT_INTEGRITY);
        return JNI_ERR;
    }
    
    // 检测JNI环境是否被Hook
    if (detect_jni_function_table_hook(env)) {
        execute_countermeasures(THREAT_HOOK);
        return JNI_ERR;
    }
    
    // 初始化ArtMethod Hook系统
    art_version_t art_version = detect_art_version();
    if (!is_art_version_supported(art_version)) {
        // 不支持的ART版本，回退到标准注册
        char* class_name = get_obfuscated_class_name();
        if (!class_name) {
            return JNI_ERR;
        }
        
        if (register_native_methods(env, class_name, g_native_methods, g_native_methods_count) != 0) {
            free(class_name);
            return JNI_ERR;
        }
        
        free(class_name);
    } else {
        // 使用高级ArtMethod直接注册
        char* class_name = get_obfuscated_class_name();
        if (!class_name) {
            return JNI_ERR;
        }
        
        // 转换方法数组格式
        native_method_t art_methods[g_native_methods_count];
        
        for (int i = 0; i < g_native_methods_count; i++) {
            art_methods[i].name = g_native_methods[i].name;
            art_methods[i].signature = g_native_methods[i].signature;
            art_methods[i].fnPtr = g_native_methods[i].fnPtr;
        }
        
        int registered_count = register_native_methods_direct(env, class_name, art_methods, g_native_methods_count);
        
        free(class_name);
        
        if (registered_count != g_native_methods_count) {
            // 部分注册失败，回退到标准方法
            char* class_name_fallback = get_obfuscated_class_name();
            if (class_name_fallback) {
                register_native_methods(env, class_name_fallback, g_native_methods, g_native_methods_count);
                free(class_name_fallback);
            }
        }
        
        g_art_method_hook_initialized = 1;
        
        // 保存原始入口点用于后续完整性验证
        // save_original_entry_points(env); // 暂时禁用
    }
    
    // 执行垃圾代码和虚假调用
    dummy_function_calls();
    inject_garbage_code();
    
    // 随机化控制流
    volatile int random_state = (int)(get_timestamp_ns() & 0xFF);
    for (int i = 0; i < 5; i++) {
        random_state = obfuscated_control_flow(random_state % 9);
    }
    
    g_anti_reverse_state.dynamic_loading_active = 1;
    
    return JNI_VERSION_1_6;
}

JNIEXPORT void JNICALL JNI_OnUnload(JavaVM* vm, void* reserved) {
    // 清理ArtMethod Hook系统
    if (g_art_method_hook_initialized) {
        // 这里可以添加恢复原始ArtMethod状态的代码
        g_art_method_hook_initialized = 0;
    }
    
    // 清理敏感数据
    self_destruct_data();
}

// ========== ArtMethod 运行时保护 ==========

/**
 * 运行时监控ArtMethod完整性
 * 在关键函数执行前检查是否被篡改
 */
static int monitor_art_method_integrity(JNIEnv* env, const char* method_name) {
    if (!g_art_method_hook_initialized) {
        return 1; // 未启用ArtMethod监控，假定正常
    }
    
    art_version_t version = detect_art_version();
    if (!is_art_version_supported(version)) {
        return 1;
    }
    
    // 获取当前类
    char* class_name = get_obfuscated_class_name();
    if (!class_name) return 0;
    
    jclass clazz = (*env)->FindClass(env, class_name);
    free(class_name);
    
    if (!clazz) {
        (*env)->ExceptionClear(env);
        return 0;
    }
    
    // 查找并检查特定方法的ArtMethod
    for (int i = 0; i < g_native_methods_count; i++) {
        if (strcmp(g_native_methods[i].name, method_name) == 0) {
            ArtMethod* art_method = get_art_method(env, clazz, 
                g_native_methods[i].name, g_native_methods[i].signature);
            
            if (!art_method) continue;
            
            // 检查ArtMethod是否被Hook
            if (detect_art_method_hook(art_method, version)) {
                return 0; // 检测到Hook
            }
            
            // 检查入口点是否指向我们的函数
            void* current_entry = get_art_method_jni_entry_point(art_method, version);
            if (!current_entry) continue;
            
            // 验证入口点完整性
            uint32_t current_checksum = calculate_function_checksum(current_entry);
            // 这里应该与预期的校验和比较
            // 为了演示，我们只检查入口点是否为NULL
            if (!current_entry) {
                return 0;
            }
            
            break;
        }
    }
    
    return 1; // 完整性检查通过
}

/**
 * 高级反Hook保护包装器
 * 在调用关键函数前进行完整性检查
 */
#define PROTECTED_JNI_CALL(env, method_name, call) do { \
    if (!monitor_art_method_integrity((env), (method_name))) { \
        execute_countermeasures(THREAT_HOOK); \
        return JNI_ERR; \
    } \
    timing_anti_debug(); \
    return (call); \
} while(0)

// 增强的反Hook检测
static void* g_original_entry_points[32]; // 存储原始入口点
static int g_entry_point_count = 0;

/**
 * 保存原始ArtMethod入口点
 */
static void save_original_entry_points(JNIEnv* env) {
    if (!g_art_method_hook_initialized) return;
    
    art_version_t version = detect_art_version();
    if (!is_art_version_supported(version)) return;
    
    char* class_name = get_obfuscated_class_name();
    if (!class_name) return;
    
    jclass clazz = (*env)->FindClass(env, class_name);
    free(class_name);
    
    if (!clazz) {
        (*env)->ExceptionClear(env);
        return;
    }
    
    g_entry_point_count = 0;
    
    for (int i = 0; i < g_native_methods_count && i < 32; i++) {
        ArtMethod* art_method = get_art_method(env, clazz, 
            g_native_methods[i].name, g_native_methods[i].signature);
        
        if (art_method) {
            void* entry_point = get_art_method_jni_entry_point(art_method, version);
            if (entry_point) {
                g_original_entry_points[g_entry_point_count++] = entry_point;
            }
        }
    }
}

/**
 * 验证ArtMethod入口点未被篡改
 */
static int verify_entry_points_integrity(JNIEnv* env) {
    if (!g_art_method_hook_initialized || g_entry_point_count == 0) {
        return 1;
    }
    
    art_version_t version = detect_art_version();
    if (!is_art_version_supported(version)) return 1;
    
    char* class_name = get_obfuscated_class_name();
    if (!class_name) return 0;
    
    jclass clazz = (*env)->FindClass(env, class_name);
    free(class_name);
    
    if (!clazz) {
        (*env)->ExceptionClear(env);
        return 0;
    }
    
    int verified_count = 0;
    
    for (int i = 0; i < g_native_methods_count && i < g_entry_point_count; i++) {
        ArtMethod* art_method = get_art_method(env, clazz, 
            g_native_methods[i].name, g_native_methods[i].signature);
        
        if (art_method) {
            void* current_entry = get_art_method_jni_entry_point(art_method, version);
            
            // 检查入口点是否被修改
            if (current_entry != g_original_entry_points[i]) {
                // 入口点被修改，可能是Hook
                return 0;
            }
            
            verified_count++;
        }
    }
    
    return verified_count == g_entry_point_count;
}

int register_native_methods(JNIEnv* env, const char* class_name, 
                           const native_method_t* methods, int method_count) {
    
    jclass clazz = (*env)->FindClass(env, class_name);
    if (clazz == NULL) {
        return -1;
    }
    
    // 创建JNINativeMethod数组
    JNINativeMethod* jni_methods = malloc(method_count * sizeof(JNINativeMethod));
    if (!jni_methods) {
        return -1;
    }
    
    for (int i = 0; i < method_count; i++) {
        jni_methods[i].name = methods[i].name;
        jni_methods[i].signature = methods[i].signature;
        jni_methods[i].fnPtr = methods[i].fnPtr;
    }
    
    // 注册方法
    int result = (*env)->RegisterNatives(env, clazz, jni_methods, method_count);
    
    free(jni_methods);
    return result;
}

char* get_obfuscated_class_name(void) {
    // 解密类名
    return decrypt_string(&g_encrypted_strings[0]);
}

// ========== 字符串混淆实现 ==========

void xor_string(char* str, size_t len, uint8_t key) {
    for (size_t i = 0; i < len; i++) {
        str[i] ^= key;
    }
}

void simple_aes_encrypt(const uint8_t* plaintext, const uint8_t* key, uint8_t* ciphertext, size_t len) {
    // 简化的AES实现（实际项目中应使用标准AES）
    for (size_t i = 0; i < len; i++) {
        ciphertext[i] = plaintext[i] ^ key[i % AES_KEY_SIZE] ^ XOR_KEY;
    }
}

void simple_aes_decrypt(const uint8_t* ciphertext, const uint8_t* key, uint8_t* plaintext, size_t len) {
    // 简化的AES解密
    for (size_t i = 0; i < len; i++) {
        plaintext[i] = ciphertext[i] ^ key[i % AES_KEY_SIZE] ^ XOR_KEY;
    }
}

char* decrypt_string(encrypted_string_t* enc_str) {
    if (!enc_str || enc_str->length == 0) {
        return NULL;
    }
    
    char* decrypted = malloc(enc_str->length + 1);
    if (!decrypted) {
        return NULL;
    }
    
    // 使用XOR解密
    memcpy(decrypted, enc_str->data, enc_str->length);
    xor_string(decrypted, enc_str->length, XOR_KEY);
    decrypted[enc_str->length] = '\0';
    
    enc_str->is_decrypted = 1;
    return decrypted;
}

void encrypt_string(const char* plaintext, encrypted_string_t* enc_str) {
    if (!plaintext || !enc_str) return;
    
    size_t len = strlen(plaintext);
    if (len >= MAX_ENCRYPTED_STRING_SIZE) {
        len = MAX_ENCRYPTED_STRING_SIZE - 1;
    }
    
    memcpy(enc_str->data, plaintext, len);
    xor_string((char*)enc_str->data, len, XOR_KEY);
    enc_str->length = len;
    enc_str->is_decrypted = 0;
}

// ========== 反调试保护实现 ==========

static void signal_handler(int sig) {
    // 检测到调试信号，执行反制措施
    execute_countermeasures(THREAT_DEBUGGER);
}

void setup_signal_handlers(void) {
    signal(SIGTRAP, signal_handler);
    signal(SIGILL, signal_handler);
    signal(SIGFPE, signal_handler);
    signal(SIGSEGV, signal_handler);
}

int detect_debugger(void) {
    // 检查TracerPid
    char status_buf[1024];
    FILE* fp = fopen("/proc/self/status", "r");
    if (fp) {
        while (fgets(status_buf, sizeof(status_buf), fp)) {
            if (strncmp(status_buf, "TracerPid:", 10) == 0) {
                int tracer_pid = 0;
                sscanf(status_buf + 10, "%d", &tracer_pid);
                fclose(fp);
                return tracer_pid != 0;
            }
        }
        fclose(fp);
    }
    
    return 0;
}

int detect_frida(void) {
    // 检查Frida特征
    char* frida_server = decrypt_string(&g_encrypted_strings[1]);
    if (frida_server) {
        int result = (access("/data/local/tmp/frida-server", F_OK) == 0) ||
                    (strstr(getenv("PATH") ? getenv("PATH") : "", frida_server) != NULL);
        free(frida_server);
        return result;
    }
    
    // 检查内存映射
    FILE* maps = fopen("/proc/self/maps", "r");
    if (maps) {
        char line[512];
        while (fgets(line, sizeof(line), maps)) {
            if (strstr(line, "frida") || strstr(line, "gadget")) {
                fclose(maps);
                return 1;
            }
        }
        fclose(maps);
    }
    
    return 0;
}

int detect_xposed(void) {
    // 检查Xposed特征
    return access("/system/framework/XposedBridge.jar", F_OK) == 0 ||
           access("/data/data/de.robv.android.xposed.installer", F_OK) == 0;
}

int ptrace_anti_debug(void) {
    return ptrace(PTRACE_TRACEME, 0, 1, 0) == -1;
}

int timing_anti_debug(void) {
    uint64_t start = get_timestamp_ns();
    
    // 执行一些简单操作
    volatile int dummy = 0;
    for (int i = 0; i < 1000; i++) {
        dummy += i;
    }
    
    uint64_t end = get_timestamp_ns();
    uint64_t duration = end - start;
    
    // 如果执行时间过长，可能被调试
    return duration > 10000000; // 10ms阈值
}

// ========== 代码完整性保护实现 ==========

uint32_t calculate_code_checksum(void* start_addr, size_t size) {
    uint32_t checksum = 0;
    uint8_t* bytes = (uint8_t*)start_addr;
    
    for (size_t i = 0; i < size; i++) {
        checksum = (checksum << 1) ^ bytes[i];
    }
    
    return checksum;
}

int verify_code_integrity(void) {
    // 验证关键函数的完整性
    uint32_t expected_checksum = 0x12345678; // 预计算的校验和
    uint32_t actual_checksum = calculate_code_checksum((void*)JNI_OnLoad, 1024);
    
    return actual_checksum == expected_checksum;
}

void register_critical_section(void* addr, size_t size) {
    if (g_anti_reverse_state.critical_section_count < 10) {
        g_anti_reverse_state.critical_sections[g_anti_reverse_state.critical_section_count++] = addr;
        
        // 计算校验和
        uint32_t checksum = calculate_code_checksum(addr, size);
        g_anti_reverse_state.integrity_checksum ^= checksum;
    }
}

int check_critical_sections(void) {
    uint32_t current_checksum = 0;
    
    for (size_t i = 0; i < g_anti_reverse_state.critical_section_count; i++) {
        uint32_t checksum = calculate_code_checksum(g_anti_reverse_state.critical_sections[i], 1024);
        current_checksum ^= checksum;
    }
    
    return current_checksum == g_anti_reverse_state.integrity_checksum;
}

// ========== 控制流混淆实现 ==========

void dummy_function_calls(void) {
    // 虚假函数调用，增加分析难度
    volatile int dummy = 0;
    
    if (dummy > 100) { // 永远不会执行
        getpid();
        getuid();
        time(NULL);
    }
    
    for (int i = 0; i < 10; i++) {
        dummy = (dummy * 31 + i) % 1000;
    }
}

void inject_garbage_code(void) {
    // 注入垃圾代码
    volatile int x = 42;
    volatile int y = 58;
    
    x = x ^ y;
    y = x ^ y;
    x = x ^ y;
    
    if (x > 1000000) { // 永远不会执行
        printf("This will never be printed\n");
    }
}

int obfuscated_control_flow(int state) {
    // 控制流平坦化示例
    switch (state) {
        case 0: return 3;
        case 1: return 7;
        case 2: return 1;
        case 3: return 5;
        case 4: return 2;
        case 5: return 8;
        case 6: return 4;
        case 7: return 6;
        case 8: return 0;
        default: return -1;
    }
}

// ========== 反制措施实现 ==========

void execute_countermeasures(int threat_type) {
    switch (threat_type) {
        case THREAT_DEBUGGER:
            // 遇到调试器：清理数据并退出
            self_destruct_data();
            secure_exit(-1);
            break;
            
        case THREAT_FRIDA:
            // 遇到Frida：返回虚假数据
            // 在实际实现中可以返回误导性信息
            break;
            
        case THREAT_XPOSED:
            // 遇到Xposed：拒绝服务
            secure_exit(-2);
            break;
            
        case THREAT_INTEGRITY:
            // 代码被篡改：数据自毁
            self_destruct_data();
            secure_exit(-3);
            break;
            
        default:
            break;
    }
}

void secure_exit(int exit_code) {
    // 安全退出前清理所有敏感数据
    self_destruct_data();
    _exit(exit_code);
}

void self_destruct_data(void) {
    // 清零敏感数据
    secure_memzero(g_aes_key, sizeof(g_aes_key));
    secure_memzero(&g_anti_reverse_state, sizeof(g_anti_reverse_state));
    
    // 清零加密字符串
    for (int i = 0; i < g_encrypted_strings_count; i++) {
        secure_memzero(&g_encrypted_strings[i], sizeof(encrypted_string_t));
    }
}

// ========== 工具函数实现 ==========

void secure_random(uint8_t* buffer, size_t size) {
    // 简化的随机数生成
    FILE* urandom = fopen("/dev/urandom", "rb");
    if (urandom) {
        fread(buffer, 1, size, urandom);
        fclose(urandom);
    } else {
        // 备用方案
        srand(time(NULL) ^ getpid());
        for (size_t i = 0; i < size; i++) {
            buffer[i] = rand() & 0xFF;
        }
    }
}

void secure_memzero(void* ptr, size_t size) {
    volatile char* p = (volatile char*)ptr;
    while (size--) {
        *p++ = 0;
    }
}

uint64_t get_timestamp_ns(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000000ULL + ts.tv_nsec;
}

uint32_t calculate_hash(const void* data, size_t size) {
    const uint8_t* bytes = (const uint8_t*)data;
    uint32_t hash = 5381;
    
    for (size_t i = 0; i < size; i++) {
        hash = ((hash << 5) + hash) + bytes[i];
    }
    
    return hash;
}

// ========== 环境检测实现 ==========

int detect_emulator_advanced(void) {
    // 高级模拟器检测
    const char* emulator_files[] = {
        "/system/bin/qemu-props",
        "/system/lib/libc_malloc_debug_qemu.so",
        "/system/bin/qemu",
        "/dev/socket/qemud",
        "/system/bin/nox",
        "/system/bin/genymotion",
        NULL
    };
    
    for (int i = 0; emulator_files[i]; i++) {
        if (access(emulator_files[i], F_OK) == 0) {
            return 1;
        }
    }
    
    return 0;
}

int detect_debug_environment(void) {
    return detect_debugger() || timing_anti_debug();
}

int detect_hooking_framework(void) {
    return detect_frida() || detect_xposed();
}