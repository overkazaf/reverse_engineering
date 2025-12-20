#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试中文字体在PDF中的显示
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
        <title>中文字体测试</title>
    </head>
    <body>
        <h1>### ❌问题 4: ⚠️Frida ⚠️使用</h1>
        <p>**问题**：⚠️如何⚠️配置Docker ⚠️环境**</p>
        <h2>测试标题 - 基础知识</h2>
        <p>这是一段中文测试文本。Android 逆向工程需要掌握多种工具。</p>
        <h3>1. Frida 动态插桩</h3>
        <p>Frida 是一个强大的动态插桩框架，支持 Android、iOS、Windows、macOS 等多个平台。</p>
        <pre><code># 安装 Frida
pip install frida frida-tools

# 查看设备上的进程
frida-ps -U</code></pre>
        <h3>2. 常用命令</h3>
        <ul>
            <li>列出所有应用：frida-ps -Ua</li>
            <li>附加到进程：frida -U -n com.example.app</li>
            <li>加载脚本：frida -U -l script.js -f com.example.app</li>
        </ul>
        <table>
            <tr>
                <th>工具</th>
                <th>描述</th>
                <th>特点</th>
            </tr>
            <tr>
                <td>Frida</td>
                <td>动态插桩工具</td>
                <td>支持多平台，功能强大</td>
            </tr>
            <tr>
                <td>Xposed</td>
                <td>Android Hook框架</td>
                <td>需要root权限</td>
            </tr>
        </table>
        <blockquote>
            注意：使用这些工具需要对目标应用有足够的了解，并且遵守相关法律法规。
        </blockquote>
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
    }

    h2 {
        font-size: 16pt;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 15pt;
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
    output_path = os.path.join(output_dir, "test_chinese_font.pdf")

    try:
        print("🚀 正在生成测试PDF...")
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
