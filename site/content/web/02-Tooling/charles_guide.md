---
title: "Charles Proxy 指南"
date: 2025-12-25
weight: 10
---

# Charles Proxy 指南

## 概述

Charles 是 Mac/Windows 上最流行的抓包工具之一，以其界面简洁、功能实用著称。在移动端（Android/iOS）逆向中，Charles 往往是首选的抓包工具。

---

## 1. 基础配置

### 抓取 HTTPS

1. **PC 端安装证书**: `Help -> SSL Proxying -> Install Charles Root Certificate`。
2. **移动端安装证书**:
    - `Help -> SSL Proxying -> Install Charles Root Certificate on a Mobile Device or Remote Browser`。
    - 手机设置代理到 Charles，浏览器访问 `chls.pro/ssl` 下载安装。
    - **注意**: Android 7.0+ 默认不信任用户安装的证书，需要将证书安装到系统分区（需 Root），或使用 VirtualXposed / Frida Hook 绕过。
3. **开启 SSL 代理**: `Proxy -> SSL Proxying Settings`，添加 `*:443`。

---

## 2. 核心功能

### Map Local (本地映射)

这是**替换线上文件**最常用的功能。

- **场景**: 你反编译了一个 JS 文件，去除了反调试代码，保存为 `hook.js`。即使没有 Root 权限，你也可以让 APP 加载这个本地文件而不是线上的原始文件。
- **操作**: 右键请求 -> `Map Local` -> Choose ... (选择你的 `hook.js`)。

### Map Remote (远程映射)

- **场景**: 将 APP 的请求重定向到你自己的服务器。
- **操作**: 右键请求 -> `Map Remote` -> 填写新的 Host/Port。

### Rewrite (重写)

比 Map 功能更细粒度，类似于 Burp 的 "Match and Replace"。

- **操作**: `Tools -> Rewrite`。
- **功能**:
- **Add Header**: 添加 `Cookie` 或 `Token`。
- **Modify Body**: 正则替换响应体内容。
- **Modify Status**: 比如把服务器的 `403` 强行改成 `200`。

### Breakpoints (断点)

- **操作**: 右键请求 -> `Breakpoints`。
- **功能**: 请求发出前断下（修改参数），响应返回前断下（修改数据）。
- _注意_: Charles 的断点会阻塞整个连接，可能会导致超时。对于复杂的逻辑修改，建议用 Rewrite 或 Map Local。

---

## 3. 移动端抓包技巧

### 抓取非 HTTP 协议 (Socks Proxy)

如果 APP 使用了自定义的 TCP 协议，Charles 的 HTTP 代理可能抓不到。

- Charles 支持 Socks 代理模式。
- 或者结合 **Postern / Drony** (Android VPN APP) 将所有流量强制转发到 Charles。

### 解决乱码问题

如果是 Protobuf 数据，Charles 默认显示乱码。

- 可以安装 "Charles Protobuf Viewer" 插件。
- 或者导出 raw data，使用 `protoc --decode_raw` 查看。

---

## 总结

Charles 是移动端逆向的轻量级利器。

- **Map Local**: 替换代码，Bypass 验证。
- **Rewrite**: 修改协议字段。
- **SSL Proxying**: 解密 HTTPS。
