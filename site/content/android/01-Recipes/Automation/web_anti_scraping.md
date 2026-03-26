---
title: "Web 反爬虫技术"
date: 2025-01-03
type: posts
tags: ["浏览器指纹", "Canvas指纹", "Frida", "代理池", "自动化", "Android"]
weight: 10
---

# Web 反爬虫技术

> **📚 前置知识**
>
> 本配方涉及以下核心技术，建议先阅读相关章节：
>
> - **[TLS 指纹技术](../Network/tls_fingerprinting_guide.md)** - 理解 JA3/JA4 指纹检测
> - **[验证码绕过技术](../Anti-Detection/captcha_bypassing_techniques.md)** - 滑块与点选验证码

网络爬虫是自动从网站提取数据的过程。由于这可能被滥用，许多现代网站和服务实施了复杂的反爬虫（或"反机器人"）技术来保护其数据。这些技术可大致分为客户端（浏览器）和服务器端防御。

---

## 1. 反爬虫技术全景

现代反爬虫体系是一个多层次、纵深防御的架构。理解其全貌有助于制定针对性的绕过策略。

### 三层防御模型

| 层次 | 防御类型 | 典型技术 | 难度 |
| ---- | -------- | -------- | ---- |
| **客户端层** | 浏览器环境检测 | JS 挑战、Canvas/WebGL 指纹、CAPTCHA、行为分析 | ★★★★ |
| **服务器端层** | 请求特征分析 | UA 检测、Header 校验、Cookie/Token 验证、速率限制 | ★★★ |
| **网络层** | 流量与连接分析 | TLS 指纹、IP 信誉、HTTP/2 指纹、TCP 指纹 | ★★★★★ |

### 技术分类总览

```
反爬虫技术
├── 被动检测（静默收集信息）
│   ├── 浏览器指纹采集 / 行为轨迹记录 / TLS·HTTP 协议指纹
├── 主动挑战（要求客户端完成任务）
│   ├── JavaScript 计算挑战 / CAPTCHA 验证码 / Proof-of-Work
└── 响应策略（检测异常后处理）
    ├── 直接封禁（403/429）/ 静默降级（返回假数据）
    └── 蜜罐诱捕 / 延迟响应
```

> **关键认识**: 现代反爬系统（CloudFlare、Akamai 等）同时部署多层技术并综合评分，而非依赖单一检测手段。绕过时也需要多维度同时处理。

---

## 2. UA/Header 检测与绕过

HTTP 请求头是服务器端最基础的检测手段。第一道防线就是检查请求头是否"看起来像"真实浏览器。

### 常见检测点

| 检测项 | 说明 | 风险等级 |
| ------ | ---- | -------- |
| `User-Agent` | 是否为已知爬虫标识（如 `python-requests/2.28`） | 高 |
| `Accept-Language` | 缺失或不合理的语言设置 | 中 |
| `Sec-Ch-Ua` | Chrome Client Hints，缺失暴露非浏览器环境 | 高 |
| `Referer` | 直接访问内页而无来源页 | 中 |
| **Header 顺序** | 不同浏览器的 Header 排列顺序不同 | 高 |

### 伪装真实浏览器请求

```python
import requests

headers = {
    "sec-ch-ua": '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-Mode": "navigate",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}
resp = requests.get("https://example.com", headers=headers)
```

对于 Header 顺序和 TLS 指纹检测，可使用 `curl_cffi` 精确模拟：

```python
from curl_cffi import requests as cffi_requests
resp = cffi_requests.get("https://example.com", impersonate="chrome123")
```

---

## 3. IP 限流与封禁

### 常见限流策略

| 策略 | 实现方式 | 特点 |
| ---- | -------- | ---- |
| **固定窗口** | 每分钟 N 次请求 | 简单但有边界突发问题 |
| **滑动窗口** | 动态计算近 N 秒请求数 | 更精确 |
| **令牌桶** | 固定速率生成令牌 | 允许短暂突发 |
| **IP 信誉评分** | 综合行为历史打分 | 最难绕过 |

### IP 类型与被封概率

| IP 类型 | 被封概率 | 成本 | 说明 |
| -------- | -------- | ---- | ---- |
| 数据中心 IP | 极高 | 低 | AWS/GCP 等 IP 段已被广泛标记 |
| 住宅代理 IP | 低 | 高 | 真实 ISP 分配的家庭宽带 IP |
| 移动网络 IP | 极低 | 中 | 运营商基站 IP，共享用户多 |

### 代理池轮转

