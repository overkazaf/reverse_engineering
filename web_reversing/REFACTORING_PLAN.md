# 目录重构方案 - Cookbook风格

## 重构目标

将现有的教程式结构重构为**烹饪食谱（Cookbook）**风格，让用户能：
1. 快速找到解决方案
2. 按难度级别学习
3. 有清晰的参考资料
4. 获得即用型代码片段

---

## 新目录结构设计

```
docs/
│
├── Part I: Getting Started (快速上手)
│   └── 00-Quick-Start/                    [新增]
│       ├── index.md                       - 5分钟快速开始
│       ├── your_first_hook.md             - 第一个Hook
│       ├── decrypt_api_params.md          - 解密API参数
│       └── bypass_simple_captcha.md       - 绕过简单验证码
│
├── Part II: Kitchen Basics (厨房基础)
│   └── 01-Foundations/                    [保持不变]
│       ├── http_https_protocol.md
│       ├── javascript_basics.md
│       └── ... (其他基础知识)
│
├── Part III: Tools & Ingredients (工具箱)
│   └── 02-Tooling/                        [保持不变]
│       ├── browser_devtools.md
│       ├── burp_suite_guide.md
│       └── ... (其他工具)
│
├── Part IV: Basic Recipes (基础配方)
│   └── 03-Basic-Recipes/                  [从02-Techniques重组]
│       ├── re_workflow.md                 - 逆向工作流
│       ├── debugging_techniques.md        - 调试技巧
│       ├── hooking_techniques.md          - Hook技术
│       ├── api_reverse_engineering.md     - API逆向
│       ├── crypto_identification.md       - 加密识别
│       ├── dynamic_parameter_analysis.md  - 动态参数分析
│       └── websocket_reversing.md         - WebSocket逆向
│
├── Part V: Advanced Recipes (高级配方)
│   └── 04-Advanced-Recipes/               [重组]
│       ├── javascript_deobfuscation.md    - JS反混淆 [从02移入]
│       ├── captcha_bypass.md              - 验证码绕过 [从02移入]
│       ├── browser_fingerprinting.md      - 浏览器指纹 [从02移入]
│       ├── javascript_vm_protection.md    - JSVMP [从03移入]
│       ├── webassembly_reversing.md       - WASM逆向 [从03移入]
│       ├── anti_scraping_deep_dive.md     - 反爬深入 [从03移入]
│       ├── frontend_hardening.md          - 前端加固 [从03移入]
│       ├── csp_bypass.md                  - CSP绕过 [从03移入]
│       ├── webrtc_fingerprinting.md       - WebRTC指纹 [从03移入]
│       ├── canvas_fingerprinting.md       - Canvas指纹 [从03移入]
│       ├── tls_fingerprinting.md          - TLS指纹 [从03移入]
│       ├── http2_http3.md                 - HTTP/2&3 [从03移入]
│       └── pwa_service_worker.md          - PWA&SW [从03移入]
│
├── Part VI: Complete Menus (完整菜单/工程化)
│   ├── 05-Case-Studies/                   [保持不变]
│   │   ├── case_ecommerce.md
│   │   ├── case_social_media.md
│   │   └── ...
│   │
│   └── 06-Engineering/                    [从04重命名]
│       ├── distributed_scraping.md
│       ├── proxy_pool_management.md
│       └── ...
│
├── Part VII: Code Kitchen (代码厨房)
│   └── 07-Scripts/                        [从06重命名]
│       ├── hooks/                         [新增子目录]
│       │   ├── network_hooks.md           [从javascript_hook_scripts重组]
│       │   ├── crypto_hooks.md
│       │   └── storage_hooks.md
│       ├── deobfuscation/                 [新增子目录]
│       │   └── deobfuscation_scripts.md
│       ├── automation/                    [新增子目录]
│       │   └── automation_scripts.md
│       └── detection/                     [新增子目录]
│           └── crypto_detection_scripts.md
│
└── Part VIII: Reference (参考资料)
    ├── 08-Cheat-Sheets/                   [新增]
    │   ├── common_commands.md
    │   ├── crypto_signatures.md
    │   ├── tool_shortcuts.md
    │   ├── regex_patterns.md
    │   └── http_headers.md
    │
    ├── 09-Templates/                      [新增]
    │   ├── project_structure.md
    │   ├── docker_setup.md
    │   └── ci_cd_pipeline.md
    │
    ├── 10-Troubleshooting/                [新增]
    │   ├── common_issues.md               - 常见问题
    │   ├── hook_not_working.md            - Hook不生效
    │   ├── decryption_failed.md           - 解密失败
    │   └── performance_issues.md          - 性能问题
    │
    └── 11-Resources/                      [从07重命名]
        ├── github_projects.md
        ├── learning_resources.md
        └── faq.md
```

---

## 详细变更映射

### 阶段1: 重命名现有目录

| 旧路径 | 新路径 | 说明 |
|--------|--------|------|
| `00-Foundations/` | `01-Foundations/` | 编号后移 |
| `01-Tooling/` | `02-Tooling/` | 编号后移 |
| `04-Engineering/` | `06-Engineering/` | 移到Complete Menus部分 |
| `06-Scripts/` | `07-Scripts/` | 移到Code Kitchen部分 |
| `07-Others/` | `11-Resources/` | 重命名并后移 |

### 阶段2: 重组Techniques和Advanced-Topics

**从 `02-Techniques/` 分出：**

基础配方 → `03-Basic-Recipes/`:
- `re_workflow.md`
- `debugging_techniques.md`
- `hooking_techniques.md`
- `api_reverse_engineering.md`
- `crypto_identification.md`
- `dynamic_parameter_analysis.md`
- `websocket_reversing.md`

