# Burp Suite 指南

## 概述

Burp Suite 不仅仅是渗透测试神器，也是 Web 逆向中最強大的中间人攻击（MITM）工具。它不仅能抓包，还能修改重发、暴力破解签名、自动化解码等。本指南仅关注逆向工程中常用的功能。

---

## 1. 基础配置 (Proxy & Cert)

### 拦截 HTTPS 流量

1.  **配置代理**: 浏览器设置代理为 `127.0.0.1:8080` (Burp 默认端口)。
2.  **安装证书**: 访问 `http://burp`，下载 CA 证书。
    - **Windows/Mac**: 双击安装，务必选择“受信任的根证书颁发机构”。
    - **Android/iOS**: 安装证书后，需在系统设置中“针对根证书启用完全信任”。

### Invisible Proxy (隐形代理)

当客户端（如某些非浏览器发包的 EXE 或 Python 脚本）不支持配置代理，或者强制校验 Host 头时：

1.  修改 Hosts 文件，将 `target.com` 指向 `127.0.0.1`。
2.  Burp -> Proxy -> Options -> Edit Interface `127.0.0.1:443` -> Request handling -> Support invisible proxying (True).
3.  这样所有发往本地 443 的流量都会被 Burp 拦截并转发。

---

## 2. Repeater (重放器)

这是逆向中最常用的模块。

- **基本用法**: 在 Proxy History 中右键请求 -> "Send to Repeater" (Ctrl+R)。
- **用途**:
  - 修改参数（如 `id=1` 改 `id=2`）测试越权。
  - 删除特定的 Header（如 `Signature`）测试是否必须。
  - 测试 Token 的有效期。

---

## 3. Intruder (入侵者)

用于自动化爆破。

- **场景**:
  - 爆破短信验证码 (4 位/6 位)。
  - 遍历用户 ID 爬取数据。
  - 如果签名算法已知，可以写插件（Extender）自动计算签名进行批量请求。

---

## 4. Decoder (解码器)

内置的编码转换工具。

- 支持 URL, Base64, Hex, Gzip 等常见格式。
- **Smart Decode**: 智能尝试解码，对付多层编码（如 Base64 里面包 URL 编码）很有效。

---

## 5. Match and Replace (自动替换)

在 Proxy -> Options -> Match and Replace 中设置规则。

- **逆向场景**:
  - **Bypass CSP**: 自动删除响应头中的 `Content-Security-Policy`，允许我们在页面执行任意 JS。
  - **修改返回包**: 将 `{"is_vip": false}` 自动替换为 `{"is_vip": true}`。
  - **注入脚本**: 在 `<body>` 标签后自动插入 `<script src="http://127.0.0.1/hook.js"></script>`。

---

## 6.常用插件 (Extensions)

从 BApp Store 安装：

1.  **Logger++**: 更强大的日志查看器，支持搜索。
2.  **Turbo Intruder**: 基于 Python 的超高性能发包器。
3.  **HackBar**: 类浏览器插件的辅助工具。

---

## 总结

在 Web 逆向中，我们通常将 Burp Suite 配合浏览器 DevTools 使用：

- **DevTools** 负责分析 JS 逻辑，生成签名。
- **Burp Suite** 负责拦截请求，验证签名，重放攻击。
