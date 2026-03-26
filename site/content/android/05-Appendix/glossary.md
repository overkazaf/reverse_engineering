---
title: "术语表 (Glossary)"
date: 2025-08-25
type: posts
tags: ["Native层", "Ghidra", "Frida", "DEX", "资源", "OLLVM"]
weight: 10
---

# 术语表 (Glossary)

收集了 Android 逆向工程中常见的术语和缩写，按类别整理为表格形式，便于快速查阅。

---

## 1. 逆向工程基础 (Reverse Engineering Fundamentals)

逆向工程领域的核心概念与通用术语。

| 中文名称 | 英文名称 | 说明 |
|---------|---------|------|
| 逆向工程 | Reverse Engineering (RE) | 通过分析软件的二进制代码来理解其功能、逻辑和结构的过程，通常在没有源代码的情况下进行。 |
| 反汇编 | Disassembly | 将机器码（二进制）翻译回汇编语言的过程，是逆向分析的基础步骤。 |
| 反编译 | Decompilation | 将低级代码（机器码或字节码）还原为高级语言（如 Java、C）的过程，结果是伪代码或近似源代码。 |
| 静态分析 | Static Analysis | 在不运行程序的情况下，通过检查其代码、结构和资源来理解程序行为的技术。 |
| 动态分析 | Dynamic Analysis | 在程序运行时对其进行监视、调试和分析的技术，通常涉及调试器、Hook 等工具。 |
| 二进制分析 | Binary Analysis | 对编译后的二进制文件进行检查和分析，包括结构解析、控制流分析、漏洞挖掘等。 |
| 调试 | Debugging | 使用调试器逐步执行程序，观察其内部状态（寄存器、内存、变量）以定位问题或理解逻辑。 |
| 断点 | Breakpoint | 调试时设置的暂停点，当程序执行到该位置时会中断，允许检查当前状态。 |
| 符号表 | Symbol Table | 二进制文件中保存的函数名、变量名等调试信息，去除符号表（strip）会增加逆向难度。 |
| 控制流图 | Control Flow Graph (CFG) | 以图形方式表示程序中所有可能执行路径的结构，用于理解程序逻辑。 |
| 调用图 | Call Graph | 表示程序中函数之间调用关系的有向图，有助于理解程序的整体架构。 |
| 交叉引用 | Cross-Reference (Xref) | 在反汇编工具中，跟踪某个函数或数据被哪些位置引用，是逆向分析的重要手段。 |
| 补丁 | Patch | 对二进制文件进行修改，用于绕过检测、修改逻辑或修复漏洞。 |
| 签名匹配 | Signature Matching | 通过已知的字节序列模式识别特定的函数、库或恶意代码的技术。 |
| 沙箱 | Sandbox | 一种隔离的执行环境，用于安全地运行和分析可疑程序而不影响主系统。 |
| 污点分析 | Taint Analysis | 追踪数据在程序中的传播路径，标记受外部输入影响的数据以发现潜在安全问题。 |
| 指令集架构 | Instruction Set Architecture (ISA) | 处理器支持的机器指令的集合，如 ARM、x86、MIPS 等。 |
| 精简指令集 | RISC (Reduced Instruction Set Computer) | 一种处理器设计理念，使用较少且简单的指令，ARM 处理器即采用此架构。 |
| 复杂指令集 | CISC (Complex Instruction Set Computer) | 一种处理器设计理念，使用较多且复杂的指令，x86 处理器即采用此架构。 |
| 可执行与可链接格式 | ELF (Executable and Linkable Format) | Linux/Android Native 层使用的标准二进制文件格式，包含代码段、数据段、符号表等。 |
| 程序入口点 | Entry Point | 程序开始执行的第一条指令的地址，通常在 ELF 文件头中指定。 |
| 重定位 | Relocation | 将程序中的符号引用绑定到实际内存地址的过程，发生在链接或加载阶段。 |
| 动态链接库 | Shared Object (SO) | Linux/Android 下的共享库文件（.so），包含可被多个程序共享的代码和数据。 |
| 过程链接表 | PLT (Procedure Linkage Table) | ELF 文件中用于延迟绑定外部函数的跳转表，调用外部函数时先经过 PLT。 |
| 全局偏移表 | GOT (Global Offset Table) | ELF 文件中存储外部符号实际地址的表，PLT 通过 GOT 来间接调用外部函数。 |
| 寄存器 | Register | CPU 内部的高速存储单元，用于临时保存数据和指令地址，ARM 架构有 R0-R15（32位）和 X0-X30（64位）等。 |
| 栈 | Stack | 后进先出的内存结构，用于保存函数调用的返回地址、局部变量和参数，栈溢出是常见的安全漏洞。 |
| 堆 | Heap | 用于动态内存分配的内存区域，malloc/free（C）或 new/delete（C++）操作的内存来自堆。 |
| 操作码 | Opcode | 机器指令中指定要执行的操作类型的部分，反汇编器将操作码翻译为人类可读的助记符。 |
| 字节序 | Endianness | 多字节数据在内存中的存储顺序，分为大端序（Big-Endian）和小端序（Little-Endian），ARM 通常使用小端序。 |
| 地址空间布局随机化 | ASLR (Address Space Layout Randomization) | 随机化进程内存布局（代码段、栈、堆等地址）的安全机制，增加漏洞利用的难度。 |
| 位置无关代码 | PIC (Position Independent Code) | 不依赖固定内存地址即可正确执行的代码，共享库通常编译为 PIC 以支持 ASLR。 |
| 反汇编器 | Disassembler | 将机器码翻译为汇编语言的工具，如 IDA Pro、Ghidra 中的反汇编引擎。 |
| 反编译器 | Decompiler | 将低级代码还原为高级语言的工具，如 Hex-Rays（C/C++）、JADX（Java）。 |
| 十六进制编辑器 | Hex Editor | 以十六进制格式查看和编辑二进制文件的工具，可直接修改文件中的任意字节。 |
| 数据流分析 | Data Flow Analysis | 追踪数据在程序中如何产生、传播和使用的分析方法，帮助理解变量赋值和函数参数传递。 |
| 逆向工程师 | Reverse Engineer | 专门从事逆向分析的技术人员，需掌握汇编语言、操作系统原理、密码学等多领域知识。 |
| 二进制差异分析 | Binary Diffing | 比较同一软件不同版本的二进制文件以发现修改内容的技术，常用于分析安全补丁修复了什么漏洞。 |
| 脱壳器/解包器 | Unpacker | 自动或半自动地从加壳/加固程序中还原出原始代码的工具或脚本。 |
| 虚拟地址 | Virtual Address (VA) | 进程看到的内存地址，由操作系统的虚拟内存机制映射到物理地址，每个进程拥有独立的虚拟地址空间。 |
| 相对虚拟地址 | RVA (Relative Virtual Address) | 相对于模块加载基址的偏移量，在分析 ELF/PE 文件时常需在 RVA 和文件偏移之间转换。 |

