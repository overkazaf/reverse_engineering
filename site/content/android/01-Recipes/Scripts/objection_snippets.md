---
title: "Objection 常用技巧 (Objection Snippets)"
date: 2025-02-09
type: posts
tags: ["Native层", "Frida脚本", "Frida", "SSL Pinning", "加密分析", "Hook"]
weight: 10
---

# Objection 常用技巧 (Objection Snippets)

> **📚 前置知识**
>
> 本配方涉及以下核心技术，建议先阅读相关章节：
>
> - **[Frida 完整指南](../../02-Tools/Dynamic/frida_guide.md)** - Objection 基于 Frida 构建
> - **[ADB 速查手册](../../02-Tools/Cheatsheets/adb_cheatsheet.md)** - 设备连接与应用启动

Objection 是一个基于 Frida 开发的运行时移动端探索工具包。它提供了类似于 shell 的交互式命令行，无需编写 JavaScript 代码即可完成大部分常见的逆向任务。

---

## Objection 简介与安装

### 什么是 Objection

Objection 是由 **@sensepost** 开发的开源工具，对 Frida 做了一层高级封装。它的核心优势在于：

| 特性 | 说明 |
|------|------|
| **零代码 Hook** | 无需编写 JavaScript，输入命令即可 Hook 任意类/方法 |
| **交互式 Shell** | 类似终端的命令行界面，支持 Tab 补全和历史记录 |
| **一键绕过** | 内置 SSL Pinning、Root 检测等常用绕过方案 |
| **跨平台** | 同时支持 Android 和 iOS |
| **可扩展** | 支持导入自定义 Frida 脚本，灵活扩展功能 |

### 安装

```bash
# 基础安装
pip3 install objection

# 升级到最新版
pip3 install --upgrade objection

# 验证安装
objection version
```

> **注意**: Objection 依赖 Frida，安装时会自动拉取对应版本的 `frida-tools`。请确保本机 Frida 版本与设备上 `frida-server` 版本一致。

### 连接设备

```bash
# 标准方式：附加到正在运行的应用
objection -g com.example.app explore

# 以 Spawn 模式启动（推荐，可在应用启动前注入）
objection -g com.example.app explore --startup-command "android sslpinning disable"

# 指定设备（多台设备连接时）
objection -S <device_id> -g com.example.app explore

# 通过网络连接远程 frida-server
objection -N -h 192.168.1.100 -p 27042 -g com.example.app explore
```

连接成功后会进入交互式 Shell，提示符类似：

```
com.example.app on (google: 13) [usb] #
```

---

## 基础命令大全

以下按功能分类整理了 Objection 中最常用的命令。

### 环境信息

| 命令 | 说明 |
|------|------|
| `env` | 显示应用的沙箱路径（data/cache/外部存储等） |
| `android hooking get current_activity` | 获取当前前台 Activity |
| `android hooking list activities` | 列出 AndroidManifest 中声明的所有 Activity |
| `android hooking list services` | 列出所有已注册的 Service |
| `android hooking list receivers` | 列出所有已注册的 BroadcastReceiver |

### 类与方法搜索

| 命令 | 说明 |
|------|------|
| `android hooking search classes <keyword>` | 模糊搜索已加载的类 |
| `android hooking search methods <keyword>` | 模糊搜索方法名 |
| `android hooking list classes` | 列出所有已加载的类（输出量巨大，建议重定向） |
| `android hooking list class_methods <class>` | 列出指定类的全部方法 |

### Hook 操作

| 命令 | 说明 |
|------|------|
| `android hooking watch class <class>` | Hook 整个类的所有方法 |
| `android hooking watch class_method <method> --dump-args --dump-return --dump-backtrace` | Hook 指定方法，打印参数、返回值和调用栈 |
| `android hooking set return_value <method> <value>` | 强制设置方法的返回值 |

### 安全绕过

| 命令 | 说明 |
|------|------|
| `android sslpinning disable` | 禁用 SSL Pinning |
| `android root disable` | 绕过 Root 检测 |
| `android root simulate` | 模拟非 Root 环境 |

### 文件系统

| 命令 | 说明 |
|------|------|
| `ls [path]` | 列出目录内容 |
| `cd <path>` | 切换目录 |
| `pwd` | 显示当前工作目录 |
| `cat <file>` | 查看文件内容 |
| `file download <remote> [local]` | 下载文件到本机 |
| `file upload <local> <remote>` | 上传文件到设备 |

