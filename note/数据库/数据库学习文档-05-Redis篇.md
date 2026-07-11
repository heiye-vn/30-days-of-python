# 数据库学习文档 - 第 05 篇：Redis 核心与锁机制

> 面向"前端转后端 Python 开发者"的数据库学习文档
> 适用读者：已掌握 Node.js 版 LangChain/LangGraph，正在学习后端 Python（FastAPI/LangChain 方向）
> 运行环境：Windows（cmd.exe，注意 GBK 编码问题，代码中不使用 emoji）

---

## 第九章 Redis 核心与锁机制

前面八章我们一直围绕关系型数据库（MySQL/PostgreSQL）展开。但是，只要你的后端系统上了规模，就会碰到两个绕不开的难题：一是"快"——某些数据每次请求都要查、延迟必须压到毫秒级，磁盘数据库扛不住；二是"锁"——当你的服务部署了多个实例，传统的 `threading.Lock` 或数据库行锁就不够用了，你需要一把能跨进程、跨机器的锁。

这两个难题的答案，都指向同一个组件：Redis。这一章我们就来彻底搞懂 Redis，特别是它的锁机制。这是从"会写 CRUD 的后端"走向"能扛住高并发的后端"的关键一跃。

> 前端类比：如果说 MySQL 是你浏览器里的 IndexedDB（持久化、容量大但慢），那么 Redis 就像是浏览器内存里的 Map / WeakMap——读写极快，但断电就丢。后端系统几乎都是"内存缓存 + 磁盘持久化"的双层结构，Redis 就是那个"内存层"。

---

### 9.1 Redis 基础认知

#### 9.1.1 Redis 是什么：内存数据库 vs 磁盘数据库的本质区别

Redis（Remote Dictionary Server）是一个基于内存的、键值对（key-value）型数据库。它的名字直译就是"远程字典服务器"——你可以把它理解成一个跑在服务器上的、超大的、支持多种数据结构的 Python dict。

它和我们之前学的 MySQL/PostgreSQL 最根本的区别在于"数据存哪里"：

```
[磁盘数据库 MySQL/PostgreSQL]
  数据存储位置：硬盘（SSD/HDD）
  读写路径：     CPU -> 内存(缓冲池) -> 磁盘
  访问延迟：     约 10ms（随机 IO，受限于磁盘寻道）
  容量上限：     TB 级别（受限于磁盘容量）
  数据安全性：   高（断电不丢，有 WAL/redo log 保证持久化）
  成本：         低（每 GB 存储成本很低）

[内存数据库 Redis]
  数据存储位置：内存（RAM）
  读写路径：     CPU -> 内存
  访问延迟：     约 0.1ms（直接内存访问，无磁盘 IO）
  容量上限：     GB 级别（受限于内存大小，内存比磁盘贵 100 倍）
  数据安全性：   中（内存断电即失，靠 RDB/AOF 持久化弥补）
  成本：         高（每 GB 内存成本远高于磁盘）
```

理解了"内存 vs 磁盘"这条根本分界线，你就理解了为什么 Redis 必须和关系型数据库搭配使用，而不是取代它：

- Redis 快，但贵且不安全（断电会丢部分数据）——适合做缓存、计数器、分布式锁这类"丢了能恢复"的数据。
- MySQL 慢，但便宜且安全——适合做订单、账户、交易这类"绝对不能丢"的数据。

一句话总结：**Redis 是数据库的"好搭档"，而不是数据库的"替代品"**。它的角色更接近于"数据的高速前置层"。

#### 9.1.2 为什么后端离不开 Redis：数据库的"好搭档"

让我们看一个具体场景，理解为什么后端离不开 Redis。

假设你做了一个内容平台，有一篇爆款文章，每秒有 10000 个用户访问文章详情页。每次访问后端都要查一次文章内容：

```sql
SELECT id, title, content, view_count FROM articles WHERE id = 12345;
```

一篇长文章的 content 字段可能有几十 KB。MySQL 每次从磁盘读取这个大字段，单次查询可能要 20ms。10000 QPS 打过去，你的 MySQL 主库很快就被打满了——连接数耗尽、CPU 飙升、慢查询堆积，最后整个系统雪崩。

加上 Redis 之后，架构变成这样：

```
用户请求
  -> FastAPI 应用
  -> 先查 Redis 缓存（0.1ms）
       命中 -> 直接返回（99% 的请求走这条路）
       未命中 -> 查 MySQL（20ms）-> 写入 Redis -> 返回
```

热点数据被 Redis 扛住，MySQL 只在缓存 miss 时被访问，QPS 从 10000 降到几十。这就是后端系统最经典的"缓存层"模式。除了缓存，Redis 在后端还承担这些角色：

- **分布式锁**：多实例部署时，保证同一时刻只有一个实例能执行关键操作（如扣库存）。
- **计数器**：点赞数、浏览量、库存余量，Redis 的 `INCR` 是原子操作，比数据库快得多。
- **会话存储**：JWT 黑名单、Session 数据，Redis 的过期机制天然适合。
- **消息队列**：List / Stream 实现轻量级异步任务。
- **排行榜**：ZSet（有序集合）天然就是排行榜数据结构。
- **限流器**：令牌桶、滑动窗口，保护数据库不被打爆。

可以说，现代后端架构里，Redis 已经是和关系型数据库同等地位的"第二块基石"。第六章我们埋了个伏笔——"分布式锁的引入：Redis SETNX / Redlock 算法（详见第九章）"，现在就来兑现它。

#### 9.1.3 前端类比理解：Redis 像浏览器内存缓存，MySQL 像 IndexedDB

如果你是前端出身，理解 Redis 最好的方式是对照浏览器的存储体系：

```
[浏览器存储体系]                      [后端存储体系]
localStorage        (持久、慢、5MB)   <-> MySQL       (持久、慢、TB)
sessionStorage      (会话级、慢)      <-> Session(内存) (会话级)
IndexedDB           (持久、大容量)   <-> PostgreSQL   (持久、结构化)
内存变量/Map         (快、易失)        <-> Redis        (快、易失、GB)
Service Worker Cache (HTTP缓存)      <-> CDN/Nginx    (静态资源缓存)
```

更精确地说：

- **Redis 类似浏览器里的 `Map` / 全局变量**：读写极快（纳秒到微秒级），但页面一刷新就没了。Redis 也是内存存储，重启会丢（虽然有持久化机制，但不是绝对可靠）。
- **MySQL 类似浏览器的 IndexedDB**：数据持久化在磁盘上，容量大，但每次读写都要走磁盘 IO，比内存慢两个数量级。
- **Redis 的过期机制（EXPIRE）类似 `setTimeout`**：你给一个 key 设置过期时间，到点自动删除——就像前端给一个定时器到点清除缓存。

记住这个类比，后面学每个 Redis 特性时都可以问自己一句："这个在前端有对应物吗？"绝大多数时候，答案是"有"。

#### 9.1.4 Redis 单线程模型与 IO 多路复用（为什么单线程还这么快）

Redis 有一个让很多人困惑的特性：**它的核心命令处理是单线程的**。一个 4 核 8G 的服务器上跑 Redis，它默认只用一个核。但即使如此，Redis 的 QPS（每秒查询数）依然能达到 10 万级别。为什么单线程还能这么快？原因有三：

**第一，内存访问本身就极快。** Redis 的数据全在内存里，单次读写是纳秒级。磁盘数据库的瓶颈在磁盘 IO，Redis 的瓶颈在内存带宽和网络，根本不在 CPU。所以单核已经够用了。

**第二，避免了多线程的上下文切换和锁竞争。** 多线程系统里，线程切换、加锁解锁都是开销。如果 Redis 用多线程处理命令，同一个 key 被两个线程同时修改，就得加锁——而锁是性能杀手。单线程天然串行，没有任何并发问题，反而更高效。

**第三，IO 多路复用（I/O Multiplexing）。** 这是单线程能扛住高并发的核心技术。原理是这样的：

```
[传统阻塞 IO 模型]（每个连接一个线程）
  连接1 -> 线程1 -> read() 阻塞等待...（CPU 空转）
  连接2 -> 线程2 -> read() 阻塞等待...
  连接3 -> 线程3 -> read() 阻塞等待...
  问题：1万个连接就要 1万个线程，内存和上下文切换爆炸

[IO 多路复用模型]（单线程管理所有连接）
  单线程 -> epoll/select 监听所有 socket
  哪个 socket 有数据就绪 -> 处理那个 -> 处理完继续监听
  1万个连接只需 1个线程，没有上下文切换开销
```

类比一下：传统模型像一家餐厅给每桌客人配一个服务员，客人发呆时服务员也干等着；IO 多路复用像一个大堂经理同时盯着所有桌子，谁举手就先服务谁。后者显然更高效。

> 注意：Redis 的"单线程"指的是**命令执行**是单线程的。Redis 6.0 之后，网络读写（接收请求、发送响应）可以多线程处理（`io-threads`），但命令执行仍然是单线程串行。这是为了在保持简单性的同时榨取网络层的性能。

#### 9.1.5 Redis vs Memcached：功能差异与选型

Redis 并非唯一的选择。在内存缓存领域，还有一个老牌选手：Memcached。两者经常被拿来对比，理解它们的差异能帮你做出正确的选型。

| 对比维度 | Redis | Memcached |
|---------|-------|-----------|
| 数据结构 | String/Hash/List/Set/ZSet/Stream/Bitmap/HyperLogLog/GEO 等 | 仅 String |
| 持久化 | RDB + AOF，重启不丢数据 | 纯内存，重启即失 |
| 单机性能 | 10万 QPS | 10万 QPS（略高，因为更简单） |
| 集群 | 原生 Cluster 分片 | 客户端分片，无原生集群 |
| 线程模型 | 单线程命令执行 | 多线程 |
| 事务 | 支持 MULTI/EXEC | 不支持 |
| 发布订阅 | 支持 Pub/Sub | 不支持 |
| Lua 脚本 | 支持 | 不支持 |
| 适用场景 | 缓存 + 锁 + 队列 + 排行榜等"数据结构型"需求 | 纯键值缓存，极致简单 |

**选型建议：**

- 如果只是做简单的 KV 缓存，追求极致性能和极简部署——Memcached 够用。
- 如果需要复杂的数据结构（排行榜、消息队列、分布式锁、计数器）——**毫不犹豫选 Redis**。
- 实际工程中，新项目几乎不再选 Memcached，Redis 已经是事实标准。除非你在维护老系统，否则直接学 Redis 就行。

前端类比：Memcached 像一个只能存字符串的 `localStorage`；Redis 像一个支持 `Map`、`Set`、`Array` 等多种数据结构的 `Map` 增强版。功能丰富度上 Redis 完胜，这也是为什么 Redis 赢得了市场。

---

### 9.2 Redis 安装与基础操作

#### 9.2.1 Windows 环境安装 Redis（WSL2 / Docker 方式）

Redis 官方对 Windows 的支持一直很弱。官方的 Windows 版本停留在 3.2（2016 年），早就过时了。对于 Windows 开发者，推荐两种方式安装 Redis：

**方式一：Docker（推荐，最省心）**

如果你已经装了 Docker Desktop，一行命令搞定：

```cmd
:: 拉取并运行 Redis 7.x
docker run -d --name myredis -p 6379:6379 redis:7-alpine --requirepass yourpassword

:: 验证是否启动成功
docker ps

:: 进入 redis-cli
docker exec -it myredis redis-cli -a yourpassword
```

参数解释：
- `-d`：后台运行
- `--name myredis`：容器命名
- `-p 6379:6379`：把容器内的 6379 端口映射到宿主机
- `redis:7-alpine`：使用基于 Alpine Linux 的精简镜像（体积小）
- `--requirepass yourpassword`：设置密码（生产环境必须设密码）

**方式二：WSL2（Ubuntu 子系统）**

如果你的 Windows 10/11 开启了 WSL2，可以在 Linux 子系统里原生安装：

```bash
# 在 WSL2 的 Ubuntu 里执行
sudo apt update
sudo apt install redis-server

# 启动 Redis
sudo service redis-server start

# 进入 redis-cli
redis-cli

# 设置密码（编辑配置文件）
sudo nano /etc/redis/redis.conf
# 找到 requirepass 行，去掉注释，改为：requirepass yourpassword
# 重启生效
sudo service redis-server restart
```

> 经验之谈：开发环境用 Docker 最省事，不用管配置文件在哪、不用管服务怎么启停。一个 `docker-compose.yml` 搞定一切。下面是一个典型的开发用 compose 文件：

```yaml
# docker-compose.yml
version: "3.8"
services:
  redis:
    image: redis:7-alpine
    container_name: dev-redis
    ports:
      - "6379:6379"
    command: redis-server --requirepass devpass123 --appendonly yes
    volumes:
      - redis-data:/data
    restart: unless-stopped

volumes:
  redis-data:
```

启动：`docker compose up -d`，停止：`docker compose down`，数据持久化在 `redis-data` 卷里。

#### 9.2.2 redis-cli 命令行工具基础

`redis-cli` 是 Redis 的命令行客户端，类似 MySQL 的 `mysql` 命令。学会用它，你才能快速调试、排查问题。

```cmd
:: 连接本地 Redis（无密码）
redis-cli

:: 连接远程 Redis（带密码）
redis-cli -h 192.168.1.100 -p 6379 -a yourpassword

:: 连接后测试连通性
127.0.0.1:6379> PING
PONG

:: 查看服务器信息
127.0.0.1:6379> INFO server
# Server
redis_version:7.2.0
redis_mode:standalone
os:Linux

:: 查看内存使用
127.0.0.1:6379> INFO memory
used_memory:1048576         # 已用内存（字节）
used_memory_human:1.00M
maxmemory:0                 # 0 表示不限制
maxmemory_policy:noeviction # 淘汰策略

:: 查看当前库有多少个 key
127.0.0.1:6379> DBSIZE
(integer) 42

:: 选择数据库（Redis 默认有 16 个库，0-15）
127.0.0.1:6379> SELECT 1
OK
127.0.0.1:6379[1]>

:: 基本键值操作
127.0.0.1:6379> SET name "张三"
OK
127.0.0.1:6379> GET name
"\xe5\xbc\xa0\xe4\xb8\x89"   # 中文显示为字节序列
127.0.0.1:6379> GET name
# 用 --raw 选项启动可以正常显示中文：redis-cli --raw -a yourpassword
张三

:: 设置带过期时间的 key（10 秒）
127.0.0.1:6379> SET token "abc123" EX 10
OK
127.0.0.1:6379> TTL token
(integer) 8    # 剩余 8 秒
127.0.0.1:6379> TTL token
(integer) -2   # -2 表示 key 已不存在（已过期被删除）

:: 删除 key
127.0.0.1:6379> DEL name
(integer) 1    # 返回删除的数量

:: 查找 key（生产环境禁用 KEYS，用 SCAN）
127.0.0.1:6379> KEYS user:*
# KEYS 会阻塞单线程，数据量大时危险！

:: 安全的遍历方式（不阻塞）
127.0.0.1:6379> SCAN 0 MATCH user:* COUNT 100
1) "0"           # 游标，0 表示遍历结束
2) 1) "user:1001"
   2) "user:1002"
```

> 重要提醒：`KEYS *` 在生产环境是禁忌。因为 Redis 是单线程的，`KEYS` 会扫描所有 key 并阻塞整个服务器。百万级 key 时，一次 `KEYS *` 可能让 Redis 卡几秒，导致所有请求超时。必须用 `SCAN` 替代，它是非阻塞、游标式遍历。

#### 9.2.3 Python redis-py / aioredis 驱动安装与连接

Redis 官方推荐的 Python 客户端是 `redis-py`。从 4.2 版本开始，`redis-py` 合并了 `aioredis`，同一个库同时支持同步和异步 API。`aioredis` 作为独立库已经停止维护，新项目直接用 `redis-py` 即可。

安装：

```cmd
:: 安装 redis-py（含异步支持）
pip install redis

:: 如果要连接 Redis Cluster（集群版）
pip install redis[hiredis]
:: hiredis 是 C 扩展，能加速解析速度，生产环境推荐安装
```

同步客户端基本用法：

