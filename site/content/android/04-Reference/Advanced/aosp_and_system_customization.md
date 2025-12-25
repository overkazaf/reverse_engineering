---
title: "AOSP 与 Android 系统裁剪"
date: 2025-06-05
tags: ["Native层", "Frida", "DEX", "高级", "Hook", "Xposed"]
weight: 10
---

# AOSP 与 Android 系统裁剪

Android 开源项目（AOSP）是 Android 操作系统的开源基础。能够编译和修改 AOSP 是进行深度系统级定制、安全研究和 ROM 开发的核心技能。本节将介绍 AOSP 的基本概念、编译流程以及常见的系统裁剪技术。

## 1. AOSP 基础与编译

### a) AOSP 源码同步

编译 AOSP 的第一步是获取其庞大的源代码树。

1. **环境准备**:
   - 一个强大的 Linux 构建服务器（推荐 Ubuntu LTS），至少需要 16GB RAM 和 300GB 的可用磁盘空间。
   - 安装必要的依赖包，如 `git`, `curl`, `python`, `Java SDK` 等。

2. **获取 Repo 工具**: `Repo` 是 Google 开发的、基于 Git 的代码库管理工具，用于管理 AOSP 中数百个不同的 Git 仓库。

```bash
# 下载 Repo 工具
mkdir -p ~/.bin
curl https://storage.googleapis.com/git-repo-downloads/repo > ~/.bin/repo
chmod a+x ~/.bin/repo
export PATH=~/.bin:$PATH
```

```bash
# 创建工作目录
mkdir aosp && cd aosp

# 初始化源码仓库，指定分支（例如 android-12.0.0_r1）
repo init -u https://android.googlesource.com/platform/manifest -b android-12.0.0_r1 --depth=1

# 开始同步源码（这将是一个漫长的过程）
repo sync -c -j8
```

- `--depth=1`: 只同步最新的 commit，大幅减少下载量。
- `-c`: 只同步当前分支。
- `-j8`: 使用 8 个线程并行同步。

### b) 编译流程

1. **设置环境**:
    ```bash
    source build/envsetup.sh
    ```
2. **选择目标 (Lunch)**:
    ```bash
    lunch aosp_arm64-eng
    ```
    - `aosp_arm64`: 目标设备架构（64 位 ARM）。
    - `eng`: 构建变体（Engineering），包含最多的调试工具，权限为 root，适合开发和逆向。其他还有 `user`（发布版）和 `userdebug`（带 root 和调试功能的用户版）。
3. **开始编译 (Make)**:
    ```bash
    m
    ```
4. **编译产物**:

编译完成后，所有的系统镜像文件都存放在 `out/target/product/<device_name>/` 目录下，主要包括：

- `system.img`: 系统分区镜像。
- `vendor.img`: 厂商分区镜像。
- `boot.img`: 启动分区镜像，包含内核和 ramdisk。
- `userdata.img`: 用户数据分区镜像。

---

## 2. 系统裁剪与定制技术

拥有了编译 AOSP 的能力后，你就可以对系统进行任意的修改。

### a) 预置与删除 App

- **路径**: App 通常定义在 `packages/apps/` 目录下。
- **修改 `PRODUCT_PACKAGES`**: 在特定设备的 `device.mk` 文件中（例如 `device/<vendor>/<device_name>/device.mk`），有一个名为 `PRODUCT_PACKAGES` 的变量。
- **增加 App**: 将你想要预置的 App 的模块名添加到这个列表中。
- **删除 App**: 从这个列表中移除你不想要的系统 App（如 `Calendar`, `Camera2`）的模块名。

### b) 修改 Framework 层

这是更深度的定制，可以改变 Android 系统的核心行为。

