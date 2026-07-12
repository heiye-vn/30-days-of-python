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


asyncio.run(main())
