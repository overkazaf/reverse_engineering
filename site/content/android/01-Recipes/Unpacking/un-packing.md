---
title: "脱壳分析加固的 Android 应用"
date: 2025-03-22
type: posts
tags: ["Native层", "签名验证", "Frida", "SSL Pinning", "代理池", "Ghidra"]
weight: 10
---

# 脱壳分析加固的 Android 应用

> **📚 前置知识**
>
> 本配方涉及以下核心技术，建议先阅读相关章节：
>
> - **[APK 结构解析](../../04-Reference/Foundations/apk_structure.md)** - 理解 DEX、Manifest 等文件结构
> - **[加固厂商识别](../Anti-Detection/app_hardening_identification.md)** - 识别不同加固方案的特征

## 问题场景

你在逆向分析一个 App 时遇到了以下情况：

- ❌ **Jadx 打开 APK 后代码完全不可读**，全是混淆的类名或空方法
- ❌ **classes.dex 文件异常小** (几十 KB)，不符合应用实际规模
- ❌ **应用启动时检测到 Frida 并闪退**，常规 Hook 无法生效
- ❌ **AndroidManifest.xml 中的 Application 入口被替换**成可疑的壳类名
- ❌ **`assets` 或 `lib` 目录中存在加密文件**，如 `.dat`、`.bin` 或奇怪命名的 `.so` 文件

这些都是应用被**加固(加壳)**的典型特征。加固技术通过加密 DEX 文件、抽取方法体、虚拟化指令等手段，让静态分析工具无法直接读取原始代码。本配方将教你如何识别、脱壳并恢复被加固的应用。

---

## 工具清单

### 必需工具

