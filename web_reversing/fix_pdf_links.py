#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复PDF中的内部链接
将指向.md文件的链接转换为PDF内部的锚点引用
"""
import os
import re
import yaml
from pathlib import Path
from urllib.parse import unquote


class PDFLinkFixer:
    """修复PDF中的Markdown链接"""

    def __init__(self, mkdocs_file="mkdocs.yml", docs_dir="docs"):
        self.mkdocs_file = mkdocs_file
        self.docs_dir = docs_dir
        self.file_to_anchor = {}  # 文件路径 -> 锚点ID的映射
        self.file_to_title = {}   # 文件路径 -> 标题的映射
        self.build_file_mapping()

    def build_file_mapping(self):
        """从mkdocs.yml构建文件路径到锚点的映射"""
        try:
            with open(self.mkdocs_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                nav_structure = config.get('nav', [])

            def process_nav_items(items, section_prefix=""):
                """递归处理导航项"""
                counter = 0
                if isinstance(items, list):
                    for item in items:
                        if isinstance(item, dict):
                            for title, path_or_subitems in item.items():
                                if isinstance(path_or_subitems, str):
                                    # 是文件路径
                                    counter += 1
                                    # 创建唯一的锚点ID
                                    # 使用文件路径作为基础，去掉.md后缀
                                    file_key = path_or_subitems.replace('.md', '')
                                    # 转换为合法的HTML ID
                                    anchor_id = file_key.replace('/', '-').replace('_', '-')

                                    self.file_to_anchor[path_or_subitems] = anchor_id
                                    self.file_to_title[path_or_subitems] = title

                                    print(f"  映射: {path_or_subitems} -> #{anchor_id}")

                                elif isinstance(path_or_subitems, list):
                                    # 递归处理子项
                                    process_nav_items(path_or_subitems, title)

            print("📋 构建文件到锚点的映射...")
            for section in nav_structure:
                if isinstance(section, dict):
                    for section_name, items in section.items():
                        if isinstance(items, list):
                            process_nav_items(items, section_name)
                        elif isinstance(items, str):
                            # 处理单个文件
                            file_key = items.replace('.md', '')
                            anchor_id = file_key.replace('/', '-').replace('_', '-')
                            self.file_to_anchor[items] = anchor_id
                            self.file_to_title[items] = section_name

            print(f"✅ 已创建 {len(self.file_to_anchor)} 个文件映射")

        except Exception as e:
            print(f"❌ 构建映射失败: {e}")
            import traceback
            traceback.print_exc()

    def resolve_relative_path(self, current_file, relative_path):
        """解析相对路径为绝对路径"""
        # 获取当前文件的目录
        current_dir = os.path.dirname(current_file)
        # 合并路径
        absolute_path = os.path.normpath(os.path.join(current_dir, relative_path))
        # 确保路径使用正斜杠
        absolute_path = absolute_path.replace('\\', '/')
        return absolute_path

    def fix_markdown_links(self, content, current_file_path):
        """
        修复Markdown内容中的链接

        Args:
            content: Markdown内容
            current_file_path: 当前文件的路径（相对于docs目录）

        Returns:
            修复后的内容
        """
        # 匹配Markdown链接: [text](path)
        # 同时支持带锚点的链接: [text](path#anchor)
        link_pattern = r'\[([^\]]+)\]\(([^)]+\.md(?:#[^)]*)?)\)'

        def replace_link(match):
            link_text = match.group(1)
            link_path = match.group(2)

            # 分离文件路径和锚点
            if '#' in link_path:
                file_part, anchor_part = link_path.split('#', 1)
                has_anchor = True
            else:
                file_part = link_path
                anchor_part = ""
                has_anchor = False

            # 跳过外部链接（包含http://或https://）
            if file_part.startswith('http://') or file_part.startswith('https://'):
                return match.group(0)

            # 解析相对路径
            if file_part.startswith('./') or file_part.startswith('../'):
                # 相对路径
                target_file = self.resolve_relative_path(current_file_path, file_part)
            else:
                # 假设是相对于docs根目录的路径
                target_file = file_part

            # 查找目标文件的锚点
            if target_file in self.file_to_anchor:
                anchor_id = self.file_to_anchor[target_file]
                # 如果原链接有锚点，将其转换为合法的HTML ID并附加
                if has_anchor:
                    # 保留原有的锚点，但需要确保它是合法的
                    safe_anchor = anchor_part.replace('_', '-').lower()
                    full_anchor = f"{anchor_id}-{safe_anchor}"
                else:
                    full_anchor = anchor_id

                # 返回新的链接格式
                new_link = f"[{link_text}](#{full_anchor})"
                print(f"    🔗 修复链接: {file_part} -> #{full_anchor}")
                return new_link
            else:
                # 文件未在映射中找到，尝试其他可能的路径
                # 有时候路径可能有细微差别，尝试模糊匹配
                for known_file, anchor_id in self.file_to_anchor.items():
                    if known_file.endswith(os.path.basename(target_file)):
                        new_link = f"[{link_text}](#{anchor_id})"
                        print(f"    🔗 模糊匹配: {file_part} -> {known_file} -> #{anchor_id}")
                        return new_link

                # 如果找不到，保持原样但给出警告
                print(f"    ⚠️  未找到映射: {target_file}")
                return match.group(0)

        # 替换所有链接
        fixed_content = re.sub(link_pattern, replace_link, content)
        return fixed_content

    def get_anchor_id_for_file(self, file_path):
        """获取文件对应的锚点ID"""
        return self.file_to_anchor.get(file_path, None)

    def get_title_for_file(self, file_path):
        """获取文件对应的标题"""
        return self.file_to_title.get(file_path, os.path.basename(file_path))


def test_link_fixer():
    """测试链接修复功能"""
    print("🧪 测试链接修复功能...")
    print("=" * 60)

    fixer = PDFLinkFixer()

    # 测试用例
    test_cases = [
        {
            "current_file": "03-Basic-Recipes/re_workflow.md",
            "content": """
参考资料:
- [调试技巧](./debugging_techniques.md)
- [JavaScript 反混淆](../04-Advanced-Recipes/javascript_deobfuscation.md)
- [API 接口逆向](./api_reverse_engineering.md#section1)
            """,
        },
        {
            "current_file": "04-Advanced-Recipes/captcha_bypass.md",
            "content": """
相关章节:
- [浏览器指纹识别](./browser_fingerprinting.md)
- [Puppeteer 工具](../02-Tooling/puppeteer_playwright.md)
- [动态参数分析](../03-Basic-Recipes/dynamic_parameter_analysis.md)
            """,
        }
    ]

    for i, test in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}:")
        print(f"当前文件: {test['current_file']}")
        print("原始内容:")
        print(test['content'])

        fixed = fixer.fix_markdown_links(test['content'], test['current_file'])
        print("\n修复后内容:")
        print(fixed)
        print("-" * 60)


if __name__ == "__main__":
    test_link_fixer()
