# Web 逆向工程烹饪食谱

欢迎来到 Web 逆向工程烹饪食谱！这是一个系统化的 Web 逆向工程学习资源库。

## 📚 内容概览

本项目系统性地组织了 Web 逆向工程领域的各类知识点，包括：

- **基础原理**: HTTP/HTTPS 协议、JavaScript、浏览器架构、WebAssembly 等
- **工具指南**: Burp Suite、Chrome DevTools、Puppeteer、AST 工具等
- **实战技术**: JS 反混淆、API 逆向、验证码绕过、调试技巧等
- **高阶专题**: JSVMP、反爬虫、浏览器指纹、前端加固等
- **工程化**: 分布式爬虫、代理池、Docker 部署、监控告警等
- **案例研究**: 电商、社交媒体、金融、视频网站等实战案例
- **脚本范例**: JavaScript Hook、反混淆、自动化等实用脚本

## 🚀 快速开始

### 在线阅读

使用 MkDocs 构建本地文档站点：

```bash
# 安装依赖
pip install -r requirements.txt

# 启动本地服务器
mkdocs serve

# 访问 http://127.0.0.1:8000
```

### 构建静态站点

```bash
# 构建静态 HTML
mkdocs build

# 输出在 site/ 目录
```

## 📖 目录结构

```
web_reversing/
├── docs/                       # 文档目录
│   ├── 00-Foundations/        # 基础原理
│   ├── 01-Tooling/            # 工具指南
│   ├── 02-Techniques/         # 实战技术
│   ├── 03-Advanced-Topics/    # 高阶专题
│   ├── 04-Engineering/        # 工程化
│   ├── 05-Case-Studies/       # 案例研究
│   ├── 06-Scripts/            # 脚本范例
│   └── 07-Others/             # 其他资源
├── mkdocs.yml                 # MkDocs 配置
├── generate_docs.py           # 文档生成脚本
├── requirements.txt           # Python 依赖
└── README.md                  # 本文件
```

## 🎯 学习路径

### 初学者路径

1. 先学习 **00-Foundations** 中的基础知识
2. 熟悉 **01-Tooling** 中的常用工具
3. 实践 **02-Techniques** 中的基本技术
4. 参考 **06-Scripts** 中的脚本示例

### 进阶路径

1. 深入 **03-Advanced-Topics** 中的高级主题
2. 学习 **04-Engineering** 中的工程化实践
3. 研究 **05-Case-Studies** 中的实战案例
4. 贡献自己的经验和脚本

## 🔧 工具推荐

### 必备工具

- **Chrome DevTools**: 浏览器内置开发者工具
- **Burp Suite**: Web 应用安全测试工具
- **Puppeteer/Playwright**: 无头浏览器自动化
- **Babel/AST Explorer**: JavaScript AST 解析

### 可选工具

- **Fiddler/Charles**: HTTP 抓包代理
- **Wireshark**: 网络协议分析
- **Postman**: API 测试工具
- **Selenium**: 浏览器自动化框架

## 💡 贡献指南

欢迎贡献！您可以：

1. 完善现有文档内容
2. 添加新的案例研究
3. 分享实用脚本
4. 报告错误或提出改进建议

## 📄 许可证

本项目仅供学习和研究使用。

## 🔗 相关项目

- [Android 逆向工程烹饪食谱](../android_reversing/)

## ⚠️ 免责声明

本项目所有内容仅供学习和研究使用，请勿用于非法用途。使用者应遵守当地法律法规和网站服务条款。

---

**Happy Reversing!** 🎉
