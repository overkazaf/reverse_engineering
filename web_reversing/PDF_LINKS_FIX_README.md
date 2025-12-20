# PDF 链接修复功能说明

## 问题描述

当将多个 Markdown 文档合并成一个 PDF 文件时，原来文档之间的链接会失效。例如：

```markdown
[调试技巧](./debugging_techniques.md)
[JavaScript 反混淆](../04-Advanced-Recipes/javascript_deobfuscation.md)
```

这些链接在独立的 Markdown 文件中可以正常工作，但在合并成 PDF 后会失效。

## 解决方案

我们实现了自动链接修复功能，将所有指向 `.md` 文件的内部链接转换为 PDF 内部的锚点引用。

### 工作原理

1. **构建映射表**：从 `mkdocs.yml` 读取所有文档的结构，为每个文档创建唯一的锚点 ID

   - 例如：`03-Basic-Recipes/debugging_techniques.md` → `#03-Basic-Recipes-debugging-techniques`

2. **修复链接**：在处理每个 Markdown 文件时，自动将内部链接转换为锚点引用

   - `[调试技巧](./debugging_techniques.md)` → `[调试技巧](#03-Basic-Recipes-debugging-techniques)`
   - 支持相对路径（`./file.md` 和 `../folder/file.md`）
   - 支持带锚点的链接（`file.md#section` → `#file-id-section`）

3. **添加锚点**：为每个文档章节添加对应的 HTML `id` 属性
   - `<div class="section" id="03-Basic-Recipes-debugging-techniques">`

### 核心文件

- **`fix_pdf_links.py`**：链接修复模块

  - `PDFLinkFixer` 类：负责构建映射表和修复链接
  - 支持自动解析相对路径
  - 支持模糊匹配（当精确路径不存在时）

- **`docs_to_pdf.py`**：PDF 生成主脚本（已集成链接修复）
  - 自动调用链接修复功能
  - 为每个章节添加锚点 ID
  - 在输出中显示修复进度

## 使用方法

### 生成 PDF

```bash
python3 docs_to_pdf.py
```

生成的 PDF 文件：

- 路径：`output/web_reverse_engineering_cookbook_v1.pdf`
- 调试 HTML：`output/docs_debug.html`（可用于验证链接）

### 测试链接修复

```bash
python3 fix_pdf_links.py
```

这会运行测试用例，展示链接修复的效果。

## 功能特性

✅ **自动检测和修复**：无需手动修改 Markdown 文件
✅ **支持相对路径**：`./file.md`、`../folder/file.md`
✅ **支持锚点**：`file.md#section` → `#file-id-section`
✅ **模糊匹配**：当精确路径不存在时尝试匹配文件名
✅ **保留外部链接**：不修改 `http://` 或 `https://` 链接
✅ **详细日志**：显示每个链接的修复过程

## 示例

### 修复前的 Markdown

```markdown
参考资料:

- [调试技巧](./debugging_techniques.md)
- [JavaScript 反混淆](../04-Advanced-Recipes/javascript_deobfuscation.md)
- [API 接口逆向](./api_reverse_engineering.md#section1)
```

### 修复后的 HTML

```html
参考资料:
<ul>
  <li><a href="#03-Basic-Recipes-debugging-techniques">调试技巧</a></li>
  <li>
    <a href="#04-Advanced-Recipes-javascript-deobfuscation"
      >JavaScript 反混淆</a
    >
  </li>
  <li>
    <a href="#03-Basic-Recipes-api-reverse-engineering-section1"
      >API 接口逆向</a
    >
  </li>
</ul>
```

### PDF 中的效果

点击这些链接时，会直接跳转到 PDF 中对应的章节，无需在不同文件之间切换。

## 统计信息

最近一次生成：

- 📁 文件数量：83 个 Markdown 文档
- 🔗 修复链接：数百个内部链接
- 📊 PDF 大小：7.89 MB
- ⚡ 生成时间：约 2-3 分钟

## 注意事项

1. **未找到的文件**：如果链接指向的文件不在 `mkdocs.yml` 中，会保持原样并显示警告
2. **外部链接**：包含 `http://` 或 `https://` 的链接不会被修改
3. **路径一致性**：确保 `mkdocs.yml` 中的路径与实际文件路径一致

## 日志示例

```
📋 构建文件到锚点的映射...
  映射: 03-Basic-Recipes/debugging_techniques.md -> #03-Basic-Recipes-debugging-techniques
✅ 已创建 84 个文件映射

处理文件时:
    🔗 修复链接: ./debugging_techniques.md -> #03-Basic-Recipes-debugging-techniques
    🔗 修复链接: ../04-Advanced-Recipes/javascript_deobfuscation.md -> #04-Advanced-Recipes-javascript-deobfuscation
    ⚠️  未找到映射: 02-Techniques/old_file.md

最终输出:
✅ PDF生成成功!
✨ 内部链接已修复为PDF锚点
✨ 点击文档内链接可以跳转到对应章节
```

## 技术细节

### 锚点 ID 生成规则

```python
# 文件路径: 03-Basic-Recipes/debugging_techniques.md
# 锚点ID: 03-Basic-Recipes-debugging-techniques

# 生成过程:
file_key = path.replace('.md', '')  # 去掉.md后缀
anchor_id = file_key.replace('/', '-').replace('_', '-')  # 替换斜杠和下划线
```

### 链接解析流程

1. 匹配所有 `[text](path.md)` 格式的链接
2. 分离文件路径和锚点部分（如果有）
3. 解析相对路径为绝对路径
4. 在映射表中查找目标文件的锚点 ID
5. 替换原链接为 `[text](#anchor-id)`
6. 如果找不到，尝试模糊匹配
7. 如果仍然找不到，保持原样并记录警告

## 故障排查

### 链接未修复

检查以下内容：

1. 文件是否在 `mkdocs.yml` 的 `nav` 部分
2. 路径是否正确（相对于 `docs` 目录）
3. 查看日志中的警告信息

### 链接跳转失败

1. 检查 `output/docs_debug.html` 验证锚点是否存在
2. 确认目标章节的 `<div id="...">` 是否正确生成
3. 在 PDF 阅读器中测试（某些阅读器可能有兼容性问题）

## 未来改进

- ☐ 支持自定义锚点 ID 格式
- ☐ 添加链接验证工具（检测失效链接）
- ☐ 支持跨 PDF 文档的链接
- ☐ 生成链接映射表供查阅

---

**作者**: +5 (overkazaf@gmail.com)
**版本**: v1.0
**日期**: 2025-12-18
