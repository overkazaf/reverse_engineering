#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown格式全面修复工具
修复所有markdown文件中的列表、表格、代码块等格式问题

功能：
1. 修复列表缩进和标记
2. 将特定列表转换为表格
3. 修复代码块
4. 统一格式规范

使用方法：
python fix_all_markdown.py                 # 扫描并报告问题
python fix_all_markdown.py --fix           # 自动修复所有问题
python fix_all_markdown.py --preview       # 预览修复效果
python fix_all_markdown.py --backup        # 修复并创建备份
"""

import os
import re
import yaml
import argparse
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime


class MarkdownFixer:
    """Markdown格式修复器"""

    def __init__(self, docs_dir="docs", mkdocs_file="mkdocs.yml"):
        self.docs_dir = docs_dir
        self.mkdocs_file = mkdocs_file
        self.files_to_fix = []
        self.issues_found = {}
        self.fixes_applied = {}

    def scan_all_files(self):
        """扫描所有markdown文件"""
        print("\n🔍 扫描所有markdown文件...")

        try:
            with open(self.mkdocs_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                nav = config.get('nav', [])
        except:
            print("❌ 无法读取mkdocs.yml，将扫描整个docs目录")
            nav = []

        # 从导航中收集文件
        def collect_files(items):
            files = []
            for item in items:
                if isinstance(item, dict):
                    for title, path in item.items():
                        if isinstance(path, str) and path.endswith('.md'):
                            file_path = os.path.join(self.docs_dir, path)
                            if os.path.exists(file_path):
                                files.append(file_path)
                        elif isinstance(path, list):
                            files.extend(collect_files(path))
            return files

        for section in nav:
            if isinstance(section, dict):
                for section_name, items in section.items():
                    if isinstance(items, list):
                        self.files_to_fix.extend(collect_files(items))

        print(f"✅ 找到 {len(self.files_to_fix)} 个markdown文件")
        return self.files_to_fix

    def analyze_file(self, file_path):
        """分析文件中的格式问题"""
        issues = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except:
            return issues

        in_code_block = False
        prev_line_blank = False

        for i, line in enumerate(lines, 1):
            # 检查代码块
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                continue

            if in_code_block:
                continue

            # 检查列表格式问题
            list_match = re.match(r'^(\s*)([-*+]|\d+\.)(\S)', line)
            if list_match:
                issues.append({
                    'line': i,
                    'type': 'list_no_space',
                    'content': line.rstrip(),
                    'fix': f"{list_match.group(1)}{list_match.group(2)} {line[len(list_match.group(1)) + len(list_match.group(2)):]}"
                })

            # 检查可能应该是表格的列表
            if line.strip().startswith('-') and ':' in line:
                # 类似 "- 名称: 值" 的格式
                if re.match(r'^\s*-\s*[^:]+:\s*.+', line):
                    issues.append({
                        'line': i,
                        'type': 'list_should_be_table',
                        'content': line.rstrip()
                    })

            # 检查不规范的缩进
            if line.startswith(' ') and not line.startswith('    '):
                # 缩进不是4的倍数
                spaces = len(line) - len(line.lstrip())
                if spaces % 4 != 0 and spaces % 2 != 0:
                    issues.append({
                        'line': i,
                        'type': 'irregular_indent',
                        'content': line.rstrip(),
                        'spaces': spaces
                    })

            prev_line_blank = line.strip() == ''

        return issues

    def fix_file(self, file_path, create_backup=True):
        """修复单个文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"❌ 无法读取 {file_path}: {e}")
            return 0

        original_lines = lines[:]
        fixes = 0

        # 备份
        if create_backup:
            backup_path = f"{file_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.writelines(original_lines)

        # 应用修复
        lines, count = self._fix_code_blocks(lines)
        fixes += count

        lines, count = self._fix_list_spacing(lines)
        fixes += count

        lines, count = self._fix_heading_spacing(lines)
        fixes += count

        lines, count = self._convert_lists_to_tables(lines)
        fixes += count

        lines, count = self._fix_indentation(lines)
        fixes += count

        # 写回文件
        if fixes > 0:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
            except Exception as e:
                print(f"❌ 无法写入 {file_path}: {e}")
                return 0

        return fixes

    def _fix_code_blocks(self, lines):
        """修复代码块"""
        fixes = 0
        in_code_block = False

        for line in lines:
            if re.match(r'^```', line):
                in_code_block = not in_code_block

        # 如果代码块未闭合，添加结束标记
        if in_code_block:
            if lines and not lines[-1].endswith('\n'):
                lines[-1] += '\n'
            lines.append('```\n')
            fixes += 1

        return lines, fixes

    def _fix_list_spacing(self, lines):
        """修复列表标记后的空格"""
        fixes = 0
        in_code_block = False

        for i, line in enumerate(lines):
            if re.match(r'^```', line):
                in_code_block = not in_code_block
                continue

            if in_code_block:
                continue

            # 跳过分隔线（--- 或 ***）
            if re.match(r'^[-*_]{3,}\s*$', line):
                continue

            # 跳过粗体/斜体标记（**text** 或 *text*）
            if re.match(r'^(\s*)*[^*]+*', line):
                continue

            # 修复列表标记后缺少空格
            match = re.match(r'^(\s*)([-*+]|\d+\.)([^\s\-*])', line)
            if match:
                indent = match.group(1)
                marker = match.group(2)
                rest = line[len(indent) + len(marker):]

                # 额外检查：确保不是分隔线的一部分
                if marker == '-' and rest.startswith('-'):
                    continue

                lines[i] = f"{indent}{marker} {rest}"
                fixes += 1

        return lines, fixes

    def _fix_heading_spacing(self, lines):
        """修复标题后的空格"""
        fixes = 0
        in_code_block = False

        for i, line in enumerate(lines):
            if re.match(r'^```', line):
                in_code_block = not in_code_block
                continue

            if in_code_block:
                continue

            # 修复标题#后缺少空格
            match = re.match(r'^(#{1,6})([^\s#])', line)
            if match:
                hashes = match.group(1)
                rest = line[len(hashes):]
                lines[i] = f"{hashes} {rest}"
                fixes += 1

        return lines, fixes

    def _convert_lists_to_tables(self, lines):
        """将符合条件的列表转换为表格"""
        fixes = 0
        in_code_block = False
        i = 0

        while i < len(lines):
            if re.match(r'^```', lines[i]):
                in_code_block = not in_code_block
                i += 1
                continue

            if in_code_block:
                i += 1
                continue

            # 检测连续的 "- 键: 值" 格式
            if re.match(r'^\s*-\s*[^:]+:\s*.+', lines[i]):
                # 收集连续的此类行
                key_value_lines = []
                j = i

                while j < len(lines) and re.match(r'^\s*-\s*[^:]+:\s*.+', lines[j]):
                    key_value_lines.append(lines[j])
                    j += 1

                # 如果有3个或更多，转换为表格
                if len(key_value_lines) >= 3:
                    table = self._create_table_from_list(key_value_lines)
                    # 替换原有行
                    lines[i:j] = table
                    fixes += 1
                    i += len(table)
                    continue

            i += 1

        return lines, fixes

    def _create_table_from_list(self, list_lines):
        """从列表创建表格"""
        rows = []

        for line in list_lines:
            match = re.match(r'^\s*-\s*([^:]+):\s*(.+)', line)
            if match:
                key = match.group(1).strip()
                value = match.group(2).strip()
                rows.append((key, value))

        if not rows:
            return list_lines

        # 创建表格
        table_lines = [
            '\n',
            '| 项目 | 说明 |\n',
            '|------|------|\n'
        ]

        for key, value in rows:
            table_lines.append(f'| {key} | {value} |\n')

        table_lines.append('\n')

        return table_lines

    def _fix_indentation(self, lines):
        """修复缩进问题"""
        fixes = 0
        in_code_block = False

        for i, line in enumerate(lines):
            if re.match(r'^```', line):
                in_code_block = not in_code_block
                continue

            if in_code_block:
                continue

            # 修复不规范的缩进（转换为4空格的倍数）
            if line.startswith(' ') and not line.strip() == '':
                spaces = len(line) - len(line.lstrip())
                if spaces % 4 != 0 and spaces % 2 == 0:
                    # 2空格缩进，不改变
                    pass
                elif spaces % 4 != 0 and spaces % 2 != 0:
                    # 奇数缩进，调整为最近的偶数
                    new_spaces = (spaces // 2) * 2
                    lines[i] = ' ' * new_spaces + line.lstrip()
                    fixes += 1

        return lines, fixes

    def fix_all_files(self, create_backup=True):
        """修复所有文件"""
        print("\n🔧 开始修复所有文件...")
        print("=" * 60)

        total_fixes = 0

        for file_path in self.files_to_fix:
            file_name = os.path.relpath(file_path, self.docs_dir)

            fixes = self.fix_file(file_path, create_backup)

            if fixes > 0:
                print(f"✅ {file_name}: {fixes} 个修复")
                self.fixes_applied[file_path] = fixes
                total_fixes += fixes
            else:
                print(f"   {file_name}: 无需修复")

        print("\n" + "=" * 60)
        print(f"🎉 完成！总计修复 {total_fixes} 个问题")
        print(f"   修复的文件: {len(self.fixes_applied)}/{len(self.files_to_fix)}")

        return total_fixes

    def generate_report(self):
        """生成修复报告"""
        report_path = "output/markdown_fix_report.md"
        os.makedirs("output", exist_ok=True)

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# Markdown格式修复报告\n\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## 📊 统计摘要\n\n")
            f.write(f"- 扫描文件数: {len(self.files_to_fix)}\n")
            f.write(f"- 修复文件数: {len(self.fixes_applied)}\n")
            f.write(f"- 总修复数: {sum(self.fixes_applied.values())}\n\n")

            if self.fixes_applied:
                f.write("## 📝 修复详情\n\n")
                for file_path, count in sorted(self.fixes_applied.items()):
                    rel_path = os.path.relpath(file_path, self.docs_dir)
                    f.write(f"- `{rel_path}`: {count} 个修复\n")

        print(f"\n📄 报告已生成: {report_path}")
        return report_path


def main():
    parser = argparse.ArgumentParser(
        description='Markdown格式全面修复工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--fix', action='store_true',
                       help='执行修复（默认只扫描）')
    parser.add_argument('--no-backup', action='store_true',
                       help='不创建备份文件')
    parser.add_argument('--preview', action='store_true',
                       help='预览将要修复的问题')

    args = parser.parse_args()

    print("╔══════════════════════════════════════════════════╗")
    print("║        Markdown格式全面修复工具                  ║")
    print("╚══════════════════════════════════════════════════╝")

    fixer = MarkdownFixer()

    # 扫描文件
    fixer.scan_all_files()

    if args.preview:
        print("\n📋 预览将要修复的问题...")
        for file_path in fixer.files_to_fix[:5]:  # 只预览前5个
            print(f"\n文件: {os.path.relpath(file_path, fixer.docs_dir)}")
            issues = fixer.analyze_file(file_path)
            if issues:
                for issue in issues[:10]:  # 每个文件最多显示10个问题
                    print(f"  行 {issue['line']}: {issue['type']}")
            else:
                print("  无问题")
        return

    if args.fix:
        # 执行修复
        total_fixes = fixer.fix_all_files(create_backup=not args.no_backup)

        # 生成报告
        fixer.generate_report()

        if total_fixes > 0:
            print("\n💡 建议:")
            print("   1. 使用 git diff 查看修改")
            print("   2. 重新生成PDF: python docs_to_pdf_final.py --no-cache")
            print("   3. 如有问题，备份文件位于: *.backup.*")
    else:
        print("\n⚠️  这是扫描模式，未执行修复")
        print("   添加 --fix 参数执行修复: python fix_all_markdown.py --fix")
        print("   添加 --preview 预览问题: python fix_all_markdown.py --preview")


if __name__ == "__main__":
    main()
