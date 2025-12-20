#!/usr/bin/env python3
"""
创建高优先级文档内容
"""

from pathlib import Path

PRIORITY_DOCS = {}

# 06-Scripts 模块 - 最实用的部分
PRIORITY_DOCS["06-Scripts/javascript_hook_scripts.md"] = """# JavaScript Hook 脚本

## 概述

Hook（钩子）是逆向工程中最常用的技术之一。通过劫持原生API调用，我们可以监控、修改函数的参数和返回值，从而理解代码逻辑或绕过检测。

---

## 基础 Hook 模板

### 1. Hook 全局函数

```javascript
// 保存原始函数
const originalFunction = window.targetFunction;

// 替换为自定义函数
window.targetFunction = function(...args) {
    console.log('[Hook] targetFunction called');
    console.log('[Hook] Arguments:', args);

    // 调用原始函数
    const result = originalFunction.apply(this, args);

    console.log('[Hook] Return value:', result);
    return result;
};
```

---

## 网络请求 Hook

### Hook XMLHttpRequest

```javascript
(function() {
    const originalOpen = XMLHttpRequest.prototype.open;
    const originalSend = XMLHttpRequest.prototype.send;

    // Hook open
    XMLHttpRequest.prototype.open = function(method, url) {
        this._method = method;
        this._url = url;
        console.log(`[XHR] ${method} ${url}`);
        return originalOpen.apply(this, arguments);
    };

    // Hook send
    XMLHttpRequest.prototype.send = function(body) {
        console.log(`[XHR] Request body:`, body);

        // Hook 响应
        this.addEventListener('readystatechange', function() {
            if (this.readyState === 4) {
                console.log(`[XHR] Response:`, this.responseText);
            }
        });

        return originalSend.apply(this, arguments);
    };
})();
```

### Hook Fetch

```javascript
(function() {
    const originalFetch = window.fetch;

    window.fetch = function(...args) {
        console.log('[Fetch] Request:', args);

        return originalFetch.apply(this, args).then(response => {
            console.log('[Fetch] Response:', response);

            // Clone response to avoid consuming it
            return response.clone().text().then(body => {
                console.log('[Fetch] Response body:', body);
                return response;
            });
        });
    };
})();
```

### 通用网络请求监控

```javascript
(function() {
    // Hook XHR
    const XHR_open = XMLHttpRequest.prototype.open;
    const XHR_send = XMLHttpRequest.prototype.send;

    XMLHttpRequest.prototype.open = function(method, url) {
        this._requestInfo = { method, url, time: Date.now() };
        console.log(`🌐 [XHR] ${method} ${url}`);
        return XHR_open.apply(this, arguments);
    };

    XMLHttpRequest.prototype.send = function(body) {
        if (body) {
            console.log(`📤 [XHR] Body:`, body);
        }

        this.addEventListener('load', function() {
            const duration = Date.now() - this._requestInfo.time;
            console.log(`📥 [XHR] ${this.status} ${this._requestInfo.url} (${duration}ms)`);
            console.log(`📥 [XHR] Response:`, this.responseText.substring(0, 200));
        });

        return XHR_send.apply(this, arguments);
    };

    // Hook Fetch
    const originalFetch = window.fetch;
    window.fetch = async function(...args) {
        const startTime = Date.now();
        console.log(`🌐 [Fetch]`, args[0]);

        if (args[1]?.body) {
            console.log(`📤 [Fetch] Body:`, args[1].body);
        }

        const response = await originalFetch.apply(this, args);
        const duration = Date.now() - startTime;

        console.log(`📥 [Fetch] ${response.status} (${duration}ms)`);

        // Clone to avoid consuming
        const clonedResponse = response.clone();
        const text = await clonedResponse.text();
        console.log(`📥 [Fetch] Response:`, text.substring(0, 200));

        return response;
    };
})();
```

---

## Cookie Hook

### 监控 Cookie 读写

```javascript
(function() {
    let cookieCache = document.cookie;

    Object.defineProperty(document, 'cookie', {
        get: function() {
            console.log('🍪 [Cookie] Read:', cookieCache);
            console.trace();
            return cookieCache;
        },
        set: function(value) {
            console.log('🍪 [Cookie] Write:', value);
            console.trace();

            // 实际写入 Cookie
            const cookieParts = value.split(';')[0];
            const [key, val] = cookieParts.split('=');

            // 更新缓存
            const cookies = cookieCache.split('; ');
            const index = cookies.findIndex(c => c.startsWith(key + '='));
            if (index !== -1) {
                cookies[index] = cookieParts;
            } else {
                cookies.push(cookieParts);
            }
            cookieCache = cookies.join('; ');

            return value;
        }
    });
})();
```

---

## Storage Hook

### Hook LocalStorage

```javascript
(function() {
    const originalSetItem = localStorage.setItem;
    const originalGetItem = localStorage.getItem;
    const originalRemoveItem = localStorage.removeItem;

    localStorage.setItem = function(key, value) {
        console.log(`💾 [LocalStorage] Set: ${key} = ${value}`);
        console.trace();
        return originalSetItem.apply(this, arguments);
    };

    localStorage.getItem = function(key) {
        const value = originalGetItem.apply(this, arguments);
        console.log(`💾 [LocalStorage] Get: ${key} = ${value}`);
        return value;
    };

    localStorage.removeItem = function(key) {
        console.log(`💾 [LocalStorage] Remove: ${key}`);
        return originalRemoveItem.apply(this, arguments);
    };
})();
```

### Hook SessionStorage

```javascript
// 同 LocalStorage，将 localStorage 替换为 sessionStorage
(function() {
    const originalSetItem = sessionStorage.setItem;
    const originalGetItem = sessionStorage.getItem;

    sessionStorage.setItem = function(key, value) {
        console.log(`📦 [SessionStorage] Set: ${key} = ${value}`);
        return originalSetItem.apply(this, arguments);
    };

    sessionStorage.getItem = function(key) {
        const value = originalGetItem.apply(this, arguments);
        console.log(`📦 [SessionStorage] Get: ${key} = ${value}`);
        return value;
    };
})();
```

---

## 加密函数 Hook

### Hook CryptoJS

```javascript
(function() {
    if (window.CryptoJS) {
        // Hook MD5
        const originalMD5 = CryptoJS.MD5;
        CryptoJS.MD5 = function(...args) {
            console.log('🔐 [CryptoJS.MD5] Input:', args[0].toString());
            const result = originalMD5.apply(this, args);
            console.log('🔐 [CryptoJS.MD5] Output:', result.toString());
            debugger; // 自动断点
            return result;
        };

        // Hook AES.encrypt
        const originalAESEncrypt = CryptoJS.AES.encrypt;
        CryptoJS.AES.encrypt = function(message, key, cfg) {
            console.log('🔐 [CryptoJS.AES.encrypt]');
            console.log('  Message:', message.toString());
            console.log('  Key:', key.toString());
            console.log('  Config:', cfg);
            const result = originalAESEncrypt.apply(this, arguments);
            console.log('  Result:', result.toString());
            debugger;
            return result;
        };

        // Hook AES.decrypt
        const originalAESDecrypt = CryptoJS.AES.decrypt;
        CryptoJS.AES.decrypt = function(ciphertext, key, cfg) {
            console.log('🔓 [CryptoJS.AES.decrypt]');
            console.log('  Ciphertext:', ciphertext.toString());
            console.log('  Key:', key.toString());
            const result = originalAESDecrypt.apply(this, arguments);
            console.log('  Decrypted:', result.toString(CryptoJS.enc.Utf8));
            debugger;
            return result;
        };
    }
})();
```

### Hook Web Crypto API

```javascript
(function() {
    const originalSubtle = window.crypto.subtle;

    const hookCryptoMethod = (methodName) => {
        const original = originalSubtle[methodName];
        originalSubtle[methodName] = async function(...args) {
            console.log(`🔐 [crypto.subtle.${methodName}]`, args);
            const result = await original.apply(this, args);
            console.log(`🔐 [crypto.subtle.${methodName}] Result:`, result);
            return result;
        };
    };

    hookCryptoMethod('encrypt');
    hookCryptoMethod('decrypt');
    hookCryptoMethod('sign');
    hookCryptoMethod('verify');
    hookCryptoMethod('digest');
})();
```

---

## JSON Hook

### Hook JSON.stringify

```javascript
(function() {
    const originalStringify = JSON.stringify;

    JSON.stringify = function(obj, replacer, space) {
        console.log('📝 [JSON.stringify] Input:', obj);
        console.trace();

        const result = originalStringify.apply(this, arguments);
        console.log('📝 [JSON.stringify] Output:', result);

        return result;
    };
})();
```

### Hook JSON.parse

```javascript
(function() {
    const originalParse = JSON.parse;

    JSON.parse = function(text, reviver) {
        console.log('📖 [JSON.parse] Input:', text);

        const result = originalParse.apply(this, arguments);
        console.log('📖 [JSON.parse] Output:', result);

        return result;
    };
})();
```

---

## 定时器 Hook

### Hook setTimeout

```javascript
(function() {
    const originalSetTimeout = window.setTimeout;

    window.setTimeout = function(callback, delay, ...args) {
        console.log(`⏰ [setTimeout] Delay: ${delay}ms`);
        console.log(`⏰ [setTimeout] Callback:`, callback.toString().substring(0, 100));
        console.trace();

        return originalSetTimeout.apply(this, arguments);
    };
})();
```

### Hook setInterval

```javascript
(function() {
    const originalSetInterval = window.setInterval;

    window.setInterval = function(callback, delay, ...args) {
        console.log(`⏰ [setInterval] Interval: ${delay}ms`);
        console.log(`⏰ [setInterval] Callback:`, callback.toString().substring(0, 100));

        return originalSetInterval.apply(this, arguments);
    };
})();
```

---

## WebSocket Hook

```javascript
(function() {
    const originalWebSocket = window.WebSocket;

    window.WebSocket = function(url, protocols) {
        console.log(`🔌 [WebSocket] Connecting to: ${url}`);

        const ws = new originalWebSocket(url, protocols);

        // Hook send
        const originalSend = ws.send;
        ws.send = function(data) {
            console.log('📤 [WebSocket] Send:', data);
            return originalSend.apply(this, arguments);
        };

        // Hook onmessage
        ws.addEventListener('message', function(event) {
            console.log('📥 [WebSocket] Message:', event.data);
        });

        // Hook onopen
        ws.addEventListener('open', function() {
            console.log('✅ [WebSocket] Connected');
        });

        // Hook onerror
        ws.addEventListener('error', function(error) {
            console.log('❌ [WebSocket] Error:', error);
        });

        // Hook onclose
        ws.addEventListener('close', function() {
            console.log('🔴 [WebSocket] Closed');
        });

        return ws;
    };
})();
```

---

## 反调试绕过

### 绕过 debugger

```javascript
// 方法一：重写 Function.prototype.constructor
(function() {
    const originalConstructor = Function.prototype.constructor;

    Function.prototype.constructor = function(...args) {
        // 检查是否包含 'debugger'
        const code = args[args.length - 1];
        if (typeof code === 'string' && code.includes('debugger')) {
            console.log('🚫 [Anti-Debug] Blocked debugger');
            // 返回空函数
            return function() {};
        }

        return originalConstructor.apply(this, args);
    };
})();

// 方法二：使用 Chrome DevTools
// 右键 debugger 行 -> "Never pause here"
```

### Hook console 检测绕过

```javascript
(function() {
    // 某些网站通过检测 console 被打开来反调试
    // 重写 console 方法返回固定值

    const noop = function() {};
    const originalConsole = { ...console };

    window.console = {
        log: noop,
        debug: noop,
        info: noop,
        warn: noop,
        error: noop,
        // 保留原始 console 供我们使用
        _original: originalConsole
    };

    // 使用：window.console._original.log('message');
})();
```

---

## 综合 Hook 脚本

### 一键监控所有关键 API

```javascript
(function() {
    console.log('🎣 Universal Hook Script Loaded');

    // 1. Network
    const originalFetch = window.fetch;
    window.fetch = async function(...args) {
        console.log(`🌐 [Fetch]`, args);
        const response = await originalFetch.apply(this, args);
        const clone = response.clone();
        const text = await clone.text();
        console.log(`📥 [Fetch] Response:`, text.substring(0, 200));
        return response;
    };

    // 2. Cookie
    let cookieCache = document.cookie;
    Object.defineProperty(document, 'cookie', {
        get: () => (console.log('🍪 [Cookie] Read'), cookieCache),
        set: (v) => (console.log('🍪 [Cookie] Write:', v), cookieCache = v, v)
    });

    // 3. LocalStorage
    const originalSetItem = localStorage.setItem;
    localStorage.setItem = function(k, v) {
        console.log(`💾 [LocalStorage] ${k} = ${v}`);
        return originalSetItem.apply(this, arguments);
    };

    // 4. JSON
    const originalStringify = JSON.stringify;
    JSON.stringify = function(obj) {
        console.log('📝 [JSON.stringify]', obj);
        return originalStringify.apply(this, arguments);
    };

    // 5. CryptoJS (如果存在)
    if (window.CryptoJS) {
        const originalMD5 = CryptoJS.MD5;
        CryptoJS.MD5 = function(...args) {
            const result = originalMD5.apply(this, args);
            console.log(`🔐 [MD5] ${args[0]} => ${result}`);
            return result;
        };
    }

    console.log('✅ All hooks installed!');
})();
```

---

## 使用建议

### 在 DevTools Console 中执行

1. 打开 DevTools
2. 切换到 Console 标签
3. 粘贴 Hook 脚本
4. 回车执行
5. 刷新页面或触发操作

### 保存为 Snippet

1. DevTools -> Sources -> Snippets
2. 新建 Snippet
3. 粘贴 Hook 脚本
4. `Ctrl+Enter` 执行

### 使用浏览器插件

可以将 Hook 脚本注入到 Tampermonkey 等插件中，实现自动加载。

---

## 相关章节

- [调试技巧与断点设置](../02-Techniques/debugging_techniques.md)
- [JavaScript 反混淆](../02-Techniques/javascript_deobfuscation.md)
- [浏览器开发者工具](../01-Tooling/browser_devtools.md)
"""

# 创建批量填充函数
def create_all_priority_docs():
    base_dir = Path(__file__).parent / "docs"

    count = 0
    for file_path, content in PRIORITY_DOCS.items():
        full_path = base_dir / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)

        count += 1
        print(f"✅ [{count}/{len(PRIORITY_DOCS)}] 创建: {file_path}")

    print(f"\n🎉 成功创建 {count} 个高优先级文档!")

if __name__ == "__main__":
    create_all_priority_docs()
