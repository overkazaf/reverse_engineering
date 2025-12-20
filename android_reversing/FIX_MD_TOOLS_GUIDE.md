# Markdown 修复工具使用指南

## 工具列表

我创建了两个可复用的 Markdown 修复工具：

### 1. fix_md_rules.py (推荐)
**基于规则的快速修复工具**

- ✅ 速度快（不需要 API）
- ✅ 结果稳定可靠
- ✅ 详细的修复日志
- ✅ 支持预览模式

### 2. fix_md_with_gemini_single.py
**使用 Gemini API 的智能修复工具**

- ⚠️ 需要 API 调用（可能超时）
- ⚠️ 消耗 API 配额
- ✅ 可以处理复杂的格式问题

---

## fix_md_rules.py 使用方法

### 基本用法

```bash
# 1. 预览修复结果（推荐先执行此步骤）
python3 fix_md_rules.py docs/path/to/file.md --dry-run

# 2. 执行实际修复（会自动备份原文件）
python3 fix_md_rules.py docs/path/to/file.md

# 3. 保存到新文件
python3 fix_md_rules.py docs/path/to/file.md -o output.md

# 4. 不备份原文件
python3 fix_md_rules.py docs/path/to/file.md --no-backup
```

### 路径格式说明

⚠️ **重要**: 文件路径必须包含 `docs/` 前缀（如果文件在 docs 目录下）

✅ **正确**:
```bash
python3 fix_md_rules.py docs/01-Recipes/Network/crypto_analysis.md
```

❌ **错误**:
```bash
python3 fix_md_rules.py 01-Recipes/Network/crypto_analysis.md  # 缺少 docs 前缀
```

### 详细日志输出

工具会显示：

1. **扫描结果**: 找到的格式问题数量
   ```
   🔍 分析格式问题:
      # # 标题: 20
      - -- 分隔线: 6
      ☐ 复选框: 6
      ```` 四引号: 4
   ```

2. **修复过程**: 每个规则修复了多少处
   ```
   ✏️  规则 1: 修复标题格式 (# # → ##)
      修复了 8 处
   ✏️  规则 2: 修复水平分隔线 (- -- → ---)
      修复了 6 处
   ```

3. **修复总结**: 文件大小变化
   ```
   📊 修复总结:
      修复前: 13,902 字节
      修复后: 13,875 字节
      变化: -27 字节
   ```

4. **Dry Run 模式**: 显示修复示例
   ```
   📋 修复示例 (前 30 行):

   行 3:
     - '# # 问题场景'
     + '## 问题场景'
   ```

### 支持的修复规则

| 规则 | 说明 | 示例 |
|------|------|------|
| 1 | 修复标题格式 | `# #` → `##` |
| 2 | 修复水平分隔线 | `- --` → `---` |
| 3 | 修复列表项符号 | `☐` → `-` |
| 4 | 修复四个反引号 | <code>\`\`\`\`</code> → <code>\`\`\`</code> |
| 5 | 修复标题后缺少空格 | `##标题` → `## 标题` |
| 6 | 修复列表项后缺少空格 | `-item` → `- item` |
| 7 | 移除过多连续空行 | 4+ 空行 → 3 空行 |
| 8 | 修复代码块标记空格 | <code>\`\`\` python</code> → <code>\`\`\`python</code> |

---

## fix_md_with_gemini_single.py 使用方法

### 基本用法

```bash
# 修复文件（覆盖原文件，自动备份）
python3 fix_md_with_gemini_single.py docs/path/to/file.md

# 保存到新文件
python3 fix_md_with_gemini_single.py docs/path/to/file.md -o output.md

# 不备份
python3 fix_md_with_gemini_single.py docs/path/to/file.md --no-backup
```

### 注意事项

- ⚠️ 大文件可能会超时（504 错误）
- ⚠️ 需要代理配置：http://127.0.0.1:1087
- ⚠️ 会验证内容长度，防止内容丢失

---

## 批量处理示例

### 修复多个文件

```bash
# 修复特定目录下的所有 .md 文件
for file in docs/01-Recipes/Network/*.md; do
    echo "Processing: $file"
    python3 fix_md_rules.py "$file"
done
```

### 先预览，再批量修复

```bash
# 第一步：预览所有文件
for file in docs/01-Recipes/Network/*.md; do
    echo "===== $file ====="
    python3 fix_md_rules.py "$file" --dry-run
    echo ""
    read -p "继续下一个? (Enter)"
done

# 第二步：批量修复（如果预览满意）
for file in docs/01-Recipes/Network/*.md; do
    python3 fix_md_rules.py "$file"
done
```

---

## 实际案例

### 案例 1: tls_fingerprinting_guide.md

**问题**:
- `# #` 标题: 8 个
- `- --` 分隔线: 8 个
- `☐` 复选框: 7 个
- ```` 四引号: 8 个

**修复**:
```bash
python3 fix_md_rules.py docs/01-Recipes/Network/tls_fingerprinting_guide.md
```

**结果**: ✅ 所有 31 个格式问题已修复

### 案例 2: crypto_analysis.md

**问题**:
- `# #` 标题: 20 个
- `- --` 分隔线: 6 个
- `☐` 复选框: 6 个
- ```` 四引号: 4 个

**修复**:
```bash
python3 fix_md_rules.py docs/01-Recipes/Network/crypto_analysis.md
```

**结果**: ✅ 所有 36 个格式问题已修复

---

## 常见问题

### Q: 什么时候使用 --dry-run?

A: **总是先使用 --dry-run 预览结果！** 这样可以：
- 查看会修复哪些内容
- 避免意外修改
- 确认修复符合预期

### Q: 备份文件在哪里?

A: 备份文件保存在原文件旁边，扩展名为 `.backup`：
```
docs/01-Recipes/Network/crypto_analysis.md          # 修复后的文件
docs/01-Recipes/Network/crypto_analysis.md.backup   # 原始备份
```

### Q: 如何恢复原文件?

A: 只需复制备份文件：
```bash
cp docs/path/to/file.md.backup docs/path/to/file.md
```

### Q: 规则修复和 Gemini API 哪个更好?

A: **大多数情况下使用 fix_md_rules.py**:
- ✅ 更快
- ✅ 更可靠
- ✅ 不会超时
- ✅ 不消耗 API

只有在遇到非常复杂的格式问题时才考虑使用 Gemini API。

---

## 下一步

修复完文件后，重新生成 PDF：

```bash
python3 docs_to_pdf_final.py --no-cache
```

---

**工具位置**:
- `/Users/nongjiawu/frida/reverse_engineering/android_reversing/fix_md_rules.py`
- `/Users/nongjiawu/frida/reverse_engineering/android_reversing/fix_md_with_gemini_single.py`

**创建时间**: 2025-12-19
