# PDF 生成器改进总结

## 新增功能

### 1. 支持指定章节范围

原版 `docs_to_pdf.py` 只能生成完整的 PDF，改进版 `docs_to_pdf_improved.py` 支持灵活的章节选择。

### 2. 命令行参数

| 参数 | 功能 | 示例 |
|------|------|------|
| `--list` | 列出所有可用章节 | `./gen_pdf.sh --list` |
| `--parts` | 按 Part 范围生成 | `./gen_pdf.sh --parts 1-2` |
| `--sections` | 按章节名称生成 | `./gen_pdf.sh --sections "Foundations,Tooling"` |
| `--output` | 自定义输出文件名 | `./gen_pdf.sh --output my_book.pdf` |
| `--translate` | 翻译代码注释 | `./gen_pdf.sh --translate` |

### 3. 便捷脚本

创建了 `gen_pdf.sh` 便捷脚本，自动切换到正确的工作目录。

## 使用示例

### 查看所有章节
```bash
./gen_pdf.sh --list
```

输出：
```
📚 可用章节列表:
============================================================

🔹 Part 1: Part I: Getting Started
  📂 Quick Start
    • Overview
    • Your First Hook
    • Decrypt API Params
    • Bypass Simple CAPTCHA

🔹 Part 2: Part II: Kitchen Basics
  📂 Foundations
    • HTTP/HTTPS Protocol
    • Browser Architecture
    ...
```

### 生成特定 Parts

#### 只生成入门章节 (Part 1-2)
```bash
./gen_pdf.sh --parts 1-2 --output getting_started.pdf
```

#### 生成工具和技术章节 (Part 3-4)
```bash
./gen_pdf.sh --parts 3-4 --output tools_and_basics.pdf
```

#### 生成高级和案例章节 (Part 5-6)
```bash
./gen_pdf.sh --parts 5-6 --output advanced_cases.pdf
```

### 生成特定章节

```bash
./gen_pdf.sh --sections "Foundations,Tooling" --output basics.pdf
```

### 生成完整手册

```bash
# 方式 1: 不指定参数（默认生成全部）
./gen_pdf.sh

# 方式 2: 指定所有 Parts
./gen_pdf.sh --parts 1-7

# 方式 3: 自定义文件名
./gen_pdf.sh --output web_cookbook_complete.pdf
```

## 主要改进点

### 1. 灵活的过滤系统

```python
# Parts 过滤器
parts_filter = [1, 2, 3]  # 只包含 Part 1, 2, 3

# Sections 过滤器
sections_filter = ["Foundations", "Tooling"]  # 只包含这两个章节
```

### 2. 智能文件命名

- 无过滤器: `web_cookbook_full.pdf`
- Parts 过滤: `web_cookbook_parts_1_2.pdf`
- Sections 过滤: `web_cookbook_Foundations_Tooling.pdf`
- 自定义: 使用 `--output` 指定

### 3. 动态目录生成

目录只包含实际生成的章节，不会显示未选中的内容。

### 4. 封面信息

封面会显示包含的章节范围：
- "包含章节: Part 1, 2"
- "包含章节: Foundations, Tooling"

## 典型使用场景

### 场景 1: 快速入门手册

为新手创建一个简化版，只包含入门内容：

```bash
./gen_pdf.sh --parts 1-3 --output quick_start_guide.pdf
```

包含:
- Part 1: Getting Started
- Part 2: Kitchen Basics
- Part 3: Tools & Ingredients

### 场景 2: 工具参考手册

为经验用户创建工具参考：

```bash
./gen_pdf.sh --sections "Tooling" --output tools_reference.pdf
```

### 场景 3: 高级技术手册

为高级用户提供深入内容：

```bash
./gen_pdf.sh --parts 5-7 --output advanced_techniques.pdf
```

包含:
- Part 5: Advanced Recipes
- Part 6: Case Studies
- Part 7: Engineering

### 场景 4: 分章节打印

生成多个小册子，便于打印和分发：

