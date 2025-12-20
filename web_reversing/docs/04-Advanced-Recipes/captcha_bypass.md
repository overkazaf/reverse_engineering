# 验证码 (CAPTCHA) 绕过

## 概述

CAPTCHA (Completely Automated Public Turing test to tell Computers and Humans Apart) 是区分人类和机器人的图灵测试。从最早的文字输入，到后来的滑块拼图，再到现在的点选、行为分析和无感验证，验证码技术在不断演进。

**逆向验证码的核心**：理解验证逻辑、识别图像内容、模拟人类行为。

**技术路线**：

1. **识别** (Recognition)：OCR、深度学习、缺口检测
2. **模拟** (Simulation)：轨迹生成、行为伪造
3. **破解** (Bypass)：协议分析、参数伪造
4. **外包** (Outsource)：打码平台、人工打码

---

## 1. 验证码类型分类

### 1.1 文字验证码 (Text-based CAPTCHA)

#### 特征

- 扭曲变形的字母/数字
- 添加噪点、干扰线
- 背景复杂化

#### 难度等级

| 类型      | 示例          | 难度     | 识别率 |
| --------- | ------------- | -------- | ------ |
| 简单数字  | 1234          | ⭐       | 95%+   |
| 字母+数字 | A3bC          | ⭐⭐     | 85%+   |
| 带噪点    | ![噪点验证码] | ⭐⭐⭐   | 70%+   |
| 严重扭曲  | ![扭曲验证码] | ⭐⭐⭐⭐ | 50%+   |

#### 识别技术

- **传统 OCR**: Tesseract (效果一般)
- **专用工具**: ddddocr (国内验证码效果极佳)
- **深度学习**: CNN 分类器（需要训练数据）

**ddddocr 使用示例**:

```python
import ddddocr
import base64

ocr = ddddocr.DdddOcr()

# 方法1: 读取图片文件
with open('captcha.png', 'rb') as f:
    image = f.read()
result = ocr.classification(image)
print(result)  # 输出: "1234"

# 方法2: Base64 字符串
image_base64 = "data:image/png;base64,iVBORw0K..."
image_bytes = base64.b64decode(image_base64.split(',')[1])
result = ocr.classification(image_bytes)
```

---

### 1.2 滑块验证码 (Slider CAPTCHA)

#### 1.2.1 拼图滑块

**特征**:

- 一张背景图
- 一个滑块（拼图碎片）
- 需要滑动到正确位置完成拼图

**代表产品**:

- 极验 (GeeTest)
- 网易易盾
- 腾讯防水墙

**识别原理**: 缺口检测

**完整破解流程**:

```python
import ddddocr
import requests
from io import BytesIO
from PIL import Image

# 1. 获取验证码图片
bg_url = "https://example.com/captcha/bg.jpg"
slider_url = "https://example.com/captcha/slider.png"

bg_img = Image.open(BytesIO(requests.get(bg_url).content))
slider_img = Image.open(BytesIO(requests.get(slider_url).content))

# 2. 使用 ddddocr 进行缺口检测
det = ddddocr.DdddOcr(det=True)  # 开启目标检测模式

# 将图片转为字节
bg_bytes = BytesIO()
bg_img.save(bg_bytes, format='PNG')
bg_bytes = bg_bytes.getvalue()

# 检测缺口位置
result = det.detection(bg_bytes)
print(result)  # 输出: {'target': [x, y, width, height]}

# 3. 计算需要滑动的距离
gap_x = result['target'][0]  # 缺口的 x 坐标

# 4. 生成滑动轨迹（见下文）
trajectory = generate_trajectory(gap_x)

# 5. 提交验证
# (具体实现见下文轨迹模拟章节)
```

**OpenCV 缺口检测**:

```python
import cv2
import numpy as np

def find_gap(bg_img, slider_img):
    """使用 OpenCV 模板匹配找缺口"""

    # 转灰度图
    bg_gray = cv2.cvtColor(np.array(bg_img), cv2.COLOR_BGR2GRAY)
    slider_gray = cv2.cvtColor(np.array(slider_img), cv2.COLOR_BGR2GRAY)

    # 边缘检测
    bg_edges = cv2.Canny(bg_gray, 100, 200)
    slider_edges = cv2.Canny(slider_gray, 100, 200)

    # 模板匹配
    result = cv2.matchTemplate(bg_edges, slider_edges, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    # 返回最佳匹配位置
    return max_loc[0]  # x 坐标

gap_x = find_gap(bg_img, slider_img)
print(f"缺口位置: {gap_x}px")
```

