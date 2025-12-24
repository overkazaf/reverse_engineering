---
title: "Wireshark 指南"
date: 2025-12-25
weight: 10
---

# Wireshark 指南

## 概述

Wireshark 是网络协议分析的“显微镜”。与 Burp/Charles 这种 HTTP 代理不同，Wireshark 捕获的是网卡层的原始数据包（TCP/IP）。

在逆向中，我们主要用它来：

1. 分析非 HTTP 的私有协议（如 WebSocket 里面的二进制流，或者 TCP 长连接）。
2. 在无法设置代理的情况下（如某些 APP 开启了 VPN 检测或不走系统代理）强制抓包。

---

## 1. 基础过滤 (Filters)

Wireshark 的过滤器语法是必须掌握的。

### 常用过滤器

- **按协议**: `http`, `tls`, `websocket`, `tcp`
- **按 IP**: `ip.addr == 1.2.3.4` (源或目的), `ip.src == 1.2.3.4`
- **按端口**: `tcp.port == 443`, `udp.port == 53`
- **按内容**: `frame contains "password"` (二进制搜索)

### 逻辑组合

`ip.addr == 1.2.3.4 && tcp.port == 8080 || http`

---

## 2. TLS 解密 (关键！)

默认情况下，Wireshark 抓到的 HTTPS 包全是乱码（TLS Encrypted Alert）。我们需要导入密钥才能解密。

### 浏览器环境 (Key Log)

Chrome 和 Firefox 支持将 TLS 会话密钥导出到文件。

1. **设置环境变量**:
    - Windows: `set SSLKEYLOGFILE=C:\keys\ssl.log`
    - Mac/Linux: `export SSLKEYLOGFILE=~/ssl.log`
2. **启动浏览器**: 在同一个终端中启动浏览器（`open -a "Google Chrome"`）。
3. **配置 Wireshark**:
    - `Preferences -> Protocols -> TLS (或 SSL)`。
    - 在 `(Pre)-Master-Secret log filename` 中选择刚才的 `ssl.log` 文件。
4. 此时，Wireshark 中的 TLS 包会自动变成解密后的 HTTP2/HTTP1.1 明文。

### 移动端环境

对于安卓 APP，很难直接导出 Key Log。通常的做法是：

- 使用 Frida 脚本 Hook OpenSSL 库的 `SSL_CTX_set_keylog_callback`，将密钥 dump 出来并通过 adb 传回 PC。
- 或者直接使用基于 Frida 的抓包工具（如 r0capture）直接保存解密后的 pcap。

---

## 3. 追踪流 (Follow Stream)

右键任意一个数据包 -> `Follow` -> `TCP Stream` (或 `TLS Stream` / `HTTP Stream`)。

- 这会把属于同一个连接的所有数据包重组成完整的对话内容，非常便于分析私有协议的握手和交互逻辑。

---

## 总结

Wireshark 的学习门槛较高，但在处理非标协议或底层网络对抗时，它是无可替代的终极工具。
