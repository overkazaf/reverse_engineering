# 音乐 App 案例

> **📚 前置知识**
>
> 本案例涉及以下核心技术，建议先阅读相关章节：
>
> - **[静态分析深入](../01-Recipes/Analysis/static_analysis_deep_dive.md)** - 使用 Jadx 定位 VIP 判断逻辑
> - **[Ghidra/IDA 指南](../02-Tools/Static/ghidra_guide.md)** - 分析 Native 层音频解密算法

音乐类 App 是非常典型的逆向分析目标。其核心场景通常围绕着 VIP 会员特权、音频数据加密和客户端风控策略。本案例将模拟对一个典型音乐 App 的分析过程。

## 核心分析目标

1. **解锁 VIP 功能**: 免费收听付费歌曲、下载无损音质、去除广告、使用专属皮肤等。
2. **音频数据提取**: 分析加密的音频文件格式（如 `ncm`, `qmcflac`），提取出可播放的 `mp3` 或 `flac` 文件。
3. **API 分析**: 分析其歌曲搜索、歌单获取、评论区等 API，为第三方工具或爬虫提供支持。

---

## 案例：分析 VIP 歌曲的播放流程

### 第 1 步：定位切入点

**目标**: 找到判断用户是否为 VIP 以及歌曲是否为付费歌曲的关键代码。

1. **界面分析**: 在 App 中播放一首需要 VIP 的歌曲，通常会弹出一个"开通 VIP"的提示框。这个提示框是绝佳的切入点。
2. **寻找关键词**: 使用 `jadx-gui` 反编译 APK，搜索与弹窗内容相关的字符串，例如"仅限 VIP"、"开通会员"等。
3. **交叉引用**: 对找到的字符串进行交叉引用，定位到显示这个弹窗的代码。你很可能会找到一个类似 `showVipDialog()` 的方法。
4. **回溯调用栈**: 继续对 `showVipDialog()` 进行交叉引用，向上回溯。通常，你会找到一个包含了核心判断逻辑的函数，其伪代码可能如下：

```java
void onPlayButtonClick(Song song) {
// isVip() determines from user information
// song.isPaywalled() determines from song information
if (!isVip() && song.isPaywalled()) {
showVipDialog();
return;
}
// ...execute playback logic...
startPlayback(song);
}

```

**目标**: 绕过 VIP 判断，让 App 认为我们是 VIP 用户。

最直接的方法是 Hook 负责判断用户身份的函数。

```javascript
Java.perform(function () {
  // Assume UserInfo class manages user information
  var UserInfo = Java.use("com.example.music.model.UserInfo");

  // Directly hook isVip method to always return true
  UserInfo.isVip.implementation = function () {
    console.log("Bypassing VIP check, returning true.");
    return true;
  };

  // Some apps may also verify VIP expiration time
  UserInfo.getVipExpireTime.implementation = function () {
    // Return a timestamp far in the future
    return new Date(2099, 11, 31).getTime();
  };
});
```

- 请求的 URL 中带有 `quality=flac` 或 `hires` 等参数。

- 服务器返回的响应 `Content-Type` 可能不是 `audio/mpeg`，而是一些自定义的类型如 `application/octet-stream`。

- 下载下来的文件（例如，`song.ncm`）无法用标准播放器播放。

2. **定位解密代码**: 这是最关键的一步。数据解密逻辑通常在 Native 层（`.so` 文件）以提高性能和逆向难度。

- **关键词搜索**: 在 IDA Pro 或 Ghidra 中打开相关的 `.so` 文件，搜索 `aes`, `cbc`, `decrypt`, `RC4` 等加密算法相关的字符串。

- **JNI 入口**: 从 Java 层调用 Native 代码需要通过 JNI (Java Native Interface)。在 Java 代码中寻找 `native` 关键字声明的函数，例如 `private native byte[] decryptAudio(byte[] encryptedData, int core);`。这个函数名就是你在 `.so` 文件中要找的符号。

- **Hook Native 函数**: 一旦定位到 JNI 函数（如 `Java_com_example_music_player_NativeDecoder_decryptAudio`），就可以使用 Frida 进行 Hook，观察其输入和输出。