```python
import random, time, requests

class ProxyRotator:
    def __init__(self, proxies: list[str]):
        self.proxies = proxies
        self.failed = {}

    def get_proxy(self) -> dict:
        available = [p for p in self.proxies if self.failed.get(p, 0) < 3]
        proxy = random.choice(available)
        return {"http": f"http://{proxy}", "https": f"http://{proxy}"}

    def mark_failed(self, proxy: str):
        self.failed[proxy] = self.failed.get(proxy, 0) + 1

rotator = ProxyRotator(["1.2.3.4:8080", "5.6.7.8:3128"])
for url in target_urls:
    proxy = rotator.get_proxy()
    try:
        resp = requests.get(url, proxies=proxy, timeout=10)
    except Exception:
        rotator.mark_failed(list(proxy.values())[0])
    time.sleep(random.uniform(1.5, 4.0))  # 随机延迟
```

---

## 4. 验证码类型与绕过

### 主流验证码类型

| 类型 | 代表产品 | 绕过难度 |
| ---- | -------- | -------- |
| **图片文字** | 传统验证码 | ★★（OCR/深度学习） |
| **滑块** | 极验 (GeeTest)、网易易盾 | ★★★ |
| **点选** | 点击文字/图标顺序 | ★★★★ |
| **reCAPTCHA v2** | Google 图像分类 | ★★★ |
| **reCAPTCHA v3** | Google 无感行为评分 | ★★★★ |
| **hCaptcha** | Intuition Machines | ★★★ |
| **Turnstile** | Cloudflare 无感挑战 | ★★★★★ |

### 滑块验证码：轨迹生成

滑块验证码的核心检测维度是**拖拽轨迹真实性**，而非仅滑动距离：

```python
import random

def generate_human_track(distance: int) -> list[dict]:
    """生成仿人类滑动轨迹：先加速后减速 + Y 轴抖动"""
    track, current, t, v = [], 0, 0, 0
    mid = distance * 0.7
    while current < distance:
        a = random.uniform(2.5, 3.5) if current < mid else random.uniform(-3.0, -1.5)
        dt = random.uniform(10, 20)
        v = max(v + a * (dt / 1000), 0.5)
        current = min(current + v * (dt / 1000) * 100, distance)
        t += dt
        track.append({"x": round(current, 2), "y": round(random.uniform(-2, 2), 2), "t": round(t)})
    return track
```

### reCAPTCHA v3 评分因素

reCAPTCHA v3 在后台收集信号并给出 0.0（机器人）到 1.0（人类）的评分，主要受以下因素影响：浏览器环境完整性、页面行为轨迹（鼠标/滚动/点击）、Google 登录状态、历史 Cookie。

> **提示**: 第三方打码平台（2Captcha、Anti-Captcha）通过真人或 AI 辅助完成验证并返回 API 结果，是绕过复杂验证码的常见商业方案。

---

## 5. JavaScript 指纹检测

浏览器指纹通过收集客户端各种特征值为访问者生成唯一标识，即使清除 Cookie 仍可追踪。

### 主要指纹维度

| 指纹类型 | 检测方式 | 信息熵 |
| -------- | -------- | ------ |
| **Canvas** | 绘制隐藏 Canvas，读取像素 hash | 高 |
| **WebGL** | 获取 GPU 渲染器信息 | 高 |
| **AudioContext** | 生成音频信号采样，不同硬件产生不同波形 | 中 |
| **字体列表** | 检测系统安装字体 | 中 |
| **Navigator** | `platform`, `hardwareConcurrency`, `deviceMemory` | 低 |

### 无头浏览器检测手段

```javascript
// 网站端常见检测点
const botSignals = {
    webdriver: navigator.webdriver === true,
    noPlugins: navigator.plugins.length === 0,
    noLanguages: !navigator.languages || navigator.languages.length === 0,
    noChromeRuntime: !window.chrome || !window.chrome.runtime,
    automationAPIs: !!(window.__puppeteer_evaluation_script__),
};
```

### Playwright Stealth 反检测

```python
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        locale="zh-CN", timezone_id="Asia/Shanghai",
    )
    page = context.new_page()
    stealth_sync(page)  # 修补 navigator.webdriver 等检测点
    page.goto("https://bot.sannysoft.com/")
    browser.close()
```

### Frida 修改 Android WebView 指纹

```javascript
// Frida 脚本：覆盖 WebView 中的指纹检测点
Java.perform(function () {
    var WebView = Java.use("android.webkit.WebView");
    WebView.loadUrl.overload("java.lang.String").implementation = function (url) {
        this.evaluateJavascript(
            `Object.defineProperty(navigator, 'webdriver', {get: () => false});` +
            `Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});`,
            null
        );
        this.loadUrl.overload("java.lang.String").call(this, url);
    };
});
```

---

## 6. Cookie/Token 机制

### 常见反爬 Cookie

