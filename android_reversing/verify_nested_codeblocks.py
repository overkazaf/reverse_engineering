#!/usr/bin/env python3
"""
验证嵌套代码块问题
"""

import re
from pathlib import Path


def check_nested_blocks(file_path: str):
    """检查文件中的嵌套代码块"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    in_code_block = False
    code_block_start_line = 0
    issues = []

    for i, line in enumerate(lines, 1):
        if re.match(r'^```', line):
            if in_code_block:
                # 代码块结束
                if line.strip() != '```':
                    # 结束标记后面还有内容，这可能是问题
                    issues.append({
                        'line': i,
                        'type': '代码块结束标记格式错误',
                        'content': line.rstrip(),
                        'context': lines[i-2:i+1] if i > 1 else lines[i-1:i+1]
                    })
                in_code_block = False
            else:
                # 代码块开始
                code_block_start_line = i
                in_code_block = True
        elif in_code_block:
            # 在代码块内部检查是否有像代码块标记的内容
            if '```' in line and not line.strip().startswith('#') and not line.strip().startswith('//'):
                # 可能是嵌套代码块或者是代码示例中的代码块
                # 需要人工检查
                issues.append({
                    'line': i,
                    'type': '代码块内包含```',
                    'content': line.rstrip(),
                    'block_start': code_block_start_line,
                    'context': lines[i-2:i+2]
                })

    return issues


def main():
    docs_dir = Path("docs")

    # 重点检查之前报告有嵌套代码块的文件
    problem_files = [
        "01-Recipes/Analysis/re_workflow.md",
        "01-Recipes/Network/tls_fingerprinting_guide.md",
        "01-Recipes/Anti-Detection/device_fingerprinting_and_bypass.md",
    ]

    for file_path in problem_files:
        full_path = docs_dir / file_path
        if not full_path.exists():
            print(f"❌ 文件不存在: {file_path}")
            continue

        issues = check_nested_blocks(str(full_path))

        if issues:
            print(f"\n📄 {file_path}")
            print(f"   发现 {len(issues)} 个潜在问题:\n")

            for issue in issues[:5]:  # 只显示前5个
                print(f"   第{issue['line']}行 - {issue['type']}")
                print(f"   内容: {issue['content']}")
                print(f"   上下文:")
                for ctx_line in issue['context']:
                    print(f"      {ctx_line.rstrip()}")
                print()
        else:
            print(f"✅ {file_path} - 无问题")


if __name__ == "__main__":
    main()
