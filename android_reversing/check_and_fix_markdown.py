#!/usr/bin/env python3
"""
检查并修复Markdown文档中的格式问题
主要关注代码块相关的渲染问题
"""

import os
import re
from pathlib import Path
from typing import List, Tuple


class MarkdownFixer:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.issues = []
        self.fixed = False

    def check_and_fix(self) -> Tuple[bool, List[str]]:
        """检查并修复Markdown文件"""
        with open(self.file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # 检查各种问题
        content = self.fix_code_block_fences(content)
        content = self.fix_code_block_spacing(content)
        content = self.fix_list_code_block_indentation(content)
        content = self.fix_inline_code_in_headers(content)
        content = self.fix_nested_code_blocks(content)
        content = self.fix_trailing_spaces_in_code_fence(content)

        # 如果有修改，写回文件
        if content != original_content:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.fixed = True

        return self.fixed, self.issues

    def fix_code_block_fences(self, content: str) -> str:
        """检查代码块的围栏是否匹配"""
        lines = content.split('\n')
        fence_count = 0
        in_code_block = False

        for i, line in enumerate(lines):
            # 匹配代码块开始/结束标记（支持```和~~~）
            if re.match(r'^```|^~~~', line.strip()):
                fence_count += 1
                in_code_block = not in_code_block

        if fence_count % 2 != 0:
            self.issues.append(f"代码块围栏不匹配（找到{fence_count}个围栏标记）")

        return content

    def fix_code_block_spacing(self, content: str) -> str:
        """修复代码块前后的空行问题"""
        # 确保代码块前后有空行（除非在文件开头/结尾或列表中）
        lines = content.split('\n')
        fixed_lines = []

        for i, line in enumerate(lines):
            # 检测代码块开始
            if re.match(r'^```', line):
                # 如果不是第一行，且前一行不为空，添加空行
                if i > 0 and fixed_lines and fixed_lines[-1].strip():
                    # 检查是否在列表项内（以数字或-开头，且有适当缩进）
                    prev_line = fixed_lines[-1] if fixed_lines else ""
                    if not re.match(r'^\s*[-*\d]+\.?\s', prev_line):
                        fixed_lines.append('')
                        self.issues.append(f"第{i+1}行：代码块前添加空行")

            fixed_lines.append(line)

            # 检测代码块结束
            if i > 0 and re.match(r'^```\s*$', lines[i-1]):
                # 如果不是最后一行，且下一行不为空，添加空行
                if i < len(lines) - 1 and line.strip():
                    # 检查是否在列表中
                    if not re.match(r'^\s*[-*\d]+\.?\s', line):
                        # 在当前行前插入空行
                        fixed_lines.insert(-1, '')
                        self.issues.append(f"第{i+1}行：代码块后添加空行")

        return '\n'.join(fixed_lines)

    def fix_list_code_block_indentation(self, content: str) -> str:
        """修复列表中代码块的缩进问题"""
        lines = content.split('\n')
        fixed_lines = []
        in_list = False
        list_indent = 0

        for i, line in enumerate(lines):
            # 检测列表项
            list_match = re.match(r'^(\s*)([-*]|\d+\.)\s', line)
            if list_match:
                in_list = True
                list_indent = len(list_match.group(1))

            # 检测代码块在列表中
            if in_list and re.match(r'^```', line):
                current_indent = len(line) - len(line.lstrip())
                expected_indent = list_indent + 4  # 列表项缩进 + 4空格

                if current_indent != expected_indent:
                    # 修复缩进
                    fixed_line = ' ' * expected_indent + line.lstrip()
                    fixed_lines.append(fixed_line)
                    self.issues.append(f"第{i+1}行：修复列表中代码块缩进 {current_indent} -> {expected_indent}")
                    continue

            # 空行重置列表状态
            if not line.strip():
                in_list = False

            fixed_lines.append(line)

        return '\n'.join(fixed_lines)

    def fix_inline_code_in_headers(self, content: str) -> str:
        """检查标题中的内联代码"""
        lines = content.split('\n')

        for i, line in enumerate(lines):
            # 匹配标题行
            if re.match(r'^#+\s', line):
                # 检查是否有未闭合的反引号
                backticks = line.count('`')
                if backticks % 2 != 0:
                    self.issues.append(f"第{i+1}行：标题中反引号不匹配")

        return content

    def fix_nested_code_blocks(self, content: str) -> str:
        """检测嵌套的代码块（这通常是错误的）"""
        lines = content.split('\n')
        in_code_block = False

        for i, line in enumerate(lines):
            if re.match(r'^```', line):
                if in_code_block and line.strip() != '```':
                    # 在代码块内又遇到带语言标识的代码块开始
                    self.issues.append(f"第{i+1}行：可能存在嵌套代码块")
                in_code_block = not in_code_block

        return content

    def fix_trailing_spaces_in_code_fence(self, content: str) -> str:
        """修复代码围栏标记后的尾随空格"""
        # 代码块开始标记后不应有空格（除了语言标识符）
        content = re.sub(r'^(```\w+)\s+$', r'\1', content, flags=re.MULTILINE)
        # 代码块结束标记后不应有任何内容
        content = re.sub(r'^```\s+(.+)$', r'```', content, flags=re.MULTILINE)

        return content


def check_docs_directory(docs_path: str = "docs"):
    """检查文档目录"""
    docs_dir = Path(docs_path)

    if not docs_dir.exists():
        print(f"❌ 目录不存在: {docs_path}")
        return

    # 查找所有Markdown文件
    md_files = list(docs_dir.rglob("*.md"))

    print(f"📁 找到 {len(md_files)} 个Markdown文件\n")

    total_fixed = 0
    total_issues = 0

    files_with_issues = []

    for md_file in md_files:
        fixer = MarkdownFixer(str(md_file))
        fixed, issues = fixer.check_and_fix()

        if issues:
            relative_path = md_file.relative_to(docs_dir)
            files_with_issues.append((relative_path, issues, fixed))
            total_issues += len(issues)
            if fixed:
                total_fixed += 1

    # 输出结果
    if files_with_issues:
        print("📋 发现问题的文件:\n")
        for file_path, issues, fixed in files_with_issues:
            status = "✅ 已修复" if fixed else "⚠️  需要人工检查"
            print(f"{status} {file_path}")
            for issue in issues:
                print(f"  - {issue}")
            print()

        print(f"\n📊 统计:")
        print(f"  - 文件总数: {len(md_files)}")
        print(f"  - 有问题的文件: {len(files_with_issues)}")
        print(f"  - 自动修复的文件: {total_fixed}")
        print(f"  - 发现的问题总数: {total_issues}")
    else:
        print("✅ 所有文档格式正确！")


if __name__ == "__main__":
    import sys

    docs_path = sys.argv[1] if len(sys.argv) > 1 else "docs"
    check_docs_directory(docs_path)
