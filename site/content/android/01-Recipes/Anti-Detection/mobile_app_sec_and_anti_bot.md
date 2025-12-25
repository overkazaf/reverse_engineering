---
title: "移动端安全与风控技术"
date: 2024-10-05
type: posts
tags: ["加密分析", "Hook", "DEX", "反检测", "IDA Pro", "反混淆"]
weight: 10
---

# 移动端安全与风控技术

> **📚 前置知识**
>
> 本配方涉及以下核心技术，建议先阅读相关章节：
>
> - **[T01: Frida 使用指南](../../02-Tools/Dynamic/frida_guide.md)** - 动态分析与 Hook 技术
> - **[C01: 反分析技术案例](../../03-Case-Studies/case_anti_analysis_techniques.md)** - 常见检测手段与绕过
> - **[R17: 设备指纹与绕过](device_fingerprinting_and_bypass.md)** - 设备指纹采集技术

现代移动应用，特别是处理敏感用户数据或有价值业务逻辑的应用，通常会实现多层安全机制来防御逆向工程、篡改和自动化滥用。这一领域涉及 RASP（运行时应用自我保护）、反机器人技术、风控引擎等多个技术方向。

---

## 技术体系概览

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           移动端风控技术体系                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         客户端安全层                                 │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐  │   │
│  │  │  环境检测   │  │  代码保护   │  │  数据加密   │  │ 设备指纹  │  │   │
│  │  │ Root/越狱  │  │ 代码混淆    │  │ 通信加密    │  │ 唯一标识  │  │   │
│  │  │ 模拟器     │  │ 反调试      │  │ 本地加密    │  │ 行为特征  │  │   │
│  │  │ Hook 框架  │  │ 完整性校验  │  │ 密钥保护    │  │ 硬件信息  │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └───────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         通信安全层                                   │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐  │   │
│  │  │ SSL Pinning │  │  请求签名   │  │  防重放     │  │ 协议加密  │  │   │
│  │  │ 证书固定    │  │ HMAC/签名  │  │ 时间戳+随机 │  │ 自定义协议│  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └───────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         服务端风控层                                 │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐  │   │
│  │  │  行为分析   │  │  规则引擎   │  │  ML 模型    │  │ 风险决策  │  │   │
│  │  │ 时序分析    │  │ 实时规则    │  │ 异常检测    │  │ 拦截/放行 │  │   │
│  │  │ 模式识别    │  │ 黑名单      │  │ 用户画像    │  │ 验证码    │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └───────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 1. 客户端安全技术

### 1.1 环境检测机制

#### Root/越狱检测

**检测维度**：

```java
// Java 实现 - 综合 Root 检测
public class RootDetection {

    // 检测维度1: 文件系统检测
    private static final String[] ROOT_PATHS = {
        "/system/bin/su", "/system/xbin/su", "/sbin/su",
        "/data/local/bin/su", "/data/local/xbin/su",
        "/system/app/Superuser.apk", "/system/etc/init.d/99SuperSUDaemon",
        "/dev/com.koushikdutta.superuser.daemon/",
        "/system/xbin/daemonsu"
    };

    // 检测维度2: Build 属性检测
    private static boolean checkBuildTags() {
        String buildTags = android.os.Build.TAGS;
        return buildTags != null && buildTags.contains("test-keys");
    }

    // 检测维度3: 危险应用检测
    private static final String[] ROOT_PACKAGES = {
        "com.topjohnwu.magisk",
        "eu.chainfire.supersu",
        "com.koushikdutta.superuser",
        "com.noshufou.android.su",
        "com.thirdparty.superuser",
        "com.yellowes.su",
        "com.devadvance.rootcloak",
        "de.robv.android.xposed.installer",
        "org.lsposed.manager"
    };

    // 检测维度4: Native 层检测
    public static native boolean nativeRootCheck();

    // 综合检测
    public static int getRootScore(Context context) {
        int score = 0;

        // 文件检测 (权重: 30)
        for (String path : ROOT_PATHS) {
            if (new File(path).exists()) {
                score += 30;
                break;
            }
        }

        // Build 属性 (权重: 20)
        if (checkBuildTags()) {
            score += 20;
        }

        // 应用检测 (权重: 25)
        PackageManager pm = context.getPackageManager();
        for (String pkg : ROOT_PACKAGES) {
            try {
                pm.getPackageInfo(pkg, 0);
                score += 25;
                break;
            } catch (PackageManager.NameNotFoundException e) {
                // 未安装
            }
        }

        // Native 检测 (权重: 25)
        if (nativeRootCheck()) {
            score += 25;
        }

        return score;  // 0-100 分，越高越可疑
    }
}
```

**Native 层检测**：

```c
// Native (C/C++) 实现 - Root 检测
#include <jni.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/stat.h>
#include <dirent.h>

// 检测 su 二进制文件
int check_su_exists() {
    const char* paths[] = {
        "/system/bin/su",
        "/system/xbin/su",
        "/sbin/su",
        "/su/bin/su",
        "/data/local/bin/su"
    };

    for (int i = 0; i < 5; i++) {
        struct stat st;
        if (stat(paths[i], &st) == 0) {
            return 1;
        }
    }
    return 0;
}

// 检测 Magisk
int check_magisk() {
    // 检测 Magisk 目录
    struct stat st;
    if (stat("/sbin/.magisk", &st) == 0) return 1;
    if (stat("/data/adb/magisk", &st) == 0) return 1;

    // 检测 Magisk 随机化路径
    DIR* dir = opendir("/data/adb/modules");
    if (dir != NULL) {
        closedir(dir);
        return 1;
    }

    return 0;
}

// 检测 SELinux 状态
int check_selinux() {
    FILE* fp = fopen("/sys/fs/selinux/enforce", "r");
    if (fp == NULL) return 0;

    int enforcing = 0;
    fscanf(fp, "%d", &enforcing);
    fclose(fp);

    // enforcing = 0 表示 Permissive 模式，可能被 Root
    return enforcing == 0 ? 1 : 0;
}

// 检测可疑进程
int check_suspicious_process() {
    FILE* fp = popen("ps -A", "r");
    if (fp == NULL) return 0;

    char line[256];
    while (fgets(line, sizeof(line), fp)) {
        if (strstr(line, "daemonsu") ||
            strstr(line, "magiskd") ||
            strstr(line, "supersu")) {
            pclose(fp);
            return 1;
        }
    }
    pclose(fp);
    return 0;
}

JNIEXPORT jboolean JNICALL
Java_com_example_RootDetection_nativeRootCheck(JNIEnv *env, jclass clazz) {
    if (check_su_exists()) return JNI_TRUE;
    if (check_magisk()) return JNI_TRUE;
    if (check_selinux()) return JNI_TRUE;
    if (check_suspicious_process()) return JNI_TRUE;
    return JNI_FALSE;
}
```

#### Hook 框架检测

**Frida 检测**：

