#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web RE Cookbook - PDF Generator (Final Edition)
将docs目录下的所有markdown文件合并成一个结构良好的PDF文件

特性：
1. Recipe 编号 - 每个食谱有唯一编号 (R01, R02, ...)
2. 完整目录 - 带 Recipe 编号的详细目录
3. 作者信息 - 包含人机协作说明
4. 并行处理 - 快速生成
5. 中文字体支持
6. PDF内链接跳转
7. 智能缓存

使用方法:
python docs_to_pdf.py                          # 完整流程（推荐）
python docs_to_pdf.py --sections 0,1 -w 8      # 指定章节和进程数
python docs_to_pdf.py --no-cache               # 禁用缓存
python docs_to_pdf.py --skip-validation        # 跳过格式验证
python docs_to_pdf.py --fix-files              # 修复文件格式问题
"""

import os
import re
import yaml
import hashlib
import pickle
import argparse
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from concurrent.futures import ProcessPoolExecutor, as_completed

import mistune
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration


# ============================================================================
# Recipe 编号映射
# ============================================================================

RECIPE_NUMBERS = {
    # Quick Start
    "00-Quick-Start/index.md": "R00",
    "00-Quick-Start/your_first_hook.md": "R01",
    "00-Quick-Start/decrypt_api_params.md": "R02",
    "00-Quick-Start/bypass_simple_captcha.md": "R03",

    # Foundations
    "01-Foundations/http_https_protocol.md": "R04",
    "01-Foundations/browser_architecture.md": "R05",
    "01-Foundations/javascript_basics.md": "R06",
    "01-Foundations/javascript_execution_mechanism.md": "R07",
    "01-Foundations/dom_and_bom.md": "R08",
    "01-Foundations/webassembly_basics.md": "R09",
    "01-Foundations/cookie_and_storage.md": "R10",
    "01-Foundations/cors_and_same_origin_policy.md": "R11",
    "01-Foundations/tls_ssl_handshake.md": "R12",
    "01-Foundations/web_api_and_ajax.md": "R13",

    # Tooling
    "02-Tooling/browser_devtools.md": "R14",
    "02-Tooling/burp_suite_guide.md": "R15",
    "02-Tooling/fiddler_guide.md": "R16",
    "02-Tooling/charles_guide.md": "R17",
    "02-Tooling/wireshark_guide.md": "R18",
    "02-Tooling/puppeteer_playwright.md": "R19",
    "02-Tooling/selenium_guide.md": "R20",
    "02-Tooling/ast_tools.md": "R21",
    "02-Tooling/nodejs_debugging.md": "R22",
    "02-Tooling/v8_tools.md": "R23",

    # Basic Recipes
    "03-Basic-Recipes/re_workflow.md": "R24",
    "03-Basic-Recipes/debugging_techniques.md": "R25",
    "03-Basic-Recipes/hooking_techniques.md": "R26",
    "03-Basic-Recipes/api_reverse_engineering.md": "R27",
    "03-Basic-Recipes/crypto_identification.md": "R28",
    "03-Basic-Recipes/dynamic_parameter_analysis.md": "R29",
    "03-Basic-Recipes/websocket_reversing.md": "R30",

    # Advanced Recipes
    "04-Advanced-Recipes/javascript_deobfuscation.md": "R31",
    "04-Advanced-Recipes/captcha_bypass.md": "R32",
    "04-Advanced-Recipes/browser_fingerprinting.md": "R33",
    "04-Advanced-Recipes/javascript_vm_protection.md": "R34",
    "04-Advanced-Recipes/webassembly_reversing.md": "R35",
    "04-Advanced-Recipes/anti_scraping_deep_dive.md": "R36",
    "04-Advanced-Recipes/frontend_hardening.md": "R37",
    "04-Advanced-Recipes/csp_bypass.md": "R38",
    "04-Advanced-Recipes/webrtc_fingerprinting.md": "R39",
    "04-Advanced-Recipes/canvas_fingerprinting.md": "R40",
    "04-Advanced-Recipes/tls_fingerprinting.md": "R41",
    "04-Advanced-Recipes/http2_http3.md": "R42",
    "04-Advanced-Recipes/pwa_service_worker.md": "R43",

    # Case Studies
    "05-Case-Studies/case_ecommerce.md": "R44",
    "05-Case-Studies/case_social_media.md": "R45",
    "05-Case-Studies/case_financial.md": "R46",
    "05-Case-Studies/case_video_streaming.md": "R47",
    "05-Case-Studies/case_news_aggregator.md": "R48",
    "05-Case-Studies/case_search_engine.md": "R49",

    # Engineering
    "06-Engineering/distributed_scraping.md": "R50",
    "06-Engineering/proxy_pool_management.md": "R51",
    "06-Engineering/data_storage_solutions.md": "R52",
    "06-Engineering/message_queue_application.md": "R53",
    "06-Engineering/docker_deployment.md": "R54",
    "06-Engineering/monitoring_and_alerting.md": "R55",
    "06-Engineering/anti_anti_scraping_framework.md": "R56",

    # Scripts
    "07-Scripts/javascript_hook_scripts.md": "R57",
    "07-Scripts/deobfuscation_scripts.md": "R58",
    "07-Scripts/automation_scripts.md": "R59",
    "07-Scripts/crypto_detection_scripts.md": "R60",

    # Cheat Sheets
    "08-Cheat-Sheets/index.md": "R61",
    "08-Cheat-Sheets/common_commands.md": "R62",
    "08-Cheat-Sheets/crypto_signatures.md": "R63",
    "08-Cheat-Sheets/tool_shortcuts.md": "R64",
    "08-Cheat-Sheets/regex_patterns.md": "R65",
    "08-Cheat-Sheets/http_headers.md": "R66",

    # Templates
    "09-Templates/index.md": "R67",
    "09-Templates/basic_scraper.md": "R68",
    "09-Templates/reverse_project.md": "R69",
    "09-Templates/docker_setup.md": "R70",
    "09-Templates/cicd_pipeline.md": "R71",
    "09-Templates/distributed_crawler.md": "R72",

    # Troubleshooting
    "10-Troubleshooting/index.md": "R73",
    "10-Troubleshooting/network_issues.md": "R74",
    "10-Troubleshooting/anti_scraping_issues.md": "R75",
    "10-Troubleshooting/javascript_debugging.md": "R76",
    "10-Troubleshooting/tool_issues.md": "R77",
    "10-Troubleshooting/data_issues.md": "R78",
    "10-Troubleshooting/docker_issues.md": "R79",

    # Resources
    "11-Resources/github_projects.md": "R80",
    "11-Resources/learning_resources.md": "R81",
    "11-Resources/faq.md": "R82",
}


def add_recipe_number_to_content(content: str, path: str) -> str:
    """给 Recipe 内容的标题添加编号前缀"""
    if path in RECIPE_NUMBERS:
        recipe_num = RECIPE_NUMBERS[path]
        # 匹配第一个一级标题 (# xxx)
        pattern = r'^(#\s+)(.+)$'
        def replace_title(match):
            return f"{match.group(1)}{recipe_num}: {match.group(2)}"
        # 只替换第一个匹配
        content = re.sub(pattern, replace_title, content, count=1, flags=re.MULTILINE)
    return content


# ============================================================================
# 格式验证和修复模块
# ============================================================================

class QuickFormatFixer:
    """快速格式修复器"""

    @staticmethod
    def fix_file_issues(file_path: str) -> int:
        """修复文件中的常见格式问题"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except:
            return 0

        original_lines = lines[:]
        fixes = 0

        # 1. 修复未闭合的代码块
        in_code_block = False
        for line in lines:
            if re.match(r'^```', line):
                in_code_block = not in_code_block

        if in_code_block:
            if lines and not lines[-1].endswith('\n'):
                lines[-1] += '\n'
            lines.append('```\n')
            fixes += 1

        # 2. 修复列表标记后缺少空格
        for i, line in enumerate(lines):
            match = re.match(r'^(\s*)([-*+]|\d+\.)([^\s])', line)
            if match:
                indent = match.group(1)
                marker = match.group(2)
                rest = line[len(indent) + len(marker):]
                lines[i] = f"{indent}{marker} {rest}"
                fixes += 1

        # 3. 修复标题后缺少空格
        for i, line in enumerate(lines):
            match = re.match(r'^(#{1,6})([^\s])', line)
            if match:
                hashes = match.group(1)
                rest = line[len(hashes):]
                lines[i] = f"{hashes} {rest}"
                fixes += 1

        # 如果有修复，写回文件
        if fixes > 0 and lines != original_lines:
            try:
                # 备份原文件
                backup_path = f"{file_path}.backup"
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.writelines(original_lines)

                # 写入修复后的内容
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
            except:
                return 0

        return fixes


