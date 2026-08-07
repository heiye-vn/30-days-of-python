# RabbitMQ 消息队列完全指南

> 面向 Agent 开发者的实战教程 —— 覆盖原理、Python（pika / aio-pika）、Node.js（amqplib）、可靠性设计与 Agent 架构实战。
>
> 编写日期：2026-08-07

---

## 目录

1. 为什么需要消息队列
2. RabbitMQ 核心模型
3. 环境搭建（Windows / Docker）
4. Python 实战（pika）
5. Python 异步实战（aio-pika）
6. Node.js 实战（amqplib）
7. 可靠性保障：消息不丢、不重、不乱
8. Agent 开发中的消息队列实战架构
9. 最佳实践与常见坑清单
10. 速查表

---

## 一、为什么需要消息队列

### 1.1 从一个真实场景说起

假设你在开发一个 Agent 应用：用户提交一个任务「帮我调研三家竞品并生成报告」，这个任务需要调用多次 LLM、跑爬虫、生成文档，整个过程可能要 2~5 分钟。

如果直接在 HTTP 请求里同步处理：

- 用户浏览器要干等几分钟，连接随时可能超时断开；
- 高峰期 100 个用户同时提交，你的服务要同时撑住 100 个 LLM 长连接，内存和并发直接爆炸；
- 一旦服务重启或崩溃，正在执行的任务全部丢失，没有任何痕迹。

引入消息队列后，架构变成：

```
用户请求 → API 服务（毫秒级返回"已受理"）→ 任务写入 RabbitMQ 队列
                                                    ↓
                                        Agent Worker 池（N 个消费者）
                                        按自己的能力取任务、慢慢执行
                                                    ↓
                                        结果写入结果队列 / 回调通知用户
```

这就是消息队列要解决的三件事。

### 1.2 消息队列的三大作用

**异步（Asynchronous）**
耗时操作不阻塞主流程。API 收到请求后立即把任务丢进队列返回，Worker 在后台慢慢消费。对 Agent 场景尤其重要——LLM 调用慢且贵，绝不能让用户请求线程陪跑。

**解耦（Decoupling）**
生产者只管发消息，不需要知道谁在消费、有几个消费者、消费者挂了怎么办。上游 API 服务和下游 Agent Worker 可以独立开发、独立部署、独立扩缩容。将来要新增一个「审计日志消费者」或「监控消费者」，只需要多订阅一个队列，主流程代码一行不改。

**削峰（Peak Shaving）**
突发流量先堆积在队列里，Worker 按自己的处理能力匀速消费。比如运营推送导致瞬间涌入 1 万个 Agent 任务，队列先兜住，10 个 Worker 每分钟消化 500 个，20 分钟处理完——系统不会被打垮。

### 1.3 消息队列在 Agent 开发中的典型位置

- **任务队列**：用户任务 → 队列 → Agent Worker 池（最常见的用法）
- **多 Agent 协作总线**：Agent A 完成规划后发布事件，Agent B/C 订阅并接力（发布/订阅模式）
- **工具调用异步化**：Agent 调用耗时工具（搜索、代码执行）时走队列，避免阻塞推理循环
- **结果/日志收集**：所有 Worker 的执行日志、token 用量统一发到日志队列，集中统计
- **限流阀**：`prefetch` + 固定数量 Worker 天然形成并发上限，防止 LLM API 限流

### 1.4 RabbitMQ 与其他 MQ 的对比

| 维度 | RabbitMQ | Kafka | Redis（Stream/List） | RocketMQ |
|---|---|---|---|---|
| 模型 | Broker 推送，消费即删 | 日志追加，可回溯重放 | 轻量队列/流 | 高吞吐分布式队列 |
| 吞吐量 | 万级 QPS | 百万级 QPS | 十万级 QPS | 十万级 QPS |
| 路由能力 | 极强（4 种 Exchange） | 弱（Topic 分区） | 弱 | 中 |
| 消息回溯 | 不支持（消费即确认删除） | 天然支持 | Stream 支持 | 支持 |
| 延迟 | 微秒~毫秒级 | 毫秒级 | 微秒级 | 毫秒级 |
| 运维复杂度 | 低 | 高 | 极低 | 中 |
| 适合场景 | 业务路由、任务分发、RPC | 日志流、事件溯源、大数据 | 简单队列、缓存旁路 | 电商级大流量 |

**选型经验**：Agent 应用的任务分发、多 Agent 事件协作，RabbitMQ 的路由灵活性（尤其 topic exchange）非常合适，生态成熟、文档友好，是入门和生产都稳妥的选择。如果后期需要「回放三天前的所有 Agent 事件做训练数据」这类需求，再考虑 Kafka 或给 RabbitMQ 配事件溯源插件。

---

## 二、RabbitMQ 核心模型

### 2.1 整体架构

RabbitMQ 的消息流转路径和你直觉里的「生产者 → 队列 → 消费者」不太一样，**中间多了一个 Exchange**：

```
Producer ──publish──▶ Exchange ──按路由规则分发──▶ Queue(s) ──consume──▶ Consumer
                        │                           ▲
                        └────── Binding 绑定 ────────┘
```

关键认知：**生产者从来不直接把消息发给队列**，而是发给 Exchange；Exchange 根据类型和路由规则决定消息进入哪些队列（可能是 0 个、1 个或多个）。

### 2.2 关键术语

| 术语 | 含义 |
|---|---|
| **Broker** | RabbitMQ 服务器本身 |
| **Virtual Host（vhost）** | 逻辑隔离单元，类似数据库的 database。权限、exchange、queue 都在 vhost 内隔离。默认是 `/` |
| **Connection** | 一条 TCP 物理连接，建立成本高 |
| **Channel** | 连接内的轻量逻辑通道。收发消息都走 Channel，一条 Connection 可开几百个 Channel。**日常编程只跟 Channel 打交道** |
| **Producer** | 消息生产者 |
| **Consumer** | 消息消费者 |
| **Exchange** | 交换器，负责路由 |
| **Queue** | 消息存储的实体，消息最终在这里排队 |
| **Binding** | Exchange 与 Queue 之间的绑定关系 |
| **Routing Key** | 消息自带的路由键（生产时指定） |
| **Binding Key** | 绑定时指定的匹配模式 |
| **Message** | 消息体（bytes）+ 一组属性（properties） |