- **路径**: Framework 核心代码位于 `frameworks/base/`。
- **示例：修改状态栏逻辑**:
  1. 找到负责状态栏管理的 `SystemUI` App (`frameworks/base/packages/SystemUI/`)。
  2. 修改其中的 Java 或 XML 文件，例如，改变时钟的显示格式或电池图标。
  3. 重新编译 `SystemUI` 模块：`m SystemUI`。
  4. 只编译模块并生成新的 `system.img`：`m snod` (`make systemimage-nodeps`)。

### c) 定制内核 (Kernel)

AOSP 默认不包含内核源码。你需要从 Google 的内核源码仓库或设备厂商的开源站点单独下载内核源码，并进行编译。

1. **获取内核源码**:
    ```bash
    git clone https://android.googlesource.com/kernel/common.git
    ```
2. **配置与编译**:
    ```bash
    # 使用与 AOSP 匹配的交叉编译工具链
    export CROSS_COMPILE=.../aarch64-linux-android-4.9/bin/aarch64-linux-android-

    # 配置内核
    make defconfig

    # 编译内核镜像
    make
    ```

### d) 制作完整的自定义 ROM

一个完整的自定义 ROM（如 LineageOS）的制作过程，就是上述所有技术的综合应用：

1. 同步 AOSP 基础代码。
2. 集成特定设备的驱动和配置文件（Device Tree）。
3. 修改 Framework，添加自定义功能（如高级重启菜单）。
4. 移除或替换系统 App。
5. 集成定制的内核。
6. 编译并打包成一个可供用户刷写的 `zip` 文件。

---

## 3. Android Linker 与 SO 加载原理

### Linker 架构与工作原理

Android 系统使用动态链接器 (`/system/bin/linker` 或 `/system/bin/linker64`) 来加载和链接共享库 (.so 文件)。

#### 系统架构

```text
Runtime.loadLibrary()
        ↓
DexPathList.loadLibrary()
        ↓
nativeLoad() [JNI]
        ↓
android_dlopen_ext()
        ↓
do_dlopen() [linker]
        ↓
find_library_internal()
        ↓
load_library() → link_image()
```

#### 核心函数分析

**find_library_internal - 查找库**:

```cpp
static soinfo* find_library_internal(android_namespace_t* ns,
                                     const char* name,
                                     int rtld_flags,
                                     const android_dlextinfo* extinfo,
                                     soinfo* needed_by) {
    // 1. 检查是否已加载
    soinfo* si = find_loaded_library_by_soname(ns, name);
    if (si != nullptr) {
        return si;
    }

    // 2. 在命名空间中搜索
    std::string realpath;
    if (!find_library_in_namespace(ns, name, &realpath)) {
        return nullptr;
    }

    // 3. 加载库文件
    return load_library(ns, realpath.c_str(), rtld_flags, extinfo, needed_by);
}
```

**load_library - 加载库**:

```cpp
static soinfo* load_library(android_namespace_t* ns,
                            const char* name,
                            int rtld_flags,
                            const android_dlextinfo* extinfo,
                            soinfo* needed_by) {
    // 1. 打开 ELF 文件
    int fd = open(name, O_RDONLY | O_CLOEXEC);

    // 2. 解析 ELF 头
    ElfReader elf_reader(name, fd, file_offset, file_size);
    if (!elf_reader.Load(extinfo)) {
        return nullptr;
    }

    // 3. 创建 soinfo 结构
    soinfo* si = soinfo_alloc(ns, realpath, &file_stat, rtld_flags, extinfo);

    // 4. 映射内存段
    if (!si->prelink_image()) {
        return nullptr;
    }

    return si;
}
```

**link_image - 链接镜像**:

```cpp
bool soinfo::link_image(const soinfo_list_t& global_group,
                        const soinfo_list_t& local_group,
                        const android_dlextinfo* extinfo) {
    // 1. 解析动态段
    if (!phdr_table_get_dynamic_section(phdr, phnum, load_bias, &dynamic, &dynamic_flags)) {
        return false;
    }

    // 2. 处理依赖库
    for (ElfW(Dyn)* d = dynamic; d->d_tag != DT_NULL; ++d) {
        if (d->d_tag == DT_NEEDED) {
            const char* library_name = get_string(d->d_un.d_val);
            soinfo* lsi = find_library(library_name, ...);
        }
    }

    // 3. 重定位处理
    if (!relocate(global_group, local_group)) {
        return false;
    }

    // 4. 调用构造函数
    call_constructors();

    return true;
}
```

