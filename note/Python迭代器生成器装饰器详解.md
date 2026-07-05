# Python 迭代器、生成器和装饰器详解

> 这三个概念经常一起出现在 Python 进阶学习中。它们看起来抽象，但本质都围绕一个核心思想：让代码更灵活、更节省资源、更容易复用。

---

## 一、先理解：什么是“可迭代”

在学习迭代器之前，先要理解“可迭代对象”。

在 Python 中，如果一个对象可以被 `for` 循环逐个取出元素，那么它就是可迭代对象，也叫 iterable。

常见的可迭代对象包括：

- 字符串：`"hello"`
- 列表：`[1, 2, 3]`
- 元组：`(1, 2, 3)`
- 字典：`{"name": "Tom", "age": 18}`
- 集合：`{1, 2, 3}`
- 文件对象
- 生成器对象

例如：

```python
names = ["Alice", "Bob", "Charlie"]

for name in names:
    print(name)
```

输出：

```text
Alice
Bob
Charlie
```

这里的列表 `names` 就是一个可迭代对象。

---

## 二、迭代器 Iterator

### 2.1 什么是迭代器

迭代器是一个可以“记住遍历位置”的对象。

它每次只返回一个值，并且知道下一个值在哪里。当所有值都取完以后，它会抛出 `StopIteration` 异常，表示迭代结束。

一个对象如果同时满足下面两个条件，就是迭代器：

1. 实现了 `__iter__()` 方法
2. 实现了 `__next__()` 方法

其中：

- `__iter__()` 返回迭代器对象本身
- `__next__()` 返回下一个元素

### 2.2 使用 iter() 和 next()

`for` 循环背后其实就是在使用 `iter()` 和 `next()`。

```python
numbers = [10, 20, 30]

iterator = iter(numbers)

print(next(iterator))
print(next(iterator))
print(next(iterator))
```

输出：

```text
10
20
30
```

如果继续调用：

```python
print(next(iterator))
```

就会报错：

```text
StopIteration
```

这说明迭代器已经没有下一个值了。

### 2.3 for 循环的本质

下面这段代码：

```python
for item in [1, 2, 3]:
    print(item)
```

可以近似理解为：

```python
items = [1, 2, 3]
iterator = iter(items)

while True:
    try:
        item = next(iterator)
        print(item)
    except StopIteration:
        break
```

所以，`for` 循环并不神秘，它只是自动帮我们不断调用 `next()`，直到遇到 `StopIteration` 为止。

### 2.4 可迭代对象和迭代器的区别

可迭代对象不一定是迭代器。

列表是可迭代对象，但它本身不是迭代器：

```python
numbers = [1, 2, 3]

print(hasattr(numbers, "__iter__"))
print(hasattr(numbers, "__next__"))
```

输出：

```text
True
False
```

通过 `iter()` 可以把可迭代对象转换成迭代器：

```python
numbers = [1, 2, 3]
iterator = iter(numbers)

print(hasattr(iterator, "__iter__"))
print(hasattr(iterator, "__next__"))
```

输出：

```text
True
True
```

总结：

| 类型 | 是否有 `__iter__()` | 是否有 `__next__()` | 例子 |
| --- | --- | --- | --- |
| 可迭代对象 | 有 | 不一定有 | list、tuple、dict、str |
| 迭代器 | 有 | 有 | `iter([1, 2, 3])` |

### 2.5 自定义一个迭代器

下面写一个从 1 数到指定数字的迭代器：

```python
class CountUp:
    def __init__(self, max_number):
        self.max_number = max_number
        self.current = 1

    def __iter__(self):
        return self

    def __next__(self):
        if self.current > self.max_number:
            raise StopIteration

        value = self.current
        self.current += 1
        return value


counter = CountUp(3)

for number in counter:
    print(number)
```

输出：

```text
1
2
3
```

执行过程：

