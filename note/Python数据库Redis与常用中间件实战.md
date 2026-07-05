# Python 数据库、Redis 与常用中间件实战

> 真实项目里的 Python 不只是写函数和脚本，还要和数据库、缓存、消息队列、对象存储、搜索服务等基础设施协作。本文以 Python 为基础，整理 MySQL、PostgreSQL、Redis、ORM 工具和常见中间件的日常命令、核心概念，以及它们在 Web API、后台任务、数据处理项目中的典型用法。

---

## 一、为什么要学数据库和中间件

很多初学项目一开始会把数据放在内存、JSON 文件或 CSV 文件里：

```python
users = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"},
]
```

这样适合练习语法，但真实项目会很快遇到问题：

- 程序重启后，内存数据会丢失。
- 多个进程同时写文件时容易冲突。
- 数据量变大后，按条件查询会越来越慢。
- 很难保证数据一致性，例如订单创建成功但库存扣减失败。
- 很难支持多用户并发访问。

数据库和中间件解决的就是这些问题。

常见分工如下：

- **MySQL / PostgreSQL**：保存长期数据，例如用户、订单、文章、权限、支付记录。
- **Redis**：做缓存、分布式锁、验证码、排行榜、限流、简单消息队列。
- **ORM**：用 Python 类和对象操作数据库，减少手写 SQL 的重复劳动。
- **Alembic / Django migrations**：管理数据库表结构变更。
- **Celery / RQ / Dramatiq**：处理异步后台任务，例如发邮件、生成报表、调用第三方接口。
- **RabbitMQ / Kafka**：做更专业的消息传递、事件流、系统解耦。
- **Elasticsearch / OpenSearch**：做全文搜索、日志检索、复杂筛选。
- **MinIO / S3**：存储图片、视频、文档等对象文件。

一句话理解：**Python 写业务逻辑，数据库保存状态，中间件提升性能、可靠性和系统协作能力。**

---

## 二、关系型数据库基础

### 2.1 数据库、表、行、列

关系型数据库可以理解为很多张表的集合。

例如用户表：

```text
users
├── id
├── username
├── email
├── password_hash
├── created_at
└── updated_at
```

每一行是一条用户记录：

```text
id | username | email             | created_at
1  | alice    | alice@example.com | 2026-07-05 10:00:00
2  | bob      | bob@example.com   | 2026-07-05 10:05:00
```

常见术语：

- **database**：数据库，存放一组表。
- **table**：表，存放同一类数据。
- **row**：行，一条记录。
- **column**：列，一个字段。
- **primary key**：主键，唯一标识一条记录，常用 `id`。
- **foreign key**：外键，表示表与表之间的关系。
- **index**：索引，用来加速查询。
- **transaction**：事务，保证一组操作要么全部成功，要么全部失败。

### 2.2 常见 SQL 分类

SQL 命令大致可以分为几类：

```sql
-- DDL：定义表结构
CREATE TABLE users (
    id BIGINT PRIMARY KEY,
    username VARCHAR(50) NOT NULL
);

-- DML：操作数据
INSERT INTO users (id, username) VALUES (1, 'alice');
UPDATE users SET username = 'Alice' WHERE id = 1;
DELETE FROM users WHERE id = 1;

-- DQL：查询数据
SELECT id, username FROM users WHERE id = 1;

-- DCL：权限控制
GRANT SELECT ON users TO app_user;

-- TCL：事务控制
BEGIN;
COMMIT;
ROLLBACK;
```

实际项目里最常写的是 `SELECT`、`INSERT`、`UPDATE`、`DELETE`，最容易被忽略但非常重要的是索引和事务。

---

## 三、MySQL 常用操作

### 3.1 Docker 启动 MySQL

学习阶段推荐用 Docker 起一个本地 MySQL：

```bash
docker run --name mysql-dev \
  -e MYSQL_ROOT_PASSWORD=rootpass \
  -e MYSQL_DATABASE=app_db \
  -e MYSQL_USER=app_user \
  -e MYSQL_PASSWORD=app_pass \
  -p 3306:3306 \
  -d mysql:8
```

查看容器：

```bash
docker ps
```

进入 MySQL 命令行：

```bash
docker exec -it mysql-dev mysql -uroot -prootpass
```

连接指定数据库：

```bash
docker exec -it mysql-dev mysql -uapp_user -papp_pass app_db
```

停止和启动：

```bash
docker stop mysql-dev
docker start mysql-dev
```

### 3.2 用户、数据库、权限

查看数据库：

```sql
SHOW DATABASES;
```

创建数据库：

```sql
CREATE DATABASE app_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

创建用户：

```sql
CREATE USER 'app_user'@'%' IDENTIFIED BY 'app_pass';
```

授权：

```sql
GRANT ALL PRIVILEGES ON app_db.* TO 'app_user'@'%';
FLUSH PRIVILEGES;
```

查看当前用户：

```sql
SELECT USER(), CURRENT_USER();
```

实际项目建议：

- 不要让应用直接使用 `root` 用户。
- 每个项目单独建数据库和用户。
- 生产环境按最小权限授权，例如只给应用库权限，不给全局权限。
- 密码放到环境变量或密钥服务里，不要写死在代码中。

### 3.3 表结构操作

创建用户表：

```sql
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

查看表：

```sql
SHOW TABLES;
```

查看表结构：

```sql
DESC users;
```

查看建表语句：

```sql
SHOW CREATE TABLE users;
```

增加字段：

```sql
ALTER TABLE users ADD COLUMN last_login_at DATETIME NULL;
```

修改字段：

```sql
ALTER TABLE users MODIFY COLUMN username VARCHAR(80) NOT NULL;
```

删除字段：

```sql
ALTER TABLE users DROP COLUMN last_login_at;
```

删除表：

```sql
DROP TABLE users;
```

生产环境注意：

- `ALTER TABLE` 可能锁表，大表变更要谨慎。
- 表结构变更应该通过迁移工具管理，不要靠手工记忆。
- 删除字段、删除表前要确认是否还有代码依赖。

