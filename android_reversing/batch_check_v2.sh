#!/bin/bash

echo "🔍 批量检查 Markdown 文件 (批次 2)..."
echo "================================"
echo ""

files=(
    "docs/01-Recipes/Anti-Detection/app_hardening_identification.md"
    "docs/01-Recipes/Anti-Detection/captcha_bypassing_techniques.md"
    "docs/01-Recipes/Anti-Detection/device_fingerprinting_and_bypass.md"
    "docs/01-Recipes/Anti-Detection/frida_anti_debugging.md"
    "docs/01-Recipes/Anti-Detection/mobile_app_sec_and_anti_bot.md"
    "docs/01-Recipes/Anti-Detection/xposed_anti_debugging.md"
)

has_issues=()
no_issues=()
results='['

for file in "${files[@]}"; do
    result=$(python3 check_markdown_v2.py "$file" 2>&1)
    if echo "$result" | grep -q "✅ 未发现明显问题"; then
        no_issues+=("$file")
        echo "✅ $file"
        results+="{\"file\":\"$file\",\"status\":\"ok\"},"
    else
        has_issues+=("$file")
        echo "⚠️ $file"
        echo "$result" | grep "⚠️" | head -3
        issue=$(echo "$result" | grep "⚠️" | head -1 | sed 's/⚠️ //')
        results+="{\"file\":\"$file\",\"status\":\"issue\",\"issue\":\"$issue\"},"
    fi
done

results="${results%,}]"

echo ""
echo "================================"
echo "📊 检查结果汇总"
echo "✅ 无问题: ${#no_issues[@]} 个"
echo "⚠️ 有问题: ${#has_issues[@]} 个"
echo ""

# 自动更新无问题的文件
if [ ${#no_issues[@]} -gt 0 ]; then
    update_json='['
    for file in "${no_issues[@]}"; do
        update_json+="[\"$file\", \"✅ 已完成\", \"-\", \"格式正确\"],"
    done
    update_json="${update_json%,}]"
    
    python3 batch_update_plan.py "$update_json"
fi