1. `for` 循环先调用 `iter(counter)`
2. `iter(counter)` 会调用 `counter.__iter__()`
3. 每次循环调用 `counter.__next__()`
4. 当 `__next__()` 抛出 `StopIteration` 时，循环结束

### 2.6 迭代器的特点

迭代器有几个重要特点：

- 惰性计算：需要一个值时才计算一个值
- 节省内存：不用一次性把所有数据放进内存
- 有状态：会记住当前遍历到哪里
- 一次性：很多迭代器遍历完以后不能重新从头遍历

例如：

```python
numbers = iter([1, 2, 3])

for number in numbers:
    print(number)

print("第二次遍历")

for number in numbers:
    print(number)
```

输出：

```text
1
2
3
第二次遍历
```

第二次没有输出数字，因为迭代器已经被消耗完了。

---

## 三、生成器 Generator

### 3.1 什么是生成器

生成器是一种特殊的迭代器。

普通函数使用 `return` 返回结果，一旦返回，函数就结束了。

生成器函数使用 `yield` 返回结果。它不会一次性结束，而是会暂停在 `yield` 处，下一次继续执行时，从暂停的位置接着往下走。

只要函数中出现了 `yield`，这个函数就不再是普通函数，而是生成器函数。

### 3.2 第一个生成器

```python
def simple_generator():
    yield 1
    yield 2
    yield 3


gen = simple_generator()

print(next(gen))
print(next(gen))
print(next(gen))
```

输出：

```text
1
2
3
```

继续调用：

```python
print(next(gen))
```

会得到：

```text
StopIteration
```

### 3.3 生成器也可以用 for 循环

生成器本身就是迭代器，所以可以直接用于 `for` 循环：

```python
def simple_generator():
    yield 1
    yield 2
    yield 3


for value in simple_generator():
    print(value)
```

输出：

```text
1
2
3
```

### 3.4 yield 的执行过程

看下面这个例子：

```python
def demo():
    print("开始")
    yield "A"

    print("继续")
    yield "B"

    print("结束")


gen = demo()

print(next(gen))
print(next(gen))
print(next(gen))
```

输出：

```text
开始
A
继续
B
结束
StopIteration
```

执行过程：

1. 调用 `demo()` 时，函数体不会立刻执行，只会返回一个生成器对象
2. 第一次 `next(gen)`，函数开始执行，遇到 `yield "A"` 暂停，并返回 `"A"`
3. 第二次 `next(gen)`，从上次暂停的位置继续执行，遇到 `yield "B"` 暂停，并返回 `"B"`
4. 第三次 `next(gen)`，继续执行到函数结束，抛出 `StopIteration`

### 3.5 生成器为什么节省内存

假设要生成 100 万个数字。

如果使用列表：

```python
numbers = [number for number in range(1_000_000)]
```

这会一次性创建一个包含 100 万个元素的列表，占用较多内存。

如果使用生成器：

```python
def generate_numbers():
    for number in range(1_000_000):
        yield number


numbers = generate_numbers()
```

这里只创建了一个生成器对象。真正的数字会在遍历时一个一个产生。

例如：

```python
for number in generate_numbers():
    if number > 5:
        break
    print(number)
```

输出：

```text
0
1
2
3
4
5
```

虽然理论上可以生成 100 万个数字，但程序只真正产生了前几个值。

### 3.6 生成器表达式

列表推导式使用中括号：

```python
squares = [x * x for x in range(5)]
print(squares)
```

输出：

```text
[0, 1, 4, 9, 16]
```

生成器表达式使用小括号：

```python
squares = (x * x for x in range(5))
print(squares)
```

输出类似：

```text
<generator object <genexpr> at 0x...>
```

想要取值，需要遍历它：

```python
squares = (x * x for x in range(5))

for value in squares:
    print(value)
```

输出：

```text
0
1
4
9
16
```

### 3.7 生成器适合用在哪里

生成器特别适合处理：

