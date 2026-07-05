# -*- coding: utf-8 -*-
"""
Day 21 - Python 类与对象练习
配套教程: Python类与对象.md

练习目录:
  1. 基础: 定义类与对象
  2. 实例属性 vs 类属性
  3. 三种方法 (实例/类/静态)
  4. @property 装饰器
  5. 继承与多态
  6. 魔术方法
  7. 抽象基类 (ABC)
  8. dataclass 数据类
  9. 综合实战: 迷你 Agent 框架
"""

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


# ============================================================
# 练习 1: 基础 - 定义类与对象
# ============================================================

class Student:
    """学生类: 练习 __init__ 和 self"""

    def __init__(self, name: str, age: int, grade: float):
        self.name = name
        self.age = age
        self.grade = grade

    def introduce(self) -> str:
        return f"我叫{self.name}, 今年{self.age}岁, 成绩是{self.grade}分"

    def is_excellent(self) -> bool:
        return self.grade >= 90


def test_student():
    print("=" * 50)
    print("练习 1: 基础类与对象")
    print("=" * 50)

    s1 = Student("小明", 20, 95)
    s2 = Student("小红", 19, 82)

    print(s1.introduce())   # 我叫小明, 今年20岁, 成绩是95分
    print(s2.introduce())   # 我叫小红, 今年19岁, 成绩是82分
    print(f"{s1.name} 是否优秀: {s1.is_excellent()}")  # True
    print(f"{s2.name} 是否优秀: {s2.is_excellent()}")  # False
    print()


# ============================================================
# 练习 2: 实例属性 vs 类属性
# ============================================================

class Employee:
    """员工类: 练习类属性 (计数器) 和实例属性"""

    company = "AI Tech Co."   # 类属性
    total_count = 0           # 类属性: 员工总数

    def __init__(self, name: str, salary: float):
        self.name = name          # 实例属性
        self.salary = salary      # 实例属性
        Employee.total_count += 1

    def info(self) -> str:
        return f"[{self.company}] {self.name}, 薪资: {self.salary}"

    @classmethod
    def get_total_count(cls) -> int:
        return cls.total_count


def test_employee():
    print("=" * 50)
    print("练习 2: 实例属性 vs 类属性")
    print("=" * 50)

    e1 = Employee("张三", 15000)
    e2 = Employee("李四", 20000)
    e3 = Employee("王五", 18000)

    print(e1.info())
    print(e2.info())
    print(f"员工总数: {Employee.get_total_count()}")  # 3
    print(f"类属性访问: {e1.company}")                # AI Tech Co.
    print()


# ============================================================
# 练习 3: 三种方法
# ============================================================

class Config:
    """配置类: 练习实例方法/类方法/静态方法"""

    defaults = {
        "temperature": 0.7,
        "max_tokens": 1000,
        "top_p": 0.9,
    }

    def __init__(self, **kwargs):
        self.settings = dict(self.defaults)
        self.settings.update(kwargs)

    # 实例方法
    def get(self, key: str):
        return self.settings.get(key)

    def set(self, key: str, value):
        if self.is_valid_key(key):
            self.settings[key] = value
        else:
            print(f"警告: 未知配置项 '{key}'")

    # 类方法 - 工厂模式
    @classmethod
    def high_quality(cls) -> "Config":
        return cls(temperature=0.3, max_tokens=2000)

    @classmethod
    def creative(cls) -> "Config":
        return cls(temperature=1.5, max_tokens=4000)

    # 静态方法 - 工具函数
    @staticmethod
    def is_valid_key(key: str) -> bool:
        valid_keys = {"temperature", "max_tokens", "top_p"}
        return key in valid_keys


def test_config():
    print("=" * 50)
    print("练习 3: 三种方法")
    print("=" * 50)

    # 使用类方法创建
    config_hq = Config.high_quality()
    config_creative = Config.creative()

    print(f"高质量模式: temperature={config_hq.get('temperature')}")
    print(f"创意模式: temperature={config_creative.get('temperature')}")

    # 实例方法修改
    config_hq.set("max_tokens", 3000)
    print(f"修改后: max_tokens={config_hq.get('max_tokens')}")

    # 静态方法
    print(f"'temperature' 是否有效: {Config.is_valid_key('temperature')}")
    print(f"'unknown' 是否有效: {Config.is_valid_key('unknown')}")
    print()


