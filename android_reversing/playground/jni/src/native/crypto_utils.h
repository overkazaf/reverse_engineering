#ifndef CRYPTO_UTILS_H
#define CRYPTO_UTILS_H

#include <stdint.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Base64 编码
 * @param data 要编码的数据
 * @param len 数据长度
 * @return 编码后的字符串（需要 free）
 */
char* base64_encode(const unsigned char* data, size_t len);

/**
 * Base64 解码
 * @param data Base64 编码的字符串
 * @param decoded_len 输出解码后数据的长度
 * @return 解码后的数据（需要 free）
 */
unsigned char* base64_decode(const char* data, size_t* decoded_len);

/**
 * XOR 加密/解密
 * @param data 要处理的数据
 * @param len 数据长度
 * @param key 密钥
 */
void xor_encrypt(unsigned char* data, size_t len, unsigned char key);

/**
 * 简单哈希函数
 * @param str 字符串
 * @return 哈希值
 */
uint32_t simple_hash(const char* str);

/**
 * 生成随机字节
 * @param buffer 输出缓冲区
 * @param len 要生成的字节数
 */
void generate_random_bytes(unsigned char* buffer, size_t len);

#ifdef __cplusplus
}
#endif

#endif // CRYPTO_UTILS_H