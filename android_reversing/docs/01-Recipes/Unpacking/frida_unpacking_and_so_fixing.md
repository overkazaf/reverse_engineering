# 使用 Frida 脱壳加固 App 并修复 SO 文件

> **📚 前置知识**
>
> 本配方涉及以下核心技术，建议先阅读相关章节：
>
> - **[Frida 完整指南](../../02-Tools/Dynamic/frida_guide.md)** - 掌握 Frida 内存操作与 Hook
> - **[SO/ELF 格式](../../04-Reference/Foundations/so_elf_format.md)** - 理解 ELF 文件结构以进行修复

## 问题场景

**你遇到了什么问题？**

- 用 jadx 打开 APK，发现代码被混淆或看不到关键逻辑
- 🛡️ APK 使用了加固（加壳）保护，无法静态分析
- 📦 SO 文件被加密，IDA Pro 无法正确加载
- 你想获取 App 运行时真正的 DEX 文件
- 🧩 需要分析 Native 层代码，但 SO 文件已被加壳

**本配方教你**：使用 Frida 动态脱壳加固 App、Dump 内存中的 DEX 和 SO 文件、修复文件格式以供分析。

**核心理念**：

> 💡 **动态脱壳：在运行时获取已解密的代码**
>
> - 加壳只是静态保护，运行时必然会解密
> - Frida 可以在 DEX/SO 加载时 dump 内存
> - 修复文件格式后即可用传统工具分析
> - 绕过所有加固方案的通用方法

**预计用时**: 30-60 分钟

---

## 工具清单

### 必需工具

- ☐ **Frida** - 动态插桩框架
- ☐ **Android 设备**（已 Root）或模拟器
- ☐ **Python 3.7+** - 运行 Frida 脚本
- ☐ **jadx-gui** - 分析脱壳后的 DEX

### 可选工具

- ☐ **IDA Pro / Ghidra** - 分析 SO 文件
- ☐ **frida-dexdump** - 自动化 DEX 脱壳
- ☐ **FRIDA-DEXDump** - 另一个流行的脱壳工具
- ☐ **SoFixer** - 修复 dump 的 SO 文件

---

## 前置条件

### ✅ 确认清单

```bash
# 1. Frida 正常运行
frida-ps -U

# 2. Python 环境
python3 --version

# 3. jadx-gui 已安装
jadx-gui --version

# 4. 检查设备 root 状态
adb shell su -c 'id'
# 应该显示 uid=0(root)
```

### 识别 App 是否加固

**方法 1：jadx 查看**

打开 APK，如果看到：

- 只有几个类和方法
- 有 `StubApp`、`ProxyApplication` 等字样
- MainActivity 逻辑异常简单

**方法 2：查看 SO 文件**

```bash
# 解压 APK
unzip app.apk -d app_unzipped

# 查看 lib 目录
ls app_unzipped/lib/arm64-v8a/

# 常见加固壳 SO 文件名
# libjiagu.so (360加固)
# libDexHelper.so (梆梆加固)
# libtup.so (腾讯加固)
# libexec.so (爱加密)
```

---

## 解决方案

### 第 1 步：使用 frida-dexdump 脱壳（10 分钟）

#### 1.1 安装 frida-dexdump

```bash
# 克隆项目
git clone https://github.com/hluwa/frida-dexdump.git
cd frida-dexdump

# 安装依赖
pip3 install frida frida-tools
```

#### 1.2 运行脱壳

```bash
# -f: 启动应用
# --no-pause: 不暂停，立即运行
python3 main.py -U -f com.example.app

# 脚本会自动：
# 1. 启动应用
# 2. Hook DEX 加载函数
# 3. 导出所有已加载的 DEX 文件
# 4. 保存到当前目录
```

**输出示例**：

```text
[DEXDump] Dumping DEX file: 0x7abc000000, size: 4562314
[DEXDump] Saved: com.example.app_classes.dex
[DEXDump] Found DEX: /data/app/.../base.apk!classes2.dex
[DEXDump] Dumping DEX file: 0x7abc500000, size: 2314567
[DEXDump] Saved: com.example.app_classes2.dex
[DEXDump] Total: 2 DEX files dumped
```

#### 1.3 验证脱壳结果

```bash
# 用 jadx 打开
jadx-gui com.example.app_classes.dex
```

---

### 第 2 步：使用 FRIDA-DEXDump（备选方案）（10 分钟）

如果 frida-dexdump 不工作，可以尝试 FRIDA-DEXDump：

```bash
# 安装
git clone https://github.com/lasting-yang/frida_dump.git
cd frida_dump

# 运行命令
python3 dump_dex.py -U -f com.example.app
```

---

### 第 3 步：手动脚本脱壳（高级）（15 分钟）

如果自动化工具失败，可以编写自定义 Frida 脚本。

