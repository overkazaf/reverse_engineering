---
title: "视频 App 与 DRM 案例"
date: 2025-09-15
weight: 10
---

# 视频 App 与 DRM 案例

> **📚 前置知识**
>
> 本案例涉及以下核心技术，建议先阅读相关章节：
>
> - **[网络抓包技术](../01-Recipes/Network/network_sniffing.md)** - 拦截 HLS/DASH 视频流协议
> - **[密码学分析](../01-Recipes/Network/crypto_analysis.md)** - 理解 AES 加密与 DRM 密钥交换

视频类 App 的逆向分析是移动端安全领域最具挑战性的方向之一，其核心难点在于数字版权管理（DRM）技术的对抗。本案例将深入探讨视频 App，特别是涉及 DRM 的分析思路。

## 核心分析目标

1. **视频流分析**: 解析视频播放的网络协议，如 `HLS` (`.m3u8`) 和 `DASH` (`.mpd`)，并提取视频分片。
2. **解锁 VIP 功能**: 绕过付费墙，观看 VIP 专属影片或解锁更高清晰度（如 1080p, 4K）。
3. **DRM 对抗**: 理解 DRM 的工作原理，并尝试获取解密视频所需的密钥。**（注意：这通常是极其困难的，且可能涉及法律风险。）**

---

## 案例：分析一个使用 Widevine DRM 的视频播放流程

### 第 1 步：视频流协议分析

**目标**: 找到描述视频信息的清单文件 (`.m3u8` 或 `.mpd`)。

1. **网络抓包**: 打开 Charles 或 Mitmproxy，启动目标视频 App 并播放一个影片。
2. **过滤请求**: 在抓包结果中，使用关键词 `m3u8` 或 `mpd` 进行过滤。你很快就能定位到一个请求，其 URL 类似于 `https://.../video.mpd`。
3. **分析清单文件**:

- **DASH (`.mpd`)**: 这是一个 XML 文件，描述了视频的各种信息，包括不同的分辨率、音轨、字幕轨道以及加密信息。

- **HLS (`.m3u8`)**: 这是一个文本文件。主 `m3u8` 文件可能指向多个子 `m3u8` 文件，每个子文件代表一种特定的码率（清晰度），并包含了该码率下所有视频分片（`.ts` 文件）的 URL。

在清单文件中，你会找到一个关键的标签，表明内容是受保护的，例如：

```xml
<!-- DASH MPD inEncryptInformation -->
<ContentProtection schemeIdUri="urn:uuid:edef8ba9-79d6-4ace-a3c8-27dcd51d21ed" cenc:default_KID="...value...">
<cenc:pssh>...</cenc:pssh>
</ContentProtection>

```

### 第 2 步：理解 DRM 工作流程 (Widevine)

Google 的 Widevine 是 Android 平台上最主流的 DRM 方案。它分为三个安全级别 (L1, L2, L3)，其中 L1 安全性最高。

1. **App 请求播放**: App 从视频清单中解析出 `pssh` 数据。
2. **获取许可证 (License)**: App 将 `pssh` 数据发送给系统的 `MediaDrm` API，生成一个许可证请求（License Request）。然后，App 将这个请求发送到视频服务提供商的许可证服务器。
3. **服务器验证**: 许可证服务器验证请求的合法性（例如，验证用户的 VIP 身份），然后返回一个加密的许可证（Encrypted License）。
4. **解密密钥**: App 将加密的许可证提供给 `MediaDrm` API。这一步是关键：

- **L1 安全级别**: 许可证的处理和内容密钥的解密完全在处理器的可信执行环境（TEE）中进行。Android 操作系统和 App 本身都无法访问到解密后的密钥。视频帧的解密也在 TEE 中完成，然后直接输出到屏幕，不会在 App 的内存中暴露。

- **L3 安全级别**: 在没有 TEE 支持的设备上，这些操作都在软件层面完成。因此，L3 是理论上最容易被攻击的。

### 第 3 步：逆向分析与信息获取

由于 L1 的硬件级保护，直接获取内容密钥（Content Key）几乎是不可能的，但在一些 arxiv 论文中，笔者确实找到了在一些特定设备中可以利用的漏洞。因此，分析的重点转向了许可证的获取过程。

**目标**: 拦截 App 与许可证服务器之间的通信，获取许可证请求和响应。

1. **定位许可证请求代码**:

- 搜索 `MediaDrm`, `getKeyRequest`, `provideKeyResponse` 等 `android.media` 包中的 DRM 相关 API。

- 使用 Frida Hook 这些方法，可以打印出 `pssh`、许可证请求和加密的许可证响应。

