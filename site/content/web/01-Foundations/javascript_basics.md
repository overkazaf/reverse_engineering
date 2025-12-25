---
title: "JavaScript 基础"
date: 2024-04-17
tags: ["Web", "HTTP", "RSA", "签名验证", "JavaScript", "加密分析"]
weight: 10
---

# JavaScript 基础

## 概述

JavaScript 是 Web 逆向工程中最重要的语言。掌握 JavaScript 的核心概念对于理解和分析 Web 应用至关重要。

---

## 数据类型

### 基本类型（Primitive Types）

```javascript
// Number
let num = 42;
let float = 3.14;
let hex = 0xff; // 255

// String
let str = "Hello";
let str2 = "World";
let template = `${str} ${str2}`; // "Hello World"

// Boolean
let isTrue = true;
let isFalse = false;

// Undefined
let notDefined;
console.log(notDefined); // undefined

// Null
let empty = null;

// Symbol (ES6+)
let sym = Symbol("description");

// BigInt (ES2020+)
let bigNum = 1234567890123456789012345678901234567890n;
```

### 引用类型（Reference Types）

```javascript
// Object
let obj = {
name: "John",
age: 30,
greet: function () {
console.log("Hello");
},
};

// Array
let arr = [1, 2, 3, 4, 5];
let mixed = [1, "two", true, null, { key: "value" }];

// Function
function myFunc() {
return "Hello";
}

// Date
let date = new Date();

// RegExp
let regex = /pattern/gi;
```

---

## 变量声明

### var vs let vs const

```javascript
// var: 函数作用域，存在变量提升
var x = 1;
if (true) {
var x = 2; // 同一个变量
console.log(x); // 2
}
console.log(x); // 2

// let: 块作用域，无变量提升
let y = 1;
if (true) {
let y = 2; // 不同的变量
console.log(y); // 2
}
console.log(y); // 1

// const: 块作用域，常量（引用不可变）
const z = 1;
// z = 2; // 错误：不能重新赋值

const obj = { name: "John" };
obj.name = "Jane"; // 可以修改对象属性
// obj = {}; // 错误：不能重新赋值
```

---

## 作用域与闭包

### 作用域链

```javascript
let global = "global";

function outer() {
let outerVar = "outer";

function inner() {
let innerVar = "inner";
console.log(global); // "global"
console.log(outerVar); // "outer"
console.log(innerVar); // "inner"
}

inner();
}

outer();
```

### 闭包（Closure）

```javascript
function createCounter() {
let count = 0;

return {
increment: function () {
count++;
return count;
},
decrement: function () {
count--;
return count;
},
getCount: function () {
return count;
},
};
}

let counter = createCounter();
console.log(counter.increment()); // 1
console.log(counter.increment()); // 2
console.log(counter.getCount()); // 2
```

**在逆向中的应用**：很多 JS 加密函数使用闭包来隐藏密钥。

---

## this 关键字

### this 的绑定规则

```javascript
// 1. 默认绑定 - 指向全局对象（严格模式下为 undefined）
function defaultBinding() {
console.log(this); // window (浏览器) 或 global (Node.js)
}

// 2. 隐式绑定 - 指向调用对象
let obj = {
name: "John",
greet: function () {
console.log(this.name);
},
};
obj.greet(); // "John"

// 3. 显式绑定 - 使用 call/apply/bind
function greet() {
console.log(this.name);
}
let person = { name: "Jane" };
greet.call(person); // "Jane"
greet.apply(person); // "Jane"
let boundGreet = greet.bind(person);
boundGreet(); // "Jane"

// 4. new 绑定 - 指向新创建的对象
function Person(name) {
this.name = name;
}
let p = new Person("Bob");
console.log(p.name); // "Bob"

// 5. 箭头函数 - 继承外层作用域的 this
let obj2 = {
name: "Alice",
greet: () => {
console.log(this.name); // undefined（继承外层 this）
},
greet2: function () {
setTimeout(() => {
console.log(this.name); // "Alice"（继承 greet2 的 this）
}, 100);
},
};
```

---

## 原型与原型链

### 原型基础

```javascript
function Person(name) {
this.name = name;
}

// 在原型上定义方法
Person.prototype.greet = function () {
console.log(`Hello, I'm ${this.name}`);
};

