---
title: "Android Studio 调试工具集"
date: 2024-04-04
type: posts
tags: ["RSA", "Native层", "浏览器指纹", "签名验证", "Frida", "JNI"]
weight: 10
---

# Android Studio 调试工具集

Android Studio 不仅仅是一个代码编辑器，它还集成了一套强大、可视化的调试和分析工具，能够极大地提升开发和逆向分析的效率。熟悉这些工具是每个 Android 工程师的必备技能。

---

## 目录

1. [日志猫 (Logcat)](#1-日志猫-logcat)
2. [Java/Kotlin 调试器](#2-javakotlin-调试器)
3. [布局检查器 (Layout Inspector)](#3-布局检查器-layout-inspector)
4. [应用分析器 (Profiler)](#4-应用分析器-profiler)
5. [数据库检查器 (Database Inspector)](#5-数据库检查器-database-inspector)
6. [APK 分析器 (APK Analyzer)](#6-apk-分析器-apk-analyzer)
7. [设备文件浏览器 (Device File Explorer)](#7-设备文件浏览器-device-file-explorer)
8. [App Inspection 统一面板](#8-app-inspection-统一面板)
9. [模拟器扩展控制](#9-模拟器扩展控制)
10. [Smali 调试 (smalidea)](#10-smali-调试-smalidea)
11. [Native 调试 (LLDB)](#11-native-调试-lldb)
12. [终端与 ADB 集成](#12-终端与-adb-集成)
13. [逆向常用插件](#13-逆向常用插件)
14. [调试技巧与最佳实践](#14-调试技巧与最佳实践)

---

## 1. 日志猫 (Logcat)

### 1.1 基本概念

Logcat 是 Android 系统的日志收集工具，Android Studio 将其封装在一个便捷的窗口中，可以实时查看来自系统和所有应用的日志信息。

### 1.2 核心功能

| 功能 | 描述 | 快捷键 |
|-----|------|-------|
| 实时日志流 | 显示来自设备或模拟器的连续日志 | - |
| 日志级别过滤 | Verbose/Debug/Info/Warn/Error/Assert | 下拉菜单 |
| 进程过滤 | 只显示当前调试应用的日志 | 下拉菜单 |
| 关键词搜索 | 支持正则表达式 | `Ctrl+F` |
| 堆栈跟踪点击 | 点击类名跳转到源码 | 单击链接 |
| 日志导出 | 保存日志到文件 | 右键菜单 |

### 1.3 高级过滤技巧

```bash
# 过滤语法示例
tag:MyTag                    # 按 Tag 过滤
level:error                  # 只显示 Error 级别
package:com.example.app      # 按包名过滤
message:exception            # 按消息内容过滤

# 组合过滤
tag:OkHttp & level:debug     # AND 组合
tag:Retrofit | tag:OkHttp    # OR 组合
-tag:System                  # 排除特定 Tag

# 正则表达式
tag~:.*Network.*             # Tag 匹配正则
message~:token=[a-zA-Z0-9]+  # 提取 token 信息
```

### 1.4 自定义日志格式

```bash
# 在终端使用 logcat 自定义格式
adb logcat -v threadtime     # 显示线程时间
adb logcat -v long           # 详细格式
adb logcat -v color          # 彩色输出

# 常用组合
adb logcat *:E               # 只显示 Error
adb logcat -s MyTag          # 只显示特定 Tag
adb logcat -b crash          # 查看崩溃日志
adb logcat -c                # 清空日志缓冲区
```

### 1.5 逆向应用场景

1. **敏感信息泄露检测**
   - 很多 App 在开发阶段会留下调试日志
   - 可能包含：加密前的请求参数、明文密钥、服务器响应

2. **工作流程分析**
   ```bash
   # 观察 App 启动流程
   adb logcat | grep -E "(onCreate|onResume|Activity)"

   # 追踪网络请求
   adb logcat | grep -i "http\|request\|response"
   ```

3. **崩溃分析**
   ```bash
   # 捕获 ANR
   adb logcat -b events | grep "am_anr"

   # 获取 Native 崩溃
   adb logcat | grep -A 50 "FATAL EXCEPTION"
   ```

---

## 2. Java/Kotlin 调试器

### 2.1 基本调试操作

| 操作 | Windows/Linux | macOS | 描述 |
|-----|--------------|-------|------|
| 切换断点 | `Ctrl+F8` | `Cmd+F8` | 在当前行添加/移除断点 |
| 步过 (Step Over) | `F8` | `F8` | 执行当前行，不进入方法 |
| 步入 (Step Into) | `F7` | `F7` | 进入当前方法 |
| 强制步入 | `Alt+Shift+F7` | `Option+Shift+F7` | 进入任何方法（包括库方法）|
| 步出 (Step Out) | `Shift+F8` | `Shift+F8` | 执行完当前方法并返回 |
| 运行到光标 | `Alt+F9` | `Option+F9` | 运行到光标所在行 |
| 恢复程序 | `F9` | `Cmd+Option+R` | 继续执行到下一个断点 |
| 计算表达式 | `Alt+F8` | `Option+F8` | 在调试时计算任意表达式 |
| 查看变量 | `Ctrl+Shift+I` | `Cmd+Shift+I` | 快速查看变量值 |

### 2.2 断点类型详解

#### 2.2.1 行断点 (Line Breakpoint)

最常用的断点类型，程序执行到该行时暂停。

```java
// 在这行设置断点
String result = encrypt(data);  // <-- 断点
```

#### 2.2.2 条件断点 (Conditional Breakpoint)

只有满足条件时才暂停：

```java
// 右键断点 -> 设置条件
// 条件示例：
userId.equals("12345")
list.size() > 100
response.code() == 401
```

#### 2.2.3 方法断点 (Method Breakpoint)

在方法入口或出口暂停：

```java
// 在方法签名行设置断点
public String encrypt(String data) {  // <-- 方法断点
    // 可以选择在进入或退出时暂停
}
```

#### 2.2.4 字段断点 (Field Watchpoint)

当字段被读取或修改时暂停：

```java
private String secretKey;  // <-- 字段断点
// 任何读取或修改 secretKey 的代码都会触发
```

#### 2.2.5 异常断点 (Exception Breakpoint)

捕获特定异常：

```
Run -> View Breakpoints -> + -> Java Exception Breakpoints
添加: java.lang.NullPointerException
添加: javax.crypto.BadPaddingException
```

### 2.3 高级调试技巧

#### 2.3.1 Evaluate Expression (计算表达式)

在断点处可以执行任意代码：

```java
// 断点暂停时，按 Alt+F8 打开计算窗口
// 可以执行：
this.getClass().getName()
Arrays.toString(encryptedBytes)
new String(Base64.decode(token, 0))
((OkHttpClient) client).dispatcher().executorService()
```

#### 2.3.2 修改变量值

在调试过程中动态修改变量：

```
1. 在 Variables 面板找到变量
2. 右键 -> Set Value
3. 输入新值

// 应用场景：
// - 绕过条件检查
// - 修改加密参数测试
// - 模拟不同的服务器响应
```

#### 2.3.3 强制返回 (Force Return)

强制方法返回指定值：

```
1. 在方法内断点暂停
2. 右键 -> Force Return
3. 输入返回值

// 应用场景：
// - 绕过 root 检测方法，强制返回 false
// - 跳过耗时操作
```

#### 2.3.4 丢弃帧 (Drop Frame)

回退到方法调用前的状态：

```
1. 在调用栈面板选择帧
2. 右键 -> Drop Frame
3. 程序回到该方法调用前

// 注意：不会撤销已经产生的副作用
```

### 2.4 附加到运行中的进程

```
Run -> Attach Debugger to Android Process
选择目标进程 -> Attach

# 要求：
# 1. App 必须是 debuggable=true
# 2. 或者设备是 userdebug/eng 版本
# 3. 或者使用 Magisk 模块开启全局可调试
```

### 2.5 逆向调试技巧

```java
// 1. Hook 前的变量观察
// 在关键加密方法前设置断点，观察参数

// 2. 追踪调用栈
// 断点暂停时查看 Call Stack 面板
// 了解方法是从哪里被调用的

// 3. 使用日志断点（不暂停，只打印）
// 右键断点 -> Suspend: 取消勾选
// 设置 Log 表达式: "param=" + param
```

---

## 3. 布局检查器 (Layout Inspector)

### 3.1 基本概念

Layout Inspector 是一个强大的可视化工具，允许你实时检查和调试正在运行的应用的视图层次结构。

### 3.2 核心功能

| 功能 | 描述 |
|-----|------|
| 3D 视图层次 | 以 3D 可旋转的视图展示 View 嵌套关系 |
| 属性查看 | 查看任意 View 的所有属性 |
| 实时更新 | 设备上操作 UI 时同步更新 |
| 重叠视图定位 | 发现被遮挡或不可见的视图 |
| Compose 支持 | 支持 Jetpack Compose UI 检查 |

### 3.3 使用步骤

```
1. 运行 App（Debug 模式）
2. Tools -> Layout Inspector
3. 选择进程
4. 等待视图层次加载

# 新版 Android Studio 可以：
View -> Tool Windows -> App Inspection -> Layout Inspector
```

### 3.4 属性检查详解

```
常用属性：
- id: View 的资源 ID（用于自动化脚本）
- text: 文本内容
- contentDescription: 无障碍描述
- visibility: 可见性状态
- clickable: 是否可点击
- alpha: 透明度
- elevation: 阴影高度
- background: 背景
```

### 3.5 逆向应用场景

1. **自动化脚本开发**
   ```python
   # UIAutomator2 示例
   # 使用 Layout Inspector 获取的 resource-id
   d(resourceId="com.example:id/login_btn").click()
   d(className="android.widget.EditText", instance=0).set_text("username")
   ```

2. **分析自定义 View**
   - 查看自定义 View 的属性
   - 理解复杂布局的层次结构

3. **检测反截图机制**
   ```java
   // 检查是否有 FLAG_SECURE 窗口
   // 在 Layout Inspector 中查找
   // WindowManager.LayoutParams.FLAG_SECURE = 0x2000
   ```

4. **分析 WebView**
   - 查看 WebView 的 URL
   - 检查 WebView 的 JavaScript 接口

---

## 4. 应用分析器 (Profiler)

### 4.1 概述

Profiler 是一套用于实时分析应用性能的工具，主要关注 CPU、内存、网络和电量四个方面。

### 4.2 CPU Profiler

#### 4.2.1 方法追踪模式

| 模式 | 精度 | 开销 | 适用场景 |
|-----|-----|-----|---------|
| Sample Java/Kotlin | 低 | 低 | 一般性能分析 |
| Trace Java/Kotlin | 高 | 高 | 精确方法追踪 |
| Sample C/C++ | 低 | 低 | Native 性能分析 |
| Trace System Calls | 高 | 中 | 系统调用分析 |

#### 4.2.2 火焰图分析

```
1. 点击 Record 开始记录
2. 在 App 中执行目标操作
3. 点击 Stop 停止记录
4. 分析结果：
   - Top Down: 从调用者到被调用者
   - Bottom Up: 从被调用者到调用者
   - Flame Chart: 火焰图可视化
   - Call Chart: 调用图表
```

#### 4.2.3 逆向应用

```java
// 追踪加密函数的完整调用链
// 1. 设置过滤条件只显示 App 的包名
// 2. 记录加密操作
// 3. 在火焰图中查找：
//    - javax.crypto.*
//    - java.security.*
//    - 自定义加密类
```

### 4.3 Memory Profiler

#### 4.3.1 内存区域

| 区域 | 描述 |
|-----|------|
| Java | Java/Kotlin 对象堆 |
| Native | C/C++ 分配的内存 |
| Graphics | 图形缓冲区 |
| Stack | 线程栈内存 |
| Code | 代码和资源内存 |
| Others | 其他系统内存 |

#### 4.3.2 堆转储分析

```
1. 点击 Dump Java Heap
2. 等待堆转储完成
3. 分析内容：
   - Allocations: 对象分配数量
   - Shallow Size: 对象自身大小
   - Retained Size: 对象及其引用的总大小

# 常用过滤：
- 按类名过滤
- 按包名过滤
- 只显示 App 的类
```

#### 4.3.3 逆向应用：内存中寻找敏感数据

```java
// 场景：App 解密数据后存储在内存中
// 步骤：
// 1. 在 App 加载数据后进行 Heap Dump
// 2. 搜索可能的类名：
//    - *Key*
//    - *Secret*
//    - *Token*
//    - *Password*
// 3. 查看对象的字段值

// 常见目标类：
// - java.lang.String
// - byte[]
// - char[]
// - SecretKeySpec
// - PrivateKey
```

### 4.4 Network Profiler

#### 4.4.1 功能概述

```
- 请求时间线可视化
- 请求/响应详情
- 连接状态追踪
- 线程信息

# 注意：
# - HTTPS 内容默认加密显示
# - 需要 HttpURLConnection 或 OkHttp
# - Android 8.0+ 设备效果更好
```

#### 4.4.2 限制与替代

```
Network Profiler 限制：
- 无法解密 HTTPS
- 不支持所有网络库
- 信息不够详细

替代方案：
- Charles/Fiddler 抓包
- mitmproxy
- Frida Hook 网络库
```

### 4.5 Energy Profiler

```
追踪能耗事件：
- CPU 唤醒
- 网络活动
- GPS 使用
- 传感器使用
- JobScheduler/WorkManager 任务

# 对逆向的帮助：
# 了解 App 后台行为，检测后台数据上报
```

---

## 5. 数据库检查器 (Database Inspector)

### 5.1 基本功能

```
1. 实时数据查看
2. 自定义 SQL 查询
3. 数据修改
4. 支持多个数据库

# 支持：
# - SQLite
# - Room
# - SQLDelight
```

### 5.2 使用方法

```sql
-- 查看所有表
SELECT name FROM sqlite_master WHERE type='table';

-- 查看表结构
PRAGMA table_info(users);

-- 查询数据
SELECT * FROM users WHERE username='admin';

-- 修改数据（测试绕过）
UPDATE users SET vip_status=1 WHERE id=1;
UPDATE config SET debug_mode=1;
```

### 5.3 逆向应用场景

1. **分析数据结构**
   ```sql
   -- 常见敏感表
   SELECT * FROM sessions;          -- 会话信息
   SELECT * FROM auth_tokens;       -- 认证令牌
   SELECT * FROM user_preferences;  -- 用户配置
   SELECT * FROM cache;             -- 缓存数据
   ```

2. **本地 VIP 绕过测试**
   ```sql
   -- 修改会员状态
   UPDATE user_info SET is_vip=1, vip_expire_time=9999999999;

   -- 解锁功能
   UPDATE features SET unlocked=1;
   ```

3. **分析加密存储**
   ```sql
   -- 很多 App 使用加密数据库
   -- 常见实现：
   -- - SQLCipher
   -- - Realm (加密模式)
   -- - 自定义加密

   -- 如果数据库被加密，需要先获取密钥
   -- 密钥可能在：
   -- - SharedPreferences
   -- - Native 代码
   -- - 服务器下发
   ```

---

## 6. APK 分析器 (APK Analyzer)

### 6.1 基本概念

APK Analyzer 是 Android Studio 内置的 APK 文件分析工具，可以分析已编译的 APK 文件结构，无需源码。

### 6.2 打开方式

```
方式一：Build -> Analyze APK -> 选择 APK 文件
方式二：直接拖拽 APK 文件到 Android Studio
方式三：双击项目中的 APK 文件
```

### 6.3 分析内容

#### 6.3.1 文件结构

```
APK 文件结构：
├── AndroidManifest.xml    # 应用配置
├── classes.dex            # Java/Kotlin 代码
├── classes2.dex           # MultiDex
├── resources.arsc         # 编译后的资源
├── res/                   # 资源文件
│   ├── drawable/
│   ├── layout/
│   └── values/
├── lib/                   # Native 库
│   ├── armeabi-v7a/
│   ├── arm64-v8a/
│   ├── x86/
│   └── x86_64/
├── assets/                # 原始资源
└── META-INF/              # 签名信息
```

#### 6.3.2 AndroidManifest.xml 分析

```xml
<!-- 关键信息 -->
<manifest package="com.example.app">
    <!-- 权限分析 -->
    <uses-permission android:name="android.permission.INTERNET"/>
    <uses-permission android:name="android.permission.READ_PHONE_STATE"/>

    <!-- 组件分析 -->
    <application android:debuggable="false"
                 android:allowBackup="true"
                 android:name=".MyApplication">

        <!-- Activity 入口 -->
        <activity android:name=".MainActivity"
                  android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
            </intent-filter>
        </activity>

        <!-- Service 分析 -->
        <service android:name=".PushService"/>

        <!-- Provider 分析 -->
        <provider android:name=".FileProvider"
                  android:authorities="com.example.fileprovider"/>
    </application>
</manifest>
```

#### 6.3.3 DEX 文件分析

```
功能：
- 查看类列表
- 查看方法数量
- 分析包结构
- 查看定义的方法和引用的方法

# 64K 方法限制分析
# 查看每个 DEX 的方法数
```

#### 6.3.4 资源分析

```
资源类型：
- drawable: 图片资源
- layout: 布局文件（可查看 XML）
- values: 字符串、颜色、尺寸等
- raw: 原始文件
- xml: 配置文件
```

### 6.4 APK 比较功能

```
1. 打开第一个 APK
2. 点击 "Compare with previous APK"
3. 选择第二个 APK
4. 查看差异：
   - 文件大小变化
   - 新增/删除的文件
   - 修改的文件

# 应用场景：
# - 分析版本更新变化
# - 对比加固前后差异
# - 追踪功能变更
```

### 6.5 逆向应用场景

1. **快速了解 APK 结构**
   - 识别加固壳（查看 DEX 结构异常）
   - 分析 Native 库架构支持
   - 查看使用的第三方 SDK

2. **提取资源**
   - 图片资源
   - 配置文件
   - assets 中的数据文件

3. **分析签名**
   ```
   META-INF/CERT.RSA 或 CERT.SF
   查看签名者信息
   验证 APK 完整性
   ```

---

## 7. 设备文件浏览器 (Device File Explorer)

### 7.1 基本功能

```
View -> Tool Windows -> Device File Explorer

功能：
- 浏览设备文件系统
- 上传/下载文件
- 删除文件
- 创建目录
- 查看文件权限

# Root 设备可以访问更多目录
```

### 7.2 重要目录

```
/data/data/<package>/           # App 私有数据（需要 root 或 debuggable）
├── shared_prefs/               # SharedPreferences XML
├── databases/                  # SQLite 数据库
├── cache/                      # 缓存目录
├── files/                      # 内部文件存储
└── lib/                        # Native 库链接

/data/app/<package>/            # APK 安装目录
├── base.apk                    # 主 APK
└── lib/                        # Native 库

/sdcard/Android/data/<package>/ # 外部存储（App 专用）
/sdcard/Android/obb/<package>/  # OBB 扩展文件

/system/                        # 系统目录
/vendor/                        # 厂商定制
```

### 7.3 逆向应用场景

1. **提取 App 数据**
   ```
   # 数据库
   /data/data/com.example.app/databases/app.db

   # SharedPreferences
   /data/data/com.example.app/shared_prefs/config.xml

   # 缓存的配置
   /data/data/com.example.app/cache/
   ```

2. **分析运行时生成的文件**
   ```
   # 动态加载的 DEX
   /data/data/com.example.app/files/*.dex

   # 解密后的 SO
   /data/data/com.example.app/files/*.so
   ```

3. **修改配置测试**
   ```xml
   <!-- 修改 SharedPreferences -->
   <!-- 下载 -> 编辑 -> 上传 -->
   <map>
       <boolean name="is_first_run" value="false"/>
       <boolean name="ad_enabled" value="false"/>
       <boolean name="debug_mode" value="true"/>
   </map>
   ```

---

## 8. App Inspection 统一面板

### 8.1 概述

App Inspection 是 Android Studio Arctic Fox 引入的统一检查面板，整合了多个工具。

```
View -> Tool Windows -> App Inspection

包含：
- Database Inspector
- Background Task Inspector
- Network Inspector (新)
```

### 8.2 Background Task Inspector

```
监控后台任务：
- WorkManager 任务
- JobScheduler 任务
- AlarmManager 任务

功能：
- 查看任务状态
- 查看任务约束
- 取消任务
- 触发任务立即执行
```

### 8.3 Network Inspector (新版)

```
比旧版 Network Profiler 更强大：
- 请求/响应详情
- 更好的搜索过滤
- 规则编辑（拦截修改请求）

# 仍然无法解密 HTTPS
```

---

## 9. 模拟器扩展控制

### 9.1 Extended Controls

```
模拟器 -> ... 按钮 -> Extended Controls

功能类别：
- Location: GPS 模拟
- Cellular: 网络状态模拟
- Battery: 电池状态
- Phone: 来电/短信模拟
- Directional pad: 方向键
- Microphone: 麦克风输入
- Fingerprint: 指纹模拟
- Virtual sensors: 传感器模拟
- Camera: 摄像头模拟
- Snapshots: 快照管理
- Screen record: 屏幕录制
- Google Play: Play 服务
- Settings: 模拟器设置
- Bug report: 生成 bug 报告
```

### 9.2 GPS 位置模拟

```
用途：
- 测试基于位置的功能
- 绕过地理围栏限制
- 模拟行进轨迹

方法：
1. Extended Controls -> Location
2. 输入经纬度 或 搜索地点
3. 点击 "Set Location"

# GPX/KML 文件支持路径模拟
```

### 9.3 快照 (Snapshots)

```
功能：
- 保存模拟器完整状态
- 快速恢复到特定状态
- 加速调试流程

应用场景：
- 保存登录后状态
- 保存特定 App 状态
- 快速复现问题
```

### 9.4 指纹模拟

```
1. Extended Controls -> Fingerprint
2. 选择指纹 ID (1-10)
3. 点击 "Touch Sensor"

# 测试生物认证功能
# 无需实际指纹硬件
```

---

## 10. Smali 调试 (smalidea)

### 10.1 概述

smalidea 是一个 Android Studio 插件，允许直接调试反编译后的 Smali 代码。

### 10.2 安装配置

```
1. 下载 smalidea 插件
   https://github.com/JesusFreke/smalidea

2. 安装插件
   Settings -> Plugins -> Install from disk

3. 重启 Android Studio
```

### 10.3 项目配置

```
1. 使用 apktool 反编译 APK
   apktool d target.apk -o target_smali

2. 在 Android Studio 中打开项目
   File -> Open -> 选择反编译目录

3. 设置为 Smali 项目
   File -> Project Structure
   -> Modules -> + -> Import Module
   -> 选择 smali 目录
```

### 10.4 调试步骤

```
1. 修改 AndroidManifest.xml
   添加 android:debuggable="true"

2. 重新打包签名
   apktool b target_smali -o target_debug.apk
   jarsigner -keystore debug.keystore target_debug.apk alias

3. 安装到设备
   adb install target_debug.apk

4. 在 Smali 代码中设置断点
   .line 42
   invoke-virtual {v0}, Lcom/example/Test;->encrypt()V  # <-- 断点

5. 附加调试器
   Run -> Attach Debugger to Android Process
```

### 10.5 Smali 调试技巧

```smali
# 查看寄存器值
# 断点暂停后，在 Variables 面板查看 v0, v1, p0, p1 等

# 常见寄存器：
# p0 = this (非静态方法)
# p1, p2... = 方法参数
# v0, v1... = 局部变量

# 修改寄存器值
# 右键 -> Set Value
```

---

## 11. Native 调试 (LLDB)

### 11.1 概述

Android Studio 集成了 LLDB 调试器，支持调试 C/C++ Native 代码。

### 11.2 配置要求

```
1. 安装 NDK
   SDK Manager -> SDK Tools -> NDK

2. 安装 LLDB
   SDK Manager -> SDK Tools -> LLDB

3. App 需要包含调试符号
   或使用带符号的 SO 文件
```

### 11.3 调试方式

#### 11.3.1 源码调试

```
1. 打开包含 Native 代码的项目
2. 选择 Native 调试配置
   Run -> Edit Configurations
   -> Debugger -> Debug type: Dual (Java + Native)

3. 在 C/C++ 代码中设置断点
4. 点击 Debug 运行
```

#### 11.3.2 附加到进程

```
1. Run -> Attach Debugger to Android Process
2. 选择进程
3. Debugger 选择 Native Only 或 Dual
4. 点击 OK
```

### 11.4 LLDB 命令

```lldb
# 基本命令
(lldb) bt                          # 查看调用栈
(lldb) frame select 2              # 选择栈帧
(lldb) register read               # 查看寄存器
(lldb) memory read 0x12345678      # 读取内存
(lldb) disassemble -a 0x12345678   # 反汇编

# 断点
(lldb) b JNI_OnLoad                # 函数断点
(lldb) b *0x12345678               # 地址断点
(lldb) br list                     # 列出断点
(lldb) br del 1                    # 删除断点

# 执行控制
(lldb) c                           # 继续执行
(lldb) n                           # 步过
(lldb) s                           # 步入
(lldb) finish                      # 步出

# 表达式
(lldb) p (char*)$x0                # 打印寄存器值
(lldb) x/10x $sp                   # 查看栈内容
```

### 11.5 逆向应用场景

```c
// 1. Hook JNI 函数
// 在 JNI_OnLoad 设置断点，分析动态注册

// 2. 分析 SO 加载
// 在 dlopen / android_dlopen_ext 设置断点

// 3. 追踪加密算法
// 在 AES / MD5 等函数设置断点

// 4. 分析反调试
// 在 ptrace / /proc/self/status 读取处设置断点
```

---

## 12. 终端与 ADB 集成

### 12.1 内置终端

```
View -> Tool Windows -> Terminal

# 直接在 Android Studio 中使用命令行
# 自动配置 PATH 包含 SDK 工具
```

### 12.2 常用 ADB 命令

```bash
# 设备管理
adb devices                          # 列出设备
adb -s <serial> shell                # 连接指定设备

# 应用管理
adb install app.apk                  # 安装应用
adb uninstall com.example.app        # 卸载应用
adb shell pm list packages           # 列出所有包
adb shell pm path com.example.app    # 获取 APK 路径

# 文件传输
adb push local.txt /sdcard/          # 上传文件
adb pull /sdcard/remote.txt ./       # 下载文件

# 调试
adb shell am start -D -n com.example/.MainActivity  # Debug 模式启动
adb forward tcp:8700 jdwp:PID        # 端口转发
adb jdwp                             # 列出可调试进程

# 日志
adb logcat -c                        # 清空日志
adb logcat *:E                       # 只显示 Error
adb bugreport                        # 生成 bug 报告

# Shell
adb shell                            # 进入 shell
adb shell "dumpsys activity"         # 查看 Activity 信息
adb shell "dumpsys package com.example.app"  # 查看包信息
```

### 12.3 Wireless ADB

```bash
# 配置无线调试 (Android 11+)
# 开发者选项 -> 无线调试 -> 启用

# 配对
adb pair <ip>:<port>
# 输入配对码

# 连接
adb connect <ip>:<port>

# 旧版本 (需要先 USB 连接)
adb tcpip 5555
adb connect <ip>:5555
```

---

## 13. 逆向常用插件

### 13.1 smalidea

```
功能：Smali 代码语法高亮和调试
地址：https://github.com/JesusFreke/smalidea
```

### 13.2 Java Decompiler (JD)

```
功能：反编译 JAR/Class 文件
集成：Android Studio 内置
```

### 13.3 APK Analyzer (内置)

```
功能：分析 APK 结构
使用：Build -> Analyze APK
```

### 13.4 Jadx (推荐配合使用)

```
功能：更强大的反编译工具
地址：https://github.com/skylot/jadx

# 虽然不是 AS 插件，但可以配合使用
# 支持导出为 Android Studio 项目
```

### 13.5 其他有用插件

```
1. Android Drawable Importer
   - 快速导入图片资源

2. ADB Idea
   - ADB 命令快捷操作

3. Key Promoter X
   - 学习快捷键

4. Rainbow Brackets
   - 彩色括号匹配
```

---

## 14. 调试技巧与最佳实践

### 14.1 调试 Release 版本

```
方法一：重新签名为 debuggable
1. 反编译 APK
2. 修改 AndroidManifest.xml: android:debuggable="true"
3. 重新打包签名

方法二：使用 Magisk 模块
- MagiskHide Props Config
- 全局开启调试

方法三：Frida spawn 注入
# 不需要 debuggable
frida -U -f com.example.app -l script.js
```

### 14.2 处理反调试

```java
// 常见反调试手段：
// 1. 检测调试器连接
Debug.isDebuggerConnected()

// 2. 检测 TracerPid
// /proc/self/status 中 TracerPid != 0

// 3. 时间检测
// 两次操作间隔过长

// 绕过方法：
// - Frida Hook 相关检测函数
// - 修改 Smali 代码跳过检测
// - 使用 Native 层 Hook
```

### 14.3 多设备调试

```
1. 连接多个设备
2. 在工具栏选择目标设备
3. 分别运行/调试

# 使用 scrcpy 同时控制多设备
scrcpy -s <serial>
```

### 14.4 远程调试

```bash
# 设置 JDWP 端口转发
adb forward tcp:8700 jdwp:<pid>

# 或使用 Android Studio 远程调试
Run -> Attach to Process -> 选择远程设备
```

### 14.5 调试快捷键速查

| 操作 | Windows/Linux | macOS |
|-----|--------------|-------|
| 运行 | `Shift+F10` | `Ctrl+R` |
| 调试 | `Shift+F9` | `Ctrl+D` |
| 停止 | `Ctrl+F2` | `Cmd+F2` |
| 步过 | `F8` | `F8` |
| 步入 | `F7` | `F7` |
| 步出 | `Shift+F8` | `Shift+F8` |
| 恢复 | `F9` | `Cmd+Option+R` |
| 切换断点 | `Ctrl+F8` | `Cmd+F8` |
| 查看断点 | `Ctrl+Shift+F8` | `Cmd+Shift+F8` |
| 计算表达式 | `Alt+F8` | `Option+F8` |

---

## 总结

Android Studio 提供了一套完整的调试和分析工具链。对于逆向工程师来说，掌握这些工具能够：

1. **快速了解 App 结构** - APK Analyzer
2. **实时分析运行状态** - Debugger + Profiler
3. **提取和分析数据** - Device File Explorer + Database Inspector
4. **UI 自动化准备** - Layout Inspector
5. **底层代码分析** - LLDB + smalidea

建议根据具体的逆向目标，选择合适的工具组合使用。
