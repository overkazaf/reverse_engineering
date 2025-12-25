---
title: "Hive 数据仓库"
date: 2025-04-25
weight: 10
---

# Hive 数据仓库

Apache Hive 是基于 Hadoop 的数据仓库工具，可以将结构化的数据文件映射为数据库表，并提供类 SQL 查询功能。

## 目录

1. [Hive 架构](#hive-架构)
2. [数据类型与存储格式](#数据类型与存储格式)
3. [DDL 操作](#ddl-操作)
4. [DML 操作](#dml-操作)
5. [分区与分桶](#分区与分桶)
6. [函数与 UDF](#函数与-udf)
7. [性能优化](#性能优化)
8. [知识要点](#知识要点)

---

## Hive 架构

### 核心组件

```
┌─────────────────────────────────────────────────────────┐
│                      Client                              │
│              (CLI / JDBC / Web UI)                       │
└─────────────────────────┬───────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                      Driver                              │
│    (SQL Parser → Compiler → Optimizer → Executor)        │
└─────────────────────────┬───────────────────────────────┘
                          ↓
┌─────────────┬───────────────────────┬───────────────────┐
│  Metastore  │   Execution Engine    │      HDFS         │
│  (MySQL等)  │  (MR/Tez/Spark)       │   (数据存储)       │
└─────────────┴───────────────────────┴───────────────────┘
```

| 组件                 | 说明                             |
| :------------------- | :------------------------------- |
| **Driver**           | 解析 SQL、生成执行计划、协调执行 |
| **Metastore**        | 存储表结构、分区等元数据         |
| **Execution Engine** | 执行引擎（MapReduce/Tez/Spark）  |

### 工作流程

1. **SQL 解析**: 词法分析 → 语法分析 → 语义分析
2. **逻辑计划**: 生成逻辑执行计划
3. **物理计划**: 转换为 MapReduce/Tez/Spark 任务
4. **执行**: 提交到 Hadoop 集群执行

---

## 数据类型与存储格式

### 基本数据类型

| 类型        | 描述         | 示例                                                    |
| :---------- | :----------- | :------------------------------------------------------ |
| `TINYINT`   | 1 字节整数   | -128 到 127                                             |
| `SMALLINT`  | 2 字节整数   | -32,768 到 32,767                                       |
| `INT`       | 4 字节整数   | -2,147,483,648 到 2,147,483,647                         |
| `BIGINT`    | 8 字节整数   | -9,223,372,036,854,775,808 到 9,223,372,036,854,775,807 |
| `FLOAT`     | 4 字节浮点数 | 3.14159                                                 |
| `DOUBLE`    | 8 字节浮点数 | 3.141592653589793                                       |
| `STRING`    | 字符串       | 'Hello World'                                           |
| `BOOLEAN`   | 布尔值       | TRUE/FALSE                                              |
| `TIMESTAMP` | 时间戳       | '2023-01-01 12:00:00'                                   |
| `DATE`      | 日期         | '2023-01-01'                                            |

### 复杂数据类型

```sql
-- Array
ARRAY<data_type>
-- 示例：ARRAY<STRING>

-- Map
MAP<primitive_type, data_type>
-- 示例：MAP<STRING, INT>

-- 结构体
STRUCT<col_name:data_type [COMMENT col_comment], ...>
-- 示例：STRUCT<name:STRING, age:INT>

-- 联合体
UNIONTYPE<data_type, data_type, ...>
```

### 存储格式对比

| 格式             | 压缩率 | 查询性能 | 写入性能 | 适用场景   |
| :--------------- | :----- | :------- | :------- | :--------- |
| **TextFile**     | 低     | 低       | 高       | 日志导入   |
| **SequenceFile** | 中     | 中       | 中       | 中间数据   |
| **RCFile**       | 高     | 中       | 低       | 列式分析   |
| **ORC**          | 很高   | 很高     | 低       | OLAP 分析  |
| **Parquet**      | 很高   | 很高     | 低       | 跨平台分析 |

---

## DDL 操作

### 数据库操作

```sql
-- 创建数据库
CREATE DATABASE IF NOT EXISTS mydb
COMMENT 'My database'
LOCATION '/user/hive/warehouse/mydb.db';

-- 使用数据库
USE mydb;

-- 显示数据库
SHOW DATABASES;

-- 删除数据库
DROP DATABASE IF EXISTS mydb CASCADE;
```

### 创建表

```sql
-- 创建内部表
CREATE TABLE employee (
    id INT,
    name STRING,
    salary DOUBLE,
    department STRING
)
STORED AS ORC
TBLPROPERTIES ('orc.compress'='SNAPPY');

-- 创建外部表
CREATE EXTERNAL TABLE external_employee (
    name STRING,
    salary DOUBLE,
    department STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/data/employee/';

-- 创建分区表
CREATE TABLE partitioned_employee (
    name STRING,
    salary DOUBLE
)
PARTITIONED BY (department STRING, year INT)
STORED AS ORC;
```

### 修改表

```sql
-- 修改列
ALTER TABLE employee CHANGE salary salary DECIMAL(10,2);

-- 添加列
ALTER TABLE employee ADD COLUMNS (bonus DOUBLE);

-- 添加分区
ALTER TABLE partitioned_employee ADD PARTITION (department='IT', year=2023);

-- 删除分区
ALTER TABLE partitioned_employee DROP PARTITION (department='IT', year=2023);

-- 重命名表
ALTER TABLE employee RENAME TO emp;
```

---

## DML 操作

### 数据插入

```sql
-- 插入数据
INSERT INTO employee VALUES (1, 'John', 5000.0, 'IT');

-- 从查询插入
INSERT INTO employee
SELECT id, name, salary, department
FROM temp_employee;

-- 覆盖插入
INSERT OVERWRITE TABLE employee
SELECT * FROM temp_employee;

-- 分区插入
INSERT INTO partitioned_employee PARTITION(department='IT', year=2023)
SELECT id, name, salary FROM temp_employee;

-- 动态分区插入
SET hive.exec.dynamic.partition=true;
SET hive.exec.dynamic.partition.mode=nonstrict;

INSERT INTO partitioned_employee PARTITION(department, year)
SELECT id, name, salary, department, year FROM temp_employee;
```

### 数据查询

```sql
-- 聚合查询
SELECT department, AVG(salary) as avg_salary
FROM employee
GROUP BY department
HAVING AVG(salary) > 6000;

-- 连接查询
SELECT e.name, d.dept_name
FROM employee e
JOIN department d ON e.department = d.dept_id;

-- 窗口函数
SELECT name, salary,
    ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) as rank
FROM employee;

-- 子查询
SELECT * FROM employee
WHERE salary > (SELECT AVG(salary) FROM employee);
```

---

## 分区与分桶

### 分区操作

```sql
-- 静态分区
INSERT INTO partitioned_employee PARTITION(department='IT', year=2023)
SELECT id, name, salary FROM source_table;

-- 动态分区
INSERT INTO partitioned_employee PARTITION(department, year)
SELECT id, name, salary, department, year FROM source_table;

-- 查询特定分区
SELECT * FROM partitioned_employee
WHERE department='IT' AND year=2023;

-- 显示分区
SHOW PARTITIONS partitioned_employee;
```

### 分桶操作

```sql
-- 创建分桶表
CREATE TABLE bucketed_employee (
    id INT,
    name STRING,
    salary DOUBLE,
    department STRING
)
CLUSTERED BY (id) INTO 4 BUCKETS
STORED AS ORC;

-- 启用分桶
SET hive.enforce.bucketing=true;

-- 插入数据（自动分桶）
INSERT INTO bucketed_employee
SELECT * FROM employee;
```

---

## 函数与 UDF

### 字符串函数

```sql
-- 字符串操作
SELECT
    CONCAT(first_name, ' ', last_name) as full_name,
    UPPER(name) as upper_name,
    LOWER(name) as lower_name,
    LENGTH(name) as name_length,
    SUBSTR(name, 1, 3) as name_prefix,
    TRIM(name) as trimmed_name,
    REGEXP_REPLACE(name, '[0-9]', '') as no_digits
FROM employee;
```

### 日期函数

```sql
-- 日期操作
SELECT
    FROM_UNIXTIME(UNIX_TIMESTAMP()) as current_time,
    YEAR(hire_date) as hire_year,
    MONTH(hire_date) as hire_month,
    DATEDIFF(CURRENT_DATE, hire_date) as days_since_hire,
    DATE_ADD(hire_date, 30) as after_30_days
FROM employee;
```

### 聚合函数

```sql
-- 聚合统计
SELECT
    COUNT(*) as total_count,
    SUM(salary) as total_salary,
    AVG(salary) as avg_salary,
    MAX(salary) as max_salary,
    MIN(salary) as min_salary,
    STDDEV(salary) as salary_stddev
FROM employee;
```

### 自定义 UDF

```java
// MyUpperUDF.java
package com.example.udf;

import org.apache.hadoop.hive.ql.exec.UDF;
import org.apache.hadoop.io.Text;

public class MyUpperUDF extends UDF {
    public Text evaluate(Text input) {
        if (input == null) return null;
        return new Text(input.toString().toUpperCase());
    }
}
```

```sql
-- 注册 UDF
ADD JAR /path/to/my-udf.jar;
CREATE TEMPORARY FUNCTION my_upper AS 'com.example.udf.MyUpperUDF';

-- 使用 UDF
SELECT my_upper(name) FROM employee;
```

---

## 性能优化

### 存储优化

```sql
-- 选择合适的存储格式
CREATE TABLE optimized_table (
    col1 STRING,
    col2 INT
)
STORED AS ORC
TBLPROPERTIES (
    'orc.compress'='SNAPPY',
    'orc.create.index'='true'
);
```

### 查询优化

```sql
-- 推荐：使用分区裁剪
SELECT * FROM partitioned_table
WHERE partition_col = 'value';

-- 避免：全表扫描
SELECT * FROM partitioned_table
WHERE non_partition_col = 'value';

-- 推荐：只查询需要的列
SELECT name, salary FROM employee;

-- 避免：SELECT *
SELECT * FROM employee;
```

### 连接优化

```sql
-- MapJoin（小表广播）
SELECT /*+ MAPJOIN(small_table) */ *
FROM large_table a
JOIN small_table b ON a.key = b.key;

-- 优化连接顺序（大表在前）
SELECT *
FROM large_table a
JOIN medium_table b ON a.key = b.key
JOIN small_table c ON b.key = c.key;
```

### 配置优化

```sql
-- 启用代价优化器
SET hive.cbo.enable=true;

-- 设置合理的 MapReduce 参数
SET mapreduce.job.reduces=10;
SET hive.exec.reducers.bytes.per.reducer=1000000000;

-- 启用并行执行
SET hive.exec.parallel=true;
SET hive.exec.parallel.thread.number=8;

-- 启用向量化执行
SET hive.vectorized.execution.enabled=true;
SET hive.vectorized.execution.reduce.enabled=true;
```

---

## 知识要点

### 1. Hive vs 传统数据库

| 特性         | Hive           | 传统数据库     |
| :----------- | :------------- | :------------- |
| **数据量**   | PB 级          | GB-TB 级       |
| **延迟**     | 高（秒-分钟）  | 低（毫秒）     |
| **ACID**     | 有限支持       | 完全支持       |
| **索引**     | 有限           | 丰富           |
| **扩展性**   | 水平扩展       | 垂直扩展       |
| **适用场景** | 离线分析       | 在线事务       |

### 2. 内部表 vs 外部表

| 特性         | 内部表               | 外部表               |
| :----------- | :------------------- | :------------------- |
| **数据管理** | Hive 管理            | 用户管理             |
| **删除表**   | 删除元数据和数据     | 只删除元数据         |
| **数据位置** | Hive 仓库目录        | 用户指定位置         |
| **使用场景** | 临时数据、中间结果   | 共享数据、外部数据源 |

### 3. 数据倾斜解决方案

```sql
-- 1. 增加 Reduce 任务数
SET mapreduce.job.reduces=100;

-- 2. 启用负载均衡
SET hive.groupby.skewindata=true;

-- 3. 使用随机前缀打散热点 Key
SELECT *
FROM (
    SELECT CONCAT(CAST(RAND() * 100 AS INT), '_', key) as new_key, value
    FROM skewed_table
) a
JOIN small_table b ON SPLIT(a.new_key, '_')[1] = b.key;

-- 4. 使用 MapJoin 避免 Shuffle
SELECT /*+ MAPJOIN(b) */ *
FROM large_table a
JOIN small_table b ON a.key = b.key;
```

### 4. 小文件问题处理

```sql
-- 1. 合并小文件
SET hive.merge.mapfiles=true;
SET hive.merge.mapredfiles=true;
SET hive.merge.size.per.task=256000000;

-- 2. 使用 Concatenate 合并 ORC 文件
ALTER TABLE table_name CONCATENATE;

-- 3. 重新组织数据
INSERT OVERWRITE TABLE new_table
SELECT * FROM old_table;
```

### 5. 性能优化清单

| 优化项       | 方法                        |
| :----------- | :-------------------------- |
| **存储格式** | 使用 ORC/Parquet 列式存储   |
| **压缩**     | 启用 Snappy/LZ4 压缩        |
| **分区**     | 合理设计分区键              |
| **分桶**     | 对大表使用分桶              |
| **索引**     | 创建适当的索引              |
| **缓存**     | 缓存热点数据                |
| **并行度**   | 调整 Map/Reduce 任务数      |
| **资源**     | 合理分配内存和 CPU          |

---

## 相关章节

- [E05: 数据仓库与处理](data_warehousing_and_processing.md)
- [E06: Apache Flink](flink.md)
- [E07: HBase 数据库](hbase.md)
- [E09: Apache Spark](spark.md)