**为什么要有 Channel？** TCP 连接的建立和销毁很昂贵（握手、认证、OS 资源）。Channel 复用一条 TCP 连接做多路复用，开几千个 Channel 几乎没有成本。最佳实践：**应用持少量 Connection，按需复用 Channel**。

### 2.3 四种 Exchange 类型

这是 RabbitMQ 最核心的知识点，务必吃透。

**① direct（直连交换器）—— 精确匹配**

消息的 routing key 必须与 binding key **完全相等**才路由。

```
routing_key="error" ──▶ binding_key="error" 的队列 ✅
routing_key="error" ──▶ binding_key="info"  的队列 ❌
```

一个队列可以绑定多个 key（比如同时绑 error 和 warning）。用途：按日志级别分发、按任务类型分发给不同 Worker 池。

**② fanout（扇出交换器）—— 广播**

无视 routing key，把消息**广播给所有绑定的队列**。用途：事件通知所有订阅方（多 Agent 协作的事件总线常用它）。

**③ topic（主题交换器）—— 模式匹配（最灵活）**

routing key 必须是「点分词」形式，如 `agent.planner.done`。binding key 支持两个通配符：

- `*`（星号）：恰好匹配**一个**单词
- `#`（井号）：匹配**零个或多个**单词

```
binding "kern.*"        匹配 "kern.info"，不匹配 "kern.info.deep"
binding "*.critical"    匹配 "kern.critical"，不匹配 "a.b.critical"？
                        —— 注意：* 只匹配一个词，"a.b.critical" 是三个词，不匹配
binding "kern.#"        匹配 "kern"、"kern.info"、"kern.info.deep"
binding "#"             匹配一切（退化为 fanout）
```

用途：多级事件体系。Agent 系统里 `agent.{角色}.{事件}` 这种命名法配合 topic exchange 极其好用。

**④ headers（头交换器）—— 按消息头匹配**

不看 routing key，根据消息 headers 属性的键值对匹配（binding 时指定 `x-match=all` 或 `any`）。性能差、用得少，了解即可。

**特殊存在：默认交换器（Default Exchange）**

每个新连接都隐含一个名为 `""`（空字符串）的 direct 交换器。所有队列自动绑定到它，binding key = 队列名。所以你 `publish(exchange='', routing_key='hello')` 时消息会精准进入名为 hello 的队列——Hello World 示例用的就是它。

### 2.4 消息生命周期与确认机制

一条消息可能「死」在很多环节，理解生命周期才能设计出可靠系统：

```
Producer 发送
   │ ① 发送失败（网络断开）→ 生产者需感知：publisher confirms
   ▼
Exchange 路由
   │ ② 路由不到任何队列 → 消息被丢弃（mandatory=true 时可退回）
   ▼
Queue 存储
   │ ③ Broker 宕机且未持久化 → 消息丢失（需持久化/仲裁队列）
   ▼
Consumer 接收（unacked 状态）
   │ ④ 消费者处理到一半崩溃 → ？
   ▼
ack / nack 决定结局
```

**ack 机制是核心：**

- `auto_ack=True`（自动确认）：消息一投递给消费者就立即从队列删除。消费者随后崩溃 → **消息丢失**。只适合可丢弃的消息。
- 手动确认：消息投递后处于 **unacked（未确认）** 状态，直到消费者显式调用：
  - `basic_ack` —— 确认完成，消息删除；
  - `basic_nack(requeue=True)` —— 拒绝并要求**重新入队**（会回到队列重新投递，注意可能死循环）；
  - `basic_nack(requeue=False)` —— 拒绝且不回队，消息被丢弃；**如果队列配置了死信交换器（DLX），消息会被路由到死信队列**——这是处理失败消息的正道。

**另一个重要细节**：消费者崩溃时，TCP 连接断开，RabbitMQ 会自动把它名下所有 unacked 消息重新投递给其他消费者——所以手动 ack 模式下任务不会丢。

### 2.5 QoS 与 prefetch（公平分发）

默认情况下 RabbitMQ 会尽可能快地把消息推给消费者（round-robin 轮询），不管消费者忙不忙。`basic_qos(prefetch_count=N)` 限制**每个消费者最多同时持有 N 条未确认消息**：

- `prefetch_count=1`：消费者每 ack 一条才发下一条——**任务队列场景的标准配置**，避免「忙的闲死、闲的撑死」；
- 配合手动 ack，prefetch 里的消息如果消费者挂了会自动重投。

---

## 三、环境搭建（Windows / Docker）

最省事的方式是 Docker 一键启动（含管理控制台）：

```bash
docker run -d --name rabbitmq ^
  -p 5672:5672 -p 15672:15672 ^
  rabbitmq:3.13-management
```

说明：

- `5672` 是 AMQP 协议端口（程序连接用）；`15672` 是管理控制台端口。
- 默认账号密码 `guest / guest`（**仅允许 localhost 连接**，远程访问需新建用户）。
- 打开 http://localhost:15672 进入管理界面，可以直观看到连接、通道、exchange、队列、消息内容——**学习阶段强烈建议全程开着它**，每条消息的去向一目了然。

常用管理命令（进入容器）：

```bash
docker exec -it rabbitmq rabbitmqctl list_queues
docker exec -it rabbitmq rabbitmqctl list_exchanges
docker exec -it rabbitmq rabbitmqctl list_bindings
docker exec -it rabbitmq rabbitmqctl status
```

不用 Docker 也可以：官网下载 Windows installer，或用 `choco install rabbitmq`（需先装 Erlang）。

---

## 四、Python 实战（pika）

pika 是 RabbitMQ 官方推荐的 Python 客户端。安装：

