# 配方编号系统

---

本书采用系统化的编号方式组织内容，帮助你快速定位所需信息。

---

## 章节编号规则

本书分为六大部分，每部分有独立的编号前缀：

| 编号前缀 | 章节名称 | 内容定位 | 示例 |
|---------|---------|---------|------|
| **R** | Recipes | 场景化解决方案（核心内容） | R01, R02... |
| **T** | Tools | 工具使用指南与原理 | T01, T02... |
| **C** | Case Studies | 实战案例分析 | C01, C02... |
| **F** | Foundations | 基础知识参考 | F01, F02... |
| **A** | Advanced | 高级主题参考 | A01, A02... |
| **E** | Engineering | 工程化参考 | E01, E02... |
| **X** | Appendix | 附录资源与索引 | X01, X02... |

---

## Recipes 分类编号

**Recipes**（配方）是本书的核心内容，按照问题场景分类：

### 01-Recipes/Network (NET)
**网络与加密相关配方**

| 配方编号 | 配方名称 | 解决的问题 |
|---------|---------|-----------|
| NET-01 | Network Sniffing | 网络抓包与协议分析 |
| NET-02 | Crypto Analysis | 加密算法分析与还原 |
| NET-03 | TLS Fingerprinting | TLS 指纹识别与处理 |
| NET-04 | JA3 Fingerprinting | JA3 指纹分析 |
| NET-05 | JA4 Fingerprinting | JA4 指纹分析 |

### 01-Recipes/Anti-Detection (AD)
**反检测与对抗相关配方**

| 配方编号 | 配方名称 | 解决的问题 |
|---------|---------|-----------|
| AD-01 | Frida Anti Debugging | Frida 反调试检测绕过 |
| AD-02 | Xposed Anti Debugging | Xposed 反检测绕过 |
| AD-03 | Captcha Bypassing | 验证码识别与绕过 |
| AD-04 | App Hardening ID | 加固方案识别 |
| AD-05 | Device Fingerprinting | 设备指纹采集与绕过 |
| AD-06 | Mobile App Security | 移动端安全与反机器人 |

### 01-Recipes/Unpacking (UNP)
**脱壳与修复相关配方**

| 配方编号 | 配方名称 | 解决的问题 |
|---------|---------|-----------|
| UNP-01 | Unpacking | 通用脱壳技术 |
| UNP-02 | Frida Unpacking | Frida 脱壳与 SO 修复 |
| UNP-03 | SO Deobfuscation | SO 文件反混淆 |
| UNP-04 | SO String Deobfuscation | SO 字符串解密 |

### 01-Recipes/Analysis (ANA)
**分析与调试相关配方**

| 配方编号 | 配方名称 | 解决的问题 |
|---------|---------|-----------|
| ANA-01 | RE Workflow | 逆向工程标准工作流 |
| ANA-02 | Static Analysis | 静态分析深入 |
| ANA-03 | Dynamic Analysis | 动态分析深入 |
| ANA-04 | OLLVM Deobfuscation | OLLVM 混淆还原 |
| ANA-05 | VMP Analysis | 虚拟机保护分析 |
| ANA-06 | JS Obfuscator | JavaScript 混淆分析 |
| ANA-07 | JS VMP | JavaScript 虚拟机保护 |
| ANA-08 | Native String | Native 字符串混淆 |

### 01-Recipes/Automation (AUTO)
**自动化与规模化相关配方**

| 配方编号 | 配方名称 | 解决的问题 |
|---------|---------|-----------|
| AUTO-01 | Device Farming | 自动化与设备群控 |
| AUTO-02 | Dial Up Proxy | 动态拨号代理池 |
| AUTO-03 | Proxy Pool Design | 代理池架构设计 |
| AUTO-04 | Scrapy | Scrapy 爬虫框架 |
| AUTO-05 | Scrapy Redis | 分布式 Scrapy |
| AUTO-06 | Docker Deployment | Docker 容器部署 |
| AUTO-07 | Virtualization | 虚拟化与容器技术 |
| AUTO-08 | Web Anti Scraping | Web 反爬虫对抗 |

### 01-Recipes/Scripts (SCR)
**脚本集合**

| 配方编号 | 配方名称 | 内容说明 |
|---------|---------|---------|
| SCR-01 | Frida Examples | Frida 脚本示例集 |
| SCR-02 | Frida Common | Frida 常用脚本 |
| SCR-03 | Automation Scripts | 自动化脚本集 |
| SCR-04 | Native Hooking | Native Hook 模式 |
| SCR-05 | Objection Snippets | Objection 代码片段 |
| SCR-06 | C For Emulation | C 语言仿真代码 |

---

## Tools 编号 (T)

工具使用指南和原理剖析，按功能分类。

### Dynamic - 动态分析工具

