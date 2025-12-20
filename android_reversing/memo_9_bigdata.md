# 🏗️ 大数据技术栈速记

## 🌟 大数据生态概览

### 📊 技术栈分层

| 层级 | 技术组件 | 作用 | 代表产品 |
|:---|:---|:---|:---|
| **存储层** | 分布式存储 | 海量数据存储 | HDFS、HBase、Cassandra |
| **计算层** | 分布式计算 | 数据处理与分析 | Spark、Flink、MapReduce |
| **数据仓库层** | 数据仓库 | 结构化数据管理 | Hive、Impala、Presto |
| **协调层** | 集群管理 | 资源调度与协调 | YARN、Mesos、K8s |
| **应用层** | 业务应用 | 数据分析与挖掘 | Jupyter、Zeppelin、Tableau |

### 🔄 数据处理模式

| 模式 | 特点 | 延迟 | 适用场景 | 代表技术 |
|:---|:---|:---|:---|:---|
| **批处理** | 大批量、高吞吐 | 分钟到小时 | 数据仓库、报表 | Spark、Hive、MapReduce |
| **流处理** | 实时、低延迟 | 毫秒到秒 | 实时监控、告警 | Flink、Storm、Kafka Streams |
| **交互式查询** | 快速响应 | 秒级 | 即席查询、探索 | Impala、Presto、Druid |

---

## 🗄️ HDFS 分布式文件系统

### 🏗️ 核心架构
```
Client → NameNode (元数据管理)
           ↓
       DataNode1, DataNode2, DataNode3...
       (数据存储，默认3副本)
```

### 🔧 关键特性
- **高容错性**: 数据多副本存储
- **高吞吐量**: 优化大文件读写
- **可扩展性**: 水平扩展存储容量
- **数据本地性**: 计算靠近数据

### 📋 常用操作
```bash
# 文件操作
hdfs dfs -ls /user/data/
hdfs dfs -put local_file.txt /user/data/
hdfs dfs -get /user/data/file.txt local_file.txt
hdfs dfs -rm /user/data/file.txt

# 目录操作
hdfs dfs -mkdir -p /user/data/year=2023/month=12
hdfs dfs -rmr /user/data/old_data

# 查看文件信息
hdfs dfs -stat %b,%o,%r /user/data/file.txt  # 大小、块大小、副本数
hdfs fsck /user/data/ -files -blocks -locations  # 文件系统检查

# 集群管理
hdfs dfsadmin -report  # 集群状态
hdfs dfsadmin -safemode get  # 安全模式状态
```

### ⚙️ 性能调优
```xml
<!-- hdfs-site.xml 配置优化 -->
<configuration>
    <!-- 块大小优化 -->
    <property>
        <name>dfs.blocksize</name>
        <value>268435456</value>  <!-- 256MB，适合大文件 -->
    </property>
    
    <!-- 副本数设置 -->
    <property>
        <name>dfs.replication</name>
        <value>3</value>
    </property>
    
    <!-- NameNode内存优化 -->
    <property>
        <name>dfs.namenode.handler.count</name>
        <value>100</value>  <!-- 处理线程数 -->
    </property>
</configuration>
```

---

## 🐝 Hive 数据仓库

### 🏗️ 架构组件
```
Hive CLI/Beeline → Hive Server2 → Metastore → HDFS
                     ↓
                 MapReduce/Spark Engine
```

### 📊 数据模型
- **Database**: 数据库命名空间
- **Table**: 对应HDFS目录结构
- **Partition**: 数据分区，提高查询效率
- **Bucket**: 数据分桶，优化Join操作

