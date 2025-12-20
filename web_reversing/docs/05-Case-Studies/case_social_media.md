# 社交媒体逆向案例

## 概述

社交媒体平台通常包含复杂的 API 调用、无限滚动加载、实时通信、内容推荐算法等。本文通过真实案例介绍社交媒体平台的逆向分析技巧。

---

## 案例一：微博/Twitter 无限滚动分页

### 背景

社交媒体的信息流通常采用无限滚动（Infinite Scroll）方式加载：

- 用户滚动到底部时自动加载下一页
- 不使用传统的 `page=1,2,3` 分页
- 使用游标（cursor）或最后一条 ID 作为分页标识

---

### 逆向步骤

#### 1. 抓包分析

滚动到底部，观察 Network 面板的 XHR 请求：

```http
GET /api/timeline?max_id=1234567890&count=20 HTTP/1.1
```

参数说明：

- `max_id`: 当前页最后一条微博的 ID
- `count`: 每页数量

响应结构：

```json
{
    "data": [
        {
            "id": "1234567890",
            "text": "微博内容...",
            "user": {...},
            "created_at": "2023-12-17 10:00:00"
        },
        // 更多微博...
    ],
    "next_cursor": "1234567850"  // 下一页的 cursor
}
```

#### 2. Python 实现爬取

```python
import requests
import time

class WeiboScraper:
    def __init__(self, cookie):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0...',
            'Cookie': cookie,
            'Referer': 'https://weibo.com/'
        })
        self.base_url = 'https://weibo.com/api/timeline'

    def fetch_timeline(self, max_id=None, count=20):
        """获取时间线"""
        params = {'count': count}
        if max_id:
            params['max_id'] = max_id

        response = self.session.get(self.base_url, params=params)
        return response.json()

    def scrape_all(self, max_pages=10):
        """爬取多页"""
        all_posts = []
        next_cursor = None

        for page in range(max_pages):
            print(f'Fetching page {page + 1}...')

            data = self.fetch_timeline(max_id=next_cursor)

            posts = data.get('data', [])
            all_posts.extend(posts)

            # 获取下一页游标
            next_cursor = data.get('next_cursor')
            if not next_cursor:
                print('No more data')
                break

            # 礼貌延迟
            time.sleep(2)

        return all_posts

# 使用
scraper = WeiboScraper(cookie='YOUR_COOKIE_HERE')
posts = scraper.scrape_all(max_pages=5)

for post in posts:
    print(f"[{post['id']}] {post['text']}")
```

---

## 案例二：Instagram/抖音图片/视频 URL 解密

### 背景

社交媒体平台的图片/视频 URL 通常经过加密或签名：

- 防止直接下载
- 防止盗链
- 添加时效性（URL 在一定时间后失效）

---

### 逆向步骤

#### 1. 观察图片加载

在 Network 面板中观察图片请求：

```http
GET /img/v2/abc123?sig=def456&ts=1702800000 HTTP/1.1
```

参数：

- `sig`: 签名
- `ts`: 时间戳

#### 2. 定位签名生成函数

在 Sources 面板搜索 `sig` 或 `signature`，找到生成逻辑：

```javascript
function generateImageSignature(imageId, timestamp) {
  // 拼接字符串
  const str = `${imageId}:${timestamp}:${SECRET_SALT}`;

  // MD5 签名
  return md5(str);
}

// 使用
const imageId = "abc123";
const timestamp = Math.floor(Date.now() / 1000);
const sig = generateImageSignature(imageId, timestamp);

const imageUrl = `/img/v2/${imageId}?sig=${sig}&ts=${timestamp}`;
```

**密钥提取**:

```javascript
// 搜索 "SECRET_SALT" 或硬编码的字符串
const SECRET_SALT = "my_secret_key_2023";
```

#### 3. Python 实现

