from typing import Any

import requests

# 推荐使用 httpbin.org 进行网络请求测试（返回你的请求信息）
# url = "https://httpbin.org/get"
# 如果上述 URL 访问较慢，可以使用国内 CDN 加速的公开 API（一言 API，返回 JSON 格式的随机短句）
url = "https://v1.hitokoto.cn"

# response = requests.get(url, timeout=10)
# data = response.json()

# print(response.status_code)
# print(data)
# print(data["hitokoto"])


"""状态码检查"""
# response2 = requests.get("https://api.github.com/users/heiye-vn", timeout=10)
#
# if response2.status_code == 404:
#     print("用户不存在")
# else:
#     response2.raise_for_status()
#     data = response2.json()
#     print(data)
#     print(data["login"])

"""状态码与异常检查 (使用国内稳定接口，免受限流与网络波动影响)"""
# 模拟请求一个不存在的路径，该接口会返回 404 状态码
# response3 = requests.get("https://v1.hitokoto.cn/not-exists-route", timeout=10)
#
# print(f"请求返回状态码: {response3.status_code}")
# if response3.status_code == 404:
#     print("资源不存在 (404)")
# else:
#     try:
#         # 如果不是 2xx 状态码，会抛出 HTTPError 异常
#         response3.raise_for_status()
#         print("请求成功")
#     except requests.exceptions.HTTPError as e:
#         print(f"HTTP 请求异常: {e}")


""" 使用 params 传递查询参数 (使用 JSONPlaceholder 代替不稳定的 httpbin) """
# 这是一个非常稳定的免费测试 API，用于获取博客文章的评论列表
# req_url = "https://jsonplaceholder.typicode.com/comments"

# 使用 params 过滤 postId 为 1 的评论（相当于请求：.../comments?postId=1）
# params = {"postId": 1}
# response4 = requests.get(url=req_url, params=params, timeout=10)
# data = response4.json()

# 打印返回的评论数据列表（会返回 5 条数据）
# print(f"获取到的评论数: {len(data)}")
# print(data[0])  # 打印第一条评论以作展示
# print(response4.url)


"""
requests.Session(): 创建会话对象
作用：
1. 自动管理与传递 Cookies（状态保持）
2. TCP 连接复用（Keep-Alive）
3. 共享全局参数（Headers、Auth、Proxies）
"""
# 模拟状态保持
session = requests.Session()

# 访问一个设置 Cookie 的测试接口（比如登录接口）
# session.get("https://v1.hitokoto.cn")  # 此时 session 会自动保存返回的 Cookies
# 发送新的请求时，session 会自动带上之前保存的所有 cookies
# response = session.get("https://v1.hitokoto.cn")
# 打印当前 session 保存的 cookies
# print(session.cookies.get_dict())


# 共享全局 Headers
with requests.Session() as session:
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Authorization": "Bearer YOUR_TOKEN",
    })

    # 第一次请求
    res1 = session.get("https://jsonplaceholder.typicode.com/posts/1")

    # 第二次请求（自动复用上一次的 TCP 连接，并携带相同的 Headers）
    res2 = session.get("https://jsonplaceholder.typicode.com/posts/2")

    # print(res1.status_code, res2.status_code)


"""
将 requests 封装成可复用函数
"""


def frtch_github_user(username: str) -> dict[str, Any]:
    url = f"https://api.github.com/users/{username}"
    response = requests.get(url, timeout=10)

    if response.status_code == 404:
        raise ValueError(f"GitHub 用户不存在：{username}")

    response.raise_for_status()
    return response.json()


def format_user_summary(user: dict[str, Any]) -> str:
    return (
        f"{user['login']} | "
        f"followers={user['followers']} | "
        f"repos={user['public_repos']}"
    )


def main() -> None:
    user = frtch_github_user("heiye-vn")
    summary = format_user_summary(user)
    print(summary)


if __name__ == "__main__":
    main()