### 🔧 DDL操作
```sql
-- 创建数据库
CREATE DATABASE IF NOT EXISTS warehouse
COMMENT 'Data warehouse database'
LOCATION '/user/hive/warehouse'
WITH DBPROPERTIES ('creator'='admin');

-- 创建外部表
CREATE EXTERNAL TABLE user_logs (
    user_id BIGINT,
    action STRING,
    timestamp TIMESTAMP,
    ip STRING
)
PARTITIONED BY (
    year INT,
    month INT,
    day INT
)
STORED AS PARQUET
LOCATION '/user/data/logs/';

-- 添加分区
ALTER TABLE user_logs ADD PARTITION (year=2023, month=12, day=25)
LOCATION '/user/data/logs/year=2023/month=12/day=25/';

-- 创建分桶表
CREATE TABLE user_profiles (
    user_id BIGINT,
    name STRING,
    age INT,
    gender STRING
)
CLUSTERED BY (user_id) INTO 32 BUCKETS
STORED AS ORC
TBLPROPERTIES ('transactional'='true');
```

### 📈 查询优化
```sql
-- 分区裁剪
SELECT COUNT(*) FROM user_logs 
WHERE year=2023 AND month=12 AND day=25;

-- 列式存储查询
SELECT user_id, COUNT(*) as action_count
FROM user_logs 
WHERE year=2023 AND month=12
GROUP BY user_id;

-- 窗口函数
SELECT user_id, action, timestamp,
       ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY timestamp DESC) as rn
FROM user_logs
WHERE year=2023 AND month=12;

-- JOIN优化
SET hive.auto.convert.join=true;
SET hive.mapjoin.smalltable.filesize=25000000;

SELECT /*+ MAPJOIN(u) */ l.user_id, u.name, COUNT(*) as actions
FROM user_logs l
JOIN user_profiles u ON l.user_id = u.user_id
WHERE l.year=2023 AND l.month=12
GROUP BY l.user_id, u.name;
```

---

## ⚡ Spark 统一分析引擎

### 🏗️ 核心组件
```
Spark Application
    ↓
Driver Program → Cluster Manager (YARN/Mesos/K8s)
    ↓              ↓
SparkContext → Executor1, Executor2, Executor3...
```

### 💻 RDD编程
```python
from pyspark import SparkContext, SparkConf

# 初始化Spark
conf = SparkConf().setAppName("DataProcessing").setMaster("yarn")
sc = SparkContext(conf=conf)

# RDD操作
lines = sc.textFile("hdfs://data/logs.txt")
words = lines.flatMap(lambda line: line.split())
word_counts = words.map(lambda word: (word, 1)) \
                  .reduceByKey(lambda a, b: a + b)

# 缓存RDD
word_counts.cache()
word_counts.collect()

# 并行度调优
rdd_optimized = sc.textFile("hdfs://data/large_file.txt", minPartitions=100)
```

### 📊 DataFrame/Dataset API
```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

# 创建SparkSession
spark = SparkSession.builder \
    .appName("DataAnalysis") \
    .config("spark.sql.adaptive.enabled", "true") \
    .getOrCreate()

# 读取数据
df = spark.read.format("parquet") \
    .option("path", "hdfs://data/user_events/") \
    .load()

# DataFrame操作
result = df.filter(col("event_date") >= "2023-12-01") \
          .groupBy("user_id", "event_type") \
          .agg(count("*").alias("event_count")) \
          .orderBy(desc("event_count"))

# 窗口函数
from pyspark.sql.window import Window

window_spec = Window.partitionBy("user_id").orderBy("timestamp")
df_with_rank = df.withColumn("rank", row_number().over(window_spec))

# 写入数据
result.write.format("delta") \
    .mode("overwrite") \
    .option("path", "hdfs://output/user_analysis/") \
    .save()
```

### 🚀 性能优化
```python
# 广播变量
broadcast_map = spark.sparkContext.broadcast(lookup_dict)

def enrich_data(row):
    return row + (broadcast_map.value.get(row.user_id),)

# 累加器
error_count = spark.sparkContext.accumulator(0)

def process_record(record):
    try:
        # 处理逻辑
        return process(record)
    except:
        error_count.add(1)
        return None

# 自适应查询执行
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
```