### 内存操作

| 命令 | 说明 |
|------|------|
| `memory list modules` | 列出所有已加载的 SO 库 |
| `memory list exports <module>` | 列出指定模块的导出函数 |
| `memory dump all <local_file>` | Dump 整个进程内存 |
| `memory dump from_base <addr> <size> <file>` | 从指定地址 Dump 指定大小的内存 |
| `memory search "<pattern>"` | 在内存中搜索字符串或 hex 模式 |

### 堆操作

| 命令 | 说明 |
|------|------|
| `android heap search instances <class>` | 在堆中搜索指定类的实例 |
| `android heap execute <hashcode> <method>` | 调用实例的方法 |
| `android heap evaluate <hashcode>` | 进入 JavaScript 交互模式操作实例 |

### 其他实用命令

| 命令 | 说明 |
|------|------|
| `import <script.js>` | 导入自定义 Frida 脚本 |
| `jobs list` | 列出当前运行的后台任务（如 Hook） |
| `jobs kill <job_id>` | 停止指定的后台任务 |
| `exit` | 退出 Objection |
| `reconnect` | 重新连接到应用 |

---

## SSL Pinning 绕过

### 一键禁用

```bash
android sslpinning disable
```

执行后 Objection 会自动 Hook 以下常见的 SSL Pinning 实现：

| Hook 目标 | 说明 |
|-----------|------|
| `TrustManagerFactory` | 替换系统默认的信任管理器 |
| `X509TrustManager.checkServerTrusted()` | 使证书校验直接通过 |
| `OkHttp CertificatePinner` | 绕过 OkHttp 的证书锁定 |
| `SSLContext.init()` | 注入自定义 TrustManager |
| `WebViewClient.onReceivedSslError()` | WebView 中忽略 SSL 错误 |

### 工作原理

Objection 底层会注入一段 Frida 脚本，将所有证书校验相关的方法替换为空实现（直接返回成功）。等效于手动编写以下 Frida 代码：

```javascript
// Objection 底层做的事情（简化版）
Java.perform(function() {
    var TrustManager = Java.registerClass({
        name: 'com.sensepost.BypassTrustManager',
        implements: [Java.use('javax.net.ssl.X509TrustManager')],
        methods: {
            checkClientTrusted: function(chain, authType) { },
            checkServerTrusted: function(chain, authType) { },
            getAcceptedIssuers: function() { return []; }
        }
    });
});
```

### 配合 Burp Suite 抓包

```bash
# 1. 在设备上设置代理
adb shell settings put global http_proxy 192.168.1.100:8080

# 2. 以 Spawn 模式启动并自动禁用 SSL Pinning
objection -g com.example.app explore --startup-command "android sslpinning disable"

# 3. 操作 App，在 Burp 中观察流量
```

### 常见问题排查

| 问题 | 解决方案 |
|------|----------|
| 禁用后仍然无法抓包 | 检查代理设置是否正确；确认 Burp 证书已安装为系统级证书 |
| 应用使用自定义 SSL 库 | 需要手动定位并 Hook 自定义校验函数 |
| Flutter 应用抓不到包 | Flutter 使用 BoringSSL，需要专用脚本 Hook `ssl_verify_peer_cert` |
| 应用使用 Network Security Config | Android 7+ 需将 Burp CA 证书安装到系统证书目录 |
| Hook 生效但请求超时 | 检查设备和代理主机是否在同一网络，防火墙是否放行 |

---

## Root 检测绕过

### 基本命令

```bash
# 禁用常见的 Root 检测
android root disable

# 模拟非 Root 环境
android root simulate
```

### Root 检测常见手段

应用通常通过以下方式检测 Root，Objection 会逐一进行绕过：

| 检测方式 | 说明 | Objection 绕过原理 |
|----------|------|-------------------|
| 检查 `su` 二进制文件 | 查找 `/system/bin/su` 等路径 | Hook `File.exists()` 对 su 路径返回 false |
| 检查 `Build.TAGS` | 检查是否包含 `test-keys` | Hook 返回 `release-keys` |
| 检查包管理器 | 检测 Magisk/SuperSU 等包名 | Hook `PackageManager.getPackageInfo()` 抛出 NameNotFoundException |
| 检查可写系统分区 | 尝试写入 `/system` | Hook 文件操作相关方法 |
| 执行 `which su` | 通过 Runtime.exec 执行命令 | Hook `Runtime.exec()` 过滤敏感命令 |

