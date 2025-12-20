# 目录重构方案 - Cookbook 风格

## 设计理念

将现有的**教程式结构**重组为**Cookbook 式结构**：
- ✅ 实战优先：Recipes 放在最前面
- ✅ 场景导向：按解决的问题分类，而非知识类型
- ✅ 快速查找：工具和参考资料单独组织
- ✅ 渐进学习：从实战到理论的路径

---

## 新目录结构

```
docs/
├── index.md                                    # 主页
│
├── 00-Quick-Start/                             # 🏁 快速开始（新增）
│   └── (待后续补充首次使用指南)
│
├── 01-Recipes/                                 # 🎯 核心：实战菜谱
│   ├── Authentication/                         # 认证与授权
│   │   └── (暂无，待后续补充)
│   ├── Network/                                # 网络与加密
│   │   ├── network_sniffing.md                # 从 02-Techniques
│   │   ├── crypto_analysis.md                 # 从 02-Techniques
│   │   ├── tls_fingerprinting_guide.md        # 从 02-Techniques
│   │   ├── ja3_fingerprinting.md              # 从 02-Techniques
│   │   └── ja4_fingerprinting.md              # 从 02-Techniques
│   ├── Anti-Detection/                         # 反检测与对抗
│   │   ├── frida_anti_debugging.md            # 从 02-Techniques
│   │   ├── xposed_anti_debugging.md           # 从 02-Techniques
│   │   ├── captcha_bypassing_techniques.md    # 从 02-Techniques
│   │   ├── app_hardening_identification.md    # 从 02-Techniques
│   │   ├── device_fingerprinting_and_bypass.md # 从 03-Advanced-Topics
│   │   └── mobile_app_sec_and_anti_bot.md     # 从 03-Advanced-Topics
│   ├── Unpacking/                              # 脱壳与修复
│   │   ├── un-packing.md                      # 从 02-Techniques
│   │   ├── frida_unpacking_and_so_fixing.md   # 从 02-Techniques
│   │   ├── so_obfuscation_deobfuscation.md    # 从 02-Techniques
│   │   └── so_string_deobfuscation.md         # 从 02-Techniques
│   ├── Analysis/                               # 分析与调试
│   │   ├── re_workflow.md                     # 从 02-Techniques
│   │   ├── static_analysis_deep_dive.md       # 从 02-Techniques
│   │   ├── dynamic_analysis_deep_dive.md      # 从 02-Techniques
│   │   ├── ollvm_deobfuscation.md             # 从 03-Advanced-Topics
│   │   ├── vmp_analysis.md                    # 从 03-Advanced-Topics
│   │   ├── js_obfuscator.md                   # 从 03-Advanced-Topics
│   │   ├── js_vmp.md                          # 从 03-Advanced-Topics
│   │   └── native_string_obfuscation.md       # 从 03-Advanced-Topics
│   ├── Automation/                             # 自动化与规模化
│   │   ├── automation_and_device_farming.md   # 从 04-Engineering
│   │   ├── dial_up_proxy_pools.md             # 从 02-Techniques
│   │   ├── proxy_pool_design.md               # 从 04-Engineering
│   │   ├── scrapy.md                          # 从 04-Engineering
│   │   ├── scrapy_redis_distributed.md        # 从 04-Engineering
│   │   ├── docker_deployment.md               # 从 04-Engineering
│   │   ├── virtualization_and_containers.md   # 从 04-Engineering
│   │   └── web_anti_scraping.md               # 从 03-Advanced-Topics
│   └── Scripts/                                # 即用脚本
│       ├── frida_script_examples.md           # 从 02-Techniques
│       ├── frida_common_scripts.md            # 从 07-Scripts
│       ├── automation_scripts.md              # 从 07-Scripts
│       ├── native_hooking.md                  # 从 07-Scripts
│       ├── objection_snippets.md              # 从 07-Scripts
│       └── c_for_emulation.md                 # 从 07-Scripts
│
├── 02-Tools/                                   # 🔨 工具指南
│   ├── Dynamic/                                # 动态分析工具
│   │   ├── frida_guide.md                     # 从 01-Tooling
│   │   ├── frida_internals.md                 # 从 01-Tooling
│   │   ├── xposed_guide.md                    # 从 01-Tooling
│   │   ├── xposed_internals.md                # 从 01-Tooling
│   │   ├── unidbg_guide.md                    # 从 01-Tooling
│   │   └── unidbg_internals.md                # 从 01-Tooling
│   ├── Static/                                 # 静态分析工具
│   │   ├── ghidra_guide.md                    # 从 01-Tooling
│   │   ├── ida_pro_guide.md                   # 从 01-Tooling
│   │   └── radare2_guide.md                   # 从 01-Tooling
│   └── Cheatsheets/                            # 速查表
│       └── adb_cheatsheet.md                  # 从 01-Tooling
│
├── 03-Case-Studies/                            # 📚 案例研究（保持不变）
│   ├── case_anti_analysis_techniques.md
│   ├── case_music_apps.md
│   ├── case_social_media_and_anti_bot.md
│   ├── case_study_app_encryption.md
│   ├── case_video_apps_and_drm.md
│   ├── case_unity_games.md
│   ├── case_flutter_apps.md
│   └── case_malware_analysis.md
│
├── 04-Reference/                               # 📖 参考资料
│   ├── Foundations/                            # 基础知识
│   │   ├── apk_structure.md                   # 从 00-Foundations
│   │   ├── android_components.md              # 从 00-Foundations
│   │   ├── android_manifest.md                # 从 00-Foundations
│   │   ├── android_studio_debug_tools.md      # 从 00-Foundations
│   │   ├── dex_format.md                      # 从 00-Foundations
│   │   ├── smali_syntax.md                    # 从 00-Foundations
│   │   ├── so_elf_format.md                   # 从 00-Foundations
│   │   ├── art_runtime.md                     # 从 00-Foundations
│   │   ├── arm_assembly.md                    # 从 00-Foundations
│   │   └── x86_and_arm_assembly_basics.md     # 从 00-Foundations
│   ├── Advanced/                               # 高级主题
│   │   ├── android_sandbox_implementation.md  # 从 03-Advanced-Topics
│   │   ├── aosp_and_system_customization.md   # 从 03-Advanced-Topics
│   │   ├── aosp_device_modification.md        # 从 03-Advanced-Topics
│   │   ├── minimal_android_rootfs.md          # 从 03-Advanced-Topics
│   │   ├── so_anti_debugging_and_obfuscation.md # 从 03-Advanced-Topics
│   │   └── so_runtime_emulation.md            # 从 03-Advanced-Topics
│   └── Engineering/                            # 工程化理论
│       ├── frameworks_and_middleware.md       # 从 04-Engineering
│       ├── message_queues.md                  # 从 04-Engineering
│       ├── redis.md                           # 从 04-Engineering
│       ├── risk_control_sdk_build_guide.md    # 从 04-Engineering
│       └── Data-Analysis/                      # 大数据分析
│           ├── data_warehousing_and_processing.md # 从 06-Data-Analysis
│           ├── flink.md                       # 从 06-Data-Analysis
│           ├── hbase.md                       # 从 06-Data-Analysis
│           ├── hive.md                        # 从 06-Data-Analysis
│           └── spark.md                       # 从 06-Data-Analysis
│
└── 05-Appendix/                                # 📎 附录
    ├── github_projects.md                      # 从 08-Others
    ├── learning_resources.md                   # 从 08-Others
    ├── ctf_platforms.md                        # 从 08-Others
    └── glossary.md                             # 从 08-Others
```

