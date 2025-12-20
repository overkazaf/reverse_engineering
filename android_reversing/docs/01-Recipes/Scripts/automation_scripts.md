# 自动化脚本 (Automation Scripts)

在 Android 逆向工程中，自动化脚本可以极大地提高效率，例如自动安装 APK、重启应用、模拟点击以及批量处理设备。Python 是编写这些脚本的首选语言。

---

## 1. 基础 ADB 封装 (Python)

虽然可以直接在 shell 中运行 `adb` 命令，但在 Python 中封装一层可以更方便地进行逻辑控制。

```python
import subprocess
import time
import os

class AdbWrapper:
    def __init__(self, device_id=None):
        self.device_id = device_id

    def run_cmd(self, cmd):
        adb_cmd = ["adb"]
        if self.device_id:
            adb_cmd.extend(["-s", self.device_id])
        adb_cmd.extend(cmd)

        try:
            result = subprocess.run(
                adb_cmd,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Error running command {' '.join(adb_cmd)}: {e.stderr}")
            return None

    def install(self, apk_path):
        print(f"Installing {apk_path}...")
        return self.run_cmd(["install", "-r", apk_path])

    def uninstall(self, package_name):
        print(f"Uninstalling {package_name}...")
        return self.run_cmd(["uninstall", package_name])

    def start_app(self, package_name, activity_name):
        print(f"Starting {package_name}/{activity_name}...")
        return self.run_cmd(["shell", "am", "start", "-n", f"{package_name}/{activity_name}"])

    def stop_app(self, package_name):
        print(f"Stopping {package_name}...")
        return self.run_cmd(["shell", "am", "force-stop", package_name])

    def clear_data(self, package_name):
        print(f"Clearing data for {package_name}...")
        return self.run_cmd(["shell", "pm", "clear", package_name])

    def click(self, x, y):
        return self.run_cmd(["shell", "input", "tap", str(x), str(y)])

    def swipe(self, x1, y1, x2, y2, duration=500):
        return self.run_cmd(["shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration)])

    def input_text(self, text):
        # Note: special characters might need escaping
        return self.run_cmd(["shell", "input", "text", text])

    def screenshot(self, remote_path="/sdcard/screenshot.png", local_path="screenshot.png"):
        self.run_cmd(["shell", "screencap", "-p", remote_path])
        self.run_cmd(["pull", remote_path, local_path])
        print(f"Screenshot saved to {local_path}")

# 使用示例
if __name__ == "__main__":
    adb = AdbWrapper()  # 默认连接第一个设备

    # 打印连接的设备
    print("Devices:", adb.run_cmd(["devices"]))

    # adb.start_app("com.example.app", "com.example.app.MainActivity")
    # time.sleep(5)
    # adb.click(500, 1000)
    # adb.screenshot()
```

---

## 2. UIAutomator2 自动化

`uiautomator2` 是一个更强大的 UI 自动化库，可以更方便地进行元素定位和操作。

### 安装

```bash
pip install uiautomator2
```

### 使用示例

```python
import uiautomator2 as u2
import time

# 连接设备 (USB)
d = u2.connect()
# 或通过 WiFi: d = u2.connect('192.168.1.100')

print(f"Connected to device: {d.info}")

# 启动 App
pkg_name = "com.example.android.apis"
d.app_start(pkg_name)

# 等待 App 启动
d.wait_activity(".ApiDemos", timeout=10)

# 查找并点击元素 (支持多种选择器)
try:
    # 通过文本查找并点击
    if d(text="App").exists:
        d(text="App").click()

    # 通过 resourceId 查找
    # d(resourceId="com.example:id/button").click()

    # 滚动查找 (向下滑动直到找到文本为 'Notification' 元素)
    d(scrollable=True).scroll.to(text="Notification")
    d(text="Notification").click()

    # 输入文本
    # d(resourceId="com.example:id/edit_text").set_text("Hello World")

    # 截图
    d.screenshot("uiauto_screenshot.jpg")

except Exception as e:
    print(f"Error: {e}")

finally:
    # 停止 App
    # d.app_stop(pkg_name)
    pass
```

---

## 3. 批量管理工具

用于批量安装 APK、设置代理等操作。

