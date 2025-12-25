---
title: "主流应用加固厂商及其特征识别"
date: 2025-01-22
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

## 目录

1. [**通用识别思路**](#通用识别思路)
2. [**主流厂商特征详解**](#主流厂商特征详解)

- [主流应用加固厂商及其特征识别](#主流应用加固厂商及其特征识别)
  - [目录](#目录)
  - [通用识别思路](#通用识别思路)
  - [主流厂商特征详解](#主流厂商特征详解)
    - [梆梆安全 (Bangcle)](#梆梆安全-bangcle)
    - [360 加固 (Qihoo 360)](#360-加固-qihoo-360)
    - [腾讯乐固 (Tencent Legu)](#腾讯乐固-tencent-legu)
    - [网易易盾 (Netease Yidun)](#网易易盾-netease-yidun)
    - [爱加密 (Ijiami)](#爱加密-ijiami)
  - [快速识别摘要表](#快速识别摘要表)

3. [**快速识别摘要表**](#快速识别摘要表)

---

## 通用识别思路

识别加固厂商通常遵循以下静态分析路径：

1. **检查 DEX 文件**：解压 APK，查看主 `classes.dex` 文件的大小。如果它非常小（通常小于 1MB），而 APK 本身体积很大，那么它很可能是一个"壳"，负责加载真正的、被加密隐藏起来的 DEX。
2. **检查 SO 库**：查看 `lib/[arch]/` 目录下的 `.so` 文件列表。加固厂商通常会放入带有自身品牌标识的 SO 库，这是最明显的特征。
3. **检查 `assets` 目录**：很多加固方案会将加密后的 DEX 文件、配置文件或其他组件放入 `assets` 目录。
4. **检查 `AndroidManifest.xml`**：加固方案通常会用自己的代理 `Application` 类替换掉原始的 `Application` 类。检查 `application` 标签下的 `android:name` 属性，可以找到代理类的名字，其包名往往暴露厂商信息。

## 主流厂商特征详解

### 梆梆安全 (Bangcle)

梆梆是最早期的加固厂商之一，特征相对明显。

- **SO 库特征**:
- `libSecShell.so`

- `libsecexe.so`

- `libsecmain.so`
- **Java 层特征**:
- 代理 Application 包名：`com.bangcle.protect` 或 `com.secshell.shell`。
- **`assets` 目录特征**:
- 可能会有 `bangcle_classes.jar` 或类似命名的加密 DEX 文件。
- **其他**:
- `AndroidManifest.xml` 的 `meta-data` 中可能会包含原始 Application 的信息。

### 360 加固 (Qihoo 360)

360 加固非常普遍，其特征也广为人知。

- **SO 库特征**:
- `libjiagu.so`

- `libprotectClass.so`

- `libjiagu_x86.so` / `libjiagu_art.so`
- **Java 层特征**:
- 代理 Application 包名：`com.qihoo.util`。

- 启动类中可能包含 `com.stub.StubApp`。
- **`assets` 目录特征**:
- `libjiagu.so` (是的，有时也会放在 assets 里)

- `.jiagu` 后缀的加密文件。

### 腾讯乐固 (Tencent Legu)

腾讯乐固通常与 Bugly SDK 一起出现，特征明显。

- **SO 库特征**:
- `liblegu.so`

- `libshella-xxxx.so` (xxxx 是版本号)
- **Java 层特征**:
- 代理 Application 包名：`com.tencent.bugly.legu`。
- **`assets` 目录特征**:
- `legu_data.so`

- `tosversion` 文件
- **其他**:
- DEX 文件头通常被修改为 `legu`。

### 网易易盾 (Netease Yidun)

网易易盾是近年来兴起的一款强大加固，特征也比较独特。

- **SO 库特征**:
- `libnesec.so` (最核心的特征)
- **Java 层特征**:
- 代理 Application 包名：`com.netease.nis.wrapper`。
- **`assets` 目录特征**:
- `nesec.dat`

- `classes.dex.ys` (加密的主 DEX)

- `xxx.dat` 格式的加密 DEX 文件。

### 爱加密 (Ijiami)

爱加密也是一款常见的加固产品。

- **SO 库特征**:
- `libexec.so`

- `libexecmain.so`

- `libijiami.so`
- **Java 层特征**:
- 代理 Application 包名：`com.ijiami.client.protect`。
- **`assets` 目录特征**:
- `ijiami.dat`

- `ijm_lib` 目录

---

## 快速识别摘要表

| 加固厂商     | 核心 SO 特征                        | Java 包名/类名特征          | `assets` 目录特征             |
| :----------- | :---------------------------------- | :-------------------------- | :---------------------------- |
| **梆梆安全** | `libSecShell.so`                    | `com.bangcle.protect`       | `bangcle_classes.jar`         |
| **360 加固** | `libjiagu.so`, `libprotectClass.so` | `com.qihoo.util`            | `.jiagu` 文件                 |
| **腾讯乐固** | `liblegu.so`                        | `com.tencent.bugly.legu`    | `legu_data.so`                |
| **网易易盾** | `libnesec.so`                       | `com.netease.nis.wrapper`   | `nesec.dat`, `classes.dex.ys` |
| **爱加密**   | `libexec.so`, `libijiami.so`        | `com.ijiami.client.protect` | `ijiami.dat`                  |
