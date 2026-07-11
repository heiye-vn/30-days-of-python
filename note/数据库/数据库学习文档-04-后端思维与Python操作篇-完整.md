# 数据库学习文档 - 第 04 篇：后端思维与 Python 操作篇

> 面向"前端转后端 Python 开发者"的数据库学习文档
> 适用读者：已掌握 Node.js 版 LangChain/LangGraph，正在学习后端 Python（FastAPI/LangChain 方向）
> 运行环境：Windows（cmd.exe，注意 GBK 编码问题，代码中不使用 emoji）

---

## 第七章 后端思维：从前端到后端的范式转换

前面六章我们打下了 SQL 和事务的硬基础。从本章开始，我们要完成一次"思维操作系统"的升级——从前端工程师的数据思维切换到后端工程师的数据思维。这个转换比学任何具体语法都重要，因为它决定了你设计的 API、数据模型和系统架构是否经得起生产环境的考验。

> 前端类比：如果你把前端技能树比作一棵以"组件渲染"为根的树，那么后端技能树是以"数据流经系统"为根的另一棵树。两棵树的节点有重叠（比如 JSON、HTTP），但根不同，生长方向完全不同。本章就是帮你完成"换根"操作。

---

### 7.1 数据流视角的转换

#### 7.1.1 前端的数据流：组件状态驱动渲染

在前端开发中，数据流的核心是"状态 -> 视图"。无论你用 React、Vue 还是原生 JS，本质上都是：

```
用户交互（点击/输入）
  -> 更新组件状态（useState / Redux dispatch）
  -> 触发重新渲染（re-render）
  -> 虚拟 DOM diff
  -> 更新真实 DOM
```

以 Redux 为例，经典的数据流是这样的：

```javascript
// 前端 Redux 数据流
// 1. 用户点击"提交订单"按钮
// 2. 派发 action
dispatch({ type: 'SUBMIT_ORDER', payload: { items: cart, total: 999 } });

// 3. reducer 处理状态变更
function orderReducer(state, action) {
  switch (action.type) {
    case 'SUBMIT_ORDER':
      return { ...state, orders: [...state.orders, action.payload], loading: true };
    case 'SUBMIT_ORDER_SUCCESS':
      return { ...state, loading: false, orders: [...state.orders, action.payload] };
    default:
      return state;
  }
}

// 4. Store 更新后，connect/useSelector 触发组件重渲染
// 5. DOM 更新，用户看到"下单成功"提示
```

这条数据流的特点是：**数据在浏览器内存中流转，生命周期短，作用范围是单个用户的浏览器**。页面刷新后，Redux Store 里的数据就没了（除非做了持久化）。前端的数据流是"垂直"的——从状态层流向视图层，不涉及跨用户、跨请求的数据共享。

#### 7.1.2 后端的数据流：请求穿越多层架构

后端的数据流完全不同。一个 HTTP 请求从到达服务器到返回响应，要穿越多个层，每一层都有不同的职责：

```
用户操作（浏览器/APP 发起 HTTP 请求）
  -> API 网关（路由、限流、认证）
  -> Controller 层（参数校验、请求解析）
  -> Service 层（业务逻辑编排）
  -> Repository 层（数据访问，ORM/SQL）
  -> Database（执行查询/写入）
  <- 结果原路返回：Database -> Repository -> Service -> Controller -> HTTP 响应
```

用 Python FastAPI 的代码来体现这个流程：

```python
# ============ Controller 层（路由 + 参数校验） ============
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/orders", tags=["orders"])

class CreateOrderRequest(BaseModel):
    user_id: int
    product_ids: list[int]

@router.post("/")
async def create_order(
    req: CreateOrderRequest,
    order_service: OrderService = Depends(get_order_service),
):
    """创建订单 - Controller 只负责接收请求、调用 Service"""
    try:
        order = await order_service.create_order(req.user_id, req.product_ids)
        return {"code": 0, "data": order}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============ Service 层（业务逻辑编排） ============
class OrderService:
    def __init__(self, order_repo: OrderRepository, product_repo: ProductRepository):
        self.order_repo = order_repo
        self.product_repo = product_repo

    async def create_order(self, user_id: int, product_ids: list[int]) -> dict:
        # 1. 查商品信息（调用 Repository）
        products = await self.product_repo.find_by_ids(product_ids)
        if len(products) != len(product_ids):
            raise ValueError("部分商品不存在")

        # 2. 计算总价
        total = sum(p["price"] for p in products)

        # 3. 扣减库存（调用 Repository）
        for p in products:
            affected = await self.product_repo.deduct_stock(p["id"], 1)
            if affected == 0:
                raise ValueError(f"商品 {p['name']} 库存不足")

        # 4. 创建订单（调用 Repository）
        order_id = await self.order_repo.insert_order(user_id, total, product_ids)
        return {"order_id": order_id, "total": total}


# ============ Repository 层（数据访问） ============
class OrderRepository:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def insert_order(self, user_id, total, product_ids) -> int:
        async with self.session_factory() as session:
            # 最终落到数据库操作
            order = Order(user_id=user_id, total_amount=total, status="CREATED")
            session.add(order)
            await session.flush()  # 获取自增 ID
            for pid in product_ids:
                session.add(OrderItem(order_id=order.id, product_id=pid, quantity=1))
            await session.commit()
            return order.id
```

注意这里的关键差异：后端数据流是**水平穿越多层**的，数据在请求生命周期内穿越 Controller -> Service -> Repository -> Database，最终持久化到磁盘。而且这些操作可能涉及**事务**（扣库存和创建订单必须在同一个事务里，要么都成功，要么都回滚），这在纯前端开发中是不存在的概念。

#### 7.1.3 全链路数据流：Redux vs 后端分层对比

理解这个转换最好的方式是做一张对照表，把 Redux 的概念映射到后端分层：

| 前端（Redux） | 后端（分层架构） | 核心差异 |
|---|---|---|
| Action（dispatch 一个动作） | HTTP Request（用户发起请求） | 前端是函数调用，后端是网络请求 |
| Reducer（纯函数处理状态变更） | Service（业务逻辑编排） | Reducer 是同步纯函数；Service 可异步、可操作 DB |
| Store（单一状态树） | Database（持久化存储） | Store 在内存中，刷新即失；DB 在磁盘上，永久存储 |
| useSelector（订阅状态变化） | Repository（查询数据库） | 前端从内存读；后端从磁盘读 |
| 组件 re-render（更新 DOM） | HTTP Response（返回 JSON） | 前端渲染 UI；后端返回数据 |
| 中间件（redux-thunk/saga） | 中间件（FastAPI middleware） | 都是请求/动作到达目标前做拦截处理 |

关键认知差异在于：

**1. 状态的生命周期完全不同。** Redux Store 的生命周期是"页面打开到关闭"，而后端的状态（数据库中的数据）生命周期是"从写入到删除"，可能跨越数年。在前端你几乎不需要担心"状态被别人改了"，因为每个用户有自己的浏览器。但在后端，你时刻面对的是多用户并发修改同一份数据。

**2. 数据的"真相来源"（Source of Truth）不同。** 前端的真相来源是 Store（或后端 API 的返回），而后端的真相来源是数据库。如果数据库里的数据错了，无论你的 Service 逻辑多完美，返回给用户的就是错的。这就是为什么后端工程师对数据库 schema 设计、数据完整性约束如此执着。

**3. 错误的代价不同。** 前端出了 bug，用户刷新一下可能就好了，最坏的情况是当前页面不可用。后端出了 bug，可能导致数据被污染——错误的转账、丢失的订单、泄露的用户信息——这些是刷新解决不了的，而且影响所有用户。

用一段代码感受这个差异：

```python
# 前端思维：直接改内存中的对象（安全，因为只有你在操作）
def frontend_thinking():
    user = {"id": 1, "balance": 1000}
    user["balance"] -= 100
    return user  # 永远成功，因为没有并发

# 后端思维：改数据库中的记录（不安全，需要考虑并发和事务）
async def backend_thinking(session):
    # 步骤1：查询用户
    user = await session.execute(
        select(User).where(User.id == 1).with_for_update()  # 加行锁
    )
    user = user.scalar_one()
    if user.balance < 100:
        raise ValueError("余额不足")

    # 步骤2：扣减余额
    user.balance -= 100

    # 步骤3：记录流水
    session.add(TransactionLog(user_id=1, amount=-100, type="payment"))

    # 步骤4：提交事务（要么全部成功，要么全部回滚）
    await session.commit()
    return user
```

前端开发者转后端时，最容易踩的坑就是"直接修改查出来的对象就以为完事了"——忘了 `commit()`，忘了加锁，忘了事务。这些概念在下一节的数据建模中会进一步体现。

---

### 7.2 数据建模思维

#### 7.2.1 前端的 JSON 对象树 vs 后端的关系模型

前端开发者处理数据时，习惯的格式是 JSON 对象树。一个用户对象可能长这样：

```javascript
// 前端习惯的数据结构：嵌套 JSON
const user = {
  id: 1,
  name: "张三",
  email: "zhangsan@example.com",
  orders: [
    {
      id: 101,
      total: 999,
      items: [
        { product_id: 1, name: "iPhone", price: 7999, qty: 1 },
        { product_id: 3, name: "AirPods", price: 1899, qty: 1 }
      ]
    }
  ],
  addresses: [
    { city: "北京", detail: "朝阳区xxx" },
    { city: "上海", detail: "浦东新区xxx" }
  ]
};
```

这种结构的特点是：**灵活、嵌套、无 schema 约束**。你可以随时加字段、改结构，不需要"迁移"。在前端这完全没问题，因为数据是从后端 API 拿来的，前端只是消费和展示。

但在后端，如果你把这种嵌套 JSON 直接存到数据库的一张表的一个字段里，你会遇到严重的维护问题：

- 怎么按订单 ID 查某个商品？（需要解析 JSON 再遍历）
- 怎么保证订单号不重复？（JSON 里没法加唯一约束）
- 怎么统计"昨天卖了多少 iPhone"？（需要遍历所有用户的 JSON）
- 怎么更新某个订单的状态而不影响其他数据？（要序列化整个 JSON 再反序列化写回）

后端的解法是**关系模型**——把嵌套结构拆平，用外键关联：

```
users 表:       id | name | email
orders 表:      id | user_id (FK) | total | status
order_items 表: id | order_id (FK) | product_id (FK) | qty | price
products 表:    id | name | price
addresses 表:   id | user_id (FK) | city | detail
```

每个实体一张表，通过外键关联。查询"张三的订单里的商品"时用 JOIN 把它们拼回来。

> 前端类比：关系模型就像把一个深度嵌套的 JSON 拆成多个独立的数据表，每个表有明确的 schema（TypeScript interface），表之间通过 id 字段关联——类似于你在前端用 normalized state（Redux 的 normalize 模式）管理数据，而不是把整个嵌套对象塞进 state。

Redux 官方文档推荐的 normalized state 就是一种"关系模型"思维：

```javascript
// Redux normalized state（已经是一种关系模型思维！）
const state = {
  users: { byId: { 1: { id: 1, name: "张三" } }, allIds: [1] },
  orders: { byId: { 101: { id: 101, userId: 1, total: 999 } }, allIds: [101] },
  orderItems: { byId: { 1: { id: 1, orderId: 101, productId: 1, qty: 1 } }, allIds: [1] }
};
```

如果你理解了 Redux 的 normalized state，你就已经理解了关系模型的核心思想：**数据扁平化存储，用 ID 关联，需要时再 join 组装**。

#### 7.2.2 ORM 作为桥梁：SQLAlchemy 连接两种思维

ORM（Object-Relational Mapping）最大的价值就是在前端的"对象树思维"和后端的"关系模型思维"之间架了一座桥梁。SQLAlchemy 让你用 Python 类定义表结构，用对象关系表达外键关联，查询时自动 JOIN 组装成对象树——既保留了关系模型的规范性，又获得了面向对象的开发体验。

```python
# SQLAlchemy 2.0 模型定义：用 Python 类表达关系模型
from sqlalchemy import String, ForeignKey, Numeric, Integer, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime
from decimal import Decimal

class Base(DeclarativeBase):
    """SQLAlchemy 2.0 基类（替代旧版 declarative_base()）"""
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64))
    email: Mapped[str] = mapped_column(String(128), unique=True)
    created_at: Mapped[datetime] = mapped_column(default=func.now())

    # 关系定义：一个用户有多个订单（类似前端的嵌套对象访问）
    orders: Mapped[list["Order"]] = relationship(back_populates="user")

class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    total: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    status: Mapped[str] = mapped_column(String(16), default="CREATED")
    created_at: Mapped[datetime] = mapped_column(default=func.now())

    # 关系定义：订单属于哪个用户
    user: Mapped["User"] = relationship(back_populates="orders")
    # 关系定义：订单包含多个订单项
    items: Mapped[list["OrderItem"]] = relationship(back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    order: Mapped["Order"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship()

class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    stock: Mapped[int] = mapped_column(Integer, default=0)
```

定义完模型后，查询时你可以像操作对象树一样访问关联数据：

```python
from sqlalchemy import select
from sqlalchemy.orm import selectinload

# 查询用户并预加载订单和订单项（类似前端的嵌套对象访问）
stmt = (
    select(User)
    .options(selectinload(User.orders).selectinload(Order.items))
    .where(User.id == 1)
)
result = await session.execute(stmt)
user = result.scalar_one()

# 此时的 user 对象就像前端的嵌套 JSON 一样可以访问：
for order in user.orders:
    print(f"订单 {order.id} 状态: {order.status}")
    for item in order.items:
        print(f"  商品ID: {item.product_id} 数量: {item.quantity}")
```

ORM 在底层会自动翻译成 SQL JOIN 查询，但你在 Python 代码里操作的依然是对象。这就是 ORM 作为"桥梁"的价值：**底层是关系模型（规范、可查询、有约束），开发体验是对象树（直观、类型安全、符合直觉）**。

#### 7.2.3 JSONB / JSON 字段：什么时候拆表，什么时候用 JSON

并非所有嵌套数据都需要拆成关系表。有一种常见的困境：某些字段结构灵活、变化频繁、不需要单独查询——比如用户的偏好设置、商品的动态属性（不同品类属性不同）、API 的响应日志。这时候如果强制拆表，会制造大量稀疏的、大部分字段为 NULL 的表，反而增加复杂度。

PostgreSQL 的 JSONB 和 MySQL 的 JSON 类型提供了一种折中方案：把灵活的嵌套结构存到 JSON 字段中，同时保留关系模型的整体规范性。

决策框架：

| 特征 | 拆成关系表 | 用 JSON 字段 |
|---|---|---|
| 是否需要独立查询/过滤 | 是 | 否 |
| 是否需要唯一约束/外键 | 是 | 否 |
| 结构是否稳定 | 稳定 | 频繁变化 |
| 是否需要做聚合统计 | 是 | 否 |
| 数据是否参与 JOIN | 是 | 否 |
| 字段数量 | 多且固定 | 少且动态 |

举例说明：

```python
# Product 表：固定属性拆成列，动态属性存 JSONB
from sqlalchemy.dialects.postgresql import JSONB

class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    stock: Mapped[int] = mapped_column(Integer, default=0)

    # PostgreSQL JSONB 字段：存储不同品类的动态属性
    # 比如手机存 {"screen_size": "6.1寸", "cpu": "A16"}
    # 电脑存 {"cpu": "M3", "ram": "16GB", "disk": "512GB"}
    # 这些属性因品类而异，且不需要作为独立列查询
    attributes: Mapped[dict] = mapped_column(JSONB, default=dict)
```

PostgreSQL 的 JSONB 还支持索引和查询操作：

```sql
-- 查所有 CPU 是 M3 的商品（JSONB 查询）
SELECT name, price, attributes->>'cpu' AS cpu
FROM products
WHERE attributes->>'cpu' = 'M3';

-- 给 JSONB 的某个 key 加 GIN 索引
CREATE INDEX idx_product_attributes
  ON products USING GIN (attributes);
```

> 前端类比：这就像 TypeScript 中，你有一部分字段用强类型 interface 定义（对应表的列），另一部分用 `Record<string, unknown>` 或 `any` 存储（对应 JSON 字段）。强类型字段方便编译器检查和重构，而灵活字段适合存"不确定结构"的数据。关系模型的列就是"强类型字段"，JSONB 就是"灵活字段"。

---

### 7.3 接口设计思维

#### 7.3.1 RESTful API 设计与数据库表结构的关系

前端开发者消费 API 时，通常把 API 看作返回 JSON 的"黑盒"。但转到后端后，你必须理解 API 的设计直接受限于数据库表结构，两者之间有密切的映射关系。

RESTful API 的核心原则是"资源导向"——每个 URL 代表一个资源，HTTP 方法代表操作类型：

```
GET    /api/users          -> 查询用户列表
POST   /api/users          -> 创建用户
GET    /api/users/{id}     -> 查询单个用户
PUT    /api/users/{id}     -> 更新用户（全量）
PATCH  /api/users/{id}     -> 更新用户（部分）
DELETE /api/users/{id}     -> 删除用户
```

这个设计看起来是"一个 API 端点对应一张表"，但实际业务中并非总是如此。关键问题是：**资源粒度怎么定？**

#### 7.3.2 资源粒度：一个端点对应一张表还是多张表联合

有三种常见情况：

**情况一：端点直接映射一张表。** 最简单的 CRUD 场景，比如用户管理：

```python
@router.get("/users")
async def list_users(skip: int = 0, limit: int = 20, db: AsyncSession = Depends(get_db)):
    stmt = select(User).offset(skip).limit(limit).order_by(User.id)
    result = await db.execute(stmt)
    return result.scalars().all()
```

这种情况下，API 返回的就是单表数据，前端拿到后直接展示。

**情况二：端点聚合多张表的数据。** 比如"订单详情"接口，需要返回订单信息 + 用户信息 + 商品列表：

```python
@router.get("/orders/{order_id}")
async def get_order_detail(order_id: int, db: AsyncSession = Depends(get_db)):
    # 多表联合查询，组装成一个聚合响应
    stmt = (
        select(Order)
        .options(
            selectinload(Order.user),
            selectinload(Order.items).selectinload(OrderItem.product),
        )
        .where(Order.id == order_id)
    )
    result = await db.execute(stmt)
    order = result.scalar_one_or_none()
    if order is None:
        raise HTTPException(404, "订单不存在")

    # 组装成前端需要的嵌套 JSON 结构
    return {
        "order_id": order.id,
        "status": order.status,
        "total": float(order.total),
        "created_at": order.created_at.isoformat(),
        "user": {
            "id": order.user.id,
            "name": order.user.name,
            "email": order.user.email,
        },
        "items": [
            {
                "product_id": item.product_id,
                "product_name": item.product.name,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),
                "subtotal": float(item.unit_price * item.quantity),
            }
            for item in order.items
        ],
    }
```

> 前端类比：这就像前端中一个"页面级组件"需要从多个 API 拿数据然后组装。后端把这种组装提前做了，前端只需要一次请求就能拿到完整数据。这就是 BFF（Backend For Frontend）模式的思路——后端按前端需要的数据形状返回，而不是按数据库表结构返回。

**情况三：一个端点操作多张表（事务性操作）。** 比如"创建订单"需要同时写 orders 表、order_items 表、扣减 products 表的库存——这些操作在一个事务里完成：

```python
@router.post("/orders")
async def create_order(req: CreateOrderRequest, db: AsyncSession = Depends(get_db)):
    # 一个请求涉及多表写入，必须在事务中完成
    async with db.begin():
        # 1. 查商品并锁行
        products = await db.execute(
            select(Product)
            .where(Product.id.in_(req.product_ids))
            .with_for_update()
        )
        products = products.scalars().all()

        # 2. 计算总价 + 扣库存
        total = Decimal("0")
        for p in products:
            if p.stock < req.quantities.get(p.id, 1):
                raise HTTPException(400, f"商品 {p.name} 库存不足")
            p.stock -= req.quantities.get(p.id, 1)
            total += p.price * req.quantities.get(p.id, 1)

        # 3. 创建订单
        order = Order(user_id=req.user_id, total=total, status="CREATED")
        db.add(order)
        await db.flush()

        # 4. 创建订单项
        for p in products:
            db.add(OrderItem(
                order_id=order.id,
                product_id=p.id,
                quantity=req.quantities.get(p.id, 1),
                unit_price=p.price,
            ))

    return {"order_id": order.id, "total": float(total)}
```