let p1 = new Person("John");
let p2 = new Person("Jane");

p1.greet(); // "Hello, I'm John"
p2.greet(); // "Hello, I'm Jane"

// p1 和 p2 共享同一个 greet 方法
console.log(p1.greet === p2.greet); // true
```

### 原型链

```javascript
let obj = { a: 1 };

// 原型链：obj -> Object.prototype -> null
console.log(obj.__proto__ === Object.prototype); // true
console.log(Object.prototype.__proto__); // null

// 属性查找会沿着原型链向上查找
console.log(obj.toString); // [Function: toString] (来自 Object.prototype)
```

### Class 语法（ES6+）

```javascript
class Person {
constructor(name) {
this.name = name;
}

greet() {
console.log(`Hello, I'm ${this.name}`);
}

static species() {
return "Homo sapiens";
}
}

class Student extends Person {
constructor(name, grade) {
super(name);
this.grade = grade;
}

study() {
console.log(`${this.name} is studying in grade ${this.grade}`);
}
}

let student = new Student("Alice", 10);
student.greet(); // "Hello, I'm Alice"
student.study(); // "Alice is studying in grade 10"
```

---

## 异步编程

### 回调函数（Callback）

```javascript
function fetchData(callback) {
setTimeout(() => {
callback("Data loaded");
}, 1000);
}

fetchData((data) => {
console.log(data); // "Data loaded" (1秒后)
});
```

### Promise

```javascript
function fetchData() {
return new Promise((resolve, reject) => {
setTimeout(() => {
let success = true;
if (success) {
resolve("Data loaded");
} else {
reject("Error occurred");
}
}, 1000);
});
}

// 使用 .then()
fetchData()
.then((data) => console.log(data))
.catch((error) => console.error(error));

// Promise 链式调用
fetch("https://api.example.com/data")
.then((response) => response.json())
.then((data) => console.log(data))
.catch((error) => console.error(error));
```

### Async/Await（ES2017+）

```javascript
async function loadData() {
try {
let response = await fetch("https://api.example.com/data");
let data = await response.json();
console.log(data);
} catch (error) {
console.error(error);
}
}

loadData();
```

---

## 常用内置对象和方法

### Array 方法

```javascript
let arr = [1, 2, 3, 4, 5];

// 遍历
arr.forEach((item) => console.log(item));

// 映射
let doubled = arr.map((x) => x * 2); // [2, 4, 6, 8, 10]

// 过滤
let evens = arr.filter((x) => x % 2 === 0); // [2, 4]

// 归约
let sum = arr.reduce((acc, x) => acc + x, 0); // 15

// 查找
let found = arr.find((x) => x > 3); // 4
let index = arr.findIndex((x) => x > 3); // 3

// 判断
let hasEven = arr.some((x) => x % 2 === 0); // true
let allPositive = arr.every((x) => x > 0); // true

// 展平
let nested = [1, [2, [3, 4]]];
let flat = nested.flat(2); // [1, 2, 3, 4]
```

### String 方法

```javascript
let str = "Hello World";

// 查找
str.indexOf("World"); // 6
str.includes("World"); // true
str.startsWith("Hello"); // true
str.endsWith("World"); // true

// 提取
str.substring(0, 5); // "Hello"
str.slice(0, 5); // "Hello"
str.substr(0, 5); // "Hello" (已废弃)

// 替换
str.replace("World", "JavaScript"); // "Hello JavaScript"
str.replaceAll("l", "L"); // "HeLLo WorLd"

// 分割与连接
str.split(" "); // ["Hello", "World"]
["Hello", "World"].join("-"); // "Hello-World"

// 大小写
str.toLowerCase(); // "hello world"
str.toUpperCase(); // "HELLO WORLD"

// 去空格
" hello ".trim(); // "hello"
" hello ".trimStart(); // "hello "
" hello ".trimEnd(); // " hello"
```

### Object 方法

```javascript
let obj = { a: 1, b: 2, c: 3 };

// 获取键、值、条目
Object.keys(obj); // ["a", "b", "c"]
Object.values(obj); // [1, 2, 3]
Object.entries(obj); // [["a", 1], ["b", 2], ["c", 3]]

