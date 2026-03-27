---
title: "Android 四大组件"
date: 2024-06-26
type: posts
tags: ["加密分析", "Hook", "基础知识", "Smali", "Android", "ARM汇编"]
weight: 10
---

# Android 四大组件

Android 的应用框架核心由四个基本组件构成。每个组件都是一个独立的实体，系统和应用可以通过它进入你的 App。理解这四个组件的职责和生命周期是进行任何 Android 开发或逆向分析的基础。

---

## 1. 四大组件概述

```text
┌───────────────────────── Android 应用架构 ─────────────────────────┐
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              Application (全局入口)                           │  │
│  │       attachBaseContext() → onCreate()                       │  │
│  └──────────────────────┬───────────────────────────────────────┘  │
│                         │                                          │
│     ┌───────────────────┼───────────────────┐                     │
│     ▼                   ▼                   ▼                     │
│  ┌────────┐      ┌───────────┐      ┌──────────────┐             │
│  │Activity│      │  Service  │      │BroadcastRecvr│             │
│  │ (前台) │      │  (后台)   │      │   (事件)     │             │
│  └───┬────┘      └─────┬─────┘      └──────┬───────┘             │
│      └─────────────────┼────────────────────┘                     │
│                        ▼                                          │
│              ┌──────────────────┐                                 │
│              │ ContentProvider  │                                 │
│              │   (数据层)       │                                 │
│              └──────────────────┘                                 │
└────────────────────────────────────────────────────────────────────┘
```

| 组件 | 逆向价值 | 典型场景 |
|------|---------|---------|
| Activity | 用户可见的界面逻辑，登录/支付等关键流程 | 协议分析、界面逻辑还原 |
| Service | 后台核心业务，加密/通信/数据处理 | 推送协议、数据同步逻辑 |
| BroadcastReceiver | 事件触发机制，开机自启、指令下发 | 恶意软件分析、远控触发 |
| ContentProvider | 数据存储与共享接口 | 数据泄露检测、SQL注入 |

---

## 2. Activity 生命周期与逆向

### 2.1 生命周期图

```text
              ┌─────────────────┐
              │   onCreate()    │ ◄── 布局加载、数据初始化
              └────────┬────────┘     setContentView(), findViewById()
                       ▼
              ┌─────────────────┐
              │   onStart()     │ ◄── Activity 可见但不可交互
              └────────┬────────┘
                       ▼
              ┌─────────────────┐
              │  onResume()     │ ◄── 到达前台，可以交互
              └────────┬────────┘
                       ▼
              ┌─────────────────┐
              │  [运行状态]      │
              └────────┬────────┘
          ┌────────────┴────────────┐
          ▼                         ▼
  ┌─────────────┐          ┌──────────────┐
  │  onPause()  │          │   onStop()   │ ◄── 完全不可见
  └──────┬──────┘          └──────┬───────┘
         │                  ┌─────┴─────┐
         │                  ▼           ▼
         │          ┌────────────┐  ┌────────────┐
         │          │ onRestart()│  │ onDestroy()│
         │          └──────┬─────┘  └────────────┘
         └─────────────────┘
```

### 2.2 生命周期与 Hook 时机

| 生命周期方法 | Hook 价值 | 典型用途 |
|-------------|----------|---------|
| `onCreate()` | 极高 | 捕获初始化参数、加密密钥生成、布局加载 |
| `onResume()` | 高 | 捕获页面激活时的刷新逻辑、Token 校验 |
| `onPause()` | 中 | 分析数据持久化逻辑、会话保存 |
| `onActivityResult()` | 高 | 捕获跨 Activity 的数据回传（如支付结果） |
| `onNewIntent()` | 中 | singleTop/singleTask 模式下的 Intent 更新 |

**Frida Hook Activity 生命周期**:

```javascript
Java.perform(function() {
    var LoginActivity = Java.use("com.example.app.LoginActivity");

    LoginActivity.onCreate.overload("android.os.Bundle").implementation = function(bundle) {
        console.log("[*] LoginActivity.onCreate() called");
        var intent = this.getIntent();
        var extras = intent.getExtras();
        if (extras != null) {
            var keys = extras.keySet().iterator();
            while (keys.hasNext()) {
                var key = keys.next();
                console.log("[*] Extra: " + key + " = " + extras.get(key));
            }
        }
        this.onCreate(bundle);
    };
});
```

### 2.3 快速定位当前 Activity

```bash
# 查看当前前台 Activity
adb shell dumpsys activity top | grep ACTIVITY

# 监控 Activity 启动（实时）
adb shell am monitor

# 启动指定 Activity（带参数）
adb shell am start -n com.example.app/.DeepLinkActivity \
    -a android.intent.action.VIEW \
    -d "myapp://payment?orderId=12345"
```

