# 使用静态分析定位 Android App 的关键逻辑

## 问题场景

**你遇到了什么问题？**

- 你想找到 App 的加密/签名算法，但代码太多不知道从哪里开始
- 你想理解 App 的完整业务逻辑，包括所有分支和边界条件
- 你想寻找安全漏洞，比如硬编码密钥、逻辑缺陷
- 你想在没有运行环境的情况下分析 APK
- 你想进行批量自动化分析

**本配方教你**：系统性地使用静态分析工具（jadx, IDA Pro, Ghidra）快速定位关键代码、追踪数据流、识别加密算法。

**核心理念**：

> **静态分析：不运行代码，看清全局**
>
> - 静态分析能看到所有代码路径（包括未触发的分支）
> - 适合理解完整算法和寻找漏洞
> - 先动态获取线索，再静态深入分析
> - 交替迭代：动态发现 → 静态验证 → 动态测试

**预计用时**: 40-90 分钟

---

## 工具清单

### 必需工具

- **jadx-gui** - Java/Smali 反编译
- **IDA Pro / Ghidra** - Native 层分析
- **文本编辑器** - 记录分析笔记

### 可选工具

- **Binary Ninja** - 可视化 CFG
- **FindCrypt** (IDA 插件) - 识别加密算法
- **YARA** - 模式匹配
- **angr** - 符号执行（高级）

---

## 前置条件

### 确认清单

```bash
# 1. jadx-gui 已安装
jadx-gui --version

# 2. IDA Pro or Ghidra 可用
# IDA Pro: 商业软件
# Ghidra: 免费，下载自 https://ghidra-sre.org/

# 3. APK 文件已解压
unzip app.apk -d app_unzipped
```

### 静态 vs 动态：何时选择什么？

| 你的目标                       | 推荐起点 | 理由                               |
| ------------------------------ | -------- | ---------------------------------- |
| **快速提取结果**（如加密参数） | 动态优先 | 直接 Hook 拿结果，不必理解全部逻辑 |
| **理解完整算法**（如协议逆向） | 静态优先 | 需要看清所有分支和边界条件         |
| **寻找漏洞**                   | 静态优先 | 需要覆盖所有代码路径，包括错误处理 |
| **对抗混淆/加壳**              | 动态优先 | 静态分析可能完全失效，先动态脱壳   |
| **批量自动化**                 | 静态优先 | 动态分析需要运行环境，静态可离线   |

**最佳实践**：

1. **先动态获取线索** - 用 Frida 快速定位关键函数
2. **再静态深入分析** - 有了"地图"后更有方向性
3. **交替迭代** - 动态发现的疑点用静态验证

---

## 解决方案

### 第 1 步：确定分析目标（5 分钟）

**明确你想找什么**：

- API 签名算法
- 加密密钥位置
- 网络协议逻辑
- 特定功能实现（如登录、支付）
- 安全漏洞

**示例**：假设目标是找到 API 请求的签名逻辑

### 第 2 步：从字符串入手（10 分钟）

**最有效的起点**：搜索关键字符串

#### 2.1 jadx-gui 字符串搜索

在 jadx-gui 中使用 `Ctrl+Shift+F` 搜索以下关键词：

```text
md5
sha
hmac
key
secret
encrypt
sign
```

找到可疑代码后分析调用关系：

```java
HashMap<String, String> params = new HashMap<>();
params.put("sign", generateSign(data));
```

### 第 3 步：交叉引用分析（10 分钟）

#### 3.1 查找函数调用者

**在 jadx-gui 中**：

1. 右键点击 `generateSign` 函数
2. 选择 **"Find Usage"** 或按 `X`
3. 查看所有调用点

**在 IDA Pro 中**：

1. 光标移到函数名
2. 按 `X` 键
3. 查看 **Xrefs to**（被谁调用）和 **Xrefs from**（调用了谁）

#### 3.2 向上追溯调用链

```text
RequestBuilder.buildParams()
       ↓
SignUtils.generateSign()  ← 目标函数
```

分析签名函数的实现：

```java
public static String generateSign(Map<String, String> params) {
    // Step 1: Sort parameters
    TreeMap<String, String> sortedParams = new TreeMap<>(params);

    // Step 2: Concatenate string
    StringBuilder sb = new StringBuilder();
    for (Map.Entry<String, String> entry : sortedParams.entrySet()) {
        sb.append(entry.getKey()).append("=").append(entry.getValue()).append("&");
    }
    sb.append("key=").append(SECRET_KEY);

    // Step 3: Calculate MD5
    return MD5.encode(sb.toString());
}
```

---

### 第 4 步：数据流分析（15 分钟）

**目标**：追踪 `SECRET_KEY` 的来源

#### 4.1 查找变量定义

**在 jadx 中**：

1. 点击 `SECRET_KEY`
2. Ctrl+Click 跳转到定义

**可能的情况**：

<details>
<summary><b>情况 1: 硬编码（最简单）</b></summary>

```java
private static final String SECRET_KEY = "abc123def456";
```

直接拿到密钥！

</details>

<details>
<summary><b>情况 2: 从配置文件读取</b></summary>