---

## 🌊 Flink 流处理引擎

### 🏗️ 核心概念
- **DataStream**: 无界数据流
- **Transformation**: 数据转换操作
- **Sink**: 数据输出
- **Watermark**: 处理事件时间

### 💻 流处理编程
```java
// Java Flink应用
public class StreamProcessingApp {
    public static void main(String[] args) throws Exception {
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        
        // 设置检查点
        env.enableCheckpointing(5000);
        env.getCheckpointConfig().setCheckpointingMode(CheckpointingMode.EXACTLY_ONCE);
        
        // 数据源
        DataStream<String> source = env.addSource(
            new FlinkKafkaConsumer<>("user-events", new SimpleStringSchema(), properties)
        );
        
        // 数据转换
        DataStream<UserEvent> events = source
            .map(json -> parseUserEvent(json))
            .filter(event -> event.getEventType().equals("click"))
            .keyBy(UserEvent::getUserId)
            .window(TumblingEventTimeWindows.of(Time.minutes(5)))
            .aggregate(new EventCountAggregator());
        
        // 输出
        events.addSink(new FlinkKafkaProducer<>("processed-events", 
                                              new UserEventSerializationSchema(),
                                              properties));
        
        env.execute("User Event Processing");
    }
}
```

### ⏰ 时间与窗口
```java
// 事件时间处理
DataStream<UserEvent> timestampedStream = source
    .assignTimestampsAndWatermarks(
        WatermarkStrategy.<UserEvent>forBoundedOutOfOrderness(Duration.ofSeconds(20))
            .withTimestampAssigner((event, timestamp) -> event.getEventTime())
    );

// 不同类型的窗口
// 滚动窗口
.window(TumblingEventTimeWindows.of(Time.minutes(5)))

// 滑动窗口  
.window(SlidingEventTimeWindows.of(Time.minutes(10), Time.minutes(5)))

// 会话窗口
.window(EventTimeSessionWindows.withGap(Time.minutes(30)))

// 计数窗口
.countWindow(1000)
```

### 🔄 状态管理
```java
// 键控状态
public class StatefulProcessor extends KeyedProcessFunction<String, UserEvent, String> {
    
    private ValueState<Long> countState;
    private MapState<String, Long> featureState;
    
    @Override
    public void open(Configuration parameters) {
        ValueStateDescriptor<Long> countDescriptor = 
            new ValueStateDescriptor<>("count", Long.class, 0L);
        countState = getRuntimeContext().getState(countDescriptor);
        
        MapStateDescriptor<String, Long> featureDescriptor = 
            new MapStateDescriptor<>("features", String.class, Long.class);
        featureState = getRuntimeContext().getMapState(featureDescriptor);
    }
    
    @Override
    public void processElement(UserEvent event, Context ctx, Collector<String> out) 
            throws Exception {
        Long currentCount = countState.value();
        countState.update(currentCount + 1);
        
        featureState.put(event.getFeature(), System.currentTimeMillis());
        
        out.collect("Processed event for user: " + ctx.getCurrentKey());
    }
}
```

---

## 🚀 Impala 交互式查询

### 🎯 核心特性
- **MPP架构**: 大规模并行处理
- **内存计算**: 避免磁盘I/O开销
- **SQL兼容**: 标准SQL语法
- **实时查询**: 秒级响应时间

### 🔧 查询优化
```sql
-- 分区表查询
SELECT customer_id, SUM(amount) as total_amount
FROM sales_fact
WHERE year = 2023 AND month = 12
GROUP BY customer_id;

-- 复杂JOIN查询
SELECT /*+ broadcast(d) */ 
    f.product_id, 
    d.product_name,
    SUM(f.sales_amount) as total_sales
FROM sales_fact f
JOIN product_dim d ON f.product_id = d.product_id
WHERE f.year = 2023
GROUP BY f.product_id, d.product_name
ORDER BY total_sales DESC
LIMIT 100;

-- 窗口函数
SELECT 
    customer_id,
    order_date,
    amount,
    SUM(amount) OVER (
        PARTITION BY customer_id 
        ORDER BY order_date 
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) as running_total
FROM orders
WHERE year = 2023;
```

