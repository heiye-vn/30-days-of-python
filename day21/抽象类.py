"""
抽象类（abstract class），简称 ABC

用来规定一组接口，子类必须实现某些方法，否则不能实例化
"""

from abc import ABC, abstractmethod


class Shape(ABC):
    # 抽象方法
    @abstractmethod
    def area(self):
        pass


class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return 3.1415926 * self.radius**2


c = Circle(5)
# print(f"圆的面积为：{c.area():.2f}")


class Storage(ABC):
    @property
    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def save(self, data):
        pass
