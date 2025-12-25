---
title: "环境配置"
date: 2024-04-22
type: posts
tags: ["入门", "Frida", "Android", "ARM汇编", "DEX", "IDA Pro"]
weight: 10
---

# 环境配置

5 分钟完成基础逆向环境搭建。

---

## 必需工具

| 工具        | 安装命令                                                |
| ----------- | ------------------------------------------------------- |
| Python 3.8+ | 官网下载或 `brew install python3`                       |
| ADB         | `brew install android-platform-tools` 或 Android Studio |
| Frida       | `pip install frida-tools`                               |

## 设备准备

**推荐新手**：使用模拟器（Genymotion 或 Android Studio AVD）

**使用真机**：

1. 设置 → 关于手机 → 连点"版本号"7 次 → 启用开发者选项
2. 开发者选项 → 启用 USB 调试
3. 连接设备，执行 `adb devices` 确认

## 安装 Frida Server

```bash
# 1. 查看设备架构
adb shell getprop ro.product.cpu.abi
# arm64-v8a → frida-server-*-android-arm64
# x86_64    → frida-server-*-android-x86_64

# 2. 下载对应版本 (版本需与本地 frida 一致)
# https://github.com/frida/frida/releases

# 3. 部署到设备
adb push frida-server /data/local/tmp/
adb shell "chmod 755 /data/local/tmp/frida-server"
adb shell "/data/local/tmp/frida-server &"

# 4. 验证
frida-ps -U
```

## 验证清单

```bash
python3 --version    # >= 3.8
adb devices          # 显示设备
frida --version      # 显示版本
frida-ps -U          # 列出进程
```

---

**环境就绪！** → [开始 10 分钟入门](./index.md)
