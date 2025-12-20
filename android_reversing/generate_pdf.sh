#!/bin/bash
# PDF生成快捷脚本

echo "╔══════════════════════════════════════════════════╗"
echo "║       Android Reverse Engineering Cookbook       ║"
echo "║              PDF Generator v2.0                  ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到python3"
    exit 1
fi

# 检查依赖
echo "🔍 检查依赖..."
python3 -c "import mistune, weasyprint, yaml" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ 缺少依赖，正在安装..."
    pip3 install mistune weasyprint pillow pyyaml
fi

# 解析参数
WORKERS=8
EXTRA_ARGS=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -w|--workers)
            WORKERS="$2"
            shift 2
            ;;
        --no-cache)
            EXTRA_ARGS="$EXTRA_ARGS --no-cache"
            shift
            ;;
        --fix)
            EXTRA_ARGS="$EXTRA_ARGS --fix-files"
            shift
            ;;
        --quick)
            EXTRA_ARGS="$EXTRA_ARGS --skip-validation"
            shift
            ;;
        *)
            echo "未知参数: $1"
            echo "用法: $0 [-w workers] [--no-cache] [--fix] [--quick]"
            exit 1
            ;;
    esac
done

# 生成PDF
echo "🚀 开始生成PDF..."
echo "   工作进程: $WORKERS"
echo "   额外参数: $EXTRA_ARGS"
echo ""

START_TIME=$(date +%s)

python3 docs_to_pdf_final.py -w $WORKERS $EXTRA_ARGS

if [ $? -eq 0 ]; then
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    echo ""
    echo "✅ 生成成功！耗时: ${DURATION}秒"
    echo "📁 输出目录: output/"
    
    # 显示文件信息
    if [ -f "output/android_reverse_engineering_cookbook_final.pdf" ]; then
        SIZE=$(du -h "output/android_reverse_engineering_cookbook_final.pdf" | cut -f1)
        echo "📊 文件大小: $SIZE"
    fi
else
    echo ""
    echo "❌ 生成失败，请检查错误信息"
    exit 1
fi

echo ""
echo "🎉 完成！"