- 大文件逐行读取
- 大量数据逐条处理
- 无限序列
- 数据管道
- 不需要一次性拿到全部结果的场景

例如读取大文件：

```python
def read_lines(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            yield line.strip()


for line in read_lines("data.txt"):
    print(line)
```

这样不会一次性把整个文件读入内存，而是每次处理一行。

### 3.8 迭代器和生成器的关系

生成器是迭代器的一种简洁写法。

如果用类写迭代器，需要实现 `__iter__()` 和 `__next__()`：

```python
class CountUp:
    def __init__(self, max_number):
        self.max_number = max_number
        self.current = 1

    def __iter__(self):
        return self

    def __next__(self):
        if self.current > self.max_number:
            raise StopIteration

        value = self.current
        self.current += 1
        return value
```

使用生成器可以写得更简单：

```python
def count_up(max_number):
    current = 1

    while current <= max_number:
        yield current
        current += 1
```

使用方式一样：

```python
for number in count_up(3):
    print(number)
```

输出：

```text
1
2
3
```

---

## 四、装饰器 Decorator

### 4.1 什么是装饰器

装饰器本质上是一个函数。

它的作用是在不修改原函数代码的情况下，给原函数增加额外功能。

可以把装饰器理解成“给函数外面套一层包装”。

比如，原函数只负责做业务：

```python
def say_hello():
    print("hello")
```

如果想在函数执行前后打印日志，直接修改函数当然可以：

```python
def say_hello():
    print("函数开始执行")
    print("hello")
    print("函数执行结束")
```

但如果很多函数都需要这个功能，每个函数都手动加日志，就会重复。装饰器就是用来解决这种问题的。

### 4.2 函数也是对象

理解装饰器之前，要先知道：在 Python 中，函数可以像普通变量一样使用。

```python
def greet():
    print("hello")


func = greet
func()
```

输出：

```text
hello
```

函数也可以作为参数传给另一个函数：

```python
def greet():
    print("hello")


def run_function(func):
    func()


run_function(greet)
```

输出：

```text
hello
```

函数还可以作为返回值：

```python
def outer():
    def inner():
        print("inner function")

    return inner


func = outer()
func()
```

输出：

```text
inner function
```

装饰器正是基于这些能力实现的。

### 4.3 手写一个最简单的装饰器

```python
def my_decorator(func):
    def wrapper():
        print("函数开始执行")
        func()
        print("函数执行结束")

    return wrapper


def say_hello():
    print("hello")


say_hello = my_decorator(say_hello)

say_hello()
```

输出：

```text
函数开始执行
hello
函数执行结束
```

执行过程：

1. `my_decorator(say_hello)` 接收原函数 `say_hello`
2. 在内部定义一个新函数 `wrapper`
3. `wrapper` 中先执行额外功能，再调用原函数
4. 返回 `wrapper`
5. 把 `wrapper` 重新赋值给 `say_hello`

所以此时调用 `say_hello()`，实际调用的是包装后的 `wrapper()`。

### 4.4 @ 语法糖

上面的写法：

```python
say_hello = my_decorator(say_hello)
```

可以用 `@` 简化：

```python
def my_decorator(func):
    def wrapper():
        print("函数开始执行")
        func()
        print("函数执行结束")

    return wrapper


@my_decorator
def say_hello():
    print("hello")


say_hello()
```

这两种写法完全等价。

`@my_decorator` 的含义就是：

```python
say_hello = my_decorator(say_hello)
```

### 4.5 装饰带参数的函数

上面的装饰器只能装饰没有参数的函数。如果原函数有参数，就需要在 `wrapper` 中接收参数。

```python
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print("函数开始执行")
        result = func(*args, **kwargs)
        print("函数执行结束")
        return result

    return wrapper


@my_decorator
def add(a, b):
    return a + b


result = add(3, 5)
print(result)
```

输出：

```text
函数开始执行
函数执行结束
8
```

