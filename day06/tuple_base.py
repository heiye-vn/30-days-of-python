"""
元组（Tuple）是 Python 中最重要的数据类型之一，它和列表（List）非常相似，
但最大的区别就是：元组是不可变（Immutable）的
可理解为： Tuple = 不可修改的 List

有序：元组中的元素有严格的先后顺序，可以通过索引（位置）来精确提取某个元素
不可变：这是元组最重要的特征。元组一旦被创建，就不能修改、添加或删除里面的元素
异构：一个元组里可以同时包含不同类型的数据（整数、字符串、列表，甚至另一个元组）
"""

"""
===== 1. 创建元组 =====
- 使用圆括号 () 创建元组
- 使用 tuple(iterable) 构造函数创建，接受一个可迭代对象（列表、元组、集合、字典、字符串）

💡：如果是一个单元素元组，需要在元素后加逗号，否则括号会被视为运算符括号
"""
t = (1, 2, 3, (55, 66))
t = t + (4,)
# print(t)

my_tuple = (1, "Hello", 3.14, True)
# print(my_tuple)

# 可以省略小括号（这被称为“元组打包”）
another_tuple = 10, 20, 30
# print(another_tuple)

my_tuple2 = tuple({"name": "张三", "age": 20})  # 传入字典时，只保留键
# print(my_tuple2)

my_tuple3 = tuple('hello world')
# print(my_tuple3)

my_tuple4 = ('python',)  # 单元素元组必须添加逗号
# print(my_tuple4)

# 元组拼接/重复
# print((1, 2) + (3, 4))
# print((55,) + (1, 2, 3))
# print(("A",) * 10)


"""
===== 2. 访问元组元素：索引和切片 =====
- 索引（Index）：通过正整数位置编号访问元素，从左到右，从0开始，从右到左，从-1开始
- 切片（Slicing）：通过起始位置和结束位置提取子元组，语法：tuple[start:stop:step]
"""
fruits = ("apple", "banana", "cherry", "orange", "kiwi")
fruits = fruits[::-1]  # 反转元组，不会修改原元组，除非重新赋值或新的变量
# print(fruits)
# print(fruits[1:4])
# print(fruits[-2])
# print(fruits[0])

# 元组内部有可变对象时，可修改可变对象内部的内容
mixed_tuple = (1, 2, [3, 4])
mixed_tuple[2][1] = 999
# print(mixed_tuple)

# 使用 list() 可把元组转换为列表
# print(list(mixed_tuple))


"""
===== 3. 元组的解包（重）
"""
person = ("Tom", 20)
name, age = person
# print(name, age)

person1 = ("Tom", 20, "男")
# name, age = person1  # noqa 解包的值必须和元组数量一致，否则会报错

ages = (20, 22, 45, 30, 56)
first, *middle, last = ages
# print(first)
# print(middle)  # 可以使用 [ * ] 来获取剩余的元素，返回一个列表
# print(last)


"""
===== 4. 元组常用方法和函数
方法：count()、index()，用法和 list 一致
函数：len()、max()、min()、sum()、sorted()，用法和 list 一致
💡：sorted() 无论传入什么类型的可迭代对象，最终返回的都是 list

del 不可删除元组某一项，只能删除整个元组
"""
# print(sorted("hello"))
# print(sorted((1, 8, 5, 7, 3)))
# print((1, 2, 3, 2, 5).index(2))
# print((1, 2, 3, 5, 7, 2, 5, 3, 2).count(2))


"""
===== 5. 元组的使用场景 =====
"""
print("\n--- 场景1：函数返回多个值 ---")


def get_user():
    return "Alice", 25, "Engineer"  # 自动打包成元组


print(get_user())
name_, age_, job_ = get_user()
print(f"解包获取：{name_}, {age_}, {job_}")

print("\n--- 场景2：作为字典的键（列表做不到） ---")
# 常用于多维标识，例如使用 (x, y) 坐标作为键
locations = {
    (0, 0): "起点位置",
    (10, 20): "终点位置"
}
print(f"坐标(10, 20)对应的是：{locations[(10, 20)]}")

print("\n--- 场景3：保护常量数据（只读） ---")
DAYS_OF_WEEK = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
# DAYS_OF_WEEK[0] = "Monday"  # 如果尝试修改，程序会抛出 TypeError，保证了配置数据的安全