```python
import hashlib
import time

class MediaDownloader:
    SECRET_SALT = "my_secret_key_2023"  # 从 JS 中提取

    def generate_signature(self, media_id, timestamp):
        """生成签名"""
        str_to_sign = f"{media_id}:{timestamp}:{self.SECRET_SALT}"
        return hashlib.md5(str_to_sign.encode()).hexdigest()

    def get_media_url(self, media_id):
        """生成有签名的媒体 URL"""
        timestamp = int(time.time())
        sig = self.generate_signature(media_id, timestamp)

        return f"https://example.com/img/v2/{media_id}?sig={sig}&ts={timestamp}"

    def download(self, media_id, save_path):
        """下载媒体"""
        url = self.get_media_url(media_id)
        response = requests.get(url)

        with open(save_path, 'wb') as f:
            f.write(response.content)

        print(f'Downloaded to {save_path}')

# 使用
downloader = MediaDownloader()
downloader.download('abc123', 'image.jpg')
```

---

## 案例三：GraphQL API 逆向

### 背景

现代社交媒体（如 Facebook, Instagram, GitHub）使用 GraphQL 而非 REST API：

- 单个端点处理所有请求
- 客户端指定需要的字段
- 复杂的查询结构

---

### 逆向步骤

#### 1. 抓包分析 GraphQL 请求

```http
POST /graphql HTTP/1.1
Content-Type: application/json

{
    "query": "query UserTimeline($userId: ID!, $first: Int!) { user(id: $userId) { posts(first: $first) { edges { node { id text created_at likes { count } } } } } }",
    "variables": {
        "userId": "12345",
        "first": 20
    }
}
```

#### 2. 理解查询结构

查询格式化后：

```graphql
query UserTimeline($userId: ID!, $first: Int!) {
  user(id: $userId) {
    posts(first: $first) {
      edges {
        node {
          id
          text
          created_at
          likes {
            count
          }
        }
      }
    }
  }
}
```

#### 3. Python 实现

```python
import requests

class GraphQLClient:
    def __init__(self, endpoint, token):
        self.endpoint = endpoint
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

    def query(self, query_string, variables=None):
        """执行 GraphQL 查询"""
        payload = {'query': query_string}
        if variables:
            payload['variables'] = variables

        response = requests.post(
            self.endpoint,
            json=payload,
            headers=self.headers
        )

        return response.json()

    def get_user_posts(self, user_id, first=20):
        """获取用户帖子"""
        query = """
        query UserTimeline($userId: ID!, $first: Int!) {
          user(id: $userId) {
            posts(first: $first) {
              edges {
                node {
                  id
                  text
                  created_at
                  likes {
                    count
                  }
                  comments {
                    count
                  }
                }
              }
            }
          }
        }
        """

        variables = {
            'userId': user_id,
            'first': first
        }

        return self.query(query, variables)

# 使用
client = GraphQLClient(
    endpoint='https://example.com/graphql',
    token='YOUR_TOKEN_HERE'
)

result = client.get_user_posts(user_id='12345', first=50)

# 解析结果
posts = result['data']['user']['posts']['edges']
for edge in posts:
    post = edge['node']
    print(f"[{post['id']}] {post['text']}")
    print(f"Likes: {post['likes']['count']}, Comments: {post['comments']['count']}")
```

---

## 案例四：实时通知与 WebSocket

### 背景

社交媒体的实时通知（新消息、点赞、评论）通常使用 WebSocket：

- 双向通信
- 服务器主动推送
- 保持长连接

---

### 逆向步骤

#### 1. 观察 WebSocket 连接

在 Network 面板的 WS 标签中查看：

```javascript
// 连接建立
ws://example.com/ws?token=abc123&userId=12345

// 接收消息
{
    "type": "notification",
    "data": {
        "id": "notify_123",
        "type": "like",
        "from_user": "user_456",
        "post_id": "post_789",
        "timestamp": 1702800000
    }
}

// 发送消息（心跳）
{
    "type": "ping",
    "timestamp": 1702800000
}
```

#### 2. Hook WebSocket

