---
title: "主流应用加固厂商及其特征识别"
date: 2025-01-22
type: posts
tags: ["代理池", "SSL Pinning", "加密分析", "脱壳", "Android", "Root检测"]
weight: 10
---

# 主流应用加固厂商及其特征识别

> **📚 前置知识**
>
> 本配方涉及以下核心技术，建议先阅读相关章节：
>
> - **[APK 结构解析](../../04-Reference/Foundations/apk_structure.md)** - 理解 DEX、SO、Manifest 等文件
> - **[Jadx 反编译指南](../../02-Tools/Static/jadx_guide.md)** - 使用反编译工具查看代码特征

Android 应用加固是一种保护 App 不被轻易逆向、篡改或攻击的技术手段。对于逆向工程师而言，在开始分析一个 App 之前，**首要任务就是识别出它所使用的加固厂商**，因为不同的加固方案需要不同的脱壳和分析策略。

本指南旨在系统性地总结中国市场主流加固厂商的静态特征"指纹"，帮助分析人员快速识别目标。

---

## 通用识别思路

识别加固厂商通常遵循以下静态分析路径：

1. **检查 DEX 文件**：解压 APK，查看主 `classes.dex` 文件的大小。如果它非常小（通常小于 1MB），而 APK 本身体积很大，那么它很可能是一个"壳"，负责加载真正的、被加密隐藏起来的 DEX。
2. **检查 SO 库**：查看 `lib/[arch]/` 目录下的 `.so` 文件列表。加固厂商通常会放入带有自身品牌标识的 SO 库，这是最明显的特征。
3. **检查 `assets` 目录**：很多加固方案会将加密后的 DEX 文件、配置文件或其他组件放入 `assets` 目录。
4. **检查 `AndroidManifest.xml`**：加固方案通常会用自己的代理 `Application` 类替换掉原始的 `Application` 类。检查 `application` 标签下的 `android:name` 属性，可以找到代理类的名字，其包名往往暴露厂商信息。

```text
+------------------+     +------------------+     +------------------+
|  解压 APK        | --> |  检查 DEX 大小    | --> |  DEX < 1MB?      |
|  (unzip/apktool) |     |  ls -la *.dex    |     |  是 -> 可能加固   |
+------------------+     +------------------+     +------------------+
         |                                               |
         +-------->  检查 lib/ SO 文件  -----> 匹配厂商特征库
         |                                               |
         +-------->  检查 assets 目录   -----> 匹配加密文件特征
         |                                               |
         +-------->  检查 Manifest      -----> 匹配 Application 类名
                                                         |
                                                  APKiD 交叉验证
```

---

## 主流厂商特征详解

### 梆梆安全 (Bangcle)

- **SO 库特征**: `libSecShell.so`、`libsecexe.so`、`libsecmain.so`、`libDexHelper.so`
- **Java 层特征**: 代理类 `com.bangcle.protect` 或 `com.secshell.shell`
- **`assets` 目录特征**: `bangcle_classes.jar`、`secData0.jar`

### 360 加固 (Qihoo 360)

- **SO 库特征**: `libjiagu.so`、`libprotectClass.so`、`libjiagu_art.so`
- **Java 层特征**: `com.qihoo.util`、`com.stub.StubApp`
- **`assets` 目录特征**: `libjiagu.so`（有时放在 assets 里）、`.jiagu` 后缀文件

### 腾讯乐固 (Tencent Legu)

- **SO 库特征**: `liblegu.so`、`libshella-xxxx.so`（xxxx 为版本号）、`libshellx-xxxx.so`
- **Java 层特征**: `com.tencent.bugly.legu`、`com.tencent.StubShell.TxAppEntry`
- **`assets` 目录特征**: `legu_data.so`、`tosversion`
- **其他**: DEX 文件头被修改为 `legu`

### 网易易盾 (Netease Yidun)

