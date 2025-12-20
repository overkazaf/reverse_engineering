# 数据处理问题

数据采集、解析和存储中的常见问题及解决方案。

---

## 编码错误

### UnicodeDecodeError

**问题表现**:

```python
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 0
```

**原因**: 文件或数据使用了不同的编码格式

**解决方案**:

#### 1. 自动检测编码

```python
import chardet

# 检测文件编码
with open('file.txt', 'rb') as f:
    raw_data = f.read()
    result = chardet.detect(raw_data)
    encoding = result['encoding']
    confidence = result['confidence']

print(f"Encoding: {encoding} (Confidence: {confidence})")

# 使用检测到的编码读取
with open('file.txt', 'r', encoding=encoding) as f:
    content = f.read()
```

#### 2. 处理网页编码

```python
import requests
from chardet import detect

response = requests.get(url)

# 方法 1: 让 requests 自动检测
response.encoding = response.apparent_encoding
text = response.text

# 方法 2: 手动检测
encoding = detect(response.content)['encoding']
text = response.content.decode(encoding, errors='ignore')

# 方法 3: 尝试常见编码
encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'big5']
for enc in encodings:
    try:
        text = response.content.decode(enc)
        break
    except UnicodeDecodeError:
        continue
```

#### 3. 忽略错误字符

```python
# 忽略无法解码的字符
text = data.decode('utf-8', errors='ignore')

# 或替换为 ?
text = data.decode('utf-8', errors='replace')

# 或使用替代方案
text = data.decode('utf-8', errors='backslashreplace')
```

### UnicodeEncodeError

**问题表现**:

```python
UnicodeEncodeError: 'ascii' codec can't encode character '\u4e2d'
```

**解决方案**:

```python
# 写入文件时指定编码
with open('output.txt', 'w', encoding='utf-8') as f:
    f.write(chinese_text)

# 打印到控制台 (Windows)
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# JSON 输出保留中文
import json
json.dumps(data, ensure_ascii=False, indent=2)
```

---

## JSON 解析失败

### JSONDecodeError

**问题表现**:

```python
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

**原因分析**:

1. 响应不是 JSON 格式
2. JSON 格式错误
3. 空响应
4. HTML 错误页面

**解决方案**:

#### 1. 检查响应内容

```python
import requests
import json

response = requests.get(url)

# 先检查状态码
if response.status_code != 200:
    print(f"Error: {response.status_code}")
    print(response.text)
    exit()

# 检查 Content-Type
content_type = response.headers.get('Content-Type', '')
if 'application/json' not in content_type:
    print(f"Warning: Content-Type is {content_type}")

# 安全解析
try:
    data = response.json()
except json.JSONDecodeError as e:
    print(f"JSON Parse Error: {e}")
    print(f"Response text: {response.text[:500]}")  # 打印前500字符
    data = None
```

#### 2. 处理畸形 JSON

```python
import json5  # pip install json5

# json5 可以解析带注释、尾随逗号的 JSON
text = '''
{
    "name": "value",  // 注释
    "items": [1, 2, 3,],  // 尾随逗号
}
'''

data = json5.loads(text)
```

#### 3. 修复常见 JSON 问题

```python
import re
import json

def fix_json(text):
    """修复常见的 JSON 问题"""
    # 移除 JavaScript 注释
    text = re.sub(r'//.*?\n', '\n', text)
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)

    # 移除尾随逗号
    text = re.sub(r',\s*}', '}', text)
    text = re.sub(r',\s*]', ']', text)

    # 单引号转双引号 (谨慎使用)
    # text = text.replace("'", '"')

    return text

# 使用
text = response.text
fixed_text = fix_json(text)
data = json.loads(fixed_text)
```

#### 4. 从 HTML 中提取 JSON

```python
import re
import json
from bs4 import BeautifulSoup

html = response.text

# 方法 1: 从 script 标签提取
soup = BeautifulSoup(html, 'lxml')
script = soup.find('script', {'id': 'initial-data'})
if script:
    data = json.loads(script.string)

# 方法 2: 使用正则提取
match = re.search(r'var\s+data\s*=\s*({.*?});', html, re.DOTALL)
if match:
    json_str = match.group(1)
    data = json.loads(json_str)

