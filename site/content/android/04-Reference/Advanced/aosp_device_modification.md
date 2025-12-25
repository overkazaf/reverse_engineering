---
title: "基于 AOSP 的深度改机技术指南"
date: 2025-04-30
tags: ["Native层", "浏览器指纹", "签名验证", "Frida", "DEX", "高级"]
weight: 10
---

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

## 详细代码样例

### 样例 1：修改 Build.java 返回伪造设备信息

**文件路径**: `frameworks/base/core/java/android/os/Build.java`

这是 App 获取设备基本信息的核心类，修改它可以伪造设备型号、品牌、指纹等。

```java
// frameworks/base/core/java/android/os/Build.java

package android.os;

import android.annotation.SystemApi;

public class Build {
    // ============================================
    // 原始代码通过 SystemProperties 获取值
    // 我们在这里硬编码或从配置文件读取伪造值
    // ============================================

    // 方案一：直接硬编码（简单但不灵活）
    public static final String DEVICE = "husky";  // Pixel 8 Pro 代号
    public static final String MODEL = "Pixel 8 Pro";
    public static final String BRAND = "google";
    public static final String MANUFACTURER = "Google";
    public static final String PRODUCT = "husky";
    public static final String HARDWARE = "tensor";

    // 指纹信息（非常重要，很多检测依赖这个）
    public static final String FINGERPRINT =
        "google/husky/husky:14/UD1A.231105.004/11010374:user/release-keys";

    // 方案二：从配置文件动态读取（推荐）
    private static final String CONFIG_PATH = "/data/system/device_spoof.conf";

    private static String getConfigValue(String key, String defaultValue) {
        try {
            java.io.File configFile = new java.io.File(CONFIG_PATH);
            if (configFile.exists()) {
                java.io.BufferedReader reader = new java.io.BufferedReader(
                    new java.io.FileReader(configFile));
                String line;
                while ((line = reader.readLine()) != null) {
                    if (line.startsWith(key + "=")) {
                        reader.close();
                        return line.substring(key.length() + 1);
                    }
                }
                reader.close();
            }
        } catch (Exception e) {
            // 读取失败时返回默认值
        }
        return defaultValue;
    }

    // 使用配置化方案的示例
    public static final String SERIAL = getConfigValue("ro.serialno", "UNKNOWN");

    // ============================================
    // 修改 VERSION 内部类
    // ============================================
    public static class VERSION {
        public static final String RELEASE = "14";
        public static final String RELEASE_OR_CODENAME = "14";
        public static final int SDK_INT = 34;  // Android 14
        public static final String SECURITY_PATCH = "2024-01-05";

        // 编译时间戳
        public static final long TIME = 1704067200000L; // 2024-01-01
    }
}
```

### 样例 2：修改 SystemProperties.cpp 拦截属性读取

**文件路径**: `frameworks/base/core/jni/android_os_SystemProperties.cpp`

这是拦截所有系统属性读取的核心位置，可以在这里对特定属性返回伪造值。