这里的：

```python
*args, **kwargs
```

表示可以接收任意位置参数和任意关键字参数。

这样装饰器就可以适配大多数函数。

### 4.6 为什么要 return result

如果装饰器内部调用了原函数，但没有返回原函数的结果，外部就拿不到返回值。

错误示例：

```python
def bad_decorator(func):
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)

    return wrapper


@bad_decorator
def add(a, b):
    return a + b


print(add(3, 5))
```

输出：

```text
None
```

正确写法：

```python
def good_decorator(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return result

    return wrapper
```

如果原函数有返回值，装饰器通常也应该把这个返回值继续返回。

### 4.7 使用 functools.wraps 保留原函数信息

普通装饰器会让原函数的名字变成 `wrapper`。

```python
def my_decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


@my_decorator
def say_hello():
    """打招呼函数"""
    print("hello")


print(say_hello.__name__)
print(say_hello.__doc__)
```

输出：

```text
wrapper
None
```

这会影响调试、文档生成和一些框架的行为。

推荐使用 `functools.wraps`：

```python
from functools import wraps


def my_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


@my_decorator
def say_hello():
    """打招呼函数"""
    print("hello")


print(say_hello.__name__)
print(say_hello.__doc__)
```

输出：

```text
say_hello
打招呼函数
```

所以，实际开发中写装饰器时，通常都建议加上 `@wraps(func)`。

### 4.8 带参数的装饰器

有时装饰器本身也需要参数。

例如：根据不同级别打印日志。

```python
from functools import wraps


def log(level):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            print(f"[{level}] 函数 {func.__name__} 开始执行")
            result = func(*args, **kwargs)
            print(f"[{level}] 函数 {func.__name__} 执行结束")
            return result

        return wrapper

    return decorator


@log("INFO")
def add(a, b):
    return a + b


print(add(2, 3))
```

输出：

```text
[INFO] 函数 add 开始执行
[INFO] 函数 add 执行结束
5
```

这里有三层函数：

1. `log(level)` 接收装饰器参数
2. `decorator(func)` 接收被装饰的函数
3. `wrapper(*args, **kwargs)` 接收原函数调用时传入的参数

`@log("INFO")` 的执行过程可以理解为：

```python
add = log("INFO")(add)
```

先执行 `log("INFO")`，得到真正的装饰器 `decorator`，再用它装饰 `add`。

### 4.9 装饰器的常见应用

装饰器在实际开发中非常常见，比如：

- 打印日志
- 统计函数运行时间
- 权限校验
- 参数检查
- 缓存结果
- 事务处理
- Web 框架中的路由注册

#### 示例一：统计函数运行时间

```python
import time
from functools import wraps


def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} 执行耗时：{end - start:.4f} 秒")
        return result

    return wrapper


@timer
def slow_task():
    time.sleep(1)
    return "任务完成"


print(slow_task())
```

输出类似：

```text
slow_task 执行耗时：1.0012 秒
任务完成
```

#### 示例二：简单权限校验

```python
from functools import wraps


def require_admin(func):
    @wraps(func)
    def wrapper(user, *args, **kwargs):
        if user.get("role") != "admin":
            print("权限不足")
            return None

        return func(user, *args, **kwargs)

    return wrapper


@require_admin
def delete_user(user, target_user_id):
    print(f"用户 {user['name']} 删除了用户 {target_user_id}")


admin = {"name": "Alice", "role": "admin"}
guest = {"name": "Bob", "role": "guest"}

delete_user(admin, 1001)
delete_user(guest, 1002)
```

输出：

```text
用户 Alice 删除了用户 1001
权限不足
```

#### 示例三：使用缓存避免重复计算

```python
from functools import wraps


def cache(func):
    data = {}

    @wraps(func)
    def wrapper(*args):
        if args in data:
            print("从缓存中读取")
            return data[args]

        result = func(*args)
        data[args] = result
        return result

    return wrapper


@cache
def multiply(a, b):
    print("正在计算")
    return a * b


print(multiply(3, 4))
print(multiply(3, 4))
```