# ============================================================
# 练习 4: @property 装饰器
# ============================================================

class Circle:
    """圆形类: 练习 @property 实现计算属性"""

    def __init__(self, radius: float):
        self._radius = radius

    @property
    def radius(self) -> float:
        return self._radius

    @radius.setter
    def radius(self, value: float):
        if value < 0:
            raise ValueError("半径不能为负数")
        self._radius = value

    @property
    def area(self) -> float:
        return math.pi * self._radius ** 2

    @property
    def circumference(self) -> float:
        return 2 * math.pi * self._radius

    @property
    def diameter(self) -> float:
        return 2 * self._radius

    def __repr__(self):
        return f"Circle(radius={self._radius})"


def test_circle():
    print("=" * 50)
    print("练习 4: @property 装饰器")
    print("=" * 50)

    c = Circle(5)
    print(f"圆形: {c}")
    print(f"半径: {c.radius}")
    print(f"面积: {c.area:.2f}")             # 78.54
    print(f"周长: {c.circumference:.2f}")    # 31.42
    print(f"直径: {c.diameter}")             # 10

    c.radius = 10
    print(f"\n修改半径为 10 后:")
    print(f"面积: {c.area:.2f}")             # 314.16

    try:
        c.radius = -1
    except ValueError as e:
        print(f"捕获错误: {e}")
    print()


# ============================================================
# 练习 5: 继承与多态
# ============================================================

class Animal:
    """动物基类"""

    def __init__(self, name: str, sound: str):
        self.name = name
        self.sound = sound

    def speak(self) -> str:
        return f"{self.name}说: {self.sound}"

    def info(self) -> str:
        return f"[{self.__class__.__name__}] {self.name}"


class Dog(Animal):
    def __init__(self, name: str, breed: str):
        super().__init__(name, "汪汪")
        self.breed = breed

    def fetch(self, item: str) -> str:
        return f"{self.name}捡回了{item}"


class Cat(Animal):
    def __init__(self, name: str, indoor: bool = True):
        super().__init__(name, "喵喵")
        self.indoor = indoor

    def purr(self) -> str:
        return f"{self.name}发出了呼噜声"


class Parrot(Animal):
    def __init__(self, name: str):
        super().__init__(name, "")
        self._vocabulary: list[str] = []

    def teach(self, word: str):
        self._vocabulary.append(word)

    def speak(self) -> str:
        if self._vocabulary:
            return f"{self.name}说: {', '.join(self._vocabulary)}"
        return f"{self.name}还不会说话"


def test_inheritance():
    print("=" * 50)
    print("练习 5: 继承与多态")
    print("=" * 50)

    animals = [
        Dog("旺财", "金毛"),
        Cat("咪咪", True),
        Parrot("小黑"),
    ]

    # 多态: 统一调用 speak()
    for animal in animals:
        print(animal.speak())

    # 子类特有方法
    dog = animals[0]
    print(dog.fetch("球"))     # 旺财捡回了球

    parrot = animals[2]
    parrot.teach("你好")
    parrot.teach("再见")
    print(parrot.speak())      # 小黑说: 你好, 再见

    # 检查继承关系
    print(f"\nDog 是否是 Animal 的子类: {issubclass(Dog, Animal)}")
    print(f"dog 是否是 Animal 的实例: {isinstance(dog, Animal)}")
    print()


# ============================================================
# 练习 6: 魔术方法
# ============================================================

class Money:
    """金额类: 练习运算符重载"""

    def __init__(self, amount: float, currency: str = "CNY"):
        self.amount = amount
        self.currency = currency

    def __repr__(self):
        return f"Money({self.amount}, '{self.currency}')"

    def __str__(self):
        prefixes = {"CNY": "CNY ", "USD": "USD ", "EUR": "EUR "}
        prefix = prefixes.get(self.currency, self.currency + " ")
        return f"{prefix}{self.amount:.2f}"

    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError(f"不能直接相加不同币种: {self.currency} 和 {other.currency}")
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("不能直接相减不同币种")
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, factor: float) -> "Money":
        return Money(self.amount * factor, self.currency)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount == other.amount and self.currency == other.currency

    def __lt__(self, other: "Money") -> bool:
        if self.currency != other.currency:
            raise ValueError("不能比较不同币种")
        return self.amount < other.amount

    def __bool__(self) -> bool:
        return self.amount > 0

    def __hash__(self):
        return hash((self.amount, self.currency))


