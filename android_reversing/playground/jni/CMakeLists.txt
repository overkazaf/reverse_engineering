cmake_minimum_required(VERSION 3.10)
project(JNIDemo)

# 设置 C 标准
set(CMAKE_C_STANDARD 99)

# 查找 JNI
find_package(JNI REQUIRED)

# 包含 JNI 头文件目录
include_directories(${JNI_INCLUDE_DIRS})
include_directories(include)

# 定义源文件
set(NATIVE_SOURCES
    src/native/jni_demo.c
    src/native/crypto_utils.c
)

# 创建共享库
add_library(jnidemo SHARED ${NATIVE_SOURCES})

# 链接 JNI 库
target_link_libraries(jnidemo ${JNI_LIBRARIES})

# 设置输出目录
set_target_properties(jnidemo PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}
)

# 如果是 macOS，修改库文件扩展名
if(APPLE)
    set_target_properties(jnidemo PROPERTIES SUFFIX .jnilib)
endif()

# 编译 Java 源文件
find_program(JAVAC_EXECUTABLE javac)
find_program(JAVAH_EXECUTABLE javah)

if(JAVAC_EXECUTABLE)
    # 创建 Java 类输出目录
    file(MAKE_DIRECTORY ${CMAKE_BINARY_DIR}/classes)
    
    # 编译 Java 文件
    add_custom_command(
        OUTPUT ${CMAKE_BINARY_DIR}/classes/com/example/JNIDemo.class
        COMMAND ${JAVAC_EXECUTABLE} 
            -d ${CMAKE_BINARY_DIR}/classes 
            ${CMAKE_SOURCE_DIR}/src/com/example/JNIDemo.java
        DEPENDS ${CMAKE_SOURCE_DIR}/src/com/example/JNIDemo.java
        COMMENT "编译 Java 源文件"
    )
    
    # 生成 JNI 头文件 (如果需要)
    if(JAVAH_EXECUTABLE)
        add_custom_command(
            OUTPUT ${CMAKE_SOURCE_DIR}/src/native/jni_demo_generated.h
            COMMAND ${JAVAH_EXECUTABLE} 
                -cp ${CMAKE_BINARY_DIR}/classes 
                -o ${CMAKE_SOURCE_DIR}/src/native/jni_demo_generated.h
                com.example.JNIDemo
            DEPENDS ${CMAKE_BINARY_DIR}/classes/com/example/JNIDemo.class
            COMMENT "生成 JNI 头文件"
        )
        
        add_custom_target(generate_headers DEPENDS 
            ${CMAKE_SOURCE_DIR}/src/native/jni_demo_generated.h)
        add_dependencies(jnidemo generate_headers)
    endif()
    
    # 创建编译 Java 的目标
    add_custom_target(compile_java ALL DEPENDS 
        ${CMAKE_BINARY_DIR}/classes/com/example/JNIDemo.class)
    
    # 复制编译后的类文件到输出目录
    add_custom_command(TARGET compile_java POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_directory
            ${CMAKE_BINARY_DIR}/classes
            ${CMAKE_BINARY_DIR}
        COMMENT "复制编译后的 Java 类文件"
    )
endif()

# 创建测试目标
add_custom_target(test
    COMMAND java -Djava.library.path=${CMAKE_BINARY_DIR} 
                 -cp ${CMAKE_BINARY_DIR} 
                 com.example.JNIDemo
    DEPENDS jnidemo compile_java
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    COMMENT "运行 JNI 测试程序"
)

# 清理目标
add_custom_target(clean-all
    COMMAND ${CMAKE_COMMAND} -E remove_directory ${CMAKE_BINARY_DIR}/classes
    COMMAND ${CMAKE_COMMAND} -E remove ${CMAKE_BINARY_DIR}/*.so
    COMMAND ${CMAKE_COMMAND} -E remove ${CMAKE_BINARY_DIR}/*.dylib
    COMMAND ${CMAKE_COMMAND} -E remove ${CMAKE_BINARY_DIR}/*.jnilib
    COMMENT "清理所有生成的文件"
)

# 安装规则（可选）
install(TARGETS jnidemo
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin
)

# 打印配置信息
message(STATUS "JNI Include Dirs: ${JNI_INCLUDE_DIRS}")
message(STATUS "JNI Libraries: ${JNI_LIBRARIES}")
message(STATUS "Build Type: ${CMAKE_BUILD_TYPE}")
message(STATUS "C Compiler: ${CMAKE_C_COMPILER}")

# 调试版本的额外标志
if(CMAKE_BUILD_TYPE STREQUAL "Debug")
    target_compile_options(jnidemo PRIVATE -g -O0 -DDEBUG)
    message(STATUS "Debug mode enabled")
else()
    target_compile_options(jnidemo PRIVATE -O2 -DNDEBUG)
endif()

# 警告选项
target_compile_options(jnidemo PRIVATE -Wall -Wextra)