---
title: "使用 TLS 指纹识别检测和绕过应用指纹"
date: 2024-11-04
tags: ["RSA", "浏览器指纹", "签名验证", "Frida", "SSL Pinning", "Canvas指纹"]
weight: 10
---

# 使用 TLS 指纹识别检测和绕过应用指纹

> **📚 前置知识**
>
> 本配方涉及以下核心技术，建议先阅读相关章节：
>
> - **[JA3 指纹技术](./ja3_fingerprinting.md)** - 理解 TLS 指纹的生成原理
> - **[JA4+ 指纹技术](./ja4_fingerprinting.md)** - 了解下一代指纹方案

## 问题场景

_你遇到了什么问题？_

- 你的自动化脚本被服务器识别并封禁了
- 你用 Python/curl 请求 API，但服务器返回 403/风控拦截
- 你想伪装成真实浏览器/官方 App 的 TLS 指纹
- 你想分析 App 使用的 TLS 库和配置
- 你想检测自己的请求是否暴露了异常的 TLS 特征

_本配方教你_：理解 TLS 指纹识别原理、如何检测自己的 TLS 指纹、以及如何伪造合法的 TLS 指纹。

_核心理念_：

> 💡 **TLS 指纹是应用的"DNA"**
>
> - TLS 握手阶段暴露了客户端使用的库和配置
> - 不同的 HTTP 客户端有不同的 TLS 指纹
> - 服务器可以通过 JA3/JA4 指纹识别你的真实身份
> - 即使使用 HTTPS，TLS 握手特征也是明文的

_预计用时_: 20-40 分钟

---

## 工具清单

### 必需工具

- - **Wireshark** - 抓取 TLS 握手包
- - **在线 JA3 检测工具** - https://ja3er.com 或 https://tls.peet.ws
- - **Python 3.7+** - 用于脚本测试

### 可选工具

- - **curl-impersonate** - 伪装浏览器 TLS 指纹的 curl
- - **tls-client** (Python) - 支持自定义 TLS 指纹的 HTTP 库
- - **Burp Suite** - 抓包分析
- - **ja3transport** (Go) - Go 语言的 TLS 伪装库

---

## 前置条件

### ✅ 确认清单

1. **Wireshark 已安装并可用**
2. **Python 3.7+ 环境配置完成**

```bash
# 验证 Wireshark 安装
wireshark --version

# 验证 Python 环境
python3 --version

# 安装必要的 Python 库
pip3 install requests pycurl tls-client

```

---

## 解决方案

### 第 1 步：理解 TLS 指纹识别原理（5 分钟）

#### 1.1 什么是 JA3 指纹？

_JA3_ 是一种通过分析 TLS `Client Hello` 包生成指纹的技术。

_提取的字段_：

1. TLS 版本（如 TLS 1.3 = 771）
2. 加密套件列表（Cipher Suites）
3. 扩展列表（Extensions）
4. 椭圆曲线列表（Elliptic Curves）
5. 椭圆曲线点格式（EC Point Formats）

_生成过程_：

```
拼接成String: "771,4865-4866-4867,0-23-65281,29-23-24,0"
↓
Calculate MD5 哈希
↓
JA3 指纹: e7d705a3286e19ea42f587b344ee6865

```

| 特性       | MD5 指纹                           | JA3 指纹                               |
| ---------- | ---------------------------------- | -------------------------------------- |
| **格式**   | MD5 哈希                           | 结构化字符串                           |
| **可读性** | 无                                 | 高（包含版本、计数等）                 |
| **示例**   | `e7d705a3286e19ea42f587b344ee6865` | `t13d1516h2_174735a34e8a_b2149a751699` |
| **优势**   | 简单，广泛支持                     | 可模糊匹配，抗干扰                     |

✅ **关键点**：不同的 HTTP 库有不同的 JA3 指纹

