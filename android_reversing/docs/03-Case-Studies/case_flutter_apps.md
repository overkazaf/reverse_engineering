# Flutter 应用逆向案例

> **📚 前置知识**
>
> 本案例涉及以下核心技术，建议先阅读相关章节：
>
> - **[SO/ELF 格式](../04-Reference/Foundations/so_elf_format.md)** - 理解 libapp.so 的结构与 Snapshot 格式
> - **[Frida Native Hook](../02-Tools/Dynamic/frida_guide.md#native-hook)** - 对 Dart 编译后的函数进行运行时 Hook

Flutter 是 Google 推出的跨平台 UI 框架，它使用 Dart 语言开发。与传统的 Android App (Java/Kotlin) 或 Unity (C#) 不同，Release 模式下的 Flutter 应用将 Dart 代码预编译 (AOT) 成了原生机器码，打包在 `libapp.so` 中，这使得逆向难度大大增加。

---

## 核心架构

1. **`lib/armeabi-v7a/libflutter.so`**: Flutter 引擎，负责渲染、通信和运行时支持。通常不需要逆向，但可以用它来定位关键的内部函数。
2. **`lib/armeabi-v7a/libapp.so`**: **逆向的核心目标**。包含了开发者的所有业务逻辑代码（Dart 代码编译后的产物）。
3. **Snapshot 格式**: `libapp.so` 实际上不仅仅是代码，还包含了一个 Dart VM Snapshot。它没有标准的 ELF 符号表，也没有类似 Java 的类结构元数据。

---

## 逆向流程

### 第 1 步：识别 Flutter 应用

解压 APK，查看 `lib` 目录。如果看到 `libflutter.so` 和 `libapp.so`，那么这肯定是一个 Flutter 应用。

### 第 2 步：使用 reFlutter 框架

由于 Dart AOT 的特殊性，直接用 IDA 分析 `libapp.so` 非常困难，因为所有函数名都被剥离了，且 Dart 的调用约定和寄存器使用方式与标准 C/C++ 不同。

**reFlutter** 是目前最强大的 Flutter 逆向辅助工具。它通过修改 Flutter 引擎 (`libflutter.so`)，在应用运行时利用 Dart VM 的内部机制来 Dump 类、函数和偏移信息。

**工具**: [reFlutter](https://github.com/Impact-I/reFlutter)

**操作步骤**:

1. **重打包**: 使用 reFlutter 处理目标 APK。
    ```bash
    reflutter target.apk
    ```
2. **安装运行**: 安装生成的 `release.RE.apk` 到手机。
3. **获取偏移**: 应用启动后，reFlutter 会在 Logcat 中输出关键的 Dart 库函数的偏移地址，或者生成一个 `dump.dart` 文件。

### 第 3 步：流量拦截 (SSL Pinning Bypass)

Flutter 应用不使用系统的代理设置，也不使用 Java 层的 HTTP 客户端 (OkHttp)，而是使用 Dart 自己的 `HttpClient`。因此，传统的抓包设置（Wi-Fi 代理）和 Frida SSL Pinning 脚本通常无效。

**reFlutter 的方案**:

reFlutter 在重打包时，会自动 Patch `libflutter.so` 中的网络校验逻辑，并强制将流量转发到指定的代理 IP（需要在 reFlutter 配置阶段输入你的 Burp/Charles IP）。这是目前拦截 Flutter 流量最稳定的方法。

**Frida 方案 (Hook 验证函数)**:

如果你不想重打包，可以使用 Frida Hook `libflutter.so` 中负责验证证书的函数。

- 函数名通常包含 `SessionVerifyCertificateChain`。
- 你需要下载对应 Flutter 版本的 `libflutter.so` 符号文件，或者通过特征码搜索该函数。
- Hook 该函数并使其直接返回验证成功。

### 第 4 步：使用 Doldrums 还原代码

**Doldrums** 是一个针对 Flutter Android 应用的静态分析工具，试图将 `libapp.so` 反编译回 Dart 伪代码。

**工具**: [Doldrums](https://github.com/rscloura/Doldrums)

注意：由于 Flutter 版本更新极快，Snapshot 格式经常变动，Doldrums 可能不支持最新的 Flutter 版本。

### 第 5 步：动态分析 (Dart VM Hook)

如果无法静态还原代码，我们需要在运行时进行 Hook。由于没有符号，我们需要结合 reFlutter 导出的偏移地址。

```javascript
// Frida Script Example: Hook Dart Function
// Assume reFlutter tells us the function offset to hook is 0x1a2b3c

var appBase = Module.findBaseAddress("libapp.so");
var targetOffset = 0x1a2b3c;
var targetFunc = appBase.add(targetOffset);

Interceptor.attach(targetFunc, {
  onEnter: function (args) {
    // Dart function parameter passing is special
    // args[0] may not be the first parameter, but a Closure or other VM structure
    // Parameters are usually stored in specific registers or stack locations
    console.log("Dart function called!");

    // Print parameters (try reading first 4 parameters)
    console.log("Arg1: " + args[0]);
    console.log("Arg2: " + args[1]);
    console.log("Arg3: " + args[2]);
  },
  onLeave: function (retval) {
    console.log("Dart function returned: " + retval);
  },
});
```

---

## 总结

1. **流量拦截**: 必须使用 **reFlutter** 对 APK 进行 Patch，或者 Hook `libflutter.so` 中的证书验证函数。
2. **代码分析**: 静态分析工具（如 Doldrums）兼容性较差，主要依赖 **reFlutter** 提取偏移 + **Frida** 动态调试。
3. **核心**: 理解 Dart VM 的工作原理（Snapshot 结构、Object Pool、Dispatch Table）是深入逆向 Flutter 的基础。
