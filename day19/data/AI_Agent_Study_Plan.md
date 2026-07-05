## Python AI Agent 开发 · 学习计划

> 目标：从前端开发者过渡到 Python AI Agent 开发，基于已有 Node.js LangChain/LangGraph 经验，补齐 Python 语言核心能力。

---

### 第一阶段：语言核心（约 1～2 周）

这是最优先的部分，后续所有内容都建立在这些基础之上。

- [ ] **面向对象编程（OOP）**
  - class 定义、`__init__`、`self`
  - 继承、`super()`、多态
  - dunder 方法：`__str__`、`__repr__`、`__call__`、`__enter__`/`__exit__`
  - `@dataclass` 数据类
  - `@property`、类方法 `@classmethod`、静态方法 `@staticmethod`
  - 抽象基类 `abc.ABC`

- [ ] **类型提示（Type Hints）**
  - 基础类型注解：`int`、`str`、`Optional`、`Union`
  - 容器类型：`list[int]`、`dict[str, Any]`
  - `typing` 模块：`TypeVar`、`Generic`、`Callable`、`Protocol`
  - 函数签名与返回值类型标注

- [ ] **Pydantic**
  - `BaseModel` 定义与字段校验
  - `Field` 配置、嵌套模型
  - 模型序列化与反序列化
  - `model_validator`、`field_validator`
  - 与 FastAPI 的集成（提前了解即可）

- [ ] **装饰器（Decorators）**
  - 函数装饰器的原理与编写
  - 带参数的装饰器
  - `functools.wraps` 保留元信息
  - 类装饰器（了解）
  - 常见内置装饰器：`@staticmethod`、`@classmethod`、`@property`、`@lru_cache`

---

### 第二阶段：并发与迭代（约 1 周）

AI Agent 开发中频繁涉及异步调用 LLM API 和流式输出，这部分非常关键。

- [ ] **异步编程（async/await）**
  - `async def`、`await` 基本语法
  - `asyncio.run()`、事件循环概念
  - `asyncio.gather()`、`asyncio.create_task()` 并发执行
  - `async with`、`async for`
  - `aiohttp` / `httpx` 异步 HTTP 请求
  - 与同步代码的互操作：`asyncio.to_thread()`

- [ ] **生成器与迭代器**
  - `yield` 关键字与生成器函数
  - 生成器表达式
  - `async generator`（`async for` + `yield`）——LLM 流式输出的基础
  - `itertools` 常用工具函数

---

### 第三阶段：实用工具（约 3～5 天）

写实际项目时高频使用，建议在项目中边做边巩固。

- [ ] **上下文管理器**
  - `with` 语句原理
  - 自定义上下文管理器（`__enter__`/`__exit__`）
  - `contextlib.contextmanager` 装饰器写法
  - 典型场景：文件操作、数据库连接、临时目录

- [ ] **文件操作与数据处理**
  - `pathlib` 路径操作（替代 `os.path`）
  - JSON / CSV 读写
  - `logging` 日志模块（替代 print 调试）
  - `python-dotenv` 环境变量管理

- [ ] **常用标准库补充**
  - `functools`：`partial`、`lru_cache`、`cached_property`
  - `collections`：`defaultdict`、`Counter`、`deque`
  - `dataclasses`：进阶用法
  - `enum`：枚举类型

---

### 第四阶段：项目实战（持续进行）

前三阶段学完后，直接进入项目实战，以下内容在实践中按需学习。

- [ ] **FastAPI 基础**
  - 路由定义、请求参数、响应模型
  - Pydantic 数据校验集成
  - 中间件（CORS、日志）
  - 异步路由处理
  - 自动 API 文档（Swagger UI）

- [ ] **数据库基础**
  - SQLite + Python 内置 `sqlite3`（轻量场景）
  - SQLAlchemy 基础用法（ORM 操作）
  - Redis 基础（缓存、会话存储）——按需学习

- [ ] **向量数据库**
  - ChromaDB（本地开发首选）
  - FAISS（高性能向量检索）
  - Embedding 生成与存储
  - 与 LangChain 的集成

- [ ] **Python AI Agent 框架**
  - LangChain Python 版
  - LangGraph Python 版
  - 工具定义与调用（Tool/Function Calling）
  - Agent 编排与状态管理
  - 流式输出处理

---

### 建议学习节奏

| 阶段 | 预计时间 | 说明 |
|------|----------|------|
| 第一阶段 | 1～2 周 | 核心基础，务必扎实 |
| 第二阶段 | 约 1 周 | 异步编程是 AI Agent 的刚需 |
| 第三阶段 | 3～5 天 | 可以在项目中边做边学 |
| 第四阶段 | 持续 | 直接上手做项目，遇到什么学什么 |

> 💡 你的 Node.js AI Agent 经验是最大优势，很多架构概念（Chain、Graph、Tool Calling）是相通的，主要成本只是在熟悉 Python 的表达方式。建议尽早进入第四阶段，在实战中巩固前三阶段的知识。
