---
title: "配方：绕过简单验证码"
date: 2024-04-30
type: posts
tags: ["浏览器指纹", "入门", "Selenium", "验证码", "Web逆向"]
weight: 10
---

# 配方：绕过简单验证码

## 配方信息

| 项目 | 说明 |
| ------------ | -------------------------- |
| **难度** | ⭐⭐ (初级) |
| **预计时间** | 30-45 分钟 |
| **所需工具** | Python 3.7+, Tesseract OCR |
| **适用场景** | 识别简单的图形验证码 |
| **前置知识** | Python 基础, PIL/Pillow 库 |

---

## 📚 前置知识

在开始本配方之前，建议先掌握以下内容：

| 知识领域 | 重要程度 | 参考资料 |
|----------|---------|---------|
| Python 基础语法 | 必需 | 了解函数、循环、条件语句等基本概念 |
| HTTP 请求基础 | 必需 | [HTTP/HTTPS 协议](../01-Foundations/http_https_protocol.md) |
| PIL/Pillow 图像处理 | 推荐 | Python 图像处理库，用于验证码预处理 |
| Chrome DevTools | 推荐 | [浏览器开发者工具](../02-Tooling/browser_devtools.md) |

> 💡 **新手提示**: 本配方侧重于**简单验证码**的识别。对于复杂验证码（滑块、点选等），请参考进阶配方 [验证码绕过](../04-Advanced-Recipes/captcha_bypass.md)。

---

## 你将学到

完成这个配方后，你将能够：

- ✅ 分析验证码生成和验证流程
- ✅ 抓取验证码图片
- ✅ 使用 OCR 技术识别文字
- ✅ 图像预处理提高识别率
- ✅ 自动化验证码识别流程
- ✅ 判断何时应该使用人工打码平台

---

## 准备工作

### 安装依赖

#### 1. 安装 Python 库

```bash
pip install pillow requests pytesseract opencv-python
```

#### 2. 安装 Tesseract OCR

**Windows**:

```bash
# 下载安装包
https://github.com/UB-Mannheim/tesseract/wiki

# 安装后配置环境变量
set PATH=%PATH%;C:\Program Files\Tesseract-OCR
```

**macOS**:

```bash
brew install tesseract
```

**Linux**:

```bash
sudo apt-get install tesseract-ocr
sudo apt-get install libtesseract-dev
```

#### 3. 验证安装

```bash
tesseract --version
# 输出: tesseract 5.x.x
```

### 检查清单

- ☐ 已安装 Python 3.7+
- ☐ 已安装所有依赖库
- ☐ Tesseract OCR 正常工作
- ☐ 了解基本的 Python 和 HTTP 请求

---

## 步骤详解

### Step 1: 分析验证码流程

#### 1.1 观察验证码

打开一个有验证码的登录页面（或使用下面的示例）：

```html
<!DOCTYPE html>
<html>
<head>
<title>验证码登录</title>
</head>
<body>
<h2>登录</h2>
<input id="username" placeholder="用户名" />
<input id="password" type="password" placeholder="密码" />
<br /><br />
<img
id="captcha"
src="/captcha"
onclick="this.src='/captcha?'+Date.now()"
/>
<br />
<input id="captcha_code" placeholder="验证码" />
<button onclick="login()">登录</button>

<script>
function login() {
const data = {
username: document.getElementById("username").value,
password: document.getElementById("password").value,
captcha: document.getElementById("captcha_code").value,
};

fetch("/api/login", {
method: "POST",
headers: { "Content-Type": "application/json" },
body: JSON.stringify(data),
})
.then((r) => r.json())
.then((result) => alert(result.message));
}
</script>
</body>
</html>
```

#### 1.2 理解验证流程

1. **获取验证码**: `GET /captcha` → 返回图片
2. **用户输入**: 人工识别并输入
3. **提交验证**: `POST /api/login` 带上验证码
4. **服务器验证**: 比对答案，返回结果

**关键点**:

- 验证码图片 URL: `/captcha`
- 验证码需要和登录请求一起提交
- 通常有会话（Cookie）关联验证码和答案

---

### Step 2: 抓取验证码图片

#### 2.1 编写抓取脚本

创建 `captcha_download.py`:

```python
import requests
from PIL import Image
from io import BytesIO

# 创建会话（保持 Cookie）
session = requests.Session()

def download_captcha(url, save_path='captcha.png'):
"""下载验证码图片"""
response = session.get(url)

if response.status_code == 200:
# 保存图片
with open(save_path, 'wb') as f:
f.write(response.content)

# 显示图片
img = Image.open(BytesIO(response.content))
img.show()

print(f"✅ 验证码已保存到: {save_path}")
return True
else:
print(f"❌ 下载失败: {response.status_code}")
return False

if __name__ == '__main__':
url = 'https://example.com/captcha'
download_captcha(url)
```

#### 2.2 运行测试

