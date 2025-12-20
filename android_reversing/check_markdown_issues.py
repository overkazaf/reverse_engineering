#!/usr/bin/env python3
"""
只检查Markdown文档中的问题，不自动修复
"""

import re
from pathlib import Path
from collections import defaultdict


def check_code_fences(content: str) -> list:
    """检查代码块围栏是否匹配"""
    issues = []
    lines = content.split('\n')
    fence_count = 0

    for i, line in enumerate(lines, 1):
        if re.match(r'^```', line.strip()):
            fence_count += 1

    if fence_count % 2 != 0:
        issues.append(f"代码块围栏不匹配（共{fence_count}个```标记，应为偶数）")

    return issues


def check_inline_code_in_headers(content: str) -> list:
    """检查标题中的内联代码"""
    issues = []
    lines = content.split('\n')

    for i, line in enumerate(lines, 1):
        if re.match(r'^#+\s', line):
            backticks = line.count('`')
            if backticks % 2 != 0:
                issues.append(f"第{i}行：标题中反引号不匹配 - {line.strip()}")

    return issues


def check_code_block_language(content: str) -> list:
    """检查代码块是否指定了语言"""
    issues = []
    lines = content.split('\n')

    for i, line in enumerate(lines, 1):
        # 匹配只有```没有语言标识的行
        if re.match(r'^```\s*$', line) and i < len(lines):
            # 不是代码块结束标记（检查上一行）
            if i == 1 or not lines[i-2].strip().startswith('```'):
                issues.append(f"第{i}行：代码块未指定语言类型")

    return issues


def check_file(file_path: Path) -> dict:
    """检查单个文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {'error': str(e)}

    all_issues = []

    # 检查各种问题
    all_issues.extend(check_code_fences(content))
    all_issues.extend(check_inline_code_in_headers(content))

    return {
        'issues': all_issues,
        'issue_count': len(all_issues)
    }


def main():
    docs_dir = Path("docs")

    if not docs_dir.exists():
        print(f"❌ 目录不存在: {docs_dir}")
        return

    md_files = list(docs_dir.rglob("*.md"))
    print(f"📁 检查 {len(md_files)} 个Markdown文件\n")

    files_with_issues = []
    issue_summary = defaultdict(int)

    for md_file in md_files:
        result = check_file(md_file)

        if 'error' in result:
            print(f"❌ 错误: {md_file.relative_to(docs_dir)} - {result['error']}")
            continue

        if result['issue_count'] > 0:
            relative_path = md_file.relative_to(docs_dir)
            files_with_issues.append((relative_path, result['issues']))

            for issue in result['issues']:
                # 提取问题类型
                if '代码块围栏' in issue:
                    issue_summary['代码块围栏不匹配'] += 1
                elif '标题中反引号' in issue:
                    issue_summary['标题反引号不匹配'] += 1
                elif '未指定语言' in issue:
                    issue_summary['代码块未指定语言'] += 1

    # 输出结果
    if files_with_issues:
        print("⚠️  发现问题的文件:\n")
        for file_path, issues in files_with_issues:
            print(f"📄 {file_path}")
            for issue in issues:
                print(f"   - {issue}")
            print()

        print("\n📊 问题统计:")
        for issue_type, count in issue_summary.items():
            print(f"   - {issue_type}: {count}")

        print(f"\n   总计:")
        print(f"   - 有问题的文件: {len(files_with_issues)}")
        print(f"   - 问题总数: {sum(issue_summary.values())}")
    else:
        print("✅ 所有文档格式正确！")


if __name__ == "__main__":
    main()
