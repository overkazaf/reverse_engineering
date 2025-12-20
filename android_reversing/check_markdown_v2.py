#!/usr/bin/env python3
import re
import sys

def check_markdown_issues(file_path):
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
    except Exception as e:
        return [f"❌ 无法读取文件: {e}"]
    
    # 检查1: 未闭合的代码块
    code_blocks = re.findall(r'```', content)
    if len(code_blocks) % 2 != 0:
        issues.append("⚠️ 代码块未闭合（```数量为奇数）")
    
    # 检查2: 标题层级（忽略代码块中的内容）
    headings = []
    in_code_block = False
    
    for i, line in enumerate(lines, 1):
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            continue
        
        if not in_code_block and line.strip().startswith('#'):
            # 只计算真正的标题（不在代码块中，且 # 后面有空格）
            match = re.match(r'^(#+)\s+', line)
            if match:
                level = len(match.group(1))
                headings.append((i, level, line.strip()))
    
    # 检查标题跳级
    for i in range(1, len(headings)):
        prev_level = headings[i-1][1]
        curr_level = headings[i][1]
        if curr_level > prev_level + 1:
            issues.append(f"⚠️ 标题跳级: 行{headings[i][0]} (从 {'#'*prev_level} 到 {'#'*curr_level})")
    
    return issues if issues else ["✅ 未发现明显问题"]

if __name__ == "__main__":
    file_path = sys.argv[1]
    issues = check_markdown_issues(file_path)
    
    print(f"\n检查文件: {file_path}")
    print("=" * 60)
    for issue in issues:
        print(issue)
    print()
