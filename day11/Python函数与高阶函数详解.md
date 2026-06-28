# Python 函数与高阶函数详解

> 适合 Python 初学者阅读。从基础概念到高级用法，系统掌握 Python 函数体系。

---

## 一、函数基础

### 1.1 什么是函数

函数是一段可重复使用的代码块，接收输入（参数）、执行操作、返回结果。

```python
def greet(name):
    return f"你好，{name}"

result = greet("小明")
print(result)  # 你好，小明
```

使用函数的好处：
- **代码复用**：避免重复写相同逻辑
- **模块化**：把大问题拆成小问题
- **可读性**：好的函数名就是文档

---

### 1.2 函数的定义与调用

```python
def add(a, b):      # 定义
    return a + b

result = add(3, 5)  # 调用
print(result)       # 8
```

**注意**：如果没有 `return`，函数默认返回 `None`。

```python
def do_nothing():
    pass

print(do_nothing())  # None
```

---

## 二、参数详解

### 2.1 位置参数

最基础的参数形式，按顺序传入：

```python
def describe_pet(type, name):
    print(f"我有一只{type}，叫{name}")

describe_pet("猫", "咪咪")  # 我有一只猫，叫咪咪
describe_pet("狗", "旺财")  # 我有一只狗，叫旺财
```

### 2.2 关键字参数

调用时明确指定参数名，顺序任意：

```python
describe_pet(name="咪咪", type="猫")  # 我有一只猫，叫咪咪
```

**混合使用规则**：位置参数必须在前，关键字参数在后。

```python
describe_pet("猫", name="咪咪")  # 正确
# describe_pet(type="猫", "咪咪")  # 错误！位置参数不能在关键字参数后面
```

### 2.3 默认参数

给参数设置默认值，调用时可以省略：

```python
def greet(name, greeting="你好"):
    return f"{greeting}，{name}"

print(greet("小明"))              # 你好，小明
print(greet("John", "Hello"))     # Hello，John
```

**陷阱：不要用可变对象做默认值**

```python
# 错误示范
def append_to(item, lst=[]):
    lst.append(item)
    return lst

print(append_to(1))  # [1]
print(append_to(2))  # [1, 2]  ← 意外！默认列表被共享了

# 正确做法
def append_to(item, lst=None):
    if lst is None:
        lst = []
    lst.append(item)
    return lst

print(append_to(1))  # [1]
print(append_to(2))  # [2]  ← 每次都是新列表
```

**原因**：默认参数在函数定义时只被求值一次，之后每次调用都复用同一个对象。

### 2.4 可变参数 *args 和 **kwargs

**\*args**：接收任意数量的位置参数，打包成元组。

```python
def sum_all(*numbers):
    total = 0
    for n in numbers:
        total += n
    return total

print(sum_all(1, 2, 3, 4))  # 10
print(sum_all(10, 20))      # 30
```

**\*\*kwargs**：接收任意数量的关键字参数，打包成字典。

```python
def print_info(**info):
    for key, value in info.items():
        print(f"{key}: {value}")

print_info(name="小明", age=20, city="北京")
# name: 小明
# age: 20
# city: 北京
```

**混合使用**：顺序必须是 普通参数 → \*args → \*\*kwargs。

```python
def example(a, b, *args, **kwargs):
    print(f"a={a}, b={b}")
    print(f"args={args}")
    print(f"kwargs={kwargs}")

example(1, 2, 3, 4, 5, x=10, y=20)
# a=1, b=2
# args=(3, 4, 5)
# kwargs={'x': 10, 'y': 20}
```

### 2.5 参数解包

可以用 `*` 和 `**` 把列表/字典拆开传给函数：

```python
def add(a, b, c):
    return a + b + c

nums = [1, 2, 3]
print(add(*nums))  # 6，把列表拆开成三个参数

info = {'a': 1, 'b': 2, 'c': 3}
print(add(**info))  # 6，把字典拆开成关键字参数
```

---

## 三、返回值

### 3.1 返回多个值

Python 函数可以返回多个值，实际上是返回元组：

```python
def get_info():
    return "小明", 20, "北京"

name, age, city = get_info()
print(name)  # 小明
print(age)   # 20

# 也可以直接接收元组
result = get_info()
print(result)  # ('小明', 20, '北京')
```

### 3.2 提前返回

用 `return` 提前结束函数：

```python
def divide(a, b):
    if b == 0:
        return "除数不能为零"
    return a / b

print(divide(10, 2))  # 5.0
print(divide(10, 0))  # 除数不能为零
```

---

## 四、变量作用域

### 4.1 局部变量 vs 全局变量

```python
x = 10  # 全局变量

def test():
    y = 20  # 局部变量
    print(x)  # 10，可以读取全局变量
    print(y)  # 20

test()
# print(y)  # 错误！y 是局部变量，函数外无法访问
```