- **SO 库特征**: `libnesec.so`（最核心特征）、`libnetease.so`
- **Java 层特征**: `com.netease.nis.wrapper.MyApplication`
- **`assets` 目录特征**: `nesec.dat`、`classes.dex.ys`

### 爱加密 (Ijiami)

- **SO 库特征**: `libexec.so`、`libexecmain.so`、`libijiami.so`
- **Java 层特征**: `com.ijiami.client.protect`
- **`assets` 目录特征**: `ijiami.dat`、`ijm_lib` 目录

### 娜迦 (Nagain / NAGA)

- **SO 库特征**: `libchaosvmp.so`、`libnagavm.so`、`libddog.so`
- **Java 层特征**: `com.nagain.protect`
- **`assets` 目录特征**: `nagain.dat`、`classes.dex.dat`

### 几维安全 (Kiwisec)

- **SO 库特征**: `libkwscmm.so`、`libkwscr.so`、`libkwslinker.so`
- **Java 层特征**: 包名含 `com.kiwisec`
- **`assets` 目录特征**: `kiwi.dat`

---

## 加固厂商识别指纹总表

| 加固厂商     | 核心 SO 特征                        | Manifest Application 类                | `assets` 特征              |
| :----------- | :---------------------------------- | :------------------------------------- | :------------------------- |
| **梆梆安全** | `libSecShell.so`                    | `com.secshell.secData.ShellApplication`| `bangcle_classes.jar`      |
| **360 加固** | `libjiagu.so`, `libprotectClass.so` | `com.stub.StubApp`                     | `.jiagu` 文件              |
| **腾讯乐固** | `liblegu.so`, `libshella-*.so`      | `com.tencent.StubShell.TxAppEntry`     | `legu_data.so`             |
| **网易易盾** | `libnesec.so`                       | `com.netease.nis.wrapper.MyApplication`| `nesec.dat`                |
| **爱加密**   | `libexec.so`, `libijiami.so`        | `com.shell.NativeApplication`          | `ijiami.dat`               |
| **娜迦**     | `libchaosvmp.so`, `libddog.so`      | `com.nagain.NagainApplication`         | `nagain.dat`               |
| **几维安全** | `libkwscmm.so`                      | 含 `kiwi` 关键字                       | `kiwi.dat`                 |
| **顶象**     | `libx3g.so`, `libdxbase.so`         | 含 `dingxiang` 关键字                  | `dx_res/`                  |
| **通付盾**   | `libegis.so`                        | 含 `egis` 关键字                       | `egis.dat`                 |

---

## 识别方法

### Manifest 检查

```bash
# 快速查看 Application 类名
aapt dump xmltree target.apk AndroidManifest.xml | grep "android:name"
```

### lib 目录分析

```bash
# 列出所有 SO 文件
unzip -l target.apk | grep "\.so$"
```

| SO 文件名关键字        | 加固厂商 |
| :--------------------- | :------- |
| `jiagu`                | 360      |
| `legu` / `shella`      | 腾讯乐固 |
| `SecShell` / `secexe`  | 梆梆安全 |
| `nesec`                | 网易易盾 |
| `ijiami`               | 爱加密   |
| `chaosvmp` / `ddog`    | 娜迦     |
| `kwscmm`               | 几维安全 |

### DEX 文件头检查

```bash
# 正常 DEX 头为 "dex\n035"，被修改则说明加固
xxd classes.dex | head -1
# legu -> 腾讯乐固 | 全零 -> 梆梆/爱加密
```

### APKiD 自动识别

```bash
pip install apkid
apkid target.apk          # 基本扫描
apkid -j target.apk       # JSON 输出
apkid -r ./apk_samples/   # 批量扫描
```

---

## 各加固方案特征对比

