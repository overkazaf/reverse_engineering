#!/bin/bash

files=(
    "docs/01-Recipes/Automation/automation_and_device_farming.md"
    "docs/01-Recipes/Automation/dial_up_proxy_pools.md"
    "docs/01-Recipes/Automation/docker_deployment.md"
    "docs/01-Recipes/Automation/proxy_pool_design.md"
)

for file in "${files[@]}"; do
    result=$(python3 check_markdown_v2.py "$file" 2>&1)
    if echo "$result" | grep -q "✅ 未发现明显问题"; then
        echo "✅ $file"
        python3 update_plan.py "$file" "✅ 已完成" "-" "格式正确"
    else
        echo "⚠️ $file"
        echo "$result" | grep "⚠️" | head -3
    fi
done
