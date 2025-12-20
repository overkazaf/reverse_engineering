#!/usr/bin/env python3
"""
生成 Android 逆向工程 PDF Cookbook
"""

import os
import subprocess
import re
from pathlib import Path
import json

# 配置
DOCS_DIR = "docs"
OUTPUT_DIR = "output"
OUTPUT_PDF = "Android_Reverse_Engineering_Cookbook.pdf"
TEMP_MD = "temp_combined.md"

# Recipe 编号映射 (文件路径 -> 编号)
RECIPE_NUMBERS = {
    # Network
    "01-Recipes/Network/network_sniffing.md": "R01",
    "01-Recipes/Network/crypto_analysis.md": "R02",
    "01-Recipes/Network/tls_fingerprinting_guide.md": "R03",
    "01-Recipes/Network/ja3_fingerprinting.md": "R04",
    "01-Recipes/Network/ja4_fingerprinting.md": "R05",
    # Anti-Detection
    "01-Recipes/Anti-Detection/frida_anti_debugging.md": "R06",
    "01-Recipes/Anti-Detection/xposed_anti_debugging.md": "R07",
    "01-Recipes/Anti-Detection/captcha_bypassing_techniques.md": "R08",
    "01-Recipes/Anti-Detection/app_hardening_identification.md": "R09",
    "01-Recipes/Anti-Detection/device_fingerprinting_and_bypass.md": "R10",
    "01-Recipes/Anti-Detection/mobile_app_sec_and_anti_bot.md": "R11",
    # Unpacking
    "01-Recipes/Unpacking/un-packing.md": "R12",
    "01-Recipes/Unpacking/frida_unpacking_and_so_fixing.md": "R13",
    "01-Recipes/Unpacking/so_obfuscation_deobfuscation.md": "R14",
    "01-Recipes/Unpacking/so_string_deobfuscation.md": "R15",
    # Analysis
    "01-Recipes/Analysis/re_workflow.md": "R16",
    "01-Recipes/Analysis/static_analysis_deep_dive.md": "R17",
    "01-Recipes/Analysis/dynamic_analysis_deep_dive.md": "R18",
    "01-Recipes/Analysis/ollvm_deobfuscation.md": "R19",
    "01-Recipes/Analysis/vmp_analysis.md": "R20",
    "01-Recipes/Analysis/js_obfuscator.md": "R21",
    "01-Recipes/Analysis/js_vmp.md": "R22",
    "01-Recipes/Analysis/native_string_obfuscation.md": "R23",
    # Automation
    "01-Recipes/Automation/automation_and_device_farming.md": "R24",
    "01-Recipes/Automation/dial_up_proxy_pools.md": "R25",
    "01-Recipes/Automation/proxy_pool_design.md": "R26",
    "01-Recipes/Automation/scrapy.md": "R27",
    "01-Recipes/Automation/scrapy_redis_distributed.md": "R28",
    "01-Recipes/Automation/docker_deployment.md": "R29",
    "01-Recipes/Automation/virtualization_and_containers.md": "R30",
    "01-Recipes/Automation/web_anti_scraping.md": "R31",
    # Scripts
    "01-Recipes/Scripts/frida_script_examples.md": "R32",
    "01-Recipes/Scripts/frida_common_scripts.md": "R33",
    "01-Recipes/Scripts/automation_scripts.md": "R34",
    "01-Recipes/Scripts/native_hooking.md": "R35",
    "01-Recipes/Scripts/objection_snippets.md": "R36",
    "01-Recipes/Scripts/c_for_emulation.md": "R37",
}

def add_recipe_number(content, rel_path):
    """给 Recipe 内容的标题添加编号前缀"""
    if rel_path in RECIPE_NUMBERS:
        recipe_num = RECIPE_NUMBERS[rel_path]
        # 匹配第一个一级标题 (# xxx)
        pattern = r'^(#\s+)(.+)$'
        def replace_title(match):
            return f"{match.group(1)}{recipe_num}: {match.group(2)}"
        # 只替换第一个匹配
        content = re.sub(pattern, replace_title, content, count=1, flags=re.MULTILINE)
    return content

def get_file_order():
    """获取文件顺序（按目录结构）"""
    file_order = []

    # 定义目录顺序
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
            # 递归获取所有 md 文件
            for root, dirs, files in os.walk(dir_path):
                # 排序目录
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

