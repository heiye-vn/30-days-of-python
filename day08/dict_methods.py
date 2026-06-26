"""
字典的常用方法：

- get(key[, default])： 获取值，不存在返回默认值
- setdefault(key[, default])：获取值，不存在则插入默认值并返回
- update(other)：更新合并字典，相同键的值会被覆盖，不存在则合并
- pop(key[, default])：删除并返回指定键的值，不存在返回默认值
- popitem()：删除并返回最后插入的键值对
- keys()：返回所有键
- values()：返回所有值
- items()：返回所有键值对
- copy()：浅拷贝
- clear()：清空字典
"""

import copy

person = {"name": "Tom", "age": 20}
person.update({"age": 30, "gender": "男"})
# person.update({"city": "China"})
# person.update(city="China")
# person.update([("city", 'China')])
# print(person)

a = {"x": 1, "y": 2}
b = {"y": 100, "z": 3}
# 合并字典（ | 或 |= ）
c = a | b
# print(c)
# a |= b
# print(a)
# b |= a
# print(b)


person1 = {"name": "Tom", "hobby": ["篮球"]}
# copy() 浅拷贝
person2 = person1.copy()
# deepcopy() 深拷贝
person3 = copy.deepcopy(person1)
person2["hobby"].append("羽毛球")  # noqa
person3["hobby"].append("足球")  # noqa

# print(person1)
# print(person2)
# print(person3)

# 动态反映字典变化
d = {"a": 1, "b": 2, "c": 3}
keyList = d.keys()
d["e"] = 5
# print(keyList)  # 自动更新

# 默认字典保持插入顺序，但如果需要按键或值排序，可以使用 sorted()
scores = {"Tom": 90, "Lucy": 95, "Jack": 88}
# 按键排序
# for name in sorted(scores):
#     print(name)

# 按值排序
# for score in sorted(scores.values(), reverse=True):
#     print(score)

# lambda: 匿名函数表达式，传入 item[1]，即值给 sorted 排序
for name, score in sorted(scores.items(), key=lambda item: item[1], reverse=True):
    print(name, score)
