#!/usr/bin/env python3
"""
更新所有文档中的内部链接
"""
import os
import re
from pathlib import Path

# 定义路径映射
PATH_MAPPINGS = {
    # 简单的目录重命名
    '00-Foundations/': '01-Foundations/',
    '01-Tooling/': '02-Tooling/',
    '04-Engineering/': '06-Engineering/',
    '06-Scripts/': '07-Scripts/',
    '07-Others/': '11-Resources/',

    # 从02-Techniques移动到03-Basic-Recipes的文件
    '02-Techniques/re_workflow.md': '03-Basic-Recipes/re_workflow.md',
    '02-Techniques/debugging_techniques.md': '03-Basic-Recipes/debugging_techniques.md',
    '02-Techniques/hooking_techniques.md': '03-Basic-Recipes/hooking_techniques.md',
    '02-Techniques/api_reverse_engineering.md': '03-Basic-Recipes/api_reverse_engineering.md',
    '02-Techniques/crypto_identification.md': '03-Basic-Recipes/crypto_identification.md',
    '02-Techniques/dynamic_parameter_analysis.md': '03-Basic-Recipes/dynamic_parameter_analysis.md',
    '02-Techniques/websocket_reversing.md': '03-Basic-Recipes/websocket_reversing.md',

    # 从02-Techniques移动到04-Advanced-Recipes的文件
    '02-Techniques/javascript_deobfuscation.md': '04-Advanced-Recipes/javascript_deobfuscation.md',
    '02-Techniques/captcha_bypass.md': '04-Advanced-Recipes/captcha_bypass.md',
    '02-Techniques/browser_fingerprinting.md': '04-Advanced-Recipes/browser_fingerprinting.md',

    # 从03-Advanced-Topics移动到04-Advanced-Recipes的文件
    '03-Advanced-Topics/javascript_vm_protection.md': '04-Advanced-Recipes/javascript_vm_protection.md',
    '03-Advanced-Topics/webassembly_reversing.md': '04-Advanced-Recipes/webassembly_reversing.md',
    '03-Advanced-Topics/anti_scraping_deep_dive.md': '04-Advanced-Recipes/anti_scraping_deep_dive.md',
    '03-Advanced-Topics/frontend_hardening.md': '04-Advanced-Recipes/frontend_hardening.md',
    '03-Advanced-Topics/csp_bypass.md': '04-Advanced-Recipes/csp_bypass.md',
    '03-Advanced-Topics/webrtc_fingerprinting.md': '04-Advanced-Recipes/webrtc_fingerprinting.md',
    '03-Advanced-Topics/canvas_fingerprinting.md': '04-Advanced-Recipes/canvas_fingerprinting.md',
    '03-Advanced-Topics/tls_fingerprinting.md': '04-Advanced-Recipes/tls_fingerprinting.md',
    '03-Advanced-Topics/http2_http3.md': '04-Advanced-Recipes/http2_http3.md',
    '03-Advanced-Topics/pwa_service_worker.md': '04-Advanced-Recipes/pwa_service_worker.md',
}

def update_links_in_file(filepath):
    """更新单个文件中的所有链接"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    updated = False

    # 按照从具体到一般的顺序替换（先替换文件名，再替换目录）
    # 这样可以避免部分替换导致的问题
    for old_path, new_path in sorted(PATH_MAPPINGS.items(), key=lambda x: len(x[0]), reverse=True):
        if old_path in content:
            content = content.replace(old_path, new_path)
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
        if update_links_in_file(md_file):
            updated_files.append(str(md_file))

    print(f"✅ 更新完成！")
    print(f"📝 总共更新了 {len(updated_files)} 个文件")

    if updated_files:
        print("\n更新的文件列表:")
        for f in sorted(updated_files):
            print(f"  - {f}")

if __name__ == '__main__':
    main()
