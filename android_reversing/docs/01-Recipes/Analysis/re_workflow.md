# Android 应用逆向工程完整工作流程

## 问题场景

你刚拿到一个 Android 应用需要分析，但面临以下挑战：

- **"拿到 APK 后应该先做什么？从哪里入手？"**
- **"静态分析和动态分析应该如何配合？"**
- **"如何系统化地分析，而不是盲目尝试？"**
- **"遇到加固、混淆、反调试该怎么办？"**
- **"分析完成后如何修改应用以达到目的？"**

本配方提供一个**经过实战验证的标准化工作流程**，帮助你系统化地完成从信息收集到代码修改的整个逆向工程过程。

---

## 工具清单

### 必备工具

| 项目                 | 说明                     |
| -------------------- | ------------------------ |
| **APK 提取**         | ADB + Package Manager    |
| **解包/回包**        | Apktool                  |
| **反编译工具**       | Jadx-GUI（推荐）或 JEB   |
| **动态分析**         | Frida + Frida-tools      |
| **Root 设备/模拟器** | Genymotion、夜神、雷电等 |

### 可选工具

| 项目            | 说明                             |
| --------------- | -------------------------------- |
| **Native 分析** | IDA Pro / Ghidra / Binary Ninja  |
| **网络抓包**    | mitmproxy / Burp Suite / Charles |
| **调试器**      | Android Studio / jdb             |
| **签名工具**    | apksigner（Android SDK 自带）    |
| **加壳检测**    | PKid / ApkTool-Plus              |

---

## 前置知识

- 了解 Android 基本架构（四大组件、Manifest 文件）
- 掌握基本 Java/Smali 语法
- 熟悉 ADB 命令
- 拥有 Root 设备（动态分析必需）

---

## 解决方案

### 核心原则

> **由外到内、由浅入深、静动结合**
>
> 1. **信息侦察** → 了解应用基本信息和技术栈
> 2. **静态分析** → 理解代码逻辑和算法
> 3. **动态验证** → 观察实际行为、绕过保护
> 4. **代码修改** → 实现永久性改动

---

## 阶段一：信息收集与初步分析（15-30 分钟）

**目标**：在不运行应用的情况下，快速了解基本信息、功能和潜在入口点。

### 步骤 1：获取 APK 文件

#### 方法 A：从已安装应用提取

```bash
# 1. 列出所有包名
adb shell pm list packages | grep <关键词>

# 示例：查找音乐应用
adb shell pm list packages | grep music
# 输出：package:com.example.musicapp

# 2. 获取 APK 路径
adb shell pm path com.example.musicapp
# 输出：package:/data/app/~~ABC123/com.example.musicapp-XYZ456/base.apk

# 3. 拉取到本地
adb pull /data/app/~~ABC123/com.example.musicapp-XYZ456/base.apk ./target.apk
```

#### 一键脚本（保存为 pull-apk.sh）

```bash
#!/bin/bash
PACKAGE=$1
APK_PATH=$(adb shell pm path $PACKAGE | cut -d: -f2 | tr -d '\r')
adb pull $APK_PATH ./$PACKAGE.apk
echo "[+] APK 已保存: $PACKAGE.apk"
```

### 步骤 2：解包 APK

```bash
# 使用 Apktool（推荐 - 解码资源和 Smali）
apktool d target.apk -o target_unpacked

# 输出目录结构：
# target_unpacked/
# ├── AndroidManifest.xml (已解码)
# ├── apktool.yml
# ├── smali/ (Dalvik 字节码)
# ├── smali_classes2/ (多个 DEX)
# ├── res/ (资源文件)
# ├── lib/ (native 库)
# ├── assets/ (资产文件)
# └── original/

# 快速查看（不解码）
unzip -l target.apk
unzip target.apk -d target_quick
```

### 步骤 3：分析 AndroidManifest.xml

```bash
# 查看已解码的 manifest
cat target_unpacked/AndroidManifest.xml

# 或使用工具美化
xmllint --format target_unpacked/AndroidManifest.xml
```

