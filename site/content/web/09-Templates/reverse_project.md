---
title: "逆向分析项目模板"
date: 2025-01-31
type: posts
tags: ["Web", "项目", "签名验证", "代理池", "加密分析", "Hook"]
weight: 10
---

# 逆向分析项目模板

Web 逆向分析的标准项目模板，帮助你系统化地进行网站分析和文档记录。

---

## 项目结构

```
reverse_project/
├── docs/
│ ├── analysis.md # 分析文档
│ ├── api_reference.md # API 接口文档
│ ├── crypto_analysis.md # 加密分析
│ └── findings.md # 发现和总结
├── scripts/
│ ├── __init__.py
│ ├── decrypt.py # 解密脚本
│ ├── sign.py # 签名生成
│ └── reproduce.py # 完整复现
├── hooks/
│ ├── network_monitor.js # 网络监控
│ ├── crypto_hook.js # 加密函数Hook
│ └── debugger_bypass.js # 反调试绕过
├── test_cases/
│ ├── test_decrypt.py # 解密测试
│ ├── test_sign.py # 签名测试
│ └── test_api.py # API 测试
├── data/
│ ├── samples/ # 样本数据
│ └── results/ # 分析结果
├── assets/
│ ├── screenshots/ # 截图
│ └── diagrams/ # 流程图
├── requirements.txt
├── README.md
└── .env.example
```

---

## 文件模板

### 1. docs/analysis.md

````markdown
# [网站名称] 逆向分析

## 基本信息

| 项目 | 说明 |
| ------------ | ----------------------------------- |
| **目标网站** | https://example.com |
| **分析日期** | 2024-01-15 |
| **难度等级** | ⭐⭐⭐ |
| **主要技术** | JavaScript 混淆、AES 加密、签名验证 |

---

## 目标

- ☐ 分析登录接口加密逻辑
- ☐ 破解 API 签名算法
- ☐ 实现完整的 Python 复现
- ☐ 编写自动化爬虫

---

## 技术栈分析

### 前端技术

- **框架**: Vue.js 3.x
- **打包工具**: Webpack 5
- **混淆**: JavaScript Obfuscator

### 后端技术

- **服务器**: Nginx + Node.js
- **API 格式**: RESTful JSON
- **认证方式**: JWT Token

---

## 分析流程

### 1. 初步侦察

**工具**: Chrome DevTools

1. 打开网站，检查网络请求
2. 识别关键 API 接口
3. 观察请求参数和响应格式

**发现**:

- 登录接口: `/api/auth/login`
- 主要参数: `username`, `password`, `timestamp`, `sign`

### 2. JavaScript 分析

**入口文件**: `app.js`

关键代码位置:

```javascript
// 位置: app.js:1234
function encryptPassword(password) {
// AES 加密实现
}

// 位置: app.js:5678
function generateSign(params) {
// 签名生成逻辑
}
```
````

### 3. 加密算法识别

详见 [crypto_analysis.md](./crypto_analysis.md)

### 4. 复现实现

详见 [自动化脚本](../07-Scripts/automation_scripts.md)

---

## 时间线

| 日期 | 进展 |
| ---------- | -------------------------- |
| 2024-01-15 | 完成初步侦察 |
| 2024-01-16 | 识别加密算法为 AES-128-CBC |
| 2024-01-17 | 破解签名算法 |
| 2024-01-18 | Python 复现成功 |

---

## 参考资源

