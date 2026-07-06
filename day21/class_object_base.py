"""
类与对象的基本概念
"""

"""
类（class）
类是一种模板、蓝图、说明书，用来描述一类事务的共同特征和行为
类使用 class 关键字定义，类名通常使用大驼峰命名法 PascalCase

对象（object）
对象是类创建出来的具体实例
"""


class Hero:
    """定义一个英雄类"""

    # 构造方法，每次实例化时都会执行
    def __init__(self, name, hp, damage):
        self.name = name
        self.hp = hp
        self.damage = damage

    # 普通方法
    def attack(self, enemy_name):
        return f"⚔️ {self.name} 发起攻击，对 {enemy_name} 造成了 {self.damage} 点伤害！"


# 实例化
hero1 = Hero("亚瑟", 3000, 150)
hero2 = Hero("妲己", 1500, 350)

# 访问属性（使用点 . 操作符）
# print(f"英雄1的名字：{hero1.name}，血量：{hero1.hp}")
# print(f"英雄2的名字：{hero2.name}，攻击力：{hero2.damage}")

# 调用方法
# print(hero1.attack("小兵A"))
# print(hero2.attack("大龙"))

# print(Hero.__doc__)


"""
定义类与创建对象
实例属性：实例属性是属于某个具体对象的数据
实例方法：实例方法是属于对象的行为，第一个参数通常叫 self（指向当前对象本身）

💡：__init__ 并不是创建对象的方法，只负责初始化对象，__new__ 才负责创建对象
"""


class Dog:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    # 定义实例方法
    def bark(self):
        print(f"{self.name}: 汪汪汪！")


dog1 = Dog("旺财", 3)
dog2 = Dog("小黑", 5)

# print(dog1.name)
# print(dog2.name)

# dog1.bark()
# Dog.bark(dog2)

# print(dog1 is dog2)


"""
构造函数(__init__ 传参的注意事项)
"""


# 1. 不要在默认参数中使用可变对象，会导致共享同一个引用
class TeamError:
    def __init__(self, members=[]):
        self.members = members


team1 = TeamError()
team2 = TeamError()

team1.members.append("Alice")
# print(team2.members)
# print(id(team1.members), "---", id(team2.members))  # 引用内存地址一样


class TeamCorrect:
    def __init__(self, members=None):
        # if members is None:
        #     members = []
        # self.members = members

        # 最佳写法：如果没有传参，默认创建空列表，如果传了参数，拷贝一份新列表防止共享引用
        self.members = list(members) if members is not None else []


team3 = TeamCorrect()
team3.members.append("Alice")

my_list = ["Bob"]
team4 = TeamCorrect(my_list)
my_list.append("Dived")

# print(team3.members)
# print(team4.members)
# print(id(team3.members), "---", id(team4.members))


"""
类属性与实例属性
类属性：属于类本身的属性，所有实例共享
实例属性：属于具体对象的属性，每个对象都有自己的实例属性

💡陷阱：类属性如果是可变对象（list、dict），所有实例会共享同一个引用
💡：如果类属性和实例属性同名，查找顺序是先查找实例对象属性，如果没有再去类中查找
"""


class Student:
    school = "Python Academy"  # 类属性

    def __init__(self, name):
        self.name = name  # 实例属性


student1 = Student("小红")
student2 = Student("小明")

# print(student1.school)
# print(student2.school)
# print(Student.school)


# 类属性适合存放所有对象共享的数据
class Circle:
    pi = 3.1415926

    def __init__(self, radius):
        self.radius = radius

    def cal_area(self):
        return self.pi * self.radius**2


# 修改类属性
Circle.pi = 3.1415
# print(Circle.pi)

circle1 = Circle(20)
# print(f"圆的面积为：{circle1.cal_area():.2f}")


"""
实例方法、类方法、静态方法

实例方法：属于对象的方法，第一个参数通常是 self，指向对象本身。使用场景：需要访问或修改对象状态
类方法：属于类的方法，第一个参数通常是 cls，指向类本身。使用场景：需要访问或修改类状态，或提供替代构造器，使用 @clasmethod 装饰器
静态方法：不属于对象或类的方法，和类有关，但不需要访问对象或类的属性。使用场景：与类相关但不需要访问类或对象属性的函数，使用 @staticmethod 装饰器
"""


# 实例方法
class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance

    # 存钱
    def deposit(self, amount):
        self.balance += amount


account = BankAccount("Alice", 100)
account.deposit(50)
# print(account.balance)


# 类方法
class User:
    count = 0

    def __init__(self, username):
        self.username = username
        User.count += 1

    @classmethod
    def get_account(cls):
        return cls.count


user1 = User("alice")
# print(user1.count)
user2 = User("bob")
# print(user2.count)

# print(user2.get_account())
# print(User.get_account())


# 类方法作为代替构造器
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


date1 = Date.from_string("2026-07-05")
# date1.show()
date2 = Date(2026, 7, 5)
# date2.show()


# 静态方法，本质上就是放在类命名空间中的普通函数，它和这个类概念相关，但不依赖某个具体的对象
class MathTool:
    @staticmethod
    def is_even(number):
        return number % 2 == 0


# print(MathTool.is_even(10))