```bash
# 基础篇
./gen_pdf.sh --parts 1-2 --output vol1_basics.pdf

# 工具篇
./gen_pdf.sh --parts 3-4 --output vol2_tools.pdf

# 高级篇
./gen_pdf.sh --parts 5-7 --output vol3_advanced.pdf
```

## 技术细节

### Parts 过滤器语法

支持以下格式：

1. **单个范围**: `1-3` → [1, 2, 3]
2. **多个数字**: `1,3,5` → [1, 3, 5]
3. **混合**: `1-3,5,7-9` → [1, 2, 3, 5, 7, 8, 9]

实现：
```python
def parse_parts_filter(parts_str):
    parts = set()
    for part in parts_str.split(','):
        part = part.strip()
        if '-' in part:
            start, end = part.split('-')
            parts.update(range(int(start), int(end) + 1))
        else:
            parts.add(int(part))
    return sorted(list(parts))
```

### Sections 过滤器语法

逗号分隔的章节名称：

```python
def parse_sections_filter(sections_str):
    return [s.strip() for s in sections_str.split(',')]
```

### 过滤逻辑

```python
def should_include_section(self, section_name, part_index):
    # 无过滤器 -> 包含所有
    if not self.parts_filter and not self.sections_filter:
        return True

    # Parts 过滤
    if self.parts_filter and section_name.startswith('Part '):
        return part_index in self.parts_filter

    # Sections 过滤
    if self.sections_filter:
        actual_section_name = section_name.split(':', 1)[1].strip()
        return actual_section_name in self.sections_filter

    return True
```

## 性能对比

| 场景 | 页数 | 生成时间 | 文件大小 |
|------|------|----------|----------|
| 完整手册 | ~500 页 | 2-3 分钟 | 15-20 MB |
| Part 1-2 | ~100 页 | 30-40 秒 | 3-5 MB |
| 单个章节 | ~20 页 | 10-15 秒 | 1-2 MB |

*性能取决于内容量和代码块数量*

## 文件结构

```
web_reversing/
├── docs_to_pdf.py              # 原版（完整生成）
├── docs_to_pdf_improved.py     # 改进版（支持过滤）
├── gen_pdf.sh                  # 便捷启动脚本
├── PDF_GENERATION_USAGE.md     # 详细使用指南
└── PDF_GENERATOR_IMPROVEMENTS.md  # 本文档
```

## 向后兼容

改进版完全向后兼容：

```bash
# 原版方式（生成全部）
python docs_to_pdf.py

# 改进版方式（生成全部）
python docs_to_pdf_improved.py

# 等价
./gen_pdf.sh
```

## 未来改进

可能的扩展方向：

1. **并行生成**: 同时生成多个 Part，提升性能
2. **增量更新**: 只重新生成修改过的章节
3. **交互模式**: 通过菜单选择要生成的章节
4. **批量生成**: 一次生成多个预定义配置
5. **书签优化**: 更好的 PDF 书签层级
6. **样式模板**: 支持多种 PDF 样式主题

## 注意事项

1. **章节名称**: 必须精确匹配 `mkdocs.yml` 中的定义
2. **工作目录**: 使用 `gen_pdf.sh` 确保在正确目录运行
3. **依赖检查**: 首次运行会检查所需依赖
4. **中文字体**: macOS 使用系统字体，其他系统可能需要调整

## 反馈与支持

- 📧 Email: overkazaf@gmail.com
- 💬 WeChat: _0xAF_

## 更新日志

### v1.1 (2025-12-18)
- ✨ 新增 `--parts` 参数支持 Part 范围选择
- ✨ 新增 `--sections` 参数支持章节名称过滤
- ✨ 新增 `--list` 命令查看所有章节
- ✨ 新增 `--output` 自定义输出文件名
- ✨ 新增 `gen_pdf.sh` 便捷脚本
- 🐛 修复章节过滤逻辑
- 📝 完善使用文档

### v1.0
- 初始版本（原 docs_to_pdf.py）
- 支持完整手册生成
- 中文字体优化