```java
// Java 实现 - Frida 检测
public class FridaDetection {

    // 检测 Frida 端口
    public static boolean checkFridaPort() {
        int[] ports = {27042, 27043, 27044, 27045};

        for (int port : ports) {
            try {
                java.net.Socket socket = new java.net.Socket();
                socket.connect(
                    new java.net.InetSocketAddress("127.0.0.1", port), 100
                );
                socket.close();
                return true;  // 端口开放
            } catch (Exception e) {
                // 连接失败
            }
        }
        return false;
    }

    // 检测 Frida 库
    public static boolean checkFridaLibrary() {
        try {
            BufferedReader reader = new BufferedReader(
                new FileReader("/proc/self/maps")
            );
            String line;
            while ((line = reader.readLine()) != null) {
                if (line.contains("frida") ||
                    line.contains("gadget") ||
                    line.contains("gum-js")) {
                    reader.close();
                    return true;
                }
            }
            reader.close();
        } catch (Exception e) {
            // 忽略
        }
        return false;
    }

    // 检测 Frida 线程
    public static boolean checkFridaThread() {
        try {
            File threadsDir = new File("/proc/self/task");
            File[] threads = threadsDir.listFiles();

            if (threads != null) {
                for (File thread : threads) {
                    File commFile = new File(thread, "comm");
                    BufferedReader reader = new BufferedReader(
                        new FileReader(commFile)
                    );
                    String comm = reader.readLine();
                    reader.close();

                    if (comm != null && (
                        comm.contains("gum-js-loop") ||
                        comm.contains("gmain") ||
                        comm.contains("pool-frida"))) {
                        return true;
                    }
                }
            }
        } catch (Exception e) {
            // 忽略
        }
        return false;
    }

    // Native 层检测
    public static native boolean nativeFridaCheck();
}
```

**Native 层 Frida 检测**：

```c
// Native (C/C++) 实现 - Frida 检测
#include <jni.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <dlfcn.h>
#include <link.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <pthread.h>

// Frida 特征字符串
static const char* frida_strings[] = {
    "LIBFRIDA",
    "frida:rpc",
    "frida-agent",
    "frida-gadget",
    "gum-js-loop",
    "pool-frida",
    "linjector"
};

// 检测内存中的 Frida 特征
int scan_memory_for_frida() {
    FILE* fp = fopen("/proc/self/maps", "r");
    if (fp == NULL) return 0;

    char line[512];
    while (fgets(line, sizeof(line), fp)) {
        for (int i = 0; i < sizeof(frida_strings) / sizeof(frida_strings[0]); i++) {
            if (strcasestr(line, frida_strings[i])) {
                fclose(fp);
                return 1;
            }
        }
    }
    fclose(fp);
    return 0;
}

// 检测 D-Bus (Frida 通信通道)
int check_dbus() {
    char line[256];
    FILE* fp = fopen("/proc/self/fd", "r");
    if (fp == NULL) return 0;

    DIR* dir = opendir("/proc/self/fd");
    if (dir == NULL) return 0;

    struct dirent* entry;
    while ((entry = readdir(dir)) != NULL) {
        char link_path[256];
        char target[256];

        snprintf(link_path, sizeof(link_path), "/proc/self/fd/%s", entry->d_name);
        ssize_t len = readlink(link_path, target, sizeof(target) - 1);

        if (len > 0) {
            target[len] = '\0';
            if (strstr(target, "frida") || strstr(target, "linjector")) {
                closedir(dir);
                return 1;
            }
        }
    }

    closedir(dir);
    return 0;
}

// 检测 Inline Hook (函数入口被修改)
int check_inline_hook(void* func_ptr) {
    unsigned char* code = (unsigned char*)func_ptr;

#if defined(__arm__)
    // ARM32: 检测 LDR PC 或 B 指令
    // LDR PC, [PC, #offset] 的 opcode 通常以 0xE5 开头
    if ((code[3] & 0xFE) == 0xE5) return 1;
#elif defined(__aarch64__)
    // ARM64: 检测 BR X16/X17 或 B 指令
    unsigned int instruction = *(unsigned int*)code;
    // B 指令: 0x14000000
    if ((instruction & 0xFC000000) == 0x14000000) return 1;
    // BR X16: 0xD61F0200
    if (instruction == 0xD61F0200 || instruction == 0xD61F0220) return 1;
#elif defined(__i386__) || defined(__x86_64__)
    // x86/x64: 检测 JMP 指令
    if (code[0] == 0xE9 || code[0] == 0xE8) return 1;  // JMP/CALL relative
    if (code[0] == 0xFF && code[1] == 0x25) return 1;  // JMP absolute
#endif

    return 0;
}

// 检测关键函数是否被 Hook
int check_common_hooks() {
    void* funcs[] = {
        dlsym(RTLD_DEFAULT, "open"),
        dlsym(RTLD_DEFAULT, "read"),
        dlsym(RTLD_DEFAULT, "write"),
        dlsym(RTLD_DEFAULT, "connect"),
        dlsym(RTLD_DEFAULT, "ptrace")
    };

    for (int i = 0; i < 5; i++) {
        if (funcs[i] && check_inline_hook(funcs[i])) {
            return 1;
        }
    }
    return 0;
}

JNIEXPORT jboolean JNICALL
Java_com_example_FridaDetection_nativeFridaCheck(JNIEnv *env, jclass clazz) {
    if (scan_memory_for_frida()) return JNI_TRUE;
    if (check_dbus()) return JNI_TRUE;
    if (check_common_hooks()) return JNI_TRUE;
    return JNI_FALSE;
}
```

### 1.2 设备指纹采集

#### 多维度指纹采集