**关键信息提取表**：

| 信息项              | 位置                               | 意义                                   |
| ------------------- | ---------------------------------- | -------------------------------------- |
| **包名**            | `<manifest package="...">`         | 应用唯一标识                           |
| **入口 Activity**   | `<activity>` 带 `LAUNCHER` intent  | 应用启动入口                           |
| **Application 类**  | `<application android:name="...">` | 自定义 Application（可能有初始化逻辑） |
| **权限**            | `<uses-permission>`                | 推断功能（网络、存储、位置等）         |
| **调试标志**        | `android:debuggable="true"`        | 可直接调试                             |
| **备份标志**        | `android:allowBackup="true"`       | 数据可导出                             |
| **导出组件**        | `android:exported="true"`          | 可被外部调用                           |
| **URL Scheme**      | `<intent-filter>` 带 `<data>`      | Deep link 入口点                       |
| **ContentProvider** | `<provider>`                       | 数据库接口                             |
| **Service**         | `<service>`                        | 后台服务                               |

#### 真实案例：分析腾讯乐固应用

```xml
<application
    android:name="com.tencent.StubShell.TxAppEntry"  <!-- 加壳特征 -->
    android:debuggable="false"
    android:allowBackup="false">

    <activity android:name=".MainActivity"
        android:exported="true">  <!-- 可外部启动 -->
        <intent-filter>
            <action android:name="android.intent.action.MAIN"/>
            <category android:name="android.intent.category.LAUNCHER"/>
        </intent-filter>

        <!-- 自定义 URL Scheme -->
        <intent-filter>
            <data android:scheme="myapp" android:host="open"/>
            <action android:name="android.intent.action.VIEW"/>
            <category android:name="android.intent.category.BROWSABLE"/>
        </intent-filter>
    </activity>
</application>
```

**分析结论**：

- 可通过 `myapp://open` URL 启动
- 调试和备份已禁用（安全配置良好）

---

### 步骤 4：快速目录结构审查

```bash
# 查看 native 库
ls -lh target_unpacked/lib/*/
# 输出示例：
# lib/arm64-v8a/libnative-lib.so (2.3 MB) ← Native 代码
# lib/arm64-v8a/libencrypt.so (450 KB) ← 可能是加密库
# lib/armeabi-v7a/libnative-lib.so

# 查看资产文件
ls -lh target_unpacked/assets/
# 输出示例：
# config.json ← 配置文件
# encrypted.dat ← 加密数据
# web/index.html ← H5 页面

# 统计 Smali 文件数量（估算代码规模）
find target_unpacked/smali* -name "*.smali" | wc -l
# 输出：8432 (约 8000+ 类)

# 搜索可疑关键词
grep -r "password" target_unpacked/smali/ | head -n 10
grep -r "encrypt" target_unpacked/smali/ | head -n 10
```

**阶段一产出**：

- 技术栈识别（是否加壳、是否使用 native 代码）
- 潜在攻击面（导出组件、URL Scheme）
- 初步分析方向（应该深入哪里）

---

## 阶段二：静态分析（1-3 小时）

**目标**：通过反编译理解应用如何工作、算法和业务逻辑。

### 步骤 1：使用 Jadx 反编译

```bash
# 启动 Jadx GUI
jadx-gui target.apk

# 或命令行模式
jadx -d target_decompiled target.apk
```

**关键搜索词**：

- "encrypt"、"decrypt"、"AES"、"DES" → 加密算法
- "http"、"api"、"request" → 网络请求
- "premium"、"vip"、"paid" → 会员检查
- "signature"、"sign" → 签名算法
- "root"、"frida"、"xposed" → 反检测

**定位关键代码**：

1. 从入口 Activity 开始（`MainActivity.onCreate()`）
2. 检查 Application 子类（`Application.onCreate()` - 初始化逻辑）
3. 搜索字符串常量（右键 → "查找用法"）
4. 分析网络请求（OkHttp、Retrofit、HttpURLConnection）
5. 追踪用户输入处理（`onClick` 回调）

