---
title: "消息队列"
date: 2025-08-09
type: posts
tags: ["大数据", "工程实践", "消息队列"]
weight: 20
---

# 消息队列

消息队列（Message Queue）是分布式系统中实现异步通信、解耦组件的核心中间件，在逆向工程数据管线中扮演着至关重要的角色。

## 消息队列概述

### 什么是消息队列

消息队列是一种进程间或服务间的异步通信机制。生产者（Producer）将消息发送到队列，消费者（Consumer）从队列中取出消息进行处理。两端无需同时在线，也无需知道对方的存在。

```text
┌──────────┐    ┌──────────────────┐    ┌──────────┐
│ Producer │───>│  Message Queue   │───>│ Consumer │
│  生产者  │    │     消息队列      │    │  消费者  │
└──────────┘    └──────────────────┘    └──────────┘
     │                                       │
     │          异步、解耦、削峰               │
     └───────── 无需直接依赖 ─────────────────┘
```

### 为什么需要消息队列

| 能力 | 说明 |
|:---|:---|
| **异步处理** | 耗时操作（反编译、特征提取）放入队列，主流程立即返回 |
| **应用解耦** | 采集端和分析端独立部署、独立扩容 |
| **流量削峰** | 突发大量样本到达时，队列缓冲避免后端过载 |
| **可靠投递** | 消息持久化保证数据不丢失 |
| **广播分发** | 一条样本数据可同时分发给多个分析引擎 |

### 逆向工程 / 数据采集中的典型场景

1. **批量 APK 分析管线** - 爬虫采集 APK 下载链接，推送到队列，多个工作节点并行反编译和特征提取
2. **实时协议抓包** - Frida Hook 抓到的网络请求实时写入队列，后端做协议解析和存储
3. **分布式爬虫调度** - URL 任务分发、去重、优先级排序
4. **样本特征聚合** - 多个分析引擎将结果写入同一队列，汇总到数据仓库

```text
┌─────────────┐     ┌───────────┐     ┌──────────────────┐
│ Frida Hook  │────>│           │────>│ 协议解析 Worker   │
│ 抓包脚本    │     │           │     └──────────────────┘
└─────────────┘     │           │     ┌──────────────────┐
                    │  Message  │────>│ 特征提取 Worker   │
┌─────────────┐     │   Queue   │     └──────────────────┘
│ APK 爬虫    │────>│           │     ┌──────────────────┐
│ 下载器      │     │           │────>│ 存储 Worker       │
└─────────────┘     └───────────┘     └──────────────────┘
```

---

## 主流消息队列对比

### 综合对比表

| 特性 | RabbitMQ | Kafka | Redis Pub/Sub | RocketMQ |
|:---|:---|:---|:---|:---|
| **开发语言** | Erlang | Scala/Java | C | Java |
| **协议** | AMQP | 自定义协议 | RESP | 自定义协议 |
| **吞吐量** | 万级/秒 | 百万级/秒 | 十万级/秒 | 十万级/秒 |
| **延迟** | 微秒级 | 毫秒级 | 微秒级 | 毫秒级 |
| **消息持久化** | 支持 | 支持（默认） | 可选（Stream） | 支持 |
| **消息回溯** | 不支持 | 支持 | Stream 支持 | 支持 |
| **消费模式** | Push/Pull | Pull | Push | Push/Pull |
| **事务消息** | 支持 | 支持 | 不支持 | 支持 |
| **延迟消息** | 插件支持 | 不原生支持 | 不支持 | 原生支持 |
| **管理界面** | 自带 Web UI | 第三方（Kafka UI） | 无 | 自带 Dashboard |
| **适用场景** | 复杂路由、可靠投递 | 大数据流、日志采集 | 轻量级通知 | 电商、金融 |
| **学习曲线** | 中等 | 较高 | 低 | 中等 |

### 性能参考（单机基准测试）

| 指标 | RabbitMQ | Kafka | Redis Stream |
|:---|:---|:---|:---|
| **写入 QPS** | ~20,000 | ~800,000 | ~100,000 |
| **读取 QPS** | ~20,000 | ~1,000,000 | ~100,000 |
| **P99 延迟** | <1ms | ~5ms | <1ms |
| **单消息大小建议** | <1MB | <1MB | <512KB |

> **注意**: 以上数据为典型配置下的参考值，实际性能受硬件、配置、消息大小等因素影响。

---

## RabbitMQ 基础

### 核心概念