```python
# ============ redis-py 同步客户端 ============
import redis

# 创建连接（带连接池）
r = redis.Redis(
    host="127.0.0.1",
    port=6379,
    db=0,
    password="yourpassword",
    decode_responses=True,   # 自动解码为 str，否则返回 bytes
    socket_timeout=5,         # 读写超时 5 秒
    socket_connect_timeout=5, # 连接超时 5 秒
    retry_on_timeout=True,   # 超时自动重试
)

# 测试连通性
print(r.ping())  # True

# 基本字符串操作
r.set("greeting", "hello redis", ex=60)  # ex=60 表示 60 秒过期
print(r.get("greeting"))  # "hello redis"

# 计数器（原子操作）
r.set("view:article:1", 0)
r.incr("view:article:1")   # +1
r.incrby("view:article:1", 5)  # +5
print(r.get("view:article:1"))  # "6"

# 批量操作（pipeline，减少网络往返）
pipe = r.pipeline()
pipe.set("key1", "val1")
pipe.set("key2", "val2")
pipe.incr("counter")
results = pipe.execute()  # 一次性发送，返回 [True, True, 2]
print(results)
```

异步客户端（配合 FastAPI / asyncio）：

```python
# ============ redis-py 异步客户端 ============
import redis.asyncio as aioredis
import asyncio

async def main():
    r = aioredis.Redis(
        host="127.0.0.1",
        port=6379,
        password="yourpassword",
        decode_responses=True,
    )
    # 异步操作和同步 API 几乎一样，只是前面加 await
    await r.set("async_key", "async_value", ex=30)
    val = await r.get("async_key")
    print(val)  # "async_value"
    await r.close()

asyncio.run(main())
```

在 FastAPI 中，通常用依赖注入管理 Redis 连接：

```python
# ============ FastAPI 中管理 Redis 连接 ============
from contextlib import asynccontextmanager
import redis.asyncio as aioredis
from fastapi import FastAPI, Request

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时创建连接池
    app.state.redis = aioredis.Redis(
        host="127.0.0.1", port=6379, password="devpass",
        decode_responses=True, max_connections=50,
    )
    yield
    # 关闭时释放连接池
    await app.state.redis.close()

app = FastAPI(lifespan=lifespan)

@app.get("/api/view/{article_id}")
async def view_article(article_id: int, request: Request):
    redis_client: aioredis.Redis = request.app.state.redis
    # 原子递增浏览量
    views = await redis_client.incr(f"view:article:{article_id}")
    return {"article_id": article_id, "views": views}
```

> 前端类比：Redis 连接池就像前端的 `fetch` 连接复用。每次 `new Redis()` 都建立 TCP 连接开销很大，连接池维护一组复用连接，用完归还而不是关闭——就像浏览器的 HTTP Keep-Alive。

---

### 9.3 Redis 数据结构与应用场景

Redis 最强大的地方在于它不只是一个简单的 KV 存储，而是支持多种数据结构。每种数据结构都对应一类经典业务场景。理解这些数据结构，等于掌握了 Redis 的"瑞士军刀"。这一节我们逐一讲解，每种都给出 Redis 命令和 Python 代码。

> 前端类比：Redis 的数据结构就像 JavaScript 里的不同集合类型——String 是基本类型、Hash 是 `Object`、List 是 `Array`、Set 是 `Set`、ZSet 是带排序的 `Map`。选择正确的数据结构，能让你的业务逻辑用一两行命令就搞定。

#### 9.3.1 String：缓存对象、计数器、分布式锁

String 是 Redis 最基础的类型。一个 key 对应一个 value，value 可以是字符串、数字、甚至二进制数据（最大 512MB）。

**经典场景一：缓存对象**

```cmd
:: 存储用户信息 JSON
127.0.0.1:6379> SET user:1001 '{"name":"张三","age":25,"city":"北京"}' EX 3600
OK
127.0.0.1:6379> GET user:1001
"{\"name\":\"张三\",\"age\":25,\"city\":\"北京\"}"
```

**经典场景二：计数器（点赞数 / 浏览量）**

`INCR` / `DECR` 是原子操作，多个请求同时 +1 也不会出错。这比数据库的 `UPDATE ... SET count = count + 1` 高效得多。

```cmd
:: 文章浏览量 +1
127.0.0.1:6379> INCR view:article:1
(integer) 1
127.0.0.1:6379> INCR view:article:1
(integer) 2
127.0.0.1:6379> INCRBY view:article:1 10
(integer) 12

:: 点赞数
127.0.0.1:6379> INCR like:article:1
(integer) 1
```

**经典场景三：分布式锁（详见 9.6 节）**

```cmd
:: SET key value NX EX seconds：不存在才设置，且 30 秒过期
127.0.0.1:6379> SET lock:order:1001 "owner-uuid-xxx" NX EX 30
OK    # 加锁成功
127.0.0.1:6379> SET lock:order:1001 "other-uuid" NX EX 30
(nil) # 加锁失败，key 已存在
```

Python 代码示例：

```python
import json
import redis

r = redis.Redis(host="127.0.0.1", port=6379, decode_responses=True)

# ---- 场景1：缓存用户对象 ----
user_data = {"name": "张三", "age": 25, "city": "北京"}
r.set("user:1001", json.dumps(user_data, ensure_ascii=False), ex=3600)

cached = r.get("user:1001")
if cached:
    user = json.loads(cached)
    print(user["name"])  # 张三

# ---- 场景2：计数器 ----
# 浏览量（每次访问 +1）
r.incr("view:article:1")
r.incr("view:article:1")
r.incrby("view:article:1", 10)
print(r.get("view:article:1"))  # "12"

# 点赞（先判断是否点过，用 Set 配合去重，这里简化展示计数）
r.incr("like:article:1")
```

#### 9.3.2 Hash：对象存储、部分更新

Hash 是一个 key 下存多个字段（field-value），像 Python 的 dict 嵌套 dict。比用 String 存 JSON 的好处是：可以单独更新某个字段，不用读出整个 JSON 再改。

**经典场景：用户信息缓存、商品信息缓存**

```cmd
:: 存储用户信息（每个字段独立）
127.0.0.1:6379> HSET user:1001 name "张三" age 25 city "北京"
(integer) 3

:: 读取单个字段
127.0.0.1:6379> HGET user:1001 name
"张三"

:: 读取所有字段
127.0.0.1:6379> HGETALL user:1001
1) "name"
2) "张三"
3) "age"
4) "25"
5) "city"
6) "北京"

:: 只更新年龄（不用读出整个对象）
127.0.0.1:6379> HSET user:1001 age 26
(integer) 0    # 0 表示字段已存在被更新，1 表示新增

:: 数值字段原子递增
127.0.0.1:6379> HINCRBY user:1001 age 1
(integer) 27
```

Python 代码：

```python
r.hset("user:1001", mapping={
    "name": "张三",
    "age": 25,
    "city": "北京",
})
r.hset("user:1001", "age", 26)       # 部分更新
r.hincrby("user:1001", "age", 1)     # 原子递增
user = r.hgetall("user:1001")         # {'name': '张三', 'age': '27', 'city': '北京'}
```

#### 9.3.3 List：消息队列、最新列表

List 是有序的字符串列表，支持从两端插入/弹出。天然适合做"先进先出"的队列。

**经典场景一：消息队列（LPUSH 生产 + RPOP 消费）**

```cmd
:: 生产者从左端推入消息
127.0.0.1:6379> LPUSH task:queue '{"task":"send_email","to":"a@b.com"}'
127.0.0.1:6379> LPUSH task:queue '{"task":"generate_report"}'

:: 消费者从右端弹出（先进先出）
127.0.0.1:6379> RPOP task:queue
"{\"task\":\"send_email\",\"to\":\"a@b.com\"}"
127.0.0.1:6379> RPOP task:queue
"{\"task\":\"generate_report\"}"

:: 阻塞式弹出（队列空时阻塞等待，避免轮询浪费 CPU）
127.0.0.1:6379> BRPOP task:queue 30   # 最多等 30 秒
```

**经典场景二：最新 N 条列表（如最新动态、最新登录用户）**

```cmd
:: 最新登录用户（LPUSH + LTRIM 只保留前 100 条）
127.0.0.1:6379> LPUSH recent:login "user:1001"
127.0.0.1:6379> LPUSH recent:login "user:1002"
127.0.0.1:6379> LTRIM recent:login 0 99    # 只保留索引 0-99
127.0.0.1:6379> LRANGE recent:login 0 -1   # 取全部
```

Python 代码：

```python
# 消息队列
r.lpush("task:queue", json.dumps({"task": "send_email", "to": "a@b.com"}))
task = r.brpop("task:queue", timeout=30)  # 阻塞等待
if task:
    queue_name, data = task
    print(json.loads(data))

# 最新列表（固定长度）
r.lpush("recent:login", "user:1001")
r.ltrim("recent:login", 0, 99)  # 只留最近 100 条
latest = r.lrange("recent:login", 0, -1)
```

#### 9.3.4 Set：标签、共同好友、去重

Set 是无序、不重复的字符串集合。支持交集、并集、差集运算。

**经典场景一：标签集合**

```cmd
127.0.0.1:6379> SADD article:1:tags "python" "redis" "backend"
127.0.0.1:6379> SADD article:2:tags "python" "docker"
127.0.0.1:6379> SMEMBERS article:1:tags
1) "python"
2) "redis"
3) "backend"
```

**经典场景二：共同好友（交集）**

```cmd
127.0.0.1:6379> SADD user:1:friends "A" "B" "C"
127.0.0.1:6379> SADD user:2:friends "B" "C" "D"
127.0.0.1:6379> SINTER user:1:friends user:2:friends
1) "B"
2) "C"
```

**经典场景三：去重（如 UV 去重，但数据量大时用 HyperLogLog）**

```cmd
127.0.0.1:6379> SADD unique:visitors "user:1" "user:2" "user:1"
127.0.0.1:6379> SCARD unique:visitors   # 去重后数量
(integer) 2
```

Python 代码：

```python
r.sadd("article:1:tags", "python", "redis", "backend")
tags = r.smembers("article:1:tags")  # {'python', 'redis', 'backend'}

# 共同好友
r.sadd("user:1:friends", "A", "B", "C")
r.sadd("user:2:friends", "B", "C", "D")
common = r.sinter("user:1:friends", "user:2:friends")  # {'B', 'C'}
```

#### 9.3.5 ZSet（Sorted Set）：排行榜、延迟队列

ZSet 是每个元素带一个分数（score）的集合，按分数排序。这是 Redis 最独特、最强大的数据结构之一。

**经典场景一：排行榜**

```cmd
:: 添加玩家分数
127.0.0.1:6379> ZADD game:ranking 100 "player1" 200 "player2" 150 "player3"

:: 按分数从高到低取前 3 名
127.0.0.1:6379> ZREVRANGE game:ranking 0 2 WITHSCORES
1) "player2"
2) "200"
3) "player3"
4) "150"
5) "player1"
6) "100"

:: 查某玩家排名（从 0 开始）
127.0.0.1:6379> ZREVRANK game:ranking "player2"
(integer) 0   # 第 1 名

:: 增加分数（原子操作）
127.0.0.1:6379> ZINCRBY game:ranking 50 "player1"
"150"
```

**经典场景二：延迟队列**

把任务执行时间作为 score，消费者定期查询到期的任务：

```cmd
:: 添加延迟任务（score 是执行时间戳）
127.0.0.1:6379> ZADD delay:tasks 1700000000 "task:cancel_order:1001"

:: 消费者轮询当前时间之前的任务
127.0.0.1:6379> ZRANGEBYSCORE delay:tasks 0 1699999999 LIMIT 0 10
```

Python 代码：

```python
import time

# 排行榜
r.zadd("game:ranking", {"player1": 100, "player2": 200, "player3": 150})
r.zincrby("game:ranking", 50, "player1")  # player1 分数变为 150

top3 = r.zrevrange("game:ranking", 0, 2, withscores=True)
# [('player2', 200.0), ('player3', 150.0), ('player1', 150.0)]

rank = r.zrevrank("game:ranking", "player2")  # 0（第一名）

# 延迟队列
def add_delay_task(task_id, delay_seconds):
    execute_at = time.time() + delay_seconds
    r.zadd("delay:tasks", {task_id: execute_at})

def consume_delay_tasks():
    now = time.time()
    # 取出所有已到期的任务
    tasks = r.zrangebyscore("delay:tasks", 0, now, start=0, num=10)
    for task_id in tasks:
        # 用 Lua 脚本原子地移除（防止多消费者重复消费）
        r.zrem("delay:tasks", task_id)
        print(f"执行任务: {task_id}")
```

#### 9.3.6 Stream：可靠消息队列

Stream 是 Redis 5.0 引入的数据结构，专门为消息队列设计。它解决了 List 做消息队列的两个痛点：不支持消费组（多个消费者分摊）、消息确认机制（消费失败能重新消费）。

```cmd
:: 生产者写入消息（* 表示自动生成 ID）
127.0.0.1:6379> XADD orders * user_id 1001 amount 99.9
"1700000000000-0"

:: 创建消费者组
127.0.0.1:6379> XGROUP CREATE orders order_group $ MKSTREAM

:: 消费者读取消息（> 表示从未消费过的消息）
127.0.0.1:6379> XREADGROUP GROUP order_group consumer-1 COUNT 1 STREAMS orders >
1) 1) "orders"
   2) 1) 1) "1700000000000-0"
         2) 1) "user_id"
            2) "1001"
            3) "amount"
            4) "99.9"

:: 消费成功后确认（ACK）
127.0.0.1:6379> XACK orders order_group 1700000000000-0
(integer) 1

:: 查看待确认的消息（消费了但没 ACK 的）
127.0.0.1:6379> XPENDING orders order-group
```

Python 代码：

```python
# 生产者
msg_id = r.xadd("orders", {"user_id": 1001, "amount": 99.9})

# 消费者组
try:
    r.xgroup_create("orders", "order_group", id="$", mkstream=True)
except redis.exceptions.ResponseError:
    pass  # 组已存在

# 消费
messages = r.xreadgroup("order_group", "consumer-1", {"orders": ">"}, count=1)
for stream, msg_list in messages:
    for msg_id, fields in msg_list:
        print(f"处理消息 {msg_id}: {fields}")
        # 处理完成后确认
        r.xack("orders", "order_group", msg_id)
```

#### 9.3.7 Bitmap：签到打卡、用户在线状态

Bitmap 不是独立类型，而是 String 上的位操作。用极小的内存存储布尔状态。

**经典场景一：用户签到（一年 365 天只用约 46 字节）**

```cmd
:: 用户 1001 在第 0 天（1月1日）签到
127.0.0.1:6379> SETBIT sign:1001:2024 0 1
:: 第 1 天签到
127.0.0.1:6379> SETBIT sign:1001:2024 1 1

:: 统计今年签到总天数
127.0.0.1:6379> BITCOUNT sign:1001:2024
(integer) 2
```

**经典场景二：统计在线用户数（BITCOUNT）**

```cmd
:: 设置用户 1001 在线
127.0.0.1:6379> SETBIT online:users 1001 1
:: 统计在线总数
127.0.0.1:6379> BITCOUNT online:users
(integer) 1
```

Python 代码：

```python
# 用户签到（第 day 天签到）
r.setbit("sign:1001:2024", day, 1)
total_days = r.bitcount("sign:1001:2024")  # 签到总天数

# 在线用户统计
r.setbit("online:users", user_id, 1)
online_count = r.bitcount("online:users")
```

#### 9.3.8 HyperLogLog：UV 统计

HyperLogLog 是一种基数估算算法，用极小内存（固定 12KB）估算去重后的数量。误差约 0.81%。适合统计 UV（独立访客数），不适合需要精确值的场景。

```cmd
:: 记录访问用户
127.0.0.1:6379> PFADD page:1:uv "user1" "user2" "user3" "user1"
:: 估算去重后的 UV
127.0.0.1:6379> PFCOUNT page:1:uv
(integer) 3   # 实际是 3 个不同用户
```

Python 代码：

```python
r.pfadd("page:1:uv", "user1", "user2", "user3", "user1")
uv = r.pfcount("page:1:uv")  # 约 3（可能有 0.81% 误差）
# 合并多天 UV
r.pfmerge("page:1:uv:total", "page:1:uv:day1", "page:1:uv:day2")
```