| 特性           | 360 加固     | 腾讯乐固     | 梆梆安全     | 爱加密       | 网易易盾     | 娜迦         | 几维安全     |
| :------------- | :----------- | :----------- | :----------- | :----------- | :----------- | :----------- | :----------- |
| **DEX 加密**   | 整体加密     | 整体加密     | 整体+抽取    | 整体加密     | 整体+VMP     | 整体+VMP     | 整体加密     |
| **DEX VMP**    | 部分函数     | 部分函数     | 支持         | 支持         | 深度 VMP     | 深度 VMP     | 核心方案     |
| **SO 混淆**    | 基础         | 基础         | OLLVM 变种   | OLLVM        | 深度定制     | 深度定制     | VMP 虚拟化   |
| **Anti-Debug** | ptrace+时间  | ptrace       | 多层检测     | ptrace+信号  | 内核级       | 多层检测     | 多层检测     |
| **Anti-Hook**  | GOT/PLT 检测 | 基础         | Inline 检测  | GOT 检测     | 全面检测     | 全面检测     | VMP 保护     |
| **Anti-Frida** | 端口+进程    | 基础         | maps+端口    | 端口检测     | 全面检测     | maps+内存    | maps+端口    |
| **保护强度**   | ★★★☆☆     | ★★★☆☆     | ★★★★☆     | ★★★☆☆     | ★★★★★     | ★★★★☆     | ★★★★☆     |
| **脱壳难度**   | ★★☆☆☆     | ★★☆☆☆     | ★★★★☆     | ★★★☆☆     | ★★★★★     | ★★★★☆     | ★★★★☆     |

> **注意**：以上评级基于旗舰版产品，免费版保护强度通常低 1-2 级。

---

## 壳的分代

Android 加固技术经历了明显的代际演变：

```text
第一代 (2013-2015)         第二代 (2015-2018)         第三代 (2018-至今)
+-------------------+     +-------------------+     +-------------------+
| DEX 整体加密      |     | DEX 函数抽取      |     | 指令级 VMP        |
| - 运行时解密还原  | --> | - 函数体替为 nop  | --> | - 字节码虚拟化    |
| - 内存中完整 DEX  |     | - 运行时动态填回  |     | - 自定义解释器    |
+-------------------+     +-------------------+     +-------------------+
  脱壳: 内存 dump           脱壳: FART 主动调用        脱壳: 逆向虚拟机
  难度: ★★☆☆☆             难度: ★★★☆☆             难度: ★★★★★
```

### 第一代：DEX 整体加密

将 `classes.dex` 整体加密，运行时壳代码解密后用 `DexClassLoader` 加载。**内存中存在完整 DEX**，直接 dump 即可。

### 第二代：DEX 函数抽取

在 DEX 加密基础上，将关键函数的方法体抽取出来，替换为 `nop`。运行时动态填回。dump 出的 DEX 中关键函数体为空，需要用 **FART** 主动调用每个方法触发填回后再 dump。

### 第三代：指令级 VMP

将字节码转换为自定义虚拟机指令，由壳自带的解释器执行。**原始字节码在任何时刻都不以标准形式存在**。需要逆向虚拟机解释器或转为动态分析策略。

**代际辨别方法：**

| 辨别维度           | 第一代          | 第二代          | 第三代          |
| :----------------- | :-------------- | :-------------- | :-------------- |
| dump DEX 是否完整  | 完整可用        | 函数体为空      | 无标准 DEX      |
| Jadx 打开效果      | 正常反编译      | 关键函数为空    | 完全无法反编译  |
| 壳 SO 大小         | < 500KB         | 0.5-2MB         | > 2MB           |
| 性能影响           | 几乎无          | 轻微            | 明显            |

---

## 自动化识别工具

### APKiD 详细用法

```bash
$ apkid target.apk
[+] target.apk!classes.dex
 |-> compiler : dexlib 2.x
 |-> packer : Tencent Legu
[+] target.apk!lib/armeabi-v7a/libshella-2.10.3.1.so
 |-> packer : Tencent Legu
 |-> anti_disassembly : Tencent Legu
```

### 自定义 Python 识别脚本

