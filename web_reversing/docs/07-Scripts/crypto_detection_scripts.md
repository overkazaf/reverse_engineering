# 加密算法识别与检测脚本

## 概述

在 Web 逆向工程中，识别目标网站使用的加密算法是分析的第一步。通过自动化检测脚本，可以快速定位加密函数调用点、识别算法类型，并提取关键参数。本章介绍加密算法的特征识别、自动检测方法以及实战 Hook 脚本。

---

## 加密算法基础知识

### 常见加密算法分类

#### 1. 散列算法（Hash Functions）

**特点**: 单向不可逆，固定长度输出

| 算法        | 输出长度          | 特征模式                                 |
| ----------- | ----------------- | ---------------------------------------- |
| **MD5**     | 128 bit (32 hex)  | 包含 `0x67452301`, `0xEFCDAB89` 等魔数   |
| **SHA-1**   | 160 bit (40 hex)  | 包含 `0x67452301`, `0xEFCDAB89` 等初始值 |
| **SHA-256** | 256 bit (64 hex)  | 包含 `0x6A09E667`, `0xBB67AE85` 等常量   |
| **SHA-512** | 512 bit (128 hex) | 64 轮运算，特征常量数组                  |
| **SM3**     | 256 bit (64 hex)  | 国密算法，初始值 `0x7380166F`            |

#### 2. 对称加密算法（Symmetric Encryption）

**特点**: 加密和解密使用相同密钥

| 算法     | 密钥长度        | 块大小  | 特征                          |
| -------- | --------------- | ------- | ----------------------------- |
| **AES**  | 128/192/256 bit | 128 bit | S-Box 替换表，MixColumns 混淆 |
| **DES**  | 56 bit          | 64 bit  | 16 轮 Feistel 结构            |
| **3DES** | 168 bit         | 64 bit  | DES 三次迭代                  |
| **RC4**  | 40-2048 bit     | 流加密  | KSA 和 PRGA 两阶段            |
| **SM4**  | 128 bit         | 128 bit | 国密算法，32 轮非线性迭代     |

#### 3. 非对称加密算法（Asymmetric Encryption）

**特点**: 公钥加密，私钥解密

| 算法    | 密钥长度           | 应用场景           |
| ------- | ------------------ | ------------------ |
| **RSA** | 1024/2048/4096 bit | 数字签名、密钥交换 |
| **ECC** | 256/384/521 bit    | 移动设备、IoT      |
| **SM2** | 256 bit            | 国密非对称算法     |

#### 4. 编码算法（Encoding）

**注意**: 编码不是加密，可逆

| 算法           | 特征                                   |
| -------------- | -------------------------------------- |
| **Base64**     | 字符集 `A-Za-z0-9+/=`，长度是 4 的倍数 |
| **Base32**     | 字符集 `A-Z2-7=`，长度是 8 的倍数      |
| **Hex**        | 字符集 `0-9A-F`，长度是 2 的倍数       |
| **URL Encode** | 包含 `%XX` 格式                        |

---

## 加密算法特征识别

### 1. 通过代码特征识别

#### MD5 特征检测

```javascript
// 检测 MD5 算法特征
function detectMD5(code) {
  const patterns = [
    // MD5 初始化向量（魔数）
    /0x67452301/i,
    /0xEFCDAB89/i,
    /0x98BADCFE/i,
    /0x10325476/i,

    // MD5 循环移位常量
    /0xD76AA478/i,
    /0xE8C7B756/i,

    // 函数名特征
    /md5|MD5/,

    // 典型操作：F = (B & C) | (~B & D)
    /[&|~]\s*[a-z0-9_]+\s*[&|]\s*[a-z0-9_]+/,
  ];

  return patterns.some((pattern) => pattern.test(code));
}
```

#### AES 特征检测

```javascript
// 检测 AES 算法特征
function detectAES(code) {
  const patterns = [
    // S-Box 替换表特征值
    /0x63.*0x7C.*0x77.*0x7B/, // S-Box 前几个值

    // Rijndael S-Box
    /sbox|s_box|SubBytes/i,

    // 轮常量 Rcon
    /rcon|round.*const/i,

    // MixColumns 多项式
    /0x02.*0x03.*0x01.*0x01/,

    // 函数名
    /aes|AES|rijndael/i,

    // CBC、ECB 等模式
    /CBC|ECB|CTR|GCM|CFB/,
  ];

  return patterns.some((pattern) => pattern.test(code));
}
```

