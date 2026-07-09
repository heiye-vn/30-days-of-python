"""
泛型：让类型保持关联
"""

from typing import Generic, TypeVar


# 普通函数
def first(items: list[int]) -> int:
    return items[0]


# 使用泛型
T = TypeVar("T")


def second(items: list[T]) -> T:
    return items[0]


# print(second([1, 2, 3, 4]))
# print(second(["Python", "Java", "Node"]))


"""
泛型类
"""


class Box(Generic[T]):
    def __init__(self, value: T):
        self.value = value

    def get(self) -> T:
        return self.value


# int_box = Box[int](123)
# print(int_box.get())

# str_box = Box[str]("hello")
# print(str_box.get())


# 或者更简洁的写法
class BoxSample[T]:
    def __init__(self, value: T):
        self.value = value

    def get(self) -> T:
        return self.value


print(BoxSample[int](123456).get())
