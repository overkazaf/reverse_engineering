---
title: "Unity 游戏逆向 (Il2Cpp) 案例"
date: 2025-03-12
type: posts
tags: ["Native层", "Ghidra", "Frida", "案例分析", "Unity游戏", "Hook", "IL2CPP", "Mono", "GameGuardian"]
weight: 10
---

# Unity 游戏逆向 (Il2Cpp) 案例

> **📚 前置知识**
>
> 本案例涉及以下核心技术，建议先阅读相关章节：
>
> - **[SO/ELF 格式](../04-Reference/Foundations/so_elf_format.md)** - 理解 libil2cpp.so 的结构
> - **[Frida Native Hook](../02-Tools/Dynamic/frida_guide.md#native-hook)** - 对 Il2Cpp 函数进行运行时修改
> - **[反分析技术案例](case_anti_analysis_techniques.md)** - 理解反调试与完整性校验

Unity 是目前最流行的移动游戏引擎之一。现代 Unity 游戏通常使用 Il2Cpp 脚本后端，将 C# 代码转换为 C++ 代码并编译为 Native 库 (`libil2cpp.so`)。这使得传统的 Java/Smali 逆向方法失效，需要全新的工具和思路。

---

## 1. Unity 游戏架构

### 1.1 Mono vs IL2CPP

Unity 提供两种脚本后端（Scripting Backend），它们决定了 C# 代码最终以何种形式运行在设备上：

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Unity 脚本后端对比                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   C# 源代码 (.cs)                                                   │
│        │                                                            │
│        ├──────────────────────┬──────────────────────┐              │
│        ▼                     ▼                       │              │
│   ┌─────────┐          ┌──────────┐                  │              │
│   │  Mono   │          │  IL2CPP  │                  │              │
│   │  后端    │          │  后端    │                  │              │
│   └────┬────┘          └─────┬────┘                  │              │
│        │                     │                       │              │
│        ▼                     ▼                       │              │
│   C# --> IL (.dll)      C# --> IL --> C++ --> .so    │              │
│        │                     │                       │              │
│        ▼                     ▼                       │              │
│   Mono VM 解释执行      Native 机器码直接执行         │              │
│        │                     │                       │              │
│        ▼                     ▼                       │              │
│   Assembly-CSharp.dll   libil2cpp.so                 │              │
│   (可直接反编译)         + global-metadata.dat        │              │
│                          (需要 Dump 还原符号)         │              │
│                                                      │              │
└─────────────────────────────────────────────────────────────────────┘
```

| 特性 | Mono 后端 | IL2CPP 后端 |
|------|-----------|-------------|
| **代码形式** | .NET DLL (IL 字节码) | Native SO (机器码) |
| **运行方式** | Mono VM 解释/JIT | CPU 直接执行 |
| **逆向难度** | 低 (dnSpy 直接反编译) | 高 (需要 IDA/Ghidra) |
| **性能** | 较低 | 较高 |
| **包体大小** | 较小 | 较大 |
| **保护强度** | 极弱 | 较强 |
| **符号信息** | 完整保留在 DLL 中 | 存储在 global-metadata.dat |
| **目前占比** | 少数老游戏 | 绝大多数新游戏 |

> **关键结论**: 2020 年之后发布的 Unity 游戏几乎都使用 IL2CPP 后端。Google Play 从 2019 年起要求提供 64 位支持，而 Mono 后端在当时对 ARM64 的支持不佳，这加速了向 IL2CPP 的迁移。

### 1.2 IL2CPP 编译流程

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  C# 源代码    │────>│  IL 字节码    │────>│  C++ 源代码   │
│  (.cs 文件)   │     │  (.dll 文件)  │     │  (.cpp 文件)  │
└──────────────┘     └──────────────┘     └──────┬───────┘
                      Roslyn 编译器               │ il2cpp.exe 转换
                                                  ▼
┌──────────────┐     ┌──────────────────┐  ┌──────────────┐
│ 最终 APK/AAB  │<───│ libil2cpp.so     │<─│  .o 目标文件  │
│              │     │ (stripped, 无符号) │  │              │
│              │     ├──────────────────┤  └──────────────┘
│              │     │ global-metadata  │        NDK 编译
│              │     │ .dat (元数据)     │
│              │     └──────────────────┘
└──────────────┘
```

### 1.3 核心文件与程序集结构

一个典型的 Unity IL2CPP 游戏 APK 解压后，关键文件如下：

```
game.apk (解压后)
├── lib/
│   ├── armeabi-v7a/                    # 32 位 ARM
│   │   ├── libil2cpp.so                # ★ 核心游戏逻辑 (50-200MB)
│   │   ├── libmain.so                  # Unity 启动入口
│   │   └── libunity.so                 # Unity 引擎运行时
│   └── arm64-v8a/                      # 64 位 ARM
│       ├── libil2cpp.so                # ★ 优先分析这个
│       ├── libmain.so
│       └── libunity.so
├── assets/
│   └── bin/
│       └── Data/
│           ├── Managed/
│           │   ├── Metadata/
│           │   │   └── global-metadata.dat  # ★ 元数据 (5-30MB)
│           │   └── Resources/
│           ├── data.unity3d              # 资源包
│           ├── level0                    # 场景文件
│           ├── sharedassets0.assets      # 共享资源
│           └── boot.config               # 启动配置
├── classes.dex                           # Java 层 (通常很薄)
├── AndroidManifest.xml
└── META-INF/
```

**`libil2cpp.so`** 内部包含了多个程序集的代码：

| 程序集名称 | 内容说明 |
|-----------|---------|
| `Assembly-CSharp` | 开发者编写的核心游戏逻辑 |
| `Assembly-CSharp-firstpass` | 第三方插件、早期初始化代码 |
| `UnityEngine` | Unity 引擎 API |
| `UnityEngine.UI` | UI 系统 |
| `mscorlib` | .NET 基础类库 |
| `System` | 系统库 |
| `Newtonsoft.Json` | JSON 序列化（如果使用） |
| `Google.Protobuf` | Protobuf 通信（如果使用） |

> 逆向时主要关注 `Assembly-CSharp`，这里面包含了游戏的业务逻辑。

---

## 2. Unity App 识别

### 2.1 文件结构特征

拿到一个 APK 后，如何快速判断它是否是 Unity 游戏？

```bash
# 解压 APK
unzip -o target.apk -d target_apk/

# 方法 1: 检查 SO 库
ls target_apk/lib/arm64-v8a/
# Unity 特征: 同时存在 libil2cpp.so, libunity.so, libmain.so

# 方法 2: 检查 metadata
ls target_apk/assets/bin/Data/Managed/Metadata/
# 存在 global-metadata.dat

# 方法 3: 检查启动配置
cat target_apk/assets/bin/Data/boot.config
# 内容类似:
# scripting-backend=il2cpp
# player-connection-mode=Listen
```

### 2.2 快速识别脚本

```bash
#!/bin/bash
# unity_detect.sh - 快速识别 Unity 游戏类型

APK=$1
TMPDIR=$(mktemp -d)

unzip -q "$APK" -d "$TMPDIR" 2>/dev/null

echo "=== Unity 游戏检测 ==="

# 检测 Unity 引擎
if [ -f "$TMPDIR/lib/arm64-v8a/libunity.so" ] || \
   [ -f "$TMPDIR/lib/armeabi-v7a/libunity.so" ]; then
    echo "[+] 检测到 Unity 引擎"

    # 判断后端类型
    if [ -f "$TMPDIR/lib/arm64-v8a/libil2cpp.so" ]; then
        echo "[+] 脚本后端: IL2CPP (64-bit)"
        SO_SIZE=$(stat -f%z "$TMPDIR/lib/arm64-v8a/libil2cpp.so" 2>/dev/null || \
                  stat -c%s "$TMPDIR/lib/arm64-v8a/libil2cpp.so" 2>/dev/null)
        echo "    libil2cpp.so 大小: $(echo "scale=2; $SO_SIZE/1048576" | bc) MB"
    elif [ -f "$TMPDIR/lib/armeabi-v7a/libil2cpp.so" ]; then
        echo "[+] 脚本后端: IL2CPP (32-bit only)"
    fi

    if [ -d "$TMPDIR/assets/bin/Data/Managed" ]; then
        DLL_COUNT=$(find "$TMPDIR/assets/bin/Data/Managed" -name "*.dll" 2>/dev/null | wc -l)
        if [ "$DLL_COUNT" -gt 0 ]; then
            echo "[+] 脚本后端: Mono (找到 $DLL_COUNT 个 DLL)"
        fi
    fi

    # 检测 metadata
    if [ -f "$TMPDIR/assets/bin/Data/Managed/Metadata/global-metadata.dat" ]; then
        META_SIZE=$(stat -f%z "$TMPDIR/assets/bin/Data/Managed/Metadata/global-metadata.dat" \
                    2>/dev/null || stat -c%s \
                    "$TMPDIR/assets/bin/Data/Managed/Metadata/global-metadata.dat" 2>/dev/null)
        echo "[+] global-metadata.dat 大小: $(echo "scale=2; $META_SIZE/1048576" | bc) MB"

        # 检查 magic number
        MAGIC=$(xxd -l 4 "$TMPDIR/assets/bin/Data/Managed/Metadata/global-metadata.dat" | \
                awk '{print $2$3}')
        if [ "$MAGIC" = "af1b b1fa" ] || [ "$MAGIC" = "AF1BB1FA" ]; then
            echo "[+] metadata 未加密 (magic: AF1BB1FA)"
        else
            echo "[!] metadata 可能已加密 (magic: $MAGIC)"
        fi
    fi

    # Unity 版本
    if [ -f "$TMPDIR/assets/bin/Data/boot.config" ]; then
        echo "[+] boot.config 内容:"
        cat "$TMPDIR/assets/bin/Data/boot.config" | sed 's/^/    /'
    fi
else
    echo "[-] 非 Unity 游戏"
fi

rm -rf "$TMPDIR"
```

### 2.3 特征库对照表

| 检测项 | Unity IL2CPP | Unity Mono | 非 Unity |
|--------|-------------|------------|---------|
| `libil2cpp.so` | 存在 | 不存在 | 不存在 |
| `libunity.so` | 存在 | 存在 | 不存在 |
| `libmono.so` | 不存在 | 存在 | 不存在 |
| `global-metadata.dat` | 存在 | 不存在 | 不存在 |
| `Assembly-CSharp.dll` | 不存在 | 存在 | 不存在 |
| `boot.config` | 通常存在 | 通常存在 | 不存在 |
| `level0`, `sharedassets*.assets` | 存在 | 存在 | 不存在 |

---

## 3. IL2CPP 逆向基础

### 3.1 为什么需要元数据

`libil2cpp.so` 在编译时会被 strip（移除符号表），直接用 IDA/Ghidra 打开只能看到海量的 `sub_XXXXXX`：

```
# IDA 中看到的 stripped libil2cpp.so
.text:00123456  sub_123456    # 这是什么函数？不知道
.text:00123500  sub_123500    # 是 AddCoin? TakeDamage? 完全不清楚
.text:00123600  sub_123600    # 上万个无名函数...
```

而 `global-metadata.dat` 就像一本字典，记录了：

- 每个类的名称、命名空间、父类
- 每个方法的名称、参数类型、返回值类型
- 每个字段的名称、类型、偏移
- 字符串字面量
- **方法在 `libil2cpp.so` 中的 RVA（相对虚拟地址）偏移**

```
┌─────────────────────────────────┐    ┌─────────────────────────────┐
│        libil2cpp.so             │    │    global-metadata.dat      │
│  (stripped, 无符号信息)          │    │    (类/方法/字段名映射)       │
├─────────────────────────────────┤    ├─────────────────────────────┤
│                                 │    │                             │
│  sub_123456:                    │◄──►│  PlayerData.AddCoin()       │
│    push {r4, r5, lr}           │    │    offset: 0x123456         │
│    ldr r4, [r0, #0x10]        │    │    params: (int amount)     │
│    add r4, r4, r1             │    │                             │
│    str r4, [r0, #0x10]        │    │  PlayerData.coin            │
│    pop {r4, r5, pc}           │    │    field_offset: 0x10       │
│                                 │    │    type: System.Int32       │
│  sub_123500:                    │◄──►│  BattleManager.TakeDamage() │
│    ...                          │    │    offset: 0x123500         │
│                                 │    │                             │
└─────────────────────────────────┘    └─────────────────────────────┘
         ▲                                        ▲
         │                                        │
         └──────── Il2CppDumper 建立映射 ──────────┘
```

### 3.2 IL2CPP 内部类型系统

IL2CPP 在运行时维护了一套完整的类型系统，核心数据结构如下：

```c
// Il2CppClass - 表示一个 C# 类
typedef struct Il2CppClass {
    Il2CppImage* image;              // 所属的程序集镜像
    void* gc_desc;
    const char* name;                // 类名 (如 "PlayerData")
    const char* namespaze;           // 命名空间 (如 "Game.Logic")
    Il2CppType byval_arg;
    Il2CppType this_arg;
    Il2CppClass* element_class;
    Il2CppClass* parent;             // 父类
    Il2CppGenericClass* generic_class;
    // ...
    FieldInfo* fields;               // 字段数组
    const MethodInfo** methods;      // 方法数组
    uint16_t field_count;
    uint16_t method_count;
    // ...
    uint32_t instance_size;          // 实例大小
    // ...
} Il2CppClass;

// MethodInfo - 表示一个 C# 方法
typedef struct MethodInfo {
    Il2CppMethodPointer methodPointer;  // ★ 函数指针 (可用于 Hook)
    const char* name;                    // 方法名 (如 "AddCoin")
    Il2CppClass* klass;                  // 所属的类
    const Il2CppType* return_type;       // 返回类型
    const ParameterInfo* parameters;     // 参数信息
    uint8_t parameters_count;            // 参数数量
    // ...
} MethodInfo;
```

### 3.3 IL2CPP 方法调用约定

在 IL2CPP 编译后的代码中，C# 方法被转换为 C 函数，调用约定如下：

```
C# 原始方法:
    public class Player {
        public int AddCoin(int amount) { ... }
    }

IL2CPP 转换后:
    int32_t Player_AddCoin(Player* __this, int32_t amount, MethodInfo* method)
                           ─────────────  ──────────────  ─────────────────
                           第一个参数       第二个参数       隐含的方法信息
                           是 this 指针     是原始参数       (通常可忽略)
```

在 ARM64 寄存器中：
| 寄存器 | 含义 |
|--------|------|
| `x0` | `this` 指针（实例方法）或第一个参数（静态方法） |
| `x1` | 第一个参数（实例方法）或第二个参数（静态方法） |
| `x2` | 第二个参数 / MethodInfo* |
| `x0` (返回) | 返回值 |

---

## 4. global-metadata.dat 分析

### 4.1 文件结构

`global-metadata.dat` 有固定的头部结构：

```c
typedef struct Il2CppGlobalMetadataHeader {
    int32_t sanity;              // 魔数: 0xFAB11BAF
    int32_t version;             // 版本号 (如 29 for Unity 2021+)
    int32_t stringLiteralOffset;
    int32_t stringLiteralSize;
    int32_t stringLiteralDataOffset;
    int32_t stringLiteralDataSize;
    int32_t stringOffset;        // 字符串表偏移
    int32_t stringSize;          // 字符串表大小
    int32_t eventsOffset;
    int32_t eventsSize;
    int32_t propertiesOffset;
    int32_t propertiesSize;
    int32_t methodsOffset;       // 方法定义表偏移
    int32_t methodsSize;
    int32_t fieldDefaultValuesOffset;
    int32_t fieldDefaultValuesSize;
    int32_t imagesOffset;        // 程序集镜像表偏移
    int32_t imagesSize;
    int32_t assembliesOffset;    // 程序集表偏移
    int32_t assembliesSize;
    // ... (更多表的偏移和大小)
} Il2CppGlobalMetadataHeader;
```

文件布局示意：

```
偏移        内容                      大小
─────────────────────────────────────────────────
0x0000      Header (魔数 + 版本 + 表指针)    ~300 字节
0x0130      String Literal Table            可变
0x????      String Table (类名/方法名)       可变
0x????      Type Definitions                可变
0x????      Method Definitions              可变
0x????      Field Definitions               可变
0x????      Image Definitions               可变
0x????      Assembly Definitions            可变
...         (其余元数据表)
EOF
```

### 4.2 加密检测

许多游戏会加密 `global-metadata.dat` 来阻止 Il2CppDumper 工作。检测方法：

```bash
# 方法 1: 检查魔数 (正常应该是 AF 1B B1 FA)
xxd -l 16 global-metadata.dat
# 正常输出: af1b b1fa 1d00 0000 ...  (1d = version 29)
# 加密输出: 随机字节 或 全零 或 其他固定值

# 方法 2: 搜索明文字符串 (正常的 metadata 包含大量可读字符串)
strings global-metadata.dat | head -20
# 正常: 能看到 System.Object, UnityEngine, MonoBehaviour 等
# 加密: 几乎没有可读字符串

# 方法 3: 检查熵值 (加密数据熵值接近 8.0)
python3 -c "
import math, sys
data = open(sys.argv[1], 'rb').read()
freq = [0] * 256
for b in data: freq[b] += 1
entropy = -sum(f/len(data) * math.log2(f/len(data)) for f in freq if f > 0)
print(f'Entropy: {entropy:.4f}')
print('加密可能性: ' + ('高' if entropy > 7.5 else '低'))
" global-metadata.dat
```

### 4.3 常见加密方案与解密思路

| 加密方案 | 特征 | 解密方法 |
|---------|------|---------|
| **XOR 全文加密** | 固定单字节/多字节异或 | 已知明文攻击 (magic bytes) |
| **AES 加密** | 高熵值，大小是 16 的倍数 | 逆向 libil2cpp.so 找密钥 |
| **自定义加密** | 各种特征 | 逆向加载流程 |
| **仅修改 Header** | Header 异常但数据区正常 | 修复 Header |
| **运行时解密** | 文件加密，内存中解密 | 内存 Dump |

**思路 1: 已知明文攻击（XOR 加密）**

```python
# xor_decrypt_metadata.py
# 利用已知的 magic number 推断 XOR key

import struct

with open("global-metadata.dat", "rb") as f:
    data = bytearray(f.read())

# global-metadata.dat 的 magic number 应该是 0xFAB11BAF
EXPECTED_MAGIC = struct.pack("<I", 0xFAB11BAF)  # AF 1B B1 FA
actual_magic = data[:4]

# 推断 XOR key
key = bytes([a ^ b for a, b in zip(actual_magic, EXPECTED_MAGIC)])
print(f"推断的 XOR key: {key.hex()}")

# 尝试解密
key_len = len(key)
decrypted = bytearray(len(data))
for i in range(len(data)):
    decrypted[i] = data[i] ^ key[i % key_len]

# 验证
dec_magic = struct.unpack("<I", decrypted[:4])[0]
dec_version = struct.unpack("<i", decrypted[4:8])[0]
print(f"解密后 magic: 0x{dec_magic:08X} (期望: 0xFAB11BAF)")
print(f"解密后 version: {dec_version} (合理范围: 24-31)")

if dec_magic == 0xFAB11BAF and 20 <= dec_version <= 35:
    with open("global-metadata-decrypted.dat", "wb") as f:
        f.write(decrypted)
    print("[+] 解密成功!")
else:
    print("[-] XOR 解密失败，可能是更复杂的加密方案")
```

**思路 2: 运行时内存 Dump（通用方法）**

无论游戏使用何种加密，在运行时 `libil2cpp.so` 必须将 metadata 解密到内存中。可以通过 Hook 加载函数来截获解密后的数据：

```javascript
// frida_dump_metadata.js
// Hook metadata 加载函数，Dump 解密后的 metadata

Java.perform(function() {
    var il2cpp = Module.findBaseAddress("libil2cpp.so");
    if (!il2cpp) {
        console.log("[-] libil2cpp.so not loaded yet");
        return;
    }

    // 方法 1: Hook il2cpp_init
    // metadata 通常在 il2cpp 初始化时加载
    var il2cpp_init = Module.findExportByName("libil2cpp.so", "il2cpp_init");
    if (il2cpp_init) {
        Interceptor.attach(il2cpp_init, {
            onEnter: function(args) {
                console.log("[*] il2cpp_init called");
            },
            onLeave: function(retval) {
                console.log("[*] il2cpp_init returned, scanning memory...");
                scanForMetadata();
            }
        });
    }

    // 方法 2: 扫描内存中的 metadata magic
    function scanForMetadata() {
        var ranges = Process.enumerateRanges("r--");
        for (var i = 0; i < ranges.length; i++) {
            var range = ranges[i];
            if (range.size < 1024) continue;

            try {
                var results = Memory.scanSync(range.base, range.size, "AF 1B B1 FA");
                for (var j = 0; j < results.length; j++) {
                    var addr = results[j].address;
                    var version = addr.add(4).readS32();

                    if (version >= 20 && version <= 35) {
                        console.log("[+] Found metadata at: " + addr +
                                    " version: " + version);

                        // 推测大小 (读取 header 中的最大偏移 + 大小)
                        var metaSize = estimateMetadataSize(addr);
                        console.log("[+] Estimated size: " + metaSize);

                        // Dump 到文件
                        var file = new File("/data/local/tmp/global-metadata-dumped.dat", "wb");
                        file.write(addr.readByteArray(metaSize));
                        file.close();
                        console.log("[+] Dumped to /data/local/tmp/global-metadata-dumped.dat");
                    }
                }
            } catch(e) {}
        }
    }

    function estimateMetadataSize(base) {
        // 遍历 header 中的 (offset, size) 对，找到最大的 offset+size
        var maxEnd = 0;
        for (var i = 2; i < 60; i += 2) {  // header 中的表偏移
            var offset = base.add(i * 4).readS32();
            var size = base.add((i + 1) * 4).readS32();
            if (offset > 0 && size > 0 && (offset + size) > maxEnd) {
                maxEnd = offset + size;
            }
        }
        return maxEnd > 0 ? maxEnd : 0x1000000;  // 默认 16MB
    }
});
```

---

## 5. Il2CppDumper 实战

### 5.1 准备工作

```bash
# 下载 Il2CppDumper (推荐 v6.7.x+)
# https://github.com/Perfare/Il2CppDumper/releases

# 解压 APK
mkdir -p ~/unity_re/target
cd ~/unity_re/target
unzip -o game.apk

# 提取关键文件
cp lib/arm64-v8a/libil2cpp.so ~/unity_re/
cp assets/bin/Data/Managed/Metadata/global-metadata.dat ~/unity_re/
```

### 5.2 运行 Dump

```bash
cd ~/unity_re

# 方式 1: 命令行模式 (推荐)
Il2CppDumper libil2cpp.so global-metadata.dat output/

# 方式 2: GUI 模式 (Windows)
# 运行 Il2CppDumper.exe，依次选择 libil2cpp.so 和 global-metadata.dat
```

成功执行后，`output/` 目录结构如下：

```
output/
├── dump.cs              # ★ 还原的 C# 伪代码 (最重要)
├── script.py            # IDA Pro 重命名脚本
├── ghidra.py            # Ghidra 重命名脚本 (Ghidra 11 可用)
├── il2cpp.h             # C 头文件 (IDA 可导入)
├── stringliteral.json   # 字符串字面量表
├── DummyDll/            # ★ 空壳 DLL (可用 dnSpy 打开)
│   ├── Assembly-CSharp.dll
│   ├── Assembly-CSharp-firstpass.dll
│   ├── UnityEngine.dll
│   ├── UnityEngine.CoreModule.dll
│   ├── mscorlib.dll
│   └── ...
└── il2cpp_types.json    # 类型信息 JSON
```

### 5.3 dump.cs 分析

`dump.cs` 是最重要的输出文件，它包含了还原后的类结构：

```csharp
// dump.cs 示例内容

// Namespace: Game.Logic
public class PlayerData // TypeDefIndex: 3456
{
    // Fields
    public int coin; // 0x10
    public int gem; // 0x14
    public int level; // 0x18
    public float hp; // 0x1C
    public float maxHp; // 0x20
    public string playerName; // 0x28
    public List<ItemData> inventory; // 0x30

    // Methods
    // RVA: 0x1A2B3C Offset: 0x1A2B3C VA: 0x1A2B3C
    public void AddCoin(int amount) { }

    // RVA: 0x1A2B80 Offset: 0x1A2B80 VA: 0x1A2B80
    public void SubCoin(int amount) { }

    // RVA: 0x1A2BC0 Offset: 0x1A2BC0 VA: 0x1A2BC0
    public int GetCoin() { }

    // RVA: 0x1A2C00 Offset: 0x1A2C00 VA: 0x1A2C00
    public void TakeDamage(float damage) { }

    // RVA: 0x1A2C80 Offset: 0x1A2C80 VA: 0x1A2C80
    public void Heal(float amount) { }

    // RVA: 0x1A2D00 Offset: 0x1A2D00 VA: 0x1A2D00
    public static PlayerData get_Instance() { }
}

// Namespace: Game.Battle
public class BattleManager : MonoBehaviour // TypeDefIndex: 3500
{
    // Fields
    public static BattleManager instance; // 0x0
    public float damageMultiplier; // 0x18
    public bool isInvincible; // 0x1C

    // Methods
    // RVA: 0x1B0000 Offset: 0x1B0000 VA: 0x1B0000
    public void CalculateDamage(PlayerData attacker, PlayerData target, float baseDmg) { }

    // RVA: 0x1B0100 Offset: 0x1B0100 VA: 0x1B0100
    public void OnBattleEnd(bool isWin) { }
}
```

> **注意**: `dump.cs` 只包含类的 **结构**（字段和方法签名），不包含方法的 **实现**。方法体需要通过 IDA/Ghidra 分析 `libil2cpp.so` 来获取。

### 5.4 在 dnSpy 中查看 DummyDll

```
步骤:
1. 打开 dnSpy (https://github.com/dnSpy/dnSpy)
2. File -> Open -> 选择 output/DummyDll/Assembly-CSharp.dll
3. 在左侧类树中浏览所有类和方法
4. 虽然方法体是空的，但可以看到完整的类继承、接口实现、枚举定义等

优势:
- 树状浏览比 dump.cs 的平面文本更直观
- 支持搜索类名、方法名、字段名
- 可以看到泛型参数、特性 (Attribute) 等详细信息
```

### 5.5 在 IDA Pro / Ghidra 中加载脚本

**IDA Pro:**

```
1. 用 IDA 打开 libil2cpp.so (选择 ARM 64-bit 或 ARM 32-bit)
2. 等待自动分析完成 (可能需要 10-30 分钟)
3. File -> Script file -> 选择 output/script.py
4. 脚本执行后，所有函数会被重命名:
   sub_1A2B3C  -->  PlayerData$$AddCoin
   sub_1A2B80  -->  PlayerData$$SubCoin
   sub_1B0000  -->  BattleManager$$CalculateDamage
```

**Ghidra:**

```
1. 创建新项目，导入 libil2cpp.so
2. 分析完成后，Window -> Script Manager
3. 运行 output/ghidra.py
4. 函数名和类型信息将被自动恢复
```

---

## 6. Frida Hook Unity 游戏

### 6.1 基础: 通过偏移 Hook

从 `dump.cs` 中获取方法的 RVA 偏移后，可以直接用 Frida Hook：

```javascript
// hook_il2cpp_basic.js
// 基础 IL2CPP Hook 模板

"use strict";

function hookIl2Cpp() {
    var soName = "libil2cpp.so";
    var baseAddr = Module.findBaseAddress(soName);

    if (!baseAddr) {
        console.log("[-] " + soName + " not loaded, retrying...");
        setTimeout(hookIl2Cpp, 1000);
        return;
    }

    console.log("[+] " + soName + " base: " + baseAddr);

    // ========================================
    // Hook PlayerData.AddCoin (RVA: 0x1A2B3C)
    // ========================================
    // 原型: void AddCoin(PlayerData* this, int amount, MethodInfo* method)
    var addCoinAddr = baseAddr.add(0x1A2B3C);
    Interceptor.attach(addCoinAddr, {
        onEnter: function(args) {
            // args[0] = this (PlayerData*)
            // args[1] = amount (int)
            // args[2] = MethodInfo*
            var thisPtr = args[0];
            var amount = args[1].toInt32();

            console.log("[*] AddCoin called, amount: " + amount);

            // 读取当前 coin 值 (字段偏移 0x10)
            var currentCoin = thisPtr.add(0x10).readS32();
            console.log("    Current coin: " + currentCoin);

            // 修改参数: 将增加量改为 99999
            args[1] = ptr(99999);
            console.log("    Modified amount to: 99999");
        },
        onLeave: function(retval) {
            console.log("[*] AddCoin finished");
        }
    });

    // ========================================
    // Hook PlayerData.TakeDamage (RVA: 0x1A2C00)
    // ========================================
    // 原型: void TakeDamage(PlayerData* this, float damage, MethodInfo* method)
    var takeDamageAddr = baseAddr.add(0x1A2C00);
    Interceptor.attach(takeDamageAddr, {
        onEnter: function(args) {
            var thisPtr = args[0];
            // 浮点参数在 ARM64 上通过 NEON 寄存器传递
            // 但 IL2CPP 有时会将 float 通过通用寄存器传递
            // 需要根据实际情况判断

            // 方法 1: 直接设置伤害为 0 (无敌)
            // 修改 float 参数
            var damagePtr = Memory.alloc(4);
            damagePtr.writeFloat(0.0);
            args[1] = damagePtr.readPointer();

            console.log("[*] TakeDamage -> damage set to 0 (god mode)");
        }
    });

    // ========================================
    // 直接修改内存中的字段值
    // ========================================
    // 如果能拿到 PlayerData 的实例指针，可以直接读写字段
    var getInstanceAddr = baseAddr.add(0x1A2D00); // PlayerData.get_Instance()
    Interceptor.attach(getInstanceAddr, {
        onLeave: function(retval) {
            if (!retval.isNull()) {
                var instance = retval;
                console.log("[*] PlayerData instance: " + instance);

                // 读取所有字段
                var coin  = instance.add(0x10).readS32();
                var gem   = instance.add(0x14).readS32();
                var level = instance.add(0x18).readS32();
                var hp    = instance.add(0x1C).readFloat();
                var maxHp = instance.add(0x20).readFloat();

                console.log("    Coin:  " + coin);
                console.log("    Gem:   " + gem);
                console.log("    Level: " + level);
                console.log("    HP:    " + hp.toFixed(1) + " / " + maxHp.toFixed(1));

                // 修改字段值
                instance.add(0x10).writeS32(999999);     // coin = 999999
                instance.add(0x14).writeS32(999999);     // gem = 999999
                instance.add(0x1C).writeFloat(99999.0);  // hp = 99999
                instance.add(0x20).writeFloat(99999.0);  // maxHp = 99999

                console.log("[+] Values modified!");
            }
        }
    });
}

// 等待 libil2cpp.so 加载
setTimeout(hookIl2Cpp, 3000);
```

### 6.2 使用 frida-il2cpp-bridge（推荐）

[frida-il2cpp-bridge](https://github.com/vfsfitvnm/frida-il2cpp-bridge) 是一个专门为 IL2CPP 游戏设计的 Frida 库，可以自动解析类型系统，无需手动计算偏移：

```javascript
// hook_il2cpp_bridge.js
// 使用 frida-il2cpp-bridge 进行更优雅的 Hook

import "frida-il2cpp-bridge";

Il2Cpp.perform(() => {
    // 1. 获取程序集
    const assembly = Il2Cpp.domain.assembly("Assembly-CSharp");
    const image = assembly.image;

    console.log("[+] Assembly-CSharp loaded");
    console.log("    Classes count: " + image.classCount);

    // ========================================
    // 2. 查找并 Hook 类方法
    // ========================================
    const PlayerData = image.class("Game.Logic.PlayerData");
    console.log("[+] PlayerData found: " + PlayerData);

    // 列出所有方法
    for (const method of PlayerData.methods) {
        console.log("    Method: " + method.name +
                    " | Params: " + method.parameterCount +
                    " | Offset: " + method.relativeVirtualAddress);
    }

    // 列出所有字段
    for (const field of PlayerData.fields) {
        console.log("    Field: " + field.name +
                    " | Type: " + field.type.name +
                    " | Offset: " + field.offset);
    }

    // ========================================
    // 3. Hook AddCoin - 修改增加量
    // ========================================
    PlayerData.method("AddCoin").implementation = function(amount) {
        console.log("[*] AddCoin called, original amount: " + amount);

        // 调用原始方法，但传入修改后的参数
        this.method("AddCoin").invoke(99999);

        console.log("[+] AddCoin modified to 99999");
    };

    // ========================================
    // 4. Hook TakeDamage - 实现无敌
    // ========================================
    PlayerData.method("TakeDamage").implementation = function(damage) {
        console.log("[*] TakeDamage blocked! Original damage: " + damage);
        // 不调用原始方法 = 不受伤
        return;
    };

    // ========================================
    // 5. Hook SubCoin - 阻止扣币
    // ========================================
    PlayerData.method("SubCoin").implementation = function(amount) {
        console.log("[*] SubCoin blocked! Tried to deduct: " + amount);
        // 不执行原始扣币逻辑
        return;
    };

    // ========================================
    // 6. 读写实例字段
    // ========================================
    const getInstance = PlayerData.method("get_Instance");
    const instance = getInstance.invoke();

    if (!instance.isNull()) {
        console.log("[+] Got PlayerData instance");
        console.log("    coin:  " + instance.field("coin").value);
        console.log("    gem:   " + instance.field("gem").value);
        console.log("    hp:    " + instance.field("hp").value);

        // 直接修改字段
        instance.field("coin").value = 999999;
        instance.field("gem").value = 999999;
        console.log("[+] Fields modified!");
    }

    // ========================================
    // 7. 追踪整个类的方法调用
    // ========================================
    const BattleManager = image.class("Game.Battle.BattleManager");
    Il2Cpp.trace()
        .classes(BattleManager)
        .and()
        .attach();

    console.log("[+] BattleManager trace enabled");
});
```

### 6.3 查找方法偏移的技巧

当 `dump.cs` 中的偏移在运行时不准确时，可以使用以下方法定位：

```javascript
// find_method_offset.js
// 在运行时搜索方法偏移

"use strict";

// 方法 1: Pattern Scanning (特征码搜索)
function findByPattern() {
    var module = Process.findModuleByName("libil2cpp.so");
    if (!module) return;

    // 例: 搜索 AddCoin 函数的开头字节 (需要先从 IDA 获取)
    // ARM64 函数通常以 STP X29, X30, [SP, #-0x??]! 开头
    var pattern = "FD 7B BE A9 FD 03 00 91";  // 示例 pattern
    var results = Memory.scanSync(module.base, module.size, pattern);

    console.log("Found " + results.length + " matches");
    results.forEach(function(match) {
        var rva = match.address.sub(module.base);
        console.log("  RVA: 0x" + rva.toString(16) + " VA: " + match.address);
    });
}

// 方法 2: 通过字符串引用定位
function findByStringRef() {
    var module = Process.findModuleByName("libil2cpp.so");
    if (!module) return;

    // 搜索游戏中的特征字符串
    var pattern = "00";  // 搜索 "AddCoin" 字符串
    var target = "AddCoin";
    var results = Memory.scanSync(module.base, module.size,
        stringToHexPattern(target));

    results.forEach(function(match) {
        console.log("[*] String '" + target + "' found at: " + match.address);

        // 搜索对这个字符串的交叉引用
        var strAddr = match.address;
        // 在代码段中搜索加载这个地址的指令
        // (需要根据 ARM64 指令格式计算)
    });
}

function stringToHexPattern(str) {
    var hex = "";
    for (var i = 0; i < str.length; i++) {
        hex += str.charCodeAt(i).toString(16).padStart(2, "0") + " ";
    }
    return hex.trim();
}

// 方法 3: 通过 IL2CPP API 获取运行时地址
function findByIl2CppApi() {
    // il2cpp_class_from_name 和 il2cpp_class_get_method_from_name
    // 是 libil2cpp.so 导出的 API

    var il2cpp_domain_get = new NativeFunction(
        Module.findExportByName("libil2cpp.so", "il2cpp_domain_get"),
        "pointer", []);

    var il2cpp_domain_get_assemblies = new NativeFunction(
        Module.findExportByName("libil2cpp.so", "il2cpp_domain_get_assemblies"),
        "pointer", ["pointer", "pointer"]);

    var il2cpp_class_from_name = new NativeFunction(
        Module.findExportByName("libil2cpp.so", "il2cpp_class_from_name"),
        "pointer", ["pointer", "pointer", "pointer"]);

    var il2cpp_class_get_method_from_name = new NativeFunction(
        Module.findExportByName("libil2cpp.so", "il2cpp_class_get_method_from_name"),
        "pointer", ["pointer", "pointer", "int"]);

    // 获取 domain
    var domain = il2cpp_domain_get();
    console.log("[*] Domain: " + domain);

    // 这种方法可以获取方法的 MethodInfo*
    // 从 MethodInfo 中读取 methodPointer 即可得到函数地址
}
```

### 6.4 Hook 运行时常用模式

```javascript
// common_hook_patterns.js
// Unity 游戏 Hook 常用模式合集

"use strict";

var il2cpp = Module.findBaseAddress("libil2cpp.so");

// ==============================
// 模式 1: 替换方法返回值
// ==============================
// 让 IsVIP() 永远返回 true
function hookIsVIP(offset) {
    Interceptor.attach(il2cpp.add(offset), {
        onLeave: function(retval) {
            retval.replace(ptr(1));  // true
        }
    });
}

// ==============================
// 模式 2: NOP 掉整个方法
// ==============================
// 让 ShowAd() 什么都不做 (ARM64)
function nopMethod(offset) {
    // ARM64: RET = 0xD65F03C0
    Memory.protect(il2cpp.add(offset), 4, "rwx");
    il2cpp.add(offset).writeU32(0xD65F03C0);
}

// ==============================
// 模式 3: Hook 构造函数追踪实例
// ==============================
var playerInstances = [];
function trackPlayerInstances(ctorOffset) {
    Interceptor.attach(il2cpp.add(ctorOffset), {
        onEnter: function(args) {
            playerInstances.push(args[0]);
            console.log("[+] New Player instance: " + args[0] +
                       " (total: " + playerInstances.length + ")");
        }
    });
}

// ==============================
// 模式 4: Hook Update 做持续修改
// ==============================
// Unity 的 Update() 每帧调用一次
function hookUpdate(offset, hpOffset, maxHpOffset) {
    var count = 0;
    Interceptor.attach(il2cpp.add(offset), {
        onEnter: function(args) {
            var self = args[0];
            // 每帧将 HP 设置为最大值
            var maxHp = self.add(maxHpOffset).readFloat();
            self.add(hpOffset).writeFloat(maxHp);

            // 每 300 帧打印一次 (大约 5 秒)
            if (count++ % 300 === 0) {
                console.log("[*] HP maintained at: " + maxHp);
            }
        }
    });
}

// ==============================
// 模式 5: Hook 网络请求修改数据
// ==============================
function hookNetworkResponse(parseOffset) {
    Interceptor.attach(il2cpp.add(parseOffset), {
        onEnter: function(args) {
            // args[1] 通常是 JSON 字符串或 protobuf 数据
            // 需要根据具体游戏的协议来修改
            console.log("[*] Network response received");
        }
    });
}
```

---

## 7. GameGuardian 与内存修改

### 7.1 GameGuardian 概述

GameGuardian (GG) 是 Android 上最流行的内存修改工具。它可以搜索和修改游戏进程的内存，适用于单机游戏或弱联网游戏。

```
┌─────────────────────────────────────────────────────┐
│               GameGuardian 工作原理                   │
├─────────────────────────────────────────────────────┤
│                                                     │
│  GameGuardian App (Root 权限)                        │
│       │                                             │
│       │ ptrace / /proc/<pid>/mem                    │
│       ▼                                             │
│  ┌─────────────────────────────────────┐            │
│  │        目标游戏进程内存空间            │            │
│  ├─────────────────────────────────────┤            │
│  │  代码段 (.text)  [r-x]              │            │
│  │  ├── libil2cpp.so                   │            │
│  │  └── libunity.so                    │            │
│  ├─────────────────────────────────────┤            │
│  │  数据段 (.data/.bss)  [rw-]         │            │
│  │  ├── 全局变量                        │            │
│  │  └── 静态字段                        │            │
│  ├─────────────────────────────────────┤            │
│  │  堆 (Heap)  [rw-]                   │            │
│  │  ├── 游戏对象实例  ◄── 搜索目标      │            │
│  │  │   ├── PlayerData.coin = 1000     │            │
│  │  │   ├── PlayerData.gem = 50        │            │
│  │  │   └── PlayerData.hp = 100.0      │            │
│  │  └── IL2CPP 管理的对象               │            │
│  ├─────────────────────────────────────┤            │
│  │  栈 (Stack)  [rw-]                  │            │
│  └─────────────────────────────────────┘            │
│                                                     │
│  搜索流程:                                           │
│  1. 搜索当前值 (如 coin=1000)                        │
│  2. 改变游戏中的值 (花掉一些 coin)                    │
│  3. 搜索新值 (如 coin=900)                           │
│  4. 重复缩小范围直到找到唯一地址                       │
│  5. 修改该地址的值                                    │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 7.2 基础搜索流程

**步骤 1: 已知值搜索**

```
场景: 游戏中显示 金币 = 1500

GG 操作:
  1. 打开 GG 悬浮窗
  2. 选择目标进程 (游戏)
  3. 搜索 -> 输入 1500
  4. 类型选择: DWORD (4字节整数)
  5. 搜索范围: 全部 (或 C++ Heap)
  6. 结果: 找到 5000+ 个地址 (太多)

缩小范围:
  7. 回到游戏，花费 200 金币 (剩余 1300)
  8. GG -> 继续搜索 -> 输入 1300
  9. 结果: 3 个地址

  10. 再次花费 100 金币 (剩余 1200)
  11. GG -> 继续搜索 -> 输入 1200
  12. 结果: 1 个地址 -> 这就是 coin 的内存地址!

修改:
  13. 选中该地址 -> 修改值为 999999
  14. 可选: 冻结该地址 (防止游戏更新值)
```

**步骤 2: 未知值搜索 (模糊搜索)**

```
场景: 游戏中 HP 显示为血条图形，不知道具体数值

GG 操作:
  1. 搜索 -> 未知值搜索
  2. 受到伤害后 -> 搜索 "减少的值"
  3. 吃血药后 -> 搜索 "增加的值"
  4. HP 未变化 -> 搜索 "未变化的值"
  5. 重复 3-5 次，缩小到几个地址
  6. 逐个修改测试
```

### 7.3 搜索类型对照

| 数据类型 | GG 中的名称 | 字节数 | 常见用途 |
|---------|------------|--------|---------|
| `DWORD` | Dword | 4 | 金币、经验值、等级 |
| `FLOAT` | Float | 4 | HP、速度、坐标 |
| `DOUBLE` | Double | 8 | 高精度数值 |
| `WORD` | Word | 2 | 小范围整数 |
| `BYTE` | Byte | 1 | 布尔值、小数值 |
| `QWORD` | Qword | 8 | 大数值、指针 |
| `XOR` | Encrypted | 4 | 异或加密后的值 |

### 7.4 加速器 (Speed Hack)

GameGuardian 内置的加速器通过 Hook 系统时间函数来改变游戏速度：

```
原理:
  Unity 游戏的 Time.deltaTime 依赖系统时钟
  加速器修改 clock_gettime / gettimeofday 的返回值
  使游戏认为时间流逝更快或更慢

效果:
  2x 加速 -> 游戏运行速度翻倍 (动画、移动、冷却都加速)
  0.5x 减速 -> 慢动作 (适用于需要精确操作的场景)

限制:
  - 服务端会检测客户端时间与服务器时间的差异
  - 许多游戏会检测 clock_gettime 是否被 Hook
  - Unity 的 Time.unscaledTime 可能不受影响
```

### 7.5 Frida 实现内存搜索

如果不方便使用 GameGuardian，可以用 Frida 实现类似的内存搜索：

```javascript
// memory_scanner.js
// 用 Frida 实现 GameGuardian 风格的内存搜索

"use strict";

var searchResults = [];

// 搜索指定整数值
function searchInt32(value) {
    searchResults = [];
    var pattern = intToHexPattern(value);
    var module = Process.findModuleByName("libil2cpp.so");

    // 在可写内存区域搜索 (堆、数据段)
    var ranges = Process.enumerateRanges("rw-");
    var total = 0;

    for (var i = 0; i < ranges.length; i++) {
        var range = ranges[i];
        if (range.size > 100 * 1024 * 1024) continue;  // 跳过超大区域

        try {
            var results = Memory.scanSync(range.base, range.size, pattern);
            for (var j = 0; j < results.length; j++) {
                searchResults.push(results[j].address);
                total++;
            }
        } catch(e) {}
    }

    console.log("[*] Found " + total + " addresses with value " + value);
    return total;
}

// 在已有结果中筛选
function refinSearch(newValue) {
    var pattern = intToHexPattern(newValue);
    var refined = [];

    for (var i = 0; i < searchResults.length; i++) {
        try {
            var current = searchResults[i].readS32();
            if (current === newValue) {
                refined.push(searchResults[i]);
            }
        } catch(e) {}
    }

    searchResults = refined;
    console.log("[*] Refined to " + refined.length + " addresses");

    if (refined.length <= 10) {
        for (var k = 0; k < refined.length; k++) {
            console.log("    [" + k + "] " + refined[k] +
                        " = " + refined[k].readS32());
        }
    }

    return refined.length;
}

// 修改指定索引的值
function modifyValue(index, newValue) {
    if (index < 0 || index >= searchResults.length) {
        console.log("[-] Invalid index");
        return;
    }
    var addr = searchResults[index];
    addr.writeS32(newValue);
    console.log("[+] " + addr + " set to " + newValue);
}

function intToHexPattern(value) {
    var buf = Memory.alloc(4);
    buf.writeS32(value);
    var bytes = buf.readByteArray(4);
    var arr = new Uint8Array(bytes);
    var hex = "";
    for (var i = 0; i < arr.length; i++) {
        hex += arr[i].toString(16).padStart(2, "0") + " ";
    }
    return hex.trim();
}

// 导出 RPC 接口供外部调用
rpc.exports = {
    search: searchInt32,
    refine: refinSearch,
    modify: modifyValue,
    count: function() { return searchResults.length; }
};
```

---

## 8. 反作弊机制分析

### 8.1 常见反作弊体系

```
┌─────────────────────────────────────────────────────────────────┐
│                    Unity 游戏反作弊体系                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐      │
│  │  客户端检测   │  │  服务端验证   │  │  第三方反作弊 SDK  │      │
│  ├──────────────┤  ├──────────────┤  ├──────────────────┤      │
│  │ 内存完整性    │  │ 数值合理性    │  │ ACE (腾讯)       │      │
│  │ 速度检测      │  │ 时间戳校验    │  │ NetEase 安全 SDK │      │
│  │ 代码校验      │  │ 行为分析      │  │ EasyAntiCheat   │      │
│  │ Hook 检测     │  │ 重放攻击防护  │  │ BattlEye        │      │
│  │ Root 检测     │  │ 服务端结算    │  │ GameGuard       │      │
│  │ 模拟器检测    │  │ 操作频率限制  │  │ 梆梆安全         │      │
│  └──────────────┘  └──────────────┘  └──────────────────┘      │
│                                                                 │
│  ┌──────────────────────────────────────────────────────┐      │
│  │                  混合防护策略                          │      │
│  │                                                      │      │
│  │  客户端: 提高作弊门槛、检测异常环境                     │      │
│  │  服务端: 最终仲裁者、验证所有关键操作                   │      │
│  │  行为分析: 大数据识别异常玩家                          │      │
│  │                                                      │      │
│  └──────────────────────────────────────────────────────┘      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 8.2 服务端验证

这是最有效的反作弊手段。关键数值的修改需要服务器确认：

```
客户端-服务端交互模型:

  ┌──────────┐                        ┌──────────┐
  │  客户端   │  ---购买请求(商品ID)--->  │  服务器   │
  │          │                        │          │
  │          │  <---扣款结果(新余额)---  │  验证:    │
  │  显示结果 │                        │  1. 余额够?│
  │          │                        │  2. 商品存在?│
  └──────────┘                        │  3. 价格对?│
                                      └──────────┘

  修改客户端 coin 显示 = 无效 (服务器不认)
  修改客户端购买请求中的价格 = 可能有效 (如果服务器不校验)
```

**绕过思路**:

```javascript
// 分析服务端验证: Hook 网络请求
// 检查哪些操作是服务端验证的、哪些是纯客户端的

Il2Cpp.perform(() => {
    const NetworkManager = Il2Cpp.domain
        .assembly("Assembly-CSharp").image
        .class("Network.NetworkManager");

    // Hook 发送请求方法
    NetworkManager.method("SendRequest").implementation = function(url, data) {
        console.log("[NET] Request: " + url);
        console.log("      Data: " + data);
        // 分析: 如果某个操作不发送网络请求，说明是纯客户端逻辑
        this.method("SendRequest").invoke(url, data);
    };

    // Hook 接收响应方法
    NetworkManager.method("OnResponse").implementation = function(response) {
        console.log("[NET] Response: " + response);
        this.method("OnResponse").invoke(response);
    };
});
```

### 8.3 内存完整性检测

游戏可能会定期检查关键内存区域是否被修改：

```c
// 典型的内存完整性检测 (伪代码)
void IntegrityCheck() {
    // 方式 1: CRC 校验关键代码段
    uint32_t crc = CalculateCRC32(codeStart, codeSize);
    if (crc != expectedCRC) {
        // 代码被篡改!
        ReportCheat();
        exit(0);
    }

    // 方式 2: 关键值哨兵
    // 在 coin 值旁边存储一个校验值
    if (coin != (coinChecksum ^ MAGIC_KEY)) {
        // coin 被外部修改!
        ReportCheat();
    }

    // 方式 3: 多副本对比
    // 同一个值存储在多个位置，定期对比
    if (coin_copy1 != coin_copy2 || coin_copy2 != coin_copy3) {
        ReportCheat();
    }
}
```

**绕过方法**:

```javascript
// bypass_integrity.js
// 绕过内存完整性检测

"use strict";

// 方法 1: Hook 完整性检测函数，让它永远返回 "正常"
// 在 dump.cs 中搜索: IntegrityCheck, AntiCheat, SecurityCheck
var il2cpp = Module.findBaseAddress("libil2cpp.so");

// 假设 IntegrityCheck 在 RVA 0x2A0000
var integrityCheck = il2cpp.add(0x2A0000);
Interceptor.replace(integrityCheck, new NativeCallback(function() {
    // 什么都不做，直接返回
    return;
}, "void", []));

// 方法 2: 如果游戏使用 CRC 校验代码段
// Hook CRC 计算函数，返回预期值
// 搜索 crc32, checksum, hash 等关键词

// 方法 3: 如果游戏使用值哨兵
// 修改值时，同时更新校验哨兵
function safeModifyCoin(instance, newValue) {
    var coinOffset = 0x10;
    var checksumOffset = 0x38;  // 需要逆向确定
    var MAGIC_KEY = 0xDEADBEEF;  // 需要逆向确定

    instance.add(coinOffset).writeS32(newValue);
    instance.add(checksumOffset).writeS32(newValue ^ MAGIC_KEY);
}
```

### 8.4 速度检测

```c
// 服务端速度检测伪代码
void OnClientAction(Action action, int64_t clientTimestamp) {
    int64_t serverTime = GetServerTime();
    int64_t timeDiff = abs(serverTime - clientTimestamp);

    // 检测 1: 客户端时间与服务器时间差异过大
    if (timeDiff > MAX_TIME_DIFF) {
        FlagSuspicious(player, "时间异常");
    }

    // 检测 2: 操作频率异常
    int64_t sinceLastAction = clientTimestamp - player.lastActionTime;
    if (sinceLastAction < MIN_ACTION_INTERVAL) {
        FlagSuspicious(player, "操作频率过高");
    }

    // 检测 3: 移动速度异常
    float distance = CalculateDistance(player.lastPos, action.newPos);
    float elapsed = (clientTimestamp - player.lastMoveTime) / 1000.0f;
    float speed = distance / elapsed;
    if (speed > MAX_ALLOWED_SPEED * 1.5f) {
        FlagSuspicious(player, "移动速度异常");
    }
}
```

### 8.5 常见第三方反作弊 SDK

| SDK | 常见游戏 | 检测 SO 库 | 特征 |
|-----|---------|-----------|------|
| 腾讯 ACE | 王者荣耀, PUBG Mobile | `libtersafe.so` | 内核级检测 |
| 网易安全 | 阴阳师, 荒野行动 | `libNetHTProtect.so` | 行为分析 |
| 梆梆安全 | 多款国产手游 | `libDexHelper.so` | 加固 + 反调试 |
| EasyAntiCheat | Fortnite, Apex | `libeac.so` | 进程扫描 |
| GameGuard | 多款韩国手游 | `libgameguard.so` | 根套件检测 |

---

## 9. 实战：修改游戏数值

本节以一个完整的流程演示如何从零开始找到并修改 Unity 游戏中的 HP / 金币 / 伤害。

### 9.1 完整流程概览

```
┌─────────────────────────────────────────────────────────────────┐
│                  Unity 游戏数值修改完整流程                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Step 1: 解包与识别                                              │
│  ├── 解压 APK                                                   │
│  ├── 确认 IL2CPP 后端                                           │
│  └── 提取 libil2cpp.so + global-metadata.dat                   │
│                                                                 │
│  Step 2: Dump 元数据                                            │
│  ├── 运行 Il2CppDumper                                         │
│  ├── (如 metadata 加密) -> 运行时 Dump                          │
│  └── 获取 dump.cs + DummyDll                                   │
│                                                                 │
│  Step 3: 静态分析定位目标                                        │
│  ├── 搜索关键类: PlayerData, GameManager, etc.                  │
│  ├── 找到目标方法的 RVA 偏移                                     │
│  ├── 找到目标字段的 Field Offset                                 │
│  └── (可选) IDA/Ghidra 分析方法实现                              │
│                                                                 │
│  Step 4: Frida Hook 验证                                        │
│  ├── Hook 目标方法，观察调用参数                                  │
│  ├── 确认偏移正确性                                              │
│  └── 理解游戏逻辑流程                                            │
│                                                                 │
│  Step 5: 编写修改脚本                                            │
│  ├── 修改方法参数/返回值                                         │
│  ├── 直接写入内存字段                                            │
│  └── 测试效果                                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 9.2 Step-by-Step 实战

**Step 1: 准备环境**

```bash
# 设备要求: 已 Root 的 Android 设备 + Frida Server 已部署

# 安装目标游戏
adb install target-game.apk

# 获取包名
adb shell pm list packages | grep game
# 输出: package:com.example.unitygame

# 提取已安装的 APK
adb shell pm path com.example.unitygame
# 输出: /data/app/com.example.unitygame-xxxxx/base.apk
adb pull /data/app/com.example.unitygame-xxxxx/base.apk game.apk
```

**Step 2: Dump 元数据**

```bash
# 解压
mkdir game_extracted && cd game_extracted
unzip ../game.apk

# 检查 metadata
xxd -l 8 assets/bin/Data/Managed/Metadata/global-metadata.dat
# 输出: 00000000: af1b b1fa 1d00 0000
# magic 正确，version 29，未加密

# 运行 Il2CppDumper
Il2CppDumper \
    lib/arm64-v8a/libil2cpp.so \
    assets/bin/Data/Managed/Metadata/global-metadata.dat \
    dump_output/

# 检查结果
ls dump_output/
# dump.cs  script.py  ghidra.py  il2cpp.h  DummyDll/  stringliteral.json
```

**Step 3: 在 dump.cs 中搜索目标**

```bash
# 搜索金币相关
grep -n -i "coin\|gold\|money\|currency" dump_output/dump.cs

# 搜索 HP 相关
grep -n -i "health\|hp\|hitpoint\|life" dump_output/dump.cs

# 搜索伤害相关
grep -n -i "damage\|attack\|atk\|hurt" dump_output/dump.cs

# 搜索单例/管理器
grep -n -i "instance\|manager\|controller\|singleton" dump_output/dump.cs
```

假设找到以下关键信息：

```csharp
// dump.cs 中找到的关键类

// === 玩家数据 ===
// Namespace: Game.Player
public class CharacterStats : MonoBehaviour  // TypeDefIndex: 2841
{
    public int gold; // 0x1C
    public int diamond; // 0x20
    public float currentHP; // 0x24
    public float maxHP; // 0x28
    public int attackPower; // 0x2C
    public int defense; // 0x30

    // RVA: 0x18A3F0
    public void AddGold(int amount) { }

    // RVA: 0x18A450
    public void SetHP(float value) { }

    // RVA: 0x18A4B0
    public float GetHP() { }

    // RVA: 0x18A510
    public void TakeDamage(float damage, bool isCritical) { }

    // RVA: 0x18A5E0
    public static CharacterStats get_LocalPlayer() { }
}

// === 战斗系统 ===
// Namespace: Game.Combat
public class DamageCalculator  // TypeDefIndex: 2900
{
    // RVA: 0x1B2000
    public static float Calculate(
        CharacterStats attacker,
        CharacterStats defender,
        int skillId) { }
}
```

**Step 4: 编写并运行 Frida 脚本**

```javascript
// game_hack.js
// 完整的游戏数值修改脚本

"use strict";

console.log("==============================");
console.log("  Unity Game Hack Script");
console.log("==============================");

function main() {
    var il2cpp = Module.findBaseAddress("libil2cpp.so");
    if (!il2cpp) {
        console.log("[-] Waiting for libil2cpp.so...");
        setTimeout(main, 2000);
        return;
    }
    console.log("[+] libil2cpp.so @ " + il2cpp);

    // ─────────────────────────────────────
    // 1. 获取玩家实例
    // ─────────────────────────────────────
    var getLocalPlayer = il2cpp.add(0x18A5E0);
    var playerInstance = null;

    Interceptor.attach(getLocalPlayer, {
        onLeave: function(retval) {
            if (!retval.isNull() && playerInstance === null) {
                playerInstance = retval;
                console.log("[+] Got player instance: " + playerInstance);
                dumpPlayerStats(playerInstance);
            }
        }
    });

    // ─────────────────────────────────────
    // 2. 金币修改: AddGold 增加量 x100
    // ─────────────────────────────────────
    var addGold = il2cpp.add(0x18A3F0);
    Interceptor.attach(addGold, {
        onEnter: function(args) {
            var original = args[1].toInt32();
            var modified = original * 100;
            args[1] = ptr(modified);
            console.log("[GOLD] " + original + " -> " + modified);
        }
    });

    // ─────────────────────────────────────
    // 3. 无敌模式: TakeDamage 伤害归零
    // ─────────────────────────────────────
    var takeDamage = il2cpp.add(0x18A510);
    Interceptor.attach(takeDamage, {
        onEnter: function(args) {
            // this = args[0], damage = args[1] (float as bits), isCritical = args[2]

            // 在 ARM64 上，float 参数可能通过浮点寄存器传递
            // 需要使用 this.context 来访问寄存器

            // 方法: 将 damage 设为 0
            // float 0.0 的二进制表示全为 0
            args[1] = ptr(0);

            console.log("[GOD] Damage blocked!");
        }
    });

    // ─────────────────────────────────────
    // 4. 伤害增强: 修改伤害计算结果
    // ─────────────────────────────────────
    var calcDamage = il2cpp.add(0x1B2000);
    Interceptor.attach(calcDamage, {
        onLeave: function(retval) {
            // 返回值是 float，需要特殊处理
            // ARM64 上 float 返回值在 s0 寄存器中
            // 但 Frida 的 retval 对 float 支持有限

            // 替代方案: 直接替换返回值
            // 使用 NativeFunction 来处理 float
        }
    });

    // ─────────────────────────────────────
    // 5. 使用 NativeFunction 调用游戏方法
    // ─────────────────────────────────────
    // 主动调用 AddGold 给自己加金币
    var addGoldFunc = new NativeFunction(
        il2cpp.add(0x18A3F0),
        "void",
        ["pointer", "int32", "pointer"]  // this, amount, MethodInfo
    );

    // 延迟调用 (等待获取到 player instance)
    setTimeout(function() {
        if (playerInstance) {
            console.log("[+] Calling AddGold(1000000)...");
            addGoldFunc(playerInstance, 1000000, ptr(0));
            console.log("[+] Done! Check your gold.");
            dumpPlayerStats(playerInstance);
        }
    }, 10000);
}

function dumpPlayerStats(instance) {
    console.log("──────── Player Stats ────────");
    console.log("  Gold:    " + instance.add(0x1C).readS32());
    console.log("  Diamond: " + instance.add(0x20).readS32());
    console.log("  HP:      " + instance.add(0x24).readFloat().toFixed(1) +
                " / " + instance.add(0x28).readFloat().toFixed(1));
    console.log("  ATK:     " + instance.add(0x2C).readS32());
    console.log("  DEF:     " + instance.add(0x30).readS32());
    console.log("──────────────────────────────");
}

// 启动
setTimeout(main, 3000);
```

**Step 5: 运行脚本**

```bash
# 方式 1: Spawn 模式 (从启动时注入)
frida -U -f com.example.unitygame -l game_hack.js --no-pause

# 方式 2: Attach 模式 (附加到已运行的游戏)
frida -U com.example.unitygame -l game_hack.js

# 输出:
# ==============================
#   Unity Game Hack Script
# ==============================
# [+] libil2cpp.so @ 0x7a3c000000
# [+] Got player instance: 0x7b12345678
# ──────── Player Stats ────────
#   Gold:    1500
#   Diamond: 50
#   HP:      100.0 / 100.0
#   ATK:     25
#   DEF:     10
# ──────────────────────────────
# [GOLD] 10 -> 1000
# [GOD] Damage blocked!
# [+] Calling AddGold(1000000)...
# [+] Done! Check your gold.
# ──────── Player Stats ────────
#   Gold:    1002500
#   Diamond: 50
#   HP:      100.0 / 100.0
#   ATK:     25
#   DEF:     10
# ──────────────────────────────
```

### 9.3 ARM64 浮点数处理技巧

在 ARM64 架构上，浮点参数通过 `d0-d7` / `s0-s7` 寄存器传递，而不是 `x0-x7`。Frida 的 `args[]` 数组无法直接读取浮点寄存器，需要特殊处理：

```javascript
// float_handling.js
// ARM64 浮点数参数处理

"use strict";

var il2cpp = Module.findBaseAddress("libil2cpp.so");

// 方法 1: 通过 this.context 访问浮点寄存器
var takeDamage = il2cpp.add(0x18A510);
Interceptor.attach(takeDamage, {
    onEnter: function(args) {
        // ARM64 浮点参数在 d0/s0 寄存器中
        // 注意: IL2CPP 中 this 在 x0, 第一个实际参数可能在 s0 或 x1
        // 取决于编译器的 ABI 决定

        // 读取 s0 寄存器 (float, 单精度)
        // Frida 中 context.d0 包含 double, 取低 32 位是 float
        if (this.context !== undefined) {
            // 某些 Frida 版本支持:
            // var damage = this.context.d0;  // as double
            // console.log("damage (from d0): " + damage);
        }
    }
});

// 方法 2: 使用 NativeFunction 正确声明参数类型
var takeDamageFunc = new NativeFunction(
    il2cpp.add(0x18A510),
    "void",
    ["pointer", "float", "bool", "pointer"]
    //  this      damage  isCrit  MethodInfo
);

// 方法 3: Interceptor.replace 替换整个函数
Interceptor.replace(il2cpp.add(0x18A510),
    new NativeCallback(function(thisPtr, damage, isCritical, methodInfo) {
        // 这里的 damage 已经是正确的 float 值了
        console.log("[*] TakeDamage: damage=" + damage + " crit=" + isCritical);

        // 调用原函数但修改参数
        takeDamageFunc(thisPtr, 0.0, false, methodInfo);
    }, "void", ["pointer", "float", "bool", "pointer"])
);
```

---

## 10. Mono 游戏逆向

虽然 IL2CPP 是主流，但仍有部分游戏（尤其是老游戏和独立游戏）使用 Mono 后端。Mono 游戏的逆向比 IL2CPP 简单得多。

### 10.1 Mono 游戏识别与文件结构

```
game_mono.apk (解压后)
├── lib/
│   └── armeabi-v7a/
│       ├── libmono.so              # Mono 运行时 (特征!)
│       ├── libmain.so
│       └── libunity.so
├── assets/
│   └── bin/
│       └── Data/
│           └── Managed/            # ★ DLL 直接存放在这里
│               ├── Assembly-CSharp.dll      # ★ 核心游戏逻辑
│               ├── Assembly-CSharp-firstpass.dll
│               ├── UnityEngine.dll
│               ├── mscorlib.dll
│               ├── System.dll
│               └── System.Core.dll
└── ...
```

> **关键区别**: Mono 游戏将 .NET DLL 直接打包在 APK 中，无需 Dump 就可以直接反编译！

### 10.2 使用 dnSpy 分析 Assembly-CSharp.dll

```
步骤:
1. 解压 APK
2. 提取 assets/bin/Data/Managed/Assembly-CSharp.dll
3. 用 dnSpy 打开

与 IL2CPP DummyDll 的区别:
- Mono 的 DLL 包含完整的 IL 字节码
- dnSpy 可以反编译出完整的方法实现 (不只是签名)
- 可以直接看到游戏逻辑的源码级伪代码
```

**dnSpy 中看到的效果:**

```csharp
// dnSpy 反编译 Mono 游戏的 Assembly-CSharp.dll
// 可以看到完整的方法实现!

namespace Game.Player
{
    public class PlayerStats : MonoBehaviour
    {
        public int gold;
        public float hp;
        public float maxHp;

        // 完整的方法实现 (不像 IL2CPP 只有签名)
        public void AddGold(int amount)
        {
            this.gold += amount;
            if (this.gold > 999999)
            {
                this.gold = 999999;
            }
            UIManager.Instance.UpdateGoldDisplay(this.gold);
            SaveManager.Save();
        }

        public void TakeDamage(float damage)
        {
            if (this.isInvincible) return;

            float actualDamage = damage - (float)this.defense * 0.5f;
            if (actualDamage < 1f) actualDamage = 1f;

            this.hp -= actualDamage;
            if (this.hp <= 0f)
            {
                this.hp = 0f;
                this.OnDeath();
            }

            UIManager.Instance.UpdateHPBar(this.hp / this.maxHp);
        }

        public bool CheckPurchase(string productId)
        {
            // 可以看到内购验证逻辑!
            if (PlayerPrefs.GetInt("purchased_" + productId, 0) == 1)
            {
                return true;
            }
            return IAPManager.Instance.VerifyPurchase(productId);
        }
    }
}
```

### 10.3 dnSpy 直接修改 DLL

dnSpy 不仅可以查看代码，还可以直接修改 IL 代码并保存：

```
修改步骤:
1. 在 dnSpy 中找到目标方法
2. 右键 -> Edit Method Body (编辑方法体)
   或 右键 -> Edit IL Instructions (编辑 IL 指令)
3. 修改代码
4. File -> Save Module (保存修改后的 DLL)
5. 将修改后的 DLL 放回 APK 中，重新签名

示例修改 (Edit Method Body):

// 原始代码:
public void TakeDamage(float damage) {
    this.hp -= damage;
    // ...
}

// 修改为:
public void TakeDamage(float damage) {
    // 不执行任何操作 = 无敌
    return;
}
```

```
IL 级别修改示例:

// 原始 IL:
// IL_0000: ldarg.0          // this
// IL_0001: ldarg.0          // this
// IL_0002: ldfld float32 PlayerStats::hp
// IL_0007: ldarg.1          // damage
// IL_0008: sub
// IL_0009: stfld float32 PlayerStats::hp

// 修改为 (直接返回):
// IL_0000: ret
```

### 10.4 Mono 游戏的运行时 Patch

如果不想重打包 APK（避免签名校验问题），可以用 Frida 在运行时 Patch Mono 方法：

```javascript
// mono_runtime_patch.js
// Mono 游戏运行时修改

"use strict";

// Mono 运行时提供了丰富的 API
var mono_get_root_domain = new NativeFunction(
    Module.findExportByName("libmono.so", "mono_get_root_domain"),
    "pointer", []);

var mono_domain_get_assemblies = new NativeFunction(
    Module.findExportByName("libmono.so", "mono_domain_assembly_open"),
    "pointer", ["pointer", "pointer"]);

var mono_class_from_name = new NativeFunction(
    Module.findExportByName("libmono.so", "mono_class_from_name"),
    "pointer", ["pointer", "pointer", "pointer"]);

var mono_class_get_method_from_name = new NativeFunction(
    Module.findExportByName("libmono.so", "mono_class_get_method_from_name"),
    "pointer", ["pointer", "pointer", "int"]);

var mono_compile_method = new NativeFunction(
    Module.findExportByName("libmono.so", "mono_compile_method"),
    "pointer", ["pointer"]);

// 获取已编译方法的 native code 地址后，可以用 Interceptor.attach Hook

function hookMonoMethod(namespace, className, methodName, paramCount) {
    // 通过 Mono API 查找方法
    var domain = mono_get_root_domain();

    // 枚举程序集找到 Assembly-CSharp
    var assemblies = Process.findModuleByName("libmono.so");
    // ... (需要遍历程序集)

    // 获取方法后编译并 Hook
    // var method = mono_class_get_method_from_name(klass, methodNamePtr, paramCount);
    // var compiled = mono_compile_method(method);
    // Interceptor.attach(compiled, { ... });
}

// 更简单的方法: 直接搜索 Mono 内部结构
// Mono 的 JIT 编译后的代码同样在内存中
// 可以通过 mono_jit_info_table_find 来查找
```

### 10.5 Mono vs IL2CPP 逆向对比总结

```
┌─────────────────────────────────────────────────────────────┐
│              Mono vs IL2CPP 逆向难度对比                      │
├──────────────────┬──────────────────┬───────────────────────┤
│      维度         │     Mono          │      IL2CPP          │
├──────────────────┼──────────────────┼───────────────────────┤
│  代码可读性       │  ★★★★★           │  ★★☆☆☆              │
│                  │  dnSpy 完整反编译  │  需 Dump+IDA 分析     │
├──────────────────┼──────────────────┼───────────────────────┤
│  修改难度         │  ★★★★★           │  ★★★☆☆              │
│                  │  直接修改 DLL      │  需要 Frida Hook     │
├──────────────────┼──────────────────┼───────────────────────┤
│  符号恢复         │  不需要            │  需要 Il2CppDumper   │
├──────────────────┼──────────────────┼───────────────────────┤
│  运行时 Hook      │  Mono API 丰富    │  需计算偏移          │
├──────────────────┼──────────────────┼───────────────────────┤
│  反重打包         │  签名校验          │  签名校验+代码校验   │
├──────────────────┼──────────────────┼───────────────────────┤
│  加密保护         │  DLL 加密          │  metadata 加密       │
│                  │  (Mono 加载时解密)  │  (il2cpp 加载时解密)  │
├──────────────────┼──────────────────┼───────────────────────┤
│  工具链           │  dnSpy             │  Il2CppDumper        │
│                  │  ILSpy             │  IDA Pro / Ghidra    │
│                  │  .NET Reflector     │  frida-il2cpp-bridge │
└──────────────────┴──────────────────┴───────────────────────┘
```

---

## 对抗与高级技巧

### 1. Metadata 加密对抗

- **现象**: Il2CppDumper 报错 `This file is not a valid metadata file`。
- **对抗**:
  - **Hook 加载函数**: 游戏必须在运行时解密 metadata 才能正常运行。Hook `libil2cpp.so` 中加载 metadata 的函数（通常是 `il2cpp::vm::MetadataCache::Register` 或相关初始化函数），Dump 出解密后的内存内容。
  - **分析解密逻辑**: 逆向 `libil2cpp.so` 的初始化流程，找到解密 metadata 的算法（通常是 XOR 或 AES），写脚本还原。

### 2. 函数地址混淆 / 动态计算

- **现象**: Il2CppDumper 导出的地址与内存中的实际地址不符。
- **对抗**:
  - 这通常是因为游戏在运行时动态修改了函数指针。
  - 使用 **Frida 的扫描功能**，根据机器码特征（Pattern Scanning）来定位函数，而不是依赖固定的偏移。

### 3. 反调试与完整性校验

- **现象**: 附加 Frida 后游戏崩溃或闪退。
- **对抗**:
  - 参考 **[反分析技术案例](case_anti_analysis_techniques.md)**，隐藏 Frida 特征，Bypass TracerPid 检测。
  - 使用 Magisk + Zygisk 模块在系统层面进行 Dump，规避应用层检测。

### 4. 字符串加密

- **现象**: `dump.cs` 中字符串字面量全部为空或乱码。
- **对抗**:
  ```javascript
  // 在运行时 Hook 字符串解密函数
  // 常见模式: 游戏自定义了 String.Create 或类似的工厂方法

  var stringDecrypt = il2cpp.add(0xXXXXXX); // 需要逆向确定
  Interceptor.attach(stringDecrypt, {
      onLeave: function(retval) {
          if (!retval.isNull()) {
              // IL2CPP 字符串结构: [Il2CppObject header][length][char data...]
              var length = retval.add(Process.pointerSize * 2).readInt();
              if (length > 0 && length < 1000) {
                  var str = retval.add(Process.pointerSize * 2 + 4)
                                  .readUtf16String(length);
                  console.log("[STR] " + str);
              }
          }
      }
  });
  ```

---

## 常用工具速查

| 工具 | 用途 | 链接 |
|------|------|------|
| **Il2CppDumper** | Dump IL2CPP 元数据 | https://github.com/Perfare/Il2CppDumper |
| **frida-il2cpp-bridge** | Frida IL2CPP Hook 框架 | https://github.com/vfsfitvnm/frida-il2cpp-bridge |
| **dnSpy** | .NET DLL 反编译/修改 | https://github.com/dnSpy/dnSpy |
| **IDA Pro** | 二进制分析 | https://hex-rays.com/ida-pro |
| **Ghidra** | 开源二进制分析 | https://ghidra-sre.org |
| **GameGuardian** | Android 内存修改 | https://gameguardian.net |
| **Il2CppInspector** | IL2CPP 分析 (替代品) | https://github.com/djkaty/Il2CppInspector |
| **Cpp2IL** | IL2CPP 反编译 | https://github.com/SamboyCoding/Cpp2IL |
| **AssetStudio** | Unity 资源提取 | https://github.com/Perfare/AssetStudio |

---

## 总结

Unity 游戏逆向的核心在于 **还原符号**。不同后端有不同的策略：

- **IL2CPP**: 使用 Il2CppDumper 还原 `global-metadata.dat` 中的类型信息，再结合 Frida 进行运行时 Hook。对抗加密时，优先尝试运行时内存 Dump。
- **Mono**: 直接用 dnSpy 反编译 `Assembly-CSharp.dll`，可以看到完整的源码级逻辑，甚至可以直接修改 DLL 重打包。

无论哪种后端，核心流程都是：**识别 -> Dump/反编译 -> 定位目标 -> Hook/修改 -> 验证效果**。

> **免责声明**: 本文仅用于安全研究和学习目的。未经授权修改他人应用可能违反法律法规和服务条款。请在合法合规的范围内使用这些技术。
