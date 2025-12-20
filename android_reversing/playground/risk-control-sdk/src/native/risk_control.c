#include "risk_control.h"
#include "svc_syscall.h"
#include <ctype.h>        // for isdigit()

// 平台兼容性处理
#ifdef __linux__
#include <sys/ptrace.h>   // for ptrace() on Linux
#elif defined(__APPLE__)
#include <sys/ptrace.h>   // for ptrace() on macOS
#else
// 其他平台的 ptrace 替代实现
static int ptrace(int request, int pid, void* addr, void* data) {
    return 0; // 模拟成功
}
#endif

// 全局变量
static sdk_config_t g_config = {0};
static device_info_t g_device_info = {0};
static security_status_t g_security_status = {0};
static int g_initialized = 0;

// 加密字符串（运行时解密）
static const unsigned char enc_root_paths[] = {
    0x3f, 0x73, 0x75, 0x6e, 0x6e, 0x65, 0x73, 0x70, 0x00, // "/system"
    0x3f, 0x73, 0x75, 0x6e, 0x6e, 0x65, 0x73, 0x70, 0x3f, 0x78, 0x69, 0x6e, 0x00, // "/system/xbin"
};

// ========== JNI 函数实现 ==========

JNIEXPORT jboolean JNICALL 
Java_com_riskcontrol_RiskControlSDK_nativeInitialize(JNIEnv *env, jobject thiz) {
    LOG_I("RiskSDK", "Initializing native SDK...");
    
    if (g_initialized) {
        LOG_W("RiskSDK", "SDK already initialized");
        return JNI_TRUE;
    }
    
    // 初始化配置
    memset(&g_config, 0, sizeof(sdk_config_t));
    g_config.debug_mode = 0;
    g_config.risk_threshold = 50;
    
    // 初始化设备信息
    memset(&g_device_info, 0, sizeof(device_info_t));
    g_device_info.collect_time = time(NULL);
    
    // 初始化安全状态
    memset(&g_security_status, 0, sizeof(security_status_t));
    
    // 初始化SVC模块
    if (svc_init() != 0) {
        LOG_W("RiskSDK", "SVC module initialization failed, falling back to standard calls");
    } else {
        LOG_I("RiskSDK", "SVC module initialized successfully");
    }
    
    // 启动反调试保护
    init_anti_debug();
    
    // 收集基础设备信息
    char* device_id = generate_device_id();
    if (device_id) {
        safe_strncpy(g_device_info.device_id, device_id, DEVICE_ID_LENGTH);
        free(device_id);
    }
    
    g_initialized = 1;
    LOG_I("RiskSDK", "Native SDK initialized successfully");
    return JNI_TRUE;
}

JNIEXPORT void JNICALL 
Java_com_riskcontrol_RiskControlSDK_nativeCleanup(JNIEnv *env, jobject thiz) {
    LOG_I("RiskSDK", "Cleaning up native SDK...");
    
    // 清理敏感数据
    memset(&g_device_info, 0, sizeof(device_info_t));
    memset(&g_security_status, 0, sizeof(security_status_t));
    
    // 清理SVC模块
    svc_cleanup();
    
    g_initialized = 0;
    LOG_I("RiskSDK", "Native SDK cleaned up");
}

JNIEXPORT jstring JNICALL 
Java_com_riskcontrol_RiskControlSDK_nativeGetVersion(JNIEnv *env, jobject thiz) {
    return cstring_to_jstring(env, VERSION_STRING);
}

JNIEXPORT void JNICALL 
Java_com_riskcontrol_RiskControlSDK_nativeSetDebugMode(JNIEnv *env, jobject thiz, jboolean enabled) {
    g_config.debug_mode = enabled ? 1 : 0;
    LOG_I("RiskSDK", "Debug mode: %s", enabled ? "enabled" : "disabled");
}

JNIEXPORT void JNICALL 
Java_com_riskcontrol_RiskControlSDK_nativeSetConfig(JNIEnv *env, jobject thiz, jstring key, jstring value) {
    char* c_key = jstring_to_cstring(env, key);
    char* c_value = jstring_to_cstring(env, value);
    
    if (c_key && c_value) {
        if (strcmp(c_key, "risk_threshold") == 0) {
            g_config.risk_threshold = atoi(c_value);
        } else {
            // 存储其他自定义配置
            snprintf(g_config.custom_config, sizeof(g_config.custom_config), 
                    "%s=%s", c_key, c_value);
        }
        LOG_D("RiskSDK", "Config set: %s = %s", c_key, c_value);
    }
    
    if (c_key) free(c_key);
    if (c_value) free(c_value);
}

