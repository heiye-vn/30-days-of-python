# Python 上下文管理器与类型注解详解

> 这份笔记面向已经会写基础 Python 代码的学习者。目标不是只记住语法，而是理解：上下文管理器到底帮我们管理什么，`with` 背后发生了什么；类型注解到底能检查什么、不能检查什么，以及怎样把它写得清晰、实用。

---

## 一、上下文管理器

### 1. 什么是上下文管理器

上下文管理器用于管理一段代码执行前后的“进入”和“退出”动作。

最常见的例子是打开文件：

```python
with open("hello.txt", "w", encoding="utf-8") as file:
    file.write("Hello, Python")
```

这段代码的重点不是“打开文件”本身，而是：

1. 进入代码块前，打开文件。
2. 执行代码块中的写入逻辑。
3. 离开代码块时，无论是否发生异常，都关闭文件。

也就是说，上下文管理器特别适合处理这类资源：

- 文件
- 网络连接
- 数据库连接
- 线程锁
- 临时修改某个状态
- 需要开始和结束配对出现的操作

如果不用 `with`，文件操作通常要写成这样：

```python
file = open("hello.txt", "w", encoding="utf-8")
try:
    file.write("Hello, Python")
finally:
    file.close()
```

`with` 本质上就是把这种“进入、执行、退出”的模式标准化了。

---

### 2. 为什么需要上下文管理器

很多资源必须被正确释放。如果忘记释放，程序可能出现隐藏问题。

例如：

```python
file = open("data.txt", "r", encoding="utf-8")
content = file.read()
# 忘记 file.close()
```

这段代码在小程序里可能看不出问题，但在长期运行的服务中，可能导致文件句柄泄漏。

再看数据库连接：

```python
connection = create_connection()
cursor = connection.cursor()
cursor.execute("select * from users")
# 如果中间报错，connection 可能没有关闭
connection.close()
```

如果中间 `execute` 报错，后面的 `close()` 不会执行。上下文管理器可以保证退出动作更可靠。

---

### 3. `with` 的基本语法

```python
with 上下文管理器对象 as 变量名:
    代码块
```

例如：

```python
with open("data.txt", "r", encoding="utf-8") as f:
    text = f.read()

print(text)
```

这里：

- `open(...)` 返回一个文件对象。
- 文件对象本身就是上下文管理器。
- `as f` 得到的是进入上下文后返回的对象。
- 缩进代码块执行结束后，文件会自动关闭。

可以验证文件是否关闭：

```python
with open("data.txt", "r", encoding="utf-8") as f:
    print(f.closed)  # False

print(f.closed)      # True
```

---

### 4. `with` 背后的协议：`__enter__` 和 `__exit__`

一个对象只要实现了两个特殊方法，就可以被 `with` 使用：

```python
class MyContext:
    def __enter__(self):
        print("进入上下文")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print("退出上下文")
```

使用它：

```python
with MyContext() as ctx:
    print("执行代码块")
```

输出：

```text
进入上下文
执行代码块
退出上下文
```

执行顺序可以理解为：

```python
manager = MyContext()
ctx = manager.__enter__()
try:
    print("执行代码块")
finally:
    manager.__exit__(...)
```

注意：

- `__enter__()` 在进入 `with` 代码块前执行。
- `__enter__()` 的返回值会赋给 `as` 后面的变量。
- `__exit__()` 在离开 `with` 代码块时执行。
- 即使代码块中发生异常，`__exit__()` 仍然会执行。

---

### 5. `__enter__` 返回什么

`__enter__` 可以返回 `self`，也可以返回其他对象。

返回 `self` 的例子：

```python
class Printer:
    def __enter__(self):
        print("准备打印")
        return self

    def print_message(self, message):
        print(message)

    def __exit__(self, exc_type, exc_value, traceback):
        print("结束打印")


with Printer() as printer:
    printer.print_message("你好")
```

返回其他对象的例子：

```python
class ListBuilder:
    def __enter__(self):
        self.items = []
        return self.items

    def __exit__(self, exc_type, exc_value, traceback):
        print("最终列表：", self.items)


with ListBuilder() as items:
    items.append("Python")
    items.append("Type Hints")
```

这里 `items` 不是 `ListBuilder` 实例本身，而是 `__enter__` 返回的列表。

---

### 6. `__exit__` 的三个异常参数

`__exit__` 方法的完整形式是：

