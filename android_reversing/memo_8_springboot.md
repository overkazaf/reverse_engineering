# 🍃 Spring Boot 技术速记

## 🚀 Spring Boot 核心概念

### 📊 核心特性

| 特性 | 说明 | 优势 |
|:---|:---|:---|
| **自动配置** | 基于类路径自动配置Bean | 减少配置代码 |
| **起步依赖** | 预定义依赖组合 | 简化依赖管理 |
| **嵌入式容器** | 内置Tomcat/Jetty/Undertow | 独立运行 |
| **生产就绪** | 健康检查、监控、外部配置 | 企业级特性 |
| **无代码生成** | 纯Java配置 | 透明可控 |

### 🏗️ 核心架构
```
Spring Boot Application
    ↓
Spring Boot Starter
    ↓
Spring Boot AutoConfiguration
    ↓
Spring Framework (IoC, AOP, etc.)
```

---

## 🔧 快速开始

### 📋 项目结构
```
src/
├── main/
│   ├── java/
│   │   └── com/example/demo/
│   │       ├── DemoApplication.java
│   │       ├── controller/
│   │       ├── service/
│   │       ├── repository/
│   │       └── model/
│   └── resources/
│       ├── application.yml
│       ├── static/
│       └── templates/
└── test/
    └── java/
```

### 🚀 主启动类
```java
@SpringBootApplication
public class DemoApplication {
    public static void main(String[] args) {
        SpringApplication.run(DemoApplication.class, args);
    }
}

// @SpringBootApplication 包含:
// @Configuration + @EnableAutoConfiguration + @ComponentScan
```

### 📦 基础依赖
```xml
<parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>2.7.0</version>
</parent>

<dependencies>
    <!-- Web开发 -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    
    <!-- 数据访问 -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-data-jpa</artifactId>
    </dependency>
    
    <!-- 测试 -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-test</artifactId>
        <scope>test</scope>
    </dependency>
</dependencies>
```

---

## 🌐 Web 开发

### 🎯 RESTful API
```java
@RestController
@RequestMapping("/api/users")
public class UserController {
    
    @Autowired
    private UserService userService;
    
    @GetMapping
    public ResponseEntity<List<User>> getAllUsers() {
        List<User> users = userService.findAll();
        return ResponseEntity.ok(users);
    }
    
    @GetMapping("/{id}")
    public ResponseEntity<User> getUserById(@PathVariable Long id) {
        User user = userService.findById(id);
        return user != null ? ResponseEntity.ok(user) : ResponseEntity.notFound().build();
    }
    
    @PostMapping
    public ResponseEntity<User> createUser(@RequestBody @Valid User user) {
        User savedUser = userService.save(user);
        return ResponseEntity.status(HttpStatus.CREATED).body(savedUser);
    }
    
    @PutMapping("/{id}")
    public ResponseEntity<User> updateUser(@PathVariable Long id, @RequestBody @Valid User user) {
        User updatedUser = userService.update(id, user);
        return ResponseEntity.ok(updatedUser);
    }
    
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteUser(@PathVariable Long id) {
        userService.deleteById(id);
        return ResponseEntity.noContent().build();
    }
}
```

### 🔍 请求处理
```java
@RestController
public class RequestController {
    
    // 路径参数
    @GetMapping("/users/{id}/posts/{postId}")
    public String getPost(@PathVariable Long id, @PathVariable Long postId) {
        return "User: " + id + ", Post: " + postId;
    }
    
    // 查询参数
    @GetMapping("/search")
    public String search(@RequestParam String keyword, 
                        @RequestParam(defaultValue = "10") int size) {
        return "Search: " + keyword + ", Size: " + size;
    }
    
    // 请求头
    @GetMapping("/header")
    public String getHeader(@RequestHeader("User-Agent") String userAgent) {
        return "User-Agent: " + userAgent;
    }
    
    // 文件上传
    @PostMapping("/upload")
    public String uploadFile(@RequestParam("file") MultipartFile file) {
        if (!file.isEmpty()) {
            // 处理文件上传
            return "File uploaded: " + file.getOriginalFilename();
        }
        return "File upload failed";
    }
}
```