```java
static {
    try {
        Properties props = new Properties();
        props.load(context.getAssets().open("config.properties"));
        SECRET_KEY = props.getProperty("api.secret");
    } catch (IOException e) {
        SECRET_KEY = null;
    }
}
```

需要检查配置文件：

```bash
cat app_unzipped/assets/config.properties
```

</details>

<details>
<summary><b>情况 3: 从 Native 层获取</b></summary>

```java
static {
    System.loadLibrary("native-lib");
    SECRET_KEY = getKeyFromNative();
}

private static native String getKeyFromNative();
```

需要分析 SO 文件。

</details>

#### 4.2 在 Ghidra 中追踪数据流

在 Ghidra 反编译窗口：

1. 双击变量名
2. 所有使用该变量的地方会高亮显示
3. 追踪变量在函数内的流动

---

### 第 5 步：Native 层分析（20 分钟）

如果关键逻辑在 SO 文件中。

#### 5.1 定位 Native 函数

**在 jadx 中找到 JNI 声明**：

```java
public native String encrypt(String plaintext);
```

**找到对应的 SO 文件**：

```bash
ls app_unzipped/lib/arm64-v8a/
# libnative-lib.so

# 用 IDA Pro 打开
```

#### 5.2 在 IDA Pro 中定位函数

使用函数窗口搜索：

1. **View → Open Subviews → Functions**
2. 搜索 `Java_com_example` 前缀
3. 双击跳转到函数

或使用 Exports 窗口：

1. **View → Open Subviews → Exports**
2. 搜索函数名
3. 双击跳转

#### 5.3 分析函数逻辑

**示例反编译代码**（IDA/Ghidra）：

```c
jstring Java_com_example_CryptoUtils_encrypt(JNIEnv *env, jobject obj, jstring plaintext) {
    const char *plain = (*env)->GetStringUTFChars(env, plaintext, 0);

    // AES encryption
    unsigned char key[16] = {0x12, 0x34, 0x56, 0x78, ...};
    unsigned char iv[16] = {0x00, 0x00, 0x00, 0x00, ...};

    unsigned char *encrypted = aes_encrypt(plain, key, iv);

    jstring result = (*env)->NewStringUTF(env, encrypted);
    (*env)->ReleaseStringUTFChars(env, plaintext, plain);

    return result;
}
```

**提取信息**：

- 密钥：`{0x12, 0x34, 0x56, 0x78, ...}`
- IV：`{0x00, 0x00, ...}`

---

### 第 6 步：识别加密算法（10 分钟）

#### 6.1 使用 FindCrypt 插件（IDA Pro）

**安装**：

```bash
# 下载
git clone https://github.com/polymorf/findcrypt-yara.git

# 复制到 IDA 插件目录
cp findcrypt3.py $IDA_PATH/plugins/
```

运行插件后会自动标记识别到的加密常量。

#### 6.2 手动识别

**常见加密算法特征**：

| 算法    | 特征常量（十六进制）                   |
| ------- | -------------------------------------- |
| AES     | `63 7C 77 7B F2 6B 6F C5` (S-Box)      |
| MD5     | `67 45 23 01 EF CD AB 89` (初始化向量) |
| SHA-1   | `67 45 23 01 EF CD AB 89 98 BA DC FE`  |
| SHA-256 | `428A2F98 71374491 B5C0FBCF`           |
| DES     | 固定的 S-Box 和 P-Box 表               |

**在 IDA 中搜索**：使用 `Alt+B`（二进制搜索）查找特征字节。

---

### 第 7 步：控制流图分析（10 分钟）

**用途**：理解复杂函数的逻辑结构

#### 7.1 查看 CFG

**IDA Pro**：按 `Space` 键切换到图形视图。

**示例登录流程图**：

```text
[检查用户名] --No--> [返回错误 1]
     ↓ Yes
[检查密码长度] --No--> [返回错误 2]
     ↓ Yes
[加密密码]
     ↓
[发送网络请求]
     ↓
[解析响应] --Failed--> [返回错误 3]
     ↓ Success
[保存 Token]
     ↓
[返回成功]
```

#### 7.2 交叉引用图

**Xrefs to**（被谁调用）：

```text
      LoginActivity.login()
              ↓
      SignUtils.generateSign()
```

**Xrefs from**（调用了谁）：

```text
SignUtils.generateSign()
              ↓
      → MD5.encode()
      → Base64.encode()
```

---

## 常见问题

### 问题 1: jadx 反编译失败

**症状**：打开 APK 后显示错误或代码不完整

**解决**：

1. **尝试不同版本的 jadx**
    ```bash
    # 使用最新版
    wget https://github.com/skylot/jadx/releases/download/v1.4.7/jadx-1.4.7.zip
    ```
2. **调整 jadx 设置**
    - 禁用 "Deobfuscation"
    - 禁用 "Inline methods"
3. **查看 Smali 代码**
    ```bash
    # 使用 apktool
    apktool d app.apk -o app_smali
    ```

### 问题 2: 找不到关键字符串

**可能原因**：

1. **字符串被加密/混淆**
    - 在运行时动态解密
    - **解决**：用 Frida Hook 查看运行时字符串
