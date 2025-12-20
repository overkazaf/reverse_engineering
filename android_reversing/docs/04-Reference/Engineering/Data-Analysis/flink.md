# Apache Flink 实时流处理

Apache Flink 是一个分布式流处理框架，专为低延迟、高吞吐量的实时数据处理而设计。

## 目录

1. [**Flink 架构**](#flink-架构)
2. [**核心概念**](#核心概念)
3. [**DataStream API**](#datastream-api)
4. [**状态管理**](#状态管理)
5. [**时间与窗口**](#时间与窗口)
6. [**容错机制**](#容错机制)
7. [**性能调优**](#性能调优)
8. [**面试要点**](#面试要点)

---

## Flink 架构

## # 集群架构

```
├── ResourceManager
└── JobMaster
↓
TaskManager1 TaskManager2 TaskManager3
├── Task Slot1 ├── Task Slot1 ├── Task Slot1
├── Task Slot2 ├── Task Slot2 ├── Task Slot2
└── Task Slot3 └── Task Slot3 └── Task Slot3

```

| **TaskManager** | 执行具体任务，管理内存和网络 |
| **Dispatcher** | 接收作业提交，启动 JobMaster |
| **ResourceManager** | 管理 TaskManager 资源 |
| **JobMaster** | 管理单个作业的执行 |

## # 运行时架构

```
Operator1 → Operator2 → Operator3

```

```java
StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

DataStream<String> stream = env
.socketTextStream("localhost", 9999)
.flatMap(new Tokenizer())
.keyBy(value -> value.f0)
.window(TumblingProcessingTimeWindows.of(Time.seconds(5)))
.sum(1);

env.execute("Word Count");

```

```
DataStream<Integer> intStream;

// 2. 元组类型
DataStream<Tuple2<String, Integer>> tupleStream;

// 3. POJO 类型
public class WordCount {
public String word;
public int count;
// constructors, getters, setters
}
DataStream<WordCount> pojoStream;

// 4. Row 类型（动态）
DataStream<Row> rowStream;

```

StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

// 1. Create from collection
DataStream<String> fromCollection = env.fromCollection(Arrays.asList("a", "b", "c"));

// 2. 从文件系统
DataStream<String> fromFile = env.readTextFile("path/to/file");

// 3. 从 Kafka
Properties props = new Properties();
props.setProperty("bootstrap.servers", "localhost:9092");
props.setProperty("group.id", "test");

DataStream<String> fromKafka = env.addSource(
new FlinkKafkaConsumer<>("topic", new SimpleStringSchema(), props));

// 4. 自定义数据源
DataStream<String> customSource = env.addSource(new CustomSourceFunction());

public class CustomSourceFunction implements SourceFunction<String> {
private volatile boolean running = true;

@Override
public void run(SourceContext<String> ctx) throws Exception {
while (running) {
ctx.collect("data-" + System.currentTimeMillis());
Thread.sleep(1000);
}
}

@Override
public void cancel() {
running = false;
}
}

```
DataStream<String> mapped = input.map(String::toUpperCase);

// 2. FlatMap - 一对多Convert
DataStream<String> flatMapped = input.flatMap(
(String line, Collector<String> out) -> {
for (String word : line.split(" ")) {
out.collect(word);
}
});

// 3. Filter - Filter
DataStream<String> filtered = input.filter(s -> s.startsWith("error"));

// 4. KeyBy - Group
KeyedStream<Tuple2<String, Integer>, String> keyed =
tupleStream.keyBy(value -> value.f0);

// 5. Reduce - Aggregate
DataStream<Tuple2<String, Integer>> reduced =
keyed.reduce((a, b) -> new Tuple2<>(a.f0, a.f1 + b.f1));

// 6. Aggregate - 自定义聚合
DataStream<Double> aggregated = keyed
.aggregate(new AverageAggregate());

public class AverageAggregate implements AggregateFunction<Tuple2<String, Integer>, Tuple2<Long, Long>, Double> {
@Override
public Tuple2<Long, Long> createAccumulator() {
return new Tuple2<>(0L, 0L);
}

@Override
public Tuple2<Long, Long> add(Tuple2<String, Integer> value, Tuple2<Long, Long> accumulator) {
return new Tuple2<>(accumulator.f0 + value.f1, accumulator.f1 + 1L);
}

@Override
public Double getResult(Tuple2<Long, Long> accumulator) {
return ((double) accumulator.f0) / accumulator.f1;
}

@Override
public Tuple2<Long, Long> merge(Tuple2<Long, Long> a, Tuple2<Long, Long> b) {
return new Tuple2<>(a.f0 + b.f0, a.f1 + b.f1);
}
}

```

// 2. 写入文件
stream.writeAsText("path/to/output");

// 3. 写入 Kafka
Properties props = new Properties();
props.setProperty("bootstrap.servers", "localhost:9092");

stream.addSink(new FlinkKafkaProducer<>("output-topic", new SimpleStringSchema(), props));

// 4. 写入数据库
stream.addSink(new CustomSinkFunction());

public class CustomSinkFunction extends RichSinkFunction<String> {
private Connection connection;

@Override
public void open(Configuration parameters) throws Exception {
// 初始化数据库连接
connection = DriverManager.getConnection("jdbc:mysql://localhost:3306/test", "user", "password");
}

@Override
public void invoke(String value, Context context) throws Exception {
// 执行插入操作
PreparedStatement stmt = connection.prepareStatement("INSERT INTO table VALUES (?)");
stmt.setString(1, value);
stmt.executeUpdate();
}

@Override
public void close() throws Exception {
if (connection != null) {
connection.close();
}
}
}

````

```java
public class StatefulMap extends RichMapFunction<Tuple2<String, Integer>, Tuple2<String, Integer>> {
private ValueState<Integer> sumState;

@Override
public void open(Configuration config) {
ValueStateDescriptor<Integer> descriptor =
new ValueStateDescriptor<>("sum", Integer.class);
sumState = getRuntimeContext().getState(descriptor);
}

@Override
public Tuple2<String, Integer> map(Tuple2<String, Integer> input) throws Exception {
Integer currentSum = sumState.value();
if (currentSum == null) {
currentSum = 0;
}
currentSum += input.f1;
sumState.update(currentSum);

return new Tuple2<>(input.f0, currentSum);
}
}

````

private ListState<String> checkpointedState;

@Override
public void snapshotState(FunctionSnapshotContext context) throws Exception {
checkpointedState.clear();
for (String element : bufferedElements) {
checkpointedState.add(element);
}
}

@Override
public void initializeState(FunctionInitializationContext context) throws Exception {
ListStateDescriptor<String> descriptor =
new ListStateDescriptor<>("buffered-elements", String.class);

checkpointedState = context.getOperatorStateStore().getListState(descriptor);

if (context.isRestored()) {
for (String element : checkpointedState.get()) {
bufferedElements.add(element);
}
}
}
}

```

// 2. FsStateBackend (生产推荐)
env.setStateBackend(new FsStateBackend("hdfs://namenode:port/flink-checkpoints"));

// 3. RocksDBStateBackend (大状态)
env.setStateBackend(new RocksDBStateBackend("hdfs://namenode:port/flink-checkpoints"));

// 配置
env.enableCheckpointing(60000); // 60 秒 checkpoint 一次
env.getCheckpointConfig().setCheckpointingMode(CheckpointingMode.EXACTLY_ONCE);
env.getCheckpointConfig().setMinPauseBetweenCheckpoints(30000);
env.getCheckpointConfig().setCheckpointTimeout(600000);

```

// 1. Processing Time (处理时间)
env.setStreamTimeCharacteristic(TimeCharacteristic.ProcessingTime);

// 2. Event Time (事件时间)
env.setStreamTimeCharacteristic(TimeCharacteristic.EventTime);

// 3. Watermark (水位线)
stream.assignTimestampsAndWatermarks(
WatermarkStrategy.<Event>forBoundedOutOfOrderness(Duration.ofSeconds(10))
.withTimestampAssigner((event, timestamp) -> event.getTimestamp()));

```
stream.keyBy(...)
.window(TumblingEventTimeWindows.of(Time.minutes(5)))
.sum(1);

// 滑动窗口 (Sliding Window)
stream.keyBy(...)
.window(SlidingEventTimeWindows.of(Time.minutes(10), Time.minutes(2)))
.sum(1);

// 会话窗口 (Session Window)
stream.keyBy(...)
.window(EventTimeSessionWindows.withGap(Time.minutes(30)))
.sum(1);

```

.countWindow(100)
.sum(1);

// 滑动计数窗口
stream.keyBy(...)
.countWindow(100, 10)
.sum(1);

```
.window(TumblingEventTimeWindows.of(Time.minutes(5)))
.reduce(new SumReduceFunction());

// 2. AggregateFunction
stream.keyBy(...)
.window(TumblingEventTimeWindows.of(Time.minutes(5)))
.aggregate(new AverageAggregateFunction());

// 3. ProcessWindowFunction
stream.keyBy(...)
.window(TumblingEventTimeWindows.of(Time.minutes(5)))
.process(new MyProcessWindowFunction());

public class MyProcessWindowFunction extends ProcessWindowFunction<Tuple2<String, Integer>, String, String, TimeWindow> {
@Override
public void process(String key, Context context, Iterable<Tuple2<String, Integer>> elements, Collector<String> out) {
int count = 0;
for (Tuple2<String, Integer> element : elements) {
count++;
}
out.collect("Window: " + context.window() + " count: " + count);
}
}

```

// EnabledCheckpoint
env.enableCheckpointing(60000, CheckpointingMode.EXACTLY_ONCE);

// ConfigCheckpoint
CheckpointConfig config = env.getCheckpointConfig();
config.setMinPauseBetweenCheckpoints(30000);
config.setCheckpointTimeout(600000);
config.setMaxConcurrentCheckpoints(1);
config.enableExternalizedCheckpoints(ExternalizedCheckpointCleanup.RETAIN_ON_CANCELLATION);

// 重启 Strategy
env.setRestartStrategy(RestartStrategies.fixedDelayRestart(
3, // 重启次数
Time.of(10, TimeUnit.SECONDS) // 重启间隔
));

env.setRestartStrategy(RestartStrategies.exponentialDelayRestart(
Time.milliseconds(1),
Time.milliseconds(1000),

1. 2, // 指数基数
   Time.milliseconds(5000), // 最大 Latency
2. 1 // 抖动因子
   ));

```

# 从 Savepoint 恢复
bin/flink run -s <savepointPath> <jarFile>

# DeleteSavepoint
bin/flink savepoint -d <savepointPath>

```

// 1. 全局并行度
env.setParallelism(4);

// 2. 算子并行度
stream.map(...).setParallelism(2);

// 3. Slot 共享组
stream.map(...).slotSharingGroup("group1");

```
taskmanager.memory.flink.size: 3g
taskmanager.memory.network.fraction: 0.1
taskmanager.memory.managed.fraction: 0.4

```

// 批量传输
env.setBufferTimeout(100);

```
backend.setPredefinedOptions(PredefinedOptions.SPINNING_DISK_OPTIMIZED);
backend.setDbStoragePath("/tmp/rocksdb");
env.setStateBackend(backend);

```

|:---|:---|:---|
| **处理模型** | 真正的流处理 | 微批处理 |
| **延迟** | 毫秒级 | 秒级 |
| **吞吐量** | 高 | 很高 |
| **状态管理** | 原生支持 | 有限支持 |
| **容错** | Checkpoint | RDD lineage |
| **反压** | 原生支持 | 有限支持 |

## # 2. 反压 (Backpressure) 机制

- **问题**: 下游处理速度跟不上上游产生速度

- **Flink 解决方案**:

1. **信用机制**: 基于信用的流量控制
2. **缓冲池**: 动态调整缓冲池大小
3. **网络栈**: TCP 流量控制
4. **监控**: Web UI 显示反压情况

## # 3. Exactly-Once 语义保证

- **组件**:
    1. **Source**: 可重放（如 Kafka offset）
    2. **内部处理**: Checkpoint 机制
    3. **Sink**: 两阶段提交或幂等写入

```java
// 两阶段提交 Sink 示例
public class TwoPhaseCommitSink extends TwoPhaseCommitSinkFunction<String, Transaction, Void> {
@Override
protected Transaction beginTransaction() throws Exception {
return new Transaction();
}

@Override
protected void invoke(Transaction transaction, String value, Context context) throws Exception {
transaction.add(value);
}

@Override
protected void preCommit(Transaction transaction) throws Exception {
transaction.flush();
}

@Override
protected void commit(Transaction transaction) {
transaction.commit();
}

@Override
protected void abort(Transaction transaction) {
transaction.rollback();
}
}

```

1. **Watermark**: 事件时间窗口
2. **Processing Time**: 处理时间窗口
3. **元素计数**: 计数窗口
4. **自定义**: 用户定义的触发器

## # 5. 状态管理最佳实践

1. **选择合适的状态类型**: ValueState vs ListState vs MapState
2. **设置状态 TTL**: 避免状态无限增长
3. **选择合适的状态后端**: 内存 vs 文件系统 vs RocksDB
4. **状态大小监控**: 及时发现状态膨胀

````java
// SetStatusTTL
StateTtlConfig ttlConfig = StateTtlConfig
.newBuilder(Time.days(7))
.setUpdateType(StateTtlConfig.UpdateType.OnCreateAndWrite)
.setStateVisibility(StateTtlConfig.StateVisibility.NeverReturnExpired)
.build();

ValueStateDescriptor<String> descriptor = new ValueStateDescriptor<>("my-state", String.class);
descriptor.enableTimeToLive(ttlConfig);


1. **检测故障**: JobManager监控TaskManager心跳
2. **重启任务**: 根据重启策略重启失败任务
3. **恢复状态**: 从最近的 Checkpoint 恢复状态
4. **重放数据**: Source 重放 Checkpoint 之后的数据
5. **继续处理**: 恢复正常处理流程
    ```
````