```cpp
// frameworks/base/core/jni/android_os_SystemProperties.cpp

#include <string>
#include <map>
#include <fstream>
#include <android-base/properties.h>
#include "jni.h"
#include "core_jni_helpers.h"

namespace android {

// 伪造属性映射表
static std::map<std::string, std::string> sSpoofedProperties;
static bool sPropertiesLoaded = false;

// 从配置文件加载伪造属性
static void loadSpoofedProperties() {
    if (sPropertiesLoaded) return;

    std::ifstream configFile("/data/system/prop_spoof.conf");
    if (configFile.is_open()) {
        std::string line;
        while (std::getline(configFile, line)) {
            // 跳过注释和空行
            if (line.empty() || line[0] == '#') continue;

            size_t pos = line.find('=');
            if (pos != std::string::npos) {
                std::string key = line.substr(0, pos);
                std::string value = line.substr(pos + 1);
                sSpoofedProperties[key] = value;
            }
        }
        configFile.close();
    }
    sPropertiesLoaded = true;
}

// 检查是否需要伪造该属性
static bool shouldSpoof(const char* key, std::string& spoofedValue) {
    loadSpoofedProperties();

    auto it = sSpoofedProperties.find(key);
    if (it != sSpoofedProperties.end()) {
        spoofedValue = it->second;
        return true;
    }

    // 硬编码的敏感属性列表（备用方案）
    static const std::map<std::string, std::string> hardcodedSpoof = {
        {"ro.serialno", "RANDOMSERIAL123"},
        {"ro.product.model", "Pixel 8 Pro"},
        {"ro.product.brand", "google"},
        {"ro.product.manufacturer", "Google"},
        {"ro.product.device", "husky"},
        {"ro.build.fingerprint", "google/husky/husky:14/UD1A.231105.004/11010374:user/release-keys"},
        {"ro.build.description", "husky-user 14 UD1A.231105.004 11010374 release-keys"},
        {"ro.boot.serialno", "RANDOMSERIAL123"},
        {"persist.sys.timezone", "America/New_York"},
        {"gsm.version.baseband", "g5300q-231020-231020-B-11108285"},
    };

    auto hardIt = hardcodedSpoof.find(key);
    if (hardIt != hardcodedSpoof.end()) {
        spoofedValue = hardIt->second;
        return true;
    }

    return false;
}

// 修改后的 native_get 函数
static jstring SystemProperties_getSS(JNIEnv* env, jclass clazz, jstring keyJ,
                                       jstring defJ) {
    const char* key = env->GetStringUTFChars(keyJ, nullptr);
    std::string spoofedValue;

    // 检查是否需要伪造
    if (shouldSpoof(key, spoofedValue)) {
        env->ReleaseStringUTFChars(keyJ, key);
        return env->NewStringUTF(spoofedValue.c_str());
    }

    // 原始逻辑：从真实属性中获取
    std::string value = android::base::GetProperty(key, "");
    env->ReleaseStringUTFChars(keyJ, key);

    if (value.empty() && defJ != nullptr) {
        return defJ;
    }
    return env->NewStringUTF(value.c_str());
}

} // namespace android
```

### 样例 3：修改 TelephonyManager 返回伪造 IMEI

**文件路径**: `frameworks/base/telephony/java/android/telephony/TelephonyManager.java`