// 合并对象
let merged = Object.assign({}, obj, { d: 4 }); // {a: 1, b: 2, c: 3, d: 4}
let spread = { ...obj, d: 4 }; // {a: 1, b: 2, c: 3, d: 4}

// 冻结对象
Object.freeze(obj);
obj.a = 100; // 无效
console.log(obj.a); // 1

// 密封对象
Object.seal(obj);
obj.a = 100; // 可以修改
delete obj.a; // 无效
```

---

## 正则表达式

### 基本语法

```javascript
// 创建正则
let regex1 = /pattern/gi;
let regex2 = new RegExp("pattern", "gi");

// 标志
// g - 全局匹配
// i - 忽略大小写
// m - 多行匹配
// s - . 匹配换行符
// u - Unicode 模式
// y - 粘性匹配

// 常用方法
let str = "Hello World 123";

str.match(/\d+/); // ["123"]
str.search(/World/); // 6
str.replace(/\d+/, "456"); // "Hello World 456"
str.split(/\s+/); // ["Hello", "World", "123"]

/World/.test(str); // true
/\d+/.exec(str); // ["123", index: 12, input: "Hello World 123"]
```

### 常用模式

```javascript
// 数字
/\d+/ // 一个或多个数字
/^\d+$/ // 整行都是数字

// 字母
/[a-zA-Z]+/ // 一个或多个字母

// 邮箱
/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/

// URL
/^https?:\/\/.+/

// 手机号（中国）
/^1[3-9]\d{9}$/

// 捕获组
let match = "2024-12-17".match(/(\d{4})-(\d{2})-(\d{2})/);
// match[0] = "2024-12-17"
// match[1] = "2024"
// match[2] = "12"
// match[3] = "17"
```

---

## 错误处理

```javascript
// try-catch
try {
// 可能出错的代码
let result = riskyOperation();
} catch (error) {
console.error("Error occurred:", error.message);
} finally {
// 无论是否出错都会执行
cleanup();
}

// 抛出错误
function divide(a, b) {
if (b === 0) {
throw new Error("Division by zero");
}
return a / b;
}

// 自定义错误
class CustomError extends Error {
constructor(message) {
super(message);
this.name = "CustomError";
}
}

throw new CustomError("Something went wrong");
```

---

## 模块化

### ES6 模块

```javascript
// math.js
export function add(a, b) {
return a + b;
}

export const PI = 3.14159;

export default class Calculator {
// ...
}

// main.js
import Calculator, { add, PI } from "./math.js";
import * as math from "./math.js";

console.log(add(1, 2)); // 3
console.log(PI); // 3.14159
let calc = new Calculator();
```

### CommonJS（Node.js）

```javascript
// math.js
function add(a, b) {
return a + b;
}

module.exports = {
add,
PI: 3.14159,
};

// main.js
const math = require("./math");
console.log(math.add(1, 2)); // 3
```

---

## 逆向分析技巧

### 1. 查找加密函数

```javascript
// 常见的加密库关键词
// CryptoJS, crypto, encrypt, decrypt, MD5, SHA, AES, RSA

// 搜索技巧
// 在 DevTools 的 Sources 面板中全局搜索这些关键词
// Ctrl+Shift+F (Windows) 或 Cmd+Opt+F (Mac)
```

### 2. Hook 函数

```javascript
// Hook 原生方法
const originalFetch = window.fetch;
window.fetch = function (...args) {
console.log("Fetch called with:", args);
return originalFetch.apply(this, args);
};

// Hook 对象方法
const originalPush = Array.prototype.push;
Array.prototype.push = function (...items) {
console.log("Array push:", items);
return originalPush.apply(this, items);
};
```

### 3. 调试混淆代码

```javascript
// 使用 debugger 语句
function suspiciousFunction() {
debugger; // 执行到这里会自动断点
// ...
}

// 条件断点
// 在 DevTools 中右键设置条件断点
// 例如：userId === '12345'

// 日志点
// 不暂停执行，只输出日志
```

---

## 相关章节

- [DOM 与 BOM](./dom_and_bom.md)
- [浏览器开发者工具](../02-Tooling/browser_devtools.md)
- [JavaScript 反混淆](../04-Advanced-Recipes/javascript_deobfuscation.md)
- [调试技巧与断点设置](../03-Basic-Recipes/debugging_techniques.md)
