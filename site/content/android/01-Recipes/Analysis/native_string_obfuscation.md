---
title: "Native 层字符串混淆与逆向"
date: 2024-12-01
type: posts
tags: ["Native层", "Ghidra", "逆向分析", "Frida", "加密分析", "Hook"]
weight: 10
---

# Native 层字符串混淆与逆向

> **📚 前置知识**
>
> 本配方涉及以下核心技术，建议先阅读相关章节：
>
> - **[SO/ELF 格式](../../04-Reference/Foundations/so_elf_format.md)** - 理解 .rodata 段与符号表
> - **[IDA Pro 指南](../../02-Tools/Static/ida_pro_guide.md)** - 使用 IDA 进行静态分析

---

## 1. Native 字符串混淆概述

在 Android Native 开发（C/C++）中，直接将明文字符串硬编码在代码中会带来安全风险。静态分析工具（如 IDA Pro、Ghidra）可以轻易地在二进制文件的 `.rodata`（只读数据）段中找到这些字符串，从而泄露 API 地址、加密密钥、敏感校验逻辑等信息。因此，开发者通常会采用各种字符串混淆技术来保护这些数据。

### 1.1 为什么要混淆字符串

字符串是逆向分析中最重要的线索之一。逆向工程师拿到 SO 文件后，往往第一步就是查看字符串表：

| 泄露类型 | 示例 | 风险等级 |
|----------|------|---------|
| API 端点 | `https://api.example.com/v2/auth` | 高 - 暴露服务端接口 |
| 加密密钥 | `AES_KEY_2024_PROD` | 严重 - 直接破解加密 |
| 调试信息 | `verify_signature failed at step 3` | 中 - 暴露校验逻辑 |
| 协议格式 | `{"cmd":"login","token":"%s"}` | 高 - 暴露通信协议 |
| License 校验 | `license_expired` / `trial_version` | 中 - 定位破解点 |

常见需要混淆的场景包括：支付 SDK（密钥、回调地址）、DRM 保护（License 服务器）、反外挂系统（检测特征串）、加固壳（自身配置）、协议加密（字段名）。

还原混淆字符串的目标是 **批量地、自动化地** 恢复明文，从而快速理解函数用途、定位关键逻辑、辅助协议分析。

---

## 2. 常见混淆方式

### 2.1 XOR 加密

最常见的字符串混淆方式，编译时异或加密，运行时异或还原：

```cpp
// 单字节 XOR：对 "secret_key" 每个字节 XOR 0xAB
char encrypted[] = { 0xD8, 0xC4, 0xC2, 0xCD, 0xC4, 0xD1, 0xDF, 0xCB, 0xC4, 0xD8, 0x00 };

char* decrypt_string(char* data, int len, char key) {
    for (int i = 0; i < len; i++)
        data[i] ^= key;
    return data;
}
```

多字节变体使用密钥轮转：`data[i] ^= key[i % key_len]`，安全性更高但本质不变。

**特点**：实现简单、开销极低；单字节密钥可被频率分析破解，IDA 中 XOR 循环特征明显。

### 2.2 栈上动态构造 (Stack-based Construction)

避免在数据段中留下完整字符串，运行时逐字节在栈上构造：

```cpp
void get_secret_url() {
    char url[20];
    url[0] = 'h'; url[1] = 't'; url[2] = 't'; url[3] = 'p';
    url[4] = 's'; url[5] = ':'; url[6] = '/'; url[7] = '/';
    url[8] = 'a'; url[9] = 'p'; url[10] = 'i'; url[11] = '.';
    url[12] = 'e'; url[13] = 'x'; url[14] = 'a'; url[15] = 'm';
    url[16] = 'p'; url[17] = 'l'; url[18] = 'e';
    url[19] = '\0';
}
```

编译器优化后常将多个字节合并为 64 位存储：

```asm
MOV     X8, #0x2F2F3A7370747468   ; "https://"
STR     X8, [SP, #0x10]
MOV     X8, #0x2E6970612F        ; "/api."
STR     X8, [SP, #0x18]
```

