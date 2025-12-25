---
title: "抓包分析 Android 应用的网络流量"
date: 2024-12-07
weight: 10
---

# 抓包分析 Android 应用的网络流量

> **📚 前置知识**
>
> 本配方涉及以下核心技术，建议先阅读相关章节：
>
> - **[ADB 速查手册](../../02-Tools/Environment/adb_cheatsheet.md)** - 设备连接与证书推送
> - **HTTP/HTTPS 协议** - 理解请求响应结构与 TLS 握手

## 问题场景

- _你遇到了什么问题？_

* 想知道某个 App 调用了哪些 API 接口
* 需要分析 API 的请求参数和响应数据
* 想查看 App 发送了哪些敏感信息（设备信息、定位等）
* 需要找到加密签名的生成逻辑
* 想重放或修改 API 请求

- _本配方教你_：配置抓包环境，拦截并分析 HTTPS 流量，绕过 SSL Pinning 限制。

- _预计用时_: 15-30 分钟（首次配置）

---

## 工具清单

### 必需工具

- _Android 设备/模拟器_（已 Root，或可安装证书）
- _抓包代理工具_（选择其一）：
  - Burp Suite（推荐，功能最强）
  - Charles（UI 友好）
  - mitmproxy（开源，可编程）
- _Frida_（用于绕过 SSL Pinning）

### 可选工具

- _Wireshark_（分析底层 TCP/UDP 流量）
- _HttpCanary_（Android 上的抓包工具，无需 PC）

---

## 前置条件

### 确认清单

```bash
# 1. Verify device connection
adb devices

# 2. Frida 可用
frida-ps -U

# 3. PC and phone on the same Wi-Fi network
# Record PC IP address（used below as YOUR_PC_IP）
# Windows: ipconfig
# macOS/Linux: ifconfig or ip addr
```

- _Android 7.0+_：需要 Root 权限安装系统证书
- _Android 6.0-_：可直接安装用户证书，无需 Root
- 或使用支持用户证书的 App（Target SDK < 24）

---

## 解决方案

### 第 1 步：配置抓包工具（5 分钟）

<details>
<summary><b>使用 Burp Suite（推荐）</b></summary>

#### 1.1 启动 Burp Suite

```bash
# Download Burp Suite Community Edition (free)
# https://portswigger.net/burp/communitydownload

# Run the command
java -jar burpsuite_community.jar
```

1. 打开 _Proxy_ → _Options_
2. 在 _Proxy Listeners_ 部分
3. 点击 _Add_，配置：

- _Bind to port_: `8888`
- _Bind to address_: `All interfaces`（或选择你的 Wi-Fi 网卡）

4. 点击 _OK_ 保存

![Burp Proxy配置](../../images/burp_proxy_config.png)

_验证_：浏览器访问 `http://YOUR_PC_IP:8888`，应该看到 Burp 的错误页面（表示代理工作正常）

</details>

<details>
<summary><b>使用 Charles</b></summary>

#### 1.1 启动 Charles

下载：https://www.charlesproxy.com/download/

#### 1.2 配置代理

1. _Proxy_ → _Proxy Settings_
2. 设置 Port 为 `8888`
3. 勾选 _Enable transparent HTTP proxying_

</details>

<details>
<summary><b>使用 mitmproxy</b></summary>

```bash
# Install
pip install mitmproxy

# startup（监听 8888 端口）
mitmproxy -p 8888 --listen-host 0.0.0.0

# 或使用 Web 界面
mitmweb -p 8888 --listen-host 0.0.0.0
# 访问 http://127.0.0.1:8081 查看流量
```

</details>

---

### 第 2 步：配置手机代理（2 分钟）

#### 2.1 连接到同一 Wi-Fi

确保手机和 PC 在*同一局域网*。

#### 2.2 设置手动代理

1. 打开手机 _设置_ → _Wi-Fi_
2. *长按*当前连接的 Wi-Fi → _修改网络_
3. 展开 _高级选项_
4. 代理设置改为 _手动_：
   - _代理服务器主机名_: `YOUR_PC_IP`（如 `192.168.1.100`）
   - _代理服务器端口_: `8888`
5. 保存

#### 2.3 验证代理连接

```bash
# 手机浏览器访问任意 HTTP 网站（如 http://example.com）
# 此时 Burp/Charles 应该显示拦截到的请求
```

### 第 3 步：安装 HTTPS 证书（5-10 分钟）

_为什么需要？_ HTTPS 流量经过加密，需要安装证书才能解密查看。

<details>
<summary><b>Burp Suite 证书安装</b></summary>

#### 3.1 下载证书

1. 手机浏览器访问 `http://burp`
2. 点击 _CA Certificate_ 下载 `cacert.der`

#### 3.2 安装证书

