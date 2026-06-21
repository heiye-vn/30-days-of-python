# 四种基本数据类型（整数、浮点数、字符串、布尔）、复杂数据类型（列表、元组、字典、集合）

# 整数（int）
x = 10
y = -5
z = 1_000_000
# print(z)

# 浮点数（float）
a = 3.14
b = -2.0
c = 3.14_15_92
# print(c)

# 复数（complex）
d = 3 + 4j
# print(d)
e = complex(3, 4)
# print(e)

# 布尔值（bool），实际上是 int 的子类（注：T 和 F 必须大写）
flag_true = True # 等于 1
# print(flag_true == 1)
flag_false = False # 等于 0
# print(flag_false == 0)

# 字符串（单/双引号，多行用 """ ），注释同样，# 为单行注释，""" 为多行注释
str1 = "hello world"
str2 = """第一行文本
第二行文本
第三行文本
"""
print(str2)

# 列表（list）：列表是一个有序地集合，可以存储不同类型的数据。类似于 JavaScript 中的数组
list1 = [0, 1, 2, 3, 4, 5] # 所有都是相同数据类型 - 数字列表
list2 = ['Banana', 'Orange', 'Mango', 'Avocado'] # 所有都是相同数据类型 - 字符串列表（水果）
list3 = ['Finland','Estonia', 'Sweden','Norway'] # 所有都是相同数据类型 - 字符串列表（国家）
list4 = ['Banana', 10, False, 9.81] # 列表中的不同数据类型 - 字符串、整数、布尔值和浮点数

# 字典（dict）：字典对象是以键值对格式存储的无序集合
dict1 = {
'first_name':'As beneath',
'last_name':'Yetta',
'country':'Finland',
'age':250,
'is_married':True,
'skills':['JS', 'React', 'Node', 'Python']
}

# 元组（enum）：元组是一个有序地集合，类似于列表，但元组一旦创建就不能修改。它们是不可变的
enum1 = ('As beneath', 'Pawel', 'Brook', 'Abraham', 'Lidiya') # 名字
# print(enum1)
# enum1[0] = "王麻子"
# enum1.append("王麻子")
print(enum1)

# 集合（set）：集合是类似于列表和元组的集合数据类型。与列表和元组不同，集合不是一个有序地集合。就像在数学中一样，Python 中的集合只存储唯一的项目
set1 = {1, 2, 3, 4, 5, 6, 6}
print(set1) #  {1, 2, 3, 4, 5, 6}，自动去重


# 数据类型检查（type）
print(f"set1 的类型是: {type(set1)}")
print(f"list1 的类型是: {type(list1)}")
print(f"dict1 的类型是: {type(dict1)}")
print(f"enum1 的类型是: {type(enum1)}")


