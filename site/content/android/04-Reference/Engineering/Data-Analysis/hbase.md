---
title: "HBase 分布式 NoSQL 数据库"
weight: 10
---

# HBase 分布式 NoSQL 数据库

Apache HBase 是一个分布式、面向列的开源数据库，基于 Google Bigtable 论文实现，运行在 HDFS 之上。

## 目录

1. [HBase 架构](#hbase-架构)
2. [数据模型](#数据模型)
3. [Shell 操作](#shell-操作)
4. [Java API](#java-api)
5. [性能优化](#性能优化)
6. [集群管理](#集群管理)
7. [知识要点](#知识要点)

---

## HBase 架构

### 核心组件

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ RegionServer│    │ RegionServer│    │ RegionServer│
│  Region1,2  │    │  Region3,4  │    │  Region5,6  │
└──────┬──────┘    └──────┬──────┘    └──────┬──────┘
       │                  │                  │
       ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────┐
│                    HDFS 集群                         │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
                  ┌───────────────┐
                  │   ZooKeeper   │
                  └───────────────┘
```

| 组件 | 说明 |
|------|------|
| HMaster | 管理 RegionServer，处理表的创建/删除，Region 分配 |
| RegionServer | 处理数据读写请求，管理多个 Region |
| Region | 表的水平分片，包含一定范围的行 |
| ZooKeeper | 协调服务，存储元数据，故障检测 |
| HDFS | 底层存储系统 |

### Region 详细结构

```
Region
├── Store (列族)
│   ├── MemStore (内存缓冲)
│   └── HFile (磁盘文件)
│       ├── Data Block
│       ├── Index Block
│       └── Bloom Filter
└── WAL (Write-Ahead Log)
```

### 写入流程

1. **Client** → **RegionServer**: 写请求
2. **WAL**: 先写预写日志（保证数据持久性）
3. **MemStore**: 数据写入内存
4. **Flush**: MemStore 达到阈值时刷写到 HFile
5. **Compaction**: 定期合并 HFile

### 读取流程

1. **Client** → **RegionServer**: 读请求
2. **MemStore**: 先查内存中的数据
3. **BlockCache**: 查询缓存的 HFile 块
4. **HFile**: 从磁盘读取数据
5. **Merge**: 合并多个来源的数据返回

---

## 数据模型

### 逻辑视图

```
Table: user_info
├── Row Key: user001
│   ├── Column Family: basic_info
│   │   ├── name:zhang_san (timestamp:1234567890)
│   │   └── age:25 (timestamp:1234567891)
│   └── Column Family: contact_info
│       ├── email:zhang@example.com (timestamp:1234567892)
│       └── phone:13800138000 (timestamp:1234567893)
└── Row Key: user002
    └── ...
```

### 物理存储

```
basic_info Store:
user001:name:1234567890 → zhang_san
user001:age:1234567891 → 25
user002:name:1234567900 → li_si

contact_info Store:
user001:email:1234567892 → zhang@example.com
user001:phone:1234567893 → 13800138000
```

### 核心概念

| 概念 | 说明 |
|------|------|
| Row Key | 行键，表的主键，按字典序排序 |
| Column Family | 列族，列的逻辑分组 |
| Column Qualifier | 列限定符，列族下的具体列 |
| Cell | 单元格，由(row, column family, column qualifier, timestamp)确定 |
| Timestamp | 时间戳，同一 Cell 的多个版本 |

---

## Shell 操作

### 连接与基本操作

```bash
# 启动 HBase Shell
hbase shell

# 查看状态
status
version

# 查看集群信息
whoami
```

### 命名空间管理

```bash
# 创建命名空间
create_namespace 'my_namespace'

# 列出命名空间
list_namespace

# 删除命名空间
drop_namespace 'my_namespace'
```

### 表操作

```bash
# 创建表（带配置）
create 'user_info',
  {NAME => 'basic_info', VERSIONS => 3, TTL => 2592000},
  {NAME => 'contact_info', COMPRESSION => 'SNAPPY'}

# 列出表
list

# 查看表结构
describe 'user_info'

# 禁用表
disable 'user_info'

# 启用表
enable 'user_info'

# 删除表
drop 'user_info'

# 修改表结构
alter 'user_info', {NAME => 'basic_info', VERSIONS => 5}
```

### 数据操作

```bash
# 插入数据
put 'user_info', 'user001', 'basic_info:name', 'zhang_san'
put 'user_info', 'user001', 'basic_info:age', '25'
put 'user_info', 'user001', 'contact_info:email', 'zhang@example.com'

# 查询单行
get 'user_info', 'user001'

# 查询指定列族
get 'user_info', 'user001', 'basic_info'

# 查询指定列
get 'user_info', 'user001', 'basic_info:name'

# 扫描表
scan 'user_info'

# 条件扫描
scan 'user_info', {STARTROW => 'user001', ENDROW => 'user999'}
scan 'user_info', {FILTER => "SingleColumnValueFilter('basic_info', 'age', >=, 'binary:18')"}

# 删除数据
delete 'user_info', 'user001', 'basic_info:age'

# 删除行
deleteall 'user_info', 'user001'

# 计数
count 'user_info'
```

---

## Java API

### 连接配置

```java
// 配置连接
Configuration conf = HBaseConfiguration.create();
conf.set("hbase.zookeeper.quorum", "node1,node2,node3");
conf.set("hbase.zookeeper.property.clientPort", "2181");

// 创建连接
Connection connection = ConnectionFactory.createConnection(conf);
Admin admin = connection.getAdmin();
```

### 表管理

```java
// 创建表
TableName tableName = TableName.valueOf("user_info");
HTableDescriptor tableDesc = new HTableDescriptor(tableName);

// 添加列族
HColumnDescriptor basicInfo = new HColumnDescriptor("basic_info");
basicInfo.setMaxVersions(3);
basicInfo.setTimeToLive(30 * 24 * 60 * 60); // 30 天 TTL

HColumnDescriptor contactInfo = new HColumnDescriptor("contact_info");
contactInfo.setCompressionType(Compression.Algorithm.SNAPPY);

tableDesc.addFamily(basicInfo);
tableDesc.addFamily(contactInfo);

// 创建表
admin.createTable(tableDesc);
```

### 数据操作

```java
Table table = connection.getTable(TableName.valueOf("user_info"));

// 插入数据
Put put = new Put(Bytes.toBytes("user001"));
put.addColumn(Bytes.toBytes("basic_info"), Bytes.toBytes("name"), Bytes.toBytes("zhang_san"));
put.addColumn(Bytes.toBytes("basic_info"), Bytes.toBytes("age"), Bytes.toBytes("25"));
table.put(put);

// 批量插入
List<Put> puts = new ArrayList<>();
for (int i = 0; i < 1000; i++) {
    Put batchPut = new Put(Bytes.toBytes("user" + String.format("%03d", i)));
    batchPut.addColumn(Bytes.toBytes("basic_info"), Bytes.toBytes("name"), Bytes.toBytes("user" + i));
    puts.add(batchPut);
}
table.put(puts);

// 查询数据
Get get = new Get(Bytes.toBytes("user001"));
get.addFamily(Bytes.toBytes("basic_info"));
Result result = table.get(get);

// 解析结果
for (Cell cell : result.listCells()) {
    String family = Bytes.toString(CellUtil.cloneFamily(cell));
    String qualifier = Bytes.toString(CellUtil.cloneQualifier(cell));
    String value = Bytes.toString(CellUtil.cloneValue(cell));
    System.out.println(family + ":" + qualifier + " = " + value);
}

// 扫描数据
Scan scan = new Scan();
scan.setStartRow(Bytes.toBytes("user001"));
scan.setStopRow(Bytes.toBytes("user999"));
scan.addFamily(Bytes.toBytes("basic_info"));

ResultScanner scanner = table.getScanner(scan);
for (Result res : scanner) {
    // 处理结果
}
scanner.close();
```

### 过滤器

```java
// 单列值过滤器
SingleColumnValueFilter filter = new SingleColumnValueFilter(
    Bytes.toBytes("basic_info"),
    Bytes.toBytes("age"),
    CompareFilter.CompareOp.GREATER_OR_EQUAL,
    Bytes.toBytes("18")
);

// 前缀过滤器
PrefixFilter prefixFilter = new PrefixFilter(Bytes.toBytes("user00"));

// 组合过滤器
FilterList filterList = new FilterList(FilterList.Operator.MUST_PASS_ALL);
filterList.addFilter(filter);
filterList.addFilter(prefixFilter);

scan.setFilter(filterList);
```

---

## 性能优化

### Row Key 设计

```java
// 1. 避免热点：使用散列前缀
String rowKey = MD5Hash.digest(userId).toString().substring(0, 2) + "_" + userId;

// 2. 时间倒序：便于查询最新数据
String rowKey = userId + "_" + (Long.MAX_VALUE - timestamp);

// 3. 组合 Key：支持多维查询
String rowKey = region + "_" + userId + "_" + timestamp;
```

### 列族设计

```java
// 合理设计：按访问模式分组
create 'user_profile',
  {NAME => 'profile', COMPRESSION => 'SNAPPY'},   // 用户基本信息
  {NAME => 'behavior', TTL => 604800}             // 用户行为数据(7天 TTL)

// 避免：列族过多
// 避免：不同访问模式的列放在同一列族
```

### 批量操作

```java
List<Put> puts = new ArrayList<>();
for (UserData user : userData) {
    Put put = createPut(user);
    puts.add(put);

    // 批量提交
    if (puts.size() >= 1000) {
        table.put(puts);
        puts.clear();
    }
}
// 提交剩余数据
if (!puts.isEmpty()) {
    table.put(puts);
}
```

### 缓存配置

```java
// 启用 Block Cache
HColumnDescriptor family = new HColumnDescriptor("data");
family.setBlockCacheEnabled(true);
family.setCacheBloomsOnWrite(true);
family.setCacheDataOnWrite(true);
family.setCacheIndexesOnWrite(true);
```

---

## 集群管理

### Region 管理

```bash
# 手动分裂 Region
split 'user_info', 'user500'

# 合并 Region
merge_region 'region1_encoded_name', 'region2_encoded_name'

# 查看 Region 信息
list_regions 'user_info'
```

### 负载均衡

```bash
# 手动触发负载均衡
balancer

# 查看负载均衡状态
balancer_enabled
```

### Compaction

```bash
# 手动触发 Major Compaction
major_compact 'user_info'

# 手动触发 Minor Compaction
compact 'user_info'

# 查看压缩状态
compaction_state 'user_info'
```

### 监控

```bash
# 查看 RegionServer 信息
list_regionservers

# 查看表统计信息
list_table_stats 'user_info'
```

---

## 知识要点

### 1. HBase vs 关系型数据库

| 特性 | HBase | 关系型数据库 |
|------|-------|-------------|
| 数据模型 | 列族模型 | 关系模型 |
| ACID | 行级原子性 | 完整ACID |
| 扩展性 | 水平扩展 | 垂直扩展 |
| 查询语言 | NoSQL API | SQL |
| 适用场景 | 大数据读写 | 复杂事务 |

### 2. 数据倾斜问题

**问题**: Region 热点，某些 Region 访问量过大

**解决方案**:
1. **Row Key 设计**: 避免单调递增，使用散列前缀
2. **预分区**: 创建表时预先分区
3. **负载均衡**: 定期执行 balance 操作

```java
// 预分区示例
byte[][] splits = new byte[10][];
for (int i = 0; i < 10; i++) {
    splits[i] = Bytes.toBytes(String.format("%02d", i));
}
admin.createTable(tableDesc, splits);
```

### 3. 读取性能优化

1. **Bloom Filter**: 快速判断数据是否存在
2. **Block Cache**: 缓存热点数据
3. **压缩**: 减少存储空间和 IO
4. **预读**: 设置合理的扫描缓存

```java
// 配置 Bloom Filter
HColumnDescriptor family = new HColumnDescriptor("data");
family.setBloomFilterType(BloomType.ROW);
```

### 4. 写入性能优化

1. **批量写入**: 减少 RPC 调用
2. **WAL**: 根据需要关闭 WAL
3. **MemStore**: 调整内存大小
4. **压缩**: 异步压缩

```java
// 关闭 WAL（数据安全性降低）
put.setDurability(Durability.SKIP_WAL);
```

### 5. 故障恢复

1. **WAL**: 通过预写日志恢复数据
2. **Region 迁移**: 自动迁移故障节点的 Region
3. **ZooKeeper**: 监控集群状态，协调故障恢复
4. **数据副本**: 依赖 HDFS 的数据副本机制

### 6. 热点问题诊断

```bash
# 1. 查看 Region 分布
list_regions 'table_name'

# 2. 查看 RegionServer 负载
status 'detailed'

# 3. 分析访问模式
# 通过日志分析热点 Row Key

# 4. 重新设计 Row Key
# 添加散列前缀或使用反向时间戳
```
