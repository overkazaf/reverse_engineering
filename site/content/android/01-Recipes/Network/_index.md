---
title: "网络分析"
date: 2025-03-14
tags: ["网络分析", "加密", "Android", "抓包"]
weight: 30
---

本节聚焦 Android 应用的网络层安全分析，涵盖流量抓包、加密密钥提取以及 TLS 指纹识别与绕过技术。掌握这些技术是理解应用通信协议和突破传输层防护的关键。

## 章节导航

### 流量捕获与加密分析
- [抓包分析 Android 应用的网络流量](network_sniffing) - 网络抓包的环境搭建、证书安装与常见问题排查
- [分析并提取 Android 应用的加密密钥](crypto_analysis) - 定位并提取应用运行时使用的加密密钥

### TLS 指纹识别
- [JA3 TLS 指纹识别技术详解](ja3_fingerprinting) - JA3 指纹的原理、生成方式与检测应用
- [JA4+ TLS/QUIC 指纹识别技术详解](ja4_fingerprinting) - 新一代 JA4+ 指纹体系的技术细节与实践
- [使用 TLS 指纹识别检测和绕过应用指纹](tls_fingerprinting_guide) - TLS 指纹的检测机制与绕过策略
