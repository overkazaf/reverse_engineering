#ifndef ART_METHOD_HOOK_H
#define ART_METHOD_HOOK_H

#include <jni.h>
#include <stdint.h>
#include <stddef.h>
#include "common_types.h"
#include <sys/mman.h>

// ART虚拟机版本检测
typedef enum {
    ART_VERSION_UNKNOWN = 0,
    ART_VERSION_5_0 = 21,      // Android 5.0 (API 21)
    ART_VERSION_5_1 = 22,      // Android 5.1 (API 22)
    ART_VERSION_6_0 = 23,      // Android 6.0 (API 23)
    ART_VERSION_7_0 = 24,      // Android 7.0 (API 24)
    ART_VERSION_7_1 = 25,      // Android 7.1 (API 25)
    ART_VERSION_8_0 = 26,      // Android 8.0 (API 26)
    ART_VERSION_8_1 = 27,      // Android 8.1 (API 27)
    ART_VERSION_9_0 = 28,      // Android 9.0 (API 28)
    ART_VERSION_10_0 = 29,     // Android 10.0 (API 29)
    ART_VERSION_11_0 = 30,     // Android 11.0 (API 30)
    ART_VERSION_12_0 = 31,     // Android 12.0 (API 31)
    ART_VERSION_13_0 = 33,     // Android 13.0 (API 33)
    ART_VERSION_14_0 = 34      // Android 14.0 (API 34)
} art_version_t;

// ArtMethod结构体定义（根据Android版本变化）
// Android 5.x - 6.x
typedef struct {
    uint32_t declaring_class_;           // GcRoot<mirror::Class>
    uint32_t access_flags_;              // 访问标志
    uint32_t dex_code_item_offset_;      // DEX代码项偏移
    uint32_t dex_method_index_;          // DEX方法索引
    uint16_t method_index_;              // 方法索引
    uint16_t hotness_count_;             // 热点计数
    void* entry_point_from_interpreter_; // 解释器入口点
    void* entry_point_from_jni_;         // JNI入口点
    void* entry_point_from_quick_compiled_code_; // 快速编译代码入口点
} ArtMethod_5_6;

// Android 7.x - 8.x
typedef struct {
    uint32_t declaring_class_;           // GcRoot<mirror::Class>
    uint32_t access_flags_;              // 访问标志
    uint32_t dex_code_item_offset_;      // DEX代码项偏移
    uint32_t dex_method_index_;          // DEX方法索引
    uint16_t method_index_;              // 方法索引
    uint16_t hotness_count_;             // 热点计数
    struct {
        void* entry_point_from_interpreter_;
        void* entry_point_from_jni_;
        void* entry_point_from_quick_compiled_code_;
    } ptr_sized_fields_;
} ArtMethod_7_8;

// Android 9.x+
typedef struct {
    uint32_t declaring_class_;           // GcRoot<mirror::Class>
    uint32_t access_flags_;              // 访问标志
    uint32_t dex_code_item_offset_;      // DEX代码项偏移
    uint32_t dex_method_index_;          // DEX方法索引
    uint16_t method_index_;              // 方法索引
    uint16_t hotness_count_;             // 热点计数
    struct {
        void* data_;                     // 数据指针（可能指向JNI函数）
        void* entry_point_from_quick_compiled_code_;
    } ptr_sized_fields_;
} ArtMethod_9_plus;

// 通用ArtMethod结构体
typedef union {
    ArtMethod_5_6 v5_6;
    ArtMethod_7_8 v7_8;
    ArtMethod_9_plus v9_plus;
} ArtMethod;

// ArtMethod访问标志
#define kAccPublic       0x0001  // class, field, method, ic
#define kAccPrivate      0x0002  // field, method, ic
#define kAccProtected    0x0004  // field, method, ic
#define kAccStatic       0x0008  // field, method, ic
#define kAccFinal        0x0010  // class, field, method, ic
#define kAccNative       0x0100  // method
#define kAccAbstract     0x0400  // class, method, ic
#define kAccSynthetic    0x1000  // class, field, method, ic

// JNI桥接函数类型
typedef void (*JNIBridgeFunc)(JNIEnv* env, jobject obj, ...);

// ArtMethod操作结果
typedef struct {
    int success;
    void* original_entry_point;
    char error_msg[256];
} art_method_result_t;

