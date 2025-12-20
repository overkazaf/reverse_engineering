# WebSocket 逆向分析

## 概述

WebSocket (WS) 是一种全双工协议，常用于即时通讯、股票行情、在线游戏、实时推送等场景。与 HTTP 不同，WS 是一次握手后建立长连接，后续数据都是帧 (Frame) 的形式双向传输。

WebSocket 逆向的本质是**协议逆向** —— 搞清楚它"说什么话"（Payload 格式）以及"怎么说话"（状态机、心跳、认证）。

---

## 1. WebSocket 协议基础

### 1.1 连接建立（Upgrade Handshake）

WebSocket 连接由 HTTP 请求升级而来：

**客户端发起升级请求**:

```http
GET /chat HTTP/1.1
Host: example.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13
```

**服务端响应**:

```http
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
```

**重点参数**:

- `Sec-WebSocket-Key`: 客户端随机生成的 Base64 编码
- `Sec-WebSocket-Accept`: 服务端根据 Key 计算的哈希值
- `Sec-WebSocket-Protocol`: 子协议（如 `chat`, `mqtt`）

### 1.2 帧结构 (Frame Structure)

WebSocket 数据以帧的形式传输：

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-------+-+-------------+-------------------------------+
|F|R|R|R| opcode|M| Payload len |    Extended payload length    |
|I|S|S|S|  (4)  |A|     (7)     |             (16/64)           |
|N|V|V|V|       |S|             |   (if payload len==126/127)   |
| |1|2|3|       |K|             |                               |
+-+-+-+-+-------+-+-------------+ - - - - - - - - - - - - - - - +
|     Extended payload length continued, if payload len == 127  |
+ - - - - - - - - - - - - - - - +-------------------------------+
|                               |Masking-key, if MASK set to 1  |
+-------------------------------+-------------------------------+
| Masking-key (continued)       |          Payload Data         |
+-------------------------------- - - - - - - - - - - - - - - - +
:                     Payload Data continued ...                :
+ - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - +
|                     Payload Data continued ...                |
+---------------------------------------------------------------+
```

**Opcode (操作码)**:

| Opcode | 类型         | 说明              |
| ------ | ------------ | ----------------- |
| 0x0    | Continuation | 分片消息的后续帧  |
| 0x1    | Text         | 文本消息（UTF-8） |
| 0x2    | Binary       | 二进制消息        |
| 0x8    | Close        | 关闭连接          |
| 0x9    | Ping         | 心跳请求          |
| 0xA    | Pong         | 心跳响应          |

---

## 2. 抓包与分析

### 2.1 Chrome DevTools

**步骤**:

1. 打开 Network 面板
2. 点击 "WS" 过滤器 → 只显示 WebSocket 连接
3. 点击连接名称 → 查看详细信息

**Messages 标签页**:

- 🟢 绿色箭头 = 客户端发送 (Send)
- 🔴 红色箭头 = 服务端接收 (Receive)
- 时间戳、大小、Opcode

**Frame 分析**:

- **Text Frame**: 直接显示 UTF-8 文本（通常是 JSON）
- **Binary Frame**: 显示为十六进制或 Base64
  - 可能是 Protobuf、MsgPack、自定义格式

**技巧**: 保存消息到文件

```javascript
// 在 Console 中执行
const messages = [...document.querySelectorAll(".message-list-item")];
const data = messages.map((m) => m.textContent);
copy(JSON.stringify(data, null, 2)); // 复制到剪贴板
```

### 2.2 Wireshark 抓包

**优势**: 适用于非浏览器应用（桌面客户端、移动 App）

**过滤器**:

```
websocket
websocket.opcode == 1  // 只显示文本帧
websocket.opcode == 2  // 只显示二进制帧
```

**SSL/TLS 解密** (对于 wss://):

1. 设置环境变量:
   ```bash
   export SSLKEYLOGFILE=~/sslkeys.log
   ```
2. 启动应用（浏览器或客户端）
3. Wireshark 配置:
   - Edit → Preferences → Protocols → TLS
   - (Pre)-Master-Secret log filename: `~/sslkeys.log`

**查看 Payload**:

- 右键帧 → Follow → WebSocket Stream
- 自动解密 Masking Key

### 2.3 mitmproxy

**优势**: 可编程拦截和修改 WebSocket 消息

**启动**:

```bash
mitmweb --mode upstream:https://api.example.com --listen-port 8080
```

**Python 脚本拦截**:

```python
# ws_intercept.py
from mitmproxy import ctx