#### 3.1 Hook OpenCommon（适用于 Android 8.0+）

**dex_dump.js**：

```javascript
function dumpDex() {
  Java.perform(function () {
    console.log("[*] DEX Dumper started");

    // 查找 libart.so
    var libart = Process.findModuleByName("libart.so");
    if (!libart) {
      console.log("[-] libart.so not found");
      return;
    }

    // Hook OpenCommon (Android 8.0+)
    // 符号名称因版本而异，需要用 nm 或 readelf 确认
    var OpenCommon = null;

    // 尝试常见符号
    var symbols = [
      "_ZN3art7DexFile10OpenCommonEPKhjS2_jRKNS_10OatDexFileEbbPS1_",
      "_ZN3art7DexFile10OpenCommonEPKhmS2_jRKNS_10OatDexFileEbbPS1_NS_6Handle",
    ];

    for (var i = 0; i < symbols.length; i++) {
      OpenCommon = Module.findExportByName("libart.so", symbols[i]);
      if (OpenCommon) {
        console.log("[+] Found OpenCommon:", OpenCommon);
        break;
      }
    }

    if (!OpenCommon) {
      console.log("[-] OpenCommon not found");
      return;
    }

    // Hook
    Interceptor.attach(OpenCommon, {
      onEnter: function (args) {
        // args[0] = base (DEX 内存地址)
        // args[1] = size (DEX 文件大小)

        var base = args[0];
        var size = args[1].toInt32();

        console.log("[*] 检测到 DEX!");
        console.log("    基址: " + base);
        console.log("    大小: " + size);

        // 读取 DEX 文件头，验证魔数
        var magic = base.readCString(4);
        if (magic === "dex\n") {
          console.log("    Magic: " + magic + " ✓");

          // Dump DEX
          var dexBytes = base.readByteArray(size);
          var fileName = "/sdcard/" + size + ".dex";

          var file = new File(fileName, "wb");
          file.write(dexBytes);
          file.close();

          console.log("[+] DEX dumped to: " + fileName);
        } else {
          console.log("    Invalid magic: " + magic);
        }
      },
    });

    console.log("[*] Hooks installed, waiting for DEX load...");
  });
}

setImmediate(dumpDex);
```

**使用方法**：

```bash
# 运行脚本
frida -U -f com.example.app -l dex_dump.js --no-pause

# 拉取到本地
adb pull /sdcard/*.dex .
```

#### 3.2 查找正确的符号名

```javascript
Module.enumerateExports("libart.so").forEach(function (exp) {
  if (exp.name.includes("DexFile") && exp.name.includes("Open")) {
    console.log(exp.name, exp.address);
  }
});
```

---

### 第 4 步：Dump SO 文件（10 分钟）

#### 4.1 查看已加载的 SO

```bash
# 查看进程加载的 SO 文件
frida -U -f com.example.app
```

在 REPL 中输入：

```javascript
Process.enumerateModules().forEach(function (m) {
  if (m.name.includes("native") || m.name.includes("encrypt")) {
    console.log(m.name, m.base, m.size);
  }
});

// 输出示例:
// libnative-lib.so 0x7abc000000 0x50000
```

#### 4.2 Dump SO 内存

```javascript
function dumpSo(moduleName) {
  var module = Process.findModuleByName(moduleName);
  if (!module) {
    console.log("[-] Module not found: " + moduleName);
    return;
  }

  console.log("[+] 找到模块:", moduleName);
  console.log("    基址: " + module.base);
  console.log("    大小: " + module.size);

  // 导出整个模块
  var buffer = module.base.readByteArray(module.size);
  var fileName = "/sdcard/" + moduleName;

  var file = new File(fileName, "wb");
  file.write(buffer);
  file.close();

  console.log("[+] 已导出到: " + fileName);
}

// 使用
dumpSo("libnative-lib.so");
```

**拉取文件**：

```bash
adb pull /sdcard/libnative-lib.so .
```

#### 4.3 使用 frida-all-in-one（推荐）

```bash
# 克隆项目
git clone https://github.com/hookmaster/frida-all-in-one.git
cd frida-all-in-one

# 运行命令
python3 dump_so.py -U com.example.app libnative-lib.so

# 会自动导出并修复 SO 文件
```

---

### 第 5 步：修复 SO 文件（10 分钟）

从内存 dump 的 SO 文件可能缺少 ELF 头信息，需要修复。

#### 5.1 使用 SoFixer

```bash
# 下载
git clone https://github.com/F8LEFT/SoFixer.git
cd SoFixer

# 编译（需要 CMake）
mkdir build && cd build
cmake ..
make

# 使用
./SoFixer ../libnative-lib.so ../libnative-lib_fixed.so
```

**输出示例**：

```text
[+] Detected architecture: ARM64
[+] Rebuilding ELF header...
[+] Fixing section table...
[+] Fixing dynamic symbols...
[+] Output file: libnative-lib_fixed.so
[+] Done!
```

