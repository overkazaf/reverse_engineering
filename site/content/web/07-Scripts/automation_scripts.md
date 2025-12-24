---
title: "浏览器自动化脚本"
date: 2025-12-25
weight: 10
---

# 浏览器自动化脚本

## 概述

浏览器自动化是 Web 逆向的重要手段。通过模拟真实用户操作，可以绕过许多反爬虫检测。本章介绍 Puppeteer 和 Playwright 的实战脚本。

---

## Puppeteer 脚本

### 基础模板

```javascript
const puppeteer = require("puppeteer");

(async () => {
// 启动浏览器
const browser = await puppeteer.launch({
headless: false, // 显示浏览器窗口
devtools: true, // 打开 DevTools
});

// 打开新页面
const page = await browser.newPage();

// 访问网站
await page.goto("https://example.com", {
waitUntil: "networkidle2", // 等待网络空闲
});

// 截图
await page.screenshot({ path: "screenshot.png" });

// 关闭浏览器
await browser.close();
})();
```

### 登录脚本

```javascript
const puppeteer = require("puppeteer");

async function login(username, password) {
const browser = await puppeteer.launch({ headless: false });
const page = await browser.newPage();

// 访问登录页
await page.goto("https://example.com/login");

// 填写表单
await page.type("#username", username);
await page.type("#password", password);

// 点击登录按钮
await page.click("#login-button");

// 等待跳转
await page.waitForNavigation();

// 获取 Cookie
const cookies = await page.cookies();
console.log("Cookies:", cookies);

await browser.close();
return cookies;
}

login("myuser", "mypassword");
```

### 无限滚动加载

```javascript
async function scrollToBottom(page) {
await page.evaluate(async () => {
await new Promise((resolve) => {
let totalHeight = 0;
const distance = 100;

const timer = setInterval(() => {
const scrollHeight = document.body.scrollHeight;
window.scrollBy(0, distance);
totalHeight += distance;

if (totalHeight >= scrollHeight) {
clearInterval(timer);
resolve();
}
}, 100);
});
});
}

// 使用
const page = await browser.newPage();
await page.goto("https://example.com/infinite-scroll");
await scrollToBottom(page);
```

### 处理滑块验证码

```javascript
async function solveSlider(page) {
// 等待滑块出现
await page.waitForSelector(".slider");

// 获取滑块和轨道元素
const slider = await page.$(".slider-button");
const track = await page.$(".slider-track");

// 获取轨道宽度
const trackBox = await track.boundingBox();
const distance = trackBox.width - 40; // 减去滑块宽度

// 模拟人类拖动轨迹
await slider.hover();
await page.mouse.down();

// 生成贝塞尔曲线轨迹
const steps = 20;
for (let i = 0; i <= steps; i++) {
const x = (distance / steps) * i;
const y = Math.sin((i / steps) * Math.PI) * 10; // 添加随机抖动
await page.mouse.move(trackBox.x + x, trackBox.y + y);
await page.waitForTimeout(Math.random() * 10 + 5);
}

await page.mouse.up();
}
```

### 拦截和修改请求

```javascript
const page = await browser.newPage();

// 启用请求拦截
await page.setRequestInterception(true);

page.on("request", (request) => {
// 拦截特定 URL
if (request.url().includes("/api/data")) {
// 修改请求头
request.continue({
headers: {
...request.headers(),
"X-Custom-Header": "MyValue",
},
});
} else {
request.continue();
}
});

page.on("response", async (response) => {
const url = response.url();
if (url.includes("/api/data")) {
const data = await response.json();
console.log("API Response:", data);
}
});

await page.goto("https://example.com");
```

### 注入 Hook 脚本

```javascript
const page = await browser.newPage();

// 在页面加载前注入脚本
await page.evaluateOnNewDocument(() => {
// Hook fetch
const originalFetch = window.fetch;
window.fetch = async function (...args) {
console.log("[Fetch]", args[0]);
const response = await originalFetch.apply(this, args);
return response;
};

// Hook localStorage
const originalSetItem = localStorage.setItem;
localStorage.setItem = function (key, value) {
console.log("[LocalStorage]", key, "=", value);
return originalSetItem.apply(this, arguments);
};
});

await page.goto("https://example.com");
```