### 应对自定义 Root 检测

当内置绕过不够用时，可以手动定位检测函数：

```bash
# 搜索可能的 Root 检测类
android hooking search classes root
android hooking search classes RootDetect
android hooking search classes SafetyNet
android hooking search classes integrity

# 搜索相关方法
android hooking search methods isRooted
android hooking search methods checkRoot
android hooking search methods isDeviceRooted

# 找到目标后直接修改返回值
android hooking set return_value com.example.app.Security.isRooted false
android hooking set return_value com.example.app.Security.checkRoot false
```

### SafetyNet / Play Integrity 绕过

```bash
# 搜索 SafetyNet 相关类
android hooking search classes SafetyNet
android hooking search classes PlayIntegrity

# Hook SafetyNet 回调，观察返回结果
android hooking watch class_method com.google.android.gms.safetynet.SafetyNetClient.attest --dump-args --dump-return
```

> **注意**: SafetyNet/Play Integrity 涉及服务端验证，单纯 Hook 客户端可能不够。生产级绕过通常需要配合 Magisk + 自定义模块。

---

## 文件系统探索

### 基本导航

```bash
# 查看应用沙箱环境变量
env

# 输出示例：
# Name                    Path
# ----                    ----
# filesDirectory          /data/data/com.example.app/files
# cacheDirectory          /data/data/com.example.app/cache
# externalCacheDirectory  /storage/emulated/0/Android/data/com.example.app/cache
# codeCacheDirectory      /data/data/com.example.app/code_cache

# 导航到应用数据目录
cd /data/data/com.example.app
ls
```

### 关键目录与文件

| 路径 | 内容 | 常见敏感信息 |
|------|------|-------------|
| `shared_prefs/` | SharedPreferences XML 文件 | Token、用户配置、加密密钥 |
| `databases/` | SQLite 数据库文件 | 用户数据、聊天记录、缓存数据 |
| `files/` | 应用自定义文件 | 日志、配置、下载内容 |
| `cache/` | 缓存目录 | 网络响应缓存、图片缓存 |
| `lib/` | Native SO 库 | 加密算法实现、核心逻辑 |
| `code_cache/` | DEX 缓存 | 动态加载的 DEX 文件 |
| `app_webview/` | WebView 数据 | Cookies、Local Storage |

### 实用操作

```bash
# 浏览 SharedPreferences
ls shared_prefs/
cat shared_prefs/app_config.xml

# 下载数据库到本机分析
file download /data/data/com.example.app/databases/app.db ./app.db

# 下载整个 SharedPreferences 目录
file download /data/data/com.example.app/shared_prefs/ ./shared_prefs/

# 上传修改后的配置文件
file upload ./modified_config.xml /data/data/com.example.app/shared_prefs/config.xml

# 查看外部存储
ls /storage/emulated/0/Android/data/com.example.app/
```

### 自动化文件收集脚本

启动 Objection 时可以用 `--startup-command` 批量执行：

```bash
objection -g com.example.app explore \
  --startup-command "ls /data/data/com.example.app/shared_prefs/" \
  --startup-command "ls /data/data/com.example.app/databases/"
```

---

## 内存操作

### 列出已加载模块

```bash
# 列出所有加载的 SO 库
memory list modules

# 输出示例：
# Name                        Base          Size     Path
# --------------------------  ----------    ------   ---------------------------------
# libnative-lib.so            0x7b12345000  0x50000  /data/app/.../lib/arm64/libnative-lib.so
# libssl.so                   0x7b23456000  0x80000  /system/lib64/libssl.so
```

```bash
# 列出指定模块的导出函数
memory list exports libnative-lib.so

# 输出示例：
# Type      Name                          Address
# --------  ----------------------------  -----------
# function  Java_com_example_encrypt      0x7b12347a00
# function  Java_com_example_decrypt      0x7b12347e00
```

### 内存 Dump

```bash
# 从指定基址 Dump 内存
memory dump from_base 0x7b12345000 0x50000 /tmp/libnative-lib.so

# Dump 整个进程内存（文件会很大）
memory dump all /tmp/full_dump.bin
```

