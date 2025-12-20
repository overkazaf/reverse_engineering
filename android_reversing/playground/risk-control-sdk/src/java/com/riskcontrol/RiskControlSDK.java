package com.riskcontrol;

import java.util.HashMap;
import java.util.Map;

/**
 * 风控SDK主类
 * 提供设备指纹采集、安全检测、风险评估等核心功能
 */
public class RiskControlSDK {
    private static RiskControlSDK instance;
    private boolean initialized = false;
    
    // 加载本地库
    static {
        try {
            System.loadLibrary("riskcontrol");
            System.out.println("[RiskSDK] Native library loaded successfully");
        } catch (UnsatisfiedLinkError e) {
            System.err.println("[RiskSDK] Failed to load native library: " + e.getMessage());
            throw new RuntimeException("Failed to initialize RiskControl SDK", e);
        }
    }
    
    private RiskControlSDK() {}
    
    /**
     * 获取SDK单例实例
     */
    public static synchronized RiskControlSDK getInstance() {
        if (instance == null) {
            instance = new RiskControlSDK();
        }
        return instance;
    }
    
    /**
     * 初始化SDK
     * @param context Android应用上下文
     * @return 初始化是否成功
     */
    public boolean initialize(Object context) {
        if (initialized) {
            return true;
        }
        
        try {
            boolean result = nativeInitialize();
            if (result) {
                initialized = true;
                System.out.println("[RiskSDK] SDK initialized successfully");
            } else {
                System.err.println("[RiskSDK] SDK initialization failed");
            }
            return result;
        } catch (Exception e) {
            System.err.println("[RiskSDK] Exception during initialization: " + e.getMessage());
            return false;
        }
    }
    
    /**
     * 获取设备指纹
     * @return 设备指纹对象
     */
    public DeviceFingerprint getDeviceFingerprint() {
        checkInitialized();
        
        Map<String, String> fingerprintData = new HashMap<>();
        
        // 调用native方法收集指纹数据
        String deviceId = nativeGetDeviceId();
        String hardwareInfo = nativeGetHardwareInfo();
        String softwareInfo = nativeGetSoftwareInfo();
        String networkInfo = nativeGetNetworkInfo();
        
        fingerprintData.put("deviceId", deviceId);
        fingerprintData.put("hardware", hardwareInfo);
        fingerprintData.put("software", softwareInfo);
        fingerprintData.put("network", networkInfo);
        
        return new DeviceFingerprint(fingerprintData);
    }
    
    /**
     * 执行安全检测
     * @return 安全检测结果
     */
    public SecurityResult performSecurityCheck() {
        checkInitialized();
        
        SecurityResult result = new SecurityResult();
        
        // 模拟器检测
        result.setEmulator(nativeDetectEmulator());
        
        // Root检测
        result.setRooted(nativeDetectRoot());
        
        // 调试检测
        result.setDebugging(nativeDetectDebug());
        
        // Hook检测
        result.setHooked(nativeDetectHook());
        
        // 代理检测
        result.setProxy(nativeDetectProxy());
        
        // VPN检测
        result.setVpn(nativeDetectVPN());
        
        return result;
    }
    
    /**
     * 评估设备风险
     * @return 风险评分结果
     */
    public RiskScore assessRisk() {
        checkInitialized();
        
        // 获取设备指纹和安全状态
        DeviceFingerprint fingerprint = getDeviceFingerprint();
        SecurityResult security = performSecurityCheck();
        
        // 调用native方法计算风险分数
        int riskScore = nativeCalculateRiskScore(
            fingerprint.getDeviceId(),
            security.isEmulator(),
            security.isRooted(),
            security.isDebugging(),
            security.isHooked()
        );
        
        // 获取风险详情
        String riskDetails = nativeGetRiskDetails();
        
        return new RiskScore(riskScore, riskDetails);
    }
    
    /**
     * 获取SDK版本信息
     * @return 版本字符串
     */
    public String getVersion() {
        return nativeGetVersion();
    }
    
    /**
     * 启用/禁用调试模式
     * @param enabled 是否启用调试
     */
    public void setDebugMode(boolean enabled) {
        nativeSetDebugMode(enabled);
    }
    
    /**
     * 设置自定义配置
     * @param config 配置映射
     */
    public void setConfiguration(Map<String, String> config) {
        checkInitialized();
        
        for (Map.Entry<String, String> entry : config.entrySet()) {
            nativeSetConfig(entry.getKey(), entry.getValue());
        }
    }
    
    /**
     * 清理SDK资源
     */
    public void cleanup() {
        if (initialized) {
            nativeCleanup();
            initialized = false;
            System.out.println("[RiskSDK] SDK cleaned up");
        }
    }
    
    private void checkInitialized() {
        if (!initialized) {
            throw new IllegalStateException("RiskControl SDK not initialized. Call initialize() first.");
        }
    }
    
    // ========== Native方法声明 ==========
    
    private native boolean nativeInitialize();
    
    // 设备指纹相关
    private native String nativeGetDeviceId();
    private native String nativeGetHardwareInfo();
    private native String nativeGetSoftwareInfo();
    private native String nativeGetNetworkInfo();
    
    // 安全检测相关
    private native boolean nativeDetectEmulator();
    private native boolean nativeDetectRoot();
    private native boolean nativeDetectDebug();
    private native boolean nativeDetectHook();
    private native boolean nativeDetectProxy();
    private native boolean nativeDetectVPN();
    
    // 风险评估相关
    private native int nativeCalculateRiskScore(String deviceId, boolean isEmulator, 
                                               boolean isRooted, boolean isDebugging, boolean isHooked);
    private native String nativeGetRiskDetails();
    
    // 配置和工具方法
    private native String nativeGetVersion();
    private native void nativeSetDebugMode(boolean enabled);
    private native void nativeSetConfig(String key, String value);
    private native void nativeCleanup();
}