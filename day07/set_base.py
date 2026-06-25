"""
Python 中的 集合（Set） 是一种非常重要且高效的数据结构。
它基于数学中的“集合论”概念，具有无序性、唯一性、可变性三大核心特征

应用场景：“去重”、“判断成员是否存在”或者“数学集合运算（交集、并集、差集等）”
"""

"""
===== 1. 集合的核心特点 =====
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
===== 2. 集合的创建 =====
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
===== 3. 集合的常用操作（增、删、查）=====
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
# print(books)

# print("node" in books)  # [ in ] 成员检测，时间复杂度为 O(1)
# print("java" not in books)


"""
===== 4. 冻结集合（frozenset）=====
frozenset 是不可变的集合。它具备集合的去重和无序特性，但不能被修改（无增删方法）。
由于其不可变性，frozenset 是“可哈希的（hashable）”，因此它可以：
1. 作为字典的键（Key）
2. 作为普通集合（set）的元素
"""
# immutable_set = frozenset([1, 2, 3, 4])
# immutable_set.add(5)  # AttributeError: 'frozenset' object has no attribute 'add'
# print(f"这是一个不可变集合: {immutable_set}")


"""
===== 5. 集合的核心操作（数学运算、关系判断）=====
"""
A = {1, 2, 3, 4}
B = {3, 4, 5, 6}

# 并集：合并所有元素 [ | 或 unio() ]
# print(A | B)
# print(A.union(B))
# print(B.union(A))

# 交集：共同拥有的元素 [ & 或 intersection() ]
# print(A & B)
# print(A.intersection(B))
# print(B.intersection(A))

# 差集：一个有，一个没有的元素 [ - 或 difference() ]
# print(A - B)
# print(A.difference(B))
# print(B - A)

# 对称差集：有且仅属于其中一个集合的元素 [ ^ 或 symmetric_difference() ]，可理解为 并集 - 交集
# print(A ^ B)
# print(A.symmetric_difference(B))
# print(B ^ A)

C = {1, 2}
D = {1, 2, 3}

# 是否子集 [ <= 或 issubset() ]
# print(C <= D)
# print(D.issubset(C))

# 是否真子集（C 是 D 的子集，且两者不相等）[ < ]
# print(C < D)  # 返回 True

# 是否超集（超集是一个集合包含另一个集合）[ >= 或 issuperset() ]
# print(D >= C)
# print(D.issuperset(C))

# 是否真超集（D 是 C 的超集，且两者不相等）[ > ]
# print(D > C)  # 返回 True

# 是否不相交
# print({1, 2}.isdisjoint({3, 4}))


"""
===== 6. 集合的常见应用场景 =====
"""
# 快速去重
data = [1, 2, 2, 3, 3, 3]
unique = list(set(data))  # [1, 2, 3]（顺序不保证）

# 高效成员检查（比 list 快得多）
valid_users = {"alice", "bob", "charlie"}
if "alice" in valid_users:  # O(1) 查找
    print("已授权")

# 找两个列表的共同元素
a = [1, 2, 3, 4]
b = [3, 4, 5, 6]
common = set(a) & set(b)

# 找差异（例如新增了哪些功能）
old_features = {"login", "search"}
new_features = {"login", "search", "export", "share"}
added = new_features - old_features
# print(f"新增功能为：{added}")