### 3.4 增删改查

插入数据：

```sql
INSERT INTO users (username, email, password_hash)
VALUES ('alice', 'alice@example.com', 'hash-value');
```

查询数据：

```sql
SELECT id, username, email
FROM users
WHERE is_active = TRUE
ORDER BY id DESC
LIMIT 20;
```

更新数据：

```sql
UPDATE users
SET email = 'new-alice@example.com'
WHERE id = 1;
```

删除数据：

```sql
DELETE FROM users WHERE id = 1;
```

实际项目里，删除通常分两类：

- **物理删除**：真的执行 `DELETE`，数据从表里移除。
- **软删除**：增加 `deleted_at` 或 `is_deleted` 字段，只标记删除。

软删除示例：

```sql
ALTER TABLE users ADD COLUMN deleted_at DATETIME NULL;

UPDATE users
SET deleted_at = CURRENT_TIMESTAMP
WHERE id = 1;

SELECT *
FROM users
WHERE deleted_at IS NULL;
```

用户、订单、支付、审计日志等重要数据通常不建议随意物理删除。

### 3.5 索引

索引用来提升查询速度。

创建普通索引：

```sql
CREATE INDEX idx_users_created_at ON users (created_at);
```

创建唯一索引：

```sql
CREATE UNIQUE INDEX idx_users_email ON users (email);
```

创建联合索引：

```sql
CREATE INDEX idx_users_active_created ON users (is_active, created_at);
```

查看索引：

```sql
SHOW INDEX FROM users;
```

删除索引：

```sql
DROP INDEX idx_users_created_at ON users;
```

使用 `EXPLAIN` 查看查询计划：

```sql
EXPLAIN
SELECT id, username
FROM users
WHERE email = 'alice@example.com';
```

索引建议：

- 经常出现在 `WHERE`、`JOIN`、`ORDER BY` 中的字段适合建索引。
- 低区分度字段不一定适合单独建索引，例如只有 true / false 的字段。
- 联合索引要注意最左前缀原则，例如 `(status, created_at)` 可以帮助按 `status` 查询。
- 索引不是越多越好，写入时也要维护索引，索引过多会拖慢写入。

### 3.6 事务

事务适合处理必须一起成功或一起失败的操作。

例如创建订单并扣减库存：

```sql
BEGIN;

INSERT INTO orders (user_id, total_amount, status)
VALUES (1, 19900, 'created');

UPDATE products
SET stock = stock - 1
WHERE id = 100 AND stock > 0;

COMMIT;
```

如果中间出错：

```sql
ROLLBACK;
```

实际项目里要特别注意：

- 事务不要包太久，避免长时间占用锁。
- 事务里不要做慢操作，例如请求外部 HTTP 接口。
- 高并发扣库存要加条件，例如 `WHERE stock > 0`。
- 事务失败后要回滚，并把错误抛给调用方。

---

## 四、PostgreSQL 常用操作

### 4.1 Docker 启动 PostgreSQL

```bash
docker run --name postgres-dev \
  -e POSTGRES_DB=app_db \
  -e POSTGRES_USER=app_user \
  -e POSTGRES_PASSWORD=app_pass \
  -p 5432:5432 \
  -d postgres:16
```

进入 `psql`：

```bash
docker exec -it postgres-dev psql -U app_user -d app_db
```

常用 `psql` 元命令：

```sql
\l          -- 查看数据库
\c app_db   -- 切换数据库
\dt         -- 查看表
\d users    -- 查看表结构
\du         -- 查看用户和角色
\q          -- 退出
```

这些命令是 `psql` 客户端命令，不是标准 SQL，所以通常以反斜杠开头。

### 4.2 数据库、用户、权限

创建数据库：

```sql
CREATE DATABASE app_db;
```

创建用户：

```sql
CREATE USER app_user WITH PASSWORD 'app_pass';
```

授权：

```sql
GRANT ALL PRIVILEGES ON DATABASE app_db TO app_user;
```

在指定库里授权 schema：

```sql
GRANT USAGE, CREATE ON SCHEMA public TO app_user;
```

PostgreSQL 里常见层级是：

```text
server
└── database
    └── schema
        └── table
```

默认 schema 通常是 `public`。大型项目可能会用多个 schema 隔离模块，例如 `auth.users`、`billing.orders`。

### 4.3 表结构操作

创建用户表：

```sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

PostgreSQL 没有 MySQL 那种 `ON UPDATE CURRENT_TIMESTAMP` 语法，常见做法是在应用层更新 `updated_at`，或者用触发器。

增加字段：

```sql
ALTER TABLE users ADD COLUMN last_login_at TIMESTAMPTZ;
```

修改字段：

```sql
ALTER TABLE users ALTER COLUMN username TYPE VARCHAR(80);
```

设置非空：

```sql
ALTER TABLE users ALTER COLUMN username SET NOT NULL;
```

删除字段：

```sql
ALTER TABLE users DROP COLUMN last_login_at;
```

### 4.4 PostgreSQL 常用数据类型

PostgreSQL 的类型系统更丰富，常见类型如下：

```sql
CREATE TABLE examples (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    amount NUMERIC(12, 2) NOT NULL,
    tags TEXT[] NOT NULL DEFAULT '{}',
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

常见选择：

- `TEXT`：文本，PostgreSQL 中很常用。
- `VARCHAR(n)`：需要限制长度时使用。
- `NUMERIC(12, 2)`：金额等精确小数。
- `TIMESTAMPTZ`：带时区时间，实际项目推荐优先使用。
- `JSONB`：二进制 JSON，适合保存灵活扩展字段。
- `UUID`：适合公开 ID、分布式生成 ID。
- `TEXT[]`：数组字段，适合简单标签，但复杂关系仍建议拆表。

JSONB 查询示例：

```sql
SELECT *
FROM examples
WHERE metadata ->> 'source' = 'api';
```

JSONB 建索引：

```sql
CREATE INDEX idx_examples_metadata ON examples USING GIN (metadata);
```

### 4.5 MySQL 和 PostgreSQL 怎么选

学习和普通业务项目，两者都可以。

MySQL 常见优势：

- 国内资料多，很多公司使用广泛。
- 运维和云厂商支持成熟。
- 适合大量传统 Web 业务。

PostgreSQL 常见优势：

- SQL 能力强，类型丰富。
- JSONB、数组、全文搜索、窗口函数体验好。
- 对复杂查询、数据分析、地理信息扩展更友好。

简单建议：

- 如果公司已有技术栈，优先跟随公司。
- 如果学习后端开发，两者至少熟悉一个，另一个了解差异。
- 如果新项目没有历史包袱，PostgreSQL 是很值得优先考虑的选择。

---

## 五、Python 直接操作数据库

### 5.1 连接字符串

很多 Python 工具都用连接字符串描述数据库：

```text
mysql+pymysql://app_user:app_pass@localhost:3306/app_db
postgresql+psycopg://app_user:app_pass@localhost:5432/app_db
```

格式通常是：

```text
数据库类型+驱动://用户名:密码@主机:端口/数据库名
```

项目里不要硬编码连接字符串，推荐放到环境变量：

```bash
DATABASE_URL=postgresql+psycopg://app_user:app_pass@localhost:5432/app_db
```

Python 读取：

```python
import os

database_url = os.environ["DATABASE_URL"]
```

### 5.2 使用 PyMySQL 操作 MySQL

安装：

```bash
pip install pymysql
```

示例：

```python
import pymysql


connection = pymysql.connect(
    host="localhost",
    port=3306,
    user="app_user",
    password="app_pass",
    database="app_db",
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor,
)

try:
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
            ("alice", "alice@example.com", "hash-value"),
        )
    connection.commit()

    with connection.cursor() as cursor:
        cursor.execute("SELECT id, username, email FROM users WHERE username = %s", ("alice",))
        user = cursor.fetchone()
        print(user)
finally:
    connection.close()
```

重点：

- 参数使用 `%s` 占位，不要自己拼接 SQL。
- 写操作后要 `commit()`。
- 出错时要 `rollback()`。
- 连接用完要关闭，Web 项目通常交给连接池管理。

错误示例：

```python
username = "alice' OR '1'='1"
sql = f"SELECT * FROM users WHERE username = '{username}'"
```

这会有 SQL 注入风险。正确写法是：

```python
cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
```

### 5.3 使用 psycopg 操作 PostgreSQL

安装：

```bash
pip install "psycopg[binary]"
```

示例：

```python
import psycopg
from psycopg.rows import dict_row


with psycopg.connect(
    "postgresql://app_user:app_pass@localhost:5432/app_db",
    row_factory=dict_row,
) as connection:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO users (username, email, password_hash)
            VALUES (%s, %s, %s)
            RETURNING id
            """,
            ("alice", "alice@example.com", "hash-value"),
        )
        user_id = cursor.fetchone()["id"]

    with connection.cursor() as cursor:
        cursor.execute("SELECT id, username, email FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        print(user)
```

`with psycopg.connect(...) as connection` 会在正常退出时提交事务，在异常退出时回滚事务。

### 5.4 直接 SQL 适合什么场景

直接写 SQL 的优点：

- 查询表达能力强。
- 性能和执行计划更直观。
- 适合复杂报表、数据分析、批量任务。

缺点：

- 重复代码多。
- 手写字段映射容易出错。
- 表结构变化后，需要手动同步多处 SQL。

实际项目常见组合：

- 普通 CRUD 用 ORM。
- 复杂查询、性能敏感逻辑用手写 SQL。
- 数据迁移、临时修复脚本可以直接写 SQL，但要谨慎审查。

---

## 六、SQLAlchemy ORM

### 6.1 ORM 解决什么问题

ORM 的全称是 Object Relational Mapping，即对象关系映射。

不用 ORM 时，你写 SQL：

```sql
SELECT id, username, email FROM users WHERE id = 1;
```

再把结果转成 Python 对象。

使用 ORM 后，可以这样写：

```python
user = session.get(User, 1)
print(user.username)
```

ORM 的价值：

- 用 Python 类表达表结构。
- 用对象表达一行数据。
- 自动处理字段映射。
- 封装常见增删改查。
- 和迁移工具配合管理表结构。

ORM 不是为了让你完全不懂 SQL。相反，使用 ORM 更需要理解 SQL、索引和事务，否则很容易写出慢查询。

### 6.2 安装 SQLAlchemy

MySQL：

```bash
pip install sqlalchemy pymysql
```

PostgreSQL：

```bash
pip install sqlalchemy "psycopg[binary]"
```

### 6.3 定义模型

以 SQLAlchemy 2.x 风格为例：

```python
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
```

模型类里的常见配置：

- `__tablename__`：数据库表名。
- `primary_key=True`：主键。
- `unique=True`：唯一约束。
- `nullable=False`：不能为空。
- `server_default=func.now()`：由数据库设置默认时间。
- `onupdate=func.now()`：更新时刷新时间。

### 6.4 创建 engine 和 session

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


DATABASE_URL = "postgresql+psycopg://app_user:app_pass@localhost:5432/app_db"

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
```

参数说明：

- `echo=True`：打印 SQL，适合调试，不建议生产开启。
- `pool_size`：连接池常驻连接数。
- `max_overflow`：连接池不够时临时增加的连接数。
- `pool_pre_ping=True`：使用前检查连接是否可用，避免拿到断开的连接。
- `autoflush=False`：避免查询前自动 flush 带来的困惑。
- `autocommit=False`：显式管理事务。

创建表：

```python
Base.metadata.create_all(bind=engine)
```

学习阶段可以用 `create_all`，正式项目更推荐 Alembic 管理迁移。

### 6.5 增删改查

新增：

```python
from sqlalchemy.exc import IntegrityError


def create_user(username: str, email: str, password_hash: str) -> User:
    session = SessionLocal()
    try:
        user = User(username=username, email=email, password_hash=password_hash)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    except IntegrityError:
        session.rollback()
        raise ValueError("用户名或邮箱已存在")
    finally:
        session.close()
```

查询单条：

```python
def get_user(user_id: int) -> User | None:
    session = SessionLocal()
    try:
        return session.get(User, user_id)
    finally:
        session.close()
```

条件查询：

```python
from sqlalchemy import select


def list_active_users(limit: int = 20) -> list[User]:
    session = SessionLocal()
    try:
        statement = (
            select(User)
            .where(User.is_active.is_(True))
            .order_by(User.id.desc())
            .limit(limit)
        )
        return list(session.scalars(statement))
    finally:
        session.close()
```

更新：

```python
def update_email(user_id: int, email: str) -> User:
    session = SessionLocal()
    try:
        user = session.get(User, user_id)
        if user is None:
            raise ValueError("用户不存在")

        user.email = email
        session.commit()
        session.refresh(user)
        return user
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
```

删除：

```python
def delete_user(user_id: int) -> None:
    session = SessionLocal()
    try:
        user = session.get(User, user_id)
        if user is None:
            return

        session.delete(user)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
```

### 6.6 FastAPI 中使用 SQLAlchemy

常见目录：

```text
app/
├── main.py
├── db.py
├── models.py
├── schemas.py
└── routers/
    └── users.py
```

`db.py`：

```python
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


DATABASE_URL = "postgresql+psycopg://app_user:app_pass@localhost:5432/app_db"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

`routers/users.py`：

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import User


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
    }
