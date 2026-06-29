from functools import wraps

"""
什么是高阶函数？

满足以下条件之一的函数称为高阶函数：
1. 函数作为参数传递给另一个函数
2. 函数作为返回值返回给调用者

函数是 “一等公民”：在 Python 中，函数可以像普通值一样被处理
"""

"""
函数赋值给变量
"""


def square(x):
    return x * x


my_func = square

# print(my_func(5))


"""
作为参数传递
"""


def apply(func, value):
    return func(value)


# print(apply(square, 5))
# print(apply(lambda x: x + 1, 20))


"""
作为返回值
"""


def get_operator(op):
    if op == "add":
        return lambda x, y: x + y
    elif op == "mul":
        return lambda x, y: x * y
    return "Invalid operator"


add_func = get_operator("add")
# print(add_func(3, 4))
# print(get_operator("reduce"))


"""
wraps 函数/装饰器的使用

wraps 是标准库 functools 模块提供的一个装饰器
作用是保留装饰函数的元数据（Metadata）、函数签名(__name__)、文档字符串(__doc__)等
"""


# ❌ 情况一：不使用 @wraps
def my_decorator(func):
    def wrapper(*args, **kwargs):
        """我是 wrapper 的文档字符串"""
        return func(*args, **kwargs)

    return wrapper


@my_decorator
def greet(name):
    """向用户问好"""
    print(f"Hello, {name}")


greet("Alice")
# 查看被装饰后的函数属性
print(greet.__name__)  # wrapper
print(greet.__doc__)  # 我是 wrapper 的文档字符串


# ✅ 情况二：使用 @wraps
def my_decorator_with_wraps(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


@my_decorator_with_wraps
def greet2(name):
    """向用户问好"""
    print(f"Hello, {name}")


print(greet2.__name__)  # greet2
print(greet2.__doc__)  # 向用户问好
