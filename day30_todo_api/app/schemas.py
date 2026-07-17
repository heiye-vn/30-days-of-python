from pydantic import BaseModel, Field


# 定义创建模型
class TodoCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str = Field(default=None, max_length=500)


# 定义更新模型
class TodoUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    completed: bool | None = None


# 定义返回模型
class TodoRead(BaseModel):
    id: int
    title: str
    description: str | None
    completed: bool
