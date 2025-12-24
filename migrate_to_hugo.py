#!/usr/bin/env python3
"""
将 MkDocs 内容迁移到 Hugo 格式
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime

# 源目录和目标目录
ANDROID_SRC = Path("android_reversing/docs")
WEB_SRC = Path("web_reversing/docs")
ANDROID_DST = Path("site/content/android")
WEB_DST = Path("site/content/web")

# 排除的文件和目录
EXCLUDE_PATTERNS = [
    "custom_theme",
    "images",
    "manage.py",
    "pdf_style.css",
    ".claude",
    ".DS_Store",
]


def extract_title_from_content(content: str) -> str:
    """从 markdown 内容中提取标题"""
    # 尝试匹配第一个 # 标题
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return ""


def has_front_matter(content: str) -> bool:
    """检查内容是否已有 front matter"""
    return content.strip().startswith('---')


def create_front_matter(title: str, weight: int = 10, description: str = "") -> str:
    """创建 Hugo front matter"""
    fm = f"""---
title: "{title}"
weight: {weight}
"""
    if description:
        fm += f'description: "{description}"\n'
    fm += "---\n\n"
    return fm


def process_markdown_file(src_path: Path, dst_path: Path, section: str):
    """处理单个 markdown 文件"""
    with open(src_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 如果已有 front matter，直接复制
    if has_front_matter(content):
        final_content = content
    else:
        # 提取标题
        title = extract_title_from_content(content)
        if not title:
            title = src_path.stem.replace('_', ' ').replace('-', ' ').title()

        # 根据文件名确定权重
        weight = 10
        name = src_path.stem
        if name == "index" or name == "_index":
            weight = 1
        elif re.match(r'^[A-Z]\d+', name):
            # 如 R01, T02, F03 等编号
            match = re.match(r'^[A-Z](\d+)', name)
            if match:
                weight = int(match.group(1))

        # 创建 front matter
        front_matter = create_front_matter(title, weight)
        final_content = front_matter + content

    # 修复内部链接
    # 将 ../../../ 等相对路径转换为 Hugo 格式
    final_content = fix_internal_links(final_content, src_path, section)

    # 确保目标目录存在
    dst_path.parent.mkdir(parents=True, exist_ok=True)

    # 写入文件
    with open(dst_path, 'w', encoding='utf-8') as f:
        f.write(final_content)

    print(f"  ✓ {src_path} -> {dst_path}")


def fix_internal_links(content: str, src_path: Path, section: str) -> str:
    """修复内部链接"""
    # 这里可以根据需要添加链接修复逻辑
    # 目前保持原样，Hugo 会自动处理大部分情况
    return content


def should_exclude(path: Path) -> bool:
    """检查是否应该排除该路径"""
    for pattern in EXCLUDE_PATTERNS:
        if pattern in str(path):
            return True
    return False


def migrate_section(src_dir: Path, dst_dir: Path, section: str):
    """迁移一个 section 的所有内容"""
    print(f"\n迁移 {section} 内容...")

    # 创建目标目录
    dst_dir.mkdir(parents=True, exist_ok=True)

    # 遍历源目录
    for src_path in src_dir.rglob("*.md"):
        if should_exclude(src_path):
            continue

        # 计算相对路径和目标路径
        rel_path = src_path.relative_to(src_dir)
        dst_path = dst_dir / rel_path

        # 处理 index.md -> _index.md 转换
        if src_path.name == "index.md":
            dst_path = dst_path.parent / "_index.md"

        process_markdown_file(src_path, dst_path, section)


def create_section_index(dst_dir: Path, title: str, description: str):
    """创建 section 索引页面"""
    index_path = dst_dir / "_index.md"

    content = f"""---
title: "{title}"
weight: 1
description: "{description}"
---

{description}

请从左侧导航或下方列表选择具体章节。
"""

    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"  ✓ 创建索引: {index_path}")


def main():
    print("开始迁移内容到 Hugo 格式...\n")

    # 创建 section 索引
    create_section_index(
        ANDROID_DST,
        "Android 逆向工程 Cookbook",
        "Android 逆向工程实战手册，涵盖 Frida、Xposed、脱壳、反混淆等核心技术。"
    )

    create_section_index(
        WEB_DST,
        "Web 逆向工程 Cookbook",
        "Web 逆向工程实战手册，涵盖 JavaScript 反混淆、反爬虫、抓包分析等技术。"
    )

    # 迁移 Android 内容
    migrate_section(ANDROID_SRC, ANDROID_DST, "android")

    # 迁移 Web 内容
    migrate_section(WEB_SRC, WEB_DST, "web")

    print("\n迁移完成!")


if __name__ == "__main__":
    main()
