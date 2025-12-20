# 🗄️ 数据库技术速记

## 📊 数据库分类与对比

### 🏗️ 数据库类型

| 类型 | 特点 | 适用场景 | 代表产品 |
|:---|:---|:---|:---|
| **关系型数据库 (RDBMS)** | ACID事务、SQL查询、表结构 | 传统业务系统 | MySQL、PostgreSQL、Oracle |
| **文档数据库** | JSON文档存储、灵活结构 | 内容管理、目录服务 | MongoDB、CouchDB |
| **键值数据库** | 简单KV存储、高性能 | 缓存、会话存储 | Redis、DynamoDB |
| **列族数据库** | 列式存储、大数据分析 | 数据仓库、日志分析 | HBase、Cassandra |
| **图数据库** | 图结构、关系查询 | 社交网络、推荐系统 | Neo4j、ArangoDB |
| **时序数据库** | 时间序列优化 | 监控、IoT数据 | InfluxDB、TimescaleDB |

### 📋 CAP定理与选择

| 特性 | 说明 | 优先选择 |
|:---|:---|:---|
| **一致性 (Consistency)** | 所有节点同时看到相同数据 | 金融、交易系统 |
| **可用性 (Availability)** | 系统持续可用 | 社交媒体、内容分发 |
| **分区容错 (Partition Tolerance)** | 网络分区时系统继续工作 | 分布式系统必选 |

---

## 🐬 MySQL 详解

### 🏗️ 存储引擎对比

| 引擎 | 事务支持 | 锁级别 | 外键 | 适用场景 |
|:---|:---|:---|:---|:---|
| **InnoDB** | ✅ | 行级锁 | ✅ | OLTP、高并发 |
| **MyISAM** | ❌ | 表级锁 | ❌ | 读多写少、数据仓库 |
| **Memory** | ❌ | 表级锁 | ❌ | 临时表、缓存 |
| **Archive** | ❌ | 行级锁 | ❌ | 归档、压缩存储 |

### 🔧 核心特性

#### 索引类型
```sql
-- 主键索引
ALTER TABLE users ADD PRIMARY KEY (id);

-- 唯一索引
CREATE UNIQUE INDEX idx_email ON users (email);

-- 普通索引
CREATE INDEX idx_name ON users (name);

-- 复合索引
CREATE INDEX idx_name_age ON users (name, age);

-- 全文索引
CREATE FULLTEXT INDEX idx_content ON articles (content);

-- 空间索引
CREATE SPATIAL INDEX idx_location ON places (coordinates);
```

#### 事务与锁
```sql
-- 事务隔离级别
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;

-- 显式锁
SELECT * FROM users WHERE id = 1 FOR UPDATE;  -- 排他锁
SELECT * FROM users WHERE id = 1 LOCK IN SHARE MODE;  -- 共享锁

-- 事务处理
START TRANSACTION;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;
```

#### 性能优化
```sql
-- 查询分析
EXPLAIN SELECT * FROM users WHERE name = 'John';
EXPLAIN FORMAT=JSON SELECT * FROM users WHERE name = 'John';

-- 索引优化
ANALYZE TABLE users;
OPTIMIZE TABLE users;

-- 慢查询分析
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;
```

### ⚙️ 配置优化
```ini
# my.cnf配置示例
[mysqld]
# 内存配置
innodb_buffer_pool_size = 2G        # 缓冲池大小
innodb_log_buffer_size = 64M         # 日志缓冲区
query_cache_size = 128M              # 查询缓存

# 连接配置
max_connections = 1000               # 最大连接数
max_connect_errors = 10              # 最大连接错误

# InnoDB配置
innodb_file_per_table = 1           # 独立表空间
innodb_flush_log_at_trx_commit = 2  # 日志刷盘策略
innodb_lock_wait_timeout = 50       # 锁等待超时
```

---

## 🐘 PostgreSQL 详解

### 🌟 高级特性

