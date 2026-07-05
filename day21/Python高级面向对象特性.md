# Python 高级面向对象特性

> 这一篇接在“类与对象”的基础之后，重点学习 Python 中更高级、更接近真实项目的面向对象写法。学完之后，你会更容易读懂框架源码，也能写出接口清晰、扩展性更好的类。

---

## 目录

1. [从普通类到高级类](#一从普通类到高级类)
2. [`property` 属性封装](#二property-属性封装)
3. [`dataclass` 数据类](#三dataclass-数据类)
4. [抽象类 ABC](#四抽象类-abc)
5. [多重继承与 MRO](#五多重继承与-mro)
6. [常用魔术方法](#六常用魔术方法)
7. [上下文管理器](#七上下文管理器)
8. [描述符 Descriptor](#八描述符-descriptor)
9. [元类 Metaclass](#九元类-metaclass)
10. [`__slots__` 限制实例属性](#十__slots__-限制实例属性)
11. [协议与鸭子类型](#十一协议与鸭子类型)
12. [枚举 Enum](#十二枚举-enum)
13. [对象拷贝与可变性](#十三对象拷贝与可变性)
14. [综合案例：插件式任务系统](#十四综合案例插件式任务系统)
15. [练习题](#十五练习题)
16. [速查表](#十六速查表)

---

## 一、从普通类到高级类

普通类通常解决两个问题：

1. 把数据组织在一起。
2. 把和数据相关的行为放在同一个地方。

例如：

```python
class User:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def introduce(self):
        return f"我是 {self.name}, 今年 {self.age} 岁"
```

高级面向对象特性解决的是更进一步的问题：

- 如何让属性更安全？使用 `property`。
- 如何快速定义只保存数据的类？使用 `dataclass`。
- 如何规定子类必须实现某些方法？使用抽象类。
- 如何让对象支持 `for`、`len()`、`with`、函数调用等语法？实现魔术方法。
- 如何复用属性校验逻辑？使用描述符。
- 如何控制“类本身”的创建过程？使用元类。

这些特性不一定每天都要自己写，但经常会在框架、ORM、Web 开发、数据建模和大型项目中出现。

---

## 二、`property` 属性封装

### 1. 为什么需要 `property`

直接暴露属性很方便：

```python
class Product:
    def __init__(self, name, price):
        self.name = name
        self.price = price


p = Product("Book", -10)
print(p.price)  # -10，不合理
```

如果想限制价格不能为负数，可以把属性改成私有变量，再通过方法访问：

```python
class Product:
    def __init__(self, name, price):
        self.name = name
        self.set_price(price)

    def get_price(self):
        return self._price

    def set_price(self, value):
        if value < 0:
            raise ValueError("price 不能为负数")
        self._price = value
```

但这样使用起来不够自然：

```python
p = Product("Book", 50)
print(p.get_price())
p.set_price(60)
```

`property` 可以让“方法调用”看起来像“属性访问”：

```python
class Product:
    def __init__(self, name, price):
        self.name = name
        self.price = price

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        if value < 0:
            raise ValueError("price 不能为负数")
        self._price = value


p = Product("Book", 50)
print(p.price)  # 像属性一样读取
p.price = 60    # 像属性一样赋值
```

### 2. 只读属性

只定义 `@property`，不定义 setter，就可以得到只读属性：

```python
class Circle:
    def __init__(self, radius):
        self.radius = radius

    @property
    def area(self):
        return 3.14159 * self.radius ** 2


c = Circle(10)
print(c.area)
# c.area = 100  # AttributeError
```

### 3. 删除属性

还可以定义删除逻辑：

```python
class Account:
    def __init__(self, password):
        self.password = password

    @property
    def password(self):
        return "******"

    @password.setter
    def password(self, value):
        if len(value) < 6:
            raise ValueError("密码长度不能少于 6 位")
        self._password = value

    @password.deleter
    def password(self):
        print("密码已清除")
        self._password = None
```

### 4. 什么时候用 `property`

适合使用：

- 属性赋值时需要校验。
- 属性读取时需要计算。
- 希望隐藏内部存储细节。
- 既想保持属性访问语法，又想保留控制逻辑。

不适合过度使用：

- 如果只是简单保存值，直接公开属性即可。
- 如果操作会产生明显副作用，普通方法更清晰。

---

## 三、`dataclass` 数据类

### 1. 普通数据类的问题

很多类只是为了存数据：

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Point(x={self.x}, y={self.y})"

    def __eq__(self, other):
        return isinstance(other, Point) and self.x == other.x and self.y == other.y
```

这类样板代码很常见，`dataclass` 可以自动生成。

```python
from dataclasses import dataclass


@dataclass
class Point:
    x: int
    y: int


p1 = Point(1, 2)
p2 = Point(1, 2)

print(p1)       # Point(x=1, y=2)
print(p1 == p2) # True
```

### 2. 默认值

```python
from dataclasses import dataclass


@dataclass
class User:
    name: str
    age: int = 18
    active: bool = True
```

有默认值的字段必须放在无默认值字段后面。

### 3. 可变默认值要用 `field`

错误写法：

```python
from dataclasses import dataclass


@dataclass
class Team:
    name: str
    members: list = []  # 不推荐
```

正确写法：

```python
from dataclasses import dataclass, field


@dataclass
class Team:
    name: str
    members: list[str] = field(default_factory=list)
```

`default_factory=list` 会为每个实例创建新的列表，避免多个对象共享同一个列表。

### 4. 冻结对象

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    host: str
    port: int


config = Config("localhost", 8000)
# config.port = 9000  # FrozenInstanceError
```

`frozen=True` 常用于配置、坐标、值对象等不希望被修改的数据。

### 5. 排序

```python
from dataclasses import dataclass


@dataclass(order=True)
class Score:
    value: int
    name: str


scores = [Score(90, "Alice"), Score(85, "Bob")]
print(sorted(scores))
```

`order=True` 会根据字段顺序生成比较方法。

### 6. 初始化后处理

```python
from dataclasses import dataclass


@dataclass
class Rectangle:
    width: float
    height: float

    def __post_init__(self):
        if self.width <= 0 or self.height <= 0:
            raise ValueError("宽和高必须为正数")
```

`__post_init__` 会在自动生成的 `__init__` 结束后执行。

---

## 四、抽象类 ABC

### 1. 抽象类的作用

抽象类用来规定一组接口：子类必须实现某些方法，否则不能实例化。

```python
from abc import ABC, abstractmethod


class Shape(ABC):
    @abstractmethod
    def area(self):
        pass


class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return 3.14159 * self.radius ** 2


c = Circle(10)
print(c.area())
```

如果子类没有实现 `area`：

```python
class BadShape(Shape):
    pass


# BadShape()  # TypeError
```

### 2. 抽象属性

```python
from abc import ABC, abstractmethod


class Storage(ABC):
    @property
    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def save(self, data):
        pass
```

### 3. 抽象类与普通继承的区别

普通父类更关注“复用代码”，抽象类更关注“规定接口”。

```python
class Animal:
    def sleep(self):
        print("sleeping")


class Plugin(ABC):
    @abstractmethod
    def run(self):
        pass
```

`Animal` 的子类可以复用 `sleep`，`Plugin` 的子类必须提供 `run`。

---

## 五、多重继承与 MRO

### 1. 什么是多重继承

Python 允许一个类继承多个父类：

```python
class Flyer:
    def move(self):
        print("fly")


class Swimmer:
    def swim(self):
        print("swim")


class Duck(Flyer, Swimmer):
    pass


d = Duck()
d.move()
d.swim()
```

### 2. 方法冲突

如果多个父类有同名方法，Python 会按照 MRO 查找。

```python
class A:
    def hello(self):
        print("A")


class B:
    def hello(self):
        print("B")


class C(A, B):
    pass


c = C()
c.hello()        # A
print(C.mro())   # [C, A, B, object]
```

MRO 是 Method Resolution Order，意思是“方法解析顺序”。

### 3. 菱形继承

```python
class Base:
    def process(self):
        print("Base")


class Left(Base):
    def process(self):
        print("Left")
        super().process()


class Right(Base):
    def process(self):
        print("Right")
        super().process()


class Child(Left, Right):
    def process(self):
        print("Child")
        super().process()


child = Child()
child.process()
print(Child.mro())
```

输出顺序：

```text
Child
Left
Right
Base
```

`super()` 不是简单调用“父类”，而是调用 MRO 中的下一个类。

### 4. Mixin 模式

Mixin 是一种小型能力类，用来给主类附加功能。

```python
class JsonMixin:
    def to_json(self):
        import json
        return json.dumps(self.__dict__, ensure_ascii=False)


class LogMixin:
    def log(self, message):
        print(f"[{self.__class__.__name__}] {message}")


class User(JsonMixin, LogMixin):
    def __init__(self, name, age):
        self.name = name
        self.age = age


u = User("Alice", 20)
print(u.to_json())
u.log("created")
```

Mixin 的建议：

- Mixin 类通常不单独实例化。
- Mixin 类尽量小而专一。
- Mixin 类名一般以 `Mixin` 结尾。
- 多个 Mixin 依赖顺序时，要特别小心 MRO。

---

## 六、常用魔术方法

魔术方法也叫特殊方法，通常以双下划线开头和结尾，例如 `__len__`、`__iter__`。它们让自定义对象可以配合 Python 内置语法使用。

### 1. 字符串表示：`__repr__` 与 `__str__`

```python
class Book:
    def __init__(self, title, price):
        self.title = title
        self.price = price

    def __repr__(self):
        return f"Book(title={self.title!r}, price={self.price!r})"

    def __str__(self):
        return f"《{self.title}》 - {self.price} 元"


book = Book("Python 入门", 59)
print(book)       # 调用 __str__
print(repr(book)) # 调用 __repr__
```

一般建议：

- `__repr__` 面向开发者，尽量准确。
- `__str__` 面向用户，尽量友好。

### 2. 容器协议：`__len__`、`__getitem__`

```python
class Library:
    def __init__(self, books):
        self.books = list(books)

    def __len__(self):
        return len(self.books)

    def __getitem__(self, index):
        return self.books[index]


library = Library(["Python", "Django", "Flask"])
print(len(library))
print(library[0])
print(library[:2])
```

实现 `__getitem__` 后，对象就可以支持索引和切片。

### 3. 可迭代对象：`__iter__`

```python
class Countdown:
    def __init__(self, start):
        self.start = start

    def __iter__(self):
        current = self.start
        while current > 0:
            yield current
            current -= 1


for number in Countdown(3):
    print(number)
```

`__iter__` 返回一个迭代器。使用生成器写法最简单。

### 4. 可调用对象：`__call__`

```python
class Multiplier:
    def __init__(self, factor):
        self.factor = factor

    def __call__(self, value):
        return value * self.factor


double = Multiplier(2)
print(double(10))  # 20
```

`__call__` 常用于：

- 封装带状态的函数。
- 编写装饰器类。
- 实现策略对象。

### 5. 数值运算：`__add__`

```python
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __repr__(self):
        return f"Vector({self.x}, {self.y})"


v1 = Vector(1, 2)
v2 = Vector(3, 4)
print(v1 + v2)
```

常见运算相关魔术方法：

| 方法 | 对应语法 |
| --- | --- |
| `__add__` | `a + b` |
| `__sub__` | `a - b` |
| `__mul__` | `a * b` |
| `__truediv__` | `a / b` |
| `__eq__` | `a == b` |
| `__lt__` | `a < b` |

### 6. 布尔值：`__bool__`

```python
class Cart:
    def __init__(self):
        self.items = []

    def __bool__(self):
        return len(self.items) > 0


cart = Cart()
if cart:
    print("购物车有商品")
else:
    print("购物车为空")
```

---

## 七、上下文管理器

上下文管理器让对象支持 `with` 语句，常用于资源管理。

```python
class FileWriter:
    def __init__(self, filename):
        self.filename = filename
        self.file = None

    def __enter__(self):
        self.file = open(self.filename, "w", encoding="utf-8")
        return self.file

    def __exit__(self, exc_type, exc_value, traceback):
        self.file.close()
        return False


with FileWriter("demo.txt") as f:
    f.write("hello")
```

`__enter__` 在进入 `with` 块时调用，返回值会赋给 `as` 后面的变量。

`__exit__` 在离开 `with` 块时调用，即使发生异常也会执行。

`__exit__` 的返回值：

- 返回 `False` 或 `None`：异常继续抛出。
- 返回 `True`：异常被吞掉。

也可以使用标准库 `contextlib` 简化：

```python
from contextlib import contextmanager


@contextmanager
def timer(name):
    import time
    start = time.time()
    try:
        yield
    finally:
        end = time.time()
        print(f"{name} 耗时: {end - start:.4f} 秒")


with timer("任务"):
    sum(range(100000))
```

---

## 八、描述符 Descriptor

### 1. 描述符是什么

描述符是定义了下面任意方法的对象：

- `__get__(self, instance, owner)`
- `__set__(self, instance, value)`
- `__delete__(self, instance)`

描述符本质上是“可复用的属性访问控制器”。

### 2. 一个校验正数的描述符

```python
class PositiveNumber:
    def __init__(self, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        if value <= 0:
            raise ValueError(f"{self.name} 必须为正数")
        instance.__dict__[self.name] = value


class Product:
    price = PositiveNumber("price")
    stock = PositiveNumber("stock")

    def __init__(self, name, price, stock):
        self.name = name
        self.price = price
        self.stock = stock


p = Product("Book", 50, 100)
print(p.price)
# p.price = -1  # ValueError
```

### 3. 使用 `__set_name__` 自动获取属性名

```python
class PositiveNumber:
    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        if value <= 0:
            raise ValueError(f"{self.name} 必须为正数")
        instance.__dict__[self.name] = value


class Product:
    price = PositiveNumber()
    stock = PositiveNumber()

    def __init__(self, price, stock):
        self.price = price
        self.stock = stock
```

### 4. `property` 也是描述符

`property` 本身就实现了描述符协议，所以描述符可以看成更底层、更通用的 `property`。

适合使用描述符的场景：

- 多个字段共享相同校验逻辑。
- ORM 字段定义。
- 表单字段校验。
- 配置项访问控制。

---

## 九、元类 Metaclass

### 1. 类也是对象

在 Python 中，对象由类创建，而类本身也是对象。普通类默认由 `type` 创建。

```python
class User:
    pass


print(type(User))  # <class 'type'>
print(type(User())) # <class '__main__.User'>
```

也可以直接用 `type` 创建类：

```python
User = type("User", (), {"role": "admin"})

u = User()
print(u.role)
```

`type(name, bases, namespace)` 的三个参数分别是：

- 类名。
- 父类元组。
- 类属性和方法组成的字典。

### 2. 自定义元类

元类可以控制类的创建过程。

```python
class UpperAttrMeta(type):
    def __new__(mcls, name, bases, namespace):
        new_namespace = {}
        for key, value in namespace.items():
            if not key.startswith("__"):
                key = key.upper()
            new_namespace[key] = value
        return super().__new__(mcls, name, bases, new_namespace)


class Config(metaclass=UpperAttrMeta):
    host = "localhost"
    port = 8000


print(Config.HOST)
print(Config.PORT)
```

### 3. 用元类做注册

```python
class PluginMeta(type):
    registry = {}

    def __new__(mcls, name, bases, namespace):
        cls = super().__new__(mcls, name, bases, namespace)
        if name != "BasePlugin":
            mcls.registry[name] = cls
        return cls


class BasePlugin(metaclass=PluginMeta):
    pass


class EmailPlugin(BasePlugin):
    pass


class SmsPlugin(BasePlugin):
    pass


print(PluginMeta.registry)
```

### 4. 什么时候使用元类

元类很强，但不应轻易使用。

适合使用：

- 框架级别的类注册。
- ORM 模型定义。
- 自动检查类定义是否符合规范。
- 修改类创建行为。

优先考虑更简单的方案：

1. 普通函数。
2. 类装饰器。
3. 父类的 `__init_subclass__`。
4. 元类。

### 5. `__init_subclass__`：更轻量的类注册

很多元类需求可以用 `__init_subclass__` 完成：

```python
class Plugin:
    registry = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Plugin.registry[cls.__name__] = cls


class CsvPlugin(Plugin):
    pass


class JsonPlugin(Plugin):
    pass


print(Plugin.registry)
```

这比元类更容易理解，也更不容易和其他框架冲突。

---

## 十、`__slots__` 限制实例属性

普通对象的属性保存在 `__dict__` 中，所以可以随时添加新属性：

```python
class User:
    pass


u = User()
u.name = "Alice"
u.age = 20
```

`__slots__` 可以限制实例允许的属性：

```python
class User:
    __slots__ = ("name", "age")

    def __init__(self, name, age):
        self.name = name
        self.age = age


u = User("Alice", 20)
# u.email = "a@example.com"  # AttributeError
```

优点：

- 防止属性名写错。
- 大量实例时可以节省内存。

注意：

- 使用 `__slots__` 后，默认没有 `__dict__`。
- 继承关系中使用 `__slots__` 时要更谨慎。
- 不是所有类都需要它，不要为了“高级”而使用。

---

## 十一、协议与鸭子类型

Python 更看重“对象能做什么”，而不是“对象是什么类型”。

```python
class FileLogger:
    def write(self, message):
        print(f"写入文件: {message}")


class ConsoleLogger:
    def write(self, message):
        print(f"输出控制台: {message}")


def log_message(logger, message):
    logger.write(message)


log_message(FileLogger(), "hello")
log_message(ConsoleLogger(), "hello")
```

两个类没有共同父类，但都能传给 `log_message`，因为它们都实现了 `write` 方法。

这就是鸭子类型：如果它走起来像鸭子，叫起来像鸭子，就可以当作鸭子使用。

### 使用 `Protocol` 做类型提示

```python
from typing import Protocol


class Writable(Protocol):
    def write(self, message: str) -> None:
        ...


def log_message(logger: Writable, message: str) -> None:
    logger.write(message)
```

`Protocol` 不强制继承，但可以帮助类型检查工具理解接口要求。

---

## 十二、枚举 Enum

当某个字段只能取固定几个值时，枚举比字符串更安全。

```python
from enum import Enum


class OrderStatus(Enum):
    CREATED = "created"
    PAID = "paid"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"


status = OrderStatus.PAID

if status is OrderStatus.PAID:
    print("订单已支付")

print(status.name)   # PAID
print(status.value)  # paid
```

枚举的好处：

- 避免字符串拼写错误。
- 让可选值集中定义。
- 代码可读性更好。

---

## 十三、对象拷贝与可变性

### 1. 赋值不是拷贝

```python
a = [1, 2, 3]
b = a
b.append(4)
print(a)  # [1, 2, 3, 4]
```

`b = a` 只是让两个变量指向同一个对象。

### 2. 浅拷贝

```python
import copy


a = [[1, 2], [3, 4]]
b = copy.copy(a)

b.append([5, 6])
b[0].append(99)

print(a)  # [[1, 2, 99], [3, 4]]
```

浅拷贝只复制最外层对象，里面的子对象仍然共享。

### 3. 深拷贝

```python
import copy


a = [[1, 2], [3, 4]]
b = copy.deepcopy(a)

b[0].append(99)
print(a)  # [[1, 2], [3, 4]]
```

深拷贝会递归复制内部对象。

### 4. 在类中控制拷贝

```python
class Bag:
    def __init__(self, items):
        self.items = list(items)

    def __copy__(self):
        return Bag(self.items)

    def __deepcopy__(self, memo):
        import copy
        return Bag(copy.deepcopy(self.items, memo))
```

---

## 十四、综合案例：插件式任务系统

下面的例子综合使用了 `dataclass`、抽象类、`__call__`、上下文管理器和类注册。

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from time import perf_counter


@dataclass
class TaskResult:
    name: str
    success: bool
    message: str = ""
    data: dict = field(default_factory=dict)


class Timer:
    def __init__(self, label):
        self.label = label

    def __enter__(self):
        self.start = perf_counter()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.end = perf_counter()
        self.elapsed = self.end - self.start
        print(f"{self.label} 耗时: {self.elapsed:.4f} 秒")
        return False


class Task(ABC):
    registry = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not getattr(cls, "abstract", False):
            Task.registry[cls.__name__] = cls

    @abstractmethod
    def run(self):
        pass

    def __call__(self):
        with Timer(self.__class__.__name__):
            return self.run()


class CountTask(Task):
    def __init__(self, limit):
        self.limit = limit

    def run(self):
        total = sum(range(self.limit + 1))
        return TaskResult(
            name="count",
            success=True,
            message="计算完成",
            data={"total": total},
        )


class HelloTask(Task):
    def __init__(self, name):
        self.name = name

    def run(self):
        return TaskResult(
            name="hello",
            success=True,
            message=f"你好，{self.name}",
        )


tasks = [
    CountTask(100),
    HelloTask("Alice"),
]

for task in tasks:
    result = task()
    print(result)

print(Task.registry)
```

这个案例中：

- `TaskResult` 用 `dataclass` 表示任务结果。
- `Task` 用抽象类规定子类必须实现 `run`。
- `__call__` 让任务对象可以像函数一样调用。
- `Timer` 用上下文管理器统计耗时。
- `__init_subclass__` 自动注册任务类。

---

## 十五、练习题

### 练习 1：带校验的学生类

创建一个 `Student` 类：

- `name` 不能为空。
- `score` 必须在 `0` 到 `100` 之间。
- 使用 `property` 实现校验。
- 添加只读属性 `level`，规则如下：
  - `score >= 90` 返回 `"A"`
  - `score >= 80` 返回 `"B"`
  - `score >= 60` 返回 `"C"`
  - 否则返回 `"D"`

### 练习 2：订单数据类

使用 `dataclass` 创建 `Order`：

- 字段：`order_id`、`items`、`status`。
- `items` 默认是空列表。
- `status` 使用枚举，默认值为 `CREATED`。
- 添加方法 `total_price()`。

### 练习 3：抽象支付类

创建抽象类 `Payment`：

- 抽象方法 `pay(amount)`。
- 实现两个子类：`AlipayPayment`、`WechatPayment`。
- 写一个函数 `checkout(payment, amount)`，接收任意 `Payment` 子类对象。

### 练习 4：自定义容器

创建 `TodoList` 类：

- 支持 `len(todo_list)`。
- 支持 `todo_list[0]`。
- 支持 `for item in todo_list`。
- 支持 `todo_list("买牛奶")`，调用后添加任务。

### 练习 5：正数字段描述符

实现描述符 `PositiveNumber`：

- 用于校验字段必须大于 0。
- 应用于 `Product.price` 和 `Product.weight`。

### 练习 6：插件注册

使用 `__init_subclass__` 或元类实现插件注册：

- 定义基类 `Plugin`。
- 所有子类自动加入 `Plugin.registry`。
- 至少创建两个插件类。
- 根据字符串名称找到插件类并实例化。

---

## 十六、速查表

| 特性 | 作用 | 常见场景 |
| --- | --- | --- |
| `@property` | 控制属性读取、赋值、删除 | 属性校验、计算属性 |
| `@dataclass` | 自动生成数据类样板代码 | 配置、DTO、值对象 |
| `ABC` / `abstractmethod` | 定义必须实现的接口 | 插件、支付、存储、任务 |
| 多重继承 | 同时继承多个父类能力 | Mixin、组合小能力 |
| MRO | 决定方法查找顺序 | 多重继承、`super()` |
| `__repr__` | 开发者视角字符串 | 调试、日志 |
| `__str__` | 用户视角字符串 | 展示文本 |
| `__len__` | 支持 `len(obj)` | 容器类 |
| `__getitem__` | 支持索引和切片 | 列表包装类 |
| `__iter__` | 支持迭代 | 自定义集合 |
| `__call__` | 对象像函数一样调用 | 策略、装饰器、任务 |
| `__enter__` / `__exit__` | 支持 `with` | 文件、锁、数据库连接 |
| 描述符 | 复用属性访问逻辑 | ORM、字段校验 |
| 元类 | 控制类的创建 | 框架、ORM、注册系统 |
| `__init_subclass__` | 子类创建时自动执行 | 插件注册、类规范检查 |
| `__slots__` | 限制实例属性 | 防错、节省内存 |
| `Protocol` | 定义结构化接口 | 类型提示、鸭子类型 |
| `Enum` | 固定可选值 | 状态、类型、模式 |

---

## 学习建议

这些高级特性可以分成三层学习：

第一层，应该熟练掌握：

- `property`
- `dataclass`
- 抽象类
- 常用魔术方法
- 上下文管理器

第二层，读源码时要能看懂：

- 多重继承与 MRO
- Mixin
- 描述符
- `__init_subclass__`
- `Protocol`

第三层，知道何时才值得使用：

- 元类
- 复杂描述符
- 深度定制对象创建和属性访问

实际写代码时，优先选择简单清晰的方案。高级特性真正的价值不是“看起来厉害”，而是在合适的地方减少重复、约束接口、表达设计意图。
