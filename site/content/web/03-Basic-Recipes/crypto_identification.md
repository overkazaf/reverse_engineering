---
title: "加密算法识别与分析"
date: 2024-10-10
tags: ["Web", "RSA", "加密分析", "Hook", "AES", "调试"]
weight: 10
---

# 加密算法识别与分析

## 概述

Web 应用中常用各种加密算法来保护数据传输和存储。识别使用了哪种算法是逆向的第一步。本文介绍常见加密算法的特征及识别方法。

---

## 📚 前置知识

在开始本配方之前，建议先掌握以下内容：

| 知识领域 | 重要程度 | 参考资料 |
|----------|---------|---------|
| JavaScript 基础 | 必需 | [JavaScript 基础](../01-Foundations/javascript_basics.md) |
| Chrome DevTools | 必需 | [浏览器开发者工具](../02-Tooling/browser_devtools.md) |
| HTTP 协议基础 | 推荐 | [HTTP/HTTPS 协议](../01-Foundations/http_https_protocol.md) |

> 💡 **提示**: 加密算法识别是逆向分析的**第一步**。掌握各种算法的输出特征后，可以快速判断目标使用的加密方式，选择合适的对抗策略。

---

## 哈希算法 (Hash Functions)

### MD5

**特征**:

- 输出长度: 128 bit (16 bytes) = 32 位十六进制字符
- 不可逆（单向）
- 已不安全，但仍广泛使用

**识别方法**:

```javascript
// 典型输出
"5d41402abc4b2a76b9719d911017c592"; // MD5("hello")

// 库特征
CryptoJS.MD5("data").toString();
md5("data");
```

**Python 实现**:

```python
import hashlib
hashlib.md5(b"hello").hexdigest()
# '5d41402abc4b2a76b9719d911017c592'
```

### SHA 家族

| 算法 | 输出长度 | 十六进制长度 | 示例 |
| ------- | -------- | ------------ | ------------------------------------------------------------------ |
| SHA-1 | 160 bit | 40 字符 | `aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d` |
| SHA-256 | 256 bit | 64 字符 | `2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824` |
| SHA-512 | 512 bit | 128 字符 | (太长省略) |

**识别方法**:

- 看输出长度
- 搜索关键词: `SHA`, `sha256`, `createHash`

**Node.js 实现**:

```javascript
const crypto = require("crypto");
crypto.createHash("sha256").update("hello").digest("hex");
```

---

## 对称加密 (Symmetric Encryption)

### AES (Advanced Encryption Standard)

**特征**:

- 块加密，块大小 128 bit
- 密钥长度: 128/192/256 bit
- 需要 **IV (Initialization Vector)**
- 模式: ECB, CBC, CTR, GCM 等

**识别方法**:

```javascript
// CryptoJS
CryptoJS.AES.encrypt("data", "password").toString();

// Web Crypto API
crypto.subtle.encrypt({ name: "AES-CBC", iv: iv }, key, data);

// 搜索关键词
"AES", "encrypt", "decrypt", "IV", "padding";
```

**常见模式对比**:

| 模式 | IV 需求 | 并行加密 | 安全性 | 备注 |
| ---- | ------- | -------- | ------ | ---------------------------- |
| ECB | 否 | 是 | 低 | 不安全，相同明文产生相同密文 |
| CBC | 是 | 否 | 中 | 最常用 |
| CTR | 是 | 是 | 高 | 流式加密 |
| GCM | 是 | 是 | 高 | 带认证 |

**Python 实现 (AES-CBC)**:

```python
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64

key = b'1234567890123456' # 16 bytes for AES-128
iv = b'abcdefghijklmnop'

# 加密
cipher = AES.new(key, AES.MODE_CBC, iv)
ciphertext = cipher.encrypt(pad(b'secret data', AES.block_size))
print(base64.b64encode(ciphertext).decode())

# 解密
cipher = AES.new(key, AES.MODE_CBC, iv)
plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
print(plaintext.decode())
```

### DES / 3DES

**特征**:

- DES: 56 bit 密钥，已过时
- 3DES: 168 bit 密钥
- 块大小: 64 bit

**识别**: 搜索 `DES`, `TripleDES`

---

## 非对称加密 (Asymmetric Encryption)

### RSA

**特征**:

- 公钥加密，私钥解密
- 密钥长度: 1024/2048/4096 bit
- 慢，通常用于加密小数据（如 AES 密钥）

**识别方法**:

```javascript
// JSEncrypt 库
var encrypt = new JSEncrypt();
encrypt.setPublicKey(publicKey);
var encrypted = encrypt.encrypt("data");

// Web Crypto API
crypto.subtle.encrypt({ name: "RSA-OAEP" }, publicKey, data);

// 关键词
"RSA", "publicKey", "privateKey", "-----BEGIN PUBLIC KEY-----";
```

**公钥格式**:

```
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...
-----END PUBLIC KEY-----
```

**Python 实现**:

```python
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import base64

# 生成密钥对
key = RSA.generate(2048)
public_key = key.publickey()

# 加密
cipher = PKCS1_OAEP.new(public_key)
ciphertext = cipher.encrypt(b'secret')
print(base64.b64encode(ciphertext).decode())

# 解密
cipher = PKCS1_OAEP.new(key)
plaintext = cipher.decrypt(ciphertext)
print(plaintext.decode())
```

---

## 编码 vs 加密

### Base64 (编码，非加密)

**特征**:

- 字符集: `A-Z`, `a-z`, `0-9`, `+`, `/`
- 结尾可能有 `=` 或 `==` 填充
- 长度是 4 的倍数

**识别**:

```javascript
btoa("hello"); // "aGVsbG8="
atob("aGVsbG8="); // "hello"
```

**Python**:

```python
import base64
base64.b64encode(b'hello').decode() # 'aGVsbG8='
base64.b64decode('aGVsbG8=').decode() # 'hello'
```

### Hex (十六进制编码)

**特征**:

- 字符集: `0-9`, `a-f`
- 每个字节用 2 个字符表示

**识别**:

```javascript
"48656c6c6f"; // "Hello" 的 Hex 编码
```

**Python**:

```python
'Hello'.encode().hex() # '48656c6c6f'
bytes.fromhex('48656c6c6f').decode() # 'Hello'
```

---

## 识别流程

### 步骤一：观察输出特征

1. **长度固定**: 可能是哈希

- 32 字符 -> MD5
- 40 字符 -> SHA-1
- 64 字符 -> SHA-256

2. **长度可变**: 可能是加密或编码
- 结尾有 `=` -> Base64
- 全是 `0-9a-f` -> Hex

### 步骤二：搜索关键词

在 Sources 面板全局搜索：

- 通用: `encrypt`, `decrypt`, `crypto`
- 库名: `CryptoJS`, `JSEncrypt`, `forge`
- 算法名: `AES`, `RSA`, `MD5`, `SHA`

### 步骤三：Hook 加密函数

```javascript
// Hook CryptoJS
if (window.CryptoJS) {
const originalAES = CryptoJS.AES.encrypt;
CryptoJS.AES.encrypt = function (message, key, cfg) {
console.log("[AES Encrypt]");
console.log("Message:", message.toString());
console.log("Key:", key.toString());
debugger;
return originalAES.apply(this, arguments);
};
}
```

---

## 常见加密库

### JavaScript 加密库

| 库名 | 特点 | 检测方法 |
| ------------------ | -------------------- | ---------------------- |
| **CryptoJS** | 最流行的纯 JS 加密库 | `window.CryptoJS` |
| **Forge** | 全功能加密库 | `window.forge` |
| **JSEncrypt** | RSA 专用 | `window.JSEncrypt` |
| **crypto-js** | CryptoJS 的 npm 包 | `require('crypto-js')` |
| **Web Crypto API** | 浏览器原生 | `window.crypto.subtle` |

### Python 加密库

| 库名 | 安装 | 用途 |
| ---------------- | -------------------------- | ------------- |
| **hashlib** | 内置 | MD5, SHA |
| **pycryptodome** | `pip install pycryptodome` | AES, RSA, DES |
| **cryptography** | `pip install cryptography` | 现代加密库 |

---

## 实战案例

### 案例 1: 识别未知哈希

**观察**:

```
输入: "admin"
输出: "21232f297a57a5a743894a0e4a801fc3"
```

**分析**:

- 长度 32 -> MD5
- 验证: `MD5("admin")` = `21232f297a57a5a743894a0e4a801fc3` ✅

### 案例 2: 识别加密算法

**观察**:

```javascript
var encrypted = "U2FsdGVkX1+gGv7..."; // Base64 格式
```

**分析**:

- 开头 `U2FsdGVkX1` -> Base64 解码 = `Salted__`
- 这是 **CryptoJS AES** 的典型特征

**验证**:

```javascript
CryptoJS.AES.encrypt("data", "password").toString();
// "U2FsdGVkX1+..."
```

---

## 相关章节

- [JavaScript Hook 技术](./hooking_techniques.md)
- [调试技巧与断点设置](./debugging_techniques.md)
- [API 接口逆向](./api_reverse_engineering.md)