### 📋 数据验证
```java
@Entity
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @NotBlank(message = "用户名不能为空")
    @Size(min = 3, max = 20, message = "用户名长度必须在3-20之间")
    private String username;
    
    @Email(message = "邮箱格式不正确")
    @NotBlank(message = "邮箱不能为空")
    private String email;
    
    @NotNull(message = "年龄不能为空")
    @Min(value = 18, message = "年龄不能小于18")
    @Max(value = 100, message = "年龄不能大于100")
    private Integer age;
    
    // getters and setters
}

// 全局异常处理
@ControllerAdvice
public class GlobalExceptionHandler {
    
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<Map<String, String>> handleValidationExceptions(
            MethodArgumentNotValidException ex) {
        Map<String, String> errors = new HashMap<>();
        ex.getBindingResult().getAllErrors().forEach((error) -> {
            String fieldName = ((FieldError) error).getField();
            String errorMessage = error.getDefaultMessage();
            errors.put(fieldName, errorMessage);
        });
        return ResponseEntity.badRequest().body(errors);
    }
}
```

---

## 🗄️ 数据访问

### 📊 JPA Repository
```java
@Entity
@Table(name = "users")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(unique = true)
    private String username;
    
    private String email;
    private Integer age;
    
    @CreationTimestamp
    private LocalDateTime createdAt;
    
    @UpdateTimestamp
    private LocalDateTime updatedAt;
    
    // constructors, getters, setters
}

// Repository接口
@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    
    // 方法名查询
    Optional<User> findByUsername(String username);
    List<User> findByAgeGreaterThan(Integer age);
    List<User> findByUsernameContainingIgnoreCase(String username);
    
    // @Query注解
    @Query("SELECT u FROM User u WHERE u.email = ?1")
    Optional<User> findByEmail(String email);
    
    @Query(value = "SELECT * FROM users WHERE age BETWEEN ?1 AND ?2", nativeQuery = true)
    List<User> findByAgeBetween(Integer minAge, Integer maxAge);
    
    // 自定义更新
    @Modifying
    @Query("UPDATE User u SET u.email = ?2 WHERE u.id = ?1")
    int updateEmailById(Long id, String email);
    
    // 分页查询
    Page<User> findByAgeGreaterThan(Integer age, Pageable pageable);
}
```

### 🔧 数据库配置
```yaml
# application.yml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/mydb?useSSL=false&allowPublicKeyRetrieval=true
    username: root
    password: password
    driver-class-name: com.mysql.cj.jdbc.Driver
    
  jpa:
    hibernate:
      ddl-auto: update
    show-sql: true
    properties:
      hibernate:
        dialect: org.hibernate.dialect.MySQL8Dialect
        format_sql: true
        
  # 连接池配置
  datasource:
    hikari:
      maximum-pool-size: 20
      minimum-idle: 5
      connection-timeout: 30000
      idle-timeout: 300000
      max-lifetime: 1800000
```

### 📈 多数据源配置
```java
@Configuration
public class DataSourceConfig {
    
    @Primary
    @Bean(name = "primaryDataSource")
    @ConfigurationProperties(prefix = "spring.datasource.primary")
    public DataSource primaryDataSource() {
        return DataSourceBuilder.create().build();
    }
    
    @Bean(name = "secondaryDataSource")
    @ConfigurationProperties(prefix = "spring.datasource.secondary")
    public DataSource secondaryDataSource() {
        return DataSourceBuilder.create().build();
    }
    
    @Primary
    @Bean(name = "primaryEntityManagerFactory")
    public LocalContainerEntityManagerFactoryBean primaryEntityManagerFactory(
            EntityManagerFactoryBuilder builder,
            @Qualifier("primaryDataSource") DataSource dataSource) {
        return builder
                .dataSource(dataSource)
                .packages("com.example.primary.entity")
                .persistenceUnit("primary")
                .build();
    }
}
```