def websocket_message(flow):
    # 拦截 WebSocket 消息
    message = flow.messages[-1]

    if message.from_client:
        ctx.log.info(f"[Client → Server] {message.content}")
        # 修改消息
        if b'"type":"ping"' in message.content:
            message.content = b'{"type":"pong"}'

    else:
        ctx.log.info(f"[Server → Client] {message.content}")
```

**运行**:

```bash
mitmproxy -s ws_intercept.py
```

---

## 3. 协议还原

### 3.1 文本协议 (Text Frame)

#### JSON 格式

最常见的 WebSocket Payload 格式：

**示例**:

```json
{
  "type": "chat",
  "user_id": 123,
  "message": "Hello World",
  "timestamp": 1638360000
}
```

**逆向步骤**:

1. 观察多个消息，提取字段规律
2. 总结消息类型（`type` 字段）
3. 编写 Python 客户端时直接 `json.loads()` 和 `json.dumps()`

#### 自定义分隔符

**示例**: 使用 `|` 分隔

```
type|chat|user_id|123|message|Hello World
```

**解析方法**:

```python
def parse_message(data):
    parts = data.split('|')
    return {
        parts[i]: parts[i+1]
        for i in range(0, len(parts), 2)
    }

# 测试
msg = "type|chat|user_id|123"
print(parse_message(msg))  # {'type': 'chat', 'user_id': '123'}
```

### 3.2 二进制协议 (Binary Frame)

#### Protobuf (Protocol Buffers)

**特征**:

- 紧凑的二进制格式
- 字段没有 Key 名称（只有 Tag 编号）
- 常见于 Google 系产品、gRPC

**识别方法**:

1. 搜索 JS 代码中的 `proto.decode`、`protobuf.Reader`
2. 查找 `.proto` 文件（可能在 JS 中嵌入或从 API 获取）

**逆向技巧 1: 提取 .proto 定义**

```javascript
// 在浏览器 Console 中搜索
for (let key in window) {
  if (key.includes("proto") || key.includes("Proto")) {
    console.log(key, window[key]);
  }
}
```

**逆向技巧 2: 使用 protobuf-inspector 猜解**

```bash
pip install protobuf-inspector

# 分析二进制数据
protobuf-inspector < message.bin
```

**输出示例**:

```
1: "chat"           # Tag 1, 类型 string
2: 123              # Tag 2, 类型 int
3: 1638360000       # Tag 3, 类型 int
```

**Python 解码**（已知 .proto 定义）:

```python
import message_pb2  # 由 protoc 编译生成

data = b'\x0a\x04chat\x10\x7b\x18\x80\xe0\xf3\xc6\x06'
msg = message_pb2.ChatMessage()
msg.ParseFromString(data)
print(msg)
```

#### MsgPack

**特征**:

- 类似二进制版的 JSON
- 支持多种数据类型（int、string、array、map）

**识别方法**: 查找 `msgpack.decode`、`msgpack.encode`

**Python 解码**:

```python
import msgpack

