---
title: "Android 沙箱技术与实现指南"
date: 2025-04-27
tags: ["Native层", "签名验证", "SSL Pinning", "代理池", "DEX", "高级"]
weight: 10
---

# Android 沙箱技术与实现指南

Android 沙箱技术，通常也被称为"虚拟化引擎"或"App 多开框架"，是一种在单个 Android 设备上创建隔离环境以运行其他应用程序的技术。它允许一个"宿主"应用程序在自己的进程空间内加载并运行一个"插件"应用程序，同时对插件应用的所有系统交互进行拦截和管理。

**核心应用场景**：应用多开、无感知隐私保护、自动化测试、免安装运行 App、安全分析。

---

## 1. 核心概念：沙箱 vs. 虚拟机

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        传统虚拟机 (VM)                                   │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐         │
│  │   Guest App 1   │  │   Guest App 2   │  │   Guest App 3   │         │
│  ├─────────────────┤  ├─────────────────┤  ├─────────────────┤         │
│  │  Guest Android  │  │  Guest Android  │  │  Guest Android  │         │
│  │     Kernel      │  │     Kernel      │  │     Kernel      │         │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘         │
│           │                    │                    │                   │
│           └────────────────────┼────────────────────┘                   │
│                                │                                        │
│                    ┌───────────┴───────────┐                           │
│                    │   Hypervisor (QEMU)   │                           │
│                    └───────────┬───────────┘                           │
│                                │                                        │
│                    ┌───────────┴───────────┐                           │
│                    │     Host Kernel       │                           │
│                    └───────────────────────┘                           │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                        Android 沙箱 (进程内虚拟化)                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                        宿主 App 进程                               │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐               │ │
│  │  │ Plugin App1 │  │ Plugin App2 │  │ Plugin App3 │               │ │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘               │ │
│  │         │                │                │                       │ │
│  │         └────────────────┼────────────────┘                       │ │
│  │                          │                                        │ │
│  │              ┌───────────┴───────────┐                           │ │
│  │              │   沙箱框架 (Hook层)    │  ◄── API 拦截与重定向      │ │
│  │              │  - Binder Proxy       │                           │ │
│  │              │  - ClassLoader        │                           │ │
│  │              │  - Resources          │                           │ │
│  │              └───────────┬───────────┘                           │ │
│  │                          │                                        │ │
│  └──────────────────────────┼────────────────────────────────────────┘ │
│                             │                                          │
│              ┌──────────────┴──────────────┐                          │
│              │    Android Framework        │                          │
│              │    (AMS, PMS, WMS...)       │                          │
│              └──────────────┬──────────────┘                          │
│                             │                                          │
│              ┌──────────────┴──────────────┐                          │
│              │       Linux Kernel          │                          │
│              └─────────────────────────────┘                          │
└─────────────────────────────────────────────────────────────────────────┘
```

| 特性 | 虚拟机 (VM) | Android 沙箱 |
|-----|------------|-------------|
| 隔离级别 | 内核级隔离 | 进程内隔离 |
| 资源开销 | 非常高 (GB级内存) | 低 (共享系统资源) |
| 启动速度 | 慢 (分钟级) | 快 (秒级) |
| 兼容性 | 完美 | 需要适配 |
| 实现复杂度 | 依赖成熟虚拟化技术 | 需要大量 Hook |

---

## 2. 沙箱实现原理详解

实现一个 Android 沙箱需要解决四大核心问题：

```
┌─────────────────────────────────────────────────────────────────┐
│                    沙箱框架核心组件                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│   │  ClassLoader │    │  Stub组件   │    │  Resources  │        │
│   │   Manager   │    │   Manager   │    │   Manager   │        │
│   └──────┬──────┘    └──────┬──────┘    └──────┬──────┘        │
│          │                  │                  │                │
│          └──────────────────┼──────────────────┘                │
│                             │                                   │
│                    ┌────────┴────────┐                         │
│                    │   Hook Manager  │                         │
│                    │  (Binder Proxy) │                         │
│                    └────────┬────────┘                         │
│                             │                                   │
│          ┌──────────────────┼──────────────────┐               │
│          │                  │                  │               │
│   ┌──────┴──────┐   ┌──────┴──────┐   ┌──────┴──────┐        │
│   │     AMS     │   │     PMS     │   │   Other     │        │
│   │    Hook     │   │    Hook     │   │   Hooks     │        │
│   └─────────────┘   └─────────────┘   └─────────────┘        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.1 类加载 (Class Loading)

由于插件 App 并未被系统"安装"，其代码不能通过常规的 `PathClassLoader` 加载。

#### 原理图

```
┌─────────────────────────────────────────────────────────────┐
│                    类加载流程                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Plugin APK                                                │
│   (/data/data/host/files/plugin.apk)                       │
│        │                                                    │
│        ▼                                                    │
│   ┌─────────────────┐                                      │
│   │  DexClassLoader │  ◄── 指定 APK 路径和 ODEX 输出目录    │
│   │                 │                                      │
│   │  - dexPath      │  = plugin.apk 路径                   │
│   │  - optDir       │  = 宿主私有目录 (存放优化后的 dex)    │
│   │  - libPath      │  = so 库路径                         │
│   │  - parent       │  = 宿主 ClassLoader                  │
│   └────────┬────────┘                                      │
│            │                                                │
│            ▼                                                │
│   ┌─────────────────┐                                      │
│   │  loadClass()    │                                      │
│   │                 │                                      │
│   │  "com.plugin    │  ──►  Plugin Activity 实例           │
│   │   .MainActivity"│                                      │
│   └─────────────────┘                                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### 代码实现

```java
/**
 * PluginClassLoaderManager.java
 * 插件类加载器管理
 */
public class PluginClassLoaderManager {

    private static final String TAG = "PluginClassLoader";

    // 缓存已加载插件的 ClassLoader
    private final Map<String, DexClassLoader> classLoaderCache = new HashMap<>();

    private final Context hostContext;

    public PluginClassLoaderManager(Context hostContext) {
        this.hostContext = hostContext;
    }

    /**
     * 为插件创建 DexClassLoader
     *
     * @param pluginApkPath 插件 APK 的完整路径
     * @param pluginId      插件唯一标识
     * @return DexClassLoader 实例
     */
    public DexClassLoader createClassLoader(String pluginApkPath, String pluginId) {
        // 检查缓存
        if (classLoaderCache.containsKey(pluginId)) {
            Log.d(TAG, "Using cached ClassLoader for: " + pluginId);
            return classLoaderCache.get(pluginId);
        }

        // 创建优化后的 DEX 输出目录
        // 注意: Android 8.0+ 推荐使用 null，系统会自动选择目录
        File optDir = hostContext.getDir("plugin_dex_" + pluginId, Context.MODE_PRIVATE);

        // 获取插件的 native library 路径
        String libPath = extractNativeLibs(pluginApkPath, pluginId);

        // 创建 DexClassLoader
        // 关键参数:
        // - dexPath: 插件 APK 路径
        // - optimizedDirectory: DEX 优化输出目录 (Android 8.0+ 可为 null)
        // - librarySearchPath: Native 库搜索路径
        // - parent: 父 ClassLoader (使用宿主的 ClassLoader)
        DexClassLoader classLoader = new DexClassLoader(
                pluginApkPath,
                optDir.getAbsolutePath(),
                libPath,
                hostContext.getClassLoader()  // 重要: 设置父加载器
        );

        // 缓存
        classLoaderCache.put(pluginId, classLoader);

        Log.d(TAG, "Created ClassLoader for plugin: " + pluginId);
        Log.d(TAG, "  APK Path: " + pluginApkPath);
        Log.d(TAG, "  Opt Dir: " + optDir.getAbsolutePath());
        Log.d(TAG, "  Lib Path: " + libPath);

        return classLoader;
    }

