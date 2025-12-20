#!/usr/bin/env python3
"""实时监控修复进度"""

import json
import os
import time
import sys

MANIFEST_FILE = "markdown_fix_manifest.json"

def clear_screen():
    os.system('clear' if os.name != 'nt' else 'cls')

def show_progress():
    while True:
        if not os.path.exists(MANIFEST_FILE):
            print("等待清单文件生成...")
            time.sleep(2)
            continue

        try:
            with open(MANIFEST_FILE, 'r', encoding='utf-8') as f:
                manifest = json.load(f)

            files = manifest.get('files', {})
            total = len(files)

            # 统计状态
            statuses = {}
            for filepath, info in files.items():
                status = info['status']
                statuses[status] = statuses.get(status, 0) + 1

            # 计算进度
            valid = statuses.get('valid', 0)
            fixed = statuses.get('fixed', 0)
            pending = statuses.get('pending', 0)
            needs_manual = statuses.get('needs_manual_fix', 0)
            error = statuses.get('error', 0)

            completed = valid + fixed
            progress = (completed * 100) // total if total > 0 else 0

            # 显示进度
            clear_screen()
            print("=" * 80)
            print("📊 Markdown 修复进度监控")
            print("=" * 80)
            print(f"\n上次更新: {manifest.get('last_updated', 'Unknown')}")
            print(f"\n总文件数: {total}")
            print(f"\n进度: {completed}/{total} ({progress}%)")
            print(f"\n{'█' * (progress // 2)}{' ' * (50 - progress // 2)} {progress}%")

            print(f"\n状态详情:")
            print(f"  ✅ 格式正常: {valid}")
            print(f"  🔧 已修复: {fixed}")
            print(f"  ⏳ 待处理: {pending}")
            print(f"  ⚠️  需要手动修复: {needs_manual}")
            print(f"  ❌ 错误: {error}")

            # 显示最近处理的文件
            recent_files = []
            for filepath, info in files.items():
                if info.get('checked_at'):
                    recent_files.append((filepath, info))

            recent_files.sort(key=lambda x: x[1].get('checked_at', ''), reverse=True)

            if recent_files:
                print(f"\n最近处理的文件 (最多显示 5 个):")
                for filepath, info in recent_files[:5]:
                    status_icon = {
                        'valid': '✅',
                        'fixed': '🔧',
                        'needs_manual_fix': '⚠️',
                        'error': '❌'
                    }.get(info['status'], '?')
                    print(f"  {status_icon} {filepath}")
                    print(f"     检查时间: {info.get('checked_at', 'Unknown')}")

            print("\n" + "=" * 80)
            print("按 Ctrl+C 退出监控")
            print("=" * 80)

            # 如果全部完成，退出
            if pending == 0:
                print("\n🎉 所有文件处理完成！")
                break

            time.sleep(5)

        except KeyboardInterrupt:
            print("\n\n监控已停止")
            sys.exit(0)
        except Exception as e:
            print(f"错误: {e}")
            time.sleep(5)

if __name__ == "__main__":
    show_progress()
