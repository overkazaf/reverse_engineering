#!/usr/bin/env python3
"""
Markdown 文档修复工具
使用 Gemini API 检查和修复 markdown 文档格式，为生成 PDF 做准备
"""

import os
import json
import time
import google.generativeai as genai
from pathlib import Path
from typing import List, Dict, Tuple
import sys
import httpx

# Gemini API 配置
API_KEY = os.environ.get("GEMINI_API_KEY", "")
MODEL_NAME = "gemini-2.5-pro"  # 使用 2.5 pro 的最新版本

# 代理配置 (可选，根据网络环境设置)
HTTP_PROXY = os.environ.get("HTTP_PROXY", "")
HTTPS_PROXY = os.environ.get("HTTPS_PROXY", "")

# 文件清单路径
MANIFEST_FILE = "markdown_fix_manifest.json"
DOCS_DIR = "docs"

# 重试配置
MAX_RETRIES = 3
RETRY_DELAY = 5  # 秒
API_CALL_DELAY = 3  # API 调用之间的延迟

# 配置代理和 Gemini API
os.environ['HTTP_PROXY'] = HTTP_PROXY
os.environ['HTTPS_PROXY'] = HTTPS_PROXY

genai.configure(
    api_key=API_KEY,
    transport='rest',
    client_options={
        'api_endpoint': 'https://generativelanguage.googleapis.com'
    }
)

