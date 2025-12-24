---
title: "Apache Spark 大数据处理"
date: 2025-12-25
weight: 10
---

# Apache Spark 大数据处理

Apache Spark 是一个统一的大数据处理引擎，支持批处理、流处理、机器学习和图计算。

## 目录

1. [Spark 架构](#spark-架构)
2. [RDD 编程](#rdd-编程)
3. [DataFrame & Dataset](#dataframe--dataset)
4. [Spark SQL](#spark-sql)
5. [Spark Streaming](#spark-streaming)
6. [性能优化](#性能优化)
7. [知识要点](#知识要点)

---

## Spark 架构

### 集群架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Driver Program                            │
│                    (SparkContext)                           │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│              Cluster Manager (YARN/Mesos/Standalone)        │
└──────┬──────────────────┬──────────────────────┬────────────┘
       │                  │                      │
┌──────▼──────┐   ┌───────▼──────┐   ┌──────────▼─────────┐
│ Worker Node1│   │ Worker Node2 │   │    Worker Node3    │
├─────────────┤   ├──────────────┤   ├────────────────────┤
│ Executor1   │   │ Executor1    │   │    Executor1       │
│ ├── Task1   │   │ ├── Task1    │   │    ├── Task1       │
│ └── Task2   │   │ └── Task2    │   │    └── Task2       │
│ Cache       │   │ Cache        │   │    Cache           │
└─────────────┘   └──────────────┘   └────────────────────┘
```

### 核心组件

| 组件 | 说明 |
|------|------|
| **SparkContext** | Spark 程序入口，协调集群资源 |
| **Cluster Manager** | 集群资源管理器 |
| **Worker Node** | 集群中的工作节点 |
| **Executor** | 运行在 Worker 上的进程，执行 Task |
| **Task** | 最小的工作单元 |

### 运行流程

1. **Driver 创建 SparkContext**
2. **资源申请**: 向 Cluster Manager 申请资源
3. **任务调度**: DAG Scheduler 将 Job 分解为 Stage 和 Task
4. **任务分发**: Task Scheduler 将 Task 分发到 Executor
5. **任务执行**: Executor 执行 Task 并返回结果

---

## RDD 编程

### RDD 基本概念

**RDD (Resilient Distributed Dataset)**: 弹性分布式数据集

#### 特性

- **不可变性**: RDD 一旦创建不可修改
- **分区性**: 数据分布在多个分区
- **容错性**: 通过血统(Lineage)恢复丢失数据
- **惰性求值**: 只有在 Action 操作时才会执行

### RDD 创建

```scala
import org.apache.spark.{SparkConf, SparkContext}

val conf = new SparkConf().setAppName("SparkExample").setMaster("local[*]")
val sc = new SparkContext(conf)

// 1. 从集合创建
val rdd1 = sc.parallelize(List(1, 2, 3, 4, 5))
val rdd2 = sc.makeRDD(Array("a", "b", "c"))

// 2. 从外部存储创建
val rdd3 = sc.textFile("hdfs://path/to/file")
val rdd4 = sc.wholeTextFiles("hdfs://path/to/directory")

// 3. 从其他 RDD 创建
val rdd5 = rdd1.map(_ * 2)
```

### Transformation 操作

```scala
val data = sc.parallelize(List(1, 2, 3, 4, 5))

// 1. map - 一对一转换
val mapped = data.map(_ * 2)

// 2. filter - 过滤
val filtered = data.filter(_ % 2 == 0)

// 3. flatMap - 一对多转换
val words = sc.parallelize(List("hello world", "spark scala"))
val flatMapped = words.flatMap(_.split(" "))

// 4. distinct - 去重
val distincted = data.distinct()

// 5. union - 合并
val rdd1 = sc.parallelize(List(1, 2, 3))
val rdd2 = sc.parallelize(List(4, 5, 6))
val unioned = rdd1.union(rdd2)

// 6. intersection - 交集
val intersected = rdd1.intersection(rdd2)

// 7. groupByKey - 按键分组
val pairs = sc.parallelize(List(("a", 1), ("b", 2), ("a", 3)))
val grouped = pairs.groupByKey()

// 8. reduceByKey - 按键聚合
val reduced = pairs.reduceByKey(_ + _)

// 9. sortByKey - 按键排序
val sorted = pairs.sortByKey()

// 10. join - 连接
val rdd3 = sc.parallelize(List(("a", "x"), ("b", "y")))
val joined = pairs.join(rdd3)
```

### Action 操作

```scala
val data = sc.parallelize(List(1, 2, 3, 4, 5))

// 1. collect - 收集所有元素到 Driver
val collected = data.collect()

// 2. count - 计算元素数
val count = data.count()

// 3. first - 获取第一个元素
val first = data.first()

// 4. take - 获取前 n 个元素
val taken = data.take(3)

// 5. reduce - 聚合所有元素
val sum = data.reduce(_ + _)

// 6. fold - 带初始值的聚合
val folded = data.fold(0)(_ + _)

// 7. aggregate - 复杂聚合
val (totalSum, totalCount) = data.aggregate((0, 0))(
  (acc, value) => (acc._1 + value, acc._2 + 1),
  (acc1, acc2) => (acc1._1 + acc2._1, acc1._2 + acc2._2)
)

// 8. foreach - 对每个元素执行操作
data.foreach(println)

// 9. saveAsTextFile - 保存为文本文件
data.saveAsTextFile("hdfs://path/to/output")
```

---

## DataFrame & Dataset

### DataFrame 创建

```scala
import org.apache.spark.sql.{SparkSession, DataFrame}

val spark = SparkSession.builder()
  .appName("DataFrameExample")
  .master("local[*]")
  .getOrCreate()

import spark.implicits._

// 1. 从 RDD 创建 DataFrame
case class Person(name: String, age: Int, city: String)
val peopleRDD = spark.sparkContext.parallelize(List(
  Person("Alice", 25, "NYC"),
  Person("Bob", 30, "LA"),
  Person("Charlie", 35, "Chicago")
))
val peopleDF = peopleRDD.toDF()

// 2. 从文件创建 DataFrame
val df = spark.read
  .option("header", "true")
  .option("inferSchema", "true")
  .csv("path/to/file.csv")

// 3. 从 JSON 创建
val jsonDF = spark.read.json("path/to/file.json")
```

### DataFrame 操作

```scala
// 1. 查看数据
df.show()
df.describe().show()

// 2. 选择列
df.select("name", "age").show()
df.select($"name", $"age" + 1).show()

// 3. 过滤
df.filter($"age" > 25).show()
df.where("age > 25").show()

// 4. 分组聚合
df.groupBy("city").count().show()
df.groupBy("city").agg(avg("age"), max("age")).show()

// 5. 排序
df.orderBy($"age".desc).show()
df.sort("name").show()

// 6. 连接
val df2 = spark.createDataFrame(List(
  ("NYC", "NY"),
  ("LA", "CA"),
  ("Chicago", "IL")
)).toDF("city", "state")

df.join(df2, "city").show()

// 7. 窗口函数
import org.apache.spark.sql.expressions.Window
import org.apache.spark.sql.functions._

val windowSpec = Window.partitionBy("city").orderBy($"age".desc)
df.withColumn("rank", row_number().over(windowSpec)).show()
```

### Dataset 类型安全

```scala
// 创建 Dataset
val ds: Dataset[Person] = df.as[Person]

// 类型安全操作
val adults = ds.filter(_.age >= 18)
val names = ds.map(_.name)

// 编译时类型检查
// ds.filter(_.salary > 1000) // 编译错误，Person 没有 salary 字段
```

---

## Spark SQL

### SQL 查询

```scala
// 注册临时视图
df.createOrReplaceTempView("people")

// SQL 查询
val result = spark.sql("""
  SELECT city, COUNT(*) as count, AVG(age) as avg_age
  FROM people
  WHERE age > 20
  GROUP BY city
  ORDER BY count DESC
""")

result.show()

// 复杂查询
val complexQuery = spark.sql("""
  SELECT name, age, city,
    ROW_NUMBER() OVER (PARTITION BY city ORDER BY age DESC) as rank
  FROM people
""")
```

### 表管理

```scala
// 列出所有表
spark.catalog.listTables().show()

// 缓存表
spark.catalog.cacheTable("people")
spark.catalog.uncacheTable("people")

// 删除临时视图
spark.catalog.dropTempView("people")
```

---

## Spark Streaming

### DStream 编程

```scala
import org.apache.spark.streaming.{StreamingContext, Seconds}

val ssc = new StreamingContext(spark.sparkContext, Seconds(1))

// 1. 从 socket 创建流
val lines = ssc.socketTextStream("localhost", 9999)

// 2. 转换操作
val words = lines.flatMap(_.split(" "))
val pairs = words.map(word => (word, 1))
val wordCounts = pairs.reduceByKey(_ + _)

// 3. 输出操作
wordCounts.print()

// 启动流处理
ssc.start()
ssc.awaitTermination()
```

### 窗口操作

```scala
// 窗口聚合
val windowedWordCounts = pairs.reduceByKeyAndWindow(
  (a: Int, b: Int) => a + b,     // reduce 函数
  (a: Int, b: Int) => a - b,     // inverse reduce 函数
  Seconds(30),                   // 窗口长度
  Seconds(10)                    // 滑动间隔
)

// 状态更新
def updateFunction(newValues: Seq[Int], runningCount: Option[Int]): Option[Int] = {
  val newCount = newValues.sum + runningCount.getOrElse(0)
  Some(newCount)
}

val stateDstream = pairs.updateStateByKey[Int](updateFunction)
```

### Structured Streaming

```scala
// 创建流式 DataFrame
val df = spark
  .readStream
  .format("socket")
  .option("host", "localhost")
  .option("port", 9999)
  .load()

// 处理流数据
val words = df.as[String].flatMap(_.split(" "))
val wordCounts = words.groupBy("value").count()

// 输出结果
val query = wordCounts.writeStream
  .outputMode("complete")
  .format("console")
  .trigger(Trigger.ProcessingTime("10 seconds"))
  .start()

query.awaitTermination()
```

---

## 性能优化

### 缓存策略

```scala
import org.apache.spark.storage.StorageLevel

// 1. 基本缓存
val cachedRDD = rdd.cache()  // MEMORY_ONLY
val persistedRDD = rdd.persist(StorageLevel.MEMORY_AND_DISK)

// 2. DataFrame 缓存
df.cache()
df.persist(StorageLevel.MEMORY_AND_DISK_SER)

// 3. 不同存储级别
StorageLevel.MEMORY_ONLY          // 仅内存
StorageLevel.MEMORY_AND_DISK      // 内存+磁盘
StorageLevel.MEMORY_ONLY_SER      // 内存序列化
StorageLevel.DISK_ONLY            // 仅磁盘
StorageLevel.MEMORY_AND_DISK_2    // 内存+磁盘，2副本
```

### 分区优化

```scala
// 1. 调整分区数
val repartitioned = rdd.repartition(4)  // 增加分区
val coalesced = rdd.coalesce(2)         // 减少分区

// 2. 自定义分区器
class CustomPartitioner(numPartitions: Int) extends Partitioner {
  override def numPartitions: Int = numPartitions

  override def getPartition(key: Any): Int = {
    key.hashCode() % numPartitions
  }
}

val partitioned = pairs.partitionBy(new CustomPartitioner(4))

// 3. 数据本地性
val localData = sc.textFile("hdfs://path", minPartitions = 4)
```

### 广播变量与累加器

```scala
// 1. 广播变量
val broadcastVar = sc.broadcast(List(1, 2, 3))
val result = rdd.map(x => x * broadcastVar.value.sum)

// 2. 累加器
val accum = sc.longAccumulator("My Accumulator")
rdd.foreach(x => accum.add(x))
println(s"Accumulator value: ${accum.value}")

// 3. 自定义累加器
class VectorAccumulator extends AccumulatorV2[Vector, Vector] {
  private var _sum = Vector.zeros(3)

  override def isZero: Boolean = _sum == Vector.zeros(3)
  override def copy(): VectorAccumulator = new VectorAccumulator
  override def reset(): Unit = _sum = Vector.zeros(3)
  override def add(v: Vector): Unit = _sum += v
  override def merge(other: AccumulatorV2[Vector, Vector]): Unit = {
    _sum += other.asInstanceOf[VectorAccumulator]._sum
  }
  override def value: Vector = _sum
}
```

### SQL 优化

```scala
// 1. 启用 CBO (基于成本的优化)
spark.conf.set("spark.sql.cbo.enabled", "true")

// 2. 启用代码生成
spark.conf.set("spark.sql.codegen.wholeStage", "true")

// 3. 广播 Join 优化
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")

// 4. 谓词下推
val optimizedDF = df.filter($"age" > 18)  // Filter 下推到数据源
```

---

## 知识要点

### 1. RDD vs DataFrame vs Dataset

| 特性 | RDD | DataFrame | Dataset |
|------|-----|-----------|---------|
| **类型安全** | 编译时 | 运行时 | 编译时 |
| **性能优化** | 无 | Catalyst优化器 | Catalyst优化器 |
| **API风格** | 函数式 | 关系型 | 类型安全的关系型 |
| **内存使用** | Java对象 | 二进制格式 | 二进制格式 |
| **序列化** | Java序列化 | 自定义编码器 | 自定义编码器 |

### 2. Spark 内存管理

#### 内存分配

```
Spark 内存 = 堆内存 × spark.memory.fraction (默认 0.6)
├── 存储内存 (Storage) × 0.5
│   └── 用于缓存 RDD、广播变量
├── 执行内存 (Execution) × 0.5
│   └── 用于 Shuffle、Join、Sort、Aggregation
└── 用户内存 (剩余部分)
    └── 用于用户自定义数据结构
```

#### 配置示例

```bash
# 1. Executor 内存
--executor-memory 4g

# 2. 内存分配比例
--conf spark.memory.fraction=0.6
--conf spark.memory.storageFraction=0.5

# 3. 序列化
--conf spark.serializer=org.apache.spark.serializer.KryoSerializer
```

### 3. Shuffle 优化

```scala
// 1. 预分区
val partitioned = rdd.partitionBy(new HashPartitioner(100))

// 2. 调整并行度
spark.conf.set("spark.sql.shuffle.partitions", "400")

// 3. 启用外部排序
spark.conf.set("spark.sql.execution.useObjectHashAggregateExec", "false")
```

### 4. 数据倾斜处理

```scala
val skewedRDD = sc.parallelize(List(("key1", 1), ("key1", 1), /* 很多 key1 */, ("key2", 1)))

// 加盐处理
val saltedRDD = skewedRDD.map { case (key, value) =>
  val salt = Random.nextInt(10)
  (s"${key}_$salt", value)
}

val result = saltedRDD.reduceByKey(_ + _)
  .map { case (saltedKey, value) =>
    val originalKey = saltedKey.split("_")(0)
    (originalKey, value)
  }
  .reduceByKey(_ + _)
```

### 5. 两阶段聚合

```scala
// 第一阶段：局部聚合
val localAgg = rdd.mapPartitions { iter =>
  iter.toList.groupBy(_._1).map { case (key, values) =>
    (key, values.map(_._2).sum)
  }.toIterator
}

// 第二阶段：全局聚合
val globalAgg = localAgg.reduceByKey(_ + _)
```

### 6. 资源配置建议

```bash
# CPU 密集型
--num-executors 10 --executor-cores 5 --executor-memory 2g

# 内存密集型
--num-executors 5 --executor-cores 2 --executor-memory 8g

# 平衡型
--num-executors 15 --executor-cores 3 --executor-memory 4g
```

### 7. 最佳实践

```scala
// 推荐
rdd.filter(...).map(...)  // 先过滤再转换

// 避免
rdd.map(...).filter(...)  // 先转换再过滤

// 减少 Shuffle
val broadcastVar = sc.broadcast(smallData)
largeRDD.map(x => x + broadcastVar.value)  // 使用广播变量代替 join
```

### 8. 数据存储格式

```scala
// 使用列式存储
df.write
  .mode("overwrite")
  .option("compression", "snappy")
  .parquet("path/to/output")  // Parquet 格式

// 分区存储
df.write
  .partitionBy("year", "month")
  .parquet("path/to/partitioned/output")
```
