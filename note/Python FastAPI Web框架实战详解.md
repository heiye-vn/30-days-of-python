# Python FastAPI Web 框架实战详解

> FastAPI 是一个现代 Python Web 框架，特别适合开发 HTTP API。它把 Python 类型注解、Pydantic 数据校验、自动 API 文档、异步能力和依赖注入组合在一起，让我们可以用比较少的代码写出结构清晰、可测试、容易维护的后端服务。

---

## 一、FastAPI 适合解决什么问题

很多 Python 学习者一开始写的是脚本：

```text
读取文件 -> 处理数据 -> 打印结果
```

但真实项目里，经常需要把能力开放给别人调用：

```text
前端页面 / 手机 App / 其他服务
        |
        v
HTTP 请求
        |
        v
Python 后端接口
        |
        v
业务逻辑 / 数据库 / 第三方 API
```

FastAPI 就是用来写这层 Python 后端接口的。

常见场景包括：

- 写 REST API，例如用户、文章、订单、任务列表。
- 给前端提供 JSON 数据。
- 封装机器学习模型、LLM Agent、数据处理脚本。
- 写内部工具接口。
- 写异步服务，例如调用多个外部 API、流式输出、WebSocket。

一句话理解：

**FastAPI 负责把 HTTP 请求变成 Python 函数调用，再把 Python 返回值变成 HTTP 响应。**

---

## 二、FastAPI、Flask、Django 怎么区分

Python Web 框架里常见三类选择：

| 框架 | 特点 | 适合场景 |
| --- | --- | --- |
| Flask | 轻量、自由、生态成熟 | 小型服务、教学、自由组合项目 |
| Django | 大而全，自带 ORM、后台、用户系统 | 内容管理、传统 Web 网站、后台系统 |
| FastAPI | 类型驱动、API 友好、异步友好、自动文档 | 现代 API 服务、微服务、AI/数据服务 |

FastAPI 的核心优势：

- 使用类型注解描述参数和返回值。
- 使用 Pydantic 自动校验请求体。
- 自动生成 Swagger UI 和 OpenAPI 文档。
- 支持同步函数和异步函数。
- 内置依赖注入，适合管理数据库 session、认证信息、配置。
- 性能较好，底层基于 Starlette 和 ASGI。

需要注意：

- FastAPI 不是 Django 那种“大而全”的框架。
- FastAPI 更偏 API 服务，不默认提供模板系统、后台管理、ORM。
- 复杂项目中，数据库、缓存、认证、任务队列等需要自己选择和组合。

---

## 三、安装与启动

推荐在虚拟环境中安装：

```bash
pip install fastapi uvicorn
```

其中：

- `fastapi`：框架本身。
- `uvicorn`：ASGI 服务器，用来运行 FastAPI 应用。

创建 `main.py`：

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello FastAPI"}
```

启动服务：

```bash
uvicorn main:app --reload
```

含义：

- `main`：文件名 `main.py`。
- `app`：文件里的 FastAPI 实例变量。
- `--reload`：开发模式，代码变更后自动重启。

访问：

```text
http://127.0.0.1:8000/
```

你会看到：

```json
{
  "message": "Hello FastAPI"
}
```

自动文档地址：

```text
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/redoc
```

这就是 FastAPI 最直观的体验：**写一个函数，就得到一个接口和一份可交互文档。**

---

## 四、FastAPI 的基本工作模型

一个接口通常由几部分组成：

```python
@app.get("/items/{item_id}")
def get_item(item_id: int, q: str | None = None):
    return {
        "item_id": item_id,
        "q": q,
    }
```

拆开看：

```text
@app.get("/items/{item_id}")
```

表示：

- HTTP 方法是 `GET`。
- 路径是 `/items/{item_id}`。
- `{item_id}` 是路径参数。

```text
def get_item(item_id: int, q: str | None = None):
```

表示：

- `item_id` 从路径里来。
- `q` 从查询参数里来。
- `item_id` 必须能转换成 `int`。
- `q` 可以不传，不传就是 `None`。

请求示例：

```text
GET /items/100?q=python
```

返回示例：

```json
{
  "item_id": 100,
  "q": "python"
}
```

如果访问：

```text
GET /items/abc
```

FastAPI 会自动返回参数校验错误，因为 `abc` 不能转换成 `int`。

---

## 五、路径参数、查询参数、请求体

### 5.1 路径参数

路径参数是 URL 路径的一部分：

```python
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id}
```

请求：

```text
GET /users/1
```

适合表示“资源 ID”：

- `/users/1`
- `/articles/100`
- `/orders/202607050001`

---

### 5.2 查询参数

查询参数在 `?` 后面：

```python
@app.get("/users")
def list_users(page: int = 1, size: int = 10, keyword: str | None = None):
    return {
        "page": page,
        "size": size,
        "keyword": keyword,
    }