- [官方文档](https://example.com/docs)
- [相关讨论](https://github.com/...)

````

### 2. docs/crypto_analysis.md

```markdown
# 加密分析文档

## 密码加密

### 算法识别

**特征**:
- 输出长度: 32 字符（Base64 编码）
- 固定 IV: `1234567890abcdef`

**结论**: AES-128-CBC

### 关键代码

```javascript
// 原始代码 (app.js:1234)
function encryptPassword(password) {
const key = CryptoJS.enc.Utf8.parse('secretkey1234567');
const iv = CryptoJS.enc.Utf8.parse('1234567890abcdef');

const encrypted = CryptoJS.AES.encrypt(password, key, {
iv: iv,
mode: CryptoJS.mode.CBC,
padding: CryptoJS.pad.Pkcs7
});

return encrypted.toString();
}
````

### Python 实现

```python
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64

def encrypt_password(password):
key = b'secretkey1234567'
iv = b'1234567890abcdef'

cipher = AES.new(key, AES.MODE_CBC, iv)
encrypted = cipher.encrypt(pad(password.encode(), 16))

return base64.b64encode(encrypted).decode()

# 测试
print(encrypt_password('mypassword'))
```

---

## 签名算法

### 算法识别

**特征**:

- 输出长度: 32 字符
- 十六进制格式

**结论**: MD5

### 签名规则

```
sign = MD5(param1 + param2 + timestamp + secret_key)
```

**参数顺序**: 按字典序排列

### 完整实现

```python
import hashlib
import time

def generate_sign(params):
# 添加时间戳
params['timestamp'] = int(time.time() * 1000)

# 按字典序排序
sorted_params = sorted(params.items())

# 拼接字符串
sign_str = ''.join([f'{k}{v}' for k, v in sorted_params])

# 添加密钥
sign_str += 'secret_key_here'

# MD5 哈希
return hashlib.md5(sign_str.encode()).hexdigest()

# 测试
params = {
'username': 'admin',
'password': 'encrypted_password_here'
}
print(generate_sign(params))
```

---

## Token 机制

### JWT 结构

```
Header.Payload.Signature
```

**示例**:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjM0NX0.xyz...
```

### 解码

```python
import jwt

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
decoded = jwt.decode(token, verify=False)
print(decoded)
# {'user_id': 12345, 'exp': 1705305600}
```

---

## 反爬措施

### 1. User-Agent 检测

- **措施**: 必须包含真实浏览器 UA
- **绕过**: 使用真实 Chrome UA

### 2. 频率限制

- **措施**: 每分钟最多 60 请求
- **绕过**: 添加随机延迟 (1-3 秒)

### 3. IP 封禁

- **措施**: 同一 IP 过多请求会被封
- **绕过**: 使用代理池轮换

````

### 3. scripts/reproduce.py

```python
"""
完整复现脚本
"""
import requests
import hashlib
import time
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64
import json


class TargetAPI:
"""目标网站 API 封装"""

def __init__(self):
self.base_url = "https://example.com"
self.session = requests.Session()
self.token = None

# 设置请求头
self.session.headers.update({
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
'Content-Type': 'application/json',
'Accept': 'application/json',
})

def encrypt_password(self, password: str) -> str:
"""
AES 加密密码

Args:
password: 明文密码

Returns:
加密后的 Base64 字符串
"""
key = b'secretkey1234567'
iv = b'1234567890abcdef'

cipher = AES.new(key, AES.MODE_CBC, iv)
encrypted = cipher.encrypt(pad(password.encode(), 16))

return base64.b64encode(encrypted).decode()

def generate_sign(self, params: dict) -> dict:
"""
生成签名

Args:
params: 请求参数

Returns:
添加了 timestamp 和 sign 的参数字典
"""
# 添加时间戳
params['timestamp'] = int(time.time() * 1000)

# 按字典序排序
sorted_params = sorted(params.items())

# 拼接字符串
sign_str = ''.join([f'{k}{v}' for k, v in sorted_params])

# 添加密钥
sign_str += 'secret_key_here'

# MD5 哈希
params['sign'] = hashlib.md5(sign_str.encode()).hexdigest()

return params

def login(self, username: str, password: str) -> bool:
"""
登录

Args:
username: 用户名
password: 密码

Returns:
是否登录成功
"""
# 加密密码
encrypted_password = self.encrypt_password(password)

# 准备参数
params = {
'username': username,
'password': encrypted_password
}

# 生成签名
params = self.generate_sign(params)

# 发送请求
url = f"{self.base_url}/api/auth/login"
response = self.session.post(url, json=params)

if response.status_code == 200:
data = response.json()
if data.get('code') == 0:
self.token = data['data']['token']
self.session.headers['Authorization'] = f'Bearer {self.token}'
print(f"✅ 登录成功! Token: {self.token[:20]}...")
return True

print(f"❌ 登录失败: {response.text}")
return False

def get_user_info(self) -> dict:
"""
获取用户信息

Returns:
用户信息字典
"""
if not self.token:
raise Exception("未登录，请先调用 login()")

url = f"{self.base_url}/api/user/info"
response = self.session.get(url)

if response.status_code == 200:
return response.json()

return None

def get_data(self, page: int = 1, size: int = 20) -> list:
"""
获取数据列表

Args:
page: 页码
size: 每页数量

Returns:
数据列表
"""
if not self.token:
raise Exception("未登录，请先调用 login()")

params = {
'page': page,
'size': size
}

# 生成签名
params = self.generate_sign(params)

url = f"{self.base_url}/api/data/list"
response = self.session.get(url, params=params)

if response.status_code == 200:
data = response.json()
return data.get('data', {}).get('items', [])

return []


def main():
"""主函数"""
print("=" * 50)
print("目标网站 API 复现测试")
print("=" * 50)

# 创建 API 实例
api = TargetAPI()

# 登录
if api.login('your_username', 'your_password'):
# 获取用户信息
user_info = api.get_user_info()
print(f"\n用户信息: {json.dumps(user_info, indent=2, ensure_ascii=False)}")

# 获取数据
data = api.get_data(page=1, size=10)
print(f"\n获取到 {len(data)} 条数据")

# 保存数据
with open('data/results/output.json', 'w', encoding='utf-8') as f:
json.dump(data, f, ensure_ascii=False, indent=2)

print("\n✅ 数据已保存到 data/results/output.json")


if __name__ == '__main__':
main()
````

### 4. test_cases/test_decrypt.py

```python
"""
解密功能测试
"""
import unittest
from scripts.reproduce import TargetAPI


class TestDecrypt(unittest.TestCase):
"""解密测试用例"""

def setUp(self):
"""初始化"""
self.api = TargetAPI()

def test_encrypt_password(self):
"""测试密码加密"""
password = "test123"
encrypted = self.api.encrypt_password(password)

# 验证输出格式
self.assertIsInstance(encrypted, str)
self.assertGreater(len(encrypted), 0)

# 验证 Base64 格式
import base64
try:
base64.b64decode(encrypted)
is_base64 = True
except:
is_base64 = False

self.assertTrue(is_base64)

print(f"✅ 加密测试通过: {password} -> {encrypted}")

def test_sign_generation(self):
"""测试签名生成"""
params = {
'username': 'test',
'password': 'encrypted_pass'
}

signed_params = self.api.generate_sign(params.copy())

# 验证签名字段存在
self.assertIn('sign', signed_params)
self.assertIn('timestamp', signed_params)

# 验证签名格式 (32位 MD5)
self.assertEqual(len(signed_params['sign']), 32)
self.assertTrue(signed_params['sign'].isalnum())

print(f"✅ 签名测试通过: {signed_params['sign']}")

def test_sign_consistency(self):
"""测试签名一致性"""
params = {
'username': 'test',
'password': 'encrypted_pass',
'timestamp': 1234567890000
}

# 同样的参数应该生成同样的签名
sign1 = self.api.generate_sign(params.copy())['sign']
sign2 = self.api.generate_sign(params.copy())['sign']

self.assertEqual(sign1, sign2)

print(f"✅ 签名一致性测试通过")


if __name__ == '__main__':
unittest.main()
```

### 5. README.md

````markdown
# [网站名称] 逆向分析项目

本项目是对 [目标网站] 的完整逆向分析和 Python 复现实现。

---

## 项目概述

**目标**: 分析并复现目标网站的登录、数据获取等核心功能

**主要成果**:

- ✅ 破解 AES-128-CBC 密码加密
- ✅ 逆向 MD5 签名算法
- ✅ 实现完整的 Python API 封装
- ✅ 编写详细的分析文档

---

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```
````

### 2. 配置参数

```bash
cp .env.example .env
# 编辑 .env 文件，填入账号密码
```

### 3. 运行复现脚本

```bash
python scripts/reproduce.py
```

---

## 项目结构

```
.
├── docs/ # 分析文档
├── scripts/ # 复现脚本
├── hooks/ # Hook 脚本
├── test_cases/ # 测试用例
├── data/ # 数据目录
└── assets/ # 资源文件
```

---

## 分析文档

详细的分析过程见:

- [完整分析文档](./docs/analysis.md)
- [加密算法分析](./docs/crypto_analysis.md)
- [API 接口文档](./docs/api_reference.md)

---

## 主要技术

- **加密**: AES-128-CBC
- **签名**: MD5 哈希
- **认证**: JWT Token
- **反混淆**: AST 解析

---

## 使用示例

```python
from scripts.reproduce import TargetAPI

# 创建 API 实例
api = TargetAPI()

# 登录
api.login('username', 'password')

# 获取数据
data = api.get_data(page=1, size=20)

print(f"获取到 {len(data)} 条数据")
```

---

## 运行测试

```bash
python -m pytest test_cases/
```

---

## 注意事项

1. 本项目仅供学习研究使用
2. 请遵守目标网站的使用条款
3. 不要用于非法用途
4. 建议添加请求延迟，避免对服务器造成压力

---

## License

MIT

````

### 6. requirements.txt

```txt
requests>=2.31.0
pycryptodome>=3.19.0
pyjwt>=2.8.0
beautifulsoup4>=4.12.0
pytest>=7.4.0
python-dotenv>=1.0.0
````

### 7. .env.example

```bash
# 目标网站账号
USERNAME=your_username
PASSWORD=your_password

# 请求配置
REQUEST_TIMEOUT=30
MAX_RETRIES=3

# 代理配置 (可选)
USE_PROXY=false
PROXY_URL=http://127.0.0.1:7890
```

---

## 使用此模板

```bash
# 1. 复制模板
cp -r templates/reverse_project my_analysis
cd my_analysis

# 2. 初始化文档
vim docs/analysis.md # 开始记录分析过程

# 3. 编写复现脚本
vim scripts/reproduce.py

# 4. 运行测试
python -m pytest test_cases/
```

---

## 最佳实践

### 分析流程建议

1. **初步侦察** (1-2 小时)

- 使用 DevTools 观察网络请求
- 识别关键 API 接口
- 记录请求参数格式

2. **JavaScript 分析** (2-4 小时)

- 定位加密相关代码
- 使用断点调试
- 记录关键函数位置

3. **算法识别** (1-2 小时)

- 根据特征识别加密算法
- 测试验证猜测
- 提取密钥和参数

4. **Python 复现** (2-3 小时)

- 实现加密函数
- 实现签名函数
- 封装完整 API

5. **测试验证** (1 小时)
- 编写单元测试
- 对比输出结果
- 修复问题

### 文档撰写建议

- **及时记录**: 每个发现都要立即记录
- **代码注释**: 标注原始代码位置 (文件名:行号)
- **截图保存**: 重要步骤保存截图到 assets/
- **时间线**: 记录分析进度时间线

---

## 相关资源

- [基础爬虫项目](./basic_scraper.md)
- [JavaScript 反混淆](../04-Advanced-Recipes/javascript_deobfuscation.md)
- [加密识别](../03-Basic-Recipes/crypto_identification.md)
