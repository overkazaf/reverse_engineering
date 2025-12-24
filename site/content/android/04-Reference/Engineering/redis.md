---
title: "Redis 常用命令备忘录"
date: 2025-12-25
weight: 10
---

# Redis 常用命令备忘录

Redis 是一个开源的、基于内存的、高性能的键值存储系统。它支持多种数据结构，如字符串、哈希、列表、集合和有序集合。本备忘录旨在提供常用命令的快速参考。

## 目录

1. [连接与服务器管理](#连接与服务器管理)
2. [键 (Key) 操作](#键-key-操作)
3. [字符串 (String)](#字符串-string)
4. [哈希 (Hash)](#哈希-hash)
5. [列表 (List)](#列表-list)
6. [集合 (Set)](#集合-set)
7. [有序集合 (Sorted Set / ZSet)](#有序集合-sorted-set--zset)
8. [Redis 架构演进](#redis-架构演进)
9. [Redis 集群详解](#redis-集群详解)
10. [布隆过滤器](#布隆过滤器)
11. [Stream 流数据结构](#stream-流数据结构)
12. [面试高频考点](#面试高频考点)

---

## 连接与服务器管理

| 命令 | 描述 |
|:-----|:-----|
| `redis-cli` | 启动 Redis 命令行客户端 |
| `redis-cli -h <host> -p <port> -a <password>` | 连接到指定的 Redis 实例 |
| `PING` | 测试服务器是否仍在运行，返回 `PONG` |
| `AUTH <password>` | 验证连接密码 |
| `SELECT <index>` | 选择数据库 (默认 0-15) |
| `FLUSHDB` | 清空当前数据库的所有键 |
| `FLUSHALL` | 清空所有数据库的所有键 |
| `INFO` | 获取服务器的信息和统计数据 |

---

## 键 (Key) 操作

| 命令 | 描述 |
|:-----|:-----|
| `KEYS <pattern>` | 查找所有符合给定模式的键 (如 `KEYS *`, `KEYS user:*`) **(慎用，会阻塞)** |
| `SCAN <cursor> [MATCH pattern] [COUNT count]` | 迭代数据库中的键，比 `KEYS` 更安全 |
| `EXISTS <key>` | 检查给定键是否存在 |
| `DEL <key> [key ...]` | 删除一个或多个键 |
| `TYPE <key>` | 返回键所存储的值的类型 (string, hash, list, set, zset) |
| `TTL <key>` | 以秒为单位，返回给定键的剩余生存时间 |
| `EXPIRE <key> <seconds>` | 为给定键设置生存时间 |
| `PERSIST <key>` | 移除给定键的生存时间，使其永久保存 |
| `RENAME <key> <newkey>` | 修改键的名称 |

---

## 字符串 (String)

字符串是 Redis 最基本的数据类型，可以存储任何类型的数据，如文本、序列化的 JSON 或二进制数据。

| 命令 | 描述 |
|:-----|:-----|
| `SET <key> <value>` | 设置指定键的值 |
| `GET <key>` | 获取指定键的值 |
| `SETEX <key> <seconds> <value>` | 设置键值对并指定过期时间 |
| `SETNX <key> <value>` | 只有在键不存在时才设置键的值 |
| `MSET <key1> <value1> [key2 value2 ...]` | 同时设置一个或多个键值对 |
| `MGET <key1> [key2 ...]` | 获取所有给定键的值 |
| `INCR <key>` | 将键中储存的数字值增一 (原子操作) |
| `DECR <key>` | 将键中储存的数字值减一 (原子操作) |
| `INCRBY <key> <increment>` | 将键所储存的值加上指定的增量值 |

---

## 哈希 (Hash)

哈希是一个键值对的集合，非常适合用于存储对象。

| 命令 | 描述 |
|:-----|:-----|
| `HSET <key> <field> <value>` | 将哈希表中字段的值设为 value |
| `HGET <key> <field>` | 获取存储在哈希表中指定字段的值 |
| `HMSET <key> <f1> <v1> [f2 v2 ...]` | 同时将多个 field-value 对设置到哈希表中 |
| `HMGET <key> <field1> [field2 ...]` | 获取所有给定字段的值 |
| `HGETALL <key>` | 获取在哈希表中指定键的所有字段和值 |
| `HKEYS <key>` | 获取哈希表中的所有字段 |
| `HVALS <key>` | 获取哈希表中的所有值 |
| `HDEL <key> <field1> [field2 ...]` | 删除一个或多个哈希表字段 |
| `HEXISTS <key> <field>` | 查看哈希表的指定字段是否存在 |

---

## 列表 (List)

列表是简单的字符串列表，按照插入顺序排序。你可以添加一个元素到列表的头部（左边）或者尾部（右边）。

| 命令 | 描述 |
|:-----|:-----|
| `LPUSH <key> <value1> [value2 ...]` | 将一个或多个值插入到列表头部 |
| `RPUSH <key> <value1> [value2 ...]` | 将一个或多个值插入到列表尾部 |
| `LPOP <key>` | 移出并获取列表的第一个元素 |
| `RPOP <key>` | 移出并获取列表的最后一个元素 |
| `LLEN <key>` | 获取列表的长度 |
| `LRANGE <key> <start> <stop>` | 获取列表指定范围内的元素 |
| `LINDEX <key> <index>` | 通过索引获取列表中的元素 |
| `LSET <key> <index> <value>` | 通过索引设置列表元素的值 |
| `LTRIM <key> <start> <stop>` | 对列表进行修剪，只保留指定区间内的元素 |

---

## 集合 (Set)

集合是字符串类型的**无序**集合。集合成员是唯一的，不能出现重复的数据。

| 命令 | 描述 |
|:-----|:-----|
| `SADD <key> <member1> [member2 ...]` | 向集合添加一个或多个成员 |
| `SMEMBERS <key>` | 返回集合中的所有成员 |
| `SISMEMBER <key> <member>` | 判断 member 元素是否是集合的成员 |
| `SCARD <key>` | 获取集合的成员数 |
| `SREM <key> <member1> [member2 ...]` | 移除集合中一个或多个成员 |
| `SPOP <key> [count]` | 随机移除并返回集合中一个或多个成员 |
| `SUNION <key1> [key2 ...]` | 返回所有给定集合的并集 |
| `SINTER <key1> [key2 ...]` | 返回所有给定集合的交集 |
| `SDIFF <key1> [key2 ...]` | 返回所有给定集合的差集 |

---

## 有序集合 (Sorted Set / ZSet)

有序集合和集合一样是字符串类型元素的集合，且不允许重复的成员。不同的是每个元素都会关联一个 `double` 类型的**分数 (score)**。

| 命令 | 描述 |
|:-----|:-----|
| `ZADD <key> <score1> <member1> [...]` | 向有序集合添加一个或多个成员 |
| `ZRANGE <key> <start> <stop> [WITHSCORES]` | 通过索引区间返回成员 (分数递增) |
| `ZREVRANGE <key> <start> <stop> [WITHSCORES]` | 返回指定区间内的成员 (分数递减) |
| `ZRANGEBYSCORE <key> <min> <max>` | 通过分数返回指定区间内的成员 |
| `ZCARD <key>` | 获取有序集合的成员数 |
| `ZSCORE <key> <member>` | 返回成员的 score 值 |
| `ZREM <key> <member1> [member2 ...]` | 移除一个或多个成员 |
| `ZCOUNT <key> <min> <max>` | 计算指定分数区间的成员数 |

---

## Redis 架构演进

### 版本发展

| 版本 | 发布时间 | 主要特性 |
|:-----|:---------|:---------|
| Redis 1.0 | 2009 年 | 基础键值存储，5 种基本数据结构 |
| Redis 2.0 | 2010 年 | 引入虚拟内存、发布订阅 |
| Redis 2.6 | 2012 年 | Lua 脚本支持、过期键处理优化 |
| Redis 2.8 | 2013 年 | 部分重同步、Sentinel 高可用 |
| Redis 3.0 | 2015 年 | **Redis Cluster 集群支持** |
| Redis 4.0 | 2017 年 | 模块系统、内存优化、混合持久化 |
| Redis 5.0 | 2018 年 | **Stream 数据结构**、动态 HZ |
| Redis 6.0 | 2020 年 | 多线程 I/O、ACL 权限控制、SSL |
| Redis 7.0 | 2022 年 | Redis Functions、多 ACL 用户 |

### 架构演进路径

#### 1. 单机模式 (Single Instance)

最简单的部署方式，适合开发和测试环境。

#### 2. 主从复制 (Master-Slave)

数据异步复制到从节点，提供读写分离能力。

#### 3. Sentinel 高可用 (Redis Sentinel)

监控主从节点，自动进行故障转移。

#### 4. 集群模式 (Redis Cluster)

数据分片存储，支持水平扩展。

### 脑裂问题 (Split-Brain)

**定义**: 脑裂是指在分布式系统中，由于网络分区或节点故障，导致系统中出现多个"大脑"（多个节点都认为自己是主节点）的情况。

**Redis 中的脑裂场景**:

```
网络分区前:
Sentinel1,2,3 ←→ Master ←→ Slave1,2

网络分区后:
PartitionA: Sentinel1 ←→ Master (原主节点)
PartitionB: Sentinel2,3 ←→ Slave1 ←→ Slave2 (选举新主节点)
```

**Redis 脑裂预防机制**:

1. **Sentinel 奇数部署**: 确保故障转移时有明确的多数派
    ```bash
    # 推荐配置：至少 3 个 Sentinel
    Sentinel1, Sentinel2, Sentinel3
    ```
2. **配置写入限制**:
    ```bash
    # 至少需要 2 个 Slave 节点，最大延迟 10 秒
    min-slaves-to-write 2
    min-slaves-max-lag 10
    ```
3. **客户端配置**:
    ```python
    sentinel = Sentinel([
        ('localhost', 26379),
        ('localhost', 26380),
        ('localhost', 26381)
    ])
    master = sentinel.master_for('mymaster', socket_timeout=0.1)
    ```

---

## Redis 集群详解

### Sentinel 模式

#### 核心功能

1. **监控 (Monitoring)**: 监控 master 和 slave 健康状态
2. **通知 (Notification)**: 故障时通知管理员
3. **自动故障转移 (Automatic Failover)**: 自动选举新 master
4. **配置提供 (Configuration Provider)**: 为客户端提供当前 master 地址

#### 工作原理

```bash
# Sentinel 配置文件
sentinel monitor mymaster 127.0.0.1 6379 2
sentinel down-after-milliseconds mymaster 30000
sentinel parallel-syncs mymaster 1
sentinel failover-timeout mymaster 180000
```

故障转移流程：

1. **主观下线 (SDOWN)**: 单个 Sentinel 认为主节点不可用
2. **客观下线 (ODOWN)**: 多数 Sentinel 确认主节点不可用
3. **领导选举**: Sentinel 之间选举领导者执行故障转移
4. **新主选择**: 选择最优 slave 提升为 master
5. **配置更新**: 更新所有节点配置

### Cluster 集群模式

#### 集群特性

- **去中心化**: 无单点故障
- **数据分片**: 自动数据分布
- **高可用**: master 故障自动切换
- **在线扩缩容**: 支持动态添加/删除节点

#### 数据分片算法

```bash
# 计算 Key 哈希 Slot
HASH_SLOT = CRC16(key) % 16384

# Slot 分配示例（3 个 Master 节点）
Master1: 0-5461 (5462 Slot)
Master2: 5462-10923 (5462 Slot)
Master3: 10924-16383 (5460 Slot)
```

#### 集群操作命令

```bash
# 创建集群
redis-cli --cluster create \
  127.0.0.1:7000 127.0.0.1:7001 127.0.0.1:7002 \
  127.0.0.1:7003 127.0.0.1:7004 127.0.0.1:7005 \
  --cluster-replicas 1

# 查看集群信息
CLUSTER INFO
CLUSTER NODES

# 重新分片
redis-cli --cluster reshard 127.0.0.1:7000

# 添加节点
redis-cli --cluster add-node 127.0.0.1:7006 127.0.0.1:7000
```

---

## 布隆过滤器

布隆过滤器是一种概率性数据结构，用于高效判断一个元素是否在集合中。

### 核心特性

- **误报率**: 可能误判存在，但不会误判不存在
- **空间效率**: 使用位数组，空间复杂度低
- **时间复杂度**: O(k) 查询时间，k 为哈希函数数量

### 实现原理

```python
# 基本流程
# 1. 初始化: 创建 m 位位数组，k 个哈希函数
# 2. 添加元素: 对元素计算 k 个哈希值，设置对应位为 1
# 3. 查询元素: 计算 k 个哈希值，检查对应位是否都为 1
```

### 参数计算

```
# 最优位数组大小
m = -n * ln(p) / (ln(2))^2

# 最优哈希函数数量
k = (m/n) * ln(2)

# 其中：n=元素数量，p=误报率，m=位数组大小，k=哈希函数数量
```

### Redis 布隆过滤器

```bash
# 加载 RedisBloom 模块
MODULE LOAD /path/to/redisbloom.so

# 创建布隆过滤器
BF.RESERVE myfilter 0.01 10000

# 添加元素
BF.ADD myfilter "user123"
BF.MADD myfilter "user1" "user2" "user3"

# 检查元素
BF.EXISTS myfilter "user123"
BF.MEXISTS myfilter "user1" "user2"

# 获取信息
BF.INFO myfilter
```

### 应用场景

1. **缓存穿透防护**: 过滤不存在的请求
2. **爬虫 URL 去重**: 避免重复爬取
3. **垃圾邮件过滤**: 快速判断发件人
4. **推荐系统**: 已推荐内容过滤

---

## Stream 流数据结构

Stream 是 Redis 5.0 引入的新数据结构，主要用于消息队列和事件流处理。

### 核心特性

- **持久化消息队列**: 消息持久化存储
- **消费者组**: 支持多消费者协作
- **消息确认**: 支持消息确认机制
- **历史消息**: 可以查询历史消息

### 消息 ID 结构

```
<毫秒时间戳>-<序列号>
例如: 1609459200000-0
```

### 基本操作

```bash
# 添加消息
XADD mystream * field1 value1 field2 value2
XADD mystream 1609459200000-0 user "john" action "login"

# 读取消息
XREAD COUNT 2 STREAMS mystream 0
XREAD BLOCK 1000 STREAMS mystream $  # 阻塞读取新消息

# 查看 Stream 信息
XINFO STREAM mystream
XLEN mystream

# 范围查询
XRANGE mystream - +
XRANGE mystream 1609459200000 1609459300000
```

### 消费者组操作

```bash
# 创建消费者组
XGROUP CREATE mystream mygroup $ MKSTREAM

# 消费者读取
XREADGROUP GROUP mygroup consumer1 COUNT 1 STREAMS mystream >

# 确认消息
XACK mystream mygroup 1609459200000-0

# 查看消费者组信息
XINFO GROUPS mystream
XINFO CONSUMERS mystream mygroup

# 处理 pending 消息
XPENDING mystream mygroup
XCLAIM mystream mygroup consumer2 1800000 1609459200000-0
```

### Stream 与其他队列对比

| 特性 | List | Pub/Sub | Stream |
|:-----|:-----|:--------|:-------|
| 持久化 | 支持 | 不支持 | 支持 |
| 多消费者 | 不支持 | 支持 | 支持 |
| 消息确认 | 不支持 | 不支持 | 支持 |
| 历史消息 | 支持 | 不支持 | 支持 |
| 消费者组 | 不支持 | 不支持 | 支持 |

---

## 面试高频考点

### 持久化机制

#### RDB (Redis Database)

```bash
# 配置文件设置
save 900 1      # 900 秒内至少 1 个 key 变化
save 300 10     # 300 秒内至少 10 个 key 变化
save 60 10000   # 60 秒内至少 10000 个 key 变化

# 手动触发
SAVE    # 同步保存（阻塞）
BGSAVE  # 异步保存（后台）
```

#### AOF (Append Only File)

```bash
# 配置选项
appendonly yes
appendfsync always    # 每次写入立即同步
appendfsync everysec  # 每秒同步一次（推荐）
appendfsync no        # 由 OS 决定同步时机
```

#### 混合持久化 (Redis 4.0+)

```bash
aof-use-rdb-preamble yes
```

### 内存淘汰策略

```bash
# 配置最大内存
maxmemory 2gb

# 淘汰策略
maxmemory-policy allkeys-lru
```

| 策略 | 说明 |
|:-----|:-----|
| `noeviction` | 不淘汰，内存满时返回错误 |
| `allkeys-lru` | 所有 key 中淘汰最近最少使用的 |
| `allkeys-lfu` | 所有 key 中淘汰最少频率的 |
| `volatile-lru` | 有过期时间的 key 中淘汰最近最少使用的 |
| `volatile-lfu` | 有过期时间的 key 中淘汰最少频率的 |
| `volatile-random` | 有过期时间的 key 中随机淘汰 |
| `volatile-ttl` | 淘汰即将过期的 key |

### 缓存问题解决方案

#### 1. 缓存穿透

- **问题**: 查询不存在的数据，绕过缓存直接查数据库
- **解决方案**:
  - 布隆过滤器预过滤
  - 空值缓存（设置较短过期时间）
  - 参数校验

#### 2. 缓存雪崩

- **问题**: 大量缓存同时失效，数据库压力激增
- **解决方案**:
  - 随机过期时间
  - 缓存预热
  - 多级缓存
  - 限流降级

#### 3. 缓存击穿

- **问题**: 热点数据过期，大量请求直达数据库
- **解决方案**:
  - 互斥锁重建缓存
  - 异步更新缓存
  - 热点数据永不过期

### 分布式锁实现

#### 基于 SETNX 的简单锁

```bash
# 加锁
SET lock_key unique_value PX 30000 NX

# 释放锁（Lua 脚本保证原子性）
if redis.call("get", KEYS[1]) == ARGV[1] then
    return redis.call("del", KEYS[1])
else
    return 0
end
```

#### Redlock 算法

1. 获取当前时间戳
2. 依次向 N 个 Redis 实例请求加锁
3. 超过 N/2+1 个实例加锁成功才算成功
4. 加锁总时间要小于锁过期时间
5. 释放所有实例上的锁

### 性能优化

#### 1. 合理的数据结构

- 小数据量使用 ziplist 编码（节省内存）
- 大数据量使用 hashtable 编码（提高性能）

#### 2. 批量操作

```bash
# 使用 pipeline 减少网络往返
PIPELINE
SET key1 value1
SET key2 value2
EXEC

# 使用 MGET/MSET 批量操作
MSET key1 value1 key2 value2
MGET key1 key2
```

#### 3. 配置优化

```bash
# 配置优化
hash-max-ziplist-entries 512
hash-max-ziplist-value 64
list-max-ziplist-size -2
set-max-intset-entries 512
```

---

## 数据库技术选型对比

### 关系型数据库

#### MySQL

| 方面 | 描述 |
|:-----|:-----|
| **存储引擎** | InnoDB (事务)、MyISAM (性能) |
| **事务支持** | 完整 ACID 支持 |
| **复制** | 主从复制、主主复制 |
| **适用场景** | Web 应用、电商系统、金融系统 |

#### PostgreSQL

| 方面 | 描述 |
|:-----|:-----|
| **数据类型** | 丰富的内置类型 (JSON、数组、地理) |
| **索引类型** | B-tree、Hash、GiST、GIN、BRIN |
| **并发控制** | MVCC 多版本并发控制 |
| **适用场景** | 复杂查询、数据分析、地理信息系统 |

### NoSQL 数据库

#### MongoDB

| 方面 | 描述 |
|:-----|:-----|
| **数据模型** | BSON 文档 |
| **分片** | 自动分片 (Auto-Sharding) |
| **复制** | 副本集 (Replica Set) |
| **适用场景** | 内容管理、实时分析、物联网 |

#### Cassandra

| 方面 | 描述 |
|:-----|:-----|
| **数据模型** | 宽列存储 |
| **一致性** | 可调一致性 |
| **分区** | 一致性哈希 |
| **适用场景** | 时序数据、日志系统、推荐系统 |

### 数据库对比总结

| 数据库 | 类型 | 一致性 | 扩展性 | 查询能力 | 适用场景 |
|:-------|:-----|:-------|:-------|:---------|:---------|
| MySQL | 关系型 | 强一致 | 垂直扩展 | 很强 | 通用业务 |
| PostgreSQL | 关系型 | 强一致 | 垂直扩展 | 很强 | 复杂分析 |
| Redis | 键值 | 最终一致 | 水平扩展 | 弱 | 缓存、会话 |
| MongoDB | 文档 | 强一致 | 水平扩展 | 中等 | 内容管理 |
| Cassandra | 列族 | 可调一致 | 线性扩展 | 弱 | 高并发写入 |

### 选型原则

1. **业务需求优先**: 根据具体业务场景选择
2. **团队能力**: 考虑团队的技术栈和维护能力
3. **成本控制**: 综合考虑开发、运维、硬件成本
4. **未来扩展**: 预留技术演进空间

### 最佳实践

- **读多写少**: MySQL/PostgreSQL + Redis
- **写多读少**: Cassandra/MongoDB + Redis
- **复杂查询**: PostgreSQL + 数据仓库
- **实时分析**: HBase + Spark/Flink
- **混合负载**: 多数据库架构 + 数据同步