data = b'\x82\xa4type\xa4chat\xa7user_id\x7b'
msg = msgpack.unpackb(data)
print(msg)  # {'type': 'chat', 'user_id': 123}
```

**在线工具**: [MessagePack Viewer](https://sugendran.github.io/msgpack-visualizer/)

#### 自定义二进制格式

**案例**: 某游戏的二进制协议

**抓包示例**:

```
00 01 00 7b 00 00 01 8b 48 65 6c 6c 6f
│  │  │     │           │
│  │  │     │           └─ "Hello" (UTF-8)
│  │  │     └─ Timestamp (4 bytes)
│  │  └─ User ID (2 bytes, 0x007b = 123)
│  └─ Message Type (1 = chat)
└─ Version
```

**逆向步骤**:

1. 对比多个消息，找出固定字段位置
2. 根据数值范围猜测字段类型（uint8, uint16, uint32）
3. 编写解析器

**Python 解析**:

```python
import struct

def parse_custom_protocol(data):
    version, msg_type, user_id, timestamp = struct.unpack('>BBHI', data[:8])
    message = data[8:].decode('utf-8')

    return {
        'version': version,
        'type': msg_type,
        'user_id': user_id,
        'timestamp': timestamp,
        'message': message
    }

# 测试
data = bytes.fromhex('00 01 00 7b 00 00 01 8b 48656c6c6f')
print(parse_custom_protocol(data))
```

---

## 4. Hook WebSocket

### 4.1 劫持 WebSocket 构造函数

在页面加载前注入脚本（通过 Tampermonkey 或浏览器扩展）：

```javascript
(function () {
  const _WebSocket = window.WebSocket;
  window.WebSocket = function (url, protocols) {
    console.log("[WS] 连接:", url);

    const ws = new _WebSocket(url, protocols);

    // Hook send 方法
    const _send = ws.send;
    ws.send = function (data) {
      console.log("[WS Send]", data);
      debugger; // 发送前断点
      return _send.apply(this, arguments);
    };

    // Hook message 事件
    ws.addEventListener("message", function (e) {
      console.log("[WS Recv]", e.data);
    });

    // Hook close 事件
    ws.addEventListener("close", function (e) {
      console.log("[WS Close]", e.code, e.reason);
    });

    // Hook error 事件
    ws.addEventListener("error", function (e) {
      console.error("[WS Error]", e);
    });

    return ws;
  };
})();
```

### 4.2 修改消息内容

```javascript
const _send = ws.send;
ws.send = function (data) {
  // 解析 JSON
  let msg = JSON.parse(data);

  // 修改内容
  if (msg.type === "chat") {
    msg.message = "Modified by hook!";
  }

  // 发送修改后的消息
  return _send.call(this, JSON.stringify(msg));
};
```

### 4.3 拦截二进制消息

```javascript
ws.addEventListener("message", function (e) {
  if (e.data instanceof ArrayBuffer) {
    // 二进制数据
    const view = new Uint8Array(e.data);
    console.log(
      "[Binary]",
      Array.from(view)
        .map((b) => b.toString(16).padStart(2, "0"))
        .join(" ")
    );
  } else {
    // 文本数据
    console.log("[Text]", e.data);
  }
});
```

---

## 5. Python 客户端实现

### 5.1 基础连接

```python
import asyncio
import websockets
import json

async def connect():
    uri = "wss://example.com/socket"

    async with websockets.connect(uri) as ws:
        print("已连接")

        # 发送消息
        await ws.send(json.dumps({
            "type": "auth",
            "token": "your_token_here"
        }))

        # 接收消息
        while True:
            message = await ws.recv()
            data = json.loads(message)
            print("收到:", data)

asyncio.run(connect())
```

### 5.2 完整客户端类

```python
import asyncio
import websockets
import json
import time

