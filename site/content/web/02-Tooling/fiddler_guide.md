---
title: "Fiddler Classic 指南"
date: 2025-12-25
weight: 10
---

# Fiddler Classic 指南

## 概述

Fiddler (Classic) 是一款历史悠久、功能强大的抓包工具。虽然界面稍显复古，但其核心优势在于**FiddlerScript**——允许你用 C# 代码极其灵活地控制 HTTP 请求的每一个细节。

---

## 1. 基础配置

### Tools -> Options -> HTTPS

- 勾选 "Decrypt HTTPS traffic"。
- 点击 "Actions" -> "Trust Root Certificate"。

### Tools -> Options -> Connections

- Fiddler listens on port: 8888 (默认)。
- 勾选 "Allow remote computers to connect" (如果要抓手机包)。

---

## 2. 核心功能

### Composer (构造器)

- **功能**: 手动构造 HTTP 请求。
- **用途**: 类似 Burp Repeater，但更偏向于从零构造请求。可以直接拖拽左侧的 Session 到 Composer tab 来快速填充。

### AutoResponder (自动响应器)

- **功能**: 自动匹配规则并返回预设内容。
- **用途**: 替换线上文件（类似 Charles Map Local）。
- Rule: `REGEX:(?insx).*\/script\.js`
- Action: `C:\Users\Admin\Desktop\hook.js`

---

## 3. FiddlerScript (终极杀器)

点击 Fiddler 下方的 "FiddlerScript" 标签页。这是基于 JScript.NET 的脚本环境。

### 常用 Hook 点

#### OnBeforeRequest (请求前)

```csharp
static function OnBeforeRequest(oSession: Session) {
// 拦截特定 URL
if (oSession.uriContains("/api/v1/sign")) {
// 修改请求体
var sBody = oSession.GetRequestBodyAsString();
sBody = sBody.Replace("vip=false", "vip=true");
oSession.utilSetRequestBody(sBody);

// 打印 Log 到 Fiddler Log 面板
FiddlerObject.log("Tampered body: " + sBody);
}
}
```

#### OnBeforeResponse (响应前)

```csharp
static function OnBeforeResponse(oSession: Session) {
if (oSession.HostnameIs("api.target.com")) {
oSession.utilDecodeResponse(); // 解码 gzip
var sBody = oSession.GetResponseBodyAsString();

// 替换 JSON 内容
if (sBody.Contains("\"is_admin\":false")) {
sBody = sBody.Replace("\"is_admin\":false", "\"is_admin\":true");
oSession.utilSetResponseBody(sBody);
oSession.oResponse.headers.Remove("Content-Security-Policy"); // 移除 CSP
}
}
}
```

### 为什么用 FiddlerScript？

- 比简单的正则替换更灵活（支持 if-else 逻辑）。
- 可以调用 .NET 库进行复杂的加解密操作。

---

## 4. 移动端抓包

1. **PC 配置**: 开启 "Allow remote computers to connect"，重启 Fiddler。
2. **手机配置**: 设置代理为 PC IP + 8888。
3. **安装证书**: 手机浏览器访问 `http://ipv4:8888`，点击链接下载证书。
4. **注意**: 即使在 PC 端，也可以用 "FiddlerScript" 控制手机的流量。

---

## 总结

如果你需要极其复杂的中间人逻辑（比如：请求 A 返回 -> 解析出 Token -> 自动发请求 B），FiddlerScript 是最佳选择。
