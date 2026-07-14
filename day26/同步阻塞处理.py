"""
在异步函数中调用同步阻塞函数，会卡主整个事件循环

比如：调用 requests.get()、time.sleep() 等
"""

import asyncio
import time

import requests
from fastapi import FastAPI

app = FastAPI()


# ❌️：错误示例（会卡死事件循环）
@app.get("bad")
async def bad_route():
    # 阻塞操作直接在主线程/事件循环中运行，卡死整个服务
    res = requests.get("https://api.github.com")
    return res.json()


# ✅️：正确写法（使用 asyncio.to_thread）
@app.get("/good")
async def good_route():
    # 将同步阻塞的 requests.get 扔进子线程运行，并用 await 等待其结果
    # 主事件循环不会被卡死，可以继续处理其他请求
    res = await asyncio.to_thread(requests.get, "https://api.github.com")
    return res.json()


""" 使用 asyncio.to_thread() 把阻塞函数放到线程里执行 """


def blocking_io(name: str) -> str:
    time.sleep(2)
    return f"{name} done"


async def main() -> None:
    result = await asyncio.to_thread(blocking_io, "task A")
    print(result)


# asyncio.run(main())


""" 并发执行多个阻塞 I/O """


def blocking_io2(index: int) -> str:
    time.sleep(2)
    return f"task-{index}"


async def main2() -> None:
    results = await asyncio.gather(
        *(asyncio.to_thread(blocking_io2, index) for index in range(5))
    )
    print(results)


# asyncio.run(main2())
