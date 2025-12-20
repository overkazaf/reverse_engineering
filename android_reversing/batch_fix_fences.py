#!/usr/bin/env python3
"""
批量修复代码块围栏不匹配问题
"""

import re
from pathlib import Path


def fix_fences_automatically(file_path: Path) -> tuple[bool, str]:
    """
    自动修复代码块围栏
    策略：找到孤立的```标记，如果它前面是代码内容，删除这个标记
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 找到所有```标记的位置
    fence_positions = []
    for i, line in enumerate(lines):
        if line.strip().startswith('```'):
            fence_positions.append(i)

    if len(fence_positions) % 2 == 0:
        return False, "代码块已匹配"

    # 找到最后一个孤立的```
    last_fence_idx = fence_positions[-1]

    # 检查这个```前面5行的内容
    context_start = max(0, last_fence_idx - 5)
    context_before = lines[context_start:last_fence_idx]

    # 如果前面有代码或注释，删除这个孤立的```
    has_code_before = any(
        line.strip() and
        not line.strip().startswith('#') and
        not line.strip().startswith('*') and
        not line.strip().startswith('-') and
        not re.match(r'^#+\s', line.strip())  # 不是标题
        for line in context_before[-3:]
    )

    if has_code_before or lines[last_fence_idx].strip() == '```':
        # 删除这个孤立的```标记
        new_lines = lines[:last_fence_idx] + lines[last_fence_idx + 1:]

        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)

        return True, f"删除第{last_fence_idx + 1}行的孤立```标记"

    return False, f"第{last_fence_idx + 1}行的```标记需要人工检查"


def main():
    docs_dir = Path("docs")

    problem_files = [
        "00-Quick-Start/setup.md",
        "02-Tools/Dynamic/xposed_internals.md",
        "04-Reference/Advanced/so_runtime_emulation.md",
        "04-Reference/Advanced/minimal_android_rootfs.md",
        "04-Reference/Foundations/so_elf_format.md",
        "04-Reference/Engineering/redis.md",
        "04-Reference/Engineering/Data-Analysis/hbase.md",
        "04-Reference/Engineering/Data-Analysis/flink.md",
        "01-Recipes/Unpacking/frida_unpacking_and_so_fixing.md",
        "01-Recipes/Network/network_sniffing.md",
        "01-Recipes/Anti-Detection/device_fingerprinting_and_bypass.md",
        "01-Recipes/Anti-Detection/xposed_anti_debugging.md",
        "01-Recipes/Scripts/frida_common_scripts.md",
        "01-Recipes/Scripts/frida_script_examples.md",
        "01-Recipes/Automation/proxy_pool_design.md",
        "01-Recipes/Automation/scrapy_redis_distributed.md",
        "01-Recipes/Automation/docker_deployment.md",
    ]

    fixed_count = 0
    for file_path_str in problem_files:
        file_path = docs_dir / file_path_str
        if not file_path.exists():
            print(f"❌ 文件不存在: {file_path_str}")
            continue

        fixed, message = fix_fences_automatically(file_path)

        if fixed:
            print(f"✅ {file_path_str}")
            print(f"   {message}")
            fixed_count += 1
        else:
            print(f"⚠️  {file_path_str}")
            print(f"   {message}")

    print(f"\n修复了 {fixed_count} 个文件")


if __name__ == "__main__":
    main()