**代码导航快捷键**：

- Ctrl+H：查看类层次结构
- Ctrl+F12：查看当前类的所有方法

---

### 步骤 2：识别代码模式

#### 正常代码

```java
// 可读的类名和方法名
public class LoginManager {
    private static final String API_URL = "https://api.example.com/login";

    public boolean login(String username, String password) {
        String encryptedPassword = AESUtil.encrypt(password);
        return ApiClient.post(API_URL, username, encryptedPassword);
    }
}
```

#### 混淆代码

```java
// ProGuard/R8 混淆
public class a {
    private static final String a = "https://api.example.com/login";

    public boolean a(String str, String str2) {
        String b = b.a(str2);  // 字符串常量通常会保留
        return c.a(a, str, b);
    }
}
```

---

### 步骤 3：分析 Native 库

如果应用包含 `.so` 文件，核心算法通常在这里实现。

#### 方法 A：使用 IDA Pro 分析

```bash
# 1. 打开 SO 文件
ida64 target_unpacked/lib/arm64-v8a/libnative-lib.so

# 2. 等待自动分析完成

# 3. 查看导出函数（Exports 窗口）
# 查找 JNI 函数命名模式：
# Java_com_example_app_NativeHelper_encrypt
# Java_<包名>_<类名>_<方法名>

# 4. 反编译关键函数（F5 反编译为伪代码）
```

#### 方法 B：使用 Ghidra 分析

```bash
# 1. 启动 Ghidra
ghidraRun

# 2. 新建项目 → 导入文件 → 选择 .so 文件

# 3. 双击文件 → 自动分析

# 4. 窗口 → Symbol Tree → Exports
# 查看导出函数列表

# 5. 双击函数 → 反编译（右侧面板显示 C 伪代码）
```

#### 方法 C：快速命令行分析

```bash
# 查看导出函数
nm -D libnative-lib.so | grep Java
# 输出示例：
# 00012340 T Java_com_example_app_Crypto_encrypt
# 00012680 T Java_com_example_app_Crypto_decrypt
# 00012a00 T Java_com_example_app_Sign_generate

# 搜索字符串（可能找到加密密钥）
strings libnative-lib.so | grep -i "key\|secret\|password"
```

### 步骤 4：创建分析笔记

```markdown
## 分析目标

- 提取登录 API 签名算法
- 绕过 VIP 会员检查
- 获取加密密钥

## 已定位的关键类/方法

1. `com.example.app.utils.SignUtil.generateSign(Map params)` - 签名生成
2. `com.example.app.user.UserManager.isPremium()` - 会员检查
3. Native: `Java_com_example_app_Crypto_encrypt` - 加密函数

## Hook 策略

- Hook `generateSign()` 查看参数和返回值
- Hook `isPremium()` 强制返回 true
- Hook native 函数获取加密密钥

## 预期挑战

- 签名算法可能在 native 层
- 可能有 Frida 检测
- 网络请求可能有 SSL pinning
```

### 阶段二产出

- 理解应用的核心功能和业务逻辑
- 定位关键类、方法和 native 函数
- 识别使用的加密/签名算法
- 确定动态分析的 hook 点清单
- 识别潜在的反调试/反 hook 机制

---

## 阶段三：动态分析（2-4 小时）

**目标**：在运行时观察实际行为，验证静态分析结论，绕过保护机制。

### 步骤 1：设置 Frida 环境

```bash
# 1. 启动 Frida Server（在设备上）
adb push frida-server /data/local/tmp/
adb shell "chmod 755 /data/local/tmp/frida-server"
adb shell "/data/local/tmp/frida-server &"

# 2. 验证连接（在 PC 上）
frida-ps -U
# 应该看到设备上运行的进程列表

# 3. 测试 hook
frida -U -f com.example.app --no-pause
# 进入交互式控制台
```

### 步骤 2：编写 Hook 脚本

基于静态分析结果，编写 Frida 脚本。

#### 示例 1：Hook 会员检查