---

## 🔧 自动配置

### ⚙️ 自定义配置类
```java
@ConfigurationProperties(prefix = "app")
@Component
public class AppProperties {
    private String name;
    private String version;
    private Security security = new Security();
    
    public static class Security {
        private boolean enabled = true;
        private String secretKey;
        
        // getters and setters
    }
    
    // getters and setters
}

// 使用配置
@Service
public class AppService {
    
    @Autowired
    private AppProperties appProperties;
    
    public void doSomething() {
        if (appProperties.getSecurity().isEnabled()) {
            // 执行安全相关逻辑
        }
    }
}
```

### 🎯 条件化配置
```java
@Configuration
public class ConditionalConfig {
    
    @Bean
    @ConditionalOnProperty(name = "app.feature.enabled", havingValue = "true")
    public FeatureService featureService() {
        return new FeatureServiceImpl();
    }
    
    @Bean
    @ConditionalOnMissingBean(FeatureService.class)
    public FeatureService defaultFeatureService() {
        return new DefaultFeatureServiceImpl();
    }
    
    @Bean
    @ConditionalOnClass(RedisTemplate.class)
    public CacheService redisCacheService() {
        return new RedisCacheService();
    }
    
    @Bean
    @ConditionalOnMissingClass("org.springframework.data.redis.core.RedisTemplate")
    public CacheService memoryCacheService() {
        return new MemoryCacheService();
    }
}
```

---

## 🛡️ 安全配置

### 🔐 Spring Security
```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {
    
    @Autowired
    private JwtAuthenticationEntryPoint jwtAuthenticationEntryPoint;
    
    @Autowired
    private JwtRequestFilter jwtRequestFilter;
    
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
    
    @Bean
    public AuthenticationManager authenticationManager(
            AuthenticationConfiguration config) throws Exception {
        return config.getAuthenticationManager();
    }
    
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http.csrf().disable()
            .authorizeHttpRequests((authz) -> authz
                .requestMatchers("/api/auth/**").permitAll()
                .requestMatchers("/api/public/**").permitAll()
                .requestMatchers(HttpMethod.GET, "/api/posts/**").permitAll()
                .requestMatchers("/api/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated()
            )
            .exceptionHandling().authenticationEntryPoint(jwtAuthenticationEntryPoint)
            .and()
            .sessionManagement().sessionCreationPolicy(SessionCreationPolicy.STATELESS);
            
        http.addFilterBefore(jwtRequestFilter, UsernamePasswordAuthenticationFilter.class);
        
        return http.build();
    }
}
```

### 🔑 JWT 实现
```java
@Component
public class JwtUtil {
    
    private String secret = "mySecretKey";
    private int jwtExpirationInMs = 86400000; // 24小时
    
    public String generateToken(UserDetails userDetails) {
        Map<String, Object> claims = new HashMap<>();
        return createToken(claims, userDetails.getUsername());
    }
    
    private String createToken(Map<String, Object> claims, String subject) {
        return Jwts.builder()
                .setClaims(claims)
                .setSubject(subject)
                .setIssuedAt(new Date(System.currentTimeMillis()))
                .setExpiration(new Date(System.currentTimeMillis() + jwtExpirationInMs))
                .signWith(SignatureAlgorithm.HS512, secret)
                .compact();
    }
    
    public Boolean validateToken(String token, UserDetails userDetails) {
        final String username = getUsernameFromToken(token);
        return (username.equals(userDetails.getUsername()) && !isTokenExpired(token));
    }
    
    public String getUsernameFromToken(String token) {
        return getClaimFromToken(token, Claims::getSubject);
    }
    
    public Date getExpirationDateFromToken(String token) {
        return getClaimFromToken(token, Claims::getExpiration);
    }
    
    public <T> T getClaimFromToken(String token, Function<Claims, T> claimsResolver) {
        final Claims claims = getAllClaimsFromToken(token);
        return claimsResolver.apply(claims);
    }
    
    private Claims getAllClaimsFromToken(String token) {
        return Jwts.parser().setSigningKey(secret).parseClaimsJws(token).getBody();
    }
    
    private Boolean isTokenExpired(String token) {
        final Date expiration = getExpirationDateFromToken(token);
        return expiration.before(new Date());
    }
}
```

