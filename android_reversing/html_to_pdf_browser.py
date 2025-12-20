#!/usr/bin/env python3
"""
使用 Chromium/Chrome 的 headless 模式将 HTML 转为 PDF
"""

import os
import subprocess
import time

HTML_FILE = "output/temp_combined.html"
PDF_FILE = "output/Android_Reverse_Engineering_Cookbook.pdf"

def find_chrome():
    """查找 Chrome/Chromium 可执行文件"""
    possible_paths = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "/usr/bin/chromium-browser",
        "/usr/bin/google-chrome",
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    return None

def convert_html_to_pdf_with_chrome(html_file, pdf_file):
    """使用 Chrome headless 模式转换"""
    chrome_path = find_chrome()

    if not chrome_path:
        print("❌ 未找到 Chrome/Chromium")
        print("请安装 Google Chrome 或 Chromium")
        return False

    print(f"✅ 找到浏览器: {os.path.basename(os.path.dirname(chrome_path))}")

    # 转换为绝对路径
    abs_html = os.path.abspath(html_file)
    abs_pdf = os.path.abspath(pdf_file)

    print(f"\n🔨 转换 HTML 到 PDF...")
    print(f"   输入: {abs_html}")
    print(f"   输出: {abs_pdf}")

    cmd = [
        chrome_path,
        '--headless',
        '--disable-gpu',
        '--print-to-pdf=' + abs_pdf,
        '--print-to-pdf-no-header',
        f'file://{abs_html}'
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )

        # 等待文件生成
        time.sleep(2)

        if os.path.exists(abs_pdf) and os.path.getsize(abs_pdf) > 1000:
            size = os.path.getsize(abs_pdf) / (1024 * 1024)
            print(f"\n✅ PDF 生成成功!")
            print(f"📄 文件: {abs_pdf}")
            print(f"📏 大小: {size:.2f} MB")
            return True
        else:
            print(f"\n❌ PDF 生成失败")
            if result.stderr:
                print(f"错误: {result.stderr[:300]}")
            return False

    except subprocess.TimeoutExpired:
        print("❌ 转换超时")
        return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def main():
    print("="*70)
    print("📚 HTML 转 PDF (使用 Chrome Headless)")
    print("="*70)

    if not os.path.exists(HTML_FILE):
        print(f"\n❌ HTML 文件不存在: {HTML_FILE}")
        print("请先运行: python3 generate_pdf_ultimate.py")
        return

    success = convert_html_to_pdf_with_chrome(HTML_FILE, PDF_FILE)

    print("\n" + "="*70)
    if success:
        print("🎉 完成！")
        print(f"📄 PDF 已生成: {PDF_FILE}")
    else:
        print("❌ 转换失败")
        print("\n💡 备选方案:")
        print("1. 手动打印:")
        print(f"   open {HTML_FILE}")
        print("   然后使用浏览器的 打印→保存为PDF 功能")
        print("\n2. 使用在线工具:")
        print("   https://www.html2pdf.com/")
    print("="*70)

if __name__ == "__main__":
    main()