### 绕过 Webdriver 检测

```javascript
const puppeteer = require("puppeteer-extra");
const StealthPlugin = require("puppeteer-extra-plugin-stealth");

puppeteer.use(StealthPlugin());

const browser = await puppeteer.launch({
headless: false,
args: [
"--disable-blink-features=AutomationControlled",
"--disable-dev-shm-usage",
"--no-sandbox",
],
});

const page = await browser.newPage();

// 隐藏 webdriver 特征
await page.evaluateOnNewDocument(() => {
Object.defineProperty(navigator, "webdriver", {
get: () => undefined,
});

// 伪造 Chrome 插件
Object.defineProperty(navigator, "plugins", {
get: () => [1, 2, 3, 4, 5],
});
});

await page.goto("https://bot-detection.com");
```

---

## Playwright 脚本

### 基础模板

```javascript
const { chromium } = require("playwright");

(async () => {
const browser = await chromium.launch({ headless: false });
const context = await browser.newContext();
const page = await context.newPage();

await page.goto("https://example.com");
await page.screenshot({ path: "screenshot.png" });

await browser.close();
})();
```

### 多浏览器测试

```javascript
const { chromium, firefox, webkit } = require("playwright");

async function testAllBrowsers(url) {
for (const browserType of [chromium, firefox, webkit]) {
const browser = await browserType.launch();
const page = await browser.newPage();
await page.goto(url);

const title = await page.title();
console.log(`${browserType.name()}: ${title}`);

await browser.close();
}
}

testAllBrowsers("https://example.com");
```

### 移动设备模拟

```javascript
const { devices } = require("playwright");

const iPhone = devices["iPhone 12"];

const browser = await chromium.launch();
const context = await browser.newContext({
...iPhone,
locale: "zh-CN",
geolocation: { longitude: 116.4, latitude: 39.9 }, // 北京
permissions: ["geolocation"],
});

const page = await context.newPage();
await page.goto("https://example.com");
```

### 并发爬取

```javascript
async function scrapeMultiplePages(urls) {
const browser = await chromium.launch();
const context = await browser.newContext();

// 并发打开多个页面
const promises = urls.map(async (url) => {
const page = await context.newPage();
await page.goto(url);

const data = await page.evaluate(() => {
return {
title: document.title,
content: document.body.innerText,
};
});

await page.close();
return data;
});

const results = await Promise.all(promises);
await browser.close();

return results;
}

const urls = [
"https://example.com/page1",
"https://example.com/page2",
"https://example.com/page3",
];

scrapeMultiplePages(urls).then(console.log);
```

### 保存登录状态

```javascript
// 登录并保存状态
async function saveLoginState() {
const browser = await chromium.launch({ headless: false });
const context = await browser.newContext();
const page = await context.newPage();

await page.goto("https://example.com/login");
await page.fill("#username", "myuser");
await page.fill("#password", "mypassword");
await page.click("#login-button");
await page.waitForNavigation();

// 保存存储状态（包含 Cookie、LocalStorage 等）
await context.storageState({ path: "state.json" });
await browser.close();
}

// 加载登录状态
async function useLoginState() {
const browser = await chromium.launch({ headless: false });
const context = await browser.newContext({
storageState: "state.json",
});
const page = await context.newPage();

// 直接访问需要登录的页面
await page.goto("https://example.com/dashboard");

await browser.close();
}
```

### 网络监控和 HAR 导出

```javascript
const context = await browser.newContext({
recordHar: { path: "network.har" },
});

const page = await context.newPage();
await page.goto("https://example.com");

// 操作页面...

await context.close(); // HAR 文件会自动保存
```

---

## 进阶技巧

### 1. 人类行为模拟

```javascript
// 随机延迟
function randomDelay(min = 100, max = 500) {
return Math.floor(Math.random() * (max - min + 1) + min);
}

// 模拟真实打字
async function typeHuman(page, selector, text) {
await page.click(selector);
for (const char of text) {
await page.type(selector, char);
await page.waitForTimeout(randomDelay(50, 150));
}
}

// 随机鼠标移动
async function randomMouseMove(page) {
const x = Math.floor(Math.random() * 800);
const y = Math.floor(Math.random() * 600);
await page.mouse.move(x, y);
}
```