# ============================================================================
# 并行处理模块
# ============================================================================

def process_single_markdown_file(args):
    """处理单个markdown文件（用于并行执行）"""
    file_path, path, counter, use_cache, cache_dir, path_to_anchor = args

    try:
        # 检查缓存
        cache_key = f"{path}_{counter}"
        cache_file = os.path.join(cache_dir,
                                  f"{hashlib.md5(cache_key.encode()).hexdigest()}.pkl")

        file_hash = hashlib.md5(open(file_path, 'rb').read()).hexdigest()

        if use_cache and os.path.exists(cache_file):
            try:
                with open(cache_file, 'rb') as f:
                    cached_data = pickle.load(f)
                    if cached_data['hash'] == file_hash:
                        return cached_data['html'], counter, path
            except:
                pass

        # 读取文件
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 给 Recipe 添加编号前缀
        content = add_recipe_number_to_content(content, path)

        # 转换内部链接为PDF锚点
        content = convert_internal_links_in_content(content, path_to_anchor)

        # 转换为HTML
        html_content = mistune.html(content)

        # 缓存结果
        if use_cache:
            os.makedirs(cache_dir, exist_ok=True)
            with open(cache_file, 'wb') as f:
                pickle.dump({
                    'hash': file_hash,
                    'html': html_content
                }, f)

        return html_content, counter, path

    except Exception as e:
        print(f"  处理文件失败 {file_path}: {e}")
        return None, counter, path


