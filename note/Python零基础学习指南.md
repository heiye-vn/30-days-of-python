## Python 零基础学习指南

> 面向完全零基础读者的 Python 入门教程。从安装环境到面向对象编程，循序渐进，每个知识点都配有可直接运行的示例代码。

---

### 第一章：认识 Python

Python 是一种解释型、动态类型的高级编程语言，由 Guido van Rossum 于 1991 年发布。它以简洁易读著称，被广泛应用于 Web 开发、数据科学、人工智能、自动化脚本、游戏开发等领域。

为什么选择 Python？因为它几乎是所有编程语言中语法最接近自然语言的。举个例子，打印一句话只需要写：

```python
print("Hello, World!")
```

同样的功能在 Java 中需要写一个类、一个 main 方法，而在 Python 中只需要一行。这种简洁性让初学者可以把精力放在"学编程思维"而不是"和语法作斗争"上。

Python 目前有两个主要版本：Python 2 和 Python 3。Python 2 已于 2020 年停止维护，所以请直接学习 Python 3（当前最新稳定版为 3.12+）。

---

### 第二章：环境搭建

#### 2.1 安装 Python

前往官网 https://www.python.org/downloads/ 下载最新的 Python 3 安装包。

Windows 用户安装时务必勾选 **"Add Python to PATH"** 这个选项，否则命令行中无法直接使用 `python` 命令。

安装完成后，打开命令提示符（Win + R 输入 `cmd`），输入：

```bash
python --version
```

如果看到类似 `Python 3.12.x` 的输出，说明安装成功。

#### 2.2 编写第一个程序

你可以使用任何文本编辑器编写 Python 代码，文件扩展名为 `.py`。这里推荐几个工具：

- **VS Code**（免费，微软出品，Python 插件体验极佳）—— 强烈推荐
- **PyCharm Community**（免费，JetBrains 出品，专为 Python 设计）
- **IDLE**（Python 自带，适合临时测试）

创建一个文件 `hello.py`，写入以下内容：

```python
# 这是我的第一个 Python 程序
print("你好，Python！")
```

然后在命令行中运行：

```bash
python hello.py
```

你会看到输出：`你好，Python！`

#### 2.3 交互式解释器

除了写文件，Python 还支持交互式运行。在命令行直接输入 `python` 就会进入交互模式：

```
>>> 1 + 1
2
>>> print("你好")
你好
>>> 3 * 7
21
```

输入 `exit()` 或按 `Ctrl+Z` 然后回车即可退出。交互式解释器特别适合快速测试一小段代码。

---

### 第三章：变量与数据类型

#### 3.1 变量

在 Python 中，不需要声明变量类型，直接赋值即可：

```python
name = "小明"       # 字符串
age = 25            # 整数
height = 1.75       # 浮点数
is_student = True   # 布尔值
```

Python 是动态类型语言，这意味着同一个变量可以在不同时刻指向不同类型的值（虽然实践中不建议这样做）：

```python
x = 10       # 此时 x 是整数
x = "hello"  # 现在 x 变成了字符串
```

变量命名规则：只能包含字母、数字和下划线，不能以数字开头，区分大小写。推荐使用小写字母加下划线的命名风格（snake_case），比如 `my_first_name`。

#### 3.2 基本数据类型

Python 有四种最基本的数据类型：

```python
# 整数 (int) —— 没有小数点
a = 42
b = -100
c = 0

# 浮点数 (float) —— 有小数点
pi = 3.14159
temperature = -5.5

# 字符串 (str) —— 用引号包裹的文本
greeting = "你好"
name = '小明'        # 单引号双引号都可以
multiline = """这是
一段多行
文本"""              # 三引号支持多行

# 布尔值 (bool) —— 只有 True 和 False
is_valid = True
is_empty = False
```

#### 3.3 类型查看与转换

使用 `type()` 函数查看变量类型：

```python
x = 42
print(type(x))   # <class 'int'>

y = "hello"
print(type(y))   # <class 'str'>
```

使用类型名作为函数进行转换：