> **用途**: Dump 出的 SO 文件可以用 IDA Pro 或 Ghidra 进行静态分析。对于加壳应用，运行时 Dump 可以获取脱壳后的 DEX/SO。

### 内存搜索

```bash
# 搜索字符串
memory search "password"
memory search "api_key"
memory search "token"

# 搜索十六进制模式
memory search "50 4b 03 04"  # ZIP 文件头
memory search "64 65 78 0a"  # DEX 文件头
```

### 堆分析

```bash
# 搜索堆中的对象实例
android heap search instances com.example.app.model.User

# 输出示例：
# Hashcode    Class                          toString()
# ----------  ----------------------------   ------------------
# 123456      com.example.app.model.User     User{name=admin}
# 789012      com.example.app.model.User     User{name=guest}

# 调用实例方法
android heap execute 123456 getToken

# 进入交互模式操作实例
android heap evaluate 123456
# 进入编辑器后输入 JavaScript：
# console.log(clazz.username.value)
# console.log(clazz.password.value)
# console.log(clazz.getToken())
```

---

## Activity / Service 操作

### 列出组件

```bash
# 列出所有 Activity
android hooking list activities

# 输出示例：
# com.example.app.MainActivity
# com.example.app.LoginActivity
# com.example.app.SettingsActivity
# com.example.app.debug.DebugActivity    <-- 可能是隐藏的调试页面

# 列出所有 Service
android hooking list services

# 列出所有 BroadcastReceiver
android hooking list receivers
```

### 获取当前 Activity

```bash
android hooking get current_activity

# 输出示例：
# Activity: com.example.app.MainActivity
# Fragment: HomeFragment
```

### 启动 Activity

```bash
# 直接启动指定 Activity（绕过正常导航流程）
android intent launch_activity com.example.app.debug.DebugActivity

# 启动需要 Extra 参数的 Activity
android intent launch_activity com.example.app.DetailActivity
```

> **实战技巧**: 有些应用会在 AndroidManifest 中声明调试用的 Activity（如 `DebugActivity`、`TestActivity`），但在正常流程中不会展示。通过 `list activities` 找到它们后直接启动，往往能发现隐藏功能。

### Hook Activity 生命周期

```bash
# 监控 Activity 的生命周期方法
android hooking watch class_method android.app.Activity.onCreate --dump-args
android hooking watch class_method android.app.Activity.onResume --dump-args

# 监控特定 Activity
android hooking watch class com.example.app.LoginActivity
```

### Service 操作

```bash
# Hook Service 的关键方法
android hooking watch class_method android.app.Service.onStartCommand --dump-args --dump-return

# 监控特定 Service
android hooking watch class com.example.app.SyncService
```

---

## Keystore 操作

Android Keystore 是应用存储加密密钥的安全容器。Objection 可以列出和提取其中的内容。

### 列出 Keystore 条目

```bash
# 列出 Android Keystore 中的所有密钥别名
android keystore list

# 输出示例：
# Alias               Type
# ------------------  ----------------
# my_rsa_key          PrivateKeyEntry
# encryption_key      SecretKeyEntry
# signing_cert        TrustedCertificateEntry
```

### 监控 Keystore 操作

```bash
# Hook KeyStore 类，观察应用如何使用密钥
android hooking watch class java.security.KeyStore --dump-args --dump-return

# Hook Cipher 类，观察加解密操作
android hooking watch class javax.crypto.Cipher --dump-args --dump-return

# 监控密钥生成
android hooking watch class_method javax.crypto.KeyGenerator.generateKey --dump-return
android hooking watch class_method java.security.KeyPairGenerator.generateKeyPair --dump-return
```

### 证书提取

```bash
# Hook 证书加载过程
android hooking watch class_method java.security.KeyStore.getCertificate --dump-args --dump-return

# 监控证书链
android hooking watch class_method java.security.KeyStore.getCertificateChain --dump-args --dump-return
```

### 实战：提取应用加密密钥

```bash
# 1. 搜索加密相关的类
android hooking search classes Crypto
android hooking search classes Cipher
android hooking search classes SecretKey

# 2. 监控 Cipher.init()，获取密钥和 IV
android hooking watch class_method javax.crypto.Cipher.init --dump-args --dump-backtrace

# 3. 监控 SecretKeySpec 构造函数，获取原始密钥字节
android hooking watch class_method javax.crypto.spec.SecretKeySpec.$init --dump-args

# 4. 监控 IvParameterSpec，获取 IV
android hooking watch class_method javax.crypto.spec.IvParameterSpec.$init --dump-args
```

