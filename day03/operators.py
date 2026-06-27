# 运算符

# ===== 一. 算术运算符（Arithmetic Operators）=====
a, b = 10, 3
# print(a + b)  # [ + ] 加
# print(a - b)  # [ - ] 减
# print(a * b)  # [ * ] 乘
# print('hi ' * 5, )  # 字符串相乘
# print(a / b)  # [ / ] 除，返回浮点数(float)
# print(a // b)  # [ // ] 整除
# print(a % b)  # [ % ] 模运算，取余
# print(a ** b)  # [ ** ] 幂运算
# print(-a)  # [ - ] 取负


# ===== 二. 赋值运算符（Assignment Operators）=====
x = 5  # [ = ] 普通赋值
# x += 3  # [ += ] 赋值并相加
# x -= 3  # [ -= ] 赋值并相减
# x *= 3  # [ *= ] 赋值并相乘
# x /= 3  # [ /= ] 赋值并相除
# x //= 3  # [ //= ] 赋值并整除
# x %= 3  # [ %= ] 赋值并取余
# x **= 3  # [ **= ] 赋值并幂运算
# print(x)
y = 10
# y &= 3  # [ &= ] 赋值并按位与
# y |= 3  # [ |= ] 赋值并按位或
# y ^= 3  # [ ^= ] 赋值并按位异或
# y <<= 3 # [ <<= ] 赋值并左移
# y >>= 3 # [ >>= ] 赋值并右移
# print(y)

# [ := ] 海象运算符，python3.8+ 引入的赋值表达式运算符，运行在表达式内部为变量赋值，常用于循环条件判断
# if name := input("请输入："):
#     print(name)

# if (n := len("Hello")) > 3:
#     print(f"长度为 {n}")


# ===== 三. 比较运算符（Comparison Operators）=====
# 比较运算符的结果都是布尔值（True | False）
m, n = 5, 10
# print(m == n)  # [ == ] 等于
# print(m != n)  # [ != ] 不等于
# print(m > n)  # [ > ] 大于
# print(m < n)  # [ < ] 小于
# print(m >= n)  # [ >= ] 大于等于
# print(m <= n)  # [ <= ] 小于等于


# ===== 四. 逻辑运算符（Logical Operators）=====
age = 20
score = 90
# print(age > 18 and score > 80)  # [ and ] 逻辑与，如果两个条件都为真，则返回真
# print(age > 18 or score > 100)  # [ or ] 逻辑或，如果两个条件中任意一个为真，则返回真
# print(not age > 30)  # [ not ] 逻辑非，返回相反结果，取反


# ===== 五. 成员运算符（Membership Operators）=====
# 用于判断一个值是否存在于一个序列（字符串、列表、元祖或字典）中
my_list = [1, 2, 3, 4, 5]
# print(8 in my_list)  # [ in ] 判断某个值是否在序列中
# print(2 not in my_list)  # [ not in ] 判断某个值是否不在序列中
my_string = "Hello World"
# print('world' in my_string)  # False, Python 严格区分大小写
# print('d' in {'d': 1})  # 字典检查 key


# ===== 六. 身份运算符（Identity Operators）=====
# 用于判断两个对象的【内存地址】是否相同
list_a = [1, 2, 3]
list_b = [1, 2, 3]
list_c = list_a
# print(list_a == list_b)  # True，== 判断的是值是否相等
# print(list_a is list_b)  # [ is ] 判断两个对象是否为同一个对象，等价于 id(list_a) == id(list_b)
# print(id(list_a))
# print(id(list_b))
# print(id(list_c))
# print(list_b is not list_c)  # [ is not ] 判断两个对象是否为不同对象，等价于 id(list_a) != id(list_b)


# ===== 七. 位运算符（Bitwise Operators）=====
# 位运算是对整数的二进制位进行操作
p, q = 0b1100, 0b1010  # 12, 10
# print(a & b)  # [ & ] 按位与（同一位都为1则为1） => 0b1000 => 8
# print(a | b)  # [ | ] 按位或（同一位只要有1则为1） => 0b1110 => 14
# print(a ^ b)  # [ ^ ] 按位异或（同一位不同则为1） => 0b0110 => 6
# print(~p)  # [ ~ ] 按位取反（取反码） => 0b0011 => -13
# print(~6)  # Python 使用补码表示整数，~x 等价于 -(x + 1)
# print(p << 2)  # [ << ] 左移（二进制位向左移动） => 0b110000 => 48
print(p >> 1)  # [ >> ] 右移（二进制位向右移动） => 0b0110 => 6

# ===== 八. 运算符优先级（Operator Precedence）=====
"""
运算符优先级（从高到低）：

| 优先级 | 运算符                                    | 说明           |
| ------ | ----------------------------------------- | -------------- |
| 高     | `()`                                      | 括号           |
| ↑      | `**`                                      | 幂运算         |
| ↑      | `+x`、`-x`、`~x`                          | 一元运算符     |
| ↑      | `*`、`/`、`//`、`%`                       | 乘、除、整除、取模 |
| ↑      | `+`、`-`                                  | 加、减         |
| ↑      | `<<`、`>>`                                | 位移运算       |
| ↑      | `&`                                       | 按位与         |
| ↑      | `^`                                       | 按位异或       |
| ↑      | `|`                                      | 按位或         |
| ↑      | `==`、`!=`、`<`、`>`、`<=`、`>=`、`is`、`in` | 比较、身份、成员运算 |
| ↑      | `not`                                     | 逻辑非         |
| ↑      | `and`                                     | 逻辑与         |
| 低     | `or`                                      | 逻辑或         |
"""
