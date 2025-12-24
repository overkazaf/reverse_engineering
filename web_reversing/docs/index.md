# Web 逆向工程 Cookbook

欢迎来到 **Web RE Cookbook** —— 一本实战导向的 Web 逆向工程实用手册。

本 Cookbook 采用**场景驱动**的组织方式，帮助你快速找到解决特定问题的方法，而非传统的知识点罗列。

---

## 新手？从这里开始

**完全新手？** 先完成 10 分钟快速入门，体验第一次 Hook！

**[10 分钟快速入门](./00-Quick-Start/index.md)** - 安装工具并完成第一次 Hook

**想看更多实战案例？**
**[解密 API 参数](./00-Quick-Start/decrypt_api_params.md)** - 学习分析和还原加密参数

---

## 如何使用本 Cookbook

### 按需查找
- **遇到问题？** 直接查看 [实战配方](#实战配方) 章节，找到对应场景的解决方案
- **参考案例？** 浏览 [案例研究](#案例研究)，学习实战分析流程
- **学习工具？** 查看 [工具指南](#工具指南) 章节，了解各类工具的使用方法
- **查阅资料？** 访问 [基础知识](#基础知识)，深入理解底层原理

### 学习路径
1. **快速上手**: 快速入门 → 基础配方 → 案例研究
2. **进阶提升**: 进阶配方 → 工程实践 → 基础知识
3. **按需查阅**: 工具指南、速查手册作为参考

---

## 知识体系结构

本知识库采用**实战优先**的组织方式：

- [**`Part I: Getting Started`**](./00-Quick-Start/): **快速上手**。帮助新手快速开始第一个逆向项目。

- [**`Part II: Recipes`**](./03-Basic-Recipes/): **实战配方**。解决具体问题的策略和方法，从基础到进阶。

- [**`Part III: Case Studies`**](./05-Case-Studies/): **案例研究**。通过真实场景的案例，综合运用所学知识。

- [**`Part IV: Foundations`**](./01-Foundations/): **基础知识**。深入理解 Web 应用和浏览器的核心原理。

- [**`Part V: Tooling`**](./02-Tooling/): **工具指南**。详尽介绍逆向工程师日常使用的关键工具。

- [**`Part VI: Engineering`**](./06-Engineering/): **工程实践**。分布式爬虫、代理池、监控告警等生产级方案。

- [**`Part VII: Reference`**](./07-Scripts/): **参考资料**。脚本集合、速查手册、项目模板。

---

### 快速入门

1. **[概述](./00-Quick-Start/index.md)** - 学习路径和准备工作

2. **[你的第一个 Hook](./00-Quick-Start/your_first_hook.md)** - 15 分钟完成第一次 Hook

3. **[解密 API 参数](./00-Quick-Start/decrypt_api_params.md)** - 学习追踪和还原加密参数

4. **[绕过简单验证码](./00-Quick-Start/bypass_simple_captcha.md)** - OCR 识别和验证码绕过

---

### 实战配方

#### 基础配方

1. **[逆向工程流程](./03-Basic-Recipes/re_workflow.md)** - 标准化的 Web 逆向分析流程

2. **[调试技术](./03-Basic-Recipes/debugging_techniques.md)** - 高级调试技巧，包括条件断点、反反调试等

3. **[Hook 技术](./03-Basic-Recipes/hooking_techniques.md)** - JavaScript Hook、Proxy 劫持等技术

4. **[API 逆向工程](./03-Basic-Recipes/api_reverse_engineering.md)** - 逆向 Web API 的签名、加密、认证机制

5. **[加密算法识别](./03-Basic-Recipes/crypto_identification.md)** - 识别和分析网站中使用的加密算法

6. **[动态参数分析](./03-Basic-Recipes/dynamic_parameter_analysis.md)** - 追踪和分析动态生成的请求参数

7. **[WebSocket 逆向](./03-Basic-Recipes/websocket_reversing.md)** - 分析 WebSocket 通信协议和消息格式

#### 进阶配方

1. **[JavaScript 反混淆](./04-Advanced-Recipes/javascript_deobfuscation.md)** - 常见混淆技术及其反混淆方法

2. **[验证码绕过](./04-Advanced-Recipes/captcha_bypass.md)** - 图形、滑块、点选、行为验证码的绕过技术

3. **[浏览器指纹](./04-Advanced-Recipes/browser_fingerprinting.md)** - 浏览器指纹的生成原理及模拟技术

4. **[JavaScript VM 保护](./04-Advanced-Recipes/javascript_vm_protection.md)** - JSVMP 等虚拟机保护技术的对抗策略

5. **[WebAssembly 逆向](./04-Advanced-Recipes/webassembly_reversing.md)** - Wasm 二进制格式的逆向分析

6. **[反爬虫深度分析](./04-Advanced-Recipes/anti_scraping_deep_dive.md)** - 设备指纹、行为分析、风控系统

7. **[前端加固技术](./04-Advanced-Recipes/frontend_hardening.md)** - 代码加固、混淆、完整性校验

8. **[CSP 绕过](./04-Advanced-Recipes/csp_bypass.md)** - 内容安全策略的原理及绕过方法

9. **[WebRTC 指纹](./04-Advanced-Recipes/webrtc_fingerprinting.md)** - WebRTC 泄露真实 IP 的原理及防护

10. **[Canvas 指纹](./04-Advanced-Recipes/canvas_fingerprinting.md)** - Canvas 指纹的生成、检测及伪装

11. **[TLS 指纹](./04-Advanced-Recipes/tls_fingerprinting.md)** - JA3/JA4 等 TLS 指纹技术及模拟

12. **[HTTP/2 与 HTTP/3](./04-Advanced-Recipes/http2_http3.md)** - 现代 HTTP 协议的特性及逆向挑战

13. **[PWA 与 Service Worker](./04-Advanced-Recipes/pwa_service_worker.md)** - 渐进式 Web 应用的逆向分析

---

### 案例研究

1. **[电商网站](./05-Case-Studies/case_ecommerce.md)** - 反爬虫机制、API 签名、价格加密

2. **[社交媒体](./05-Case-Studies/case_social_media.md)** - 登录验证、动态加载、反爬虫策略

3. **[金融网站](./05-Case-Studies/case_financial.md)** - 高强度加密、设备指纹、风控系统

4. **[视频流媒体](./05-Case-Studies/case_video_streaming.md)** - DRM 保护、流媒体协议、防下载技术

5. **[新闻聚合](./05-Case-Studies/case_news_aggregator.md)** - 内容提取、实时更新监控

6. **[搜索引擎](./05-Case-Studies/case_search_engine.md)** - 反爬虫策略及数据采集技术

---

### 基础知识

1. **[HTTP/HTTPS 协议](./01-Foundations/http_https_protocol.md)** - 协议原理、请求/响应结构、Headers

2. **[浏览器架构](./01-Foundations/browser_architecture.md)** - 多进程架构、渲染引擎、JavaScript 引擎

3. **[JavaScript 基础](./01-Foundations/javascript_basics.md)** - 核心语法、作用域、闭包、原型链

4. **[JavaScript 执行机制](./01-Foundations/javascript_execution_mechanism.md)** - 事件循环、调用栈、异步编程

5. **[DOM 与 BOM](./01-Foundations/dom_and_bom.md)** - 文档对象模型和浏览器对象模型

6. **[WebAssembly 基础](./01-Foundations/webassembly_basics.md)** - 设计理念、二进制格式、与 JS 交互

7. **[Cookie 与 Storage](./01-Foundations/cookie_and_storage.md)** - 客户端存储机制

8. **[CORS 与同源策略](./01-Foundations/cors_and_same_origin_policy.md)** - 浏览器安全策略及跨域机制

9. **[TLS/SSL 握手](./01-Foundations/tls_ssl_handshake.md)** - 握手过程、证书验证、加密协商

10. **[Web API 与 Ajax](./01-Foundations/web_api_and_ajax.md)** - XMLHttpRequest、Fetch API、WebSocket

---

### 工具指南

1. **[浏览器开发者工具](./02-Tooling/browser_devtools.md)** - Chrome/Firefox DevTools 全面介绍

2. **[Burp Suite 指南](./02-Tooling/burp_suite_guide.md)** - 代理、拦截、重放、扫描

3. **[Fiddler 指南](./02-Tooling/fiddler_guide.md)** - 流量捕获、修改、重放

4. **[Charles 指南](./02-Tooling/charles_guide.md)** - SSL 代理、断点、重写

5. **[Wireshark 指南](./02-Tooling/wireshark_guide.md)** - 深度网络包分析、协议解析

6. **[Puppeteer 与 Playwright](./02-Tooling/puppeteer_playwright.md)** - 无头浏览器自动化

7. **[Selenium 指南](./02-Tooling/selenium_guide.md)** - 浏览器自动化、元素定位

8. **[AST 工具](./02-Tooling/ast_tools.md)** - Babel、ESPrima 等 AST 解析工具

9. **[Node.js 调试](./02-Tooling/nodejs_debugging.md)** - 调试器、Chrome DevTools 集成

10. **[V8 工具](./02-Tooling/v8_tools.md)** - 命令行工具、内存分析、性能分析

---

### 工程实践

1. **[分布式爬虫](./06-Engineering/distributed_scraping.md)** - 大规模分布式爬虫系统架构

2. **[代理池管理](./06-Engineering/proxy_pool_management.md)** - 代理池构建、维护、调度策略

3. **[数据存储方案](./06-Engineering/data_storage_solutions.md)** - MySQL、MongoDB、Redis、Elasticsearch

4. **[消息队列应用](./06-Engineering/message_queue_application.md)** - RabbitMQ、Kafka 在爬虫中的使用

5. **[Docker 部署](./06-Engineering/docker_deployment.md)** - 容器化部署、环境隔离、快速扩展

6. **[监控与告警](./06-Engineering/monitoring_and_alerting.md)** - 爬虫系统的监控、日志、告警体系

7. **[反反爬框架](./06-Engineering/anti_anti_scraping_framework.md)** - 通用的反爬虫对抗框架

---

### 脚本集合

1. **[JavaScript Hook 脚本](./07-Scripts/javascript_hook_scripts.md)** - Cookie、Fetch、WebSocket 拦截脚本

2. **[反混淆脚本](./07-Scripts/deobfuscation_scripts.md)** - 基于 AST 的反混淆脚本示例

3. **[自动化脚本](./07-Scripts/automation_scripts.md)** - Puppeteer、Playwright 常用脚本

4. **[加密检测脚本](./07-Scripts/crypto_detection_scripts.md)** - 自动识别常见加密算法

---

### 速查手册

- **[常用命令](./08-Cheat-Sheets/common_commands.md)** - 常用命令速查
- **[加密签名](./08-Cheat-Sheets/crypto_signatures.md)** - 加密算法特征识别
- **[工具快捷键](./08-Cheat-Sheets/tool_shortcuts.md)** - 开发工具快捷键
- **[正则表达式](./08-Cheat-Sheets/regex_patterns.md)** - 常用正则表达式
- **[HTTP 头部](./08-Cheat-Sheets/http_headers.md)** - HTTP 头部参考

---

### 项目模板

- **[基础爬虫](./09-Templates/basic_scraper.md)** - 基础爬虫项目模板
- **[逆向项目](./09-Templates/reverse_project.md)** - 逆向分析项目模板
- **[Docker 配置](./09-Templates/docker_setup.md)** - Docker 配置模板
- **[CI/CD 流水线](./09-Templates/cicd_pipeline.md)** - 持续集成配置
- **[分布式爬虫](./09-Templates/distributed_crawler.md)** - 分布式爬虫模板

---

### 问题排查

- **[网络问题](./10-Troubleshooting/network_issues.md)** - 网络连接问题排查
- **[反爬问题](./10-Troubleshooting/anti_scraping_issues.md)** - 反爬虫问题排查
- **[JavaScript 调试](./10-Troubleshooting/javascript_debugging.md)** - JS 调试问题排查
- **[工具问题](./10-Troubleshooting/tool_issues.md)** - 工具使用问题排查
- **[数据问题](./10-Troubleshooting/data_issues.md)** - 数据采集问题排查
- **[Docker 问题](./10-Troubleshooting/docker_issues.md)** - Docker 相关问题排查

---

### 附录

- **[GitHub 开源项目](./11-Resources/github_projects.md)** - 推荐的开源项目和工具
- **[学习资源](./11-Resources/learning_resources.md)** - 优质学习资源、博客、视频
- **[常见问题 FAQ](./11-Resources/faq.md)** - 常见问题和解决方案