#### RSA 特征检测

```javascript
// 检测 RSA 算法特征
function detectRSA(code) {
  const patterns = [
    // 模幂运算
    /mod.*exp|modular.*exponentiation/i,

    // 大数运算库
    /bigint|big.*integer|jsbn/i,

    // RSA 关键字
    /rsa|RSA/,

    // 公钥指数 e (常见值：65537 = 0x10001)
    /0x10001|65537/,

    // PKCS 填充
    /pkcs.*1|oaep|pss/i,
  ];

  return patterns.some((pattern) => pattern.test(code));
}
```

### 2. 通过常量特征识别

```javascript
// 加密算法常量数据库
const CRYPTO_CONSTANTS = {
  MD5: [
    0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476, 0xd76aa478, 0xe8c7b756,
    0x242070db,
  ],

  SHA1: [0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476, 0xc3d2e1f0],

  SHA256: [
    0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c,
    0x1f83d9ab, 0x5be0cd19,
  ],

  AES_SBOX: [
    0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b,
    0xfe, 0xd7, 0xab, 0x76,
  ],

  SM3: [
    0x7380166f, 0x4914b2b9, 0x172442d7, 0xda8a0600, 0xa96f30bc, 0x163138aa,
    0xe38dee4d, 0xb0fb0e4e,
  ],
};

// 在代码中搜索这些常量
function findCryptoConstants(code) {
  const found = [];

  for (const [algo, constants] of Object.entries(CRYPTO_CONSTANTS)) {
    const hexConstants = constants.map(
      (c) => "0x" + c.toString(16).toUpperCase()
    );

    for (const constant of hexConstants) {
      if (code.includes(constant)) {
        found.push({ algorithm: algo, constant });
      }
    }
  }

  return found;
}
```

### 3. 通过输出特征识别

```javascript
// 根据输出长度判断可能的算法
function guessAlgorithmByOutputLength(output) {
  const length = output.length;

  const lengthMap = {
    32: ["MD5 (hex)", "MD4 (hex)"],
    40: ["SHA-1 (hex)", "RIPEMD-160 (hex)"],
    64: ["SHA-256 (hex)", "SM3 (hex)", "RIPEMD-256 (hex)"],
    128: ["SHA-512 (hex)", "Whirlpool (hex)"],

    // Base64 编码的长度（近似）
    24: ["MD5 (base64)"],
    28: ["SHA-1 (base64)"],
    44: ["SHA-256 (base64)"],
    88: ["SHA-512 (base64)"],
  };

  return lengthMap[length] || ["Unknown"];
}

// 测试示例
console.log(guessAlgorithmByOutputLength("5d41402abc4b2a76b9719d911017c592"));
// Output: ['MD5 (hex)', 'MD4 (hex)']
```

---

## 自动化检测脚本

### 综合加密检测脚本

