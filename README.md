<div align="center">

![Stars](https://img.shields.io/github/stars/overkazaf/reverse_engineering?style=flat-square&color=58a6ff)
![Language](https://img.shields.io/github/languages/top/overkazaf/reverse_engineering?style=flat-square&color=58a6ff)
![Last Commit](https://img.shields.io/github/last-commit/overkazaf/reverse_engineering?style=flat-square&color=58a6ff)
![Repo Size](https://img.shields.io/github/repo-size/overkazaf/reverse_engineering?style=flat-square&color=58a6ff)

</div>

# 逆向工程烹饪食谱 (Reverse Engineering Cookbook)

欢迎来到逆向工程烹饪食谱！这是一个系统化的逆向工程学习资源库，涵盖 Android 和 Web 两大领域。

## 📚 项目概览

本项目包含两个子项目：

### 🤖 [Android 逆向工程烹饪食谱](./android_reversing/)

专注于 Android 应用逆向分析，涵盖：
- APK 结构、DEX 文件格式、ARM 汇编
- Frida、Xposed、Unidbg 等工具
- 脱壳、反混淆、加密分析等技术
- VMP、OLLVM、反调试等高级主题
- 分布式爬虫、消息队列、容器化等工程实践
- 音乐、视频、社交等应用案例

### 🌐 [Web 逆向工程烹饪食谱](./web_reversing/)

专注于 Web 应用逆向分析，涵盖：
- HTTP/HTTPS 协议、JavaScript、浏览器架构
- Burp Suite、Chrome DevTools、Puppeteer 等工具
- JS 反混淆、API 逆向、验证码绕过等技术
- JSVMP、反爬虫、浏览器指纹等高级主题
- 分布式爬虫、代理池、Docker 部署等工程实践
- 电商、社交、金融等网站案例

## 🎯 适用人群

- 安全研究人员
- 逆向工程师
- 爬虫开发者
- 移动/Web 开发者
- 对逆向技术感兴趣的学习者

## 🚀 快速开始

### Android 逆向

```bash
cd reverse_engineering/android_reversing
pip install -r requirements.txt
mkdocs serve
# 访问 http://127.0.0.1:8000
```

### Web 逆向

```bash
cd reverse_engineering/web_reversing
pip install -r requirements.txt
mkdocs serve
# 访问 http://127.0.0.1:8000
```

## 📖 目录结构

```
reverse_engineering/
├── android_reversing/          # Android 逆向工程
│   ├── docs/
│   │   ├── 00-Foundations/    # 基础原理
│   │   ├── 01-Tooling/        # 工具指南
│   │   ├── 02-Techniques/     # 实战技术
│   │   ├── 03-Advanced-Topics/# 高阶专题
│   │   ├── 04-Engineering/    # 工程化
│   │   ├── 05-Case-Studies/   # 案例研究
│   │   ├── 06-Data-Analysis/  # 数据分析
│   │   ├── 07-Scripts/        # 脚本范例
│   │   └── 08-Others/         # 其他资源
│   ├── playground/            # 实践代码
│   ├── mkdocs.yml
│   └── README.md
│
└── web_reversing/              # Web 逆向工程
    ├── docs/
    │   ├── 00-Foundations/    # 基础原理
    │   ├── 01-Tooling/        # 工具指南
    │   ├── 02-Techniques/     # 实战技术
    │   ├── 03-Advanced-Topics/# 高阶专题
    │   ├── 04-Engineering/    # 工程化
    │   ├── 05-Case-Studies/   # 案例研究
    │   ├── 06-Scripts/        # 脚本范例
    │   └── 07-Others/         # 其他资源
    ├── mkdocs.yml
    └── README.md
```

## 🔧 核心工具

### Android 工具
- **Frida**: 动态插桩框架
- **Xposed**: 系统级 Hook 框架
- **Unidbg**: Native 库模拟执行
- **IDA Pro**: 静态分析利器
- **Ghidra**: 开源逆向工程工具

### Web 工具
- **Burp Suite**: Web 安全测试工具
- **Chrome DevTools**: 浏览器开发者工具
- **Puppeteer/Playwright**: 无头浏览器
- **Babel/AST**: JavaScript 代码分析
- **Wireshark**: 网络协议分析

## 💡 学习路径

### 初学者路径 (3-6 个月)

1. **基础阶段** (1-2 个月)
   - 学习 00-Foundations 中的基础知识
   - Android: APK 结构、DEX 格式、ARM 汇编
   - Web: HTTP 协议、JavaScript、浏览器架构

2. **工具阶段** (1-2 个月)
   - 熟悉 01-Tooling 中的常用工具
   - Android: Frida、Xposed 基础使用
   - Web: DevTools、Burp Suite 基础使用

3. **实践阶段** (1-2 个月)
   - 练习 02-Techniques 中的基本技术
   - 参考 Scripts 中的脚本示例
   - 尝试简单的 Case Studies

### 进阶路径 (6-12 个月)

1. **深入技术** (2-3 个月)
   - 深入 03-Advanced-Topics 中的高级主题
   - Android: VMP、OLLVM、反调试
   - Web: JSVMP、反爬虫、浏览器指纹

2. **工程实践** (2-3 个月)
   - 学习 04-Engineering 中的工程化实践
   - 构建分布式爬虫系统
   - 实现自动化分析流程

3. **综合应用** (2-6 个月)
   - 研究 05-Case-Studies 中的实战案例
   - 独立完成复杂项目
   - 贡献自己的经验和脚本

## 🌟 特色亮点

- **系统化**: 从基础到高级，循序渐进
- **实战性**: 大量真实案例和可运行脚本
- **工程化**: 不仅教技术，更教工程实践
- **开源**: 持续更新，欢迎贡献
- **中文**: 完整的中文文档体系

## 💡 贡献指南

我们欢迎各种形式的贡献：

1. **内容贡献**
   - 完善现有文档
   - 添加新的技术文章
   - 分享案例研究

2. **代码贡献**
   - 提供实用脚本
   - 改进工具链
   - 修复 bug

3. **反馈建议**
   - 报告错误
   - 提出改进意见
   - 分享学习心得

## 📄 许可证

本项目采用 MIT 许可证，仅供学习和研究使用。

## ⚠️ 免责声明

本项目所有内容仅供学习和研究使用，请勿用于非法用途。

使用者应：
- 遵守当地法律法规
- 遵守目标应用/网站的服务条款
- 尊重知识产权
- 仅在授权环境中进行测试

项目维护者不对使用者的任何行为负责。

## 🔗 相关资源

### 社区
- [Frida 官方文档](https://frida.re/docs/)
- [OWASP](https://owasp.org/)
- [看雪论坛](https://bbs.pediy.com/)

### 工具
- [Frida](https://frida.re/)
- [Burp Suite](https://portswigger.net/burp)
- [IDA Pro](https://hex-rays.com/ida-pro/)
- [Ghidra](https://ghidra-sre.org/)

### 学习资源
- [Android Security Wiki](https://github.com/ashishb/android-security-awesome)
- [Web Security Academy](https://portswigger.net/web-security)

---

**Happy Reversing!** 🎉

如有问题或建议，欢迎提 Issue 或 PR。
