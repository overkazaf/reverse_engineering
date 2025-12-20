# HTTP/2 与 HTTP/3

## 概述

HTTP/2 和 HTTP/3 是 HTTP 协议的最新版本，带来了性能提升和新的特性。在逆向工程中，理解这些协议的工作原理对于分析现代 Web 应用至关重要。

**为什么要学习 HTTP/2 和 HTTP/3？**

1. **现代网站的标准**: 大部分主流网站已迁移到 HTTP/2，HTTP/3 也在快速普及
2. **性能优化**: 多路复用、头部压缩等特性改变了请求模式
3. **逆向难度增加**: 二进制协议、加密传输增加了分析难度
4. **指纹识别**: TLS 指纹和协议特征可用于检测自动化工具

---

## 1. HTTP/1.x 的局限性

### 1.1 队头阻塞 (Head-of-Line Blocking)

**问题**: HTTP/1.1 在单个 TCP 连接上一次只能处理一个请求

```
请求1: |========== 响应 ==========|
请求2:                              |===== 响应 =====|
请求3:                                                |== 响应 ==|
```

**影响**: 前面的慢请求会阻塞后面的所有请求

**变通方案** (HTTP/1.1):

- **Pipeline**: 发送多个请求但仍按顺序响应（浏览器默认禁用）
- **Domain Sharding**: 使用多个域名增加并发连接数
- **连接复用**: 保持连接 (Keep-Alive)

**限制**: 浏览器通常限制每个域名最多 6 个并发连接

---

### 1.2 头部冗余

**问题**: 每个请求都重复发送相同的 HTTP 头部

```http
GET /api/data?id=1 HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0...
Accept: application/json
Cookie: session=abc123...
```

```http
GET /api/data?id=2 HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0...        <-- 重复
Accept: application/json          <-- 重复
Cookie: session=abc123...         <-- 重复
```

**影响**: 带宽浪费，尤其是移动网络

---

### 1.3 明文协议

**问题**: HTTP/1.x 本身不强制加密

**安全风险**:

- 中间人攻击
- 流量嗅探
- 内容篡改

---

## 2. HTTP/2 详解

### 2.1 核心特性

#### 2.1.1 二进制分帧 (Binary Framing)

**HTTP/1.x**: 基于文本，使用换行符分隔

```
GET /index.html HTTP/1.1\r\n
Host: example.com\r\n
\r\n
```

**HTTP/2**: 基于二进制帧

```
+-----------------------------------------------+
|                 Frame Header                   |
+-----------------------------------------------+
| Length (24) | Type (8) | Flags (8) | R |Stream|
+-----------------------------------------------+
|                 Frame Payload                  |
+-----------------------------------------------+
```

**帧类型**:

- `HEADERS`: HTTP 头部
- `DATA`: 消息体
- `PRIORITY`: 优先级
- `RST_STREAM`: 重置流
- `SETTINGS`: 连接设置
- `PUSH_PROMISE`: 服务器推送
- `PING`: 心跳检测
- `GOAWAY`: 连接关闭
- `WINDOW_UPDATE`: 流量控制
- `CONTINUATION`: 头部延续

**逆向影响**:

- ✅ **更高效**: 解析速度快
- ❌ **不可读**: 无法直接用 `cat` 查看
- 🛠️ **需要工具**: Wireshark、Chrome DevTools

---

#### 2.1.2 多路复用 (Multiplexing)

**原理**: 在单个 TCP 连接上并发多个 HTTP 流 (Streams)

```
TCP 连接
|
├── Stream 1: GET /css/style.css
├── Stream 3: GET /js/app.js
├── Stream 5: GET /img/logo.png
└── Stream 7: POST /api/submit
```

**优势**:

- **消除队头阻塞**: 请求和响应不再相互阻塞
- **减少连接数**: 一个域名只需一个连接
- **降低延迟**: 同时发送多个请求

**逆向影响**:

- Network 面板中请求顺序与实际发送顺序可能不同
- 无法通过请求顺序判断逻辑流程
- 需要关注 Stream ID 而非时间戳

**Chrome DevTools 中查看**:

1. 打开 Network 面板
2. 右键表头 → 勾选 "Protocol"
3. 查看协议列显示 `h2`（HTTP/2）

---

#### 2.1.3 头部压缩 (HPACK)

**原理**: 使用专用压缩算法（HPACK）和静态/动态表

**静态表** (常见头部预定义):

```
Index | Header Name     | Header Value
------+-----------------+-------------
1     | :authority      |
2     | :method         | GET
3     | :method         | POST
4     | :path           | /
5     | :path           | /index.html
...
```

