import os
from pathlib import Path

"""
math（数学运算）：提供许多数学公式和常量
常量：pi（圆周率）、e（自然常数）、tau（2π）、inf（正无穷）、nan（非数字）
"""
# print(math.floor(3.6))  # 向下取整
# print(math.ceil(3.2))  # 向上取整
# print(math.radians(90))  # 角度转换为弧度
# print(math.pi)  # 圆周率
# print(math.trunc(3.699))

# print(math.pow(2, 10))
# print(2 ** 10)

"""
random（随机数）：提供随机数生成
常用于生成随机数字、洗牌、随机选择等
"""
# print(random.randint(1, 10))  # 产生 1 到 10 之间的随机整数
# print(random.random())  # 产生 0.0 到 1.0 之间的随机浮点数
# print(random.uniform(1, 10))  # 产生 1.0 到 10.0 之间的随机浮点数
fruits = ['苹果', '香蕉', '橘子']
# print(random.choice(fruits))


print(os.getcwd())
print(os.listdir(os.getcwd()))
print(Path.cwd())
print(Path.home())