2. **字符串在 Native 层**
    ```bash
    # 在 SO 文件中搜索
    strings libnative-lib.so | grep "sign"
    ```
3. **字符串被拆分**
    ```java
    // Code might be
    String key = "sec" + "ret" + "key";
    ```

### 问题 3: IDA Pro 没有自动识别函数

**症状**：打开 SO 文件后只看到数据，没有函数

**解决**：

1. **手动创建函数**

   - 按 'P' 键创建函数
   - 按 'C' 键转换为代码

2. **使用自动分析**

   - 勾选 "Create Functions"
   - 勾选 "Analyze Code"

3. **检查是否被混淆**
   - OLLVM 控制流平坦化
   - 参考：[OLLVM 反混淆](./ollvm_deobfuscation.md)

### 问题 4: 代码太复杂看不懂

**策略**：

1. **重命名变量和函数**
    ```text
    IDA: 按 'N' 键重命名
    Ghidra: 右键 → Rename
    ```
    ```java
    // Original
    String a = b(c, d);

    // After renaming
    String encryptedData = encrypt(plaintext, key);
    ```
2. **添加注释**
    ```text
    IDA: 按 ';' 键添加注释
    Ghidra: 右键 → Set Comment
    ```
3. **分段理解**
    - 一次只分析一个功能
    - 画流程图记录逻辑

### 问题 5: 如何验证静态分析结果？

**方法 1：使用 CyberChef**

访问 https://gchq.github.io/CyberChef/ 测试加密算法。

**方法 2：Python 重现**

```python
import hashlib

def generate_sign(params, secret_key):
    # 从静态分析复制的逻辑
    sorted_params = sorted(params.items())
    sign_str = '&'.join([f'{k}={v}' for k, v in sorted_params])
    sign_str += f'&key={secret_key}'
    return hashlib.md5(sign_str.encode()).hexdigest()

# 测试
params = {'user': 'test', 'timestamp': '1234567890'}
secret = 'abc123'
print(generate_sign(params, secret))
```

**方法 3：Frida 对比**

```javascript
Java.perform(function () {
  var SignUtils = Java.use("com.example.SignUtils");
  var HashMap = Java.use("java.util.HashMap");

  var params = HashMap.$new();
  params.put("user", "test");
  params.put("timestamp", "1234567890");

  var sign = SignUtils.generateSign(params);
  console.log("[*] 签名结果:", sign);
});
```

---

## 延伸阅读

### 相关配方

- **[逆向工程工作流](./re_workflow.md)** - 完整的分析流程
- **[密码学分析](../Network/crypto_analysis.md)** - 加密算法识别
- **[OLLVM 反混淆](./ollvm_deobfuscation.md)** - 处理混淆代码

### 工具深入

- **[IDA Pro 使用指南](../../02-Tools/Static/ida_pro_guide.md)**
- **[Ghidra 使用指南](../../02-Tools/Static/ghidra_guide.md)**

### 在线资源

| 资源            | 链接                                                     |
| --------------- | -------------------------------------------------------- |
| IDA Pro 教程    | https://www.hex-rays.com/products/ida/support/tutorials/ |
| Ghidra 官方手册 | https://ghidra-sre.org/docs/                             |
| FindCrypt 插件  | https://github.com/polymorf/findcrypt-yara               |

### 理论基础

- **[ARM 汇编基础](../../04-Reference/Foundations/arm_assembly.md)**
- **[DEX 文件格式](../../04-Reference/Foundations/dex_format.md)**
- **[ELF 文件格式](../../04-Reference/Foundations/so_elf_format.md)**

---

## 快速参考

### jadx 快捷键

| 快捷键         | 功能              |
| -------------- | ----------------- |
| `Ctrl+Shift+F` | 全局搜索          |
| `Ctrl+F`       | 当前文件搜索      |
| `X`            | 查找用法（Xrefs） |
| `Ctrl+Click`   | 跳转到定义        |
| `Alt+←`        | 后退              |
| `F5`           | 重新反编译        |

### IDA Pro 快捷键

| 快捷键      | 功能              |
| ----------- | ----------------- |
| `X`         | 交叉引用          |
| `N`         | 重命名            |
| `;`         | 添加注释          |
| `Space`     | 切换图形/文本视图 |
| `G`         | 跳转到地址        |
| `P`         | 创建函数          |
| `C`         | 转换为代码        |
| `A`         | 转换为字符串      |
| `Shift+F12` | 查看字符串        |
| `Alt+T`     | 文本搜索          |
| `Alt+B`     | 二进制搜索        |

### 分析流程模板

```text
1. 分析目标: _______________
2. 入口点: _______________
3. 关键函数: _______________
4. 调用链:
   _______________ → _______________ → _______________
5. 关键变量:
   - 名称: _______________
   - 类型: _______________
   - 来源: _______________
6. 算法识别: _______________
7. 验证结果: _______________
8. 下一步: _______________
```

---

**成功定位关键逻辑了吗？** 现在你可以理解 App 的核心算法了！

下一步推荐：[动态分析深入](./dynamic_analysis_deep_dive.md)（验证和测试你的发现）
