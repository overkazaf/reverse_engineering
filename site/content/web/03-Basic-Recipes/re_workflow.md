---
title: "Web 逆向工程工作流"
date: 2025-12-25
weight: 10
---

# Web 逆向工程工作流

一个系统化的 Web 逆向分析完整流程，从初步侦查到自动化实现。

---

## 配方信息

| 项目 | 说明 |
| ------------ | -------------------------------------------------- |
| **难度** | ⭐⭐⭐ (中级) |
| **预计时间** | 2-8 小时 (根据目标复杂度) |
| **所需工具** | Chrome DevTools, Burp Suite (可选), Python/Node.js |
| **适用场景** | 任何 Web 逆向项目 |

---

## 📚 前置知识

在开始本配方之前，建议先掌握以下内容：

| 知识领域 | 重要程度 | 参考资料 |
|----------|---------|---------|
| Chrome DevTools 基础 | 必需 | [浏览器开发者工具](../02-Tooling/browser_devtools.md) |
| JavaScript 基础 | 必需 | [JavaScript 基础](../01-Foundations/javascript_basics.md) |
| HTTP 协议 | 推荐 | [HTTP/HTTPS 协议](../01-Foundations/http_https_protocol.md) |
| Hook 技术基础 | 推荐 | [Hook 技术](./hooking_techniques.md) |

> 💡 **提示**: 本配方是一个**系统化的方法论**，适合作为所有逆向项目的标准流程参考。建议先完成快速入门系列后再学习本配方。

---

## 学习目标

完成本配方后，你将能够：

- ✅ 系统化地分析任何 Web 应用
- ✅ 快速定位关键加密和签名逻辑
- ✅ 选择合适的自动化方案
- ✅ 构建可复现的逆向流程

---

## 阶段一：信息收集 (Reconnaissance)

### 1. 目标确认

- **明确目标**: 要逆向什么功能？登录？数据加密？API 签名？
- **合法性检查**: 确保在授权范围内进行测试

### 2. 技术栈识别

**工具**:

- **Wappalyzer** (浏览器插件): 识别框架、库、服务器
- **BuiltWith**: 查看网站技术栈

**手动检查**:

```javascript
// Console 中查看全局对象
window.jQuery && jQuery.fn.jquery; // jQuery 版本
window.React && React.version; // React 版本
window.Vue && Vue.version; // Vue 版本
```

### 3. 资源枚举

- **查看 HTML 源代码**: `Ctrl+U`
- **检查 JavaScript 文件**: Sources 面板查看所有 JS 文件
- **检查网络请求**: Network 面板查看 API 端点

---

## 阶段二：流量分析 (Traffic Analysis)

### 1. 抓包分析

**目标**: 了解客户端与服务器的通信方式

**步骤**:

1. 打开 DevTools -> Network 面板
2. 清空记录，执行目标操作（如登录、提交表单）
3. 分析请求：
    - 请求方法（GET/POST）
    - 请求参数
    - 请求头（特别是自定义 Header）
    - 响应数据格式

**关键问题**:

- 是否有签名参数？（如 `sign`, `signature`, `token`）
- 时间戳格式？（Unix 时间戳 / 毫秒）
- 是否有加密数据？（Base64 / Hex 编码特征）

### 2. 定位关键请求

在 Network 面板使用过滤器：

- Filter by keyword: `sign`, `encrypt`, `token`
- Filter by type: `Fetch/XHR`

---

## 阶段三：静态分析 (Static Analysis)

### 1. JavaScript 代码定位

**方法一：全局搜索**

1. `Ctrl+Shift+F` 打开全局搜索
2. 搜索关键词：
    - 参数名：`sign`, `timestamp`
    - 加密关键词：`encrypt`, `crypto`, `MD5`, `AES`
    - API 端点：`/api/login`

**方法二：利用 Network Initiator**

1. 在 Network 面板点击目标请求
2. 查看 Initiator 标签页
3. 点击调用链中的文件名，跳转到源码

### 2. 代码美化

如果代码被压缩：

- DevTools 自动格式化：点击 `{}` 按钮
- 在线工具：`beautifier.io`

如果代码被混淆：

- 参考 [JavaScript 反混淆](../04-Advanced-Recipes/javascript_deobfuscation.md)