### 4.2 global 关键字

要在函数内部**修改**全局变量，需要 `global` 声明：

```python
count = 0

def increment():
    global count
    count += 1

increment()
print(count)  # 1
```

### 4.3 作用域规则（LEGB）

Python 查找变量的顺序：

1. **L**ocal：函数内部
2. **E**nclosing：外层函数（闭包场景）
3. **G**lobal：模块级别
4. **B**uilt-in：内置名称

```python
x = "global"

def outer():
    x = "outer"
    
    def inner():
        x = "inner"
        print(x)  # inner
    
    inner()
    print(x)  # outer

outer()
print(x)  # global
```

---

## 五、匿名函数 lambda

### 5.1 基本用法

`lambda` 用于创建简单的匿名函数，只能包含单个表达式：

```python
# 普通函数
def square(x):
    return x * x

# 等价的 lambda
square_lambda = lambda x: x * x

print(square(5))         # 25
print(square_lambda(5))  # 25
```

### 5.2 常见使用场景

lambda 通常作为参数传给其他函数：

```python
# 按绝对值排序
nums = [-3, 1, -2, 4]
sorted_nums = sorted(nums, key=lambda x: abs(x))
print(sorted_nums)  # [1, -2, -3, 4]

# 按字典的某个值排序
students = [
    {'name': '小明', 'age': 20},
    {'name': '小红', 'age': 18},
    {'name': '小华', 'age': 22},
]
sorted_students = sorted(students, key=lambda s: s['age'])
print([s['name'] for s in sorted_students])  # ['小红', '小明', '小华']
```

---

## 六、文档字符串 docstring

### 6.1 基本用法

用三引号给函数写说明文档：

```python
def calculate_bmi(weight, height):
    """
    计算 BMI 指数。
    
    参数:
        weight (float): 体重（公斤）
        height (float): 身高（米）
    
    返回:
        float: BMI 指数
    """
    return weight / (height ** 2)

# 查看文档
print(calculate_bmi.__doc__)
# 或
help(calculate_bmi)
```

### 6.2 类型提示（Python 3.5+）

用类型注解提高代码可读性：

```python
def greet(name: str, age: int = 18) -> str:
    return f"你好，{name}，你今年{age}岁"

# 注意：类型提示只是说明，Python 不会强制检查
greet("小明")           # 正确
greet("小明", "二十")   # 类型提示建议是 int，但运行时不会报错
```

---

## 七、高阶函数

### 7.1 什么是高阶函数

满足以下条件之一的函数就是高阶函数：

1. **接收函数作为参数**
2. **返回函数作为结果**

这是函数式编程的核心概念。

### 7.2 函数是一等公民

在 Python 中，函数可以像普通值一样被处理：

```python
# 赋值给变量
def square(x):
    return x * x

my_func = square
print(my_func(5))  # 25

# 作为参数传递
def apply(func, value):
    return func(value)

print(apply(square, 5))  # 25
print(apply(lambda x: x + 1, 5))  # 6

# 作为返回值
def get_operator(op):
    if op == "add":
        return lambda x, y: x + y
    elif op == "mul":
        return lambda x, y: x * y

add_func = get_operator("add")
print(add_func(3, 4))  # 7
```

---

## 八、常用高阶函数

### 8.1 map()：映射

对序列中的每个元素应用函数，返回迭代器：

```python
nums = [1, 2, 3, 4, 5]

# 用函数
def double(x):
    return x * 2

result = list(map(double, nums))
print(result)  # [2, 4, 6, 8, 10]

# 用 lambda（更简洁）
result = list(map(lambda x: x * 2, nums))
print(result)  # [2, 4, 6, 8, 10]

# 多个序列
list1 = [1, 2, 3]
list2 = [10, 20, 30]
result = list(map(lambda x, y: x + y, list1, list2))
print(result)  # [11, 22, 33]
```

### 8.2 filter()：过滤

保留序列中使函数返回 `True` 的元素：

```python
nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# 过滤出偶数
evens = list(filter(lambda x: x % 2 == 0, nums))
print(evens)  # [2, 4, 6, 8, 10]

# 过滤出大于 5 的数
big_nums = list(filter(lambda x: x > 5, nums))
print(big_nums)  # [6, 7, 8, 9, 10]

# 过滤掉空字符串
words = ["hello", "", "world", "", "python"]
non_empty = list(filter(lambda s: s, words))
print(non_empty)  # ['hello', 'world', 'python']
```

### 8.3 reduce()：累积

对序列进行累积操作，需要 `functools`：

