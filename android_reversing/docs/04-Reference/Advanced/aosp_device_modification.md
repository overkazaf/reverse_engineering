# 基于 AOSP 的深度改机技术指南

在 Android 安全和逆向工程领域，"改机"指的是修改设备的各种硬件和软件标识符，以绕过应用程序的安全检测或实现隐私保护。虽然使用 Xposed 或 Frida 等 Hook 框架可以在应用层实现改机，但这些方法容易被检测。**基于 AOSP (Android Open Source Project) 源码进行修改，是从系统层面伪造设备指纹的终极手段**，因为 App 获取到的信息是由系统本身"真实"地提供的。

本文旨在提供一个关于如何通过修改 AOSP 源码来实现深度改机的技术框架和思路。

---

## 目录

1. [核心思想：应用层 Hook vs. 系统层修改](#核心思想应用层-hook-vs-系统层修改)
2. [准备工作](#准备工作)
3. [关键参数定位与修改](#关键参数定位与修改)
   - [Build Info (build.prop)](#build-info-buildprop)
   - [硬件参数 (IMEI, MAC, Android ID)](#硬件参数-imei-mac-android-id)
   - [系统属性 (System Properties)](#系统属性-system-properties)
   - [内核参数 (Serial Number)](#内核参数-serial-number)
4. [编译与刷机](#编译与刷机)
5. [优势与挑战](#优势与挑战)

---

## 核心思想：应用层 Hook vs. 系统层修改

| 特性         | 应用层 Hook (Xposed/Frida)                   | AOSP 系统层修改                                              |
| :----------- | :------------------------------------------- | :----------------------------------------------------------- |
| **原理**     | 在 App 运行时，拦截 API 调用，返回伪造结果。 | 直接修改 Android 框架层源码，使 API **本身**就返回伪造的值。 |
| **效果**     | 较好，但可被检测。                           | **极好**，效果彻底。                                         |
| **检测难度** | 容易被反 Hook、反调试技术检测到。            | 极难被检测，因为对 App 来说系统行为是"原生"的。              |
| **实现难度** | 相对较低，只需编写 Hook 脚本。               | **非常高**，需要编译整个 Android 系统。                      |
| **适用性**   | 通用性强，适用于大多数设备。                 | 通常只适用于 AOSP 支持良好的设备（如 Google Pixel）。        |

**结论**: AOSP 改机的本质是**构建一个"出厂设置"就是伪装状态的自定义操作系统**。

---

## 准备工作

1. **硬件要求**:
   - 一台高性能的 PC（至少 16GB RAM，推荐 32GB 或更高）。
   - 大容量高速硬盘（SSD，至少 500GB 可用空间）。
   - 一台受 AOSP 官方支持的设备（如 Google Pixel 系列），用于刷机验证。

2. **软件环境**:
   - Linux 操作系统（推荐 Ubuntu LTS 版本）。
   - 熟悉 Android 编译环境，安装好 `repo` 和所有必需的依赖库。

3. **AOSP 源码**:
   - 根据你的目标设备和 Android 版本，初始化并同步对应的 AOSP 源码仓库。

---

## 关键参数定位与修改

### Build Info (build.prop)

这些是描述设备型号、品牌、制造商等最基础的信息。

- **定位**: 这些值通常定义在 `device/` 目录下的特定于设备的 `*.mk` makefile 文件中，或者在 `build/make/target/product/` 下的通用产品定义文件中。

- **修改示例**:
  - 打开 `device/<vendor>/<product_name>/device.mk` 或类似文件。
  - 找到并修改以下变量：

    ```makefile
    PRODUCT_MODEL := Pixel 8 Pro
    PRODUCT_BRAND := Google
    PRODUCT_NAME := my_custom_device
    PRODUCT_DEVICE := generic
    PRODUCT_MANUFACTURER := MyCompany
    ```

### 硬件参数 (IMEI, MAC, Android ID)

这些是更敏感、更核心的设备标识符。修改它们需要深入到 Framework 层的 Java 代码和 JNI。

- **IMEI (Telephony)**:
  - **定位**: `frameworks/opt/telephony/src/java/com/android/internal/telephony/Phone.java` 或相关的 `*SubInfo.java` 文件。
  - **修改思路**: 找到 `getImei()` 或类似方法，在其中硬编码或返回一个动态生成的伪造 IMEI。

- **MAC Address (Wi-Fi)**:
  - **定位**: `frameworks/base/wifi/java/android/net/wifi/WifiInfo.java`。
  - **修改思路**: 找到 `getMacAddress()` 方法。注意，在高版本 Android 中，该方法可能返回一个固定的、非真实的 MAC 地址。需要找到其更底层的实现，可能在 `wpa_supplicant` 或 Wi-Fi 驱动的 JNI 接口中。

- **Android ID**:
  - **定位**: `frameworks/base/services/core/java/com/android/server/pm/Settings.java` 中的 `getStringForUser()` 方法，结合 `android.provider.Settings.Secure.ANDROID_ID` 的实现。
  - **修改思路**: 找到生成和存储 Android ID 的逻辑，将其替换为返回一个固定的或每次启动都随机生成的值。

### 系统属性 (System Properties)

App 通过 `android.os.SystemProperties.get()` 获取各种系统属性。

- **定位**: `frameworks/base/core/java/android/os/SystemProperties.java` 及其对应的 JNI 实现 `frameworks/base/core/jni/android_os_SystemProperties.cpp`。

- **修改思路**: 直接在 `SystemProperties.cpp` 的 `native_get` 方法中进行拦截。判断传入的属性名，如果是目标属性（如 `ro.serialno`），则返回一个伪造的值，否则执行原始逻辑。

### 内核参数 (Serial Number)

一些底层信息（如 CPU 序列号）直接由 Linux 内核通过 `/proc` 文件系统暴露。

- **定位**: 内核源码中的 `arch/<arch>/kernel/setup.c` 或相关驱动文件。

- **修改思路**:
  1. 下载与 AOSP 版本匹配的内核源码。
  2. 找到向 `/proc/cpuinfo` 或 `/proc/serial` 等文件写入信息的代码。
  3. 修改这部分逻辑，使其输出伪造的信息。
  4. 重新编译内核 (`boot.img`)。

---

## 编译与刷机

1. **设置环境**: `source build/envsetup.sh`

2. **选择目标**: `lunch aosp_<device_name>-userdebug` (例如 `lunch aosp_husky-userdebug` 对应 Pixel 8 Pro)

3. **开始编译**: `make -j$(nproc)` (这会花费数小时)

4. **刷机**:
   - 将设备置于 `fastboot` 模式。
   - 执行 `fastboot flashall -w`，这将刷写所有编译生成的镜像 (`system.img`, `boot.img`, `vendor.img` 等)。

---

## 优势与挑战

### 优势

- **彻底性**: 从系统根源上改变设备指纹，几乎无法被应用层技术检测。
- **稳定性**: 不会像 Hook 框架那样因为应用更新或加固而失效。
- **性能好**: 没有额外的 Hook 开销，所有修改都是原生代码。

### 挑战

- **技术门槛极高**: 需要深入理解 AOSP 源码结构、编译系统和 Linux 内核。
- **时间成本高**: 全量编译一次 AOSP 通常需要数小时。
- **设备限制**: 强依赖于有良好 AOSP 支持和开放驱动的设备。
- **维护困难**: 每次 Android 版本更新，都需要重新进行源码适配和修改。
