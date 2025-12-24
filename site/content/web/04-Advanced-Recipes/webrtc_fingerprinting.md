---
title: "WebRTC 指纹与隐私"
weight: 10
---

# WebRTC 指纹与隐私

## 概述

WebRTC (Web Real-Time Communication) 是一种支持网页浏览器进行实时语音、视频通信和数据共享的技术。然而，WebRTC 也可能泄露用户的真实 IP 地址和其他设备信息，成为指纹识别和隐私泄露的重要途径。

---

## 📚 前置知识

在开始本配方之前，建议先掌握以下内容：

| 知识领域 | 重要程度 | 参考资料 |
|----------|---------|---------|
| 浏览器架构 | 必需 | [浏览器架构](../01-Foundations/browser_architecture.md) |
| 浏览器指纹识别 | 必需 | [浏览器指纹识别](./browser_fingerprinting.md) |
| JavaScript 基础 | 必需 | [JavaScript 基础](../01-Foundations/javascript_basics.md) |
| Hook 技术 | 推荐 | [Hook 技术](../03-Basic-Recipes/hooking_techniques.md) |

> 💡 **提示**: WebRTC 是最容易**泄露真实 IP** 的途径之一。即使使用 VPN 或代理，WebRTC 也可能暴露你的本地 IP。了解这一机制对于隐私保护和自动化爬虫至关重要。

---

## 基础概念

### 定义

**WebRTC** 是一组标准化的 API，允许浏览器和移动应用程序进行点对点的实时通信，无需安装插件或第三方软件。

**主要组件**:

- **getUserMedia**: 访问摄像头和麦克风
- **RTCPeerConnection**: 建立点对点音视频通信
- **RTCDataChannel**: 点对点数据传输

**隐私风险**:

- 泄露真实 IP 地址（绕过 VPN/代理）
- 收集设备指纹信息
- 获取本地网络拓扑
- 暴露媒体设备信息

### 核心原理

#### WebRTC 连接建立过程

```
客户端 A 客户端 B
| |
|-- 1. 创建 RTCPeerConnection ----------->|
| |
|-- 2. 收集 ICE Candidates --------------->|
| (包含本地/公网 IP) |
| |
|<- 3. 交换 SDP Offer/Answer --------------|
| |
|-- 4. 建立点对点连接 -------------------->|
| |
|<======= 5. 实时通信 =====================>|
```

#### ICE (Interactive Connectivity Establishment)

WebRTC 使用 ICE 协议收集候选连接路径：

- **Host Candidate**: 本地 IP 地址（局域网 IP）
- **Server Reflexive Candidate**: 公网 IP（通过 STUN 服务器获取）
- **Relay Candidate**: 中继 IP（通过 TURN 服务器）

这些信息可以被 JavaScript 访问，导致 IP 泄露。

---

## 详细内容

### IP 地址泄露

#### 1. **本地 IP 泄露**

即使用户使用 VPN，WebRTC 仍可能泄露真实的本地 IP。

**泄露机制**:

```javascript
// 创建 RTCPeerConnection
const pc = new RTCPeerConnection({
iceServers: [{ urls: "stun:stun.l.google.com:19302" }],
});

// 创建虚拟数据通道
pc.createDataChannel("");

// 创建 Offer
pc.createOffer().then((offer) => pc.setLocalDescription(offer));

// 监听 ICE 候选
pc.onicecandidate = (ice) => {
if (ice && ice.candidate && ice.candidate.candidate) {
const candidate = ice.candidate.candidate;
console.log("ICE Candidate:", candidate);

// 解析 IP 地址
const ipRegex =
/([0-9]{1,3}(\.[0-9]{1,3}){3}|[a-f0-9]{1,4}(:[a-f0-9]{1,4}){7})/;
const match = candidate.match(ipRegex);
if (match) {
console.log("Leaked IP:", match[1]);
}
}
};
```

**泄露的信息**:

- 内网 IPv4 地址 (192.168.x.x, 10.x.x.x)
- 内网 IPv6 地址
- 公网 IPv4/IPv6 地址
- mDNS 候选（某些浏览器）

#### 2. **公网 IP 泄露**

通过 STUN 服务器获取用户的真实公网 IP，绕过 VPN/代理。

**完整示例**:

```javascript
function getIPs(callback) {
const ips = [];
const pc = new RTCPeerConnection({
iceServers: [
{ urls: "stun:stun.l.google.com:19302" },
{ urls: "stun:stun1.l.google.com:19302" },
],
});

pc.createDataChannel("");
pc.createOffer().then((offer) => pc.setLocalDescription(offer));

pc.onicecandidate = (ice) => {
if (!ice || !ice.candidate || !ice.candidate.candidate) {
return;
}

const candidate = ice.candidate.candidate;
const ipRegex =
/([0-9]{1,3}(\.[0-9]{1,3}){3}|[a-f0-9]{1,4}(:[a-f0-9]{1,4}){7})/;
const match = candidate.match(ipRegex);

if (match && !ips.includes(match[1])) {
ips.push(match[1]);
callback(match[1], candidate);
}
};
}

// 使用
getIPs((ip, candidate) => {
console.log("IP:", ip);
console.log(
"Type:",
candidate.includes("typ host")
? "Local"
: candidate.includes("typ srflx")
? "Public"
: "Relay"
);
});
```

### 设备指纹信息

#### 1. **媒体设备枚举**

WebRTC 可以枚举用户的音视频设备：

```javascript
navigator.mediaDevices.enumerateDevices().then((devices) => {
devices.forEach((device) => {
console.log({
kind: device.kind, // "audioinput", "videoinput", "audiooutput"
label: device.label, // 设备名称
deviceId: device.deviceId, // 唯一标识符
groupId: device.groupId, // 设备组
});
});
});
```

**指纹用途**:

- `deviceId` 可作为持久化标识符
- 设备数量和类型组合形成独特指纹
- 设备名称可能暴露硬件信息

#### 2. **编解码器支持**

不同设备支持不同的音视频编解码器：

```javascript
const pc = new RTCPeerConnection();

pc.createOffer().then((offer) => {
const codecs = [];

// 解析 SDP 获取支持的编解码器
offer.sdp.split("\r\n").forEach((line) => {
if (line.startsWith("a=rtpmap:")) {
codecs.push(line);
}
});

console.log("Supported codecs:", codecs);
});
```

#### 3. **RTC 统计信息**

```javascript
const pc = new RTCPeerConnection();

pc.getStats().then((stats) => {
stats.forEach((report) => {
console.log({
type: report.type,
id: report.id,
timestamp: report.timestamp,
...report,
});
});
});
```

**可获取的信息**:

- 网络质量指标
- 传输统计
- 编解码器性能
- 硬件加速能力

### 隐私保护检测

#### 检测 WebRTC 泄露

```javascript
async function detectWebRTCLeak() {
const results = {
localIPs: [],
publicIPs: [],
devices: [],
leakDetected: false,
};

// 1. 检测 IP 泄露
const pc = new RTCPeerConnection({
iceServers: [{ urls: "stun:stun.l.google.com:19302" }],
});

pc.createDataChannel("");
pc.createOffer().then((offer) => pc.setLocalDescription(offer));

await new Promise((resolve) => {
pc.onicecandidate = (ice) => {
if (!ice || !ice.candidate) {
resolve();
return;
}

const candidate = ice.candidate.candidate;
const ipMatch = candidate.match(/([0-9]{1,3}\.){3}[0-9]{1,3}/);

if (ipMatch) {
const ip = ipMatch[0];
if (
ip.startsWith("192.168.") ||
ip.startsWith("10.") ||
ip.startsWith("172.")
) {
results.localIPs.push(ip);
} else {
results.publicIPs.push(ip);
results.leakDetected = true;
}
}
};

setTimeout(resolve, 2000);
});

// 2. 检测设备枚举
try {
const devices = await navigator.mediaDevices.enumerateDevices();
results.devices = devices.map((d) => ({
kind: d.kind,
label: d.label,
hasId: !!d.deviceId,
}));
} catch (e) {
console.log("Device enumeration blocked");
}

return results;
}

// 使用
detectWebRTCLeak().then((results) => {
console.log("WebRTC Leak Detection Results:", results);
if (results.leakDetected) {
console.warn("⚠️ WebRTC IP leak detected!");
}
});
```

---

## 实战示例

### 示例 1: 完整的 IP 泄露检测工具