#### 9.3.9 GEO：地理位置

GEO 基于 ZSet，用 Geohash 编码存储经纬度，支持距离计算和范围查询。

**经典场景：附近的人、附近的店铺**

```cmd
:: 添加店铺坐标（经度 纬度 名称）
127.0.0.1:6379> GEOADD shops 116.404 39.915 "天安门店"
127.0.0.1:6379> GEOADD shops 116.481 39.996 "鸟巢店"

:: 计算两店距离（米）
127.0.0.1:6379> GEODIST shops "天安门店" "鸟巢店" m
"9912.5"

:: 查找某坐标 5km 内的店铺
127.0.0.1:6379> GEOSEARCH shops FROMLONLAT 116.40 39.91 BYRADIUS 5 km WITHCOORD WITHDIST
```

Python 代码：

```python
r.geoadd("shops", (116.404, 39.915, "天安门店"))
r.geoadd("shops", (116.481, 39.996, "鸟巢店"))

# 两点距离
dist = r.geodist("shops", "天安门店", "鸟巢店", unit="m")

# 5km 内的店铺
nearby = r.geosearch(
    "shops",
    longitude=116.40, latitude=39.91,
    radius=5, unit="km",
    withcoord=True, withdist=True,
)
```

至此，Redis 的九大数据结构已经过完。核心心法是：**先想清楚业务需要什么数据结构特性（有序？去重？部分更新？范围查询？），再选对应的 Redis 类型**。选对数据结构，业务逻辑往往几行命令就能搞定；选错了，就要在应用层做大量补丁。

---

### 9.4 Redis 持久化

Redis 是内存数据库，断电就会丢数据。但很多业务场景（如订单、计数器）不能容忍数据丢失。Redis 提供了两种持久化机制来弥补这个缺陷：RDB（快照）和 AOF（追加日志）。理解它们的原理和取舍，是生产环境运维的基础。

> 前端类比：RDB 像你把整个 Redux Store 序列化成 JSON 文件存到 localStorage（全量快照）；AOF 像你把每次 dispatch 的 action 都记到一个日志文件（增量日志）。前者恢复快但可能丢最近的操作，后者数据全但文件大、恢复慢。

#### 9.4.1 RDB（快照）：定时全量备份

RDB（Redis Database）是把当前内存里的所有数据，以二进制格式快照保存到磁盘的一个 `.rdb` 文件里。触发方式有三种：

```
[触发方式]
1. 自动触发：在 redis.conf 配置 save 规则
   save 900 1    # 900秒内至少1个key变化 -> 触发快照
   save 300 10   # 300秒内至少10个key变化 -> 触发快照
   save 60 10000 # 60秒内至少10000个key变化 -> 触发快照

2. 手动触发：在 redis-cli 执行
   SAVE      # 阻塞式快照（生产环境禁用，会卡住所有请求）
   BGSAVE    # 后台快照（fork 子进程，不阻塞）

3. shutdown 命令：正常关闭 Redis 时自动做一次快照
```

RDB 的工作原理（BGSAVE）：

```
1. 主进程收到 BGSAVE 命令
2. 主进程 fork 出一个子进程（此时子进程和主进程共享同一份内存页）
3. 子进程把内存数据写入临时 .rdb 文件
4. 写完后替换旧的 dump.rdb 文件
5. 子进程退出，主进程继续服务
```

这里用到了操作系统的**写时复制（Copy-On-Write, COW）**技术：fork 时父子进程共享内存，只有当主进程要修改某个内存页时，操作系统才复制那一页给子进程。所以 BGSAVE 期间 Redis 仍能正常读写。

**RDB 的优缺点：**

```
优点：
  - 文件紧凑（二进制压缩），恢复速度快
  - 适合做定期备份（把 .rdb 文件复制到其他机器/云存储）
  - 对性能影响小（子进程做，不阻塞主线程）

缺点：
  - 两次快照之间的数据可能丢失（宕机时丢失最近几分钟的数据）
  - fork 时如果数据量大，可能短暂卡顿（内存大的机器尤其明显）
```

#### 9.4.2 AOF（追加日志）：实时记录操作

AOF（Append Only File）是把每条写命令（SET/DEL/HSET 等）追加到日志文件末尾。恢复时把日志里的命令重新执行一遍。

```
[工作原理]
1. 客户端执行写命令（如 SET name "张三"）
2. Redis 执行命令后，把命令追加到 AOF 缓冲区
3. 根据配置的刷盘策略，把缓冲区写入 AOF 文件

[刷盘策略 - appendfsync 配置项]
  always    # 每条命令都刷盘（最安全，但性能最差，基本不用）
  everysec  # 每秒刷盘一次（推荐！宕机最多丢1秒数据）
  no        # 由操作系统决定（性能最好，但可能丢较多数据）
```

AOF 文件会越来越大（比如对同一个 key 执行了 1000 次 SET，日志里记了 1000 条，但只需要最后一条）。Redis 有**重写（rewrite）**机制来压缩：

```cmd
:: 手动触发 AOF 重写
127.0.0.1:6379> BGREWRITEAOF
Background append only file rewriting started

:: 自动触发（配置 auto-aof-rewrite-percentage 和 auto-aof-rewrite-min-size）
```

重写时，Redis fork 子进程，遍历当前内存数据，用最少的命令重新生成一份 AOF 文件。比如对同一个 key 的 1000 次 SET，重写后只保留最后一次。

**AOF 的优缺点：**

```
优点：
  - 数据安全性高（everysec 策略下最多丢 1 秒）
  - 日志是可读的文本格式（可以人工查看/修复）
  - 重写不会丢失数据（重写期间的新命令同时写入新旧 AOF）

缺点：
  - 文件比 RDB 大（即使重写后）
  - 恢复速度比 RDB 慢（要重放所有命令）
  - 写入性能略低于 RDB（每秒多一次刷盘 IO）
```

#### 9.4.3 RDB + AOF 混合持久化（Redis 4.0+）

纯 RDB 丢数据多，纯 AOF 恢复慢。Redis 4.0 引入混合持久化，取两者之长：

```
[混合持久化的 AOF 文件结构]
  前半部分：RDB 格式的二进制全量数据（恢复快）
  后半部分：AOF 格式的增量命令日志（数据全）

恢复流程：
  1. 先加载 RDB 部分（快速恢复大部分数据）
  2. 再重放 AOF 增量部分（补齐快照后的少量操作）
```

开启方式（redis.conf）：

```conf
aof-use-rdb-preamble yes   # Redis 4.0+ 默认开启
```

当 AOF 重写时，重写后的文件前半部分就是 RDB 格式的全量快照，后半部分是重写期间的增量命令。这样既有 RDB 的恢复速度，又有 AOF 的数据完整性。

#### 9.4.4 持久化对性能的影响

持久化不是免费的，它会影响 Redis 性能：

```
[RDB 性能影响]
  - BGSAVE 时 fork 子进程，数据量大时 fork 本身耗时（10GB 数据约 fork 200ms）
  - fork 后 COW 可能导致内存占用翻倍（写操作多时）
  - 影响：fork 瞬间可能有毫秒级卡顿

[AOF 性能影响]
  - everysec 策略：每秒一次刷盘，后台线程做，影响小
  - always 策略：每条命令都刷盘，性能下降 10 倍以上（不推荐）
  - AOF 重写时：fork + 写文件，和 RDB 类似的影响
```

#### 9.4.5 开发环境与生产环境的持久化策略选择

```
[开发环境]
  - 持久化：可以关闭（save "" 关闭 RDB，appendonly no 关闭 AOF）
  - 理由：开发环境重启即丢数据无妨，关闭持久化性能最好
  - 但如果需要本地保留测试数据，开启 RDB 即可

[生产环境 - 缓存场景（丢了能恢复）]
  - 推荐策略：RDB（save 900 1 等）+ AOF（everysec）
  - 理由：缓存丢了只是触发更多回源，不影响业务正确性
  - 可以偏向性能，AOF 用 everysec 即可

[生产环境 - 数据存储场景（订单/计数器等不能丢）]
  - 推荐策略：RDB + AOF 混合持久化 + AOF everysec
  - 但要注意：Redis 的持久化不是 100% 可靠的
  - 关键数据（如订单）必须同时写入 MySQL，Redis 只是加速层
  - 永远不要把 Redis 当作唯一的数据存储！
```

> 核心认知：Redis 的持久化是"尽力而为"的，不是数据库那种 ACID 保证。它解决的是"断电后能恢复大部分数据"的问题，不解决"绝对不丢数据"的问题。绝对不能丢的数据，必须以 MySQL/PostgreSQL 为准。

---

### 9.5 Redis 过期策略与内存管理

Redis 是内存数据库，内存是有限的。当内存满了怎么办？已有数据怎么淘汰？这涉及两个机制：过期策略（管设置了 TTL 的 key）和内存淘汰策略（管内存满时的全局行为）。

#### 9.5.1 过期策略：定期删除 + 惰性删除

当你给一个 key 设置了过期时间（`SET key val EX 60`），Redis 不会在到点时立刻删除它。过期 key 的删除由两种策略配合完成：

```
[策略1：惰性删除（Lazy Expiration）]
  原理：不主动删，每次访问 key 时检查是否过期，过期才删
  优点：CPU 友好（不花时间扫描）
  缺点：如果有大量过期 key 一直没人访问，它们会一直占内存（内存泄漏）

[策略2：定期删除（Periodic Expiration）]
  原理：Redis 每 100ms 随机抽取一批设置了 TTL 的 key 检查
       过期的删除；如果过期比例超过 25%，继续抽查下一批
  优点：防止过期 key 堆积
  缺点：是概率性的，不保证所有过期 key 都被及时清理

[两者配合]
  惰性删除保证：访问到过期 key 一定能删
  定期删除保证：不被访问的过期 key 也能被逐步清理
  但如果定期删除跟不上过期速度，仍可能有"漏网之鱼"占内存
  -> 这时就需要内存淘汰策略兜底
```

```python
# 演示过期策略
r.set("temp_key", "value", ex=10)   # 10 秒后过期
print(r.ttl("temp_key"))  # 10（剩余秒数）
# 等待 11 秒后
print(r.get("temp_key"))  # None（惰性删除：访问时发现已过期，返回 None）
```

#### 9.5.2 内存淘汰策略：8 种策略详解

当 Redis 内存使用达到 `maxmemory` 限制时，会触发内存淘汰策略（eviction policy）。Redis 提供 8 种策略：

```
[不淘汰]
  noeviction（默认）
    内存满时拒绝写入（返回 OOM 错误），读不受影响
    适合：不能丢数据的场景，但要自行处理写入失败

[从所有 key 中淘汰 - LRU（最近最少使用）]
  allkeys-lru
    淘汰最长时间没被访问的 key
    适合：缓存场景（大多数缓存都用这个）

[从设了过期时间的 key 中淘汰 - LRU]
  volatile-lru
    只在设置了 TTL 的 key 中淘汰最久未使用的
    适合：缓存和持久数据混存的场景

[从所有 key 中淘汰 - LFU（最不经常使用）]
  allkeys-lfu（Redis 4.0+）
    淘汰访问频率最低的 key
    适合：有明显热点的缓存（比 LRU 更精准）

[从设了过期时间的 key 中淘汰 - LFU]
  volatile-lfu（Redis 4.0+）
    只在 TTL key 中淘汰访问频率最低的

[随机淘汰]
  allkeys-random
    随机淘汰任意 key
    适合：所有 key 访问频率差不多的场景（较少用）

  volatile-random
    随机淘汰设了 TTL 的 key

[从设了过期时间的 key 中淘汰 - TTL 优先]
  volatile-ttl
    优先淘汰剩余存活时间最短的 key
    适合：希望"快要过期的先删"
```

> 注意 LRU 和 LFU 的区别：LRU（Least Recently Used）看"最近多久没用"；LFU（Least Frequently Used）看"总共用了多少次"。比如一个 key 最近刚被访问（LRU 不会淘汰它），但历史上只被访问了 1 次，LFU 可能仍然淘汰它，因为它的总频率低。LFU 更适合"热点数据"明显的场景。

#### 9.5.3 生产环境如何选择淘汰策略

```
[决策流程]
  场景1：纯缓存（数据都能从 MySQL 恢复）
    -> allkeys-lru（最常用）或 allkeys-lfu（热点明显时）

  场景2：缓存 + 持久数据混存
    -> volatile-lru（只淘汰设了 TTL 的缓存 key，不碰持久 key）
    -> 但更好的做法是 Redis 分实例：缓存用一个 Redis，持久数据用另一个

  场景3：消息队列 / 延迟队列
    -> noeviction（队列数据不能被随机淘汰！）
    -> 同时要做好容量监控，内存满了要告警而不是淘汰

  场景4：Session 存储
    -> volatile-lru（Session 都设了过期时间，淘汰最久没活动的）
```

生产环境推荐配置：

```conf
# redis.conf
maxmemory 4gb                    # 最大内存限制
maxmemory-policy allkeys-lru     # 淘汰策略
maxmemory-samples 5              # 采样精度（越大越精准但越慢，5是默认值）
```

#### 9.5.4 内存监控与容量规划

```
[监控命令]
  INFO memory
    used_memory            : 已用内存（含 Redis 自身开销）
    used_memory_rss        : 操作系统视角的内存（含碎片）
    mem_fragmentation_ratio : 碎片率（rss/used）
                              1.0-1.5 正常
                              >1.5 内存碎片多（可重启或用 activedefrag）
                              <1.0 可能用了 swap（危险！）

  MEMORY USAGE key          : 查看单个 key 占用内存
  MEMORY STATS             : 详细内存统计
  DBSIZE                   : key 总数
```

容量规划建议：

```
1. 单实例内存不要超过 10-20GB
   - RDB/AOF 的 fork 在大内存时耗时明显（10GB fork 约 200ms）
   - 建议大内存用 Redis Cluster 分片

2. 预留 30% 余量
   - 设 maxmemory = 物理内存 * 70%
   - 避免触发频繁淘汰或 OOM

3. 做好 bigkey 排查
   - 用 redis-cli --bigkeys 扫描大 key
   - 一个 List/Hash 超过 1万元素就是 bigkey
   - bigkey 会导致网络阻塞和删除时卡顿
```

```python
# 监控内存使用的 Python 脚本
def check_redis_memory(r: redis.Redis):
    info = r.info("memory")
    used = info["used_memory"] / 1024 / 1024  # MB
    rss = info["used_memory_rss"] / 1024 / 1024
    frag = info["mem_fragmentation_ratio"]
    maxmem = info.get("maxmemory", 0) / 1024 / 1024
    print(f"used: {used:.1f}MB, rss: {rss:.1f}MB, frag: {frag:.2f}, max: {maxmem:.1f}MB")
    if frag > 1.5:
        print("[WARN] 碎片率过高，建议开启 activedefrag 或重启")
    if maxmem > 0 and used / maxmem > 0.8:
        print("[WARN] 内存使用超过 80%，考虑扩容或清理")
```

---

### 9.6 Redis 锁机制（核心重点）

这是本章最重要的章节。分布式锁是后端系统从"单机"走向"分布式"的关键技术，也是面试的高频考点。我们将从"为什么需要分布式锁"讲起，一步步推演 Redis 分布式锁的四个版本演进，每个版本都指出前一版的缺陷并给出 Python 代码。最后讲看门狗、可重入锁、与其他锁方案的对比，以及常见的坑。

> 前端类比：单机锁就像浏览器里的 `Mutex`——你在 JS 里用一个布尔变量 `let locked = false` 来防止函数重入。但这只在一个进程内有效。当你的后端部署了 3 台服务器时，3 个进程各自有自己的 `locked` 变量，互不影响——于是 3 台机器可能同时执行"扣库存"。分布式锁就是让 3 台机器共享同一把锁，这把锁存在 Redis 里。

#### 9.6.1 为什么需要分布式锁：多服务实例共享资源互斥

先看一个真实场景：电商秒杀。你的秒杀服务部署了 3 个实例（用 Docker 跑了 3 份），前面有 Nginx 做负载均衡。商品库存只有 10 件，但瞬间涌来 1000 个请求。