```python
# 字符串转整数
num_str = "123"
num = int(num_str)      # 123

# 整数转字符串
age = 25
age_str = str(age)      # "25"

# 字符串转浮点数
price_str = "9.99"
price = float(price_str) # 9.99

# 浮点数转整数（直接截断小数部分）
pi = 3.14
pi_int = int(pi)         # 3
```

#### 3.4 字符串详解

字符串是最常用的数据类型之一，有很多便捷的操作：

```python
name = "Python"

# 拼接
full = "Hello " + name        # "Hello Python"

# 重复
line = "-" * 20               # "--------------------"

# 长度
length = len(name)            # 6

# 索引（从 0 开始）
first = name[0]               # "P"
last = name[-1]               # "n"（负索引从末尾数）

# 切片 [起始:结束]（不包含结束位置）
sub = name[0:3]               # "Pyt"
sub2 = name[2:]               # "thon"
sub3 = name[:4]               # "Pyth"

# 常用方法
text = "  Hello World  "
print(text.strip())           # "Hello World"（去除两端空格）
print(text.upper())           # "  HELLO WORLD  "
print(text.lower())           # "  hello world  "
print(text.replace("World", "Python"))  # "  Hello Python  "
print(text.strip().split(" "))         # ["Hello", "World"]

# f-string 格式化（Python 3.6+，推荐方式）
name = "小明"
age = 25
print(f"我叫{name}，今年{age}岁")       # 我叫小明，今年25岁
print(f"明年我{age + 1}岁")            # 明年我26岁
print(f"圆周率保留两位：{3.14159:.2f}") # 圆周率保留两位：3.14
```

---

### 第四章：运算符

#### 4.1 算术运算符

```python
a = 10
b = 3

print(a + b)    # 13  加法
print(a - b)    # 7   减法
print(a * b)    # 30  乘法
print(a / b)    # 3.333...  除法（结果是浮点数）
print(a // b)   # 3   整除（地板除）
print(a % b)    # 1   取余数
print(a ** b)   # 1000 幂运算（10的3次方）
```

#### 4.2 比较运算符

比较运算的结果总是布尔值（True 或 False）：

```python
x = 10
print(x == 10)   # True   等于
print(x != 5)    # True   不等于
print(x > 5)     # True   大于
print(x < 5)     # False  小于
print(x >= 10)   # True   大于等于
print(x <= 10)   # True   小于等于
```

#### 4.3 逻辑运算符

```python
a = True
b = False

print(a and b)   # False  两者都为 True 才为 True
print(a or b)    # True   任一为 True 就为 True
print(not a)     # False  取反
```

逻辑运算符常用于组合条件判断：

```python
age = 25
has_id = True
if age >= 18 and has_id:
    print("可以进入")
```

#### 4.4 赋值运算符

```python
x = 10
x += 3    # 等同于 x = x + 3，结果 13
x -= 2    # 等同于 x = x - 2，结果 11
x *= 4    # 等同于 x = x * 4，结果 44
x //= 5   # 等同于 x = x // 5，结果 8
```

---

### 第五章：控制流

#### 5.1 条件判断 (if / elif / else)

```python
score = 85

if score >= 90:
    print("优秀")
elif score >= 80:
    print("良好")        # ← 会输出这个
elif score >= 60:
    print("及格")
else:
    print("不及格")
```

注意事项：条件后面要加冒号 `:`，缩进用 4 个空格（不要用 Tab）。Python 用缩进来表示代码块，这是它最显著的特征之一。

条件可以嵌套，但建议不要超过三层：

```python
age = 20
is_member = True

if age >= 18:
    if is_member:
        print("成年会员")
    else:
        print("成年非会员")
else:
    print("未成年")
```

#### 5.2 for 循环

`for` 循环用于遍历一个序列（列表、字符串、范围等）：