```javascript
class WebRTCLeakDetector {
constructor() {
this.ips = new Set();
this.candidates = [];
}

async detect() {
return new Promise((resolve) => {
const pc = new RTCPeerConnection({
iceServers: [
{ urls: "stun:stun.l.google.com:19302" },
{ urls: "stun:stun1.l.google.com:19302" },
{ urls: "stun:stun.services.mozilla.com" },
],
});

pc.createDataChannel("leak-test");
pc.createOffer()
.then((offer) => pc.setLocalDescription(offer))
.catch((err) => console.error(err));

pc.onicecandidate = (event) => {
if (!event || !event.candidate) {
pc.close();
resolve(this.generateReport());
return;
}

this.processCandidate(event.candidate);
};

// 超时保护
setTimeout(() => {
pc.close();
resolve(this.generateReport());
}, 5000);
});
}

processCandidate(candidate) {
this.candidates.push(candidate.candidate);

const parts = candidate.candidate.split(" ");
const ip = parts[4];
const type = parts[7];

if (ip && this.isValidIP(ip)) {
this.ips.add(ip);
console.log(`Found ${type} IP: ${ip}`);
}
}

isValidIP(str) {
// IPv4
const ipv4 = /^(\d{1,3}\.){3}\d{1,3}$/;
// IPv6
const ipv6 = /^([\da-f]{1,4}:){7}[\da-f]{1,4}$/i;

return ipv4.test(str) || ipv6.test(str);
}

generateReport() {
const report = {
ips: Array.from(this.ips),
local: [],
public: [],
ipv6: [],
candidates: this.candidates,
};

report.ips.forEach((ip) => {
if (ip.includes(":")) {
report.ipv6.push(ip);
} else if (this.isLocalIP(ip)) {
report.local.push(ip);
} else {
report.public.push(ip);
}
});

return report;
}

isLocalIP(ip) {
return (
ip.startsWith("192.168.") ||
ip.startsWith("10.") ||
ip.match(/^172\.(1[6-9]|2\d|3[01])\./)
);
}
}

// 使用
const detector = new WebRTCLeakDetector();
detector.detect().then((report) => {
console.log("=== WebRTC Leak Report ===");
console.log("Local IPs:", report.local);
console.log("Public IPs:", report.public);
console.log("IPv6:", report.ipv6);

if (report.public.length > 0) {
console.warn("⚠️ Public IP leak detected!");
}
});
```

### 示例 2: 禁用 WebRTC

```javascript
// 方法1: 覆盖 RTCPeerConnection (不推荐，可能破坏功能)
(function () {
"use strict";

const noop = function () {};
const noopPromise = function () {
return Promise.resolve();
};

window.RTCPeerConnection = function () {
return {
createOffer: noopPromise,
createAnswer: noopPromise,
setLocalDescription: noopPromise,
setRemoteDescription: noopPromise,
close: noop,
addEventListener: noop,
};
};

console.log("WebRTC has been disabled");
})();

// 方法2: 浏览器设置
// Chrome: chrome://flags/#enable-webrtc-hide-local-ips-with-mdns
// Firefox: media.peerconnection.enabled = false

// 方法3: 浏览器扩展
// - WebRTC Leak Prevent (Chrome)
// - Disable WebRTC (Firefox)
```

### 示例 3: 设备指纹采集

```javascript
async function collectWebRTCFingerprint() {
const fingerprint = {};

// 1. 媒体设备
try {
const devices = await navigator.mediaDevices.enumerateDevices();
fingerprint.devices = devices.map((d) => ({
kind: d.kind,
id: d.deviceId,
groupId: d.groupId,
}));
fingerprint.deviceCount = {
audioinput: devices.filter((d) => d.kind === "audioinput").length,
videoinput: devices.filter((d) => d.kind === "videoinput").length,
audiooutput: devices.filter((d) => d.kind === "audiooutput").length,
};
} catch (e) {
fingerprint.devices = "blocked";
}

// 2. 支持的编解码器
const pc = new RTCPeerConnection();
const offer = await pc.createOffer({
offerToReceiveAudio: true,
offerToReceiveVideo: true,
});

fingerprint.codecs = {
audio: [],
video: [],
};

offer.sdp.split("\r\n").forEach((line) => {
if (line.startsWith("a=rtpmap:")) {
const codec = line.split(" ")[1];
if (line.includes("audio")) {
fingerprint.codecs.audio.push(codec);
} else if (line.includes("video")) {
fingerprint.codecs.video.push(codec);
}
}
});

pc.close();

// 3. RTC 能力
fingerprint.capabilities = {
audio: RTCRtpSender.getCapabilities
? RTCRtpSender.getCapabilities("audio")
: null,
video: RTCRtpSender.getCapabilities
? RTCRtpSender.getCapabilities("video")
: null,
};

return fingerprint;
}

// 使用
collectWebRTCFingerprint().then((fp) => {
console.log("WebRTC Fingerprint:", fp);

// 计算指纹哈希
const fpString = JSON.stringify(fp);
console.log("Fingerprint hash:", hashCode(fpString));
});

function hashCode(str) {
let hash = 0;
for (let i = 0; i < str.length; i++) {
const char = str.charCodeAt(i);
hash = (hash << 5) - hash + char;
hash = hash & hash;
}
return hash.toString(16);
}
```

