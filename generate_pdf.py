#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reverse Engineering Cookbook - Unified PDF Generator

Unified PDF generator for both Android and Web reverse engineering cookbooks.
Outputs all PDFs to the project root's output directory.

Features:
1. Recipe numbering - Each recipe has a unique ID (R01, R02, ...)
2. Detailed TOC - Table of contents with Recipe numbers
3. Parallel processing - 2-4x speed improvement
4. Chinese font support - No encoding issues
5. Internal link conversion - MD links to PDF anchors
6. Format auto-fix - Code blocks, lists, headings
7. Smart caching - 10-20x faster regeneration
8. Unified output - All PDFs in ./output/

Usage:
    python generate_pdf.py android              # Generate Android PDF
    python generate_pdf.py web                  # Generate Web PDF
    python generate_pdf.py all                  # Generate both PDFs
    python generate_pdf.py android -w 8         # Use 8 worker processes
    python generate_pdf.py web --no-cache       # Disable cache
    python generate_pdf.py all --fix-files      # Auto-fix format issues
"""

import os
import re
import sys
import yaml
import hashlib
import pickle
import argparse
from datetime import datetime
from typing import List, Dict, Optional
from concurrent.futures import ProcessPoolExecutor, as_completed

import mistune
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration


# ============================================================================
# Project Configuration
# ============================================================================

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")
CACHE_DIR = os.path.join(OUTPUT_DIR, ".cache")

PROJECTS = {
    "android": {
        "name": "Android Reverse Engineering Cookbook",
        "short_name": "Android RE Cookbook",
        "docs_dir": os.path.join(PROJECT_ROOT, "android_reversing", "docs"),
        "mkdocs_file": os.path.join(PROJECT_ROOT, "android_reversing", "mkdocs.yml"),
        "output_file": "android_reverse_engineering_cookbook.pdf",
        "theme_color": "#4a90e2",
        "icon": "",
        "subtitle": "从入门到精通的 Android 逆向与安全分析",
        "created_date": "2025-08-01",
        "topics": [
            "基础知识、工具指南、实战技巧与进阶主题",
            "涵盖 Frida、Unidbg、Xposed、IDA Pro 等核心工具",
            "包含数据分析、工程实践与真实案例研究"
        ]
    },
    "web": {
        "name": "Web Reverse Engineering Cookbook",
        "short_name": "Web RE Cookbook",
        "docs_dir": os.path.join(PROJECT_ROOT, "web_reversing", "docs"),
        "mkdocs_file": os.path.join(PROJECT_ROOT, "web_reversing", "mkdocs.yml"),
        "output_file": "web_reverse_engineering_cookbook.pdf",
        "theme_color": "#4CAF50",
        "icon": "",
        "subtitle": "从入门到精通的 Web 逆向与数据采集",
        "created_date": "2025-10-13",
        "topics": [
            "基础知识、工具指南、实战技巧与进阶配方",
            "涵盖 DevTools、Burp Suite、Puppeteer 等核心工具",
            "包含分布式爬虫、工程实践与真实案例研究"
        ]
    }
}


# ============================================================================
# Recipe Numbering - Maps file paths to Recipe IDs (separated by project)
# ============================================================================

ANDROID_RECIPE_NUMBERS = {
    # Quick Start (Q系列)
    "00-Quick-Start/intro.md": "Q01",
    "00-Quick-Start/index.md": "Q02",
    "00-Quick-Start/setup.md": "Q03",

    # Recipes - 按 mkdocs.yml 中的实际顺序编号 (R01-R35)
    # ===== 入门基础 (R01-R03) =====
    "01-Recipes/Analysis/re_workflow.md": "R01",
    "01-Recipes/Network/network_sniffing.md": "R02",
    "01-Recipes/Scripts/objection_snippets.md": "R03",
    # ===== 核心分析 (R04-R08) =====
    "01-Recipes/Analysis/static_analysis_deep_dive.md": "R04",
    "01-Recipes/Analysis/dynamic_analysis_deep_dive.md": "R05",
    "01-Recipes/Scripts/frida_common_scripts.md": "R06",
    "01-Recipes/Native/jni_development.md": "R07",
    "01-Recipes/Native/so_compilation.md": "R08",
    # ===== 脱壳与解密 (R09-R13) =====
    "01-Recipes/Unpacking/un-packing.md": "R09",
    "01-Recipes/Unpacking/frida_unpacking_and_so_fixing.md": "R10",
    "01-Recipes/Network/crypto_analysis.md": "R11",
    "01-Recipes/Unpacking/so_string_deobfuscation.md": "R12",
    "01-Recipes/Analysis/native_string_obfuscation.md": "R13",
    # ===== 反检测对抗 (R14-R18) =====
    "01-Recipes/Anti-Detection/app_hardening_identification.md": "R14",
    "01-Recipes/Anti-Detection/frida_anti_debugging.md": "R15",
    "01-Recipes/Anti-Detection/xposed_anti_debugging.md": "R16",
    "01-Recipes/Anti-Detection/device_fingerprinting_and_bypass.md": "R17",
    "01-Recipes/Scripts/native_hooking.md": "R18",
    # ===== 高级反混淆 (R19-R22) =====
    "01-Recipes/Unpacking/so_obfuscation_deobfuscation.md": "R19",
    "01-Recipes/Analysis/ollvm_deobfuscation.md": "R20",
    "01-Recipes/Analysis/vmp_analysis.md": "R21",
    "01-Recipes/Scripts/c_for_emulation.md": "R22",
    # ===== 网络与协议 (R23-R27) =====
    "01-Recipes/Network/tls_fingerprinting_guide.md": "R23",
    "01-Recipes/Network/ja3_fingerprinting.md": "R24",
    "01-Recipes/Network/ja4_fingerprinting.md": "R25",
    "01-Recipes/Anti-Detection/captcha_bypassing_techniques.md": "R26",
    "01-Recipes/Anti-Detection/mobile_app_sec_and_anti_bot.md": "R27",
    # ===== 自动化工程 (R28-R35) =====
    "01-Recipes/Scripts/automation_scripts.md": "R28",
    "01-Recipes/Automation/scrapy.md": "R29",
    "01-Recipes/Automation/scrapy_redis_distributed.md": "R30",
    "01-Recipes/Automation/proxy_pool_design.md": "R31",
    "01-Recipes/Automation/dial_up_proxy_pools.md": "R32",
    "01-Recipes/Automation/docker_deployment.md": "R33",
    "01-Recipes/Automation/virtualization_and_containers.md": "R34",
    "01-Recipes/Automation/automation_and_device_farming.md": "R35",

    # Tools - Dynamic (T01-T06)
    "02-Tools/Dynamic/frida_guide.md": "T01",
    "02-Tools/Dynamic/frida_internals.md": "T02",
    "02-Tools/Dynamic/xposed_guide.md": "T03",
    "02-Tools/Dynamic/xposed_internals.md": "T04",
    "02-Tools/Dynamic/unidbg_guide.md": "T05",
    "02-Tools/Dynamic/unidbg_internals.md": "T06",
    # Tools - Static (T07-T09)
    "02-Tools/Static/ghidra_guide.md": "T07",
    "02-Tools/Static/ida_pro_guide.md": "T08",
    "02-Tools/Static/radare2_guide.md": "T09",
    # Tools - Cheatsheets (T10)
    "02-Tools/Cheatsheets/adb_cheatsheet.md": "T10",

    # Case Studies (C01-C08)
    "03-Case-Studies/case_anti_analysis_techniques.md": "C01",
    "03-Case-Studies/case_music_apps.md": "C02",
    "03-Case-Studies/case_social_media_and_anti_bot.md": "C03",
    "03-Case-Studies/case_study_app_encryption.md": "C04",
    "03-Case-Studies/case_video_apps_and_drm.md": "C05",
    "03-Case-Studies/case_unity_games.md": "C06",
    "03-Case-Studies/case_flutter_apps.md": "C07",
    "03-Case-Studies/case_malware_analysis.md": "C08",

    # Reference - Foundations (F01-F10)
    "04-Reference/Foundations/apk_structure.md": "F01",
    "04-Reference/Foundations/android_components.md": "F02",
    "04-Reference/Foundations/android_manifest.md": "F03",
    "04-Reference/Foundations/android_studio_debug_tools.md": "F04",
    "04-Reference/Foundations/dex_format.md": "F05",
    "04-Reference/Foundations/smali_syntax.md": "F06",
    "04-Reference/Foundations/so_elf_format.md": "F07",
    "04-Reference/Foundations/art_runtime.md": "F08",
    "04-Reference/Foundations/arm_assembly.md": "F09",
    "04-Reference/Foundations/x86_and_arm_assembly_basics.md": "F10",
    "04-Reference/Foundations/totp.md": "F11",
    "04-Reference/Foundations/selinux.md": "F12",
    "04-Reference/Foundations/binary_analysis_toolkit.md": "F13",

    # Reference - Advanced (A01-A07)
    "04-Reference/Advanced/android_sandbox_implementation.md": "A01",
    "04-Reference/Advanced/aosp_and_system_customization.md": "A02",
    "04-Reference/Advanced/aosp_device_modification.md": "A03",
    "04-Reference/Advanced/minimal_android_rootfs.md": "A04",
    "04-Reference/Advanced/so_anti_debugging_and_obfuscation.md": "A05",
    "04-Reference/Advanced/so_runtime_emulation.md": "A06",
    "04-Reference/Advanced/magisk_lsposed_internals.md": "A07",

    # Reference - Engineering (E01-E09)
    "04-Reference/Engineering/frameworks_and_middleware.md": "E01",
    "04-Reference/Engineering/message_queues.md": "E02",
    "04-Reference/Engineering/redis.md": "E03",
    "04-Reference/Engineering/risk_control_sdk_build_guide.md": "E04",
    "04-Reference/Engineering/Data-Analysis/data_warehousing_and_processing.md": "E05",
    "04-Reference/Engineering/Data-Analysis/flink.md": "E06",
    "04-Reference/Engineering/Data-Analysis/hbase.md": "E07",
    "04-Reference/Engineering/Data-Analysis/hive.md": "E08",
    "04-Reference/Engineering/Data-Analysis/spark.md": "E09",
    "04-Reference/Engineering/automation_vs_api_reverse.md": "E10",

    # Appendix (X01-X05)
    "05-Appendix/github_projects.md": "X01",
    "05-Appendix/learning_resources.md": "X02",
    "05-Appendix/ctf_platforms.md": "X03",
    "05-Appendix/glossary.md": "X04",
    "05-Appendix/numbering.md": "X05",
}

WEB_RECIPE_NUMBERS = {
    # Quick Start (Q01-Q04)
    "00-Quick-Start/index.md": "Q01",
    "00-Quick-Start/your_first_hook.md": "Q02",
    "00-Quick-Start/decrypt_api_params.md": "Q03",
    "00-Quick-Start/bypass_simple_captcha.md": "Q04",

    # Foundations (F01-F10)
    "01-Foundations/http_https_protocol.md": "F01",
    "01-Foundations/browser_architecture.md": "F02",
    "01-Foundations/javascript_basics.md": "F03",
    "01-Foundations/javascript_execution_mechanism.md": "F04",
    "01-Foundations/dom_and_bom.md": "F05",
    "01-Foundations/webassembly_basics.md": "F06",
    "01-Foundations/cookie_and_storage.md": "F07",
    "01-Foundations/cors_and_same_origin_policy.md": "F08",
    "01-Foundations/tls_ssl_handshake.md": "F09",
    "01-Foundations/web_api_and_ajax.md": "F10",

    # Tools (T01-T10)
    "02-Tooling/browser_devtools.md": "T01",
    "02-Tooling/burp_suite_guide.md": "T02",
    "02-Tooling/fiddler_guide.md": "T03",
    "02-Tooling/charles_guide.md": "T04",
    "02-Tooling/wireshark_guide.md": "T05",
    "02-Tooling/puppeteer_playwright.md": "T06",
    "02-Tooling/selenium_guide.md": "T07",
    "02-Tooling/ast_tools.md": "T08",
    "02-Tooling/nodejs_debugging.md": "T09",
    "02-Tooling/v8_tools.md": "T10",

    # Recipes - Basic (R01-R07)
    "03-Basic-Recipes/re_workflow.md": "R01",
    "03-Basic-Recipes/debugging_techniques.md": "R02",
    "03-Basic-Recipes/hooking_techniques.md": "R03",
    "03-Basic-Recipes/api_reverse_engineering.md": "R04",
    "03-Basic-Recipes/crypto_identification.md": "R05",
    "03-Basic-Recipes/dynamic_parameter_analysis.md": "R06",
    "03-Basic-Recipes/websocket_reversing.md": "R07",

    # Recipes - Advanced (R08-R20)
    "04-Advanced-Recipes/javascript_deobfuscation.md": "R08",
    "04-Advanced-Recipes/captcha_bypass.md": "R09",
    "04-Advanced-Recipes/browser_fingerprinting.md": "R10",
    "04-Advanced-Recipes/javascript_vm_protection.md": "R11",
    "04-Advanced-Recipes/webassembly_reversing.md": "R12",
    "04-Advanced-Recipes/anti_scraping_deep_dive.md": "R13",
    "04-Advanced-Recipes/frontend_hardening.md": "R14",
    "04-Advanced-Recipes/csp_bypass.md": "R15",
    "04-Advanced-Recipes/webrtc_fingerprinting.md": "R16",
    "04-Advanced-Recipes/canvas_fingerprinting.md": "R17",
    "04-Advanced-Recipes/tls_fingerprinting.md": "R18",
    "04-Advanced-Recipes/http2_http3.md": "R19",
    "04-Advanced-Recipes/pwa_service_worker.md": "R20",

    # Case Studies (C01-C06)
    "05-Case-Studies/case_ecommerce.md": "C01",
    "05-Case-Studies/case_social_media.md": "C02",
    "05-Case-Studies/case_financial.md": "C03",
    "05-Case-Studies/case_video_streaming.md": "C04",
    "05-Case-Studies/case_news_aggregator.md": "C05",
    "05-Case-Studies/case_search_engine.md": "C06",

    # Engineering (E01-E07)
    "06-Engineering/distributed_scraping.md": "E01",
    "06-Engineering/proxy_pool_management.md": "E02",
    "06-Engineering/data_storage_solutions.md": "E03",
    "06-Engineering/message_queue_application.md": "E04",
    "06-Engineering/docker_deployment.md": "E05",
    "06-Engineering/monitoring_and_alerting.md": "E06",
    "06-Engineering/anti_anti_scraping_framework.md": "E07",

    # Scripts (S01-S04)
    "07-Scripts/javascript_hook_scripts.md": "S01",
    "07-Scripts/deobfuscation_scripts.md": "S02",
    "07-Scripts/automation_scripts.md": "S03",
    "07-Scripts/crypto_detection_scripts.md": "S04",

    # Cheat Sheets (H01-H05)
    "08-Cheat-Sheets/common_commands.md": "H01",
    "08-Cheat-Sheets/crypto_signatures.md": "H02",
    "08-Cheat-Sheets/tool_shortcuts.md": "H03",
    "08-Cheat-Sheets/regex_patterns.md": "H04",
    "08-Cheat-Sheets/http_headers.md": "H05",

    # Templates (P01-P05)
    "09-Templates/basic_scraper.md": "P01",
    "09-Templates/reverse_project.md": "P02",
    "09-Templates/docker_setup.md": "P03",
    "09-Templates/cicd_pipeline.md": "P04",
    "09-Templates/distributed_crawler.md": "P05",

    # Troubleshooting (D01-D06)
    "10-Troubleshooting/network_issues.md": "D01",
    "10-Troubleshooting/anti_scraping_issues.md": "D02",
    "10-Troubleshooting/javascript_debugging.md": "D03",
    "10-Troubleshooting/tool_issues.md": "D04",
    "10-Troubleshooting/data_issues.md": "D05",
    "10-Troubleshooting/docker_issues.md": "D06",

    # Appendix (X01-X03)
    "11-Resources/github_projects.md": "X01",
    "11-Resources/learning_resources.md": "X02",
    "11-Resources/faq.md": "X03",
}

# Combined for backward compatibility - used by functions that need both
RECIPE_NUMBERS = {**ANDROID_RECIPE_NUMBERS, **WEB_RECIPE_NUMBERS}


def add_recipe_number_to_content(content: str, path: str) -> str:
    """Add Recipe number prefix to the first heading in content (uses global RECIPE_NUMBERS)

    Skip if the heading already contains a recipe number pattern (e.g., R01:, T05:, etc.)
    """
    if path in RECIPE_NUMBERS:
        recipe_num = RECIPE_NUMBERS[path]
        # Match first level-1 heading (# xxx)
        pattern = r'^(#\s+)(.+)$'
        match = re.search(pattern, content, flags=re.MULTILINE)
        if match:
            heading_text = match.group(2)
            # Skip if heading already starts with a recipe number pattern (R01:, T05:, Q01:, etc.)
            if re.match(r'^[RTCFAESHDPQX]\d+:', heading_text):
                return content
            # Add recipe number prefix
            def replace_title(m):
                return f"{m.group(1)}{recipe_num}: {m.group(2)}"
            content = re.sub(pattern, replace_title, content, count=1, flags=re.MULTILINE)
    return content


def add_recipe_number_to_content_with_dict(content: str, path: str, recipe_numbers: dict) -> str:
    """Add Recipe number prefix to the first heading in content (uses provided recipe_numbers dict)

    Skip if the heading already contains a recipe number pattern (e.g., R01:, T05:, etc.)
    """
    if path in recipe_numbers:
        recipe_num = recipe_numbers[path]
        # Match first level-1 heading (# xxx)
        pattern = r'^(#\s+)(.+)$'
        match = re.search(pattern, content, flags=re.MULTILINE)
        if match:
            heading_text = match.group(2)
            # Skip if heading already starts with a recipe number pattern (R01:, T05:, Q01:, etc.)
            if re.match(r'^[RTCFAESHDPQX]\d+:', heading_text):
                return content
            # Add recipe number prefix
            def replace_title(m):
                return f"{m.group(1)}{recipe_num}: {m.group(2)}"
            content = re.sub(pattern, replace_title, content, count=1, flags=re.MULTILINE)
    return content


# ============================================================================
# Format Fixer
# ============================================================================

class QuickFormatFixer:
    """Quick format fixer for common Markdown issues"""

    @staticmethod
    def fix_file_issues(file_path: str) -> int:
        """Fix common format issues in a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except:
            return 0

        original_lines = lines[:]
        fixes = 0

        # 1. Fix unclosed code blocks
        in_code_block = False
        for line in lines:
            if re.match(r'^```', line):
                in_code_block = not in_code_block

        if in_code_block:
            if lines and not lines[-1].endswith('\n'):
                lines[-1] += '\n'
            lines.append('```\n')
            fixes += 1

        # 2. Fix list markers without space
        for i, line in enumerate(lines):
            match = re.match(r'^(\s*)([-*+]|\d+\.)([^\s])', line)
            if match:
                indent = match.group(1)
                marker = match.group(2)
                rest = line[len(indent) + len(marker):]
                lines[i] = f"{indent}{marker} {rest}"
                fixes += 1

        # 3. Fix headings without space
        for i, line in enumerate(lines):
            match = re.match(r'^(#{1,6})([^\s#])', line)
            if match:
                hashes = match.group(1)
                rest = line[len(hashes):]
                lines[i] = f"{hashes} {rest}"
                fixes += 1

        # Write back if fixed
        if fixes > 0 and lines != original_lines:
            try:
                backup_path = f"{file_path}.backup"
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.writelines(original_lines)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
            except:
                return 0

        return fixes