```java
// Java 实现 - 设备指纹采集
public class DeviceFingerprint {

    // 硬件指纹
    public static class HardwareFingerprint {
        public String androidId;
        public String serialNumber;
        public String imei;
        public String macAddress;
        public String cpuInfo;
        public String buildInfo;
    }

    // 软件指纹
    public static class SoftwareFingerprint {
        public String osVersion;
        public List<String> installedApps;
        public String timezone;
        public String language;
        public Map<String, String> systemProperties;
    }

    // 行为指纹
    public static class BehaviorFingerprint {
        public long[] touchPattern;      // 触摸时间间隔
        public float[] sensorData;       // 传感器数据特征
        public int screenOrientation;    // 屏幕方向变化频率
        public long sessionDuration;     // 会话时长
    }

    // 综合采集
    public static Map<String, Object> collectFingerprint(Context context) {
        Map<String, Object> fingerprint = new HashMap<>();

        // 1. Android ID
        fingerprint.put("android_id", Settings.Secure.getString(
            context.getContentResolver(), Settings.Secure.ANDROID_ID
        ));

        // 2. Build 信息
        fingerprint.put("build_model", Build.MODEL);
        fingerprint.put("build_brand", Build.BRAND);
        fingerprint.put("build_device", Build.DEVICE);
        fingerprint.put("build_product", Build.PRODUCT);
        fingerprint.put("build_manufacturer", Build.MANUFACTURER);
        fingerprint.put("build_fingerprint", Build.FINGERPRINT);
        fingerprint.put("build_hardware", Build.HARDWARE);
        fingerprint.put("build_board", Build.BOARD);
        fingerprint.put("build_bootloader", Build.BOOTLOADER);
        fingerprint.put("build_display", Build.DISPLAY);
        fingerprint.put("build_host", Build.HOST);
        fingerprint.put("build_id", Build.ID);
        fingerprint.put("build_tags", Build.TAGS);
        fingerprint.put("build_type", Build.TYPE);
        fingerprint.put("build_user", Build.USER);

        // 3. 系统信息
        fingerprint.put("sdk_int", Build.VERSION.SDK_INT);
        fingerprint.put("release", Build.VERSION.RELEASE);
        fingerprint.put("incremental", Build.VERSION.INCREMENTAL);

        // 4. 屏幕信息
        DisplayMetrics dm = context.getResources().getDisplayMetrics();
        fingerprint.put("screen_width", dm.widthPixels);
        fingerprint.put("screen_height", dm.heightPixels);
        fingerprint.put("screen_density", dm.density);
        fingerprint.put("screen_dpi", dm.densityDpi);

        // 5. 网络信息
        try {
            List<NetworkInterface> interfaces = Collections.list(
                NetworkInterface.getNetworkInterfaces()
            );
            for (NetworkInterface ni : interfaces) {
                byte[] mac = ni.getHardwareAddress();
                if (mac != null && ni.getName().equals("wlan0")) {
                    StringBuilder sb = new StringBuilder();
                    for (byte b : mac) {
                        sb.append(String.format("%02X:", b));
                    }
                    fingerprint.put("wifi_mac", sb.substring(0, sb.length() - 1));
                }
            }
        } catch (Exception e) {
            // 忽略
        }

        // 6. 传感器信息
        SensorManager sm = (SensorManager) context.getSystemService(
            Context.SENSOR_SERVICE
        );
        List<Sensor> sensors = sm.getSensorList(Sensor.TYPE_ALL);
        List<String> sensorNames = new ArrayList<>();
        for (Sensor s : sensors) {
            sensorNames.add(s.getName() + ":" + s.getVendor());
        }
        fingerprint.put("sensors", sensorNames);

        // 7. CPU 信息
        fingerprint.put("cpu_abi", Build.SUPPORTED_ABIS);
        fingerprint.put("cpu_cores", Runtime.getRuntime().availableProcessors());

        // 8. 内存信息
        ActivityManager am = (ActivityManager) context.getSystemService(
            Context.ACTIVITY_SERVICE
        );
        ActivityManager.MemoryInfo mi = new ActivityManager.MemoryInfo();
        am.getMemoryInfo(mi);
        fingerprint.put("total_memory", mi.totalMem);

        // 9. 存储信息
        StatFs stat = new StatFs(Environment.getExternalStorageDirectory().getPath());
        fingerprint.put("total_storage", stat.getBlockSizeLong() * stat.getBlockCountLong());

        // 10. 时区和语言
        fingerprint.put("timezone", TimeZone.getDefault().getID());
        fingerprint.put("language", Locale.getDefault().getLanguage());
        fingerprint.put("country", Locale.getDefault().getCountry());

        return fingerprint;
    }

    // 计算指纹哈希
    public static String computeFingerprintHash(Map<String, Object> fingerprint) {
        try {
            // 排序键以确保一致性
            TreeMap<String, Object> sorted = new TreeMap<>(fingerprint);

            StringBuilder sb = new StringBuilder();
            for (Map.Entry<String, Object> entry : sorted.entrySet()) {
                sb.append(entry.getKey()).append("=").append(entry.getValue()).append("|");
            }

            MessageDigest md = MessageDigest.getInstance("SHA-256");
            byte[] hash = md.digest(sb.toString().getBytes("UTF-8"));

            StringBuilder hexString = new StringBuilder();
            for (byte b : hash) {
                hexString.append(String.format("%02x", b));
            }

            return hexString.toString();
        } catch (Exception e) {
            return null;
        }
    }
}
```

#### Canvas 指纹

```java
// Java 实现 - Canvas 指纹
public class CanvasFingerprint {

    public static String generateCanvasFingerprint(Context context) {
        // 创建 Bitmap
        Bitmap bitmap = Bitmap.createBitmap(200, 50, Bitmap.Config.ARGB_8888);
        Canvas canvas = new Canvas(bitmap);

        // 绘制背景
        canvas.drawColor(Color.WHITE);

        // 绘制文本
        Paint textPaint = new Paint();
        textPaint.setAntiAlias(true);
        textPaint.setTextSize(14);
        textPaint.setColor(Color.rgb(102, 204, 0));
        textPaint.setTypeface(Typeface.create("Arial", Typeface.BOLD));

        String text = "Canvas Fingerprint 🎨";
        canvas.drawText(text, 10, 30, textPaint);

        // 绘制几何图形
        Paint shapePaint = new Paint();
        shapePaint.setColor(Color.rgb(255, 102, 0));
        shapePaint.setStyle(Paint.Style.FILL);
        canvas.drawRect(150, 10, 180, 40, shapePaint);

        shapePaint.setColor(Color.rgb(0, 102, 255));
        canvas.drawCircle(190, 25, 10, shapePaint);

        // 提取像素数据并计算哈希
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        bitmap.compress(Bitmap.CompressFormat.PNG, 100, baos);
        byte[] imageData = baos.toByteArray();

        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            byte[] hash = md.digest(imageData);

            StringBuilder sb = new StringBuilder();
            for (byte b : hash) {
                sb.append(String.format("%02x", b));
            }
            return sb.toString();
        } catch (Exception e) {
            return null;
        }
    }
}
```

---

## 2. 通信安全技术

### 2.1 请求签名机制

#### HMAC 签名实现

```java
// Java 实现 - 请求签名
public class RequestSigner {

    private static final String HMAC_ALGORITHM = "HmacSHA256";
    private byte[] secretKey;

    public RequestSigner(byte[] secretKey) {
        this.secretKey = secretKey;
    }

    // 生成签名
    public String sign(Map<String, String> params, long timestamp, String nonce) {
        // 1. 排序参数
        TreeMap<String, String> sortedParams = new TreeMap<>(params);

        // 2. 构建待签名字符串
        StringBuilder sb = new StringBuilder();
        for (Map.Entry<String, String> entry : sortedParams.entrySet()) {
            if (sb.length() > 0) {
                sb.append("&");
            }
            sb.append(entry.getKey()).append("=").append(entry.getValue());
        }

        // 3. 添加时间戳和随机数
        sb.append("&timestamp=").append(timestamp);
        sb.append("&nonce=").append(nonce);

        // 4. 计算 HMAC
        try {
            Mac mac = Mac.getInstance(HMAC_ALGORITHM);
            SecretKeySpec keySpec = new SecretKeySpec(secretKey, HMAC_ALGORITHM);
            mac.init(keySpec);

            byte[] signature = mac.doFinal(sb.toString().getBytes("UTF-8"));

            // 5. Base64 编码
            return Base64.encodeToString(signature, Base64.NO_WRAP);
        } catch (Exception e) {
            return null;
        }
    }

    // 生成随机数
    public static String generateNonce() {
        byte[] nonce = new byte[16];
        new SecureRandom().nextBytes(nonce);

        StringBuilder sb = new StringBuilder();
        for (byte b : nonce) {
            sb.append(String.format("%02x", b));
        }
        return sb.toString();
    }

    // 构建签名请求
    public Map<String, String> buildSignedRequest(
            String url,
            Map<String, String> params) {

        long timestamp = System.currentTimeMillis() / 1000;
        String nonce = generateNonce();
        String signature = sign(params, timestamp, nonce);

        Map<String, String> signedParams = new HashMap<>(params);
        signedParams.put("timestamp", String.valueOf(timestamp));
        signedParams.put("nonce", nonce);
        signedParams.put("sign", signature);

        return signedParams;
    }
}
```

#### 复杂签名算法示例

某些应用使用更复杂的签名算法：