class WebSocketClient:
    def __init__(self, uri, token):
        self.uri = uri
        self.token = token
        self.ws = None
        self.running = False

    async def connect(self):
        """连接 WebSocket"""
        self.ws = await websockets.connect(
            self.uri,
            extra_headers={
                "User-Agent": "Mozilla/5.0",
                "Origin": "https://example.com"
            }
        )
        self.running = True
        print("[连接成功]")

        # 发送认证消息
        await self.send_message({
            "type": "auth",
            "token": self.token
        })

    async def send_message(self, data):
        """发送消息"""
        message = json.dumps(data)
        await self.ws.send(message)
        print(f"[发送] {message}")

    async def receive_loop(self):
        """接收消息循环"""
        try:
            while self.running:
                message = await self.ws.recv()
                await self.handle_message(message)
        except websockets.ConnectionClosed:
            print("[连接已关闭]")
            self.running = False

    async def handle_message(self, message):
        """处理收到的消息"""
        try:
            data = json.loads(message)
            print(f"[收到] {data}")

            # 根据消息类型处理
            if data.get("type") == "ping":
                # 响应心跳
                await self.send_message({"type": "pong"})

            elif data.get("type") == "data":
                # 处理业务数据
                self.process_data(data)

        except Exception as e:
            print(f"[错误] 处理消息失败: {e}")

    def process_data(self, data):
        """处理业务数据"""
        # 这里实现你的业务逻辑
        pass

    async def heartbeat_loop(self):
        """心跳循环"""
        while self.running:
            await asyncio.sleep(30)  # 每 30 秒
            if self.running:
                await self.send_message({"type": "ping"})

    async def run(self):
        """运行客户端"""
        await self.connect()

        # 并发运行接收循环和心跳循环
        await asyncio.gather(
            self.receive_loop(),
            self.heartbeat_loop()
        )

    async def close(self):
        """关闭连接"""
        self.running = False
        if self.ws:
            await self.ws.close()
            print("[已断开连接]")

# 使用
async def main():
    client = WebSocketClient(
        uri="wss://example.com/socket",
        token="your_token_here"
    )

    try:
        await client.run()
    except KeyboardInterrupt:
        await client.close()

asyncio.run(main())
```

### 5.3 断线重连

```python
class WebSocketClient:
    # ... 前面的代码 ...

    async def run_with_reconnect(self):
        """带自动重连的运行"""
        max_retries = 5
        retry_count = 0

        while retry_count < max_retries:
            try:
                await self.connect()
                retry_count = 0  # 连接成功，重置计数

                await asyncio.gather(
                    self.receive_loop(),
                    self.heartbeat_loop()
                )

            except Exception as e:
                retry_count += 1
                wait_time = min(2 ** retry_count, 60)  # 指数退避，最多 60 秒
                print(f"[错误] {e}")
                print(f"[重连] {retry_count}/{max_retries}，等待 {wait_time} 秒...")
                await asyncio.sleep(wait_time)

        print("[失败] 超过最大重试次数")
```

### 5.4 处理二进制消息

```python
import struct

class WebSocketClient:
    async def handle_message(self, message):
        # 判断消息类型
        if isinstance(message, bytes):
            # 二进制消息
            await self.handle_binary_message(message)
        else:
            # 文本消息
            await self.handle_text_message(message)

    async def handle_binary_message(self, data):
        """处理二进制消息"""
        # 示例：自定义协议
        msg_type, user_id, timestamp = struct.unpack('>BHI', data[:7])
        payload = data[7:]

        print(f"[二进制] type={msg_type}, user_id={user_id}, time={timestamp}")
        print(f"[Payload] {payload.hex()}")

    async def handle_text_message(self, message):
        """处理文本消息"""
        data = json.loads(message)
        print(f"[文本] {data}")
```

---

## 6. 认证与安全

### 6.1 Token 认证

**方式 1: 在连接 URL 中传递**

```python
uri = f"wss://example.com/socket?token={token}"
```

**方式 2: 在 Header 中传递**

```python
ws = await websockets.connect(
    uri,
    extra_headers={"Authorization": f"Bearer {token}"}
)
```

**方式 3: 连接后发送认证消息**

```python
await ws.send(json.dumps({"type": "auth", "token": token}))
response = await ws.recv()
# 验证认证是否成功
```

### 6.2 加密消息

**案例**: 某聊天应用的 AES 加密

**浏览器端**:

```javascript
// 发送前加密
function sendEncrypted(ws, data) {
  const key = CryptoJS.enc.Utf8.parse("1234567890abcdef");
  const iv = CryptoJS.enc.Utf8.parse("abcdef1234567890");
  const encrypted = CryptoJS.AES.encrypt(JSON.stringify(data), key, {
    iv: iv,
    mode: CryptoJS.mode.CBC,
  });
  ws.send(encrypted.toString()); // Base64 格式
}
```

**Python 复现**:

```python
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
import json