```javascript
Interceptor.attach(
  Module.findExportByName(
    "libaudiodecrypt.so",
    "Java_com_example_music_player_NativeDecoder_decryptAudio"
  ),
  {
    onEnter: function (args) {
      // args[0] is JNIEnv*, args[1] is jclass, args[2] is encrypted data jbyteArray
      console.log("Entering decryptAudio...");
      // Can save encrypted data for subsequent offline analysis
      this.encryptedBuffer = args[2];
    },
    onLeave: function (retval) {
      // retval is the decrypted jbyteArray
      console.log("Leaving decryptAudio. Decrypted data pointer: " + retval);
      // Here you can read the memory pointed to by retval to get the decrypted PCM or MP3 data
    },
  }
);
```

通过动态分析，你已经能够获取到解密后的音频数据。但如果想开发一个独立的、离线的格式转换工具，就需要彻底理解其加密方案。

- **静态分析 Native 代码**: 在 Ghidra/IDA 中仔细分析 `decryptAudio` 函数的逻辑。它可能包含：
- **元数据解析**: 从加密文件头部读取歌曲 ID、专辑封面、比特率等信息。

- **密钥派生**: 使用一个固定的 Core Key 和从文件元数据中提取的 Nonce 来派生出每个文件唯一的 AES Key。

- **解密循环**: 循环读取加密的音频帧，使用 AES 或其他算法进行解密。
- **代码实现**: 使用 Python 的 `cryptography` 等库，将你在 Native 代码中看到的逻辑重新实现一遍。最终，你就能开发出一个可以将 `.ncm` 批量转换为 `.flac` 的工具。

---

## 主流平台加密方案实例

虽然通用的分析思路是一致的，但不同平台的具体实现细节各不相同。了解这些特征有助于更快地定位问题。

### 网某云音乐 (`.ncm`)

- **文件格式**: `.ncm`

- **加密细节**: 采用 **AES + RC4** 的混合加密方案。

1. **元数据 (Meta)**: 文件中包含一块加密的元数据区域，其中含有歌曲名、专辑封面、AES Key 等信息。这块区域本身使用一个固定的 Meta Key 进行 AES-ECB 解密。
2. **音频数据 (Audio)**: 音频帧数据使用 AES-ECB 加密。解密所需的 AES Key 就存在于上一步解密后的元数据中。然而，最终的解密密钥流是通过一个类似 RC4-KSA 的算法，基于这个 AES Key 生成的。

- **逆向切入点**:
- 在 SO 库中搜索字符串 `ncm`, `core`, `meta`, `AES`, `RC4`。

- 其解密逻辑通常被封装在一个或多个专门的 Native 函数中。

### Q某音乐 (`.qmcflac`, `.mflac`, `.qmc0`)

- **文件格式**: `.qmcflac`, `.qmc0`, `.qmc3`, `.mflac` 等。

- **加密细节**: **未使用标准加密算法**，而是一套自定义的字节**置乱 (Scramble)** 方案。
- 其核心是依赖一个巨大的**静态映射表 (Seed Map)**，这个表硬编码在 SO 文件中。

- 解密时，根据当前字节在文件中的偏移量，通过一个复杂的公式计算出在映射表中的索引，然后取出表中的值与加密字节进行运算（通常是异或）。
- **逆向切入点**:
- 由于没有使用标准算法，搜索加密关键词是无效的。

- 逆向的关键是在 SO 文件中**找到那个巨大的静态数组（映射表）**。

- 定位一个紧凑的循环，该循环体内部包含了复杂的偏移量计算和查表操作。

### 某狗音乐 (`.kgm`, `.vpr`)

- **文件格式**: `.kgm`, `.vpr`。

- **加密细节**: 同样是**自定义的置乱算法**，与 Q某音乐思路相似，但实现不同。
- 依赖多个静态表（通常在开源项目中被称为 `table1`, `table2`）。

- 文件头包含了解密所需的关键信息，如密钥长度等。解密密钥由文件头信息和静态表共同派生。
- **逆向切入点**:
- 分析文件头的解析逻辑。

- 定位多个静态表，并还原其查表和密钥生成的算法。