#### 7.3.3 分页、过滤、排序的数据库层面实现

前端常用的 Ant Design Table 或 Element Plus Table 组件需要分页、排序、过滤功能。前端开发者往往以为这些是组件自己实现的，但实际数据量大时，这些操作必须下沉到数据库层面执行，否则一次查出十万条数据传到前端会让浏览器崩溃。

```python
@router.get("/users")
async def list_users(
    page: int = 1,
    page_size: int = 20,
    keyword: str | None = None,
    status: str | None = None,
    sort_by: str = "id",
    sort_order: str = "asc",
    db: AsyncSession = Depends(get_db),
):
    # 构建动态查询条件
    stmt = select(User)

    # 过滤：相当于前端的 filter
    if keyword:
        stmt = stmt.where(
            or_(
                User.name.ilike(f"%{keyword}%"),
                User.email.ilike(f"%{keyword}%"),
            )
        )
    if status:
        stmt = stmt.where(User.status == status)

    # 排序：相当于前端的 sorter
    sort_column = getattr(User, sort_by, User.id)
    if sort_order == "desc":
        stmt = stmt.order_by(sort_column.desc())
    else:
        stmt = stmt.order_by(sort_column.asc())

    # 分页：相当于前端的 pagination
    total = await db.scalar(
        select(func.count()).select_from(stmt.subquery())
    )
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    users = result.scalars().all()

    return {
        "list": [serialize_user(u) for u in users],
        "total": total,
        "page": page,
        "page_size": page_size,
    }
```

> 前端类比：前端 Ant Table 的 `onChange(pagination, filters, sorter)` 回调里，你拿到分页/排序/过滤参数后发请求给后端。在 Node.js 后端，你需要把这些参数翻译成 SQL 的 LIMIT/OFFSET/ORDER BY/WHERE。上面这段 Python 代码做的就是这件事——把前端的分页/过滤/排序参数翻译成数据库查询。

#### 7.3.4 GraphQL 与数据库查询的 N+1 问题

GraphQL 是前端友好的查询语言——前端声明需要什么字段，后端按需返回。但 GraphQL 的灵活查询模式容易触发数据库的 N+1 问题：一个列表查询返回 N 条记录，然后对每条记录再查一次关联数据，总共 N+1 次查询。

```python
# N+1 问题示例（GraphQL resolver 中常见）
async def resolve_orders():
    # 第1次查询：查出 100 个订单
    orders = await db.execute(select(Order))
    orders = orders.scalars().all()

    result = []
    for order in orders:  # 循环 100 次
        # 每次循环都查一次用户 -> 100 次查询！总共 1 + 100 = 101 次
        user = await db.scalar(select(User).where(User.id == order.user_id))
        result.append({"order_id": order.id, "user_name": user.name})
    return result
```

解决方案是使用预加载（eager loading），一次性 JOIN 查出所有需要的数据：

```python
# 修复 N+1：使用 selectinload 一次性加载关联数据
async def resolve_orders_fixed():
    stmt = select(Order).options(selectinload(Order.user))
    result = await db.execute(stmt)
    orders = result.scalars().all()
    # 总共只查 2 次：1 次查订单，1 次查所有关联用户（IN 查询）
    return [{"order_id": o.id, "user_name": o.user.name} for o in orders]
```

关于 N+1 的详细性能分析和预加载策略，将在 8.4 节深入展开。

---

### 7.4 安全思维

#### 7.4.1 SQL 注入攻击原理与防御

SQL 注入是后端最经典的安全漏洞。前端开发者可能觉得"不就是把用户输入拼到 SQL 里吗"，但就是这么简单的操作，曾经导致了无数数据泄露事件。

**攻击原理：** 当你用字符串拼接方式构造 SQL，用户输入中包含 SQL 关键字时，攻击者可以"逃逸"出你的 SQL 语义，执行任意操作。

```python
# 危险代码！SQL 注入漏洞
def login_vulnerable(username: str, password: str):
    conn = get_connection()
    cursor = conn.cursor()

    # 字符串拼接构造 SQL -- 极其危险！
    sql = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    cursor.execute(sql)
    return cursor.fetchone()

# 攻击者输入：username = "admin' --", password = "anything"
# 实际执行的 SQL 变成：
# SELECT * FROM users WHERE username = 'admin' --' AND password = 'anything'
# "--" 是 SQL 注释，后面的密码校验被注释掉了！
# 结果：不需要密码就能登录 admin 账号

# 更严重的攻击：username = "'; DROP TABLE users; --"
# 实际执行的 SQL：
# SELECT * FROM users WHERE username = ''; DROP TABLE users; --' AND password = 'x'
# users 表被删除！
```

> 前端类比：这类似于前端的 XSS（跨站脚本注入）攻击。如果你用 `innerHTML = userInput` 直接渲染用户输入，攻击者在输入中注入 `<script>` 标签就能执行任意 JS。SQL 注入和 XSS 的本质是一样的：**把用户输入当代码执行**。前端的防御是 `textContent` 或 `escapeHtml`，后端的防御是**参数化查询**。

**防御方案：参数化查询。** 参数化查询的核心是"数据与代码分离"——SQL 模板和用户输入分开发送给数据库引擎，数据库保证用户输入永远被当作"数据"而不是"代码"：

```python
# 安全代码：参数化查询
def login_safe(username: str, password: str):
    conn = get_connection()
    cursor = conn.cursor()

    # 用占位符，用户输入作为参数传递
    sql = "SELECT * FROM users WHERE username = %s AND password = %s"
    cursor.execute(sql, (username, password))  # 参数化！
    return cursor.fetchone()

# 此时攻击者输入 "admin' --"，数据库引擎会把它当作
# 一个普通字符串去匹配 username 字段，而不是 SQL 语法
# 查询条件变成：username = "admin' --"（一个完整的字符串）
# 找不到匹配的用户，登录失败 -- 攻击被防御
```

SQLAlchemy 的查询 API 默认就是参数化的：

```python
# SQLAlchemy 2.0 安全查询
from sqlalchemy import select

# 安全：SQLAlchemy 自动参数化
stmt = select(User).where(User.username == username)
# 底层生成的 SQL：SELECT * FROM users WHERE username = ?
# ? 是参数占位符，username 值安全传入

# 安全：使用 .in_() 操作
stmt = select(User).where(User.id.in_(id_list))
# 底层：SELECT * FROM users WHERE id IN (?, ?, ?)
```

**绝对禁止的做法：** 用 f-string 或字符串拼接构造 SQL，然后把拼接好的字符串传给 `execute()`。即使用户输入看起来"无害"，也不能信任——攻击者总能找到你没想到的注入方式。

#### 7.4.2 最小权限原则：数据库用户权限设计

最小权限原则（Principle of Least Privilege）是安全设计的基石：一个组件只应该拥有完成其任务所需的最少权限，不多给一分。

在数据库层面，这意味着不同的应用组件应该使用不同的数据库用户，每个用户只有必要的权限：

```sql
-- 生产环境的数据库用户设计

-- 1. 应用读写用户（Web 应用使用）
CREATE USER app_readwrite PASSWORD 'strong_random_password_1';
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_readwrite;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_readwrite;
-- 注意：不给 CREATE / DROP / ALTER / TRUNCATE 权限
-- 应用运行时不需要改表结构

-- 2. 只读分析用户（BI/报表系统使用）
CREATE USER app_readonly PASSWORD 'strong_random_password_2';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_readonly;
-- 只能查，不能改

-- 3. 迁移工具用户（Alembic/Flyway 使用）
CREATE USER app_migrator PASSWORD 'strong_random_password_3';
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO app_migrator;
GRANT CREATE ON SCHEMA public TO app_migrator;
-- 迁移工具需要改表结构，但只通过 CI/CD 管道使用，不暴露给应用
```

> 前端类比：这类似于前端的权限控制。你的后台管理系统有"普通用户"和"管理员"角色，普通用户只能查看和编辑自己的数据，管理员可以管理所有用户。数据库用户权限设计也是同样的思路——按角色分配最小权限。

如果应用使用的数据库用户有 CREATE/DROP 权限，一旦应用存在 SQL 注入漏洞，攻击者就能 DROP TABLE 删除整张表。但如果应用用户只有 SELECT/INSERT/UPDATE/DELETE 权限，即使被注入，攻击者也无法删除表或改表结构，损失可以被控制在数据层面。

#### 7.4.3 敏感数据加密存储

数据库中存储的敏感信息需要加密或哈希处理。关键区分两个概念：

- **哈希（Hash）**：单向不可逆。用于密码存储——即使数据库泄露，攻击者也无法还原原始密码。
- **加密（Encryption）**：双向可逆。用于需要还原明文的数据——如手机号需要查询时要解密显示。

**密码哈希：**

```python
# 密码哈希：使用 bcrypt（行业标准）
import bcrypt

def hash_password(plain_password: str) -> str:
    """将明文密码哈希存储"""
    # bcrypt 自动加盐，无需手动处理
    salt = bcrypt.gensalt(rounds=12)  # rounds 越高越安全，但越慢
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )

# 使用
stored_hash = hash_password("MyPassword123")  # 存入数据库
is_valid = verify_password("MyPassword123", stored_hash)  # True
is_wrong = verify_password("wrong", stored_hash)  # False
```

> 前端类比：密码哈希就像前端的 `btoa()`/`atob()` 的区别——`btoa` 是编码（可逆），而密码哈希是单向的（不可逆）。你绝对不能"解码"出原始密码，验证密码的方式是把用户输入的密码同样哈希一遍，对比两个哈希值是否一致。这和前端比较 `password === storedPassword` 的逻辑类似，但安全性完全不同。

**手机号/身份证等可逆加密：**

```python
# 对称加密：用于需要还原明文的敏感数据
from cryptography.fernet import Fernet
import os

# 密钥应该从环境变量读取，不要硬编码
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")  # 32 字节 base64 编码密钥
cipher = Fernet(ENCRYPTION_KEY)

def encrypt_phone(phone: str) -> str:
    """加密手机号"""
    return cipher.encrypt(phone.encode("utf-8")).decode("utf-8")

def decrypt_phone(encrypted: str) -> str:
    """解密手机号"""
    return cipher.decrypt(encrypted.encode("utf-8")).decode("utf-8")

# 使用
encrypted_phone = encrypt_phone("13800138000")  # 存入数据库
plain_phone = decrypt_phone(encrypted_phone)    # 查询时解密
```

#### 7.4.4 数据脱敏：日志和返回前端的字段处理

即使敏感数据在数据库中加密存储了，在日志和 API 返回中也必须做脱敏处理。一个常见的错误是：在日志里打印了完整的用户信息（包括手机号、身份证），导致日志文件成为数据泄露源。

```python
# 数据脱敏工具函数
def mask_phone(phone: str) -> str:
    """手机号脱敏：138****0000"""
    if len(phone) < 7:
        return "***"
    return phone[:3] + "****" + phone[-4:]

def mask_email(email: str) -> str:
    """邮箱脱敏：z***@example.com"""
    name, domain = email.split("@")
    return name[0] + "***@" + domain

def mask_id_card(id_card: str) -> str:
    """身份证脱敏：110***********0000"""
    if len(id_card) < 8:
        return "***"
    return id_card[:3] + "*" * (len(id_card) - 7) + id_card[-4:]

# API 返回时脱敏
@router.get("/users/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(404, "用户不存在")

    # 返回前端的字段做脱敏处理
    return {
        "id": user.id,
        "name": user.name,
        "phone": mask_phone(user.phone),        # 138****0000
        "email": mask_email(user.email),        # z***@example.com
        "id_card": mask_id_card(user.id_card),  # 110***********0000
    }

# 日志记录时也要脱敏
import logging
logger = logging.getLogger(__name__)

@router.post("/users")
async def create_user(req: CreateUserRequest, db: AsyncSession = Depends(get_db)):
    # 错误：日志中打印了完整手机号
    # logger.info(f"创建用户: {req.phone}")

    # 正确：日志中脱敏
    logger.info(f"创建用户: phone={mask_phone(req.phone)}")
    # ...
```

#### 7.4.5 防止数据泄露：软删除的隐私问题与备份安全

**软删除的隐私问题：** 软删除（Soft Delete）通过给记录加 `deleted_at` 标记来"删除"数据，而不是物理删除。这在业务上方便（可以恢复、可以审计），但在隐私合规上是个陷阱——用户以为自己"注销了账号"，实际上数据还在数据库里，只是查询时过滤了。GDPR 等隐私法规要求用户有权要求"彻底删除"个人数据，这时你需要一个"硬删除"流程。

```python
# 软删除：标记 deleted_at（业务层面方便，但数据还在）
@router.delete("/users/{user_id}")
async def soft_delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if user:
        user.deleted_at = datetime.now()
        await db.commit()
    return {"message": "用户已注销"}

# GDPR 合规：用户要求彻底删除时执行硬删除
@router.delete("/users/{user_id}/permanent")
async def hard_delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    # 先删除关联数据
    await db.execute(delete(OrderItem).where(OrderItem.order_id.in_(
        select(Order.id).where(Order.user_id == user_id)
    )))
    await db.execute(delete(Order).where(Order.user_id == user_id))
    # 再删除用户
    await db.execute(delete(User).where(User.id == user_id))
    await db.commit()
    logger.info(f"用户 {user_id} 数据已永久删除（GDPR 合规）")
    return {"message": "用户数据已永久删除"}
```

**备份安全：** 数据库备份文件包含了所有数据，如果备份文件泄露，即使生产数据库做了加密和权限控制，也等于零防护。备份文件必须加密存储，且备份介质要有严格的访问控制。

---

### 7.5 性能思维

#### 7.5.1 前端性能 vs 后端性能

前端和后端的性能关注点完全不同。理解这个差异是后端思维转换的关键。

| 维度 | 前端性能 | 后端性能 |
|---|---|---|
| 核心指标 | 首屏加载时间（FCP/LCP）、交互响应速度（FID）、渲染帧率（FPS） | API 响应时间（P99/P95）、QPS（每秒查询数）、数据库连接数 |
| 瓶颈所在 | 网络下载、JS 执行、DOM 渲染、包体积 | 数据库查询、连接数、锁等待、磁盘 IO |
| 优化手段 | 代码分割、懒加载、CDN、Tree-shaking、虚拟列表 | 加索引、优化 SQL、连接池、缓存、读写分离 |
| 用户体验 | 单个用户感知：慢就是慢 | 所有用户共享：一个慢查询拖垮整个服务 |
| 扩展方式 | CDN 分发静态资源 | 水平扩展服务实例 + 数据库分库分表 |

> 前端类比：前端性能优化你关心的是"用户的浏览器要多久才能渲染完页面"——这是单用户的体验。后端性能优化你关心的是"服务器在高并发下能不能扛住"——这是多用户共享的资源问题。前端像优化一辆车的加速性能（单个用户体验），后端像优化一条高速公路的通行能力（整体吞吐量）。

后端性能问题的可怕之处在于"连锁反应"：一个慢查询会导致数据库连接被占满 -> 连接池耗尽 -> 新请求排队等待连接 -> 请求超时 -> 前端报 502 -> 整个服务不可用。这种"雪崩效应"在前端几乎不存在（一个页面慢不会影响其他用户的页面），但在后端是常态。

#### 7.5.2 慢查询日志与分析

慢查询是后端性能问题的头号杀手。定位慢查询的标准流程是：开启慢查询日志 -> 找到慢 SQL -> 用 EXPLAIN 分析执行计划 -> 优化（加索引/改 SQL/改表结构）。

**MySQL 慢查询日志：**

```sql
-- 查看慢查询日志是否开启
SHOW VARIABLES LIKE 'slow_query_log%';
SHOW VARIABLES LIKE 'long_query_time';

-- 开启慢查询日志
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1;  -- 超过 1 秒的查询记录

-- 查看慢查询日志文件位置
SHOW VARIABLES LIKE 'slow_query_log_file';
```

**EXPLAIN 分析执行计划：**

```sql
-- 在 SQL 前加 EXPLAIN，查看数据库怎么执行这条查询
EXPLAIN SELECT * FROM orders WHERE user_id = 1;

-- PostgreSQL 更详细的分析（实际执行并统计耗时）
EXPLAIN ANALYZE SELECT * FROM orders WHERE user_id = 1;
```

EXPLAIN 输出的关键字段：

| 字段 | 含义 | 优化信号 |
|---|---|---|
| type（MySQL） | 访问类型 | ALL = 全表扫描（危险！）；ref/eq_ref = 索引查找（好） |
| key | 使用的索引 | NULL 表示没用索引，需要加 |
| rows | 预估扫描行数 | 越小越好，百万级说明没走索引 |
| Extra | 额外信息 | Using filesort（需要优化）、Using temporary（需要优化） |
| cost（PostgreSQL） | 查询成本 | 越低越好 |

> 前端类比：EXPLAIN 就像 Chrome DevTools 的 Performance 面板——你不用猜哪段代码慢，工具直接告诉你哪一步花了多少时间。EXPLAIN ANALYZE 更进一步，它会真正执行查询并记录每一步的实际耗时，类似于 DevTools 里带时间轴的火焰图。

#### 7.5.3 数据库连接池：为什么不能每次请求新建连接

前端开发者可能不理解"连接池"的概念——前端每次 `fetch` 请求都是新建一个 HTTP 连接（虽然 HTTP/2 有多路复用），为什么后端不能每次请求新建一个数据库连接？

原因在于数据库连接的**创建成本极高**。一个 MySQL 连接的建立过程包括：TCP 三次握手 -> 认证握手 -> 权限校验 -> 初始化 session 变量，整个过程通常需要 10-50ms。如果你的 API 每秒处理 1000 个请求，每请求新建+关闭连接就要消耗 10-50 秒的 CPU 时间，这是不可接受的。

```python
# 错误做法：每次请求新建连接
def get_user_bad(user_id: int):
    conn = pymysql.connect(...)  # 新建连接，10-50ms
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    result = cursor.fetchone()
    conn.close()  # 关闭连接
    return result
    # 1000 QPS 时，光是建连就要消耗 10-50 秒 CPU 时间

# 正确做法：使用连接池
from sqlalchemy.ext.asyncio import create_async_engine

# 创建连接池（应用启动时创建一次）
engine = create_async_engine(
    "mysql+aiomysql://user:pass@localhost:3306/mydb",
    pool_size=20,          # 常驻连接数
    max_overflow=10,       # 突发时可额外创建的连接数
    pool_timeout=30,       # 等待连接的超时时间（秒）
    pool_recycle=3600,     # 连接最大存活时间（秒），防止数据库主动断开
    pool_pre_ping=True,    # 使用连接前先 ping 一下，防止拿到已断开的连接
)

# 每次请求从池中借连接，用完归还
async def get_user_good(user_id: int):
    async with engine.connect() as conn:  # 从池中借连接，0ms
        result = await conn.execute(
            text("SELECT * FROM users WHERE id = :uid"),
            {"uid": user_id},
        )
        return result.fetchone()
    # 连接自动归还到池中，不关闭
```

> 前端类比：连接池就像前端的 HTTP Keep-Alive 或连接复用。但前端的 HTTP 连接创建成本较低，所以浏览器通常不显式管理"连接池"。数据库连接创建成本极高（涉及认证、权限校验、session 初始化），所以必须复用。类比一下：如果每次 `fetch` 都要先建立 TLS 握手（HTTPS 首次连接约 100-300ms），你会希望复用这个连接。数据库连接的建连成本比 TLS 握手还高，所以连接池是刚需。

#### 7.5.4 缓存层：Redis 作为数据库前置缓存

