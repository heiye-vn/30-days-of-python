# Python 面向对象编程：设计思维与实战指南

> 前两篇教程（`Python类与对象.md` 和 `Python高级面向对象特性.md`）讲了 OOP 的"语法"——类怎么定义、继承怎么写、魔术方法怎么用。这一篇换一个角度：站在**资深工程师**的视角，讲"怎么想"和"怎么设计"。学完语法之后，真正难的是——面对一个需求时，如何拆出合理的类、划清职责边界、写出扩展性好的代码。

---

## 目录

- [一、OOP 的核心思想：像搭积木一样写程序](#一oop-的核心思想像搭积木一样写程序)
  - [1.1 从"写过程"到"搭积木"](#11-从写过程到搭积木)
  - [1.2 对象的本质：数据 + 行为 + 身份](#12-对象的本质数据--行为--身份)
  - [1.3 类设计的黄金法则：高内聚、低耦合](#13-类设计的黄金法则高内聚低耦合)
- [二、类之间的关系](#二类之间的关系)
  - [2.1 关联（Association）](#21-关联association)
  - [2.2 聚合（Aggregation）](#22-聚合aggregation)
  - [2.3 组合（Composition）](#23-组合composition)
  - [2.4 继承（Inheritance）](#24-继承inheritance)
  - [2.5 依赖（Dependency）](#25-依赖dependency)
  - [2.6 关系强度对比](#26-关系强度对比)
- [三、面向对象设计原则（SOLID）](#三面向对象设计原则solid)
  - [3.1 单一职责原则（SRP）](#31-单一职责原则srp)
  - [3.2 开闭原则（OCP）](#32-开闭原则ocp)
  - [3.3 里氏替换原则（LSP）](#33-里氏替换原则lsp)
  - [3.4 接口隔离原则（ISP）](#34-接口隔离原则isp)
  - [3.5 依赖倒置原则（DIP）](#35-依赖倒置原则dip)
- [四、常用设计模式（Python 实战版）](#四常用设计模式python-实战版)
  - [4.1 工厂模式（Factory）](#41-工厂模式factory)
  - [4.2 策略模式（Strategy）](#42-策略模式strategy)
  - [4.3 观察者模式（Observer）](#43-观察者模式observer)
  - [4.4 单例模式（Singleton）](#44-单例模式singleton)
  - [4.5 装饰器模式（Decorator）](#45-装饰器模式decorator)
  - [4.6 建造者模式（Builder）](#46-建造者模式builder)
  - [4.7 适配器模式（Adapter）](#47-适配器模式adapter)
  - [4.8 设计模式速查表](#48-设计模式速查表)
- [五、组合优于继承：最重要的设计直觉](#五组合优于继承最重要的设计直觉)
  - [5.1 继承的常见滥用](#51-继承的常见滥用)
  - [5.2 用组合替代继承](#52-用组合替代继承)
  - [5.3 Mixin：轻量级能力注入](#53-mixin轻量级能力注入)
- [六、面向对象建模实战：从需求到类图](#六面向对象建模实战从需求到类图)
  - [6.1 需求分析](#61-需求分析)
  - [6.2 识别类和对象](#62-识别类和对象)
  - [6.3 确定属性和方法](#63-确定属性和方法)
  - [6.4 确定类之间的关系](#64-确定类之间的关系)
  - [6.5 代码实现](#65-代码实现)
- [七、OOP 反模式：新手最容易踩的坑](#七oop-反模式新手最容易踩的坑)
  - [7.1 上帝类（God Class）](#71-上帝类god-class)
  - [7.2 贫血模型（Anemic Model）](#72-贫血模型anemic-model)
  - [7.3 过度继承](#73-过度继承)
  - [7.4 紧耦合](#74-紧耦合)
  - [7.5 可变共享状态](#75-可变共享状态)
- [八、OOP vs 函数式 vs 过程式：什么时候用什么](#八oop-vs-函数式-vs-过程式什么时候用什么)
- [九、综合项目：任务调度系统](#九综合项目任务调度系统)
- [十、学习路线图与推荐阅读](#十学习路线图与推荐阅读)
- [十一、速查表](#十一速查表)

---

## 一、OOP 的核心思想：像搭积木一样写程序

### 1.1 从"写过程"到"搭积木"

初学者写代码通常是"过程式"思维——从上往下一步步执行：

```python
# 过程式：一步步操作数据
user_name = input("用户名: ")
user_email = input("邮箱: ")

# 校验
if len(user_name) < 3:
    print("用户名太短")
if "@" not in user_email:
    print("邮箱格式错误")

# 保存
with open("users.txt", "a") as f:
    f.write(f"{user_name},{user_email}\n")

# 发通知
send_welcome_email(user_email)
```

这种方式写小脚本没问题。但当程序变复杂时，数据和操作散落各处，改一处可能牵连十处。

OOP 的思路完全不同：**先把程序拆成一个个"角色"，每个角色管好自己的数据，做自己的事情，角色之间通过清晰的接口协作。**

```python
# OOP：角色各司其职
user = User(name="张三", email="zhangsan@example.com")
validator = UserValidator()
repository = UserRepository("users.txt")
notifier = EmailNotifier()

validator.validate(user)          # 校验是校验员的职责
repository.save(user)             # 存储是仓库的职责
notifier.send_welcome(user)       # 通知是通知员的职责
```

这就像搭积木：每块积木（类）有明确的形状和接口，拼在一起就能构建出复杂的系统。

### 1.2 对象的本质：数据 + 行为 + 身份

理解对象需要抓住三个要素：

| 要素 | 含义 | 例子（银行账户） |
| --- | --- | --- |
| **身份（Identity）** | 每个对象是独一无二的 | 卡号 6222...1234 的那个账户 |
| **状态（State）** | 对象当前的数据 | 余额 5000 元，户名"张三" |
| **行为（Behavior）** | 对象能做什么 | 存款、取款、查询余额 |

```python
class BankAccount:
    def __init__(self, owner: str, account_no: str, balance: float = 0):
        self.owner = owner          # 状态
        self.account_no = account_no  # 身份标识
        self._balance = balance     # 状态（私有）

    def deposit(self, amount: float):       # 行为
        if amount <= 0:
            raise ValueError("存款金额必须大于 0")
        self._balance += amount

    def withdraw(self, amount: float):      # 行为
        if amount <= 0:
            raise ValueError("取款金额必须大于 0")
        if amount > self._balance:
            raise ValueError("余额不足")
        self._balance -= amount

    @property
    def balance(self) -> float:             # 只读属性
        return self._balance

    def __repr__(self):
        return f"BankAccount('{self.owner}', '{self.account_no}')"
```

关键洞察：**对象不只是"一堆数据"，也不只是"一堆函数"，而是把数据和行为绑成一个整体。** 这也是为什么 `_balance` 用私有属性——外部不应该直接修改余额，必须通过 `deposit` / `withdraw` 这些行为来变更。

### 1.3 类设计的黄金法则：高内聚、低耦合

这六个字是 OOP 设计的终极目标：

**高内聚**：一个类只做一件事，把它做好。

```python
# 高内聚：每个类职责清晰
class Order:
    """只负责订单数据和状态"""
class PaymentProcessor:
    """只负责支付逻辑"""
class ShippingService:
    """只负责发货逻辑"""
```

**低耦合**：类之间的依赖尽可能少，改一个类尽量不影响其他类。

```python
# 低耦合：通过接口协作，不关心具体实现
class Order:
    def __init__(self, payment_processor):
        self._payment = payment_processor  # 依赖抽象，不依赖具体类

    def checkout(self, amount):
        self._payment.process(amount)      # 只调用接口，不管内部细节
```

如果 `Order` 直接写死 `AliPayProcessor().process(amount)`，就是高耦合——以后换成微信支付就得改 `Order` 的代码。

---

## 二、类之间的关系

写 OOP 程序，类与类之间不是孤立的。理解它们之间的关系类型，是做好设计的基础。

### 2.1 关联（Association）

两个类之间有"使用"关系，但各自独立生存。

```python
class Teacher:
    def __init__(self, name: str):
        self.name = name

    def teach(self, course):
        print(f"{self.name} 正在教授 {course.name}")

class Course:
    def __init__(self, name: str):
        self.name = name

# 老师和课程有关联，但各自独立
teacher = Teacher("王老师")
course = Course("Python 入门")
teacher.teach(course)
```

### 2.2 聚合（Aggregation）

整体和部分的关系，但部分可以脱离整体独立存在。用"空心菱形"表示。

```python
class Department:
    def __init__(self, name: str):
        self.name = name
        self.employees: list[Employee] = []

    def add_employee(self, emp: "Employee"):
        self.employees.append(emp)

class Employee:
    def __init__(self, name: str):
        self.name = name

# 部门解散了，员工还在（可以转到其他部门）
alice = Employee("Alice")
dept = Department("研发部")
dept.add_employee(alice)
```

### 2.3 组合（Composition）

更强的整体-部分关系，部分不能脱离整体独立存在。用"实心菱形"表示。

```python
class House:
    def __init__(self, address: str):
        self.address = address
        self.rooms: list[Room] = []  # 房间属于房子

    def add_room(self, name: str, area: float):
        self.rooms.append(Room(name, area))

class Room:
    def __init__(self, name: str, area: float):
        self.name = name
        self.area = area

# 房子拆了，房间也就不存在了
house = House("北京市xx小区")
house.add_room("客厅", 30.0)
house.add_room("卧室", 15.0)
```

### 2.4 继承（Inheritance）

"is-a"关系：子类是父类的一种特殊形式。

```python
class Vehicle:
    def move(self): ...

class Car(Vehicle):       # Car is-a Vehicle
    def move(self): print("汽车在路上行驶")

class Ship(Vehicle):      # Ship is-a Vehicle
    def move(self): print("轮船在水上航行")
```

### 2.5 依赖（Dependency）

最弱的关系，一个类在某个方法中临时使用了另一个类。

```python
class Report:
    def export(self, formatter):
        # Report 临时依赖 formatter，用完就扔
        return formatter.format(self.data)
```

### 2.6 关系强度对比

从弱到强排列：

```text
依赖 → 关联 → 聚合 → 组合 → 继承
最弱                          最强
```

**设计原则：优先使用弱的关系。** 继承是最强的关系，意味着最大的耦合，所以有"组合优于继承"这条经典建议（后面会详细展开）。

---

## 三、面向对象设计原则（SOLID）

SOLID 是五条经过大量实践验证的设计原则，由 Robert C. Martin（"Uncle Bob"）提出。它们不是"必须遵守的法律"，而是帮你写出好设计的思维工具。

### 3.1 单一职责原则（SRP）

> 一个类应该只有一个引起它变化的原因。

通俗说：**一个类只管一件事。**

```python
# 违反 SRP：一个类干了太多事
class UserManager:
    def save_to_db(self, user): ...
    def send_email(self, user): ...
    def generate_report(self): ...
    def validate_input(self, data): ...
```

```python
# 遵守 SRP：拆分职责
class UserRepository:
    """只管数据库存取"""
    def save(self, user): ...
    def find_by_id(self, user_id): ...

class EmailService:
    """只管发邮件"""
    def send_welcome(self, user): ...
    def send_reset(self, user): ...

class UserValidator:
    """只管校验"""
    def validate(self, data) -> list[str]: ...
```

好处：改数据库逻辑不影响发邮件，改邮件模板不影响数据校验。每个类都很小，改起来心里有底。

### 3.2 开闭原则（OCP）

> 软件应该对扩展开放，对修改关闭。

通俗说：**加新功能时，应该"加代码"而不是"改代码"。**

```python
# 违反 OCP：每次加新支付方式都要改这个函数
def process_payment(method: str, amount: float):
    if method == "alipay":
        print(f"支付宝支付 {amount} 元")
    elif method == "wechat":
        print(f"微信支付 {amount} 元")
    # 明天加 Apple Pay？后天加数字货币？得一直改这里
```

```python
# 遵守 OCP：加新支付方式只需新建类，不改旧代码
from abc import ABC, abstractmethod

class PaymentMethod(ABC):
    @abstractmethod
    def pay(self, amount: float): ...

class AlipayPayment(PaymentMethod):
    def pay(self, amount: float):
        print(f"支付宝支付 {amount} 元")

class WechatPayment(PaymentMethod):
    def pay(self, amount: float):
        print(f"微信支付 {amount} 元")

# 扩展：只需新建类
class ApplePayPayment(PaymentMethod):
    def pay(self, amount: float):
        print(f"Apple Pay 支付 {amount} 元")

# 使用方不需要关心具体是哪种支付
def checkout(payment: PaymentMethod, amount: float):
    payment.pay(amount)

checkout(AlipayPayment(), 100)
checkout(ApplePayPayment(), 200)
```

### 3.3 里氏替换原则（LSP）

> 子类对象应该能替换父类对象，程序不会出错。

通俗说：**子类不能"缩水"父类的能力。**

```python
# 违反 LSP 的经典案例
class Rectangle:
    def __init__(self):
        self._width = 0
        self._height = 0

    def set_width(self, w):  self._width = w
    def set_height(self, h): self._height = h
    def area(self):          return self._width * self._height

class Square(Rectangle):
    """正方形继承矩形，但违反了 LSP"""
    def set_width(self, w):
        self._width = w
        self._height = w   # 强制宽=高，改变了矩形的行为

    def set_height(self, h):
        self._width = h
        self._height = h

def test_area(shape: Rectangle):
    shape.set_width(5)
    shape.set_height(4)
    assert shape.area() == 20  # 传入 Square 时这里会变成 16，测试失败！
```

正方形不是矩形的合理子类（在这个接口设计下），因为矩形的 `set_width` 和 `set_height` 是独立的，正方形打破了这个约定。

修正方案：让它们共享一个 `Shape` 抽象父类，而不是让正方形继承矩形。

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self) -> float: ...

class Rectangle(Shape):
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height
    def area(self): return self.width * self.height

class Square(Shape):
    def __init__(self, side: float):
        self.side = side
    def area(self): return self.side ** 2
```

### 3.4 接口隔离原则（ISP）

> 客户端不应该被迫依赖它不使用的接口。

通俗说：**接口要小而专，不要大而全。**

```python
# 违反 ISP：一个大接口，强迫所有实现者实现全部方法
class Worker(ABC):
    @abstractmethod
    def work(self): ...
    @abstractmethod
    def eat(self): ...
    @abstractmethod
    def sleep(self): ...

class Robot(Worker):
    def work(self): print("机器人工作中")
    def eat(self): raise NotImplementedError("机器人不吃饭")  # 被迫实现不需要的方法
    def sleep(self): raise NotImplementedError("机器人不睡觉")
```

```python
# 遵守 ISP：拆分成小接口
class Workable(ABC):
    @abstractmethod
    def work(self): ...

class Eatable(ABC):
    @abstractmethod
    def eat(self): ...

class HumanWorker(Workable, Eatable):
    def work(self): print("人类工作中")
    def eat(self): print("人类吃饭中")

class RobotWorker(Workable):       # 只需要 Workable
    def work(self): print("机器人工作中")
```

### 3.5 依赖倒置原则（DIP）

> 高层模块不应该依赖低层模块，两者都应该依赖抽象。

通俗说：**别写死"我要用哪个具体实现"，而是说"我需要一个能做某事的东西"。**

```python
# 违反 DIP：高层直接依赖具体低层
class NotificationService:
    def __init__(self):
        self.smtp = SMTPMailer()     # 写死了用 SMTP

    def notify(self, user, message):
        self.smtp.send(user.email, message)
```

```python
# 遵守 DIP：依赖抽象接口
class MessageSender(ABC):
    @abstractmethod
    def send(self, to: str, content: str): ...

class SMTPSender(MessageSender):
    def send(self, to: str, content: str):
        print(f"SMTP 发送到 {to}: {content}")

class SlackSender(MessageSender):
    def send(self, to: str, content: str):
        print(f"Slack 发送到 {to}: {content}")

class NotificationService:
    def __init__(self, sender: MessageSender):  # 依赖抽象
        self._sender = sender

    def notify(self, user_email: str, message: str):
        self._sender.send(user_email, message)

# 注入不同的实现
service1 = NotificationService(SMTPSender())
service2 = NotificationService(SlackSender())
```

这就是**依赖注入**（Dependency Injection）——不在类内部创建依赖，而是从外部传进来。它让代码更容易测试（可以传入 Mock 对象）和更容易切换实现。

---

## 四、常用设计模式（Python 实战版）

设计模式是经过反复验证的"解决特定问题的通用方案"。不需要死记硬背 23 种 GoF 模式，先掌握最常用的几种就够。

### 4.1 工厂模式（Factory）

**场景**：创建对象时，不想让调用方知道具体创建哪个类。

```python
class Logger(ABC):
    @abstractmethod
    def log(self, message: str): ...

class FileLogger(Logger):
    def log(self, message: str):
        with open("app.log", "a", encoding="utf-8") as f:
            f.write(message + "\n")

class ConsoleLogger(Logger):
    def log(self, message: str):
        print(f"[LOG] {message}")

class DatabaseLogger(Logger):
    def log(self, message: str):
        print(f"[DB LOG] INSERT INTO logs VALUES ('{message}')")

# 工厂函数
def create_logger(log_type: str) -> Logger:
    loggers = {
        "file": FileLogger,
        "console": ConsoleLogger,
        "database": DatabaseLogger,
    }
    if log_type not in loggers:
        raise ValueError(f"未知日志类型: {log_type}")
    return loggers[log_type]()

# 使用方不需要知道具体类
logger = create_logger("console")
logger.log("应用启动")
```

Python 中工厂可以是一个简单的函数，不需要像 Java 那样搞一个 `LoggerFactory` 类。

### 4.2 策略模式（Strategy）

**场景**：同一个操作有多种算法，运行时选择用哪种。

```python
class SortStrategy(ABC):
    @abstractmethod
    def sort(self, data: list) -> list: ...

class BubbleSort(SortStrategy):
    def sort(self, data: list) -> list:
        arr = data.copy()
        n = len(arr)
        for i in range(n):
            for j in range(0, n - i - 1):
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
        return arr

class QuickSort(SortStrategy):
    def sort(self, data: list) -> list:
        if len(data) <= 1:
            return data
        pivot = data[len(data) // 2]
        left = [x for x in data if x < pivot]
        middle = [x for x in data if x == pivot]
        right = [x for x in data if x > pivot]
        return self.sort(left) + middle + self.sort(right)

class Sorter:
    def __init__(self, strategy: SortStrategy = None):
        self._strategy = strategy or QuickSort()

    def set_strategy(self, strategy: SortStrategy):
        self._strategy = strategy

    def sort(self, data: list) -> list:
        return self._strategy.sort(data)

# 运行时切换策略
sorter = Sorter()
data = [64, 34, 25, 12, 22, 11, 90]

print(sorter.sort(data))             # 默认快排
sorter.set_strategy(BubbleSort())
print(sorter.sort(data))             # 切换成冒泡
```

Python 的函数是一等公民，策略模式还可以更简洁——直接传函数：

```python
# Pythonic 写法：用函数替代策略类
def bubble_sort(data): return sorted(data)  # 简化演示
def quick_sort(data):  return sorted(data)

sorter_func = quick_sort
result = sorter_func([64, 34, 25, 12, 22])
```

### 4.3 观察者模式（Observer）

**场景**：一个对象状态变化时，自动通知所有关心它的对象。

```python
from typing import Protocol

class Observer(Protocol):
    def update(self, event: str, data: dict): ...

class EventBus:
    """事件总线：发布-订阅"""
    def __init__(self):
        self._listeners: dict[str, list[Observer]] = {}

    def subscribe(self, event: str, observer: Observer):
        self._listeners.setdefault(event, []).append(observer)

    def unsubscribe(self, event: str, observer: Observer):
        if event in self._listeners:
            self._listeners[event].remove(observer)

    def publish(self, event: str, data: dict = None):
        for observer in self._listeners.get(event, []):
            observer.update(event, data or {})

# 观察者实现
class EmailNotifier:
    def update(self, event: str, data: dict):
        print(f"[邮件] 事件 {event}: 给用户 {data.get('user', '?')} 发送通知")

class LogRecorder:
    def update(self, event: str, data: dict):
        print(f"[日志] 记录事件 {event}: {data}")

class MetricsCollector:
    def update(self, event: str, data: dict):
        print(f"[指标] 统计事件 {event}")

# 使用
bus = EventBus()
bus.subscribe("user.registered", EmailNotifier())
bus.subscribe("user.registered", LogRecorder())
bus.subscribe("order.created", MetricsCollector())

bus.publish("user.registered", {"user": "张三", "email": "zs@example.com"})
# [邮件] 事件 user.registered: 给用户 张三 发送通知
# [日志] 记录事件 user.registered: {'user': '张三', 'email': 'zs@example.com'}
```

观察者模式在 GUI 事件处理、消息队列、响应式编程中非常常见。

### 4.4 单例模式（Singleton）

**场景**：确保某个类只有一个实例，全局共享。

```python
class AppConfig:
    """应用配置：全局只需要一份"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._settings = {}
        return cls._instance

    def set(self, key: str, value):
        self._settings[key] = value

    def get(self, key: str, default=None):
        return self._settings.get(key, default)

# 不管创建多少次，都是同一个对象
config1 = AppConfig()
config2 = AppConfig()
print(config1 is config2)  # True

config1.set("debug", True)
print(config2.get("debug"))  # True
```

Pythonic 替代方案：用模块级变量也可以实现单例效果。

```python
# settings.py（模块本身就是天然的单例）
_settings = {}

def set(key, value):
    _settings[key] = value

def get(key, default=None):
    return _settings.get(key, default)
```

### 4.5 装饰器模式（Decorator）

**场景**：动态给对象添加额外功能，而不改变原始类。

```python
class TextProcessor(ABC):
    @abstractmethod
    def process(self, text: str) -> str: ...

class PlainText(TextProcessor):
    def process(self, text: str) -> str:
        return text

class UpperCaseDecorator(TextProcessor):
    def __init__(self, wrapped: TextProcessor):
        self._wrapped = wrapped

    def process(self, text: str) -> str:
        return self._wrapped.process(text).upper()

class TrimDecorator(TextProcessor):
    def __init__(self, wrapped: TextProcessor):
        self._wrapped = wrapped

    def process(self, text: str) -> str:
        return self._wrapped.process(text).strip()

class ReverseDecorator(TextProcessor):
    def __init__(self, wrapped: TextProcessor):
        self._wrapped = wrapped

    def process(self, text: str) -> str:
        return self._wrapped.process(text)[::-1]

# 像套娃一样层层包装
processor = PlainText()
processor = UpperCaseDecorator(processor)    # 先转大写
processor = TrimDecorator(processor)         # 再去空格

result = processor.process("  hello world  ")
print(result)  # "HELLO WORLD"
```

Python 的函数装饰器（`@decorator`）其实就是装饰器模式的语法糖。

### 4.6 建造者模式（Builder）

**场景**：创建复杂对象时，参数太多导致构造函数难以使用。

```python
from dataclasses import dataclass, field

@dataclass
class HttpRequest:
    method: str
    url: str
    headers: dict = field(default_factory=dict)
    params: dict = field(default_factory=dict)
    body: str = ""
    timeout: int = 30

class HttpRequestBuilder:
    def __init__(self, method: str, url: str):
        self._request = HttpRequest(method=method, url=url)

    def header(self, key: str, value: str):
        self._request.headers[key] = value
        return self  # 返回 self 支持链式调用

    def param(self, key: str, value: str):
        self._request.params[key] = value
        return self

    def body(self, body: str):
        self._request.body = body
        return self

    def timeout(self, seconds: int):
        self._request.timeout = seconds
        return self

    def build(self) -> HttpRequest:
        return self._request

# 链式构建，清晰可读
request = (HttpRequestBuilder("POST", "https://api.example.com/users")
    .header("Content-Type", "application/json")
    .header("Authorization", "Bearer token123")
    .param("format", "json")
    .body('{"name": "张三", "age": 25}')
    .timeout(60)
    .build())

print(request)
```

### 4.7 适配器模式（Adapter）

**场景**：已有类的接口和期望的接口不一致，需要一个"转换器"。

```python
# 已有的旧接口
class OldPaymentGateway:
    def charge(self, card_number: str, amount_cents: int):
        print(f"刷卡 {card_number}，扣费 {amount_cents} 分")

# 期望的新接口
class PaymentProcessor(ABC):
    @abstractmethod
    def pay(self, user_id: str, amount_yuan: float): ...

# 适配器：把旧接口适配成新接口
class PaymentAdapter(PaymentProcessor):
    def __init__(self, gateway: OldPaymentGateway, user_card_map: dict):
        self._gateway = gateway
        self._user_cards = user_card_map

    def pay(self, user_id: str, amount_yuan: float):
        card = self._user_cards.get(user_id)
        if not card:
            raise ValueError(f"用户 {user_id} 未绑定银行卡")
        # 转换：元 → 分
        self._gateway.charge(card, int(amount_yuan * 100))

# 使用
gateway = OldPaymentGateway()
adapter = PaymentAdapter(gateway, {"user_001": "6222-1234-5678"})
adapter.pay("user_001", 99.9)  # 内部自动转换为 9990 分
```

### 4.8 设计模式速查表

| 模式 | 解决什么问题 | Python 中的典型场景 |
| --- | --- | --- |
| 工厂 | 不想暴露创建细节 | 日志器、数据库连接、解析器 |
| 策略 | 同一操作多种算法 | 排序、压缩、加密、支付方式 |
| 观察者 | 状态变更自动通知 | 事件总线、消息队列、GUI 事件 |
| 单例 | 全局唯一实例 | 配置管理、连接池、日志器 |
| 装饰器 | 动态添加功能 | 中间件、缓存、权限检查、日志 |
| 建造者 | 复杂对象分步构建 | HTTP 请求、SQL 查询、报表 |
| 适配器 | 接口不兼容时转换 | 第三方 API 封装、遗留系统对接 |
| 代理 | 控制对象访问 | 懒加载、权限控制、缓存 |
| 模板方法 | 骨架相同，细节不同 | 数据处理管线、测试基类 |

---

## 五、组合优于继承：最重要的设计直觉

"Composition over Inheritance"是 OOP 中被低估最多、误解最多的一条建议。

### 5.1 继承的常见滥用

```python
# 用继承来"复用代码"——看起来很省事，实际很危险
class Animal:
    def eat(self): print("吃东西")
    def sleep(self): print("睡觉")
    def make_sound(self): raise NotImplementedError

class Dog(Animal):
    def make_sound(self): print("汪汪")
    def fetch(self): print("捡球")

class Robot:
    def eat(self): print("充电")      # 机器人"吃"电？
    def sleep(self): print("待机")    # 机器人"睡"觉？
    def make_sound(self): print("嘟嘟")

# Robot 继承 Animal 不合适——机器人不是动物
# 但为了复用 eat/sleep 的代码而继承，这就是滥用
```

继承表达的是"is-a"关系（狗是动物），不是为了"省几行代码"。当你继承只是为了复用代码，而不是因为子类确实是父类的一种，就该用组合。

### 5.2 用组合替代继承

```python
# 把"能力"拆成独立组件，通过组合来装配
class EatBehavior:
    def eat(self): print("吃东西")

class ChargeBehavior:
    def eat(self): print("充电")

class SleepBehavior:
    def sleep(self): print("睡觉")

class StandbyBehavior:
    def sleep(self): print("待机")

class SoundBehavior:
    def __init__(self, sound: str):
        self.sound = sound
    def make_sound(self): print(self.sound)

# 通过组合装配行为
class Dog:
    def __init__(self):
        self._eat = EatBehavior()
        self._sleep = SleepBehavior()
        self._sound = SoundBehavior("汪汪")

    def eat(self):        self._eat.eat()
    def sleep(self):      self._sleep.sleep()
    def make_sound(self): self._sound.make_sound()

class Robot:
    def __init__(self):
        self._eat = ChargeBehavior()      # 充电代替吃饭
        self._sleep = StandbyBehavior()    # 待机代替睡觉
        self._sound = SoundBehavior("嘟嘟")

    def eat(self):        self._eat.eat()
    def sleep(self):      self._sleep.sleep()
    def make_sound(self): self._sound.make_sound()
```

这种"行为组件"的写法在游戏开发中非常常见（Entity-Component-System 模式）。好处是：新增一种行为只需写一个新类，修改某个行为不影响其他行为。

### 5.3 Mixin：轻量级能力注入

当你确实需要"给多个不相关的类添加某个小能力"时，Python 的 Mixin 是一种优雅的折中。

```python
class JsonMixin:
    """给任何类添加 JSON 序列化能力"""
    def to_json(self) -> str:
        import json
        return json.dumps(self.__dict__, ensure_ascii=False)

class LogMixin:
    """给任何类添加日志能力"""
    def log(self, message: str):
        print(f"[{self.__class__.__name__}] {message}")

# 按需混入
class User(JsonMixin, LogMixin):
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email

user = User("张三", "zs@example.com")
user.log("用户创建成功")        # [User] 用户创建成功
print(user.to_json())          # {"name": "张三", "email": "zs@example.com"}
```

Mixin 的规则：

- Mixin 类不应该有 `__init__`（或者 `__init__` 参数极少）。
- Mixin 类不应该继承其他非 Mixin 类。
- Mixin 的名字通常以 `Mixin` 结尾，表明它的用途。

---

## 六、面向对象建模实战：从需求到类图

下面模拟一个真实需求，演示从"需求描述"到"代码实现"的完整思考过程。

### 6.1 需求分析

> 开发一个简易图书管理系统：用户可以搜索图书、借阅图书、归还图书。系统需要记录借阅历史，超期未还要收取罚款。管理员可以添加图书、查看借阅统计。

### 6.2 识别类和对象

从需求描述中提取名词，候选类就藏在里面：

| 需求中的名词 | 是否建模为类 | 理由 |
| --- | --- | --- |
| 图书 | ✅ `Book` | 核心实体，有自己的属性和行为 |
| 用户 | ✅ `User` | 核心实体 |
| 管理员 | ✅ `Admin`（User 的子类或角色） | 有特殊权限 |
| 借阅记录 | ✅ `BorrowRecord` | 独立的业务实体 |
| 罚款 | ✅ `Fine` | 有自己的计算逻辑 |
| 搜索 | ❌ 不需要类 | 是行为，放在 Library 或 Book 的方法中 |
| 统计 | ❌ 不需要类 | 是行为，放在 Library 的方法中 |
| 系统 | ✅ `Library` | 作为整体协调者 |

### 6.3 确定属性和方法

```python
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

class BookStatus(Enum):
    AVAILABLE = "可借"
    BORROWED = "已借出"
    LOST = "遗失"

@dataclass
class Book:
    isbn: str
    title: str
    author: str
    status: BookStatus = BookStatus.AVAILABLE
    daily_fine: float = 0.5  # 每天罚款金额

    def __str__(self):
        return f"《{self.title}》({self.author}) [{self.status.value}]"

@dataclass
class BorrowRecord:
    book: Book
    borrower_name: str
    borrow_date: datetime = field(default_factory=datetime.now)
    due_days: int = 14  # 借期 14 天
    return_date: datetime = None

    @property
    def due_date(self) -> datetime:
        return self.borrow_date + timedelta(days=self.due_days)

    @property
    def is_overdue(self) -> bool:
        if self.return_date:
            return self.return_date > self.due_date
        return datetime.now() > self.due_date

    @property
    def fine_amount(self) -> float:
        if not self.is_overdue:
            return 0.0
        end = self.return_date or datetime.now()
        overdue_days = (end - self.due_date).days
        return overdue_days * self.book.daily_fine

    def return_book(self):
        self.return_date = datetime.now()
        self.book.status = BookStatus.AVAILABLE
```

### 6.4 确定类之间的关系

```text
Library "拥有" 多个 Book        → 组合关系
Library "管理" 多个 BorrowRecord → 聚合关系
User "产生" BorrowRecord         → 关联关系
BorrowRecord "引用" Book         → 依赖关系
Admin is-a User                  → 继承关系
```

### 6.5 代码实现

```python
class Library:
    """图书馆：系统核心协调者"""

    def __init__(self, name: str):
        self.name = name
        self._books: dict[str, Book] = {}          # isbn → Book
        self._records: list[BorrowRecord] = []

    def add_book(self, book: Book):
        self._books[book.isbn] = book

    def search(self, keyword: str) -> list[Book]:
        keyword = keyword.lower()
        return [
            b for b in self._books.values()
            if keyword in b.title.lower() or keyword in b.author.lower()
        ]

    def borrow(self, isbn: str, borrower: str) -> BorrowRecord:
        book = self._books.get(isbn)
        if not book:
            raise ValueError(f"图书 {isbn} 不存在")
        if book.status != BookStatus.AVAILABLE:
            raise ValueError(f"{book.title} 当前不可借")

        book.status = BookStatus.BORROWED
        record = BorrowRecord(book=book, borrower_name=borrower)
        self._records.append(record)
        return record

    def return_book(self, isbn: str) -> dict:
        for record in reversed(self._records):
            if record.book.isbn == isbn and record.return_date is None:
                record.return_book()
                fine = record.fine_amount
                return {"record": record, "fine": fine}
        raise ValueError(f"未找到 {isbn} 的借阅记录")

    def get_statistics(self) -> dict:
        total = len(self._records)
        overdue = sum(1 for r in self._records if r.is_overdue and not r.return_date)
        total_fines = sum(r.fine_amount for r in self._records)
        return {
            "总借阅次数": total,
            "当前逾期未还": overdue,
            "累计罚款": total_fines,
            "馆藏图书": len(self._books),
        }

# 使用演示
lib = Library("城市图书馆")
lib.add_book(Book("978-0-1", "Python 编程", "Guido"))
lib.add_book(Book("978-0-2", "算法导论", "CLRS"))

record = lib.borrow("978-0-1", "张三")
print(record)

result = lib.return_book("978-0-1")
print(f"归还成功，罚款: {result['fine']} 元")
print(lib.get_statistics())
```

---

## 七、OOP 反模式：新手最容易踩的坑

### 7.1 上帝类（God Class）

一个类干所有事，几千行代码，改一处怕牵动全局。

```python
# 反模式
class System:
    def handle_user_login(self): ...
    def process_payment(self): ...
    def generate_report(self): ...
    def send_notification(self): ...
    def backup_database(self): ...
    # ... 还有 50 个方法
```

解法：按职责拆分，参考 SRP。

### 7.2 贫血模型（Anemic Model）

类只有属性没有行为，所有逻辑都写在"Service"里——类变成了数据容器。

```python
# 贫血模型：Order 只是个数据包
class Order:
    def __init__(self, items, discount):
        self.items = items
        self.discount = discount

# 所有逻辑都在 Service 里
class OrderService:
    def calculate_total(self, order):
        subtotal = sum(item.price * item.qty for item in order.items)
        return subtotal * (1 - order.discount)

    def is_valid(self, order):
        return len(order.items) > 0 and all(item.qty > 0 for item in order.items)
```

```python
# 充血模型：Order 自己管理自己的逻辑
class Order:
    def __init__(self, items, discount=0):
        self.items = items
        self.discount = discount

    @property
    def total(self):
        subtotal = sum(item.price * item.qty for item in self.items)
        return subtotal * (1 - self.discount)

    @property
    def is_valid(self):
        return len(self.items) > 0 and all(item.qty > 0 for item in self.items)

    def add_item(self, item):
        self.items.append(item)

    def apply_discount(self, rate: float):
        if not 0 <= rate <= 1:
            raise ValueError("折扣率必须在 0-1 之间")
        self.discount = rate
```

Service 层不是不能有，但它应该只负责**协调**（调用多个领域对象），而不是把领域对象的行为全部抢过来。

### 7.3 过度继承

层层嵌套，5 层以上的继承链，改底层类影响全局。

```python
# 反模式：过深的继承链
class Entity: ...
class LivingEntity(Entity): ...
class Animal(LivingEntity): ...
class Mammal(Animal): ...
class Dog(Mammal): ...
class GoldenRetriever(Dog): ...
```

解法：保持继承链 2-3 层，用组合代替深层继承。

### 7.4 紧耦合

类之间直接互相引用具体实现，改一个就要改一片。

```python
# 反模式
class Order:
    def checkout(self):
        db = MySQLDatabase()          # 写死数据库
        payment = AlipayProcessor()    # 写死支付方式
        notifier = SMSNotifier()       # 写死通知方式
        # ...
```

解法：依赖注入 + 接口抽象，参考 DIP。

### 7.5 可变共享状态

多个对象共享可变状态，谁都可以改，出 bug 极难排查。

```python
# 反模式
class Config:
    settings = {}   # 类属性，所有实例共享同一个字典

c1 = Config()
c2 = Config()
c1.settings["debug"] = True
print(c2.settings["debug"])  # True —— c2 被意外影响了
```

解法：使用实例属性，或使用不可变数据结构。

```python
# 正确做法
from dataclasses import dataclass, field

@dataclass
class Config:
    settings: dict = field(default_factory=dict)  # 每个实例独立的字典
```

---

## 八、OOP vs 函数式 vs 过程式：什么时候用什么

Python 是多范式语言，三种风格都能写。关键是选对场景：

| 范式 | 核心思想 | 适合场景 | Python 示例 |
| --- | --- | --- | --- |
| 过程式 | 按步骤执行 | 简单脚本、一次性任务 | 数据清洗脚本 |
| OOP | 对象协作 | 有状态的实体、复杂系统 | Web 框架、游戏、GUI |
| 函数式 | 纯函数、不可变 | 数据变换、并行处理 | 数据管道、map/filter |

实战中它们经常混合使用：

```python
# OOP + 函数式的混合
from dataclasses import dataclass
from typing import Callable

@dataclass(frozen=True)  # 不可变 → 函数式
class Transaction:
    amount: float
    category: str
    date: str

class Budget:
    """OOP：有状态的管理器"""
    def __init__(self):
        self._transactions: list[Transaction] = []

    def add(self, t: Transaction):
        self._transactions.append(t)

    # 函数式风格的数据查询
    def total_by_category(self) -> dict[str, float]:
        result = {}
        for t in self._transactions:
            result[t.category] = result.get(t.category, 0) + t.amount
        return result

    def filter_by(self, predicate: Callable[[Transaction], bool]):
        """接受函数作为参数 → 函数式"""
        return [t for t in self._transactions if predicate(t)]

budget = Budget()
budget.add(Transaction(100, "餐饮", "2024-01-01"))
budget.add(Transaction(50, "交通", "2024-01-01"))
budget.add(Transaction(200, "餐饮", "2024-01-02"))

# 用 lambda（函数式风格）过滤
expensive = budget.filter_by(lambda t: t.amount > 80)
print(expensive)
```

经验法则：

- **数据和行为紧密关联** → 用类（OOP）。
- **纯粹的数据变换** → 用函数（函数式）。
- **简单的顺序操作** → 直接写脚本（过程式）。
- **大型项目** → OOP 做骨架，函数式做数据处理。

---

## 九、综合项目：任务调度系统

下面是一个稍大的完整项目，综合运用本教程讲到的设计原则和模式。

```python
"""
任务调度系统
涉及：SOLID 原则、策略模式、观察者模式、建造者模式、组合优于继承
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Protocol


# ---------- 枚举与数据类 ----------

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class TaskStatus(Enum):
    PENDING = "待执行"
    RUNNING = "执行中"
    SUCCESS = "成功"
    FAILED = "失败"
    CANCELLED = "已取消"

@dataclass
class TaskResult:
    success: bool
    message: str
    duration_seconds: float = 0.0
    data: dict = field(default_factory=dict)


# ---------- 事件系统（观察者模式）----------

class EventListener(Protocol):
    def on_event(self, event_type: str, task_id: str, detail: dict): ...

class EventBus:
    def __init__(self):
        self._listeners: dict[str, list[EventListener]] = {}

    def subscribe(self, event_type: str, listener: EventListener):
        self._listeners.setdefault(event_type, []).append(listener)

    def publish(self, event_type: str, task_id: str, detail: dict = None):
        for listener in self._listeners.get(event_type, []):
            listener.on_event(event_type, task_id, detail or {})

class ConsoleLogger:
    def on_event(self, event_type: str, task_id: str, detail: dict):
        time = datetime.now().strftime("%H:%M:%S")
        print(f"  [{time}] [{event_type}] 任务 {task_id}: {detail}")

class MetricsCollector:
    def __init__(self):
        self.counts: dict[str, int] = {}

    def on_event(self, event_type: str, task_id: str, detail: dict):
        self.counts[event_type] = self.counts.get(event_type, 0) + 1


# ---------- 任务执行器（策略模式）----------

class TaskExecutor(ABC):
    """任务执行策略"""
    @abstractmethod
    def execute(self, task_id: str, params: dict) -> TaskResult: ...

class ShellExecutor(TaskExecutor):
    def execute(self, task_id: str, params: dict) -> TaskResult:
        command = params.get("command", "echo hello")
        print(f"    执行 Shell: {command}")
        return TaskResult(True, f"命令 '{command}' 执行完成", 1.2)

class HttpExecutor(TaskExecutor):
    def execute(self, task_id: str, params: dict) -> TaskResult:
        url = params.get("url", "https://example.com")
        method = params.get("method", "GET")
        print(f"    HTTP {method} {url}")
        return TaskResult(True, f"请求 {url} 成功", 0.5, {"status_code": 200})

class PythonExecutor(TaskExecutor):
    def execute(self, task_id: str, params: dict) -> TaskResult:
        func_name = params.get("function", "unknown")
        print(f"    调用 Python 函数: {func_name}")
        return TaskResult(True, f"函数 {func_name} 执行成功", 0.1)


# ---------- 任务与任务构建器（建造者模式）----------

class Task:
    def __init__(self, task_id: str, executor_type: str, params: dict,
                 priority: Priority = Priority.MEDIUM, max_retries: int = 0):
        self.id = task_id
        self.executor_type = executor_type
        self.params = params
        self.priority = priority
        self.max_retries = max_retries
        self.status = TaskStatus.PENDING
        self.retries = 0
        self.result: TaskResult = None

class TaskBuilder:
    def __init__(self, task_id: str):
        self._id = task_id
        self._executor_type = "shell"
        self._params = {}
        self._priority = Priority.MEDIUM
        self._max_retries = 0

    def executor(self, executor_type: str):
        self._executor_type = executor_type
        return self

    def params(self, **kwargs):
        self._params = kwargs
        return self

    def priority(self, p: Priority):
        self._priority = p
        return self

    def retries(self, n: int):
        self._max_retries = n
        return self

    def build(self) -> Task:
        return Task(
            task_id=self._id,
            executor_type=self._executor_type,
            params=self._params,
            priority=self._priority,
            max_retries=self._max_retries,
        )


# ---------- 调度器（核心协调者）----------

class TaskScheduler:
    def __init__(self):
        self._executors: dict[str, TaskExecutor] = {}
        self._tasks: dict[str, Task] = {}
        self._event_bus = EventBus()

    def register_executor(self, name: str, executor: TaskExecutor):
        self._executors[name] = executor

    def subscribe(self, event_type: str, listener: EventListener):
        self._event_bus.subscribe(event_type, listener)

    def submit(self, task: Task):
        self._tasks[task.id] = task
        self._event_bus.publish("task.submitted", task.id,
                                {"priority": task.priority.name})

    def run_task(self, task_id: str):
        task = self._tasks.get(task_id)
        if not task:
            raise ValueError(f"任务 {task_id} 不存在")

        executor = self._executors.get(task.executor_type)
        if not executor:
            raise ValueError(f"未知执行器: {task.executor_type}")

        task.status = TaskStatus.RUNNING
        self._event_bus.publish("task.started", task.id, {})

        try:
            task.result = executor.execute(task.id, task.params)
            task.status = TaskStatus.SUCCESS if task.result.success else TaskStatus.FAILED
        except Exception as e:
            task.result = TaskResult(False, str(e))
            task.status = TaskStatus.FAILED

        if task.status == TaskStatus.FAILED and task.retries < task.max_retries:
            task.retries += 1
            task.status = TaskStatus.PENDING
            self._event_bus.publish("task.retry", task.id,
                                    {"attempt": task.retries})
            self.run_task(task_id)  # 重试
        else:
            self._event_bus.publish(
                f"task.{task.status.value}",
                task.id,
                {"message": task.result.message} if task.result else {},
            )

    def run_all(self):
        # 按优先级排序执行
        sorted_tasks = sorted(
            self._tasks.values(),
            key=lambda t: t.priority.value,
            reverse=True,
        )
        for task in sorted_tasks:
            if task.status == TaskStatus.PENDING:
                self.run_task(task.id)

    def get_report(self) -> dict:
        return {
            "总任务数": len(self._tasks),
            "成功": sum(1 for t in self._tasks.values() if t.status == TaskStatus.SUCCESS),
            "失败": sum(1 for t in self._tasks.values() if t.status == TaskStatus.FAILED),
            "待执行": sum(1 for t in self._tasks.values() if t.status == TaskStatus.PENDING),
        }


# ---------- 运行演示 ----------
if __name__ == "__main__":
    print("=" * 60)
    print("任务调度系统演示")
    print("=" * 60)

    # 创建调度器
    scheduler = TaskScheduler()

    # 注册执行器（策略模式）
    scheduler.register_executor("shell", ShellExecutor())
    scheduler.register_executor("http", HttpExecutor())
    scheduler.register_executor("python", PythonExecutor())

    # 订阅事件（观察者模式）
    logger = ConsoleLogger()
    metrics = MetricsCollector()
    scheduler.subscribe("task.submitted", logger)
    scheduler.subscribe("task.started", logger)
    scheduler.subscribe("task.成功", logger)
    scheduler.subscribe("task.失败", logger)
    scheduler.subscribe("task.submitted", metrics)
    scheduler.subscribe("task.成功", metrics)

    # 构建并提交任务（建造者模式）
    t1 = (TaskBuilder("backup-db")
          .executor("shell")
          .params(command="pg_dump mydb > backup.sql")
          .priority(Priority.HIGH)
          .retries(2)
          .build())

    t2 = (TaskBuilder("health-check")
          .executor("http")
          .params(url="https://api.example.com/health", method="GET")
          .priority(Priority.CRITICAL)
          .build())

    t3 = (TaskBuilder("send-report")
          .executor("python")
          .params(function="generate_daily_report")
          .priority(Priority.LOW)
          .build())

    scheduler.submit(t1)
    scheduler.submit(t2)
    scheduler.submit(t3)

    print("\n--- 开始执行 ---")
    scheduler.run_all()

    print("\n--- 执行报告 ---")
    for k, v in scheduler.get_report().items():
        print(f"  {k}: {v}")

    print(f"\n事件统计: {metrics.counts}")
```

---

## 十、学习路线图与推荐阅读

### 学习路线

```text
第一阶段：语法基础（已在前两篇完成）
  ├── 定义类、创建对象
  ├── __init__、self
  ├── 实例属性 vs 类属性
  ├── 实例方法 / 类方法 / 静态方法
  └── @property

第二阶段：OOP 三大特性（已在前两篇完成）
  ├── 封装
  ├── 继承
  └── 多态

第三阶段：设计思维（本篇重点）
  ├── 类之间的关系
  ├── SOLID 原则
  ├── 组合优于继承
  └── 反模式识别

第四阶段：设计模式（本篇重点）
  ├── 创建型：工厂、建造者、单例
  ├── 结构型：适配器、装饰器
  └── 行为型：策略、观察者

第五阶段：高级特性（已在高级篇完成）
  ├── 魔术方法
  ├── 描述符
  ├── 元类
  └── __init_subclass__

第六阶段：实战积累
  ├── 阅读优秀开源项目源码
  ├── 自己设计一个小系统
  └── 重构一段"烂代码"
```

### 推荐书籍

| 书名 | 作者 | 适合阶段 | 核心价值 |
| --- | --- | --- | --- |
| 《Python 编程：从入门到实践》 | Eric Matthes | 入门 | 全面基础 |
| 《流畅的 Python》 | Luciano Ramalho | 中级 | Python 高级特性与最佳实践 |
| 《Head First 设计模式》 | Freeman 等 | 中级 | 设计模式入门，生动易懂 |
| 《重构：改善既有代码的设计》 | Martin Fowler | 中高级 | 如何把烂代码变好 |
| 《Clean Architecture》 | Robert C. Martin | 高级 | 架构层面的设计原则 |
| 《Design Patterns》（GoF） | Gamma 等 | 高级 | 设计模式的经典原著 |

---

## 十一、速查表

### 设计原则速查

| 原则 | 一句话 | 自检问题 |
| --- | --- | --- |
| SRP | 一个类只做一件事 | 这个类能用一句话描述吗？ |
| OCP | 加新功能不改旧代码 | 加新类型时，需要改 if-else 吗？ |
| LSP | 子类能替换父类 | 子类有没有"缩水"父类行为？ |
| ISP | 接口要小而专 | 实现者是否被迫实现了不需要的方法？ |
| DIP | 依赖抽象不依赖具体 | 类里有没有 `new` 出具体实现？ |

### 关系选择速查

```text
需要复用代码？
  ├── 是"is-a"关系？ → 继承（保持 2-3 层以内）
  ├── 是"has-a"关系？ → 组合（优先选择）
  ├── 只是小能力注入？ → Mixin
  └── 临时使用？ → 依赖（方法参数传入）
```

### 模式选择速查

```text
需要灵活创建对象？ → 工厂 / 建造者
需要运行时切换算法？ → 策略
需要状态变更通知？ → 观察者
需要全局唯一实例？ → 单例
需要动态添加功能？ → 装饰器
需要对接不兼容接口？ → 适配器
```

### OOP 设计自检清单

```text
□ 每个类能用一句话说清楚它做什么吗？（SRP）
□ 加新功能时，需要改已有类的代码吗？（OCP）
□ 有没有超过 3 层的继承链？
□ 子类真的"是一种"父类吗？（LSP）
□ 类之间是否通过接口（抽象类/Protocol）协作？（DIP）
□ 有没有一个类超过 200 行？考虑拆分（God Class）
□ 类的属性有没有被外部直接修改？考虑封装
□ 共享状态是可变对象吗？考虑不可变或实例隔离
```

---

## 结语

面向对象编程不是目的，而是手段。它的终极目标是让代码**容易理解、容易修改、容易测试**。

三条最核心的直觉：

1. **高内聚、低耦合** —— 每个类职责清晰，类之间松耦合。
2. **组合优于继承** —— 优先考虑组合，只在真正是"is-a"关系时才继承。
3. **依赖抽象不依赖具体** —— 面向接口编程，让系统各部分可以独立替换。

语法层面的知识（前两篇）+ 设计思维（本篇）+ 大量练习和源码阅读，三者结合才能真正掌握 OOP。去读一些优秀的 Python 开源项目（Flask、Requests、SQLAlchemy 等），看看高手是怎么组织类的，比单纯看教程收获更大。