```text
┌─────────────────────────────────────────────────────────────┐
│                        RabbitMQ Broker                      │
│                                                             │
│  ┌──────────┐    Binding     ┌─────────┐                   │
│  │ Exchange │──────────────>│  Queue  │──> Consumer 1      │
│  │  交换机  │    RoutingKey  │  队列   │                    │
│  │          │──────┐        └─────────┘                    │
│  └──────────┘      │        ┌─────────┐                    │
│       ↑            └──────>│  Queue  │──> Consumer 2      │
│       │                     │  队列   │                    │
│   Producer                  └─────────┘                    │
└─────────────────────────────────────────────────────────────┘
```

| 概念 | 说明 |
|:---|:---|
| **Exchange（交换机）** | 接收生产者消息，根据规则路由到队列 |
| **Queue（队列）** | 存储消息，等待消费者拉取 |
| **Binding（绑定）** | Exchange 与 Queue 之间的关联规则 |
| **Routing Key** | 消息的路由键，Exchange 据此决定投递目标 |
| **Virtual Host** | 逻辑隔离单元，类似数据库的 schema |

### Exchange 类型

| 类型 | 路由规则 | 典型用途 |
|:---|:---|:---|
| **direct** | 精确匹配 Routing Key | 任务按类型分发 |
| **fanout** | 广播到所有绑定队列 | 通知所有消费者 |
| **topic** | 通配符匹配 Routing Key（`*` 和 `#`） | 灵活的多级路由 |
| **headers** | 根据消息 headers 匹配 | 复杂条件路由 |

### Python pika 基础示例

#### 安装依赖

```bash
pip install pika
```

#### 生产者

```python
import pika
import json

def create_connection():
    """创建 RabbitMQ 连接"""
    credentials = pika.PlainCredentials('guest', 'guest')
    parameters = pika.ConnectionParameters(
        host='localhost',
        port=5672,
        virtual_host='/',
        credentials=credentials,
        heartbeat=600,
        blocked_connection_timeout=300,
    )
    return pika.BlockingConnection(parameters)

def publish_task(task_data: dict):
    """发布分析任务到队列"""
    connection = create_connection()
    channel = connection.channel()

    # 声明交换机和队列
    channel.exchange_declare(
        exchange='re_analysis',
        exchange_type='direct',
        durable=True,
    )
    channel.queue_declare(queue='apk_analysis', durable=True)
    channel.queue_bind(
        queue='apk_analysis',
        exchange='re_analysis',
        routing_key='apk',
    )

    # 发布消息（持久化）
    channel.basic_publish(
        exchange='re_analysis',
        routing_key='apk',
        body=json.dumps(task_data),
        properties=pika.BasicProperties(
            delivery_mode=2,  # 消息持久化
            content_type='application/json',
        ),
    )
    print(f"[x] 已发送任务: {task_data['apk_name']}")
    connection.close()

# 批量发送 APK 分析任务
if __name__ == '__main__':
    tasks = [
        {'apk_name': 'target_v1.0.apk', 'url': 'https://...', 'priority': 'high'},
        {'apk_name': 'target_v2.0.apk', 'url': 'https://...', 'priority': 'normal'},
    ]
    for task in tasks:
        publish_task(task)
```

#### 消费者

```python
import pika
import json
import time

def callback(ch, method, properties, body):
    """处理分析任务"""
    task = json.loads(body)
    print(f"[*] 开始分析: {task['apk_name']}")

    try:
        # 模拟耗时的反编译操作
        time.sleep(5)
        print(f"[✓] 分析完成: {task['apk_name']}")
        # 手动确认消息
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"[!] 分析失败: {e}")
        # 拒绝消息，重新入队
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def start_consumer():
    """启动消费者"""
    connection = create_connection()
    channel = connection.channel()

    channel.queue_declare(queue='apk_analysis', durable=True)
    # 每次只取一条消息，处理完再取下一条
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue='apk_analysis',
        on_message_callback=callback,
        auto_ack=False,  # 手动确认
    )

    print('[*] 等待分析任务，按 Ctrl+C 退出')
    channel.start_consuming()

if __name__ == '__main__':
    start_consumer()
```

### Topic Exchange 模式（多级路由）

