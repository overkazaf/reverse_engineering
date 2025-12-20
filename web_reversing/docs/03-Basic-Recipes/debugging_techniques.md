# 调试技巧与断点设置

## 概述

调试是逆向工程的核心技能。掌握高级调试技巧可以大幅提升逆向效率，快速定位关键代码，理解程序逻辑。

---

## 断点类型

### 1. 行断点 (Line Breakpoint)

最基本的断点类型，点击行号即可设置。

**快捷键**:

- 设置/取消断点: 点击行号
- 禁用所有断点: `Ctrl+F8` (Windows) / `Cmd+F8` (Mac)

**技巧**:

- 在函数入口设置断点
- 在可疑的加密、签名函数处设置

### 2. 条件断点 (Conditional Breakpoint)

只有满足特定条件时才触发的断点。

**设置方法**:

1. 右键行号
2. 选择 "Add conditional breakpoint"
3. 输入条件表达式

**示例**:

```javascript
// 只有当 user_id 为 12345 时才断点
user_id === 12345;

// 只有当参数包含 'admin' 时才断点
params.username.includes("admin");

// 循环中每 100 次才断点
i % 100 === 0;
```

**使用场景**:

- 大量循环中定位特定数据
- 多次调用的函数中定位特定参数

### 3. 日志点 (Logpoint)

不暂停执行，只输出日志。

**设置方法**:

1. 右键行号
2. 选择 "Add logpoint"
3. 输入要输出的表达式

**示例**:

```javascript
// 输出变量值
"User ID:", user_id;

// 输出对象
"Params:", params;

// 输出函数返回值
"Result:", calculateSign(params);
```

**优势**:

- 不影响代码执行流程
- 适合追踪变量变化
- 比插入 console.log 更方便

### 4. DOM 断点 (DOM Breakpoint)

监控 DOM 变化。

**类型**:

- **Subtree modifications**: 子节点变化
- **Attribute modifications**: 属性变化
- **Node removal**: 节点移除

**使用场景**:

- 追踪动态生成的验证码图片
- 追踪价格数据的动态更新
- 追踪表单的自动填充

**设置方法**:

1. Elements 面板选中元素
2. 右键 -> Break on
3. 选择断点类型

### 5. XHR/Fetch 断点

在网络请求发送时触发断点。

**设置方法**:

1. Sources 面板
2. 右侧 "XHR/fetch Breakpoints"
3. 输入 URL 关键词

**示例**:

```
/api/login
/api/user/info
sign
token
```

**使用场景**:

- 快速定位 API 调用代码
- 追踪请求参数生成逻辑

### 6. 事件断点 (Event Listener Breakpoint)

在特定事件触发时断点。

**常用事件**:

- Mouse -> click
- Mouse -> mousedown/mouseup
- Keyboard -> keydown/keyup
- Form -> submit
- Timer -> setTimeout/setInterval

**使用场景**:

- 不知道点击事件绑定在哪里
- 追踪表单提交逻辑
- 追踪定时器中的反调试代码

---

## 单步执行

### 快捷键

| 操作          | Windows/Linux | Mac         | 说明                 |
| ------------- | ------------- | ----------- | -------------------- |
| **Step Over** | `F10`         | `F10`       | 跳过函数，执行下一行 |
| **Step Into** | `F11`         | `F11`       | 进入函数内部         |
| **Step Out**  | `Shift+F11`   | `Shift+F11` | 跳出当前函数         |
| **Continue**  | `F8`          | `F8`        | 继续执行到下一个断点 |
| **Resume**    | `F8`          | `F8`        | 恢复脚本执行         |

### 使用技巧

**Step Over vs Step Into**:

- 如果下一行是库函数（如 `JSON.stringify`），用 **Step Over**
- 如果下一行是业务函数（如 `generateSign`），用 **Step Into**

**Step Out**:

- 进错函数了？用 **Step Out** 快速返回

**Continue**:

- 循环中不想一步步执行？在循环后设置断点，用 **Continue** 跳过

---

## 调用栈分析 (Call Stack)

### 查看调用栈

断点停下后，右侧 Call Stack 面板显示函数调用链：

```
generateRequest (main.js:123)
  |- getData (utils.js:45)
       |- onClick (app.js:789)
            |- <anonymous>
```

### 使用技巧

1. **从下往上看**: 最下面是事件入口，最上面是当前位置
2. **点击跳转**: 点击任意一层可以查看该层的代码和变量
3. **过滤库文件**: 右键 -> Blackbox script，隐藏第三方库