#### 数据类型
```sql
-- JSON类型
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL
);

INSERT INTO products (data) VALUES 
('{"name": "iPhone", "price": 999, "tags": ["phone", "apple"]}');

-- 查询JSON
SELECT data->>'name' AS name FROM products;
SELECT * FROM products WHERE data @> '{"tags": ["phone"]}';

-- 数组类型
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50),
    aliases TEXT[]
);

INSERT INTO tags (name, aliases) VALUES 
('Python', ARRAY['py', 'python3']);

-- 查询数组
SELECT * FROM tags WHERE 'py' = ANY(aliases);
```

#### 扩展功能
```sql
-- 全文搜索
CREATE INDEX idx_fts ON documents USING gin(to_tsvector('english', content));
SELECT * FROM documents 
WHERE to_tsvector('english', content) @@ to_tsquery('english', 'search & query');

-- 地理信息系统 (PostGIS)
CREATE EXTENSION postgis;
CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    geom GEOMETRY(POINT, 4326)
);

-- 分区表
CREATE TABLE sales (
    id SERIAL,
    sale_date DATE,
    amount DECIMAL(10,2)
) PARTITION BY RANGE (sale_date);

CREATE TABLE sales_2023 PARTITION OF sales
FOR VALUES FROM ('2023-01-01') TO ('2024-01-01');
```

---

## 🍃 MongoDB 详解

### 📊 文档数据库特性

#### 基础操作
```javascript
// 插入文档
db.users.insertOne({
    name: "John Doe",
    email: "john@example.com",
    age: 30,
    hobbies: ["reading", "swimming"],
    address: {
        street: "123 Main St",
        city: "New York",
        country: "USA"
    }
});

// 查询文档
db.users.find({age: {$gte: 25}});
db.users.find({"address.city": "New York"});
db.users.find({hobbies: {$in: ["reading", "coding"]}});

// 更新文档
db.users.updateOne(
    {email: "john@example.com"},
    {$set: {age: 31}, $push: {hobbies: "cooking"}}
);

// 聚合查询
db.users.aggregate([
    {$match: {age: {$gte: 25}}},
    {$group: {_id: "$address.city", count: {$sum: 1}}},
    {$sort: {count: -1}}
]);
```

#### 索引与性能
```javascript
// 创建索引
db.users.createIndex({email: 1});                    // 单字段索引
db.users.createIndex({name: 1, age: -1});           // 复合索引
db.users.createIndex({name: "text"});               // 文本索引
db.users.createIndex({"address.location": "2dsphere"}); // 地理索引

// 分析查询
db.users.find({name: "John"}).explain("executionStats");

// 优化建议
db.users.getIndexes();
db.stats();
```

#### 复制集与分片
```javascript
// 复制集配置
rs.initiate({
    _id: "myReplicaSet",
    members: [
        {_id: 0, host: "localhost:27017"},
        {_id: 1, host: "localhost:27018"},
        {_id: 2, host: "localhost:27019"}
    ]
});

// 分片配置
sh.enableSharding("mydb");
sh.shardCollection("mydb.users", {_id: "hashed"});
```

---

## ⚡ Redis 高级特性

### 🔧 数据结构详解

#### String 操作
```redis
SET user:1001 "John Doe"
GET user:1001
INCR page_views
INCRBY score 10
SETEX session:abc123 3600 "session_data"  # 设置过期时间
```

#### Hash 操作
```redis
HSET user:1001 name "John" age 30 email "john@example.com"
HGET user:1001 name
HGETALL user:1001
HINCRBY user:1001 age 1
```

#### List 操作
```redis
LPUSH tasks "task1" "task2" "task3"
RPOP tasks
LRANGE tasks 0 -1
LTRIM tasks 0 99  # 保留前100个元素
```

#### Set 操作
```redis
SADD tags:python "web" "backend" "scripting"
SINTER tags:python tags:web     # 交集
SUNION tags:python tags:java    # 并集
SDIFF tags:python tags:java     # 差集
```

#### Sorted Set 操作
```redis
ZADD leaderboard 1000 "player1" 1500 "player2" 800 "player3"
ZREVRANGE leaderboard 0 9 WITHSCORES  # 排行榜前10
ZINCRBY leaderboard 100 "player1"     # 增加分数
```

### 🚀 高级功能

#### 发布订阅
```redis
# 发布者
PUBLISH news "Breaking news!"

# 订阅者
SUBSCRIBE news
PSUBSCRIBE news:*  # 模式订阅
```