当数据库成为性能瓶颈时，缓存是第一道防线。Redis 作为内存数据库，读写速度比 MySQL/PostgreSQL 快 1-2 个数量级（微秒 vs 毫秒），适合缓存热点数据。

最常用的缓存策略是 Cache-Aside（旁路缓存）：

```
读流程：
  1. 先查 Redis 缓存
  2. 缓存命中 -> 直接返回
  3. 缓存未命中 -> 查数据库 -> 写入缓存 -> 返回

写流程：
  1. 更新数据库
  2. 删除缓存（不是更新缓存，避免并发不一致）
```

```python
import redis.asyncio as redis
import json

redis_client = redis.Redis(host="localhost", port=6379, db=0)

async def get_user_cached(user_id: int, db: AsyncSession) -> dict:
    # 1. 先查缓存
    cache_key = f"user:{user_id}"
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    # 2. 缓存未命中，查数据库
    user = await db.get(User, user_id)
    if not user:
        return None

    user_data = {"id": user.id, "name": user.name, "email": user.email}

    # 3. 写入缓存，设置过期时间（防止数据永久不一致）
    await redis_client.setex(cache_key, 300, json.dumps(user_data))  # 5 分钟过期

    return user_data

async def update_user_cached(user_id: int, name: str, db: AsyncSession):
    # 1. 更新数据库
    user = await db.get(User, user_id)
    user.name = name
    await db.commit()

    # 2. 删除缓存（下次读取时会重新加载最新数据）
    await redis_client.delete(f"user:{user_id}")
```

缓存的使用也有代价：缓存一致性（数据库改了缓存没同步）、缓存穿透（查询不存在的数据绕过缓存打穿数据库）、缓存雪崩（大量缓存同时过期导致数据库瞬时压力）。这些问题的解决方案将在第九章 Redis 篇详细讨论。

---

### 7.6 扩展性思维

#### 7.6.1 垂直拆分 vs 水平拆分

当单台数据库扛不住业务量时，需要考虑拆分。拆分有两个维度：垂直（按字段/业务拆）和水平（按行/数据拆）。

**垂直拆分：** 把一张有很多字段的宽表，按业务域拆成多张窄表，或者把不同业务模块拆到不同的数据库实例。

```
拆分前（一个数据库实例）：
  users 表（50 个字段，含基本信息、支付信息、社交信息、偏好设置...）
  products 表
  orders 表
  logs 表（写入量大）

垂直拆分后（按业务拆到不同实例）：
  用户数据库实例：users 表（基本信息 + 社交 + 偏好）
  支付数据库实例：payments 表 + payment_logs 表
  订单数据库实例：orders 表 + order_items 表
  日志数据库实例：logs 表（单独实例，避免影响业务）
```

> 前端类比：垂直拆分就像前端的代码分割——你把一个巨大的 `monolith.ts` 拆成多个模块文件，按业务域组织。前端的"按路由懒加载"也是一种垂直拆分：不同页面加载不同代码，避免单个 bundle 过大。

**水平拆分：** 把同一张表的数据按某种规则分散到多个数据库实例（分库）或同一实例的多张表（分表）。

```
拆分前：
  orders 表（1 亿行，查询越来越慢）

水平分表后（按 user_id 取模拆成 4 张表）：
  orders_0 表：user_id % 4 == 0 的订单
  orders_1 表：user_id % 4 == 1 的订单
  orders_2 表：user_id % 4 == 2 的订单
  orders_3 表：user_id % 4 == 3 的订单
  每张表约 2500 万行，查询性能显著提升
```

> 前端类比：水平拆分就像前端的虚拟列表（react-window/virtualized）——你不会一次渲染 10000 个 DOM 节点，而是只渲染可视区域的 50 个。水平分表也是类似的思路：不把 1 亿行放一张表，而是分成 4 张表每张 2500 万行。

#### 7.6.2 读写分离：主从复制架构

大多数业务系统中读写比例严重不均衡——读多写少（比如电商：浏览商品 >> 下单）。读写分离的核心思路是：写操作走主库（保证数据一致性），读操作走从库（分担主库压力）。

```
架构：
  主库（Master）：处理所有写操作（INSERT/UPDATE/DELETE）
  从库1（Slave1）：从主库复制数据，处理读操作
  从库2（Slave2）：从主库复制数据，处理读操作
  从库3（Slave3）：从主库复制数据，处理读操作

数据同步：主库 -> binlog -> 从库 replay -> 数据一致
```

```python
# 读写分离的 SQLAlchemy 实现
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

# 主库引擎（写操作）
master_engine = create_async_engine(
    "mysql+aiomysql://app:pass@master-host:3306/mydb",
    pool_size=10,
)

# 从库引擎（读操作）
slave_engine = create_async_engine(
    "mysql+aiomysql://app:pass@slave-host:3306/mydb",
    pool_size=30,  # 从库连接池更大，因为读请求多
)

# 写操作用主库 session
async def write_user(user_data: dict):
    async with AsyncSession(master_engine) as session:
        user = User(**user_data)
        session.add(user)
        await session.commit()

# 读操作用从库 session
async def read_user(user_id: int):
    async with AsyncSession(slave_engine) as session:
        return await session.get(User, user_id)
```

读写分离的关键挑战是**复制延迟**：主库写入后，数据复制到从库有延迟（通常毫秒级，但网络异常时可能秒级甚至分钟级）。用户刚提交了订单（写主库），马上刷新"我的订单"页（读从库），如果复制还没完成，用户会看到"订单不存在"——这就是"写后读不一致"问题。解决方案是对"写后立即读"的场景路由到主库。

#### 7.6.3 分库分表策略

分库分表的拆分策略有三种主要模式：

**按业务拆（垂直分库）：** 用户库、订单库、商品库分别独立部署。适合业务边界清晰的大型系统。

**按用户/ID 拆（水平分库）：** 按 user_id 取模或范围分片。适合单表数据量过大。

```
按 user_id 取模分库（4 个库）：
  DB_0: user_id % 4 == 0 的所有数据
  DB_1: user_id % 4 == 1
  DB_2: user_id % 4 == 2
  DB_3: user_id % 4 == 3

按 user_id 范围分库：
  DB_0: user_id 1 ~ 250万
  DB_1: user_id 250万 ~ 500万
  DB_2: user_id 500万 ~ 750万
  DB_3: user_id 750万 ~ 1000万
```

**按时间拆（水平分表）：** 按月/按天分表。适合日志、流水、订单等时间序列数据。

```
按月分表：
  orders_202401 表：2024年1月的订单
  orders_202402 表：2024年2月的订单
  orders_202403 表：2024年3月的订单
  ...
```

> 前端类比：按时间分表就像前端的"按日期分文件"——比如你把每天的日志写到 `log-2024-01-15.json` 而不是全部堆在一个 `log.json` 里。查询某天的日志时只加载对应文件，不用遍历整个历史。

#### 7.6.4 分库分表后的全局唯一 ID

分库分表后，自增主键（AUTO_INCREMENT）不再可用——多个表各自自增会产生重复 ID。需要全局唯一 ID 生成方案：

**方案一：UUID** -- 简单但太长（36 字符），作为主键影响索引性能。

**方案二：数据库自增表** -- 用一张独立的表生成 ID，性能瓶颈集中在这张表上。

**方案三：雪花算法（Snowflake）** -- 最常用的方案，生成 64 位整数 ID，包含时间戳 + 机器 ID + 序列号：

```
雪花 ID 结构（64 位）：
  1 bit 符号位（固定 0）
  41 bit 时间戳（毫秒级，约 69 年）
  10 bit 机器 ID（最多 1024 台机器）
  12 bit 序列号（每毫秒最多 4096 个 ID）

  示例：1759286423105123456（一个 19 位数字）
```

```python
# Python 雪花算法 ID 生成器（简化版）
import time

class SnowflakeGenerator:
    def __init__(self, machine_id: int):
        self.machine_id = machine_id & 0x3FF  # 10 bit 机器 ID
        self.sequence = 0
        self.last_timestamp = -1

    def generate_id(self) -> int:
        now = int(time.time() * 1000)
        if now == self.last_timestamp:
            self.sequence = (self.sequence + 1) & 0xFFF  # 12 bit 序列号
            if self.sequence == 0:
                while now <= self.last_timestamp:
                    now = int(time.time() * 1000)
        else:
            self.sequence = 0
        self.last_timestamp = now

        return ((now << 22) | (self.machine_id << 12) | self.sequence)

# 使用
gen = SnowflakeGenerator(machine_id=1)
order_id = gen.generate_id()  # 1759286423105123456
```

#### 7.6.5 数据库中间件与代理层

分库分表后，应用代码需要知道数据在哪个库/哪张表，这会让业务代码充满路由逻辑。数据库中间件的作用是在应用和数据库之间加一层代理，让应用像操作单库一样操作分库分表。

- **ShardingSphere（Apache）**：支持分库分表、读写分离、分布式事务，支持 Java/Python 等多语言。
- **ProxySQL**：MySQL 代理层，支持读写分离、连接池、查询路由。
- **PgBouncer**：PostgreSQL 连接池中间件，降低连接数开销。
- **Vitess**：Google 开源的 MySQL 集群方案，支持分片和自动故障转移。

> 前端类比：数据库中间件就像前端的 API Gateway 或 BFF 层——你的代码不直接调用多个后端服务，而是通过 Gateway 统一入口。Gateway 负责路由请求到正确的后端服务，应用层不需要知道服务部署在哪。数据库中间件做的也是这件事——应用发 SQL 给中间件，中间件路由到正确的分片。

---

### 7.7 后端开发者的数据库日常

#### 7.7.1 数据库迁移管理

前端开发者习惯用 Git 管理代码变更，但数据库的表结构变更（加字段、改类型、加索引）如何管理？答案是**数据库迁移工具**。

迁移工具的核心思想是：**把数据库的每一次结构变更记录为版本化的脚本文件，纳入 Git 管理**。这样数据库的 schema 变更和代码变更是同步的、可追溯的、可回滚的。

主流迁移工具：

| 工具 | 适用场景 | 语言生态 |
|---|---|---|
| Alembic | SQLAlchemy 项目的首选 | Python |
| Flyway | Java 生态为主，也支持通用 SQL 脚本 | Java/通用 |
| Liquibase | 企业级，支持 XML/YAML/JSON 格式变更日志 | Java/通用 |
| Django Migrations | Django 内置迁移系统 | Python/Django |

> 前端类比：数据库迁移就像前端的"版本化 schema"。如果你用过 GraphQL 的 schema 版本管理，或者 Prisma 的 `prisma migrate` 命令，概念完全一样——把结构变更变成可追溯的版本文件。Alembic 之于 SQLAlchemy，就像 Prisma Migrate 之于 Prisma。

Alembic 的基本工作流：

```bash
# 1. 初始化 Alembic（项目根目录执行）
alembic init alembic

# 2. 修改 alembic.ini 配置数据库连接
# 修改 alembic/env.py 关联 SQLAlchemy 模型

# 3. 自动检测模型变更，生成迁移脚本
alembic revision --autogenerate -m "add phone field to users"

# 4. 执行迁移（应用变更到数据库）
alembic upgrade head

# 5. 回滚上一次迁移
alembic downgrade -1

# 6. 查看迁移历史
alembic history
```

生成的迁移脚本示例：

```python
# alembic/versions/a1b2c3d4_add_phone_field_to_users.py
"""add phone field to users

Revision ID: a1b2c3d4
Revises: 9z8y7x6w
Create Date: 2024-01-15 10:00:00
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'a1b2c3d4'
down_revision = '9z8y7x6w'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('users', sa.Column('phone', sa.String(20), nullable=True))
    # 创建索引
    op.create_index('ix_users_phone', 'users', ['phone'])

def downgrade():
    op.drop_index('ix_users_phone', table_name='users')
    op.drop_column('users', 'phone')
```

#### 7.7.2 为什么不能直接改生产数据库

后端新手最常见的危险操作是：直接连接生产数据库执行 `ALTER TABLE` 或 `DELETE`。这可能导致以下灾难：

**1. 长时间锁表。** 在 MySQL 中，`ALTER TABLE` 可能锁住整张表，期间所有读写都被阻塞。一张百万行表的 ALTER 可能执行数分钟，导致服务不可用。

**2. 不可回滚。** 手动执行的 DDL 没有版本记录，如果改错了，你可能不记得改了什么、怎么回滚。

**3. 团队不同步。** 你手动加了字段，但其他开发者的代码不知道这个字段，部署后可能报错。

**4. 审计缺失。** 手动操作数据库不经过任何审批流程，出了问题无法追溯。

正确做法是通过迁移脚本，经过代码审查和 CI/CD 管道执行：

```
开发流程：
  1. 本地修改 SQLAlchemy 模型（加字段）
  2. alembic revision --autogenerate 生成迁移脚本
  3. 本地 alembic upgrade head 测试
  4. Git commit 迁移脚本
  5. PR Review（同事审查迁移脚本）
  6. 合并到 main 分支
  7. CI/CD 自动执行 alembic upgrade（或手动执行）
  8. 生产数据库变更完成，有记录可追溯
```

#### 7.7.3 数据备份与恢复策略

数据是后端系统最有价值的资产。备份策略的设计需要回答三个问题：备份什么？多久备份一次？怎么恢复？

**备份类型：**

| 类型 | 说明 | 恢复速度 | 数据完整性 |
|---|---|---|---|
| 全量备份 | 备份整个数据库 | 快 | 完整但可能不是最新 |
| 增量备份 | 备份自上次备份以来的变更 | 中 | 需要全量+增量组合恢复 |
| 日志备份 | 备份 binlog/WAL 日志 | 慢 | 可恢复到任意时间点（PITR） |

**MySQL 备份：**

```bash
# 全量备份（mysqldump）
mysqldump -u root -p --single-transaction --routines --triggers mydb > backup_20240115.sql

# 恢复
mysql -u root -p mydb < backup_20240115.sql

# 使用 binlog 做时间点恢复（PITR）
# 1. 恢复全量备份
mysql -u root -p mydb < backup_20240115.sql
# 2. 重放 binlog 到指定时间点
mysqlbinlog --start-datetime="2024-01-15 10:00:00" ^
            --stop-datetime="2024-01-15 14:00:00" ^
            mysql-bin.000123 | mysql -u root -p mydb
```

**PostgreSQL 备份：**

```bash
# 全量备份
pg_dump -U postgres -F c mydb > backup_20240115.dump

# 恢复
pg_restore -U postgres -d mydb -c backup_20240115.dump

# 使用 WAL 做时间点恢复（PITR）
# 配置 archive_mode=on, archive_command='cp %p /backup/wal/%f'
# 恢复时：恢复基础备份 -> 重放 WAL 日志到目标时间点
```

**备份策略建议：**
- 每日全量备份 + 每小时增量/binlog 备份
- 备份文件加密存储，异地备份（防机房故障）
- 定期做恢复演练（只有成功恢复的备份才是有效备份）

#### 7.7.4 生产环境数据库监控指标

后端工程师需要关注的生产数据库监控指标：

| 指标 | 正常范围 | 异常信号 | 工具 |
|---|---|---|---|
| 连接数 | < max_connections 的 80% | 接近上限 -> 连接泄露 | SHOW STATUS LIKE 'Threads_connected' |
| QPS（每秒查询数） | 取决于业务基线 | 突然飙升 -> 可能被攻击或 BUG | SHOW STATUS LIKE 'Questions' |
| 慢查询数 | < 10/分钟 | 大量慢查询 -> 索引失效或数据量暴增 | slow_query_log |
| 锁等待 | < 1 秒 | 长时间锁等待 -> 死锁或长事务 | SHOW ENGINE INNODB STATUS |
| 缓冲池命中率 | > 95% | 低于 90% -> 内存不足或查询低效 | SHOW STATUS LIKE 'Innodb_buffer_pool_read%' |
| 复制延迟 | < 1 秒 | 秒级延迟 -> 从库数据过期 | SHOW SLAVE STATUS (Seconds_Behind_Master) |

```python
# 简单的数据库健康检查脚本
import pymysql

def check_mysql_health():
    conn = pymysql.connect(host="localhost", user="monitor", password="xxx", database="mydb")
    cursor = conn.cursor()

    # 检查连接数
    cursor.execute("SHOW STATUS LIKE 'Threads_connected'")
    threads_connected = int(cursor.fetchone()[1])

    # 检查最大连接数
    cursor.execute("SHOW VARIABLES LIKE 'max_connections'")
    max_connections = int(cursor.fetchone()[1])

    connection_usage = threads_connected / max_connections * 100
    if connection_usage > 80:
        alert(f"连接数告警: {threads_connected}/{max_connections} ({connection_usage:.1f}%)")

    # 检查慢查询
    cursor.execute("SHOW STATUS LIKE 'Slow_queries'")
    slow_queries = int(cursor.fetchone()[1])
    if slow_queries > 100:
        alert(f"慢查询告警: {slow_queries} 条")

    cursor.close()
    conn.close()

def alert(message: str):
    # 发送告警（钉钉/飞书/邮件）
    print(f"[ALERT] {message}")
```

> 前端类比：数据库监控就像前端的性能监控（Sentry / DataDog / 阿里云 ARMS）。前端你监控 JS 错误率、白屏率、接口响应时间；后端你监控数据库连接数、慢查询数、锁等待时间。两者都是"先有指标，才能优化"——你不能优化你无法度量的东西。

---
# 第八章 Python 数据库操作实战

> 前端转后端 Python 开发者的实战指南。本章假设你已经学完前 7 章（数据库基础、MySQL、PostgreSQL、表设计、SQL 进阶、事务与锁、后端思维），掌握了 SQL 语法和数据库设计原理，现在需要把这些知识用 Python 代码落地。
>
> 本章所有代码在 Windows 10/11 + Python 3.11+ 环境下编写，遵循 PEP 8 规范，不使用 emoji 字符（避免 GBK 编码报错）。数据库连接信息请根据你的实际环境替换。

---

## 8.1 Python 连接 MySQL

Python 连接 MySQL 的驱动有很多，选择哪个驱动取决于你的项目需求。下面逐一讲解最常用的四种方案。

### 8.1.1 pymysql：纯 Python 驱动，同步

pymysql 是最常用的 MySQL 驱动之一，它是纯 Python 实现，不需要编译 C 扩展，安装简单，在 Windows 上零障碍。对于大多数中小型项目，pymysql 完全够用。

**安装：**

```bash
pip install pymysql
```

**连接与 CRUD 完整示例：**

```python
# -*- coding: utf-8 -*-
"""
pymysql 完整 CRUD 示例
数据库准备脚本（先在 MySQL 中执行）:
    CREATE DATABASE IF NOT EXISTS demo_db
        DEFAULT CHARACTER SET utf8mb4
        DEFAULT COLLATE utf8mb4_unicode_ci;

    USE demo_db;

    CREATE TABLE IF NOT EXISTS users (
        id          INT AUTO_INCREMENT PRIMARY KEY,
        username    VARCHAR(50)  NOT NULL UNIQUE,
        email       VARCHAR(100) NOT NULL,
        age         INT,
        created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""

import pymysql
from pymysql.cursors import DictCursor


def get_connection():
    """创建并返回一个 MySQL 连接"""
    return pymysql.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="your_password",
        database="demo_db",
        charset="utf8mb4",
        cursorclass=DictCursor,   # 返回字典形式的结果，方便按列名取值
    )


def create_user(username: str, email: str, age: int):
    """插入一条用户记录"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO users (username, email, age)
                VALUES (%s, %s, %s)
            """
            cursor.execute(sql, (username, email, age))
        conn.commit()
        print(f"[OK] 已创建用户: {username}, 受影响行数: {cursor.rowcount}")
        return cursor.lastrowid
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] 创建用户失败: {e}")
        raise
    finally:
        conn.close()


def get_user_by_id(user_id: int):
    """根据 ID 查询单个用户"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT id, username, email, age, created_at FROM users WHERE id = %s"
            cursor.execute(sql, (user_id,))
            return cursor.fetchone()
    finally:
        conn.close()


def list_users(limit: int = 10, offset: int = 0):
    """查询用户列表（分页）"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT id, username, email, age, created_at
                FROM users
                ORDER BY id DESC
                LIMIT %s OFFSET %s
            """
            cursor.execute(sql, (limit, offset))
            return cursor.fetchall()
    finally:
        conn.close()


def update_user_age(user_id: int, new_age: int):
    """更新用户年龄"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = "UPDATE users SET age = %s WHERE id = %s"
            cursor.execute(sql, (new_age, user_id))
        conn.commit()
        print(f"[OK] 已更新用户 {user_id} 的年龄为 {new_age}, 受影响行数: {cursor.rowcount}")
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] 更新失败: {e}")
        raise
    finally:
        conn.close()


def delete_user(user_id: int):
    """删除用户"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = "DELETE FROM users WHERE id = %s"
            cursor.execute(sql, (user_id,))
        conn.commit()
        print(f"[OK] 已删除用户 {user_id}, 受影响行数: {cursor.rowcount}")
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] 删除失败: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    # 完整的增删改查演示
    new_id = create_user("zhangsan", "zhangsan@example.com", 28)
    user = get_user_by_id(new_id)
    print(f"查询结果: {user}")

    users = list_users(limit=5)
    print(f"用户列表: {users}")

    update_user_age(new_id, 29)
    print(f"更新后: {get_user_by_id(new_id)}")

    delete_user(new_id)
    print(f"删除后查询: {get_user_by_id(new_id)}")
```