```javascript
// Hook WebSocket 构造函数
const OriginalWebSocket = window.WebSocket;
window.WebSocket = function (url, protocols) {
  console.log("[WebSocket] Connecting to:", url);

  const ws = new OriginalWebSocket(url, protocols);

  // Hook onmessage
  const originalOnMessage = ws.onmessage;
  ws.onmessage = function (event) {
    console.log("[WebSocket] Received:", event.data);
    if (originalOnMessage) {
      originalOnMessage.call(this, event);
    }
  };

  // Hook send
  const originalSend = ws.send;
  ws.send = function (data) {
    console.log("[WebSocket] Sending:", data);
    return originalSend.call(this, data);
  };

  return ws;
};
```

#### 3. Python 实现 WebSocket 客户端

```python
import websocket
import json
import threading
import time

class SocialMediaWS:
    def __init__(self, token, user_id):
        self.token = token
        self.user_id = user_id
        self.ws = None
        self.running = False

    def on_message(self, ws, message):
        """接收消息回调"""
        data = json.loads(message)
        print(f'[Received] {data}')

        if data['type'] == 'notification':
            self.handle_notification(data['data'])

    def on_error(self, ws, error):
        """错误回调"""
        print(f'[Error] {error}')

    def on_close(self, ws, close_status_code, close_msg):
        """关闭回调"""
        print(f'[Closed] Code: {close_status_code}, Message: {close_msg}')
        self.running = False

    def on_open(self, ws):
        """连接建立回调"""
        print('[Connected]')
        self.running = True

        # 启动心跳线程
        threading.Thread(target=self.send_heartbeat, daemon=True).start()

    def send_heartbeat(self):
        """发送心跳"""
        while self.running:
            if self.ws:
                ping_msg = json.dumps({
                    'type': 'ping',
                    'timestamp': int(time.time())
                })
                self.ws.send(ping_msg)
                print('[Heartbeat] Sent')

            time.sleep(30)  # 每30秒一次

    def handle_notification(self, data):
        """处理通知"""
        notif_type = data['type']
        if notif_type == 'like':
            print(f"User {data['from_user']} liked your post {data['post_id']}")
        elif notif_type == 'comment':
            print(f"User {data['from_user']} commented on your post")
        elif notif_type == 'follow':
            print(f"User {data['from_user']} followed you")

    def connect(self):
        """建立连接"""
        url = f"ws://example.com/ws?token={self.token}&userId={self.user_id}"

        self.ws = websocket.WebSocketApp(
            url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )

        # 运行（阻塞）
        self.ws.run_forever()

    def disconnect(self):
        """断开连接"""
        self.running = False
        if self.ws:
            self.ws.close()

# 使用
ws_client = SocialMediaWS(token='YOUR_TOKEN', user_id='12345')
ws_client.connect()  # 阻塞运行
```

---

## 案例五：推荐算法参数逆向

### 背景

社交媒体的推荐算法会根据用户行为调整内容：

- 点赞、评论、分享
- 停留时间
- 滚动速度
- 交互频率

这些数据通过 API 发送到服务器。

---

### 逆向步骤

#### 1. 抓包分析行为上报

```http
POST /api/behavior HTTP/1.1
Content-Type: application/json

{
    "session_id": "sess_123",
    "events": [
        {
            "type": "view",
            "post_id": "post_789",
            "duration": 5.2,  // 停留时间（秒）
            "timestamp": 1702800000
        },
        {
            "type": "like",
            "post_id": "post_789",
            "timestamp": 1702800005
        },
        {
            "type": "share",
            "post_id": "post_789",
            "platform": "wechat",
            "timestamp": 1702800010
        }
    ]
}
```

#### 2. 定位行为追踪代码