```python
def __exit__(self, exc_type, exc_value, traceback):
    ...
```

三个参数含义如下：

| 参数 | 含义 |
| --- | --- |
| `exc_type` | 异常类型，例如 `ValueError` |
| `exc_value` | 异常对象，例如 `ValueError("xxx")` |
| `traceback` | 异常调用栈信息 |

如果 `with` 代码块没有发生异常，这三个参数都是 `None`。

示例：

```python
class DebugContext:
    def __enter__(self):
        print("进入")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print("异常类型：", exc_type)
        print("异常对象：", exc_value)
        print("退出")


with DebugContext():
    result = 10 / 0
```

输出大致如下：

```text
进入
异常类型： <class 'ZeroDivisionError'>
异常对象： division by zero
退出
Traceback ...
ZeroDivisionError: division by zero
```

你会发现：`__exit__` 执行了，但异常仍然继续向外抛出。

---

### 7. `__exit__` 是否吞掉异常

`__exit__` 的返回值决定异常是否继续传播。

如果返回 `True`，异常会被“吞掉”：

```python
class IgnoreZeroDivision:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is ZeroDivisionError:
            print("捕获并忽略除零错误")
            return True


with IgnoreZeroDivision():
    print(10 / 0)

print("程序继续执行")
```

输出：

```text
捕获并忽略除零错误
程序继续执行
```

如果 `__exit__` 返回 `False` 或者什么都不返回，异常会继续抛出。

实际开发中要谨慎吞异常。除非你非常确定这个异常可以被安全忽略，否则让异常继续暴露更好。

---

### 8. 实战示例：计时器上下文管理器

```python
import time


class Timer:
    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.end = time.perf_counter()
        self.elapsed = self.end - self.start
        print(f"耗时：{self.elapsed:.4f} 秒")


with Timer():
    total = sum(range(10_000_000))
```

这个上下文管理器管理的不是文件，而是“一段代码的计时状态”。

如果希望在代码块外拿到耗时：

```python
with Timer() as timer:
    total = sum(range(10_000_000))

print(timer.elapsed)
```

---

### 9. 实战示例：临时修改工作目录

```python
from pathlib import Path
import os


class ChangeDirectory:
    def __init__(self, target_dir):
        self.target_dir = Path(target_dir)
        self.original_dir = None

    def __enter__(self):
        self.original_dir = Path.cwd()
        os.chdir(self.target_dir)
        return self.target_dir

    def __exit__(self, exc_type, exc_value, traceback):
        os.chdir(self.original_dir)


print("原目录：", Path.cwd())

with ChangeDirectory("note") as current:
    print("临时目录：", Path.cwd())

print("恢复目录：", Path.cwd())
```

这个例子体现了上下文管理器的一个重要用途：临时改变某种全局状态，并确保最后恢复。

---

### 10. 使用 `contextlib.contextmanager` 简化写法

如果不想写一个完整的类，可以使用标准库 `contextlib`。

```python
from contextlib import contextmanager


@contextmanager
def simple_context():
    print("进入")
    try:
        yield "资源对象"
    finally:
        print("退出")


with simple_context() as resource:
    print(resource)
```

输出：

```text
进入
资源对象
退出
```

这里的关键是 `yield`：

- `yield` 前面的代码相当于 `__enter__`。
- `yield` 后面的代码相当于 `__exit__`。
- `yield` 出去的值会赋给 `as` 后面的变量。

更实际的计时器写法：

```python
from contextlib import contextmanager
import time


@contextmanager
def timer():
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        print(f"耗时：{elapsed:.4f} 秒")


with timer():
    sum(range(5_000_000))
```

如果只是简单的前后处理，`@contextmanager` 很方便；如果上下文对象本身有较多状态和方法，用类更清晰。

---

### 11. 同时管理多个上下文

可以在一个 `with` 语句中管理多个上下文：

```python
with open("input.txt", "r", encoding="utf-8") as source, \
     open("output.txt", "w", encoding="utf-8") as target:
    content = source.read()
    target.write(content.upper())
```

也可以写成嵌套：

```python
with open("input.txt", "r", encoding="utf-8") as source:
    with open("output.txt", "w", encoding="utf-8") as target:
        content = source.read()
        target.write(content.upper())
```

多个上下文的进入顺序是从左到右，退出顺序是从右到左。

---

### 12. 动态数量的上下文：`ExitStack`

