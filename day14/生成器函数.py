from collections.abc import Generator
import sys

"""
yield 关键字

生成器是一种特殊的函数，用 yield 代替 return，每次承产出一个值后暂停
"""


def count_up(n):
    i = 1
    while i <= n:
        yield i
        i += 1


# for num in count_up(5):
#     print(num)


"""
生成器表达式

类似列表推导式，但用圆括号，非元组，返回的是一个生成器（generator）对象
"""
squares_gen = (x * x for x in range(10))
# print(type(squares_gen))  # <class 'generator'>
# print(isinstance(squares_gen, Generator)) # True
# print(list(squares_gen))


"""
生成器的优势：惰性求值，节省内存
"""
# 列表: 一次性生成所有元素，占用大量内存
big_list = [x * x for x in range(10000000)]
print(f"列表占用内存: {sys.getsizeof(big_list) / 1024 / 1024:.2f} MB")

# 生成器：按需生产，几乎不占内存
big_gen = (x * x for x in range(10000000))
print(f"生成器占用内存: {sys.getsizeof(big_gen)} 字节")
