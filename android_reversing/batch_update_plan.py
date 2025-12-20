#!/usr/bin/env python3
import sys

def batch_update_plan(updates):
    """批量更新计划文件
    updates: [(file_path, status, issues, notes), ...]
    """
    with open('MARKDOWN_FIX_PLAN.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    completed_count = 0
    fixed_count = 0
    
    for file_path, status, issues, notes in updates:
        pattern = f'| {file_path} | ⏳ 待检查 | - | - |'
        replacement = f'| {file_path} | {status} | {issues} | {notes} |'
        content = content.replace(pattern, replacement)
        
        if '✅' in status:
            completed_count += 1
        elif '✔️' in status:
            fixed_count += 1
    
    # 更新统计
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('- **待检查**:'):
            current = int(line.split(':')[1].strip())
            lines[i] = f'- **待检查**: {current - len(updates)}'
        elif line.startswith('- **已完成**:'):
            current = int(line.split(':')[1].strip())
            lines[i] = f'- **已完成**: {current + completed_count}'
        elif line.startswith('- **已修复**:'):
            current = int(line.split(':')[1].strip())
            lines[i] = f'- **已修复**: {current + fixed_count}'
    
    content = '\n'.join(lines)
    
    with open('MARKDOWN_FIX_PLAN.md', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 批量更新完成: {len(updates)} 个文件")

if __name__ == "__main__":
    # 从命令行读取更新列表
    import json
    updates_json = sys.argv[1]
    updates = json.loads(updates_json)
    batch_update_plan(updates)
