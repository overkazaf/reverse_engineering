#!/usr/bin/env python3
"""
批量生成 Web 逆向工程文档框架
"""

import os
from pathlib import Path

# 定义文档结构
DOCS_STRUCTURE = {
    "00-Foundations": {
        "browser_architecture.md": "浏览器架构与渲染引擎",
        "dom_and_bom.md": "DOM 与 BOM",
        "webassembly_basics.md": "WebAssembly 基础",
        "cookie_and_storage.md": "Cookie 与 Storage",
        "cors_and_same_origin_policy.md": "CORS 与同源策略",
        "tls_ssl_handshake.md": "TLS/SSL 握手过程",
        "web_api_and_ajax.md": "Web API 与 Ajax",
    },
    "01-Tooling": {
        "browser_devtools.md": "浏览器开发者工具",
        "burp_suite_guide.md": "Burp Suite 指南",
        "fiddler_guide.md": "Fiddler 指南",
        "charles_guide.md": "Charles 指南",
        "wireshark_guide.md": "Wireshark 网络分析",
        "puppeteer_playwright.md": "Puppeteer 与 Playwright",
        "selenium_guide.md": "Selenium WebDriver",
        "ast_tools.md": "AST 解析工具",
        "nodejs_debugging.md": "Node.js 调试工具",
        "v8_tools.md": "V8 引擎工具",
    },
    "02-Techniques": {
        "re_workflow.md": "逆向工程工作流",
        "javascript_deobfuscation.md": "JavaScript 反混淆",
        "debugging_techniques.md": "调试技巧与断点设置",
        "crypto_identification.md": "加密算法识别与分析",
        "api_reverse_engineering.md": "API 接口逆向",
        "websocket_reversing.md": "WebSocket 逆向",
        "hooking_techniques.md": "Hook 技术",
        "dynamic_parameter_analysis.md": "动态参数生成分析",
        "captcha_bypass.md": "验证码识别与绕过",
        "browser_fingerprinting.md": "浏览器指纹识别",
    },
    "03-Advanced-Topics": {
        "javascript_vm_protection.md": "JavaScript 虚拟机保护",
        "webassembly_reversing.md": "WebAssembly 逆向",
        "anti_scraping_deep_dive.md": "反爬虫技术深度分析",
        "frontend_hardening.md": "前端加固技术",
        "csp_bypass.md": "CSP 绕过技术",
        "webrtc_fingerprinting.md": "WebRTC 指纹与隐私",
        "canvas_fingerprinting.md": "Canvas 指纹技术",
        "tls_fingerprinting.md": "TLS 指纹识别",
        "http2_http3.md": "HTTP/2 与 HTTP/3",
        "pwa_service_worker.md": "PWA 与 Service Worker",
    },
    "04-Engineering": {
        "distributed_scraping.md": "分布式爬虫架构",
        "proxy_pool_management.md": "代理池管理",
        "data_storage_solutions.md": "数据存储方案",
        "message_queue_application.md": "消息队列应用",
        "docker_deployment.md": "Docker 容器化部署",
        "monitoring_and_alerting.md": "监控与告警系统",
        "anti_anti_scraping_framework.md": "反爬虫对抗框架",
    },
    "05-Case-Studies": {
        "case_ecommerce.md": "电商网站逆向",
        "case_social_media.md": "社交媒体逆向",
        "case_financial.md": "金融网站逆向",
        "case_video_streaming.md": "视频网站逆向",
        "case_news_aggregator.md": "新闻聚合网站",
        "case_search_engine.md": "搜索引擎对抗",
    },
    "06-Scripts": {
        "javascript_hook_scripts.md": "JavaScript Hook 脚本",
        "deobfuscation_scripts.md": "反混淆脚本",
        "automation_scripts.md": "浏览器自动化脚本",
        "crypto_detection_scripts.md": "加密算法识别脚本",
    },
    "07-Others": {
        "github_projects.md": "开源项目推荐",
        "learning_resources.md": "学习资源",
        "faq.md": "常见问题 FAQ",
    }
}

def generate_doc_template(title, category):
    """生成文档模板"""
    template = f"""# {title}

## 概述

本文介绍 {title} 的相关知识和技术。

---

## 基础概念

### 定义

TODO: 添加定义和基本概念

### 核心原理

TODO: 添加核心原理说明

---

## 详细内容

### 主要特性

1. **特性1**
   - 说明1

2. **特性2**
   - 说明2

3. **特性3**
   - 说明3

---

## 实战示例

### 示例1

```javascript
// TODO: 添加代码示例
```

### 示例2

```javascript
// TODO: 添加代码示例
```

---

## 最佳实践

1. **实践1**: 说明
2. **实践2**: 说明
3. **实践3**: 说明

---

## 常见问题

### Q: 问题1

**A**: 答案1

### Q: 问题2

**A**: 答案2

---

## 进阶阅读

- 相关链接1
- 相关链接2

---

## 相关章节

- TODO: 添加相关章节链接
"""
    return template

def main():
    """主函数"""
    base_dir = Path(__file__).parent / "docs"

    for category, files in DOCS_STRUCTURE.items():
        category_dir = base_dir / category
        category_dir.mkdir(parents=True, exist_ok=True)

        for filename, title in files.items():
            filepath = category_dir / filename

            # 如果文件已存在，跳过
            if filepath.exists():
                print(f"跳过已存在的文件: {filepath}")
                continue

            # 生成文档内容
            content = generate_doc_template(title, category)

            # 写入文件
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"生成文件: {filepath}")

    print("\n文档框架生成完成!")

if __name__ == "__main__":
    main()
