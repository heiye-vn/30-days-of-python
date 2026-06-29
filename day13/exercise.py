"""
列表推导式 & lambda 函数练习
"""

"""
1. 使用列表推导式过滤出列表中的负数和零
numbers = [-4, -3, -2, -1, 0, 2, 4, 6]
"""
numbers = [-4, -3, -2, -1, 0, 2, 4, 6]
filter_numbers = [num for num in numbers if num <= 0]
# print(filter_numbers)

"""
2. 将以下列表中的列表展平为一维列表
list_of_lists = [[[1, 2, 3]], [[4, 5, 6]], [[7, 8, 9]]]

输出:
[1, 2, 3, 4, 5, 6, 7, 8, 9]
"""
list_of_lists = [[[1, 2, 3]], [[4, 5, 6]], [[7, 8, 9]]]
flattened_list = [
    num for sublist1 in list_of_lists for sublist2 in sublist1 for num in sublist2
]
# print(flattened_list)


"""
3. 使用列表推导式创建以下元组列表
[(0, 1, 0, 0, 0, 0, 0),
(1, 1, 1, 1, 1, 1, 1),
(2, 1, 2, 4, 8, 16, 32),
(3, 1, 3, 9, 27, 81, 243),
(4, 1, 4, 16, 64, 256, 1024),
(5, 1, 5, 25, 125, 625, 3125),
(6, 1, 6, 36, 216, 1296, 7776),
(7, 1, 7, 49, 343, 2401, 16807),
(8, 1, 8, 64, 512, 4096, 32768),
(9, 1, 9, 81, 729, 6561, 59049),
(10, 1, 10, 100, 1000, 10000, 100000)]
"""
tuple_list = [(i, 1, i ** 2, i ** 3, i ** 4, i ** 5, i ** 6) for i in range(11)]
# print(tuple_list)


"""
4. 将以下列表展平成一个新列表
countries = [[('芬兰', '赫尔辛基')], [('瑞典', '斯德哥尔摩')], [('挪威', '奥斯陆')]]

输出:
[['芬兰', 'FIN', '赫尔辛基'], ['瑞典', 'SWE', '斯德哥尔摩'], ['挪威', 'NOR', '奥斯陆']]
"""
countries = [[("芬兰", "赫尔辛基")], [("瑞典", "斯德哥尔摩")], [("挪威", "奥斯陆")]]

# 定义国家缩写映射字典
# code_map = {'芬兰': 'FIN', '瑞典': 'SWE', '挪威': 'NOR'}
# 定义 lambda 函数将元组转换为指定格式的列表
# format_country = lambda x: [x[0], code_map.get(x[0], ''), x[1]]
# 结合列表推导式和 lambda 函数，推导式列表中直接写 lambda 表达式需要调用
# result = [(lambda item: [item[0], code_map.get(item[0]), item[1]])(item) for sublist in countries for item in sublist]
# print(result)
# 或者
# result_ = [format_country(item) for sublist in countries for item in sublist]
# print(result_)

"""
5. 将以下列表转换为字典列表
countries = [[('芬兰', '赫尔辛基')], [('瑞典', '斯德哥尔摩')], [('挪威', '奥斯陆')]]

输出:
[{'国家': '芬兰', '城市': '赫尔辛基'},
{'国家': '瑞典', '城市': '斯德哥尔摩'},
{'国家': '挪威', '城市': '奥斯陆'}]
"""
# format_county = lambda x: {'国家': x[0], '城市': x[1]}
# result = [format_county(item) for sublist in countries for item in sublist]
# print(result)


"""
6. 将以下列表转换为连接字符串的列表
names = [[('Alice', 'Yahoo')], [('David', 'Smith')], [('Donald', 'Trump')], [('Bill', 'Gates')]]

输出:
['Alice Yahoo', 'David Smith', 'Donald Trump', 'Bill Gates']
"""
names = [
    [("Alice", "Yahoo")],
    [("David", "Smith")],
    [("Donald", "Trump")],
    [("Bill", "Gates")],
]
result = [f"{item[0]} {item[1]}" for sublist in names for item in sublist]
# print(result)


"""
7. 编写一个 lambda 函数，可以求解线性函数的斜率或 y 截距
"""
# 方案一：定义一个多功能 lambda 函数，通过参数 'target' 控制求解目标 ('slope' 或 'intercept')
solve_linear = lambda p1, p2, target='slope': (
    (p2[1] - p1[1]) / (p2[0] - p1[0])
    if target == 'slope'
    else p1[1] - ((p2[1] - p1[1]) / (p2[0] - p1[0])) * p1[0]
)

# 方案二：定义两个职责单一的 lambda 函数，且截距函数可以复用斜率函数
calc_slope = lambda p1, p2: (p2[1] - p1[1]) / (p2[0] - p1[0])
calc_intercept = lambda p1, p2: p1[1] - calc_slope(p1, p2) * p1[0]

# 测试用例：两点 (1, 2) 和 (3, 5)
# 对应线性方程为 y = 1.5x + 0.5
point_a = (1, 2)
point_b = (3, 5)

# print("--- 方案一测试 ---")
# print(f"两点 {point_a} 和 {point_b} 的斜率为: {solve_linear(point_a, point_b, 'slope')}")
# print(f"两点 {point_a} 和 {point_b} 的 y 截距为: {solve_linear(point_a, point_b, 'intercept')}")
#
# print("\n--- 方案二测试 ---")
# print(f"两点 {point_a} 和 {point_b} 的斜率为: {calc_slope(point_a, point_b)}")
# print(f"两点 {point_a} 和 {point_b} 的 y 截距为: {calc_intercept(point_a, point_b)}")
