"""
展开（Spreading）

使用 *（针对可迭代对象）和 **（针对字典）将容器中的元素 “铺开”。

展开和解包在语法上相同，单使用场景有所不同
"""

"""
* 展开可迭代对象
"""


# 函数调用时展开
def add(a, b, c):
    return a + b + c


numbers = [1, 2, 3]
# print(add(*numbers))


# 展开元组
coords = (10, 20)
# print(add(30, *coords))


# 展开生成器
# print(add(*range(1, 4)))


# 合并列表
list1 = [1, 2, 3]
list2 = [4, 5, 6]
list3 = [7, 8, 9]

merged = [*list1, *list2, *list3]
# print(merged)


# 在合并时添加额外元素
extended = [0, *list1, *list2, 99]
# print(extended)


# 合并集合
set1 = {1, 2, 3}
set2 = {3, 4, 5}
merged_set = {*set1, *set2}
# print(merged_set)


# 字符串展开为字符列表
chars = [*"Hello"]
# print(chars)


"""
** 展开字典
"""
# 合并字典
defaults = {"theme": "light", "language": "zh-CN", "font_size": 14}
user_prefs = {"theme": "dark", "font_size": 16}

# 方式一：使用 | 并集运算符
# final_config = defaults | user_prefs
# print(final_config)

# 方式二：使用 ** 展开，会自动覆盖重复的键
# final_config = {**defaults, **user_prefs}
# print(final_config)


# 函数调用时展开字典
def create_user(name, age, email, role="user"):
    return {"name": name, "age": age, "email": email, "role": role}


base_info = {"name": "Alice", "age": 30}
contact_info = {"email": "alice@example.com"}
extra = {"role": "admin"}

# 展开多个字典 + 额外参数
user = create_user(**base_info, **contact_info, **extra)
print(user)
