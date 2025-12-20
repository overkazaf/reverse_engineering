#!/usr/bin/env python3
"""
Markdown 格式检查和修复脚本
"""
import re
import sys
from pathlib import Path

def check_markdown_issues(file_path):
    """检查 markdown 文件的常见问题"""
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
    
    # 检查2: 混乱的标题层级
    headings = []
    for i, line in enumerate(lines, 1):
        if line.strip().startswith('#'):
            level = len(re.match(r'^#+', line.strip()).group())
            headings.append((i, level, line.strip()))
    
    # 检查标题跳级（如从 # 直接到 ###）
    for i in range(1, len(headings)):
        prev_level = headings[i-1][1]
        curr_level = headings[i][1]
        if curr_level > prev_level + 1:
            issues.append(f"⚠️ 标题跳级: 行{headings[i][0]} (从 {'#'*prev_level} 到 {'#'*curr_level})")
    
    # 检查3: 列表格式问题
    list_issues = 0
    for i, line in enumerate(lines, 1):
        # 检查列表项后是否有多余空行
        if re.match(r'^[\*\-\+]\s', line.strip()):
            if i < len(lines) - 1:
                next_line = lines[i]
                if next_line.strip() == '' and i < len(lines) - 2:
                    next_next = lines[i+1].strip()
                    if re.match(r'^[\*\-\+]\s', next_next):
                        list_issues += 1
    
    if list_issues > 3:
        issues.append(f"⚠️ 列表项之间有多余空行（{list_issues}处）")
    
    # 检查4: 中英文混杂的代码注释
    chinese_in_code = []
    in_code_block = False
    code_start_line = 0
    
    for i, line in enumerate(lines, 1):
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            if in_code_block:
                code_start_line = i
        elif in_code_block:
            # 检查是否有中英文混合的注释
            if re.search(r'#.*[\u4e00-\u9fff].*[a-zA-Z]', line):
                chinese_in_code.append(i)
    
    if len(chinese_in_code) > 5:
        issues.append(f"⚠️ 代码块中有中英文混杂的注释（{len(chinese_in_code)}行）")
    
    # 检查5: 空标题
    empty_headings = [i for i, line in enumerate(lines, 1) 
                     if re.match(r'^#+\s*$', line.strip())]
    if empty_headings:
        issues.append(f"⚠️ 空标题: 行{empty_headings}")
    
    # 检查6: 重复的空行
    excessive_blanks = 0
    blank_count = 0
    for line in lines:
        if line.strip() == '':
            blank_count += 1
        else:
            if blank_count >= 3:
                excessive_blanks += 1
            blank_count = 0
    
    if excessive_blanks > 5:
        issues.append(f"⚠️ 有{excessive_blanks}处连续3个以上空行")
    
    # 检查7: 未转义的特殊字符
    special_chars = []
    for i, line in enumerate(lines, 1):
        if not line.strip().startswith('```') and not in_code_block:
            # 检查未转义的 < >
            if re.search(r'[^`]<[^/]', line) or re.search(r'[^-]>', line):
                if not re.search(r'https?://', line):  # 排除 URL
                    special_chars.append(i)
    
    if special_chars and len(special_chars) > 3:
        issues.append(f"⚠️ 可能有未转义的特殊字符 < > ({len(special_chars)}行)")
    
    return issues if issues else ["✅ 未发现明显问题"]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python check_markdown.py <file.md>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    issues = check_markdown_issues(file_path)
    
    print(f"\n检查文件: {file_path}")
    print("=" * 60)
    for issue in issues:
        print(issue)
    print()