### 3. 算法识别

**常见特征**:

- MD5: `16 字节` 输出，通常表示为 32 位十六进制
- SHA256: `32 字节` 输出，64 位十六进制
- AES: 需要密钥和 IV
- Base64: 结尾可能有 `=` 填充

---

## 阶段四：动态调试 (Dynamic Analysis)

### 1. 设置断点

**断点类型**:

- **行断点**: 直接点击行号
- **条件断点**: 右键行号 -> "Add conditional breakpoint"
- **XHR/Fetch 断点**: 在 Sources 面板右侧勾选
- **事件断点**: Mouse -> click

### 2. 追踪参数生成

当断点停下后：

1. 查看 **Call Stack** (调用栈)
2. 查看 **Scope** (作用域变量)
3. 单步执行 (`F10` / `F11`)，观察变量变化

### 3. Hook 关键函数

```javascript
// Hook fetch
const originalFetch = window.fetch;
window.fetch = function (...args) {
console.log("[Fetch]", args);
return originalFetch.apply(this, arguments);
};

// Hook JSON.stringify (常用于构造请求体)
const originalStringify = JSON.stringify;
JSON.stringify = function (obj) {
console.log("[JSON.stringify]", obj);
debugger; // 自动断点
return originalStringify.apply(this, arguments);
};
```

---

## 阶段五：逻辑还原 (Logic Reconstruction)

### 1. 梳理签名流程

绘制流程图：

```
用户输入 ->
参数收集 (username, password, timestamp) ->
参数排序 ->
字符串拼接 ->
加盐 (salt) ->
哈希计算 (MD5/SHA256) ->
签名字段 (sign)
```

### 2. 提取关键代码

将核心加密/签名函数复制到单独文件，或用 Python/Node.js 重写。

---

## 阶段六：自动化实现 (Automation)

### 方案一：扣 JavaScript 代码

**适用场景**: 算法复杂，难以还原

**工具**: Node.js

```javascript
// encrypt.js
function generateSign(params) {
// 复制的原始代码
let str = Object.keys(params)
.sort()
.map((k) => `${k}=${params[k]}`)
.join("&");
return md5(str + "secret_salt");
}

module.exports = { generateSign };
```

```python
# main.py
import execjs
import requests

with open('encrypt.js', 'r') as f:
js_code = f.read()

ctx = execjs.compile(js_code)
sign = ctx.call('generateSign', {'user': 'admin', 'pass': '123456'})

response = requests.post('https://target.com/api/login', data={'sign': sign})
```

### 方案二：纯 Python 实现

**适用场景**: 算法简单，可以用 Python 重写

```python
import hashlib
import time

def generate_sign(params):
sorted_params = sorted(params.items())
param_str = '&'.join([f"{k}={v}" for k, v in sorted_params])
sign_str = param_str + 'secret_salt'
return hashlib.md5(sign_str.encode()).hexdigest()

params = {
'username': 'admin',
'password': '123456',
'timestamp': int(time.time())
}

params['sign'] = generate_sign(params)
```

### 方案三：RPC 调用浏览器

**适用场景**: 算法依赖浏览器环境（Canvas 指纹、WebGL 等）

**工具**: Puppeteer / Selenium

```javascript
// Puppeteer
const puppeteer = require("puppeteer");

(async () => {
const browser = await puppeteer.launch();
const page = await browser.newPage();
await page.goto("https://target.com");

const sign = await page.evaluate(() => {
// 调用网页中的加密函数
return window.generateSign({ user: "admin" });
});

console.log("Sign:", sign);
await browser.close();
})();
```

---

## 阶段七：测试与验证

### 1. 单元测试

确保提取的算法输出与浏览器一致：

```python
import unittest

class TestSignGeneration(unittest.TestCase):
def test_sign(self):
params = {'user': 'test', 'timestamp': 1234567890}
sign = generate_sign(params)
# 与浏览器中生成的签名对比
self.assertEqual(sign, 'expected_sign_value')
```

### 2. 实战测试

使用生成的参数发送实际请求，验证服务器响应。

---

## 常见陷阱

### 1. 时间戳同步问题

