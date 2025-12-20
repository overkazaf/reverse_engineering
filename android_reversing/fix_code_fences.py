#!/usr/bin/env python3
"""
自动修复代码块围栏不匹配的问题
"""

import re
from pathlib import Path


def fix_code_fences_in_file(file_path: Path) -> tuple[bool, str]:
    """修复文件中的代码块围栏"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')

    # 统计代码块标记
    fence_lines = []
    for i, line in enumerate(lines):
        if line.strip().startswith('```'):
            fence_lines.append((i, line))

    if len(fence_lines) % 2 == 0:
        return False, "代码块围栏已匹配"

    # 找到问题所在
    # 检查每对围栏之间的内容
    issues = []
    for i in range(0, len(fence_lines) - 1, 2):
        start_idx, start_line = fence_lines[i]
        if i + 1 < len(fence_lines):
            end_idx, end_line = fence_lines[i + 1]

            # 检查是否是合法的代码块
            # 开始标记应该有语言标识或为空
            # 结束标记应该只有```
            if end_line.strip() != '```' and not end_line.strip().startswith('```'):
                issues.append(f"第{end_idx+1}行：结束标记格式错误")

            # 检查中间的内容
            between_lines = lines[start_idx+1:end_idx]
            for j, line in enumerate(between_lines):
                if line.strip().startswith('```'):
                    issues.append(f"第{start_idx + j + 2}行：代码块内部包含```")

    # 如果有奇数个围栏，最后一个可能是多余的或缺少配对
    if len(fence_lines) % 2 != 0:
        last_idx, last_line = fence_lines[-1]

        # 检查最后一个围栏前后的context
        context_before = lines[max(0, last_idx-3):last_idx]
        context_after = lines[last_idx+1:min(len(lines), last_idx+4)]

        # 判断这是一个多余的标记还是缺少配对
        # 如果前面有代码内容但没有开始标记，说明缺少开始标记
        # 如果后面有代码内容但没有结束标记，说明缺少结束标记
        # 否则可能是多余的标记

        has_code_before = any(line.strip() and not line.strip().startswith('#') for line in context_before[-2:])
        has_code_after = any(line.strip() and not line.strip().startswith('#') and not line.strip().startswith('*') for line in context_after[:2])

        issue_desc = f"第{last_idx+1}行：孤立的```标记\n"
        issue_desc += f"  前面内容: {[l.strip()[:30] for l in context_before[-2:] if l.strip()]}\n"
        issue_desc += f"  后面内容: {[l.strip()[:30] for l in context_after[:2] if l.strip()]}\n"

        if has_code_before and not has_code_after:
            issue_desc += "  推测：可能是多余的结束标记，建议删除\n"
        elif has_code_after and not has_code_before:
            issue_desc += "  推测：可能缺少结束标记\n"
        else:
            issue_desc += "  推测：可能是多余的标记，建议删除\n"

        return False, issue_desc

    return False, "未能自动修复，需要人工检查"


def main():
    docs_dir = Path("docs")

    problem_files = [
        "00-Quick-Start/setup.md",
        "03-Case-Studies/case_study_app_encryption.md",
        "01-Recipes/Analysis/re_workflow.md",
        "01-Recipes/Scripts/automation_scripts.md",
    ]

    for file_path_str in problem_files:
        file_path = docs_dir / file_path_str
        if not file_path.exists():
            print(f"❌ 文件不存在: {file_path_str}")
            continue

        fixed, message = fix_code_fences_in_file(file_path)

        print(f"\n📄 {file_path_str}")
        print(f"   {message}")


if __name__ == "__main__":
    main()
