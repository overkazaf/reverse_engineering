# Markdown 文档格式检查与修复计划

**生成时间**: 2025-12-18
**总文件数**: 96
**当前进度**: 1/96 (1%)

---

## 📋 状态说明

- ⏳ **待检查** - 尚未开始
- 🔍 **检查中** - 正在分析
- ✅ **已完成** - 格式正确，无需修复
- ⚠️ **需修复** - 发现问题，需要修复
- ✔️ **已修复** - 问题已修复并确认

---

## 📂 文件清单

### 00-Quick-Start (2 files)

| 文件 | 状态 | 问题 | 备注 |
|------|------|------|------|
| docs/00-Quick-Start/index.md | ✔️ 已修复 | 标题跳级 | 添加二级标题'操作步骤' |
| docs/00-Quick-Start/setup.md | ✅ 已完成 | - | 格式正确 |

### 01-Recipes/Analysis (8 files)

| 文件 | 状态 | 问题 | 备注 |
|------|------|------|------|
| docs/01-Recipes/Analysis/dynamic_analysis_deep_dive.md | ✅ 已完成 | - | 格式正确 |
| docs/01-Recipes/Analysis/js_obfuscator.md | ✅ 已完成 | - | 格式正确 |
| docs/01-Recipes/Analysis/js_vmp.md | ✅ 已完成 | - | 格式正确 |
| docs/01-Recipes/Analysis/native_string_obfuscation.md | ✅ 已完成 | - | 格式正确 |
| docs/01-Recipes/Analysis/ollvm_deobfuscation.md | ✅ 已完成 | - | 格式正确 |
| docs/01-Recipes/Analysis/re_workflow.md | ✔️ 已修复 | 代码块+标题跳级 | 已修复主要问题 |
| docs/01-Recipes/Analysis/static_analysis_deep_dive.md | ✔️ 已修复 | 代码块+标题跳级 | 添加标题层级 |
| docs/01-Recipes/Analysis/vmp_analysis.md | ✅ 已完成 | - | 格式正确 |

### 01-Recipes/Anti-Detection (6 files)

| 文件 | 状态 | 问题 | 备注 |
|------|------|------|------|
| docs/01-Recipes/Anti-Detection/app_hardening_identification.md | ✅ 已完成 | - | 格式正确 |
| docs/01-Recipes/Anti-Detection/captcha_bypassing_techniques.md | ✅ 已完成 | - | 格式正确 |
| docs/01-Recipes/Anti-Detection/device_fingerprinting_and_bypass.md | ⚠️ 需修复 | 代码块和标题层级 | 部分修复，仍有3处标题跳级 |
| docs/01-Recipes/Anti-Detection/frida_anti_debugging.md | ✔️ 已修复 | 代码块未闭合 | 添加缺失的代码块标记 |
| docs/01-Recipes/Anti-Detection/mobile_app_sec_and_anti_bot.md | ✅ 已完成 | - | 格式正确 |
| docs/01-Recipes/Anti-Detection/xposed_anti_debugging.md | ✅ 已完成 | - | 格式正确 |

### 01-Recipes/Automation (8 files)

| 文件 | 状态 | 问题 | 备注 |
|------|------|------|------|
| docs/01-Recipes/Automation/automation_and_device_farming.md | ⏳ 待检查 | - | - |
| docs/01-Recipes/Automation/dial_up_proxy_pools.md | ✅ 已完成 | - | 格式正确 |
| docs/01-Recipes/Automation/docker_deployment.md | ✅ 已完成 | - | 格式正确 |
| docs/01-Recipes/Automation/proxy_pool_design.md | ✅ 已完成 | - | 格式正确 |
| docs/01-Recipes/Automation/scrapy.md | ⏳ 待检查 | - | - |
| docs/01-Recipes/Automation/scrapy_redis_distributed.md | ⏳ 待检查 | - | - |
| docs/01-Recipes/Automation/virtualization_and_containers.md | ⏳ 待检查 | - | - |
| docs/01-Recipes/Automation/web_anti_scraping.md | ⏳ 待检查 | - | - |

### 01-Recipes/Network (5 files)

