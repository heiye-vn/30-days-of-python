"""
练习
"""

"""
练习1：定义一个书籍类
要求：
1. 类名为 Book
2. 属性包括 title、author、price
3. 定义 show_info 方法，打印书籍信息
4. 创建两个书籍对象并调用方法
"""


class Book:
    def __init__(self, title, author, price):
        self.title = title
        self.author = author
        self.price = price

    def show_info(self):
        print(
            f"书籍信息：\n标题：{self.title}\n作者:{self.author}\n价格：{self.price}\n{'===' * 20}"
        )


book1 = Book("西游记", "吴承恩", 55)
book2 = Book("红楼梦", "曹雪芹", 66)
# book1.show_info()
# book2.show_info()


"""
练习2：银行账户类
要求：
1. 类名为 BankAccount。
2. 属性包括 owner 和 balance。
3. 方法包括 deposit()、withdraw()、show_balance()。
4. 取款时余额不足要给出提示。
5. 存款和取款金额不能小于等于 0
"""


class BankAccount:
    def __init__(self, owner, balance):
        self.owner = owner
        self.balance = balance  # 触发 setter 校验，确保初始余额不为负数

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        if value < 0:
            raise ValueError("账户余额不能为负数！")
        self._balance = value

    # 存款
    def deposit(self, value):
        if value <= 0:
            raise ValueError("存款金额不能小于等于 0！")
        self.balance += value

    # 取款
    def withdraw(self, value):
        if value <= 0:
            raise ValueError("取款金额不能小于等于 0！")
        if value > self.balance:
            raise ValueError("余额不足！")
        self.balance -= value

    def show_balance(self):
        print(f"当前账户：{self.owner} 的余额为：{self.balance}")


account1 = BankAccount("地主老王", 200000)
account1.withdraw(3199)
# account1.show_balance()


"""
练习3：使用类属性统计对象数量
要求：
1. 定义 User 类。
2. 每创建一个用户，对象数量加 1。
3. 提供类方法 get_count() 返回用户数量。
"""


class User:
    obj_count = 0

    def __init__(self, name):
        self.name = name
        User.obj_count += 1
        # type(self).obj_count += 1

    @classmethod
    def get_count(cls):
        return cls.obj_count


user1 = User("Alice")
user2 = User("Bob")
# print(user2.get_count())


"""
练习4：继承练习
要求：
1. 定义父类 Shape，包含 area() 方法。
2. 定义子类 Rectangle 和 Circle。
3. 分别重写 area() 方法。
4. 编写函数 print_area(shape)，传入不同形状对象并打印面积。
"""


class Shape:
    def area(self):
        pass


class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height


class Circle(Shape):
    pi = 3.141592653589793

    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return self.pi * (self.radius**2)  # 返回原始数值


def print_area(shape):
    # 在函数内部打印面积，并可在此处做格式化
    print(f"该形状的面积为：{shape.area():.2f}")


# print(print_area(Rectangle(10, 20)))
# print(print_area(Circle(5)))


"""
练习5：商品类与 @property
要求：
1. 定义 Product 类。
2. 属性包括 name 和 price。
3. 使用 @property 控制 price，禁止价格为负数。
4. 定义 discount(rate) 方法，返回打折后的价格。
"""


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
            raise ValueError("商品价格不能为负数！")
        else:
            self._price = value

    def discount(self, rate):
        return self.price * rate


product1 = Product("iPhone 12", 1000)
print(product1.discount(0.7))
