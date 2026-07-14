import asyncio

from fastapi import FastAPI
from fastapi.responses import StreamingResponse


# 使用异步（迭代）生成器实现流式输出
async def fake_llm_stream():
    tokens = ["你", "好", "，", "世界"]

    for token in tokens:
        await asyncio.sleep(0.3)
        yield token


async def main() -> None:
    async for token in fake_llm_stream():
        print(token, end="", flush=True)


# asyncio.run(main())


"""
FastAPI 中返回流式响应示例
"""
app = FastAPI()


async def generate_tokens():
    tokens = ["hello", " ", "async", " ", "world"]

    for token in tokens:
        await asyncio.sleep(0.2)
        yield token


@app.get("/stream")
async def stream():
    return StreamingResponse(generate_tokens(), media_type="text/plain")


async def agent_stream(question: str):
    steps = [
        "分析问题...",
        "检索资料...",
        "调用工具...",
        "生成回答...",
    ]

    for step in steps:
        await asyncio.sleep(0.5)
        yield step


async def main2() -> None:
    async for chunk in agent_stream("什么是异步编程？"):
        print(chunk)


# asyncio.run(main2())