### 某我音乐 (`.kwm`)

- **文件格式**: `.kwm`。

- **加密细节**: 采用相对简单的 **XOR 异或加密**。
- 解密密钥由一个**硬编码在 SO 中的静态密钥 (Base Key)** 与该歌曲的**资源 ID (`rid`)** 进行运算后得出。`rid` 是一个 uin64_t 类型的数字。

- 得到最终密钥后，对加密的音频数据进行逐字节异或即可完成解密。
- **逆向切入点**:
- 搜索关键词 `rid`, `kwm`。

- 定位一个逻辑相对简单的函数，其包含了获取 `rid`、与静态密钥进行运算、然后循环异或的过程。

---

## API 签名与加密实战

以下是基于真实项目的 API 加密实现分析，展示了如何逆向还原各平台的请求签名逻辑。

### 网某云音乐 API 加密实现

网某云音乐采用 **AES + RSA** 双层加密方案，Web 端和 App 端使用不同的加密策略。

#### 核心密钥常量

```python
class Music163:
    def __init__(self):
        # Web 端 AES 密钥和 IV
        self.aes_key = '0CoJUm6Qyw8W****'
        self.aes_iv = '01020304050***08'

        # RSA 公钥参数
        self.rsa_exponent = '010001'
        self.rsa_modulus = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22****'

        # 随机字符集，用于生成随机密钥
        self.words = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
```

#### Web 端加密流程 (params + encSecKey)

```python
def aes(self, data, key, iv):
    """AES-CBC 加密，PKCS7 填充"""
    bs = AES.block_size
    pkcs7 = lambda t: t + (bs - len(t) % bs) * chr(bs - len(t) % bs)
    cryptor = AES.new(key, AES.MODE_CBC, iv)
    encrypt_text = cryptor.encrypt(str.encode(pkcs7(data)))
    return str(base64.encodebytes(encrypt_text), encoding='utf-8').strip()

def rsa(self, data, exponent, modulus):
    """RSA 加密（无填充，反向字节序）"""
    res = int(codecs.encode(data[::-1].encode('utf-8'), 'hex_codec'), 16) ** int(exponent, 16) % int(modulus, 16)
    return format(res, 'x').zfill(256)

def get_formdata(self, data):
    """生成 Web 端请求参数"""
    # 1. 生成 16 位随机密钥
    random_key = ''.join([random.choice(self.words) for _ in range(16)])

    # 2. 两次 AES 加密：先用固定 key，再用随机 key
    params = self.aes(self.aes(data, self.aes_key, self.aes_iv), random_key, self.aes_iv)

    # 3. RSA 加密随机密钥
    seckey = self.rsa(random_key, self.rsa_exponent, self.rsa_modulus)

    return {"params": params, "encSecKey": seckey}
```

#### App 端 eapi 接口加密

```python
def md5_app_sign(self, path, data):
    """App 端签名算法"""
    string = "nobody" + path + "use" + data + "md5for******"
    return hashlib.new("md5", string.encode()).hexdigest()

def encrypt_app_params(self, path, data):
    """App 端参数加密"""
    sign = self.md5_app_sign(path, data)
    # 使用固定分隔符拼接
    string = str.encode(path + "-36cd479****-" + data + "-36cd479****-" + sign)
    # PKCS7 填充
    string = string + (chr((16 - (len(string) % 16))).encode() * (16 - (len(string) % 16)))
    # AES-ECB 加密
    encryptor = AES.new(b"e82ckenh8dic****", AES.MODE_ECB)
    ciphertext = encryptor.encrypt(string)
    return binascii.b2a_hex(ciphertext).upper()

def decrypt_app_data(self, data):
    """App 端响应解密"""
    encryptor = AES.new(b"e82ckenh8dic****", AES.MODE_ECB)
    data = encryptor.decrypt(data).decode()
    return data[:data.rfind("}") + 1]
```

#### 设备指纹 Cookie 构造