```javascript
// hook_premium.js - 绕过 VIP 检查

Java.perform(function () {
  console.log("[+] 开始 hook 会员检查...");

  var UserManager = Java.use("com.example.app.user.UserManager");

  // Hook isPremium 方法
  UserManager.isPremium.implementation = function () {
    console.log("[+] isPremium() 被调用");

    // 调用原始方法查看真实结果
    var realResult = this.isPremium();
    console.log("    真实返回值: " + realResult);

    // 强制返回 true
    console.log("    修改返回值: true");
    return true;
  };

  console.log("[+] Hook 完成");
});
```

#### 示例 2：提取签名算法

```javascript
// hook_sign.js - 提取签名算法

Java.perform(function () {
  var SignUtil = Java.use("com.example.app.utils.SignUtil");

  SignUtil.generateSign.implementation = function (params) {
    console.log("\n[SIGN] generateSign() 被调用");
    console.log("    参数类型: " + params.$className);

    // 如果是 Map，遍历打印
    if (params.$className === "java.util.HashMap") {
      var HashMap = Java.use("java.util.HashMap");
      var entrySet = params.entrySet();
      var iterator = entrySet.iterator();

      console.log("    参数内容:");
      while (iterator.hasNext()) {
        var entry = iterator.next();
        var key = entry.getKey();
        var value = entry.getValue();
        console.log("        " + key + " = " + value);
      }
    }

    // 调用原始方法
    var result = this.generateSign(params);

    console.log("    签名结果: " + result);
    console.log("    签名长度: " + result.length);

    // 打印调用栈
    console.log("    调用栈:");
    console.log(
      Java.use("android.util.Log").getStackTraceString(
        Java.use("java.lang.Exception").$new()
      )
    );

    return result;
  };

  console.log("[+] 签名 hook 完成");
});
```

#### 示例 3：Hook Native 函数

```javascript
// hook_native.js - Hook native 加密函数

var encryptAddr = Module.findExportByName(
  "libnative-lib.so",
  "Java_com_example_app_Crypto_encrypt"
);

if (encryptAddr) {
  console.log("[+] 找到 encrypt 函数: " + encryptAddr);

  Interceptor.attach(encryptAddr, {
    onEnter: function (args) {
      console.log("\n[NATIVE] encrypt() 被调用");
      console.log("    JNIEnv*: " + args[0]);
      console.log("    jobject: " + args[1]);

      // 第 3 个参数通常是 jstring（输入数据）
      try {
        var env = Java.vm.getEnv();
        var inputStr = env.getStringUtfChars(args[2], null);
        var input = inputStr.readCString();
        console.log("    输入: " + input);
        env.releaseStringUtfChars(args[2], inputStr);
      } catch (e) {
        console.log("    输入: [无法读取]");
      }
    },

    onLeave: function (retval) {
      // 返回值也是 jstring（密文）
      try {
        var env = Java.vm.getEnv();
        var outputStr = env.getStringUtfChars(retval, null);
        var output = outputStr.readCString();
        console.log("    输出: " + output);
        env.releaseStringUtfChars(retval, outputStr);
      } catch (e) {
        console.log("    输出: " + retval);
      }
    },
  });

  console.log("[+] Native hook 完成");
} else {
  console.log("[-] 未找到 encrypt 函数");
}
```

### 步骤 3：绕过反调试检测