#### 5.2 验证修复结果

```bash
# 检查文件类型
file libnative-lib_fixed.so
# 应该显示: ELF 64-bit LSB shared object, ARM aarch64...

# 用 IDA Pro 打开
# 或用 readelf 查看
readelf -h libnative-lib_fixed.so
```

---

## 原理深入

### DEX 脱壳原理

```text
App 启动
    ↓
壳代码加载
    ↓
解密原始 DEX（在内存中）
    ↓
调用 DexFile::OpenCommon 加载 DEX ← Frida Hook 点
    ↓
Frida 读取内存中的 DEX 数据
    ↓
保存到文件
```

### OpenCommon 函数签名

```cpp
// Android 8.0+ 的 OpenCommon 签名（简化）
static std::unique_ptr<DexFile> OpenCommon(
    const uint8_t* base,  // DEX 内存基址
    size_t size,          // DEX 大小
    ...
)
```

### SO Dump 原理

```text
内存中的 SO 布局:
[ELF Header]   ← 可能被壳破坏
[.text 段]
[.data 段]
[.rodata 段]
...
[Symbol Table] ← 需要重建
[String Table] ← 需要重建
```

直接 dump 内存只能获取段数据，缺少完整 ELF 结构，所以需要 SoFixer 修复。

### 常见加固壳识别

| 加固厂商 | SO 文件名       | 特点     |
| -------- | --------------- | -------- |
| 360 加固 | libjiagu.so     | 整体加密 |
| 梆梆加固 | libDexHelper.so | 方法抽取 |
| 腾讯加固 | libtup.so       | VMP 保护 |
| 爱加密   | libexec.so      | 多层加密 |
| 网易易盾 | libnesec.so     | 云端保护 |

**通用策略**：所有加固都需要在运行时解密，Frida 脱壳对所有方案都有效！

---

## 常见问题

### ❌ 问题 1: frida-dexdump 报错 "Failed to spawn"

**症状**：无法启动应用

**解决**：

```bash
# 1. 确认应用已安装
adb shell pm list packages | grep example

# 2. 确认包名正确
# 从 AndroidManifest.xml 获取准确包名

# 3. 尝试 Attach 模式
# 先手动启动应用
adb shell am start -n com.example.app/.MainActivity

# 再附加
python3 main.py -U com.example.app
```

### ❌ 问题 2: Dump 的 DEX 无法用 jadx 打开

**可能原因**：DEX 头部损坏

**解决步骤**：

1. **检查魔数**
    ```bash
    xxd dumped.dex | head -1
    # 应该看到: 64 65 78 0a (dex\n)
    ```
2. **验证 DEX 大小**
    ```python
    # 验证 DEX 大小
    with open('dumped.dex', 'rb') as f:
        f.seek(32)  # 跳到 file_size 字段
        size = int.from_bytes(f.read(4), 'little')
        print(f"DEX 声明的大小: {size}")

    import os
    actual_size = os.path.getsize('dumped.dex')
    print(f"实际文件大小: {actual_size}")
    ```
3. **使用 dexrepair 修复**
    ```bash
    git clone https://github.com/anestisb/dexrepair.git
    python3 dexrepair/dexrepair.py dumped.dex fixed.dex
    ```

### ❌ 问题 3: Hook 点没有触发

**检查步骤**：

1. **确认 libart.so 已加载**
    ```javascript
    var libart = Process.findModuleByName("libart.so");
    console.log("libart found:", libart !== null);
    ```
2. **列出所有 OpenCommon 符号**
    ```javascript
    Module.enumerateExports("libart.so").forEach(function (exp) {
      if (exp.name.includes("OpenCommon")) {
        console.log(exp.name);
      }
    });
    ```
3. **尝试其他 Hook 点**
    ```javascript
    // Android 7.0-
    var OpenMemory = Module.findExportByName(
      "libart.so",
      "_ZN3art7DexFile10OpenMemoryEPKhjRKNSt3__112basic_stringIcNS3_11char_traitsIcEENS3_9allocatorIcEEEEjPNS_6MemMapEPKNS_10OatDexFileEPS9_"
    );
```

### ❌ 问题 4: SO 文件修复后 IDA 仍无法分析

**症状**：IDA 打开后只显示数据，没有函数

**解决**：

1. **手动定义函数**
    在 IDA 中：
    - 光标移到疑似函数起始处
    - 按 'P' 键创建函数
    - 按 'C' 键转换为代码
2. **使用符号恢复工具**
    ```bash
    # 如果原始 SO 有符号表
    readelf -s original.so > symbols.txt

    # 用 IDA 脚本导入符号
    ```
