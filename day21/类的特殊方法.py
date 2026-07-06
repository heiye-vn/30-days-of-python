"""
魔术方法：让对象更像内置类型

也叫特殊方法，通常以双下划线开头和结尾
"""

"""
字符串表示
__str__: 面向用户，用于显示给用户
__repr__ : 面向开发者，用于显示给开发者
"""


class Student:
    def __init__(self, name, score):
        self.name = name
        self.score = score

    def __str__(self):
        return f"{self.name} 的成绩是：{self.score}"

    def __repr__(self):
        return f"Student(name={self.name!r}, score={self.score!r})"


student = Student("Alice", 95)
# print(student)
# print(str(student))
# print(repr(student))

""" __len__、__getitem__ """


class Playlist:
    def __init__(self, songs):
        self.songs = songs

    def __len__(self):
        return len(self.songs)

    # 让对象支持通过 [索引] 访问
    def __getitem__(self, index):
        return self.songs[index]


playlist = Playlist(["Song A", "Song B", "Song C"])
# print(len(playlist))
# print(playlist[1])

""" __add__、__eq__  """


class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __eq__(self, other):
        if not isinstance(other, Vector):
            return False
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Vector({self.x}, {self.y})"


v1 = Vector(1, 2)
v2 = Vector(3, 4)
# print(v1 + v2)
print(v1 == v2)
