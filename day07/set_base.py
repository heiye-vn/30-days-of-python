"""
Python 中的 集合（Set） 是一种非常重要且高效的数据结构。
它基于数学中的“集合论”概念，具有无序性、唯一性、可变性三大核心特征

应用场景：“去重”、“判断成员是否存在”或者“数学集合运算（交集、并集、差集等）”
"""

"""
===== 1. 集合的核心特点
- 无序性（Unordered）：集合中的元素没有固定的顺序，因此不能通过索引（比如 set[0]）来访问它
- 唯一性（Unique）：集合中不允许有重复的元素。如果存在重复的元素，它会自动过滤掉
- 可变性（Mutable）：集合是可变的，可以添加或删除元素
- 不可变元素（Immutable）：集合中的元素必须是不可变的，比如数字、字符串、元组等，不能包含可变对象（比如列表、字典、集合）
"""

set_1 = {3, 1, 5, 2}
# print(set_2)

# set_2 = {"apple", "banana", "cherry", [1, 2]} # noqa 集合的元素不能包含可变对象，会报错
# print(set_3)

set_3 = {"apple", "banana", "cherry"}  # 集合元素是无序的，每次运行结果可能不同
# print(set_4)


"""
===== 2. 集合的创建
创建集合主要有两种方法：使用花括号 {} 或 set() 函数
set() 方法可以接受一个可迭代对象作为参数，比如列表、元组、字符串等，存在重复元素会自动过滤

💡：创建空集合时，必须使用 set()。如果用 empty_set = {}，Python 会认为创建的是一个空字典（Dict）
"""
empty_set = set()
# print(type(empty_set))

# print(set('hello'))

my_list = [1, 2, 2, 3, "Apple", "Apple"]
unique_set = set(my_list)
# print(unique_set)


"""
===== 3. 集合的常用操作（增、删、查）
"""

"""
添加元素：
- add() - 添加单个元素；
- update() - 添加多个元素，接受可迭代对象作为参数
"""
fruits = {"apple", "banana"}
fruits.add("cherry")
# print(fruits)
fruits.update(["orange", "grape"])
# print(fruits)
fruits.update({'react', 'vue', 'angular'})
# print(fruits)
fruits.update((1, 2, 1, 3))  # noqa
# print(fruits)
fruits.update('hello')
# print(fruits)
fruits.update({"name": "张三", "age": 20})  # 添加字典时会把键添加到集合中
# print(fruits)

"""
删除元素：
- remove()：删除指定元素，元素不存在会报错
- discard()：删除指定元素，元素不存在不会报错（更安全）
- pop()：随机删除并返回一个元素（集合无序，无法控制删除哪个元素）
- clear()：清空集合
"""
numbers = {10, 20, 30, 40}
# numbers.remove(10)
# numbers.discard(40)
# print(numbers)
books = {'vue', 'react', 'angular', 'node'}
# del_el = books.pop()
# print(del_el)

# books.clear()
print(books)

print("node" in books)  # [ in ] 成员检测，时间复杂度为 O(1)
print("java" not in books)
