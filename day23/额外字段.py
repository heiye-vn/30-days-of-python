"""
在 Pydantic 中，ignore、forbid 和 allow 用来控制如何处理额外字段的三种策略
"""

from pydantic import BaseModel, ConfigDict, ValidationError

"""
1. ignore (忽略) - 默认行为，最常用
"""


class UserIgnore(BaseModel):
    model_config = ConfigDict(extra="ignore")
    username: str


user_ign = UserIgnore(username="alex", age=18)
# print(user_ign.model_dump())  # 额外传入的字段被忽略


"""
2. forbid（禁止） - 严格校验
应用场景：严格的 API 设计。例如前端向后端提交表单
"""


class UserForbid(BaseModel):
    model_config = ConfigDict(extra="forbid")
    username: str


try:
    UserForbid(username="alex", age=18)
except ValidationError as e:
    print("报错了！不允许有额外字段：")
    print(e.json(indent=2))


"""
3. allow（允许） - 宽容保留
应用场景：动态属性场景。当你需要将数据透传，或者有些属性虽然不用校验，但后续逻辑中仍需原样保留并提取时使用
"""


class UserAllow(BaseModel):
    model_config = ConfigDict(extra="allow")
    username: str


user_alw = UserAllow(username="alex", age=18)
# print(user_alw.model_dump())  # 额外的字段被保留
# print(user_alw.model_extra)  # 获取额外的字段
