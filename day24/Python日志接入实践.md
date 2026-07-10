# Python 日志系统完全指南

> 日志是生产环境的"黑匣子"。print 只能帮你调试眼前的代码，而 logging 能帮你在凌晨 3 点从一条报错信息里还原整个事故链。

---

## 一、为什么不用 print

print 有三个致命问题：没有级别区分，无法控制输出目的地，没有统一格式。当你的程序从脚本变成服务，从本地跑到服务器，print 就不够用了。

logging 模块解决的就是这三个问题：

- **级别**：DEBUG / INFO / WARNING / ERROR / CRITICAL，按需过滤
- **目的地**：控制台、文件、网络、邮件，可以同时输出到多个地方
- **格式**：时间戳、模块名、行号、进程号，想加什么加什么

---

## 二、5 分钟上手

```python
import logging

# 最简配置：设置最低级别为 INFO，默认是 WARNING
logging.basicConfig(level=logging.INFO)

logging.debug("这条不会显示，因为级别低于 INFO")
logging.info("服务启动成功")
logging.warning("磁盘空间不足 20%")
logging.error("数据库连接失败")
logging.critical("系统崩溃")
```

输出：

```
INFO:root:服务启动成功
WARNING:root:磁盘空间不足 20%
ERROR:root:数据库连接失败
CRITICAL:root:系统崩溃
```

`basicConfig` 只能调用一次。如果需要更灵活的配置，往下看。

---

## 三、核心架构：四大组件

logging 的架构可以拆成四个角色：

| 组件 | 职责 | 类比 |
|------|------|------|
| Logger | 决定"记什么"——暴露 `info()` / `error()` 等接口 | 记者 |
| Handler | 决定"写到哪"——控制台、文件、网络 | 印刷厂 / 电视台 |
| Formatter | 决定"长什么样"——时间、级别、消息格式 | 排版编辑 |
| Filter | 决定"要不要记"——比级别更精细的过滤 | 审核员 |

它们的关系：Logger 把日志记录交给 Handler，Handler 用 Formatter 格式化后输出，Filter 在两端做拦截。

### 3.1 Logger：获取与命名

```python
# 推荐：用 __name__ 命名，自动对应模块路径
logger = logging.getLogger(__name__)

# 也支持自定义名称
logger = logging.getLogger("payment.service")
```

Logger 有层级关系，用 `.` 分隔。`payment.service` 是 `payment` 的子 Logger，子 Logger 产生的日志会冒泡到父 Logger。这个机制让你可以在父级统一配置 Handler。

### 3.2 五大日志级别

```
级别        数值    典型场景
─────────────────────────────────────────────
DEBUG       10     开发调试信息，生产环境关闭
INFO        20     正常运行事件：请求到达、任务完成
WARNING     30     异常但不影响运行：重试、降级、废弃API
ERROR       40     功能失败：某个请求处理出错
CRITICAL    50     系统级故障：程序无法继续运行
```

自定义级别一般不需要，但如果你的框架有特殊需求：

```python
TRACE = 5
logging.addLevelName(TRACE, "TRACE")

def trace(self, msg, *args, **kwargs):
    if self.isEnabledFor(TRACE):
        self._log(TRACE, msg, args, **kwargs)

logging.Logger.trace = trace
```

### 3.3 常用 Handler

```python
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

# 输出到控制台
console = logging.StreamHandler()

# 输出到文件（追加模式）
file_handler = logging.FileHandler("app.log", encoding="utf-8")

# 按大小滚动：每个文件最大 5MB，保留 3 个备份
rotating = RotatingFileHandler(
    "app.log", maxBytes=5*1024*1024, backupCount=3, encoding="utf-8"
)

# 按时间滚动：每天午夜切割，保留 30 天
timed = TimedRotatingFileHandler(
    "app.log", when="midnight", backupCount=30, encoding="utf-8"
)
```

### 3.4 Formatter：统一格式

```python
# 基础格式
fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

# 完整格式（推荐生产环境）
fmt = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# JSON 格式（适合 ELK / Loki 等日志平台采集）
# 需要三方库 python-json-logger，后面会讲
```

常用格式化字段一览：

| 字段 | 含义 |
|------|------|
| `%(asctime)s` | 时间戳 |
| `%(levelname)s` | 级别名称 |
| `%(name)s` | Logger 名称 |
| `%(filename)s` | 文件名 |
| `%(lineno)d` | 行号 |
| `%(funcName)s` | 函数名 |
| `%(module)s` | 模块名 |
| `%(process)d` | 进程 ID |
| `%(thread)d` | 线程 ID |
| `%(message)s` | 日志消息 |

---

## 四、完整配置示例

### 4.1 代码配置（适合脚本和小项目）