```javascript
Java.perform(function () {
  var MediaDrm = Java.use("android.media.MediaDrm");

  // Hook getKeyRequest method to capture license requests
  MediaDrm.getKeyRequest.implementation = function (
    scope,
    initData,
    mimeType,
    keyType,
    optionalParameters
  ) {
    console.log("Intercepting getKeyRequest...");
    // initData is the pssh
    console.log("PSSH (initData):", bytesToHex(initData));

    var keyRequest = this.getKeyRequest(
      scope,
      initData,
      mimeType,
      keyType,
      optionalParameters
    );
    // keyRequest is a complex object, needs further parsing
    // ...
    return keyRequest;
  };

  // Hook provideKeyResponse method to capture encrypted license
  MediaDrm.provideKeyResponse.implementation = function (scope, response) {
    console.log("Intercepting provideKeyResponse...");
    // response is the encrypted license obtained from the server
    console.log("Encrypted License (response):", bytesToHex(response));

    return this.provideKeyResponse(scope, response);
  };
});
function bytesToHex(arr) {
  /* ... a function to convert byte array to hex string ... */
}
```

3. **CDM (内容解密模块) 分析**: Widevine 的 L3 级 CDM 是一个原生库（`.so` 文件），负责处理白盒加密的逻辑。对这个 `.so` 文件进行深入的静态和动态分析，是理论上还原出设备密钥（Device Key）的唯一途径，这也是 CDM Challenge 等比赛的核心。这是一个极其复杂和耗时的过程。

---

## 主流平台 DRM 与加密方案实例

### 国内平台 (某酷、某奇艺、某讯视频、某果 TV)

国内主流视频平台在加密策略上通常采用**"自研加密方案 + 标准 DRM"**的混合模式。

- 对于拥有全球版权的影视剧（如好莱坞大片），它们会使用行业标准的 Widevine DRM。

- 对于大量的自制剧、综艺等内容，它们更倾向于使用自研的加密方案，其核心是对 HLS 协议进行改造。

**通用模式：保护 HLS 密钥的获取过程**

1. **视频流**: 普遍使用 HLS (`.m3u8`) 协议。
2. **加密算法**: `.m3u8` 文件中会声明视频分片（`.ts` 文件）使用 `AES-128-CBC` 加密。
3. **核心保护**: **视频数据本身的加密算法是标准的，但获取解密密钥（Key）的过程是高度定制和保护的。**

- `.m3u8` 文件本身不是静态的，而是通过一个需要复杂签名的 API 动态生成的。

- `#EXT-X-KEY` 标签中指向的密钥 URL (`key.key`) 也不是一个能直接访问的地址，访问它同样需要正确的 Cookie、Referer 和加密参数。

4. **逆向关键**:

- **定位播放 API**: 逆向的重点是找到 App 中负责请求视频播放信息的 API。这个 API 的请求参数通常包含视频 ID、清晰度、以及一个类似我们在上一章分析过的、包含设备指纹和时间戳的 `sign` 或 `token`。

- **模拟合法请求**: 只要能够成功模拟这个 API 的调用，就能获取到一个包含了有效密钥 URL 的 `.m3u8` 文件。拿到密钥后，就可以使用标准的 `AES-128` 算法解密 `.ts` 文件并合并成一个完整的视频。

- **某讯视频的 `vkey`**: 一个典型的例子是某讯视频，其播放 API 中需要一个至关重要的 `vkey` 参数，这个参数的生成算法就封装在客户端的 SO 库中。

### 国外平台 (Netflix, 某管, Hulu, HBO Max)

国外主流视频平台，特别是内容提供商，严格且深度地依赖标准化的 DRM 体系。逆向的焦点**完全不在于分析视频文件格式或算法，而在于 DRM 许可证的获取流程**。

#### Netflix / Hulu / HBO Max

- **DRM 方案**: 在 Android 上无一例外地使用 Google Widevine，在苹果设备上使用 FairPlay。

- **安全级别**: 对于高清内容（HD, 4K），强制要求设备的 Widevine 安全级别为 L1。这意味着密钥交换和内容解密全程在硬件 TEE 中完成，App 和操作系统均无法触及明文密钥。

- **许可证请求保护**: 逆向的唯一着眼点是 App 发起许可证请求的过程。
- 这个请求被多种方式保护，例如 Netflix 使用自研的 **MSL (Message Security Layer)** 协议对许可证请求本身进行二次封装和加密。

- App 会采集大量设备指纹信息，连同用户的身份凭证一起，用于生成许可证请求。服务端的风控系统会严格校验这些信息，以确保请求来自于一个合法的、未被篡改的官方 App 客户端。
- **逆向结论**: 在 L1 保护下，通过逆向 App 来获取视频解密密钥以进行离线下载是**几乎不可能**的。分析的主要意义在于理解其架构和安全强度。

#### 某管

某管的情况比较特殊，它需要区分对待：

- **付费内容 (某管 Premium / 电影)**: 与 Netflix 类似，使用标准的 Widevine DRM 进行保护。