```java
// frameworks/base/telephony/java/android/telephony/TelephonyManager.java

package android.telephony;

import android.content.Context;
import android.os.SystemProperties;
import java.security.MessageDigest;
import java.util.Random;

public class TelephonyManager {
    private Context mContext;

    // ============================================
    // IMEI 伪造相关
    // ============================================

    // 生成符合 Luhn 校验的有效 IMEI
    private static String generateValidImei(String baseImei) {
        if (baseImei.length() != 14) {
            baseImei = "86123456789012"; // 默认基础 IMEI
        }

        // 计算 Luhn 校验位
        int sum = 0;
        for (int i = 0; i < 14; i++) {
            int digit = baseImei.charAt(i) - '0';
            if (i % 2 == 1) {
                digit *= 2;
                if (digit > 9) digit -= 9;
            }
            sum += digit;
        }
        int checkDigit = (10 - (sum % 10)) % 10;

        return baseImei + checkDigit;
    }

    // 基于设备特征生成稳定的伪造 IMEI
    private String getSpoofedImei(int slotIndex) {
        try {
            // 从配置文件读取
            String configImei = readConfigValue("imei_slot_" + slotIndex);
            if (configImei != null && configImei.length() == 15) {
                return configImei;
            }

            // 基于某个种子生成稳定的 IMEI
            String seed = SystemProperties.get("ro.spoof.seed", "default_seed");
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            md.update((seed + "_imei_" + slotIndex).getBytes());
            byte[] hash = md.digest();

            StringBuilder sb = new StringBuilder();
            sb.append("86"); // TAC 前缀 (中国)
            for (int i = 0; i < 12; i++) {
                sb.append(Math.abs(hash[i]) % 10);
            }

            return generateValidImei(sb.toString());

        } catch (Exception e) {
            return "861234567890123"; // 降级到默认值
        }
    }

    // 修改后的 getImei 方法
    public String getImei(int slotIndex) {
        // 检查是否启用伪造
        if (isSpoofEnabled()) {
            return getSpoofedImei(slotIndex);
        }

        // 原始实现
        return getImeiInternal(slotIndex);
    }

    @Deprecated
    public String getDeviceId(int slotIndex) {
        return getImei(slotIndex);
    }

    // ============================================
    // MEID 伪造 (CDMA 设备)
    // ============================================

    private String getSpoofedMeid() {
        String seed = SystemProperties.get("ro.spoof.seed", "default_seed");
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            md.update((seed + "_meid").getBytes());
            byte[] hash = md.digest();

            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < 14; i++) {
                int val = Math.abs(hash[i]) % 16;
                sb.append(Integer.toHexString(val).toUpperCase());
            }
            return sb.toString();
        } catch (Exception e) {
            return "A0000012345678";
        }
    }

    public String getMeid(int slotIndex) {
        if (isSpoofEnabled()) {
            return getSpoofedMeid();
        }
        return getMeidInternal(slotIndex);
    }

    // ============================================
    // 订阅者 ID (IMSI) 伪造
    // ============================================

    public String getSubscriberId(int subId) {
        if (isSpoofEnabled()) {
            // IMSI 格式: MCC (3位) + MNC (2-3位) + MSIN (9-10位)
            String seed = SystemProperties.get("ro.spoof.seed", "default_seed");
            try {
                MessageDigest md = MessageDigest.getInstance("SHA-256");
                md.update((seed + "_imsi_" + subId).getBytes());
                byte[] hash = md.digest();

                StringBuilder sb = new StringBuilder();
                sb.append("460"); // MCC (中国)
                sb.append("00");  // MNC (中国移动)
                for (int i = 0; i < 10; i++) {
                    sb.append(Math.abs(hash[i]) % 10);
                }
                return sb.toString();
            } catch (Exception e) {
                return "460001234567890";
            }
        }
        return getSubscriberIdInternal(subId);
    }

    // ============================================
    // 工具方法
    // ============================================

    private boolean isSpoofEnabled() {
        return "true".equals(SystemProperties.get("persist.spoof.enabled", "false"));
    }

    private String readConfigValue(String key) {
        // 实现配置文件读取逻辑
        return null;
    }

    // 原始内部实现（保留以供调用）
    private native String getImeiInternal(int slotIndex);
    private native String getMeidInternal(int slotIndex);
    private native String getSubscriberIdInternal(int subId);
}
```

### 样例 4：修改 WifiInfo 返回伪造 MAC 地址

**文件路径**: `frameworks/base/wifi/java/android/net/wifi/WifiInfo.java`

