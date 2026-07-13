import asyncio

"""顺序执行"""


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


# asyncio.run(main())


"""并发执行"""


async def main2() -> None:
    task1 = asyncio.create_task(job("A", 2))
    task2 = asyncio.create_task(job("B", 3))
    task3 = asyncio.create_task(job("C", 1))

    result1 = await task1
    result2 = await task2
    result3 = await task3

    print(result1, result2, result3)


# asyncio.run(main2())


"""使用 asyncio.gather() 简化 """


async def main3() -> None:
    results = await asyncio.gather(job("A", 2), job("B", 3), job("C", 1))
    print(results)


# 会按传入的协程/task顺序返回结果
# asyncio.run(main3())  # ['A', 'B', 'C']


"""
asyncio.gather()：批量并发，常用于：
- 同时请求多个 API
- 同时处理多个用户输入
- 同时调用多个 Agent 工具
- 同时执行多个检索任务
"""


# 并发获取多个 URL
async def fetch_url(url: str) -> str:
    await asyncio.sleep(1)
    return f"content from {url}"


async def main4() -> None:
    urls = [
        "https://example.com/a",
        "https://example.com/b",
        "https://example.com/c",
    ]

    # 【*】表示参数解包
    results = await asyncio.gather(*(fetch_url(url) for url in urls))

    for result in results:
        print(result)


asyncio.run(main4())
