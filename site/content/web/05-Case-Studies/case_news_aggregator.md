---
title: "新闻聚合网站"
date: 2025-06-14
weight: 10
---

# 新闻聚合网站

## 概述

新闻聚合网站（如 Hacker News、Reddit、今日头条）汇集多个新闻源，并提供个性化推荐。本文通过 5 个真实案例，深入讲解新闻聚合平台的逆向技术。

---

## 案例 1: RSS/Atom Feed 聚合与解析

### 背景

传统新闻聚合依赖 RSS/Atom feeds。逆向这些 feeds 可以实现自定义新闻聚合器。

### Feed 格式

#### RSS 2.0

```xml
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
<title>Example News</title>
<link>https://news.example.com</link>
<description>Latest news from Example</description>
<item>
<title>Breaking News: AI Breakthrough</title>
<link>https://news.example.com/article/123</link>
<description>Scientists announce major AI advancement...</description>
<pubDate>Mon, 18 Dec 2023 10:00:00 GMT</pubDate>
<guid>https://news.example.com/article/123</guid>
</item>
</channel>
</rss>
```

#### Atom 1.0

```xml
<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
<title>Example News</title>
<link href="https://news.example.com"/>
<updated>2023-12-18T10:00:00Z</updated>
<entry>
<title>Breaking News: AI Breakthrough</title>
<link href="https://news.example.com/article/123"/>
<id>urn:uuid:1234-5678-90ab-cdef</id>
<updated>2023-12-18T10:00:00Z</updated>
<summary>Scientists announce major AI advancement...</summary>
</entry>
</feed>
```

### Python 实现 - RSS 聚合器

```python
import feedparser
import requests
from datetime import datetime
from typing import List, Dict
import sqlite3

class RSSAggregator:
def __init__(self, db_path='news.db'):
self.db_path = db_path
self.init_database()

def init_database(self):
"""初始化数据库"""
conn = sqlite3.connect(self.db_path)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS articles (
id INTEGER PRIMARY KEY AUTOINCREMENT,
title TEXT,
link TEXT UNIQUE,
description TEXT,
published DATETIME,
source TEXT,
category TEXT,
read BOOLEAN DEFAULT 0
)
''')

conn.commit()
conn.close()

def fetch_feed(self, feed_url: str, source_name: str):
"""获取并解析 RSS/Atom feed"""
try:
# 使用 feedparser 自动检测格式
feed = feedparser.parse(feed_url)

articles = []

for entry in feed.entries:
article = {
'title': entry.get('title', ''),
'link': entry.get('link', ''),
'description': entry.get('description') or entry.get('summary', ''),
'published': self._parse_date(entry.get('published', '')),
'source': source_name,
'category': self._extract_category(entry)
}

articles.append(article)

return articles

except Exception as e:
print(f"Error fetching {feed_url}: {e}")
return []

def _parse_date(self, date_str):
"""解析日期"""
if not date_str:
return datetime.now()

try:
# feedparser 已经解析了日期
from email.utils import parsedate_to_datetime
return parsedate_to_datetime(date_str)
except:
return datetime.now()

def _extract_category(self, entry):
"""提取分类"""
# 从 tags 中提取
if hasattr(entry, 'tags'):
return ', '.join([tag.term for tag in entry.tags[:3]])

# 从 category 中提取
if hasattr(entry, 'category'):
return entry.category

return 'General'

def save_articles(self, articles: List[Dict]):
"""保存文章到数据库"""
conn = sqlite3.connect(self.db_path)
cursor = conn.cursor()

for article in articles:
try:
cursor.execute('''
INSERT OR IGNORE INTO articles
(title, link, description, published, source, category)
VALUES (?, ?, ?, ?, ?, ?)
''', (
article['title'],
article['link'],
article['description'],
article['published'],
article['source'],
article['category']
))
except Exception as e:
print(f"Error saving article: {e}")

conn.commit()
conn.close()

def aggregate_multiple_feeds(self, feeds: Dict[str, str]):
"""
聚合多个 feeds
feeds: {'Source Name': 'feed_url', ...}
"""
all_articles = []

for source_name, feed_url in feeds.items():
print(f"Fetching {source_name}...")
articles = self.fetch_feed(feed_url, source_name)
all_articles.extend(articles)

self.save_articles(all_articles)
print(f"Total articles fetched: {len(all_articles)}")

return all_articles

def get_latest_articles(self, limit=20, category=None):
"""获取最新文章"""
conn = sqlite3.connect(self.db_path)
cursor = conn.cursor()

if category:
cursor.execute('''
SELECT * FROM articles
WHERE category LIKE ?
ORDER BY published DESC
LIMIT ?
''', (f'%{category}%', limit))
else:
cursor.execute('''
SELECT * FROM articles
ORDER BY published DESC
LIMIT ?
''', (limit,))

articles = cursor.fetchall()
conn.close()

return articles

# 使用示例
aggregator = RSSAggregator()

# 定义 feeds
feeds = {
'Hacker News': 'https://news.ycombinator.com/rss',
'TechCrunch': 'https://techcrunch.com/feed/',
'Ars Technica': 'https://feeds.arstechnica.com/arstechnica/index',
'The Verge': 'https://www.theverge.com/rss/index.xml',
'Reddit Python': 'https://www.reddit.com/r/python/.rss'
}

# 聚合所有 feeds
aggregator.aggregate_multiple_feeds(feeds)

# 获取最新 20 篇文章
latest = aggregator.get_latest_articles(limit=20)

for article in latest:
print(f"[{article[5]}] {article[1]}") # [source] title
print(f" {article[2]}") # link
print()
```