### 2.4 混淆代码中的定位技巧

Activity 类名不会被混淆（Manifest 中声明），但内部方法和字段会。定位策略：

1. 从 Manifest 找到 Activity 类名（明文）
2. 分析 `onCreate()` 中的 `setContentView(R.layout.xxx)` 找到布局 ID
3. 通过布局 XML 中的控件 ID 反向追踪 `findViewById()` 调用
4. 从控件的事件监听器切入，追踪业务逻辑

---

## 3. Service 分析

### 3.1 Service 类型

```text
启动服务 (Started):   startService() → onStartCommand() → [后台运行] → stopSelf()
绑定服务 (Bound):     bindService()  → onBind() → [Binder 交互] → onUnbind()
前台服务 (Foreground): startForegroundService() → startForeground(id, notification)
```

### 3.2 Service 中常见的逆向目标

```java
public class CryptoService extends Service {
    private SecretKey aesKey;

    @Override
    public void onCreate() {
        super.onCreate();
        // 逆向关键点 1: 密钥初始化
        aesKey = generateKey("hardcoded_seed_123");
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        if ("ENCRYPT_AND_SEND".equals(intent.getAction())) {
            // 逆向关键点 2: 数据加密流程
            byte[] plainData = intent.getByteArrayExtra("data");
            byte[] encrypted = encrypt(aesKey, plainData);
            sendToServer(encrypted);
        }
        return START_STICKY; // 被杀后自动重启
    }

    @Override
    public IBinder onBind(Intent intent) {
        // 逆向关键点 3: 暴露给其他组件的接口
        return new CryptoBinder();
    }

    public class CryptoBinder extends Binder {
        public byte[] encryptData(byte[] data) { return encrypt(aesKey, data); }
        public byte[] decryptData(byte[] data) { return decrypt(aesKey, data); }
    }
}
```

### 3.3 Hook Service 关键方法

```javascript
Java.perform(function() {
    var CryptoService = Java.use("com.example.app.CryptoService");

    CryptoService.onStartCommand.implementation = function(intent, flags, startId) {
        console.log("[*] CryptoService.onStartCommand()");
        console.log("[*] Action: " + intent.getAction());
        return this.onStartCommand(intent, flags, startId);
    };

    // Hook 加密方法直接获取密钥和明文/密文
    CryptoService.encrypt.implementation = function(key, data) {
        console.log("[*] 密钥: " + key.toString());
        console.log("[*] 明文: " + bytesToHex(data));
        var result = this.encrypt(key, data);
        console.log("[*] 密文: " + bytesToHex(result));
        return result;
    };
});
```

```bash
# 列出运行中的 Service
adb shell dumpsys activity services com.example.app
```

---

## 4. BroadcastReceiver 分析

### 4.1 静态注册与动态注册

**静态注册** -- `AndroidManifest.xml` 中声明，App 未运行也能响应：

```xml
<receiver android:name=".receiver.BootReceiver"
          android:exported="true">
    <intent-filter>
        <action android:name="android.intent.action.BOOT_COMPLETED" />
    </intent-filter>
</receiver>
```

**动态注册** -- 代码中注册，需要搜索 `registerReceiver` 调用来发现：

```java
receiver = new NetworkChangeReceiver();
IntentFilter filter = new IntentFilter(ConnectivityManager.CONNECTIVITY_ACTION);
registerReceiver(receiver, filter);
```

### 4.2 发现动态注册的 Receiver

```javascript
Java.perform(function() {
    var ContextWrapper = Java.use("android.content.ContextWrapper");
    ContextWrapper.registerReceiver.overload(
        "android.content.BroadcastReceiver", "android.content.IntentFilter"
    ).implementation = function(receiver, filter) {
        console.log("[*] registerReceiver: " + receiver.getClass().getName());
        for (var i = 0; i < filter.countActions(); i++) {
            console.log("[*]   Action: " + filter.getAction(i));
        }
        return this.registerReceiver(receiver, filter);
    };
});
```

### 4.3 恶意软件中常见的 Receiver 模式

| 监听的广播 Action | 恶意用途 |
|------------------|---------|
| `BOOT_COMPLETED` | 开机自启，持久化驻留 |
| `CONNECTIVITY_ACTION` | 网络恢复时上传窃取的数据 |
| `SMS_RECEIVED` | 拦截短信（验证码窃取） |
| `NEW_OUTGOING_CALL` | 监听/拦截电话拨打 |
| `SCREEN_ON` / `SCREEN_OFF` | 判断用户活跃状态 |
| 自定义 Action | C2 指挥控制指令下发 |

