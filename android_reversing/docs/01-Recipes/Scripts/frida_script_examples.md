# Frida 实战脚本集

> **📚 前置知识**
>
> 本配方涉及以下核心技术，建议先阅读相关章节：
>
> - **[Frida 完整指南](../../02-Tools/Dynamic/frida_guide.md)** - 掌握 Frida 基础语法
> - **[Frida 常用脚本](./frida_common_scripts.md)** - 常用脚本模板

本文档收集了适用于各种常见场景的 Frida 脚本。这些脚本旨在作为即用型模板，您可以根据特定目标进行修改。

---

## 目录

1. [信息收集 (Information Gathering)](#信息收集)
2. [Hook 与修改 (Hooking & Modification)](#hook-与修改)
3. [网络监控与绕过 (Networking)](#网络监控与绕过)
4. [数据持久化与脱壳 (Storage & Dumping)](#数据持久化与脱壳)
5. [反调试与环境检测绕过 (Anti-Analysis)](#反调试与环境检测绕过)
6. [UI 与事件 (UI & Events)](#ui-与事件)

---

### 信息收集

#### 1. 枚举指定类的所有方法

```javascript
// Usage: frida -U -f com.example.app -l list_methods.js
// Replace 'com.example.target class' below
Java.perform(function () {
  var targetClass = "com.example.TargetClass";
  var wrapper = Java.use(targetClass);
  var ownMethods = wrapper.class.getDeclaredMethods();

  console.log("Methods of class " + targetClass + ":");
  ownMethods.forEach(function (method) {
    console.log(method.toString());
  });
});
```

console.log("Listing all loaded classes...");
Java.enumerateLoadedClasses({
onMatch: function(className) {
console.log(className);
},
onComplete: function() {
console.log("Class enumeration complete.");
}
});
});

```
Java.perform(function() {
var TargetClass = Java.use('com.example.app.CryptoUtils');
var methodName = 'encrypt'; // Method name to trace

// Handle method overloads
TargetClass[methodName].overloads.forEach(function(overload) {
overload.implementation = function() {
console.log('\n[+] Called ' + TargetClass.$className + '.' + methodName);

// Print arguments
for (var i = 0; i < arguments.length; i++) {
console.log(' - Argument ' + i + ': ' + arguments[i]);
}

// Call original method
var retval = this[methodName].apply(this, arguments);

// Print return value
console.log(' - Return value: ' + retval);

return retval;
};
});
});

```

Java.perform(function() {
var PremiumUtils = Java.use('com.example.app.PremiumUtils');

PremiumUtils.isUserPremium.implementation = function() {
console.log('[+] Bypassing Premium check...');
return true; // Return true directly
};
});

```

Java.choose('com.example.app.UserInfo', {
onMatch: function(instance) {
console.log('[+] Found UserInfo instance.');
// Directly modify field value
instance.userLevel.value = 99;
console.log(' - Patched userLevel to 99.');
},
onComplete: function() {}
});
});

```

```javascript
// Usage: frida -U --no-pause -f com.example.app -l universal_ssl_unpinning.js
// Source: https://codeshare.frida.re/@pcipolloni/universal-android-ssl-pinning-bypass-with-frida/
setTimeout(function () {
  Java.perform(function () {
    console.log("");
    console.log("[.] Android SSL Pinning Bypass");

    var CertificateFactory = Java.use("java.security.cert.CertificateFactory");
    var FileInputStream = Java.use("java.io.FileInputStream");
    var BufferedInputStream = Java.use("java.io.BufferedInputStream");
    var X509Certificate = Java.use("java.security.cert.X509Certificate");
    var KeyStore = Java.use("java.security.KeyStore");
    var TrustManagerFactory = Java.use("javax.net.ssl.TrustManagerFactory");
    var SSLContext = Java.use("javax.net.ssl.SSLContext");

    // TrustManagerImpl (android > 7)
    try {
      var TrustManagerImpl = Java.use(
        "com.android.org.conscrypt.TrustManagerImpl"
      );
      TrustManagerImpl.verifyChain.implementation = function (
        untrustedChain,
        trustAnchorChain,
        host,
        clientAuth,
        ocspData,
        tlsSctData
      ) {
        console.log(
          "[+] Bypassing TrustManagerImpl verifyChain() for host: " + host
        );
        return untrustedChain;
      };
    } catch (e) {
      console.log("[-] TrustManagerImpl not found. Skipping.");
    }

    // OkHttp3
    try {
      var OkHttpClient = Java.use("okhttp3.OkHttpClient");
      OkHttpClient.Builder.prototype.build.implementation = function () {
        var builder = this.build.call(this);
        console.log("[+] OkHttp3 CertificatePinner removed.");
        builder.certificatePinner.value = null;
        return builder;
      };
    } catch (e) {
      console.log("[-] OkHttp3 not found. Skipping.");
    }

    // TrustManager (universal)
    var TrustManager = Java.use("javax.net.ssl.X509TrustManager");
    var checkServerTrusted = TrustManager.checkServerTrusted;
    checkServerTrusted.overload(
      "java.security.cert.X509Certificate[]",
      "java.lang.String"
    ).implementation = function (chain, authType) {
      console.log(
        "[+] Bypassing TrustManager checkServerTrusted for authType: " +
          authType
      );
      return;
    };
  });
}, 0);
```

Java.perform(function() {
var sharedPrefsEditor = Java.use('android.app.SharedPreferencesImpl$EditorImpl');

sharedPrefsEditor.putString.implementation = function(key, value) {
console.log('[SP Write] key: ' + key + ', value: ' + value);
return this.putString(key, value);
};

var sharedPrefs = Java.use('android.app.SharedPreferencesImpl');
sharedPrefs.getString.implementation = function(key, defValue) {
var value = this.getString(key, defValue);
console.log('[SP Read] key: ' + key + ', value: ' + value);
return value;
};
});

```

SQLiteDatabase.query.overload('java.lang.String', '[Ljava.lang.String;', 'java.lang.String', '[Ljava.lang.String;', 'java.lang.String', 'java.lang.String', 'java.lang.String').implementation = function(table, columns, selection, selectionArgs, groupBy, having, orderBy) {
console.log("\n[SQL Query] Table: " + table);
console.log(" - Columns: " + columns);
console.log(" - Selection: " + selection);
console.log(" - Selection Args: " + selectionArgs);
return this.query(table, columns, selection, selectionArgs, groupBy, having, orderBy);
};

SQLiteDatabase.execSQL.overload('java.lang.String', '[Ljava.lang.Object;').implementation = function(sql, bindArgs) {
console.log("\n[SQL execSQL] SQL: " + sql);
console.log(" - Bind Args: " + bindArgs);
return this.execSQL(sql, bindArgs);
};
});

```

Java.perform(function () {
var RootCheckClass = Java.use('com.example.security.RootUtil'); // Replace with target class

RootCheckClass.isDeviceRooted.implementation = function() {
console.log('[+] Bypassing root check...');
return false;
};
});

```
Debug.isDebuggerConnected.implementation = function() {
console.log('[+] Bypassing isDebuggerConnected check...');
return false;
}
});

```

Java.perform(function() {
var View = Java.use('android.view.View');

View.setOnClickListener.implementation = function(listener) {
var originalListener = listener;
var view = this;

// Create a new listener to wrap the original listener
var newListener = Java.implement(Java.use('android.view.View$OnClickListener'), {
onClick: function(v) {
console.log('[+] View clicked! Class: ' + view.getClass().getName() + ', ID: ' + view.getId());
if (originalListener) {
originalListener.onClick(v); // Call the original click event
}
}
});

// Set the new listener
this.setOnClickListener(newListener);
};
});
