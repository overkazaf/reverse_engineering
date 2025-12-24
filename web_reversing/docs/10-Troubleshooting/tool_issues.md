# 工具使用问题

常见开发和逆向工具的问题及解决方案。

---

## Chrome DevTools 问题

### 无法打开 DevTools

**问题**: 按 F12 或右键检查无反应

**解决方案**:

```javascript
// 1. 检查是否被禁用
// 某些网站会禁用右键菜单和快捷键

// 绕过方法 1: 在地址栏输入
//inspect

// 绕过方法 2: 从菜单打开
// Chrome → 更多工具 → 开发者工具

// 绕过方法 3: 使用快捷键组合
chrome: Ctrl + Shift + I(Windows / Linux);
Cmd + Option + I(Mac);
```

### DevTools 显示异常

**问题**: DevTools 界面混乱、卡顿或崩溃

**解决方案**:

```bash
# 1. 重置 DevTools 设置
# 打开 DevTools → Settings (F1) → Restore defaults

# 2. 清除 DevTools 缓存
# Settings → Preferences → Network → Disable cache (while DevTools is open)

# 3. 禁用扩展
# 在隐身模式打开 (Ctrl + Shift + N)

# 4. 完全重置 Chrome
# 删除用户数据目录
# Windows: %LOCALAPPDATA%\Google\Chrome\User Data
# Mac: ~/Library/Application Support/Google/Chrome
# Linux: ~/.config/google-chrome
```

### Network 面板无法抓包

**问题**: Network 标签页中看不到请求

**解决方案**:

1. **检查过滤器**

```javascript
// Network 面板中，确保:
// - 未勾选 "Hide data URLs"
// - Filter 输入框为空
// - All 类型已选中
```

2. **启用日志保留**

```javascript
// Network → 勾选 "Preserve log"
// 这样页面跳转后仍能看到之前的请求
```

3. **清除缓存**

```javascript
// 右键刷新按钮 → "Empty Cache and Hard Reload"
```

---

## Burp Suite 配置问题

### 代理配置不生效

**问题**: 设置代理后浏览器无法访问网站

**解决方案**:

#### 1. 检查代理设置

```bash
# Burp Suite 默认代理
127.0.0.1:8080

# 浏览器代理设置 (Chrome)
chrome://settings/system
# 或使用 SwitchyOmega 扩展
```

#### 2. 检查 Burp 监听器

```
Proxy → Options → Proxy Listeners
确保:
- Running: 勾选
- Interface: 127.0.0.1:8080
- Support invisible proxying: 勾选 (如需要)
```

#### 3. 防火墙设置

```bash
# Windows 防火墙可能阻止本地端口
# 添加入站规则允许 8080 端口

# Linux
sudo ufw allow 8080
```

### SSL 证书问题

**问题**: HTTPS 网站显示证书错误

**解决方案**:

#### 1. 导入 Burp CA 证书

```bash
# 1. 导出证书
# Proxy → Options → Import/Export CA certificate
# 导出为 DER 格式

# 2. 安装到系统
# Windows: 双击 .cer 文件 → 安装到"受信任的根证书颁发机构"
# Mac: 双击 → 添加到钥匙串 → 设置为"始终信任"
# Linux: sudo cp cacert.der /usr/local/share/ca-certificates/burp.crt
# sudo update-ca-certificates
```

#### 2. Firefox 特殊配置

```
Firefox 使用独立证书存储

1. 打开 Firefox → Settings → Privacy & Security
2. Certificates → View Certificates → Import
3. 导入 Burp CA 证书
4. 勾选 "Trust this CA to identify websites"
```

### Burp 拦截太多请求

**问题**: Proxy intercept 拦截了过多无关请求

**解决方案**:

```
# 配置拦截规则
Proxy → Options → Intercept Client Requests

# 添加规则,只拦截目标域名
And URL Is in target scope

# 或添加白名单
And URL matches: ^https://target\.com/.*
```

---

## Fiddler 问题

### 无法捕获 HTTPS 流量

**解决方案**:

```
1. Tools → Options → HTTPS
2. 勾选 "Capture HTTPS CONNECTs"
3. 勾选 "Decrypt HTTPS traffic"
4. 点击 "Actions" → "Trust Root Certificate"
5. 重启 Fiddler
```

### 代理冲突

**问题**: 与其他代理工具冲突

**解决方案**:

```bash
# 1. 检查系统代理
netsh winhttp show proxy # Windows

# 2. 重置系统代理
netsh winhttp reset proxy

# 3. 关闭其他代理工具
# 如 Charles, Burp, Proxifier 等
```

---

## Python 环境问题

### ModuleNotFoundError

**问题**: `ModuleNotFoundError: No module named 'xxx'`

**解决方案**:

```bash
# 1. 检查是否安装
pip list | grep xxx

# 2. 安装模块
pip install xxx

# 3. 检查 Python 版本
python --version
pip --version

# 4. 如果有多个 Python 版本
python3 -m pip install xxx

# 5. 使用虚拟环境
python -m venv venv
source venv/bin/activate # Linux/Mac
venv\Scripts\activate # Windows
pip install -r requirements.txt
```

### SSL 证书验证失败

**问题**: `SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]`

**解决方案**:

```python
# 方法 1: 升级 certifi
pip install --upgrade certifi

# 方法 2: 在代码中禁用验证 (不推荐用于生产环境)
import requests
requests.get(url, verify=False)

# 方法 3: 指定证书路径
import certifi
requests.get(url, verify=certifi.where())

# 方法 4: 设置环境变量
import os
os.environ['REQUESTS_CA_BUNDLE'] = '/path/to/ca-bundle.crt'
```

### 编码问题

**问题**: `UnicodeDecodeError` 或 `UnicodeEncodeError`

**解决方案**:

```python
# 读取文件时指定编码
with open('file.txt', 'r', encoding='utf-8') as f:
content = f.read()

# 写入文件时指定编码
with open('file.txt', 'w', encoding='utf-8') as f:
f.write(content)

# 处理网络响应
response.encoding = 'utf-8'
text = response.text

# 或使用 chardet 自动检测
import chardet
encoding = chardet.detect(response.content)['encoding']
text = response.content.decode(encoding)
```

---

## Node.js 问题

### npm 安装失败

**问题**: `npm ERR! code EACCES` 或下载超时

**解决方案**:

```bash
# 1. 权限问题 (Linux/Mac)
sudo chown -R $USER ~/.npm
sudo chown -R $USER /usr/local/lib/node_modules

# 2. 使用淘宝镜像
npm config set registry https://registry.npmmirror.com

# 3. 清除缓存
npm cache clean --force

# 4. 删除 node_modules 重新安装
rm -rf node_modules package-lock.json
npm install

# 5. 使用 cnpm
npm install -g cnpm --registry=https://registry.npmmirror.com
cnpm install
```

### Node 版本问题

**问题**: 项目需要特定 Node 版本

**解决方案**:

```bash
# 使用 nvm 管理多版本
# 安装 nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# 安装特定版本
nvm install 18.17.0
nvm use 18.17.0

# 设置默认版本
nvm alias default 18.17.0

# 或使用 n
npm install -g n
n 18.17.0
```

---

## Postman 问题

### 脚本执行错误

**问题**: Pre-request Script 或 Tests 脚本报错

**解决方案**:

```javascript
// 1. 检查语法
// Postman 使用受限的 JavaScript 环境

// 2. 常用功能示例

// 设置环境变量
pm.environment.set("token", jsonData.token);

// 发送请求
pm.sendRequest("https://api.example.com/data", (err, res) => {
if (err) {
console.log(err);
} else {
console.log(res.json());
}
});

// 使用 CryptoJS
const encrypted = CryptoJS.MD5("message").toString();

// 使用 moment.js
const now = moment().format();
```

### 请求失败

**问题**: 请求返回错误

**解决方案**:

```javascript
// 1. 检查代理设置
Settings → Proxy → 关闭 "Use the system proxy"

// 2. 禁用 SSL 验证 (仅测试环境)
Settings → General → 关闭 "SSL certificate verification"

// 3. 添加详细日志
console.log("Request:", pm.request);
console.log("Response:", pm.response);
```

---

## VS Code 问题

### Python IntelliSense 不工作

**解决方案**:

```json
// settings.json
{
"python.defaultInterpreterPath": "/path/to/python",
"python.analysis.typeCheckingMode": "basic",
"python.analysis.autoImportCompletions": true
}
```

### 调试配置

**launch.json 示例**:

```json
{
"version": "0.2.0",
"configurations": [
{
"name": "Python: Current File",
"type": "python",
"request": "launch",
"program": "${file}",
"console": "integratedTerminal",
"env": {
"PYTHONPATH": "${workspaceFolder}"
}
},
{
"name": "Node: Current File",
"type": "node",
"request": "launch",
"program": "${file}",
"skipFiles": ["<node_internals>/**"]
}
]
}
```

---

## Git 问题

### 推送失败

**问题**: `! [rejected] ... (fetch first)`

**解决方案**:

```bash
# 1. 先拉取远程更改
git pull origin main

# 2. 如果有冲突，解决后提交
git add .
git commit -m "Merge conflicts"

# 3. 推送
git push origin main

# 强制推送 (谨慎使用)
git push -f origin main
```

### 大文件问题

**问题**: 文件过大无法提交

**解决方案**:

```bash
# 1. 使用 Git LFS
git lfs install
git lfs track "*.psd"
git add .gitattributes

# 2. 从历史中移除大文件
git filter-branch --tree-filter 'rm -f large_file.zip' HEAD

# 3. 使用 .gitignore
echo "*.log" >> .gitignore
echo "data/" >> .gitignore
```

---

## Wireshark 问题

### 无法捕获 HTTPS 内容

**问题**: 抓包只能看到加密流量

**解决方案**:

```bash
# 1. 配置 SSL/TLS 密钥日志文件

# 设置环境变量 (Chrome/Firefox)
export SSLKEYLOGFILE=~/sslkeys.log # Linux/Mac
set SSLKEYLOGFILE=C:\sslkeys.log # Windows

# 2. 在 Wireshark 中配置
# Edit → Preferences → Protocols → TLS
# (Pre)-Master-Secret log filename: 选择上面的文件

# 3. 重启浏览器后抓包,就能看到解密内容
```

### 过滤规则

**常用过滤器**:

```
# HTTP 请求
http.request

# 特定域名
http.host contains "example.com"

# 特定 IP
ip.addr == 192.168.1.1

# 端口
tcp.port == 443

# 包含特定字符串
frame contains "password"
```

---

## 抓包工具配置

### 系统代理设置

#### Windows

```bash
# 设置代理
netsh winhttp set proxy 127.0.0.1:8080

# 查看代理
netsh winhttp show proxy

# 取消代理
netsh winhttp reset proxy
```

#### macOS

```bash
# 通过 networksetup
sudo networksetup -setwebproxy "Wi-Fi" 127.0.0.1 8080
sudo networksetup -setsecurewebproxy "Wi-Fi" 127.0.0.1 8080

# 关闭代理
sudo networksetup -setwebproxystate "Wi-Fi" off
sudo networksetup -setsecurewebproxystate "Wi-Fi" off
```

#### Linux

```bash
# 设置环境变量
export http_proxy="http://127.0.0.1:8080"
export https_proxy="http://127.0.0.1:8080"

# 永久设置 (添加到 ~/.bashrc)
echo 'export http_proxy="http://127.0.0.1:8080"' >> ~/.bashrc
echo 'export https_proxy="http://127.0.0.1:8080"' >> ~/.bashrc
```

---

## 相关章节

- [Burp Suite 指南](../02-Tooling/burp_suite_guide.md)
- [Chrome DevTools](../02-Tooling/browser_devtools.md)
- [Node.js 调试](../02-Tooling/nodejs_debugging.md)
- [常用命令](../08-Cheat-Sheets/common_commands.md)
