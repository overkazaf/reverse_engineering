cmake_minimum_required(VERSION 3.10)
project(RiskControlSDK VERSION 1.0.0)

# 设置 C 标准
set(CMAKE_C_STANDARD 99)
set(CMAKE_CXX_STANDARD 11)

# 配置选项
option(ENABLE_DEBUG "Enable debug mode" OFF)
option(ENABLE_ANTI_REVERSE "Enable anti-reverse engineering protection" ON)
option(ENABLE_SVC_SYSCALLS "Enable SVC system calls" ON)
option(BUILD_ANDROID "Build for Android platform" OFF)

# 编译器标志
if(ENABLE_DEBUG)
    add_definitions(-DDEBUG=1)
    set(CMAKE_BUILD_TYPE Debug)
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -g -O0")
else()
    add_definitions(-DNDEBUG=1)
    set(CMAKE_BUILD_TYPE Release)
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -O2 -s")
endif()

# 反逆向保护编译选项
if(ENABLE_ANTI_REVERSE)
    add_definitions(-DANTI_REVERSE_ENABLED=1)
    # 启用代码混淆和加固选项
    if(CMAKE_C_COMPILER_ID MATCHES "Clang")
        set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fno-stack-protector")
        set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fvisibility=hidden")
        set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -ffunction-sections -fdata-sections")
    endif()
endif()

# SVC系统调用支持
if(ENABLE_SVC_SYSCALLS)
    add_definitions(-DSVC_SYSCALLS_ENABLED=1)
endif()

# Android 平台配置
if(BUILD_ANDROID)
    add_definitions(-DANDROID_PLATFORM=1)
    
    # Android NDK 配置
    if(ANDROID_NDK)
        set(CMAKE_SYSTEM_NAME Android)
        set(CMAKE_SYSTEM_VERSION ${ANDROID_PLATFORM})
        set(CMAKE_ANDROID_ARCH_ABI ${ANDROID_ABI})
        set(CMAKE_ANDROID_NDK ${ANDROID_NDK})
    endif()
endif()

# 查找 JNI
find_package(JNI REQUIRED)
if(JNI_FOUND)
    message(STATUS "JNI found: ${JNI_INCLUDE_DIRS}")
    include_directories(${JNI_INCLUDE_DIRS})
else()
    message(FATAL_ERROR "JNI not found")
endif()

# 包含目录
include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${CMAKE_CURRENT_SOURCE_DIR}/src/native
)

# 源文件列表
set(NATIVE_SOURCES
    src/native/risk_control.c
    src/native/anti_reverse.c
    src/native/art_method_hook.c
)

# 条件编译源文件
if(ENABLE_SVC_SYSCALLS)
    list(APPEND NATIVE_SOURCES src/native/svc_syscall.c)
endif()

# 创建共享库
add_library(riskcontrol SHARED ${NATIVE_SOURCES})

# 链接库
target_link_libraries(riskcontrol ${JNI_LIBRARIES})

# 在非 Android 平台上链接 dl 库
if(NOT BUILD_ANDROID)
    target_link_libraries(riskcontrol dl)
endif()

# 设置目标属性
set_target_properties(riskcontrol PROPERTIES
    VERSION ${PROJECT_VERSION}
    SOVERSION 1
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib
)

# 平台特定设置
if(APPLE)
    set_target_properties(riskcontrol PROPERTIES
        SUFFIX .jnilib
        MACOSX_RPATH ON
    )
elseif(ANDROID)
    # Android 特定设置
    set_target_properties(riskcontrol PROPERTIES
        ANDROID_GUI TRUE
    )
    
    # 链接 Android 特定库
    target_link_libraries(riskcontrol log android)
endif()

# 编译选项
target_compile_options(riskcontrol PRIVATE
    -Wall
    -Wextra
    -Wno-unused-parameter
    -fPIC
)