```python
import pika
import json

def setup_topic_exchange():
    """为不同类型的逆向任务设置 Topic 路由"""
    connection = create_connection()
    channel = connection.channel()

    channel.exchange_declare(exchange='re_tasks', exchange_type='topic', durable=True)

    # 不同分析队列
    queues = {
        'static_analysis': 'task.static.#',    # 匹配所有静态分析
        'dynamic_analysis': 'task.dynamic.#',   # 匹配所有动态分析
        'all_analysis': 'task.#',               # 匹配所有任务
    }
    for queue_name, binding_key in queues.items():
        channel.queue_declare(queue=queue_name, durable=True)
        channel.queue_bind(
            exchange='re_tasks',
            queue=queue_name,
            routing_key=binding_key,
        )

    # 发布不同类型的任务
    # routing_key='task.static.apk' -> 匹配 static_analysis 和 all_analysis
    channel.basic_publish(
        exchange='re_tasks',
        routing_key='task.static.apk',
        body=json.dumps({'type': 'jadx_decompile', 'target': 'app.apk'}),
    )

    # routing_key='task.dynamic.frida' -> 匹配 dynamic_analysis 和 all_analysis
    channel.basic_publish(
        exchange='re_tasks',
        routing_key='task.dynamic.frida',
        body=json.dumps({'type': 'frida_hook', 'target': 'com.example.app'}),
    )

    connection.close()
```

---

## Kafka 基础

### 核心概念

```text
┌────────────────────────── Kafka Cluster ──────────────────────────┐
│                                                                   │
│  Topic: "apk_samples"                                            │
│  ┌──────────────────────────────────────────┐                    │
│  │ Partition 0: [msg0][msg3][msg6][msg9]... │ ──> Consumer A     │
│  │ Partition 1: [msg1][msg4][msg7][msg10].. │ ──> Consumer B     │
│  │ Partition 2: [msg2][msg5][msg8][msg11].. │ ──> Consumer C     │
│  └──────────────────────────────────────────┘                    │
│                                                                   │
│  Consumer Group: "analysis_group"                                │
│  每个 Partition 只由同组内一个 Consumer 消费                        │
│                                                                   │
│  Broker 1 (Leader P0)    Broker 2 (Leader P1)    Broker 3        │
│  ├── P0 (Leader)         ├── P1 (Leader)         ├── P2 (Leader) │
│  ├── P1 (Replica)        ├── P2 (Replica)        ├── P0 (Replica)│
│  └── P2 (Replica)        └── P0 (Replica)        └── P1 (Replica)│
└───────────────────────────────────────────────────────────────────┘
```

| 概念 | 说明 |
|:---|:---|
| **Topic（主题）** | 消息的逻辑分类，类似数据库中的表 |
| **Partition（分区）** | Topic 的物理分片，实现并行读写 |
| **Offset（偏移量）** | 消息在 Partition 中的唯一序号 |
| **Consumer Group** | 消费者组，组内成员分担 Partition |
| **Broker** | Kafka 服务节点 |
| **Replication** | 分区副本，提供高可用 |

### kafka-python 基础示例

#### 安装依赖

```bash
pip install kafka-python
```

#### 生产者

```python
from kafka import KafkaProducer
import json
import time

def create_producer():
    """创建 Kafka 生产者"""
    return KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        key_serializer=lambda k: k.encode('utf-8') if k else None,
        # 可靠性配置
        acks='all',             # 等待所有副本确认
        retries=3,              # 重试次数
        retry_backoff_ms=500,   # 重试间隔
        # 性能配置
        batch_size=16384,       # 批量发送大小
        linger_ms=10,           # 等待凑批时间
        compression_type='gzip',
    )

def send_apk_samples(producer, samples: list):
    """批量发送 APK 样本信息"""
    for sample in samples:
        future = producer.send(
            topic='apk_samples',
            key=sample['package_name'],  # 同一包名发到同一分区
            value=sample,
        )
        # 异步回调
        future.add_callback(
            lambda metadata: print(
                f"[✓] 发送成功: partition={metadata.partition}, "
                f"offset={metadata.offset}"
            )
        )
        future.add_errback(
            lambda exc: print(f"[!] 发送失败: {exc}")
        )

    producer.flush()  # 确保所有消息发送完成

if __name__ == '__main__':
    producer = create_producer()
    samples = [
        {
            'package_name': 'com.example.app',
            'version': '1.0.0',
            'sha256': 'abc123...',
            'source': 'market_crawler',
            'timestamp': time.time(),
        },
        {
            'package_name': 'com.target.app',
            'version': '2.3.1',
            'sha256': 'def456...',
            'source': 'manual_upload',
            'timestamp': time.time(),
        },
    ]
    send_apk_samples(producer, samples)
    producer.close()
```

#### 消费者

