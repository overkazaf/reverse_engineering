#!/usr/bin/env python3
"""
基于规则的 Markdown 修复工具
不依赖 API，快速修复常见格式问题
"""

import re
import os
import sys
import argparse

def fix_markdown_with_rules(content, verbose=True):
    """使用规则修复 Markdown 内容"""

    original_length = len(content)
    original_content = content

    if verbose:
        print(f"\n   📏 原文件大小: {original_length:,} 字节\n")

    # 1. 修复标题格式 (# # → ##)
    count_before = len(re.findall(r'^(#+)\s+#', content, re.MULTILINE))
    content = re.sub(r'^(#+)\s+#', lambda m: '#' * (len(m.group(1)) + 1), content, flags=re.MULTILINE)
    count_after = len(re.findall(r'^(#+)\s+#', content, re.MULTILINE))
    if verbose and count_before > 0:
        print(f"   ✏️  规则 1: 修复标题格式 (# # → ##)")
        print(f"      修复了 {count_before - count_after} 处")

    # 2. 修复水平分隔线 (- -- → ---)
    count_before = len(re.findall(r'^-\s+--\n', content, re.MULTILINE))
    content = re.sub(r'^-\s+--\n', '---\n', content, flags=re.MULTILINE)
    count_after = len(re.findall(r'^-\s+--\n', content, re.MULTILINE))
    if verbose and count_before > 0:
        print(f"   ✏️  规则 2: 修复水平分隔线 (- -- → ---)")
        print(f"      修复了 {count_before - count_after} 处")

    # 3. 修复列表项符号 (☐ → -)
    count_before = len(re.findall(r'☐', content))
    content = re.sub(r'☐', '-', content)
    count_after = len(re.findall(r'☐', content))
    if verbose and count_before > 0:
        print(f"   ✏️  规则 3: 修复列表项符号 (☐ → -)")
        print(f"      修复了 {count_before - count_after} 处")

    # 4. 修复四个反引号 (```` → ```)
    count_before = len(re.findall(r'````', content))
    content = re.sub(r'````', '```', content)
    count_after = len(re.findall(r'````', content))
    if verbose and count_before > 0:
        print(f"   ✏️  规则 4: 修复四个反引号 (```` → ```)")
        print(f"      修复了 {count_before - count_after} 处")

    # 5. 修复标题后缺少空格 (##标题 → ## 标题)
    count_before = len(re.findall(r'^(#{1,6})([^\s#])', content, re.MULTILINE))
    content = re.sub(r'^(#{1,6})([^\s#])', r'\1 \2', content, flags=re.MULTILINE)
    count_after = len(re.findall(r'^(#{1,6})([^\s#])', content, re.MULTILINE))
    if verbose and count_before > 0:
        print(f"   ✏️  规则 5: 修复标题后缺少空格 (##标题 → ## 标题)")
        print(f"      修复了 {count_before - count_after} 处")

    # 6. 修复列表项后缺少空格 (如 -item → - item, *item → * item)
    count_before = len(re.findall(r'^(\s*[-*+])([^\s])', content, re.MULTILINE))
    content = re.sub(r'^(\s*[-*+])([^\s])', r'\1 \2', content, flags=re.MULTILINE)
    count_after = len(re.findall(r'^(\s*[-*+])([^\s])', content, re.MULTILINE))
    if verbose and count_before > 0:
        print(f"   ✏️  规则 6: 修复列表项后缺少空格 (-item → - item)")
        print(f"      修复了 {count_before - count_after} 处")

    # 7. 移除过多连续空行 (3个以上 → 2个)
    count_before = len(re.findall(r'\n{4,}', content))
    content = re.sub(r'\n{4,}', '\n\n\n', content)
    count_after = len(re.findall(r'\n{4,}', content))
    if verbose and count_before > 0:
        print(f"   ✏️  规则 7: 移除过多连续空行 (4+ 空行 → 3 空行)")
        print(f"      修复了 {count_before - count_after} 处")

    # 8. 修复中英文混排 - 代码块中的问题
    # 移除代码块标记中的空格
    count_before = len(re.findall(r'^```\s+([a-z]+)\s*$', content, re.MULTILINE))
    content = re.sub(r'^```\s+([a-z]+)\s*$', r'```\1', content, flags=re.MULTILINE)
    count_after = len(re.findall(r'^```\s+([a-z]+)\s*$', content, re.MULTILINE))
    if verbose and count_before > 0:
        print(f"   ✏️  规则 8: 修复代码块标记空格 (``` python → ```python)")
        print(f"      修复了 {count_before - count_after} 处")

    if verbose:
        print(f"\n   📊 修复总结:")
        print(f"      修复前: {original_length:,} 字节")
        print(f"      修复后: {len(content):,} 字节")
        print(f"      变化: {len(content) - original_length:+,} 字节")

    return content