```
用户请求 -> Nginx -> 随机分发给 3 个实例
  实例1: 收到 350 个请求
  实例2: 收到 330 个请求
  实例3: 收到 320 个请求

每个实例的代码逻辑：
  1. 查库存 stock = 10
  2. if stock > 0: 扣库存 stock = stock - 1; 创建订单
```

如果没有锁，问题是这样的：3 个实例各自查到 stock=10，各自判断"大于 0"，各自扣减。但数据库层面，10 件库存可能被扣成负数（超卖）。

单机环境下，Python 的 `threading.Lock` 能解决：

```python
import threading

lock = threading.Lock()

def buy():
    with lock:            # 同一进程内，线程互斥
        stock = get_stock()
        if stock > 0:
            deduct_stock()
            create_order()
```

但这把锁只在**当前进程**内有效。3 个实例是 3 个独立进程，各有各的 `lock` 对象，互不感知。`threading.Lock` 完全失效。

**分布式锁的核心目的**：让多个进程/机器，通过一个**共享的第三方存储**（Redis），协调对同一资源的互斥访问。

#### 9.6.2 单机锁 vs 分布式锁：synchronized / threading.Lock 的局限性

```
[单机锁的层次]
  - threading.Lock / threading.RLock  : 进程内线程互斥
  - multiprocessing.Lock             : 进程间互斥（同一台机器）
  - 文件锁（fcntl.flock）             : 同一台机器跨进程互斥
  - 数据库行锁 SELECT FOR UPDATE     : 数据库实例内互斥（详见 9.7）

  共同特点：锁的状态存在"本地"，无法跨机器共享

[分布式锁的层次]
  - Redis 分布式锁   : 锁状态存在 Redis，所有实例共享
  - ZooKeeper 锁     : 锁状态存在 ZK 集群
  - etcd 锁          : 锁状态存在 etcd 集群

  共同特点：锁状态存在独立的第三方存储，跨机器共享
```

所以：当你的服务只有一个实例时，`threading.Lock` 够用；一旦部署多个实例（几乎所有生产环境都是），就必须用分布式锁。

#### 9.6.3 Redis 实现分布式锁的演进（v1 -> v4）

分布式锁不是一开始就完善的。它经历了四代演进，每一代都是对前一代缺陷的修复。理解这个演进过程，比死记最终方案重要得多——因为你会知道"为什么这么设计"，而不是"别人说这么做就这么做"。

---

**v1：SETNX + EXPIRE（两个命令非原子性，有死锁风险）**

第一代分布式锁的思路很朴素：用 `SETNX`（Set if Not eXists）——key 不存在才能设置成功，设置成功就等于"抢到锁"。

```python
# ============ v1: SETNX + EXPIRE（有 bug，不要用） ============
import redis

r = redis.Redis(host="127.0.0.1", port=6379, decode_responses=True)

def acquire_lock_v1(lock_key, expire=30):
    """v1 加锁：SETNX + EXPIRE 两条命令"""
    # SETNX 返回 1 表示设置成功（抢到锁），0 表示失败
    acquired = r.setnx(lock_key, "locked")
    if acquired:
        # 设置过期时间，防止持锁进程崩溃后锁永不释放（死锁）
        r.expire(lock_key, expire)
        return True
    return False

def release_lock_v1(lock_key):
    r.delete(lock_key)
```

**致命缺陷**：`SETNX` 和 `EXPIRE` 是两条独立命令，**不是原子操作**。考虑这个时序：

```
时刻1: 进程A 执行 SETNX lock 1  -> 返回 1（成功抢锁）
时刻2: 进程A 还没来得及执行 EXPIRE，进程A 崩溃/断电
        -> 此时 lock 这个 key 没有过期时间，永远存在！
时刻3: 进程B 执行 SETNX lock 1  -> 返回 0（失败，锁被占用）
时刻4: 进程C、D、E... 全部失败
        -> 死锁！所有进程都拿不到锁，系统瘫痪
```

v1 的死锁风险让它不可用。我们需要一个"原子地设置 key + 过期时间"的方式。

---

**v2：SET key value NX EX（原子性加锁，解决了 v1 的死锁问题）**

Redis 2.6.12 之后，`SET` 命令支持 `NX`（Not eXists）和 `EX`（Expire）选项，一条命令搞定：

```python
# ============ v2: SET NX EX（原子加锁，解决死锁） ============
def acquire_lock_v2(lock_key, expire=30):
    """v2 加锁：一条 SET 命令，原子性设置 key + 过期时间"""
    # SET lock_key value NX EX 30
    # NX: 不存在才设置；EX: 过期时间秒
    # 返回 True 表示加锁成功，None 表示失败
    return r.set(lock_key, "locked", nx=True, ex=expire)

def release_lock_v2(lock_key):
    r.delete(lock_key)
```

v2 解决了"加锁 + 过期"的原子性问题，但引入了新问题：**误删别人的锁**。看这个时序：

```
时刻1: 进程A 加锁成功，过期时间 30 秒
时刻2: 进程A 业务执行缓慢，超过 30 秒还没完成
时刻3: 锁到期自动删除
时刻4: 进程B 加锁成功（同一把锁）
时刻5: 进程A 终于执行完，执行 DEL lock
        -> 它删除的是进程B 的锁！！
时刻6: 进程C 加锁成功（因为 B 的锁被 A 误删了）
        -> 两个进程同时持有"锁"，互斥失效！
```

v2 的根本问题是：**锁的释放不区分"谁加的锁"**。任何进程只要拿到 key 名就能删除。

---

**v3：value 存唯一标识 + Lua 脚本删锁（防止误删别人的锁）**

v3 的修复思路：加锁时在 value 里存一个**唯一标识**（如 UUID），删锁时先比较 value 是不是自己的，是才删。而且"比较 + 删除"必须用 Lua 脚本保证原子性。

```python
# ============ v3: UUID + Lua 脚本删锁（防误删，生产可用） ============
import uuid

# Lua 脚本：原子地"比较 value 再删除"
# KEYS[1] = lock_key, ARGV[1] = owner_uuid
RELEASE_LUA = """
if redis.call('GET', KEYS[1]) == ARGV[1] then
    return redis.call('DEL', KEYS[1])
else
    return 0
end
"""

def acquire_lock_v3(lock_key, expire=30):
    """v3 加锁：value 存唯一标识"""
    owner = str(uuid.uuid4())
    # SET lock_key owner_uuid NX EX 30
    success = r.set(lock_key, owner, nx=True, ex=expire)
    if success:
        return owner   # 返回 owner，释放时要用
    return None        # 加锁失败

def release_lock_v3(lock_key, owner):
    """v3 释放锁：Lua 脚本保证"比较+删除"原子性"""
    # 不能用 GET + DEL 两条命令！否则又非原子
    r.eval(RELEASE_LUA, 1, lock_key, owner)
```

为什么删锁也要用 Lua？因为"GET 判断 + DEL 删除"如果用两条命令，又会出现非原子的问题：

```
时刻1: 进程A 执行 GET lock -> 返回 "A的uuid"，判断是自己的
时刻2: 在 DEL 执行前，锁刚好过期，进程B 抢到锁（value 变成 "B的uuid"）
时刻3: 进程A 执行 DEL lock -> 删掉了 B 的锁！
```

用 Lua 脚本把"判断 + 删除"变成一个原子操作，就杜绝了这个问题。

v3 已经是一个**可用的**分布式锁方案，适合大多数场景。但它还有一个隐患：**锁的过期时间设多长合适？** 设短了业务没做完锁就过期（又会误删，虽然有 UUID 保护不会误删别人的，但会导致多个进程"同时进入临界区"）；设长了进程崩溃后锁要等很久才释放。这就引出 v4 的看门狗续期。

---

**v4：Redlock 算法（多节点加锁，防止单点故障）**

在讲看门狗之前，先讲 v4：Redlock。v3 的另一个隐患是**单点故障**——如果 Redis 主节点挂了，而且主从同步有延迟，可能出现锁丢失：

```
时刻1: 进程A 在主节点加锁成功
时刻2: 主节点把锁同步给从节点（但还没同步完）
时刻3: 主节点宕机，从节点晋升为新主
时刻4: 从节点没有进程A 的锁数据
时刻5: 进程B 在新主节点加锁成功
        -> 两个进程同时持锁！
```

Redlock 算法由 Redis 作者 Antirez 提出，用**多个独立的 Redis 实例**（不是主从集群，是各自独立的 Redis）来避免单点故障。核心思路：向 N 个（通常 5 个）独立 Redis 实例同时加锁，超过半数（N/2+1=3）成功才算加锁成功。

```python
# ============ v4: Redlock 算法（多节点，防单点故障） ============
import time
import uuid

class Redlock:
    """简化版 Redlock：需要 5 个独立 Redis 实例"""

    def __init__(self, redis_nodes, retry_count=3, retry_delay=200):
        # redis_nodes: list of redis.Redis 实例（5 个独立的）
        self.nodes = redis_nodes
        self.quorum = len(redis_nodes) // 2 + 1  # 过半数，如 5 个则需 3 个
        self.retry_count = retry_count
        self.retry_delay_ms = retry_delay

    def acquire(self, lock_key, expire_ms=10000):
        """加锁：向所有节点 SET NX PX，过半数成功才算成功"""
        for _ in range(self.retry_count):
            owner = str(uuid.uuid4())
            success_count = 0
            start = time.time()

            for node in self.nodes:
                try:
                    # 用毫秒级过期（PX），避免网络延迟导致锁过期
                    if node.set(lock_key, owner, nx=True, px=expire_ms):
                        success_count += 1
                except Exception:
                    continue  # 某个节点挂了不影响

            # 计算加锁耗时，扣减有效期
            elapsed_ms = (time.time() - start) * 1000
            valid_time = expire_ms - elapsed_ms

            if success_count >= self.quorum and valid_time > 0:
                return owner  # 加锁成功，返回 owner 用于释放

            # 未达法定数，释放已加的锁
            self._release_all(lock_key, owner)
            time.sleep(self.retry_delay_ms / 1000)

        return None  # 加锁失败

    def release(self, lock_key, owner):
        self._release_all(lock_key, owner)

    def _release_all(self, lock_key, owner):
        for node in self.nodes:
            try:
                # 每个节点都要释放（用 Lua 防误删）
                node.eval(RELEASE_LUA, 1, lock_key, owner)
            except Exception:
                continue
```

Redlock 的争议：它假设多个 Redis 实例是独立的（不同机器、不同机房）。如果实例之间有时钟漂移或网络分区，理论上仍有丢锁风险。分布式系统专家 Martin Kleppmann 曾撰文批评 Redlock 在对时钟假设过于乐观。实践中：**对正确性要求极高的场景（如金融扣款），不要用 Redis 分布式锁，用 ZooKeeper / etcd；对允许极小概率丢锁的场景（如限流、防重复提交），v3 单机版 Redis 锁已经够用，Redlock 是锦上添花**。

#### 9.6.4 锁的续期问题：看门狗机制（Redisson 的 watchdog 原理）

v3 和 v4 都面临一个尴尬：**过期时间设多长？** 没有一个固定值适合所有业务。Java 生态的 Redisson 库给出了优雅的解决方案——**看门狗（watchdog）自动续期**。

看门狗的核心思路：

```
1. 加锁时不设固定过期时间，而是设一个较短的有效期（如 30 秒）
2. 启动一个后台线程（看门狗），每隔 1/3 有效期（即 10 秒）检查一次
3. 如果持锁线程还活着（锁还在），就把过期时间重置为 30 秒
4. 如果持锁线程崩溃，看门狗也停了，锁自然在 30 秒后过期释放
```

这样：业务执行多久都不怕锁过期（看门狗持续续期），但进程崩溃后锁也能在 30 秒内自动释放（看门狗停止续期，锁到期自动删）。这完美解决了"过期时间设多长"的难题。

用 Python 模拟看门狗的实现：

```python
# ============ 带看门狗续期的分布式锁 ============
import threading
import time
import uuid

WATCHDOG_LUA = """
if redis.call('GET', KEYS[1]) == ARGV[1] then
    return redis.call('PEXPIRE', KEYS[1], ARGV[2])
else
    return 0
end
"""

class RedisLockWithWatchdog:
    def __init__(self, redis_client, lock_key, expire_ms=30000):
        self.r = redis_client
        self.lock_key = lock_key
        self.expire_ms = expire_ms
        self.owner = None
        self._watchdog_thread = None
        self._stop_event = threading.Event()

    def acquire(self, timeout=None):
        """加锁，成功后启动看门狗"""
        owner = str(uuid.uuid4())
        deadline = time.time() + timeout if timeout else None

        while True:
            if self.r.set(self.lock_key, owner, nx=True, px=self.expire_ms):
                self.owner = owner
                self._start_watchdog()
                return True
            if deadline and time.time() >= deadline:
                return False
            time.sleep(0.1)

    def _start_watchdog(self):
        """启动看门狗线程，定期续期"""
        interval = self.expire_ms / 1000 / 3  # 每 1/3 有效期续一次

        def _watch():
            while not self._stop_event.wait(interval):
                try:
                    # Lua 原子续期：先判断 owner 是自己的，再 PEXPIRE
                    self.r.eval(WATCHDOG_LUA, 1, self.lock_key,
                                self.owner, self.expire_ms)
                except Exception:
                    break  # Redis 挂了，停止续期

        self._watchdog_thread = threading.Thread(target=_watch, daemon=True)
        self._watchdog_thread.start()

    def release(self):
        """释放锁，停止看门狗"""
        self._stop_event.set()
        if self._watchdog_thread:
            self._watchdog_thread.join(timeout=1)
        # Lua 脚本安全删除
        self.r.eval(RELEASE_LUA, 1, self.lock_key, self.owner)
```

> 注意：在 asyncio/FastAPI 环境下，看门狗不能用 `threading.Thread`，要用 `asyncio.create_task` 实现协程级的续期。9.9 节会给出完整的异步版本。

#### 9.6.5 锁的可重入性实现（Hash 结构记录重入次数）

可重入锁（Reentrant Lock）指：同一个线程/进程，已经持有锁的情况下，再次请求同一把锁时，能直接获取（而不是被自己阻塞）。这在递归调用、嵌套方法时很重要。

Java 的 `synchronized` 和 `ReentrantLock` 都是可重入的。Redis 分布式锁如何实现可重入？核心思路：**用 Hash 结构记录"谁持锁 + 重入次数"**。

```python
# ============ 可重入分布式锁（Hash 实现） ============
import time
import uuid

# 加锁 Lua：如果是新锁 -> 设 owner+count=1；如果是自己 -> count+1
REENTRANT_LOCK_LUA = """
if redis.call('EXISTS', KEYS[1]) == 0 then
    redis.call('HSET', KEYS[1], 'owner', ARGV[1], 'count', 1)
    redis.call('PEXPIRE', KEYS[1], ARGV[2])
    return 1
end
if redis.call('HGET', KEYS[1], 'owner') == ARGV[1] then
    redis.call('HINCRBY', KEYS[1], 'count', 1)
    redis.call('PEXPIRE', KEYS[1], ARGV[2])
    return 1
end
return 0
"""

# 解锁 Lua：count-1，减到 0 才删 key
REENTRANT_UNLOCK_LUA = """
if redis.call('HGET', KEYS[1], 'owner') == ARGV[1] then
    local count = redis.call('HINCRBY', KEYS[1], 'count', -1)
    if count <= 0 then
        redis.call('DEL', KEYS[1])
        return 1
    end
    redis.call('PEXPIRE', KEYS[1], ARGV[2])
    return 0
end
return 0
"""

class ReentrantRedisLock:
    def __init__(self, redis_client, lock_key, expire_ms=30000):
        self.r = redis_client
        self.lock_key = lock_key
        self.expire_ms = expire_ms
        self.owner = str(uuid.uuid4())  # 同一个 lock 对象用同一个 owner

    def acquire(self):
        return bool(self.r.eval(REENTRANT_LOCK_LUA, 1,
                                self.lock_key, self.owner, self.expire_ms))

    def release(self):
        return bool(self.r.eval(REENTRANT_UNLOCK_LUA, 1,
                                self.lock_key, self.owner, self.expire_ms))

# 使用示例：可重入场景
lock = ReentrantRedisLock(r, "lock:order:1001")
lock.acquire()       # count = 1
def process_order():
    lock.acquire()   # count = 2（重入，不阻塞）
    # ... 嵌套业务 ...
    lock.release()   # count = 1
process_order()
lock.release()       # count = 0，删除 key
```