**动态表** (会话中出现的头部):

```
62 | cookie: session=abc123
63 | user-agent: Mozilla/5.0...
```

**编码示例**:

```http
# 原始头部
:method: GET
:path: /api/user
cookie: session=abc123

# HPACK 编码 (简化表示)
82          # :method GET (静态表索引 2)
84          # :path /api/user (字面量)
BE          # cookie: session=abc123 (动态表索引 62)
```

**压缩率**: 通常可达 70-90%

**逆向难点**:

- 头部是动态压缩的，无法直接解析
- 需要维护会话状态才能正确解码
- 工具支持: Wireshark 自动解压

---

#### 2.1.4 服务器推送 (Server Push)

**原理**: 服务器主动推送客户端未请求的资源

**流程**:

```
客户端 -> 服务器: GET /index.html

服务器 -> 客户端: PUSH_PROMISE stream=2 (推送 /style.css)
服务器 -> 客户端: HEADERS stream=1 (响应 index.html)
服务器 -> 客户端: DATA stream=1 (<html>...)
服务器 -> 客户端: HEADERS stream=2 (响应 style.css)
服务器 -> 客户端: DATA stream=2 (body { ... })
```

**好处**:

- 减少往返延迟 (RTT)
- 提前加载关键资源

**逆向注意**:

- Network 面板中看到 `Push` 标记
- 可能看到未发起请求的资源加载

---

#### 2.1.5 流量控制 (Flow Control)

**原理**: 使用 `WINDOW_UPDATE` 帧控制发送速率

**场景**: 防止快速发送方压垮慢速接收方

```
发送方                接收方
  |                      |
  |---- DATA (16KB) ---->|
  |                      | (缓冲区满)
  |<-- WINDOW_UPDATE ---|  (通知可接收)
  |---- DATA (16KB) ---->|
```

---

### 2.2 HTTP/2 抓包与分析

#### 使用 Wireshark 分析 HTTP/2

**步骤**:

1. **启动抓包**: 捕获 HTTPS 流量
2. **解密 TLS**: 设置 SSL/TLS 解密（需要私钥或浏览器密钥日志）
3. **过滤 HTTP/2**: 使用过滤器 `http2`

**Chrome 导出密钥日志**:

```bash
# macOS/Linux
export SSLKEYLOGFILE=~/sslkeys.log
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome

# Windows
set SSLKEYLOGFILE=C:\sslkeys.log
"C:\Program Files\Google\Chrome\Application\chrome.exe"
```

**Wireshark 配置**:

1. `Edit` → `Preferences` → `Protocols` → `TLS`
2. `(Pre)-Master-Secret log filename`: 选择 `sslkeys.log`
3. 重启 Wireshark

**分析 HTTP/2 帧**:

```
Frame 123: HEADERS
  Stream ID: 3
  :method: GET
  :path: /api/data
  :authority: example.com

Frame 125: DATA
  Stream ID: 3
  Data Length: 1024
  Payload: {"result": ...}
```

---

#### 使用 Chrome DevTools

**查看 HTTP/2 协议**:

1. Network 面板 → 右键表头 → 勾选 "Protocol"
2. 看到 `h2` 表示 HTTP/2

**查看帧详情** (实验性):

1. `chrome://net-internals/#http2`
2. 查看活跃的 HTTP/2 会话和流

---

### 2.3 HTTP/2 逆向实战

#### 案例: 复现 HTTP/2 请求

**问题**: `curl` 默认使用 HTTP/1.1

**解决**: 使用 `curl` 的 HTTP/2 支持

```bash
# 强制使用 HTTP/2
curl --http2 https://example.com/api/data

# 查看详细信息
curl --http2 -v https://example.com/api/data

# 输出示例
* Using HTTP2, server supports multi-use
* Connection state changed (HTTP/2 confirmed)
* Using Stream ID: 1 (easy handle 0x7f9c8c004000)
> GET /api/data HTTP/2
> Host: example.com
> User-Agent: curl/7.79.1
```

**Python 请求 (使用 httpx)**:

```python
import httpx

# httpx 默认支持 HTTP/2
async with httpx.AsyncClient(http2=True) as client:
    response = await client.get('https://example.com/api/data')
    print(f"HTTP版本: {response.http_version}")  # HTTP/2
    print(response.json())
```

---

#### 案例: 识别服务器推送

**在 Chrome DevTools 中**:

- Initiator 列显示 "Push / Other"
- Protocol 列显示 `h2`

**在代码中检测**:

```javascript
// Service Worker 中拦截服务器推送
self.addEventListener("push", function (event) {
  console.log("Received server push:", event);
});

// 性能 API 检测
performance.getEntriesByType("navigation").forEach((entry) => {
  if (entry.nextHopProtocol === "h2") {
    console.log("使用 HTTP/2");
  }
});
```

---

## 3. HTTP/3 详解

### 3.1 核心特性

#### 3.1.1 基于 QUIC 协议

**QUIC (Quick UDP Internet Connections)**:

- 基于 **UDP** 而非 TCP
- 内置 TLS 1.3 加密
- 由 Google 开发，后标准化为 IETF QUIC

**协议栈对比**:

```
HTTP/1.1               HTTP/2                 HTTP/3
--------               ------                 ------
HTTP                   HTTP/2                 HTTP/3
TCP                    TCP                    QUIC
TLS                    TLS                    (内置 TLS 1.3)
IP                     IP                     UDP
                                             IP
```

---

#### 3.1.2 0-RTT 连接建立

**TCP + TLS 1.2** (HTTP/1.1, HTTP/2):

```
客户端 -> 服务器: SYN                       (1 RTT)
服务器 -> 客户端: SYN-ACK
客户端 -> 服务器: ACK

客户端 -> 服务器: ClientHello               (2 RTT)
服务器 -> 客户端: ServerHello, Certificate
客户端 -> 服务器: Finished

客户端 -> 服务器: HTTP Request              (3 RTT)
```

**QUIC** (HTTP/3):

```
首次连接:
客户端 -> 服务器: Initial Packet (含 ClientHello)  (1 RTT)
服务器 -> 客户端: Handshake Packet
客户端 -> 服务器: HTTP Request                     (1 RTT 完成)

后续连接 (0-RTT):
客户端 -> 服务器: 0-RTT Packet (含加密的 HTTP 请求)  (0 RTT!)
```

**性能提升**: 可减少 66% 的握手延迟

---

#### 3.1.3 消除队头阻塞

**HTTP/2 的问题**: TCP 层面仍有队头阻塞

```
TCP 连接
|
├── Stream 1: ████████ (丢包!) ████████
├── Stream 3: ████████ (等待) ████████
└── Stream 5: ████████ (等待) ████████
```

当 TCP 丢包时，所有 HTTP/2 流都会被阻塞，直到重传完成。

**HTTP/3 的解决**: QUIC 独立流

```
QUIC 连接
|
├── Stream 1: ████████ (丢包!) ████████
├── Stream 3: ████████ (继续传输) ████████
└── Stream 5: ████████ (继续传输) ████████
```

每个 QUIC 流独立，丢包只影响当前流。

---

#### 3.1.4 连接迁移 (Connection Migration)

**场景**: 移动设备从 WiFi 切换到 4G

**TCP/HTTP/2**: 连接断开，需要重新建立

```
WiFi (IP: 192.168.1.10) ----X----> 切换到 4G (IP: 10.0.0.5)
需要重新三次握手 + TLS 握手 + HTTP/2 建立
```

**QUIC/HTTP/3**: 连接保持

```
WiFi (连接 ID: abc123) -----> 切换到 4G (连接 ID: abc123)
通过连接 ID 识别，无需重新握手
```

**优势**:

- 移动网络切换无感知
- 视频播放、下载不中断

---

### 3.2 HTTP/3 抓包与分析

#### Wireshark 抓包 HTTP/3

**步骤**:

1. **捕获 UDP 流量**: HTTP/3 使用 UDP 端口（通常 443）
2. **解密 QUIC**: 需要 QUIC 密钥日志

**Chrome 导出 QUIC 密钥**:

```bash
export SSLKEYLOGFILE=~/sslkeys.log
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --enable-quic
```

**Wireshark 过滤器**:

```
quic
http3
```

---

#### Chrome 查看 HTTP/3

**检测方法**:

1. **Network 面板**: Protocol 列显示 `h3` 或 `h3-29`
2. **chrome://net-internals/#quic**: 查看 QUIC 会话详情
3. **开发者工具**: 在 Network 面板的 Protocol 列查看

**JavaScript 检测**:

```javascript
// 检测 HTTP 版本
fetch("https://example.com/api/data").then((response) => {
  console.log(response.headers.get("alt-svc"));
  // 输出: h3=":443"; ma=2592000
});

// Performance API
performance.getEntriesByType("resource").forEach((entry) => {
  console.log(entry.nextHopProtocol); // h3, h2, http/1.1
});
```

---

### 3.3 HTTP/3 逆向实战

#### 案例: 使用 curl 发送 HTTP/3 请求

