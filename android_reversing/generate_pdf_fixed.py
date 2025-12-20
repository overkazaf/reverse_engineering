#!/usr/bin/env python3
"""
修复版 PDF 生成脚本
解决 YAML 解析、图片链接和 LaTeX 特殊字符问题
"""

import os
import subprocess
import re
from pathlib import Path

# 配置
DOCS_DIR = "docs"
OUTPUT_DIR = "output"
OUTPUT_PDF = "Android_Reverse_Engineering_Cookbook.pdf"
TEMP_MD = "temp_combined_fixed.md"

def get_file_order():
    """获取文件顺序（按目录结构）"""
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

    # 添加 index.md
    index_file = os.path.join(DOCS_DIR, "index.md")
    if os.path.exists(index_file):
        file_order.insert(0, index_file)

    return file_order

def fix_markdown_content(content):
    """修复 Markdown 内容中的问题"""

    # 1. 移除可能导致问题的 emoji 和特殊 Unicode 字符
    # content = re.sub(r'[^\x00-\x7F\u4e00-\u9fff]+', '', content)

    # 2. 转义 LaTeX 特殊字符（在代码块外）
    def escape_latex_outside_code(text):
        """在代码块外转义 LaTeX 特殊字符"""
        # 分离代码块
        parts = []
        current_pos = 0
        in_code_block = False

        for match in re.finditer(r'```', text):
            # 添加代码块之前的内容
            if not in_code_block:
                before = text[current_pos:match.start()]
                # 转义特殊字符
                before = before.replace('\\', '\\\\')
                before = before.replace('$', '\\$')
                before = before.replace('%', '\\%')
                before = before.replace('&', '\\&')
                before = before.replace('#', '\\#')
                before = before.replace('_', '\\_')
                before = before.replace('{', '\\{')
                before = before.replace('}', '\\}')
                parts.append(before)
            else:
                # 代码块内容不转义
                parts.append(text[current_pos:match.start()])

            parts.append('```')
            current_pos = match.end()
            in_code_block = not in_code_block

        # 添加剩余内容
        if not in_code_block:
            remaining = text[current_pos:]
            remaining = remaining.replace('\\', '\\\\')
            remaining = remaining.replace('$', '\\$')
            remaining = remaining.replace('%', '\\%')
            remaining = remaining.replace('&', '\\&')
            remaining = remaining.replace('#', '\\#')
            remaining = remaining.replace('_', '\\_')
            remaining = remaining.replace('{', '\\{')
            remaining = remaining.replace('}', '\\}')
            parts.append(remaining)
        else:
            parts.append(text[current_pos:])

        return ''.join(parts)

    # 暂时不转义，因为可能导致更多问题
    # content = escape_latex_outside_code(content)

    # 3. 修复水平分割线（避免被误认为 YAML）
    # 将单独一行的 --- 替换为 ___
    content = re.sub(r'^---$', '___', content, flags=re.MULTILINE)

    # 4. 移除失效的图片引用（404的链接）
    # 常见的失效图片
    invalid_images = [
        r'!\[.*?\]\(https://frida\.re/static/images/.*?\)',
        r'!\[.*?\]\(\.\.\/\.\.\/images/burp_proxy_config\.png\)',
    ]
    for pattern in invalid_images:
        content = re.sub(pattern, '', content)

    # 5. 修复可能导致问题的标题格式
    content = re.sub(r'^#\s+#', '##', content, flags=re.MULTILINE)

    return content

def combine_markdown_files(files, output_file):
    """合并 Markdown 文件"""
    print(f"\n📝 合并 {len(files)} 个文件...")

    with open(output_file, 'w', encoding='utf-8') as outfile:
        # 写入简化的 YAML 头（避免解析问题）
        outfile.write("---\n")
        outfile.write("title: \"Android Reverse Engineering Cookbook\"\n")
        outfile.write("author: \"Android RE Team\"\n")
        outfile.write("date: \"2025-12-19\"\n")
        outfile.write("documentclass: book\n")
        outfile.write("papersize: a4\n")
        outfile.write("geometry: margin=2.5cm\n")
        outfile.write("---\n\n")

        # 添加标题页
        outfile.write("\\begin{titlepage}\n")
        outfile.write("\\centering\n")
        outfile.write("\\vspace*{5cm}\n")
        outfile.write("{\\Huge\\bfseries Android Reverse Engineering Cookbook\\par}\n")
        outfile.write("\\vspace{2cm}\n")
        outfile.write("{\\Large 完整的 Android 逆向工程学习和实战指南\\par}\n")
        outfile.write("\\vfill\n")
        outfile.write("{\\large 2025-12-19\\par}\n")
        outfile.write("\\end{titlepage}\n\n")

        outfile.write("\\newpage\n\n")
        outfile.write("\\tableofcontents\n\n")
        outfile.write("\\newpage\n\n")

        for i, filepath in enumerate(files, 1):
            try:
                with open(filepath, 'r', encoding='utf-8') as infile:
                    content = infile.read()

                # 修复内容
                content = fix_markdown_content(content)

                rel_path = os.path.relpath(filepath, DOCS_DIR)
                outfile.write(f"\n<!-- 文件: {rel_path} -->\n\n")
                outfile.write(content)

                if i < len(files):
                    outfile.write("\n\n\\newpage\n\n")

                print(f"  ✅ [{i}/{len(files)}] {rel_path}")

            except Exception as e:
                print(f"  ❌ 读取失败 {filepath}: {e}")
                continue

    print(f"\n✅ 合并完成: {output_file}")
    return output_file