```python
from kafka import KafkaConsumer
import json

def create_consumer(group_id: str):
    """创建 Kafka 消费者"""
    return KafkaConsumer(
        'apk_samples',
        bootstrap_servers=['localhost:9092'],
        group_id=group_id,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        # 偏移量管理
        auto_offset_reset='earliest',  # 从最早消息开始
        enable_auto_commit=False,      # 手动提交偏移量
        # 性能配置
        max_poll_records=100,
        fetch_max_wait_ms=500,
    )

def run_analysis_consumer():
    """运行分析消费者"""
    consumer = create_consumer('analysis_group')

    try:
        for message in consumer:
            sample = message.value
            print(
                f"[*] 收到样本: {sample['package_name']} v{sample['version']}"
                f" | partition={message.partition} offset={message.offset}"
            )

            # 执行分析逻辑
            result = analyze_sample(sample)

            # 手动提交偏移量（确保处理完成后再提交）
            consumer.commit()
            print(f"[✓] 分析完成，已提交 offset")

    except KeyboardInterrupt:
        print("[*] 消费者关闭中...")
    finally:
        consumer.close()

def analyze_sample(sample: dict) -> dict:
    """分析 APK 样本（示例）"""
    return {
        'package_name': sample['package_name'],
        'is_obfuscated': True,
        'permissions': ['INTERNET', 'READ_PHONE_STATE'],
        'native_libs': ['libprotect.so'],
    }

if __name__ == '__main__':
    run_analysis_consumer()
```

#### 多分区并行消费

```python
from kafka import KafkaConsumer, TopicPartition
import threading

def partition_consumer(partition_id: int):
    """为指定分区创建独立消费者"""
    consumer = KafkaConsumer(
        bootstrap_servers=['localhost:9092'],
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        enable_auto_commit=True,
    )

    tp = TopicPartition('apk_samples', partition_id)
    consumer.assign([tp])

    print(f"[*] 消费者已分配 Partition {partition_id}")

    for message in consumer:
        print(f"[P{partition_id}] {message.value['package_name']}")

# 为每个分区启动一个线程
threads = []
for i in range(3):
    t = threading.Thread(target=partition_consumer, args=(i,))
    t.daemon = True
    t.start()
    threads.append(t)
```

---

## Redis 消息方案

Redis 提供了三种实现消息队列的方式，各有特点。

### 方案对比

| 特性 | List（列表队列） | Pub/Sub | Stream |
|:---|:---|:---|:---|
| **持久化** | 支持（RDB/AOF） | 不支持 | 支持 |
| **消费者组** | 不支持 | 不支持 | 支持 |
| **消息确认** | 手动实现 | 无 | XACK |
| **消息回溯** | 不支持 | 不支持 | 支持 |
| **阻塞读取** | BRPOP | 订阅阻塞 | XREAD BLOCK |
| **适用场景** | 简单任务队列 | 实时通知/广播 | 完整消息队列 |

### List 队列（最简单方案）

```python
import redis
import json
import time

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# === 生产者 ===
def push_task(queue_name: str, task: dict):
    """推送任务到 List 队列"""
    r.lpush(queue_name, json.dumps(task))

# === 消费者 ===
def consume_tasks(queue_name: str, timeout: int = 0):
    """阻塞式消费任务"""
    while True:
        # BRPOP: 阻塞式右弹出，超时返回 None
        result = r.brpop(queue_name, timeout=timeout)
        if result:
            _, raw = result
            task = json.loads(raw)
            yield task

# === 可靠队列（RPOPLPUSH 模式） ===
def reliable_consume(source: str, processing: str):
    """
    从 source 取出消息，同时放入 processing 队列。
    处理成功后从 processing 删除；失败则可重新入队。
    """
    raw = r.rpoplpush(source, processing)
    if raw:
        task = json.loads(raw)
        try:
            process_task(task)
            # 处理成功，从 processing 队列删除
            r.lrem(processing, 1, raw)
        except Exception:
            # 处理失败，从 processing 移回 source
            r.rpoplpush(processing, source)

# 使用示例
if __name__ == '__main__':
    push_task('hook_tasks', {'target': 'com.example.app', 'script': 'hook_ssl.js'})

    for task in consume_tasks('hook_tasks', timeout=5):
        print(f"处理任务: {task}")
```

### Pub/Sub（发布/订阅）

```python
import redis
import json
import threading

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# === 发布者 ===
def publish_event(channel: str, event: dict):
    """发布事件"""
    r.publish(channel, json.dumps(event))

# === 订阅者 ===
def subscribe_events(channels: list):
    """订阅事件"""
    pubsub = r.pubsub()
    pubsub.subscribe(*channels)

    for message in pubsub.listen():
        if message['type'] == 'message':
            event = json.loads(message['data'])
            yield event

# 模式订阅（通配符）
def pattern_subscribe(pattern: str):
    """使用通配符订阅"""
    pubsub = r.pubsub()
    pubsub.psubscribe(pattern)

    for message in pubsub.listen():
        if message['type'] == 'pmessage':
            channel = message['channel']
            event = json.loads(message['data'])
            print(f"[{channel}] {event}")

# 使用示例
if __name__ == '__main__':
    # 订阅所有分析相关频道
    # pattern_subscribe('analysis.*')

    # 发布 Hook 结果事件
    publish_event('analysis.hook_result', {
        'package': 'com.example.app',
        'function': 'encrypt',
        'args': ['plaintext'],
        'return': 'ciphertext_base64...',
    })
```