---

## 📊 监控与管理

### 🔍 Actuator 配置
```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus,env
  endpoint:
    health:
      show-details: always
  metrics:
    export:
      prometheus:
        enabled: true
  info:
    env:
      enabled: true
```

### 🎯 自定义健康检查
```java
@Component
public class CustomHealthIndicator implements HealthIndicator {
    
    @Override
    public Health health() {
        try {
            // 执行健康检查逻辑
            boolean isHealthy = checkExternalService();
            
            if (isHealthy) {
                return Health.up()
                        .withDetail("status", "Service is running")
                        .withDetail("timestamp", System.currentTimeMillis())
                        .build();
            } else {
                return Health.down()
                        .withDetail("status", "Service is not available")
                        .build();
            }
        } catch (Exception e) {
            return Health.down()
                    .withDetail("error", e.getMessage())
                    .build();
        }
    }
    
    private boolean checkExternalService() {
        // 实际的健康检查逻辑
        return true;
    }
}
```

### 📈 自定义指标
```java
@RestController
public class MetricsController {
    
    private final MeterRegistry meterRegistry;
    private final Counter requestCounter;
    private final Timer requestTimer;
    
    public MetricsController(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;
        this.requestCounter = Counter.builder("api.requests.total")
                .description("Total API requests")
                .register(meterRegistry);
        this.requestTimer = Timer.builder("api.requests.duration")
                .description("API request duration")
                .register(meterRegistry);
    }
    
    @GetMapping("/api/data")
    public ResponseEntity<String> getData() {
        return Timer.Sample.start(meterRegistry)
                .stop(requestTimer)
                .recordCallable(() -> {
                    requestCounter.increment();
                    // 业务逻辑
                    return ResponseEntity.ok("Data");
                });
    }
}
```

---

## 🧪 测试

### 🔧 单元测试
```java
@SpringBootTest
class UserServiceTest {
    
    @MockBean
    private UserRepository userRepository;
    
    @Autowired
    private UserService userService;
    
    @Test
    void shouldCreateUser() {
        // Given
        User user = new User();
        user.setUsername("testuser");
        user.setEmail("test@example.com");
        
        User savedUser = new User();
        savedUser.setId(1L);
        savedUser.setUsername("testuser");
        savedUser.setEmail("test@example.com");
        
        when(userRepository.save(any(User.class))).thenReturn(savedUser);
        
        // When
        User result = userService.createUser(user);
        
        // Then
        assertThat(result.getId()).isEqualTo(1L);
        assertThat(result.getUsername()).isEqualTo("testuser");
        verify(userRepository).save(user);
    }
}
```

### 🌐 集成测试
```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
@Testcontainers
class UserControllerIntegrationTest {
    
    @Container
    static MySQLContainer<?> mysql = new MySQLContainer<>("mysql:8.0")
            .withDatabaseName("testdb")
            .withUsername("test")
            .withPassword("test");
    
    @Autowired
    private TestRestTemplate restTemplate;
    
    @Autowired
    private UserRepository userRepository;
    
    @Test
    void shouldCreateAndRetrieveUser() {
        // Given
        User user = new User();
        user.setUsername("testuser");
        user.setEmail("test@example.com");
        user.setAge(25);
        
        // When - Create user
        ResponseEntity<User> createResponse = restTemplate.postForEntity(
                "/api/users", user, User.class);
        
        // Then
        assertThat(createResponse.getStatusCode()).isEqualTo(HttpStatus.CREATED);
        assertThat(createResponse.getBody().getId()).isNotNull();
        
        // When - Get user
        ResponseEntity<User> getResponse = restTemplate.getForEntity(
                "/api/users/" + createResponse.getBody().getId(), User.class);
        
        // Then
        assertThat(getResponse.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(getResponse.getBody().getUsername()).isEqualTo("testuser");
    }
}
```

