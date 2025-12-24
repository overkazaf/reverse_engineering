---
title: "故障排除 - Troubleshooting"
weight: 1
---

# 故障排除 - Troubleshooting

遇到问题？这里有常见问题的解决方案和调试技巧。

---

## 问题分类

### [ 网络和请求问题](./network_issues.md)

- 请求超时
- 连接被拒绝
- SSL 证书错误
- 代理配置问题
- Cookie 失效

### [ 反爬虫问题](./anti_scraping_issues.md)

- IP 被封禁
- 验证码拦截
- User-Agent 检测
- JavaScript 挑战
- 频率限制

### [ JavaScript 调试问题](./javascript_debugging.md)

- 断点不生效
- 变量查看失败
- Source Map 错误
- 混淆代码调试
- 异步代码跟踪

### [ 工具使用问题](./tool_issues.md)

- Chrome DevTools 问题
- Burp Suite 配置
- Fiddler 代理问题
- Postman 脚本错误
- Node.js 环境问题

### [ 数据处理问题](./data_issues.md)

- 编码错误
- JSON 解析失败
- 数据库连接问题
- 文件读写错误
- 内存溢出

### [ Docker 部署问题](./docker_issues.md)

- 容器启动失败
- 网络连接问题
- 卷挂载错误
- 权限问题
- 资源限制

---

## 🆘 快速查找

### 按错误信息查找

| 错误信息 | 可能原因 | 解决方案 |
| ------------------------------- | ---------------- | ----------------------------------------------------------- |
| `Connection refused` | 目标服务器不可用 | [网络问题](./network_issues.md#连接被拒绝) |
| `SSL certificate verify failed` | SSL 证书验证失败 | [SSL 问题](./network_issues.md#ssl-证书错误) |
| `403 Forbidden` | 被反爬虫拦截 | [反爬问题](./anti_scraping_issues.md#403-forbidden) |
| `429 Too Many Requests` | 请求频率过高 | [频率限制](./anti_scraping_issues.md#429-too-many-requests) |
| `JSONDecodeError` | JSON 格式错误 | [JSON 问题](./data_issues.md#json-解析失败) |
| `UnicodeDecodeError` | 编码问题 | [编码问题](./data_issues.md#编码错误) |
| `TimeoutError` | 请求超时 | [超时问题](./network_issues.md#请求超时) |
| `ModuleNotFoundError` | 模块未安装 | [环境问题](./tool_issues.md#python-环境问题) |

### 按场景查找

- **无法抓包**: [代理配置](./tool_issues.md#抓包工具配置)
- **Cookie 不生效**: [Cookie 问题](./network_issues.md#cookie-失效)
- **加密无法破解**: [JavaScript 调试](./javascript_debugging.md)
- **爬虫被封**: [反爬虫对策](./anti_scraping_issues.md)
- **数据存储失败**: [数据库问题](./data_issues.md#数据库连接问题)

---

## 调试技巧

### 1. 系统化排查

```
问题出现
↓
查看错误日志
↓
确定问题类型
↓
查阅相关文档
↓
尝试解决方案
↓
验证修复
```

### 2. 日志收集

**Python 示例**:

```python
import logging

# 配置详细日志
logging.basicConfig(
level=logging.DEBUG,
format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
handlers=[
logging.FileHandler('debug.log'),
logging.StreamHandler()
]
)

logger = logging.getLogger(__name__)
logger.debug("详细调试信息")
```

**Scrapy 示例**:

```python
# settings.py
LOG_LEVEL = 'DEBUG'
LOG_FILE = 'scrapy_debug.log'
```

### 3. 网络请求调试

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 配置重试策略
session = requests.Session()
retry = Retry(
total=3,
backoff_factor=1,
status_forcelist=[500, 502, 503, 504]
)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

# 详细日志
import http.client
http.client.HTTPConnection.debuglevel = 1
```

### 4. JavaScript 调试

```javascript
// 1. 添加条件断点
// 右键断点 -> Edit breakpoint -> 输入条件
// 例如: userId === 123

// 2. 使用 debugger 语句
function suspiciousFunction() {
debugger; // 代码会在这里暂停
// ... 可疑代码
}

// 3. 监控变量变化
// Sources -> Watch -> 添加表达式

// 4. 查看调用栈
// Sources -> Call Stack
```

---

## 常见问题 FAQ

### Q: 为什么我的代理不生效？

**A**: 检查以下几点:

1. 代理配置格式是否正确
2. 代理服务是否正在运行
3. 系统代理设置是否正确
4. 是否需要设置环境变量

详见: [代理配置问题](./network_issues.md#代理配置问题)

### Q: 如何处理验证码？

**A**: 常见方法:

1. 使用验证码识别服务 (2Captcha, 打码平台)
2. 自建 OCR 识别
3. 使用浏览器自动化绕过
4. 分析验证码生成逻辑

详见: [验证码处理](./anti_scraping_issues.md#验证码拦截)

### Q: 为什么 Cookie 传过去还是失败？

**A**: 可能原因:

1. Cookie 已过期
2. 缺少必要的 Cookie 字段
3. Cookie 域名或路径不匹配
4. 需要其他请求头配合

详见: [Cookie 问题](./network_issues.md#cookie-失效)

### Q: JavaScript 混淆代码怎么调试？

**A**: 技巧:

1. 使用 Source Map (如果有)
2. 格式化代码 (Beautify)
3. 使用 AST 工具还原
4. 单步调试追踪

详见: [JavaScript 调试](./javascript_debugging.md)

---

## 预防措施

### 代码质量

```python
# 1. 异常处理
try:
response = requests.get(url, timeout=10)
response.raise_for_status()
except requests.exceptions.Timeout:
logger.error(f"Request timeout: {url}")
except requests.exceptions.HTTPError as e:
logger.error(f"HTTP error: {e.response.status_code}")
except Exception as e:
logger.exception(f"Unexpected error: {e}")

# 2. 参数验证
def process_data(data):
if not data:
raise ValueError("Data cannot be empty")
if not isinstance(data, dict):
raise TypeError("Data must be a dictionary")
# 处理数据...

# 3. 资源管理
with open('file.txt', 'r') as f:
data = f.read()
# 文件自动关闭
```

### 日志记录

```python
# 记录关键操作
logger.info(f"Processing URL: {url}")

# 记录错误详情
logger.error(f"Failed to parse: {url}", exc_info=True)

# 记录性能指标
import time
start = time.time()
# ... 操作
logger.info(f"Operation took {time.time() - start:.2f}s")
```

### 监控告警

- 设置请求成功率监控
- 配置错误日志告警
- 监控资源使用情况
- 定期检查数据质量

---

## 相关资源

- [Chrome DevTools 指南](../02-Tooling/browser_devtools.md)
- [调试技巧](../03-Basic-Recipes/debugging_techniques.md)
- [常用命令](../08-Cheat-Sheets/common_commands.md)
- [FAQ](../11-Resources/faq.md)

---

## 🆘 获取帮助

如果以上内容无法解决您的问题:

1. 查看 [GitHub Issues](https://github.com/your-repo/issues)
2. 提交新的 Issue (附带详细错误日志)
3. 加入社区讨论
4. 查看官方文档

---

记住：**调试是一门艺术，耐心是关键！** 