### 高级功能

#### 1. Feed 自动发现

某些网站没有明显的 RSS 链接，需要自动发现:

```python
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def discover_feeds(url):
"""自动发现网站的 RSS/Atom feeds"""
try:
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

feeds = []

# 查找 <link> 标签
for link in soup.find_all('link', type=['application/rss+xml', 'application/atom+xml']):
feed_url = urljoin(url, link.get('href', ''))
feed_title = link.get('title', 'Untitled Feed')

feeds.append({
'url': feed_url,
'title': feed_title,
'type': link.get('type')
})

# 常见的 feed 路径
common_paths = ['/feed', '/rss', '/atom.xml', '/rss.xml', '/feed.xml']

for path in common_paths:
test_url = urljoin(url, path)
try:
r = requests.head(test_url, timeout=3)
if r.status_code == 200:
feeds.append({
'url': test_url,
'title': f'Feed at {path}',
'type': 'application/rss+xml'
})
except:
continue

return feeds

except Exception as e:
print(f"Error discovering feeds: {e}")
return []

# 使用示例
feeds = discover_feeds('https://blog.example.com')
for feed in feeds:
print(f"{feed['title']}: {feed['url']}")
```

#### 2. Full Content Extraction

RSS feed 通常只包含摘要，需要提取完整内容:

```python
from newspaper import Article
import re

class FullContentExtractor:
def __init__(self):
pass

def extract_article(self, url):
"""提取完整文章内容"""
try:
article = Article(url)
article.download()
article.parse()

# NLP 处理（可选）
article.nlp()

return {
'title': article.title,
'authors': article.authors,
'publish_date': article.publish_date,
'text': article.text,
'top_image': article.top_image,
'videos': article.movies,
'keywords': article.keywords,
'summary': article.summary
}

except Exception as e:
print(f"Error extracting {url}: {e}")
return None

def clean_text(self, text):
"""清理文本"""
# 移除多余空行
text = re.sub(r'\n{3,}', '\n\n', text)

# 移除广告标记
ad_patterns = [
r'\[广告\].*?\n',
r'Advertisement.*?\n',
r'Sponsored.*?\n'
]

for pattern in ad_patterns:
text = re.sub(pattern, '', text, flags=re.IGNORECASE)

return text.strip()

# 使用示例
extractor = FullContentExtractor()
content = extractor.extract_article('https://news.example.com/article/123')

if content:
print(f"Title: {content['title']}")
print(f"Summary: {content['summary']}")
```