def combine_markdown_files(files, output_file):
    """合并 Markdown 文件"""
    print(f"\n📝 合并 {len(files)} 个文件...")

    with open(output_file, 'w', encoding='utf-8') as outfile:
        # 写入标题页
        outfile.write("---\n")
        outfile.write("title: Android Reverse Engineering Cookbook\n")
        outfile.write("author: +5, Gemini Pro 3.0, Claude Code Opus 4.5\n")
        outfile.write("date: 2025-12-19\n")
        outfile.write("---\n\n")

        outfile.write("# Android Reverse Engineering Cookbook\n\n")
        outfile.write("完整的 Android 逆向工程学习和实战指南\n\n")
        outfile.write("---\n\n")
        outfile.write("\\newpage\n\n")

        for i, filepath in enumerate(files, 1):
            try:
                with open(filepath, 'r', encoding='utf-8') as infile:
                    content = infile.read()

                    # 获取相对路径
                    rel_path = os.path.relpath(filepath, DOCS_DIR)

                    # 给 Recipe 添加编号
                    content = add_recipe_number(content, rel_path)

                    outfile.write(f"\n<!-- 文件: {rel_path} -->\n\n")

                    # 写入内容
                    outfile.write(content)

                    # 添加分页
                    if i < len(files):
                        outfile.write("\n\n\\newpage\n\n")

                print(f"  ✅ [{i}/{len(files)}] {rel_path}")

            except Exception as e:
                print(f"  ❌ 读取文件失败 {filepath}: {e}")
                continue

def generate_pdf_with_pandoc(md_file, pdf_file):
    """使用 Pandoc 生成 PDF"""
    print(f"\n🔨 生成 PDF: {pdf_file}")

    # 添加 TeX 路径到环境变量
    import os
    env = os.environ.copy()
    tex_path = "/usr/local/texlive/2025/bin/universal-darwin"
    if os.path.exists(tex_path):
        env['PATH'] = f"{tex_path}:{env.get('PATH', '')}"

    # Pandoc 命令
    cmd = [
        'pandoc',
        md_file,
        '-o', pdf_file,
        '--pdf-engine=xelatex',
        '--toc',  # 目录
        '--toc-depth=3',
        '--number-sections',  # 章节编号
        '-V', 'geometry:margin=1in',
        '-V', 'documentclass=book',
        '-V', 'papersize=a4',
        '-V', 'fontsize=11pt',
        # 中文字体支持
        '-V', 'CJKmainfont=PingFang SC',
        '-V', 'CJKsansfont=PingFang SC',
        '-V', 'CJKmonofont=Menlo',
        # 代码高亮 (新语法)
        '--highlight-style=tango',
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, env=env)
        print(f"✅ PDF 生成成功: {pdf_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ PDF 生成失败:")
        print(f"错误: {e.stderr}")
        return False
    except FileNotFoundError:
        print("❌ 未找到 pandoc 命令")
        print("请安装 Pandoc: brew install pandoc")
        print("还需要安装: brew install basictex")
        return False

def main():
    print("="*70)
    print("📚 Android 逆向工程 Cookbook PDF 生成器")
    print("="*70)

    # 创建输出目录
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 获取文件列表
    print("\n📂 扫描文件...")
    files = get_file_order()
    print(f"找到 {len(files)} 个 Markdown 文件")

    # 合并文件
    temp_md_path = os.path.join(OUTPUT_DIR, TEMP_MD)
    combine_markdown_files(files, temp_md_path)

    # 生成 PDF
    pdf_path = os.path.join(OUTPUT_DIR, OUTPUT_PDF)
    success = generate_pdf_with_pandoc(temp_md_path, pdf_path)

    if success:
        print(f"\n🎉 完成！")
        print(f"📄 PDF 文件: {pdf_path}")

        # 获取文件大小
        file_size = os.path.getsize(pdf_path) / (1024 * 1024)  # MB
        print(f"📏 文件大小: {file_size:.2f} MB")

        # 保留临时文件以便检查
        print(f"📝 临时 Markdown: {temp_md_path}")
    else:
        print(f"\n❌ PDF 生成失败")
        print(f"💡 你仍然可以查看合并的 Markdown 文件: {temp_md_path}")

    print("\n" + "="*70)

if __name__ == "__main__":
    main()
