"""
Task：异步任务
"""

import asyncio

"""
create_task(): 手动创建任务

💡：使用 create_task() 创建的任务最好使用 await
"""


async def background_sync() -> None:
    await asyncio.sleep(2)
    print("后台任务同步完成")


async def main() -> None:
    task = asyncio.create_task(background_sync())

    print("继续处理主流程")
    await asyncio.sleep(1)
    print("主流程处理了一部分")

    await task


# asyncio.run(main())


"""
TaskGroup(): 更结构化的并发，清晰管理任务组

特点：
- 任务生命周期更清晰
- 其中一个任务失败时，其他任务会被取消
- 更适合结构化并发
"""


async def job(name: str, seconds: int) -> str:
    await asyncio.sleep(seconds)
    return name


async def main2() -> None:
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(job("A", 2))
        task2 = tg.create_task(job("B", 1))

    print(task1.result())
    print(task2.result())


asyncio.run(main2())