有时你不知道要打开多少个文件，例如文件路径来自列表。

这时可以用 `contextlib.ExitStack`：

```python
from contextlib import ExitStack


files = ["a.txt", "b.txt", "c.txt"]

with ExitStack() as stack:
    opened_files = [
        stack.enter_context(open(name, "r", encoding="utf-8"))
        for name in files
    ]

    for file in opened_files:
        print(file.read())
```

`ExitStack` 会记录所有进入的上下文，并在退出时按相反顺序清理它们。

---

### 13. 异步上下文管理器

在异步编程中，可以使用 `async with`。

异步上下文管理器需要实现：

- `__aenter__`
- `__aexit__`

示例：

```python
import asyncio


class AsyncConnection:
    async def __aenter__(self):
        print("异步连接开始")
        await asyncio.sleep(1)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        print("异步连接关闭")
        await asyncio.sleep(1)


async def main():
    async with AsyncConnection() as connection:
        print("使用连接")


asyncio.run(main())
```

真实项目中，异步数据库连接、异步 HTTP 客户端经常使用 `async with`。

---

### 14. 上下文管理器常见误区

#### 误区 1：以为 `with` 只能用于文件

文件只是最常见的例子。只要有“开始”和“结束”成对出现的逻辑，都可以考虑上下文管理器。

#### 误区 2：在 `__exit__` 中随便返回 `True`

返回 `True` 会吞掉异常。除非你明确知道异常可以忽略，否则不要这样做。

#### 误区 3：把业务逻辑全塞进上下文管理器

上下文管理器应该主要负责资源管理或状态管理，而不是承担复杂业务逻辑。

#### 误区 4：忘记 `@contextmanager` 里要用 `try...finally`

不推荐这样写：

```python
@contextmanager
def bad_context():
    print("进入")
    yield
    print("退出")
```

如果 `yield` 之后的代码块报错，后面的 `print("退出")` 不一定按预期执行。更稳妥的写法是：

```python
@contextmanager
def good_context():
    print("进入")
    try:
        yield
    finally:
        print("退出")
```

---

## 二、类型注解

### 1. 什么是类型注解

类型注解是给变量、函数参数、函数返回值、类属性等位置标明类型的一种语法。

例如：

```python
def add(a: int, b: int) -> int:
    return a + b
```

这里：

- `a: int` 表示参数 `a` 期望是整数。
- `b: int` 表示参数 `b` 期望是整数。
- `-> int` 表示函数返回值期望是整数。

类型注解不是强制类型检查。Python 运行时默认不会因为类型注解而拒绝错误类型。

```python
def greet(name: str) -> str:
    return "Hello, " + name


print(greet("Alice"))  # 正常
print(greet(123))      # 运行时会在字符串拼接处报错，不是因为注解本身报错
```

类型注解主要用于：

- 提高代码可读性。
- 帮助编辑器自动补全。
- 帮助工具发现潜在错误，例如 mypy、pyright。
- 让大型项目的接口更清晰。

---

### 2. Typing 模块

Python 内置的简单类型（int、str、float、bool、bytes、None）可以直接使用，但更复杂的类型需要借助 typing 模块。

`typing` 模块是**类型提示（Type Hints）**的标准库。

**核心作用：为代码添加类型注解，提升可读性和工具支持，但不影响运行时行为**。

### 3. 变量类型注解

基本写法：

```python
age: int = 18
name: str = "Alice"
height: float = 1.68
is_active: bool = True
```

也可以先声明，后赋值：

```python
count: int
count = 10
```

如果类型很明显，简单变量通常不一定要写注解：

```python
name = "Alice"
age = 18
```

更值得写注解的是类型不明显的地方：

```python
users: list[str] = []
scores: dict[str, int] = {}
```

如果不写注解，空列表 `[]` 的元素类型不明确，类型检查工具很难知道以后应该放什么。

---

### 4. 函数参数和返回值注解

```python
def repeat(text: str, times: int) -> str:
    return text * times
```

调用：

```python
message = repeat("Hi", 3)
print(message)  # HiHiHi
```

没有返回值的函数，返回类型通常写 `None`：

```python
def log(message: str) -> None:
    print(f"[LOG] {message}")
```

注意：如果函数没有显式 `return`，它实际返回 `None`。

```python
def do_something() -> None:
    print("working")
```

---

