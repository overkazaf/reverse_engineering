#!/usr/bin/env python3
"""
改进的 Markdown 文档修复工具
- 对小文件使用 Gemini 完整修复
- 对大文件使用基于规则的修复，避免内容丢失
"""

import os
import json
import time
import re
import google.generativeai as genai
from typing import List, Dict, Tuple

# Gemini API 配置
API_KEY = "AIzaSyDjV8l0sZKvHRLmVw0Jtw4y4oJMD4FEcsE"
MODEL_NAME = "gemini-2.5-pro"

# 代理配置
HTTP_PROXY = "http://127.0.0.1:1087"
HTTPS_PROXY = "https://127.0.0.1:1087"

# 文件清单路径
MANIFEST_FILE = "markdown_fix_manifest.json"
DOCS_DIR = "docs"

# 重试配置
MAX_RETRIES = 3
RETRY_DELAY = 5
API_CALL_DELAY = 3

# 文件大小阈值（3KB）- 超过此大小的文件使用规则修复
SIZE_THRESHOLD = 3 * 1024

# 配置代理
os.environ['HTTP_PROXY'] = HTTP_PROXY
os.environ['HTTPS_PROXY'] = HTTPS_PROXY

genai.configure(api_key=API_KEY)

class ImprovedMarkdownFixer:
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

    def fix_with_rules(self, content: str) -> Tuple[str, List[str]]:
        """使用规则修复常见问题"""
        issues = []
        fixed_content = content

        # 1. 修复水平分割线
        if re.search(r'^\s*-\s*--\s*$', fixed_content, re.MULTILINE):
            fixed_content = re.sub(r'^\s*-\s*--\s*$', '---', fixed_content, flags=re.MULTILINE)
            issues.append("修复水平分割线格式 (- -- → ---)")

        # 2. 修复标题层级（# # → ##）
        if re.search(r'^#\s+#', fixed_content, re.MULTILINE):
            fixed_content = re.sub(r'^#\s+#', '##', fixed_content, flags=re.MULTILINE)
            issues.append("修复标题层级格式 (# # → ##)")

        # 3. 检查未闭合的代码块（不自动修复，以免破坏内容）
        code_blocks = re.findall(r'```', fixed_content)
        if len(code_blocks) % 2 != 0:
            issues.append(f"⚠️ 检测到未闭合的代码块（{len(code_blocks)} 个 ``` 标记）")

        # 4. 修复列表项前缀（☐ → -）
        if '☐' in fixed_content:
            fixed_content = fixed_content.replace('☐', '-')
            issues.append("修复列表项前缀 (☐ → -)")

        # 5. 修复连续多个空行
        if re.search(r'\n{4,}', fixed_content):
            fixed_content = re.sub(r'\n{4,}', '\n\n\n', fixed_content)
            issues.append("移除过多的连续空行")

        return fixed_content, issues

    def check_with_gemini_small_file(self, content: str, filepath: str) -> Tuple[bool, str, str]:
        """
        使用 Gemini 检查并修复小文件（< 3KB）
        """
        # 简化的提示词，强调返回完整文档
        prompt = f"""你是 Markdown 文档修复专家。

文件: {filepath}
大小: {len(content)} 字节

请检查并修复以下问题：
1. 代码块闭合（``` 成对）
2. 标题格式（## 不是 # #）
3. 水平线格式（--- 不是 - --）
4. 列表格式

**重要**: 你必须返回完整的修复后文档，不能省略任何内容！

如果格式正常，回答: "格式正常"
如果有问题，返回完整修复后的文档，格式如下：
```markdown
[完整的修复后文档内容]
```

文档内容:
---
{content}
---
"""

        for attempt in range(MAX_RETRIES):
            try:
                print(f"  尝试 Gemini API ({attempt + 1}/{MAX_RETRIES})...")
                response = self.model.generate_content(prompt)
                response_text = response.text

                # 检查是否格式正常
                if "格式正常" in response_text:
                    return True, "格式正常", ""

                # 提取修复后的内容
                md_start = response_text.find("```markdown")
                if md_start != -1:
                    md_start = response_text.find("\n", md_start) + 1
                    md_end = response_text.find("```", md_start)
                    if md_end != -1:
                        fixed_content = response_text[md_start:md_end].strip()

                        # 验证修复后的内容长度
                        if len(fixed_content) < len(content) * 0.8:
                            print(f"  ⚠️ Gemini 返回的内容太短 ({len(fixed_content)} vs {len(content)}), 使用规则修复")
                            return False, "Gemini 返回内容不完整", ""

                        return False, "Gemini 修复", fixed_content

                # 如果没有找到 markdown 块，使用规则修复
                return False, "无法解析 Gemini 响应", ""

            except Exception as e:
                print(f"  ❌ API 失败 ({attempt + 1}/{MAX_RETRIES}): {str(e)}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY * (attempt + 1))

        return False, "API 调用失败", ""

    def process_file(self, filepath: str) -> bool:
        """处理单个文件"""
        print(f"\n{'='*80}")
        print(f"📄 处理文件: {filepath}")
        print(f"{'='*80}")

        # 读取文件
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"❌ 读取失败: {e}")
            self.manifest["files"][filepath]["status"] = "error"
            self.manifest["files"][filepath]["issues"] = f"Read error: {str(e)}"
            self.save_manifest()
            return False

        file_size = len(content)
        print(f"📏 文件大小: {file_size:,} bytes")

        # 根据文件大小选择策略
        if file_size < SIZE_THRESHOLD:
            print("🤖 使用 Gemini API 修复（小文件）")
            is_valid, issues, fixed_content = self.check_with_gemini_small_file(content, filepath)
        else:
            print("📐 使用规则修复（大文件）")
            fixed_content, issue_list = self.fix_with_rules(content)
            is_valid = len(issue_list) == 0
            issues = "\n".join(issue_list) if issue_list else "格式正常"

        # 更新清单
        self.manifest["files"][filepath]["checked_at"] = time.strftime("%Y-%m-%d %H:%M:%S")

        if is_valid:
            print("✅ 格式正常")
            self.manifest["files"][filepath]["status"] = "valid"
            self.manifest["files"][filepath]["issues"] = issues
            self.save_manifest()
            return True

        elif fixed_content:
            # 验证修复后的内容
            if len(fixed_content) < len(content) * 0.7:
                print(f"⚠️ 修复后内容太短 ({len(fixed_content)} vs {len(content)}), 跳过")
                self.manifest["files"][filepath]["status"] = "needs_manual_fix"
                self.manifest["files"][filepath]["issues"] = "修复后内容不完整"
                self.save_manifest()
                return False

            print(f"🔧 应用修复...")
            print(f"  问题: {issues}")

            # 备份
            backup_path = filepath + ".backup"
            try:
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                # 写入修复内容
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)

                print(f"✅ 已修复 (备份: {backup_path})")
                print(f"  原始: {len(content):,} bytes → 修复: {len(fixed_content):,} bytes")

                self.manifest["files"][filepath]["status"] = "fixed"
                self.manifest["files"][filepath]["fixed_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                self.manifest["files"][filepath]["issues"] = issues
                self.save_manifest()
                return True

            except Exception as e:
                print(f"❌ 写入失败: {e}")
                self.manifest["files"][filepath]["status"] = "error"
                self.save_manifest()
                return False
        else:
            print("⚠️ 无法修复")
            self.manifest["files"][filepath]["status"] = "needs_manual_fix"
            self.manifest["files"][filepath]["issues"] = issues
            self.save_manifest()
            return False

    def run(self):
        """运行主流程"""
        print("🚀 改进的 Markdown 文档修复工具")
        print(f"  策略: 小文件(<{SIZE_THRESHOLD}B)用 Gemini，大文件用规则")
        print("="*80)

        # 扫描文件
        print("\n📂 扫描文件...")
        files = self.scan_markdown_files()
        print(f"找到 {len(files)} 个文件")

        # 更新清单
        self.update_manifest(files)

        # 统计
        total = len(files)
        pending = sum(1 for f in files if self.manifest["files"][f]["status"] == "pending")

        print(f"\n待处理: {pending} 个文件")

        # 处理文件
        for i, filepath in enumerate(files, 1):
            if self.manifest["files"][filepath]["status"] == "pending":
                print(f"\n📈 进度: {i}/{total} ({i*100//total}%)")
                self.process_file(filepath)

                time.sleep(API_CALL_DELAY)

        # 最终统计
        print("\n" + "="*80)
        print("🎉 处理完成！")
        print("="*80)

        stats = {}
        for f in files:
            status = self.manifest["files"][f]["status"]
            stats[status] = stats.get(status, 0) + 1

        print(f"\n✅ 格式正常: {stats.get('valid', 0)}")
        print(f"🔧 已修复: {stats.get('fixed', 0)}")
        print(f"⚠️  需手动: {stats.get('needs_manual_fix', 0)}")
        print(f"❌ 错误: {stats.get('error', 0)}")


def main():
    fixer = ImprovedMarkdownFixer()
    fixer.run()


if __name__ == "__main__":
    main()
