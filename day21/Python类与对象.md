# Python 类与对象详解

> 面向对象编程（Object-Oriented Programming，OOP）是一种把程序组织成“对象之间协作”的编程思想。Python 中“一切皆对象”，理解类与对象，是写出可维护代码、理解第三方库源码、设计大型程序结构的重要基础。

---

## 目录

1. [为什么需要类和对象](#一为什么需要类和对象)
2. [类与对象的基本概念](#二类与对象的基本概念)
3. [定义类与创建对象](#三定义类与创建对象)
4. [实例属性与实例方法](#四实例属性与实例方法)
5. [构造方法 `__init__`](#五构造方法-__init__)
6. [类属性与实例属性](#六类属性与实例属性)
7. [实例方法、类方法、静态方法](#七实例方法类方法静态方法)
8. [封装：隐藏实现细节](#八封装隐藏实现细节)
9. [属性访问控制：`@property`](#九属性访问控制-property)
10. [继承：复用和扩展代码](#十继承复用和扩展代码)
11. [方法重写与 `super()`](#十一方法重写与-super)
12. [多态：同一接口，不同实现](#十二多态同一接口不同实现)
13. [魔术方法：让对象更像内置类型](#十三魔术方法让对象更像内置类型)
14. [对象的生命周期](#十四对象的生命周期)
15. [组合：比继承更灵活的复用](#十五组合比继承更灵活的复用)
16. [数据类 `dataclass`](#十六数据类-dataclass)
17. [常见错误与最佳实践](#十七常见错误与最佳实践)
18. [综合案例：学生管理系统雏形](#十八综合案例学生管理系统雏形)
19. [练习题](#十九练习题)
20. [速查表](#二十速查表)

---

## 一、为什么需要类和对象

假设我们要管理学生信息，最开始可能会这样写：

```python
student1_name = "Alice"
student1_age = 18
student1_score = 95

student2_name = "Bob"
student2_age = 19
student2_score = 88

def print_student(name, age, score):
    print(f"{name}, {age}岁, 成绩: {score}")

print_student(student1_name, student1_age, student1_score)
print_student(student2_name, student2_age, student2_score)
```

这样写有几个问题：

1. 同一个学生的数据被拆散在多个变量中，容易传错。
2. 学生相关的行为，比如展示信息、判断是否及格，和学生数据分离。
3. 学生越来越多时，变量数量会爆炸。
4. 程序缺少清晰的抽象，后期维护困难。

可以先用字典改进：

```python
student = {
    "name": "Alice",
    "age": 18,
    "score": 95,
}

def print_student(student):
    print(f"{student['name']}, {student['age']}岁, 成绩: {student['score']}")
```

字典能把数据放在一起，但它仍然有问题：

```python
student["socre"] = 100  # 拼写错误，Python 不会马上提醒
```

类和对象可以把“数据”和“行为”绑定在一起：

```python
class Student:
    def __init__(self, name, age, score):
        self.name = name
        self.age = age
        self.score = score

    def show_info(self):
        print(f"{self.name}, {self.age}岁, 成绩: {self.score}")


student = Student("Alice", 18, 95)
student.show_info()
```

这里的 `Student` 就是一种抽象：它描述了“学生”应该有哪些数据，以及能做什么事情。

---

## 二、类与对象的基本概念

### 2.1 类是什么

类（class）是一种模板、蓝图、说明书，用来描述一类事物的共同特征和行为。

例如：

| 类 | 共同特征 | 共同行为 |
| --- | --- | --- |
| `Student` | 姓名、年龄、成绩 | 学习、考试、展示信息 |
| `Dog` | 名字、品种、年龄 | 吃饭、叫、奔跑 |
| `BankAccount` | 户名、余额 | 存款、取款、查询余额 |
| `Car` | 品牌、颜色、速度 | 启动、加速、刹车 |

### 2.2 对象是什么

对象（object）是类创建出来的具体实例。

如果 `Student` 是“学生”这个模板，那么：

```python
alice = Student("Alice", 18, 95)
bob = Student("Bob", 19, 88)
```

`alice` 和 `bob` 就是两个不同的学生对象。

### 2.3 类和对象的关系

```text
类：设计图
对象：根据设计图造出来的具体东西

类：Student
对象：Alice 这个学生、Bob 这个学生

类：Car
对象：一辆红色 Tesla、一辆黑色 BMW
```

### 2.4 Python 中一切皆对象

在 Python 中，整数、字符串、列表、函数、模块、类本身都是对象。

```python
print(type(10))          # <class 'int'>
print(type("hello"))     # <class 'str'>
print(type([1, 2, 3]))   # <class 'list'>
print(type(print))       # <class 'builtin_function_or_method'>
```

常见的写法本质上也是对象调用方法：

```python
text = "python"
print(text.upper())  # 字符串对象调用 upper 方法

numbers = [3, 1, 2]
numbers.sort()       # 列表对象调用 sort 方法
print(numbers)
```

---

## 三、定义类与创建对象

### 3.1 最简单的类

```python
class Dog:
    pass


dog1 = Dog()
dog2 = Dog()

print(dog1)
print(dog2)
print(dog1 is dog2)  # False，两个不同对象
```

说明：

1. `class Dog:` 定义一个类。
2. 类名通常使用大驼峰命名法，例如 `Dog`、`BankAccount`、`StudentManager`。
3. `pass` 表示暂时什么都不写，占位。
4. `Dog()` 会创建一个 `Dog` 对象。

### 3.2 给对象添加属性

```python
class Dog:
    pass


dog = Dog()
dog.name = "旺财"
dog.age = 3

print(dog.name)
print(dog.age)
```

Python 允许动态给对象添加属性，但在实际开发中，更推荐在 `__init__` 中统一定义属性，这样结构更清晰。

---

## 四、实例属性与实例方法

### 4.1 实例属性

实例属性是属于某个具体对象的数据。

```python
class Dog:
    def __init__(self, name, age):
        self.name = name
        self.age = age


dog1 = Dog("旺财", 3)
dog2 = Dog("小黑", 5)

print(dog1.name)  # 旺财
print(dog2.name)  # 小黑
```

`dog1.name` 和 `dog2.name` 互不影响，因为它们属于不同对象。

### 4.2 实例方法

实例方法是属于对象的行为，第一个参数通常叫 `self`。

```python
class Dog:
    def __init__(self, name):
        self.name = name

    def bark(self):
        print(f"{self.name}：汪汪！")


dog = Dog("旺财")
dog.bark()
```

### 4.3 `self` 是什么

`self` 表示当前对象本身。

```python
class Student:
    def __init__(self, name):
        self.name = name

    def say_hi(self):
        print(f"你好，我是 {self.name}")


alice = Student("Alice")
bob = Student("Bob")

alice.say_hi()  # self 是 alice
bob.say_hi()    # self 是 bob
```

调用：

```python
alice.say_hi()
```

大致等价于：

```python
Student.say_hi(alice)
```

所以实例方法必须接收当前对象，一般写成 `self`。

### 4.4 `self` 不是关键字

下面这样也能运行：

```python
class Cat:
    def __init__(this, name):
        this.name = name
```

但不推荐。Python 社区约定统一使用 `self`，这会让代码更容易读。

---

## 五、构造方法 `__init__`

`__init__` 是对象创建后自动调用的方法，常用于初始化对象属性。

```python
class Student:
    def __init__(self, name, age, score):
        self.name = name
        self.age = age
        self.score = score


student = Student("Alice", 18, 95)
print(student.name)
```

### 5.1 `__init__` 不是创建对象的方法

严格来说：

1. `__new__` 负责创建对象。
2. `__init__` 负责初始化对象。

初学阶段通常只需要掌握 `__init__`。

### 5.2 参数默认值

```python
class User:
    def __init__(self, username, is_active=True):
        self.username = username
        self.is_active = is_active


user1 = User("alice")
user2 = User("bob", False)

print(user1.is_active)  # True
print(user2.is_active)  # False
```

### 5.3 不要在默认参数中使用可变对象

错误示例：

```python
class Team:
    def __init__(self, members=[]):
        self.members = members


team1 = Team()
team2 = Team()

team1.members.append("Alice")
print(team2.members)  # ['Alice']，意外共享了同一个列表
```

推荐写法：

```python
class Team:
    def __init__(self, members=None):
        if members is None:
            members = []
        self.members = members


team1 = Team()
team2 = Team()

team1.members.append("Alice")
print(team2.members)  # []
```

---

## 六、类属性与实例属性

### 6.1 实例属性

实例属性属于对象，每个对象都有自己的副本。

```python
class Student:
    def __init__(self, name):
        self.name = name


alice = Student("Alice")
bob = Student("Bob")

alice.name = "Alicia"
print(alice.name)  # Alicia
print(bob.name)    # Bob
```

### 6.2 类属性

类属性属于类，被所有实例共享。

```python
class Student:
    school = "Python Academy"

    def __init__(self, name):
        self.name = name


alice = Student("Alice")
bob = Student("Bob")

print(alice.school)
print(bob.school)
print(Student.school)
```

### 6.3 类属性适合放什么

类属性适合存放所有对象共享的数据：

```python
class Circle:
    pi = 3.1415926

    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return self.pi * self.radius ** 2
```

### 6.4 类属性的修改

```python
class Student:
    school = "Python Academy"


alice = Student()
bob = Student()

Student.school = "AI Academy"

print(alice.school)  # AI Academy
print(bob.school)    # AI Academy
```

注意下面这个例子：

```python
alice.school = "Alice Private School"

print(alice.school)    # Alice Private School
print(bob.school)      # AI Academy
print(Student.school)  # AI Academy
```

`alice.school = ...` 创建了一个同名实例属性，它遮住了类属性，并没有修改类属性。

### 6.5 类属性中的可变对象要小心

错误示例：

```python
class Student:
    hobbies = []

    def __init__(self, name):
        self.name = name


alice = Student("Alice")
bob = Student("Bob")

alice.hobbies.append("reading")
print(bob.hobbies)  # ['reading']
```

如果每个学生都应该有自己的爱好列表，应写成实例属性：

```python
class Student:
    def __init__(self, name):
        self.name = name
        self.hobbies = []
```

---

## 七、实例方法、类方法、静态方法

Python 类中常见的三类方法：

| 方法类型 | 装饰器 | 第一个参数 | 适合场景 |
| --- | --- | --- | --- |
| 实例方法 | 无 | `self` | 需要访问或修改对象状态 |
| 类方法 | `@classmethod` | `cls` | 需要访问或修改类状态，或提供替代构造器 |
| 静态方法 | `@staticmethod` | 无固定参数 | 和类有关，但不需要访问对象或类状态 |

### 7.1 实例方法

```python
class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount


account = BankAccount("Alice", 100)
account.deposit(50)
print(account.balance)  # 150
```

### 7.2 类方法

```python
class User:
    count = 0

    def __init__(self, username):
        self.username = username
        User.count += 1

    @classmethod
    def get_count(cls):
        return cls.count


user1 = User("alice")
user2 = User("bob")

print(User.get_count())  # 2
```

`cls` 表示当前类。类方法可以被类调用，也可以被对象调用，但通常用类调用更清晰。

### 7.3 类方法作为替代构造器

```python
class Date:
    def __init__(self, year, month, day):
        self.year = year
        self.month = month
        self.day = day

    @classmethod
    def from_string(cls, text):
        year, month, day = text.split("-")
        return cls(int(year), int(month), int(day))

    def show(self):
        print(f"{self.year}年{self.month}月{self.day}日")


date = Date.from_string("2026-07-05")
date.show()
```

### 7.4 静态方法

```python
class MathTool:
    @staticmethod
    def is_even(number):
        return number % 2 == 0


print(MathTool.is_even(10))  # True
```

静态方法本质上就是放在类命名空间中的普通函数。它和这个类概念相关，但不依赖某个具体对象。

---

## 八、封装：隐藏实现细节

封装的核心思想：把数据和操作数据的方法放在一起，并限制外部直接随意修改内部状态。

### 8.1 公开属性

```python
class User:
    def __init__(self, username):
        self.username = username
```

`username` 是公开属性，外部可以直接访问和修改：

```python
user = User("alice")
user.username = "bob"
```

### 8.2 单下划线：约定为内部使用

```python
class User:
    def __init__(self, username, password):
        self.username = username
        self._password = password
```

`_password` 仍然可以访问，但意思是：这是内部属性，外部不要随便用。

```python
user = User("alice", "123456")
print(user._password)  # 能访问，但不推荐
```

### 8.3 双下划线：名称改写

```python
class User:
    def __init__(self, username, password):
        self.username = username
        self.__password = password

    def check_password(self, password):
        return self.__password == password


user = User("alice", "123456")
print(user.check_password("123456"))  # True
```

直接访问会失败：

```python
# print(user.__password)  # AttributeError
```

但双下划线并不是绝对安全，只是触发名称改写：

```python
print(user._User__password)  # 可以访问，不建议这样做
```

所以 Python 的封装更强调“约定”和“接口设计”，不是绝对禁止。

---

## 九、属性访问控制：`@property`

`@property` 可以把方法伪装成属性访问，同时保留校验逻辑。

### 9.1 基本用法

```python
class Circle:
    def __init__(self, radius):
        self.radius = radius

    @property
    def area(self):
        return 3.1415926 * self.radius ** 2


circle = Circle(3)
print(circle.area)  # 像属性一样访问，不需要 circle.area()
```

`area` 是根据 `radius` 计算出来的，不应该手动保存，否则可能和半径不同步。

### 9.2 setter 校验数据

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
            raise ValueError("价格不能为负数")
        self._price = value


product = Product("Keyboard", 299)
print(product.price)

product.price = 399
print(product.price)

# product.price = -1  # ValueError
```

这里的关键点：

1. 外部仍然使用 `product.price`。
2. 内部实际保存到 `self._price`。
3. 修改价格时会自动触发校验。

---

## 十、继承：复用和扩展代码

继承可以让一个类获得另一个类的属性和方法。

```python
class Animal:
    def __init__(self, name):
        self.name = name

    def eat(self):
        print(f"{self.name} 正在吃东西")


class Dog(Animal):
    def bark(self):
        print(f"{self.name}：汪汪！")


dog = Dog("旺财")
dog.eat()
dog.bark()
```

`Dog` 继承了 `Animal`，所以 `Dog` 对象可以调用 `eat()`。

### 10.1 父类与子类

```text
Animal 是父类、基类、超类
Dog 是子类、派生类
```

### 10.2 `isinstance` 和 `issubclass`

```python
dog = Dog("旺财")

print(isinstance(dog, Dog))      # True
print(isinstance(dog, Animal))   # True
print(issubclass(Dog, Animal))   # True
```

### 10.3 继承适合表达“是一种”的关系

合理：

```text
Dog 是一种 Animal
Student 是一种 Person
Circle 是一种 Shape
```

不合理：

```text
Car 是一种 Engine   # 错，汽车有一个发动机，但汽车不是发动机
```

这种“有一个”的关系更适合使用组合。

---

## 十一、方法重写与 `super()`

子类可以重新定义父类已有的方法，这叫方法重写（override）。

### 11.1 方法重写

```python
class Animal:
    def speak(self):
        print("动物发出声音")


class Dog(Animal):
    def speak(self):
        print("汪汪！")


class Cat(Animal):
    def speak(self):
        print("喵喵！")


dog = Dog()
cat = Cat()

dog.speak()
cat.speak()
```

### 11.2 使用 `super()` 调用父类方法

```python
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age


class Student(Person):
    def __init__(self, name, age, score):
        super().__init__(name, age)
        self.score = score


student = Student("Alice", 18, 95)
print(student.name, student.age, student.score)
```

`super().__init__(name, age)` 的意思是：调用父类的初始化逻辑，避免重复写 `self.name = name` 和 `self.age = age`。

### 11.3 扩展父类方法

```python
class Logger:
    def log(self, message):
        print(f"[LOG] {message}")


class FileLogger(Logger):
    def log(self, message):
        super().log(message)
        print("消息已写入文件")


logger = FileLogger()
logger.log("程序启动")
```

子类不是完全替代父类逻辑，而是在父类逻辑基础上做扩展。

---

## 十二、多态：同一接口，不同实现

多态指不同对象对同一个方法调用作出不同响应。

```python
class Dog:
    def speak(self):
        print("汪汪！")


class Cat:
    def speak(self):
        print("喵喵！")


class Duck:
    def speak(self):
        print("嘎嘎！")


def make_it_speak(animal):
    animal.speak()


make_it_speak(Dog())
make_it_speak(Cat())
make_it_speak(Duck())
```

Python 更看重对象“能不能做某件事”，而不是它“到底是什么类型”。这常被称为鸭子类型：

```text
如果一个对象走起来像鸭子，叫起来像鸭子，那么它就可以被当作鸭子使用。
```

### 12.1 多态的好处

假设我们有多个支付方式：

```python
class Alipay:
    def pay(self, amount):
        print(f"支付宝支付 {amount} 元")


class WeChatPay:
    def pay(self, amount):
        print(f"微信支付 {amount} 元")


class CreditCard:
    def pay(self, amount):
        print(f"信用卡支付 {amount} 元")


def checkout(payment_method, amount):
    payment_method.pay(amount)


checkout(Alipay(), 100)
checkout(WeChatPay(), 200)
checkout(CreditCard(), 300)
```

`checkout` 不关心支付对象具体是哪种类型，只关心它有没有 `pay` 方法。以后增加新的支付方式时，`checkout` 不需要修改。

---

## 十三、魔术方法：让对象更像内置类型

魔术方法也叫特殊方法，通常以双下划线开头和结尾，例如 `__str__`、`__len__`、`__add__`。

### 13.1 `__str__` 和 `__repr__`

```python
class Student:
    def __init__(self, name, score):
        self.name = name
        self.score = score

    def __str__(self):
        return f"{self.name} 的成绩是 {self.score}"

    def __repr__(self):
        return f"Student(name={self.name!r}, score={self.score!r})"


student = Student("Alice", 95)
print(student)        # 调用 __str__
print(repr(student))  # 调用 __repr__
```

区别：

1. `__str__` 面向用户，追求可读。
2. `__repr__` 面向开发者，追求明确，最好能辅助调试。

### 13.2 `__len__`

```python
class Playlist:
    def __init__(self, songs):
        self.songs = songs

    def __len__(self):
        return len(self.songs)


playlist = Playlist(["Song A", "Song B", "Song C"])
print(len(playlist))  # 3
```

### 13.3 `__add__`

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

print(v1 + v2)  # Vector(4, 6)
```

### 13.4 `__eq__`

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        if not isinstance(other, Point):
            return False
        return self.x == other.x and self.y == other.y


p1 = Point(1, 2)
p2 = Point(1, 2)

print(p1 == p2)  # True
```

如果不定义 `__eq__`，对象默认比较身份，也就是是否为同一个对象。

### 13.5 常见魔术方法速览

| 方法 | 触发场景 |
| --- | --- |
| `__init__` | 初始化对象 |
| `__str__` | `print(obj)`、`str(obj)` |
| `__repr__` | `repr(obj)`、交互式环境显示 |
| `__len__` | `len(obj)` |
| `__eq__` | `obj1 == obj2` |
| `__lt__` | `obj1 < obj2` |
| `__add__` | `obj1 + obj2` |
| `__contains__` | `x in obj` |
| `__getitem__` | `obj[index]` |
| `__setitem__` | `obj[index] = value` |
| `__call__` | `obj()` |

---

## 十四、对象的生命周期

对象的生命周期大致包括：

```text
创建对象 -> 初始化对象 -> 使用对象 -> 对象不再被引用 -> 垃圾回收
```

### 14.1 创建与初始化

```python
class Demo:
    def __init__(self):
        print("对象初始化")


demo = Demo()
```

### 14.2 引用

变量保存的不是对象本身，而是对象的引用。

```python
class Student:
    def __init__(self, name):
        self.name = name


alice = Student("Alice")
another = alice

another.name = "Alicia"
print(alice.name)  # Alicia
```

`alice` 和 `another` 指向同一个对象。

### 14.3 判断是否为同一个对象

```python
a = [1, 2, 3]
b = a
c = [1, 2, 3]

print(a == c)  # True，值相等
print(a is c)  # False，不是同一个对象
print(a is b)  # True，是同一个对象
```

### 14.4 `__del__` 不推荐依赖

```python
class FileWrapper:
    def __del__(self):
        print("对象即将销毁")
```

`__del__` 的调用时机不稳定，不建议依赖它释放关键资源。文件、网络连接等资源应该使用 `with` 或显式关闭。

---

## 十五、组合：比继承更灵活的复用

组合是指一个对象内部持有另一个对象。

```python
class Engine:
    def start(self):
        print("发动机启动")


class Car:
    def __init__(self, engine):
        self.engine = engine

    def start(self):
        self.engine.start()
        print("汽车启动")


engine = Engine()
car = Car(engine)
car.start()
```

这里 `Car` 并不是 `Engine`，而是拥有一个 `Engine`。

### 15.1 继承和组合怎么选

| 关系 | 推荐方式 | 示例 |
| --- | --- | --- |
| 是一种 | 继承 | `Dog` 是一种 `Animal` |
| 有一个 | 组合 | `Car` 有一个 `Engine` |
| 使用某能力 | 组合 | `OrderService` 使用 `PaymentClient` |

实际开发中，组合通常比继承更灵活。继承层级太深时，代码会变得难以理解。

---

## 十六、数据类 `dataclass`

当一个类主要用于保存数据时，可以使用 `dataclass` 简化代码。

### 16.1 普通类写法

```python
class Student:
    def __init__(self, name, age, score):
        self.name = name
        self.age = age
        self.score = score

    def __repr__(self):
        return f"Student(name={self.name!r}, age={self.age!r}, score={self.score!r})"
```

### 16.2 `dataclass` 写法

```python
from dataclasses import dataclass


@dataclass
class Student:
    name: str
    age: int
    score: float


student = Student("Alice", 18, 95)
print(student)
```

`dataclass` 会自动生成常用方法，例如：

1. `__init__`
2. `__repr__`
3. `__eq__`

### 16.3 默认值

```python
from dataclasses import dataclass


@dataclass
class User:
    username: str
    is_active: bool = True
```

### 16.4 可变默认值使用 `field`

```python
from dataclasses import dataclass, field


@dataclass
class Team:
    name: str
    members: list[str] = field(default_factory=list)


team1 = Team("A")
team2 = Team("B")

team1.members.append("Alice")
print(team2.members)  # []
```

---

## 十七、常见错误与最佳实践

### 17.1 忘记写 `self`

错误示例：

```python
class Student:
    def show_info():
        print("hello")


student = Student()
# student.show_info()  # TypeError
```

正确写法：

```python
class Student:
    def show_info(self):
        print("hello")
```

### 17.2 把实例属性误写成局部变量

错误示例：

```python
class Student:
    def __init__(self, name):
        name = name
```

正确写法：

```python
class Student:
    def __init__(self, name):
        self.name = name
```

### 17.3 类属性和实例属性混淆

```python
class Counter:
    count = 0

    def __init__(self):
        self.count += 1


c1 = Counter()
c2 = Counter()

print(Counter.count)  # 0，不是 2
print(c1.count)       # 1
print(c2.count)       # 1
```

原因：`self.count += 1` 会在实例上创建或修改实例属性，而不是修改类属性。

正确写法：

```python
class Counter:
    count = 0

    def __init__(self):
        Counter.count += 1
```

更灵活的写法：

```python
class Counter:
    count = 0

    def __init__(self):
        type(self).count += 1
```

### 17.4 不要过度使用继承

继承不是复用代码的唯一方式。继承表达的是“是什么”，组合表达的是“有什么”或“使用什么”。

```python
class EmailSender:
    def send(self, message):
        print(f"发送邮件: {message}")


class NotificationService:
    def __init__(self, sender):
        self.sender = sender

    def notify(self, message):
        self.sender.send(message)
```

### 17.5 类名、方法名、属性名规范

```python
class BankAccount:  # 类名：大驼峰
    bank_name = "Python Bank"  # 类属性：小写加下划线

    def __init__(self, owner_name):  # 方法名：小写加下划线
        self.owner_name = owner_name  # 属性名：小写加下划线
```

### 17.6 让对象保持有效状态

不要让对象轻易进入非法状态。

```python
class BankAccount:
    def __init__(self, owner, balance=0):
        if balance < 0:
            raise ValueError("初始余额不能为负数")
        self.owner = owner
        self.balance = balance

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("取款金额必须大于 0")
        if amount > self.balance:
            raise ValueError("余额不足")
        self.balance -= amount
```

---

## 十八、综合案例：学生管理系统雏形

这个案例把类、对象、实例方法、类方法、封装、魔术方法组合起来。

```python
class Student:
    school = "Python Academy"

    def __init__(self, student_id, name, age, score):
        self.student_id = student_id
        self.name = name
        self.age = age
        self._score = score

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, value):
        if not 0 <= value <= 100:
            raise ValueError("成绩必须在 0 到 100 之间")
        self._score = value

    def is_passed(self):
        return self.score >= 60

    def update_score(self, score):
        self.score = score

    def __str__(self):
        status = "及格" if self.is_passed() else "不及格"
        return f"{self.student_id} - {self.name} - {self.score}分 - {status}"


class StudentManager:
    def __init__(self):
        self.students = {}

    def add_student(self, student):
        if student.student_id in self.students:
            raise ValueError("学生编号已存在")
        self.students[student.student_id] = student

    def remove_student(self, student_id):
        if student_id not in self.students:
            raise KeyError("学生不存在")
        del self.students[student_id]

    def find_student(self, student_id):
        return self.students.get(student_id)

    def list_students(self):
        return list(self.students.values())

    def average_score(self):
        if not self.students:
            return 0
        total = sum(student.score for student in self.students.values())
        return total / len(self.students)


manager = StudentManager()

manager.add_student(Student("S001", "Alice", 18, 95))
manager.add_student(Student("S002", "Bob", 19, 58))
manager.add_student(Student("S003", "Charlie", 18, 82))

for student in manager.list_students():
    print(student)

print(f"平均分: {manager.average_score():.2f}")

student = manager.find_student("S002")
if student:
    student.update_score(66)
    print(student)
```

这个案例中的设计：

1. `Student` 负责描述单个学生。
2. `StudentManager` 负责管理多个学生。
3. `score` 使用 `@property` 做范围校验。
4. `__str__` 控制学生对象被打印时的展示效果。
5. 学生集合使用字典保存，方便通过学号查找。

---

## 十九、练习题

### 练习 1：定义一个书籍类

要求：

1. 类名为 `Book`。
2. 属性包括 `title`、`author`、`price`。
3. 定义 `show_info()` 方法，打印书籍信息。
4. 创建两个书籍对象并调用方法。

参考结构：

```python
class Book:
    pass
```

### 练习 2：银行账户类

要求：

1. 类名为 `BankAccount`。
2. 属性包括 `owner` 和 `balance`。
3. 方法包括 `deposit()`、`withdraw()`、`show_balance()`。
4. 取款时余额不足要给出提示。
5. 存款和取款金额不能小于等于 0。

### 练习 3：使用类属性统计对象数量

要求：

1. 定义 `User` 类。
2. 每创建一个用户，对象数量加 1。
3. 提供类方法 `get_count()` 返回用户数量。

### 练习 4：继承练习

要求：

1. 定义父类 `Shape`，包含 `area()` 方法。
2. 定义子类 `Rectangle` 和 `Circle`。
3. 分别重写 `area()` 方法。
4. 编写函数 `print_area(shape)`，传入不同形状对象并打印面积。

### 练习 5：商品类与 `@property`

要求：

1. 定义 `Product` 类。
2. 属性包括 `name` 和 `price`。
3. 使用 `@property` 控制 `price`，禁止价格为负数。
4. 定义 `discount(rate)` 方法，返回打折后的价格。

---

## 二十、速查表

### 20.1 基础语法

```python
class 类名:
    类属性 = 值

    def __init__(self, 参数):
        self.实例属性 = 参数

    def 实例方法(self):
        pass
```

### 20.2 创建对象

```python
obj = 类名(参数)
```

### 20.3 访问属性和方法

```python
obj.name
obj.method()
```

### 20.4 类方法

```python
class Demo:
    @classmethod
    def method(cls):
        pass
```

### 20.5 静态方法

```python
class Demo:
    @staticmethod
    def method():
        pass
```

### 20.6 继承

```python
class Child(Parent):
    pass
```

### 20.7 调用父类方法

```python
super().__init__()
```

### 20.8 属性控制

```python
class Product:
    def __init__(self, price):
        self.price = price

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        if value < 0:
            raise ValueError("价格不能为负数")
        self._price = value
```

### 20.9 面向对象三大特性

| 特性 | 含义 | Python 示例 |
| --- | --- | --- |
| 封装 | 隐藏内部细节，对外提供接口 | `_password`、`@property` |
| 继承 | 子类复用和扩展父类能力 | `class Dog(Animal)` |
| 多态 | 同一方法，不同对象有不同表现 | `animal.speak()` |

### 20.10 一句话总结

类是模板，对象是实例；属性描述对象有什么，方法描述对象能做什么。面向对象的关键不是把所有代码都塞进类里，而是用类表达清晰的业务概念，让数据和行为自然地组织在一起。
