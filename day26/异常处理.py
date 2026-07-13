import asyncio


# 普通 await 的异常处理
async def risky() -> str:
    await asyncio.sleep(1)
    raise ValueError("出错了")


async def main() -> None:
    try:
        result = await risky()
        print(result)
    except ValueError as e:
        print(f"捕获异常：{e}")


# asyncio.run(main())


"""
gather 中的异常
默认情况下，gather() 中任何一个任务抛出异常，gather() 会把异常继续抛出去
"""


async def ok() -> str:
    await asyncio.sleep(1)
    return "ok"


async def fail() -> str:
    await asyncio.sleep(1)
    raise RuntimeError("failed")


async def main2() -> None:
    try:
        results = await asyncio.gather(ok(), fail())
        print(results)
    except RuntimeError as error:
        print(f"捕获异常：{error}")


# asyncio.run(main2())


"""
使用 return_exceptions=True 可将异常也返回
使用场景：
- 一批任务只要有一个失败就整体失败：不用
- 一批任务彼此独立，失败的单独记录：可以用
"""


async def main3() -> None:
    results = await asyncio.gather(ok(), fail(), return_exceptions=True)

    for result in results:
        if isinstance(result, Exception):
            print(f"任务失败：{result}")
        else:
            print(f"任务成功：{result}")


asyncio.run(main3())