```python
import logging
from logging.handlers import RotatingFileHandler

def setup_logger():
    logger = logging.getLogger("myapp")
    logger.setLevel(logging.DEBUG)

    # 控制台：INFO 及以上
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S"
    ))

    # 文件：DEBUG 及以上，按大小滚动
    file_handler = RotatingFileHandler(
        "logs/app.log", maxBytes=10*1024*1024,
        backupCount=5, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s"
    ))

    logger.addHandler(console)
    logger.addHandler(file_handler)
    return logger

logger = setup_logger()
logger.info("Logger 配置完成，开始运行")
```

### 4.2 dictConfig（推荐中大型项目）

把配置放到字典里，和代码解耦。可以直接读 YAML / JSON 文件：

```python
import logging.config

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,  # 重要！不要禁用已有的 logger
    "formatters": {
        "simple": {
            "format": "%(asctime)s [%(levelname)s] %(message)s"
        },
        "detailed": {
            "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "simple",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": "logs/app.log",
            "maxBytes": 10485760,
            "backupCount": 5,
            "encoding": "utf-8"
        }
    },
    "loggers": {
        "myapp": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
            "propagate": False
        }
    },
    "root": {
        "level": "WARNING",
        "handlers": ["console"]
    }
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("myapp")
```

### 4.3 从 YAML 文件加载

```python
import yaml
import logging.config
from pathlib import Path

config_path = Path("config/logging.yaml")
with open(config_path) as f:
    config = yaml.safe_load(f)

logging.config.dictConfig(config)
```

---

## 五、项目实战：标准日志模块

在多模块项目中，推荐这样组织日志：

```
myproject/
├── config/
│   └── logging.yaml       # 集中配置
├── core/
│   ├── __init__.py
│   └── logger.py          # logger 工厂函数
├── services/
│   ├── order.py           # logger = get_logger(__name__)
│   └── payment.py         # logger = get_logger(__name__)
└── main.py
```

`core/logger.py`：

```python
import logging
import logging.config
import yaml
from pathlib import Path

_configured = False

def setup_logging(config_path: str = "config/logging.yaml"):
    """应用启动时调用一次"""
    global _configured
    path = Path(config_path)
    if path.exists():
        with open(path) as f:
            logging.config.dictConfig(yaml.safe_load(f))
    else:
        logging.basicConfig(level=logging.INFO)
    _configured = True

def get_logger(name: str) -> logging.Logger:
    """各模块通过此函数获取 logger"""
    if not _configured:
        setup_logging()
    return logging.getLogger(name)
```

`services/order.py`：

```python
from core.logger import get_logger

logger = get_logger(__name__)  # 自动命名为 "services.order"

def create_order(user_id: str, items: list):
    logger.info(f"创建订单: user={user_id}, items={len(items)}")
    try:
        # 业务逻辑...
        order_id = "ORD-20240101-001"
        logger.info(f"订单创建成功: {order_id}")
        return order_id
    except Exception as e:
        logger.error(f"订单创建失败: user={user_id}, error={e}", exc_info=True)
        raise
```

关键细节是 `exc_info=True`，它会自动把异常堆栈附加到日志里。没有这个参数，你只能看到 "订单创建失败"，看不到完整的 traceback。

---

## 六、进阶技巧

### 6.1 结构化日志（JSON）

生产环境的日志通常会被 ELK、Loki、Datadog 等平台采集。JSON 格式让日志可被程序化解析：

```bash
pip install python-json-logger
```

```python
from pythonjsonlogger import jsonlogger

handler = logging.StreamHandler()
handler.setFormatter(jsonlogger.JsonFormatter(
    "%(asctime)s %(levelname)s %(name)s %(message)s %(lineno)d",
    rename_fields={
        "levelname": "level",
        "asctime": "timestamp",
        "name": "logger"
    }
))

logger = logging.getLogger("api")
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# 支持 extra 字段，会被自动序列化为 JSON
logger.info("用户登录", extra={"user_id": "u123", "ip": "192.168.1.1"})
```

输出：

```json
{"timestamp": "2024-01-15 10:30:00", "level": "INFO", "logger": "api", "message": "用户登录", "lineno": 42, "user_id": "u123", "ip": "192.168.1.1"}
```

### 6.2 敏感信息脱敏

日志里不能出现密码、token、手机号。用 Filter 自动脱敏：

```python
import re
import logging

class SensitiveFilter(logging.Filter):
    """自动脱敏手机号和邮箱"""
    PHONE_RE = re.compile(r"1[3-9]\d{9}")
    EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")

    def filter(self, record):
        msg = record.getMessage()
        msg = self.PHONE_RE.sub("1**********", msg)
        msg = self.EMAIL_RE.sub("****@****", msg)
        record.msg = msg
        record.args = ()  # 已经格式化过了，清空 args
        return True

logger = logging.getLogger("user_service")
logger.addFilter(SensitiveFilter())

logger.info("用户注册: phone=13812345678, email=test@example.com")
# 输出: 用户注册: phone=1**********, email=****@****
```