```

请求：

```text
GET /users?page=2&size=20&keyword=alice
```

适合表示过滤、分页、排序：

- `page`
- `size`
- `keyword`
- `sort`
- `status`

---

### 5.3 请求体

请求体通常用于 `POST`、`PUT`、`PATCH`，常见格式是 JSON。

```python
from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    age: int = Field(ge=0, le=150)


@app.post("/users")
def create_user(user: UserCreate):
    return {
        "message": "created",
        "user": user,
    }
```

请求：

```http
POST /users
Content-Type: application/json

{
  "name": "Alice",
  "age": 20
}
```

FastAPI 会自动做几件事：

- 读取 JSON 请求体。
- 调用 Pydantic 校验字段。
- 把校验后的数据转换成 `UserCreate` 对象。
- 校验失败时返回清晰的错误信息。
- 把模型结构展示到 `/docs` 文档里。

这也是 FastAPI 和 Pydantic 配合最自然的地方。

---

## 六、响应模型 response_model

接口接收数据时要校验，返回数据时也应该控制格式。

例如创建用户时，输入模型里有密码，但响应里不能把密码返回给前端：

```python
from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str
    password: str = Field(min_length=8)


class UserRead(BaseModel):
    id: int
    username: str


@app.post("/users", response_model=UserRead)
def create_user(user: UserCreate):
    saved_user = {
        "id": 1,
        "username": user.username,
        "password": user.password,
    }
    return saved_user
```

虽然 `saved_user` 里有 `password`，但因为声明了：

```python
response_model=UserRead
```

最终响应只会包含：

```json
{
  "id": 1,
  "username": "alice"
}
```

`response_model` 的价值：

- 控制接口对外暴露的字段。
- 让响应结构进入 OpenAPI 文档。
- 避免误返回敏感字段。
- 让前端和调用方知道稳定的数据格式。

---

## 七、状态码与异常处理

### 7.1 指定状态码

创建资源时，一般返回 `201 Created`：

```python
from fastapi import status


@app.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    return {"message": "created"}
```

常见状态码：

| 状态码 | 含义 |
| --- | --- |
| 200 | 请求成功 |
| 201 | 创建成功 |
| 204 | 成功，但无响应体 |
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 409 | 资源冲突 |
| 422 | 请求体验证失败 |
| 500 | 服务器内部错误 |

---

### 7.2 HTTPException

当资源不存在时，不应该随便返回字符串，应该返回标准 HTTP 错误：

```python
from fastapi import HTTPException


@app.get("/users/{user_id}")
def get_user(user_id: int):
    if user_id != 1:
        raise HTTPException(status_code=404, detail="用户不存在")

    return {"id": 1, "name": "Alice"}
```

响应：

```json
{
  "detail": "用户不存在"
}
```

`HTTPException` 适合表示业务层面的 HTTP 错误：

- 找不到资源。
- 用户无权限。
- 数据冲突。
- 请求不符合业务规则。

---

## 八、同步函数与异步函数

FastAPI 支持两种路由函数：

```python
@app.get("/sync")
def sync_api():
    return {"mode": "sync"}
```

```python
@app.get("/async")
async def async_api():
    return {"mode": "async"}
```

怎么选？

| 场景 | 推荐 |
| --- | --- |
| 普通计算、简单逻辑 | `def` |
| 同步数据库客户端 | `def` |
| 调用异步 HTTP 客户端 | `async def` |
| 异步数据库客户端 | `async def` |
| WebSocket、流式输出 | `async def` |

不要以为所有接口都必须写成 `async def`。

关键原则：

**如果函数内部用了异步库并且需要 `await`，就写 `async def`；否则写普通 `def` 通常更简单。**

错误示例：

```python
import time