```java
// frameworks/base/wifi/java/android/net/wifi/WifiInfo.java

package android.net.wifi;

import android.os.Parcel;
import android.os.Parcelable;
import android.os.SystemProperties;
import java.security.MessageDigest;

public class WifiInfo implements Parcelable {
    private String mMacAddress;
    private String mBSSID;

    // ============================================
    // MAC 地址伪造
    // ============================================

    // 生成格式正确的随机 MAC 地址
    private static String generateSpoofedMac(String seed) {
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            md.update(seed.getBytes());
            byte[] hash = md.digest();

            // 确保是本地管理的单播地址
            // 第一个字节：xxxxxx10 (本地管理, 单播)
            hash[0] = (byte) ((hash[0] & 0xFC) | 0x02);

            return String.format("%02x:%02x:%02x:%02x:%02x:%02x",
                hash[0] & 0xFF, hash[1] & 0xFF, hash[2] & 0xFF,
                hash[3] & 0xFF, hash[4] & 0xFF, hash[5] & 0xFF);

        } catch (Exception e) {
            return "02:00:00:00:00:00";
        }
    }

    // 根据 SSID 生成稳定的伪造 MAC（可选：每个网络不同 MAC）
    private String getPerNetworkMac(String ssid) {
        String seed = SystemProperties.get("ro.spoof.seed", "default") + "_wifi_" + ssid;
        return generateSpoofedMac(seed);
    }

    public String getMacAddress() {
        // 检查是否启用伪造
        if (isSpoofEnabled()) {
            String spoofMode = SystemProperties.get("persist.spoof.wifi.mode", "fixed");

            switch (spoofMode) {
                case "random":
                    // 每次请求生成随机 MAC
                    return generateSpoofedMac(String.valueOf(System.nanoTime()));

                case "per_network":
                    // 每个网络使用不同但稳定的 MAC
                    return getPerNetworkMac(getSSID());

                case "fixed":
                default:
                    // 使用固定的伪造 MAC
                    String configMac = SystemProperties.get("persist.spoof.wifi.mac", "");
                    if (!configMac.isEmpty()) {
                        return configMac;
                    }
                    String seed = SystemProperties.get("ro.spoof.seed", "default") + "_wifi";
                    return generateSpoofedMac(seed);
            }
        }

        // 原始逻辑
        return mMacAddress;
    }

    // ============================================
    // BSSID 伪造（可选）
    // ============================================

    public String getBSSID() {
        if (isSpoofEnabled() &&
            "true".equals(SystemProperties.get("persist.spoof.wifi.bssid", "false"))) {
            // 伪造 BSSID（AP 的 MAC 地址）
            String seed = SystemProperties.get("ro.spoof.seed", "default") + "_bssid_" + mBSSID;
            return generateSpoofedMac(seed);
        }
        return mBSSID;
    }

    private boolean isSpoofEnabled() {
        return "true".equals(SystemProperties.get("persist.spoof.enabled", "false"));
    }
}
```

### 样例 5：修改 Settings.Secure 返回伪造 Android ID

**文件路径**: `frameworks/base/core/java/android/provider/Settings.java`

```java
// frameworks/base/core/java/android/provider/Settings.java

package android.provider;

import android.content.ContentResolver;
import android.os.SystemProperties;
import java.security.MessageDigest;

public final class Settings {

    public static final class Secure extends NameValueTable {
        public static final String ANDROID_ID = "android_id";

        // ============================================
        // Android ID 伪造
        // ============================================

        private static String sSpoofedAndroidId = null;

        private static synchronized String getSpoofedAndroidId() {
            if (sSpoofedAndroidId != null) {
                return sSpoofedAndroidId;
            }

            // 从配置读取
            String configId = SystemProperties.get("persist.spoof.android_id", "");
            if (!configId.isEmpty() && configId.length() == 16) {
                sSpoofedAndroidId = configId;
                return sSpoofedAndroidId;
            }

            // 基于种子生成稳定的 Android ID
            String seed = SystemProperties.get("ro.spoof.seed", "default_seed");
            try {
                MessageDigest md = MessageDigest.getInstance("SHA-256");
                md.update((seed + "_android_id").getBytes());
                byte[] hash = md.digest();

                StringBuilder sb = new StringBuilder();
                for (int i = 0; i < 8; i++) {
                    sb.append(String.format("%02x", hash[i] & 0xFF));
                }
                sSpoofedAndroidId = sb.toString();

            } catch (Exception e) {
                sSpoofedAndroidId = "0123456789abcdef";
            }

            return sSpoofedAndroidId;
        }

        public static String getString(ContentResolver resolver, String name) {
            // 拦截 Android ID 请求
            if (ANDROID_ID.equals(name) && isSpoofEnabled()) {
                return getSpoofedAndroidId();
            }

            // 其他可能需要拦截的值
            if ("bluetooth_address".equals(name) && isSpoofEnabled()) {
                return getSpoofedBluetoothAddress();
            }

            // 原始实现
            return getStringInternal(resolver, name);
        }

        // ============================================
        // 蓝牙地址伪造
        // ============================================

        private static String getSpoofedBluetoothAddress() {
            String seed = SystemProperties.get("ro.spoof.seed", "default") + "_bt";
            try {
                MessageDigest md = MessageDigest.getInstance("SHA-256");
                md.update(seed.getBytes());
                byte[] hash = md.digest();

                return String.format("%02X:%02X:%02X:%02X:%02X:%02X",
                    hash[0] & 0xFF, hash[1] & 0xFF, hash[2] & 0xFF,
                    hash[3] & 0xFF, hash[4] & 0xFF, hash[5] & 0xFF);

            } catch (Exception e) {
                return "00:00:00:00:00:00";
            }
        }

        private static boolean isSpoofEnabled() {
            return "true".equals(SystemProperties.get("persist.spoof.enabled", "false"));
        }

        private static native String getStringInternal(ContentResolver resolver, String name);
    }
}
```

