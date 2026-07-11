"""
迭代器是一种设计模式，它提供了一种方法顺序访问一个聚合对象中各个元素，而又不暴露该对象的内部表示

迭代对象（Iterable）：实现了 __iter()__ 方法的对象
迭代器（Iterator）：同时实现了 __iter()__ 和 __next()__ 的对象
"""

from collections.abc import Iterable

"""
两个核心方法：

__iter__(): 返回迭代器对象本身
__next__(): 返回下一个元素，当没有更多元素时，抛出 StopIteration 异常
"""

""" 迭代对象、迭代器的实现 """


class CounterIterator:
    """迭代器"""

    def __init__(self, current, end):
        self.current = current
        self.end = end

    def __iter__(self):
        return self  # 迭代器本身也是可迭代的（返回对象本身）

    def __next__(self):
        if self.current >= self.end:
            raise StopIteration  # 没有更多元素时，抛出异常
        val = self.current
        self.current += 1
        return val


class Counter:
    """一个可迭代对象"""

    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __iter__(self):
        # 返回一个迭代器实例
        return CounterIterator(self.start, self.end)


# for i in Counter(0, 5):
#     print(i)


""" 迭代器底层使用的是 iter() 和 next() """
numbers = [10, 20, 30]
iterator = iter(numbers)

# print(next(iterator))
# print(next(iterator))
# print(next(iterator))
# print(next(iterator))  # 找不到元素，抛出 StopIteration 异常


""" 判断是否可迭代 """
# print(isinstance(numbers, Iterable))
# print(isinstance(10, Iterable))


numbers_ = iter([1, 2, 3])
for number in numbers_:
    print(number)

print("第二次遍历")

# 不会进行第二次遍历，因为迭代器对象一次遍历完就会耗尽
for number in numbers_:
    print(number)

"""
迭代器相关方法：

iter(): 将迭代对象转为迭代器
next(): 获取下一个元素
"""


""" 实现自定义计数迭代器 """


class CountUp:
    def __init__(self, max_number):
        self.max_number = max_number
        self.current = 1

    def __iter__(self):
        return self

    def __next__(self):
        if self.current > self.max_number:
            raise StopIteration

        value = self.current
        self.current += 1
        return value


counter = CountUp(5)
for number in counter:
    print(number)
