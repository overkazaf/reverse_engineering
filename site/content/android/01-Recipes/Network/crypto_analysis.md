---
title: "分析并提取 Android 应用的加密密钥"
date: 2025-04-07
type: posts
tags: ["RSA", "加密分析", "Hook", "DEX", "IDA Pro", "反混淆"]
weight: 10
---

# 分析并提取 Android 应用的加密密钥

> **📚 前置知识**
>
> 本配方涉及以下核心技术，建议先阅读相关章节：
>
> - **[Frida 完整指南](../../02-Tools/Dynamic/frida_guide.md)** - 使用 Hook 拦截加密函数
> - **[网络抓包技术](./network_sniffing.md)** - 捕获加密前后的数据对比

## 问题场景

_你遇到了什么问题？_

- App 的 API 请求参数被加密了，看不懂内容
- 想知道 App 使用了什么加密算法
- 需要提取加密密钥来解密数据
- 想重现 App 的加密/签名逻辑用于自动化
- 需要绕过加密验证或签名检查

_本配方教你_：识别加密算法、定位密钥位置、使用 Frida 动态提取密钥。

_核心理念_：

> 💡 **密码学逆向的关键不是破解算法，而是找到密钥**
>
> - 不要试图"破解" AES/RSA 等成熟算法（几乎不可能）
> - 用动态分析直接提取密钥
> - 或直接调用 App 自己的加密函数（利用已有密钥）

_预计用时_: 30-60 分钟

---

## 工具清单

### 必需工具

- **jadx-gui** - Java 层静态分析
- **Frida** - 动态 Hook 提取密钥
- **Android 设备**（已 Root）

### 可选工具

- **IDA Pro / Ghidra** - Native 层分析
- **Burp Suite** - 抓包查看加密后的数据
- **CyberChef** - 在线加密/解密工具（<https://gchq.github.io/CyberChef/）>

---

## 前置条件

### ✅ 确认清单

```bash
# 1. Frida 正常运行
frida-ps -U

# 2. jadx-gui 已安装
jadx-gui --version

# 3. 抓包环境已配置（可选）
# 参考: network_sniffing.md
```

---

## 解决方案

### 第 1 步：识别加密算法（5 分钟）

#### 1.1 搜索特征字符串

用 jadx-gui 打开 APK，全局搜索：

```bash
# 对称加密
AES
DES
3DES

# 非对称加密
RSA
ECC

# 哈希算法
MD5
SHA
SHA256
HMAC

# 加密模式
ECB
CBC
CTR
GCM

# Padding
PKCS5Padding
PKCS7Padding

# 编码
Base64
```

#### 1.2 搜索 Java 加密 API

```java
// Java 层加密 API
javax.crypto.Cipher
javax.crypto.spec.SecretKeySpec
javax.crypto.spec.IvParameterSpec
javax.crypto.Mac
java.security.Signature
java.security.MessageDigest

// Base64 编码
android.util.Base64
java.util.Base64
```

#### 1.3 检查 Native 层加密

```bash
# 解压 APK
unzip app.apk -d app_unzipped

# 搜索 .so 文件中的加密库
strings app_unzipped/lib/*/lib*.so | grep -i -E "openssl|crypto|encrypt|aes|rsa"

# 或使用 rabin2 分析
rabin2 -z app_unzipped/lib/arm64-v8a/libnative.so | grep -i encrypt
```

---

### 第 2 步：定位加密代码（10 分钟）

#### 2.1 跟踪加密字符串

假设你搜到了 `AES/CBC/PKCS5Padding`：

1. 在 jadx 中点击这个字符串
2. 查看交叉引用（`X` 键或右键 → Find Usage）
3. 跳转到使用这个字符串的函数

**典型代码模式**：

```java
// 你可能会看到类似这样的代码
public static String encrypt(String plaintext) {
    Cipher cipher = Cipher.getInstance("AES/CBC/PKCS5Padding");
    SecretKeySpec key = new SecretKeySpec(KEY_BYTES, "AES");
    IvParameterSpec iv = new IvParameterSpec(IV_BYTES);
    cipher.init(Cipher.ENCRYPT_MODE, key, iv);
    byte[] encrypted = cipher.doFinal(plaintext.getBytes());
    return Base64.encodeToString(encrypted, Base64.DEFAULT);
}
```

**记录关键信息**：

```text
密钥变量: KEY_BYTES
IV 变量: IV_BYTES
加密函数: com.example.app.CryptoUtils.encrypt()
```

