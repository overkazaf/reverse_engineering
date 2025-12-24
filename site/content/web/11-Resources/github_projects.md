---
title: "开源项目推荐"
weight: 10
---

# 开源项目推荐

## 概述

本章精选了 Web 逆向工程领域的优质开源项目，涵盖工具、框架、库和学习资源。这些项目可以帮助你快速入门、提升技能、解决实际问题。

---

## 浏览器自动化

| 项目名称 | Stars | 语言 | 简介 | 主要特点 | 安装命令 |
| --------------------------------------------------------------------------------- | ----- | --------------------- | ------------------------------------ | ---------------------------------------------------------------------------------- | -------------------------------------------- |
| **[Puppeteer](https://github.com/puppeteer/puppeteer)** | 87k+ | JavaScript/TypeScript | Google 官方 Chrome/Chromium 自动化库 | • 官方支持，API 稳定<br>• 性能优秀<br>• 生态丰富（puppeteer-extra 插件） | `npm install puppeteer` |
| **[Playwright](https://github.com/microsoft/playwright)** | 63k+ | JavaScript/TypeScript | 微软开发的跨浏览器自动化框架 | • 支持 Chrome、Firefox、Safari<br>• 并发能力强<br>• 移动端模拟<br>• 网络拦截和修改 | `npm install @playwright/test` |
| **[Selenium](https://github.com/SeleniumHQ/selenium)** | 30k+ | 多语言 | 最早的浏览器自动化框架 | • 支持多种编程语言<br>• 成熟稳定<br>• 社区庞大 | `pip install selenium` |
| **[puppeteer-extra-plugin-stealth](https://github.com/berstend/puppeteer-extra)** | 6k+ | JavaScript | Puppeteer 反检测插件 | • 绕过 Webdriver 检测<br>• 伪造 Chrome 特征<br>• 自动规避常见反爬虫 | `npm install puppeteer-extra-plugin-stealth` |

**使用场景**: 自动化测试、网页截图/PDF 生成、爬虫开发、E2E 测试、绕过自动化检测

---

## JavaScript 分析

| 项目名称 | Stars | 语言 | 简介 | 主要特点 | 安装命令 |
| ------------------------------------------------------------------------------------------- | ----- | ---------- | ---------------------------- | ------------------------------------------------------------- | ------------------------------------------- |
| **[Babel](https://github.com/babel/babel)** | 43k+ | JavaScript | JavaScript 编译器和 AST 工具 | • 强大的 AST 操作能力<br>• 丰富的转换插件<br>• 反混淆核心工具 | `npm install @babel/core @babel/parser` |
| **[javascript-obfuscator](https://github.com/javascript-obfuscator/javascript-obfuscator)** | 9k+ | JavaScript | JavaScript 代码混淆工具 | • 多种混淆选项<br>• 字符串加密<br>• 控制流平坦化 | `npm install javascript-obfuscator` |
| **[webcrack](https://github.com/j4k0xb/webcrack)** | 2k+ | TypeScript | Webpack bundle 反混淆工具 | • 自动识别 Webpack 打包<br>• 提取模块代码<br>• 还原目录结构 | `npm install -g webcrack` |
| **[de4js](https://github.com/lelinhtinh/de4js)** | 1.5k+ | JavaScript | 在线 JavaScript 反混淆工具 | • 支持多种混淆格式<br>• 在线使用，无需安装<br>• 可视化展示 | 在线版: https://lelinhtinh.github.io/de4js/ |

**使用场景**: JavaScript 反混淆、代码转换、AST 分析、Webpack 打包代码分析、了解混淆技术

---

## 网络抓包与分析

| 项目名称 | Stars | 语言 | 简介 | 主要特点 | 安装命令 |
| ----------------------------------------------------------------- | ----- | ---------- | --------------------------------- | ----------------------------------------------------------------------------- | ------------------------------------ |
| **[mitmproxy](https://github.com/mitmproxy/mitmproxy)** | 35k+ | Python | 强大的 MITM 代理工具 | • 命令行和 Web 界面<br>• 支持 HTTP/HTTPS<br>• Python 脚本定制<br>• 自动化 API | `pip install mitmproxy` |
| **[Whistle](https://github.com/avwo/whistle)** | 14k+ | JavaScript | 基于 Node.js 的抓包调试代理工具 | • Web 可视化界面<br>• 规则配置灵活<br>• 支持 HTTPS、WebSocket<br>• 插件扩展 | `npm install -g whistle && w2 start` |
| **[har-validator](https://github.com/ahmadnassri/har-validator)** | 140+ | JavaScript | HAR (HTTP Archive) 文件验证和解析 | • 验证 HAR 格式<br>• 提取请求/响应数据<br>• 命令行工具 | `npm install har-validator` |

**使用场景**: 移动端抓包、API 分析、请求重放、前端调试、API Mock、跨域问题调试、HAR 文件分析

---

## 加密与解密

| 项目名称 | Stars | 语言 | 简介 | 主要特点 | 访问方式 |
| -------------------------------------------------- | ----- | ---------- | ---------------------------- | --------------------------------------------------------------------------------------- | ----------------------------------------- |
| **[CyberChef](https://github.com/gchq/CyberChef)** | 26k+ | JavaScript | "网络瑞士军刀"，数据处理工具 | • 200+ 操作（编码、加密、压缩等）<br>• 拖拽式操作流程<br>• 无需编程 | 在线版: https://gchq.github.io/CyberChef/ |
| **[crypto-js](https://github.com/brix/crypto-js)** | 15k+ | JavaScript | JavaScript 加密库 | • 常用加密算法（MD5、SHA、AES、RSA）<br>• 纯 JavaScript 实现<br>• 浏览器和 Node.js 通用 | `npm install crypto-js` |

**使用场景**: 数据转换、加密解密、格式分析、加密算法识别、参数签名复现

---

## 指纹识别

| 项目名称 | Stars | 语言 | 简介 | 主要特点 | 访问方式 |
| ------------------------------------------------------------------- | ----- | ---------- | -------------------- | ------------------------------------------------------------- | ------------------------------------------------ |
| **[FingerprintJS](https://github.com/fingerprintjs/fingerprintjs)** | 22k+ | TypeScript | 浏览器指纹识别库 | • 99.5% 准确率<br>• Canvas/WebGL/Audio 指纹<br>• 免费开源版本 | `npm install @fingerprintjs/fingerprintjs` |
| **[creepjs](https://github.com/abrahamjuliot/creepjs)** | 2k+ | JavaScript | 浏览器指纹和特征检测 | • 检测浏览器伪造<br>• 展示所有指纹信息<br>• 在线 Demo | 在线版: https://abrahamjuliot.github.io/creepjs/ |

**使用场景**: 了解指纹技术、反指纹测试、指纹检测和分析

---

## 爬虫框架

| 项目名称 | Stars | 语言 | 简介 | 主要特点 | 安装命令 |
| ----------------------------------------------- | ----- | ---------- | ------------------------ | -------------------------------------------------------------------------------------- | --------------------- |
| **[Scrapy](https://github.com/scrapy/scrapy)** | 52k+ | Python | 强大的爬虫框架 | • 异步高性能<br>• 中间件和管道系统<br>• 分布式爬虫支持（Scrapy-Redis）<br>• 丰富的插件 | `pip install scrapy` |
| **[crawlee](https://github.com/apify/crawlee)** | 14k+ | TypeScript | Node.js Web 爬虫和抓取库 | • 支持 Puppeteer/Playwright<br>• 自动重试和队列管理<br>• 代理轮换<br>• TypeScript 友好 | `npm install crawlee` |

**使用场景**: 大规模爬虫项目、现代 JavaScript 爬虫

---

## 逆向辅助工具

| 项目名称 | Stars | 语言 | 简介 | 主要特点 | 安装/使用 |
| -------------------------------------------------------------------- | ----- | ------ | --------------------------------------- | ----------------------------------------------------------------------- | ------------------------------------ |
| **[curl-impersonate](https://github.com/lwthiker/curl-impersonate)** | 6k+ | C | 伪造浏览器 TLS 指纹的 curl | • 完美模拟 Chrome/Firefox TLS 指纹<br>• 绕过 JA3 检测<br>• 命令行工具 | `curl_chrome124 https://example.com` |
| **[httpx](https://github.com/encode/httpx)** | 13k+ | Python | 下一代 Python HTTP 客户端 | • HTTP/2 和 HTTP/3 支持<br>• 同步/异步 API<br>• 连接池 | `pip install httpx` |
| **[requests-html](https://github.com/psf/requests-html)** | 14k+ | Python | 结合 Requests 和 PyQuery 的 HTML 解析库 | • JavaScript 渲染（内置 Chromium）<br>• jQuery 风格选择器<br>• 简单易用 | `pip install requests-html` |

**使用场景**: TLS 指纹绕过、现代 HTTP 请求、需要 JS 渲染的爬虫

---

## WebAssembly 工具

| 项目名称 | Stars | 语言 | 简介 | 主要工具 | 使用示例 |
| ----------------------------------------------- | ----- | ---- | -------------------------- | ------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------- |
| **[wabt](https://github.com/WebAssembly/wabt)** | 6k+ | C++ | WebAssembly Binary Toolkit | • wasm2wat（二进制转文本）<br>• wat2wasm（文本转二进制）<br>• wasm-objdump（反汇编）<br>• wasm-decompile（反编译） | `wasm2wat module.wasm -o module.wat`<br>`wasm-decompile module.wasm -o module.c` |

**使用场景**: Wasm 逆向分析、Wasm 代码分析

---

## 浏览器插件

| 插件名称 | Stars | 支持浏览器 | 简介 | 主要功能 |
| ---------------------------------------------------------------- | ----- | ----------------------------- | --------------------- | ------------------------------------------------------------------ |
| **[Tampermonkey](https://github.com/Tampermonkey/tampermonkey)** | 4k+ | Chrome、Firefox、Safari、Edge | 用户脚本管理器 | • 注入自定义 JavaScript<br>• 脚本市场（Greasy Fork）<br>• 自动更新 |
| **EditThisCookie** | - | Chrome、Firefox | Cookie 编辑工具 | • 查看/编辑 Cookie<br>• 导入/导出<br>• 搜索过滤 |
| **JSON Viewer** | - | Chrome、Firefox | JSON 格式化浏览器插件 | • 语法高亮<br>• 折叠展开<br>• 搜索过滤 |

**使用场景**: 注入 Hook 脚本、修改页面行为、自动化操作、Cookie 调试和管理

---

## 验证码识别

| 项目名称 | Stars | 语言 | 简介 | 主要特点 | 安装命令 |
| ------------------------------------------------------------------------- | ----- | ------ | ---------------------------- | -------------------------------------------------- | --------------------------------- |
| **[ddddocr](https://github.com/sml2h3/ddddocr)** | 9k+ | Python | 带带弟弟 OCR，简单验证码识别 | • 无需训练<br>• 识别准确率高<br>• 支持滑块缺口检测 | `pip install ddddocr` |
| **[hcaptcha-challenger](https://github.com/QIN2DIM/hcaptcha-challenger)** | 700+ | Python | hCaptcha 自动识别 | • 基于 YOLOv8<br>• 自动化流程 | `pip install hcaptcha-challenger` |

**使用场景**: 简单验证码识别、hCaptcha 绕过

---

## 学习资源项目

| 项目名称 | Stars | 语言 | 简介 | 主要内容 |
| ------------------------------------------------------------------------------- | ----- | ------ | ---------------------------- | ------------------------------------------------------------------ |
| **[awesome-web-scraping](https://github.com/lorien/awesome-web-scraping)** | 7k+ | - | Web 爬虫资源合集 | • 爬虫框架<br>• 代理服务<br>• 验证码识别<br>• 反爬虫资源 |
| **[javascript-questions](https://github.com/lydiahallie/javascript-questions)** | 61k+ | 多语言 | JavaScript 进阶问题集 | • 涵盖闭包、原型链、异步等<br>• 逐题解答<br>• 适合面试准备 |
| **[You-Dont-Know-JS](https://github.com/getify/You-Dont-Know-JS)** | 178k+ | 英文 | 深入理解 JavaScript 系列书籍 | • 作用域与闭包<br>• this 与对象原型<br>• 异步与性能<br>• ES6+ 特性 |

**使用场景**: JavaScript 基础加强、面试准备、深入理解 JavaScript

---

## 其他实用工具

| 工具名称 | Stars | 语言 | 简介 | 主要功能 | 访问方式 |
| --------------------------------------- | ----- | ---- | ------------------ | ------------------------------------------------------ | ----------------- |
| **[Postman](https://www.postman.com/)** | - | - | API 开发和测试工具 | • 请求构造<br>• 集合管理<br>• 环境变量<br>• 自动化测试 | 官网下载 |
| **[jq](https://github.com/jqlang/jq)** | 30k+ | C | 命令行 JSON 处理器 | • 强大的过滤和转换<br>• 管道操作<br>• 轻量级 | `brew install jq` |

**使用示例**:

```bash
# jq 处理 JSON
curl https://api.example.com/data | jq '.items[] | .name'
```

---

## 工具组合方案

### 方案一：全栈爬虫

```
Puppeteer + puppeteer-extra-plugin-stealth
↓
mitmproxy（抓包分析）
↓
Babel（反混淆）
↓
Python requests/httpx（请求复现）
```

### 方案二：高性能爬虫

```
Scrapy（框架）
↓
Scrapy-Redis（分布式）
↓
代理池（IP 轮换）
↓
消息队列（任务调度）
```

### 方案三：JavaScript 逆向

```
Chrome DevTools（动态调试）
↓
Babel + AST Explorer（反混淆）
↓
CyberChef（数据处理）
↓
Node.js（算法复现）
```

---

## 持续关注

建议定期关注以下资源：

| 资源名称 | 链接 | 说明 |
| ------------------- | --------------------------------------- | ------------ |
| **GitHub Trending** | https://github.com/trending/javascript | 发现热门项目 |
| **Awesome Lists** | https://github.com/sindresorhus/awesome | 优质资源合集 |
| **Reddit** | r/webscraping | 社区讨论 |
| **Stack Overflow** | 标签 `web-scraping` | 技术问答 |

---

## 相关章节

- [学习资源](./learning_resources.md)
- [浏览器开发者工具](../02-Tooling/browser_devtools.md)
- [Puppeteer 与 Playwright](../02-Tooling/puppeteer_playwright.md)
- [AST 解析工具](../02-Tooling/ast_tools.md)
