---
title: "正则表达式速查表"
date: 2025-03-05
weight: 10
---

# 正则表达式速查表

## 常用元字符

| 元字符 | 说明 | 示例 |
| ------ | ---------------------- | ---------------------------------- | ---- | -------------------- |
| `.` | 任意单个字符（除换行） | `a.c` 匹配 `abc`, `a1c` |
| `*` | 0 次或多次 | `ab*` 匹配 `a`, `ab`, `abb` |
| `+` | 1 次或多次 | `ab+` 匹配 `ab`, `abb` (不匹配`a`) |
| `?` | 0 次或 1 次 | `ab?` 匹配 `a`, `ab` |
| `^` | 行首 | `^hello` 匹配行首的 hello |
| `$` | 行尾 | `world$` 匹配行尾的 world |
| `\` | 转义字符 | `\.` 匹配点号 |
| ` | ` | 或 | `cat | dog` 匹配 cat 或 dog |
| `[]` | 字符集 | `[abc]` 匹配 a 或 b 或 c |
| `[^]` | 否定字符集 | `[^abc]` 不匹配 a,b,c |
| `()` | 分组 | `(ab)+` 匹配 ab, abab |

## 预定义字符类

| 字符类 | 等价于 | 说明 |
| ------ | ---------------- | ---------- |
| `\d` | `[0-9]` | 数字 |
| `\D` | `[^0-9]` | 非数字 |
| `\w` | `[a-zA-Z0-9_]` | 单词字符 |
| `\W` | `[^a-zA-Z0-9_]` | 非单词字符 |
| `\s` | `[ \t\n\r\f\v]` | 空白字符 |
| `\S` | `[^ \t\n\r\f\v]` | 非空白字符 |

## Web 逆向常用模式

### URL 匹配

```regex
# 完整 URL
https?://[\w\-\.]+(/[\w\-\./?%&=]*)?

# 提取域名
https?://([^/]+)

# 提取路径
https?://[^/]+(/[^?]+)

# 提取查询参数
[?&]([^=]+)=([^&]+)

# 提取所有 URL (宽松)
https?://[^\s]+
```

**Python 示例**:

```python
import re

text = "Visit https://example.com/api?key=value and http://test.com"
urls = re.findall(r'https?://[^\s]+', text)
# ['https://example.com/api?key=value', 'http://test.com']
```

### 加密特征

```regex
# MD5 (32位十六进制)
[a-f0-9]{32}

# SHA1 (40位)
[a-f0-9]{40}

# SHA256 (64位)
[a-f0-9]{64}

# Base64
[A-Za-z0-9+/]{4,}={0,2}

# JWT Token
eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+

