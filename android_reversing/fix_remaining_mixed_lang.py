#!/usr/bin/env python3
"""
修复剩余的中英文混用错误
"""

import re
import sys
from pathlib import Path

# 定义需要修复的模式和替换
FIXES = [
    (r'# View所有符号\（Include未Export\）', '# 查看所有符号（包括未导出）'),
    (r'#### Shuffle优化', '#### Shuffle 优化'),
    (r'### Region详细结构', '### Region 详细结构'),
    (r'# 手动触发Minor Compaction  ', '# 手动触发 Minor Compaction  '),
    (r'# 也Can克隆 LSPosed\（更现代Implement\）', '# 也可以克隆 LSPosed（更现代实现）'),
    (r'# Check内容\（MustIsCompleteClassName，NoFileExtensionName\）', '# 检查内容（必须是完整类名，无文件扩展名）'),
    (r'./gradlew assembleDebug   # Debug版', './gradlew assembleDebug   # Debug 版'),
    (r'./gradlew assembleRelease # Release版', './gradlew assembleRelease # Release 版'),
    (r'# 重启Target App\（App更改\）', '# 重启目标 App（应用更改）'),
    (r"android_ids = \['id1', 'id2', 'id3', \.\.\.\]  # 采集Data", "android_ids = ['id1', 'id2', 'id3', ...]  # 采集数据"),
    (r'# Hamming距离', '# Hamming 距离'),
    (r'# 加权Calculate', '# 加权计算'),
    (r'stability \* 50 \* 0\.4 \+    # Stable性权重40%', 'stability * 50 * 0.4 +    # 稳定性权重40%'),
    (r'# Calculate新指纹', '# 计算新指纹'),
    (r'# True机应该显示:', '# 真机应该显示:'),
    (r'# isp: "China Mobile"  # True机更常见', '# isp: "China Mobile"  # 真机更常见'),
    (r'# Modify系统Property', '# 修改系统属性'),
    (r'# Install预设App', '# 安装预设 App'),
    (r'probabilities\.append\(prob\[1\]\)  # True实设备概率', 'probabilities.append(prob[1])  # 真实设备概率'),
    (r'# Use香农熵衡量多样性', '# 使用香农熵衡量多样性'),
    (r'# 综合Check', '# 综合检查'),
    (r'# Detection过于规律Op', '# 检测过于规律的操作'),
    (r'# Detection不自然Speed', '# 检测不自然的速度'),
    (r'# Get特征重要性排Name', '# 获取特征重要性排名'),
    (r'# 模拟外部FunctionAddress', '# 模拟外部函数地址'),
    (r'# 实际NeedCompleteDecode指令', '# 实际需要完整解码指令'),
    (r'# 从设备上拉取File \(以 arm64 为例\)', '# 从设备上拉取文件 (以 arm64 为例)'),
]

def fix_file(file_path: Path) -> bool:
    """修复单个文件"""
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content

        for pattern, replacement in FIXES:
            content = re.sub(pattern, replacement, content)

        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            print(f"✓ 修复: {file_path}")
            return True
        return False
    except Exception as e:
        print(f"✗ 错误 {file_path}: {e}")
        return False

def main():
    docs_dir = Path('docs')
    if not docs_dir.exists():
        print("错误: docs 目录不存在")
        sys.exit(1)

    md_files = list(docs_dir.rglob('*.md'))
    print(f"找到 {len(md_files)} 个 Markdown 文件")

    fixed_count = 0
    for md_file in md_files:
        if fix_file(md_file):
            fixed_count += 1

    print(f"\n完成！修复了 {fixed_count} 个文件")

if __name__ == '__main__':
    main()
