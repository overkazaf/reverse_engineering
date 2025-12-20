# 基础爬虫项目模板

一个简单但完整的 Python 爬虫项目模板，适合单机数据采集。

---

## 📁 项目结构

```
basic_scraper/
├── config/
│   ├── __init__.py
│   ├── settings.py          # 配置参数
│   └── logging.conf         # 日志配置
├── scrapers/
│   ├── __init__.py
│   ├── base_scraper.py      # 基础爬虫类
│   └── target_scraper.py    # 目标网站爬虫
├── utils/
│   ├── __init__.py
│   ├── crypto.py            # 加密解密工具
│   ├── headers.py           # 请求头生成
│   └── parser.py            # 数据解析
├── data/
│   ├── raw/                 # 原始数据
│   └── processed/           # 处理后数据
├── logs/                    # 日志目录
├── tests/
│   ├── __init__.py
│   └── test_scraper.py      # 测试用例
├── .env.example             # 环境变量示例
├── .gitignore
├── requirements.txt
├── README.md
└── main.py                  # 入口文件
```

---

## 📄 文件内容

### 1. requirements.txt

```txt
requests>=2.31.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
python-dotenv>=1.0.0
pycryptodome>=3.19.0
pymongo>=4.6.0
redis>=5.0.0
loguru>=0.7.0
```

### 2. config/settings.py

```python
"""
项目配置文件
"""
import os
from dotenv import load_dotenv
from pathlib import Path

# 加载环境变量
load_dotenv()

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

# 目标网站配置
TARGET_URL = "https://example.com"
API_BASE_URL = "https://api.example.com"

# 请求配置
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
RETRY_DELAY = 2  # 秒

# 请求头配置
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
}

# 代理配置
USE_PROXY = os.getenv('USE_PROXY', 'false').lower() == 'true'
PROXY_URL = os.getenv('PROXY_URL', '')
PROXIES = {
    'http': PROXY_URL,
    'https': PROXY_URL,
} if USE_PROXY and PROXY_URL else None

# 数据库配置
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
MONGODB_DB = os.getenv('MONGODB_DB', 'scraper_db')
MONGODB_COLLECTION = os.getenv('MONGODB_COLLECTION', 'data')

# Redis 配置
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')

# 数据存储配置
DATA_DIR = BASE_DIR / 'data'
RAW_DATA_DIR = DATA_DIR / 'raw'
PROCESSED_DATA_DIR = DATA_DIR / 'processed'

# 日志配置
LOG_DIR = BASE_DIR / 'logs'
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# 创建必要的目录
for directory in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, LOG_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# 业务配置
BATCH_SIZE = 100  # 批处理大小
SLEEP_INTERVAL = (1, 3)  # 请求间隔（秒）范围
```

### 3. config/logging.conf

```python
"""
日志配置
"""
from loguru import logger
import sys
from pathlib import Path

# 日志目录
LOG_DIR = Path(__file__).resolve().parent.parent / 'logs'
LOG_DIR.mkdir(exist_ok=True)

# 移除默认处理器
logger.remove()

# 添加控制台输出
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)

# 添加文件输出 - INFO 级别
logger.add(
    LOG_DIR / "info_{time:YYYY-MM-DD}.log",
    rotation="00:00",  # 每天午夜轮转
    retention="30 days",  # 保留30天
    encoding="utf-8",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="INFO"
)

# 添加文件输出 - ERROR 级别
logger.add(
    LOG_DIR / "error_{time:YYYY-MM-DD}.log",
    rotation="00:00",
    retention="90 days",  # 错误日志保留90天
    encoding="utf-8",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="ERROR"
)
```

### 4. scrapers/base_scraper.py

```python
"""
基础爬虫类
"""
import time
import random
import requests
from typing import Dict, Any, Optional
from config.settings import *
from config.logging import logger


class BaseScraper:
    """基础爬虫类"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)

    def request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> Optional[requests.Response]:
        """
        发送 HTTP 请求（带重试）

        Args:
            method: HTTP 方法 (GET, POST, etc.)
            url: 请求 URL
            **kwargs: 其他请求参数

        Returns:
            Response 对象或 None
        """
        for attempt in range(MAX_RETRIES):
            try:
                # 合并代理配置
                if PROXIES:
                    kwargs.setdefault('proxies', PROXIES)

                # 设置超时
                kwargs.setdefault('timeout', REQUEST_TIMEOUT)

                # 发送请求
                response = self.session.request(method, url, **kwargs)
                response.raise_for_status()

                logger.info(f"请求成功: {method} {url} - {response.status_code}")
                return response

            except requests.exceptions.RequestException as e:
                logger.warning(f"请求失败 (尝试 {attempt + 1}/{MAX_RETRIES}): {e}")

                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY * (attempt + 1))
                else:
                    logger.error(f"请求最终失败: {method} {url}")
                    return None

    def get(self, url: str, **kwargs) -> Optional[requests.Response]:
        """GET 请求"""
        return self.request('GET', url, **kwargs)

    def post(self, url: str, **kwargs) -> Optional[requests.Response]:
        """POST 请求"""
        return self.request('POST', url, **kwargs)

    def sleep(self):
        """随机休眠"""
        sleep_time = random.uniform(*SLEEP_INTERVAL)
        logger.debug(f"休眠 {sleep_time:.2f} 秒")
        time.sleep(sleep_time)

    def save_json(self, data: Dict[Any, Any], filename: str):
        """保存 JSON 数据"""
        import json
        filepath = PROCESSED_DATA_DIR / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"数据已保存: {filepath}")

    def save_csv(self, data: list, filename: str):
        """保存 CSV 数据"""
        import csv

        if not data:
            logger.warning("没有数据可保存")
            return

        filepath = PROCESSED_DATA_DIR / filename

        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)

        logger.info(f"数据已保存: {filepath} ({len(data)} 条)")
```