```java
// Java 实现 - 复杂签名算法示例
public class ComplexSigner {

    // 签名算法: SHA256(MD5(params) + timestamp + deviceId + salt)
    public static String complexSign(
            Map<String, String> params,
            long timestamp,
            String deviceId,
            String salt) {

        try {
            // 1. 对参数进行 MD5
            TreeMap<String, String> sorted = new TreeMap<>(params);
            StringBuilder paramStr = new StringBuilder();
            for (Map.Entry<String, String> e : sorted.entrySet()) {
                paramStr.append(e.getKey()).append(e.getValue());
            }

            MessageDigest md5 = MessageDigest.getInstance("MD5");
            byte[] paramHash = md5.digest(paramStr.toString().getBytes("UTF-8"));
            String paramMd5 = bytesToHex(paramHash);

            // 2. 拼接其他要素
            String toSign = paramMd5 + timestamp + deviceId + salt;

            // 3. SHA256
            MessageDigest sha256 = MessageDigest.getInstance("SHA-256");
            byte[] finalHash = sha256.digest(toSign.getBytes("UTF-8"));

            return bytesToHex(finalHash);

        } catch (Exception e) {
            return null;
        }
    }

    // 带加密的签名
    public static String encryptedSign(
            Map<String, String> params,
            String key) {

        try {
            // 1. JSON 序列化
            JSONObject json = new JSONObject(params);
            String plaintext = json.toString();

            // 2. AES 加密
            SecretKeySpec keySpec = new SecretKeySpec(
                key.getBytes("UTF-8"), "AES"
            );
            Cipher cipher = Cipher.getInstance("AES/CBC/PKCS5Padding");
            byte[] iv = new byte[16];
            new SecureRandom().nextBytes(iv);
            IvParameterSpec ivSpec = new IvParameterSpec(iv);

            cipher.init(Cipher.ENCRYPT_MODE, keySpec, ivSpec);
            byte[] encrypted = cipher.doFinal(plaintext.getBytes("UTF-8"));

            // 3. 组合 IV + 密文
            byte[] result = new byte[iv.length + encrypted.length];
            System.arraycopy(iv, 0, result, 0, iv.length);
            System.arraycopy(encrypted, 0, result, iv.length, encrypted.length);

            // 4. Base64 编码
            return Base64.encodeToString(result, Base64.NO_WRAP);

        } catch (Exception e) {
            return null;
        }
    }

    private static String bytesToHex(byte[] bytes) {
        StringBuilder sb = new StringBuilder();
        for (byte b : bytes) {
            sb.append(String.format("%02x", b));
        }
        return sb.toString();
    }
}
```

### 2.2 防重放攻击

```java
// Java 实现 - 防重放机制
public class AntiReplay {

    // 客户端实现
    public static class ClientAntiReplay {
        private AtomicLong sequence = new AtomicLong(0);

        // 生成唯一请求 ID
        public String generateRequestId() {
            long timestamp = System.currentTimeMillis();
            long seq = sequence.incrementAndGet();
            String deviceId = getDeviceId();

            // 格式: timestamp-sequence-deviceId-random
            String random = UUID.randomUUID().toString().substring(0, 8);
            return String.format("%d-%d-%s-%s", timestamp, seq, deviceId, random);
        }

        // 添加时间戳和签名
        public void addAntiReplayHeaders(HttpURLConnection conn, String body) {
            long timestamp = System.currentTimeMillis();
            String nonce = UUID.randomUUID().toString();
            String requestId = generateRequestId();

            // 计算签名: HMAC(timestamp + nonce + body)
            String toSign = timestamp + nonce + body;
            String signature = computeHmac(toSign);

            conn.setRequestProperty("X-Timestamp", String.valueOf(timestamp));
            conn.setRequestProperty("X-Nonce", nonce);
            conn.setRequestProperty("X-Request-Id", requestId);
            conn.setRequestProperty("X-Signature", signature);
        }

        private String computeHmac(String data) {
            // ... HMAC 计算
            return "";
        }

        private String getDeviceId() {
            // ... 获取设备 ID
            return "";
        }
    }

    // 服务端验证逻辑 (伪代码)
    public static class ServerAntiReplay {
        private Set<String> usedNonces = new ConcurrentHashSet<>();
        private static final long TIMESTAMP_TOLERANCE = 300000;  // 5 分钟容差

        public boolean validateRequest(
                long timestamp,
                String nonce,
                String requestId,
                String signature,
                String body) {

            // 1. 验证时间戳
            long now = System.currentTimeMillis();
            if (Math.abs(now - timestamp) > TIMESTAMP_TOLERANCE) {
                return false;  // 时间戳过期
            }

            // 2. 验证 nonce 唯一性
            if (usedNonces.contains(nonce)) {
                return false;  // 重放攻击
            }
            usedNonces.add(nonce);

            // 3. 验证签名
            String expectedSignature = computeHmac(timestamp + nonce + body);
            if (!signature.equals(expectedSignature)) {
                return false;  // 签名不匹配
            }

            return true;
        }

        private String computeHmac(String data) {
            // ... HMAC 计算
            return "";
        }
    }
}
```

---

## 3. 服务端风控技术

### 3.1 行为分析