```python
def get_app_cookie(self, device):
    """构造 App 端设备指纹 Cookie"""
    cookies = {
        "EVNSM": "1.0.0",
        "osver": device.get("os_version"),        # 系统版本
        "deviceId": device.get("device_id"),       # 设备 ID
        "appver": "9.1.0",                         # App 版本
        "NMDI": device.get("nmdi"),                # 网易设备标识
        "NMCID": device.get("cid"),                # 渠道 ID
        "versioncode": "9001000",
        "mobilename": device.get("model").replace(" ", ""),  # 手机型号
        "resolution": device.get("resolution"),    # 分辨率
        "os": "android",
        "channel": "ali"                           # 渠道来源
    }

    if "music_a" in device:
        cookies["MUSIC_A"] = device.get("music_a")  # 登录凭证
    if "nmtid" in device:
        cookies["NMTID"] = device.get("nmtid")      # 跟踪 ID
    if "csrf" in device:
        cookies["__csrf"] = device.get("csrf")       # CSRF Token

    return "; ".join([f"{k}={v}" for k, v in cookies.items()])
```

#### 实际请求示例

```python
def search(self, keyword, offset):
    """歌手搜索 API 调用示例"""
    # 1. 构造请求数据
    data = json.dumps({
        "sub": "false",
        "s": keyword,
        "q_scene": "normal",
        "offset": str(offset),
        "queryCorrect": "true",
        "checkToken": self.random_check_token(),  # 随机校验 Token
        "limit": "100",
        "header": "{}",
        "e_r": "true"
    }, ensure_ascii=False)

    # 2. 加密参数
    url = "https://interface.music.163.com/eapi/v1/search/artist/get"
    encrypted = self.encrypt_app_params("/api/v1/search/artist/get", data)

    # 3. 发送请求
    headers = self.get_app_headers()
    res = requests.post(url, data=f"params={encrypted.decode()}", headers=headers)

    # 4. 解密响应
    return json.loads(self.decrypt_app_data(res.content))
```

---

### 全某 K 歌/某狗音乐音频解密

全某 K 歌使用 `.tkm` 格式存储加密音频，解密算法基于预计算的异或表。

#### 异或映射表生成

```python
# 核心 Seed 映射表（256 字节）
SEED_MAP = [
    0x77, 0x48, 0x32, 0x73, 0xDE, 0xF2, 0xC0, 0xC8, 0x95,
    0xEC, 0x30, 0xB2, 0x51, 0xC3, 0xE1, 0xA0, 0x9E, 0xE6,
    0x9D, 0xCF, 0xFA, 0x7F, 0x14, 0xD1, 0xCE, 0xB8, 0xDC,
    # ... 共 256 个字节
    0x4A, 0x11
]

class Mask:
    """生成解密掩码序列"""
    def __init__(self):
        self.index = 0

    def next(self):
        """计算下一个掩码字节"""
        v11 = self.index
        if v11 >= 0x8000:
            v11 %= 0x7FFF

        # 核心算法：平方加常数取模后查表
        result = SEED_MAP[(v11 * v11 + 80923) % 256]
        self.index += 1
        return result
```

#### 预计算异或文件生成

```python
def generate_xbytes_file():
    """生成约 200MB 的异或表文件（一次性生成）"""
    mask = Mask()
    with open("xbytes", "wb") as f:
        # 生成 209,771,520 字节的异或表
        # 这个大小足以覆盖大多数音频文件
        m = [mask.next() for _ in range(209771520)]
        f.write(bytes(m))
```

#### 音频解密实现

```python
import sys

class Kg:
    def __init__(self):
        self.xbytes_file = "/path/to/xbytes"  # 预计算的异或表文件

    def tkm2m4a(self, tkm_data):
        """将加密的 .tkm 文件解密为 .m4a"""
        if len(tkm_data) > 209771520:
            return None  # 文件过大，超出异或表范围

        with open(self.xbytes_file, "rb") as xbytes_file:
            xbytes = xbytes_file.read()

            # 将字节序列转换为大整数进行异或运算
            int_tkm = int.from_bytes(tkm_data, sys.byteorder)
            int_xbytes = int.from_bytes(xbytes[:len(tkm_data)], sys.byteorder)

            # 核心解密：整数异或
            m4a = (int_tkm ^ int_xbytes).to_bytes(len(tkm_data), sys.byteorder)
            return bytes(m4a)
```

