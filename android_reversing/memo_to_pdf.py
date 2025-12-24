#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memo to PDF Converter
将所有memo markdown文件合并成一个结构良好的PDF文件

依赖安装:
pip install markdown2 weasyprint pillow

使用方法:
python memo_to_pdf.py
"""

import os
import re
import glob
from datetime import datetime
import markdown2
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

class MemoToPDFConverter:
    def __init__(self, memo_dir="."):
        self.memo_dir = memo_dir
        self.output_dir = "output"
        self.memo_files = []
        self.font_config = FontConfiguration()
        
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
        
    def find_memo_files(self):
        """查找所有memo文件并按序号排序"""
        pattern = os.path.join(self.memo_dir, "memo_*.md")
        files = glob.glob(pattern)
        
        # 按文件名中的数字排序
        def extract_number(filename):
            match = re.search(r'memo_(\d+)', filename)
            return int(match.group(1)) if match else 0
            
        self.memo_files = sorted(files, key=extract_number)
        print(f"Found {len(self.memo_files)} memo files:")
        for file in self.memo_files:
            print(f"  - {os.path.basename(file)}")
        
        return self.memo_files
    
    def get_memo_info(self):
        """获取memo文件信息映射"""
        memo_info = {
            "memo_1_foundations.md": {"title": "Android 逆向基础知识", "icon": "📱"},
            "memo_2_tooling.md": {"title": "动态分析工具与技术", "icon": "🛠️"},
            "memo_3_unidbg.md": {"title": "Unidbg 模拟执行框架", "icon": "🖥️"},
            "memo_4_redis.md": {"title": "Redis 内存数据库", "icon": "🚀"},
            "memo_5_scrapy.md": {"title": "Scrapy 爬虫框架", "icon": "🕷️"},
            "memo_6_mq.md": {"title": "消息队列技术", "icon": "📬"},
            "memo_7_db.md": {"title": "数据库技术", "icon": "🗄️"},
            "memo_8_springboot.md": {"title": "Spring Boot 技术", "icon": "🍃"},
            "memo_9_bigdata.md": {"title": "大数据技术栈", "icon": "🏗️"},
        }
        return memo_info
    
    def create_css_styles(self):
        """创建PDF样式"""
        css_content = """
        /* 使用系统字体确保中文正确显示 - 使用明确的字体路径 */
        @font-face {
            font-family: 'Noto Sans SC';
            src: url('file:///System/Library/Fonts/Hiragino Sans GB.ttc') format('truetype'),
                 url('file:///System/Library/Fonts/STHeiti Light.ttc') format('truetype'),
                 url('file:///System/Library/Fonts/Supplemental/Songti.ttc') format('truetype'),
                 url('file:///Library/Fonts/Arial Unicode.ttf') format('truetype');
            font-weight: normal;
        }

        @font-face {
            font-family: 'Noto Sans SC';
            src: url('file:///System/Library/Fonts/Hiragino Sans GB.ttc') format('truetype'),
                 url('file:///System/Library/Fonts/STHeiti Medium.ttc') format('truetype'),
                 url('file:///System/Library/Fonts/Supplemental/Songti.ttc') format('truetype');
            font-weight: bold;
        }

        @font-face {
            font-family: 'Fira Code';
            src: url('file:///System/Library/Fonts/Menlo.ttc') format('truetype'),
                 url('file:///System/Library/Fonts/Monaco.dfont') format('truetype'),
                 url('file:///Library/Fonts/Arial Unicode.ttf') format('truetype');
        }

        /* 页面设置 */
        @page {
            size: A4;
            margin: 2.5cm 2cm 3cm 2cm;
            
            @top-left {
                content: "Android 逆向工程速记手册";
                font-family: 'Noto Sans SC', sans-serif;
                font-size: 10pt;
                color: #666;
                border-bottom: 1px solid #e0e0e0;
                padding-bottom: 5pt;
            }
            
            @top-right {
                content: "Page " counter(page);
                font-family: 'Noto Sans SC', sans-serif;
                font-size: 10pt;
                color: #666;
                border-bottom: 1px solid #e0e0e0;
                padding-bottom: 5pt;
            }
            
            @bottom-center {
                content: "© 2024 Android 逆向工程速记手册";
                font-family: 'Noto Sans SC', sans-serif;
                font-size: 9pt;
                color: #999;
                border-top: 1px solid #e0e0e0;
                padding-top: 5pt;
            }
        }
        
        /* 基础样式 */
        body {
            font-family: 'Noto Sans SC', sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #333;
            background: white;
        }
        
        /* 标题样式 */
        h1 {
            font-size: 24pt;
            font-weight: 700;
            color: #1a1a1a;
            margin-top: 30pt;
            margin-bottom: 20pt;
            page-break-before: always;
            border-bottom: 3px solid #4a90e2;
            padding-bottom: 10pt;
        }
        
        h2 {
            font-size: 18pt;
            font-weight: 600;
            color: #2c3e50;
            margin-top: 25pt;
            margin-bottom: 15pt;
            border-left: 4px solid #4a90e2;
            padding-left: 15pt;
        }
        
        h3 {
            font-size: 14pt;
            font-weight: 500;
            color: #34495e;
            margin-top: 20pt;
            margin-bottom: 12pt;
        }
        
        h4 {
            font-size: 12pt;
            font-weight: 500;
            color: #555;
            margin-top: 15pt;
            margin-bottom: 10pt;
        }
        
        /* 段落样式 */
        p {
            margin-bottom: 12pt;
            text-align: justify;
        }
        
        /* 列表样式 */
        ul, ol {
            margin-bottom: 12pt;
            padding-left: 20pt;
        }
        
        li {
            margin-bottom: 6pt;
        }
        
        /* 代码样式 */
        code {
            font-family: 'Fira Code', monospace;
            font-size: 9.5pt;
            background-color: #f8f9fa;
            padding: 2pt 4pt;
            border-radius: 3pt;
            border: 1px solid #e9ecef;
        }
        
        pre {
            font-family: 'Fira Code', monospace;
            font-size: 9pt;
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 6pt;
            padding: 15pt;
            margin: 15pt 0;
            overflow-x: auto;
            line-height: 1.4;
        }
        
        pre code {
            background: none;
            border: none;
            padding: 0;
        }
        
        /* 表格样式 */
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 15pt 0;
            font-size: 10pt;
        }
        
        th, td {
            border: 1px solid #ddd;
            padding: 8pt 12pt;
            text-align: left;
        }
        
        th {
            background-color: #f8f9fa;
            font-weight: 600;
            color: #495057;
        }
        
        tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        
        /* 引用样式 */
        blockquote {
            border-left: 4px solid #6c757d;
            padding-left: 15pt;
            margin: 15pt 0;
            color: #6c757d;
            font-style: italic;
        }
        
        /* 链接样式 */
        a {
            color: #4a90e2;
            text-decoration: none;
        }
        
        a:hover {
            text-decoration: underline;
        }
        
        /* 强调样式 */
        strong, b {
            font-weight: 600;
            color: #2c3e50;
        }
        
        em, i {
            font-style: italic;
            color: #555;
        }
        
        /* 分隔线 */
        hr {
            border: none;
            border-top: 2px solid #e9ecef;
            margin: 25pt 0;
        }
        
        /* 目录页面特殊样式 */
        .toc-page {
            page-break-before: always;
        }
        
        .toc-title {
            font-size: 28pt;
            font-weight: 700;
            text-align: center;
            color: #1a1a1a;
            margin-bottom: 40pt;
            border-bottom: 3px solid #4a90e2;
            padding-bottom: 15pt;
        }
        
        .toc-item {
            margin-bottom: 15pt;
            padding: 10pt;
            border-radius: 6pt;
            background-color: #f8f9fa;
            border-left: 4px solid #4a90e2;
        }
        
        .toc-item h2 {
            margin: 0;
            font-size: 16pt;
            color: #2c3e50;
            border: none;
            padding: 0;
        }
        
        .toc-item p {
            margin: 5pt 0 0 0;
            color: #666;
            font-size: 10pt;
        }
        
        /* 章节分页 */
        .chapter {
            page-break-before: always;
        }
        
        /* 打印优化 */
        @media print {
            body {
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
            }
        }
        """
        
        return CSS(string=css_content, font_config=self.font_config)
    
    def process_markdown_content(self, content):
        """处理markdown内容，优化PDF显示效果"""
        # 替换emoji为文字描述（可选，因为PDF可能不支持某些emoji）
        emoji_replacements = {
            "📱": "[手机]",
            "🛠️": "[工具]", 
            "🖥️": "[电脑]",
            "🚀": "[火箭]",
            "🕷️": "[蜘蛛]",
            "📬": "[邮箱]",
            "🗄️": "[文件柜]",
            "🍃": "[叶子]",
            # 可以根据需要添加更多emoji替换
        }
        
        # 为了保持美观，暂时保留emoji
        # for emoji, replacement in emoji_replacements.items():
        #     content = content.replace(emoji, replacement)
        
        # 处理代码块语言标识
        content = re.sub(r'```(\w+)\n', r'```\n', content)
        
        # 优化表格显示
        content = re.sub(r'\|:---\|', '|---|', content)
        content = re.sub(r'\|:---:\|', '|---|', content)
        
        return content
    
    def create_table_of_contents(self):
        """创建目录页面"""
        memo_info = self.get_memo_info()
        
        toc_html = """
        <div class="toc-page">
            <h1 class="toc-title">📚 目录</h1>
        """
        
        for i, memo_file in enumerate(self.memo_files, 1):
            filename = os.path.basename(memo_file)
            info = memo_info.get(filename, {"title": "未知章节", "icon": "📄"})
            
            toc_html += f"""
            <div class="toc-item">
                <h2>{info['icon']} 第{i}章 {info['title']}</h2>
                <p>文件: {filename}</p>
            </div>
            """
        
        toc_html += "</div>"
        return toc_html
    
    def create_cover_page(self):
        """创建封面页面"""
        cover_html = f"""
        <div style="text-align: center; margin-top: 150pt;">
            <h1 style="font-size: 36pt; color: #1a1a1a; margin-bottom: 30pt; border: none;">
                📱 Android 逆向工程速记手册
            </h1>
            <h2 style="font-size: 20pt; color: #666; font-weight: 400; border: none; padding: 0;">
                Android Reverse Engineering Quick Reference
            </h2>
            <div style="margin-top: 80pt; font-size: 14pt; color: #888;">
                <p>涵盖基础知识、工具使用、实战技巧、知识要点</p>
                <p>支持 Frida、Unidbg、Scrapy、Redis、数据库、Spring Boot 等技术栈</p>
            </div>
            <div style="margin-top: 100pt; font-size: 12pt; color: #aaa;">
                <p style="font-size: 48pt; margin-bottom: 15pt;">🧑‍💻</p>
                <p style="font-size: 16pt; color: #666; margin-bottom: 20pt;"><strong>作者 Authors: +5, Gemini Pro 3.0, Claude Code Opus 4.5</strong></p>
                <p>📧 Email: overkazaf@gmail.com</p>
                <p>💬 WeChat: _0xAF_</p>
                <p>🐙 GitHub: github.com/your-username</p>
                <p style="margin-top: 30pt;">📅 生成时间: {datetime.now().strftime('%Y年%m月%d日')}</p>
                <p>📌 版本: v1.0</p>
            </div>
            <div style="margin-top: 40pt; padding: 25pt 40pt; background-color: #fff8e1; border-radius: 8pt; border-left: 4px solid #ffa726;">
                <p style="font-size: 13pt; color: #e65100; font-weight: 600; margin-bottom: 15pt; text-align: center;">
                    📖 关于这本速记手册的诞生 | About This Quick Reference
                </p>
                <p style="font-size: 10.5pt; color: #444; line-height: 1.9; text-align: justify; margin-bottom: 12pt;">
                    这本速记手册的诞生，是一次有趣的<strong>人机协作</strong>实验。除了笔者（<strong>+5</strong>）在Android逆向工程领域的日常记录和实战经验积累，
                    本书还得到了两位AI助手的鼎力支持——<strong>Gemini Pro 3.0</strong>和<strong>Claude Code Opus 4.5</strong>。
                    这个协作过程就像一个真实的技术团队：
                </p>
                <div style="margin-left: 20pt; margin-bottom: 12pt;">
                    <p style="font-size: 10pt; color: #444; line-height: 1.7; margin-bottom: 8pt;">
                        📚 <strong>Gemini Pro 3.0</strong>（研究员 & 知识架构师）：负责技术调研、资料搜集、知识体系整理，
                        以及提供技术思路和解决方案建议，就像团队中的技术顾问和知识管家。
                    </p>
                    <p style="font-size: 10pt; color: #444; line-height: 1.7; margin-bottom: 8pt;">
                        💻 <strong>Claude Code Opus 4.5</strong>（软件工程师 & 自动化专家）：负责编写和优化代码示例、
                        批量处理Markdown格式问题、自动化文档生成流程，以及代码质量把关，就像团队中的全栈开发和DevOps工程师。
                    </p>
                    <p style="font-size: 10pt; color: #444; line-height: 1.7; margin-bottom: 8pt;">
                        🎯 <strong>+5</strong>（技术负责人 & 总编辑）：负责整体架构设计、技术方向把控、内容审核修订、
                        以及最终质量保障，就像团队中的Tech Lead和Editor-in-Chief。
                    </p>
                </div>
                <p style="font-size: 10pt; color: #666; line-height: 1.8; text-align: justify; font-style: italic; margin-bottom: 12pt;">
                    This quick reference is born from an intriguing <strong>human-AI collaboration</strong>, like a real tech team:
                    <strong>Gemini Pro 3.0</strong> (Research Engineer & Knowledge Architect) handles technical research,
                    resource gathering, knowledge organization, and solution consulting;
                    <strong>Claude Code Opus 4.5</strong> (Software Engineer & Automation Expert) crafts code examples,
                    batch-processes Markdown formatting, automates documentation workflows, and ensures code quality;
                    <strong>+5</strong> (Tech Lead & Editor-in-Chief) steers the architecture, technical direction,
                    content revision, and final quality assurance.
                </p>
                <p style="font-size: 10pt; color: #555; line-height: 1.8; text-align: justify; margin-bottom: 12pt;">
                    🤝 我相信，人类的实践智慧与AI的知识整合能力相结合，能够创造出更优质的学习资源。
                    希望这种跨越人机边界的协作方式，能为大家带来<strong>不一样的阅读体验</strong>，
                    也为技术文档的创作开辟新的可能性。
                </p>
                <p style="font-size: 10pt; color: #444; line-height: 1.8; text-align: justify; border-top: 1px dashed #ffa726; padding-top: 12pt;">
                    ✈️ <strong>创作初衷</strong>：这本速记手册最初是为了记录笔者日常的逆向工作和技术积累。
                    在漫长的飞机旅途中，或是在咖啡馆小憩时，翻阅这些精心整理的技术笔记，
                    回顾那些有意思的逆向知识点和解题思路，既是一种放松，也是一种学习。
                    希望这本手册也能成为你旅途中的良伴，让技术学习变得更加轻松愉快。
                </p>
            </div>
            <div style="margin-top: 30pt; padding: 25pt 40pt; border-top: 1px solid #ddd; border-bottom: 1px solid #ddd;">
                <p style="font-size: 11pt; color: #555; font-style: italic; line-height: 1.8; text-align: center;">
                    "If the highest aim of a captain were to preserve his ship,<br/>
                    he would keep it in port forever."
                </p>
                <p style="font-size: 9pt; color: #888; text-align: right; margin-top: 10pt;">
                    — St. Thomas Aquinas, <em>Summa Theologica</em> (1265-1274)
                </p>
            </div>
            <div style="margin-top: 30pt; padding: 25pt 40pt; background-color: #f9f9f9; border-radius: 8pt;">
                <p style="font-size: 10.5pt; color: #444; line-height: 1.9; text-align: justify; margin-bottom: 15pt;">
                    The journey begins with the thrill of solving puzzles—that exhilarating rush when code
                    finally yields its secrets. Yet seasoned reverse engineers walk a different path. They
                    remain humble, ever-curious, and deeply reflective. In time, they all return to first
                    principles: understanding how systems are <em>built</em> is the only true way to understand
                    how they can be <em>unraveled</em>.
                </p>
                <p style="font-size: 10pt; color: #666; line-height: 1.8; text-align: justify; font-style: italic;">
                    初涉此道，多为破解之时的快意。而行至深处者，早已超越这份欣喜。他们怀谦卑之心，
                    持求知之念，善于思考，最终都会回归技术的本质——唯有洞悉系统<strong>构建</strong>之道，
                    方能参透其<strong>拆解</strong>之法。知己知彼，百战不殆。
                </p>
            </div>
        </div>
        """
        return cover_html
    
    def merge_memo_files(self):
        """合并所有memo文件"""
        if not self.memo_files:
            self.find_memo_files()
        
        memo_info = self.get_memo_info()
        
        # 创建完整的HTML内容
        full_html = """
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Android 逆向工程速记手册</title>
        </head>
        <body>
        """
        
        # 添加封面
        full_html += self.create_cover_page()
        
        # 添加目录
        full_html += self.create_table_of_contents()
        
        # 添加各章节内容
        for i, memo_file in enumerate(self.memo_files, 1):
            try:
                with open(memo_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 处理内容
                content = self.process_markdown_content(content)
                
                # 转换为HTML
                html_content = markdown2.markdown(
                    content, 
                    extras=['fenced-code-blocks', 'tables', 'strike', 'task_list']
                )
                
                # 添加章节标识
                filename = os.path.basename(memo_file)
                info = memo_info.get(filename, {"title": "未知章节", "icon": "📄"})
                
                chapter_html = f"""
                <div class="chapter">
                    <h1>{info['icon']} 第{i}章 {info['title']}</h1>
                    {html_content}
                </div>
                """
                
                full_html += chapter_html
                print(f"Processed: {filename}")
                
            except Exception as e:
                print(f"Error processing {memo_file}: {e}")
                continue
        
        full_html += """
        </body>
        </html>
        """
        
        return full_html
    
    def generate_pdf(self, output_filename="android_reverse_engineering_memo.pdf"):
        """生成PDF文件"""
        print("开始生成PDF...")
        
        # 合并所有memo文件
        html_content = self.merge_memo_files()
        
        # 创建CSS样式
        css_styles = self.create_css_styles()
        
        # 生成PDF
        output_path = os.path.join(self.output_dir, output_filename)
        
        try:
            html_doc = HTML(string=html_content)
            html_doc.write_pdf(
                output_path,
                stylesheets=[css_styles],
                font_config=self.font_config
            )
            
            print(f"✅ PDF生成成功: {output_path}")
            print(f"📄 文件大小: {os.path.getsize(output_path) / 1024 / 1024:.2f} MB")
            
            # 同时保存HTML版本用于调试
            html_path = os.path.join(self.output_dir, "memo_debug.html")
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"🔍 调试HTML已保存: {html_path}")
            
            return output_path
            
        except Exception as e:
            print(f"❌ PDF生成失败: {e}")
            return None
    
    def generate_individual_pdfs(self):
        """生成单个memo文件的PDF"""
        print("开始生成单独的PDF文件...")
        
        if not self.memo_files:
            self.find_memo_files()
        
        memo_info = self.get_memo_info()
        css_styles = self.create_css_styles()
        
        for memo_file in self.memo_files:
            try:
                filename = os.path.basename(memo_file)
                base_name = os.path.splitext(filename)[0]
                
                with open(memo_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 处理内容
                content = self.process_markdown_content(content)
                
                # 转换为HTML
                html_content = markdown2.markdown(
                    content, 
                    extras=['fenced-code-blocks', 'tables', 'strike', 'task_list']
                )
                
                # 创建完整HTML
                info = memo_info.get(filename, {"title": "未知章节", "icon": "📄"})
                
                full_html = f"""
                <!DOCTYPE html>
                <html lang="zh-CN">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>{info['title']}</title>
                </head>
                <body>
                    <h1>{info['icon']} {info['title']}</h1>
                    {html_content}
                </body>
                </html>
                """
                
                # 生成PDF
                output_path = os.path.join(self.output_dir, f"{base_name}.pdf")
                html_doc = HTML(string=full_html)
                html_doc.write_pdf(
                    output_path,
                    stylesheets=[css_styles],
                    font_config=self.font_config
                )
                
                print(f"✅ 已生成: {output_path}")
                
            except Exception as e:
                print(f"❌ 生成 {memo_file} 失败: {e}")
                continue


def main():
    """主函数"""
    print("🚀 Android 逆向工程速记手册 PDF 生成器")
    print("=" * 50)
    
    # 检查依赖
    try:
        import markdown2
        import weasyprint
        print("✅ 依赖检查通过")
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install markdown2 weasyprint pillow")
        return
    
    # 创建转换器
    converter = MemoToPDFConverter()
    
    # 查找memo文件
    memo_files = converter.find_memo_files()
    if not memo_files:
        print("❌ 未找到memo文件")
        return
    
    print("\n选择生成模式:")
    print("1. 生成合并PDF (推荐)")
    print("2. 生成单独PDF")
    print("3. 生成全部")
    
    choice = input("请选择 (1-3): ").strip()
    
    if choice == "1":
        converter.generate_pdf()
    elif choice == "2":
        converter.generate_individual_pdfs()
    elif choice == "3":
        converter.generate_pdf()
        converter.generate_individual_pdfs()
    else:
        print("❌ 无效选择")
        return
    
    print("\n🎉 PDF生成完成!")
    print("📁 输出目录:", os.path.abspath(converter.output_dir))


if __name__ == "__main__":
    main()