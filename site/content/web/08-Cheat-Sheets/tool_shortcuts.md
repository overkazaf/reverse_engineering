---
title: "工具快捷键速查表"
date: 2025-04-16
tags: ["Web", "代理池", "速查表", "Hook", "参考", "ARM汇编"]
weight: 10
---

# 工具快捷键速查表

## Chrome DevTools

### 打开/切换面板

| 快捷键 | 功能 |
| ------------------------------------------- | ----------------------- |
| `F12` | 打开/关闭 DevTools |
| `Ctrl+Shift+I` (Win) / `Cmd+Option+I` (Mac) | 打开/关闭 DevTools |
| `Ctrl+Shift+J` (Win) / `Cmd+Option+J` (Mac) | 直接打开 Console |
| `Ctrl+Shift+C` (Win) / `Cmd+Option+C` (Mac) | 元素检查模式 |
| `Ctrl+Shift+M` (Win) / `Cmd+Shift+M` (Mac) | 设备模拟模式 |
| `Ctrl+Shift+P` (Win) / `Cmd+Shift+P` (Mac) | 命令面板 |
| `Ctrl+[` / `Ctrl+]` | 切换面板 |
| `Esc` | 显示/隐藏抽屉 (Console) |

### Sources 面板

| 快捷键 | 功能 |
| ------------------- | ------------- |
| `F8` | 暂停/继续 |
| `F9` | 设置/取消断点 |
| `F10` | 单步跳过 |
| `F11` | 单步进入 |
| `Shift+F11` | 单步跳出 |
| `Ctrl+F` | 搜索文件 |
| `Ctrl+Shift+F` | 全局搜索 |
| `Ctrl+G` | 跳转到行 |
| `Ctrl+O` / `Ctrl+P` | 打开文件 |
| `Ctrl+Shift+O` | 跳转到函数 |

### Console 面板

| 快捷键 | 功能 |
| --------- | ------------ |
| `Ctrl+L` | 清空 Console |
| `↑` / `↓` | 历史命令导航 |
| `Tab` | 自动补全 |
| `Ctrl+U` | 清除当前输入 |

### Elements 面板

| 快捷键 | 功能 |
| --------- | ------------- |
| `↑` / `↓` | 导航 DOM 树 |
| `→` | 展开节点 |
| `←` | 收起节点 |
| `F2` | 编辑 HTML |
| `Delete` | 删除节点 |
| `Ctrl+Z` | 撤销 |
| `H` | 隐藏/显示元素 |

### Network 面板

| 快捷键 | 功能 |
| -------------- | ------------- |
| `Ctrl+R` | 重新加载 |
| `Ctrl+Shift+R` | 强制重新加载 |
| `Ctrl+E` | 开始/停止录制 |
| `Ctrl+F` | 搜索请求 |

---

## VS Code

### 通用