```python
# 遍历列表
fruits = ["苹果", "香蕉", "橘子"]
for fruit in fruits:
    print(fruit)

# 遍历字符串
for char in "Hello":
    print(char)       # 依次打印 H, e, l, l, o

# 使用 range() 生成数字序列
for i in range(5):
    print(i)          # 打印 0, 1, 2, 3, 4

for i in range(2, 8):
    print(i)          # 打印 2, 3, 4, 5, 6, 7

for i in range(0, 10, 2):
    print(i)          # 打印 0, 2, 4, 6, 8（步长为2）
```

`enumerate()` 函数可以同时获取索引和值：

```python
colors = ["红", "绿", "蓝"]
for index, color in enumerate(colors):
    print(f"第{index}个颜色是{color}")
```

#### 5.3 while 循环

`while` 循环在条件为 True 时持续执行：

```python
count = 0
while count < 5:
    print(count)
    count += 1       # 别忘了更新条件，否则会死循环
```

#### 5.4 break 和 continue

```python
# break：立即跳出循环
for i in range(10):
    if i == 5:
        break
    print(i)         # 打印 0, 1, 2, 3, 4

# continue：跳过本次，继续下一次循环
for i in range(10):
    if i % 2 == 0:
        continue
    print(i)         # 打印 1, 3, 5, 7, 9（跳过偶数）
```

#### 5.5 列表推导式

列表推导式是 Python 最优雅的特性之一，用一行代码创建列表：

```python
# 传统写法
squares = []
for i in range(10):
    squares.append(i ** 2)

# 列表推导式写法
squares = [i ** 2 for i in range(10)]
# 结果：[0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

# 带条件筛选
even_squares = [i ** 2 for i in range(10) if i % 2 == 0]
# 结果：[0, 4, 16, 36, 64]

# 字符串处理
words = ["hello", "world", "python"]
upper_words = [w.upper() for w in words]
# 结果：["HELLO", "WORLD", "PYTHON"]
```

---

### 第六章：复合数据结构

#### 6.1 列表 (list)

列表是 Python 中最常用的数据结构，用方括号表示，可以包含不同类型的元素：

```python
# 创建列表
numbers = [1, 2, 3, 4, 5]
mixed = [1, "hello", True, 3.14]
empty = []

# 访问元素
print(numbers[0])     # 1（第一个元素）
print(numbers[-1])    # 5（最后一个元素）

# 修改元素
numbers[0] = 10
print(numbers)        # [10, 2, 3, 4, 5]

# 常用方法
numbers.append(6)     # 末尾添加 → [10, 2, 3, 4, 5, 6]
numbers.insert(1, 99) # 在索引1处插入 → [10, 99, 2, 3, 4, 5, 6]
numbers.remove(3)     # 删除第一个值为3的元素
popped = numbers.pop() # 弹出并返回最后一个元素
numbers.extend([7, 8]) # 合并另一个列表
numbers.sort()        # 排序（原地排序，修改原列表）
numbers.reverse()     # 反转

# 切片
a = [0, 1, 2, 3, 4, 5]
print(a[1:4])    # [1, 2, 3]
print(a[:3])     # [0, 1, 2]
print(a[3:])     # [3, 4, 5]
print(a[::2])    # [0, 2, 4]（步长为2）

# 长度、最大值、最小值、求和
nums = [3, 1, 4, 1, 5, 9]
print(len(nums))  # 6
print(max(nums))  # 9
print(min(nums))  # 1
print(sum(nums))  # 23

# 判断元素是否在列表中
print(4 in nums)   # True
print(10 in nums)  # False
```

#### 6.2 元组 (tuple)

元组和列表类似，但**创建后不可修改**（不可变），用圆括号表示：

```python
point = (3, 4)
rgb = (255, 128, 0)

# 访问元素（和列表一样用索引）
print(point[0])   # 3

# 解包
x, y = point
print(x)          # 3
print(y)          # 4

# 元组不可修改
# point[0] = 10   # ← 这行会报错 TypeError

# 常见用途：函数返回多个值时自动使用元组
def get_position():
    return 100, 200   # 返回元组 (100, 200)

x, y = get_position()
```

什么时候用元组而不是列表？当你希望数据不会被意外修改时，比如坐标、颜色值、数据库查询的一行记录等。