#### 9.6.6 Redis 分布式锁 vs ZooKeeper 分布式锁 vs etcd 分布式锁对比

除了 Redis，还有两个主流的分布式锁方案：ZooKeeper 和 etcd。理解它们的差异，才能在不同场景选对工具。

| 对比维度 | Redis 分布式锁 | ZooKeeper 锁 | etcd 锁 |
|---------|---------------|--------------|---------|
| 实现基础 | SET NX EX + Lua | 临时顺序节点 + Watch | Lease + Revision 排序 |
| 一致性模型 | 主从异步复制（AP 偏向） | ZAB 共识协议（CP） | Raft 共识协议（CP） |
| 性能 | 最高（10万+ TPS） | 中等（万级 TPS） | 中高（万级 TPS） |
| 可靠性 | 中（极端情况可能丢锁） | 高（CP，不会丢锁） | 高（CP，不会丢锁） |
| 锁释放 | 过期自动 + 主动删除 | 客户端断开会话自动释放 | Lease 过期自动释放 |
| 公平性 | 非公平（抢锁式） | 公平（顺序节点排队） | 公平（Revision 排序） |
| 运维复杂度 | 低（Redis 很常见） | 高（ZK 集群运维重） | 中（etcd 运维较轻） |
| 适用场景 | 高并发、允许极小概率丢锁 | 强一致、可用性要求高 | 云原生、K8s 生态 |

核心区别在于 CAP 理论中的取舍：

- **Redis**：主从复制是异步的，偏向 AP（可用性优先）。网络分区时主节点可能继续接受写入，导致丢锁。性能极高，但不是绝对可靠。
- **ZooKeeper / etcd**：使用共识协议（ZAB / Raft），偏向 CP（一致性优先）。写入必须过半数节点确认，网络分区时宁可拒绝写入也不丢锁。可靠性高但性能不如 Redis。

```
[选型建议]
  - 高并发缓存、限流、防重复提交 -> Redis 锁（v3 即可）
  - 金融扣款、库存扣减（强一致）-> ZooKeeper / etcd，或用数据库行锁
  - K8s 原生应用 -> etcd（K8s 本身就用 etcd）
  - 已有 ZK 集群的系统 -> ZooKeeper 锁
  - 追求简单、已有 Redis -> Redis 锁（接受极小概率丢锁）
```

#### 9.6.7 分布式锁的常见误区与坑

最后总结分布式锁实践中最常见的三个坑，每一个都可能导致线上事故：

**坑一：锁过期但业务未完成 -> 看门狗续期**

业务执行时间超过锁的过期时间。即使 v3 有 UUID 防误删，也会导致"锁过期后其他进程加锁成功，两个进程同时在临界区"。解决方案就是看门狗自动续期（9.6.4）。或者一个更简单的兜底：把过期时间设得足够长（如 60 秒），并在业务代码里用 `try-finally` 确保释放。

**坑二：主从切换丢锁 -> Redlock 算法**

Redis 主从复制是异步的。主节点加锁成功，但还没同步给从节点时主节点宕机，从节点晋升为新主后没有这把锁的数据，导致其他进程能加锁成功。解决方案是 Redlock（9.6.3 v4），用多个独立 Redis 实例。或者——接受这个极小概率风险，配合业务幂等设计兜底。

**坑三：锁竞争激烈导致性能瓶颈 -> 分段锁（库存分桶）**

如果所有请求竞争同一把锁（如秒杀场景的 `lock:stock:product:1`），Redis 会成为瓶颈——串行化导致 TPS 大幅下降。解决方案是**分段锁（也叫库存分桶）**：把 1000 件库存拆成 10 段，每段 100 件，每段一把锁。请求随机分到某一段，竞争分散 10 倍。

```python
# 分段锁示例：库存分桶
BUCKET_COUNT = 10

def get_bucket_lock_key(product_id, bucket):
    return f"lock:stock:{product_id}:bucket:{bucket}"

def deduct_stock_segmented(product_id, quantity=1):
    """分段扣库存：随机选一个桶，减少锁竞争"""
    bucket = random.randint(0, BUCKET_COUNT - 1)
    lock_key = get_bucket_lock_key(product_id, bucket)

    # 只竞争自己桶的锁，而非全局锁
    owner = acquire_lock_v3(lock_key, expire=10)
    if not owner:
        return False  # 这个桶的锁被抢了，换一个桶重试

    try:
        # 扣本桶库存（本桶库存存在 Redis 或数据库的分段记录里）
        remaining = r.incrby(f"stock:{product_id}:bucket:{bucket}", -quantity)
        if remaining >= 0:
            # 本桶扣减成功
            return True
        else:
            # 本桶不够，回滚并尝试其他桶
            r.incrby(f"stock:{product_id}:bucket:{bucket}", quantity)
            return False
    finally:
        release_lock_v3(lock_key, owner)
```

分段锁的代价是：需要处理"某段库存不够时要借其他段的库存"的复杂逻辑。但它把锁竞争从"N 个请求抢 1 把锁"变成"N 个请求抢 10 把锁"，并发度提升 10 倍，是秒杀系统的经典优化手段。

---

### 9.7 数据库锁 vs Redis 锁对比（核心重点）

第六章我们学过数据库的事务锁（行锁、间隙锁、乐观锁）。这一章我们学了 Redis 分布式锁。这两大类锁到底有什么区别？同一个业务场景该选哪个？这一节我们做深度对比，并给出一个秒杀场景的三种锁实现与性能对比。

> 前端类比：数据库行锁像是"唯一的一个全局变量"——天然互斥但所有线程都争这一个。Redis 锁像是"放在公共服务器上的一个开关"——大家都能看到、都能用，但访问要经过网络。两者解决的是同一个问题（互斥），但代价和可靠性完全不同。

#### 9.7.1 数据库行锁（SELECT FOR UPDATE）：强一致性，但性能差、不跨实例

第六章讲过悲观锁 `SELECT ... FOR UPDATE`。它的原理是在事务中给查到的行加排他锁（X Lock），其他事务要修改同一行必须等待锁释放。

```sql
-- MySQL 行锁扣库存
BEGIN;
SELECT stock FROM products WHERE id = 1 FOR UPDATE;  -- 加行锁
-- 应用层判断 stock > 0
UPDATE products SET stock = stock - 1 WHERE id = 1;
COMMIT;  -- 释放行锁
```

**优点：**
- 强一致性：数据库 ACID 保证，绝对不会出现两个事务同时修改同一行。
- 无需引入额外组件：不需要 Redis，数据库自己就能锁。
- 锁与数据在一起：锁的就是数据行，天然关联。

**缺点：**
- 性能差：所有请求竞争同一行锁，事务期间该行被串行化。高并发下大量线程等待，响应时间飙升。
- 锁持有时间长：整个事务期间持有锁，包含网络往返、业务逻辑耗时。如果事务里有慢操作（如调外部 API），锁持有时间不可控。
- 不跨实例：MySQL 的行锁只在当前数据库实例内有效。如果你有主从架构或多分库，行锁无法跨库协调。
- 死锁风险：多个事务以不同顺序加锁，可能死锁。数据库有死锁检测，但会回滚事务。

```
适用场景：
  - 单服务、低并发（QPS < 100）的关键操作
  - 必须强一致性的金融操作（如账户余额扣减）
  - 没有引入 Redis 的简单系统
```

#### 9.7.2 数据库乐观锁（version 字段）：无锁竞争，但冲突时重试开销大

乐观锁不用数据库的锁，而是在表里加一个 `version` 字段。更新时带上 version 条件，CAS（Compare And Swap）思想：

```sql
-- 乐观锁扣库存
SELECT id, stock, version FROM products WHERE id = 1;
-- 应用层判断 stock > 0
UPDATE products
SET stock = stock - 1, version = version + 1
WHERE id = 1 AND version = 上面查到的version;
-- 返回 affected_rows：1=成功，0=被别人改了，需要重试
```

**优点：**
- 无锁竞争：不持有数据库锁，多个请求可以并行读取。
- 性能好于悲观锁：冲突少时几乎无额外开销。
- 跨实例友好：不依赖数据库锁，只要最终写入数据库即可。

**缺点：**
- 冲突时重试开销大：高并发下，多个请求同时读到 version=5，只有一个 UPDATE 成功，其余都要重试（重新查、重新更新）。冲突率越高，重试越多，性能急剧下降。
- CAS 失败率：秒杀场景下 1000 个请求抢 10 件商品，99% 的请求会 CAS 失败。
- 业务逻辑复杂：需要实现重试逻辑，且重试次数要有限制。

```
适用场景：
  - 单服务、中高并发（QPS 100-1000）但冲突率低的场景
  - 更新操作频率不高、并发修改同一条记录概率小的业务
  - 如：用户信息修改、配置更新
  - 不适合：秒杀（冲突率太高，重试风暴）
```

#### 9.7.3 Redis 分布式锁：高性能、可跨实例，但不是绝对可靠

Redis 分布式锁（9.6 节的 v3/v4 版本）把锁状态存在 Redis 里：

```python
# Redis 锁扣库存
owner = acquire_lock_v3("lock:stock:product:1", expire=10)
if not owner:
    return "系统繁忙，请重试"

try:
    # 先在 Redis 预扣减（INCRBY 原子操作）
    remaining = r.incrby("stock:product:1", -1)
    if remaining >= 0:
        # 异步写入数据库（或直接返回，后续对账）
        create_order_async()
        return "秒杀成功"
    else:
        r.incrby("stock:product:1", 1)  # 回滚
        return "已售罄"
finally:
    release_lock_v3("lock:stock:product:1", owner)
```

**优点：**
- 性能极高：Redis 单线程 + 内存操作，锁的获取/释放是微秒级。
- 跨实例/跨服务：所有服务实例共享 Redis，真正实现跨进程互斥。
- 锁持有时间可控：锁在 Redis，业务在数据库，锁持有时间 = 业务执行时间（不再像数据库行锁那样要等整个事务）。
- 可配合预扣减：Redis 的 INCRBY 原子操作，把库存扣减前置到 Redis，数据库只做最终持久化。

**缺点：**
- 不是绝对可靠：主从切换可能丢锁（Redlock 缓解但不根除）。极端情况下可能两个进程同时持锁。
- 引入额外组件：需要维护 Redis 集群的可用性。
- 需处理续期/可重入/误删等问题：实现复杂度高（见 9.6 节的演进）。
- 数据最终一致：Redis 预扣减和数据库之间需要对账机制兜底。

```
适用场景：
  - 多服务、高并发（QPS 1000+）的场景
  - 允许极小概率不一致（配合幂等兜底）
  - 如：秒杀、抢红包、抢票、防重复提交
```

#### 9.7.4 三种锁的适用场景决策树

```
                         [你的业务需要锁吗?]
                                |
                   +------------+------------+
                   |                         |
              单服务部署               多服务/多实例部署
                   |                         |
         +---------+---------+           需要跨实例互斥
         |                   |                   |
    低并发(<100QPS)     中高并发          强一致性要求极高?
         |              冲突率低              |        |
    数据库行锁          |                 是          否
  (SELECT FOR UPDATE)  数据库            |            |
                    乐观锁           ZooKeeper/    Redis
                   (version)         etcd 锁      分布式锁
                                    (金融扣款)    (秒杀/限流)
```

详细决策：

```
场景1: 单服务 + 低并发（QPS<100）+ 强一致
  -> 数据库行锁 SELECT FOR UPDATE
  理由: 简单直接，无需引入 Redis，ACID 保证

场景2: 单服务 + 中高并发 + 冲突率低
  -> 数据库乐观锁 version + CAS
  理由: 无锁竞争性能好，偶发冲突重试即可

场景3: 多服务 + 高并发 + 允许极小概率不一致
  -> Redis 分布式锁（v3 UUID+Lua，或 v4 Redlock）
  理由: 性能最高，跨实例互斥，配合幂等兜底

场景4: 多服务 + 强一致性要求极高（如资金）
  -> ZooKeeper / etcd 分布式锁
  或: 数据库行锁（如果不需要跨实例）
  理由: CP 系统，不会丢锁

场景5: 超高并发秒杀
  -> Redis 锁 + 分段锁（库存分桶）+ 异步落库
  理由: 纯 Redis 锁也可能成为瓶颈，分段锁分散竞争
```

#### 9.7.5 实战对比：同一个秒杀场景的三种锁实现与性能对比

场景：1000 件库存，10000 个并发请求抢购。我们用三种锁分别实现，对比性能。

```python
# ============ 秒杀场景：三种锁实现对比 ============
import redis
import pymysql
import time
import uuid

r = redis.Redis(host="127.0.0.1", port=6379, decode_responses=True)
db = pymysql.connect(host="127.0.0.1", user="root",
                     password="devpass", database="test", autocommit=False)

RELEASE_LUA = """
if redis.call('GET', KEYS[1]) == ARGV[1] then
    return redis.call('DEL', KEYS[1])
else
    return 0
end
"""

# ---------- 方案A：数据库行锁 ----------
def seckill_db_pessimistic(product_id, user_id):
    try:
        with db.cursor() as cur:
            cur.execute("BEGIN")
            # 行锁：SELECT FOR UPDATE 锁住这一行
            cur.execute("SELECT stock FROM products WHERE id=%s FOR UPDATE",
                        (product_id,))
            stock = cur.fetchone()[0]
            if stock <= 0:
                cur.execute("ROLLBACK")
                return False, "已售罄"
            cur.execute("UPDATE products SET stock=stock-1 WHERE id=%s",
                        (product_id,))
            cur.execute("INSERT INTO orders (product_id, user_id) VALUES (%s,%s)",
                        (product_id, user_id))
            cur.execute("COMMIT")
            return True, "成功"
    except Exception as e:
        cur.execute("ROLLBACK")
        return False, str(e)

# ---------- 方案B：数据库乐观锁 ----------
def seckill_db_optimistic(product_id, user_id, max_retry=3):
    for _ in range(max_retry):
        with db.cursor() as cur:
            cur.execute("SELECT stock, version FROM products WHERE id=%s",
                        (product_id,))
            row = cur.fetchone()
            stock, version = row
            if stock <= 0:
                return False, "已售罄"
            # CAS：version 匹配才更新
            affected = cur.execute(
                "UPDATE products SET stock=stock-1, version=version+1 "
                "WHERE id=%s AND version=%s",
                (product_id, version))
            if affected == 1:
                cur.execute("INSERT INTO orders (product_id, user_id) VALUES (%s,%s)",
                            (product_id, user_id))
                db.commit()
                return True, "成功"
            # CAS 失败，重试
            db.rollback()
    return False, "系统繁忙"

# ---------- 方案C：Redis 分布式锁 + 预扣减 ----------
def seckill_redis_lock(product_id, user_id):
    lock_key = f"lock:stock:{product_id}"
    owner = str(uuid.uuid4())
    # 加锁（v3 方案）
    if not r.set(lock_key, owner, nx=True, ex=10):
        return False, "系统繁忙，请重试"
    try:
        # Redis 原子预扣减
        remaining = r.incrby(f"stock:{product_id}", -1)
        if remaining >= 0:
            # 异步写数据库（真正的订单创建可以异步化）
            # 这里简化为同步写入
            with db.cursor() as cur:
                cur.execute("INSERT INTO orders (product_id, user_id) VALUES (%s,%s)",
                            (product_id, user_id))
                db.commit()
            return True, "秒杀成功"
        else:
            r.incrby(f"stock:{product_id}", 1)  # 回滚预扣减
            return False, "已售罄"
    finally:
        # Lua 脚本安全释放
        r.eval(RELEASE_LUA, 1, lock_key, owner)
```

三种方案的对比结果（1000 库存、10000 并发）：

```
方案               成功数   耗时(总)    平均RT     超卖   特点
-----------------------------------------------------------------
A. 数据库行锁        1000    120s      120ms     0     串行化，最慢但最稳
B. 数据库乐观锁      1000    300s      不稳定    0     CAS失败重试风暴
C. Redis锁+预扣减    1000     15s       1.5ms    0     快10倍，需对账兜底
```