| Cookie | 产品 | 生成方式 |
| ------ | ---- | -------- |
| `__cf_bm` / `cf_clearance` | Cloudflare | JS 挑战通过后设置 |
| `_abck` | Akamai | Sensor data 提交后获取 |
| `__ac_nonce` | PerimeterX | PX 脚本计算后设置 |
| `datadome` | DataDome | JS 计算后设置 |

### WAF Token 流程（以 Cloudflare 为例）

```
客户端                      Cloudflare                   源站
  │── 首次请求 ──────────>│                              │
  │<── 返回 JS 挑战 ─────│  (HTTP 503 + 混淆 JS)       │
  │   [执行 JS + 采集指纹]│                              │
  │── 提交答案 ──────────>│── 验证 ──>                  │
  │<── 302 + Set-Cookie ──│  (cf_clearance)              │
  │── 携带 Cookie 访问 ──>│── 代理转发 ────────────────>│
  │<── 真实内容 ──────────│<── 源站响应 ────────────────│
```

### Cookie 提取与复用

```python
from playwright.sync_api import sync_playwright

def extract_cf_cookies(url: str) -> dict:
    """用 Playwright 通过挑战后提取 Cookie，再用 requests 高效请求"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(5000)
        cookies = {c["name"]: c["value"] for c in page.context.cookies()}
        browser.close()
    return cookies
```

> **注意**: `cf_clearance` 通常绑定 IP + User-Agent，更换后需重新获取。

---

## 7. 动态渲染页面

### SPA/CSR 挑战

| 渲染方式 | 说明 | 爬取难度 |
| -------- | ---- | -------- |
| **SSR** | HTML 包含完整内容 | ★ |
| **CSR** | HTML 为空壳，数据由 JS 渲染 | ★★★ |
| **SSG** | 构建时生成完整 HTML | ★ |

### 方案一：API 优先（推荐）

打开浏览器 DevTools → Network → 筛选 XHR/Fetch 请求 → 找到 JSON API → 直接调用（比渲染快 10-100 倍）。

### 方案二：Playwright 渲染

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    page = p.chromium.launch().new_page()
    page.goto("https://example.com/spa")
    page.wait_for_selector(".product-list", timeout=15000)
    for _ in range(5):  # 处理无限滚动
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(1500)
    html = page.content()
```

### 方案三：拦截网络请求

```python
from playwright.sync_api import sync_playwright

api_data = []
def on_response(resp):
    if "/api/" in resp.url and resp.status == 200:
        try: api_data.append(resp.json())
        except: pass

with sync_playwright() as p:
    page = p.chromium.launch().new_page()
    page.on("response", on_response)
    page.goto("https://example.com/products")
    page.wait_for_load_state("networkidle")
# api_data 中包含所有拦截到的 JSON 响应
```

---

## 8. 蜜罐与陷阱

蜜罐 (Honeypot) 是网站设置的对人类不可见但爬虫会触发的陷阱。

### 常见类型

| 陷阱类型 | 实现方式 | 原理 |
| -------- | -------- | ---- |
| **隐藏链接** | `display:none` 的 `<a>` 标签 | 人类看不到不会点击 |
| **不可见表单** | 隐藏 `<input>` | 爬虫自动填写，人类不会 |
| **假数据页面** | 含标记数据的页面 | 追踪假数据传播 |
| **无限目录** | 动态生成无限分页链接 | 爬虫无限循环 |

### 蜜罐检测

```python
from bs4 import BeautifulSoup

def is_honeypot(element) -> bool:
    style = element.get("style", "").lower()
    traps = ["display:none", "display: none", "visibility:hidden",
             "opacity:0", "font-size:0", "left:-9999"]
    if any(t in style for t in traps):
        return True
    classes = " ".join(element.get("class", [])).lower()
    return any(k in classes for k in ["trap", "honey", "hidden", "invisible"])

