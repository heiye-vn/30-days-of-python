"""
类和对象的三大特性：封装、继承、多态
"""

"""
封装（Encapsulation）—— 保护数据
核心思想：把数据和操作数据的方法放在一起，并限制外部直接随意修改内部状态

🚀: python 的封装更强调“约定” 和 “接口设计”，不是绝对禁止的
"""


# 公开属性（无任何前导下划线），可以随意在类的外部访问和修改
class User:
    def __init__(self, username, password, age):
        self.username = username  # 共有属性
        self._password = password  # 受保护属性
        self.__age = age  # 私有属性

    # Getter 读取属性
    @property
    def age(self):
        return self.__age


user1 = User("alice", "123456", "18")
user1.username = "bob"
# print(user1.username)

# 受保护属性（单下划线开头），仍然可以访问，但是约定提示外部不要直接访问或修改（通常仅提供内部或子类使用）
user2 = User("wangling", "admin123", "18")
# ❌ 虽然不会报错，但不推荐在外部修改或访问受保护属性
# user2._password = "admin456"
# print(user2._password)

# 私有属性（双下划线开头）
user3 = User("李四", "admin000", "20")
# ❌ 外部直接访问 __age 会报错，因为 __age 被 Python 解释器重命名为 _User__age，依旧不推荐
# print(user3.__age)
# print(user3._User__age)
# print(user3.age)


"""
@property 装饰器：属性访问控制
将方法转换为属性，从而可以像访问属性一样访问方法，同时保留校验逻辑
"""


# 基本用法
class Circle:
    def __init__(self, radius):
        self.radius = radius

    @property
    def area(self):
        return 3.1415926 * self.radius**2


circle = Circle(3)
# print(circle.area)


# setter 校验数据
class Product:
    def __init__(self, name, price):
        self.name = name
        self.__price = price

    # Getter 获取属性
    @property
    def price(self):
        return self.__price

    #
    @price.setter
    def price(self, value):
        if value < 0:
            raise ValueError("价格不能为负数")
        self.__price = value


product1 = Product("Keyboard", 299)
# print(product1.price)

# 修改价格时会自动触发校验
# product1.price = -200
product1.price = 399
# print(product1.price)


"""
继承（Inheritance）—— 代码复用，扩展
核心思想：可以让一个类获得另一个类的属性和方法
"""


# 父类/基类/超类
class Animal:
    def __init__(self, name):
        self.name = name

    def eat(self):
        print(f"{self.name} 正在吃东西")


# 子类/派生类
class Dog(Animal):
    def bark(self):
        print(f"{self.name} 汪汪")


dog = Dog("旺财")
# dog.eat()
# dog.bark()

"""
isinstance(): 判断的是 “实例（对象）与类” 之间的所属关系
issubclass(): 判断的是 “类与类” 之间的继承关系
"""
# print(isinstance(dog, Dog))
# print(isinstance(product1, Dog))

# print(issubclass(Dog, Animal))
# print(issubclass(Product, Animal))


"""
方法重写与 super()

方法重写: 子类可以重新定义父类已有的方法（Override）
super(): 用于调用父类的方法
"""


# 方法重写
class Humans:
    def speak(self):  # noqa
        print("人可以说话")


class Chinese:
    def speak(self):  # noqa
        print("说的是中文")


class American:
    def speak(self):  # noqa
        print("Speaking in English")


# human1 = Chinese()
# human1.speak()
# human2 = American()
# human2.speak()


# 使用 super() 调用方法
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age


class Student(Person):
    def __init__(self, name, age, score):
        super().__init__(name, age)  # 调用父类的构造方法，初始化逻辑
        self.score = score


student = Student("小红", 18, 95)
# print(student.name, student.age, student.score)


# 扩展父类方法
class Logger:
    def log(self, message):  # noqa
        print(f"[LOG] {message}")


class FileLogger(Logger):
    def log(self, message):
        super().log(message)
        print("消息已写入文件")


logger = FileLogger()
# logger.log("程序启动")


"""
多态（Polymorphism）—— 同一接口，不同实现
核心思想：不同对象对同一个方法调用做出不同响应

多态的三个前提条件：
- 有继承关系
- 有方法重写
- 父类引用指向子类对象

鸭子类型多态（Duck Typing Polymorphism）：更看重对象“能不能做某件事”，而不是它“到底是什么类型”
"""


# 多态示例一，依赖继承（经典多态）
class Hero:
    def __init__(self, name, hp, damage):
        self.name = name
        self.hp = hp
        self.damage = damage

    def attack(self, enemy_name):
        return f"⚔️ {self.name} 发起攻击，对 {enemy_name} 造成了 {self.damage} 点伤害！"


class Archer(Hero):
    def attack(self, enemy_name):
        return f"🏹 {self.name} 射出了一支冷箭，对 {enemy_name} 造成 {self.damage} 点穿透伤害！"


warrior = Hero("亚瑟", 3000, 150)
hunter = Archer("后羿", 1200, 280)

heroes = [warrior, hunter]
# for hero in heroes:
#     print(hero.attack("敌方英雄"))


# 多态示例二，不依赖继承（鸭子类型多态），不关心对象类型，只关心对象是否具有相应方法
class Bird:
    def speak(self):  # noqa
        print("叽叽！")


class Cat:
    def speak(self):  # noqa
        print("喵喵！")


class Duck:
    def speak(self):  # noqa
        print("嘎嘎！")


def make_it_speak(animal):
    animal.speak()


# make_it_speak(Bird())
# make_it_speak(Cat())
# make_it_speak(Duck())


# 多态示例三：多支付方式
class Alipay:
    def pay(self, amount):  # noqa
        print(f"支付宝支付 {amount} 元")


class WeChatPay:
    def pay(self, amount):  # noqa
        print(f"微信支付 {amount} 元")


class CreditCard:
    def pay(self, amount):  # noqa
        print(f"信用卡支付 {amount} 元")


# 不关心支付对象具体是哪种类型，只关心是否具有 pay 方法，后续添加新的支付方式时无需修改 checkout 函数
def checkout(payment_method, amount):
    payment_method.pay(amount)


checkout(Alipay(), 100)
checkout(WeChatPay(), 200)
checkout(CreditCard(), 300)
