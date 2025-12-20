#include "jni_demo.h"
#include "crypto_utils.h"

// ========== 辅助函数实现 ==========

char* jstring_to_cstring(JNIEnv *env, jstring jstr) {
    if (jstr == NULL) return NULL;
    
    const char *utf_chars = (*env)->GetStringUTFChars(env, jstr, NULL);
    if (utf_chars == NULL) return NULL;
    
    size_t len = strlen(utf_chars);
    char *result = (char*)malloc(len + 1);
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

void print_hex(const unsigned char *data, size_t len) {
    for (size_t i = 0; i < len; i++) {
        printf("%02X ", data[i]);
    }
    printf("\n");
}

// ========== JNI 函数实现 ==========

JNIEXPORT jstring JNICALL 
Java_com_example_JNIDemo_processString(JNIEnv *env, jclass clazz, jstring input) {
    char *c_input = jstring_to_cstring(env, input);
    if (c_input == NULL) {
        return cstring_to_jstring(env, "Error: Invalid input string");
    }
    
    // 简单的字符串处理：转换为大写并添加前缀
    size_t len = strlen(c_input);
    char *result = (char*)malloc(len + 20);
    sprintf(result, "[Native] %s", c_input);
    
    // 转换为大写
    for (size_t i = 9; result[i]; i++) {  // 跳过 "[Native] " 前缀
        if (result[i] >= 'a' && result[i] <= 'z') {
            result[i] = result[i] - 32;
        }
    }
    
    jstring jresult = cstring_to_jstring(env, result);
    
    free(c_input);
    free(result);
    return jresult;
}

JNIEXPORT jint JNICALL 
Java_com_example_JNIDemo_addNumbers(JNIEnv *env, jclass clazz, jint a, jint b) {
    return a + b;
}

JNIEXPORT jboolean JNICALL 
Java_com_example_JNIDemo_checkString(JNIEnv *env, jclass clazz, jstring str) {
    char *c_str = jstring_to_cstring(env, str);
    if (c_str == NULL) return JNI_FALSE;
    
    // 检查字符串是否包含 "test"
    jboolean result = (strstr(c_str, "test") != NULL) ? JNI_TRUE : JNI_FALSE;
    
    free(c_str);
    return result;
}

JNIEXPORT jbyteArray JNICALL 
Java_com_example_JNIDemo_encryptBytes(JNIEnv *env, jclass clazz, jbyteArray data, jint key) {
    jsize len = (*env)->GetArrayLength(env, data);
    jbyte *bytes = (*env)->GetByteArrayElements(env, data, NULL);
    
    if (bytes == NULL) return NULL;
    
    // XOR 加密
    for (jsize i = 0; i < len; i++) {
        bytes[i] ^= (jbyte)key;
    }
    
    jbyteArray result = (*env)->NewByteArray(env, len);
    (*env)->SetByteArrayRegion(env, result, 0, len, bytes);
    
    (*env)->ReleaseByteArrayElements(env, data, bytes, JNI_ABORT);
    return result;
}

JNIEXPORT jbyteArray JNICALL 
Java_com_example_JNIDemo_decryptBytes(JNIEnv *env, jclass clazz, jbyteArray data, jint key) {
    // XOR 解密（与加密相同）
    return Java_com_example_JNIDemo_encryptBytes(env, clazz, data, key);
}

JNIEXPORT jint JNICALL 
Java_com_example_JNIDemo_sumIntArray(JNIEnv *env, jclass clazz, jintArray numbers) {
    jsize len = (*env)->GetArrayLength(env, numbers);
    jint *elements = (*env)->GetIntArrayElements(env, numbers, NULL);
    
    if (elements == NULL) return 0;
    
    jint sum = 0;
    for (jsize i = 0; i < len; i++) {
        sum += elements[i];
    }
    
    (*env)->ReleaseIntArrayElements(env, numbers, elements, JNI_ABORT);
    return sum;
}

JNIEXPORT jobjectArray JNICALL 
Java_com_example_JNIDemo_processStringArray(JNIEnv *env, jclass clazz, jobjectArray inputs) {
    jsize len = (*env)->GetArrayLength(env, inputs);
    
    // 创建输出数组
    jclass stringClass = (*env)->FindClass(env, "java/lang/String");
    jobjectArray result = (*env)->NewObjectArray(env, len, stringClass, NULL);
    
    for (jsize i = 0; i < len; i++) {
        jstring input = (jstring)(*env)->GetObjectArrayElement(env, inputs, i);
        char *c_input = jstring_to_cstring(env, input);
        
        if (c_input != NULL) {
            // 添加索引前缀
            char *processed = (char*)malloc(strlen(c_input) + 20);
            sprintf(processed, "[%d] %s", (int)i, c_input);
            
            jstring j_processed = cstring_to_jstring(env, processed);
            (*env)->SetObjectArrayElement(env, result, i, j_processed);
            
            free(c_input);
            free(processed);
        }
    }
    
    return result;
}

JNIEXPORT jstring JNICALL 
Java_com_example_JNIDemo_base64Encode(JNIEnv *env, jclass clazz, jbyteArray data) {
    jsize len = (*env)->GetArrayLength(env, data);
    jbyte *bytes = (*env)->GetByteArrayElements(env, data, NULL);
    
    if (bytes == NULL) return NULL;
    
    char *encoded = base64_encode((unsigned char*)bytes, len);
    jstring result = cstring_to_jstring(env, encoded);
    
    (*env)->ReleaseByteArrayElements(env, data, bytes, JNI_ABORT);
    free(encoded);
    return result;
}

JNIEXPORT jbyteArray JNICALL 
Java_com_example_JNIDemo_base64Decode(JNIEnv *env, jclass clazz, jstring data) {
    char *c_data = jstring_to_cstring(env, data);
    if (c_data == NULL) return NULL;
    
    size_t decoded_len;
    unsigned char *decoded = base64_decode(c_data, &decoded_len);
    
    if (decoded == NULL) {
        free(c_data);
        return NULL;
    }
    
    jbyteArray result = (*env)->NewByteArray(env, decoded_len);
    (*env)->SetByteArrayRegion(env, result, 0, decoded_len, (jbyte*)decoded);
    
    free(c_data);
    free(decoded);
    return result;
}

JNIEXPORT void JNICALL 
Java_com_example_JNIDemo_triggerCallback(JNIEnv *env, jobject obj) {
    // 获取类和回调方法
    jclass cls = (*env)->GetObjectClass(env, obj);
    jmethodID callback_method = (*env)->GetMethodID(env, cls, "javaCallback", "(Ljava/lang/String;)V");
    
    if (callback_method == NULL) {
        printf("[-] Could not find javaCallback method\n");
        return;
    }
    
    // 调用 Java 回调方法
    jstring message = cstring_to_jstring(env, "Hello from Native code!");
    (*env)->CallVoidMethod(env, obj, callback_method, message);
    
    printf("[Native] Callback triggered successfully\n");
}

JNIEXPORT void JNICALL 
Java_com_example_JNIDemo_throwException(JNIEnv *env, jclass clazz) {
    jclass exception_class = (*env)->FindClass(env, "java/lang/RuntimeException");
    (*env)->ThrowNew(env, exception_class, "This is a test exception from native code");
}

JNIEXPORT jboolean JNICALL 
Java_com_example_JNIDemo_handleException(JNIEnv *env, jclass clazz) {
    // 故意调用一个会产生异常的 JNI 函数
    jstring invalid_string = NULL;
    const char *chars = (*env)->GetStringUTFChars(env, invalid_string, NULL);
    
    // 检查是否有异常发生
    if ((*env)->ExceptionCheck(env)) {
        printf("[Native] Exception detected, clearing it...\n");
        (*env)->ExceptionClear(env);
        return JNI_TRUE;
    }
    
    return JNI_FALSE;
}

JNIEXPORT jlong JNICALL 
Java_com_example_JNIDemo_performanceTest(JNIEnv *env, jclass clazz, jint iterations) {
    clock_t start = clock();
    
    // 执行大量简单操作
    volatile int sum = 0;
    for (int i = 0; i < iterations; i++) {
        sum += i;
    }
    
    clock_t end = clock();
    long duration_ms = ((long)(end - start) * 1000) / CLOCKS_PER_SEC;
    
    printf("[Native] Performance test completed: %d iterations in %ld ms\n", 
           iterations, duration_ms);
    
    return duration_ms;
}

JNIEXPORT jstring JNICALL 
Java_com_example_JNIDemo_getSystemInfo(JNIEnv *env, jclass clazz) {
    char info[512];
    time_t now = time(NULL);
    char *time_str = ctime(&now);
    
    // 移除换行符
    if (time_str) {
        char *newline = strchr(time_str, '\n');
        if (newline) *newline = '\0';
    }
    
    snprintf(info, sizeof(info), 
        "System Information:\n"
        "- Timestamp: %s\n"
        "- Pointer size: %zu bytes\n"
        "- int size: %zu bytes\n"
        "- long size: %zu bytes\n"
        "- Process ID: %d\n",
        time_str ? time_str : "unknown",
        sizeof(void*),
        sizeof(int),
        sizeof(long),
        getpid ? getpid() : -1
    );
    
    return cstring_to_jstring(env, info);
}