| 客户端          | JA3 指纹                           |
| --------------- | ---------------------------------- |
| Chrome 120      | `579ccef312d18482fc42e2b822ca2430` |
| Firefox 121     | `3b5074b1b5d032e5620f69f9f700ff0e` |
| Python requests | `084c44f52a434da89e0b1bc98f8dd159` |
| curl 默认       | `51c64c77e60f3980eea90869b68c58a8` |

_问题_：如果你用 Python requests 访问服务器，即使设置了 User-Agent，服务器也能通过 JA3 识别出你不是真实浏览器

---

### 第 2 步：检测你的 TLS 指纹（10 分钟）

#### 2.1 在线检测

_方法 1：访问 JA3 检测网站_

```bash
# 用 curl 测试
curl https://ja3er.com/json

# 用 Python requests 测试
python3 << 'EOF'
import requests
r = requests.get('https://ja3er.com/json')
print(r.text)
EOF
```

```json
{
  "ja3": "084c44f52a434da89e0b1bc98f8dd159",
  "ja3_text": "771,4865-4866-4867-49195-49199-49196-49200-52393-52392-49171-49172-156-157-47-53,0-23-65281-10-11-35-16-5-13-18-51-45-43-27-21,29-23-24,0",
  "User-Agent": "python-requests/2.31.0"
}
```

```bash
curl -s https://tls.peet.ws/api/all | jq .
```

1. 打开 Wireshark
2. 过滤器输入：`tls.handshake.type == 1`（只显示 Client Hello）
3. 在终端执行请求：

```bash
curl https://example.com

```

接着展开 **Transport Layer Security → Handshake Protocol: Client Hello**

_查看关键字段_：

```text
- TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384 (0xc030)
- ...
Extension: supported_groups (len=10)
- secp256r1 (0x0017)
- x25519 (0x001d)
- ...
```

✅ **成功标志**：你已经看到了自己客户端的 TLS 握手特征

---

### 第 3 步：获取目标指纹（5 分钟）

**目标**：获取真实浏览器或官方 App 的 JA3 指纹用于伪装

#### 3.1 浏览器指纹

**方法 1：直接查询**

Chrome 浏览器访问 https://ja3er.com/json

记录显示的 JA3 哈希值。

**方法 2：从 GitHub 数据库查询**

访问 https://github.com/salesforce/ja3/blob/master/lists/osx-nix-ja3.csv

搜索 "Chrome"、"Safari"、"Firefox" 找到对应版本的 JA3。

#### 3.2 android App 指纹

**使用 Wireshark 抓取真实 App 的流量**：

1. 配置手机走电脑代理
2. Wireshark 监听对应网卡
3. 打开目标 App，触发网络请求
4. 过滤 `tls.handshake.type == 1` 找到 Client Hello 包
5. 记录或导出该包

**提取 JA3**：

```bash
# Use ja3 Tool（NeedInstall）
pip3 install pyshark
python3 << 'EOF'
import pyshark
cap = pyshark.FileCapture('capture.pcap', display_filter='tls.handshake.type == 1')
for pkt in cap:
print(pkt.tls.handshake_ciphersuite)
EOF

```

### 第 4 步：伪造 TLS 指纹（15 分钟）

#### 4.1 使用 curl-impersonate（推荐）

**curl-impersonate** 是一个修改版的 curl，能完美模拟浏览器的 TLS 指纹。

**安装**（macOS）：

```bash
# Use Homebrew
brew install curl-impersonate

# or downloadpre-compiled version
# https://github.com/lwthiker/curl-impersonate/releases

```

```bash
# 伪装成 Chrome 120
curl_chrome120 https://ja3er.com/json

# 伪装成 Firefox 121
curl_ff121 https://ja3er.com/json

# 伪装成 Safari 17
curl_safari17 https://ja3er.com/json

```

#### 4.2 使用 Python tls-client 库

**安装**：

```bash
pip3 install tls-client
```

**基本使用**：