# 方法 3: 提取 JSON-LD
script = soup.find('script', {'type': 'application/ld+json'})
if script:
    data = json.loads(script.string)
```

---

## 数据库连接问题

### MongoDB 连接失败

**问题表现**:

```python
ServerSelectionTimeoutError: localhost:27017: [Errno 111] Connection refused
```

**解决方案**:

```python
import pymongo
from pymongo.errors import ServerSelectionTimeoutError

# 添加超时和错误处理
try:
    client = pymongo.MongoClient(
        'mongodb://localhost:27017/',
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        socketTimeoutMS=5000
    )

    # 测试连接
    client.server_info()
    print("✅ MongoDB connected")

except ServerSelectionTimeoutError as e:
    print(f"❌ MongoDB connection failed: {e}")
    print("提示:")
    print("1. 检查 MongoDB 是否运行: systemctl status mongod")
    print("2. 检查端口: netstat -an | grep 27017")
    print("3. 检查防火墙设置")
    exit()
```

#### 认证问题

```python
# 带认证的连接
client = pymongo.MongoClient(
    'mongodb://username:password@localhost:27017/',
    authSource='admin',  # 认证数据库
    authMechanism='SCRAM-SHA-256'  # 认证机制
)

# 或使用 URI 格式
uri = 'mongodb://username:password@host1:27017,host2:27017/database?authSource=admin'
client = pymongo.MongoClient(uri)
```

### MySQL 连接问题

**问题表现**:

```python
Error 2003: Can't connect to MySQL server on 'localhost'
```

**解决方案**:

```python
import mysql.connector
from mysql.connector import Error

try:
    connection = mysql.connector.connect(
        host='localhost',
        port=3306,
        database='testdb',
        user='root',
        password='password',
        connect_timeout=10,
        autocommit=True,
        charset='utf8mb4'
    )

    if connection.is_connected():
        db_info = connection.get_server_info()
        print(f"✅ Connected to MySQL Server version {db_info}")

except Error as e:
    print(f"❌ Error: {e}")
    print("检查项:")
    print("1. MySQL 服务是否运行")
    print("2. 用户名密码是否正确")
    print("3. 是否允许远程连接")
    print("4. 防火墙设置")

finally:
    if connection and connection.is_connected():
        connection.close()
```

### Redis 连接问题

**解决方案**:

```python
import redis
from redis.exceptions import ConnectionError

try:
    r = redis.Redis(
        host='localhost',
        port=6379,
        password='password',  # 如果有密码
        db=0,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5
    )

    # 测试连接
    r.ping()
    print("✅ Redis connected")

except ConnectionError as e:
    print(f"❌ Redis connection failed: {e}")
except redis.AuthenticationError:
    print("❌ Redis authentication failed")
```

---

## 文件读写错误

### 文件不存在

**问题表现**:

```python
FileNotFoundError: [Errno 2] No such file or directory: 'data.txt'
```

**解决方案**:

```python
import os
from pathlib import Path