```

在 Web 项目中，一个请求通常使用一个数据库 session，请求结束后关闭。

### 6.7 常见 ORM 坑

#### N+1 查询

例如查询 20 个订单，每个订单再查询用户：

```python
orders = session.scalars(select(Order).limit(20)).all()
for order in orders:
    print(order.user.username)
```

如果 `order.user` 每次都触发一次查询，就会变成 1 + 20 次 SQL。

解决思路是预加载：

```python
from sqlalchemy.orm import selectinload


statement = select(Order).options(selectinload(Order.user)).limit(20)
orders = session.scalars(statement).all()
```

#### session 生命周期混乱

不要把同一个 session 当全局变量在整个应用里复用。

推荐：

- 脚本：一个任务一个 session。
- Web API：一个请求一个 session。
- 后台任务：一个任务一个 session。

#### 循环里逐条提交

低效写法：

```python
for item in items:
    session.add(item)
    session.commit()
```

更常见写法：

```python
for item in items:
    session.add(item)

session.commit()
```

---

## 七、Alembic 数据库迁移

### 7.1 为什么需要迁移工具

项目上线后，表结构会不断变化：

- 新增字段。
- 修改字段长度。
- 增加索引。
- 新增表。
- 数据修复。

如果只靠手工执行 SQL，很容易出现：

- 开发环境和生产环境结构不一致。
- 不知道某个字段是谁什么时候加的。
- 回滚困难。
- 多人协作时互相覆盖。

Alembic 可以把每次表结构变更记录成版本文件，像管理代码一样管理数据库结构。

### 7.2 初始化 Alembic

安装：

```bash
pip install alembic
```

初始化：

```bash
alembic init migrations
```

常见目录：

```text
project/
├── alembic.ini
├── migrations/
│   ├── env.py
│   └── versions/
└── app/
    └── models.py
```

配置数据库地址：

```ini
sqlalchemy.url = postgresql+psycopg://app_user:app_pass@localhost:5432/app_db
```

实际项目中更推荐从环境变量读取，避免把密码写到配置文件。

### 7.3 生成和执行迁移

创建迁移文件：

```bash
alembic revision -m "create users table"
```

自动检测模型变化：

```bash
alembic revision --autogenerate -m "add users table"
```

执行到最新版本：

```bash
alembic upgrade head
```

回滚一个版本：

```bash
alembic downgrade -1
```

查看当前版本：

```bash
alembic current
```

查看历史：

```bash
alembic history
```

### 7.4 迁移文件示例

```python
from alembic import op
import sqlalchemy as sa


revision = "202607050001"
down_revision = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_unique_constraint("uq_users_username", "users", ["username"])
    op.create_unique_constraint("uq_users_email", "users", ["email"])


def downgrade() -> None:
    op.drop_constraint("uq_users_email", "users", type_="unique")
    op.drop_constraint("uq_users_username", "users", type_="unique")
    op.drop_table("users")
```

注意：

- 自动生成后一定要人工 review。
- 生产环境迁移前要备份。
- 大表加索引、改字段类型要评估锁表和执行时间。
- `downgrade` 不一定总能完美恢复数据，但至少要明确回滚策略。

---

## 八、Django ORM 简介

### 8.1 Django ORM 的特点

如果项目使用 Django，通常直接使用 Django ORM，而不是额外引入 SQLAlchemy。

Django ORM 的特点：

- 和 Django admin、表单、认证系统集成紧密。
- 自带 migration 工具。
- 模型、查询、权限、后台管理是一套完整体系。

### 8.2 定义模型

```python
from django.db import models


