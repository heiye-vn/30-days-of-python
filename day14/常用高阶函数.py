"""
Python 常用高阶函数有：
map、filter、functools.reduce、sorted、functools.partial、装饰器、
"""

from functools import reduce, partial

"""
1. map(func, iterable): 映射，第一个参数为函数，第二及后续参数为可迭代对象
对序列中的每个元素应用函数，返回一个迭代器对象
"""
nums = [1, 2, 3, 4, 5]


def double(x):
    return x * 2


result = list(map(double, nums))
# print(result)

# 或者结合 lambda 表达式
result_ = list(map(lambda x: x * 2, nums))
# print(result_)

# 多个序列
list1 = [1, 2, 3]
list2 = [10, 20, 30]
result3 = list(map(lambda x, y: x + y, list1, list2))
# print(result3)


"""
2.filter(func, iterable): 过滤
第一个参数为过滤规则函数或 None，如果传 None，保留非 False 值
第二个参数为可迭代对象，且只能传一个
保留序列中使用函数返回 True 的元素
"""
nums2 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# 过滤出偶数
evens = list(filter(lambda x: x % 2 == 0, nums2))
# print(evens)

# 过滤出大于 5 的数
large_nums = list(filter(lambda x: x > 5, nums2))
# print(large_nums)

# 过滤掉空字符串
words = ["hello", "", "world", "", "python"]
non_empty = list(filter(lambda s: s, words))
# print(non_empty)
non_empty2 = list(filter(None, words))  # 保留非 False 值
# print(non_empty2)


"""
3. reduce((function, iterable[, initializer]): 累积
参数1：累积计算函数，必须接收 2 个参数的函数，参数1为累积值，参数2为当前元素
参数2：可迭代对象，只能传 1 个
参数3：初始值，可选参数
对序列进行累积操作，需要 functools
"""
# 求和
total = reduce(lambda x, y: x + y, nums)
# print(total)

# 求积
product = reduce(lambda x, y: x * y, nums)
# print(product)

# 找最大值
max_val = reduce(lambda a, b: max(a, b), nums)
# print(max_val)

# 带初始值
total_with_init = reduce(lambda x, y: x + y, nums, 100)
# print(total_with_init)


"""
4. partial(): “固定”一个函数的某些参数，从而生成一个参数更少的新函数，类似函数加工工厂
- 接收一个函数作为参数（它的第一个参数就是要被包装的目标函数）。
- 返回一个可调用的新对象（新函数）

例：
Python 的内置函数 int(x, base=10) 可以把字符串转换成整数，其中 base 代表进制（默认是十进制）。
如果经常需要转换二进制字符串，每次都写 int(x, base=2) 会很麻烦。这时就可以用 partial 来固定 base 参数
"""
# 传入 int 函数，并固定 base 参数为 2
binary_to_int = partial(int, base=2)


# print(type(binary_to_int))
# print(isinstance(binary_to_int, partial))
# print(binary_to_int("1000"))

def test_func(x, y):
    return x + y


# 包装自定义函数
new_func = partial(test_func, y=2)
# print(new_func(3))

"""
5. sorted(iterable, *, key=None, reverse=False): 排序
💡：* 号后面的参数必须显示地写出参数名，即 key=value 形式
iterable：可迭代对象
key：命名参数，排序规则，可选，类型为 Callable（接收一个参数并返回一个值的函数/方法/lambda）
reverse：命名参数，是否降序，可选
返回一个新的排序后的列表
"""
# 按绝对值排序
nums3 = [-5, 3, -1, 4, -2]
sorted_by_abs = sorted(nums3, key=abs, reverse=True)
# print(sorted_by_abs)

# 按字符串长度排序
words = ["python", "java", "c", "javascript"]
sorted_by_len = sorted(words, key=len)
# print(sorted_by_len)

# 按字典的某个键排序
students = [
    {'name': '小明', 'score': 85},
    {'name': '小红', 'score': 92},
    {'name': '小华', 'score': 78},
]
# 按分数排序
sorted_by_score = sorted(students, key=lambda s: s['score'], reverse=True)
# print(sorted_by_score)
# print([s['name'] for s in sorted_by_score])

# 多条件排序，先按分数降序，分数相同按名字升序
students_ = [
    {'name': '小明', 'score': 85},
    {'name': '小红', 'score': 92},
    {'name': '小华', 'score': 85},
]
sorted_students = sorted(students_, key=lambda s: (-s['score'], s['name']))
# print(sorted_students)


"""
6. zip(*iterables, strict=False): 拉链函数，打包多个可迭代对象
*iterables：可迭代对象，可以传多个
strict：命名参数，是否严格模式，可选，默认为 False，即以最短的可迭代对象为准，如果设置为 True，则要求所有可迭代对象长度相同

将多个序列对应位置的元素打包成元组
—— 非高阶函数
"""
names = ["小明", "小红", "小华"]
scores = [85, 92, 78]

# 配对
pairs = list(zip(names, scores))
# print(pairs)

# 解包
names2, scores2 = zip(*pairs)
# print(list(names2))
# print(scores2)

# 配合 dict 使用
score_dict = dict(zip(names, scores))
# print(score_dict)

# 长度不一致时，以最短为真, strict=True 则严格要求长度一致，否则报错
list1 = [1, 2, 3, 4]
list2 = ["a", "b"]
# print(list(zip(list1, list2, strict=True)))


"""
7. enumerate(iterable, start=0): 用于在遍历一个可迭代对象时，同时获取“当前循环的索引（计数器）”和“元素值”。
 —— 非高阶函数
"""
fruits = ["苹果", "香蕉", "橘子"]

# 默认生成的索引（非原列表索引）从 0 开始
# 1. 默认从 0 开始计数
# for index, fruit in enumerate(fruits):
#     print(f"索引 {index}: {fruit}")

# 2. 自定义从 1 开始计数
# for num, fruit in enumerate(fruits, start=1):
#     print(f"第 {num} 个水果是: {fruit}")


"""
8. 逻辑判断函数：any、all —— 非高阶函数
any(iterable): 存在即为真
all(iterable): 全真才为真，如果可迭代对象长度为空，则返回 True
"""
# any：只要有一个为 True 就返回 True
# print(any([0, 0, 1]))
# print(any([0, 0, 0]))
# print(any([]))
# print(any("hello"))

# all：全部为 True 才返回 True
# print(all([1, 1, 1]))
# print(all([1, 0, 1]))
# print(all([]))
# print(all({}))
# print(all(set()))
# print(all(""))

# 配合生成器表达式
nums4 = [2, 4, 6, 8, 10]
# print(all(n % 2 == 0 for n in nums4))  # 列表所有值执行 n % 2 == 0 都为 True
# print(any(n > 5 for n in nums4))