```javascript
// crypto-detector.js
class CryptoDetector {
  constructor() {
    this.detectedAlgorithms = new Set();
    this.suspiciousFunctions = [];
  }

  // 扫描全局对象
  scanGlobalObjects() {
    const cryptoLibraries = [
      "CryptoJS",
      "forge",
      "sjcl",
      "crypto",
      "subtle",
      "JSEncrypt",
      "aesjs",
      "md5",
      "sha1",
      "sha256",
    ];

    cryptoLibraries.forEach((lib) => {
      if (window[lib]) {
        console.log(`✅ 发现加密库: ${lib}`);
        this.detectedAlgorithms.add(lib);
      }
    });

    // 检测 Web Crypto API
    if (window.crypto && window.crypto.subtle) {
      console.log("✅ 发现 Web Crypto API");
      this.detectedAlgorithms.add("WebCrypto");
    }
  }

  // 扫描已加载的 JS 文件
  async scanLoadedScripts() {
    const scripts = Array.from(document.scripts);

    for (const script of scripts) {
      if (!script.src) continue;

      try {
        const response = await fetch(script.src);
        const code = await response.text();

        const algorithms = this.detectAlgorithmsInCode(code);

        if (algorithms.length > 0) {
          console.log(`📜 文件: ${script.src}`);
          console.log(`   算法:`, algorithms);
        }
      } catch (e) {
        console.log(`⚠️  无法读取: ${script.src}`);
      }
    }
  }

  // 在代码中检测算法
  detectAlgorithmsInCode(code) {
    const algorithms = [];

    // 检测各种算法
    const detectors = {
      MD5: this.detectMD5,
      "SHA-1": this.detectSHA1,
      "SHA-256": this.detectSHA256,
      AES: this.detectAES,
      DES: this.detectDES,
      RSA: this.detectRSA,
      Base64: this.detectBase64,
      HMAC: this.detectHMAC,
      SM3: this.detectSM3,
      SM4: this.detectSM4,
    };

    for (const [name, detector] of Object.entries(detectors)) {
      if (detector(code)) {
        algorithms.push(name);
      }
    }

    return algorithms;
  }

  // 各种检测函数
  detectMD5(code) {
    return /0x67452301|0xEFCDAB89|0x98BADCFE|md5/i.test(code);
  }

  detectSHA1(code) {
    return /0x67452301.*0xEFCDAB89.*0x98BADCFE.*0x10325476.*0xC3D2E1F0|sha1/i.test(
      code
    );
  }

  detectSHA256(code) {
    return /0x6A09E667|0xBB67AE85|sha256/i.test(code);
  }

  detectAES(code) {
    return /aes|rijndael|SubBytes|MixColumns|0x63.*0x7C.*0x77/i.test(code);
  }

  detectDES(code) {
    return /\bdes\b|feistel|permutation.*choice/i.test(code);
  }

  detectRSA(code) {
    return /\brsa\b|modpow|0x10001|65537/i.test(code);
  }

  detectBase64(code) {
    return /base64|atob|btoa|ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789/i.test(
      code
    );
  }

  detectHMAC(code) {
    return /hmac|hash.*based.*message.*authentication/i.test(code);
  }

  detectSM3(code) {
    return /sm3|0x7380166F/i.test(code);
  }

  detectSM4(code) {
    return /sm4|0xA3B1BAC6/i.test(code);
  }

  // 生成报告
  generateReport() {
    console.log("\n=== 加密算法检测报告 ===");
    console.log(`检测到的加密库数量: ${this.detectedAlgorithms.size}`);
    console.log(`检测到的算法:`, Array.from(this.detectedAlgorithms));
  }
}

// 使用方法
const detector = new CryptoDetector();
detector.scanGlobalObjects();
detector.scanLoadedScripts().then(() => {
  detector.generateReport();
});
```

---

## 加密库 Hook 脚本

### Hook CryptoJS

```javascript
(function () {
  if (!window.CryptoJS) {
    console.log("⚠️  CryptoJS 未加载");
    return;
  }

  console.log("🎣 开始 Hook CryptoJS");

  // Hook 所有散列算法
  const hashAlgorithms = [
    "MD5",
    "SHA1",
    "SHA256",
    "SHA512",
    "SHA3",
    "RIPEMD160",
  ];

  hashAlgorithms.forEach((algo) => {
    if (CryptoJS[algo]) {
      const original = CryptoJS[algo];
      CryptoJS[algo] = function (message) {
        console.log(`🔐 [CryptoJS.${algo}]`);
        console.log(`   输入:`, message.toString());

        const result = original.apply(this, arguments);

        console.log(`   输出:`, result.toString());
        console.trace();

        return result;
      };
    }
  });

  // Hook AES 加密
  if (CryptoJS.AES) {
    const originalEncrypt = CryptoJS.AES.encrypt;
    const originalDecrypt = CryptoJS.AES.decrypt;

    CryptoJS.AES.encrypt = function (message, key, cfg) {
      console.log("🔐 [CryptoJS.AES.encrypt]");
      console.log("   明文:", message.toString());
      console.log("   密钥:", key.toString());
      console.log("   配置:", cfg);

      const result = originalEncrypt.apply(this, arguments);

      console.log("   密文:", result.toString());
      console.log("   Base64:", result.toString());
      console.trace();

      return result;
    };

    CryptoJS.AES.decrypt = function (ciphertext, key, cfg) {
      console.log("🔓 [CryptoJS.AES.decrypt]");
      console.log("   密文:", ciphertext.toString());
      console.log("   密钥:", key.toString());

      const result = originalDecrypt.apply(this, arguments);

      console.log("   明文:", result.toString(CryptoJS.enc.Utf8));
      console.trace();

      return result;
    };
  }

  // Hook HMAC
  if (CryptoJS.HmacSHA256) {
    const originalHmac = CryptoJS.HmacSHA256;
    CryptoJS.HmacSHA256 = function (message, key) {
      console.log("🔐 [CryptoJS.HmacSHA256]");
      console.log("   消息:", message.toString());
      console.log("   密钥:", key.toString());

      const result = originalHmac.apply(this, arguments);

      console.log("   HMAC:", result.toString());

      return result;
    };
  }

  console.log("✅ CryptoJS Hook 完成");
})();
```

