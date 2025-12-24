#!/usr/bin/env python3
"""
为 Hugo 站点的所有目录创建缺失的 _index.md 文件
"""

import os
from pathlib import Path

# 目录名称到中文标题的映射
DIR_TITLES = {
    # Android sections
    "01-Recipes": "实战配方",
    "02-Tools": "工具指南",
    "03-Case-Studies": "案例研究",
    "04-Reference": "参考资料",
    "05-Appendix": "附录",

    # Android sub-sections
    "Analysis": "分析技术",
    "Anti-Detection": "反检测对抗",
    "Automation": "自动化工程",
    "Native": "Native 开发",
    "Network": "网络分析",
    "Scripts": "脚本集合",
    "Unpacking": "脱壳技术",
    "Dynamic": "动态分析工具",
    "Static": "静态分析工具",
    "Cheatsheets": "速查手册",
    "Advanced": "进阶主题",
    "Foundations": "基础知识",
    "Engineering": "工程实践",
    "Data-Analysis": "数据分析",

    # Web sections
    "01-Foundations": "基础知识",
    "02-Tooling": "工具指南",
    "03-Basic-Recipes": "基础配方",
    "04-Advanced-Recipes": "进阶配方",
    "05-Case-Studies": "案例研究",
    "06-Engineering": "工程实践",
    "07-Scripts": "脚本集合",
    "08-Cheat-Sheets": "速查手册",
    "09-Templates": "项目模板",
    "10-Troubleshooting": "问题排查",
    "11-Resources": "学习资源",
}

def get_title(dir_name: str) -> str:
    """获取目录的中文标题"""
    return DIR_TITLES.get(dir_name, dir_name.replace("-", " ").replace("_", " ").title())

def create_index_file(dir_path: Path, section: str):
    """为目录创建 _index.md"""
    index_path = dir_path / "_index.md"

    if index_path.exists():
        return False

    dir_name = dir_path.name
    title = get_title(dir_name)

    # 计算相对深度来确定 weight
    depth = len(dir_path.relative_to(Path("site/content")).parts)
    weight = depth * 10

    content = f"""---
title: "{title}"
weight: {weight}
---

{title}相关内容。
"""

    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"  Created: {index_path}")
    return True

def main():
    content_dir = Path("site/content")
    created = 0

    # 遍历所有目录
    for root, dirs, files in os.walk(content_dir):
        root_path = Path(root)

        # 跳过 content 根目录
        if root_path == content_dir:
            continue

        # 检查是否有子目录或 .md 文件
        has_content = any(f.endswith('.md') for f in files) or len(dirs) > 0

        if has_content:
            # 确定 section (android 或 web)
            rel_path = root_path.relative_to(content_dir)
            section = rel_path.parts[0] if rel_path.parts else ""

            if create_index_file(root_path, section):
                created += 1

    print(f"\nCreated {created} _index.md files")

if __name__ == "__main__":
    main()
