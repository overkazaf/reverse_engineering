---
title: "SO 文件字符串混淆对抗指南"
date: 2025-01-19
type: posts
tags: ["Native层", "签名验证", "Frida", "Ghidra", "DEX", "加固"]
weight: 10
---

# SO 文件字符串混淆对抗指南

> **📚 前置知识**
>
> 本配方涉及以下核心技术，建议先阅读相关章节：
>
> - **[SO/ELF 格式](../../04-Reference/Foundations/so_elf_format.md)** - 理解 .rodata 段与字符串存储
> - **[Frida Native Hook](../../02-Tools/Dynamic/frida_guide.md#native-hook)** - 动态拦截解密函数

在 Android Native 层安全中，字符串混淆是一种用于隐藏敏感信息、增加逆向分析难度的常用技术。开发者通过对 SO 文件中的关键字符串（如 API URL、加密密钥、Shell 命令、功能开关等）进行编码或加密，可以有效防止静态分析工具（如 `strings` 命令或 IDA Pro 的字符串窗口）直接发现它们。

本文旨在系统性地介绍 SO 文件中常见的字符串混淆技术，并提供一套从静态分析到动态分析的完整对抗策略。

---

## 字符串混淆的核心思想

其本质是**避免将明文字符串直接存储在二进制文件的 `.rodata` 或 `.data` 段中**。取而代之的是，在程序运行时，通过特定的函数动态地在内存中（栈或堆）恢复出原始的字符串。

一个典型的流程如下：

```text
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

## 对抗策略三：IDA Pro 自动化脚本

当你已经理解了解密算法，可以编写 IDA Python 脚本批量解密所有字符串并添加注释。

### 示例：XOR 解密脚本

```python
import idautils
import idaapi
import idc

class StringDecryptor:
    """IDA Pro 字符串批量解密器"""

    def __init__(self, decrypt_func_addr, xor_key):
        self.decrypt_func = decrypt_func_addr
        self.xor_key = xor_key

    def xor_decrypt(self, data):
        """XOR 解密"""
        result = bytearray()
        for i, b in enumerate(data):
            result.append(b ^ self.xor_key[i % len(self.xor_key)])
        return result.decode('utf-8', errors='ignore').rstrip('\x00')

    def get_encrypted_data(self, call_addr):
        """
        从调用点提取加密数据的地址和长度
        假设调用约定: decrypt_string(encrypted_ptr, length)
        """
        # 回溯查找参数设置指令
        prev_head = idc.prev_head(call_addr)
        encrypted_ptr = None
        length = None

        # 简化处理：向前查找 MOV 指令
        for _ in range(10):
            mnem = idc.print_insn_mnem(prev_head)
            if mnem in ['MOV', 'LDR', 'LEA']:
                op0 = idc.get_operand_value(prev_head, 0)
                op1 = idc.get_operand_value(prev_head, 1)
                # 根据寄存器判断是哪个参数
                # 这里需要根据实际情况调整
            prev_head = idc.prev_head(prev_head)

        return encrypted_ptr, length

    def process_all_xrefs(self):
        """处理解密函数的所有交叉引用"""
        decrypted_count = 0

        for xref in idautils.XrefsTo(self.decrypt_func):
            call_addr = xref.frm

            # 获取加密数据
            try:
                encrypted_ptr, length = self.get_encrypted_data(call_addr)
                if encrypted_ptr and length:
                    # 读取加密数据
                    encrypted_data = idc.get_bytes(encrypted_ptr, length)
                    if encrypted_data:
                        # 解密
                        decrypted = self.xor_decrypt(encrypted_data)
                        # 添加注释
                        idc.set_cmt(call_addr, f'Decrypted: "{decrypted}"', 0)
                        print(f"[+] 0x{call_addr:x}: {decrypted}")
                        decrypted_count += 1
            except Exception as e:
                print(f"[-] 0x{call_addr:x}: 处理失败 - {e}")

        print(f"\n[*] 共解密 {decrypted_count} 个字符串")

# 使用示例
if __name__ == "__main__":
    # 配置解密函数地址和密钥
    DECRYPT_FUNC = 0x12340  # 替换为实际地址
    XOR_KEY = bytes([0x5A, 0x3C, 0x7B, 0x2E])  # 替换为实际密钥

    decryptor = StringDecryptor(DECRYPT_FUNC, XOR_KEY)
    decryptor.process_all_xrefs()
```

### 示例：通用解密框架

```python
import idaapi
import idautils
import idc

def find_decrypt_functions():
    """
    自动识别可能的解密函数
    特征：高交叉引用数 + 包含 XOR 操作 + 循环结构
    """
    candidates = []

    for func_ea in idautils.Functions():
        xref_count = len(list(idautils.XrefsTo(func_ea)))

        # 高交叉引用数是解密函数的典型特征
        if xref_count < 10:
            continue

        # 检查是否包含 XOR 指令
        has_xor = False
        has_loop = False

        for head in idautils.Heads(func_ea, idc.find_func_end(func_ea)):
            mnem = idc.print_insn_mnem(head)
            if mnem == 'EOR' or mnem == 'XOR':  # ARM: EOR, x86: XOR
                has_xor = True
            if mnem in ['B', 'JMP', 'BNE', 'JNE']:  # 循环跳转
                target = idc.get_operand_value(head, 0)
                if target < head:  # 向后跳转（循环特征）
                    has_loop = True

        if has_xor and has_loop:
            func_name = idc.get_func_name(func_ea)
            candidates.append({
                'addr': func_ea,
                'name': func_name,
                'xrefs': xref_count
            })
            print(f"[*] 候选解密函数: {func_name} @ 0x{func_ea:x} (xrefs: {xref_count})")

    return candidates

# 运行识别
find_decrypt_functions()
```

---

## 对抗策略四：Ghidra 脚本解密

Ghidra 的 Java/Python API 同样可以实现自动化解密。

### Ghidra Python 脚本示例

```python
# Ghidra 脚本：批量解密字符串
# 在 Ghidra Script Manager 中运行

from ghidra.program.model.symbol import RefType
from ghidra.program.model.listing import CodeUnit

def xor_decrypt(data, key):
    """XOR 解密"""
    result = []
    for i, b in enumerate(data):
        result.append(chr(b ^ key[i % len(key)]))
    return ''.join(result).rstrip('\x00')

def get_bytes_at(addr, size):
    """读取指定地址的字节"""
    bytes_list = []
    for i in range(size):
        b = getByte(addr.add(i))
        bytes_list.append(b & 0xFF)
    return bytes_list

def process_decrypt_function(decrypt_func_addr, xor_key):
    """处理解密函数的所有引用"""
    func = getFunctionAt(toAddr(decrypt_func_addr))
    if not func:
        print("[-] 未找到函数")
        return

    # 获取所有调用点
    refs = getReferencesTo(func.getEntryPoint())

    for ref in refs:
        if ref.getReferenceType() == RefType.UNCONDITIONAL_CALL:
            call_addr = ref.getFromAddress()

            # 这里需要分析调用点的参数
            # 简化示例：假设加密数据地址在调用前的某个指令中
            print(f"[*] 调用点: {call_addr}")

            # 添加注释（示例）
            # codeUnit = currentProgram.getListing().getCodeUnitAt(call_addr)
            # codeUnit.setComment(CodeUnit.EOL_COMMENT, "Decrypted: xxx")

# 配置
DECRYPT_FUNC = 0x12340
XOR_KEY = [0x5A, 0x3C, 0x7B, 0x2E]

process_decrypt_function(DECRYPT_FUNC, XOR_KEY)
```

---

## 对抗策略五：Unidbg 模拟执行

当解密算法过于复杂，或者涉及多层加密时，使用 Unidbg 直接调用 SO 中的解密函数是最稳妥的方法。

### Unidbg 解密框架

```java
import com.github.unidbg.AndroidEmulator;
import com.github.unidbg.linux.android.AndroidEmulatorBuilder;
import com.github.unidbg.linux.android.dvm.*;
import com.github.unidbg.Module;
import com.github.unidbg.pointer.UnidbgPointer;
import com.sun.jna.Pointer;

public class StringDecryptor extends AbstractJni {
    private final AndroidEmulator emulator;
    private final VM vm;
    private final Module module;

    // 解密函数的偏移地址
    private static final long DECRYPT_FUNC_OFFSET = 0x1234;

    public StringDecryptor() {
        // 创建模拟器
        emulator = AndroidEmulatorBuilder
                .for32Bit()
                .setProcessName("com.example.app")
                .build();

        // 创建 Dalvik VM
        vm = emulator.createDalvikVM();
        vm.setJni(this);
        vm.setVerbose(false);

        // 加载 SO 文件
        DalvikModule dm = vm.loadLibrary("native-lib", true);
        module = dm.getModule();

        // 调用 JNI_OnLoad
        dm.callJNI_OnLoad(emulator);
    }

    /**
     * 调用 Native 解密函数
     * @param encryptedData 加密的数据
     * @return 解密后的字符串
     */
    public String decrypt(byte[] encryptedData) {
        // 分配内存存放加密数据
        UnidbgPointer inputPtr = emulator.getMemory().malloc(encryptedData.length, false).getPointer();
        inputPtr.write(0, encryptedData, 0, encryptedData.length);

        // 分配输出缓冲区
        UnidbgPointer outputPtr = emulator.getMemory().malloc(encryptedData.length, false).getPointer();

        // 调用解密函数
        // 假设函数签名: void decrypt(char* input, int len, char* output)
        long funcAddr = module.base + DECRYPT_FUNC_OFFSET;
        Number result = module.callFunction(
                emulator,
                funcAddr,
                inputPtr,
                encryptedData.length,
                outputPtr
        );

        // 读取解密结果
        String decrypted = outputPtr.getString(0);
        return decrypted;
    }

    /**
     * 批量解密
     */
    public void decryptAll(byte[][] encryptedStrings) {
        for (int i = 0; i < encryptedStrings.length; i++) {
            String result = decrypt(encryptedStrings[i]);
            System.out.printf("[%d] %s%n", i, result);
        }
    }

    public static void main(String[] args) {
        StringDecryptor decryptor = new StringDecryptor();

        // 从 IDA 中提取的加密字符串
        byte[][] encrypted = {
            {0x5A, 0x3C, 0x7B, 0x2E, 0x00},  // 示例数据
            {0x1F, 0x2E, 0x3D, 0x4C, 0x00},
        };

        decryptor.decryptAll(encrypted);
    }
}
```

### Unidbg + Frida 联动

先用 Frida 收集加密字符串，再用 Unidbg 批量解密：

```python
# 步骤 1: Frida 脚本收集加密数据
frida_script = """
var encryptedStrings = [];

Interceptor.attach(Module.findBaseAddress("libnative.so").add(0x1234), {
    onEnter: function(args) {
        var ptr = args[0];
        var len = args[1].toInt32();
        var data = ptr.readByteArray(len);
        encryptedStrings.push({
            address: ptr,
            data: Array.from(new Uint8Array(data))
        });
    }
});

// 导出收集的数据
rpc.exports = {
    getEncryptedStrings: function() {
        return encryptedStrings;
    }
};
"""

# 步骤 2: 将收集的数据传给 Unidbg 解密
# (见上面的 Java 代码)
```

---

## 对抗策略六：常见混淆库识别

了解常见的混淆库及其特征，可以加速分析过程。

### 常见混淆库特征

| 混淆库 | 识别特征 | 解密方法 |
|--------|----------|----------|
| **字节跳动 SDK** | 函数名含 `_ss_`，字符串表在 `.data` 段末尾 | Hook `ss_decrypt` 系列函数 |
| **腾讯乐固** | `libshell*.so`，`classes.dex` 加密 | 需要先脱壳，再分析字符串 |
| **360 加固** | `libjiagu.so`，自定义 linker | 等待解密后 dump 内存 |
| **网易易盾** | `libNetHTProtect.so` | Hook 初始化后的字符串访问 |
| **梆梆加固** | `libDexHelper.so`，多层解密 | 逐层分析，可能需要多次 dump |

### 快速识别脚本

```python
# Frida 脚本：识别常见加固/混淆
var signatures = {
    "字节跳动": ["_ss_", "libsscronet.so"],
    "腾讯乐固": ["libshell", "libBugly"],
    "360加固": ["libjiagu", "lib360"],
    "网易易盾": ["libNetHTProtect", "libnesec"],
    "梆梆加固": ["libDexHelper", "libSecShell"]
};

function identifyProtection() {
    var modules = Process.enumerateModules();

    for (var sdk in signatures) {
        var patterns = signatures[sdk];
        for (var i = 0; i < modules.length; i++) {
            for (var j = 0; j < patterns.length; j++) {
                if (modules[i].name.indexOf(patterns[j]) !== -1) {
                    console.log("[!] 检测到: " + sdk);
                    console.log("    模块: " + modules[i].name);
                    return sdk;
                }
            }
        }
    }
    console.log("[*] 未识别到常见加固");
    return null;
}

identifyProtection();
```

---

## 高级技巧与注意事项

### 1. 处理动态密钥

有些混淆方案使用动态生成的密钥，例如基于设备 ID、时间戳等：

```javascript
// Frida: Hook 密钥生成函数
Interceptor.attach(Module.findExportByName("libnative.so", "generateKey"), {
    onLeave: function(retval) {
        console.log("[*] 动态密钥: " + retval.readCString());
        // 保存密钥供后续分析
    }
});
```

### 2. 处理多层加密

当字符串经过多层加密时，需要逐层分析：

```javascript
// Frida: 追踪多层解密
var decryptLayers = [];

function hookDecryptLayer(funcAddr, layerName) {
    Interceptor.attach(funcAddr, {
        onEnter: function(args) {
            this.input = args[0].readByteArray(32);
        },
        onLeave: function(retval) {
            var output = retval.readByteArray(32);
            decryptLayers.push({
                layer: layerName,
                input: this.input,
                output: output
            });
            console.log("[" + layerName + "] " + hexdump(output));
        }
    });
}

// Hook 所有解密层
hookDecryptLayer(base.add(0x1000), "Base64Decode");
hookDecryptLayer(base.add(0x2000), "XORDecrypt");
hookDecryptLayer(base.add(0x3000), "AESDecrypt");
```

### 3. 内存 Dump 时机

对于在 `JNI_OnLoad` 或 `.init_array` 中解密字符串的情况：

```javascript
// 在 SO 加载完成后立即 dump
Interceptor.attach(Module.findExportByName(null, "android_dlopen_ext"), {
    onLeave: function(retval) {
        var module = Process.findModuleByName("libtarget.so");
        if (module) {
            // 此时字符串可能已解密到内存
            console.log("[*] SO 已加载，开始 dump");
            dumpDecryptedStrings(module);
        }
    }
});
```

---

## 总结：最高效的分析流程

对于字符串混淆，推荐以下工作流程：

```text
┌─────────────────────────────────────────────────────────────────┐
│  1. 快速识别                                                      │
│     └─ 使用识别脚本判断是否为已知加固/混淆库                         │
├─────────────────────────────────────────────────────────────────┤
│  2. 静态分析定位                                                   │
│     ├─ IDA/Ghidra 搜索高交叉引用 + XOR 特征的函数                   │
│     └─ 识别解密函数签名和调用约定                                    │
├─────────────────────────────────────────────────────────────────┤
│  3. 动态验证                                                       │
│     ├─ Frida Hook 解密函数，确认算法正确性                           │
│     └─ 收集加密数据样本和解密结果                                    │
├─────────────────────────────────────────────────────────────────┤
│  4. 选择解密方案                                                   │
│     ├─ 简单算法 → IDA/Ghidra 脚本批量解密并注释                      │
│     ├─ 复杂算法 → Unidbg 模拟执行                                   │
│     └─ 实时需求 → Frida 持续 Hook                                   │
├─────────────────────────────────────────────────────────────────┤
│  5. 输出结果                                                       │
│     ├─ IDB/Ghidra 项目带完整注释                                    │
│     ├─ 解密字符串映射表 (地址 → 明文)                                │
│     └─ 可复用的解密脚本/工具                                        │
└─────────────────────────────────────────────────────────────────┘
```

### 工具选择建议

| 场景 | 推荐工具 | 理由 |
|------|----------|------|
| 快速获取明文 | Frida Hook | 最快，无需理解算法 |
| 离线批量分析 | IDA Python 脚本 | 可保存带注释的项目 |
| 复杂/未知算法 | Unidbg | 直接调用原函数，100% 正确 |
| 需要修改二进制 | Ghidra + Patch | 可导出修改后的 SO |
| 研究算法细节 | IDA + 手动分析 | 理解完整逻辑 |
