# PDF中文字体乱码修复说明

## 问题描述

在使用Python脚本导出PDF时，中文字符显示为乱码（问号框 `�`），如截图所示。

## 问题原因

WeasyPrint生成PDF时无法正确加载中文字体，原因包括：

1. **使用`local()`函数引用字体**：WeasyPrint不支持CSS的`local()`函数来引用系统字体
2. **使用Google Fonts CDN**：PDF生成时无法访问在线字体资源
3. **缺少明确的字体文件路径**：WeasyPrint需要使用`file://`协议明确指定字体文件的绝对路径

## 解决方案

### 1. 找到macOS系统中可用的中文字体

使用以下命令查找系统中支持中文的字体：

```bash
# 查找支持中文的字体
fc-list :lang=zh | head -10

# 在macOS上找到的可用字体：
# - Hiragino Sans GB (冬青黑体简体)
# - STHeiti (华文黑体)
# - Songti SC (宋体简体)
# - Arial Unicode MS (支持中文)
```

### 2. 修改字体配置

在`docs_to_pdf.py`和`memo_to_pdf.py`中，将CSS字体配置修改为使用明确的文件路径：

**修改前（错误示例）：**
```css
@font-face {
    font-family: 'Chinese Sans';
    src: local('PingFang SC'), local('Microsoft YaHei');  /* ❌ WeasyPrint不支持 */
}

@import url('https://fonts.googleapis.com/...');  /* ❌ 无法访问CDN */
```

**修改后（正确示例）：**
```css
@font-face {
    font-family: 'Chinese Sans';
    src: url('file:///System/Library/Fonts/Hiragino Sans GB.ttc') format('truetype'),
         url('file:///System/Library/Fonts/STHeiti Light.ttc') format('truetype'),
         url('file:///System/Library/Fonts/Supplemental/Songti.ttc') format('truetype'),
         url('file:///Library/Fonts/Arial Unicode.ttf') format('truetype');
    font-weight: normal;
}

@font-face {
    font-family: 'Chinese Sans';
    src: url('file:///System/Library/Fonts/Hiragino Sans GB.ttc') format('truetype'),
         url('file:///System/Library/Fonts/STHeiti Medium.ttc') format('truetype'),
         url('file:///System/Library/Fonts/Supplemental/Songti.ttc') format('truetype');
    font-weight: bold;
}
```

### 3. 已修改的文件

以下文件已经修复：

- ✅ `docs_to_pdf.py` - 文档PDF生成器
- ✅ `memo_to_pdf.py` - 速记手册PDF生成器
- ✅ `test_chinese_font.py` - 中文字体测试脚本（新增）

## 验证修复

### 方法1：运行测试脚本

```bash
# 生成测试PDF
python3 test_chinese_font.py

# 验证PDF中的中文字符
python3 test_pdf_fonts.py output/test_chinese_font.pdf
```

**预期输出：**
```
✅ 测试PDF生成成功!
📁 文件路径: output/test_chinese_font.pdf
📊 文件大小: 204.52 KB

🔤 Chinese characters found: 152
✅ Chinese characters detected: 问 题 使 用 问 题 如 何...
✅ PDF contains Chinese characters!
```

### 方法2：生成完整PDF

```bash
# 生成文档PDF
python3 docs_to_pdf.py

# 或生成速记手册PDF
python3 memo_to_pdf.py
```

打开生成的PDF文件，确认中文字符正常显示，不再是问号框。

## macOS系统中文字体位置

| 字体名称 | 文件路径 | 说明 |
|---------|---------|------|
| Hiragino Sans GB | `/System/Library/Fonts/Hiragino Sans GB.ttc` | 冬青黑体（推荐） |
| STHeiti Light | `/System/Library/Fonts/STHeiti Light.ttc` | 华文黑体细体 |
| STHeiti Medium | `/System/Library/Fonts/STHeiti Medium.ttc` | 华文黑体中等 |
| Songti SC | `/System/Library/Fonts/Supplemental/Songti.ttc` | 宋体简体 |
| Arial Unicode MS | `/Library/Fonts/Arial Unicode.ttf` | Arial Unicode（备用） |

## 其他系统适配

### Windows系统

