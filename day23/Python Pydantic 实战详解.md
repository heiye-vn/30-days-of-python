# Python Pydantic 实战详解

> Pydantic 的核心价值不是“少写几个 if 判断”，而是把项目里的数据边界变清楚：外部传进来的 JSON、配置文件、环境变量、数据库记录、LLM 结构化输出，都先经过模型校验，再进入业务逻辑。这样代码会更稳，也更容易维护。

---

## 一、Pydantic 解决什么问题

真实项目里，很多 bug 不是算法错了，而是数据形状和你以为的不一样。

例如你期望拿到这样的用户数据：

```python
user = {
    "id": 1001,
    "name": "Alice",
    "age": 20,
}
```

但实际接口可能返回：

```python
user = {
    "id": "1001",
    "name": "Alice",
    "age": "20",
    "extra": "unexpected",
}
```

如果直接用 `dict`，你会在业务代码里到处写判断：

```python
user_id = int(user["id"])
age = int(user["age"])

if age < 0:
    raise ValueError("age 不能小于 0")
```

项目变大以后，这类判断会散落在很多地方。Pydantic 更推荐把规则集中在模型里：

```python
from pydantic import BaseModel, Field


class User(BaseModel):
    id: int
    name: str
    age: int = Field(ge=0)


user = User.model_validate({
    "id": "1001",
    "name": "Alice",
    "age": "20",
})

print(user.id)
print(user.age)
```

Pydantic 会做几件事：

- 根据类型注解把输入数据转换成目标类型。
- 检查字段是否缺失。
- 检查字段是否满足约束。
- 生成清晰的错误信息。
- 把模型序列化成 `dict` 或 JSON。

一句话理解：**类型注解告诉编辑器“我希望是什么类型”，Pydantic 在运行时检查“真实传进来的数据能不能变成这个类型”。**

---

## 二、BaseModel 基本用法

### 2.1 定义模型

Pydantic 最常用的入口是 `BaseModel`：

```python
from pydantic import BaseModel


class Product(BaseModel):
    id: int
    name: str
    price: float
    in_stock: bool = True
```

创建模型：

```python
product = Product(id="1", name="Keyboard", price="299.00")

print(product.id)        # 1
print(product.price)     # 299.0
print(product.in_stock)  # True
```

这里 `"1"` 会被转换为 `int`，`"299.00"` 会被转换为 `float`。

这也是 Pydantic 和普通 `dataclass` 的一个重要区别：`dataclass` 主要负责减少样板代码，Pydantic 还会做运行时校验和转换。

### 2.2 校验失败时会发生什么

```python
from pydantic import BaseModel, ValidationError


class Product(BaseModel):
    id: int
    name: str
    price: float


try:
    Product(id="abc", name="Keyboard", price="299.00")
except ValidationError as exc:
    print(exc)
```

`id="abc"` 不能转换成整数，所以会抛出 `ValidationError`。

实际项目里通常会这样处理：

```python
import logging

logger = logging.getLogger(__name__)


try:
    product = Product.model_validate(raw_data)
except ValidationError:
    logger.exception("商品数据格式不正确")
    raise
```

不要把 `ValidationError` 悄悄吞掉。数据格式不对是很重要的问题，应该记录日志或者返回明确错误。

### 2.3 `model_validate()` 和直接构造有什么区别

下面两种写法都常见：

```python
product = Product(id=1, name="Keyboard", price=299.0)
```

```python
product = Product.model_validate(raw_data)
```

推荐经验：

- 数据已经是明确的关键字参数时，可以直接 `Product(...)`。
- 数据来自外部接口、JSON、配置文件、数据库、LLM 输出时，推荐 `Product.model_validate(raw_data)`。

这样代码语义更清楚：这里是在“校验外部数据”。

---

## 三、Field：字段约束和元信息

`Field` 用来给字段加约束、默认值、说明、别名等信息。

```python
from pydantic import BaseModel, Field


class CreateUserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=8)
    age: int = Field(ge=0, le=150)
    email: str | None = None
```

常见约束：

- `min_length` / `max_length`：限制字符串长度。
- `ge`：大于等于。
- `gt`：大于。
- `le`：小于等于。
- `lt`：小于。
- `default`：默认值。
- `default_factory`：动态默认值。
- `description`：字段说明，常用于 API 文档。

动态默认值示例：

```python
from datetime import datetime
from pydantic import BaseModel, Field


class Event(BaseModel):
    name: str
    created_at: datetime = Field(default_factory=datetime.now)
```

不要这样写：

```python
created_at: datetime = datetime.now()
```

因为这会在类定义时执行一次，后续所有实例可能拿到同一个时间。`default_factory` 会在每次创建实例时重新调用。

---

## 四、嵌套模型：表达复杂数据结构

