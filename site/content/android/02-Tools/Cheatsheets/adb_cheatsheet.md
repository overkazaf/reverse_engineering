---
title: "常用 ADB 命令大全"
date: 2024-11-07
type: posts
tags: ["ADB", "Android调试", "逆向工程"]
weight: 10
---

# 常用 ADB 命令大全

ADB (Android Debug Bridge) 是一个功能强大的命令行工具，可让您与模拟器实例或连接的 Android 设备进行通信。它是 Android 逆向工程中最基础也是最重要的工具之一。

---

## 目录

- [设备连接与管理](#设备连接与管理)
- [应用管理](#应用管理)
- [文件传输](#文件传输)
- [Shell 命令](#shell-命令)
- [日志与调试](#日志与调试)
- [网络调试](#网络调试)
- [逆向工程常用组合](#逆向工程常用组合)
- [Root 环境命令](#root-环境命令)
- [自动化脚本](#自动化脚本)

---

## 设备连接与管理

### 基本设备操作

| 命令 | 描述 |
| --- | --- |
| `adb devices` | 列出所有连接的设备 |
| `adb devices -l` | 列出所有连接的设备及其详细信息（型号、传输方式等） |
| `adb -s <序列号> <命令>` | 向指定设备发送命令（多设备时必须指定） |
| `adb -d <命令>` | 向唯一连接的 USB 设备发送命令 |
| `adb -e <命令>` | 向唯一运行的模拟器发送命令 |
| `adb kill-server` | 终止 ADB 服务器进程 |
| `adb start-server` | 启动 ADB 服务器进程 |

### 无线调试

| 命令 | 描述 |
| --- | --- |
| `adb tcpip 5555` | 将设备 adbd 切换到 TCP 模式（端口 5555） |
| `adb connect <IP>:5555` | 通过 WiFi 连接到设备 |
| `adb disconnect <IP>:5555` | 断开指定的无线连接 |
| `adb disconnect` | 断开所有无线连接 |
| `adb pair <IP>:<端口>` | Android 11+ 无线配对（需要配对码） |

> **无线调试步骤（传统方式）**：
> 1. USB 连接设备，确认 `adb devices` 可见
> 2. 执行 `adb tcpip 5555`
> 3. 查看设备 IP：`adb shell ip addr show wlan0`
> 4. 拔掉 USB，执行 `adb connect <设备IP>:5555`

> **Android 11+ 无线调试**：
> 1. 设备开启 **开发者选项 -> 无线调试**
> 2. 点击 **使用配对码配对设备**，获取配对地址和配对码
> 3. 电脑执行 `adb pair <IP>:<配对端口>`，输入配对码
> 4. 配对成功后执行 `adb connect <IP>:<连接端口>`

### 设备重启与信息

| 命令 | 描述 |
| --- | --- |
| `adb reboot` | 正常重启设备 |
| `adb reboot bootloader` | 重启到引导加载程序 (Bootloader/Fastboot) |
| `adb reboot recovery` | 重启到恢复模式 (Recovery) |
| `adb reboot sideload` | 重启到 Sideload 模式（用于刷机） |
| `adb root` | 以 root 权限重启 adbd 服务（仅 userdebug/eng 版本） |
| `adb unroot` | 以普通权限重启 adbd 服务 |
| `adb shell getprop ro.product.model` | 获取设备型号 |
| `adb shell getprop ro.build.version.release` | 获取 Android 系统版本 |
| `adb shell getprop ro.build.version.sdk` | 获取 SDK 版本（API Level） |
| `adb shell getprop ro.product.cpu.abi` | 获取 CPU 架构 |
| `adb shell getprop ro.debuggable` | 查看系统是否为可调试版本 |
| `adb shell wm size` | 获取屏幕分辨率 |
| `adb shell wm density` | 获取屏幕像素密度 (DPI) |
| `adb shell getprop` | 列出所有系统属性 |

---

## 应用管理

### 安装与卸载

| 命令 | 描述 |
| --- | --- |
| `adb install <apk路径>` | 安装应用 |
| `adb install -r <apk路径>` | 重新安装应用（保留数据） |
| `adb install -t <apk路径>` | 允许安装测试包（test-only APK） |
| `adb install -g <apk路径>` | 安装并授予所有运行时权限 |
| `adb install -d <apk路径>` | 允许降级安装（版本号更低） |
| `adb install-multiple <apk1> <apk2>` | 安装 Split APK（多个 APK 文件） |
| `adb uninstall <包名>` | 完全卸载应用 |
| `adb uninstall -k <包名>` | 卸载应用但保留数据和缓存 |

### 包管理 (pm)

| 命令 | 描述 |
| --- | --- |
| `adb shell pm list packages` | 列出所有已安装的包名 |
| `adb shell pm list packages -f` | 列出所有包名及其 APK 路径 |
| `adb shell pm list packages -3` | 只列出第三方（用户安装的）应用 |
| `adb shell pm list packages -s` | 只列出系统应用 |
| `adb shell pm list packages <关键词>` | 按关键词过滤包名 |
| `adb shell pm path <包名>` | 获取指定应用的 APK 路径 |
| `adb shell pm dump <包名>` | 查看应用的完整信息 |
| `adb shell pm clear <包名>` | 清除应用所有数据和缓存 |
| `adb shell pm disable-user --user 0 <包名>` | 禁用应用（免 root 冻结） |
| `adb shell pm enable <包名>` | 启用被禁用的应用 |

### 权限管理

| 命令 | 描述 |
| --- | --- |
| `adb shell pm grant <包名> <权限>` | 授予指定权限 |
| `adb shell pm revoke <包名> <权限>` | 撤销指定权限 |
| `adb shell pm list permissions -g` | 列出所有权限组 |
| `adb shell dumpsys package <包名>` | 查看应用详细信息（含已授权限） |

### Activity 管理 (am)

| 命令 | 描述 |
| --- | --- |
| `adb shell am start -n <包名>/<Activity>` | 启动指定 Activity |
| `adb shell am start -D -n <包名>/<Activity>` | 以调试模式启动 Activity |
| `adb shell am start -a android.intent.action.VIEW -d <URL>` | 使用浏览器打开 URL |
| `adb shell am startservice -n <包名>/<Service>` | 启动指定 Service |
| `adb shell am broadcast -a <action>` | 发送广播 |
| `adb shell am force-stop <包名>` | 强制停止应用 |
| `adb shell am set-debug-app -w <包名>` | 设为调试模式（启动时等待调试器） |
| `adb shell am clear-debug-app` | 清除调试应用设置 |
| `adb shell dumpsys activity top` | 查看当前 Activity 栈信息 |

---

## 文件传输

### 基本操作

| 命令 | 描述 |
| --- | --- |
| `adb push <本地路径> <远程路径>` | 将文件/目录从电脑推送到设备 |
| `adb pull <远程路径> [本地路径]` | 将文件/目录从设备拉取到电脑 |
| `adb shell ls -la <路径>` | 列出文件详细信息（含权限、大小） |
| `adb shell cp <源路径> <目标路径>` | 在设备上复制文件 |
| `adb shell mv <源路径> <目标路径>` | 在设备上移动或重命名文件 |
| `adb shell rm <文件路径>` | 在设备上删除文件 |
| `adb shell mkdir -p <路径>` | 在设备上创建目录（含中间目录） |
| `adb shell chmod <权限> <路径>` | 修改文件权限 |

### 逆向工程常用文件路径

| 路径 | 说明 |
| --- | --- |
| `/data/data/<包名>/` | 应用私有数据目录 |
| `/data/data/<包名>/shared_prefs/` | SharedPreferences（XML 配置文件） |
| `/data/data/<包名>/databases/` | SQLite 数据库文件 |
| `/data/data/<包名>/cache/` | 应用缓存目录 |
| `/data/data/<包名>/files/` | 应用内部文件目录 |
| `/data/data/<包名>/lib/` | 应用 Native 库（so 文件） |
| `/data/app/<包名>*/` | APK 安装目录 |
| `/data/local/tmp/` | 临时文件目录（所有用户可写） |
| `/sdcard/` 或 `/storage/emulated/0/` | 外部存储根目录 |
| `/sdcard/Android/data/<包名>/` | 应用外部存储目录 |
| `/system/app/` | 系统预装应用目录 |
| `/system/framework/` | 系统框架 JAR 文件 |
| `/proc/<PID>/maps` | 进程内存映射 |
| `/proc/<PID>/status` | 进程状态信息 |

---

## Shell 命令

### dumpsys（系统服务信息）

| 命令 | 描述 |
| --- | --- |
| `dumpsys activity` | Activity 管理器状态 |
| `dumpsys package <包名>` | 应用详细信息（版本、权限、签名等） |
| `dumpsys meminfo <包名>` | 应用内存使用情况 |
| `dumpsys cpuinfo` | CPU 使用情况 |
| `dumpsys battery` | 电池状态信息 |
| `dumpsys wifi` | WiFi 状态信息 |
| `dumpsys window displays` | 屏幕显示信息 |
| `dumpsys netstats` | 网络流量统计 |

### settings（系统设置）

| 命令 | 描述 |
| --- | --- |
| `settings list global` | 列出所有 global 命名空间设置 |
| `settings list secure` | 列出所有 secure 命名空间设置 |
| `settings get global http_proxy` | 获取当前 HTTP 代理设置 |
| `settings put global http_proxy <IP>:<端口>` | 设置全局 HTTP 代理 |
| `settings delete global http_proxy` | 删除全局 HTTP 代理 |
| `settings get secure android_id` | 获取 Android ID |

### input（输入模拟）

| 命令 | 描述 |
| --- | --- |
| `input text '<文本>'` | 输入文本（不支持中文） |
| `input keyevent <按键码>` | 发送按键事件 |
| `input tap <x> <y>` | 模拟单击 |
| `input swipe <x1> <y1> <x2> <y2> [时长ms]` | 模拟滑动 |
| `input keyevent --longpress <按键码>` | 模拟长按 |

> **常用按键码**：
>
> | 按键码 | 说明 | 按键码 | 说明 |
> | --- | --- | --- | --- |
> | `3` | HOME | `4` | BACK |
> | `24` | 音量+ | `25` | 音量- |
> | `26` | POWER | `82` | MENU |
> | `66` | ENTER | `67` | DEL (退格) |
> | `187` | APP_SWITCH | `224` | WAKEUP |

### 截屏与录屏

| 命令 | 描述 |
| --- | --- |
| `adb shell screencap /sdcard/screenshot.png` | 截屏保存到设备 |
| `adb exec-out screencap -p > screenshot.png` | 截屏直接输出到电脑 |
| `adb shell screenrecord /sdcard/demo.mp4` | 录制屏幕视频（Ctrl+C 停止） |
| `adb shell screenrecord --time-limit 10 /sdcard/demo.mp4` | 录制 10 秒屏幕视频 |

---

## 日志与调试

### Logcat 基础

| 命令 | 描述 |
| --- | --- |
| `adb logcat` | 实时打印设备日志 |
| `adb logcat -c` | 清除旧的日志缓存 |
| `adb logcat -d` | 输出当前日志到屏幕并退出 |
| `adb logcat -b <缓冲区>` | 查看指定缓冲区（main/system/crash/events） |
| `adb logcat -b all` | 查看所有日志缓冲区 |
| `adb logcat -v threadtime` | 显示日期、时间、PID、TID |
| `adb logcat -f /sdcard/log.txt` | 将日志输出到设备上的文件 |
| `adb logcat -t 100` | 只输出最近 100 条日志 |

### Logcat 过滤

| 命令 | 描述 |
| --- | --- |
| `adb logcat *:E` | 只显示 Error 及以上级别 |
| `adb logcat *:S <标签>:<优先级>` | 按标签和优先级过滤 |
| `adb logcat -s <标签>` | 只显示指定标签的日志 |
| `adb logcat --pid=<PID>` | 只显示指定进程的日志 |

> **日志优先级**（由低到高）：`V`(Verbose) < `D`(Debug) < `I`(Info) < `W`(Warning) < `E`(Error) < `F`(Fatal) < `S`(Silent)

> **示例**：`adb logcat *:S MyApp:D` 只显示 MyApp 标签 Debug 及以上日志；`adb logcat --pid=$(adb shell pidof com.example.app)` 按进程过滤。

### 崩溃与 ANR 分析

| 命令 | 描述 |
| --- | --- |
| `adb logcat -b crash` | 查看崩溃日志缓冲区 |
| `adb logcat -b crash -d` | 输出崩溃日志并退出 |
| `adb shell cat /data/anr/traces.txt` | 查看 ANR traces（需要 root） |
| `adb pull /data/anr/` | 拉取所有 ANR trace 文件 |
| `adb bugreport <输出路径>` | 生成完整 Bug 报告 |

### 调试相关

| 命令 | 描述 |
| --- | --- |
| `adb jdwp` | 列出可调试的 Java 进程 PID |
| `adb forward tcp:<本地端口> jdwp:<PID>` | 转发 JDWP 调试端口 |
| `adb shell ps -A` | 列出所有进程 |
| `adb shell cat /proc/<PID>/maps` | 查看进程内存映射 |
| `adb shell top -n 1` | 查看 CPU/内存占用快照 |
| `adb shell strace -p <PID>` | 跟踪进程系统调用（需要 root） |

---

## 网络调试

### 端口转发

| 命令 | 描述 |
| --- | --- |
| `adb forward tcp:<PC端口> tcp:<设备端口>` | PC 端口转发到设备端口 |
| `adb forward tcp:8080 localabstract:<socket名>` | 转发到设备抽象 Unix socket |
| `adb forward --list` | 列出所有端口转发规则 |
| `adb forward --remove-all` | 移除所有转发规则 |
| `adb reverse tcp:<设备端口> tcp:<PC端口>` | 反向转发：设备端口 -> PC 端口 |
| `adb reverse --list` | 列出所有反向转发规则 |
| `adb reverse --remove-all` | 移除所有反向转发规则 |

> **正向转发 vs 反向转发**：
> - `adb forward`：PC 上访问某端口时，流量转发到设备。常用于连接设备上的调试服务。
> - `adb reverse`：设备上访问某端口时，流量转发到 PC。常用于让设备连接 PC 上的本地服务。

### 抓包代理设置（Burp Suite / Charles）

```bash
# 设置全局 HTTP 代理
adb shell settings put global http_proxy <PC_IP>:8080

# 查看当前代理设置
adb shell settings get global http_proxy

# 删除全局代理
adb shell settings delete global http_proxy

# 删除代理后重启网络使其生效
adb shell svc wifi disable && adb shell svc wifi enable
```

> **完整抓包步骤**：
> 1. PC 上启动 Burp Suite / Charles，监听 `0.0.0.0:8080`
> 2. 设置设备代理：`adb shell settings put global http_proxy <PC_IP>:8080`
> 3. 将 CA 证书推送到设备并安装（HTTPS 抓包需要）
> 4. Android 7.0+ 需额外配置 `network_security_config.xml` 或 root 安装系统级证书
> 5. 完成后清除代理：`adb shell settings delete global http_proxy`

### 网络状态

| 命令 | 描述 |
| --- | --- |
| `adb shell ip addr` | 查看 IP 地址信息 |
| `adb shell ip route` | 查看路由表 |
| `adb shell netstat -tlnp` | 查看监听的 TCP 端口 |
| `adb shell ping <地址>` | 测试网络连通性 |
| `adb shell svc wifi enable/disable` | 开启/关闭 WiFi |
| `adb shell svc data enable/disable` | 开启/关闭移动数据 |

---

## 逆向工程常用组合

### 提取 APK

```bash
# 通过 pm path 获取路径后 pull
adb shell pm path com.example.app
# 输出: package:/data/app/com.example.app-xxxx/base.apk
adb pull /data/app/com.example.app-xxxx/base.apk ./app.apk

# 一行命令提取
adb pull $(adb shell pm path com.example.app | sed 's/package://') ./app.apk
```

### 提取应用数据

```bash
# 需要 root 权限
adb pull /data/data/com.example.app/shared_prefs/ ./shared_prefs/
adb pull /data/data/com.example.app/databases/ ./databases/

# 无 root 时使用 run-as（仅限 debuggable 应用）
adb shell run-as com.example.app cat databases/app.db > app.db

# 使用 adb backup（部分应用可能禁止备份）
adb backup -f backup.ab -noapk com.example.app
```

### 设置可调试模式

```bash
adb shell am set-debug-app -w com.example.app       # 启动时等待调试器附加
adb shell su -c "resetprop ro.debuggable 1"          # 修改属性（需 root + Magisk）
adb shell su -c "stop; start"                        # 重启 zygote 使其生效
adb jdwp                                             # 列出所有可调试进程 PID
```

### 安装系统级 CA 证书（HTTPS 抓包）

```bash
# 需要 root，适用于 Android 7.0+ 抓取 HTTPS 流量
openssl x509 -inform DER -in cacert.der -out cacert.pem
HASH=$(openssl x509 -inform PEM -subject_hash_old -in cacert.pem | head -1)
cp cacert.pem ${HASH}.0

adb push ${HASH}.0 /sdcard/
adb shell su -c "mount -o rw,remount /system"
adb shell su -c "cp /sdcard/${HASH}.0 /system/etc/security/cacerts/"
adb shell su -c "chmod 644 /system/etc/security/cacerts/${HASH}.0"
adb shell su -c "mount -o ro,remount /system"
adb reboot
```

### 查看当前 Activity

```bash
adb shell dumpsys activity activities | grep mResumedActivity  # 当前前台 Activity
adb shell dumpsys activity top | head -30                      # Activity 完整信息
adb logcat -s ActivityManager:I | grep -E "START|LAUNCH"       # 实时监控启动
```

---

## Root 环境命令

### 基本 Root 操作

| 命令 | 描述 |
| --- | --- |
| `adb shell su` | 在 adb shell 中获取 root 权限 |
| `adb shell su -c '<命令>'` | 以 root 身份执行单条命令 |
| `adb shell id` | 查看当前用户 UID/GID 信息 |

### 文件系统挂载

| 命令 | 描述 |
| --- | --- |
| `mount -o rw,remount /system` | 将 /system 重新挂载为可读写 |
| `mount -o ro,remount /system` | 将 /system 恢复为只读 |
| `mount -o rw,remount /` | 挂载根目录为可读写（Android 10+） |
| `cat /proc/mounts` | 查看所有已挂载的文件系统 |

> **注意**：Android 10+ 使用动态分区和 system-as-root，`/system` 可能需要通过 Magisk overlay 方式修改。

### SELinux 命令

| 命令 | 描述 |
| --- | --- |
| `getenforce` | 查看当前 SELinux 模式 |
| `setenforce 0` | 设置为 Permissive（宽容模式） |
| `setenforce 1` | 设置为 Enforcing（强制模式） |
| `dmesg \| grep avc` | 查看 SELinux 拒绝日志 |

> **逆向工程中的 SELinux**：
> - Frida 附加进程等注入操作在 Enforcing 模式下常会失败
> - 临时关闭：`su -c "setenforce 0"` 可解决大部分 SELinux 拦截问题
> - Magisk 通常自动处理 SELinux 策略，但某些操作可能仍需手动设置

### Magisk / KernelSU 命令

| 命令 | 描述 |
| --- | --- |
| `magisk -v` | 查看 Magisk 版本 |
| `magisk --denylist ls` | 列出 DenyList 中的应用 |
| `magisk --denylist add <包名>` | 将应用添加到 DenyList |
| `magisk --denylist rm <包名>` | 将应用从 DenyList 移除 |
| `magiskpolicy --live "allow <规则>"` | 动态添加 SELinux 策略 |
| `resetprop <属性名> <值>` | 修改系统属性（包括只读属性） |
| `resetprop --delete <属性名>` | 删除系统属性 |
| `ksud --version` | 查看 KernelSU 版本 |
| `ksud module list` | 列出 KernelSU 已安装的模块 |

---

## 自动化脚本

### 批量提取第三方 APK

```bash
#!/bin/bash
mkdir -p ./extracted_apks
for pkg in $(adb shell pm list packages -3 | sed 's/package://'); do
    apk_path=$(adb shell pm path "$pkg" | sed 's/package://' | tr -d '\r')
    echo "[*] 提取: $pkg"
    adb pull "$apk_path" "./extracted_apks/${pkg}.apk" 2>/dev/null
done
```

### 清除应用数据并重启

```bash
#!/bin/bash
PKG=${1:?"用法: $0 <包名>"}
adb shell am force-stop "$PKG"
adb shell pm clear "$PKG"
LAUNCHER=$(adb shell cmd package resolve-activity --brief "$PKG" | tail -1 | tr -d '\r')
adb shell am start -n "$LAUNCHER"
```

### Frida 注入一键启动

```bash
#!/bin/bash
PKG=${1:?"用法: $0 <包名> [脚本路径]"}
SCRIPT=${2:-""}
# 启动 frida-server（如果尚未运行）
if ! adb shell "su -c 'ps -A'" | grep -q frida-server; then
    adb shell "su -c '/data/local/tmp/frida-server -D &'" && sleep 2
fi
adb shell am force-stop "$PKG"
[ -n "$SCRIPT" ] && frida -U -f "$PKG" -l "$SCRIPT" --no-pause || frida -U -f "$PKG" --no-pause
```

### 常用单行命令

```bash
# 获取当前前台应用包名
adb shell dumpsys activity activities | grep mResumedActivity | awk '{print $4}' | cut -d'/' -f1

# 快速提取当前前台应用的 APK
pkg=$(adb shell dumpsys activity activities | grep mResumedActivity | awk '{print $4}' | cut -d'/' -f1)
adb pull $(adb shell pm path $pkg | sed 's/package://') ./${pkg}.apk

# 获取应用的 UID / 签名信息 / 权限
adb shell dumpsys package com.example.app | grep userId
adb shell dumpsys package com.example.app | grep -A 1 "Signatures"
adb shell dumpsys package com.example.app | grep -A 100 "requested permissions:" | grep "android.permission"

# 查看应用是否可调试
adb shell dumpsys package com.example.app | grep "flags=" | head -1

# 获取设备 WiFi IP 地址
adb shell ip addr show wlan0 | grep "inet " | awk '{print $2}' | cut -d'/' -f1

# 列出设备上所有监听的端口
adb shell su -c "ss -tlnp"
```

---

> **提示**：本文中的 Shell 命令（如 `am`, `pm`, `dumpsys` 等）需要在 `adb shell` 环境中执行，也可以直接使用 `adb shell <命令>` 格式从电脑端调用。需要 root 权限的命令需要先执行 `su` 或使用 `su -c '<命令>'` 形式。