---

## 案例 2: 个性化推荐算法逆向

### 背景

新闻聚合平台（如今日头条、Reddit）使用推荐算法个性化内容。逆向这些算法可以理解推荐机制。

### Reddit 排名算法

Reddit 使用 "Hot" 排名算法:

```python
from datetime import datetime
import math

def reddit_hot_score(ups, downs, date):
"""
Reddit Hot 算法
- ups: 点赞数
- downs: 踩数
- date: 发布时间
"""
# 计算分数
s = ups - downs

# 排序（1 表示正分，-1 表示负分，0 表示中性）
order = math.log(max(abs(s), 1), 10)

if s > 0:
sign = 1
elif s < 0:
sign = -1
else:
sign = 0

# 时间衰减（Reddit epoch: 2005-12-08 07:46:43）
epoch = datetime(2005, 12, 8, 7, 46, 43)
seconds = (date - epoch).total_seconds() - 1134028003

return round(sign * order + seconds / 45000, 7)

# 示例
post1_score = reddit_hot_score(
ups=100,
downs=10,
date=datetime.now()
)

post2_score = reddit_hot_score(
ups=500,
downs=50,
date=datetime.now()
)

print(f"Post 1 score: {post1_score}")
print(f"Post 2 score: {post2_score}")
```

### Hacker News 排名算法

```python
from datetime import datetime

def hackernews_ranking(points, num_comments, hours_since_submission, gravity=1.8):
"""
Hacker News 排名算法
- points: 点数（点赞 - 踩）
- num_comments: 评论数
- hours_since_submission: 发布后的小时数
- gravity: 重力参数（默认 1.8）
"""
return (points - 1) / pow((hours_since_submission + 2), gravity)

# 示例
story1_rank = hackernews_ranking(
points=150,
num_comments=30,
hours_since_submission=2
)

story2_rank = hackernews_ranking(
points=80,
num_comments=10,
hours_since_submission=6
)

print(f"Story 1 rank: {story1_rank}")
print(f"Story 2 rank: {story2_rank}")
```

### 今日头条推荐逆向

通过抓包分析，发现今日头条使用以下参数:

```python
import requests
import hashlib
import time
import json

class ToutiaoRecommender:
def __init__(self):
self.base_url = "https://www.toutiao.com/api/pc/feed/"
self.session = requests.Session()

def generate_signature(self, timestamp):
"""
生成签名
逆向自 Toutiao 的 JS 代码
"""
# 简化版本（实际算法更复杂）
secret = "toutiao_secret_2024"
str_to_sign = f"{timestamp}|{secret}"
return hashlib.md5(str_to_sign.encode()).hexdigest()

def get_recommendations(self, category='news', count=20):
"""获取推荐内容"""
timestamp = int(time.time())
signature = self.generate_signature(timestamp)

params = {
'category': category,
'count': count,
'min_behot_time': timestamp,
'_signature': signature
}

headers = {
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
'Referer': 'https://www.toutiao.com/'
}

response = self.session.get(
self.base_url,
params=params,
headers=headers
)

data = response.json()

articles = []
for item in data.get('data', []):
article = {
'title': item.get('title'),
'url': item.get('source_url'),
'abstract': item.get('abstract'),
'source': item.get('source'),
'publish_time': item.get('publish_time'),
'has_video': item.get('has_video', False),
'image_url': item.get('image_url')
}
articles.append(article)

return articles

# 使用示例
recommender = ToutiaoRecommender()
articles = recommender.get_recommendations(category='tech', count=10)

for article in articles:
print(f"[{article['source']}] {article['title']}")
print(f" {article['url']}")
```

### 协同过滤推荐实现