    /**
     * 从插件 APK 中提取 native 库
     */
    private String extractNativeLibs(String apkPath, String pluginId) {
        File libDir = hostContext.getDir("plugin_lib_" + pluginId, Context.MODE_PRIVATE);

        try {
            // 获取设备 ABI
            String abi = Build.SUPPORTED_ABIS[0];  // 如 "arm64-v8a"

            ZipFile zipFile = new ZipFile(apkPath);
            Enumeration<? extends ZipEntry> entries = zipFile.entries();

            while (entries.hasMoreElements()) {
                ZipEntry entry = entries.nextElement();
                String name = entry.getName();

                // 查找匹配的 native 库
                if (name.startsWith("lib/" + abi + "/") && name.endsWith(".so")) {
                    String soName = name.substring(name.lastIndexOf('/') + 1);
                    File outFile = new File(libDir, soName);

                    // 解压 so 文件
                    try (InputStream in = zipFile.getInputStream(entry);
                         FileOutputStream out = new FileOutputStream(outFile)) {
                        byte[] buffer = new byte[8192];
                        int len;
                        while ((len = in.read(buffer)) != -1) {
                            out.write(buffer, 0, len);
                        }
                    }

                    Log.d(TAG, "Extracted native lib: " + soName);
                }
            }

            zipFile.close();
        } catch (IOException e) {
            Log.e(TAG, "Failed to extract native libs", e);
        }

        return libDir.getAbsolutePath();
    }

    /**
     * 加载插件中的类
     */
    public Class<?> loadPluginClass(String pluginId, String className)
            throws ClassNotFoundException {

        DexClassLoader classLoader = classLoaderCache.get(pluginId);
        if (classLoader == null) {
            throw new IllegalStateException("Plugin not loaded: " + pluginId);
        }

        return classLoader.loadClass(className);
    }

    /**
     * 通过反射创建插件对象实例
     */
    @SuppressWarnings("unchecked")
    public <T> T createPluginInstance(String pluginId, String className, Class<T> expectedType)
            throws Exception {

        Class<?> clazz = loadPluginClass(pluginId, className);

        if (!expectedType.isAssignableFrom(clazz)) {
            throw new ClassCastException(className + " is not a " + expectedType.getName());
        }

        return (T) clazz.getDeclaredConstructor().newInstance();
    }
}
```

### 2.2 组件生命周期管理 (Component Lifecycle)

插件 App 的组件（Activity, Service 等）并没有在宿主 App 的 `AndroidManifest.xml` 中注册，因此无法被系统直接启动。

#### 占坑原理图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Activity 启动流程对比                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  【正常启动】                                                            │
│                                                                         │
│  App ──► startActivity(TargetActivity) ──► AMS ──► 启动 TargetActivity  │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  【沙箱启动 - 占坑机制】                                                  │
│                                                                         │
│  Step 1: 发起请求                                                       │
│  ┌──────────┐                                                          │
│  │ Plugin   │  startActivity(PluginActivity)                           │
│  │ App      │  ────────────────┐                                       │
│  └──────────┘                  │                                       │
│                                ▼                                       │
│  Step 2: Hook 拦截      ┌─────────────┐                                │
│                         │  AMS Hook   │  检测到插件 Intent              │
│                         │ (动态代理)   │                                │
│                         └──────┬──────┘                                │
│                                │                                       │
│  Step 3: Intent 替换           ▼                                       │
│                         ┌─────────────┐                                │
│                         │ 替换为      │                                │
│                         │ StubActivity│                                │
│                         │ Intent      │                                │
│                         └──────┬──────┘                                │
│                                │                                       │
│  Step 4: 系统启动              ▼                                       │
│                         ┌─────────────┐                                │
│                         │    AMS      │  正常启动流程                   │
│                         └──────┬──────┘                                │
│                                │                                       │
│  Step 5: 还原与委托            ▼                                       │
│                         ┌─────────────────────────────────┐            │
│                         │         StubActivity            │            │
│                         │  onCreate() {                   │            │
│                         │    // 从 Intent 恢复插件信息     │            │
│                         │    // 创建 PluginActivity 实例  │            │
│                         │    // 委托生命周期调用          │            │
│                         │  }                              │            │
│                         └─────────────────────────────────┘            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

#### AndroidManifest.xml 占坑配置

```xml
<!-- 宿主 App 的 AndroidManifest.xml -->
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.sandbox.host">

    <application>
        <!-- 宿主自己的组件 -->
        <activity android:name=".MainActivity" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <!-- ========== 占坑 Activity (Stub Activities) ========== -->

        <!-- 标准模式 -->
        <activity android:name=".stub.StubActivity$Standard1"
            android:launchMode="standard"
            android:theme="@style/Theme.AppCompat.Light" />
        <activity android:name=".stub.StubActivity$Standard2"
            android:launchMode="standard" />

        <!-- SingleTop 模式 -->
        <activity android:name=".stub.StubActivity$SingleTop1"
            android:launchMode="singleTop" />

        <!-- SingleTask 模式 -->
        <activity android:name=".stub.StubActivity$SingleTask1"
            android:launchMode="singleTask" />

        <!-- SingleInstance 模式 -->
        <activity android:name=".stub.StubActivity$SingleInstance1"
            android:launchMode="singleInstance" />

        <!-- 透明主题 (用于对话框类 Activity) -->
        <activity android:name=".stub.StubActivity$Translucent1"
            android:theme="@android:style/Theme.Translucent.NoTitleBar" />

        <!-- ========== 占坑 Service ========== -->
        <service android:name=".stub.StubService$Service1" />
        <service android:name=".stub.StubService$Service2" />

        <!-- ========== 占坑 ContentProvider ========== -->
        <provider
            android:name=".stub.StubContentProvider"
            android:authorities="com.sandbox.host.stub.provider"
            android:exported="false" />

        <!-- ========== 占坑 BroadcastReceiver (静态注册) ========== -->
        <receiver android:name=".stub.StubReceiver$Receiver1" />

    </application>
</manifest>
```

#### StubActivity 实现

```java
/**
 * StubActivity.java
 * 占坑 Activity 基类 - 负责委托生命周期给插件 Activity
 */
public class StubActivity extends Activity {

    private static final String TAG = "StubActivity";

    // 存储原始插件 Intent 的 Key
    public static final String EXTRA_PLUGIN_INTENT = "sandbox_plugin_intent";
    public static final String EXTRA_PLUGIN_ID = "sandbox_plugin_id";
    public static final String EXTRA_PLUGIN_CLASS = "sandbox_plugin_class";

    // 被代理的插件 Activity
    private Activity pluginActivity;

    // 插件的 Resources
    private Resources pluginResources;

