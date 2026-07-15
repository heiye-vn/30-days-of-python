"""
FastAPI 服务

安装：pip install fastapi uvicorn
启动服务：uvicorn main:app --reload
"""

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello FastAPI"}


# 路径参数
@app.get("/items/{item_id}")
def get_item(item_id: int, q: str | None = None):
    return {
        "item_id": item_id,
        "q": q,
    }


# 查询参数
@app.get("/users")
def list_users(page: int = 1, size: int = 10, keyword: str | None = None):
    return {
        "page": page,
        "size": size,
        "keyword": keyword,
    }


"""
请求体：常用于 POST、PUT、PATCH，常见格式为 JSON
"""


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    age: int = Field(ge=0, le=150)


@app.post("/users")
def create_user(user: UserCreate):
    return {"message": "created", "user": user}
