# 快速开始指南

## 项目概览

本项目包含两个逆向工程手册：

| 项目 | 描述 | 文章数 |
|------|------|--------|
| **Android 逆向工程烹饪食谱** | Android 应用逆向分析完整指南 | 72+ 篇 |
| **Web 逆向工程烹饪食谱** | Web 应用逆向分析完整指南 | 60+ 篇 |

---

## 快速启动

### 1. Android 逆向工程

```bash
# 进入 Android 项目目录
cd android_reversing

# 创建虚拟环境 (推荐)
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt

# 启动 MkDocs 服务器
mkdocs serve

# 访问 http://127.0.0.1:8000
```

### 2. Web 逆向工程

```bash
# 进入 Web 项目目录
cd web_reversing

# 创建虚拟环境 (推荐)
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt

# 启动 MkDocs 服务器
mkdocs serve

# 访问 http://127.0.0.1:8000
```

---

## 生成 PDF 文档

使用项目根目录的统一 PDF 生成脚本，所有 PDF 输出到 `output/` 目录：

```bash
# 安装 PDF 生成依赖
pip install mistune weasyprint pillow pyyaml

# 生成 Android PDF
python generate_pdf.py android

# 生成 Web PDF
python generate_pdf.py web

# 生成两个项目的 PDF
python generate_pdf.py all

# 使用更多并行进程加速
python generate_pdf.py all -w 8

# 禁用缓存（文件修改后）
python generate_pdf.py android --no-cache

# 自动修复格式问题
python generate_pdf.py web --fix-files
```

**输出位置：**
```
output/
├── android_reverse_engineering_cookbook.pdf  # Android PDF
├── web_reverse_engineering_cookbook.pdf      # Web PDF
├── android_debug.html                        # 调试用 HTML
└── web_debug.html                            # 调试用 HTML
```

---

## 构建静态网站

```bash
# Android 项目
cd android_reversing && mkdocs build
# 输出目录: site/

# Web 项目
cd web_reversing && mkdocs build
# 输出目录: site/
```

---

## 项目结构

```
reverse_engineering/
├── README.md                   # 项目总体介绍
├── QUICK_START.md              # 本文件 - 快速开始指南
├── generate_pdf.py             # 统一 PDF 生成脚本
├── output/                     # PDF 统一输出目录
│   ├── android_reverse_engineering_cookbook.pdf
│   └── web_reverse_engineering_cookbook.pdf
│
├── android_reversing/          # Android 逆向工程
│   ├── docs/
│   │   ├── 00-Quick-Start/     # 快速入门
│   │   ├── 01-Recipes/         # 实战食谱
│   │   │   ├── Automation/     # 自动化与爬虫
│   │   │   ├── Network/        # 网络分析
│   │   │   ├── Scripts/        # Frida 脚本
│   │   │   └── Unpacking/      # 脱壳与修复
│   │   ├── 02-Tools/           # 工具详解
│   │   ├── 03-Case-Studies/    # 案例研究
│   │   ├── 04-Reference/       # 参考资料
│   │   └── 05-Appendix/        # 附录
│   ├── playground/             # 实践代码
│   ├── mkdocs.yml              # MkDocs 配置
│   └── README_FINAL.md         # Android 项目说明
│
└── web_reversing/              # Web 逆向工程
    ├── docs/
    │   ├── 00-Quick-Start/     # 快速入门
    │   ├── 01-Foundations/     # 基础原理
    │   ├── 02-Tooling/         # 工具指南
    │   ├── 03-Basic-Recipes/   # 基础食谱
    │   ├── 04-Advanced-Recipes/# 高级食谱
    │   ├── 05-Case-Studies/    # 案例研究
    │   ├── 06-Engineering/     # 工程化
    │   ├── 07-Scripts/         # 脚本范例
    │   ├── 08-Cheat-Sheets/    # 速查表
    │   ├── 09-Templates/       # 模板
    │   ├── 10-Troubleshooting/ # 故障排除
    │   └── 11-Resources/       # 资源链接
    ├── mkdocs.yml              # MkDocs 配置
    └── README.md               # Web 项目说明
```

---

## 内容概览

### Android 逆向工程

| 章节 | 内容 |
|------|------|
| **Quick-Start** | 环境配置、工具安装 |
| **Recipes** | Frida 脚本、网络分析、脱壳修复、自动化爬虫 |
| **Tools** | Frida、Unidbg、Xposed、IDA Pro、Ghidra |
| **Case-Studies** | 音乐 App、视频 DRM、社交反爬、风控 SDK |
| **Reference** | ARM 汇编、Smali 语法、ART 运行时 |
| **Appendix** | 术语表、资源链接 |

### Web 逆向工程

| 章节 | 内容 |
|------|------|
| **Quick-Start** | 环境配置、工具安装 |
| **Foundations** | HTTP/HTTPS、JavaScript、浏览器架构、WebAssembly |
| **Tooling** | Chrome DevTools、Burp Suite、Puppeteer、AST 工具 |
| **Basic-Recipes** | JS Hook、断点调试、请求拦截 |
| **Advanced-Recipes** | JSVMP 分析、反指纹、验证码绕过 |
| **Case-Studies** | 电商、社交媒体、金融网站 |
| **Engineering** | 分布式爬虫、代理池、Docker 部署 |
| **Cheat-Sheets** | 常用命令速查 |
| **Templates** | 脚本模板、配置模板 |
| **Troubleshooting** | 常见问题解决 |

---

## 核心工具

### Android 工具

| 工具 | 用途 |
|------|------|
| **Frida** | 动态插桩框架，Hook Java/Native 函数 |
| **Unidbg** | Native 库模拟执行，无需真机 |
| **Xposed** | 系统级 Hook 框架 |
| **IDA Pro** | 静态逆向分析 |
| **Ghidra** | 开源逆向工程工具 |

### Web 工具

| 工具 | 用途 |
|------|------|
| **Chrome DevTools** | 浏览器调试、网络分析 |
| **Burp Suite** | Web 请求拦截与修改 |
| **Puppeteer/Playwright** | 无头浏览器自动化 |
| **Babel/AST** | JavaScript 代码分析与转换 |
| **Wireshark** | 网络协议分析 |

---

## 常见问题

### Q: MkDocs 启动失败？

检查是否安装了所有依赖：
```bash
pip install -r requirements.txt
```

### Q: PDF 生成失败？

确保安装了 WeasyPrint 的系统依赖：
```bash
# macOS
brew install cairo pango gdk-pixbuf libffi

# Ubuntu/Debian
sudo apt-get install build-essential python3-dev python3-pip \
    python3-setuptools python3-wheel python3-cffi libcairo2 \
    libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 \
    libffi-dev shared-mime-info

# Windows
# 使用 GTK+ for Windows Runtime Environment Installer
```

### Q: 如何部署到 GitHub Pages？

```bash
# 构建并部署
mkdocs gh-deploy
```

### Q: 端口被占用？

```bash
# 使用其他端口
mkdocs serve -a 127.0.0.1:8080
```

---

## 技术栈

| 类别 | 技术 |
|------|------|
| **文档系统** | MkDocs + Material 主题 |
| **PDF 生成** | WeasyPrint + markdown2 |
| **语言** | Python 3.8+ |
| **格式** | Markdown (CommonMark) |

---

## 联系方式

- **Email**: overkazaf@gmail.com
- **WeChat**: _0xAF_

---

## 许可证

MIT License - 仅供学习和研究使用

---

**Happy Reversing!**