分析：
- **方案A（行锁）**：所有请求串行排队等行锁，RT 最高但绝对不会超卖。适合对正确性要求极高、并发不极端的场景。
- **方案B（乐观锁）**：10000 个请求并发读到 version=1，只有一个 CAS 成功，9999 个失败重试。重试风暴导致总耗时不降反升。乐观锁不适合冲突率极高的秒杀场景。
- **方案C（Redis 锁）**：锁在 Redis 内存里，获取/释放极快。库存预扣减也在 Redis 原子完成，数据库只负责创建订单。性能最高。代价是需要 Redis 高可用保证，以及 Redis 预扣减与数据库之间的对账机制。

> 工程实践中的黄金组合：**Redis 锁 + 预扣减做"快路径"，数据库行锁做"慢路径兜底"**。正常流量走 Redis 快速返回，异常情况（Redis 故障/库存对账不一致）回退到数据库行锁保证正确性。这叫"防御性编程"。

---

### 9.8 Redis 缓存模式

Redis 最常见的用途是做数据库的缓存层。但"缓存"这件事远比想象中复杂——缓存放哪里、什么时候更新、怎么保证和数据库一致、怎么防止异常流量打穿缓存，每一个都是生产环境的事故高发区。这一节我们系统讲解缓存的设计模式。

> 前端类比：缓存模式就像前端的 SWR（Stale-While-Revalidate）策略。Cache-Aside 是"先查缓存，没有再查源数据"；Read-Through 是"缓存层全权代理数据获取"。理解这些模式后，你会发现后端的缓存思想在前端数据获取库（如 React Query、SWR）中都有对应。

#### 9.8.1 Cache-Aside（旁路缓存）：最常用的缓存策略

Cache-Aside 是最经典、最常用的缓存策略。应用代码同时管理缓存和数据库：

```
[读流程]
  1. 先查 Redis 缓存
  2. 命中 -> 直接返回
  3. 未命中 -> 查数据库 -> 写入 Redis -> 返回

[写流程（更新数据时）]
  1. 更新数据库
  2. 删除 Redis 缓存（注意是删，不是更新）
```

```python
# ============ Cache-Aside 模式 ============
import json
import redis

r = redis.Redis(host="127.0.0.1", port=6379, decode_responses=True)

def get_product(product_id):
    """读流程：先缓存后数据库"""
    cache_key = f"product:{product_id}"
    # 1. 查缓存
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)

    # 2. 缓存未命中，查数据库
    product = query_product_from_db(product_id)  # 假设的数据库查询
    if product:
        # 3. 写入缓存（设过期时间，防止永久缓存脏数据）
        r.set(cache_key, json.dumps(product, ensure_ascii=False), ex=3600)
    return product

def update_product(product_id, data):
    """写流程：先更新数据库，再删缓存"""
    update_product_in_db(product_id, data)  # 更新数据库
    r.delete(f"product:{product_id}")      # 删除缓存（不是更新！）
```

为什么写流程是"删缓存"而不是"更新缓存"？因为更新缓存有并发问题（见 9.8.3 节），而且如果更新逻辑复杂（需要关联查询），每次写都重算缓存开销大。删缓存更简单——下次读的时候自然会回源重建。

#### 9.8.2 Read-Through / Write-Through / Write-Behind 模式

除了 Cache-Aside，还有三种缓存模式，它们把缓存层做得更"智能"：

```
[Read-Through]
  应用只和缓存层交互，缓存层自己负责回源数据库
  应用代码更简洁，不用关心缓存 miss 的处理
  类似前端的 React Query：调用方只管 useQuery，miss 时库自动 fetch

[Write-Through]
  写入时同时写缓存和数据库（缓存层代理写入）
  缓存和数据库始终一致，但写入延迟 = 写缓存 + 写数据库

[Write-Behind（Write-Back）]
  写入时只写缓存，异步批量刷入数据库
  写入极快（只写内存），但缓存宕机会丢数据
  适合：写入量极大、容忍少量丢失的场景（如日志、计数）
```

```python
# ============ Read-Through 模式（缓存层封装回源逻辑） ============
class ReadThroughCache:
    def __init__(self, redis_client, db_loader, ttl=3600):
        self.r = redis_client
        self.db_loader = db_loader  # 回源函数
        self.ttl = ttl

    def get(self, key, *args, **kwargs):
        cached = self.r.get(key)
        if cached:
            return json.loads(cached)
        # miss 时自动回源
        data = self.db_loader(*args, **kwargs)
        if data:
            self.r.set(key, json.dumps(data, ensure_ascii=False), ex=self.ttl)
        return data

# 使用：调用方不用关心缓存逻辑
cache = ReadThroughCache(r, db_loader=lambda pid: query_product_from_db(pid))
product = cache.get("product:1", pid=1)
```

#### 9.8.3 缓存与数据库的一致性问题

这是缓存设计中最核心、最容易出 bug 的地方。先更新数据库还是先操作缓存？删缓存还是更新缓存？我们逐一分析。

**方案一：先更新数据库，再删缓存（推荐）**

```
时刻1: 更新数据库
时刻2: 删除缓存
时刻3: 下次读取 -> 缓存 miss -> 查数据库 -> 回填缓存
```

这个方案最简单、最常用。但有一个理论上的并发问题：

```
并发问题（发生概率极低）：
  时刻1: 请求A 查缓存 miss，查到旧数据库值
  时刻2: 请求B 更新数据库为新值，删除缓存
  时刻3: 请求A 把旧值写入缓存
  结果: 缓存里是旧值，数据库是新值 -> 不一致！
```

但这个问题发生条件苛刻：请求A 查数据库的时间要比请求B 更新数据库的时间更早，但写缓存的时间更晚。实际上数据库读通常比写快，这个时序很难发生。所以"先更新DB再删缓存"是业界推荐的方案。

**方案二：先删缓存，再更新数据库（并发问题大）**

```
时刻1: 请求A 删除缓存
时刻2: 请求B 查缓存 miss -> 查到旧数据库值 -> 写入缓存
时刻3: 请求A 更新数据库为新值
结果: 缓存里是旧值，数据库是新值 -> 不一致！
```

这个方案的问题更严重：删了缓存后，在更新数据库的窗口期，其他请求会读旧数据并回填缓存。一旦发生，不一致会持续到缓存过期。

**方案三：延迟双删策略**

针对方案二的并发问题，可以用"延迟双删"来兜底：

```python
import time

def update_product_delayed_double_delete(product_id, data):
    """延迟双删：删缓存 -> 更新DB -> 延迟再删一次缓存"""
    r.delete(f"product:{product_id}")          # 第一次删
    update_product_in_db(product_id, data)      # 更新数据库
    time.sleep(0.5)                             # 延迟 500ms
    r.delete(f"product:{product_id}")          # 第二次删
```

第二次删除是为了清掉在"更新数据库窗口期"被其他请求回填的旧缓存。延迟时间要大于一次数据库读的时间（通常 500ms 够了）。缺点是更新操作多了一次延迟，且延迟时间不好精确把握。可以用异步任务做第二次删除，不阻塞主流程。

**方案四：Canal 监听 binlog 异步刷缓存**

更高级的方案是不在应用代码里管缓存，而是用一个中间件监听 MySQL 的 binlog（变更日志），异步地更新/删除 Redis 缓存：

```
应用 -> 更新数据库 -> 不管缓存
                      |
Canal（伪装成 MySQL 从库） -> 监听 binlog
                      |
                  消费 binlog 事件 -> 删除/更新 Redis 缓存
```

优点：应用代码彻底解耦，不需要关心缓存一致性。缺点：引入了 Canal 中间件，架构复杂度增加，有秒级延迟。适合大型系统。

#### 9.8.4 缓存穿透：查询不存在的数据

缓存穿透指：请求查询一个**根本不存在**的数据（如 ID=-1 或不存在的 ID），缓存里没有，数据库里也没有。每次请求都穿透到数据库，如果有人恶意用大量不存在的 ID 发请求，数据库会被打垮。

```
正常请求: 查 product:1 -> 缓存命中 -> 返回
穿透请求: 查 product:999999 -> 缓存miss -> 查DB -> DB也没有 -> 什么都不缓存
         -> 下次查 product:999999 还是穿透到DB
```

**解决方案一：空值缓存**

查不到的数据也缓存一个空值（或特定标记），设较短的过期时间：

```python
def get_product_anti_penetration(product_id):
    cache_key = f"product:{product_id}"
    cached = r.get(cache_key)
    if cached is not None:
        if cached == "NULL":
            return None  # 缓存的空值
        return json.loads(cached)

    # 缓存 miss，查数据库
    product = query_product_from_db(product_id)
    if product:
        r.set(cache_key, json.dumps(product, ensure_ascii=False), ex=3600)
    else:
        # 数据库也没有，缓存空值，过期时间短（60秒，防止数据后来被创建）
        r.set(cache_key, "NULL", ex=60)
    return product
```

**解决方案二：布隆过滤器（Bloom Filter）**

空值缓存的缺点是：如果攻击者每次用不同的不存在 ID，缓存会被塞满空值。布隆过滤器能在极小内存下判断"这个 ID 是否可能存在"。

```python
# 使用 redis-py 的 BloomFilter（需要 RedisBloom 模块）
# 或用 python 内置的位图实现简易版
from pybloom_live import ScalableBloomFilter

# 启动时把所有存在的 product_id 加载进布隆过滤器
bf = ScalableBloomFilter(initial_capacity=1000000, error_rate=0.001)
for pid in get_all_product_ids_from_db():
    bf.add(pid)

def get_product_with_bloom(product_id):
    # 先过布隆过滤器
    if str(product_id) not in bf:
        # 布隆过滤器说不存在，一定不存在（可能有极小误判率）
        return None
    # 可能存在，走正常缓存逻辑
    return get_product_anti_penetration(product_id)
```

布隆过滤器的特点：说不存在就一定不存在，说存在可能误判（假阳性）。误差率可配置（如 0.1%）。

#### 9.8.5 缓存击穿：热点 key 过期

缓存击穿指：某个**热点 key** 突然过期（如被手动删除或 TTL 到期），瞬间大量请求同时 miss，全部穿透到数据库。和穿透的区别是：穿透是"查不存在的数据"，击穿是"查存在的数据但缓存刚好没了"。

```
秒杀商品 product:1 有 10万 QPS，缓存过期那一瞬间
  -> 10万请求同时缓存 miss -> 10万请求同时查DB -> DB 被打垮
```

**解决方案一：互斥锁（只让一个请求回源）**

```python
def get_product_with_mutex(product_id):
    cache_key = f"product:{product_id}"
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)

    # 缓存 miss，用分布式锁防止并发回源
    lock_key = f"lock:cache:{product_id}"
    owner = str(uuid.uuid4())
    if r.set(lock_key, owner, nx=True, ex=10):
        try:
            # 再查一次缓存（可能在等锁期间被别人填了）
            cached = r.get(cache_key)
            if cached:
                return json.loads(cached)
            # 查数据库，回填缓存
            product = query_product_from_db(product_id)
            r.set(cache_key, json.dumps(product), ex=3600)
            return product
        finally:
            r.eval(RELEASE_LUA, 1, lock_key, owner)
    else:
        # 没抢到锁，等一下重试
        time.sleep(0.1)
        return get_product_with_mutex(product_id)
```

**解决方案二：热点 key 永不过期（逻辑过期）**

不设 TTL，改用 value 里存一个逻辑过期时间。后台异步检测过期后异步刷新：

```python
# value 里存 {"data": product, "expire": 时间戳}
def get_product_logical_expire(product_id):
    cache_key = f"product:{product_id}"
    cached = r.get(cache_key)
    if not cached:
        return None
    item = json.loads(cached)
    if time.time() < item["expire"]:
        # 未过期，直接返回
        return item["data"]
    # 逻辑过期，异步刷新（其他请求先用旧值）
    owner = r.set(f"lock:refresh:{product_id}", "1", nx=True, ex=10)
    if owner:
        # 开异步任务刷新缓存
        asyncio.create_task(refresh_cache(product_id))
    return item["data"]  # 返回旧值，不阻塞用户
```

#### 9.8.6 缓存雪崩：大量 key 同时过期

缓存雪崩指：大量 key 在**同一时刻**过期（如批量导入数据时设了相同的 TTL），导致大量请求同时穿透到数据库。和击穿的区别是：击穿是一个热点 key，雪崩是大面积 key。

```
场景：运营批量上架 1000 个商品，每个商品缓存设 TTL=3600s
      1小时后，1000 个商品缓存同时过期 -> 1000 个 DB 查询同时涌入 -> DB 崩溃
```

**解决方案一：随机过期时间**

给 TTL 加一个随机值，打散过期时间点：

```python
import random

def cache_product(product_id, data, base_ttl=3600):
    # 基础 TTL 3600s + 随机 0-600s，避免同时过期
    ttl = base_ttl + random.randint(0, 600)
    r.set(f"product:{product_id}", json.dumps(data), ex=ttl)
```

**解决方案二：多级缓存**

不只有 Redis 一层，加一层本地缓存（如 Python 的 `cachetools` LRU）：

```python
from cachetools import TTLCache

# L1: 进程内缓存（微秒级，但只对当前进程有效）
local_cache = TTLCache(maxsize=1000, ttl=60)

def get_product_multi_level(product_id):
    # L1 本地缓存
    if product_id in local_cache:
        return local_cache[product_id]
    # L2 Redis 缓存
    cached = r.get(f"product:{product_id}")
    if cached:
        data = json.loads(cached)
        local_cache[product_id] = data
        return data
    # L3 数据库
    data = query_product_from_db(product_id)
    if data:
        r.set(f"product:{product_id}", json.dumps(data), ex=3600)
        local_cache[product_id] = data
    return data
```

多级缓存的代价是数据一致性更难保证（L1 本地缓存在多实例间不同步）。适合读多写少、能容忍短暂不一致的场景。

#### 9.8.7 实战：商品详情页的缓存设计

综合以上模式，设计一个完整的商品详情页缓存方案：

```python
# ============ 商品详情页缓存设计 ============
import json
import random
import time
import uuid
import redis

r = redis.Redis(host="127.0.0.1", port=6379, decode_responses=True)

RELEASE_LUA = """
if redis.call('GET', KEYS[1]) == ARGV[1] then
    return redis.call('DEL', KEYS[1])
else
    return 0
end
"""

class ProductCache:
    """商品缓存：防穿透 + 防击穿 + 防雪崩"""

    NULL_TTL = 60          # 空值缓存 60 秒
    CACHE_TTL = 3600       # 正常缓存 1 小时（+ 随机）
    LOCK_TTL = 10          # 互斥锁 10 秒

    def get_product(self, product_id):
        cache_key = f"product:{product_id}"

        # 1. 查缓存
        cached = r.get(cache_key)
        if cached == "NULL":
            return None  # 空值缓存，防穿透
        if cached:
            return json.loads(cached)

        # 2. 缓存 miss，用互斥锁防击穿
        lock_key = f"lock:cache:{product_id}"
        owner = str(uuid.uuid4())
        if r.set(lock_key, owner, nx=True, ex=self.LOCK_TTL):
            try:
                # double check：拿到锁后再查一次缓存
                cached = r.get(cache_key)
                if cached == "NULL":
                    return None
                if cached:
                    return json.loads(cached)

                # 3. 查数据库
                product = self._query_db(product_id)
                if product:
                    # 防雪崩：随机 TTL
                    ttl = self.CACHE_TTL + random.randint(0, 600)
                    r.set(cache_key, json.dumps(product, ensure_ascii=False), ex=ttl)
                else:
                    # 防穿透：缓存空值
                    r.set(cache_key, "NULL", ex=self.NULL_TTL)
                return product
            finally:
                r.eval(RELEASE_LUA, 1, lock_key, owner)
        else:
            # 没抢到锁，短暂等待后重试
            time.sleep(0.05)
            return self.get_product(product_id)

    def _query_db(self, product_id):
        # 实际查数据库的逻辑
        pass

    def update_product(self, product_id, data):
        """更新商品：先更DB再删缓存"""
        self._update_db(product_id, data)
        r.delete(f"product:{product_id}")
```

这套方案同时防御了三大缓存问题：空值缓存防穿透、互斥锁防击穿、随机 TTL 防雪崩。是生产环境商品详情页的标准做法。

---

### 9.9 Python 操作 Redis 实战