```python
# Python 实现 - 服务端行为分析
import time
import statistics
from collections import defaultdict
from typing import List, Dict, Optional

class BehaviorAnalyzer:
    """用户行为分析引擎"""

    def __init__(self):
        self.user_sessions = defaultdict(list)
        self.request_history = defaultdict(list)

    def record_request(self, user_id: str, request_data: Dict):
        """记录用户请求"""
        timestamp = time.time()

        self.request_history[user_id].append({
            'timestamp': timestamp,
            'endpoint': request_data.get('endpoint'),
            'params': request_data.get('params'),
            'user_agent': request_data.get('user_agent'),
            'ip': request_data.get('ip')
        })

        # 保留最近 1000 条记录
        if len(self.request_history[user_id]) > 1000:
            self.request_history[user_id] = self.request_history[user_id][-1000:]

    def analyze_request_frequency(self, user_id: str, window_seconds: int = 60) -> Dict:
        """分析请求频率"""
        now = time.time()
        recent_requests = [
            r for r in self.request_history[user_id]
            if now - r['timestamp'] < window_seconds
        ]

        return {
            'request_count': len(recent_requests),
            'requests_per_second': len(recent_requests) / window_seconds,
            'unique_endpoints': len(set(r['endpoint'] for r in recent_requests)),
            'unique_ips': len(set(r['ip'] for r in recent_requests))
        }

    def analyze_timing_pattern(self, user_id: str) -> Dict:
        """分析请求时间模式"""
        requests = self.request_history[user_id]
        if len(requests) < 10:
            return {'status': 'insufficient_data'}

        # 计算请求间隔
        intervals = []
        for i in range(1, len(requests)):
            interval = requests[i]['timestamp'] - requests[i-1]['timestamp']
            intervals.append(interval)

        return {
            'mean_interval': statistics.mean(intervals),
            'std_interval': statistics.stdev(intervals) if len(intervals) > 1 else 0,
            'min_interval': min(intervals),
            'max_interval': max(intervals),
            # 标准差过小可能是机器人
            'is_suspicious': statistics.stdev(intervals) < 0.1 if len(intervals) > 1 else False
        }

    def analyze_endpoint_pattern(self, user_id: str) -> Dict:
        """分析端点访问模式"""
        requests = self.request_history[user_id]

        endpoint_counts = defaultdict(int)
        for r in requests:
            endpoint_counts[r['endpoint']] += 1

        total = len(requests)
        endpoint_distribution = {
            ep: count / total
            for ep, count in endpoint_counts.items()
        }

        # 计算熵值 (多样性指标)
        import math
        entropy = -sum(
            p * math.log2(p) for p in endpoint_distribution.values() if p > 0
        )

        return {
            'endpoint_distribution': endpoint_distribution,
            'entropy': entropy,
            # 熵值过低表示行为模式过于单一
            'is_suspicious': entropy < 1.0
        }

    def calculate_risk_score(self, user_id: str) -> int:
        """计算风险评分 (0-100)"""
        score = 0

        # 频率分析
        freq = self.analyze_request_frequency(user_id)
        if freq['requests_per_second'] > 10:
            score += 30
        elif freq['requests_per_second'] > 5:
            score += 15

        # 时间模式分析
        timing = self.analyze_timing_pattern(user_id)
        if timing.get('is_suspicious'):
            score += 25

        # 端点模式分析
        endpoint = self.analyze_endpoint_pattern(user_id)
        if endpoint.get('is_suspicious'):
            score += 20

        # IP 一致性
        if freq['unique_ips'] > 3:
            score += 15  # 多 IP 可疑

        return min(score, 100)


class RateLimiter:
    """速率限制器"""

    def __init__(self):
        self.request_counts = defaultdict(list)
        self.blocked_users = set()

    def check_rate_limit(
        self,
        user_id: str,
        endpoint: str,
        limit: int = 100,
        window: int = 60
    ) -> bool:
        """检查是否超过速率限制"""
        if user_id in self.blocked_users:
            return False

        now = time.time()
        key = f"{user_id}:{endpoint}"

        # 清理过期记录
        self.request_counts[key] = [
            ts for ts in self.request_counts[key]
            if now - ts < window
        ]

        # 检查是否超限
        if len(self.request_counts[key]) >= limit:
            return False

        # 记录本次请求
        self.request_counts[key].append(now)
        return True

    def block_user(self, user_id: str, duration: int = 3600):
        """封禁用户"""
        self.blocked_users.add(user_id)
        # 在实际实现中，应该使用定时任务在 duration 后解封

    def is_blocked(self, user_id: str) -> bool:
        """检查用户是否被封禁"""
        return user_id in self.blocked_users


class RuleEngine:
    """规则引擎"""

    def __init__(self):
        self.rules = []

    def add_rule(self, rule_func, action: str, description: str):
        """添加规则"""
        self.rules.append({
            'func': rule_func,
            'action': action,
            'description': description
        })

    def evaluate(self, request_data: Dict) -> List[Dict]:
        """评估所有规则"""
        triggered_rules = []

        for rule in self.rules:
            try:
                if rule['func'](request_data):
                    triggered_rules.append({
                        'action': rule['action'],
                        'description': rule['description']
                    })
            except Exception as e:
                pass

        return triggered_rules


# 使用示例
def create_default_rules():
    engine = RuleEngine()

    # 规则1: 检测高频请求
    engine.add_rule(
        lambda r: r.get('requests_per_minute', 0) > 100,
        'rate_limit',
        '请求频率过高'
    )

    # 规则2: 检测可疑 User-Agent
    suspicious_uas = ['python-requests', 'curl', 'wget', 'scrapy']
    engine.add_rule(
        lambda r: any(ua in r.get('user_agent', '').lower() for ua in suspicious_uas),
        'challenge',
        '可疑 User-Agent'
    )

    # 规则3: 检测异常时间模式
    engine.add_rule(
        lambda r: r.get('timing_std', 1) < 0.05,
        'captcha',
        '请求时间间隔过于规律'
    )

    # 规则4: 检测异常地理位置
    engine.add_rule(
        lambda r: r.get('geo_velocity', 0) > 1000,  # km/h
        'block',
        '地理位置异常跳跃'
    )

    return engine
```

### 3.2 机器学习检测

```python
# Python 实现 - ML 异常检测
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib

class MLBotDetector:
    """基于机器学习的机器人检测"""

    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()

    def extract_features(self, user_data: Dict) -> np.ndarray:
        """提取特征向量"""
        features = [
            # 请求频率特征
            user_data.get('requests_per_minute', 0),
            user_data.get('requests_per_hour', 0),
            user_data.get('unique_endpoints', 0),

            # 时间模式特征
            user_data.get('timing_mean', 0),
            user_data.get('timing_std', 0),
            user_data.get('timing_min', 0),
            user_data.get('timing_max', 0),

            # 会话特征
            user_data.get('session_duration', 0),
            user_data.get('page_views', 0),
            user_data.get('bounce_rate', 0),

            # 设备特征
            1 if user_data.get('has_touch', False) else 0,
            1 if user_data.get('has_sensors', False) else 0,
            user_data.get('screen_width', 0),
            user_data.get('screen_height', 0),

            # 行为特征
            user_data.get('mouse_movements', 0),
            user_data.get('keyboard_events', 0),
            user_data.get('scroll_events', 0)
        ]

        return np.array(features).reshape(1, -1)

    def train(self, training_data: List[Dict]):
        """训练模型"""
        X = np.vstack([
            self.extract_features(d) for d in training_data
        ])

        # 标准化
        X_scaled = self.scaler.fit_transform(X)

        # 使用隔离森林进行异常检测
        self.model = IsolationForest(
            n_estimators=100,
            contamination=0.1,  # 预期异常比例
            random_state=42
        )
        self.model.fit(X_scaled)

    def predict(self, user_data: Dict) -> Dict:
        """预测是否为机器人"""
        if self.model is None:
            raise ValueError("模型未训练")

        X = self.extract_features(user_data)
        X_scaled = self.scaler.transform(X)

        # -1 表示异常，1 表示正常
        prediction = self.model.predict(X_scaled)[0]
        score = self.model.decision_function(X_scaled)[0]

        return {
            'is_bot': prediction == -1,
            'confidence': abs(score),
            'anomaly_score': -score  # 越高越异常
        }

    def save_model(self, path: str):
        """保存模型"""
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler
        }, path)

    def load_model(self, path: str):
        """加载模型"""
        data = joblib.load(path)
        self.model = data['model']
        self.scaler = data['scaler']


class DeepLearningBotDetector:
    """基于深度学习的机器人检测"""

    def __init__(self):
        self.model = None

    def build_model(self, input_dim: int):
        """构建神经网络模型"""
        import tensorflow as tf

        self.model = tf.keras.Sequential([
            tf.keras.layers.Dense(128, activation='relu', input_shape=(input_dim,)),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dense(1, activation='sigmoid')
        ])

        self.model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy', 'AUC']
        )

    def train(self, X_train: np.ndarray, y_train: np.ndarray,
              X_val: np.ndarray = None, y_val: np.ndarray = None):
        """训练模型"""
        callbacks = [
            tf.keras.callbacks.EarlyStopping(
                patience=5,
                restore_best_weights=True
            ),
            tf.keras.callbacks.ReduceLROnPlateau(
                factor=0.5,
                patience=3
            )
        ]

        validation_data = None
        if X_val is not None and y_val is not None:
            validation_data = (X_val, y_val)

        self.model.fit(
            X_train, y_train,
            epochs=100,
            batch_size=32,
            validation_data=validation_data,
            callbacks=callbacks
        )

    def predict(self, X: np.ndarray) -> np.ndarray:
        """预测"""
        return self.model.predict(X)
```

