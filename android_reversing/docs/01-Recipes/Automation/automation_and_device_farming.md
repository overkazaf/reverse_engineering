# 工程化：自动化与群控系统

在虚拟化和容器化解决了"环境"问题之后，自动化和群控系统则负责解决"执行"和"管理"的问题。它们是驱动整个规模化测试和分析流水线运转的核心引擎。

---

## 1. 自动化框架

自动化框架是模拟用户行为、与 App UI 进行交互的工具集。它的核心任务是代替人工，实现对 App 的程序化控制。

### a) 主流框架对比

| 框架                      | 驱动原理                                | 优点                                                                 | 缺点                                                                                | 适用场景                                      |
| ------------------------- | --------------------------------------- | -------------------------------------------------------------------- | ----------------------------------------------------------------------------------- | --------------------------------------------- |
| **Appium**                | WebDriver 协议 -> UIAutomator2/XCUITest | 跨平台（Android/iOS），多语言支持，生态成熟，功能强大。              | 环境配置复杂，执行速度相对较慢，对 App 有一定的侵入性（需要安装 WebDriver Agent）。 | 标准化的、跨平台的端到端（E2E）功能测试。     |
| **UIAutomator2 (Python)** | Google UIAutomator2                     | 直接与设备通信，速度快，稳定，API 简洁易用。                         | 仅支持 Android，功能相对 Appium 较少。                                              | 纯 Android 平台的快速自动化、爬虫和日常脚本。 |
| **Airtest / Poco**        | 图像识别 + UI 控件                      | 能够解决无法获取 UI 控件树的问题（如游戏），跨引擎（Unity, Cocos）。 | 图像识别不稳定，受分辨率和 UI 变化影响大，速度慢。                                  | 游戏自动化，黑盒测试。                        |

### b) 脚本编写的最佳实践

**分离 UI 元素与业务逻辑 (Page Object Model)**: 不要将 UI 元素的定位符（如 `resource-id`）硬编码在业务代码中。应该为每个页面创建一个类（Page Object），封装该页面的所有元素和操作。当 UI 变化时，你只需要修改对应的 Page Object，而无需改动业务流程代码。

**明确的断言**: 每个测试用例都应该有明确的成功或失败的判断标准（断言）。例如，点击登录后，断言"用户名"元素是否出现在下一个页面。

**异常处理与重试**: 网络延迟、系统弹窗等都可能导致自动化失败。在关键步骤加入合理的等待、异常捕获和重试机制，可以大大提高脚本的稳定性。

**日志与报告**: 在脚本的关键节点输出有意义的日志。测试结束后，生成图文并茂的测试报告（如 Allure Report），方便快速定位问题。

---

### c) Poco 自动化技术深度解析

Poco 是网易推出的 UI 自动化测试框架，专为游戏和复杂应用设计，是 Airtest 项目的核心组件之一。

#### 核心架构与原理

```text
┌─────────────────────────────────────────────────────────┐
│                      控制端 (PC)                         │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ Poco Client │──│  RPC 通信    │──│  测试脚本    │    │
│  └─────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────┘
                          │
                    WebSocket/Socket
                          │
┌─────────────────────────────────────────────────────────┐
│                   设备端 (手机/模拟器)                   │
│  ┌──────────────────────────────────────────────────┐   │
│  │              Poco SDK (嵌入游戏/应用)              │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────┐    │   │
│  │  │ RPC 服务 │  │ UI树抓取 │  │  指令执行器  │    │   │
│  │  └──────────┘  └──────────┘  └──────────────┘    │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

**工作流程**:

1. **SDK 嵌入**: 游戏/应用集成 Poco SDK，启动 RPC 服务
2. **建立连接**: 控制端通过 WebSocket 与 SDK 通信
3. **UI 树获取**: SDK 遍历游戏引擎的 UI 控件，生成控件树
4. **指令执行**: 接收控制端指令，操作对应 UI 控件
5. **结果回传**: 将操作结果和状态信息返回控制端

#### SDK 集成方式

**Unity 引擎集成**:

```csharp
// Unity 项目中集成 Poco SDK
using Poco;

public class PocoManager : MonoBehaviour {
    void Start() {
        // 启动 Poco 服务
        var poco = new PocoServiceBuilder()
            .SetPort(5001)
            .SetDebugMode(true)
            .Build();

        poco.Start();
    }
}
```

**Cocos2d-x 集成**:

```cpp
// Cocos2d-x 项目集成
bool AppDelegate::applicationDidFinishLaunching() {
    // 初始化 Poco 服务
    poco::PocoManager::getInstance()->start();

    return true;
}
```

**Android 原生集成**:

```java
public class MainActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // 启动 Poco 服务
        Poco.start("poco", 5001);
    }
}
```

#### Python 控制端使用

**基础连接与操作**:

```python
from poco.drivers.unity3d import UnityPoco
from poco.drivers.android.uiautomation import AndroidUiautomationPoco

