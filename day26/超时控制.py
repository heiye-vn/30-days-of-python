"""
asyncio 提供了多种超时控制机制
"""

import asyncio

"""
asyncio.wait_for()
基础的超时控制，超时后会自动取消被包裹的协程，并抛出 asyncio.TimeoutError
适合对单个协程设置超时
"""


async def slow_api() -> str:
    await asyncio.sleep(5)
    return "done"


async def main() -> None:
    try:
        print("接口请求中...")
        result = await asyncio.wait_for(slow_api(), timeout=2)
        print(result)
    except asyncio.TimeoutError:
        print("请求超时")


# asyncio.run(main())


"""
asyncio.timeout() —— 推荐
基于上下文管理器，可以包裹多条语句，适合一段代码块的超时控制
"""


async def main2() -> None:
    try:
        print("接口请求中...")
        async with asyncio.timeout(2):
            result = await slow_api()
            print(result)
    except TimeoutError:
        print("请求超时")


# asyncio.run(main2())


# 动态调整超时
async def main3() -> None:
    try:
        print("接口请求中...")
        async with asyncio.timeout(5.0) as cm:
            # 根据条件动态延长超时
            # cm.reschedule(asyncio.get_event_loop().time() + 10.0)
            await asyncio.sleep(8)
            print("完成！")
    except TimeoutError:
        print("超时了！")


# asyncio.run(main3())


"""
asyncio.timeout_at()
绝对超时时间，适合多个任务共享同一个截止时间的场景
"""


async def main4() -> None:
    loop = asyncio.get_event_loop()
    deadline = loop.time() + 3.0  # 绝对截止时间

    try:
        async with asyncio.timeout_at(deadline):
            await asyncio.sleep(10)
    except TimeoutError:
        print("超时了！")


# asyncio.run(main4())


"""
Demo: 带超时的重试
"""


async def fetch_data():
    await asyncio.sleep(2)
    return {"status": "ok"}


async def fetch_with_retry(max_retries=3, timeout=1.5):
    for attempt in range(1, max_retries + 1):
        try:
            async with asyncio.timeout(timeout):
                result = await fetch_data()
                return result
        except TimeoutError:
            print(f"第 {attempt} 次尝试超时")
            if attempt == max_retries:
                raise  # 最后一次仍超时，向上抛出
            await asyncio.sleep(0.5 * attempt)  # 退避等待
    return None


# asyncio.run(fetch_with_retry())