---

## Hook 功能

### Watch 命令详解

`android hooking watch` 是 Objection 最核心的命令，支持多种选项：

```bash
# 基本用法：Hook 整个类
android hooking watch class com.example.app.CryptoUtil

# Hook 单个方法
android hooking watch class_method com.example.app.CryptoUtil.encrypt

# 完整选项：打印参数 + 返回值 + 调用栈
android hooking watch class_method com.example.app.CryptoUtil.encrypt \
  --dump-args \
  --dump-return \
  --dump-backtrace
```

各选项说明：

| 选项 | 说明 |
|------|------|
| `--dump-args` | 打印方法被调用时的所有参数 |
| `--dump-return` | 打印方法的返回值 |
| `--dump-backtrace` | 打印调用栈，显示是谁调用了这个方法 |

### 修改返回值

```bash
# 让方法始终返回 true
android hooking set return_value com.example.app.Security.isVPN true

# 让方法始终返回 false
android hooking set return_value com.example.app.Security.isRooted false

# 返回字符串
android hooking set return_value com.example.app.Config.getApiUrl "https://my-proxy.com"
```

### 列出已加载的类

```bash
# 列出所有类（输出量非常大）
android hooking list classes

# 建议结合搜索使用
android hooking search classes com.example
android hooking search classes encrypt
android hooking search classes certificate
android hooking search classes token
android hooking search classes auth
```

### 管理 Hook 任务

每个 `watch` 命令会创建一个后台任务：

```bash
# 查看所有活跃的 Hook 任务
jobs list

# 输出示例：
# Job ID  Hooks  Type
# ------  -----  -----
# 1       12     watch-class
# 2       1      watch-method

# 停止某个 Hook 任务
jobs kill 1
```

---

## 数据库操作

### 列出数据库

```bash
# 列出应用的所有 SQLite 数据库
android hooking search classes SQLiteDatabase

# 或者直接浏览数据库目录
ls /data/data/com.example.app/databases/

# 输出示例：
# Type   Size      Name
# -----  --------  ---------------
# File   2.1 MB    app.db
# File   32.0 KB   app.db-journal
# File   512.0 KB  analytics.db
```

### 连接并查询数据库

```bash
# 连接数据库
sqlite connect /data/data/com.example.app/databases/app.db

# 查看所有表
sqlite execute query "SELECT name FROM sqlite_master WHERE type='table';"

# 查询表结构
sqlite execute query "PRAGMA table_info(users);"

# 查询数据
sqlite execute query "SELECT * FROM users;"
sqlite execute query "SELECT username, token FROM users WHERE id=1;"

# 断开连接
sqlite disconnect
```

### 下载数据库到本机分析

```bash
# 下载到本机
file download /data/data/com.example.app/databases/app.db ./app.db

# 在本机使用 sqlite3 打开
# sqlite3 ./app.db
# .tables
# .schema users
# SELECT * FROM users;
```

### 监控数据库操作

```bash
# Hook SQLiteDatabase 的 query 方法，观察应用执行了哪些 SQL
android hooking watch class_method android.database.sqlite.SQLiteDatabase.rawQuery --dump-args
android hooking watch class_method android.database.sqlite.SQLiteDatabase.execSQL --dump-args

# Hook ContentProvider
android hooking watch class_method android.content.ContentResolver.query --dump-args --dump-backtrace
```

---

## 实战组合技

### 场景一：分析登录流程

```bash
# 第 1 步：禁用 SSL Pinning 以便抓包
android sslpinning disable

# 第 2 步：找到登录相关的类
android hooking search classes Login
android hooking search classes Auth
android hooking search classes Credential

# 第 3 步：列出目标类的方法
android hooking list class_methods com.example.app.LoginManager

# 第 4 步：Hook 登录方法，观察参数
android hooking watch class_method com.example.app.LoginManager.login \
  --dump-args --dump-return --dump-backtrace

# 第 5 步：Hook 加密方法，看密码如何被加密
android hooking watch class_method com.example.app.CryptoUtil.encrypt \
  --dump-args --dump-return

# 第 6 步：在 App 中执行登录操作，观察输出
```