def convert_internal_links_in_content(content, path_to_anchor):
    """转换markdown内容中的内部链接为PDF锚点"""

    def replace_link(match):
        link_text = match.group(1)
        link_url = match.group(2)

        # 只处理相对路径的 .md 链接
        if not (link_url.endswith('.md') or '.md#' in link_url):
            return match.group(0)

        # 提取文件路径和锚点
        if '#' in link_url:
            file_path, anchor = link_url.split('#', 1)
        else:
            file_path = link_url
            anchor = None

        # 规范化路径
        normalized_path = file_path
        while normalized_path.startswith('./'):
            normalized_path = normalized_path[2:]
        while normalized_path.startswith('../'):
            normalized_path = normalized_path[3:]

        # 查找对应的锚点ID
        target_anchor = None
        if normalized_path in path_to_anchor:
            target_anchor = path_to_anchor[normalized_path]
        else:
            # 模糊匹配文件名
            filename = normalized_path.split('/')[-1]
            for path, anchor_id in path_to_anchor.items():
                if path.endswith(filename):
                    target_anchor = anchor_id
                    break

        if target_anchor:
            if anchor:
                return f'[{link_text}](#{target_anchor}-{anchor})'
            else:
                return f'[{link_text}](#{target_anchor})'
        else:
            # 找不到映射，返回纯文本
            return f'{link_text}'

    # 处理所有链接
    content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', replace_link, content)
    return content


# ============================================================================
# 主转换器
# ============================================================================