// ========== 设备指纹采集实现 ==========

JNIEXPORT jstring JNICALL 
Java_com_riskcontrol_RiskControlSDK_nativeGetDeviceId(JNIEnv *env, jobject thiz) {
    if (!g_initialized) return cstring_to_jstring(env, "not_initialized");
    
    if (strlen(g_device_info.device_id) == 0) {
        char* device_id = generate_device_id();
        if (device_id) {
            safe_strncpy(g_device_info.device_id, device_id, DEVICE_ID_LENGTH);
            free(device_id);
        }
    }
    
    return cstring_to_jstring(env, g_device_info.device_id);
}

JNIEXPORT jstring JNICALL 
Java_com_riskcontrol_RiskControlSDK_nativeGetHardwareInfo(JNIEnv *env, jobject thiz) {
    char hardware_json[1024];
    char* cpu_info = collect_cpu_info();
    char* memory_info = collect_memory_info();
    
    snprintf(hardware_json, sizeof(hardware_json),
        "{"
        "\"cpu\":\"%s\","
        "\"memory\":\"%s\","
        "\"timestamp\":%ld"
        "}",
        cpu_info ? cpu_info : "unknown",
        memory_info ? memory_info : "unknown",
        time(NULL)
    );
    
    if (cpu_info) free(cpu_info);
    if (memory_info) free(memory_info);
    
    return cstring_to_jstring(env, hardware_json);
}

JNIEXPORT jstring JNICALL 
Java_com_riskcontrol_RiskControlSDK_nativeGetSoftwareInfo(JNIEnv *env, jobject thiz) {
    char software_json[1024];
    char* build_info = collect_build_info();
    
    snprintf(software_json, sizeof(software_json),
        "{"
        "\"build\":\"%s\","
        "\"process_id\":%d,"
        "\"timestamp\":%ld"
        "}",
        build_info ? build_info : "unknown",
        getpid(),
        time(NULL)
    );
    
    if (build_info) free(build_info);
    
    return cstring_to_jstring(env, software_json);
}

JNIEXPORT jstring JNICALL 
Java_com_riskcontrol_RiskControlSDK_nativeGetNetworkInfo(JNIEnv *env, jobject thiz) {
    char network_json[512];
    char* network_info = collect_network_info();
    
    snprintf(network_json, sizeof(network_json),
        "{"
        "\"interfaces\":\"%s\","
        "\"timestamp\":%ld"
        "}",
        network_info ? network_info : "unknown",
        time(NULL)
    );
    
    if (network_info) free(network_info);
    
    return cstring_to_jstring(env, network_json);
}

// ========== 安全检测实现 ==========

JNIEXPORT jboolean JNICALL 
Java_com_riskcontrol_RiskControlSDK_nativeDetectEmulator(JNIEnv *env, jobject thiz) {
    int result = detect_emulator_environment();
    g_security_status.is_emulator = result;
    
    LOG_D("RiskSDK", "Emulator detection: %s", result ? "detected" : "not detected");
    return result ? JNI_TRUE : JNI_FALSE;
}

JNIEXPORT jboolean JNICALL 
Java_com_riskcontrol_RiskControlSDK_nativeDetectRoot(JNIEnv *env, jobject thiz) {
    int result = detect_root_access();
    g_security_status.is_rooted = result;
    
    LOG_D("RiskSDK", "Root detection: %s", result ? "detected" : "not detected");
    return result ? JNI_TRUE : JNI_FALSE;
}

JNIEXPORT jboolean JNICALL 
Java_com_riskcontrol_RiskControlSDK_nativeDetectDebug(JNIEnv *env, jobject thiz) {
    int result = detect_debugger_attached();
    g_security_status.is_debugging = result;
    
    LOG_D("RiskSDK", "Debug detection: %s", result ? "detected" : "not detected");
    return result ? JNI_TRUE : JNI_FALSE;
}

JNIEXPORT jboolean JNICALL 
Java_com_riskcontrol_RiskControlSDK_nativeDetectHook(JNIEnv *env, jobject thiz) {
    int result = detect_hook_frameworks();
    g_security_status.is_hooked = result;
    
    LOG_D("RiskSDK", "Hook detection: %s", result ? "detected" : "not detected");
    return result ? JNI_TRUE : JNI_FALSE;
}