@app.get("/bad")
async def bad_api():
    time.sleep(5)
    return {"ok": True}
```

`time.sleep(5)` 会阻塞事件循环。异步函数里应该使用异步等待：

```python
import asyncio


@app.get("/good")
async def good_api():
    await asyncio.sleep(5)
    return {"ok": True}
```

如果要调用同步耗时库，需要更谨慎，避免阻塞整个服务。

---

## 九、依赖注入 Depends

依赖注入是 FastAPI 很重要的设计。

简单理解：

**把接口需要的公共前置逻辑，抽成函数，然后让 FastAPI 自动调用。**

例如分页参数：

```python
from fastapi import Depends
from pydantic import BaseModel, Field


class Pagination(BaseModel):
    page: int = Field(default=1, ge=1)
    size: int = Field(default=10, ge=1, le=100)


def get_pagination(page: int = 1, size: int = 10) -> Pagination:
    return Pagination(page=page, size=size)


@app.get("/articles")
def list_articles(pagination: Pagination = Depends(get_pagination)):
    return {
        "page": pagination.page,
        "size": pagination.size,
    }
```

更常见的依赖包括：

- 获取数据库 session。
- 获取当前登录用户。
- 校验 API Key。
- 读取配置。
- 复用分页、过滤参数。

例如模拟当前用户：

```python
from fastapi import Depends, Header, HTTPException


def get_current_user(x_token: str | None = Header(default=None)):
    if x_token != "secret-token":
        raise HTTPException(status_code=401, detail="未登录")

    return {"id": 1, "username": "alice"}


@app.get("/me")
def read_me(current_user: dict = Depends(get_current_user)):
    return current_user
```

请求时需要带请求头：

```http
GET /me
X-Token: secret-token
```

依赖注入的好处：

- 接口函数更干净。
- 公共逻辑可以复用。
- 测试时可以替换依赖。
- 复杂项目里可以清晰管理数据库、认证、配置等边界。

---

## 十、APIRouter：拆分路由

小项目可以把所有代码写在 `main.py`。

但项目变大后，建议按模块拆分：

```text
app/
├── main.py
├── routers/
│   ├── users.py
│   └── todos.py
├── schemas/
│   ├── user.py
│   └── todo.py
└── services/
    └── todo_service.py
```

`routers/todos.py`：

```python
from fastapi import APIRouter

router = APIRouter(prefix="/todos", tags=["todos"])


@router.get("/")
def list_todos():
    return [{"id": 1, "title": "Learn FastAPI"}]
```

`main.py`：

```python
from fastapi import FastAPI

from app.routers import todos

app = FastAPI(title="Todo API")

app.include_router(todos.router)
```

这样可以避免 `main.py` 越写越大。

---

## 十一、小项目：Todo API

下面用一个小项目把 FastAPI 的核心知识串起来。

项目目标：

- 创建待办事项。
- 查看待办列表。
- 查看单个待办。
- 更新待办状态。
- 删除待办。
- 使用 Pydantic 校验请求和响应。
- 使用 `HTTPException` 处理不存在的资源。
- 使用 `Depends` 注入仓库对象。
- 使用 `TestClient` 写测试。

为了聚焦 FastAPI，本项目先使用内存字典保存数据，不接数据库。

---

### 11.1 项目结构

```text
todo_api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── dependencies.py
│   ├── schemas.py
│   ├── repository.py
│   └── routers/
│       ├── __init__.py
│       └── todos.py
└── tests/
    └── test_todos.py
```

安装依赖：

```bash
pip install fastapi uvicorn pytest httpx
```

说明：

- `fastapi`：Web 框架。
- `uvicorn`：开发服务器。
- `pytest`：测试框架。
- `httpx`：FastAPI 测试客户端底层会用到。

---

### 11.2 schemas.py：定义请求和响应模型

`app/schemas.py`：

```python
from pydantic import BaseModel, Field


class TodoCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)


class TodoUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    completed: bool | None = None


class TodoRead(BaseModel):
    id: int
    title: str
    description: str | None
    completed: bool