def test_magic_methods():
    print("=" * 50)
    print("练习 6: 魔术方法")
    print("=" * 50)

    salary = Money(10000, "CNY")
    bonus = Money(3000, "CNY")
    rent = Money(2500, "CNY")

    # __str__
    print(f"工资: {salary}")       # ¥10000.00
    print(f"奖金: {bonus}")       # ¥3000.00

    # __add__ / __sub__
    total = salary + bonus
    remaining = total - rent
    print(f"总收入: {total}")      # ¥13000.00
    print(f"扣除房租: {remaining}") # ¥10500.00

    # __mul__
    doubled = salary * 2
    print(f"双倍工资: {doubled}")  # ¥20000.00

    # __eq__ / __lt__
    print(f"salary == Money(10000, 'CNY'): {salary == Money(10000, 'CNY')}")
    print(f"rent < bonus: {rent < bonus}")

    # __bool__
    empty = Money(0, "CNY")
    print(f"bool(salary): {bool(salary)}")  # True
    print(f"bool(empty): {bool(empty)}")    # False

    # __hash__ (可以作为 dict key)
    prices = {salary: "月薪", bonus: "奖金"}
    print(f"字典查找: {prices[salary]}")
    print()


# ============================================================
# 练习 7: 抽象基类 (ABC)
# ============================================================

class Shape(ABC):
    """形状抽象基类"""

    @abstractmethod
    def area(self) -> float:
        """计算面积"""
        pass

    @abstractmethod
    def perimeter(self) -> float:
        """计算周长"""
        pass

    def describe(self) -> str:
        """通用方法 (非抽象)"""
        return f"{self.__class__.__name__}: 面积={self.area():.2f}, 周长={self.perimeter():.2f}"


class RectangleShape(Shape):
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height

    def perimeter(self) -> float:
        return 2 * (self.width + self.height)


class CircleShape(Shape):
    def __init__(self, radius: float):
        self.radius = radius

    def area(self) -> float:
        return math.pi * self.radius ** 2

    def perimeter(self) -> float:
        return 2 * math.pi * self.radius


class TriangleShape(Shape):
    def __init__(self, a: float, b: float, c: float):
        if a + b <= c or a + c <= b or b + c <= a:
            raise ValueError("不构成三角形")
        self.a, self.b, self.c = a, b, c

    def area(self) -> float:
        s = (self.a + self.b + self.c) / 2
        return math.sqrt(s * (s - self.a) * (s - self.b) * (s - self.c))

    def perimeter(self) -> float:
        return self.a + self.b + self.c


def test_abc():
    print("=" * 50)
    print("练习 7: 抽象基类")
    print("=" * 50)

    # shape = Shape()  # TypeError: 不能实例化抽象类

    shapes = [
        RectangleShape(4, 6),
        CircleShape(5),
        TriangleShape(3, 4, 5),
    ]

    for shape in shapes:
        print(shape.describe())

    # 验证所有 shape 都是 Shape 的实例
    print(f"\n全部是 Shape 子类实例: {all(isinstance(s, Shape) for s in shapes)}")
    print()


# ============================================================
# 练习 8: dataclass 数据类
# ============================================================

@dataclass
class Task:
    """任务数据类"""
    title: str
    priority: int = 0
    completed: bool = False
    tags: list = field(default_factory=list)

    def __post_init__(self):
        if self.priority < 0:
            raise ValueError("优先级不能为负数")

    def complete(self):
        self.completed = True
        return self


@dataclass(frozen=True)
class Coordinate:
    """不可变坐标"""
    x: float
    y: float

    def distance_to(self, other: "Coordinate") -> float:
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)


@dataclass(order=True)
class PriorityItem:
    """支持排序的优先级项目"""
    priority: int
    name: str = field(compare=False)  # name 不参与排序


def test_dataclass():
    print("=" * 50)
    print("练习 8: dataclass 数据类")
    print("=" * 50)

    # 基础用法
    task1 = Task("学习 Python OOP", priority=5, tags=["python", "oop"])
    task2 = Task("写练习代码", priority=3)
    print(task1)  # Task(title='学习 Python OOP', priority=5, ...)

    # 修改状态
    task1.complete()
    print(f"任务完成: {task1.completed}")

    # frozen dataclass
    p1 = Coordinate(0, 0)
    p2 = Coordinate(3, 4)
    print(f"两点距离: {p1.distance_to(p2)}")  # 5.0

    # 排序 dataclass
    items = [
        PriorityItem(3, "低优先级"),
        PriorityItem(1, "高优先级"),
        PriorityItem(2, "中优先级"),
    ]
    sorted_items = sorted(items)
    for item in sorted_items:
        print(f"  优先级 {item.priority}: {item.name}")
    print()


