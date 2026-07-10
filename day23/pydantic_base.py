"""
Pydantic：
Pydantic 是 Python 中最流行的数据校验（Data Validation）和设置管理（Settings Management）库
"""

import logging
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, ValidationError

"""
BaseModel：定义模型
"""


class Product(BaseModel):
    id: int
    name: str
    price: float
    quantity: int
    in_stock: bool


# product = Product(id=1001, name="Keyboard", price="299.00", quantity=20, in_stock=True)
# print(
#     type(product.price)
# )  # <class 'float'>，运行时会自动做类型转换（数据类型能转的前提下，不能则报错）


# 不能进行数据转换时会报 validation error
# try:
#     Product(id="abc", name="Keyboard", price="299.0", quantity=1, in_stock=True)
# except ValidationError as exc:
#     print(exc)

# 实际应用
# logger = logging.getLogger(__name__)
#
# product2 = Product(id="abc", name="Keyboard", price="299.0", quantity=1, in_stock=True)
# try:
#     product = Product.model_validate(product2)
# except ValidationError:
#     logger.exception("商品数据格式不正确，请检查")
#     raise


class UserModel(BaseModel):
    id: int
    username: str
    signup_at: Optional[datetime] = None  # 可选字段
    friends: List[int] = []  # 可选列表，默认为空


user1 = UserModel(
    id=1, username="jack", signup_at="2026-07-10 09:00:00", friends=["11", "12"]
)
# print(type(user1.signup_at))
# print(user1.friends)

# try:
#     user2 = UserModel(id="not-an-int", username="rose")
# except ValidationError as e:
#     print(e.json(indent=2))


"""
Field：字段约束和元信息
Field 可用来给字段加约束、默认值、说明、别名等信息

常见约束：
min_length / max_length：限制字符串长度
ge：大于等于、gt：大于、le：小于等于、lt：小于
default：固定默认值、default_factory：动态默认值（字典、列表、元组、时间等类型）
description：字段说明，常用于 API 文档
"""


class CreateUserModel(BaseModel):
    username: str = Field(min_length=3, max_length=30, description="用户名")
    password: str = Field(min_length=8, description="密码")
    age: int = Field(ge=0, le=120, description="年龄，要求在 0 岁至 120 岁的范围")
    # 别名（Alias）：当输入数据是 JSON (通常是 camelCase) 时非常有用
    # user_email: str = Field(validation_alias="userEmail")
    user_email: str
    # 普通默认值，固定不变
    sex: str = Field(default="男")
    # 动态默认值
    created_at: datetime = Field(default_factory=datetime.now)


user2 = CreateUserModel(
    username="张三111", password="zs123456", age=25, user_email="zs@example.com"
)
# print(user2.sex)
# print(user2.created_at)

user3 = CreateUserModel(
    username="Rose",
    password="rose123456",
    age=23,
    user_email="rose@example.com",
    sex="女",
)
# print(user3.created_at)


"""
嵌套模型：表达复杂数据结构
"""


class Address(BaseModel):
    city: str
    street: str
    zipcode: str


class OrderItem(BaseModel):
    sku: str
    quantity: int = Field(gt=0)
    unit_price: float = Field(gt=0)


class Order(BaseModel):
    id: int
    user_id: int
    address: Address
    items: List[OrderItem]


# 使用
order = Order.model_validate({
    "id": "10001",
    "user_id": 88,
    "address": {
        "city": "Shanghai",
        "street": "Nanjing Road",
        "zipcode": "200000",
    },
    "items": [
        {"sku": "keyboard", "quantity": 1, "unit_price": 299},
        {"sku": "mouse", "quantity": 2, "unit_price": 99},
    ],
})
# print(order.address.city)
# print(order.items[0].sku)