```python
#!/usr/bin/env python3
"""APK 加固厂商识别脚本"""
import zipfile, sys
from pathlib import Path

SIGNATURES = {
    "360加固":   {"so": ["libjiagu", "libprotectClass"],
                  "assets": [".jiagu"], "app": ["com.stub.StubApp"]},
    "腾讯乐固": {"so": ["liblegu", "libshella", "libshellx"],
                  "assets": ["legu_data", "tosversion"], "app": ["com.tencent.StubShell"]},
    "梆梆安全": {"so": ["libSecShell", "libsecexe", "libsecmain"],
                  "assets": ["bangcle_classes"], "app": ["com.bangcle", "com.secshell"]},
    "网易易盾": {"so": ["libnesec"],
                  "assets": ["nesec.dat", "classes.dex.ys"], "app": ["com.netease.nis"]},
    "爱加密":   {"so": ["libijiami", "libexecmain"],
                  "assets": ["ijiami.dat"], "app": ["com.ijiami"]},
    "娜迦":     {"so": ["libchaosvmp", "libddog", "libnagavm"],
                  "assets": ["nagain"], "app": ["com.nagain"]},
    "几维安全": {"so": ["libkwscmm", "libkwscr"],
                  "assets": ["kiwi.dat"], "app": ["com.kiwisec"]},
}

def identify(apk_path):
    results = {}
    with zipfile.ZipFile(apk_path) as zf:
        files = zf.namelist()
        for name, sigs in SIGNATURES.items():
            score, matches = 0, []
            for f in files:
                fl = f.lower()
                for p in sigs["so"]:
                    if p.lower() in fl and f.endswith(".so"):
                        score += 3; matches.append(f"SO: {f}")
                for p in sigs["assets"]:
                    if p.lower() in fl and "assets" in fl:
                        score += 2; matches.append(f"Assets: {f}")
            # 检查 DEX 大小
            for f in files:
                if f == "classes.dex" and zf.getinfo(f).file_size < 500*1024:
                    score += 1; matches.append("DEX < 500KB")
            if score > 0:
                results[name] = {"score": score, "matches": matches}
    return results

if __name__ == "__main__":
    apk = sys.argv[1] if len(sys.argv) > 1 else exit("用法: python detect.py <apk>")
    for name, data in sorted(identify(apk).items(), key=lambda x: -x[1]["score"]):
        level = "高" if data["score"] >= 5 else "中" if data["score"] >= 3 else "低"
        print(f"[{level}] {name} (分数:{data['score']})")
        for m in data["matches"]:
            print(f"    - {m}")
```

### RASP 运行时检测脚本 (Frida)

```javascript
// rasp_detect.js - 运行时检测加固类型
Java.perform(function() {
    var packer_map = {
        "libjiagu": "360加固", "liblegu": "腾讯乐固", "libshella": "腾讯乐固",
        "libSecShell": "梆梆安全", "libnesec": "网易易盾",
        "libijiami": "爱加密", "libchaosvmp": "娜迦", "libkwscmm": "几维安全",
    };
    Process.enumerateModules().forEach(function(mod) {
        for (var key in packer_map) {
            if (mod.name.indexOf(key) !== -1) {
                console.log("[!] " + mod.name + " -> " + packer_map[key]
                    + " (base:" + mod.base + " size:" + mod.size + ")");
            }
        }
    });
});
```

---

## 针对不同壳的脱壳策略