```python
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class CollaborativeFilteringRecommender:
def __init__(self):
self.user_item_matrix = None
self.item_similarity = None

def fit(self, user_item_matrix):
"""
训练推荐模型
user_item_matrix: numpy array, shape (n_users, n_items)
"""
self.user_item_matrix = user_item_matrix

# 计算物品相似度（基于用户行为）
self.item_similarity = cosine_similarity(user_item_matrix.T)

def recommend(self, user_id, top_n=10):
"""为用户推荐 top_n 篇文章"""
# 获取用户已阅读的文章
user_ratings = self.user_item_matrix[user_id]

# 计算推荐分数
scores = self.item_similarity.T.dot(user_ratings)

# 排除已阅读的文章
scores[user_ratings > 0] = -1

# 返回 top_n
top_items = np.argsort(scores)[::-1][:top_n]

return top_items

# 示例
# 用户-文章矩阵（1 表示阅读，0 表示未阅读）
user_item_matrix = np.array([
[1, 1, 0, 0, 1, 0], # 用户 0
[1, 0, 1, 0, 0, 1], # 用户 1
[0, 1, 1, 1, 0, 0], # 用户 2
[0, 0, 1, 1, 1, 1], # 用户 3
])

recommender = CollaborativeFilteringRecommender()
recommender.fit(user_item_matrix)

# 为用户 0 推荐
recommendations = recommender.recommend(user_id=0, top_n=3)
print(f"Recommended articles for user 0: {recommendations}")
```

---

## 案例 3: 实时新闻推送（WebSocket/SSE）

### 背景

现代新闻网站使用 WebSocket 或 Server-Sent Events (SSE) 推送实时新闻。

### WebSocket 实时推送

#### 服务端（Node.js）

```javascript
const WebSocket = require("ws");
const wss = new WebSocket.Server({ port: 8080 });

// 模拟新闻源
function getLatestNews() {
return {
id: Date.now(),
title: `Breaking News at ${new Date().toLocaleTimeString()}`,
content: "Lorem ipsum dolor sit amet...",
timestamp: Date.now(),
};
}

// 广播给所有客户端
wss.on("connection", (ws) => {
console.log("New client connected");

// 每 5 秒推送一条新闻
const interval = setInterval(() => {
const news = getLatestNews();
ws.send(JSON.stringify(news));
}, 5000);

ws.on("close", () => {
clearInterval(interval);
console.log("Client disconnected");
});
});
```

#### 客户端（Python）

```python
import websocket
import json
import threading

class RealtimeNewsClient:
def __init__(self, ws_url):
self.ws_url = ws_url
self.ws = None
self.news_callback = None

def on_message(self, ws, message):
"""收到消息时的回调"""
try:
news = json.loads(message)
print(f"[{news['timestamp']}] {news['title']}")

if self.news_callback:
self.news_callback(news)

except Exception as e:
print(f"Error parsing message: {e}")

def on_error(self, ws, error):
"""错误回调"""
print(f"WebSocket error: {error}")

def on_close(self, ws, close_status_code, close_msg):
"""连接关闭回调"""
print("WebSocket connection closed")

def on_open(self, ws):
"""连接建立回调"""
print("WebSocket connection opened")

def connect(self, callback=None):
"""连接到 WebSocket 服务器"""
self.news_callback = callback

self.ws = websocket.WebSocketApp(
self.ws_url,
on_open=self.on_open,
on_message=self.on_message,
on_error=self.on_error,
on_close=self.on_close
)

# 在单独的线程中运行
wst = threading.Thread(target=self.ws.run_forever)
wst.daemon = True
wst.start()

def send(self, message):
"""发送消息"""
if self.ws:
self.ws.send(json.dumps(message))

def close(self):
"""关闭连接"""
if self.ws:
self.ws.close()

# 使用示例
def handle_news(news):
"""处理接收到的新闻"""
print(f"Received: {news['title']}")
# 保存到数据库、发送通知等

client = RealtimeNewsClient('ws://localhost:8080')
client.connect(callback=handle_news)

# 保持运行
import time
try:
while True:
time.sleep(1)
except KeyboardInterrupt:
client.close()
```

