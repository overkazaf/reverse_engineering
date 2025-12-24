---
title: "Unity 游戏逆向 (Il2Cpp) 案例"
weight: 10
---

# Unity 游戏逆向 (Il2Cpp) 案例

> **📚 前置知识**
>
> 本案例涉及以下核心技术，建议先阅读相关章节：
>
> - **[SO/ELF 格式](../04-Reference/Foundations/so_elf_format.md)** - 理解 libil2cpp.so 的结构
> - **[Frida Native Hook](../02-Tools/Dynamic/frida_guide.md#native-hook)** - 对 Il2Cpp 函数进行运行时修改

Unity 是目前最流行的移动游戏引擎之一。现代 Unity 游戏通常使用 Il2Cpp 脚本后端，将 C# 代码转换为 C++ 代码并编译为 Native 库 (`libil2cpp.so`)。这使得传统的 Java/Smali 逆向方法失效，需要全新的工具和思路。

## 核心架构与文件结构

一个典型的 Unity Il2Cpp 游戏包含以下关键文件：

1. **`lib/armeabi-v7a/libil2cpp.so`**: 这是游戏的核心逻辑库。所有的 C# 脚本（玩家控制、游戏逻辑、网络通信）都被编译到了这里。
2. **`assets/bin/Data/Managed/global-metadata.dat`**: 这是 Il2Cpp 的元数据文件。它包含了被转换前的 C# 类名、方法名、字段名以及它们在 `libil2cpp.so` 中的偏移地址。**这是逆向的关键钥匙**。
3. **`lib/armeabi-v7a/libmain.so`** (或 `libunity.so`): Unity 引擎的运行时库，通常不需要修改。

---

## 逆向流程

### 第 1 步：元数据提取 (Metadata Dumping)

由于 `libil2cpp.so` 是剥离了符号表 (stripped) 的二进制文件，直接用 IDA 打开只能看到成千上万个无名函数 (`sub_xxxx`)。我们需要结合 `global-metadata.dat` 来还原这些函数的真实名称。

- **工具**: [Il2CppDumper](https://github.com/Perfare/Il2CppDumper)

1. 将 APK 解压，提取出 `libil2cpp.so` 和 `global-metadata.dat`。
2. 运行 `Il2CppDumper.exe <libil2cpp.so> <global-metadata.dat>`。
3. 工具会生成：

- **`dump.cs`**: 还原后的 C# 伪代码，展示了所有类、字段和方法结构。
- **`script.py`**: 用于 IDA Pro 的 Python 脚本，可以自动重命名 IDA 中的函数。
- **`ghidra.py`**: 用于 Ghidra 的脚本。
- **`DummyDll/`**: 生成的空 DLL 文件，可以用 dnSpy 打开查看类结构。

### 第 2 步：静态分析与定位

使用 `dnSpy` 打开生成的 Dummy DLL，或是直接阅读 `dump.cs`，我们可以像阅读源码一样浏览游戏的类结构。

- **寻找切入点**:
- **货币修改**: 搜索 `Coin`, `Gem`, `Money`, `Currency` 等关键词。寻找 `AddCoin()`, `GetMoney()`, `UpdateCurrency()` 等方法。
- **无敌/高伤害**: 搜索 `PlayerController`, `BattleManager`, `Health`, `Damage`。寻找 `TakeDamage()`, `OnHit()` 等方法。
- **内购破解**: 搜索 `IAP`, `Purchase`, `Store`, `Payment`。寻找 `OnPurchaseSuccess()`, `VerifyReceipt()` 等方法。

- **示例**:
  在 `dump.cs` 中找到如下类：

```csharp
public class PlayerData {
public int coin;
public int gem;
public void AddCoin(int amount); // Address: 0x123456
public void SubCoin(int amount); // Address: 0x123460
}

```

// Il2Cpp Hook Template

var soName = "libil2cpp.so";
var baseAddr = Module.findBaseAddress(soName);

if (baseAddr) {
// Target function offset: 0x123456 (AddCoin)
var addCoinFunc = baseAddr.add(0x123456);

Interceptor.attach(addCoinFunc, {
onEnter: function(args) {
// args[0] is 'this' pointer (PlayerData instance)
// args[1] is amount (coin count to add)

console.log("[*] AddCoin called");
console.log(" Amount: " + args[1].toInt32());

// Modify parameter: force add 99999 regardless of game logic
args[1] = ptr(99999);
},
onLeave: function(retval) {
console.log("[*] AddCoin finished");
}
});
} else {
console.log("[-] libil2cpp.so not found!");
}

```
// Use frida-il2cpp-bridge
Il2Cpp.perform(() => {
// 1. Find class
const PlayerData = Il2Cpp.domain.assembly("Assembly-CSharp").image.class("PlayerData");

// 2. Hook method (auto process offset, no need to calculate manually)
PlayerData.method("SubCoin").implementation = function (amount) {
console.log("[*] SubCoin called with amount: " + amount);
// Prevent coin deduction (do nothing)
return;
};

// 3. Manually call method
// Assume we want to call PlayerData.Instance.AddCoin(1000)
// Need to find static instance or current instance first

// Trace all PlayerData instance creation
Il2Cpp.traceClass(PlayerData);
});

```

- **对抗**:
  - **Hook 加载函数**: 游戏必须在运行时解密 metadata 才能正常运行。Hook `libil2cpp.so` 中加载 metadata 的函数（通常是 `il2cpp::vm::MetadataCache::Register` 或相关初始化函数），Dump 出解密后的内存内容。
- **分析解密逻辑**: 逆向 `libil2cpp.so` 的初始化流程，找到解密 metadata 的算法（通常是 XOR 或 AES），写脚本还原。

### 2. 函数地址混淆 / 动态计算

- **现象**: Il2CppDumper 导出的地址与内存中的实际地址不符。
- **对抗**:
- 这通常是因为游戏在运行时动态修改了函数指针。
- 使用 **Frida 的扫描功能**，根据机器码特征（Pattern Scanning）来定位函数，而不是依赖固定的偏移。

### 3. 反调试与完整性校验

- **现象**: 附加 Frida 后游戏崩溃或闪退。
- **对抗**:
- 参考 "Anti-Debugging" 章节，隐藏 Frida 特征，Bypass TracerPid 检测。
- 使用 Magisk + Riru + Il2CppDumper (Zygisk 版) 在系统层面进行 Dump，规避应用层检测。

---

## 总结

Unity Il2Cpp 逆向的核心在于**还原符号**。只要拿到了正确的 `global-metadata.dat` 和 `libil2cpp.so` 的映射关系，剩下的工作就变成了标准的逻辑分析和 Native Hook。熟练掌握 Il2CppDumper 和 Frida 是搞定这类游戏的关键。
