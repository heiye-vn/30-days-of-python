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