class UserProfile(models.Model):
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.username
```

生成迁移：

```bash
python manage.py makemigrations
```

执行迁移：

```bash
python manage.py migrate
```

查看 SQL：

```bash
python manage.py sqlmigrate app_name 0001
```

### 8.3 常用查询

新增：

```python
user = UserProfile.objects.create(
    username="alice",
    email="alice@example.com",
)
```

查询单条：

```python
user = UserProfile.objects.get(id=1)
```

查询列表：

```python
users = UserProfile.objects.filter(is_active=True).order_by("-id")[:20]
```

更新：

```python
user.email = "new-alice@example.com"
user.save(update_fields=["email", "updated_at"])
```

批量更新：

```python
UserProfile.objects.filter(is_active=False).update(is_active=True)
```

删除：

```python
user.delete()
```

### 8.4 Django ORM 优化

外键对象预加载：

```python
orders = Order.objects.select_related("user").all()
```

多对多或反向关系预加载：

```python
users = UserProfile.objects.prefetch_related("groups").all()
```

只取部分字段：

```python
users = UserProfile.objects.only("id", "username")
```

查看 SQL：

```python
print(UserProfile.objects.filter(is_active=True).query)
```

Django 项目里常见原则：

- 复杂业务不要都塞进 view，可以放到 service 层。
- 避免模板里触发大量懒加载查询。
- 查询列表接口时注意分页。
- 对高频查询字段建索引。

---

## 九、Redis 常用操作

### 9.1 Redis 适合做什么

Redis 是内存数据库，特点是快，但内存成本高，通常用来保存短期、高频、可重建的数据。

常见场景：

- 缓存热门数据。
- 保存验证码、短信码、登录态。
- 分布式锁。
- 计数器、限流器。
- 排行榜。
- 简单队列。
- Celery broker 或 result backend。

不适合：

- 存放必须长期可靠保存的核心业务数据。
- 存放特别大的对象。
- 替代关系型数据库做复杂查询。

### 9.2 Docker 启动 Redis

```bash
docker run --name redis-dev -p 6379:6379 -d redis:7
```

进入命令行：

```bash
docker exec -it redis-dev redis-cli
```

测试连接：

```bash
PING
```

返回：

```text
PONG
```

### 9.3 String 操作

设置值：

```redis
SET name Alice
```

获取值：

```redis
GET name
```

设置过期时间：

```redis
SET verify:phone:13800000000 123456 EX 300
```

查看剩余时间：

```redis
TTL verify:phone:13800000000
```

自增：

```redis
INCR page:view:1001
```

自增指定数量：

```redis
INCRBY page:view:1001 10
```

删除：

```redis
DEL name
```

### 9.4 Hash 操作

Hash 适合保存对象的多个字段：

```redis
HSET user:1 username alice email alice@example.com age 20
HGET user:1 username
HGETALL user:1
HDEL user:1 age
```

适合：

- 用户简单信息缓存。
- 配置项缓存。
- 小对象缓存。

不建议把一个特别大的对象塞进单个 Hash。

### 9.5 List 操作

List 可用于简单队列：

```redis
LPUSH tasks send_email:1
RPOP tasks
```

阻塞式弹出：

```redis
BRPOP tasks 5
```

查看范围：

```redis
LRANGE tasks 0 -1
```

生产环境如果任务很重要，更推荐 Celery、RabbitMQ、Kafka 等专业方案。

### 9.6 Set 操作

Set 是无序不重复集合：

```redis
SADD article:1:likes user:1 user:2 user:3
SISMEMBER article:1:likes user:1
SCARD article:1:likes
SREM article:1:likes user:2
```

适合：

- 点赞用户集合。
- 去重。
- 标签集合。
- 黑名单、白名单。

### 9.7 Sorted Set 操作

Sorted Set 适合排行榜：

```redis
ZADD leaderboard 100 alice 80 bob 120 carol
ZREVRANGE leaderboard 0 9 WITHSCORES
ZRANK leaderboard alice
ZREVRANK leaderboard alice
ZINCRBY leaderboard 10 alice
```

按分数范围查询：

```redis
ZRANGEBYSCORE leaderboard 80 120 WITHSCORES
```

### 9.8 Key 管理

查看 key 是否存在：

```redis
EXISTS user:1
```

设置过期时间：

```redis
EXPIRE user:1 3600
```

查看类型：

```redis
TYPE user:1
```

谨慎使用：

```redis
KEYS *
```

`KEYS *` 在大量 key 时可能阻塞 Redis，生产环境更推荐：

```redis
SCAN 0 MATCH user:* COUNT 100
```

### 9.9 Python 操作 Redis

安装：

```bash
pip install redis
```

基础用法：

```python
import redis


r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

r.set("name", "Alice", ex=300)
print(r.get("name"))

r.hset("user:1", mapping={
    "username": "alice",
    "email": "alice@example.com",
})
print(r.hgetall("user:1"))
```

连接 URL：

```python
import redis


r = redis.from_url("redis://localhost:6379/0", decode_responses=True)
```

### 9.10 缓存模式

最常见的是 Cache Aside 模式：

```python
import json


def get_user_profile(user_id: int) -> dict:
    cache_key = f"user:profile:{user_id}"

    cached = r.get(cache_key)
    if cached is not None:
        return json.loads(cached)

    user = query_user_from_database(user_id)
    if user is None:
        raise ValueError("用户不存在")

    data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
    }
    r.set(cache_key, json.dumps(data), ex=300)
    return data
```

更新数据时删除缓存：

```python
def update_user_email(user_id: int, email: str) -> None:
    update_user_email_in_database(user_id, email)
    r.delete(f"user:profile:{user_id}")
```

为什么通常是删除缓存，而不是直接更新缓存：

- 删除后下次查询会重新从数据库加载，逻辑简单。
- 避免缓存和数据库写入顺序导致不一致。
- 对复杂对象更安全。

### 9.11 分布式锁

简单锁：

```python
import time
import uuid


def acquire_lock(key: str, ttl: int = 10) -> str | None:
    token = str(uuid.uuid4())
    ok = r.set(key, token, nx=True, ex=ttl)
    return token if ok else None


def release_lock(key: str, token: str) -> None:
    script = """
    if redis.call("get", KEYS[1]) == ARGV[1] then
        return redis.call("del", KEYS[1])
    else
        return 0
    end
    """
    r.eval(script, 1, key, token)


token = acquire_lock("lock:order:1001", ttl=30)
if token is None:
    raise RuntimeError("请稍后重试")

try:
    handle_order(1001)
finally:
    release_lock("lock:order:1001", token)