- _Android 7.0+ （需要 Root）_：

```bash
# 1. 转换证书格式
openssl x509 -inform DER -in cacert.der -out cacert.pem

# 2. 计算证书哈希
HASH=$(openssl x509 -inform PEM -subject_hash_old -in cacert.pem | head -1)

# 3. 重命名并推送到系统目录
cp cacert.pem $HASH.0
adb root
adb remount
adb push $HASH.0 /system/etc/security/cacerts/
adb shell chmod 644 /system/etc/security/cacerts/$HASH.0

# 4. 重启设备
adb reboot
```

</details>

<details>
<summary><b>Charles 证书安装</b></summary>

1. 手机浏览器访问 `http://chls.pro/ssl`
2. 下载并安装证书
3. Android 7.0+ 同样需要安装到系统目录（参考 Burp 步骤）

</details>

<details>
<summary><b>mitmproxy 证书安装</b></summary>

1. 手机浏览器访问 `http://mitm.it`
2. 点击 Android 图标下载证书
3. 安装步骤同上

</details>

---

### 第 4 步：开始抓包（1 分钟）

#### 4.1 清空旧记录

- _Burp_: Proxy → HTTP history → 右键 → _Clear history_
- _Charles_: Proxy → _Clear Session_

#### 4.2 启动目标 App

在手机上打开要分析的应用，正常使用。

#### 4.3 查看流量

在抓包工具中：

- 查看 HTTP history / Sequence
- 筛选目标 App 的域名
- 分析 Request/Response 内容

_示例分析点_：

- 请求 URL 和参数
- Request Headers（`User-Agent`, `Authorization`, 自定义签名头）
- Request Body（POST 数据）
- Response Body（API 返回的 JSON/XML）

---

### 第 5 步：绕过 SSL Pinning（如遇到）

_症状_：

- 证书已安装，但 HTTPS 请求仍无法抓取
- App 显示"网络错误"或直接闪退
- 抓包工具显示 SSL 握手失败

_原因_：App 启用了 SSL Pinning（证书锁定），拒绝信任系统证书。

#### 方法 1: 使用 Frida 通用脚本（推荐）

_下载脚本_ `bypass_ssl_pinning.js`：

```javascript
// Universal android SSL Pinning Bypass
Java.perform(function () {
  console.log(" [SSL Pinning Bypass] 已启动");

  // 拦截 TrustManagerImpl (常用)
  try {
    var TrustManagerImpl = Java.use(
      "com.android.org.conscrypt.TrustManagerImpl"
    );
    TrustManagerImpl.verifyChain.implementation = function (
      untrustedChain,
      trustAnchorChain,
      host,
      clientAuth,
      ocspData,
      tlsSctData
    ) {
      console.log("✓ [TrustManagerImpl] BypassCertValidate: " + host);
      return untrustedChain;
    };
  } catch (e) {
    console.log("! TrustManagerImpl 不存在");
  }

  // Hook OkHttp3
  try {
    var CertificatePinner = Java.use("okhttp3.CertificatePinner");
    CertificatePinner.check.overload(
      "java.lang.String",
      "java.util.List"
    ).implementation = function (hostname, peerCertificates) {
      console.log("✓ [OkHttp3] Bypass SSL Pinning: " + hostname);
      return;
    };
  } catch (e) {
    console.log("! OkHttp3 不存在");
  }

  // Hook SSLContext
  try {
    var SSLContext = Java.use("javax.net.ssl.SSLContext");
    SSLContext.init.overload(
      "[Ljavax.net.ssl.KeyManager;",
      "[Ljavax.net.ssl.TrustManager;",
      "java.security.SecureRandom"
    ).implementation = function (keyManager, trustManager, secureRandom) {
      console.log("✓ [SSLContext] 使用自定义 TrustManager");
      this.init(keyManager, null, secureRandom);
    };
  } catch (e) {
    console.log("! SSLContext hook 失败");
  }

  console.log(" [SSL Pinning Bypass] 配置完成\n");
});
```

```bash
# 方式1：附加到运行中的 App
frida -U com.example.app -l bypass_ssl_pinning.js

# 方式2：启动 App 并注入
frida -U -f com.example.app -l bypass_ssl_pinning.js --no-pause
```

```
[SSL Pinning Bypass] 配置完成
```

#### 方法 2: 使用 Xposed 模块

<details>
<summary><b>JustTrustMe 安装步骤</b></summary>

1. 确保设备已安装 Xposed Framework
2. 下载 JustTrustMe 模块：https://github.com/Fuzion24/JustTrustMe
3. 在 Xposed Installer 中激活
4. 重启设备

</details>

#### 方法 3: 修改 APK（重打包）

<details>
<summary><b>APK 重打包步骤</b></summary>

如果 Frida 被检测，可以修改 APK 来信任用户证书：