```bash
pip install pika
```

> pika 的 `BlockingConnection` 简单直观但**不是线程安全的**，且为阻塞模型。异步场景请用 4.5 节的 aio-pika。

### 4.1 Hello World（最简单的点对点）

**生产者 send.py**

```python
import pika

# 1. 建立连接
credentials = pika.PlainCredentials('guest', 'guest')
params = pika.ConnectionParameters(
    host='localhost',
    port=5672,
    virtual_host='/',
    credentials=credentials,
)
connection = pika.BlockingConnection(params)
channel = connection.channel()

# 2. 声明队列（幂等操作：队列已存在则什么都不做）
#    生产者和消费者谁先启动都能声明，保证队列一定存在
channel.queue_declare(queue='hello')

# 3. 发布消息
#    exchange='' 表示用默认交换器，routing_key 即队列名
channel.basic_publish(
    exchange='',
    routing_key='hello',
    body='Hello RabbitMQ!',   # body 必须是 bytes，中文需 encode('utf-8')
)
print(' [x] Sent "Hello RabbitMQ!"')

# 4. 关闭连接（确保缓冲区消息刷出，不能省略）
connection.close()
```

**消费者 receive.py**

```python
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='hello')

def callback(ch, method, properties, body):
    print(f' [x] Received: {body.decode()}')
    # properties 里能看到 content_type、headers、delivery_mode 等元数据

# auto_ack=True：消息投递即删除，适合演示；生产环境用手动 ack
channel.basic_consume(queue='hello', on_message_callback=callback, auto_ack=True)

print(' [*] Waiting for messages. Press CTRL+C to exit')
channel.start_consuming()   # 阻塞循环
```

### 4.2 Work Queue（任务队列 + 公平分发 + 持久化）

这是 Agent 任务分发最核心的模式。要点：**队列持久化 + 消息持久化 + 手动 ack + prefetch=1**。

**生产者 new_task.py**

```python
import sys
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# durable=True：队列元数据持久化，Broker 重启后队列还在
# 注意：已存在的同名队列若属性不同，这里会报 PRECONDITION_FAILED
channel.queue_declare(queue='task_queue', durable=True)

# 开启发布者确认：Broker 落盘后会向生产者回 ack
channel.confirm_delivery()

message = ' '.join(sys.argv[1:]) or 'Hello World!'

try:
    channel.basic_publish(
        exchange='',
        routing_key='task_queue',
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2,          # 消息持久化（写入磁盘）
            content_type='text/plain',
        ),
        mandatory=True,               # 路由不到队列时抛 UnroutableError 而不是静默丢弃
    )
    print(f' [x] Sent {message!r}（已被 Broker 确认）')
except pika.exceptions.UnroutableError:
    print(' [!] 消息无法路由到任何队列')

connection.close()
```

**消费者 worker.py**

```python
import time
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='task_queue', durable=True)

# 公平分发：每个消费者最多同时持有 1 条未确认消息
channel.basic_qos(prefetch_count=1)

def callback(ch, method, properties, body):
    task = body.decode()
    print(f' [x] Received {task!r}')
    time.sleep(task.count('.'))       # 模拟耗时：几个点睡几秒
    print(' [x] Done')
    # 处理完成后才手动确认 —— 确认前崩溃，消息会自动重投给其他 Worker
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(queue='task_queue', on_message_callback=callback)
print(' [*] Waiting for messages. Press CTRL+C to exit')
channel.start_consuming()
```

**验证持久化**：启动 worker 处理几条消息后 `docker restart rabbitmq`，未 ack 的消息会在重启后重新出现。

### 4.3 Publish / Subscribe（fanout 广播）

日志/事件广播模式。每个消费者绑定自己的**临时独占队列**，都能收到完整副本。

**发布日志 emit_log.py**

```python
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# 声明 fanout 交换器
channel.exchange_declare(exchange='logs', exchange_type='fanout')

message = 'info: Agent task started'
# fanout 会忽略 routing_key，填空即可
channel.basic_publish(exchange='logs', routing_key='', body=message)
print(f' [x] Sent {message!r}')
connection.close()
```

**订阅日志 receive_logs.py**

```python
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.exchange_declare(exchange='logs', exchange_type='fanout')

# queue='' 让 Broker 生成随机名的临时队列
# exclusive=True：连接断开时队列自动删除
result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

# 绑定：logs 交换器的所有消息都会复制一份到这个队列
channel.queue_bind(exchange='logs', queue=queue_name)

def callback(ch, method, properties, body):
    print(f' [x] {body.decode()}')

channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
print(' [*] Waiting for logs. Press CTRL+C to exit')
channel.start_consuming()
```

开两个终端跑两份 receive_logs.py，再跑 emit_log.py——两个订阅者都能收到。

### 4.4 Routing（direct 按级别分发）

在 4.3 基础上换 exchange 类型并启用 routing key：

```python
# 生产者：按严重级别路由
channel.exchange_declare(exchange='direct_logs', exchange_type='direct')
channel.basic_publish(
    exchange='direct_logs',
    routing_key=severity,        # 'info' / 'warning' / 'error'
    body=message,
)
```

```python
# 消费者：只接收感兴趣的级别（可多次绑定多个 key）
result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue
for severity in ['error', 'warning']:
    channel.queue_bind(
        exchange='direct_logs',
        queue=queue_name,
        routing_key=severity,
    )
```

### 4.5 Topic（模式匹配路由）

```python
# 生产者
channel.exchange_declare(exchange='topic_logs', exchange_type='topic')
channel.basic_publish(
    exchange='topic_logs',
    routing_key='agent.planner.done',
    body='planning finished',
)
```

```python
# 消费者：按需绑定模式
#   'agent.#'           → 所有 agent 事件
#   'agent.planner.*'   → planner 的单级事件
#   '#.done'            → 任何来源的 done 事件
channel.queue_bind(exchange='topic_logs', queue=queue_name,
                   routing_key='agent.#')
```

