"""
FastAPI 服务

安装：pip install fastapi uvicorn
启动服务：uvicorn main:app --reload
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from starlette import status

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


"""
响应模型：response_model
控制返回数据的格式，避免误返回敏感字段
"""


class UserCreate2(BaseModel):
    username: str
    password: str = Field(min_length=8)


class UserResponse(BaseModel):
    id: int
    username: str


@app.post(
    "/users/add", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def create_user2(user: UserCreate2):
    saved_user = {"id": 1, "username": user.username, "password": user.password}
    return saved_user


"""
HTTPException 异常
"""


@app.get("/users/{user_id}")
def get_user(user_id: int):
    if user_id != 1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    return {"id": 1, "username": "Alice"}
