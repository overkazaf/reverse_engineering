#include "crypto_utils.h"
#include <stdlib.h>
#include <string.h>

// Base64 编码表
static const char base64_chars[] = 
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

// Base64 解码表
static const int base64_decode_table[256] = {
    -1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,
    -1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,
    -1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,62,-1,-1,-1,63,
    52,53,54,55,56,57,58,59,60,61,-1,-1,-1,-1,-1,-1,
    -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9,10,11,12,13,14,
    15,16,17,18,19,20,21,22,23,24,25,-1,-1,-1,-1,-1,
    -1,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,
    41,42,43,44,45,46,47,48,49,50,51,-1,-1,-1,-1,-1
};

char* base64_encode(const unsigned char* data, size_t len) {
    if (data == NULL || len == 0) return NULL;
    
    size_t output_len = 4 * ((len + 2) / 3);
    char* encoded = (char*)malloc(output_len + 1);
    if (encoded == NULL) return NULL;
    
    size_t i, j;
    for (i = 0, j = 0; i < len;) {
        uint32_t a = i < len ? data[i++] : 0;
        uint32_t b = i < len ? data[i++] : 0;
        uint32_t c = i < len ? data[i++] : 0;
        
        uint32_t triple = (a << 16) + (b << 8) + c;
        
        encoded[j++] = base64_chars[(triple >> 18) & 63];
        encoded[j++] = base64_chars[(triple >> 12) & 63];
        encoded[j++] = base64_chars[(triple >> 6) & 63];
        encoded[j++] = base64_chars[triple & 63];
    }
    
    // 添加填充
    size_t padding = len % 3;
    if (padding == 1) {
        encoded[output_len - 2] = '=';
        encoded[output_len - 1] = '=';
    } else if (padding == 2) {
        encoded[output_len - 1] = '=';
    }
    
    encoded[output_len] = '\0';
    return encoded;
}

unsigned char* base64_decode(const char* data, size_t* decoded_len) {
    if (data == NULL) return NULL;
    
    size_t len = strlen(data);
    if (len % 4 != 0) return NULL;
    
    size_t output_len = len / 4 * 3;
    if (data[len - 1] == '=') output_len--;
    if (data[len - 2] == '=') output_len--;
    
    unsigned char* decoded = (unsigned char*)malloc(output_len);
    if (decoded == NULL) return NULL;
    
    size_t i, j;
    for (i = 0, j = 0; i < len;) {
        uint32_t a = base64_decode_table[(unsigned char)data[i++]];
        uint32_t b = base64_decode_table[(unsigned char)data[i++]];
        uint32_t c = base64_decode_table[(unsigned char)data[i++]];
        uint32_t d = base64_decode_table[(unsigned char)data[i++]];
        
        if (a == -1 || b == -1 || c == -1 || d == -1) {
            free(decoded);
            return NULL;
        }
        
        uint32_t triple = (a << 18) + (b << 12) + (c << 6) + d;
        
        if (j < output_len) decoded[j++] = (triple >> 16) & 255;
        if (j < output_len) decoded[j++] = (triple >> 8) & 255;
        if (j < output_len) decoded[j++] = triple & 255;
    }
    
    *decoded_len = output_len;
    return decoded;
}

void xor_encrypt(unsigned char* data, size_t len, unsigned char key) {
    for (size_t i = 0; i < len; i++) {
        data[i] ^= key;
    }
}

uint32_t simple_hash(const char* str) {
    uint32_t hash = 5381;
    int c;
    
    while ((c = *str++)) {
        hash = ((hash << 5) + hash) + c;
    }
    
    return hash;
}

void generate_random_bytes(unsigned char* buffer, size_t len) {
    // 简单的伪随机数生成（仅用于演示）
    static unsigned int seed = 1;
    for (size_t i = 0; i < len; i++) {
        seed = seed * 1103515245 + 12345;
        buffer[i] = (seed >> 16) & 0xFF;
    }
}