```python
import os
import glob
from concurrent.futures import ThreadPoolExecutor

class BatchManager:
    def __init__(self, adb_wrapper):
        self.adb = adb_wrapper

    def install_all(self, directory):
        """批量安装目录下所有 APK"""
        apk_files = glob.glob(os.path.join(directory, "*.apk"))
        print(f"Found {len(apk_files)} APKs.")

        # 使用线程池并发安装 (注意：ADB 并发可能不稳定，视情况调整)
        with ThreadPoolExecutor(max_workers=3) as executor:
            executor.map(self.adb.install, apk_files)

    def setup_proxy(self, host, port):
        """设置全局 HTTP 代理"""
        print(f"Setting global http proxy to {host}:{port}...")
        self.adb.run_cmd(["shell", "settings", "put", "global", "http_proxy", f"{host}:{port}"])

    def clear_proxy(self):
        """清除全局 HTTP 代理"""
        print("Clearing global http proxy...")
        self.adb.run_cmd(["shell", "settings", "put", "global", "http_proxy", ":0"])

    def get_device_info(self):
        """获取设备信息"""
        info = {}
        info['brand'] = self.adb.run_cmd(["shell", "getprop", "ro.product.brand"])
        info['model'] = self.adb.run_cmd(["shell", "getprop", "ro.product.model"])
        info['sdk'] = self.adb.run_cmd(["shell", "getprop", "ro.build.version.sdk"])
        info['android'] = self.adb.run_cmd(["shell", "getprop", "ro.build.version.release"])
        return info

# 使用示例
if __name__ == "__main__":
    adb = AdbWrapper()
    manager = BatchManager(adb)

    # 批量安装当前目录下 apks 文件夹中所有 apk
    # manager.install_all("./apks")

    # 设置代理以便抓包
    # manager.setup_proxy("192.168.1.10", "8080")

    # 获取设备信息
    # info = manager.get_device_info()
    # print(info)
```

---

## 4. Frida 自动化脚本

结合 Frida 进行自动化 Hook。

```python
import frida
import sys
import time

def on_message(message, data):
    if message['type'] == 'send':
        print(f"[*] {message['payload']}")
    elif message['type'] == 'error':
        print(f"[!] {message['stack']}")

def run_frida_script(package_name, script_path):
    """运行 Frida 脚本"""
    try:
        # 连接设备
        device = frida.get_usb_device(timeout=5)
        print(f"[+] Connected to: {device}")

        # 启动或附加到应用
        try:
            pid = device.spawn([package_name])
            session = device.attach(pid)
            spawned = True
        except:
            session = device.attach(package_name)
            spawned = False

        # 加载脚本
        with open(script_path, 'r') as f:
            script_code = f.read()

        script = session.create_script(script_code)
        script.on('message', on_message)
        script.load()

        # 如果是 spawn 模式，恢复应用
        if spawned:
            device.resume(pid)

        print(f"[+] Script loaded, press Ctrl+C to exit")
        sys.stdin.read()

    except KeyboardInterrupt:
        print("\n[*] Exiting...")
    except Exception as e:
        print(f"[-] Error: {e}")

if __name__ == "__main__":
    run_frida_script("com.example.app", "hook_script.js")
```

---

## 5. 多设备管理

管理多台设备进行并行测试。

```python
import subprocess
from concurrent.futures import ThreadPoolExecutor

def get_connected_devices():
    """获取所有已连接设备"""
    result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
    lines = result.stdout.strip().split('\n')[1:]  # 跳过标题行
    devices = []
    for line in lines:
        if '\t' in line:
            device_id, status = line.split('\t')
            if status == 'device':
                devices.append(device_id)
    return devices

def run_on_device(device_id, task_func, *args):
    """在指定设备上运行任务"""
    adb = AdbWrapper(device_id)
    return task_func(adb, *args)

def run_on_all_devices(task_func, *args):
    """在所有设备上并行运行任务"""
    devices = get_connected_devices()
    print(f"[+] Found {len(devices)} devices")

    with ThreadPoolExecutor(max_workers=len(devices)) as executor:
        futures = [
            executor.submit(run_on_device, device_id, task_func, *args)
            for device_id in devices
        ]
        results = [f.result() for f in futures]
    return results

# 示例任务
def install_apk_task(adb, apk_path):
    return adb.install(apk_path)

def screenshot_task(adb, output_dir):
    device_id = adb.device_id or "default"
    local_path = f"{output_dir}/{device_id}_screenshot.png"
    adb.screenshot(local_path=local_path)
    return local_path

# 使用示例
if __name__ == "__main__":
    devices = get_connected_devices()
    print(f"Connected devices: {devices}")

    # 在所有设备上安装 APK
    # run_on_all_devices(install_apk_task, "./app.apk")

    # 在所有设备上截图
    # run_on_all_devices(screenshot_task, "./screenshots")
```

---

## 总结

自动化脚本是 Android 逆向工程的重要工具。通过 Python 封装 ADB 命令、使用 UIAutomator2 进行 UI 自动化、结合 Frida 进行动态分析，可以构建强大的自动化测试和分析流程。