```bash
# 向导出的 Receiver 发送广播测试
adb shell am broadcast \
    -a com.example.app.ACTION_EXECUTE_COMMAND \
    --es command "get_device_info"
```

---

## 5. ContentProvider 分析

### 5.1 URI 结构

```text
content://com.example.app.provider/users/10
\_____/   \________________________/ \___/ \/
 scheme          authority           path   id

常见模式:
  content://authority/table          → 所有记录
  content://authority/table/10       → ID=10 的记录
  content://authority/table/10/sub   → 子资源
```

### 5.2 安全风险：SQL 注入

```java
@Override
public Cursor query(Uri uri, String[] projection, String selection,
                    String[] selectionArgs, String sortOrder) {
    // 如果 selection 未做过滤，可能存在 SQL 注入
    // 攻击: selection = "1=1) UNION SELECT password FROM credentials--"
    return db.query("users", projection, selection, selectionArgs,
                    null, null, sortOrder);
}
```

### 5.3 通过 adb 测试 ContentProvider

```bash
# 查询导出的 ContentProvider
adb shell content query --uri content://com.example.app.provider/users

# SQL 注入测试
adb shell content query \
    --uri content://com.example.app.provider/users \
    --where "name='admin' OR '1'='1'"

# 路径遍历测试 (FileProvider)
adb shell content read \
    --uri content://com.example.app.fileprovider/root/data/data/com.example.app/shared_prefs/config.xml
```

### 5.4 FileProvider 路径遍历漏洞

```xml
<!-- res/xml/file_paths.xml -->
<paths>
    <!-- 危险: 暴露整个外部存储 -->
    <external-path name="external" path="." />
    <!-- 危险: 暴露应用私有目录根 -->
    <root-path name="root" path="" />
    <!-- 安全: 只暴露特定目录 -->
    <files-path name="images" path="images/" />
</paths>
```

---

## 6. Application 类

### 6.1 Application 的特殊地位

`Application` 类是应用中最先被创建的对象，生命周期覆盖整个进程。这使它成为逆向中最关键的切入点。

```text
应用启动顺序:
  1. Zygote fork 新进程
  2. Application.attachBaseContext()  ◄── 最早的代码入口，壳在此脱壳
  3. ContentProvider.onCreate()       ◄── 在 Application.onCreate 之前！
  4. Application.onCreate()           ◄── 全局初始化，SDK/网络/安全检测
  5. 首个 Activity/Service/Receiver 创建
```

### 6.2 典型的 Application 子类

```java
public class MyApplication extends Application {

    @Override
    protected void attachBaseContext(Context base) {
        super.attachBaseContext(base);
        MultiDex.install(this);  // 多 DEX 加载
        // 加固壳入口: 360/腾讯乐固/梆梆 在此解密并加载真正的 DEX
    }

    @Override
    public void onCreate() {
        super.onCreate();
        initNetwork();           // 网络框架配置
        initEncryption();        // 加密模块初始化
        initAntiDebug();         // 反调试检测
        initRootDetection();     // Root 检测
        loadNativeLibrary();     // 加载 SO 库
    }
}
```

### 6.3 Hook Application 关键方法

```javascript
Java.perform(function() {
    var MyApp = Java.use("com.example.app.MyApplication");

    MyApp.attachBaseContext.implementation = function(context) {
        console.log("[*] attachBaseContext() -- 最早入口");
        this.attachBaseContext(context);
        // 此时加固壳已解密 DEX
    };

    // 绕过安全检测
    MyApp.initAntiDebug.implementation = function() {
        console.log("[*] 跳过反调试检测");
    };
    MyApp.initRootDetection.implementation = function() {
        console.log("[*] 跳过 Root 检测");
    };
});
```

在 Manifest 中定位: `<application android:name=".MyApplication" ...>`。如果没有 `android:name` 属性，则使用默认的 `android.app.Application` 类。

---

## 7. Intent 机制

### 7.1 Intent 的组成

```text
Action     → 要执行的操作（如 VIEW, SEND, MAIN）
Data       → 操作的数据 URI（如 content://, http://）
Category   → 对组件的附加限定（如 LAUNCHER, DEFAULT）
Component  → 显式指定目标组件（包名+类名）
Extras     → 附加的键值对数据（Bundle）
Flags      → 控制启动模式和任务栈行为
```

### 7.2 显式 vs 隐式 Intent