### 场景二：提取应用 Token

```bash
# 方法一：从 SharedPreferences 中直接读取
cat /data/data/com.example.app/shared_prefs/auth.xml

# 方法二：从堆中搜索 Token 对象
android heap search instances com.example.app.model.AuthToken
android heap execute <hashcode> getAccessToken

# 方法三：Hook 网络请求，从 Header 中获取
android hooking watch class_method okhttp3.Request.header --dump-args --dump-return
android hooking watch class_method okhttp3.Request$Builder.addHeader --dump-args
```

### 场景三：绕过多重保护分析加密

```bash
# 第 1 步：绕过安全检测
android root disable
android sslpinning disable

# 第 2 步：搜索加密相关类
android hooking search classes Cipher
android hooking search classes AES
android hooking search classes encrypt

# 第 3 步：Hook 加密入口
android hooking watch class_method javax.crypto.Cipher.doFinal --dump-args --dump-return
android hooking watch class_method javax.crypto.Cipher.init --dump-args --dump-backtrace

# 第 4 步：Hook 密钥生成
android hooking watch class_method javax.crypto.spec.SecretKeySpec.$init --dump-args

# 第 5 步：操作应用触发加密流程，从输出中收集：
#   - 加密算法（AES/DES/RSA）
#   - 密钥字节
#   - IV 向量
#   - 明文和密文
```

### 场景四：快速信息收集

```bash
# 一次性执行多条命令快速了解应用
objection -g com.example.app explore \
  --startup-command "android hooking list activities" \
  --startup-command "android hooking list services" \
  --startup-command "android hooking list receivers" \
  --startup-command "android keystore list" \
  --startup-command "env"
```

---

## Objection vs Frida CLI

### 什么时候用 Objection

| 场景 | 推荐工具 | 原因 |
|------|----------|------|
| 快速禁用 SSL Pinning | **Objection** | 一条命令搞定 |
| 搜索类和方法 | **Objection** | 内置搜索命令，无需写代码 |
| 浏览文件系统 | **Objection** | 交互式 Shell 体验更好 |
| 简单的方法 Hook | **Objection** | watch 命令即可 |
| 修改方法返回值 | **Objection** | set return_value 一行搞定 |
| 复杂的参数构造/修改 | **Frida CLI** | 需要 JavaScript 灵活处理 |
| 批量 Hook + 自定义逻辑 | **Frida CLI** | 脚本更灵活，可以写循环和条件判断 |
| Native 层 Hook (Interceptor) | **Frida CLI** | Objection 对 Native Hook 支持有限 |
| 自动化测试脚本 | **Frida CLI** | Python 绑定更适合自动化 |
| RPC 远程调用 | **Frida CLI** | 需要 `frida.get_remote_device()` 等 API |

### 组合使用

Objection 和 Frida 并不是二选一的关系，最高效的方式是组合使用：

```bash
# 1. 用 Objection 快速侦察
objection -g com.example.app explore
# > android hooking search classes Encrypt
# > android hooking list class_methods com.example.app.EncryptUtil
# > android hooking watch class_method com.example.app.EncryptUtil.encrypt --dump-args

# 2. 发现目标后，导入自定义 Frida 脚本进行精细操作
import /path/to/custom_hook.js
```

在 Objection Shell 中导入自定义脚本：

```bash
# 导入脚本
import /path/to/my_script.js

# 脚本示例（my_script.js）：
# Java.perform(function() {
#     var EncryptUtil = Java.use("com.example.app.EncryptUtil");
#     EncryptUtil.encrypt.overload("java.lang.String").implementation = function(input) {
#         console.log("[*] encrypt 输入: " + input);
#         var result = this.encrypt(input);
#         console.log("[*] encrypt 输出: " + result);
#         // 可以在这里修改参数或返回值
#         return result;
#     };
# });
```

### 总结

```
初步侦察 / 快速验证  -->  Objection（零代码，交互式）
     |
     v
深入分析 / 自动化     -->  Frida CLI（脚本灵活，可编程）
     |
     v
生产级方案            -->  Frida Python 绑定 + 自定义 Agent
```

Objection 是逆向分析的"瑞士军刀"，适合快速上手和初步侦察。当需要更复杂的逻辑时，再切换到原生 Frida 脚本。两者配合使用，可以显著提升逆向效率。