---

## 2. Android 平台 (Android Platform)

Android 系统架构、运行时、组件和开发相关的术语。

| 中文名称 | 英文名称 | 说明 |
|---------|---------|------|
| Android 运行时 | ART (Android Runtime) | Android 5.0 引入的应用运行时环境，使用 AOT 编译技术将字节码预编译为机器码，完全取代了 Dalvik。 |
| Dalvik 虚拟机 | Dalvik VM | Google 早期为 Android 设计的虚拟机，使用 JIT（即时编译）技术，在 Android 5.0 后被 ART 取代。 |
| DEX 文件 | DEX (Dalvik Executable) | Android 平台的可执行字节码文件格式，APK 中的 classes.dex 包含应用的所有 Java/Kotlin 编译后的代码。 |
| 多 DEX | MultiDex | 当应用方法数超过 65536 限制时，将代码拆分为多个 DEX 文件（classes.dex、classes2.dex 等）的机制。 |
| OAT 文件 | OAT (Of Ahead-of-Time) | ART 运行时使用的私有 ELF 格式文件，包含 AOT 编译后的机器码及原始 DEX 数据。 |
| ODEX 文件 | ODEX (Optimized DEX) | 经过优化的 DEX 文件，系统在安装或首次运行时生成，以提高加载速度。 |
| VDEX 文件 | VDEX (Verified DEX) | Android 8.0 引入的文件格式，包含经过验证的 DEX 文件，用于加速启动和更新流程。 |
| Smali | Smali | Dalvik 字节码的人类可读汇编语言表示，可直接修改后重新打包，是 Android 逆向的重要中间格式。 |
| Baksmali | Baksmali | 将 DEX 文件反汇编为 Smali 代码的工具，名字来源于冰岛语"反汇编"。 |
| Android 应用包 | APK (Android Package) | Android 应用的安装包格式，本质是一个 ZIP 压缩包，包含 DEX、资源文件、清单文件和签名信息。 |
| AAB 包 | AAB (Android App Bundle) | Google 推出的新发布格式，由 Google Play 根据设备配置动态生成优化的 APK。 |
| 清单文件 | AndroidManifest.xml | 每个 APK 必须包含的核心配置文件，声明包名、组件、权限、最低 SDK 版本等关键信息。 |
| 孵化进程 | Zygote | Android 系统中所有应用进程的父进程，通过 fork 机制快速创建新的应用进程，预加载了常用类和资源。 |
| 系统服务器 | System Server | 由 Zygote fork 出的第一个进程，承载了大量核心系统服务（AMS、PMS、WMS 等）。 |
| 活动管理服务 | AMS (Activity Manager Service) | 管理 Activity 生命周期、任务栈和进程调度的核心系统服务。 |
| 包管理服务 | PMS (Package Manager Service) | 负责应用安装、卸载、权限管理和包信息查询的系统服务。 |
| Binder 机制 | Binder IPC | Android 特有的高效进程间通信 (IPC) 机制，基于内存映射实现，几乎所有系统服务都通过 Binder 通信。 |
| AIDL 接口 | AIDL (Android Interface Definition Language) | Android 接口定义语言，用于定义跨进程通信的接口，编译后生成 Binder 通信所需的代理类。 |
| JNI 接口 | JNI (Java Native Interface) | Java 与 Native 代码（C/C++）之间的桥梁，允许 Java 调用本地函数，也允许 Native 代码回调 Java 方法。 |
| NDK 开发包 | NDK (Native Development Kit) | Android 官方提供的 Native 开发工具集，允许使用 C/C++ 编写高性能模块或复用已有 C 库。 |
| 调试桥 | ADB (Android Debug Bridge) | Android 调试桥，通用命令行工具，用于与模拟器或 Android 设备通信，支持 shell、文件传输、日志等功能。 |
| AOSP 项目 | AOSP (Android Open Source Project) | Android 开源项目，即 Android 系统的完整源代码，是研究系统底层行为的第一手资料。 |
| ARM 架构 | ARM (Advanced RISC Machines) | 广泛用于移动设备的精简指令集处理器架构，Android 设备主要使用 ARM 及其 64 位变体 AArch64。 |
| 引导加载程序 | Bootloader | 设备开机后最先运行的程序，负责硬件初始化并加载操作系统内核，解锁 Bootloader 是刷机的前提。 |
| 恢复模式 | Recovery | Android 设备的特殊启动模式，用于恢复出厂设置、刷入 OTA 更新包或自定义 ROM。 |
| 获取 Root 权限 | Rooting | 获取 Android 设备超级用户权限的过程，使用户可以完全控制系统，也是许多逆向工具的前提。 |
| SELinux 策略 | SELinux (Security-Enhanced Linux) | Android 使用的强制访问控制系统，限制进程对文件和资源的访问权限，增加安全性。 |
| 内容提供者 | Content Provider | Android 四大组件之一，提供跨进程的数据共享接口，常通过 URI 访问数据库或文件。 |
| 广播接收器 | Broadcast Receiver | Android 四大组件之一，用于接收和响应系统或应用发出的广播消息。 |
| 服务 | Service | Android 四大组件之一，在后台执行长时间运行的操作，没有用户界面。 |
| Intent 消息 | Intent | Android 组件之间通信的消息对象，用于启动 Activity、Service 或发送广播，可携带数据。 |
| 应用沙箱 | App Sandbox | Android 为每个应用分配独立的 UID 和数据目录，通过 Linux 权限机制实现应用间的隔离。 |
| 权限模型 | Permission Model | Android 通过声明和授予权限来控制应用对敏感资源（相机、定位、存储等）的访问。 |
| 预编译 | AOT (Ahead-Of-Time Compilation) | ART 在安装时将字节码预编译为机器码的技术，相比 JIT 提高了运行时性能但增加安装时间。 |
| 即时编译 | JIT (Just-In-Time Compilation) | 在程序运行时将字节码编译为机器码的技术，Android 7.0 后 ART 同时使用 AOT + JIT 的混合方案。 |
| 设备树 | Device Tree (DT/DTB) | 描述硬件配置信息的数据结构，内核通过它识别设备硬件，自定义内核时可能需要修改。 |
| GKI 内核 | GKI (Generic Kernel Image) | Google 推出的通用内核镜像，将内核分为 Google 维护的通用核心和厂商模块，简化内核更新流程。 |
| Boot 镜像 | Boot Image (boot.img) | Android 设备的启动镜像，包含内核、ramdisk 等组件，Magisk 和 KernelSU 通过修补 boot.img 实现 Root。 |
| 分区 | Partition | Android 设备存储的分区结构，常见的有 system、vendor、data、boot、recovery 等分区。 |
| 叠加文件系统 | OverlayFS | 允许在只读文件系统上叠加可写层的文件系统，Magisk 的 systemless 修改机制基于类似原理。 |
| 属性系统 | Property System | Android 的全局键值对配置系统，通过 getprop/setprop 访问，常用于检查设备状态和编译信息。 |
| 应用签名 | App Signing | Android 要求每个 APK 必须用开发者的私钥签名，签名信息存储在 META-INF 目录或 APK Signing Block 中。 |
| DEX 字节码 | Dalvik Bytecode | Dalvik/ART 虚拟机执行的指令集，基于寄存器架构，与 Java 字节码（基于栈架构）不同。 |
| ABI 接口 | ABI (Application Binary Interface) | 应用二进制接口，定义了二进制代码如何与系统交互，Android 支持 armeabi-v7a、arm64-v8a、x86、x86_64 等 ABI。 |
| 进程间通信 | IPC (Inter-Process Communication) | 不同进程之间交换数据和信号的机制，Android 中主要通过 Binder、Socket、共享内存等方式实现。 |
| 可信执行环境 | TEE (Trusted Execution Environment) | 处理器中与普通执行环境隔离的安全区域，用于保护敏感操作（如指纹验证、密钥存储）。 |