    // 插件的 ClassLoader
    private ClassLoader pluginClassLoader;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // 从 Intent 中恢复插件信息
        Intent intent = getIntent();
        String pluginId = intent.getStringExtra(EXTRA_PLUGIN_ID);
        String pluginClassName = intent.getStringExtra(EXTRA_PLUGIN_CLASS);
        Intent pluginIntent = intent.getParcelableExtra(EXTRA_PLUGIN_INTENT);

        Log.d(TAG, "StubActivity onCreate");
        Log.d(TAG, "  Plugin ID: " + pluginId);
        Log.d(TAG, "  Plugin Class: " + pluginClassName);

        try {
            // 获取插件的 ClassLoader 和 Resources
            PluginManager pm = PluginManager.getInstance();
            pluginClassLoader = pm.getPluginClassLoader(pluginId);
            pluginResources = pm.getPluginResources(pluginId);

            // 创建插件 Activity 实例
            Class<?> pluginClass = pluginClassLoader.loadClass(pluginClassName);
            pluginActivity = (Activity) pluginClass.getDeclaredConstructor().newInstance();

            // 注入上下文 (关键步骤)
            injectContext(pluginActivity, pluginIntent);

            // 调用插件 Activity 的 onCreate
            invokeOnCreate(savedInstanceState);

        } catch (Exception e) {
            Log.e(TAG, "Failed to create plugin activity", e);
            finish();
        }
    }

    /**
     * 注入自定义 Context 到插件 Activity
     */
    private void injectContext(Activity activity, Intent pluginIntent) throws Exception {
        // 使用反射注入 mBase (ContextWrapper 的底层 Context)
        // 创建一个代理 Context，拦截资源访问等调用

        PluginContext pluginContext = new PluginContext(this, pluginResources, pluginClassLoader);

        // 反射设置 Activity 的 mBase
        Field mBaseField = ContextWrapper.class.getDeclaredField("mBase");
        mBaseField.setAccessible(true);
        mBaseField.set(activity, pluginContext);

        // 反射设置 Activity 的 mIntent
        Field mIntentField = Activity.class.getDeclaredField("mIntent");
        mIntentField.setAccessible(true);
        mIntentField.set(activity, pluginIntent);

        // 反射设置 Activity 的 mApplication
        Field mApplicationField = Activity.class.getDeclaredField("mApplication");
        mApplicationField.setAccessible(true);
        mApplicationField.set(activity, getApplication());

        Log.d(TAG, "Context injected successfully");
    }

    /**
     * 调用插件 Activity 的 onCreate
     */
    private void invokeOnCreate(Bundle savedInstanceState) throws Exception {
        // 获取 Activity.onCreate 方法
        Method onCreateMethod = Activity.class.getDeclaredMethod("onCreate", Bundle.class);
        onCreateMethod.setAccessible(true);

        // 调用插件的 onCreate
        onCreateMethod.invoke(pluginActivity, savedInstanceState);

        // 设置 ContentView (如果插件设置了)
        View contentView = pluginActivity.getWindow().getDecorView();
        if (contentView != null) {
            setContentView(contentView);
        }
    }

    // ========== 生命周期委托 ==========

    @Override
    protected void onStart() {
        super.onStart();
        if (pluginActivity != null) {
            invokeLifecycleMethod("onStart");
        }
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (pluginActivity != null) {
            invokeLifecycleMethod("onResume");
        }
    }

    @Override
    protected void onPause() {
        if (pluginActivity != null) {
            invokeLifecycleMethod("onPause");
        }
        super.onPause();
    }

    @Override
    protected void onStop() {
        if (pluginActivity != null) {
            invokeLifecycleMethod("onStop");
        }
        super.onStop();
    }

    @Override
    protected void onDestroy() {
        if (pluginActivity != null) {
            invokeLifecycleMethod("onDestroy");
        }
        super.onDestroy();
    }

    @Override
    protected void onSaveInstanceState(Bundle outState) {
        if (pluginActivity != null) {
            try {
                Method method = Activity.class.getDeclaredMethod(
                        "onSaveInstanceState", Bundle.class);
                method.setAccessible(true);
                method.invoke(pluginActivity, outState);
            } catch (Exception e) {
                Log.e(TAG, "onSaveInstanceState failed", e);
            }
        }
        super.onSaveInstanceState(outState);
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        if (pluginActivity != null) {
            try {
                Method method = Activity.class.getDeclaredMethod(
                        "onActivityResult", int.class, int.class, Intent.class);
                method.setAccessible(true);
                method.invoke(pluginActivity, requestCode, resultCode, data);
            } catch (Exception e) {
                Log.e(TAG, "onActivityResult failed", e);
            }
        }
        super.onActivityResult(requestCode, resultCode, data);
    }

    @Override
    public void onBackPressed() {
        if (pluginActivity != null) {
            pluginActivity.onBackPressed();
        } else {
            super.onBackPressed();
        }
    }

    /**
     * 通用生命周期方法调用
     */
    private void invokeLifecycleMethod(String methodName) {
        try {
            Method method = Activity.class.getDeclaredMethod(methodName);
            method.setAccessible(true);
            method.invoke(pluginActivity);
        } catch (Exception e) {
            Log.e(TAG, methodName + " failed", e);
        }
    }

    // ========== 资源访问重写 ==========

    @Override
    public Resources getResources() {
        // 返回插件的 Resources
        return pluginResources != null ? pluginResources : super.getResources();
    }

    @Override
    public ClassLoader getClassLoader() {
        // 返回插件的 ClassLoader
        return pluginClassLoader != null ? pluginClassLoader : super.getClassLoader();
    }

    // ========== 占坑子类 (用于不同启动模式) ==========

    public static class Standard1 extends StubActivity {}
    public static class Standard2 extends StubActivity {}
    public static class SingleTop1 extends StubActivity {}
    public static class SingleTask1 extends StubActivity {}
    public static class SingleInstance1 extends StubActivity {}
    public static class Translucent1 extends StubActivity {}
}
```

### 2.3 系统服务 Hook (Binder Proxy)

这是整个沙箱技术**最核心、最复杂**的部分。

#### Binder Hook 原理图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Binder Hook 原理                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  【Hook 前】                                                             │
│                                                                         │
│  App ──► ActivityManager.getService() ──► IActivityManager (Binder)    │
│                                                  │                      │
│                                                  ▼                      │
│                                          ActivityManagerService         │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  【Hook 后】                                                             │
│                                                                         │
│  App ──► ActivityManager.getService() ──► IActivityManager (Proxy)     │
│                                                  │                      │
│                                    ┌─────────────┴─────────────┐       │
│                                    │    InvocationHandler      │       │
│                                    │    (我们的拦截逻辑)        │       │
│                                    │                           │       │
│                                    │  invoke(method, args) {   │       │
│                                    │    if (是插件调用) {       │       │
│                                    │      修改 args            │       │
│                                    │    }                      │       │
│                                    │    return 原始调用        │       │
│                                    │  }                        │       │
│                                    └─────────────┬─────────────┘       │
│                                                  │                      │
│                                                  ▼                      │
│                                    IActivityManager (原始 Binder)       │
│                                                  │                      │
│                                                  ▼                      │
│                                          ActivityManagerService         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

#### AMS Hook 实现

```java
/**
 * AMSHook.java
 * ActivityManagerService Hook 实现
 */
public class AMSHook {

    private static final String TAG = "AMSHook";