# UUID
[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}
```

**JavaScript 示例**:

```javascript
const md5Pattern = /[a-f0-9]{32}/g;
const md5Hashes = text.match(md5Pattern);
```

### API 响应提取

```regex
# JSON 字符串值
"([^"]+)"\s*:\s*"([^"]+)"

# 提取 token
["']token["']\s*:\s*["']([^"']+)["']

# 提取数字ID
["']id["']\s*:\s*(\d+)

# 提取所有键值对
["'](\w+)["']\s*:\s*["']?([^,"']+)["']?
```

**示例**:

```python
import re
import json

response = '{"token":"abc123","user_id":12345}'

# 提取 token
token = re.search(r'"token"\s*:\s*"([^"]+)"', response).group(1)
# 'abc123'
```

### Cookie 提取

```regex
# 提取所有 Cookie
([^=]+)=([^;]+)

# 提取特定 Cookie
session_id=([^;]+)

# 提取 Cookie 属性
;\s*(\w+)=([^;]+)
```

**示例**:

```python
cookie_str = "session_id=abc123; user=admin; expires=Wed, 21 Oct 2025"
cookies = dict(re.findall(r'([^=]+)=([^;]+)', cookie_str))
# {'session_id': 'abc123', 'user': 'admin', 'expires': 'Wed, 21 Oct 2025'}
```

### JavaScript 代码模式

```regex
# 函数定义
function\s+(\w+)\s*\([^)]*\)

# 变量声明
(var|let|const)\s+(\w+)\s*=\s*([^;]+)

# 字符串字面量
["']([^"']+)["']

# 数字字面量
\b\d+\.?\d*\b

# 注释
//.*$|/\*[\s\S]*?\*/
```

### 手机号/邮箱

```regex
# 中国手机号
1[3-9]\d{9}

# 邮箱
[\w\.-]+@[\w\.-]+\.\w+

# IPv4
\b(?:\d{1,3}\.){3}\d{1,3}\b

# 身份证号
[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]
```

## JavaScript 中使用

### 基础用法

```javascript
const pattern = /pattern/flags;

// 常用方法
pattern.test(str) // 返回 true/false
str.match(pattern) // 返回匹配数组
str.replace(pattern, replacement)
pattern.exec(str) // 返回详细匹配信息
```

### Flags (标志)

| Flag | 说明 |
| ---- | ---------------------------- |
| `g` | 全局匹配 |
| `i` | 忽略大小写 |
| `m` | 多行模式 |
| `s` | dotAll 模式（.匹配所有字符） |
| `u` | Unicode 模式 |
| `y` | 粘性匹配 |

### 示例

```javascript
// 提取所有链接
const html = '<a href="/page1">Link</a><a href="/page2">Link2</a>';
const links = html.match(/href="([^"]+)"/g);
// ['href="/page1"', 'href="/page2"']

// 只提取 href 值
const hrefValues = [...html.matchAll(/href="([^"]+)"/g)].map((m) => m[1]);
// ['/page1', '/page2']
```

## Python 中使用

### re 模块

```python
import re

# 编译正则（提高性能）
pattern = re.compile(r'pattern')

# 常用方法
re.search(pattern, string) # 查找第一个匹配
re.findall(pattern, string) # 查找所有匹配
re.finditer(pattern, string) # 返回迭代器
re.sub(pattern, repl, string) # 替换
re.split(pattern, string) # 分割
```

### Flags

```python
re.IGNORECASE # 或 re.I - 忽略大小写
re.MULTILINE # 或 re.M - 多行模式
re.DOTALL # 或 re.S - .匹配所有字符
re.VERBOSE # 或 re.X - 详细模式（可以写注释）
```

### 示例

```python
# 提取加密参数
code = 'sign=md5("user"+password+"secret")'
match = re.search(r'sign=(\w+)\("([^"]+)"\+(\w+)\+"([^"]+)"\)', code)
if match:
algorithm = match.group(1) # 'md5'
param1 = match.group(2) # 'user'
param2 = match.group(3) # 'password'
secret = match.group(4) # 'secret'
```

## 高级技巧

### 非贪婪匹配

```regex
# 贪婪（尽可能多）
.*

# 非贪婪（尽可能少）
.*?

# 示例
<div>content</div><div>more</div>

# 贪婪: <div>.*</div>
# 匹配: <div>content</div><div>more</div>

# 非贪婪: <div>.*?</div>
# 匹配: <div>content</div>
```

### 前瞻和后顾

```regex
# 正向前瞻 (?=pattern)
\w+(?=\d) # 匹配后面跟数字的单词

# 负向前瞻 (?!pattern)
\w+(?!\d) # 匹配后面不跟数字的单词

# 正向后顾 (?<=pattern)
(?<=\$)\d+ # 匹配前面有$符号的数字

# 负向后顾 (?<!pattern)
(?<!\$)\d+ # 匹配前面没有$符号的数字
```

### 命名分组

```python
# Python
pattern = r'(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})'
match = re.search(pattern, '2024-01-15')
print(match.group('year')) # '2024'
print(match.group('month')) # '01'
```

```javascript
// JavaScript
const pattern = /(?<year>\d{4})-(?<month>\d{2})-(?<day>\d{2})/;
const match = "2024-01-15".match(pattern);
console.log(match.groups.year); // '2024'
```

## 在线测试工具

- **Regex101**: <https://regex101.com/> (推荐，有详细说明)
- **RegExr**: <https://regexr.com/>
- **RegexPal**: <https://www.regexpal.com/>

## 实战示例集

### 1. 提取 JavaScript 函数调用

```regex
(\w+)\s*\(([^)]*)\)
```

```python
code = "encrypt('password', 'key'); hash(data)"
calls = re.findall(r'(\w+)\s*\(([^)]*)\)', code)
# [('encrypt', "'password', 'key'"), ('hash', 'data')]
```

### 2. 清理 HTML 标签

```python
html = "<p>Hello <strong>World</strong></p>"
text = re.sub(r'<[^>]+>', '', html)
# "Hello World"
```

### 3. 验证时间戳格式

```regex
# 13位时间戳（毫秒）
\b1\d{12}\b

# 10位时间戳（秒）
\b1\d{9}\b
```

### 4. 提取混淆变量名

```regex
# 提取 _0x 开头的变量
_0x[a-f0-9]+
```

```python
code = "var _0x1234 = function(_0xabcd) { return _0xabcd + _0x5678; }"
vars = re.findall(r'_0x[a-f0-9]+', code)
# ['_0x1234', '_0xabcd', '_0xabcd', '_0x5678']
```

## 性能优化

### 避免回溯

```regex
# 慢（大量回溯）
(a+)*b

# 快（使用原子组）
(?>a+)*b
```

### 编译正则

```python
# 如果要多次使用，先编译
pattern = re.compile(r'complex_pattern')
for text in texts:
matches = pattern.findall(text) # 更快
```

## 相关章节

- [常用命令](./common_commands.md)
- [JavaScript 反混淆](../04-Advanced-Recipes/javascript_deobfuscation.md)
- [API 逆向](../03-Basic-Recipes/api_reverse_engineering.md)
