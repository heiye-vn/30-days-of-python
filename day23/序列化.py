"""
Pydantic 提供了两个方法用于数据的序列化，模型 -> Dict / JSON
"""

from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str
    email: str | None = None


user = User(id=1, name="Alice")
# print(type(user))

# 转为 dict 格式
user_dict = user.model_dump()
# print(user_dict)
# print(user.model_dump(exclude_none=True))  # 去除值为 None 的字段

# 转换为 json 字符串
user_json = user.model_dump_json()
# print(user_json)
# print(user.model_dump_json(exclude_none=True))

# 导出部分字段
public_user = user.model_dump(include={"id", "name"})
# print(public_user)

# 排除字段
safe_user = user.model_dump(exclude={"id"})
# print(safe_user)