#ifdef __cplusplus
extern "C" {
#endif

// ========== ART版本检测 ==========

/**
 * 检测当前ART虚拟机版本
 * @return ART版本枚举值
 */
art_version_t detect_art_version(void);

/**
 * 获取ART版本字符串
 * @param version 版本枚举值
 * @return 版本字符串
 */
const char* get_art_version_string(art_version_t version);

/**
 * 检查ART版本兼容性
 * @param version 目标版本
 * @return 1兼容，0不兼容
 */
int is_art_version_supported(art_version_t version);

// ========== ArtMethod查找和操作 ==========

/**
 * 通过反射获取ArtMethod指针
 * @param env JNI环境
 * @param clazz Java类
 * @param method_name 方法名
 * @param signature 方法签名
 * @return ArtMethod指针，失败返回NULL
 */
ArtMethod* get_art_method(JNIEnv* env, jclass clazz, const char* method_name, const char* signature);

/**
 * 通过jmethodID获取ArtMethod指针
 * @param method_id JNI方法ID
 * @return ArtMethod指针
 */
ArtMethod* jmethodid_to_art_method(jmethodID method_id);

/**
 * 验证ArtMethod指针有效性
 * @param art_method ArtMethod指针
 * @return 1有效，0无效
 */
int validate_art_method(ArtMethod* art_method);

/**
 * 获取ArtMethod的访问标志
 * @param art_method ArtMethod指针
 * @param version ART版本
 * @return 访问标志
 */
uint32_t get_art_method_access_flags(ArtMethod* art_method, art_version_t version);

/**
 * 设置ArtMethod的访问标志
 * @param art_method ArtMethod指针
 * @param version ART版本
 * @param flags 新的访问标志
 * @return 操作结果
 */
art_method_result_t set_art_method_access_flags(ArtMethod* art_method, art_version_t version, uint32_t flags);

// ========== JNI入口点操作 ==========

/**
 * 获取ArtMethod的JNI入口点
 * @param art_method ArtMethod指针
 * @param version ART版本
 * @return JNI入口点指针
 */
void* get_art_method_jni_entry_point(ArtMethod* art_method, art_version_t version);

/**
 * 设置ArtMethod的JNI入口点
 * @param art_method ArtMethod指针
 * @param version ART版本
 * @param entry_point 新的入口点
 * @return 操作结果
 */
art_method_result_t set_art_method_jni_entry_point(ArtMethod* art_method, art_version_t version, void* entry_point);

/**
 * 获取ArtMethod的快速编译代码入口点
 * @param art_method ArtMethod指针
 * @param version ART版本
 * @return 入口点指针
 */
void* get_art_method_quick_entry_point(ArtMethod* art_method, art_version_t version);

/**
 * 设置ArtMethod的快速编译代码入口点
 * @param art_method ArtMethod指针
 * @param version ART版本
 * @param entry_point 新的入口点
 * @return 操作结果
 */
art_method_result_t set_art_method_quick_entry_point(ArtMethod* art_method, art_version_t version, void* entry_point);

// ========== 高级方法注册 ==========

/**
 * 直接通过ArtMethod注册native方法
 * @param env JNI环境
 * @param clazz Java类
 * @param method_name 方法名
 * @param signature 方法签名
 * @param native_func native函数指针
 * @return 操作结果
 */
art_method_result_t register_native_method_direct(JNIEnv* env, jclass clazz, 
                                                 const char* method_name, 
                                                 const char* signature, 
                                                 void* native_func);

// native_method_t 定义在 common_types.h 中

/**
 * 批量注册native方法
 * @param env JNI环境
 * @param class_name 类名
 * @param methods 方法数组
 * @param method_count 方法数量
 * @return 成功注册的方法数量
 */
int register_native_methods_direct(JNIEnv* env, const char* class_name, 
                                  const native_method_t* methods, int method_count);

/**
 * 创建JNI桥接函数
 * @param target_func 目标函数指针
 * @param version ART版本
 * @return 桥接函数指针
 */
void* create_jni_bridge(void* target_func, art_version_t version);

// ========== 内存保护操作 ==========

/**
 * 修改内存页面保护属性
 * @param addr 地址
 * @param size 大小
 * @param prot 保护属性
 * @return 0成功，-1失败
 */
int change_memory_protection(void* addr, size_t size, int prot);

/**
 * 获取内存页面大小
 * @return 页面大小
 */
size_t get_page_size(void);

/**
 * 对齐到页面边界
 * @param addr 地址
 * @return 对齐后的地址
 */
void* align_to_page(void* addr);

// ========== Hook检测和对抗 ==========

/**
 * 检测ArtMethod是否被Hook
 * @param art_method ArtMethod指针
 * @param version ART版本
 * @return 1被Hook，0正常
 */
int detect_art_method_hook(ArtMethod* art_method, art_version_t version);

/**
 * 检测JNI函数表是否被Hook
 * @param env JNI环境
 * @return 1被Hook，0正常
 */
int detect_jni_function_table_hook(JNIEnv* env);

/**
 * 恢复被Hook的ArtMethod
 * @param art_method ArtMethod指针
 * @param version ART版本
 * @param original_entry_point 原始入口点
 * @return 操作结果
 */
art_method_result_t restore_art_method(ArtMethod* art_method, art_version_t version, void* original_entry_point);

// ========== 调试和诊断 ==========

/**
 * 打印ArtMethod信息
 * @param art_method ArtMethod指针
 * @param version ART版本
 */
void dump_art_method_info(ArtMethod* art_method, art_version_t version);

/**
 * 验证JNI环境完整性
 * @param env JNI环境
 * @return 1完整，0被篡改
 */
int verify_jni_env_integrity(JNIEnv* env);

/**
 * 获取ART运行时信息
 * @param info_buffer 信息缓冲区
 * @param buffer_size 缓冲区大小
 * @return 0成功，-1失败
 */
int get_art_runtime_info(char* info_buffer, size_t buffer_size);

// ========== 工具函数 ==========

/**
 * 计算函数指针校验和
 * @param func_ptr 函数指针
 * @return 校验和
 */
uint32_t calculate_function_checksum(void* func_ptr);

/**
 * 生成随机JNI桥接代码
 * @param target_func 目标函数
 * @param bridge_code 输出的桥接代码
 * @param code_size 代码大小
 * @return 0成功，-1失败
 */
int generate_random_jni_bridge(void* target_func, void* bridge_code, size_t code_size);

/**
 * 混淆函数指针
 * @param func_ptr 原始函数指针
 * @param key 混淆密钥
 * @return 混淆后的指针
 */
void* obfuscate_function_pointer(void* func_ptr, uint32_t key);

/**
 * 解混淆函数指针
 * @param obfuscated_ptr 混淆的指针
 * @param key 混淆密钥
 * @return 原始函数指针
 */
void* deobfuscate_function_pointer(void* obfuscated_ptr, uint32_t key);

// 全局变量
extern art_version_t g_art_version;
extern int g_art_method_hook_initialized;

#ifdef __cplusplus
}
#endif

#endif // ART_METHOD_HOOK_H