真实接口里的数据通常不是一层。

例如订单数据：

```python
from pydantic import BaseModel, Field


class Address(BaseModel):
    city: str
    street: str
    zipcode: str


class OrderItem(BaseModel):
    sku: str
    quantity: int = Field(gt=0)
    unit_price: float = Field(ge=0)


class Order(BaseModel):
    id: int
    user_id: int
    address: Address
    items: list[OrderItem]
```

使用：

```python
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

print(order.address.city)
print(order.items[0].sku)
```

嵌套模型的好处是：

- 数据结构一眼能看懂。
- 子结构可以复用。
- 错误定位更清楚，例如 `items.1.quantity` 出错。
- FastAPI、OpenAPI、LLM 结构化输出都可以复用同一套 schema。

---

## 五、序列化：模型转 dict / JSON

Pydantic v2 常用两个方法：

```python
model.model_dump()
model.model_dump_json()
```

示例：

```python
from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str
    email: str | None = None


user = User(id=1, name="Alice")

print(user.model_dump())
print(user.model_dump(exclude_none=True))
print(user.model_dump_json())
```

输出类似：

```python
{"id": 1, "name": "Alice", "email": None}
{"id": 1, "name": "Alice"}
```

实际项目中常见用法：

```python
payload = user.model_dump(exclude_none=True)
```

这样可以把 `None` 字段去掉，再传给外部 API 或写入 JSON 文件。

也可以只导出部分字段：

```python
public_user = user.model_dump(include={"id", "name"})
```

或者排除敏感字段：

```python
safe_data = user.model_dump(exclude={"password"})
```

---

## 六、field_validator：单字段校验

字段约束能解决很多问题，但有些规则需要自己写。

例如用户名不允许包含空格：

```python
from pydantic import BaseModel, field_validator


class CreateUserRequest(BaseModel):
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def username_must_not_contain_space(cls, value: str) -> str:
        if " " in value:
            raise ValueError("username 不能包含空格")
        return value
```

注意：

- 校验通过时要返回处理后的值。
- 校验失败时抛出 `ValueError`。
- `@field_validator` 适合只依赖当前字段的规则。

也可以在校验里做简单清洗：

```python
from pydantic import BaseModel, field_validator


class Tag(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return value.strip().lower()
```

但不要把太重的业务逻辑放进 validator。它应该负责“数据是否合格”和“轻量规范化”，不要在里面查数据库、发请求、写文件。

---

## 七、model_validator：多字段联合校验

如果规则需要同时看多个字段，就用 `model_validator`。

例如结束时间必须晚于开始时间：

```python
from datetime import datetime
from pydantic import BaseModel, model_validator


class TimeRange(BaseModel):
    start_at: datetime
    end_at: datetime

    @model_validator(mode="after")
    def check_time_range(self) -> "TimeRange":
        if self.end_at <= self.start_at:
            raise ValueError("end_at 必须晚于 start_at")
        return self
```

实际项目里常见的联合校验：

- `start_at` 必须早于 `end_at`。
- `min_price` 不能大于 `max_price`。
- `password` 和 `confirm_password` 必须一致。
- 某个字段存在时，另一个字段也必须存在。

---

## 八、严格模式：什么时候不希望自动转换

Pydantic 默认会尝试做类型转换，例如 `"123"` 转成 `123`。

这在处理 HTTP 请求和配置文件时很方便，但有些场景你可能希望更严格：

```python
from pydantic import BaseModel, ConfigDict


class PaymentRequest(BaseModel):
    model_config = ConfigDict(strict=True)

    amount: float
    user_id: int
```

严格模式下，传入 `"100.0"` 不会被自动转换成 `float`。

经验建议：

- 面向用户输入、HTTP 查询参数、环境变量时，可以接受合理转换。
- 金额、权限、安全策略、内部事件等关键数据，可以考虑更严格。
- 不要为了“看起来严谨”到处开严格模式，否则会让接口使用体验变差。

---

## 九、额外字段：ignore / forbid / allow

默认情况下，多余字段通常会被忽略。

```python
from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str


user = User.model_validate({
    "id": 1,
    "name": "Alice",
    "unknown": "value",
})

print(user.model_dump())
```

如果希望外部数据不能带任何未定义字段，可以配置：

```python
from pydantic import BaseModel, ConfigDict


class User(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    name: str
```

实际项目建议：

- 对外部 API 请求体：推荐 `extra="forbid"`，避免调用方传错字段还不知道。
- 对第三方 API 响应：可以用默认忽略，因为第三方可能新增字段。
- 对日志、埋点、动态 metadata：可以考虑 `extra="allow"`。

---

## 十、配置管理：BaseSettings

项目配置很适合用 Pydantic 管理，尤其是环境变量。

Pydantic v2 中，Settings 功能在单独的包里：