前面几节我们学了 Redis 的概念、数据结构、锁机制和缓存模式。这一节我们把这些知识落地到 Python 代码，给出可以直接用在生产项目里的工具类和装饰器。

#### 9.9.1 redis-py 同步客户端：连接、基本操作、管道

```python
# ============ redis-py 同步客户端完整示例 ============
import redis
import json

# 连接池配置
pool = redis.ConnectionPool(
    host="127.0.0.1",
    port=6379,
    db=0,
    password="yourpassword",
    max_connections=20,        # 最大连接数
    socket_timeout=5,
    socket_connect_timeout=5,
    retry_on_timeout=True,
    health_check_interval=30,  # 每30秒做一次健康检查
)

r = redis.Redis(connection_pool=pool, decode_responses=True)

# ---- 基本操作 ----
r.set("name", "value", ex=60)
r.get("name")
r.delete("name")
r.exists("name")        # 返回 1 或 0
r.expire("name", 30)    # 给已有 key 设过期时间
r.ttl("name")          # 查看剩余 TTL

# ---- 管道（Pipeline）：批量减少网络往返 ----
# 场景：需要执行多条独立命令时，用 pipeline 一次性发送
pipe = r.pipeline()
for i in range(100):
    pipe.set(f"key:{i}", f"value:{i}")
pipe.execute()  # 1 次网络往返执行 100 条命令

# ---- 事务（MULTI/EXEC）：多条命令原子执行 ----
pipe = r.pipeline(transaction=True)
pipe.set("account:A", 100)
pipe.set("account:B", 200)
pipe.execute()  # 要么全部成功，要么全部失败

# ---- WATCH 乐观锁：监控 key 变化 ----
# 场景：转账时先 WATCH 余额，如果余额在事务执行前被改了，事务失败
def transfer(from_key, to_key, amount):
    with r.pipeline() as pipe:
        while True:
            try:
                pipe.watch(from_key)
                balance = int(pipe.get(from_key) or 0)
                if balance < amount:
                    pipe.unwatch()
                    return False, "余额不足"
                pipe.multi()
                pipe.decrby(from_key, amount)
                pipe.incrby(to_key, amount)
                pipe.execute()
                return True, "转账成功"
            except redis.WatchError:
                continue  # 余额被改了，重试
```

#### 9.9.2 aioredis / redis-py 异步客户端：配合 asyncio / FastAPI

从 redis-py 4.2 起，异步 API 和同步 API 在同一个包里：

```python
# ============ redis-py 异步客户端（FastAPI 场景） ============
import redis.asyncio as aioredis
from contextlib import asynccontextmanager
from fastapi import FastAPI

# 连接池
async_pool = aioredis.ConnectionPool(
    host="127.0.0.1", port=6379, password="yourpassword",
    max_connections=50, decode_responses=True,
)
async_r = aioredis.Redis(connection_pool=async_pool)

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = async_r
    yield
    await async_r.aclose()  # 关闭连接池

app = FastAPI(lifespan=lifespan)

@app.get("/api/product/{product_id}")
async def get_product(product_id: int):
    redis_client: aioredis.Redis = app.state.redis
    # 异步管道
    async with redis_client.pipeline(transaction=True) as pipe:
        await pipe.hgetall(f"product:{product_id}").execute()
        result = await pipe.execute()
    return result[0] if result else None
```

> 注意：异步客户端的方法名和同步一样，但需要 `await`。`close()` 变成 `aclose()`（避免和 asyncio 的 close 冲突）。

#### 9.9.3 连接池管理：ConnectionPool 的配置与最佳实践

连接池是 Redis 客户端的核心。配置不好会导致连接泄漏或性能下降。

```python
# ============ 连接池最佳实践 ============
import redis

# 生产环境推荐配置
pool = redis.ConnectionPool(
    host="127.0.0.1",
    port=6379,
    db=0,
    password="yourpassword",

    # 连接数
    max_connections=50,        # 根据 QPS 和单次操作耗时计算
    # 估算: max_connections = QPS * avg_latency_seconds
    # 如 5000 QPS * 0.002s = 10，留余量设 50

    # 超时
    socket_connect_timeout=2,  # 建连超时 2 秒（超过说明 Redis 可能挂了）
    socket_timeout=5,          # 读写超时 5 秒

    # 健康检查
    health_check_interval=30,  # 每 30 秒发 PING 检查连接活性

    # 重试
    retry_on_timeout=True,
    retry_on_error=[redis.ConnectionError],

    # 编码
    decode_responses=True,     # 自动 str 解码

    # 编码错误处理
    encoding="utf-8",
    errors="strict",           # 编码错误直接报错，别静默
)
```

连接池使用的常见错误：

```python
# 错误1：每次请求都新建 Redis 客户端（没复用连接池）
@app.get("/bad")
def bad_endpoint():
    r = redis.Redis(host="127.0.0.1")  # 每次都新建连接！性能灾难
    return r.get("key")

# 正确：全局共享一个连接池
r = redis.Redis(connection_pool=pool)  # 模块级初始化一次
@app.get("/good")
def good_endpoint():
    return r.get("key")  # 从池里取连接，用完归还

# 错误2：连接数设太大（如 1000）
# Redis 是单线程，连接太多反而增加 Redis 端的连接管理负担
# 且每个连接占内存，1000 个连接可能占几十 MB

# 错误3：不在应用关闭时关闭连接池
# 导致连接泄漏。FastAPI 的 lifespan 里要 close
```

#### 9.9.4 Lua 脚本执行：EVAL / EVALSHA

Lua 脚本是 Redis 的"原子操作利器"。当多条命令必须原子执行时（如分布式锁的"判断+删除"），用 Lua 脚本。Redis 会把整个 Lua 脚本当作一个命令执行，中间不会被其他命令打断。

```cmd
:: EVAL 脚本 参数个数 key列表 arg列表
127.0.0.1:6379> EVAL "return redis.call('GET', KEYS[1])" 1 mykey
```

EVAL 每次都发送完整脚本，浪费带宽。EVALSHA 先用 SCRIPT LOAD 缓存脚本，之后只发 SHA 摘要：

```cmd
:: 先加载脚本，返回 SHA
127.0.0.1:6379> SCRIPT LOAD "if redis.call('GET',KEYS[1])==ARGV[1] then return redis.call('DEL',KEYS[1]) else return 0 end"
"a5260a5a8b1e4c7a8b1e4c7a8b1e4c7a8b1e4c7a"

:: 之后用 SHA 调用
127.0.0.1:6379> EVALSHA "a5260a5a8b1e4c7a..." 1 lock_key owner_uuid
```

```python
# ============ Python 执行 Lua 脚本 ============
import redis

r = redis.Redis(host="127.0.0.1", port=6379, decode_responses=True)

# 令牌桶限流的 Lua 脚本
TOKEN_BUCKET_LUA = """
local key = KEYS[1]
local capacity = tonumber(ARGV[1])    -- 桶容量
local rate = tonumber(ARGV[2])        -- 每秒补充速率
local now = tonumber(ARGV[3])        -- 当前时间戳（秒）
local requested = tonumber(ARGV[4])  -- 本次请求消耗

local data = redis.call('HMGET', key, 'tokens', 'last_time')
local tokens = tonumber(data[1]) or capacity
local last_time = tonumber(data[2]) or now

-- 按速率补充令牌
local delta = now - last_time
tokens = math.min(capacity, tokens + delta * rate)

if tokens < requested then
    return 0  -- 令牌不足，拒绝
end

tokens = tokens - requested
redis.call('HMSET', key, 'tokens', tokens, 'last_time', now)
redis.call('EXPIRE', key, 3600)
return 1  -- 允许
"""

# 注册脚本（返回 SHA，后续复用）
sha = r.script_load(TOKEN_BUCKET_LUA)

def allow_request(user_id, capacity=10, rate=1):
    now = time.time()
    result = r.evalsha(sha, 1, f"token_bucket:{user_id}",
                      capacity, rate, now, 1)
    return bool(result)
```

#### 9.9.5 实战：用 Python + Redis 实现分布式锁工具类（完整代码）

综合 9.6 节的演进，这里给出一个生产可用的、带看门狗续期的分布式锁工具类（异步版，适配 FastAPI）：

```python
# ============ 生产级 Redis 分布式锁工具类（异步版） ============
import asyncio
import uuid
import logging
import redis.asyncio as aioredis

logger = logging.getLogger(__name__)

# Lua：原子加锁（可重入版，Hash 结构）
LOCK_LUA = """
if redis.call('EXISTS', KEYS[1]) == 0 then
    redis.call('HSET', KEYS[1], 'owner', ARGV[1], 'count', 1)
    redis.call('PEXPIRE', KEYS[1], ARGV[2])
    return 1
end
if redis.call('HGET', KEYS[1], 'owner') == ARGV[1] then
    redis.call('HINCRBY', KEYS[1], 'count', 1)
    redis.call('PEXPIRE', KEYS[1], ARGV[2])
    return 1
end
return 0
"""

# Lua：原子解锁（count-1，到0才删）
UNLOCK_LUA = """
if redis.call('HGET', KEYS[1], 'owner') == ARGV[1] then
    local count = redis.call('HINCRBY', KEYS[1], 'count', -1)
    if count <= 0 then
        redis.call('DEL', KEYS[1])
        return 1
    end
    redis.call('PEXPIRE', KEYS[1], ARGV[2])
    return 0
end
return 0
"""

# Lua：续期（判断 owner 后 PEXPIRE）
RENEW_LUA = """
if redis.call('HGET', KEYS[1], 'owner') == ARGV[1] then
    return redis.call('PEXPIRE', KEYS[1], ARGV[2])
else
    return 0
end
"""


class AsyncRedisLock:
    """
    异步 Redis 分布式锁（可重入 + 看门狗续期）

    特性：
      - 可重入：同一 owner 可多次加锁（Hash 记 count）
      - 看门狗：自动续期，防止业务未完成锁过期
      - 原子性：加锁/解锁/续期均用 Lua 脚本
      - 超时等待：支持 wait_timeout 参数
    """

    def __init__(
        self,
        redis_client: aioredis.Redis,
        lock_key: str,
        expire_ms: int = 30000,
        wait_timeout: float | None = None,
    ):
        self.r = redis_client
        self.lock_key = lock_key
        self.expire_ms = expire_ms
        self.wait_timeout = wait_timeout
        self.owner = str(uuid.uuid4())
        self._renew_task: asyncio.Task | None = None
        self._lock_sha: str | None = None
        self._unlock_sha: str | None = None
        self._renew_sha: str | None = None

    async def _ensure_shas(self):
        """注册 Lua 脚本（只注册一次）"""
        if self._lock_sha is None:
            self._lock_sha = await self.r.script_load(LOCK_LUA)
            self._unlock_sha = await self.r.script_load(UNLOCK_LUA)
            self._renew_sha = await self.r.script_load(RENEW_LUA)

    async def acquire(self) -> bool:
        """加锁，成功返回 True。如果设了 wait_timeout 会等待。"""
        await self._ensure_shas()

        deadline = None
        if self.wait_timeout:
            deadline = asyncio.get_event_loop().time() + self.wait_timeout

        while True:
            result = await self.r.evalsha(
                self._lock_sha, 1, self.lock_key, self.owner, self.expire_ms
            )
            if result:
                self._start_watchdog()
                return True

            if deadline and asyncio.get_event_loop().time() >= deadline:
                return False

            await asyncio.sleep(0.05)  # 等 50ms 重试

    def _start_watchdog(self):
        """启动看门狗协程，定期续期"""
        interval = self.expire_ms / 1000 / 3  # 每 1/3 有效期续一次

        async def _renew_loop():
            try:
                while True:
                    await asyncio.sleep(interval)
                    result = await self.r.evalsha(
                        self._renew_sha, 1, self.lock_key,
                        self.owner, self.expire_ms
                    )
                    if not result:
                        logger.warning("锁续期失败，可能已被释放或 owner 变更")
                        break
            except asyncio.CancelledError:
                pass
            except Exception as e:
                logger.error(f"看门狗异常: {e}")

        self._renew_task = asyncio.create_task(_renew_loop())

    async def release(self):
        """释放锁，停止看门狗"""
        if self._renew_task:
            self._renew_task.cancel()
            try:
                await self._renew_task
            except asyncio.CancelledError:
                pass
            self._renew_task = None

        await self.r.evalsha(
            self._unlock_sha, 1, self.lock_key, self.owner, self.expire_ms
        )

    async def __aenter__(self):
        acquired = await self.acquire()
        if not acquired:
            raise TimeoutError(f"获取锁 {self.lock_key} 超时")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.release()


# ---- 使用示例 ----
# async def seckill(product_id, user_id):
#     async with AsyncRedisLock(r, f"lock:stock:{product_id}", expire_ms=10000):
#         remaining = await r.incrby(f"stock:{product_id}", -1)
#         if remaining >= 0:
#             await create_order_in_db(product_id, user_id)
#             return "秒杀成功"
#         await r.incrby(f"stock:{product_id}", 1)  # 回滚
#         return "已售罄"
```

#### 9.9.6 实战：用 Python + Redis 实现缓存装饰器（@cache 装饰器）

让缓存的接入变得"无感"——给函数加一个 `@redis_cache` 装饰器，自动处理缓存命中/miss/回源/防穿透：

```python
# ============ Redis 缓存装饰器 ============
import json
import hashlib
import functools
import redis.asyncio as aioredis

def _build_cache_key(func_name, args, kwargs, prefix="cache"):
    """根据函数名+参数生成缓存 key"""
    # 把参数序列化为稳定的字符串，取 MD5（key 不能太长）
    key_data = f"{func_name}:{args}:{sorted(kwargs.items())}"
    key_hash = hashlib.md5(key_data.encode("utf-8")).hexdigest()
    return f"{prefix}:{func_name}:{key_hash}"


def redis_cache(
    redis_client: aioredis.Redis,
    ttl: int = 3600,
    prefix: str = "cache",
    cache_none: bool = True,
    none_ttl: int = 60,
):
    """
    Redis 缓存装饰器

    参数：
      ttl:          正常缓存过期时间（秒）
      prefix:       key 前缀
      cache_none:   是否缓存 None（防穿透）
      none_ttl:     None 值缓存过期时间（秒）
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = _build_cache_key(func.__name__, args, kwargs, prefix)

            # 1. 查缓存
            cached = await redis_client.get(cache_key)
            if cached == "__NULL__":
                return None  # 缓存的空值
            if cached is not None:
                return json.loads(cached)

            # 2. 缓存 miss，执行原函数（回源）
            result = await func(*args, **kwargs)

            # 3. 回填缓存
            if result is not None:
                await redis_client.set(
                    cache_key,
                    json.dumps(result, ensure_ascii=False),
                    ex=ttl,
                )
            elif cache_none:
                # 防穿透：缓存空值
                await redis_client.set(cache_key, "__NULL__", ex=none_ttl)

            return result

        # 暴露缓存 key 生成方法，方便手动失效缓存
        wrapper.cache_key = lambda *a, **kw: _build_cache_key(
            func.__name__, a, kw, prefix
        )
        # 暴露失效方法
        async def invalidate(*args, **kwargs):
            key = _build_cache_key(func.__name__, args, kwargs, prefix)
            await redis_client.delete(key)
        wrapper.invalidate = invalidate

        return wrapper
    return decorator


# ---- 使用示例 ----
# # 定义带缓存的查询函数
# @redis_cache(redis_client=r, ttl=3600, cache_none=True)
# async def get_product(product_id: int):
#     """查询商品详情，自动缓存 1 小时"""
#     return await db.fetch_one(
#         "SELECT * FROM products WHERE id = $1", product_id
#     )
#
# # 调用（第一次走 DB，后续走缓存）
# product = await get_product(1)
#
# # 更新后手动失效缓存
# await get_product.invalidate(1)
```

这个装饰器的亮点：
- **防穿透**：None 结果也缓存，短 TTL。
- **key 生成**：根据函数名+参数自动生成 MD5 key，不用手动管 key 命名。
- **手动失效**：暴露 `invalidate` 方法，更新数据时主动清缓存。
- **异步**：原生支持 asyncio，适合 FastAPI。

---

### 9.10 Redis + 数据库经典配合场景