- **普通 UGC 内容**: 大部分视频没有使用 DRM 加密，但使用了另一种巧妙的保护方式——**动态 URL 签名**。
- **现象**: 使用 `yt-dlp` 等工具下载视频时，会看到它有一个"deciphering signature"的过程。

- **原理**: 视频流的 URL 中包含一个 `s` 或 `sig` 参数，这个签名是由一段混淆过的 JavaScript 代码（在 Web 端）或 Native 代码（在 App 端）动态生成的。该算法将视频的 `cipher` (一段加密字符串) 和其他参数作为输入，输出一个解密的签名。

- **逆向关键**: 逆向的重点不再是 DRM，而是**找到并还原那段负责计算签名的 JavaScript/Native 函数**。由于代码经过了高度混淆，这依然是一项具有挑战性的工作。

### 音乐流媒体平台 (某果音乐, 某破天)

音乐流媒体平台同样采用 DRM 保护其内容，但由于音频文件体积较小、交互模式不同，其加密方案与视频平台有所差异。

#### 某果音乐

某果音乐采用 **Widevine DRM + HLS** 的组合方案保护其音频内容。

**认证体系**:

- **accessToken**: 从 Web 端 JavaScript 中提取的 JWT Token，用于 API 认证
- **mediaUserToken**: 用户身份令牌，存储在 Cookie 中，用于访问个人化内容和高品质音源

**API 架构**:

```python
class AppleMusicAPI:
    # 元数据 API - 获取专辑、歌曲、播放列表信息
    METADATA_API = "https://amp-api.music.apple.com/v1/catalog/{storefront}/{type}s/{id}"

    # 播放信息 API - 获取音频流地址和加密参数
    WEBPLAYBACK_API = "https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/webPlayback"

    def get_webplayback(self, adam_id):
        """获取音频播放信息"""
        return self.session.post(
            self.WEBPLAYBACK_API,
            json={'salableAdamId': adam_id}
        ).json()["songList"][0]
```

**DRM 解密流程**:

1. 从 webPlayback 接口获取 HLS 播放列表 URL
2. 解析 `.m3u8` 文件，提取 `#EXT-X-KEY` 中的 PSSH 数据
3. 使用 Widevine CDM 构造 License Challenge
4. 向 `hls-key-server-url` 发送许可证请求
5. 解析 License 响应，提取 AES 解密密钥
6. 使用密钥解密音频分片

```python
def get_decryption_key(self, song_id, pssh):
    """获取音频解密密钥"""
    # 构造 Widevine PSSH 对象
    widevine_pssh = WidevinePsshData()
    widevine_pssh.algorithm = 1
    widevine_pssh.key_ids.append(base64.b64decode(pssh.split(",")[1]))

    # 获取 License Challenge
    pssh_obj = PSSH(widevine_pssh.SerializeToString())
    session = self.cdm.open()
    challenge = base64.b64encode(
        self.cdm.get_license_challenge(session, pssh_obj)
    ).decode()

    # 请求 License
    license_resp = self.session.post(
        self.license_url,
        json={
            "adamId": song_id,
            "challenge": challenge,
            "key-system": "com.widevine.alpha",
            "uri": f"data:;base64,{pssh}",
        }
    ).json()

    # 解析密钥
    self.cdm.parse_license(session, license_resp["license"])
    return next(
        k for k in self.cdm.get_keys(session)
        if k.type == "CONTENT"
    ).key.hex()
```

**音频格式**: 主要使用 `28:ctrp256` 格式 (256kbps AAC)，通过 HLS 协议分发。

---

#### 某破天

某破天 采用**双轨加密方案**，根据音频格式使用不同的加密机制。

**认证体系**:

- **sp_dc Cookie**: 用户会话凭证，从浏览器 Cookie 中提取
- **TOTP 令牌**: 时间动态令牌，用于生成 accessToken (详见 [TOTP 技术原理](../04-Reference/Foundations/totp.md))
- **Client Token**: 设备认证令牌，包含设备指纹信息

**TOTP 认证机制** (关键反爬措施):

```python
class MusicTOTP:
    """某破天 使用动态 TOTP 进行 API 认证"""

    def __init__(self):
        # 从远程获取 TOTP 参数 (需要定期更新)
        self.version = self._fetch_param("VERSION")
        self.period = self._fetch_param("PERIOD")
        self.digits = self._fetch_param("DIGITS")
        self.secret = self._derive_secret()

    def generate(self, timestamp_ms):
        """生成 TOTP 令牌"""
        counter = timestamp_ms // 1000 // self.period
        counter_bytes = counter.to_bytes(8, byteorder="big")

        h = hmac.new(self.secret, counter_bytes, hashlib.sha1)
        hmac_result = h.digest()

        offset = hmac_result[-1] & 0x0F
        binary = (
            (hmac_result[offset] & 0x7F) << 24 |
            (hmac_result[offset + 1] & 0xFF) << 16 |
            (hmac_result[offset + 2] & 0xFF) << 8 |
            (hmac_result[offset + 3] & 0xFF)
        )
        return str(binary % (10 ** self.digits)).zfill(self.digits)
```