### 5. 常见内置类型注解

Python 3.9 之后，可以直接用内置集合类型写注解：

```python
names: list[str] = ["Alice", "Bob"]
scores: dict[str, int] = {"Alice": 95, "Bob": 88}
point: tuple[int, int] = (10, 20)
unique_ids: set[int] = {1, 2, 3}
```

含义如下：

| 注解 | 含义 |
| --- | --- |
| `list[str]` | 字符串列表 |
| `dict[str, int]` | 键是字符串，值是整数的字典 |
| `tuple[int, int]` | 两个整数组成的元组 |
| `set[int]` | 整数组成的集合 |

元组还可以表示不定长度：

```python
numbers: tuple[int, ...] = (1, 2, 3, 4)
```

`tuple[int, ...]` 表示这个元组可以有任意多个元素，但每个元素都是 `int`。

---

### 6. `Any`：任意类型

`Any` 表示任何类型都可以。

```python
from typing import Any


def print_value(value: Any) -> None:
    print(value)
```

`Any` 很灵活，但也会削弱类型检查。

```python
from typing import Any


data: Any = "hello"
data = 123
data = {"name": "Alice"}
```

类型检查工具通常不会对 `Any` 做严格检查。所以不要为了省事到处写 `Any`。它更适合这些场景：

- 处理第三方库返回的动态数据。
- 迁移旧代码时暂时兜底。
- 某个函数确实可以接受任意类型。

---

### 7. `Union` 和 `|`：多个可能类型

如果一个值可能是多种类型，可以使用联合类型。

Python 3.10 之后推荐写法：

```python
def normalize_id(value: int | str) -> str:
    return str(value)
```

Python 3.9 及之前的写法：

```python
from typing import Union


def normalize_id(value: Union[int, str]) -> str:
    return str(value)
```

这两种含义相同：`value` 可以是 `int`，也可以是 `str`。

---

### 8. `Optional`：可能为 `None`

`Optional[str]` 表示值可以是 `str`，也可以是 `None`。

```python
from typing import Optional


def find_user(user_id: int) -> Optional[str]:
    if user_id == 1:
        return "Alice"
    return None
```

Python 3.10 之后更推荐：

```python
def find_user(user_id: int) -> str | None:
    if user_id == 1:
        return "Alice"
    return None
```

`Optional[str]` 和 `str | None` 含义一样。

常见错误是忘记处理 `None`：

```python
name = find_user(2)
print(name.upper())  # 如果 name 是 None，这里会报错
```

更安全的写法：

```python
name = find_user(2)
if name is not None:
    print(name.upper())
else:
    print("用户不存在")
```

---

### 9. `Literal`：限定具体取值

如果一个参数只能取几个固定值，可以用 `Literal`。

```python
from typing import Literal


Mode = Literal["read", "write", "append"]


def open_resource(mode: Mode) -> None:
    print(f"打开模式：{mode}")


open_resource("read")   # 合法
open_resource("delete") # 类型检查工具会提示错误
```

`Literal` 适合描述有限的字符串、数字、布尔值选项。

---

### 10. 类型别名

如果一个类型写起来很长，可以起别名。

```python
UserId = int
UserName = str


def get_user_name(user_id: UserId) -> UserName:
    return "Alice"
```

复杂一点的例子：

```python
JsonValue = str | int | float | bool | None | list["JsonValue"] | dict[str, "JsonValue"]
```

不过递归类型对初学者来说不必强求，知道类型别名可以提高可读性即可。

Python 3.12 引入了更明确的 `type` 语句：

```python
type UserId = int
type ScoreMap = dict[str, int]
```

如果你的项目还要兼容 Python 3.11 或更早版本，就不要使用这种新语法。

---

### 11. `Callable`：函数类型

函数也可以作为参数传递。

```python
from collections.abc import Callable


def apply_twice(func: Callable[[int], int], value: int) -> int:
    return func(func(value))


def add_one(x: int) -> int:
    return x + 1


print(apply_twice(add_one, 10))  # 12
```

`Callable[[int], int]` 表示：

- 这是一个可调用对象。
- 它接收一个 `int` 参数。
- 它返回一个 `int`。

多个参数的函数：

```python
from collections.abc import Callable


Calculator = Callable[[int, int], int]


def calculate(a: int, b: int, operation: Calculator) -> int:
    return operation(a, b)
```

---

