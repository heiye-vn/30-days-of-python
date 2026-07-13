# Python 异步编程详解

> 异步编程是后续学习 FastAPI、OpenAI SDK、AI Agent、流式输出、并发请求、工具调用编排时绕不开的基础。它不是为了让单个任务跑得更快，而是为了让程序在等待网络、文件、数据库、模型响应时，不把整个程序卡住。

---

## 一、先建立直觉：为什么需要异步

假设你要调用 3 个接口：

- 接口 A 需要 2 秒
- 接口 B 需要 3 秒
- 接口 C 需要 1 秒

如果按同步方式一个一个调用，总耗时大约是：

```text
2 + 3 + 1 = 6 秒
```

如果用异步方式同时发起请求，总耗时大约是：

```text
max(2, 3, 1) = 3 秒
```

这就是异步编程最核心的价值：当某个任务在等待时，让程序去处理别的任务。

### 1.1 同步代码的问题

同步代码的执行方式是“一步一步来”。

```python
import time


def download(name: str, seconds: int) -> str:
    print(f"开始下载 {name}")
    time.sleep(seconds)
    print(f"下载完成 {name}")
    return name


def main() -> None:
    download("A", 2)
    download("B", 3)
    download("C", 1)


main()
```

这段代码会依次等待 A、B、C。`time.sleep()` 期间，当前线程被阻塞，什么都干不了。

### 1.2 异步代码的直觉

异步代码的执行方式更像“先把任务都安排出去，谁准备好了就处理谁”。

```python
import asyncio


async def download(name: str, seconds: int) -> str:
    print(f"开始下载 {name}")
    await asyncio.sleep(seconds)
    print(f"下载完成 {name}")
    return name


async def main() -> None:
    results = await asyncio.gather(
        download("A", 2),
        download("B", 3),
        download("C", 1),
    )
    print(results)


asyncio.run(main())
```

这里的 `await asyncio.sleep(seconds)` 不会阻塞整个程序，而是告诉事件循环：

> 当前任务要等一会儿，你先去执行别的任务。

---

## 二、并发、并行、异步的区别

这几个词经常混在一起，但含义不同。

### 2.1 并发 Concurrency

并发表示“同时处理多个任务”的能力。

它不一定是真的同时执行，可能是任务之间快速切换。

例如：

```text
任务 A 等网络响应
切到任务 B
任务 B 等数据库响应
切到任务 C
任务 C 完成
切回任务 A
```

异步编程主要解决的是并发问题。

### 2.2 并行 Parallelism

并行表示“多个任务真的在同一时刻执行”。

例如多核 CPU 同时运行多个计算任务。

Python 里常见并行方式：

- 多进程：`multiprocessing`
- 进程池：`ProcessPoolExecutor`
- 某些释放 GIL 的 C 扩展，例如 NumPy 的底层计算

### 2.3 异步 Asynchronous

异步是一种编程模型，重点是：

> 遇到等待操作时，不傻等，而是把控制权交还给调度器。

异步适合 I/O 密集型任务：

- HTTP 请求
- 数据库访问
- 文件读写
- WebSocket 通信
- LLM API 调用
- 流式输出
- Agent 同时调用多个工具

异步不擅长 CPU 密集型任务：

- 大量数学计算
- 图片压缩
- 视频转码
- 复杂加密解密
- 大规模文本本地解析

CPU 密集型任务通常应该用多进程、任务队列，或者交给专门的计算服务。

---

## 三、Python 异步编程的核心组件

Python 的异步编程主要围绕 `asyncio` 展开。

常见核心概念：

- `async def`：定义协程函数
- coroutine：协程对象
- `await`：等待一个异步操作完成
- event loop：事件循环
- task：被事件循环调度的任务
- `asyncio.run()`：启动事件循环并运行入口协程
- `asyncio.create_task()`：创建并发任务
- `asyncio.gather()`：等待多个任务完成
- `async with`：异步上下文管理器
- `async for`：异步迭代

---

## 四、async def：定义协程函数

普通函数用 `def` 定义：

