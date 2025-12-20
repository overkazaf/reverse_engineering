#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复 Markdown 文件中的 HTML 注释，避免 PDF 转换时出现乱码
"""

import os
import re
from pathlib import Path

def fix_html_comments(content):
    """
    将 HTML 注释转换为更友好的格式

    策略：
    1. 代码块中的注释保持原样（已经在 ``` 中）
    2. 独立行的注释改为普通文本（去掉 <!-- -->）
    3. 行内注释改为 `注释内容` 格式
    """

    # 分割内容为行
    lines = content.split('\n')
    result_lines = []
    in_code_block = False

    for line in lines:
        # 检测代码块
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            result_lines.append(line)
            continue

        # 如果在代码块中，不处理
        if in_code_block:
            result_lines.append(line)
            continue

        # 处理 HTML 注释
        # 情况1: 独立行的注释（整行只有注释）
        if re.match(r'^\s*<!--.*-->\s*$', line):
            # 提取注释内容
            match = re.search(r'<!--\s*(.*?)\s*-->', line)
            if match:
                comment_text = match.group(1)
                # 转换为普通文本（保持缩进）
                indent = re.match(r'^(\s*)', line).group(1)
                result_lines.append(f"{indent}**{comment_text}**")
            else:
                result_lines.append(line)

        # 情况2: 行内包含注释
        elif '<!--' in line and '-->' in line:
            # 将 HTML 注释改为行内代码格式
            fixed_line = re.sub(r'<!--\s*(.*?)\s*-->', r'`\1`', line)
            result_lines.append(fixed_line)

        else:
            result_lines.append(line)

    return '\n'.join(result_lines)

def process_file(file_path):
    """处理单个文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查是否包含 HTML 注释
        if '<!--' not in content:
            return False

        # 修复注释
        fixed_content = fix_html_comments(content)

        # 如果内容有变化，写回文件
        if fixed_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)

            # 统计修改了多少注释
            original_comments = len(re.findall(r'<!--.*?-->', content))
            remaining_comments = len(re.findall(r'<!--.*?-->', fixed_content))
            print(f"✓ {file_path}: 修复了 {original_comments - remaining_comments} 个注释")
            return True

        return False

    except Exception as e:
        print(f"✗ {file_path}: 处理失败 - {e}")
        return False

def main():
    """主函数"""
    docs_dir = Path('docs')

    if not docs_dir.exists():
        print("错误: docs 目录不存在")
        return

    # 查找所有 Markdown 文件
    md_files = list(docs_dir.rglob('*.md'))

    print(f"找到 {len(md_files)} 个 Markdown 文件")
    print("开始修复 HTML 注释...\n")

    processed_count = 0

    for md_file in md_files:
        if process_file(md_file):
            processed_count += 1

    print(f"\n完成! 共处理了 {processed_count} 个文件")

if __name__ == '__main__':
    main()
