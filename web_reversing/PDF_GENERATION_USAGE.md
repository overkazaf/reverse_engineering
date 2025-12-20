# PDF 生成使用指南

## 简介

`docs_to_pdf_improved.py` 是改进版的 PDF 生成工具，支持灵活的章节范围选择。

## 安装依赖

```bash
pip install markdown2 weasyprint pillow pyyaml
```

## 基本使用

### 1. 查看所有可用章节

```bash
python docs_to_pdf_improved.py --list
```

输出示例：
```
📚 可用章节列表:
============================================================

🔹 Part 1: Part I: Getting Started
  📂 Quick Start
    • Overview
    • Your First Hook
    • Decrypt API Params

🔹 Part 2: Part II: Kitchen Basics
  📂 Foundations
    • HTTP/HTTPS Protocol
    • Browser Architecture
    • JavaScript Basics
...
```

### 2. 生成全部章节

```bash
python docs_to_pdf_improved.py
```

生成文件：`output/web_cookbook_full.pdf`

### 3. 生成指定 Part 范围

#### 生成 Part 1 到 Part 2
```bash
python docs_to_pdf_improved.py --parts 1-2
```

生成文件：`output/web_cookbook_parts_1_2.pdf`

#### 生成 Part 1 和 Part 3（跳过 Part 2）
```bash
python docs_to_pdf_improved.py --parts 1,3
```

生成文件：`output/web_cookbook_parts_1_3.pdf`

#### 复杂范围组合
```bash
python docs_to_pdf_improved.py --parts 1-3,5
```

生成 Part 1, 2, 3, 5

### 4. 生成指定章节

```bash
python docs_to_pdf_improved.py --sections "Foundations,Tooling"
```

生成文件：`output/web_cookbook_Foundations_Tooling.pdf`

注意：章节名称要精确匹配，使用逗号分隔，不要有多余空格。

### 5. 自定义输出文件名

```bash
python docs_to_pdf_improved.py --parts 1-2 --output my_cookbook.pdf
```

生成文件：`output/my_cookbook.pdf`

### 6. 启用中文注释翻译

```bash
python docs_to_pdf_improved.py --parts 1-2 --translate
```

会将代码中的中文注释翻译为英文。

## 高级用法

### 组合参数

```bash
# 生成 Part 1-2，自定义文件名，翻译注释
python docs_to_pdf_improved.py --parts 1-2 --output getting_started.pdf --translate

# 生成特定章节，自定义文件名
python docs_to_pdf_improved.py --sections "Foundations,Tooling,Techniques" --output basics.pdf
```

## 命令行参数说明

| 参数 | 简写 | 说明 | 示例 |
|------|------|------|------|
| `--list` | 无 | 列出所有可用章节 | `--list` |
| `--parts` | 无 | 指定 Part 范围 | `--parts 1-2` 或 `--parts 1,3,5` |
| `--sections` | 无 | 指定章节名称 | `--sections "Foundations,Tooling"` |
| `--output` | `-o` | 输出文件名 | `--output my_book.pdf` 或 `-o my_book.pdf` |
| `--translate` | 无 | 翻译代码注释 | `--translate` |

## Parts 过滤器语法

支持以下格式：

1. **范围**: `1-3` → 生成 Part 1, 2, 3
2. **列表**: `1,3,5` → 生成 Part 1, 3, 5
3. **混合**: `1-3,5,7-9` → 生成 Part 1, 2, 3, 5, 7, 8, 9

## Sections 过滤器语法

使用逗号分隔的章节名称：

```bash
--sections "Foundations,Tooling,Techniques"
```

章节名称必须精确匹配 `mkdocs.yml` 中的定义。

## 输出文件命名规则

- **全部章节**: `web_cookbook_full.pdf`
- **指定 Parts**: `web_cookbook_parts_1_2.pdf`
- **指定 Sections**: `web_cookbook_Foundations_Tooling.pdf`
- **自定义**: 使用 `--output` 指定

## 典型使用场景

### 场景 1: 初学者入门包

生成入门相关的前两个 Part：

```bash
python docs_to_pdf_improved.py --parts 1-2 --output getting_started.pdf
```

### 场景 2: 工具参考手册

只生成工具相关章节：

```bash
python docs_to_pdf_improved.py --sections "Tooling" --output tools_reference.pdf
```

### 场景 3: 高级主题精选

生成高级主题和案例研究：

```bash
python docs_to_pdf_improved.py --parts 5-6 --output advanced_topics.pdf
```

### 场景 4: 完整手册（英文注释版）

生成全部内容并翻译注释：

```bash
python docs_to_pdf_improved.py --translate --output full_handbook_en.pdf
```

## 注意事项

1. **章节名称大小写敏感**：使用 `--list` 查看精确的章节名称
2. **输出目录**：所有 PDF 文件生成到 `output/` 目录
3. **中文字体**：脚本会自动使用系统中文字体，确保中文正确显示
4. **生成时间**：完整手册可能需要 1-2 分钟，部分章节更快

## 故障排除

### 问题 1: 找不到章节

**错误信息**: "没有找到匹配的章节"

**解决方法**:
1. 运行 `--list` 查看所有可用章节
2. 确认章节名称拼写和大小写正确
3. 确认 Part 编号是否存在

### 问题 2: 中文显示问题

**解决方法**:
- macOS: 确保系统有 Hiragino Sans GB 或 STHeiti 字体
- 其他系统: 编辑脚本中的字体路径

### 问题 3: PDF 生成失败

**检查步骤**:
1. 确认所有依赖已安装: `pip list | grep -E "markdown2|weasyprint|yaml"`
2. 检查 `mkdocs.yml` 文件存在且格式正确
3. 确认 `docs/` 目录存在

## 性能优化建议

1. **分块生成**: 大型手册建议按 Part 分块生成，然后合并
2. **禁用翻译**: 如果不需要英文注释，不要使用 `--translate`
3. **并行生成**: 可以同时运行多个命令生成不同部分

## 与原版的区别

| 功能 | 原版 (docs_to_pdf.py) | 改进版 (docs_to_pdf_improved.py) |
|------|------------------------|-----------------------------------|
| 生成范围 | 全部章节 | 支持选择 Parts/Sections |
| 命令行参数 | 无 | 丰富的命令行选项 |
| 章节列表 | 无 | `--list` 命令 |
| 输出文件名 | 固定 | 可自定义 |
| 适用场景 | 完整手册 | 灵活的部分生成 |

## 更多示例

```bash
# 查看帮助信息
python docs_to_pdf_improved.py --help

# 只生成 Part 3
python docs_to_pdf_improved.py --parts 3

# 生成多个分散的 Parts
python docs_to_pdf_improved.py --parts 1,4,6

# 生成工具和技术两个章节
python docs_to_pdf_improved.py --sections "Tooling,Techniques" --output tools_and_techniques.pdf
```

## 反馈与改进

如有问题或建议，请联系：
- 📧 Email: overkazaf@gmail.com
- 💬 WeChat: _0xAF_