### 4.6 RPC 模式（请求-响应）

RabbitMQ 也能做 RPC：客户端发送时带上 `reply_to`（回复队列）和 `correlation_id`（关联 ID），服务端处理完把结果发回 reply_to，客户端按 correlation_id 匹配响应。

> Agent 开发中「同步等待一个子任务结果」可以用它，但如果调用链很深，建议改用 8.2 的事件驱动模式，避免层层阻塞。

**RPC 服务端 rpc_server.py**

```python
import pika

def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)

def on_request(ch, method, props, body):
    n = int(body)
    print(f' [.] fib({n})')
    response = fib(n)
    # 把结果发回客户端指定的 reply_to 队列，带上原 correlation_id
    ch.basic_publish(
        exchange='',
        routing_key=props.reply_to,
        properties=pika.BasicProperties(correlation_id=props.correlation_id),
        body=str(response),
    )
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='rpc_queue')
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='rpc_queue', on_message_callback=on_request)
print(' [x] Awaiting RPC requests')
channel.start_consuming()
```

**RPC 客户端 rpc_client.py**

```python
import uuid
import pika

class RpcClient:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()
        # 客户端专属的临时回复队列
        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue
        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self._on_response,
            auto_ack=True,
        )

    def _on_response(self, ch, method, props, body):
        # 用 correlation_id 匹配是不是我这次调用的响应
        if props.correlation_id == self.corr_id:
            self.response = body

    def call(self, n, timeout_s=10):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key='rpc_queue',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=str(n),
        )
        # 轮询等待响应（process_data_events 处理到达的消息）
        import time
        deadline = time.time() + timeout_s
        while self.response is None and time.time() < deadline:
            self.connection.process_data_events(time_limit=1)
        if self.response is None:
            raise TimeoutError('RPC timeout')
        return int(self.response)

client = RpcClient()
print(f' [x] Requesting fib(30)')
print(f' [.] Got {client.call(30)}')
```

### 4.7 异步版本：aio-pika（推荐用于 Agent 项目）

Agent 框架（LangChain / LangGraph / 自研 runtime）普遍是 asyncio 生态，pika 的阻塞模型格格不入。**aio-pika** 是基于 asyncio 的现代客户端，自带断线重连（robust connection）。

```bash
pip install aio-pika
```

```python
import asyncio
import aio_pika

async def main():
    # connect_robust：网络抖动自动重连，队列/交换器自动恢复
    connection = await aio_pika.connect_robust('amqp://guest:guest@localhost/')

    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)

        queue = await channel.declare_queue('task_queue', durable=True)

        # ---- 发送 ----
        await channel.default_exchange.publish(
            aio_pika.Message(
                body=b'hello async world',
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,  # 持久化
                content_type='text/plain',
            ),
            routing_key='task_queue',
        )
        print(' [x] Sent')

        # ---- 消费（iterator 写法，天然适配 async for）----
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                # message.process() 上下文管理器：
                #   正常退出 → 自动 ack
                #   抛异常   → 自动 nack(requeue=False)
                async with message.process():
                    print(f' [x] Received: {message.body.decode()}')
                    # 模拟只处理一条就退出演示
                    break

asyncio.run(main())
```

aio-pika 要点：

- `connect_robust` 比 `connect` 多了自动重连与拓扑恢复，生产环境直接用 robust；
- `message.process()` 是最省心的 ack 管理方式；需要精细控制时用 `await message.ack()` / `await message.nack(requeue=...)` / `await message.reject()`；
- 声明 fanout/topic 交换器：`await channel.declare_exchange('logs', aio_pika.ExchangeType.FANOUT)`；
- 绑定：`await queue.bind('logs')`。

---

## 五、Node.js 实战（amqplib）

amqplib 是 Node.js 生态事实标准的 AMQP 客户端，提供 Promise 和 Callback 两套 API，本文全部使用 Promise 版。

```bash
npm install amqplib
```

### 5.1 Hello World

**生产者 send.js**

```javascript
const amqp = require('amqplib');

async function main() {
  // connect 返回 Promise<Connection>
  const connection = await amqp.connect('amqp://guest:guest@localhost:5672');
  const channel = await connection.createChannel();

  const queue = 'hello';
  // assertQueue：队列不存在则创建；durable 等选项必须与已存在队列一致
  await channel.assertQueue(queue, { durable: false });

  // body 必须是 Buffer
  channel.sendToQueue(queue, Buffer.from('Hello RabbitMQ!'));
  console.log(' [x] Sent "Hello RabbitMQ!"');

  await channel.close();
  await connection.close();
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
```

**消费者 receive.js**

```javascript
const amqp = require('amqplib');

async function main() {
  const connection = await amqp.connect('amqp://guest:guest@localhost:5672');
  const channel = await connection.createChannel();

  const queue = 'hello';
  await channel.assertQueue(queue, { durable: false });

  console.log(' [*] Waiting for messages. Press CTRL+C to exit');

  // noAck: false → 手动确认模式
  await channel.consume(queue, (msg) => {
    if (!msg) return;                    // 消费被取消时 msg 可能为 null
    console.log(' [x] Received:', msg.content.toString());
    channel.ack(msg);                    // 手动确认
  }, { noAck: false });
}

main().catch(console.error);
```

### 5.2 Work Queue（持久化 + 公平分发 + 确认）

**生产者 new_task.js**

```javascript
const amqp = require('amqplib');

async function main() {
  const connection = await amqp.connect('amqp://guest:guest@localhost:5672');
  const channel = await connection.createChannel();

  await channel.assertQueue('task_queue', { durable: true });

  const message = process.argv.slice(2).join(' ') || 'Hello World!';

  // persistent: true → 消息持久化
  channel.sendToQueue('task_queue', Buffer.from(message), { persistent: true });
  console.log(` [x] Sent "${message}"`);

  await channel.close();
  await connection.close();
}

main().catch(console.error);
```

**消费者 worker.js**

