---
title: "常用 ADB 命令大全"
date: 2024-11-07
weight: 10
---

# 常用 ADB 命令大全

ADB (Android Debug Bridge) 是一个功能强大的命令行工具，可让您与模拟器实例或连接的 Android 设备进行通信。

---

## 目录

- [常用 ADB 命令大全](#常用-adb-命令大全)
  - [目录](#目录)
    - [设备管理](#设备管理)
    - [文件管理](#文件管理)
    - [应用管理](#应用管理)
    - [网络](#网络)
    - [系统与调试](#系统与调试)
    - [Logcat 日志查看](#logcat-日志查看)
    - [高级 Shell 命令](#高级-shell-命令)

---

### 设备管理

| 命令                                         | 描述                            |
| -------------------------------------------- | ------------------------------- |
| `adb devices -l`                             | 列出所有连接的设备及其详细信息  |
| `adb reboot`                                 | 重启设备                        |
| `adb reboot bootloader`                      | 重启到引导加载程序 (Bootloader) |
| `adb reboot recovery`                        | 重启到恢复模式 (Recovery)       |
| `adb root`                                   | 以 root 权限重启 adbd 服务      |
| `adb shell getprop ro.product.model`         | 获取设备型号                    |
| `adb shell getprop ro.build.version.release` | 获取 Android 系统版本           |
| `adb shell wm size`                          | 获取屏幕分辨率                  |
| `adb shell wm density`                       | 获取屏幕像素密度 (DPI)          |

---

### 文件管理

| 命令                               | 描述                             |
| ---------------------------------- | -------------------------------- |
| `adb push <本地路径> <远程路径>`   | 将文件或文件夹从电脑推送到设备   |
| `adb pull <远程路径> [本地路径]`   | 将文件或文件夹从设备拉取到电脑   |
| `adb shell ls <路径>`              | 列出设备指定路径下的文件和文件夹 |
| `adb shell cd <路径>`              | 切换设备上的当前目录             |
| `adb shell pwd`                    | 显示设备上的当前工作目录         |
| `adb shell cp <源路径> <目标路径>` | 在设备上复制文件                 |
| `adb shell mv <源路径> <目标路径>` | 在设备上移动或重命名文件         |
| `adb shell rm <文件路径>`          | 在设备上删除文件                 |
| `adb shell mkdir <路径>`           | 在设备上创建新目录               |

---

### 应用管理

| 命令                                        | 描述                                  |
| ------------------------------------------- | ------------------------------------- | --------------------- |
| `adb install <apk路径>`                     | 安装应用                              |
| `adb install -r <apk路径>`                  | 重新安装应用（保留数据）              |
| `adb install -g <apk路径>`                  | 为应用授予所有运行时权限              |
| `adb uninstall <包名>`                      | 卸载应用                              |
| `adb shell pm list packages`                | 列出所有已安装的应用包名              |
| `adb shell pm list packages -f`             | 列出所有已安装的应用包名及其 APK 路径 |
| `adb shell pm list packages -3`             | 列出所有第三方应用包名                |
| `adb shell pm path <包名>`                  | 获取指定应用的 APK 路径               |
| `adb shell am start -n <包名>/<Activity名>` | 启动一个 Activity                     |
| `adb shell am force-stop <包名>`            | 强制停止应用                          |
| `adb shell pm clear <包名>`                 | 清除应用数据和缓存                    |
| `adb shell dumpsys activity                 | grep mFocusedActivity`                | 获取当前前台 Activity |

---

### 网络

| 命令                                        | 描述                               |
| ------------------------------------------- | ---------------------------------- |
| `adb forward tcp:<PC端口> tcp:<设备端口>`   | 将电脑端口的请求转发到设备端口     |
| `adb forward --list`                        | 列出所有端口转发规则               |
| `adb forward --remove-all`                  | 移除所有端口转发规则               |
| `adb shell netstat`                         | 查看网络状态（监听的端口、连接等） |
| `adb shell ifconfig` or `adb shell ip addr` | 查看网络接口信息和 IP 地址         |

---

### 系统与调试

| 命令                                         | 描述                                                       |
| -------------------------------------------- | ---------------------------------------------------------- |
| `adb shell ps`                               | 查看设备上的进程列表                                       |
| `adb shell top`                              | 查看实时资源占用情况                                       |
| `adb shell dumpsys <服务名>`                 | Dump 指定系统服务的信息 (如 `activity`, `battery`, `wifi`) |
| `adb shell screencap /sdcard/screenshot.png` | 截屏并保存到设备                                           |
| `adb shell screenrecord /sdcard/demo.mp4`    | 录制屏幕（Ctrl+C 停止）                                    |
| `adb bugreport [路径]`                       | 生成并拉取完整的 bug 报告                                  |
| `adb jdwp`                                   | 列出设备上可供调试的 Java 进程 ID (JDWP)                   |

---

### Logcat 日志查看

| 命令                             | 描述                      |
| -------------------------------- | ------------------------- | ------------------------------- |
| `adb logcat`                     | 实时打印设备日志          |
| `adb logcat -c`                  | 清除旧的日志缓存          |
| `adb logcat -d`                  | Dump 当前日志到屏幕并退出 |
| `adb logcat -f /sdcard/log.txt`  | 将日志输出到设备上的文件  |
| `adb logcat *:S <标签>:<优先级>` | 按标签和优先级过滤日志    |
| `adb logcat                      | grep <关键词>`            | 在日志中搜索关键词 (区分大小写) |

- **日志优先级**:

- `V` — Verbose (最低)

- `D` — Debug

- `I` — Info

- `W` — Warning

- `E` — Error

- `F` — Fatal

- `S` — Silent (最高)

- **示例**: `adb logcat *:S MyApp:D` 只显示标签为 "MyApp" 且优先级为 Debug 或更高的日志。

---

### 高级 Shell 命令

| 命令                                                 | 描述                                                   |
| ---------------------------------------------------- | ------------------------------------------------------ |
| `adb shell input text '<文本>'`                      | 向当前输入框输入文本（不支持中文）                     |
| `adb shell input keyevent <按键码>`                  | 发送一个按键事件 (例如 `3`=HOME, `4`=BACK, `26`=POWER) |
| `adb shell input tap <x> <y>`                        | 模拟在屏幕指定坐标的单击事件                           |
| `adb shell input swipe <x1> <y1> <x2> <y2> [时长ms]` | 模拟滑动事件                                           |
| `adb shell settings get <命名空间> <键>`             | 获取系统设置项的值                                     |
| `adb shell settings put <命名空间> <键> <值>`        | 修改系统设置项的值                                     |
| `adb shell content query --uri <URI>`                | 查询 Content Provider 中的数据                         |
| `adb shell ime list -s`                              | 列出可用的输入法                                       |
| `adb shell ime set <输入法ID>`                       | 设置默认输入法                                         |