```python
def hello() -> str:
    return "hello"
```

异步函数用 `async def` 定义：

```python
async def hello() -> str:
    return "hello"
```

注意：调用异步函数不会立刻执行函数体，而是返回一个协程对象。

```python
async def hello() -> str:
    print("hello")
    return "done"


result = hello()
print(result)
```

输出类似：

```text
<coroutine object hello at 0x...>
```

这说明 `hello()` 只是创建了一个协程对象，还没有真正运行。

要运行协程，需要：

- 在异步函数里使用 `await`
- 或者在程序入口用 `asyncio.run()`

---

## 五、await：等待异步操作

`await` 的作用是等待一个可等待对象完成。

常见可等待对象包括：

- 协程对象
- `asyncio.Task`
- 某些异步库返回的对象

示例：

```python
import asyncio


async def say_hello() -> str:
    await asyncio.sleep(1)
    return "hello"


async def main() -> None:
    message = await say_hello()
    print(message)


asyncio.run(main())
```

### 5.1 await 不是“开新线程”

很多初学者会误解：写了 `await` 就等于开了新线程。

不是。

`await` 的真正含义是：

> 我现在要等一个异步操作，等的时候可以把控制权交出去。

如果只有一个任务，异步代码并不会神奇地变快。

```python
async def main() -> None:
    await asyncio.sleep(1)
    await asyncio.sleep(1)
    await asyncio.sleep(1)
```

这依然大约需要 3 秒，因为它们还是顺序执行。

要并发执行，需要创建多个任务。

---

## 六、asyncio.run()：启动异步程序

`asyncio.run()` 通常用于异步程序的最外层入口。

```python
import asyncio


async def main() -> None:
    print("start")
    await asyncio.sleep(1)
    print("end")


asyncio.run(main())
```

可以理解为：

1. 创建事件循环
2. 把 `main()` 这个协程交给事件循环运行
3. 等 `main()` 执行完
4. 关闭事件循环

### 6.1 不要在已经运行的事件循环里调用 asyncio.run()

下面这种写法容易报错：

```python
async def inner() -> None:
    print("inner")


async def outer() -> None:
    asyncio.run(inner())  # 错误示例
```

在一个异步函数内部，应该直接 `await`：

```python
async def inner() -> None:
    print("inner")


async def outer() -> None:
    await inner()
```

在 FastAPI、Jupyter Notebook、异步测试框架里，事件循环通常已经存在，所以不能随便嵌套 `asyncio.run()`。

---

## 七、事件循环 Event Loop

事件循环是异步程序的调度中心。

你可以把它理解为一个不断工作的调度器：

```text
检查哪些任务可以执行
执行一小段
遇到 await，任务让出控制权
切换到其他可以执行的任务
等待 I/O 事件回来
恢复对应任务
```

一个简化版流程：

```text
main task 开始
  遇到 await 网络请求
  main task 暂停
  event loop 去运行其他 task
网络响应回来
  event loop 恢复 main task
main task 继续执行
```

所以异步程序的关键不是“多线程”，而是“协作式调度”。

---

## 八、协程 Coroutine 和任务 Task

### 8.1 协程对象只是“待执行的异步函数”

```python
async def fetch() -> str:
    await asyncio.sleep(1)
    return "data"


coro = fetch()
```

`coro` 是协程对象，但它还没有被事件循环调度。

### 8.2 Task 是被事件循环调度的协程

```python
import asyncio


async def fetch(name: str, seconds: int) -> str:
    print(f"{name} start")
    await asyncio.sleep(seconds)
    print(f"{name} end")
    return name


async def main() -> None:
    task = asyncio.create_task(fetch("A", 2))
    print("task created")

    result = await task
    print(result)


asyncio.run(main())
```

`asyncio.create_task()` 会把协程包装成任务，并交给事件循环调度。

---

## 九、顺序 await 和并发 task 的区别

这是异步编程最容易踩坑的地方。

### 9.1 顺序执行