---

## 🎯 常见面试题及答案

### Q1: Spring Boot的自动配置原理？
**A**: 
1. **@EnableAutoConfiguration**: 启用自动配置
2. **spring.factories**: 加载自动配置类列表
3. **条件注解**: 根据条件决定是否生效(@ConditionalOnClass等)
4. **配置属性**: 通过@ConfigurationProperties绑定配置
5. **Bean注册**: 满足条件时注册相应的Bean

### Q2: Spring Boot Starter的作用？
**A**: 
- **依赖管理**: 预定义相关依赖的组合
- **自动配置**: 提供默认配置减少手动配置
- **版本管理**: 统一管理依赖版本避免冲突
- **最佳实践**: 提供经过验证的配置组合

### Q3: Spring Boot如何实现热部署？
**A**: 
1. **spring-boot-devtools**: 开发工具依赖
2. **类加载器**: 使用restart类加载器重启应用
3. **文件监听**: 监控classpath变化
4. **排除资源**: 配置不需要重启的资源
5. **IDE支持**: 配合IDE的自动编译功能

### Q4: Spring Boot的配置优先级？
**A**: 优先级从高到低：
1. 命令行参数
2. Java系统属性
3. 操作系统环境变量  
4. application-{profile}.properties
5. application.properties
6. @ConfigurationProperties注解

### Q5: 如何自定义Spring Boot Starter？
**A**: 
1. **创建模块**: 创建xxx-spring-boot-starter模块
2. **自动配置类**: 编写AutoConfiguration类
3. **配置属性**: 定义Properties类
4. **spring.factories**: 注册自动配置类
5. **条件注解**: 使用条件注解控制生效条件

### Q6: Spring Boot如何处理跨域问题？
**A**: 
```java
@Configuration
public class CorsConfig {
    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration configuration = new CorsConfiguration();
        configuration.setAllowedOriginPatterns(Arrays.asList("*"));
        configuration.setAllowedMethods(Arrays.asList("*"));
        configuration.setAllowedHeaders(Arrays.asList("*"));
        configuration.setAllowCredentials(true);
        
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", configuration);
        return source;
    }
}
```

### Q7: Spring Boot的异常处理机制？
**A**: 
1. **@ControllerAdvice**: 全局异常处理
2. **@ExceptionHandler**: 具体异常处理方法
3. **ErrorController**: 自定义错误页面
4. **响应状态码**: 设置合适的HTTP状态码
5. **错误信息**: 返回友好的错误信息

### Q8: Spring Boot如何集成Redis？
**A**: 
```java
@Configuration
public class RedisConfig {
    @Bean
    public RedisTemplate<String, Object> redisTemplate(RedisConnectionFactory factory) {
        RedisTemplate<String, Object> template = new RedisTemplate<>();
        template.setConnectionFactory(factory);
        template.setKeySerializer(new StringRedisSerializer());
        template.setValueSerializer(new GenericJackson2JsonRedisSerializer());
        return template;
    }
}
```

### Q9: Spring Boot的事务管理？
**A**: 
```java
@Service
@Transactional
public class UserService {
    
    @Transactional(rollbackFor = Exception.class)
    public void createUser(User user) {
        // 业务逻辑
    }
    
    @Transactional(readOnly = true)
    public User findUser(Long id) {
        return userRepository.findById(id);
    }
}
```

### Q10: Spring Boot性能优化建议？
**A**: 
1. **JVM调优**: 调整堆内存、GC参数
2. **连接池**: 配置数据库连接池参数
3. **缓存**: 使用Redis、本地缓存
4. **异步处理**: 使用@Async处理耗时操作
5. **监控**: 使用Actuator监控应用状态
6. **分页**: 大数据量查询使用分页
7. **索引**: 数据库查询优化索引

