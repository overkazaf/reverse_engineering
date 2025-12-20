#!/usr/bin/env python3
"""
修复setup.md中的代码块问题
将暴露在外的命令重新包裹到代码块中
"""

import re

def is_command_line(line):
    """判断是否是命令行"""
    stripped = line.strip()
    if not stripped or stripped.startswith('#') or stripped.startswith('-') or stripped.startswith('*') or stripped.startswith('>'):
        return False

    # 检查是否包含常见命令
    commands = ['adb', 'frida', 'python', 'pip', 'sudo', 'brew', 'git', 'curl', 'wget', 'npm', 'chmod', 'mkdir']
    return any(cmd in stripped.lower() for cmd in commands)

def fix_setup_file(file_path):
    """修复setup.md文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    i = 0
    in_code_block = False
    pending_commands = []  # 待处理的命令行

    while i < len(lines):
        line = lines[i]

        # 检测代码块标记
        if line.strip().startswith('```'):
            # 如果有待处理的命令，先添加它们
            if pending_commands:
                # 添加代码块包裹
                lang = 'bash' if any('sudo' in cmd or '#!/' in cmd for cmd in pending_commands) else 'bash'
                new_lines.append(f'```{lang}\n')
                new_lines.extend(pending_commands)
                new_lines.append('```\n')
                new_lines.append('\n')
                pending_commands = []

            in_code_block = not in_code_block

            # 检查是否是孤立的```（前后都没有代码）
            if line.strip() == '```' and not in_code_block:
                # 检查前后是否有命令
                has_command_before = i > 0 and is_command_line(lines[i-1])
                has_command_after = i < len(lines) - 1 and is_command_line(lines[i+1])

                if not has_command_before and not has_command_after:
                    # 孤立的```，跳过
                    print(f"删除第{i+1}行的孤立```")
                    i += 1
                    continue

            new_lines.append(line)
            i += 1
            continue

        # 如果在代码块中，直接添加
        if in_code_block:
            new_lines.append(line)
            i += 1
            continue

        # 如果是命令行但不在代码块中
        if is_command_line(line):
            print(f"发现代码块外的命令：第{i+1}行 - {line.strip()}")
            pending_commands.append(line)
            i += 1
            continue

        # 普通文本行
        # 如果有待处理的命令，先添加它们
        if pending_commands:
            # 添加代码块包裹
            new_lines.append('```bash\n')
            new_lines.extend(pending_commands)
            new_lines.append('```\n')
            new_lines.append('\n')
            pending_commands = []

        new_lines.append(line)
        i += 1

    # 文件结束，处理剩余的命令
    if pending_commands:
        new_lines.append('```bash\n')
        new_lines.extend(pending_commands)
        new_lines.append('```\n')

    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    print(f"\n修复完成！")

if __name__ == "__main__":
    fix_setup_file("docs/00-Quick-Start/setup.md")