```python
import asyncio


async def job(name: str, seconds: int) -> str:
    print(f"{name} start")
    await asyncio.sleep(seconds)
    print(f"{name} end")
    return name


async def main() -> None:
    result1 = await job("A", 2)
    result2 = await job("B", 3)
    result3 = await job("C", 1)
    print(result1, result2, result3)


asyncio.run(main())
```

执行过程：

```text
A start
等待 A 完成
B start
等待 B 完成
C start
等待 C 完成
```

总耗时约 6 秒。

### 9.2 并发执行

```python
import asyncio


async def job(name: str, seconds: int) -> str:
    print(f"{name} start")
    await asyncio.sleep(seconds)
    print(f"{name} end")
    return name


async def main() -> None:
    task1 = asyncio.create_task(job("A", 2))
    task2 = asyncio.create_task(job("B", 3))
    task3 = asyncio.create_task(job("C", 1))

    result1 = await task1
    result2 = await task2
    result3 = await task3

    print(result1, result2, result3)


asyncio.run(main())
```

总耗时约 3 秒。

### 9.3 使用 gather 更简洁

```python
import asyncio


async def job(name: str, seconds: int) -> str:
    print(f"{name} start")
    await asyncio.sleep(seconds)
    print(f"{name} end")
    return name


async def main() -> None:
    results = await asyncio.gather(
        job("A", 2),
        job("B", 3),
        job("C", 1),
    )
    print(results)


asyncio.run(main())
```

`asyncio.gather()` 会并发运行多个可等待对象，并按传入顺序返回结果。

即使 C 最先完成，结果仍然按 A、B、C 的顺序放在列表里。

---

## 十、asyncio.gather()：批量并发

`gather()` 常用于：

- 同时请求多个 API
- 同时处理多个用户输入
- 同时调用多个 Agent 工具
- 同时执行多个检索任务

示例：并发获取多个 URL。

```python
import asyncio


async def fetch_url(url: str) -> str:
    await asyncio.sleep(1)
    return f"content from {url}"


async def main() -> None:
    urls = [
        "https://example.com/a",
        "https://example.com/b",
        "https://example.com/c",
    ]

    results = await asyncio.gather(
        *(fetch_url(url) for url in urls)
    )

    for result in results:
        print(result)


asyncio.run(main())
```

这里的 `*` 是参数解包：

```python
asyncio.gather(*(fetch_url(url) for url in urls))
```

等价于：

```python
asyncio.gather(
    fetch_url("https://example.com/a"),
    fetch_url("https://example.com/b"),
    fetch_url("https://example.com/c"),
)
```

---

## 十一、create_task()：手动创建任务

`gather()` 适合“我有一批任务，现在全部等它们完成”。

`create_task()` 更适合“我想先启动一个后台任务，然后继续做别的事情”。

```python
import asyncio


async def background_sync() -> None:
    await asyncio.sleep(2)
    print("后台同步完成")


async def main() -> None:
    task = asyncio.create_task(background_sync())

    print("继续处理主流程")
    await asyncio.sleep(1)
    print("主流程处理了一部分")

    await task


asyncio.run(main())
```

### 11.1 create_task 后最好要 await

不要随手创建一个任务然后完全不管。

```python
asyncio.create_task(background_sync())  # 不推荐
```

如果任务内部报错，而你没有等待或收集它，错误可能会变得很难追踪。

更稳妥的方式：

```python
task = asyncio.create_task(background_sync())
await task
```

如果确实要做后台任务，需要有日志、错误处理和生命周期管理。

---

## 十二、TaskGroup：更结构化的并发

Python 3.11 开始提供 `asyncio.TaskGroup`，可以更清晰地管理一组任务。

```python
import asyncio


async def job(name: str, seconds: int) -> str:
    await asyncio.sleep(seconds)
    return name


async def main() -> None:
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(job("A", 2))
        task2 = tg.create_task(job("B", 1))

    print(task1.result())
    print(task2.result())


asyncio.run(main())
```

`TaskGroup` 的好处：

- 任务生命周期更清晰
- 其中一个任务失败时，其他任务会被取消
- 更适合结构化并发