### 12. `Iterable`、`Sequence`、`Mapping`

写函数参数类型时，不一定总要写具体容器，比如 `list[str]`。

如果函数只需要遍历，可以写 `Iterable[str]`：

```python
from collections.abc import Iterable


def join_names(names: Iterable[str]) -> str:
    return ", ".join(names)
```

这样列表、元组、集合都可以传入：

```python
join_names(["Alice", "Bob"])
join_names(("Alice", "Bob"))
join_names({"Alice", "Bob"})
```

如果函数需要按索引访问，可以写 `Sequence[str]`：

```python
from collections.abc import Sequence


def first_item(items: Sequence[str]) -> str:
    return items[0]
```

如果函数只需要读取字典式映射，可以写 `Mapping[str, int]`：

```python
from collections.abc import Mapping


def show_scores(scores: Mapping[str, int]) -> None:
    for name, score in scores.items():
        print(name, score)
```

一般原则：

- 参数类型尽量写宽一点，只要求你真正需要的能力。
- 返回值类型可以写具体一点，让调用者更清楚拿到什么。

---

### 13. `TypedDict`：给字典规定结构

普通字典注解只能描述键和值的类型：

```python
user: dict[str, str] = {
    "name": "Alice",
    "email": "alice@example.com",
}
```

但它不能表达“必须有 name 和 email 两个键”。

可以用 `TypedDict`：

```python
from typing import TypedDict


class User(TypedDict):
    name: str
    email: str
    age: int


def send_email(user: User) -> None:
    print(f"发送邮件给 {user['name']}：{user['email']}")


alice: User = {
    "name": "Alice",
    "email": "alice@example.com",
    "age": 18,
}
```

如果少写字段，类型检查工具会提示：

```python
bob: User = {
    "name": "Bob",
    "email": "bob@example.com",
    # 缺少 age
}
```

部分字段可选时，可以这样写：

```python
from typing import NotRequired, TypedDict


class UserProfile(TypedDict):
    name: str
    email: str
    bio: NotRequired[str]
```

---

### 14. `Protocol`：按能力描述类型

有时我们不关心对象属于哪个类，只关心它有没有某些方法。

```python
from typing import Protocol


class SupportsClose(Protocol):
    def close(self) -> None:
        ...


def close_resource(resource: SupportsClose) -> None:
    resource.close()
```

任何有 `close()` 方法的对象，都可以被视为 `SupportsClose`。

```python
class FileLike:
    def close(self) -> None:
        print("关闭文件")


class Connection:
    def close(self) -> None:
        print("关闭连接")


close_resource(FileLike())
close_resource(Connection())
```

这叫结构化类型：看对象“长什么样”，而不只看它“继承自谁”。

---

### 15. 泛型：让类型保持关联

看一个普通函数：

```python
def first(items: list[int]) -> int:
    return items[0]
```

它只能处理 `list[int]`。如果想让它既能处理 `list[int]`，也能处理 `list[str]`，同时返回类型和元素类型保持一致，就需要泛型。

```python
from typing import TypeVar


T = TypeVar("T")


def first(items: list[T]) -> T:
    return items[0]
```

现在：

```python
number = first([1, 2, 3])        # 类型推断为 int
name = first(["Alice", "Bob"])   # 类型推断为 str
```

泛型的重点是“类型之间有关系”。

再看一个例子：

```python
from typing import TypeVar


T = TypeVar("T")


def choose(left: T, right: T) -> T:
    return left
```

这表示：

- `left` 和 `right` 应该是同一种类型。
- 返回值也是这种类型。

---

### 16. 泛型类

自己写容器类时，也可以使用泛型。

```python
from typing import Generic, TypeVar


T = TypeVar("T")


class Box(Generic[T]):
    def __init__(self, value: T):
        self.value = value

    def get(self) -> T:
        return self.value


int_box = Box[int](123)
str_box = Box[str]("hello")

number = int_box.get()  # int
text = str_box.get()    # str
```

Python 3.12 支持更简洁的泛型类语法：

```python
class Box[T]:
    def __init__(self, value: T):
        self.value = value

    def get(self) -> T:
        return self.value
```

如果项目需要兼容旧版本，仍然使用 `Generic` 和 `TypeVar` 更稳妥。

---

### 17. `Self`：返回当前类实例

链式调用中，经常需要返回 `self`。

