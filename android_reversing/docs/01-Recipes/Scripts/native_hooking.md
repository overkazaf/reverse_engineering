# Native 层 Hook 技巧 (Native Hooking Patterns)

> **📚 前置知识**
>
> 本配方涉及以下核心技术，建议先阅读相关章节：
>
> - **[Frida Native Hook](../../02-Tools/Dynamic/frida_guide.md#native-hook)** - 掌握 Interceptor API
> - **[SO/ELF 格式](../../04-Reference/Foundations/so_elf_format.md)** - 理解 libc 函数与符号

在 Android 逆向中，Native 层 (C/C++) 的分析往往比 Java 层更具挑战性。Hook 标准 C 库 (libc) 函数是理解 Native 层行为、脱壳和还原算法的重要手段。

---

## 1. 文件操作监控 (File I/O)

监控文件操作可以帮助我们发现 App 读取了哪些配置文件、加载了哪些 Dex/So 文件，或者将解密后的数据写入到了哪里。

### Hook `open` / `openat`

```javascript
// Hook open and openat to trace file access
function hookFileOpen() {
  // Intercept 'open'
  var openPtr = Module.findExportByName("libc.so", "open");
  if (openPtr) {
    Interceptor.attach(openPtr, {
      onEnter: function (args) {
        this.path = args[0].readCString();
        this.flags = args[1].toInt32();
      },
      onLeave: function (retval) {
        if (
          this.path &&
          (this.path.endsWith(".dex") || this.path.endsWith(".so"))
        ) {
          console.log("[open] FD: " + retval + " Path: " + this.path);
        }
      },
    });
  }

  // Intercept 'openat' (commonly used on newer android versions)
  var openatPtr = Module.findExportByName("libc.so", "openat");
  if (openatPtr) {
    Interceptor.attach(openatPtr, {
      onEnter: function (args) {
        // args[0] is dirfd, args[1] is path
        this.path = args[1].readCString();
        this.flags = args[2].toInt32();
      },
      onLeave: function (retval) {
        if (
          this.path &&
          (this.path.indexOf("base.apk") >= 0 || this.path.indexOf(".dex") >= 0)
        ) {
          console.log("[openat] FD: " + retval + " Path: " + this.path);
        }
      },
    });
  }
}

hookFileOpen();
```

---

## 2. 动态库加载监控 (dlopen)

监控 `dlopen` 可以帮助我们发现 App 动态加载了哪些 SO 文件，这对于分析加壳应用非常有用。

### Hook `dlopen` / `android_dlopen_ext`

```javascript
function hookDlopen() {
  var dlopen = Module.findExportByName(null, "dlopen");
  var android_dlopen_ext = Module.findExportByName(null, "android_dlopen_ext");

  if (dlopen) {
    Interceptor.attach(dlopen, {
      onEnter: function (args) {
        this.path = args[0].readCString();
      },
      onLeave: function (retval) {
        if (this.path) {
          console.log("[dlopen] " + this.path + " -> Handle: " + retval);
          if (this.path.indexOf("libnative-lib.so") >= 0) {
            // Library loaded, ready to hook functions inside it
            console.log("[+] Target library loaded!");
          }
        }
      },
    });
  }

  if (android_dlopen_ext) {
    Interceptor.attach(android_dlopen_ext, {
      onEnter: function (args) {
        this.path = args[0].readCString();
      },
      onLeave: function (retval) {
        if (this.path) {
          console.log(
            "[android_dlopen_ext] " + this.path + " -> Handle: " + retval
          );
        }
      },
    });
  }
}

hookDlopen();
```

---

## 3. 内存操作监控 (memcpy)

监控 `memcpy` 可以帮助我们发现内存中的数据拷贝，特别是在脱壳时可以捕获解密后的 DEX 文件。

### Hook `memcpy`

```javascript
function hookMemcpy() {
  var memcpy = Module.findExportByName("libc.so", "memcpy");

  Interceptor.attach(memcpy, {
    onEnter: function (args) {
      this.dest = args[0];
      this.src = args[1];
      this.n = args[2].toInt32();
    },
    onLeave: function (retval) {
      // Filter by size or content to reduce noise
      if (this.n > 100 && this.n < 200) {
        // Check if source contains specific magic bytes (e.g., ELF header)
        try {
          var magic = this.src.readU32();
          if (magic == 0x464c457f) {
            // .ELF
            console.log("[memcpy] ELF header detected! Size: " + this.n);
            console.log(hexdump(this.src, { length: 32 }));
          }
        } catch (e) {}
      }

      // Check for DEX magic (dex\n035)
      if (this.n > 1000) {
        try {
          var dexMagic = this.src.readUtf8String(4);
          if (dexMagic === "dex\n") {
            console.log("[memcpy] DEX file detected! Size: " + this.n);
            // Dump DEX file
            var dexData = this.src.readByteArray(this.n);
            var filename = "/data/local/tmp/dump_" + Date.now() + ".dex";
            var file = new File(filename, "wb");
            file.write(dexData);
            file.close();
            console.log("[+] DEX dumped to: " + filename);
          }
        } catch (e) {}
      }
    },
  });
}

hookMemcpy();
```

---

## 4. 符号解析监控 (dlsym)

监控 `dlsym` 可以帮助我们发现 App 动态查找了哪些函数，这对于分析混淆代码非常有用。

### Hook `dlsym`

```javascript
function hookDlsym() {
  var dlsym = Module.findExportByName(null, "dlsym");

  Interceptor.attach(dlsym, {
    onEnter: function (args) {
      this.handle = args[0];
      this.symbol = args[1].readCString();
    },
    onLeave: function (retval) {
      if (this.symbol) {
        console.log(
          "[dlsym] Symbol: " + this.symbol + " -> Address: " + retval
        );

        // Hook specific functions when resolved
        if (this.symbol === "encrypt" && !retval.isNull()) {
          console.log("[+] Found encrypt function, hooking...");
          hookNativeFunction(retval, "encrypt");
        }
      }
    },
  });
}

function hookNativeFunction(addr, name) {
  Interceptor.attach(addr, {
    onEnter: function (args) {
      console.log("[" + name + "] called");
      console.log("  arg0: " + args[0]);
      console.log("  arg1: " + args[1]);
    },
    onLeave: function (retval) {
      console.log("  retval: " + retval);
    },
  });
}

hookDlsym();
```

---

## 5. 字符串比较监控 (strcmp)

监控字符串比较函数可以帮助我们发现 App 的校验逻辑，如 Root 检测、调试检测等。

### Hook `strcmp` / `strstr`

```javascript
function hookStringFunctions() {
  // Hook strcmp
  var strcmp = Module.findExportByName("libc.so", "strcmp");
  if (strcmp) {
    Interceptor.attach(strcmp, {
      onEnter: function (args) {
        var s1 = args[0].readCString();
        var s2 = args[1].readCString();

        // Filter for interesting strings
        var keywords = ["root", "su", "magisk", "frida", "xposed", "debug"];
        for (var i = 0; i < keywords.length; i++) {
          if (
            (s1 && s1.toLowerCase().indexOf(keywords[i]) >= 0) ||
            (s2 && s2.toLowerCase().indexOf(keywords[i]) >= 0)
          ) {
            console.log("[strcmp] " + s1 + " VS " + s2);
            break;
          }
        }
      },
    });
  }

  // Hook strstr
  var strstr = Module.findExportByName("libc.so", "strstr");
  if (strstr) {
    Interceptor.attach(strstr, {
      onEnter: function (args) {
        this.haystack = args[0].readCString();
        this.needle = args[1].readCString();
      },
      onLeave: function (retval) {
        if (this.needle && this.needle.toLowerCase().indexOf("frida") >= 0) {
          console.log(
            "[strstr] Searching for: " +
              this.needle +
              " in: " +
              this.haystack.substring(0, 50)
          );
          // Return NULL to bypass detection
          retval.replace(ptr(0));
        }
      },
    });
  }
}

hookStringFunctions();
```

---

## 6. 系统调用监控

监控系统调用可以帮助我们发现 App 的底层行为。

### Hook `syscall`

```javascript
function hookSyscall() {
  var syscall = Module.findExportByName("libc.so", "syscall");

  if (syscall) {
    Interceptor.attach(syscall, {
      onEnter: function (args) {
        var syscallNumber = args[0].toInt32();

        // Common syscall numbers on ARM64
        var syscallNames = {
          56: "openat",
          57: "close",
          63: "read",
          64: "write",
          78: "readlinkat",
          79: "fstatat",
          101: "nanosleep",
          172: "getpid",
          174: "getuid",
        };

        if (syscallNames[syscallNumber]) {
          console.log("[syscall] " + syscallNames[syscallNumber]);
        }
      },
    });
  }
}

hookSyscall();
```

---

## 7. 综合示例：脱壳辅助

结合多个 Hook 点进行脱壳分析。

```javascript
// Comprehensive unpacking helper
function unpackHelper() {
  console.log("[+] Unpacking helper started");

  var dexCount = 0;

  // Hook mmap to catch memory mapping
  var mmap = Module.findExportByName("libc.so", "mmap");
  Interceptor.attach(mmap, {
    onEnter: function (args) {
      this.addr = args[0];
      this.length = args[1].toInt32();
      this.prot = args[2].toInt32();
    },
    onLeave: function (retval) {
      if (this.length > 100000 && this.prot == 5) {
        // PROT_READ | PROT_EXEC
        try {
          var magic = retval.readUtf8String(4);
          if (magic === "dex\n") {
            console.log(
              "[mmap] DEX detected! Size: " + this.length + " Address: " + retval
            );
            dexCount++;
            var filename =
              "/data/local/tmp/unpack_" + dexCount + "_" + Date.now() + ".dex";
            var file = new File(filename, "wb");
            file.write(retval.readByteArray(this.length));
            file.close();
            console.log("[+] Dumped to: " + filename);
          }
        } catch (e) {}
      }
    },
  });

  // Hook dvmDexFileOpenPartial (for Dalvik)
  // Hook art::DexFile::Open (for ART)
  var artDexOpen = Module.findExportByName(
    "libart.so",
    "_ZN3art7DexFile10OpenMemoryEPKhjRKNSt3__112basic_stringIcNS3_11char_traitsIcEENS3_9allocatorIcEEEEjPNS_6MemMapEPKNS_7OatFileEPS9_"
  );
  if (artDexOpen) {
    Interceptor.attach(artDexOpen, {
      onEnter: function (args) {
        console.log("[art::DexFile::OpenMemory] called");
        this.base = args[0];
        this.size = args[1].toInt32();
      },
      onLeave: function (retval) {
        if (this.size > 0) {
          console.log("[+] ART DEX loaded, size: " + this.size);
        }
      },
    });
  }
}

unpackHelper();
```

---

## 总结

Native 层 Hook 是 Android 逆向的核心技能之一。通过 Hook libc 函数（如 open、dlopen、memcpy、strcmp 等），我们可以：

1. 监控文件操作，发现配置文件和动态加载的库
2. 跟踪内存操作，捕获解密后的数据
3. 分析字符串比较，绕过安全检测
4. 进行脱壳分析，提取被保护的 DEX 文件

在实践中，需要根据目标应用的具体行为来选择合适的 Hook 点。
