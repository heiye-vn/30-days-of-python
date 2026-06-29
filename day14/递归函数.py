"""
递归函数：函数调用自身
"""

import time
from functools import lru_cache


# 阶乘： n * (n - 1) * (n - 2) * ... * 1
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)


# print(factorial(5))


"""
斐波拉契数列
"""


def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


# 测试运算时间
start = time.time()
result = fibonacci(35)
end = time.time()
print(f"fibonacci 结果：{result}")
print(f"fibonacci 运算时间：{end - start:.4f} 秒")


"""
使用 lru_cache 优化

lru_cache 是一个装饰器，用于缓存函数结果，避免重复计算

fibonacci(100) 的执行时间很久，无止境，一直在重复计算
fibonacci_fast(100) 几乎在毫秒级完成计算
"""


@lru_cache()
def fibonacci_fast(n):
    if n <= 1:
        return n
    return fibonacci_fast(n - 1) + fibonacci_fast(n - 2)


# 测试运算时间
start_ = time.time()
result_ = fibonacci_fast(100)
end_ = time.time()
print(f"fibonacci_fast 结果：{result_}")
print(f"fibonacci_fast 运算时间：{end_ - start_:.4f} 秒")
