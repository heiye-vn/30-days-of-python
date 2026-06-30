"""
timeit 模块。官方提供的基准测试功能，用于测试小段代码的执行时间。
默认执行 1,000,000 次代码并返回总耗时（秒），有效清除单次运行的随机误差
"""

import timeit

"""
常用API

timeit.timeit(stmt, setup, number): 测量单行或多行代码的执行时间
timeit.repeat(stmt, setup, repeat, number): 重复多次测量，返回一个时间列表
"""

"""
Demo: 测试【列表推导式】和 【map】的性能
"""

# 测试列表推导式
list_comp_time = timeit.timeit(
    stmt="[x**2 for x in range(1000)]",
    number=10000
)

# 测试 map 函数
map_time = timeit.timeit(
    stmt="list(map(lambda x: x**2, range(1000)))",
    number=10000
)


# print(f"列表推导式耗时：{list_comp_time:.4f} 秒")
# print(f"map 函数耗时：{map_time:.4f} 秒")


# 测量一段代码执行 100 万次的总时间
# t = timeit.timeit('"-".join(str(n) for n in range(100))', number=1_000_000)
# print(f"{t:.3f} 秒")


# 在函数上使用（更常见）
def my_func():
    return sum(range(1000))


t = timeit.timeit(my_func, number=10_000)
print(f"平均每次: {t / 10_000 * 1e6:.2f} 微秒")