对初学者来说，先熟练 `gather()` 和 `create_task()`，再学习 `TaskGroup` 即可。

---

## 十三、异常处理

### 13.1 普通 await 的异常处理

```python
import asyncio


async def risky() -> str:
    await asyncio.sleep(1)
    raise ValueError("出错了")


async def main() -> None:
    try:
        result = await risky()
        print(result)
    except ValueError as error:
        print(f"捕获异常: {error}")


asyncio.run(main())
```

### 13.2 gather 中的异常

默认情况下，`gather()` 中任何一个任务抛出异常，`gather()` 会把异常继续抛出去。

```python
import asyncio


async def ok() -> str:
    await asyncio.sleep(1)
    return "ok"


async def fail() -> str:
    await asyncio.sleep(1)
    raise RuntimeError("failed")


async def main() -> None:
    try:
        results = await asyncio.gather(ok(), fail())
        print(results)
    except RuntimeError as error:
        print(f"捕获异常: {error}")


asyncio.run(main())
```

如果希望异常也作为结果返回，可以使用 `return_exceptions=True`：

```python
results = await asyncio.gather(
    ok(),
    fail(),
    return_exceptions=True,
)

for result in results:
    if isinstance(result, Exception):
        print(f"任务失败: {result}")
    else:
        print(f"任务成功: {result}")
```

在实际业务中，是否使用 `return_exceptions=True` 要看场景：

- 一批任务只要有一个失败就整体失败：不用
- 一批任务彼此独立，失败的单独记录：可以用

---

## 十四、超时控制

异步程序里一定要重视超时。

如果调用外部 API 不设置超时，一个请求卡住，可能拖垮整个流程。

### 14.1 wait_for

```python
import asyncio


async def slow_api() -> str:
    await asyncio.sleep(5)
    return "done"


async def main() -> None:
    try:
        result = await asyncio.wait_for(slow_api(), timeout=2)
        print(result)
    except asyncio.TimeoutError:
        print("请求超时")


asyncio.run(main())
```

### 14.2 timeout 上下文

Python 3.11 开始可以使用 `asyncio.timeout()`：

```python
import asyncio


async def slow_api() -> str:
    await asyncio.sleep(5)
    return "done"


async def main() -> None:
    try:
        async with asyncio.timeout(2):
            result = await slow_api()
            print(result)
    except TimeoutError:
        print("请求超时")


asyncio.run(main())
```

### 14.3 timeout_at 绝对超时时间

```python
async def main() -> None:
    loop = asyncio.get_event_loop()
    deadline = loop.time() + 3.0  # 绝对截止时间

    try:
        async with asyncio.timeout_at(deadline):
            await asyncio.sleep(10)
    except TimeoutError:
        print("超时了！")


asyncio.run(main())
```

适合多个任务共享同一个截止时间的场景

在 AI Agent 里，超时尤其重要：

- LLM 调用可能慢
- 工具调用可能卡住
- 数据库查询可能超时
- 外部搜索可能失败

一个健壮的 Agent 不能无限等待某个工具。

---

## 十五、取消任务 Cancellation

异步任务可以被取消。

```python
import asyncio


async def long_job() -> None:
    try:
        print("任务开始")
        await asyncio.sleep(10)
        print("任务完成")
    except asyncio.CancelledError:
        print("任务被取消，执行清理逻辑")
        raise


async def main() -> None:
    task = asyncio.create_task(long_job())
    await asyncio.sleep(1)
    task.cancel()

    try:
        await task
    except asyncio.CancelledError:
        print("main 捕获到任务取消")


asyncio.run(main())
```

注意：

- `task.cancel()` 只是请求取消
- 任务通常会在下一个 `await` 点收到 `CancelledError`
- 捕获 `CancelledError` 后，通常要重新 `raise`

在 Web 服务中，客户端断开连接、服务关闭、请求超时，都可能触发任务取消。

---

## 十六、限制并发数量：Semaphore

并发不是越多越好。

比如你要调用 1000 次 API，如果一次性全部发出去，可能会：