```javascript
// bypass_all.js - 综合绕过脚本

Java.perform(function () {
  console.log("[+] 加载反检测模块...");

  // 1. 绕过 Frida 端口检测
  var connect = Module.findExportByName("libc.so", "connect");
  Interceptor.attach(connect, {
    onEnter: function (args) {
      var sockaddr = ptr(args[1]);
      var port = (sockaddr.add(2).readU8() << 8) | sockaddr.add(3).readU8();
      if (port === 27042 || port === 27043) {
        console.log("[检测] 拦截了 Frida 端口扫描");
        sockaddr.add(2).writeU8(0xff);
      }
    },
  });

  // 2. 绕过 TracerPid 检测
  var fgets = Module.findExportByName("libc.so", "fgets");
  Interceptor.attach(fgets, {
    onLeave: function (retval) {
      if (retval && !retval.isNull()) {
        var line = retval.readCString();
        if (line && line.includes("TracerPid:")) {
          retval.writeUtf8String("TracerPid:\t0\n");
          console.log("[检测] 修改 TracerPid 为 0");
        }
      }
    },
  });

  // 3. 绕过字符串检测
  var strstr = Module.findExportByName("libc.so", "strstr");
  Interceptor.attach(strstr, {
    onLeave: function (retval) {
      if (this.needle && this.needle.toLowerCase().includes("frida")) {
        retval.replace(ptr(0));
        console.log("[检测] 隐藏 Frida 字符串");
      }
    },
    onEnter: function (args) {
      this.needle = args[1].readCString();
    },
  });

  console.log("[+] 反检测模块加载完成");
});
```

### 步骤 4：运行分析

```bash
# 组合使用多个脚本
frida -U -f com.example.app \
    -l bypass_all.js \
    -l hook_premium.js \
    --no-pause
```

### 步骤 5：网络流量分析

```bash
# 1. 配置代理
adb shell settings put global http_proxy 192.168.1.100:8080

# 2. 启动应用并绕过 SSL pinning
frida -U -f com.example.app -l bypass_ssl_pinning.js --no-pause

# 3. 在 Burp Suite 中查看流量
```

#### Hook OkHttp 请求

```javascript
// hook_okhttp.js
Java.perform(function () {
  var RealInterceptorChain = Java.use(
    "okhttp3.internal.http.RealInterceptorChain"
  );

  RealInterceptorChain.proceed.implementation = function (request) {
    console.log(
      "\n[HTTP] " + request.method() + " " + request.url().toString()
    );

    // 打印请求头
    var headers = request.headers();
    for (var i = 0; i < headers.size(); i++) {
      console.log("    " + headers.name(i) + ": " + headers.value(i));
    }

    var response = this.proceed(request);

    console.log("[RESP] Code: " + response.code());

    return response;
  };
});
```

### 阶段三产出

- 成功绕过会员检查、反调试等限制
- 完整的网络请求/响应日志
- 准备好重打包的修改点

---

## 阶段四：代码修改与重打包（30-60 分钟）

**目标**：对应用进行永久性修改，实现持久化的功能改变。

### 步骤 1：修改 Smali 代码

基于动态分析结果，在 Smali 层面进行修改。

#### 示例 1：绕过会员检查

**原始 Java 代码**（Jadx 反编译）：

```java
public boolean isPremium() {
    return this.userInfo.vipStatus == 1;
}
```

**原始 Smali 代码**：

```smali
.method public isPremium()Z
    .locals 2

    # 读取 userInfo.vipStatus
    iget-object v0, p0, Lcom/example/app/user/UserManager;->userInfo:Lcom/example/app/model/UserInfo;
    iget v0, v0, Lcom/example/app/model/UserInfo;->vipStatus:I

    # 比较是否等于 1
    const/4 v1, 0x1
    if-ne v0, v1, :cond_0

    # 如果相等，返回 true
    const/4 v0, 0x1
    return v0

    # 如果不相等，返回 false
    :cond_0
    const/4 v0, 0x0
    return v0
.end method
```

**修改后 Smali 代码**：

```smali
.method public isPremium()Z
    .locals 1

    # 直接返回 true，跳过所有检查
    const/4 v0, 0x1
    return v0
.end method
```

#### 示例 2：移除广告显示

**原始 Smali 代码**：

```smali
.method private showAd()V
    .locals 1

    # 检查是否不是 VIP
    invoke-virtual {p0}, Lcom/example/app/MainActivity;->isPremium()Z
    move-result v0

    # 如果不是 VIP，显示广告
    if-nez v0, :cond_0
    invoke-direct {p0}, Lcom/example/app/MainActivity;->loadAdView()V

    :cond_0
    return-void
.end method
```