```

锁的要点：

- 使用 `NX` 保证只有不存在时才设置。
- 设置过期时间，避免进程崩溃后死锁。
- 释放锁时校验 token，避免删掉别人的锁。
- 锁内逻辑要短，超时要可接受。

### 9.12 限流

简单固定窗口限流：

```python
def check_rate_limit(user_id: int, limit: int = 60, window: int = 60) -> bool:
    key = f"rate:user:{user_id}"
    count = r.incr(key)
    if count == 1:
        r.expire(key, window)
    return count <= limit
```

含义：每个用户 60 秒内最多请求 60 次。

更精确的限流可以使用滑动窗口、令牌桶，或者直接使用网关和专门限流组件。

---

## 十、异步 Python 中的数据库和 Redis

### 10.1 什么时候需要异步

如果项目使用 FastAPI、Starlette、aiohttp 等异步框架，并且接口需要高并发处理大量 I/O，可以考虑异步数据库和 Redis 客户端。

但要记住：

- 异步不是自动更快。
- 异步链路里不要混入阻塞数据库驱动。
- CPU 密集型任务不适合靠 asyncio 提速。
- 数据库本身仍然有连接数和吞吐限制。

### 10.2 SQLAlchemy Async

安装 PostgreSQL 异步驱动：

```bash
pip install sqlalchemy asyncpg
```

创建异步 engine：

```python
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


DATABASE_URL = "postgresql+asyncpg://app_user:app_pass@localhost:5432/app_db"

engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
```

查询：

```python
from sqlalchemy import select


async def get_user(user_id: int, db: AsyncSession) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()
```

提交：

```python
async def create_user(db: AsyncSession, username: str, email: str) -> User:
    user = User(username=username, email=email, password_hash="hash-value")
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
```

### 10.3 异步 Redis

```python
import redis.asyncio as redis


r = redis.from_url("redis://localhost:6379/0", decode_responses=True)


async def cache_value() -> None:
    await r.set("name", "Alice", ex=300)
    value = await r.get("name")
    print(value)
```

Web 应用关闭时要关闭连接：

```python
await r.aclose()
```

---

## 十一、消息队列和后台任务

### 11.1 为什么需要后台任务

用户请求里不适合做太慢、容易失败、可以稍后处理的事情。

例如：

- 发送邮件。
- 生成 PDF 报表。
- 调用第三方 API。
- 处理上传文件。
- 批量导入数据。
- 爬虫和定时任务。

如果这些都放在 HTTP 请求里，用户会等待很久，而且失败后不好重试。

更好的方式：

```text
用户请求
  └── 写入数据库
  └── 投递任务
      └── worker 后台执行
```

### 11.2 Celery + Redis

安装：

```bash
pip install celery redis
```

`tasks.py`：

```python
from celery import Celery


celery_app = Celery(
    "app",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
)


@celery_app.task(bind=True, max_retries=3)
def send_welcome_email(self, user_id: int) -> None:
    try:
        user = query_user_from_database(user_id)
        send_email(user.email, "欢迎注册", "欢迎使用我们的产品")
    except Exception as exc:
        raise self.retry(exc=exc, countdown=10)
```

启动 worker：

```bash
celery -A tasks worker --loglevel=info
```

投递任务：

```python
from tasks import send_welcome_email


send_welcome_email.delay(user_id=1001)
```

定时任务可以用 Celery Beat：

```bash
celery -A tasks beat --loglevel=info
```

Celery 使用建议：

- 任务参数尽量传 ID，不要传大对象。
- 任务要设计成可重试、可幂等。
- 任务里单独创建数据库 session，不要复用 Web 请求里的 session。
- 记录任务日志和失败原因。
- 重要任务要设置超时、重试次数、死信或补偿策略。

### 11.3 RabbitMQ 和 Kafka 简介

Redis 可以做轻量队列，但更专业的消息系统通常是 RabbitMQ 或 Kafka。

RabbitMQ 常见特点：

- 适合任务队列、业务消息、可靠投递。
- 支持交换机、路由键、确认机制。
- 常用于订单、通知、异步处理。

Kafka 常见特点：

- 适合高吞吐事件流。
- 消息按 topic 保存，可以重复消费。
- 常用于日志、埋点、数据管道、实时计算。

简单选择：

- 后台任务：优先 Celery + Redis 或 Celery + RabbitMQ。
- 业务系统解耦：RabbitMQ 很常见。
- 大规模事件流、日志流：Kafka 更合适。

---

## 十二、其他常用中间件

### 12.1 Elasticsearch / OpenSearch

适合：

- 全文搜索。
- 日志检索。
- 商品筛选。
- 多条件复杂查询。

常见流程：

```text
业务数据写入 PostgreSQL / MySQL
  └── 同步到 Elasticsearch
      └── 搜索接口从 Elasticsearch 查询
```

注意：

- 搜索引擎通常不是主数据库。
- 主数据仍然应该保存在关系型数据库里。
- 搜索索引可以重建，所以要保留可靠的数据源。

### 12.2 MinIO / S3

适合保存对象文件：

- 用户头像。
- 图片、视频。
- PDF、Excel、Word。
- 日志归档。
- 模型文件。

常见做法：

```text
文件内容 -> S3 / MinIO
文件元数据 -> MySQL / PostgreSQL
```

数据库里保存：

```text
id
bucket
object_key
filename
content_type
size
created_at
```

不要把大文件二进制内容直接塞进关系型数据库，除非你非常清楚这样做的代价。

### 12.3 Nginx

Nginx 常见用途：

- 反向代理 Python Web 服务。
- 处理静态文件。
- HTTPS 终止。
- 负载均衡。
- 限制请求体大小、超时时间。

常见结构：

```text
client
  └── nginx
      └── gunicorn / uvicorn
          └── Python app
