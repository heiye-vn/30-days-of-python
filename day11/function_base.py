"""
函数（Function）
"""

"""
===== 1. 函数的定义与调用 =====
在 Python 中，使用 def 关键字来定义函数
"""


def greet():
    """这是一个向人打招呼的函数"""
    print("Hello！欢迎学习 Python 函数！")


# greet()
# print(greet.__doc__)


"""
===== 2. 函数的参数（重点）=====
"""


# 1. 位置参数: 调用函数时，根据参数定义的顺序依次传入值。数量和顺序必须一致
def power(x, n):
    return x**n


# print(power(2, 3))
# print(power(3, 2))


# 2. 关键字参数: 调用函数时，通过 参数名 = 值 的形式传递。这样可以不按顺序传递参数
def describe_pet(pet_name, animal_type):
    print(f"我有一只 {animal_type}，它的名字叫 {pet_name}。")


# 顺序乱了也没关系，因为指定了参数名
# describe_pet(animal_type="猫咪", pet_name="小白")
# describe_pet("大黄", "狗狗")  # 如果使用位置参数，则实参的顺序必须和形参一致


# 3. 默认参数: 在定义函数时，可以为参数指定默认值。如果调用时没有传这个参数，就使用默认值
# 注：默认参数必须在位置参数的后面
def enroll(name, gender, city="北京"):
    print(f"姓名: {name}, 性别: {gender}, 城市: {city}")


# enroll("张三", "男")
# enroll("李四", "女", "上海")


# 4. 可变参数（位置可变参数 / 关键字可变参数）
def total_score(name, *args, **kwargs):
    print(f"学生: {name}")
    print(f"各科分数 (元组): {args}")
    print(f"其他信息 (字典): {kwargs}")


# total_score("小明", 90, 85, 95, 班级="一班", 老师="王老师")


"""
===== 3. 函数的返回值（return）=====
"""


def get_max_and_min(numbers):
    if not numbers:
        return None  # 空列表直接返回 None
    return max(numbers), min(numbers)  # 返回多个值


res = get_max_and_min([12, 5, 23, 89, 3])
# print(res)

# 也可以用多个变量直接解包接收
highest, lowest = get_max_and_min([12, 5, 23, 89, 3])
# print(highest)


"""
===== 4. 变量的作用域 =====
使用 global 关键字可以修改全局变量
"""
count = 10  # 全局变量


def modify_count():
    global count  # 声明我们要修改全局变量 count
    count = 20
    local_var = 5  # 局部变量
    print(local_var)  # 只能函数内部访问


# modify_count()
# print(count)  # 输出 20 (已被修改)
# print(local_var)  # 报错！函数外部无法访问局部变量


x = "global"  # G


def outer():
    x = "enclosing"  # E
    print(x)

    def inner():
        x = "local"  # L
        print(x)  # 打印 "local"

    inner()


outer()
print(x)