---

## 3. 加密与签名 (Cryptography & Signatures)

密码学算法、签名机制和安全认证相关的术语。

| 中文名称 | 英文名称 | 说明 |
|---------|---------|------|
| 高级加密标准 | AES (Advanced Encryption Standard) | 对称加密算法，使用 128/192/256 位密钥，是目前最广泛使用的对称加密标准。 |
| DES 加密 | DES (Data Encryption Standard) | 早期的对称加密标准，因 56 位密钥过短已被淘汰，3DES 是其增强版本但也逐步退出使用。 |
| RSA 算法 | RSA (Rivest-Shamir-Adleman) | 经典的非对称加密算法，基于大数分解难题，广泛用于数字签名和密钥交换。 |
| 椭圆曲线加密 | ECC (Elliptic Curve Cryptography) | 基于椭圆曲线数学的非对称加密体系，在相同安全强度下密钥比 RSA 短得多。 |
| ECDSA 签名 | ECDSA (Elliptic Curve Digital Signature Algorithm) | 基于椭圆曲线的数字签名算法，常用于 HTTPS 证书和区块链签名。 |
| 消息认证码 | HMAC (Hash-based Message Authentication Code) | 基于哈希函数和密钥的消息认证码，用于验证数据完整性和来源真实性。 |
| MD5 哈希 | MD5 (Message Digest 5) | 128 位哈希算法，因存在碰撞漏洞已不适合用于安全场景，但仍常见于文件校验和旧系统中。 |
| SHA 哈希 | SHA (Secure Hash Algorithm) | 安全哈希算法家族，包括 SHA-1（已不安全）、SHA-256、SHA-512 等，用于完整性校验和数字签名。 |
| CRC 校验 | CRC (Cyclic Redundancy Check) | 循环冗余校验，用于检测数据传输错误，不适合用于安全用途但在文件格式中非常常见。 |
| 对称加密 | Symmetric Encryption | 加密和解密使用同一密钥的加密方式，速度快，适合加密大量数据，如 AES、DES。 |
| 非对称加密 | Asymmetric Encryption | 使用公钥加密、私钥解密（或反之）的加密方式，用于密钥交换和数字签名，如 RSA、ECC。 |
| 数字签名 | Digital Signature | 使用私钥对数据摘要进行加密生成签名，任何人可用公钥验证，确保数据完整性和来源不可否认。 |
| APK 签名 | APK Signing | Android 应用必须经过签名才能安装，签名用于验证应用来源和完整性，包含 v1/v2/v3/v4 多种方案。 |
| 签名校验 | Signature Verification | 应用运行时检查自身签名是否被篡改的保护机制，常用于防止重打包和破解。 |
| 密钥库 | KeyStore | Android 提供的安全密钥存储系统，支持硬件级密钥保护（TEE/StrongBox），密钥不可导出。 |
| 基于时间的一次性密码 | TOTP (Time-based One-Time Password) | 基于当前时间和共享密钥生成一次性密码的算法，常用于双因素认证（如 Google Authenticator）。 |
| 基于计数器的一次性密码 | HOTP (HMAC-based One-Time Password) | 基于计数器和共享密钥生成一次性密码的算法，是 TOTP 的基础。 |
| Base64 编码 | Base64 | 将二进制数据转换为 ASCII 字符串的编码方式，常见于网络传输和配置文件中，注意它不是加密。 |
| XOR 运算 | XOR (Exclusive OR) | 异或运算，最简单的加密原语，常在简单的加密、校验和混淆中使用。 |
| 白盒加密 | White-Box Cryptography | 将密钥嵌入到算法实现中的加密技术，即使攻击者可以观察算法执行过程也无法提取密钥。 |
| 密钥派生函数 | KDF (Key Derivation Function) | 从密码或主密钥派生出加密密钥的函数，如 PBKDF2、scrypt、Argon2，增加暴力破解难度。 |
| 分组密码模式 | Block Cipher Mode | 分组密码的工作模式，如 ECB、CBC、CTR、GCM 等，不同模式的安全性和性能特征不同。 |
| 初始化向量 | IV (Initialization Vector) | 加密时使用的随机值，确保相同明文在不同加密操作中产生不同密文，CBC 和 GCM 模式都需要 IV。 |
| 填充方式 | Padding | 将明文填充至分组密码要求的块长度的方法，常见的有 PKCS5/PKCS7 Padding 和 Zero Padding。 |
| RC4 流密码 | RC4 | 早期广泛使用的流加密算法，已被发现多个安全弱点，不推荐使用但在旧系统中仍可能遇到。 |
| 国密算法 | SM Series (SM2/SM3/SM4) | 中国国家密码管理局发布的商用密码算法，SM2 是非对称加密，SM3 是哈希算法，SM4 是对称加密。 |
| 证书签名方案 | APK Signature Scheme | Android APK 签名机制的演进：v1（基于 JAR）、v2（全文件签名）、v3（支持密钥轮换）、v4（增量安装）。 |
| 密钥协商 | Key Exchange | 通信双方在不安全信道上协商出共享密钥的过程，如 Diffie-Hellman (DH) 和 ECDHE 算法。 |
| 随机数生成器 | RNG (Random Number Generator) | 生成随机数的组件，密码学安全的 RNG (CSPRNG) 是加密系统的基础，弱随机数会导致严重安全问题。 |
| 消息摘要 | Message Digest | 对任意长度数据计算出的固定长度哈希值，用于验证数据完整性，不可逆推出原始数据。 |
| 数字信封 | Digital Envelope | 结合对称加密和非对称加密的混合加密方案：用随机对称密钥加密数据，再用接收方公钥加密对称密钥。 |
| 盐值 | Salt | 在哈希计算前添加的随机数据，确保相同的明文产生不同的哈希值，防止彩虹表攻击。 |

