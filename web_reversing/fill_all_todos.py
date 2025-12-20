#!/usr/bin/env python3
"""
批量填充所有包含TODO的文档 - 完整版
这个脚本会一次性填充所有剩余的模板文档
"""

from pathlib import Path
import re

# 所有需要填充的文档内容 - 按模块组织
ALL_TODO_DOCS = {}

# === 02-Techniques 模块 ===
ALL_TODO_DOCS["02-Techniques/browser_fingerprinting.md"] = """# 浏览器指纹识别

## 概述

浏览器指纹（Browser Fingerprinting）是一种通过收集浏览器和设备的各种特征来唯一标识用户的技术。即使用户清除Cookie或使用隐身模式，仍然可以通过指纹追踪。

---

## 指纹组成要素

### 1. User-Agent

最基础的指纹信息，包含操作系统、浏览器版本等：

```javascript
navigator.userAgent
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
    availHeight: screen.availHeight
};
```

### 3. 时区与语言

```javascript
const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;  // "Asia/Shanghai"
const language = navigator.language;  // "zh-CN"
const languages = navigator.languages;  // ["zh-CN", "zh", "en"]
```

### 4. 插件列表

```javascript
const plugins = Array.from(navigator.plugins).map(p => p.name);
// ["Chrome PDF Plugin", "Chrome PDF Viewer", ...]
```

**注意**: 现代浏览器出于隐私考虑，已限制对插件列表的访问。

### 5. Canvas 指纹

通过 Canvas 渲染差异生成指纹（详见 [Canvas 指纹技术](../03-Advanced-Topics/canvas_fingerprinting.md)）：

```javascript
function getCanvasFingerprint() {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    ctx.textBaseline = 'top';
    ctx.font = '14px Arial';
    ctx.fillText('fingerprint', 2, 2);
    return canvas.toDataURL();
}
```

### 6. WebGL 指纹

```javascript
function getWebGLFingerprint() {
    const canvas = document.createElement('canvas');
    const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');

    const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
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
    const baseFonts = ['monospace', 'sans-serif', 'serif'];
    const testFonts = ['Arial', 'Verdana', 'Times New Roman', 'Courier', 'Comic Sans MS'];

    const detectedFonts = [];

    testFonts.forEach(font => {
        // 通过测量文本宽度的变化来检测字体是否存在
        // ... 实现逻辑
    });

    return detectedFonts;
}
```

### 9. 硬件信息

```javascript
const hardwareInfo = {
    cpuCores: navigator.hardwareConcurrency,  // CPU 核心数
    deviceMemory: navigator.deviceMemory,  // 设备内存（GB）
    platform: navigator.platform,  // "Win32", "MacIntel"
    vendor: navigator.vendor  // "Google Inc."
};
```

---

## 指纹库使用

### FingerprintJS

最流行的开源指纹库：

```javascript
// 安装：npm install @fingerprintjs/fingerprintjs

import FingerprintJS from '@fingerprintjs/fingerprintjs'

// 初始化
const fpPromise = FingerprintJS.load();

// 获取指纹
fpPromise.then(fp => fp.get()).then(result => {
    console.log('Visitor ID:', result.visitorId);
    console.log('Components:', result.components);
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
HTMLCanvasElement.prototype.toDataURL = function() {
    console.log('[Fingerprint] Canvas fingerprinting detected!');
    console.trace();
    return originalToDataURL.apply(this, arguments);
};

// Hook WebGL
const originalGetParameter = WebGLRenderingContext.prototype.getParameter;
WebGLRenderingContext.prototype.getParameter = function(param) {
    console.log('[Fingerprint] WebGL fingerprinting detected!', param);
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
await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...');

// Selenium
options.add_argument('user-agent=Mozilla/5.0...')
```

### 3. 伪造 Canvas/WebGL

```javascript
// 注入噪点到 Canvas
const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
HTMLCanvasElement.prototype.toDataURL = function() {
    // 添加随机噪点
    const ctx = this.getContext('2d');
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
const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');

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

- [Canvas 指纹技术](../03-Advanced-Topics/canvas_fingerprinting.md)
- [TLS 指纹识别](../03-Advanced-Topics/tls_fingerprinting.md)
- [反爬虫技术深度分析](../03-Advanced-Topics/anti_scraping_deep_dive.md)
"""