---

### 第 3 步：找到密钥位置（10 分钟）

<details>
<summary><b>📍 位置 1: Java 代码硬编码（难度：低）</b></summary>

**查找方法**：

```java
// 搜索关键词
SecretKeySpec
byte[] key
private static final byte[]
```

**示例**：

```java
private static final byte[] KEY = {
    0x12, 0x34, 0x56, 0x78,
    0x9a, 0xbc, 0xde, 0xf0,
    // ... 16/24/32 字节
};
```

**密钥长度**：

- AES-128: 16 字节
- AES-192: 24 字节
- AES-256: 32 字节

</details>

<details>
<summary><b>📍 位置 2: 资源文件（难度：低）</b></summary>

**查找路径**：

```bash
# 检查 assets 目录
ls app_unzipped/assets/

# 检查 res/raw
ls app_unzipped/res/raw/

# 搜索二进制文件
find app_unzipped -type f -exec file {} \; | grep data
```

**常见文件名**：

- `secret.key`
- `config.dat`
- `license.bin`

</details>

<details>
<summary><b>📍 位置 3: Native (.so) 硬编码（难度：中）</b></summary>

**IDA Pro 分析**：

1. 打开 `.so` 文件
2. 跳转到 **Strings** 窗口 (`Shift+F12`)
3. 搜索关键字符串
4. 查看交叉引用找到使用密钥的函数

**Ghidra 分析**：

1. 导入 `.so` 文件
2. 搜索 → For Strings
3. 筛选长度为 16/24/32 的可疑字符串

</details>

<details>
<summary><b>📍 位置 4: 动态生成（难度：高）</b></summary>

**特征**：密钥通过算法计算，常见方式：

```java
// 基于设备信息生成
String deviceId = getDeviceId();
byte[] key = MD5(deviceId + SALT);

// 基于时间戳
long timestamp = System.currentTimeMillis();
byte[] key = HMACSHA256(timestamp, SECRET);
```

**从服务器获取**：

- 启动时从服务器获取密钥
- 可能经过 RSA 加密传输

**对策**：

1. 抓包查看密钥传输
2. Hook 网络请求获取密钥
3. 或直接 Hook 加密函数（密钥已在内存中）

</details>

---

### 第 4 步：动态提取密钥（15 分钟）

_终极方法_：无论密钥藏在哪，只要加密函数被调用，Hook 就能抓到

#### 4.1 Hook Java 层加密

**通用 AES Hook 脚本** `dump_aes_key.js`：

```javascript
Java.perform(function () {
  console.log("\n[Crypto Hook] 启动\n");

  // Hook Cipher.init
  var Cipher = Java.use("javax.crypto.Cipher");
  Cipher.init.overload(
    "int",
    "java.security.Key",
    "java.security.spec.AlgorithmParameterSpec"
  ).implementation = function (opmode, key, spec) {
    console.log("\n🔐 [Cipher.init] 捕获!");

    // 模式
    var mode = opmode == 1 ? "ENCRYPT" : "DECRYPT";
    console.log("    模式: " + mode);

    // 算法
    console.log("    算法: " + this.getAlgorithm());

    // 提取密钥
    try {
      var secretKey = Java.cast(
        key,
        Java.use("javax.crypto.spec.SecretKeySpec")
      );
      var keyBytes = secretKey.getEncoded();
      var Base64 = Java.use("android.util.Base64");
      console.log("    密钥 (Base64): " + Base64.encodeToString(keyBytes, 0));
      console.log("    密钥 (Hex): " + bytesToHex(keyBytes));
    } catch (e) {
      console.log("    密钥类型: " + key.$className);
    }

    // 提取 IV
    if (spec) {
      try {
        var ivSpec = Java.cast(
          spec,
          Java.use("javax.crypto.spec.IvParameterSpec")
        );
        var ivBytes = ivSpec.getIV();
        console.log("    IV (Hex): " + bytesToHex(ivBytes));
      } catch (e) {}
    }

    return this.init(opmode, key, spec);
  };

  // Hook Cipher.doFinal
  Cipher.doFinal.overload("[B").implementation = function (input) {
    var result = this.doFinal(input);

    console.log("\n📦 [Cipher.doFinal] 捕获!");
    console.log("    输入长度: " + input.length);
    console.log("    输出长度: " + result.length);
    console.log("    输入数据 (前32字节): " + bytesToHex(input.slice(0, 32)));
    console.log("    输出数据 (前32字节): " + bytesToHex(result.slice(0, 32)));

    return result;
  };

  function bytesToHex(bytes) {
    var hex = [];
    for (var i = 0; i < bytes.length && i < 32; i++) {
      hex.push(("0" + (bytes[i] & 0xff).toString(16)).slice(-2));
    }
    return hex.join(" ");
  }

  console.log("✅ [Crypto Hook] 配置完成\n");
});
```