#### 6.3 字典 (dict)

字典用键值对存储数据，查找速度极快：

```python
# 创建字典
person = {
    "name": "小明",
    "age": 25,
    "city": "北京"
}

# 访问值
print(person["name"])        # 小明
print(person.get("age"))     # 25
print(person.get("gender", "未知"))  # "未知"（键不存在时返回默认值）

# 添加 / 修改
person["email"] = "xm@example.com"   # 添加新键值对
person["age"] = 26                   # 修改已有键的值

# 删除
del person["city"]
age = person.pop("age")      # 弹出并返回该值

# 遍历
for key, value in person.items():
    print(f"{key}: {value}")

# 只遍历键或值
for key in person.keys():
    print(key)
for value in person.values():
    print(value)

# 判断键是否存在
print("name" in person)    # True

# 字典推导式
squares = {x: x**2 for x in range(5)}
# 结果：{0: 0, 1: 1, 2: 4, 3: 9, 4: 16}
```

#### 6.4 集合 (set)

集合中的元素不重复，适合去重和集合运算：

```python
# 创建集合
fruits = {"苹果", "香蕉", "橘子", "苹果"}
print(fruits)   # {"苹果", "橘子", "香蕉"}（自动去重）

# 从列表去重
numbers = [1, 2, 2, 3, 3, 3]
unique = list(set(numbers))   # [1, 2, 3]

# 集合运算
a = {1, 2, 3, 4}
b = {3, 4, 5, 6}

print(a | b)    # {1, 2, 3, 4, 5, 6}  并集
print(a & b)    # {3, 4}              交集
print(a - b)    # {1, 2}              差集

# 添加和删除
fruits.add("葡萄")
fruits.remove("香蕉")
```

---

### 第七章：函数

#### 7.1 定义与调用

函数用 `def` 关键字定义，是组织代码的基本单元：

```python
def greet(name):
    """向某人打招呼"""        # 这是文档字符串（docstring）
    return f"你好，{name}！"

message = greet("小明")
print(message)   # 你好，小明！
```

#### 7.2 参数类型

```python
# 默认参数
def power(base, exp=2):
    return base ** exp

print(power(3))       # 9 （使用默认指数2）
print(power(3, 3))    # 27

# 关键字参数（调用时指定参数名，顺序可以任意）
def describe_pet(name, animal_type):
    print(f"我有一只{animal_type}，叫{name}")

describe_pet(animal_type="猫", name="咪咪")

# 可变参数 *args —— 接收任意数量的位置参数
def sum_all(*numbers):
    total = 0
    for n in numbers:
        total += n
    return total

print(sum_all(1, 2, 3))       # 6
print(sum_all(1, 2, 3, 4, 5)) # 15

# 可变关键字参数 **kwargs —— 接收任意数量的关键字参数
def print_info(**kwargs):
    for key, value in kwargs.items():
        print(f"{key}: {value}")

print_info(name="小明", age=25, city="北京")
```

#### 7.3 返回值

```python
# 返回多个值（实际上是返回元组）
def min_max(numbers):
    return min(numbers), max(numbers)

low, high = min_max([3, 1, 4, 1, 5, 9])
print(low)    # 1
print(high)   # 9

# 没有 return 或 return 后面没有值，函数返回 None
def say_hello():
    print("Hello!")

result = say_hello()  # 打印 Hello!
print(result)          # None
```

#### 7.4 作用域

变量在函数内部定义的是局部变量，在外部不可见：

```python
x = "全局变量"

def my_func():
    x = "局部变量"
    print(x)     # 局部变量

my_func()
print(x)         # 全局变量
```

#### 7.5 Lambda 表达式

Lambda 是一种简短的匿名函数，适合简单的计算：

```python
# 普通函数
def double(x):
    return x * 2

# Lambda 等价写法
double = lambda x: x * 2

# Lambda 最常见于排序、过滤等场景的 key 参数
students = [("小明", 85), ("小红", 92), ("小华", 78)]
students.sort(key=lambda s: s[1], reverse=True)
# 按分数从高到低：[("小红", 92), ("小明", 85), ("小华", 78)]
```