class EncryptedWebSocketClient(WebSocketClient):
    def __init__(self, uri, token):
        super().__init__(uri, token)
        self.key = b'1234567890abcdef'
        self.iv = b'abcdef1234567890'

    def encrypt_message(self, data):
        """加密消息"""
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        plaintext = json.dumps(data).encode()
        encrypted = cipher.encrypt(pad(plaintext, AES.block_size))
        return base64.b64encode(encrypted).decode()

    def decrypt_message(self, encrypted_b64):
        """解密消息"""
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        encrypted = base64.b64decode(encrypted_b64)
        decrypted = unpad(cipher.decrypt(encrypted), AES.block_size)
        return json.loads(decrypted.decode())

    async def send_message(self, data):
        """发送加密消息"""
        encrypted = self.encrypt_message(data)
        await self.ws.send(encrypted)

    async def handle_message(self, message):
        """处理加密消息"""
        try:
            decrypted = self.decrypt_message(message)
            print(f"[收到] {decrypted}")
        except Exception as e:
            print(f"[错误] 解密失败: {e}")
```

---

## 7. 实战案例

### 案例 1：股票行情 WebSocket

**目标**: 获取实时股票价格

**分析过程**:

1. Chrome DevTools 抓包，发现消息格式为 JSON
2. 观察消息类型:

   ```json
   // 订阅股票
   {"type": "subscribe", "symbols": ["AAPL", "TSLA"]}

   // 接收行情
   {"type": "quote", "symbol": "AAPL", "price": 150.25, "time": 1638360000}
   ```

3. 发现需要登录后获取 Token

**完整脚本**:

```python
import asyncio
import websockets
import json

async def stock_client():
    # 1. 登录获取 Token（省略登录代码）
    token = "your_token_here"

    # 2. 连接 WebSocket
    uri = f"wss://quotes.example.com/stream?token={token}"
    async with websockets.connect(uri) as ws:
        print("已连接股票行情服务器")

        # 3. 订阅股票
        await ws.send(json.dumps({
            "type": "subscribe",
            "symbols": ["AAPL", "TSLA", "GOOG"]
        }))

        # 4. 接收行情
        while True:
            message = await ws.recv()
            data = json.loads(message)

            if data["type"] == "quote":
                symbol = data["symbol"]
                price = data["price"]
                print(f"{symbol}: ${price}")

            elif data["type"] == "ping":
                # 响应心跳
                await ws.send(json.dumps({"type": "pong"}))

asyncio.run(stock_client())
```

### 案例 2：游戏协议逆向（Protobuf）

**目标**: 逆向某在线游戏的 WebSocket 协议

**分析过程**:

1. 抓包发现是二进制消息（Opcode = 0x2）
2. 搜索 JS 代码，找到 `proto` 对象和 `.proto` 定义
3. 提取 `.proto` 文件并使用 `protoc` 编译

**.proto 定义**:

```protobuf
syntax = "proto3";

message GameMessage {
    enum Type {
        LOGIN = 0;
        MOVE = 1;
        CHAT = 2;
    }

    Type type = 1;
    int32 user_id = 2;
    int64 timestamp = 3;
    bytes payload = 4;
}

message MovePayload {
    float x = 1;
    float y = 2;
    float z = 3;
}
```

**编译 .proto**:

```bash
protoc --python_out=. game.proto
```

**Python 客户端**:

```python
import asyncio
import websockets
import game_pb2
import time