| 文件 | 状态 | 问题 | 备注 |
|------|------|------|------|
| docs/01-Recipes/Network/crypto_analysis.md | ⏳ 待检查 | - | - |
| docs/01-Recipes/Network/ja3_fingerprinting.md | ⏳ 待检查 | - | - |
| docs/01-Recipes/Network/ja4_fingerprinting.md | ⏳ 待检查 | - | - |
| docs/01-Recipes/Network/network_sniffing.md | ⏳ 待检查 | - | - |
| docs/01-Recipes/Network/tls_fingerprinting_guide.md | ⏳ 待检查 | - | - |

### 01-Recipes/Scripts (6 files)

| 文件 | 状态 | 问题 | 备注 |
|------|------|------|------|
| docs/01-Recipes/Scripts/automation_scripts.md | ⏳ 待检查 | - | - |
| docs/01-Recipes/Scripts/c_for_emulation.md | ⏳ 待检查 | - | - |
| docs/01-Recipes/Scripts/frida_common_scripts.md | ⏳ 待检查 | - | - |
| docs/01-Recipes/Scripts/frida_script_examples.md | ⏳ 待检查 | - | - |
| docs/01-Recipes/Scripts/native_hooking.md | ⏳ 待检查 | - | - |
| docs/01-Recipes/Scripts/objection_snippets.md | ⏳ 待检查 | - | - |

### 01-Recipes/Unpacking (4 files)

| 文件 | 状态 | 问题 | 备注 |
|------|------|------|------|
| docs/01-Recipes/Unpacking/frida_unpacking_and_so_fixing.md | ⏳ 待检查 | - | - |
| docs/01-Recipes/Unpacking/so_obfuscation_deobfuscation.md | ⏳ 待检查 | - | - |
| docs/01-Recipes/Unpacking/so_string_deobfuscation.md | ⏳ 待检查 | - | - |
| docs/01-Recipes/Unpacking/un-packing.md | ⏳ 待检查 | - | - |

### 02-Tools (10 files)

| 文件 | 状态 | 问题 | 备注 |
|------|------|------|------|
| docs/02-Tools/Cheatsheets/adb_cheatsheet.md | ⏳ 待检查 | - | - |
| docs/02-Tools/Dynamic/frida_guide.md | ⏳ 待检查 | - | - |
| docs/02-Tools/Dynamic/frida_internals.md | ⏳ 待检查 | - | - |
| docs/02-Tools/Dynamic/unidbg_guide.md | ⏳ 待检查 | - | - |
| docs/02-Tools/Dynamic/unidbg_internals.md | ⏳ 待检查 | - | - |
| docs/02-Tools/Dynamic/xposed_guide.md | ⏳ 待检查 | - | - |
| docs/02-Tools/Dynamic/xposed_internals.md | ⏳ 待检查 | - | - |
| docs/02-Tools/Static/ghidra_guide.md | ⏳ 待检查 | - | - |
| docs/02-Tools/Static/ida_pro_guide.md | ⏳ 待检查 | - | - |
| docs/02-Tools/Static/radare2_guide.md | ⏳ 待检查 | - | - |

### 03-Case-Studies (8 files)

| 文件 | 状态 | 问题 | 备注 |
|------|------|------|------|
| docs/03-Case-Studies/case_anti_analysis_techniques.md | ⏳ 待检查 | - | - |
| docs/03-Case-Studies/case_flutter_apps.md | ⏳ 待检查 | - | - |
| docs/03-Case-Studies/case_malware_analysis.md | ⏳ 待检查 | - | - |
| docs/03-Case-Studies/case_music_apps.md | ⏳ 待检查 | - | - |
| docs/03-Case-Studies/case_social_media_and_anti_bot.md | ⏳ 待检查 | - | - |
| docs/03-Case-Studies/case_study_app_encryption.md | ⏳ 待检查 | - | - |
| docs/03-Case-Studies/case_unity_games.md | ⏳ 待检查 | - | - |
| docs/03-Case-Studies/case_video_apps_and_drm.md | ⏳ 待检查 | - | - |

### 04-Reference (29 files)

