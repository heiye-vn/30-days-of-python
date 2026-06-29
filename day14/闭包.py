"""
闭包：允许嵌套函数访问外部封闭函数的作用域。

在 Python 中，闭包是通过在另一个封装函数内部嵌套函数，然后返回内部函数来创建的
"""

from day14.常用高阶函数 import double

"""
简单来说，闭包是这样一种现象：

当一个内部函数引用了它外部函数的变量，并且这个内部函数被返回到外部使用时，即使外部函数已经执行完毕返回了，
内部函数依然能「记住」并访问那些被引用的变量

这种「带着外部环境一起走」的函数，就是闭包。
"""


# 计数器
def make_counter():
    count = 0  # 外部函数的局部变量

    def counter():
        nonlocal count  # 引用外部变量，使用 nonlocal 声明，否则会报错
        count += 1
        return count

    return counter  # 返回内部函数


# count 变量被绑定到 counter 函数上，并没有销毁
c1 = make_counter()
# print(c1)  # noqa
# print(c1())
# print(c1())
# print(c1())


"""
闭包是如何「记住」变量的？

Python 在内部用 __closure__ 的属性存储被引用的变量

修改闭包变量时，需要使用 nonlocal 关键字声明外部变量，否则会报错
"""


def outer():
    x = 10
    y = 20

    def inner():
        return x + y

    return inner


f = outer()
# print(f.__closure__)  # noqa
# print(f.__closure__[0].cell_contents)  # noqa 10
# print(f.__closure__[1].cell_contents)  # noqa 20


"""
闭包的常见用途
"""


# 1. 状态保持
def make_multiplier(factor):
    def multiply(n):
        return n * factor

    return multiply


result_double = make_multiplier(2)
result_triple = make_multiplier(3)
# print(result_double(5))
# print(result_triple(5))


# 2. 装饰器
def log_call(func):
    def wrapper(*args, **kwargs):
        print(f"调用 {func.__name__}")
        result = func(*args, **kwargs)
        print(f"{func.__name__} 执行完毕")
        return result

    return wrapper


@log_call
def greet(name):
    print(f"你好 {name}")


# greet("小明")


# ✖ 循环中闭包的错误示例
funcs = []
# for i in range(3):
#
#     def f():
#         return i
#
#     funcs.append(f)

# 由于闭包持有的是变量本身（cell 引用），而不是创建时的值，因此所有闭包都会引用同一个变量
# print(funcs)
# print(funcs[0]())  # 2
# print(funcs[1]())  # 2
# print(funcs[2]())  # 2


# 解决方法一：利用默认参数立即求值
# for i in range(3):
#
#     def f(val=i):
#         return val
#
#     funcs.append(f)

# print(funcs[0]())  # 0
# print(funcs[1]())  # 1
# print(funcs[2]())  # 2


# 使用工厂函数
def make_f(val_i):
    def f_():
        return val_i

    return f_


for i in range(3):
    funcs.append(make_f(i))

print(funcs[0]())  # 0
print(funcs[1]())  # 1
print(funcs[2]())  # 2
