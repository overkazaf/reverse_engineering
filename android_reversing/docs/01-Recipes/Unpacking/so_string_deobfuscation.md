# SO 文件字符串混淆对抗指南

在 Android Native 层安全中，字符串混淆是一种用于隐藏敏感信息、增加逆向分析难度的常用技术。开发者通过对 SO 文件中的关键字符串（如 API URL、加密密钥、Shell 命令、功能开关等）进行编码或加密，可以有效防止静态分析工具（如 `strings` 命令或 IDA Pro 的字符串窗口）直接发现它们。

本文旨在系统性地介绍 SO 文件中常见的字符串混淆技术，并提供一套从静态分析到动态分析的完整对抗策略。

---

## 目录

- [字符串混淆的核心思想](#字符串混淆的核心思想)
- [常见的混淆技术](#常见的混淆技术)
- [对抗策略一：静态分析 (IDA Pro / Ghidra)](#对抗策略一静态分析-ida-pro--ghidra)
  - [识别解密/解混淆函数](#识别解密解混淆函数)
  - [定位交叉引用](#定位交叉引用)
  - [自动化脚本解密](#自动化脚本解密)
- [对抗策略二：动态分析 (Frida)](#对抗策略二动态分析-frida)
  - [Hook 解密函数（首选策略）](#hook-解密函数首选策略)
  - [内存漫游与搜索](#内存漫游与搜索)
- [总结：最高效的分析流程](#总结最高效的分析流程)

---

## 字符串混淆的核心思想

其本质是**避免将明文字符串直接存储在二进制文件的 `.rodata` 或 `.data` 段中**。取而代之的是，在程序运行时，通过特定的函数动态地在内存中（栈或堆）恢复出原始的字符串。

一个典型的流程如下：

```
加密的字节数组 -> 解密/解混淆函数 -> 内存中的明文字符串
```

我们的目标就是截获"内存中的明文字符串"。

---

## 常见的混淆技术

1. **简单编码**:
   - **Base64**: 将 Base64 编码后的字符串存储，使用时再解码。
   - **ROT13/Caesar Cipher**: 简单的字符位移。

2. **按位运算**:
   - **XOR (异或)**: 将原始字符串与一个固定的（或动态计算的）密钥进行按字节异或。这是最常见、最高效的一种方式。

3. **栈上构建**:
   - 不在任何段中存储字符串，而是在函数开始时，通过一系列 `mov` 指令逐字节地将字符串 push 到栈上。

   ```c++
   void get_secret_string() {
       char secret[12];
       secret[0] = 's';
       secret[1] = 'e';
       // ...
       secret[10] = 't';
       secret[11] = '\0';
       // use secret
   }
   ```

4. **标准加密算法**:
   - 使用如 AES, RC4, DES 等标准对称加密算法。密钥本身可能被再次混淆或从其他地方动态获取。

---

## 对抗策略一：静态分析 (IDA Pro / Ghidra)

静态分析的目标是**理解解密逻辑并自动化地应用它**。

### 识别解密/解混淆函数

**特征**: 解密函数通常具有以下一个或多个特征：

- 接受一个指向字节数组的指针和一个长度作为参数。
- 函数内部包含一个循环结构（`for` / `while`）。
- 循环内部有按位操作，特别是 `XOR` (异或) 指令。
- 函数的交叉引用（Xrefs）非常多，且调用的地方都伴随着一个数据块的地址。

**方法**: 在 IDA Pro 或 Ghidra 中，通过搜索这些代码模式，通常能很快定位到核心的解密函数。

### 定位交叉引用

一旦你识别出了解密函数（例如 `decrypt_string`），立即查看它的所有交叉引用。每一个调用 `decrypt_string` 的地方，都是一个加密字符串被使用的地方。传递给该函数的参数，就是加密的数据。

### 自动化脚本解密

这是静态分析的精髓所在。

1. **分析算法**: 仔细阅读解密函数的汇编或反编译代码，用一种高级语言（如 Python）重新实现其逻辑。

   ```python
   # 示例: Python 实现的简单 XOR 解密算法
   def decrypt_xor(data, key):
       decrypted = bytearray()
       for i in range(len(data)):
           decrypted.append(data[i] ^ key[i % len(key)])
       return decrypted.decode('utf-8')
   ```

2. **脚本逻辑**:
   1. 获取解密函数的地址。
   2. 遍历该函数的所有交叉引用。
   3. 在每个交叉引用的地方，解析其参数，提取出加密数据块的地址和长度。
   4. 读取加密数据。
   5. 调用步骤 1 中实现的 Python 解密函数。
   6. **将解密后的明文字符串，作为注释，添加到交叉引用的代码行旁边**。

3. **效果**: 运行脚本后，IDA/Ghidra 中的代码将变得非常易读，所有加密字符串都以注释的形式被"还原"了。

---

## 对抗策略二：动态分析 (Frida)

动态分析的核心思想是**不关心解密过程，只关心解密结果**。它通常更快速、更直接。

### Hook 解密函数（首选策略）

这是对抗字符串混淆**最简单、最高效**的方法。

1. **定位函数**: 使用静态分析工具（IDA/Ghidra）找到解密函数的地址。

2. **编写 Frida 脚本**:
   - **Hook `onEnter`**: 在进入解密函数时，打印其输入参数（加密的字节数组）。
   - **Hook `onLeave` (更常用)**: 在函数返回时，直接读取其返回值。因为返回值通常就是指向内存中明文字符串的指针。

   ```javascript
   const decryptFuncPtr = Module.findExportByName(
       "libnative-lib.so",
       "Java_com_example_MainActivity_decryptString"
   );
   // 或者直接使用地址:
   // const decryptFuncPtr = Module.getBaseAddress("libnative-lib.so").add(0x1234);

   Interceptor.attach(decryptFuncPtr, {
       onEnter: function(args) {
           console.log("进入 decryptString，数据: " + args[0].readCString());
       },
       onLeave: function(retval) {
           // retval 是指向解密后字符串的指针
           var decryptedString = retval.readCString();
           console.log("解密后的字符串 -> " + decryptedString);
           // 可以进一步将结果写入文件
           // send({ decrypted: decryptedString });
       }
   });
   ```

### 内存漫游与搜索

在某些情况下，App 可能会在启动时一次性解密大量字符串，并将它们存放在一个特定的内存区域。

**方法**:

1. 让 App 运行一段时间。
2. 使用 Frida 的 `Memory.scan` API 在进程的整个内存空间中搜索你感兴趣的字符串模式（例如，`https://`）。

```javascript
// 十六进制表示 "https://"
var pattern = "68 74 74 70 73 3a 2f 2f";
var module = Process.findModuleByName("libnative-lib.so");

Memory.scan(module.base, module.size, pattern, {
    onMatch: function(address, size) {
        console.log("在以下地址找到模式: " + address);
        // 可能需要回退一些字节来找到字符串的起始位置
        console.log(address.readCString());
    },
    onComplete: function() {
        console.log("内存扫描完成。");
    }
});
```

---

## 总结：最高效的分析流程

对于字符串混淆，最高效的工作流程是结合静态和动态分析：

1. **静态分析定位**: 使用 IDA Pro 或 Ghidra 快速浏览 SO 文件，识别出可能的解密/解混淆函数。

2. **动态分析验证/获取**: 使用 Frida 对上一步定位到的函数地址进行 Hook，运行 App 并观察 `onLeave` 的返回值，快速获取所有解密后的字符串。

3. **(可选) 静态分析脚本化**: 如果需要对大量字符串进行离线分析或希望得到一个带注释的、更易读的反汇编文件，再回到静态分析工具中，根据已知的算法编写自动化解密脚本。