### 5. scrapers/target_scraper.py

```python
"""
目标网站爬虫
"""
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper
from config.settings import TARGET_URL
from config.logging import logger


class TargetScraper(BaseScraper):
    """目标网站爬虫"""

    def __init__(self):
        super().__init__()
        self.base_url = TARGET_URL

    def scrape_list(self, page: int = 1):
        """
        抓取列表页

        Args:
            page: 页码

        Returns:
            列表数据
        """
        url = f"{self.base_url}/list?page={page}"
        response = self.get(url)

        if not response:
            return []

        soup = BeautifulSoup(response.text, 'lxml')
        items = []

        # TODO: 实现具体的解析逻辑
        for item in soup.select('.item'):
            data = {
                'title': item.select_one('.title').text.strip(),
                'link': item.select_one('a')['href'],
                # 添加更多字段...
            }
            items.append(data)

        logger.info(f"页面 {page} 抓取到 {len(items)} 条数据")
        return items

    def scrape_detail(self, url: str):
        """
        抓取详情页

        Args:
            url: 详情页 URL

        Returns:
            详情数据
        """
        response = self.get(url)

        if not response:
            return None

        soup = BeautifulSoup(response.text, 'lxml')

        # TODO: 实现具体的解析逻辑
        data = {
            'url': url,
            'title': soup.select_one('h1').text.strip(),
            'content': soup.select_one('.content').text.strip(),
            # 添加更多字段...
        }

        logger.info(f"详情页抓取成功: {url}")
        return data

    def run(self, start_page: int = 1, end_page: int = 10):
        """
        运行爬虫

        Args:
            start_page: 起始页
            end_page: 结束页
        """
        logger.info(f"开始抓取: 页面 {start_page} 到 {end_page}")

        all_items = []

        for page in range(start_page, end_page + 1):
            # 抓取列表
            items = self.scrape_list(page)
            all_items.extend(items)

            # 休眠
            self.sleep()

        # 保存数据
        self.save_json(all_items, 'list_data.json')
        self.save_csv(all_items, 'list_data.csv')

        logger.info(f"抓取完成: 共 {len(all_items)} 条数据")
```

### 6. main.py

```python
"""
主程序入口
"""
from scrapers.target_scraper import TargetScraper
from config.logging import logger


def main():
    """主函数"""
    logger.info("=" * 50)
    logger.info("爬虫程序启动")
    logger.info("=" * 50)

    try:
        # 创建爬虫实例
        scraper = TargetScraper()

        # 运行爬虫
        scraper.run(start_page=1, end_page=5)

        logger.info("=" * 50)
        logger.info("爬虫程序结束")
        logger.info("=" * 50)

    except KeyboardInterrupt:
        logger.warning("用户中断程序")
    except Exception as e:
        logger.exception(f"程序异常: {e}")


if __name__ == '__main__':
    main()
```

### 7. .env.example

```bash
# 代理配置
USE_PROXY=false
PROXY_URL=http://127.0.0.1:7890

# 数据库配置
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB=scraper_db
MONGODB_COLLECTION=data

# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# 日志级别
LOG_LEVEL=INFO
```

### 8. .gitignore

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# 环境变量
.env
.env.local

# 数据和日志
data/
logs/
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo
.DS_Store

# 测试
.pytest_cache/
.coverage
htmlcov/
```

### 9. README.md

````markdown
# 基础爬虫项目

## 功能特性

- ✅ 完整的项目结构
- ✅ 配置文件管理
- ✅ 日志系统 (Loguru)
- ✅ 错误重试机制
- ✅ 代理支持
- ✅ 数据存储 (JSON/CSV)
- ✅ 环境变量配置

## 快速开始

### 1. 安装依赖

\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 2. 配置环境

\`\`\`bash
cp .env.example .env

# 编辑 .env 文件

\`\`\`

### 3. 运行爬虫

\`\`\`bash
python main.py
\`\`\`

## 项目结构

\`\`\`
.
├── config/ # 配置文件
├── scrapers/ # 爬虫模块
├── utils/ # 工具函数
├── data/ # 数据存储
├── logs/ # 日志文件
└── main.py # 入口文件
\`\`\`

## 使用说明

### 自定义爬虫

1. 编辑 `scrapers/target_scraper.py`
2. 实现 `scrape_list()` 和 `scrape_detail()` 方法
3. 修改 `config/settings.py` 中的 `TARGET_URL`

### 数据存储

数据默认保存在 `data/processed/` 目录：

- JSON 格式: `list_data.json`
- CSV 格式: `list_data.csv`

### 日志查看

日志保存在 `logs/` 目录：

- INFO 日志: `info_YYYY-MM-DD.log`
- ERROR 日志: `error_YYYY-MM-DD.log`

## License

MIT
\`\`\`

---

## 🚀 使用此模板

```bash
# 1. 复制模板
cp -r templates/basic_scraper my_project
cd my_project

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境
cp .env.example .env
vim .env

# 5. 运行
python main.py
```
````

---

## 📚 相关模板

- [逆向分析项目](./reverse_project.md)
- [Docker 部署](./docker_setup.md)
- [分布式爬虫](./distributed_crawler.md)
