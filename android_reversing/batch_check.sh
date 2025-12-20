#!/bin/bash

echo "🔍 批量检查 Markdown 文件..."
echo "================================"
echo ""

files=(
    "docs/01-Recipes/Analysis/dynamic_analysis_deep_dive.md"
    "docs/01-Recipes/Analysis/js_obfuscator.md"
    "docs/01-Recipes/Analysis/js_vmp.md"
    "docs/01-Recipes/Analysis/native_string_obfuscation.md"
    "docs/01-Recipes/Analysis/ollvm_deobfuscation.md"
    "docs/01-Recipes/Analysis/re_workflow.md"
    "docs/01-Recipes/Analysis/static_analysis_deep_dive.md"
    "docs/01-Recipes/Analysis/vmp_analysis.md"
)

has_issues=()
no_issues=()

for file in "${files[@]}"; do
    result=$(python3 check_markdown_v2.py "$file" 2>&1)
    if echo "$result" | grep -q "✅ 未发现明显问题"; then
        no_issues+=("$file")
        echo "✅ $file"
    else
        has_issues+=("$file")
        echo "⚠️ $file"
        echo "$result" | grep "⚠️"
    fi
done

echo ""
echo "================================"
echo "📊 检查结果汇总"
echo "✅ 无问题: ${#no_issues[@]} 个"
echo "⚠️ 有问题: ${#has_issues[@]} 个"
