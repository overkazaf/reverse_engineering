---
title: "Smali 语法入门"
date: 2024-07-12
weight: 10
---

# Smali 语法入门

Smali/Baksmali 是 Dalvik 虚拟机字节码的汇编器/反汇编器。Smali 是对 DEX 格式的一种人类可读的表示，允许我们精确地查看和修改应用的行为。理解 Smali 是进行 Android 应用静态 patching（修改后重打包）的关键。

## 目录

1. [基本概念](#基本概念)
2. [数据类型与表示](#数据类型与表示)
3. [文件与类结构](#文件与类结构)
4. [常用指令](#常用指令)
5. [Smali 实战：修改方法](#smali-实战修改方法)

---

## 基本概念

### 寄存器 (Registers)

Dalvik VM 是基于寄存器的。方法内的局部变量存储在寄存器中。

| 寄存器类型          | 说明           |
| ------------------- | -------------- |
| `v0`, `v1`, `v2`... | 本地变量寄存器 |
| `p0`, `p1`, `p2`... | 方法参数寄存器 |

**关于 `p0` 的特殊说明**：

- 对于**非静态方法**，`p0` 总是指向 `this`（当前对象实例），参数从 `p1` 开始
- 对于**静态方法**，参数从 `p0` 开始

**示例**：一个有两个参数的非静态方法：

- `p0` = `this`
- `p1` = 第一个参数
- `p2` = 第二个参数

### 常用声明

| 声明        | 说明                               |
| ----------- | ---------------------------------- |
| `.locals`   | 声明方法使用的本地变量寄存器数量   |
| `.prologue` | 方法体的序言部分                   |
| `.line`     | 对应原始 Java 代码的行号，用于调试 |

---

## 数据类型与表示

Smali 使用特定的描述符来表示 Java 中的数据类型。

| Smali 类型        | Java 类型           | 描述                            |
| ----------------- | ------------------- | ------------------------------- |
| `V`               | `void`              | 空返回类型                      |
| `Z`               | `boolean`           | 布尔值                          |
| `B`               | `byte`              | 字节                            |
| `S`               | `short`             | 短整型                          |
| `C`               | `char`              | 字符                            |
| `I`               | `int`               | 整型                            |
| `J`               | `long`              | 长整型（占用两个寄存器）        |
| `F`               | `float`             | 浮点型                          |
| `D`               | `double`            | 双精度浮点型（占用两个寄存器）  |
| `L<包名>/<类名>;` | `package.ClassName` | 对象类型，以 `L` 开头，`;` 结尾 |
| `[<类型>`         | `type[]`            | 数组类型                        |

### 类型表示示例

| Smali                  | Java                   |
| ---------------------- | ---------------------- |
| `Ljava/lang/String;`   | `java.lang.String`     |
| `[I`                   | `int[]`                |
| `[[Ljava/lang/Object;` | `java.lang.Object[][]` |
| `[Ljava/lang/String;`  | `String[]`             |

---

## 文件与类结构

每个 `.smali` 文件对应一个 Java 类。

### 类定义

```smali
# 定义类、访问修饰符和完整类路径
.class public Lcom/example/app/MainActivity;

# 定义父类
.super Landroid/app/Activity;

# 定义源文件名（可选）
.source "MainActivity.java"
```

### 字段定义

```smali
# 格式: .field <访问修饰符> [static] [final] <字段名>:<字段类型>

# 实例字段
.field private TAG:Ljava/lang/String;

# 静态常量字段
.field public static final MY_CONSTANT:I = 0x1
```

### 方法定义

```smali
# 格式: .method <访问修饰符> [static] [final] <方法名>(<参数类型>)<返回类型>
.method public onCreate(Landroid/os/Bundle;)V
    # 声明本地变量寄存器数量
    .locals 3

    # 声明参数寄存器
    .param p1, "savedInstanceState"    # p1 是 savedInstanceState

    # 方法体开始
    .prologue
    .line 15

    # ... Smali 指令 ...

    # 方法返回
    return-void
.end method
```

---

## 常用指令

### 赋值与移动指令

| 指令                       | 说明                                          |
| -------------------------- | --------------------------------------------- |
| `const-string v1, "Hello"` | 将字符串 "Hello" 赋值给 `v1`                  |
| `const/4 v0, 0x1`          | 将 4 位常量 1 赋值给 `v0`                     |
| `const/16 v0, 0x100`       | 将 16 位常量赋值给 `v0`                       |
| `move-result-object v0`    | 将上一个 `invoke` 返回的对象结果移动到 `v0`   |
| `move-result v0`           | 将上一个 `invoke` 返回的非对象结果移动到 `v0` |
| `move-exception v0`        | 在 `catch` 块中，将捕获的异常对象移动到 `v0`  |

### 对象操作指令

| 指令                                                                      | 说明         |
| ------------------------------------------------------------------------- | ------------ |
| `new-instance v0, Ljava/lang/StringBuilder;`                              | 创建新实例   |
| `iget-object v0, p0, Lcom/example/MyClass;->myField:Ljava/lang/String;`   | 获取实例字段 |
| `iput-object v1, p0, Lcom/example/MyClass;->myField:Ljava/lang/String;`   | 设置实例字段 |
| `sget-object v0, Lcom/example/Constants;->SOME_STRING:Ljava/lang/String;` | 获取静态字段 |
| `sput-object v0, Lcom/example/Constants;->SOME_STRING:Ljava/lang/String;` | 设置静态字段 |

### 方法调用指令

| 指令                                                                               | 说明                               |
| ---------------------------------------------------------------------------------- | ---------------------------------- |
| `invoke-virtual {p0, p1}, Lcom/example/MyClass;->myMethod(I)V`                     | 调用虚方法（公有/保护方法）        |
| `invoke-direct {p0}, Ljava/lang/Object;-><init>()V`                                | 调用直接方法（私有方法或构造函数） |
| `invoke-static {v0}, Landroid/util/Log;->d(Ljava/lang/String;Ljava/lang/String;)I` | 调用静态方法                       |
| `invoke-super {p0, p1}, Landroid/app/Activity;->onCreate(Landroid/os/Bundle;)V`    | 调用父类方法                       |
| `invoke-interface {p0, v0}, Ljava/util/List;->add(Ljava/lang/Object;)Z`            | 调用接口方法                       |

### 跳转/条件指令

| 指令                      | 说明                                           |
| ------------------------- | ---------------------------------------------- |
| `goto :label_10`          | 无条件跳转到 `:label_10`                       |
| `if-eqz v0, :label_10`    | 如果 `v0 == 0`（或 `false`/`null`），则跳转    |
| `if-nez v0, :label_10`    | 如果 `v0 != 0`（或 `true`/`not null`），则跳转 |
| `if-eq v0, v1, :label_10` | 如果 `v0 == v1`，则跳转                        |
| `if-ne v0, v1, :label_10` | 如果 `v0 != v1`，则跳转                        |
| `if-lt v0, v1, :label_10` | 如果 `v0 < v1`，则跳转                         |
| `if-ge v0, v1, :label_10` | 如果 `v0 >= v1`，则跳转                        |

### 运算指令

| 指令                   | 说明                                   |
| ---------------------- | -------------------------------------- |
| `add-int v0, v1, v2`   | `v0 = v1 + v2`（整型加法）             |
| `sub-int v0, v1, v2`   | `v0 = v1 - v2`（整型减法）             |
| `mul-int v0, v1, v2`   | `v0 = v1 * v2`（整型乘法）             |
| `div-int v0, v1, v2`   | `v0 = v1 / v2`（整型除法）             |
| `mul-int/2addr v0, v1` | `v0 = v0 * v1`（结果存回第一个寄存器） |

---

## Smali 实战：修改方法

假设我们要修改一个方法，让它总是返回 `true`。

### 原始 Java 代码

```java
public class LicenseCheck {
    public boolean isLicensed() {
        // ... 复杂的检查逻辑 ...
        return false;
    }
}
```

### 原始 Smali 代码

```smali
.method public isLicensed()Z
    .locals 1

    # ... 复杂检查逻辑对应的 smali 指令 ...

    const/4 v0, 0x0    # v0 = 0 (false)
    return v0
.end method
```

### 修改后的 Smali 代码

```smali
.method public isLicensed()Z
    .locals 1

    # 删除所有复杂检查逻辑，直接返回 true

    const/4 v0, 0x1    # v0 = 1 (true)
    return v0
.end method
```

### 修改步骤

1. 使用 `apktool d app.apk -o app_decoded/` 解包 APK
2. 找到并修改目标 `.smali` 文件
3. 使用 `apktool b app_decoded/ -o new_app.apk` 重新打包
4. 用 `jarsigner` 或 `apksigner` 对 `new_app.apk` 进行签名

---

## 常见修改技巧

### 1. 让方法返回固定值

```smali
# 返回 true
const/4 v0, 0x1
return v0

# 返回 false
const/4 v0, 0x0
return v0

# 返回 null
const/4 v0, 0x0
return-object v0
```

### 2. 跳过方法体直接返回

```smali
.method public checkSomething()V
    .locals 0

    # 直接返回，跳过所有检查
    return-void
.end method
```

### 3. 修改条件判断

```smali
# 原始：if-eqz v0, :skip  (如果 v0 == 0 则跳过)
# 修改：if-nez v0, :skip  (如果 v0 != 0 则跳过)
# 或者直接：goto :skip    (无条件跳过)
```
