"""
同步 (Synchronous)：代码按顺序执行，遇到耗时操作（如网络请求、文件读写）时，整个线程阻塞等待，
直到操作完成才继续下一行。

多线程 (Multithreading)：利用多个线程并发执行。但在 Python 中，由于 GIL（全局解释器锁） 的存在，
多线程无法真正实现 CPU 并行计算，它主要适用于 I/O 密集型任务。且线程切换有开销，共享内存需要加锁

异步 (Asynchronous / asyncio)：单线程内的并发。通过事件循环（Event Loop）和协程（Coroutine），
在遇到 I/O 等待时主动让出控制权，去执行其他任务
"""

import asyncio
import time

"""
asyncio: Python 官方的异步框架
包含：Event Loop、Task、Future、Coroutine、Queue、Lock、Semaphore 等
"""

"""
异步编程的核心组件：
主要用的是内置 asyncio 模块，常见概念有：
- async def：定义协程函数
- coroutine：协程对象
- await：等待一个异步操作完成（只能在协程函数中使用）
- event loop：事件循环
- task：被事件循环调度的任务
- asyncio.run()：启动事件循环并运行入口协程
- asyncio.create_task()：创建并发任务
- asyncio.gather()：等待多个任务完成
- async with：异步上下文管理器
- async for：异步迭代
"""


"""
协程（Coroutine）
协程是异步编程的基本单元。是一个可以暂停和恢复执行的函数，使用 async def 定义协程函数

调用协程函数不会立即执行，而是返回一个协程对象
需要使用 asyncio.run 来执行或者在另一个协程函数中使用 await 来执行

💡：await 关键字只能出现在协程函数内部，本质是暂停当前协程的执行，将控制权交还给事件循环
"""


async def hello():
    print("hello")


# asyncio.run(hello())


async def fetch_data():
    print("开始获取数据...")
    await asyncio.sleep(2)  # 模拟 I/O 操作
    return {"data": "hello"}


# result = asyncio.run(fetch_data())
# print(result)


# 并发执行多个协程
async def embed_chunk(chunk: str, delay: float) -> list[float]:
    await asyncio.sleep(delay)  # 模拟调用 embedding API
    return [0.1, 0.2, 0.3]  # 模拟返回的向量数据


async def main():
    chunks = ["chunk1", "chunk2", "chunk3"]

    start = time.time()
    # gather: 并发运行多个协程，等所有结果都返回
    results = await asyncio.gather(*(embed_chunk(chunk, 1.0) for chunk in chunks))
    print(f"耗时：{time.time() - start:.2f}秒")
    print(results)


# asyncio.run(main())

"""
await：等待异步操作，即等待一个可等待对象完成
- 协程对象
- asyncio.Task
- 某些异步库返回的对象
"""


async def say_hello() -> str:
    await asyncio.sleep(1)
    return "hello"


async def main2() -> None:
    message = await say_hello()
    print(message)


# asyncio.run(main2())


"""
Task：被事件循环调度的协程

使用 asyncio.create_taks() 将协程包装成任务，交给事件循环调度
"""


async def fetch(name: str, seconds: int) -> str:
    print(f"{name} start")
    await asyncio.sleep(seconds)
    print(f"{name} end")
    return name


async def main3() -> None:
    task = asyncio.create_task(fetch("A", 2))
    print("task created")

    result = await task
    print(result)


# asyncio.run(main3())


"""
取消任务（Cancellation）
异步任务可以被取消
"""


async def long_job() -> None:
    try:
        print("任务开始")
        await asyncio.sleep(10)
        print("任务完成")
    except asyncio.CancelledError:
        print("任务被取消，执行清理逻辑")
        raise


async def main4() -> None:
    task = asyncio.create_task(long_job())
    await asyncio.sleep(1)
    task.cancel()

    try:
        await task
    except asyncio.CancelledError:
        print("main 捕获到任务取消")


# asyncio.run(main4())


"""
限制并发数量（Semaphore）
"""


async def call_api(index: int, semaphore: asyncio.Semaphore) -> str:
    async with semaphore:
        print(f"开始请求 {index}")
        await asyncio.sleep(1)
        print(f"完成请求 {index}")
        return f"result-{index}"


async def main5() -> None:
    semaphore = asyncio.Semaphore(3)

    tasks = [call_api(index, semaphore) for index in range(10)]

    results = await asyncio.gather(*tasks)
    print(results)


# start = time.time()
# asyncio.run(main5())
# print(f"执行时间：{time.time() - start:.2f} s")


"""
异步山下文管理器（async with）
内部实现的是 __aenter()__ 和 __aexit__() 方法
"""


"""
异步生成器（async for）
用于遍历异步可迭代对象

async for item in iterable:
等价于JavaScript中的：for await (const item of iterable)
"""


async def stream_lines():
    for i in range(5):
        await asyncio.sleep(0.5)  # 模拟异步 I/O
        yield f"第 {i} 行数据"


async def stream_numbers():
    for number in range(3):
        await asyncio.sleep(1)
        yield number


async def main6() -> None:
    async for line in stream_lines():
        print(line)


asyncio.run(main6())