- 触发限流
- 耗尽连接池
- 占满内存
- 被对方服务拒绝

可以使用 `asyncio.Semaphore` 限制同时运行的任务数量。

```python
import asyncio


async def call_api(index: int, semaphore: asyncio.Semaphore) -> str:
    async with semaphore:
        print(f"开始请求 {index}")
        await asyncio.sleep(1)
        print(f"完成请求 {index}")
        return f"result-{index}"


async def main() -> None:
    semaphore = asyncio.Semaphore(3)

    tasks = [
        call_api(index, semaphore)
        for index in range(10)
    ]

    results = await asyncio.gather(*tasks)
    print(results)


asyncio.run(main())
```

这里虽然有 10 个任务，但同一时间最多只有 3 个任务进入请求逻辑。

在 OpenAI、Embedding、RAG、网页抓取等场景中，这非常常用。

---

## 十七、异步 HTTP 请求：httpx 示例

同步 HTTP 请求常见库是 `requests`。

异步 HTTP 请求常用：

- `httpx`
- `aiohttp`

`httpx` 的好处是同时支持同步和异步 API，接口比较现代。

安装：

```bash
pip install httpx
```

异步请求示例：

```python
import asyncio

import httpx


async def fetch(client: httpx.AsyncClient, url: str) -> str:
    response = await client.get(url, timeout=10)
    response.raise_for_status()
    return response.text


async def main() -> None:
    urls = [
        "https://example.com",
        "https://httpbin.org/get",
    ]

    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(
            *(fetch(client, url) for url in urls)
        )

    for html in results:
        print(len(html))


asyncio.run(main())
```

重点：

- 使用 `httpx.AsyncClient`
- 请求前加 `await`
- 用 `async with` 管理连接池
- 设置超时时间
- 用 `raise_for_status()` 处理 HTTP 错误

---

## 十八、async with：异步上下文管理器

普通上下文管理器：

```python
with open("data.txt", "r", encoding="utf-8") as file:
    content = file.read()
```

异步上下文管理器：

```python
async with httpx.AsyncClient() as client:
    response = await client.get("https://example.com")
```

`async with` 背后调用的是：

- `__aenter__()`
- `__aexit__()`

它常用于需要异步打开和关闭资源的场景：

- HTTP 客户端连接池
- 数据库连接
- Redis 连接
- WebSocket 连接
- 文件异步操作

简化示例：

```python
import asyncio


class AsyncResource:
    async def __aenter__(self) -> "AsyncResource":
        print("异步打开资源")
        await asyncio.sleep(1)
        return self

    async def __aexit__(self, exc_type, exc, traceback) -> None:
        print("异步关闭资源")
        await asyncio.sleep(1)


async def main() -> None:
    async with AsyncResource() as resource:
        print(resource)


asyncio.run(main())
```

---

## 十九、async for：异步迭代

普通 `for` 用来遍历普通可迭代对象：

```python
for item in [1, 2, 3]:
    print(item)
```

`async for` 用来遍历异步可迭代对象。

它常见于：

- 分页异步读取数据
- WebSocket 持续接收消息
- LLM 流式输出
- 异步数据库游标

### 19.1 异步生成器

```python
import asyncio


async def stream_numbers():
    for number in range(3):
        await asyncio.sleep(1)
        yield number


async def main() -> None:
    async for number in stream_numbers():
        print(number)


asyncio.run(main())
```

这里的 `stream_numbers()` 是异步生成器。

它既可以 `await`，又可以 `yield`。

---

## 二十、LLM 流式输出和 async generator

AI 应用里经常需要流式输出：

```text
模型生成一个 token
前端立刻显示一个 token
模型继续生成
前端继续显示
```

这时异步生成器非常合适。

```python
import asyncio


async def fake_llm_stream():
    tokens = ["你", "好", "，", "世", "界"]

    for token in tokens:
        await asyncio.sleep(0.3)
        yield token


async def main() -> None:
    async for token in fake_llm_stream():
        print(token, end="", flush=True)


asyncio.run(main())
```

