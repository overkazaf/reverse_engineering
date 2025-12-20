#!/usr/bin/env python3
"""
修复列表中代码块的缩进问题
"""

import re
from pathlib import Path


def fix_list_code_blocks(file_path: str) -> tuple[bool, list]:
    """修复列表中的代码块缩进"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    fixed = False
    issues = []
    new_lines = []

    i = 0
    while i < len(lines):
        line = lines[i]
        new_lines.append(line)

        # 检测列表项后的代码块
        # 列表项格式：以 - 或 * 或 数字. 开头
        list_match = re.match(r'^(\s*)([-*]|\d+\.)\s', line)

        if list_match:
            list_indent = len(list_match.group(1))  # 列表项的缩进
            expected_code_indent = list_indent + 4  # 列表内容缩进应为列表项缩进+4

            # 向前查找，看看是否有代码块
            j = i + 1
            found_code_block = False

            while j < len(lines):
                next_line = lines[j]

                # 如果遇到空行，跳过
                if not next_line.strip():
                    new_lines.append(next_line)
                    j += 1
                    continue

                # 检查是否是代码块开始
                code_start_match = re.match(r'^(\s*)```(\w*)', next_line)
                if code_start_match:
                    current_indent = len(code_start_match.group(1))
                    lang = code_start_match.group(2)

                    # 如果缩进不对，修复它
                    if current_indent != expected_code_indent:
                        fixed_line = ' ' * expected_code_indent + '```' + lang + '\n'
                        new_lines.append(fixed_line)
                        issues.append(f"第{j+1}行：修复代码块开始缩进 {current_indent} -> {expected_code_indent}")
                        fixed = True
                    else:
                        new_lines.append(next_line)

                    # 找到代码块结束
                    j += 1
                    while j < len(lines):
                        code_line = lines[j]

                        # 检查是否是代码块结束
                        if re.match(r'^(\s*)```\s*$', code_line):
                            end_indent = len(code_line) - len(code_line.lstrip())

                            # 修复结束标记的缩进
                            if end_indent != expected_code_indent:
                                fixed_line = ' ' * expected_code_indent + '```\n'
                                new_lines.append(fixed_line)
                                issues.append(f"第{j+1}行：修复代码块结束缩进 {end_indent} -> {expected_code_indent}")
                                fixed = True
                            else:
                                new_lines.append(code_line)
                            j += 1
                            break
                        else:
                            # 代码块内容，保持原样
                            new_lines.append(code_line)
                            j += 1

                    found_code_block = True
                    # 继续处理这个列表项后面的内容
                    i = j - 1
                    break
                else:
                    # 不是代码块，继续查找
                    # 如果这一行的缩进小于等于列表项缩进，说明列表项结束了
                    line_indent = len(next_line) - len(next_line.lstrip())
                    if next_line.strip() and line_indent <= list_indent:
                        break

                    new_lines.append(next_line)
                    j += 1

            if found_code_block:
                i = j
                continue

        i += 1

    # 如果有修改，写回文件
    if fixed:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)

    return fixed, issues


def main():
    docs_dir = Path("docs")

    # 检查所有MD文件
    md_files = list(docs_dir.rglob("*.md"))

    total_fixed = 0
    all_issues = []

    for md_file in md_files:
        fixed, issues = fix_list_code_blocks(str(md_file))

        if fixed:
            relative_path = md_file.relative_to(docs_dir)
            print(f"✅ 已修复: {relative_path}")
            for issue in issues:
                print(f"   - {issue}")
            total_fixed += 1
            all_issues.extend(issues)

    print(f"\n📊 统计:")
    print(f"   - 修复的文件数: {total_fixed}")
    print(f"   - 修复的问题数: {len(all_issues)}")


if __name__ == "__main__":
    main()