# ============================================================================
# Parallel Processing
# ============================================================================

def process_single_markdown_file(args):
    """Process a single markdown file (for parallel execution)"""
    file_path, path, counter, use_cache, cache_dir, path_to_anchor, recipe_numbers = args

    try:
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

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Add Recipe number to content's first heading (e.g., "# 验证码绕过" -> "# R27: 验证码绕过")
        content = add_recipe_number_to_content_with_dict(content, path, recipe_numbers)

        # Convert internal links to PDF anchors
        content = convert_internal_links(content, path_to_anchor)

        # Convert to HTML
        html_content = mistune.html(content)

        # Cache result
        if use_cache:
            os.makedirs(cache_dir, exist_ok=True)
            with open(cache_file, 'wb') as f:
                pickle.dump({
                    'hash': file_hash,
                    'html': html_content
                }, f)

        return html_content, counter, path

    except Exception as e:
        print(f"  Error processing {file_path}: {e}")
        return None, counter, path


def convert_internal_links(content, path_to_anchor):
    """Convert internal markdown links to PDF anchors"""

    def replace_link(match):
        link_text = match.group(1)
        link_url = match.group(2)

        if not (link_url.endswith('.md') or '.md#' in link_url):
            return match.group(0)

        if '#' in link_url:
            file_path, anchor = link_url.split('#', 1)
        else:
            file_path = link_url
            anchor = None

        normalized_path = file_path
        while normalized_path.startswith('./'):
            normalized_path = normalized_path[2:]
        while normalized_path.startswith('../'):
            normalized_path = normalized_path[3:]

        target_anchor = None
        if normalized_path in path_to_anchor:
            target_anchor = path_to_anchor[normalized_path]
        else:
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
            return f'{link_text}'

    content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', replace_link, content)
    return content