#### SO 内存布局

```text
0x7000000000 ┌─────────────────┐
             │ .text (RX)      │ 代码段
0x7001000000 ├─────────────────┤
             │ .rodata (R)     │ 只读数据段
0x7002000000 ├─────────────────┤
             │ .data (RW)      │ 可读写数据段
0x7003000000 ├─────────────────┤
             │ .bss (RW)       │ 未初始化数据段
0x7004000000 └─────────────────┘
```

#### 内存保护设置

```cpp
int phdr_table_protect_segments(const ElfW(Phdr)* phdr_table,
                                size_t phdr_count,
                                ElfW(Addr) load_bias) {
    for (size_t i = 0; i < phdr_count; ++i) {
        const ElfW(Phdr)* phdr = &phdr_table[i];
        if (phdr->p_type != PT_LOAD) continue;

        int prot = PFLAGS_TO_PROT(phdr->p_flags);
        if (mprotect(reinterpret_cast<void*>(seg_page_start + load_bias),
                     seg_page_end - seg_page_start, prot) < 0) {
            return -1;
        }
    }
    return 0;
}
```

---

## 4. 反调试与检测技术

### init 函数中的反调试

```cpp
__attribute__((constructor))
void anti_debug_check() {
    // 检测 Frida
    if (access("/data/local/tmp/frida-server", F_OK) == 0) {
        _exit(1);
    }

    // 检测调试器
    if (ptrace(PTRACE_TRACEME, 0, 1, 0) == -1) {
        _exit(1);
    }

    // 检测虚拟机环境
    check_emulator_files();
}
```

### 符号表检测

```cpp
void check_loaded_symbols() {
    void* handle = dlopen(NULL, RTLD_NOW);

    // 检测 Frida 符号
    if (dlsym(handle, "frida_agent_main") != NULL) {
        _exit(1);
    }

    // 检测 Xposed 符号
    if (dlsym(handle, "xposed_bridge") != NULL) {
        _exit(1);
    }
}
```

### 代码完整性校验

```cpp
void check_code_integrity() {
    Dl_info info;
    dladdr((void*)check_code_integrity, &info);

    // 计算代码段哈希
    uint32_t current_hash = calculate_hash(info.dli_fbase, TEXT_SIZE);
    if (current_hash != EXPECTED_HASH) {
        _exit(1);
    }
}
```

---

## 5. Frida 绕过技术

### 绕过 ptrace 检测

```javascript
var ptrace = Module.findExportByName("libc.so", "ptrace");
if (ptrace) {
    Interceptor.attach(ptrace, {
        onEnter: function(args) {
            var request = args[0].toInt32();
            if (request === 0) { // PTRACE_TRACEME
                console.log("[+] ptrace(PTRACE_TRACEME) blocked");
                args[0] = ptr(-1); // 修改参数使其失败
            }
        },
        onLeave: function(retval) {
            retval.replace(ptr(0)); // 返回成功
        }
    });
}
```

### 隐藏 Frida 符号

```javascript
var dlsym = Module.findExportByName("libdl.so", "dlsym");
Interceptor.attach(dlsym, {
    onEnter: function(args) {
        this.symbol_name = args[1].readCString();
    },
    onLeave: function(retval) {
        var blocked_symbols = ["frida_agent_main", "xposed_bridge"];
        if (blocked_symbols.includes(this.symbol_name)) {
            console.log("[+] Hiding symbol: " + this.symbol_name);
            retval.replace(ptr(0));
        }
    }
});
```

### 绕过 mprotect 检测

