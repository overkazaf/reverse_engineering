# C 代码：用于运行时仿真与设备指纹生成

在逆向工程中，直接使用 C/C++ 编写一些辅助工具或重现目标逻辑是一种非常高效的策略。这可以帮助我们脱离复杂的 App 环境，对核心算法进行独立的测试、Fuzzing 或仿真。

---

## 1. 运行时仿真 (Runtime Emulation)

当我们在 SO 文件中定位到一个关键的核心算法（如自定义加密、签名生成）后，如果该算法逻辑清晰且依赖较少，最好的方法就是将其逻辑用 C/C++ "翻译"一遍。

### 场景示例：重现一个简单的 XOR 加密算法

假设在 IDA Pro 中看到如下伪代码：

```c
// Decompiled pseudo-code from IDA
void encrypt_data(char* data, int len) {
    for (int i = 0; i < len; ++i) {
        data[i] = (data[i] ^ 0x5A) + 5;
    }
}
```

### 重现与验证代码

```c
// emulate_encrypt.c
#include <stdio.h>
#include <string.h>
#include <stdint.h>

// Re-implementation of the encryption algorithm
void simulate_encrypt(char* data, size_t len) {
    for (size_t i = 0; i < len; ++i) {
        data[i] = (data[i] ^ 0x5A) + 5;
    }
}

// Corresponding decryption for our own testing
void simulate_decrypt(char* data, size_t len) {
    for (size_t i = 0; i < len; ++i) {
        data[i] = (data[i] - 5) ^ 0x5A;
    }
}

// Helper function: Print hexadecimal
void print_hex(const char* label, uint8_t* data, size_t len) {
    printf("%s: ", label);
    for (size_t i = 0; i < len; i++) {
        printf("%02x ", data[i]);
    }
    printf("\n");
}

int main() {
    char my_data[] = "this_is_a_test_message";
    size_t len = strlen(my_data);

    printf("=== XOR Encryption Algorithm Test ===\n\n");
    printf("Original: %s\n", my_data);
    print_hex("Original HEX", (uint8_t*)my_data, len);
    printf("\n");

    // Encrypt it
    simulate_encrypt(my_data, len);
    printf("After encryption:\n");
    print_hex("Encrypted HEX", (uint8_t*)my_data, len);
    printf("\n");

    // Decrypt it
    simulate_decrypt(my_data, len);
    printf("After decryption: %s\n", my_data);
    print_hex("Decrypted HEX", (uint8_t*)my_data, len);

    return 0;
}
```

### 编译与运行

```bash
# 编译
gcc emulate_encrypt.c -o emulate

# 运行
./emulate

# 输出:
# === XOR Encryption Algorithm Test ===
#
# Original: this_is_a_test_message
# Original HEX: 74 68 69 73 5f 69 73 5f 61 5f 74 65 73 74 5f 6d ...
#
# After encryption:
# Encrypted HEX: 29 37 38 2e 0a 38 2e 0a 3e 0a 29 3a 2e 29 0a 32 ...
#
# After decryption: this_is_a_test_message
```

---

## 2. 设备指纹生成 (Device Fingerprint Generation)

许多 App 会通过读取 Android 系统的 `build.prop` 或其他系统属性来生成设备指纹，用于识别和跟踪设备。在进行自动化操作时，我们需要能够模拟这些指纹。

`getprop` 是 Android shell 中的一个命令，可以读取系统属性。我们也可以用 C 代码在 Native 层实现类似的功能，从而生成可以乱真的指纹数据。

### 场景示例：用 C 读取关键设备属性并生成 JSON

```c
// device_fingerprint.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

// A simple wrapper to execute a shell command and get its output
// In a real scenario, you might use direct system calls for better performance/stealth
char* get_prop(const char* key) {
    char command[256];
    snprintf(command, sizeof(command), "getprop %s", key);

    FILE* fp = popen(command, "r");
    if (fp == NULL) {
        return NULL;
    }

    char* line = malloc(256);
    if (fgets(line, 256, fp) == NULL) {
        free(line);
        pclose(fp);
        return NULL;
    }

    // Remove trailing newline
    line[strcspn(line, "\n")] = 0;
    pclose(fp);
    return line;
}

int main() {
    // List of properties we want to fetch
    const char* props_to_fetch[] = {
        "ro.product.brand",
        "ro.product.model",
        "ro.product.manufacturer",
        "ro.product.device",
        "ro.build.version.release",
        "ro.build.version.sdk",
        "ro.build.fingerprint",
        "ro.serialno",
        "ro.boot.serialno"
    };
    int num_props = sizeof(props_to_fetch) / sizeof(props_to_fetch[0]);

    printf("{\n");
    printf("  \"timestamp\": %ld,\n", time(NULL));
    printf("  \"device\": {\n");

    for (int i = 0; i < num_props; ++i) {
        char* value = get_prop(props_to_fetch[i]);
        if (value) {
            // Extract last part of property name for cleaner key
            const char* last_dot = strrchr(props_to_fetch[i], '.');
            const char* key = last_dot ? last_dot + 1 : props_to_fetch[i];

            printf("    \"%s\": \"%s\"", key, value);
            if (i < num_props - 1) {
                printf(",");
            }
            printf("\n");
            free(value);
        }
    }

    printf("  }\n");
    printf("}\n");

    return 0;
}
```

