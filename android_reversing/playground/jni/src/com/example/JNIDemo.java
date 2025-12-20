package com.example;

/**
 * JNI 演示类
 * 展示 Java 与 Native 代码的交互
 */
public class JNIDemo {
    
    // 加载本地库
    static {
        try {
            System.loadLibrary("jnidemo");
            System.out.println("[+] Native library loaded successfully");
        } catch (UnsatisfiedLinkError e) {
            System.err.println("[-] Failed to load native library: " + e.getMessage());
            System.exit(1);
        }
    }
    
    // ========== 基础数据类型演示 ==========
    
    /**
     * 字符串处理示例
     */
    public static native String processString(String input);
    
    /**
     * 整数计算示例
     */
    public static native int addNumbers(int a, int b);
    
    /**
     * 布尔值转换示例
     */
    public static native boolean checkString(String str);
    
    // ========== 数组操作演示 ==========
    
    /**
     * 字节数组加密（XOR 示例）
     */
    public static native byte[] encryptBytes(byte[] data, int key);
    
    /**
     * 字节数组解密
     */
    public static native byte[] decryptBytes(byte[] data, int key);
    
    /**
     * 整数数组求和
     */
    public static native int sumIntArray(int[] numbers);
    
    // ========== 复杂数据结构演示 ==========
    
    /**
     * 字符串数组处理
     */
    public static native String[] processStringArray(String[] inputs);
    
    /**
     * Base64 编码示例
     */
    public static native String base64Encode(byte[] data);
    
    /**
     * Base64 解码示例
     */
    public static native byte[] base64Decode(String data);
    
    // ========== 回调机制演示 ==========
    
    /**
     * Java 回调方法（被 native 代码调用）
     */
    public void javaCallback(String message) {
        System.out.println("[Java Callback] " + message);
    }
    
    /**
     * 触发回调的 native 方法
     */
    public native void triggerCallback();
    
    // ========== 异常处理演示 ==========
    
    /**
     * 会抛出异常的 native 方法
     */
    public static native void throwException() throws RuntimeException;
    
    /**
     * 检查并处理异常的 native 方法
     */
    public static native boolean handleException();
    
    // ========== 性能测试 ==========
    
    /**
     * 性能测试：大量 JNI 调用
     */
    public static native long performanceTest(int iterations);
    
    /**
     * 获取系统信息
     */
    public static native String getSystemInfo();
    
    // ========== 主方法：演示所有功能 ==========
    
    public static void main(String[] args) {
        System.out.println("=".repeat(60));
        System.out.println("            JNI Demo - Java Native Interface");
        System.out.println("=".repeat(60));
        
        JNIDemo demo = new JNIDemo();
        
        // 1. 基础数据类型测试
        System.out.println("\n[1] 基础数据类型测试");
        System.out.println("-".repeat(30));
        
        String result = processString("Hello JNI!");
        System.out.println("String processing: " + result);
        
        int sum = addNumbers(42, 58);
        System.out.println("42 + 58 = " + sum);
        
        boolean check = checkString("test");
        System.out.println("String check result: " + check);
        
        // 2. 数组操作测试
        System.out.println("\n[2] 数组操作测试");
        System.out.println("-".repeat(30));
        
        byte[] originalData = "Secret Message".getBytes();
        System.out.println("Original: " + new String(originalData));
        
        byte[] encrypted = encryptBytes(originalData, 0x42);
        System.out.print("Encrypted: ");
        for (byte b : encrypted) {
            System.out.printf("%02X ", b);
        }
        System.out.println();
        
        byte[] decrypted = decryptBytes(encrypted, 0x42);
        System.out.println("Decrypted: " + new String(decrypted));
        
        int[] numbers = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};
        int arraySum = sumIntArray(numbers);
        System.out.println("Array sum (1-10): " + arraySum);
        
        // 3. 字符串数组测试
        System.out.println("\n[3] 字符串数组测试");
        System.out.println("-".repeat(30));
        
        String[] inputs = {"apple", "banana", "cherry"};
        String[] processed = processStringArray(inputs);
        System.out.print("Processed strings: ");
        for (String s : processed) {
            System.out.print(s + " ");
        }
        System.out.println();
        
        // 4. Base64 编码测试
        System.out.println("\n[4] Base64 编码测试");
        System.out.println("-".repeat(30));
        
        String message = "Hello World!";
        String encoded = base64Encode(message.getBytes());
        System.out.println("Encoded: " + encoded);
        
        byte[] decoded = base64Decode(encoded);
        System.out.println("Decoded: " + new String(decoded));
        
        // 5. 回调机制测试
        System.out.println("\n[5] 回调机制测试");
        System.out.println("-".repeat(30));
        
        demo.triggerCallback();
        
        // 6. 异常处理测试
        System.out.println("\n[6] 异常处理测试");
        System.out.println("-".repeat(30));
        
        try {
            throwException();
        } catch (RuntimeException e) {
            System.out.println("Caught exception: " + e.getMessage());
        }
        
        boolean exceptionHandled = handleException();
        System.out.println("Exception handled in native: " + exceptionHandled);
        
        // 7. 系统信息
        System.out.println("\n[7] 系统信息");
        System.out.println("-".repeat(30));
        
        String sysInfo = getSystemInfo();
        System.out.println(sysInfo);
        
        // 8. 性能测试
        System.out.println("\n[8] 性能测试");
        System.out.println("-".repeat(30));
        
        int iterations = 1000000;
        System.out.println("Running " + iterations + " JNI calls...");
        long duration = performanceTest(iterations);
        System.out.println("Duration: " + duration + " ms");
        System.out.println("Average: " + (double)duration / iterations * 1000 + " μs per call");
        
        System.out.println("\n" + "=".repeat(60));
        System.out.println("All tests completed successfully!");
        System.out.println("=".repeat(60));
    }
}