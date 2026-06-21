import sys

import math

print("Hello, World!")
print(f"系统信息：{sys.version}")
print(f"当前正在使用的 Python 解释器路径是：{sys.executable}")
print("🎉 恭喜！你的虚拟环境运行完全正常！")

# print("*" * 10)

x = 1

# print(3_2)
# print(3.14_15_92)

# print(3 // 2) # //：整除运算符，会返回除法结果的整数部分
# print(-7.0 // 2) # 针对负数时会向下取整，-3.5 => -4

# print( 3 ** 2)
# print( 3.0 ** 2)

# print( -3.0 ** 2)

# 这是第一个注释
# 这是第二个注释

"""这是多行注释
多行注释占用多行。
Python 正在吞噬世界
"""

point1 = (2, 3)
point2 = (10, 8)

distance = ((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2) ** 0.5
print(distance)

# 获取平方根
print(9 ** 0.5)
print(math.sqrt(9))
print(9 ** (1/2))