如果在Windows上运行，需要修改字体路径：

```css
@font-face {
    font-family: 'Chinese Sans';
    src: url('file:///C:/Windows/Fonts/msyh.ttc') format('truetype'),      /* 微软雅黑 */
         url('file:///C:/Windows/Fonts/simhei.ttf') format('truetype'),    /* 黑体 */
         url('file:///C:/Windows/Fonts/simsun.ttc') format('truetype');    /* 宋体 */
    font-weight: normal;
}
```

### Linux系统

Linux系统字体路径：

```css
@font-face {
    font-family: 'Chinese Sans';
    src: url('file:///usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc') format('truetype'),
         url('file:///usr/share/fonts/truetype/wqy/wqy-microhei.ttc') format('truetype'),
         url('file:///usr/share/fonts/truetype/arphic/uming.ttc') format('truetype');
    font-weight: normal;
}
```

## 跨平台解决方案

为了让代码在不同平台上都能工作，可以添加平台检测：

```python
import platform
import os

def get_chinese_fonts():
    """根据操作系统返回中文字体路径"""
    system = platform.system()

    if system == 'Darwin':  # macOS
        return [
            "url('file:///System/Library/Fonts/Hiragino Sans GB.ttc')",
            "url('file:///System/Library/Fonts/STHeiti Light.ttc')",
            "url('file:///Library/Fonts/Arial Unicode.ttf')"
        ]
    elif system == 'Windows':
        return [
            "url('file:///C:/Windows/Fonts/msyh.ttc')",
            "url('file:///C:/Windows/Fonts/simhei.ttf')",
            "url('file:///C:/Windows/Fonts/simsun.ttc')"
        ]
    elif system == 'Linux':
        return [
            "url('file:///usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')",
            "url('file:///usr/share/fonts/truetype/wqy/wqy-microhei.ttc')"
        ]
    else:
        return ["url('file:///Library/Fonts/Arial Unicode.ttf')"]
```

## 测试清单

- [x] 测试PDF生成成功
- [x] 中文标题正常显示
- [x] 中文正文正常显示
- [x] 表格中的中文正常显示
- [x] 代码注释中的中文正常显示
- [x] 可以使用PyPDF2提取中文文本
- [x] emoji符号正常显示（❌⚠️✅等）

## 常见问题

### Q1: 为什么WeasyPrint不支持`local()`函数？

WeasyPrint是一个独立的渲染引擎，不依赖浏览器，因此不支持浏览器才有的`local()`字体查找机制。它需要明确的文件路径。

### Q2: 如何确认字体文件是否存在？

```bash
# 检查字体文件
ls -la /System/Library/Fonts/Hiragino\ Sans\ GB.ttc
ls -la /System/Library/Fonts/STHeiti\ Light.ttc
```

### Q3: 如果字体文件不存在怎么办？

可以下载并安装开源中文字体，如：
- Noto Sans CJK SC (Google)
- Source Han Sans (Adobe)
- 文泉驿微米黑 (WenQuanYi Micro Hei)

安装后修改CSS中的字体路径。

### Q4: PDF文件过大怎么办？

使用字体子集化减小文件大小：

```python
from weasyprint.text.fonts import FontConfiguration

font_config = FontConfiguration()
# WeasyPrint会自动进行字体子集化，只嵌入使用的字符
```

## 总结

**核心要点：**

1. WeasyPrint生成PDF时必须使用`file://`协议指定字体的绝对路径
2. 不能使用`local()`函数或在线字体（Google Fonts）
3. 需要根据不同操作系统配置相应的字体路径
4. 建议提供多个字体作为回退方案

**修复效果：**

✅ 中文字符正常显示
✅ emoji符号正常显示
✅ 表格和代码中的中文正常显示
✅ PDF文件可搜索中文内容

## 参考资源

- [WeasyPrint官方文档](https://doc.courtbouillon.org/weasyprint/)
- [CSS @font-face规范](https://www.w3.org/TR/css-fonts-3/#font-face-rule)
- [macOS系统字体目录](https://support.apple.com/zh-cn/HT201722)

---

**修复日期：** 2025-12-18
**测试环境：** macOS (Darwin 25.1.0), Python 3.12, WeasyPrint 59.0+
