---
title: "Frida 核心模块与实现原理"
date: 2025-12-25
weight: 10
---

# Frida 核心模块与实现原理

Frida 是一个功能强大的动态插桩框架，但要充分利用它，理解其内部工作原理至关重要。本指南将深入探讨构成 Frida 的几个核心模块、它们的作用以及它们是如何协同工作的。

---

## 目录

- [Frida 核心模块与实现原理](#frida-核心模块与实现原理)
  - [目录](#目录)
    - [Frida 的 architecture 概览](#frida-的-architecture-概览)
    - [核心组件详解](#核心组件详解)
      - [**Frida-Server**: 设备端的守护进程](#frida-server-设备端的守护进程)
      - [**Frida-Core**: 注入目标进程的核心引擎](#frida-core-注入目标进程的核心引擎)
      - [**Frida-Gum**: 实现 Hook 的魔法棒](#frida-gum-实现-hook-的魔法棒)
        - [`Interceptor`: 函数拦截器](#interceptor-函数拦截器)
        - [`Stalker`: 指令级跟踪器](#stalker-指令级跟踪器)
      - [**JavaScript (V8) 运行时**: 脚本的执行环境](#javascript-v8-运行时-脚本的执行环境)
      - [**语言绑定 (Bindings)**: 你的控制台](#语言绑定-bindings-你的控制台)
    - [工作流程串讲](#工作流程串讲)

---

### Frida 的 architecture 概览

Frida 采用的是一种**客户端-服务器 (Client-Server)** 架构。

!!! question "思考：为什么需要这样复杂的架构？"
Frida 为什么不设计成一个简单的工具，而要分成客户端、服务器、Agent 三层？

- **跨平台的必然选择**：

* **隔离性**：你的分析脚本（Python）运行在 PC，不会影响目标设备的性能
* **安全性**：Server 只负责进程管理和注入，真正的"危险操作"在隔离的进程内
* **灵活性**：同一个 Server 可以同时为多个客户端服务，支持团队协作
* **跨语言**：PC 端用 Python/Node.js 编写自动化脚本，目标进程内用 JavaScript 操作内存，各取所长

这种架构的本质是：**把"控制"和"执行"分离**，就像遥控无人机——遥控器在你手上，但飞行逻辑在机上。

- **客户端 (Client)**: 运行在你 PC 上的部分。这包括你编写的 Python 或 Node.js 脚本，以及你使用的 Frida 命令行工具 (`frida`, `frida-trace` 等)。

- **服务器 (Server)**: 在目标设备（如 Android 手机）上以后台守护进程模式运行的 `frida-server`。

- **Agent**: 当你附加到一个目标进程时，Frida 会将一个动态库 (`frida-agent.so`) **注入**到该进程的内存空间中。这个 Agent 负责执行你在客户端脚本中定义的逻辑。

![Frida Architecture](https://frida.re/static/images/frida-architecture.png)

- 图片来源: frida.re\*

---

### 核心组件详解

#### **Frida-Server**: 设备端的守护进程

`frida-server` 是一个在目标设备上运行的二进制文件。它的主要职责是：

1. **监听连接**: 监听来自你 PC 上 Frida 客户端的 TCP 连接。
2. **进程管理**: 枚举目标设备上正在运行的进程，获取应用信息。
3. **注入 Agent**: 当客户端指定要附加 (attach) 或启动 (spawn) 一个应用时，`frida-server` 负责将 `frida-agent.so` 注入到目标进程中。在 Android 上，它通常通过 `ptrace` 来实现这一点。

#### **Frida-Core**: 注入目标进程的核心引擎

`frida-core` 是 Frida 的核心，它被编译成 `frida-agent.so` 并注入到目标进程。它是一个用 C 语言编写的多平台库，主要负责：

1. **进程内通信**: 建立一个与 `frida-server` 的通信渠道，从而间接地与你的 PC 客户端通信。
2. **加载 JavaScript 引擎**: 它内部嵌入了一个 Google V8 JavaScript 引擎。
3. **暴露原生 API**: 将底层的 `frida-gum` 功能通过 JavaScript API (如 `Interceptor`, `Memory`, `NativePointer`) 暴露给用户脚本。

#### **Frida-Gum**: 实现 Hook 的魔法棒

`frida-gum` 是 `frida-core` 中最具魔力的部分，它是一个跨平台的代码插桩工具包。所有 Hook 和代码跟踪功能都由它提供。

##### `Interceptor`: 函数拦截器

`Interceptor` 是你最常使用的功能，用于 Hook/Trace/替换任意函数。

!!! tip "深入理解：Hook 的本质是什么？"
很多人把 Hook 当成"黑魔法"，但其实原理很朴素：

- **Hook = 劫持程序的执行流**

想象你在高速公路上设置了一个收费站：

1. **原始道路**：函数的正常执行流程
2. **收费站（Trampoline）**：你插入的代码
3. **改道标志（JMP）**：修改函数入口的跳转指令
4. **恢复通行**：执行原始指令后继续

理解了这个本质，你就能：

- 判断哪些 Hook 会相互冲突（都修改同一个函数入口）
- 理解为什么有些反 Hook 检测能发现你（检查函数头的修改）
- 知道如何写更隐蔽的 Hook（inline hook vs. PLT/GOT hook）

* **实现原理**:

1. **动态代码生成**: 当你 `Interceptor.attach` 一个函数时，Frida-Gum 会在内存中动态地生成一小段汇编代码，我们称之为**蹦床 (Trampoline)**。
2. **函数头重写 (Prologue Rewriting)**: Frida-Gum 会修改目标函数入口点（函数头）的几条指令，将其替换为一个**无条件跳转 (`JMP`) 指令**，该指令指向刚刚创建的蹦床。Frida 会非常小心地保存被它覆盖掉的原始指令。
3. **执行流程**:

- 当应用调用目标函数时，它会首先跳转到蹦床。

- 蹦床代码会保存当前的 CPU 上下文（寄存器状态），然后调用你在 JavaScript 中定义的 `onEnter` 回调。

- `onEnter` 执行完毕后，蹦床会执行被它覆盖掉的原始函数指令，然后跳转回原始函数的剩余部分继续执行。

- 当原始函数执行完毕后，控制权返回给蹦床，蹦床再调用你的 `onLeave` 回调。

- 最后，蹦床恢复之前保存的 CPU 上下文，并将返回值传递给原始的调用者。

##### `Stalker`: 指令级跟踪器

`Stalker` 是 Frida 的代码跟踪引擎，功能极其强大但使用也更复杂。它可以用来记录一个线程执行过的**每一条**汇编指令。

- **实现原理 (基于动态重新编译)**:

1. **基本块 (Basic Block)**: Stalker 将代码分解为“基本块”。一个基本块是一系列连续的指令，只有一个入口点和一个出口点（通常是跳转或返回指令）。
2. **代码拷贝与插桩**: 当一个线程将要执行某个基本块时，Stalker 会：
   a. 将这个基本块的所有指令**拷贝**到一块新的内存区域。
   b. 在这份拷贝中**插入**你的分析代码（例如，记录指令地址、寄存器值的代码）。
   c. 执行这份被插桩后的代码副本。
3. **代码缓存 (Code Cache)**: Stalker 会缓存这些被修改过的基本块。下次再执行到同一个基本块时，可以直接使用缓存中的版本，极大地提高了性能。
4. **链接 (Chaining)**: Stalker 会修改每个插桩后基本块的末尾，使其跳转到下一个即将执行的原始基本块对应的“插桩版本”，从而形成一个完整的跟踪链。

简而言之，`Stalker` 通过创建和执行原始代码的“带监控的副本”来实现无死角的指令级跟踪。

#### **JavaScript (V8) 运行时**: 脚本的执行环境

为什么我们用 JavaScript 写 Hook 逻辑？因为 `frida-agent.so` 在注入目标进程后，会初始化一个 V8 引擎实例。你的 JS 脚本被完整地加载到这个 V8 引擎中执行。

这带来了巨大的优势：

- **高级语言的便利性**: 你可以在目标进程的地址空间内，用 JavaScript 的便利性来操作内存、调用函数。

- **JIT 编译**: V8 的即时编译 (JIT) 特性使得你的 JS 脚本能以接近原生的速度运行，性能远超解释执行。

- **强大的生态**: 可以利用现有的 JS 库。

#### **语言绑定 (Bindings)**: 你的控制台

`frida-python`, `frida-node` 等库是你的“控制端”。它们负责：

- **连接 Server**: 与设备上的 `frida-server` 建立通信。

- **发送指令**: 将你的指令（如“附加到 PID 1234”）发送给 `frida-server`。

- **加载脚本**: 将你的 `.js` 脚本文件内容发送给 `frida-agent.so` 里的 V8 引擎去执行。

- **双向通信 (RPC)**: 建立一个双向的 RPC 通道。这使得你在 JS 中调用 `send()` 的数据能被 Python 的 `on_message` 回调接收，反之亦然。

---

### 工作流程串讲

当你执行 `frida -U -f com.example.app -l script.js` 时，发生了什么？

1. **[PC]** `frida` (Python 客户端) 解析命令。
2. **[PC -> Phone]** 客户端通过 USB 连接到手机上的 `frida-server`。
3. **[PC -> Phone]** 客户端向 `frida-server` 发送指令：“请以 `spawn` 模式启动 `com.example.app`”。
4. **[Phone]** `frida-server` 找到 `com.example.app` 并启动它，但使其处于**暂停**状态。
5. **[Phone]** `frida-server` 将 `frida-agent.so` 注入到这个新创建的应用进程中。
6. **[Phone]** `frida-agent.so` 在进程内初始化，启动 V8 引擎，并建立与 `frida-server` 的内部通信。
7. **[PC -> Phone]** 客户端读取 `script.js` 的内容，并通过 `frida-server` 将其发送给 `frida-agent.so`。
8. **[Phone]** `frida-agent.so` 中的 V8 引擎执行 `script.js` 的代码（例如，`Interceptor.attach(...)`）。
9. **[PC -> Phone]** 客户端发送“恢复进程”的指令。
10. **[Phone]** 应用进程从暂停状态中恢复，开始正常执行。当它调用被 Hook 的函数时，你在 `script.js` 中定义的逻辑就会被触发。
11. **[双向]** 脚本中的 `send()` 消息会通过 `agent -> server -> client` 的路径回到你的 PC 终端上显示。