# === 06-Scripts 模块 - 最实用的部分 ===
ALL_TODO_DOCS["06-Scripts/deobfuscation_scripts.md"] = """# 反混淆脚本

## 概述

JavaScript 混淆是保护代码逻辑的常用手段。本章提供常用的反混淆脚本和技术，帮助还原混淆后的代码。

---

## 混淆类型识别

### 1. 变量名混淆

**特征**:
```javascript
var _0x1a2b = 'Hello';
var _0x3c4d = 'World';
console.log(_0x1a2b, _0x3c4d);
```

**工具**: Prettier 格式化后手动重命名

### 2. 字符串数组混淆

**特征**:
```javascript
var _0x1234 = ['Hello', 'World', 'console', 'log'];
var _0xa = _0x1234[0];
var _0xb = _0x1234[1];
window[_0x1234[2]][_0x1234[3]](_0xa, _0xb);
```

**脚本**: 见下方字符串数组还原脚本

### 3. 控制流平坦化

**特征**:
```javascript
var _0x1 = 0;
while(true) {
    switch(_0x1) {
        case 0: console.log('A'); _0x1 = 1; break;
        case 1: console.log('B'); _0x1 = 2; break;
        case 2: return;
    }
}
```

### 4. 死代码注入

**特征**:
```javascript
function real() {
    var fake1 = 123;
    if (false) { /* 永远不会执行的代码 */ }
    return 'real';
}
```

---

## 在线工具

### 1. Prettier

**用途**: 格式化压缩的代码

```bash
# 安装
npm install -g prettier

# 格式化
prettier --write obfuscated.js
```

**在线版**: https://prettier.io/playground/

### 2. JS-Beautify

**用途**: 美化 JavaScript 代码

```bash
npm install -g js-beautify
js-beautify obfuscated.js > formatted.js
```

**在线版**: https://beautifier.io/

### 3. de4js

**用途**: 综合反混淆工具

**在线版**: https://lelinhtinh.github.io/de4js/

支持:
- JSFuck
- JJencode
- AAencode
- URLencode
- Packer
- JavaScript Obfuscator

---

## AST 反混淆脚本

### 基础框架

使用 Babel 解析和转换 AST：

```javascript
const parser = require("@babel/parser");
const traverse = require("@babel/traverse").default;
const generator = require("@babel/generator").default;
const t = require("@babel/types");
const fs = require("fs");

// 1. 读取混淆代码
const code = fs.readFileSync("obfuscated.js", "utf-8");

// 2. 解析为 AST
const ast = parser.parse(code);

// 3. 遍历和转换
traverse(ast, {
    // 在这里添加转换规则
});

// 4. 生成代码
const output = generator(ast, {}, code);
fs.writeFileSync("deobfuscated.js", output.code);
```

### 脚本 1: 常量折叠

**目标**: 计算常量表达式

```javascript
traverse(ast, {
    BinaryExpression(path) {
        // 如果两个操作数都是字面量
        if (t.isLiteral(path.node.left) && t.isLiteral(path.node.right)) {
            // 计算结果
            const result = eval(path.toString());
            // 替换为结果
            path.replaceWith(t.valueToNode(result));
        }
    }
});
```

**示例**:
```javascript
// Before
var a = 1 + 2;

// After
var a = 3;
```

### 脚本 2: 字符串数组还原

**目标**: 还原字符串数组引用

```javascript
let stringArray = [];

traverse(ast, {
    // 第一步：找到字符串数组
    VariableDeclarator(path) {
        if (t.isArrayExpression(path.node.init)) {
            const name = path.node.id.name;
            stringArray = path.node.init.elements.map(e => e.value);
        }
    },

    // 第二步：替换数组访问
    MemberExpression(path) {
        // _0x1234[0] => stringArray[0]
        if (t.isIdentifier(path.node.object) &&
            t.isNumericLiteral(path.node.property)) {
            const index = path.node.property.value;
            const value = stringArray[index];
            if (value !== undefined) {
                path.replaceWith(t.stringLiteral(value));
            }
        }
    }
});
```

**示例**:
```javascript
// Before
var _0x1234 = ['log', 'Hello'];
console[_0x1234[0]](_0x1234[1]);

// After
console['log']('Hello');
// 后续还可以继续优化为: console.log('Hello');
```

### 脚本 3: 计算成员表达式

**目标**: `obj['prop']` → `obj.prop`

```javascript
traverse(ast, {
    MemberExpression(path) {
        // 如果是 obj['prop'] 形式
        if (path.node.computed && t.isStringLiteral(path.node.property)) {
            const propName = path.node.property.value;
            // 检查是否是合法标识符
            if (/^[a-zA-Z_$][a-zA-Z0-9_$]*$/.test(propName)) {
                path.node.computed = false;
                path.node.property = t.identifier(propName);
            }
        }
    }
});
```

**示例**:
```javascript
// Before
console['log']('Hello');

// After
console.log('Hello');
```

### 脚本 4: 删除死代码

**目标**: 删除 `if (false)` 等死代码

```javascript
traverse(ast, {
    IfStatement(path) {
        // 如果条件是 false
        if (t.isBooleanLiteral(path.node.test, { value: false })) {
            // 删除整个 if 语句
            path.remove();
        }
        // 如果条件是 true
        else if (t.isBooleanLiteral(path.node.test, { value: true })) {
            // 用 consequent 替换整个 if
            path.replaceWithMultiple(path.node.consequent.body);
        }
    }
});
```

### 脚本 5: 函数内联

**目标**: 内联简单的包装函数

```javascript
const functionMap = {};

traverse(ast, {
    // 收集函数定义
    FunctionDeclaration(path) {
        const name = path.node.id.name;
        // 只处理简单的返回语句函数
        if (path.node.body.body.length === 1 &&
            t.isReturnStatement(path.node.body.body[0])) {
            functionMap[name] = path.node.body.body[0].argument;
        }
    },

    // 替换函数调用
    CallExpression(path) {
        if (t.isIdentifier(path.node.callee)) {
            const name = path.node.callee.name;
            if (functionMap[name]) {
                // 替换为函数体
                path.replaceWith(functionMap[name]);
            }
        }
    }
});
```

---

## 完整反混淆流程

### 自动化脚本

```javascript
const fs = require("fs");
const parser = require("@babel/parser");
const traverse = require("@babel/traverse").default;
const generator = require("@babel/generator").default;
const t = require("@babel/types");

function deobfuscate(inputFile, outputFile) {
    console.log(`[1/5] 读取文件: ${inputFile}`);
    const code = fs.readFileSync(inputFile, "utf-8");

    console.log("[2/5] 解析 AST");
    const ast = parser.parse(code);

    console.log("[3/5] 常量折叠");
    constantFolding(ast);

    console.log("[4/5] 字符串数组还原");
    restoreStringArray(ast);

    console.log("[5/5] 清理和格式化");
    cleanup(ast);

    const output = generator(ast, { comments: false }, code);
    fs.writeFileSync(outputFile, output.code);
    console.log(`✅ 完成! 输出到: ${outputFile}`);
}

function constantFolding(ast) {
    traverse(ast, {
        BinaryExpression(path) {
            if (path.isConstantExpression()) {
                const result = path.evaluate();
                if (result.confident) {
                    path.replaceWith(t.valueToNode(result.value));
                }
            }
        }
    });
}

function restoreStringArray(ast) {
    let stringArray = [];
    let arrayName = "";

    traverse(ast, {
        VariableDeclarator(path) {
            if (t.isArrayExpression(path.node.init)) {
                arrayName = path.node.id.name;
                stringArray = path.node.init.elements.map(e => e.value);
            }
        }
    });

    if (stringArray.length === 0) return;

    traverse(ast, {
        MemberExpression(path) {
            if (t.isIdentifier(path.node.object, { name: arrayName }) &&
                t.isNumericLiteral(path.node.property)) {
                const index = path.node.property.value;
                const value = stringArray[index];
                if (value !== undefined) {
                    path.replaceWith(t.stringLiteral(value));
                }
            }
        }
    });
}

function cleanup(ast) {
    traverse(ast, {
        // 删除空语句
        EmptyStatement(path) {
            path.remove();
        },
        // obj['prop'] -> obj.prop
        MemberExpression(path) {
            if (path.node.computed && t.isStringLiteral(path.node.property)) {
                const prop = path.node.property.value;
                if (/^[a-zA-Z_$][a-zA-Z0-9_$]*$/.test(prop)) {
                    path.node.computed = false;
                    path.node.property = t.identifier(prop);
                }
            }
        }
    });
}

// 使用示例
deobfuscate("obfuscated.js", "deobfuscated.js");
```

---

## 针对特定混淆器

### JavaScript Obfuscator

特征识别：
```javascript
var _0x1234 = function() {
    /* ... */
};
(function(_0xabc, _0xdef) {
    /* ... */
}(_0x1234, 0x123));
```

工具: https://github.com/javascript-deobfuscator/webcrack

### Webpack Bundle

使用 `webcrack`:
```bash
npm install -g webcrack
webcrack bundle.js -o output/
```

### JJencode

```javascript
function decode_jjencode(encoded) {
    // JJencode 使用颜文字编码
    return eval(encoded);
}
```

在线: https://utf-8.jp/public/jjencode.html

---

## 实战案例

### 案例：某电商网站混淆分析

**原始代码**:
```javascript
var _0x1a2b=['log','价格'];
console[_0x1a2b[0]](_0x1a2b[1]);
```

**反混淆步骤**:

1. **字符串数组提取**:
   ```javascript
   // _0x1a2b = ['log', '价格']
   ```

2. **替换引用**:
   ```javascript
   console['log']('价格');
   ```

3. **成员表达式优化**:
   ```javascript
   console.log('价格');
   ```

---

## 工具集合

| 工具 | 用途 | 链接 |
|------|------|------|
| **Prettier** | 格式化 | https://prettier.io/ |
| **de4js** | 综合反混淆 | https://lelinhtinh.github.io/de4js/ |
| **webcrack** | Webpack 反打包 | https://github.com/j4k0xb/webcrack |
| **Babel** | AST 操作 | https://babeljs.io/ |
| **AST Explorer** | 可视化 AST | https://astexplorer.net/ |

---

## 最佳实践

1. **分步处理**: 不要一次性处理所有混淆，逐步还原
2. **保留原文件**: 始终保留原始混淆代码作为备份
3. **验证正确性**: 每一步都要验证代码功能未被破坏
4. **结合动态调试**: AST 反混淆 + DevTools 调试结合使用
5. **识别混淆器**: 不同混淆器用不同工具，事半功倍

---

## 相关章节

- [JavaScript 反混淆](../02-Techniques/javascript_deobfuscation.md)
- [AST 解析工具](../01-Tooling/ast_parsing_tools.md)
- [调试技巧与断点设置](../02-Techniques/debugging_techniques.md)
"""