**安装支持 HTTP/3 的 curl** (需要编译):

```bash
# macOS (使用 Homebrew)
brew install curl --with-nghttp3

# 检查版本
curl --version
# Features: ... HTTP3 ...
```

**发送请求**:

```bash
# 强制使用 HTTP/3
curl --http3 https://cloudflare-quic.com/

# 查看详细信息
curl --http3 -v https://cloudflare-quic.com/
# * Using HTTP/3 Stream ID: 0 (easy handle 0x...)
# > GET / HTTP/3
# > Host: cloudflare-quic.com
```

---

#### 案例: Python 使用 HTTP/3

**使用 httpx** (实验性支持):

```python
import httpx

# 需要安装 HTTP/3 支持
# pip install httpx[http3]

async with httpx.AsyncClient(http3=True) as client:
    response = await client.get('https://cloudflare-quic.com/')
    print(f"HTTP版本: {response.http_version}")  # HTTP/3
    print(response.text)
```

---

## 4. 版本对比总结

| 特性           | HTTP/1.1        | HTTP/2   | HTTP/3             |
| -------------- | --------------- | -------- | ------------------ |
| **协议类型**   | 文本            | 二进制   | 二进制             |
| **传输层**     | TCP             | TCP      | UDP (QUIC)         |
| **加密**       | 可选 (HTTPS)    | 强制 TLS | 内置 TLS 1.3       |
| **多路复用**   | ❌              | ✅       | ✅                 |
| **队头阻塞**   | 严重            | TCP 层   | 无                 |
| **头部压缩**   | ❌              | HPACK    | QPACK              |
| **服务器推送** | ❌              | ✅       | ✅                 |
| **连接建立**   | 3 RTT (TCP+TLS) | 3 RTT    | 1 RTT (0-RTT 可用) |
| **连接迁移**   | ❌              | ❌       | ✅                 |
| **浏览器支持** | 100%            | 97%+     | 75%+ (增长中)      |

---

## 5. 逆向工程注意事项

### 5.1 协议协商 (ALPN)

服务器通过 **ALPN (Application-Layer Protocol Negotiation)** 告知客户端支持的协议。

**TLS 握手中的 ALPN**:

```
ClientHello:
  ALPN Extension: [h2, http/1.1]

ServerHello:
  ALPN Extension: h2
```

**HTTP/3 协商** (通过 Alt-Svc 头):

```http
HTTP/2 200 OK
Alt-Svc: h3=":443"; ma=2592000

# ma = max-age (缓存时间)
```

客户端收到后，后续请求会尝试使用 HTTP/3。

---

### 5.2 抓包工具选择

| 工具                | HTTP/1.1 | HTTP/2 | HTTP/3 | 备注          |
| ------------------- | -------- | ------ | ------ | ------------- |
| **Wireshark**       | ✅       | ✅     | ✅     | 需要配置解密  |
| **Chrome DevTools** | ✅       | ✅     | ✅     | 最方便        |
| **Burp Suite**      | ✅       | ✅     | ❌     | 不支持 HTTP/3 |
| **Charles Proxy**   | ✅       | ✅     | ❌     | 不支持 HTTP/3 |
| **mitmproxy**       | ✅       | ✅     | ⚠️     | 实验性支持    |

**注意**: 大部分 MITM 代理工具不支持 HTTP/3，因为 QUIC 难以中间人攻击。

---

### 5.3 自动化工具兼容性

#### Puppeteer / Playwright

```javascript
// 默认支持 HTTP/2 和 HTTP/3
const browser = await puppeteer.launch();
const page = await browser.newPage();

await page.goto("https://cloudflare-quic.com/");

// 检测协议版本
const protocol = await page.evaluate(() => {
  return performance.getEntriesByType("navigation")[0].nextHopProtocol;
});

console.log(`使用协议: ${protocol}`); // h2 或 h3
```

#### Requests (Python)

```python
import requests

# requests 默认只支持 HTTP/1.1
# 需要使用 httpx 或 urllib3 的新版本

import httpx

async with httpx.AsyncClient(http2=True) as client:
    response = await client.get('https://example.com/')
    print(response.http_version)  # HTTP/2
```

---

### 5.4 TLS 指纹识别

HTTP/2 和 HTTP/3 的使用会影响 TLS 指纹。

**JA3 指纹差异**:

```
HTTP/1.1 Client:
  ALPN: [http/1.1]

HTTP/2 Client:
  ALPN: [h2, http/1.1]

HTTP/3 Client:
  ALPN: [h3, h2, http/1.1]
```