    private Object originalAMS;  // 原始的 IActivityManager
    private Object proxyAMS;     // 代理后的 IActivityManager

    /**
     * 执行 Hook
     */
    public void hook() {
        try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                // Android 8.0+
                hookActivityManager();
            } else {
                // Android 8.0 以下
                hookActivityManagerNative();
            }
            Log.d(TAG, "AMS Hook installed successfully");
        } catch (Exception e) {
            Log.e(TAG, "AMS Hook failed", e);
        }
    }

    /**
     * Android 8.0+ 的 Hook 方式
     */
    private void hookActivityManager() throws Exception {
        // 1. 获取 ActivityManager 类
        Class<?> activityManagerClass = Class.forName("android.app.ActivityManager");

        // 2. 获取 IActivityManagerSingleton 字段
        Field singletonField = activityManagerClass.getDeclaredField("IActivityManagerSingleton");
        singletonField.setAccessible(true);
        Object singleton = singletonField.get(null);

        // 3. 获取 Singleton 类的 mInstance 字段
        Class<?> singletonClass = Class.forName("android.util.Singleton");
        Field mInstanceField = singletonClass.getDeclaredField("mInstance");
        mInstanceField.setAccessible(true);

        // 4. 获取原始的 IActivityManager 实例
        originalAMS = mInstanceField.get(singleton);

        // 5. 获取 IActivityManager 接口
        Class<?> iActivityManagerClass = Class.forName("android.app.IActivityManager");

        // 6. 创建动态代理
        proxyAMS = Proxy.newProxyInstance(
                iActivityManagerClass.getClassLoader(),
                new Class<?>[] { iActivityManagerClass },
                new AMSInvocationHandler(originalAMS)
        );

        // 7. 替换原始实例
        mInstanceField.set(singleton, proxyAMS);

        Log.d(TAG, "IActivityManagerSingleton hooked");
    }

    /**
     * Android 8.0 以下的 Hook 方式
     */
    private void hookActivityManagerNative() throws Exception {
        // 1. 获取 ActivityManagerNative 类
        Class<?> amnClass = Class.forName("android.app.ActivityManagerNative");

        // 2. 获取 gDefault 字段
        Field gDefaultField = amnClass.getDeclaredField("gDefault");
        gDefaultField.setAccessible(true);
        Object gDefault = gDefaultField.get(null);

        // 3. gDefault 是一个 Singleton，获取其 mInstance
        Class<?> singletonClass = Class.forName("android.util.Singleton");
        Field mInstanceField = singletonClass.getDeclaredField("mInstance");
        mInstanceField.setAccessible(true);

        // 4. 获取原始 IActivityManager
        originalAMS = mInstanceField.get(gDefault);

        // 5. 创建动态代理并替换
        Class<?> iActivityManagerClass = Class.forName("android.app.IActivityManager");
        proxyAMS = Proxy.newProxyInstance(
                iActivityManagerClass.getClassLoader(),
                new Class<?>[] { iActivityManagerClass },
                new AMSInvocationHandler(originalAMS)
        );

        mInstanceField.set(gDefault, proxyAMS);

        Log.d(TAG, "ActivityManagerNative.gDefault hooked");
    }

    /**
     * InvocationHandler - 核心拦截逻辑
     */
    private class AMSInvocationHandler implements InvocationHandler {

        private final Object target;  // 原始 IActivityManager

        AMSInvocationHandler(Object target) {
            this.target = target;
        }

        @Override
        public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
            String methodName = method.getName();

            Log.v(TAG, "AMS method called: " + methodName);

            // ========== startActivity 拦截 ==========
            if ("startActivity".equals(methodName)) {
                return handleStartActivity(method, args);
            }

            // ========== startService 拦截 ==========
            if ("startService".equals(methodName)) {
                return handleStartService(method, args);
            }

            // ========== bindService 拦截 ==========
            if ("bindService".equals(methodName)) {
                return handleBindService(method, args);
            }

            // ========== 其他方法，直接调用原始实现 ==========
            return method.invoke(target, args);
        }

        /**
         * 处理 startActivity 调用
         */
        private Object handleStartActivity(Method method, Object[] args) throws Throwable {
            // 找到 Intent 参数的位置
            int intentIndex = findIntentIndex(args);
            if (intentIndex == -1) {
                return method.invoke(target, args);
            }

            Intent originalIntent = (Intent) args[intentIndex];

            // 检查是否是插件 Intent
            ComponentName component = originalIntent.getComponent();
            if (component == null) {
                return method.invoke(target, args);
            }

            String className = component.getClassName();
            PluginInfo pluginInfo = PluginManager.getInstance().findPluginByClass(className);

            if (pluginInfo == null) {
                // 不是插件组件，正常启动
                return method.invoke(target, args);
            }

            Log.d(TAG, "Intercepted plugin Activity: " + className);

            // ========== 替换为 Stub Activity ==========

            // 根据插件 Activity 的 launchMode 选择合适的 Stub
            String stubClassName = selectStubActivity(pluginInfo, className);

            // 创建新的 Intent，指向 Stub Activity
            Intent stubIntent = new Intent();
            stubIntent.setClassName(
                    PluginManager.getInstance().getHostPackageName(),
                    stubClassName
            );

            // 保存原始 Intent 和插件信息
            stubIntent.putExtra(StubActivity.EXTRA_PLUGIN_INTENT, originalIntent);
            stubIntent.putExtra(StubActivity.EXTRA_PLUGIN_ID, pluginInfo.pluginId);
            stubIntent.putExtra(StubActivity.EXTRA_PLUGIN_CLASS, className);

            // 复制 Flags
            stubIntent.setFlags(originalIntent.getFlags());

            // 替换参数中的 Intent
            args[intentIndex] = stubIntent;

            Log.d(TAG, "Replaced with stub: " + stubClassName);

            // 调用原始方法
            return method.invoke(target, args);
        }

        /**
         * 处理 startService 调用
         */
        private Object handleStartService(Method method, Object[] args) throws Throwable {
            int intentIndex = findIntentIndex(args);
            if (intentIndex == -1) {
                return method.invoke(target, args);
            }

            Intent originalIntent = (Intent) args[intentIndex];
            ComponentName component = originalIntent.getComponent();

            if (component == null) {
                return method.invoke(target, args);
            }

            PluginInfo pluginInfo = PluginManager.getInstance()
                    .findPluginByClass(component.getClassName());

            if (pluginInfo == null) {
                return method.invoke(target, args);
            }

            // 替换为 Stub Service
            Intent stubIntent = new Intent();
            stubIntent.setClassName(
                    PluginManager.getInstance().getHostPackageName(),
                    "com.sandbox.host.stub.StubService$Service1"
            );
            stubIntent.putExtra("plugin_service_intent", originalIntent);
            stubIntent.putExtra("plugin_id", pluginInfo.pluginId);
            stubIntent.putExtra("plugin_class", component.getClassName());

            args[intentIndex] = stubIntent;
            return method.invoke(target, args);
        }

        /**
         * 处理 bindService 调用
         */
        private Object handleBindService(Method method, Object[] args) throws Throwable {
            // 类似 startService 的处理逻辑
            return handleStartService(method, args);
        }

        /**
         * 在参数数组中找到 Intent 的位置
         */
        private int findIntentIndex(Object[] args) {
            if (args == null) return -1;
            for (int i = 0; i < args.length; i++) {
                if (args[i] instanceof Intent) {
                    return i;
                }
            }
            return -1;
        }

        /**
         * 根据 launchMode 选择合适的 Stub Activity
         */
        private String selectStubActivity(PluginInfo pluginInfo, String activityClass) {
            // 解析插件的 AndroidManifest 获取 launchMode
            int launchMode = pluginInfo.getActivityLaunchMode(activityClass);

            switch (launchMode) {
                case 1:  // singleTop
                    return "com.sandbox.host.stub.StubActivity$SingleTop1";
                case 2:  // singleTask
                    return "com.sandbox.host.stub.StubActivity$SingleTask1";
                case 3:  // singleInstance
                    return "com.sandbox.host.stub.StubActivity$SingleInstance1";
                default: // standard
                    return "com.sandbox.host.stub.StubActivity$Standard1";
            }
        }
    }
}
```

#### PMS Hook 实现

```java
/**
 * PMSHook.java
 * PackageManagerService Hook - 用于欺骗系统"以为"插件已安装
 */
