"""
Python 的字典是一种 可变的 (Mutable)、无序的（在 Python 3.7+ 后表现为按插入顺序排列） 键值对 (Key-Value) 集合

键 (Key) 的严格限制：必须可哈希 (Hashable)：
字典的键必须是不可变类型，
例如：字符串、数字、元组。而像列表（List）、字典（Dict）这样可变的对象，是绝对不能作为键的

为什么？
因为字典底层依赖哈希表。如果键的值改变了，它的哈希值就会变，你就再也找不到对应的 Value 了

应用场景：Web开发（Django/FastAPI）、数据分析（Pandas）、AI（LangChain、OpenAI）、爬虫、自动化脚本，
几乎都会大量使用 Dict
"""

"""
===== 1. 字典（Dictionary）的定义及创建方式 =====
字典是一种：键（key）-> 值（value）的映射关系
字典的创建方式：{}、dict()、嵌套元组/列表转换、zip()、fromkeys()
字典的特点：
- Key 唯一（后面的覆盖前面），且必须可哈希 (Hashable)
💡：用 str 作为 key 时必须用字符串，否则会被当做是变量
- Value 可重复，可以是任意类型
"""
# str、int、float、bool、tuple 可作为 key，实际场景中 str、int 最为常用
d1 = {
    "name": '张三',
    True: False,
    55: "55",
    (1, 2, 3): [1, 2, 3]
}
# print(d1)

# dict() 方式创建，关键字 + 关键字参数
d2 = dict(name='张三', age=18)
# print(d2)

# 嵌套元组/列表转化
d3 = dict([("name", '王麻子'), ("age", 25)])
# print(d3)

# 使用 zip()，返回一个 zip 对象（迭代器）
keys = ["name", "age", "gender"]
values = ["Tom", 20, "男"]
person = dict(zip(keys, values))
# print(person)

# fromkeys() 批量初始化
d4 = dict.fromkeys(["a", "b", "c"], 0)
# print(d4)
# 💡：如果默认值是可变对象，所有键会共享同一个引用！
d5 = dict.fromkeys(['x', 'y', 'z'], [])
d5['y'].extend([1, 2, 3])
# print(d5)


"""
===== 2. 字典的访问、修改、删除、遍历 =====
"""
d6 = {"name": "Alice", "age": 30}
# ❌ 直接访问：键不存在时抛出 KeyError
# print(d6["name"])
# print(d6['sex'])
# ✅ get()：键不存在时返回默认值（默认为 None）
# print(d6.get("sex"))
# print(d6.get("sex", "Not Found"))
# ✅ setdefault()：键不存在时设置默认值并返回；键存在则返回已有值
# print(d6.setdefault('name'))
# print(d6.setdefault("sex", '男'))
# print(d6)
# 使用 in 或 not in 判断 key 是否存在
# print("name" in d6)
# print("city" not in d6)

# 新增/修改
# d6["name"] = "王麻子"
# d6["city"] = "赵国"
# print(d6)

# 删除
# del d6["age"]  # del 删除指定键，不存在会报错
# val = d6.pop('city', 'None')  # 删除指定键，可设置默认值
# print(val)
# k, v = d6.popitem()  # 删除最后一个键值对
# print(k, v)
# d6.clear()  # 清空字典
# print(d6)


"""
3. 字典的遍历 =====
- 遍历键
- 遍历值
- 同时遍历键和值
"""
d7 = {"name": "Alice", "age": 30, "city": "Beijing"}
# ✅ 推荐：直接遍历键（默认是遍历键，不需要加 .keys()）
# for key in d7:
#     print(key)

# ✅ 同时获取键和值
# for key, value in d7.items():
#     print(f"{key}: {value}")

# 遍历值
# for value in d7.values():
#     print(value)

# ❌：遍历时不能直接修改字典，会抛出 RuntimeError
# for key in d7:
#     if key == 'age':
#         del d7[key]
# print(d7)

# ✅ 方法一：遍历字典键的 "副本"
# for key in list(d7.keys()):
#     if key == 'age':
#         del d7[key]
# print(d7)

# ✅ 方法二：使用字典推导式创建一个新字典（更 Pythonic）
# filtered_d7 = {k: v for k, v in d7.items() if k != "age"}
# print(filtered_d7)
# print(d7)


"""
===== x. 字典推导式（Dict Comprehension）
从一个可迭代对象快速生成字典时，推导式是首选
"""
# 将员工名字和工号列表快速组合成字典
names = ["Alice", "Bob", "Charlie", "David"]
ids = [1001, 1002, 1003]
# zip() 可以将多个可迭代对象组合成一个元组格式的迭代器对象
employee_map = {name: emp_id for name, emp_id in zip(names, ids)}
# print(employee_map)