### Hook Web Crypto API

```javascript
(function () {
  if (!window.crypto || !window.crypto.subtle) {
    console.log("⚠️  Web Crypto API 不可用");
    return;
  }

  console.log("🎣 开始 Hook Web Crypto API");

  const subtle = window.crypto.subtle;

  // Hook encrypt
  const originalEncrypt = subtle.encrypt;
  subtle.encrypt = async function (algorithm, key, data) {
    console.log("🔐 [crypto.subtle.encrypt]");
    console.log("   算法:", algorithm);
    console.log("   密钥:", key);
    console.log("   数据长度:", data.byteLength, "bytes");

    // 转换为可读格式
    const dataArray = new Uint8Array(data);
    console.log("   数据（前100字节）:", Array.from(dataArray.slice(0, 100)));

    const result = await originalEncrypt.apply(this, arguments);

    console.log("   密文长度:", result.byteLength, "bytes");
    console.trace();

    return result;
  };

  // Hook decrypt
  const originalDecrypt = subtle.decrypt;
  subtle.decrypt = async function (algorithm, key, data) {
    console.log("🔓 [crypto.subtle.decrypt]");
    console.log("   算法:", algorithm);
    console.log("   密钥:", key);
    console.log("   密文长度:", data.byteLength, "bytes");

    const result = await originalDecrypt.apply(this, arguments);

    const plaintext = new Uint8Array(result);
    console.log("   明文:", new TextDecoder().decode(plaintext));

    return result;
  };

  // Hook digest
  const originalDigest = subtle.digest;
  subtle.digest = async function (algorithm, data) {
    console.log("🔐 [crypto.subtle.digest]");
    console.log("   算法:", algorithm);

    const dataArray = new Uint8Array(data);
    const text = new TextDecoder().decode(dataArray);
    console.log("   输入:", text);

    const result = await originalDigest.apply(this, arguments);

    // 转换为 Hex
    const hashArray = Array.from(new Uint8Array(result));
    const hashHex = hashArray
      .map((b) => b.toString(16).padStart(2, "0"))
      .join("");
    console.log("   哈希:", hashHex);

    return result;
  };

  // Hook sign
  const originalSign = subtle.sign;
  subtle.sign = async function (algorithm, key, data) {
    console.log("🔐 [crypto.subtle.sign]");
    console.log("   算法:", algorithm);
    console.log("   密钥:", key);

    const result = await originalSign.apply(this, arguments);

    const sigArray = Array.from(new Uint8Array(result));
    const sigHex = sigArray
      .map((b) => b.toString(16).padStart(2, "0"))
      .join("");
    console.log("   签名:", sigHex);

    return result;
  };

  console.log("✅ Web Crypto API Hook 完成");
})();
```

### Hook JSEncrypt (RSA)

```javascript
(function () {
  if (!window.JSEncrypt) {
    console.log("⚠️  JSEncrypt 未加载");
    return;
  }

  console.log("🎣 开始 Hook JSEncrypt");

  const originalEncrypt = JSEncrypt.prototype.encrypt;
  const originalDecrypt = JSEncrypt.prototype.decrypt;

  JSEncrypt.prototype.encrypt = function (text) {
    console.log("🔐 [JSEncrypt.encrypt]");
    console.log("   明文:", text);
    console.log("   公钥:", this.getPublicKey());

    const result = originalEncrypt.apply(this, arguments);

    console.log("   密文:", result);
    console.trace();

    return result;
  };

  JSEncrypt.prototype.decrypt = function (text) {
    console.log("🔓 [JSEncrypt.decrypt]");
    console.log("   密文:", text);

    const result = originalDecrypt.apply(this, arguments);

    console.log("   明文:", result);

    return result;
  };

  console.log("✅ JSEncrypt Hook 完成");
})();
```

---

## 实战案例

### 案例 1: 识别某电商网站的签名算法

**场景**: 某电商网站的 API 请求包含签名参数 `sign`

**步骤 1: 检测加密库**

```javascript
const detector = new CryptoDetector();
detector.scanGlobalObjects();
// 输出: ✅ 发现加密库: CryptoJS
```

**步骤 2: Hook CryptoJS**

发现调用了 `CryptoJS.MD5`：