---

## 4. Hook 与插桩 (Hooking & Instrumentation)

函数拦截、代码注入和动态修改程序行为相关的术语。

| 中文名称 | 英文名称 | 说明 |
|---------|---------|------|
| 挂钩/钩子 | Hook | 拦截函数调用、消息或事件的技术，用于监视或修改程序行为，是动态分析的核心手段。 |
| 内联钩子 | Inline Hook | 直接修改目标函数开头的指令，插入跳转指令到自定义代码，是 Native 层最常用的 Hook 方式。 |
| PLT 钩子 | PLT Hook | 通过修改 GOT/PLT 表中的函数地址来拦截对外部库函数的调用，对同一 SO 内的调用无效。 |
| 跳板 | Trampoline | Hook 技术中用于保存原始指令并跳转回原函数继续执行的代码片段，确保原始功能不被破坏。 |
| 动态插桩 | Dynamic Binary Instrumentation (DBI) | 在程序运行时动态插入分析代码的技术，无需修改原始二进制文件，如 Frida、DynamoRIO。 |
| 静态插桩 | Static Binary Instrumentation (SBI) | 在程序执行前修改二进制文件以插入分析代码的技术，修改后的文件可独立运行。 |
| Java 层 Hook | Java-level Hook | 通过替换 ART 虚拟机中的方法入口来拦截 Java/Kotlin 方法调用，如 Xposed、Frida 的 Java.use。 |
| Native 层 Hook | Native-level Hook | 对 C/C++ 编译的 Native 代码（.so 文件）进行拦截，通常使用 Inline Hook 或 PLT Hook。 |
| 方法替换 | Method Swizzling | 在运行时将一个方法的实现替换为另一个方法，在 iOS/Objective-C 中尤为常见，Android 中也有类似机制。 |
| 代码注入 | Code Injection | 将自定义代码注入到目标进程中执行的技术，通常通过 ptrace、dlopen 或 LD_PRELOAD 实现。 |
| ptrace 系统调用 | ptrace | Linux 提供的进程跟踪系统调用，调试器通过它控制目标进程的执行、读写内存和寄存器。 |
| 进程注入 | Process Injection | 将代码或共享库加载到另一个正在运行的进程的地址空间中，是实现 Hook 的前提步骤。 |
| LD_PRELOAD | LD_PRELOAD | Linux 环境变量，指定在所有其他共享库之前加载的库，可用于拦截标准库函数调用。 |
| 代理/拦截器 | Interceptor | Frida 中用于拦截 Native 函数调用的 API，可在函数执行前后插入自定义逻辑。 |
| 替换 | Replacer | 完全替换目标函数实现的 Hook 方式，原始函数将不再被调用。 |
| Stalker 追踪器 | Stalker | Frida 提供的代码追踪引擎，可以追踪目标进程每一条执行的指令，用于代码覆盖率分析。 |
| ART 方法入口 | ART Entry Point | ART 虚拟机中每个 Java 方法的执行入口指针，Hook 框架通过修改它来实现方法拦截。 |
| 系统调用钩子 | Syscall Hook | 拦截应用对 Linux 内核系统调用的技术，可在内核层面监控文件访问、网络通信等行为。 |
| 虚函数表钩子 | VTable Hook | 通过修改 C++ 对象的虚函数表指针来拦截虚函数调用的技术。 |
| 异常处理钩子 | Exception Hook | 通过设置硬件断点或修改异常处理机制来实现的 Hook 技术，比修改代码更隐蔽。 |
| 回调函数 | Callback | Hook 触发时执行的自定义函数，分为 onEnter（函数执行前）和 onLeave（函数返回后）两种时机。 |
| 函数指针替换 | Function Pointer Replacement | 通过修改存储函数指针的内存位置来重定向函数调用的技术，适用于通过指针调用的场景。 |
| 代码覆盖率 | Code Coverage | 记录程序执行时哪些代码被实际运行的技术，Frida 的 Stalker 可用于收集覆盖率信息以辅助模糊测试。 |

---

