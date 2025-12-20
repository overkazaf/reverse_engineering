#!/usr/bin/env python3
"""
修复文档之间的交叉引用链接
"""
import os
import re
from pathlib import Path

# 定义跨目录的相对链接修复规则
CROSS_REF_FIXES = {
    # 从03-Basic-Recipes引用到04-Advanced-Recipes的文件
    ('03-Basic-Recipes', './javascript_deobfuscation.md'): '../04-Advanced-Recipes/javascript_deobfuscation.md',
    ('03-Basic-Recipes', './captcha_bypass.md'): '../04-Advanced-Recipes/captcha_bypass.md',
    ('03-Basic-Recipes', './browser_fingerprinting.md'): '../04-Advanced-Recipes/browser_fingerprinting.md',

    # 从04-Advanced-Recipes引用到03-Basic-Recipes的文件
    ('04-Advanced-Recipes', './debugging_techniques.md'): '../03-Basic-Recipes/debugging_techniques.md',
    ('04-Advanced-Recipes', './dynamic_parameter_analysis.md'): '../03-Basic-Recipes/dynamic_parameter_analysis.md',
    ('04-Advanced-Recipes', './crypto_identification.md'): '../03-Basic-Recipes/crypto_identification.md',

    # 旧的03-Advanced-Topics引用（现在是04-Advanced-Recipes）
    ('03-Basic-Recipes', '../03-Advanced-Topics/crypto_identification.md'): '../03-Basic-Recipes/crypto_identification.md',
    ('04-Advanced-Recipes', '../03-Advanced-Topics/jsvmp.md'): './javascript_vm_protection.md',
}

def fix_links_in_file(filepath):
    """修复单个文件中的交叉引用链接"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    updated = False

    # 获取文件所在目录
    parent_dir = filepath.parent.name

    # 应用交叉引用修复规则
    for (source_dir, old_link), new_link in CROSS_REF_FIXES.items():
        if parent_dir == source_dir and old_link in content:
            content = content.replace(old_link, new_link)
            updated = True

    if updated:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    docs_dir = Path('docs')
    updated_files = []

    # 遍历所有.md文件
    for md_file in docs_dir.rglob('*.md'):
        if fix_links_in_file(md_file):
            updated_files.append(str(md_file))

    print(f"✅ 交叉引用修复完成！")
    print(f"📝 总共更新了 {len(updated_files)} 个文件")

    if updated_files:
        print("\n更新的文件列表:")
        for f in sorted(updated_files):
            print(f"  - {f}")

if __name__ == '__main__':
    main()