```python
from typing import Self


class Query:
    def __init__(self):
        self.conditions: list[str] = []

    def where(self, condition: str) -> Self:
        self.conditions.append(condition)
        return self

    def build(self) -> str:
        return " and ".join(self.conditions)


query = Query().where("age > 18").where("active = true")
print(query.build())
```

`Self` 表示返回当前类的实例，特别适合链式 API。

---

### 18. `ClassVar` 和实例属性

类属性和实例属性不一样。

```python
from typing import ClassVar


class User:
    count: ClassVar[int] = 0

    def __init__(self, name: str):
        self.name = name
        User.count += 1
```

`count` 是类属性，所有实例共享。

`name` 是实例属性，每个对象各有一份。

`ClassVar[int]` 告诉类型检查工具：这个属性属于类，不应该当作实例字段来处理。

---

### 19. `Final`：不希望被重新赋值

```python
from typing import Final


MAX_RETRY: Final[int] = 3
```

`Final` 表示这个名字不应该再被重新赋值。

```python
MAX_RETRY = 5  # 类型检查工具会提示
```

注意：运行时 Python 仍然允许重新赋值。`Final` 主要是给检查工具和读代码的人看的。

---

### 20. `Annotated`：给类型附加元信息

`Annotated` 可以在类型之外附加额外信息。

```python
from typing import Annotated


Age = Annotated[int, "must be >= 0"]


def set_age(age: Age) -> None:
    print(age)
```

单独使用时，`Annotated` 对运行时没有特殊效果。它通常配合框架使用，例如 FastAPI、Pydantic 等。

示意：

```python
from typing import Annotated


UserId = Annotated[int, "database primary key"]
```

---

### 21. `overload`：同一个函数的多种调用形式

有些函数根据参数不同返回不同类型。

```python
from typing import overload


@overload
def parse(value: int) -> int:
    ...


@overload
def parse(value: str) -> str:
    ...


def parse(value: int | str) -> int | str:
    return value
```

`@overload` 只用于类型检查，真正运行的是最后那个没有 `@overload` 的实现。

一个更实际的例子：

```python
from typing import overload


@overload
def get_item(index: int) -> str:
    ...


@overload
def get_item(index: slice) -> list[str]:
    ...


def get_item(index: int | slice) -> str | list[str]:
    data = ["a", "b", "c"]
    return data[index]
```

当传入 `int` 时，返回 `str`；传入 `slice` 时，返回 `list[str]`。

---

### 22. `NewType`：区分含义不同的相同底层类型

用户 ID 和商品 ID 都可能是 `int`，但它们的业务含义不同。

```python
from typing import NewType


UserId = NewType("UserId", int)
ProductId = NewType("ProductId", int)


def get_user(user_id: UserId) -> str:
    return f"user:{user_id}"


uid = UserId(1)
pid = ProductId(1)

get_user(uid)  # 合法
get_user(pid)  # 类型检查工具会提示
```

运行时 `UserId(1)` 基本还是一个整数，但类型检查工具会把它看成更具体的类型。

---

### 23. 前向引用与 `from __future__ import annotations`

有时类的方法需要返回类自身：

```python
class Node:
    def __init__(self, value: int):
        self.value = value
        self.next: Node | None = None
```

在某些 Python 版本中，类体还没定义完就引用 `Node`，可能会出问题。可以使用字符串：

```python
class Node:
    def __init__(self, value: int):
        self.value = value
        self.next: "Node | None" = None
```

也可以在文件开头添加：

```python
from __future__ import annotations
```

这样注解会延迟求值，写类型时更方便。

---

### 24. 类型注解不会自动校验运行时数据

下面的代码可以运行到函数内部：

```python
def double(value: int) -> int:
    return value * 2


print(double("ha"))
```

输出：

```text
haha
```

虽然 `value` 标注为 `int`，但是 Python 没有自动阻止传入字符串。

如果需要运行时校验，要自己写判断，或者使用 Pydantic 这类库。

```python
def double(value: int) -> int:
    if not isinstance(value, int):
        raise TypeError("value must be int")
    return value * 2
```

所以要区分：

- 类型注解：给人、编辑器、静态检查工具看。
- 运行时校验：程序执行时真正检查数据是否合法。

---

### 25. 使用类型检查工具

常见工具：

- mypy
- pyright
- basedpyright
- PyCharm 内置检查
- VS Code Pylance

安装 mypy：