### 样例 6：修改内核层序列号 (/proc/cpuinfo)

**文件路径**: `kernel/arch/arm64/kernel/cpuinfo.c` (ARM64) 或 `kernel/arch/arm/kernel/setup.c` (ARM32)

```c
// kernel/arch/arm64/kernel/cpuinfo.c

#include <linux/kernel.h>
#include <linux/seq_file.h>
#include <linux/random.h>
#include <linux/string.h>

// 伪造的序列号（可以编译时指定）
static char spoofed_serial[32] = "SPOOFED_SERIAL_123";
static int serial_initialized = 0;

// 生成随机序列号（可选）
static void generate_random_serial(void) {
    if (serial_initialized) return;

    // 检查是否需要生成随机序列号
    // 可以通过内核参数 androidboot.spoof_serial=random 控制
    char* spoof_param = strstr(saved_command_line, "androidboot.spoof_serial=");
    if (spoof_param) {
        char mode[16] = {0};
        sscanf(spoof_param, "androidboot.spoof_serial=%15s", mode);

        if (strcmp(mode, "random") == 0) {
            unsigned char random_bytes[8];
            get_random_bytes(random_bytes, sizeof(random_bytes));
            snprintf(spoofed_serial, sizeof(spoofed_serial),
                     "%02X%02X%02X%02X%02X%02X%02X%02X",
                     random_bytes[0], random_bytes[1], random_bytes[2], random_bytes[3],
                     random_bytes[4], random_bytes[5], random_bytes[6], random_bytes[7]);
        } else if (strcmp(mode, "none") != 0) {
            // 使用指定的序列号
            strncpy(spoofed_serial, mode, sizeof(spoofed_serial) - 1);
        }
    }

    serial_initialized = 1;
}

// 修改 /proc/cpuinfo 的输出
static int c_show(struct seq_file *m, void *v) {
    int i;

    // ... 原有的 CPU 信息输出代码 ...

    // 在末尾添加序列号
    generate_random_serial();

    // 原始代码可能是：
    // seq_printf(m, "Serial\t\t: %016llx\n", system_serial);

    // 修改为：
    seq_printf(m, "Serial\t\t: %s\n", spoofed_serial);

    // 伪造硬件信息（可选）
    seq_printf(m, "Hardware\t: Qualcomm Technologies, Inc SM8550\n");
    seq_printf(m, "Revision\t: 0001\n");

    return 0;
}
```

**另一种方案：修改 /proc/sys/kernel/random/boot_id**

```c
// kernel/drivers/char/random.c

static ssize_t boot_id_show(struct kobject *kobj,
                            struct kobj_attribute *attr, char *buf)
{
    // 原始代码生成真实的 boot_id
    // 我们可以返回伪造的或基于种子生成的值

#ifdef CONFIG_SPOOF_BOOT_ID
    // 编译时配置的固定值
    return sprintf(buf, "12345678-1234-1234-1234-123456789abc\n");
#else
    // 原始实现
    return sprintf(buf, "%pU\n", &boot_id);
#endif
}
```

