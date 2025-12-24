---
title: "浏览器指纹识别"
weight: 10
---

# 浏览器指纹识别

## 概述

浏览器指纹（Browser Fingerprinting）是一种通过收集浏览器和设备的各种特征来唯一标识用户的技术。即使用户清除 Cookie 或使用隐身模式，仍然可以通过指纹追踪。

---

## 📚 前置知识

在开始本配方之前，建议先掌握以下内容：

| 知识领域 | 重要程度 | 参考资料 |
|----------|---------|---------|
| 浏览器架构 | 必需 | [浏览器架构](../01-Foundations/browser_architecture.md) |
| JavaScript 基础 | 必需 | [JavaScript 基础](../01-Foundations/javascript_basics.md) |
| DOM 与 BOM | 必需 | [DOM 与 BOM](../01-Foundations/dom_and_bom.md) |
| Hook 技术 | 推荐 | [Hook 技术](../03-Basic-Recipes/hooking_techniques.md) |
| 浏览器自动化 | 推荐 | [Puppeteer/Playwright](../02-Tooling/puppeteer_playwright.md) |

> 💡 **提示**: 浏览器指纹是现代反爬虫系统的**核心检测手段**。理解指纹的生成原理，才能有效地伪装和规避检测。建议配合 [Canvas 指纹](./canvas_fingerprinting.md) 和 [WebRTC 指纹](./webrtc_fingerprinting.md) 一起学习。

---

## 指纹组成要素

### 1. User-Agent

最基础的指纹信息，包含操作系统、浏览器版本等：

```javascript
navigator.userAgent;
// "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36..."
```

### 2. Screen 信息

```javascript
const screenInfo = {
width: screen.width,
height: screen.height,
colorDepth: screen.colorDepth,
pixelDepth: screen.pixelDepth,
availWidth: screen.availWidth,
availHeight: screen.availHeight,
};
```

### 3. 时区与语言

```javascript
const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone; // "Asia/Shanghai"
const language = navigator.language; // "zh-CN"
const languages = navigator.languages; // ["zh-CN", "zh", "en"]
```

### 4. 插件列表

```javascript
const plugins = Array.from(navigator.plugins).map((p) => p.name);
// ["Chrome PDF Plugin", "Chrome PDF Viewer", ...]
```

**注意**: 现代浏览器出于隐私考虑，已限制对插件列表的访问。

### 5. Canvas 指纹

通过 Canvas 渲染差异生成指纹（详见 [Canvas 指纹技术](../04-Advanced-Recipes/canvas_fingerprinting.md)）：

```javascript
function getCanvasFingerprint() {
const canvas = document.createElement("canvas");
const ctx = canvas.getContext("2d");
ctx.textBaseline = "top";
ctx.font = "14px Arial";
ctx.fillText("fingerprint", 2, 2);
return canvas.toDataURL();
}
```

### 6. WebGL 指纹

```javascript
function getWebGLFingerprint() {
const canvas = document.createElement("canvas");
const gl =
canvas.getContext("webgl") || canvas.getContext("experimental-webgl");

const debugInfo = gl.getExtension("WEBGL_debug_renderer_info");
const vendor = gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL);
const renderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);

return { vendor, renderer };
}
```

### 7. 音频指纹 (AudioContext)

```javascript
function getAudioFingerprint() {
const audioContext = new (window.AudioContext || window.webkitAudioContext)();
const oscillator = audioContext.createOscillator();
const analyser = audioContext.createAnalyser();
const gainNode = audioContext.createGain();
const scriptProcessor = audioContext.createScriptProcessor(4096, 1, 1);

// 通过音频处理的细微差异生成指纹
// ... 复杂的音频处理逻辑
}
```

### 8. 字体检测

```javascript
function detectFonts() {
const baseFonts = ["monospace", "sans-serif", "serif"];
const testFonts = [
"Arial",
"Verdana",
"Times New Roman",
"Courier",
"Comic Sans MS",
];

const detectedFonts = [];

testFonts.forEach((font) => {
// 通过测量文本宽度的变化来检测字体是否存在
// ... 实现逻辑
});

return detectedFonts;
}
```

### 9. 硬件信息

```javascript
const hardwareInfo = {
cpuCores: navigator.hardwareConcurrency, // CPU 核心数
deviceMemory: navigator.deviceMemory, // 设备内存（GB）
platform: navigator.platform, // "Win32", "MacIntel"
vendor: navigator.vendor, // "Google Inc."
};
```

---

## 指纹库使用

### FingerprintJS

最流行的开源指纹库：

```javascript
// 安装：npm install @fingerprintjs/fingerprintjs

import FingerprintJS from "@fingerprintjs/fingerprintjs";

// 初始化
const fpPromise = FingerprintJS.load();

// 获取指纹
fpPromise
.then((fp) => fp.get())
.then((result) => {
console.log("Visitor ID:", result.visitorId);
console.log("Components:", result.components);
});
```

**特点**:

- 准确率高（99.5%）
- 持久性强
- 开源免费

---

## 检测指纹采集

### 方法一：监控 API 调用

```javascript
// Hook Canvas API
const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
HTMLCanvasElement.prototype.toDataURL = function () {
console.log("[Fingerprint] Canvas fingerprinting detected!");
console.trace();
return originalToDataURL.apply(this, arguments);
};

// Hook WebGL
const originalGetParameter = WebGLRenderingContext.prototype.getParameter;
WebGLRenderingContext.prototype.getParameter = function (param) {
console.log("[Fingerprint] WebGL fingerprinting detected!", param);
return originalGetParameter.apply(this, arguments);
};
```

### 方法二：检查第三方脚本

在 DevTools -> Sources 中搜索关键词：

- `fingerprint`
- `FingerprintJS`
- `canvas.toDataURL`
- `WEBGL_debug_renderer_info`

---

## 反指纹技术

### 1. 使用浏览器插件

**推荐插件**:

- **Canvas Blocker** (Firefox/Chrome): 阻止 Canvas 指纹
- **Privacy Badger**: 阻止追踪器
- **uBlock Origin**: 阻止广告和追踪

### 2. 修改 User-Agent

```javascript
// Puppeteer
await page.setUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...");

// Selenium
options.add_argument("user-agent=Mozilla/5.0...");
```

### 3. 伪造 Canvas/WebGL

```javascript
// 注入噪点到 Canvas
const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
HTMLCanvasElement.prototype.toDataURL = function () {
// 添加随机噪点
const ctx = this.getContext("2d");
const imageData = ctx.getImageData(0, 0, this.width, this.height);
for (let i = 0; i < imageData.data.length; i += 4) {
if (Math.random() < 0.001) {
imageData.data[i] = Math.floor(Math.random() * 256);
}
}
ctx.putImageData(imageData, 0, 0);
return originalToDataURL.apply(this, arguments);
};
```

### 4. 使用指纹伪造库

**Puppeteer Stealth Plugin**:

```javascript
const puppeteer = require("puppeteer-extra");
const StealthPlugin = require("puppeteer-extra-plugin-stealth");

puppeteer.use(StealthPlugin());

const browser = await puppeteer.launch();
```

### 5. 统一环境特征

确保所有请求使用相同的：

- User-Agent
- Screen 分辨率
- 时区和语言
- Canvas/WebGL 输出

---

## 绕过策略

### 策略一：使用真实浏览器

Puppeteer/Playwright 控制真实浏览器，天然具有完整指纹。

### 策略二：指纹池

维护多个不同的指纹配置，轮换使用：

```python
FINGERPRINT_POOL = [
{
'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0',
'screen': {'width': 1920, 'height': 1080},
'timezone': 'America/New_York',
'language': 'en-US'
},
{
'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ...',
'screen': {'width': 1440, 'height': 900},
'timezone': 'America/Los_Angeles',
'language': 'en-US'
}
]

# 随机选择一个指纹
fingerprint = random.choice(FINGERPRINT_POOL)
```

### 策略三：住宅代理

高质量住宅代理通常自带真实用户的完整指纹。

---

## 测试工具

### 在线测试

- [AmIUnique](https://amiunique.org/) - 指纹唯一性测试
- [BrowserLeaks](https://browserleaks.com/) - 全面的浏览器信息泄露检测
- [Cover Your Tracks](https://coveryourtracks.eff.org/) - EFF 的隐私测试
- [Fingerprint.com Demo](https://fingerprint.com/demo/) - FingerprintJS 演示

### 命令行测试

```bash
# 使用 curl 测试 TLS 指纹
curl --user-agent "Mozilla/5.0..." https://tls.peet.ws/api/clean
```

---

## 实战案例

### 案例：某社交网站检测

**现象**: Python requests 访问返回空数据，浏览器正常。

**分析步骤**:

1. 对比请求头 - 已伪造，仍失败
2. 检查 Cookie - 已携带，仍失败
3. 怀疑指纹检测

**解决方案**:

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option('excludeSwitches', ['enable-automation'])
options.add_experimental_option('useAutomationExtension', False)

driver = webdriver.Chrome(options=options)

# 修改 navigator.webdriver
driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
'source': '''
Object.defineProperty(navigator, 'webdriver', {
get: () => undefined
})
'''
})

driver.get('https://target.com')
```

---

## 总结

浏览器指纹是现代反爬虫的核心技术之一。对抗策略：

1. 使用真实浏览器（Puppeteer/Selenium）
2. 安装反指纹插件
3. 伪造指纹信息
4. 使用指纹池轮换
5. 采用住宅代理

---

## 相关章节

- [Canvas 指纹技术](../04-Advanced-Recipes/canvas_fingerprinting.md)
- [TLS 指纹识别](../04-Advanced-Recipes/tls_fingerprinting.md)
- [反爬虫技术深度分析](../04-Advanced-Recipes/anti_scraping_deep_dive.md)