# Unity 游戏连接
poco = UnityPoco(('192.168.1.100', 5001))

# Android 原生应用连接
poco = AndroidUiautomationPoco(
    use_airtest_input=True,
    screenshot_each_action=False
)

# 基本操作
poco('Button').click()                  # 点击按钮
poco('InputField').set_text('test')     # 输入文本
poco('ScrollView').swipe('up')          # 滑动操作

# 等待元素出现
poco('LoadingPanel').wait_for_disappearance()  # 等待加载完成
```

**高级选择器**:

```python
# 属性选择
poco(text='确定').click()
poco(name='startBtn', enabled=True).click()
poco(type='Button', visible=True).click()

# 相对位置选择
poco('username').sibling('password')  # 兄弟节点
poco('title').parent()                 # 父节点

# 条件过滤
buttons = poco('Button').filter(
    lambda x: x.get_text().startswith('确定')
)
```

**游戏专用操作**:

```python
# 拖拽操作
poco.drag_to([0.2, 0.2], [0.8, 0.8])

# 多点触控
poco.pinch(in_or_out='in', center=[0.5, 0.5], percent=0.6)

# 等待游戏状态
def wait_for_battle_end():
    return poco('BattleResult').exists()

poco.wait_for_all(wait_for_battle_end, timeout=60)
```

#### 跨引擎适配

```python
def get_poco_instance(engine_type, device_info):
    """根据引擎类型创建对应的 Poco 实例"""
    if engine_type == 'unity':
        return UnityPoco(device_info['addr'])
    elif engine_type == 'cocos':
        return CocosJSPoco(device_info['addr'])
    elif engine_type == 'unreal':
        return UE4Poco(device_info['addr'])
    elif engine_type == 'android':
        return AndroidUiautomationPoco()
    else:
        raise ValueError(f"Unsupported engine: {engine_type}")
```

#### 连接池管理

```python
import queue

class PocoConnectionPool:
    def __init__(self, max_connections=10):
        self.pool = queue.Queue(max_connections)
        self.max_connections = max_connections

    def get_connection(self, addr):
        try:
            return self.pool.get_nowait()
        except queue.Empty:
            return UnityPoco(addr)

    def return_connection(self, conn):
        try:
            self.pool.put_nowait(conn)
        except queue.Full:
            pass  # 丢弃多余连接
```

#### 批量操作优化

```python
def batch_get_elements(poco, selectors):
    """批量获取多个元素，减少 RPC 调用"""
    elements = {}
    for name, selector in selectors.items():
        try:
            elements[name] = poco(selector)
        except:
            elements[name] = None
    return elements

# 使用示例
ui_elements = batch_get_elements(poco, {
    'start_btn': 'StartButton',
    'settings_btn': 'SettingsButton',
    'exit_btn': 'ExitButton'
})
```

#### 稳定性增强

```python
from functools import wraps
import time