async def game_client():
    uri = "wss://game.example.com/ws"

    async with websockets.connect(uri) as ws:
        # 发送登录消息
        login_msg = game_pb2.GameMessage()
        login_msg.type = game_pb2.GameMessage.LOGIN
        login_msg.user_id = 12345
        login_msg.timestamp = int(time.time())
        await ws.send(login_msg.SerializeToString())

        # 发送移动消息
        move_msg = game_pb2.GameMessage()
        move_msg.type = game_pb2.GameMessage.MOVE
        move_msg.user_id = 12345
        move_msg.timestamp = int(time.time())

        # 嵌入移动数据
        move_payload = game_pb2.MovePayload()
        move_payload.x = 100.5
        move_payload.y = 200.3
        move_payload.z = 50.0
        move_msg.payload = move_payload.SerializeToString()

        await ws.send(move_msg.SerializeToString())

        # 接收消息
        while True:
            data = await ws.recv()
            msg = game_pb2.GameMessage()
            msg.ParseFromString(data)
            print(f"收到消息: type={msg.type}, user_id={msg.user_id}")

asyncio.run(game_client())
```

### 案例 3：聊天应用协议

**目标**: 自动发送消息到聊天室

**分析过程**:

1. 发现消息格式为 JSON
2. 需要先认证，然后保持心跳
3. 序列号 (seq) 必须递增

**完整脚本**:

```python
import asyncio
import websockets
import json
import time

class ChatClient:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.seq = 0
        self.ws = None

    def next_seq(self):
        """生成下一个序列号"""
        self.seq += 1
        return self.seq

    async def connect(self):
        """连接并认证"""
        self.ws = await websockets.connect("wss://chat.example.com/ws")

        # 发送认证消息
        await self.ws.send(json.dumps({
            "seq": self.next_seq(),
            "type": "auth",
            "username": self.username,
            "password": self.password
        }))

        # 等待认证响应
        response = await self.ws.recv()
        data = json.loads(response)

        if data.get("type") == "auth_success":
            print("认证成功")
            return True
        else:
            print("认证失败:", data)
            return False

    async def send_chat(self, room_id, message):
        """发送聊天消息"""
        await self.ws.send(json.dumps({
            "seq": self.next_seq(),
            "type": "chat",
            "room_id": room_id,
            "message": message,
            "timestamp": int(time.time() * 1000)
        }))

    async def heartbeat_loop(self):
        """心跳循环"""
        while True:
            await asyncio.sleep(30)
            await self.ws.send(json.dumps({
                "seq": self.next_seq(),
                "type": "ping"
            }))

    async def receive_loop(self):
        """接收消息循环"""
        while True:
            message = await self.ws.recv()
            data = json.loads(message)
            print(f"[{data['seq']}] {data['type']}: {data.get('message', '')}")

    async def run(self):
        """运行客户端"""
        if await self.connect():
            # 发送测试消息
            await self.send_chat(room_id=1, message="Hello from bot!")

            # 并发运行接收和心跳
            await asyncio.gather(
                self.receive_loop(),
                self.heartbeat_loop()
            )

# 使用
async def main():
    client = ChatClient("bot_user", "bot_password")
    await client.run()

asyncio.run(main())
```

---

## 8. 常见问题与调试

### 8.1 连接失败

**错误**: `WebSocketException: Invalid HTTP status code: 403`

**原因**:

- 缺少必要的 Headers（如 Origin、User-Agent）
- Token 过期或无效
- IP 被封禁

**解决方案**:

```python
# 添加完整的 Headers
ws = await websockets.connect(
    uri,
    extra_headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Origin": "https://example.com",
        "Referer": "https://example.com/chat",
        "Cookie": "session=YOUR_SESSION_COOKIE"
    }
)
```

### 8.2 心跳超时

**现象**: 连接过几分钟后自动断开

**原因**: 服务器要求定期发送心跳，否则会主动关闭连接

**解决方案**:

```python
async def heartbeat_loop(self):
    while self.running:
        try:
            await asyncio.wait_for(
                self.ws.send(json.dumps({"type": "ping"})),
                timeout=5.0  # 5 秒超时
            )
            await asyncio.sleep(30)  # 每 30 秒发送一次
        except asyncio.TimeoutError:
            print("[心跳超时]")
            break
