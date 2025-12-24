---
title: "常用命令速查表"
date: 2025-12-25
weight: 10
---

# 常用命令速查表

## Chrome DevTools Console 命令

### 选择元素

| 命令 | 说明 | 示例 |
| ------ | ------------------------------------ | --------------------------------- |
| `$()` | 等同于 `document.querySelector()` | `$('#username')` |
| `$$()` | 等同于 `document.querySelectorAll()` | `$$('.item')` |
| `$x()` | XPath 选择器 | `$x('//div[@class="container"]')` |
| `$0` | 当前选中的元素 | `$0.innerHTML` |
| `$1` | 上一个选中的元素 | `$1.classList` |

### 实用函数

| 命令 | 说明 | 示例 |
| ------------- | ------------------ | ---------------------------- |
| `copy()` | 复制到剪贴板 | `copy($0)` |
| `clear()` | 清空 Console | `clear()` |
| `keys()` | 获取对象所有键 | `keys(window)` |
| `values()` | 获取对象所有值 | `values(localStorage)` |
| `monitor()` | 监控函数调用 | `monitor(fetch)` |
| `unmonitor()` | 取消监控 | `unmonitor(fetch)` |
| `table()` | 表格显示数据 | `table([{name:'a',age:20}])` |
| `debug()` | 在函数第一行设断点 | `debug(myFunction)` |
| `undebug()` | 移除断点 | `undebug(myFunction)` |

### 网络相关

```javascript
// 查看所有 Cookie
document.cookie;

// 清空所有 Cookie
document.cookie.split(";").forEach((c) => {
document.cookie = c
.replace(/^ +/, "")
.replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/");
});

// 查看 LocalStorage
Object.keys(localStorage);

// 清空 LocalStorage
localStorage.clear();

// 发送 GET 请求
fetch("https://api.example.com/data")
.then((r) => r.json())
.then(console.log);

// 发送 POST 请求
fetch("https://api.example.com/login", {
method: "POST",
headers: { "Content-Type": "application/json" },
body: JSON.stringify({ username: "admin", password: "123456" }),
})
.then((r) => r.json())
.then(console.log);
```

---

## Python 常用库

### Requests

```python
import requests

# GET 请求
response = requests.get('https://example.com')
print(response.text)

# POST 请求
response = requests.post('https://example.com/api', json={
'username': 'admin',
'password': '123456'
})
print(response.json())

# 设置 Headers
headers = {
'User-Agent': 'Mozilla/5.0 ...',
'Authorization': 'Bearer token123'
}
response = requests.get('https://example.com', headers=headers)

# 使用代理
proxies = {
'http': 'http://127.0.0.1:8080',
'https': 'http://127.0.0.1:8080'
}
response = requests.get('https://example.com', proxies=proxies)

# Session 保持
session = requests.Session()
session.get('https://example.com/login')
session.post('https://example.com/api', json={'key': 'value'})
```

### BeautifulSoup

```python
from bs4 import BeautifulSoup

# 解析 HTML
soup = BeautifulSoup(html, 'html.parser')

# 查找元素
soup.find('div', class_='content') # 查找第一个
soup.find_all('a') # 查找所有
soup.select('.class #id tag') # CSS 选择器

# 获取属性
element = soup.find('a')
element.get('href') # 获取 href
element.text # 获取文本
element.get_text(strip=True) # 获取文本（去空格）
```

### Regex (re)

```python
import re

# 查找
match = re.search(r'pattern', text)
matches = re.findall(r'pattern', text)

# 替换
result = re.sub(r'old', 'new', text)

# 编译（提高性能）
pattern = re.compile(r'pattern')
matches = pattern.findall(text)
```

---

## cURL 命令

### 基本用法

```bash
# GET 请求
curl https://example.com

# POST 请求
curl -X POST https://example.com/api \
-H "Content-Type: application/json" \
-d '{"username":"admin","password":"123456"}'

# 设置 User-Agent
curl -A "Mozilla/5.0 ..." https://example.com

# 保存 Cookie
curl -c cookies.txt https://example.com

# 使用 Cookie
curl -b cookies.txt https://example.com

# 跟随重定向
curl -L https://example.com

# 显示响应头
curl -i https://example.com

# 只显示响应头
curl -I https://example.com

# 使用代理
curl -x http://127.0.0.1:8080 https://example.com

# 忽略 SSL 证书
curl -k https://example.com

# 上传文件
curl -F "file=@/path/to/file" https://example.com/upload
```

### 调试用法