**API 架构**:

```python
class MusicAPI:
    # 元数据 API
    METADATA_API = "https://api.example.com/v1/{type}/{item_id}"

    # 播放信息 API
    PLAYBACK_API = "https://gue1-spclient.example.com/track-playback/v1/media/{type}:{id}"

    # 流地址解析 API
    STREAM_API = "https://gue1-spclient.example.com/storage-resolve/v2/files/audio/interactive/11/{file_id}"

    # Widevine 许可证 API (AAC 格式)
    WIDEVINE_LICENSE_API = "https://gue1-spclient.example.com/widevine-license/v1/{type}/license"

    # PlayPlay 许可证 API (Vorbis 格式)
    PLAYPLAY_LICENSE_API = "https://gew4-spclient.example.com/playplay/v1/key/{file_id}"
```

**双轨加密方案**:

| 格式       | 加密方式           | 品质            | 密钥获取             |
| ---------- | ------------------ | --------------- | -------------------- |
| OGG Vorbis | PlayPlay (AES-CTR) | 96/160/320 kbps | PlayPlay API         |
| AAC (M4A)  | Widevine DRM       | 128/256 kbps    | Widevine License API |

**PlayPlay 解密** (Vorbis 格式):

```python
def decrypt_playplay(self, decryption_key, encrypted_path, decrypted_path):
    """某破天 自研 PlayPlay 加密使用 AES-CTR 模式"""
    cipher = AES.new(
        decryption_key,
        AES.MODE_CTR,
        nonce=bytes.fromhex("72e067fbddcb****"),  # 固定 Nonce
        initial_value=bytes.fromhex("ebe8bc643f63****"),  # 固定 IV
    )

    with open(encrypted_path, "rb") as f:
        encrypted_data = f.read()

    decrypted_data = cipher.decrypt(encrypted_data)

    # 查找 OGG 文件头
    offset = decrypted_data.find(b"OggS")
    with open(decrypted_path, "wb") as f:
        f.write(decrypted_data[offset:])
```

**JA3 指纹检测绕过**:

某破天 使用 JA3 指纹检测来识别非官方客户端。绕过方案：

```python
from curl_cffi import requests as curl_requests

# 使用 curl_cffi 模拟 Chrome 的 TLS 指纹
session = curl_requests.Session(impersonate="chrome120")
```

**无头浏览器保活** (Token 自动刷新):

某破天 的 accessToken 有效期较短，且 TOTP 认证可能被风控拦截。使用无头浏览器可以模拟真实用户行为，自动获取新的 Token：

```python
class HeadlessTokenFetcher:
    """使用无头浏览器自动获取 某破天 Token"""

    def __init__(self):
        self.token_file = Path.home() / '.music_token.json'
        self.cookies_file = Path('./cookies.txt')

    def fetch_with_playwright(self):
        """使用 Playwright 无头浏览器获取 Token"""
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-blink-features=AutomationControlled'
                ]
            )

            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                           'AppleWebKit/537.36 Chrome/142.0.0.0 Safari/537.36'
            )

            # 加载预存的 Cookies (包含 sp_dc)
            if self.cookies_file.exists():
                cookies = self._load_cookies()
                context.add_cookies(cookies)

            page = context.new_page()
            token_data = {}

            # 拦截网络响应，捕获 Token
            def handle_response(response):
                nonlocal token_data
                if '/api/token' in response.url and 'reason=init' in response.url:
                    data = response.json()
                    if 'accessToken' in data:
                        token_data = data

            page.on('response', handle_response)

            # 访问 某破天 触发 Token 请求
            page.goto('https://open.example.com', wait_until='networkidle')
            page.wait_for_timeout(3000)

            browser.close()

            if token_data:
                self._save_token(token_data)
                return True
            return False
```

**保活策略**:

1. 定时任务每 30-50 分钟刷新 Token (有效期约 1 小时)
2. 在 License 请求失败 (403) 时自动触发刷新
3. 使用 Cookies 而非账号密码，避免登录风控
4. 模拟真实浏览器指纹，绕过自动化检测

**逆向要点**:

1. TOTP 参数需要动态获取，某破天 会定期更新
2. 高品质音源 (320kbps Vorbis, 256kbps AAC) 需要 Premium 账户
3. PlayPlay 的 Nonce 和 IV 是固定的，但密钥是动态获取的
4. Client Token 包含设备指纹，用于风控检测
5. 建议使用无头浏览器保活方案，比纯 API 方式更稳定

---

## 视频平台 API 签名实战

以下是基于 yt-dlp 项目的真实实现分析，展示了如何逆向还原各平台的视频获取逻辑。