---

## Scope 变量查看

### 作用域类型

- **Local**: 当前函数的局部变量
- **Closure**: 闭包变量
- **Global**: 全局变量

### 技巧

**查看复杂对象**:

- 右键 -> Store as global variable
- 在 Console 中操作该变量（会自动命名为 `temp1`, `temp2`...）

**修改变量**:

- 双击变量值可以直接修改
- 用于测试不同参数的影响

---

## Console 调试技巧

### 条件输出

```javascript
// 只有当条件满足时才输出
if (user_id === 12345) {
  console.log("Target user:", user_id);
}
```

### 分组输出

```javascript
console.group("User Info");
console.log("ID:", user_id);
console.log("Name:", username);
console.groupEnd();
```

### 表格输出

```javascript
const users = [
  { id: 1, name: "Alice" },
  { id: 2, name: "Bob" },
];
console.table(users);
```

### 性能测量

```javascript
console.time("encrypt");
// ... 加密代码
console.timeEnd("encrypt"); // encrypt: 12.345ms
```

### 堆栈追踪

```javascript
console.trace("Where am I?");
```

---

## 高级调试技巧

### 1. Blackbox 第三方库

避免调试时进入 jQuery、React 等第三方库：

**方法一**:

1. Settings -> Blackboxing
2. 添加模式：`/node_modules/`, `/jquery.*.js`

**方法二**:

- 在 Call Stack 中右键 -> Blackbox script

### 2. 异步代码调试

**问题**: 异步代码断点后，Call Stack 断裂。

**解决**: 勾选 "Async" 按钮（Call Stack 上方），显示完整异步调用栈。

### 3. Source Map

**问题**: 生产环境代码被压缩/混淆，无法调试。

**解决**: 如果有 Source Map 文件（`.map`），DevTools 会自动加载原始代码。

### 4. Local Overrides (本地替换)

**用途**: 修改线上 JS 文件并保存，刷新后依然生效。

**步骤**:

1. Sources -> Overrides
2. 选择本地文件夹
3. 修改文件并保存 (`Ctrl+S`)

**应用**:

- 删除反调试代码
- 添加日志输出
- 修改加密逻辑测试

### 5. Snippets (代码片段)

**用途**: 保存常用的 Hook 脚本，快速执行。

**步骤**:

1. Sources -> Snippets
2. 新建 Snippet
3. 粘贴脚本，`Ctrl+Enter` 执行

---

## 反调试对抗

### 1. 无限 debugger

**特征**:

```javascript
setInterval(() => {
  debugger;
}, 100);
```

**绕过方法**:

- **方法一**: 右键断点行 -> "Never pause here"
- **方法二**: Hook `Function.prototype.constructor` (见 [Hook 脚本](../07-Scripts/javascript_hook_scripts.md))
- **方法三**: Local Overrides 删除该段代码

### 2. 检测 DevTools 打开

**特征**:

```javascript
setInterval(() => {
  if (window.outerWidth - window.innerWidth > 160) {
    alert("DevTools detected!");
    window.location.href = "about:blank";
  }
}, 1000);
```

**绕过方法**:

- 使用独立窗口模式（Undock into separate window）
- Hook `window.outerWidth` 和 `window.innerWidth`

### 3. 检测时间差

**特征**:

```javascript
let start = Date.now();
debugger;
let end = Date.now();
if (end - start > 100) {
  console.log("Debugger detected!");
}
```

**绕过方法**:

- Hook `Date.now()` 返回固定增量

---

## 实战示例

### 示例一：追踪加密函数

**目标**: 找到生成 `sign` 参数的函数

**步骤**:

1. Network 面板找到包含 `sign` 的请求
2. 全局搜索 `sign`（可能有上百个结果）
3. 设置 XHR 断点，URL 填 `/api/`
4. 刷新页面，断点停下
5. 查看 Call Stack，定位到 `generateSign` 函数
6. 单步调试，理解加密逻辑

### 示例二：绕过滑块验证码

**目标**: 分析滑块验证逻辑

**步骤**:

1. 右键滑块元素 -> Break on -> Attribute modifications
2. 拖动滑块，断点停下
3. 查看 Call Stack，找到验证函数
4. 分析轨迹生成和验证逻辑

---

## 相关章节

- [JavaScript Hook 脚本](../07-Scripts/javascript_hook_scripts.md)
- [浏览器开发者工具](../02-Tooling/browser_devtools.md)
- [逆向工程工作流](./re_workflow.md)
