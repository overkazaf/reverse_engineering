#ifndef JNI_DEMO_H
#define JNI_DEMO_H

#include <jni.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

// JNI 函数声明

#ifdef __cplusplus
extern "C" {
#endif

// 基础数据类型处理
JNIEXPORT jstring JNICALL Java_com_example_JNIDemo_processString(JNIEnv *env, jclass clazz, jstring input);
JNIEXPORT jint JNICALL Java_com_example_JNIDemo_addNumbers(JNIEnv *env, jclass clazz, jint a, jint b);
JNIEXPORT jboolean JNICALL Java_com_example_JNIDemo_checkString(JNIEnv *env, jclass clazz, jstring str);

// 数组操作
JNIEXPORT jbyteArray JNICALL Java_com_example_JNIDemo_encryptBytes(JNIEnv *env, jclass clazz, jbyteArray data, jint key);
JNIEXPORT jbyteArray JNICALL Java_com_example_JNIDemo_decryptBytes(JNIEnv *env, jclass clazz, jbyteArray data, jint key);
JNIEXPORT jint JNICALL Java_com_example_JNIDemo_sumIntArray(JNIEnv *env, jclass clazz, jintArray numbers);

// 复杂数据结构
JNIEXPORT jobjectArray JNICALL Java_com_example_JNIDemo_processStringArray(JNIEnv *env, jclass clazz, jobjectArray inputs);
JNIEXPORT jstring JNICALL Java_com_example_JNIDemo_base64Encode(JNIEnv *env, jclass clazz, jbyteArray data);
JNIEXPORT jbyteArray JNICALL Java_com_example_JNIDemo_base64Decode(JNIEnv *env, jclass clazz, jstring data);

// 回调机制
JNIEXPORT void JNICALL Java_com_example_JNIDemo_triggerCallback(JNIEnv *env, jobject obj);

// 异常处理
JNIEXPORT void JNICALL Java_com_example_JNIDemo_throwException(JNIEnv *env, jclass clazz);
JNIEXPORT jboolean JNICALL Java_com_example_JNIDemo_handleException(JNIEnv *env, jclass clazz);

// 性能测试
JNIEXPORT jlong JNICALL Java_com_example_JNIDemo_performanceTest(JNIEnv *env, jclass clazz, jint iterations);

// 系统信息
JNIEXPORT jstring JNICALL Java_com_example_JNIDemo_getSystemInfo(JNIEnv *env, jclass clazz);

// 辅助函数
char* jstring_to_cstring(JNIEnv *env, jstring jstr);
jstring cstring_to_jstring(JNIEnv *env, const char *cstr);
void print_hex(const unsigned char *data, size_t len);

#ifdef __cplusplus
}
#endif

#endif // JNI_DEMO_H