### 2. 代理池集成

```javascript
const proxies = [
"http://proxy1.com:8080",
"http://proxy2.com:8080",
"http://proxy3.com:8080",
];

async function scrapeWithProxy(url) {
const proxy = proxies[Math.floor(Math.random() * proxies.length)];

const browser = await chromium.launch({
proxy: { server: proxy },
});

const page = await browser.newPage();
await page.goto(url);

// 爬取数据...

await browser.close();
}
```

### 3. 失败重试

```javascript
async function retryOperation(operation, maxRetries = 3) {
for (let i = 0; i < maxRetries; i++) {
try {
return await operation();
} catch (error) {
console.log(`Attempt ${i + 1} failed:`, error.message);
if (i === maxRetries - 1) throw error;
await new Promise((resolve) => setTimeout(resolve, 1000 * (i + 1)));
}
}
}

// 使用
await retryOperation(async () => {
await page.goto("https://example.com");
await page.click("#button");
});
```

---

## 完整爬虫示例

```javascript
const puppeteer = require("puppeteer-extra");
const StealthPlugin = require("puppeteer-extra-plugin-stealth");
const fs = require("fs");

puppeteer.use(StealthPlugin());

class WebScraper {
constructor() {
this.browser = null;
this.page = null;
}

async init() {
this.browser = await puppeteer.launch({
headless: false,
args: ["--no-sandbox"],
});
this.page = await this.browser.newPage();
await this.page.setViewport({ width: 1920, height: 1080 });
}

async login(username, password) {
await this.page.goto("https://example.com/login");
await this.page.type("#username", username, { delay: 100 });
await this.page.type("#password", password, { delay: 100 });
await this.page.click("#login-button");
await this.page.waitForNavigation();
}

async scrapeData(url) {
await this.page.goto(url);

const data = await this.page.evaluate(() => {
const items = [];
document.querySelectorAll(".item").forEach((item) => {
items.push({
title: item.querySelector(".title")?.innerText,
price: item.querySelector(".price")?.innerText,
link: item.querySelector("a")?.href,
});
});
return items;
});

return data;
}

async close() {
await this.browser.close();
}
}

// 使用
(async () => {
const scraper = new WebScraper();
await scraper.init();
await scraper.login("myuser", "mypassword");

const data = await scraper.scrapeData("https://example.com/products");
fs.writeFileSync("data.json", JSON.stringify(data, null, 2));

await scraper.close();
})();
```

---

## 商业化浏览器自动化解决方案对比

在大规模数据采集和自动化测试场景中，商业化服务可以显著降低运维成本和技术门槛。以下是市场主流方案的详细对比。

### 1. 商业浏览器云服务（Browser-as-a-Service）

#### Browserless.io

**核心优势**:

- 托管式无头浏览器服务
- 自动扩展，无需运维
- 内置反检测和代理池
- 支持 Puppeteer/Playwright API

**定价**:

- Hobby: $29/月（10,000 次请求）
- Startup: $79/月（50,000 次请求）
- Business: $299/月（250,000 次请求）
- Enterprise: 定制化

**技术规格**:

```javascript
// 使用示例 - 与 Puppeteer 完全兼容
const browser = await puppeteer.connect({
browserWSEndpoint: "wss://chrome.browserless.io?token=YOUR_TOKEN",
});
```

**适用场景**:

- PDF 生成服务
- 网页截图 API
- 轻量级爬虫（< 100 万页/月）

**官网**: https://www.browserless.io/

**优劣分析**:

- ✅ 零运维成本
- ✅ 按需付费
- ❌ 受限于供应商网络
- ❌ 大规模场景成本高

---

#### BrowserStack Automate

**核心优势**:

- 2000+真实设备和浏览器组合
- 企业级可靠性（99.9% SLA）
- 详细的测试报告和视频录制
- 与 CI/CD 无缝集成

**定价**:

- Team: $29/月（1 个并发）
- Business: $99/月（5 个并发）
- Enterprise: $299/月起（25 个并发）

**技术规格**:

```javascript
// Selenium 集成
const caps = {
"bstack:options": {
userName: "YOUR_USERNAME",
accessKey: "YOUR_KEY",
},
browserName: "Chrome",
browserVersion: "latest",
};
```

**适用场景**:

- 跨浏览器兼容性测试
- 移动端自动化测试
- 企业级 QA 自动化

**官网**: https://www.browserstack.com/

**竞品对比**:

- Sauce Labs（类似定价和功能）
- LambdaTest（更便宜，$15/月起）

---

#### Apify

**核心优势**:

- 专业网页爬取平台
- 1000+ 现成的爬虫 Actor
- 内置代理池和反检测
- Serverless 架构

**定价**:

- Free: $0（每月$5 额度）
- Personal: $49/月
- Team: $499/月
- Enterprise: 定制化

**技术特点**:

```javascript
// Actor 示例 - 爬取Google搜索
const Apify = require("apify");

Apify.main(async () => {
const requestQueue = await Apify.openRequestQueue();
await requestQueue.addRequest({ url: "https://google.com" });

const crawler = new Apify.PuppeteerCrawler({
requestQueue,
handlePageFunction: async ({ page, request }) => {
const title = await page.title();
console.log(`Title: ${title}`);
},
});

await crawler.run();
});
```

**适用场景**:

- 中大规模数据采集
- 市场监测和价格追踪
- 无需维护基础设施的团队

**官网**: https://apify.com/

---

### 2. 验证码打码服务对比

| 服务商 | reCAPTCHA v2 | reCAPTCHA v3 | hCaptcha | 滑块验证码 | 价格（1000 次） | 成功率 | 速度 |
| -------------------- | ------------ | ------------ | -------- | ---------- | --------------- | ------ | ------ |
| **2Captcha** | ✅ | ✅ | ✅ | ✅ | $2.99 | 95%+ | 10-30s |
| **Anti-Captcha** | ✅ | ✅ | ✅ | ✅ | $2.00 | 96%+ | 8-25s |
| **CapSolver** | ✅ | ✅ | ✅ | ✅ | $1.50 | 94%+ | 15-35s |
| **DeathByCaptcha** | ✅ | ✅ | ❌ | ✅ | $1.39 | 92%+ | 20-40s |
| **CapMonster Cloud** | ✅ | ✅ | ✅ | ✅ | $0.90 | 93%+ | 15-30s |

#### 推荐方案

**2Captcha**（最可靠）

```javascript
const solver = new Captcha.Solver("YOUR_API_KEY");

const result = await solver.recaptcha({
pageurl: "https://example.com",
googlekey: "6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-",
version: "v2",
});

console.log("Token:", result.data);
```

**官网**: https://2captcha.com/
**成本估算**: 10 万次验证码 ≈ $300

---

**Anti-Captcha**（速度最快）

- 支持浏览器扩展自动集成
- 提供 Puppeteer/Playwright 插件

**官网**: https://anti-captcha.com/

---

### 3. 代理 IP 服务对比

#### 住宅代理（Residential Proxy）

**Bright Data**（原 Luminati）

- 最大的住宅 IP 池（7200 万+）
- 按流量计费：$12.75/GB 起
- 企业级可靠性
- **官网**: https://brightdata.com/

**Smartproxy**

- 4000 万+ 住宅 IP
- 按流量计费：$12.50/GB 起
- 更友好的定价
- **官网**: https://smartproxy.com/

**对比**:
| 特性 | Bright Data | Smartproxy | Oxylabs |
|------|-------------|------------|---------|
| IP 池大小 | 7200 万+ | 4000 万+ | 1 亿+ |
| 价格/GB | $12.75 | $12.50 | $15.00 |
| 最低消费 | $500/月 | $75/月 | $300/月 |
| 成功率 | 99.5% | 99.3% | 99.6% |

---

#### 数据中心代理（Datacenter Proxy）

**成本低，适合大规模爬取**:

- Webshare: $2.00/10 个代理/月
- Proxy-Seller: $1.20/IP/月
- ProxyRack: $65/5000 端口/月

**局限**: 易被识别为代理，封禁率较高

---

### 4. 分布式爬虫平台对比

#### Scrapy Cloud（Scrapinghub）

**功能**:

- Scrapy 项目托管
- 自动扩展 Crawler
- 内置代理和反检测

**定价**:

- Free: 1 个爬虫
- Professional: $9/月/爬虫
- Enterprise: 定制化

**官网**: https://www.zyte.com/scrapy-cloud/

---

#### Crawlera（智能代理路由）

**功能**:

- 自动切换代理 IP
- 智能重试机制
- 绕过反爬虫

**定价**: $25/月起（10,000 次请求）

**Python 集成**:

```python
import requests

proxies = {
'http': 'http://YOUR_API_KEY:@proxy.crawlera.com:8011/'
}

response = requests.get('https://example.com', proxies=proxies)
```

---

#### ParseHub（可视化爬虫）

**特点**:

- 无代码爬虫构建器
- 自动处理 JavaScript 渲染
- 云端运行

**定价**:

- Free: 5 个项目
- Standard: $189/月（20 个项目）
- Professional: $599/月（无限项目）

**适用**: 非技术人员、快速原型

**官网**: https://www.parsehub.com/

---

### 5. 成本效益分析

#### 案例：电商价格监控（100,000 页/天）

**方案 A：自建**

- 成本：服务器 $100/月 + 代理 $200/月 = **$300/月**
- 运维：需要 DevOps 工程师
- 风险：需要持续维护反检测

**方案 B：Apify**

- 成本：Team 计划 **$499/月**
- 运维：零运维
- 风险：低，平台负责反检测

**方案 C：Bright Data + Browserless**

- 成本：代理 $500/月 + 浏览器 $299/月 = **$799/月**
- 运维：最小化
- 风险：最低，企业级 SLA

**结论**:

- < 1 万页/天：自建最划算
- 1-10 万页/天：Apify 性价比高
- > 10 万页/天：混合方案（自建+商业代理）

---

### 6. 技术选型决策树

```
需要跨浏览器测试？
├─ 是 → BrowserStack/Sauce Labs
└─ 否 → 需要大规模爬取？
├─ 是（>10万页/天）→ 自建 + Bright Data代理
└─ 否 → 团队有DevOps？
├─ 是 → 自建Puppeteer Cluster
└─ 否 → Apify/ParseHub
```

---

### 7. 开源 vs 商业方案综合对比

| 维度 | 自建开源 | 半托管（Apify） | 全托管（BrowserStack） |
| -------------- | ---------- | --------------- | ---------------------- |
| **初始成本** | 低 | 中 | 低 |
| **运营成本** | 高（人力） | 低 | 零 |
| **可扩展性** | 需自行实现 | 自动扩展 | 自动扩展 |
| **技术控制** | 完全控制 | 部分控制 | 有限控制 |
| **学习曲线** | 陡峭 | 中等 | 平缓 |
| **反检测能力** | 需自己维护 | 平台提供 | 平台提供 |
| **合规性** | 自行负责 | 平台协助 | 平台负责 |

---

### 8. 2025 年新趋势

#### AI 驱动的爬虫

**Browse AI**

- 无代码 AI 爬虫训练
- 自动适应网站结构变化
- 价格：$49/月起

**官网**: https://www.browse.ai/

---

#### Playwright 托管服务

**Microsoft Playwright Testing**（预览版）

- Azure 云端 Playwright 执行
- 与 GitHub Actions 集成
- 按使用量计费

**状态**: 公开预览

---

### 9. 避坑指南

**常见陷阱**:

1. ❌ 过度依赖免费服务（稳定性差）
2. ❌ 忽视法律合规（爬虫合法性审查）
3. ❌ 低估运维成本（自建需要专人维护）
4. ❌ 选错代理类型（住宅 vs 数据中心）

**最佳实践**:

1. ✅ 从小规模开始，逐步扩展
2. ✅ 混合使用开源和商业工具
3. ✅ 设置合理的 rate limiting
4. ✅ 定期评估成本效益

---

## 相关章节

- [Puppeteer 与 Playwright](../02-Tooling/puppeteer_playwright.md)
- [Selenium WebDriver](../02-Tooling/selenium_webdriver.md)
- [JavaScript Hook 脚本](javascript_hook_scripts.md)
- [反爬虫对抗技术](../02-Techniques/anti_anti_scraping.md)
