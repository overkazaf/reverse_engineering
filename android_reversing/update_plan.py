#!/usr/bin/env python3
import sys

def update_plan(file_path, status, issues="", notes=""):
    with open('MARKDOWN_FIX_PLAN.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 转义特殊字符
    file_path_escaped = file_path.replace('/', r'\/')
    
    # 更新状态
    pattern = f'| {file_path} | ⏳ 待检查 | - | - |'
    replacement = f'| {file_path} | {status} | {issues} | {notes} |'
    
    content = content.replace(pattern, replacement)
    
    # 更新统计
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('- **待检查**:'):
            count = int(line.split(':')[1].strip())
            lines[i] = f'- **待检查**: {count - 1}'
        elif line.startswith('- **已修复**:') and '✔️' in status:
            count = int(line.split(':')[1].strip())
            lines[i] = f'- **已修复**: {count + 1}'
        elif line.startswith('**当前进度**:'):
            lines[i] = f'**当前进度**: 1/96 (1%)'
    
    content = '\n'.join(lines)
    
    with open('MARKDOWN_FIX_PLAN.md', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 已更新计划文件: {file_path} -> {status}")

if __name__ == "__main__":
    update_plan(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "", sys.argv[4] if len(sys.argv) > 4 else "")