## 5. 保护与混淆 (Protection & Obfuscation)

软件保护、代码混淆、反调试和加固相关的术语。

| 中文名称 | 英文名称 | 说明 |
|---------|---------|------|
| 代码混淆 | Obfuscation | 使代码难以理解但保持功能不变的技术，包括重命名、控制流扁平化、字符串加密等手段。 |
| 加壳/加固 | Packing / Hardening | 对 APK 进行保护处理，将原始 DEX 加密隐藏，运行时才解密加载，增加逆向分析难度。 |
| 脱壳 | Unpacking | 从加固的 APK 中还原出原始 DEX 文件的过程，常用方法包括内存 dump、Hook ClassLoader 等。 |
| OLLVM 混淆 | OLLVM (Obfuscator-LLVM) | 基于 LLVM 编译器框架的开源代码混淆项目，支持控制流扁平化、虚假控制流、指令替换等。 |
| 控制流扁平化 | Control Flow Flattening (CFF) | OLLVM 的核心混淆技术，将正常的控制流结构转化为 switch-case 分发器结构，严重增加分析难度。 |
| 虚假控制流 | Bogus Control Flow (BCF) | 在代码中插入永远不会执行的假分支，干扰分析者对真实逻辑的判断。 |
| 指令替换 | Instruction Substitution | 用功能等价但更复杂的指令序列替换简单指令，增加反汇编代码的阅读难度。 |
| 字符串加密 | String Encryption | 将程序中的明文字符串加密存储，运行时才解密使用，防止通过字符串搜索定位关键代码。 |
| 虚拟机保护 | VMP (Virtual Machine Protection) | 将原始代码转换为自定义字节码，并内置专用解释器来执行，是最强的代码保护技术之一。 |
| 花指令 | Junk Code / Dead Code | 插入不影响程序功能的无用指令或永远不执行的代码，用于干扰反汇编器和分析者。 |
| 反调试 | Anti-Debug | 检测程序是否正在被调试的保护技术，常通过检查 ptrace 状态、/proc/self/status、时间差等实现。 |
| 反 Root 检测 | Anti-Root Detection | 检测设备是否已获取 Root 权限的技术，常检查 su 二进制文件、Magisk 痕迹、系统属性等。 |
| 反 Hook 检测 | Anti-Hook Detection | 检测程序是否被 Hook 框架拦截的技术，常检查 Frida 端口、Xposed 特征、内存中的 Hook 痕迹。 |
| 反模拟器检测 | Anti-Emulator Detection | 检测应用是否运行在模拟器中的技术，常检查硬件属性、传感器数据、设备指纹等特征。 |
| 完整性校验 | Integrity Check | 应用运行时验证自身代码或资源是否被篡改的机制，常对 DEX、SO 文件计算哈希值并比对。 |
| 代码抽取 | Code Extraction / Function-level Packing | 将 DEX 中的方法体抽取并加密存储，运行时才恢复到内存中执行，比整体加壳更难脱壳。 |
| ProGuard 混淆 | ProGuard | Android 官方推荐的 Java 字节码混淆和优化工具，可进行类名/方法名重命名、无用代码删除等。 |
| R8 编译器 | R8 | Google 推出的替代 ProGuard 的新一代代码缩减和混淆工具，已成为 Android 构建的默认工具。 |
| 名称混淆 | Name Obfuscation / Renaming | 将类名、方法名、变量名替换为无意义的短名称（如 a、b、c），最基础的混淆手段。 |
| 环境检测 | Environment Detection | 应用在运行时检查执行环境是否正常（非 Root、非模拟器、非调试模式等），是保护链的第一环。 |
| 反篡改 | Anti-Tampering | 应用在运行时验证自身代码、资源和签名的完整性，发现篡改后终止运行或上报服务器。 |
| 代码虚拟化 | Code Virtualization | VMP 的核心技术，将原始指令转换为自定义虚拟机的字节码，每次编译可生成不同的指令集。 |
| 混合保护 | Multi-layered Protection | 同时使用多种保护技术（加壳 + 混淆 + 反调试 + VMP）构建多层防御体系，增加破解成本。 |
| 运行时解密 | Runtime Decryption | 将关键代码或数据加密存储，仅在需要时解密到内存中执行或使用，执行后再清除明文。 |
| 调试器检测 | Debugger Detection | 检测是否有调试器附加到进程的技术，常通过 TracerPid、断点扫描、时间检测等方式实现。 |
| 时间检测 | Timing Check | 通过测量代码执行的时间差来检测调试行为，因为单步调试会显著增加执行时间。 |
| Frida 检测 | Frida Detection | 检测 Frida 是否注入到进程中的技术，常检查默认端口 (27042)、内存特征字符串、线程名称等。 |
| SafetyNet / Play Integrity | SafetyNet / Play Integrity API | Google 提供的设备完整性检测 API，可验证设备是否已 Root、Bootloader 是否已解锁等。 |

---

## 6. 网络与协议 (Network & Protocols)

网络通信、安全协议和流量分析相关的术语。

