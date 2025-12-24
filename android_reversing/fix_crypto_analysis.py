#!/usr/bin/env python3
"""
使用 Gemini API 修复 crypto_analysis.md
"""

import google.generativeai as genai
import os

# Gemini API 配置
API_KEY = os.environ.get("GEMINI_API_KEY", "")
MODEL_NAME = "gemini-2.5-pro"

# 代理配置 (可选，根据网络环境设置)
# 如需代理，请设置环境变量 HTTP_PROXY 和 HTTPS_PROXY

if not API_KEY:
    print("错误: 请设置 GEMINI_API_KEY 环境变量")
    exit(1)

genai.configure(api_key=API_KEY)

def fix_crypto_analysis():
    """修复 tls_fingerprinting_guide.md 文件"""

    file_path = "docs/01-Recipes/Network/tls_fingerprinting_guide.md"

    print("📄 读取文件...")
    with open(file_path, 'r', encoding='utf-8') as f:
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
        if len(fixed_content) < len(content) * 0.8:
            print(f"\n⚠️  警告：修复后内容比原文件短 {100 - (len(fixed_content)*100//len(content))}%")
            print("这可能表示内容丢失，建议检查。")

            response = input("\n是否继续保存？(y/n): ")
            if response.lower() != 'y':
                print("❌ 已取消保存")
                return False

        # 备份原文件
        backup_path = file_path + ".gemini_backup"
        print(f"\n💾 备份原文件到: {backup_path}")
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)

        # 保存修复后的文件
        print(f"💾 保存修复后的文件...")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)

        print(f"\n✅ 修复完成!")
        print(f"📄 文件: {file_path}")
        print(f"📋 备份: {backup_path}")

        # 显示修复摘要
        print(f"\n📊 修复摘要:")
        print(f"   原文件: {len(content):,} 字节")
        print(f"   新文件: {len(fixed_content):,} 字节")
        print(f"   变化: {len(fixed_content) - len(content):+,} 字节 ({((len(fixed_content) - len(content))*100/len(content)):+.1f}%)")

        return True

    except Exception as e:
        print(f"\n❌ API 调用失败: {e}")
        return False

if __name__ == "__main__":
    print("="*70)
    print("🔧 TLS Fingerprinting Guide Markdown 修复工具 (Gemini API)")
    print("="*70)

    success = fix_crypto_analysis()

    print("\n" + "="*70)
    if success:
        print("🎉 修复成功！")
        print("\n下一步:")
        print("1. 检查修复后的文件:")
        print("   code docs/01-Recipes/Network/tls_fingerprinting_guide.md")
        print("\n2. 对比原文件和修复后文件:")
        print("   diff docs/01-Recipes/Network/tls_fingerprinting_guide.md.gemini_backup docs/01-Recipes/Network/tls_fingerprinting_guide.md")
        print("\n3. 如果满意，重新生成 PDF:")
        print("   python3 docs_to_pdf_final.py --no-cache")
    else:
        print("❌ 修复失败")
    print("="*70)
