# 03-Advanced-Topics Summary

本章节讲解了 Web 逆向中的高阶对抗技术。

---

## 💭 开始前的思考

进入高级领域之前，挑战你的思维：

1. **为什么网站要检测你在调试？** 这对用户体验有什么影响？
2. **指纹识别真的能唯一标识一个人吗？** 如果不能，为什么还要用？
3. **WebAssembly 是黑盒吗？** 编译后的代码就一定安全吗？
4. **攻防对抗会有终点吗？** 还是永远的猫鼠游戏？

高级技术的背后，是攻防双方的智慧博弈。

---

## 主要内容

- **反调试 Bypass**:
  - 检测点识别 (Function.prototype.toString, debugger, 窗口大小)。
  - 绕过方案 (置空函数、Hook 构造器、修改环境)。
- **指纹识别与伪造**:
  - Canvas 指纹、WebGL 指纹、Audio 指纹。
  - 浏览器指纹库 (FingerprintJS) 原理分析。
- **自动化检测绕过**:
  - `navigator.webdriver` 属性隐藏。
  - CDP (Chrome DevTools Protocol) 识别绕过。
- **Wasm 逆向进阶**:
  - 复杂算法还原。
  - 动态注入与内存 Dump。