1. 反编译 APK
2. 修改 `AndroidManifest.xml`，添加：
    ```xml
    <application android:networkSecurityConfig="@xml/network_security_config">
    ```
3. 创建 `res/xml/network_security_config.xml`：
    ```xml
    <network-security-config>
        <base-config cleartextTrafficPermitted="true">
            <trust-anchors>
                <certificates src="system" />
                <certificates src="user" />
            </trust-anchors>
        </base-config>
    </network-security-config>
    ```
4. 重新打包并签名 APK

</details>

---

## 工作原理

### MITM（中间人攻击）流程

```
1. App 发起 HTTPS 请求
2. 代理解密请求（使用安装的证书）
3. 代理重新加密并转发到真实服务器
4. 服务器响应经过代理返回给 App
```

### SSL Pinning 是什么？

App 内置了服务器证书的指纹（Hash），只信任特定证书：

```java
CertificatePinner pinner = new CertificatePinner.Builder()
    .add("api.example.com", "sha256/AAAAAAAAAA...")
    .build();
```

---

## 常见问题

### 问题 1: 手机无法连接代理

_症状_：浏览器显示"无法连接到代理服务器"

_检查_：

1. PC 和手机是否在同一 Wi-Fi？
2. PC 防火墙是否允许 8888 端口？

```bash
# Windows 防火墙规则（以管理员身份运行）
netsh advfirewall firewall add rule name="Burp Proxy" dir=in action=allow protocol=TCP localport=8888

# macOS
# 系统偏好设置 → 安全性与隐私 → 防火墙选项 → 允许 Java
```

```bash
# 检查端口
netstat -an | grep 8888 # macOS/Linux
netstat -an | findstr 8888 # Windows
```

### 问题 2: 证书无效

_症状_：浏览器显示证书无效

_Android 7.0+ 限制_：

- 默认只信任系统证书
- 必须将证书安装到 `/system/etc/security/cacerts/`（需要 Root）

_无 Root 设备的解决方案_：

- 使用 Magisk + MagiskTrustUserCerts 模块
- 或修改 APK（参考方法 3）

### 问题 3: Frida 脚本不生效

_可能原因_：

1. _App 使用了自定义网络库_
   → 需要定位具体的类名和方法，定制 Hook 脚本

2. _Frida 被检测_
   → 使用重命名的 frida-server：

```bash
adb push frida-server /data/local/tmp/random_name
adb shell "/data/local/tmp/random_name &"
```

### 问题 4: 抓不到某些请求

_可能原因_：

1. _使用了 HTTP/2 或 QUIC_
   → Burp Suite → Proxy → Options → HTTP/2 → 勾选"Enable HTTP/2"

2. _直接使用 Socket 通信_
   → 需要使用 Wireshark 或 tcpdump 抓取原始 TCP 包

3. _加密的自定义协议_
   → 需要逆向分析加密算法并解密

---

## 延伸阅读

### 相关配方

- _[密码学分析](./crypto_analysis.md)_ - 分析 API 签名和加密算法
- _[Frida 反调试绕过](../Anti-Detection/frida_anti_debugging.md)_ - 如果 App 检测到 Frida
- _[TLS 指纹分析](./tls_fingerprinting_guide.md)_ - 理解 TLS 指纹技术

### 工具深入

- _[Frida 完整指南](../../02-Tools/Dynamic/frida_guide.md)_
- _[Burp Suite 使用技巧]_ - TODO，一个比较流氓的工具

### 案例分析

- _[音乐 App 分析](../../03-Case-Studies/case_music_apps.md)_ - API 抓包实战
- _[社交媒体风控](../../03-Case-Studies/case_social_media_and_anti_bot.md)_ - 复杂签名分析

---

## 快速参考

### 一键启动脚本

- _macOS/Linux_:

```bash
#!/bin/bash
# start_proxy.sh

# 获取本机 IP
IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -1)

echo "代理地址: $IP:8888"
echo "配置手机代理到: $IP:8888"
echo "证书下载: http://burp (Burp) 或 http://mitm.it (mitmproxy)"
echo ""

# 启动 mitmproxy
mitmweb -p 8888 --listen-host 0.0.0.0
```

- _Windows_:

```batch
@echo off
REM start_proxy.bat

for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do set IP=%%a
echo 代理地址: %IP%:8888
echo 配置手机代理到: %IP%:8888
pause

java -jar burpsuite_community.jar
```

### 快速 SSL Pinning 绕过

```bash
# 下载通用 SSL Pinning 绕过脚本
curl -O https://codeshare.frida.re/@pcipolloni/universal-android-ssl-pinning-bypass-with-frida/

# 运行
frida -U -f com.target.app -l universal-ssl-pinning.js --no-pause
```