```

这里分成三个模型：

- `TodoCreate`：创建时允许传什么。
- `TodoUpdate`：更新时允许传什么。
- `TodoRead`：响应时返回什么。

为什么不要只用一个模型？

因为不同场景的数据规则不一样：

- 创建时不需要客户端传 `id`。
- 更新时字段通常可以部分传。
- 响应时要包含服务端生成的 `id` 和 `completed`。

---

### 11.3 repository.py：封装数据访问

`app/repository.py`：

```python
from app.schemas import TodoCreate, TodoRead, TodoUpdate


class TodoRepository:
    def __init__(self):
        self._todos: dict[int, TodoRead] = {}
        self._next_id = 1

    def list(self) -> list[TodoRead]:
        return list(self._todos.values())

    def get(self, todo_id: int) -> TodoRead | None:
        return self._todos.get(todo_id)

    def create(self, data: TodoCreate) -> TodoRead:
        todo = TodoRead(
            id=self._next_id,
            title=data.title,
            description=data.description,
            completed=False,
        )
        self._todos[todo.id] = todo
        self._next_id += 1
        return todo

    def update(self, todo_id: int, data: TodoUpdate) -> TodoRead | None:
        todo = self.get(todo_id)
        if todo is None:
            return None

        update_data = data.model_dump(exclude_unset=True)
        updated = todo.model_copy(update=update_data)
        self._todos[todo_id] = updated
        return updated

    def delete(self, todo_id: int) -> bool:
        if todo_id not in self._todos:
            return False

        del self._todos[todo_id]
        return True
```

这里先用内存字典模拟数据库。

注意 `update` 方法：

```python
update_data = data.model_dump(exclude_unset=True)
```

`exclude_unset=True` 表示只取调用方真正传入的字段。

例如请求体是：

```json
{
  "completed": true
}
```

那么 `update_data` 只会包含：

```python
{"completed": True}
```

不会把没传的 `title`、`description` 覆盖成 `None`。

---

### 11.4 dependencies.py：定义依赖

`app/dependencies.py`：

```python
from app.repository import TodoRepository

todo_repository = TodoRepository()


def get_todo_repository() -> TodoRepository:
    return todo_repository
```

这里用一个全局仓库对象保存数据。

真实项目里，这里经常会变成：

- 获取数据库 session。
- 获取 Redis 连接。
- 获取当前用户。
- 获取配置对象。

---

### 11.5 routers/todos.py：编写接口

`app/routers/todos.py`：

```python
from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.dependencies import get_todo_repository
from app.repository import TodoRepository
from app.schemas import TodoCreate, TodoRead, TodoUpdate

router = APIRouter(prefix="/todos", tags=["todos"])


@router.get("/", response_model=list[TodoRead])
def list_todos(repo: TodoRepository = Depends(get_todo_repository)):
    return repo.list()


@router.post("/", response_model=TodoRead, status_code=status.HTTP_201_CREATED)
def create_todo(
    data: TodoCreate,
    repo: TodoRepository = Depends(get_todo_repository),
):
    return repo.create(data)


@router.get("/{todo_id}", response_model=TodoRead)
def get_todo(
    todo_id: int,
    repo: TodoRepository = Depends(get_todo_repository),
):
    todo = repo.get(todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="待办事项不存在")

    return todo


@router.patch("/{todo_id}", response_model=TodoRead)
def update_todo(
    todo_id: int,
    data: TodoUpdate,
    repo: TodoRepository = Depends(get_todo_repository),
):
    todo = repo.update(todo_id, data)
    if todo is None:
        raise HTTPException(status_code=404, detail="待办事项不存在")

    return todo


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(
    todo_id: int,
    repo: TodoRepository = Depends(get_todo_repository),
):
    deleted = repo.delete(todo_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="待办事项不存在")

    return Response(status_code=status.HTTP_204_NO_CONTENT)
```

这几个接口对应 REST 风格：

| 方法 | 路径 | 作用 |
| --- | --- | --- |
| `GET` | `/todos/` | 获取列表 |
| `POST` | `/todos/` | 创建待办 |
| `GET` | `/todos/{todo_id}` | 获取单个待办 |
| `PATCH` | `/todos/{todo_id}` | 局部更新待办 |
| `DELETE` | `/todos/{todo_id}` | 删除待办 |

---

### 11.6 main.py：组装应用

`app/main.py`：

```python
from fastapi import FastAPI