class MarkdownFixer:
    def __init__(self):
        self.model = genai.GenerativeModel(MODEL_NAME)
        self.manifest = self.load_manifest()

    def load_manifest(self) -> Dict:
        """加载或创建文件清单"""
        if os.path.exists(MANIFEST_FILE):
            with open(MANIFEST_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"files": {}, "last_updated": time.strftime("%Y-%m-%d %H:%M:%S")}

    def save_manifest(self):
        """保存文件清单"""
        self.manifest["last_updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(MANIFEST_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.manifest, f, indent=2, ensure_ascii=False)

    def scan_markdown_files(self) -> List[str]:
        """扫描 docs 目录下的所有 md 文件"""
        md_files = []
        for root, dirs, files in os.walk(DOCS_DIR):
            for file in files:
                if file.endswith('.md'):
                    filepath = os.path.join(root, file)
                    md_files.append(filepath)
        return sorted(md_files)

    def update_manifest(self, files: List[str]):
        """更新文件清单"""
        for filepath in files:
            if filepath not in self.manifest["files"]:
                self.manifest["files"][filepath] = {
                    "status": "pending",
                    "checked_at": None,
                    "fixed_at": None,
                    "issues": None
                }
        self.save_manifest()

    def check_markdown_format(self, content: str, filepath: str) -> Tuple[bool, str, str]:
        """
        使用 Gemini API 检查 markdown 格式（带重试机制）
        返回: (is_valid, issues, fixed_content)
        """
        prompt = f"""你是一个专业的 Markdown 文档格式检查和修复专家。

这是一份关于 Android 逆向工程的技术文档，将会被合并到一个完整的 PDF cookbook 中。

文件路径: {filepath}

请检查以下 Markdown 文档的格式，重点关注：
1. 代码块是否正确闭合（```开始和结束）
2. 标题层级是否正确
3. 列表格式是否正确
4. 链接和图片引用是否正确
5. 表格格式是否完整
6. 中英文混排时是否有格式问题
7. 特殊字符是否正确转义
8. 代码块的语言标识是否正确（如 python, java, bash 等）

请按以下格式回答：

**格式状态**: [正常/异常]

**发现的问题**:
- 问题1描述
- 问题2描述
（如果格式正常，则写"无"）

**修复后的文档**:
```markdown
[如果有问题，在这里输出修复后的完整文档内容]
```

如果格式正常，修复后的文档部分输出"无需修复"。

---

待检查的文档内容：

{content}
"""

        for attempt in range(MAX_RETRIES):
            try:
                print(f"  尝试 API 调用 ({attempt + 1}/{MAX_RETRIES})...")
                response = self.model.generate_content(prompt)
                response_text = response.text

                # 解析响应
                is_valid = "格式状态**: 正常" in response_text or "格式状态: 正常" in response_text

                # 提取问题描述
                issues_start = response_text.find("**发现的问题**")
                issues_end = response_text.find("**修复后的文档**")
                issues = ""
                if issues_start != -1 and issues_end != -1:
                    issues = response_text[issues_start:issues_end].strip()

                # 提取修复后的内容
                fixed_content = ""
                if not is_valid:
                    # 查找 markdown 代码块
                    md_start = response_text.find("```markdown")
                    if md_start != -1:
                        md_start = response_text.find("\n", md_start) + 1
                        md_end = response_text.find("```", md_start)
                        if md_end != -1:
                            fixed_content = response_text[md_start:md_end].strip()

                return is_valid, issues, fixed_content

            except Exception as e:
                error_msg = str(e)
                print(f"  ❌ API 调用失败 (尝试 {attempt + 1}/{MAX_RETRIES}): {error_msg}")

                if attempt < MAX_RETRIES - 1:
                    wait_time = RETRY_DELAY * (attempt + 1)
                    print(f"  ⏳ 等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    print(f"  ❌ 达到最大重试次数，放弃处理")
                    return False, f"API Error after {MAX_RETRIES} retries: {error_msg}", ""

        return False, "Unknown error", ""

    def process_file(self, filepath: str) -> bool:
        """处理单个文件"""
        print(f"\n{'='*80}")
        print(f"📄 处理文件: {filepath}")
        print(f"{'='*80}")

        # 读取文件内容
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"❌ 读取文件失败: {str(e)}")
            self.manifest["files"][filepath]["status"] = "error"
            self.manifest["files"][filepath]["issues"] = f"Read error: {str(e)}"
            self.save_manifest()
            return False

        # 检查格式
        print("🔍 检查文档格式...")
        is_valid, issues, fixed_content = self.check_markdown_format(content, filepath)

        # 更新清单
        self.manifest["files"][filepath]["checked_at"] = time.strftime("%Y-%m-%d %H:%M:%S")

        if is_valid:
            print("✅ 格式正常，无需修复")
            self.manifest["files"][filepath]["status"] = "valid"
            self.manifest["files"][filepath]["issues"] = "无"
            self.save_manifest()
            return True
        else:
            print("⚠️  发现格式问题:")
            print(issues)

            if fixed_content:
                print("\n🔧 应用修复...")
                try:
                    # 备份原文件
                    backup_path = filepath + ".backup"
                    with open(backup_path, 'w', encoding='utf-8') as f:
                        f.write(content)

                    # 写入修复后的内容
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(fixed_content)

                    print(f"✅ 文件已修复（备份: {backup_path}）")
                    self.manifest["files"][filepath]["status"] = "fixed"
                    self.manifest["files"][filepath]["fixed_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                    self.manifest["files"][filepath]["issues"] = issues
                    self.save_manifest()
                    return True

                except Exception as e:
                    print(f"❌ 写入文件失败: {str(e)}")
                    self.manifest["files"][filepath]["status"] = "error"
                    self.manifest["files"][filepath]["issues"] = f"Write error: {str(e)}"
                    self.save_manifest()
                    return False
            else:
                print("❌ 无法自动修复")
                self.manifest["files"][filepath]["status"] = "needs_manual_fix"
                self.manifest["files"][filepath]["issues"] = issues
                self.save_manifest()
                return False

    def run(self):
        """运行主流程"""
        print("🚀 Markdown 文档修复工具")
        print("="*80)

        # 扫描文件
        print("\n📂 扫描 Markdown 文件...")
        files = self.scan_markdown_files()
        print(f"找到 {len(files)} 个文件")

        # 更新清单
        self.update_manifest(files)

        # 统计
        total = len(files)
        pending = sum(1 for f in files if self.manifest["files"][f]["status"] == "pending")
        valid = sum(1 for f in files if self.manifest["files"][f]["status"] == "valid")
        fixed = sum(1 for f in files if self.manifest["files"][f]["status"] == "fixed")
        error = sum(1 for f in files if self.manifest["files"][f]["status"] == "error")
        manual = sum(1 for f in files if self.manifest["files"][f]["status"] == "needs_manual_fix")

        print(f"\n📊 当前状态:")
        print(f"  总计: {total}")
        print(f"  待处理: {pending}")
        print(f"  格式正常: {valid}")
        print(f"  已修复: {fixed}")
        print(f"  需要手动修复: {manual}")
        print(f"  错误: {error}")

        # 处理文件
        processed = 0
        for i, filepath in enumerate(files, 1):
            if self.manifest["files"][filepath]["status"] in ["pending", "needs_manual_fix", "error"]:
                print(f"\n📈 进度: {i}/{total} ({i*100//total}%)")
                self.process_file(filepath)
                processed += 1

                # API 限流，避免过快请求
                print(f"⏳ 等待 {API_CALL_DELAY} 秒...")
                time.sleep(API_CALL_DELAY)

        # 最终统计
        print("\n" + "="*80)
        print("🎉 处理完成！")
        print("="*80)

        valid = sum(1 for f in files if self.manifest["files"][f]["status"] == "valid")
        fixed = sum(1 for f in files if self.manifest["files"][f]["status"] == "fixed")
        error = sum(1 for f in files if self.manifest["files"][f]["status"] == "error")
        manual = sum(1 for f in files if self.manifest["files"][f]["status"] == "needs_manual_fix")

        print(f"\n📊 最终统计:")
        print(f"  ✅ 格式正常: {valid}")
        print(f"  🔧 已修复: {fixed}")
        print(f"  ⚠️  需要手动修复: {manual}")
        print(f"  ❌ 错误: {error}")

        if manual > 0:
            print("\n⚠️  以下文件需要手动修复:")
            for filepath, info in self.manifest["files"].items():
                if info["status"] == "needs_manual_fix":
                    print(f"  - {filepath}")

        print(f"\n📄 详细清单已保存到: {MANIFEST_FILE}")
        print("\n下一步: 运行 PDF 生成脚本检查格式合法性")


def main():
    try:
        fixer = MarkdownFixer()
        fixer.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