最后这一节，我们把前面学的所有 Redis 知识串联起来，看看 Redis 和数据库在实际业务中是如何配合的。每个场景都是生产环境真实使用的模式，给出简要的 Python 代码。

> 前端类比：Redis + 数据库的配合，就像前端的"内存状态 + 持久化存储"。Redux Store 是内存里的临时状态（快），localStorage 是持久化存储（慢但可靠）。后端的 Redis 和 MySQL 也是这个关系——快慢搭配，各司其职。

#### 9.10.1 缓存层：热点数据缓存减轻数据库压力

这是 Redis 最经典的用途。9.8 节已经详细讲过 Cache-Aside 模式，这里给一个 FastAPI 中的标准实现：

```python
# ============ 场景1：热点数据缓存 ============
import json
import redis.asyncio as aioredis
from fastapi import FastAPI

app = FastAPI()
r = aioredis.Redis(host="127.0.0.1", port=6379, decode_responses=True)

@app.get("/api/articles/{article_id}")
async def get_article(article_id: int):
    cache_key = f"article:{article_id}"

    # 1. 先查 Redis
    cached = await r.get(cache_key)
    if cached:
        return json.loads(cached)

    # 2. 缓存 miss，查数据库
    article = await db_fetch_one(
        "SELECT id, title, content FROM articles WHERE id = $1", article_id
    )
    if article:
        # 3. 写入缓存，随机 TTL 防雪崩
        import random
        ttl = 3600 + random.randint(0, 300)
        await r.set(cache_key, json.dumps(article, ensure_ascii=False), ex=ttl)

    return article

@app.put("/api/articles/{article_id}")
async def update_article(article_id: int, data: dict):
    # 先更新数据库，再删缓存（Cache-Aside 推荐方案）
    await db_execute(
        "UPDATE articles SET title=$1, content=$2 WHERE id=$3",
        data["title"], data["content"], article_id
    )
    await r.delete(f"article:{article_id}")
    return {"status": "updated"}
```

#### 9.10.2 分布式锁：保护数据库写入的并发安全

9.6 节详细讲了 Redis 分布式锁。这里给一个在 FastAPI 中保护"创建订单"的示例，防止同一用户重复下单：

```python
# ============ 场景2：分布式锁防重复操作 ============
from my_locks import AsyncRedisLock  # 9.9.5 节的锁工具类

@app.post("/api/orders")
async def create_order(user_id: int, product_id: int):
    # 用 user_id+product_id 作为锁粒度，防止同一用户重复下单
    lock_key = f"lock:order:{user_id}:{product_id}"

    async with AsyncRedisLock(r, lock_key, expire_ms=10000, wait_timeout=3):
        # 检查是否已下过单（幂等）
        existing = await r.get(f"order:exists:{user_id}:{product_id}")
        if existing:
            return {"status": "already_ordered"}

        # 扣库存 + 创建订单（数据库操作）
        await db_execute(
            "UPDATE products SET stock=stock-1 WHERE id=$1 AND stock>0",
            product_id
        )
        order_id = await db_fetch_one(
            "INSERT INTO orders (user_id, product_id) VALUES ($1,$2) RETURNING id",
            user_id, product_id
        )
        # 标记已下单（防重复，5分钟过期）
        await r.set(f"order:exists:{user_id}:{product_id}", "1", ex=300)

    return {"order_id": order_id, "status": "success"}
```

#### 9.10.3 计数器：Redis 实时计数 + 定时同步到数据库

Redis 的 `INCR` 是原子的，适合做实时计数器。但 Redis 计数不持久，需要定期同步到数据库做持久化存储。

```python
# ============ 场景3：计数器（浏览量/点赞数） ============
import asyncio

# 实时计数：每次访问 +1
@app.get("/api/articles/{article_id}/view")
async def record_view(article_id: int):
    # Redis 实时计数（微秒级）
    await r.incr(f"view:article:{article_id}")
    return {"status": "ok"}

# 定时同步：后台任务，每分钟把 Redis 计数刷到数据库
async def sync_counters_to_db():
    """后台任务：把 Redis 计数同步到 MySQL"""
    while True:
        # 扫描所有 view:article:* 的 key
        async for key in r.scan_iter(match="view:article:*", count=100):
            article_id = key.split(":")[2]
            count = await r.get(key)
            if count:
                # 写入数据库（UPSERT）
                await db_execute(
                    "INSERT INTO article_stats (article_id, view_count) "
                    "VALUES ($1, $2) "
                    "ON CONFLICT (article_id) "
                    "DO UPDATE SET view_count = article_stats.view_count + $2",
                    int(article_id), int(count)
                )
                # 重置 Redis 计数（避免重复累加）
                await r.set(key, 0)
        await asyncio.sleep(60)  # 每分钟同步一次

# 启动后台任务
@app.on_event("startup")
async def start_sync():
    asyncio.create_task(sync_counters_to_db())
```

这种"Redis 实时计数 + 定时落库"的模式，既保证了计数的实时性和高性能，又保证了数据的持久化。

#### 9.10.4 限流器：令牌桶 / 滑动窗口限流保护数据库

限流是保护数据库的"第一道防线"。在请求到达数据库之前，先用 Redis 限流拦截超量请求。

```python
# ============ 场景4：滑动窗口限流器 ============
# 原理：用 ZSet 记录每个请求的时间戳，统计时间窗口内的请求数

import time

async def is_rate_limited(user_id: str, limit: int = 100, window: int = 60):
    """
    滑动窗口限流：每 user_id 在 window 秒内最多 limit 次请求

    原理：用 ZSet 存请求时间戳，删除窗口外的旧记录，统计当前窗口内的请求数
    """
    key = f"ratelimit:{user_id}"
    now = time.time()
    window_start = now - window

    # Lua 脚本保证原子性
    lua = """
    -- 1. 删除窗口外的旧记录
    redis.call('ZREMRANGEBYSCORE', KEYS[1], 0, ARGV[1])
    -- 2. 统计当前窗口内的请求数
    local count = redis.call('ZCARD', KEYS[1])
    if count < tonumber(ARGV[3]) then
        -- 3. 未超限，记录本次请求
        redis.call('ZADD', KEYS[1], ARGV[2], ARGV[2])
        redis.call('EXPIRE', KEYS[1], ARGV[4])
        return 1  -- 允许
    end
    return 0  -- 拒绝
    """
    allowed = await r.eval(
        lua, 1, key,
        window_start,   # ARGV[1]: 窗口起点
        now,            # ARGV[2]: 当前时间戳（作为 member 和 score）
        limit,          # ARGV[3]: 限制次数
        window,         # ARGV[4]: 过期时间
    )
    return not bool(allowed)  # True 表示被限流

# 在 FastAPI 中间件里使用
@app.middleware("http")
async def rate_limit_middleware(request, call_next):
    user_id = get_user_id_from_token(request)  # 假设的鉴权函数
    if await is_rate_limited(user_id, limit=100, window=60):
        return JSONResponse(
            status_code=429,
            content={"detail": "请求过于频繁，请稍后再试"}
        )
    return await call_next(request)
```

#### 9.10.5 会话管理：Redis 存 Session + 数据库存用户信息

传统方案是把 Session 存在数据库或文件里，性能差。Redis 天然适合存 Session——有过期机制、读写快、支持多实例共享。

```python
# ============ 场景5：Redis 存储会话 ============
import secrets
import json

async def create_session(user_id: int, user_info: dict) -> str:
    """登录成功后创建 Session"""
    session_id = secrets.token_urlsafe(32)
    session_data = {
        "user_id": user_id,
        "username": user_info["username"],
        "role": user_info["role"],
        "login_at": time.time(),
    }
    # 存入 Redis，30 分钟过期
    await r.set(
        f"session:{session_id}",
        json.dumps(session_data, ensure_ascii=False),
        ex=1800
    )
    return session_id

async def get_session(session_id: str) -> dict | None:
    """从 Redis 读取 Session"""
    data = await r.get(f"session:{session_id}")
    if data:
        return json.loads(data)
    return None  # 过期或不存在

async def refresh_session(session_id: str):
    """用户活跃时续期 Session"""
    await r.expire(f"session:{session_id}", 1800)

async def destroy_session(session_id: str):
    """登出时销毁 Session"""
    await r.delete(f"session:{session_id}")

# FastAPI 依赖注入
from fastapi import Depends, HTTPException, Request

async def get_current_user(request: Request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    session = await get_session(token)
    if not session:
        raise HTTPException(status_code=401, detail="未登录或会话已过期")
    return session
```

数据库只存用户的基础信息（注册信息、角色权限），Redis 存登录会话。两者各司其职。

#### 9.10.6 消息队列：List/Stream 实现异步写数据库

有些写操作不需要同步返回结果（如发邮件、生成报表、记录日志），可以用 Redis 做消息队列，异步处理。

```python
# ============ 场景6：消息队列（异步处理） ============

# 生产者：API 接收请求后，把任务推入队列，立即返回
@app.post("/api/send-notification")
async def send_notification(user_id: int, message: str):
    task = json.dumps({
        "type": "send_email",
        "user_id": user_id,
        "message": message,
    }, ensure_ascii=False)
    # 推入 Redis List（左端进）
    await r.lpush("task:notification", task)
    return {"status": "queued"}  # 立即返回，不等邮件发完

# 消费者：后台 worker 阻塞式消费队列
async def notification_worker():
    """后台消费者：从队列右端弹出任务，执行"""
    while True:
        # BRPOP 阻塞等待，最多等 30 秒
        result = await r.brpop("task:notification", timeout=30)
        if result is None:
            continue  # 队列空，继续等
        queue_name, task_data = result
        task = json.loads(task_data)
        try:
            if task["type"] == "send_email":
                await send_email(task["user_id"], task["message"])
        except Exception as e:
            # 处理失败，推入死信队列
            await r.lpush("task:notification:failed", task_data)

@app.on_event("startup")
async def start_workers():
    asyncio.create_task(notification_worker())
```

用 Stream（9.3.6 节）可以做更可靠的消息队列，支持消费组和 ACK 机制，适合不能丢消息的场景。

#### 9.10.7 排行榜：ZSet 实时排行 + 定时持久化到数据库

```python
# ============ 场景7：排行榜 ============

# 实时更新分数
@app.post("/api/game/score")
async def update_score(player_id: str, score: int):
    # ZINCRBY 原子更新分数
    new_score = await r.zincrby("game:ranking", score, player_id)
    return {"player_id": player_id, "total_score": new_score}

# 查询排行榜
@app.get("/api/game/leaderboard")
async def get_leaderboard(top: int = 10):
    # ZREVRANGE 按分数降序取前 N
    top_players = await r.zrevrange(
        "game:ranking", 0, top - 1, withscores=True
    )
    result = []
    for rank, (player_id, score) in enumerate(top_players, 1):
        result.append({
            "rank": rank,
            "player_id": player_id,
            "score": int(score),
        })
    return result

# 定时持久化：每小时把排行榜写入数据库
async def persist_leaderboard():
    while True:
        await asyncio.sleep(3600)  # 每小时一次
        all_scores = await r.zrevrange(
            "game:ranking", 0, -1, withscores=True
        )
        for rank, (player_id, score) in enumerate(all_scores, 1):
            await db_execute(
                "INSERT INTO leaderboard (player_id, score, rank, snapshot_at) "
                "VALUES ($1, $2, $3, NOW())",
                player_id, int(score), rank
            )
```

ZSet 排行榜的优势：实时更新和查询都是 O(log N) 复杂度，10万玩家的排行榜也能毫秒级响应。

#### 9.10.8 购物车：Redis Hash 存储 + 结算时写入数据库

购物车的特点是：频繁增删改、需要跨设备同步、但不需要持久化每一步操作。Redis Hash 是理想选择——结算时才写入数据库。

```python
# ============ 场景8：购物车 ============

# 添加商品到购物车
@app.post("/api/cart/{user_id}/items")
async def add_to_cart(user_id: int, product_id: int, quantity: int = 1):
    # HINCRBY 原子增加商品数量
    cart_key = f"cart:{user_id}"
    new_qty = await r.hincrby(cart_key, str(product_id), quantity)
    # 设购物车过期时间（30天不操作自动清空）
    await r.expire(cart_key, 30 * 86400)
    return {"product_id": product_id, "quantity": new_qty}

# 查看购物车
@app.get("/api/cart/{user_id}")
async def get_cart(user_id: int):
    cart_key = f"cart:{user_id}"
    items = await r.hgetall(cart_key)  # {product_id: quantity}
    if not items:
        return {"items": []}
    # 批量查商品详情（用 pipeline 减少往返）
    pipe = r.pipeline()
    for pid in items:
        pipe.hgetall(f"product:{pid}")
    products = await pipe.execute()

    cart_items = []
    for (pid, qty), product in zip(items.items(), products):
        if product:
            cart_items.append({
                "product_id": int(pid),
                "quantity": int(qty),
                "name": product.get("name"),
                "price": float(product.get("price", 0)),
            })
    return {"items": cart_items}

# 结算：把购物车转为订单，写入数据库
@app.post("/api/cart/{user_id}/checkout")
async def checkout(user_id: int):
    cart_key = f"cart:{user_id}"
    items = await r.hgetall(cart_key)
    if not items:
        raise HTTPException(status_code=400, detail="购物车为空")

    # 用分布式锁防止重复结算
    async with AsyncRedisLock(r, f"lock:checkout:{user_id}", expire_ms=30):
        total = 0
        order_items = []
        for pid, qty in items.items():
            # 查商品价格并扣库存
            product = await db_fetch_one(
                "SELECT id, name, price, stock FROM products WHERE id=$1",
                int(pid)
            )
            if not product or product["stock"] < int(qty):
                raise HTTPException(
                    status_code=400,
                    detail=f"商品 {pid} 库存不足"
                )
            total += product["price"] * int(qty)
            order_items.append((int(pid), int(qty), product["price"]))

        # 写入数据库：创建订单 + 订单明细（事务）
        async with db.transaction():
            order_id = await db_fetch_one(
                "INSERT INTO orders (user_id, total, status) "
                "VALUES ($1, $2, 'paid') RETURNING id",
                user_id, total
            )
            for pid, qty, price in order_items:
                await db_execute(
                    "INSERT INTO order_items (order_id, product_id, quantity, price) "
                    "VALUES ($1, $2, $3, $4)",
                    order_id, pid, qty, price
                )
                await db_execute(
                    "UPDATE products SET stock = stock - $1 WHERE id = $2",
                    qty, pid
                )

        # 清空购物车
        await r.delete(cart_key)

    return {"order_id": order_id, "total": total, "status": "success"}
```

购物车的 Redis 设计亮点：
- **Hash 结构**：一个用户一个 Hash，field 是商品 ID，value 是数量。增删改都是单字段操作，O(1)。
- **过期机制**：购物车设 30 天 TTL，不活跃自动清理。
- **结算时才落库**：购物车期间的全部操作都在 Redis，只有结算（最终结果）才写入数据库。大大减轻数据库写入压力。

---

至此，第九章 Redis 核心与锁机制全部讲完。回顾一下本章的知识脉络：

```
9.1  基础认知        -> Redis 是什么、为什么快、和 MySQL 的分工
9.2  安装与连接      -> 环境搭建、redis-cli、redis-py 驱动
9.3  数据结构        -> 9 种结构 + 各自的经典业务场景
9.4  持久化          -> RDB / AOF / 混合，如何保证数据不丢
9.5  内存管理        -> 过期策略 + 8 种淘汰策略
9.6  锁机制 [核心]   -> 4 代演进 + 看门狗 + 可重入 + 对比
9.7  锁对比 [核心]   -> 数据库锁 vs Redis 锁 + 决策树 + 秒杀实战
9.8  缓存模式        -> Cache-Aside + 一致性 + 穿透/击穿/雪崩
9.9  Python 实战     -> 连接池 + Lua + 分布式锁工具类 + 缓存装饰器
9.10 经典配合场景    -> 8 个 Redis + 数据库的经典组合
```

记住核心心法：**Redis 是数据库的"好搭档"，不是"替代品"**。快的数据放 Redis，重要的数据放 MySQL，用锁保护并发，用缓存减轻压力。下一章我们将进入实战业务场景设计，把这一章的 Redis 知识和前面的数据库知识综合运用到真实业务中。
