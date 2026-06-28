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