# 安全编译选项
if(ENABLE_ANTI_REVERSE)
    target_compile_options(riskcontrol PRIVATE
        -fstack-protector-all
        -D_FORTIFY_SOURCE=2
        -Wformat
        -Wformat-security
    )
    
    # 链接时优化
    if(CMAKE_BUILD_TYPE STREQUAL "Release")
        target_link_options(riskcontrol PRIVATE
            -Wl,--gc-sections
            -Wl,--strip-all
        )
    endif()
endif()

# Java 编译部分
find_program(JAVAC_EXECUTABLE javac)
find_program(JAR_EXECUTABLE jar)

if(JAVAC_EXECUTABLE AND JAR_EXECUTABLE)
    # Java 源文件
    file(GLOB_RECURSE JAVA_SOURCES "src/java/*.java")
    
    # 创建 Java 类输出目录
    set(JAVA_CLASS_DIR ${CMAKE_BINARY_DIR}/classes)
    file(MAKE_DIRECTORY ${JAVA_CLASS_DIR})
    
    # 编译 Java 文件
    add_custom_target(compile_java ALL
        COMMAND ${JAVAC_EXECUTABLE}
            -d ${JAVA_CLASS_DIR}
            -cp ${JAVA_CLASS_DIR}
            ${JAVA_SOURCES}
        DEPENDS ${JAVA_SOURCES}
        COMMENT "Compiling Java sources"
    )
    
    # 创建 JAR 文件
    add_custom_target(create_jar ALL
        COMMAND ${JAR_EXECUTABLE} 
            cvf ${CMAKE_BINARY_DIR}/lib/riskcontrol-sdk.jar
            -C ${JAVA_CLASS_DIR} .
        DEPENDS compile_java
        COMMENT "Creating JAR file"
    )
    
    # 依赖关系
    add_dependencies(create_jar riskcontrol)
endif()

# 示例程序
if(JAVAC_EXECUTABLE)
    # 创建示例程序
    add_custom_target(example ALL
        COMMAND ${CMAKE_COMMAND} -E copy_directory
            ${CMAKE_CURRENT_SOURCE_DIR}/examples
            ${CMAKE_BINARY_DIR}/examples
        COMMENT "Copying example files"
    )
    
    add_dependencies(example create_jar)
endif()

# 测试目标
enable_testing()

# 单元测试
add_custom_target(test_native
    COMMAND echo "Running native tests..."
    # 这里可以添加实际的测试命令
    COMMENT "Running native unit tests"
)

# Java 测试
if(JAVAC_EXECUTABLE)
    add_custom_target(test_java
        COMMAND java -Djava.library.path=${CMAKE_BINARY_DIR}/lib
                     -cp ${CMAKE_BINARY_DIR}/lib/riskcontrol-sdk.jar
                     com.riskcontrol.RiskControlSDK
        DEPENDS create_jar
        COMMENT "Running Java tests"
    )
endif()

# 基准测试
add_custom_target(benchmark
    COMMAND echo "Running performance benchmarks..."
    COMMENT "Running performance benchmarks"
)

# 文档生成
find_program(DOXYGEN_EXECUTABLE doxygen)
if(DOXYGEN_EXECUTABLE)
    configure_file(
        ${CMAKE_CURRENT_SOURCE_DIR}/Doxyfile.in
        ${CMAKE_CURRENT_BINARY_DIR}/Doxyfile
        @ONLY
    )
    
    add_custom_target(docs
        COMMAND ${DOXYGEN_EXECUTABLE} ${CMAKE_CURRENT_BINARY_DIR}/Doxyfile
        WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
        COMMENT "Generating API documentation with Doxygen"
    )
endif()

# 代码检查
find_program(CPPCHECK_EXECUTABLE cppcheck)
if(CPPCHECK_EXECUTABLE)
    add_custom_target(cppcheck
        COMMAND ${CPPCHECK_EXECUTABLE}
            --enable=all
            --std=c99
            --verbose
            --quiet
            ${CMAKE_CURRENT_SOURCE_DIR}/src/native
        COMMENT "Running static code analysis with cppcheck"
    )
endif()