- **现象**: 签名正确，但服务器返回"签名过期"
- **原因**: 服务器校验时间戳，要求与服务器时间误差在几秒内
- **解决**: 使用服务器时间或 NTP 同步

### 2. Nonce 唯一性

- **现象**: 重放请求失败
- **原因**: Nonce（随机数）被服务器记录，重复使用会被拒绝
- **解决**: 每次请求生成新的 UUID

### 3. 环境依赖

- **现象**: 扣下的 JS 代码在 Node.js 中报错
- **原因**: 代码依赖浏览器全局对象（window, document, navigator）
- **解决**: Mock 这些对象，或使用 jsdom

---

## ✅ 验证清单

完成以下检查确保逆向成功：

### 阶段验证

- ☐ **信息收集完成**

- ☐ 识别了技术栈和框架
- ☐ 枚举了所有关键资源
- ☐ 记录了目标功能

- ☐ **流量分析完成**

- ☐ 捕获了关键请求
- ☐ 识别了签名/加密参数
- ☐ 分析了请求头和响应

- ☐ **代码定位完成**

- ☐ 找到了加密/签名函数
- ☐ 理解了参数生成逻辑
- ☐ 识别了算法类型

- ☐ **动态调试完成**

- ☐ 成功设置断点
- ☐ 追踪了完整调用链
- ☐ 提取了关键参数

- ☐ **自动化实现完成**
- ☐ 编写了复现代码
- ☐ 测试输出与浏览器一致
- ☐ 实际请求成功

---

## 故障排除

### 问题：找不到关键代码

**症状**: 搜索加密关键词无结果

**解决方案**:

1. 尝试搜索函数调用模式: `CryptoJS`, `btoa`, `atob`
2. 从 Network Initiator 反向追踪
3. 查找混淆后的变量名模式: `_0x`, `__`
4. 使用 XHR 断点自动拦截

### 问题：扣下的 JS 代码无法运行

**症状**: `ReferenceError: window is not defined`

**解决方案**:

```javascript
// 在 Node.js 中 Mock 浏览器对象
global.window = global;
global.document = {};
global.navigator = {
userAgent: "Mozilla/5.0...",
};
```

### 问题：签名验证失败

**症状**: 服务器返回 "Invalid signature"

**解决方案**:

1. 检查参数排序是否正确
2. 检查编码格式 (UTF-8 vs GBK)
3. 检查时间戳精度 (秒 vs 毫秒)
4. 检查是否缺少隐藏参数
5. 使用 diff 工具对比浏览器和代码的输出

---

## 最佳实践

### 1. 分阶段记录

为每个阶段创建笔记文件：

```
analysis/
├── 01-recon.md # 信息收集记录
├── 02-traffic.md # 流量分析
├── 03-code.md # 代码定位
├── 04-algorithm.md # 算法分析
└── 05-implementation.md # 实现方案
```

### 2. 版本控制

```bash
git init
git add .
git commit -m "Initial analysis"

# 每个阶段提交
git commit -m "Phase 1: Recon completed"
```

### 3. 测试驱动

先写测试用例，再实现：

```python
def test_sign_generation():
# 从浏览器获取的已知值
expected = "abc123def456"
actual = generate_sign(test_params)
assert actual == expected
```

---

## 总结

Web 逆向工程是一个循环迭代的过程：

```
信息收集 -> 流量分析 -> 静态分析 -> 动态调试 -> 逻辑还原 -> 自动化 -> 测试 -> (循环)
```

**核心原则**:

1. **逐层深入**: 从外到内，先了解整体再钻研细节
2. **工具组合**: DevTools + Burp Suite + Python
3. **记录文档**: 记录关键发现，便于后续参考
4. **测试验证**: 每个阶段都要验证正确性

**成功标志**:

- ✅ 能够稳定复现目标功能
- ✅ 代码输出与浏览器完全一致
- ✅ 理解完整的加密/签名流程
- ✅ 可以批量自动化执行

---

## 相关章节

- [调试技巧与断点设置](./debugging_techniques.md)
- [API 接口逆向](./api_reverse_engineering.md)
- [JavaScript 反混淆](../04-Advanced-Recipes/javascript_deobfuscation.md)
- [加密算法识别](./crypto_identification.md)
- [Hook 技巧](./hooking_techniques.md)