### ⚙️ 性能调优
```sql
-- 统计信息更新
COMPUTE STATS sales_fact;
COMPUTE INCREMENTAL STATS sales_fact PARTITION (year=2023, month=12);

-- 查询提示
SELECT /*+ straight_join */ *
FROM large_table a
JOIN small_table b ON a.id = b.id;

-- 内存优化
SET mem_limit=8GB;
SET disable_codegen=false;
SET runtime_filter_mode=GLOBAL;
```

---

## 🏺 HBase 列族数据库

### 🏗️ 数据模型
```
Table
  ↓
Row Key → Column Family → Column Qualifier → Cell (Value + Timestamp)
```

### 💻 Java API操作
```java
// 连接HBase
Configuration conf = HBaseConfiguration.create();
conf.set("hbase.zookeeper.quorum", "zk1,zk2,zk3");
Connection connection = ConnectionFactory.createConnection(conf);

// 创建表
Admin admin = connection.getAdmin();
TableName tableName = TableName.valueOf("user_profiles");
HTableDescriptor tableDesc = new HTableDescriptor(tableName);
tableDesc.addFamily(new HColumnDescriptor("info"));
tableDesc.addFamily(new HColumnDescriptor("stats"));
admin.createTable(tableDesc);

// 插入数据
Table table = connection.getTable(tableName);
Put put = new Put(Bytes.toBytes("user123"));
put.addColumn(Bytes.toBytes("info"), Bytes.toBytes("name"), Bytes.toBytes("John"));
put.addColumn(Bytes.toBytes("info"), Bytes.toBytes("age"), Bytes.toBytes("30"));
put.addColumn(Bytes.toBytes("stats"), Bytes.toBytes("login_count"), Bytes.toBytes("150"));
table.put(put);

// 查询数据
Get get = new Get(Bytes.toBytes("user123"));
Result result = table.get(get);
byte[] name = result.getValue(Bytes.toBytes("info"), Bytes.toBytes("name"));
System.out.println("Name: " + Bytes.toString(name));

// 扫描数据
Scan scan = new Scan();
scan.setStartRow(Bytes.toBytes("user100"));
scan.setStopRow(Bytes.toBytes("user200"));
ResultScanner scanner = table.getScanner(scan);
for (Result r : scanner) {
    // 处理结果
    processResult(r);
}
```

### 🔧 性能优化
```java
// 批量操作
List<Put> puts = new ArrayList<>();
for (UserData user : users) {
    Put put = new Put(Bytes.toBytes(user.getId()));
    put.addColumn(Bytes.toBytes("info"), Bytes.toBytes("name"), 
                  Bytes.toBytes(user.getName()));
    puts.add(put);
}
table.put(puts);

// 预分区
byte[][] splitKeys = new byte[][] {
    Bytes.toBytes("1000"),
    Bytes.toBytes("2000"),
    Bytes.toBytes("3000")
};
admin.createTable(tableDesc, splitKeys);

// 布隆过滤器
HColumnDescriptor cf = new HColumnDescriptor("info");
cf.setBloomFilterType(BloomType.ROW);
cf.setBlockCacheEnabled(true);
tableDesc.addFamily(cf);
```

---

## 🎯 常见面试题及答案

### Q1: HDFS的读写流程是什么？
**A**: 
**写流程**:
1. Client向NameNode请求写文件
2. NameNode检查权限和命名空间，返回DataNode列表
3. Client向第一个DataNode写数据
4. DataNode之间形成Pipeline进行副本复制
5. 所有副本写入完成后返回确认

**读流程**:
1. Client向NameNode请求读文件
2. NameNode返回文件块位置信息
3. Client直接从DataNode读取数据
4. 选择最近的DataNode读取以优化性能

