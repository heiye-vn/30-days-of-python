
"""
基于 asyncio 实现基础异步协程并发
"""

import asyncio
import time


async def task(name):
    print(f"{name} 开始执行")
    
    await asyncio.sleep(2)  # 模拟异步 I/O 等待
    
    """ 三个协程任务在同一个线程中，而 time.sleep 会同步阻塞当前线程，因此每个任务在执行时都会等待 2 秒 """
    # time.sleep(2)
    
    print(f"{name} 执行结束")


async def main():
    await asyncio.gather(
        task("任务1"),
        task("任务2"),
        task("任务3")
    )


asyncio.run(main())
