# Xposed 框架入门

Xposed 是一个在 Android 平台上广受欢迎的动态代码 Hook 框架。与 Frida 主要用于实时、临时的分析不同，Xposed 旨在对系统和应用进行**永久性**的修改。它通过替换一个核心系统进程 (`app_process`)，在应用启动时加载自定义模块，从而实现对任意方法的高效 Hook。

## 目录

- [Xposed 框架入门](#xposed-框架入门)
  - [Xposed 是一个在 Android 平台上广受欢迎的动态代码 Hook 框架。与 Frida 主要用于实时、临时的分析不同，Xposed 旨在对系统和应用进行**永久性**的修改。它通过替换一个核心系统进程 (`app_process`)，在应用启动时加载自定义模块，从而实现对任意方法的高效 Hook。](#xposed-是一个在-android-平台上广受欢迎的动态代码-hook-框架与-frida-主要用于实时临时的分析不同xposed-旨在对系统和应用进行永久性的修改它通过替换一个核心系统进程-app_process在应用启动时加载自定义模块从而实现对任意方法的高效-hook)
  - [目录](#目录)
    - [核心原理](#核心原理)
    - [Xposed vs. Frida](#xposed-vs-frida)
    - [环境搭建 (以 LSPosed 为例)](#环境搭建-以-lsposed-为例)
    - [开发第一个 Xposed 模块](#开发第一个-xposed-模块)
      - [1. 项目结构](#1-项目结构)

---

### 核心原理

Xposed 的工作基础是它能够在 Android 系统启动的核心阶段介入，并将自己的代码注入到每一个应用程序进程中。

1. **Zygote 注入**: Xposed 通过替换系统原生的 `/system/bin/app_process` 可执行文件，实现了对 Zygote 进程（所有 App 进程的父进程）的控制。当 Zygote 启动时，会加载 Xposed 的核心 Jar 包（Xposed Bridge）。
2. **方法 Hook**: 当模块需要 Hook 一个方法时，Xposed 会在运行时深入虚拟机（ART）内部，直接修改该方法在内存中的数据结构。它将目标方法"伪装"成一个 Native 方法，并将其执行入口指向 Xposed 的一个通用桥接函数。
3. **执行流重定向**: 当 App 调用被 Hook 的方法时，执行流会先进入 Xposed 的桥接函数，在这里 Xposed 依次调用所有模块的 `beforeHookedMethod`，然后调用原方法，最后再调用所有模块的 `afterHookedMethod`，从而实现对方法调用的完全控制。

> 想要更深入地了解其实现细节，请参考 [**Xposed Internals: A Deep Dive**](./xposed_internals.md)。

---

### Xposed vs. Frida

| 特性         | Xposed                                                       | Frida                                                      |
| :----------- | :----------------------------------------------------------- | :--------------------------------------------------------- |
| **核心目标** | **永久性修改**: 对应用或系统功能进行长期、稳定的修改。       | **动态分析**: 用于实时、临时的分析、逆向和快速原型验证。   |
| **运行环境** | 需要 Root，通过刷入框架修改系统，**需要重启**。              | 通常需要 Root，但无需重启，通过 `frida-server` 动态附加。  |
| **开发语言** | **Java**: 模块是标准的 Android APK。                         | **JavaScript**: 主要使用 JS 编写脚本，也支持其他语言绑定。 |
| **开发周期** | 较慢：编码 → 编译 APK → 安装 → 激活 → 重启 App/设备 → 测试。 | 极快：编写/修改脚本 → 附加进程 → 立即看到结果。            |
| **稳定性**   | 极高。为长期运行设计，一旦激活，随 App 启动自动生效。        | 较低。依赖于 `frida-server` 和附加会话，App 重启后失效。   |
| **适用场景** | UI 定制、功能增强、去广告、隐私控制（如伪造数据）。          | SSL Pinning 绕过、算法逆向、协议分析、漏洞挖掘。           |

- **总结**: 如果你想写一个"插件"来永久性地改变一个 App 的功能，用 Xposed；如果你想分析一个 App 的内部行为，用 Frida。

---

### 环境搭建 (以 LSPosed 为例)

当前，LSPosed 是社区中最主流、兼容性最好的 Xposed 框架实现，它基于 Riru/Zygisk，以 Magisk 模块的形式工作。

1. **前提条件**:
   - 一台已解锁并刷入 Magisk 的 Android 设备（Android 8.1+）。
2. **安装 Riru 或启用 Zygisk**:
   - **Zygisk (推荐)**: 在 Magisk Manager 中，进入设置，开启 `Zygisk` 选项。
   - **Riru (备选)**: 在 Magisk Manager 的"模块"部分，搜索并安装 `Riru` 模块。
3. **安装 LSPosed**:
   - 从 [LSPosed 的 GitHub Releases](https://github.com/LSPosed/LSPosed/releases) 页面下载最新的 Zygisk 版本 ZIP 包。
   - 在 Magisk Manager 的"模块"页，选择"从本地安装"，然后选中下载的 LSPosed ZIP 包。
   - 安装完成后，点击右下角的"重启"按钮。
4. **验证安装**:
   - 重启后，桌面上会出现 LSPosed 的管理程序图标。
   - 打开 LSPosed，如果状态显示为"已激活"，则表示框架安装成功。

---

### 开发第一个 Xposed 模块

我们将创建一个简单的模块，来 Hook 系统的时钟，在后面加上一个小尾巴。

#### 1. 项目结构

- 在 Android Studio 中创建一个新的、空的 Android 项目。

- 在 app 的 `build.gradle` 文件中添加 Xposed API 依赖：
  ```groovy
  dependencies {
  // ... other dependencies
  compileOnly 'de.robv.android.xposed:api:82'
  // 'compileOnly' is used because the framework is already provided by the system, only needed at compile time
  }
  ```

* 创建一个新的 Java 类，例如 `ClockHook`，并让它实现 `IXposedHookLoadPackage` 接口。

```java
package com.example.myxposedmodule;

import de.robv.android.xposed.IXposedHookLoadPackage;
import de.robv.android.xposed.XC_MethodHook;
import de.robv.android.xposed.XposedBridge;
import de.robv.android.xposed.XposedHelpers;
import de.robv.android.xposed.callbacks.XC_LoadPackage.LoadPackageParam;
import android.widget.TextView;

public class ClockHook implements IXposedHookLoadPackage {
@Override
public void handleLoadPackage(final LoadPackageParam lpparam) throws Throwable {
// We only care about system UI
if (!lpparam.packageName.equals("com.android.systemui")) {
return;
}

XposedBridge.log("Loaded app: " + lpparam.packageName);

// Find and Hook the clock update class and method
// (Note: class names and method names may differ across Android versions)
XposedHelpers.findAndHookMethod(
"com.android.systemui.statusbar.policy.Clock", // Class name
lpparam.classLoader, // ClassLoader
"updateClock", // Method name
new XC_MethodHook() { // Hook callback
@Override
protected void afterHookedMethod(MethodHookParam param) throws Throwable {
super.afterHookedMethod(param);
TextView clockView = (TextView) param.thisObject;
String originalTime = clockView.getText().toString();
String newTime = originalTime + " ";
clockView.setText(newTime);
XposedBridge.log("Clock hooked! New time: " + newTime);
}
}
);
}
}
```

- 在 `app/src/main/AndroidManifest.xml` 的 `<application>` 标签内，添加 meta-data 来声明这是一个 Xposed 模块。

```xml
<meta-data
android:name="xposedmodule"
android:value="true" />
<meta-data
android:name="xposeddescription"
android:value="This is an example module that adds a tail to system clock" />
<meta-data
android:name="xposedminversion"
android:value="52" />

```

- 在 `assets` 文件夹内，创建一个名为 `xposed_init` 的文本文件。

- 在 `xposed_init` 文件中，写入你的 Hook 类的完整路径：

  ```text
  com.example.myxposedmodule.ClockHook
  ```

1. **构建 APK**: 在 Android Studio 中构建你的项目，生成 APK。
2. **安装 APK**: 将 APK 安装到你的测试设备上。
3. **激活模块**:
   - 打开 LSPosed Manager。
   - 进入"模块"部分，找到你刚刚安装的模块。
   - 点击它，然后**启用**模块。
   - 在作用域列表中，勾选"**SystemUI**"。
4. **重启目标进程**:
   - 在 LSPosed 的状态页右上角，点击三个点菜单，选择"软重启"或"重启 SystemUI"，或者直接重启手机。
5. **查看效果**: 查看你的状态栏时钟，它现在应该带有一个 小尾巴了！你也可以在 LSPosed 的日志中看到 `XposedBridge.log` 输出的信息。

---

### 核心 API 详解

#### `IXposedHookLoadPackage`

这是所有模块的入口点。它只有一个方法 `handleLoadPackage(LoadPackageParam lpparam)`。当任何一个 App 启动时，Xposed 都会调用这个方法，并传入 `lpparam` 对象，其中包含了非常有用的信息：

- `lpparam.packageName`: 当前加载的 App 的包名。

- `lpparam.processName`: 当前进程名。

- `lpparam.classLoader`: 当前 App 的 ClassLoader，这是 Hook App 内部类的**必需品**。

#### `XposedHelpers`

一个包含大量静态辅助方法的工具类，极大简化了反射操作。

- `findAndHookMethod(String className, ClassLoader classLoader, String methodName, Object... parameterTypesAndCallback)`: 最核心的 Hook 方法。最后一个参数必须是 `XC_MethodHook` 回调。

- `findClass(String className, ClassLoader classLoader)`: 查找一个类。

- `getObjectField(Object obj, String fieldName)` / `setObjectField(Object obj, String fieldName, Object value)`: 获取/设置对象的成员变量。

- `callMethod(Object obj, String methodName, Object... args)`: 调用一个对象的方法。

- `getStaticObjectField(...)` / `callStaticMethod(...)`: 用于操作静态变量和静态方法。

#### `XC_MethodHook`

这是一个抽象类，你需要继承它并重写它的两个核心方法。

- `beforeHookedMethod(MethodHookParam param)`: 在原方法执行**前**被调用。

- `afterHookedMethod(MethodHookParam param)`: 在原方法执行**后**被调用。

这两个方法都接收一个 `MethodHookParam` 对象，它包含了本次方法调用的所有上下文信息：

- `param.thisObject`: `this` 指针，即方法所属的对象实例。

- `param.args`: `Object[]` 数组，包含了方法被调用时的所有参数。你可以在 `beforeHookedMethod` 中修改它。

- `param.getResult()`: 获取原方法的返回值。只能在 `afterHookedMethod` 中调用。

- `param.setResult(Object result)`: 设置一个新的返回值。如果在 `beforeHookedMethod` 中调用，原方法将**不会被执行**。如果在 `afterHookedMethod` 中调用，它会覆盖原方法的返回值。

- `param.getThrowable()` / `param.setThrowable(Throwable t)`: 用于获取/设置方法抛出的异常。

---

### 常见应用场景

- **UI 定制**: 修改系统或应用的外观，如状态栏、通知、锁屏等（代表作：`GravityBox`）。

- **功能增强**: 为应用添加原生不支持的功能，如为微信添加防撤回、自动抢红包功能。

- **去除限制**: 破解应用的付费功能、去除截图限制、去除广告等。

- **隐私保护**: 拦截应用获取敏感信息的请求（如定位、联系人、设备 ID），并返回虚假或空数据（代表作：`XPrivacyLua`）。

- **安全分析**:
- 绕过 SSL Pinning（尽管 Frida 更灵活）。

- 禁用 Root 检测或反调试机制。

- 日志记录：打印关键方法的参数和返回值，分析应用行为。