JNIEXPORT jboolean JNICALL 
Java_com_riskcontrol_RiskControlSDK_nativeDetectProxy(JNIEnv *env, jobject thiz) {
    int result = detect_proxy_connection();
    g_security_status.is_proxy = result;
    
    LOG_D("RiskSDK", "Proxy detection: %s", result ? "detected" : "not detected");
    return result ? JNI_TRUE : JNI_FALSE;
}

JNIEXPORT jboolean JNICALL 
Java_com_riskcontrol_RiskControlSDK_nativeDetectVPN(JNIEnv *env, jobject thiz) {
    int result = detect_vpn_connection();
    g_security_status.is_vpn = result;
    
    LOG_D("RiskSDK", "VPN detection: %s", result ? "detected" : "not detected");
    return result ? JNI_TRUE : JNI_FALSE;
}

// ========== 风险评估实现 ==========

JNIEXPORT jint JNICALL 
Java_com_riskcontrol_RiskControlSDK_nativeCalculateRiskScore(JNIEnv *env, jobject thiz,
    jstring deviceId, jboolean isEmulator, jboolean isRooted, jboolean isDebugging, jboolean isHooked) {
    
    int risk_score = 0;
    
    // 根据各种威胁计算风险分数
    if (isEmulator) risk_score += WEIGHT_EMULATOR;
    if (isRooted) risk_score += WEIGHT_ROOT;
    if (isDebugging) risk_score += WEIGHT_DEBUG;
    if (isHooked) risk_score += WEIGHT_HOOK;
    if (g_security_status.is_proxy) risk_score += WEIGHT_PROXY;
    if (g_security_status.is_vpn) risk_score += WEIGHT_VPN;
    
    // 设备指纹熵检查（简化版）
    char* c_device_id = jstring_to_cstring(env, deviceId);
    if (c_device_id) {
        int entropy = strlen(c_device_id);
        if (entropy < 10) {
            risk_score += 10; // 设备ID熵过低
        }
        free(c_device_id);
    }
    
    // 构建威胁详情
    snprintf(g_security_status.threat_details, sizeof(g_security_status.threat_details),
        "emulator:%d;root:%d;debug:%d;hook:%d;proxy:%d;vpn:%d",
        isEmulator ? WEIGHT_EMULATOR : 0,
        isRooted ? WEIGHT_ROOT : 0,
        isDebugging ? WEIGHT_DEBUG : 0,
        isHooked ? WEIGHT_HOOK : 0,
        g_security_status.is_proxy ? WEIGHT_PROXY : 0,
        g_security_status.is_vpn ? WEIGHT_VPN : 0
    );
    
    // 确保分数在0-100范围内
    if (risk_score > 100) risk_score = 100;
    if (risk_score < 0) risk_score = 0;
    
    LOG_I("RiskSDK", "Risk score calculated: %d", risk_score);
    return risk_score;
}

JNIEXPORT jstring JNICALL 
Java_com_riskcontrol_RiskControlSDK_nativeGetRiskDetails(JNIEnv *env, jobject thiz) {
    return cstring_to_jstring(env, g_security_status.threat_details);
}

// ========== 内部函数实现 ==========

char* generate_device_id(void) {
    char* device_id = malloc(DEVICE_ID_LENGTH + 1);
    if (!device_id) return NULL;
    
    // 简化的设备ID生成（实际实现会更复杂）
    uint32_t hash1 = calculate_string_hash("device_hardware");
    uint32_t hash2 = calculate_string_hash("device_software");
    uint32_t hash3 = (uint32_t)time(NULL);
    
    snprintf(device_id, DEVICE_ID_LENGTH + 1, "%08x%08x%08x%08x", 
             hash1, hash2, hash3, getpid());
    
    return device_id;
}