```

生产环境里，Python 应用通常不直接暴露给公网，而是放在 Nginx 后面。

---

## 十三、项目中的典型目录结构

一个包含数据库、Redis、后台任务的 FastAPI 项目可以这样组织：

```text
app/
├── main.py
├── core/
│   ├── config.py
│   └── logging.py
├── db/
│   ├── base.py
│   ├── session.py
│   └── migrations/
├── models/
│   ├── user.py
│   └── order.py
├── schemas/
│   ├── user.py
│   └── order.py
├── repositories/
│   ├── user_repository.py
│   └── order_repository.py
├── services/
│   ├── user_service.py
│   └── order_service.py
├── cache/
│   └── redis_client.py
├── tasks/
│   ├── celery_app.py
│   └── email_tasks.py
└── api/
    └── routes/
        ├── users.py
        └── orders.py
```

常见分层：

- `models/`：数据库 ORM 模型。
- `schemas/`：Pydantic 输入输出模型。
- `repositories/`：封装数据库查询。
- `services/`：业务逻辑。
- `api/routes/`：HTTP 路由。
- `cache/`：Redis 客户端和缓存函数。
- `tasks/`：后台任务。
- `core/config.py`：统一读取配置。

示例调用链：

```text
POST /orders
  └── api/routes/orders.py
      └── services/order_service.py
          ├── repositories/order_repository.py
          ├── repositories/product_repository.py
          ├── cache/redis_client.py
          └── tasks/email_tasks.py
```

这样做的好处是：

- API 层不直接写复杂 SQL。
- 业务逻辑集中在 service 层。
- 数据库操作集中在 repository 层，方便测试和替换。
- Redis、任务队列等基础设施有明确边界。

---

## 十四、配置管理

### 14.1 环境变量

项目里常见配置：

```bash
APP_ENV=dev
DATABASE_URL=postgresql+psycopg://app_user:app_pass@localhost:5432/app_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=change-me
```

Python 读取：

```python
import os


database_url = os.environ["DATABASE_URL"]
redis_url = os.environ["REDIS_URL"]
```

### 14.2 Pydantic Settings

安装：

```bash
pip install pydantic-settings
```

示例：

```python
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "dev"
    database_url: str
    redis_url: str = "redis://localhost:6379/0"
    secret_key: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

使用：

```python
settings = get_settings()
print(settings.database_url)
```

注意：

- `.env` 适合本地开发。
- 生产环境配置通常由容器平台、CI/CD、密钥管理服务注入。
- `.env` 不应该提交真实密码。

---

## 十五、常见实战场景

### 15.1 用户注册

流程：

```text
接收注册请求
  └── 校验参数
  └── 检查用户名/邮箱是否重复
  └── 密码哈希
  └── 写入 users 表
  └── 删除或刷新相关缓存
  └── 投递欢迎邮件任务
```

关键点：

- 用户名和邮箱要有唯一索引。
- 密码必须哈希，不能明文保存。
- 数据库唯一约束错误要转换成友好的业务错误。
- 发送邮件不要阻塞注册接口。

### 15.2 登录和验证码

验证码可以放 Redis：

```python
def save_login_code(phone: str, code: str) -> None:
    r.set(f"login_code:{phone}", code, ex=300)


def verify_login_code(phone: str, code: str) -> bool:
    key = f"login_code:{phone}"
    saved = r.get(key)
    if saved != code:
        return False
    r.delete(key)
    return True
```

注意：

- 验证码要设置过期时间。
- 验证成功后删除，避免重复使用。
- 发送验证码接口要限流。
- 不要在日志里打印验证码和密码。

### 15.3 秒杀扣库存

简单数据库扣库存：

```sql
UPDATE products
SET stock = stock - 1
WHERE id = 1001 AND stock > 0;
```

如果影响行数为 1，说明扣减成功；如果为 0，说明库存不足。

项目中还要考虑：

- 防重复下单。
- 用户限购。
- 请求限流。
- 异步创建订单。
- 超时未支付释放库存。
- Redis 预扣库存和数据库最终一致性。

不要一开始就把秒杀系统做得很复杂。先保证数据库层面的正确性，再根据性能瓶颈引入缓存和队列。

### 15.4 列表分页

普通分页：

```sql
SELECT id, title, created_at
FROM articles
ORDER BY id DESC
LIMIT 20 OFFSET 1000;
```

数据量大时，`OFFSET` 很大可能变慢。可以使用游标分页：

```sql
SELECT id, title, created_at
FROM articles
WHERE id < 10000
ORDER BY id DESC
LIMIT 20;
```

接口返回：

```json
{
  "items": [],
  "next_cursor": 9980
}
```

适合信息流、日志列表、消息列表。

### 15.5 数据导入

导入 CSV 到数据库时：

- 分批读取，不要一次性加载全部数据。
- 每批提交一次事务。
- 对错误行记录日志。
- 对唯一键冲突制定策略：跳过、更新、报错。
- 大量导入前可以临时关闭不必要的二级索引，完成后重建，但要谨慎。

Python 示例：

```python
import csv


def import_users(path: str, batch_size: int = 1000) -> None:
    session = SessionLocal()
    batch: list[User] = []
    try:
        with open(path, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                batch.append(User(
                    username=row["username"],
                    email=row["email"],
                    password_hash=row["password_hash"],
                ))

                if len(batch) >= batch_size:
                    session.add_all(batch)
                    session.commit()
                    batch.clear()

            if batch:
                session.add_all(batch)
                session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
```

---

## 十六、排查问题常用命令

### 16.1 MySQL 排查

查看连接：

```sql
SHOW PROCESSLIST;
```

查看慢查询配置：

```sql
SHOW VARIABLES LIKE 'slow_query%';
SHOW VARIABLES LIKE 'long_query_time';
```

查看表大小：

```sql
SELECT
    table_name,
    ROUND((data_length + index_length) / 1024 / 1024, 2) AS size_mb
FROM information_schema.tables
WHERE table_schema = 'app_db'
ORDER BY size_mb DESC;
```

查看执行计划：

```sql
EXPLAIN SELECT * FROM users WHERE email = 'alice@example.com';
```

### 16.2 PostgreSQL 排查

查看连接：

```sql
SELECT pid, usename, datname, state, query
FROM pg_stat_activity
WHERE datname = 'app_db';
```