**修改后 Smali 代码**：

```smali
.method private showAd()V
    .locals 0

    # 直接返回，不执行任何操作
    return-void
.end method
```

### 步骤 2：重新打包 APK

```bash
# 1. 使用 Apktool 重打包
apktool b target_unpacked -o modified.apk

# 输出：
# I: Using Apktool 2.x.x
# I: Checking whether sources has changed...
# I: Smali folder: smali
# I: Smali folder: smali_classes2
# I: Copying raw resources...
# I: Copying libs... (/lib)
# I: Copying assets... (/assets)
# I: Building apk file...
# I: Copying unknown files/dir...
# I: Built apk into: modified.apk

# 2. 检查生成的 APK
ls -lh modified.apk
# -rw-r--r-- 1 user user 8.5M modified.apk
```

### 步骤 3：签名 APK

```bash
# 1. 生成签名密钥（只需执行一次）
keytool -genkey -v \
    -keystore my-release-key.keystore \
    -alias my-key-alias \
    -keyalg RSA \
    -keysize 2048 \
    -validity 10000

# 提示输入密码和信息：
# Enter keystore password: [输入密码]
# Re-enter new password: [再次输入]
# What is your first and last name? [随意填写]
# ...

# 2. 签名 APK
apksigner sign \
    --ks my-release-key.keystore \
    --ks-key-alias my-key-alias \
    --out signed.apk \
    modified.apk

# 提示输入 keystore 密码
# 输出：signed.apk

# 3. 验证签名
apksigner verify signed.apk
# 输出：Verifies
# 表示签名成功
```

#### 使用 uber-apk-signer（更简单）

```bash
java -jar uber-apk-signer.jar --apks modified.apk
# 输出：modified-aligned-debugSigned.apk
```

### 步骤 4：安装测试

```bash
# 1. 卸载原应用（如果存在）
adb uninstall com.example.app

# 2. 安装修改后的 APK
adb install signed.apk

# 如果遇到签名冲突：
# adb install -r signed.apk (替换安装)

# 3. 启动应用
adb shell am start -n com.example.app/.MainActivity

# 4. 查看日志验证修改
adb logcat | grep "example.app"
```

**验证清单**：

- 修改的功能生效（例如 VIP 权限解锁）
- 没有崩溃或异常行为
- 网络功能正常（如果修改了签名相关代码）

### 常见问题排查

```bash
# 查看崩溃日志
adb logcat | grep "AndroidRuntime"

# 常见错误：
# 1. "INSTALL_PARSE_FAILED_NO_CERTIFICATES"
#    → 签名失败，重新签名

# 2. "INSTALL_FAILED_UPDATE_INCOMPATIBLE"
#    → 签名不匹配，先卸载原应用

# 3. 应用崩溃
#    → 查看 logcat，可能是 Smali 语法错误
```

---

## 工作流程总结

```text
信息收集 (15-30 分钟)
        ↓
    快速了解技术栈
    避免盲目分析浪费时间
        ↓
静态分析 (1-3 小时)
        ↓
    理解代码逻辑和算法
    定位关键函数和 hook 点
        ↓
动态分析 (2-4 小时)
        ↓
    验证静态分析结论
    绕过运行时保护
    获取实际数据（密钥、API 参数）
        ↓
代码修改 (30-60 分钟)
        ↓
    永久性修改
    无需每次都使用 Frida
```

### 静态 vs 动态分析对比

| 场景         | 静态分析         | 动态分析     | 推荐     |
| ------------ | ---------------- | ------------ | -------- |
| **绕过混淆** | 困难             | 可行         | 动态     |
| **获取密钥** | 难（可能硬编码） | 易（运行时） | 动态     |
| **修改代码** | 精确             | 不持久       | 静态     |
| **时间成本** | 高（有混淆时）   | 中等         | 结合使用 |

---

## 常见问题

### 问题 1：Apktool 解包失败

**错误信息**：`brut.androlib.AndrolibException: Could not decode arsc file`