---

### 第八章：文件操作

#### 8.1 读写文本文件

```python
# 写入文件（会覆盖已有内容）
with open("example.txt", "w", encoding="utf-8") as f:
    f.write("第一行内容\n")
    f.write("第二行内容\n")

# 追加内容
with open("example.txt", "a", encoding="utf-8") as f:
    f.write("追加的第三行\n")

# 读取整个文件
with open("example.txt", "r", encoding="utf-8") as f:
    content = f.read()
    print(content)

# 逐行读取（更省内存，适合大文件）
with open("example.txt", "r", encoding="utf-8") as f:
    for line in f:
        print(line.strip())    # strip() 去掉行尾的换行符

# 读取所有行为列表
with open("example.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()
```

`with` 语句是 Python 中操作文件的最佳实践，它会在代码块结束后自动关闭文件，即使发生异常也不例外。

#### 8.2 处理 JSON 文件

JSON 是互联网上最常用的数据交换格式，Python 内置了 `json` 模块：

```python
import json

# 将 Python 字典写入 JSON 文件
data = {
    "name": "小明",
    "age": 25,
    "hobbies": ["编程", "阅读", "游泳"]
}

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# 从 JSON 文件读取
with open("data.json", "r", encoding="utf-8") as f:
    loaded = json.load(f)
    print(loaded["name"])        # 小明
    print(loaded["hobbies"][0])  # 编程

# 字符串与 JSON 互转
json_str = json.dumps(data, ensure_ascii=False)
print(json_str)

parsed = json.loads(json_str)
print(parsed["age"])   # 25
```

---

### 第九章：异常处理

程序运行时难免出错。异常处理让你的程序在遇到问题时不会直接崩溃，而是优雅地处理。

#### 9.1 try / except

```python
try:
    number = int(input("请输入一个数字："))
    result = 10 / number
    print(f"结果是：{result}")
except ValueError:
    print("输入的不是有效数字！")
except ZeroDivisionError:
    print("不能除以零！")
except Exception as e:
    print(f"发生了未知错误：{e}")
finally:
    print("程序执行完毕")    # 无论是否异常都会执行
```

#### 9.2 常见异常类型

```python
# ZeroDivisionError —— 除以零
# 1 / 0

# TypeError —— 类型错误
# "hello" + 5

# IndexError —— 索引越界
# my_list = [1, 2, 3]
# print(my_list[10])

# KeyError —— 字典键不存在
# my_dict = {"a": 1}
# print(my_dict["b"])

# FileNotFoundError —— 文件不存在
# open("不存在的文件.txt")

# ValueError —— 值不合法
# int("abc")
```

#### 9.3 主动抛出异常

```python
def set_age(age):
    if age < 0:
        raise ValueError("年龄不能为负数")
    if not isinstance(age, int):
        raise TypeError("年龄必须是整数")
    return age
```

---

### 第十章：面向对象编程 (OOP)

面向对象编程是一种将数据和操作数据的方法组织在一起（称为"对象"）的编程范式。

#### 10.1 类与对象

```python
class Dog:
    """一只狗的类"""

    # 类变量（所有实例共享）
    species = "犬科"

    # 初始化方法（构造函数）
    def __init__(self, name, age):
        # 实例变量（每个实例独有）
        self.name = name
        self.age = age

    # 实例方法
    def bark(self):
        return f"{self.name}在叫：汪汪！"

    def info(self):
        return f"{self.name}，{self.age}岁，{self.species}"

# 创建对象（实例化）
my_dog = Dog("旺财", 3)
print(my_dog.bark())    # 旺财在叫：汪汪！
print(my_dog.info())    # 旺财，3岁，犬科
print(my_dog.name)      # 旺财
```

#### 10.2 继承

继承允许你基于已有的类创建新类，新类自动拥有父类的所有属性和方法：

