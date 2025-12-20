#!/usr/bin/env python3
"""
通用的 Gemini API Markdown 修复工具
支持指定输入文件和输出文件
"""

import google.generativeai as genai
import os
import sys
import argparse

# Gemini API 配置
API_KEY = "AIzaSyDjV8l0sZKvHRLmVw0Jtw4y4oJMD4FEcsE"
MODEL_NAME = "gemini-2.5-pro"

# 代理配置
HTTP_PROXY = "http://127.0.0.1:1087"
HTTPS_PROXY = "https://127.0.0.1:1087"

os.environ['HTTP_PROXY'] = HTTP_PROXY
os.environ['HTTPS_PROXY'] = HTTPS_PROXY

genai.configure(api_key=API_KEY)

def fix_markdown_file(input_file, output_file=None, backup=True):
    """
    修复 Markdown 文件

    Args:
        input_file: 输入文件路径
        output_file: 输出文件路径（如果为None，则覆盖原文件）
        backup: 是否备份原文件

    Returns:
        bool: 是否成功
    """

    if not os.path.exists(input_file):
        print(f"❌ 文件不存在: {input_file}")
        return False

    print(f"📄 读取文件: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    print(f"📏 原文件大小: {len(content)} 字节")

    # 创建简化的提示词
    prompt = f"""修复以下 Markdown 文档的格式问题：
1. `# #` → `##`
2. `- --` → `---`
3. `☐` → `-`
4. 修复代码块闭合
5. 保持所有内容不变

直接返回修复后的文档：

{content}
"""

    print("\n🤖 调用 Gemini API 修复文档...")
    print("⏳ 这可能需要 30-60 秒...\n")

    model = genai.GenerativeModel(MODEL_NAME)

    try:
        response = model.generate_content(prompt)
        fixed_content = response.text

        # 移除可能的 markdown 代码块标记
        if fixed_content.startswith("```markdown"):
            fixed_content = fixed_content[len("```markdown"):].strip()
        if fixed_content.endswith("```"):
            fixed_content = fixed_content[:-3].strip()

        print(f"✅ Gemini API 返回成功")
        print(f"📏 修复后大小: {len(fixed_content)} 字节")

        # 验证内容长度（防止内容丢失）
        if len(fixed_content) < len(content) * 0.7:
            print(f"\n⚠️  警告：修复后内容比原文件短 {100 - (len(fixed_content)*100//len(content))}%")
            print("这可能表示内容丢失，建议检查。")

            response = input("\n是否继续保存？(y/n): ")
            if response.lower() != 'y':
                print("❌ 已取消保存")
                return False

        # 决定输出文件路径
        if output_file is None:
            output_file = input_file

        # 备份原文件
        if backup and output_file == input_file:
            backup_path = input_file + ".gemini_backup"
            print(f"\n💾 备份原文件到: {backup_path}")
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)

        # 保存修复后的文件
        print(f"💾 保存修复后的文件: {output_file}")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(fixed_content)

        print(f"\n✅ 修复完成!")

        # 显示修复摘要
        print(f"\n📊 修复摘要:")
        print(f"   原文件: {len(content):,} 字节")
        print(f"   新文件: {len(fixed_content):,} 字节")
        print(f"   变化: {len(fixed_content) - len(content):+,} 字节 ({((len(fixed_content) - len(content))*100/len(content)):+.1f}%)")

        if backup and output_file == input_file:
            print(f"\n📋 备份: {backup_path}")

        return True

    except Exception as e:
        print(f"\n❌ API 调用失败: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description='使用 Gemini API 修复 Markdown 文件格式',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 修复文件（覆盖原文件，自动备份）
  python3 fix_md_with_gemini_single.py input.md

  # 修复文件并保存到新文件
  python3 fix_md_with_gemini_single.py input.md -o output.md

  # 修复文件，不备份
  python3 fix_md_with_gemini_single.py input.md --no-backup
        """
    )

    parser.add_argument('input', help='输入的 Markdown 文件路径')
    parser.add_argument('-o', '--output', help='输出文件路径（默认覆盖原文件）')
    parser.add_argument('--no-backup', action='store_true', help='不备份原文件')

    args = parser.parse_args()

    print("="*70)
    print("🔧 Gemini API Markdown 修复工具")
    print("="*70)

    success = fix_markdown_file(
        args.input,
        args.output,
        backup=not args.no_backup
    )

    print("\n" + "="*70)
    if success:
        print("🎉 修复成功！")
        if args.output:
            print(f"\n输出文件: {args.output}")
        else:
            print(f"\n文件已更新: {args.input}")
            if not args.no_backup:
                print(f"备份文件: {args.input}.gemini_backup")
    else:
        print("❌ 修复失败")
    print("="*70)

if __name__ == "__main__":
    main()
