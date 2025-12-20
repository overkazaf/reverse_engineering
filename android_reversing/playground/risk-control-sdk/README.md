# 风控SDK - 基于设备指纹的风险控制系统

这是一个基于 JNI 实现的设备指纹风控SDK，用于移动应用的安全风险评估和欺诈检测。

## 功能特性

### 🔍 设备指纹采集
- **硬件指纹**: CPU信息、内存、存储、传感器
- **软件指纹**: 操作系统、运行时环境、安装的应用
- **网络指纹**: IP地址、网络类型、代理检测
- **行为指纹**: 用户交互模式、设备使用习惯

### 🛡️ 安全检测
- **模拟器检测**: 多种模拟器环境识别
- **Root/越狱检测**: 系统完整性验证
- **调试检测**: 反调试和动态分析检测
- **Hook检测**: Frida、Xposed等Hook框架检测

### 📊 风险评估
- **设备风险评分**: 综合评估设备安全等级
- **行为异常检测**: 识别可疑的用户行为
- **黑名单匹配**: 已知恶意设备识别
- **实时风险监控**: 持续监控设备状态变化

## 技术架构

```
┌─────────────────────────────────────────────┐
│                Java Layer                   │
├─────────────────────────────────────────────┤
│  RiskControlSDK  │  DeviceFingerprint      │
│  SecurityChecker │  BehaviorAnalyzer       │
└─────────────────────────────────────────────┘
                    │ JNI Interface
┌─────────────────────────────────────────────┐
│                Native Layer                 │
├─────────────────────────────────────────────┤
│  Fingerprint     │  Security              │
│  Collection      │  Detection             │
│                  │                        │
│  Anti-Debug      │  Behavior              │
│  Protection      │  Analysis              │
└─────────────────────────────────────────────┘
```

## 核心组件

### 1. 设备指纹采集器 (DeviceFingerprintCollector)
负责收集各种设备特征信息，生成唯一的设备标识。

### 2. 安全检测器 (SecurityDetector)
检测设备的安全状态，识别潜在的安全威胁。

### 3. 行为分析器 (BehaviorAnalyzer)
分析用户行为模式，检测异常操作。

### 4. 风险评估引擎 (RiskAssessmentEngine)
综合各种信息进行风险评分和决策。

## API 使用示例

```java
// 初始化SDK
RiskControlSDK sdk = RiskControlSDK.getInstance();
sdk.initialize(context);

// 获取设备指纹
DeviceFingerprint fingerprint = sdk.getDeviceFingerprint();
String deviceId = fingerprint.getDeviceId();

// 安全检测
SecurityResult security = sdk.performSecurityCheck();
boolean isRooted = security.isRooted();
boolean isEmulator = security.isEmulator();

// 风险评估
RiskScore score = sdk.assessRisk();
int riskLevel = score.getRiskLevel(); // 0-100
```

## 编译说明

### 依赖要求
- Android NDK r20+
- CMake 3.10+
- JDK 8+

### 构建步骤
```bash
cd risk-control-sdk
mkdir build && cd build
cmake ..
make
```

### Android Studio 集成
```gradle
android {
    externalNativeBuild {
        cmake {
            path "src/main/cpp/CMakeLists.txt"
            version "3.10.2"
        }
    }
}
```

## 安全特性

### 反逆向保护
- **代码混淆**: Native代码符号混淆
- **字符串加密**: 关键字符串运行时解密
- **控制流混淆**: 使用OLLVM等工具
- **反调试**: 多层反调试保护

### 完整性保护
- **签名验证**: APK签名完整性检查
- **CRC校验**: 关键代码段校验
- **运行时保护**: 内存完整性监控

## 应用场景

- 🏦 **金融风控**: 银行、支付应用的设备风险识别
- 🛒 **电商反欺诈**: 虚假账号、刷单行为检测
- 🎮 **游戏安全**: 外挂、模拟器检测
- 📱 **移动安全**: 企业应用的设备合规检查

## 许可证

本项目仅用于学习和研究目的。