| 文件 | 状态 | 问题 | 备注 |
|------|------|------|------|
| docs/04-Reference/Advanced/android_sandbox_implementation.md | ⏳ 待检查 | - | - |
| docs/04-Reference/Advanced/aosp_and_system_customization.md | ⏳ 待检查 | - | - |
| docs/04-Reference/Advanced/aosp_device_modification.md | ⏳ 待检查 | - | - |
| docs/04-Reference/Advanced/minimal_android_rootfs.md | ⏳ 待检查 | - | - |
| docs/04-Reference/Advanced/so_anti_debugging_and_obfuscation.md | ⏳ 待检查 | - | - |
| docs/04-Reference/Advanced/so_runtime_emulation.md | ⏳ 待检查 | - | - |
| docs/04-Reference/Engineering/Data-Analysis/data_warehousing_and_processing.md | ⏳ 待检查 | - | - |
| docs/04-Reference/Engineering/Data-Analysis/flink.md | ⏳ 待检查 | - | - |
| docs/04-Reference/Engineering/Data-Analysis/hbase.md | ⏳ 待检查 | - | - |
| docs/04-Reference/Engineering/Data-Analysis/hive.md | ⏳ 待检查 | - | - |
| docs/04-Reference/Engineering/Data-Analysis/spark.md | ⏳ 待检查 | - | - |
| docs/04-Reference/Engineering/frameworks_and_middleware.md | ⏳ 待检查 | - | - |
| docs/04-Reference/Engineering/message_queues.md | ⏳ 待检查 | - | - |
| docs/04-Reference/Engineering/redis.md | ⏳ 待检查 | - | - |
| docs/04-Reference/Engineering/risk_control_sdk_build_guide.md | ⏳ 待检查 | - | - |
| docs/04-Reference/Foundations/android_components.md | ⏳ 待检查 | - | - |
| docs/04-Reference/Foundations/android_manifest.md | ⏳ 待检查 | - | - |
| docs/04-Reference/Foundations/android_studio_debug_tools.md | ⏳ 待检查 | - | - |
| docs/04-Reference/Foundations/apk_structure.md | ⏳ 待检查 | - | - |
| docs/04-Reference/Foundations/arm_assembly.md | ⏳ 待检查 | - | - |
| docs/04-Reference/Foundations/art_runtime.md | ⏳ 待检查 | - | - |
| docs/04-Reference/Foundations/dex_format.md | ⏳ 待检查 | - | - |
| docs/04-Reference/Foundations/smali_syntax.md | ⏳ 待检查 | - | - |
| docs/04-Reference/Foundations/so_elf_format.md | ⏳ 待检查 | - | - |
| docs/04-Reference/Foundations/x86_and_arm_assembly_basics.md | ⏳ 待检查 | - | - |

### 05-Appendix (4 files)

| 文件 | 状态 | 问题 | 备注 |
|------|------|------|------|
| docs/05-Appendix/ctf_platforms.md | ⏳ 待检查 | - | - |
| docs/05-Appendix/github_projects.md | ⏳ 待检查 | - | - |
| docs/05-Appendix/glossary.md | ⏳ 待检查 | - | - |
| docs/05-Appendix/learning_resources.md | ⏳ 待检查 | - | - |

### Other (6 files)

| 文件 | 状态 | 问题 | 备注 |
|------|------|------|------|
| docs/custom_theme/css/chat.css.md | ⏳ 待检查 | - | - |
| docs/custom_theme/css/cyberpunk-theme.css.md | ⏳ 待检查 | - | - |
| docs/custom_theme/js/chat.js.md | ⏳ 待检查 | - | - |
| docs/custom_theme/js/editor.js.md | ⏳ 待检查 | - | - |
| docs/custom_theme/js/interview.js.md | ⏳ 待检查 | - | - |
| docs/index.md | ⏳ 待检查 | - | - |

---

## 📊 统计信息

- **总计**: 96 个文件
- **待检查**: 72
- **检查中**: 0
- **已完成**: 14
- **需修复**: 0
- **已修复**: 4

---

## 🔧 修复记录

_此处记录每个文件的修复详情_

