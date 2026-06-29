"""
装饰器（Decorator）是高阶函数最典型、最常用的应用场景，没有之一。

可以理解为它是一个标准并且完整的“函数加工厂”
"""
import time

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
    def wrapper(*args, **kwargs):
        start = time.time()
        result_ = func(*args, **kwargs)  # 调用传入的 “原函数”
        end = time.time()
        print(f"执行耗时：{end - start:.4f} 秒")
        return result_

    # 将加工好的新函数返回
    return wrapper


# 使用转时期（语法糖：@）
@timer
def download_file():
    print("开始下载...")
    time.sleep(1.5)  # 模拟下载耗时
    print("下载完成。")


# 调用 download_file，实际上运行的是加工后的 wrapper 函数
download_file()