public class PMSHook {

    private static final String TAG = "PMSHook";

    /**
     * Hook PackageManager
     */
    public void hook(Context context) {
        try {
            // 1. 获取 ActivityThread
            Class<?> activityThreadClass = Class.forName("android.app.ActivityThread");
            Method currentActivityThreadMethod = activityThreadClass
                    .getDeclaredMethod("currentActivityThread");
            Object activityThread = currentActivityThreadMethod.invoke(null);

            // 2. 获取 sPackageManager 字段
            Field sPackageManagerField = activityThreadClass
                    .getDeclaredField("sPackageManager");
            sPackageManagerField.setAccessible(true);
            Object originalPM = sPackageManagerField.get(activityThread);

            // 3. 创建动态代理
            Class<?> iPackageManagerClass = Class.forName("android.content.pm.IPackageManager");
            Object proxyPM = Proxy.newProxyInstance(
                    iPackageManagerClass.getClassLoader(),
                    new Class<?>[] { iPackageManagerClass },
                    new PMSInvocationHandler(originalPM)
            );

            // 4. 替换 sPackageManager
            sPackageManagerField.set(activityThread, proxyPM);

            // 5. 同时需要 Hook ApplicationPackageManager 中的 mPM
            PackageManager pm = context.getPackageManager();
            Field mPMField = pm.getClass().getDeclaredField("mPM");
            mPMField.setAccessible(true);
            mPMField.set(pm, proxyPM);

            Log.d(TAG, "PMS Hook installed");

        } catch (Exception e) {
            Log.e(TAG, "PMS Hook failed", e);
        }
    }

    /**
     * PMS InvocationHandler
     */
    private class PMSInvocationHandler implements InvocationHandler {

        private final Object target;

        PMSInvocationHandler(Object target) {
            this.target = target;
        }

        @Override
        public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
            String methodName = method.getName();

            // ========== getPackageInfo 拦截 ==========
            if ("getPackageInfo".equals(methodName)) {
                String packageName = (String) args[0];

                // 检查是否是插件包名
                PluginInfo pluginInfo = PluginManager.getInstance()
                        .findPluginByPackage(packageName);

                if (pluginInfo != null) {
                    // 返回插件的 PackageInfo
                    Log.d(TAG, "getPackageInfo for plugin: " + packageName);
                    return pluginInfo.packageInfo;
                }
            }

            // ========== getActivityInfo 拦截 ==========
            if ("getActivityInfo".equals(methodName)) {
                ComponentName component = (ComponentName) args[0];

                PluginInfo pluginInfo = PluginManager.getInstance()
                        .findPluginByClass(component.getClassName());

                if (pluginInfo != null) {
                    // 返回插件的 ActivityInfo
                    return pluginInfo.getActivityInfo(component.getClassName());
                }
            }

            // ========== getServiceInfo 拦截 ==========
            if ("getServiceInfo".equals(methodName)) {
                ComponentName component = (ComponentName) args[0];

                PluginInfo pluginInfo = PluginManager.getInstance()
                        .findPluginByClass(component.getClassName());

                if (pluginInfo != null) {
                    return pluginInfo.getServiceInfo(component.getClassName());
                }
            }

            // ========== queryIntentActivities 拦截 ==========
            if ("queryIntentActivities".equals(methodName)) {
                Intent intent = (Intent) args[0];

                // 如果是查询插件的 Activity，返回插件信息
                List<ResolveInfo> pluginResults = PluginManager.getInstance()
                        .queryPluginActivities(intent);

                if (!pluginResults.isEmpty()) {
                    // 合并系统结果和插件结果
                    @SuppressWarnings("unchecked")
                    List<ResolveInfo> systemResults = (List<ResolveInfo>)
                            method.invoke(target, args);
                    systemResults.addAll(pluginResults);
                    return systemResults;
                }
            }

            return method.invoke(target, args);
        }
    }
}
```

### 2.4 资源管理 (Resource Management)

插件 App 需要加载自己的布局、字符串、图片等资源。

#### 资源加载原理图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        资源加载原理                                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   Plugin APK (res/ 目录)                                               │
│        │                                                                │
│        ▼                                                                │
│   ┌─────────────────┐                                                  │
│   │  AssetManager   │  ◄── addAssetPath(pluginApkPath)                │
│   │                 │       (通过反射调用隐藏 API)                      │
│   └────────┬────────┘                                                  │
│            │                                                            │
│            ▼                                                            │
│   ┌─────────────────┐                                                  │
│   │    Resources    │  ◄── new Resources(assetManager, dm, config)    │
│   │   (插件专用)     │                                                  │
│   └────────┬────────┘                                                  │
│            │                                                            │
│            ▼                                                            │
│   ┌─────────────────┐                                                  │
│   │  PluginContext  │  ◄── 重写 getResources() 返回插件 Resources     │
│   └────────┬────────┘                                                  │
│            │                                                            │
│            ▼                                                            │
│   ┌─────────────────────────────────────────────────────┐              │
│   │  Plugin Activity                                    │              │
│   │                                                     │              │
│   │  setContentView(R.layout.activity_main)            │              │
│   │  getString(R.string.app_name)                      │              │
│   │  getDrawable(R.drawable.icon)                      │              │
│   │                                                     │              │
│   │  ◄── 这些调用会使用 PluginContext 的 Resources      │              │
│   └─────────────────────────────────────────────────────┘              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

#### 代码实现

```java
/**
 * PluginResourcesManager.java
 * 插件资源管理
 */
public class PluginResourcesManager {

    private static final String TAG = "PluginResources";

    private final Context hostContext;
    private final Map<String, Resources> resourcesCache = new HashMap<>();

    public PluginResourcesManager(Context hostContext) {
        this.hostContext = hostContext;
    }

