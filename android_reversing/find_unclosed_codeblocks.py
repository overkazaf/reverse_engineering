#!/usr/bin/env python3
"""
找到未闭合的代码块
"""

import re
from pathlib import Path


def find_unclosed_blocks(file_path: Path) -> list:
    """找到未闭合的代码块"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    issues = []
    in_code_block = False
    code_block_start = 0

    for i, line in enumerate(lines, 1):
        # 检测代码块开始/结束
        if line.strip().startswith('```'):
            if in_code_block:
                # 代码块结束
                in_code_block = False
                code_block_start = 0
            else:
                # 代码块开始
                in_code_block = True
                code_block_start = i

    # 如果遍历完还在代码块中，说明有未闭合的代码块
    if in_code_block:
        issues.append({
            'type': '未闭合的代码块',
            'start_line': code_block_start,
            'message': f'代码块从第{code_block_start}行开始，但没有找到结束标记'
        })

    return issues


def main():
    docs_dir = Path("docs")

    problem_files = [
        "03-Case-Studies/case_study_app_encryption.md",
        "00-Quick-Start/setup.md",
        "01-Recipes/Analysis/re_workflow.md",
        "01-Recipes/Scripts/automation_scripts.md",
    ]

    for file_path in problem_files:
        full_path = docs_dir / file_path
        if not full_path.exists():
            print(f"❌ 文件不存在: {file_path}")
            continue

        issues = find_unclosed_blocks(full_path)

        if issues:
            print(f"\n📄 {file_path}")
            for issue in issues:
                print(f"   ⚠️  {issue['message']}")

                # 显示代码块开始位置的内容
                with open(full_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    start = max(0, issue['start_line'] - 1)
                    end = min(len(lines), issue['start_line'] + 3)

                    print(f"   代码块开始位置:")
                    for j in range(start, end):
                        print(f"      {j+1:4d}: {lines[j].rstrip()}")
        else:
            print(f"✅ {file_path} - 代码块都已正确闭合")


if __name__ == "__main__":
    main()