| 加固厂商       | 壳代数 | 推荐脱壳方法               | 推荐工具                 | 难度       |
| :------------- | :----- | :------------------------- | :----------------------- | :--------- |
| **360 基础版** | 一代   | 内存 dump                  | Frida dump / FDex2       | ★☆☆☆☆   |
| **360 企业版** | 二代   | FART 主动调用              | FART / Youpk             | ★★★☆☆   |
| **腾讯乐固**   | 一代   | 修复 DEX 头 + dump         | Frida dump               | ★★☆☆☆   |
| **梆梆基础**   | 一代   | 内存 dump                  | Frida dump               | ★★☆☆☆   |
| **梆梆企业**   | 二/三  | FART + 手动修复            | FART / IDA               | ★★★★☆   |
| **爱加密**     | 一/二  | FART 主动调用              | FART / Frida             | ★★★☆☆   |
| **网易易盾**   | 三代   | Hook 关键 API / 不脱壳     | Frida Hook / 动态分析    | ★★★★★   |
| **娜迦**       | 二/三  | FART + VMP 逆向            | FART / IDA               | ★★★★☆   |
| **几维安全**   | 三代   | VMP 逆向 / 运行时 Hook     | IDA / Frida              | ★★★★☆   |

```text
决策流程:
  识别加固 --> 一代壳 --> Frida dump DEX --> Jadx 反编译
          --> 二代壳 --> FART 脱壳 --> 回填 CodeItem --> Jadx
          --> 三代壳 --> 值得脱壳? -- 是 --> 逆向 VMP (数天~数周)
                                    -- 否 --> Hook API / 抓包 / 内存搜索
```

---

## SO 保护识别

### OLLVM 混淆识别

OLLVM 通过控制流平坦化增加逆向难度。IDA 中典型表现为**星型 CFG**（所有基本块回到一个中心分发器）。

```text
正常函数 CFG:               OLLVM 平坦化后 CFG:
   +-----+                     +----------+
   | 入口 |                     |  分发器   |<-------+
   +--+--+                     | (switch)  |        |
      |                        +--+--+--+--+        |
   +--v--+                       |  |  |  |         |
   | 判断 |                  +---+  |  |  +---+     |
   +--+--+                  v      v  v      v     |
      |                    BB1   BB2  BB3   BB4    |
   +--v--+                  +------+--+------+     |
   | 返回 |                        +---------------+
   +-----+
```

| 特征           | 正常函数       | OLLVM 平坦化函数     |
| :------------- | :------------- | :------------------- |
| 基本块数量     | < 20           | > 50                 |
| CFG 形状       | 树状/DAG       | 星型（中心分发器）   |
| 函数大小       | 正常           | 膨胀 3-10 倍         |
| 反编译效果     | 正常           | 大量嵌套 switch      |

### SO VMP 识别

SO 层 VMP 将原生 ARM/ARM64 指令转换为自定义字节码，由嵌入的虚拟机解释执行。

**识别特征：**

```text
原始 SO 函数:                VMP 保护后:
  func_a:                    func_a:
    mov r0, #1                 push {r0-r12}
    add r1, r0, #2             ldr r0, =vm_bytecode_a
    str r1, [sp]               bl  vm_dispatcher    ----+
    bx lr                      pop {r0-r12}             |
                               bx lr                    |
                                                        |
                             vm_dispatcher:    <---------+
                               ; 读取自定义字节码
                               ; 查 opcode handler 表
                               ; 分发执行
                               ; 循环直到 VM_EXIT
```

| 判断依据                           | 具体表现                            |
| :--------------------------------- | :---------------------------------- |
| 函数入口统一调用 dispatcher        | IDA 中大量函数只有 `bl vm_entry`    |
| 存在大段不可反汇编数据             | IDA 标记为 `.data` 或 `DCB` 字节   |
| 函数指针数组（handler 表）         | IDA 中可见连续的函数指针表          |
| SO 体积异常膨胀                    | 相比未保护版本大 2-5 倍             |

### Anti-Tampering 识别

SO 文件完整性校验常见于加固后的 Native 库中。

| 校验方式           | 识别方法                                     | 绕过思路                  |
| :----------------- | :------------------------------------------- | :------------------------ |
| CRC32 校验         | 搜索 `crc32` 函数调用                        | Hook `crc32` 返回期望值   |
| SHA256 校验        | 搜索 `SHA256_Init/Update/Final`              | Hook SHA256 函数族        |
| 自实现校验         | 搜索 `mmap` + 循环读取 + 比较                | 定位校验函数并 NOP        |
| `.init_array` 校验 | 检查 ELF `.init_array` 段中的函数            | 修改 `.init_array` 入口   |
| `JNI_OnLoad` 校验  | 分析 `JNI_OnLoad` 中的校验逻辑              | Hook `JNI_OnLoad` 跳过    |