ALL_TODO_DOCS["06-Scripts/automation_scripts.md"] = """# 浏览器自动化脚本

## 概述

浏览器自动化是 Web 逆向的重要手段。通过模拟真实用户操作，可以绕过许多反爬虫检测。本章介绍 Puppeteer 和 Playwright 的实战脚本。

---

## Puppeteer 脚本

### 基础模板

```javascript
const puppeteer = require('puppeteer');

(async () => {
    // 启动浏览器
    const browser = await puppeteer.launch({
        headless: false,  // 显示浏览器窗口
        devtools: true,   // 打开 DevTools
    });

    // 打开新页面
    const page = await browser.newPage();

    // 访问网站
    await page.goto('https://example.com', {
        waitUntil: 'networkidle2'  // 等待网络空闲
    });

    // 截图
    await page.screenshot({ path: 'screenshot.png' });

    // 关闭浏览器
    await browser.close();
})();
```

### 登录脚本

```javascript
const puppeteer = require('puppeteer');

async function login(username, password) {
    const browser = await puppeteer.launch({ headless: false });
    const page = await browser.newPage();

    // 访问登录页
    await page.goto('https://example.com/login');

    // 填写表单
    await page.type('#username', username);
    await page.type('#password', password);

    // 点击登录按钮
    await page.click('#login-button');

    // 等待跳转
    await page.waitForNavigation();

    // 获取 Cookie
    const cookies = await page.cookies();
    console.log('Cookies:', cookies);

    await browser.close();
    return cookies;
}

login('myuser', 'mypassword');
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
await page.goto('https://example.com/infinite-scroll');
await scrollToBottom(page);
```

### 处理滑块验证码

```javascript
async function solveSlider(page) {
    // 等待滑块出现
    await page.waitForSelector('.slider');

    // 获取滑块和轨道元素
    const slider = await page.$('.slider-button');
    const track = await page.$('.slider-track');

    // 获取轨道宽度
    const trackBox = await track.boundingBox();
    const distance = trackBox.width - 40;  // 减去滑块宽度

    // 模拟人类拖动轨迹
    await slider.hover();
    await page.mouse.down();

    // 生成贝塞尔曲线轨迹
    const steps = 20;
    for (let i = 0; i <= steps; i++) {
        const x = (distance / steps) * i;
        const y = Math.sin(i / steps * Math.PI) * 10;  // 添加随机抖动
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

page.on('request', (request) => {
    // 拦截特定 URL
    if (request.url().includes('/api/data')) {
        // 修改请求头
        request.continue({
            headers: {
                ...request.headers(),
                'X-Custom-Header': 'MyValue'
            }
        });
    } else {
        request.continue();
    }
});

page.on('response', async (response) => {
    const url = response.url();
    if (url.includes('/api/data')) {
        const data = await response.json();
        console.log('API Response:', data);
    }
});

await page.goto('https://example.com');
```

### 注入 Hook 脚本

```javascript
const page = await browser.newPage();

// 在页面加载前注入脚本
await page.evaluateOnNewDocument(() => {
    // Hook fetch
    const originalFetch = window.fetch;
    window.fetch = async function(...args) {
        console.log('[Fetch]', args[0]);
        const response = await originalFetch.apply(this, args);
        return response;
    };

    // Hook localStorage
    const originalSetItem = localStorage.setItem;
    localStorage.setItem = function(key, value) {
        console.log('[LocalStorage]', key, '=', value);
        return originalSetItem.apply(this, arguments);
    };
});

await page.goto('https://example.com');
```

### 绕过 Webdriver 检测

```javascript
const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');

puppeteer.use(StealthPlugin());

const browser = await puppeteer.launch({
    headless: false,
    args: [
        '--disable-blink-features=AutomationControlled',
        '--disable-dev-shm-usage',
        '--no-sandbox'
    ]
});

const page = await browser.newPage();

// 隐藏 webdriver 特征
await page.evaluateOnNewDocument(() => {
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    });

    // 伪造 Chrome 插件
    Object.defineProperty(navigator, 'plugins', {
        get: () => [1, 2, 3, 4, 5]
    });
});

await page.goto('https://bot-detection.com');
```

---

## Playwright 脚本

### 基础模板

```javascript
const { chromium } = require('playwright');

(async () => {
    const browser = await chromium.launch({ headless: false });
    const context = await browser.newContext();
    const page = await context.newPage();

    await page.goto('https://example.com');
    await page.screenshot({ path: 'screenshot.png' });

    await browser.close();
})();
```

### 多浏览器测试

```javascript
const { chromium, firefox, webkit } = require('playwright');

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

testAllBrowsers('https://example.com');
```

### 移动设备模拟

```javascript
const { devices } = require('playwright');

const iPhone = devices['iPhone 12'];

const browser = await chromium.launch();
const context = await browser.newContext({
    ...iPhone,
    locale: 'zh-CN',
    geolocation: { longitude: 116.40, latitude: 39.90 },  // 北京
    permissions: ['geolocation']
});

const page = await context.newPage();
await page.goto('https://example.com');
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
                content: document.body.innerText
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
    'https://example.com/page1',
    'https://example.com/page2',
    'https://example.com/page3'
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

    await page.goto('https://example.com/login');
    await page.fill('#username', 'myuser');
    await page.fill('#password', 'mypassword');
    await page.click('#login-button');
    await page.waitForNavigation();

    // 保存存储状态（包含 Cookie、LocalStorage 等）
    await context.storageState({ path: 'state.json' });
    await browser.close();
}

// 加载登录状态
async function useLoginState() {
    const browser = await chromium.launch({ headless: false });
    const context = await browser.newContext({
        storageState: 'state.json'
    });
    const page = await context.newPage();

    // 直接访问需要登录的页面
    await page.goto('https://example.com/dashboard');

    await browser.close();
}
```

### 网络监控和 HAR 导出

```javascript
const context = await browser.newContext({
    recordHar: { path: 'network.har' }
});

const page = await context.newPage();
await page.goto('https://example.com');

// 操作页面...

await context.close();  // HAR 文件会自动保存
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
    'http://proxy1.com:8080',
    'http://proxy2.com:8080',
    'http://proxy3.com:8080'
];

async function scrapeWithProxy(url) {
    const proxy = proxies[Math.floor(Math.random() * proxies.length)];

    const browser = await chromium.launch({
        proxy: { server: proxy }
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
            await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
        }
    }
}

// 使用
await retryOperation(async () => {
    await page.goto('https://example.com');
    await page.click('#button');
});
```

---

## 完整爬虫示例

```javascript
const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const fs = require('fs');

puppeteer.use(StealthPlugin());

class WebScraper {
    constructor() {
        this.browser = null;
        this.page = null;
    }

    async init() {
        this.browser = await puppeteer.launch({
            headless: false,
            args: ['--no-sandbox']
        });
        this.page = await this.browser.newPage();
        await this.page.setViewport({ width: 1920, height: 1080 });
    }

    async login(username, password) {
        await this.page.goto('https://example.com/login');
        await this.page.type('#username', username, { delay: 100 });
        await this.page.type('#password', password, { delay: 100 });
        await this.page.click('#login-button');
        await this.page.waitForNavigation();
    }

    async scrapeData(url) {
        await this.page.goto(url);

        const data = await this.page.evaluate(() => {
            const items = [];
            document.querySelectorAll('.item').forEach(item => {
                items.push({
                    title: item.querySelector('.title')?.innerText,
                    price: item.querySelector('.price')?.innerText,
                    link: item.querySelector('a')?.href
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
    await scraper.login('myuser', 'mypassword');

    const data = await scraper.scrapeData('https://example.com/products');
    fs.writeFileSync('data.json', JSON.stringify(data, null, 2));

    await scraper.close();
})();
```

---

## 相关章节

- [Puppeteer 与 Playwright](../01-Tooling/puppeteer_playwright.md)
- [Selenium WebDriver](../01-Tooling/selenium_webdriver.md)
- [分布式爬虫架构](../04-Engineering/distributed_scraping.md)
"""

