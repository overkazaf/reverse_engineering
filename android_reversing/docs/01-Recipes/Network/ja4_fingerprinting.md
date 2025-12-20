# JA4+ TLS/QUIC 指纹识别技术详解

JA4+ 是由 FoxIO (原 Salesforce 的 JA3 团队) 开发的一套网络指纹识别方法的集合，旨在成为 JA3 的下一代演进版本。它不仅仅是对 JA3 的简单升级，而是一个更全面、更具结构化和可操作性的指纹套件，旨在解决 JA3 的核心痛点，并扩展到 QUIC 和 HTTP 等协议。

---

## 目录

- [JA4+ TLS/QUIC 指纹识别技术详解](#ja4-tlsquic-指纹识别技术详解)
  - [目录](#目录)
  - [为什么需要 JA4+ (JA3 的局限性)](#为什么需要-ja4-ja3-的局限性)
  - [JA4 的核心设计 - 不再是哈希](#ja4-的核心设计---不再是哈希)
  - [JA4+ 套件概览](#ja4-套件概览)
    - [JA4 (客户端 TLS)](#ja4-客户端-tls)
    - [JA4S (服务器端 TLS)](#ja4s-服务器端-tls)
    - [JA4H (HTTP 客户端)](#ja4h-http-客户端)
    - [JA4X (TLS 证书)](#ja4x-tls-证书)
    - [JA4L (实验性)](#ja4l-实验性)
  - [JA4 vs JA3：核心优势](#ja4-vs-ja3核心优势)
  - [应用与实践](#应用与实践)

---

## 为什么需要 JA4+ (JA3 的局限性)

JA3 是一个非常成功的技术，但其核心设计——一个单一的 MD5 哈希——带来了几个无法克服的挑战：

- **缺乏上下文**: 一个 MD5 哈希是不透明的。`e7d705a3...` 和 `a8d9b1c2...` 这两个哈希值，我们无法判断它们代表的客户端有多相似。可能只是 TLS 扩展顺序的一个微小变化，就导致了完全不同的哈希。
- **"雪崩效应"**: 客户端的任何微小更新（例如，Chrome 101 -> 102）都可能导致 JA3 哈希完全改变，使得基于精确匹配的规则变得非常脆弱。
- **难以进行模糊搜索**: 无法进行"搜索所有使用 TLS 1.3 但不包含某个特定加密套件的客户端"这样的灵活查询。
- **易于被模仿**: 攻击者只需要精确复现 `Client Hello` 的特定字段，就能完全复制一个合法应用的 JA3 哈希。

JA4+ 的诞生就是为了解决这些问题。

---

## JA4 的核心设计 - 不再是哈希

JA4 最大的革新是**放弃了单一、不透明的哈希值**，转而采用一种**结构化、人类可读的字符串格式**。这使得指纹本身就携带了丰富的上下文信息。

JA4 的指纹格式为：`Protocol_Version_Ciphers_Extensions_Signature`，每个部分都有特定的含义和构造方法。

一个典型的 JA4 指纹例子：`t13d1516h2_174735a34e8a_b2149a751699`

我们来分解它：

- **`t` (Protocol)**: 协议。`t` 代表 TLS, `q` 代表 QUIC。
- **`13` (TLS Version)**: `Client Hello` 中支持的最高 TLS 版本。`12` = TLS 1.2, `13` = TLS 1.3。
- **`d1516h2` (Ciphers & Extensions Count)**:
  - `d`: 客户端支持的加密套件是有序的 (sorted)。`i` 表示无序 (insipid)。
  - `15`: 客户端提供了 15 个加密套件。
  - `16`: 客户端提供了 16 个扩展。
  - `h2`: 客户端在 `Client Hello` 中使用了 2 个 GREASE (Generate Random Extensions And Sustain Extensibility) 值，这通常是现代浏览器的特征。
- **`_` (分隔符)**
- **`174735a34e8a` (Extensions)**: 这是对**有序的**扩展列表进行特定算法计算后得到的**部分哈希**。相似的扩展列表会产生相似的哈希前缀。
- **`_` (分隔符)**
- **`b2149a751699` (Signature Algorithms)**: 这是对签名算法和支持的组（椭圆曲线）进行部分哈希计算后得到的值。

这种结构使得指纹既能用于精确匹配，也能用于强大的模糊匹配。

---

## JA4+ 套件概览

JA4+ 不是单一的工具，而是一个方法论集合。

### JA4 (客户端 TLS)

- **目标**: 识别发起 TLS 连接的客户端应用。
- **格式**: 如上所述的 `p_v_c_e_s` 结构。

### JA4S (服务器端 TLS)

- **目标**: 识别响应 TLS 连接的服务器应用。
- **格式**: `p_v_c_e`，比客户端指纹稍简单。
  - 例如：`t13d03_a06f30d07525`
  - `t` = TLS, `13` = TLS 1.3, `d` = 有序, `03` = 3 个扩展, `a06...` = 扩展的部分哈希。
- **应用**: 将 JA4 和 JA4S 结合，可以进行更精准的匹配，例如"只告警这个特定 JA4 连接到这个特定 JA4S 的行为"。

### JA4H (HTTP 客户端)

- **目标**: 对 HTTP 请求进行指纹识别，作为对 JA4 的补充。
- **格式**: `p_m_v_h`
  - `p`: 协议 (`h`=HTTP/1, `h2`=HTTP/2)。
  - `m`: 请求方法 (`g`=GET, `p`=POST)。
  - `v`: HTTP 版本。
  - `h`: 对 HTTP Header 的特定组合进行哈希。
- **应用**: 可以用来检测 JA4 欺骗。例如，一个声称自己是 Chrome 的 JA4 指纹，却发送了不符合 Chrome 行为的 JA4H 指纹，这很可能是一个恶意客户端。

### JA4X (TLS 证书)

- **目标**: 对 TLS 证书链进行指纹识别。
- **应用**: 快速识别自签名证书、特定恶意软件使用的证书等。

### JA4L (实验性)

- **L** for **L**ightweight。这是一个更简单的版本，只包含数字和计数，不包含哈希。
- **应用**: 适用于性能极高或资源受限的环境，提供基本的模糊匹配能力。

---

## JA4 vs JA3：核心优势

| 特性         | JA4+                          | JA3                |
| :----------- | :---------------------------- | :----------------- |
| **格式**     | **结构化字符串**              | 单一 MD5 哈希      |
| **可读性**   | **高**，指纹本身包含信息      | **无**             |
| **模糊匹配** | **原生支持**，可按部分查询    | 否                 |
| **上下文**   | **丰富** (协议, 版本, 计数)   | 无                 |
| **欺骗难度** | **更高**，需匹配行为逻辑      | 较低，只需匹配字段 |
| **覆盖范围** | TLS, QUIC, HTTP, Certificates | 仅 TLS             |
| **健壮性**   | **高**，微小变化不影响大局    | 低，"雪崩效应"     |

---

## 应用与实践

JA4+ 的应用场景比 JA3 更广泛和深入：

- **高级威胁狩猎**:
  - 利用结构化格式进行模糊搜索，如"查找所有 TLS 1.3 但扩展数异常少的连接"
  - 结合 JA4 + JA4S + JA4H 进行多维度关联分析
  - 检测 C2 (Command & Control) 通信的特征模式

- **Bot 检测与反爬虫**:
  - 验证声称的浏览器身份与实际 JA4H 行为是否一致
  - 检测自动化工具 (Selenium, Puppeteer) 的指纹特征
  - 识别代理工具和流量中转

- **欺骗检测**:
  - JA4 声称是 Chrome，但 JA4H 的 Header 顺序不符合 Chrome 行为
  - TLS 指纹与 HTTP 指纹不匹配的异常连接
  - 检测指纹伪造工具的使用

- **安全运营 (SOC)**:
  - 快速分类和标记未知流量
  - 建立应用基线，检测偏离正常行为的连接
  - 与 SIEM 系统集成进行实时告警

### Python 实现示例

```python
import hashlib
from typing import List, Tuple

class JA4Fingerprint:
    """JA4 指纹生成器"""

    def __init__(self):
        self.grease_values = {
            0x0a0a, 0x1a1a, 0x2a2a, 0x3a3a, 0x4a4a,
            0x5a5a, 0x6a6a, 0x7a7a, 0x8a8a, 0x9a9a,
            0xaaaa, 0xbaba, 0xcaca, 0xdada, 0xeaea, 0xfafa
        }

    def generate(self, client_hello: dict) -> str:
        """
        生成 JA4 指纹

        Args:
            client_hello: 解析后的 Client Hello 数据
                - protocol: 'tls' 或 'quic'
                - version: TLS 版本 (如 0x0303 表示 TLS 1.2)
                - ciphers: 加密套件列表
                - extensions: 扩展列表
                - signature_algorithms: 签名算法列表

        Returns:
            JA4 指纹字符串
        """
        # 1. 协议标识
        protocol = 't' if client_hello.get('protocol') == 'tls' else 'q'

        # 2. TLS 版本
        version = self._get_version_string(client_hello.get('version', 0x0303))

        # 3. 过滤 GREASE 值
        ciphers = [c for c in client_hello.get('ciphers', [])
                   if c not in self.grease_values]
        extensions = [e for e in client_hello.get('extensions', [])
                      if e not in self.grease_values]

        # 4. 排序标识
        sorted_ciphers = sorted(ciphers)
        is_sorted = 'd' if ciphers == sorted_ciphers else 'i'

        # 5. 计数
        cipher_count = f"{len(ciphers):02d}"
        ext_count = f"{len(extensions):02d}"

        # 6. GREASE 计数
        grease_count = sum(1 for c in client_hello.get('ciphers', [])
                          if c in self.grease_values)
        grease_str = f"h{grease_count}" if grease_count > 0 else ""

        # 7. 扩展哈希 (取前12位)
        ext_hash = self._hash_list(sorted(extensions))[:12]

        # 8. 签名算法哈希
        sig_algs = client_hello.get('signature_algorithms', [])
        sig_hash = self._hash_list(sig_algs)[:12]

        # 组装指纹
        prefix = f"{protocol}{version}{is_sorted}{cipher_count}{ext_count}{grease_str}"
        return f"{prefix}_{ext_hash}_{sig_hash}"

    def _get_version_string(self, version: int) -> str:
        """将 TLS 版本转换为字符串"""
        version_map = {
            0x0301: "10",  # TLS 1.0
            0x0302: "11",  # TLS 1.1
            0x0303: "12",  # TLS 1.2
            0x0304: "13",  # TLS 1.3
        }
        return version_map.get(version, "00")

    def _hash_list(self, items: List[int]) -> str:
        """对列表进行哈希"""
        data = ','.join(f"{x:04x}" for x in items)
        return hashlib.sha256(data.encode()).hexdigest()


class JA4HFingerprint:
    """JA4H (HTTP) 指纹生成器"""

    def generate(self, http_request: dict) -> str:
        """
        生成 JA4H 指纹

        Args:
            http_request: HTTP 请求数据
                - method: 请求方法 (GET, POST, etc.)
                - version: HTTP 版本 (1.1, 2, 3)
                - headers: Header 字典 (保持顺序)

        Returns:
            JA4H 指纹字符串
        """
        # 协议
        version = http_request.get('version', '1.1')
        if version == '2':
            proto = 'h2'
        elif version == '3':
            proto = 'h3'
        else:
            proto = 'h1'

        # 方法
        method = http_request.get('method', 'GET')[0].lower()

        # Header 名称列表 (小写，保持顺序)
        headers = http_request.get('headers', {})
        header_names = [k.lower() for k in headers.keys()]

        # Header 哈希
        header_hash = hashlib.sha256(','.join(header_names).encode()).hexdigest()[:12]

        # Cookie 存在标识
        has_cookie = 'c' if 'cookie' in header_names else 'n'

        # Referer 存在标识
        has_referer = 'r' if 'referer' in header_names else 'n'

        return f"{proto}{method}{has_cookie}{has_referer}_{header_hash}"


# 使用示例
if __name__ == "__main__":
    # 模拟 Chrome 的 Client Hello
    chrome_hello = {
        'protocol': 'tls',
        'version': 0x0304,  # TLS 1.3
        'ciphers': [
            0x1301, 0x1302, 0x1303,  # TLS 1.3 ciphers
            0xc02c, 0xc02b, 0xc030,  # ECDHE ciphers
        ],
        'extensions': [
            0x0000,  # server_name
            0x0017,  # extended_master_secret
            0x0023,  # session_ticket
            0x000d,  # signature_algorithms
            0x002b,  # supported_versions
            0x002d,  # psk_key_exchange_modes
            0x0033,  # key_share
        ],
        'signature_algorithms': [0x0403, 0x0503, 0x0603, 0x0804, 0x0805],
    }

    ja4 = JA4Fingerprint()
    fingerprint = ja4.generate(chrome_hello)
    print(f"JA4 Fingerprint: {fingerprint}")

    # 模拟 HTTP 请求
    http_req = {
        'method': 'GET',
        'version': '2',
        'headers': {
            'Host': 'example.com',
            'User-Agent': 'Mozilla/5.0...',
            'Accept': '*/*',
            'Accept-Language': 'en-US',
            'Cookie': 'session=abc123',
        }
    }

    ja4h = JA4HFingerprint()
    http_fp = ja4h.generate(http_req)
    print(f"JA4H Fingerprint: {http_fp}")
```

### 检测工具集成

```python
# Wireshark / tshark 提取 JA4
# 需要安装 JA4+ 插件: https://github.com/FoxIO-LLC/ja4

# 使用 tshark 提取 JA4 指纹
tshark_cmd = """
tshark -r capture.pcap -Y "tls.handshake.type == 1" \
    -T fields -e ip.src -e ja4.ja4
"""

# Zeek (Bro) 集成
zeek_script = """
@load ja4

event ssl_client_hello(c: connection, version: count, ...) {
    local ja4 = JA4::fingerprint(c);
    print fmt("JA4: %s from %s", ja4, c$id$orig_h);
}
"""
```

---

## 延伸阅读

### 相关配方

- **[JA3 指纹详解](./ja3_fingerprinting.md)** - JA3 基础知识
- **[TLS 指纹识别](./tls_fingerprinting_guide.md)** - TLS 指纹概述
- **[网络抓包](./network_sniffing.md)** - 获取 TLS 握手包

### 工具与资源

- [JA4+ 官方仓库](https://github.com/FoxIO-LLC/ja4) - 官方实现和文档
- [JA4 数据库](https://ja4db.com/) - 已知应用的 JA4 指纹库
- [Wireshark JA4 插件](https://github.com/FoxIO-LLC/ja4/tree/main/wireshark) - Wireshark 集成

### 参考文献

- [JA4+ 技术白皮书](https://blog.foxio.io/ja4%2B-network-fingerprinting) - FoxIO 官方博客
- [JA4+ 设计原理](https://engineering.salesforce.com/ja4-network-fingerprinting-9376fe9ca637) - Salesforce Engineering
