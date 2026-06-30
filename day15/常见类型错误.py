# import math

"""
Python 中的常见类型错误
"""
from calendar import error

# SyntaxError（语法错误）
# print "hello"
# if True
#     print("Hello") # SyntaxError: expected ':'


"""
NameError（变量未定义）
变量名拼写错误或作用域使用不当 
"""
# print(age)


"""
TypeError（类型错误）
传入参数类型不符合要求，或进行了不支持的类型运算
"""
# print(1 + "2")


"""
ValueError（值错误）
参数类型正确，但值不合法，例如字符串转整数失败
"""
# int("abc")  # "abc" 不能转换为整数
# math.sqrt(-1)  # 平方根不能是负数（实数范围）


"""
IndexError（下标越界）
访问列表、元组或字符串时索引越界
"""
# nums = [1, 2, 3]
# print(nums[5])


"""
KeyError（字典键不存在）
访问字典中不存在的键，尤其是在处理 JSON 数据时
"""
# person = {
#     "name": "Tom"
# }
# print(person["age"])


"""
AttributeError（属性错误）
对象调用了不存在的方法或属性
"""
# "abc".append(1) # 'str' object has no attribute 'append'
# nums = [1, 2]
# nums.upper() # 'list' object has no attribute 'upper'


"""
ModuleNotFoundError（模块未找到）
环境配置或依赖安装不完整导致模块无法导入
"""
# import abcdefg # No module named 'abcdefg'


# ImportError（模块导入错误）
# from math import hello # cannot import name 'hello' from 'math'


"""
FileNotFoundError（文件不存在）
读取配置文件、日志文件或上传文件时路径错误
"""
# open("hello.txt")
# from pathlib import Path
#
# path = Path("hello.txt")
# if path.exists():
#     with open(path) as f:
#         print(f.read())
# else:
#     print("文件不存在")


# ZeroDivisionError（除零错误）
# result = 10 / 0  # division by zero，被除数不能为零


# OverflowError（数值溢出）
# math.exp(1000)


# RecursionError（递归过深）
# def test():
#     test()
#
#
# test() # maximum recursion depth exceeded


# RuntimeError（运行时错误）
# d = {"a": 1}
#
# for k in d:
#     d["b"] = 2  # dictionary changed size during iteration，字典遍历时不允许修改


"""
NotImplementedError（未实现错误）
常用于开发框架或定义接口时，提醒子类必须实现某个方法。
"""


class Animal:
    def speak(self):
        raise NotImplementedError("子类必须实现 speak 方法")


class Dog(Animal):
    pass


# Dog().speak() # NotImplementedError: 子类必须实现 speak 方法


"""
AssertionError（断言失败）
断言用于开发和调试阶段验证程序状态
"""
age = -1

# assert age >= 0, "年龄不能为负数" # AssertionError: 年龄不能为负数


"""
自定义异常（Custom Exception）
在实际项目中，我们经常定义自己的异常类型，使错误更具业务语义
"""


class BalanceNotEnoughError(Exception):
    """余额不足异常"""
    pass


def withdraw(balance, amount):
    if amount > balance:
        raise BalanceNotEnoughError("余额不足")
    return balance - amount


try:
    withdraw(100, 200)
except BalanceNotEnoughError as e:
    print(e)