#### Lua脚本
```redis
# 原子性操作
EVAL "
    local current = redis.call('GET', KEYS[1])
    if current == false then
        return redis.call('SET', KEYS[1], ARGV[1])
    else
        return current
    end
" 1 mykey myvalue
```

#### 流处理
```redis
# 添加消息到流
XADD mystream * sensor-id 1234 temperature 19.8

# 读取消息
XREAD COUNT 2 STREAMS mystream 0

# 创建消费者组
XGROUP CREATE mystream mygroup $ MKSTREAM
XREADGROUP GROUP mygroup myconsumer COUNT 1 STREAMS mystream >
```

---

## 📈 时序数据库 InfluxDB

### 🕐 时序数据特点
- **时间戳**: 每条记录都有时间戳
- **标签**: 索引字段，用于分组和过滤
- **字段**: 实际的数值数据
- **保留策略**: 自动删除旧数据

### 🔧 基础操作
```sql
-- 写入数据
INSERT cpu,host=server01,region=us-west value=0.64

-- 查询数据
SELECT mean(value) FROM cpu 
WHERE time >= now() - 1h 
GROUP BY time(5m), host

-- 创建保留策略
CREATE RETENTION POLICY "one_week" ON "mydb" 
DURATION 1w REPLICATION 1 DEFAULT

-- 连续查询
CREATE CONTINUOUS QUERY "cq_mean" ON "mydb"
BEGIN
    SELECT mean(value) INTO "average" FROM "cpu" 
    GROUP BY time(1h)
END
```

---

## 🎯 数据库设计原则

### 📋 关系型数据库设计

#### 范式化设计
```sql
-- 第一范式：原子性
-- 错误示例
CREATE TABLE users (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    phones VARCHAR(200)  -- 存储多个电话号码
);

-- 正确示例
CREATE TABLE users (
    id INT PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE user_phones (
    id INT PRIMARY KEY,
    user_id INT,
    phone VARCHAR(20),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 第三范式：消除传递依赖
-- 错误示例
CREATE TABLE orders (
    id INT PRIMARY KEY,
    customer_id INT,
    customer_name VARCHAR(100),  -- 依赖于customer_id
    customer_city VARCHAR(50)    -- 依赖于customer_id
);

-- 正确示例
CREATE TABLE customers (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    city VARCHAR(50)
);

CREATE TABLE orders (
    id INT PRIMARY KEY,
    customer_id INT,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);
```

#### 索引设计原则
```sql
-- 1. 选择性高的列建索引
CREATE INDEX idx_email ON users (email);  -- 邮箱唯一性高

-- 2. 复合索引最左前缀
CREATE INDEX idx_name_age_city ON users (name, age, city);
-- 可以使用: (name), (name, age), (name, age, city)
-- 不能使用: (age), (city), (age, city)

-- 3. 覆盖索引
CREATE INDEX idx_cover ON users (name, age, email);
SELECT name, age, email FROM users WHERE name = 'John';  -- 覆盖索引

-- 4. 避免在索引列使用函数
-- 错误
SELECT * FROM users WHERE UPPER(name) = 'JOHN';
-- 正确  
CREATE INDEX idx_name_upper ON users ((UPPER(name)));
```

---

## 🎯 常见面试题及答案

### Q1: MySQL和PostgreSQL的主要区别？
**A**: 
- **ACID支持**: PostgreSQL完全符合ACID，MySQL InnoDB部分支持
- **并发控制**: PostgreSQL使用MVCC，MySQL使用锁+MVCC
- **数据类型**: PostgreSQL支持更丰富的数据类型(JSON、数组、自定义类型)
- **扩展性**: PostgreSQL可扩展性更强，支持自定义函数和操作符
- **性能**: MySQL读性能较好，PostgreSQL复杂查询性能更优

### Q2: 如何优化数据库查询性能？
**A**: 
1. **索引优化**: 为WHERE、ORDER BY、JOIN字段建索引
2. **查询优化**: 避免SELECT *，使用LIMIT限制结果
3. **结构优化**: 适当反范式化，分区表
4. **配置优化**: 调整缓冲池、连接数等参数
5. **硬件优化**: SSD存储、增加内存