| 编号 | 工具名称 | 内容类型 |
|-----|---------|---------|
| T01 | Frida Guide | 使用指南 |
| T02 | Frida Internals | 内部原理 |
| T03 | Xposed Guide | 使用指南 |
| T04 | Xposed Internals | 内部原理 |
| T05 | Unidbg Guide | 使用指南 |
| T06 | Unidbg Internals | 内部原理 |

### Static - 静态分析工具

| 编号 | 工具名称 | 内容类型 |
|-----|---------|---------|
| T07 | Ghidra Guide | 使用指南 |
| T08 | IDA Pro Guide | 使用指南 |
| T09 | Radare2 Guide | 使用指南 |

### Cheatsheets - 速查表

| 编号 | 名称 | 内容说明 |
|-----|-----|---------|
| T10 | ADB Cheatsheet | ADB 命令速查 |

---

## Case Studies 编号 (C)

真实场景的案例分析，综合运用各类技术。

| 编号 | 案例名称 | 分析对象 |
|-----|---------|---------|
| C01 | Anti Analysis Techniques | 反分析技术案例 |
| C02 | Music Apps | 音乐 App 分析 |
| C03 | Social Media & Anti Bot | 社交媒体与风控 |
| C04 | App Encryption | 应用加密案例 |
| C05 | Video Apps & DRM | 视频 App 与 DRM |
| C06 | Unity Games (Il2Cpp) | Unity 游戏分析 |
| C07 | Flutter Apps | Flutter 应用分析 |
| C08 | Malware Analysis | 恶意软件分析 |

---

## Reference 编号

参考资料和理论知识，按主题分类。

### Foundations 基础知识 (F)

| 编号 | 主题 | 内容说明 |
|-----|-----|---------|
| F01 | APK Structure | APK 文件结构 |
| F02 | Android Components | 四大组件 |
| F03 | Android Manifest | 清单文件解析 |
| F04 | Android Studio Debug Tools | 调试工具 |
| F05 | DEX Format | DEX 文件格式 |
| F06 | Smali Syntax | Smali 语法 |
| F07 | SO ELF Format | ELF 文件格式 |
| F08 | ART Runtime | ART 运行时 |
| F09 | ARM Assembly | ARM 汇编 |
| F10 | x86 & ARM Assembly Basics | 汇编基础 |
| F11 | TOTP | 时间动态密码原理 |

### Advanced 高级主题 (A)

| 编号 | 主题 | 内容说明 |
|-----|-----|---------|
| A01 | Android Sandbox Implementation | 沙箱实现原理 |
| A02 | AOSP & System Customization | AOSP 系统定制 |
| A03 | AOSP Device Modification | 设备修改 |
| A04 | Minimal Android Rootfs | 最小化根文件系统 |
| A05 | SO Anti Debugging & Obfuscation | SO 反调试与混淆 |
| A06 | SO Runtime Emulation | SO 运行时仿真 |

### Engineering 工程化 (E)

| 编号 | 主题 | 内容说明 |
|-----|-----|---------|
| E01 | Frameworks & Middleware | 框架与中间件 |
| E02 | Message Queues | 消息队列 |
| E03 | Redis | Redis 数据库 |
| E04 | Risk Control SDK Build Guide | 风控 SDK 构建 |
| E05 | Data Warehousing & Processing | 数据仓库与处理 |
| E06 | Flink | 流处理框架 |
| E07 | HBase | 分布式数据库 |
| E08 | Hive | 数据仓库 |
| E09 | Spark | 大数据处理 |
| E10 | Automation vs API Reverse | 群控与API逆向对比 |

---

## Appendix 编号 (X)

附录资源和社区资源。

| 编号 | 名称 | 内容说明 |
|-----|-----|---------|
| X01 | Github Projects | 开源项目推荐 |
| X02 | Learning Resources | 学习资源汇总 |
| X03 | CTF Platforms | CTF 平台推荐 |
| X04 | Glossary | 术语表 |

---

## 如何使用编号系统

### 快速引用

在讨论或笔记中，你可以使用简短的编号引用特定配方：

- "参考 R02 了解加密分析方法"
- "这个问题可以用 R06 的方法解决"
- "代码示例见 R32"
- "工具使用参考 T01"

### 交叉引用

本书各章节之间存在大量交叉引用，编号系统帮助你快速定位：

```
分析加密算法时 (R02)，可能需要先脱壳 (R12)，
然后使用 Frida (T01) 进行动态分析 (R18)，
参考 C04 了解完整案例。
```

### 学习路径规划

你可以根据编号规划自己的学习路径：

**初学者路径**：
```
F01 → F05 → T01 → R01 → R06
```

**爬虫开发者路径**：
```
R01 → R02 → R10 → R27 → R28
```

**安全研究员路径**：
```
R16 → R12 → R19 → A05 → C08
```

---

## 版本说明

本编号系统会随着内容更新而扩展。新增配方将获得新的编号，已有配方的编号保持不变，确保引用的稳定性。

当前版本：**v1.0**

---

**现在你已经了解了本书的组织结构，开始你的学习之旅吧！**

**推荐下一步**：[10 分钟快速入门](./index.md)