soup = BeautifulSoup(html, "html.parser")
safe_links = [a["href"] for a in soup.find_all("a", href=True) if not is_honeypot(a)]
```

> **注意**: 高级蜜罐通过外部 CSS 或 JS 控制可见性，仅检查内联样式不够，必要时需解析完整 CSS 规则。

---

## 9. 综合反爬方案分析

### 主流商业产品

| 产品 | 厂商 | 核心技术 | 绕过难度 |
| ---- | ---- | -------- | -------- |
| **Bot Management** | Cloudflare | JS 挑战 + Turnstile + ML 行为分析 | ★★★★ |
| **Bot Manager** | Akamai | Sensor Data + 设备指纹 + IP 情报 | ★★★★★ |
| **Advanced Bot Protection** | PerimeterX (HUMAN) | 行为生物识别 + JS 混淆 | ★★★★★ |
| **DataDome** | DataDome | ML 实时检测 + CAPTCHA | ★★★★ |
| **Shape Security** | F5 Networks | JS 代码变形 + 信号收集 | ★★★★★ |

### Cloudflare 多级防护

1. **IP 防火墙** — 基于 IP 信誉的访问控制
2. **速率限制** — 可配置的请求频率限制
3. **JS Challenge** — 轻量级 JS 计算挑战（五秒盾）
4. **Managed Challenge (Turnstile)** — 根据风险评分决定是否展示 CAPTCHA
5. **Bot Management (企业版)** — ML 行为分析 + JA3/JA4 指纹

### Akamai Sensor Data 结构

```
sensor_data:
├── 设备信息: UA / 屏幕分辨率 / 时区
├── 浏览器指纹: Canvas hash / WebGL 渲染器 / AudioContext
├── 行为数据: 鼠标轨迹 / 键盘事件 / 触摸事件 / 滚动
└── 环境检测: 自动化工具 / DevTools / 虚拟机检测
```

> **逆向要点**: Akamai JS 高度混淆且频繁更新（有时每天更新），直接逆向 sensor data 的维护成本极高。使用带 stealth 补丁的真实浏览器是更可持续的方案。

---

## 10. 实战对抗策略

### 绕过决策树

```
1. 有公开 API / RSS？       → 是 → 直接调用（最优方案）
2. 服务端渲染（SSR）？       → 是 → requests + 正确 Headers
3. 有 JS 挑战 / WAF？       → 否 → Playwright 渲染即可
4. 哪家 WAF？               → Cloudflare: Playwright+stealth+住宅代理
                             → Akamai: 真实浏览器+行为模拟+高质量代理
5. 有 CAPTCHA？             → 是 → 打码平台 API
6. 有 IP 限制？             → 是 → 代理池轮转 + 频率控制
```

### 策略对比

| 策略 | 适用场景 | 成功率 | 速度 | 成本 |
| ---- | -------- | ------ | ---- | ---- |
| requests + Headers | 无 JS 防护的简单站点 | ★★ | ★★★★★ | 免费 |
| curl_cffi 模拟指纹 | 有 TLS/Header 检测 | ★★★ | ★★★★ | 免费 |
| Playwright + Stealth | Cloudflare / 一般 WAF | ★★★★ | ★★ | 免费 |
| 真实浏览器 + 行为模拟 | 高级 WAF (Akamai/PX) | ★★★★★ | ★ | 代理费 |
| 逆向 JS 生成 Token | 特定目标深度对抗 | ★★★★ | ★★★★★ | 人力高 |
| 打码平台 + 自动化 | 有验证码拦截 | ★★★★ | ★★★ | 按次计费 |

---

## 专题：绕过 Cloudflare 五秒盾

Cloudflare 的"I'm Under Attack Mode"是一个常见的强力反机器人措施，用户会看到持续约五秒的"Checking your browser..."页面，即"五秒盾"。

### 工作原理

五秒盾的核心是 **JavaScript 挑战**。首次访问时服务器返回高度混淆的 JS 代码，执行以下步骤：

1. **环境检测** — 检查 `window`、`document` 等对象及浏览器指纹
2. **计算密集型任务** — 执行复杂数学运算（现代浏览器 1-2 秒可完成，纯 `requests` 无法完成）
3. **生成验证 Token** — 计算结果作为 Token 提交给 Cloudflare 验证
4. **设置身份 Cookie** — 验证通过后设置 `cf_clearance`，后续请求携带即可免挑战

### 绕过方案

**方案一：Playwright 通过挑战（推荐）**

```python
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

def bypass_cloudflare(target_url: str) -> tuple[str, dict]:
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(viewport={"width": 1920, "height": 1080}, locale="zh-CN")
        page = context.new_page()
        stealth_sync(page)
        page.goto(target_url)

        # 等待 cf_clearance Cookie 出现
        for _ in range(30):
            cookies = {c["name"]: c["value"] for c in context.cookies()}
            if "cf_clearance" in cookies:
                break
            page.wait_for_timeout(1000)

        content = page.content()
        browser.close()
    return content, cookies
```

**方案二：提取 Cookie 后用 requests 复用**

```python
import requests

# cf_clearance 绑定 IP + User-Agent，必须保持一致
cookies = {"cf_clearance": "从浏览器获取的值", "__cf_bm": "对应的值"}
headers = {"User-Agent": "获取 Cookie 时使用的 UA 字符串"}
resp = requests.get("https://protected-site.com/data", cookies=cookies, headers=headers)
```

> **注意**: 更换 IP 或 UA 后 `cf_clearance` 会失效，需重新通过挑战获取。