# 方法 1: 检查文件是否存在
file_path = 'data.txt'
if os.path.exists(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
else:
    print(f"File not found: {file_path}")

# 方法 2: 使用 Path 对象
file_path = Path('data.txt')
if file_path.exists():
    content = file_path.read_text(encoding='utf-8')

# 方法 3: 创建目录
output_dir = Path('output/data')
output_dir.mkdir(parents=True, exist_ok=True)

# 方法 4: 使用绝对路径
from pathlib import Path
base_dir = Path(__file__).resolve().parent
file_path = base_dir / 'data' / 'file.txt'
```

### 权限错误

**问题表现**:

```python
PermissionError: [Errno 13] Permission denied: '/var/log/app.log'
```

**解决方案**:

```bash
# Linux/Mac
# 1. 修改文件权限
chmod 666 /var/log/app.log

# 2. 修改目录权限
chmod 777 /var/log/

# 3. 修改所有者
sudo chown $USER:$USER /var/log/app.log

# 4. 使用用户目录
# 在代码中使用 ~/data/ 而不是 /var/log/
```

```python
# 使用用户目录
from pathlib import Path

home = Path.home()
log_dir = home / '.myapp' / 'logs'
log_dir.mkdir(parents=True, exist_ok=True)

log_file = log_dir / 'app.log'
```

---

## 内存问题

### 内存溢出

**问题表现**:

```python
MemoryError
```

**解决方案**:

#### 1. 分批处理大文件

```python
# 不要一次性读取整个文件
# ❌ 错误方式
with open('huge_file.txt', 'r') as f:
    content = f.read()  # 可能导致内存溢出

# ✅ 正确方式:按行读取
with open('huge_file.txt', 'r') as f:
    for line in f:
        process_line(line)

# 或使用生成器
def read_large_file(file_path, chunk_size=1024*1024):
    """分块读取大文件"""
    with open(file_path, 'r') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk

for chunk in read_large_file('huge_file.txt'):
    process_chunk(chunk)
```

#### 2. 使用迭代器

```python
# ❌ 一次性加载所有数据
urls = [f"https://example.com/page/{i}" for i in range(100000)]

# ✅ 使用生成器
def url_generator(count):
    for i in range(count):
        yield f"https://example.com/page/{i}"

for url in url_generator(100000):
    process_url(url)
```

#### 3. 清理不用的对象

```python
import gc

# 手动触发垃圾回收
gc.collect()

# 删除大对象
del large_dataframe
gc.collect()
```

#### 4. 使用数据库而非内存

```python
# ❌ 所有数据存在内存中
all_data = []
for item in items:
    all_data.append(process(item))

# ✅ 直接存入数据库
import sqlite3

conn = sqlite3.connect('data.db')
cursor = conn.cursor()

for item in items:
    data = process(item)
    cursor.execute("INSERT INTO results VALUES (?, ?)", (data.id, data.value))
    conn.commit()
```

---

## CSV 处理问题

### 编码和分隔符

```python
import csv
import chardet

# 检测编码
with open('data.csv', 'rb') as f:
    result = chardet.detect(f.read())
    encoding = result['encoding']

# 读取 CSV
with open('data.csv', 'r', encoding=encoding) as f:
    # 自动检测分隔符
    sample = f.read(1024)
    f.seek(0)
    sniffer = csv.Sniffer()
    delimiter = sniffer.sniff(sample).delimiter

    reader = csv.DictReader(f, delimiter=delimiter)
    for row in reader:
        print(row)
```

### 处理大型 CSV

```python
import pandas as pd

# 分块读取
chunk_size = 10000
for chunk in pd.read_csv('large.csv', chunksize=chunk_size):
    process_chunk(chunk)

# 只读取需要的列
df = pd.read_csv('data.csv', usecols=['col1', 'col2'])

# 指定数据类型节省内存
df = pd.read_csv('data.csv', dtype={'id': 'int32', 'value': 'float32'})
```

---

## XML/HTML 解析问题

### 解析失败

```python
from bs4 import BeautifulSoup
from lxml import etree

html = response.text

# 方法 1: BeautifulSoup (宽容)
soup = BeautifulSoup(html, 'lxml')  # 或 'html.parser'

# 方法 2: lxml (严格)
try:
    tree = etree.HTML(html)
except etree.XMLSyntaxError as e:
    print(f"Parse error: {e}")

# 处理畸形 HTML
from lxml.html import fromstring
from lxml.html.clean import Cleaner

cleaner = Cleaner()
cleaned_html = cleaner.clean_html(html)
doc = fromstring(cleaned_html)
```

---

## 数据验证

### 使用 Pydantic

```python
from pydantic import BaseModel, validator, ValidationError
from typing import Optional

class Item(BaseModel):
    id: int
    name: str
    price: float
    stock: Optional[int] = 0

    @validator('price')
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        return v

# 验证数据
try:
    item = Item(id=1, name='Product', price=19.99)
except ValidationError as e:
    print(e.json())
```

---

## 📚 相关章节

- [数据存储方案](../06-Engineering/data_storage_solutions.md)
- [Python 编码问题](../01-Foundations/javascript_basics.md)
- [常用命令](../08-Cheat-Sheets/common_commands.md)
