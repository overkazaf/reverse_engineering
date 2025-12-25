---
title: "配方：解密 API 参数"
date: 2024-04-01
weight: 10
---

# 配方：解密 API 参数

## 配方信息

| 项目 | 说明 |
| ------------ | -------------------------------------------- |
| **难度** | ⭐⭐ (初级) |
| **预计时间** | 30-45 分钟 |
| **所需工具** | Chrome 浏览器, Python 3.7+ |
| **适用场景** | 破解 API 签名、解密请求参数 |
| **前置知识** | 完成 [你的第一个 Hook](./your_first_hook.md) |

---

## 📚 前置知识

在开始本配方之前，建议先掌握以下内容：

| 知识领域 | 重要程度 | 参考资料 |
|----------|---------|---------|
| 你的第一个 Hook | 必需 | [你的第一个 Hook](./your_first_hook.md) |
| JavaScript 基础 | 推荐 | [JavaScript 基础](../01-Foundations/javascript_basics.md) |
| HTTP 协议基础 | 推荐 | [HTTP/HTTPS 协议](../01-Foundations/http_https_protocol.md) |
| Chrome DevTools | 推荐 | [浏览器开发者工具](../02-Tooling/browser_devtools.md) |

> 💡 **新手提示**: 如果你已完成"你的第一个 Hook"配方，就可以开始本教程了。对加密算法不熟悉也没关系，我们会在实践中逐步讲解。

---

## 你将学到

完成这个配方后，你将能够：

- ✅ 使用 XHR 断点定位加密函数
- ✅ 分析 JavaScript 加密代码
- ✅ 识别常见加密算法（MD5, SHA256, AES 等）
- ✅ 提取密钥和加密参数
- ✅ 用 Python 复现加密逻辑
- ✅ 构造有效的 API 请求

---

## 准备工作

### 检查清单

- ☐ 完成了"你的第一个 Hook"配方
- ☐ 已安装 Python 3.7+
- ☐ 安装了 requests 库: `pip install requests`
- ☐ 了解基本的 Python 语法

### 实战目标

我们将分析一个加密的登录接口，目标是：

1. 找到密码加密函数
2. 分析加密算法
3. 用 Python 实现相同的加密
4. 成功发送登录请求

---

## 步骤详解

### Step 1: 找到加密的请求

#### 1.1 打开示例页面

访问模拟登录页面（使用本地 HTML 文件或在线 Demo）：

```html
<!DOCTYPE html>
<html>
<head>
<title>登录示例</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/crypto-js/4.1.1/crypto-js.min.js"></script>
</head>
<body>
<h2>登录</h2>
<input id="username" placeholder="用户名" value="admin" />
<input id="password" type="password" placeholder="密码" value="123456" />
<button onclick="login()">登录</button>

<script>
function login() {
const username = document.getElementById("username").value;
const password = document.getElementById("password").value;

// 加密密码
const encryptedPassword = CryptoJS.MD5(password).toString();

// 生成签名
const timestamp = Date.now();
const sign = CryptoJS.MD5(
username + encryptedPassword + timestamp + "SECRET_KEY"
).toString();

// 发送请求
fetch("/api/login", {
method: "POST",
headers: { "Content-Type": "application/json" },
body: JSON.stringify({
username: username,
password: encryptedPassword,
timestamp: timestamp,
sign: sign,
}),
})
.then((r) => r.json())
.then((data) => console.log(data));
}
</script>
</body>
</html>
```

将上面的代码保存为 `login_demo.html` 并在浏览器中打开。

#### 1.2 触发请求

1. 打开开发者工具（F12）
2. 切换到 **Network** 标签
3. 点击"登录"按钮
4. 观察 Network 面板中的请求

你会看到一个 POST 请求到 `/api/login`，查看请求体：

```json
{
"username": "admin",
"password": "e10adc3949ba59abbe56e057f20f883e",
"timestamp": 1702887654321,
"sign": "a1b2c3d4e5f6..."
}
```

**发现**: `password` 不是明文，而是一串 32 位的十六进制字符串（很可能是 MD5）

---

### Step 2: 定位加密函数

#### 2.1 使用 XHR 断点

1. 在 **Sources** 标签下，右侧找到 **XHR/fetch Breakpoints**
2. 点击 `+` 添加断点
3. 输入 `/api/login`