- [x] **Frida** - 动态插桩框架
- [x] **frida-dexdump** - 自动化 DEX dumper ([GitHub](https://github.com/hluwa/frida-dexdump))
- [x] **ADB** - 设备通信工具
- [x] **Root 权限设备** 或模拟器 (必须)

### 可选工具

- ☐ **FUPK3** - 针对特定壳的专用脱壳工具
- ☐ **Youpk** - 较新的脱壳工具
- ☐ **PKid/ApkTool-Plus** - 加固类型识别工具
- ☐ **MT 管理器** - Android 端 APK 分析工具
- ☐ **IDA Pro/Ghidra** - Native 层分析 (SO 加固时需要)

---

## 前置条件

在开始前请确认：

✅ **设备已 Root** 并安装 Frida Server
✅ **了解 DEX 文件基本结构** (至少知道 magic number `0x6465780A`)
✅ **应用已安装**并能正常启动 (即使有反调试)
✅ **磁盘空间充足** (脱壳可能产生大量文件)

---

## 解决方案

### 核心原理

> **"代码运行必解密"**
>
> 无论加固技术多么复杂，加密后的代码最终都必须在内存中恢复成可执行的 DEX 格式，才能被 ART 执行。脱壳的核心思想是：**在代码被解密后、执行前的那一刻，从内存中将其 dump 出来。**

---

### 第 1 步: 识别加固类型 (5-10 分钟)

不同代际的加固技术需要不同的脱壳策略，先识别目标应用使用了什么加固技术。

#### 方法 A: 使用工具快速识别

```bash
# 使用 PKid (ApkTool-Plus) 检测
# 下载: https://github.com/rover12421/ApkToolPlus
java -jar ApkToolPlus.jar -pkid target.apk

# 输出示例:
# [+] 检测到加固厂商: 腾讯乐固 (Tencent Legu)
# [+] 加固类型: 第二代壳 (方法抽取)
```

#### 方法 B: 手动检测

```bash
# 1. 检查 AndroidManifest.xml 中的 Application 类
unzip -p target.apk AndroidManifest.xml | strings | grep -i "application"

# 可疑类名:
# com.tencent.StubShell.TxAppEntry (腾讯乐固)
# com.secneo.apkwrapper.ApplicationWrapper (梆梆 Security)
# com.baidu.protect.StubApplication (百度加固)

# 2. 检查 DEX 文件大小
unzip -l target.apk | grep classes.dex
# 如果 classes.dex < 100KB 且 App 功能复杂，很可能加壳

# 3. 检查可疑文件
unzip -l target.apk | grep -E "\.dat|\.bin|ijm_lib|secdata"
# 这些文件通常包含加密的原始 DEX

# 4. 检查 lib 目录中的可疑 SO
unzip -l target.apk | grep "lib/.*\.so" | grep -E "(exec|vmp|protect)"
```

#### 加固技术代际对照表

| 代际       | 时期      | 技术特点               | 典型厂商             | 识别特征                 | 脱壳难度 |
| ---------- | --------- | ---------------------- | -------------------- | ------------------------ | -------- |
| **第一代** | 2010-2015 | 整体 DEX 加密          | 早期爱加密、360      | Application 入口被替换   | 简单     |
| **第二代** | 2015-2018 | 方法抽取 (Stolen Code) | 腾讯乐固、阿里聚安全 | 大量空方法、libexec.so   | 中等     |
| **第三代** | 2018-2021 | 指令虚拟化 (VMP)       | 梆梆 VMP、顶象科技   | 自定义 VM 引擎、私有指令 | 困难     |
| **第四代** | 2021-至今 | 云端+多重保护          | 腾讯御安全、阿里云   | 云端下发代码、多层加壳   | 极难     |

---

### 第 2 步: 选择脱壳策略 (5 分钟)

根据识别出的加固类型，选择合适的脱壳方法：

#### 第一代壳 (整体加密)

**策略**: Hook ClassLoader，在 DEX 加载时 dump
**推荐工具**: 手写 Frida 脚本或 frida-dexdump
**成功率**: 95%+

#### 第二代壳 (方法抽取)

**策略**: Hook ArtMethod 的 invoke，在方法首次调用时 dump CodeItem
**推荐工具**: FART 技术 (Frida ART Hook) + frida-dexdump
**成功率**: 80%+ (取决于代码覆盖率)

#### 第三代壳 (虚拟化)

**策略**: Hook 虚拟机引擎，获取指令流 + 映射表逆向
**推荐工具**: IDA Pro + 自定义脚本
**成功率**: 50% (需要深入分析虚拟机实现)

#### 第四代壳 (云端)

**策略**: 网络抓包 + 内存扫描 + 多层 dump
**推荐工具**: mitmproxy + frida-dexdump + 自定义脚本
**成功率**: 30% (部分逻辑可能无法获取)

---

### 第 3 步: 执行脱壳 (10-60 分钟)

以下提供针对不同代际的脱壳脚本。

#### 方法 A: 使用 frida-dexdump (通用，推荐首选)

```bash
# 1. 启动 Frida Server
adb push frida-server /data/local/tmp/
adb shell "chmod 755 /data/local/tmp/frida-server"
adb shell "/data/local/tmp/frida-server &"

# 2. 安装 frida-dexdump
pip3 install frida-dexdump

# 3. 运行脱壳 (Spawn 模式，在 App 启动时拦截)
python3 -m frida_dexdump -U -f com.target.app -o ./output

# 输出示例:
# [+] Hooking ClassLoader...
# [+] Dumped DEX: /output/com.target.app_1234567890.dex (5.2 MB)
# [+] Dumped DEX: /output/com.target.app_0987654321.dex (1.8 MB)
# [+] Total: 2 DEX files dumped

# 4. 将 DEX 文件拉取到本地
adb pull /data/data/com.target.app/files/*.dex ./dumped_dex/
```

**参数说明**:

- `-U`: 使用 USB 连接的设备
- `-f com.target.app`: Spawn 模式启动应用
- `-o ./output`: 输出目录

---

#### 方法 B: 手写 Hook 脚本 (第一代壳)

适用于简单的整体加密壳。

```javascript
// unpacker_gen1.js - 第一代壳通用脚本

Java.perform(function () {
  console.log("[+] 开始 Hook ClassLoader...");

  // 拦截 1: DexClassLoader (最常见)
  var DexClassLoader = Java.use("dalvik.system.DexClassLoader");
  DexClassLoader.$init.implementation = function (
    dexPath,
    optimizedDirectory,
    librarySearchPath,
    parent
  ) {
    console.log("[+] DexClassLoader 加载 DEX:");
    console.log("    路径: " + dexPath);

    // 尝试复制 DEX 文件
    if (dexPath && dexPath.indexOf("/data/data/") !== -1) {
      try {
        var File = Java.use("java.io.File");
        var FileInputStream = Java.use("java.io.FileInputStream");
        var FileOutputStream = Java.use("java.io.FileOutputStream");

        var srcFile = File.$new(dexPath);
        if (srcFile.exists()) {
          var timestamp = Date.now();
          var dstPath =
            "/data/data/com.target.app/dumped_" + timestamp + ".dex";
          var dstFile = File.$new(dstPath);

          var fis = FileInputStream.$new(srcFile);
          var fos = FileOutputStream.$new(dstFile);

          var buffer = Java.array("byte", [1024]);
          var len;
          while ((len = fis.read(buffer)) > 0) {
            fos.write(buffer, 0, len);
          }

          fis.close();
          fos.close();

          console.log("✓ [已导出] " + dstPath);
        }
      } catch (e) {
        console.log("[-] 复制失败: " + e);
      }
    }

    return this.$init(dexPath, optimizedDirectory, librarySearchPath, parent);
  };

  // Hook 2: InMemoryDexClassLoader (内存加载)
  try {
    var InMemoryDexClassLoader = Java.use(
      "dalvik.system.InMemoryDexClassLoader"
    );
    InMemoryDexClassLoader.$init.overload(
      "java.nio.ByteBuffer",
      "java.lang.ClassLoader"
    ).implementation = function (byteBuffer, classLoader) {
      console.log("[+] InMemoryDexClassLoader 加载内存 DEX");

      // 从 ByteBuffer 提取 DEX
      try {
        var remaining = byteBuffer.remaining();
        console.log("    DEX 大小: " + remaining + " bytes");

        // 获取字节数组
        var bytes = Java.array("byte", [remaining]);
        byteBuffer.get(bytes);

        // 写入文件
        var timestamp = Date.now();
        var dstPath = "/data/data/com.target.app/memory_" + timestamp + ".dex";
        var File = Java.use("java.io.File");
        var FileOutputStream = Java.use("java.io.FileOutputStream");

        var dstFile = File.$new(dstPath);
        var fos = FileOutputStream.$new(dstFile);
        fos.write(bytes);
        fos.close();

        console.log("✓ [已导出] " + dstPath);

        // 重置 ByteBuffer 位置
        byteBuffer.position(0);
      } catch (e) {
        console.log("[-] 导出失败: " + e);
      }

      return this.$init(byteBuffer, classLoader);
    };
  } catch (e) {
    console.log("[-] InMemoryDexClassLoader 不存在 (Android < 8.0)");
  }

  console.log("[+] Hook 完成，等待 DEX 加载...");
});
```

**使用方法**:

```bash
# Spawn 模式 (推荐)
frida -U -f com.target.app -l unpacker_gen1.js --no-pause

# Attach 模式
frida -U com.target.app -l unpacker_gen1.js
```

---

#### 方法 C: FART 技术 (第二代壳 - 方法抽取)

FART (Frida-ART-Hook) 是针对方法抽取壳的高级技术。

```javascript
// unpacker_fart.js - FART (Frida-ART-Hook) 脚本

// 警告: 此脚本需要深入理解 ART 内部机制，不同 Android 版本可能需要调整偏移

var artMethodInvokeAddr = null;

// 根据 Android 版本查找 ArtMethod::Invoke 符号
var symbols = [
  "_ZN3art9ArtMethod6InvokeEPNS_6ThreadEPjjPNS_6JValueEPKc", // Android 7.0+
  "_ZN3art9ArtMethod6InvokeEPNS_6ThreadEPjmPNS_6JValueEPKc", // Android 8.0+
];

for (var i = 0; i < symbols.length; i++) {
  artMethodInvokeAddr = Module.findExportByName("libart.so", symbols[i]);
  if (artMethodInvokeAddr) {
    console.log("[+] 找到 ArtMethod::Invoke: " + artMethodInvokeAddr);
    break;
  }
}

if (!artMethodInvokeAddr) {
  console.log("[-] 未找到 ArtMethod::Invoke，无法继续");
} else {
  Interceptor.attach(artMethodInvokeAddr, {
    onEnter: function (args) {
      var artMethod = args[0];

      // 读取 ArtMethod 结构中的 CodeItem (偏移因版本而异)
      // 这里以 Android 7.0 为例，实际使用需要根据版本调整
      try {
        // 获取方法名 (通过 PrettyMethod)
        var prettyMethodAddr = Module.findExportByName(
          "libart.so",
          "_ZN3art9ArtMethod12PrettyMethodEv"
        );
        if (prettyMethodAddr) {
          var prettyMethod = new NativeFunction(prettyMethodAddr, "pointer", [
            "pointer",
          ]);
          var methodName = prettyMethod(artMethod).readCString();

          // 只关注 App 自身方法，忽略系统方法
          if (methodName && methodName.indexOf("com.target.app") !== -1) {
            console.log("[+] 调用方法: " + methodName);

            // 尝试获取 CodeItem
            // 注意: CodeItem 偏移在不同版本中不同
            // Android 7.0: offset 24
            // Android 8.0+: offset 16
            var codeItemOffset = 24; // 需要根据实际版本调整
            var codeItemPtr = artMethod.add(codeItemOffset).readPointer();

            if (codeItemPtr && !codeItemPtr.isNull()) {
              // 读取 CodeItem 结构
              var registersSize = codeItemPtr.readU16();
              var insSize = codeItemPtr.add(2).readU16();
              var outsSize = codeItemPtr.add(4).readU16();
              var triesSize = codeItemPtr.add(6).readU16();
              var insnsSize = codeItemPtr.add(12).readU32();

              if (insnsSize > 0 && insnsSize < 100000) {
                console.log("    找到 CodeItem: insnsSize = " + insnsSize);

                // 导出字节码
                var insnsPtr = codeItemPtr.add(16);
                var codeData = Memory.readByteArray(insnsPtr, insnsSize * 2);

                // 保存到文件
                var safeMethodName = methodName.replace(/[^a-zA-Z0-9]/g, "_");
                var filename =
                  "/data/data/com.target.app/code_" + safeMethodName + ".bin";
                var file = new File(filename, "wb");
                file.write(codeData);
                file.close();

                console.log("✓ [已导出 CodeItem] " + filename);
              }
            }
          }
        }
      } catch (e) {
        // 忽略读取错误
      }
    },
  });

  console.log("[+] FART Hook 已激活，开始监控方法调用...");
}
```

**注意事项**:

- 此技术需要较深的 ART 内部知识
- 只能 dump **被调用过的方法**，未触发的方法无法恢复

---

#### 方法 D: 内存扫描 (通用兜底方案)

当其他方法失效时，可以定期扫描内存中的 DEX magic number。

```javascript
// unpacker_memscan.js - 内存扫描脚本

function scanMemoryForDex() {
  console.log("[+] 开始扫描内存中的 DEX 文件...");

  var ranges = Process.enumerateRanges("r--"); // 仅扫描可读区域
  var found = 0;

  ranges.forEach(function (range) {
    try {
      // DEX magic: "dex\n" = 0x6465780A
      var pattern = "64 65 78 0a";

      Memory.scan(range.base, range.size, pattern, {
        onMatch: function (address, size) {
          console.log("[+] 发现潜在 DEX: " + address);

          try {
            // 读取 DEX 文件大小 (偏移 32 字节处)
            var dexSize = address.add(32).readU32();

            // 合理性检查
            if (dexSize > 0x1000 && dexSize < 50 * 1024 * 1024) {
              console.log(
                "    DEX Size: " + (dexSize / 1024).toFixed(2) + " KB"
              );

              // Dump DEX
              var dexData = Memory.readByteArray(address, dexSize);
              var filename =
                "/data/data/com.target.app/memdump_" +
                address.toString().replace("0x", "") +
                ".dex";
              var file = new File(filename, "wb");
              file.write(dexData);
              file.close();

              console.log("✓ [Dumped] " + filename);
              found++;
            }
          } catch (e) {
            // 读取失败，跳过
          }
        },
        onComplete: function () {},
      });
    } catch (e) {
      // 忽略无法访问的内存区域
    }
  });

  console.log("[+] 扫描完成，找到 " + found + " 个 DEX 文件");
}

// 每 5 秒扫描一次
setInterval(function () {
  scanMemoryForDex();
}, 5000);

console.log("[+] 内存扫描已启动");
```

---

### 第 4 步: 验证和修复 DEX (10-30 分钟)

脱壳后的 DEX 文件可能不完整或有损坏，需要验证和修复。

#### 验证步骤

```bash
# 1. 拉取导出的 DEX 文件
adb pull /data/data/com.target.app/ ./dumped_files/

# 2. 查看提取到的 DEX 文件
ls -lh ./dumped_files/*.dex
# 输出示例:
# -rw-r--r-- 1 user user 5.2M dumped_1234567890.dex
# -rw-r--r-- 1 user user 1.8M dumped_0987654321.dex

# 3. 验证 DEX 文件完整性
xxd ./dumped_files/dumped_1234567890.dex | head -n 2
# 应该看到 DEX magic: 64 65 78 0a (dex\n)

# 4. 使用 Jadx 打开验证
jadx ./dumped_files/dumped_1234567890.dex
# 如果能正常反编译，表示脱壳成功
```

#### 常见需要修复的情况

1. **方法体被 NOP 填充**:

   - 症状: Jadx 反编译后看到大量空方法或只有 `return` 的方法
   - 原因: 壳用占位符替换了真实代码
   - 解决: 如果用 FART dump 了 CodeItem，需要手动替换回去

2. **字符串池损坏**:

   - 症状: 反编译后字符串显示为乱码或缺失
   - 解决: 使用 `dex-repair` 工具重建字符串池

3. **类/方法索引错乱**:
   - 症状: 方法调用关系不正确
   - 解决: 使用 `smali/baksmali` 重新组装

#### 自动化修复工具

```bash
# 使用 dex-repair (开源工具)
git clone https://github.com/F8LEFT/dex-repair
cd dex-repair
python3 repair.py ./dumped_files/dumped_1234567890.dex -o ./fixed.dex

# 验证修复结果
jadx ./fixed.dex
```

#### 手动修复流程 (FART 方法抽取)

```bash
# 1. 将导出的 CodeItem 替换回 DEX
# 这需要使用 DexPatcher 或自定义脚本

# 2. 反汇编 DEX
baksmali d dumped_1234567890.dex -o ./smali_output

# 3. 查找空方法并替换
# 在 smali_output 中，找到方法体为空的 .smali 文件
# 将导出的 CodeItem 反汇编后的内容复制进去

# 4. 重新组装
smali a ./smali_output -o ./repacked.dex

# 5. 验证
jadx ./repacked.dex
```

---

## 原理深入

### 加固流程示意

```text
打包时加固流程:
┌─────────────────┐
│ 1. DEX 加密     │  将 classes.dex 加密为 encrypted.dat
└────────┬────────┘
         ↓
┌─────────────────┐
│ 2. 壳代替换     │  用壳 DEX 替换 classes.dex
└────────┬────────┘
         ↓
┌─────────────────┐
│ 3. 重新打包签名 │  生成加固后的 APK
└─────────────────┘

运行时解密流程:
Application.onCreate()
         ↓
    壳代码执行
         ↓
解密 encrypted.dat
         ↓
DexClassLoader.load(解密后的 DEX)
         ↓
跳转到原始 Application 入口
```

### 脱壳时机示意

```text
App 启动
    ↓
壳代码运行
    ↓
解密原始 DEX        ← Hook 点 1: ClassLoader
    ↓
ART 加载 DEX 到内存  ← Hook 点 2: libart.so
    ↓
编译为 OAT 格式
    ↓
类初始化和方法调用   ← Hook 点 3: ArtMethod::Invoke
    ↓
原始代码执行
```

---

## 常见问题

### ❌ 问题 1: frida-dexdump 无法 dump 任何文件

**可能原因**:

1. 壳检测到 Frida 并提前退出
2. Hook 时机太晚，DEX 已经加载完毕
3. 使用了非标准的加载方式

**解决方案**:

```bash
# 1. 先绕过 Frida 检测
frida -U -f com.target.app -l bypass_frida_detection.js --no-pause

# 等待应用启动后，再运行 dexdump (分两步)
frida -U com.target.app -l frida_dexdump_manual.js

# 2. 尝试更早的拦截点
# 修改 frida-dexdump 源码，在 libc.so fork() 之前就注入

# 3. 使用内存扫描作为兜底方案
frida -U com.target.app -l unpacker_memscan.js
```

### ❌ 问题 2: Dump 的 DEX 无法被 Jadx 识别

**可能原因**:

1. Dump 的时机不对，DEX 还未完全解密
2. DEX 文件被截断
3. 内存中的 DEX 已被修改 (如方法抽取)

**解决方案**:

```bash
# 1. 检查 DEX 文件头
xxd dumped.dex | head -n 5
# 前 4 字节必须是: 64 65 78 0a (dex\n)
# 后 4 字节是版本号: 30 33 35 00 (035) 或 30 33 38 00 (038)

# 2. 验证文件大小
# 偏移 32 字节处记录文件大小
dd if=dumped.dex bs=1 skip=32 count=4 | xxd
# 与实际文件大小对比

# 3. 尝试修复工具
dex-repair dumped.dex -o fixed.dex

# 4. 如果是方法抽取壳，需要用 FART 补全方法体
```

### ❌ 问题 3: FART 脚本导致应用崩溃

**可能原因**:

1. ArtMethod 结构偏移错误 (Android 版本不匹配)
2. 读取了无效的内存地址
3. Hook 符号错误

**解决方案**:

```javascript
// 1. 添加异常保护
Interceptor.attach(artMethodInvokeAddr, {
  onEnter: function (args) {
    try {
      var artMethod = args[0];
      // ... 你的代码
    } catch (e) {
      console.log("[-] 捕获异常: " + e);
      // 不要重新抛出，避免崩溃
    }
  },
});

// 2. 根据 Android 版本动态调整偏移
var androidVersion = Java.androidVersion;
var codeItemOffset;
if (androidVersion >= 10) {
  codeItemOffset = 16; // Android 10+
} else if (androidVersion >= 8) {
  codeItemOffset = 20; // Android 8-9
} else {
  codeItemOffset = 24; // Android 7
}

// 3. 检查指针有效性
if (codeItemPtr && !codeItemPtr.isNull()) {
  // 尝试读取前先检查是否可读
  try {
    Process.findRangeByAddress(codeItemPtr); // 会抛出异常如果地址无效
    var insnsSize = codeItemPtr.add(12).readU32();
    // ...
  } catch (e) {
    console.log("[-] 无效地址: " + codeItemPtr);
  }
}
```

### ❌ 问题 4: 方法抽取壳只 dump 出部分方法

**可能原因**:

1. FART 技术只能 dump 被调用过的方法
2. 部分方法在特定条件下才会触发

**解决方案**:

```bash
# 1. 使用 FART 技术 (见第 3 步方法 C)
# 必须触发所有关键方法调用才能完整导出

# 2. 手动触发方法调用
# 写一个测试脚本，遍历所有类的所有方法并调用

# 3. 使用专用工具
# FUPK3、Youpk 等工具已内置方法主动调用逻辑
```

**主动调用所有方法的脚本**:

```javascript
Java.perform(function () {
  Java.enumerateLoadedClasses({
    onMatch: function (className) {
      if (className.indexOf("com.target.app") !== -1) {
        try {
          var clazz = Java.use(className);
          var methods = clazz.class.getDeclaredMethods();

          methods.forEach(function (method) {
            try {
              // 尝试调用静态方法 (传空参数)
              console.log("[+] 尝试调用: " + method.getName());
              method.invoke(null, []);
            } catch (e) {
              // 忽略调用失败
            }
          });
        } catch (e) {}
      }
    },
    onComplete: function () {
      console.log("[+] 方法触发完成");
    },
  });
});
```

---

## 相关链接

### 相关配方

| 项目                                                                          | 说明                     |
| ----------------------------------------------------------------------------- | ------------------------ |
| [Recipe: 绕过 App 对 Frida 的检测](../Anti-Detection/frida_anti_debugging.md) | 脱壳前通常需要先过反调试 |
| [Recipe: 抓包分析 Android 应用的网络流量](../Network/network_sniffing.md)     | 脱壳后抓包分析加密逻辑   |
| [Recipe: SO 混淆与反混淆](./so_obfuscation_deobfuscation.md)                  | Native 层加固的处理      |

### 工具深入

- [Frida 内部原理](../../02-Tools/Dynamic/frida_internals.md) - 理解 Frida Hook 机制
- [Unidbg 使用指南](../../02-Tools/Dynamic/unidbg_guide.md) - 仿真执行 Native 解密函数

### 案例分析

> **💡 思路一句话**: 脱壳的本质是「在 DEX 被解密加载到内存后，从内存中 dump 出来」— 不同加固方案的壳不同，但 DEX 最终都要进入 ART 虚拟机执行，在这个时机点 dump 就对了。

- [案例: 某音乐 App 的加固分析](../../03-Case-Studies/case_music_apps.md)

### 参考资料

- [DEX 文件格式详解](../../04-Reference/Foundations/dex_format.md)
- [ART 运行时机制](../../04-Reference/Foundations/art_runtime.md)

---

## 快速参考

### 加固检测速查表

| 检测项               | 命令                                                        | 可疑特征                                             |
| -------------------- | ----------------------------------------------------------- | ---------------------------------------------------- |
| **Application 入口** | `unzip -p app.apk AndroidManifest.xml \| grep android:name` | `StubShell`, `ApplicationWrapper`, `StubApplication` |
| **DEX 文件大小**     | `unzip -l app.apk \| grep classes.dex`                      | < 100 KB (复杂应用)                                  |
| **加密数据文件**     | `unzip -l app.apk \| grep -E "\.dat\|\.bin"`                | `assets/` 下的 .dat/.bin 文件                        |
| **可疑 SO 库**       | `unzip -l app.apk \| grep "lib/.*\.so"`                     | `libexec.so`, `libvmp.so`, `libprotect.so`           |
| **使用 PKid**        | `java -jar ApkToolPlus.jar -pkid app.apk`                   | 直接输出加固厂商                                     |

### 常用脱壳命令

```bash
# 1. 使用 frida-dexdump (推荐)
python3 -m frida_dexdump -U -f com.target.app -o ./output

# 2. 手写脚本 (Spawn 模式)
frida -U -f com.target.app -l unpacker.js --no-pause

# 3. 内存扫描
frida -U com.target.app -l memscan.js

# 4. 拉取导出文件
adb pull /data/data/com.target.app/ ./dumped/

# 5. 验证 DEX 文件
xxd dumped.dex | head -n 2  # 检查 magic number
jadx dumped.dex             # 尝试反编译
```

### 常用工具

| 工具              | 用途               | 链接                                                |
| ----------------- | ------------------ | --------------------------------------------------- |
| **frida-dexdump** | 自动化 DEX dumper  | [GitHub](https://github.com/hluwa/frida-dexdump)    |
| **FUPK3**         | 针对特定壳的脱壳机 | [GitHub](https://github.com/F8LEFT/FUPK3)           |
| **Youpk**         | 较新的脱壳工具     | [GitHub](https://github.com/Youlor/Youpk)           |
| **PKid**          | 加固识别工具       | [GitHub](https://github.com/rover12421/ApkToolPlus) |
| **dex-repair**    | DEX 文件修复工具   | [GitHub](https://github.com/F8LEFT/dex-repair)      |

---

**💡 提示**: 脱壳是一个需要耐心和经验的过程。如果一种方法不奏效，尝试组合多种技术。记住，**代码运行必解密** - 只要应用能正常运行，理论上就能脱壳。