```
🔐 [CryptoJS.MD5]
   输入: timestamp=1638360000&user_id=123456&secret=abc123
   输出: 5d41402abc4b2a76b9719d911017c592
```

**步骤 3: 分析签名逻辑**

```javascript
// 还原签名函数
function generateSign(timestamp, userId, secret) {
  const str = `timestamp=${timestamp}&user_id=${userId}&secret=${secret}`;
  return CryptoJS.MD5(str).toString();
}
```

### 案例 2: 破解 AES 加密的请求参数

**场景**: 请求体是加密的 Base64 字符串

**步骤 1: Hook CryptoJS.AES**

```
🔐 [CryptoJS.AES.encrypt]
   明文: {"user":"admin","password":"123456"}
   密钥: my-secret-key-16
   配置: {mode: CBC, iv: ...}
   密文: U2FsdGVkX1+... (Base64)
```

**步骤 2: 提取加密参数**

- 算法: AES-CBC
- 密钥: `my-secret-key-16`
- IV: (从配置中提取)
- 模式: CBC

**步骤 3: Python 复现**

```python
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64

def aes_encrypt(plaintext, key, iv):
    cipher = AES.new(key.encode(), AES.MODE_CBC, iv.encode())
    ciphertext = cipher.encrypt(pad(plaintext.encode(), AES.block_size))
    return base64.b64encode(ciphertext).decode()

# 使用
key = 'my-secret-key-16'
iv = '...'  # 从 Hook 结果中获取
data = '{"user":"admin","password":"123456"}'
encrypted = aes_encrypt(data, key, iv)
```

---

## 工具集成

### 浏览器插件检测

可以将检测脚本集成到浏览器插件中，实现自动化分析：

```javascript
// content-script.js
chrome.runtime.sendMessage({
  type: "crypto_detected",
  algorithms: detector.detectedAlgorithms,
});
```

### Node.js 静态分析

```javascript
const fs = require("fs");
const detector = new CryptoDetector();

const code = fs.readFileSync("target.js", "utf-8");
const algorithms = detector.detectAlgorithmsInCode(code);

console.log("检测到的算法:", algorithms);
```

---

## 最佳实践

1. **多层检测**: 结合全局对象扫描、代码特征匹配、常量识别
2. **动态 Hook**: 优先使用 Hook 脚本捕获运行时调用
3. **静态分析**: 对混淆代码先反混淆再检测
4. **交叉验证**: 通过输入输出特征验证算法识别结果
5. **保存证据**: 记录完整的加密参数（密钥、IV、模式等）

---

## 相关工具

| 工具                | 功能                   | 链接                                                                 |
| ------------------- | ---------------------- | -------------------------------------------------------------------- |
| **hash-identifier** | 哈希类型识别           | https://github.com/blackploit/hash-identifier                        |
| **CyberChef**       | 综合加密分析           | https://gchq.github.io/CyberChef/                                    |
| **Ciphey**          | 自动解密工具           | https://github.com/Ciphey/Ciphey                                     |
| **findcrypt**       | IDA 插件，查找加密常量 | https://github.com/you0708/ida/tree/master/idapython_tools/findcrypt |

---

## 商业化解决方案对比

在企业级 Web 逆向项目中，除了开源工具，还有多种商业化解决方案可选。以下是专业工具和服务的详细对比。

### 1. 商业加密分析工具

#### IDA Pro + Hex-Rays (Binary Analysis)

**适用场景**: 深度二进制分析、WASM 逆向、复杂加密算法识别

**优势**:

- 业界标准的反汇编工具
- 强大的 F5 反编译功能
- 丰富的插件生态（findcrypt、IDAScope）
- 支持多种架构（x86、ARM、MIPS、WASM）

**劣势**:

- 价格昂贵（个人版 $385，专业版 $1,879+）
- 学习曲线陡峭
- 主要针对二进制，JavaScript 分析需配合其他工具

**官网**: https://hex-rays.com/ida-pro/

**替代方案**: Ghidra（免费，NSA 开源）、Binary Ninja

---

#### JEB Decompiler

**适用场景**: Android/JavaScript 混合逆向、DEX 分析

**优势**:

- 优秀的 Android DEX 反编译
- 支持 JavaScript/TypeScript 分析
- 交互式反混淆
- 内置调试器

**价格**: 个人版 $99/月，专业版 $249/月

**官网**: https://www.pnfsoftware.com/

---

### 2. 商业加密识别服务

#### Detect It Easy (DiE)

**类型**: 免费工具（商业级质量）

**功能**:

- 自动识别 PE/ELF/Mach-O 文件中的加密算法
- 检测加壳/混淆技术
- 签名数据库持续更新

**适用于**: Windows/Linux 二进制分析

**GitHub**: https://github.com/horsicq/Detect-It-Easy

---

#### Fortify Static Code Analyzer

**类型**: 企业级静态代码分析

**功能**:

- 自动检测代码中的加密弱点
- 识别不安全的加密实现
- 合规性检查（OWASP、PCI DSS）

**价格**: 企业定价（年费 $50,000+）

**官网**: https://www.microfocus.com/en-us/cyberres/application-security/static-code-analyzer

**开源替代**: Semgrep、SonarQube

---

### 3. 云端加密分析平台

#### VirusTotal Intelligence

**功能**:

- 自动识别恶意软件中的加密算法
- 大规模样本库交叉分析
- API 接口集成

**价格**:

- 免费版：有限查询
- 高级版：$500/月起

**官网**: https://www.virustotal.com/

**应用**: 样本快速分析、加密特征库查询

---

#### Hybrid Analysis

**功能**:

- 沙箱动态分析
- 自动提取加密密钥
- 网络流量解密

**价格**:

- 免费社区版
- 企业版：定制化定价

**官网**: https://www.hybrid-analysis.com/

---

### 4. 专业咨询服务

#### Trail of Bits (安全咨询)

**服务内容**:

- 定制化加密算法逆向
- 智能合约审计
- 协议分析

**典型项目**: $20,000 - $200,000

**官网**: https://www.trailofbits.com/

---

#### NCC Group (Cryptography Services)

**服务内容**:

- 加密协议设计审查
- 密码学实现审计
- 侧信道攻击测试

**官网**: https://www.nccgroup.com/

---

### 5. 开源 vs 商业方案对比

| 维度           | 开源方案    | 商业方案              |
| -------------- | ----------- | --------------------- |
| **成本**       | 免费        | $100/月 - $50,000/年+ |
| **学习曲线**   | 中等        | 较低（有支持）        |
| **功能完整性** | 基础-中等   | 高级-企业级           |
| **更新频率**   | 社区驱动    | 定期更新 + 技术支持   |
| **适用规模**   | 个人-小团队 | 中大型企业            |
| **法律合规**   | 需自行审查  | 提供合规保证          |
| **技术支持**   | 社区论坛    | 7x24 专业支持         |

---

### 6. 推荐技术选型

#### 个人学习/小团队

**方案**:

- CyberChef（在线分析）
- Ciphey（自动解密）
- 自建检测脚本

**成本**: $0

---

#### 初创公司/中小企业

**方案**:

- JEB Decompiler（$99-249/月）
- VirusTotal Intelligence（$500/月）
- 开源工具 + 商业工具组合

**成本**: $1,000-3,000/月

---

#### 大型企业/安全公司

**方案**:

- IDA Pro 团队许可
- Fortify/Checkmarx 企业版
- 专业咨询服务（按需）

**成本**: $50,000-200,000/年

---

### 7. 新兴趋势：AI 驱动的加密分析

#### Anthropic Claude/OpenAI GPT (LLM 辅助)

**应用场景**:

- 代码片段快速分析
- 加密算法识别辅助
- 伪代码生成

**局限性**:

- 无法处理大规模代码
- 可能产生误判
- 不适合保密项目

**成本**: API 调用费用（$0.01-0.06/1K tokens）

---

#### Zerocopter AI Code Analysis

**功能**:

- AI 驱动的漏洞检测
- 自动识别加密弱点
- 智能推荐修复方案

**状态**: 测试阶段

---

### 8. 实际案例对比

#### 案例: 某金融 APP 加密逆向

**需求**: 识别并复现交易签名算法

**方案 A（开源）**:

- 工具: Frida + 自写 Hook 脚本
- 时间: 3-5 天
- 成本: $0
- 风险: 需要专业技能

**方案 B（商业）**:

- 工具: JEB Decompiler + Trail of Bits 咨询
- 时间: 1-2 天
- 成本: $5,000-15,000
- 风险: 低，有专业保障

**结论**: 紧急项目或缺乏经验时，商业方案 ROI 更高

---

## 相关章节

- [JavaScript Hook 脚本](javascript_hook_scripts.md)
- [调试技巧与断点设置](../03-Basic-Recipes/debugging_techniques.md)
- [常见加密算法分析](../03-Algorithms/common_crypto_algorithms.md)
