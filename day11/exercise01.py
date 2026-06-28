# 1. 声明一个函数 add_two_numbers。它接受两个参数并返回它们的和
def add_two_numbers(a, b):
    return a + b


# print(add_two_numbers(10, 20))

# 2. 圆的面积计算公式为：area = π x r x r。编写一个函数计算 area_of_circle
PI = 3.141592654


def area_of_circle(r):
    return PI * (r ** 2)


# print(f"{area_of_circle(14):.2f}")


"""
3. 编写一个名为 add_all_nums 的函数，它接受不定数量的参数并求和所有参数。
检查所有列表项是否都是数字类型。如果不是，给予合理的反馈
"""


def add_all_nums(*args):
    print(args)
    total_num = 0
    for num in args:
        if type(num) != int and type(num) != float:
            return "All arguments must be numbers"
        total_num += num
    return total_num


# print(add_all_nums(1, 2, 3, 4, 5, 6, 7, 8, 9, 10))
# print(add_all_nums(1, 2, 3, 4, 5, 6, 7, 8, 9, "10"))

"""
4. 摄氏温度（°C）可以使用以下公式转换为华氏温度（°F）：°F = (°C x 9/5) + 32。
编写一个函数将 °C 转换为 °F，convert_celsius_to_fahrenheit
"""


def convert_celsius_to_fahrenheit(celsius):
    # 仅负责纯粹的温度转换逻辑
    return (celsius * 9 / 5) + 32


# 外部处理输入和打印
# celsius_input = input("请输入摄氏温度（°C）：")
# try
#     c_val = float(celsius_input)
#     f_val = convert_celsius_to_fahrenheit(c_val)
#     print(f"摄氏温度（°C）：{c_val} 对应的华氏温度（°F）：{f_val}")
# except ValueError:
#     print("请输入合法的数字！")

"""
5. 编写一个名为 check_season 的函数，它接受一个月份作为参数并返回季节：秋季、冬季、春季或夏季。
"""


def check_season(month):
    # 将传入的参数先转换为整数（防御性编程）
    try:
        m = int(month)
    except ValueError:
        return "请输入正确的月份数字"

    # 使用 Python 的链式比较简化逻辑
    if 3 <= m <= 5:
        return "春季"
    elif 6 <= m <= 8:
        return "夏季"
    elif 9 <= m <= 11:
        return "秋季"
    elif m == 12 or m == 1 or m == 2:
        return "冬季"
    else:
        return "请输入 1 到 12 之间的月份"


# input_month = input("请输入月份：")
# print(check_season(input_month))

# 6. 编写一个名为 calculate_slope 的函数，它返回线性方程的斜率
def calculate_slope(x1, y1, x2, y2):
    if x2 - x1 == 0:
        return "斜率不存在（垂直于 x 轴）"
    return (y2 - y1) / (x2 - x1)


# print(calculate_slope(7, 2, 4, 3))

"""
7. 二次方程按以下公式计算：ax² + bx + c = 0。编写一个函数计算二次方程的解集，solve_quadratic_eqn
"""


def solve_quadratic_eqn(a, b, c):
    if a == 0:
        if b != 0:
            return -c / b  # 退化为一次方程的解
        else:
            return "无解"

    delta = b ** 2 - 4 * a * c
    if delta < 0:
        return "无解"
    elif delta == 0:
        return -b / (2 * a)
    else:
        return (-b + delta ** 0.5) / (2 * a), (-b - delta ** 0.5) / (2 * a)


# print(solve_quadratic_eqn(1, 2, 1))


# 8. 声明一个名为 print_list 的函数。它接受一个列表作为参数，并打印列表的每个元素
def print_list(lst):
    for item in lst:
        print(item)


# print_list([1, 2, 3, 4, 5])


# 9. 声明一个名为 reverse_list 的函数。它接受一个数组作为参数，并返回数组的反转（使用循环）
def reverse_list(lst):
    reversed_list = []
    # 使用 range 从最后一个索引递减到 0
    for i in range(len(lst) - 1, -1, -1):
        reversed_list.append(lst[i])
    return reversed_list


def reverse_list1(lst):
    reversed_list = []
    for item in lst:
        reversed_list.insert(0, item)
    return reversed_list


# print(reverse_list([1, 2, 3, 4, 5]))
# print(reverse_list1(["A", "B", "C"]))


# 10. 声明一个名为 capitalize_list_items 的函数。它接受一个列表作为参数，并返回一个大写的列表项
def capitalize_list_items(lst):
    # return [item.capitalize() for item in lst]
    # return [item.upper() for item in lst]
    # 仅对字符串类型的元素进行转换，非字符串元素保持原样
    return [item.capitalize() if isinstance(item, str) else item for item in lst]


# print(capitalize_list_items(["hello", "world", "python"]))
# print(capitalize_list_items([1, "hello", "world", "python", True]))


# 11. 声明一个名为 add_item 的函数。它接受一个列表和一个项作为参数。它返回在末尾添加项的列表
def add_item(lst, item):
    return lst + [item]


# food_staff = ['Potato', 'Tomato', 'Mango', 'Milk']
# print(add_item(food_staff, 'Meat'))
# numbers = [2, 3, 7, 9]
# print(add_item(numbers, 5))


# 12. 声明一个名为 remove_item 的函数。它接受一个列表和一个项作为参数。它返回移除该项后的列表
def remove_item(lst, item):
    return [it for it in lst if it != item]


# food_staff = ['Potato', 'Tomato', 'Mango', 'Milk']
# print(remove_item(food_staff, 'Mango'))
# numbers = [2, 3, 7, 9]
# print(remove_item(numbers, 3))


# 13. 声明一个名为 sum_of_numbers 的函数。它接受一个数字参数并将范围内的所有数字相加
def sum_of_numbers(n):
    # n 如果很大时用 range 计算范围会消耗计算资源
    # return sum(range(1, n + 1))
    # 使用等差数列求和方式计算
    return n * (n + 1) / 2


# print(sum_of_numbers(10))
# print(sum_of_numbers(100))
# print(sum_of_numbers(3))


# 14. 声明一个名为 sum_of_odds 的函数。它接受一个数字参数并将范围内的所有奇数相加
def sum_of_odds(n):
    return sum(range(1, n + 1, 2))


# print(sum_of_odds(10))


# 15. 声明一个名为 sum_of_even 的函数。它接受一个数字参数并将范围内的所有偶数相加
def sum_of_even(n):
    return sum(range(2, n + 1, 2))

# print(sum_of_even(5))
