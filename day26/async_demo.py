"""
Demo: 异步批量抓取
"""

import asyncio
from dataclasses import dataclass

import httpx


@dataclass
class FetchResult:
    url: str
    ok: bool
    status_code: int | None = None
    error: str | None = None
    length: int = 0


async def fetch_one(
    client: httpx.AsyncClient, url: str, semaphore: asyncio.Semaphore
) -> FetchResult:
    async with semaphore:
        try:
            response = await client.get(url)
            response.raise_for_status()

            return FetchResult(
                url=url,
                ok=True,
                status_code=response.status_code,
                length=len(response.text),
            )
        except httpx.HTTPError as error:
            return FetchResult(url=url, ok=False, error=str(error))


async def fetch_all(urls: list[str]) -> list[FetchResult]:
    timeout = httpx.Timeout(10.0)
    semaphore = asyncio.Semaphore(3)

    async with httpx.AsyncClient(timeout=timeout) as client:
        tasks = [fetch_one(client, url, semaphore) for url in urls]
        return await asyncio.gather(*tasks)


async def main() -> None:
    urls = [
        "https://example.com",
        "https://httpbin.org/get",
        "https://httpbin.org/status/404",
    ]

    results = await fetch_all(urls)

    for result in results:
        if result.ok:
            print(f"[OK] {result.url} {result.status_code} {result.length}")
        else:
            print(f"[ERR] {result.url} {result.error}")


if __name__ == "__main__":
    asyncio.run(main())