3. **检查是否有 OLLVM 混淆**
    - 如果看到大量跳转和无意义的代码块
    - 可能是 OLLVM 控制流平坦化
    - 参考：[OLLVM 反混淆](../Analysis/ollvm_deobfuscation.md)

### ❌ 问题 5: App 检测到 Frida 并崩溃

**症状**：启动后立即退出，logcat 显示反调试提示

**解决**：

参考 [Frida 反调试绕过](../Anti-Detection/frida_anti_debugging.md)

快速方法：

```bash
# 使用 Magisk Hide
# 或使用修改版 Frida 服务器
wget https://github.com/hluwa/strongR-frida-android/releases/download/xxx/frida-server
```

---

## 相关链接

### 相关 Recipe

- **[应用脱壳总览](./un-packing.md)** - 各种脱壳技术对比
- **[Frida 反调试绕过](../Anti-Detection/frida_anti_debugging.md)** - 处理反 Frida 检测
- **[SO 混淆分析](./so_obfuscation_deobfuscation.md)** - 分析混淆的 SO 文件
- **[OLLVM 反混淆](../Analysis/ollvm_deobfuscation.md)** - 处理控制流混淆

### 工具深入

- **[Frida 完整指南](../../02-Tools/Dynamic/frida_guide.md)**
- **[IDA Pro 使用](../../02-Tools/Static/ida_pro_guide.md)**

### 项目资源

| 项目                 | 说明            | 链接                                           |
| -------------------- | --------------- | ---------------------------------------------- |
| **frida-dexdump**    | 自动化 DEX 脱壳 | https://github.com/hluwa/frida-dexdump         |
| **FRIDA-DEXDump**    | 深度 DEX 脱壳   | https://github.com/lasting-yang/frida_dump     |
| **SoFixer**          | SO 文件修复     | https://github.com/F8LEFT/SoFixer              |
| **frida-all-in-one** | 综合工具集      | https://github.com/hookmaster/frida-all-in-one |

### 理论基础

- **[DEX 文件格式](../../04-Reference/Foundations/dex_format.md)**
- **[SO/ELF 文件格式](../../04-Reference/Foundations/so_elf_format.md)**
- **[ART 运行时](../../04-Reference/Foundations/art_runtime.md)**

---

## 快速参考

### 脱壳工具对比

| 工具              | 类型   | 难度 | 特点               |
| ----------------- | ------ | ---- | ------------------ |
| **frida-dexdump** | 自动化 | 简单 | 简单，支持多版本   |
| **FRIDA-DEXDump** | 自动化 | 简单 | 深度搜索，更全面   |
| **手动脚本**      | 定制   | 中等 | 灵活，适合特殊情况 |
| **objection**     | 交互式 | 简单 | 多功能，含脱壳     |

### 一键脱壳脚本

**auto_unpack.sh**：

```bash
#!/bin/bash

PACKAGE=$1

if [ -z "$PACKAGE" ]; then
    echo "用法: $0 <package_name>"
    exit 1
fi

echo "🔓 开始脱壳: $PACKAGE"

# 1. Dump DEX
echo ""
echo "📦 导出 DEX 文件..."
python3 ~/tools/frida-dexdump/main.py -U -f $PACKAGE

# 2. Dump SO
echo ""
echo "📚 导出 SO 文件..."
frida -U -f $PACKAGE -l dump_all_so.js --no-pause

sleep 5

# 3. 拉取文件
echo ""
echo "📥 拉取文件..."
adb pull /sdcard/*.dex .
adb pull /sdcard/*.so .

# 4. 清理
adb shell rm /sdcard/*.dex
adb shell rm /sdcard/*.so

echo ""
echo "✅ 完成! 文件已保存到当前目录"
ls -lh *.dex *.so
```

### dump_all_so.js

```javascript
function dumpAllSo() {
  var modules = Process.enumerateModules();
  console.log("[*] 找到 " + modules.length + " 个模块");

  modules.forEach(function (module) {
    // 只导出 .so 文件
    if (!module.name.endsWith(".so")) {
      return;
    }

    // 排除系统库
    if (module.path.startsWith("/system") || module.path.startsWith("/apex")) {
      return;
    }

    console.log("[+] 导出: " + module.name);
    console.log("    路径: " + module.path);
    console.log("    基址: " + module.base);
    console.log("    大小: " + module.size);

    try {
      var buffer = module.base.readByteArray(module.size);
      var fileName = "/sdcard/" + module.name;
      var file = new File(fileName, "wb");
      file.write(buffer);
      file.close();
      console.log("    已保存: " + fileName);
    } catch (e) {
      console.log("    错误: " + e);
    }
  });

  console.log("[*] 完成!");
}

setImmediate(dumpAllSo);
```

---

**💡 提示**: 脱壳是一个反复试错的过程。如果一种方法不起作用，尝试其他方法或工具。大多数加固方案都可以通过 Frida 动态脱壳绕过。