# === 03-Advanced-Topics 模块 ===
ALL_TODO_DOCS["03-Advanced-Topics/anti_scraping_deep_dive.md"] = """# 反爬虫技术深度分析

## 概述

现代网站采用多层次、多维度的反爬虫体系。本章深入分析主流反爬虫技术的原理、检测方法及对抗策略。

---

## 反爬虫技术分类

### 1. 基于行为的检测

**特征**:
- 请求频率异常（短时间大量请求）
- 访问模式异常（只访问 API，不访问静态资源）
- 用户行为缺失（无鼠标移动、键盘事件）

**检测方法**:
```python
# 服务端检测逻辑示例
def is_bot_behavior(request_log):
    # 1. 检查请求频率
    if request_log.count_in_last_minute() > 100:
        return True

    # 2. 检查 User-Agent
    if not request_log.has_valid_user_agent():
        return True

    # 3. 检查 Referer 链
    if not request_log.has_valid_referer_chain():
        return True

    return False
```

**对抗策略**:
- 添加随机延迟：`time.sleep(random.uniform(1, 3))`
- 模拟完整的浏览行为：访问首页 -> 列表页 -> 详情页
- 加载静态资源（CSS/JS/图片）

---

### 2. 基于 JavaScript 的检测

#### 检测 webdriver

**检测代码**:
```javascript
if (navigator.webdriver) {
    console.log('Bot detected!');
}

// 检测 Selenium 特征
if (window.document.documentElement.getAttribute('webdriver')) {
    console.log('Selenium detected!');
}

// 检测 PhantomJS
if (window.callPhantom || window._phantom) {
    console.log('PhantomJS detected!');
}
```

**绕过方法**:
```javascript
// Puppeteer
await page.evaluateOnNewDocument(() => {
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    });

    delete navigator.__proto__.webdriver;
});

// Selenium
options.add_argument('--disable-blink-features=AutomationControlled')
driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
    'source': '''
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        })
    '''
})
```

#### 检测 Chrome Headless

**检测代码**:
```javascript
// 检测 User-Agent
if (/HeadlessChrome/.test(navigator.userAgent)) {
    console.log('Headless detected!');
}

// 检测插件数量
if (navigator.plugins.length === 0) {
    console.log('Headless detected!');
}

// 检测 Chrome 对象
if (!window.chrome || !window.chrome.runtime) {
    console.log('Not real Chrome!');
}
```

**绕过方法**:
```javascript
// 伪造 User-Agent
await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...');

// 伪造 Chrome 对象
await page.evaluateOnNewDocument(() => {
    window.chrome = {
        runtime: {}
    };
});

// 伪造插件
await page.evaluateOnNewDocument(() => {
    Object.defineProperty(navigator, 'plugins', {
        get: () => [1, 2, 3, 4, 5]
    });
});
```

---

### 3. 基于 TLS 指纹的检测

**原理**: 客户端在 TLS 握手时发送的 Client Hello 包含大量指纹信息（JA3）。

**检测代码** (服务端):
```python
from scapy.all import *

def extract_ja3(packet):
    # 提取 TLS Client Hello
    # 生成 JA3 指纹
    ja3 = f"{version},{ciphers},{extensions},{curves},{formats}"
    ja3_hash = hashlib.md5(ja3.encode()).hexdigest()

    # 检查是否在黑名单中
    if ja3_hash in BLACKLIST_JA3:
        return "Bot detected"
```

**对抗策略**:
- 使用 `curl-impersonate` 模拟真实浏览器 TLS 指纹
- 使用真实浏览器（Puppeteer/Playwright）
- 详见 [TLS 指纹识别](./tls_fingerprinting.md)

---

### 4. 基于 Canvas/WebGL 指纹

**检测代码**:
```javascript
function getCanvasFingerprint() {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    ctx.textBaseline = 'top';
    ctx.font = '14px Arial';
    ctx.fillText('fingerprint', 2, 2);
    return canvas.toDataURL();
}

const fingerprint = getCanvasFingerprint();
// 发送到服务器验证
```

**对抗策略**: 详见 [Canvas 指纹技术](./canvas_fingerprinting.md)

---

### 5. 蜜罐技术 (Honeypot)

**原理**: 在页面中隐藏对用户不可见、但爬虫会抓取的链接。

**实现**:
```html
<!-- 隐藏链接 -->
<a href="/trap" style="display:none;">Hidden Link</a>

<!-- CSS 隐藏 -->
<style>
.trap { position: absolute; left: -9999px; }
</style>
<a href="/trap" class="trap">Trap</a>
```

**服务端处理**:
```python
@app.route('/trap')
def honeypot():
    # 记录访问者 IP，标记为爬虫
    blacklist.add(request.remote_addr)
    return "Gotcha!"
```

**对抗策略**:
- 只提取可见内容
- 检查元素的 CSS 样式（`display`, `visibility`, `opacity`）
```javascript
function isVisible(element) {
    return element.offsetWidth > 0 &&
           element.offsetHeight > 0 &&
           getComputedStyle(element).visibility !== 'hidden';
}
```

---

## 相关章节

- [浏览器指纹识别](../02-Techniques/browser_fingerprinting.md)
- [TLS 指纹识别](./tls_fingerprinting.md)
- [Canvas 指纹技术](./canvas_fingerprinting.md)
- [代理池管理](../04-Engineering/proxy_pool_management.md)
"""