```bash
# 显示详细信息
curl -v https://example.com

# 显示时间统计
curl -w "@curl-format.txt" -o /dev/null -s https://example.com

# curl-format.txt 内容:
# time_namelookup: %{time_namelookup}\n
# time_connect: %{time_connect}\n
# time_appconnect: %{time_appconnect}\n
# time_redirect: %{time_redirect}\n
# time_pretransfer: %{time_pretransfer}\n
# time_starttransfer: %{time_starttransfer}\n
# ----------\n
# time_total: %{time_total}\n
```

---

## Git 常用命令

### 基础操作

```bash
# 查看状态
git status

# 添加文件
git add .
git add file.txt

# 提交
git commit -m "message"

# 推送
git push origin master

# 拉取
git pull origin master

# 查看历史
git log
git log --oneline --graph

# 回退
git reset --hard HEAD^ # 回退一个版本
git reset --hard commit_id # 回退到指定版本
```

### 分支操作

```bash
# 创建分支
git branch feature-name

# 切换分支
git checkout feature-name

# 创建并切换
git checkout -b feature-name

# 合并分支
git merge feature-name

# 删除分支
git branch -d feature-name
```

### 查看差异

```bash
# 查看修改
git diff

# 查看已暂存的修改
git diff --staged

# 查看两个提交的差异
git diff commit1 commit2
```

---

## Node.js / npm

### 包管理

```bash
# 安装包
npm install package-name
npm install -g package-name # 全局安装
npm install --save-dev package # 开发依赖

# 卸载包
npm uninstall package-name

# 更新包
npm update package-name

# 查看已安装的包
npm list
npm list -g

# 查看包信息
npm info package-name
```

### 常用脚本

```bash
# 运行脚本
npm run script-name

# 常见的预定义脚本
npm start
npm test
npm run build
```

---

## Bash 文本处理

### grep

```bash
# 搜索文本
grep "pattern" file.txt

# 忽略大小写
grep -i "pattern" file.txt

# 递归搜索
grep -r "pattern" directory/

# 显示行号
grep -n "pattern" file.txt

# 反向匹配（不包含）
grep -v "pattern" file.txt

# 正则表达式
grep -E "regex pattern" file.txt
```

### sed

```bash
# 替换文本
sed 's/old/new/' file.txt # 替换每行第一个
sed 's/old/new/g' file.txt # 替换所有
sed -i 's/old/new/g' file.txt # 直接修改文件

# 删除行
sed '/pattern/d' file.txt # 删除匹配的行
sed '1d' file.txt # 删除第一行
sed '1,10d' file.txt # 删除1-10行
```

### awk

```bash
# 打印列
awk '{print $1}' file.txt # 打印第一列
awk '{print $1,$3}' file.txt # 打印第1和第3列

# 条件过滤
awk '$3 > 100' file.txt # 第3列大于100的行

# 求和
awk '{sum+=$1} END {print sum}' file.txt
```

---

## Docker 常用命令

### 镜像操作

```bash
# 拉取镜像
docker pull image-name

# 查看镜像
docker images

# 删除镜像
docker rmi image-name

# 构建镜像
docker build -t image-name .
```

### 容器操作

```bash
# 运行容器
docker run -d --name container-name image-name
docker run -it image-name /bin/bash # 交互式

# 查看容器
docker ps # 运行中的
docker ps -a # 所有的

# 停止容器
docker stop container-name

# 启动容器
docker start container-name

# 删除容器
docker rm container-name

# 查看日志
docker logs container-name

# 进入容器
docker exec -it container-name /bin/bash
```

---

## 快速参考

### 编码/解码

```python
# Base64
import base64
encoded = base64.b64encode(b'text')
decoded = base64.b64decode(encoded)

# URL编码
from urllib.parse import quote, unquote
encoded = quote('text with spaces')
decoded = unquote(encoded)

# JSON
import json
json_str = json.dumps({'key': 'value'})
obj = json.loads(json_str)
```

### 时间戳

```python
import time
import datetime

# 当前时间戳（秒）
timestamp = int(time.time())

# 当前时间戳（毫秒）
timestamp_ms = int(time.time() * 1000)

# 时间戳转日期
dt = datetime.datetime.fromtimestamp(timestamp)
print(dt.strftime('%Y-%m-%d %H:%M:%S'))

# 日期转时间戳
dt = datetime.datetime(2024, 1, 1, 12, 0, 0)
timestamp = int(dt.timestamp())
```

```javascript
// JavaScript
const timestamp = Date.now(); // 毫秒
const timestampSec = Math.floor(Date.now() / 1000); // 秒

// 时间戳转日期
const date = new Date(timestamp);
console.log(date.toLocaleString());
```

---

## 相关章节

- [加密算法特征](./crypto_signatures.md) - 加密算法识别
- [正则表达式](./regex_patterns.md) - 常用正则模式
- [HTTP 头速查](./http_headers.md) - HTTP 请求头
