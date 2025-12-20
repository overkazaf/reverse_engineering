# 06-Scripts Summary

本章节收录了 Web 逆向工程中常用的实战脚本和自动化工具，涵盖 Hook 技术、反混淆、加密检测和浏览器自动化等核心领域。所有脚本均经过实战验证，可直接应用于真实项目。

---

## 本章内容概览

### 1. [JavaScript Hook 脚本](javascript_hook_scripts.md)

**核心技术**: 运行时函数劫持、API 监控、动态分析

Hook（钩子）是 Web 逆向的核心技术，通过运行时劫持原生 API 或自定义函数，实现无侵入式监控和行为修改。

**涵盖内容**:

- **基础 Hook 模板**: 全局函数劫持、原型链 Hook
- **网络请求监控**: XHR、Fetch、WebSocket Hook
- **存储操作拦截**: Cookie、LocalStorage、SessionStorage Hook
- **加密函数追踪**: CryptoJS、Web Crypto API、JSEncrypt Hook
- **高级技术**:
  - 使用 ES6 Proxy 实现深度拦截
  - 性能优化和条件 Hook
  - 函数调用栈追踪和性能分析
  - 防御性 Hook 避免被检测
  - Hook 管理框架封装
- **实战案例**:
  - 破解动态密钥生成算法
  - 绕过虚拟机检测
  - 参数污染检测
- **最佳实践**: Hook 时机、性能考虑、错误处理

**适用场景**: API 调试、加密分析、反调试绕过、行为追踪

---

### 2. [反混淆脚本](deobfuscation_scripts.md)

**核心技术**: AST 变换、静态分析、动态执行结合

JavaScript 混淆是代码保护的常用手段，反混淆技术通过 AST（抽象语法树）变换和模式识别还原代码逻辑。

**涵盖内容**:

- **混淆类型识别**:
  - 变量名混淆
  - 字符串数组混淆
  - 控制流平坦化
  - 死代码注入
- **在线工具**: Prettier、JS-Beautify、de4js
- **AST 反混淆核心脚本**:
  - 基础框架（Babel 解析器）
  - 常量折叠
  - 字符串数组还原
  - 成员表达式计算
  - 死代码删除
  - 函数内联
- **高级 AST 变换**:
  - 数组/对象解构还原
  - 三元表达式简化
  - 逗号表达式展开
  - 控制流平坦化还原（状态机分析）
- **动态执行辅助**:
  - Node.js 沙箱执行
  - 选择性安全执行
- **实战案例**:
  - javascript-obfuscator 高级配置破解
  - Webpack 打包代码还原
- **自动化工具链**: 完整反混淆流水线
- **性能优化**: 增量处理、缓存优化、并行处理
- **调试技术**: 安全 AST 遍历、调试模式

**适用场景**: 代码还原、逻辑分析、混淆器识别

---

### 3. [加密算法识别脚本](crypto_detection_scripts.md)

**核心技术**: 特征匹配、常量识别、动态监控

识别目标网站使用的加密算法是逆向分析的第一步，通过自动化检测快速定位加密点并提取关键参数。

**涵盖内容**:

- **加密算法基础知识**:
  - 散列算法（MD5、SHA 系列、SM3）
  - 对称加密（AES、DES、3DES、RC4、SM4）
  - 非对称加密（RSA、ECC、SM2）
  - 编码算法（Base64、Base32、Hex）
- **特征识别方法**:
  - 代码特征检测（MD5、AES、RSA 特征模式）
  - 常量特征识别（魔数、S-Box、初始向量）
  - 输出特征判断（长度反推算法）
- **自动化检测脚本**:
  - 综合加密检测器（CryptoDetector 类）
  - 全局对象扫描
  - 已加载脚本分析
  - 算法特征匹配引擎
- **加密库 Hook**:
  - CryptoJS 全方位 Hook（MD5、SHA、AES、HMAC）
  - Web Crypto API 拦截
  - JSEncrypt RSA 监控
- **实战案例**:
  - 识别电商网站签名算法（MD5）
  - 破解 AES 加密请求参数
  - Python 复现加密逻辑
- **工具集成**: 浏览器插件、Node.js 静态分析
- **专业工具**: hash-identifier、CyberChef、Ciphey、findcrypt

**适用场景**: 加密算法识别、密钥提取、签名逆向、算法复现

---

### 4. [浏览器自动化脚本](automation_scripts.md)

**核心技术**: Puppeteer/Playwright、反检测、行为模拟

浏览器自动化通过程序化控制真实浏览器，实现数据采集、行为模拟，并绕过 JavaScript 验证和指纹检测。

**涵盖内容**:

- **技术选型对比**: Puppeteer vs Playwright vs Selenium
- **Puppeteer 实战脚本**:
  - 基础模板和配置
  - 登录自动化
  - 无限滚动加载
  - 滑块验证码处理
  - 请求拦截和修改
  - Hook 脚本注入
  - Webdriver 检测绕过
- **Playwright 实战脚本**:
  - 跨浏览器测试
  - 移动设备模拟
  - 并发爬取
  - 登录状态保存和恢复
  - HAR 网络监控导出
