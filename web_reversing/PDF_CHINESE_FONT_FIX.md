# PDF中文字体乱码修复说明 - Web RE版本

## 问题描述

在使用Python脚本导出Web逆向工程文档PDF时，中文字符显示为乱码（问号框 `�`）。

## 修复内容

已对 `web_reversing/docs_to_pdf.py` 应用与 `android_reversing` 相同的字体修复方案。

### 修改的文件

- ✅ `docs_to_pdf.py` - 主PDF生成器（第280-306行）
- ✅ `test_chinese_font.py` - 中文字体测试脚本（新增）

### 字体配置修复

**修改前（错误）：**
```css
@font-face {
    font-family: 'Chinese Sans';
    src: local('PingFang SC'), local('Microsoft YaHei');  /* ❌ WeasyPrint不支持 */
}
```

**修改后（正确）：**
```css
@font-face {
    font-family: 'Chinese Sans';
    src: url('file:///System/Library/Fonts/Hiragino Sans GB.ttc') format('truetype'),
         url('file:///System/Library/Fonts/STHeiti Light.ttc') format('truetype'),
         url('file:///System/Library/Fonts/Supplemental/Songti.ttc') format('truetype'),
         url('file:///Library/Fonts/Arial Unicode.ttf') format('truetype');
    font-weight: normal;
}
```

## 使用的中文字体（macOS）

| 字体名称 | 文件路径 | 说明 |
|---------|---------|------|
| Hiragino Sans GB | `/System/Library/Fonts/Hiragino Sans GB.ttc` | 冬青黑体（推荐） |
| STHeiti Light | `/System/Library/Fonts/STHeiti Light.ttc` | 华文黑体细体 |
| STHeiti Medium | `/System/Library/Fonts/STHeiti Medium.ttc` | 华文黑体中等 |
| Songti SC | `/System/Library/Fonts/Supplemental/Songti.ttc` | 宋体简体 |
| Arial Unicode MS | `/Library/Fonts/Arial Unicode.ttf` | Arial Unicode（备用） |

## 如何使用

### 生成Web RE文档PDF

```bash
cd web_reversing
python3 docs_to_pdf.py
```

输出文件：`output/web_reverse_engineering_cookbook_v1.pdf`

### 运行测试

```bash
cd web_reversing
python3 test_chinese_font.py
```

生成测试PDF：`output/test_chinese_font.pdf`

## 验证修复

测试PDF包含以下内容，确保中文正常显示：

- ✅ Web 逆向工程标题
- ✅ Burp Suite 使用指南
- ✅ Chrome DevTools 调试技巧
- ✅ JavaScript 混淆与反混淆
- ✅ 表格中的中文内容
- ✅ emoji符号 (⚠️✅📁等)

## 文档特色

`web_reverse_engineering_cookbook_v1.pdf` 包含：

1. **基础知识** (Foundations)
   - HTTP协议详解
   - JavaScript基础
   - 浏览器工作原理

2. **工具使用** (Tooling)
   - Burp Suite
   - Chrome DevTools
   - Fiddler/Charles
   - Puppeteer

3. **逆向技术** (Techniques)
   - JavaScript反混淆
   - 网络协议分析
   - 加密算法识别
   - API逆向

4. **高级主题** (Advanced Topics)
   - AST分析
   - WebAssembly逆向
   - PWA安全分析

5. **工程实践** (Engineering)
   - 自动化爬虫
   - 反爬虫策略
   - 分布式架构

6. **案例研究** (Case Studies)
   - 实际案例分析
   - 常见反爬破解
   - 风控系统绕过

## 与Android RE版本的区别

| 特性 | Android RE | Web RE |
|-----|-----------|--------|
| 主题色 | 蓝色 (#4a90e2) | 绿色 (#4CAF50) |
| 封面标题 | Android Reverse Engineering | Web Reverse Engineering |
| 内容范围 | 移动应用安全 | Web应用安全 |
| 工具栈 | Frida, Xposed, IDA | Burp, DevTools, Puppeteer |

## 相关文档

- 主修复文档：`../android_reversing/PDF_CHINESE_FONT_FIX.md`
- Web RE项目说明：`README.md`
- 链接修复说明：`PDF_LINKS_FIX_README.md`

## 跨平台适配

如需在Windows或Linux上使用，请参考主修复文档中的跨平台方案：
`../android_reversing/PDF_CHINESE_FONT_FIX.md`

## 常见问题

### Q: 为什么Web RE和Android RE使用相同的字体配置？

A: 两个项目都使用WeasyPrint生成PDF，字体配置方案相同。主要区别在于文档内容和主题配色。

### Q: 生成的PDF文件很大怎么办？

A: WeasyPrint会自动进行字体子集化，只嵌入实际使用的字符。如果PDF仍然很大，可能是因为：
- 包含大量图片
- 代码示例较多
- 文档章节众多

### Q: 如何只生成部分章节？

A: 修改 `mkdocs.yml` 中的 `nav` 配置，注释掉不需要的章节。

## 修复日期

**修复日期：** 2025-12-18
**测试环境：** macOS (Darwin 25.1.0), Python 3.12, WeasyPrint 59.0+
**修复人员：** Claude Code

---

**注意：** 本修复与 `android_reversing` 项目使用相同的字体方案，确保两个项目的PDF输出一致。
