# 02-Techniques Summary

本章节涵盖了 Android 逆向的中级技术。

## 主要内容

- **静态分析**:
  - Manifest 分析 (权限、组件导出)。
  - 交叉引用 (Xref) 搜索关键字符串 (Token, Key, URL)。
- **动态分析**:
  - Hook Java 层函数 (参数/返回值修改)。
  - Log 插桩 (Smali 插桩 / Frida Console)。
- **抓包技术**:
  - HTTPS 抓包配置 (系统证书安装)。
  - VPN / Proxy 流量转发 (Postern, Drony)。
  - SSL Pinning 绕过 (Frida 脚本, JustTrustMe)。
