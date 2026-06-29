from beartype import beartype
from typeguard import typechecked


def greet(name: str, age: int = 18) -> str:
    return f"你好，我叫{name}，今年{age}岁"


# print(greet("小明"))
# print(greet("张三", 20))
# print(greet("小红", "十六"))  # noqa 运行不会报错，编辑器会提示类型错误（noqa 可以忽略类型错误）

"""
以上的类型注解方式仅在编辑器中提供类型检查和提示，运行时不会进行类型检查。
可以使用三方库来实现运行时类型检查

- typeguard：提供了一个 @typechecked 装饰器，可以直接对函数进行运行时类型检查。如果类型不符，会抛出 TypeError
- beartype：它的运行速度非常快，几乎没有运行时开销
"""


# 使用装饰器开启运行时类型检查
@typechecked
def add(a: int, b: int) -> int:
    return a + b


# print(add(1, 2))
# print(add(a=1, b=2))
# print(add(1, '2'))


@beartype
def greet_(name: str, age: int = 18) -> str:
    return f"大家好，我叫{name}，今年{age}岁"

# print(greet_('王麻子', 20))
# print(greet_("韩老魔", "三十"))
