# 主流 App 加密签名机制案例

> **📚 前置知识**
>
> 本案例涉及以下核心技术，建议先阅读相关章节：
>
> - **[密码学分析](../01-Recipes/Network/crypto_analysis.md)** - 理解 sign 签名机制和常见哈希算法
> - **[网络抓包](../01-Recipes/Network/network_sniffing.md)** - 拦截并分析 API 请求中的加密字段

对主流 App 的 API 加密机制进行逆向分析，是检验和应用逆向工程综合能力的最佳实战。本案例研究将以常见的电商和社交类 App 为例，剖析其网络请求中核心加密字段和签名的生成逻辑，展示理论知识在实战中的应用。

> **免责声明**: 本文内容基于公开技术和过往分析经验的总结，旨在技术交流与学习。具体的加密实现会频繁更新，本文不保证与线上最新版本完全一致。

---

## 目录

- [通用加密与签名模式](#通用加密与签名模式)
- [案例分析 1：电商 App (类某多多模式)](#案例分析-1电商-app-类某多多模式)
- [案例分析 2：社交 App (类某红书模式)](#案例分析-2社交-app-类某红书模式)
- [案例分析 3：某节跳动系 (某音/TikTok)](#案例分析-3某节跳动系-某音tiktok)
- [案例分析 4：某手](#案例分析-4某手)
- [案例分析 5：某团](#案例分析-5某团)
- [案例分析 6：某里系 (某宝、某付宝)](#案例分析-6某里系-某宝某付宝)
- [逆向分析通用策略](#逆向分析通用策略)
- [高级策略：黑盒 RPC 调用详解](#高级策略黑盒-rpc-调用详解)

---

## 通用加密与签名模式

在分析具体案例前，我们先了解几种行业内通用的 API 保护模式：

- **请求体加密**：对整个 POST Body 进行对称（AES）或非对称（RSA）加密，保护数据内容隐私。

- **参数级加密**：仅对请求中的个别敏感字段（如密码、手机号）进行加密。

- **`sign` 签名机制**：**最核心、最普遍的模式**。通过对请求参数、时间戳、随机数等进行组合和哈希，生成一个签名值。服务器端会以同样的方式计算签名并进行比对，用于：
  - **防篡改**：确保传输过程中的数据未被修改。
  - **防重放**：通过加入时间戳或 Nonce，让签名一次有效。
  - **身份认证**：验证请求是否由合法的客户端发出。

---

## 案例分析 1：电商 App (类某多多模式)

### 核心风控字段 (`anti_content`)

- **现象**: 在其 API 请求中，经常能看到一个名为 `anti_content` 的、内容极长的加密字段。

- **本质**: 它并非简单的 API 参数签名，而是一个由客户端 SDK 生成的、高度复杂的**风控数据包**。它更侧重于**识别"人"与"机器"**，而非认证 API 调用本身。

- **可能包含的内容**:
  - **设备指纹**: 包含之前文档中提到的几乎所有硬件、软件和系统特征。
  - **环境检测**: 是否 Root、是否越狱、是否使用了 Hook 框架 (Frida/Xposed)、是否在模拟器中运行。
  - **传感器数据**: 在特定时间段内采集的加速度计、陀螺仪数据，用于判断设备是否在正常物理状态下。
  - **行为数据**：用户的点击坐标、滑动轨迹等。

- **逆向挑战**: `anti_content` 的生成逻辑通常被封装在高度混淆的原生 SO 库中，并可能包含 `SVC` 系统调用等反分析技术。完整复现其算法的难度极高。

### API 认证签名 (`sign`)

- **现象**: 除了 `anti_content`，请求参数中还有一个相对独立的 `sign` 字段。

- **目的**: 这个字段才是真正用于 API 级别认证的签名。

- **典型生成逻辑**:
  1. 收集所有请求参数（GET Query Params 和 POST Form Body Params）。
  2. 剔除 `sign` 字段本身。
  3. 按参数名的 ASCII 字母顺序进行排序。
  4. 将排序后的参数拼接成 `key=value&...` 的字符串（空值参数可能不参与拼接）。
  5. 在拼接好的字符串**前后**或**中间**插入一个固定的密钥（App Secret / Salt），这个密钥通常硬编码在 SO 文件中。
  6. 对最终的字符串进行 MD5 或 HMAC-SHA256 哈希，得到签名值。

---

## 案例分析 2：社交 App (类某红书模式)

### 复杂的请求头签名 (`X-Sign`)

- **现象**: 认证信息不放在 URL 参数中，而是位于 HTTP 请求头，如 `X-Sign`, `X-T` (时间戳), `X-B3-TraceId` 等。

- **`X-Sign` 的构成**:
  - **格式**: 通常是 `MD5(some_string)` 的形式。
  - **`some_string` 的拼接方式**: `URL Path + Sorted Query Params + (POST Body Hash) + Token/Salt`。
    - 这意味着，不仅 URL 参数，连 POST 的内容也参与了签名计算。
    - 有时还会包含其他请求头的值。

- **动态 Salt**: 其签名用的密钥可能不是固定的，而是部分由服务器下发，或与时间戳、设备信息动态生成，这使得暴力破解和简单模拟请求变得非常困难。

### 设备信息上报 (`X-DeviceInfo`)

- **现象**: 有一个专门的请求头，如 `X-DeviceInfo`，其内容是加密或 Base64 编码后的 JSON 字符串，里面是详细的设备指纹信息。

- **关联性**: 服务端的风控系统会将 `X-Sign` 和 `X-DeviceInfo` 进行强关联校验。
  - 首先验证 `X-Sign` 是否合法。
  - 然后解码 `X-DeviceInfo`，分析设备是否可信。
  - 最后，可能会交叉验证，例如，某个版本的 App 是否可能运行在某个特定的 Android SDK 版本上，如果不匹配，则判定为异常。

---

## 案例分析 3：某节跳动系 (某音/TikTok)

- **现象**: 其 API 请求中包含多个复杂的自定义请求头，如 `X-Gorgon`, `X-Khronos`, `X-Argus`, `X-Ladon`。请求体通常是经过 Protobuf 序列化后再加密的二进制数据。

- **核心逻辑**:
  - **设备注册**: App 首次启动时会进行设备注册 (`/service/2/device_register/`)，获取服务器下发的 `device_id` 和 `install_id`。这两个 ID 是后续所有业务请求的身份基础。
  - **多重签名系统**: `X-Gorgon` 是最核心的 API 请求签名，它将 URL、Cookie、POST Body 的哈希、设备指纹信息等多种因素混合计算而成。`X-Khronos` 是加密过的时间戳。这套体系确保了请求的来源、时效和完整性都可被验证。
  - **Protobuf 序列化**: 大量使用 Protobuf 进行数据交换，相比 JSON，它更高效，但也增加了逆向难度，因为分析者需要先找到或还原 `.proto` 文件才能理解数据结构。
  - **Cronet 网络库**: 使用 Google 的 Cronet 网络库进行网络请求，这使得常规的 OkHttp Hook 方法失效，必须深入到更底层的 `cronet.so` 或系统网络调用层面去进行 Hook。

- **逆向挑战**:
  - **虚拟机保护 (VMP)**: 其核心 SO 库（如 `libmetasec_ml.so`, `libmsaoaidsec.so`）使用了行业顶级的 VMP 或其自研的虚拟机保护技术。这会将原始的 ARM 指令转换成虚拟机自定义的字节码，导致 IDA 等工具无法进行静态分析。
  - **算法快速迭代**: 签名算法几乎每个版本都在变化，增加了长期维护的难度。
  - **分析策略**: 鉴于 VMP 的存在，完全还原签名算法几乎是不可能的。业界主流的策略是**放弃算法还原，转向 RPC 调用**。即通过 Frida 等工具找到 SO 中负责计算签名的函数（无论是导出还是非导出函数），模拟其运行环境和参数，直接调用它来获取签名结果。

---

## 案例分析 4：某手

- **现象**: API 请求参数中包含 `sig` 和 `__NS_sig` 字段。请求体同样可能使用 Protobuf 序列化并加密。

- **核心逻辑**:
  - **双签名体系**:
    - `sig`: 一个相对传统的 API 签名，通常是对所有请求参数进行排序、拼接、加盐后进行 MD5 或 HMAC 哈希。
    - `__NS_sig` (New Signature): 这是一个更复杂的风控签名，其计算过程融入了大量的设备指纹信息，用于对抗模拟器和脚本。
  - **动态 Salt**: 在加密和签名过程中会使用到一个 `client_salt`，这个盐值并非固定，而是可能从 Protobuf 数据中动态获取，或者通过 JNI 调用 SO 库动态生成，这增加了模拟请求的难度。

- **逆向挑战**:
  - 其核心 SO 库（如 `libcore.so`）经过了深度混淆，虽然可能不是 VMP 级别，但静态分析依然困难重重。
  - 同样大量使用了 Protobuf，需要投入精力去逆向其数据结构。

---

## 案例分析 5：某团

- **现象**: API 请求中包含大量自定义请求头，如 `M-TraceId`。请求体被加密，并且能看到 `rohr` 和 `mtgsig` 等新一代的风控及签名字段。

- **核心逻辑**:
  - **中心化风控库**: 核心保护逻辑高度集中在 `libmtguard.so` 中，该库负责生成几乎所有的签名和风控数据。
  - **请求压缩与加密**: 请求体可能会先用 `zlib` 或 `gzip` 进行压缩，然后再通过 AES 进行加密，服务器端需要先解密再解压。
  - **`rohr` & `mtgsig`**: 这是其新一代的风控签名体系。`rohr` 是一个风控令牌，包含了加密的设备和环境信息；`mtgsig` 是 API 签名，它在计算时会依赖 `rohr` 的部分数据，两者强关联。
  - **统一请求网关**: 有一个统一的 API 网关，加密和签名逻辑相对集中，便于统一管理和迭代。

- **逆向挑战**:
  - `libmtguard.so` 是逆向的重中之重，其内部逻辑复杂且经过混淆。
  - 风控维度极广，除了常规的设备指纹，还可能包括地理位置、历史行为、网络环境等，对伪造设备画像的一致性要求非常高。

---

## 案例分析 6：某里系 (某宝、某付宝)

- **现象**: API 请求中包含一个 `sign` 字段，并且还有一个名为 `wua` 的神秘参数。网络请求通过自有的 MTop 网关进行分发。

- **核心逻辑**:
  - **统一网关 (MTop)**: 某里系 App 使用自研的 MTop 作为统一无线网关。所有的 API 请求都经过这个网关，便于统一进行签名校验、安全风控和流量调度。
  - **安全核心 (`libsgmain.so`)**: 所有的安全逻辑都高度集成在 `libsgmain.so` 以及一系列 `libsgxxx.so` (如 `libsgsecuritybody.so`) 的安全组件中。这是某里安全的核心技术结晶，负责签名 `sign` 和风控参数 `wua` 的生成。
  - **`sign` 签名**: 签名算法极其复杂。它不仅包含 API 的业务参数，还会将时间戳、App 版本、Token 以及从安全 SDK 中获取的大量设备指纹信息一同参与计算。其拼接和加密方式非常规整。
  - **`wua` 风控参数**: 这是一个类似于 `anti_content` 的黑盒风控参数。它由 `libsgmain.so` 采集海量的设备信息（包括硬件、系统、网络、传感器、环境检测等）后，经过高度混淆的算法加密生成。`wua` 的生成难度和重要性甚至高于 `sign`。服务端会将 `sign` 和 `wua` 进行强关联校验。
  - **ACCS 通道**: 使用自研的 ACCS (Alibaba Cloud Channel Service) 长连接通道，基于 HTTP/2，进一步封装了网络请求，使得常规抓包和分析变得更加困难。

- **逆向挑战**:
  - **顶级混淆**: `libsgmain.so` 及其依赖库使用了自研的、多层次的复杂混淆技术，静态分析几乎无法下手，是业界公认的最难逆向的 SO 库之一。
  - **动态加载与反调试**: 安全组件的加载和初始化过程非常隐晦，并伴有大量的反调试和环境检测手段，给动态调试和分析设置了极高的门槛。
  - **黑盒 RPC 调用**: 与某节系类似，业界的主流策略是放弃算法还原。逆向的终极目标是在 SO 文件中找到一个类似 `main` 的函数入口，通过 RPC 调用的方式，传入请求参数，获取计算好的 `sign` 和 `wua` 值。定位这个入口需要极其深厚的动态调试和二进制分析功底。

---

## 逆向分析通用策略

1. **静态分析 (Jadx/Ghidra)**:
   - **全局搜索**：搜索关键词，如 `sign`, `encrypt`, 以及上述案例中的 `anti_content`, `X-Sign`, `X-Gorgon`, `mtgsig`, `wua` 等。
   - **定位网络库**: 现代 App 大多使用 OkHttp。搜索 `okhttp3.Interceptor` 的实现类，因为加密和签名的逻辑常常在自定义拦截器中统一处理。
   - **追踪 JNI 调用**: 找到 Java 层调用 Native 方法的地方，重点关注那些函数名可疑（如 `getSignFromC`）、参数多且包含字节数组的函数。

2. **动态分析 (Frida)**:
   - **Hook 加密算法**: 这是最有效的方法。Hook `java.security.MessageDigest.digest` 和 `javax.crypto.Mac.doFinal`，打印它们的输入（即被签名的明文）和调用堆栈，可以瞬间定位到生成签名的代码位置。
   - **Hook 网络请求**: Hook `okhttp3.Request.Builder` 的 `build()` 方法，或 `okhttp3.OkHttpClient` 的 `newCall` 方法，可以 dump 出所有即将发出的网络请求的完整信息（URL, Headers, Body），用于和抓包结果对比。
   - **Hook SO 函数**: 定位到核心 SO 库后，用 Frida `Interceptor.attach` 直接 Hook 目标导出函数，观察其输入和输出。对于非导出函数，可以通过基地址加偏移的方式进行 Hook。

---

## 高级策略：黑盒 RPC 调用详解

在分析某节、某里等顶级厂商的加固 SO 时，会发现其核心逻辑受 VMP (虚拟机保护) 或自研虚拟机保护。这意味着原始的 ARM 指令被转换成了一套自定义的、无法被常规反汇编工具解析的字节码。在这种情况下，试图完全理解并"白盒"地还原签名算法，几乎是不可能的。

因此，业界的分析思路从"算法还原"转向"算法利用"，这便是**黑盒 RPC (Remote Procedure Call) 调用**。

### 什么是黑盒 RPC 调用？

核心思想是：**不再关心函数内部是如何实现的，而是将其作为一个整体，一个黑盒子。我们只关心它的输入和输出。**

我们将通过 Frida 等工具，在 App 的运行时环境中，强行调用这个黑盒函数，让它为我们计算出所需的结果（如 `sign`, `wua`），然后将结果返回给外部的自动化程序。

这就好比我们使用一个网站的 API，我们不需要它的源码，只需要知道它的 URL、参数和返回值格式就能使用它。在这里，SO 里的函数就是那个"API"。

### 实现黑盒 RPC 的核心步骤

#### 第一步：定位目标函数地址 (Finding the Function Pointer)

这是最困难、最耗时的一步，需要深厚的动态调试功底。

1. **从 JNI 入口开始**: 从 Java 层调用 Native 方法的地方（`JNI` 函数）作为起点。
2. **主动调用与插桩**: 使用 Frida 主动调用该 JNI 函数，并使用 `Stalker` 等指令级跟踪工具，记录下执行轨迹。
3. **执行流分析**: 分析 Stalker 产生的巨大日志，或使用 `Unicorn Engine` 等模拟执行工具进行分析，理清复杂的跳转和计算逻辑，最终找到一个"干净"的函数入口——它接收相对原始的业务参数，返回最终的签名结果。这个函数的地址（通常是 SO 基址 + 偏移量）就是我们的目标。

#### 第二步：分析函数原型 (Analyzing the Prototype)

确定目标函数的输入和输出。

- **输入参数**: 在上一步找到的函数调用点下断点，观察调用前各寄存器（ARM32 下重点关注 R0-R3）和栈上的值，推断出函数的参数类型、数量和顺序。参数可能是字符串、字节数组、结构体指针等。
- **返回值**: 在函数返回点下断点，观察 R0 寄存器的值，确定函数的返回值是什么（通常是一个指向结果字符串的指针或一个状态码）。

#### 第三步：构建 RPC 服务端 (Frida Agent)

编写一个 Frida 脚本，将定位到的原生函数封装成一个可供远程调用的服务。

**agent.js:**

```javascript
// 1. Get SO base address
const baseAddr = Module.findBaseAddress("libsgmain.so");
// 2. Calculate target function absolute address
// This 0x123456 is the function offset found through great effort in step one
const targetFuncPtr = baseAddr.add(0x123456);

// 3. Define function based on the prototype analyzed in step two
// Assume function prototype is: char* func(char* input1, int input2)
const nativeFunc = new NativeFunction(targetFuncPtr, "pointer", [
  "pointer",
  "int",
]);

// 4. Expose interface using rpc.exports
rpc.exports = {
  // Define a remote call interface named getSign
  getSign: function (param1, param2) {
    console.log("RPC call received, invoking native function...");
    // Prepare parameters for native function
    const input1Ptr = Memory.allocUtf8String(param1);

    // Call native function
    const resultPtr = nativeFunc(input1Ptr, param2);

    // Read and return result
    return resultPtr.readUtf8String();
  },
};
```

**client.py:**

```python
import frida

def main():
    # Connect to frida-server on device
    device = frida.get_usb_device()

    # Attach to target App process
    pid = device.spawn(["com.example.app"])
    session = device.attach(pid)

    # Load Frida Agent script
    with open("agent.js") as f:
        script_code = f.read()
    script = session.create_script(script_code)
    script.load()

    # Prepare parameters
    api_params_str = "param1=value1&param2=value2"
    some_int_value = 123

    # Call RPC interface like calling a local function
    print("Calling RPC function: getSign...")
    result_sign = script.exports.get_sign(api_params_str, some_int_value)

    print(f"Successfully got sign: {result_sign}")

    # Can use the obtained sign to construct and send network requests here
    # ...

    session.detach()

if __name__ == '__main__':
    main()
```

通过黑盒 RPC，我们可以绕过对 VMP 等复杂技术的直接对抗，将逆向的重点放在寻找和调用关键函数上，这在当今的高级移动安全攻防中是一种务实且高效的策略。