### B 某站 WBI 签名机制

B 某站使用 **WBI (Web 接口签名)** 机制保护其 API 接口。

#### WBI 密钥获取与签名

```python
class BiliBaseIE:
    _WBI_KEY_CACHE_TIMEOUT = 30  # 密钥缓存 30 秒

    def _get_wbi_key(self, video_id):
        """从 nav 接口获取 WBI 签名密钥"""
        if time.time() < self._wbi_key_cache.get('ts', 0) + self._WBI_KEY_CACHE_TIMEOUT:
            return self._wbi_key_cache['key']

        # 获取 img_url 和 sub_url 中的文件名
        session_data = self._download_json(
            'https://api.example.com/x/web-interface/nav', video_id,
            note='Downloading wbi sign')

        lookup = ''.join(traverse_obj(session_data, (
            'data', 'wbi_img', ('img_url', 'sub_url'),
            {lambda x: x.rpartition('/')[2].partition('.')[0]})))

        # getMixinKey() 的置换表 - 从 B某站 前端 JS 逆向得到
        mixin_key_enc_tab = [
            46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35,
            27, 43, 5, 49, 33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13,
            37, 48, 7, 16, 24, 55, 40, 61, 26, 17, 0, 1, 60, 51, 30, 4,
            22, 25, 54, 21, 56, 59, 6, 63, 57, 62, 11, 36, 20, 34, 44, 52,
        ]

        # 通过置换表生成最终密钥
        self._wbi_key_cache.update({
            'key': ''.join(lookup[i] for i in mixin_key_enc_tab)[:32],
            'ts': time.time(),
        })
        return self._wbi_key_cache['key']

    def _sign_wbi(self, params, video_id):
        """对请求参数进行 WBI 签名"""
        params['wts'] = round(time.time())
        # 过滤特殊字符
        params = {
            k: ''.join(filter(lambda char: char not in "!'()*", str(v)))
            for k, v in sorted(params.items())
        }
        query = urllib.parse.urlencode(params)
        # 计算 w_rid = md5(query + wbi_key)
        params['w_rid'] = hashlib.md5(
            f'{query}{self._get_wbi_key(video_id)}'.encode()
        ).hexdigest()
        return params
```

#### 视频格式提取

```python
def extract_formats(self, play_info):
    """从 playurl 接口提取视频格式"""
    formats = []

    # 提取音频轨道 (DASH)
    audios = traverse_obj(play_info, ('dash', (None, 'dolby'), 'audio', ...))
    flac_audio = traverse_obj(play_info, ('dash', 'flac', 'audio'))
    if flac_audio:
        audios.append(flac_audio)

    for audio in audios:
        formats.append({
            'url': traverse_obj(audio, 'baseUrl', 'base_url', 'url'),
            'acodec': traverse_obj(audio, ('codecs', {str.lower})),
            'vcodec': 'none',
            'tbr': float_or_none(audio.get('bandwidth'), scale=1000),
        })

    # 提取视频轨道 (DASH)
    for video in traverse_obj(play_info, ('dash', 'video', ...)):
        formats.append({
            'url': traverse_obj(video, 'baseUrl', 'base_url', 'url'),
            'fps': float_or_none(traverse_obj(video, 'frameRate', 'frame_rate')),
            'width': int_or_none(video.get('width')),
            'height': int_or_none(video.get('height')),
            'vcodec': video.get('codecs'),
            'acodec': 'none',
            'dynamic_range': {126: 'DV', 125: 'HDR10'}.get(video.get('id')),
        })

    return formats
```

---

### 某奇艺 SDK 签名算法

某奇艺使用复杂的 **SDK** 进行请求签名，其核心是多轮 MD5 变换。

#### SDK 解释器实现

