#!/usr/bin/env python3
"""
检查所有文档的代码块围栏匹配状态
"""

from pathlib import Path

docs_dir = Path("docs")
md_files = list(docs_dir.rglob("*.md"))

unmatched_files = []

for md_file in md_files:
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
            fence_count = content.count('```')

        if fence_count % 2 != 0:
            relative_path = md_file.relative_to(docs_dir)
            unmatched_files.append((str(relative_path), fence_count))
    except Exception as e:
        print(f"错误读取 {md_file}: {e}")

if unmatched_files:
    print(f"❌ 发现 {len(unmatched_files)} 个文件代码块围栏不匹配:\n")
    for file_path, count in sorted(unmatched_files):
        print(f"   {file_path}: {count} 个```标记")
else:
    print("✅ 所有文档代码块围栏都匹配！")