输出会逐步出现，而不是等所有内容生成完再一次性返回。

### 20.1 FastAPI 中返回流式响应

示意代码：

```python
import asyncio

from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()


async def generate_tokens():
    tokens = ["hello", " ", "async", " ", "world"]

    for token in tokens:
        await asyncio.sleep(0.2)
        yield token


@app.get("/stream")
async def stream():
    return StreamingResponse(generate_tokens(), media_type="text/plain")
```

这就是后续做聊天机器人、Agent 前端流式响应时的基础。

---

## 二十一、OpenAI SDK 中的异步思路

具体 SDK API 以后要以你安装的版本和官方文档为准，但核心思想通常类似：

- 同步客户端：直接调用，当前流程等待
- 异步客户端：配合 `await` 使用，便于并发调用
- 流式响应：通常可以配合 `async for` 消费

一个概念示例：

```python
import asyncio


async def call_llm(prompt: str) -> str:
    await asyncio.sleep(1)
    return f"模型回答: {prompt}"


async def main() -> None:
    prompts = [
        "总结这篇文章",
        "提取关键词",
        "生成标题",
    ]

    results = await asyncio.gather(
        *(call_llm(prompt) for prompt in prompts)
    )

    for result in results:
        print(result)


asyncio.run(main())
```

在真实 OpenAI、Claude、Embedding 或 Rerank 调用中，你经常会遇到这类需求：

- 并发处理多个用户请求
- 并发生成多个候选答案
- 并发请求多个工具
- 并发生成多段文本的 embedding
- 流式读取模型输出

这时异步编程就不是“高级技巧”，而是基本功。

---

## 二十二、FastAPI 为什么天然适合异步

FastAPI 支持两种路由函数：

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/sync")
def sync_route():
    return {"message": "sync"}


@app.get("/async")
async def async_route():
    return {"message": "async"}
```

### 22.1 什么时候用 async def

如果路由内部有异步 I/O，使用 `async def`：

```python
import httpx
from fastapi import FastAPI

app = FastAPI()


@app.get("/users")
async def get_users():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://example.com/users")
        return response.json()
```

适合：

- 调异步 HTTP API
- 调异步数据库
- 调异步 Redis
- WebSocket
- 流式响应
- 异步 LLM SDK

### 22.2 什么时候用 def

如果路由内部是纯同步阻塞代码，可以先用普通 `def`：

```python
@app.get("/calculate")
def calculate():
    result = sum(range(100000))
    return {"result": result}
```

注意：不要在 `async def` 里直接调用长时间阻塞的同步函数。

错误示例：

```python
import time
from fastapi import FastAPI

app = FastAPI()


@app.get("/bad")
async def bad_route():
    time.sleep(5)  # 阻塞事件循环
    return {"ok": True}
```

应该改成：

```python
import asyncio
import time
from fastapi import FastAPI

app = FastAPI()


def blocking_work() -> str:
    time.sleep(5)
    return "done"


@app.get("/better")
async def better_route():
    result = await asyncio.to_thread(blocking_work)
    return {"result": result}
```

---

## 二十三、同步阻塞代码与 asyncio.to_thread()

很多老库没有异步版本，比如：

- `requests`
- 某些数据库 SDK
- 某些文件处理库
- 大量本地工具函数

在异步函数里直接调用这些阻塞函数，会卡住事件循环。

可以用 `asyncio.to_thread()` 把阻塞函数放到线程里执行。

```python
import asyncio
import time


def blocking_io(name: str) -> str:
    time.sleep(2)
    return f"{name} done"


async def main() -> None:
    result = await asyncio.to_thread(blocking_io, "task A")
    print(result)


asyncio.run(main())
```

并发执行多个阻塞 I/O：

```python
import asyncio
import time


def blocking_io(index: int) -> str:
    time.sleep(2)
    return f"task-{index}"


async def main() -> None:
    results = await asyncio.gather(
        *(asyncio.to_thread(blocking_io, index) for index in range(5))
    )
    print(results)