### Q3: 什么是数据库事务的ACID特性？
**A**: 
- **原子性 (Atomicity)**: 事务要么全部成功，要么全部回滚
- **一致性 (Consistency)**: 事务前后数据完整性约束不被破坏
- **隔离性 (Isolation)**: 并发事务互不干扰
- **持久性 (Durability)**: 已提交事务的结果永久保存

### Q4: 解释数据库的隔离级别？
**A**: 
- **READ UNCOMMITTED**: 读未提交，可能脏读
- **READ COMMITTED**: 读已提交，避免脏读但可能不可重复读
- **REPEATABLE READ**: 可重复读，避免脏读和不可重复读
- **SERIALIZABLE**: 串行化，最高隔离级别，避免所有并发问题

### Q5: NoSQL和关系型数据库如何选择？
**A**: 
选择关系型数据库：
- 需要强一致性和事务支持
- 复杂查询和报表需求
- 数据结构稳定

选择NoSQL：
- 大规模数据和高并发
- 数据结构灵活多变
- 水平扩展需求

### Q6: 如何设计数据库分库分表？
**A**: 
1. **垂直分库**: 按业务模块分离不同数据库
2. **水平分库**: 按分片键将数据分散到多个数据库
3. **垂直分表**: 将大表按列拆分为多个表
4. **水平分表**: 按行将大表拆分为多个小表

### Q7: Redis持久化方式的区别？
**A**: 
- **RDB**: 快照持久化，文件小恢复快，但可能丢失数据
- **AOF**: 日志持久化，数据安全但文件大恢复慢
- **混合持久化**: RDB+AOF，兼顾性能和安全性

### Q8: 如何处理数据库死锁？
**A**: 
1. **预防**: 统一加锁顺序，减少锁持有时间
2. **检测**: 数据库自动检测死锁环路
3. **解决**: 回滚代价最小的事务
4. **避免**: 使用适当的隔离级别，优化SQL

### Q9: 什么是数据库连接池？为什么需要？
**A**: 
连接池维护一定数量的数据库连接供应用重复使用。

优势：
- 减少连接创建/销毁开销
- 控制并发连接数
- 提高应用性能
- 更好的资源管理

### Q10: 如何保证分布式数据库的一致性？
**A**: 
1. **2PC (两阶段提交)**: 强一致性但性能差
2. **3PC (三阶段提交)**: 改进2PC的阻塞问题
3. **Raft/Paxos**: 分布式共识算法
4. **最终一致性**: 通过异步复制实现
5. **SAGA模式**: 长事务的分布式处理

### Q11: Hive/MySQL/ES 索引的区别？
**A**:
- **MySQL (InnoDB)**: 使用 **B+树** 索引，适合精确查找和范围查询。数据和索引紧密耦合，主键是聚簇索引，叶子节点直接存储数据行。
- **Hive**: 本质上没有传统意义的索引，依赖 **分区(Partition)** 和 **分桶(Bucket)** 进行数据筛选，核心是HDFS上的全量或大量数据扫描。新版本支持了一些基本索引（如Bitmap），但不是主要查询方式。
- **Elasticsearch**: 使用 **倒排索引(Inverted Index)**，专为全文搜索设计。将文本分词，建立词元到文档的映射，实现快速的文本检索。对数值和地理位置数据使用BKD树。

### Q12: 数据库连接池获取不到连接的可能性分析？
**A**:
1.  **连接泄露 (Connection Leak)**: 应用从连接池借用连接后，在`finally`块或异常路径中没有归还，导致连接池耗尽。
2.  **连接池��置过小**: `maximum-pool-size` 对于应用并发量来说太小，导致请求需要长时间等待。
3.  **数据库或网络问题**: 数据库本身宕机、响应缓慢，或网络不稳定，导致连接池无法创建或验证新连接，请求超时。
4.  **事务未提交**: 长时间运行的事务或死锁占用了连接，没有及时释放。
5.  **配置不当**: `idleTimeout` 或 `maxLifetime` 设置不合理，例如，防火墙在连接池回收空闲连接前就将其关闭了，导致池中存在失效连接。