```bash
python captcha_download.py
```

**输出**: 图片会自动打开，并保存为 `captcha.png`

---

### Step 3: OCR 识别验证码

#### 3.1 基础识别

创建 `captcha_ocr.py`:

```python
import pytesseract
from PIL import Image

def recognize_captcha(image_path):
"""识别验证码"""
# 加载图片
img = Image.open(image_path)

# OCR 识别
text = pytesseract.image_to_string(img, config='--psm 7 digits')

# 清理结果（去除空格和换行）
result = text.strip().replace(' ', '').replace('\n', '')

print(f"识别结果: {result}")
return result

if __name__ == '__main__':
result = recognize_captcha('captcha.png')
print(f"✅ 验证码是: {result}")
```

**参数说明**:

- `--psm 7`: Page Segmentation Mode = 7（单行文本）
- `digits`: 只识别数字

#### 3.2 测试识别

```bash
python captcha_ocr.py
```

**可能的问题**: 识别率很低或完全识别不出来

**原因**: 验证码有干扰（噪点、线条、倾斜等）

---

### Step 4: 图像预处理

#### 4.1 增强识别率

创建 `captcha_preprocess.py`:

```python
import cv2
import numpy as np
from PIL import Image
import pytesseract

def preprocess_image(image_path):
"""预处理验证码图片"""
# 读取图片
img = cv2.imread(image_path)

# 1. 转灰度
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# 2. 二值化（去除噪点）
_, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

# 3. 去噪（形态学操作）
kernel = np.ones((2, 2), np.uint8)
opening = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)

# 4. 保存处理后的图片
processed_path = 'captcha_processed.png'
cv2.imwrite(processed_path, opening)

print(f"✅ 预处理完成: {processed_path}")
return processed_path

def recognize_with_preprocess(image_path):
"""预处理后识别"""
# 预处理
processed_path = preprocess_image(image_path)

# OCR 识别
img = Image.open(processed_path)
text = pytesseract.image_to_string(img, config='--psm 7 digits')
result = text.strip().replace(' ', '').replace('\n', '')

print(f"识别结果: {result}")
return result

if __name__ == '__main__':
result = recognize_with_preprocess('captcha.png')
print(f"✅ 验证码是: {result}")
```

#### 4.2 对比效果

```bash
# 原始识别
python captcha_ocr.py
# 输出: 12O4 (错误)

# 预处理后识别
python captcha_preprocess.py
# 输出: 1234 (正确)
```

---

### Step 5: 完整自动化流程

#### 5.1 集成所有步骤

创建 `auto_login.py`:

```python
import requests
import pytesseract
from PIL import Image
from io import BytesIO
import cv2
import numpy as np

class CaptchaBypass:
def __init__(self, base_url):
self.base_url = base_url
self.session = requests.Session()

def download_captcha(self):
"""下载验证码"""
url = f"{self.base_url}/captcha"
response = self.session.get(url)

if response.status_code == 200:
return response.content
return None

def preprocess_image(self, image_bytes):
"""预处理图片"""
# 字节 → numpy array
nparr = np.frombuffer(image_bytes, np.uint8)
img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

# 灰度化
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# 二值化
_, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

# 去噪
kernel = np.ones((2, 2), np.uint8)
opening = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)

# numpy array → PIL Image
img_pil = Image.fromarray(opening)
return img_pil

def recognize_captcha(self, img):
"""OCR 识别"""
text = pytesseract.image_to_string(img, config='--psm 7 digits')
result = text.strip().replace(' ', '').replace('\n', '')
return result

def login(self, username, password):
"""自动登录"""
# 1. 下载验证码
print(" 下载验证码...")
captcha_bytes = self.download_captcha()

# 2. 预处理
print(" 预处理图片...")
processed_img = self.preprocess_image(captcha_bytes)

# 3. 识别
print(" 识别验证码...")
captcha_code = self.recognize_captcha(processed_img)
print(f"✅ 识别结果: {captcha_code}")

# 4. 登录
print(" 发送登录请求...")
response = self.session.post(
f"{self.base_url}/api/login",
json={
'username': username,
'password': password,
'captcha': captcha_code
}
)

result = response.json()
print(f" 响应: {result}")

return result

if __name__ == '__main__':
bypass = CaptchaBypass('https://example.com')
result = bypass.login('admin', '123456')

if result['code'] == 0:
print(" 登录成功！")
else:
print(f"❌ 登录失败: {result['message']}")
```

#### 5.2 运行测试

```bash
python auto_login.py
```

**预期输出**:

```
下载验证码...
预处理图片...
识别验证码...
✅ 识别结果: 1234
发送登录请求...
响应: {'code': 0, 'message': '登录成功', 'token': '...'}
登录成功！
```

---

## ✅ 验证清单

完成后，检查以下项目：

- ☐ 成功下载验证码图片
- ☐ Tesseract OCR 能正常识别
- ☐ 预处理提高了识别率
- ☐ 完整的自动化流程能运行
- ☐ 识别准确率达到 60% 以上

