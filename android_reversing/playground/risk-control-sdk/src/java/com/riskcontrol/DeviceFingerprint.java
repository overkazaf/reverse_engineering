package com.riskcontrol;

import java.util.Map;
import java.util.HashMap;
import java.security.MessageDigest;

/**
 * 设备指纹类
 * 包含设备的各种特征信息用于唯一标识设备
 */
public class DeviceFingerprint {
    private Map<String, String> fingerprintData;
    private String deviceId;
    private long timestamp;
    
    public DeviceFingerprint(Map<String, String> data) {
        this.fingerprintData = new HashMap<>(data);
        this.deviceId = data.get("deviceId");
        this.timestamp = System.currentTimeMillis();
    }
    
    /**
     * 获取设备唯一标识
     * @return 设备ID
     */
    public String getDeviceId() {
        return deviceId;
    }
    
    /**
     * 获取硬件信息
     * @return 硬件信息JSON字符串
     */
    public String getHardwareInfo() {
        return fingerprintData.get("hardware");
    }
    
    /**
     * 获取软件信息
     * @return 软件信息JSON字符串
     */
    public String getSoftwareInfo() {
        return fingerprintData.get("software");
    }
    
    /**
     * 获取网络信息
     * @return 网络信息JSON字符串
     */
    public String getNetworkInfo() {
        return fingerprintData.get("network");
    }
    
    /**
     * 获取指纹创建时间戳
     * @return 时间戳
     */
    public long getTimestamp() {
        return timestamp;
    }
    
    /**
     * 获取所有指纹数据
     * @return 指纹数据映射
     */
    public Map<String, String> getAllData() {
        return new HashMap<>(fingerprintData);
    }
    
    /**
     * 计算指纹的哈希值
     * @return SHA-256哈希值
     */
    public String getFingerprint() {
        try {
            StringBuilder sb = new StringBuilder();
            
            // 按固定顺序拼接所有数据
            sb.append(fingerprintData.get("deviceId"));
            sb.append(fingerprintData.get("hardware"));
            sb.append(fingerprintData.get("software"));
            sb.append(fingerprintData.get("network"));
            
            // 计算SHA-256哈希
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            byte[] hash = md.digest(sb.toString().getBytes("UTF-8"));
            
            // 转换为十六进制字符串
            StringBuilder hexString = new StringBuilder();
            for (byte b : hash) {
                String hex = Integer.toHexString(0xff & b);
                if (hex.length() == 1) {
                    hexString.append('0');
                }
                hexString.append(hex);
            }
            
            return hexString.toString();
        } catch (Exception e) {
            return "hash_error";
        }
    }
    
    /**
     * 与另一个指纹比较相似度
     * @param other 另一个设备指纹
     * @return 相似度分数 (0-100)
     */
    public int similarity(DeviceFingerprint other) {
        if (other == null) return 0;
        
        int totalScore = 0;
        int maxScore = 0;
        
        // 比较设备ID
        maxScore += 25;
        if (this.deviceId != null && this.deviceId.equals(other.deviceId)) {
            totalScore += 25;
        }
        
        // 比较硬件信息
        maxScore += 25;
        if (compareStrings(this.getHardwareInfo(), other.getHardwareInfo()) > 0.8) {
            totalScore += 25;
        }
        
        // 比较软件信息
        maxScore += 25;
        if (compareStrings(this.getSoftwareInfo(), other.getSoftwareInfo()) > 0.7) {
            totalScore += 25;
        }
        
        // 比较网络信息（权重较低，因为网络环境容易变化）
        maxScore += 25;
        if (compareStrings(this.getNetworkInfo(), other.getNetworkInfo()) > 0.5) {
            totalScore += 25;
        }
        
        return (totalScore * 100) / maxScore;
    }
    
    private double compareStrings(String s1, String s2) {
        if (s1 == null || s2 == null) return 0.0;
        if (s1.equals(s2)) return 1.0;
        
        // 简单的字符串相似度计算
        int maxLen = Math.max(s1.length(), s2.length());
        if (maxLen == 0) return 1.0;
        
        int editDistance = calculateEditDistance(s1, s2);
        return 1.0 - (double) editDistance / maxLen;
    }
    
    private int calculateEditDistance(String s1, String s2) {
        int[][] dp = new int[s1.length() + 1][s2.length() + 1];
        
        for (int i = 0; i <= s1.length(); i++) {
            dp[i][0] = i;
        }
        
        for (int j = 0; j <= s2.length(); j++) {
            dp[0][j] = j;
        }
        
        for (int i = 1; i <= s1.length(); i++) {
            for (int j = 1; j <= s2.length(); j++) {
                if (s1.charAt(i - 1) == s2.charAt(j - 1)) {
                    dp[i][j] = dp[i - 1][j - 1];
                } else {
                    dp[i][j] = 1 + Math.min(Math.min(dp[i - 1][j], dp[i][j - 1]), dp[i - 1][j - 1]);
                }
            }
        }
        
        return dp[s1.length()][s2.length()];
    }
    
    /**
     * 检查指纹是否有效
     * @return 是否有效
     */
    public boolean isValid() {
        return deviceId != null && 
               !deviceId.isEmpty() && 
               fingerprintData.size() >= 3;
    }
    
    /**
     * 转换为JSON字符串
     * @return JSON格式的指纹数据
     */
    public String toJson() {
        StringBuilder json = new StringBuilder();
        json.append("{");
        json.append("\"timestamp\":").append(timestamp).append(",");
        json.append("\"deviceId\":\"").append(escapeJson(deviceId)).append("\",");
        
        for (Map.Entry<String, String> entry : fingerprintData.entrySet()) {
            if (!entry.getKey().equals("deviceId")) {
                json.append("\"").append(escapeJson(entry.getKey())).append("\":");
                json.append("\"").append(escapeJson(entry.getValue())).append("\",");
            }
        }
        
        // 移除最后的逗号
        if (json.charAt(json.length() - 1) == ',') {
            json.setLength(json.length() - 1);
        }
        
        json.append("}");
        return json.toString();
    }
    
    private String escapeJson(String str) {
        if (str == null) return "";
        return str.replace("\\", "\\\\")
                 .replace("\"", "\\\"")
                 .replace("\n", "\\n")
                 .replace("\r", "\\r")
                 .replace("\t", "\\t");
    }
    
    @Override
    public String toString() {
        return String.format("DeviceFingerprint{deviceId='%s', timestamp=%d, dataSize=%d}", 
                           deviceId, timestamp, fingerprintData.size());
    }
    
    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        
        DeviceFingerprint that = (DeviceFingerprint) obj;
        return deviceId != null ? deviceId.equals(that.deviceId) : that.deviceId == null;
    }
    
    @Override
    public int hashCode() {
        return deviceId != null ? deviceId.hashCode() : 0;
    }
}