def retry_on_failure(max_retries=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    print(f"Attempt {attempt + 1} failed: {e}")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

@retry_on_failure(max_retries=3, delay=2)
def stable_click(poco, selector):
    """稳定的点击操作，带重试机制"""
    element = poco(selector)
    if element.exists():
        element.click()
        return True
    else:
        raise Exception(f"Element {selector} not found")
```

#### 日志与调试

```python
import logging
import time
from poco.utils.logger import setup_logger

# 设置 Poco 日志
setup_logger(level=logging.DEBUG)

# 自定义操作日志
class PocoLogger:
    @staticmethod
    def log_action(action, element, result=None):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {action} on {element}, result: {result}")

    @staticmethod
    def log_screenshot(path):
        print(f"Screenshot saved: {path}")

# 使用示例
def logged_click(poco, selector):
    try:
        poco(selector).click()
        PocoLogger.log_action("CLICK", selector, "SUCCESS")
    except Exception as e:
        PocoLogger.log_action("CLICK", selector, f"FAILED: {e}")
        # 保存错误时的截图
        screenshot_path = f"error_{int(time.time())}.png"
        poco.snapshot(screenshot_path)
        PocoLogger.log_screenshot(screenshot_path)
        raise
```

#### 群控集成示例

```python
class DevicePocoController:
    def __init__(self, device_id, poco_port=5001):
        self.device_id = device_id
        self.poco_port = poco_port
        self.poco = None

    def connect(self):
        """连接到设备上的 Poco 服务"""
        device_ip = self.get_device_ip(self.device_id)
        self.poco = UnityPoco((device_ip, self.poco_port))
        return self.poco is not None

    def execute_task(self, task_config):
        """执行自动化任务"""
        try:
            actions = task_config['actions']
            for action in actions:
                self.execute_action(action)
            return {"status": "success", "device_id": self.device_id}
        except Exception as e:
            return {"status": "failed", "error": str(e), "device_id": self.device_id}

    def execute_action(self, action):
        """执行单个操作"""
        action_type = action['type']

        if action_type == 'click':
            self.poco(action['selector']).click()
        elif action_type == 'input':
            self.poco(action['selector']).set_text(action['text'])
        elif action_type == 'wait':
            time.sleep(action['duration'])
        # ... 其他操作类型
```

#### 性能优化建议

1. **连接复用**: 使用连接池管理 Poco 连接，避免频繁建立连接
2. **批量操作**: 合并多个 UI 操作，减少 RPC 调用次数
3. **缓存控件**: 对于频繁访问的 UI 控件，缓存其引用
4. **异步操作**: 对于耗时操作使用异步模式提高效率
5. **错误处理**: 完善的异常捕获和恢复机制
6. **性能监控**: 监控 RPC 调用延迟和成功率

#### 与其他自动化框架对比

| 特性           | Poco               | Appium       | UIAutomator2       |
| :------------- | :----------------- | :----------- | :----------------- |
| **游戏支持**   | 优秀               | 不支持       | 不支持             |
| **跨引擎**     | Unity/Cocos/UE4    | 仅原生       | 仅 Android 原生    |
| **集成复杂度** | 中等(需 SDK)       | 低(无需修改) | 低(无需修改)       |
| **执行速度**   | 快                 | 中等         | 快                 |
| **稳定性**     | 高                 | 中等         | 高                 |
| **学习成本**   | 中等               | 高           | 低                 |

Poco 特别适合游戏自动化测试、游戏 AI 训练、游戏内容验证等场景，是移动游戏自动化的首选方案。

---

## 2. 群控系统 (Device Farming)

群控系统是一个将大量物理设备或虚拟设备（模拟器）汇集成一个统一的、可编程的资源池，并对其进行集中化管理、调度和监控的平台。

### a) 核心架构

一个工业级的群控系统通常是微服务架构，包含以下核心组件：

1. **API 网关 (API Gateway)**:
   - 作为所有服务的统一入口，负责请求路由、身份认证和速率限制。

2. **设备管理服务 (Device Management Service)**:
   - 维护一个包含所有设备（真机/模拟器）信息的数据库。
   - 通过心跳机制实时监控每个设备的状态（空闲、占用、离线、健康状况）。
   - 处理设备的接入和注销。

3. **任务调度服务 (Task Scheduling Service)**:
   - 接收用户提交的任务（例如，"在 Android 12 上对 App X 执行 Y 测试"）。
   - 根据任务要求（设备类型、系统版本等）和预设的调度策略（如优先级、FIFO）从设备管理服务中查询并锁定一个合适的设备。

4. **执行代理 (Agent)**:
   - 在每个物理设备或模拟器上运行的一个轻量级代理程序。
   - 负责接收并执行来自调度中心的具体指令，如：安装/卸载 APK、启动/停止 Appium、执行 shell 命令、上传/下载文件等。

5. **结果收集与报告服务**:
   - 接收来自 Agent 的实时日志、截图、录屏和测试结果。
   - 将结果存入数据库，并在任务结束后生成最终的测试报告。

6. **Web 管理前端**:
   - 提供一个可视化的界面，让用户可以实时查看设备列表、远程控制设备（如 STF）、提交任务、查看任务队列和历史报告。

### b) 开源方案与自研

**STF (Smartphone Test Farm)**: 提供了优秀的设备管理和远程控制功能，是许多自研群控系统的基础。但它本身不包含任务调度和报告等功能。

**自研**: 许多大型公司会基于 STF、Appium、Docker、Kubernetes 等开源技术栈，结合自身的业务需求，搭建自研的群控平台，以实现更灵活的调度逻辑和更深入的业务集成。

---

## 总结

自动化与群控系统是移动端工程化能力的集中体现。它将底层的设备资源、中层的执行脚本和上层的业务需求有机地结合在一起，形成了一个强大的、可扩展的自动化解决方案，是现代 App 开发、测试和安全分析不可或缺的一环。
