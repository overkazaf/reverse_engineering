#!/usr/bin/env python3
"""
终极版 PDF 生成 - 使用 HTML 转 PDF
绕过 LaTeX 的特殊字符问题
"""

import os
import subprocess
import re

DOCS_DIR = "docs"
OUTPUT_DIR = "output"
OUTPUT_PDF = "Android_Reverse_Engineering_Cookbook.pdf"
OUTPUT_HTML = "temp_combined.html"

def get_file_order():
    """获取文件列表"""
    file_order = []
    dir_order = [
        "00-Quick-Start",
        "01-Recipes",
        "02-Tools",
        "03-Case-Studies",
        "04-Reference",
        "05-Appendix"
    ]

    for dir_name in dir_order:
        dir_path = os.path.join(DOCS_DIR, dir_name)
        if os.path.exists(dir_path):
            for root, dirs, files in os.walk(dir_path):
                dirs.sort()
                for file in sorted(files):
                    if file.endswith('.md') and file != 'summary.md':
                        file_order.append(os.path.join(root, file))

    index_file = os.path.join(DOCS_DIR, "index.md")
    if os.path.exists(index_file):
        file_order.insert(0, index_file)

    return file_order

def generate_html_from_markdown(files, output_html):
    """从 Markdown 生成 HTML"""
    print(f"\n📝 合并并生成 HTML...")

    # 创建临时 markdown 文件
    temp_md = os.path.join(OUTPUT_DIR, "temp_all.md")

    with open(temp_md, 'w', encoding='utf-8') as outfile:
        outfile.write("# Android Reverse Engineering Cookbook\n\n")
        outfile.write("完整的 Android 逆向工程学习和实战指南\n\n")
        outfile.write("---\n\n")

        for i, filepath in enumerate(files, 1):
            try:
                with open(filepath, 'r', encoding='utf-8') as infile:
                    content = infile.read()

                # 简单清理
                content = re.sub(r'^---$', '___', content, flags=re.MULTILINE)
                content = re.sub(r'^#\s+#', '##', content, flags=re.MULTILINE)

                rel_path = os.path.relpath(filepath, DOCS_DIR)
                outfile.write(f"\n<!-- {rel_path} -->\n\n")
                outfile.write(content)
                outfile.write("\n\n")

                print(f"  ✅ [{i}/{len(files)}] {rel_path}")
            except Exception as e:
                print(f"  ❌ {filepath}: {e}")

    # 使用 pandoc 转换为 HTML
    print("\n🔨 转换为 HTML...")

    cmd = [
        'pandoc',
        temp_md,
        '-o', output_html,
        '--standalone',
        '--toc',
        '--toc-depth=2',
        '--css=https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.1.0/github-markdown.min.css',
        '--highlight-style=tango',
        '--metadata', 'title=Android Reverse Engineering Cookbook',
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ HTML 生成成功: {output_html}")
        return True
    except Exception as e:
        print(f"❌ HTML 生成失败: {e}")
        return False

def convert_html_to_pdf_with_wkhtmltopdf(html_file, pdf_file):
    """使用 wkhtmltopdf 转换 HTML 到 PDF"""
    print(f"\n🔨 转换 HTML 到 PDF (使用 wkhtmltopdf)...")

    cmd = [
        'wkhtmltopdf',
        '--enable-local-file-access',
        '--margin-top', '20mm',
        '--margin-bottom', '20mm',
        '--margin-left', '20mm',
        '--margin-right', '20mm',
        '--footer-center', '[page]/[topage]',
        '--footer-font-size', '9',
        html_file,
        pdf_file
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if os.path.exists(pdf_file) and os.path.getsize(pdf_file) > 1000:
            size = os.path.getsize(pdf_file) / (1024 * 1024)
            print(f"✅ PDF 生成成功: {pdf_file}")
            print(f"📏 文件大小: {size:.2f} MB")
            return True
        else:
            print("❌ PDF 生成失败")
            if result.stderr:
                print(result.stderr[:500])
            return False
    except FileNotFoundError:
        print("❌ 未找到 wkhtmltopdf")
        print("请安装: brew install wkhtmltopdf")
        return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def convert_html_to_pdf_with_prince(html_file, pdf_file):
    """使用 prince 转换（商业工具，效果最好）"""
    print(f"\n🔨 转换 HTML 到 PDF (使用 Prince)...")

    cmd = ['prince', html_file, '-o', pdf_file]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=600)
        size = os.path.getsize(pdf_file) / (1024 * 1024)
        print(f"✅ PDF 生成成功: {pdf_file}")
        print(f"📏 文件大小: {size:.2f} MB")
        return True
    except FileNotFoundError:
        return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def convert_html_to_pdf_with_pandoc(html_file, pdf_file):
    """使用 pandoc 直接从 HTML 生成 PDF"""
    print(f"\n🔨 转换 HTML 到 PDF (使用 pandoc)...")

    env = os.environ.copy()
    for tex_path in [
        "/usr/local/texlive/2025/bin/universal-darwin",
        "/usr/local/texlive/2024/bin/universal-darwin",
    ]:
        if os.path.exists(tex_path):
            env['PATH'] = f"{tex_path}:{env.get('PATH', '')}"
            break

    cmd = [
        'pandoc',
        html_file,
        '-o', pdf_file,
        '--pdf-engine=wkhtmltopdf',
        '-V', 'margin-top=20mm',
        '-V', 'margin-bottom=20mm',
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=600)
        if os.path.exists(pdf_file) and os.path.getsize(pdf_file) > 1000:
            size = os.path.getsize(pdf_file) / (1024 * 1024)
            print(f"✅ PDF 生成成功: {pdf_file}")
            print(f"📏 文件大小: {size:.2f} MB")
            return True
        return False
    except Exception as e:
        return False

def main():
    print("="*70)
    print("📚 PDF 生成器 - 终极版 (HTML路径)")
    print("="*70)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 获取文件
    print("\n📂 扫描文件...")
    files = get_file_order()
    print(f"找到 {len(files)} 个文件")

    # 生成 HTML
    html_path = os.path.join(OUTPUT_DIR, OUTPUT_HTML)
    if not generate_html_from_markdown(files, html_path):
        print("\n❌ HTML 生成失败，退出")
        return

    # 尝试多种转换方法
    pdf_path = os.path.join(OUTPUT_DIR, OUTPUT_PDF)

    print("\n" + "="*70)
    print("🔄 尝试转换 HTML 到 PDF...")
    print("="*70)

    # 方法 1: Prince (最好但需要安装)
    if convert_html_to_pdf_with_prince(html_path, pdf_path):
        print("\n🎉 成功！使用了 Prince")
        return

    # 方法 2: wkhtmltopdf
    if convert_html_to_pdf_with_wkhtmltopdf(html_path, pdf_path):
        print("\n🎉 成功！使用了 wkhtmltopdf")
        return

    # 方法 3: pandoc with wkhtmltopdf
    if convert_html_to_pdf_with_pandoc(html_path, pdf_path):
        print("\n🎉 成功！使用了 pandoc")
        return

    # 都失败了
    print("\n" + "="*70)
    print("⚠️  所有转换方法都失败了")
    print("="*70)
    print(f"\n✅ HTML 文件已生成: {html_path}")
    print("你可以:")
    print("1. 在浏览器中打开 HTML 并打印为 PDF")
    print(f"   open {html_path}")
    print("\n2. 安装 wkhtmltopdf 后重试:")
    print("   brew install wkhtmltopdf")
    print(f"   wkhtmltopdf {html_path} {pdf_path}")

if __name__ == "__main__":
    main()