```bash
pip install pydantic-settings
```

示例：

```python
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="APP_",
        extra="ignore",
    )

    debug: bool = False
    database_url: str
    openai_api_key: str = Field(repr=False)
    request_timeout: int = 30


settings = Settings()
```

对应 `.env`：

```text
APP_DEBUG=true
APP_DATABASE_URL=postgresql://user:password@localhost:5432/app
APP_OPENAI_API_KEY=your-api-key
APP_REQUEST_TIMEOUT=60
```

使用：

```python
print(settings.debug)
print(settings.database_url)
print(settings.request_timeout)
```

`Field(repr=False)` 可以避免对象打印时直接暴露密钥。

实际项目里常见写法：

```python
from functools import lru_cache


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

这样全项目复用同一个配置对象，也方便测试时替换。

---

## 十一、FastAPI 中的典型用法

FastAPI 和 Pydantic 的配合非常自然：请求体、响应体、错误提示、接口文档都可以由模型驱动。

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()


class CreateTaskRequest(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    priority: int = Field(ge=1, le=5)


class TaskResponse(BaseModel):
    id: int
    title: str
    priority: int
    done: bool


@app.post("/tasks", response_model=TaskResponse)
def create_task(request: CreateTaskRequest) -> TaskResponse:
    return TaskResponse(
        id=1,
        title=request.title,
        priority=request.priority,
        done=False,
    )
```

这里 Pydantic 做了几件事：

- 校验请求 JSON。
- 把请求数据转换成 `CreateTaskRequest` 对象。
- 校验响应结果是否符合 `TaskResponse`。
- 生成 OpenAPI 文档。

在 FastAPI 项目里，通常会把模型分层：

```text
src/
└── todo_app/
    ├── api/
    │   └── routes.py
    ├── schemas/
    │   └── task.py
    ├── services/
    │   └── task_service.py
    └── settings.py
```

`schemas/task.py`：

```python
from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    priority: int = Field(default=3, ge=1, le=5)


class TaskRead(BaseModel):
    id: int
    title: str
    priority: int
    done: bool
```

经验规则：

- 请求模型叫 `XxxCreate`、`XxxUpdate`。
- 响应模型叫 `XxxRead` 或 `XxxResponse`。
- 数据库 ORM 模型和 API schema 不要混成一个类。

---

## 十二、AI Agent 项目中的用法

做 AI Agent 时，Pydantic 特别适合表达“工具入参”和“模型结构化输出”。

### 12.1 工具入参

例如有一个搜索工具：

```python
from pydantic import BaseModel, Field


class SearchInput(BaseModel):
    query: str = Field(min_length=1, description="搜索关键词")
    top_k: int = Field(default=5, ge=1, le=20, description="返回结果数量")
```

业务函数：

```python
def search_documents(input_data: SearchInput) -> list[str]:
    query = input_data.query
    top_k = input_data.top_k
    return []
```

当 LLM 决定调用工具时，先用 `SearchInput` 校验参数，可以避免这些问题：

- `top_k` 传成负数。
- 缺少 `query`。
- 多传了业务不认识的字段。
- 字段类型不符合预期。

### 12.2 结构化输出

例如你希望模型输出一个任务拆解结果：

```python
from pydantic import BaseModel, Field


class TaskStep(BaseModel):
    title: str
    detail: str
    estimated_minutes: int = Field(ge=1)


class TaskPlan(BaseModel):
    goal: str
    steps: list[TaskStep]
    risks: list[str] = []
```

拿到模型输出后，不要直接信任字符串里的 JSON：

```python
plan = TaskPlan.model_validate(raw_output)
```

后续业务只处理 `TaskPlan`，而不是到处写 `raw_output["steps"][0]["title"]`。

这会让 Agent 项目更稳，因为 LLM 输出天然有不确定性，越靠近边界越应该校验。

---

## 十三、Pydantic 和 dataclass 怎么选

可以这样判断：

| 场景 | 推荐 |
|---|---|
| 内部简单数据对象，不需要运行时校验 | `dataclass` |
| 外部输入、API 请求、JSON、配置文件 | Pydantic |
| 需要自动生成 JSON Schema | Pydantic |
| 需要字段约束、嵌套校验、序列化 | Pydantic |
| 性能极端敏感、数据已可信 | `dataclass` 或普通类 |

简单经验：

- **边界数据用 Pydantic。**
- **内部纯业务对象可以用 dataclass。**

边界数据包括：

- HTTP 请求和响应。
- 配置文件和环境变量。
- 第三方 API 返回。
- 消息队列 payload。
- LLM 输出。
- 从 CSV / JSON 文件读入的数据。

---

## 十四、项目中的组织方式

一个实际项目可以这样组织：

