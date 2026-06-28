# 1. 声明一个名为 evens_and_odds 的函数。它接受一个正整数作为参数并计算该数内偶数和奇数的数量
def evens_and_odds(n):
    count = {"even": 0, "odd": 0}
    for i in range(1, n + 1):
        if i % 2 == 0:
            count["even"] += 1
        else:
            count["odd"] += 1
    return count["even"], count["odd"]


def evens_and_odds_(n):
    # even_count = len(range(2, n + 1, 2))
    # odd_count = len(range(1, n + 1, 2))

    even_count = n // 2
    odd_count = (n + 1) // 2

    return even_count, odd_count


# result = evens_and_odds_(11)
# print(f"偶数数量：{result[0]}，奇数数量：{result[1]}")


"""
2. 调用你的函数 factorial，它接受一个整数作为参数并返回该数的阶乘
阶乘：n!=n×(n−1)×(n−2)×...×2×1
利用递归实现
"""


def factorial(n):
    if n == 0 or n == 1:
        return 1
    else:
        return n * factorial(n - 1)


# print(factorial(5))


# 3. 编写一个名为 is_prime 的函数，检查一个数是否是质数
def is_prime(n):
    if n <= 1:
        return False
    # 只需要检查到 n 的平方根即可
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True


# print(is_prime(91))


# 4.编写一个函数检查列表中的所有项是否都是唯一的
def is_only(lst):
    to_set_data = set(lst)
    return len(lst) == len(to_set_data)


# print(is_only([1, 2, 3, 4, 5, 2, 8, 9]))


# 5. 编写一个函数检查列表中的所有项是否都是相同的数据类型
def is_same_type(lst):
    if not lst:
        return True  # 空列表默认返回 True

    first_type = type(lst[0])
    for i in lst:
        if type(i) is not first_type:
            return False
    return True

    # 或者使用推导式（更简洁）
    # return len(set(type(i) for i in lst)) <= 1


# print(is_same_type([1, 2, 3, 4, 5, "hello"]))


# 6. 编写一个函数检查提供的变量是否是一个有效的 python 变量
def is_valid_variable_name(var_name):
    if not var_name[0].isalpha() and var_name[0] != "_":
        return False
    for char in var_name:
        if not (char.isalnum() or char == "_"):
            return False
    return True


# print(is_valid_variable_name("my_variable"))
# print(is_valid_variable_name("123variable"))
# print(is_valid_variable_name("variable1"))
# print(is_valid_variable_name("variable-name"))
