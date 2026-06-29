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
    elif op == 'mul':
        return lambda x, y: x * y
    return "Invalid operator"


add_func = get_operator("add")
print(add_func(3, 4))
# print(get_operator("reduce"))
