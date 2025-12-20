# 📝 模拟面试题生成器使用说明

## 🎯 功能介绍

`interview_generator.py` 是一个基于 Gemini API 的模拟面试题生成工具，可以根据你的 memo 文档内容智能生成 Android 逆向工程相关的面试题目。

### ✨ 核心特色
- 📚 **内容驱动**: 直接从memo文档提取知识点作为面试问题，确保问题贴合你的学习内容
- 🤖 **AI增强答案**: Gemini专注于为提取的问题生成详细、准确的参考答案
- 🌐 **HTML交互式界面**: 精美的网页界面，支持点击查看答案
- 📁 **文件管理**: HTML文件自动保存到 `interviews/` 目录，便于管理
- ⌨️ **快捷键支持**: 按 `H` 键隐藏所有答案，按 `S` 键显示所有答案
- 📱 **响应式设计**: 支持手机和桌面设备查看

### 🎨 工作原理
1. **内容解析**: 自动解析memo文档的章节结构（二级、三级标题）
2. **话题提取**: 基于内容结构和类型智能分类（概念解释、实践操作、概念对比等）
3. **问题生成**: 根据话题内容生成贴合的面试问题
4. **答案扩展**: 使用Gemini API为每个问题生成详细的技术解答
5. **HTML渲染**: 输出交互式HTML页面，便于复习和练习

## ⚙️ 环境准备

1. **安装依赖**：
   ```bash
   pip install google-generativeai python-dotenv
   ```

2. **配置 API Key**：
   在项目根目录创建 `.env` 文件，添加：
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

3. **代理设置**（如需要）：
   脚本已配置使用 `http://127.0.0.1:1087` 作为代理，如需修改请编辑脚本中的 `proxy_url` 变量。

## 🚀 使用方法

### 基本用法

```bash
# 生成HTML格式面试题（默认），自动保存到 interviews/ 目录
python3 interview_generator.py

# 指定memo文件生成HTML面试题
python3 interview_generator.py -f memo_1_foundations.md

# 生成15个面试题
python3 interview_generator.py -n 15

# 指定输出文件名（会自动放到 interviews/ 目录）
python3 interview_generator.py -o my_questions.html

# 生成JSON格式（保存到项目根目录）
python3 interview_generator.py -t json
```

### 参数说明

- `-f, --file`: 指定要基于的memo文件路径（不指定则随机选择）
- `-n, --num`: 生成题目数量（默认10个）
- `-o, --output`: 指定输出文件路径（不指定则自动生成文件名）
- `-t, --format`: 输出格式，html（默认）或 json

## 📊 生成题目特点

### 题目难度分布
- **基础题 (40%)**: 概念理解、基本操作
- **中级题 (40%)**: 实践应用、问题分析
- **高级题 (20%)**: 架构设计、深度优化

### 题目类型
- **概念解释**: 技术原理、架构理解
- **实践操作**: 工具使用、代码实现
- **问题排查**: 调试技能、故障分析
- **架构设计**: 系统设计、最佳实践

## 📋 输出格式

### 🌐 HTML交互式界面（推荐）
- **精美界面**: 现代化设计，支持响应式布局
- **交互功能**: 点击按钮查看/隐藏答案
- **难度标识**: 彩色标签区分题目难度（基础/中级/高级）
- **统计信息**: 顶部显示题目数量和难度分布
- **快捷键**: 
  - 按 `H` 键隐藏所有答案
  - 按 `S` 键显示所有答案
- **文件管理**: 自动保存到 `interviews/` 目录

### 📄 JSON数据格式
```json
{
  "generated_at": "/path/to/project",
  "total_questions": 10,
  "questions": [
    {
      "id": 1,
      "question": "请解释APK文件的主要组成结构，并说明每个组件的作用",
      "answer": "详细的参考答案内容...",
      "difficulty": "基础",
      "category": "概念解释",
      "key_points": ["APK结构", "组件作用", "文件系统"]
    }
  ]
}
```

## 🎓 使用建议

1. **定期练习**: 建议每周使用不同的memo文件生成面试题进行复习
2. **难度递进**: 先从基础题开始，逐步提高到高级题
3. **记录答案**: 将你的答案记录下来，便于后续回顾
4. **组合使用**: 可以同时使用多个memo文件的题目进行综合练习

## 🔧 自定义扩展

如需自定义题目生成逻辑，可以修改脚本中的：
- `generate_interview_questions()` 方法中的 prompt 模板
- `extract_knowledge_points()` 方法来改变知识点提取逻辑
- 难度分布比例和题目类型

## 🐛 故障排除

1. **API Key 错误**: 确保 `.env` 文件中的 `GEMINI_API_KEY` 正确
2. **网络连接问题**: 检查代理设置或网络连通性
3. **文件未找到**: 确保memo文件存在且路径正确
4. **JSON解析错误**: API响应格式可能有变化，检查 `generate_interview_questions` 方法