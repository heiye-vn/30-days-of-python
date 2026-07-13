"""
同步 HTTP 请求的常用库为：requests

异步 HTTP 请求常用：httpx、aiohttp
"""

import asyncio

import httpx

"""
httpx: 同时支持同步和异步 API
"""


async def fetch(client: httpx.AsyncClient, url: str) -> str:
    response = await client.get(url, timeout=10)
    response.raise_for_status()  # 处理 HTTP 错误
    return response.text


async def main() -> None:
    urls = ["https://example.com", "https://jsonplaceholder.typicode.com/posts/1"]

    # 使用异步上下文管理器（async with）管理连接池
    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(*(fetch(client, url) for url in urls))

    for html in results:
        print(len(html))


asyncio.run(main())