```javascript
const amqp = require('amqplib');

async function main() {
  const connection = await amqp.connect('amqp://guest:guest@localhost:5672');
  const channel = await connection.createChannel();

  await channel.assertQueue('task_queue', { durable: true });

  // 公平分发：每个消费者最多 1 条未确认消息
  channel.prefetch(1);

  console.log(' [*] Waiting for messages. Press CTRL+C to exit');

  channel.consume('task_queue', (msg) => {
    if (!msg) return;
    const task = msg.content.toString();
    console.log(` [x] Received "${task}"`);

    // 模拟耗时工作：几个点睡几秒
    const seconds = (task.match(/\./g) || []).length * 1000;
    setTimeout(() => {
      console.log(' [x] Done');
      channel.ack(msg);                  // 完成后手动确认
      // channel.nack(msg, false, true); // 拒绝：第2参=仅这条，第3参=是否重入队
    }, seconds);
  }, { noAck: false });
}

main().catch(console.error);
```

### 5.3 Publish / Subscribe（fanout）

**发布者 emit_log.js**

```javascript
const amqp = require('amqplib');

async function main() {
  const connection = await amqp.connect('amqp://guest:guest@localhost:5672');
  const channel = await connection.createChannel();

  // assertExchange：声明 fanout 交换器
  await channel.assertExchange('logs', 'fanout', { durable: true });

  const message = 'info: Agent task started';
  // publish 到 exchange，routing key 对 fanout 无意义
  channel.publish('logs', '', Buffer.from(message));
  console.log(` [x] Sent "${message}"`);

  await channel.close();
  await connection.close();
}

main().catch(console.error);
```

**订阅者 receive_logs.js**

```javascript
const amqp = require('amqplib');

async function main() {
  const connection = await amqp.connect('amqp://guest:guest@localhost:5672');
  const channel = await connection.createChannel();

  await channel.assertExchange('logs', 'fanout', { durable: true });

  // 空队列名 → Broker 生成随机名；exclusive → 连接断开即删除
  const q = await channel.assertQueue('', { exclusive: true });
  await channel.bindQueue(q.queue, 'logs', '');

  console.log(' [*] Waiting for logs. Press CTRL+C to exit');
  await channel.consume(q.queue, (msg) => {
    if (!msg) return;
    console.log(' [x]', msg.content.toString());
  }, { noAck: true });
}

main().catch(console.error);
```

### 5.4 Routing 与 Topic

```javascript
// direct：与 fanout 只差 exchange 类型和 routing key 的使用
await channel.assertExchange('direct_logs', 'direct', { durable: true });
channel.publish('direct_logs', 'error', Buffer.from(message));

// 消费端绑定
const q = await channel.assertQueue('', { exclusive: true });
await channel.bindQueue(q.queue, 'direct_logs', 'error');
await channel.bindQueue(q.queue, 'direct_logs', 'warning');
```

```javascript
// topic：模式匹配
await channel.assertExchange('topic_logs', 'topic', { durable: true });
channel.publish('topic_logs', 'agent.planner.done', Buffer.from('ok'));

const q = await channel.assertQueue('', { exclusive: true });
await channel.bindQueue(q.queue, 'topic_logs', 'agent.#');   // 收所有 agent 事件
```

### 5.5 发布者确认（Confirm Channel）

普通 channel 的 `publish/sendToQueue` 不等待 Broker 确认。要保证「发出去了」，用 **ConfirmChannel**：

```javascript
const amqp = require('amqplib');

async function main() {
  const connection = await amqp.connect('amqp://guest:guest@localhost:5672');
  // 关键：createConfirmChannel
  const channel = await connection.createConfirmChannel();

  await channel.assertQueue('task_queue', { durable: true });

  channel.sendToQueue(
    'task_queue',
    Buffer.from('important task'),
    { persistent: true },
    (err) => {
      // 每条消息的确认回调
      if (err) console.error(' [!] 未确认:', err);
      else console.log(' [x] Broker 已确认收到');
    }
  );

  // 或批量等待：所有未确认消息都收到 ack/nack 后 resolve
  await channel.waitForConfirms();

  await channel.close();
  await connection.close();
}

main().catch(console.error);
```

### 5.6 连接管理的正确姿势

amqplib 的连接不会自动重连，必须自己监听事件并重建。生产环境推荐这样的封装：

```javascript
const amqp = require('amqplib');

const AMQP_URL = 'amqp://guest:guest@localhost:5672';

class AmqpClient {
  constructor() {
    this.connection = null;
    this.channel = null;
    this.closing = false;
  }

  async connect() {
    this.connection = await amqp.connect(AMQP_URL);

    // 连接异常：记录但不退出，等 close 事件触发重连
    this.connection.on('error', (err) => {
      console.error('[amqp] connection error:', err.message);
    });

    // 连接关闭：非主动关闭则 3 秒后重连
    this.connection.on('close', () => {
      if (this.closing) return;
      console.warn('[amqp] connection closed, reconnecting in 3s...');
      setTimeout(() => this.connect().catch(() => {}), 3000);
    });

    this.channel = await this.connection.createChannel();
    await this.channel.assertQueue('task_queue', { durable: true });
    this.channel.prefetch(1);
    console.log('[amqp] connected');
  }

  async consume(queue, handler) {
    await this.channel.consume(queue, async (msg) => {
      if (!msg) return;
      try {
        await handler(msg.content, msg);
        this.channel.ack(msg);
      } catch (err) {
        console.error('[amqp] handler error:', err);
        // 失败不重入队 → 走死信队列（见第六章），避免毒消息死循环
        this.channel.nack(msg, false, false);
      }
    }, { noAck: false });
  }

  async publish(queue, content, options = {}) {
    // 连接断开时 sendToQueue 会抛错，交给上层重试
    this.channel.sendToQueue(queue, Buffer.from(content),
      { persistent: true, ...options });
  }

  async close() {
    this.closing = true;
    await this.channel?.close();
    await this.connection?.close();
  }
}

module.exports = AmqpClient;
```