### 编译与运行

使用 Android NDK 进行交叉编译：

```bash
# 设置 NDK 路径 (根据实际安装位置修改)
export NDK_PATH=~/Android/Sdk/ndk/25.1.8937393

# 编译 (arm64 架构)
$NDK_PATH/toolchains/llvm/prebuilt/linux-x86_64/bin/aarch64-linux-android21-clang \
    device_fingerprint.c -o fingerprint

# 推送到设备
adb push fingerprint /data/local/tmp/
adb shell chmod +x /data/local/tmp/fingerprint

# 运行
adb shell /data/local/tmp/fingerprint
```

### 输出示例

```json
{
  "timestamp": 1734518400,
  "device": {
    "brand": "google",
    "model": "Pixel 5",
    "manufacturer": "Google",
    "device": "redfin",
    "release": "13",
    "sdk": "33",
    "fingerprint": "google/redfin/redfin:13/TQ3A.230901.001/10750268:user/release-keys",
    "serialno": "XXXXXXXXXX"
  }
}
```

---

## 3. 更复杂的算法仿真

### 示例：HMAC-SHA256 签名仿真

```c
// hmac_sign.c
#include <stdio.h>
#include <string.h>
#include <openssl/hmac.h>
#include <openssl/sha.h>

void hmac_sha256(const char* key, const char* data, unsigned char* result) {
    unsigned int len = 32;
    HMAC(EVP_sha256(),
         key, strlen(key),
         (unsigned char*)data, strlen(data),
         result, &len);
}

void print_hex(unsigned char* data, size_t len) {
    for (size_t i = 0; i < len; i++) {
        printf("%02x", data[i]);
    }
    printf("\n");
}

int main() {
    const char* key = "secret_key_12345";
    const char* data = "user=test&timestamp=1234567890";

    unsigned char result[32];
    hmac_sha256(key, data, result);

    printf("HMAC-SHA256 Signature:\n");
    print_hex(result, 32);

    return 0;
}
```

### 编译

```bash
# 需要链接 OpenSSL
gcc hmac_sign.c -o hmac_sign -lssl -lcrypto

# 运行
./hmac_sign
```

---

## 4. 使用 Unidbg 进行 SO 仿真

对于复杂的 Native 算法，可以使用 Unidbg 进行完整仿真，而不需要手动翻译代码。

```java
// Java 代码示例 (Unidbg)
import com.github.unidbg.AndroidEmulator;
import com.github.unidbg.linux.android.AndroidEmulatorBuilder;
import com.github.unidbg.linux.android.dvm.DalvikModule;
import com.github.unidbg.linux.android.dvm.VM;

public class EmulatorExample {
    private AndroidEmulator emulator;
    private VM vm;
    private DalvikModule dm;

    public EmulatorExample() {
        // 创建模拟器
        emulator = AndroidEmulatorBuilder
            .for64Bit()
            .setProcessName("com.example.app")
            .build();

        // 创建虚拟机
        vm = emulator.createDalvikVM();

        // 加载 SO 文件
        dm = vm.loadLibrary("libnative-lib.so", false);

        // 调用 JNI_OnLoad
        dm.callJNI_OnLoad(emulator);
    }

    public String callEncrypt(String input) {
        // 调用 Native 方法
        // ... (具体实现取决于目标函数签名)
        return "";
    }
}
```

---

## 总结

使用 C/C++ 进行运行时仿真的优势：

1. **独立测试**: 脱离 App 环境，可以快速迭代测试
2. **便于 Fuzzing**: 可以对算法进行大规模模糊测试
3. **性能优越**: 相比在 App 内 Hook，独立运行效率更高
4. **便于分享**: 可以将仿真代码分享给团队其他成员

在实践中，建议结合动态分析（Frida Hook）和静态分析（IDA Pro）的结果，逐步完善仿真代码，直到输出与目标函数完全一致。