```bash
# 用 readelf 检查 .init_array（校验逻辑常藏在这里）
readelf -d libnative.so | grep INIT
readelf -x .init_array libnative.so
```

---

## 运行时保护识别

```text
RASP 保护层次
+----------------------------------------------+
| 应用层: Root/Magisk/KernelSU 检测, 模拟器检测 |
+----------------------------------------------+
| 框架层: Frida/Xposed 检测, 签名校验, DEX CRC  |
+----------------------------------------------+
| 系统层: ptrace 反调试, /proc/self/maps,       |
|         TracerPid, SELinux 状态               |
+----------------------------------------------+
```

| 检测目标 | 检测方法                             | 识别特征（Frida 可观测）         |
| :------- | :----------------------------------- | :------------------------------- |
| Frida    | 扫描 27042 端口 / maps 中搜 `frida` | `connect()` 到 27042 / `fopen`   |
| Root     | 检查 `/system/bin/su` 等路径         | `File.exists()` 访问 su 路径     |
| Xposed   | 查找 `de.robv.android.xposed` 类    | `ClassLoader.loadClass()` 调用   |
| 调试器   | `ptrace(PTRACE_TRACEME)` / TracerPid | `ptrace` syscall / 读取 status   |
| 完整性   | DEX CRC / APK 签名校验              | `getPackageInfo()` + 签名比对    |

---

## 实战：快速判断加固方案

完整工作流（约 5 分钟）：

### 第 1 步：基础检查

```bash
# 解压并检查 DEX 大小 -- 小于 500KB 基本确认加固
unzip -l target.apk | grep "classes.dex"

# 列出所有 SO 文件
unzip -l target.apk | grep "\.so$"

# 查看 DEX 文件头
unzip -p target.apk classes.dex | xxd | head -1
```

### 第 2 步：APKiD 扫描

```bash
apkid target.apk
```

### 第 3 步：Manifest 确认

```bash
aapt dump xmltree target.apk AndroidManifest.xml | grep "android:name"
# 比对本文「加固厂商识别指纹总表」中的 Application 类名
```

### 第 4 步：制定策略

```text
识别结果 --> 查阅「针对不同壳的脱壳策略」表
  |
  +-> 一代壳 -> Frida dump -> Jadx 反编译 -> 分析
  +-> 二代壳 -> FART 脱壳 -> 回填 CodeItem -> 分析
  +-> 三代壳 -> 评估是否值得脱壳
  |     +-- 是 -> 逆向 VMP 解释器（耗时数天到数周）
  |     +-- 否 -> Hook 关键 API / 网络抓包 / 内存搜索
  +-> 未加固 -> 直接 Jadx 反编译
```

### 完整示例 (360 加固)

```bash
$ apkid target.apk
[+] target.apk!classes.dex
 |-> packer : Qihoo 360 (DexProtector)
[+] target.apk!lib/armeabi-v7a/libjiagu.so
 |-> packer : Qihoo 360

$ unzip -l target.apk | grep "\.so$"
  lib/armeabi-v7a/libjiagu.so
  lib/armeabi-v7a/libjiagu_art.so
# 确认 360 加固，一代壳 -> Frida dump 即可

$ frida -U -f com.target.app -l frida_dex_dump.js --no-pause
# dump 后用 Jadx 打开分析
```

---

> **总结**：加固识别是逆向分析的第一步。掌握各厂商的静态特征"指纹"后，结合 APKiD 自动化工具和手动验证，可以在 **5 分钟内**完成加固方案的判定，从而选择最高效的脱壳和分析策略。