| 中文名称 | 英文名称 | 说明 |
|---------|---------|------|
| 传输层安全协议 | TLS (Transport Layer Security) | 为网络通信提供加密、身份认证和数据完整性的安全协议，HTTPS 的基础，是 SSL 的后继版本。 |
| 安全套接字层 | SSL (Secure Sockets Layer) | TLS 的前身，已被废弃但"SSL"一词仍被广泛用于指代 TLS 加密连接。 |
| 证书锁定 | SSL/Certificate Pinning | 应用内预置服务器证书或公钥的指纹，仅信任特定证书而非系统证书链，防止中间人攻击。 |
| 中间人攻击 | MITM (Man-In-The-Middle) | 攻击者在通信双方之间拦截和修改数据的攻击方式，是抓包分析 HTTPS 流量的核心原理。 |
| 代理服务器 | Proxy | 位于客户端和服务器之间的中介，用于转发、监视或修改网络请求，逆向中常用于抓包分析。 |
| 数字证书 | Certificate (X.509) | 由证书颁发机构 (CA) 签发的电子文件，用于证明服务器或客户端的身份，包含公钥和持有者信息。 |
| 证书颁发机构 | CA (Certificate Authority) | 签发和管理数字证书的受信任机构，浏览器和操作系统预装了一组受信任 CA 的根证书。 |
| 自签名证书 | Self-Signed Certificate | 未经受信任 CA 签发的证书，由使用者自己签发，用于测试和抓包场景。 |
| 系统证书存储 | System Certificate Store | Android 系统存储受信任根证书的位置（/system/etc/security/cacerts/），Android 7+ 默认不信任用户安装的证书。 |
| 抓包 | Packet Capture / Traffic Sniffing | 截获和记录网络数据包的过程，用于分析应用的网络通信协议和数据格式。 |
| HTTP 协议 | HTTP (HyperText Transfer Protocol) | 超文本传输协议，Web 通信的基础协议，明文传输，易于分析但不安全。 |
| HTTPS 协议 | HTTPS (HTTP Secure) | 在 HTTP 基础上使用 TLS 加密的安全协议，是现代应用网络通信的标准。 |
| WebSocket 协议 | WebSocket | 在单个 TCP 连接上提供全双工通信的协议，常用于实时消息推送和聊天功能。 |
| gRPC 协议 | gRPC (Google Remote Procedure Call) | Google 开发的高性能 RPC 框架，使用 Protocol Buffers 作为序列化格式和 HTTP/2 作为传输协议。 |
| Protocol Buffers | Protobuf (Protocol Buffers) | Google 开发的高效二进制序列化格式，比 JSON 更紧凑和快速，需要 .proto 定义文件才能正确解析。 |
| JSON 格式 | JSON (JavaScript Object Notation) | 轻量级的文本数据交换格式，广泛用于 Web API 和移动应用的数据传输。 |
| 请求签名 | Request Signing | 对 API 请求参数和时间戳等计算签名的机制，服务器通过验证签名来防止请求被篡改或重放。 |
| 请求重放 | Replay Attack | 将截获的有效请求重新发送以欺骗服务器的攻击方式，通过时间戳和 nonce 可以防御。 |
| OkHttp 客户端 | OkHttp | Android 平台最流行的 HTTP 客户端库，拦截其 Interceptor 链是分析网络请求的常用方法。 |
| Retrofit 框架 | Retrofit | 基于 OkHttp 的类型安全 HTTP 客户端库，通过注解定义 API 接口，逆向时分析其接口定义可快速了解所有 API。 |
| DNS 解析 | DNS (Domain Name System) | 将域名转换为 IP 地址的系统，应用可能使用自定义 DNS 或 DoH (DNS over HTTPS) 来防止 DNS 劫持。 |
| SNI 字段 | SNI (Server Name Indication) | TLS 握手时客户端发送的目标域名字段，明文传输，可被用于识别和过滤 HTTPS 流量。 |
| HTTP/2 协议 | HTTP/2 | HTTP 协议的第二个主要版本，支持多路复用、头部压缩和服务器推送，抓包分析比 HTTP/1.1 更复杂。 |
| QUIC 协议 | QUIC (Quick UDP Internet Connections) | 基于 UDP 的传输层协议，HTTP/3 的基础，因加密传输和 UDP 通道使传统抓包工具较难拦截。 |
| 双向认证 | Mutual TLS (mTLS) | 客户端和服务器都需要提供证书的双向认证方式，比单向 SSL Pinning 更难绕过。 |
| 网络安全配置 | Network Security Config | Android 7.0 引入的 XML 配置文件，允许应用声明网络安全策略（如信任的 CA、域名 Pinning）。 |

---

## 7. 工具名称 (Tool Names)

逆向工程中常用的软件工具和框架。