# ============================================================
# 练习 9: 综合实战 - 迷你 Agent 框架
# ============================================================

@dataclass
class ChatMessage:
    role: str       # "system" / "user" / "assistant"
    content: str
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            from datetime import datetime
            self.timestamp = datetime.now().strftime("%H:%M:%S")


class ToolBase:
    """工具基类"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def execute(self, input_text: str) -> str:
        raise NotImplementedError


class EchoTool(ToolBase):
    """回声工具 (演示用)"""

    def __init__(self):
        super().__init__("echo", "回显输入内容")

    def execute(self, input_text: str) -> str:
        return f"[Echo] {input_text}"


class MathTool(ToolBase):
    """数学计算工具"""

    def __init__(self):
        super().__init__("math", "执行数学计算")

    def execute(self, input_text: str) -> str:
        # 简单的表达式解析 (仅演示)
        allowed_chars = set("0123456789+-*/.() ")
        if all(c in allowed_chars for c in input_text):
            try:
                result = eval(input_text)
                return f"计算结果: {input_text} = {result}"
            except Exception:
                return "计算错误: 无效表达式"
        return "计算错误: 包含不允许的字符"


class MiniAgent:
    """迷你 Agent: 综合运用类与对象的知识"""

    def __init__(self, name: str, system_prompt: str = "你是一个有帮助的助手"):
        self.name = name
        self.system_prompt = system_prompt
        self._memory: list[ChatMessage] = []
        self._tools: dict[str, ToolBase] = {}

        # 添加系统消息
        self._add_message("system", system_prompt)

    def register_tool(self, tool: ToolBase):
        """注册工具"""
        self._tools[tool.name] = tool
        print(f"  [注册工具] {tool.name}: {tool.description}")

    def _add_message(self, role: str, content: str):
        self._memory.append(ChatMessage(role=role, content=content))

    def _find_tool(self, text: str) -> ToolBase | None:
        """根据文本内容匹配工具"""
        for tool in self._tools.values():
            if tool.name in text.lower():
                return tool
        return None

    def chat(self, user_input: str) -> str:
        """处理用户输入并返回响应"""
        self._add_message("user", user_input)

        # 尝试匹配工具
        tool = self._find_tool(user_input)
        if tool:
            result = tool.execute(user_input)
            response = f"[{self.name}] 调用工具 {tool.name} -> {result}"
        else:
            response = f"[{self.name}] 收到: {user_input}"

        self._add_message("assistant", response)
        return response

    def get_history(self) -> list[ChatMessage]:
        return list(self._memory)

    def __repr__(self):
        return f"MiniAgent(name='{self.name}', tools={list(self._tools.keys())}, messages={len(self._memory)})"


def test_mini_agent():
    print("=" * 50)
    print("练习 9: 综合实战 - 迷你 Agent")
    print("=" * 50)

    # 创建 Agent
    agent = MiniAgent("小Q", "你是一个智能助手, 可以使用工具帮助用户")
    print(f"Agent: {agent}")

    # 注册工具
    agent.register_tool(EchoTool())
    agent.register_tool(MathTool())

    # 对话
    print()
    print(agent.chat("你好, 今天天气不错"))
    print(agent.chat("echo 测试回声"))
    print(agent.chat("3.14 * 2"))

    # 查看历史
    print(f"\n对话历史 ({len(agent.get_history())} 条):")
    for msg in agent.get_history():
        print(f"  [{msg.timestamp}] {msg.role}: {msg.content[:40]}...")

    print(f"\n最终 Agent 状态: {agent}")
    print()


# ============================================================
# 运行所有练习
# ============================================================

if __name__ == "__main__":
    print("\n" + "#" * 60)
    print("# Day 21 - Python 类与对象练习")
    print("#" * 60 + "\n")

    test_student()
    test_employee()
    test_config()
    test_circle()
    test_inheritance()
    test_magic_methods()
    test_abc()
    test_dataclass()
    test_mini_agent()

    print("=" * 50)
    print("所有练习完成!")
    print("=" * 50)
