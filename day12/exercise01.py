import random
import string

import requests


# 1. 编写一个生成六位数/字符 random_user_id 的函数
def random_user_id():
    string1 = string.ascii_letters  # 字母 a-z、A-Z
    string2 = string.digits  # 字符串 0-9
    string3 = string1 + string2
    return "".join(random.sample(string3, 6))  # 随机取 6 个字符


# print(string.digits)
# print(string.ascii_letters)
# print(random_user_id())


"""
2. 修改上一个任务。声明一个名为 user_id_gen_by_user 的函数。
它不接受任何参数，但接受两个输入。一个输入是字符的数量，另一个输入是应生成的 ID 数量
"""


def user_id_gen_by_user():
    num = int(input("请输入字符数量："))
    quantity = int(input("请输入生成数量："))
    for _ in range(quantity):
        print("".join(random.sample(string.ascii_letters + string.digits, num)))


# user_id_gen_by_user()


# 3. 编写一个名为 rgb_color_gen 的函数。它将生成 RGB 颜色（每个值范围从 0 到 255）
def rgb_color_gen():
    return f"rgb({random.randint(0, 255)},{random.randint(0, 255)},{random.randint(0, 255)})"


# print(rgb_color_gen())


# 4. 编写一个函数，它在 0-9 的范围内返回七个随机数的数组。所有数字必须是唯一的
def seven_random_numbers():
    return random.sample(range(0, 10), 7)


# print(seven_random_numbers())


# 5. 调用你的函数 shuffle_list，它接受一个列表作为参数并返回一个打乱的列表
def shuffle_list(lst):
    random.shuffle(lst)
    return lst


# print(shuffle_list([1, 2, 3, 4, 5, 6]))


response = requests.get("https://api.github.com")
print(response.status_code)