```python
import tls_client

# 创建会话，伪装成 Chrome 120
session = tls_client.Session(
    client_identifier="chrome_120",
    random_tls_extension_order=True
)

# 发送请求
response = session.get("https://ja3er.com/json")
print(response.json())
```

**支持的客户端标识符**：

```python
# 桌面浏览器
"chrome_103", "chrome_110", "chrome_120"
"firefox_102", "firefox_104", "firefox_121"
"safari_15_3", "safari_16_0", "safari_17_0"

# 移动端
"okhttp4_android_7", "okhttp4_android_8", "okhttp4_android_13"
```

**自定义 JA3 字符串**：

```python
import tls_client

session = tls_client.Session(
    client_identifier="custom",
    ja3_string="771,4865-4866-4867-49195-49199-49196-49200-52393-52392-49171-49172-156-157-47-53,0-23-65281-10-11-35-16-5-13-18-51-45-43-27-21,29-23-24,0"
)
```

#### 4.3 使用 Go ja3transport 库

```go
package main

import (
    "fmt"
    "io"
    "net/http"
    "github.com/CUCyber/ja3transport"
)

func main() {
    // 创建带 JA3 指纹的 Transport
    tr, _ := ja3transport.NewTransport("771,4865-4866-4867-49195-49199-49196-49200-52393-52392-49171-49172-156-157-47-53,0-23-65281-10-11-35-16-5-13-18-51-45-43-27-21,29-23-24,0")

    client := &http.Client{Transport: tr}

    resp, _ := client.Get("https://ja3er.com/json")
    defer resp.Body.Close()

    body, _ := io.ReadAll(resp.Body)
    fmt.Println(string(body))
}
```

### 第 5 步：验证伪装效果（5 分钟）

**创建对比脚本** `compare_ja3.sh`：

```bash
#!/bin/bash

echo "=== 原生 curl ==="
curl -s https://ja3er.com/json | jq -r '.ja3'

echo ""
echo "=== curl-impersonate (Chrome) ==="
curl_chrome120 -s https://ja3er.com/json | jq -r '.ja3'

echo ""
echo "=== Python requests ==="
python3 -c "import requests; print(requests.get('https://ja3er.com/json').json()['ja3'])"

echo ""
echo "=== Python tls-client ==="
python3 << 'EOF'
import tls_client
session = tls_client.Session(client_identifier="chrome_120")
print(session.get("https://ja3er.com/json").json()['ja3'])
EOF
```

**运行对比**：

```bash
chmod +x compare_ja3.sh
./compare_ja3.sh
```

**预期输出**：

```
=== 原生 curl ===
51c64c77e60f3980eea90869b68c58a8

=== curl-impersonate (Chrome) ===
579ccef312d18482fc42e2b822ca2430

=== Python requests ===
084c44f52a434da89e0b1bc98f8dd159

=== Python tls-client ===
579ccef312d18482fc42e2b822ca2430
```

**实战示例 - 访问受保护的 API**：

```python
import tls_client

# 使用伪装的 TLS 指纹
session = tls_client.Session(client_identifier="chrome_120")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

response = session.get('https://api.example.com/protected', headers=headers)
print(response.status_code)
print(response.text)
```

**伪装效果对比**：

| 工具       | User-Agent | TLS 指纹 | 服务器响应       |
| ---------- | ---------- | -------- | ---------------- |
| requests   | Chrome     | Python   | ❌ 403 Forbidden |
| tls-client | Chrome     | Chrome   | ✅ 200 OK        |

---

## 工作原理

### TLS 握手过程

```
客户端                              服务器
   |                                  |
   |--- Client Hello ---------------→|
   |    (JA3 指纹在此生成)             |
   |                                  |
   |←-- Server Hello ----------------|
   |    (Server JA3S 指纹)            |
   |                                  |
   |--- Key Exchange --------------→|
   |←-- Finished -------------------|
   |                                  |
   |←→ 加密数据传输 ←→|
```

### JA3 指纹生成细节

**原始字符串示例**：