**运行脚本**：

```bash
frida -U -f com.example.app -l dump_aes_key.js
```

**预期输出**：

```text
🔐 [Cipher.init] 捕获!
    模式: ENCRYPT
    算法: AES/CBC/PKCS5Padding
    密钥 (Base64): MTIzNDU2Nzg5MGFiY2RlZg==
    密钥 (Hex): 31 32 33 34 35 36 37 38 39 30 61 62 63 64 65 66
    IV (Hex): 66 65 64 63 62 61 30 39 38 37 36 35 34 33 32 31

📦 [Cipher.doFinal] 捕获!
    输入长度: 128
    输出长度: 144
    输入数据 (前32字节): 7b 22 75 73 65 72 6e 61 6d 65 22 3a ...
    输出数据 (前32字节): a3 b2 c1 d0 e4 f5 ...
```

#### 4.2 Hook Native 层加密

**查找 Native 加密函数**：

```bash
# 使用 nm 查看函数
nm -D libnative.so | grep -i encrypt

# 使用 Frida
frida -U -f com.example.app
> Module.enumerateExports('libnative.so').filter(e => e.name.includes('encrypt'))
```

**Hook Native 函数**：

```javascript
Interceptor.attach(
  Module.findExportByName("libnative.so", "Java_com_example_Crypto_encrypt"),
  {
    onEnter: function (args) {
      console.log("\n[Native Encrypt] 调用!");

      // args[0] = JNIEnv*
      // args[1] = jclass
      // args[2] = 第一个参数（通常是明文）
      // args[3] = 第二个参数（可能是密钥）

      // 读取字符串参数
      var plaintext = Java.vm
        .getEnv()
        .getStringUtfChars(args[2], null)
        .readCString();
      console.log("    明文: " + plaintext);

      // 保存指针用于后续读取
      this.keyPtr = args[3];
    },
    onLeave: function (retval) {
      // retval 是返回值（密文）
      console.log("    返回值: " + retval);
    },
  }
);
```

---

### 第 5 步：验证密钥（5 分钟）

#### 5.1 使用 CyberChef 验证

1. 打开 <https://gchq.github.io/CyberChef/>
2. 选择操作：`AES Decrypt`
3. 输入：
    ```text
    | 项目 | 说明 |
    | --- | --- |
    | **Key** (Hex) | `31 32 33 34 ...` |
    | **IV** (Hex) | `66 65 64 63 ...` |
    | **Mode** | `CBC` |
    | **Input** | 密文（Base64 或 Hex） |
    ```
4. 点击 **Bake!**

如果解密成功，说明密钥正确！

#### 5.2 Python 脚本验证

```python
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64

# 从 Frida 获取的密钥和 IV（Hex 转 bytes）
key = bytes.fromhex('31323334353637383930616263646566')
iv = bytes.fromhex('66656463626130393837363534333231')

# 从抓包获取的密文
ciphertext = base64.b64decode('YWJjZGVmZ2hpamtsbW5vcA==')

# 解密
cipher = AES.new(key, AES.MODE_CBC, iv)
plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)

print("解密结果:", plaintext.decode())
```

#### 5.3 直接调用 App 的加密函数

```javascript
Java.perform(function () {
  var CryptoUtils = Java.use("com.example.app.CryptoUtils");

  // 调用加密函数
  var encrypted = CryptoUtils.encrypt("Hello World");
  console.log("加密结果: " + encrypted);

  // 调用解密函数
  var decrypted = CryptoUtils.decrypt(encrypted);
  console.log("解密结果: " + decrypted);
});
```

---

## 工作原理

### 常见加密算法对照表

| 算法类型       | 算法    | 密钥长度           | 用途             |
| -------------- | ------- | ------------------ | ---------------- |
| **对称加密**   | AES     | 128/192/256 bit    | 加密数据         |
|                | DES     | 56 bit             | 旧标准（不安全） |
|                | 3DES    | 168 bit            | DES 增强版       |
| **非对称加密** | RSA     | 1024/2048/4096 bit | 密钥交换、签名   |
|                | ECC     | 256/384/521 bit    | RSA 的高效替代   |
| **哈希**       | MD5     | 128 bit 输出       | 校验（不安全）   |
|                | SHA-256 | 256 bit 输出       | 安全哈希         |
|                | HMAC    | 可变               | 带密钥的哈希     |

