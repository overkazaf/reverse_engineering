# JNI 代码示例与练习

这是一个简单的 JNI (Java Native Interface) 示例项目，展示了 Java 和 C/C++ 代码之间的交互。

## 项目结构

```
jni/
├── README.md                   # 项目说明
├── CMakeLists.txt              # CMake 构建配置
├── src/
│   ├── com/example/JNIDemo.java # Java 类定义
│   └── native/
│       ├── jni_demo.c          # JNI 实现 (C语言)
│       ├── jni_demo.h          # JNI 头文件
│       └── crypto_utils.c      # 加密工具示例
├── include/
│   └── jni.h                   # JNI 头文件 (标准)
└── build/                      # 构建输出目录
```

## 功能特性

本示例包含以下 JNI 功能演示：

1. **基础数据类型转换** - 字符串、整数、布尔值等
2. **数组操作** - 字节数组的读取和写入
3. **加密算法** - 简单的 XOR 加密示例
4. **字符串处理** - UTF-8 字符串操作
5. **错误处理** - JNI 异常处理机制
6. **回调机制** - 从 Native 代码调用 Java 方法

## 编译步骤

### 前提条件

- 安装 CMake (>= 3.10)
- 安装 JDK (推荐 OpenJDK 8+)
- 安装 GCC 或 Clang 编译器

### 构建命令

```bash
# 1. 创建构建目录
mkdir build
cd build

# 2. 配置 CMake
cmake ..

# 3. 编译项目
make

# 4. 运行测试
java -Djava.library.path=. -cp . com.example.JNIDemo
```

### Android 交叉编译

```bash
# 使用 Android NDK
export ANDROID_NDK=/path/to/ndk
mkdir build-android
cd build-android

cmake -DCMAKE_TOOLCHAIN_FILE=$ANDROID_NDK/build/cmake/android.toolchain.cmake \
      -DANDROID_ABI=arm64-v8a \
      -DANDROID_PLATFORM=android-21 \
      ..

make
```

## 学习要点

1. **JNI 函数命名规则**：`Java_包名_类名_方法名`
2. **数据类型映射**：Java 类型到 JNI 类型的转换
3. **内存管理**：正确释放 JNI 分配的资源
4. **异常处理**：检查和处理 JNI 异常
5. **性能优化**：避免频繁的 JNI 调用

## 常见问题

- **UnsatisfiedLinkError**: 检查库文件路径和函数名
- **内存泄漏**: 确保调用相应的 Release 函数
- **编码问题**: 使用 Modified UTF-8 编码

## 调试技巧

1. 使用 `javah` 生成标准的 JNI 头文件
2. 启用 JNI 检查：`-Xcheck:jni`
3. 使用 GDB 调试 Native 代码
4. 使用 Frida 进行动态分析