**对抗方法**: 使用 `curl-impersonate` 或 `tls-client` 库模拟真实浏览器指纹。

---

## 6. 性能优化建议

### 6.1 针对 HTTP/2

1. **减少域名分片**: HTTP/2 不需要多域名，反而有害
2. **避免内联资源**: HTTP/2 的多路复用使独立文件更高效
3. **使用服务器推送**: 预推送关键 CSS/JS
4. **合理设置优先级**: 标记关键资源的优先级

---

### 6.2 针对 HTTP/3

1. **启用 0-RTT**: 减少重复访问的延迟
2. **优化 UDP**: 确保防火墙不阻止 UDP 443
3. **降级策略**: 在 HTTP/3 失败时降级到 HTTP/2

---

## 7. 常见问题

### Q1: 如何强制使用特定的 HTTP 版本？

**Chrome**:

```bash
# 禁用 HTTP/2
chrome --disable-http2

# 禁用 QUIC (HTTP/3)
chrome --disable-quic
```

**curl**:

```bash
curl --http1.1 https://example.com/  # 强制 HTTP/1.1
curl --http2 https://example.com/    # 强制 HTTP/2
curl --http3 https://example.com/    # 强制 HTTP/3
```

---

### Q2: Burp Suite 无法抓取 HTTP/3 流量怎么办？

**解决方案**:

1. **禁用 HTTP/3**: 在浏览器中禁用 QUIC
   - Chrome: `chrome://flags/` 搜索 "QUIC"，设为 Disabled
2. **使用 Wireshark**: Burp 不支持 HTTP/3，使用 Wireshark 抓包
3. **服务器降级**: 删除 `Alt-Svc` 头，阻止客户端升级到 HTTP/3

---

### Q3: HTTP/2 是否会泄露更多指纹信息？

**是的**，HTTP/2 引入了新的指纹点：

- **SETTINGS 帧参数**: 不同客户端的初始设置不同
- **优先级树**: 请求优先级的设置方式
- **流 ID 分配**: 奇偶性和顺序

**检测示例**:

```
Chrome:
  SETTINGS_HEADER_TABLE_SIZE: 65536
  SETTINGS_INITIAL_WINDOW_SIZE: 6291456

Firefox:
  SETTINGS_HEADER_TABLE_SIZE: 4096
  SETTINGS_INITIAL_WINDOW_SIZE: 65535
```

**对抗**: 使用真实浏览器而非脚本工具。

---

## 8. 工具与资源

### 推荐工具

| 工具          | 用途                   | 链接                                 |
| ------------- | ---------------------- | ------------------------------------ |
| **Wireshark** | 抓包分析               | https://www.wireshark.org/           |
| **httpx**     | Python HTTP/2/3 客户端 | https://www.python-httpx.org/        |
| **curl**      | 命令行 HTTP 客户端     | https://curl.se/                     |
| **h2spec**    | HTTP/2 合规性测试      | https://github.com/summerwind/h2spec |
| **quic-go**   | Go 语言 QUIC 实现      | https://github.com/quic-go/quic-go   |

---

### 学习资源

- [HTTP/2 RFC 7540](https://datatracker.ietf.org/doc/html/rfc7540)
- [HTTP/3 RFC 9114](https://datatracker.ietf.org/doc/html/rfc9114)
- [QUIC RFC 9000](https://datatracker.ietf.org/doc/html/rfc9000)
- [HTTP/2 Explained (中文)](https://http2-explained.haxx.se/zh)

---

## 9. 总结

HTTP/2 和 HTTP/3 是现代 Web 的基石，理解它们对于逆向工程至关重要：

**HTTP/2**:

- ✅ 已广泛部署，必须掌握
- ✅ 工具支持完善
- ⚠️ TCP 队头阻塞仍存在

**HTTP/3**:

- 🚀 未来趋势，逐步普及
- 🔒 更安全（内置加密）
- ⚠️ 工具支持有限

**逆向建议**:

1. 优先使用 Chrome DevTools 分析
2. HTTP/2 可用 Burp/Charles，HTTP/3 用 Wireshark
3. 代码中使用 httpx 支持新协议
4. 注意协议降级和兼容性

---

## 相关章节

- [HTTP/HTTPS 协议](../01-Foundations/http_https_protocol.md)
- [TLS/SSL 握手过程](../01-Foundations/tls_ssl_handshake.md)
- [TLS 指纹识别](./tls_fingerprinting.md)
- [Wireshark 指南](../02-Tooling/wireshark_guide.md)
- [浏览器开发者工具](../02-Tooling/browser_devtools.md)