### 6.3 异常堆栈记录

三种方式记录异常，适用于不同场景：

```python
try:
    result = 1 / 0
except ZeroDivisionError:
    # 方式 1：在 error 中附加完整堆栈
    logger.error("计算失败", exc_info=True)

    # 方式 2：等价写法，更语义化
    logger.exception("计算失败")

    # 方式 3：只记异常类型和消息，不记堆栈
    import traceback
    logger.error("计算失败: %s", traceback.format_exc(limit=1))
```

### 6.4 性能：延迟格式化

日志消息的字符串拼接有开销。在高频率调用的代码路径上，用惰性求值：

```python
# 不推荐：即使 DEBUG 被过滤，f-string 也会被求值
logger.debug(f"处理了 {len(items)} 条数据，耗时 {elapsed:.3f}s")

# 推荐：使用 % 占位符，只有真正输出时才格式化
logger.debug("处理了 %d 条数据，耗时 %.3fs", len(items), elapsed)

# 推荐：检查级别再构造（适合特别昂贵的操作）
if logger.isEnabledFor(logging.DEBUG):
    detail = expensive_debug_dump()
    logger.debug("详细状态: %s", detail)
```

### 6.5 第三方库日志控制

很多库（requests、urllib3、SQLAlchemy）自己也有 logger。噪音太多时，把它们的级别调高：

```python
# 抑制 requests / urllib3 的冗余日志
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)

# 抑制 SQLAlchemy 的 SQL 日志（生产环境）
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
```

---

## 七、loguru：更现代的替代方案

如果你觉得标准库的 logging 配置太繁琐，`loguru` 是一个开箱即用的替代品：

```bash
pip install loguru
```

```python
from loguru import logger

# 开箱即用，不需要任何配置
logger.info("Hello from loguru!")

# 添加文件 handler，自动按时间轮转
logger.add(
    "logs/app_{time:YYYY-MM-DD}.log",
    rotation="00:00",      # 每天午夜轮转
    retention="30 days",   # 保留 30 天
    compression="zip",     # 压缩旧日志
    encoding="utf-8",
    level="DEBUG"
)

# 异常自动带堆栈，不需要 exc_info=True
try:
    1 / 0
except:
    logger.exception("出错了")

# 结构化输出（JSON）
logger.add("logs/app.json", serialize=True)

# 按级别分文件
logger.add("logs/error.log", level="ERROR")
logger.add("logs/info.log", level="INFO", filter=lambda r: r["level"].no <= 20)
```

loguru 的优点是零配置、API 简洁、自动带颜色。缺点是它不是标准库，大型团队项目通常还是用标准 logging + dictConfig，保持生态兼容。

---

## 八、最佳实践速查表

| 场景 | 做法 |
|------|------|
| 获取 logger | `logging.getLogger(__name__)` |
| 配置方式 | 小项目用 `basicConfig`，中项目用 `dictConfig` |
| 日志格式 | 必须包含时间、级别、logger名、行号 |
| 文件滚动 | 生产环境必须用 `RotatingFileHandler` |
| 异常记录 | 用 `logger.exception()` 或 `exc_info=True` |
| 字符串拼接 | 用 `%s` 占位符，不要用 f-string |
| 敏感信息 | 用 Filter 脱敏，永远不要记录密码和 token |
| 第三方库 | 把 urllib3、SQLAlchemy 等调成 WARNING |
| 编码 | Windows 上文件 handler 必须指定 `encoding="utf-8"` |
| propagate | 子 logger 配了 handler 就设 `propagate=False`，避免重复输出 |

---

## 九、常见问题排查

**日志重复输出**：子 logger 的 `propagate` 默认是 True，日志会同时被子和父的 handler 各输出一次。解决方法是设 `propagate=False`，或者只在父级配 handler。

**日志文件为空**：检查 handler 的 level 是否高于 logger 的 level。如果 logger 是 DEBUG 但 handler 是 INFO，DEBUG 消息不会写入文件。

**中文乱码**：`FileHandler` 必须指定 `encoding="utf-8"`。Windows 默认编码是 GBK，不指定就会乱码。

**basicConfig 不生效**：`basicConfig` 只在 root logger 没有任何 handler 时才生效。如果之前导入的库已经配过 root logger，basicConfig 会被静默忽略。解决方法是用 `force=True`（Python 3.8+）或手动配置。

**日志文件越来越大**：没有用滚动 handler。换成 `RotatingFileHandler` 或 `TimedRotatingFileHandler`，设置 `maxBytes` 和 `backupCount`。

---

*日志写得好，线上问题半小时定位；日志写得差，线上问题全靠猜。花 30 分钟把日志系统搭好，以后能省无数个小时。*