---

## 文件移动映射表

### 从 00-Foundations → 04-Reference/Foundations
- apk_structure.md
- android_components.md
- android_manifest.md
- android_studio_debug_tools.md
- dex_format.md
- smali_syntax.md
- so_elf_format.md
- art_runtime.md
- arm_assembly.md
- x86_and_arm_assembly_basics.md

### 从 01-Tooling → 02-Tools
- **→ Dynamic/**:
  - frida_guide.md
  - frida_internals.md
  - xposed_guide.md
  - xposed_internals.md
  - unidbg_guide.md
  - unidbg_internals.md
- **→ Static/**:
  - ghidra_guide.md
  - ida_pro_guide.md
  - radare2_guide.md
- **→ Cheatsheets/**:
  - adb_cheatsheet.md

### 从 02-Techniques → 01-Recipes
- **→ Network/**:
  - network_sniffing.md
  - crypto_analysis.md
  - tls_fingerprinting_guide.md
  - ja3_fingerprinting.md
  - ja4_fingerprinting.md
- **→ Anti-Detection/**:
  - frida_anti_debugging.md
  - xposed_anti_debugging.md
  - captcha_bypassing_techniques.md
  - app_hardening_identification.md
- **→ Unpacking/**:
  - un-packing.md
  - frida_unpacking_and_so_fixing.md
  - so_obfuscation_deobfuscation.md
  - so_string_deobfuscation.md
- **→ Analysis/**:
  - re_workflow.md
  - static_analysis_deep_dive.md
  - dynamic_analysis_deep_dive.md
- **→ Scripts/**:
  - frida_script_examples.md
- **→ Automation/**:
  - dial_up_proxy_pools.md

### 从 03-Advanced-Topics 分流
- **→ 01-Recipes/Anti-Detection/**:
  - device_fingerprinting_and_bypass.md
  - mobile_app_sec_and_anti_bot.md
- **→ 01-Recipes/Analysis/**:
  - ollvm_deobfuscation.md
  - vmp_analysis.md
  - js_obfuscator.md
  - js_vmp.md
  - native_string_obfuscation.md
- **→ 01-Recipes/Automation/**:
  - web_anti_scraping.md
- **→ 04-Reference/Advanced/**:
  - android_sandbox_implementation.md
  - aosp_and_system_customization.md
  - aosp_device_modification.md
  - minimal_android_rootfs.md
  - so_anti_debugging_and_obfuscation.md
  - so_runtime_emulation.md

### 从 04-Engineering 分流
- **→ 01-Recipes/Automation/**:
  - automation_and_device_farming.md
  - proxy_pool_design.md
  - scrapy.md
  - scrapy_redis_distributed.md
  - docker_deployment.md
  - virtualization_and_containers.md
- **→ 04-Reference/Engineering/**:
  - frameworks_and_middleware.md
  - message_queues.md
  - redis.md
  - risk_control_sdk_build_guide.md

### 从 05-Case-Studies → 03-Case-Studies (保持不变)
- 所有文件原位保留

### 从 06-Data-Analysis → 04-Reference/Engineering/Data-Analysis
- data_warehousing_and_processing.md
- flink.md
- hbase.md
- hive.md
- spark.md

### 从 07-Scripts → 01-Recipes/Scripts
- frida_common_scripts.md
- automation_scripts.md
- native_hooking.md
- objection_snippets.md
- c_for_emulation.md

### 从 08-Others → 05-Appendix
- github_projects.md
- learning_resources.md
- ctf_platforms.md
- glossary.md

---

## 变更理由

### 1. 实战优先 (Recipes First)
- **之前**: Foundations → Tooling → Techniques
- **现在**: Recipes → Tools → Reference
- **原因**: Cookbook 强调快速解决问题，理论知识作为参考资料后置

### 2. 场景分类 (Scenario-Based)
- **之前**: 按知识类型（Techniques, Advanced Topics, Engineering）
- **现在**: 按问题场景（Network, Anti-Detection, Unpacking...）
- **原因**: 用户通常以"我想做什么"而非"我想学什么"来查找

### 3. 合并脚本 (Unified Scripts)
- **之前**: 分散在 02-Techniques 和 07-Scripts
- **现在**: 统一放在 01-Recipes/Scripts
- **原因**: 所有即用脚本集中管理，更符合 Cookbook 理念

### 4. 工具独立 (Tools Separation)
- **之前**: Tooling 混合了 Guide 和 Internals
- **现在**: 按工具类型（Dynamic/Static）+ Cheatsheets 分类
- **原因**: 更清晰的工具索引，快速查找速查表

### 5. 理论后置 (Reference as Support)
- **之前**: Foundations 在最前面
- **现在**: Reference 在后面
- **原因**: Cookbook 用户优先查找解决方案，需要时才查理论

---

## 优势总结

✅ **快速定位**: 用户可以直接按问题场景找到 Recipe
✅ **逻辑清晰**: Recipes → Tools → Cases → Reference 的渐进路径
✅ **易于扩展**: 新 Recipe 可以直接添加到对应场景分类
✅ **保持兼容**: 所有现有内容都被保留，只是重新组织
✅ **符合习惯**: 与主流 Cookbook（如 O'Reilly Cookbook 系列）结构一致

---

## 下一步行动

1. ✅ 用户确认方案
2. ⬜ 创建新目录结构
3. ⬜ 移动所有文件
4. ⬜ 更新 mkdocs.yml 配置
5. ⬜ 更新 index.md 主页
6. ⬜ 测试构建确保无错误