#### 伴奏下载完整流程

```python
def download_accompany(self, mid):
    """下载并解密全民K歌伴奏"""
    # 1. 获取 vkey（访问凭证）
    vkey = self.get_vkey()

    # 2. 构造媒体 URL
    media_url = f"http://bsy.tsmusic.kg.qq.com/{media_mid}.tkm?vkey={vkey}&guid=1736440468&fromtag=0"

    # 3. 下载加密音频
    res = requests.get(media_url, headers=self.get_headers())
    encrypted_data = res.content

    # 4. 解密为 m4a
    decrypted = self.tkm2m4a(encrypted_data)

    # 5. 保存文件
    with open(f"{mid}.m4a", "wb") as f:
        f.write(decrypted)
```

---

### 某米音乐 API 签名

某米音乐使用 **Token + MD5** 签名机制。

```python
class XiaMi:
    def get_token_from_cookies(self, cookies):
        """从 Cookie 中提取 Token"""
        if cookies:
            token = re.findall("xm_sg_tk=(.*?)_.*?;", cookies)
            return token[0] if token else None

    def get_sign(self, key, token, query=""):
        """计算请求签名"""
        # 获取 API 路径
        path = self.get_path(self.urls.get(key))
        # 签名公式: md5(token + "_xmMain_" + path + "_" + query)
        return hashlib.md5(f"{token}_xmMain_{path}_{query}".encode()).hexdigest()

    def search_songs(self, keyword, page=1):
        """歌曲搜索示例"""
        # 1. 获取 Token 和 Cookie
        ua_token, cookies = self.get_cookies()
        token = self.get_token_from_cookies(cookies)

        # 2. 构造查询参数
        query = json.dumps({"key": keyword, "pagingVO": {"page": page, "pageSize": 30}})

        # 3. 计算签名
        sign = self.get_sign("song_search", token, query)

        # 4. 构造 URL
        q = base64.b64encode(query.encode()).decode()
        url = f"https://www.xiami.com/api/search/searchSongs?_q={q}&_s={sign}"

        # 5. 发送请求
        headers = self.get_headers(xmua=ua_token, cookies=cookies)
        return requests.get(url, headers=headers).json()
```

---

## 逆向要点总结

### 密钥提取策略

| 平台       | 加密方式   | 密钥位置                | 提取难度 |
| ---------- | ---------- | ----------------------- | -------- |
| 网某云音乐 | AES+RSA    | 硬编码在 JS/Java 代码中 | 中       |
| Q某音乐    | 静态映射表 | 硬编码在 SO 文件中      | 高       |
| 某狗音乐   | 多表异或   | SO 文件 + 服务端        | 高       |
| 某我音乐   | XOR + RID  | SO 文件中静态密钥       | 低       |
| 某米音乐   | MD5 签名   | Cookie 中的 Token       | 低       |

### 通用逆向流程

1. **抓包分析**: 使用 Charles/Fiddler 捕获 HTTPS 请求，识别加密字段
2. **定位加密点**: 在 APK 中搜索 URL 路径或参数名，定位加密函数
3. **分析算法**: 静态分析 Java/Smali 代码，动态 Hook 验证
4. **提取密钥**: 从代码或内存中提取硬编码的密钥常量
5. **复现实现**: 使用 Python 等语言还原加密逻辑
6. **绕过检测**: 处理设备指纹、请求频率等风控策略

---

## 总结

这个案例展示了从客户端功能绕过，到网络协议分析，再到核心加密算法逆向的完整流程。它结合了 Java 层的 Hook 和 Native 层的分析，是移动端逆向中非常具有代表性的场景。

通过分析真实的音乐平台爬虫项目，我们可以看到：

1. **加密复杂度差异**: 不同平台的加密强度差异明显，从简单的 MD5 签名到复杂的双层 AES+RSA
2. **音频加密特点**: 音频数据加密通常采用流式加密（XOR/RC4）以保证性能
3. **设备指纹重要性**: 现代 App 大量依赖设备指纹进行风控，需要完整模拟
4. **Native 层保护**: 核心加密逻辑往往放在 SO 文件中，增加逆向难度