```text
my_project/
├── src/
│   └── my_project/
│       ├── main.py
│       ├── settings.py
│       ├── schemas/
│       │   ├── user.py
│       │   └── task.py
│       ├── services/
│       │   └── task_service.py
│       └── clients/
│           └── github_client.py
└── tests/
    ├── test_settings.py
    └── test_task_schema.py
```

建议分工：

- `settings.py`：放 `BaseSettings` 配置模型。
- `schemas/`：放 API 请求响应模型、外部数据模型。
- `services/`：放业务逻辑，不直接处理杂乱的原始 dict。
- `clients/`：调用第三方 API，并把响应转换成 Pydantic 模型。

第三方 API 客户端示例：

```python
import httpx
from pydantic import BaseModel


class GithubUser(BaseModel):
    id: int
    login: str
    html_url: str


def get_github_user(username: str) -> GithubUser:
    response = httpx.get(f"https://api.github.com/users/{username}", timeout=10)
    response.raise_for_status()
    return GithubUser.model_validate(response.json())
```

这样 `clients/` 之外的代码拿到的就是可靠的 `GithubUser`，而不是未知形状的 `dict`。

---

## 十五、测试 Pydantic 模型

模型里有约束，就值得测。

```python
import pytest
from pydantic import ValidationError


def test_create_user_request_accepts_valid_data():
    request = CreateUserRequest(
        username="alice",
        password="password123",
        age=20,
    )

    assert request.username == "alice"


def test_create_user_request_rejects_short_password():
    with pytest.raises(ValidationError):
        CreateUserRequest(
            username="alice",
            password="123",
            age=20,
        )
```

优先测试：

- 自定义 validator。
- 金额、时间范围、权限这类关键约束。
- 配置模型是否能正确读取环境变量。
- 第三方 API 响应模型是否覆盖真实字段。

不需要把 Pydantic 自己已经保证的基础能力全部测一遍。比如 `int` 字段不能接受无法转换的字符串，这种通常不用测。

---

## 十六、常见反模式

### 16.1 把业务逻辑塞进 validator

不推荐：

```python
@field_validator("user_id")
@classmethod
def check_user_exists(cls, value: int) -> int:
    if not database.user_exists(value):
        raise ValueError("用户不存在")
    return value
```

validator 里查数据库会让模型变重，也让测试和复用变麻烦。

更推荐：

```python
request = CreateOrderRequest.model_validate(raw_data)
user = user_service.get_user(request.user_id)
```

模型负责数据形状，service 负责业务规则。

### 16.2 所有模型都写在一个 schemas.py

项目小的时候可以，项目稍大就会混乱。

更推荐按领域拆：

```text
schemas/
├── user.py
├── order.py
└── payment.py
```

### 16.3 API 模型和数据库模型混用

数据库模型通常关心表结构，API 模型关心对外暴露什么。

例如用户表里可能有 `hashed_password`，但响应模型绝不能返回它。

```python
class UserResponse(BaseModel):
    id: int
    username: str
```

### 16.4 忘记处理敏感字段

密钥、密码、token 不应该随便打印或返回：

```python
from pydantic import BaseModel, Field


class Settings(BaseModel):
    api_key: str = Field(repr=False)
```

响应模型里也不要包含敏感字段。

---

## 十七、学习路线

建议按这个顺序练：

1. `BaseModel`：会定义模型、创建实例、读取字段。
2. `Field`：会写默认值、长度、数值范围。
3. 嵌套模型：会表达 list、dict、子模型。
4. `model_dump()`：会把模型转成 dict / JSON。
5. `field_validator`：会写单字段校验。
6. `model_validator`：会写多字段联合校验。
7. `BaseSettings`：会管理 `.env` 和环境变量。
8. FastAPI：会定义请求模型和响应模型。
9. AI Agent：会用 Pydantic 约束工具参数和结构化输出。

---

## 总结

Pydantic 最适合放在项目边界：

- 外部请求进来时，用它校验请求。
- 配置加载进来时，用它校验配置。
- 第三方 API 返回时，用它校验响应。
- LLM 输出结构化数据时，用它校验格式。
- 数据要返回给用户时，用它控制序列化结果。

把边界守住以后，业务代码里就不需要到处猜“这个字段到底有没有”“这个值到底是不是 int”。这就是 Pydantic 在实际项目里的真正价值：让不可靠的外部数据，变成可靠的内部对象。

---

## 参考资料

- [Pydantic Models](https://docs.pydantic.dev/latest/concepts/models/)
- [Pydantic Fields](https://docs.pydantic.dev/latest/concepts/fields/)
- [Pydantic Validators](https://docs.pydantic.dev/latest/concepts/validators/)
- [Pydantic Serialization](https://docs.pydantic.dev/latest/concepts/serialization/)
- [Pydantic Settings Management](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