```

### 8.3 消息乱序

**现象**: 收到的消息顺序不对

**原因**: 网络延迟或服务器并发处理

**解决方案**: 使用序列号 (seq) 重新排序

```python
class MessageQueue:
    def __init__(self):
        self.queue = {}
        self.next_seq = 1

    def add_message(self, seq, data):
        """添加消息"""
        self.queue[seq] = data
        self.process_queue()

    def process_queue(self):
        """按序处理消息"""
        while self.next_seq in self.queue:
            data = self.queue.pop(self.next_seq)
            print(f"[处理消息 {self.next_seq}] {data}")
            self.next_seq += 1
```

### 8.4 调试技巧

**打印十六进制**:

```python
def hex_dump(data):
    """打印十六进制"""
    hex_str = ' '.join(f'{b:02x}' for b in data)
    print(f"[Hex] {hex_str}")

# 使用
async def handle_message(self, message):
    if isinstance(message, bytes):
        hex_dump(message)
```

**保存到文件**:

```python
import datetime

def log_message(message, direction):
    """记录消息到文件"""
    timestamp = datetime.datetime.now().isoformat()
    with open('ws_log.txt', 'a') as f:
        f.write(f"[{timestamp}] {direction}\n{message}\n\n")

# 使用
async def send_message(self, data):
    message = json.dumps(data)
    log_message(message, "SEND")
    await self.ws.send(message)

async def handle_message(self, message):
    log_message(message, "RECV")
    # ... 处理逻辑
```

---

## 9. 工具推荐

| 工具                | 用途                 | 平台    |
| ------------------- | -------------------- | ------- |
| **Chrome DevTools** | 浏览器内 WS 抓包调试 | Chrome  |
| **Wireshark**       | 深度包分析、SSL 解密 | 全平台  |
| **mitmproxy**       | 可编程拦截和修改     | 全平台  |
| **wscat**           | 命令行 WS 客户端测试 | Node.js |
| **websocat**        | 高级命令行 WS 工具   | Rust    |
| **Postman**         | API 测试（支持 WS）  | 全平台  |

**wscat 使用**:

```bash
npm install -g wscat

# 连接
wscat -c wss://echo.websocket.org

# 发送消息
> Hello WebSocket

# 带 Header
wscat -c wss://example.com/ws -H "Authorization: Bearer token123"
```

---

## 总结

WebSocket 逆向的关键步骤：

1. ✅ **抓包分析**: Chrome DevTools / Wireshark / mitmproxy
2. ✅ **协议识别**: JSON / Protobuf / MsgPack / 自定义格式
3. ✅ **Hook 技术**: 劫持 WebSocket 构造函数和方法
4. ✅ **客户端实现**: Python websockets 库，处理认证、心跳、重连
5. ✅ **加密处理**: AES/RSA 加密消息的加解密
6. ✅ **调试技巧**: 日志记录、十六进制 dump、消息重排序

**记住**: WebSocket 逆向的本质是**协议逆向** —— 搞清楚它"说什么话"（Payload 格式）以及"怎么说话"（状态机、心跳、认证），你就能伪造它。

---

## 相关章节

- [动态参数分析](./dynamic_parameter_analysis.md)
- [API 逆向与重放攻击](./api_reverse_engineering.md)
- [Wireshark 使用指南](../02-Tooling/wireshark_guide.md)
- [Hooking 技术](./hooking_techniques.md)
- [加密算法识别](../03-Basic-Recipes/crypto_identification.md)