### Stream（推荐方案）

Redis 5.0 引入的 Stream 是最完善的消息队列方案，支持消费者组、消息确认、消息回溯。

```python
import redis
import json
import time

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# === 生产者 ===
def add_to_stream(stream: str, data: dict):
    """向 Stream 添加消息"""
    msg_id = r.xadd(stream, data, maxlen=10000)  # 限制最大长度
    print(f"[✓] 消息 ID: {msg_id}")
    return msg_id

# === 创建消费者组 ===
def create_consumer_group(stream: str, group: str):
    """创建消费者组"""
    try:
        r.xgroup_create(stream, group, id='0', mkstream=True)
        print(f"[✓] 消费者组 {group} 已创建")
    except redis.exceptions.ResponseError as e:
        if 'BUSYGROUP' in str(e):
            print(f"[*] 消费者组 {group} 已存在")
        else:
            raise

# === 消费者 ===
def stream_consumer(stream: str, group: str, consumer_name: str):
    """消费者组模式消费"""
    while True:
        # 读取新消息
        messages = r.xreadgroup(
            groupname=group,
            consumername=consumer_name,
            streams={stream: '>'},  # '>' 表示只读取新消息
            count=10,
            block=5000,  # 阻塞 5 秒
        )

        if not messages:
            continue

        for stream_name, stream_messages in messages:
            for msg_id, fields in stream_messages:
                print(f"[{consumer_name}] 处理: {msg_id} -> {fields}")

                # 处理完成后确认
                r.xack(stream, group, msg_id)

# === 处理未确认消息（故障恢复） ===
def claim_pending_messages(stream: str, group: str, consumer: str,
                           min_idle_time: int = 60000):
    """认领超时未确认的消息"""
    pending = r.xpending_range(stream, group, '-', '+', count=10)
    for entry in pending:
        msg_id = entry['message_id']
        idle = entry['time_since_delivered']
        if idle > min_idle_time:
            claimed = r.xclaim(stream, group, consumer, min_idle_time, [msg_id])
            print(f"[*] 已认领超时消息: {claimed}")

# 使用示例
if __name__ == '__main__':
    STREAM = 'hook_results'
    GROUP = 'analysis_group'

    create_consumer_group(STREAM, GROUP)

    # 生产者：写入 Hook 抓取结果
    add_to_stream(STREAM, {
        'package': 'com.example.app',
        'method': 'javax.crypto.Cipher.doFinal',
        'input': 'aGVsbG8=',
        'output': 'ZW5jcnlwdGVk',
        'timestamp': str(time.time()),
    })

    # 消费者：处理结果
    stream_consumer(STREAM, GROUP, 'worker-1')
```

---

## 在逆向工程中的应用

### 场景一：批量 APK 自动化分析

```text
┌──────────────┐    ┌──────────┐    ┌─────────────────┐    ┌──────────┐
│ 应用市场爬虫  │───>│  Kafka   │───>│ 分析 Worker 集群 │───>│  Kafka   │
│ 定时抓取新版本│    │ (样本队列)│    │ JADX + Frida    │    │ (结果队列)│
└──────────────┘    └──────────┘    └─────────────────┘    └──────────┘
                                                                │
                                                                ↓
                                                          ┌──────────┐
                                                          │ ES / DB  │
                                                          │ 结果存储  │
                                                          └──────────┘
```

