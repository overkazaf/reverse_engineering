#ifndef RISK_CONTROL_H
#define RISK_CONTROL_H

#include <jni.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <dirent.h>
#include <time.h>
#include <stdint.h>  // 添加标准整数类型支持

// 调试宏定义
#ifdef DEBUG
#define LOG_D(tag, fmt, ...) printf("[DEBUG][%s] " fmt "\n", tag, ##__VA_ARGS__)
#else
#define LOG_D(tag, fmt, ...) do {} while(0)
#endif

#define LOG_I(tag, fmt, ...) printf("[INFO][%s] " fmt "\n", tag, ##__VA_ARGS__)
#define LOG_W(tag, fmt, ...) printf("[WARN][%s] " fmt "\n", tag, ##__VA_ARGS__)
#define LOG_E(tag, fmt, ...) printf("[ERROR][%s] " fmt "\n", tag, ##__VA_ARGS__)

// 常量定义
#define MAX_PATH_LEN 512
#define MAX_BUFFER_SIZE 1024
#define DEVICE_ID_LENGTH 32
#define VERSION_STRING "1.0.0"

// 风险评分权重
#define WEIGHT_EMULATOR 30
#define WEIGHT_ROOT 25
#define WEIGHT_DEBUG 20
#define WEIGHT_HOOK 15
#define WEIGHT_PROXY 10
#define WEIGHT_VPN 5

// 配置结构体
typedef struct {
    int debug_mode;
    int risk_threshold;
    char custom_config[256];
} sdk_config_t;

// 设备信息结构体
typedef struct {
    char device_id[DEVICE_ID_LENGTH + 1];
    char cpu_info[256];
    char memory_info[128];
    char build_info[256];
    char network_info[128];
    time_t collect_time;
} device_info_t;

// 安全状态结构体
typedef struct {
    int is_emulator;
    int is_rooted;  
    int is_debugging;
    int is_hooked;
    int is_proxy;
    int is_vpn;
    char threat_details[512];
} security_status_t;

#ifdef __cplusplus
extern "C" {
#endif

// ==========  JNI 函数声明 ==========

// 初始化和配置
JNIEXPORT jboolean JNICALL Java_com_riskcontrol_RiskControlSDK_nativeInitialize(JNIEnv *env, jobject thiz);
JNIEXPORT void JNICALL Java_com_riskcontrol_RiskControlSDK_nativeCleanup(JNIEnv *env, jobject thiz);
JNIEXPORT jstring JNICALL Java_com_riskcontrol_RiskControlSDK_nativeGetVersion(JNIEnv *env, jobject thiz);
JNIEXPORT void JNICALL Java_com_riskcontrol_RiskControlSDK_nativeSetDebugMode(JNIEnv *env, jobject thiz, jboolean enabled);
JNIEXPORT void JNICALL Java_com_riskcontrol_RiskControlSDK_nativeSetConfig(JNIEnv *env, jobject thiz, jstring key, jstring value);

// 设备指纹采集
JNIEXPORT jstring JNICALL Java_com_riskcontrol_RiskControlSDK_nativeGetDeviceId(JNIEnv *env, jobject thiz);
JNIEXPORT jstring JNICALL Java_com_riskcontrol_RiskControlSDK_nativeGetHardwareInfo(JNIEnv *env, jobject thiz);
JNIEXPORT jstring JNICALL Java_com_riskcontrol_RiskControlSDK_nativeGetSoftwareInfo(JNIEnv *env, jobject thiz);
JNIEXPORT jstring JNICALL Java_com_riskcontrol_RiskControlSDK_nativeGetNetworkInfo(JNIEnv *env, jobject thiz);

// 安全检测
JNIEXPORT jboolean JNICALL Java_com_riskcontrol_RiskControlSDK_nativeDetectEmulator(JNIEnv *env, jobject thiz);
JNIEXPORT jboolean JNICALL Java_com_riskcontrol_RiskControlSDK_nativeDetectRoot(JNIEnv *env, jobject thiz);
JNIEXPORT jboolean JNICALL Java_com_riskcontrol_RiskControlSDK_nativeDetectDebug(JNIEnv *env, jobject thiz);
JNIEXPORT jboolean JNICALL Java_com_riskcontrol_RiskControlSDK_nativeDetectHook(JNIEnv *env, jobject thiz);
JNIEXPORT jboolean JNICALL Java_com_riskcontrol_RiskControlSDK_nativeDetectProxy(JNIEnv *env, jobject thiz);
JNIEXPORT jboolean JNICALL Java_com_riskcontrol_RiskControlSDK_nativeDetectVPN(JNIEnv *env, jobject thiz);

// 风险评估
JNIEXPORT jint JNICALL Java_com_riskcontrol_RiskControlSDK_nativeCalculateRiskScore(JNIEnv *env, jobject thiz, 
    jstring deviceId, jboolean isEmulator, jboolean isRooted, jboolean isDebugging, jboolean isHooked);
JNIEXPORT jstring JNICALL Java_com_riskcontrol_RiskControlSDK_nativeGetRiskDetails(JNIEnv *env, jobject thiz);

// ========== 内部函数声明 ==========

// 设备指纹相关
char* generate_device_id(void);
char* collect_cpu_info(void);
char* collect_memory_info(void);
char* collect_build_info(void);
char* collect_network_info(void);
uint32_t calculate_string_hash(const char* str);

// 安全检测相关
int detect_emulator_environment(void);
int detect_root_access(void);
int detect_debugger_attached(void);
int detect_hook_frameworks(void);
int detect_proxy_connection(void);
int detect_vpn_connection(void);

// 文件系统检查
int file_exists(const char* path);
int directory_exists(const char* path);
char* read_file_content(const char* path);
int check_file_permissions(const char* path);

// 进程检查
int check_process_exists(const char* process_name);
int check_running_processes(void);
int get_process_info(char* buffer, size_t size);

// 网络检查
int check_network_interfaces(void);
int detect_proxy_settings(void);

// 系统属性检查
char* get_system_property(const char* key);
int check_system_properties(void);

// 反调试保护
void init_anti_debug(void);
void check_debug_status(void);
int ptrace_protection(void);

// 字符串混淆和加密
char* decrypt_raw_string(const unsigned char* encrypted, size_t len);
void encrypt_sensitive_data(char* data, size_t len);

// 工具函数
char* jstring_to_cstring(JNIEnv *env, jstring jstr);
jstring cstring_to_jstring(JNIEnv *env, const char *cstr);
void safe_strncpy(char* dest, const char* src, size_t size);
int safe_strcmp(const char* s1, const char* s2);

#ifdef __cplusplus
}
#endif

#endif // RISK_CONTROL_H