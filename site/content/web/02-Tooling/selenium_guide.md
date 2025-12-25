---
title: "Selenium 指南"
date: 2024-07-07
type: posts
tags: ["Web", "代理池", "Hook", "抓包", "Playwright", "DevTools"]
weight: 10
---

# Selenium 指南

## 概述

Selenium 是 Web 自动化领域的元老。虽然在轻量级和抗检测性上不如 Puppeteer/Playwright，但由于其生态成熟、多语言支持好（Python/Java），依然在一些大型爬虫项目中有应用。

对于逆向工程师来说，主要需要了解如何 **Bypass Selenium 检测**。

---

## 1. 基础使用 (Python)

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
# 尽可能使用 CDP 命令来规避检测
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

driver = webdriver.Chrome(options=options)
driver.get("https://example.com")
```

---

## 2. 反爬虫检测与绕过

许多网站会通过 `window.navigator.webdriver` 来检测 Selenium。

### 检测原理

浏览器启动时，如果是自动化控制模式，`navigator.webdriver` 会被设置为 `true`。

### 绕过方案

#### 方案 A: CDP 方法 (推荐)

在加载页面前，执行 CDP 命令删除该属性。

```python
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
"source": """
Object.defineProperty(navigator, 'webdriver', {
get: () => undefined
})
"""
})
```

#### 方案 B: 中间人代理

使用 mitmproxy / Burp 拦截响应，注入 JS 代码覆盖 `navigator` 属性。

#### 方案 C: undetected-chromedriver

这是一个专门为了绕过检测而修改过的 ChromeDriver 封装库。

```bash
pip install undetected-chromedriver
```

```python
import undetected_chromedriver as uc
driver = uc.Chrome()
driver.get('https://nowsecure.nl') # 这是一个高强度检测站
```

---

## 3. 为什么逆向中可以较少用 Selenium？

1. **指纹严重**: Selenium 留下的特征比 Puppeteer 多得多（如 `cdc_` 变量）。
2. **Hook 不便**: 虽然可以通过 CDP 注入，但原生 API 对 Request Interception 的支持不如 Puppeteer 优雅。
3. **环境重**: 需要下载对应版本的 WebDriver，容易出现版本不兼容问题。

---

## 总结

如果你要写一个新的逆向脚本，建议首选 **Puppeteer / Playwright**。如果你必须维护现有的 Selenium 项目，请熟练掌握 **CDP 注入** 和 **undetected-chromedriver** 来对抗反爬虫。
