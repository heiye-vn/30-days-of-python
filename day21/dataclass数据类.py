"""
dataclass：数据类

dataclass 是 Python 3.7 引入的一个装饰器，用于自动生成数据类。数据类主要用于存储数据，不包含复杂逻辑。
"""

from dataclasses import dataclass, field

""" 普通写法 """


class Student:
    def __init__(self, name, age, score):
        self.name = name
        self.age = age
        self.score = score

    def __repr__(self):
        # 使用 !r 表示调用对象的 __repr__ 方法，!s（默认） 表示调用对象的 __str__ 方法
        return f"Student(name={self.name!r}, age={self.age!r}, score={self.score!r})"


student1 = Student("小王", 18, 90)
# print(student1)


"""
dataclass 写法
会自动生成常用方法，如：__init__、__repr__、__eq__ 等
"""


@dataclass
class Person:
    name: str
    age: int
    height: float
    weight: float
    sex: str = "男"

    def greet(self):
        return f"Hello, my name is {self.name}"


person1 = Person("小李", 25, 175, 70)
# print(person1)
# print(person1.greet())

""" 可变默认值使用 field """


@dataclass
class Team:
    name: str
    members: list[str] = field(default_factory=list)


team1 = Team("A")
team2 = Team("B")

team1.members.append("Alice")
# print(team1.members)  # ['Alice']
# print(team2.members)  # []