```python
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        return "..."

class Cat(Animal):
    def speak(self):
        return f"{self.name}：喵~"

class Dog(Animal):
    def speak(self):
        return f"{self.name}：汪！"

# 多态：不同类型的对象可以用相同的方式调用
animals = [Cat("咪咪"), Dog("旺财")]
for animal in animals:
    print(animal.speak())
# 咪咪：喵~
# 旺财：汪！
```

#### 10.3 封装与属性

```python
class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self._balance = balance   # 约定 _ 开头表示"内部使用"

    @property
    def balance(self):
        """余额属性（只读）"""
        return self._balance

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("存款金额必须大于零")
        self._balance += amount

    def withdraw(self, amount):
        if amount > self._balance:
            raise ValueError("余额不足")
        self._balance -= amount

# 使用
account = BankAccount("小明", 1000)
account.deposit(500)
print(account.balance)    # 1500
# account.balance = 9999  # ← 这行会报错，因为 balance 是只读属性
```

#### 10.4 魔术方法（dunder methods）

```python
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        """print() 时的输出"""
        return f"Vector({self.x}, {self.y})"

    def __repr__(self):
        """调试时的表示"""
        return f"Vector({self.x}, {self.y})"

    def __add__(self, other):
        """支持 + 运算符"""
        return Vector(self.x + other.x, self.y + other.y)

    def __len__(self):
        """支持 len() 函数"""
        return int((self.x**2 + self.y**2) ** 0.5)

v1 = Vector(3, 4)
v2 = Vector(1, 2)
v3 = v1 + v2
print(v3)      # Vector(4, 6)
```

---

### 第十一章：模块与包

#### 11.1 导入模块

模块就是一个 `.py` 文件，包就是一个包含模块的文件夹。Python 的标准库提供了大量开箱即用的功能。

```python
# 导入整个模块
import math
print(math.sqrt(16))    # 4.0
print(math.pi)          # 3.14159...

# 导入特定内容
from math import sqrt, pi
print(sqrt(16))

# 起别名
import datetime as dt
now = dt.datetime.now()
print(now)

from collections import Counter
words = ["apple", "banana", "apple", "cherry", "banana", "apple"]
count = Counter(words)
print(count)           # Counter({"apple": 3, "banana": 2, "cherry": 1})
print(count.most_common(2))  # [("apple", 3), ("banana", 2)]
```

#### 11.2 常用标准库速览

```python
# os —— 操作系统相关
import os
print(os.getcwd())          # 当前工作目录
os.makedirs("new_folder", exist_ok=True)  # 创建文件夹
print(os.listdir("."))      # 列出当前目录的文件

# pathlib —— 更现代的路径操作（推荐）
from pathlib import Path
p = Path("example.txt")
p.write_text("Hello!", encoding="utf-8")
content = p.read_text(encoding="utf-8")
print(p.exists())           # True

# random —— 随机数
import random
print(random.randint(1, 100))          # 1到100的随机整数
print(random.choice(["红", "绿", "蓝"])) # 随机选一个
nums = list(range(10))
random.shuffle(nums)                    # 打乱顺序

# datetime —— 日期时间
from datetime import datetime, timedelta
now = datetime.now()
print(now.strftime("%Y-%m-%d %H:%M:%S"))   # 格式化输出
tomorrow = now + timedelta(days=1)

# re —— 正则表达式
import re
text = "我的邮箱是 test@example.com 和 hello@world.org"
emails = re.findall(r'[\w.]+@[\w.]+', text)
print(emails)   # ["test@example.com", "hello@world.org"]
```

#### 11.3 安装第三方包

Python 的第三方生态极其丰富，通过 `pip` 命令安装：

```bash
# 安装单个包
pip install requests

# 安装多个包
pip install requests pandas numpy

# 查看已安装的包
pip list

# 导出依赖列表（方便协作）
pip freeze > requirements.txt

# 从依赖列表安装
pip install -r requirements.txt
```

使用示例——用 `requests` 库发起 HTTP 请求：

```python
import requests

response = requests.get("https://httpbin.org/get")
data = response.json()
print(data)
```