```python
"""
完整示例：APK 批量分析管线
- 生产者：爬虫发现新版 APK
- 消费者：反编译 + 特征提取
- 结果：写入结果队列供下游消费
"""
from kafka import KafkaProducer, KafkaConsumer
import json
import subprocess
import hashlib

# --- 生产者：爬虫端 ---
class ApkCrawlerProducer:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=['localhost:9092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        )

    def on_new_apk_found(self, apk_info: dict):
        """发现新 APK 时调用"""
        self.producer.send('apk_tasks', value=apk_info)
        self.producer.flush()

# --- 消费者：分析端 ---
class AnalysisWorker:
    def __init__(self, worker_id: str):
        self.worker_id = worker_id
        self.consumer = KafkaConsumer(
            'apk_tasks',
            bootstrap_servers=['localhost:9092'],
            group_id='analysis_workers',
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        )
        self.result_producer = KafkaProducer(
            bootstrap_servers=['localhost:9092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        )

    def run(self):
        for message in self.consumer:
            task = message.value
            print(f"[Worker-{self.worker_id}] 分析: {task['package_name']}")

            result = self.analyze(task)
            # 结果写入下游队列
            self.result_producer.send('analysis_results', value=result)
            self.result_producer.flush()
            self.consumer.commit()

    def analyze(self, task: dict) -> dict:
        """执行分析（示意）"""
        return {
            'package_name': task['package_name'],
            'worker': self.worker_id,
            'obfuscation': 'proguard',
            'native_libs': ['libsec.so'],
            'suspicious_apis': [
                'Landroid/telephony/TelephonyManager;->getDeviceId',
                'Ljavax/crypto/Cipher;->getInstance',
            ],
        }
```

### 场景二：Frida Hook 实时数据管线

```python
"""
Frida Hook 结果实时采集与分析
- Frida 脚本 Hook 关键函数
- Hook 结果通过消息队列实时传输
- 后端实时解析和存储
"""
import frida
import redis
import json
import time

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Frida 脚本
HOOK_SCRIPT = """
Java.perform(function() {
    var Cipher = Java.use('javax.crypto.Cipher');

    Cipher.doFinal.overload('[B').implementation = function(input) {
        var result = this.doFinal(input);

        // 将 Hook 结果发送到 Python 端
        send({
            type: 'crypto',
            algorithm: this.getAlgorithm(),
            input: Array.from(input),
            output: Array.from(result),
            timestamp: Date.now()
        });

        return result;
    };
});
"""

def on_message(message, data):
    """Frida 消息回调 -> 写入 Redis Stream"""
    if message['type'] == 'send':
        payload = message['payload']
        r.xadd('frida_hooks', {
            'type': payload['type'],
            'algorithm': payload.get('algorithm', ''),
            'input_hex': bytes(payload['input']).hex(),
            'output_hex': bytes(payload['output']).hex(),
            'timestamp': str(payload['timestamp']),
        }, maxlen=50000)

def start_hook(package_name: str):
    """启动 Frida Hook 并将结果写入消息队列"""
    device = frida.get_usb_device()
    session = device.attach(package_name)
    script = session.create_script(HOOK_SCRIPT)
    script.on('message', on_message)
    script.load()

    print(f"[*] Hook 已启动: {package_name}")
    print(f"[*] 结果写入 Redis Stream: frida_hooks")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        session.detach()
```

### 场景三：分布式爬虫 URL 调度

```python
"""
基于 RabbitMQ 的分布式爬虫调度器
- 优先级队列：高优先级 URL 先处理
- 去重：基于 Redis Set 去重
- 重试：失败的 URL 重新入队
"""
import pika
import redis
import json
import hashlib

r = redis.Redis(host='localhost', port=6379, db=0)

class UrlScheduler:
    def __init__(self):
        connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost')
        )
        self.channel = connection.channel()

        # 声明优先级队列（最大优先级 10）
        self.channel.queue_declare(
            queue='url_queue',
            durable=True,
            arguments={'x-max-priority': 10},
        )

    def add_url(self, url: str, priority: int = 5, meta: dict = None):
        """添加 URL 到队列（自动去重）"""
        url_hash = hashlib.md5(url.encode()).hexdigest()

        # Redis Set 去重
        if r.sadd('crawled_urls', url_hash) == 0:
            return False  # 已存在

        task = {'url': url, 'priority': priority, 'meta': meta or {}}
        self.channel.basic_publish(
            exchange='',
            routing_key='url_queue',
            body=json.dumps(task),
            properties=pika.BasicProperties(
                delivery_mode=2,
                priority=priority,
            ),
        )
        return True

    def get_stats(self) -> dict:
        """获取队列统计"""
        q = self.channel.queue_declare(queue='url_queue', passive=True)
        return {
            'pending': q.method.message_count,
            'crawled_total': r.scard('crawled_urls'),
        }
```

---

## 架构模式

### 模式一：生产者-消费者（Point-to-Point）

最基础的模式，一条消息只被一个消费者处理。

```text
Producer ──> [Queue] ──> Consumer

多消费者竞争消费（负载均衡）:

Producer ──> [Queue] ──> Consumer A
                    ├──> Consumer B
                    └──> Consumer C
```

适用场景：任务分发、工作队列。

