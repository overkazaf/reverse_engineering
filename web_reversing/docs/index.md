# Web 逆向工程 Cookbook

欢迎来到 **Web RE Cookbook** —— 一本实战导向的 Web 逆向工程实用手册。

本 Cookbook 采用**场景驱动**的组织方式，帮助你快速找到解决特定问题的方法，而非传统的知识点罗列。

---

## 🚀 新手？从这里开始

**完全新手？** 先完成 10 分钟快速入门，体验第一次 Hook！

👉 **[10 分钟快速入门](./00-Quick-Start/index.md)** - 安装工具并完成第一次 Hook

**想看更多实战案例？**
👉 **[解密 API 参数](./00-Quick-Start/decrypt_api_params.md)** - 学习分析和还原加密参数

---

## 📖 如何使用本 Cookbook

### 🎯 按需查找
- **遇到问题？** 直接查看 [Basic Recipes](#-03-basic-recipes---基础配方) 或 [Advanced Recipes](#-04-advanced-recipes---高级配方) 章节，找到对应场景的解决方案
- **学习工具？** 查看 [Tooling](#-01-tooling---工具指南) 章节，了解各类工具的使用方法
- **参考案例？** 浏览 [Case Studies](#-05-case-studies---案例研究)，学习实战分析流程
- **查阅资料？** 访问 [Foundations](#-00-foundations---基础原理)，深入理解底层原理

### 📚 学习路径
1. **新手入门**: Foundations → Tooling → Basic Recipes
2. **实战为主**: Basic Recipes → Tooling → Case Studies
3. **进阶提升**: Case Studies → Advanced Recipes → Engineering

---

## 知识体系结构

本知识库从基础到实践，系统性地组织了 Web 逆向工程领域的各类知识点，主要包括：

- [**`Part I: Getting Started`**](./00-Quick-Start/): **快速上手**。帮助新手快速开始第一个逆向项目。

- [**`Part II: Kitchen Basics`**](./01-Foundations/): **厨房基础**。构成了 Web 应用和浏览器的核心基石。

- [**`Part III: Tools & Ingredients`**](./02-Tooling/): **工具箱**。详尽介绍逆向工程师日常使用的关键工具。

- [**`Part IV: Basic Recipes`**](./03-Basic-Recipes/): **基础配方**。介绍解决具体问题的基本策略和方法。

- [**`Part V: Advanced Recipes`**](./04-Advanced-Recipes/): **高级配方**。深入探讨代码混淆、虚拟机保护、反爬虫等高级技术。

- [**`Part VI: Complete Menus`**](./05-Case-Studies/): **完整菜单**。通过真实场景的案例，综合运用所学知识。

- [**`Part VII: Code Kitchen`**](./07-Scripts/): **代码厨房**。提供即用型脚本和工具集。

- [**`Part VIII: Reference`**](./11-Resources/): **参考资料**。速查表、模板和学习资源。

---

### 📚 `00-Foundations` - 基础原理

1.  **[HTTP/HTTPS 协议 (`http_https_protocol.md`)](./01-Foundations/http_https_protocol.md)**

    - 深入理解 HTTP/HTTPS 协议的工作原理、请求/响应结构、状态码、Headers 等核心概念。

2.  **[浏览器架构与渲染引擎 (`browser_architecture.md`)](./01-Foundations/browser_architecture.md)**

    - 详细介绍浏览器的多进程架构、渲染引擎（Blink/WebKit/Gecko）、JavaScript 引擎（V8/SpiderMonkey）的工作原理。

3.  **[JavaScript 基础 (`javascript_basics.md`)](./01-Foundations/javascript_basics.md)**

    - 涵盖 JavaScript 的核心语法、作用域、闭包、原型链、异步编程等基础知识。

4.  **[DOM 与 BOM (`dom_and_bom.md`)](./01-Foundations/dom_and_bom.md)**

    - 解析文档对象模型（DOM）和浏览器对象模型（BOM）的结构与操作方法。

5.  **[WebAssembly 基础 (`webassembly_basics.md`)](./01-Foundations/webassembly_basics.md)**

    - 介绍 WebAssembly 的设计理念、二进制格式、与 JavaScript 的交互等。

6.  **[Cookie 与 Storage (`cookie_and_storage.md`)](./01-Foundations/cookie_and_storage.md)**

    - 详解 Cookie、LocalStorage、SessionStorage、IndexedDB 等客户端存储机制。

7.  **[CORS 与同源策略 (`cors_and_same_origin_policy.md`)](./01-Foundations/cors_and_same_origin_policy.md)**

    - 深入理解浏览器的同源策略、CORS 跨域资源共享机制及其安全 implications。

8.  **[TLS/SSL 握手过程 (`tls_ssl_handshake.md`)](./01-Foundations/tls_ssl_handshake.md)**

    - 详细解析 TLS/SSL 握手过程、证书验证、加密算法协商等安全机制。

9.  **[Web API 与 Ajax (`web_api_and_ajax.md`)](./01-Foundations/web_api_and_ajax.md)**

    - 介绍 XMLHttpRequest、Fetch API、WebSocket 等 Web API 的使用和逆向分析。

---

### 🔨 `01-Tooling` - 工具指南

1.  **[浏览器开发者工具 (`browser_devtools.md`)](./02-Tooling/browser_devtools.md)**

    - 全面介绍 Chrome DevTools、Firefox Developer Tools 的各项功能，包括 Elements、Console、Sources、Network、Performance、Application 等面板。

2.  **[Burp Suite 指南 (`burp_suite_guide.md`)](./02-Tooling/burp_suite_guide.md)**

    - 详细介绍 Burp Suite 的代理、拦截、重放、扫描等功能，以及插件开发。

3.  **[Fiddler 指南 (`fiddler_guide.md`)](./02-Tooling/fiddler_guide.md)**

    - 介绍 Fiddler 的流量捕获、修改、重放、性能分析等功能。

4.  **[Charles 指南 (`charles_guide.md`)](./02-Tooling/charles_guide.md)**

    - 详解 Charles Proxy 的使用，包括 SSL 代理、断点、重写、节流等功能。

5.  **[Wireshark 网络分析 (`wireshark_guide.md`)](./02-Tooling/wireshark_guide.md)**

    - 介绍使用 Wireshark 进行深度网络包分析、协议解析、流量过滤等。

6.  **[Puppeteer 与 Playwright (`puppeteer_playwright.md`)](./02-Tooling/puppeteer_playwright.md)**

    - 介绍无头浏览器自动化工具 Puppeteer 和 Playwright 的使用和逆向应用。

7.  **[Selenium WebDriver (`selenium_guide.md`)](./02-Tooling/selenium_guide.md)**

    - 详细介绍 Selenium 的浏览器自动化、元素定位、事件触发等功能。

8.  **[AST 解析工具 (`ast_tools.md`)](./02-Tooling/ast_tools.md)**

    - 介绍 Babel、ESPrima、Acorn 等抽象语法树（AST）解析工具及其在代码分析中的应用。

9.  **[Node.js 调试工具 (`nodejs_debugging.md`)](./02-Tooling/nodejs_debugging.md)**

    - 介绍 Node.js 的调试器、Chrome DevTools 集成、日志分析等调试技术。

10. **[V8 引擎工具 (`v8_tools.md`)](./02-Tooling/v8_tools.md)**

    - 介绍 V8 的命令行工具、内存分析、性能分析、反优化等高级功能。

---

### 🔬 `02-Techniques` - 实战技术

1.  **[逆向工程工作流 (`re_workflow.md`)](./03-Basic-Recipes/re_workflow.md)**

    - 提供一个标准化的 Web 逆向分析流程，从信息收集、流量分析、代码分析到自动化实现。

2.  **[JavaScript 反混淆 (`javascript_deobfuscation.md`)](./04-Advanced-Recipes/javascript_deobfuscation.md)**

    - 详细介绍常见的 JavaScript 混淆技术及其反混淆方法，包括字符串编码、控制流平坦化等。

3.  **[调试技巧与断点设置 (`debugging_techniques.md`)](./03-Basic-Recipes/debugging_techniques.md)**

    - 介绍高级调试技巧，包括条件断点、日志点、动态代码修改、反反调试等。

4.  **[加密算法识别与分析 (`crypto_identification.md`)](./03-Basic-Recipes/crypto_identification.md)**

    - 教你如何识别网站中使用的加密算法（AES、RSA、MD5、SHA 等）并进行分析。

5.  **[API 接口逆向 (`api_reverse_engineering.md`)](./03-Basic-Recipes/api_reverse_engineering.md)**

    - 介绍如何通过流量分析、代码追踪等方法逆向 Web API 的签名、加密、认证机制。

6.  **[WebSocket 逆向 (`websocket_reversing.md`)](./03-Basic-Recipes/websocket_reversing.md)**

    - 详解如何分析和逆向 WebSocket 通信协议、消息格式、加密方式。

7.  **[Hook 技术 (`hooking_techniques.md`)](./03-Basic-Recipes/hooking_techniques.md)**

    - 介绍 JavaScript Hook、Native Hook、Proxy 劫持等技术及其在逆向中的应用。

8.  **[动态参数生成分析 (`dynamic_parameter_analysis.md`)](./03-Basic-Recipes/dynamic_parameter_analysis.md)**

    - 教你如何追踪和分析动态生成的请求参数、签名、时间戳等。

9.  **[验证码识别与绕过 (`captcha_bypass.md`)](./04-Advanced-Recipes/captcha_bypass.md)**

    - 介绍常见验证码类型（图形、滑块、点选、行为）的识别和绕过技术。

10. **[浏览器指纹识别 (`browser_fingerprinting.md`)](./04-Advanced-Recipes/browser_fingerprinting.md)**

    - 详解浏览器指纹的生成原理及如何模拟真实浏览器环境。

---

### 🚀 `03-Advanced-Topics` - 高阶专题

1.  **[JavaScript 虚拟机保护 (`javascript_vm_protection.md`)](./04-Advanced-Recipes/javascript_vm_protection.md)**

    - 分析 JSVMP 等虚拟机保护技术的原理及其对抗策略。

2.  **[WebAssembly 逆向 (`webassembly_reversing.md`)](./04-Advanced-Recipes/webassembly_reversing.md)**

    - 介绍 WebAssembly 二进制格式的逆向分析、反编译、调试技术。

3.  **[反爬虫技术深度分析 (`anti_scraping_deep_dive.md`)](./04-Advanced-Recipes/anti_scraping_deep_dive.md)**

    - 深入探讨现代反爬虫技术，包括设备指纹、行为分析、风控系统等。

4.  **[前端加固技术 (`frontend_hardening.md`)](./04-Advanced-Recipes/frontend_hardening.md)**

    - 分析前端代码加固、混淆、加密、完整性校验等保护技术。

5.  **[CSP 绕过技术 (`csp_bypass.md`)](./04-Advanced-Recipes/csp_bypass.md)**

    - 详解内容安全策略（CSP）的原理及绕过方法。

6.  **[WebRTC 指纹与隐私 (`webrtc_fingerprinting.md`)](./04-Advanced-Recipes/webrtc_fingerprinting.md)**

    - 介绍 WebRTC 泄露真实 IP、设备信息的原理及防护方法。

7.  **[Canvas 指纹技术 (`canvas_fingerprinting.md`)](./04-Advanced-Recipes/canvas_fingerprinting.md)**

    - 详解 Canvas 指纹的生成原理、检测方法及伪装技术。

8.  **[TLS 指纹识别 (`tls_fingerprinting.md`)](./04-Advanced-Recipes/tls_fingerprinting.md)**

    - 介绍 JA3/JA4 等 TLS 指纹技术及如何模拟真实浏览器的 TLS 握手。

9.  **[HTTP/2 与 HTTP/3 (`http2_http3.md`)](./04-Advanced-Recipes/http2_http3.md)**

    - 深入分析现代 HTTP 协议的特性及其在逆向中的挑战。

10. **[PWA 与 Service Worker (`pwa_service_worker.md`)](./04-Advanced-Recipes/pwa_service_worker.md)**

    - 介绍渐进式 Web 应用（PWA）和 Service Worker 的逆向分析。

---

### 🔩 `04-Engineering` - 工程化

1.  **[分布式爬虫架构 (`distributed_scraping.md`)](./06-Engineering/distributed_scraping.md)**

    - 介绍如何构建大规模分布式爬虫系统，包括任务调度、去重、容错等。

2.  **[代理池管理 (`proxy_pool_management.md`)](./06-Engineering/proxy_pool_management.md)**

    - 详解代理池的构建、维护、质量检测、调度策略等。

3.  **[数据存储方案 (`data_storage_solutions.md`)](./06-Engineering/data_storage_solutions.md)**

    - 介绍 MySQL、MongoDB、Redis、Elasticsearch 等在爬虫系统中的应用。

4.  **[消息队列应用 (`message_queue_application.md`)](./06-Engineering/message_queue_application.md)**

    - 详解 RabbitMQ、Kafka、Redis Queue 在分布式爬虫中的使用。

5.  **[Docker 容器化部署 (`docker_deployment.md`)](./06-Engineering/docker_deployment.md)**

    - 介绍如何使用 Docker 容器化部署爬虫系统，实现环境隔离和快速扩展。

6.  **[监控与告警系统 (`monitoring_and_alerting.md`)](./06-Engineering/monitoring_and_alerting.md)**

    - 详解如何构建爬虫系统的监控、日志、告警体系。

7.  **[反爬虫对抗框架 (`anti_anti_scraping_framework.md`)](./06-Engineering/anti_anti_scraping_framework.md)**

    - 介绍如何构建通用的反爬虫对抗框架，包括请求伪装、行为模拟等。

---

### 📊 `05-Case-Studies` - 案例研究

1.  **[电商网站逆向 (`case_ecommerce.md`)](./05-Case-Studies/case_ecommerce.md)**

    - 分析主流电商网站的反爬虫机制、API 签名、价格加密等技术。

2.  **[社交媒体逆向 (`case_social_media.md`)](./05-Case-Studies/case_social_media.md)**

    - 探讨社交媒体平台的登录验证、动态加载、反爬虫策略等。

3.  **[金融网站逆向 (`case_financial.md`)](./05-Case-Studies/case_financial.md)**

    - 分析金融网站的高强度加密、设备指纹、风控系统等。

4.  **[视频网站逆向 (`case_video_streaming.md`)](./05-Case-Studies/case_video_streaming.md)**

    - 详解视频网站的 DRM 保护、流媒体协议、防下载技术等。

5.  **[新闻聚合网站 (`case_news_aggregator.md`)](./05-Case-Studies/case_news_aggregator.md)**

    - 介绍新闻网站的内容提取、反爬虫机制、实时更新监控等。

6.  **[搜索引擎对抗 (`case_search_engine.md`)](./05-Case-Studies/case_search_engine.md)**

    - 分析搜索引擎的反爬虫策略及数据采集技术。

---

### 📚 `06-Scripts` - 脚本范例

1.  **[JavaScript Hook 脚本 (`javascript_hook_scripts.md`)](./07-Scripts/javascript_hook_scripts.md)**

    - 提供常用的 JavaScript Hook 脚本，包括 Cookie、Fetch、WebSocket 等的拦截。

2.  **[反混淆脚本 (`deobfuscation_scripts.md`)](./07-Scripts/deobfuscation_scripts.md)**

    - 提供基于 AST 的 JavaScript 反混淆脚本示例。

3.  **[浏览器自动化脚本 (`automation_scripts.md`)](./07-Scripts/automation_scripts.md)**

    - 提供 Puppeteer、Playwright 的常用自动化脚本。

4.  **[加密算法识别脚本 (`crypto_detection_scripts.md`)](./07-Scripts/crypto_detection_scripts.md)**

    - 提供自动识别常见加密算法的脚本工具。

---

### 🔗 `07-Others` - 其他资源

1.  **[开源项目推荐 (`github_projects.md`)](./11-Resources/github_projects.md)**

    - 推荐优秀的 Web 逆向相关开源项目和工具。

2.  **[学习资源 (`learning_resources.md`)](./11-Resources/learning_resources.md)**

    - 整理优质的学习资源、博客、视频教程等。

3.  **[常见问题 FAQ (`faq.md`)](./11-Resources/faq.md)**

    - 汇总 Web 逆向中的常见问题和解决方案。