```
771,4865-4866-4867-49195-49199,0-23-65281-10-11,29-23-24,0
 │        │                      │          │      │
 │        │                      │          │      └─ EC Point Formats
 │        │                      │          └─ Supported Groups (椭圆曲线)
 │        │                      └─ Extensions
 │        └─ Cipher Suites
 └─ TLS 版本 (771 = TLS 1.2)
```

**JA4 指纹格式**：

```
t13d1516h2_174735a34e8a_b2149a751699
│  │  │  │  │            │
│  │  │  │  │            └─ Signature Algorithms 哈希
│  │  │  │  └─ Extensions 哈希（截断）
│  │  │  └─ h2 = HTTP/2
│  │  └─ 16 个 Extensions
│  └─ 15 个 Cipher Suites
└─ TLS 1.3
```

- 可读性强（无需查表）

---

## 常见问题

### ❌ 问题 1: curl-impersonate 安装失败

**症状**：Homebrew 找不到 curl-impersonate

**解决**：

```bash
# macOS/Linux: 手动下载预编译版本
wget https://github.com/lwthiker/curl-impersonate/releases/download/v0.6.1/curl-impersonate-v0.6.1.x86_64-linux-gnu.tar.gz

tar -xzf curl-impersonate-*.tar.gz
cd curl-impersonate-*
sudo cp curl_* /usr/local/bin/
```

### ❌ 问题 2: tls-client 不支持某个浏览器版本

**症状**：`ValueError: Unknown client identifier: chrome_999`

**解决**：查看支持的客户端列表

```python
import tls_client
print(tls_client.settings.ClientIdentifiers)
```

### ❌ 问题 3: 伪装后仍被检测

**可能原因**：

1. **HTTP/2 指纹不匹配**

   - JA3 指纹是浏览器，但 HTTP 头顺序/值不对
   - **解决**：使用完整的浏览器模拟（包括 HTTP/2 特征）

2. **行为特征异常**

   - 请求速度太快
   - 缺少 Referer/Cookie
   - **解决**：添加延迟、模拟真实用户行为

3. **IP 信誉问题**

   - IP 被标记为数据中心/代理
   - **解决**：使用住宅代理或轮换 IP

4. **设备指纹**
   - 服务器检测 Canvas 指纹、WebGL 指纹等
   - **解决**：使用真实浏览器自动化（Selenium + undetected-chromedriver）

### ❌ 问题 4: 如何在 Frida 中修改 TLS 指纹？

**场景**：你想修改 Android App 的 TLS 指纹

**方法：Hook Java 层 SSLSocket**

```javascript
Java.perform(function () {
  var SSLSocket = Java.use("javax.net.ssl.SSLSocket");

  SSLSocket.setEnabledCipherSuites.implementation = function (suites) {
    console.log("[*] Original Cipher Suites:", suites);

    // 修改为目标指纹加密套件
    var customSuites = [
      "TLS_AES_128_GCM_SHA256",
      "TLS_AES_256_GCM_SHA384",
      "TLS_CHACHA20_POLY1305_SHA256",
    ];

    console.log("[*] ModifyAfter:", customSuites);
    return this.setEnabledCipherSuites(customSuites);
  };
});
```

## 延伸阅读

### 相关配方

- **[网络抓包](./network_sniffing.md)** - 抓取 TLS 握手包
- **[密码学分析](./crypto_analysis.md)** - 分析加密实现
- **[JA3 指纹详解](./ja3_fingerprinting.md)** - JA3 技术深入
- **[JA4 指纹详解](./ja4_fingerprinting.md)** - JA4+ 套件详解

### 工具深入

- **curl-impersonate 文档** - https://github.com/lwthiker/curl-impersonate
- **tls-client (Python)** - https://github.com/FlorianREGAZ/Python-Tls-Client
- **ja3transport (Go)** - https://github.com/CUCyber/ja3transport

### 在线资源