---

### 第十二章：实用技巧与进阶

#### 12.1 解包

```python
# 列表/元组解包
a, b, c = [1, 2, 3]
first, *rest = [1, 2, 3, 4, 5]
print(first)   # 1
print(rest)    # [2, 3, 4, 5]

first, *middle, last = [1, 2, 3, 4, 5]
print(middle)  # [2, 3, 4]

# 字典解包（Python 3.5+）
defaults = {"color": "红", "size": "M"}
custom = {"size": "L", "brand": "Nike"}
merged = {**defaults, **custom}
# {"color": "红", "size": "L", "brand": "Nike"}
```

#### 12.2 三元表达式

```python
age = 20
status = "成年" if age >= 18 else "未成年"
print(status)   # 成年
```

#### 12.3 生成器

生成器是一种惰性求值的迭代器，适合处理大量数据：

```python
def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        yield a    # yield 代替 return，使函数变成生成器
        a, b = b, a + b

# 使用
for num in fibonacci(10):
    print(num)   # 0, 1, 1, 2, 3, 5, 8, 13, 21, 34

# 生成器表达式（类似列表推导式，但更省内存）
squares = (x**2 for x in range(1000000))
# 不会立即计算所有值，每次取一个
```

#### 12.4 装饰器

装饰器是在不修改函数本身的情况下增强函数功能的工具：

```python
import time

def timer(func):
    """计算函数执行时间的装饰器"""
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} 耗时 {end - start:.4f} 秒")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(1)
    return "完成"

slow_function()
# 输出：slow_function 耗时 1.00xx 秒
```

#### 12.5 类型提示（Type Hints）

Python 3.5+ 支持类型提示，不影响运行但能让代码更易读、IDE 提示更准确：

```python
def greet(name: str, times: int = 1) -> str:
    return (f"Hello, {name}! " * times).strip()

def process_numbers(numbers: list[int]) -> dict[str, float]:
    return {
        "mean": sum(numbers) / len(numbers),
        "max": max(numbers),
        "min": min(numbers),
    }
```

---

### 第十三章：实战练习建议

学习编程最重要的就是动手写。以下是按难度递进的练习项目：

**入门级（第1-3章知识）：**

- 计算器：接收两个数字和运算符，输出结果
- 猜数字游戏：程序随机生成一个数字，用户来猜，给出"大了"或"小了"的提示
- 温度转换器：摄氏度与华氏度互相转换

**进阶级（第4-7章知识）：**

- 通讯录管理系统：用字典存储联系人，支持增删改查
- 简易记事本：用文件读写实现笔记的创建、查看、删除
- 词频统计器：读取一篇文章，统计每个单词出现的次数并排序

**挑战级（综合知识）：**

- 待办事项 CLI 工具：命令行版的 todo list，支持添加、完成、删除、列出，数据持久化到 JSON 文件
- 网页爬虫入门：用 `requests` + `BeautifulSoup` 抓取网页标题和链接
- 数据分析入门：用 `pandas` 读取 CSV 文件，进行简单的数据统计和可视化

**推荐的练习方式：** 每学完一章就动手做对应的练习，遇到不会的先自己查、先自己试，实在不行再看答案。编程能力的提升来自于"自己解决问题"的过程，而不是"看懂答案"的瞬间。

---

### 附录：学习资源推荐

**官方与系统学习：**

- Python 官方教程（中文）：https://docs.python.org/zh-cn/3/tutorial/
- 《Python Crash Course》（入门经典书籍）
- Real Python 网站：https://realpython.com （高质量教程和文章）

**练习平台：**

- LeetCode（https://leetcode.cn）—— 算法题，从"简单"难度开始
- 洛谷（https://www.luogu.com.cn）—— 中文算法练习平台
- Codewars（https://www.codewars.com）—— 游戏化的编程挑战

**社区：**

- Stack Overflow —— 全球最大的编程问答社区
- Python 中文社区 —— 搜索"Python 中文社区"可找到论坛和公众号

祝学习顺利！