---

## 4. 设备证明技术

### 4.1 Google Play Integrity API

```java
// Java 实现 - Play Integrity API
import com.google.android.play.core.integrity.IntegrityManager;
import com.google.android.play.core.integrity.IntegrityManagerFactory;
import com.google.android.play.core.integrity.IntegrityTokenRequest;
import com.google.android.play.core.integrity.IntegrityTokenResponse;

public class PlayIntegrityChecker {

    private IntegrityManager integrityManager;

    public PlayIntegrityChecker(Context context) {
        this.integrityManager = IntegrityManagerFactory.create(context);
    }

    // 请求完整性令牌
    public void requestIntegrityToken(String nonce, IntegrityCallback callback) {
        // nonce 应该是服务器生成的随机值
        IntegrityTokenRequest request = IntegrityTokenRequest.builder()
            .setNonce(nonce)
            .build();

        integrityManager.requestIntegrityToken(request)
            .addOnSuccessListener(response -> {
                String token = response.token();
                // 将 token 发送到服务器验证
                callback.onSuccess(token);
            })
            .addOnFailureListener(e -> {
                callback.onFailure(e);
            });
    }

    public interface IntegrityCallback {
        void onSuccess(String token);
        void onFailure(Exception e);
    }
}
```

**服务端验证**：

```python
# Python 实现 - 服务端验证 Play Integrity Token
import json
import base64
from google.auth import jwt
from google.oauth2 import service_account
import requests

class PlayIntegrityVerifier:
    """Play Integrity API 服务端验证"""

    def __init__(self, package_name: str, credentials_path: str):
        self.package_name = package_name
        self.credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=['https://www.googleapis.com/auth/playintegrity']
        )

    def verify_token(self, token: str, nonce: str) -> Dict:
        """验证完整性令牌"""

        # 1. 调用 Google API 解码令牌
        url = f"https://playintegrity.googleapis.com/v1/{self.package_name}:decodeIntegrityToken"

        headers = {
            'Authorization': f'Bearer {self.credentials.token}',
            'Content-Type': 'application/json'
        }

        data = {
            'integrityToken': token
        }

        response = requests.post(url, headers=headers, json=data)
        result = response.json()

        if 'tokenPayloadExternal' not in result:
            return {'valid': False, 'error': 'Invalid token'}

        payload = result['tokenPayloadExternal']

        # 2. 验证 nonce
        if payload.get('requestDetails', {}).get('nonce') != nonce:
            return {'valid': False, 'error': 'Nonce mismatch'}

        # 3. 验证包名
        if payload.get('appIntegrity', {}).get('packageName') != self.package_name:
            return {'valid': False, 'error': 'Package name mismatch'}

        # 4. 检查设备完整性
        device_integrity = payload.get('deviceIntegrity', {})
        device_verdict = device_integrity.get('deviceRecognitionVerdict', [])

        # 5. 检查应用完整性
        app_integrity = payload.get('appIntegrity', {})
        app_verdict = app_integrity.get('appRecognitionVerdict')

        # 6. 检查账号完整性
        account_details = payload.get('accountDetails', {})
        account_verdict = account_details.get('appLicensingVerdict')

        return {
            'valid': True,
            'device_verdict': device_verdict,
            'app_verdict': app_verdict,
            'account_verdict': account_verdict,
            'is_genuine_device': 'MEETS_DEVICE_INTEGRITY' in device_verdict,
            'is_genuine_app': app_verdict == 'PLAY_RECOGNIZED',
            'is_licensed': account_verdict == 'LICENSED'
        }

    def calculate_risk_level(self, verification_result: Dict) -> str:
        """根据验证结果计算风险等级"""
        if not verification_result.get('valid'):
            return 'HIGH'

        score = 0

        if verification_result.get('is_genuine_device'):
            score += 40
        if verification_result.get('is_genuine_app'):
            score += 30
        if verification_result.get('is_licensed'):
            score += 30

        if score >= 80:
            return 'LOW'
        elif score >= 50:
            return 'MEDIUM'
        else:
            return 'HIGH'
```

### 4.2 SafetyNet Attestation (已弃用，仅供参考)

```java
// Java 实现 - SafetyNet Attestation (Legacy)
import com.google.android.gms.safetynet.SafetyNet;
import com.google.android.gms.safetynet.SafetyNetApi;

public class SafetyNetChecker {

    private static final String API_KEY = "YOUR_API_KEY";

    public static void checkSafetyNet(Context context, SafetyNetCallback callback) {
        // 生成随机 nonce
        byte[] nonce = new byte[32];
        new SecureRandom().nextBytes(nonce);

        SafetyNet.getClient(context)
            .attest(nonce, API_KEY)
            .addOnSuccessListener(response -> {
                String jwsResult = response.getJwsResult();
                // 将 JWS 发送到服务器验证
                callback.onSuccess(jwsResult);
            })
            .addOnFailureListener(e -> {
                callback.onFailure(e);
            });
    }

    public interface SafetyNetCallback {
        void onSuccess(String jws);
        void onFailure(Exception e);
    }
}
```

---

## 5. 常见风控 SDK 分析

### 5.1 主流风控 SDK 特征

| SDK 名称 | 厂商 | 主要特征 | 检测能力 |
|----------|------|----------|----------|
| **同盾** | 同盾科技 | 设备指纹、行为分析 | Root/模拟器/篡改检测 |
| **阿里聚安全** | 阿里巴巴 | 多维度风控 | 完整风控体系 |
| **腾讯御安全** | 腾讯 | 终端安全、数据加密 | 加固+风控 |
| **网易易盾** | 网易 | 反外挂、反作弊 | 游戏场景优化 |
| **极验** | 极验科技 | 行为验证、验证码 | 人机识别 |
| **数美科技** | 数美 | 智能风控 | ML 驱动 |

### 5.2 SDK 检测绕过思路