| 快捷键 | 功能 |
| -------------- | ------------ |
| `Ctrl+P` | 快速打开文件 |
| `Ctrl+Shift+P` | 命令面板 |
| `Ctrl+B` | 切换侧边栏 |
| `Ctrl+\` | 拆分编辑器 |
| `Ctrl+W` | 关闭编辑器 |
| `Ctrl+Tab` | 切换编辑器 |
| `Ctrl+Shift+N` | 新窗口 |

### 编辑

| 快捷键 | 功能 |
| -------------------- | ------------------ |
| `Ctrl+X` | 剪切行 |
| `Ctrl+C` | 复制行 |
| `Ctrl+Shift+K` | 删除行 |
| `Alt+↑/↓` | 移动行 |
| `Shift+Alt+↑/↓` | 复制行 |
| `Ctrl+/` | 切换注释 |
| `Ctrl+Shift+[` / `]` | 折叠/展开代码块 |
| `Ctrl+D` | 选择下一个相同内容 |
| `Ctrl+Shift+L` | 选择所有相同内容 |
| `Alt+Click` | 多光标 |

### 搜索/替换

| 快捷键 | 功能 |
| ----------------- | ----------------- |
| `Ctrl+F` | 查找 |
| `Ctrl+H` | 替换 |
| `Ctrl+Shift+F` | 全局查找 |
| `Ctrl+Shift+H` | 全局替换 |
| `F3` / `Shift+F3` | 查找下一个/上一个 |

### 调试

| 快捷键 | 功能 |
| ----------- | ------------- |
| `F5` | 开始/继续调试 |
| `F9` | 切换断点 |
| `F10` | 单步跳过 |
| `F11` | 单步进入 |
| `Shift+F11` | 单步跳出 |
| `Shift+F5` | 停止调试 |

---

## Burp Suite

### 通用

| 快捷键 | 功能 |
| -------------- | ------------------ |
| `Ctrl+Shift+P` | 前进到下一个标签页 |
| `Ctrl+Shift+N` | 后退到上一个标签页 |
| `Ctrl+T` | 转发请求到其他工具 |

### Proxy 拦截

| 快捷键 | 功能 |
| -------- | --------------- |
| `Ctrl+F` | 转发请求 |
| `Ctrl+D` | 丢弃请求 |
| `Ctrl+I` | 切换拦截开/关 |
| `Ctrl+R` | 发送到 Repeater |
| `Ctrl+S` | 发送到 Scanner |

### Repeater

| 快捷键 | 功能 |
| ------------ | ----------------- |
| `Ctrl+Space` | 发送请求 |
| `Ctrl+R` | 切换原始/美化视图 |

### Intruder

| 快捷键 | 功能 |
| -------- | -------- |
| `Ctrl+I` | 开始攻击 |

---

## Fiddler

| 快捷键 | 功能 |
| ----------- | ----------------- |
| `F12` | 开始/停止捕获 |
| `F5` | 刷新会话列表 |
| `F2` | 为会话添加注释 |
| `Ctrl+X` | 删除所有会话 |
| `Ctrl+F` | 查找会话 |
| `Shift+Del` | 删除选中会话 |
| `U` | 解压缩响应 |
| `D` | 解码选中的文本 |
| `B` | 在 Brea 前 kpoint |

---

## Charles

| 快捷键 | 功能 |
| ------------------------------ | ------------- |
| `Cmd+R` (Mac) / `Ctrl+R` (Win) | 开始/停止录制 |
| `Cmd+K` | 清空会话 |
| `Cmd+F` | 查找 |
| `Cmd+E` | 启用/禁用断点 |

---

## Python IDE (PyCharm)

### 导航

| 快捷键 | 功能 |
| -------------- | ---------- |
| `Ctrl+N` | 查找类 |
| `Ctrl+Shift+N` | 查找文件 |
| `Ctrl+B` | 跳转到定义 |
| `Ctrl+Alt+←` | 后退 |
| `Ctrl+Alt+→` | 前进 |

### 编辑

| 快捷键 | 功能 |
| ------------ | ------------- |
| `Ctrl+D` | 复制行 |
| `Ctrl+Y` | 删除行 |
| `Ctrl+/` | 注释/取消注释 |
| `Ctrl+Alt+L` | 格式化代码 |
| `Ctrl+Space` | 代码补全 |

### 调试

| 快捷键 | 功能 |
| ---------- | -------- |
| `Shift+F9` | 调试 |
| `F8` | 单步跳过 |
| `F7` | 单步进入 |
| `Shift+F8` | 单步跳出 |
| `F9` | 继续执行 |
| `Ctrl+F8` | 切换断点 |

---

## 浏览器通用

| 快捷键 | 功能 |
| ------------------- | -------------------- |
| `Ctrl+T` | 新标签页 |
| `Ctrl+W` | 关闭标签页 |
| `Ctrl+Shift+T` | 重新打开关闭的标签页 |
| `Ctrl+Tab` | 下一个标签页 |
| `Ctrl+Shift+Tab` | 上一个标签页 |
| `Ctrl+L` | 地址栏 |
| `Ctrl+D` | 添加书签 |
| `Ctrl+H` | 历史记录 |
| `Ctrl+J` | 下载记录 |
| `F5` | 刷新 |
| `Ctrl+F5` | 强制刷新（清除缓存） |
| `Ctrl+U` | 查看源代码 |
| `Ctrl+Shift+Delete` | 清除浏览数据 |

---

## Wireshark

| 快捷键 | 功能 |
| -------- | -------------- |
| `Ctrl+E` | 开始/停止捕获 |
| `Ctrl+W` | 关闭捕获 |
| `Ctrl+R` | 重新加载 |
| `Ctrl+F` | 查找数据包 |
| `Ctrl+G` | 跳转到数据包 |
| `Ctrl+M` | 标记数据包 |
| `Ctrl+B` | 查找下一个标记 |

---

## Git GUI (SourceTree)

| 快捷键 | 功能 |
| -------------- | ----------- |
| `Ctrl+1` | File Status |
| `Ctrl+2` | History |
| `Ctrl+3` | Search |
| `Ctrl+R` | Refresh |
| `Ctrl+P` | Push |
| `Ctrl+Shift+P` | Pull |

---

## 自定义快捷键建议

为常用操作设置快捷键可以大幅提高效率：

### Chrome Snippets

1. DevTools → Sources → Snippets
2. 创建常用 Hook 脚本
3. 右键 → "Run" 或按 `Ctrl+Enter`

### Tampermonkey

设置快捷键执行用户脚本：

```javascript
// ==UserScript==
// @name My Hook Script
// @grant GM_registerMenuCommand
// ==/UserScript==

GM_registerMenuCommand("Execute Hook", function () {
// Your hook code
});
```

---

## 相关章节

- [Chrome DevTools](../02-Tooling/browser_devtools.md)
- [Burp Suite](../02-Tooling/burp_suite_guide.md)
- [常用命令](./common_commands.md)
