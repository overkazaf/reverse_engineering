#ifndef ANTI_REVERSE_H
#define ANTI_REVERSE_H

#include <jni.h>
#include <stdint.h>
#include <stddef.h>
#include "common_types.h"

// 字符串混淆宏定义
#define XOR_KEY 0x5A
#define AES_KEY_SIZE 16
#define MAX_ENCRYPTED_STRING_SIZE 256

// 包含 art_method_hook.h 来获取 native_method_t 定义
// 注意：这里不能重复定义，由 art_method_hook.h 提供

// 加密字符串结构体
typedef struct {
    unsigned char data[MAX_ENCRYPTED_STRING_SIZE];
    size_t length;
    int is_decrypted;
} encrypted_string_t;

// 反逆向检测状态
typedef struct {
    int anti_debug_active;
    int string_obfuscation_active;
    int dynamic_loading_active;
    uint32_t integrity_checksum;
    void* critical_sections[10];
    size_t critical_section_count;
} anti_reverse_state_t;

#ifdef __cplusplus
extern "C" {
#endif

// ========== 字符串混淆相关 ==========

/**
 * 初始化字符串混淆模块
 * 在.init_array中调用
 */
void __attribute__((constructor)) init_string_obfuscation(void);

/**
 * XOR字符串加密/解密
 * @param str 字符串
 * @param len 长度
 * @param key 密钥
 */
void xor_string(char* str, size_t len, uint8_t key);

/**
 * 简单的AES加密（演示用）
 * @param plaintext 明文
 * @param key 密钥
 * @param ciphertext 密文输出
 * @param len 数据长度
 */
void simple_aes_encrypt(const uint8_t* plaintext, const uint8_t* key, uint8_t* ciphertext, size_t len);

/**
 * 简单的AES解密（演示用）
 * @param ciphertext 密文
 * @param key 密钥
 * @param plaintext 明文输出
 * @param len 数据长度
 */
void simple_aes_decrypt(const uint8_t* ciphertext, const uint8_t* key, uint8_t* plaintext, size_t len);

/**
 * 解密字符串
 * @param enc_str 加密字符串结构体
 * @return 解密后的字符串（需要释放）
 */
char* decrypt_string(encrypted_string_t* enc_str);

/**
 * 加密字符串
 * @param plaintext 明文字符串
 * @param enc_str 加密字符串结构体输出
 */
void encrypt_string(const char* plaintext, encrypted_string_t* enc_str);

// ========== 动态注册相关 ==========

/**
 * JNI_OnLoad函数 - 执行动态注册
 * @param vm Java虚拟机指针
 * @param reserved 保留参数
 * @return JNI版本
 */
JNIEXPORT jint JNICALL JNI_OnLoad(JavaVM* vm, void* reserved);

/**
 * JNI_OnUnload函数 - 清理资源
 * @param vm Java虚拟机指针
 * @param reserved 保留参数
 */
JNIEXPORT void JNICALL JNI_OnUnload(JavaVM* vm, void* reserved);

/**
 * 动态注册JNI方法
 * @param env JNI环境指针
 * @param class_name 类名
 * @param methods 方法数组
 * @param method_count 方法数量
 * @return 0成功，否则失败
 */
int register_native_methods(JNIEnv* env, const char* class_name, 
                           const native_method_t* methods, int method_count);

/**
 * 获取混淆后的类名
 * @return 解密后的类名（需要释放）
 */
char* get_obfuscated_class_name(void);

// ========== 反调试保护 ==========

/**
 * 初始化反调试保护
 * 在.init_array中调用
 */
void __attribute__((constructor)) init_anti_debug_protection(void);

/**
 * 检测调试器
 * @return 1检测到调试器，0正常
 */
int detect_debugger(void);

/**
 * 检测Frida
 * @return 1检测到Frida，0正常
 */
int detect_frida(void);

/**
 * 检测Xposed
 * @return 1检测到Xposed，0正常
 */
int detect_xposed(void);

/**
 * ptrace反调试
 * @return 1检测到调试，0正常
 */
int ptrace_anti_debug(void);

/**
 * 信号处理反调试
 */
void setup_signal_handlers(void);

/**
 * 时间检测反调试
 * @return 1检测到调试，0正常
 */
int timing_anti_debug(void);

// ========== 代码完整性保护 ==========

/**
 * 计算代码段校验和
 * @param start_addr 起始地址
 * @param size 大小
 * @return 校验和
 */
uint32_t calculate_code_checksum(void* start_addr, size_t size);

/**
 * 验证代码完整性
 * @return 1完整，0被篡改
 */
int verify_code_integrity(void);

/**
 * 注册关键代码段
 * @param addr 地址
 * @param size 大小
 */
void register_critical_section(void* addr, size_t size);

/**
 * 检查关键代码段完整性
 * @return 1完整，0被篡改
 */
int check_critical_sections(void);

// ========== 内存保护 ==========

/**
 * 内存页面保护
 * @param addr 地址
 * @param size 大小
 * @param prot 保护标志
 */
int protect_memory_region(void* addr, size_t size, int prot);

/**
 * 内存数据加密
 * @param data 数据
 * @param size 大小
 * @param key 密钥
 */
void encrypt_memory_data(void* data, size_t size, const uint8_t* key);

/**
 * 内存数据解密
 * @param data 数据
 * @param size 大小
 * @param key 密钥
 */
void decrypt_memory_data(void* data, size_t size, const uint8_t* key);

// ========== 控制流混淆 ==========

/**
 * 虚假函数调用（增加分析难度）
 */
void dummy_function_calls(void);

/**
 * 垃圾代码注入
 */
void inject_garbage_code(void);

/**
 * 控制流平坦化辅助函数
 * @param state 状态值
 * @return 下一个状态
 */
int obfuscated_control_flow(int state);

// ========== 环境检测 ==========

/**
 * 检测是否在模拟器中运行
 * @return 1是模拟器，0真机
 */
int detect_emulator_advanced(void);

/**
 * 检测调试环境
 * @return 1调试环境，0正常
 */
int detect_debug_environment(void);

/**
 * 检测Hook框架
 * @return 1检测到Hook，0正常
 */
int detect_hooking_framework(void);

// ========== 反制措施 ==========

/**
 * 遇到威胁时的反制措施
 * @param threat_type 威胁类型
 */
void execute_countermeasures(int threat_type);

/**
 * 安全退出
 * @param exit_code 退出码
 */
void secure_exit(int exit_code);

/**
 * 数据自毁
 */
void self_destruct_data(void);

// ========== 工具函数 ==========

/**
 * 安全随机数生成
 * @param buffer 缓冲区
 * @param size 大小
 */
void secure_random(uint8_t* buffer, size_t size);

/**
 * 安全内存清零
 * @param ptr 指针
 * @param size 大小
 */
void secure_memzero(void* ptr, size_t size);

/**
 * 获取当前时间戳（高精度）
 * @return 时间戳
 */
uint64_t get_timestamp_ns(void);

/**
 * 计算哈希值
 * @param data 数据
 * @param size 大小
 * @return 哈希值
 */
uint32_t calculate_hash(const void* data, size_t size);

// 威胁类型枚举
enum threat_type {
    THREAT_DEBUGGER = 1,
    THREAT_FRIDA = 2,
    THREAT_XPOSED = 3,
    THREAT_EMULATOR = 4,
    THREAT_HOOK = 5,
    THREAT_INTEGRITY = 6
};

// 全局变量声明
extern anti_reverse_state_t g_anti_reverse_state;
extern uint8_t g_aes_key[AES_KEY_SIZE];
// g_encrypted_strings 在 anti_reverse.c 中定义为 static

#ifdef __cplusplus
}
#endif

#endif // ANTI_REVERSE_H