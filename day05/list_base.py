"""
Python 的 List（列表） 是最常用、最灵活的数据结构。可以理解为 JavaScript 中的 Array，但功能更强大。
特点：有序、可变（可以随时添加或修改）、可存储任意类型数据、允许存在重复元素
"""

"""
===== 1. 列表的创建 =====
方式一：使用方括号 [] 创建
方式二：使用 list() 构造函数创建
"""
# 空列表
# print([])
# print(list())

"""
补充：Python 创建指定长度列表的方式
注意：不能像 JS 那样使用 list(5)，因为 list() 只能接收可迭代对象。
推荐做法：使用乘法创建长度为 5 的列表，输出 [None, None, None, None, None]，必须带默认值
"""
# print([0] * 5)
# print(list(range(5)))

mixed_list = [1, "hello", 3.14, True, [1, 2, 3]]  # 混合类型列表
# print(mixed_list)
# print(len(mixed_list))  # 使用 len() 函数获取列表长度


"""
===== 2. 索引与切片 =====
列表是有序的，每个元素都有一个位置编号，称为索引 (Index)。
正向索引（从左到右）从 0 开始，反向索引（从右到左）从 -1 开始

切片（Slicing）允许一次性提取列表中的一部分，语法：list[start:stop:step]
起始索引：[start, end)

当步长(step)为负数时，切片从右向左进行，此时 start 可以且应该大于 stop，否则会返回空列表
"""
fruits = ["apple", "banana", "cherry", "date", "elderberry"]
nums = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
# print(fruits[0])
# print(fruits[-2])
# print(fruits[2:4])
# print(fruits[::2])
# print(fruits[::-1])  # 反转列表
# print(nums[2:8:-2])


"""
===== 3. list 的增删改查及常用方法 =====
新增：
- append(x)：在列表末尾添加，x 可以是任意类型，返回 None
- extend(iterable)：在列表末尾添加可迭代对象的元素，类似 js 中的 concat()，返回 None
- insert(i, x)：在指定位置插入元素，返回 None

删除：
- remove(x)：删除列表中第一个值为 x 的元素，返回 None
- pop([i])：删除并返回列表中索引为 i 的元素，如果不指定索引，则删除并返回最后一个元素
- clear()：删除列表中所有元素，返回 None
- del：删除特定索引的元素，或者直接删除整个列表变量

修改：
- 通过索引修改元素

查询及其他方法：
- index(x)：返回列表中第一个值为 x 的元素的索引，如果不存在则报错
- count(x)：返回元素 x 在列表中出现的次数
- sort()：对列表进行原地排序（默认升序）。如果是字母则按字母表顺序，传入 reverse=True 为降序
- reverse()：原地反转列表中的元素顺序
- copy()：返回列表的浅拷贝
"""

# ===== 添加 =====
basket = ['banana', 'apple', 'orange', 'apple']  # noqa
basket.append([1, 2])  # noqa 在列表末尾添加一个元素 [1, 2]，整体添加
basket.append({"name": '张三'})  # noqa
basket.append({'react', 'vue', 'angular'})  # noqa
# print(basket)
basket.extend([7, 8])  # noqa 在列表末尾添加可迭代对象元素，展开添加
# print(basket)
basket.insert(1, (1, 2))  # noqa
# print(basket)

# ===== 删除 =====
# basket.remove("apple")
# print(basket)
# print(basket.pop(1))
# print(basket)
# basket.clear()
# print(basket)
# del basket[6]
# print(basket)
# del basket
# print(basket)  # noqa NameError: name 'basket' is not defined

# ===== 修改、查询 =====
# basket[0] = "grape"
# print(basket)
# print(basket.count('apple'))
# print(basket.count((1, 2)))  # noqa
# print(basket.index('apple'))

# ===== 排序、反转 =====
# basket.reverse()
# print(basket)
# basket.sort()  # 注意：这里会报错 TypeError。因为前面给 basket 添加了不同类型的数据，Python 无法对包含字符串、数字、字典等混合类型的列表进行大小比较排序。
# print(basket)

# 演示正常的排序（元素必须是可相互比较的类型，通常是全数字或全字符串）：
num_list = [3, 1, 4, 1, 5, 9, 2, 6]
# num_list.sort()
# print(num_list)
# num_list.sort(reverse=True)
# print(num_list)

# 使用内置函数 sorted 对 num_list 进行排序，不会修改原列表，返回新的排序结果
new_sorted_list = sorted(num_list, reverse=True)
# print(new_sorted_list)
# print(num_list)


"""
===== 4. 深浅拷贝 =====
"""
a = [1, 2, 3, [44, 55]]
# b = a
# print(a == b)
# a 和 b 的内存地址相同
# print(id(a))
# print(id(b))
# a[1] = 5
# print(b)  # a 和 b 指向同一个对象，因此 b 也会被修改

# ===== 浅拷贝 =====
c = a.copy()
a.append(999)
# print(f"列表c：{c}")
d = a[::]
d[0] = 55
a.append(777)
# print(f"列表a：{a}")
# print(f"列表d：{d}")
a[3][1] = 66  # noqa 修改嵌套列表中的元素
# print(f"列表a：{a}")
# print(f"列表d：{d}")
# print(f"列表c：{c}")
# print(id(a[3]))
# print(id(c[3]))
# print(id(d[3]))  # a、c、c 三个列表的深层列表地址还是相同

# ===== 深拷贝 =====
# 浅拷贝只拷贝第一层，如果需要连同嵌套的可变对象一起完全独立拷贝，需要用到 copy 模块的 deepcopy
import copy

e = copy.deepcopy(a)
a[3][0] = 888  # noqa 修改原始列表 a 的嵌套列表元素
# print("\n--- 深拷贝测试 ---")
# print(f"修改 a 后，列表a：{a}")
# print(f"修改 a 后，列表e (深拷贝)：{e}")  # 列表 e 里的嵌套列表完全不受影响
# print(id(a[3]))
# print(id(e[3]))


"""
===== 5. 列表推导式（List Comprehension）=====
Python 中极其强大且优雅的特性，用于根据已有的序列快速创建新列表，代码简洁高效
💡：列表推导式比等价的 for + append 快 20-30%，因为底层做了 C 级别优化
"""
# 基本形式: [表达式 for 变量 in 可迭代]
squares = [i ** 2 for i in range(10)]
# print(squares)

# 带条件过滤
even_squares = [i ** 2 for i in range(10) if i % 2 == 0]
# print(even_squares)

# 带 if-else（注意位置不同！）
labels = ["event" if i % 2 == 0 else "odd" for i in range(5)]
# print(labels)

# 嵌套循环 → 展平二维列表
# 循环从外到内 for row in matrix -> for num in row
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
flat = [num for row in matrix for num in row]
print(flat)

# 传统写法
flat_ = []
for row in matrix:  # 第一层：遍历每一行
    for num in row:  # 第二层：遍历行中的每个元素
        flat_.append(num)
print(flat_)
