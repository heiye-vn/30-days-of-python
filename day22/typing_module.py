"""
typing 模块中的一些 API 用法
"""

from dataclasses import dataclass
from typing import (
    Annotated,
    ClassVar,
    Final,
    NewType,
    NotRequired,
    Required,
    Self,
    TypedDict,
    Union,
    final,
    overload,
)

from pydantic import BaseModel, Field

from day14.常用高阶函数 import total

"""
Self：返回当前实例，常用于链式调用
"""


class Query:
    def __init__(self):
        self.conditions: list[str] = []

    def where(self, condition: str) -> Self:
        self.conditions.append(condition)
        return self

    def build(self) -> str:
        return " and ".join(self.conditions)


query = Query().where("age > 18").where("active = true")
# print(query.build())


"""
ClassVar
类型标注工具，用来告诉类型检查器："这个变量是类级别的，不是实例级别的，不需要当做实例字段来处理（不用 init 初始化）
"""


@dataclass
class LLMTool:
    # 类级别：不参与 __init__，所有实例共享
    version: ClassVar[str] = "1.0"
    max_retries: ClassVar[int] = 3

    # 实例级别：每个实例不同，会生成 __init__ 参数
    name: str
    api_key: str


tool1 = LLMTool(name="gpt-4", api_key="sk-xxx")
tool2 = LLMTool(name="Claude", api_key="sk-yyy")


# print(LLMTool.version)  #  "1.0" — 类变量，不用实例也能访问
# print(tool1.max_retries)  # 3 — 实例也能访问，但不需要在 __init__ 里传


"""
Final: 不希望被重新赋值，可作用于变量、属性、方法或类
"""
# 声明一个全局常量
MAX_CONNECTIONS: Final[int] = 100


# 限制类属性被修改
class WebServer:
    # 声明端口号为不可变属性
    port: Final[int]

    def __init__(self, port: int) -> None:
        self.port = port  # 允许在 __init__ 中进行首次赋值

    # def configure(self) -> None:
    #     self.port = 8080 # 'port' 为 'Final'，不能被重新赋值


# 限制方法被子类重写
class BaseService:
    @final
    def authenticate(self) -> bool:
        """核心认证逻辑，禁止子类重写"""
        return True


# class CustomService(BaseService):
#     def authenticate(self) -> bool: # 提示：被标记为 '@final'，不应被重写
#         return False


# 限制类被继承
@final
class SecureConnection: ...


# class HackyConnection(SecureConnection): ... # 提示：'SecureConnection' 被标记为 '@final'，不应为子类


"""
Annotated: 允许在现有类型提示上附加额外信息（附加自定义元数据）
"""
# UserId = Annotated[int, "database primary ket"]
# print(UserId)


# 数据校验与限制
# 定义一个限制长度的用户名类型
# 静态检查器只认为它是 str，但 Pydantic 会在运行时校验长度
Username = Annotated[str, Field(min_length=3, max_length=15)]


class User(BaseModel):
    name: Username
    # 限制年龄在 18 到 120 之间
    age: Annotated[int, Field(ge=18, le=120)]


"""
overload: 用于声明函数重载
告诉静态类型检查器/IDE，同一个函数根据输入参数的类型或数量的不同，会返回不同类型的结果
"""


# 1. 声明重载签名 A：如果输入是 str，返回也是 str
@overload
def double(value: str) -> str: ...


# 2. 声明函数重载 B：如果输入是 int，返回也是 int
@overload
def double(value: int) -> int: ...


# 3. 编写具体实现（必须是紧随其后的最后一个函数，不带 @overload）
def double(value: str | int) -> Union[str, int]:
    if isinstance(value, str):
        return value + value
    elif isinstance(value, int):
        return value * 2
    raise TypeError("不支持的类型")


# print(double("hello"))
# print(double(21))
# print(double([1, 2]))


"""
NewType：创建独特的类型
作用是帮助静态类型检查器区分两个底层数据类型相同，但业务语义完全不同的变量，从而避免逻辑错误
"""


# 不使用 NewType
def get_user_profile(user_id: int):
    pass


product_id = 9999
# 逻辑错误，商品id 传给了需要用户 id 的函数
get_user_profile(product_id)

# 使用 NewType
# 创建两个基于 int 的全新独特类型
UserId = NewType("UserId", int)
ProductId = NewType("ProductId", int)
# print(type(UserId)) # <class 'typing.NewType'>
# print(type(ProductId))


def get_user_profile_(userId: UserId): ...


# 1. 显示创建特定类型的变量
my_user_id = UserId(12345)
# print(type(my_user_id)) # <class 'int'>
my_product_id = ProductId(9999)
# print(my_user_id + 10)

# 2. 正常调用
get_user_profile_(my_user_id)

# get_user_profile_(my_product_id)  # 应为类型 'UserId'，但实际为 'ProductId'

# get_user_profile_(66666) # 类型 'UserId'，但实际为 'int'


"""
TypedDict: 给字典（Dict）对象声明一组固定的键，并未每个键指定对应的值类型
默认情况下，定义的所有键都必须存在
可以使用 total 属性整体控制，或者使用 Required 或 NotRequired
"""


class Movie(TypedDict):
    title: str
    year: int
    rating: float


# 实例化一个符合规范的普通字典
my_movie: Movie = {"title": "Inception", "year": 2010, "rating": 8.8}

# bad_movie: Movie = {
#     "title": "Inception",
#     "year": 2010,
#     "rating": 8.8,
#     "director": "Nolan",  # TypedDict 'Movie' 的额外键 'director'
# }

# my_movie["year"] = "2010" # 应为类型 'int'，但实际为 'str'


# total 整体控制
class UserProfile(TypedDict, total=False):
    username: str
    email: str


user: UserProfile = {}


# 使用 Required 或 NotRequired 控制某个键
class Student(TypedDict):
    id: int
    username: Required[str]  # 显示声明必填
    avatar_url: NotRequired[str]  # 显示声明不必填