    /**
     * 为插件创建 Resources 对象
     */
    public Resources createPluginResources(String pluginApkPath, String pluginId) {
        if (resourcesCache.containsKey(pluginId)) {
            return resourcesCache.get(pluginId);
        }

        try {
            Resources pluginResources;

            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
                pluginResources = createResourcesV21(pluginApkPath);
            } else {
                pluginResources = createResourcesLegacy(pluginApkPath);
            }

            resourcesCache.put(pluginId, pluginResources);
            Log.d(TAG, "Created Resources for plugin: " + pluginId);

            return pluginResources;

        } catch (Exception e) {
            Log.e(TAG, "Failed to create plugin Resources", e);
            return hostContext.getResources();
        }
    }

    /**
     * Android 5.0+ 创建 Resources
     */
    @TargetApi(Build.VERSION_CODES.LOLLIPOP)
    private Resources createResourcesV21(String pluginApkPath) throws Exception {
        // 创建新的 AssetManager
        AssetManager assetManager = AssetManager.class.newInstance();

        // 反射调用 addAssetPath (这是隐藏 API)
        Method addAssetPathMethod = AssetManager.class.getDeclaredMethod(
                "addAssetPath", String.class);
        addAssetPathMethod.setAccessible(true);

        // 先添加宿主资源路径
        addAssetPathMethod.invoke(assetManager, hostContext.getPackageResourcePath());

        // 再添加插件资源路径
        int cookie = (int) addAssetPathMethod.invoke(assetManager, pluginApkPath);
        if (cookie == 0) {
            throw new RuntimeException("Failed to add asset path: " + pluginApkPath);
        }

        // 获取宿主的 DisplayMetrics 和 Configuration
        Resources hostResources = hostContext.getResources();
        DisplayMetrics dm = hostResources.getDisplayMetrics();
        Configuration config = hostResources.getConfiguration();

        // 创建新的 Resources
        return new Resources(assetManager, dm, config);
    }

    /**
     * Android 5.0 以下创建 Resources (兼容模式)
     */
    private Resources createResourcesLegacy(String pluginApkPath) throws Exception {
        AssetManager assetManager = AssetManager.class.newInstance();

        Method addAssetPathMethod = AssetManager.class.getDeclaredMethod(
                "addAssetPath", String.class);
        addAssetPathMethod.setAccessible(true);
        addAssetPathMethod.invoke(assetManager, pluginApkPath);

        Resources hostResources = hostContext.getResources();

        return new Resources(
                assetManager,
                hostResources.getDisplayMetrics(),
                hostResources.getConfiguration()
        );
    }

    /**
     * 获取插件的 Resources
     */
    public Resources getPluginResources(String pluginId) {
        return resourcesCache.get(pluginId);
    }
}

/**
 * PluginContext.java
 * 插件专用 Context - 重写资源访问方法
 */
public class PluginContext extends ContextWrapper {

    private final Resources pluginResources;
    private final ClassLoader pluginClassLoader;
    private final AssetManager pluginAssetManager;

    public PluginContext(Context base, Resources pluginResources, ClassLoader pluginClassLoader) {
        super(base);
        this.pluginResources = pluginResources;
        this.pluginClassLoader = pluginClassLoader;
        this.pluginAssetManager = pluginResources.getAssets();
    }

    @Override
    public Resources getResources() {
        return pluginResources;
    }

    @Override
    public AssetManager getAssets() {
        return pluginAssetManager;
    }

    @Override
    public ClassLoader getClassLoader() {
        return pluginClassLoader;
    }

    @Override
    public Resources.Theme getTheme() {
        // 创建使用插件 Resources 的 Theme
        Resources.Theme theme = pluginResources.newTheme();
        // 可以在这里应用插件定义的主题
        return theme;
    }

    @Override
    public Object getSystemService(String name) {
        // 某些系统服务可能需要特殊处理
        if (Context.LAYOUT_INFLATER_SERVICE.equals(name)) {
            // 返回使用插件 Resources 的 LayoutInflater
            LayoutInflater inflater = (LayoutInflater) super.getSystemService(name);
            return inflater.cloneInContext(this);
        }
        return super.getSystemService(name);
    }

    @Override
    public Context getApplicationContext() {
        // 返回宿主的 Application Context
        return super.getApplicationContext();
    }

    @Override
    public String getPackageName() {
        // 返回插件的包名（如果需要欺骗）
        // 或者返回宿主包名（取决于需求）
        return super.getPackageName();
    }
}
```

---

## 3. 完整示例：最小化沙箱实现

### 3.1 PluginManager 核心类

```java
/**
 * PluginManager.java
 * 插件管理器 - 沙箱框架的核心入口
 */
public class PluginManager {

    private static final String TAG = "PluginManager";
    private static volatile PluginManager instance;

    private Context hostContext;
    private String hostPackageName;

    // 各个管理器
    private PluginClassLoaderManager classLoaderManager;
    private PluginResourcesManager resourcesManager;

    // 已加载的插件信息
    private final Map<String, PluginInfo> loadedPlugins = new ConcurrentHashMap<>();

    // Hook 管理
    private AMSHook amsHook;
    private PMSHook pmsHook;

    private PluginManager() {}

    public static PluginManager getInstance() {
        if (instance == null) {
            synchronized (PluginManager.class) {
                if (instance == null) {
                    instance = new PluginManager();
                }
            }
        }
        return instance;
    }

    /**
     * 初始化沙箱框架 (在 Application.onCreate 中调用)
     */
    public void init(Context context) {
        this.hostContext = context.getApplicationContext();
        this.hostPackageName = context.getPackageName();

        // 初始化管理器
        classLoaderManager = new PluginClassLoaderManager(hostContext);
        resourcesManager = new PluginResourcesManager(hostContext);

        // 安装 Hook
        installHooks();

        Log.d(TAG, "PluginManager initialized");
    }

    /**
     * 安装系统 Hook
     */
    private void installHooks() {
        // Hook AMS
        amsHook = new AMSHook();
        amsHook.hook();

        // Hook PMS
        pmsHook = new PMSHook();
        pmsHook.hook(hostContext);

        Log.d(TAG, "System hooks installed");
    }

    /**
     * 加载插件
     *
     * @param apkPath 插件 APK 路径
     * @return 插件信息
     */
    public PluginInfo loadPlugin(String apkPath) {
        Log.d(TAG, "Loading plugin: " + apkPath);

        try {
            // 1. 解析插件 APK
            PluginInfo pluginInfo = parsePluginApk(apkPath);
            String pluginId = pluginInfo.pluginId;

            // 2. 创建 ClassLoader
            DexClassLoader classLoader = classLoaderManager.createClassLoader(apkPath, pluginId);
            pluginInfo.classLoader = classLoader;

            // 3. 创建 Resources
            Resources resources = resourcesManager.createPluginResources(apkPath, pluginId);
            pluginInfo.resources = resources;

            // 4. 缓存插件信息
            loadedPlugins.put(pluginId, pluginInfo);

            // 5. 调用插件 Application 的 onCreate (如果有)
            initPluginApplication(pluginInfo);

            Log.d(TAG, "Plugin loaded successfully: " + pluginId);
            Log.d(TAG, "  Package: " + pluginInfo.packageName);
            Log.d(TAG, "  Activities: " + pluginInfo.activities.size());
            Log.d(TAG, "  Services: " + pluginInfo.services.size());

            return pluginInfo;

        } catch (Exception e) {
            Log.e(TAG, "Failed to load plugin: " + apkPath, e);
            return null;
        }
    }