```python
class VideoSDK:
    def __init__(self, target, ip, timestamp):
        self.target = target
        self.ip = ip
        self.timestamp = timestamp

    @staticmethod
    def split_sum(data):
        """将十六进制字符串每个字符转为整数求和"""
        return str(sum(int(p, 16) for p in data))

    @staticmethod
    def digit_sum(num):
        """计算数字各位之和"""
        return str(sum(map(int, str(num))))

    def even_odd(self):
        """分离时间戳的奇偶位"""
        even = self.digit_sum(str(self.timestamp)[::2])
        odd = self.digit_sum(str(self.timestamp)[1::2])
        return even, odd

    def mod(self, modulus):
        """对 IP 地址取模并拼接"""
        self.target = hashlib.md5(self.target.encode()).hexdigest()
        chunks = [self.target[i*32:(i+1)*32] for i in range(1)]
        ip = list(map(int, self.ip.split('.')))
        self.target = chunks[0] + ''.join(str(p % modulus) for p in ip)

    def split(self, chunksize):
        """按块大小分割并与 IP 混合"""
        modulus_map = {4: 256, 5: 10, 8: 100}
        self.target = hashlib.md5(self.target.encode()).hexdigest()
        chunks = [self.target[i*chunksize:(i+1)*chunksize]
                  for i in range(32 // chunksize)]
        ip = list(map(int, self.ip.split('.')))
        ret = ''
        for i, chunk in enumerate(chunks):
            ip_part = str(ip[i] % modulus_map[chunksize]) if i < 4 else ''
            ret += (ip_part + chunk) if chunksize == 8 else (chunk + ip_part)
        self.target = ret

    def handle_input16(self):
        """16 字节分割处理"""
        self.target = hashlib.md5(self.target.encode()).hexdigest()
        self.target = (self.split_sum(self.target[:16]) +
                       self.target +
                       self.split_sum(self.target[16:]))

    def date(self, scheme):
        """日期混合 (y/m/d 组合)"""
        self.target = hashlib.md5(self.target.encode()).hexdigest()
        d = time.localtime(self.timestamp)
        strings = {'y': str(d.tm_year), 'm': f'{d.tm_mon:02d}', 'd': f'{d.tm_mday:02d}'}
        self.target += ''.join(strings[c] for c in scheme)


class VideoSDKInterpreter:
    """动态解释执行从服务器获取的 SDK 代码"""
    def __init__(self, sdk_code):
        self.sdk_code = sdk_code

    def run(self, target, ip, timestamp):
        # 解码混淆的 JS 代码
        self.sdk_code = decode_packed_codes(self.sdk_code)
        # 提取函数调用序列
        functions = re.findall(r'input=([a-zA-Z0-9]+)\(input', self.sdk_code)

        sdk = VideoSDK(target, ip, timestamp)

        for function in functions:
            if re.match(r'mod\d+', function):
                sdk.mod(int(function[3:]))
            elif re.match(r'date[ymd]{3}', function):
                sdk.date(function[4:])
            elif re.match(r'split\d+', function):
                sdk.split(int(function[5:]))
            # ... 其他函数映射

        return sdk.target
```

#### 登录与密钥获取

```python
def get_raw_data(self, tvid, video_id):
    """获取视频播放数据"""
    tm = int(time.time() * 1000)
    key = 'd5fb4bd9d50c4be6948c97edd7254***'  # 硬编码密钥
    sc = hashlib.md5((str(tm) + key + tvid).encode()).hexdigest()

    params = {
        'tvid': tvid,
        'vid': video_id,
        'src': '76f90cbd92f94a2e925d83e8ccd22***',
        'sc': sc,
        't': tm,
    }
    return self._download_json(api_url, video_id, query=params)
```

---

### 某讯视频 cKey 加密

某讯视频使用 **AES-CBC** 加密生成 cKey 参数。

#### cKey 生成算法

```python
from aes import aes_cbc_encrypt_bytes

class TencentBaseIE:
    _APP_VERSION = '3.5.57'
    _PLATFORM = '10901'

    def _get_ckey(self, video_id, url, guid):
        """生成 cKey 加密参数"""
        ua = self.get_param('http_headers')['User-Agent']

        # 构造 payload: vid|timestamp|magic|version|guid|platform|url|ua||Mozilla|...
        payload = (
            f'{video_id}|{int(time.time())}|mg3c3b04ba|{self._APP_VERSION}|'
            f'{guid}|{self._PLATFORM}|{url[:48]}|{ua.lower()[:48]}||Mozilla|'
            f'Netscape|Windows x86_64|00|'
        )

        # AES-CBC 加密
        # Key: Ok\xda\xa3\x9e/\x8c\xb0\x7f^r-\x9e\xde\x**\x**
        # IV:  \x01PJ\xf3V\xe6\x19\xcf.B\xbb\xa6\x**?**\x**
        encrypted = aes_cbc_encrypt_bytes(
            bytes(f'|{sum(map(ord, payload))}|{payload}', 'utf-8'),
            b'Ok\xda\xa3\x9e/\x8c\xb0\x7f^r-\x9e\xde\x**\x**',
            b'\x01PJ\xf3V\xe6\x19\xcf.B\xbb\xa6\x**?**\x**',
            padding_mode='whitespace'
        )
        return encrypted.hex().upper()

    def _get_video_api_response(self, video_url, video_id, series_id, ...):
        """请求视频 API"""
        guid = ''.join(random.choices(string.digits + string.ascii_lowercase, k=16))
        ckey = self._get_ckey(video_id, video_url, guid)

        query = {
            'vid': video_id,
            'cid': series_id,
            'cKey': ckey,
            'encryptVer': '8.1',
            'sphls': '2',        # HLS 格式
            'dtype': '3',
            'defn': video_quality,
            'sphttps': '1',      # 启用 HTTPS
            'hevclv': '28',      # 启用 HEVC
            'drm': '40',         # DRM 标识
            'guid': guid,
            'flowid': ''.join(random.choices(string.ascii_lowercase + string.digits, k=32)),
        }
        return self._download_json(self._API_URL, video_id, query=query)
```