### AES 加密流程

```text
明文数据
    ↓
[AES Encrypt] ← 使用密钥 + IV
    ↓
密文数据
    ↓
[Base64 Encode] ← 便于传输
    ↓
最终密文
```

---

## 常见问题

### ❌ 问题 1: Hook 脚本不生效

**症状**：运行 Frida 脚本后没有任何输出

**检查**：

1. **确认加密函数被调用了吗？**
    ```javascript
    Java.use("javax.crypto.Cipher").$init.overload().implementation = function () {
      console.log("[TEST] Cipher 实例化");
      return this.$init();
    };
    ```
2. **加密是否在 Native 层？**
    - 改用 Native Hook
3. **类名可能被混淆**
    - 搜索所有包含 `Cipher` 的类：
    ```javascript
    Java.enumerateLoadedClasses({
      onMatch: function (className) {
        if (className.toLowerCase().includes("cipher")) {
          console.log(className);
        }
      },
      onComplete: function () {},
    });
    ```

### ❌ 问题 2: 解密失败

**可能原因**：

1. **IV 不正确**
    - 确认是否使用了 IV
    - 某些实现会将 IV 附加在密文开头
2. **Padding 不匹配**
    - 尝试不同的 Padding：`PKCS5Padding`, `PKCS7Padding`, `NoPadding`
3. **编码问题**
    ```python
    # 尝试不同编码
    ciphertext = base64.b64decode(data)  # Base64
    ciphertext = bytes.fromhex(data)     # Hex
    ciphertext = data.encode()           # UTF-8
    ```
4. **密钥派生**
    - 可能使用了 PBKDF2 等密钥派生函数
    - Hook `SecretKeyFactory.generateSecret()` 查看

### ❌ 问题 3: Native 函数找不到

**症状**：`Module.findExportByName()` 返回 `null`

**解决**：

1. **函数可能未导出**
    ```bash
    # 查看所有符号（包括未导出）
    readelf -s libnative.so | grep encrypt
    ```
2. **使用地址偏移 Hook**
    ```javascript
    var baseAddr = Module.findBaseAddress('libnative.so');
    var funcAddr = baseAddr.add(0x1234);  // 从 IDA 获取偏移
    Interceptor.attach(funcAddr, { ... });
    ```
3. **动态注册的 JNI 方法**

```javascript
// Hook RegisterNatives
var RegisterNatives = Module.findExportByName(
  "libart.so",
  "_ZN3art3JNI15RegisterNativesEP7_JNIEnvP7_jclassPK15JNINativeMethodi"
);
Interceptor.attach(RegisterNatives, {
  onEnter: function (args) {
    var methods = ptr(args[2]);
    console.log("Register JNI Method:", methods.readCString());
  },
});
```

### ❌ 问题 4: 密钥是字符串而非字节数组

**症状**：

```java
// 看到类似这样的代码
SecretKeySpec key = new SecretKeySpec("MyPassword123".getBytes(), "AES");
```

**解决方案**：

**1. 使用密钥派生函数（KDF）**

```python
from Crypto.Protocol.KDF import PBKDF2

password = "MyPassword123"
salt = b"somesalt"  # 需要从代码中找到
key = PBKDF2(password, salt, dkLen=16)  # 16 字节 AES-128
```

**说明**：

- `PBKDF2` 会将任意长度的密码派生为固定长度的密钥
- `salt` 通常在代码中硬编码或从服务器获取
- `dkLen` 决定输出密钥长度：16 (AES-128) / 24 (AES-192) / 32 (AES-256)

**2. Hook 密钥派生函数**

```javascript
var SecretKeyFactory = Java.use("javax.crypto.SecretKeyFactory");
SecretKeyFactory.generateSecret.implementation = function (keySpec) {
  var key = this.generateSecret(keySpec);
  console.log("[密钥派生] 算法:", this.getAlgorithm());
  console.log("[密钥派生] 密钥 (Hex):", bytesToHex(key.getEncoded()));

  // 尝试获取 salt（如果是 PBEKeySpec）
  try {
    var PBEKeySpec = Java.use("javax.crypto.spec.PBEKeySpec");
    var pbeSpec = Java.cast(keySpec, PBEKeySpec);
    console.log("[密钥派生] Salt:", bytesToHex(pbeSpec.getSalt()));
    console.log("[密钥派生] 迭代次数:", pbeSpec.getIterationCount());
  } catch (e) {}

  return key;
};
```