| 中文名称 | 英文名称 | 说明 |
|---------|---------|------|
| Frida 框架 | Frida | 跨平台的动态插桩工具包，通过 JavaScript API 在运行时监视和修改应用行为，支持 Android/iOS/Windows/macOS。 |
| Objection 工具 | Objection | 基于 Frida 的运行时移动安全探索工具，提供了许多开箱即用的功能，无需编写脚本即可进行常见分析。 |
| r2frida 插件 | r2frida | 将 radare2 和 Frida 结合的插件，可在 radare2 命令行中使用 Frida 的动态分析能力。 |
| Xposed 框架 | Xposed Framework | 经典的 Android Hook 框架，通过替换 app_process 来拦截应用和系统的 Java 方法调用。 |
| LSPosed 框架 | LSPosed | 基于 Riru/Zygisk 的现代 Xposed 框架实现，支持 Android 8.0 以上版本，可针对特定应用生效。 |
| IDA Pro 反汇编器 | IDA Pro (Interactive DisAssembler) | 业界标准的交互式反汇编器和调试器，支持多种处理器架构，Hex-Rays 反编译器是其核心插件。 |
| Ghidra 分析框架 | Ghidra | 美国 NSA 开源的软件逆向工程框架，提供反汇编、反编译、脚本自动化等功能，是 IDA 的免费替代品。 |
| radare2 框架 | radare2 (r2) | 开源的命令行逆向工程框架，支持反汇编、调试、二进制修补等功能，以强大的命令行接口著称。 |
| JADX 反编译器 | JADX | 将 Android DEX/APK 文件反编译为 Java 源代码的工具，提供 GUI 和命令行两种模式。 |
| JEB 反编译器 | JEB Decompiler | 商业级 Android 反编译器和调试器，支持 DEX 和 Native 代码分析，反编译质量优秀。 |
| apktool 工具 | apktool | 用于反编译和重打包 APK 的工具，可以解码资源文件和反汇编 Smali 代码。 |
| dex2jar 工具 | dex2jar | 将 DEX 文件转换为 Java JAR 文件的工具集，常与 JD-GUI 配合使用进行反编译分析。 |
| Magisk 框架 | Magisk | 开源的 Android Root 解决方案，以 Systemless 方式挂载修改，不修改系统分区，支持 MagiskHide 隐藏 Root。 |
| KernelSU 框架 | KernelSU | 基于内核的 Android Root 方案，在内核层面实现 su 权限管理，比 Magisk 更难被检测。 |
| Riru 模块 | Riru | 通过注入 Zygote 进程来实现模块化功能扩展的框架，是 LSPosed 等模块的基础（已逐步被 Zygisk 取代）。 |
| Zygisk 注入 | Zygisk | Magisk 内置的 Zygote 注入机制，替代 Riru 成为新的模块加载方式，与 Magisk 深度集成。 |
| unidbg 模拟器 | unidbg | 基于 Unicorn 引擎的 Android Native 函数模拟执行框架，可在 PC 上脱离 Android 环境运行 SO 中的函数。 |
| Unicorn 引擎 | Unicorn Engine | 轻量级的多架构 CPU 模拟器引擎，支持 ARM/x86/MIPS 等，常用于模拟执行二进制代码片段。 |
| Charles 抓包 | Charles Proxy | 跨平台的 HTTP/HTTPS 抓包工具，提供图形界面，可拦截、查看和修改网络请求。 |
| mitmproxy 抓包 | mitmproxy | 开源的交互式 HTTPS 代理工具，支持命令行和 Web 界面，可通过 Python 脚本扩展功能。 |
| Burp Suite 工具 | Burp Suite | 业界标准的 Web 安全测试平台，功能强大的拦截代理，常用于 API 分析和安全测试。 |
| Wireshark 抓包 | Wireshark | 网络协议分析器，可捕获和分析网络层数据包，支持数百种协议的深度解析。 |
| Android Studio | Android Studio | Google 官方的 Android 开发 IDE，内置了调试器、Profiler、APK 分析器等逆向分析中也有用的工具。 |
| LLDB 调试器 | LLDB | LLVM 项目的调试器，Android NDK 默认使用的 Native 代码调试工具。 |
| GDB 调试器 | GDB (GNU Debugger) | 经典的 GNU 调试器，支持远程调试 Android Native 代码，常配合 gdbserver 使用。 |
| Frida-tools 工具集 | frida-tools | Frida 官方提供的命令行工具集，包括 frida-ps、frida-trace、frida-discover 等常用工具。 |
| Fridump 工具 | Fridump | 基于 Frida 的内存转储工具，可导出目标进程的内存内容用于搜索敏感数据。 |
| Cydia Substrate | Cydia Substrate | 早期的移动平台 Hook 框架，最初用于 iOS 越狱插件开发，也曾支持 Android。 |
| 010 Editor | 010 Editor | 专业的十六进制/二进制编辑器，支持 Binary Template 语法以结构化方式解析二进制文件格式。 |
| Capstone 引擎 | Capstone | 轻量级的多架构反汇编引擎库，支持 ARM/x86/MIPS 等，常被集成到其他逆向工具中。 |
| Keystone 引擎 | Keystone | 轻量级的多架构汇编引擎库，Capstone 的互补工具，可将汇编代码编译为机器码。 |
| Drozer 工具 | Drozer | Android 安全评估框架，用于发现应用的攻击面，测试 Activity、Content Provider 等组件的安全性。 |
| QEMU 模拟器 | QEMU | 开源的通用处理器模拟器，Android 模拟器（AVD）基于 QEMU，也可用于运行其他架构的二进制文件。 |
| CyberChef 工具 | CyberChef | GCHQ 开源的数据转换和分析工具，提供 Web 界面，可方便地进行编码、解码、加解密等操作。 |

---

## 8. 数据采集 (Data Collection & Scraping)

数据采集、爬虫技术和反爬对抗相关的术语。

| 中文名称 | 英文名称 | 说明 |
|---------|---------|------|
| 网络爬虫 | Web Crawler / Spider | 自动浏览和抓取网页内容的程序，按照链接结构系统性地遍历网站。 |
| 数据抓取 | Scraping / Data Scraping | 从网页或应用中自动提取结构化数据的技术，通常需要解析 HTML 或 API 响应。 |
| API 采集 | API Scraping | 直接调用应用或网站的后端 API 接口来获取数据，效率高于页面抓取，常需要逆向签名算法。 |
| 代理池 | Proxy Pool | 维护大量代理 IP 地址的资源池，用于分散请求来源以避免 IP 被封锁。 |
| IP 轮换 | IP Rotation | 在多个代理 IP 之间自动切换，使每个请求来自不同的 IP 地址，降低被检测的风险。 |
| 频率限制 | Rate Limiting | 服务器限制单个客户端在一定时间内的请求次数，是最基本的反爬措施之一。 |
| 验证码 | CAPTCHA (Completely Automated Public Turing test to tell Computers and Humans Apart) | 用于区分人类用户和自动程序的挑战-响应测试，包括图片验证码、滑块验证码、行为验证等。 |
| 指纹检测 | Fingerprinting | 通过收集设备/浏览器的各种特征信息（UA、分辨率、Canvas、WebGL 等）来唯一标识用户的技术。 |
| 设备指纹 | Device Fingerprint | 基于设备硬件和软件特征（IMEI、Android ID、传感器等）生成的唯一标识符，用于追踪和风控。 |
| 浏览器指纹 | Browser Fingerprint | 通过 Canvas、WebGL、字体列表、插件等浏览器特征生成的唯一标识，无需 Cookie 即可追踪用户。 |
| User-Agent 标识 | User-Agent (UA) | HTTP 请求头中标识客户端软件信息的字段，反爬系统常通过 UA 检测异常请求。 |
| Cookie 管理 | Cookie | 服务器存储在客户端的小型数据文件，用于维持会话状态和用户标识，爬虫需要正确管理 Cookie。 |
| 反爬虫机制 | Anti-Scraping / Anti-Bot | 网站或应用用于检测和阻止自动化数据采集的各种防御措施的统称。 |
| 风险控制 | Risk Control (风控) | 服务器端通过分析用户行为模式、设备信息、请求频率等来识别异常行为并采取限制措施。 |
| 请求头伪装 | Header Spoofing | 修改 HTTP 请求头（如 User-Agent、Referer 等）使请求看起来来自正常浏览器或应用。 |
| Selenium 自动化 | Selenium | 浏览器自动化测试框架，可模拟真实用户操作网页，常用于需要 JavaScript 渲染的页面数据采集。 |
| Appium 自动化 | Appium | 移动应用自动化测试框架，支持 Android/iOS 应用的自动化操作，可用于 App 数据采集。 |
| adb 自动化 | ADB Automation | 通过 ADB 命令模拟触摸、滑动、输入等操作来自动化控制 Android 设备，是简易的 App 数据采集方式。 |
| 协议还原 | Protocol Reverse Engineering | 通过抓包分析还原应用的通信协议细节（加密方式、签名算法、参数含义），是 API 采集的关键步骤。 |
| 接口签名还原 | Signature Algorithm Reverse | 逆向分析应用的请求签名生成算法，使爬虫能够构造出服务器可接受的合法签名。 |
| 无头浏览器 | Headless Browser | 没有图形界面的浏览器实例（如 Headless Chrome、Puppeteer），可在后台自动化执行网页操作。 |
| 会话管理 | Session Management | 在多次请求之间维护登录状态和上下文信息，爬虫需要正确处理 Token 刷新和会话过期。 |
| 数据清洗 | Data Cleaning | 对采集到的原始数据进行去重、格式化、纠错等处理，使其达到可用的质量标准。 |
| OCR 识别 | OCR (Optical Character Recognition) | 光学字符识别技术，用于将图片中的文字转换为可编辑文本，常用于识别图片验证码。 |
| 滑块验证 | Slider CAPTCHA | 需要用户拖动滑块到正确位置的验证码类型，自动化破解需要图像识别和轨迹模拟。 |
| 行为验证 | Behavioral Verification | 通过分析用户的鼠标轨迹、键盘输入模式、触摸手势等行为特征来判断是否为真人操作。 |