高级配方 → `04-Advanced-Recipes/`:
- `javascript_deobfuscation.md`
- `captcha_bypass.md`
- `browser_fingerprinting.md`

**从 `03-Advanced-Topics/` 全部移入 `04-Advanced-Recipes/`:**
- 所有文件移入高级配方

### 阶段3: 创建新目录

1. **00-Quick-Start/** (新建空目录，稍后补充内容)
2. **08-Cheat-Sheets/** (新建空目录)
3. **09-Templates/** (新建空目录)
4. **10-Troubleshooting/** (新建空目录)

---

## 文件移动清单

### 步骤1: 创建新目录结构
```bash
mkdir -p docs/00-Quick-Start
mkdir -p docs/03-Basic-Recipes
mkdir -p docs/04-Advanced-Recipes
mkdir -p docs/08-Cheat-Sheets
mkdir -p docs/09-Templates
mkdir -p docs/10-Troubleshooting
```

### 步骤2: 移动文件到Basic-Recipes
```bash
mv docs/02-Techniques/re_workflow.md docs/03-Basic-Recipes/
mv docs/02-Techniques/debugging_techniques.md docs/03-Basic-Recipes/
mv docs/02-Techniques/hooking_techniques.md docs/03-Basic-Recipes/
mv docs/02-Techniques/api_reverse_engineering.md docs/03-Basic-Recipes/
mv docs/02-Techniques/crypto_identification.md docs/03-Basic-Recipes/
mv docs/02-Techniques/dynamic_parameter_analysis.md docs/03-Basic-Recipes/
mv docs/02-Techniques/websocket_reversing.md docs/03-Basic-Recipes/
```

### 步骤3: 移动文件到Advanced-Recipes
```bash
# 从02-Techniques移入
mv docs/02-Techniques/javascript_deobfuscation.md docs/04-Advanced-Recipes/
mv docs/02-Techniques/captcha_bypass.md docs/04-Advanced-Recipes/
mv docs/02-Techniques/browser_fingerprinting.md docs/04-Advanced-Recipes/

# 从03-Advanced-Topics移入
mv docs/03-Advanced-Topics/javascript_vm_protection.md docs/04-Advanced-Recipes/
mv docs/03-Advanced-Topics/webassembly_reversing.md docs/04-Advanced-Recipes/
mv docs/03-Advanced-Topics/anti_scraping_deep_dive.md docs/04-Advanced-Recipes/
mv docs/03-Advanced-Topics/frontend_hardening.md docs/04-Advanced-Recipes/
mv docs/03-Advanced-Topics/csp_bypass.md docs/04-Advanced-Recipes/
mv docs/03-Advanced-Topics/webrtc_fingerprinting.md docs/04-Advanced-Recipes/
mv docs/03-Advanced-Topics/canvas_fingerprinting.md docs/04-Advanced-Recipes/
mv docs/03-Advanced-Topics/tls_fingerprinting.md docs/04-Advanced-Recipes/
mv docs/03-Advanced-Topics/http2_http3.md docs/04-Advanced-Recipes/
mv docs/03-Advanced-Topics/pwa_service_worker.md docs/04-Advanced-Recipes/
```

### 步骤4: 重命名目录
```bash
mv docs/00-Foundations docs/01-Foundations
mv docs/01-Tooling docs/02-Tooling
mv docs/04-Engineering docs/06-Engineering
mv docs/06-Scripts docs/07-Scripts
mv docs/07-Others docs/11-Resources
```

### 步骤5: 删除空目录
```bash
rmdir docs/02-Techniques
rmdir docs/03-Advanced-Topics
```

---

## 需要更新的引用

所有文档中的内部链接需要批量更新：

### 链接替换规则

```
00-Foundations/  → 01-Foundations/
01-Tooling/      → 02-Tooling/
02-Techniques/   → 03-Basic-Recipes/ 或 04-Advanced-Recipes/
03-Advanced-Topics/ → 04-Advanced-Recipes/
04-Engineering/  → 06-Engineering/
06-Scripts/      → 07-Scripts/
07-Others/       → 11-Resources/
```

### 特殊替换（需要逐个确认）

```
../02-Techniques/javascript_deobfuscation.md → ../04-Advanced-Recipes/javascript_deobfuscation.md
../02-Techniques/captcha_bypass.md → ../04-Advanced-Recipes/captcha_bypass.md
../02-Techniques/browser_fingerprinting.md → ../04-Advanced-Recipes/browser_fingerprinting.md
```

---

## mkdocs.yml 更新

完整的新导航结构（见下一节）

---

## 风险评估

**低风险：**
- ✅ 只是移动和重命名，不修改内容
- ✅ Git可以追踪所有变更

**需要注意：**
- ⚠️ 内部链接需要仔细更新
- ⚠️ summary.md文件需要同步移动
- ⚠️ 确保没有遗漏的引用

---

## 回滚方案

如果重构出现问题，使用Git回滚：

```bash
git checkout HEAD -- docs/
```

---

## 执行顺序

1. ✅ 创建此重构计划文档
2. ⏳ 用户确认方案
3. ⏳ 执行文件移动（分步执行，每步验证）
4. ⏳ 更新mkdocs.yml
5. ⏳ 批量更新内部链接
6. ⏳ 测试mkdocs serve
7. ⏳ Git提交

---

## 预期效果

重构后的目录结构将：
- ✨ 更符合Cookbook风格
- ✨ 有清晰的难度分级（Basic → Advanced）
- ✨ 分离参考资料和教程内容
- ✨ 为后续内容扩展预留空间
- ✨ 保持所有现有内容完整性

---

## 下一步

等待用户确认后执行重构。
