#ifndef COMMON_TYPES_H
#define COMMON_TYPES_H

// 公共类型定义，避免头文件间的重复定义问题

/**
 * JNI方法结构体定义
 */
typedef struct {
    const char* name;
    const char* signature;
    void* fnPtr;
} native_method_t;

#endif // COMMON_TYPES_H