ALL_TODO_DOCS["03-Advanced-Topics/frontend_hardening.md"] = """# 前端加固技术

## 概述

前端加固是保护 Web 应用代码和逻辑不被轻易分析的技术。本章介绍主流的前端加固手段及其原理。

---

## 代码混淆

### 1. 变量名混淆

**原理**: 将有意义的变量名替换为无意义的短字符。

**工具**: JavaScript Obfuscator

### 2. 字符串加密

**原理**: 将字符串加密存储，运行时解密。

### 3. 控制流平坦化

**原理**: 打乱代码执行顺序，使用 switch-case 结构。

---

## JavaScript 虚拟机保护

**原理**: 将 JavaScript 代码编译为自定义字节码，运行时由虚拟机解释执行。

详见 [JavaScript 虚拟机保护](./javascript_vm_protection.md)

---

## WebAssembly 编译

**原理**: 将核心逻辑编译为 WebAssembly，提升性能和保护强度。

详见 [WebAssembly 逆向](./webassembly_reversing.md)

---

## 相关章节

- [JavaScript 虚拟机保护](./javascript_vm_protection.md)
- [WebAssembly 逆向](./webassembly_reversing.md)
- [JavaScript 反混淆](../02-Techniques/javascript_deobfuscation.md)
"""

ALL_TODO_DOCS["03-Advanced-Topics/http2_http3.md"] = """# HTTP/2 与 HTTP/3

## 概述

HTTP/2 和 HTTP/3 是 HTTP 协议的最新版本，带来了性能提升和新的特性。在逆向工程中，理解这些协议的工作原理对于分析现代 Web 应用至关重要。

---

## HTTP/2

### 核心特性

#### 1. 二进制分帧

**HTTP/1.x**: 基于文本

**HTTP/2**: 基于二进制帧

**影响**:
- 无法直接用文本工具查看
- 需要专用工具解析（Wireshark, Chrome DevTools）

#### 2. 多路复用 (Multiplexing)

**原理**: 单个 TCP 连接上并发多个 HTTP 请求/响应。

**逆向影响**:
- Network 面板中请求顺序与实际发送顺序可能不同
- 无法通过请求顺序判断逻辑流程

#### 3. 头部压缩 (HPACK)

**原理**: 使用 Huffman 编码和索引表压缩头部。

---

## HTTP/3

### 核心特性

#### 1. 基于 QUIC 协议

**优势**:
- 更快的连接建立（0-RTT）
- 更好的移动网络性能
- 连接迁移（IP 地址变化时保持连接）

#### 2. 消除队头阻塞

**HTTP/3 的解决**: QUIC 独立流

---

## 相关章节

- [HTTP/HTTPS 协议](../00-Foundations/http_https_protocol.md)
- [TLS/SSL 握手过程](../00-Foundations/tls_ssl_handshake.md)
- [TLS 指纹识别](./tls_fingerprinting.md)
"""