> Python 侧对应策略：pika 需要自己包重试循环；aio-pika 用 `connect_robust` 即可。

---

## 六、可靠性保障：消息不丢、不重、不乱

生产环境必须回答三个问题：**消息会不会丢？会不会重复消费？失败消息去哪？**

### 6.1 防丢失的三道防线

消息可能在三个环节丢失，逐一设防：

**① 生产者 → Broker：开启 publisher confirms**

- Python：`channel.confirm_delivery()` 后，`basic_publish` 若未获确认会抛 `pika.exceptions.NackError`；
- Node：使用 `createConfirmChannel()` + `waitForConfirms()`。
- 兜底：捕获异常后重试或落本地表（「本地消息表」模式）。

**② Broker 内部：持久化 + 高可用队列**

- 队列声明 `durable=True`；
- 消息设置 `delivery_mode=2`（Python）/ `persistent: true`（Node）；
- 单节点磁盘故障仍可能丢最近几秒的消息（持久化是异步刷盘），高要求场景使用**仲裁队列（quorum queue）**——基于 Raft 协议多副本复制：

```python
channel.queue_declare(queue='orders', durable=True,
                      arguments={'x-queue-type': 'quorum'})
```

```javascript
await channel.assertQueue('orders', {
  durable: true,
  arguments: { 'x-queue-type': 'quorum' },
});
```

**③ Broker → 消费者：手动 ack**

- 关闭 auto_ack，业务逻辑**成功执行完**再 ack；
- 消费者崩溃后 unacked 消息自动重投；
- 注意：ack 之后写数据库失败这类「ack 时机」问题，要靠幂等（6.4）兜底。

### 6.2 死信交换器（DLX）：失败消息的正确归宿

消息在以下三种情况会变成「死信（dead-letter）」：

1. 被 `basic_nack / basic_reject` 且 `requeue=False`；
2. 消息 TTL 过期；
3. 队列达到最大长度。

死信会被重新发布到该队列配置的**死信交换器**，通常引入一个专门的死信队列做人工排查、告警或延迟重试。

**Python 配置示例：**

```python
# 1. 死信交换器和死信队列
channel.exchange_declare(exchange='dlx', exchange_type='direct')
channel.queue_declare(queue='dead_tasks')
channel.queue_bind(exchange='dlx', queue='dead_tasks', routing_key='failed')

# 2. 业务队列声明时绑定 DLX 与 TTL
channel.queue_declare(
    queue='agent_tasks',
    durable=True,
    arguments={
        'x-dead-letter-exchange': 'dlx',           # 死信去向
        'x-dead-letter-routing-key': 'failed',     # 死信的路由键
        'x-message-ttl': 5 * 60 * 1000,            # 5 分钟未消费即过期
        'x-max-length': 10000,                     # 队列最大长度
    },
)
```

**Node.js 配置示例：**

```javascript
await channel.assertExchange('dlx', 'direct', { durable: true });
await channel.assertQueue('dead_tasks', { durable: true });
await channel.bindQueue('dead_tasks', 'dlx', 'failed');

await channel.assertQueue('agent_tasks', {
  durable: true,
  arguments: {
    'x-dead-letter-exchange': 'dlx',
    'x-dead-letter-routing-key': 'failed',
    'x-message-ttl': 5 * 60 * 1000,
    'x-max-length': 10000,
  },
});
```

**重要陷阱**：`arguments` 属于队列定义的一部分。对**已存在**的队列用不同 arguments 调用 `queue_declare / assertQueue`，Broker 会直接报 `PRECONDITION_FAILED` 并关闭 channel。修改参数必须先删除旧队列（管理台或 `queue_delete`），或换一个队列名。

### 6.3 延迟重试：用 TTL 实现延迟队列

RabbitMQ 没有原生延迟消息，但可以用「TTL + DLX」实现：建一个带 TTL 的中间队列（无消费者），消息过期后自动流入死信队列，死信队列才是真正的消费队列——于是消息「延迟了 N 秒」才被消费。

```
发送 → delay_queue(x-message-ttl=30s, x-dead-letter-exchange=retry_dlx)
         （无消费者，静置 30 秒）
              ↓ 过期变成死信
       retry_dlx → retry_queue → 消费者执行重试
```

注意：队列级 TTL 全体一致；若用消息级 TTL（每条不同），队首消息不过期会阻塞后面的消息（除非用 RabbitMQ 4.0+ 或 `rabbitmq_delayed_message_exchange` 插件）。

### 6.4 幂等性：解决重复消费

「至少一次投递（at-least-once）」是 RabbitMQ 的承诺，这意味着重复不可避免：消费者处理完但 ack 前崩溃 → 消息重投 → 业务执行两次。解决办法不在 MQ，在业务层：

- **唯一 ID 去重**：每条消息带 `message_id`（或业务单号），消费前查 Redis/数据库「已处理集合」，处理完写入；
- **数据库唯一约束**：插入操作靠 unique key 天然去重；
- **状态机校验**：只允许 `pending → running → done` 的合法流转，重复消息因状态不符被安全跳过；
- **乐观锁/版本号**：更新操作带版本号，重复执行无效化。

```python
def callback(ch, method, props, body):
    msg_id = props.message_id
    if redis.set(f'consumed:{msg_id}', 1, nx=True, ex=86400):
        do_business(body)          # 首次：执行业务
    ch.basic_ack(delivery_tag=method.delivery_tag)  # 重复：直接 ack
```

### 6.5 顺序性

单队列 + 单消费者 = 严格有序；多消费者并发时无法保证全局顺序。需要按 key 有序（如同一用户的任务有序）时，要么单消费者，要么按 key 哈希到多个队列、每个队列单消费者。

---

## 七、Agent 开发中的消息队列实战架构

### 7.1 异步 Agent 任务队列（最核心模式）

整体拓扑：

