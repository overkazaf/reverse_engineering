package com.riskcontrol;

import java.util.Map;
import java.util.HashMap;

/**
 * 风险评分结果类
 * 包含设备的综合风险评分和详细分析
 */
public class RiskScore {
    private int riskLevel; // 0-100，100为最高风险
    private String riskDetails;
    private Map<String, Integer> riskFactors;
    private long timestamp;
    
    public RiskScore(int riskLevel, String details) {
        this.riskLevel = Math.max(0, Math.min(100, riskLevel));
        this.riskDetails = details != null ? details : "";
        this.riskFactors = new HashMap<>();
        this.timestamp = System.currentTimeMillis();
        parseRiskDetails();
    }
    
    /**
     * 获取风险等级分数
     * @return 风险分数 (0-100，100为最高风险)
     */
    public int getRiskLevel() {
        return riskLevel;
    }
    
    /**
     * 获取风险等级描述
     * @return 风险等级字符串
     */
    public String getRiskLevelDescription() {
        if (riskLevel <= 20) return "低风险";
        if (riskLevel <= 40) return "较低风险";
        if (riskLevel <= 60) return "中等风险";
        if (riskLevel <= 80) return "高风险";
        return "极高风险";
    }
    
    /**
     * 获取风险详情
     * @return 风险详细信息
     */
    public String getRiskDetails() {
        return riskDetails;
    }
    
    /**
     * 获取时间戳
     * @return 评分时间戳
     */
    public long getTimestamp() {
        return timestamp;
    }
    
    /**
     * 获取各个风险因子的分数
     * @return 风险因子映射
     */
    public Map<String, Integer> getRiskFactors() {
        return new HashMap<>(riskFactors);
    }
    
    /**
     * 获取特定风险因子的分数
     * @param factor 风险因子名称
     * @return 分数，如果不存在返回0
     */
    public int getRiskFactor(String factor) {
        return riskFactors.getOrDefault(factor, 0);
    }
    
    /**
     * 检查是否允许操作
     * @param threshold 风险阈值
     * @return 是否允许
     */
    public boolean isAllowed(int threshold) {
        return riskLevel <= threshold;
    }
    
    /**
     * 获取风险颜色代码（用于UI显示）
     * @return 颜色代码
     */
    public String getColorCode() {
        if (riskLevel <= 20) return "#00C851"; // 绿色
        if (riskLevel <= 40) return "#FFBB33"; // 黄色
        if (riskLevel <= 60) return "#FF8800"; // 橙色
        if (riskLevel <= 80) return "#FF4444"; // 红色
        return "#CC0000"; // 深红色
    }
    
    /**
     * 获取建议的处理策略
     * @return 策略建议列表
     */
    public String[] getRecommendedActions() {
        if (riskLevel <= 20) {
            return new String[]{"正常放行", "记录日志"};
        } else if (riskLevel <= 40) {
            return new String[]{"增强监控", "记录详细日志"};
        } else if (riskLevel <= 60) {
            return new String[]{"二次验证", "人工审核", "限制功能"};
        } else if (riskLevel <= 80) {
            return new String[]{"拒绝服务", "加入观察列表", "人工介入"};
        } else {
            return new String[]{"立即阻断", "加入黑名单", "安全团队处理"};
        }
    }
    
    /**
     * 解析风险详情，提取各个风险因子
     */
    private void parseRiskDetails() {
        if (riskDetails == null || riskDetails.isEmpty()) {
            return;
        }
        
        // 简单的解析逻辑，实际实现可能更复杂
        String[] factors = riskDetails.split(";");
        for (String factor : factors) {
            if (factor.contains(":")) {
                String[] parts = factor.split(":");
                if (parts.length == 2) {
                    try {
                        String name = parts[0].trim();
                        int score = Integer.parseInt(parts[1].trim());
                        riskFactors.put(name, score);
                    } catch (NumberFormatException e) {
                        // 忽略解析错误
                    }
                }
            }
        }
    }
    
    /**
     * 与历史风险评分比较
     * @param historical 历史评分
     * @return 比较结果：正数表示风险增加，负数表示风险降低
     */
    public int compareWith(RiskScore historical) {
        if (historical == null) return riskLevel;
        return this.riskLevel - historical.riskLevel;
    }
    
    /**
     * 检查风险是否在可接受范围内
     * @return 是否可接受
     */
    public boolean isAcceptableRisk() {
        return riskLevel <= 30; // 默认阈值为30
    }
    
    /**
     * 获取风险趋势（需要历史数据支持）
     * @param previousScores 历史评分数组
     * @return 趋势描述
     */
    public String getRiskTrend(RiskScore[] previousScores) {
        if (previousScores == null || previousScores.length == 0) {
            return "无历史数据";
        }
        
        int totalChange = 0;
        for (RiskScore score : previousScores) {
            if (score != null) {
                totalChange += (this.riskLevel - score.riskLevel);
            }
        }
        
        double avgChange = (double) totalChange / previousScores.length;
        
        if (avgChange > 5) return "风险上升";
        if (avgChange < -5) return "风险下降";
        return "风险稳定";
    }
    
    /**
     * 转换为JSON字符串
     * @return JSON格式的风险评分
     */
    public String toJson() {
        StringBuilder json = new StringBuilder();
        json.append("{");
        json.append("\"riskLevel\":").append(riskLevel).append(",");
        json.append("\"riskLevelDescription\":\"").append(getRiskLevelDescription()).append("\",");
        json.append("\"riskDetails\":\"").append(escapeJson(riskDetails)).append("\",");
        json.append("\"timestamp\":").append(timestamp).append(",");
        json.append("\"colorCode\":\"").append(getColorCode()).append("\",");
        json.append("\"isAcceptable\":").append(isAcceptableRisk()).append(",");
        
        json.append("\"riskFactors\":{");
        int i = 0;
        for (Map.Entry<String, Integer> entry : riskFactors.entrySet()) {
            json.append("\"").append(escapeJson(entry.getKey())).append("\":");
            json.append(entry.getValue());
            if (++i < riskFactors.size()) {
                json.append(",");
            }
        }
        json.append("},");
        
        json.append("\"recommendedActions\":[");
        String[] actions = getRecommendedActions();
        for (int j = 0; j < actions.length; j++) {
            json.append("\"").append(escapeJson(actions[j])).append("\"");
            if (j < actions.length - 1) {
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
        return String.format("RiskScore{level=%d (%s), acceptable=%b, factors=%d}", 
                           riskLevel, getRiskLevelDescription(), isAcceptableRisk(), riskFactors.size());
    }
    
    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        
        RiskScore riskScore = (RiskScore) obj;
        return riskLevel == riskScore.riskLevel;
    }
    
    @Override
    public int hashCode() {
        return riskLevel;
    }
}