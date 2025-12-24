---
title: "反爬虫技术深度分析"
date: 2025-12-25
weight: 10
---

# 反爬虫技术深度分析

## 概述

现代网站采用多层次、多维度的反爬虫体系。本章深入分析主流反爬虫技术的原理、检测方法及对抗策略。

---

## 📚 前置知识

在开始本配方之前，建议先掌握以下内容：

| 知识领域 | 重要程度 | 参考资料 |
|----------|---------|---------|
| 浏览器指纹识别 | 必需 | [浏览器指纹识别](./browser_fingerprinting.md) |
| HTTP/HTTPS 协议 | 必需 | [HTTP/HTTPS 协议](../01-Foundations/http_https_protocol.md) |
| Hook 技术 | 必需 | [Hook 技术](../03-Basic-Recipes/hooking_techniques.md) |
| TLS 指纹 | 推荐 | [TLS 指纹识别](./tls_fingerprinting.md) |
| 浏览器自动化 | 推荐 | [Puppeteer/Playwright](../02-Tooling/puppeteer_playwright.md) |

> 💡 **提示**: 反爬虫对抗是一场**持续的攻防战**。本配方整合了指纹、行为、协议等多维度的检测与绕过技术，是逆向工程的综合应用。

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
console.log("Bot detected!");
}

// 检测 Selenium 特征
if (window.document.documentElement.getAttribute("webdriver")) {
console.log("Selenium detected!");
}

// 检测 PhantomJS
if (window.callPhantom || window._phantom) {
console.log("PhantomJS detected!");
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
console.log("Headless detected!");
}

// 检测插件数量
if (navigator.plugins.length === 0) {
console.log("Headless detected!");
}

// 检测 Chrome 对象
if (!window.chrome || !window.chrome.runtime) {
console.log("Not real Chrome!");
}
```

**绕过方法**:

```javascript
// 伪造 User-Agent
await page.setUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...");

// 伪造 Chrome 对象
await page.evaluateOnNewDocument(() => {
window.chrome = {
runtime: {},
};
});

