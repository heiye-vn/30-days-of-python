"""
多重继承

python 中允许一个类继承多个父类
"""


class Flyer:
    def move(self):  # noqa
        print("fly")


class Swimmer:
    def swim(self):  # noqa
        print("swim")


class Duck(Flyer, Swimmer):
    pass


d = Duck()
# d.move()
# d.swim()


"""
方法冲突

MRO（方法解析顺序）
在 Python 中，MRO 决定了在多继承（Multiple Inheritance）的情况下，当调用一个方法或属性时，Python 解释器搜索该方法/属性的类路径顺序
"""


class A:
    def hello(self):  # noqa
        print("A - hello")


class B:
    def hello(self):  # noqa
        print("B - hello")


class C(A, B):
    pass


c = C()
# c.hello()


"""
菱形继承

super() 不是简单调用 ”父类“，而是调用 MRO 中的下一个类
"""


class Base:
    def process(self):  # noqa
        print("Base - process")


class Left(Base):
    def process(self):  # noqa
        print("Left - process")
        super().process()


class Right(Base):
    def process(self):  # noqa
        print("Right - process")
        super().process()


class Child(Left, Right):
    def process(self):
        print("Child - process")
        super().process()


child = Child()
# child.process()
# print(Child.mro())


"""
Mixin 模式
Mixin 是一种小型能力类，用于给主类附加功能

💡：
- Mixin 类通常不单独实例化
- Mixin 类尽量小而专一
- Mixin 类名一般以 Mixin 结尾 
- 多个 Mixin 依赖顺序时，要注意 MRO 的执行顺序
"""


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
