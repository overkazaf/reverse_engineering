---
title: "Android Binder 跨进程通信机制"
date: 2024-07-08
type: posts
tags: ["Native层", "代理池", "Frida", "基础知识", "Hook", "Smali"]
weight: 10
---

# Android Binder 跨进程通信机制

Binder 是 Android 系统中最核心、最独特的 IPC（Inter-Process Communication，跨进程通信）机制。可以说：**无 Binder，不 Android**。

理解 Binder 不能只把它当成一个"技术"，而要把它看作一种**架构设计**。

---

## 目录

1. [为什么需要 Binder](#1-为什么需要-binder)
2. [Binder 架构：四要素](#2-binder-架构四要素)
3. [Binder 通信原理：一次拷贝](#3-binder-通信原理一次拷贝)
4. [Binder 驱动详解](#4-binder-驱动详解)
5. [AIDL 与代码层实现](#5-aidl-与代码层实现)
6. [实战示例代码](#6-实战示例代码)
7. [Binder 通信流程图解](#7-binder-通信流程图解)
8. [Binder 在逆向中的应用](#8-binder-在逆向中的应用)
9. [总结](#9-总结)

---

## 1. 为什么需要 Binder

在 Linux 系统中，已经有了管道 (Pipe)、Socket、共享内存、信号量等 IPC 机制，为什么 Google 还要重新造一个轮子？

### 1.1 传统 IPC 的问题

| IPC 机制 | 数据拷贝次数 | 优点 | 缺点 |
|---------|-------------|------|------|
| 管道 (Pipe) | 2 次 | 简单 | 单向、效率低 |
| Socket | 2 次 | 通用、可跨网络 | 效率低、开销大 |
| 共享内存 | 0 次 | 效率最高 | 同步复杂、不安全 |
| 信号量 | - | 同步原语 | 只能传信号 |
| **Binder** | **1 次** | 高效、安全、易用 | Android 特有 |

### 1.2 Binder 的优势

**性能 (Performance)**：
- Socket 传输效率低（数据拷贝 2 次）
- 共享内存虽然快（拷贝 0 次）但管理复杂且不安全
- Binder 只需 **1 次拷贝**，完全满足移动端高频调用需求

**安全 (Security)**：
- 传统 Linux IPC 对通信双方的身份校验较弱（通常依赖 UID/GID）
- Binder 机制支持**实名制**，内核层直接校验 UID/PID
- 适合权限分明的 Android App 沙箱模型

**面向对象 (Object-Oriented)**：
- Android 的设计理念是组件化（Activity, Service）
- Binder 天然支持 **RPC**（远程过程调用）
- 跨进程调用函数就像调用本地对象的方法一样自然

---

## 2. Binder 架构：四要素

Binder 采用 **C/S (Client-Server)** 架构，包含四个关键角色：

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Binder 通信架构                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │                         用户空间                                  │  │
│   │                                                                   │  │
│   │  ┌─────────────┐                          ┌─────────────┐        │  │
│   │  │   Client    │                          │   Server    │        │  │
│   │  │ (App 进程)  │                          │ (系统服务)  │        │  │
│   │  │             │                          │             │        │  │
│   │  │  Proxy      │──────────────────────────│    Stub     │        │  │
│   │  │  (代理)     │                          │   (存根)    │        │  │
│   │  └──────┬──────┘                          └──────┬──────┘        │  │
│   │         │                                        │               │  │
│   │         │    ┌─────────────────────┐            │               │  │
│   │         │    │  ServiceManager     │            │               │  │
│   │         │    │   (服务注册中心)    │            │               │  │
│   │         │    │                     │            │               │  │
│   │         │    │  ┌───────────────┐ │            │               │  │
│   │         │    │  │ 服务名 → 句柄 │ │            │               │  │
│   │         │    │  │ GPS → 0x01   │ │            │               │  │
│   │         │    │  │ Audio → 0x02 │ │            │               │  │
│   │         │    │  └───────────────┘ │            │               │  │
│   │         │    └──────────┬──────────┘            │               │  │
│   │         │               │                       │               │  │
│   └─────────┼───────────────┼───────────────────────┼───────────────┘  │
│             │               │                       │                  │
│   ┌─────────┼───────────────┼───────────────────────┼───────────────┐  │
│   │         ▼               ▼                       ▼               │  │
│   │  ┌─────────────────────────────────────────────────────────┐   │  │
│   │  │                   Binder Driver                          │   │  │
│   │  │                   (/dev/binder)                          │   │  │
│   │  │                                                          │   │  │
│   │  │  ┌──────────────────────────────────────────────────┐   │   │  │
│   │  │  │              内核缓冲区 (mmap)                    │   │   │  │
│   │  │  │         ↕ 内存映射 ↕                              │   │   │  │
│   │  │  │    Client 数据 ────────────► Server 可见          │   │   │  │
│   │  │  └──────────────────────────────────────────────────┘   │   │  │
│   │  │                                                          │   │  │
│   │  └─────────────────────────────────────────────────────────┘   │  │
│   │                         内核空间                               │  │
│   └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.1 Client (客户端)

发起服务请求的进程。

```java
// Client 端代码示例
// 获取系统服务
LocationManager locationManager =
    (LocationManager) context.getSystemService(Context.LOCATION_SERVICE);

// 调用服务方法 (实际是跨进程调用)
Location location = locationManager.getLastKnownLocation(GPS_PROVIDER);
```

### 2.2 Server (服务端)

提供服务的进程。

```java
// Server 端代码示例
public class LocationManagerService extends ILocationManager.Stub {

    @Override
    public Location getLastKnownLocation(String provider) {
        // 真正的定位逻辑
        return calculateLocation(provider);
    }
}
```

### 2.3 ServiceManager (服务注册中心)

**作用**：电话本 / DNS。

```java
/**
 * ServiceManager 核心功能
 */
public class ServiceManager {

    // 服务注册表
    private static HashMap<String, IBinder> sCache = new HashMap<>();

    /**
     * Server 注册服务
     */
    public static void addService(String name, IBinder service) {
        // 向 Binder 驱动注册
        // "我是定位服务，句柄是 0x01"
        sCache.put(name, service);
    }

    /**
     * Client 获取服务
     */
    public static IBinder getService(String name) {
        // 返回服务的 Binder 代理
        return sCache.get(name);
    }
}
```

**流程**：
1. Server 启动后注册到 ServiceManager
2. Client 想用服务时，先问 ServiceManager 要到 Server 的句柄
3. Client 通过句柄与 Server 通信

### 2.4 Binder Driver (Binder 驱动)

**位置**：Linux 内核层 (`/dev/binder`)

**作用**：幕后英雄
- Client、Server、ServiceManager 都在用户空间，彼此不能直接访问内存
- 所有的数据传输、对象映射、线程管理，全靠内核里的驱动来搬运

```c
// Binder 驱动核心数据结构
struct binder_proc {
    struct hlist_node proc_node;
    struct rb_root threads;      // 线程红黑树
    struct rb_root nodes;        // Binder 实体红黑树
    struct rb_root refs_by_desc; // Binder 引用红黑树
    struct rb_root refs_by_node;

    struct list_head todo;       // 待处理任务列表
    wait_queue_head_t wait;      // 等待队列

    struct mm_struct *vma_vm_mm; // 内存映射
    void *buffer;                // 内核缓冲区
    size_t buffer_size;          // 缓冲区大小
};
```

---

## 3. Binder 通信原理：一次拷贝

这是 Binder 最核心的技术亮点。

### 3.1 传统 IPC (如 Socket)：两次拷贝

```
┌─────────────┐          ┌─────────────┐          ┌─────────────┐
│   Client    │          │   Kernel    │          │   Server    │
│  用户空间   │          │   内核空间   │          │  用户空间   │
│             │          │             │          │             │
│   [数据]    │ ──────►  │   [数据]    │ ──────►  │   [数据]    │
│             │  copy 1  │             │  copy 2  │             │
│             │          │             │          │             │
└─────────────┘          └─────────────┘          └─────────────┘
        ↑                       ↑                       ↑
   用户态数据           copy_from_user          copy_to_user
                        copy_to_user
```

### 3.2 Binder 机制：一次拷贝

```
┌─────────────┐          ┌─────────────────────────────────────────┐
│   Client    │          │              Kernel + Server             │
│  用户空间   │          │  ┌─────────────┐    ┌─────────────┐     │
│             │          │  │ 内核缓冲区   │◄──►│ Server 映射  │     │
│   [数据]    │ ──────►  │  │   [数据]    │    │   [数据]    │     │
│             │  copy 1  │  │             │    │  (可直接读)  │     │
│             │          │  └─────────────┘    └─────────────┘     │
└─────────────┘          │        ↑                   ↑            │
                         │        └───── mmap 映射 ───┘            │
                         │            (同一物理内存)                │
                         └─────────────────────────────────────────┘
```

### 3.3 内存映射原理

```c
/**
 * Binder 内存映射实现
 */

// Server 启动时调用
int binder_mmap(struct file *filp, struct vm_area_struct *vma) {
    struct binder_proc *proc = filp->private_data;

    // 1. 分配内核缓冲区
    proc->buffer = kzalloc(vma->vm_end - vma->vm_start, GFP_KERNEL);

    // 2. 将内核缓冲区映射到 Server 的用户空间
    //    这样内核缓冲区和 Server 用户空间指向同一物理内存
    remap_pfn_range(vma, vma->vm_start,
                    virt_to_phys(proc->buffer) >> PAGE_SHIFT,
                    vma->vm_end - vma->vm_start,
                    vma->vm_page_prot);

    return 0;
}

// 数据传输时
void binder_transaction(struct binder_proc *target_proc,
                        struct binder_buffer *buffer,
                        void __user *data, size_t size) {

    // 只需要一次拷贝：从 Client 用户空间 → 内核缓冲区
    copy_from_user(buffer->data, data, size);

    // Server 直接可见 (因为 mmap 映射)
    // 不需要 copy_to_user
}
```

### 3.4 一次拷贝 vs 零次拷贝

| 方案 | 拷贝次数 | 优点 | 缺点 |
|-----|---------|------|------|
| 共享内存 | 0 次 | 效率最高 | 需要同步机制、不安全 |
| **Binder** | **1 次** | 安全、有驱动管理 | 效率略低于共享内存 |
| Socket | 2 次 | 通用 | 效率低 |

---

## 4. Binder 驱动详解

### 4.1 Binder 驱动入口

```c
// 驱动初始化
static int __init binder_init(void) {
    int ret;

    // 创建 /dev/binder 设备节点
    ret = misc_register(&binder_miscdev);

    // 创建 Binder 工作队列
    binder_deferred_workqueue =
        create_singlethread_workqueue("binder");

    return ret;
}

// 文件操作
static const struct file_operations binder_fops = {
    .owner          = THIS_MODULE,
    .open           = binder_open,
    .release        = binder_release,
    .mmap           = binder_mmap,           // 内存映射
    .unlocked_ioctl = binder_ioctl,          // 核心控制
    .poll           = binder_poll,
    .flush          = binder_flush,
};
```

### 4.2 ioctl 命令

```c
// Binder 驱动的 ioctl 命令
#define BINDER_WRITE_READ           _IOWR('b', 1, struct binder_write_read)
#define BINDER_SET_MAX_THREADS      _IOW('b', 5, __u32)
#define BINDER_SET_CONTEXT_MGR      _IOW('b', 7, __s32)
#define BINDER_THREAD_EXIT          _IOW('b', 8, __s32)
#define BINDER_VERSION              _IOWR('b', 9, struct binder_version)

// 最核心的命令：BINDER_WRITE_READ
// 用于发送和接收 Binder 数据
struct binder_write_read {
    binder_size_t write_size;       // 写入数据大小
    binder_size_t write_consumed;   // 已消费的写入数据
    binder_uintptr_t write_buffer;  // 写入缓冲区

    binder_size_t read_size;        // 读取数据大小
    binder_size_t read_consumed;    // 已消费的读取数据
    binder_uintptr_t read_buffer;   // 读取缓冲区
};
```

### 4.3 Binder 协议命令

```c
// Client → Driver 的命令 (BC: Binder Command)
enum binder_driver_command_protocol {
    BC_TRANSACTION = _IOW('c', 0, struct binder_transaction_data),
    BC_REPLY = _IOW('c', 1, struct binder_transaction_data),
    BC_ACQUIRE_RESULT = _IOW('c', 2, __s32),
    BC_FREE_BUFFER = _IOW('c', 3, binder_uintptr_t),
    BC_INCREFS = _IOW('c', 4, __u32),
    BC_ACQUIRE = _IOW('c', 5, __u32),
    BC_RELEASE = _IOW('c', 6, __u32),
    BC_DECREFS = _IOW('c', 7, __u32),
    BC_ENTER_LOOPER = _IO('c', 12),
    BC_EXIT_LOOPER = _IO('c', 13),
    BC_REGISTER_LOOPER = _IO('c', 11),
};

// Driver → Client/Server 的返回 (BR: Binder Return)
enum binder_driver_return_protocol {
    BR_ERROR = _IOR('r', 0, __s32),
    BR_OK = _IO('r', 1),
    BR_TRANSACTION = _IOR('r', 2, struct binder_transaction_data),
    BR_REPLY = _IOR('r', 3, struct binder_transaction_data),
    BR_DEAD_BINDER = _IOR('r', 15, binder_uintptr_t),
    BR_SPAWN_LOOPER = _IO('r', 13),
};
```

---

## 5. AIDL 与代码层实现

### 5.1 AIDL 文件定义

```java
// ILocationService.aidl
package com.example.service;

interface ILocationService {
    Location getLastKnownLocation(String provider);
    void requestLocationUpdates(String provider, long minTime,
                                float minDistance,
                                ILocationListener listener);
}
```

### 5.2 生成的代码结构

```java
/**
 * AIDL 编译后生成的代码
 */
public interface ILocationService extends IInterface {

    // Stub: Server 端实现
    public static abstract class Stub extends Binder
            implements ILocationService {

        private static final String DESCRIPTOR =
            "com.example.service.ILocationService";

        public Stub() {
            this.attachInterface(this, DESCRIPTOR);
        }

        // 将 IBinder 转换为接口
        public static ILocationService asInterface(IBinder obj) {
            if (obj == null) return null;

            // 检查是否同一进程 (本地调用)
            IInterface iin = obj.queryLocalInterface(DESCRIPTOR);
            if (iin != null && iin instanceof ILocationService) {
                return (ILocationService) iin;
            }

            // 跨进程，返回 Proxy
            return new Proxy(obj);
        }

        @Override
        public boolean onTransact(int code, Parcel data,
                                  Parcel reply, int flags) {
            switch (code) {
                case TRANSACTION_getLastKnownLocation: {
                    data.enforceInterface(DESCRIPTOR);
                    String provider = data.readString();

                    // 调用真正的实现
                    Location result = this.getLastKnownLocation(provider);

                    reply.writeNoException();
                    result.writeToParcel(reply, 0);
                    return true;
                }
            }
            return super.onTransact(code, data, reply, flags);
        }
    }

    // Proxy: Client 端代理
    private static class Proxy implements ILocationService {
        private IBinder mRemote;

        Proxy(IBinder remote) {
            mRemote = remote;
        }

        @Override
        public Location getLastKnownLocation(String provider) {
            Parcel data = Parcel.obtain();
            Parcel reply = Parcel.obtain();

            try {
                data.writeInterfaceToken(DESCRIPTOR);
                data.writeString(provider);

                // 跨进程调用
                mRemote.transact(TRANSACTION_getLastKnownLocation,
                                data, reply, 0);

                reply.readException();
                Location result = Location.CREATOR.createFromParcel(reply);
                return result;
            } finally {
                data.recycle();
                reply.recycle();
            }
        }
    }
}
```

### 5.3 Parcel 数据序列化

```java
/**
 * Parcel: Binder 数据传输的序列化容器
 */
public class Location implements Parcelable {
    private double latitude;
    private double longitude;
    private String provider;

    // 写入 Parcel
    @Override
    public void writeToParcel(Parcel dest, int flags) {
        dest.writeDouble(latitude);
        dest.writeDouble(longitude);
        dest.writeString(provider);
    }

    // 从 Parcel 读取
    public static final Creator<Location> CREATOR = new Creator<Location>() {
        @Override
        public Location createFromParcel(Parcel in) {
            Location location = new Location();
            location.latitude = in.readDouble();
            location.longitude = in.readDouble();
            location.provider = in.readString();
            return location;
        }

        @Override
        public Location[] newArray(int size) {
            return new Location[size];
        }
    };
}
```

---

## 6. 实战示例代码

### 6.1 完整 AIDL 服务实现

以下是一个完整的自定义 Binder 服务示例，包含服务端、客户端和 AIDL 定义。

**步骤 1：定义 AIDL 接口**

```java
// ICalculatorService.aidl
package com.example.binderservice;

interface ICalculatorService {
    int add(int a, int b);
    int subtract(int a, int b);
    int multiply(int a, int b);
    double divide(int a, int b);

    // 支持回调的异步方法
    oneway void calculateAsync(int a, int b, ICalculatorCallback callback);
}

// ICalculatorCallback.aidl
package com.example.binderservice;

interface ICalculatorCallback {
    void onResult(int result);
    void onError(String message);
}
```

**步骤 2：实现服务端**

```java
/**
 * 计算器服务实现
 * Server 端：实现 AIDL 定义的接口
 */
public class CalculatorService extends Service {

    private static final String TAG = "CalculatorService";

    // Binder 实现类
    private final ICalculatorService.Stub mBinder = new ICalculatorService.Stub() {

        @Override
        public int add(int a, int b) throws RemoteException {
            Log.d(TAG, "add() called: " + a + " + " + b);
            // 可以获取调用者的 UID/PID 进行权限校验
            int callingUid = Binder.getCallingUid();
            int callingPid = Binder.getCallingPid();
            Log.d(TAG, "Caller UID: " + callingUid + ", PID: " + callingPid);

            return a + b;
        }

        @Override
        public int subtract(int a, int b) throws RemoteException {
            return a - b;
        }

        @Override
        public int multiply(int a, int b) throws RemoteException {
            return a * b;
        }

        @Override
        public double divide(int a, int b) throws RemoteException {
            if (b == 0) {
                throw new RemoteException("Division by zero");
            }
            return (double) a / b;
        }

        @Override
        public void calculateAsync(int a, int b, ICalculatorCallback callback)
                throws RemoteException {
            // 异步计算，通过回调返回结果
            new Thread(() -> {
                try {
                    Thread.sleep(1000); // 模拟耗时操作
                    int result = a + b;
                    callback.onResult(result);
                } catch (Exception e) {
                    try {
                        callback.onError(e.getMessage());
                    } catch (RemoteException re) {
                        Log.e(TAG, "Callback failed", re);
                    }
                }
            }).start();
        }
    };

    @Override
    public IBinder onBind(Intent intent) {
        Log.d(TAG, "Service bound");
        return mBinder;
    }

    @Override
    public void onCreate() {
        super.onCreate();
        Log.d(TAG, "Service created");
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        Log.d(TAG, "Service destroyed");
    }
}
```

**步骤 3：AndroidManifest.xml 注册服务**

```xml
<!-- AndroidManifest.xml -->
<service
    android:name=".CalculatorService"
    android:enabled="true"
    android:exported="true">
    <intent-filter>
        <action android:name="com.example.binderservice.CALCULATOR" />
    </intent-filter>
</service>
```

**步骤 4：实现客户端**

```java
/**
 * 客户端：跨进程调用服务
 */
public class MainActivity extends AppCompatActivity {

    private static final String TAG = "CalculatorClient";

    private ICalculatorService mService;
    private boolean mBound = false;

    // ServiceConnection 处理绑定事件
    private ServiceConnection mConnection = new ServiceConnection() {

        @Override
        public void onServiceConnected(ComponentName name, IBinder service) {
            Log.d(TAG, "Service connected");

            // 将 IBinder 转换为 AIDL 接口
            // asInterface() 会判断是否同一进程
            mService = ICalculatorService.Stub.asInterface(service);
            mBound = true;

            // 注册死亡代理
            try {
                service.linkToDeath(mDeathRecipient, 0);
            } catch (RemoteException e) {
                e.printStackTrace();
            }
        }

        @Override
        public void onServiceDisconnected(ComponentName name) {
            Log.d(TAG, "Service disconnected");
            mService = null;
            mBound = false;
        }
    };

    // 死亡代理：监控 Server 进程是否死亡
    private IBinder.DeathRecipient mDeathRecipient = new IBinder.DeathRecipient() {
        @Override
        public void binderDied() {
            Log.w(TAG, "Service died! Reconnecting...");
            mService = null;
            mBound = false;
            // 可以在这里尝试重新绑定
            bindToService();
        }
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // 绑定服务
        bindToService();
    }

    private void bindToService() {
        Intent intent = new Intent();
        intent.setAction("com.example.binderservice.CALCULATOR");
        intent.setPackage("com.example.binderservice"); // 目标包名
        bindService(intent, mConnection, Context.BIND_AUTO_CREATE);
    }

    /**
     * 调用服务方法
     */
    public void performCalculation() {
        if (!mBound || mService == null) {
            Log.e(TAG, "Service not bound");
            return;
        }

        try {
            // 同步调用
            int sum = mService.add(10, 20);
            Log.d(TAG, "10 + 20 = " + sum);

            int diff = mService.subtract(30, 15);
            Log.d(TAG, "30 - 15 = " + diff);

            double quotient = mService.divide(100, 4);
            Log.d(TAG, "100 / 4 = " + quotient);

            // 异步调用 (通过回调)
            mService.calculateAsync(5, 7, new ICalculatorCallback.Stub() {
                @Override
                public void onResult(int result) throws RemoteException {
                    Log.d(TAG, "Async result: " + result);
                    runOnUiThread(() -> {
                        // 更新 UI
                    });
                }

                @Override
                public void onError(String message) throws RemoteException {
                    Log.e(TAG, "Async error: " + message);
                }
            });

        } catch (RemoteException e) {
            Log.e(TAG, "Remote call failed", e);
        }
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (mBound) {
            unbindService(mConnection);
            mBound = false;
        }
    }
}
```

### 6.2 Native Binder (C++) 示例

在 Native 层直接使用 Binder，不依赖 Java/Kotlin。

**Server 端 (C++)**

```cpp
// NativeCalculatorService.h
#pragma once

#include <binder/Binder.h>
#include <binder/IInterface.h>
#include <binder/Parcel.h>

namespace android {

// 接口定义
class INativeCalculator : public IInterface {
public:
    DECLARE_META_INTERFACE(NativeCalculator);

    enum {
        TRANSACTION_ADD = IBinder::FIRST_CALL_TRANSACTION,
        TRANSACTION_SUBTRACT,
        TRANSACTION_MULTIPLY,
    };

    virtual int32_t add(int32_t a, int32_t b) = 0;
    virtual int32_t subtract(int32_t a, int32_t b) = 0;
    virtual int32_t multiply(int32_t a, int32_t b) = 0;
};

// Server 端 Stub 实现
class BnNativeCalculator : public BnInterface<INativeCalculator> {
public:
    virtual status_t onTransact(uint32_t code,
                                const Parcel& data,
                                Parcel* reply,
                                uint32_t flags) override;
};

// 具体服务实现
class NativeCalculatorService : public BnNativeCalculator {
public:
    NativeCalculatorService();
    virtual ~NativeCalculatorService();

    virtual int32_t add(int32_t a, int32_t b) override;
    virtual int32_t subtract(int32_t a, int32_t b) override;
    virtual int32_t multiply(int32_t a, int32_t b) override;
};

} // namespace android
```

```cpp
// NativeCalculatorService.cpp
#include "NativeCalculatorService.h"
#include <binder/IPCThreadState.h>
#include <binder/ProcessState.h>
#include <binder/IServiceManager.h>
#include <utils/Log.h>

#define LOG_TAG "NativeCalculator"

namespace android {

IMPLEMENT_META_INTERFACE(NativeCalculator, "com.example.INativeCalculator");

// Stub onTransact - 处理来自 Client 的请求
status_t BnNativeCalculator::onTransact(uint32_t code,
                                         const Parcel& data,
                                         Parcel* reply,
                                         uint32_t flags) {
    switch (code) {
        case TRANSACTION_ADD: {
            CHECK_INTERFACE(INativeCalculator, data, reply);
            int32_t a = data.readInt32();
            int32_t b = data.readInt32();

            // 获取调用者信息
            uid_t callingUid = IPCThreadState::self()->getCallingUid();
            pid_t callingPid = IPCThreadState::self()->getCallingPid();
            ALOGD("add() called by UID=%d, PID=%d", callingUid, callingPid);

            int32_t result = add(a, b);
            reply->writeNoException();
            reply->writeInt32(result);
            return NO_ERROR;
        }

        case TRANSACTION_SUBTRACT: {
            CHECK_INTERFACE(INativeCalculator, data, reply);
            int32_t a = data.readInt32();
            int32_t b = data.readInt32();
            int32_t result = subtract(a, b);
            reply->writeNoException();
            reply->writeInt32(result);
            return NO_ERROR;
        }

        case TRANSACTION_MULTIPLY: {
            CHECK_INTERFACE(INativeCalculator, data, reply);
            int32_t a = data.readInt32();
            int32_t b = data.readInt32();
            int32_t result = multiply(a, b);
            reply->writeNoException();
            reply->writeInt32(result);
            return NO_ERROR;
        }

        default:
            return BBinder::onTransact(code, data, reply, flags);
    }
}

// 服务实现
NativeCalculatorService::NativeCalculatorService() {
    ALOGD("NativeCalculatorService created");
}

NativeCalculatorService::~NativeCalculatorService() {
    ALOGD("NativeCalculatorService destroyed");
}

int32_t NativeCalculatorService::add(int32_t a, int32_t b) {
    ALOGD("add(%d, %d)", a, b);
    return a + b;
}

int32_t NativeCalculatorService::subtract(int32_t a, int32_t b) {
    ALOGD("subtract(%d, %d)", a, b);
    return a - b;
}

int32_t NativeCalculatorService::multiply(int32_t a, int32_t b) {
    ALOGD("multiply(%d, %d)", a, b);
    return a * b;
}

} // namespace android

// 服务进程入口
int main(int argc, char** argv) {
    using namespace android;

    ALOGD("Starting NativeCalculatorService");

    // 初始化 ProcessState (打开 /dev/binder)
    sp<ProcessState> proc(ProcessState::self());

    // 获取 ServiceManager
    sp<IServiceManager> sm = defaultServiceManager();

    // 注册服务
    sm->addService(String16("native.calculator"),
                   new NativeCalculatorService());

    ALOGD("NativeCalculatorService registered");

    // 启动 Binder 线程池
    ProcessState::self()->startThreadPool();

    // 主线程也加入处理
    IPCThreadState::self()->joinThreadPool();

    return 0;
}
```

**Client 端 (C++) - Proxy 实现**

```cpp
// NativeCalculatorClient.cpp
#include <binder/IServiceManager.h>
#include <binder/IPCThreadState.h>
#include <binder/ProcessState.h>
#include <binder/Parcel.h>
#include <utils/Log.h>

#define LOG_TAG "NativeCalculatorClient"

namespace android {

// Client Proxy 实现
class BpNativeCalculator : public BpInterface<INativeCalculator> {
public:
    explicit BpNativeCalculator(const sp<IBinder>& impl)
        : BpInterface<INativeCalculator>(impl) {}

    virtual int32_t add(int32_t a, int32_t b) override {
        Parcel data, reply;
        data.writeInterfaceToken(INativeCalculator::getInterfaceDescriptor());
        data.writeInt32(a);
        data.writeInt32(b);

        // 跨进程调用
        remote()->transact(TRANSACTION_ADD, data, &reply);

        reply.readExceptionCode();
        return reply.readInt32();
    }

    virtual int32_t subtract(int32_t a, int32_t b) override {
        Parcel data, reply;
        data.writeInterfaceToken(INativeCalculator::getInterfaceDescriptor());
        data.writeInt32(a);
        data.writeInt32(b);

        remote()->transact(TRANSACTION_SUBTRACT, data, &reply);

        reply.readExceptionCode();
        return reply.readInt32();
    }

    virtual int32_t multiply(int32_t a, int32_t b) override {
        Parcel data, reply;
        data.writeInterfaceToken(INativeCalculator::getInterfaceDescriptor());
        data.writeInt32(a);
        data.writeInt32(b);

        remote()->transact(TRANSACTION_MULTIPLY, data, &reply);

        reply.readExceptionCode();
        return reply.readInt32();
    }
};

} // namespace android

// 客户端入口
int main(int argc, char** argv) {
    using namespace android;

    ALOGD("NativeCalculatorClient starting");

    // 初始化 ProcessState
    sp<ProcessState> proc(ProcessState::self());

    // 获取 ServiceManager
    sp<IServiceManager> sm = defaultServiceManager();

    // 获取服务
    sp<IBinder> binder = sm->getService(String16("native.calculator"));
    if (binder == nullptr) {
        ALOGE("Service not found!");
        return -1;
    }

    // 创建 Proxy
    sp<INativeCalculator> calculator =
        interface_cast<INativeCalculator>(binder);

    // 调用服务
    int32_t sum = calculator->add(100, 200);
    ALOGD("100 + 200 = %d", sum);

    int32_t diff = calculator->subtract(500, 300);
    ALOGD("500 - 300 = %d", diff);

    int32_t product = calculator->multiply(12, 12);
    ALOGD("12 * 12 = %d", product);

    return 0;
}
```

### 6.3 ServiceManager 原理与实现

```cpp
/**
 * ServiceManager 的核心实现
 * 位置: frameworks/native/cmds/servicemanager/
 */

// ServiceManager 数据结构
struct svcinfo {
    struct svcinfo *next;       // 链表
    uint32_t handle;            // Binder 句柄
    struct binder_death death;  // 死亡通知
    int allow_isolated;         // 是否允许 isolated 进程访问
    size_t len;                 // 服务名长度
    uint16_t name[0];           // 服务名 (UTF-16)
};

// 服务注册
int do_add_service(struct binder_state *bs,
                   const uint16_t *s, size_t len,
                   uint32_t handle, uid_t uid, int allow_isolated) {
    struct svcinfo *si;

    // 权限检查
    if (!svc_can_register(s, len, uid)) {
        ALOGE("add_service('%s',%x) uid=%d - PERMISSION DENIED",
              str8(s, len), handle, uid);
        return -1;
    }

    // 检查服务是否已存在
    si = find_svc(s, len);
    if (si) {
        if (si->handle) {
            // 服务已存在，更新句柄
            svcinfo_death(bs, si);
        }
        si->handle = handle;
    } else {
        // 创建新服务
        si = malloc(sizeof(*si) + (len + 1) * sizeof(uint16_t));
        si->handle = handle;
        si->len = len;
        memcpy(si->name, s, (len + 1) * sizeof(uint16_t));
        si->name[len] = '\0';
        si->death.func = (void*) svcinfo_death;
        si->death.ptr = si;
        si->allow_isolated = allow_isolated;
        si->next = svclist;
        svclist = si;  // 头插法
    }

    // 注册死亡通知
    binder_acquire(bs, handle);
    binder_link_to_death(bs, handle, &si->death);

    return 0;
}

// 服务查找
uint32_t do_find_service(const uint16_t *s, size_t len,
                         uid_t uid, pid_t spid) {
    struct svcinfo *si = find_svc(s, len);

    if (!si || !si->handle) {
        return 0;  // 服务不存在
    }

    // 权限检查
    if (!si->allow_isolated) {
        uid_t appid = uid % AID_USER;
        if (appid >= AID_ISOLATED_START && appid <= AID_ISOLATED_END) {
            return 0;  // isolated 进程无权访问
        }
    }

    return si->handle;
}
```

### 6.4 Parcel 底层原理

```cpp
/**
 * Parcel 内部结构详解
 * 位置: frameworks/native/libs/binder/Parcel.cpp
 */

class Parcel {
public:
    Parcel();
    ~Parcel();

    // 数据写入
    status_t writeInt32(int32_t val);
    status_t writeInt64(int64_t val);
    status_t writeFloat(float val);
    status_t writeDouble(double val);
    status_t writeString16(const String16& str);
    status_t writeStrongBinder(const sp<IBinder>& val);

    // 数据读取
    int32_t readInt32();
    int64_t readInt64();
    float readFloat();
    double readDouble();
    String16 readString16();
    sp<IBinder> readStrongBinder();

private:
    status_t            mError;
    uint8_t*            mData;          // 数据缓冲区
    size_t              mDataSize;      // 当前数据大小
    size_t              mDataCapacity;  // 缓冲区容量
    mutable size_t      mDataPos;       // 读写位置

    binder_size_t*      mObjects;       // Binder 对象偏移数组
    size_t              mObjectsSize;   // Binder 对象数量
    size_t              mObjectsCapacity;
};

// 写入 int32 的实现
status_t Parcel::writeInt32(int32_t val) {
    return writeAligned(val);
}

template<class T>
status_t Parcel::writeAligned(T val) {
    // 确保 4 字节对齐
    static_assert(PAD_SIZE_UNSAFE(sizeof(T)) == sizeof(T));

    if ((mDataPos + sizeof(val)) <= mDataCapacity) {
restart_write:
        *reinterpret_cast<T*>(mData + mDataPos) = val;
        mDataPos += sizeof(val);
        if (mDataPos > mDataSize) {
            mDataSize = mDataPos;
        }
        return NO_ERROR;
    }

    // 需要扩容
    status_t err = growData(sizeof(val));
    if (err == NO_ERROR) goto restart_write;
    return err;
}

// 写入 Binder 对象 (特殊处理)
status_t Parcel::writeStrongBinder(const sp<IBinder>& val) {
    return flatten_binder(ProcessState::self(), val, this);
}

status_t flatten_binder(const sp<ProcessState>& proc,
                        const sp<IBinder>& binder,
                        Parcel* out) {
    flat_binder_object obj;

    if (binder != nullptr) {
        BBinder* local = binder->localBinder();
        if (!local) {
            // 远程 Binder (Proxy)
            BpBinder* proxy = binder->remoteBinder();
            obj.hdr.type = BINDER_TYPE_HANDLE;
            obj.binder = 0;
            obj.handle = proxy ? proxy->handle() : 0;
            obj.cookie = 0;
        } else {
            // 本地 Binder (Stub)
            obj.hdr.type = BINDER_TYPE_BINDER;
            obj.binder = reinterpret_cast<uintptr_t>(local->getWeakRefs());
            obj.cookie = reinterpret_cast<uintptr_t>(local);
        }
    } else {
        // null Binder
        obj.hdr.type = BINDER_TYPE_BINDER;
        obj.binder = 0;
        obj.cookie = 0;
    }

    return finish_flatten_binder(binder, obj, out);
}
```

### 6.5 Binder 线程池管理

```cpp
/**
 * Binder 线程池详解
 */

// ProcessState: 每个进程一个
class ProcessState : public virtual RefBase {
public:
    static sp<ProcessState> self();

    // 打开 Binder 驱动
    int getContextObject(const sp<IBinder>& caller);

    // 启动线程池
    void startThreadPool();

    // 设置最大线程数
    void setThreadPoolMaxThreadCount(size_t maxThreads);

private:
    ProcessState(const char* driver);

    int                 mDriverFD;      // /dev/binder 文件描述符
    void*               mVMStart;       // mmap 起始地址
    size_t              mMaxThreads;    // 最大线程数

    Mutex               mLock;
    Vector<BBinder*>    mBindersByHandle;  // 句柄 → BBinder 映射
};

// IPCThreadState: 每个线程一个
class IPCThreadState {
public:
    static IPCThreadState* self();

    // 加入线程池处理请求
    void joinThreadPool(bool isMain = true);

    // 发起跨进程调用
    status_t transact(int32_t handle,
                      uint32_t code,
                      const Parcel& data,
                      Parcel* reply,
                      uint32_t flags);

    // 获取调用者信息
    uid_t getCallingUid() const;
    pid_t getCallingPid() const;

private:
    IPCThreadState();

    int                 mProcess;
    pid_t               mCallingPid;
    uid_t               mCallingUid;

    Parcel              mIn;   // 读取缓冲区
    Parcel              mOut;  // 写入缓冲区
};

// 线程池工作循环
void IPCThreadState::joinThreadPool(bool isMain) {
    mOut.writeInt32(isMain ? BC_ENTER_LOOPER : BC_REGISTER_LOOPER);

    status_t result;
    do {
        // 处理待处理的任务
        processPendingDerefs();

        // 阻塞等待请求
        result = getAndExecuteCommand();

        // 如果驱动请求创建新线程
        if (result == -ECONNREFUSED) {
            ALOGI("Binder driver refused");
            break;
        }

    } while (result != -ECONNREFUSED);

    mOut.writeInt32(BC_EXIT_LOOPER);
    talkWithDriver(false);
}

// 处理单个命令
status_t IPCThreadState::getAndExecuteCommand() {
    status_t result;
    int32_t cmd;

    // 与驱动通信
    result = talkWithDriver();
    if (result >= NO_ERROR) {
        size_t IN = mIn.dataAvail();
        if (IN < sizeof(int32_t)) return result;

        cmd = mIn.readInt32();

        // 处理命令
        result = executeCommand(cmd);
    }

    return result;
}

status_t IPCThreadState::executeCommand(int32_t cmd) {
    switch ((uint32_t)cmd) {
        case BR_TRANSACTION: {
            binder_transaction_data tr;
            result = mIn.read(&tr, sizeof(tr));

            // 保存调用者信息
            mCallingPid = tr.sender_pid;
            mCallingUid = tr.sender_euid;

            // 查找目标 BBinder
            if (tr.target.ptr) {
                // 调用 onTransact
                reinterpret_cast<BBinder*>(tr.cookie)->transact(
                    tr.code, buffer, &reply, tr.flags);
            }

            // 发送回复
            if ((tr.flags & TF_ONE_WAY) == 0) {
                sendReply(reply, 0);
            }
            break;
        }

        case BR_DEAD_BINDER: {
            BpBinder* proxy = (BpBinder*)mIn.readPointer();
            proxy->sendObituary();
            break;
        }

        // ... 其他命令
    }

    return result;
}
```

---

## 7. Binder 通信流程图解

### 7.1 完整通信流程

```
App 想获取 GPS 数据的完整流程:

┌──────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│  1. 服务注册阶段                                                          │
│  ──────────────────                                                      │
│                                                                          │
│  GPS Service                          ServiceManager                     │
│      │                                     │                             │
│      │  addService("location", binder)     │                             │
│      │ ──────────────────────────────────► │                             │
│      │                                     │  登记: location → 0x01      │
│      │                                     │                             │
│                                                                          │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  2. 服务获取阶段                                                          │
│  ──────────────────                                                      │
│                                                                          │
│  App (Client)                         ServiceManager                     │
│      │                                     │                             │
│      │  getService("location")             │                             │
│      │ ──────────────────────────────────► │                             │
│      │                                     │                             │
│      │  ◄─────────────────────────────────  │                             │
│      │       返回 Proxy (句柄 0x01)         │                             │
│      │                                     │                             │
│                                                                          │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  3. 服务调用阶段                                                          │
│  ──────────────────                                                      │
│                                                                          │
│  App (Proxy)        Binder Driver         GPS Service (Stub)            │
│      │                   │                      │                        │
│      │  transact()       │                      │                        │
│      │  [数据打包]        │                      │                        │
│      │ ────────────────► │                      │                        │
│      │                   │  copy_from_user      │                        │
│      │                   │  [1次拷贝到内核]      │                        │
│      │                   │                      │                        │
│      │                   │  唤醒 Server 线程     │                        │
│      │                   │ ────────────────────► │                        │
│      │                   │                      │  onTransact()          │
│      │                   │                      │  [解析数据]             │
│      │                   │                      │  [执行 getLocation]    │
│      │                   │                      │  [结果打包]             │
│      │                   │  ◄──────────────────  │                        │
│      │                   │     reply             │                        │
│      │  ◄─────────────── │                      │                        │
│      │    返回结果        │                      │                        │
│      │                   │                      │                        │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

### 7.2 形象比喻

```
假设 App 想找系统获取 GPS 数据:

1. ServiceManager (前台接待):
   系统启动时，GPS 服务就在这里登记了。

2. App (Client):
   跑到前台问："我要找 GPS 服务"。

3. ServiceManager:
   给了 App 一个号牌 (Binder Proxy/句柄)，
   说："你拿着这个号牌，对着它说话，GPS 服务就能听见。"

4. Binder 驱动 (传送门):
   - App 对着号牌喊："现在的经纬度是多少？"（写入数据）
   - 驱动把这句话瞬间传送到了 GPS 服务的耳朵里（内存映射）

5. GPS 服务 (Server):
   算了一下，通过驱动把结果"经度100，纬度30"传回去。

6. App:
   号牌里传来了声音，App 拿到了数据。
```

---

## 7. Binder 在逆向中的应用

### 8.1 Hook Binder 调用

```javascript
/**
 * Frida Hook Binder.transact
 * 监控所有跨进程调用
 */
Java.perform(function() {
    var Binder = Java.use("android.os.Binder");

    Binder.transact.overload('int', 'android.os.Parcel',
                              'android.os.Parcel', 'int')
        .implementation = function(code, data, reply, flags) {

        console.log("[Binder.transact]");
        console.log("  code: " + code);
        console.log("  flags: " + flags);

        // 读取 Parcel 数据
        data.setDataPosition(0);
        var interfaceToken = data.readInterfaceToken();
        console.log("  interface: " + interfaceToken);
        data.setDataPosition(0);

        // 调用原方法
        var result = this.transact(code, data, reply, flags);

        // 读取返回数据
        reply.setDataPosition(0);
        console.log("  reply size: " + reply.dataSize());

        return result;
    };
});
```

### 8.2 监控系统服务调用

```javascript
/**
 * Hook ServiceManager.getService
 * 监控 App 获取了哪些系统服务
 */
Java.perform(function() {
    var ServiceManager = Java.use("android.os.ServiceManager");

    ServiceManager.getService.overload('java.lang.String')
        .implementation = function(name) {

        console.log("[ServiceManager.getService] " + name);

        // 打印调用栈
        console.log(Java.use("android.util.Log")
            .getStackTraceString(Java.use("java.lang.Exception").$new()));

        return this.getService(name);
    };
});
```

### 8.3 分析 AIDL 接口

```javascript
/**
 * 动态分析 AIDL 接口
 */
Java.perform(function() {
    // Hook 所有继承自 Binder 的类
    Java.enumerateLoadedClasses({
        onMatch: function(className) {
            if (className.includes("$Stub")) {
                try {
                    var cls = Java.use(className);
                    console.log("[AIDL Stub] " + className);

                    // Hook onTransact
                    cls.onTransact.overload('int', 'android.os.Parcel',
                                            'android.os.Parcel', 'int')
                        .implementation = function(code, data, reply, flags) {
                        console.log("  [" + className + "] code: " + code);
                        return this.onTransact(code, data, reply, flags);
                    };
                } catch (e) {}
            }
        },
        onComplete: function() {}
    });
});
```

### 8.4 Binder 数据解析

```javascript
/**
 * 解析 Parcel 数据
 */
function parseParcel(parcel) {
    parcel.setDataPosition(0);

    var result = {
        dataSize: parcel.dataSize(),
        dataPosition: parcel.dataPosition(),
        dataCapacity: parcel.dataCapacity()
    };

    // 尝试读取不同类型的数据
    try {
        result.interfaceToken = parcel.readInterfaceToken();
    } catch (e) {}

    parcel.setDataPosition(0);

    // Dump 原始数据
    var data = parcel.marshall();
    result.rawData = hexdump(data, { length: Math.min(data.length, 256) });

    return result;
}
```

---

## 8. 总结

### 8.1 Binder 核心要点

| 特性 | 说明 |
|-----|------|
| **地位** | Android 的神经系统 |
| **架构** | C/S 架构：Client、Server、ServiceManager、Driver |
| **性能** | 1 次拷贝 (mmap 内存映射) |
| **安全** | 内核层 UID/PID 校验 |
| **易用** | AIDL 封装 RPC 调用 |

### 8.2 限制

1. **传输大小限制**：通常 1MB - 8KB，过大的图片不要通过 Binder 传
2. **同步调用**：Client 发起的调用通常是同步的，Server 耗时太久会导致 ANR
3. **Android 特有**：不是标准 Linux IPC，只能在 Android 中使用

### 8.3 Binder 的重要性

理解了 Binder，你就理解了：
- 为什么 Android App 可以互相调起
- 为什么系统服务可以管理所有 App
- 插件化和组件化开发的底层基石
- LSPosed 等框架的跨进程通信机制

---

**推荐下一步**：
- [ART 运行时](./art_runtime.md)
- [Magisk 与 LSPosed 原理](../Advanced/magisk_lsposed_internals.md)