**3. 直接使用字符串密钥**

```python
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import hashlib

# 从代码中找到的字符串密码
password = "MyPassword123"

# 方法 1: 直接使用前 16 字节
key = password.encode()[:16].ljust(16, b'\0')

# 方法 2: MD5 哈希（常见做法，输出正好 16 字节）
key = hashlib.md5(password.encode()).digest()

# 方法 3: SHA256 前 16 字节
key = hashlib.sha256(password.encode()).digest()[:16]

# 然后用于解密
cipher = AES.new(key, AES.MODE_CBC, iv)
plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
```

---

## 延伸阅读

### 相关配方

- **[网络抓包](./network_sniffing.md)** - 获取加密后的数据样本
- **[Frida 反调试](../Anti-Detection/frida_anti_debugging.md)** - 如果 App 检测到 Hook
- **[Native Hook 模式](../../01-Recipes/Scripts/native_hooking.md)** - 深入 Native 层分析

### 工具深入

- **[Frida 完整指南](../../02-Tools/Dynamic/frida_guide.md)**
- **[IDA Pro 使用](../../02-Tools/Static/ida_pro_guide.md)**

### 案例分析

> **💡 思路一句话**: 抓包拿到加密请求 → 在 jadx 中搜索加密相关类名（Cipher, MessageDigest, Mac）→ hook 加解密方法获取明文和密钥 → 用 Python 重写加密逻辑验证。

- **[音乐 App 分析](../../03-Case-Studies/case_music_apps.md)** - 加密音频格式分析
- **[社交媒体风控](../../03-Case-Studies/case_social_media_and_anti_bot.md)** - API 签名算法逆向

### 理论基础

- **[密码学基础知识](../../04-Reference/Foundations/)** - TODO

---

## 快速参考

### Hook 脚本模板库

#### 1. RSA Hook

```javascript
var Cipher = Java.use("javax.crypto.Cipher");
Cipher.init.overload("int", "java.security.Key").implementation = function (
  opmode,
  key
) {
  console.log("[RSA] 模式:", opmode == 1 ? "ENCRYPT" : "DECRYPT");
  console.log("[RSA] 密钥类型:", key.$className);

  // 获取公钥/私钥
  if (key.$className.includes("PublicKey")) {
    console.log("[RSA] 公钥:", bytesToHex(key.getEncoded()));
  } else if (key.$className.includes("PrivateKey")) {
    console.log("[RSA] 私钥:", bytesToHex(key.getEncoded()));
  }

  return this.init(opmode, key);
};
```

#### 2. HMAC Hook

```javascript
var Mac = Java.use("javax.crypto.Mac");
Mac.init.implementation = function (key) {
  console.log("[HMAC] 算法:", this.getAlgorithm());

  var secretKey = Java.cast(key, Java.use("javax.crypto.spec.SecretKeySpec"));
  console.log("[HMAC] 密钥:", bytesToHex(secretKey.getEncoded()));

  return this.init(key);
};

Mac.doFinal.overload("[B").implementation = function (data) {
  var result = this.doFinal(data);
  console.log("[HMAC] 输入:", bytesToHex(data));
  console.log("[HMAC] 输出:", bytesToHex(result));
  return result;
};
```

#### 3. Base64 Hook

```javascript
var Base64 = Java.use("android.util.Base64");
Base64.decode.overload("java.lang.String", "int").implementation = function (
  str,
  flags
) {
  var result = this.decode(str, flags);
  console.log("[Base64] 解码:");
  console.log("    输入:", str.substring(0, 50) + "...");
  console.log("    输出 (Hex):", bytesToHex(result));
  return result;
};
```

### OpenSSL 命令速查

```bash
# AES 加密
echo "Hello" | openssl enc -aes-128-cbc -K 31323334353637383930616263646566 -iv 66656463626130393837363534333231 -base64

# AES 解密
echo "密文" | base64 -d | openssl enc -d -aes-128-cbc -K 31323334353637383930616263646566 -iv 66656463626130393837363534333231

# 生成 MD5
echo -n "text" | openssl md5

# 生成 SHA256
echo -n "text" | openssl sha256

# RSA 密钥生成
openssl genrsa -out private.pem 2048
openssl rsa -in private.pem -pubout -out public.pem
```