---

#### 1.2.2 旋转滑块

**特征**:

- 圆形图片被旋转打乱
- 滑动滑块旋转图片，使其归位

**识别方法**:

1. **特征提取**: SIFT/ORB 特征点匹配
2. **角度计算**: 计算旋转角度
3. **滑动映射**: 将角度映射为滑动距离

```python
import cv2

def find_rotation_angle(original_img, rotated_img):
    """计算旋转角度"""

    # 使用 ORB 特征检测
    orb = cv2.ORB_create()

    kp1, des1 = orb.detectAndCompute(original_img, None)
    kp2, des2 = orb.detectAndCompute(rotated_img, None)

    # 特征匹配
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)
    matches = sorted(matches, key=lambda x: x.distance)

    # 计算旋转角度（简化版）
    # 实际实现需要更复杂的几何变换
    angle = calculate_angle_from_matches(kp1, kp2, matches)

    return angle
```

---

### 1.3 点选验证码 (Click-based CAPTCHA)

**特征**:

- 给出一张图片和文字提示
- 要求按顺序点击图中的特定对象
- 示例："请依次点击图中的红绿灯"

**代表产品**:

- 腾讯防水墙
- 12306 验证码（早期）

**识别技术**:

- **YOLO**: 目标检测神经网络
- **分类器**: 训练针对特定类别的识别器

**YOLO 识别示例**:

```python
from ultralytics import YOLO

# 加载预训练模型
model = YOLO('yolov8n.pt')

# 识别图中的对象
results = model('captcha.jpg')

# 提取红绿灯的位置
traffic_lights = []
for r in results:
    boxes = r.boxes
    for box in boxes:
        class_id = int(box.cls[0])
        if class_id == 9:  # COCO 数据集中红绿灯的类别 ID
            x, y, w, h = box.xywh[0].tolist()
            traffic_lights.append((int(x), int(y)))

print(f"检测到的红绿灯位置: {traffic_lights}")
# 输出: [(120, 80), (300, 150), ...]

# 按要求顺序点击
for x, y in traffic_lights:
    click(x, y)
```

---

### 1.4 行为验证码 (Behavioral CAPTCHA)

**特征**:

- 不是单纯的图像识别
- 分析鼠标轨迹、点击速度、设备指纹等行为特征
- 通常是"无感验证"

**代表产品**:

- Google reCAPTCHA v3
- 阿里云滑动验证

**关键指标**:

- **鼠标轨迹**: 曲线自然度、加速度变化
- **设备指纹**: Canvas、WebGL、AudioContext
- **环境特征**: User-Agent、时区、语言、屏幕分辨率
- **行为时序**: 停留时间、操作速度

**对抗方法**:

1. **模拟真实行为** (见轨迹模拟章节)
2. **绕过指纹检测** (见 [浏览器指纹识别](../04-Advanced-Recipes/browser_fingerprinting.md))
3. **使用真实浏览器** (Puppeteer + Stealth 插件)

---

### 1.5 语音验证码 (Audio CAPTCHA)

**特征**:

- 播放含有数字/字母的语音
- 通常是为视障人士提供的替代方案

**识别技术**:

- **语音识别**: Google Speech API, Baidu ASR
- **深度学习**: DeepSpeech, Wav2Vec

```python
import speech_recognition as sr

# 下载音频文件
audio_url = "https://example.com/captcha/audio.wav"
# ...下载到本地

# 使用 Google Speech API 识别
recognizer = sr.Recognizer()
with sr.AudioFile("captcha.wav") as source:
    audio = recognizer.record(source)

try:
    text = recognizer.recognize_google(audio)
    print(f"识别结果: {text}")
except sr.UnknownValueError:
    print("无法识别")
```

---

## 2. 轨迹模拟 (Trajectory Simulation)

识别出"缺口位置"只是第一步，关键是**如何滑过去**。匀速直线运动一定会被判定为机器人。

### 2.1 贝塞尔曲线轨迹

**原理**: 使用三次贝塞尔曲线模拟人手的加速-匀速-减速过程

**Python 实现**:

```python
import numpy as np
import random

def ease_out_quad(x):
    """缓出函数"""
    return 1 - (1 - x) ** 2

def ease_in_quad(x):
    """缓入函数"""
    return x ** 2

def ease_out_back(x):
    """回弹函数"""
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * pow(x - 1, 3) + c1 * pow(x - 1, 2)

def generate_trajectory(distance, overshoot=True):
    """
    生成滑动轨迹

    :param distance: 总距离
    :param overshoot: 是否过冲（滑过头再回来）
    :return: [(x, y, t), ...] 轨迹点列表
    """
    trajectory = []

    # 参数设置
    if overshoot:
        # 过冲：滑到distance + 5~10px，再回来
        overshoot_distance = distance + random.randint(5, 10)
    else:
        overshoot_distance = distance

    # 第一阶段：加速阶段 (30%)
    current = 0
    t = 0
    while current < overshoot_distance * 0.3:
        t += random.randint(10, 20)  # 时间间隔 10-20ms
        ratio = current / (overshoot_distance * 0.3)
        move = ease_in_quad(ratio) * 5 + random.uniform(0, 2)
        current += move

        # 添加y轴抖动
        y = random.randint(-2, 2)
        trajectory.append((int(current), y, t))

    # 第二阶段：匀速阶段 (40%)
    while current < overshoot_distance * 0.7:
        t += random.randint(10, 15)
        move = random.uniform(3, 5)
        current += move
        y = random.randint(-3, 3)
        trajectory.append((int(current), y, t))

    # 第三阶段：减速阶段 (30%)
    start_decel = current
    while current < overshoot_distance:
        t += random.randint(15, 25)
        ratio = (current - start_decel) / (overshoot_distance - start_decel)
        move = (1 - ease_out_quad(ratio)) * 3 + random.uniform(0, 1)
        current += move
        y = random.randint(-2, 2)
        trajectory.append((int(current), y, t))

    # 如果有过冲，添加回退阶段
    if overshoot:
        back_to = distance
        while current > back_to:
            t += random.randint(10, 15)
            move = random.uniform(1, 3)
            current -= move
            y = random.randint(-1, 1)
            trajectory.append((int(current), y, t))

    return trajectory

# 使用示例
trajectory = generate_trajectory(200, overshoot=True)
print(f"生成了 {len(trajectory)} 个轨迹点")
# 输出: [(3, 1, 15), (7, -1, 28), (12, 0, 43), ...]
```

---

### 2.2 真实轨迹采集与重放

**思路**: 记录真人滑动的轨迹，建立轨迹库，每次随机选择一条并缩放

**采集脚本** (在浏览器 Console 中运行):

```javascript
let trajectory = [];
let startTime = null;

document.addEventListener("mousedown", function (e) {
  if (e.target.className.includes("slider")) {
    startTime = Date.now();
    trajectory = [];

    document.addEventListener("mousemove", recordMove);
    document.addEventListener("mouseup", endRecording);
  }
});

function recordMove(e) {
  if (startTime) {
    trajectory.push({
      x: e.clientX,
      y: e.clientY,
      t: Date.now() - startTime,
    });
  }
}

function endRecording() {
  console.log(JSON.stringify(trajectory));
  copy(JSON.stringify(trajectory)); // 自动复制到剪贴板

  document.removeEventListener("mousemove", recordMove);
  document.removeEventListener("mouseup", endRecording);
}
```

**重放与缩放**:

```python
import json

def scale_trajectory(original_trajectory, target_distance):
    """
    缩放轨迹以适应新的距离

    :param original_trajectory: 原始轨迹 [{'x': 100, 'y': 0, 't': 150}, ...]
    :param target_distance: 目标距离
    :return: 缩放后的轨迹
    """
    # 计算原始距离
    original_distance = original_trajectory[-1]['x'] - original_trajectory[0]['x']

    # 计算缩放比例
    scale = target_distance / original_distance

    # 缩放轨迹
    scaled_trajectory = []
    base_x = original_trajectory[0]['x']

    for point in original_trajectory:
        scaled_x = (point['x'] - base_x) * scale
        scaled_trajectory.append({
            'x': int(scaled_x),
            'y': point['y'],
            't': point['t']
        })

    return scaled_trajectory

# 加载轨迹库
with open('trajectories.json', 'r') as f:
    trajectory_library = json.load(f)

# 随机选择一条轨迹
import random
trajectory = random.choice(trajectory_library)

# 缩放到目标距离
scaled_trajectory = scale_trajectory(trajectory, gap_x)
```

---

### 2.3 Puppeteer ghost-cursor 插件

**安装**:

```bash
npm install ghost-cursor
```

**使用示例**:

```javascript
const puppeteer = require("puppeteer");
const { createCursor } = require("ghost-cursor");

(async () => {
  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();
  const cursor = createCursor(page);

  await page.goto("https://example.com/captcha");

  // 找到滑块元素
  const slider = await page.$(".slider-button");
  const sliderBox = await slider.boundingBox();

  // 计算目标位置（假设缺口在 200px 处）
  const targetX = sliderBox.x + 200;
  const targetY = sliderBox.y + sliderBox.height / 2;

  // 使用 ghost-cursor 移动鼠标（自动生成逼真轨迹）
  await cursor.move(sliderBox.x, sliderBox.y);
  await cursor.click(); // 按下鼠标

  // 移动到目标位置（包含随机抖动和曲线）
  await cursor.move(targetX, targetY, {
    waitForSelector: false,
    paddingPercentage: 10, // 10% 的随机偏移
  });

  await page.mouse.up(); // 释放鼠标

  await browser.close();
})();
```

---

## 3. 协议破解 (Protocol Reverse)

有些验证码不需要模拟轨迹，直接破解其加密参数即可。

### 3.1 极验 (GeeTest) 协议分析

**流程**:

1. 初始化：`GET /api/captcha/init`
2. 获取图片：`GET /captcha/bg/{challenge}.jpg`
3. 验证：`POST /api/captcha/verify`

**验证参数**:

```javascript
{
    "challenge": "abc123...",  // 挑战码
    "validate": "def456...",   // 加密后的轨迹
    "seccode": "validate|jordan"  // validate + "|jordan"
}
```

**validate 生成逻辑** (简化版):

```javascript
// 极验加密算法（已公开部分）
function get_validate(trajectory, challenge) {
  // 1. 编码轨迹
  let encoded_trajectory = encode_trajectory(trajectory);

  // 2. 与 challenge 进行运算
  let combined = encoded_trajectory + challenge;

  // 3. MD5 + Base64
  let validate = md5(combined).substring(0, 32);

  return validate;
}

function encode_trajectory(trajectory) {
  // 轨迹编码（实际更复杂，包含加密和压缩）
  let encoded = "";
  for (let point of trajectory) {
    encoded +=
      int_to_char(point.x) + int_to_char(point.y) + int_to_char(point.t);
  }
  return encoded;
}
```

**Python 破解示例**:

```python
import requests
import hashlib

def crack_geetest(gap_x):
    """破解极验滑块验证"""

    # 1. 初始化获取 challenge
    init_url = "https://api.geetest.com/get.php"
    response = requests.get(init_url, params={
        'gt': 'your_gt_key',
        't': int(time.time() * 1000)
    })
    data = response.json()
    challenge = data['challenge']

    # 2. 生成轨迹
    trajectory = generate_trajectory(gap_x)

    # 3. 计算 validate (简化版，实际需要逆向完整算法)
    validate = calculate_validate(trajectory, challenge)

    # 4. 提交验证
    verify_url = "https://api.geetest.com/ajax.php"
    result = requests.post(verify_url, data={
        'gt': 'your_gt_key',
        'challenge': challenge,
        'validate': validate,
        'seccode': validate + '|jordan'
    })

    return result.json()
```

**注意**: 真实的极验算法非常复杂，包含多重加密、混淆和服务器端验证。上述代码仅为示意。

---

### 3.2 reCAPTCHA 令牌获取

**Google reCAPTCHA v2**:

```python
from selenium import webdriver
import time

driver = webdriver.Chrome()
driver.get('https://www.google.com/recaptcha/api2/demo')

# 找到 reCAPTCHA iframe
iframe = driver.find_element_by_css_selector('iframe[src*="recaptcha"]')
driver.switch_to.frame(iframe)

# 点击复选框
checkbox = driver.find_element_by_id('recaptcha-anchor')
checkbox.click()

# 等待验证完成
time.sleep(3)

# 切回主页面获取 token
driver.switch_to.default_content()
token = driver.find_element_by_id('g-recaptcha-response').get_attribute('value')
print(f"reCAPTCHA Token: {token}")
```

---

## 4. 商业打码平台对比

当技术方案成本过高或成功率不稳定时，商业打码平台是最佳选择。

