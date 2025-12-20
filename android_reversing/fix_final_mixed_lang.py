#!/usr/bin/env python3
"""
最终修复剩余的中英文混用错误
"""

import re
import sys
from pathlib import Path

# 定义需要修复的模式和替换
FIXES = [
    (r'AtNot标准Memory区域', '在非标准内存区域'),
    (r'隐藏Call栈', '隐藏调用栈'),
    (r'黑Name单模式', '黑名单模式'),
    (r'Detection相关ErrorLog', '检测相关错误日志'),
    (r'ViewModuleLog\（False设Module标签', '查看模块日志（假设模块标签'),
    (r'Case例', '案例'),
    (r'案例：金融App风控绕过', '案例：金融 App 风控绕过'),
    (r'某音乐App的加固分析', '某音乐 App 的加固分析'),
    (r'From设备池InGet未Use指纹', '从设备池中获取未使用的指纹'),
    (r'Database写', '数据库写'),
    (r'Reduce阶段', 'Reduce 阶段'),
    (r'Shuffle优化', 'Shuffle 优化'),
    (r'Region详细结构', 'Region 详细结构'),
    (r'If为 真', '如果为真'),
    (r'Is AtNot标准Memory', '是否在非标准内存'),
    (r'IfClassNameContains', '如果类名包含'),
    (r'False装File不存At', '伪装文件不存在'),
    (r'Hook Success', 'Hook 成功'),
    (r'IsNo有Detection', '是否有检测'),
    (r'No法Use', '无法使用'),
    (r'未Detection到', '未检测到'),
    (r'逐Enabled并Test', '逐个启用并测试'),
    (r'Must有This三', '必须有这三个'),
    (r'快速GetI/O', '快速获取I/O'),
    (r'ModifyReturnValue', '修改返回值'),
    (r'不In断Flow', '不中断流程'),
    (r'Only看Single点', '只看单点'),
    (r'简单Xor加密', '简单 Xor 加密'),
    (r'DetectionCode段Complete性', '检测代码段完整性'),
    (r'可读写Execute页面', '可读写执行页面'),
    (r'Start定When器Detection', '启动定时器检测'),
    (r'定期Detection系统CallTime', '定期检测系统调用时间'),
    (r'系统Call被InterceptorDebug', '系统调用被拦截或调试'),
    (r'根据Detection次数选择不同ResponseStrategy', '根据检测次数选择不同响应策略'),
    (r'固定Time戳', '固定时间戳'),
    (r'每次Call略微增加纳Second', '每次调用略微增加纳秒'),
    (r'AutoDetection并Bypass', '自动检测并绕过'),
    (r'Implement多Layer级Protected机制', '实现多层级保护机制'),
    (r'关KeyFunctionOnly有in/atAllDetection通过After才能正常Execute', '关键函数只有在所有检测通过后才能正常执行'),
    (r'各种Detection权重评分', '各种检测权重评分'),
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