**可能原因**：

1. APK 使用了资源混淆（AndResGuard）
2. APK 已损坏
3. Apktool 版本过旧

**解决方案**：

```bash
# 1. 更新 Apktool 到最新版本
# 下载：https://ibotpeaches.github.io/Apktool/

# 2. 使用 -r 参数跳过资源解码
apktool d target.apk -r -o target_unpacked
# -r: 不解码资源文件 (resources.arsc)

# 3. 使用 --only-main-classes 仅解码主 DEX
apktool d target.apk --only-main-classes -o target_unpacked

# 4. 如果只需要 Smali，直接使用 dex2jar + jd-gui
d2j-dex2jar target.apk
# 生成 target-dex2jar.jar，用 JD-GUI 打开
```

### 问题 2：代码混淆严重无法阅读

**解决方案**：

```bash
# 1. 优先使用动态分析
# 混淆的代码在运行时行为不变
# 使用 Frida 直接 hook，观察参数和返回值

# 2. 利用字符串常量定位
# 字符串通常不会被混淆
# 在 Jadx 中搜索关键字符串，反向定位代码

# 3. 重命名类/方法（Jadx 支持）
# 右键类名 → Rename
# 根据功能手动重命名为有意义的名称

# 4. 使用符号还原工具
# 如果有 mapping.txt（混淆映射文件）
# 可以使用工具还原符号
```

### 问题 3：Frida 无法连接应用

**可能原因**：

1. 应用未运行
2. 包名错误
3. Frida Server 未启动

**解决方案**：

```bash
# 1. 检查 Frida Server 是否运行
adb shell ps | grep frida-server
# 如果没有输出，需要启动 Frida Server

# 2. 确认应用正在运行
adb shell ps | grep com.example.app
# 或
frida-ps -U | grep example

# 3. 使用正确的包名
# 查看已安装应用的包名
adb shell pm list packages | grep example

# 4. 使用 spawn 模式（自动启动应用）
frida -U -f com.example.app -l script.js --no-pause
# -f: spawn 模式，会自动启动应用

# 5. 检查设备连接
adb devices
# 应显示：device（不是 offline 或 unauthorized）
```

### 问题 4：重打包后应用崩溃

**可能原因**：

1. Smali 语法错误
2. 修改破坏了类结构
3. 缺少依赖

**解决方案**：

```bash
# 1. 查看详细崩溃日志
adb logcat -c  # 清空日志
adb logcat | grep -E "AndroidRuntime|FATAL"

# 2. 验证 Smali 语法
# 用 Apktool 重新反编译修改后的 APK
apktool d signed.apk -o verify_unpacked
# 查看是否有错误提示

# 3. 回滚修改，逐步测试
# 先修改单个方法，通过后再修改其他

# 4. 使用 baksmali/smali 验证
baksmali d modified.apk -o smali_test
smali a smali_test -o test.dex
# 如果验证通过，说明 Smali 语法正确

# 5. 检查方法签名是否正确
# 确保修改的方法签名与接口/父类匹配
```

---

## 相关资源

### 相关 Recipe

| Recipe                                                               | 说明                   |
| -------------------------------------------------------------------- | ---------------------- |
| [Android 应用网络流量分析](../Network/network_sniffing.md)           | 详细的网络流量分析步骤 |
| [绕过应用对 Frida 的检测](../Anti-Detection/frida_anti_debugging.md) | 反调试绕过             |
| [脱壳和分析加固的 Android 应用](../Unpacking/un-packing.md)          | 处理加壳应用           |
| [Frida 常用脚本速查](../Scripts/frida_common_scripts.md)             | 现成的脚本模板         |

### 工具深入

- [Frida 使用指南](../../02-Tools/Dynamic/frida_guide.md) - 完整的 Frida 使用手册
- [Ghidra 使用指南](../../02-Tools/Static/ghidra_guide.md) - Native 代码分析
- [IDA Pro 使用指南](../../02-Tools/Static/ida_pro_guide.md) - 专业逆向工程工具