asyncio.run(main())
```

注意：

- `to_thread()` 适合阻塞 I/O
- 不适合大量 CPU 密集型计算
- CPU 密集型计算更适合进程池

---

## 二十四、异步编程中的常见错误

### 24.1 忘记 await

错误：

```python
async def get_data() -> str:
    return "data"


async def main() -> None:
    data = get_data()
    print(data)
```

输出的是协程对象，不是结果。

正确：

```python
data = await get_data()
```

### 24.2 在 async 函数里使用 time.sleep()

错误：

```python
import time


async def main() -> None:
    time.sleep(1)
```

正确：

```python
import asyncio


async def main() -> None:
    await asyncio.sleep(1)
```

### 24.3 在 async 函数里使用 requests

错误：

```python
import requests


async def get_page() -> str:
    response = requests.get("https://example.com")
    return response.text
```

更推荐：

```python
import httpx


async def get_page() -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get("https://example.com")
        return response.text
```

如果暂时必须使用 `requests`：

```python
import asyncio
import requests


def get_page_sync() -> str:
    response = requests.get("https://example.com", timeout=10)
    return response.text


async def get_page() -> str:
    return await asyncio.to_thread(get_page_sync)
```

### 24.4 以为 async 一定更快

异步不是让每一步更快，而是让等待重叠。

如果任务本身没有等待，例如纯计算：

```python
def calculate() -> int:
    return sum(i * i for i in range(10_000_000))
```

改成 `async def` 通常不会更快。

### 24.5 一次性创建太多任务

错误：

```python
tasks = [call_api(i) for i in range(10000)]
results = await asyncio.gather(*tasks)
```

更稳妥：

```python
semaphore = asyncio.Semaphore(10)


async def limited_call(index: int):
    async with semaphore:
        return await call_api(index)
```

---

## 二十五、AI Agent 中异步编程的典型场景

### 25.1 并发工具调用

Agent 可能要同时调用多个工具：

- 搜索网页
- 查询数据库
- 获取用户资料
- 检索向量数据库
- 调用外部 API

示例：

```python
import asyncio


async def search_web(query: str) -> str:
    await asyncio.sleep(1)
    return f"web result for {query}"


async def search_vector_db(query: str) -> str:
    await asyncio.sleep(1)
    return f"vector result for {query}"


async def get_user_profile(user_id: str) -> str:
    await asyncio.sleep(1)
    return f"profile for {user_id}"


async def agent_context(query: str, user_id: str) -> dict[str, str]:
    web_result, vector_result, profile = await asyncio.gather(
        search_web(query),
        search_vector_db(query),
        get_user_profile(user_id),
    )

    return {
        "web": web_result,
        "vector": vector_result,
        "profile": profile,
    }
```

如果这三个工具互不依赖，就不应该一个一个等。

### 25.2 多文档 Embedding

```python
import asyncio


async def embed_text(text: str) -> list[float]:
    await asyncio.sleep(0.5)
    return [0.1, 0.2, 0.3]


async def embed_documents(documents: list[str]) -> list[list[float]]:
    semaphore = asyncio.Semaphore(5)

    async def limited_embed(text: str) -> list[float]:
        async with semaphore:
            return await embed_text(text)

    return await asyncio.gather(
        *(limited_embed(document) for document in documents)
    )
```

这里既使用并发提升速度，又使用 `Semaphore` 控制并发，避免触发限流。

### 25.3 流式 Agent 响应

```python
import asyncio


async def agent_stream(question: str):
    steps = [
        "分析问题...",
        "检索资料...",
        "调用工具...",
        "生成回答...",
    ]

    for step in steps:
        await asyncio.sleep(0.5)
        yield step


async def main() -> None:
    async for chunk in agent_stream("什么是异步编程？"):
        print(chunk)


asyncio.run(main())
```

后续接 FastAPI 时，这种异步生成器可以直接变成接口流式响应。

---

## 二十六、一个完整小练习：异步批量抓取

下面是一个接近真实项目风格的例子：

- 使用 `httpx.AsyncClient`
- 设置超时
- 限制并发
- 捕获异常
- 汇总结果

```python
import asyncio
from dataclasses import dataclass

