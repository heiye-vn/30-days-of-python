"""
FastAPI 服务

安装：pip install fastapi uvicorn
启动服务：uvicorn main:app --reload
"""

from app.routers import todos
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from starlette import status

app = FastAPI(title="Todo API")

app.include_router(todos.router)


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


"""
Depends：依赖注入系统
可以将可复用的逻辑（如认证、数据库连接、参数校验）抽取为独立函数，然后"声明式"地注入到路由中

常见的依赖有：获取数据库 session、获取当前登录用户、校验 API Key、读取配置、复用分页、过滤参数等
"""


class Pagination(BaseModel):
    page: int = Field(default=1, ge=1)
    size: int = Field(default=10, ge=1, le=100)


# 定义依赖函数，会自动从请求的 Query 参数中提取 page 和 size
def get_pagination(page: int = 1, size: int = 10) -> Pagination:
    return Pagination(page=page, size=size)


# 使用 Depends 注入分页函数
@app.get("/articles")
def list_articles(pagination: Pagination = Depends(get_pagination)):
    return {"page": pagination.page, "size": pagination.size}


# 使用 Depends 注入分页函数
@app.get("/orders")
def list_orders(pagination: Pagination = Depends(get_pagination)):
    return {"page": pagination.page, "size": pagination.size}


# 模拟当前用户
def get_current_user(x_token: str | None = Header(default=None)):
    if x_token != "secret-token":
        raise HTTPException(status_code=401, detail="未登录")

    return {"id": 1, "username": "alice"}


@app.get("/me")
def read_me(current_user: dict = Depends(get_current_user)):
    return current_user