---

### 某酷 CNA 设备标识

某酷使用 **CNA (Client Network Address)** 作为设备标识。

```python
class VideoIE:
    @staticmethod
    def get_ysuid():
        """生成会话 ID"""
        return f'{int(time.time())}{"".join(random.choices(string.ascii_letters, k=3))}'

    def _real_extract(self, url):
        video_id = self._match_id(url)

        # 设置必要的 Cookie
        self._set_cookie('example.com', '__ysuid', self.get_ysuid())
        self._set_cookie('example.com', 'xreferrer', 'http://www.example.com')

        # 从 mmstat.com 获取 CNA (通过 ETag 头)
        _, urlh = self._download_webpage_handle(
            'https://log.mmstat.com/eg.js', video_id, 'Retrieving cna info')
        cna = urlh.headers['etag'][1:-1]  # 去除双引号

        # 构造 API 请求参数
        params = {
            'vid': video_id,
            'ccode': '0564',
            'client_ip': '192.168.1.1',
            'utid': cna,                   # CNA 作为 utid
            'client_ts': time.time() / 1000,
        }

        data = self._download_json(
            'https://ups.example.com/ups/get.json', video_id,
            query=params, headers={'Referer': url})['data']

        # 提取 m3u8 格式
        formats = [{
            'url': stream['m3u8_url'],
            'format_id': self.get_format_name(stream.get('stream_type')),
            'ext': 'mp4',
            'protocol': 'm3u8_native',
            'width': stream.get('width'),
            'height': stream.get('height'),
        } for stream in data['stream']]

        return {'id': video_id, 'formats': formats, ...}
```

---

### 某果 TV tk2 令牌

某果 TV 使用 **Base64 编码的设备信息** 作为令牌。

```python
class MGTVIE:
    def _real_extract(self, url):
        video_id = self._match_id(url)

        # 生成 tk2 令牌: Base64(did=uuid|pno=1030|ver=0.3.0301|clit=timestamp)
        tk2 = base64.urlsafe_b64encode(
            f'did={uuid.uuid4()}|pno=1030|ver=0.3.0301|clit={int(time.time())}'.encode()
        )[::-1]  # 反转字节序

        # 第一步: 获取 pm2 令牌
        api_data = self._download_json(
            'https://pcweb.api.example.com/player/video', video_id,
            query={'tk2': tk2, 'video_id': video_id, 'type': 'pch5'})['data']

        # 第二步: 使用 pm2 获取流地址
        stream_data = self._download_json(
            'https://pcweb.api.example.com/player/getSource', video_id,
            query={
                'tk2': tk2,
                'pm2': api_data['atc']['pm2'],  # 第一步获取的令牌
                'video_id': video_id,
                'type': 'pch5',
                'src': 'intelmgtv',
            })['data']

        # 提取 HLS 流
        stream_domain = traverse_obj(stream_data, ('stream_domain', ...), get_all=False)
        formats = []
        for stream in traverse_obj(stream_data, ('stream', lambda _, v: v['url'])):
            format_info = self._download_json(
                urljoin(stream_domain, stream['url']), video_id)
            formats.append({
                'url': format_info['info'],
                'ext': 'mp4',
                'protocol': 'm3u8_native',
            })
        return {'id': video_id, 'formats': formats}
```

---

### 某管 Innertube 客户端体系

某管使用 **Innertube API** 与多种客户端类型进行通信。

#### 客户端配置

```python
INNERTUBE_CLIENTS = {
    'web': {
        'INNERTUBE_CONTEXT': {
            'client': {
                'clientName': 'WEB',
                'clientVersion': '2.20250312.04.00',
            },
        },
        'INNERTUBE_CONTEXT_CLIENT_NAME': 1,
        'PO_TOKEN_REQUIRED_CONTEXTS': ['gvs'],  # 需要 PoToken
        'SUPPORTS_COOKIES': True,
    },
    'android': {
        'INNERTUBE_CONTEXT': {
            'client': {
                'clientName': 'ANDROID',
                'clientVersion': '20.10.38',
                'androidSdkVersion': 30,
                'userAgent': 'com.google.android.youtube/20.10.38 (Linux; U; Android 11) gzip',
                'osName': 'Android',
                'osVersion': '11',
            },
        },
        'INNERTUBE_CONTEXT_CLIENT_NAME': 3,
        'REQUIRE_JS_PLAYER': False,
    },
    'ios': {
        'INNERTUBE_CONTEXT': {
            'client': {
                'clientName': 'IOS',
                'clientVersion': '20.10.4',
                'deviceMake': 'Apple',
                'deviceModel': 'iPhone16,2',
                'userAgent': 'com.google.ios.youtube/20.10.4 (iPhone16,2; U; CPU iOS 18_3_2 like Mac OS X;)',
            },
        },
        'INNERTUBE_CONTEXT_CLIENT_NAME': 5,
    },
    'tv': {
        'INNERTUBE_CONTEXT': {
            'client': {
                'clientName': 'TVHTML5',
                'clientVersion': '7.20250312.16.00',
                'userAgent': 'Mozilla/5.0 (ChromiumStylePlatform) Cobalt/Version',
            },
        },
        'INNERTUBE_CONTEXT_CLIENT_NAME': 7,
    },
}
```