**关键要点说明：**

1. **参数化查询**：pymysql 使用 `%s` 作为占位符，不要用字符串拼接 SQL，否则会有 SQL 注入风险。
2. **事务管理**：pymysql 默认开启事务，执行写操作后必须调用 `conn.commit()`。如果出错，调用 `conn.rollback()` 回滚。
3. **游标类型**：`DictCursor` 让查询结果返回字典，按列名取值更直观。默认的 `Cursor` 返回元组。
4. **资源释放**：`finally` 块中关闭连接，防止连接泄漏。在生产环境中应该使用连接池。

### 8.1.2 mysqlclient：C 扩展驱动，高性能

mysqlclient（即 MySQL-python 的 Fork 版本）是 C 扩展实现的驱动，性能比 pymysql 高 2-5 倍，API 与 pymysql 高度兼容。但安装时需要 C 编译器，在 Windows 上可能需要安装预编译的 wheel 包。

**安装（Windows）：**

```bash
# 推荐使用预编译 wheel，避免本地编译
pip install mysqlclient
```

如果安装失败，可以去 [https://www.lfd.uci.edu/~gohlke/pythonlibs/](https://www.lfd.uci.edu/~gohlke/pythonlibs/) 下载对应 Python 版本的 wheel 文件，然后用 `pip install 文件名.whl` 安装。

**使用方式（与 pymysql 几乎一致）：**

```python
# -*- coding: utf-8 -*-
"""
mysqlclient 使用示例
mysqlclient 的 API 与 pymysql 几乎一致，可以直接替换 import
"""
import MySQLdb  # mysqlclient 的导入名是 MySQLdb
from MySQLdb.cursors import DictCursor


def get_connection():
    return MySQLdb.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        passwd="your_password",   # 注意: mysqlclient 用 passwd 而非 password
        db="demo_db",             # 注意: mysqlclient 用 db 而非 database
        charset="utf8mb4",
        cursorclass=DictCursor,
    )


def batch_insert(users: list[tuple]):
    """批量插入，演示 mysqlclient 的性能优势"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO users (username, email, age) VALUES (%s, %s, %s)"
            # executemany 批量执行，性能远超循环单条插入
            cursor.executemany(sql, users)
        conn.commit()
        print(f"[OK] 批量插入 {cursor.rowcount} 条记录")
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] 批量插入失败: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    data = [
        ("user_001", "u001@example.com", 20),
        ("user_002", "u002@example.com", 21),
        ("user_003", "u003@example.com", 22),
    ]
    batch_insert(data)
```

**pymysql 与 mysqlclient 对比：**

| 对比维度 | pymysql | mysqlclient |
|---------|---------|-------------|
| 实现语言 | 纯 Python | C 扩展 |
| 安装难度 | 极简（pip install 即可） | 需 C 编译器或预编译 wheel |
| 性能 | 基准（较慢） | 快 2-5 倍 |
| API 兼容性 | 标准 | 与 pymysql 高度兼容 |
| Windows 友好度 | 优秀 | 需注意 wheel 版本匹配 |
| 适用场景 | 开发环境、中小项目 | 生产环境、高并发场景 |

### 8.1.3 aiomysql / asyncmy：异步驱动

在现代异步框架（FastAPI、aiohttp、Sanic）中，数据库操作也需要异步化，否则数据库 I/O 会阻塞事件循环。aiomysql 是基于 pymysql 的异步驱动，asyncmy 是基于 mysqlclient 的异步驱动（性能更好）。

**安装：**

```bash
pip install aiomysql
# 或者高性能版本:
pip install asyncmy
```

**aiomysql 异步 CRUD 完整示例：**

```python
# -*- coding: utf-8 -*-
"""
aiomysql 异步 CRUD 示例
需要 Python 3.8+
"""
import asyncio
import aiomysql


async def create_pool():
    """创建异步连接池"""
    pool = await aiomysql.create_pool(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="your_password",
        db="demo_db",
        charset="utf8mb4",
        minsize=2,     # 连接池最小连接数
        maxsize=10,    # 连接池最大连接数
        pool_recycle=3600,  # 连接回收时间（秒），防止 MySQL 8 小时超时断开
    )
    return pool


async def create_user(pool, username: str, email: str, age: int):
    """异步插入用户"""
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            sql = "INSERT INTO users (username, email, age) VALUES (%s, %s, %s)"
            await cursor.execute(sql, (username, email, age))
            await conn.commit()
            return cursor.lastrowid


async def get_user_by_id(pool, user_id: int):
    """异步查询单个用户"""
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            sql = "SELECT * FROM users WHERE id = %s"
            await cursor.execute(sql, (user_id,))
            return await cursor.fetchone()


async def list_users(pool, limit: int = 10):
    """异步查询用户列表"""
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            sql = "SELECT * FROM users ORDER BY id DESC LIMIT %s"
            await cursor.execute(sql, (limit,))
            return await cursor.fetchall()


async def update_user_age(pool, user_id: int, new_age: int):
    """异步更新用户年龄"""
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            sql = "UPDATE users SET age = %s WHERE id = %s"
            await cursor.execute(sql, (new_age, user_id))
            await conn.commit()
            return cursor.rowcount


async def delete_user(pool, user_id: int):
    """异步删除用户"""
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            sql = "DELETE FROM users WHERE id = %s"
            await cursor.execute(sql, (user_id,))
            await conn.commit()
            return cursor.rowcount


async def main():
    pool = await create_pool()
    try:
        # 异步并发执行多个操作
        new_id = await create_user(pool, "lisi", "lisi@example.com", 30)
        print(f"[OK] 创建用户 ID: {new_id}")

        user = await get_user_by_id(pool, new_id)
        print(f"查询结果: {user}")

        users = await list_users(pool, limit=5)
        print(f"用户列表: {users}")

        await update_user_age(pool, new_id, 31)
        print(f"更新后: {await get_user_by_id(pool, new_id)}")

        await delete_user(pool, new_id)
        print(f"删除后: {await get_user_by_id(pool, new_id)}")
    finally:
        pool.close()
        await pool.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
```

### 8.1.4 连接池的使用

每次创建数据库连接都需要 TCP 三次握手、认证、分配资源，开销很大。连接池预先创建一批连接，复用它们，能显著提升性能。

**方案一：DBUtils（配合 pymysql / mysqlclient）**

```python
# -*- coding: utf-8 -*-
"""
DBUtils 连接池 + pymysql 示例
安装: pip install dbutils pymysql
"""
import pymysql
from dbutils.pooled_db import PooledDB
from pymysql.cursors import DictCursor


# 创建连接池（全局只需创建一次）
pool = PooledDB(
    creator=pymysql,        # 使用的驱动
    maxconnections=20,      # 最大连接数
    mincached=2,            # 初始空闲连接数
    maxcached=5,            # 最大空闲连接数
    maxshared=3,            # 最大共享连接数（pymysql 不支持，设为 0 或 3）
    host="127.0.0.1",
    port=3306,
    user="root",
    password="your_password",
    database="demo_db",
    charset="utf8mb4",
    cursorclass=DictCursor,
    blocking=True,          # 连接池满时阻塞等待，而非报错
)


def get_user_by_id(user_id: int):
    """从连接池获取连接，执行查询后归还"""
    conn = pool.connection()  # 从池中借出一个连接
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            return cursor.fetchone()
    finally:
        conn.close()  # close() 不是真正关闭，而是归还到连接池


if __name__ == "__main__":
    user = get_user_by_id(1)
    print(f"查询结果: {user}")
```

**方案二：SQLAlchemy 内置连接池（推荐）**

SQLAlchemy 自带高质量的连接池实现，后面 8.3 节会详细讲解。这里先展示用 SQLAlchemy Core 直接操作连接池的方式：

```python
# -*- coding: utf-8 -*-
"""
SQLAlchemy Core 连接池示例（直接执行原生 SQL）
安装: pip install sqlalchemy pymysql
"""
from sqlalchemy import create_engine, text


# create_engine 自动管理连接池
# 连接字符串格式: mysql+pymysql://user:password@host:port/database
engine = create_engine(
    "mysql+pymysql://root:your_password@127.0.0.1:3306/demo_db?charset=utf8mb4",
    pool_size=10,          # 连接池大小
    max_overflow=20,       # 允许超过 pool_size 的额外连接数
    pool_timeout=30,      # 获取连接超时时间（秒）
    pool_recycle=3600,    # 连接回收周期（秒）
    pool_pre_ping=True,   # 使用前检查连接是否存活，防止"MySQL has gone away"
    echo=False,           # 设为 True 可打印执行的 SQL，调试用
)


def get_user_by_id(user_id: int):
    """使用连接池执行原生 SQL 查询"""
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM users WHERE id = :uid"),
            {"uid": user_id}
        )
        return result.mappings().first()  # 返回字典形式


if __name__ == "__main__":
    user = get_user_by_id(1)
    print(f"查询结果: {user}")
```

**连接池关键参数说明：**

| 参数 | 说明 | 推荐值 |
|------|------|--------|
| pool_size | 连接池常驻连接数 | 5-20（根据并发量） |
| max_overflow | 超出 pool_size 的额外连接 | pool_size 的 1-2 倍 |
| pool_timeout | 获取连接超时 | 30 秒 |
| pool_recycle | 连接自动回收周期 | 3600 秒（MySQL 默认 wait_timeout=28800） |
| pool_pre_ping | 使用前健康检查 | True（强烈建议） |

---

## 8.2 Python 连接 PostgreSQL

PostgreSQL 在 Python 生态中有三个主力驱动：psycopg2（经典）、psycopg3（新一代）、asyncpg（高性能异步）。

### 8.2.1 psycopg2 / psycopg2-binary：标准驱动

psycopg2 是 PostgreSQL 最成熟的 Python 驱动，部分用 C 实现，性能优于纯 Python 驱动。`psycopg2-binary` 是预编译版本，包含二进制依赖，安装更简单，适合开发和测试。生产环境建议用 `psycopg2`（从源码编译），以便自定义编译选项。

**安装：**

```bash
# 开发环境快速安装
pip install psycopg2-binary
# 生产环境（需要 PostgreSQL 开发头文件）
pip install psycopg2
```

**连接与 CRUD 完整示例：**

```python
# -*- coding: utf-8 -*-
"""
psycopg2 完整 CRUD 示例
数据库准备脚本（先在 PostgreSQL 中执行）:
    CREATE DATABASE demo_db;

    \c demo_db

    CREATE TABLE users (
        id          SERIAL PRIMARY KEY,
        username    VARCHAR(50)  NOT NULL UNIQUE,
        email       VARCHAR(100) NOT NULL,
        age         INT,
        created_at  TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
"""
import psycopg2
from psycopg2.extras import RealDictCursor


def get_connection():
    """创建 PostgreSQL 连接"""
    return psycopg2.connect(
        host="127.0.0.1",
        port=5432,
        user="postgres",
        password="your_password",
        dbname="demo_db",
        cursor_factory=RealDictCursor,  # 返回字典形式的结果
    )


def create_user(username: str, email: str, age: int):
    """插入用户并返回新记录的 ID"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # PostgreSQL 使用 %s 占位符（不是 :name 也不是 ?）
            # RETURNING 子句是 PG 特性，可以返回插入后的数据
            sql = """
                INSERT INTO users (username, email, age)
                VALUES (%s, %s, %s)
                RETURNING id, username, email, age, created_at
            """
            cursor.execute(sql, (username, email, age))
            new_user = cursor.fetchone()
        conn.commit()
        print(f"[OK] 已创建用户: {new_user}")
        return new_user
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] 创建失败: {e}")
        raise
    finally:
        conn.close()


def get_user_by_id(user_id: int):
    """根据 ID 查询"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE id = %s",
                (user_id,)
            )
            return cursor.fetchone()
    finally:
        conn.close()


def list_users(limit: int = 10, offset: int = 0):
    """分页查询用户列表"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users ORDER BY id DESC LIMIT %s OFFSET %s",
                (limit, offset)
            )
            return cursor.fetchall()
    finally:
        conn.close()


def update_user_age(user_id: int, new_age: int):
    """更新用户年龄，返回更新后的记录"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE users SET age = %s
                WHERE id = %s
                RETURNING id, username, age
                """,
                (new_age, user_id)
            )
            updated = cursor.fetchone()
        conn.commit()
        print(f"[OK] 更新结果: {updated}")
        return updated
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] 更新失败: {e}")
        raise
    finally:
        conn.close()


def delete_user(user_id: int):
    """删除用户"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        print(f"[OK] 删除 {cursor.rowcount} 条记录")
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] 删除失败: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    new_user = create_user("wangwu", "wangwu@example.com", 25)
    print(f"查询: {get_user_by_id(new_user['id'])}")
    print(f"列表: {list_users(limit=5)}")
    update_user_age(new_user["id"], 26)
    delete_user(new_user["id"])
```

**psycopg2 与 pymysql 的关键差异：**

1. **占位符**：两者都用 `%s`，但 psycopg2 还支持命名占位符 `%(name)s`，适合复杂参数。
2. **RETURNING 子句**：PostgreSQL 的 `INSERT ... RETURNING` 可以直接返回插入的行，不需要二次查询 `lastrowid`。
3. **事务默认行为**：psycopg2 默认在执行第一条 SQL 时开启事务，需要手动 `commit()`。可以设置 `conn.autocommit = True` 关闭自动事务。
4. **数据类型适配**：psycopg2 自动处理 JSON/JSONB、数组、UUID 等 PG 特有类型。

### 8.2.2 psycopg3（新一代驱动）

psycopg3 是 psycopg2 的全面重写版本，同时支持同步和异步 API，采用分模块安装（核心包 + 可选的 C 加速），架构更现代。从 2021 年发布以来逐步成熟，是目前推荐的 PostgreSQL 驱动。

**安装：**

```bash
# 核心包（纯 Python）
pip install "psycopg[binary]"
# 或者带 C 加速
pip install "psycopg[c]"
# 如果需要连接池
pip install "psycopg[pool]"
```

**与 psycopg2 的对比：**

| 对比维度 | psycopg2 | psycopg3 |
|---------|----------|----------|
| 异步支持 | 不支持（需要 psycopg2pool 等三方库） | 原生支持 async/await |
| 连接池 | 需要第三方（如 psycopg2.pool） | 内置 `psycopg.pool` |
| 安装方式 | 整体包，需要 C 编译 | 模块化安装，C 加速可选 |
| 参数传递 | `%s` 或 `%(name)s` | `%s` 或 `%(name)s`（兼容），也支持 `$1` 风格 |
| 性能 | 良好 | 更好（减少 GIL 竞争） |
| 类型适配 | 需要手动注册 | 自动适配，更灵活 |
| 服务端游标 | 支持 | 支持（API 更清晰） |

**psycopg3 完整示例：**

```python
# -*- coding: utf-8 -*-
"""
psycopg3 完整 CRUD 示例（同步模式）
安装: pip install "psycopg[binary]"
"""
import psycopg
from psycopg.rows import dict_row


# 连接字符串格式（psycopg3 推荐用连接字符串）
DSN = "host=127.0.0.1 port=5432 user=postgres password=your_password dbname=demo_db"


def create_user(username: str, email: str, age: int):
    """插入用户"""
    with psycopg.connect(DSN, row_factory=dict_row) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users (username, email, age)
                VALUES (%s, %s, %s)
                RETURNING id, username, email, age, created_at
                """,
                (username, email, age)
            )
            # psycopg3 在 with 上下文中自动 commit
            new_user = cursor.fetchone()
            print(f"[OK] 已创建: {new_user}")
            return new_user


def get_user_by_id(user_id: int):
    """查询单个用户"""
    with psycopg.connect(DSN, row_factory=dict_row) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            return cursor.fetchone()


def list_users(limit: int = 10, offset: int = 0):
    """分页查询"""
    with psycopg.connect(DSN, row_factory=dict_row) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users ORDER BY id DESC LIMIT %s OFFSET %s",
                (limit, offset)
            )
            return cursor.fetchall()


def batch_create_users(users_data: list[tuple]):
    """批量插入，使用 execute_values 高效写入"""
    from psycopg.rows import tuple_row
    with psycopg.connect(DSN, row_factory=tuple_row) as conn:
        with conn.cursor() as cursor:
            # psycopg3 的 executemany 支持管道模式，比 psycopg2 快很多
            cursor.executemany(
                "INSERT INTO users (username, email, age) VALUES (%s, %s, %s)",
                users_data,
            )
        print(f"[OK] 批量插入 {len(users_data)} 条记录")


if __name__ == "__main__":
    user = create_user("zhaoliu", "zhaoliu@example.com", 27)
    print(f"查询: {get_user_by_id(user['id'])}")
    print(f"列表: {list_users(limit=5)}")
    batch_create_users([
        ("batch_001", "b001@example.com", 20),
        ("batch_002", "b002@example.com", 21),
    ])
```

### 8.2.3 asyncpg：高性能异步驱动

asyncpg 是专门为 asyncio 设计的 PostgreSQL 异步驱动，它直接实现了 PostgreSQL 协议（不依赖 libpq C 库），性能极高，在基准测试中比 psycopg2 快 3-5 倍。FastAPI 的异步项目首选用它。

**安装：**

```bash
pip install asyncpg
```

**异步 CRUD 完整示例：**

```python
# -*- coding: utf-8 -*-
"""
asyncpg 异步 CRUD 示例
注意: asyncpg 使用 $1, $2 风格的占位符（不是 %s）
"""
import asyncio
import asyncpg


DSN = "postgresql://postgres:your_password@127.0.0.1:5432/demo_db"


async def create_pool():
    """创建异步连接池"""
    pool = await asyncpg.create_pool(
        DSN,
        min_size=5,       # 最小连接数
        max_size=20,      # 最大连接数
        command_timeout=60,  # SQL 执行超时（秒）
    )
    return pool


async def create_user(pool, username: str, email: str, age: int):
    """异步插入用户"""
    async with pool.acquire() as conn:
        # asyncpg 使用 $1, $2 风格占位符
        row = await conn.fetchrow(
            """
            INSERT INTO users (username, email, age)
            VALUES ($1, $2, $3)
            RETURNING id, username, email, age, created_at
            """,
            username, email, age
        )
        # asyncpg 返回的是 Record 对象，可以按列名取值
        return dict(row)


async def get_user_by_id(pool, user_id: int):
    """异步查询单个用户"""
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id, username, email, age, created_at FROM users WHERE id = $1",
            user_id
        )
        return dict(row) if row else None


async def list_users(pool, limit: int = 10, offset: int = 0):
    """异步分页查询"""
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM users ORDER BY id DESC LIMIT $1 OFFSET $2",
            limit, offset
        )
        return [dict(r) for r in rows]


async def update_user_age(pool, user_id: int, new_age: int):
    """异步更新"""
    async with pool.acquire() as conn:
        result = await conn.execute(
            "UPDATE users SET age = $1 WHERE id = $2",
            new_age, user_id
        )
        return result  # 返回 "UPDATE 1" 表示更新了 1 行


async def delete_user(pool, user_id: int):
    """异步删除"""
    async with pool.acquire() as conn:
        result = await conn.execute("DELETE FROM users WHERE id = $1", user_id)
        return result


async def transaction_demo(pool):
    """演示事务：转账场景"""
    async with pool.acquire() as conn:
        # asyncpg 的事务通过 async with 管理
        async with conn.transaction():
            # 这里的操作要么全部成功，要么全部回滚
            await conn.execute(
                "UPDATE accounts SET balance = balance - 100 WHERE user_id = $1",
                1
            )
            await conn.execute(
                "UPDATE accounts SET balance = balance + 100 WHERE user_id = $2",
                2
            )
            # 如果没有异常，自动 commit；有异常则自动 rollback


async def main():
    pool = await create_pool()
    try:
        user = await create_user(pool, "async_user", "async@example.com", 22)
        print(f"创建: {user}")
        print(f"查询: {await get_user_by_id(pool, user['id'])}")
        print(f"列表: {await list_users(pool, limit=5)}")
        await update_user_age(pool, user["id"], 23)
        print(f"更新后: {await get_user_by_id(pool, user["id"])}")
        await delete_user(pool, user["id"])
    finally:
        await pool.close()


if __name__ == "__main__":
    asyncio.run(main())
```

### 8.2.4 连接池：psycopg.pool / asyncpg.create_pool

上面 asyncpg 的示例已经展示了 `asyncpg.create_pool` 的用法，这里补充 psycopg3 内置连接池的用法：

```python
# -*- coding: utf-8 -*-
"""
psycopg3 连接池示例
安装: pip install "psycopg[pool]"
"""
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row


# 全局连接池（应用启动时创建，关闭时销毁）
pool = ConnectionPool(
    conninfo="host=127.0.0.1 port=5432 user=postgres password=your_password dbname=demo_db",
    min_size=5,          # 最小保持的连接数
    max_size=20,         # 最大连接数
    timeout=30,          # 获取连接超时
    max_idle=300,         # 空闲连接最大存活时间（秒）
    row_factory=dict_row,
)


def get_user_by_id(user_id: int):
    """从连接池获取连接执行查询"""
    with pool.connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            return cursor.fetchone()


def create_user(username: str, email: str, age: int):
    """插入用户"""
    with pool.connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO users (username, email, age) VALUES (%s, %s, %s) RETURNING *",
                (username, email, age)
            )
            # psycopg3 的 connection 上下文管理器在退出时自动 commit
            return cursor.fetchone()


if __name__ == "__main__":
    user = create_user("pool_user", "pool@example.com", 24)
    print(f"创建: {user}")
    print(f"查询: {get_user_by_id(user['id'])}")
```

---

## 8.3 SQLAlchemy ORM 详解

这是本章最重要的部分。SQLAlchemy 是 Python 生态中最强大的数据库工具包，它既是 ORM（对象关系映射），也是 SQL 表达式语言（Core）。无论你用 FastAPI、Flask 还是其他框架，SQLAlchemy 都是后端项目的标配。

### 8.3.1 SQLAlchemy 2.0 架构：Core + ORM

SQLAlchemy 2.0 是一次重大升级，引入了全新的类型系统、统一的 API 风格和原生异步支持。理解它的架构是掌握它的前提。

**Core 层（SQL 表达式语言）：**
- Core 是 SQLAlchemy 的基础，提供 SQL 构造器，让你用 Python 对象构建 SQL 语句
- 核心对象：`Engine`（引擎/连接池）、`Connection`（连接）、`Table`（表定义）、`select()`（查询构造）
- 适合：需要精细控制 SQL、复杂查询、报表统计、批量操作
- 类比：相当于 JavaScript 中的 query builder（如 Knex.js）

**ORM 层（对象关系映射）：**
- ORM 构建在 Core 之上，将数据库表映射为 Python 类，表行映射为对象实例
- 核心对象：`DeclarativeBase`（基类）、`Session`（会话）、`Mapped`（类型注解）、`relationship()`（关系映射）
- 适合：CRUD 业务逻辑、模型驱动开发、标准 Web 应用
- 类比：相当于 Node.js 中的 Prisma、TypeORM、Sequelize

**与 1.x 的关键区别：**

| 维度 | 1.x（旧版） | 2.0（新版） |
|------|------------|------------|
| 基类 | `declarative_base()` 返回基类 | 继承 `DeclarativeBase` 类 |
| 类型注解 | `Column(Integer)` 声明类型 | `Mapped[int]` 注解 + `mapped_column()` |
| 查询 API | `session.query(User).filter(...)` | `session.execute(select(User).where(...))` |
| 异步支持 | 需要第三方扩展 | 原生 `AsyncSession`、`async_engine` |
| 风格 | "经典"风格，多套 API 并存 | 统一为 2.0 风格，废弃旧 API |
| 新增类型 | 无 | 全面使用 Python type hints（PEP 484） |

**安装：**

```bash
# 核心包 + 驱动
pip install sqlalchemy[asyncio] pymysql asyncpg

# 或者只用同步
pip install sqlalchemy pymysql
```

> **给前端开发者的类比**：如果你用过 Node.js 的 Prisma，SQLAlchemy 2.0 的 `Mapped` 注解就类似 Prisma 的 schema 定义，`select()` 就类似 Prisma 的 `prisma.user.findMany()`，`Session` 类似 Prisma Client 的 transaction 上下文。但 SQLAlchemy 更底层、更灵活。

### 8.3.2 模型定义：使用 DeclarativeBase

SQLAlchemy 2.0 使用类继承的方式定义模型基类，这是与 1.x 最大的语法差异之一。

```python
# -*- coding: utf-8 -*-
"""
SQLAlchemy 2.0 模型定义示例（新版 DeclarativeBase 语法）
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """所有模型的基类"""
    pass


class User(Base):
    """用户表模型"""
    __tablename__ = "users"

    # Mapped[int] 是 Python 类型注解，告诉 SQLAlchemy 这个字段的 Python 类型
    # mapped_column() 定义数据库层面的列属性
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Mapped[str] 表示 Python 层面是 str 类型
    # String(50) 在数据库层面创建 VARCHAR(50)
    # 注意: 2.0 中可以根据 Mapped 注解自动推导 SQL 类型，但建议显式声明长度
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 可空字段

    # server_default 定义数据库层面的默认值
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


# 不要再用旧版语法:
# from sqlalchemy.orm import declarative_base
# Base = declarative_base()    # <-- 1.x 旧语法，2.0 中已废弃
```

**Mapped 类型注解详解：**

`Mapped[X]` 中的 `X` 是 Python 类型，SQLAlchemy 会自动推导对应的 SQL 类型：

| Python 类型注解 | 自动推导的 SQL 类型 | 说明 |
|----------------|-------------------|------|
| `Mapped[int]` | INTEGER | 整数 |
| `Mapped[str]` | VARCHAR | 字符串（需用 `mapped_column(String(N))` 指定长度） |
| `Mapped[bool]` | BOOLEAN | 布尔值 |
| `Mapped[float]` | FLOAT | 浮点数 |
| `Mapped[datetime]` | DATETIME | 日期时间 |
| `Mapped[date]` | DATE | 日期 |
| `Mapped[bytes]` | LargeBinary | 二进制数据 |
| `Mapped[Optional[int]]` | INTEGER NULL | 可空整数（`Optional[X]` 等价于 `X | None`） |
| `Mapped[str | None]` | VARCHAR NULL | 可空字符串（Python 3.10+ 语法） |

### 8.3.3 Column 类型映射

下面通过一个更完整的模型定义来展示各种类型映射：

```python
# -*- coding: utf-8 -*-
"""
SQLAlchemy 2.0 类型映射完整示例
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional
import uuid

from sqlalchemy import (
    String, Integer, BigInteger, Float, Numeric, Boolean,
    DateTime, Date, Time, Text, LargeBinary, JSON,
    ForeignKey, Uuid, func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Product(Base):
    """商品表 - 演示各种类型映射"""
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Numeric 用于金额，避免浮点精度问题
    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False  # 10位总精度，2位小数
    )

    # Float 用于不需要高精度的场景
    weight: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # JSON 类型：MySQL 用 JSON，PostgreSQL 用 JSONB
    attributes: Mapped[dict] = mapped_column(JSON, default=dict)

    # UUID 类型
    sku: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),  # as_uuid=True 表示 Python 层面用 uuid.UUID 对象
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )

    def __repr__(self) -> str:
        return f"<Product(id={self.id}, name='{self.name}', price={self.price})>"
```

### 8.3.4 关系定义：relationship() + ForeignKey

关系映射是 ORM 的核心功能。SQLAlchemy 用 `ForeignKey` 定义外键约束，用 `relationship()` 定义对象间的关系。

**一对多关系（one-to-many）：用户与文章**

```python
from sqlalchemy import String, Integer, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Optional, List
from datetime import datetime


class Base(DeclarativeBase):
    pass


class User(Base):
    """用户表（一的一方）"""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)

    # relationship 定义与 Article 的关系
    # back_populates 双向关联: User.articles <-> Article.author
    # 一对多: 一个用户有多篇文章
    articles: Mapped[List["Article"]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan"  # 删除用户时级联删除其文章
    )


class Article(Base):
    """文章表（多的一方）"""
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[Optional[str]] = mapped_column(Text)
    views: Mapped[int] = mapped_column(Integer, default=0)

    # 外键: 指向 users 表的 id
    author_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
    )

    # relationship 的另一端
    author: Mapped[Optional["User"]] = relationship(back_populates="articles")

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp())
```

**多对多关系（many-to-many）：文章与标签**

```python
# 多对多需要一张中间表
from sqlalchemy import Table, Column


# 中间表: article_tags
article_tag = Table(
    "article_tags",
    Base.metadata,
    Column("article_id", ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Tag(Base):
    """标签表"""
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)

    # 多对多关系: secondary 指定中间表
    articles: Mapped[List["Article"]] = relationship(
        secondary=article_tag,
        back_populates="tags"
    )


# 修改 Article 模型，添加 tags 关系
class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[Optional[str]] = mapped_column(Text)
    views: Mapped[int] = mapped_column(Integer, default=0)
    author_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )

    author: Mapped[Optional["User"]] = relationship(back_populates="articles")
    tags: Mapped[List["Tag"]] = relationship(
        secondary=article_tag,
        back_populates="articles"
    )

    # 评论关系（一对多）
    comments: Mapped[List["Comment"]] = relationship(
        back_populates="article",
        cascade="all, delete-orphan"
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp())


class Comment(Base):
    """评论表"""
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(Text)
    article_id: Mapped[int] = mapped_column(
        ForeignKey("articles.id", ondelete="CASCADE")
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    article: Mapped["Article"] = relationship(back_populates="comments")
    # 也可以加 user 关系
    user: Mapped["User"] = relationship()  # 不加 back_populates 表示单向
```

**关系参数详解：**

| 参数 | 说明 |
|------|------|
| `back_populates` | 双向关系，两端互相引用对方的属性名 |
| `cascade="all, delete-orphan"` | 级联操作：删除父对象时删除子对象 |
| `lazy="select"` | 默认加载策略，访问时发查询（会导致 N+1） |
| `lazy="selectin"` | 用 IN 查询预加载（推荐，解决 N+1） |
| `lazy="joined"` | 用 JOIN 预加载 |
| `secondary` | 多对多关系的中间表 |
| `order_by` | 关系集合的默认排序 |

### 8.3.5 查询 API：使用 select() 语句

SQLAlchemy 2.0 统一使用 `select()` 构造查询，取代了 1.x 的 `Query` API。这是从"旧时代"迁移到"新时代"最重要的变化。

**基础查询：where 条件**

```python
from sqlalchemy import select, and_, or_, desc, asc
from sqlalchemy.orm import Session


def query_examples(session: Session):
    # ---- 基本查询 ----
    # 查询所有用户 (等价 SQL: SELECT * FROM users)
    stmt = select(User)
    users = session.execute(stmt).scalars().all()

    # 按条件查询 (WHERE username = 'zhangsan')
    stmt = select(User).where(User.username == "zhangsan")
    user = session.execute(stmt).scalars().first()

    # 按主键查询（推荐方式）
    user = session.get(User, 1)  # 等价于 SELECT * FROM users WHERE id = 1

    # ---- 多条件查询 ----
    # AND 条件
    stmt = select(User).where(
        User.age >= 18,
        User.age <= 60,
    )
    # 或者用 and_
    stmt = select(User).where(
        and_(User.age >= 18, User.age <= 60)
    )

    # OR 条件
    stmt = select(User).where(
        or_(User.username == "admin", User.email.like("%@example.com"))
    )

    # ---- 模糊查询 ----
    stmt = select(User).where(User.username.like("%zhang%"))
    stmt = select(User).where(User.username.ilike("%Zhang%"))  # 不区分大小写

    # ---- IN 查询 ----
    stmt = select(User).where(User.id.in_([1, 2, 3]))

    # ---- IS NULL / IS NOT NULL ----
    stmt = select(User).where(User.age.is_(None))
    stmt = select(User).where(User.age.is_not(None))

    # ---- 排序 ----
    stmt = select(User).order_by(desc(User.created_at))  # 降序
    stmt = select(User).order_by(asc(User.age))          # 升序
    stmt = select(User).order_by(User.age.desc(), User.id.asc())  # 多字段排序

    # ---- 限制数量 ----
    stmt = select(User).limit(10).offset(20)  # 分页: LIMIT 10 OFFSET 20

    return session.execute(stmt).scalars().all()
```

**进阶查询：join、group_by、func**

```python
from sqlalchemy import func, count, avg, sum as sql_sum


def advanced_queries(session: Session):
    # ---- JOIN 查询 ----
    # 查询每个用户及其文章数量
    # 方法1: 使用 join + group_by
    stmt = (
        select(
            User.id,
            User.username,
            func.count(Article.id).label("article_count"),
        )
        .outerjoin(Article, Article.author_id == User.id)  # LEFT JOIN
        .group_by(User.id, User.username)
        .order_by(desc("article_count"))
    )
    result = session.execute(stmt).all()
    for row in result:
        print(f"用户: {row.username}, 文章数: {row.article_count}")

    # 方法2: 使用关系自动 join
    # 当查询中引用了 relationship 时，SQLAlchemy 会自动 join
    stmt = (
        select(Article)
        .join(Article.author)   # 通过关系 JOIN
        .where(User.username == "zhangsan")
    )
    articles = session.execute(stmt).scalars().all()

    # ---- 子查询 ----
    # 查询文章数大于 5 的用户
    subq = (
        select(Article.author_id, func.count(Article.id).label("cnt"))
        .group_by(Article.author_id)
        .having(func.count(Article.id) > 5)
        .subquery()
    )
    stmt = (
        select(User)
        .join(subq, User.id == subq.c.author_id)
    )
    active_users = session.execute(stmt).scalars().all()

    # ---- 聚合查询 ----
    # 统计每个标签被多少文章使用
    stmt = (
        select(
            Tag.name,
            func.count(article_tag.c.article_id).label("usage_count"),
        )
        .join(article_tag)
        .group_by(Tag.name)
        .order_by(desc("usage_count"))
    )
    result = session.execute(stmt).all()

    # ---- EXISTS 查询 ----
    from sqlalchemy import exists
    stmt = select(User).where(
        exists().where(Article.author_id == User.id)
    )
    users_with_articles = session.execute(stmt).scalars().all()

    # ---- 聚合函数 ----
    total_users = session.execute(select(func.count(User.id))).scalar()
    avg_age = session.execute(select(func.avg(User.age))).scalar()
    total_views = session.execute(
        select(func.sum(Article.views))
    ).scalar()

    return result
```

### 8.3.6 会话管理（Session）

Session 是 SQLAlchemy ORM 的核心，它实现了"工作单元"（Unit of Work）模式，负责追踪对象的变更并统一刷新到数据库。

```python
# -*- coding: utf-8 -*-
"""
Session 会话管理详解
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


engine = create_engine(
    "mysql+pymysql://root:your_password@127.0.0.1:3306/demo_db?charset=utf8mb4",
    echo=False,
    pool_size=10,
    pool_recycle=3600,
)

# sessionmaker 是 Session 工厂
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def demo_session_basic():
    """基本会话操作"""
    # 方式1: 使用上下文管理器（推荐）
    with Session(engine) as session:
        # 创建对象
        user = User(username="session_test", email="st@example.com", age=25)
        session.add(user)

        # flush: 将变更发送到数据库但不提交事务
        # 此时数据库事务已开启，但未提交
        # flush 后 user.id 会被填充（自增主键回填）
        session.flush()
        print(f"flush 后，user.id = {user.id}")  # 此时已有值

        # commit: 提交事务，变更持久化
        session.commit()
        print(f"commit 后，user.id = {user.id}")

    # 方式2: 使用 sessionmaker
    session = SessionLocal()
    try:
        user = User(username="session_test2", email="st2@example.com", age=26)
        session.add(user)
        session.commit()
    except Exception as e:
        session.rollback()  # 出错时回滚
        print(f"[ERROR] {e}")
    finally:
        session.close()  # 关闭会话（归还连接到连接池）


def demo_session_bulk():
    """批量操作"""
    with Session(engine) as session:
        # 批量添加
        users = [
            User(username=f"bulk_{i}", email=f"bulk{i}@example.com", age=20 + i)
            for i in range(100)
        ]
        session.add_all(users)
        session.commit()
        print(f"[OK] 批量添加 {len(users)} 条")

        # 批量更新（高性能，绕过 ORM）
        from sqlalchemy import update
        session.execute(
            update(User)
            .where(User.username.like("bulk_%"))
            .values(age=99)
        )
        session.commit()

        # 批量删除
        from sqlalchemy import delete
        session.execute(
            delete(User).where(User.username.like("bulk_%"))
        )
        session.commit()


def demo_session_transaction():
    """嵌套事务（SAVEPOINT）"""
    with Session(engine) as session:
        user1 = User(username="tx_user1", email="tx1@example.com", age=20)
        session.add(user1)
        session.flush()

        # 开始一个嵌套事务（SAVEPOINT）
        nested = session.begin_nested()
        try:
            user2 = User(username="tx_user2", email="tx2@example.com", age=21)
            session.add(user2)
            # 模拟异常
            raise ValueError("模拟出错")
        except ValueError as e:
            nested.rollback()  # 回滚到 SAVEPOINT，user2 被撤销
            print(f"[ROLLBACK] 嵌套事务回滚: {e}")

        # user1 仍然在事务中，不受影响
        session.commit()  # 提交 user1
        print("[OK] 主事务提交成功，user1 已保存，user2 已回滚")
```

**Session 核心方法说明：**

| 方法 | 说明 |
|------|------|
| `session.add(obj)` | 将对象加入会话，标记为待插入 |
| `session.add_all([obj1, obj2])` | 批量加入 |
| `session.flush()` | 将待处理的变更发送到数据库（不提交事务），主键回填 |
| `session.commit()` | 提交事务，所有变更持久化 |
| `session.rollback()` | 回滚事务，撤销所有未提交的变更 |
| `session.delete(obj)` | 标记对象为待删除 |
| `session.get(Model, id)` | 按主键查询 |
| `session.refresh(obj)` | 从数据库重新加载对象的状态 |
| `session.expire(obj)` | 标记对象为过期，下次访问时重新查询 |
| `session.merge(obj)` | 将游离态对象合并到会话中 |

### 8.3.7 异步 SQLAlchemy：AsyncSession + async_engine

SQLAlchemy 2.0 原生支持异步操作，这是 FastAPI 异步数据库操作的标配。

```python
# -*- coding: utf-8 -*-
"""
异步 SQLAlchemy 完整示例
安装: pip install sqlalchemy[asyncio] asyncpg
"""
import asyncio
from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, Integer, Text, ForeignKey, DateTime, func, select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String(100))
    age: Mapped[Optional[int]] = mapped_column(Integer)

    articles: Mapped[List["Article"]] = relationship(
        back_populates="author", cascade="all, delete-orphan"
    )


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[Optional[str]] = mapped_column(Text)
    author_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )

    author: Mapped[Optional["User"]] = relationship(back_populates="articles")


# 创建异步引擎
# PostgreSQL: postgresql+asyncpg://...
# MySQL: mysql+aiomysql://...
async_engine = create_async_engine(
    "postgresql+asyncpg://postgres:your_password@127.0.0.1:5432/demo_db",
    echo=False,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,
)

# 异步 Session 工厂
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,  # 异步环境下 commit 后不要 expire（避免隐式 IO）
)


async def async_create_user(username: str, email: str, age: int):
    """异步创建用户"""
    async with AsyncSessionLocal() as session:
        user = User(username=username, email=email, age=age)
        session.add(user)
        await session.commit()
        await session.refresh(user)  # 刷新以获取自增 ID 和默认值
        return user


async def async_get_user(user_id: int):
    """异步查询用户"""
    async with AsyncSessionLocal() as session:
        # 异步按主键查询
        user = await session.get(User, user_id)
        return user


async def async_list_users(min_age: int = 0, limit: int = 10):
    """异步查询用户列表"""
    async with AsyncSessionLocal() as session:
        stmt = (
            select(User)
            .where(User.age >= min_age)
            .order_by(User.id.desc())
            .limit(limit)
        )
        result = await session.execute(stmt)
        return result.scalars().all()


async def async_update_user_age(user_id: int, new_age: int):
    """异步更新"""
    async with AsyncSessionLocal() as session:
        user = await session.get(User, user_id)
        if user:
            user.age = new_age
            await session.commit()
            return True
        return False


async def async_delete_user(user_id: int):
    """异步删除"""
    async with AsyncSessionLocal() as session:
        user = await session.get(User, user_id)
        if user:
            await session.delete(user)
            await session.commit()
            return True
        return False


async def async_create_user_with_articles(username: str, email: str, articles_data: list):
    """异步创建用户及其文章（演示关系操作）"""
    async with AsyncSessionLocal() as session:
        user = User(username=username, email=email, age=25)
        # 直接通过关系添加文章
        for title, content in articles_data:
            article = Article(title=title, content=content)
            user.articles.append(article)

        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


async def main():
    # 创建表（仅用于演示，生产环境用 Alembic）
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # CRUD 演示
    user = await async_create_user("async_orm", "asyncorm@example.com", 28)
    print(f"创建: {user}")

    fetched = await async_get_user(user.id)
    print(f"查询: {fetched}")

    users = await async_list_users(min_age=20, limit=5)
    print(f"列表: {users}")

    await async_update_user_age(user.id, 29)
    print(f"更新后: {await async_get_user(user.id)}")

    # 关系操作
    await async_create_user_with_articles(
        "writer001",
        "writer@example.com",
        [("Python 入门", "Python 基础内容"), ("数据库设计", "表设计原则")]
    )

    await async_delete_user(user.id)
    print(f"删除后: {await async_get_user(user.id)}")

    # 关闭引擎
    await async_engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
```

> **异步注意事项**：`expire_on_commit=False` 在异步环境中是必须的。因为 `commit()` 后默认会 `expire` 所有对象，下次访问属性时会触发隐式的数据库查询，这在异步环境中会报错（不能在 async 函数外执行 IO）。

### 8.3.8 实战：用户-文章-评论模型完整 CRUD

下面给出一个完整可运行的实战项目，包含模型定义和所有 CRUD 操作。这个示例使用 MySQL（你也可以改成 PostgreSQL，只需修改连接字符串）。

```python
# -*- coding: utf-8 -*-
"""
实战: 用户-文章-评论 模型完整 CRUD
数据库: MySQL (改连接字符串即可切换 PostgreSQL)
依赖: pip install sqlalchemy pymysql
"""
from datetime import datetime
from typing import Optional, List

from sqlalchemy import (
    create_engine, select, func, desc, and_, or_,
    String, Integer, Text, ForeignKey, DateTime,
)
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column, relationship,
    Session, sessionmaker, selectinload,
)


# ============================================================
# 1. 模型定义
# ============================================================

class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    age: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )

    articles: Mapped[List["Article"]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan",
        lazy="selectin",  # 预加载策略，避免 N+1
    )
    comments: Mapped[List["Comment"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[Optional[str]] = mapped_column(Text)
    views: Mapped[int] = mapped_column(Integer, default=0)
    author_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )

    author: Mapped[Optional["User"]] = relationship(back_populates="articles")
    comments: Mapped[List["Comment"]] = relationship(
        back_populates="article",
        cascade="all, delete-orphan",
        order_by="Comment.created_at.desc()",  # 评论按时间降序
    )

    def __repr__(self):
        return f"<Article(id={self.id}, title='{self.title}')>"


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    article_id: Mapped[int] = mapped_column(
        ForeignKey("articles.id", ondelete="CASCADE")
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )

    article: Mapped["Article"] = relationship(back_populates="comments")
    user: Mapped["User"] = relationship(back_populates="comments")

    def __repr__(self):
        return f"<Comment(id={self.id}, content='{self.content[:20]}...')>"


# ============================================================
# 2. 数据库连接与会话
# ============================================================

DATABASE_URL = "mysql+pymysql://root:your_password@127.0.0.1:3306/demo_db?charset=utf8mb4"

engine = create_engine(DATABASE_URL, echo=False, pool_recycle=3600)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db():
    """获取数据库会话的生成器（FastAPI 依赖注入也会用到）"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================
# 3. 用户 CRUD
# ============================================================

def create_user(username: str, email: str, age: int) -> User:
    """创建用户"""
    with Session(engine) as session:
        user = User(username=username, email=email, age=age)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


def get_user(user_id: int) -> Optional[User]:
    """按 ID 查询用户"""
    with Session(engine) as session:
        return session.get(User, user_id)


def get_user_with_articles(user_id: int) -> Optional[User]:
    """查询用户及其文章（使用预加载避免 N+1）"""
    with Session(engine) as session:
        stmt = (
            select(User)
            .options(selectinload(User.articles))  # 预加载文章
            .where(User.id == user_id)
        )
        return session.execute(stmt).scalars().first()


def list_users(min_age: int = 0, max_age: int = 150, limit: int = 20) -> List[User]:
    """分页查询用户列表"""
    with Session(engine) as session:
        stmt = (
            select(User)
            .where(and_(User.age >= min_age, User.age <= max_age))
            .order_by(desc(User.created_at))
            .limit(limit)
        )
        return list(session.execute(stmt).scalars().all())


def update_user(user_id: int, **kwargs) -> Optional[User]:
    """更新用户（支持部分字段更新）"""
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            return None
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        session.commit()
        session.refresh(user)
        return user


def delete_user(user_id: int) -> bool:
    """删除用户（级联删除其文章和评论）"""
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            return False
        session.delete(user)
        session.commit()
        return True


# ============================================================
# 4. 文章 CRUD
# ============================================================

def create_article(author_id: int, title: str, content: str) -> Optional[Article]:
    """创建文章"""
    with Session(engine) as session:
        user = session.get(User, author_id)
        if not user:
            print(f"[ERROR] 用户 {author_id} 不存在")
            return None
        article = Article(title=title, content=content, author_id=author_id)
        session.add(article)
        session.commit()
        session.refresh(article)
        return article


def get_article_with_comments(article_id: int) -> Optional[Article]:
    """查询文章及其评论和评论者（三级预加载）"""
    with Session(engine) as session:
        stmt = (
            select(Article)
            .options(
                selectinload(Article.comments).selectinload(Comment.user),  # 预加载评论+评论者
            )
            .where(Article.id == article_id)
        )
        return session.execute(stmt).scalars().first()


def list_articles_by_author(author_id: int) -> List[Article]:
    """查询某用户的所有文章"""
    with Session(engine) as session:
        stmt = select(Article).where(Article.author_id == author_id)
        return list(session.execute(stmt).scalars().all())


def increment_views(article_id: int):
    """增加文章浏览量（使用原子操作，避免并发问题）"""
    from sqlalchemy import update
    with Session(engine) as session:
        session.execute(
            update(Article)
            .where(Article.id == article_id)
            .values(views=Article.views + 1)
        )
        session.commit()


def search_articles(keyword: str, limit: int = 10) -> List[Article]:
    """搜索文章标题或内容"""
    with Session(engine) as session:
        stmt = (
            select(Article)
            .where(
                or_(
                    Article.title.like(f"%{keyword}%"),
                    Article.content.like(f"%{keyword}%"),
                )
            )
            .order_by(desc(Article.views))
            .limit(limit)
        )
        return list(session.execute(stmt).scalars().all())


# ============================================================
# 5. 评论 CRUD
# ============================================================

def create_comment(article_id: int, user_id: int, content: str) -> Optional[Comment]:
    """创建评论"""
    with Session(engine) as session:
        article = session.get(Article, article_id)
        if not article:
            print(f"[ERROR] 文章 {article_id} 不存在")
            return None
        comment = Comment(
            content=content,
            article_id=article_id,
            user_id=user_id,
        )
        session.add(comment)
        session.commit()
        session.refresh(comment)
        return comment


def list_comments_by_article(article_id: int) -> List[Comment]:
    """查询文章的所有评论"""
    with Session(engine) as session:
        stmt = (
            select(Comment)
            .where(Comment.article_id == article_id)
            .order_by(desc(Comment.created_at))
        )
        return list(session.execute(stmt).scalars().all())


# ============================================================
# 6. 统计查询
# ============================================================

def get_user_article_stats():
    """统计每个用户的文章数量和总浏览量"""
    with Session(engine) as session:
        stmt = (
            select(
                User.id,
                User.username,
                func.count(Article.id).label("article_count"),
                func.sum(Article.views).label("total_views"),
            )
            .outerjoin(Article, Article.author_id == User.id)
            .group_by(User.id, User.username)
            .order_by(desc("total_views"))
        )
        result = session.execute(stmt).all()
        return [
            {
                "user_id": row.id,
                "username": row.username,
                "article_count": row.article_count,
                "total_views": row.total_views or 0,
            }
            for row in result
        ]


def get_popular_articles(top_n: int = 10):
    """获取热门文章（含作者信息）"""
    with Session(engine) as session:
        stmt = (
            select(Article)
            .options(selectinload(Article.author))  # 预加载作者
            .order_by(desc(Article.views))
            .limit(top_n)
        )
        articles = session.execute(stmt).scalars().all()
        return [
            {
                "id": a.id,
                "title": a.title,
                "views": a.views,
                "author": a.author.username if a.author else None,
            }
            for a in articles
        ]


# ============================================================
# 7. 主函数: 运行完整演示
# ============================================================

def main():
    # 创建所有表
    Base.metadata.create_all(engine)
    print("[OK] 表创建完成")

    # 创建用户
    u1 = create_user("alice", "alice@example.com", 25)
    u2 = create_user("bob", "bob@example.com", 30)
    print(f"创建用户: {u1}, {u2}")

    # 创建文章
    a1 = create_article(u1.id, "Python 数据库入门", "从零开始学习...")
    a2 = create_article(u1.id, "SQLAlchemy 2.0 指南", "新版语法详解...")
    a3 = create_article(u2.id, "FastAPI 实战", "RESTful API 开发...")
    print(f"创建文章: {a1}, {a2}, {a3}")

    # 增加浏览量
    increment_views(a1.id)
    increment_views(a1.id)
    increment_views(a1.id)
    increment_views(a2.id)
    increment_views(a2.id)

    # 创建评论
    create_comment(a1.id, u2.id, "写得好!")
    create_comment(a1.id, u2.id, "学到了很多")
    create_comment(a2.id, u2.id, "期待更多")

    # 查询: 用户及其文章（预加载）
    user_with_articles = get_user_with_articles(u1.id)
    print(f"\n用户 {user_with_articles.username} 的文章:")
    for art in user_with_articles.articles:
        print(f"  - {art.title} (浏览: {art.views})")

    # 查询: 文章及其评论（三级预加载）
    article_detail = get_article_with_comments(a1.id)
    print(f"\n文章 '{article_detail.title}' 的评论:")
    for c in article_detail.comments:
        print(f"  [{c.user.username}] {c.content}")

    # 统计查询
    print(f"\n用户文章统计:")
    for stat in get_user_article_stats():
        print(f"  {stat['username']}: {stat['article_count']} 篇, "
              f"总浏览 {stat['total_views']}")

    print(f"\n热门文章:")
    for art in get_popular_articles(top_n=5):
        print(f"  [{art['author']}] {art['title']} - {art['views']} 浏览")

    # 搜索
    print(f"\n搜索 'Python':")
    for art in search_articles("Python"):
        print(f"  {art.title}")

    # 更新
    updated = update_user(u1.id, age=26, email="alice_new@example.com")
    print(f"\n更新后: {updated}")

    # 删除（级联）
    # delete_user(u1.id)  # 会级联删除该用户的文章和评论


if __name__ == "__main__":
    main()
```

这段代码是本章的核心成果。它演示了：
1. 完整的三表模型（用户-文章-评论）及一对多关系
2. 级联删除策略（`cascade="all, delete-orphan"` + 外键 `ondelete="CASCADE"`）
3. 预加载策略（`selectinload`）解决 N+1 问题
4. 2.0 新语法查询（`select().where().order_by()`）
5. 聚合统计查询（`func.count`、`func.sum`、`group_by`）
6. 原子更新（`UPDATE ... SET views = views + 1`）
7. 完整的 CRUD 封装，可以直接作为项目骨架

---

## 8.4 原生 SQL vs ORM

ORM 不是银弹。理解什么时候用 ORM、什么时候用原生 SQL，是后端工程师的核心技能。

### 8.4.1 什么时候用原生 SQL，什么时候用 ORM

**决策指南：**

```
                    +---------------------------+
                    | 需要执行数据库操作          |
                    +---------------------------+
                               |
                    +----------+----------+
                    |                     |
              简单 CRUD            复杂查询/批量操作
              (增删改查)           (统计/报表/ETL)
                    |                     |
              使用 ORM              使用原生 SQL
              (SQLAlchemy)         (text() / Core)
                    |                     |
                    +----------+----------+
                               |
                    +----------+----------+
                    |                     |
              需要 100% 控制         性能极端敏感
              SQL 执行计划           (每毫秒都重要)
                    |                     |
              使用原生 SQL            使用原生 SQL
```

**使用 ORM 的场景：**
- 标准 CRUD 操作（增删改查单条/多条记录）
- 基于对象模型的业务逻辑（如"给用户添加一篇文章"）
- 需要类型安全和 IDE 自动补全
- 需要跨数据库兼容（一套代码同时跑 MySQL 和 PG）
- 团队中有不熟悉 SQL 的开发者

**使用原生 SQL 的场景：**
- 复杂统计查询（多表 JOIN + 子查询 + 窗口函数）
- 批量数据导入/导出（如 `INSERT INTO ... SELECT`、`LOAD DATA`）
- 数据库特定的高级特性（如 PostgreSQL 的 `LATERAL JOIN`、CTE）
- 性能极端敏感的场景（ORM 有额外开销）
- 需要精确控制 SQL 执行计划

**混合策略（最佳实践）：**

实际项目中通常是混合使用：90% 的操作用 ORM，10% 的复杂查询用原生 SQL。SQLAlchemy 完美支持这种混合模式。

### 8.4.2 复杂查询的 SQLAlchemy Core 方案

当 ORM 的 `select()` 难以表达复杂查询时，可以用 `text()` 直接写原生 SQL，或用 Core 表达式构建。

**使用 text() 执行原生 SQL：**

```python
# -*- coding: utf-8 -*-
"""
SQLAlchemy text() 原生 SQL 示例
"""
from sqlalchemy import create_engine, text


engine = create_engine(
    "mysql+pymysql://root:your_password@127.0.0.1:3306/demo_db?charset=utf8mb4"
)


def raw_sql_examples():
    """text() 原生 SQL 用法"""
    with engine.connect() as conn:
        # ---- 简单查询 ----
        # 使用 :name 命名参数（SQLAlchemy 风格，不是 %s）
        stmt = text("SELECT * FROM users WHERE age > :min_age ORDER BY id")
        result = conn.execute(stmt, {"min_age": 20})
        for row in result.mappings():  # mappings() 返回字典
            print(row)

        # ---- 写操作 ----
        stmt = text(
            "INSERT INTO users (username, email, age) VALUES (:name, :email, :age)"
        )
        conn.execute(stmt, {"name": "raw_user", "email": "raw@example.com", "age": 25})
        conn.commit()

        # ---- 复杂统计查询（ORM 难以表达的） ----
        # 窗口函数: 每个用户浏览量最高的文章
        stmt = text("""
            SELECT
                username,
                title,
                views,
                RANK() OVER (PARTITION BY author_id ORDER BY views DESC) AS rnk
            FROM articles
            JOIN users ON articles.author_id = users.id
            WHERE views > 0
            ORDER BY author_id, rnk
        """)
        result = conn.execute(stmt)
        for row in result:
            print(f"{row.username} | {row.title} | views={row.views} | rank={row.rnk}")

        # ---- 动态 SQL 构建 ----
        # 使用 Core 表达式动态拼接条件
        from sqlalchemy import table, column

        users_table = table("users",
            column("id"),
            column("username"),
            column("age"),
        )

        # 动态条件
        conditions = []
        params = {}
        if some_condition:  # 假设的外部条件
            conditions.append(users_table.c.age > 20)
            params["min_age"] = 20

        stmt = select(users_table)
        if conditions:
            stmt = stmt.where(*conditions)
        # ...


raw_sql_examples()
```

### 8.4.3 SQL 注入防御：参数化查询

SQL 注入是 Web 安全的头号威胁。前端开发者转向后端时，必须深刻理解参数化查询。

**危险代码（字符串拼接，绝不要这样写）：**

```python
# !!! 危险代码 - 仅作反面教材，切勿在生产环境使用 !!!

def dangerous_query(username: str):
    """危险: 直接拼接 SQL 字符串，存在 SQL 注入漏洞"""
    conn = get_connection()  # 假设的连接获取函数
    # 攻击者输入 username = "admin' OR '1'='1"
    # 拼接后变成: SELECT * FROM users WHERE username = 'admin' OR '1'='1'
    # 这会返回所有用户！
    sql = f"SELECT * FROM users WHERE username = '{username}'"
    cursor = conn.cursor()
    cursor.execute(sql)  # 危险!
    return cursor.fetchone()


def dangerous_query_2(table_name: str, user_input: str):
    """更危险: 表名也不能参数化，只能拼接"""
    # 如果 user_input = "1; DROP TABLE users; --"
    # 执行后 users 表会被删除！
    sql = f"SELECT * FROM {table_name} WHERE id = {user_input}"
    cursor.execute(sql)  # 极度危险!
```

**安全代码（参数化查询）：**

```python
# -*- coding: utf-8 -*-
"""
SQL 注入防御: 参数化查询最佳实践
"""

# ---- pymysql 安全写法 ----
def safe_query_pymysql(username: str):
    """安全: 使用 %s 占位符，驱动会自动转义"""
    import pymysql
    conn = pymysql.connect(host="127.0.0.1", user="root",
                           password="xxx", database="demo_db")
    with conn.cursor() as cursor:
        # %s 是参数占位符，pymysql 会安全处理
        sql = "SELECT * FROM users WHERE username = %s"
        cursor.execute(sql, (username,))  # 注意: 传元组
        return cursor.fetchone()


# ---- SQLAlchemy text() 安全写法 ----
def safe_query_sqlalchemy(username: str):
    """安全: 使用 :name 命名参数"""
    from sqlalchemy import create_engine, text
    engine = create_engine("mysql+pymysql://root:xxx@127.0.0.1/demo_db")
    with engine.connect() as conn:
        stmt = text("SELECT * FROM users WHERE username = :uname")
        result = conn.execute(stmt, {"uname": username})
        return result.mappings().first()


# ---- SQLAlchemy ORM 安全写法 ----
def safe_query_orm(username: str):
    """安全: ORM 自动参数化"""
    from sqlalchemy import select
    from sqlalchemy.orm import Session
    with Session(engine) as session:
        stmt = select(User).where(User.username == username)
        return session.execute(stmt).scalars().first()


# ---- 动态表名/列名的安全处理 ----
def safe_dynamic_table(table_name: str):
    """
    表名和列名不能参数化，必须使用白名单验证
    """
    # 白名单: 只允许已知的表名
    ALLOWED_TABLES = {"users", "articles", "comments"}
    if table_name not in ALLOWED_TABLES:
        raise ValueError(f"非法表名: {table_name}")

    from sqlalchemy import text
    with engine.connect() as conn:
        # 表名经过白名单验证后才能安全拼接
        stmt = text(f"SELECT * FROM {table_name} LIMIT 10")
        result = conn.execute(stmt)
        return result.mappings().all()


# ---- LIKE 查询的安全处理 ----
def safe_like_search(keyword: str):
    """LIKE 查询也需要转义特殊字符"""
    # 用户输入中可能包含 % 和 _ 通配符
    # 需要转义这些字符，否则可能被用于通配符注入
    import re
    # 转义 LIKE 通配符
    escaped = re.escape(keyword).replace("\\%", "\\\\%").replace("\\_", "\\\\_")
    # 去掉 re.escape 添加的多余反斜杠（只针对 % 和 _）
    escaped = keyword.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")

    from sqlalchemy import text
    with engine.connect() as conn:
        # 使用 ESCAPE 子句指定转义字符
        stmt = text(
            "SELECT * FROM articles WHERE title LIKE :kw ESCAPE '\\\\'"
        )
        result = conn.execute(stmt, {"kw": f"%{escaped}%"})
        return result.mappings().all()
```

**安全原则总结：**

1. **值参数化**：所有用户输入的值（WHERE 条件值、INSERT 值等）必须用参数化查询，绝不拼接。
2. **表名/列名白名单**：表名和列名不能用参数化，必须用白名单验证。
3. **LIKE 转义**：用户输入中的 `%` 和 `_` 需要转义。
4. **ORM 更安全**：ORM 的 `where(Model.column == value)` 自动参数化，不容易出错。
5. **最小权限原则**：数据库用户只给必要的权限，即使注入成功也限制破坏范围。

### 8.4.4 性能对比：ORM 的 N+1 问题与预加载

N+1 是 ORM 最经典的性能陷阱。理解它、避免它是后端开发者的必修课。

**什么是 N+1 问题：**

假设查询 10 个用户，然后访问每个用户的文章列表。如果 ORM 对每个用户单独发一次查询文章的 SQL，总共发 1（查用户）+ 10（查文章）= 11 次查询，这就是 N+1。

**问题代码（N+1）：**

```python
# -*- coding: utf-8 -*-
"""
N+1 问题演示与解决方案
"""
from sqlalchemy import select
from sqlalchemy.orm import Session


# !!! 问题代码: N+1 查询 !!!
def bad_n_plus_one(session: Session):
    """每个用户的文章单独查询一次，导致 N+1"""
    # 第 1 次查询: 获取所有用户
    users = session.execute(select(User)).scalars().all()

    for user in users:
        # 遍历到每个用户的 articles 属性时，ORM 发起 1 次查询
        # 如果有 100 个用户，这里就是 100 次查询
        print(f"{user.username} 有 {len(user.articles)} 篇文章")
    # 总计: 1 + 100 = 101 次查询


# ---- 解决方案 1: selectinload（推荐） ----
def good_selectin(session: Session):
    """使用 selectinload 预加载，1 + 1 = 2 次查询"""
    from sqlalchemy.orm import selectinload
    stmt = (
        select(User)
        .options(selectinload(User.articles))  # 预加载文章
    )
    users = session.execute(stmt).scalars().all()

    for user in users:
        # 此时 articles 已经加载，不会发额外查询
        print(f"{user.username} 有 {len(user.articles)} 篇文章")
    # 总计: 2 次查询 (1 次查用户 + 1 次用 IN 查所有文章)


# ---- 解决方案 2: joinedload ----
def good_joinedload(session: Session):
    """使用 joinedload 预加载，1 次查询（JOIN）"""
    from sqlalchemy.orm import joinedload
    stmt = (
        select(User)
        .options(joinedload(User.articles))  # JOIN 预加载
    )
    users = session.execute(stmt).scalars().all()
    # 总计: 1 次查询 (JOIN 查询)
    for user in users:
        print(f"{user.username} 有 {len(user.articles)} 篇文章")


# ---- 解决方案 3: 手动 JOIN 查询 ----
def manual_join(session: Session):
    """手动 JOIN，适合只需要统计数据的场景"""
    from sqlalchemy import func
    stmt = (
        select(
            User.id,
            User.username,
            func.count(Article.id).label("article_count"),
        )
        .outerjoin(Article, Article.author_id == User.id)
        .group_by(User.id, User.username)
    )
    result = session.execute(stmt).all()
    for row in result:
        print(f"{row.username} 有 {row.article_count} 篇文章")
    # 总计: 1 次查询
```

**selectinload vs joinedload 对比：**

| 维度 | selectinload | joinedload |
|------|-------------|------------|
| 查询次数 | 1 + 1（主查询 + IN 查询） | 1（JOIN 查询） |
| SQL 复杂度 | 简单（两条独立 SQL） | 复杂（JOIN 可能产生笛卡尔积） |
| 数据量影响 | 适合一对多关系（多的一方数据量大） | 适合一对一或多对一关系 |
| 结果去重 | 不需要（主表无重复） | 需要 `unique()` 去重（JOIN 导致主表重复） |
| 分页友好 | 友好（主查询分页即可） | 不友好（JOIN 后分页逻辑复杂） |
| 推荐度 | 一对多首选 | 一对一/多对一首选 |

**选择指南：**

```python
# 一对多: 用 selectinload
stmt = select(User).options(selectinload(User.articles))

# 多对一/一对一: 用 joinedload
stmt = select(Article).options(joinedload(Article.author))

# 多级预加载: 链式使用
stmt = (
    select(User)
    .options(
        selectinload(User.articles)
        .selectinload(Article.comments)
        .joinedload(Comment.user)
    )
)
```

---

## 8.5 数据库迁移工具

数据库迁移工具用于管理数据库 Schema 的版本控制。就像 Git 管理代码变更一样，迁移工具管理表结构的变更。在 Python 生态中，Alembic 是 SQLAlchemy 的官方迁移工具，功能强大且生态成熟。

### 8.5.1 Alembic 基础：初始化

**安装：**

```bash
pip install alembic
```

**初始化项目：**

```bash
# 在项目根目录执行
alembic init alembic
```

执行后会在当前目录生成：

```
项目根目录/
  alembic.ini          # Alembic 配置文件
  alembic/             # 迁移目录
    env.py             # 迁移环境配置（需要修改）
    script.py.mako     # 迁移脚本模板
    versions/          # 迁移脚本存放目录（初始为空）
```

**配置 alembic.ini：**

打开 `alembic.ini`，找到 `sqlalchemy.url` 行，修改为你的数据库连接字符串：

```ini
# alembic.ini 中的关键配置
[alembic]
# 数据库连接字符串
sqlalchemy.url = mysql+pymysql://root:your_password@127.0.0.1:3306/demo_db?charset=utf8mb4

# 迁移脚本存放目录
script_location = alembic

# 模板前缀，用于新迁移脚本的文件名格式
# 例如: 001_create_users.py
file_template = %%(rev)s_%%(slug)s

# 时间戳格式
timezone = UTC
```

**配置 env.py：**

`env.py` 是 Alembic 的核心配置文件，需要修改它以连接你的模型定义。打开 `alembic/env.py`，做如下修改：

```python
# alembic/env.py 关键修改部分

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# ===== 新增: 导入你的模型 =====
import sys
import os

# 将项目根目录加入 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# 导入模型的 Base 和所有模型定义
# (确保所有模型在此处被 import，否则 autogenerate 无法检测到)
from models import Base  # 替换为你的实际模块路径
import models  # 触发所有模型定义的加载

# 设置 target_metadata，autogenerate 依赖它
target_metadata = Base.metadata
# ============================

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def run_migrations_offline() -> None:
    """离线模式: 生成 SQL 脚本但不执行"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """在线模式: 直接连接数据库执行迁移"""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # 比较类型变更（默认 False，建议开启）
            compare_type=True,
            # 比较服务端默认值变更
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### 8.5.2 自动生成迁移脚本（autogenerate）

Alembic 的 autogenerate 功能可以对比模型定义和数据库当前状态，自动生成迁移脚本。

```bash
# 自动生成迁移脚本
# -m 后面是迁移说明
alembic revision --autogenerate -m "create users table"
```

这会在 `alembic/versions/` 目录下生成一个 Python 文件，例如 `a1b2c3d4e5f6_create_users_table.py`。

**autogenerate 的能力与局限：**

**能做到的：**
- 新增/删除表
- 新增/删除/修改列
- 新增/删除索引
- 新增/删除外键约束
- 修改列的 nullability

**做不到或需要人工检查的：**
- 列重命名（会被识别为"删除旧列+新增新列"，数据会丢失）
- 列类型变更（如 VARCHAR(50) 改为 VARCHAR(100)，需要人工确认）
- 数据迁移/回填（需要手动编写）
- 自定义约束/触发器/存储过程
- 枚举类型变更

> **重要原则**：autogenerate 生成的脚本一定要人工审查后再执行。不要盲目信任自动生成的结果。

### 8.5.3 迁移脚本的编写

一个标准的迁移脚本包含两个函数：`upgrade()`（升级）和 `downgrade()`（降级）。

```python
"""create users table

Revision ID: a1b2c3d4e5f6
Revises:
Create Date: 2024-01-15 10:30:00
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = "a1b2c3d4e5f6"
down_revision = None  # 第一个迁移，down_revision 为 None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """升级: 创建 users 表"""
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(50), nullable=False),
        sa.Column("email", sa.String(100), nullable=False),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.current_timestamp()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
    )

    # 创建索引
    op.create_index("ix_users_email", "users", ["email"])


def downgrade() -> None:
    """降级: 删除 users 表"""
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
```

### 8.5.4 常见迁移操作

下面通过一个迁移脚本展示各种常见操作：

```python
"""add articles table and modify users

Revision ID: b2c3d4e5f6a1
Revises: a1b2c3d4e5f6
Create Date: 2024-01-16 14:00:00
"""
from alembic import op
import sqlalchemy as sa


revision = "b2c3d4e5f6a1"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ---- 1. 加字段 ----
    # 给 users 表加 phone 字段
    op.add_column("users", sa.Column("phone", sa.String(20), nullable=True))

    # ---- 2. 改类型 ----
    # 将 username 从 VARCHAR(50) 改为 VARCHAR(100)
    # 注意: MySQL 和 PostgreSQL 的 ALTER COLUMN 语法不同
    # Alembic 的 alter_column 会自动适配
    op.alter_column(
        "users", "username",
        existing_type=sa.String(50),
        type_=sa.String(100),
        nullable=False,
    )

    # ---- 3. 加索引 ----
    op.create_index("ix_users_phone", "users", ["phone"], unique=True)

    # ---- 4. 创建新表 ----
    op.create_table(
        "articles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("views", sa.Integer(), server_default="0"),
        sa.Column("author_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.current_timestamp()),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # ---- 5. 数据回填 ----
    # 给所有现有文章设置默认浏览量为 0（如果 server_default 未生效）
    op.execute("UPDATE articles SET views = 0 WHERE views IS NULL")

    # ---- 6. 批量操作（MySQL 不支持 ALTER COLUMN 单独操作，需要 batch mode） ----
    # batch_alter_table 用于 SQLite 和有特殊限制的数据库
    with op.batch_alter_table("articles") as batch_op:
        batch_op.alter_column("views", new_column_name="view_count",
                              existing_type=sa.Integer())


def downgrade() -> None:
    # 降级是升级的逆操作，顺序相反
    with op.batch_alter_table("articles") as batch_op:
        batch_op.alter_column("view_count", new_column_name="views",
                              existing_type=sa.Integer())

    op.drop_table("articles")
    op.drop_index("ix_users_phone", table_name="users")
    op.alter_column("users", "username",
                    existing_type=sa.String(100),
                    type_=sa.String(50),
                    nullable=False)
    op.drop_column("users", "phone")
```

### 8.5.5 迁移的最佳实践

**1. 每个变更一个脚本**

不要在一个迁移脚本中做太多事情。一个脚本只做一件事（如"添加 phone 字段"），这样如果某个迁移有问题，可以精确回滚。

**2. 向前兼容（Forward Compatibility）**

数据库变更需要先于代码部署。也就是说，数据库先迁移到新结构，新代码再上线。旧代码应该能在新数据库结构下正常工作。

**3. 生产环境安全发布**

```bash
# 第一步: 在测试环境执行迁移
alembic upgrade head

# 第二步: 生成 SQL 脚本，人工审查
alembic upgrade head --sql > migration.sql

# 第三步: 生产环境先备份
# mysqldump -u root -p demo_db > backup_$(date +%Y%m%d).sql

# 第四步: 生产环境执行迁移（建议在低峰期）
alembic upgrade head

# 如果出问题，回滚
alembic downgrade -1  # 回退一个版本
```

**4. 其他原则**

- 永远写 `downgrade()` 函数，确保可以回滚
- 不要修改已发布的迁移脚本（已执行过的迁移），新建一个修正迁移
- 在 CI/CD 中自动执行 `alembic upgrade head`（先在测试环境验证）
- 对于大型表的结构变更（加索引、改类型），需要在停机或低峰期执行

### 8.5.6 MySQL 与 PostgreSQL 的迁移差异

| 操作 | MySQL | PostgreSQL |
|------|-------|------------|
| 加列 | `ADD COLUMN` | `ADD COLUMN` |
| 加列+默认值 | 直接加（MySQL 8 支持快速加列） | `ADD COLUMN ... DEFAULT ...` |
| 改列类型 | `MODIFY COLUMN` | `ALTER COLUMN ... TYPE` |
| 加索引（大表） | `ALTER TABLE ... ADD INDEX`（锁表） | `CREATE INDEX CONCURRENTLY`（不锁表） |
| 重命名列 | `CHANGE COLUMN` 或 `RENAME COLUMN` | `RENAME COLUMN` |
| 枚举类型 | 使用 VARCHAR + CHECK | 使用原生 ENUM 类型 |
| 批量操作 | 不需要 batch mode | 不需要 batch mode |
| batch_alter_table | 一般不需要 | 一般不需要（SQLite 才需要） |

**PostgreSQL 特有: 不锁表加索引**

```python
def upgrade() -> None:
    # PostgreSQL 支持并发建索引（不阻塞写入）
    # 注意: Alembic 的 op.create_index 需要特殊处理
    op.execute("CREATE INDEX CONCURRENTLY ix_users_email ON users (email)")


def downgrade() -> None:
    op.execute("DROP INDEX CONCURRENTLY ix_users_email")
```

> 注意：`CREATE INDEX CONCURRENTLY` 不能在事务中执行。需要在 `env.py` 中配置 `transaction_per_migration = False`，或者在迁移函数中手动控制事务。

### 8.5.7 实战：从零搭建带 Alembic 迁移的 Python 项目

下面是一个完整的项目结构示例。

**项目目录结构：**

```
my_project/
  alembic.ini
  alembic/
    env.py
    script.py.mako
    versions/
  models/
    __init__.py
    base.py          # Base 定义
    user.py          # User 模型
    article.py       # Article 模型
  config.py
  main.py
  requirements.txt
```

**models/base.py：**

```python
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """所有模型的基类"""
    pass
```

**models/user.py：**

```python
from sqlalchemy import String, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from datetime import datetime
from models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    age: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )
```

**models/article.py：**

```python
from sqlalchemy import String, Integer, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
from datetime import datetime
from models.base import Base


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[Optional[str]] = mapped_column(Text)
    author_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )
```

**models/\_\_init\_\_.py：**

```python
# 确保所有模型都被导入，这样 Alembic 的 autogenerate 才能检测到
from models.base import Base
from models.user import User
from models.article import Article

__all__ = ["Base", "User", "Article"]
```

**config.py：**

```python
import os

# 从环境变量读取配置，避免硬编码密码
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:your_password@127.0.0.1:3306/demo_db?charset=utf8mb4"
)
```

**完整操作流程（命令行执行）：**

```bash
# 1. 安装依赖
pip install sqlalchemy pymysql alembic

# 2. 初始化 Alembic
alembic init alembic

# 3. 修改 alembic.ini 中的 sqlalchemy.url
#    修改 alembic/env.py 导入模型（参考 8.5.1）

# 4. 自动生成第一个迁移
alembic revision --autogenerate -m "create users and articles tables"

# 5. 审查生成的迁移脚本（在 alembic/versions/ 目录下）

# 6. 执行迁移
alembic upgrade head

# 7. 验证: 查看当前版本
alembic current

# 8. 后续修改模型后，重复步骤 4-6
```

**常用 Alembic 命令汇总：**

```bash
# 查看当前版本
alembic current

# 查看历史记录
alembic history

# 升级到最新
alembic upgrade head

# 升级到指定版本
alembic upgrade a1b2c3d4e5f6

# 回退一个版本
alembic downgrade -1

# 回退到指定版本
alembic downgrade a1b2c3d4e5f6

# 生成 SQL 脚本（不执行，仅查看）
alembic upgrade head --sql

# 手动创建空迁移（不自动生成）
alembic revision -m "add some column manually"
```

---

## 8.6 FastAPI + 数据库集成

这是本章的实战高潮部分。我们将搭建一个完整的 RESTful API 项目，集成异步 SQLAlchemy 和 FastAPI 的依赖注入系统，实现用户 CRUD 和订单查询接口。

### 8.6.1 FastAPI 依赖注入 + 数据库会话管理

FastAPI 的依赖注入系统是管理数据库会话的最佳方式。每个请求获取一个独立的 Session，请求结束后自动归还到连接池。

**核心思路：**

```
请求进入 -> 依赖注入获取 AsyncSession -> 执行业务逻辑 -> 返回响应 -> 依赖注入关闭 Session

如果出错 -> 异常处理 -> Session 自动回滚 -> 返回错误响应
```

### 8.6.2 项目结构

```
fastapi_demo/
  main.py              # 应用入口
  config.py            # 配置
  database.py           # 数据库连接与会话
  models.py            # SQLAlchemy ORM 模型
  schemas.py           # Pydantic 模型（请求/响应 schema）
  crud.py              # 数据库操作封装
  api/
    __init__.py
    users.py            # 用户相关路由
    orders.py           # 订单相关路由
  requirements.txt
```

### 8.6.3 完整项目代码

**requirements.txt：**

```
fastapi==0.110.0
uvicorn[standard]==0.29.0
sqlalchemy[asyncio]==2.0.29
asyncpg==0.29.0
pydantic==2.6.4
python-dotenv==1.0.1
```

**config.py：**

```python
# -*- coding: utf-8 -*-
"""应用配置"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """全局配置"""
    # 数据库连接（默认 PostgreSQL，也可改为 MySQL）
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:your_password@127.0.0.1:5432/demo_db"
    )
    # MySQL 备选:
    # DATABASE_URL = "mysql+aiomysql://root:your_password@127.0.0.1:3306/demo_db"

    PROJECT_NAME: str = "FastAPI Demo"
    API_V1_PREFIX: str = "/api/v1"

    # 分页默认值
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100


settings = Settings()
```

**database.py：**

```python
# -*- coding: utf-8 -*-
"""
数据库连接与会话管理
提供异步引擎和异步 Session 工厂
"""
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from config import settings


# 异步引擎（全局唯一）
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,              # 设为 True 可打印 SQL，调试用
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,
    pool_pre_ping=True,     # 使用前检查连接
)

# 异步 Session 工厂
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # 异步环境必须关闭
    autoflush=False,
)


async def get_db() -> AsyncSession:
    """
    数据库会话依赖
    每个 HTTP 请求获取一个独立的 Session
    请求结束后自动关闭（归还连接到连接池）
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            # 注意: 不在这里 commit，让业务层决定何时提交
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

**models.py：**

```python
# -*- coding: utf-8 -*-
"""
SQLAlchemy ORM 模型
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from sqlalchemy import (
    String, Integer, BigInteger, Numeric, Text, DateTime,
    ForeignKey, func,
)
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column, relationship,
)


class Base(DeclarativeBase):
    pass


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(100))
    age: Mapped[Optional[int]] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )

    # 关系
    orders: Mapped[List["Order"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class Order(Base):
    """订单表"""
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    order_no: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE")
    )
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    remark: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )

    # 关系
    user: Mapped["User"] = relationship(back_populates="orders")
    items: Mapped[List["OrderItem"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Order(id={self.id}, order_no='{self.order_no}')>"


class OrderItem(Base):
    """订单明细表"""
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("orders.id", ondelete="CASCADE")
    )
    product_name: Mapped[str] = mapped_column(String(200))
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    # 关系
    order: Mapped["Order"] = relationship(back_populates="items")

    def __repr__(self):
        return f"<OrderItem(id={self.id}, product='{self.product_name}')>"
```

**schemas.py：**

```python
# -*- coding: utf-8 -*-
"""
Pydantic 模型（请求/响应 schema）
与 ORM 模型分离，职责清晰:
- models.py: 数据库表结构定义
- schemas.py: API 请求/响应数据格式
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ============================================================
# 用户相关 Schema
# ============================================================

class UserBase(BaseModel):
    """用户基础字段（创建和更新共用）"""
    username: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=100)
    age: Optional[int] = Field(None, ge=0, le=150)


class UserCreate(UserBase):
    """创建用户请求"""
    password: str = Field(..., min_length=6, max_length=100)


class UserUpdate(BaseModel):
    """更新用户请求（所有字段可选）"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    age: Optional[int] = Field(None, ge=0, le=150)
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """用户响应（包含数据库生成的字段）"""
    model_config = ConfigDict(from_attributes=True)  # 从 ORM 对象读取属性

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserWithOrders(UserResponse):
    """用户及其订单信息"""
    model_config = ConfigDict(from_attributes=True)
    orders: List["OrderResponse"] = []


# ============================================================
# 订单相关 Schema
# ============================================================

class OrderItemBase(BaseModel):
    product_name: str = Field(..., max_length=200)
    quantity: int = Field(..., gt=0)
    unit_price: Decimal = Field(..., gt=0)


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemResponse(OrderItemBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class OrderBase(BaseModel):
    order_no: str = Field(..., max_length=50)
    remark: Optional[str] = None


class OrderCreate(OrderBase):
    """创建订单请求"""
    user_id: int
    items: List[OrderItemCreate] = Field(..., min_length=1)


class OrderResponse(OrderBase):
    """订单响应"""
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    total_amount: Decimal
    status: str
    created_at: datetime
    items: List[OrderItemResponse] = []


# 解决前向引用
UserWithOrders.model_rebuild()


# ============================================================
# 通用 Schema
# ============================================================

class PaginatedResponse(BaseModel):
    """通用分页响应"""
    total: int
    page: int
    page_size: int
    items: List  # 泛型，使用时具体指定


class MessageResponse(BaseModel):
    """通用消息响应"""
    message: str
```

**crud.py：**

```python
# -*- coding: utf-8 -*-
"""
数据库 CRUD 操作封装
所有数据库操作都在这里，API 路由只调用这些函数
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Tuple

from sqlalchemy import select, func, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError

import models
import schemas


# ============================================================
# 用户 CRUD
# ============================================================

async def get_user(db: AsyncSession, user_id: int) -> Optional[models.User]:
    """按 ID 查询用户"""
    return await db.get(models.User, user_id)


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[models.User]:
    """按用户名查询"""
    stmt = select(models.User).where(models.User.username == username)
    result = await db.execute(stmt)
    return result.scalars().first()


async def get_user_with_orders(db: AsyncSession, user_id: int) -> Optional[models.User]:
    """查询用户及其订单（预加载）"""
    stmt = (
        select(models.User)
        .options(selectinload(models.User.orders))
        .where(models.User.id == user_id)
    )
    result = await db.execute(stmt)
    return result.scalars().first()


async def get_users(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    is_active: Optional[bool] = None,
) -> Tuple[List[models.User], int]:
    """
    分页查询用户列表
    返回: (用户列表, 总数)
    """
    # 构建基础查询
    base_stmt = select(models.User)
    count_stmt = select(func.count(models.User.id))

    # 条件过滤
    if is_active is not None:
        base_stmt = base_stmt.where(models.User.is_active == is_active)
        count_stmt = count_stmt.where(models.User.is_active == is_active)

    # 获取总数
    total = await db.execute(count_stmt)
    total = total.scalar()

    # 分页
    offset = (page - 1) * page_size
    stmt = base_stmt.order_by(models.User.id.desc()).offset(offset).limit(page_size)
    result = await db.execute(stmt)
    users = list(result.scalars().all())

    return users, total


async def create_user(db: AsyncSession, user: schemas.UserCreate) -> models.User:
    """创建用户"""
    db_user = models.User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        age=user.age,
    )
    db.add(db_user)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise ValueError("用户名或邮箱已存在")
    await db.refresh(db_user)
    return db_user


async def update_user(
    db: AsyncSession,
    user_id: int,
    user_update: schemas.UserUpdate,
) -> Optional[models.User]:
    """更新用户（部分字段）"""
    db_user = await db.get(models.User, user_id)
    if not db_user:
        return None

    # 只更新非 None 的字段
    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)

    await db.commit()
    await db.refresh(db_user)
    return db_user


async def delete_user(db: AsyncSession, user_id: int) -> bool:
    """删除用户（级联删除订单）"""
    db_user = await db.get(models.User, user_id)
    if not db_user:
        return False
    await db.delete(db_user)
    await db.commit()
    return True


# ============================================================
# 订单 CRUD
# ============================================================

async def create_order(
    db: AsyncSession,
    order: schemas.OrderCreate,
) -> models.Order:
    """创建订单（含明细）"""
    # 检查用户是否存在
    user = await get_user(db, order.user_id)
    if not user:
        raise ValueError("用户不存在")

    # 计算总金额
    total = sum(
        item.quantity * item.unit_price
        for item in order.items
    )

    # 创建订单
    db_order = models.Order(
        order_no=order.order_no,
        user_id=order.user_id,
        total_amount=total,
        status="pending",
        remark=order.remark,
    )
    db.add(db_order)
    await db.flush()  # 获取自增 ID

    # 创建订单明细
    for item in order.items:
        db_item = models.OrderItem(
            order_id=db_order.id,
            product_name=item.product_name,
            quantity=item.quantity,
            unit_price=item.unit_price,
        )
        db.add(db_item)

    await db.commit()
    await db.refresh(db_order)
    return db_order


async def get_order_with_items(
    db: AsyncSession,
    order_id: int,
) -> Optional[models.Order]:
    """查询订单及其明细（预加载）"""
    stmt = (
        select(models.Order)
        .options(selectinload(models.Order.items))
        .where(models.Order.id == order_id)
    )
    result = await db.execute(stmt)
    return result.scalars().first()


async def get_orders_by_user(
    db: AsyncSession,
    user_id: int,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[models.Order], int]:
    """查询用户的订单列表（分页）"""
    # 总数
    count_stmt = select(func.count(models.Order.id)).where(
        models.Order.user_id == user_id
    )
    total = (await db.execute(count_stmt)).scalar()

    # 分页查询
    offset = (page - 1) * page_size
    stmt = (
        select(models.Order)
        .where(models.Order.user_id == user_id)
        .order_by(models.Order.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    orders = list(result.scalars().all())

    return orders, total


async def update_order_status(
    db: AsyncSession,
    order_id: int,
    status: str,
) -> Optional[models.Order]:
    """更新订单状态"""
    # 使用 Core 原子更新，避免并发问题
    stmt = (
        update(models.Order)
        .where(models.Order.id == order_id)
        .values(status=status)
    )
    await db.execute(stmt)
    await db.commit()
    return await db.get(models.Order, order_id)
```

**api/users.py：**

```python
# -*- coding: utf-8 -*-
"""
用户相关 API 路由
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

import schemas
import crud
from database import get_db
from config import settings


router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/",
    response_model=schemas.UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建用户",
)
async def create_user(
    user: schemas.UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    创建新用户:
    - username: 唯一用户名
    - email: 唯一邮箱
    - age: 可选年龄
    """
    # 检查用户名是否已存在
    existing = await crud.get_user_by_username(db, username=user.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="用户名已存在",
        )
    try:
        return await crud.create_user(db, user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/{user_id}",
    response_model=schemas.UserResponse,
    summary="查询用户详情",
)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    """根据 ID 查询用户信息"""
    user = await crud.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )
    return user


@router.get(
    "/{user_id}/orders",
    response_model=schemas.UserWithOrders,
    summary="查询用户及其订单",
)
async def get_user_with_orders(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    """查询用户信息及其所有订单"""
    user = await crud.get_user_with_orders(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )
    return user


@router.get(
    "/",
    response_model=schemas.PaginatedResponse,
    summary="分页查询用户列表",
)
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    is_active: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """
    分页查询用户列表:
    - page: 页码（从 1 开始）
    - page_size: 每页数量
    - is_active: 过滤激活状态
    """
    users, total = await crud.get_users(db, page, page_size, is_active)
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": users,
    }


@router.patch(
    "/{user_id}",
    response_model=schemas.UserResponse,
    summary="更新用户",
)
async def update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: AsyncSession = Depends(get_db),
):
    """部分更新用户信息（PATCH 语义: 只更新提供的字段）"""
    user = await crud.update_user(db, user_id, user_update)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )
    return user


@router.delete(
    "/{user_id}",
    response_model=schemas.MessageResponse,
    summary="删除用户",
)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    """删除用户（级联删除其订单）"""
    success = await crud.delete_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )
    return {"message": "用户已删除"}
```

**api/orders.py：**

```python
# -*- coding: utf-8 -*-
"""
订单相关 API 路由
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

import schemas
import crud
from database import get_db
from config import settings


router = APIRouter(prefix="/orders", tags=["orders"])


@router.post(
    "/",
    response_model=schemas.OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建订单",
)
async def create_order(
    order: schemas.OrderCreate,
    db: AsyncSession = Depends(get_db),
):
    """创建订单（含订单明细）"""
    try:
        return await crud.create_order(db, order)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/{order_id}",
    response_model=schemas.OrderResponse,
    summary="查询订单详情",
)
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
):
    """查询订单及其明细"""
    order = await crud.get_order_with_items(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在",
        )
    return order


@router.get(
    "/user/{user_id}",
    response_model=schemas.PaginatedResponse,
    summary="查询用户订单列表",
)
async def list_user_orders(
    user_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    db: AsyncSession = Depends(get_db),
):
    """分页查询指定用户的所有订单"""
    # 先检查用户是否存在
    user = await crud.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )

    orders, total = await crud.get_orders_by_user(db, user_id, page, page_size)
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": orders,
    }


@router.patch(
    "/{order_id}/status",
    response_model=schemas.OrderResponse,
    summary="更新订单状态",
)
async def update_order_status_api(
    order_id: int,
    new_status: str = Query(..., description="新状态: pending/paid/shipped/done/cancelled"),
    db: AsyncSession = Depends(get_db),
):
    """更新订单状态"""
    valid_statuses = {"pending", "paid", "shipped", "done", "cancelled"}
    if new_status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效状态，可选: {', '.join(valid_statuses)}",
        )
    order = await crud.update_order_status(db, order_id, new_status)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在",
        )
    return order
```

**api/\_\_init\_\_.py：**

```python
from api.users import router as users_router
from api.orders import router as orders_router

__all__ = ["users_router", "orders_router"]
```

**main.py：**

```python
# -*- coding: utf-8 -*-
"""
FastAPI 应用入口
启动命令: uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from config import settings
from database import engine
from models import Base
from api import users_router, orders_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    启动时执行，关闭时执行
    """
    # ---- 启动阶段 ----
    # 生产环境用 Alembic 管理表结构，这里仅用于开发环境自动建表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("[STARTUP] 数据库表已准备就绪")

    yield  # 应用运行期间

    # ---- 关闭阶段 ----
    await engine.dispose()
    print("[SHUTDOWN] 数据库连接池已关闭")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="FastAPI + SQLAlchemy 2.0 异步数据库操作示例",
    version="1.0.0",
    lifespan=lifespan,
)

# 注册路由
app.include_router(users_router, prefix=settings.API_V1_PREFIX)
app.include_router(orders_router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["health"])
async def root():
    """健康检查"""
    return {"status": "ok", "message": "FastAPI Demo is running"}


@app.get("/health", tags=["health"])
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "service": settings.PROJECT_NAME}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
```

### 8.6.4 运行与测试

**启动应用：**

```bash
# 设置数据库环境变量（可选，也可以直接修改 config.py）
set DATABASE_URL=postgresql+asyncpg://postgres:your_password@127.0.0.1:5432/demo_db

# 启动
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

启动后访问 `http://localhost:8000/docs` 可以看到 Swagger UI 文档，所有 API 接口都可以在页面上测试。

**测试 API（命令行示例）：**

```bash
# 创建用户
curl -X POST http://localhost:8000/api/v1/users/ ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"alice\",\"email\":\"alice@example.com\",\"age\":25,\"password\":\"secret123\"}"

# 查询用户列表
curl http://localhost:8000/api/v1/users/?page=1&page_size=10

# 查询用户详情
curl http://localhost:8000/api/v1/users/1

# 更新用户
curl -X PATCH http://localhost:8000/api/v1/users/1 ^
  -H "Content-Type: application/json" ^
  -d "{\"age\":26,\"full_name\":\"Alice Zhang\"}"

# 创建订单
curl -X POST http://localhost:8000/api/v1/orders/ ^
  -H "Content-Type: application/json" ^
  -d "{\"order_no\":\"ORD20240115001\",\"user_id\":1,\"items\":[{\"product_name\":\"Python Book\",\"quantity\":2,\"unit_price\":59.90}]}"

# 查询用户订单
curl http://localhost:8000/api/v1/orders/user/1

# 更新订单状态
curl -X PATCH "http://localhost:8000/api/v1/orders/1/status?new_status=paid"

# 删除用户
curl -X DELETE http://localhost:8000/api/v1/users/1
```

### 8.6.5 关键设计说明

**1. 事务在请求生命周期中的管理**

在 `database.py` 的 `get_db()` 中，Session 的生命周期与请求一致。事务策略如下：

- CRUD 层负责在写操作后调用 `commit()`
- 如果请求处理过程中抛出异常，`get_db()` 的 `except` 块会 `rollback()`
- 读操作不 commit，保持只读语义

如果需要在一个请求中执行多个操作并保证原子性，可以在路由层显式管理事务：

```python
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from database import get_db


@router.post("/transfer")
async def transfer(
    from_id: int,
    to_id: int,
    amount: Decimal,
    db: AsyncSession = Depends(get_db),
):
    """转账: 要么全部成功，要么全部失败"""
    try:
        # 扣款
        await db.execute(
            update(Account).where(Account.id == from_id)
            .values(balance=Account.balance - amount)
        )
        # 加款
        await db.execute(
            update(Account).where(Account.id == to_id)
            .values(balance=Account.balance + amount)
        )
        # 一次性提交
        await db.commit()
        return {"message": "转账成功"}
    except Exception:
        await db.rollback()
        raise HTTPException(400, "转账失败")
```

**2. Pydantic 模型与 ORM 模型的分离与转换**

这是前端转后端时容易混淆的概念。核心原则是**职责分离**：

- `models.py`（ORM 模型）：定义数据库表结构，与数据库 Schema 一一对应
- `schemas.py`（Pydantic 模型）：定义 API 的请求和响应格式，与数据库结构解耦

两者通过 `model_config = ConfigDict(from_attributes=True)` 桥接，Pydantic 可以直接从 ORM 对象读取属性：

```python
# Pydantic 模型
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    email: str

# 转换: ORM 对象 -> Pydantic 对象
orm_user = await db.get(User, 1)  # ORM 对象
response = UserResponse.model_validate(orm_user)  # 自动转换
```

**分离的好处：**
- 数据库字段可以比 API 暴露的字段多（如 `password` 不暴露）
- API 可以有计算字段（如 `full_name` 由 `first_name + last_name` 拼接）
- 请求和响应用不同的模型（创建请求不需要 `id`，响应用户不包含 `password`）
- 修改数据库结构不影响 API 契约

**3. 分页查询的通用封装**

上面的 `list_users` 和 `list_user_orders` 都使用了分页，模式一致。可以封装一个通用的分页工具：

```python
# -*- coding: utf-8 -*-
"""
通用分页工具
"""
from typing import TypeVar, Generic, List, Tuple, Optional
from dataclasses import dataclass

from sqlalchemy import select, func, Select
from sqlalchemy.ext.asyncio import AsyncSession


T = TypeVar("T")


@dataclass
class Page(Generic[T]):
    """分页结果"""
    items: List[T]
    total: int
    page: int
    page_size: int

    @property
    def total_pages(self) -> int:
        return (self.total + self.page_size - 1) // self.page_size if self.page_size else 0


async def paginate(
    db: AsyncSession,
    stmt: Select,
    page: int = 1,
    page_size: int = 20,
) -> Page:
    """
    通用分页查询
    用法:
        stmt = select(User).where(User.is_active == True)
        result = await paginate(db, stmt, page=1, page_size=10)
    """
    # 获取总数
    count_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
    total = (await db.execute(count_stmt)).scalar()

    # 分页
    offset = (page - 1) * page_size
    paginated_stmt = stmt.offset(offset).limit(page_size)
    result = await db.execute(paginated_stmt)
    items = list(result.scalars().all())

    return Page(items=items, total=total, page=page, page_size=page_size)


# 使用示例:
# async def list_users(db, page, page_size):
#     stmt = select(User).order_by(User.id.desc())
#     return await paginate(db, stmt, page, page_size)
```

---

## 本章总结

本章从底层驱动到上层框架，完整覆盖了 Python 数据库操作的方方面面：

1. **驱动层**（8.1-8.2）：掌握了 MySQL 和 PostgreSQL 的同步/异步驱动选择，理解了连接池的配置和使用。

2. **ORM 层**（8.3）：深入学习了 SQLAlchemy 2.0 的新语法（DeclarativeBase、Mapped、select()），掌握了模型定义、关系映射、查询 API、会话管理和异步操作。这是后端 Python 开发者每天都要用的核心技能。

3. **工程实践**（8.4-8.5）：学会了 ORM 与原生 SQL 的选择策略、SQL 注入防御、N+1 问题与预加载策略，以及使用 Alembic 进行数据库迁移管理。

4. **项目集成**（8.6）：搭建了完整的 FastAPI + 异步数据库项目，理解了依赖注入管理会话、Pydantic 与 ORM 模型分离、事务管理和分页封装。

**给前端开发者的最后建议：**

- 如果你用过 Node.js 的 Prisma 或 TypeORM，SQLAlchemy 2.0 的概念是相通的，但 API 更底层、更灵活
- 先掌握同步操作（8.1-8.3 的同步部分），再学异步（AsyncSession）
- 在实际项目中，推荐直接使用 8.6 的项目结构作为起点
- 数据库操作的核心难点不在语法，而在 N+1 问题、事务管理、迁移策略这些工程问题
- 多写、多测、多用 `echo=True` 观察 SQL 输出，是掌握 ORM 的最佳方式
