# 复数（complex）使用演示

print("=" * 50)
print("复数基础演示")
print("=" * 50)

# 1. 创建复数的两种方式
num1 = 3 + 4j          # 直接字面量方式
num2 = complex(3, 4)   # 使用 complex() 函数

print(f"\n方式1 - 字面量: num1 = {num1}")
print(f"方式2 - 函数:   num2 = {num2}")
print(f"两者相等: {num1 == num2}")

# 2. 不同的创建方式
print("\n" + "=" * 50)
print("不同的复数创建方式")
print("=" * 50)

c1 = complex(5, 0)      # 只有实部: 5+0j
c2 = complex(0, 7)      # 只有虚部: 0+7j
c3 = complex(2, -3)     # 负虚部: 2-3j
c4 = complex(-1, -2)    # 负实部和负虚部: -1-2j
c5 = complex('3+4j')    # 从字符串创建

print(f"c1 = complex(5, 0)    → {c1}")
print(f"c2 = complex(0, 7)    → {c2}")
print(f"c3 = complex(2, -3)   → {c3}")
print(f"c4 = complex(-1, -2)  → {c4}")
print(f"c5 = complex('3+4j')  → {c5}")

# 3. 获取实部和虚部
print("\n" + "=" * 50)
print("获取复数的实部和虚部")
print("=" * 50)

num = 3 + 4j
print(f"\n复数: {num}")
print(f"实部 (real): {num.real}")
print(f"虚部 (imag): {num.imag}")
print(f"共轭复数: {num.conjugate()}")
print(f"模（绝对值）: {abs(num)}")  # √(3² + 4²) = 5

# 4. 复数运算
print("\n" + "=" * 50)
print("复数运算")
print("=" * 50)

a = 2 + 3j
b = 1 - 2j

print(f"\na = {a}")
print(f"b = {b}")
print(f"a + b = {a + b}")      # 加法: (2+1) + (3-2)j = 3+1j
print(f"a - b = {a - b}")      # 减法: (2-1) + (3+2)j = 1+5j
print(f"a * b = {a * b}")      # 乘法
print(f"a / b = {a / b}")      # 除法

# 5. 实际应用场景：交流电路计算
print("\n" + "=" * 50)
print("实际应用：交流电路阻抗计算")
print("=" * 50)

# 电阻 R = 10Ω，感抗 XL = 5jΩ，容抗 XC = -3jΩ
R = complex(10, 0)    # 纯电阻
XL = complex(0, 5)    # 感抗
XC = complex(0, -3)   # 容抗

# 总阻抗 Z = R + XL + XC
Z = R + XL + XC
print(f"\n电阻 R = {R} Ω")
print(f"感抗 XL = {XL} Ω")
print(f"容抗 XC = {XC} Ω")
print(f"总阻抗 Z = {Z} Ω")
print(f"阻抗大小 |Z| = {abs(Z):.2f} Ω")

# 6. 类型检查
print("\n" + "=" * 50)
print("类型检查")
print("=" * 50)

print(f"\ntype(3 + 4j) = {type(3 + 4j)}")
print(f"isinstance(3 + 4j, complex) = {isinstance(3 + 4j, complex)}")
print(f"isinstance(10, complex) = {isinstance(10, complex)}")  # False
print(f"isinstance(10.5, complex) = {isinstance(10.5, complex)}")  # False