```
                        ┌──────────────────────────────┐
用户提交任务 → API 服务 ─┤ agent_tasks 队列（durable+DLX）├→ Agent Worker 池（N 个，可水平扩容）
                        └──────────────────────────────┘         │
                                │ 超过重试上限                    ├→ agent_results 队列 → 通知服务 → WebSocket/回调给用户
                                ▼                                └→ agent.events（topic）→ 监控/日志/审计
                          dead_tasks 死信队列 → 告警 + 人工排查
```

**Worker 端完整示例（Python，带重试计数与死信）：**

```python
import json
import pika

MAX_RETRIES = 3

def run_agent(task: dict) -> str:
    """这里替换成你的 Agent 执行逻辑：LLM 调用、工具链、多步推理..."""
    print(f'    >> 执行任务: {task["prompt"][:40]}')
    return f'任务 {task["id"]} 的结果...'

def on_task(ch, method, props, body):
    task = json.loads(body)
    try:
        result = run_agent(task)

        # 结果发到结果队列，透传 correlation_id 便于前端关联
        ch.basic_publish(
            exchange='',
            routing_key='agent_results',
            body=json.dumps({'task_id': task['id'], 'result': result},
                            ensure_ascii=False).encode('utf-8'),
            properties=pika.BasicProperties(
                correlation_id=props.correlation_id,
                delivery_mode=2,
            ),
        )
        # 同时发布事件到 topic 交换器，供监控/审计订阅
        ch.basic_publish(
            exchange='agent.events',
            routing_key=f'agent.worker.done',
            body=json.dumps({'task_id': task['id']}).encode('utf-8'),
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        headers = dict(props.headers or {})
        retry_count = headers.get('x-retry-count', 0)

        if retry_count < MAX_RETRIES:
            # 重投：带上递增的重试计数（注意这是"重新发布"，消息会排到队尾）
            headers['x-retry-count'] = retry_count + 1
            ch.basic_publish(
                exchange='',
                routing_key='agent_tasks',
                body=body,
                properties=pika.BasicProperties(
                    headers=headers,
                    delivery_mode=2,
                    message_id=props.message_id,   # 保留原 message_id 供幂等
                ),
            )
            ch.basic_ack(delivery_tag=method.delivery_tag)
            print(f' [~] 任务 {task["id"]} 第 {retry_count + 1} 次重试: {e}')
        else:
            # 超过上限：拒绝且不重入队 → 流入死信队列，触发告警
            print(f' [!] 任务 {task["id"]} 重试耗尽，进入死信队列')
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # 拓扑声明（生产环境建议集中在一个 setup 脚本里做）
    channel.exchange_declare(exchange='agent.events', exchange_type='topic',
                             durable=True)
    channel.exchange_declare(exchange='dlx', exchange_type='direct', durable=True)
    channel.queue_declare(queue='dead_tasks', durable=True)
    channel.queue_bind(exchange='dlx', queue='dead_tasks', routing_key='failed')
    channel.queue_declare(queue='agent_results', durable=True)
    channel.queue_declare(
        queue='agent_tasks', durable=True,
        arguments={'x-dead-letter-exchange': 'dlx',
                   'x-dead-letter-routing-key': 'failed'},
    )
    channel.basic_qos(prefetch_count=1)   # Worker 一次只拿一个任务
    channel.basic_consume(queue='agent_tasks', on_message_callback=on_task)

    print(' [*] Agent worker 就绪，等待任务...')
    channel.start_consuming()

if __name__ == '__main__':
    main()
```

**API 端提交任务（FastAPI 示例）：**

```python
import json, uuid
import pika
from fastapi import FastAPI

app = FastAPI()
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.confirm_delivery()

@app.post('/tasks')
def submit_task(prompt: str):
    task_id = str(uuid.uuid4())
    channel.basic_publish(
        exchange='',
        routing_key='agent_tasks',
        body=json.dumps({'id': task_id, 'prompt': prompt},
                        ensure_ascii=False).encode('utf-8'),
        properties=pika.BasicProperties(
            delivery_mode=2,
            message_id=task_id,              # 幂等去重的依据
            correlation_id=task_id,          # 贯穿全链路的追踪 ID
        ),
        mandatory=True,
    )
    return {'task_id': task_id, 'status': 'queued'}   # 毫秒级返回
```

**扩缩容**：任务积压时把 Worker 从 3 个扩到 10 个即可，队列和 API 完全无感——这就是解耦的价值。

### 7.2 多 Agent 事件协作（topic 事件总线）

多个 Agent 分工协作时，用 topic exchange 做事件总线，避免 Agent 之间硬编码互调：

```
事件命名约定：agent.{角色}.{事件}
  agent.planner.started   规划 Agent 开始
  agent.planner.done      规划完成（附带任务拆解结果）
  agent.researcher.done   调研 Agent 完成
  agent.writer.done       撰写 Agent 完成
  agent.pipeline.failed   流水线失败
```

```python
# 编排 Agent：只关心"规划完成"事件，收到后派发子任务
channel.queue_bind(exchange='agent.events', queue='orchestrator_in',
                   routing_key='agent.planner.done')

# 监控 Agent：订阅所有事件（# 通配）
channel.queue_bind(exchange='agent.events', queue='monitor_in',
                   routing_key='#')

# 某个 Agent 完成时发布事件（事件体里带上上下文和追踪 ID）
channel.basic_publish(
    exchange='agent.events',
    routing_key='agent.researcher.done',
    body=json.dumps({
        'task_id': task_id,
        'trace_id': trace_id,
        'output': research_result,
    }).encode('utf-8'),
    properties=pika.BasicProperties(delivery_mode=2),
)
```

好处：新增一个 Agent 角色只需新增订阅，其他 Agent 代码零改动；监控、审计、计费（统计 token）作为旁路订阅者接入，不影响主链路。

### 7.3 设计要点小结

**什么时候用队列，什么时候直接调用？** 短平快（<1s、无需重试）的内部调用直接函数调用；涉及 LLM 生成、外部 API、用户可异步等待的，一律走队列。

