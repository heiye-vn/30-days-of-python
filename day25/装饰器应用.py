"""
装饰器的常见应用场景：
打印日志、统计函数运行时间、权限校验、参数检查、缓存结果、事务处理、 Web 框架中的路由注册 等
"""

import time
from functools import lru_cache, wraps

""" 示例1. 统计函数运行时间 """


def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} 函数执行耗时 {elapsed:.4f} 秒")
        return result

    return wrapper


@timer
def embed_text(text):
    time.sleep(0.1)
    return [0.1, 0.2, 0.03]


# embed_text("hello world")


""" 示例2. 简单权限校验 """


def require_admin(func):
    @wraps(func)
    def wrapper(user, *args, **kwargs):
        if user.get("role") != "admin":
            print("权限不足")
            return None

        return func(user, *args, **kwargs)

    return wrapper


@require_admin
def delete_user(user, target_user_id: int) -> None:
    print(f"用户 {user['name']} 删除了用户 {target_user_id}")


admin = {"name": "Alice", "role": "admin"}
guest = {"name": "Bob", "role": "guest"}

# delete_user(admin, 1001)
# delete_user(guest, 1002)


""" 示例3. 使用缓存避免重复计算 """


def my_cache(func):
    data = {}

    @wraps(func)
    def wrapper(*args):
        if args in data:
            print("从缓存中读取")
            return data[args]

        result = func(*args)
        data[args] = result
        return result

    return wrapper


@my_cache
def multipy(a, b):
    print("正在计算")
    return a * b


# print(multipy(3, 4))
# print(multipy(3, 4))


# functools 中的 lru_cache 装饰器也有缓存功能
@lru_cache
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


# print(fibonacci(30))


"""
迭代器、生成器、装饰器的结合使用示例
"""


def logged(func):
    """装饰器：给生成器函数加日志"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"开始调用：{func.__name__}")
        yield from func(*args, **kwargs)  # 装饰生成器函数时用 yield from 透传
        print(f"调用完成：{func.__name__}")

    return wrapper


@logged
def chunk_stream(text, size=500):
    for i in range(0, len(text), size):
        yield text[i : i + size]


for chunk in chunk_stream("一段很长的文本" * 100):
    print(len(chunk))