- **JA3 检测** - https://ja3er.com
- **TLS 指纹检测** - https://tls.peet.ws
- **JA3 数据库** - https://github.com/salesforce/ja3

### 理论基础

- **[TLS 协议详解](../../04-Reference/Advanced/)** - TODO
- **[HTTP/2 指纹](../../04-Reference/Advanced/)** - TODO

---

## 快速参考

### 常用工具对比

| 工具                   | 语言   | 难度 | 特点                 |
| ---------------------- | ------ | ---- | -------------------- |
| **curl-impersonate**   | Bash   |      | 最简单，完美模拟     |
| **tls-client**         | Python |      | 易用，支持多种浏览器 |
| **ja3transport**       | Go     |      | 高性能，需要 Go 环境 |
| **requests + urllib3** | Python |      | 复杂，需深度定制     |

### 快速检测脚本

**detect_ja3.sh**：

```bash
#!/bin/bash

echo "正在检测 TLS 指纹..."
echo ""

URL="https://ja3er.com/json"

# 检测当前客户端
JA3=$(curl -s "$URL" | jq -r '.ja3')
echo "你的 JA3: $JA3"

# 查询已知指纹
echo ""
echo "常见客户端 JA3:"
echo "  Chrome 120:  579ccef312d18482fc42e2b822ca2430"
echo "  Firefox 121: 3b5074b1b5d032e5620f69f9f700ff0e"
echo "  Safari 17:   4e2d5f6c3e8f7a9b0c1d2e3f4a5b6c7d"
echo "  Python req:  084c44f52a434da89e0b1bc98f8dd159"
echo "  curl:        51c64c77e60f3980eea90869b68c58a8"

# 对比
if [ "$JA3" == "579ccef312d18482fc42e2b822ca2430" ]; then
    echo ""
    echo "✅ 匹配: Chrome 120"
elif [ "$JA3" == "084c44f52a434da89e0b1bc98f8dd159" ]; then
    echo ""
    echo "⚠️ 匹配: Python requests (容易被识别)"
else
    echo ""
    echo "❓ 未知指纹"
fi
```

### TLS 指纹伪装模板

**browser_session.py**：

```python
"""
TLS 指纹伪装模板
"""
import tls_client


class BrowserSession:
    """模拟浏览器会话"""

    PROFILES = {
        'chrome': 'chrome_120',
        'firefox': 'firefox_121',
        'safari': 'safari_17_0',
        'android': 'okhttp4_android_13'
    }

    def __init__(self, browser='chrome'):
        """初始化会话

        Args:
            browser: 浏览器类型 ('chrome', 'firefox', 'safari', 'android')
        """
        identifier = self.PROFILES.get(browser, 'chrome_120')
        self.session = tls_client.Session(
            client_identifier=identifier,
            random_tls_extension_order=True
        )
        self._set_headers(browser)

    def _set_headers(self, browser):
        """设置对应 HTTP 头"""
        user_agents = {
            'chrome': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'firefox': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'safari': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
            'android': 'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.144 Mobile Safari/537.36'
        }

        self.session.headers.update({
            'User-Agent': user_agents.get(browser, user_agents['chrome']),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

    def get(self, url, **kwargs):
        """发送 GET 请求"""
        return self.session.get(url, **kwargs)

    def post(self, url, **kwargs):
        """发送 POST 请求"""
        return self.session.post(url, **kwargs)

    def verify_fingerprint(self):
        """验证 TLS 指纹"""
        r = self.get('https://ja3er.com/json')
        return r.json()


# 使用示例
if __name__ == '__main__':
    # 创建 Chrome 会话
    browser = BrowserSession('chrome')

    # 验证指纹
    print("验证 TLS 指纹...")
    result = browser.verify_fingerprint()
    print(f"JA3: {result['ja3']}")
    print(f"User-Agent: {result['User-Agent']}")

    # 发送请求
    response = browser.get('https://api.example.com/data')
    print(f"\n状态码: {response.status_code}")
```