```bash
pip install mypy
```

检查文件：

```bash
mypy app.py
```

安装 pyright：

```bash
pip install pyright
```

检查项目：

```bash
pyright
```

类型注解本身不会让代码更安全，真正让它发挥作用的是：

1. 认真写清楚接口类型。
2. 使用类型检查工具。
3. 不滥用 `Any`。
4. 对 `None`、字典结构、回调函数等容易出错的位置重点标注。

---

### 26. 类型注解的推荐实践

#### 推荐 1：函数签名优先写

比起给每个局部变量都写类型，先给函数参数和返回值写注解更重要。

```python
def create_user(name: str, age: int) -> dict[str, str | int]:
    return {"name": name, "age": age}
```

函数签名是代码的接口，最值得清晰。

#### 推荐 2：空容器最好写注解

```python
tasks: list[str] = []
user_scores: dict[str, int] = {}
```

否则工具不知道里面将来要放什么。

#### 推荐 3：不要到处写 `Any`

```python
from typing import Any


def process(data: Any) -> Any:
    return data
```

这基本等于放弃类型检查。除非你有明确理由，否则尽量写更具体的类型。

#### 推荐 4：参数用抽象类型，返回用具体类型

```python
from collections.abc import Iterable


def normalize_names(names: Iterable[str]) -> list[str]:
    return [name.strip().title() for name in names]
```

参数写 `Iterable[str]`，表示只需要能遍历。

返回写 `list[str]`，表示调用者确实会拿到列表。

#### 推荐 5：显式处理 `None`

```python
def get_email(user_id: int) -> str | None:
    if user_id == 1:
        return "alice@example.com"
    return None


email = get_email(2)
if email is None:
    print("没有邮箱")
else:
    print(email.lower())
```

这能避免很多 `NoneType has no attribute ...` 错误。

---

## 三、把上下文管理器和类型注解结合起来

### 1. 给上下文管理器类加类型注解

```python
from types import TracebackType
from typing import Self


class Timer:
    def __enter__(self) -> Self:
        import time

        self._start: float = time.perf_counter()
        self.elapsed: float = 0.0
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        import time

        self.elapsed = time.perf_counter() - self._start
        print(f"耗时：{self.elapsed:.4f} 秒")


with Timer() as timer:
    sum(range(1_000_000))

print(timer.elapsed)
```

这里有几个重点：

- `__enter__` 返回 `Self`，表示返回当前上下文对象。
- `exc_type` 可能是异常类型，也可能是 `None`。
- `exc_value` 可能是异常对象，也可能是 `None`。
- `traceback` 可以用 `types.TracebackType | None` 标注。

---

### 2. 使用 `AbstractContextManager`

如果你要声明一个参数“必须是上下文管理器”，可以使用：

```python
from contextlib import AbstractContextManager


def use_context(manager: AbstractContextManager[str]) -> None:
    with manager as value:
        print(value.upper())
```

`AbstractContextManager[str]` 表示进入上下文后得到的是 `str`。

示例：

```python
from contextlib import AbstractContextManager, contextmanager
from collections.abc import Iterator


@contextmanager
def message_context() -> Iterator[str]:
    print("进入")
    try:
        yield "hello"
    finally:
        print("退出")


def use_context(manager: AbstractContextManager[str]) -> None:
    with manager as value:
        print(value.upper())


use_context(message_context())
```

---

### 3. 给 `@contextmanager` 写类型注解

被 `@contextmanager` 装饰的函数通常标注为 `Iterator[T]` 或 `Generator[T, None, None]`。

简单写法：

```python
from collections.abc import Iterator
from contextlib import contextmanager


@contextmanager
def managed_number() -> Iterator[int]:
    print("准备数字")
    try:
        yield 100
    finally:
        print("清理数字")


with managed_number() as number:
    print(number + 1)
```

更完整写法：

```python
from collections.abc import Generator
from contextlib import contextmanager


@contextmanager
def managed_text() -> Generator[str, None, None]:
    yield "hello"
```

含义是：

- `str`：`yield` 产生的类型。
- 第一个 `None`：外部通过 `send()` 发送进来的类型，一般不用。
- 第二个 `None`：生成器最终返回的类型，一般也是 `None`。

初学阶段建议用 `Iterator[T]`，更容易理解。

---

### 4. 给异步上下文管理器写类型注解