---

## 9. 其他常用术语 (Other Common Terms)

不属于以上分类但在逆向工程中经常遇到的术语。

| 中文名称 | 英文名称 | 说明 |
|---------|---------|------|
| 重打包 | Repackaging | 反编译 APK 后修改代码或资源，再重新签名打包为可安装的 APK 的过程。 |
| 二次打包检测 | Repackaging Detection | 应用检测自身是否被重新打包和签名的保护机制，通常通过校验签名证书实现。 |
| 内存转储 | Memory Dump | 将进程运行时的内存内容保存到文件中，用于分析加密数据、脱壳或提取运行时信息。 |
| 类加载器 | ClassLoader | Java/Android 中负责加载类的组件，加固方案常自定义 ClassLoader 来实现 DEX 的动态解密加载。 |
| 反射 | Reflection | Java 的一种机制，允许在运行时检查和操作类、方法和字段，常用于绕过访问限制或调用隐藏 API。 |
| 序列化 | Serialization | 将对象转换为字节流的过程，用于存储或网络传输，反序列化是其逆过程。 |
| Native 方法注册 | RegisterNatives | JNI 中动态注册 Native 方法与 Java 方法映射关系的函数，静态注册则通过固定的命名规则实现。 |
| 系统属性 | System Properties | Android 系统的键值对配置（如 ro.build.fingerprint），通过 getprop 命令读取，常被检测机制引用。 |
| Logcat 日志 | Logcat | Android 系统的日志系统，记录应用和系统的运行日志，`adb logcat` 是调试和分析时的重要信息来源。 |
| FART 脱壳 | FART (ART Runtime Unpacker) | 基于 ART 主动调用原理的 Android 脱壳工具，通过修改系统源码实现对加固应用的自动化脱壳。 |
| DexDump 脱壳 | DexDump | 从运行中的进程内存中提取 DEX 文件的工具，常基于 Frida 实现，用于脱壳加固应用。 |
| IL2CPP 逆向 | IL2CPP (Intermediate Language To C++) | Unity 游戏引擎的脚本后端，将 C# 代码编译为 C++，全局元数据文件 (global-metadata.dat) 是逆向分析的关键。 |
| so 加载 | SO Loading (dlopen/dlsym) | Android 中通过 dlopen 加载动态库、dlsym 查找符号的过程，Hook 这些函数可监控库加载行为。 |
| init_array | .init_array Section | ELF 文件中在 main 函数执行前自动调用的初始化函数数组，加固方案常在此处执行解密逻辑。 |
| JNI_OnLoad | JNI_OnLoad | 共享库被 Java 层 System.loadLibrary 加载时自动调用的函数，常用于动态注册 Native 方法和执行初始化。 |
| maps 文件 | /proc/self/maps | Linux 进程的内存映射文件，显示进程的所有内存区域和加载的共享库，是分析内存布局的重要依据。 |
| Dex 优化 | Dexopt / dex2oat | Android 系统将 DEX 编译为优化格式（ODEX/OAT）的过程，dex2oat 是 ART 使用的编译工具。 |
| 方法分辨率 | Method Resolution | ART 根据方法签名和类层次关系查找实际要调用的方法实现的过程。 |
| Linker 链接器 | Linker (/system/bin/linker64) | Android 系统的动态链接器，负责在运行时加载和链接共享库（SO 文件），Hook linker 可监控库加载。 |
| 脱壳点 | Unpacking Point | 在加固应用执行过程中，原始 DEX 已被解密且完整存在于内存中的时机，是执行内存 dump 的最佳时机。 |
| 主动调用 | Active Invocation | 一种脱壳技术，通过主动调用类的所有方法来触发 ART 对方法体的还原，从而获取完整的 DEX 数据。 |
| Smali 注入 | Smali Injection | 在反编译后的 Smali 代码中插入自定义逻辑（如日志打印），然后重新打包运行以辅助分析。 |
| 模糊测试 | Fuzzing | 向程序输入大量随机或变异的数据以触发崩溃和异常行为的自动化测试技术，用于发现安全漏洞。 |
| 符号执行 | Symbolic Execution | 使用符号值（而非具体值）执行程序以探索所有可能路径的分析技术，可用于自动化求解混淆后的逻辑。 |
| CTF 竞赛 | CTF (Capture The Flag) | 信息安全领域的竞赛形式，参赛者需要通过逆向工程、漏洞利用等技术找到隐藏的 Flag。 |
| PoC 验证 | PoC (Proof of Concept) | 漏洞概念验证代码，用于证明安全漏洞的存在和可利用性。 |
| CVE 编号 | CVE (Common Vulnerabilities and Exposures) | 公开已知安全漏洞的统一标识编号系统，如 CVE-2023-XXXXX。 |