### Q2: Hive和传统数据库的区别？
**A**: 
- **数据规模**: Hive处理PB级数据，传统数据库处理GB-TB级
- **查询延迟**: Hive分钟级，传统数据库毫秒-秒级
- **ACID支持**: Hive部分支持，传统数据库完全支持
- **Schema**: Hive读时模式，传统数据库写时模式
- **计算模式**: Hive批处理，传统数据库事务处理

### Q3: Spark相比MapReduce的优势？
**A**: 
- **内存计算**: Spark基于内存，MapReduce基于磁盘
- **DAG执行**: Spark支持复杂数据流，MapReduce只支持Map-Reduce
- **编程模型**: Spark提供丰富API，MapReduce编程复杂
- **迭代算法**: Spark天然支持，MapReduce需要多轮作业
- **实时处理**: Spark支持流处理，MapReduce只支持批处理

### Q4: Flink的Exactly-Once语义如何实现？
**A**: 
1. **检查点机制**: 定期保存算子状态快照
2. **两阶段提交**: 对外部系统使用2PC协议
3. **幂等写入**: 支持幂等的Sink连接器
4. **状态恢复**: 失败时从最近检查点恢复
5. **端到端保证**: 从Source到Sink的完整保证

### Q5: HBase适合什么场景？不适合什么场景？
**A**: 
**适合场景**:
- 大数据量的随机读写
- 稀疏数据存储
- 实时数据访问
- 时序数据存储

**不适合场景**:
- 复杂的关联查询
- 小数据量应用
- 强一致性要求
- 频繁的全表扫描

### Q6: 如何优化大数据查询性能？
**A**: 
1. **分区设计**: 合理的分区策略减少扫描数据量
2. **索引优化**: 创建合适的索引加速查询
3. **数据格式**: 使用列式存储格式(Parquet、ORC)
4. **数据压缩**: 减少I/O和存储开销
5. **查询优化**: 谓词下推、列裁剪、JOIN优化
6. **缓存策略**: 合理使用内存缓存
7. **并行度调优**: 调整任务并行度

### Q7: 大数据架构设计需要考虑哪些因素？
**A**: 
- **数据特性**: 数据量、增长速度、数据类型
- **业务需求**: 实时性要求、查询模式、SLA
- **技术选型**: 批处理vs流处理、SQL vs NoSQL
- **成本考虑**: 硬件成本、运维成本、人员成本
- **扩展性**: 水平扩展能力、存储扩展能力
- **可靠性**: 数据容错、服务可用性
- **安全性**: 数据加密、访问控制、审计

### Q8: Lambda架构和Kappa架构的区别？
**A**: 
**Lambda架构**:
- 批处理层 + 流处理层 + 服务层
- 数据双写，保证准确性
- 复杂度高，维护成本大

**Kappa架构**:
- 只有流处理层
- 所有数据当作流处理
- 架构简单，维护容易
- 依赖流处理引擎的可靠性

### Q9: 数据湖和数据仓库的区别？
**A**: 
| 特性 | 数据湖 | 数据仓库 |
|:---|:---|:---|
| **数据结构** | 原始数据，结构化+非结构化 | 结构化数据 |
| **Schema** | Schema-on-Read | Schema-on-Write |
| **存储成本** | 低 | 高 |
| **处理速度** | 慢 | 快 |
| **灵活性** | 高 | 低 |
| **数据质量** | 低 | 高 |

### Q10: 如何保证大数据平台的数据质量？
**A**: 
1. **数据采集**: 源头数据校验和清洗
2. **ETL过程**: 数据转换过程中的质量检查
3. **数据监控**: 实时监控数据质量指标
4. **数据血缘**: 跟踪数据来源和处理过程
5. **异常检测**: 自动检测数据异常和波动
6. **数据治理**: 建立数据质量管理制度
7. **元数据管理**: 完善的元数据管理体系