### Q11: 线程池的原理？
**A**:
Java线程池 (`ThreadPoolExecutor`) 的核心工作流程如下：
1.  **核心线程**: 当任务提交时，如果当前线程数小于 `corePoolSize`，则创建新线程处理任务。
2.  **任务队列**: 如果核心线程都在忙，新任务会被放入一个阻塞队列 (`BlockingQueue`) 等待。
3.  **最大线程**: 如果任务队列也满了，且当前线程数小于 `maximumPoolSize`，则创建新的非核心线程来处理任务。
4.  **拒绝策略**: 如果线程数已达最大值且队列已满，则执行拒绝策略 (`RejectedExecutionHandler`)，如抛出异常、丢弃任务等。
**核心优势**: 复用线程，减少创建销毁开销；控制并发数，防止资源耗尽。

### Q12: Spring Boot 中注解生效的原理？
**A**:
主要依赖 **Java反射** 和 **动态代理 (AOP)**，在Spring容器启动和Bean生命周期中实现：
1.  **启动阶段扫描**: Spring Boot启动时通过 `@ComponentScan` 扫描指定包下的类，利用反射检查类上的注解（如 `@Component`, `@Service`），将它们注册为Bean定义。
2.  **Bean生命周期处理**: 在Bean实例化和初始化的过程中，`BeanPostProcessor` (如 `AutowiredAnnotationBeanPostProcessor`) 会介入。它利用反射扫描Bean的字段和方法上的 `@Autowired` 等注解，并从容器中获取依赖的Bean进行注入。
3.  **AOP与代理**: 像 `@Transactional` 或自定义的 `@Aspect` 注解，Spring会为目标Bean创建一个代理对象（JDK动态代理或CGLIB）。当调用被注解的方法时，实际上是调用代理对象的方法，代理会在真实方法执行前后织入相应的逻辑（如开启/提交事务）。
4.  **`@Configuration`**: 被 `@Configuration` 注解的类也会被CGLIB代理，以确保通过方法调用获取 `@Bean` 时，返回的是容器中的单例实例。

---

## 🚀 进阶主题

### 异步处理
```java
@Configuration
@EnableAsync
public class AsyncConfig {
    @Bean
    public Executor taskExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(5);
        executor.setMaxPoolSize(10);
        executor.setQueueCapacity(25);
        executor.setThreadNamePrefix("Async-");
        executor.initialize();
        return executor;
    }
}

@Service
public class EmailService {
    @Async
    public void sendEmail(String to, String subject, String body) {
        // 发送邮件的耗时操作
    }
}
```

### 定时任务
```java
@Configuration
@EnableScheduling
public class SchedulingConfig {
}

@Component
public class ScheduledTasks {
    
    @Scheduled(fixedRate = 5000) // 每5秒执行一次
    public void reportCurrentTime() {
        // ...
    }
    
    @Scheduled(cron = "0 0 1 * * ?") // 每天凌晨1点执行
    public void cleanup() {
        // ...
    }
}
```

### WebSocket
```java
@Configuration
@EnableWebSocketMessageBroker
public class WebSocketConfig implements WebSocketMessageBrokerConfigurer {
    
    @Override
    public void configureMessageBroker(MessageBrokerRegistry config) {
        config.enableSimpleBroker("/topic");
        config.setApplicationDestinationPrefixes("/app");
    }
    
    @Override
    public void registerStompEndpoints(StompEndpointRegistry registry) {
        registry.addEndpoint("/ws").withSockJS();
    }
}

@Controller
public class GreetingController {
    
    @MessageMapping("/hello")
    @SendTo("/topic/greetings")
    public Greeting greeting(HelloMessage message) throws Exception {
        Thread.sleep(1000); // simulated delay
        return new Greeting("Hello, " + HtmlUtils.htmlEscape(message.getName()) + "!");
    }
}
```