| 平台                                                    | 价格          | 支持类型                           | 成功率 | 响应时间 | API 友好度 |
| ------------------------------------------------------- | ------------- | ---------------------------------- | ------ | -------- | ---------- |
| **[2Captcha](https://2captcha.com/)**                   | $2.99/1000 次 | 文字、reCAPTCHA、hCaptcha、GeeTest | 90%+   | 10-30 秒 | ⭐⭐⭐⭐⭐ |
| **[Anti-Captcha](https://anti-captcha.com/)**           | $2.00/1000 次 | 全类型                             | 92%+   | 15-40 秒 | ⭐⭐⭐⭐⭐ |
| **[CapSolver](https://www.capsolver.com/)**             | $0.80/1000 次 | reCAPTCHA、hCaptcha、FunCaptcha    | 88%+   | 20-50 秒 | ⭐⭐⭐⭐   |
| **[Death By Captcha](https://www.deathbycaptcha.com/)** | $1.39/1000 次 | 文字、图片                         | 85%+   | 30-60 秒 | ⭐⭐⭐     |
| **[极验通](https://jytong.net/)** (国内)                | ¥0.5/次       | 极验专用                           | 95%+   | 5-15 秒  | ⭐⭐⭐⭐   |
| **[超级鹰](https://www.chaojiying.com/)** (国内)        | ¥0.1-0.6/次   | 国内验证码                         | 80%+   | 10-30 秒 | ⭐⭐⭐     |

### 4.1 2Captcha 使用示例

**Python SDK**:

```bash
pip install 2captcha-python
```

**代码示例**:

```python
from twocaptcha import TwoCaptcha

# 初始化
solver = TwoCaptcha('YOUR_API_KEY')

# 1. 文字验证码
result = solver.normal('captcha.png')
print(result['code'])  # 输出: "AB3CD"

# 2. reCAPTCHA v2
result = solver.recaptcha(
    sitekey='6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-',
    url='https://example.com/login'
)
print(result['code'])  # reCAPTCHA token

# 3. hCaptcha
result = solver.hcaptcha(
    sitekey='10000000-ffff-ffff-ffff-000000000001',
    url='https://example.com'
)

# 4. GeeTest
result = solver.geetest(
    gt='geetest_gt',
    challenge='geetest_challenge',
    url='https://example.com'
)
print(result)  # {'challenge': '...', 'validate': '...', 'seccode': '...'}
```

---

### 4.2 自建打码平台

对于大规模需求，可以考虑自建人工打码平台：

**架构**:

```
爬虫服务器 → 任务队列 (Redis) → 打码工作台 (Web) → 打码员
```

**成本估算**:

- 打码员工资: ¥0.05-0.10/次
- 服务器成本: ¥200/月
- 适用场景: 日处理量 > 100,000 次

---

## 5. 实战案例

### 案例 1: 破解某电商网站登录滑块

**目标**: 自动化登录并获取 Cookie

**步骤**:

1. **分析验证流程**:

   ```
   1) POST /api/login → 返回需要验证
   2) GET /captcha/init → 获取背景图和滑块
   3) 识别缺口位置
   4) 生成轨迹
   5) POST /captcha/verify → 提交轨迹
   6) 验证通过后重新登录
   ```

2. **完整代码**:

   ```python
   import ddddocr
   import requests
   from trajectory import generate_trajectory

   class LoginCracker:
       def __init__(self):
           self.session = requests.Session()
           self.det = ddddocr.DdddOcr(det=True)

       def login(self, username, password):
           # 1. 尝试登录
           resp = self.session.post('https://example.com/api/login', data={
               'username': username,
               'password': password
           })

           if resp.json()['need_captcha']:
               # 2. 需要验证码
               captcha_token = self.solve_captcha()

               # 3. 带验证码重新登录
               resp = self.session.post('https://example.com/api/login', data={
                   'username': username,
                   'password': password,
                   'captcha_token': captcha_token
               })

           return resp.json()

       def solve_captcha(self):
           # 获取验证码图片
           init_resp = self.session.get('https://example.com/captcha/init').json()
           bg_url = init_resp['bg_url']

           # 下载背景图
           bg_img = requests.get(bg_url).content

           # 识别缺口
           result = self.det.detection(bg_img)
           gap_x = result['target'][0]

           # 生成轨迹
           trajectory = generate_trajectory(gap_x)

           # 提交验证
           verify_resp = self.session.post('https://example.com/captcha/verify', json={
               'token': init_resp['token'],
               'trajectory': trajectory
           })

           return verify_resp.json()['captcha_token']

   # 使用
   cracker = LoginCracker()
   result = cracker.login('username', 'password')
   print(result)
   ```

---

### 案例 2: 使用 Puppeteer + 2Captcha 破解 reCAPTCHA

```javascript
const puppeteer = require("puppeteer");
const solver = require("2captcha");

(async () => {
  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();

  await page.goto("https://example.com/login");

  // 获取 reCAPTCHA sitekey
  const sitekey = await page.evaluate(() => {
    return document
      .querySelector("[data-sitekey]")
      .getAttribute("data-sitekey");
  });

  // 调用 2Captcha 解决
  const captchaSolver = new solver.Solver("YOUR_API_KEY");
  const result = await captchaSolver.recaptcha(sitekey, page.url());

  // 注入 token
  await page.evaluate((token) => {
    document.getElementById("g-recaptcha-response").innerHTML = token;
  }, result.data);

  // 提交表单
  await page.click("#submit-button");

  await page.waitForNavigation();
  console.log("登录成功!");

  await browser.close();
})();
```

---

## 6. 防御对抗

### 6.1 验证码服务商的防御手段

| 防御手段       | 说明                        | 对抗方法                   |
| -------------- | --------------------------- | -------------------------- |
| **设备指纹**   | Canvas、WebGL、AudioContext | Puppeteer Stealth 插件     |
| **行为分析**   | 鼠标轨迹、键盘节奏          | ghost-cursor、真实轨迹重放 |
| **IP 风控**    | 频率限制、黑名单            | 代理池、住宅 IP            |
| **Token 绑定** | 令牌与设备/会话绑定         | 保持 Session、Cookie       |
| **时间戳校验** | 限制验证码有效期            | 加快识别速度               |
| **重放检测**   | 检测轨迹是否重复            | 每次生成新轨迹             |

---

### 6.2 最佳实践

1. **组合策略**: 识别 + 打码平台 (识别失败时降级)
2. **速率控制**: 避免短时间大量请求
3. **真实环境**: 使用真实浏览器而非无头模式
4. **轨迹多样性**: 不要使用固定轨迹模板
5. **异常处理**: 验证失败时重试而非崩溃

---

## 7. 常见问题

### Q1: ddddocr 识别率不高怎么办？

**解决方案**:

- 图像预处理：去噪、二值化、增强对比度
- 尝试不同的 OCR 工具对比
- 考虑使用打码平台

### Q2: 滑块总是验证失败？

**可能原因**:

- 缺口识别不准确
- 轨迹太假（匀速直线）
- 设备指纹被识别
- IP 被风控

**调试方法**:

- 在浏览器中手动验证是否通过
- 检查 Network 面板的验证响应
- 对比真人滑动的轨迹

### Q3: 打码平台响应太慢？

**优化方法**:

- 使用异步并发
- 预先识别简单验证码，复杂的才用打码
- 选择响应更快的平台（如极验通）

---

## 8. 工具与资源

### 推荐工具

| 工具                | 用途              | 链接                                           |
| ------------------- | ----------------- | ---------------------------------------------- |
| **ddddocr**         | 中文验证码 OCR    | https://github.com/sml2h3/ddddocr              |
| **YOLOv8**          | 目标检测          | https://github.com/ultralytics/ultralytics     |
| **ghost-cursor**    | 自然鼠标轨迹      | https://github.com/Xetera/ghost-cursor         |
| **2Captcha**        | 商业打码平台      | https://2captcha.com/                          |
| **hcaptcha-solver** | hCaptcha 自动求解 | https://github.com/QIN2DIM/hcaptcha-challenger |

---

## 9. 总结

验证码对抗是一场**永恒的猫鼠游戏**。技术路线选择取决于：

- **个人学习**: 手动识别 + 轨迹模拟（ddddocr + 贝塞尔曲线）
- **小规模爬虫**: 打码平台（2Captcha、超级鹰）
- **大规模商业**: 深度学习 + 行为伪造 + 分布式架构
- **终极方案**: 真实设备 + 真实用户行为 + 指纹伪造

**核心原则**:

1. **成本优先**: 选择性价比最高的方案
2. **稳定性优先**: 牺牲一定速度换取成功率
3. **合法合规**: 遵守目标网站的服务条款
4. **持续优化**: 验证码在升级，方案也要迭代

---

## 相关章节

- [浏览器自动化脚本](../07-Scripts/automation_scripts.md)
- [浏览器指纹识别](./browser_fingerprinting.md)
- [Puppeteer 与 Playwright](../02-Tooling/puppeteer_playwright.md)
- [动态参数分析](../03-Basic-Recipes/dynamic_parameter_analysis.md)
