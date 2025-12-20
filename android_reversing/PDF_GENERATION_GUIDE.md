# PDF 生成完整指南

## 📚 概述

本项目提供了三个版本的PDF生成工具，满足不同需求：

| 工具 | 特点 | 适用场景 |
|------|------|---------|
| docs_to_pdf.py | 原始版本，功能完整 | 稳定可靠，作为参考 |
| docs_to_pdf_fast.py | 并行处理，速度快 | 日常使用，快速生成 |
| docs_to_pdf_robust.py | 详细验证，格式检查 | 格式诊断，问题定位 |
| **docs_to_pdf_ultimate.py** | **集大成者** | **一站式解决方案** |

## 🚀 推荐：一键生成

```bash
# 最简单的方式：快速生成PDF
python docs_to_pdf_ultimate.py --quick

# 带格式验证和修复的完整流程
python docs_to_pdf_ultimate.py --fix-and-generate

# 首次生成（不使用缓存）
python docs_to_pdf_ultimate.py --quick --no-cache
```

## 详细文档

请参考 PDF_SPEED_OPTIMIZATION.md 了解性能优化详情。
