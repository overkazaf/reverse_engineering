#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Docs to PDF Converter - Web RE Cookbook Edition (Improved)
支持指定章节范围的PDF生成

使用方法:
# 生成全部章节
python docs_to_pdf_improved.py

# 生成 Part I 和 Part II
python docs_to_pdf_improved.py --parts 1-2

# 生成特定的 Parts
python docs_to_pdf_improved.py --parts 1,3

# 生成特定的章节
python docs_to_pdf_improved.py --sections "Foundations,Tooling"

# 列出所有可用的章节
python docs_to_pdf_improved.py --list

# 指定输出文件名
python docs_to_pdf_improved.py --output my_cookbook.pdf --parts 1-2
"""

import os
import re
import yaml
import argparse
from datetime import datetime
import markdown2
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from fix_pdf_links import PDFLinkFixer


class ChineseCommentTranslator:
    """翻译代码中的中文注释为英文"""

    def __init__(self, use_ai=True):
        self.use_ai = use_ai
        self.translation_cache = {}

    def is_chinese(self, text):
        """检测文本是否包含中文"""
        return bool(re.search(r'[\u4e00-\u9fa5]', text))

    def translate_text(self, text):
        """翻译单行文本"""
        if not self.is_chinese(text):
            return text

        # 检查缓存
        if text in self.translation_cache:
            return self.translation_cache[text]

        # 简单的词汇替换（回退方案）
        replacements = {
            '绕过': 'Bypass',
            '反调试': 'Anti-Debugging',
            '检测': 'Detection',
            '策略': 'Strategy',
            '修改': 'Modify',
            '拦截': 'Intercept',
            '返回': 'Return',
            '调用': 'Call',
            '函数': 'Function',
            '方法': 'Method',
            '类': 'Class',
            '对象': 'Object',
            '参数': 'Parameter',
            '变量': 'Variable',
            '注释': 'Comment',
            '代码': 'Code',
            '脚本': 'Script',
            '配置': 'Config',
            '设置': 'Setting',
            '初始化': 'Initialize',
            '处理': 'Process',
            '解析': 'Parse',
            '生成': 'Generate',
            '创建': 'Create',
            '删除': 'Delete',
            '更新': 'Update',
            '查询': 'Query',
            '插入': 'Insert',
            '获取': 'Get',
            '设置': 'Set',
            '判断': 'Check',
            '如果': 'If',
            '否则': 'Else',
            '循环': 'Loop',
            '遍历': 'Iterate',
            '打印': 'Print',
            '输出': 'Output',
            '输入': 'Input',
            '读取': 'Read',
            '写入': 'Write',
            '文件': 'File',
            '目录': 'Directory',
            '路径': 'Path',
            '数据': 'Data',
            '结果': 'Result',
            '错误': 'Error',
            '异常': 'Exception',
            '成功': 'Success',
            '失败': 'Failed',
            '开始': 'Start',
            '结束': 'End',
        }

        result = text
        for zh, en in replacements.items():
            result = result.replace(zh, en)

        self.translation_cache[text] = result
        return result

    def translate_code_block(self, code, language=''):
        """翻译代码块中的中文注释"""
        lines = code.split('\n')
        translated_lines = []

        for line in lines:
            # 检测各种注释格式
            comment_patterns = [
                (r'^(\s*//\s*)(.+)$', r'\1'),           # JavaScript, Java, C++ single line
                (r'^(\s*#\s*)(.+)$', r'\1'),            # Python, Shell
                (r'^(\s*/\*\s*)(.+)(\s*\*/)$', r'\1'),  # C-style block comment
                (r'^(\s*<!--\s*)(.+)(\s*-->)$', r'\1'), # HTML comment
                (r'^(\s*--\s*)(.+)$', r'\1'),           # SQL, Lua
            ]

            translated = False
            for pattern, prefix_group in comment_patterns:
                match = re.match(pattern, line)
                if match:
                    # 提取注释部分
                    if len(match.groups()) == 2:
                        prefix = match.group(1)
                        comment = match.group(2)
                        if self.is_chinese(comment):
                            translated_comment = self.translate_text(comment)
                            translated_lines.append(prefix + translated_comment)
                            translated = True
                            break
                    elif len(match.groups()) == 3:
                        prefix = match.group(1)
                        comment = match.group(2)
                        suffix = match.group(3)
                        if self.is_chinese(comment):
                            translated_comment = self.translate_text(comment)
                            translated_lines.append(prefix + translated_comment + suffix)
                            translated = True
                            break

            if not translated:
                # 行内注释处理
                inline_pattern = r'(.+?)(//|#)(\s*)(.+)$'
                match = re.match(inline_pattern, line)
                if match and self.is_chinese(match.group(4)):
                    code_part = match.group(1)
                    comment_marker = match.group(2)
                    space = match.group(3)
                    comment = match.group(4)
                    translated_comment = self.translate_text(comment)
                    translated_lines.append(code_part + comment_marker + space + translated_comment)
                else:
                    translated_lines.append(line)

        return '\n'.join(translated_lines)


class DocsToPDFConverter:
    def __init__(self, docs_dir="docs", mkdocs_file="mkdocs.yml", translate_comments=False,
                 parts_filter=None, sections_filter=None):
        self.docs_dir = docs_dir
        self.mkdocs_file = mkdocs_file
        self.translate_comments = translate_comments
        self.parts_filter = parts_filter  # 例如: [1, 2] 或 range(1, 3)
        self.sections_filter = sections_filter  # 例如: ["Foundations", "Tooling"]
        self.output_dir = "output"
        self.nav_structure = []
        self.font_config = FontConfiguration()
        self.translator = ChineseCommentTranslator()

        # 初始化链接修复器
        self.link_fixer = PDFLinkFixer(mkdocs_file=mkdocs_file, docs_dir=docs_dir)

        # 作者信息
        self.author_email = "overkazaf@gmail.com"
        self.author_wechat = "_0xAF_"
        self.generation_date = datetime.now().strftime('%Y-%m-%d')

        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)

    def load_navigation_structure(self):
        """从mkdocs.yml加载导航结构"""
        try:
            with open(self.mkdocs_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                self.nav_structure = config.get('nav', [])
                print(f"✅ 已加载导航结构，共 {len(self.nav_structure)} 个主要部分")
                return self.nav_structure
        except Exception as e:
            print(f"❌ 加载mkdocs.yml失败: {e}")
            return []

    def list_available_sections(self):
        """列出所有可用的章节"""
        if not self.nav_structure:
            self.load_navigation_structure()

        print("\n📚 可用章节列表:")
        print("=" * 60)

        part_num = 0
        for section in self.nav_structure:
            if isinstance(section, dict):
                for section_name, items in section.items():
                    # 检测是否是 Part
                    if section_name.startswith('Part '):
                        part_num += 1
                        print(f"\n🔹 Part {part_num}: {section_name}")
                    else:
                        print(f"\n🔹 {section_name}")

                    # 递归列出所有子章节
                    def list_items(items, indent=2):
                        if isinstance(items, list):
                            for item in items:
                                if isinstance(item, dict):
                                    for title, path_or_subitems in item.items():
                                        if isinstance(path_or_subitems, str):
                                            print(f"{' ' * indent}• {title}")
                                        elif isinstance(path_or_subitems, list):
                                            print(f"{' ' * indent}📂 {title}")
                                            list_items(path_or_subitems, indent + 2)

                    if isinstance(items, list):
                        list_items(items)

        print("\n" + "=" * 60)
        print(f"\n总计 {part_num} 个 Part")
        print("\n使用方法:")
        print("  --parts 1-2      : 生成 Part 1 到 Part 2")
        print("  --parts 1,3      : 生成 Part 1 和 Part 3")
        print("  --sections \"Foundations,Tooling\" : 生成指定章节")

    def should_include_section(self, section_name, part_index):
        """判断是否应该包含该章节"""
        # 如果没有设置任何过滤器，包含所有章节
        if not self.parts_filter and not self.sections_filter:
            return True

        # 按 Part 过滤
        if self.parts_filter and section_name.startswith('Part '):
            return part_index in self.parts_filter

        # 按章节名称过滤
        if self.sections_filter:
            # 提取实际的章节名称（去除 Part 前缀）
            actual_section_name = section_name
            if ':' in section_name:
                actual_section_name = section_name.split(':', 1)[1].strip()

            return actual_section_name in self.sections_filter

        # Home 默认不包含（除非明确指定）
        if section_name == "Home":
            return False

        return True

    def create_css_styles(self):
        """创建PDF样式"""
        css_content = """
        @font-face {
            font-family: 'Chinese Sans';
            src: url('file:///System/Library/Fonts/Hiragino Sans GB.ttc') format('truetype'),
                 url('file:///System/Library/Fonts/STHeiti Light.ttc') format('truetype'),
                 url('file:///System/Library/Fonts/Supplemental/Songti.ttc') format('truetype');
            font-weight: normal;
        }

        @font-face {
            font-family: 'Code Font';
            src: url('file:///System/Library/Fonts/Menlo.ttc') format('truetype'),
                 url('file:///System/Library/Fonts/Monaco.dfont') format('truetype');
        }

        @page {
            size: A4;
            margin: 2.5cm 2cm 3cm 2cm;

            @top-left {
                content: "Web Reverse Engineering Cookbook";
                font-family: 'Chinese Sans', sans-serif;
                font-size: 10pt;
                color: #666;
            }

            @top-right {
                content: "Page " counter(page);
                font-family: 'Chinese Sans', sans-serif;
                font-size: 10pt;
                color: #666;
            }
        }

        body {
            font-family: 'Chinese Sans', 'Noto Sans SC', sans-serif;
            font-size: 11pt;
            line-height: 1.8;
            color: #333;
        }

        h1 {
            font-size: 24pt;
            font-weight: 700;
            color: #1a1a1a;
            margin-top: 30pt;
            margin-bottom: 20pt;
            page-break-before: always;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10pt;
        }

        h1.no-page-break {
            page-break-before: auto;
        }

        h2 {
            font-size: 18pt;
            font-weight: 600;
            color: #2c3e50;
            margin-top: 25pt;
            margin-bottom: 15pt;
            border-left: 4px solid #4CAF50;
            padding-left: 15pt;
        }

        h3 {
            font-size: 14pt;
            font-weight: 500;
            color: #34495e;
            margin-top: 20pt;
            margin-bottom: 12pt;
        }

        code {
            font-family: 'Code Font', 'Menlo', 'Monaco', monospace;
            font-size: 9pt;
            background-color: #f8f9fa;
            padding: 2pt 4pt;
            border-radius: 3pt;
        }

        pre {
            font-family: 'Code Font', monospace;
            font-size: 8.5pt;
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            padding: 12pt;
            margin: 12pt 0;
            white-space: pre-wrap;
            word-wrap: break-word;
            page-break-inside: avoid;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin: 15pt 0;
            page-break-inside: avoid;
        }

        th, td {
            border: 1px solid #ddd;
            padding: 8pt;
            text-align: left;
        }

        th {
            background-color: #f8f9fa;
            font-weight: 600;
        }

        .cover-page {
            text-align: center;
            page-break-after: always;
        }
        """

        return CSS(string=css_content, font_config=self.font_config)

    def create_cover_page(self):
        """创建封面页面"""
        # 生成过滤信息
        filter_info = ""
        if self.parts_filter:
            parts_str = ', '.join(map(str, sorted(self.parts_filter)))
            filter_info = f"<p style='font-size: 12pt; color: #888;'>包含章节: Part {parts_str}</p>"
        elif self.sections_filter:
            sections_str = ', '.join(self.sections_filter)
            filter_info = f"<p style='font-size: 12pt; color: #888;'>包含章节: {sections_str}</p>"

        cover_html = f"""
        <div class="cover-page">
            <div style="margin-top: 150pt;">
                <h1 style="font-size: 36pt; color: #1a1a1a; margin-bottom: 30pt; border: none; page-break-before: auto;" class="no-page-break">
                    Web Reverse Engineering Cookbook
                </h1>
                <h2 style="font-size: 20pt; color: #666; font-weight: 400; border: none; padding: 0;">
                    Complete Guide to Web Security Analysis
                </h2>
                {filter_info}
                <div style="margin-top: 80pt; font-size: 14pt; color: #888;">
                    <p>Author: +5</p>
                    <p>📧 {self.author_email}</p>
                    <p>💬 {self.author_wechat}</p>
                    <p>📅 {self.generation_date}</p>
                </div>
            </div>
        </div>
        """
        return cover_html

    def create_table_of_contents(self, filtered_structure):
        """创建目录页面（仅包含过滤后的章节）"""
        toc_html = """
        <div class="toc-page" style="page-break-after: always;">
            <h1 class="toc-title no-page-break" style="font-size: 28pt; text-align: center; margin-bottom: 40pt;">📚 目录</h1>
        """

        item_counter = 0
        for section_info in filtered_structure:
            section_name = section_info['name']
            items = section_info['items']

            toc_html += f"""
            <div class="toc-section" style="margin-bottom: 25pt;">
                <h2 style="font-size: 18pt; margin-bottom: 15pt;">{section_name}</h2>
            """

            # 递归处理目录项
            def process_toc_items(items, level=0):
                nonlocal item_counter, toc_html
                if isinstance(items, list):
                    for item in items:
                        if isinstance(item, dict):
                            for title, path_or_subitems in item.items():
                                if isinstance(path_or_subitems, str):
                                    item_counter += 1
                                    indent = "  " * level
                                    toc_html += f"""
                                    <div style="margin-bottom: 8pt; padding: 8pt;">{indent}{item_counter}. {title}</div>
                                    """
                                elif isinstance(path_or_subitems, list):
                                    indent = "  " * level
                                    toc_html += f"""
                                    <div style="margin-bottom: 8pt;">{indent}📂 {title}</div>
                                    """
                                    process_toc_items(path_or_subitems, level + 1)

            if isinstance(items, list):
                process_toc_items(items)

            toc_html += "</div>"

        toc_html += "</div>"
        return toc_html

    def process_markdown_content(self, content, file_path=None):
        """处理markdown内容"""
        # 修复内部链接
        if file_path:
            content = self.link_fixer.fix_markdown_links(content, file_path)

        # 翻译代码注释（如果启用）
        if self.translate_comments:
            def translate_code_block(match):
                language = match.group(1) if match.group(1) else ''
                code = match.group(2)
                translated_code = self.translator.translate_code_block(code, language)
                return f'```{language}\n{translated_code}\n```'

            content = re.sub(r'```(\w*)\n(.*?)```', translate_code_block, content, flags=re.DOTALL)

        return content

    def merge_docs_files(self):
        """合并文档文件（应用过滤器）"""
        if not self.nav_structure:
            self.load_navigation_structure()

        # 过滤导航结构
        filtered_structure = []
        part_index = 0

        for section in self.nav_structure:
            if isinstance(section, dict):
                for section_name, items in section.items():
                    # 如果是 Part，增加索引
                    if section_name.startswith('Part '):
                        part_index += 1

                    # 判断是否应该包含该章节
                    if self.should_include_section(section_name, part_index):
                        filtered_structure.append({
                            'name': section_name,
                            'items': items
                        })
                        print(f"✅ 包含章节: {section_name}")
                    else:
                        print(f"⏭️  跳过章节: {section_name}")

        if not filtered_structure:
            print("❌ 没有找到匹配的章节！")
            return None

        # 创建HTML内容
        full_html = """
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <title>Web Reverse Engineering Cookbook</title>
        </head>
        <body>
        """

        # 添加封面
        full_html += self.create_cover_page()

        # 添加目录
        full_html += self.create_table_of_contents(filtered_structure)

        # 添加章节内容
        article_counter = 0
        for section_info in filtered_structure:
            section_name = section_info['name']
            items = section_info['items']

            # 跳过 Home
            if section_name == "Home":
                continue

            full_html += f"""
            <div class="chapter">
                <h1 class="no-page-break">{section_name}</h1>
            """

            # 递归处理导航项
            def process_nav_items(items, level=0):
                nonlocal article_counter, full_html
                if isinstance(items, list):
                    for item in items:
                        if isinstance(item, dict):
                            for title, path_or_subitems in item.items():
                                if isinstance(path_or_subitems, str):
                                    article_counter += 1
                                    file_path = os.path.join(self.docs_dir, path_or_subitems)

                                    if os.path.exists(file_path):
                                        try:
                                            with open(file_path, 'r', encoding='utf-8') as f:
                                                content = f.read()

                                            content = self.process_markdown_content(content, path_or_subitems)
                                            html_content = markdown2.markdown(
                                                content,
                                                extras=[
                                                    'fenced-code-blocks',
                                                    'tables',
                                                    'header-ids',
                                                    'code-friendly',
                                                ]
                                            )

                                            anchor_id = self.link_fixer.get_anchor_id_for_file(path_or_subitems)

                                            full_html += f"""
                                            <div class="section" id="{anchor_id}">
                                                <h2>{article_counter}. {title}</h2>
                                                {html_content}
                                            </div>
                                            """

                                            print(f"✅ [{article_counter}] 已处理: {path_or_subitems}")

                                        except Exception as e:
                                            print(f"❌ 处理文件失败 {file_path}: {e}")
                                    else:
                                        print(f"⚠️  文件不存在: {file_path}")

                                elif isinstance(path_or_subitems, list):
                                    process_nav_items(path_or_subitems, level + 1)

            if isinstance(items, list):
                process_nav_items(items)

            full_html += "</div>"

        full_html += """
        </body>
        </html>
        """

        return full_html

    def generate_pdf(self, output_filename=None):
        """生成PDF文件"""
        if output_filename is None:
            # 根据过滤器生成文件名
            if self.parts_filter:
                parts_str = '_'.join(map(str, sorted(self.parts_filter)))
                output_filename = f"web_cookbook_parts_{parts_str}.pdf"
            elif self.sections_filter:
                sections_str = '_'.join(self.sections_filter)
                output_filename = f"web_cookbook_{sections_str}.pdf"
            else:
                output_filename = "web_cookbook_full.pdf"

        print("\n🚀 开始生成PDF...")
        print("=" * 60)

        # 合并文档
        html_content = self.merge_docs_files()

        if not html_content:
            print("❌ 没有内容可生成")
            return None

        # 创建CSS样式
        css_styles = self.create_css_styles()

        # 生成PDF
        output_path = os.path.join(self.output_dir, output_filename)

        try:
            print("\n📄 正在渲染PDF...")
            html_doc = HTML(string=html_content)
            html_doc.write_pdf(
                output_path,
                stylesheets=[css_styles],
                font_config=self.font_config
            )

            file_size_mb = os.path.getsize(output_path) / 1024 / 1024

            print(f"\n✅ PDF生成成功!")
            print(f"📁 文件路径: {output_path}")
            print(f"📊 文件大小: {file_size_mb:.2f} MB")

            print("\n" + "=" * 60)
            print("🎉 PDF生成完成!")

            return output_path

        except Exception as e:
            print(f"\n❌ PDF生成失败: {e}")
            import traceback
            traceback.print_exc()
            return None


def parse_parts_filter(parts_str):
    """解析 parts 过滤器
    支持格式:
    - "1-3" -> [1, 2, 3]
    - "1,3,5" -> [1, 3, 5]
    - "1-3,5" -> [1, 2, 3, 5]
    """
    parts = set()
    for part in parts_str.split(','):
        part = part.strip()
        if '-' in part:
            start, end = part.split('-')
            parts.update(range(int(start), int(end) + 1))
        else:
            parts.add(int(part))
    return sorted(list(parts))


def parse_sections_filter(sections_str):
    """解析 sections 过滤器
    支持格式: "Foundations,Tooling,Techniques"
    """
    return [s.strip() for s in sections_str.split(',')]


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Web RE Cookbook PDF Generator - 支持章节范围选择',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 生成全部章节
  python docs_to_pdf_improved.py

  # 生成 Part 1 到 Part 2
  python docs_to_pdf_improved.py --parts 1-2

  # 生成 Part 1 和 Part 3
  python docs_to_pdf_improved.py --parts 1,3

  # 生成特定章节
  python docs_to_pdf_improved.py --sections "Foundations,Tooling"

  # 列出所有可用章节
  python docs_to_pdf_improved.py --list

  # 指定输出文件名
  python docs_to_pdf_improved.py --output my_book.pdf --parts 1-2
        """
    )

    parser.add_argument('--list', action='store_true',
                        help='列出所有可用的章节')
    parser.add_argument('--parts', type=str,
                        help='指定要生成的 Part 范围，例如: "1-2" 或 "1,3,5"')
    parser.add_argument('--sections', type=str,
                        help='指定要生成的章节名称，例如: "Foundations,Tooling"')
    parser.add_argument('--output', '-o', type=str,
                        help='输出文件名')
    parser.add_argument('--translate', action='store_true',
                        help='翻译代码中的中文注释为英文')

    args = parser.parse_args()

    print("🚀 Web Reverse Engineering Cookbook - PDF Generator")
    print("=" * 60)
    print(f"📧 Author: overkazaf@gmail.com")
    print(f"💬 vx: _0xAF_")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}")
    print("=" * 60)

    # 检查依赖
    try:
        import markdown2
        import weasyprint
        import yaml
        print("✅ 依赖检查通过")
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install markdown2 weasyprint pillow pyyaml")
        return

    # 解析过滤器
    parts_filter = None
    sections_filter = None

    if args.parts:
        parts_filter = parse_parts_filter(args.parts)
        print(f"🔹 Part 过滤器: {parts_filter}")

    if args.sections:
        sections_filter = parse_sections_filter(args.sections)
        print(f"🔹 章节过滤器: {sections_filter}")

    # 创建转换器
    converter = DocsToPDFConverter(
        translate_comments=args.translate,
        parts_filter=parts_filter,
        sections_filter=sections_filter
    )

    # 加载导航结构
    nav = converter.load_navigation_structure()
    if not nav:
        print("❌ 未找到导航结构")
        return

    # 如果是列出章节，则只列出不生成
    if args.list:
        converter.list_available_sections()
        return

    # 生成PDF
    converter.generate_pdf(output_filename=args.output)


if __name__ == "__main__":
    main()
