"""
对象的生命周期有：

创建对象 → 初始化对象 → 使用对象 → 对象不再被引用 → 垃圾回收
"""

""" 创建与初始化 """


class Demo:
    def __init__(self):
        print("对象初始化")


# demo = Demo()
# demo2 = Demo()


"""
引用：变量保存的不是对象本身，而是对象的引用
"""


class Student:
    def __init__(self, name):
        self.name = name


alice = Student("Alice")
another = alice

# print(id(alice), "---", id(another))
# print(alice == another)
# print(alice is another)

another.name = "Dived"
# print(id(another.name), "---", id(alice.name))


"""
组合：比继承更灵活的复用 
表现形式：一个对象包含另一个对象
"""


# 1. 定义不同的零部件类
class Engine:
    def start(self):  # noqa
        print("发动机启动")


class Wheel:
    def __init__(self, brand):
        self.brand = brand

    def roll(self):
        print(f"车轮（品牌：{self.brand}）：开始转动...")


class GPS:
    def locate(self):  # noqa
        print("GPS 导航：正在定位当前位置...")


# 2. 修改 Car 类，使其接收多个部件类参数
class Car:
    def __init__(self, engine, wheels, gps):
        self.engine = engine
        self.wheels = wheels
        self.gps = gps

    def start_journey(self):
        print("--- 准备出发 ---")
        self.engine.start()
        self.gps.locate()
        # 让所有车轮转动
        for wheel in self.wheels:
            wheel.roll()
        print("汽车已顺利行驶！")


# 3. 实例化各个部件
my_engine = Engine()
my_gps = GPS()
my_wheels = [Wheel("Michelin"), Wheel("Michelin"), Wheel("Michelin"), Wheel("Michelin")]

# 4. 组装并初始化 Car 对象
my_car = Car(engine=my_engine, wheels=my_wheels, gps=my_gps)

my_car.start_journey()
# print(issubclass(Car, Engine))  # False, Car 与 Engine 并无继承关系
