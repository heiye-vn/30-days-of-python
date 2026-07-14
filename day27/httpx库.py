"""
httpx：现代 HTTP 客户端，支持：
同步请求、异步请求、连接池、超时配置、HTTP/2
"""

import asyncio

import httpx

""" httpx 同步请求 """

# url = "https://api.github.com/users/octocat"
#
# response = httpx.get(url, timeout=10)
# response.raise_for_status()

# data = response.json()
# print(data["login"])


"""
httpx.Client，客户端对象，类似 requests.Session
"""


def fetch_user(username: str) -> dict:
    with httpx.Client(
        base_url="https://api.github.com",
        headers={"User-Agent": "python-study-demo/1.0"},
        timeout=10,
    ) as client:
        response = client.get(f"/users/{username}")
        response.raise_for_status()
        return response.json()


# user = fetch_user("heiye-vn")
# print(user)


""" httpx 异步请求 """


async def fetch_user2(username: str) -> dict:
    async with httpx.AsyncClient(
        base_url="https://api.github.com", timeout=10
    ) as client:
        response = await client.get(f"/users/{username}")
        response.raise_for_status()
        return response.json()


async def main() -> None:
    user = await fetch_user2("afei")
    print(user)


# asyncio.run(main())