// 伪造插件
await page.evaluateOnNewDocument(() => {
Object.defineProperty(navigator, "plugins", {
get: () => [1, 2, 3, 4, 5],
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
const canvas = document.createElement("canvas");
const ctx = canvas.getContext("2d");
ctx.textBaseline = "top";
ctx.font = "14px Arial";
ctx.fillText("fingerprint", 2, 2);
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
.trap {
position: absolute;
left: -9999px;
}
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
return (
element.offsetWidth > 0 &&
element.offsetHeight > 0 &&
getComputedStyle(element).visibility !== "hidden"
);
}
```

---

### 6. CSS 反爬技术

#### 6.1 CSS 偏移隐藏

**原理**: 使用 CSS 样式将真实内容偏移到不可见区域，页面上显示的是伪造数据。

**实现示例**:

```html
<style>
.price {
position: relative;
}
.price .real {
position: absolute;
left: -9999px;
}
.price .fake {
position: relative;
}
</style>

<div class="price">
<span class="real">¥199</span>
<span class="fake">¥9999</span>
</div>
```

**特点**:

- 页面源码中显示假数据
- 真实数据通过 CSS 定位隐藏
- 正常用户看到的是真实数据

**对抗策略**:

```python
from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get('https://example.com')

# 获取元素
element = driver.find_element(By.CLASS_NAME, 'price')

# 获取渲染后的可见文本（会获取到真实数据）
visible_text = element.text

# 或使用 JavaScript 获取计算后的样式
script = """
var element = arguments[0];
var style = window.getComputedStyle(element);
if (style.display !== 'none' &&
style.visibility !== 'hidden' &&
style.opacity !== '0' &&
parseInt(style.left) > -1000) {
return element.innerText;
}
return null;
```

#### 6.2 字体反爬技术

**原理**: 通过自定义字体文件（@font-face），将页面文本字符映射到字体文件中的不同字形，使得爬虫抓取到的文字与实际显示的文字不一致。

**典型案例**: 猫眼电影、大众点评、58 同城、汽车之家、天眼查、起点中文网

**实现机制**:

```html
<!-- HTML 中显示的是乱码或特殊编码 -->
<span class="rating">&#xe601;&#xe602;&#xe603;</span>

<!-- CSS 引入自定义字体 -->
<style>
@font-face {
font-family: "CustomFont";
src: url("/fonts/custom_12345.woff") format("woff");
}
.rating {
font-family: "CustomFont";
}
</style>
```

**字体文件结构**:

```
WOFF 字体文件
├── cmap 表 (字符映射表)
│ ├── &#xe601; → "8"
│ ├── &#xe602; → "."
│ └── &#xe603; → "5"
├── glyf 表 (字形轮廓)
│ ├── glyph_001 (数字 8 的轮廓)
│ ├── glyph_002 (点号的轮廓)
│ └── glyph_003 (数字 5 的轮廓)
```

**破解方法**:

**方法 1: 字体文件解析**

```python
from fontTools.ttLib import TTFont
import requests
import re

# 1. 从页面提取字体文件 URL
def extract_font_url(html):
pattern = r'url\(["\']?(/fonts/[^"\']+\.woff[^"\']*)["\']?\)'
match = re.search(pattern, html)
return match.group(1) if match else None

# 2. 下载字体文件
font_url = 'https://example.com/fonts/custom.woff'
response = requests.get(font_url)
with open('custom.woff', 'wb') as f:
f.write(response.content)

# 3. 解析字体文件
font = TTFont('custom.woff')

# 4. 提取字符映射
cmap = font.getBestCmap() # 获取最佳字符映射表

# 5. 提取字形坐标
def get_glyph_outline(font, glyph_name):
"""获取字形轮廓坐标"""
glyf_table = font['glyf']
glyph = glyf_table[glyph_name]
if glyph.isComposite():
return None # 跳过复合字形
coordinates = []
if hasattr(glyph, 'coordinates'):
for x, y in glyph.coordinates:
coordinates.append((x, y))
return coordinates

# 6. 建立字形与真实字符的映射
font_map = {}
for unicode_val, glyph_name in cmap.items():
outline = get_glyph_outline(font, glyph_name)
# 通过比对坐标识别真实字符
# 这里需要预先建立标准字形库
real_char = recognize_char_by_outline(outline)
font_map[chr(unicode_val)] = real_char

print(font_map)
# {'\ue601': '8', '\ue602': '.', '\ue603': '5'}

# 7. 解密文本
def decrypt_text(encrypted_text, font_map):
decrypted = ''
for char in encrypted_text:
decrypted += font_map.get(char, char)
return decrypted

encrypted = '&#xe601;&#xe602;&#xe603;' # HTML 实体
decrypted = decrypt_text(encrypted, font_map)
print(decrypted) # "8.5"
```

**方法 2: OCR 识别（针对动态字体）**

```python
from selenium import webdriver
from PIL import Image
import pytesseract
from io import BytesIO

def ocr_screenshot(url, selector):
"""截图并 OCR 识别"""
driver = webdriver.Chrome()
driver.get(url)

# 定位元素
element = driver.find_element(By.CSS_SELECTOR, selector)

# 截取元素截图
screenshot = element.screenshot_as_png
image = Image.open(BytesIO(screenshot))

# OCR 识别
text = pytesseract.image_to_string(image, lang='chi_sim+eng')

driver.quit()
return text.strip()
```

**方法 3: 字形相似度匹配**

```python
import numpy as np
from fontTools.pens.recordingPen import RecordingPen

def calculate_similarity(outline1, outline2):
"""计算两个字形轮廓的相似度"""
# 将坐标序列转换为向量
vec1 = np.array(outline1).flatten()
vec2 = np.array(outline2).flatten()

# 归一化
vec1 = vec1 / np.linalg.norm(vec1)
vec2 = vec2 / np.linalg.norm(vec2)

# 计算余弦相似度
similarity = np.dot(vec1, vec2)
return similarity

# 建立标准字形库（需提前准备）
standard_glyphs = {
'0': [(10, 20), (30, 20), ...],
'1': [(15, 5), (15, 35), ...],
# ... 其他字符
}

def recognize_char_by_outline(outline):
"""通过轮廓识别字符"""
max_similarity = 0
recognized_char = ''

for char, std_outline in standard_glyphs.items():
similarity = calculate_similarity(outline, std_outline)
if similarity > max_similarity:
max_similarity = similarity
recognized_char = char

return recognized_char if max_similarity > 0.8 else '?'
```

**进阶对抗: 动态字体反爬**

某些网站（如大众点评）使用**动态字体**，每次访问字体文件的映射关系都不同：

```python
# 访问 1：&#xe601; → "8"
# 访问 2：&#xe601; → "3" （映射关系改变）
```

**破解方法**:

- **实时解析**: 每次请求都重新下载字体文件并解析
- **机器学习**: 训练 CNN 模型识别字形
- **OCR 方案**: 使用 Selenium 渲染后截图 OCR

**参考案例分析**: 大众点评评分字体破解

```python
import requests
from fontTools.ttLib import TTFont
import re

class DianpingFontCracker:
def __init__(self):
self.base_font = None # 基准字体（固定映射）
self.current_font = None # 当前页面字体

def download_font(self, url):
"""下载字体文件"""
response = requests.get(url)
with open('temp.woff', 'wb') as f:
f.write(response.content)
return TTFont('temp.woff')

def extract_font_url(self, html):
"""从 HTML 中提取字体 URL"""
pattern = r'url\("(.*?\.woff)"\)'
match = re.search(pattern, html)
return match.group(1) if match else None

def build_mapping(self, font, base_font):
"""通过对比基准字体建立映射"""
mapping = {}

for code in font.getBestCmap():
glyph_name = font.getBestCmap()[code]
outline = self.get_outline(font, glyph_name)

# 与基准字体对比
for base_code, base_glyph in base_font.getBestCmap().items():
base_outline = self.get_outline(base_font, base_glyph)

if self.is_similar(outline, base_outline):
# 基准字体的字符是已知的
real_char = chr(base_code)
mapping[chr(code)] = real_char
break

return mapping

def get_outline(self, font, glyph_name):
"""获取字形轮廓"""
glyf = font['glyf'][glyph_name]
if hasattr(glyf, 'coordinates'):
return list(glyf.coordinates)
return []

def is_similar(self, outline1, outline2, threshold=0.9):
"""判断两个轮廓是否相似"""
if len(outline1) != len(outline2):
return False
return calculate_similarity(outline1, outline2) > threshold

def decrypt(self, html_content):
"""解密页面内容"""
# 1. 提取字体 URL
font_url = self.extract_font_url(html_content)

# 2. 下载字体
current_font = self.download_font(font_url)

# 3. 建立映射
mapping = self.build_mapping(current_font, self.base_font)

# 4. 替换加密文本
decrypted_html = html_content
for enc_char, real_char in mapping.items():
decrypted_html = decrypted_html.replace(enc_char, real_char)

return decrypted_html
```

**资源**:

- [今天，我终于弄懂了字体反爬是个啥玩意！](https://cuiqingcai.com/6431.html)
- [终于解决大众点评的字体反爬了！](https://blog.csdn.net/m0_49077792/article/details/111369149)
- [Python 爬虫六：字体反爬处理（猫眼+汽车之家）](https://blog.csdn.net/xing851483876/article/details/82928607)

---

### 7. JavaScript 反调试技术

#### 7.1 无限 Debugger 循环

**原理**: 使用 `debugger` 语句配合定时器或递归，持续暂停 JavaScript 执行。

**实现方式**:

**方式 1: 直接循环**

```javascript
setInterval(function () {
debugger;
}, 100);
```

**方式 2: 自执行函数**

```javascript
(function () {
function detect() {
debugger;
detect();
}
detect();
})();
```

**方式 3: eval/Function 动态执行**

```javascript
setInterval(function () {
(function () {
return false;
})
["constructor"]("debugger")
["call"]();
}, 50);

// 或使用 eval
setInterval(function () {
eval("debugger");
}, 50);
```

**方式 4: 时间检测**

```javascript
setInterval(function () {
var start = new Date();
debugger;
var end = new Date();

// 检测时间差，判断是否在调试
if (end - start > 100) {
console.log("Developer tools detected!");
// 清空页面或重定向
document.body.innerHTML = "";
window.location.href = "about:blank";
}
}, 1000);
```

#### 7.2 绕过反调试的方法

**方法 1: 禁用所有断点**

Chrome DevTools 操作:

1. 打开 Sources 面板
2. 点击右侧的"Deactivate breakpoints"按钮（快捷键 Ctrl+F8）
3. 所有 debugger 语句将被忽略

**方法 2: Never Pause Here (永不在此暂停)**

```
1. 在 debugger 行右键
2. 选择 "Never pause here"
3. 该行的 debugger 将被忽略
```

**方法 3: 条件断点覆盖**

```
1. 在 debugger 行设置条件断点
2. 条件设为 false
3. 断点将永不触发
```

**方法 4: Hook Function 构造器**

```javascript
// 在页面加载前注入（通过浏览器扩展或 Fiddler）
(function () {
var originalFunction = window.Function;
window.Function = function () {
var args = Array.prototype.slice.call(arguments);
var code = args[args.length - 1];

// 检测并移除 debugger
if (code && typeof code === "string" && code.includes("debugger")) {
console.log("Blocked debugger:", code);
args[args.length - 1] = code.replace(/debugger/g, "");
}

return originalFunction.apply(this, args);
};

// 处理 eval
var originalEval = window.eval;
window.eval = function (code) {
if (typeof code === "string" && code.includes("debugger")) {
console.log("Blocked eval debugger:", code);
code = code.replace(/debugger/g, "");
}
return originalEval.call(this, code);
};
})();
```

**方法 5: 本地文件替换**

使用 Fiddler/Charles 替换 JavaScript 文件:

```javascript
// 1. 保存原始 JS 文件
// 2. 移除所有 debugger 语句
// 3. 使用 Fiddler AutoResponder 替换

// Fiddler AutoResponder 规则:
// REGEX:https://example.com/js/protect.js
// 本地文件路径: C:\temp\protect_cracked.js
```

**方法 6: Chrome DevTools Protocol (CDP)**

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
chrome_options.add_experimental_option('useAutomationExtension', False)

driver = webdriver.Chrome(options=chrome_options)

# 禁用 debugger
driver.execute_cdp_cmd('Debugger.disable', {})

# 设置断点行为
driver.execute_cdp_cmd('Debugger.setBreakpointsActive', {'active': False})

driver.get('https://example.com')
```

**方法 7: 重写 debugger (Proxy)**

```javascript
// 使用 Proxy 拦截 debugger
(function () {
var handler = {
construct: function (target, args) {
var code = args[args.length - 1];
if (typeof code === "string") {
code = code.replace(/debugger/g, "");
args[args.length - 1] = code;
}
return new target(...args);
},
};

window.Function = new Proxy(Function, handler);
})();
```

**参考资源**:

- [浏览器反调试绕过无限 debugger 及代码执行器检测](https://blog.csdn.net/Revivedsun/article/details/105448505)
- [绕过 JavaScript debugger 三种解决方法](https://blog.csdn.net/wh445306/article/details/103638742)
- [JS 逆向：常见无限 Debugger 以及绕过方法](https://cloud.tencent.com/developer/article/2242577)
- [几种常见的前端反调试方法及突破方式](https://tree.moe/anti-debug-and-solution/)

#### 7.3 检测开发者工具

**检测方法 1: 窗口尺寸检测**

```javascript
function detectDevTools() {
var widthThreshold = window.outerWidth - window.innerWidth > 160;
var heightThreshold = window.outerHeight - window.innerHeight > 160;

if (widthThreshold || heightThreshold) {
console.log("DevTools detected!");
return true;
}
return false;
}

setInterval(detectDevTools, 1000);
```

**检测方法 2: console.log 时间检测**

```javascript
var devtools = { open: false };

var checkStatus = function () {
var element = new Image();
Object.defineProperty(element, "id", {
get: function () {
devtools.open = true;
},
});

console.log("%c", element);
console.clear();
};

setInterval(function () {
devtools.open = false;
checkStatus();

if (devtools.open) {
console.log("DevTools detected!");
// 执行反制措施
}
}, 1000);
```

**绕过方法**: 使用无头浏览器或禁用 console 输出

```javascript
// Hook console.log
console.log = function () {};
console.warn = function () {};
console.error = function () {};
```

---

### 8. 验证码技术

#### 8.1 验证码类型

现代验证码主要分为以下几类:

1. **图形验证码**: 最传统的验证码，包含扭曲文字、噪点等
2. **滑块验证码**: 拖动滑块拼合图片（如极验、网易易盾）
3. **点选验证码**: 按顺序点击特定文字或物体
4. **行为验证码**: 分析用户行为轨迹（鼠标移动、点击模式）
5. **智能验证码**: 无感验证，通过设备指纹和行为分析判断

#### 8.2 主流验证码服务商

| 服务商 | 类型 | 特点 | 破解难度 |
| ----------------------- | ---------------- | ------------------------ | -------- |
| **极验 (GeeTest)** | 滑块、点选、智能 | 行为轨迹分析、多维度风控 | ★★★★★ |
| **网易易盾** | 滑块、点选、智能 | 图像乱序、背景融合 | ★★★★★ |
| **阿里云盾** | 滑块、智能 | 风控引擎、设备指纹 | ★★★★★ |
| **腾讯天御** | 滑块、点选、智能 | 交互动态加载 | ★★★★★ |
| **点触验证码** | 滑块、点选 | 多种验证方式 | ★★★★☆ |
| **Google reCAPTCHA v3** | 智能 | 无感验证、风险评分 | ★★★★☆ |

#### 8.3 滑块验证码原理与破解

**极验滑块验证码工作流程**:

```
1. 用户访问页面
2. 加载验证码组件
3. 显示缺口图片和滑块
4. 用户拖动滑块
5. 记录轨迹数据：
    - 鼠标移动轨迹
    - 速度变化
    - 加速度
    - 时间戳
6. 提交轨迹到服务器验证
7. 服务器分析行为特征：
    - 轨迹是否平滑
    - 速度是否自然
    - 是否符合人类行为
8. 返回验证结果
```

**破解方法**:

**方法 1: 图像识别 + 轨迹模拟**

```python
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from PIL import Image
import cv2
import numpy as np
import time
import random

class SliderCracker:
def __init__(self, driver):
self.driver = driver

def get_gap_distance(self, bg_img, slide_img):
"""计算缺口距离"""
# 1. 转换为灰度图
bg_gray = cv2.cvtColor(np.array(bg_img), cv2.COLOR_RGB2GRAY)
slide_gray = cv2.cvtColor(np.array(slide_img), cv2.COLOR_RGB2GRAY)

# 2. 边缘检测
bg_edges = cv2.Canny(bg_gray, 100, 200)

# 3. 模板匹配
result = cv2.matchTemplate(bg_edges, slide_gray, cv2.TM_CCOEFF_NORMED)
min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

# 4. 返回匹配位置（缺口距离）
return max_loc[0]

def get_track(self, distance):
"""生成拖动轨迹（模拟人类行为）"""
track = []
current = 0
mid = distance * 4 / 5 # 减速点
t = 0.2 # 时间间隔
v = 0 # 初速度

while current < distance:
if current < mid:
a = 2 # 加速度
else:
a = -3 # 减速

v0 = v
v = v0 + a * t
move = v0 * t + 1/2 * a * t * t
current += move

track.append(round(move))

return track

def move_slider(self, slider, track):
"""移动滑块"""
ActionChains(self.driver).click_and_hold(slider).perform()

for x in track:
ActionChains(self.driver).move_by_offset(xoffset=x, yoffset=0).perform()
time.sleep(random.uniform(0.001, 0.002))

# 随机抖动（模拟人类修正）
for _ in range(3):
ActionChains(self.driver).move_by_offset(
xoffset=random.uniform(-2, 2),
yoffset=random.uniform(-2, 2)
).perform()
time.sleep(random.uniform(0.01, 0.02))

ActionChains(self.driver).release().perform()

def crack(self):
"""破解滑块验证码"""
# 1. 等待验证码加载
time.sleep(2)

# 2. 获取背景图和滑块图
bg_element = self.driver.find_element(By.CLASS_NAME, 'geetest_canvas_bg')
slide_element = self.driver.find_element(By.CLASS_NAME, 'geetest_canvas_slice')

# 3. 截图
bg_img = Image.open(BytesIO(bg_element.screenshot_as_png))
slide_img = Image.open(BytesIO(slide_element.screenshot_as_png))

# 4. 计算缺口距离
distance = self.get_gap_distance(bg_img, slide_img)

# 5. 生成轨迹
track = self.get_track(distance - 7) # 减去滑块宽度

# 6. 拖动滑块
slider = self.driver.find_element(By.CLASS_NAME, 'geetest_slider_button')
self.move_slider(slider, track)

# 7. 等待验证结果
time.sleep(2)
```

**方法 2: 深度学习识别**

```python
import tensorflow as tf
from tensorflow.keras import layers, models

class CaptchaCNN:
def __init__(self):
self.model = self.build_model()

def build_model(self):
"""构建 CNN 模型"""
model = models.Sequential([
layers.Conv2D(32, (3, 3), activation='relu', input_shape=(60, 260, 3)),
layers.MaxPooling2D((2, 2)),
layers.Conv2D(64, (3, 3), activation='relu'),
layers.MaxPooling2D((2, 2)),
layers.Conv2D(64, (3, 3), activation='relu'),
layers.Flatten(),
layers.Dense(64, activation='relu'),
layers.Dense(1, activation='linear') # 输出缺口位置
])

model.compile(
optimizer='adam',
loss='mse',
metrics=['mae']
)

return model

def train(self, X_train, y_train, epochs=50):
"""训练模型"""
self.model.fit(
X_train, y_train,
epochs=epochs,
validation_split=0.2
)

def predict_gap(self, image):
"""预测缺口位置"""
image = np.expand_dims(image, axis=0)
return self.model.predict(image)[0][0]
```

**方法 3: 打码平台**

```python
import requests

class OCRService:
def __init__(self, api_key):
self.api_key = api_key
self.api_url = 'http://api.ttshitu.com/predict'

def recognize_slider(self, bg_img_path, slide_img_path):
"""使用打码平台识别滑块验证码"""
with open(bg_img_path, 'rb') as f:
bg_img = f.read()
with open(slide_img_path, 'rb') as f:
slide_img = f.read()

data = {
'username': 'your_username',
'password': 'your_password',
'typeid': '33', # 滑块验证码类型
'image': base64.b64encode(bg_img).decode(),
'slide': base64.b64encode(slide_img).decode()
}

response = requests.post(self.api_url, json=data)
result = response.json()

return result['data']['result'] # 返回缺口距离
```

#### 8.4 点选验证码

**原理**: 用户需要按顺序点击指定的文字或图片。

**破解方法**:

```python
from paddleocr import PaddleOCR

class ClickCaptchaCracker:
def __init__(self):
self.ocr = PaddleOCR(use_angle_cls=True, lang='ch')

def recognize_text(self, image_path):
"""识别图片中的文字位置"""
result = self.ocr.ocr(image_path, cls=True)

text_positions = []
for line in result:
for word_info in line:
box = word_info[0] # 坐标
text = word_info[1][0] # 文字
confidence = word_info[1][1] # 置信度

# 计算中心点
center_x = (box[0][0] + box[2][0]) / 2
center_y = (box[0][1] + box[2][1]) / 2

text_positions.append({
'text': text,
'x': center_x,
'y': center_y,
'confidence': confidence
})

return text_positions

def click_sequence(self, driver, target_texts, positions):
"""按顺序点击指定文字"""
for target_text in target_texts:
for pos in positions:
if pos['text'] == target_text:
# 点击该位置
element = driver.find_element(By.CLASS_NAME, 'captcha-image')
ActionChains(driver).move_to_element_with_offset(
element,
pos['x'],
pos['y']
).click().perform()
time.sleep(0.5)
break
```

#### 8.5 行为验证码

**检测维度**:

1. **鼠标轨迹**: 曲线是否平滑、是否符合贝塞尔曲线
2. **速度变化**: 是否有加速度变化
3. **点击时机**: 何时开始拖动、何时释放
4. **设备指纹**: Canvas、WebGL、字体列表等
5. **环境信息**: IP、User-Agent、浏览器版本
6. **历史行为**: 该用户/IP 的历史验证记录

**对抗策略**:

```python
import numpy as np
import random

class HumanBehaviorSimulator:
@staticmethod
def bezier_curve(start, end, control_points, steps=100):
"""生成贝塞尔曲线轨迹"""
points = [start] + control_points + [end]
n = len(points) - 1
curve = []

for t in np.linspace(0, 1, steps):
point = [0, 0]
for i, p in enumerate(points):
binomial = np.math.comb(n, i) * (1 - t)**(n - i) * t**i
point[0] += binomial * p[0]
point[1] += binomial * p[1]
curve.append(point)

return curve

@staticmethod
def add_random_jitter(track, max_jitter=2):
"""添加随机抖动"""
jittered_track = []
for point in track:
jittered_track.append([
point[0] + random.uniform(-max_jitter, max_jitter),
point[1] + random.uniform(-max_jitter, max_jitter)
])
return jittered_track

@staticmethod
def simulate_drag(driver, element, distance):
"""模拟人类拖动行为"""
# 1. 生成控制点
control_points = [
[random.uniform(distance * 0.3, distance * 0.4), random.uniform(-5, 5)],
[random.uniform(distance * 0.6, distance * 0.7), random.uniform(-5, 5)]
]

# 2. 生成曲线
curve = HumanBehaviorSimulator.bezier_curve(
[0, 0], [distance, 0], control_points
)

# 3. 添加抖动
curve = HumanBehaviorSimulator.add_random_jitter(curve)

# 4. 执行拖动
ActionChains(driver).click_and_hold(element).perform()

for point in curve:
ActionChains(driver).move_by_offset(
point[0] - last_x,
point[1] - last_y
).perform()
time.sleep(random.uniform(0.001, 0.003))
last_x, last_y = point

# 5. 释放前的停顿
time.sleep(random.uniform(0.1, 0.3))
ActionChains(driver).release().perform()
```

#### 8.6 成本分析

| 验证码类型 | 破解成本（2025） | 成功率 | 说明 |
| -------------------- | ---------------- | ------ | -------------------- |
| 普通图形验证码 | ¥0.001-0.005/次 | 95%+ | OCR 识别 |
| 滑块验证码（无风控） | ¥0.01-0.05/次 | 80-90% | 图像识别 + 轨迹模拟 |
| 极验/易盾（带风控） | ¥1-5/次 | 60-80% | 深度学习 + 行为模拟 |
| 智能验证码 | ¥5-20/次 | 40-60% | 需要大量设备指纹伪造 |

**对比**: 智能带风控的验证码破解成本是普通验证码的 **100-1000 倍**。

**参考资源**:

- [2025 最新滑块验证码、图形验证码解决方案](https://blog.csdn.net/qq_44866828/article/details/148482799)
- [使用 Python + Selenium 破解滑块验证码](https://www.aneasystone.com/archives/2018/03/python-selenium-geetest-crack.html)
- [验证码哪家强？六大验证平台评测](https://www.aqniu.com/tools-tech/29545.html)
- [滑块验证码能被机器破解吗](https://www.cnblogs.com/worktile/articles/18958534)

---

## 相关章节

- [浏览器指纹识别](../04-Advanced-Recipes/browser_fingerprinting.md)
- [TLS 指纹识别](./tls_fingerprinting.md)
- [Canvas 指纹技术](./canvas_fingerprinting.md)
- [代理池管理](../06-Engineering/proxy_pool_management.md)
- [JavaScript Hook 技术](../07-Scripts/javascript_hook_scripts.md)