- **高级反检测技术**:
  - 完整的反检测方案（puppeteer-extra + stealth 插件）
  - CDP（Chrome DevTools Protocol）级别控制
  - 浏览器指纹伪造（WebGL、Canvas、User-Agent）
  - 网络和 CPU 限速模拟
- **验证码处理**:
  - 滑块验证码自动化（轨迹生成、图像识别）
  - 集成第三方打码平台（2captcha）
  - reCAPTCHA 求解
- **分布式爬虫架构**:
  - 基于 Redis 的任务队列
  - Worker 分布式部署
  - 结果存储和去重
- **性能监控与优化**:
  - 实时性能监控（请求统计、耗时分析）
  - 资源优化（禁用图片、阻止追踪）
  - 并发控制（p-limit）
  - 内存管理（页面池）
- **错误处理与恢复**:
  - 智能重试机制（指数退避）
  - 会话恢复（Cookie、LocalStorage 持久化）
- **最佳实践**: 并发控制、内存管理、日志记录
- **工具生态**: puppeteer-cluster、crawlee、browserless

**适用场景**: 数据采集、自动化测试、反爬虫对抗、验证码破解

---

## 学习路径建议

### 初级阶段

1. **入门**: 从[JavaScript Hook 脚本](javascript_hook_scripts.md)开始，掌握基础 Hook 技术
2. **实践**: 使用简单的 Hook 脚本监控网络请求和 Cookie 操作
3. **工具**: 熟悉 Chrome DevTools 和浏览器控制台

### 中级阶段

1. **深化**: 学习[反混淆脚本](deobfuscation_scripts.md)，理解 AST 变换原理
2. **检测**: 掌握[加密算法识别](crypto_detection_scripts.md)，能够快速定位加密点
3. **自动化**: 使用[浏览器自动化](automation_scripts.md)实现简单的数据采集

### 高级阶段

1. **综合应用**: 结合 Hook、反混淆、加密识别完成复杂逆向任务
2. **架构设计**: 构建分布式爬虫系统，处理大规模数据采集
3. **对抗升级**: 研究高级反检测技术，应对复杂的反爬虫机制

---

## 实战技能矩阵

| 技能点       | JavaScript Hook | 反混淆              | 加密识别   | 浏览器自动化         |
| ------------ | --------------- | ------------------- | ---------- | -------------------- |
| **难度**     | ⭐⭐            | ⭐⭐⭐              | ⭐⭐⭐     | ⭐⭐⭐⭐             |
| **应用频率** | ⭐⭐⭐⭐⭐      | ⭐⭐⭐⭐            | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐             |
| **前置知识** | JavaScript 基础 | AST、Babel          | 密码学基础 | Node.js、异步编程    |
| **必备工具** | DevTools        | Babel、AST Explorer | CyberChef  | Puppeteer/Playwright |
| **核心产出** | 监控脚本        | 可读代码            | 算法参数   | 自动化流程           |

---

## 快速参考

### 常用代码片段

**1. 通用 Hook 模板**

```javascript
const original = target.method;
target.method = function (...args) {
  console.log("Arguments:", args);
  const result = original.apply(this, args);
  console.log("Result:", result);
  return result;
};
```

**2. AST 常量折叠**

```javascript
traverse(ast, {
  BinaryExpression(path) {
    const result = path.evaluate();
    if (result.confident) {
      path.replaceWith(t.valueToNode(result.value));
    }
  },
});
```

**3. 加密检测**

```javascript
if (window.CryptoJS) {
  console.log("检测到 CryptoJS");
  // 安装Hook
}
```

**4. 反检测浏览器启动**

```javascript
const browser = await puppeteer.launch({
  headless: false,
  args: ["--disable-blink-features=AutomationControlled"],
});
```

---

## 扩展阅读

### 相关章节

- [调试技巧与断点设置](../03-Basic-Recipes/debugging_techniques.md)
- [浏览器开发者工具](../02-Tooling/browser_devtools.md)
- [AST 解析工具](../02-Tooling/ast_parsing_tools.md)
- [Puppeteer 与 Playwright](../02-Tooling/puppeteer_playwright.md)

### 推荐资源

- **Babel Handbook**: https://github.com/jamiebuilds/babel-handbook
- **Puppeteer 官方文档**: https://pptr.dev/
- **Playwright 官方文档**: https://playwright.dev/
- **CryptoJS 文档**: https://cryptojs.gitbook.io/

### 社区与论坛

- **GitHub**: 搜索相关开源项目学习
- **Stack Overflow**: JavaScript 逆向相关问题
- **吾爱破解**: 国内逆向技术论坛
- **看雪论坛**: 专业安全技术社区

---

## 持续更新

本章节的脚本和技术会持续更新，以应对不断演进的 Web 逆向挑战。建议定期回顾，关注：

- 新的混淆技术和对应的反混淆方法
- 最新的反爬虫检测手段和绕过技巧
- 加密算法的新变种和识别方法
- 浏览器自动化框架的新特性

**最后更新**: 2025 年 12 月

---

**下一步**: 选择感兴趣的章节深入学习，结合实际项目练习，逐步提升 Web 逆向技能。