### Server-Sent Events (SSE)

#### 服务端（Python Flask）

```python
from flask import Flask, Response
import time
import json

app = Flask(__name__)

def generate_news_stream():
"""生成新闻流"""
while True:
news = {
'id': int(time.time()),
'title': f'Breaking News at {time.strftime("%H:%M:%S")}',
'content': 'Lorem ipsum dolor sit amet...',
'timestamp': int(time.time())
}

# SSE 格式
yield f"data: {json.dumps(news)}\n\n"

time.sleep(5)

@app.route('/news/stream')
def news_stream():
"""SSE 端点"""
return Response(
generate_news_stream(),
mimetype='text/event-stream',
headers={
'Cache-Control': 'no-cache',
'X-Accel-Buffering': 'no'
}
)

if __name__ == '__main__':
app.run(debug=True, threaded=True)
```

#### 客户端（Python）

```python
import requests
import json

class SSENewsClient:
def __init__(self, sse_url):
self.sse_url = sse_url

def listen(self, callback):
"""监听 SSE 事件"""
headers = {
'Accept': 'text/event-stream',
'Cache-Control': 'no-cache'
}

response = requests.get(
self.sse_url,
stream=True,
headers=headers
)

# 逐行读取
for line in response.iter_lines():
if line:
decoded_line = line.decode('utf-8')

# SSE 事件格式: "data: {...}"
if decoded_line.startswith('data:'):
data = decoded_line[5:].strip()

try:
news = json.loads(data)
callback(news)
except Exception as e:
print(f"Error parsing SSE data: {e}")

# 使用示例
def handle_sse_news(news):
print(f"[SSE] {news['title']}")

client = SSENewsClient('http://localhost:5000/news/stream')
client.listen(callback=handle_sse_news)
```

---

## 案例 4: 付费墙绕过与内容提取

### 背景

许多新闻网站使用付费墙（Paywall）限制内容访问。常见类型包括硬付费墙和软付费墙。

### 软付费墙类型

#### 1. JavaScript 隐藏内容

内容在 HTML 中，但用 CSS/JS 隐藏:

```html
<div class="article-content">
<p>First paragraph visible...</p>
<div class="paywall-blur">
<p>Premium content hidden here...</p>
<p>More premium content...</p>
</div>
</div>

<div class="paywall-overlay">
<h3>Subscribe to read more</h3>
<button>Subscribe Now</button>
</div>

<style>
.paywall-blur {
filter: blur(5px);
user-select: none;
}
</style>
```

**绕过方法**:

```python
from bs4 import BeautifulSoup
import requests

def bypass_soft_paywall(url):
"""绕过软付费墙"""
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# 移除付费墙遮罩
for overlay in soup.find_all(class_='paywall-overlay'):
overlay.decompose()

# 移除模糊效果（通过提取原始内容）
blurred = soup.find_all(class_='paywall-blur')
for element in blurred:
element['class'] = [] # 移除 class

# 提取完整文本
article = soup.find(class_='article-content')
return article.get_text(strip=True) if article else None

# 使用示例
content = bypass_soft_paywall('https://news.example.com/premium-article')
print(content)
```

#### 2. Cookie 限制

限制免费文章数量（通过 Cookie 追踪）:

```python
class PaywallBypass:
def __init__(self):
self.session = requests.Session()

def clear_cookies(self):
"""清除 cookies 重置计数"""
self.session.cookies.clear()

def use_incognito_headers(self):
"""使用隐身模式请求头"""
self.session.headers.update({
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
'Referer': 'https://www.google.com/',
'DNT': '1'
})

def get_article(self, url):
"""获取文章（绕过 cookie 限制）"""
self.clear_cookies()
self.use_incognito_headers()

response = self.session.get(url)
return response.text

# 使用示例
bypass = PaywallBypass()
content = bypass.get_article('https://news.example.com/article/123')
```