查看慢查询需要开启扩展或日志配置，常见扩展：

```sql
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
```

查看表大小：

```sql
SELECT
    relname AS table_name,
    pg_size_pretty(pg_total_relation_size(relid)) AS size
FROM pg_catalog.pg_statio_user_tables
ORDER BY pg_total_relation_size(relid) DESC;
```

查看执行计划：

```sql
EXPLAIN ANALYZE
SELECT * FROM users WHERE email = 'alice@example.com';
```

### 16.3 Redis 排查

查看信息：

```redis
INFO
```

查看内存：

```redis
INFO memory
```

查看客户端连接：

```redis
CLIENT LIST
```

查看慢命令：

```redis
SLOWLOG GET 10
```

查看 key 数量：

```redis
DBSIZE
```

扫描 key：

```redis
SCAN 0 MATCH user:* COUNT 100
```

---

## 十七、安全和可靠性建议

### 17.1 数据库安全

- 应用不要使用 root / superuser。
- 数据库端口不要直接暴露到公网。
- 密码不要提交到 Git。
- 生产环境开启备份，并定期演练恢复。
- 重要操作要有审计日志。
- SQL 参数必须绑定，不要字符串拼接。

### 17.2 事务和一致性

- 钱、库存、订单状态这类核心数据要优先保证正确。
- 同一事务里不要放外部网络请求。
- 跨系统一致性通常靠状态机、消息队列、补偿任务，而不是一个超大事务。
- 对可能重复执行的任务设计幂等键。

### 17.3 缓存可靠性

- 缓存必须设置合理过期时间。
- 不能把 Redis 当作唯一数据源保存核心业务数据。
- 热点 key 要注意击穿问题。
- 大量 key 同时过期可能造成缓存雪崩，可以给过期时间加随机抖动。

示例：

```python
import random


ttl = 300 + random.randint(0, 60)
r.set(cache_key, value, ex=ttl)
```

### 17.4 连接池

连接池不是越大越好。

例如：

```text
4 个 Web 进程
每个进程 pool_size = 10
最大基础连接数 = 40
```

如果数据库最大连接数只有 100，还要给后台任务、管理工具、迁移脚本留余量。

常见建议：

- 根据进程数计算总连接数。
- 设置连接超时和回收。
- 请求结束及时释放 session。
- 慢查询比盲目加连接池更值得优先排查。

---

## 十八、学习路线

### 18.1 第一阶段：会用

目标：

- 能启动 MySQL / PostgreSQL / Redis。
- 能创建表、插入、查询、更新、删除。
- 能理解主键、唯一索引、普通索引。
- 能用 Python 连接数据库和 Redis。

练习：

- 做一个用户表。
- 写注册、查询、修改资料、删除用户脚本。
- 用 Redis 保存验证码和计数器。

### 18.2 第二阶段：会放进项目

目标：

- 会使用 SQLAlchemy 或 Django ORM。
- 会用 Alembic 或 Django migrations 管理表结构。
- 会在 FastAPI / Django 项目里管理 session。
- 会把配置放到环境变量。
- 会用 Redis 做缓存和限流。

练习：

- 做一个文章 API。
- 用户可以发布、查看、分页浏览文章。
- 热门文章列表用 Redis 缓存。
- 发布文章后异步发送通知任务。

### 18.3 第三阶段：会排查和优化

目标：

- 会看执行计划。
- 会定位慢查询。
- 会设计合理索引。
- 会处理事务、锁、并发写入问题。
- 会评估缓存一致性。
- 会设计后台任务重试和幂等。

练习：

- 给文章列表造 100 万条数据。
- 对比有索引和无索引的查询性能。
- 用 `EXPLAIN` 分析查询计划。
- 模拟任务失败，验证重试和幂等逻辑。

---

## 十九、常用命令速查

### 19.1 Docker

```bash
docker ps
docker logs mysql-dev
docker logs postgres-dev
docker logs redis-dev
docker stop mysql-dev
docker start mysql-dev
docker exec -it mysql-dev mysql -uroot -prootpass
docker exec -it postgres-dev psql -U app_user -d app_db
docker exec -it redis-dev redis-cli
```

### 19.2 MySQL

```sql
SHOW DATABASES;
USE app_db;
SHOW TABLES;
DESC users;
SHOW CREATE TABLE users;
SHOW INDEX FROM users;
EXPLAIN SELECT * FROM users WHERE email = 'alice@example.com';
SHOW PROCESSLIST;
```

### 19.3 PostgreSQL

```sql
\l
\c app_db
\dt
\d users
\du
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'alice@example.com';
```

### 19.4 Redis

```redis
PING
GET key
SET key value EX 300
DEL key
TTL key
HGETALL user:1
LRANGE tasks 0 -1
ZREVRANGE leaderboard 0 9 WITHSCORES
INFO memory
SLOWLOG GET 10
SCAN 0 MATCH user:* COUNT 100
```

### 19.5 Alembic

```bash
alembic init migrations
alembic revision -m "create users table"
alembic revision --autogenerate -m "add users table"
alembic upgrade head
alembic downgrade -1
alembic current
alembic history
```

---

## 二十、总结

数据库和中间件不是孤立的工具，而是 Python 项目的基础能力。

学习时可以按这个顺序理解：

1. 先掌握 SQL 和关系型数据库，知道数据如何长期保存。
2. 再学习 Redis，理解缓存、限流、锁和短期状态。
3. 然后使用 ORM，把数据库操作放进真实 Python 项目。
4. 接着学习迁移工具，让表结构变化可追踪、可回滚。
5. 最后引入消息队列、搜索、对象存储等中间件，解决更复杂的系统问题。

真正写项目时，不要一开始就追求复杂架构。先用 MySQL 或 PostgreSQL 把核心数据模型设计清楚，用 ORM 写出可维护的业务代码，再根据性能和可靠性问题逐步引入 Redis、任务队列和其他中间件。工具越多，系统越需要边界清晰、配置明确、日志完整和测试兜底。