### 样例 7：集中式配置管理方案

创建一个系统服务来统一管理所有伪造值。

**新建文件**: `frameworks/base/services/core/java/com/android/server/DeviceSpoofService.java`

```java
// frameworks/base/services/core/java/com/android/server/DeviceSpoofService.java

package com.android.server;

import android.content.Context;
import android.os.SystemProperties;
import android.util.Log;
import org.json.JSONObject;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.security.MessageDigest;
import java.util.HashMap;
import java.util.Map;

public class DeviceSpoofService extends SystemService {
    private static final String TAG = "DeviceSpoofService";
    private static final String CONFIG_PATH = "/data/system/spoof_config.json";

    private static DeviceSpoofService sInstance;
    private Map<String, String> mSpoofedValues = new HashMap<>();
    private boolean mEnabled = false;
    private String mSeed;

    // 单例访问
    public static DeviceSpoofService getInstance() {
        return sInstance;
    }

    public DeviceSpoofService(Context context) {
        super(context);
        sInstance = this;
    }

    @Override
    public void onStart() {
        loadConfiguration();
        publishBinderService("device_spoof", new BinderService());
    }

    private void loadConfiguration() {
        try {
            File configFile = new File(CONFIG_PATH);
            if (!configFile.exists()) {
                Log.i(TAG, "No spoof config found, using defaults");
                return;
            }

            StringBuilder content = new StringBuilder();
            BufferedReader reader = new BufferedReader(new FileReader(configFile));
            String line;
            while ((line = reader.readLine()) != null) {
                content.append(line);
            }
            reader.close();

            JSONObject config = new JSONObject(content.toString());

            mEnabled = config.optBoolean("enabled", false);
            mSeed = config.optString("seed", String.valueOf(System.currentTimeMillis()));

            // 加载预设值
            JSONObject values = config.optJSONObject("values");
            if (values != null) {
                for (java.util.Iterator<String> it = values.keys(); it.hasNext();) {
                    String key = it.next();
                    mSpoofedValues.put(key, values.getString(key));
                }
            }

            Log.i(TAG, "Spoof config loaded, enabled=" + mEnabled +
                       ", values count=" + mSpoofedValues.size());

        } catch (Exception e) {
            Log.e(TAG, "Failed to load config", e);
        }
    }

    // ============================================
    // 公共 API
    // ============================================

    public boolean isEnabled() {
        return mEnabled;
    }

    public String getSpoofedValue(String key) {
        if (!mEnabled) return null;

        // 优先返回配置中的值
        if (mSpoofedValues.containsKey(key)) {
            return mSpoofedValues.get(key);
        }

        // 否则基于种子生成
        return generateValue(key);
    }

    public String getImei(int slot) {
        String key = "imei_" + slot;
        String value = getSpoofedValue(key);
        if (value != null) return value;

        return generateImei(slot);
    }

    public String getAndroidId() {
        String value = getSpoofedValue("android_id");
        if (value != null) return value;

        return generateHexString("android_id", 16);
    }

    public String getMacAddress() {
        String value = getSpoofedValue("wifi_mac");
        if (value != null) return value;

        return generateMacAddress("wifi_mac");
    }

    public String getSerialNumber() {
        String value = getSpoofedValue("serial");
        if (value != null) return value;

        return generateAlphanumeric("serial", 16);
    }

    // ============================================
    // 生成器方法
    // ============================================

    private String generateValue(String key) {
        return generateHexString(key, 16);
    }

    private String generateHexString(String key, int length) {
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            md.update((mSeed + "_" + key).getBytes());
            byte[] hash = md.digest();

            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < length / 2; i++) {
                sb.append(String.format("%02x", hash[i] & 0xFF));
            }
            return sb.toString();

        } catch (Exception e) {
            return null;
        }
    }

    private String generateAlphanumeric(String key, int length) {
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            md.update((mSeed + "_" + key).getBytes());
            byte[] hash = md.digest();

            String chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ";
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < length; i++) {
                sb.append(chars.charAt(Math.abs(hash[i % hash.length]) % chars.length()));
            }
            return sb.toString();

        } catch (Exception e) {
            return null;
        }
    }

    private String generateImei(int slot) {
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            md.update((mSeed + "_imei_" + slot).getBytes());
            byte[] hash = md.digest();

            StringBuilder sb = new StringBuilder();
            sb.append("86"); // TAC 前缀
            for (int i = 0; i < 12; i++) {
                sb.append(Math.abs(hash[i]) % 10);
            }

            // 计算 Luhn 校验位
            String base = sb.toString();
            int sum = 0;
            for (int i = 0; i < 14; i++) {
                int digit = base.charAt(i) - '0';
                if (i % 2 == 1) {
                    digit *= 2;
                    if (digit > 9) digit -= 9;
                }
                sum += digit;
            }
            int check = (10 - (sum % 10)) % 10;

            return base + check;

        } catch (Exception e) {
            return "861234567890123";
        }
    }

    private String generateMacAddress(String key) {
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            md.update((mSeed + "_" + key).getBytes());
            byte[] hash = md.digest();

            // 设置本地管理位
            hash[0] = (byte) ((hash[0] & 0xFC) | 0x02);

            return String.format("%02x:%02x:%02x:%02x:%02x:%02x",
                hash[0] & 0xFF, hash[1] & 0xFF, hash[2] & 0xFF,
                hash[3] & 0xFF, hash[4] & 0xFF, hash[5] & 0xFF);

        } catch (Exception e) {
            return "02:00:00:00:00:00";
        }
    }
}
```