class FinalDocsToPDFConverter:
    """Web RE Cookbook PDF转换器 - 完善版"""

    def __init__(self, docs_dir="docs", mkdocs_file="mkdocs.yml",
                 section_filter=None, validate=True, auto_fix=False,
                 use_cache=True, workers=None):
        self.docs_dir = docs_dir
        self.mkdocs_file = mkdocs_file
        self.output_dir = "output"
        self.cache_dir = os.path.join(self.output_dir, ".cache")
        self.nav_structure = []
        self.font_config = FontConfiguration()
        self.path_to_anchor = {}
        self.section_filter = section_filter
        self.validate = validate
        self.auto_fix = auto_fix
        self.use_cache = use_cache
        self.workers = workers or os.cpu_count()

        # 作者信息
        self.author_email = "overkazaf@gmail.com"
        self.author_wechat = "_0xAF_"
        self.generation_date = datetime.now().strftime('%Y-%m-%d')

        os.makedirs(self.output_dir, exist_ok=True)
        if use_cache:
            os.makedirs(self.cache_dir, exist_ok=True)

    def load_navigation_structure(self):
        """从mkdocs.yml加载导航结构"""
        try:
            with open(self.mkdocs_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                self.nav_structure = config.get('nav', [])
                print(f"  已加载导航结构，共 {len(self.nav_structure)} 个主要部分")
                return self.nav_structure
        except Exception as e:
            print(f"  加载mkdocs.yml失败: {e}")
            return []

    def should_include_section(self, section_idx, section_name):
        """判断是否应该包含该章节"""
        if self.section_filter is None:
            return True

        if section_idx in self.section_filter:
            return True

        for filter_name in self.section_filter:
            if isinstance(filter_name, str) and filter_name.lower() in section_name.lower():
                return True

        return False

    def build_path_anchor_mapping(self):
        """预先构建文件路径到锚点ID的映射"""
        counter = 0

        def scan_nav_items(nav_items):
            nonlocal counter
            for item in nav_items:
                if isinstance(item, dict):
                    for title, path in item.items():
                        if isinstance(path, str):
                            counter += 1
                            anchor_id = f"section-{counter}"
                            self.path_to_anchor[path] = anchor_id
                        elif isinstance(path, list):
                            scan_nav_items(path)

        for section in self.nav_structure:
            if isinstance(section, dict):
                for section_name, items in section.items():
                    if section_name != "Home" and isinstance(items, list):
                        scan_nav_items(items)

        print(f"  已建立 {len(self.path_to_anchor)} 个文件路径映射")

    def validate_and_fix_files(self):
        """验证并修复文件格式"""
        if not self.validate:
            return

        print("\n  验证文件格式...")

        total_issues = 0
        total_fixes = 0

        for path, anchor_id in self.path_to_anchor.items():
            file_path = os.path.join(self.docs_dir, path)
            if not os.path.exists(file_path):
                continue

            # 检查是否有问题
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                has_issues = False

                # 检查未闭合的代码块
                in_code_block = False
                for line in content.split('\n'):
                    if re.match(r'^```', line):
                        in_code_block = not in_code_block
                if in_code_block:
                    has_issues = True
                    total_issues += 1

                if has_issues and self.auto_fix:
                    fixes = QuickFormatFixer.fix_file_issues(file_path)
                    total_fixes += fixes

            except:
                continue

        if total_issues > 0:
            print(f"  发现 {total_issues} 个格式问题")
            if self.auto_fix:
                print(f"  已自动修复 {total_fixes} 个问题")
        else:
            print("  所有文件格式正确")

    def collect_files_to_process(self):
        """收集所有需要处理的文件"""
        files_to_process = []
        article_counter = 0

        def collect_nav_items(nav_items):
            nonlocal article_counter
            for item in nav_items:
                if isinstance(item, dict):
                    for title, path in item.items():
                        if isinstance(path, str):
                            article_counter += 1
                            file_path = os.path.join(self.docs_dir, path)
                            if os.path.exists(file_path):
                                files_to_process.append((
                                    file_path, path, article_counter,
                                    self.use_cache, self.cache_dir,
                                    self.path_to_anchor
                                ))
                        elif isinstance(path, list):
                            collect_nav_items(path)

        section_idx = 0
        for section in self.nav_structure:
            if isinstance(section, dict):
                for section_name, items in section.items():
                    if section_name == "Home":
                        section_idx += 1
                        continue

                    if not self.should_include_section(section_idx, section_name):
                        section_idx += 1
                        continue

                    section_idx += 1
                    if isinstance(items, list):
                        collect_nav_items(items)

        return files_to_process

    def merge_docs_files_parallel(self):
        """并行合并所有docs文件"""
        if not self.nav_structure:
            self.load_navigation_structure()

        self.build_path_anchor_mapping()

        # 验证和修复（如果需要）
        if self.validate:
            self.validate_and_fix_files()

        # 创建基础HTML
        full_html = """
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Web Reverse Engineering Cookbook</title>
        </head>
        <body>
        """

        # 添加封面和目录
        full_html += self.create_cover_page()
        full_html += self.create_table_of_contents()

        # 收集所有要处理的文件
        files_to_process = self.collect_files_to_process()
        print(f"\n  开始并行处理 {len(files_to_process)} 个文件，使用 {self.workers} 个工作进程...")

        # 并行处理文件
        results = {}
        with ProcessPoolExecutor(max_workers=self.workers) as executor:
            futures = {executor.submit(process_single_markdown_file, args): args
                      for args in files_to_process}

            completed = 0
            for future in as_completed(futures):
                html_content, counter, path = future.result()
                if html_content:
                    results[counter] = (html_content, path)
                    completed += 1
                    if completed % 10 == 0 or completed == len(files_to_process):
                        print(f"    进度: {completed}/{len(files_to_process)}")

        print(f"  并行处理完成，共处理 {len(results)} 个文件")

        section_idx = 0
        for section in self.nav_structure:
            if isinstance(section, dict):
                for section_name, items in section.items():
                    if section_name == "Home":
                        section_idx += 1
                        continue

                    if not self.should_include_section(section_idx, section_name):
                        section_idx += 1
                        continue

                    section_idx += 1

                    full_html += f"""
                    <div class="chapter">
                        <h1 class="no-page-break">{section_name}</h1>
                    """

                    # 收集该section下的所有结果
                    def add_results(nav_items, html_output):
                        for item in nav_items:
                            if isinstance(item, dict):
                                for title, path in item.items():
                                    if isinstance(path, str) and path in self.path_to_anchor:
                                        counter = int(self.path_to_anchor[path].split('-')[1])
                                        if counter in results:
                                            html_content, _ = results[counter]
                                            anchor_id = self.path_to_anchor[path]
                                            # 获取 Recipe 编号
                                            recipe_prefix = ""
                                            if path in RECIPE_NUMBERS:
                                                recipe_prefix = f"[{RECIPE_NUMBERS[path]}] "
                                            html_output.append(f"""
                                            <div class="section" id="{anchor_id}">
                                                <h2>{recipe_prefix}{title}</h2>
                                                {html_content}
                                            </div>
                                            """)
                                    elif isinstance(path, list):
                                        add_results(path, html_output)

                    section_html = []
                    if isinstance(items, list):
                        add_results(items, section_html)
                    full_html += ''.join(section_html)
                    full_html += "</div>"

        full_html += """
        </body>
        </html>
        """

        return full_html

    def create_cover_page(self):
        """创建封面页面 - 包含作者信息和人机协作说明"""
        return f"""
        <div class="cover-page">
            <div style="margin-top: 120pt;">
                <h1 style="font-size: 40pt; color: #1a1a1a; margin-bottom: 20pt; border: none; page-break-before: auto;" class="no-page-break">
                    Web Reverse Engineering<br/>Cookbook
                </h1>
                <h2 style="font-size: 18pt; color: #666; font-weight: 400; border: none; padding: 0;">
                    Complete Guide to Web Security Analysis & Data Extraction
                </h2>
                <div style="margin-top: 50pt; font-size: 12pt; color: #888;">
                    <p>Browser DevTools, Traffic Analysis, JavaScript Deobfuscation</p>
                    <p>CAPTCHA Bypass, Fingerprinting, Anti-Scraping Techniques</p>
                    <p>Distributed Crawling, Engineering Best Practices</p>
                </div>
            </div>
        </div>
        <div style="page-break-before: always; text-align: center; margin-top: 60pt;">
            <div style="font-size: 12pt; color: #aaa;">
                <p style="font-size: 40pt; margin-bottom: 15pt;">&#x1F310;</p>
                <p style="font-size: 16pt; color: #666; margin-bottom: 20pt;"><strong>Authors: +5, Gemini Pro 3.0, Claude Code Opus 4.5</strong></p>
                <p>Email: {self.author_email}</p>
                <p>WeChat: {self.author_wechat}</p>
                <p style="margin-top: 25pt;">Date: {self.generation_date}</p>
                <p>Version: v2.0</p>
            </div>
            <div style="margin-top: 30pt; padding: 20pt 35pt; background-color: #fff8e1; border-radius: 8pt; border-left: 4px solid #ffa726; text-align: left;">
                <p style="font-size: 13pt; color: #e65100; font-weight: 600; margin-bottom: 12pt; text-align: center;">
                    About This Cookbook | 关于这本食谱
                </p>
                <p style="font-size: 10pt; color: #444; line-height: 1.8; text-align: justify; margin-bottom: 10pt;">
                    这本食谱的诞生，是一次有趣的<strong>人机协作</strong>实验。除了笔者（<strong>+5</strong>）在Web逆向工程领域的日常记录和实战经验积累，
                    本书还得到了两位AI助手的鼎力支持——<strong>Gemini Pro 3.0</strong>和<strong>Claude Code Opus 4.5</strong>。
                    这个协作过程就像一个真实的技术团队：
                </p>
                <div style="margin-left: 15pt; margin-bottom: 10pt;">
                    <p style="font-size: 9.5pt; color: #444; line-height: 1.7; margin-bottom: 6pt;">
                        <strong>Gemini Pro 3.0</strong>（研究员 & 知识架构师）：负责技术调研、资料搜集、知识体系整理，
                        以及提供技术思路和解决方案建议，就像团队中的技术顾问和知识管家。
                    </p>
                    <p style="font-size: 9.5pt; color: #444; line-height: 1.7; margin-bottom: 6pt;">
                        <strong>Claude Code Opus 4.5</strong>（软件工程师 & 自动化专家）：负责编写和优化代码示例、
                        批量处理Markdown格式问题、自动化文档生成流程，以及代码质量把关，就像团队中的全栈开发和DevOps工程师。
                    </p>
                    <p style="font-size: 9.5pt; color: #444; line-height: 1.7; margin-bottom: 6pt;">
                        <strong>+5</strong>（技术负责人 & 总编辑）：负责整体架构设计、技术方向把控、内容审核修订、
                        以及最终质量保障，就像团队中的Tech Lead和Editor-in-Chief。
                    </p>
                </div>
                <p style="font-size: 9.5pt; color: #555; line-height: 1.7; text-align: justify; font-style: italic;">
                    This cookbook is born from an intriguing human-AI collaboration, like a real tech team:
                    Gemini Pro 3.0 (Research Engineer) handles technical research and knowledge organization;
                    Claude Code Opus 4.5 (Software Engineer) crafts code examples and automates documentation;
                    +5 (Tech Lead) steers the architecture, content revision, and quality assurance.
                </p>
            </div>
            <div style="margin-top: 25pt; padding: 18pt 35pt; border-top: 1px solid #ddd; border-bottom: 1px solid #ddd;">
                <p style="font-size: 11pt; color: #555; font-style: italic; line-height: 1.7; text-align: center;">
                    "If the highest aim of a captain were to preserve his ship,<br/>
                    he would keep it in port forever."
                </p>
                <p style="font-size: 9pt; color: #888; text-align: right; margin-top: 8pt;">
                    — St. Thomas Aquinas, <em>Summa Theologica</em> (1265-1274)
                </p>
            </div>
            <div style="margin-top: 25pt; padding: 18pt 35pt; background-color: #e3f2fd; border-radius: 8pt;">
                <p style="font-size: 11pt; color: #1565c0; font-weight: 600; margin-bottom: 10pt; text-align: center;">
                    Recipe 编号系统 | Recipe Numbering System
                </p>
                <p style="font-size: 10pt; color: #444; line-height: 1.8; text-align: justify;">
                    本书中的每个Recipe都有唯一编号（R01, R02, ...），便于快速定位和交叉引用。
                    目录页面会显示所有Recipe及其编号，帮助你快速找到需要的内容。
                </p>
                <p style="font-size: 9.5pt; color: #666; line-height: 1.7; text-align: justify; font-style: italic; margin-top: 8pt;">
                    Each recipe in this cookbook is assigned a unique identifier (R01, R02, etc.) for easy reference.
                    The table of contents displays all recipes with their numbers.
                </p>
            </div>
        </div>
        """

    def create_table_of_contents(self):
        """创建详细目录页面 - 带 Recipe 编号，与 Android 版保持一致"""
        toc_html = """
        <div class="toc-page">
            <h1 class="toc-title no-page-break">Table of Contents | 目录</h1>
        """

        # 构建目录条目
        toc_entries = []

        def build_toc_entries(nav_items, level=0, parent_has_multiple_sections=False):
            """
            递归构建目录条目
            level: 当前层级
            parent_has_multiple_sections: 父级 Part 是否有多个子 section
            """
            entries = []
            for item in nav_items:
                if isinstance(item, dict):
                    for title, path in item.items():
                        if isinstance(path, str):
                            recipe_num = RECIPE_NUMBERS.get(path, "")
                            entries.append({
                                'title': title,
                                'recipe': recipe_num,
                                'level': level,
                                'path': path
                            })
                        elif isinstance(path, list):
                            # 子章节
                            entries.append({
                                'title': title,
                                'recipe': '',
                                'level': level,
                                'is_section': True,
                                'parent_has_multiple': parent_has_multiple_sections
                            })
                            entries.extend(build_toc_entries(path, level + 1, parent_has_multiple_sections))
            return entries

        for section in self.nav_structure:
            if isinstance(section, dict):
                for section_name, items in section.items():
                    if section_name == "Home":
                        continue
                    # 添加主章节 (Part)
                    toc_entries.append({
                        'title': section_name,
                        'recipe': '',
                        'level': 0,
                        'is_part': True
                    })
                    if isinstance(items, list):
                        # 检查这个 Part 下有多少个子 section
                        section_count = sum(1 for item in items if isinstance(item, dict) and isinstance(list(item.values())[0], list))
                        has_multiple_sections = section_count > 1
                        toc_entries.extend(build_toc_entries(items, 1, has_multiple_sections))

        # 生成目录HTML
        for entry in toc_entries:
            if entry.get('is_part'):
                toc_html += f"""
                <div class="toc-part">
                    <h2 style="color: #2c3e50; font-size: 14pt; margin-top: 20pt; margin-bottom: 10pt; border-left: 4px solid #4CAF50; padding-left: 10pt;">
                        {entry['title']}
                    </h2>
                </div>
                """
            elif entry.get('is_section'):
                indent = entry['level'] * 15
                # 如果父级 Part 有多个 section，使用更醒目的样式
                if entry.get('parent_has_multiple'):
                    toc_html += f"""
                    <div class="toc-section" style="margin-left: {indent}pt; margin-top: 10pt; margin-bottom: 6pt; padding: 4pt 8pt; background-color: #f5f5f5; border-radius: 4pt; border-left: 3px solid #81c784;">
                        <span style="font-weight: 600; color: #2e7d32; font-size: 10.5pt;">{entry['title']}</span>
                    </div>
                    """
                else:
                    toc_html += f"""
                    <div class="toc-section" style="margin-left: {indent}pt; margin-top: 8pt; margin-bottom: 4pt;">
                        <span style="font-weight: 600; color: #444; font-size: 10.5pt;">{entry['title']}</span>
                    </div>
                    """
            else:
                indent = entry['level'] * 15
                recipe_badge = f'<span style="background: #e8f5e9; color: #2e7d32; padding: 1pt 5pt; border-radius: 3pt; font-size: 8pt; font-weight: 600; margin-right: 6pt;">{entry["recipe"]}</span>' if entry['recipe'] else ''
                toc_html += f"""
                <div class="toc-entry" style="margin-left: {indent}pt; margin-top: 3pt; padding: 3pt 0;">
                    {recipe_badge}<span style="color: #555; font-size: 9.5pt;">{entry['title']}</span>
                </div>
                """

        toc_html += """
            <div style="margin-top: 25pt; text-align: center; color: #888; font-size: 10pt; border-top: 1px solid #ddd; padding-top: 15pt;">
                <p>Total Recipes: 82 | 共 82 个 Recipe</p>
            </div>
        </div>
        """

        return toc_html

    def create_css_styles(self):
        """创建PDF样式 - 完善的中文字体支持"""
        css_content = """
        /* 使用系统字体确保中文正确显示 */
        @font-face {
            font-family: 'Chinese Sans';
            src: url('file:///System/Library/Fonts/Hiragino Sans GB.ttc') format('truetype'),
                 url('file:///System/Library/Fonts/STHeiti Light.ttc') format('truetype'),
                 url('file:///System/Library/Fonts/Supplemental/Songti.ttc') format('truetype'),
                 url('file:///Library/Fonts/Arial Unicode.ttf') format('truetype');
            font-weight: normal;
        }

        @font-face {
            font-family: 'Chinese Sans';
            src: url('file:///System/Library/Fonts/Hiragino Sans GB.ttc') format('truetype'),
                 url('file:///System/Library/Fonts/STHeiti Medium.ttc') format('truetype'),
                 url('file:///System/Library/Fonts/Supplemental/Songti.ttc') format('truetype');
            font-weight: bold;
        }

        @font-face {
            font-family: 'Code Font';
            src: url('file:///System/Library/Fonts/Menlo.ttc') format('truetype'),
                 url('file:///System/Library/Fonts/Monaco.dfont') format('truetype'),
                 url('file:///Library/Fonts/Arial Unicode.ttf') format('truetype');
        }

        /* 页面设置 */
        @page {
            size: A4;
            margin: 2.5cm 2cm 3cm 2cm;

            @top-left {
                content: "Web RE Cookbook";
                font-family: 'Chinese Sans', sans-serif;
                font-size: 10pt;
                color: #666;
                border-bottom: 1px solid #e0e0e0;
                padding-bottom: 5pt;
            }

            @top-right {
                content: "Page " counter(page);
                font-family: 'Chinese Sans', sans-serif;
                font-size: 10pt;
                color: #666;
                border-bottom: 1px solid #e0e0e0;
                padding-bottom: 5pt;
            }

            @bottom-center {
                content: "Web Reverse Engineering Cookbook v2.0";
                font-family: 'Chinese Sans', sans-serif;
                font-size: 9pt;
                color: #999;
                border-top: 1px solid #e0e0e0;
                padding-top: 5pt;
            }
        }

        /* 基础样式 */
        body {
            font-family: 'Chinese Sans', 'Noto Sans SC', 'Microsoft YaHei', sans-serif;
            font-size: 11pt;
            line-height: 1.8;
            color: #333;
            background: white;
        }

        /* 标题样式 */
        h1 {
            font-family: 'Chinese Sans', sans-serif;
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
            font-family: 'Chinese Sans', sans-serif;
            font-size: 18pt;
            font-weight: 600;
            color: #2c3e50;
            margin-top: 25pt;
            margin-bottom: 15pt;
            border-left: 4px solid #4CAF50;
            padding-left: 15pt;
            page-break-after: avoid;
        }

        h3 {
            font-family: 'Chinese Sans', sans-serif;
            font-size: 14pt;
            font-weight: 500;
            color: #34495e;
            margin-top: 20pt;
            margin-bottom: 12pt;
            page-break-after: avoid;
        }

        h4 {
            font-family: 'Chinese Sans', sans-serif;
            font-size: 12pt;
            font-weight: 500;
            color: #555;
            margin-top: 15pt;
            margin-bottom: 10pt;
            page-break-after: avoid;
        }

        /* 段落样式 */
        p {
            margin-bottom: 12pt;
            text-align: justify;
            orphans: 3;
            widows: 3;
        }

        /* 列表样式 */
        ul, ol {
            margin-bottom: 12pt;
            padding-left: 25pt;
        }

        li {
            margin-bottom: 6pt;
            orphans: 2;
            widows: 2;
        }

        /* 代码样式 */
        code {
            font-family: 'Code Font', 'Menlo', 'Monaco', 'Consolas', monospace;
            font-size: 9pt;
            background-color: #f8f9fa;
            padding: 2pt 4pt;
            border-radius: 3pt;
            border: 1px solid #e9ecef;
            word-wrap: break-word;
        }

        pre {
            font-family: 'Code Font', 'Menlo', 'Monaco', 'Consolas', monospace;
            font-size: 8.5pt;
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 6pt;
            padding: 12pt;
            margin: 12pt 0;
            overflow-x: auto;
            line-height: 1.5;
            white-space: pre-wrap;
            word-wrap: break-word;
            page-break-inside: avoid;
        }

        pre code {
            background: none;
            border: none;
            padding: 0;
            font-size: 8.5pt;
        }

        /* 表格样式 */
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 15pt 0;
            font-size: 10pt;
            page-break-inside: avoid;
        }

        th, td {
            border: 1px solid #ddd;
            padding: 8pt 12pt;
            text-align: left;
            word-wrap: break-word;
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
            color: #4CAF50;
            text-decoration: none;
            word-wrap: break-word;
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

        /* 封面样式 */
        .cover-page {
            text-align: center;
            page-break-after: always;
        }

        /* 目录样式 */
        .toc-page {
            page-break-after: always;
        }

        .toc-title {
            font-size: 28pt;
            font-weight: 700;
            text-align: center;
            color: #1a1a1a;
            margin-bottom: 30pt;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 15pt;
        }

        /* 章节样式 */
        .chapter {
            page-break-before: always;
        }

        /* 每个序号章节另起一页 */
        .section {
            margin-bottom: 30pt;
            page-break-before: always;
        }

        /* 第一个section不分页（紧跟大章节标题） */
        .chapter .section:first-of-type {
            page-break-before: auto;
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

    def generate_pdf(self, output_filename="web_reverse_engineering_cookbook_v2.pdf"):
        """生成PDF文件"""
        print("\n" + "=" * 60)
        print("Web RE Cookbook - PDF Generator (Final Edition)")
        print("=" * 60)
        print(f"  并行处理: {self.workers} 个工作进程")
        print(f"  缓存: {'启用' if self.use_cache else '禁用'}")
        print(f"  验证: {'启用' if self.validate else '禁用'}")
        print(f"  自动修复: {'启用' if self.auto_fix else '禁用'}")
        print("=" * 60)

        # 合并所有docs文件
        html_content = self.merge_docs_files_parallel()

        # 创建CSS样式
        css_styles = self.create_css_styles()

        # 生成PDF
        if os.path.dirname(output_filename):
            output_path = output_filename
        else:
            output_path = os.path.join(self.output_dir, output_filename)

        try:
            print("\n  正在渲染PDF...")
            html_doc = HTML(string=html_content)
            html_doc.write_pdf(
                output_path,
                stylesheets=[css_styles],
                font_config=self.font_config
            )

            file_size_mb = os.path.getsize(output_path) / 1024 / 1024

            print(f"\n  PDF生成成功!")
            print(f"  文件路径: {output_path}")
            print(f"  文件大小: {file_size_mb:.2f} MB")

            # 保存HTML用于调试
            html_path = os.path.join(self.output_dir, "docs_final_debug.html")
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"  调试HTML: {html_path}")

            print("\n" + "=" * 60)
            print("  PDF生成完成!")
            print("  特性:")
            print("     Recipe 编号 (R01-R82)")
            print("     详细目录（带 Recipe 编号）")
            print("     作者信息 & 人机协作说明")
            print("     完善中文支持")
            print("     PDF内链接跳转")
            print("     智能缓存")
            print("=" * 60)

            return output_path

        except Exception as e:
            print(f"\n  PDF生成失败: {e}")
            import traceback
            traceback.print_exc()
            return None


def parse_section_filter(sections_arg):
    """解析章节过滤参数"""
    if not sections_arg:
        return None

    result = []
    for item in sections_arg.split(','):
        item = item.strip()
        try:
            result.append(int(item))
        except ValueError:
            result.append(item)

    return result


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Web RE Cookbook - PDF Generator (Final Edition)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s                                  # 完整流程（推荐）
  %(prog)s --sections 0,1 -w 8              # 指定章节和进程数
  %(prog)s --no-cache                       # 禁用缓存（文件修改后）
  %(prog)s --skip-validation                # 跳过验证快速生成
  %(prog)s --fix-files                      # 修复文件格式问题
  %(prog)s --fix-files --no-cache -w 12     # 组合使用
        """
    )
    parser.add_argument('--sections', '-s', type=str,
                       help='指定要生成的章节（索引或名称，逗号分隔）')
    parser.add_argument('--output', '-o', type=str,
                       help='输出文件名')
    parser.add_argument('--no-cache', action='store_true',
                       help='禁用缓存')
    parser.add_argument('--skip-validation', action='store_true',
                       help='跳过格式验证')
    parser.add_argument('--fix-files', action='store_true',
                       help='自动修复文件格式问题')
    parser.add_argument('--workers', '-w', type=int,
                       help='并行工作进程数（默认：CPU核心数）')

    args = parser.parse_args()

    print("=" * 60)
    print("Web RE Cookbook - PDF Generator")
    print("Final Edition with Recipe Numbering")
    print("=" * 60)
    print("  特性:")
    print("     Recipe 编号 (R01-R82)")
    print("     详细目录（带 Recipe 编号）")
    print("     作者信息 & 人机协作说明")
    print("     并行处理 (2-4倍提速)")
    print("     完善中文支持")
    print("     PDF内链接跳转")
    print("     智能缓存 (10-20倍二次提速)")
    print("=" * 60)

    # 检查依赖
    try:
        import mistune
        import weasyprint
        import yaml
        print("  依赖检查通过")
    except ImportError as e:
        print(f"  缺少依赖: {e}")
        print("请运行: pip install mistune weasyprint pillow pyyaml")
        return

    section_filter = parse_section_filter(args.sections) if args.sections else None

    converter = FinalDocsToPDFConverter(
        section_filter=section_filter,
        validate=not args.skip_validation,
        auto_fix=args.fix_files,
        use_cache=not args.no_cache,
        workers=args.workers
    )

    nav = converter.load_navigation_structure()
    if not nav:
        print("  未找到导航结构")
        return

    if section_filter:
        print(f"\n  将生成章节: {section_filter}")

    output_filename = args.output if args.output else "web_reverse_engineering_cookbook_v2.pdf"
    if section_filter:
        base_name = output_filename.replace('.pdf', '')
        output_filename = f"{base_name}_partial.pdf"

    converter.generate_pdf(output_filename)


if __name__ == "__main__":
    main()
