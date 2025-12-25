---
title: "TOTP 技术原理"
date: 2024-04-13
tags: ["签名验证", "加密分析", "基础知识", "Smali", "Android", "DEX"]
weight: 10
---

# TOTP 技术原理

**TOTP (Time-Based One-Time Password)** 是一种基于时间的一次性密码算法，广泛应用于双因素认证 (2FA) 和 API 防护场景。

## 核心原理

TOTP 基于 **HMAC-SHA1** 算法，结合共享密钥和当前时间戳生成动态密码。其核心公式为：

```
TOTP = HMAC-SHA1(Secret, TimeCounter) mod 10^Digits
```

其中：
- `TimeCounter = floor(CurrentTime / Period)`
- `Period` 通常为 30 秒
- `Digits` 通常为 6 位

---

## 算法流程

```
┌─────────────────────────────────────────────────────────────┐
│                      TOTP 生成流程                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌──────────┐     ┌──────────────┐     ┌───────────────┐   │
│   │ 当前时间  │ ──► │ 计算时间计数器 │ ──► │ HMAC-SHA1    │   │
│   │ (毫秒)   │     │ T = t / period│     │ (secret, T)  │   │
│   └──────────┘     └──────────────┘     └───────┬───────┘   │
│                                                 │           │
│   ┌──────────┐     ┌──────────────┐     ┌───────▼───────┐   │
│   │ 6-8位OTP │ ◄── │  取模运算     │ ◄── │ 动态截断      │   │
│   │ (输出)   │     │ mod 10^digits│     │ (取4字节)     │   │
│   └──────────┘     └──────────────┘     └───────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 关键参数

| 参数 | 说明 | 典型值 |
| ---- | ---- | ------ |
| Secret | 共享密钥 (Base32编码) | 16-32 字节 |
| Period | 时间步长 | 30 秒 |
| Digits | OTP 位数 | 6-8 位 |
| Algorithm | 哈希算法 | SHA1 / SHA256 / SHA512 |

---

## 标准实现

以下是符合 **RFC 6238** 规范的 Python 实现：

```python
import hmac
import hashlib
import time
import base64

def generate_totp(secret: bytes, period: int = 30, digits: int = 6) -> str:
    """
    生成 TOTP 一次性密码

    Args:
        secret: 共享密钥 (原始字节)
        period: 时间步长 (秒)
        digits: OTP 位数

    Returns:
        生成的 OTP 字符串
    """
    # 1. 计算时间计数器
    counter = int(time.time()) // period
    counter_bytes = counter.to_bytes(8, byteorder='big')

    # 2. HMAC-SHA1 计算
    hmac_result = hmac.new(secret, counter_bytes, hashlib.sha1).digest()

    # 3. 动态截断 (Dynamic Truncation)
    offset = hmac_result[-1] & 0x0F
    binary = (
        (hmac_result[offset] & 0x7F) << 24 |
        (hmac_result[offset + 1] & 0xFF) << 16 |
        (hmac_result[offset + 2] & 0xFF) << 8 |
        (hmac_result[offset + 3] & 0xFF)
    )

    # 4. 取模得到最终 OTP
    otp = binary % (10 ** digits)
    return str(otp).zfill(digits)


def generate_totp_from_base32(secret_base32: str, period: int = 30, digits: int = 6) -> str:
    """
    从 Base32 编码的密钥生成 TOTP

    Args:
        secret_base32: Base32 编码的共享密钥
        period: 时间步长 (秒)
        digits: OTP 位数

    Returns:
        生成的 OTP 字符串
    """
    # 解码 Base32 密钥
    secret = base64.b32decode(secret_base32.upper())
    return generate_totp(secret, period, digits)


# 使用示例
if __name__ == "__main__":
    # Base32 编码的测试密钥
    test_secret = "JBSWY3DPEHPK3PXP"
    otp = generate_totp_from_base32(test_secret)
    print(f"Generated OTP: {otp}")
```

---

## 动态截断详解

动态截断 (Dynamic Truncation) 是 TOTP 的关键步骤，用于从 20 字节的 HMAC 结果中提取 4 字节作为 OTP 的来源：

1. **取偏移量**: 从 HMAC 结果的最后一个字节取低 4 位作为偏移量 (0-15)
2. **提取 4 字节**: 从偏移量位置开始取 4 个字节
3. **屏蔽符号位**: 将第一个字节的最高位置 0，确保结果为正数
4. **取模运算**: 对 10^digits 取模，得到最终的 OTP

```python
# 动态截断伪代码
offset = hmac_result[-1] & 0x0F  # 取最后字节的低4位
binary = hmac_result[offset:offset+4]  # 取4字节
binary[0] &= 0x7F  # 屏蔽符号位
otp = int.from_bytes(binary, 'big') % (10 ** digits)
```

---

## 在反爬场景中的应用

### 1. 动态 Token 生成

服务端和客户端共享密钥，客户端生成的 TOTP 作为请求签名的一部分：

```python
def sign_request(params: dict, secret: bytes) -> dict:
    """使用 TOTP 签名请求"""
    totp = generate_totp(secret)
    params['timestamp'] = int(time.time() * 1000)
    params['otp'] = totp
    return params
```

### 2. 防重放攻击

由于 OTP 有时效性 (通常 30 秒)，捕获的请求无法长期复用。服务端验证时通常允许 ±1 个周期的容差：

```python
def verify_totp(secret: bytes, otp: str, tolerance: int = 1) -> bool:
    """验证 TOTP，允许时间误差"""
    for offset in range(-tolerance, tolerance + 1):
        counter = (int(time.time()) // 30) + offset
        expected = generate_totp_with_counter(secret, counter)
        if otp == expected:
            return True
    return False
```

### 3. 密钥保护

共享密钥通常经过混淆或加密存储在客户端，增加逆向难度：

- **硬编码混淆**: 密钥被拆分或异或后存储
- **加密配置**: 密钥加密存储在配置文件中
- **远程获取**: 启动时从服务端安全获取密钥

---

## 逆向要点

### 1. 定位密钥存储

```javascript
// 常见的密钥存储位置
1. 硬编码在 JS/SO 中
2. 存储在 SharedPreferences / localStorage
3. 从服务端 API 动态获取
4. 使用设备信息派生 (PBKDF2, HKDF)
```

### 2. 确定算法参数

```python
# 需要确定的参数
1. Period (时间步长): 常见值 30, 60
2. Digits (位数): 常见值 6, 8
3. Algorithm (算法): SHA1, SHA256, SHA512
4. 时间基准: Unix 时间戳 vs 自定义纪元
```

### 3. 时间同步

```python
# 注意事项
1. 客户端和服务端时间可能存在偏差
2. 服务端通常允许 ±1 个周期的容差
3. 某些实现使用毫秒级时间戳
4. 注意时区问题
```

---

## 与 HOTP 的区别

| 特性 | TOTP | HOTP |
| ---- | ---- | ---- |
| 计数器 | 基于时间 | 基于事件 (递增) |
| 有效期 | 时间窗口内 | 直到使用 |
| 同步问题 | 需要时间同步 | 需要计数器同步 |
| 适用场景 | 双因素认证 | 硬件令牌 |
| RFC 规范 | RFC 6238 | RFC 4226 |

---

## 参考资料

- [RFC 6238 - TOTP: Time-Based One-Time Password Algorithm](https://tools.ietf.org/html/rfc6238)
- [RFC 4226 - HOTP: An HMAC-Based One-Time Password Algorithm](https://tools.ietf.org/html/rfc4226)
- [Google Authenticator 实现](https://github.com/google/google-authenticator)