```javascript
var mprotect = Module.findExportByName("libc.so", "mprotect");
Interceptor.attach(mprotect, {
    onEnter: function(args) {
        var addr = args[0];
        var size = args[1].toInt32();
        var prot = args[2].toInt32();

        console.log("[+] mprotect called: " + addr + ", size: " + size + ", prot: " + prot);

        // 防止移除执行权限
        if ((prot & 0x4) == 0) { // PROT_EXEC
            args[2] = ptr(prot | 0x4);
        }
    }
});
```

### 隐藏敏感路径

```javascript
var access = Module.findExportByName("libc.so", "access");
Interceptor.attach(access, {
    onEnter: function(args) {
        var path = args[0].readCString();
        var sensitive_paths = [
            "/data/local/tmp/frida-server",
            "/system/xbin/su",
            "/system/app/Superuser.apk"
        ];

        if (sensitive_paths.some(p => path.includes(p))) {
            console.log("[+] Blocking access to: " + path);
            args[0] = Memory.allocUtf8String("/non/existent/path");
        }
    }
});
```

---

## 6. init_array 注入技术

### Python 脚本注入

```python
from elftools.elf.elffile import ELFFile

def inject_init_array(elf_path, hook_function_addr):
    with open(elf_path, 'r+b') as f:
        elf = ELFFile(f)

        # 查找 .init_array 段
        init_array = elf.get_section_by_name('.init_array')
        if init_array:
            # 在现有函数指针后添加新函数地址
            f.seek(init_array['sh_offset'] + init_array['sh_size'])
            f.write(hook_function_addr.to_bytes(8, 'little'))
```

### C 代码运行时注入

```cpp
void inject_init_array_runtime() {
    // 1. 找到目标 SO 加载基址
    void* base_addr = dlopen("target.so", RTLD_NOLOAD);

    // 2. 解析 ELF 头找到 .init_array 段
    ElfW(Ehdr)* ehdr = (ElfW(Ehdr)*)base_addr;
    ElfW(Shdr)* shdr = (ElfW(Shdr)*)((char*)base_addr + ehdr->e_shoff);

    // 3. 修改内存保护
    mprotect(init_array_addr, init_array_size, PROT_READ | PROT_WRITE);

    // 4. 添加函数指针
    *(void**)(init_array_addr + init_array_size) = target_function;

    // 5. 恢复保护
    mprotect(init_array_addr, init_array_size, PROT_READ);
}
```

---

## 7. 综合反调试检测

```cpp
class AntiDebugChecker {
private:
    static bool check_debugger_presence() {
        return ptrace(PTRACE_TRACEME, 0, 1, 0) == -1;
    }

    static bool check_frida_artifacts() {
        const char* frida_files[] = {
            "/data/local/tmp/frida-server",
            "/data/local/tmp/frida-agent-64.so"
        };

        for (auto file : frida_files) {
            if (access(file, F_OK) == 0) return true;
        }
        return false;
    }

    static bool check_memory_maps() {
        FILE* fp = fopen("/proc/self/maps", "r");
        char line[512];
        while (fgets(line, sizeof(line), fp)) {
            if (strstr(line, "frida") || strstr(line, "gum-js-loop")) {
                fclose(fp);
                return true;
            }
        }
        fclose(fp);
        return false;
    }

public:
    static void comprehensive_check() {
        if (check_debugger_presence() ||
            check_frida_artifacts() ||
            check_memory_maps()) {
            // 执行对抗措施
            execute_countermeasures();
        }
    }
};
```

### 定时检测线程

```cpp
void start_anti_debug_thread() {
    std::thread([]{
        while (true) {
            std::this_thread::sleep_for(std::chrono::seconds(5));
            AntiDebugChecker::comprehensive_check();
        }
    }).detach();
}
```

---

## 总结

掌握 AOSP 编译和系统定制技术的意义：

- 深入理解 Android Framework 的工作原理，为 Hook 和逆向提供更底层的视角。
- 通过修改系统来绕过应用层的反分析技术，实现"降维打击"。
