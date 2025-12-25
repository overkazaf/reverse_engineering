---
title: "Objection 常用技巧 (Objection Snippets)"
date: 2025-02-09
weight: 10
---

# Objection 常用技巧 (Objection Snippets)

> **📚 前置知识**
>
> 本配方涉及以下核心技术，建议先阅读相关章节：
>
> - **[Frida 完整指南](../../02-Tools/Dynamic/frida_guide.md)** - Objection 基于 Frida 构建
> - **[ADB 速查手册](../../02-Tools/Environment/adb_cheatsheet.md)** - 设备连接与应用启动

Objection 是一个基于 Frida 开发的运行时移动端探索工具包。它提供了类似于 shell 的交互式命令行，无需编写 JavaScript 代码即可完成大部分常见的逆向任务。

- **安装**: `pip install objection`
- **启动**: `objection -g com.example.app explore`

## 1. 内存漫游与类查找

在不知道从何入手时，首先浏览应用中加载了哪些类。

- **搜索类**:

```bash
# 搜索包含 "Crypto" 的类
android hooking search classes Crypto
```

```bash
# 搜索包含 "encrypt" 的方法
android hooking search methods encrypt
```

```bash
# 列出 com.example.app.MainActivity 的所有方法
android hooking list class_methods com.example.app.MainActivity
```

## 2. Hook 方法

Objection 的核心功能之一是快速 Hook 类或方法，打印调用的参数、返回值和调用栈。

- **Hook 整个类的所有方法**:

```bash
android hooking watch class com.example.app.CryptoUtil
```

```bash
# 拦截 encrypt 方法，并打印参数和返回值
android hooking watch class_method com.example.app.CryptoUtil.encrypt --dump-args --dump-return
```

```bash
# 强制 isRooted 方法返回 false
android hooking set return_value com.example.app.Security.isRooted false
```

## 3. 堆操作

可以搜索内存中存在的对象实例，甚至调用这些实例的方法。

- **搜索堆中的实例**:

```bash
# 查找内存中现存的 User 实例
android heap search instances com.example.app.User
```

```bash
# 假设上一步搜索到实例 hashcode 为 123456
# 调用该实例的 getToken 方法
android heap execute 123456 getToken
```

```bash
# 查看该实例的 username 字段值
android heap evaluate 123456
# (进入编辑器后输入) console.log(clazz.username.value)
```

## 4. Activity 与 Fragment

- **查看当前 Activity**:

```bash
android hooking get current_activity
```

```bash
android hooking list fragments
```

```bash
android intent launch_activity com.example.app.SecretActivity
```

## 5. 内存与 SO 库操作

- **列出加载的 SO 库**:

```bash
memory list modules
```

```bash
# 将 libnative-lib.so 导出到本地文件 (用于修复脱壳后的 SO)
memory dump from_base 0x7b12345000 0x50000 output.so
# 或自动下载
memory dump all libnative-lib.so
```

## 6. 文件系统操作

```bash
ls
cd cache
cat log.txt
file download /data/data/com.example.app/shared_prefs/config.xml
```

## 7. 安全绕过

- **禁用 SSL Pinning**:

```bash
android sslpinning disable
```

```bash
android root disable
```

## 8. 导入自定义脚本

```bash
import /path/to/my_script.js
```