```python
# RabbitMQ 工作队列 - 自动负载均衡
# 多个 Worker 绑定同一队列，RabbitMQ 自动轮询分发
channel.basic_qos(prefetch_count=1)  # 每次只取一条，处理完再取
channel.basic_consume(queue='task_queue', on_message_callback=callback)
```

### 模式二：发布-订阅（Publish-Subscribe）

一条消息被所有订阅者接收。

```text
                    ┌──> [Queue A] ──> Subscriber A (静态分析)
Publisher ──> [Exchange: fanout]
                    └──> [Queue B] ──> Subscriber B (动态分析)

一份样本同时进入静态分析和动态分析管线
```

适用场景：事件广播、多管线并行处理。

```python
# RabbitMQ Fanout 广播
channel.exchange_declare(exchange='sample_events', exchange_type='fanout')

# 每个订阅者创建自己的临时队列
result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue
channel.queue_bind(exchange='sample_events', queue=queue_name)
```

### 模式三：请求-应答（Request-Reply）

生产者发送请求，等待消费者返回结果。

```text
┌──────────┐  Request   ┌───────┐  Request   ┌──────────┐
│  Client  │──────────>│ Queue │──────────>│  Worker  │
│          │<──────────│       │<──────────│          │
└──────────┘  Reply     └───────┘  Reply     └──────────┘
              (via callback queue)
```

```python
import pika
import uuid
import json

class RpcClient:
    """RPC 客户端：发送分析请求并等待结果"""
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost')
        )
        self.channel = self.connection.channel()

        # 创建回调队列
        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue
        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self._on_response,
            auto_ack=True,
        )
        self.responses = {}

    def _on_response(self, ch, method, props, body):
        self.responses[props.correlation_id] = json.loads(body)

    def analyze(self, sample: dict, timeout: int = 30) -> dict:
        """发送分析请求并等待结果"""
        corr_id = str(uuid.uuid4())

        self.channel.basic_publish(
            exchange='',
            routing_key='rpc_analysis',
            body=json.dumps(sample),
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=corr_id,
            ),
        )

        # 等待响应
        start = time.time()
        while corr_id not in self.responses:
            self.connection.process_data_events(time_limit=1)
            if time.time() - start > timeout:
                raise TimeoutError("分析超时")

        return self.responses.pop(corr_id)
```

---

## 部署与监控

### Docker Compose 一键部署

```yaml
# docker-compose.yml
version: '3.8'

services:
  # --- RabbitMQ ---
  rabbitmq:
    image: rabbitmq:3-management
    container_name: rabbitmq
    ports:
      - "5672:5672"    # AMQP
      - "15672:15672"  # Web 管理界面
    environment:
      RABBITMQ_DEFAULT_USER: admin
      RABBITMQ_DEFAULT_PASS: admin123
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
    restart: unless-stopped

  # --- Kafka ---
  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    container_name: zookeeper
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000

  kafka:
    image: confluentinc/cp-kafka:7.5.0
    container_name: kafka
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_LOG_RETENTION_HOURS: 168  # 7 天
      KAFKA_LOG_SEGMENT_BYTES: 1073741824
    volumes:
      - kafka_data:/var/lib/kafka/data

  # --- Kafka UI ---
  kafka-ui:
    image: provectuslabs/kafka-ui:latest
    container_name: kafka-ui
    depends_on:
      - kafka
    ports:
      - "8080:8080"
    environment:
      KAFKA_CLUSTERS_0_NAME: local
      KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS: kafka:9092
      KAFKA_CLUSTERS_0_ZOOKEEPER: zookeeper:2181

  # --- Redis ---
  redis:
    image: redis:7-alpine
    container_name: redis
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data

volumes:
  rabbitmq_data:
  kafka_data:
  redis_data:
```

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看 Kafka 日志
docker-compose logs -f kafka

# 停止并清理
docker-compose down -v
```

### 监控工具

| 消息队列 | 监控方案 | 说明 |
|:---|:---|:---|
| **RabbitMQ** | 自带 Management UI | http://localhost:15672 |
| **Kafka** | Kafka UI / Kafdrop | 查看 Topic、消费者组、Lag |
| **Redis** | RedisInsight / redis-cli | `INFO` 命令查看统计 |
| **通用** | Prometheus + Grafana | 采集 Exporter 指标，统一大盘 |

### Python 监控脚本示例

```python
"""
消息队列健康检查脚本
"""
import redis
import pika
from kafka.admin import KafkaAdminClient