#### 3. Google/Facebook Referrer 绕过

某些网站允许从搜索引擎/社交媒体来的流量:

```python
def bypass_with_referrer(url):
"""使用 Referrer 绕过付费墙"""
headers = {
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
'Referer': 'https://www.google.com/' # 或 'https://t.co/'
}

response = requests.get(url, headers=headers)
return response.text

# 使用示例
content = bypass_with_referrer('https://news.example.com/article/123')
```

### Archive.is / Web Archive 绕过

```python
import requests
from urllib.parse import quote

class ArchiveBypass:
def __init__(self):
self.archive_api = "https://archive.is/submit/"
self.wayback_api = "https://web.archive.org/save/"

def archive_is(self, url):
"""使用 Archive.is 存档并获取内容"""
# 提交存档请求
data = {'url': url}
response = requests.post(self.archive_api, data=data, allow_redirects=False)

# 获取存档 URL
archive_url = response.headers.get('Location')

if archive_url:
# 获取存档内容
archive_content = requests.get(archive_url).text
return archive_content
else:
return None

def wayback_machine(self, url):
"""使用 Wayback Machine"""
# 保存快照
save_url = f"{self.wayback_api}{url}"
requests.get(save_url)

# 获取最新快照
snapshot_url = f"https://web.archive.org/web/{url}"
response = requests.get(snapshot_url)

return response.text

# 使用示例
bypass = ArchiveBypass()
content = bypass.archive_is('https://news.example.com/premium-article')
```

---

## 案例 5: 反爬虫对抗与内容去重

### 背景

新闻聚合网站需要处理大量内容，同时避免被源网站封禁。

### User-Agent 轮换

```python
import random

class UserAgentRotator:
def __init__(self):
self.user_agents = [
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15',
'Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15'
]

def get_random_ua(self):
"""获取随机 User-Agent"""
return random.choice(self.user_agents)

def make_request(self, url):
"""使用随机 UA 发送请求"""
headers = {'User-Agent': self.get_random_ua()}
response = requests.get(url, headers=headers)
return response.text
```

### 内容去重（SimHash）

```python
import hashlib
from collections import defaultdict

class ContentDeduplicator:
def __init__(self, threshold=3):
"""
threshold: 汉明距离阈值（越小越严格）
"""
self.threshold = threshold
self.seen_hashes = {}

def simhash(self, text, hashbits=64):
"""计算文本的 SimHash"""
# 分词（简化版本）
tokens = text.lower().split()

# 词频统计
freq = defaultdict(int)
for token in tokens:
freq[token] += 1

# 初始化向量
vector = [0] * hashbits

for token, weight in freq.items():
# 计算 token 的 hash
h = int(hashlib.md5(token.encode()).hexdigest(), 16)

for i in range(hashbits):
# 检查第 i 位是否为 1
if h & (1 << i):
vector[i] += weight
else:
vector[i] -= weight

# 生成 SimHash
fingerprint = 0
for i in range(hashbits):
if vector[i] > 0:
fingerprint |= (1 << i)

return fingerprint

def hamming_distance(self, hash1, hash2):
"""计算汉明距离"""
x = hash1 ^ hash2
distance = 0

while x:
distance += 1
x &= x - 1

return distance

def is_duplicate(self, text, article_id):
"""检查文章是否重复"""
fingerprint = self.simhash(text)

# 检查是否与已存在的文章相似
for existing_id, existing_hash in self.seen_hashes.items():
distance = self.hamming_distance(fingerprint, existing_hash)

if distance <= self.threshold:
return True, existing_id

# 保存新文章的 hash
self.seen_hashes[article_id] = fingerprint

return False, None

# 使用示例
dedup = ContentDeduplicator(threshold=3)

articles = [
{'id': 1, 'text': 'Breaking news: AI makes major breakthrough in language processing'},
{'id': 2, 'text': 'Breaking news: AI makes significant breakthrough in language processing'},
{'id': 3, 'text': 'Weather forecast shows sunny skies ahead'},
]

for article in articles:
is_dup, original_id = dedup.is_duplicate(article['text'], article['id'])

if is_dup:
print(f"Article {article['id']} is duplicate of {original_id}")
else:
print(f"Article {article['id']} is unique")
```

