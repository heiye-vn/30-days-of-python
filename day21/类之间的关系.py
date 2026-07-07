"""
在 OOP 中，类与类之间不是孤立的，有多种关系类型
"""

from abc import ABC, abstractmethod

"""
1. 关联（Association）
两个类之间有 “使用关系”，但各自独立生存
"""


class Teacher:
    def __init__(self, name: str):
        self.name = name

    def teach(self, subject):
        print(f"{self.name}正在教授{subject.name}")


class Course:
    def __init__(self, name: str):
        self.name = name


# 老师和课程有关联，但各自独立
teacher = Teacher("王老师")
course = Course("Python 入门")
# teacher.teach(course)


"""
2. 聚合（Aggregation）
整体和部分的关系。但部分可以脱离整体独立存在。用 “空心菱形” 表示
"""


class Employee:
    def __init__(self, name: str):
        self.name = name


class Department:
    def __init__(self, name: str):
        self.name = name
        self.employees: list[Employee] = []

    def add_employee(self, emp: Employee):
        self.employees.append(emp)


# 部门解散了，员工还在（可以转到其他部门）
alice = Employee("Alice")
dept = Department("研发部")
dept.add_employee(alice)
# print(f"【{dept.name}】员工：{dept.employees}")


"""
3. 组合（Composition）
更强的【整体-部分】关系，部分不能脱离整体独立存在。用 “实心菱形” 表示
"""


class Heart:
    """心脏类（部分）"""

    def beat(self):  # noqa
        print("心脏跳动中...")


class Person:
    """人类（整体）"""

    def __init__(self, name: str):
        self.name = name
        self.heart = Heart()  # 组合关系：生命周期绑定，随 Person 一起创建

    def alive(self):
        self.heart.beat()


# 如果 Person 实例被销毁（垃圾回收），内部的 Heart 实例也会随之销毁
person = Person("老张")
# person.alive()


"""
4. 继承（Inheritance）
”is-a“ 关系：子类是父类的一种特殊形式
"""


class Vehicle:
    def move(self): ...


class Car(Vehicle):
    def move(self):
        print("汽车在路上行驶")


class Ship(Vehicle):
    def move(self):
        print("轮船在水上航行")


"""
5. 依赖（Dependency）
最弱的关系，一个类在某个方法中临时使用了另一个类
"""


class Ink:
    """墨水类"""

    def get_color(self) -> str:  # noqa
        return "蓝色"


class Pen:
    """钢笔类"""

    def write(self, ink: Ink):  # noqa
        # Pen 临时使用 Ink，作为方法参数传入
        color = ink.get_color()
        print(f"用 {color} 墨水写字")


"""
6. 实现（Realization）
定义了接口（或抽象契约），子类负责实现该接口的具体行为
"""


class Flyable(ABC):
    """飞行基类（抽象接口）"""

    @abstractmethod
    def fly(self):
        pass


class Bird(Flyable):
    """实现接口"""

    def fly(self):
        print("bird fly")