```javascript
// 追踪帖子浏览
const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      const postId = entry.target.dataset.postId;
      const viewStart = Date.now();

      // 记录开始时间
      viewTimers[postId] = viewStart;
    } else {
      const postId = entry.target.dataset.postId;
      if (viewTimers[postId]) {
        const duration = (Date.now() - viewTimers[postId]) / 1000;

        // 上报浏览事件
        trackEvent({
          type: "view",
          post_id: postId,
          duration: duration,
        });

        delete viewTimers[postId];
      }
    }
  });
});

// 监听所有帖子
document.querySelectorAll(".post").forEach((post) => {
  observer.observe(post);
});

// 追踪点赞
function handleLike(postId) {
  trackEvent({
    type: "like",
    post_id: postId,
    timestamp: Date.now(),
  });

  // 实际的点赞请求
  fetch("/api/like", {
    method: "POST",
    body: JSON.stringify({ post_id: postId }),
  });
}
```

#### 3. 批量上报优化

```javascript
// 批量收集事件
let eventQueue = [];

function trackEvent(event) {
  event.timestamp = Date.now();
  eventQueue.push(event);

  // 达到阈值或超时后批量发送
  if (eventQueue.length >= 10) {
    flushEvents();
  }
}

function flushEvents() {
  if (eventQueue.length === 0) return;

  fetch("/api/behavior", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: sessionId,
      events: eventQueue,
    }),
  });

  eventQueue = [];
}

// 定时刷新
setInterval(flushEvents, 30000); // 每30秒

// 页面卸载时发送
window.addEventListener("beforeunload", flushEvents);
```

---

## 反爬虫对抗

### 常见检测手段

1. **频率限制**

   - 单 IP 每分钟请求限制
   - 账号每日爬取上限

2. **行为分析**

   - 鼠标移动轨迹
   - 滚动行为
   - 停留时间分布

3. **设备指纹**

   - Canvas 指纹
   - WebGL 指纹
   - 字体指纹

4. **验证码**
   - 滑块验证
   - 图片识别
   - 行为验证

### 绕过策略

```python
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import random

class StealthScraper:
    def __init__(self):
        # 使用 undetected-chromedriver 绕过检测
        options = uc.ChromeOptions()
        options.add_argument('--disable-blink-features=AutomationControlled')

        self.driver = uc.Chrome(options=options)

    def human_like_scroll(self):
        """模拟真人滚动"""
        # 随机滚动距离
        scroll_distance = random.randint(300, 700)

        # 分多次滚动（模拟真人）
        for _ in range(random.randint(3, 6)):
            self.driver.execute_script(f"window.scrollBy(0, {random.randint(50, 150)})")
            time.sleep(random.uniform(0.1, 0.3))

        # 停顿
        time.sleep(random.uniform(1, 3))

    def scrape_feed(self):
        """爬取信息流"""
        self.driver.get('https://example.com/feed')
        time.sleep(3)

        posts = []
        for page in range(5):
            # 模拟真人滚动
            self.human_like_scroll()

            # 提取帖子
            post_elements = self.driver.find_elements(By.CLASS_NAME, 'post')
            for elem in post_elements:
                posts.append({
                    'id': elem.get_attribute('data-post-id'),
                    'text': elem.find_element(By.CLASS_NAME, 'text').text
                })

            # 随机停顿
            time.sleep(random.uniform(2, 5))

        return posts

# 使用
scraper = StealthScraper()
posts = scraper.scrape_feed()
```

---

## 总结

社交媒体逆向的关键技术：

1. **分页机制理解**

   - 游标分页
   - 时间戳分页
   - ID 分页

2. **API 逆向**

   - REST API
   - GraphQL
   - WebSocket

3. **签名与加密**

   - URL 签名
   - 参数加密
   - Token 生成

4. **行为模拟**

   - 鼠标轨迹
   - 滚动行为
   - 随机延迟

5. **反检测**
   - 设备指纹伪造
   - 代理轮换
   - 无头浏览器检测绕过

---

## 相关章节

- [GraphQL API 分析](../02-Techniques/graphql_analysis.md)
- [WebSocket 通信分析](../02-Techniques/websocket_analysis.md)
- [无限滚动加载](../02-Techniques/infinite_scroll.md)
- [设备指纹识别](../03-Advanced-Topics/device_fingerprinting.md)
