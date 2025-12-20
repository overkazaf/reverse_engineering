#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试中文字体在PDF中的显示 - Web RE版本
"""

from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
import os

def test_chinese_font():
    """测试中文字体渲染"""
    font_config = FontConfiguration()

    # 创建测试HTML
    html_content = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <title>中文字体测试 - Web RE</title>
    </head>
    <body>
        <h1>Web 逆向工程中文测试</h1>
        <p>**问题**：⚠️如何⚠️配置浏览器开发者工具**</p>
        <h2>测试标题 - 基础知识</h2>
        <p>这是一段中文测试文本。Web 逆向工程需要掌握浏览器、JavaScript、网络协议等多种技术。</p>
        <h3>1. Burp Suite 使用指南</h3>
        <p>Burp Suite 是一个强大的 Web 应用安全测试平台，广泛用于渗透测试和安全研究。</p>
        <pre><code># 启动 Burp Suite
java -jar burpsuite.jar

# 配置代理
# 浏览器设置 -> 网络 -> 代理服务器
# HTTP: localhost:8080</code></pre>
        <h3>2. Chrome DevTools 调试技巧</h3>
        <ul>
            <li>Elements：查看和修改DOM结构</li>
            <li>Console：执行JavaScript代码</li>
            <li>Network：监控网络请求</li>
            <li>Sources：断点调试JavaScript</li>
        </ul>
        <table>
            <tr>
                <th>工具</th>
                <th>描述</th>
                <th>特点</th>
            </tr>
            <tr>
                <td>Burp Suite</td>
                <td>Web安全测试平台</td>
                <td>功能强大，插件丰富</td>
            </tr>
            <tr>
                <td>Chrome DevTools</td>
                <td>浏览器开发工具</td>
                <td>内置强大，使用方便</td>
            </tr>
            <tr>
                <td>Puppeteer</td>
                <td>无头浏览器控制</td>
                <td>自动化测试</td>
            </tr>
        </table>
        <blockquote>
            注意：使用这些工具需要对Web技术有足够的了解，并且遵守相关法律法规。
        </blockquote>
        <h3>3. JavaScript混淆与反混淆</h3>
        <p>JavaScript代码可能经过混淆处理，需要使用反混淆工具来理解其逻辑。</p>
        <pre><code>// 混淆后的代码示例
var _0x1234=['log','测试','Hello'];
(function(_0xabcd,_0xef01){
    var _0x2345=function(_0x3456){
        while(--_0x3456){
            _0xabcd['push'](_0xabcd['shift']());
        }
    };
    _0x2345(++_0xef01);
}(_0x1234,0x123));

// 反混淆工具
// - de4js.com
// - beautifier.io
// - AST 分析工具</code></pre>
    </body>
    </html>
    """

    # 创建CSS样式
    css_content = """
    /* 使用系统字体确保中文正确显示 */
    @font-face {
        font-family: 'Chinese Sans';
        src: url('file:///System/Library/Fonts/Hiragino Sans GB.ttc') format('truetype'),
             url('file:///System/Library/Fonts/STHeiti Light.ttc') format('truetype'),
             url('file:///System/Library/Fonts/Supplemental/Songti.ttc') format('truetype'),
             url('file:///Library/Fonts/Arial Unicode.ttf') format('truetype');
        font-weight: normal;
    }

    @font-face {
        font-family: 'Chinese Sans';
        src: url('file:///System/Library/Fonts/Hiragino Sans GB.ttc') format('truetype'),
             url('file:///System/Library/Fonts/STHeiti Medium.ttc') format('truetype');
        font-weight: bold;
    }

    body {
        font-family: 'Chinese Sans', sans-serif;
        font-size: 12pt;
        line-height: 1.6;
        margin: 2cm;
    }

    h1 {
        font-size: 20pt;
        font-weight: bold;
        color: #1a1a1a;
        margin-top: 20pt;
        border-bottom: 3px solid #4CAF50;
        padding-bottom: 10pt;
    }

    h2 {
        font-size: 16pt;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 15pt;
        border-left: 4px solid #4CAF50;
        padding-left: 15pt;
    }

    h3 {
        font-size: 14pt;
        font-weight: bold;
        color: #34495e;
        margin-top: 12pt;
    }

    pre {
        background-color: #f8f9fa;
        padding: 10pt;
        border-radius: 4pt;
        font-family: 'Chinese Sans', monospace;
        font-size: 10pt;
        white-space: pre-wrap;
        word-wrap: break-word;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        margin: 15pt 0;
    }

    th, td {
        border: 1px solid #ddd;
        padding: 8pt;
        text-align: left;
    }

    th {
        background-color: #f8f9fa;
        font-weight: bold;
    }

    blockquote {
        border-left: 4px solid #6c757d;
        padding-left: 15pt;
        margin: 15pt 0;
        color: #6c757d;
        font-style: italic;
    }
    """

    css = CSS(string=css_content, font_config=font_config)

    # 生成PDF
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "test_chinese_font_web.pdf")

    try:
        print("🚀 正在生成Web RE测试PDF...")
        html_doc = HTML(string=html_content)
        html_doc.write_pdf(
            output_path,
            stylesheets=[css],
            font_config=font_config
        )

        file_size = os.path.getsize(output_path) / 1024
        print(f"✅ 测试PDF生成成功!")
        print(f"📁 文件路径: {output_path}")
        print(f"📊 文件大小: {file_size:.2f} KB")
        print("\n请打开PDF文件检查中文是否正常显示。")

        return output_path
    except Exception as e:
        print(f"❌ 生成失败: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_chinese_font()