```javascript
// Frida 脚本 - 通用风控 SDK 绕过框架
(function() {
    "use strict";

    console.log("[*] Risk Control SDK Bypass Framework");

    Java.perform(function() {
        // 1. 绕过设备指纹采集
        bypassDeviceFingerprint();

        // 2. 绕过环境检测
        bypassEnvironmentCheck();

        // 3. 绕过行为采集
        bypassBehaviorCollection();

        // 4. 绕过完整性校验
        bypassIntegrityCheck();
    });

    function bypassDeviceFingerprint() {
        console.log("[*] Bypassing device fingerprint...");

        // Hook Settings.Secure.getString
        var Settings = Java.use("android.provider.Settings$Secure");
        Settings.getString.overload(
            "android.content.ContentResolver",
            "java.lang.String"
        ).implementation = function(resolver, name) {
            if (name === "android_id") {
                // 返回固定或随机的 Android ID
                return generateFakeAndroidId();
            }
            return this.getString(resolver, name);
        };

        // Hook TelephonyManager
        var TelephonyManager = Java.use("android.telephony.TelephonyManager");

        TelephonyManager.getDeviceId.overload().implementation = function() {
            return generateFakeImei();
        };

        TelephonyManager.getSubscriberId.overload().implementation = function() {
            return generateFakeImsi();
        };

        // Hook NetworkInterface
        var NetworkInterface = Java.use("java.net.NetworkInterface");
        NetworkInterface.getHardwareAddress.implementation = function() {
            return generateFakeMac();
        };
    }

    function bypassEnvironmentCheck() {
        console.log("[*] Bypassing environment check...");

        // Root 检测绕过
        var File = Java.use("java.io.File");
        var rootPaths = ["/system/bin/su", "/system/xbin/su", "/sbin/su"];

        File.exists.implementation = function() {
            var path = this.getAbsolutePath();
            for (var i = 0; i < rootPaths.length; i++) {
                if (path.indexOf(rootPaths[i]) !== -1) {
                    return false;
                }
            }
            return this.exists();
        };

        // Build 属性修改
        var Build = Java.use("android.os.Build");
        Build.FINGERPRINT.value = "samsung/dreamltexx/dreamlte:9/PPR1.180610.011/G950FXXS5DSL1:user/release-keys";
        Build.TAGS.value = "release-keys";
        Build.TYPE.value = "user";
    }

    function bypassBehaviorCollection() {
        console.log("[*] Bypassing behavior collection...");

        // Hook 传感器数据采集
        var SensorManager = Java.use("android.hardware.SensorManager");

        SensorManager.registerListener.overload(
            "android.hardware.SensorEventListener",
            "android.hardware.Sensor",
            "int"
        ).implementation = function(listener, sensor, rate) {
            // 可以选择不注册或注册一个假的监听器
            console.log("[*] SensorManager.registerListener blocked");
            return true;  // 返回成功但不实际注册
        };

        // Hook 触摸事件采集
        // 这通常在 View 层实现，需要针对具体 SDK

        // Hook 位置信息采集
        var LocationManager = Java.use("android.location.LocationManager");
        LocationManager.getLastKnownLocation.overload("java.lang.String").implementation = function(provider) {
            console.log("[*] LocationManager.getLastKnownLocation blocked");
            return null;
        };
    }

    function bypassIntegrityCheck() {
        console.log("[*] Bypassing integrity check...");

        // Hook PackageManager 签名验证
        var PackageManager = Java.use("android.app.ApplicationPackageManager");

        PackageManager.getPackageInfo.overload("java.lang.String", "int").implementation = function(pkg, flags) {
            var info = this.getPackageInfo(pkg, flags);

            // 如果请求签名，可以返回原始签名
            if ((flags & 0x40) !== 0) {
                console.log("[*] Signature check intercepted for: " + pkg);
                // 这里可以替换签名
            }

            return info;
        };

        // Hook MessageDigest (用于校验)
        var MessageDigest = Java.use("java.security.MessageDigest");

        MessageDigest.digest.overload("[B").implementation = function(input) {
            // 检测是否是完整性校验
            // 可以根据调用栈判断
            return this.digest(input);
        };
    }

    // 辅助函数
    function generateFakeAndroidId() {
        // 生成看起来真实的 Android ID
        var chars = "0123456789abcdef";
        var result = "";
        for (var i = 0; i < 16; i++) {
            result += chars.charAt(Math.floor(Math.random() * chars.length));
        }
        return result;
    }

    function generateFakeImei() {
        // 生成符合 Luhn 校验的 IMEI
        var imei = "35";  // TAC 开头
        for (var i = 0; i < 12; i++) {
            imei += Math.floor(Math.random() * 10);
        }
        // 计算校验位
        imei += calculateLuhnCheckDigit(imei);
        return imei;
    }

    function generateFakeImsi() {
        // 中国移动 IMSI 示例
        return "460001234567890";
    }

    function generateFakeMac() {
        // 返回随机 MAC 地址字节数组
        var mac = [];
        for (var i = 0; i < 6; i++) {
            mac.push(Math.floor(Math.random() * 256));
        }
        return Java.array('byte', mac);
    }

    function calculateLuhnCheckDigit(number) {
        var sum = 0;
        var alternate = false;

        for (var i = number.length - 1; i >= 0; i--) {
            var n = parseInt(number.charAt(i), 10);
            if (alternate) {
                n *= 2;
                if (n > 9) n -= 9;
            }
            sum += n;
            alternate = !alternate;
        }

        return (10 - (sum % 10)) % 10;
    }

})();
```

---

## 6. 绕过策略总结

### 6.1 客户端绕过

| 检测类型 | 绕过方法 | 难度 | 持久性 |
|----------|----------|------|--------|
| Root 检测 | MagiskHide/DenyList | ⭐⭐ | 高 |
| Frida 检测 | 自定义端口/过滤 maps | ⭐⭐⭐ | 中 |
| 模拟器检测 | 修改 Build 属性 | ⭐⭐ | 高 |
| 签名校验 | Hook getPackageInfo | ⭐⭐ | 高 |
| 设备指纹 | Hook 采集函数 | ⭐⭐⭐ | 中 |
| SSL Pinning | Hook TrustManager | ⭐⭐ | 高 |

### 6.2 通信层绕过

| 防护类型 | 绕过方法 | 难度 |
|----------|----------|------|
| 请求签名 | 逆向签名算法 | ⭐⭐⭐⭐ |
| 防重放 | 模拟时间戳/nonce | ⭐⭐ |
| 协议加密 | 逆向加密算法 | ⭐⭐⭐⭐ |
| 证书固定 | 安装自定义证书 | ⭐⭐ |

### 6.3 最佳实践

```
┌─────────────────────────────────────────────────────────────────┐
│                      风控对抗最佳实践                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. 分层分析                                                    │
│     ├── 先观察网络请求，了解通信协议                             │
│     ├── 识别加密/签名参数                                       │
│     └── 定位关键函数                                            │
│                                                                 │
│  2. 环境准备                                                    │
│     ├── 使用 MagiskHide 隐藏 Root                               │
│     ├── 使用自定义端口的 Frida                                  │
│     └── 准备干净的测试设备/模拟器                               │
│                                                                 │
│  3. 动态分析                                                    │
│     ├── Hook 网络层函数追踪请求                                 │
│     ├── Hook 加密函数获取明文                                   │
│     └── Hook 签名函数获取算法                                   │
│                                                                 │
│  4. 静态辅助                                                    │
│     ├── 反编译定位关键代码                                      │
│     ├── 分析混淆后的算法逻辑                                    │
│     └── 提取密钥和配置                                          │
│                                                                 │
│  5. 验证测试                                                    │
│     ├── 使用脚本验证签名算法                                    │
│     ├── 模拟请求测试服务端响应                                  │
│     └── 长期运行测试稳定性                                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 7. 实战案例

### 7.1 某电商 App 签名算法还原

```python
# Python 实现 - 还原的签名算法示例
import hashlib
import hmac
import time
import json
import base64

class EcommerceAppSigner:
    """某电商 App 签名算法还原"""

    def __init__(self, app_key: str, app_secret: str, device_id: str):
        self.app_key = app_key
        self.app_secret = app_secret
        self.device_id = device_id

    def sign_request(self, api: str, params: dict) -> dict:
        """签名请求"""
        timestamp = int(time.time() * 1000)
        nonce = self._generate_nonce()

        # 1. 构建待签名参数
        sign_params = {
            'api': api,
            'appkey': self.app_key,
            'deviceid': self.device_id,
            'timestamp': str(timestamp),
            'nonce': nonce,
            **params
        }

        # 2. 参数排序
        sorted_keys = sorted(sign_params.keys())
        sign_str = '&'.join([
            f"{k}={sign_params[k]}" for k in sorted_keys
        ])

        # 3. HMAC-SHA256 签名
        signature = hmac.new(
            self.app_secret.encode('utf-8'),
            sign_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        # 4. 返回完整请求参数
        return {
            **sign_params,
            'sign': signature
        }

    def _generate_nonce(self) -> str:
        """生成随机数"""
        import random
        import string
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))