---

## 进阶练习

### 练习 1: 提高识别率

尝试不同的预处理方法：

```python
# 方法1: 调整二值化阈值
_, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

# 方法2: 膨胀和腐蚀
dilate = cv2.dilate(binary, kernel, iterations=1)
erode = cv2.erode(dilate, kernel, iterations=1)

# 方法3: 去除边框
h, w = gray.shape
gray = gray[5:h-5, 5:w-5]
```

### 练习 2: 处理字母验证码

修改 OCR 配置：

```python
# 识别字母+数字
text = pytesseract.image_to_string(img, config='--psm 7')

# 只识别大写字母+数字
text = pytesseract.image_to_string(img, config='--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
```

### 练习 3: 使用机器学习

对于复杂验证码，可以使用深度学习：

```python
# 使用 CRNN 模型
import torch
from crnn import CRNN

model = CRNN()
model.load_state_dict(torch.load('captcha_model.pth'))
result = model.predict(img)
```

**训练数据**: 需要标注 1000+验证码样本

---

## 常见问题

### Q1: OCR 完全识别不出来怎么办？

**A**: 可能的原因和解决方案：

1. **干扰太强**:

- 尝试更激进的预处理
- 使用机器学习模型
- 考虑使用打码平台

2. **字体特殊**:

- 训练 Tesseract 自定义字体
- 使用深度学习模型

3. **验证码类型不适合 OCR**:
    - 滑块验证码 → 使用轨迹模拟
    - 点选验证码 → 使用图像识别
    - 行为验证码 → 分析行为模式

### Q2: 识别率只有 30%，如何提高？

**A**: 按顺序尝试：

1. **优化预处理** (可提升到 60%)
2. **调整 OCR 参数** (可提升到 70%)
3. **多次识别取最可能结果** (可提升到 80%)
4. **训练自定义模型** (可提升到 90%+)

**代码示例**:

```python
# 多次识别
results = []
for i in range(5):
result = recognize_captcha(img)
results.append(result)

# 取出现最多的结果
from collections import Counter
most_common = Counter(results).most_common(1)[0][0]
```

### Q3: 何时应该使用打码平台？

**A**: 以下情况建议使用打码平台：

- 验证码非常复杂（扭曲、重叠、背景复杂）
- 识别率低于 60%且优化无效
- 验证码类型多变
- 项目预算充足

**推荐平台**:

- 超级鹰: <http://www.chaojiying.com/>
- 打码兔: <http://www.dama2.com/>

**成本**: 约 ¥0.001 - ¥0.01 / 张

### Q4: 如何处理滑块验证码？

**A**: 滑块验证码不适合 OCR，需要：

1. **模拟滑动轨迹**:

```python
# 生成模拟人类的轨迹
def generate_track(distance):
track = []
current = 0
while current < distance:
v = random.randint(1, 5)
track.append(v)
current += v
return track
```

2. **分析缺口位置**:

- 使用图像识别找到缺口
- 计算需要移动的距离

参考: [验证码绕过](../../04-Advanced-Recipes/captcha_bypass.md)

---

## 原理解析

### OCR 工作原理

```
图片 → 预处理 → 特征提取 → 字符分类 → 文本输出
```

**关键步骤**:

1. **二值化**: 转为黑白图片，突出文字
2. **去噪**: 移除干扰点和线条
3. **分割**: 将字符分割为独立的部分
4. **识别**: 将每个字符与字库对比

### 为什么需要预处理？

原始验证码的干扰：

- 噪点（随机点）
- 干扰线（随机线条）
- 颜色变化
- 字符粘连或断裂

预处理可以：

- 去除噪点和线条
- 统一颜色（黑白）
- 修复断裂
- 分离粘连

---

## 相关配方

### 基础配方

- [调试技巧](../../03-Basic-Recipes/debugging_techniques.md) - 调试验证流程

### 高级配方

- [验证码识别与绕过](../../04-Advanced-Recipes/captcha_bypass.md) - 更多验证码类型
- [浏览器指纹](../../04-Advanced-Recipes/browser_fingerprinting.md) - 行为验证码

### 工具脚本

- [自动化脚本](../../07-Scripts/automation_scripts.md) - Selenium 自动化

---

## 恭喜！

你已经掌握了：

- ✅ 验证码流程分析
- ✅ OCR 基础使用
- ✅ 图像预处理技巧
- ✅ 自动化验证码识别

**下一步**:

- 深入学习 [验证码绕过](../../04-Advanced-Recipes/captcha_bypass.md)
- 或开始 [基础配方](../../03-Basic-Recipes/) 的系统学习

---

**小贴士**:

- OCR 不是万能的，复杂验证码需要机器学习
- 遵守网站的服务条款和请求频率限制
- 合法合规使用这些技术

Happy Bypassing! 