### 案例研究

- [案例：音乐应用分析](../../03-Case-Studies/case_music_apps.md) - 完整工作流程实践
- [案例：应用加密分析](../../03-Case-Studies/case_study_app_encryption.md)

### 参考资料

- [APK 文件结构详解](../../04-Reference/Foundations/apk_structure.md)
- [Smali 语法参考](../../04-Reference/Foundations/smali_syntax.md)
- [Android 组件详解](../../04-Reference/Foundations/android_components.md)

---

## 速查手册

### 工作流程快速地图

```text
解包 APK ──────── 分析 Manifest ──────── 查看目录
    │                   │                   │
    └───────────────────┼───────────────────┘
                        ↓
                  确定分析方向
                        ↓
        ┌───────────────┼───────────────┐
        ↓                               ↓
    静态分析                         动态分析
   (Jadx/IDA)                        (Frida)
        │                               │
        ├─ 定位关键代码                 │
        ├─ 理解算法逻辑                 │
        └─ 确定 hook 点 ────────────────┤
                                        │
                ┌───────────────────────┤
                ↓                       ↓
            Hook 验证               绕过保护
                │                       │
                └───────────┬───────────┘
                            ↓
                      提取关键数据
                     (密钥/算法)
                            ↓
                       修改 Smali
                            ↓
                    重打包 & 签名
                            ↓
                      测试 & 验证
```

### 常用命令速查

| 操作            | 工具       | 命令                                                             |
| --------------- | ---------- | ---------------------------------------------------------------- |
| **解包**        | Apktool    | `apktool d app.apk -o unpacked`                                  |
| **反编译**      | Jadx       | `jadx-gui app.apk`                                               |
| **Native 分析** | IDA/Ghidra | 直接打开 `.so` 文件                                              |
| **动态分析**    | Frida      | `frida -U -f <pkg> -l script.js --no-pause`                      |
| **重打包**      | Apktool    | `apktool b unpacked -o modified.apk`                             |
| **签名**        | apksigner  | `apksigner sign --ks key.keystore --out signed.apk modified.apk` |
| **安装**        | ADB        | `adb install signed.apk`                                         |

### 常用快捷操作

```bash
# 1. 一键提取 APK 脚本（保存为 get-apk.sh）
#!/bin/bash
PKG=$1
APK_PATH=$(adb shell pm path $PKG | cut -d: -f2 | tr -d '\r')
adb pull $APK_PATH ./$PKG.apk
echo "[+] 已保存: $PKG.apk"

# 使用：./get-apk.sh com.example.app

# 2. 一键解包 + 反编译
apktool d app.apk && jadx-gui app.apk &

# 3. 快速查看 Manifest
apktool d -s app.apk -o temp && cat temp/AndroidManifest.xml

# 4. 自动签名脚本（保存为 sign-apk.sh）
#!/bin/bash
APK=$1
java -jar uber-apk-signer.jar --apks $APK
echo "[+] 签名 APK 已创建"

# 5. Frida 快速 hook（交互模式）
frida -U com.example.app
# 进入后执行:
# Java.perform(function() {
#     var cls = Java.use("com.example.Class");
#     cls.method.implementation = function() { return true; };
# });
```

### 决策树

```text
拿到 APK
    │
    ├─ 有源码?
    │   └─ 有 → 直接阅读代码 → 动态验证
    │   └─ 无 → 继续
    │
    ├─ 是否加壳?
    │   └─ 是 → 先脱壳（参见脱壳 Recipe）
    │   └─ 否 → 继续
    │
    ├─ 是否混淆?
    │   └─ 重度混淆 → 优先动态分析（Frida）
    │   └─ 轻度/无 → 优先静态分析（Jadx）
    │
    ├─ Native 代码多?
    │   └─ 是 → 用 IDA/Ghidra 分析 .so
    │   └─ 否 → 专注 Java 层
    │
    └─ 有反调试?
        └─ 是 → 先绕过检测
        └─ 否 → 直接 hook
```