```python
from types import TracebackType
from typing import Self


class AsyncResource:
    async def __aenter__(self) -> Self:
        print("打开异步资源")
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        print("关闭异步资源")
```

如果用 `@asynccontextmanager`：

```python
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager


@asynccontextmanager
async def async_message() -> AsyncIterator[str]:
    print("进入")
    try:
        yield "hello"
    finally:
        print("退出")
```

---

## 四、综合案例

### 案例：读取文件、统计单词、记录耗时

```python
from collections.abc import Iterable
from contextlib import contextmanager
from pathlib import Path
from time import perf_counter
from typing import TypedDict


class WordStats(TypedDict):
    total: int
    unique: int


@contextmanager
def timer(label: str):
    start = perf_counter()
    try:
        yield
    finally:
        elapsed = perf_counter() - start
        print(f"{label} 耗时：{elapsed:.4f} 秒")


def read_words(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    return text.split()


def calculate_stats(words: Iterable[str]) -> WordStats:
    word_list = list(words)
    return {
        "total": len(word_list),
        "unique": len(set(word_list)),
    }


def main() -> None:
    path = Path("article.txt")

    with timer("统计单词"):
        words = read_words(path)
        stats = calculate_stats(words)

    print(f"总词数：{stats['total']}")
    print(f"不重复词数：{stats['unique']}")


if __name__ == "__main__":
    main()
```

这个例子中：

- `timer` 是上下文管理器，用来管理计时逻辑。
- `Path` 表示路径类型。
- `read_words` 返回 `list[str]`。
- `calculate_stats` 接收 `Iterable[str]`，返回结构化字典 `WordStats`。
- `main` 没有返回值，所以标注为 `None`。

---

## 五、学习路线建议

### 上下文管理器学习顺序

1. 先熟练使用 `with open(...)`。
2. 理解 `try...finally` 和资源释放。
3. 学会 `__enter__`、`__exit__`。
4. 学会 `contextlib.contextmanager`。
5. 再了解 `ExitStack`、`async with`。

### 类型注解学习顺序

1. 先给函数参数和返回值写基础类型。
2. 学会 `list[str]`、`dict[str, int]`、`tuple[int, ...]`。
3. 学会 `str | None` 和 `int | str`。
4. 学会 `Callable`、`Iterable`、`Mapping`。
5. 学会 `TypedDict`、`Protocol`、泛型。
6. 最后再看 `overload`、`Annotated`、`NewType` 等进阶工具。

---

## 六、快速总结

### 上下文管理器

上下文管理器解决的是“进入前准备、退出后清理”的问题。

核心协议：

```python
def __enter__(self):
    ...

def __exit__(self, exc_type, exc_value, traceback):
    ...
```

常见用途：

- 自动关闭文件。
- 自动关闭数据库连接。
- 自动释放锁。
- 临时修改状态后恢复。
- 统计代码块耗时。

### 类型注解

类型注解解决的是“代码接口是否清楚、类型关系是否明确”的问题。

常见写法：

```python
def func(name: str, age: int) -> str:
    return f"{name}: {age}"
```

重要原则：

- 类型注解默认不在运行时强制检查。
- 类型注解要配合 mypy、pyright 等工具才更有价值。
- 函数签名最值得写清楚。
- 少用 `Any`。
- 对可能为 `None` 的值要显式处理。
- 参数类型可以适当抽象，返回类型尽量明确。

---

## 七、练习题

### 练习 1：写一个日志上下文管理器

要求：

- 进入时打印 `开始执行：任务名`。
- 退出时打印 `结束执行：任务名`。
- 即使代码块报错，也要打印结束信息。

参考接口：

```python
with log_task("导入数据"):
    print("正在导入...")
```

可以分别用类和 `@contextmanager` 实现一遍。

### 练习 2：写一个临时环境变量上下文管理器

要求：

- 进入时设置某个环境变量。
- 退出时恢复原来的值。
- 如果原来没有这个环境变量，退出时删除它。

提示：使用 `os.environ`。

### 练习 3：给函数补全类型注解

```python
def filter_active_users(users):
    return [user for user in users if user["active"]]
```

可以尝试使用 `TypedDict` 描述用户结构。

### 练习 4：写一个泛型函数

要求：

- 函数名：`last`
- 接收一个非空列表。
- 返回列表最后一个元素。
- 返回类型要和列表元素类型一致。

提示：使用 `TypeVar`。