# 内存检查
find_program(VALGRIND_EXECUTABLE valgrind)
if(VALGRIND_EXECUTABLE)
    add_custom_target(memcheck
        COMMAND ${VALGRIND_EXECUTABLE}
            --tool=memcheck
            --leak-check=full
            --show-leak-kinds=all
            --track-origins=yes
            ${CMAKE_BINARY_DIR}/lib/libriskcontrol.so
        COMMENT "Running memory check with Valgrind"
    )
endif()

# 安装规则
install(TARGETS riskcontrol
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin
    ARCHIVE DESTINATION lib
)

# 安装头文件
install(FILES
    src/native/risk_control.h
    src/native/anti_reverse.h
    DESTINATION include/riskcontrol
)

if(EXISTS ${CMAKE_BINARY_DIR}/lib/riskcontrol-sdk.jar)
    install(FILES ${CMAKE_BINARY_DIR}/lib/riskcontrol-sdk.jar
        DESTINATION lib
    )
endif()

# 安装示例
install(DIRECTORY examples/
    DESTINATION share/riskcontrol/examples
    PATTERN "*.java"
    PATTERN "*.md"
)

# 打包配置
set(CPACK_PACKAGE_NAME "RiskControlSDK")
set(CPACK_PACKAGE_VERSION ${PROJECT_VERSION})
set(CPACK_PACKAGE_DESCRIPTION_SUMMARY "Device Fingerprinting Risk Control SDK")
set(CPACK_PACKAGE_VENDOR "Security Research")
set(CPACK_PACKAGE_CONTACT "research@security.com")

if(ANDROID)
    set(CPACK_GENERATOR "TGZ")
    set(CPACK_PACKAGE_FILE_NAME "${CPACK_PACKAGE_NAME}-${CPACK_PACKAGE_VERSION}-android-${ANDROID_ABI}")
else()
    set(CPACK_GENERATOR "TGZ;ZIP")
    set(CPACK_PACKAGE_FILE_NAME "${CPACK_PACKAGE_NAME}-${CPACK_PACKAGE_VERSION}-${CMAKE_SYSTEM_NAME}")
endif()

include(CPack)

# 自定义目标汇总
add_custom_target(all_tests
    DEPENDS test_native test_java
    COMMENT "Running all tests"
)

add_custom_target(quality_check
    DEPENDS cppcheck memcheck
    COMMENT "Running quality checks"
)

# 清理目标
add_custom_target(clean-all
    COMMAND ${CMAKE_COMMAND} -E remove_directory ${CMAKE_BINARY_DIR}/lib
    COMMAND ${CMAKE_COMMAND} -E remove_directory ${CMAKE_BINARY_DIR}/classes
    COMMAND ${CMAKE_COMMAND} -E remove_directory ${CMAKE_BINARY_DIR}/examples
    COMMENT "Cleaning all generated files"
)

# 显示配置信息
message(STATUS "=== RiskControl SDK Configuration ===")
message(STATUS "Version: ${PROJECT_VERSION}")
message(STATUS "Build Type: ${CMAKE_BUILD_TYPE}")
message(STATUS "Debug Mode: ${ENABLE_DEBUG}")
message(STATUS "Anti-Reverse: ${ENABLE_ANTI_REVERSE}")
message(STATUS "SVC Syscalls: ${ENABLE_SVC_SYSCALLS}")
message(STATUS "Android Build: ${BUILD_ANDROID}")
message(STATUS "C Compiler: ${CMAKE_C_COMPILER}")
message(STATUS "C Flags: ${CMAKE_C_FLAGS}")
message(STATUS "JNI Include: ${JNI_INCLUDE_DIRS}")
message(STATUS "JNI Libraries: ${JNI_LIBRARIES}")
message(STATUS "=====================================")

# 构建脚本生成
configure_file(
    ${CMAKE_CURRENT_SOURCE_DIR}/scripts/build.sh.in
    ${CMAKE_CURRENT_BINARY_DIR}/build.sh
    @ONLY
)

# Android 构建脚本
if(BUILD_ANDROID)
    configure_file(
        ${CMAKE_CURRENT_SOURCE_DIR}/scripts/build-android.sh.in
        ${CMAKE_CURRENT_BINARY_DIR}/build-android.sh
        @ONLY
    )
endif()