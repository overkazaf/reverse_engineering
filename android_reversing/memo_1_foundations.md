# 📱 Android 逆向基础知识速记

## 📦 APK 文件结构

### 🗂️ 主要组成
```
/
├── AndroidManifest.xml       # [必需] 应用清单文件
├── classes.dex              # [必需] Dalvik 字节码文件
├── classes2.dex             # [可选] Multi-DEX 时的额外代码
├── resources.arsc           # [必需] 预编译资源文件索引
├── res/                     # [必需] 未编译资源目录
├── lib/                     # [可选] 原生库(.so文件)目录
├── assets/                  # [可选] 原始资源目录
└── META-INF/                # [必需] 签名和证书信息
```

### 🔧 处理方法
- **解包**: `apktool d myapp.apk` 或 `unzip myapp.apk`
- **反编译**: `jadx-gui myapp.apk` 直接查看 Java 代码
- **动态分析**: `adb install` + `frida` Hook 运行时行为

---

## 🏗️ ARM 汇编基础

### 📋 指令分类
- **数据移动**: `MOV R1, R2` / `LDR R0, [SP, #4]` / `STR R0, [SP, #4]`
- **地址加载**: `ADR X0, aHelloWorld`
- **算术逻辑**: 加减乘除、位运算
- **分支跳转**: 条件执行、函数调用
- **栈操作**: Push/Pop 指令

---

## ⚡ ART Runtime 详解

### 🔄 执行模式演进

| 特性 | Dalvik (JIT) | ART (AOT) | ART 混合模式 |
|:---|:---|:---|:---|
| **编译时机** | 运行时编译 | 安装时编译 | 安装快速 + 运行时优化 |
| **性能** | 较低 | 高 | 平衡 |
| **启动速度** | 慢 | 快 | 快 |
| **存储占用** | 小 | 大 | 适中 |
| **安装时间** | 快 | 慢 | 快 |

### 📊 ART 混合编译流程
```
1. 初次安装 → 快速安装，无AOT编译
2. 首次运行 → 解释执行 + JIT编译热点 + 生成Profile
3. 设备空闲 → 根据Profile进行AOT编译热点代码
```

### 🎯 对逆向的影响
- **Hook 复杂化**: 需要处理 AOT 编译后的机器码
- **脱壳难度增加**: 需要监控 OAT 文件和 dex2oat 调用
- **分析工具**: 使用 `oatdump` 分析 OAT 文件

---

## 📋 DEX 文件格式

### 📊 DEX vs CLASS 对比

| 特性 | .class (JVM) | .dex (Android) |
|:---|:---|:---|
| **文件数量** | 每个源文件对应一个 | 多个class合并成单个dex |
| **指令架构** | 基于栈 | 基于寄存器 |
| **常量池** | 独立常量池 | 全局共享常量池 |
| **冗余度** | 高 | 低（去重优化） |

### 🏗️ DEX 结构层次（记忆口诀）

```
📚 基础标识层 (IDs): String → Type → Field → Method
   "字符串是基础，类型靠字符串，字段方法都要类型"

📐 原型定义层: Proto IDs
   "原型描述方法长什么样"

🏛️ 类结构层: Class Defs  
   "类定义是骨架，把所有ID组装成完整的类"

💾 实际内容层: Data Section
   "数据区是血肉，存放真正的代码和数据"
```

### 🔧 运行原理
- **Dalvik (4.4-)**: JIT 编译 DEX 字节码
- **ART (4.4+)**: AOT (dex2oat) + JIT 混合优化

---

## 🔧 Smali 汇编语言

Smali 是 Dalvik 字节码的人类可读表示，是静态 patching 的关键工具。

---

## 📚 Android .so 文件详解 (ELF)

### 🏗️ ELF 文件结构

#### 📋 ELF Header
- **Magic Number**: 文件识别标识
- **Architecture**: CPU 架构 (ARM/ARM64/x86)
- **Type**: 文件类型 (可执行/共享库)
- **Entry Point**: 程序启动地址

#### 📊 关键 Section

| Section | 作用 | 重要性 |
|:---|:---|:---|
| **.text** | 程序机器码 | ⭐⭐⭐⭐⭐ |
| **.rodata** | 只读数据(字符串常量) | ⭐⭐⭐⭐ |
| **.data** | 已初始化全局变量 | ⭐⭐⭐ |
| **.bss** | 未初始化数据区 | ⭐⭐ |
| **.init_array** | 库加载时执行的函数 | ⭐⭐⭐⭐⭐ |
| **.dynsym** | 动态符号表 | ⭐⭐⭐⭐ |