    /**
     * 解析插件 APK 的 AndroidManifest
     */
    private PluginInfo parsePluginApk(String apkPath) throws Exception {
        PackageManager pm = hostContext.getPackageManager();

        // 解析 PackageInfo
        PackageInfo packageInfo = pm.getPackageArchiveInfo(apkPath,
                PackageManager.GET_ACTIVITIES |
                PackageManager.GET_SERVICES |
                PackageManager.GET_RECEIVERS |
                PackageManager.GET_PROVIDERS |
                PackageManager.GET_META_DATA);

        if (packageInfo == null) {
            throw new RuntimeException("Failed to parse APK: " + apkPath);
        }

        // 修正 sourceDir (因为 APK 未安装，需要手动设置)
        packageInfo.applicationInfo.sourceDir = apkPath;
        packageInfo.applicationInfo.publicSourceDir = apkPath;

        // 创建 PluginInfo
        PluginInfo pluginInfo = new PluginInfo();
        pluginInfo.pluginId = generatePluginId(packageInfo.packageName);
        pluginInfo.packageName = packageInfo.packageName;
        pluginInfo.apkPath = apkPath;
        pluginInfo.packageInfo = packageInfo;

        // 解析 Activities
        if (packageInfo.activities != null) {
            for (ActivityInfo activityInfo : packageInfo.activities) {
                pluginInfo.activities.put(activityInfo.name, activityInfo);
            }
        }

        // 解析 Services
        if (packageInfo.services != null) {
            for (ServiceInfo serviceInfo : packageInfo.services) {
                pluginInfo.services.put(serviceInfo.name, serviceInfo);
            }
        }

        // 解析 Receivers
        if (packageInfo.receivers != null) {
            for (ActivityInfo receiverInfo : packageInfo.receivers) {
                pluginInfo.receivers.put(receiverInfo.name, receiverInfo);
            }
        }

        return pluginInfo;
    }

    /**
     * 初始化插件的 Application
     */
    private void initPluginApplication(PluginInfo pluginInfo) {
        try {
            String appClassName = pluginInfo.packageInfo.applicationInfo.className;
            if (appClassName == null || appClassName.isEmpty()) {
                return;
            }

            // 加载 Application 类
            Class<?> appClass = pluginInfo.classLoader.loadClass(appClassName);
            Application pluginApp = (Application) appClass.getDeclaredConstructor().newInstance();

            // 创建 PluginContext
            PluginContext pluginContext = new PluginContext(
                    hostContext,
                    pluginInfo.resources,
                    pluginInfo.classLoader
            );

            // 注入 Context
            Method attachMethod = ContextWrapper.class.getDeclaredMethod("attachBaseContext", Context.class);
            attachMethod.setAccessible(true);
            attachMethod.invoke(pluginApp, pluginContext);

            // 调用 onCreate
            pluginApp.onCreate();

            pluginInfo.application = pluginApp;
            Log.d(TAG, "Plugin Application initialized: " + appClassName);

        } catch (Exception e) {
            Log.w(TAG, "Failed to init plugin Application", e);
        }
    }

    /**
     * 启动插件 Activity
     */
    public void startPluginActivity(Context context, String pluginId, String activityClass) {
        PluginInfo pluginInfo = loadedPlugins.get(pluginId);
        if (pluginInfo == null) {
            Log.e(TAG, "Plugin not loaded: " + pluginId);
            return;
        }

        Intent intent = new Intent();
        intent.setComponent(new ComponentName(pluginInfo.packageName, activityClass));

        // 这个 Intent 会被 AMS Hook 拦截并替换为 Stub
        context.startActivity(intent);
    }

    /**
     * 启动插件的主 Activity
     */
    public void startPluginMainActivity(Context context, String pluginId) {
        PluginInfo pluginInfo = loadedPlugins.get(pluginId);
        if (pluginInfo == null) {
            Log.e(TAG, "Plugin not loaded: " + pluginId);
            return;
        }

        // 查找主 Activity
        String mainActivity = findMainActivity(pluginInfo);
        if (mainActivity != null) {
            startPluginActivity(context, pluginId, mainActivity);
        } else {
            Log.e(TAG, "No main activity found in plugin: " + pluginId);
        }
    }

    /**
     * 查找插件的主 Activity (LAUNCHER)
     */
    private String findMainActivity(PluginInfo pluginInfo) {
        try {
            PackageManager pm = hostContext.getPackageManager();
            Intent launchIntent = new Intent(Intent.ACTION_MAIN);
            launchIntent.addCategory(Intent.CATEGORY_LAUNCHER);
            launchIntent.setPackage(pluginInfo.packageName);

            // 遍历所有 Activity 查找带有 LAUNCHER category 的
            for (ActivityInfo activityInfo : pluginInfo.activities.values()) {
                // 简化处理：返回第一个 Activity 作为主入口
                return activityInfo.name;
            }
        } catch (Exception e) {
            Log.e(TAG, "Failed to find main activity", e);
        }
        return null;
    }

    // ========== Getter 方法 ==========

    public String getHostPackageName() {
        return hostPackageName;
    }

    public ClassLoader getPluginClassLoader(String pluginId) {
        PluginInfo info = loadedPlugins.get(pluginId);
        return info != null ? info.classLoader : null;
    }

    public Resources getPluginResources(String pluginId) {
        PluginInfo info = loadedPlugins.get(pluginId);
        return info != null ? info.resources : null;
    }

    public PluginInfo findPluginByPackage(String packageName) {
        for (PluginInfo info : loadedPlugins.values()) {
            if (info.packageName.equals(packageName)) {
                return info;
            }
        }
        return null;
    }

    public PluginInfo findPluginByClass(String className) {
        for (PluginInfo info : loadedPlugins.values()) {
            if (info.activities.containsKey(className) ||
                info.services.containsKey(className) ||
                info.receivers.containsKey(className)) {
                return info;
            }
        }
        return null;
    }

    private String generatePluginId(String packageName) {
        return packageName + "_" + System.currentTimeMillis();
    }
}

/**
 * PluginInfo.java
 * 插件信息数据类
 */
public class PluginInfo {
    public String pluginId;
    public String packageName;
    public String apkPath;
    public PackageInfo packageInfo;

    public ClassLoader classLoader;
    public Resources resources;
    public Application application;

    public Map<String, ActivityInfo> activities = new HashMap<>();
    public Map<String, ServiceInfo> services = new HashMap<>();
    public Map<String, ActivityInfo> receivers = new HashMap<>();

    public ActivityInfo getActivityInfo(String className) {
        return activities.get(className);
    }

    public ServiceInfo getServiceInfo(String className) {
        return services.get(className);
    }

    public int getActivityLaunchMode(String className) {
        ActivityInfo info = activities.get(className);
        return info != null ? info.launchMode : 0;
    }

    public List<ResolveInfo> queryActivities(Intent intent) {
        // 根据 Intent 查询匹配的 Activity
        List<ResolveInfo> results = new ArrayList<>();
        // ... 实现 Intent 匹配逻辑
        return results;
    }
}
```

### 3.2 使用示例

```java
/**
 * HostApplication.java
 * 宿主 App 的 Application
 */
public class HostApplication extends Application {

    @Override
    public void onCreate() {
        super.onCreate();

        // 初始化沙箱框架
        PluginManager.getInstance().init(this);
    }
}

/**
 * MainActivity.java
 * 宿主 App 的主 Activity
 */
public class MainActivity extends AppCompatActivity {

    private static final String TAG = "MainActivity";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // 加载插件按钮
        findViewById(R.id.btnLoadPlugin).setOnClickListener(v -> loadPlugin());