def fix_file(input_file, output_file=None, backup=True, dry_run=False):
    """
    修复文件

    Args:
        input_file: 输入文件路径
        output_file: 输出文件路径（如果为None，则覆盖原文件）
        backup: 是否备份原文件
        dry_run: 是否为预览模式（不实际保存文件）
    """

    if not os.path.exists(input_file):
        print(f"❌ 文件不存在: {input_file}")
        return False

    print(f"📄 读取文件: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 分析格式问题
    print(f"\n🔍 分析格式问题:")
    hash_hash = len(re.findall(r'^#\s+#', content, re.MULTILINE))
    dash_dash = len(re.findall(r'^\s*-\s+--\s*$', content, re.MULTILINE))
    checkbox = len(re.findall(r'☐', content))
    quad_ticks = len(re.findall(r'````', content))

    print(f"   # # 标题: {hash_hash}")
    print(f"   - -- 分隔线: {dash_dash}")
    print(f"   ☐ 复选框: {checkbox}")
    print(f"   ```` 四引号: {quad_ticks}")

    if hash_hash == 0 and dash_dash == 0 and checkbox == 0 and quad_ticks == 0:
        print(f"\n✅ 文件格式正常，无需修复")
        return True

    # 应用修复
    print(f"\n🔧 应用规则修复...")
    fixed_content = fix_markdown_with_rules(content)

    # Dry run 模式：只显示结果，不保存
    if dry_run:
        print(f"\n👁️  预览模式 (--dry-run): 不会修改文件\n")

        # 显示修复前后的差异示例
        print("="*70)
        print("📋 修复示例 (前 30 行):")
        print("="*70)

        original_lines = content.split('\n')[:30]
        fixed_lines = fixed_content.split('\n')[:30]

        changes_shown = 0
        for i, (orig, fixed) in enumerate(zip(original_lines, fixed_lines), 1):
            if orig != fixed:
                print(f"\n行 {i}:")
                print(f"  - {repr(orig)}")
                print(f"  + {repr(fixed)}")
                changes_shown += 1
                if changes_shown >= 5:  # 只显示前 5 个变化
                    print(f"\n  ... (还有更多变化)")
                    break

        if changes_shown == 0:
            print("  (前 30 行没有变化)")

        print("\n" + "="*70)
        print(f"💡 如果满意，移除 --dry-run 参数重新运行以保存文件")
        print(f"   python3 fix_md_rules.py {input_file}")
        return True

    # 决定输出文件路径
    if output_file is None:
        output_file = input_file

    # 备份原文件
    if backup and output_file == input_file:
        backup_path = input_file + ".backup"
        print(f"\n💾 备份原文件到: {backup_path}")
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)

    # 保存修复后的文件
    print(f"💾 保存修复后的文件: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(fixed_content)

    print(f"\n✅ 修复完成!")

    if backup and output_file == input_file:
        print(f"📋 备份: {backup_path}")

    return True

def main():
    parser = argparse.ArgumentParser(
        description='使用规则修复 Markdown 文件格式（不使用 API）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 预览修复结果（不修改文件）
  python3 fix_md_rules.py input.md --dry-run

  # 修复文件（覆盖原文件，自动备份）
  python3 fix_md_rules.py input.md

  # 修复文件并保存到新文件
  python3 fix_md_rules.py input.md -o output.md

  # 修复文件，不备份
  python3 fix_md_rules.py input.md --no-backup
        """
    )

    parser.add_argument('input', help='输入的 Markdown 文件路径')
    parser.add_argument('-o', '--output', help='输出文件路径（默认覆盖原文件）')
    parser.add_argument('--no-backup', action='store_true', help='不备份原文件')
    parser.add_argument('--dry-run', action='store_true', help='预览模式，只显示修复结果，不修改文件')

    args = parser.parse_args()

    print("="*70)
    print("🔧 规则引擎 Markdown 修复工具")
    if args.dry_run:
        print("👁️  模式: 预览 (Dry Run)")
    print("="*70)

    success = fix_file(
        args.input,
        args.output,
        backup=not args.no_backup,
        dry_run=args.dry_run
    )

    print("\n" + "="*70)
    if success:
        print("🎉 修复成功！")
        if args.output:
            print(f"\n输出文件: {args.output}")
        else:
            print(f"\n文件已更新: {args.input}")
            if not args.no_backup:
                print(f"备份文件: {args.input}.backup")
    else:
        print("❌ 修复失败")
    print("="*70)

if __name__ == "__main__":
    main()
