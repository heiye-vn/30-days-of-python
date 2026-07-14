import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

import httpx
import requests

"""
使用线程处理并发（ThreadPoolExecutor）

针对同步函数，可使用线程池方式处理并发
"""


def fetch_github_user(username: str) -> dict[str, Any]:
    url = f"https://api.github.com/users/{username}"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def main() -> None:
    usernames = ["heiye-vn", "afei", "coderwhy", "pallets", "psf"]

    # 同时运行 5 个线程，executor.map 会按照输入顺序返回结果
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = executor.map(fetch_github_user, usernames)

    for user in results:
        print(user["login"], user["public_repos"])


# 使用 as_completed 获取先完成的结果
def main2() -> None:
    usernames = ["heiye-vn", "afei", "coderwhy", "pallets", "psf"]

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(fetch_github_user, username): username
            for username in usernames
        }

        for future in as_completed(futures):
            username = futures[future]
            try:
                user = future.result()
            except Exception as exc:
                print(f"{username} 请求失败：{exc}")
            else:
                print(user["login"], user["public_repos"])


"""
使用 asyncio、httpx 处理异步并发，控制异步并发数量，处理部分请求失败
"""


async def get_github_user(
    client: httpx.AsyncClient, username: str, semaphore: asyncio.Semaphore
) -> dict[str, Any]:
    async with semaphore:
        response = await client.get(f"/users/{username}")
        response.raise_for_status()
        return response.json()


async def main3() -> None:
    usernames = [
        "heiye-vn",
        "afei",
        "coderwhy",
        "not-exists-user-xyz",
        "pallets",
        "psf",
    ]
    semaphore = asyncio.Semaphore(3)

    async with httpx.AsyncClient(
        base_url="https://api.github.com", timeout=10
    ) as client:
        tasks = [get_github_user(client, username, semaphore) for username in usernames]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    for username, result in zip(usernames, results):
        if isinstance(result, Exception):
            print(f"{username} 请求失败：{result}")
        else:
            print(result["login"], result["public_repos"])


if __name__ == "__main__":
    # main()
    # main2()
    asyncio.run(main3())