```python
from functools import reduce

nums = [1, 2, 3, 4, 5]

# 求和
total = reduce(lambda x, y: x + y, nums)
print(total)  # 15

# 求积
product = reduce(lambda x, y: x * y, nums)
print(product)  # 120

# 找最大值
max_val = reduce(lambda x, y: x if x > y else y, nums)
print(max_val)  # 5

# 带初始值
total_with_init = reduce(lambda x, y: x + y, nums, 100)
print(total_with_init)  # 115
```

**reduce 的工作流程**：

```
reduce(lambda x, y: x + y, [1, 2, 3, 4])
→ ((1 + 2) + 3) + 4
→ 10
```

### 8.4 sorted()：排序

接收 `key` 参数自定义排序规则：

```python
# 按绝对值排序
nums = [-5, 3, -1, 4, -2]
sorted_by_abs = sorted(nums, key=abs)
print(sorted_by_abs)  # [-1, -2, 3, 4, -5]

# 按字符串长度排序
words = ["python", "java", "c", "javascript"]
sorted_by_len = sorted(words, key=len)
print(sorted_by_len)  # ['c', 'java', 'python', 'javascript']

# 按字典的某个键排序
students = [
    {'name': '小明', 'score': 85},
    {'name': '小红', 'score': 92},
    {'name': '小华', 'score': 78},
]

# 按分数降序
sorted_students = sorted(students, key=lambda s: s['score'], reverse=True)
print([s['name'] for s in sorted_students])  # ['小红', '小明', '小华']

# 多条件排序：先按分数降序，分数相同按名字升序
students = [
    {'name': '小明', 'score': 85},
    {'name': '小红', 'score': 92},
    {'name': '小华', 'score': 85},
]
sorted_students = sorted(students, key=lambda s: (-s['score'], s['name']))
print([s['name'] for s in sorted_students])  # ['小红', '小华', '小明']
```

### 8.5 zip()：配对

将多个序列对应位置的元素打包成元组：

```python
names = ["小明", "小红", "小华"]
scores = [85, 92, 78]

# 配对
pairs = list(zip(names, scores))
print(pairs)  # [('小明', 85), ('小红', 92), ('小华', 78)]

# 解包
names2, scores2 = zip(*pairs)
print(list(names2))   # ['小明', '小红', '小华']
print(list(scores2))  # [85, 92, 78]

# 配合 dict 使用
score_dict = dict(zip(names, scores))
print(score_dict)  # {'小明': 85, '小红': 92, '小华': 78}

# 长度不一致时，以最短为准
list1 = [1, 2, 3, 4]
list2 = ['a', 'b']
print(list(zip(list1, list2)))  # [(1, 'a'), (2, 'b')]
```

### 8.6 enumerate()：带索引遍历

```python
fruits = ["苹果", "香蕉", "橘子"]

# 默认从 0 开始
for i, fruit in enumerate(fruits):
    print(f"{i}: {fruit}")
# 0: 苹果
# 1: 香蕉
# 2: 橘子

# 自定义起始索引
for i, fruit in enumerate(fruits, start=1):
    print(f"{i}. {fruit}")
# 1. 苹果
# 2. 香蕉
# 3. 橘子
```

### 8.7 any() 和 all()：逻辑判断

```python
# any：只要有一个为 True 就返回 True
print(any([0, 0, 1]))    # True
print(any([0, 0, 0]))    # False
print(any([]))           # False

# all：全部为 True 才返回 True
print(all([1, 1, 1]))    # True
print(all([1, 0, 1]))    # False
print(all([]))           # True

# 配合生成器表达式
nums = [2, 4, 6, 8, 10]
print(all(n % 2 == 0 for n in nums))  # True，全是偶数
print(any(n > 5 for n in nums))       # True，有大于 5 的数
```

---

## 九、自定义高阶函数

### 9.1 函数作为参数

```python
def apply_twice(func, value):
    """对值应用函数两次"""
    return func(func(value))

print(apply_twice(lambda x: x + 1, 5))   # 7
print(apply_twice(lambda x: x * 2, 3))   # 12

def compose(f, g):
    """函数组合：先 g 后 f"""
    return lambda x: f(g(x))

# (x + 1) * 2
add_then_double = compose(lambda x: x * 2, lambda x: x + 1)
print(add_then_double(5))  # 12：(5 + 1) * 2
```

### 9.2 函数作为返回值（闭包基础）

```python
def power_factory(exponent):
    """生成求幂函数"""
    def power(base):
        return base ** exponent
    return power

square = power_factory(2)
cube = power_factory(3)

print(square(5))  # 25
print(cube(5))    # 125
```

### 9.3 函数组合与管道