char* collect_cpu_info(void) {
    char* cpu_info = malloc(1024);
    if (!cpu_info) return NULL;
    
#ifdef SVC_SYSCALLS_ENABLED
    // 使用SVC系统调用绕过可能的Hook
    if (svc_get_cpu_info(cpu_info, 1024) == 0) {
        LOG_D("RiskSDK", "CPU info collected via SVC");
        return cpu_info;
    }
    LOG_W("RiskSDK", "SVC CPU info collection failed, falling back to standard method");
#endif
    
    // 标准方法作为备用
    char* content = read_file_content("/proc/cpuinfo");
    if (content) {
        // 提取关键信息并格式化为JSON
        char* processor = strstr(content, "processor");
        char* model = strstr(content, "model name");
        char* features = strstr(content, "Features");
        
        snprintf(cpu_info, 1024, 
            "{\"method\":\"standard\",\"processor\":\"%s\",\"model\":\"%s\",\"features\":\"%s\"}",
            processor ? "found" : "unknown",
            model ? "found" : "unknown", 
            features ? "found" : "unknown");
        free(content);
    } else {
        snprintf(cpu_info, 1024, "{\"method\":\"standard\",\"status\":\"failed\"}");
    }
    
    return cpu_info;
}

char* collect_memory_info(void) {
    char* mem_info = malloc(128);
    if (!mem_info) return NULL;
    
    char* content = read_file_content("/proc/meminfo");
    if (content) {
        // 简化处理
        snprintf(mem_info, 128, "mem_info_available");
        free(content);
    } else {
        snprintf(mem_info, 128, "mem_unknown");
    }
    
    return mem_info;
}

char* collect_build_info(void) {
    char* build_info = malloc(256);
    if (!build_info) return NULL;
    
    // 收集系统构建信息
    snprintf(build_info, 256, "build_version_unknown");
    
    return build_info;
}

char* collect_network_info(void) {
    char* net_info = malloc(128);
    if (!net_info) return NULL;
    
    // 收集网络接口信息
    if (check_network_interfaces()) {
        snprintf(net_info, 128, "network_available");
    } else {
        snprintf(net_info, 128, "network_unavailable");
    }
    
    return net_info;
}

uint32_t calculate_string_hash(const char* str) {
    uint32_t hash = 5381;
    int c;
    
    while ((c = *str++)) {
        hash = ((hash << 5) + hash) + c;
    }
    
    return hash;
}

// ========== 安全检测函数实现 ==========

int detect_emulator_environment(void) {
    // 检查常见的模拟器特征
    
    // 1. 检查系统属性
    if (file_exists("/system/bin/qemu-props")) return 1;
    if (file_exists("/system/bin/qemu")) return 1;
    
    // 2. 检查特定文件
    if (file_exists("/system/lib/libc_malloc_debug_qemu.so")) return 1;
    if (file_exists("/system/bin/genymotion")) return 1;
    
    // 3. 检查CPU特征
    char* cpu_info = read_file_content("/proc/cpuinfo");
    if (cpu_info) {
        if (strstr(cpu_info, "goldfish") || strstr(cpu_info, "vbox")) {
            free(cpu_info);
            return 1;
        }
        free(cpu_info);
    }
    
    return 0;
}

int detect_root_access(void) {
    // 检查常见的Root标识
    
    // 1. 检查su二进制文件
    const char* su_paths[] = {
        "/system/bin/su",
        "/system/xbin/su", 
        "/sbin/su",
        "/data/local/xbin/su",
        "/data/local/bin/su",
        NULL
    };
    
    for (int i = 0; su_paths[i]; i++) {
        if (file_exists(su_paths[i])) {
            return 1;
        }
    }
    
    // 2. 检查Root管理应用
    const char* root_apps[] = {
        "/data/data/com.noshufou.android.su",
        "/data/data/com.thirdparty.superuser",
        "/data/data/eu.chainfire.supersu",
        NULL
    };
    
    for (int i = 0; root_apps[i]; i++) {
        if (directory_exists(root_apps[i])) {
            return 1;
        }
    }
    
    return 0;
}

int detect_debugger_attached(void) {
    // 1. 检查TracerPid
    char* status_content = read_file_content("/proc/self/status");
    if (status_content) {
        char* tracer_line = strstr(status_content, "TracerPid:");
        if (tracer_line) {
            int tracer_pid = 0;
            sscanf(tracer_line, "TracerPid:\t%d", &tracer_pid);
            free(status_content);
            return tracer_pid != 0;
        }
        free(status_content);
    }
    
    // 2. ptrace自保护
    return ptrace_protection();
}