---

## 最佳实践

### 用户隐私保护

1. **使用浏览器扩展**

- WebRTC Leak Prevent
- uBlock Origin (启用隐私过滤)
- Privacy Badger

2. **浏览器设置**

**Firefox**:

- `about:config` → `media.peerconnection.enabled` = `false`
- `media.peerconnection.ice.default_address_only` = `true`
- `media.peerconnection.ice.no_host` = `true`

**Chrome**:

- `chrome://flags/#enable-webrtc-hide-local-ips-with-mdns` 启用
- 使用扩展程序

3. **VPN 配置**

- 确保 VPN 支持 WebRTC 保护
- 启用 VPN 的 IPv6 泄露防护
- 测试 VPN 是否真正阻止 WebRTC 泄露

4. **定期检测**
- 访问 https://browserleaks.com/webrtc
- 使用 https://ipleak.net
- 自定义检测脚本

### 网站开发者

1. **最小权限原则**

- 仅在必要时请求媒体权限
- 明确告知用户为何需要 WebRTC

2. **隐私声明**

- 说明如何使用 WebRTC
- 告知可能收集的信息

3. **提供控制选项**
- 允许用户禁用 WebRTC 功能
- 提供替代方案

---

## 常见问题

### Q: VPN 能防止 WebRTC 泄露吗？

**A**: 不一定。WebRTC 可以绕过 VPN 直接泄露本地和公网 IP：

- **本地 IP**: VPN 无法隐藏（192.168.x.x）
- **公网 IP**: 可能绕过 VPN 隧道泄露真实 IP
- **解决方案**: 禁用 WebRTC 或使用支持 WebRTC 保护的 VPN

### Q: 为什么浏览器允许 WebRTC 泄露 IP？

**A**:

- WebRTC 设计用于点对点通信，需要真实 IP 建立连接
- 这是功能需求，不是安全漏洞
- 浏览器逐步增强隐私保护（如 mDNS）

### Q: mDNS 是什么？如何保护隐私？

**A**:
**mDNS** (Multicast DNS) 是一种隐私保护机制：

- 用随机 `.local` 地址替代真实本地 IP
- Chrome 和 Safari 默认启用
- Firefox 需要手动配置

示例：`a1b2c3d4.local` 而不是 `192.168.1.100`

### Q: 如何检测网站是否在收集 WebRTC 指纹？

**A**:

1. 打开浏览器开发者工具
2. 在 Console 中运行：

```javascript
RTCPeerConnection.prototype._createOffer = RTCPeerConnection.prototype.createOffer;
RTCPeerConnection.prototype.createOffer = function () {
    console.trace("WebRTC createOffer called");
    return this._createOffer.apply(this, arguments);
};
```
3. 查看是否有 WebRTC 调用的堆栈追踪

---

## 进阶阅读

### 官方文档

- [WebRTC API - MDN](https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API)
- [WebRTC 规范](https://www.w3.org/TR/webrtc/)
- [ICE 协议 RFC 5245](https://tools.ietf.org/html/rfc5245)

### 隐私研究

- [WebRTC IP Leak Vulnerability](https://research.checkpoint.com/webrtc-vulnerability/)
- [Fingerprintability of WebRTC](https://arxiv.org/abs/1605.08805)
- [WebRTC Privacy and Security Considerations](https://tools.ietf.org/html/draft-ietf-rtcweb-security)

### 检测工具

- [BrowserLeaks WebRTC Test](https://browserleaks.com/webrtc)
- [IPLeak.net](https://ipleak.net/)
- [Perfect Privacy Check IP](https://www.perfect-privacy.com/en/tests/check-ip)

---

## 相关章节

- [Canvas 指纹识别](./canvas_fingerprinting.md)
- [TLS 指纹识别](./tls_fingerprinting.md)
- [浏览器指纹技术](../01-Tools/browser_fingerprinting.md)
- [隐私保护技术](../02-Techniques/privacy_protection.md)