### 智能限流

```python
import time
from collections import deque

class RateLimiter:
def __init__(self, max_requests, time_window):
"""
max_requests: 时间窗口内的最大请求数
time_window: 时间窗口（秒）
"""
self.max_requests = max_requests
self.time_window = time_window
self.requests = deque()

def wait_if_needed(self):
"""如果需要，等待直到可以发送请求"""
now = time.time()

# 移除超出时间窗口的请求
while self.requests and self.requests[0] < now - self.time_window:
self.requests.popleft()

# 如果达到限制，等待
if len(self.requests) >= self.max_requests:
sleep_time = self.requests[0] + self.time_window - now
if sleep_time > 0:
print(f"Rate limit reached, waiting {sleep_time:.2f} seconds...")
time.sleep(sleep_time)

# 记录本次请求
self.requests.append(time.time())

def request(self, url):
"""发送受限流控制的请求"""
self.wait_if_needed()
response = requests.get(url)
return response

# 使用示例
limiter = RateLimiter(max_requests=10, time_window=60) # 每分钟最多 10 次

for i in range(20):
response = limiter.request(f'https://news.example.com/article/{i}')
print(f"Fetched article {i}")
```

---

## 防护与对抗总结

### 新闻聚合平台防护

1. **付费墙**: JavaScript 隐藏、Cookie 限制、订阅验证
2. **反爬虫**: User-Agent 检测、频率限制、CAPTCHA
3. **内容保护**: 反调试、混淆、水印
4. **API 限流**: Token 验证、IP 限制
5. **版权保护**: DMCA 通知、法律行动

### 对抗策略

1. **付费墙绕过**: Referrer 欺骗、Archive 存档、浏览器扩展
2. **智能爬取**: UA 轮换、代理池、延迟控制
3. **内容提取**: newspaper3k、Readability、自定义解析器
4. **去重算法**: SimHash、MinHash、LSH
5. **分布式采集**: 多节点、任务队列、增量更新

---

## 法律与道德声明

**本文仅用于技术研究和教育目的**。未经授权爬取和绕过付费墙可能违反:

- 网站服务条款 (ToS)
- 版权法 (Copyright Law)
- 计算机欺诈和滥用法 (CFAA)
- 数字千年版权法 (DMCA)

请仅在授权环境下进行测试，尊重内容创作者的权益和版权。

---

## 工具推荐

### RSS/Atom 工具

- **feedparser**: Python RSS/Atom 解析库
- **Feedly**: 商业 RSS 聚合服务
- **Inoreader**: RSS 阅读器

### 内容提取

- **newspaper3k**: 新闻文章提取
- **Readability**: 内容提取算法
- **Trafilatura**: 网页内容提取
- **BeautifulSoup**: HTML 解析

### 去重算法

- **simhash**: 文本指纹
- **datasketch**: MinHash 实现
- **faiss**: 向量相似度搜索

### 实时推送

- **websocket-client**: Python WebSocket 客户端
- **Socket.IO**: 实时通信框架
- **SSE**: Server-Sent Events

---

## 相关章节

- [HTTP/HTTPS 协议](../01-Foundations/http_https_protocol.md)
- [JavaScript Hook 技术](../02-Techniques/js_hook.md)
- [WebSocket 逆向](../03-Advanced-Topics/websocket_reversing.md)
- [内容安全策略绕过](../04-Advanced-Recipes/csp_bypass.md)
- [搜索引擎对抗](./case_search_engine.md)
