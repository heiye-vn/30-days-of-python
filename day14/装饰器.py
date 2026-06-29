"""
装饰器（Decorator）是高阶函数最典型、最常用的应用场景，没有之一。

可以理解为它是一个标准并且完整的“函数加工厂”
"""

import time
from functools import wraps

"""
高阶函数的本质：底层实质上就是一行高阶函数的调用

@my_decorator
def my_func():
    pass

my_func = my_decrotator(my_func)

输入：把 my_func 函数作为参数传给 my_decorator。
输出：my_decorator 加工后，返回一个新的函数（通常叫 wrapper）并覆盖原有的 my_func
"""


# 简单的“耗时统计”装饰器
def timer(func):
    # 内部定义一个加工后的新函数，接收任意位置参数和关键字参数
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()

        result_ = func(*args, **kwargs)  # 调用传入的 "原函数"
        end = time.time()
        print(f"执行耗时：{end - start:.4f} 秒")
        return result_

    return wrapper


# 使用装饰器（语法糖：@）
@timer
def download_file():
    print("开始下载...")
    time.sleep(1.5)  # 模拟下载耗时
    print("下载完成。")


# 调用 download_file，实际上运行的是加工后的 wrapper 函数
download_file()
print(download_file.__name__)


# 带参数的装饰器
def repeat(times):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(times):
                result = func(*args, **kwargs)
            return result

        return wrapper

    return decorator


@repeat(3)
def greet(name):
    print(f"你好, {name}!")


# greet("张三")


"""
总结：

无参数装饰器：只需要两层结构（最外层接收函数 func，最内层接收函数参数 args/kwargs）

有参数装饰器：需要三层结构（最外层接收装饰器参数，第二层接收函数 func，最内层接收函数参数 args/kwargs）
"""
