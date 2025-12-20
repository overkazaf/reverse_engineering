package com.riskcontrol;

import java.util.ArrayList;
import java.util.List;

/**
 * 安全检测结果类
 * 包含各种安全威胁的检测结果
 */
public class SecurityResult {
    private boolean isEmulator = false;
    private boolean isRooted = false;
    private boolean isDebugging = false;
    private boolean isHooked = false;
    private boolean isProxy = false;
    private boolean isVpn = false;
    private List<String> threatDetails = new ArrayList<>();
    private int securityScore = 100; // 100为最安全
    
    // ========== Getter和Setter方法 ==========
    
    public boolean isEmulator() {
        return isEmulator;
    }
    
    public void setEmulator(boolean emulator) {
        isEmulator = emulator;
        if (emulator) {
            threatDetails.add("模拟器环境检测");
            securityScore -= 30;
        }
    }
    
    public boolean isRooted() {
        return isRooted;
    }
    
    public void setRooted(boolean rooted) {
        isRooted = rooted;
        if (rooted) {
            threatDetails.add("设备已Root");
            securityScore -= 25;
        }
    }
    
    public boolean isDebugging() {
        return isDebugging;
    }
    
    public void setDebugging(boolean debugging) {
        isDebugging = debugging;
        if (debugging) {
            threatDetails.add("调试器附加");
            securityScore -= 20;
        }
    }
    
    public boolean isHooked() {
        return isHooked;
    }
    
    public void setHooked(boolean hooked) {
        isHooked = hooked;
        if (hooked) {
            threatDetails.add("Hook框架检测");
            securityScore -= 15;
        }
    }
    
    public boolean isProxy() {
        return isProxy;
    }
    
    public void setProxy(boolean proxy) {
        isProxy = proxy;
        if (proxy) {
            threatDetails.add("代理服务器");
            securityScore -= 10;
        }
    }
    
    public boolean isVpn() {
        return isVpn;
    }
    
    public void setVpn(boolean vpn) {
        isVpn = vpn;
        if (vpn) {
            threatDetails.add("VPN连接");
            securityScore -= 5;
        }
    }
    
    /**
     * 获取安全评分
     * @return 安全分数 (0-100，100最安全)
     */
    public int getSecurityScore() {
        return Math.max(0, securityScore);
    }
    
    /**
     * 获取威胁详情列表
     * @return 威胁详情
     */
    public List<String> getThreatDetails() {
        return new ArrayList<>(threatDetails);
    }
    
    /**
     * 获取安全等级
     * @return 安全等级字符串
     */
    public String getSecurityLevel() {
        int score = getSecurityScore();
        if (score >= 90) return "安全";
        if (score >= 70) return "较安全";
        if (score >= 50) return "中等风险";
        if (score >= 30) return "高风险";
        return "极高风险";
    }
    
    /**
     * 检查是否存在任何安全威胁
     * @return 是否存在威胁
     */
    public boolean hasThreat() {
        return isEmulator || isRooted || isDebugging || isHooked || isProxy || isVpn;
    }
    
    /**
     * 获取检测到的威胁数量
     * @return 威胁数量
     */
    public int getThreatCount() {
        int count = 0;
        if (isEmulator) count++;
        if (isRooted) count++;
        if (isDebugging) count++;
        if (isHooked) count++;
        if (isProxy) count++;
        if (isVpn) count++;
        return count;
    }
    
    /**
     * 获取建议的安全措施
     * @return 安全建议列表
     */
    public List<String> getSecurityRecommendations() {
        List<String> recommendations = new ArrayList<>();
        
        if (isEmulator) {
            recommendations.add("禁止在模拟器环境下使用");
        }
        if (isRooted) {
            recommendations.add("建议使用未Root的设备");
        }
        if (isDebugging) {
            recommendations.add("检测到调试行为，请停止调试");
        }
        if (isHooked) {
            recommendations.add("检测到Hook框架，存在被篡改风险");
        }
        if (isProxy) {
            recommendations.add("建议关闭代理服务器");
        }
        if (isVpn) {
            recommendations.add("建议断开VPN连接");
        }
        
        if (recommendations.isEmpty()) {
            recommendations.add("设备安全状态良好");
        }
        
        return recommendations;
    }
    
    /**
     * 转换为JSON字符串
     * @return JSON格式的安全检测结果
     */
    public String toJson() {
        StringBuilder json = new StringBuilder();
        json.append("{");
        json.append("\"isEmulator\":").append(isEmulator).append(",");
        json.append("\"isRooted\":").append(isRooted).append(",");
        json.append("\"isDebugging\":").append(isDebugging).append(",");
        json.append("\"isHooked\":").append(isHooked).append(",");
        json.append("\"isProxy\":").append(isProxy).append(",");
        json.append("\"isVpn\":").append(isVpn).append(",");
        json.append("\"securityScore\":").append(getSecurityScore()).append(",");
        json.append("\"securityLevel\":\"").append(getSecurityLevel()).append("\",");
        json.append("\"threatCount\":").append(getThreatCount()).append(",");
        json.append("\"threatDetails\":[");
        
        for (int i = 0; i < threatDetails.size(); i++) {
            json.append("\"").append(escapeJson(threatDetails.get(i))).append("\"");
            if (i < threatDetails.size() - 1) {
                json.append(",");
            }
        }
        json.append("]}");
        
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
        return String.format("SecurityResult{score=%d, level='%s', threats=%d}", 
                           getSecurityScore(), getSecurityLevel(), getThreatCount());
    }
}