def generate_pdf_with_pandoc(md_file, pdf_file):
    """使用 Pandoc 生成 PDF"""
    print(f"\n🔨 生成 PDF: {pdf_file}")

    # 添加 TeX 路径
    env = os.environ.copy()
    tex_path = "/usr/local/texlive/2025/bin/universal-darwin"
    if os.path.exists(tex_path):
        env['PATH'] = f"{tex_path}:{env.get('PATH', '')}"
    else:
        tex_path = "/usr/local/texlive/2024/bin/universal-darwin"
        if os.path.exists(tex_path):
            env['PATH'] = f"{tex_path}:{env.get('PATH', '')}"

    # Pandoc 命令
    cmd = [
        'pandoc',
        md_file,
        '-o', pdf_file,
        '--pdf-engine=xelatex',
        '--toc',
        '--toc-depth=2',
        '--number-sections',
        # 中文字体支持
        '-V', 'CJKmainfont=PingFang SC',
        '-V', 'mainfont=PingFang SC',
        # 代码字体
        '-V', 'monofont=Menlo',
        # 页面设置
        '-V', 'fontsize=11pt',
        '-V', 'linestretch=1.2',
        # 代码高亮
        '--highlight-style=tango',
        # 其他选项
        '--standalone',
        '--from=markdown',
        '--fail-if-warnings=false',
    ]

    try:
        print("  执行 pandoc 命令...")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=env,
            timeout=600  # 10分钟超时
        )

        if result.returncode == 0:
            print(f"✅ PDF 生成成功: {pdf_file}")

            # 显示文件大小
            if os.path.exists(pdf_file):
                size = os.path.getsize(pdf_file) / (1024 * 1024)
                print(f"📏 文件大小: {size:.2f} MB")

            return True
        else:
            print(f"❌ PDF 生成失败:")
            if result.stderr:
                # 只显示错误的前20行
                error_lines = result.stderr.split('\n')[:20]
                print('\n'.join(error_lines))
                if len(result.stderr.split('\n')) > 20:
                    print(f"... 还有 {len(result.stderr.split('\n')) - 20} 行错误信息")
            return False

    except subprocess.TimeoutExpired:
        print("❌ PDF 生成超时（10分钟）")
        return False
    except FileNotFoundError:
        print("❌ 未找到 pandoc 命令")
        print("请安装: brew install pandoc")
        return False
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        return False

def main():
    print("="*70)
    print("📚 Android 逆向工程 Cookbook PDF 生成器（修复版）")
    print("="*70)

    # 创建输出目录
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 获取文件列表
    print("\n📂 扫描文件...")
    files = get_file_order()
    print(f"找到 {len(files)} 个文件")

    # 合并文件
    temp_md_path = os.path.join(OUTPUT_DIR, TEMP_MD)
    combine_markdown_files(files, temp_md_path)

    # 检查合并文件大小
    md_size = os.path.getsize(temp_md_path) / 1024
    print(f"📄 合并文件大小: {md_size:.1f} KB")

    # 生成 PDF
    pdf_path = os.path.join(OUTPUT_DIR, OUTPUT_PDF)
    success = generate_pdf_with_pandoc(temp_md_path, pdf_path)

    print("\n" + "="*70)
    if success:
        print("🎉 完成！")
        print(f"📄 PDF 文件: {pdf_path}")
        print(f"📝 临时 Markdown: {temp_md_path}")
    else:
        print("❌ PDF 生成失败")
        print(f"💡 你可以查看合并的 Markdown: {temp_md_path}")
        print("\n可能的解决方案:")
        print("1. 检查是否安装了 xelatex: which xelatex")
        print("2. 检查中文字体: fc-list | grep 'PingFang'")
        print("3. 查看详细错误信息在上面的输出中")
    print("="*70)

if __name__ == "__main__":
    main()
