import com.riskcontrol.*;
import java.util.HashMap;
import java.util.Map;

/**
 * 风控SDK演示程序
 * 展示设备指纹采集、安全检测、风险评估等功能
 */
public class RiskControlDemo {
    
    public static void main(String[] args) {
        System.out.println("=".repeat(80));
        System.out.println("           Risk Control SDK - 设备指纹风控演示");
        System.out.println("=".repeat(80));
        
        try {
            // 1. 初始化SDK
            System.out.println("\n[1] 正在初始化风控SDK...");
            RiskControlSDK sdk = RiskControlSDK.getInstance();
            
            if (!sdk.initialize(null)) {
                System.err.println("[-] SDK初始化失败！");
                System.exit(1);
            }
            
            System.out.println("[+] SDK初始化成功");
            System.out.println("    版本: " + sdk.getVersion());
            
            // 2. 配置SDK
            System.out.println("\n[2] 配置SDK参数...");
            sdk.setDebugMode(true);
            
            Map<String, String> config = new HashMap<>();
            config.put("risk_threshold", "60");
            config.put("enable_svc", "true");
            config.put("anti_debug", "true");
            sdk.setConfiguration(config);
            
            System.out.println("[+] SDK配置完成");
            
            // 3. 设备指纹采集
            System.out.println("\n[3] 采集设备指纹...");
            System.out.println("-".repeat(50));
            
            DeviceFingerprint fingerprint = sdk.getDeviceFingerprint();
            
            System.out.println("设备ID: " + fingerprint.getDeviceId());
            System.out.println("指纹哈希: " + fingerprint.getFingerprint());
            System.out.println("创建时间: " + fingerprint.getTimestamp());
            
            // 显示详细信息
            System.out.println("\n硬件信息:");
            System.out.println(formatJson(fingerprint.getHardwareInfo()));
            
            System.out.println("\n软件信息:");
            System.out.println(formatJson(fingerprint.getSoftwareInfo()));
            
            System.out.println("\n网络信息:");
            System.out.println(formatJson(fingerprint.getNetworkInfo()));
            
            // 4. 安全检测
            System.out.println("\n[4] 执行安全检测...");
            System.out.println("-".repeat(50));
            
            SecurityResult security = sdk.performSecurityCheck();
            
            System.out.println("安全评分: " + security.getSecurityScore() + "/100");
            System.out.println("安全等级: " + security.getSecurityLevel());
            
            // 显示检测结果
            System.out.println("\n威胁检测结果:");
            System.out.printf("  模拟器检测: %s%n", security.isEmulator() ? "❌ 检测到" : "✅ 正常");
            System.out.printf("  Root检测: %s%n", security.isRooted() ? "❌ 检测到" : "✅ 正常");
            System.out.printf("  调试检测: %s%n", security.isDebugging() ? "❌ 检测到" : "✅ 正常");
            System.out.printf("  Hook检测: %s%n", security.isHooked() ? "❌ 检测到" : "✅ 正常");
            System.out.printf("  代理检测: %s%n", security.isProxy() ? "❌ 检测到" : "✅ 正常");
            System.out.printf("  VPN检测: %s%n", security.isVpn() ? "❌ 检测到" : "✅ 正常");
            
            if (security.hasThreat()) {
                System.out.println("\n检测到的威胁:");
                for (String threat : security.getThreatDetails()) {
                    System.out.println("  ⚠️  " + threat);
                }
                
                System.out.println("\n安全建议:");
                for (String recommendation : security.getSecurityRecommendations()) {
                    System.out.println("  💡 " + recommendation);
                }
            }
            
            // 5. 风险评估
            System.out.println("\n[5] 综合风险评估...");
            System.out.println("-".repeat(50));
            
            RiskScore riskScore = sdk.assessRisk();
            
            System.out.println("风险分数: " + riskScore.getRiskLevel() + "/100");
            System.out.println("风险等级: " + riskScore.getRiskLevelDescription());
            System.out.println("颜色代码: " + riskScore.getColorCode());
            System.out.println("是否可接受: " + (riskScore.isAcceptableRisk() ? "✅ 是" : "❌ 否"));
            
            // 显示风险因子
            System.out.println("\n风险因子分析:");
            Map<String, Integer> riskFactors = riskScore.getRiskFactors();
            for (Map.Entry<String, Integer> factor : riskFactors.entrySet()) {
                System.out.printf("  %s: %d分%n", factor.getKey(), factor.getValue());
            }
            
            // 显示处理建议
            System.out.println("\n建议处理策略:");
            String[] actions = riskScore.getRecommendedActions();
            for (String action : actions) {
                System.out.println("  📋 " + action);
            }
            
            // 6. JSON格式输出
            System.out.println("\n[6] JSON格式数据输出");
            System.out.println("-".repeat(50));
            
            System.out.println("\n设备指纹JSON:");
            System.out.println(fingerprint.toJson());
            
            System.out.println("\n安全检测JSON:");
            System.out.println(security.toJson());
            
            System.out.println("\n风险评估JSON:");
            System.out.println(riskScore.toJson());
            
            // 7. 设备指纹比较（模拟）
            System.out.println("\n[7] 设备指纹相似度比较");
            System.out.println("-".repeat(50));
            
            // 创建一个相似的指纹进行比较
            DeviceFingerprint similarFingerprint = sdk.getDeviceFingerprint();
            int similarity = fingerprint.similarity(similarFingerprint);
            System.out.println("与当前设备相似度: " + similarity + "%");
            
            // 8. 性能测试
            System.out.println("\n[8] 性能测试");
            System.out.println("-".repeat(50));
            
            long startTime = System.currentTimeMillis();
            
            // 连续执行多次检测
            int testRounds = 10;
            System.out.println("执行 " + testRounds + " 轮完整检测...");
            
            for (int i = 0; i < testRounds; i++) {
                sdk.getDeviceFingerprint();
                sdk.performSecurityCheck();
                sdk.assessRisk();
                System.out.print(".");
            }
            
            long endTime = System.currentTimeMillis();
            long duration = endTime - startTime;
            
            System.out.println("\n性能统计:");
            System.out.println("  总耗时: " + duration + "ms");
            System.out.println("  平均耗时: " + (duration / testRounds) + "ms/轮");
            System.out.println("  处理速度: " + (testRounds * 1000 / duration) + "次/秒");
            
            // 9. 清理资源
            System.out.println("\n[9] 清理SDK资源...");
            sdk.cleanup();
            System.out.println("[+] 资源清理完成");
            
        } catch (Exception e) {
            System.err.println("[-] 发生异常: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
        
        System.out.println("\n" + "=".repeat(80));
        System.out.println("                    演示程序执行完成");
        System.out.println("=".repeat(80));
    }
    
    /**
     * 格式化JSON字符串输出
     * @param json JSON字符串
     * @return 格式化后的字符串
     */
    private static String formatJson(String json) {
        if (json == null || json.isEmpty()) {
            return "{}";
        }
        
        // 简单的JSON格式化
        StringBuilder formatted = new StringBuilder();
        int indent = 0;
        boolean inString = false;
        
        for (char c : json.toCharArray()) {
            switch (c) {
                case '{':
                case '[':
                    if (!inString) {
                        formatted.append(c).append('\n');
                        indent++;
                        addIndent(formatted, indent);
                    } else {
                        formatted.append(c);
                    }
                    break;
                case '}':
                case ']':
                    if (!inString) {
                        formatted.append('\n');
                        indent--;
                        addIndent(formatted, indent);
                        formatted.append(c);
                    } else {
                        formatted.append(c);
                    }
                    break;
                case ',':
                    formatted.append(c);
                    if (!inString) {
                        formatted.append('\n');
                        addIndent(formatted, indent);
                    }
                    break;
                case '"':
                    formatted.append(c);
                    inString = !inString;
                    break;
                default:
                    formatted.append(c);
                    break;
            }
        }
        
        return formatted.toString();
    }
    
    private static void addIndent(StringBuilder sb, int indent) {
        for (int i = 0; i < indent * 2; i++) {
            sb.append(' ');
        }
    }
}