**特点**：`.rodata` 中无完整字符串；反编译器中表现为大量连续赋值。

### 2.3 自定义编码

开发者自行设计的方案，如自定义字母表 Base64、S-Box 查表替换等。分析时需要逆向编码算法本身。

### 2.4 编译期加密 (constexpr)

利用 C++11/14 的 `constexpr` 在编译期完成加密：

```cpp
template <int N>
struct ObfuscatedString {
    char data[N];
    static constexpr char KEY = 0x55;
    constexpr ObfuscatedString(const char (&str)[N]) : data{} {
        for (int i = 0; i < N; i++) data[i] = str[i] ^ KEY;
    }
    char* decrypt() {
        for (int i = 0; i < N; i++) data[i] ^= KEY;
        return data;
    }
};

#define OBF(str) []{ \
    constexpr auto s = ObfuscatedString<sizeof(str)>(str); \
    static auto copy = s; return copy.decrypt(); }()

const char* url = OBF("https://api.example.com");
```

常见于开源混淆库：`obfuscate.h`、`ADVobfuscator`、`skCrypter`。编译产物中只有密文，源码保持可读。

### 2.5 OLLVM 字符串加密

OLLVM 的 `-mllvm -sobf` 自动加密所有字符串常量：编译时加密写入 `.rodata`，生成解密函数注册到 `.init_array`，SO 加载时自动执行解密。详见[第 9 节](#9-ollvm-字符串加密)。

---

## 3. 静态分析识别

### 3.1 快速判断是否存在混淆

| 检查项 | 操作 | 未混淆特征 | 混淆特征 |
|--------|------|-----------|---------|
| 字符串窗口 | `Shift+F12` | 大量可读字符串 | 字符串极少或全是乱码 |
| .rodata 段 | 双击进入 | 可见 ASCII 文本 | 全是不可读字节 |
| .init_array | 查看段内容 | 仅标准初始化 | 包含多个可疑函数指针 |
| 函数特征 | 浏览反编译代码 | 直接引用字符串常量 | 大量位运算和循环 |

### 3.2 XOR 加密的识别特征

IDA 反汇编中的典型模式 -- LDRB + EOR + STRB 循环：

```asm
loc_loop:
    LDRB    W9, [X8]          ; 读取加密字节
    EOR     W9, W9, #0xAB     ; XOR 解密
    STRB    W9, [X8]          ; 写回
    ADD     X8, X8, #1
    SUBS    W10, W10, #1
    B.NE    loc_loop
```

反编译伪代码表现为简洁的循环 `data[i] ^= 0xABu`。多字节密钥变体中 `i % key_len` 常被优化为 `i & (key_len - 1)`。

### 3.3 栈构造字符串的识别

看到大量连续的 `MOV byte/word/dword` 指令写入同一栈缓冲区，且立即数在 ASCII 范围（0x20-0x7E）内，几乎可以确定是栈构造字符串。IDA 优化后常表现为 QWORD/DWORD 赋值。

### 3.4 .init_array 的检查

在 IDA 中按 `Ctrl+S` 打开段列表，找到 `.init_array` 段，逐一检查其中的函数指针。如果某个函数内部包含循环 XOR 操作并修改 `.rodata` 数据，它很可能是 OLLVM 的字符串解密函数。

---

## 4. XOR 解密实战

### 4.1 识别流程

1. **定位加密数据**：在 `.rodata` 中发现不可读字节序列
2. **寻找交叉引用**：按 `X` 查看该地址被哪些函数引用
3. **分析解密函数**：确认是 XOR 循环模式，提取密钥
4. **手动验证**：

```python
encrypted = [0xD8, 0xC4, 0xC2, 0xCD, 0xC4, 0xD1, 0xDF, 0xCB, 0xC4, 0xD8]
result = ''.join(chr(b ^ 0xAB) for b in encrypted)
print(result)  # "secret_key"
```

### 4.2 暴力破解未知密钥

当密钥未知时，对单字节 XOR 可尝试全部 256 种可能：

```python
def guess_xor_key(encrypted_data):
    for key in range(256):
        decrypted = bytes([b ^ key for b in encrypted_data])
        if all(0x20 <= c < 0x7F or c == 0 for c in decrypted):
            print(f"Key=0x{key:02X}: {decrypted.decode('ascii', errors='replace')}")
```

也可利用频率分析：密文中出现最多的字节可能对应 NULL 终止符（XOR key = 该字节本身）。

---

## 5. 栈构造字符串

### 5.1 逐字节构造的还原

Ghidra 反编译输出中看到连续的单字节赋值：

```c
buf[0]=0x68; buf[1]=0x74; buf[2]=0x74; buf[3]=0x70; // "http"
```

直接将十六进制值转为 ASCII 即可还原。

### 5.2 编译器优化合并的还原

IDA 反编译常将多字节合并为整数常量（小端序）：

```c
*(_QWORD *)&buf[0] = 0x2F2F3A7370747468LL;  // "https://"
*(_DWORD *)&buf[8] = 0x2E697061;              // "api."
```

还原方法：

```python
import struct
def qword_to_str(val):
    return struct.pack('<Q', val).decode('ascii', errors='replace').rstrip('\x00')

print(qword_to_str(0x2F2F3A7370747468))  # "https://"
```

推荐使用 IDA 插件 **FLOSS** 或 **strdeob** 自动识别栈构造字符串。

---

## 6. Frida 动态解密

核心思路：Hook 解密函数的入口和出口，在运行时截获明文。

### 6.1 Hook 解密函数

```javascript
function hookDecryptFunction() {
    var base = Module.findBaseAddress("libtarget.so");
    // sub_1234 是静态分析确认的解密函数
    var decrypt_func = base.add(0x1234);

    Interceptor.attach(decrypt_func, {
        onEnter: function(args) {
            this.buf = args[0];
            this.len = args[1].toInt32();
        },
        onLeave: function(retval) {
            try {
                var plaintext = this.buf.readUtf8String();
                console.log("[+] 解密: " + plaintext);
                send({ type: "decrypted", addr: this.buf.toString(), text: plaintext });
            } catch (e) {}
        }
    });
}

// 等待 SO 加载后再 Hook
Interceptor.attach(Module.findExportByName(null, "dlopen"), {
    onEnter: function(args) { this.path = args[0].readUtf8String(); },
    onLeave: function(retval) {
        if (this.path && this.path.indexOf("libtarget.so") !== -1)
            hookDecryptFunction();
    }
});
```

### 6.2 Python 端批量收集

```python
import frida, json, sys

collected = {}

def on_message(msg, data):
    if msg['type'] == 'send' and msg['payload'].get('type') == 'decrypted':
        addr, text = msg['payload']['addr'], msg['payload']['text']
        if addr not in collected:
            collected[addr] = text
            print(f"[+] {addr}: {text}")

device = frida.get_usb_device()
pid = device.spawn(["com.target.app"])
session = device.attach(pid)
script = session.create_script(open("hook_decrypt.js").read())
script.on('message', on_message)
script.load()
device.resume(pid)

try: sys.stdin.read()
except KeyboardInterrupt: pass

json.dump(collected, open("decrypted_strings.json", "w"), indent=2, ensure_ascii=False)
print(f"[*] 共收集 {len(collected)} 个字符串")
```

### 6.3 内存扫描法

当无法定位解密函数时，让应用运行后扫描内存：

```javascript
setTimeout(function() {
    var mod = Process.findModuleByName("libtarget.so");
    Memory.scan(mod.base, mod.size, "68 74 74 70 73 3A 2F 2F", {
        onMatch: function(addr, size) {
            try { console.log("[+] " + addr + ": " + addr.readUtf8String()); }
            catch(e) {}
        },
        onComplete: function() {}
    });
}, 3000);
```

**局限性**：只能发现已解密的字符串；结果含大量噪声；部分方案使用后会清除明文。

---

## 7. Unicorn/Unidbg 模拟解密

适用于独立、无外部依赖的解密函数，脱离 App 环境直接解密。

### 7.1 Unicorn Engine

```python
from unicorn import *
from unicorn.arm64_const import *

def emulate_decrypt(func_bytes, encrypted_data):
    CODE, DATA, STACK = 0x10000, 0x20000, 0x30000

    mu = Uc(UC_ARCH_ARM64, UC_MODE_ARM)
    mu.mem_map(CODE, 0x10000)
    mu.mem_map(DATA, 0x10000)
    mu.mem_map(STACK, 0x10000)

    mu.mem_write(CODE, func_bytes)
    mu.mem_write(DATA, encrypted_data)
    mu.reg_write(UC_ARM64_REG_X0, DATA)
    mu.reg_write(UC_ARM64_REG_X1, len(encrypted_data))
    mu.reg_write(UC_ARM64_REG_SP, STACK + 0xFF00)

    mu.emu_start(CODE, CODE + len(func_bytes))
    return bytes(mu.mem_read(DATA, len(encrypted_data)))

# 从 IDA 导出解密函数机器码（Edit -> Export Data -> Raw bytes）
# result = emulate_decrypt(func_bytes, encrypted)
```

### 7.2 Unidbg（推荐）

Unidbg 自动处理 JNI 环境和 SO 加载，更适合 Android 场景：

```java
AndroidEmulator emulator = AndroidEmulatorBuilder.for64Bit().build();
emulator.getMemory().setLibraryResolver(new AndroidResolver(23));
Module module = emulator.loadLibrary(new File("libtarget.so"));
// .init_array 自动执行，OLLVM 加密字符串已解密

// 方式 1：直接调用解密函数
Number result = module.callFunction(emulator, 0x1234, dataPtr, len)[0];

// 方式 2：直接读取已解密的 .rodata
UnidbgPointer ptr = UnidbgPointer.pointer(emulator, module.base + 0x4000);
System.out.println(new String(ptr.getByteArray(0, 64)).trim());
```

| 特性 | Unicorn | Unidbg |
|------|---------|--------|
| 语言 | Python/C | Java |
| JNI 支持 | 需手动模拟 | 内置 |
| .init_array | 需手动执行 | 自动执行 |
| SO 加载 | 需手动映射 ELF | 自动加载和重定位 |
| 适用场景 | 简单独立函数 | 复杂 SO，有 JNI 依赖 |

---

## 8. IDAPython 批量解密脚本

### 8.1 通用解密框架

```python
import idaapi, idautils, idc

class StringDecryptor:
    def __init__(self, func_addr):
        self.func_addr = func_addr
        self.results = []

    def decrypt(self, data, key):
        raise NotImplementedError

    def extract_args(self, call_ea):
        """在调用点向上回溯提取 ARM64 参数 (X0=数据, X1=长度, X2=密钥)"""
        ea, args = call_ea, {}
        for _ in range(20):
            ea = idc.prev_head(ea)
            if ea == idaapi.BADADDR: break
            mnem = idc.print_insn_mnem(ea)
            if mnem in ("BL", "B"): break
            op0 = idc.print_operand(ea, 0)
            val = idc.get_operand_value(ea, 1)
            if "X0" in op0 or "W0" in op0: args['arg0'] = val
            elif "X1" in op0 or "W1" in op0: args['arg1'] = val
            elif "X2" in op0 or "W2" in op0: args['arg2'] = val
        return args

    def run(self):
        for xref in idautils.CodeRefsTo(self.func_addr, 0):
            args = self.extract_args(xref)
            addr, length = args.get('arg0'), args.get('arg1')
            if not addr or not length or length > 4096: continue
            encrypted = idaapi.get_bytes(addr, length)
            if not encrypted: continue
            decrypted = self.decrypt(encrypted, args.get('arg2'))
            if decrypted:
                text = decrypted.decode('utf-8', errors='replace').rstrip('\x00')
                idc.set_cmt(xref, f'STR: "{text}"', 0)
                self.results.append((xref, text))
                print(f"  [+] 0x{xref:X}: \"{text}\"")
        print(f"[*] 共解密 {len(self.results)} 个字符串")


class XorDecryptor(StringDecryptor):
    def __init__(self, func_addr, fixed_key=None):
        super().__init__(func_addr)
        self.fixed_key = fixed_key

    def decrypt(self, data, key=None):
        k = self.fixed_key if self.fixed_key is not None else (key or 0)
        return bytes([b ^ k for b in data])


class MultiXorDecryptor(StringDecryptor):
    def __init__(self, func_addr, key_bytes):
        super().__init__(func_addr)
        self.key_bytes = key_bytes

    def decrypt(self, data, key=None):
        return bytes([data[i] ^ self.key_bytes[i % len(self.key_bytes)]
                      for i in range(len(data))])

# 使用: XorDecryptor(0x1234, fixed_key=0xAB).run()
```

### 8.2 处理 ADRP/ADD 寻址

ARM64 访问全局数据使用 ADRP+ADD 指令对，需特殊解析：

```python
def resolve_adrp_add(adrp_ea, add_ea):
    """ADRP X0, #page; ADD X0, X0, #off -> 目标地址"""
    page = (adrp_ea & ~0xFFF) + (idc.get_operand_value(adrp_ea, 1) << 12)
    return page + idc.get_operand_value(add_ea, 2)
```

在 `extract_args` 中识别 ADRP 指令后记录其地址，遇到对应的 ADD 时调用 `resolve_adrp_add` 计算真实数据地址。

---

## 9. OLLVM 字符串加密

### 9.1 工作原理

```text
编译期: "hello" ──[LLVM Pass]──> 密文 0xA3 0xB2 ... 写入 .rodata
运行期: .init_array ──> 解密函数() ──> .rodata 密文原地解密为 "hello"
                        ↑ SO 加载时自动执行（在 JNI_OnLoad 之前）
```

**关键特征**：`.rodata` 全是不可读数据；`.init_array` 有额外函数指针；解密函数内是大量重复的循环 XOR 块，每个字符串使用不同密钥。

### 9.2 典型解密函数

```c
// IDA 反编译 - OLLVM datadiv_decode 函数
void __fastcall datadiv_decode_1234567890(void) {
    unsigned char *p1 = (unsigned char *)&unk_4100;
    for (int i = 0; i < 10; i++) p1[i] ^= 0x37;

    unsigned char *p2 = (unsigned char *)&unk_4110;
    for (int i = 0; i < 24; i++) p2[i] ^= 0x5A;

    unsigned char *p3 = (unsigned char *)&unk_4130;
    for (int i = 0; i < 8; i++)  p3[i] ^= 0xC3;
    // ... 数十甚至数百个这样的块
}
```

函数名通常以 `datadiv_decode` 开头（可能被 strip）；函数在 `.init_array` 注册。

### 9.3 IDAPython 解密 OLLVM 字符串

```python
def find_init_array_functions():
    """遍历 .init_array 段，返回所有函数地址"""
    seg = idaapi.get_segm_by_name(".init_array")
    if not seg: return []
    funcs, ea = [], seg.start_ea
    ptr_size = 8 if idaapi.get_inf_structure().is_64bit() else 4
    while ea < seg.end_ea:
        addr = idaapi.get_qword(ea) if ptr_size == 8 else idaapi.get_dword(ea)
        if addr and idaapi.get_func(addr): funcs.append(addr)
        ea += ptr_size
    return funcs

def is_decrypt_function(func_addr):
    """检查函数内 EOR 指令数量是否超过阈值"""
    func = idaapi.get_func(func_addr)
    if not func: return False
    count, ea = 0, func.start_ea
    while ea < func.end_ea:
        if idc.print_insn_mnem(ea) == "EOR": count += 1
        ea = idc.next_head(ea)
    return count > 3

def ollvm_batch_decrypt(decrypt_table):
    """根据提取的 (地址, 长度, 密钥) 列表批量解密"""
    for addr, length, key in decrypt_table:
        encrypted = idaapi.get_bytes(addr, length)
        if not encrypted: continue
        decrypted = bytes([b ^ key for b in encrypted])
        try:
            text = decrypted.decode('utf-8').rstrip('\x00')
            idc.set_cmt(addr, f'"{text}"', 0)
            idc.create_strlit(addr, addr + length)
            print(f"[+] 0x{addr:X} [key=0x{key:02X}]: \"{text}\"")
        except:
            print(f"[?] 0x{addr:X}: {decrypted.hex()}")
```

### 9.4 Unidbg 一键解密

最简单有效的方案 -- 让 Unidbg 加载 SO（自动执行 `.init_array`），然后 dump 解密后的内存：

```java
Module module = emulator.loadLibrary(new File("libtarget.so"));
// .init_array 已自动执行，所有字符串已解密
// dump 后用 strings 命令提取：strings -n 4 libtarget_decrypted.bin
```

---

## 10. 实战案例：完整字符串解密流程

### 10.1 场景

目标：某支付 SDK 的 `libpaysdk.so`，需还原加密字符串以分析通信协议。

### 10.2 步骤一：初步分析

```bash
$ strings -n 6 libpaysdk.so | head -10
# 几乎没有有意义的字符串，确认存在混淆
```

IDA 中 `Shift+F12` 打开字符串窗口，仅有系统字符串，自定义字符串全部缺失。

### 10.3 步骤二：检查 .init_array

发现可疑函数 `sub_3B40`，反编译后看到典型 OLLVM 模式：

```c
void sub_3B40() {
    byte_6100[0] ^= 0x37u; byte_6100[1] ^= 0x37u; // ... 共 25 字节
    byte_6120[0] ^= 0x5Au; byte_6120[1] ^= 0x5Au; // ... 共 48 字节
    // 第 3 组 - 第 N 组 ...
}
```

### 10.4 步骤三：IDAPython 解密

```python
decrypt_table = [
    (0x6100, 25, 0x37), (0x6120, 48, 0x5A), (0x6150, 16, 0xC3),
    (0x6160, 32, 0x91), (0x6180, 12, 0x44), (0x6190, 64, 0xBE),
]
ollvm_batch_decrypt(decrypt_table)
```

输出结果：

```text
[+] 0x6100 [key=0x37]: "https://pay.example.com/api"
[+] 0x6120 [key=0x5A]: "X-Signature"
[+] 0x6150 [key=0xC3]: "AES/CBC/PKCS5Padding"
[+] 0x6160 [key=0x91]: "RSA/ECB/OAEPWithSHA-256"
[+] 0x6180 [key=0x44]: "merchant_id"
[+] 0x6190 [key=0xBE]: "{"code":%d,"data":"%s","sign":"%s"}"
```

### 10.5 步骤四：Frida 验证

```javascript
var base = Module.findBaseAddress("libpaysdk.so");
Interceptor.attach(base.add(0x1A00), {
    onEnter: function(args) {
        console.log("[*] URL参数: " + args[0].readUtf8String());
        // 如果输出 "https://pay.example.com/api"，则验证解密正确
    }
});
```

### 10.6 方法选择指南

| 场景 | 推荐方法 | 原因 |
|------|---------|------|
| 简单 XOR，密钥已知 | IDAPython 脚本 | 最快速，可批量处理 |
| OLLVM 字符串加密 | Unidbg 加载 + dump | 无需分析解密逻辑 |
| 栈构造字符串 | IDA 手动分析 / FLOSS | 需识别指令模式 |
| 复杂自定义算法 | Frida 动态 Hook | 无需理解算法 |
| 有反调试保护 | Unicorn 模拟执行 | 脱离 App 环境 |
| 未知混淆方案 | 先 Frida 采样再静态分析 | 先确认类型再选工具 |

> **实践建议**：真实项目中往往需要组合多种方法。先用 Frida 快速采样确认混淆类型，再用 IDAPython 或 Unidbg 批量解密，最后用 Frida 验证结果完整性。
