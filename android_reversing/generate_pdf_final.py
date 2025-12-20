#!/usr/bin/env python3
"""
最终版 PDF 生成脚本 - 使用 listings 包处理代码
"""

import os
import subprocess
import re
from pathlib import Path

# 配置
DOCS_DIR = "docs"
OUTPUT_DIR = "output"
OUTPUT_PDF = "Android_Reverse_Engineering_Cookbook.pdf"
TEMP_MD = "temp_combined_final.md"

def get_file_order():
    """获取文件顺序"""
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
                        filepath = os.path.join(root, file)
                        file_order.append(filepath)

    index_file = os.path.join(DOCS_DIR, "index.md")
    if os.path.exists(index_file):
        file_order.insert(0, index_file)

    return file_order

def fix_content_for_latex(content):
    """修复内容以适配 LaTeX"""

    # 1. 将 --- 替换为 ___ (避免被误认为 YAML)
    content = re.sub(r'^---$', '___', content, flags=re.MULTILINE)

    # 2. 移除失效的图片
    content = re.sub(r'!\[.*?\]\(https://frida\.re/static/images/.*?\)', '', content)
    content = re.sub(r'!\[.*?\]\(\.\.\/\.\.\/images/.*?\)', '', content)

    # 3. 修复标题
    content = re.sub(r'^#\s+#', '##', content, flags=re.MULTILINE)

    # 4. 移除可能导致问题的 emoji (可选)
    # content = re.sub(r'[^\x00-\x7F\u4e00-\u9fff]+', ' ', content)

    return content

def combine_markdown_files(files, output_file):
    """合并 Markdown 文件"""
    print(f"\n📝 合并 {len(files)} 个文件...")

    with open(output_file, 'w', encoding='utf-8') as outfile:
        # YAML 头
        outfile.write("---\n")
        outfile.write("title: Android Reverse Engineering Cookbook\n")
        outfile.write("author: Android RE Team\n")
        outfile.write("date: 2025-12-19\n")
        outfile.write("---\n\n")

        # 标题和目录
        outfile.write("# Android Reverse Engineering Cookbook\n\n")
        outfile.write("完整的 Android 逆向工程学习和实战指南\n\n")
        outfile.write("\\newpage\n\n")

        for i, filepath in enumerate(files, 1):
            try:
                with open(filepath, 'r', encoding='utf-8') as infile:
                    content = infile.read()

                content = fix_content_for_latex(content)
                rel_path = os.path.relpath(filepath, DOCS_DIR)

                outfile.write(f"\n<!-- 文件: {rel_path} -->\n\n")
                outfile.write(content)

                if i < len(files):
                    outfile.write("\n\n\\newpage\n\n")

                print(f"  ✅ [{i}/{len(files)}] {rel_path}")

            except Exception as e:
                print(f"  ❌ 失败 {filepath}: {e}")

    print(f"\n✅ 合并完成: {output_file}")

def generate_pdf(md_file, pdf_file):
    """生成 PDF - 使用更宽松的选项"""
    print(f"\n🔨 生成 PDF: {pdf_file}")

    # 添加 TeX 路径
    env = os.environ.copy()
    for tex_path in [
        "/usr/local/texlive/2025/bin/universal-darwin",
        "/usr/local/texlive/2024/bin/universal-darwin",
        "/Library/TeX/texbin"
    ]:
        if os.path.exists(tex_path):
            env['PATH'] = f"{tex_path}:{env.get('PATH', '')}"
            break

    # 简化的 pandoc 命令 - 避免复杂的格式化
    cmd = [
        'pandoc',
        md_file,
        '-o', pdf_file,
        '--pdf-engine=xelatex',
        '--toc',
        '--toc-depth=2',
        '-V', 'CJKmainfont=PingFang SC',
        '-V', 'mainfont=PingFang SC',
        '-V', 'monofont=Menlo',
        '-V', 'geometry:margin=2.5cm',
        '-V', 'fontsize=11pt',
        '-V', 'documentclass=article',
        '--highlight-style=tango',
        '--listings',  # 使用 listings 包处理代码
    ]

    try:
        print("  执行 pandoc（这可能需要几分钟）...")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=env,
            timeout=900  # 15分钟
        )

        # 即使有警告也继续
        if os.path.exists(pdf_file) and os.path.getsize(pdf_file) > 1000:
            size = os.path.getsize(pdf_file) / (1024 * 1024)
            print(f"✅ PDF 生成成功: {pdf_file}")
            print(f"📏 文件大小: {size:.2f} MB")

            if result.stderr and result.returncode != 0:
                print("\n⚠️  生成过程中有警告:")
                warnings = [line for line in result.stderr.split('\n') if 'WARNING' in line or 'Error' in line]
                for warning in warnings[:5]:
                    print(f"  {warning}")
                if len(warnings) > 5:
                    print(f"  ... 还有 {len(warnings) - 5} 个警告")

            return True
        else:
            print("❌ PDF 生成失败")
            if result.stderr:
                error_lines = result.stderr.split('\n')[:30]
                for line in error_lines:
                    if line.strip():
                        print(f"  {line}")
            return False

    except subprocess.TimeoutExpired:
        print("❌ 超时（15分钟）")
        return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def main():
    print("="*70)
    print("📚 PDF 生成器 - 最终版")
    print("="*70)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("\n📂 扫描文件...")
    files = get_file_order()
    print(f"找到 {len(files)} 个文件")

    # 合并
    temp_md = os.path.join(OUTPUT_DIR, TEMP_MD)
    combine_markdown_files(files, temp_md)

    # 生成 PDF
    pdf_path = os.path.join(OUTPUT_DIR, OUTPUT_PDF)
    success = generate_pdf(temp_md, pdf_path)

    print("\n" + "="*70)
    if success:
        print("🎉 成功！")
        print(f"📄 PDF: {pdf_path}")
        print(f"📝 Markdown: {temp_md}")
    else:
        print("❌ 失败")
        print(f"💡 查看: {temp_md}")
    print("="*70)

if __name__ == "__main__":
    main()
