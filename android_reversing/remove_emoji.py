#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Emoji清理工具
移除markdown文档中过多的emoji表情，保留提问相关的emoji

保留的emoji：
- ❓ 🤔 💡 - 提问、思考、建议
- ⚠️ ❌ ✅ - 警告、错误、成功（重要标记）

移除的emoji：
- 装饰性emoji（🚀 ⚡ 📱 🔧 等）
- 过度AI风格的emoji

使用方法：
python remove_emoji.py                 # 预览将要移除的emoji
python remove_emoji.py --fix           # 执行清理
python remove_emoji.py --aggressive    # 激进模式（移除更多）
"""

import os
import re
import yaml
import argparse
from pathlib import Path
from typing import List, Dict, Set
from datetime import datetime


class EmojiCleaner:
    """Emoji清理器"""

    # 保留的emoji（提问、警告相关）
    KEEP_EMOJIS = {
        '❓', '🤔', '💡',  # 提问、思考、建议
        '⚠️', '⚠', '❌', '✅',  # 警告、错误、成功
        '⚡',  # 重要提示
        '📝',  # 注意事项
    }

    # 标题中常见的装饰性emoji（会被移除）
    DECORATIVE_EMOJIS = {
        '🚀', '📱', '🔧', '⚙️', '🛠️', '📖', '💼', '📚', '📎',
        '🎯', '🔍', '📊', '📄', '📁', '🎉', '✨', '🌟', '⭐',
        '🔥', '💪', '👍', '👌', '🎓', '📌', '🔗', '💻', '🖥️',
        '📲', '🌐', '🔒', '🔓', '🎨', '🏗️', '🌈', '💎', '🎪',
        '🎭', '🎬', '🎮', '🎯', '🏆', '🎁', '🎊', '🎈', '🚩',
    }

    # 章节标题emoji（可能需要保留用于导航，但可选移除）
    SECTION_EMOJIS = {
        '🏠', '📱', '🛠️', '🔧', '🚀', '⚙️', '📖', '💼',
        '📚', '📎', '📊', '📝',
    }

    def __init__(self, docs_dir="docs", mkdocs_file="mkdocs.yml", aggressive=False):
        self.docs_dir = docs_dir
        self.mkdocs_file = mkdocs_file
        self.aggressive = aggressive
        self.files_to_clean = []
        self.emoji_stats = {}
        self.changes_made = {}

    def scan_all_files(self):
        """扫描所有markdown文件"""
        print("\n🔍 扫描所有markdown文件...")

        try:
            with open(self.mkdocs_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                nav = config.get('nav', [])
        except:
            print("❌ 无法读取mkdocs.yml")
            return []

        def collect_files(items):
            files = []
            for item in items:
                if isinstance(item, dict):
                    for title, path in item.items():
                        if isinstance(path, str) and path.endswith('.md'):
                            file_path = os.path.join(self.docs_dir, path)
                            if os.path.exists(file_path):
                                files.append(file_path)
                        elif isinstance(path, list):
                            files.extend(collect_files(path))
            return files

        for section in nav:
            if isinstance(section, dict):
                for section_name, items in section.items():
                    if isinstance(items, list):
                        self.files_to_clean.extend(collect_files(items))

        print(f"✅ 找到 {len(self.files_to_clean)} 个markdown文件")
        return self.files_to_clean

    def analyze_file(self, file_path):
        """分析文件中的emoji使用情况"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            return {}

        emoji_count = {}

        # 使用正则查找所有emoji（精确匹配emoji符号）
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # 表情符号
            "\U0001F300-\U0001F5FF"  # 符号和象形文字
            "\U0001F680-\U0001F6FF"  # 交通和地图
            "\U0001F1E0-\U0001F1FF"  # 国旗
            "\U00002600-\U000027BF"  # 杂项符号
            "\U0001F900-\U0001F9FF"  # 补充符号和象形文字
            "\U0001FA70-\U0001FAFF"  # 扩展符号
            "\U00002300-\U000023FF"  # 技术符号
            "⚠️⚡✅❌❓💡📝🚀📱🔧⚙️🛠️📖💼📚📎"  # 常见emoji
            "🎯🔍📊📄📁🎉✨🌟⭐🔥💪👍👌🎓📌🔗💻🖥️"
            "]+",
            flags=re.UNICODE
        )

        for emoji in emoji_pattern.findall(content):
            for char in emoji:
                emoji_count[char] = emoji_count.get(char, 0) + 1

        return emoji_count

    def should_remove_emoji(self, emoji, context=''):
        """判断是否应该移除该emoji"""
        # 保留的emoji
        if emoji in self.KEEP_EMOJIS:
            return False

        # 激进模式：移除更多
        if self.aggressive:
            # 激进模式下，只保留KEEP_EMOJIS
            return True

        # 普通模式：移除装饰性emoji
        if emoji in self.DECORATIVE_EMOJIS:
            return True

        # 检查是否在标题中
        if context.startswith('#'):
            # 标题中的emoji，根据是否在SECTION_EMOJIS中判断
            if emoji in self.SECTION_EMOJIS:
                return False  # 保留章节emoji用于导航
            return True  # 移除其他标题emoji

        return False

    def clean_file(self, file_path, create_backup=True):
        """清理单个文件中的emoji"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"❌ 无法读取 {file_path}: {e}")
            return 0

        original_content = ''.join(lines)
        cleaned_lines = []
        changes = 0

        for line in lines:
            cleaned_line = line
            original_line = line

            # 检测emoji并决定是否移除
            emoji_pattern = re.compile(
                "["
                "\U0001F600-\U0001F64F"  # 表情符号
                "\U0001F300-\U0001F5FF"  # 符号和象形文字
                "\U0001F680-\U0001F6FF"  # 交通和地图
                "\U0001F1E0-\U0001F1FF"  # 国旗
                "\U00002600-\U000027BF"  # 杂项符号
                "\U0001F900-\U0001F9FF"  # 补充符号
                "\U0001FA70-\U0001FAFF"  # 扩展符号
                "\U00002300-\U000023FF"  # 技术符号
                "⚠️⚡✅❌❓💡📝🚀📱🔧⚙️🛠️📖💼📚📎"
                "🎯🔍📊📄📁🎉✨🌟⭐🔥💪👍👌🎓📌🔗💻🖥️"
                "]+",
                flags=re.UNICODE
            )

            def remove_emoji(match):
                emoji = match.group()
                # 判断每个emoji字符
                result = ''
                for char in emoji:
                    if not self.should_remove_emoji(char, cleaned_line):
                        result += char
                return result

            cleaned_line = emoji_pattern.sub(remove_emoji, cleaned_line)

            # 清理多余空格（emoji移除后可能留下）
            cleaned_line = re.sub(r'  +', ' ', cleaned_line)
            cleaned_line = re.sub(r'^ +', '', cleaned_line, flags=re.MULTILINE)

            if cleaned_line != original_line:
                changes += 1

            cleaned_lines.append(cleaned_line)

        if changes > 0:
            # 备份原文件
            if create_backup:
                backup_path = f"{file_path}.backup.emoji.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(original_content)

            # 写入清理后的内容
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(cleaned_lines)
            except Exception as e:
                print(f"❌ 无法写入 {file_path}: {e}")
                return 0

        return changes

    def clean_all_files(self, create_backup=True):
        """清理所有文件"""
        print("\n🧹 开始清理emoji...")
        print("=" * 60)

        mode = "激进模式" if self.aggressive else "标准模式"
        print(f"清理模式: {mode}")
        print(f"保留emoji: {' '.join(self.KEEP_EMOJIS)}")
        print("=" * 60)

        total_changes = 0

        for file_path in self.files_to_clean:
            file_name = os.path.relpath(file_path, self.docs_dir)
            changes = self.clean_file(file_path, create_backup)

            if changes > 0:
                print(f"✅ {file_name}: 清理 {changes} 处")
                self.changes_made[file_path] = changes
                total_changes += changes
            else:
                print(f"   {file_name}: 无需清理")

        print("\n" + "=" * 60)
        print(f"🎉 完成！总计清理 {total_changes} 处emoji")
        print(f"   清理的文件: {len(self.changes_made)}/{len(self.files_to_clean)}")

        return total_changes

    def preview_changes(self):
        """预览将要清理的emoji"""
        print("\n📋 预览emoji使用情况...")
        print("=" * 60)

        all_emojis = {}

        for file_path in self.files_to_clean[:10]:  # 预览前10个文件
            emoji_count = self.analyze_file(file_path)
            for emoji, count in emoji_count.items():
                all_emojis[emoji] = all_emojis.get(emoji, 0) + count

        if not all_emojis:
            print("未发现emoji")
            return

        print("发现的emoji（按使用频率排序）：\n")

        # 分类显示
        will_keep = []
        will_remove = []

        for emoji, count in sorted(all_emojis.items(), key=lambda x: x[1], reverse=True):
            if emoji in self.KEEP_EMOJIS:
                will_keep.append((emoji, count))
            else:
                will_remove.append((emoji, count))

        print("✅ 将保留的emoji:")
        for emoji, count in will_keep:
            print(f"   {emoji} - 使用 {count} 次")

        print("\n❌ 将移除的emoji:")
        for emoji, count in will_remove:
            print(f"   {emoji} - 使用 {count} 次")

        print("\n" + "=" * 60)
        print(f"总计: {len(will_keep)} 个保留, {len(will_remove)} 个移除")

    def generate_report(self):
        """生成清理报告"""
        report_path = "output/emoji_cleanup_report.md"
        os.makedirs("output", exist_ok=True)

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# Emoji清理报告\n\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## 📊 统计摘要\n\n")
            f.write(f"- 扫描文件数: {len(self.files_to_clean)}\n")
            f.write(f"- 清理文件数: {len(self.changes_made)}\n")
            f.write(f"- 总清理数: {sum(self.changes_made.values())}\n\n")

            f.write("## ✅ 保留的emoji\n\n")
            for emoji in self.KEEP_EMOJIS:
                f.write(f"- {emoji}\n")

            if self.changes_made:
                f.write("\n## 📝 清理详情\n\n")
                for file_path, count in sorted(self.changes_made.items()):
                    rel_path = os.path.relpath(file_path, self.docs_dir)
                    f.write(f"- `{rel_path}`: {count} 处清理\n")

        print(f"\n📄 报告已生成: {report_path}")
        return report_path


def main():
    parser = argparse.ArgumentParser(
        description='Emoji清理工具 - 移除过多的装饰性emoji',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--fix', action='store_true',
                       help='执行清理（默认只预览）')
    parser.add_argument('--aggressive', action='store_true',
                       help='激进模式（移除更多emoji）')
    parser.add_argument('--no-backup', action='store_true',
                       help='不创建备份文件')

    args = parser.parse_args()

    print("╔══════════════════════════════════════════════════╗")
    print("║            Emoji清理工具                         ║")
    print("╚══════════════════════════════════════════════════╝")

    cleaner = EmojiCleaner(aggressive=args.aggressive)

    # 扫描文件
    cleaner.scan_all_files()

    if args.fix:
        # 执行清理
        total_changes = cleaner.clean_all_files(create_backup=not args.no_backup)

        # 生成报告
        cleaner.generate_report()

        if total_changes > 0:
            print("\n💡 建议:")
            print("   1. 使用 git diff 查看修改")
            print("   2. 重新生成PDF: python docs_to_pdf_final.py --no-cache")
            print("   3. 如有问题，备份文件位于: *.backup.emoji.*")
    else:
        # 预览模式
        cleaner.preview_changes()
        print("\n⚠️  这是预览模式，未执行清理")
        print("   添加 --fix 参数执行清理: python remove_emoji.py --fix")
        print("   添加 --aggressive 使用激进模式: python remove_emoji.py --fix --aggressive")


if __name__ == "__main__":
    main()