from app.routers import todos

app = FastAPI(
    title="Todo API",
    description="一个用于学习 FastAPI 的待办事项接口项目",
    version="0.1.0",
)

app.include_router(todos.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
```

启动：

```bash
uvicorn app.main:app --reload
```

访问文档：

```text
http://127.0.0.1:8000/docs
```

---

## 十二、用 curl 测试接口

### 12.1 健康检查

```bash
curl http://127.0.0.1:8000/health
```

响应：

```json
{
  "status": "ok"
}
```

---

### 12.2 创建待办

```bash
curl -X POST http://127.0.0.1:8000/todos/ \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"学习 FastAPI\",\"description\":\"完成 Todo API 示例\"}"
```

响应：

```json
{
  "id": 1,
  "title": "学习 FastAPI",
  "description": "完成 Todo API 示例",
  "completed": false
}
```

---

### 12.3 查看列表

```bash
curl http://127.0.0.1:8000/todos/
```

响应：

```json
[
  {
    "id": 1,
    "title": "学习 FastAPI",
    "description": "完成 Todo API 示例",
    "completed": false
  }
]
```

---

### 12.4 更新状态

```bash
curl -X PATCH http://127.0.0.1:8000/todos/1 \
  -H "Content-Type: application/json" \
  -d "{\"completed\":true}"
```

响应：

```json
{
  "id": 1,
  "title": "学习 FastAPI",
  "description": "完成 Todo API 示例",
  "completed": true
}
```

---

### 12.5 删除待办

```bash
curl -X DELETE -i http://127.0.0.1:8000/todos/1
```

成功时返回 `204 No Content`。

---

## 十三、自动 API 文档为什么重要

FastAPI 会根据以下信息生成 OpenAPI 文档：

- 路径和 HTTP 方法。
- 函数参数。
- Pydantic 请求模型。
- Pydantic 响应模型。
- 状态码。
- tags、title、description 等元信息。

这带来几个好处：

- 后端可以直接在浏览器里调试接口。
- 前端可以查看字段类型、必填项、示例响应。
- 其他服务可以基于 OpenAPI 生成客户端代码。
- 团队沟通成本更低。

如果你在 Pydantic 字段上写说明，文档会更清楚：

```python
from pydantic import BaseModel, Field


class TodoCreate(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=100,
        description="待办事项标题",
        examples=["学习 FastAPI"],
    )
```

---

## 十四、测试 FastAPI 接口

FastAPI 可以用 `TestClient` 直接测试接口，不需要真的启动 uvicorn。

`tests/test_todos.py`：

```python
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_todo():
    response = client.post(
        "/todos/",
        json={
            "title": "学习 FastAPI",
            "description": "写一个 Todo API",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["id"] >= 1
    assert data["title"] == "学习 FastAPI"
    assert data["completed"] is False


def test_create_todo_with_empty_title():
    response = client.post(
        "/todos/",
        json={
            "title": "",
            "description": "标题不能为空",
        },
    )

    assert response.status_code == 422


def test_get_missing_todo():
    response = client.get("/todos/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "待办事项不存在"
```

运行测试：

```bash
pytest
```

测试重点不是验证 FastAPI 自己能不能工作，而是验证你的业务规则：

- 创建成功时状态码是否正确。
- 请求体验证是否生效。
- 不存在的资源是否返回 404。
- 响应字段是否符合预期。

---

## 十五、依赖替换：让测试更干净

前面的 `todo_repository` 是全局对象。测试之间可能互相影响，因为数据会留在内存里。

FastAPI 支持在测试时替换依赖：

```python
from fastapi.testclient import TestClient

from app.dependencies import get_todo_repository
from app.main import app
from app.repository import TodoRepository


def create_test_client():
    test_repo = TodoRepository()

    def override_get_todo_repository():
        return test_repo

    app.dependency_overrides[get_todo_repository] = override_get_todo_repository
    return TestClient(app)


def test_create_and_get_todo():
    client = create_test_client()

    create_response = client.post("/todos/", json={"title": "Test Todo"})
    assert create_response.status_code == 201

    todo_id = create_response.json()["id"]

    get_response = client.get(f"/todos/{todo_id}")
    assert get_response.status_code == 200
    assert get_response.json()["title"] == "Test Todo"

    app.dependency_overrides.clear()
```

这就是依赖注入在测试中的价值：

- 生产环境用真实数据库。
- 测试环境用内存仓库或测试数据库。
- 接口代码本身不用改。

---

## 十六、项目分层怎么理解

一个 FastAPI 项目常见分层：

```text
HTTP 请求
  |
  v
Router 层：处理路径、参数、状态码、HTTPException
  |
  v
Service 层：处理业务逻辑
  |
  v
Repository 层：处理数据库访问
  |
  v
Database
```

小项目可以省略 Service 层：

```text
Router -> Repository
```

复杂项目建议加 Service 层：

```text
Router -> Service -> Repository
```

职责划分：

| 层 | 负责什么 | 不应该做什么 |
| --- | --- | --- |
| Router | HTTP 参数、状态码、调用 service | 写复杂业务逻辑 |
| Service | 业务规则、流程编排 | 直接关心 HTTP 请求对象 |
| Repository | 数据库增删改查 | 决定业务规则 |
| Schema | 请求和响应数据结构 | 写业务流程 |

一个判断标准：

**如果这段逻辑离开 HTTP 接口后仍然成立，就应该考虑放到 Service，而不是 Router。**

---

## 十七、从内存版升级到数据库版

Todo API 的内存版适合学习，但真实项目需要数据库。

升级方向：

```text
TodoRepository
    |
    v
SQLAlchemy / SQLModel / Tortoise ORM / asyncpg
    |
    v
PostgreSQL / MySQL / SQLite
```

数据库版通常需要新增：

- 数据库连接配置。
- ORM 模型，例如 `TodoTable`。
- 数据库 session 依赖。
- 迁移工具，例如 Alembic。
- 启动和关闭生命周期管理。

依赖函数可能变成这样：

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

这里的 `yield` 表示：

- 请求开始时创建数据库 session。
- 接口处理期间把 session 注入进去。
- 请求结束后自动关闭 session。

这也是 FastAPI 依赖系统很常见的用法。

---

## 十八、常见错误和避坑

### 18.1 API 模型和数据库模型混用

不要把数据库 ORM 模型直接当作接口响应模型。

原因：

- 数据库字段不一定都应该暴露。
- 接口字段和表字段经常不完全一致。
- 容易误返回密码、token、内部状态等敏感信息。

推荐：

```text
ORM Model：描述数据库表
Pydantic Schema：描述 API 输入输出
```

---

### 18.2 忘记 response_model

没有 `response_model` 时，接口可能返回过多字段。

推荐为主要接口都写响应模型：

```python
@router.get("/{todo_id}", response_model=TodoRead)
def get_todo(todo_id: int):
    ...
```

---

### 18.3 在 async def 中调用阻塞代码

错误：

```python
@app.get("/slow")
async def slow():
    time.sleep(10)
    return {"ok": True}
```

如果用了同步数据库驱动、同步 HTTP 客户端、同步文件操作，要谨慎放在 `async def` 里。

---

### 18.4 把所有代码写进 main.py

初学可以，项目变大后不建议。

更好的组织方式：

```text
main.py：创建 app，注册 router
routers/：接口层
schemas/：Pydantic 模型
services/：业务逻辑
repositories/：数据访问
dependencies.py：依赖注入
config.py：配置
```

---

### 18.5 错误地理解 422

FastAPI 请求体验证失败时，默认返回 `422 Unprocessable Entity`。

这通常表示：

- 字段缺失。
- 类型不对。
- 字段约束不满足。
- JSON 结构不符合模型。

例如 `title` 要求非空，但传了空字符串，就会返回 422。

---

## 十九、FastAPI 和 AI Agent 开发的关系

如果你后续学习 AI Agent，FastAPI 非常实用。

常见用法：

- 把 Agent 封装成 HTTP API。
- 给前端提供聊天接口。
- 提供工具调用接口。
- 做流式输出接口。
- 结合 WebSocket 做实时交互。
- 用 Pydantic 定义工具入参和结构化输出。

例如一个简单的聊天接口形状：

```python
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    answer: str


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    answer = f"你说的是：{request.message}"
    return ChatResponse(answer=answer)
```

后面如果替换成真实 LLM 调用，接口形状可以保持不变。

---

## 二十、学习路线建议

如果你已经学过 Python 基础、Pydantic、异步编程，可以按这个顺序学习 FastAPI：

1. 会写最简单的 `GET`、`POST` 接口。
2. 掌握路径参数、查询参数、请求体。
3. 熟悉 Pydantic 请求模型和响应模型。
4. 掌握 `HTTPException` 和状态码。
5. 会使用 `/docs` 调试接口。
6. 会用 `APIRouter` 拆分模块。
7. 理解 `Depends` 依赖注入。
8. 会写 `TestClient` 接口测试。
9. 接入数据库 session。
10. 再学习认证、权限、部署、日志、监控。

不要一开始就追求“大而全项目”。更推荐先把一个小 API 写完整：

```text
Todo API
用户 API
文章 API
文件上传 API
聊天 API
```

每个项目都练习：

- 请求模型。
- 响应模型。
- 状态码。
- 错误处理。
- 测试。
- 模块拆分。

---

## 二十一、完整单文件练习版

如果暂时不想拆目录，可以先用一个单文件版本练习。

`main.py`：

```python
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI(title="Simple Todo API")


class TodoCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)


class TodoUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    completed: bool | None = None


class TodoRead(BaseModel):
    id: int
    title: str
    description: str | None
    completed: bool


todos: dict[int, TodoRead] = {}
next_id = 1


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/todos", response_model=list[TodoRead])
def list_todos():
    return list(todos.values())


@app.post("/todos", response_model=TodoRead, status_code=status.HTTP_201_CREATED)
def create_todo(data: TodoCreate):
    global next_id

    todo = TodoRead(
        id=next_id,
        title=data.title,
        description=data.description,
        completed=False,
    )
    todos[todo.id] = todo
    next_id += 1
    return todo


@app.get("/todos/{todo_id}", response_model=TodoRead)
def get_todo(todo_id: int):
    todo = todos.get(todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="待办事项不存在")

    return todo


@app.patch("/todos/{todo_id}", response_model=TodoRead)
def update_todo(todo_id: int, data: TodoUpdate):
    todo = todos.get(todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="待办事项不存在")

    update_data = data.model_dump(exclude_unset=True)
    updated = todo.model_copy(update=update_data)
    todos[todo_id] = updated
    return updated


@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int):
    if todo_id not in todos:
        raise HTTPException(status_code=404, detail="待办事项不存在")

    del todos[todo_id]
```

启动：

```bash
uvicorn main:app --reload
```

练习顺序：

1. 先访问 `/health`。
2. 打开 `/docs`。
3. 创建一条 Todo。
4. 查询 Todo 列表。
5. 更新 Todo 状态。
6. 删除 Todo。
7. 故意传空标题，观察 422 错误。
8. 查询不存在的 ID，观察 404 错误。

---

## 二十二、总结

FastAPI 的核心不是“写接口很快”这么简单，而是它把几个重要能力组合得很好：

- 用路由把 HTTP 请求映射到 Python 函数。
- 用类型注解描述参数类型。
- 用 Pydantic 校验请求和响应数据。
- 用 `response_model` 控制对外输出。
- 用 `HTTPException` 表达 HTTP 错误。
- 用 `Depends` 复用依赖和公共逻辑。
- 用 `APIRouter` 组织中大型项目。
- 用自动文档降低前后端协作成本。
- 用测试保证接口行为稳定。

如果把 FastAPI 放进整个 Python 学习路线里，它通常位于这些知识之后：

```text
Python 基础
  -> 函数、模块、异常、类型注解
  -> Pydantic
  -> HTTP 基础
  -> 异步编程
  -> FastAPI
  -> 数据库 / 认证 / 部署 / AI Agent API
```

真正掌握 FastAPI 的关键，是多写几个小而完整的 API。不要只看语法，要把“请求进来、数据校验、业务处理、响应出去、测试覆盖”这一整条链路跑通。

---

## 参考资料

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Pydantic 官方文档](https://docs.pydantic.dev/latest/)
- [Uvicorn 官方文档](https://www.uvicorn.org/)