```python
def pipeline(*functions):
    """创建函数管道：依次执行传入的函数"""
    def pipe(value):
        for func in functions:
            value = func(value)
        return value
    return pipe

# 定义处理步骤
def clean(text):
    return text.strip()

def lower(text):
    return text.lower()

def remove_punctuation(text):
    return ''.join(c for c in text if c.isalnum() or c == ' ')

# 组合成管道
process = pipeline(clean, lower, remove_punctuation)

text = "  Hello, World!  "
print(process(text))  # "hello world"
```

---

## 十、偏函数（Partial）

### 10.1 使用 functools.partial

固定函数的部分参数，生成新函数：

```python
from functools import partial

def power(base, exponent):
    return base ** exponent

# 固定 exponent = 2
square = partial(power, exponent=2)
cube = partial(power, exponent=3)

print(square(5))  # 25
print(cube(5))    # 125

# 固定 base = 2
powers_of_2 = partial(power, 2)
print(powers_of_2(3))   # 8
print(powers_of_2(10))  # 1024
```

### 10.2 应用场景

```python
from functools import partial

# 创建带默认参数的 print
print_no_newline = partial(print, end='')

# 创建整数转换器
int2 = partial(int, base=2)   # 二进制
int16 = partial(int, base=16) # 十六进制

print(int2('1010'))    # 10
print(int16('ff'))     # 255
```

---

## 十一、装饰器基础

装饰器是高阶函数最典型的应用，用于在不修改原函数的前提下扩展功能。

### 11.1 基本结构

```python
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print("函数执行前")
        result = func(*args, **kwargs)
        print("函数执行后")
        return result
    return wrapper

@my_decorator
def say_hello(name):
    print(f"你好，{name}")

say_hello("小明")
# 函数执行前
# 你好，小明
# 函数执行后
```

### 11.2 实用示例：计时装饰器

```python
import time
from functools import wraps

def timer(func):
    @wraps(func)  # 保留原函数的名字和文档
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} 执行时间：{end - start:.4f} 秒")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(1)
    return "完成"

slow_function()
# slow_function 执行时间：1.0012 秒
```

### 11.3 带参数的装饰器

```python
def repeat(times):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(3)
def greet(name):
    print(f"你好，{name}")

greet("小明")
# 你好，小明
# 你好，小明
# 你好，小明
```

---

## 十二、生成器函数

### 12.1 yield 关键字

生成器是一种特殊的函数，用 `yield` 替代 `return`，每次产出一个值后暂停：

```python
def count_up(n):
    i = 1
    while i <= n:
        yield i
        i += 1

for num in count_up(5):
    print(num)
# 1
# 2
# 3
# 4
# 5
```

### 12.2 生成器的优势

**惰性求值**，节省内存：

```python
# 列表：一次性生成所有元素，占用大量内存
big_list = [x * x for x in range(10000000)]  # 占用约 80MB

# 生成器：按需产生，几乎不占内存
big_gen = (x * x for x in range(10000000))   # 占用约 120 字节
```

### 12.3 生成器表达式

类似列表推导式，但用圆括号：

```python
# 列表推导式
squares_list = [x * x for x in range(10)]
print(squares_list)  # [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

# 生成器表达式
squares_gen = (x * x for x in range(10))
print(list(squares_gen))  # [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
```

---

## 十三、递归函数

### 13.1 基本概念

函数调用自身：

```python
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

print(factorial(5))  # 120 = 5 * 4 * 3 * 2 * 1
```

### 13.2 斐波那契数列

```python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

print([fibonacci(i) for i in range(10)])
# [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

### 13.3 使用 lru_cache 优化

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def fibonacci_fast(n):
    if n <= 1:
        return n
    return fibonacci_fast(n - 1) + fibonacci_fast(n - 2)

print(fibonacci_fast(100))  # 瞬间计算完成
```

---

## 十四、要点总结

### 函数基础
- 函数是可重复使用的代码块
- 参数顺序：普通参数 → \*args → \*\*kwargs
- 不要用可变对象做默认参数
- 作用域遵循 LEGB 规则

### 高阶函数
- 接收函数或返回函数的函数
- 内置：map、filter、reduce、sorted、zip、enumerate
- 自定义：组合、管道、装饰器

### 实用技巧
- lambda 用于简单的匿名函数
- 装饰器用于扩展函数功能
- 生成器用于处理大量数据
- 递归配合 lru_cache 避免重复计算

---

## 十五、练习建议

把上面的代码都敲一遍，重点练习：

1. **参数传递**：位置参数、关键字参数、默认参数、\*args、\*\*kwargs
2. **高阶函数**：用 map、filter、sorted 处理列表
3. **自定义高阶函数**：写一个接收函数作为参数的函数
4. **装饰器**：写一个计时装饰器或日志装饰器
5. **生成器**：实现一个无限序列生成器

多动手、多思考，函数是 Python 的核心，掌握好了后续学习会轻松很多。