### 🔗 加载与链接流程
```
System.loadLibrary() → linker → ELF解析 → 内存映射 → 
符号解析 → .init_array执行 → JNI_OnLoad调用
```

### 🛡️ 常见保护与对抗

| 保护手段 | 攻击方法 |
|:---|:---|
| **字符串加密** | Hook解密函数、内存Dump |
| **代码混淆(OLLVM)** | 动态分析、去混淆工具(d810) |
| **反调试** | Hook检测函数、环境伪装 |

---

## 🎯 常见面试题及答案

### Q1: 解释 ART 和 Dalvik 的主要区别？
**A**: Dalvik 使用 JIT 在运行时编译，ART 使用 AOT 在安装时编译。从 Android 7.0 开始，ART 采用混合模式：安装时快速安装 + 运行时 JIT + 空闲时 AOT 优化热点代码。

### Q2: DEX 文件相比 CLASS 文件有什么优势？
**A**: 
- 文件合并减少I/O开销
- 全局常量池去重
- 基于寄存器的指令集更适合移动设备
- 字符串和元数据去重，减少内存占用

### Q3: init_array 段在逆向分析中的重要性？
**A**: init_array 存储在库加载时自动执行的函数指针，常被用于：
- 反调试检测
- 密钥初始化
- 运行时解密
- 环境检测
是分析 SO 文件的重要入口点。

### Q4: 如何分析被混淆的 Native 代码？
**A**: 
1. **静态分析**: 使用去混淆工具如 d810
2. **动态分析**: Frida Hook 关键函数
3. **模拟执行**: Unidbg 黑盒调用
4. **指令级分析**: 单步调试跟踪执行流

### Q5: OAT 文件在 Android 逆向中的作用？
**A**: OAT 是 ART 预编译的机器码文件，包含：
- 原始 DEX 数据
- 编译后的机器码
- 元数据信息
脱壳时需要同时关注 DEX 和 OAT 文件的生成。

### Q6: JNI 函数命名规则是什么？
**A**: `Java_包名_类名_方法名`，其中包名和类名的点号替换为下划线。
例如：`com.example.Test.native_func` → `Java_com_example_Test_native_1func`

### Q7: 如何快速定位 SO 文件中的关键逻辑？
**A**: 
1. 分析导出函数和 JNI 函数
2. 检查 init_array 中的初始化函数  
3. 搜索敏感字符串的交叉引用
4. Hook 高频调用的函数
5. 分析程序入口点和关键API调用

### Q8: ARM64 和 ARM32 汇编的主要区别？
**A**: 
- **寄存器**: ARM64 有 31 个 64 位通用寄存器 (X0-X30)，ARM32 有 16 个 32 位寄存器 (R0-R15)
- **指令长度**: ARM64 固定 4 字节，ARM32 支持 Thumb 模式（2字节）
- **调用约定**: ARM64 前 8 个参数用寄存器传递，ARM32 前 4 个
- **地址空间**: ARM64 支持更大的虚拟地址空间

### Q9: SSL/TLS 连接过程分析？
**A**:
SSL/TLS 握手过程主要目的是安全地协商出对称加密密钥，流程如下：
1.  **ClientHello**: 客户端发送支持的TLS版本、密码套件列表和一个随机数 `client_random`。
2.  **ServerHello**: 服务器选择一个TLS版本和密码套件，并返回自己的随机数 `server_random`。
3.  **Certificate**: 服务器发送其数字证书，其中包含服务器的公钥。
4.  **ServerHelloDone**: 服务器告知客户端初始协商结束。
5.  **ClientKeyExchange**: 客户端生成一个预主密钥 `pre-master secret`，用服务器的公钥加密后发送给服务器。
6.  **ChangeCipherSpec**: 客户端通知服务器，后续通信将使用协商好的密钥进行加密。
7.  **Finished**: 客户端发送一个加密的、包含前面所有握手消息摘要的 `Finished` 消息，供服务器校验。
8.  **服务器解密与验证**: 服务器用自己的私钥解密得到 `pre-master secret`，并与客户端一样，各自生成主密钥和会话密钥。然后也发送 `ChangeCipherSpec` 和 `Finished` 消息给客户端。
9.  **加密通信**: 握手完成，双方使用对称的会话密钥进行加密通信。