# ============================================================================
# Main PDF Converter
# ============================================================================

class UnifiedPDFConverter:
    """Unified PDF converter for both Android and Web cookbooks"""

    def __init__(self, project_key: str, validate=True, auto_fix=False,
                 use_cache=True, workers=None):
        if project_key not in PROJECTS:
            raise ValueError(f"Unknown project: {project_key}. Use 'android' or 'web'.")

        self.project = PROJECTS[project_key]
        self.project_key = project_key
        self.docs_dir = self.project["docs_dir"]
        self.mkdocs_file = self.project["mkdocs_file"]
        self.output_dir = OUTPUT_DIR
        self.cache_dir = os.path.join(CACHE_DIR, project_key)
        self.nav_structure = []
        self.font_config = FontConfiguration()
        self.path_to_anchor = {}
        self.validate = validate
        self.auto_fix = auto_fix
        self.use_cache = use_cache
        self.workers = workers or os.cpu_count()
        self.recipe_count = 0

        # Select recipe numbers based on project
        self.recipe_numbers = ANDROID_RECIPE_NUMBERS if project_key == "android" else WEB_RECIPE_NUMBERS

        # Author info
        self.author_email = "overkazaf@gmail.com"
        self.author_wechat = "_0xAF_"
        self.created_date = self.project.get("created_date", "2025-08-01")
        self.revision_date = datetime.now().strftime("%Y-%m-%d")

        os.makedirs(self.output_dir, exist_ok=True)
        if use_cache:
            os.makedirs(self.cache_dir, exist_ok=True)

    def load_navigation_structure(self):
        """Load navigation structure from mkdocs.yml"""
        try:
            with open(self.mkdocs_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                self.nav_structure = config.get('nav', [])
                print(f"  Loaded {len(self.nav_structure)} main sections")
                return self.nav_structure
        except Exception as e:
            print(f"  Failed to load mkdocs.yml: {e}")
            return []

    def build_path_anchor_mapping(self):
        """Build file path to anchor ID mapping"""
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

        self.recipe_count = sum(1 for path in self.path_to_anchor if path in self.recipe_numbers)
        print(f"  Built {len(self.path_to_anchor)} file path mappings")
        print(f"  Found {self.recipe_count} recipes with numbers")

    def validate_and_fix_files(self):
        """Validate and fix file format issues"""
        if not self.validate:
            return

        print("\n  Validating file formats...")

        total_issues = 0
        total_fixes = 0

        for path, anchor_id in self.path_to_anchor.items():
            file_path = os.path.join(self.docs_dir, path)
            if not os.path.exists(file_path):
                continue

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                has_issues = False
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
            print(f"  Found {total_issues} format issues")
            if self.auto_fix:
                print(f"  Auto-fixed {total_fixes} issues")
        else:
            print("  All files formatted correctly")

    def collect_files_to_process(self):
        """Collect all files to process"""
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
                                    self.path_to_anchor,
                                    self.recipe_numbers
                                ))
                        elif isinstance(path, list):
                            collect_nav_items(path)

        for section in self.nav_structure:
            if isinstance(section, dict):
                for section_name, items in section.items():
                    if section_name == "Home":
                        continue
                    if isinstance(items, list):
                        collect_nav_items(items)

        return files_to_process

    def merge_docs_files_parallel(self):
        """Merge all docs files in parallel"""
        if not self.nav_structure:
            self.load_navigation_structure()

        self.build_path_anchor_mapping()

        if self.validate:
            self.validate_and_fix_files()

        # Create base HTML
        full_html = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{self.project['name']}</title>
        </head>
        <body>
        """

        full_html += self.create_cover_page()
        full_html += self.create_table_of_contents()

        files_to_process = self.collect_files_to_process()
        print(f"\n  Processing {len(files_to_process)} files with {self.workers} workers...")

        # Parallel processing
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
                        print(f"    Progress: {completed}/{len(files_to_process)}")

        print(f"  Processed {len(results)} files")

        # Add results to HTML
        theme_color = self.project['theme_color']
        for section in self.nav_structure:
            if isinstance(section, dict):
                for section_name, items in section.items():
                    if section_name == "Home":
                        continue

                    full_html += f"""
                    <div class="chapter">
                        <h1 class="no-page-break">{section_name}</h1>
                    """

                    def add_results(nav_items, html_output, level=0):
                        for item in nav_items:
                            if isinstance(item, dict):
                                for title, path in item.items():
                                    if isinstance(path, str) and path in self.path_to_anchor:
                                        counter = int(self.path_to_anchor[path].split('-')[1])
                                        if counter in results:
                                            html_content, _ = results[counter]
                                            anchor_id = self.path_to_anchor[path]
                                            # Title from mkdocs.yml already contains recipe number (e.g., "R27: 验证码绕过技术")
                                            # So we don't need to add recipe_prefix here
                                            html_output.append(f"""
                                            <div class="section" id="{anchor_id}">
                                                <h2>{title}</h2>
                                                {html_content}
                                            </div>
                                            """)
                                    elif isinstance(path, list):
                                        # Add subsection header for nested categories
                                        html_output.append(f"""
                                        <div class="subsection-header" style="margin-top: 30pt; margin-bottom: 15pt; page-break-before: auto;">
                                            <h3 style="font-size: 16pt; color: {theme_color}; border-left: 4px solid {theme_color}; padding-left: 12pt; margin: 0;">{title}</h3>
                                        </div>
                                        """)
                                        add_results(path, html_output, level + 1)

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

    def _generate_learning_paths(self):
        """Generate recommended learning paths based on project type"""
        if self.project_key == "android":
            return """
                <ul style="font-size: 9.5pt; color: #444; line-height: 1.8; margin: 0; padding-left: 20pt;">
                    <li><strong>零基础入门</strong>：快速入门(Q) → 基础知识(F) → 工具指南(T) → 基础配方(R01-R15)</li>
                    <li><strong>安全研究员</strong>：反检测(R06-R11) → 脱壳技术(R12-R15) → 分析技术(R16-R23) → 案例分析(C)</li>
                    <li><strong>数据工程师</strong>：网络分析(R01-R05) → 自动化(R24-R31) → 工程实践(E) → 脚本集合(R32-R37)</li>
                    <li><strong>进阶开发者</strong>：工具内部原理(T02/T04/T06) → 进阶主题(A) → 真实案例(C)</li>
                </ul>
            """
        else:
            return """
                <ul style="font-size: 9.5pt; color: #444; line-height: 1.8; margin: 0; padding-left: 20pt;">
                    <li><strong>零基础入门</strong>：快速入门(Q) → 基础知识(F) → 工具指南(T) → 基础配方(R01-R07)</li>
                    <li><strong>安全研究员</strong>：高级配方(R08-R20) → 案例分析(C) → 问题排查(D)</li>
                    <li><strong>数据工程师</strong>：基础配方(R) → 工程实践(E) → 项目模板(P) → 脚本集合(S)</li>
                    <li><strong>前端开发者</strong>：基础知识(F) → 工具指南(T) → JS逆向(R08/R11) → 速查手册(H)</li>
                </ul>
            """

    def _generate_numbering_table(self):
        """Generate numbering system table based on project type"""
        if self.project_key == "android":
            # Android: Q, R, T, C, F, A, E, X
            return """
                <table style="width: 100%; font-size: 9pt; border-collapse: collapse; margin: 8pt 0;">
                    <tr style="background: #e8f4fd;">
                        <td style="padding: 6pt 10pt; border: 1px solid #bbdefb;"><strong>Q</strong> - 快速入门</td>
                        <td style="padding: 6pt 10pt; border: 1px solid #bbdefb;"><strong>R</strong> - 实战配方</td>
                        <td style="padding: 6pt 10pt; border: 1px solid #bbdefb;"><strong>T</strong> - 工具指南</td>
                    </tr>
                    <tr>
                        <td style="padding: 6pt 10pt; border: 1px solid #bbdefb;"><strong>C</strong> - 案例分析</td>
                        <td style="padding: 6pt 10pt; border: 1px solid #bbdefb;"><strong>F</strong> - 基础知识</td>
                        <td style="padding: 6pt 10pt; border: 1px solid #bbdefb;"><strong>A</strong> - 进阶主题</td>
                    </tr>
                    <tr style="background: #e8f4fd;">
                        <td style="padding: 6pt 10pt; border: 1px solid #bbdefb;"><strong>E</strong> - 工程实践</td>
                        <td style="padding: 6pt 10pt; border: 1px solid #bbdefb;"><strong>X</strong> - 附录资源</td>
                        <td style="padding: 6pt 10pt; border: 1px solid #bbdefb;"></td>
                    </tr>
                </table>
            """
        else:
            # Web: Q, F, T, R, C, E, S, H, P, D, X
            return """
                <table style="width: 100%; font-size: 9pt; border-collapse: collapse; margin: 8pt 0;">
                    <tr style="background: #e8f4fd;">
                        <td style="padding: 6pt 10pt; border: 1px solid #bbdefb;"><strong>Q</strong> - 快速入门</td>
                        <td style="padding: 6pt 10pt; border: 1px solid #bbdefb;"><strong>F</strong> - 基础知识</td>
                        <td style="padding: 6pt 10pt; border: 1px solid #bbdefb;"><strong>T</strong> - 工具指南</td>
                    </tr>
                    <tr>
                        <td style="padding: 6pt 10pt; border: 1px solid #bbdefb;"><strong>R</strong> - 实战配方</td>
                        <td style="padding: 6pt 10pt; border: 1px solid #bbdefb;"><strong>C</strong> - 案例分析</td>
                        <td style="padding: 6pt 10pt; border: 1px solid #bbdefb;"><strong>E</strong> - 工程实践</td>
                    </tr>
                    <tr style="background: #e8f4fd;">
                        <td style="padding: 6pt 10pt; border: 1px solid #bbdefb;"><strong>S</strong> - 脚本集合</td>
                        <td style="padding: 6pt 10pt; border: 1px solid #bbdefb;"><strong>H</strong> - 速查手册</td>
                        <td style="padding: 6pt 10pt; border: 1px solid #bbdefb;"><strong>P</strong> - 项目模板</td>
                    </tr>
                    <tr>
                        <td style="padding: 6pt 10pt; border: 1px solid #bbdefb;"><strong>D</strong> - 问题排查</td>
                        <td style="padding: 6pt 10pt; border: 1px solid #bbdefb;"><strong>X</strong> - 附录资源</td>
                        <td style="padding: 6pt 10pt; border: 1px solid #bbdefb;"></td>
                    </tr>
                </table>
            """

    def create_cover_page(self):
        """Create cover page"""
        topics_html = "".join([f"<p>{topic}</p>" for topic in self.project['topics']])
        theme_color = self.project['theme_color']

        return f"""
        <div class="cover-page">
            <div style="margin-top: 120pt;">
                <h1 style="font-size: 36pt; color: #1a1a1a; margin-bottom: 25pt; border: none; page-break-before: auto;" class="no-page-break">
                    {self.project['icon']} {self.project['name']}
                </h1>
                <h2 style="font-size: 18pt; color: #666; font-weight: 400; border: none; padding: 0;">
                    {self.project['subtitle']}
                </h2>
                <div style="margin-top: 60pt; font-size: 12pt; color: #888;">
                    {topics_html}
                </div>
            </div>
        </div>
        <div style="page-break-before: always; text-align: center; margin-top: 60pt;">
            <div style="font-size: 12pt; color: #aaa;">
                <p style="font-size: 40pt; margin-bottom: 15pt;">{self.project['icon']}</p>
                <p style="font-size: 14pt; color: #666; margin-bottom: 20pt;"><strong>Authors: +5/Gemini Pro 3.0/Claude Code Opus 4.5</strong></p>
                <p>Email: {self.author_email}</p>
                <p>WeChat: {self.author_wechat}</p>
                <p style="margin-top: 25pt;">📅 Created: {self.created_date}</p>
                <p>🔄 Last Revised: {self.revision_date}</p>
                <p>📌 Version: v2.0</p>
            </div>
            <div style="page-break-before: always;margin-top: 50pt; padding: 25pt 40pt; text-align: center;">
                <p style="font-size: 12pt; font-style: italic; color: #555; line-height: 1.8; margin-bottom: 8pt;">
                    "If the highest aim of a captain were to preserve his ship,<br/>
                    he would keep it in port forever."
                </p>
                <p style="font-size: 10pt; color: #888; margin-bottom: 30pt;">
                    — St. Thomas Aquinas, <em>Summa Theologica</em> (1265-1274)
                </p>
                <hr style="width: 50%; margin: 30pt auto; border: none; border-top: 1px solid #ddd;"/>
            </div>
            <div style="page-break-before: always; padding: 40pt 35pt; text-align: justify;">
                <p style="font-size: 11pt; color: #333; line-height: 2.0; margin-bottom: 25pt;">
                    The journey begins with the thrill of solving puzzles—that exhilarating rush when code finally yields its secrets. Yet seasoned reverse engineers walk a different path. They remain humble, ever-curious, and deeply reflective. In time, they all return to first principles: understanding how systems are <em>built</em> is the only true way to understand how they can be <em>unraveled</em>.
                </p>
                <p style="font-size: 11pt; color: #333; line-height: 2.0;">
                    初涉此道，多为破解之时的快意。而行至深处者，早已超越这份欣喜。他们怀谦卑之心，持求知之念，善于思考，最终都会回归技术的本质——唯有洞悉系统<strong>构建</strong>之道，方能参透其<strong>拆解</strong>之法。知己知彼，百战不殆。
                </p>
            </div>
            <div style="page-break-before: always;margin-top: 30pt; padding: 20pt 35pt; background-color: #fff8e1; border-radius: 8pt; border-left: 4px solid #ffa726; text-align: left;">
                <p style="font-size: 13pt; color: #e65100; font-weight: 600; margin-bottom: 15pt; text-align: center;">
                    写在前面
                </p>
                <p style="font-size: 10pt; color: #444; line-height: 1.9; text-align: justify; margin-bottom: 12pt;">
                    <strong>逆向工程</strong>，这门充满神秘色彩的技术艺术，一直是安全研究者、开发者和技术爱好者心中的"圣杯"。它不仅需要扎实的编程功底，更需要对系统底层的深刻理解，以及那份在迷宫中寻找出口的耐心与智慧。然而，市面上的逆向工程资料要么过于零散，要么晦涩难懂，让许多初学者望而却步。
                </p>
                <p style="font-size: 10pt; color: #444; line-height: 1.9; text-align: justify; margin-bottom: 12pt;">
                    本书的诞生，源于我近期阅读r0ysue的多本逆向书籍， 如《Frida Android SO逆向深入实践》，《unidbg逆向工程原理与实践》等之后的冲动，以及个人多年逆向实战中的朴素愿望：<em>将散落在各处的知识碎片，系统地串联成一条清晰的学习路径</em>。最初只是想整理平时的学习笔记，以便在旅途中、闲暇时刻享受离线阅读的乐趣。而当 AI 浪潮以不可阻挡之势席卷而来，我意识到这已不再是"要不要拥抱"的问题，而是"如何更好地拥抱"——为什么不借此机会，通过Vide Coding尝试一次真正意义上的<strong>人机协作</strong>呢？
                </p>
                <p style="font-size: 10pt; color: #444; line-height: 1.9; text-align: justify; margin-bottom: 12pt;">
                    有人说 AI 让知识变得"廉价"了，但我更愿意这样理解：<strong>AI 时代，知识不是更廉价，而是更易获取</strong>。真正稀缺的，从来不是信息本身，而是<em>将知识有效组织、精准表达、并转化为可执行智慧</em>的能力。当每个人都能轻松调用 AI 获取答案时，区分高手与新手的，恰恰是谁能把这些碎片化的知识串联成体系，谁能让它们在实战中真正发挥作用。这本手册，正是这一理念的实践。
                </p>
                <p style="font-size: 10pt; color: #444; line-height: 1.9; text-align: justify; margin-bottom: 12pt;">
                    于是，这本手册成为了一次独特的创作实验。在这个项目中，分工明确而高效：
                    <ul>
                    <li><strong>Claude Code Opus 4.5</strong> 化身"牛马程序员"，负责所有代码示例的编写与调试、大型代码库的深度理解与重构、架构流程图的创建、批量处理 Markdown 格式问题，以及自动化文档生成流程</li>
                    <li><strong>Gemini Pro 3.0</strong> 担当"科研老师傅"，负责海量技术知识点的调研、梳理与发散，从 arXiv 前沿论文到工业界实践资料的深度阅读与分析</li>
                    <li>而我则作为"Agent善后工程师"，结合自己的实战经验，负责全书的顶层架构设计、内容审核、版本管理、关键技术把关，以及疯狂地指挥Agent更合理地消耗token</li>
                    </ul>
                </p>
            </div>
            <div style="page-break-before: always;margin-top: 20pt; padding: 18pt 35pt; background-color: #f3e5f5; border-radius: 8pt; border-left: 4px solid #9c27b0; text-align: left;">
                <p style="font-size: 12pt; color: #6a1b9a; font-weight: 600; margin-bottom: 12pt; text-align: center;">
                    这本书适合谁？
                </p>
                <p style="font-size: 10pt; color: #444; line-height: 1.9; text-align: justify; margin-bottom: 10pt;">
                    无论你是<strong>安全研究员</strong>、<strong>渗透测试工程师</strong>、<strong>数据工程师</strong>，还是对底层技术充满好奇的<strong>开发者</strong>，本书都将为你提供从入门到进阶的完整路径。我们采用"<strong>配方式</strong>"的组织结构，每个章节都是一个独立的实战案例，你可以按需阅读，也可以系统学习。
                </p>
                <p style="font-size: 10pt; color: #444; line-height: 1.9; text-align: justify; margin-bottom: 12pt;">
                    书中涵盖了<strong>网络抓包</strong>、<strong>加密分析</strong>、<strong>反检测对抗</strong>、<strong>脱壳修复</strong>、<strong>动态分析</strong>等核心主题，并配有大量可直接运行的代码示例。我们的目标是：<em>让你读完每一个配方后，都能立即动手实践</em>。
                </p>
                <p style="font-size: 10pt; color: #6a1b9a; font-weight: 600; margin-bottom: 8pt;">📚 推荐学习路径：</p>
                {self._generate_learning_paths()}
            </div>
            <div style="page-break-before: always;margin-top: 25pt; padding: 18pt 35pt; background-color: #e3f2fd; border-radius: 8pt;">
                <p style="font-size: 11pt; color: #1565c0; font-weight: 600; margin-bottom: 12pt; text-align: center;">
                    分类编号系统
                </p>
                <p style="font-size: 10pt; color: #444; line-height: 1.8; text-align: justify; margin-bottom: 10pt;">
                    本手册采用<strong>分类编号系统</strong>，每个章节都有一个唯一标识符，便于快速检索和引用：
                </p>
                {self._generate_numbering_table()}
                <p style="font-size: 9pt; color: #666; line-height: 1.6; text-align: center; margin-top: 8pt;">
                    例如：<span style="background: #e8f5e9; padding: 2pt 6pt; border-radius: 3pt;">R01</span> 表示第一个实战配方，
                    <span style="background: #e8f5e9; padding: 2pt 6pt; border-radius: 3pt;">T05</span> 表示第五个工具指南
                </p>
            </div>
            <div style="page-break-before: always;margin-top: 25pt; padding: 18pt 35pt; background-color: #e8f5e9; border-radius: 8pt; border-left: 4px solid #4caf50;">
                <p style="font-size: 11pt; color: #2e7d32; font-weight: 600; margin-bottom: 12pt; text-align: center;">
                    📖 关于本版本
                </p>
                <p style="font-size: 10pt; color: #444; line-height: 1.8; text-align: justify; margin-bottom: 10pt;">
                    您正在阅读的是<strong>静态 PDF 版本</strong>，专为<strong>离线阅读</strong>和<strong>打印</strong>优化。内容定期更新，适合系统性学习和随时查阅。
                </p>
                <p style="font-size: 10pt; color: #444; line-height: 1.8; text-align: justify;">
                    我们正在构建<strong>动态交互版本</strong>，支持与 <strong>AI Agent / LLM</strong> 实时对话，可以针对具体问题获得定制化解答、代码示例生成、以及更深入的互动学习体验。敬请期待！
                </p>
            </div>
        </div>
        """

    def create_table_of_contents(self):
        """Create detailed table of contents with Recipe numbers"""
        theme_color = self.project['theme_color']

        # 章节标题中英文翻译映射
        section_translations = {
            # 主分类
            "Home": "首页",
            "Quick Start": "快速入门",
            "Recipes": "实战配方",
            "Tools": "工具指南",
            "Case Studies": "案例分析",
            "Reference": "参考资料",
            "Appendix": "附录",
            "Foundations": "基础知识",
            # Android 子分类
            "Network": "网络分析",
            "Anti-Detection": "反检测",
            "Unpacking": "脱壳技术",
            "Analysis": "分析技术",
            "Automation": "自动化",
            "Scripts": "脚本集合",
            "Dynamic": "动态分析工具",
            "Static": "静态分析工具",
            "Cheatsheets": "速查表",
            "Advanced": "进阶主题",
            "Engineering": "工程实践",
            "Data Analysis": "数据分析",
            "Data-Analysis": "数据分析",
            # Web 子分类
            "Basic": "基础配方",
            "Tooling": "工具箱",
            "Cheat Sheets": "速查手册",
            "Templates": "项目模板",
            "Troubleshooting": "问题排查",
            "Resources": "学习资源",
        }

        def translate_title(title):
            """翻译标题，保留编号前缀"""
            # 检查是否有编号前缀 (如 "R01: xxx" 或 "T05: xxx")
            if ': ' in title:
                prefix, rest = title.split(': ', 1)
                # 检查 rest 是否需要翻译
                translated = section_translations.get(rest, rest)
                return f"{prefix}: {translated}"
            return section_translations.get(title, title)

        toc_html = f"""
        <div class="toc-page" style="page-break-before: always;">
            <h1 class="toc-title no-page-break">目录</h1>
        """

        # Build TOC entries
        toc_entries = []

        def build_toc_entries(nav_items, level=0):
            entries = []
            for item in nav_items:
                if isinstance(item, dict):
                    for title, path in item.items():
                        if isinstance(path, str):
                            recipe_num = self.recipe_numbers.get(path, "")
                            entries.append({
                                'title': title,
                                'recipe': recipe_num,
                                'level': level,
                                'path': path
                            })
                        elif isinstance(path, list):
                            # Subsection
                            entries.append({
                                'title': title,
                                'recipe': '',
                                'level': level,
                                'is_section': True
                            })
                            entries.extend(build_toc_entries(path, level + 1))
            return entries

        for section in self.nav_structure:
            if isinstance(section, dict):
                for section_name, items in section.items():
                    if section_name == "Home":
                        continue
                    # Add main section
                    toc_entries.append({
                        'title': section_name,
                        'recipe': '',
                        'level': 0,
                        'is_part': True
                    })
                    if isinstance(items, list):
                        toc_entries.extend(build_toc_entries(items, 1))

        # Generate TOC HTML
        recipe_count = 0
        for entry in toc_entries:
            translated_title = translate_title(entry['title'])
            if entry.get('is_part'):
                toc_html += f"""
                <div class="toc-part">
                    <h2 style="color: #2c3e50; font-size: 14pt; margin-top: 18pt; margin-bottom: 8pt; border-left: 4px solid {theme_color}; padding-left: 10pt;">
                        {translated_title}
                    </h2>
                </div>
                """
            elif entry.get('is_section'):
                indent = entry['level'] * 12
                toc_html += f"""
                <div class="toc-section" style="margin-left: {indent}pt; margin-top: 6pt;">
                    <span style="font-weight: 600; color: #444; font-size: 10.5pt;">{translated_title}</span>
                </div>
                """
            else:
                indent = entry['level'] * 12
                if entry['recipe']:
                    recipe_count += 1
                    # 根据编号前缀选择不同颜色
                    prefix = entry['recipe'][0] if entry['recipe'] else ''
                    badge_colors = {
                        'Q': ('#fff3e0', '#e65100'),  # 橙色 - Quick Start
                        'R': ('#e8f5e9', '#2e7d32'),  # 绿色 - Recipes
                        'T': ('#e3f2fd', '#1565c0'),  # 蓝色 - Tools
                        'C': ('#fce4ec', '#c2185b'),  # 粉色 - Case Studies
                        'F': ('#f3e5f5', '#7b1fa2'),  # 紫色 - Foundations
                        'A': ('#ffebee', '#c62828'),  # 红色 - Advanced
                        'E': ('#e0f2f1', '#00695c'),  # 青色 - Engineering
                        'S': ('#fffde7', '#f9a825'),  # 黄色 - Scripts
                        'H': ('#eceff1', '#455a64'),  # 灰色 - Cheat Sheets
                        'P': ('#e8eaf6', '#3949ab'),  # 靛蓝 - Templates
                        'D': ('#fff8e1', '#ff8f00'),  # 琥珀 - Troubleshooting
                        'X': ('#efebe9', '#5d4037'),  # 棕色 - Appendix
                    }
                    bg_color, text_color = badge_colors.get(prefix, ('#e8f5e9', '#2e7d32'))
                    recipe_badge = f'<span style="background: {bg_color}; color: {text_color}; padding: 1pt 5pt; border-radius: 3pt; font-size: 8pt; font-weight: 600; margin-right: 6pt;">{entry["recipe"]}</span>'
                    # Strip recipe number prefix from title to avoid duplication (e.g., "R01: 标题" -> "标题")
                    display_title = re.sub(r'^[QRTCFAESHDPX]\d+:\s*', '', translated_title)
                else:
                    recipe_badge = ''
                    display_title = translated_title
                toc_html += f"""
                <div class="toc-entry" style="margin-left: {indent}pt; margin-top: 3pt; padding: 3pt 0;">
                    {recipe_badge}<span style="color: #555; font-size: 9.5pt;">{display_title}</span>
                </div>
                """

        toc_html += f"""
            <div style="margin-top: 25pt; text-align: center; color: #888; font-size: 10pt; border-top: 1px solid #ddd; padding-top: 15pt;">
                <p>章节总数: {recipe_count}</p>
            </div>
        </div>
        """

        return toc_html

    def create_css_styles(self):
        """Create PDF styles with Chinese font support"""
        theme_color = self.project['theme_color']

        css_content = f"""
        @font-face {{
            font-family: 'Chinese Sans';
            src: url('file:///System/Library/Fonts/Hiragino Sans GB.ttc') format('truetype'),
                 url('file:///System/Library/Fonts/STHeiti Light.ttc') format('truetype'),
                 url('file:///System/Library/Fonts/Supplemental/Songti.ttc') format('truetype'),
                 url('file:///Library/Fonts/Arial Unicode.ttf') format('truetype');
            font-weight: normal;
        }}

        @font-face {{
            font-family: 'Chinese Sans';
            src: url('file:///System/Library/Fonts/Hiragino Sans GB.ttc') format('truetype'),
                 url('file:///System/Library/Fonts/STHeiti Medium.ttc') format('truetype');
            font-weight: bold;
        }}

        @font-face {{
            font-family: 'Code Font';
            src: url('file:///System/Library/Fonts/Menlo.ttc') format('truetype'),
                 url('file:///System/Library/Fonts/Monaco.dfont') format('truetype');
        }}

        @page {{
            size: A4;
            margin: 2.5cm 2cm 3cm 2cm;

            @top-left {{
                content: "{self.project['short_name']}";
                font-family: 'Chinese Sans', sans-serif;
                font-size: 10pt;
                color: #666;
                border-bottom: 1px solid #e0e0e0;
                padding-bottom: 5pt;
            }}

            @top-right {{
                content: "Page " counter(page);
                font-family: 'Chinese Sans', sans-serif;
                font-size: 10pt;
                color: #666;
                border-bottom: 1px solid #e0e0e0;
                padding-bottom: 5pt;
            }}

            @bottom-center {{
                content: "{self.project['name']} v2.0";
                font-family: 'Chinese Sans', sans-serif;
                font-size: 9pt;
                color: #999;
                border-top: 1px solid #e0e0e0;
                padding-top: 5pt;
            }}
        }}

        body {{
            font-family: 'Chinese Sans', 'Noto Sans SC', 'Microsoft YaHei', sans-serif;
            font-size: 11pt;
            line-height: 1.8;
            color: #333;
            background: white;
        }}

        h1 {{
            font-family: 'Chinese Sans', sans-serif;
            font-size: 24pt;
            font-weight: 700;
            color: #1a1a1a;
            margin-top: 30pt;
            margin-bottom: 20pt;
            page-break-before: always;
            border-bottom: 3px solid {theme_color};
            padding-bottom: 10pt;
        }}

        h1.no-page-break {{ page-break-before: auto; }}

        h2 {{
            font-family: 'Chinese Sans', sans-serif;
            font-size: 18pt;
            font-weight: 600;
            color: #2c3e50;
            margin-top: 25pt;
            margin-bottom: 15pt;
            border-left: 4px solid {theme_color};
            padding-left: 15pt;
            page-break-after: avoid;
        }}

        h3 {{
            font-family: 'Chinese Sans', sans-serif;
            font-size: 14pt;
            font-weight: 500;
            color: #34495e;
            margin-top: 20pt;
            margin-bottom: 12pt;
            page-break-after: avoid;
        }}

        h4 {{
            font-family: 'Chinese Sans', sans-serif;
            font-size: 12pt;
            font-weight: 500;
            color: #555;
            margin-top: 15pt;
            margin-bottom: 10pt;
            page-break-after: avoid;
        }}

        p {{
            margin-bottom: 12pt;
            text-align: justify;
            orphans: 3;
            widows: 3;
        }}

        ul, ol {{
            margin-bottom: 12pt;
            padding-left: 25pt;
        }}

        li {{
            margin-bottom: 6pt;
            orphans: 2;
            widows: 2;
        }}

        code {{
            font-family: 'Code Font', 'Menlo', 'Monaco', 'Consolas', monospace;
            font-size: 9pt;
            background-color: #f8f9fa;
            padding: 2pt 4pt;
            border-radius: 3pt;
            border: 1px solid #e9ecef;
            word-wrap: break-word;
        }}

        pre {{
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
        }}

        pre code {{
            background: none;
            border: none;
            padding: 0;
            font-size: 8.5pt;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15pt 0;
            font-size: 10pt;
            page-break-inside: avoid;
        }}

        th, td {{
            border: 1px solid #ddd;
            padding: 8pt 12pt;
            text-align: left;
            word-wrap: break-word;
        }}

        th {{
            background-color: #f8f9fa;
            font-weight: 600;
            color: #495057;
        }}

        tr:nth-child(even) {{ background-color: #f8f9fa; }}

        blockquote {{
            border-left: 4px solid #6c757d;
            padding-left: 15pt;
            margin: 15pt 0;
            color: #6c757d;
            font-style: italic;
        }}

        a {{
            color: {theme_color};
            text-decoration: none;
            word-wrap: break-word;
        }}

        strong, b {{
            font-weight: 600;
            color: #2c3e50;
        }}

        em, i {{
            font-style: italic;
            color: #555;
        }}

        hr {{
            border: none;
            border-top: 2px solid #e9ecef;
            margin: 25pt 0;
        }}

        .cover-page {{ text-align: center; page-break-after: always; }}
        .toc-page {{ page-break-after: always; }}

        .toc-title {{
            font-size: 28pt;
            font-weight: 700;
            text-align: center;
            color: #1a1a1a;
            margin-bottom: 30pt;
            border-bottom: 3px solid {theme_color};
            padding-bottom: 15pt;
        }}

        .chapter {{ page-break-before: always; }}
        .section {{ margin-bottom: 30pt; page-break-before: always; }}
        .chapter .section:first-of-type {{ page-break-before: auto; }}

        @media print {{
            body {{
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
            }}
        }}
        """

        return CSS(string=css_content, font_config=self.font_config)

    def generate_pdf(self, output_filename=None):
        """Generate PDF file"""
        if output_filename is None:
            output_filename = self.project['output_file']

        print("\n" + "=" * 60)
        print(f"  {self.project['icon']} {self.project['name']}")
        print("=" * 60)
        print(f"  Workers: {self.workers}")
        print(f"  Cache: {'Enabled' if self.use_cache else 'Disabled'}")
        print(f"  Validation: {'Enabled' if self.validate else 'Disabled'}")
        print(f"  Auto-fix: {'Enabled' if self.auto_fix else 'Disabled'}")
        print("=" * 60)

        html_content = self.merge_docs_files_parallel()
        css_styles = self.create_css_styles()

        output_path = os.path.join(self.output_dir, output_filename)

        try:
            print("\n  Rendering PDF...")
            html_doc = HTML(string=html_content)
            html_doc.write_pdf(
                output_path,
                stylesheets=[css_styles],
                font_config=self.font_config
            )

            file_size_mb = os.path.getsize(output_path) / 1024 / 1024

            print(f"\n  PDF generated successfully!")
            print(f"  Output: {output_path}")
            print(f"  Size: {file_size_mb:.2f} MB")

            # Save debug HTML
            html_path = os.path.join(self.output_dir, f"{self.project_key}_debug.html")
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            print("\n" + "=" * 60)
            print("  Features included:")
            print("    - Recipe numbering (R01, R02, ...)")
            print("    - Detailed TOC with Recipe numbers")
            print("    - Parallel processing")
            print("    - Chinese font support")
            print("    - Internal PDF links")
            print("    - Smart caching")
            print("=" * 60)

            return output_path

        except Exception as e:
            print(f"\n  PDF generation failed: {e}")
            import traceback
            traceback.print_exc()
            return None


# ============================================================================
# Main Function
# ============================================================================

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Unified PDF Generator for Reverse Engineering Cookbooks',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s android                  # Generate Android PDF
  %(prog)s web                      # Generate Web PDF
  %(prog)s all                      # Generate both PDFs
  %(prog)s android -w 8             # Use 8 worker processes
  %(prog)s web --no-cache           # Disable cache
  %(prog)s all --fix-files          # Auto-fix format issues
        """
    )
    parser.add_argument('project', choices=['android', 'web', 'all'],
                       help='Project to generate PDF for')
    parser.add_argument('--output', '-o', type=str,
                       help='Output filename (default: project-specific name)')
    parser.add_argument('--no-cache', action='store_true',
                       help='Disable caching')
    parser.add_argument('--skip-validation', action='store_true',
                       help='Skip format validation')
    parser.add_argument('--fix-files', action='store_true',
                       help='Auto-fix format issues')
    parser.add_argument('--workers', '-w', type=int,
                       help='Number of parallel workers (default: CPU count)')

    args = parser.parse_args()

    print("=" * 60)
    print("  Reverse Engineering Cookbook - PDF Generator")
    print("=" * 60)
    print("  Features:")
    print("    - Recipe numbering (R01, R02, ...)")
    print("    - Detailed TOC with Recipe numbers")
    print("    - Parallel processing (2-4x speedup)")
    print("    - Chinese font support")
    print("    - Internal PDF links")
    print("    - Smart caching (10-20x regeneration speedup)")
    print("    - Unified output directory")
    print("=" * 60)

    # Check dependencies
    try:
        import mistune
        import weasyprint
        import yaml
        print("  Dependencies OK")
    except ImportError as e:
        print(f"  Missing dependency: {e}")
        print("  Run: pip install mistune weasyprint pillow pyyaml")
        return 1

    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    projects_to_generate = []
    if args.project == 'all':
        projects_to_generate = ['android', 'web']
    else:
        projects_to_generate = [args.project]

    success = True
    for project_key in projects_to_generate:
        try:
            converter = UnifiedPDFConverter(
                project_key=project_key,
                validate=not args.skip_validation,
                auto_fix=args.fix_files,
                use_cache=not args.no_cache,
                workers=args.workers
            )

            nav = converter.load_navigation_structure()
            if not nav:
                print(f"  No navigation found for {project_key}")
                success = False
                continue

            output_filename = args.output if args.output and len(projects_to_generate) == 1 else None
            result = converter.generate_pdf(output_filename)

            if not result:
                success = False

        except Exception as e:
            print(f"  Error generating {project_key} PDF: {e}")
            import traceback
            traceback.print_exc()
            success = False

    print("\n" + "=" * 60)
    if success:
        print("  All PDFs generated successfully!")
        print(f"  Output directory: {OUTPUT_DIR}")
    else:
        print("  Some PDFs failed to generate")
    print("=" * 60)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
