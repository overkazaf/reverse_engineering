# DEX 文件相关

DEX (Dalvik Executable) 文件是 Android 操作系统的核心组成部分之一。它们是专门为在内存和处理器速度受限的设备上高效运行而设计的。本指南将深入探讨 DEX 文件的定义、格式、运行原理以及相关工具。

!!! question "思考：理解 DEX 格式的实战价值"
很多初学者会问："DEX 格式这么复杂，我真的需要了解这些底层细节吗？"

考虑这些实际场景：

- **加固对抗**：当 App 使用了 DEX 加壳（如梆梆、360），你需要知道 DEX 的魔数、签名字段在哪，才能判断脱壳是否完整
- **动态加载分析**：很多 App 会在运行时解密并加载隐藏的 DEX，理解 `Class Defs` 结构能帮你快速定位被隐藏的恶意代码
- **Multi-DEX 定位**：当你想 Hook 某个类，但不知道它在哪个 `classes.dex` 中时，理解 String IDs 和 Type IDs 能帮你快速搜索
- **方法数优化**：理解 65536 方法数限制的根本原因（Method IDs 索引用 16 位），能帮你更好地进行模块化设计

## DEX 格式不是学术知识，而是你破解加固、分析恶意代码的**手术刀**。

## 目录

1. [**定义与角色**：什么是 DEX 文件？](#定义与角色)
2. [**DEX vs. CLASS**：与 Java 字节码的对比](#dex-vs-class)
3. [**DEX 文件结构**：深入剖析格式](#dex-文件结构)
4. [**运行原理**：DEX 文件如何被执行？](#运行原理)
5. [**Multi-DEX**：应对方法数限制](#multi-dex)
6. [**DEX 分析与处理工具**](#dex-分析与处理工具)

---

### 定义与角色

**DEX 文件**是包含了 Android 应用代码的单个可执行文件。在打包（Build）过程中，Java 编译器首先将 `.java` 源码文件编译成标准的 Java 字节码 `.class` 文件。然后，Android SDK 中的 `d8` 工具（旧版本为 `dx`）会将所有的 `.class` 文件（包括项目代码和依赖库）优化并合并成 **一个或多个** `classes.dex` 文件。

这个 `classes.dex` 文件最终被打包进 APK (Android Package) 中。当用户安装并运行应用时，Android 系统（特别是 ART）会直接执行 DEX 文件中的代码。

**核心角色**：

- **紧凑性**: 将所有类文件合并，并共享字符串和常量，大大减少了文件体积和 I/O 开销。

- **高效性**: 采用基于寄存器的指令集，更接近底层硬件，执行效率比基于栈的 JVM 更高。

- **移动优化**: 专为内存有限的移动设备设计。

## 本文档参考了 Android 官方关于 [DEX 文件格式](https://source.android.com/docs/core/dalvik/dex-format) 的说明。

### DEX vs. CLASS

| 特性           | `.class` 文件 (JVM)              | `.dex` 文件 (ART/Dalvik)                       |
| -------------- | -------------------------------- | ---------------------------------------------- |
| **文件数量**   | 每个源文件对应一个 `.class` 文件 | 所有 `.class` 文件合并成一个或多个 `.dex` 文件 |
| **指令集架构** | **基于栈 (Stack-based)**         | **基于寄存器 (Register-based)**                |
| **常量池**     | 每个文件都有自己独立的常量池     | 所有类共享一个全局的字符串和常量池             |
| **冗余信息**   | 大量冗余字符串（如类名、方法名） | 字符串和常量去重，通过索引引用，冗余少         |
| **平台**       | 任何有 JVM 的地方                | Android 平台                                   |
| **转换工具**   | `javac`                          | `javac` -> `d8`/`dx`                           |

---

### DEX 文件结构

DEX 文件格式非常紧凑和高效，其结构可以大致分为以下几个部分，并由一个 `header` 来描述整个文件的元数据和偏移量。

!!! tip "逆向技巧：从结构入手快速定位"
面对一个陌生的 DEX 文件，如何快速找到你感兴趣的代码？

**自顶向下的分析策略**：

1. **看 Header**：检查魔数确认文件完整性，查看 `class_defs_size` 了解有多少个类
2. **搜 String IDs**：用 `dexdump` 或 `strings` 搜索关键字符串（如 "encrypt", "http://"），定位可疑代码
3. **查 Method IDs**：通过方法名索引找到具体实现
4. **跳 Class Defs**：直接定位到目标类的完整定义
5. **读 Code Item**：最后才深入字节码细节

这种"线索驱动"的方法，比漫无目的地浏览代码高效得多。

<!-- ![DEX File Structure](../images/dex-format.png) -->

A DEX file consists of several main sections:

### 1. 头部 (Header)

- **Header**: 文件头，包含魔数（`dex\n035\0`）、校验和、签名，以及指向其他数据结构（如字符串、类定义等）的偏移量和大小。

- **String IDs**: 字符串标识符列表。包含 DEX 文件中用到的所有字符串（如类名、方法名、变量名、字符串常量），并为每个字符串分配一个唯一的 ID。

- **Type IDs**: 类型标识符列表。包含代码中用到的所有类型（类、接口、数组、基本类型），并指向 `String IDs` 中的相应字符串。

- **Proto IDs**: 方法原型标识符列表。定义了方法的返回类型和参数类型。

- **Field IDs**: 字段标识符列表。定义了类的成员变量，包括其所属类、类型和名称。

- **Method IDs**: 方法标识符列表。定义了方法，包括其所属类、原型 (Proto ID) 和名称。

- **Class Defs**: 类定义列表。这是核心部分，包含了每个类的详细信息：访问标志、父类、实现的接口、源码文件名、注解、以及指向其字段和方法的指针。

- **Data Section**: 数据区，包含了所有类的实际内容，例如：
- **Code Item**: 实际的方法字节码（Dalvik 指令）。

- **Class Data**: 类的字段和方法列表的具体数据。

- **Map List**: 描述整个 DEX 文件数据布局的映射表，`dexdump` 等工具使用它来解析文件。

---

### 运行原理

DEX 文件的执行由 Android 运行时 (ART) 负责，在 Android 5.0 之前由 Dalvik 虚拟机 (DVM) 负责。

#### 1. Dalvik 虚拟机 (DVM) - android 4.4 及更早版本

- **JIT (Just-In-Time) 编译**: 当应用运行时，DVM 会解释执行 DEX 字节码。对于频繁执行的"热点"代码路径，JIT 编译器会将其动态编译成本地机器码，以提高后续执行速度。

- **缺点**: 每次启动应用都需要进行解释和 JIT 编译，导致应用启动速度较慢，且运行时消耗更多计算资源。

#### 2. android 运行时 (ART) - Android 5.0 及更高版本

- **AOT (Ahead-Of-Time) 编译**: 在应用**安装时**，ART 会使用 `dex2oat` 工具将 DEX 文件中的字节码预编译成设备原生的机器码，并保存为 OAT (Optimized Android file format) 文件。

- **优点**:
- **启动速度快**: 应用直接执行预编译的本地代码，无需实时编译，大大加快了启动速度。

- **性能更高**: AOT 可以进行更深度的优化，性能通常优于 JIT。

- **更省电**: 减少了运行时的 CPU 计算负担。
- **AOT + JIT 混合模式 (Android 7.0+ )**:
- 为了平衡安装速度/空间占用和性能，ART 引入了混合模式。

- **安装时**: 不进行完全 AOT 编译，或只编译部分关键代码。

- **首次运行**: 解释执行，并使用 JIT 编译热点代码，同时收集分析信息 (Profile)。

- **设备空闲时**: 当设备充电且空闲时，系统会根据收集到的分析信息，对常用代码进行 AOT 编译，实现最佳性能。

---

### Multi-DEX

单个 DEX 文件有一个方法引用数上限（65,536 个），当应用（包括其依赖库）的方法总数超过这个限制时，编译会失败。

为了解决这个问题，Android 引入了 **Multi-DEX** 机制。打包工具会将应用代码分割到多个 DEX 文件中，例如 `classes.dex`, `classes2.dex`, `classes3.dex` 等。主 `classes.dex` 文件会优先加载，然后应用代码会负责加载其余的 DEX 文件。

## 从 Android 5.0 (API 21) 开始，ART 原生支持加载多个 DEX 文件，无需额外的库。对于更早的版本，则需要使用官方的 `multidex-support-library`。

### DEX 分析与处理工具

| 工具                 | 描述                                                                                           |
| -------------------- | ---------------------------------------------------------------------------------------------- |
| **d8 / dx**          | Google 官方工具，用于将 `.class` 文件转换为 `.dex` 文件。`d8` 是新一代的转换器。               |
| **dexdump**          | 位于 Android SDK `build-tools` 中，用于打印 DEX 文件的详细信息，包括头信息、类、方法和字节码。 |
| **baksmali**         | 将 `.dex` 文件反汇编成 `.smali` 文件。Smali 是一种人类可读的 Dalvik 字节码表示形式。           |
| **smali**            | 将 `.smali` 文件重新汇编成 `.dex` 文件。常用于修改应用逻辑后重新打包。                         |
| **Jadx**             | 非常强大的反编译工具，可以直接将 APK/DEX 文件反编译成可读的 Java 代码，并提供图形化界面。      |
| **Ghidra / IDA Pro** | 高级逆向工程工具，支持对 DEX 文件和原生库进行深度静态和动态分析。                              |

---

## DEX 文件解析实战

本节通过代码示例，深入讲解如何解析 DEX 文件的各个部分。

### DEX Header 详细结构

DEX 文件头共 112 字节（0x70），包含文件的元数据和各区域的偏移量：

```
偏移量    大小    字段名              描述
────────────────────────────────────────────────────────────────
0x00      8      magic               魔数: "dex\n035\0" 或 "dex\n039\0"
0x08      4      checksum            Adler32 校验和（从 0x0C 开始计算）
0x0C      20     signature           SHA-1 签名（从 0x20 开始计算）
0x20      4      file_size           DEX 文件总大小
0x24      4      header_size         头部大小，固定为 0x70 (112)
0x28      4      endian_tag          字节序标记: 0x12345678 (小端)
0x2C      4      link_size           链接段大小
0x30      4      link_off            链接段偏移
0x34      4      map_off             Map 段偏移
0x38      4      string_ids_size     字符串 ID 数量
0x3C      4      string_ids_off      字符串 ID 表偏移
0x40      4      type_ids_size       类型 ID 数量
0x44      4      type_ids_off        类型 ID 表偏移
0x48      4      proto_ids_size      原型 ID 数量
0x4C      4      proto_ids_off       原型 ID 表偏移
0x50      4      field_ids_size      字段 ID 数量
0x54      4      field_ids_off       字段 ID 表偏移
0x58      4      method_ids_size     方法 ID 数量
0x5C      4      method_ids_off      方法 ID 表偏移
0x60      4      class_defs_size     类定义数量
0x64      4      class_defs_off      类定义表偏移
0x68      4      data_size           数据段大小
0x6C      4      data_off            数据段偏移
```

### Python DEX 解析器

以下是一个完整的 Python DEX 解析器实现：

```python
#!/usr/bin/env python3
"""
DEX 文件解析器 - 用于分析 Android DEX 文件结构
"""

import struct
import hashlib
import zlib
from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path


@dataclass
class DexHeader:
    """DEX 文件头结构"""
    magic: bytes
    checksum: int
    signature: bytes
    file_size: int
    header_size: int
    endian_tag: int
    link_size: int
    link_off: int
    map_off: int
    string_ids_size: int
    string_ids_off: int
    type_ids_size: int
    type_ids_off: int
    proto_ids_size: int
    proto_ids_off: int
    field_ids_size: int
    field_ids_off: int
    method_ids_size: int
    method_ids_off: int
    class_defs_size: int
    class_defs_off: int
    data_size: int
    data_off: int


@dataclass
class ClassDef:
    """类定义结构"""
    class_idx: int
    access_flags: int
    superclass_idx: int
    interfaces_off: int
    source_file_idx: int
    annotations_off: int
    class_data_off: int
    static_values_off: int


@dataclass
class MethodId:
    """方法 ID 结构"""
    class_idx: int
    proto_idx: int
    name_idx: int


class DexParser:
    """DEX 文件解析器"""

    # 访问标志常量
    ACC_PUBLIC = 0x0001
    ACC_PRIVATE = 0x0002
    ACC_PROTECTED = 0x0004
    ACC_STATIC = 0x0008
    ACC_FINAL = 0x0010
    ACC_SYNCHRONIZED = 0x0020
    ACC_VOLATILE = 0x0040
    ACC_BRIDGE = 0x0040
    ACC_TRANSIENT = 0x0080
    ACC_VARARGS = 0x0080
    ACC_NATIVE = 0x0100
    ACC_INTERFACE = 0x0200
    ACC_ABSTRACT = 0x0400
    ACC_STRICT = 0x0800
    ACC_SYNTHETIC = 0x1000
    ACC_ANNOTATION = 0x2000
    ACC_ENUM = 0x4000
    ACC_CONSTRUCTOR = 0x10000
    ACC_DECLARED_SYNCHRONIZED = 0x20000

    def __init__(self, dex_path: str):
        self.dex_path = Path(dex_path)
        with open(dex_path, 'rb') as f:
            self.data = f.read()
        self.header: Optional[DexHeader] = None
        self.strings: List[str] = []
        self.types: List[str] = []
        self.class_defs: List[ClassDef] = []
        self.method_ids: List[MethodId] = []

    def parse(self) -> bool:
        """解析 DEX 文件"""
        if not self._parse_header():
            return False
        self._parse_strings()
        self._parse_types()
        self._parse_method_ids()
        self._parse_class_defs()
        return True

    def _parse_header(self) -> bool:
        """解析 DEX 头部"""
        if len(self.data) < 112:
            print("文件太小，不是有效的 DEX 文件")
            return False

        # 检查魔数
        magic = self.data[0:8]
        if not magic.startswith(b'dex\n'):
            print(f"无效的魔数: {magic}")
            return False

        # 解析头部各字段
        self.header = DexHeader(
            magic=magic,
            checksum=struct.unpack('<I', self.data[8:12])[0],
            signature=self.data[12:32],
            file_size=struct.unpack('<I', self.data[32:36])[0],
            header_size=struct.unpack('<I', self.data[36:40])[0],
            endian_tag=struct.unpack('<I', self.data[40:44])[0],
            link_size=struct.unpack('<I', self.data[44:48])[0],
            link_off=struct.unpack('<I', self.data[48:52])[0],
            map_off=struct.unpack('<I', self.data[52:56])[0],
            string_ids_size=struct.unpack('<I', self.data[56:60])[0],
            string_ids_off=struct.unpack('<I', self.data[60:64])[0],
            type_ids_size=struct.unpack('<I', self.data[64:68])[0],
            type_ids_off=struct.unpack('<I', self.data[68:72])[0],
            proto_ids_size=struct.unpack('<I', self.data[72:76])[0],
            proto_ids_off=struct.unpack('<I', self.data[76:80])[0],
            field_ids_size=struct.unpack('<I', self.data[80:84])[0],
            field_ids_off=struct.unpack('<I', self.data[84:88])[0],
            method_ids_size=struct.unpack('<I', self.data[88:92])[0],
            method_ids_off=struct.unpack('<I', self.data[92:96])[0],
            class_defs_size=struct.unpack('<I', self.data[96:100])[0],
            class_defs_off=struct.unpack('<I', self.data[100:104])[0],
            data_size=struct.unpack('<I', self.data[104:108])[0],
            data_off=struct.unpack('<I', self.data[108:112])[0],
        )
        return True

    def _read_uleb128(self, offset: int) -> tuple:
        """读取 ULEB128 编码的整数"""
        result = 0
        shift = 0
        size = 0
        while True:
            byte = self.data[offset + size]
            result |= (byte & 0x7f) << shift
            size += 1
            if (byte & 0x80) == 0:
                break
            shift += 7
        return result, size

    def _parse_strings(self):
        """解析字符串表"""
        if not self.header:
            return

        self.strings = []
        offset = self.header.string_ids_off

        for i in range(self.header.string_ids_size):
            # 读取字符串数据偏移
            string_data_off = struct.unpack('<I', self.data[offset:offset+4])[0]
            offset += 4

            # 读取 ULEB128 编码的字符串长度
            str_len, size = self._read_uleb128(string_data_off)

            # 读取 MUTF-8 编码的字符串
            str_start = string_data_off + size
            str_bytes = self.data[str_start:str_start + str_len]
            try:
                self.strings.append(str_bytes.decode('utf-8', errors='replace'))
            except:
                self.strings.append(str_bytes.hex())

    def _parse_types(self):
        """解析类型表"""
        if not self.header:
            return

        self.types = []
        offset = self.header.type_ids_off

        for i in range(self.header.type_ids_size):
            descriptor_idx = struct.unpack('<I', self.data[offset:offset+4])[0]
            offset += 4
            if descriptor_idx < len(self.strings):
                self.types.append(self.strings[descriptor_idx])
            else:
                self.types.append(f"<invalid:{descriptor_idx}>")

    def _parse_method_ids(self):
        """解析方法 ID 表"""
        if not self.header:
            return

        self.method_ids = []
        offset = self.header.method_ids_off

        for i in range(self.header.method_ids_size):
            class_idx = struct.unpack('<H', self.data[offset:offset+2])[0]
            proto_idx = struct.unpack('<H', self.data[offset+2:offset+4])[0]
            name_idx = struct.unpack('<I', self.data[offset+4:offset+8])[0]
            offset += 8

            self.method_ids.append(MethodId(class_idx, proto_idx, name_idx))

    def _parse_class_defs(self):
        """解析类定义表"""
        if not self.header:
            return

        self.class_defs = []
        offset = self.header.class_defs_off

        for i in range(self.header.class_defs_size):
            class_def = ClassDef(
                class_idx=struct.unpack('<I', self.data[offset:offset+4])[0],
                access_flags=struct.unpack('<I', self.data[offset+4:offset+8])[0],
                superclass_idx=struct.unpack('<I', self.data[offset+8:offset+12])[0],
                interfaces_off=struct.unpack('<I', self.data[offset+12:offset+16])[0],
                source_file_idx=struct.unpack('<I', self.data[offset+16:offset+20])[0],
                annotations_off=struct.unpack('<I', self.data[offset+20:offset+24])[0],
                class_data_off=struct.unpack('<I', self.data[offset+24:offset+28])[0],
                static_values_off=struct.unpack('<I', self.data[offset+28:offset+32])[0],
            )
            offset += 32
            self.class_defs.append(class_def)

    def get_access_flags_str(self, flags: int) -> str:
        """将访问标志转换为可读字符串"""
        result = []
        if flags & self.ACC_PUBLIC: result.append("public")
        if flags & self.ACC_PRIVATE: result.append("private")
        if flags & self.ACC_PROTECTED: result.append("protected")
        if flags & self.ACC_STATIC: result.append("static")
        if flags & self.ACC_FINAL: result.append("final")
        if flags & self.ACC_ABSTRACT: result.append("abstract")
        if flags & self.ACC_INTERFACE: result.append("interface")
        if flags & self.ACC_NATIVE: result.append("native")
        return " ".join(result)

    def verify_checksum(self) -> bool:
        """验证 Adler32 校验和"""
        if not self.header:
            return False
        calculated = zlib.adler32(self.data[12:]) & 0xffffffff
        return calculated == self.header.checksum

    def verify_signature(self) -> bool:
        """验证 SHA-1 签名"""
        if not self.header:
            return False
        calculated = hashlib.sha1(self.data[32:]).digest()
        return calculated == self.header.signature

    def print_header(self):
        """打印头部信息"""
        if not self.header:
            print("未解析头部")
            return

        h = self.header
        print("=" * 60)
        print("DEX 文件头信息")
        print("=" * 60)
        print(f"魔数:           {h.magic}")
        print(f"DEX 版本:       {h.magic[4:7].decode()}")
        print(f"校验和:         0x{h.checksum:08X} {'(有效)' if self.verify_checksum() else '(无效)'}")
        print(f"SHA-1 签名:     {h.signature.hex()}")
        print(f"文件大小:       {h.file_size} bytes ({h.file_size / 1024:.2f} KB)")
        print(f"头部大小:       {h.header_size} bytes")
        print(f"字节序:         {'小端' if h.endian_tag == 0x12345678 else '大端'}")
        print("-" * 60)
        print(f"字符串数量:     {h.string_ids_size}")
        print(f"类型数量:       {h.type_ids_size}")
        print(f"原型数量:       {h.proto_ids_size}")
        print(f"字段数量:       {h.field_ids_size}")
        print(f"方法数量:       {h.method_ids_size}")
        print(f"类定义数量:     {h.class_defs_size}")
        print("=" * 60)

    def print_classes(self, limit: int = 20):
        """打印类列表"""
        print(f"\n前 {limit} 个类:")
        print("-" * 60)
        for i, class_def in enumerate(self.class_defs[:limit]):
            class_name = self.types[class_def.class_idx] if class_def.class_idx < len(self.types) else "?"
            flags = self.get_access_flags_str(class_def.access_flags)
            print(f"  [{i:4d}] {flags} {class_name}")

    def search_strings(self, keyword: str) -> List[tuple]:
        """搜索包含关键字的字符串"""
        results = []
        keyword_lower = keyword.lower()
        for i, s in enumerate(self.strings):
            if keyword_lower in s.lower():
                results.append((i, s))
        return results

    def find_methods_by_name(self, name: str) -> List[tuple]:
        """按名称搜索方法"""
        results = []
        for i, method in enumerate(self.method_ids):
            method_name = self.strings[method.name_idx] if method.name_idx < len(self.strings) else ""
            if name.lower() in method_name.lower():
                class_name = self.types[method.class_idx] if method.class_idx < len(self.types) else "?"
                results.append((i, class_name, method_name))
        return results


# 使用示例
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法: python dex_parser.py <dex文件路径> [搜索关键字]")
        sys.exit(1)

    parser = DexParser(sys.argv[1])
    if not parser.parse():
        sys.exit(1)

    parser.print_header()
    parser.print_classes()

    # 如果提供了搜索关键字
    if len(sys.argv) >= 3:
        keyword = sys.argv[2]
        print(f"\n搜索字符串: '{keyword}'")
        results = parser.search_strings(keyword)
        for idx, s in results[:20]:
            print(f"  [{idx}] {s[:80]}...")

        print(f"\n搜索方法: '{keyword}'")
        methods = parser.find_methods_by_name(keyword)
        for idx, class_name, method_name in methods[:20]:
            print(f"  [{idx}] {class_name}->{method_name}")
```

### 使用示例

```bash
# 基本用法 - 解析 DEX 文件
python dex_parser.py classes.dex

# 搜索包含特定关键字的字符串和方法
python dex_parser.py classes.dex "encrypt"

# 输出示例:
# ============================================================
# DEX 文件头信息
# ============================================================
# 魔数:           b'dex\n035\x00'
# DEX 版本:       035
# 校验和:         0x8A3B2C1D (有效)
# SHA-1 签名:     a1b2c3d4e5f6...
# 文件大小:       2048576 bytes (2000.56 KB)
# 方法数量:       15234
# 类定义数量:     1523
```

---

## Frida 运行时 DEX 分析

在动态分析中，我们经常需要在运行时 dump 或分析 DEX 文件，特别是针对加固应用。

### 基础 DEX Dump 脚本

```javascript
/**
 * Frida DEX Dump 脚本
 * 用于从内存中提取已加载的 DEX 文件
 */

// DEX 魔数
const DEX_MAGIC = [0x64, 0x65, 0x78, 0x0a];  // "dex\n"

// 在内存中搜索 DEX 文件
function searchDexInMemory() {
    const results = [];

    Process.enumerateRanges('r--').forEach(function(range) {
        try {
            const pattern = '64 65 78 0a 30 33';  // dex\n03
            Memory.scan(range.base, range.size, pattern, {
                onMatch: function(address, size) {
                    console.log('[+] 发现 DEX @ ' + address);
                    results.push(address);
                },
                onError: function(reason) {},
                onComplete: function() {}
            });
        } catch (e) {}
    });

    return results;
}

// 从内存地址 dump DEX 文件
function dumpDex(address, filename) {
    try {
        // 读取 DEX 文件大小（偏移 0x20 处的 4 字节）
        const fileSize = Memory.readU32(address.add(0x20));
        console.log('[*] DEX 大小: ' + fileSize + ' bytes');

        // 读取整个 DEX 文件
        const dexData = Memory.readByteArray(address, fileSize);

        // 写入文件
        const file = new File('/data/local/tmp/' + filename, 'wb');
        file.write(dexData);
        file.close();

        console.log('[+] 已保存: /data/local/tmp/' + filename);
        return true;
    } catch (e) {
        console.log('[-] Dump 失败: ' + e);
        return false;
    }
}

// Hook ClassLoader.loadClass 监控类加载
function hookClassLoader() {
    Java.perform(function() {
        const ClassLoader = Java.use('java.lang.ClassLoader');

        ClassLoader.loadClass.overload('java.lang.String').implementation = function(name) {
            console.log('[ClassLoader] 加载类: ' + name);
            return this.loadClass(name);
        };
    });
}

// Hook DexFile 构造函数，捕获动态加载的 DEX
function hookDexFile() {
    Java.perform(function() {
        // Android 8.0+ 使用 DexPathList
        try {
            const DexPathList = Java.use('dalvik.system.DexPathList');
            const makePathElements = DexPathList.makePathElements;

            if (makePathElements) {
                makePathElements.overload(
                    'java.util.List',
                    'java.io.File',
                    'java.util.List'
                ).implementation = function(files, optimizedDirectory, suppressedExceptions) {
                    console.log('[DexPathList] 加载 DEX 文件:');
                    const iterator = files.iterator();
                    while (iterator.hasNext()) {
                        console.log('  - ' + iterator.next());
                    }
                    return makePathElements.call(this, files, optimizedDirectory, suppressedExceptions);
                };
            }
        } catch (e) {
            console.log('[-] Hook DexPathList 失败: ' + e);
        }

        // Hook InMemoryDexClassLoader (Android 8.0+)
        try {
            const InMemoryDexClassLoader = Java.use('dalvik.system.InMemoryDexClassLoader');
            InMemoryDexClassLoader.$init.overload(
                'java.nio.ByteBuffer',
                'java.lang.ClassLoader'
            ).implementation = function(dexBuffer, parent) {
                console.log('[!] 检测到内存 DEX 加载!');
                console.log('    大小: ' + dexBuffer.remaining() + ' bytes');

                // Dump 内存中的 DEX
                const size = dexBuffer.remaining();
                const dexBytes = new Uint8Array(size);
                for (let i = 0; i < size; i++) {
                    dexBytes[i] = dexBuffer.get(i);
                }

                const timestamp = Date.now();
                const filename = 'inmemory_' + timestamp + '.dex';

                // 使用 Java 写入文件
                const FileOutputStream = Java.use('java.io.FileOutputStream');
                const fos = FileOutputStream.$new('/data/local/tmp/' + filename);
                fos.write(Java.array('byte', Array.from(dexBytes)));
                fos.close();

                console.log('[+] 已 Dump: /data/local/tmp/' + filename);

                return this.$init(dexBuffer, parent);
            };
        } catch (e) {
            console.log('[-] Hook InMemoryDexClassLoader 失败: ' + e);
        }
    });
}

// 列出所有已加载的 DEX 文件
function listLoadedDex() {
    Java.perform(function() {
        Java.enumerateClassLoaders({
            onMatch: function(loader) {
                try {
                    const pathList = loader.pathList.value;
                    if (pathList) {
                        const dexElements = pathList.dexElements.value;
                        console.log('\n[ClassLoader] ' + loader.$className);
                        for (let i = 0; i < dexElements.length; i++) {
                            const element = dexElements[i];
                            const dexFile = element.dexFile.value;
                            if (dexFile) {
                                console.log('  DEX: ' + dexFile.mFileName.value);
                            }
                        }
                    }
                } catch (e) {}
            },
            onComplete: function() {}
        });
    });
}

// 主入口
console.log('[*] DEX 分析脚本已加载');
console.log('[*] 可用命令:');
console.log('    searchDex() - 搜索内存中的 DEX');
console.log('    listLoadedDex() - 列出已加载的 DEX');
console.log('    hookDexFile() - Hook DEX 加载');

// 自动执行
Java.perform(function() {
    listLoadedDex();
    hookDexFile();
});
```

### 高级: 针对加固 App 的 DEX Dump

```javascript
/**
 * 针对主流加固方案的 DEX Dump
 * 支持: 梆梆、360、爱加密、腾讯乐固等
 */

// 通用脱壳点 - Hook openDexFile
function hookOpenDexFile() {
    const artModule = Process.findModuleByName('libart.so');
    if (!artModule) {
        console.log('[-] 未找到 libart.so');
        return;
    }

    // 搜索 OpenDexFilesFromOat 或相关函数
    const symbols = artModule.enumerateSymbols();
    symbols.forEach(function(sym) {
        if (sym.name.indexOf('OpenDexFile') !== -1 &&
            sym.name.indexOf('Oat') === -1) {
            console.log('[*] 发现符号: ' + sym.name + ' @ ' + sym.address);

            Interceptor.attach(sym.address, {
                onEnter: function(args) {
                    console.log('[OpenDexFile] 调用');
                    // args[0] 通常是 DEX 数据指针
                    // args[1] 是大小
                },
                onLeave: function(retval) {
                    console.log('[OpenDexFile] 返回: ' + retval);
                }
            });
        }
    });
}

// Hook mmap，捕获 DEX 映射
function hookMmap() {
    const mmapPtr = Module.findExportByName('libc.so', 'mmap');

    Interceptor.attach(mmapPtr, {
        onEnter: function(args) {
            this.size = args[1].toInt();
        },
        onLeave: function(retval) {
            if (this.size > 0x1000 && retval.toInt() > 0) {
                try {
                    // 检查是否是 DEX 文件
                    const magic = Memory.readByteArray(retval, 4);
                    const magicArray = new Uint8Array(magic);

                    if (magicArray[0] === 0x64 &&
                        magicArray[1] === 0x65 &&
                        magicArray[2] === 0x78 &&
                        magicArray[3] === 0x0a) {
                        console.log('[!] mmap 映射了 DEX!');
                        console.log('    地址: ' + retval);
                        console.log('    大小: ' + this.size);

                        // Dump
                        const filename = 'mmap_dex_' + Date.now() + '.dex';
                        const data = Memory.readByteArray(retval, this.size);
                        const file = new File('/data/local/tmp/' + filename, 'wb');
                        file.write(data);
                        file.close();
                        console.log('[+] 已保存: ' + filename);
                    }
                } catch (e) {}
            }
        }
    });
}

// 初始化
console.log('[*] 加固脱壳脚本已加载');
hookOpenDexFile();
hookMmap();
```

---

## 实战分析案例

### 案例 1: 分析 APK 中的敏感方法

```bash
# 1. 解压 APK
unzip app.apk -d app_extracted

# 2. 使用我们的解析器搜索敏感方法
python dex_parser.py app_extracted/classes.dex "encrypt"
python dex_parser.py app_extracted/classes.dex "decrypt"
python dex_parser.py app_extracted/classes.dex "password"
python dex_parser.py app_extracted/classes.dex "secret"

# 3. 搜索网络相关
python dex_parser.py app_extracted/classes.dex "http"
python dex_parser.py app_extracted/classes.dex "api"
```

### 案例 2: 验证 DEX 完整性（检测篡改）

```python
def check_dex_integrity(dex_path: str) -> dict:
    """检查 DEX 文件完整性"""
    parser = DexParser(dex_path)
    parser.parse()

    result = {
        'path': dex_path,
        'checksum_valid': parser.verify_checksum(),
        'signature_valid': parser.verify_signature(),
        'header': {
            'version': parser.header.magic[4:7].decode() if parser.header else None,
            'file_size': parser.header.file_size if parser.header else 0,
            'method_count': parser.header.method_ids_size if parser.header else 0,
            'class_count': parser.header.class_defs_size if parser.header else 0,
        }
    }

    # 检查异常特征
    warnings = []
    if parser.header:
        if parser.header.method_ids_size > 60000:
            warnings.append('方法数接近上限，可能需要 Multi-DEX')
        if parser.header.link_size > 0:
            warnings.append('包含链接段，可能是非标准 DEX')

    result['warnings'] = warnings
    return result

# 批量检查
import os
for dex_file in os.listdir('app_extracted'):
    if dex_file.endswith('.dex'):
        result = check_dex_integrity(f'app_extracted/{dex_file}')
        print(f"\n{dex_file}:")
        print(f"  校验和: {'通过' if result['checksum_valid'] else '失败'}")
        print(f"  签名: {'通过' if result['signature_valid'] else '失败'}")
        print(f"  类数量: {result['header']['class_count']}")
        print(f"  方法数量: {result['header']['method_count']}")
```

### 案例 3: 定位加固壳的特征

常见加固厂商的特征字符串：

| 加固厂商 | 特征字符串/类名 |
|---------|----------------|
| 梆梆加固 | `com.secneo.`, `libsecexe.so`, `libDexHelper.so` |
| 360加固 | `com.stub.`, `libjiagu.so`, `libprotectClass.so` |
| 爱加密 | `com.ijiami.`, `libexec.so`, `libexecmain.so` |
| 腾讯乐固 | `com.tencent.bugly`, `libshella`, `libBugly.so` |
| 娜迦加固 | `com.nagain.`, `libnaga.so` |
| 通付盾 | `com.payegis.`, `libegis.so` |

```python
# 检测加固类型
def detect_packer(dex_path: str) -> str:
    parser = DexParser(dex_path)
    parser.parse()

    packers = {
        'secneo': '梆梆加固',
        'stub.StubApp': '360加固',
        'ijiami': '爱加密',
        'tencent.StubShell': '腾讯乐固',
        'nagain': '娜迦加固',
        'payegis': '通付盾',
    }

    for keyword, name in packers.items():
        results = parser.search_strings(keyword)
        if results:
            return f"检测到 {name}"

    return "未检测到已知加固"
```

---

## 常见问题与技巧

!!! warning "65536 方法数限制"
    DEX 文件的 Method IDs 使用 16 位索引，最多只能引用 65536 个方法。这就是著名的 "64K 方法数限制"。

    **解决方案**:

    - 启用 Multi-DEX（Android 5.0+ 原生支持）
    - 使用 ProGuard/R8 移除未使用的代码
    - 合理划分模块，减少依赖

!!! tip "快速判断 DEX 版本"
    ```python
    # DEX 035 - Android 7.0 及之前
    # DEX 037 - Android 8.0 引入默认方法
    # DEX 038 - Android 9.0
    # DEX 039 - Android 10.0+

    with open('classes.dex', 'rb') as f:
        magic = f.read(8)
        version = magic[4:7].decode()
        print(f"DEX 版本: {version}")
    ```

!!! info "修复损坏的 DEX"
    如果校验和或签名不匹配，可以重新计算并修复：

    ```python
    import hashlib
    import zlib

    def fix_dex(data: bytes) -> bytes:
        """修复 DEX 文件的校验和和签名"""
        data = bytearray(data)

        # 重新计算 SHA-1 签名 (从偏移 0x20 开始)
        sha1 = hashlib.sha1(data[32:]).digest()
        data[12:32] = sha1

        # 重新计算 Adler32 校验和 (从偏移 0x0C 开始)
        checksum = zlib.adler32(bytes(data[12:])) & 0xffffffff
        data[8:12] = checksum.to_bytes(4, 'little')

        return bytes(data)
    ```