```java
// 显式 -- 直接指定目标，可直接追踪
Intent explicit = new Intent(this, PaymentActivity.class);
explicit.putExtra("order_id", "ORD_12345");
startActivity(explicit);

// 隐式 -- 通过 Action/Data 匹配，需查 Manifest 中的 intent-filter
Intent implicit = new Intent("com.example.app.ACTION_PAY");
implicit.setData(Uri.parse("pay://checkout?token=abc123"));
startActivity(implicit);
```

### 7.3 Deep Link 分析

Deep Link 允许外部通过 URI 直接打开应用特定页面，是重要的攻击面：

```xml
<activity android:name=".DeepLinkActivity" android:exported="true">
    <intent-filter>
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />
        <data android:scheme="myapp" android:host="payment" />
        <data android:scheme="https" android:host="www.example.com"
              android:pathPrefix="/pay" />
    </intent-filter>
</activity>
```

```bash
# 测试 Deep Link
adb shell am start -a android.intent.action.VIEW \
    -d "myapp://payment?orderId=12345&token=abc"
```

### 7.4 追踪 Intent 数据流

```javascript
Java.perform(function() {
    var Activity = Java.use("android.app.Activity");
    Activity.startActivity.overload("android.content.Intent").implementation = function(intent) {
        console.log("[*] 调用者: " + this.getClass().getName());
        console.log("[*] 目标: " + intent.getComponent());
        console.log("[*] Action: " + intent.getAction());
        console.log("[*] Data: " + intent.getDataString());
        var bundle = intent.getExtras();
        if (bundle != null) {
            var keys = bundle.keySet().iterator();
            while (keys.hasNext()) {
                var key = keys.next();
                console.log("[*] Extra: " + key + " = " + bundle.get(key));
            }
        }
        this.startActivity(intent);
    };
});
```

---

## 8. 逆向中的关键切入点

### 8.1 分析流程

```text
Step 1: 静态分析 Manifest
  → 找 Application 子类、主 Activity、exported 组件、权限列表

Step 2: 动态定位目标组件
  → dumpsys activity top、dumpsys activity services、logcat

Step 3: Hook 关键生命周期
  → attachBaseContext (壳)、onCreate (页面)、onStartCommand (后台)、onReceive (事件)

Step 4: 追踪数据流
  → Intent 传递、加密函数、网络请求、ContentProvider 操作
```

### 8.2 按场景选择 Hook 目标

| 逆向目标 | 首选 Hook 组件 | 关键方法 |
|----------|---------------|---------|
| 登录协议 | LoginActivity | `onCreate()` 中的按钮事件 |
| 支付流程 | PaymentActivity / PayService | `onClick()`, `onActivityResult()` |
| 数据加密 | CryptoService / EncryptUtil | `encrypt()`, `decrypt()`, `sign()` |
| 网络请求 | OkHttp Interceptor | `intercept()`, `proceed()` |
| 推送消息 | PushService / PushReceiver | `onStartCommand()`, `onReceive()` |
| 反调试绕过 | Application / NativeLib | `onCreate()`, JNI 函数 |

### 8.3 混淆应用的突破策略

```text
未混淆的通常保留:                    通常被混淆:
  Activity/Service/Provider 类名       内部工具类名 (Utils → a)
  JNI native 方法名                    方法名 (encryptData → b)
  日志字符串（如果未被移除）            字段名 (secretKey → c)
```

突破方法：

1. **从组件入手**: Activity/Service 类名是明文，从生命周期方法开始追踪
2. **字符串搜索**: 搜索错误提示、URL、常量字符串定位关键逻辑
3. **API 调用追踪**: Hook `Cipher.doFinal()`、`URL.openConnection()` 从底层向上追踪
4. **交叉引用**: 在 jadx/IDA 中从已知方法出发追踪调用链

### 8.4 实战：从零开始分析

```bash
# 1. 解包
apktool d target.apk -o target_decoded

# 2. 快速浏览 Manifest
grep "android:name" target_decoded/AndroidManifest.xml | head -5
grep "exported=\"true\"" target_decoded/AndroidManifest.xml
grep -A5 "MAIN" target_decoded/AndroidManifest.xml

# 3. 动态定位
adb shell dumpsys activity top | grep "ACTIVITY"
adb logcat | grep -i "com.example.app"

# 4. Frida 注入
frida -U -f com.example.app -l hook_script.js
```

### 8.5 逆向分析优先级

1. **Application** - 全局初始化，识别加固方案，绕过安全检测
2. **Activity** - 从界面入手，找到目标功能入口点
3. **Service** - 后台核心业务：加密、通信、数据处理
4. **BroadcastReceiver** - 系统事件和自定义事件响应
5. **ContentProvider** - 数据接口，可能存在数据泄露

---