import httpx


@dataclass
class FetchResult:
    url: str
    ok: bool
    status_code: int | None = None
    error: str | None = None
    length: int = 0


async def fetch_one(
    client: httpx.AsyncClient,
    url: str,
    semaphore: asyncio.Semaphore,
) -> FetchResult:
    async with semaphore:
        try:
            response = await client.get(url)
            response.raise_for_status()

            return FetchResult(
                url=url,
                ok=True,
                status_code=response.status_code,
                length=len(response.text),
            )
        except httpx.HTTPError as error:
            return FetchResult(
                url=url,
                ok=False,
                error=str(error),
            )


async def fetch_all(urls: list[str]) -> list[FetchResult]:
    timeout = httpx.Timeout(10.0)
    semaphore = asyncio.Semaphore(3)

    async with httpx.AsyncClient(timeout=timeout) as client:
        tasks = [
            fetch_one(client, url, semaphore)
            for url in urls
        ]
        return await asyncio.gather(*tasks)


async def main() -> None:
    urls = [
        "https://example.com",
        "https://httpbin.org/get",
        "https://httpbin.org/status/404",
    ]

    results = await fetch_all(urls)

    for result in results:
        if result.ok:
            print(f"[OK] {result.url} {result.status_code} {result.length}")
        else:
            print(f"[ERR] {result.url} {result.error}")


if __name__ == "__main__":
    asyncio.run(main())
```

这类结构在真实项目里很常见。

---

## 二十七、学习路线建议

建议按下面顺序练：

1. 先理解 `async def`、`await`、`asyncio.run()`
2. 再掌握 `gather()` 和 `create_task()`
3. 然后练习异常、超时、取消
4. 接着学习 `Semaphore` 控制并发
5. 再练 `async with` 和 `async for`
6. 最后放到 FastAPI、OpenAI、Agent 流式输出里使用

最重要的判断标准：

> 只要你在等待网络、数据库、外部 API、模型响应，就应该想到异步。

---

## 二十八、速查表

| 写法 | 作用 | 常见场景 |
|---|---|---|
| `async def` | 定义异步函数 | 异步路由、异步工具函数 |
| `await` | 等待异步结果 | 等 HTTP、数据库、LLM |
| `asyncio.run()` | 启动异步程序 | 命令行脚本入口 |
| `asyncio.gather()` | 并发等待多个任务 | 批量 API、批量 embedding |
| `asyncio.create_task()` | 创建后台调度任务 | 先启动任务，稍后等待 |
| `asyncio.TaskGroup` | 结构化管理多个任务 | Python 3.11+ 并发任务组 |
| `asyncio.wait_for()` | 设置超时 | 防止外部调用卡死 |
| `asyncio.timeout()` | 超时上下文 | Python 3.11+ |
| `asyncio.Semaphore` | 限制并发量 | 防止 API 限流 |
| `asyncio.to_thread()` | 在线程中运行阻塞函数 | 兼容同步库 |
| `async with` | 异步资源管理 | HTTP 客户端、数据库连接 |
| `async for` | 异步迭代 | 流式输出、WebSocket |

---

## 二十九、最后总结

Python 异步编程的核心不是语法，而是思维方式：

> 当任务在等待 I/O 时，把等待时间让出来，让程序去推进其他任务。

你后续学习 FastAPI、OpenAI、AI Agent 时，会反复遇到这些问题：

- 一个接口里要不要写 `async def`
- 多个 LLM 请求如何并发
- 流式输出为什么要用 `async for`
- 为什么不能在异步路由里写 `time.sleep()`
- 为什么批量调用 API 要限制并发
- 同步 SDK 和异步 SDK 怎么选
- 工具调用失败、超时、取消怎么处理

把 `asyncio` 的这套基础打牢，后面看 FastAPI、LangChain、LangGraph、OpenAI SDK、WebSocket、SSE、Agent 工具编排时，会轻松很多。