输出：

```text
正在计算
12
从缓存中读取
12
```

Python 标准库中也有类似功能：

```python
from functools import lru_cache


@lru_cache
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


print(fibonacci(30))
```

---

## 五、三者之间的关系

### 5.1 迭代器和生成器

生成器是迭代器的一种。

它们都可以被 `next()` 调用，也都可以用于 `for` 循环。

区别在于：

- 迭代器可以通过类手动实现
- 生成器通常用 `yield` 快速创建
- 生成器写法更简洁，更适合表达“逐个产生数据”的逻辑

### 5.2 生成器和装饰器

生成器关注的是“怎么一个一个地产生数据”。

装饰器关注的是“怎么在不修改原函数的前提下增强函数功能”。

两者用途不同，但都体现了 Python 中函数和对象的灵活性。

### 5.3 对比总结

| 概念 | 解决的问题 | 核心语法 | 常见用途 |
| --- | --- | --- | --- |
| 迭代器 | 逐个访问数据 | `__iter__()`、`__next__()` | 自定义遍历逻辑 |
| 生成器 | 更简单地创建迭代器 | `yield`、生成器表达式 | 大数据处理、惰性计算 |
| 装饰器 | 给函数增强功能 | `@decorator` | 日志、计时、权限、缓存 |

---

## 六、常见易错点

### 6.1 迭代器遍历完不能自动重来

```python
iterator = iter([1, 2, 3])

print(list(iterator))
print(list(iterator))
```

输出：

```text
[1, 2, 3]
[]
```

第二次为空，因为迭代器已经被消耗完。

如果想重新遍历，可以重新创建迭代器：

```python
numbers = [1, 2, 3]

print(list(iter(numbers)))
print(list(iter(numbers)))
```

### 6.2 生成器函数调用后不会立刻执行

```python
def demo():
    print("开始执行")
    yield 1


gen = demo()
print("生成器已创建")
next(gen)
```

输出：

```text
生成器已创建
开始执行
```

调用 `demo()` 只是创建生成器对象，真正执行发生在 `next(gen)` 或 `for` 遍历时。

### 6.3 装饰器容易忘记返回原函数结果

错误写法：

```python
def decorator(func):
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)

    return wrapper
```

如果原函数有返回值，这样会导致返回 `None`。

推荐写法：

```python
def decorator(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return result

    return wrapper
```

### 6.4 装饰器建议使用 functools.wraps

推荐模板：

```python
from functools import wraps


def decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return result

    return wrapper
```

这个模板在真实项目中很常用。

---

## 七、综合示例：用生成器读取数据，用装饰器统计耗时

下面把生成器和装饰器结合起来。

```python
import time
from functools import wraps


def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} 耗时：{end - start:.4f} 秒")
        return result

    return wrapper


def read_numbers(max_number):
    for number in range(1, max_number + 1):
        yield number


@timer
def calculate_sum(max_number):
    total = 0

    for number in read_numbers(max_number):
        total += number

    return total


result = calculate_sum(1_000_000)
print(result)
```

这个例子中：

- `read_numbers()` 是生成器，负责一个一个地产生数字
- `calculate_sum()` 负责计算总和
- `@timer` 负责统计函数执行时间

三个部分各司其职，代码职责更清晰。

---

## 八、记忆口诀

可以这样记：

- 可迭代对象：能被 `for` 循环遍历的对象
- 迭代器：能被 `next()` 一个一个取值的对象
- 生成器：用 `yield` 写出来的简洁迭代器
- 装饰器：给函数套一层包装，增强功能但不改原函数

一句话总结：

> 迭代器负责“一个一个取”，生成器负责“一个一个生成”，装饰器负责“在函数外面加功能”。

