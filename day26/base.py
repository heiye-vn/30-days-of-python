import asyncio
import time


# 同步代码
def download(name: str, seconds: int) -> str:
    print(f"开始下载 {name}")
    time.sleep(seconds)
    print(f"下载完成 {name}")
    return name


def main() -> None:
    download("file A", 2)
    download("file B", 3)
    download("file C", 1)


# main()


# 异步执行


async def download_(name: str, seconds: int) -> str:
    print(f"开始下载 {name}")
    await asyncio.sleep(seconds)
    print(f"下载完成 {name}")
    return name


async def main_() -> None:
    results = await asyncio.gather(
        download_("FileA", 2), download_("FileB", 3), download_("FileC", 1)
    )
    print(results)


if __name__ == "__main__":
    start = time.time()
    # main()
    asyncio.run(main_())
    print(f"总耗时：{time.time() - start:.2f}秒")
