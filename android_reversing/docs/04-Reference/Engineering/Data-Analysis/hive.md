# Hive 数据仓库

Apache Hive 是基于 Hadoop 的数据仓库工具，可以将结构化的数据文件映射为数据库表，并提供类 SQL 查询功能。

## 目录

1. [**Hive 架构**](#hive-架构)
2. [**数据类型与存储格式**](#数据类型与存储格式)
3. [**DDL 操作**](#ddl-操作)
4. [**DML 操作**](#dml-操作)
5. [**分区与分桶**](#分区与分桶)
6. [**函数与 UDF**](#函数与udf)
7. [**性能优化**](#性能优化)
8. [**面试要点**](#面试要点)

---

## Hive 架构

## # 核心组件

```
Metastore (Metadata storage)
↓
HDFS (Data storage) + MapReduce/Tez/Spark (Compute engine)

```

| **Driver** | 解析 SQL、生成执行计划、协调执行 |
| **Execution Engine** | 执行引擎（MapReduce/Tez/Spark） |

## # 工作流程

1. **SQL 解析**: 词法分析 → 语法分析 → 语义分析
2. **逻辑计划**: 生成逻辑执行计划
3. **物理计划**: 转换为 MapReduce/Tez/Spark 任务
4. **执行**: 提交到 Hadoop 集群执行

---

## 数据类型与存储格式

## # 基本数据类型

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

## # 复杂数据类型

```sql
- - Array
ARRAY<data_type>
- - 示例：ARRAY<STRING>

- - Map
MAP<primitive_type, data_type>
- - 示例：MAP<STRING, INT>

- - 结构体
STRUCT<col_name:data_type [COMMENT col_comment], ...>
- - 示例：STRUCT<name:STRING, age:INT>

- - 联合体
UNIONTYPE<data_type, data_type, ...>

```

| **SequenceFile** | 中 | 中 | 中 | 中间数据 |
| **RCFile** | 高 | 中 | 低 | 列式分析 |
| **ORC** | 很高 | 很高 | 低 | OLAP 分析 |
| **Parquet** | 很高 | 很高 | 低 | 跨平台分析 |

---

## DDL 操作

## # 数据库操作

```sql
- - 创建数据库
CREATE DATABASE IF NOT EXISTS mydb
COMMENT 'My database'
LOCATION '/user/hive/warehouse/mydb.db';

- - 使用数据库
USE mydb;

- - 显示数据库
SHOW DATABASES;

- - 删除数据库
DROP DATABASE IF EXISTS mydb CASCADE;

```

id INT,
name STRING,
salary DOUBLE,
department STRING
)
STORED AS ORC
TBLPROPERTIES ('orc.compress'='SNAPPY');

```
name STRING,
salary DOUBLE,
department STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/data/employee/';

```

name STRING,
salary DOUBLE
)
PARTITIONED BY (department STRING, year INT)
STORED AS ORC;

```

- - 修改列
ALTER TABLE employee CHANGE salary salary DECIMAL(10,2);

- - 添加分区
ALTER TABLE partitioned_employee ADD PARTITION (department='IT', year=2023);

- - 删除分区
ALTER TABLE partitioned_employee DROP PARTITION (department='IT', year=2023);

- - 重命名表
ALTER TABLE employee RENAME TO emp;

```

- - 插入数据
    INSERT INTO employee VALUES (1, 'John', 5000.0, 'IT');

- - 从查询插入
    INSERT INTO employee
    SELECT id, name, salary, department
    FROM temp_employee;

- - 覆盖插入
    INSERT OVERWRITE TABLE employee
    SELECT \* FROM temp_employee;

- - 分区插入
    INSERT INTO partitioned_employee PARTITION(department='IT', year=2023)
    SELECT id, name, salary FROM temp_employee;

- - 动态分区插入
    SET hive.exec.dynamic.partition=true;
    SET hive.exec.dynamic.partition.mode=nonstrict;

INSERT INTO partitioned_employee PARTITION(department, year)
SELECT id, name, salary, department, year FROM temp_employee;

```

- - 聚合查询
SELECT department, AVG(salary) as avg_salary
FROM employee
GROUP BY department
HAVING AVG(salary) > 6000;

- - 连接查询
SELECT e.name, d.dept_name
FROM employee e
JOIN department d ON e.department = d.dept_id;

- - 窗口函数
SELECT name, salary,
ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) as rank
FROM employee;

```

```sql
- - 静态分区
INSERT INTO partitioned_employee PARTITION(department='IT', year=2023)
SELECT id, name, salary FROM source_table;

- - 动态分区
INSERT INTO partitioned_employee PARTITION(department, year)
SELECT id, name, salary, department, year FROM source_table;

- - 查询特定分区
SELECT * FROM partitioned_employee
WHERE department='IT' AND year=2023;

```

CREATE TABLE bucketed_employee (
id INT,
name STRING,
salary DOUBLE,
department STRING
)
CLUSTERED BY (id) INTO 4 BUCKETS
STORED AS ORC;

- - 启用分桶
    SET hive.enforce.bucketing=true;

- - 插入数据（自动分桶）
    INSERT INTO bucketed_employee
    SELECT \* FROM employee;

````

```sql
- - 字符串操作
SELECT
CONCAT(first_name, ' ', last_name) as full_name,
UPPER(name) as upper_name,
LENGTH(name) as name_length,
SUBSTR(name, 1, 3) as name_prefix
FROM employee;

````

FROM_UNIXTIME(UNIX_TIMESTAMP()) as current_time,
YEAR(hire_date) as hire_year,
DATEDIFF(CURRENT_DATE, hire_date) as days_since_hire
FROM employee;

```
COUNT(*) as total_count,
SUM(salary) as total_salary,
AVG(salary) as avg_salary,
MAX(salary) as max_salary,
MIN(salary) as min_salary,
STDDEV(salary) as salary_stddev
FROM employee;

```

public String evaluate(String input) {
if (input == null) return null;
return input.toUpperCase();
}
}

```

- - 使用 UDF
SELECT my_upper(name) FROM employee;

```

- - 选择合适的存储格式
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
SELECT * FROM partitioned_table
WHERE partition_col = 'value';

- - 避免：全表扫描
SELECT * FROM partitioned_table
WHERE non_partition_col = 'value';

```

- - 避免：SELECT _
    SELECT _ FROM employee;

```
FROM employee e
JOIN department d ON e.dept_id = d.id
WHERE e.salary > 5000;

```

- - 启用代价优化器
    SET hive.cbo.enable=true;

- - 设置合理的 MapReduce 参数
    SET mapreduce.job.reduces=10;
    SET hive.exec.reducers.bytes.per.reducer=1000000000;

- - 启用并行执行
    SET hive.exec.parallel=true;
    SET hive.exec.parallel.thread.number=8;

````
|:---|:---|:---|
| **数据量** | PB级 | GB-TB级 |
| **延迟** | 高（秒-分钟） | 低（毫秒） |
| **ACID** | 有限支持 | 完全支持 |
| **索引** | 有限 | 丰富 |
| **扩展性** | 水平扩展 | 垂直扩展 |
| **适用场景** | 离线分析 | 在线事务 |

## # 2. 内部表 vs 外部表

| 特性 | 内部表 | 外部表 |
|:---|:---|:---|
| **数据管理** | Hive管理 | 用户管理 |
| **删除表** | 删除元数据和数据 | 只删除元数据 |
| **数据位置** | Hive仓库目录 | 用户指定位置 |
| **使用场景** | 临时数据、中间结果 | 共享数据、外部数据源 |

## # 3. 数据倾斜解决方案

```sql
- - 1. 增加 Reduce 任务数
SET mapreduce.job.reduces=100;

- - 2. 启用负载均衡
SET hive.groupby.skewindata=true;

- - 3. 使用随机前缀
SELECT /*+ MAPJOIN(b) */ *
FROM (
SELECT CONCAT(CAST(RAND() * 100 AS INT), '_', key) as new_key, value
FROM skewed_table
) a
JOIN small_table b ON a.key = b.key;

````

- - 1. 合并小文件
       SET hive.merge.mapfiles=true;
       SET hive.merge.mapredfiles=true;
       SET hive.merge.size.per.task=256000000;

- - 2. 使用 Concatenate
       ALTER TABLE table_name CONCATENATE;

- - 3. 重新组织数据
       INSERT OVERWRITE TABLE new_table
       SELECT \* FROM old_table;

```
4. **分桶**: 对大表使用分桶
5. **索引**: 创建适当的索引
6. **缓存**: 缓存热点数据
7. **并行度**: 调整Map/Reduce任务数
8. **资源**: 合理分配内存和CPU
```