#### 签名解密机制

某管对视频 URL 使用 **动态 JavaScript 签名** 保护：

```python
from jsinterp import JSInterpreter

class VideoTubeIE:
    _PLAYER_INFO_RE = (
        r'/s/player/(?P<id>[a-zA-Z0-9_-]{8,})/(?:tv-)?player',
        r'/(?P<id>[a-zA-Z0-9_-]{8,})/player.*?/base\.js$',
    )

    def _decrypt_signature(self, s, video_id, player_url):
        """
        解密签名的核心流程:
        1. 下载并缓存 player.js
        2. 使用 JSInterpreter 解析混淆的 JS
        3. 找到签名解密函数并执行
        """
        # 获取 player.js 代码
        player_code = self._download_webpage(player_url, video_id)

        # 使用 JS 解释器解析并执行解密函数
        jsi = JSInterpreter(player_code)

        # 在 player.js 中搜索解密函数入口
        # 函数名是动态混淆的，需要通过特征匹配
        func_name = self._search_regex(
            r'\.get\("n"\)\)&&\(b=([a-zA-Z0-9$]+)(?:\[\d+\])?\([a-zA-Z0-9]\)',
            player_code, 'Initial JS player n function name')

        decrypted = jsi.call_function(func_name, s)
        return decrypted
```

---

## 视频平台逆向要点对比

| 平台     | 签名机制             | 加密方式          | 设备标识        | 难度 |
| -------- | -------------------- | ----------------- | --------------- | ---- |
| B 某站   | WBI (md5 + 置换表)   | 无                | SESSDATA Cookie | 中   |
| 某奇艺   | SDK (多轮 md5)       | RSA 登录          | IP + 时间戳     | 高   |
| 某讯视频 | cKey (AES-CBC)       | DRM 可选          | GUID            | 高   |
| 某酷     | CNA (ETag)           | 无                | utid/ysuid      | 低   |
| 某果 TV  | tk2 (Base64)         | 无                | UUID            | 低   |
| 某管     | Innertube + JS 签名  | DRM 可选          | PoToken         | 高   |
| 某果音乐 | JWT + mediaUserToken | Widevine (HLS)    | 设备证书        | 高   |
| 某破天   | TOTP + ClientToken   | Widevine/PlayPlay | sp_dc + JA3     | 高   |

---

## 通用逆向策略

### 1. 网络层分析

```python
# 抓包分析要点
1. 识别视频清单接口 (*.m3u8, *.mpd, getSource, playurl 等)
2. 分析请求头中的签名参数 (sign, ckey, token 等)
3. 追踪 Cookie 和 Session 机制
4. 识别设备指纹参数 (guid, utid, deviceId 等)
```

### 2. 前端 JS 逆向

```python
# 常见混淆手段及应对
1. 变量名混淆 → 根据上下文推断功能
2. 字符串加密 → 找到解密函数，动态执行
3. 控制流平坦化 → 使用 AST 还原
4. 代码压缩 → 使用 beautifier 格式化
```

### 3. 设备模拟

```python
# 模拟客户端请求
headers = {
    'User-Agent': 'com.example.app/1.0.0 (Linux; Android 11)',
    'X-Client-Info': json.dumps({
        'platform': 'android',
        'version': '1.0.0',
        'device_id': generate_device_id(),
    })
}
```

---

## 总结

视频 App 的 DRM 逆向是一场与硬件和复杂密码学协议的艰苦斗争。与音乐 App 不同，其核心目标通常不是开发一个"下载器"，而是理解其安全体系的强度和弱点。

- 对于普通分析，重点是**拦截和理解信令**（清单文件、许可证请求/响应）。

- 对于高级研究，核心是**攻击 L3 的 CDM 实现**，但这需要极高的逆向工程和密码学知识。

这个领域的攻防水平代表了整个行业安全对抗的顶峰。

通过分析 yt-dlp 项目的实现，我们可以看到：

1. **签名算法多样性**: 从简单的 MD5 到复杂的多轮变换，各平台都有独特的保护机制
2. **客户端模拟的重要性**: 正确的 User-Agent 和设备标识是成功请求的关键
3. **动态代码执行**: 许多平台使用动态生成的混淆代码，需要 JS 解释器来处理
4. **Token 时效性**: 大多数签名包含时间戳，需要实时计算而非缓存
