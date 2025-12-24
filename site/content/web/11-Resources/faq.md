---
title: "常见问题 (FAQ)"
date: 2025-12-25
weight: 10
---

# 常见问题 (FAQ)

## 概述

本章汇总了 Web 逆向工程中的常见问题和解答，帮助你快速解决常见困惑。

---

## 入门问题

### Q1: 学习 Web 逆向需要哪些基础知识？

**A**:

**必备基础**:

1. **HTTP/HTTPS 协议**: 理解请求/响应、状态码、头部
2. **JavaScript 基础**: 变量、函数、闭包、原型链、异步编程
3. **HTML/CSS**: DOM 结构、选择器
4. **开发者工具**: Chrome DevTools 基本使用

**推荐掌握**:

1. Python/Node.js 编程
2. 正则表达式
3. 基础加密算法（MD5、SHA、AES）
4. 网络抓包工具（Burp Suite、Charles）

**可选进阶**:

1. 数据结构与算法
2. 编译原理（AST）
3. WebAssembly
4. 密码学

---

### Q2: 我应该从哪里开始学习？

**A**:

**推荐学习路线**:

**第一阶段：基础入门（1-2 周）**

1. 学习 HTTP 协议和浏览器工作原理
2. 熟练使用 Chrome DevTools（Network、Sources、Console）
3. 掌握 JavaScript 基础语法

**第二阶段：工具使用（1-2 周）**

1. 学习 Burp Suite 或 Charles 抓包
2. 了解 Puppeteer/Playwright 基本用法
3. 练习简单的爬虫项目

**第三阶段：技术提升（2-4 周）**

1. 学习 JavaScript 反混淆
2. 理解常见加密算法
3. 掌握 Hook 技术

**第四阶段：实战演练（持续）**

1. 分析真实网站案例
2. 参与 CTF 比赛
3. 阅读优秀开源项目

---

### Q3: Web 逆向合法吗？

**A**:

**合法性取决于目的和方式**:

**✅ 合法场景**:

- 学习和研究目的
- 自己网站的安全测试
- 获得授权的渗透测试
- CTF 比赛
- 开源项目分析

**❌ 非法场景**:

- 未经授权访问他人系统
- 窃取敏感数据
- 恶意攻击网站
- 侵犯知识产权
- 违反用户协议（ToS）

**建议**:

1. 遵守 `robots.txt`
2. 尊重网站的服务条款
3. 不要进行 DDoS 攻击
4. 不要爬取敏感个人信息
5. 设置合理的请求频率

---

## 技术问题

### Q4: 如何绕过反爬虫检测？

**A**:

**分层对抗策略**:

**第一层：基础伪装**

```python
headers = {
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...',
'Referer': 'https://example.com/',
'Accept': 'text/html,application/xhtml+xml,application/xml',
'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}
```

**第二层：行为模拟**

```python
import time
import random

time.sleep(random.uniform(1, 3)) # 随机延迟
```

**第三层：使用真实浏览器**

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
browser = p.chromium.launch()
page = browser.new_page()
page.goto('https://example.com')
```

**第四层：代理轮换**

```python
proxies = ['http://proxy1.com:8080', 'http://proxy2.com:8080']
proxy = random.choice(proxies)
```

详见: [反爬虫技术深度分析](../04-Advanced-Recipes/anti_scraping_deep_dive.md)

---

### Q5: 如何找到加密参数的生成位置？

**A**:

**方法一：全局搜索**

1. 打开 DevTools -> Sources
2. `Ctrl+Shift+F` 全局搜索参数名（如 `sign`）
3. 查看每个结果，找到赋值位置

**方法二：XHR 断点**

1. DevTools -> Sources -> XHR/fetch Breakpoints
2. 添加 URL 关键词（如 `/api/`）
3. 刷新页面，断点停下
4. 查看 Call Stack，定位生成函数

**方法三：Hook 拦截**

```javascript
const originalFetch = window.fetch;
window.fetch = function (...args) {
console.log("[Fetch]", args);
debugger; // 自动断点
return originalFetch.apply(this, args);
};
```

详见: [调试技巧与断点设置](../03-Basic-Recipes/debugging_techniques.md)

---

### Q6: JavaScript 代码被混淆了怎么办？

**A**:

**分步还原**:

**第一步：格式化**

```bash
# 使用 Prettier
prettier --write obfuscated.js
```

**第二步：识别混淆类型**

- 变量名混淆：`_0x1a2b`
- 字符串数组：`var arr = ['str1', 'str2']`
- 控制流平坦化：`switch-case` 结构

**第三步：使用工具**

- 在线工具: https://lelinhtinh.github.io/de4js/
- AST 工具: Babel
- Webpack 反打包: webcrack

**第四步：手动分析**

- 动态调试优于静态分析
- 结合 DevTools 断点
- 理解核心逻辑即可，无需完全还原

详见: [JavaScript 反混淆](../04-Advanced-Recipes/javascript_deobfuscation.md)

---

### Q7: 如何处理动态加载的内容？

**A**:

**方法一：Puppeteer 等待加载**

```javascript
await page.goto("https://example.com");

// 等待特定元素出现
await page.waitForSelector(".item");

// 等待网络空闲
await page.waitForNetworkIdle();
```

**方法二：Selenium 等待**

```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

wait = WebDriverWait(driver, 10)
element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'item')))
```

**方法三：分析 AJAX 请求**

1. 直接分析动态内容的 API 请求
2. 跳过页面渲染，直接请求 API
3. 效率更高

---

## 相关章节

- [学习资源](./learning_resources.md)
- [开源项目推荐](./github_projects.md)
- [逆向工程工作流](../03-Basic-Recipes/re_workflow.md)