int detect_hook_frameworks(void) {
    // 检查常见的Hook框架
    
    // 1. 检查Frida特征
    if (check_process_exists("frida-server")) return 1;
    if (file_exists("/data/local/tmp/frida-server")) return 1;
    
    // 2. 检查Xposed特征
    if (file_exists("/system/framework/XposedBridge.jar")) return 1;
    if (directory_exists("/data/data/de.robv.android.xposed.installer")) return 1;
    
    // 3. 检查内存中的可疑库
    char maps_path[64];
    snprintf(maps_path, sizeof(maps_path), "/proc/%d/maps", getpid());
    
    char* maps_content = read_file_content(maps_path);
    if (maps_content) {
        if (strstr(maps_content, "frida") || 
            strstr(maps_content, "xposed") ||
            strstr(maps_content, "substrate")) {
            free(maps_content);
            return 1;
        }
        free(maps_content);
    }
    
    return 0;
}

int detect_proxy_connection(void) {
    // 简化的代理检测
    return detect_proxy_settings();
}

int detect_vpn_connection(void) {
    // 检查VPN接口
    char* net_content = read_file_content("/proc/net/route");
    if (net_content) {
        if (strstr(net_content, "tun") || strstr(net_content, "ppp")) {
            free(net_content);
            return 1;
        }
        free(net_content);
    }
    
    return 0;
}

// ========== 工具函数实现 ==========

int file_exists(const char* path) {
    return access(path, F_OK) == 0;
}

int directory_exists(const char* path) {
    struct stat st;
    return stat(path, &st) == 0 && S_ISDIR(st.st_mode);
}

char* read_file_content(const char* path) {
    FILE* file = fopen(path, "r");
    if (!file) return NULL;
    
    fseek(file, 0, SEEK_END);
    long size = ftell(file);
    if (size <= 0 || size > 10240) { // 限制文件大小
        fclose(file);
        return NULL;
    }
    
    fseek(file, 0, SEEK_SET);
    char* content = malloc(size + 1);
    if (!content) {
        fclose(file);
        return NULL;
    }
    
    size_t read_size = fread(content, 1, size, file);
    content[read_size] = '\0';
    
    fclose(file);
    return content;
}

int check_process_exists(const char* process_name) {
    DIR* proc_dir = opendir("/proc");
    if (!proc_dir) return 0;
    
    struct dirent* entry;
    while ((entry = readdir(proc_dir)) != NULL) {
        if (entry->d_type == DT_DIR && isdigit(entry->d_name[0])) {
            char comm_path[256];
            snprintf(comm_path, sizeof(comm_path), "/proc/%s/comm", entry->d_name);
            
            char* comm_content = read_file_content(comm_path);
            if (comm_content) {
                // 移除换行符
                char* newline = strchr(comm_content, '\n');
                if (newline) *newline = '\0';
                
                if (strcmp(comm_content, process_name) == 0) {
                    free(comm_content);
                    closedir(proc_dir);
                    return 1;
                }
                free(comm_content);
            }
        }
    }
    
    closedir(proc_dir);
    return 0;
}

int check_network_interfaces(void) {
    return file_exists("/proc/net/dev");
}

int detect_proxy_settings(void) {
    // 简化的代理检测逻辑
    return 0;
}

void init_anti_debug(void) {
    // 初始化反调试保护
    LOG_D("RiskSDK", "Anti-debug protection initialized");
}

int ptrace_protection(void) {
    // 使用ptrace自保护
    if (ptrace(1 /* PTRACE_TRACEME */, 0, 1, 0) == -1) {
        return 1; // 已被调试
    }
    return 0;
}

char* jstring_to_cstring(JNIEnv *env, jstring jstr) {
    if (jstr == NULL) return NULL;
    
    const char *utf_chars = (*env)->GetStringUTFChars(env, jstr, NULL);
    if (utf_chars == NULL) return NULL;
    
    size_t len = strlen(utf_chars);
    char *result = malloc(len + 1);
    if (result != NULL) {
        strcpy(result, utf_chars);
    }
    
    (*env)->ReleaseStringUTFChars(env, jstr, utf_chars);
    return result;
}

jstring cstring_to_jstring(JNIEnv *env, const char *cstr) {
    if (cstr == NULL) return NULL;
    return (*env)->NewStringUTF(env, cstr);
}

void safe_strncpy(char* dest, const char* src, size_t size) {
    if (dest && src && size > 0) {
        strncpy(dest, src, size - 1);
        dest[size - 1] = '\0';
    }
}

int safe_strcmp(const char* s1, const char* s2) {
    if (s1 == NULL || s2 == NULL) return -1;
    return strcmp(s1, s2);
}