def check_redis(host='localhost', port=6379) -> dict:
    """检查 Redis 状态"""
    r = redis.Redis(host=host, port=port)
    info = r.info()
    return {
        'status': 'ok',
        'connected_clients': info['connected_clients'],
        'used_memory_human': info['used_memory_human'],
        'total_commands_processed': info['total_commands_processed'],
    }

def check_rabbitmq(host='localhost', port=5672) -> dict:
    """检查 RabbitMQ 状态"""
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host, port=port)
        )
        connection.close()
        return {'status': 'ok'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def check_kafka(bootstrap_servers='localhost:9092') -> dict:
    """检查 Kafka 状态"""
    try:
        admin = KafkaAdminClient(bootstrap_servers=bootstrap_servers)
        topics = admin.list_topics()
        admin.close()
        return {'status': 'ok', 'topics': topics}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

if __name__ == '__main__':
    print("Redis:", check_redis())
    print("RabbitMQ:", check_rabbitmq())
    print("Kafka:", check_kafka())
```

---

## 选型建议

### 决策矩阵

根据项目需求，从以下维度评估选型：

| 需求维度 | RabbitMQ | Kafka | Redis Stream |
|:---|:---|:---|:---|
| **吞吐量 > 50万/秒** | -- | ++ | + |
| **延迟 < 1ms** | ++ | - | ++ |
| **消息持久化** | + | ++ | + |
| **消息回溯/重放** | - | ++ | + |
| **复杂路由规则** | ++ | - | - |
| **消费者组** | + | ++ | + |
| **运维复杂度低** | + | - | ++ |
| **已有 Redis 基础设施** | - | - | ++ |
| **大数据生态集成** | - | ++ | - |

> `++` 非常适合 | `+` 适合 | `-` 不太适合 | `--` 不推荐

### 按场景推荐

```text
需要消息回溯/大数据量？
├── 是 → Kafka
│       适合：日志采集、APK 样本流、大规模爬虫数据
└── 否
    ├── 需要复杂路由？
    │   ├── 是 → RabbitMQ
    │   │       适合：多类型任务分发、优先级队列、RPC 模式
    │   └── 否
    │       ├── 项目已用 Redis？
    │       │   ├── 是 → Redis Stream
    │       │   │       适合：轻量级任务队列、实时通知、Frida 数据管线
    │       │   └── 否 → RabbitMQ（通用性最好）
    │       └──
    └──
```

### 逆向工程项目典型选型

| 项目类型 | 推荐方案 | 理由 |
|:---|:---|:---|
| **个人工具/小团队** | Redis Stream | 无需额外部署，Redis 通常已有 |
| **Frida Hook 实时采集** | Redis Stream | 低延迟，数据量适中 |
| **批量 APK 分析平台** | Kafka | 高吞吐，支持回溯重分析 |
| **分布式爬虫系统** | RabbitMQ | 优先级队列、灵活路由 |
| **企业级安全分析平台** | Kafka + RabbitMQ | Kafka 做数据总线，RabbitMQ 做任务调度 |
| **临时脚本/PoC** | Redis List | 最简单，几行代码即可 |

### 混合架构示例

大型逆向工程平台通常采用混合方案：

```text
┌──────────────────────────────────────────────────────────────────┐
│                      混合消息队列架构                              │
│                                                                  │
│  ┌─────────┐         ┌───────────┐         ┌──────────────┐     │
│  │ 爬虫集群 │──────>│   Kafka    │──────>│ Flink / Spark │     │
│  │ 数据采集 │  高吞吐 │  数据总线  │  流处理  │  实时分析     │     │
│  └─────────┘         └───────────┘         └──────────────┘     │
│                            │                                     │
│                            ↓                                     │
│  ┌─────────┐         ┌───────────┐         ┌──────────────┐     │
│  │ 管理后台 │──────>│ RabbitMQ  │──────>│ 分析 Worker   │     │
│  │ 任务下发 │  路由   │  任务调度  │  分发    │ JADX+Frida   │     │
│  └─────────┘         └───────────┘         └──────────────┘     │
│                                                   │              │
│                                                   ↓              │
│  ┌─────────┐         ┌───────────┐         ┌──────────────┐     │
│  │ 前端展示 │<──────│   Redis   │<──────│ 结果汇总      │     │
│  │ 实时推送 │  低延迟 │  Stream   │  写入    │ 入库/通知     │     │
│  └─────────┘         └───────────┘         └──────────────┘     │
└──────────────────────────────────────────────────────────────────┘
```

每层选用最适合的消息队列：

- **Kafka** - 数据总线层，承载高吞吐的原始数据流
- **RabbitMQ** - 任务调度层，提供灵活的路由和优先级管理
- **Redis Stream** - 结果推送层，低延迟实时通知前端