# 使用示例
signer = EcommerceAppSigner(
    app_key="your_app_key",
    app_secret="your_app_secret",
    device_id="your_device_id"
)

signed_params = signer.sign_request(
    api="product.list",
    params={"category": "electronics", "page": "1"}
)

print(json.dumps(signed_params, indent=2))
```

### 7.2 某社交 App 设备指纹绕过

```javascript
// Frida 脚本 - 某社交 App 设备指纹绕过
Java.perform(function() {
    console.log("[*] Hooking social app fingerprint...");

    // Hook 该 App 的设备信息采集类
    var DeviceInfo = Java.use("com.social.app.security.DeviceInfo");

    DeviceInfo.getAndroidId.implementation = function() {
        console.log("[*] getAndroidId called");
        return "a1b2c3d4e5f67890";  // 固定值
    };

    DeviceInfo.getDeviceModel.implementation = function() {
        return "SM-G950F";  // 伪装成三星 S8
    };

    DeviceInfo.isRooted.implementation = function() {
        console.log("[*] isRooted called, returning false");
        return false;
    };

    DeviceInfo.isEmulator.implementation = function() {
        console.log("[*] isEmulator called, returning false");
        return false;
    };

    // Hook 签名验证
    var SignatureVerifier = Java.use("com.social.app.security.SignatureVerifier");

    SignatureVerifier.verify.implementation = function(context) {
        console.log("[*] SignatureVerifier.verify called, returning true");
        return true;
    };

    console.log("[+] All hooks installed successfully");
});
```

---

## 总结

移动端安全与风控是一个持续对抗的领域。防御方不断升级检测手段，攻击方也在持续优化绕过技术。理解这些技术的原理，有助于：

1. **安全研究人员**: 评估应用的安全性
2. **开发人员**: 设计更健壮的防护方案
3. **逆向工程师**: 更高效地分析和绕过防护

关键是要建立**分层防御**的思维，单一检测点很容易被绕过，需要多维度、多层次的综合防护。

---

## 扩展阅读

### 学术论文

以下是与移动端安全和风控技术相关的学术论文，可以帮助深入理解该领域的技术原理：

**设备指纹与用户识别**

| 论文标题 | 主题 | arXiv 链接 |
|----------|------|------------|
| *Device Fingerprinting: A Comprehensive Survey* | 设备指纹技术综述 | [arXiv:2311.01344](https://arxiv.org/abs/2311.01344) |
| *Fingerprinting Mobile Devices Using Personalized Configurations* | 移动设备指纹识别 | [arXiv:1708.09109](https://arxiv.org/abs/1708.09109) |
| *Cross-Browser Fingerprinting via OS and Hardware Level Features* | 跨浏览器指纹 | [arXiv:1503.01408](https://arxiv.org/abs/1503.01408) |

**机器人检测与反爬虫**

| 论文标题 | 主题 | arXiv 链接 |
|----------|------|------------|
| *Bot Detection in Social Networks: A Survey* | 社交网络机器人检测综述 | [arXiv:2005.12963](https://arxiv.org/abs/2005.12963) |
| *A Survey on Deep Learning Based Bot Detection Techniques* | 深度学习机器人检测 | [arXiv:2301.10912](https://arxiv.org/abs/2301.10912) |
| *Detecting and Characterizing Web Bot Traffic in a Large E-commerce Platform* | 电商平台机器人流量检测 | [arXiv:2003.02595](https://arxiv.org/abs/2003.02595) |

**移动应用安全**

| 论文标题 | 主题 | arXiv 链接 |
|----------|------|------------|
| *A Survey on Security and Privacy of Android Applications* | Android 应用安全综述 | [arXiv:2101.06298](https://arxiv.org/abs/2101.06298) |
| *Android Malware Detection: A Survey* | Android 恶意软件检测综述 | [arXiv:1904.05999](https://arxiv.org/abs/1904.05999) |
| *Deep Learning for Android Malware Detection* | 深度学习恶意软件检测 | [arXiv:1802.03316](https://arxiv.org/abs/1802.03316) |
| *RASP: Runtime Application Self-Protection* | RASP 运行时保护 | [arXiv:1907.04093](https://arxiv.org/abs/1907.04093) |

**行为分析与异常检测**

| 论文标题 | 主题 | arXiv 链接 |
|----------|------|------------|
| *Deep Learning for Anomaly Detection: A Survey* | 异常检测深度学习综述 | [arXiv:1901.03407](https://arxiv.org/abs/1901.03407) |
| *User Behavior Analysis for Security Applications* | 用户行为安全分析 | [arXiv:2006.04559](https://arxiv.org/abs/2006.04559) |
| *Continuous Authentication via Behavioral Biometrics* | 行为生物特征认证 | [arXiv:2003.06494](https://arxiv.org/abs/2003.06494) |

**风控与欺诈检测**

| 论文标题 | 主题 | arXiv 链接 |
|----------|------|------------|
| *A Survey of Credit Card Fraud Detection Techniques* | 信用卡欺诈检测综述 | [arXiv:2007.07373](https://arxiv.org/abs/2007.07373) |
| *Financial Fraud Detection: A Machine Learning Perspective* | 金融欺诈 ML 检测 | [arXiv:2009.07136](https://arxiv.org/abs/2009.07136) |
| *Graph Neural Networks for Fraud Detection* | 图神经网络欺诈检测 | [arXiv:2007.02402](https://arxiv.org/abs/2007.02402) |

**逆向工程与代码保护**

| 论文标题 | 主题 | arXiv 链接 |
|----------|------|------------|
| *A Survey on Software Obfuscation and Deobfuscation* | 代码混淆与反混淆综述 | [arXiv:1710.01236](https://arxiv.org/abs/1710.01236) |
| *Machine Learning for Reverse Engineering* | 机器学习逆向工程 | [arXiv:2009.12120](https://arxiv.org/abs/2009.12120) |
| *Binary Code Analysis: A Survey* | 二进制代码分析综述 | [arXiv:2205.03454](https://arxiv.org/abs/2205.03454) |

### 推荐阅读顺序

对于不同背景的读者，建议按以下顺序阅读：

**安全研究员**：
1. *A Survey on Security and Privacy of Android Applications* - 了解整体安全态势
2. *Device Fingerprinting: A Comprehensive Survey* - 理解设备识别技术
3. *RASP: Runtime Application Self-Protection* - 学习防护技术

**风控工程师**：
1. *Bot Detection in Social Networks: A Survey* - 机器人检测基础
2. *Deep Learning for Anomaly Detection: A Survey* - 异常检测方法
3. *Financial Fraud Detection: A Machine Learning Perspective* - 风控模型设计

**逆向工程师**：
1. *A Survey on Software Obfuscation and Deobfuscation* - 混淆技术原理
2. *Binary Code Analysis: A Survey* - 二进制分析技术
3. *Android Malware Detection: A Survey* - 恶意软件分析

---

**相关章节**：
- [R17: 设备指纹与绕过](device_fingerprinting_and_bypass.md)
- [C01: 反分析技术案例](../../03-Case-Studies/case_anti_analysis_techniques.md)
- [R26: 验证码绕过技术](captcha_bypassing_techniques.md)
