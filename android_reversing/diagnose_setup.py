#!/usr/bin/env python3
"""
诊断setup.md中的代码块问题
"""

with open("docs/00-Quick-Start/setup.md", 'r', encoding='utf-8') as f:
    lines = f.readlines()

in_code_block = False
issues = []

for i, line in enumerate(lines, 1):
    if line.strip().startswith('```'):
        in_code_block = not in_code_block
        print(f"{i:4d}: {line.rstrip()} [{'开始' if in_code_block else '结束'}]")
    elif not in_code_block:
        # 检查是否是命令行（不在代码块中）
        stripped = line.strip()
        if stripped and not stripped.startswith('#') and not stripped.startswith('-') and not stripped.startswith('*'):
            # 可能是命令
            if any(cmd in stripped for cmd in ['adb', 'frida', 'python', 'pip', 'sudo', 'brew', 'git']):
                print(f"{i:4d}: ⚠️  {line.rstrip()} [代码块外的可能命令]")
                issues.append(i)

print(f"\n发现 {len(issues)} 处可能的问题")
print(f"问题行: {issues[:20]}")