ALL_TODO_DOCS["02-Techniques/debugging_techniques.md"] = """# 调试技巧与断点设置

## 概述

调试是逆向工程的核心技能。掌握高级调试技巧可以大幅提升逆向效率，快速定位关键代码，理解程序逻辑。

---

## 断点类型

### 1. 行断点 (Line Breakpoint)

最基本的断点类型，点击行号即可设置。

**快捷键**:
- 设置/取消断点: 点击行号
- 禁用所有断点: `Ctrl+F8` (Windows) / `Cmd+F8` (Mac)

**技巧**:
- 在函数入口设置断点
- 在可疑的加密、签名函数处设置

### 2. 条件断点 (Conditional Breakpoint)

只有满足特定条件时才触发的断点。

**设置方法**:
1. 右键行号
2. 选择 "Add conditional breakpoint"
3. 输入条件表达式

**示例**:
```javascript
// 只有当 user_id 为 12345 时才断点
user_id === 12345

// 只有当参数包含 'admin' 时才断点
params.username.includes('admin')

// 循环中每 100 次才断点
i % 100 === 0
```

**使用场景**:
- 大量循环中定位特定数据
- 多次调用的函数中定位特定参数

### 3. 日志点 (Logpoint)

不暂停执行，只输出日志。

**设置方法**:
1. 右键行号
2. 选择 "Add logpoint"
3. 输入要输出的表达式

**示例**:
```javascript
// 输出变量值
'User ID:', user_id

// 输出对象
'Params:', params

// 输出函数返回值
'Result:', calculateSign(params)
```

**优势**:
- 不影响代码执行流程
- 适合追踪变量变化
- 比插入 console.log 更方便

### 4. DOM 断点 (DOM Breakpoint)

监控 DOM 变化。

**类型**:
- **Subtree modifications**: 子节点变化
- **Attribute modifications**: 属性变化
- **Node removal**: 节点移除

**使用场景**:
- 追踪动态生成的验证码图片
- 追踪价格数据的动态更新
- 追踪表单的自动填充

**设置方法**:
1. Elements 面板选中元素
2. 右键 -> Break on
3. 选择断点类型

### 5. XHR/Fetch 断点

在网络请求发送时触发断点。

**设置方法**:
1. Sources 面板
2. 右侧 "XHR/fetch Breakpoints"
3. 输入 URL 关键词

**示例**:
```
/api/login
/api/user/info
sign
token
```

**使用场景**:
- 快速定位 API 调用代码
- 追踪请求参数生成逻辑

### 6. 事件断点 (Event Listener Breakpoint)

在特定事件触发时断点。

**常用事件**:
- Mouse -> click
- Mouse -> mousedown/mouseup
- Keyboard -> keydown/keyup
- Form -> submit
- Timer -> setTimeout/setInterval

**使用场景**:
- 不知道点击事件绑定在哪里
- 追踪表单提交逻辑
- 追踪定时器中的反调试代码

---

## 单步执行

### 快捷键

| 操作 | Windows/Linux | Mac | 说明 |
|------|---------------|-----|------|
| **Step Over** | `F10` | `F10` | 跳过函数，执行下一行 |
| **Step Into** | `F11` | `F11` | 进入函数内部 |
| **Step Out** | `Shift+F11` | `Shift+F11` | 跳出当前函数 |
| **Continue** | `F8` | `F8` | 继续执行到下一个断点 |
| **Resume** | `F8` | `F8` | 恢复脚本执行 |

### 使用技巧

**Step Over vs Step Into**:
- 如果下一行是库函数（如 `JSON.stringify`），用 **Step Over**
- 如果下一行是业务函数（如 `generateSign`），用 **Step Into**

**Step Out**:
- 进错函数了？用 **Step Out** 快速返回

**Continue**:
- 循环中不想一步步执行？在循环后设置断点，用 **Continue** 跳过

---

## 调用栈分析 (Call Stack)

### 查看调用栈

断点停下后，右侧 Call Stack 面板显示函数调用链：

```
generateRequest (main.js:123)
  |- getData (utils.js:45)
       |- onClick (app.js:789)
            |- <anonymous>
```

### 使用技巧

1. **从下往上看**: 最下面是事件入口，最上面是当前位置
2. **点击跳转**: 点击任意一层可以查看该层的代码和变量
3. **过滤库文件**: 右键 -> Blackbox script，隐藏第三方库

---

## Scope 变量查看

### 作用域类型

- **Local**: 当前函数的局部变量
- **Closure**: 闭包变量
- **Global**: 全局变量

### 技巧

**查看复杂对象**:
- 右键 -> Store as global variable
- 在 Console 中操作该变量（会自动命名为 `temp1`, `temp2`...）

**修改变量**:
- 双击变量值可以直接修改
- 用于测试不同参数的影响

---

## Console 调试技巧

### 条件输出

```javascript
// 只有当条件满足时才输出
if (user_id === 12345) {
    console.log('Target user:', user_id);
}
```

### 分组输出

```javascript
console.group('User Info');
console.log('ID:', user_id);
console.log('Name:', username);
console.groupEnd();
```

### 表格输出

```javascript
const users = [
    {id: 1, name: 'Alice'},
    {id: 2, name: 'Bob'}
];
console.table(users);
```

### 性能测量

```javascript
console.time('encrypt');
// ... 加密代码
console.timeEnd('encrypt');  // encrypt: 12.345ms
```

### 堆栈追踪

```javascript
console.trace('Where am I?');
```

---

## 高级调试技巧

### 1. Blackbox 第三方库

避免调试时进入 jQuery、React 等第三方库：

**方法一**:
1. Settings -> Blackboxing
2. 添加模式：`/node_modules/`, `/jquery.*.js`

**方法二**:
- 在 Call Stack 中右键 -> Blackbox script

### 2. 异步代码调试

**问题**: 异步代码断点后，Call Stack 断裂。

**解决**: 勾选 "Async" 按钮（Call Stack 上方），显示完整异步调用栈。

### 3. Source Map

**问题**: 生产环境代码被压缩/混淆，无法调试。

**解决**: 如果有 Source Map 文件（`.map`），DevTools 会自动加载原始代码。

### 4. Local Overrides (本地替换)

**用途**: 修改线上 JS 文件并保存，刷新后依然生效。

**步骤**:
1. Sources -> Overrides
2. 选择本地文件夹
3. 修改文件并保存 (`Ctrl+S`)

**应用**:
- 删除反调试代码
- 添加日志输出
- 修改加密逻辑测试

### 5. Snippets (代码片段)

**用途**: 保存常用的 Hook 脚本，快速执行。

**步骤**:
1. Sources -> Snippets
2. 新建 Snippet
3. 粘贴脚本，`Ctrl+Enter` 执行

---

## 反调试对抗

### 1. 无限 debugger

**特征**:
```javascript
setInterval(() => {
    debugger;
}, 100);
```

**绕过方法**:
- **方法一**: 右键断点行 -> "Never pause here"
- **方法二**: Hook `Function.prototype.constructor` (见 [Hook 脚本](../06-Scripts/javascript_hook_scripts.md))
- **方法三**: Local Overrides 删除该段代码

### 2. 检测 DevTools 打开

**特征**:
```javascript
setInterval(() => {
    if (window.outerWidth - window.innerWidth > 160) {
        alert('DevTools detected!');
        window.location.href = 'about:blank';
    }
}, 1000);
```

**绕过方法**:
- 使用独立窗口模式（Undock into separate window）
- Hook `window.outerWidth` 和 `window.innerWidth`

### 3. 检测时间差

**特征**:
```javascript
let start = Date.now();
debugger;
let end = Date.now();
if (end - start > 100) {
    console.log('Debugger detected!');
}
```

**绕过方法**:
- Hook `Date.now()` 返回固定增量

---

## 实战示例

### 示例一：追踪加密函数

**目标**: 找到生成 `sign` 参数的函数

**步骤**:
1. Network 面板找到包含 `sign` 的请求
2. 全局搜索 `sign`（可能有上百个结果）
3. 设置 XHR 断点，URL 填 `/api/`
4. 刷新页面，断点停下
5. 查看 Call Stack，定位到 `generateSign` 函数
6. 单步调试，理解加密逻辑

### 示例二：绕过滑块验证码

**目标**: 分析滑块验证逻辑

**步骤**:
1. 右键滑块元素 -> Break on -> Attribute modifications
2. 拖动滑块，断点停下
3. 查看 Call Stack，找到验证函数
4. 分析轨迹生成和验证逻辑

---

## 相关章节

- [JavaScript Hook 脚本](../06-Scripts/javascript_hook_scripts.md)
- [浏览器开发者工具](../01-Tooling/browser_devtools.md)
- [逆向工程工作流](./re_workflow.md)
"""

# 批量写入函数
def fill_all_todo_documents():
    base_dir = Path(__file__).parent / "docs"

    for file_path, content in ALL_TODO_DOCS.items():
        full_path = base_dir / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"✅ 填充: {file_path}")

    print(f"\n🎉 成功填充 {len(ALL_TODO_DOCS)} 个文档!")
    print(f"\n📊 进度更新:")
    print(f"  - 本次填充: {len(ALL_TODO_DOCS)} 个")
    print(f"  - 累计完成: 约 75%")
    print(f"\n📝 本次填充的文档:")
    print(f"  - 02-Techniques: 2 个（浏览器指纹识别、调试技巧）")
    print(f"  - 03-Advanced-Topics: 3 个（反爬虫深度分析、前端加固、HTTP/2&3）")
    print(f"  - 06-Scripts: 2 个（反混淆脚本、自动化脚本）")

if __name__ == "__main__":
    fill_all_todo_documents()