**消息体放什么？** 只放 ID 和轻量上下文（task_id、trace_id、必要参数），**不要塞大 payload**（生成的长文本、图片请存对象存储/数据库，消息里放引用）。消息体过大会拖慢 Broker。

**追踪贯穿全链路**：入口处生成 trace_id，通过 `correlation_id` 或 headers 透传到每个环节，排查问题时能一键串起「用户请求 → 队列 → Worker → 结果」。

**与现成框架的关系**：Python 里 Celery / Dramatiq / arq 都以 RabbitMQ 为 broker，帮你封装了重试、定时、结果存储——如果需求标准，直接用它们；如果你的 Agent 运行时是自研的（比如 LangGraph 自托管），按本文手写 Worker 反而更可控。Node 侧 BullMQ 更常用 Redis，若技术栈已定 RabbitMQ，就用 amqplib 手写或找社区封装。

---

## 八、最佳实践与常见坑清单

**连接与通道**

- 每个进程 1~2 条 Connection 足矣，不要为每条消息新建连接；Channel 可随用随建，但建议复用；
- pika BlockingConnection 不是线程安全的——多线程请用「每线程一条连接」或换 aio-pika 异步模型；
- 务必处理断线重连（amqplib 监听 close 事件重建；aio-pika 用 connect_robust；pika 自己包重试）。

**队列与声明**

- 生产者和消费者都声明队列（幂等），避免「谁先启动谁报错」；
- 队列属性（durable、arguments）一经创建不可变更，改动需删除重建——生产环境用独立的初始化脚本/迁移流程管理拓扑；
- 别在生产环境用 `exclusive` 临时队列承接重要数据（连接一断数据全没）。

**消费端**

- 生产环境永远手动 ack，且 ack 放在业务成功**之后**；
- `prefetch_count` 别用默认无限——根据单条任务耗时和 Worker 内存设置（重任务设 1~5）；
- 毒消息（永远处理失败的消息）必须兜底：限制重试次数后 nack(requeue=False) 进死信队列，**不要无脑 requeue=true**，会无限循环打爆 CPU；
- 消费逻辑里捕获所有异常，别让未处理异常导致连接断开。

**生产端**

- 重要消息必开 confirm 模式 + 持久化；
- 消息带 `message_id`（幂等）和 `correlation_id`（追踪）；
- 发送失败要有重试与兜底（本地消息表），不能静默吞掉。

**运维**

- 管理控制台常开，关注队列深度（堆积）和消费者数量——**队列持续堆积 = 消费能力不足，扩容 Worker**；
- 设置队列长度上限和 TTL，防止异常情况下内存被无限堆积撑爆；
- 监控告警接 Management API（`GET /api/queues/{vhost}/{queue}`）或 Prometheus 插件。

**安全**

- 生产环境新建用户、设置最小权限、修改 guest 密码；远程部署禁用 guest 或限制来源；
- 跨服务部署考虑 TLS（amqps://，端口 5671）。

---

## 九、速查表

### 概念速查

| 我想... | 用什么 |
|---|---|
| 点对点任务 | 默认交换器 + queue_declare |
| 任务分发给 Worker 池 | 队列 + prefetch + 手动 ack |
| 广播给所有订阅者 | fanout exchange |
| 按类别精确分发 | direct exchange |
| 多级模式匹配 | topic exchange（`*` 一个词，`#` 任意词） |
| 请求-响应 | reply_to + correlation_id |
| 延迟执行 | TTL + DLX |
| 失败消息兜底 | 死信交换器 DLX |
| 高可用 | quorum queue（x-queue-type=quorum） |

### API 对照表（Python pika ↔ Node amqplib）

| 操作 | Python (pika) | Node (amqplib) |
|---|---|---|
| 连接 | `pika.BlockingConnection(params)` | `amqp.connect(url)` |
| 建通道 | `connection.channel()` | `connection.createChannel()` |
| 声明队列 | `channel.queue_declare(q, durable=True)` | `channel.assertQueue(q, {durable:true})` |
| 声明交换器 | `channel.exchange_declare(e, exchange_type='topic')` | `channel.assertExchange(e, 'topic', {})` |
| 绑定 | `channel.queue_bind(exchange=e, queue=q, routing_key=k)` | `channel.bindQueue(q, e, k)` |
| 发送 | `channel.basic_publish(exchange, key, body, properties)` | `channel.publish(e, key, Buffer)` / `sendToQueue` |
| 消费 | `channel.basic_consume(queue, on_message_callback=cb)` | `channel.consume(queue, cb)` |
| 确认 | `ch.basic_ack(delivery_tag=...)` | `channel.ack(msg)` |
| 拒绝 | `ch.basic_nack(delivery_tag, requeue=False)` | `channel.nack(msg, false, false)` |
| 限流 | `channel.basic_qos(prefetch_count=1)` | `channel.prefetch(1)` |
| 发布者确认 | `channel.confirm_delivery()` | `connection.createConfirmChannel()` |
| 消息持久化 | `BasicProperties(delivery_mode=2)` | `{ persistent: true }` |
| 临时队列 | `queue_declare(queue='', exclusive=True)` | `assertQueue('', {exclusive:true})` |

### 学习路线建议

1. 用 Docker 起 RabbitMQ，打开管理控制台；
2. 跑通 4.1/5.1 Hello World，在控制台观察消息流动；
3. 实现 Work Queue：开 2 个 Worker，发 5 条不同耗时任务，观察公平分发；
4. 动手杀 Worker 进程（`Ctrl+C` 到一半），验证 unacked 消息重投；
5. 改造为 confirm + 持久化 + DLX 的完整版（7.1 的代码可直接用）；
6. 用 topic exchange 搭一个两个 Agent 协作的最小事件总线；
7. 最后按 6.4 补上幂等设计，你就拥有了一套生产级骨架。

---

> 延伸阅读：RabbitMQ 官方教程（rabbitmq.com/tutorials，有 Python/Node 多语言版，本文结构与其呼应但补充了生产细节）、官方 Reliability Guide、Quorum Queues 文档。