        // 启动插件按钮
        findViewById(R.id.btnStartPlugin).setOnClickListener(v -> startPlugin());
    }

    private void loadPlugin() {
        // 从 assets 复制插件 APK 到私有目录
        String pluginPath = copyPluginFromAssets("plugin.apk");

        // 加载插件
        PluginInfo pluginInfo = PluginManager.getInstance().loadPlugin(pluginPath);

        if (pluginInfo != null) {
            Toast.makeText(this, "插件加载成功: " + pluginInfo.packageName,
                    Toast.LENGTH_SHORT).show();

            // 保存 pluginId 供后续使用
            getPreferences(MODE_PRIVATE)
                    .edit()
                    .putString("last_plugin_id", pluginInfo.pluginId)
                    .apply();
        } else {
            Toast.makeText(this, "插件加载失败", Toast.LENGTH_SHORT).show();
        }
    }

    private void startPlugin() {
        String pluginId = getPreferences(MODE_PRIVATE).getString("last_plugin_id", null);

        if (pluginId == null) {
            Toast.makeText(this, "请先加载插件", Toast.LENGTH_SHORT).show();
            return;
        }

        // 启动插件的主 Activity
        PluginManager.getInstance().startPluginMainActivity(this, pluginId);
    }

    private String copyPluginFromAssets(String assetName) {
        File outFile = new File(getFilesDir(), assetName);

        try (InputStream in = getAssets().open(assetName);
             FileOutputStream out = new FileOutputStream(outFile)) {

            byte[] buffer = new byte[8192];
            int len;
            while ((len = in.read(buffer)) != -1) {
                out.write(buffer, 0, len);
            }

        } catch (IOException e) {
            Log.e(TAG, "Failed to copy plugin", e);
        }

        return outFile.getAbsolutePath();
    }
}
```

---

## 4. 知名开源项目参考

| 项目 | 描述 | 特点 |
|-----|------|-----|
| **[VirtualApp](https://github.com/asLody/VirtualApp)** | 最著名的 Android 沙箱 | 代码结构清晰，功能完整 |
| **[VirtualXposed](https://github.com/AJunxx/VirtualXposed)** | 免 Root 运行 Xposed | 基于 VirtualApp |
| **[DroidPlugin](https://github.com/AJunxx/DroidPlugin)** | 360 开发的插件框架 | 四大组件支持完整 |
| **[Shadow](https://github.com/AJunxx/Shadow)** | 腾讯开源插件框架 | 零反射、全动态 |
| **[RePlugin](https://github.com/AJunxx/RePlugin)** | 360 开源插件框架 | 稳定、灵活 |

---

## 5. 挑战与局限

### 5.1 兼容性问题

```
┌─────────────────────────────────────────────────────────────┐
│                    Android 版本兼容性                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Android 版本    主要变化                    影响           │
│   ─────────────────────────────────────────────────────────│
│   Android 9.0    隐藏 API 限制               反射受限       │
│   Android 10     Scoped Storage             文件访问限制    │
│   Android 11     Package Visibility          包可见性限制   │
│   Android 12     exported 必须显式声明        Manifest 变化 │
│   Android 13     通知权限变化                 运行时权限     │
│   Android 14     前台服务类型                 服务限制      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 绕过隐藏 API 限制

```java
/**
 * 绕过 Android 9.0+ 的隐藏 API 限制
 */
public class HiddenApiBypass {

    /**
     * 方法1: 通过修改调用者身份
     */
    public static void bypassHiddenApiRestrictions() {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.P) {
            return;
        }

        try {
            Method forName = Class.class.getDeclaredMethod("forName", String.class);
            Method getDeclaredMethod = Class.class.getDeclaredMethod(
                    "getDeclaredMethod", String.class, Class[].class);

            Class<?> vmRuntimeClass = (Class<?>) forName.invoke(null, "dalvik.system.VMRuntime");
            Method getRuntime = (Method) getDeclaredMethod.invoke(vmRuntimeClass, "getRuntime", null);
            Method setHiddenApiExemptions = (Method) getDeclaredMethod.invoke(
                    vmRuntimeClass, "setHiddenApiExemptions", new Class[]{String[].class});

            Object vmRuntime = getRuntime.invoke(null);
            setHiddenApiExemptions.invoke(vmRuntime, new Object[]{new String[]{"L"}});

        } catch (Exception e) {
            Log.e("HiddenApiBypass", "Failed to bypass hidden API", e);
        }
    }
}
```

### 5.3 Native Code 支持

对于包含 JNI/Native 代码的插件，需要额外处理：

```java
/**
 * Native 库加载器
 */
public class NativeLibraryLoader {

    /**
     * 为插件修改 Native 库搜索路径
     */
    public static void patchNativeLibraryPath(ClassLoader classLoader, String libPath) {
        try {
            // 获取 BaseDexClassLoader 的 pathList 字段
            Field pathListField = BaseDexClassLoader.class.getDeclaredField("pathList");
            pathListField.setAccessible(true);
            Object pathList = pathListField.get(classLoader);

            // 获取 DexPathList 的 nativeLibraryDirectories 字段
            Field nativeLibDirsField = pathList.getClass()
                    .getDeclaredField("nativeLibraryDirectories");
            nativeLibDirsField.setAccessible(true);

            @SuppressWarnings("unchecked")
            List<File> nativeLibDirs = (List<File>) nativeLibDirsField.get(pathList);

            // 添加插件的 lib 目录
            nativeLibDirs.add(0, new File(libPath));

            // 同时需要更新 nativeLibraryPathElements
            // ... (更复杂的反射操作)

        } catch (Exception e) {
            Log.e("NativeLoader", "Failed to patch native library path", e);
        }
    }
}
```

---

## 6. 安全分析视角

从逆向工程和安全分析的角度，沙箱技术有以下应用：

### 6.1 行为分析

```java
/**
 * 在沙箱中监控 App 行为
 */
public class BehaviorMonitor {

    /**
     * 监控网络请求
     */
    public void hookNetwork() {
        // Hook OkHttp、HttpURLConnection 等
    }

    /**
     * 监控文件访问
     */
    public void hookFileAccess() {
        // Hook File 类的 read/write 操作
    }

    /**
     * 监控敏感 API 调用
     */
    public void hookSensitiveAPIs() {
        // 监控获取设备ID、定位、联系人等 API
    }
}
```

### 6.2 动态脱壳

沙箱环境是执行动态脱壳的理想场所，因为可以完全控制 App 的加载和执行过程。

---

## 7. 总结

Android 沙箱技术通过进程内虚拟化实现了在单一设备上运行多个隔离应用的能力。核心技术包括：

| 模块 | 技术 | 关键类/方法 |
|-----|-----|------------|
| 类加载 | DexClassLoader | `loadClass()`, `addAssetPath()` |
| 组件管理 | Stub 占坑 | `AndroidManifest.xml`, 反射 |
| 系统 Hook | 动态代理 | `Proxy.newProxyInstance()` |
| 资源管理 | 自定义 Resources | `AssetManager`, `ContextWrapper` |

这项技术在应用多开、安全分析、自动化测试等领域有广泛应用，但也面临着 Android 版本兼容性、厂商 ROM 差异、Native 代码支持等挑战。

**推荐下一步**：[AOSP 与系统定制](./aosp_and_system_customization.md)
