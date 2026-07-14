import asyncio
import time

# import random
from typing import Any, Dict, List

# ==========================================
# 场景：AI 智能助手（Agent）信息检索与多工具并行调用
# ==========================================
# 典型场景描述：
# 当用户向 Agent 提出复杂问题时（例如：“帮我分析下苹果公司今天的股价，并结合我之前的投资偏好，生成一份简报”），
# Agent 需要执行以下异步/并发操作以提升响应速度和用户体验：
# 1. 【并发检索】并发查询：用户画像库（DB）、历史上下文、实时网络搜索（Web Search）。
# 2. 【并行工具调用】根据 LLM 决策，并行调用多个外部 API（如苹果股价 API、科技新闻 API）。
# 3. 【异步流式输出】在后台进行日志审计和分析的同时，向用户流式输出（Streaming）生成的简报。


# 模拟异步延迟的网络请求/数据库查询
async def fetch_user_profile(user_id: str) -> Dict[str, Any]:
    print(f"[DB] 开始读取用户 {user_id} 的投资偏好...")
    await asyncio.sleep(1.0)  # 模拟网络/数据库延迟
    profile = {"user_id": user_id, "preference": "科技股, 风险偏好保守", "name": "张三"}
    print(f"[DB] 用户 {user_id} 偏好读取完成: {profile['preference']}")
    return profile


async def search_web_news(query: str) -> List[str]:
    print(f"[Search] 开始在全网搜索: '{query}' 的最新动态...")
    await asyncio.sleep(1.5)  # 模拟网页爬取和搜索延迟
    results = [
        "苹果发布了最新的 AI 战略，市场反响热烈。",
        "分析师上调苹果公司目标价至 240 美元。",
    ]
    print(f"[Search] 网页搜索完成，获取到 {len(results)} 条相关新闻")
    return results


async def get_stock_price(ticker: str) -> Dict[str, Any]:
    print(f"[API] 开始请求 {ticker} 的实时股价...")
    await asyncio.sleep(0.8)  # 模拟第三方 API 接口调用延迟
    price_info = {"ticker": ticker, "price": 224.50, "change": "+1.2%"}
    print(f"[API] 股价获取成功: {ticker} -> {price_info['price']}")
    return price_info


# 模拟 Agent 的流式文本输出
async def stream_llm_response(prompt: str):
    print(f"提示词：{prompt}")
    print("\n[LLM] 开始生成简报 (流式输出中)...")
    response_text = (
        "【苹果公司投资简报】\n"
        "根据您的投资偏好（保守型，关注科技股），目前苹果公司（AAPL）股价为 224.50 美元，今日上涨 1.2%。\n"
        "近期新闻显示分析师普遍看好其最新的 AI 战略。建议您继续保持观察，无需急于调仓。\n"
    )

    # 模拟流式生成 token
    for char in response_text:
        print(char, end="", flush=True)
        await asyncio.sleep(0.03)  # 模拟打字机效果
    print("\n[LLM] 简报生成完毕。\n")


# 模拟后台审计/日志记录任务（不需要阻塞主流程）
async def background_audit_log(action: str, duration: float):
    print("[Audit] [后台] 开始记录 Agent 行为日志...")
    await asyncio.sleep(2.0)  # 模拟写入慢速日志系统或云端监控
    print(f"[Audit] [后台] 日志记录成功。操作: {action}, 耗时: {duration:.2f}s")


# Agent 核心协同逻辑
async def run_agent(user_id: str, ticker: str):
    start_time = time.time()
    print("=== Agent 任务启动 ===")

    # ----------------------------------------------------
    # 阶段 1：并发检索外部上下文 (Concurrent Context Retrieval)
    # ----------------------------------------------------
    # 我们不希望顺序等待 DB 读完再去 Search，因此使用 asyncio.gather 并发执行
    print("\n--- 阶段 1：并发检索上下文 ---")
    user_task = fetch_user_profile(user_id)
    search_task = search_web_news(f"{ticker} 股价 新闻")
    stock_task = get_stock_price(ticker)

    # gather 会并发调度这三个协程，总耗时约等于耗时最长的那一个任务 (1.5s)，而不是三者相加 (1.0 + 1.5 + 0.8 = 3.3s)
    user_profile, news_list, stock_info = await asyncio.gather(
        user_task, search_task, stock_task
    )

    retrieval_duration = time.time() - start_time
    print(
        f"[*] 阶段 1 完成！并发检索耗时: {retrieval_duration:.2f}s (若串行则需约 3.3s)"
    )

    # ----------------------------------------------------
    # 阶段 2：大模型推理与流式响应 + 后台审计并发执行
    # ----------------------------------------------------
    print("\n--- 阶段 2：LLM 流式输出 与 后台任务并行 ---")
    prompt = f"用户偏好: {user_profile}, 实时数据: {stock_info}, 相关新闻: {news_list}"

    # 我们可以把 LLM 流式输出与后台审计任务同时放入事件循环。
    # 对于用户来说，他能立刻看到打字机流式输出，而审计日志在后台悄悄写入，不阻塞用户的交互。
    # 使用 asyncio.create_task 将审计任务提交到后台运行
    audit_task = asyncio.create_task(
        background_audit_log(
            action=f"generate_report_{ticker}", duration=retrieval_duration
        )
    )

    # 阻塞等待流式输出完成
    await stream_llm_response(prompt)

    # 确保后台任务也执行完了再退出程序（生产环境中，常驻服务无需显式 await 后台任务退出）
    await audit_task

    total_duration = time.time() - start_time
    print(f"=== Agent 任务全部结束，总耗时: {total_duration:.2f}s ===")


if __name__ == "__main__":
    # 启动异步事件循环
    asyncio.run(run_agent(user_id="usr_9527", ticker="AAPL"))