![XHR Breakpoint](https://via.placeholder.com/600x300?text=XHR+Breakpoint)

4. 再次点击"登录"按钮

**结果**: 代码会在发送请求前暂停

#### 2.2 查看调用栈

在 **Call Stack** 面板中，你会看到：

```
fetch (async)
login (login_demo.html:24)
onclick (login_demo.html:12)
```

5. 点击 `login` 函数，跳转到源代码

![Call Stack](https://via.placeholder.com/600x300?text=Call+Stack)

#### 2.3 观察加密代码

现在你可以看到完整的加密逻辑：

```javascript
const encryptedPassword = CryptoJS.MD5(password).toString();
const sign = CryptoJS.MD5(
username + encryptedPassword + timestamp + "SECRET_KEY"
).toString();
```

**分析**:

- 密码使用 **MD5** 加密
- 签名使用 `用户名 + 加密后的密码 + 时间戳 + 密钥` 拼接后再 MD5
- 密钥是 `SECRET_KEY`

---

### Step 3: 在 Console 中验证

#### 3.1 测试加密函数

在 Console 中执行：

```javascript
// 测试 MD5
CryptoJS.MD5("123456").toString();
// 输出: "e10adc3949ba59abbe56e057f20f883e"
```

#### 3.2 完整测试

```javascript
const username = "admin";
const password = "123456";
const timestamp = Date.now();

const encryptedPassword = CryptoJS.MD5(password).toString();
const sign = CryptoJS.MD5(
username + encryptedPassword + timestamp + "SECRET_KEY"
).toString();

console.log({
encryptedPassword: encryptedPassword,
sign: sign,
timestamp: timestamp,
});
```

**输出**:

```
{
encryptedPassword: "e10adc3949ba59abbe56e057f20f883e",
sign: "f7c3bc1d808e04732adf679965ccc34c",
timestamp: 1702887654321
}
```

✅ **验证**: 每次执行，`encryptedPassword` 都是固定的，但 `sign` 会变化（因为时间戳在变）

---

### Step 4: Python 复现

#### 4.1 安装依赖

```bash
pip install requests
```

#### 4.2 编写 Python 脚本

创建 `login.py`:

```python
import hashlib
import time
import requests

def md5(text):
"""MD5 加密"""
return hashlib.md5(text.encode()).hexdigest()

def login(username, password):
# 1. 加密密码
encrypted_password = md5(password)

# 2. 生成时间戳
timestamp = int(time.time() * 1000)

# 3. 生成签名
sign_string = username + encrypted_password + str(timestamp) + 'SECRET_KEY'
sign = md5(sign_string)

# 4. 构造请求体
payload = {
'username': username,
'password': encrypted_password,
'timestamp': timestamp,
'sign': sign
}

print(f" 发送请求:")
print(f" Username: {username}")
print(f" Encrypted Password: {encrypted_password}")
print(f" Timestamp: {timestamp}")
print(f" Sign: {sign}")

# 5. 发送请求
response = requests.post(
'https://example.com/api/login',
json=payload,
headers={'Content-Type': 'application/json'}
)

print(f"\n 响应:")
print(f" Status Code: {response.status_code}")
print(f" Response: {response.text}")

return response.json()

if __name__ == '__main__':
# 测试
result = login('admin', '123456')
print(f"\n✅ 登录结果: {result}")
```

#### 4.3 运行测试

```bash
python login.py
```

**预期输出**:

```
发送请求:
Username: admin
Encrypted Password: e10adc3949ba59abbe56e057f20f883e
Timestamp: 1702887654321
Sign: f7c3bc1d808e04732adf679965ccc34c

响应:
Status Code: 200
Response: {"code":0,"message":"登录成功","data":{"token":"..."}}

✅ 登录结果: {'code': 0, 'message': '登录成功', 'data': {...}}
```

---

## ✅ 验证清单

完成后，检查以下项目：

- ☐ 成功找到了加密函数位置
- ☐ 识别出加密算法是 MD5
- ☐ 提取出了密钥 `SECRET_KEY`
- ☐ 理解了签名生成逻辑
- ☐ Python 脚本能正确生成加密参数
- ☐ 成功发送了请求并得到响应

---

## 进阶练习

### 练习 1: 分析更复杂的加密

尝试分析使用 AES 加密的接口：

```javascript
// 示例：AES 加密
const key = CryptoJS.enc.Utf8.parse("1234567890abcdef");
const iv = CryptoJS.enc.Utf8.parse("abcdefghijklmnop");
const encrypted = CryptoJS.AES.encrypt(password, key, { iv: iv });
```

**提示**: Python 使用 `pycryptodome` 库：

```bash
pip install pycryptodome
```

### 练习 2: 处理动态密钥

有些网站的密钥是动态生成的：

```javascript
const key = CryptoJS.MD5(username + timestamp).toString();
```

**任务**: 修改 Python 脚本，支持动态密钥

### 练习 3: 批量测试

编写脚本测试多个账号：

```python
users = [
('user1', 'password1'),
('user2', 'password2'),
('user3', 'password3')
]

for username, password in users:
result = login(username, password)
print(f"{username}: {result['message']}")
```

---

## 常见问题

### Q1: 如何判断使用了哪种加密算法？

**A**: 根据特征识别：

| 特征 | 可能的算法 |
| ---------------------- | ---------- |
| 32 位十六进制 | MD5 |
| 40 位十六进制 | SHA1 |
| 64 位十六进制 | SHA256 |
| Base64 编码 + 固定长度 | AES/DES |
| 看到 `CryptoJS.MD5` | 确定是 MD5 |

**工具**: 使用 [加密算法识别](../../03-Basic-Recipes/crypto_identification.md)

### Q2: 找不到加密函数？代码被混淆了怎么办？

**A**: 使用以下技巧：

1. 搜索加密库名称：`CryptoJS`, `crypto`, `encrypt`
2. 搜索特征字符串：`MD5`, `AES`, `SHA`
3. Hook 可疑函数查看输入输出
4. 使用 [JavaScript 反混淆](../../04-Advanced-Recipes/javascript_deobfuscation.md)

### Q3: Python 生成的签名不对？

**A**: 检查以下几点：

1. **字符编码**: 确保使用 UTF-8
2. **时间戳格式**: 毫秒还是秒？
3. **拼接顺序**: 参数顺序是否正确？
4. **密钥**: 是否有隐藏的盐或密钥？

**调试技巧**:

```python
# 在 Python 中打印中间值
sign_string = username + encrypted_password + str(timestamp) + 'SECRET_KEY'
print(f"Sign String: {sign_string}")
print(f"Sign: {md5(sign_string)}")
```

然后在浏览器中对比：

```javascript
console.log(username + encryptedPassword + timestamp + "SECRET_KEY");
```

### Q4: 如何处理非标准的加密？

**A**: 有些网站使用自定义加密：

```javascript
function customEncrypt(data) {
// 自定义算法
return data.split("").reverse().join("");
}
```

**解决**:

1. 完整理解算法逻辑
2. 用 Python 逐行翻译
3. 或者考虑使用 [RPC 调用](../../04-Advanced-Recipes/javascript_vm_protection.md#rpc调用)

---

## 原理解析

### 为什么网站要加密参数？

1. **安全性**: 防止密码明文传输
2. **防篡改**: 签名确保参数未被修改
3. **防重放**: 时间戳防止重放攻击
4. **反爬虫**: 增加逆向难度

### 签名的作用

```
签名 = Hash(所有参数 + 密钥)
```

服务器也使用相同算法计算签名，如果不一致则拒绝请求：

```python
# 服务器端验证
received_sign = request.json['sign']
calculated_sign = md5(username + password + timestamp + 'SECRET_KEY')

if received_sign != calculated_sign:
return {'code': -1, 'message': '签名错误'}
```

---

## 相关配方

### 基础配方

- [加密算法识别](../../03-Basic-Recipes/crypto_identification.md) - 识别加密算法
- [API 逆向](../../03-Basic-Recipes/api_reverse_engineering.md) - API 逆向完整流程

### 高级配方

- [JavaScript 反混淆](../../04-Advanced-Recipes/javascript_deobfuscation.md) - 处理混淆代码
- [JSVMP](../../04-Advanced-Recipes/javascript_vm_protection.md) - 处理虚拟机保护

### 案例研究

- [电商网站逆向](../../05-Case-Studies/case_ecommerce.md) - 真实案例

---

## 恭喜！

你已经掌握了：

- ✅ 定位加密函数的方法
- ✅ 分析常见加密算法
- ✅ 用 Python 复现加密逻辑
- ✅ 构造有效的 API 请求

**下一步**:

- 学习 [绕过简单验证码](./bypass_simple_captcha.md)
- 或深入 [API 逆向](../../03-Basic-Recipes/api_reverse_engineering.md)

---

**小贴士**:

- 总是先在浏览器 Console 中验证你的理解
- 记录你分析过的加密算法，建立自己的知识库
- 遇到不懂的加密算法，可以搜索或参考 [加密算法识别](../../03-Basic-Recipes/crypto_identification.md)

Happy Decrypting! 
