#!/bin/bash
# PDF 生成便捷脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 运行改进版的 PDF 生成脚本
python3 docs_to_pdf_improved.py "$@"
