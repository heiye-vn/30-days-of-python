"""
装饰器（Decorator）

装饰器本质上是一个高阶函数，它接受一个函数作为参数，返回一个新的增强函数。
它利用了 Python 中“函数是一等公民”和“闭包”的特性

装饰器的用途：
1. 在不修改原函数代码的情况下，给函数增加功能
2. 用于日志记录、权限检查、事务处理、缓存、权限校验等场景
"""

import functools
import time
from functools import wraps


def my_decorator(func):
    def wrapper():
        print("函数开始执行")
        func()
        print("函数执行结束")

    return wrapper


def login():
    print("登录成功")


# login = my_decorator(login)
# login()


@my_decorator
def login_():
    print("login success!")


# login_()


"""
装饰带参数的函数
被装饰的函数有参数，则需要在 wrapper 中接收参数
使用 *args 和 **kwargs 可以接受任意位置参数和任意关键字参数

💡💡💡：自定义装饰器时，推荐使用 @wraps 装饰器，可以保留被装饰函数的元信息（__name__，__doc__ 等）
"""


def my_decorator2(func):
    @wraps(func)  # # 保留原函数的 __name__、__doc__ 等元信息，非常重要！
    def wrapper(*args, **kwargs):
        print("函数开始执行")
        result = func(*args, **kwargs)
        print("函数执行结束")
        return result

    return wrapper


@my_decorator2
def add(a, b):
    return a + b


# print(add(3, 5))


"""
带参数的装饰器（装饰器工厂）
装饰器本身需要接收参数时，要再包一层
"""


# 根据不同级别打印日志
def my_log(level):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            print(f"[{level}] 函数 {func.__name__} 开始执行")
            result = func(*args, **kwargs)
            print(f"[{level}] 函数 {func.__name__} 执行结束")
            return result

        return wrapper

    return decorator


@my_log("INFO")
def add(a, b):
    return a + b


# print(add(5, 10))


def retry(max_attempts=3, delay=1.0):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:  # noqa
                    last_exc = 0
                    print(f"第 {attempt} 次调用失败：{e}")
                    time.sleep(delay)
            raise last_exc

        return wrapper

    return decorator


@retry(max_attempts=5, delay=0.5)
def call_openai_embedding(text):
    pass  # 调用可能因为网络抖动失败的 API


"""
类装饰器
装饰器不仅能装饰函数，也能是一个类（只要实现 __call__ 方法），也能用来装饰类本身
"""


class CountCalls:
    def __init__(self, func):
        functools.update_wrapper(self, func)
        self.func = func
        self.count = 0

    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f"调用次数：{self.count}")
        return self.func(*args, **kwargs)


@CountCalls
def search(query):
    return f"searching {query}"


# search("rag")
# search("rag")