**配置文件示例** (`/data/system/spoof_config.json`):

```json
{
    "enabled": true,
    "seed": "my_unique_seed_12345",
    "values": {
        "model": "Pixel 8 Pro",
        "brand": "google",
        "manufacturer": "Google",
        "device": "husky",
        "product": "husky",
        "fingerprint": "google/husky/husky:14/UD1A.231105.004/11010374:user/release-keys",
        "android_id": "a1b2c3d4e5f67890",
        "serial": "ABCD1234EFGH5678",
        "imei_0": "861234567890123",
        "imei_1": "861234567890124",
        "wifi_mac": "02:ab:cd:ef:12:34"
    }
}
```

### 样例 8：修改 SensorManager 伪造传感器数据

**文件路径**: `frameworks/base/core/java/android/hardware/SensorManager.java`

```java
// frameworks/base/core/java/android/hardware/SensorManager.java

package android.hardware;

import android.os.SystemProperties;
import java.util.ArrayList;
import java.util.List;

public abstract class SensorManager {

    // ============================================
    // 传感器列表伪造
    // ============================================

    // 修改传感器列表，隐藏或伪造某些传感器
    public List<Sensor> getSensorList(int type) {
        List<Sensor> realList = getSensorListInternal(type);

        if (!isSpoofEnabled()) {
            return realList;
        }

        List<Sensor> spoofedList = new ArrayList<>();

        for (Sensor sensor : realList) {
            // 可选：隐藏某些传感器
            if (shouldHideSensor(sensor)) {
                continue;
            }

            // 伪造传感器的厂商和名称
            Sensor spoofedSensor = spoofSensorInfo(sensor);
            spoofedList.add(spoofedSensor);
        }

        return spoofedList;
    }

    private boolean shouldHideSensor(Sensor sensor) {
        // 例如：隐藏指纹传感器信息
        String name = sensor.getName().toLowerCase();
        return name.contains("fingerprint") || name.contains("biometric");
    }

    private Sensor spoofSensorInfo(Sensor original) {
        // 创建一个带伪造信息的传感器副本
        // 注意：这需要修改 Sensor 类使其可修改或创建新的构造器
        return new SpoofedSensor(original,
            "Qualcomm", // 伪造的厂商
            "Qualcomm Accelerometer" // 伪造的名称
        );
    }

    private boolean isSpoofEnabled() {
        return "true".equals(SystemProperties.get("persist.spoof.enabled", "false"));
    }

    protected abstract List<Sensor> getSensorListInternal(int type);
}
```

---

## 编译与刷机

1. **设置环境**: `source build/envsetup.sh`

2. **选择目标**: `lunch aosp_<device_name>-userdebug` (例如 `lunch aosp_husky-userdebug` 对应 Pixel 8 Pro)

3. **开始编译**: `make -j$(nproc)` (这会花费数小时)

4. **刷机**:
   - 将设备置于 `fastboot` 模式。
   - 执行 `fastboot flashall -w`，这将刷写所有编译生成的镜像 (`system.img`, `boot.img`, `vendor.img` 等)。

---

## 增量编译技巧

修改特定模块后，无需全量编译：

```bash
# 只编译 Framework
m framework

# 只编译 TelephonyProvider
m TelephonyProvider

# 只编译 SystemUI
m SystemUI

# 只重新生成 system.img（不重新编译模块）
m snod

# 只重新生成 boot.img
m bootimage

# 使用 adb 同步修改的文件（无需刷机）
adb root
adb remount
adb sync system
adb reboot
```

---

## 测试与验证

### 验证脚本

创建一个 App 或使用 adb shell 验证伪造是否生效：

```bash
#!/system/bin/sh
# 验证改机效果

echo "=== Build Info ==="
getprop ro.product.model
getprop ro.product.brand
getprop ro.build.fingerprint
getprop ro.serialno

echo "=== Android ID ==="
settings get secure android_id

echo "=== IMEI (需要电话权限) ==="
service call iphonesubinfo 1

echo "=== Wi-Fi MAC ==="
cat /sys/class/net/wlan0/address

echo "=== CPU Serial ==="
cat /proc/cpuinfo | grep Serial
```

### 常见检测点对照表

| 检测项 | API/路径 | 对应修改位置 |
|--------|----------|--------------|
| 设备型号 | `Build.MODEL` | `Build.java` |
| 品牌 | `Build.BRAND` | `Build.java` |
| 指纹 | `Build.FINGERPRINT` | `Build.java` |
| 序列号 | `Build.SERIAL` | `Build.java` + 内核 |
| Android ID | `Settings.Secure.ANDROID_ID` | `Settings.java` |
| IMEI | `TelephonyManager.getImei()` | `TelephonyManager.java` |
| MAC 地址 | `WifiInfo.getMacAddress()` | `WifiInfo.java` |
| 系统属性 | `SystemProperties.get()` | `SystemProperties.cpp` |
| CPU 序列号 | `/proc/cpuinfo` | 内核 `cpuinfo.c` |
| Boot ID | `/proc/sys/kernel/random/boot_id` | 内核 `random.c` |

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

---

## 进阶技巧

### 1. 随机种子管理

使用单一种子生成所有伪造值，保证同一"设备身份"的一致性：

```java
// 初始化时设置种子
adb shell setprop ro.spoof.seed "unique_device_$(date +%s)"
```

### 2. 多身份切换

通过切换种子实现多个"设备身份"：

```bash
# 切换到身份 A
adb shell setprop persist.spoof.profile "profile_a"
adb shell svc power reboot

# 切换到身份 B
adb shell setprop persist.spoof.profile "profile_b"
adb shell svc power reboot
```

### 3. 避免检测的注意事项

- **保持一致性**: 所有相关字段要匹配（如 Model 和 Fingerprint 中的设备名要一致）
- **合法格式**: IMEI 要通过 Luhn 校验，MAC 要是合法格式
- **时间戳合理**: Build 时间不要设置成未来时间
- **避免已知测试值**: 不要使用 `000000000000000` 等明显的测试值
